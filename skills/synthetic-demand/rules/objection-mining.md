# Objection & Driver Mining — The Revenue-at-Risk Ledger

## Core Principle

A low `demand_score` is a dead end. A structured *objection* is a revenue-tagged fix. The paper treated
the free-text rationales personas give as a "byproduct"; for SDV they are a **primary output** — because
they are the only part of the forecast that tells the GTM machine *what to change*. This step turns the
reactions you already have into prioritized, dollar-weighted work.

This is also where the governing law earns its keep:

> **Rank, don't score. Never ask a synthetic respondent for a number.**

You **do not re-poll** the panel for objections. The free-text reactions were already elicited in
character during steps 4–6 of the core loop (and the duels in `rules/comparative-scaling.md`). Mining is
a **pure extraction pass over existing text** — no new calls, and certainly no "rate how much this
objection bothers you 1–5." Severity and frequency are *read out of the reactions you have*, never asked.

## From reactions to structured items

Extract two kinds of structured item. Never carry raw prose downstream.

**Objections** (reasons not to buy):

```
{ segment, objection, severity (high|medium|low), frequency (0–1 of segment) }
```

**Drivers** (reasons they want it):

```
{ segment, driver, strength (high|medium|low) }
```

### The three mining rules

1. **Cluster near-duplicate reactions into one objection with a frequency** — do not list raw quotes.
   "It's too expensive," "I can't justify that price," and "not in my budget" are one objection, not
   three. The cluster's `frequency` is the fraction of the segment whose reaction landed in it (0–1).
2. **Keep exactly ONE representative verbatim per objection** for color. The structured fields drive
   every decision; the quote is human texture for the artifact, nothing more.
3. **Severity ≠ frequency.** `severity` = how hard this objection *blocks the sale* (a hard "no" is
   high; a shrug is low). `frequency` = how *widespread* it is in the segment. A high-severity objection
   held by 5% of a segment is a different problem than a medium-severity one held by 60% — keep them on
   separate axes so the promotion table can weigh both.

Drivers carry only `strength` (no frequency axis) because their job is to feed *what to amplify*, not
what to fix — the strongest drivers per segment become creative and copy hooks, not ledger items.

## Promotion → B-tier blockers

High-impact objections are promoted onto the **B-axis** (B = **Blocker**), GTM's own demand-side tier.

> The B-axis is GTM-native. It deliberately replaces the SRD source's `D0/D1/D2` naming, which collides
> with other tier conventions in this repo. B also never clashes with the **F** fidelity tiers
> (`rules/fidelity-tiers.md`) or HVA's read-ladder rungs — severity lives on its own letter.

| Objection profile | Tier | Meaning |
|---|---|---|
| severity **high** + frequency **≥ 0.4** in a paying segment | **B0 — Demand Blocker** | Kills conversion *now* — fix the offer / copy / proof / price |
| severity **medium**, or lower frequency | **B1 — Demand Friction** | Dampens conversion |
| severity **low** | **B2 — Demand Polish** | Minor lift |

"Paying segment" matters: a B0 is only a B0 when it blocks people who would otherwise *pay*. A loud
objection from a segment that was never going to buy is noise, not a blocker — gate the high+frequent
rule on a revenue-bearing segment.

## Each promoted item carries revenue at risk

Every B-tier item is tagged with the money it threatens, so the funnel can triage by dollars, not by how
loud the objection felt:

```
revenue_at_risk = segment.revenue_pct × target_MRR
```

`target_MRR` is the project's revenue target, read from `.gtm/config.json` (the same revenue figure the
rest of the Command Center plans against). `segment.revenue_pct` is the persona segment's share of that
target — the weighting already used in `rules/elicitation-methods.md` and `rules/comparative-scaling.md`.

So each promoted item carries, at minimum:

| Field | Source |
|---|---|
| `segment` | the persona segment the objection clusters in |
| `tier` | B0 / B1 / B2 from the table above |
| `severity`, `frequency` | read from the clustered reactions |
| `revenue_at_risk` ($) | `segment.revenue_pct × target_MRR` |
| `verbatim` | the one representative quote |
| `remedy` | a suggested fix (below) |

### Suggested remedy

Pair every B-tier item with a concrete next move, not a diagnosis:

- **add a guarantee** (risk-reversal that neutralizes the objection),
- **show proof** (testimonial, result, credential that closes a believability gap), or
- **re-price** to the WTP the price test supports, per `rules/price-sensitivity.md`.

## Where B-tiers go (GTM-native destinations)

The B0/B1/B2 ledger is GTM's own and feeds GTM's own surfaces. It does **not** flow into SRD's
gap-audit by default — that bridge is optional interop, below.

| Destination | What it consumes | What it produces |
|---|---|---|
| `agents/creative-director.md` | the objection + its driver counter-evidence | new creative *angles* that answer the objection head-on |
| `skills/irresistible-offer/` | the objection + suggested remedy | offer-stack layers / guarantees that neutralize it |
| `agents/email-marketer.md` | the ranked objection list | an objection-handling email sequence (one beat per top objection) |
| `agents/funnel-diagnostician.md` *(Phase 6)* | the full B-tier ledger | a revenue-at-risk ledger written to `.gtm/sdv/revenue-at-risk.md`, sorted by `revenue_at_risk` |

The strongest **drivers** ride the same rails in the positive direction: they become the angles
`creative-director` *leads* with and the value layers `irresistible-offer` stacks on.

### Optional Phase-7 interop with SRD

If — and only if — an external `srd/` directory is present, GTM **may additionally** expose this ledger
to SRD's `srd/gap-audit.md` as demand-tagged fix items. This is a one-way courtesy export. GTM **owns**
its B-tier ledger, writes it to `.gtm/sdv/revenue-at-risk.md`, and never depends on SRD being there.
When SRD is absent (the common case), nothing about this step changes.

## Common Mistakes

1. **Dumping raw quotes instead of structured items.** A wall of verbatims is not an objection list.
   Cluster into `{ segment, objection, severity, frequency }`, keep one quote each for color.
2. **Forgetting to tag B0 items with revenue at risk.** A B0 with no `revenue_at_risk` can't be triaged
   by the funnel — the dollar tag is what turns a prediction into prioritized work.
3. **Re-polling instead of mining existing reactions.** The reactions are already in hand from
   elicitation and the duels. Asking the panel a fresh "what are your objections?" round (or worse,
   asking it to rate severity) violates the governing law and adds nothing.
