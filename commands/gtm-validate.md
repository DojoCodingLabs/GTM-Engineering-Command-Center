---
name: gtm-validate
description: Unified two-stage pre-flight gate — neuro (attention/memory) + SDV (purchase intent/price/objections) blended into one DEPLOY/TEST/ITERATE/SKIP decision before spend. Validates ad creatives, offers, and landing copy.
argument-hint: "[path|dir] [--surface ad_creative|offer|copy] [--compare a b] | offer.yml"
---

# Unified Pre-Flight Gate

You run the **two-stage pre-flight**: neuro-testing predicts whether the brain will *notice, feel, and remember* a creative; **SDV** predicts whether the persona would *actually buy* it, at this price, and which variant wins. One blended verdict comes out: **DEPLOY / TEST / ITERATE / SKIP**, plus a **lever** telling you what to fix.

**The discipline:** rank, don't score. The comparative ranking is the headline; absolute scores and the neuro composite can only make a verdict *more conservative*, never mint a DEPLOY. Read `skills/synthetic-demand/SKILL.md` and `skills/synthetic-demand/rules/preflight-matrix.md` first.

**The two scorers are independent and license-clean.** `scripts/sdv-score.py` (MIT, stdlib) decides demand. `scripts/preflight-score.py` (MIT, stdlib) composes the neuro + SDV *outputs* — it never imports neuro code. Neuro (`scripts/neuro-score.py`) is the only Tribe v2 (CC-BY-NC) entry point and is **optional**: when Tribe v2 is absent or disallowed, the gate degrades cleanly to an SDV-only verdict.

## Arguments

- `/gtm-validate` — auto-detect the latest creatives in `.gtm/creatives/` (surface `ad_creative`)
- `/gtm-validate path/to/creative.png --surface ad_creative` — validate specific creative(s)
- `/gtm-validate offer.yml --surface offer` — validate an offer stack (runs the price test)
- `/gtm-validate "headline A" "headline B" --surface copy` — validate landing copy / headlines
- `/gtm-validate --compare a.png b.png` — two-variant duel

Surface defaults to `ad_creative`. Never mix surfaces in one run — demand scores are surface-local.

## Phase 0: Pre-flight setup

1. Read `.gtm/config.json` → `sdv` block (autonomy, ssr_mode, thresholds, min_resamples), `personas` block, and `targets`.
2. Detect the **neuro stage** (optional — only for `ad_creative`):
   ```bash
   python3 -c "from tribev2 import TribeModel; print('available')" 2>/dev/null
   ```
   - Available → Stage 1 runs. Absent → announce "neuro stage skipped (Tribe v2 not installed) — SDV-only verdict" and proceed. (Offer/copy surfaces never run neuro.)
3. Echo the CC-BY-NC notice when the neuro stage is active: "Tribe v2 is CC-BY-NC (non-commercial); it scores attention/memory only and is composed as a separate artifact — the SDV/MIT path runs independently."

## Stage 1: Neuro (ad creatives only, optional)

Delegate to the **neuro-analyst** agent / `/gtm-neurotest` plumbing: prepare stimuli (image→3s video) and run
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/neuro-score.py --input <stimuli> --output .gtm/validate/neuro-{date}.json
```
Collect the per-creative `composite` values into a map `{id: composite}`. **Do not threshold or band these yourself** — the composite is batch-relative (min-max normalized across the batch); the blend consumes it as a within-batch *rank* only. If only one creative is present, neuro is uninterpretable (raw) — the blend will flag `neuro-absolute-invalid` and fall back to SDV-only.

## Stage 2: SDV (always)

Delegate to the **demand-forecaster** agent (read `agents/demand-forecaster.md`). It declares the fidelity tier (F0–F3), assembles the panel from `.gtm/personas/` (or generates one), elicits free-text reactions and maps them to pmfs (FLR, or SSR via `scripts/ssr_embed.py` if embeddings detected), ranks comparatively with ≥5 resamples, scores the battery, and (for `offer`) runs the price test. It writes the concept + forecast and runs:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sdv-score.py .gtm/sdv/forecasts/<id>.input.json --config .gtm/config.json --out .gtm/validate/sdv-{date}.json
```
The SDV output carries each variant's comparative `rank`, `verdict`, `demand_score_relative` (or `_calibrated` at F3), and the batch `rank_stability`.

## Stage 3: Blend (the Pre-Flight Matrix)

For `ad_creative` with a neuro map, blend:
```bash
echo '{"sdv": <sdv-output>, "neuro": {"V1": 72.0, ...}}' | \
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight-score.py - --config .gtm/config.json --out .gtm/validate/scores-{date}.json
```
The matrix (`rules/preflight-matrix.md`) is asymmetric and reproducible:
- **strong demand + weak attention** → `ITERATE` · lever **visual** (the offer works; fix the creative execution before scaling)
- **strong attention + weak demand** → `ITERATE` · lever **offer** (it grabs the eye but won't sell — fix the offer/proof, not the visual)
- **both strong + stable #1 + F3** → `DEPLOY`
- **unstable rank** → tie → capped at `TEST`
- neuro **never upgrades** an SDV verdict; it only holds, downgrades, or sets the lever.

For `offer` and `copy` (no neuro), the SDV verdict is the verdict; the lever comes from the weakest construct.

## Phase 4: Present results

Ranked table, leading with the comparative signal:
```
Pre-Flight — {date} · surface: {surface} · fidelity: {F0–F3}{+SSR} · neuro stage: {active|skipped}

| # | Variant            | Neuro band | SDV demand | Stability | Verdict | Lever  |
|---|--------------------|-----------|------------|-----------|---------|--------|
| 1 | V1 outcome-hook    | strong    | 71 (rel)   | stable    | TEST    | offer  |
| 2 | V2 pain-hook       | weak      | 64 (rel)   | stable    | ITERATE | visual |

Headline: V1 wins the panel (stable). No DEPLOY below F3 — absolute demand is directional.
Levers: V1 → sharpen the offer/proof to lift purchase intent; V2 → strengthen the visual hook.
{For offers: VW acceptable range $X–$Y · revenue-max price $Z · per-segment split.}
{Caveats from the scorer, incl. neuro-absolute-invalid / neuro stage skipped / OOD < F3.}
```

## Phase 5: Save + route objections

- Write the human report to `.gtm/validate/results-{date}.md` and raw JSON to `.gtm/validate/scores-{date}.json`.
- Route mined objections (B0/B1/B2 from the forecast) per `skills/synthetic-demand/rules/objection-mining.md`: B0 demand-blockers with revenue at risk → flag for the creative-director (new angles), irresistible-offer (guarantees), and (Phase 6) the funnel-diagnostician ledger.
- Update `.gtm/MEMORY.md` with the two separate axes (fidelity tier ≠ realized confidence — see `/gtm-learn`).

## Where it slots

`/gtm-validate` is the Create→Deploy gate. It is invoked by `/hva-forge` (Phase 3) for forged creative batches, and as the (new) pre-flight step in `/gtm` and `/gtm-create` before `/gtm-deploy`. Only DEPLOY/TEST verdicts proceed to deployment; ITERATE/SKIP loop back with the lever.

## Error handling

- **No personas + nothing detected** → F0; present ranking only, refuse any absolute go/no-go, label "directional".
- **Tribe v2 absent** → SDV-only verdict; say so explicitly. Never block on neuro.
- **Single creative** → neuro is uninterpretable (raw); the blend flags `neuro-absolute-invalid` and uses SDV-only; SDV manufactures a status-quo reference.
- **SDV scorer raises** (e.g. a number-elicited one-hot pmf, or cross-surface comparison) → surface the error; re-elicit with the two-step protocol. Never silently skip.
