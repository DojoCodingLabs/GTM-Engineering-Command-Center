# The Desk — CLEAR, the Read Ladder, and the decision contract

Layer 3 of the Stack and the decision diamond of the Loop. The Desk is the single place where the algorithm's early behavior becomes a cut-or-scale call. This file is the **human-readable contract** that `scripts/hva-score.py` implements deterministically and that `scripts/tests/test_hva_score.py` verifies. Every rule here is a testable condition.

Read by **volume, never by calendar time.** "It has only been 48 hours" is not a reason; "it has only had 600 impressions" is.

---

## The Read Ladder

Three rungs, selected by impressions (with a spend-based escalation). You only judge a creative on the metrics its rung has earned.

| Rung | Trigger | What you may read |
|---|---|---|
| **First read** | 1,000–2,000 impressions | CPM, CTR, thumbstop rate, quality ranking, early engagement |
| **Second read** | 2,000–5,000 impressions | cost per micro-conversion (add-to-cart, lead, registration, install), landing-page-view quality |
| **Hard read** | 5,000+ impressions **OR** ≥ 2× target CPA in spend (`hard_read_spend_multiple`, default 2.0) | purchases, qualified leads, CAC, ROAS, contribution margin |

Below ~1,000 impressions a creative is at the **below-first** rung: `hold` (insufficient signal). If its batchmates have many times its impressions, tag it **under-delivered** and retest in a cleaner batch rather than concluding anything.

The framework defines the hard-read spend trigger as "one to two times target CPA." The scorer uses the conservative end (**2×**, `hard_read_spend_multiple`) so that the second-read diagnostics (e.g. `fix-landing-or-offer`) remain reachable for a creative that has spent 1–2× CPA without yet earning 5,000 impressions — escalating to "hard" at 1× would short-circuit those reads.

---

## CLEAR — the checks, in evaluation order

The scorer evaluates these in order; the **first matching rule wins** the verdict. Verdicts are `cut`, `hold`, or `scale`. Every verdict carries a `triggering_signal` naming exactly why.

### C — Clean (the gate)
If the row is not from server-side / CAPI truth (`clean == false`), the verdict is **`hold`** with signal `dirty-feed`. No clean feed, no decision. The platform undercounts real conversions ~20–30% (see `evidence-base.md`), so deciding on platform-only data makes you fast and wrong. This gate runs first, before anything else.

### E — Economics (the fast-clock kill)
If `spend ≥ kill_multiple × target_cpa` (default `kill_multiple = 3.0`) **and** `qualifying_conversions == 0` → **`cut`**, signal `economics-3x-cpa-zero-conv`. Thresholds are spend-relative to your CAC, never a borrowed impression count.

### L — Lead (leading-indicator reads, from the Diagnostic Table)
Judged on leading indicators, never first-window ROAS. Evaluated at the rung the creative has reached:

| Condition | Rung | Verdict | Signal |
|---|---|---|---|
| ≥5,000 impressions, zero meaningful post-click action (no micro-conv, no conv) | hard | `cut` | `5k-impressions-zero-action` |
| ≥2,000 impressions, CTR below batch median by margin **and** quality ranking below average | second+ | `cut` | `bad-hook-ctr` (kill or rewrite the hook) |
| Strong CTR, weak micro-conversion | second+ | `hold` | `fix-landing-or-offer` (the creative works; fix the page/offer — do not cut the creative) |
| Good micro-conversion, weak purchase | hard | `hold` | `fix-price-checkout-trust` |
| Frequency ≥ ceiling (default 3.0) **and** CPA rising above target | hard | `hold` | `fatigue-refresh` (build variants from the winning angle) |
| Has conversions but CPA above target, frequency below ceiling | hard | `hold` | `cpa-above-target` (not scale-eligible; not yet fatigued) |

The two `hold` "fix-…" signals are deliberate: a creative that earns clicks but the funnel leaks is **not** a creative failure. The Desk surfaces the diagnosis without killing a good creative.

### A — Asymmetry (two clocks)
- **Fast clock — cut:** any single bad leading signal above is sufficient to cut. Cheap, reversible, immediate.
- **Slow clock — scale:** a creative is never scaled on a leading signal alone. It must reach the **hard read** and have a confirmed true conversion economics: `qualifying_conversions > 0` **and** `CPA = spend / qualifying_conversions ≤ target_cpa`.

The clocks are mismatched on purpose: cut fast, scale slow.

### R — Replication (the multiple-comparisons guard)
Economics passing the slow clock is necessary but **not sufficient**. A lone winner among many simultaneous tests is probably a multiple-comparisons ghost (testing `k` variants inflates the false-winner chance to `1-(1-α)^k`). Before a creative is `scale`-eligible it must also survive a **Benjamini-Hochberg** correction across the batch:

1. For each creative compute conversion rate `p_i = conversions_i / impressions_i`.
2. One-sided two-proportion z-test of creative `i` against the rest of the batch (creative rate > rest rate) → `p_value_i`, using pooled standard error. `Φ` via `math.erf`. If `n_i == 0` or `se == 0` → `p_value = 1.0`.
3. Compute B-H adjusted q-values at FDR `bh_alpha` (default `0.10`): sort p-values ascending; `q_(j) = min over r ≥ j of (k / r) × p_(r)`, clamped to ≤ 1.
4. A creative is **replication-confirmed** iff `q_value_i ≤ bh_alpha`.

**Verdict resolution for a slow-clock candidate:**
- Economics good **and** `q_value ≤ bh_alpha` → **`scale`**, signal `confirmed-winner` (carries `q_value`).
- Economics good **but** `q_value > bh_alpha` → **`hold`**, signal `awaiting-replication` (promising, unconfirmed — do not bet budget; let it accrue volume or repeat in a clean batch).

This is what kills "1 winner out of 100": with `k=100`, a modest single winner's raw p-value will not survive B-H, so it lands on `awaiting-replication`, not `scale`.

If none of C/E/L/A/R fire, the verdict is **`hold`** with signal `insufficient-signal`.

---

## The Diagnostic Table (signal → action) — full reference

| Signal | Action | Maps to |
|---|---|---|
| 5,000 impressions, zero meaningful post-click action | Kill | `cut: 5k-impressions-zero-action` |
| 2,000+ impressions, terrible CTR and poor diagnostics | Kill or rewrite the hook | `cut: bad-hook-ctr` |
| Strong CTR, weak add-to-cart or lead | Fix the landing page or offer | `hold: fix-landing-or-offer` |
| Good add-to-cart, weak purchase | Fix price, checkout, trust, or offer | `hold: fix-price-checkout-trust` |
| High spend velocity plus early conversion | Promote, then confirm the creative truth | slow-clock candidate → `scale`/`awaiting-replication` |
| Frequency rising plus CPA rising | Refresh the creative | `hold: fatigue-refresh` |
| Low spend, strong batchmates | Tag "under-delivered," retest in a cleaner batch | `hold: under-delivered` |
| Winner fatigues after scale | Build variants from the winning angle | `hold: fatigue-refresh` → Vault families |

> **Never read spend velocity as creative truth.** The ad the algorithm funds early may be the one it found a cheap audience for, not the better creative (divergent delivery; see `evidence-base.md`). High spend + early conversion makes a creative a *candidate*, confirmed only by the slow clock + replication.

---

## Scorer I/O contract

`scripts/hva-score.py` reads an insights JSON and a config, and emits a decision JSON. This contract is stable; the tests pin it.

### Input — insights rows
A JSON object `{ "creatives": [ row, ... ] }` (or a bare array). Each row:

| Field | Type | Notes |
|---|---|---|
| `ad_id` | string | identifier |
| `name` | string | optional, for display |
| `impressions` | number | required |
| `spend` | number | account currency |
| `clicks` | number | for CTR if `ctr` absent |
| `ctr` | number | optional; fraction or percent — normalized internally |
| `frequency` | number | optional |
| `quality_ranking` | string | `above_average` \| `average` \| `below_average` (or `below_average_*`); optional |
| `micro_conversions` | number | add-to-cart / LP view / lead / registration; optional, default 0 |
| `conversions` | number | qualifying CAPI events; default 0 |
| `clean` | bool | server-side/CAPI truth for this row; default `true` if a top-level `clean` flag is set, else required |

### Input — config (subset of `.gtm/config.json`)
`target_cpa` (required), `kill_multiple` (3.0), `bh_alpha` (0.10), `frequency_ceiling` (3.0), `hard_read_spend_multiple` (2.0 → hard read at ≥ 2× target CPA in spend), `ctr_margin` (median margin for `bad-hook-ctr`, default 0.6 → CTR < 0.6 × batch-median CTR counts as terrible), `autonomy` (`recommend` \| `cut-auto` \| `full-auto`), `scale_bid_cap_multiple` (0.7), `max_daily_budget_increase_pct` (20).

### Output
```json
{
  "summary": {
    "k": 5, "baseline_rate": 0.012, "bh_alpha": 0.10,
    "autonomy": "recommend",
    "counts": { "cut": 2, "hold": 2, "scale": 1 }
  },
  "creatives": [
    {
      "ad_id": "1234",
      "name": "pain-point-claymation",
      "rung": "hard",
      "verdict": "cut",
      "triggering_signal": "economics-3x-cpa-zero-conv",
      "reason": "Spent $63 (3.2x target CPA) with 0 qualifying events.",
      "clock": "fast",
      "q_value": null,
      "metrics": { "impressions": 8200, "spend": 63.0, "ctr": 0.009, "cpa": null, "conv": 0 },
      "autonomy_action": "recommend-pause"
    }
  ]
}
```

### `autonomy_action` resolution (the only place autonomy is applied)
| verdict | `recommend` | `cut-auto` | `full-auto` |
|---|---|---|---|
| `cut` | `recommend-pause` | `auto-pause` | `auto-pause` |
| `scale` | `recommend-scale` | `recommend-scale` | `auto-scale` (bounded by `scale_bid_cap_multiple` + `max_daily_budget_increase_pct`) |
| `hold` | `hold` | `hold` | `hold` |

Pausing only ever saves money and is reversible, so it is automated one tier earlier than scaling. The `hva-desk` agent executes these actions; the scorer never calls the Meta CLI itself (separation of decision from action — the decision must be reproducible and testable in isolation).
