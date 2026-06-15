# Price Sensitivity — Van Westendorp + Gabor-Granger

## Core Principle

The paper measures purchase intent at the concept's *implied* price and **never varies price.** But for a
GTM **offer** — a $497 LATAM info-product, a $997 cohort, a paid SaaS plan — **price is the decision.** Is
the offer priced right? What does demand look like at $297 vs $697? SDV adds a synthetic price-sensitivity
layer the paper lacks, and it runs **only on the `offer` surface** (a bare `ad_creative` carries no price;
`copy` tests wording). Price-testing a creative or a headline is a category error — the price test is gated
to `offer`.

The governing law of the skill still holds, unbent:

> **Rank, don't score. Never ask a synthetic respondent for a number.**

You **never** ask a synthetic respondent to "set the price." You elicit free-text reactions at *specific*
prices, in character, and aggregate. And the resulting willingness-to-pay is **a price, never a
0–100 demand_score input** — `willingness_to_pay` is explicitly dropped from the blend in the scorer
(`c != "willingness_to_pay"` in `demand_score()`). WTP's effect on the verdict flows in only through
`price_fairness` (a Likert construct) and through the demand curve, never as a number poured into the
composite.

## Method 1 — Van Westendorp PSM (where's the acceptable band?)

Ask each respondent four price questions about the offer, **in character**, as free-text-then-map (the
reaction call never sees a number to repeat; the price they name is mapped onto the panel's cumulative
curves in a separate step):

1. **Too cheap** — "At what price would this feel so cheap you'd doubt it's any good?"
2. **Cheap / bargain** — "At what price would this be such a deal you'd grab it without thinking?"
3. **Expensive** — "At what price would this start to feel expensive, but you'd still consider it?"
4. **Too expensive** — "At what price would you definitely walk away?"

Aggregate the four **cumulative curves** across the panel. `too_cheap` and `cheap` *descend* with price
(fewer people still call it cheap as the price climbs); `expensive` and `too_expensive` *ascend*. The
scorer's `van_westendorp_crossings(curves)` takes the four curves
(`{"too_cheap","cheap","expensive","too_expensive"}` → `{price: fraction}`), finds the crossings by linear
interpolation on each sign change, and returns:

- **PMC** (Point of Marginal Cheapness) — crossing of `too_cheap` × `expensive`; the **lower** edge of the
  acceptable range.
- **PME** (Point of Marginal Expensiveness) — crossing of `cheap` × `too_expensive`; the **upper** edge.
- **OPP** (Optimal Price Point) — crossing of `too_cheap` × `too_expensive`; the price minimizing total
  price resistance.
- **IPP** (Indifference Price Point) — crossing of `cheap` × `expensive`; the typical/expected price the
  market reads as "normal."
- **`acceptable_range` = [PMC, PME]** — the band the market will tolerate, written to
  `willingness_to_pay.acceptable_range` in the forecast.

The exact mapping, verbatim from the scorer:

```python
pmc = _crossing(curves["too_cheap"],  curves["expensive"],      prices)   # lower bound
pme = _crossing(curves["cheap"],      curves["too_expensive"],  prices)   # upper bound
opp = _crossing(curves["too_cheap"],  curves["too_expensive"],  prices)   # optimal price point
ipp = _crossing(curves["cheap"],      curves["expensive"],      prices)   # indifference price point
return {"pmc": pmc, "pme": pme, "opp": opp, "ipp": ipp, "acceptable_range": [pmc, pme]}
```

VW answers **"what price band will the market tolerate?"** — it never names the revenue-max price; that's
Gabor-Granger's job.

## Method 2 — Gabor-Granger (what's the revenue-maximizing price?)

Sweep the offer across discrete price points (`offer.price_test.price_points`, e.g. the LATAM odd-pricing
ladder `[297, 497, 697, 997, 1497]`). At **each** price, run the normal purchase-intent elicitation and
get a distribution, then estimate conversion and build the demand curve. The scorer's
`gabor_granger_revenue_index(price_conversion)` takes a `{price: est_conversion}` map and is exactly:

```python
def gabor_granger_revenue_index(price_conversion):
    """Gabor-Granger: revenue_index(p) = p * est_conversion(p); argmax = revenue-max price."""
    items = sorted(price_conversion.items())
    curve = [{"price": p, "est_conversion": c, "revenue_index": round(p * c, 4)}
             for p, c in items]
    best = max(curve, key=lambda x: x["revenue_index"]) if curve else None
    return {"demand_curve": curve,
            "revenue_max_price": best["price"] if best else None}
```

So, in words:

```
revenue_index(price) = price × est_conversion(price)
revenue_max_price    = argmax over the swept prices of revenue_index
```

- `est_conversion(price)` = `f(purchase_intent distribution at that price)` — the top-box / top-2-box share
  of the PI pmf, then the **intent→behavior discount** from `rules/calibration.md`
  (`intent_behavior_discount()` — 0.5 below F3, 1.0 only when an F3 calibration map justifies it).
- The **revenue-maximizing price** is `argmax revenue_index` → `revenue_max_price`, surfaced as the
  Gabor-Granger optimum.
- Report the **full `demand_curve` array** (every `{price, est_conversion, revenue_index}` row) so the user
  sees the *shape*, not just the peak. A peak that's a flat plateau across two prices is a different call
  than a sharp single-price spike.

GG answers **"which price makes the most money?"** Run **both** VW and GG whenever you can: VW gives the
tolerable band, GG finds the optimum inside it. A revenue-max price that sits *above* PME is a flag — the
optimum is outside what the market says it will tolerate, and the curve is probably under-sampled.

## Modeled vs. calibrated `est_conversion`

`est_conversion` is **modeled, not measured**, below F3 — it is the PI top-box share times the conservative
default haircut, and it **must be labeled as such** in the forecast. At **F3**, the synthetic→actual map
(`rules/calibration.md`) replaces the modeled `f(...)` with a calibrated one
(`intent_behavior_discount()` returns the fitted `learned_discount` instead of 0.5), and the
revenue-maximizing price becomes a *trustworthy* number rather than a directional one. Below F3, present the
whole price layer as directional — the *shape* of the curve (where demand falls off) is informative even
when the absolute conversion level is not.

## Monotonicity-or-flag (a real demand curve never rises with price)

A real demand curve is **monotonic non-increasing**: as price goes up, estimated conversion goes down (or
holds), never up. Rising conversion with rising price is **noise**, not signal. The scorer's
`is_monotonic_nonincreasing(values)` is the guard:

```python
def is_monotonic_nonincreasing(values):
    """A real demand curve never rises with price; rising est_conversion is noise to flag."""
    return all(values[i] >= values[i + 1] for i in range(len(values) - 1))
```

Run it on the `est_conversion` series (in ascending price order). If it returns `False`, **do not** pass the
curve off as signal — add panel samples (re-elicit at the offending price points) or **flag** the run as
under-powered. Reporting the `revenue_max_price` off a non-monotonic curve is reporting an artifact.

## Per-segment demand curves

Different personas have different wallets — a bootstrapping LATAM solopreneur and a funded team do not share
a WTP. **Compute the curve per segment**, weighted by the segment's `user_pct` / `revenue_pct` (the same
segment weights used in `rules/comparative-scaling.md` and `rules/objection-mining.md`), and surface the
split rather than only the blend:

> "Blended optimum is $497, but P01 (bootstrapper, 15% of users) drops off above $297 while P03 (agency
> owner, 40% of revenue) is price-insensitive to $1497 — consider a two-tier offer or regional pricing."

Segment heterogeneity is often the most valuable finding here: it turns "what price?" into "which prices,
for whom?" — the seed of tiering, regional/LATAM pricing, and payment plans. A blended curve that hides a
bimodal panel will pick a price that's wrong for *both* halves.

## Worked Framing — a $497 LATAM info-product

- Anchor price 497; sweep the odd-pricing ladder `[297, 497, 697, 997, 1497]`.
- **VW** → is $497 inside `[PMC, PME]`, or already past PME for the core bootstrapper segment?
- **GG** → does `revenue_index` peak at 497, or would 697 — with lower `est_conversion` but a higher price —
  actually earn more? Report the full `demand_curve` so the plateau (if any) is visible.
- **Monotonicity** → confirm `est_conversion` falls (or holds) from 297→1497; if it bumps up at, say, 697,
  re-sample before trusting the peak.
- **Per-segment** → who churns out of the funnel at $497, and what `revenue_pct` do they represent? That's
  the input to a daily-cost reframe ("menos que un café al día") or a payment plan.

## Where the price test plugs in

- **Anchor** — the offer stack's value-anchored "Total value" (from `skills/irresistible-offer/`) is the VW
  `anchor_price`; the LATAM odd-pricing points ($497/$997 ladders, daily-cost framing) supply the GG
  `price_points`. See `skills/irresistible-offer/rules/offer-frameworks.md`.
- **Objections** — a `price_fairness` low score or a clustered "too expensive" objection promotes onto the
  **B-tier** axis (B0/B1/B2, `rules/objection-mining.md`) with a remedy of *re-price to the WTP the price
  test supports*.
- **Gate** — `/gtm-validate --surface offer` runs the full battery **plus** this price test, returning the
  revenue-max price and the acceptable band alongside the comparative ranking.

## Common Mistakes

1. **Asking the model to "pick a price."** That's the same sin as asking for a rating — sweep specific
   prices and elicit reactions instead. Never elicit a number.
2. **Running the price test off-`offer`.** It is gated to the `offer` surface; a creative/copy has no price
   reveal to test.
3. **Letting WTP into the 0–100 blend.** It's a price; it routes through `price_fairness` + the demand
   curve. The scorer drops it explicitly.
4. **One blended curve, hiding segment heterogeneity.** The split is usually the insight — compute per
   segment, weighted by `user_pct` / `revenue_pct`.
5. **Treating modeled `est_conversion` as calibrated.** Below F3 it's directional; say so. Only an F3 map
   earns a trustworthy absolute conversion.
6. **Non-monotonic demand curves passed off as signal.** Demand should fall as price rises; if
   `is_monotonic_nonincreasing` is `False`, add samples or flag it — don't report the peak.
7. **Running GG without VW (or vice-versa).** The band and the optimum answer different questions; a
   revenue-max price above PME is a flag, not a recommendation.
