# Anchor Sets

## Core Principle

Anchor statements are the **load-bearing calibration** of the whole method — and they are the source
paper's single biggest admitted weakness. Its mapping rode on **6 anchor sets "manually optimized for the
57 [personal-care] surveys,"** and the authors concede "it remains elusive how well they would perform for
other surveys." Point those anchors at a SaaS dev-tool ad or a $500 diagnostic offer and the calibration
is gone. SDV therefore **never hard-codes one anchor set.** It generates, ensembles, and (when possible)
derives anchors from real customer language. This obeys the governing law — **rank, don't score; never ask
a synthetic respondent for a number** — because anchors are how a free-text reaction becomes a Likert
*distribution* in a separate step, with no number ever elicited.

## What an Anchor Set Is

For one construct, an anchor set is **5 short statements — one per Likert point** — expressing
increasing intensity of that construct. The synthetic respondent's free-text reaction is mapped to a
distribution by its similarity to these five.

Properties of good anchors:
- **Monotonic**: point 5 is unambiguously stronger than point 1; each step up increases intensity.
- **Short & generic-within-domain**: a sentence, not a paragraph; reusable across concepts in the domain.
- **Domain-appropriate vocabulary**: how *this* buyer talks (a SaaS dev-tool buyer ≠ a DTC fitness shopper).
- **Separable**: adjacent points are distinct enough that a clear reaction lands cleanly.

Example — `purchase_intent`, generic baseline:

| Point | Anchor |
|-------|--------|
| 1 | "I would definitely not buy this." |
| 2 | "I probably wouldn't buy this." |
| 3 | "I'm on the fence — I might or might not buy it." |
| 4 | "I'd probably buy this." |
| 5 | "I would definitely buy this." |

The generic set is the **cold-start fallback only** (F0). Always specialize it.

## The Three Upgrades Over the Paper

### 1. Auto-generate per construct AND per domain `[robustness]`

Before a run, generate an anchor set for each measured construct *in the concept's domain and buyer
vocabulary*. A `differentiation` anchor for a **SaaS dev-tool ad** ("this does something my current stack
can't") reads nothing like one for a **DTC fitness offer** ("this is a workout plan unlike any I've tried").
Derive the domain from the concept + personas.

### 2. Ensemble multiple sets `[robustness, accuracy↑]`

Generate **3–6 paraphrased sets per construct** (vary phrasing, keep intensity). Map the reaction
against each, then **average the resulting pmfs.** This is exactly what the paper did to stabilize its
mapping (m=6 sets) — averaging over sets cancels the idiosyncrasies of any one wording. Single-set
mapping is fragile; ensembling is the cheap robustness win.

### 3. Derive anchors from real customer language `[robustness]` (F2)

When the project exposes real text — **testimonials, reviews, support tickets, sales-call notes,
PostHog session feedback/recordings, ad comments, churn-survey answers** — mine it for phrases at each
intensity and fold them into the ensemble. Real "I'd have paid double" / "way too expensive for what it is"
lines are better anchors than anything synthesized, because they're in the buyer's actual voice. This is
what promotes a run from F1 to **F2 (data-anchored)**. Record in the forecast which anchors were
data-derived.

## Anchor Templates Per Construct

Specialize each to the domain. Showing point 1 and point 5 as the intensity poles:

| Construct | Point 1 (low) | Point 5 (high) |
|-----------|---------------|----------------|
| purchase_intent | "Definitely wouldn't buy." | "Definitely would buy." |
| appeal | "This doesn't appeal to me at all." | "I love this — it really grabs me." |
| comprehension | "I have no idea what this is or what I'd get." | "Crystal clear what this is and what I get." |
| differentiation | "This is just like everything else out there." | "I've never seen anything that does this." |
| believability | "I don't believe these claims." | "I completely believe this will deliver." |
| price_fairness | "Wildly overpriced for what it is." | "A genuine steal for the value." |
| share_intent | "I'd never mention this to anyone." | "I'd actively recommend this to people." |

(`willingness_to_pay` is elicited via price methods — Van Westendorp + Gabor-Granger — not an anchored
Likert; see `price-sensitivity.md`.)

## How SSR Mode Consumes Anchors

In SSR mode, `scripts/ssr_embed.py` takes the respondent's free-text reaction plus the **ensemble of
anchor sets** (5 statements each), embeds all of them, scores cosine similarity of the reaction against
each anchor, and **averages the per-set pmfs** into the final length-5 distribution. The ensemble is
passed as `anchor_sets` (a list of 5-statement sets); a single flat list of 5 is accepted and treated as
one set. Each set must have exactly 5 statements or the script falls back to FLR. The forecast records
which anchors were **data-derived** (the F1→F2 promotion).

## Validation Before Use

- **Monotonicity check**: confirm the 5 statements form a clear low→high gradient (in SSR mode, the
  pairwise embedding similarities should increase toward the matching pole; in FLR mode, sanity-read them).
- **Anti-collapse**: if generated anchors for adjacent points are near-identical, regenerate — they must
  be separable or the mapping flattens.
- **Domain fit**: read them as the persona. If a phrase sounds like the wrong buyer (a DTC fitness line on
  a dev-tool ad), rewrite it.

## Common Mistakes

1. **Reusing one domain's anchors everywhere.** The paper's core caveat — don't inherit DTC-fitness
   anchors for a SaaS dev-tool concept.
2. **A single anchor set.** Always ensemble; one wording is fragile.
3. **Non-monotonic or overlapping anchors.** Adjacent points must be distinct and ordered.
4. **Over-long, over-specific anchors.** Keep them short and generic-within-domain or they only match
   one phrasing.
5. **Ignoring available real text.** If reviews/tickets/PostHog feedback exist and you synthesized anchors
   anyway, you left the biggest robustness gain — the F2 promotion — on the table.
