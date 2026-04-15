# Creative Testing Methodology

## Minimum Sample Sizes Before Decisions

Never kill a creative without statistically meaningful data. Here are the minimum thresholds:

### By Metric

| Metric | Minimum impressions | Minimum events | Confidence |
|--------|-------------------|-----------------|------------|
| CTR (click-through rate) | 1,000 per variant | 10 clicks | Directional |
| CPC (cost per click) | 2,000 per variant | 30 clicks | Moderate |
| CVR (conversion rate) | 5,000 per variant | 20 conversions | Moderate |
| CPA (cost per acquisition) | N/A | 30 conversions | High |
| ROAS (return on ad spend) | N/A | 50 conversions | High |

### By Budget Level

| Daily budget per ad set | Min days before killing | Min conversions per variant |
|------------------------|------------------------|---------------------------|
| $20-30 | 7 days | 15 |
| $30-50 | 5 days | 20 |
| $50-100 | 3-5 days | 30 |
| $100+ | 2-3 days | 50 |

## CTR Benchmarks by Vertical

These are benchmarks for Meta Ads. Performance below "poor" indicates a creative or targeting problem.

| Vertical | Poor | Average | Good | Excellent |
|----------|------|---------|------|-----------|
| EdTech | <0.8% | 1.0-1.5% | 1.5-2.5% | >3.0% |
| B2B SaaS | <0.5% | 0.8-1.2% | 1.2-2.0% | >2.5% |
| E-commerce | <0.8% | 1.0-1.5% | 1.5-2.5% | >3.0% |
| Consumer apps | <1.0% | 1.5-2.5% | 2.5-4.0% | >4.0% |
| Financial services | <0.4% | 0.6-1.0% | 1.0-1.5% | >2.0% |
| Fitness/wellness | <0.8% | 1.2-2.0% | 2.0-3.5% | >4.0% |

### LATAM-Specific Adjustments

LATAM markets typically see 10-30% higher CTRs than US/EU due to:
- Lower ad saturation in the market
- Higher social media engagement rates
- More responsive to aspirational messaging

Adjust benchmarks upward by ~20% when running in CO, MX, AR, BR.

## Creative Testing Framework

### Phase 1: Angle Testing (Week 1-2)

Test fundamentally different messages to find which angle resonates:

| Variant | Angle | Example headline |
|---------|-------|-----------------|
| A | Pain point | "Tired of job rejections?" |
| B | Aspiration | "Build your dream career in tech" |
| C | Social proof | "2,400 graduates now earning $80K+" |
| D | Urgency | "Only 30 spots left in March cohort" |
| E | Authority | "The #1 rated bootcamp in LATAM" |

**Decision:** After 7 days with sufficient data, identify the top 2 angles. Kill the bottom 3.

### Phase 2: Hook Testing (Week 3-4)

Take the winning angle and test different hooks (first line / first 3 seconds):

| Variant | Hook style | Example |
|---------|-----------|---------|
| A | Question | "What if you could land a dev job in 90 days?" |
| B | Stat | "87% of bootcamp grads fail technical interviews." |
| C | Story | "Last year, Maria was a teacher making $800/month..." |
| D | Command | "Stop applying to jobs you're not qualified for." |
| E | Controversy | "College degrees are a waste of time for developers." |

**Decision:** After 7 days, keep top 2 hooks. These become your control creatives.

### Phase 3: Visual Testing (Week 5-6)

With the winning angle + hook, test different visual approaches:

| Variant | Visual | Notes |
|---------|--------|-------|
| A | Testimonial photo (face) | Real person, candid, not stock |
| B | Screenshot/product | Show the actual product interface |
| C | Text-heavy graphic | Bold headline on colored background |
| D | Before/After | Split layout showing transformation |
| E | Video (15-30s) | Same hook as winning static, but animated |

**Decision:** After 7 days, keep top 2 visuals. Combine with winning hooks for final creative suite.

### Phase 4: Iteration (Ongoing)

Every 2-3 weeks, create 3 new variations of the winning creative:
- Same angle and hook, different execution
- New testimonials or case studies
- Seasonal or topical updates
- Format experiments (carousel, Reels, etc.)

## When to Kill a Creative

### Immediate Kill (Don't Wait for Full Data)

- Zero clicks after 500+ impressions (the creative is not being seen as relevant)
- 1,000+ impressions with CTR below 0.3% (fundamentally broken creative)
- All budget going to one variant in Advantage+ (other variants getting zero delivery)

### Scheduled Kill (After Minimum Data)

- CPA above 2x target after spending 3x target CPA
- CTR declined 30%+ week-over-week (creative fatigue)
- Frequency above 3.5 (same people seeing it too many times)
- Negative comments/reactions outnumbering positive engagement

### Never Kill

- A creative that's still within target CPA, even if CTR is below benchmark (conversions matter more than clicks)
- A creative with fewer than 15 conversions (insufficient data)
- A creative during its first 72 hours (learning phase)

## Creative Fatigue Detection

### Leading Indicators (Act Before It's Too Late)

| Signal | Warning threshold | Critical threshold |
|--------|------------------|-------------------|
| CTR declining WoW | -15% | -30% |
| CPM increasing WoW | +20% | +40% |
| Frequency | 2.5 | 3.5+ |
| Negative feedback rate | Any increase | 2x increase |

### Creative Refresh Cadence

| Daily spend level | Refresh frequency | Variants to add |
|-------------------|-------------------|----------------|
| $20-50/day | Every 3-4 weeks | 2-3 new variants |
| $50-200/day | Every 2-3 weeks | 3-5 new variants |
| $200-500/day | Every 1-2 weeks | 5-7 new variants |
| $500+/day | Weekly | 5-10 new variants |

## Testing Documentation Template

Log every test for institutional knowledge:

```
Test Name: [Descriptive name]
Date Range: [Start - End]
Hypothesis: [What we expected]
Variable Tested: [Angle / Hook / Visual / Copy length / CTA]
Control: [Description of baseline creative]
Variants: [List each variant]
Budget Per Variant: [$X/day]
Results:
  - Variant A: CPA $XX, CTR X.X%, XX conversions
  - Variant B: CPA $XX, CTR X.X%, XX conversions
  - Control: CPA $XX, CTR X.X%, XX conversions
Winner: [Which variant won]
Learning: [What we learned for future tests]
Next Action: [Scale winner / Test new variable / Iterate]
```

Keep a running log of all tests. Patterns emerge over time that inform your creative strategy.
