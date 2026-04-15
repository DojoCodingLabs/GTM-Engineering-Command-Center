# Cohort Revenue Analysis -- Monthly Cohort Tracking from Stripe

## What Is Cohort Revenue Analysis

Cohort analysis groups customers by their signup month and tracks their revenue behavior over time. This reveals whether your business is truly healthy or if aggregate MRR growth is masking underlying problems.

## Why Cohorts Matter

```
Scenario A: MRR growing 10% MoM
  Looks great in aggregate. But:
  - January cohort: -15% revenue by month 3 (high churn)
  - February cohort: -12% revenue by month 3
  - Growth is 100% from new customers, not retention
  - If acquisition slows, MRR collapses

Scenario B: MRR growing 10% MoM
  - January cohort: +5% revenue by month 3 (expansion)
  - February cohort: +8% revenue by month 3
  - Existing customers are paying more over time
  - Business is fundamentally healthy

Both look identical in aggregate MRR. Cohort analysis reveals the truth.
```

## Building the Cohort Table

### Data Extraction from Stripe

```typescript
async function buildRevenueCohortTable(stripe: Stripe, months: number = 12) {
  // Step 1: Get all customers with their subscription history
  const customers = await fetchAllCustomers(stripe);

  // Step 2: Assign each customer to a cohort (signup month)
  const cohorts: Map<string, CohortData> = new Map();

  for (const customer of customers) {
    const signupMonth = formatMonth(customer.created); // "2026-01"
    if (!cohorts.has(signupMonth)) {
      cohorts.set(signupMonth, { customers: [], monthlyRevenue: {} });
    }
    cohorts.get(signupMonth)!.customers.push(customer.id);
  }

  // Step 3: For each cohort, calculate revenue per month
  for (const [cohortMonth, cohortData] of cohorts) {
    for (const customerId of cohortData.customers) {
      const invoices = await stripe.invoices.list({
        customer: customerId,
        status: 'paid',
        limit: 100,
      });

      for (const invoice of invoices.data) {
        const invoiceMonth = formatMonth(invoice.created);
        const monthsAfterSignup = monthDiff(cohortMonth, invoiceMonth);

        if (monthsAfterSignup >= 0 && monthsAfterSignup < months) {
          const key = `month_${monthsAfterSignup}`;
          cohortData.monthlyRevenue[key] =
            (cohortData.monthlyRevenue[key] || 0) + invoice.total;
        }
      }
    }
  }

  return cohorts;
}
```

### Cohort Table Format

```
Cohort Revenue Table (revenue in $ per cohort per month after signup)

Cohort    | Size | Month 0 | Month 1 | Month 2 | Month 3 | Month 4 | Month 5 | Month 6
----------|------|---------|---------|---------|---------|---------|---------|--------
Jan 2026  | 120  | $3,600  | $3,240  | $3,060  | $2,880  | $2,736  | $2,600  | $2,470
Feb 2026  | 150  | $4,500  | $4,140  | $3,960  | $3,780  | $3,591  | —       | —
Mar 2026  | 180  | $5,400  | $5,076  | $4,878  | $4,682  | —       | —       | —
Apr 2026  | 200  | $6,000  | $5,640  | $5,358  | —       | —       | —       | —

Reading the table:
  - Down the column: How much each cohort generates in month N after signup
  - Across the row: How one cohort's revenue changes over time
  - Declining rows = churn > expansion
  - Growing rows = expansion > churn (ideal)
```

### Normalized Cohort Table (% of Month 0)

```
More useful than absolute numbers. Shows retention as percentage of initial revenue.

Cohort    | Month 0 | Month 1 | Month 2 | Month 3 | Month 4 | Month 5 | Month 6
----------|---------|---------|---------|---------|---------|---------|--------
Jan 2026  | 100%    | 90%     | 85%     | 80%     | 76%     | 72%     | 69%
Feb 2026  | 100%    | 92%     | 88%     | 84%     | 80%     | —       | —
Mar 2026  | 100%    | 94%     | 90.3%   | 86.7%   | —       | —       | —
Apr 2026  | 100%    | 94%     | 89.3%   | —       | —       | —       | —

Interpretation:
  - If Month 12 is > 100% → Net revenue expansion (best-in-class)
  - If Month 12 is 80-100% → Healthy retention
  - If Month 12 is 60-80% → Moderate churn, improvement needed
  - If Month 12 is < 60% → High churn, critical issue
```

## Expansion vs Contraction Revenue

### Tracking Expansion

```
Expansion occurs when a customer in an existing cohort increases their MRR:
  - Plan upgrade (Basic → Pro)
  - Seat increase (5 seats → 10 seats)
  - Add-on purchase (additional feature/product)
  - Usage overage (pay-as-you-go above included amount)

Track expansion per cohort:

Cohort    | Month 0  | Expansion M1 | Expansion M2 | Expansion M3
----------|----------|-------------|-------------|-------------
Jan 2026  | $3,600   | $180 (+5%)  | $120 (+3%)  | $90 (+2.5%)
Feb 2026  | $4,500   | $270 (+6%)  | $180 (+4%)  | —
```

### Tracking Contraction

```
Contraction occurs when a customer decreases their MRR:
  - Plan downgrade (Pro → Basic)
  - Seat decrease (10 seats → 5 seats)
  - Remove add-on

Track contraction separately:

Cohort    | Month 0  | Contract M1 | Contract M2 | Contract M3
----------|----------|------------|------------|------------
Jan 2026  | $3,600   | -$180 (-5%) | -$90 (-2.5%) | -$60 (-1.7%)
```

### Net Revenue Retention by Cohort

```
Net Revenue Retention (NRR) = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR

Per-cohort NRR at month 12:

Cohort    | Starting MRR | Expansion | Contraction | Churn | NRR
----------|-------------|-----------|-------------|-------|-----
Jan 2026  | $3,600      | $720      | -$180       | -$900 | 90%
Feb 2026  | $4,500      | $1,350    | -$225       | -$900 | 105%

February cohort has >100% NRR — customers are paying MORE over time.
This is the sign of a healthy SaaS business.
```

## Cohort Analysis Patterns

### Pattern: Improving Cohort Quality

```
If recent cohorts retain better than older cohorts:
  - Product is improving (better onboarding, better features)
  - Targeting is improving (acquiring better-fit customers)
  - Pricing is better aligned with value

Month 6 retention by cohort:
  Jan: 69% → Feb: 72% → Mar: 75% → Apr: 78%

This is excellent. Your product-market fit is improving.
```

### Pattern: Degrading Cohort Quality

```
If recent cohorts retain worse than older cohorts:
  - Product quality declining or not keeping up
  - Acquisition is reaching less-ideal customers (scaling too fast)
  - Competition is offering alternatives

Month 6 retention by cohort:
  Jan: 80% → Feb: 75% → Mar: 70% → Apr: 65%

This is alarming. Investigate what changed in acquisition or product.
```

### Pattern: Consistent Cohort Curve

```
All cohorts follow the same retention curve:
  Month 1: 90-92%, Month 3: 82-85%, Month 6: 72-75%

This means your product experience is stable.
Focus optimization on:
  1. The steepest drop-off point (usually Month 1 → Month 2)
  2. Expansion revenue (upsell existing cohorts)
```

### Pattern: Bi-Modal Cohorts

```
Some cohorts retain at 90%+, others at 50%.
Correlate with:
  - Acquisition channel (organic cohorts retain better?)
  - Seasonality (holiday signups are less serious?)
  - Pricing changes (free trial vs paid trial?)
  - Product changes (new feature launch affected onboarding?)

This pattern always has a specific cause. Find it.
```

## Cohort Dashboard Visualization

```
Essential cohort views for a GTM dashboard:

1. Revenue Cohort Heatmap
   Rows: Cohort months
   Columns: Months since signup
   Cells: Colored by retention % (green > 90%, yellow 70-90%, red < 70%)

2. Cohort Revenue Waterfall
   Stacked bar chart showing:
   - Starting MRR (green)
   - Expansion (dark green)
   - Contraction (yellow)
   - Churn (red)
   - Ending MRR (blue)

3. NRR Over Time
   Line chart of Net Revenue Retention by cohort month
   Shows trend: improving, stable, or degrading

4. Cohort Size vs Revenue Per Customer
   Are you acquiring more customers or more valuable customers?
   Both is ideal. Size growing but revenue per customer falling = problem.
```

## Segmented Cohort Analysis

### By Acquisition Channel

```
Split cohorts by how the customer was acquired:
  - Organic (SEO, direct) → typically highest retention
  - Paid (Meta, Google) → varies by targeting quality
  - Referral → typically high retention (warm introduction)
  - Partnership → depends on partner quality

If paid cohorts retain 50% worse than organic:
  - Your paid targeting is bringing wrong customers
  - Your ad promise doesn't match product reality
  - You need to improve onboarding for paid-acquired users
```

### By Plan Type

```
Split cohorts by their starting plan:
  - Free → Paid conversion rate + time to convert
  - Trial → Paid conversion rate
  - Monthly → Churn rate (typically higher)
  - Annual → Churn rate (typically lower, committed)
  - Enterprise → Retention + expansion rate

This reveals which pricing structure creates the best customers.
```

### By Geography

```
Split cohorts by customer location:
  - Different markets have different retention patterns
  - LATAM may have higher payment failure rates (card issues)
  - US/EU may have higher ARPU but similar retention
  - Helps decide where to invest marketing budget
```
