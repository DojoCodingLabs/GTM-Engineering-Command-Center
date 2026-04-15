# Scaling Playbook: From $20/day to $1000/day

## Overview

Scaling paid acquisition is not linear. Each budget level introduces new challenges that require different strategies. This playbook covers the full journey from validation through scale.

## Phase 1: Validation ($20-50/day)

**Duration:** 2-4 weeks
**Goal:** Find one profitable creative + audience combination
**Risk level:** Low (controlled experimentation)

### Setup

- 2-3 ad sets with different audiences
- 3-5 creative variants per ad set via Advantage+ Creative
- ABO (ad set budget optimization) for precise budget control
- $20-30/day per ad set

### What to Expect

- High CPA volatility (swings of 50-100% day to day are normal)
- Some ad sets will get zero conversions
- Learning phase takes longer at low budgets (7-10 days)
- Algorithm has limited data to optimize

### Decision Framework

| After 7 days... | Action |
|-----------------|--------|
| 1+ ad set with CPA at target | Move to Phase 2 |
| No ad set below 2x target CPA | Change creative or targeting. Do NOT increase budget. |
| All ad sets above 3x target CPA | Fundamental problem: offer, landing page, or market fit. Stop and fix. |

### What Breaks at This Level

- **Nothing** -- this is your safest testing ground
- Only risk: spending too little per ad set (below 2x CPA) prevents the algorithm from learning

## Phase 2: Optimization ($50-100/day per ad set)

**Duration:** 2-4 weeks
**Goal:** Scale winning combinations, find 2-3 profitable ad sets
**Risk level:** Moderate

### How to Enter Phase 2

Prerequisites:
- At least 1 ad set with CPA at or below target for 5+ days
- At least 20 conversions total in the winning ad set
- Clear understanding of which creative angle is working

### Actions

1. **Scale the winner:** Increase budget by 20% every 3 days
2. **Duplicate and test audiences:** Take the winning creative and test it against new audiences:
   - Lookalike 1% of converters (if you have 100+ conversions total)
   - Broader interest targeting
   - New geographic expansion (test 1 new country at a time)
3. **Iterate on creative:** Create 3 new variants of the winning angle
4. **Start building retargeting audiences:** Website visitors, video viewers, engagement custom audiences

### Budget Progression

```
Week 1: $50/day per ad set (2-3 ad sets = $100-150 total)
Week 2: $60/day (20% increase on performers)
Week 3: $72/day
Week 4: $86/day
```

### What Breaks at This Level

- **Creative fatigue starts appearing** -- CTR drops after 2-3 weeks on the same creative. Have new variants ready.
- **Audience overlap** -- Multiple ad sets can compete for the same users, inflating CPM. Use the Audience Overlap tool in Ads Manager to check.
- **Learning phase resets** -- Budget changes larger than 20% or targeting changes restart optimization.

## Phase 3: Growth ($100-500/day per ad set)

**Duration:** 4-8 weeks
**Goal:** Maximize conversion volume while maintaining CPA
**Risk level:** High (meaningful daily spend)

### How to Enter Phase 3

Prerequisites:
- 3+ ad sets with consistent CPA at target for 2+ weeks
- 100+ total conversions in the account
- Lookalike audiences built from converters
- At least 2 proven creative angles
- Retargeting campaigns active

### Actions

1. **Switch to CBO:** Campaign Budget Optimization distributes budget more efficiently across 3+ ad sets
2. **Expand targeting:** Reduce specificity. If you were targeting "software engineering" interests, try broader "technology" or even broad targeting (no interests)
3. **Full-funnel approach:**
   - Campaign 1 (10% budget): Awareness -- video views, reach
   - Campaign 2 (70% budget): Conversion -- your proven ad sets
   - Campaign 3 (20% budget): Retargeting -- website visitors, video viewers
4. **Geographic expansion:** If you started in Colombia, test Mexico. Then Argentina. One at a time.
5. **Creative production:** You need 5-10 new creative variants per week at this level

### Budget Progression

```
Week 1: $150/day total (across 3+ ad sets)
Week 3: $200/day
Week 5: $300/day
Week 7: $400/day
Week 9: $500/day
```

### What Breaks at This Level

- **CPA increases 15-25%** -- This is natural. You've exhausted the easiest-to-convert audiences. Factor this into your unit economics.
- **Creative fatigue accelerates** -- Higher frequency means faster burnout. You need a creative pipeline, not one-off assets.
- **Audience saturation** -- In smaller LATAM markets (Colombia: 50M, Costa Rica: 5M), you can exhaust target audiences faster than in the US. Watch frequency closely.
- **Cash flow pressure** -- At $500/day you're spending $15K/month. Ensure your conversion-to-revenue cycle supports this.

## Phase 4: Scale ($500-1000+/day)

**Duration:** Ongoing
**Goal:** Dominate your category acquisition
**Risk level:** Very high (significant daily commitment)

### How to Enter Phase 4

Prerequisites:
- Profitable unit economics proven over 4+ weeks
- LTV:CAC ratio above 3:1
- Creative production system (not ad-hoc creation)
- Dedicated analytics tracking (PostHog dashboards, UTM discipline)
- Cash reserves to absorb 2-4 weeks of underperformance during scaling

### Actions

1. **Multi-campaign architecture:**
   - Prospecting broad (CBO, broad targeting, all proven creative)
   - Prospecting interest (ABO, specific audiences, testing new creative)
   - Retargeting warm (website visitors 7-30 days)
   - Retargeting hot (cart abandoners, pricing page visitors)
   - Retention/upsell (existing customers, cross-sell)

2. **Automated rules:** Set up Meta's automated rules:
   - Pause ad sets if CPA > 2.5x target after spending 3x CPA
   - Send alert if frequency > 3.5
   - Increase budget 15% if CPA < 0.8x target for 3 days

3. **Cross-platform expansion:**
   - Google Ads (search + YouTube) for high-intent capture
   - TikTok Ads for younger demographics
   - LinkedIn Ads for B2B segments
   - Each platform gets its own Phase 1-2 validation cycle

4. **Reporting cadence:**
   - Daily: CPA, spend, and conversion check (5 minutes)
   - Weekly: full performance review, budget reallocation, creative refresh
   - Monthly: LTV:CAC analysis, channel mix optimization, audience refresh

### What Breaks at This Level

- **CPA increases 20-40%** -- At this volume, you're reaching colder audiences. This is the cost of scale. Your LTV must support it.
- **Creative team becomes bottleneck** -- You need a system: briefs, production, review, launch. One person cannot keep up.
- **Attribution becomes murky** -- Multi-touch attribution, cross-platform overlap, and organic lift make measurement harder. Use incrementality testing if possible.
- **Algorithm dependency** -- Meta's algorithm makes more decisions at this level. A platform algorithm change can swing CPA 30% overnight. Diversify channels.
- **Team needed** -- At $1000+/day ($30K+/month), you need dedicated ad operations. One person reviewing metrics is a single point of failure.

## Scaling Risk Mitigation

### The "Slow Scale, Fast Kill" Rule

- **Scale slowly:** 20% increases every 3 days
- **Kill fast:** If CPA is 3x target after spending 5x CPA, pause immediately

### Budget Rollback Protocol

If CPA spikes after a budget increase:

1. **Wait 48 hours** -- Algorithms need time to recalibrate
2. **If CPA hasn't recovered after 48 hours:** Roll budget back to previous level
3. **Wait 72 hours at the lower budget** to restabilize
4. **Try again** with a 10% increase instead of 20%
5. **If it fails again:** The current ceiling has been reached. Focus on creative refresh or audience expansion before trying to scale further.

### Emergency Shutoff Criteria

Immediately pause all campaigns if:
- Daily spend exceeds 2x your daily budget setting (Meta billing glitch -- rare but happens)
- Zero conversions for 24+ hours across all ad sets (tracking is broken)
- CPA exceeds 5x target across the board (something fundamentally changed)
- Landing page is down or returning errors (check before blaming the ads)

## Scaling Math

```
Monthly budget at $20/day:   $600
Monthly budget at $50/day:   $1,500
Monthly budget at $100/day:  $3,000
Monthly budget at $500/day:  $15,000
Monthly budget at $1000/day: $30,000

At target CPA of $15:
$600/month  = 40 conversions/month
$1,500      = 100
$3,000      = 200
$15,000     = 1,000 (likely lower due to scale CPA increase)
$30,000     = 1,500-2,000 (CPA increases 20-40% at scale)
```

Factor in the CPA increase at scale when building your financial model. Linear extrapolation of Phase 1 CPA is the most common scaling mistake.
