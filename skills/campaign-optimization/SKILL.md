---
name: campaign-optimization
description: Campaign optimization methodology — budget allocation, creative testing, scaling playbook, week-by-week ops
---

# Campaign Optimization System

Systematic methodology for optimizing paid acquisition campaigns from launch through scale. Covers the full lifecycle: learning phase management, creative testing, budget allocation, and scaling.

## Week 1-2 Optimization Playbook

### Days 1-3: Learning Phase (DO NOT TOUCH)

Meta's algorithm needs 50 optimization events per ad set per week to exit the learning phase. During days 1-3:

- **Do NOT** change budgets, targeting, or creative
- **Do NOT** kill underperforming ads (insufficient data)
- **Do NOT** duplicate ad sets
- **DO** monitor delivery status (should show "Learning")
- **DO** verify pixel events are firing correctly
- **DO** check that all creative variations are serving impressions

Minimum thresholds before making any decision:
| Metric | Minimum data needed |
|--------|-------------------|
| Impressions per ad | 1,000 |
| Clicks per ad | 50 |
| Conversions per ad set | 15 |
| Spend per ad set | 2x your target CPA |

### Day 4-5: First Read

Review performance but only make minor adjustments:
- Pause any ad with 0 clicks after 500+ impressions (creative is broken, not underperforming)
- Check frequency -- if above 2.0 already, audience is too small
- Verify landing page load time (>3s kills conversion rates)

### Day 7: First Decision Point

After 7 days with sufficient data:

1. **Kill losers**: Pause ad sets with CPA > 2x your target after spending 3x target CPA
2. **Keep runners**: Ad sets within 1-2x target CPA continue for another week
3. **Note winners**: Ad sets below target CPA are candidates for scaling

### Day 10-14: Optimize Winners

- Increase budget on winning ad sets by 20% (never more than 20% at once)
- Create new ad sets with winning creative + new audiences
- Start testing new creative variations against the control
- Build lookalike audiences from converters if you have 100+ conversion events

## Key Performance Metrics

### Primary Metrics (Optimize For)

| Metric | Formula | Good benchmark (EdTech LATAM) |
|--------|---------|-------------------------------|
| CPA (Cost Per Acquisition) | Spend / Conversions | $5-25 (lead), $50-200 (paid user) |
| ROAS (Return on Ad Spend) | Revenue / Spend | 3x+ for sustainable growth |
| CAC (Customer Acquisition Cost) | Total marketing cost / New customers | < 1/3 of LTV |

### Secondary Metrics (Diagnose With)

| Metric | What it tells you | Alarm threshold |
|--------|-------------------|-----------------|
| CTR (Click-Through Rate) | Creative resonance | < 1% = creative problem |
| CPC (Cost Per Click) | Audience + creative quality | > $2 LATAM = targeting issue |
| CVR (Conversion Rate) | Landing page effectiveness | < 2% = page problem |
| CPM (Cost Per 1000 Impressions) | Auction competitiveness | > $15 LATAM = audience too narrow |
| Frequency | Ad fatigue signal | > 3 in 7 days = rotate creative |
| Hook Rate (video) | First 3s retention | < 25% = weak hook |
| Hold Rate (video) | Full video views / impressions | < 5% = content issue |
| Thumb-Stop Ratio | 3s views / impressions | < 20% = visual not stopping scroll |

## Creative Testing Methodology

### Testing Hierarchy

Test in this order (highest impact first):
1. **Angle/Message** -- What pain point or desire are you leading with?
2. **Format** -- Image vs video vs carousel
3. **Hook** -- First line of text, first 3 seconds of video
4. **Visual** -- Colors, composition, faces vs no faces
5. **Copy length** -- Short vs medium vs long primary text
6. **CTA** -- SIGN_UP vs LEARN_MORE vs different CTA text

### Statistical Significance

Never kill a creative without sufficient data:

| Daily budget per ad set | Min days before decision | Min conversions |
|------------------------|------------------------|-----------------|
| $20-50 | 5-7 days | 15 per variant |
| $50-100 | 3-5 days | 25 per variant |
| $100+ | 2-3 days | 50 per variant |

### Winner Criteria

A creative is a "winner" when:
- CPA is at or below target for 3+ consecutive days
- At least 30 conversions tracked
- CTR is above 1.5% (shows broad appeal, not just niche)
- Frequency is below 3 (not just retargeting effects)

### Iteration Process

1. Run 3-5 creative variants per ad set
2. After 7 days, identify the winner
3. Create 3 new variations inspired by the winner (same angle, different execution)
4. Replace the losers with the new variations
5. Repeat weekly -- creative fatigue is the #1 scaling killer

## Budget Allocation Framework

### The 70/20/10 Rule

| Allocation | Purpose | What goes here |
|------------|---------|----------------|
| 70% | Proven performers | Ad sets with CPA below target, scaling |
| 20% | Testing | New audiences, new creative, new angles |
| 10% | Moonshots | Completely new approaches, new platforms |

### Budget Adjustment Rules

- **Never increase budget by more than 20% per day** -- resets learning phase
- **Never decrease budget by more than 50%** -- better to pause entirely
- **Minimum daily budget per ad set**: 2x your target CPA (so Meta can optimize)
- **If CPA spikes after budget increase**: wait 48 hours before reacting
- **If CPA doesn't recover after 72 hours**: roll back budget to previous level

## Scaling Stages

### Stage 1: Validation ($20-50/day per ad set)

Goal: Find winning creative + audience combinations.
- 2-3 ad sets with different audiences
- 3-5 creative variants per ad set
- Success: at least 1 ad set with CPA at target after 7 days

### Stage 2: Optimization ($50-100/day per ad set)

Goal: Optimize and expand what works.
- Scale winning ad sets by 20% every 3 days
- Add 1-2 new audiences per week
- Introduce lookalike audiences (1%, 2%, 3%)
- Success: 3+ ad sets with consistent CPA

### Stage 3: Growth ($100-500/day per ad set)

Goal: Maximize volume while maintaining efficiency.
- Switch to CBO for budget distribution
- Expand to broader audiences (reduce targeting specificity)
- Launch in new geos (test 1 country at a time)
- Success: predictable daily conversion volume

### Stage 4: Scale ($500-1000+/day per ad set)

Goal: Dominate your category.
- Multiple campaigns by objective (conversion + retargeting + awareness)
- Full-funnel approach (TOFU awareness, MOFU consideration, BOFU conversion)
- Creative team producing 5-10 new variants per week
- Risk: CPAs increase 20-40% at scale -- factor this into unit economics
- Success: sustainable ROAS at high volume

## Common Pitfalls

1. **Touching campaigns during learning phase** -- Resets the algorithm, wastes spend
2. **Scaling too fast** -- 2x budget overnight kills performance
3. **Creative fatigue denial** -- If CTR drops 30%+, the creative is tired no matter how good it was
4. **Audience overlap** -- Multiple ad sets competing for the same users inflates CPM
5. **Ignoring frequency** -- Frequency > 5 = you're annoying people, not persuading them
6. **Optimizing for clicks instead of conversions** -- High CTR with low CVR = wrong audience
7. **No exclusions** -- Always exclude existing customers from acquisition campaigns
8. **Weekend panic** -- B2B campaigns naturally dip on weekends, don't panic-pause Friday afternoon
