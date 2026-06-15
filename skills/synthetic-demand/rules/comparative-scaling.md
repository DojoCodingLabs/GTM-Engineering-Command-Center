# Comparative Scaling — The Accuracy Spine

## Core Principle

**Ranking is the reliable signal; absolute scores are not.** Design every run so that the headline
output is a *comparison*, not a number. This is just the governing law of the skill restated for the
scaling layer:

> **Rank, don't score. Never ask a synthetic respondent for a number.**

This is the cleverest move in SDV, and it's grounded in the paper's own data. The flagship result —
**ρ ≈ 90% correlation attainment** — is a *ranking* metric (how well synthetic mean intent orders
concepts the way humans do). The *absolute* distribution match (KS, plus a residual positivity offset
the authors admit they never fully removed) is the weaker, anchor-dependent part. So the method is
*most* trustworthy when asked **"which of these is better?"** and *least* trustworthy when asked
**"what's the absolute score?"** SDV is built to ask the question the method answers well.

Conveniently, this is also the shape of almost every real GTM decision: *which* ad creative, *which*
landing headline, *which* price, *which* offer framing. You almost never need the bare number — you
need the order.

## Two Comparative Instruments

### 1. Best–Worst Scaling (MaxDiff-style) — preferred for 3–6 variants

Show each persona the full variant set. Ask them, in character, to pick the **one they'd most likely
buy** and the **one they'd least likely buy**, with a one-line reason for each (free text — never a
rating). From this:

```
best_worst_share(V) = (times V picked best − times V picked worst) / times V appeared
```

Range −1.0 (always worst) to +1.0 (always best). This single number is robust, intuitive, and far more
stable across reruns than absolute construct means.

For **>6 variants**, show each persona **random subsets of 4–5** (a MaxDiff design) and aggregate
shares across subsets — never make a persona rank 10 creatives at once.

### 2. Pairwise Duels — preferred for 2 variants, or to break ties

For each pair (A, B), ask "which would you actually buy, A or B — and why?" Aggregate into:

```
win_rate(V) = duels won by V / duels V participated in
```

Optionally fit a **Bradley–Terry** strength per variant from the pairwise outcomes for a smooth ranking
when there are many pairs. Plain win-rate is fine for small sets.

| Instrument | Best for | Headline statistic | Range |
|---|---|---|---|
| Best–Worst Scaling | 3–6 variants (MaxDiff subsets for >6) | `best_worst_share(V)` | −1.0 … +1.0 |
| Pairwise Duels | 2 variants, or tie-breaks | `win_rate(V)` (opt. Bradley–Terry strength) | 0.0 … 1.0 |

## Aggregation Across the Panel

- Compute best-worst share / win-rate **per persona first**, then aggregate **weighted by `user_pct`**
  for a market-share view and **weighted by `revenue_pct`** for a revenue view. Report whichever the
  decision needs — an ad creative aimed at high-LTV segments should be judged on the revenue-weighted
  ranking, not the headcount one.
- Always surface **segment splits**: a variant can win the panel but lose the segment that actually
  pays. **"V2 wins the panel but V1 wins P01/P03 = 62% of revenue"** is a far more useful sentence than
  a single overall rank, and it's the kind of split that flips a launch decision.

## Rank Stability (mandatory — guardrail §6)

A ranking is only allowed to be called **stable** when it survives **≥5 resamples**. One resample is
not evidence; it is a coin you flipped once. This is stricter than a "run it at least twice" rule of
thumb, and it is enforced in `scripts/sdv-score.py`, not left to prose.

What the scorer does:

- Resample the panel (and the elicited reactions) **≥5 times** and recompute the comparative ranking
  each time.
- Report a **stability statistic**, not a one-shot boolean: the **fraction of resamples in which the
  #1 variant holds its rank**, plus the **mean Kendall's τ** of the full order across resamples. A high
  hold-fraction with high mean τ ⇒ `rank_stability: "stable"`.
- **Fewer than 5 resamples ⇒ `rank_stability: "indeterminate"`**, which **caps the verdict at TEST** —
  the scorer will not mint a DEPLOY off an unresolved ranking.
- A #1 whose lead sits **inside resample noise** (the runner-up overtakes it on some resamples, low
  hold-fraction / low τ) is **`"unstable"` = a TIE, never a winner.** Say so loudly in the report and
  decide on other grounds (cost, brand fit, neuro-testing read) or escalate to a real human test.

**Tie to HVA's "don't bet on a ghost" discipline.** This is the *synthetic* mirror of HVA's
**R**eplication rung in CLEAR and guardrail **G8**: *a lone winner among many simultaneous tests is
probably a multiple-comparisons ghost — confirm with a correction (Benjamini-Hochberg) or a clean
repeat before betting budget.* HVA polices that on **real spend**; comparative scaling polices it on
**synthetic demand**, *before* a dollar moves. An unstable #1 is exactly the ghost Benjamini-Hochberg
exists to catch — except here the correction is the resample distribution, and the rule is the same:
**don't crown a coin flip.** A within-noise lead is not a winner you forgot to celebrate; it is a tie
you must report.

## Single-Variant Runs Still Get a Comparison

If the concept has only one variant (`comparison_mode: single`), **manufacture a reference** so the
persona still makes a *relative* judgment rather than an inflated absolute one. Use, in order of
preference:

1. The **status quo / "do nothing"** alternative the segment currently uses.
2. A **known competitor** or the category default.
3. A **neutral baseline** version of the concept (e.g., a plain-vanilla rewording of the headline).

Report absolute purchase-intent for context, but frame the verdict as **"preferred over status quo by
X% of the segment,"** which is both more honest and more accurate than a lonely 4.2/5.

## How Comparative and Absolute Combine

- **Comparative rank = the headline.** It decides *which* variant ships.
- **Absolute purchase-intent distribution = context.** It hints at *how strong* demand is in absolute
  terms — but it can only ever **sharpen the read conservatively** (make a verdict *more* cautious,
  never mint a DEPLOY). It is trusted as a genuine go/no-go **only at F3** once calibrated to real
  outcomes (Meta CVR / Stripe / PostHog — see `calibration.md`). Below F3 it travels as
  `demand_score_relative`.
- **`demand_score`** (`construct-battery.md`) blends constructs into a 0–100. When two variants' demand
  scores are within noise, the **comparative signal breaks the tie** — not the decimal places.

| Fidelity tier | What the comparative rank claims | What the absolute `demand_score` may claim |
|---|---|---|
| **F0 Cold-start** | ranking only | directional only — never a verdict |
| **F1 Persona-grounded** | ranking + relative | still soft; conservative sharpening only |
| **F2 Data-anchored** | ranking + better-grounded relative | better-grounded, still not go/no-go |
| **F3 Outcome-calibrated** | ranking (still the headline) | **absolute go/no-go enabled** |

## Common Mistakes

1. **Averaging absolute scores and calling it a ranking.** Use best-worst / duels; they're more stable.
2. **Ignoring segment weights.** An unweighted panel average can crown a variant the paying segment hates.
3. **Too many variants at once.** >6 → use MaxDiff subsets, not a 10-way rank.
4. **Calling a ranking stable off one resample.** Stability requires **≥5 resamples**; fewer is
   `indeterminate` and caps the verdict at TEST.
5. **Reporting a winner from an unstable ranking.** If the #1 sits inside resample noise, it's a TIE —
   the ghost HVA's Benjamini-Hochberg discipline exists to catch. Say so.
6. **Letting a single-variant run produce a lonely inflated 4.2/5** instead of a comparison vs. status quo.
