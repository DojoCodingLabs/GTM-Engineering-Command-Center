# Construct Battery & Demand Score

## Core Principle

Conversion is **multivariate**. The Maier et al. paper measured one construct (purchase intent) plus a
single "relevance" cameo. But a concept can fail for very different reasons — unclear, unbelievable, not
differentiated, mispriced — and a lone purchase-intent number hides *which*. SDV measures a **battery** of
constructs, each elicited in character and mapped to its own Likert distribution, then blends them into one
composite **Demand Score** while keeping the per-construct detail that tells you *why* a concept under- or
over-performs. More correlated signals also **reduce variance**, so the composite is more stable than any
single read.

This is where the governing law of the skill earns its keep:

> **Rank, don't score. Never ask a synthetic respondent for a number.**

Every construct below is elicited as a brief free-text reaction (the reaction call never sees the scale),
then mapped to a 5-point pmf in a *separate* step (`rules/elicitation-methods.md`). The Demand Score is a
*reconstruction* over those mapped distributions — it never minted itself by polling a persona for a digit.

## The Eight Constructs

| Construct | The question (in character) | Scale | Reading |
|-----------|------------------------------|-------|---------|
| **purchase_intent** | "Would you actually buy this?" | 1–5 | The core demand signal |
| **appeal** | "How much does this grab you?" | 1–5 | Gut attraction, pre-rational scroll-stop |
| **comprehension** | "Do you understand what this is and what you get?" | 1–5 | Low ⇒ confused copy, not weak demand |
| **differentiation** | "Is this meaningfully different from your alternatives?" | 1–5 | Low ⇒ commodity / me-too |
| **believability** | "Do you believe it'll deliver what it promises?" | 1–5 | Low ⇒ trust/proof gap |
| **price_fairness** | "Is this worth the price shown?" | 1–5 | Value perception at the displayed price |
| **willingness_to_pay** | (elicited via price methods, not a reaction) | currency | The price they'd accept — see `rules/price-sensitivity.md` |
| **share_intent** | "Would you tell someone about this?" | 1–5 | Virality / advocacy proxy |

Measure a **surface-appropriate subset** — you don't need `price_fairness` for a bare creative whose price
lives on the landing page. The subset and weights actually used are fixed per surface in the scorer
(`scripts/sdv-score.py`), not chosen ad hoc; see below.

## Composite Demand Score (0–100)

Blend the Likert constructs (each mean normalized from 1–5 to 0–1 as `(mean−1)/4`) with default weights:

| Construct | Default weight |
|-----------|----------------|
| purchase_intent | 0.35 |
| price_fairness | 0.15 |
| appeal | 0.15 |
| comprehension | 0.10 |
| differentiation | 0.10 |
| believability | 0.10 |
| share_intent | 0.05 |

```
demand_score = 100 × Σ( weight_c × (mean_c − 1) / 4 )   over measured constructs,
               with weights renormalized to sum to 1 over whatever subset was measured.
```

This table is the scorer's `DEFAULT_WEIGHTS` dict, verbatim — they must stay in lockstep. The weights
sum to 1.00 over the full battery; on any measured subset the scorer renormalizes the present weights to
sum to 1 before applying the formula.

`willingness_to_pay` is a **price, not a 0–1 score** — it is **excluded from the blend**. The scorer drops
it explicitly (`c != "willingness_to_pay"`) even if a weight were supplied. Its effect on demand flows in
through `price_fairness` and through the price-sensitivity curve, never directly into the 0–100 number.

## Per-surface subsets & reweighting

The defaults suit a full offer. The scorer's `_surface_weights()` swaps in a surface-specific weight set
(and therefore a specific construct subset) for the two wired non-offer surfaces. These are the exact
weights the scorer uses — do not improvise them:

| Surface | Construct subset & weights (sum to 1.00) | Rationale |
|---------|-------------------------------------------|-----------|
| **`ad_creative`** | purchase_intent 0.30 · appeal 0.25 · comprehension 0.20 · differentiation 0.15 · share_intent 0.10 | A scroll-stopping, instantly-legible, shareable creative matters more than price perception — the landing page handles price. |
| **`copy`** | purchase_intent 0.30 · comprehension 0.30 · believability 0.25 · appeal 0.15 | Copy's job is clarity + trust; up-weight `comprehension` + `believability`. |
| **`offer`** | the full default battery (the 7-row table above) | A full offer stack with a visible price exercises every construct, including `price_fairness` and `willingness_to_pay` via a price test. |

`feature` exists in the construct table as a **future seam** — it is a recognized surface name but is **not
a wired surface**: `_surface_weights()` has no `feature` branch, so it would fall through to the full default
battery. Don't rely on it until it's wired.

The weights actually applied (default, surface-specific, or an explicit `weights` override on the forecast)
are **recorded in the forecast** so `demand_score` is fully reproducible from construct means × the recorded
weights. A forecast whose score can't be reconstructed from its own recorded weights is invalid.

## §8 guardrail — do NOT compare demand_score across surfaces

A `demand_score` of **70 on the 4-construct `copy` subset is not the same evidentiary thing** as a 70 on the
7-construct `offer` battery. They are computed over different construct subsets with different weights, so
the two numbers live on **different, non-comparable scales**. Treat `demand_score` as comparable **only within
a single surface**.

This is enforced, not advisory: `assert_single_surface()` in the scorer **raises** if a comparison set mixes
surfaces (`"cannot compare across surfaces … — demand_scores are only comparable within a single surface"`).
Rank creatives against creatives and offers against offers; never rank a creative's score against an offer's.

## Objection & Driver Mining → the Gap-Audit Bridge

A low score is a dead end; a structured *objection* is an actionable, revenue-tagged fix. From the free-text
reactions you already elicited (don't re-poll), cluster near-duplicate reactions into **structured**
objections (`segment, objection, severity, frequency`) and drivers (`segment, driver, strength`) — never dump
raw quotes. High-severity, high-frequency objections promote into the gap audit as demand-tagged blockers on
the **B-tier** axis (**B0** Demand Blocker · **B1** Demand Friction · **B2** Demand Polish), each carrying the
segment, revenue at risk, and a suggested remedy.

That is the whole mechanism — the full B0/B1/B2 thresholds, the promotion rules, and the revenue-at-risk math
live in **`rules/objection-mining.md`**. Do not duplicate them here; this section only points the battery at
the bridge.

## Common Mistakes

1. **Reporting only purchase_intent.** You lose the *why*; you can't tell a pricing problem from a clarity
   problem from a trust problem. Always report the full measured battery.
2. **Fixed weights regardless of surface.** Use the scorer's per-surface weights — `ad_creative`, `copy`,
   and `offer` each have their own subset; don't apply the offer defaults to a creative.
3. **Comparing demand_score across surfaces.** A `copy` 70 ≠ an `offer` 70; the scorer raises on it. Rank
   within a surface only.
4. **Asking a persona for a number.** Elicit a free-text reaction (scale-blind), then map to a pmf in a
   separate call. A near-one-hot pmf is the signature of a number that was elicited and softmaxed — rejected.
5. **Letting WTP into the 0–100 blend directly.** It's a price; route it through `price_fairness` + the
   price-sensitivity curve.
6. **Not recording the weights used.** If `demand_score` can't be reconstructed from the recorded weights,
   the forecast isn't reproducible.
7. **Dumping raw quotes as "objections."** Cluster into structured items with severity + frequency, then
   promote B0 blockers per `rules/objection-mining.md`.
