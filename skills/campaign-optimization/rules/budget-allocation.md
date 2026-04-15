# Budget Allocation Rules

## The 20% Rule

Never increase or decrease an ad set's budget by more than 20% in a single adjustment. Larger changes reset Meta's learning phase, throwing away accumulated optimization data.

### Why 20%?

Meta's algorithm calibrates delivery based on your current budget. A 20% change is gradual enough that the algorithm can adapt without restarting the learning phase. Larger changes trigger a full recalibration.

```
Current budget: $50/day
Max safe increase: $60/day (+20%)
Next day max: $72/day (+20% of $60)
After 5 days of 20% increases: $124/day

This is how you 2.5x a budget in 5 days without breaking performance.
```

### Budget Increase Schedule

| Day | Budget | Change |
|-----|--------|--------|
| 1 | $50 | Starting budget |
| 4 | $60 | +20% (after 3 days of stable CPA) |
| 7 | $72 | +20% |
| 10 | $86 | +20% |
| 13 | $103 | +20% |
| 16 | $124 | +20% |

Wait at least 2-3 days between increases to let the algorithm stabilize.

## CPA Thresholds for Budget Decisions

### When to Increase Budget

All of these must be true:
- CPA is at or below target for 3+ consecutive days
- At least 20 conversions in the last 7 days for the ad set
- Frequency is below 3.0 (audience not saturated)
- No major creative fatigue (CTR hasn't dropped more than 20%)

**Action:** Increase budget by 20%.

### When to Maintain Budget

Any of these are true:
- CPA is within 1-1.5x of target
- Ad set has fewer than 15 conversions (insufficient data)
- Budget was changed in the last 48 hours (still stabilizing)

**Action:** Do nothing. Wait for more data.

### When to Decrease Budget

Any of these are true:
- CPA is above 2x target for 3+ consecutive days after spending at least 3x target CPA
- Frequency above 4.0 (audience exhaustion)
- CTR dropped below 0.5% (creative completely exhausted)

**Action:** Reduce budget by 20% or pause the ad set entirely if the trend persists.

### When to Pause (Not Decrease)

- CPA above 3x target after spending 5x target CPA
- Zero conversions after spending 2x target CPA
- Creative has been running 30+ days with declining performance

**Action:** Pause the ad set. Reducing budget on a dying ad set just prolongs the loss.

## The 70/20/10 Allocation Framework

### 70% -- Proven Performers

Allocate the majority of budget to ad sets and campaigns with proven, predictable performance.

Criteria for "proven":
- Running for 14+ days
- CPA consistently at or below target
- 50+ total conversions
- Stable creative (not declining)

### 20% -- Testing

Allocate testing budget to new audiences, new creative, new angles.

Testing rules:
- Each test ad set gets exactly 2x your target CPA per day as budget (minimum viable spend)
- Run each test for exactly 7 days before making decisions
- Only test one variable at a time (new audience OR new creative, not both)
- Maximum 3 tests running simultaneously per campaign

### 10% -- Moonshots

Allocate a small amount to completely new approaches:
- New platforms (TikTok, LinkedIn, YouTube)
- Radically different creative formats (UGC vs polished, video vs static)
- New market segments or geos
- Experimental offers or pricing

The 10% is allowed to fail. Its purpose is discovering the next 70%.

## Budget Pacing

### Daily Budget vs Lifetime Budget

| Feature | Daily Budget | Lifetime Budget |
|---------|-------------|----------------|
| Spend control | Predictable daily spend | May front-load or back-load |
| Algorithm flexibility | Less flexible | More flexible (can spike on good days) |
| Best for | Ongoing campaigns | Fixed-date promotions, events |
| Reporting | Easier to track | Harder to compare day-over-day |

**Recommendation:** Use daily budgets for evergreen campaigns. Use lifetime budgets only for campaigns with hard end dates (product launches, seasonal promotions).

### Minimum Viable Budget Per Ad Set

```
Minimum daily budget = 2 x target CPA

Example:
  Target CPA: $15
  Minimum daily budget: $30 per ad set
  With 3 ad sets: $90/day minimum campaign budget
```

Below this threshold, Meta's algorithm cannot optimize effectively. You'll get sporadic delivery and unreliable data.

### Campaign Budget Distribution (CBO)

When using Campaign Budget Optimization, Meta distributes budget across ad sets automatically. You can guide this with limits:

```json
{
  "daily_min_spend_target": 1500,  // Ensure at least $15/day
  "daily_spend_cap": 8000          // No more than $80/day
}
```

Use min/max limits to:
- Prevent one ad set from starving others
- Cap a proven performer if you want to test others
- Ensure new ad sets get enough spend to exit learning

## Weekly Budget Review Checklist

Every Monday, review the previous week's performance:

1. **Calculate blended CPA** across all active ad sets
2. **Identify top 3 performers** (lowest CPA with 10+ conversions)
3. **Identify bottom 3 performers** (highest CPA with sufficient spend)
4. **Check frequency** across all ad sets (any above 3.5?)
5. **Review creative CTR trends** (any declining more than 20% week-over-week?)
6. **Decide:**
   - Increase budget on top performers (if headroom exists)
   - Decrease or pause bottom performers
   - Launch new tests to replace paused ad sets
7. **Log the decision** with rationale for future reference

## Anti-Patterns

- **Doubling budget overnight** -- Resets learning, CPA spikes, then you panic-pause. Loses money twice.
- **Micro-managing daily** -- Changing budgets every day prevents the algorithm from optimizing. Check every 3 days max.
- **Setting budget too low to learn** -- $10/day when your CPA is $20 means the algorithm can never get enough conversions to optimize. Budget must be at least 2x CPA.
- **Not pausing losers** -- Reducing a losing ad set's budget from $50 to $10 just loses $10/day slowly instead of $50/day quickly. Pause and reallocate.
- **Ignoring creative refresh** -- Budget increases cannot fix creative fatigue. If CTR is dying, no amount of budget will save it. New creative first, then scale.
