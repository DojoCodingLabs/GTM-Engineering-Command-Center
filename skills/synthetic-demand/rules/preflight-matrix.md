# The Pre-Flight Matrix — Blending Neuro + SDV Into One Verdict

This is the contract for the **unified two-stage pre-flight gate** (`/gtm-validate`). It pins
exactly what `scripts/preflight-score.py` does when it composes a neuro stage (attention/memory)
with an SDV stage (purchase intent/price) into a single **DEPLOY / TEST / ITERATE / SKIP** verdict
plus a **lever** (what to fix). The scorer is the source of truth; this file documents it. If the
two ever disagree, the code wins and this file is the bug.

- **Neuro** (`scripts/neuro-score.py`) — Meta **Tribe v2**, **CC-BY-NC** (non-commercial). Scores
  attention/emotion/memory only. Optional.
- **SDV** (`scripts/sdv-score.py`) — purchase intent / price / objections, **MIT**, stdlib. Always runs.
- **Blend** (`scripts/preflight-score.py`) — **MIT**, stdlib. Composes the two **JSON outputs**.

## The license firewall is structural

`preflight-score.py` **never imports neuro code**. It reads two JSON artifacts off disk — the SDV
scorer's output and a normalized neuro composite map `{id: composite}` — and composes their
**outputs only**. The MIT/SDV path and the CC-BY-NC/neuro path stay in separate processes; the only
thing that crosses the boundary is a number that has already been computed. This keeps the
non-commercial license off the demand path: SDV runs fully standalone when Tribe v2 is absent.

## Input

```json
{ "sdv": <sdv-score.py output>, "neuro": { "V1": 72.0, "V2": 64.0, ... } }
```

`neuro` is optional. When present it is a map from variant id to that variant's raw composite.

## GUARDRAIL §2 — neuro is a WITHIN-BATCH RANK, never an absolute

`neuro-score.py` **min-max normalizes its composite across the batch** and returns a *raw* value for
a single creative. So a neuro "70" is **not a property of the creative** — it is an artifact of which
other creatives were in the batch. The blend therefore refuses to read the number as a score and uses
only its **rank among the batch**:

1. `ranks_from_composites()` sorts the map descending — higher composite = better = rank 1.
2. `neuro_band(rank, n)` converts a 1-based rank to a **tertile band** by normalized position
   `pos = (rank-1)/(n-1)` (0.0 = best, 1.0 = worst):
   - `pos ≤ 1/3` → **strong**
   - `pos ≥ 2/3` → **weak**
   - else → **mid**
3. **Batch < 2 → no band.** `neuro_band` returns `None` and neuro contributes **nothing**; the run
   emits the caveat **`neuro-absolute-invalid`** ("a single creative's neuro composite is raw and
   batch-relative, so it is uninterpretable — SDV-only verdict"). A lone creative has no rank.

Do **not** threshold or band neuro composites yourself anywhere upstream. Hand the blend the raw
composite map and let it rank.

## GUARDRAIL §3 — this is a decision MATRIX, not a weighted average

Two separately-validated models measuring **different constructs** have no validated linear
combination. There is therefore **no blended 0-100 and no blended DEPLOY line**. Neuro can only:

- **HOLD** the SDV verdict (leave it unchanged), or
- **DOWNGRADE** it (make it more conservative), or
- **set the LEVER** (label what to fix).

**Invariant: neuro never UPGRADES an SDV verdict.** Dead demand cannot be rescued by attention.

## The matrix (`blend(sdv_verdict, band)` → `(verdict, lever)`)

| SDV verdict | Neuro band       | → Verdict | Lever    | Why |
|-------------|------------------|-----------|----------|-----|
| DEPLOY      | strong / mid     | DEPLOY    | none     | demand strong, attention fine — ship |
| DEPLOY      | weak             | ITERATE   | visual   | demand strong but attention weak → fix the **creative execution** before scaling |
| TEST        | strong / mid     | TEST      | offer    | hold the test; sharpen offer/proof to lift intent |
| TEST        | weak             | ITERATE   | both     | shaky demand **and** weak attention → fix both |
| ITERATE     | strong / mid     | ITERATE   | offer    | attention is fine, demand is weak → fix the **OFFER**, not the visual |
| ITERATE     | weak             | ITERATE   | both     | weak on both axes → fix both |
| SKIP        | (any)            | SKIP      | none     | demand is dead; attention cannot rescue it |

The asymmetry is the whole point: **strong demand + weak attention → `visual`** (the offer works, the
creative doesn't stop the scroll), while **strong attention + weak demand → `offer`** (it grabs the
eye but won't sell — don't waste the cycle polishing a visual that already works).

### SDV-only path (no neuro — `band is None`)

Verdict is **unchanged** (the SDV verdict passes straight through). The lever comes from the verdict:
`TEST` or `ITERATE` → **offer**; `DEPLOY` or `SKIP` → **none**. This is the path taken for the `offer`
and `copy` surfaces (which never run neuro), and whenever the neuro stage is skipped or invalid.

## Levers

| Lever    | Meaning |
|----------|---------|
| `none`   | nothing to fix on this axis (ship, or it's dead) |
| `visual` | fix the **creative execution** — hook, contrast, motion, face, pacing |
| `offer`  | fix the **offer / copy / proof** — price, guarantee, benefit, believability |
| `both`   | weak on both axes — fix the creative *and* the offer |

## Action resolution (`resolve_action(verdict, lever, autonomy)`)

Autonomy is applied in exactly **one place**. Spending money is **human-gated**:

| Verdict  | Action            | Autonomy gate |
|----------|-------------------|---------------|
| DEPLOY   | `recommend-deploy`| **never auto** — deploying spends money, always a human decision |
| SKIP     | `auto-archive`    | only when autonomy ∈ {`cut-auto`, `full-auto`} |
| SKIP     | `recommend-archive` | otherwise (`recommend`) |
| TEST / ITERATE | `hold`      | always — loops back with the lever |

This extends `hva-score.py`'s `resolve_action(verdict, autonomy)` with a `lever` argument (a new
function, not a copy); the reused part is the autonomy semantics.

## Graceful degradation

| Situation | Behavior |
|-----------|----------|
| Tribe v2 absent / CC-BY-NC disallowed | no `neuro` key → **SDV-only verdict**; caveat "neuro stage skipped (model artifact absent)" |
| Single creative (batch < 2) | neuro uninterpretable → **SDV-only verdict**; caveat **`neuro-absolute-invalid`** |
| `offer` / `copy` surface | neuro never runs → **SDV-only verdict**; lever = weakest construct |

In every degraded case the verdict is exactly the SDV verdict — neuro absence can only *remove*
conservatism the neuro stage would have added; it can never change a DEPLOY into something safer that
the demand model didn't ask for.

## Output

```json
{
  "summary": { "autonomy": "...", "neuro_stage": "active|skipped", "counts": {...} },
  "caveats": [ ... ],
  "creatives": [
    { "id": "V1", "sdv_verdict": "TEST", "neuro_band": "weak",
      "verdict": "ITERATE", "lever": "both", "action": "hold" }
  ]
}
```

`neuro_stage` is `active` only when at least one band was computed (batch ≥ 2 with a neuro map);
otherwise `skipped`.

## Common Mistakes

1. **Treating a neuro composite as an absolute score.** "V1 got 72, that's above 70, so it deploys."
   No — 72 is a batch-relative artifact. The blend uses rank only, and only to make SDV *more*
   conservative. There is no neuro DEPLOY line.
2. **Banding neuro yourself before the blend.** Hand the scorer the raw composite map; let
   `neuro_band()` rank. Pre-thresholding reintroduces the absolute reading §2 forbids.
3. **Expecting neuro to upgrade a verdict.** A strong neuro band on an `ITERATE` SDV result still
   yields `ITERATE` — it just sets the lever to `offer`. Neuro never mints a DEPLOY.
4. **Averaging the two stages into one 0-100.** §3 — there is no validated linear combination of two
   different constructs. It's a matrix, not a blended number.
5. **Running neuro on a single creative and trusting the band.** Batch < 2 is `neuro-absolute-invalid`;
   the verdict silently falls back to SDV-only. Score creatives in batches.
6. **Auto-deploying at high autonomy.** DEPLOY is *always* `recommend-deploy`. Only SKIP can
   auto-archive (at `cut-auto`/`full-auto`). Money is human-gated.
7. **Blocking the gate when Tribe v2 is missing.** Never block on neuro. SDV is the spine; neuro is an
   optional conservatism layer on top.
