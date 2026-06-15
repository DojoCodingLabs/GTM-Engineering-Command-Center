# Revenue-at-Risk — Mapping Demand Blockers onto the Funnel

## Core Principle

A funnel can leak for two completely different reasons, and the fix is different in each case:

> **The funnel may leak because the OFFER has a demand blocker, not because the page is slow.**

A **funnel/page/tracking bottleneck** is mechanical — a slow LCP, a broken CAPI event, a confusing
onboarding step, a checkout that 500s. You fix it with engineering. A **demand blocker** is about the
*offer itself* — the price, the proof, the risk the buyer is asked to carry. No amount of page-speed work
closes a sale the buyer doesn't believe in. This file is the bridge that keeps the two diagnoses from
being confused: it takes the SDV demand-side **B-tier blockers** (`skills/synthetic-demand/rules/objection-mining.md`)
and maps them onto the **AARRR funnel stages** the diagnostician already scores, so the funnel report can
say *which* leaks are demand and *which* are plumbing.

> **No naming collision.** **F** = fidelity tiers (F0–F3, how grounded the SDV forecast is). **B** =
> demand blocker tiers (B0/B1/B2, how hard an objection blocks the sale). The five **AARRR stages**
> (Acquisition, Activation, Retention, Revenue, Referral) are a separate axis again — a B0 blocker *lands
> on* a stage, it does not rename it. Three orthogonal axes, no clash.

## The B-tiers (read from objection-mining first)

These tiers are defined in `skills/synthetic-demand/rules/objection-mining.md`; this file consumes them
without redefining them. The thresholds — quoted here so the funnel reads the same table the SDV skill
promotes against:

| Objection profile | Tier | Funnel meaning |
|---|---|---|
| severity **high** + frequency **≥ 0.4** in a paying segment | **B0 — Demand Blocker** | **Kills conversion now** — the offer, not the page, is why this stage leaks |
| severity **medium**, or lower frequency | **B1 — Demand Friction** | Dampens conversion — friction on the offer |
| severity **low** | **B2 — Demand Polish** | Minor lift — polish |

"Paying segment" is load-bearing: a B0 is only a B0 when it blocks people who would otherwise *pay*. A
loud objection from a segment that was never going to buy is noise, not a blocker.

## Revenue at risk — the dollar tag

Every B-tier item carries the money it threatens, so the funnel triages by dollars, not by how loud the
objection felt:

```
revenue_at_risk = segment.revenue_pct × target_MRR
```

`target_MRR` is the project's revenue target, read from `.gtm/config.json` (the same revenue figure the
rest of the Command Center plans against). `segment.revenue_pct` is the persona segment's share of that
target. This is the *identical* formula the SDV ledger uses — the funnel does not invent a second number;
it reads the `revenue_at_risk` already computed on each `top_objections[]` entry of the forecast.

## Mapping B-tiers onto AARRR stages

A demand blocker doesn't float free — it lands on the funnel stage where the buyer is making the
decision the objection is about. Map by what the objection is *about*:

| Objection is about… | Lands on AARRR stage | Why |
|---|---|---|
| price / "too expensive" / "can't justify the cost" | **Revenue** | the price decision happens at checkout — the leak is at the paywall, but the cause is the offer |
| believability / "does this actually work?" / missing proof | **Activation** (and **Revenue**) | the buyer never reaches first value because they don't trust the promise |
| risk / "what if it doesn't work for me?" | **Revenue** | risk is what a guarantee neutralizes at the point of purchase |
| fit / "not for someone like me" | **Acquisition → Activation** | wrong-audience signal — the offer's targeting, not the landing page |
| "I'll come back later" / low urgency | **Retention** | the offer gives no reason to return |

The funnel reports the blocker **alongside** the mechanical bottleneck on the same stage, never instead
of it. A stage can have both: a slow checkout page (plumbing) *and* a B0 price objection (demand). Naming
both is the point — the engineer fixes the page, the offer fixes the price, and the report doesn't let
one hide the other.

## Distinguishing a demand blocker from a funnel bottleneck

When a stage leaks, ask which kind of leak it is **before** prescribing:

| Signal | Likely a funnel/page/tracking bottleneck | Likely a DEMAND blocker |
|---|---|---|
| where the evidence comes from | PostHog/Stripe/Meta metrics, session recordings, LCP, error rates | SDV `top_objections[]` in the forecast, real review/comment language |
| what the buyer does | bounces fast, errors out, never sees the page | reads everything, then doesn't buy |
| the fix that moves it | engineering: speed, copy clarity, fix the event/CAPI | the offer: guarantee, proof, or re-price |
| who owns it | funnel-diagnostician / landing-page-builder | irresistible-offer / creative-director |

If checkout CVR is low **and** there's a B0 price objection in the forecast, the page is probably fine —
the offer is mispriced. If checkout CVR is low and there's **no** B-tier blocker on Revenue, look at the
plumbing (broken Stripe flow, missing trust badges, slow page). The SDV ledger is what lets the
diagnostician tell these apart instead of guessing.

## Remedies — one concrete move per tier

Pair every B-tier item with a move, not a diagnosis. These are the same three remedies the SDV ledger
prescribes (`objection-mining.md`):

- **add a guarantee** — risk-reversal that neutralizes the objection (best for risk/"what if it doesn't
  work" objections on **Revenue**),
- **show proof** — testimonial, result, or credential that closes a believability gap (best for
  "does it work?" objections on **Activation**/**Revenue**),
- **re-price** — move to the WTP the price test supports, per
  `skills/synthetic-demand/rules/price-sensitivity.md` (best for "too expensive" objections on
  **Revenue**; let Van Westendorp / Gabor–Granger set the band and the revenue-max point, never guess).

| Tier | Default posture |
|---|---|
| **B0** | Block-clearing move now — it's killing conversion. Usually re-price or add a guarantee. |
| **B1** | Friction reducer — proof or copy that softens the objection. |
| **B2** | Polish — worth doing, not worth blocking a launch on. |

## The ranked revenue-at-risk ledger

The funnel emits the blockers as a single ranked ledger, **B0 above B1 above B2**, each tier sorted by
`revenue_at_risk` descending — most-dollars-at-risk first. `agents/funnel-diagnostician.md` writes this to
`.gtm/sdv/revenue-at-risk.md`. Each row carries: stage, tier, $ at risk, the objection, its representative
verbatim, and the remedy. That ledger is the demand-side companion to the AARRR scorecard: the scorecard
says where the funnel leaks, the ledger says which of those leaks the *offer* is responsible for and what
it costs.

## Fidelity caveat

The B-tiers and their `revenue_at_risk` are only as trustworthy as the forecast's **fidelity tier**
(`skills/synthetic-demand/rules/fidelity-tiers.md`). Below **F3**, the dollar figures are **directional**
— rank the blockers, prioritize the offer work, but don't quote `revenue_at_risk` as a measured number.
A high-fidelity ledger sharpens the bands; it does not make a sub-F3 figure a guarantee. Carry the
forecast's directional label through onto the ledger.

## Common Mistakes

1. **Blaming the page when the offer is the problem.** A low Revenue score with a B0 price objection in
   the forecast is a *pricing* problem, not a checkout-speed problem. Read the ledger before prescribing
   an engineering fix.
2. **Blaming the offer when the plumbing is broken.** The mirror error: if there's no B-tier blocker on
   the leaking stage, it's likely tracking/page/flow — fix the mechanics, don't re-write the offer.
3. **Colliding the axes.** F (fidelity) and B (blocker) and the AARRR stages are three separate things. A
   B0 *lands on* Revenue; it is not "F0" and it does not rename the stage.
4. **Quoting `revenue_at_risk` as measured below F3.** It's `segment.revenue_pct × target_MRR` weighted by
   a directional forecast until F3 calibration — keep the directional label on.
5. **Listing blockers without a remedy.** A B0 with no remedy can't be acted on. Every row gets a
   guarantee / proof / re-price move tied to the stage it lands on.
