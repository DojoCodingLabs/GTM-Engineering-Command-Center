# Neural Score Interpretation Guide

## Score Ranges (0-100 Normalized)

| Range | Label | Meaning |
|-------|-------|---------|
| 80-100 | **Exceptional** | Top performer in this batch. Strong neural engagement. Deploy with confidence. |
| 60-79 | **Strong** | Above average. Likely to perform well. Good candidate for deployment. |
| 40-59 | **Average** | Middle of the pack. May work but won't stand out. Consider iterating. |
| 20-39 | **Weak** | Below average. This dimension is dragging the creative down. Needs work. |
| 0-19 | **Poor** | Significantly underperforming. Fundamental issue in this dimension. |

**Remember**: Scores are RELATIVE to the batch being tested. A score of 80 means "best in this set of 5 creatives," not "objectively strong across all ads ever made." Always test 3+ creatives together for meaningful comparison.

## Decision Matrix

| Composite Score | Verdict | Budget Allocation | Action |
|----------------|---------|-------------------|--------|
| 70+ | **DEPLOY** | Full allocation (40-50% of ad set budget) | Ship immediately. This is your lead creative. |
| 55-69 | **TEST** | Reduced allocation (15-25%) | Include as a variant. Let Meta/Google optimize between DEPLOY and TEST. |
| 40-54 | **ITERATE** | 0% — do not deploy | Has potential but needs improvement. See fix guide below. |
| 0-39 | **SKIP** | 0% — kill it | Fundamental problems. Start over with a different angle. |

## Creative Iteration Guide

When a dimension scores below 50, here's how to fix it:

### Low Attention (Visual Cortex < 50)
The creative blends into the feed. The brain's visual processing system isn't engaged.

**Fixes:**
- Increase contrast between background and foreground elements
- Use bolder, more saturated colors (especially in the first 200ms of viewing)
- Add a human face — faces are neurologically prioritized (fusiform face area)
- Use asymmetric layouts instead of centered, predictable compositions
- Add subtle motion (video instead of static, or animated text)
- Increase the size of the primary visual element (hero image, product screenshot)
- Use the "pattern interrupt" technique — something unexpected that breaks visual monotony

### Low Emotion (Amygdala Region < 50)
The creative doesn't trigger an emotional response. The viewer feels nothing.

**Fixes:**
- Switch to a personal story angle (first-person narrative > third-person claims)
- Use PAS framework: make the PAIN vivid and specific before offering the solution
- Add human faces showing emotion (joy, surprise, frustration) — mirror neurons drive empathy
- Use warm color tones (oranges, reds) which activate limbic system more than cool tones
- Include a personal loss/gain framing ("You're losing $X every month" > "Save $X")
- Use social proof with emotional weight ("Maria went from $0 to $47K MRR in 6 months")
- Add aspirational imagery — show the desired end state, not just the product

### Low Memory (Hippocampus < 50)
The creative won't be remembered. The brand is invisible.

**Fixes:**
- Make the logo larger and more prominent (above the fold, not corner-tucked)
- Use brand colors consistently throughout (not just accent — dominant presence)
- Create a distinctive visual signature that's unique to your brand
- Use a memorable tagline or number (brains encode specific numbers better than vague claims)
- Add a repeating visual motif that appears in all your creatives (builds brand pattern recognition)
- Leverage the Von Restorff effect — one element that's dramatically different stands out in memory

### Low Decision (Prefrontal < 50)
The creative doesn't drive action. The viewer isn't considering the offer.

**Fixes:**
- Make the CTA more specific: "Start free trial" > "Learn more"
- Add urgency: "Offer expires Friday" or "Only 50 spots left"
- Include a specific benefit with a number: "Save 14 hours/week" > "Save time"
- Reduce perceived risk: "No credit card required" / "Cancel anytime" / "30-day guarantee"
- Show the value stack: list everything included to make the offer feel overwhelming
- Use direct address: "You" and "your" activate self-referential processing in prefrontal cortex

### Low Comprehension (Wernicke's < 50)
The message isn't landing. The brain's language processing system isn't engaging with the copy.

**Fixes:**
- Simplify copy to 8th-grade reading level (Flesch-Kincaid score > 60)
- Shorten sentences to under 15 words
- Use one idea per creative (not three benefits crammed together)
- Improve visual hierarchy: headline > subheadline > body > CTA (clear reading path)
- Use familiar words, not jargon (unless targeting experts who expect it)
- Add visual cues that guide the eye to the text (arrows, gaze direction of faces)

### Low Reward (Striatum < 50)
The offer doesn't feel valuable. The brain's reward system isn't activating.

**Fixes:**
- Lead with the free/trial/discount angle (reward anticipation)
- Show social proof that others got value ("4.9★ rating from 1,800 users")
- Use before/after framing (show the transformation)
- Make the benefit tangible: "$47/mo for a tool that saves $500/mo" (explicit ROI)
- Add gamification elements if appropriate (badges, progress, achievements)
- Use the word "free" — it's the most powerful reward trigger in advertising

## Cross-Creative Comparison

When comparing creatives side-by-side:

1. **Look at the spread first** — If all creatives score within 5 points of each other, none is clearly better. You need more diverse creative angles.
2. **Identify the dimension driver** — Which dimension creates the biggest score difference? That's what differentiates your creatives.
3. **Don't optimize for one dimension** — A creative that scores 95 on attention but 20 on decision is a "pretty picture that doesn't convert." Balance matters.
4. **The composite matters most** — Individual dimensions inform iteration; the composite determines deployment.

## Calibration Over Time

After running campaigns with neuro-tested creatives:

1. Record: { creative_name, neural_composite, actual_CPA, actual_CTR, actual_conversion_rate }
2. Calculate correlation between neural composite and actual performance
3. If correlation is strong (r > 0.5): the default weights are working
4. If correlation is weak: run a linear regression to find better weights
5. Save updated weights to `.gtm/learnings/neuro-calibration.md`
6. Future neuro-tests use calibrated weights automatically

Expected calibration accuracy:
- After 5 campaigns: rough correlation, ±20% accuracy
- After 15 campaigns: moderate correlation, ±10% accuracy
- After 30+ campaigns: strong correlation, ±5% accuracy (dataset-specific)
