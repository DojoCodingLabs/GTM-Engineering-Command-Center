# Outcome Calibration & the Intent→Behavior Discount

## Core Principle

**A synthetic signal is not a conversion rate until real outcomes say so.** This file owns the two
steps that turn an elicited intent distribution into an *honest* `est_conversion`: the **intent→behavior
discount** (the haircut every forecast applies) and the **F3 outcome-calibration loop** (the only thing
that earns the right to drop that haircut and make an absolute go/no-go call). It restates the governing
law of the skill, because calibration is where the temptation to mint a number is strongest:

> **Rank, don't score. Never ask a synthetic respondent for a number.**

Capability detection, the F0→F3 tier ladder, familiarity, and CI-width *sizing* live in
`rules/fidelity-tiers.md`. This file does not re-derive them — it consumes the tier and decides what an
`est_conversion` is allowed to claim at that tier. The two files share the same scorer
(`scripts/sdv-score.py`); read both before touching either.

## Step 3 — The F3 Outcome-Calibration Loop `[accuracy↑]`

This is the loop the source paper (Maier et al.) structurally could not run — their dataset was offline.
GTM is not offline: the Command Center ships ad creatives, offers, and copy, and watches what they
actually do. When the project has **both** shipped variants **and** real conversion data, fit a map from
synthetic signal to observed outcome and apply it forward.

1. **Assemble training pairs.** For each historically-shipped variant, pair its **synthetic signal**
   (the same `top_2_box_share` / mean purchase-intent the scorer would compute today, recomputed the
   *same* way — never a stale hand-entered number) with its **actual observed conversion**. Pairs live in
   `.gtm/sdv/calibration/`.
2. **Fit a monotonic map `g: synthetic_signal → actual_conversion`** — isotonic regression, or Platt
   scaling for a smooth logistic. Monotonic because more synthetic intent must never predict *less* real
   conversion; a non-monotone fit is a bug, not a finding.
3. **Apply `g`** to a new forecast's synthetic signal to produce a **calibrated `est_conversion`** (and,
   for `offer` surfaces, a revenue-maximizing price — see `rules/price-sensitivity.md`).
4. **Tighten CIs from `g`'s held-out residual.** The calibrated CI is the residual spread of `g` on
   **held-out** pairs, not the training fit. Report it as a calibration CI on `est_conversion`.

### The GTM adapter — what "actual conversion" is, per surface

This is a real adapter, not a rename of the source's Stripe-only hook. Each surface binds the synthetic
signal to a *different* real outcome pulled from a *different* system:

| Surface | Synthetic signal (this run) | "Actual conversion" (real GTM data) | Source |
|---|---|---|---|
| **`ad_creative`** | top-2-box purchase_intent share | ad-level **CTR · CVR · ROAS** | Meta / Google Ads (`/gtm-metrics` snapshots) |
| **`offer`** | top-2-box share + WTP curve | **checkout CVR** (and revenue/visitor) | Stripe / PostHog funnel |
| **`copy`** | top-2-box share | the downstream conversion of the page the copy is on | PostHog / GA |

A pair is `(synthetic_signal, actual_conversion)` tagged with its surface; **never** mix surfaces in one
map (a creative CTR and a checkout CVR are different outcomes on different scales — the same §8 firewall
that forbids cross-surface `demand_score` comparison forbids cross-surface calibration).

## Step 4 — The Intent→Behavior Discount `[accuracy↑]`

Even perfectly-matched *stated* intent over-predicts *action* — the intention–behavior gap. Convert
intent to estimated action with a discount multiplier:

| Tier | Discount | What it is |
|---|---|---|
| **F0 / F1 / F2 (uncalibrated)** | `0.5` (default) | `est_conversion ≈ top_2_box_share × 0.5` — a Juster-scale-inspired haircut. A **MODELED estimate**, not a measurement. Label it as such. |
| **F3 (calibrated)** | learned, folded into `g` | The discount is whatever `g` learned; no separate multiplier. `1.0` is reachable **only** when calibration error clears tolerance (below). |

The scorer is the law here. `intent_behavior_discount(tier, calibration)` returns `0.5` for F0–F2, and
returns the learned discount **only** when `tier == "F3"` *and* the calibration map carries
`valid: true`. There is no path in the code where a high `top_2_box_share` alone earns `1.0` — and there
must be no such path in your prose either. An uncalibrated `est_conversion` always travels with its
`× 0.5` label and the word "modeled".

## Guardrail §5 — the GTM evidence floor (stronger than the source)

The source let F3 unlock on mere *capability detection* (Stripe present ⇒ T3). **That is not enough
here.** Detecting that Meta/Stripe/PostHog *exist* tells you a map *could* be fit; it does not tell you a
map *was* fit, or that it's any good. F3's "absolute go/no-go" must clear three additional gates:

1. **Minimum paired observations, spanning ≥K distinct outcome levels.** Before *any* absolute verdict,
   require a floor of `(synthetic_signal, actual_conversion)` pairs **and** that those pairs span at least
   **K distinct outcome levels** (you cannot calibrate a curve from points that all sit at the same
   conversion rate — that's one level, not a map). Below the floor: **stay F2**, apply the default `0.5`
   discount, and say **calibration is pending more data**. Capability-detected-F3 with too few/too-flat
   pairs is reported as F2-with-pending-calibration, not F3.
2. **Ship the map with held-out validation error and a calibration CI.** A map without a held-out error
   estimate is not shippable. If the **calibration CI spans the verdict boundary** (the threshold between
   DEPLOY and TEST), the verdict **reverts to "directional"** — you do not know which side of the line you
   are on, so you do not get to call it.
3. **`intent_behavior_discount = 1.0` only when calibration error is below tolerance — NOT merely when
   `tier == F3`.** Tier is necessary, not sufficient. A fitted-but-inaccurate map keeps a discount < 1.0
   (or stays at the default). `tier == F3` is a permission to *look*, not a permission to *claim*.

> **Isotonic regression interpolates perfectly at low n and will report illusory-tight CIs.** With a
> handful of points an isotonic fit passes through every training pair, drives in-sample residual toward
> zero, and reports a calibration CI so tight it looks authoritative — and it is fiction. Guard against it
> with the held-out residual (gate 2) and the pair/level floor (gate 1); never read tightness off the
> training fit. **Never fabricate a map from a handful of points.**

## Where calibration pairs live, and how they accrue

| What | Where |
|---|---|
| `(synthetic_signal, actual_conversion)` pairs, tagged by surface | `.gtm/sdv/calibration/` |
| The fitted map `g` + held-out error + calibration CI | written alongside the pairs, referenced by `forecast.calibration` |

The **`/gtm-learn`** loop is what fills `.gtm/sdv/calibration/`: as campaigns ship and
`/gtm-metrics` snapshots land, it appends new pairs and **promotes the tier as evidence accrues** —
F1→F2 once customer language / analytics exist, F2→F3 only once the evidence floor above is cleared.
Promotion is earned by data over time, never asserted up front. A fresh project with no shipped history
sits at F0–F2 and says so; F3 is the destination, not the default.

## What a calibrated `est_conversion` may claim

- **F0 / F1 / F2:** "Modeled est. conversion ≈ top-2-box × 0.5 = 3.1% (directional — uncalibrated; the
  0.5 is a default intent→behavior haircut, not a measured rate). Lead with the ranking."
- **F3 (floor cleared):** "Calibrated est. conversion 4.1% (90% calibration CI 3.4–4.8%), held-out
  error ±0.6pp, from 24 paired observations across 6 outcome levels. Above the DEPLOY boundary on both
  CI bounds. Ship V2."
- **F3 (floor NOT cleared):** report as **F2-with-pending-calibration** — default discount, no absolute
  verdict, "calibration pending: have N pairs across L levels, need the floor."

## Common Mistakes

1. **Claiming absolute go/no-go below F3.** Lead with the ranking; the absolute field is
   `demand_score_relative` and `est_conversion` is modeled-only until F3.
2. **Fitting a map from a handful of points.** Stay F2; say calibration is pending. A low-n isotonic fit
   interpolates perfectly and reports illusory-tight CIs — fiction.
3. **`intent_behavior_discount = 1.0` without F3 data.** Intent over-predicts action; the default `0.5`
   haircut holds until a *valid* map says otherwise. `1.0` needs calibration error under tolerance, not
   just `tier == F3`.
4. **Unlocking F3 on capability detection alone.** Detecting Meta/Stripe/PostHog means a map *could* be
   fit, not that one *was* — or that it's good. Clear the evidence floor (pairs, levels, held-out error,
   CI not spanning the boundary) first.
5. **Reading CI tightness off the training fit.** Use `g`'s **held-out** residual; an in-sample fit (and
   especially isotonic regression) will lie to you about how sure it is.
6. **Mixing surfaces in one calibration map.** A creative's CTR and a checkout CVR are different outcomes
   on different scales — calibrate each surface against its own real signal, never pooled.
7. **Calibrating against a stale hand-entered synthetic number.** Recompute the synthetic signal the
   *same* way the scorer would today, or the pair is comparing two different instruments.
