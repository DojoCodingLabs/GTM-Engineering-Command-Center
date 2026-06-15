# Stimulus Design — Show the Buyer What the Buyer Actually Sees

## Core Principle

**Garbage stimulus → garbage forecast.** The synthetic respondent reacts to whatever you show them, so the
stimulus must match *how the buyer actually encounters the surface* — price visible, hook visible, CTA
visible, in context. Abstract descriptions ("an ad about a coding course") inflate scores because they hide
the friction a real buyer feels in-feed and on-page; show the thing **as it is really met.**

This obeys the governing law one layer down:

> **Rank, don't score. Never ask a synthetic respondent for a number.**

A faithful stimulus is what lets a free-text reaction be honest. Loaded or abstracted stimuli manufacture
the very positivity the anti-positivity stack (`rules/elicitation-methods.md`) then has to fight. Build the
stimulus neutral and real, and the reaction — and the ranking it feeds — stays clean.

## Per-Surface Stimulus

Each GTM surface is encountered differently, so each is framed differently. (These are the three wired
surfaces; `feature` is a future seam — see `rules/construct-battery.md`.)

### `ad_creative`
Feed the **rendered creative itself** — the actual image/video as it appears in-feed — through Claude's
vision, **plus the hook and CTA shown on it.** Do **not** paraphrase the asset; the visual carries most of
the signal. The paper used concept slides and noted text-only "mildly reduces performance"; for an ad
creative the pixels *are* the stimulus. Add only minimal context (placement: feed / story / Reels /
banner). Frame the reaction as a **scroll-stopping moment**: "this just appeared in your feed — do you
stop, and do you get it in 2 seconds?" Up-weight `appeal` + `comprehension` (the scorer's `ad_creative`
weights, `rules/construct-battery.md`). The price lives on the landing page, so a creative carries **no
price reveal** and gets **no price test**.

### `offer`
Show the **full offer stack as the buyer sees it on the page**: the promise/outcome, what's included
(the stacked deliverables), the **visible price reveal (prominent)**, the timeframe, any guarantee, and any
proof (testimonials, local results, logos). This is the offer built by `skills/irresistible-offer/` — the
value-anchored "Total value" line, the LATAM odd-pricing ($497/$997), the guarantee tier. Missing the price
or the proof changes the reaction entirely — include what is *really* on the page. A complete offer stimulus
is what **enables the price test** (`rules/price-sensitivity.md`): the anchored Total value seeds the Van
Westendorp `anchor_price`, the odd-pricing points seed the Gabor-Granger sweep.

### `copy`
Show the **headline + landing block in context**, as a section of the page, **not** a bare sentence on its
own. Test wording variants with everything else held constant (see Variant Hygiene). Up-weight
`comprehension` + `believability` (the scorer's `copy` weights). Copy's job is clarity and trust; a headline
read out of its block reads differently than the same headline above the proof and CTA it actually sits with.

## Multimodal Handling

- **FLR (default):** feed the real image/screenshot directly to the vision-capable model for the reaction
  step. The buyer sees pixels; so should the synthetic buyer.
- **SSR (embeddings):** the embedding model is text-only, so **transcribe the asset to a faithful text
  description first** (as the paper did with GPT-4o on concept images), then embed the *reaction*. Still
  generate the reaction from the actual image — only the anchor-mapping step uses text.
- Keep a record of any transcription in the concept/forecast file so runs are reproducible.

## Variant Hygiene (vary one thing; hold format constant)

- **Isolating a driver** (which hook? which headline? which price? which guarantee tier?) → vary **exactly
  one element** across variants, hold everything else constant. Otherwise you can't attribute the win — and
  the comparative ranking, the headline signal, becomes uninterpretable.
- **Choosing overall** (which whole concept?) → vary the whole concept, but keep the **format** of
  presentation identical so you're comparing concepts, not production polish.
- Give variants neutral internal labels (V1/V2/V3). **Never** leak which one you favor into the stimulus.
- Stay on **one surface** per comparison set — the scorer refuses cross-surface ranking
  (`assert_single_surface`), and stimulus hygiene is where that discipline starts: don't pit a creative
  against an offer.

## Priming Separation (leak no evaluation cues)

Keep the two prompts clean and **separate**:

- **Persona priming** = *who the respondent is* (demographics, JTBD, wallet, skeptic stance) — from
  `rules/elicitation-methods.md`. This is the panel's identity.
- **Stimulus** = *what they see* — the `ad_creative` / `offer` / `copy`, exactly as encountered. This is the
  thing under test.

Never write evaluation cues into the stimulus ("rate this amazing offer," "our best-selling course,"
"limited-time deal you'll love"). Loaded framing manufactures positivity and destroys the signal. The
stimulus should be **as neutral as the real-world encounter — and no more flattering.** Persona priming
shapes *who reacts*; it must never bleed an evaluation cue into *what they react to*.

## Common Mistakes

1. **Abstract descriptions instead of the real encounter.** Show the price, the CTA, the proof — the actual
   page, the actual creative.
2. **Paraphrasing an ad instead of feeding the image.** For `ad_creative`, feed the rendered asset to
   vision; the visual is the signal.
3. **An offer stimulus with no visible price reveal.** Then the price test has no anchor and no sweep — and
   the reaction is to a different thing than the buyer meets.
4. **A bare headline instead of the headline in its landing block.** `copy` is tested in context.
5. **Changing several things between variants** so the winner is unattributable — vary exactly one element.
6. **Leaking the favored variant**, or writing flattering framing into the stimulus, or letting persona
   priming bleed an evaluation cue into the stimulus.
7. **Forgetting placement/context** (feed vs. landing vs. pricing page) — context shapes the reaction.
