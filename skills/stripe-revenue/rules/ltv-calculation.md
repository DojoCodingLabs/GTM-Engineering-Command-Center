# LTV Calculation -- Lifetime Value Formulas, LTV:CAC Ratio, and Payback Period

## LTV Formulas

### Formula 1: Simple LTV (Monthly Subscription)

```
LTV = ARPU / Monthly Churn Rate

Where:
  ARPU = Average Revenue Per User per month (MRR / active subscribers)
  Monthly Churn Rate = % of subscribers who cancel per month

Example:
  ARPU = $30/month
  Monthly churn rate = 5% (0.05)
  LTV = $30 / 0.05 = $600

This customer is worth $600 over their lifetime on average.
```

### Formula 2: LTV with Gross Margin

```
LTV = (ARPU x Gross Margin) / Monthly Churn Rate

Where:
  Gross Margin = Revenue minus cost of goods sold (hosting, support, etc.)
  For SaaS, gross margin is typically 70-85%

Example:
  ARPU = $30/month
  Gross margin = 80% (0.80)
  Monthly churn rate = 5%
  LTV = ($30 x 0.80) / 0.05 = $24 / 0.05 = $480

This is a more conservative and accurate LTV.
```

### Formula 3: LTV with Expansion Revenue

```
LTV = ARPU x Gross Margin x (1 / (Churn Rate - Expansion Rate))

Only valid when Churn Rate > Expansion Rate (otherwise LTV is theoretically infinite).

Example:
  ARPU = $30/month
  Gross margin = 80%
  Monthly churn rate = 5%
  Monthly expansion rate = 2% (upgrades, seat additions)
  Net churn = 5% - 2% = 3%
  LTV = $30 x 0.80 x (1 / 0.03) = $24 x 33.3 = $800

Expansion revenue significantly increases LTV.
```

### Formula 4: Cohort-Based LTV (Most Accurate)

```
Instead of a formula, calculate LTV from actual cohort data:

For each cohort:
  LTV = Sum of all revenue from the cohort / Number of customers in the cohort

Example:
  January 2025 cohort: 100 customers, $72,000 total revenue over 12 months
  Cohort LTV (12-month) = $72,000 / 100 = $720

Extrapolate to full lifetime:
  If Month 12 retention is 60%, and revenue per remaining customer is stable:
  Projected LTV = (12-month revenue) + (remaining_customers x ARPU x avg_remaining_months)

This is the most accurate method because it uses real data, not assumptions.
```

### Formula 5: Probabilistic LTV (Advanced)

```
For each month t in the customer lifecycle:
  Expected_Revenue(t) = Survival_Rate(t) x Expected_ARPU(t)

LTV = Sum from t=0 to infinity of Expected_Revenue(t) / (1 + discount_rate)^t

Where:
  Survival_Rate(t) = probability customer is still active at month t
  Expected_ARPU(t) = expected revenue from active customer at month t (includes expansion)
  discount_rate = monthly discount rate (typically 0.5-1% for SaaS)

This accounts for:
  - Non-linear churn (higher churn in early months, stabilizing later)
  - Revenue expansion over time
  - Time value of money
```

## Calculating ARPU from Stripe

```typescript
async function calculateARPU(stripe: Stripe): Promise<number> {
  let totalMRR = 0;
  let activeSubscriptions = 0;

  let hasMore = true;
  let startingAfter: string | undefined;

  while (hasMore) {
    const response = await stripe.subscriptions.list({
      status: 'active',
      limit: 100,
      ...(startingAfter && { starting_after: startingAfter }),
    });

    for (const sub of response.data) {
      const subMRR = calculateSubscriptionMRR(sub);
      totalMRR += subMRR;
      activeSubscriptions++;
    }

    hasMore = response.has_more;
    if (response.data.length > 0) {
      startingAfter = response.data[response.data.length - 1].id;
    }
  }

  if (activeSubscriptions === 0) return 0;
  return Math.round(totalMRR / activeSubscriptions); // In cents
}
```

## Calculating Churn Rate from Stripe

```typescript
async function calculateMonthlyChurnRate(
  stripe: Stripe,
  startOfMonth: number,
  endOfMonth: number
): Promise<number> {
  // Count subscriptions active at start of month
  // This requires historical data -- use subscription events or snapshots

  // Method: Count cancellations in the month vs active at start
  const cancellations = await stripe.subscriptions.list({
    status: 'canceled',
    created: { gte: startOfMonth, lt: endOfMonth },
    limit: 100,
  });

  const activeAtStart = await stripe.subscriptions.list({
    status: 'active',
    created: { lt: startOfMonth },
    limit: 1, // Just need count
  });

  // Note: This is simplified. For accurate churn, use webhook events
  // to count subscription.deleted events during the period.
  const churnRate = cancellations.data.length / (activeAtStart.data.length || 1);
  return churnRate;
}
```

## LTV:CAC Ratio

### Calculation

```
LTV:CAC = Lifetime Value / Customer Acquisition Cost

Where:
  CAC = Total marketing and sales spend / New customers acquired

Example:
  LTV = $600
  Monthly marketing spend = $10,000
  New customers this month = 50
  CAC = $10,000 / 50 = $200
  LTV:CAC = $600 / $200 = 3:1
```

### Benchmarks

| Ratio | Assessment | Action |
|-------|-----------|--------|
| < 1:1 | Losing money on every customer | Stop spending. Fix product or pricing. |
| 1:1 - 2:1 | Unprofitable or barely breaking even | Reduce CAC or increase LTV urgently. |
| 2:1 - 3:1 | Acceptable but tight | Optimize. Reduce churn, increase ARPU. |
| 3:1 - 5:1 | Healthy | Sweet spot. Scale acquisition. |
| 5:1 - 8:1 | Very healthy | Could invest more in acquisition. |
| > 8:1 | Under-investing in growth | You're leaving growth on the table. Spend more. |

### Segmented LTV:CAC

```
Calculate LTV:CAC by acquisition channel:

Channel      | CAC   | LTV   | Ratio | Verdict
-------------|-------|-------|-------|--------
Organic/SEO  | $15   | $720  | 48:1  | Best channel, invest in content
Google Search| $80   | $650  | 8.1:1 | Very healthy, scale
Meta Ads     | $25   | $500  | 20:1  | Great efficiency, scale
LinkedIn Ads | $200  | $400  | 2:1   | Marginal, optimize or reallocate
Referral     | $10   | $800  | 80:1  | Build referral program

This reveals which channels deserve more budget (high ratio) and which
are burning money (low ratio).
```

## CAC Payback Period

### Calculation

```
CAC Payback Period = CAC / (ARPU x Gross Margin)

Units: months (how many months until you recover the customer acquisition cost)

Example:
  CAC = $200
  ARPU = $30/month
  Gross Margin = 80%
  Monthly Gross Profit per Customer = $30 x 0.80 = $24
  Payback Period = $200 / $24 = 8.3 months
```

### Benchmarks

| Payback Period | Assessment | SaaS Stage |
|---------------|-----------|------------|
| < 6 months | Excellent | Scale aggressively |
| 6-12 months | Good | Healthy growth |
| 12-18 months | Acceptable | For enterprise SaaS only |
| 18-24 months | Concerning | Optimize CAC or increase ARPU |
| > 24 months | Unsustainable | Fix before scaling further |

### Why Payback Period Matters More Than LTV:CAC

```
LTV:CAC can be misleading because LTV plays out over years.
Payback period tells you how much CASH you need to fund growth.

Example:
  LTV:CAC = 5:1 (looks great!)
  But payback period = 18 months

  To acquire 100 customers/month at $200 CAC:
    Monthly spend: $20,000
    Time to recoup: 18 months
    Cash needed before breakeven: $20,000 x 18 = $360,000

  Can you afford to invest $360K before seeing returns?
  If not, a 5:1 LTV:CAC doesn't help.
```

## LTV Improvement Levers

### Reduce Churn (Biggest Impact)

```
Impact of churn reduction on LTV:

At $30 ARPU:
  5% monthly churn → LTV = $600
  4% monthly churn → LTV = $750 (+25%)
  3% monthly churn → LTV = $1,000 (+67%)
  2% monthly churn → LTV = $1,500 (+150%)

Reducing churn from 5% to 3% DOUBLES your LTV.
This is almost always the highest-ROI investment.
```

### Increase ARPU (Second Biggest)

```
ARPU increase methods:
  1. Price increase (simplest, often underutilized)
  2. Upsell to higher tiers (feature gating)
  3. Seat-based pricing (grows with customer's team)
  4. Usage-based component (pay for what you use)
  5. Add-ons and expansions (complementary products)

Impact at 5% churn:
  $30 ARPU → LTV = $600
  $40 ARPU → LTV = $800 (+33%)
  $50 ARPU → LTV = $1,000 (+67%)
```

### Increase Expansion Revenue

```
Expansion revenue offsets churn and can push NRR above 100%:

No expansion:
  Churn 5%, ARPU $30 → LTV = $600

With 2% expansion:
  Net churn 3% (5% - 2%), ARPU $30 → LTV = $1,000

With 4% expansion:
  Net churn 1% (5% - 4%), ARPU $30 → LTV = $3,000

At net-negative churn (expansion > churn), revenue per cohort GROWS over time.
This is the holy grail of SaaS economics.
```

## LTV Monitoring Dashboard

```
Key LTV metrics to track monthly:

1. Overall LTV (Simple formula)
2. LTV by acquisition channel
3. LTV by plan/pricing tier
4. LTV by geography
5. LTV:CAC ratio (overall and by channel)
6. CAC Payback Period
7. Cohort LTV curves (actual vs projected)
8. ARPU trend (monthly)
9. Churn rate trend (monthly)
10. Expansion rate trend (monthly)

Alerts:
  - LTV:CAC drops below 3:1 → Warning
  - Payback period exceeds 12 months → Warning
  - Churn rate increases 2+ consecutive months → Warning
  - ARPU declining 3+ consecutive months → Warning
```

## Common LTV Mistakes

```
1. Using LTV from 6 months of data to justify 24-month payback
   If you only have 6 months of data, your "LTV" is actually "6-month revenue."
   Projecting to full lifetime is speculative. Be conservative.

2. Applying average LTV to all channels
   Organic customers may have 2x the LTV of paid customers.
   Using blended LTV to justify high-CAC channels is dangerous.

3. Ignoring negative unit economics during "growth"
   LTV:CAC of 1.5:1 is not "we'll fix it at scale."
   It's "we lose money on every customer and more customers means more losses."

4. Not updating LTV as product evolves
   LTV from 2024 data may not reflect 2026 product improvements.
   Recalculate quarterly using latest cohort data.

5. Confusing revenue LTV with profit LTV
   LTV should be calculated on gross profit (ARPU x margin), not raw revenue.
   A $100 ARPU with 40% margin has worse LTV than $50 ARPU with 80% margin.
```
