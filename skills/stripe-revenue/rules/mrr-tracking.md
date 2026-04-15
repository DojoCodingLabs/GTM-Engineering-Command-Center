# MRR Tracking -- Calculating and Monitoring Monthly Recurring Revenue from Stripe

## MRR Calculation Algorithm

### Step 1: Fetch Active Subscriptions

```typescript
async function fetchActiveSubscriptions(stripe: Stripe): Promise<Stripe.Subscription[]> {
  const subscriptions: Stripe.Subscription[] = [];
  const statuses: Stripe.Subscription.Status[] = ['active', 'trialing', 'past_due'];

  for (const status of statuses) {
    let hasMore = true;
    let startingAfter: string | undefined;

    while (hasMore) {
      const response = await stripe.subscriptions.list({
        status,
        limit: 100,
        expand: ['data.items.data.price'],
        ...(startingAfter && { starting_after: startingAfter }),
      });

      subscriptions.push(...response.data);
      hasMore = response.has_more;
      if (response.data.length > 0) {
        startingAfter = response.data[response.data.length - 1].id;
      }
    }
  }

  return subscriptions;
}
```

### Step 2: Calculate MRR Per Subscription

```typescript
function calculateSubscriptionMRR(subscription: Stripe.Subscription): number {
  let mrr = 0;

  for (const item of subscription.items.data) {
    const price = item.price;
    const quantity = item.quantity || 1;
    let amount = price.unit_amount || 0; // Amount in cents

    // Normalize to monthly
    if (price.recurring) {
      switch (price.recurring.interval) {
        case 'day':
          amount = amount * 30.44; // Average days per month
          break;
        case 'week':
          amount = amount * 4.33; // Average weeks per month
          break;
        case 'month':
          amount = amount * 1; // Already monthly
          break;
        case 'year':
          amount = amount / 12;
          break;
      }

      // Handle interval_count (e.g., every 3 months)
      if (price.recurring.interval_count > 1 && price.recurring.interval === 'month') {
        amount = amount / price.recurring.interval_count;
      }
    }

    mrr += amount * quantity;
  }

  // Apply discount if present
  if (subscription.discount?.coupon) {
    const coupon = subscription.discount.coupon;
    if (coupon.percent_off) {
      mrr = mrr * (1 - coupon.percent_off / 100);
    } else if (coupon.amount_off) {
      // Normalize discount to monthly if coupon is for the subscription interval
      mrr = Math.max(0, mrr - coupon.amount_off);
    }
  }

  return Math.round(mrr); // Return in cents
}
```

### Step 3: Calculate Total MRR

```typescript
function calculateTotalMRR(subscriptions: Stripe.Subscription[]): {
  total: number;
  byStatus: Record<string, number>;
  byPlan: Record<string, number>;
} {
  const byStatus: Record<string, number> = {};
  const byPlan: Record<string, number> = {};
  let total = 0;

  for (const sub of subscriptions) {
    const mrr = calculateSubscriptionMRR(sub);
    total += mrr;

    // Aggregate by status
    byStatus[sub.status] = (byStatus[sub.status] || 0) + mrr;

    // Aggregate by plan/product
    const planName = sub.items.data[0]?.price?.product?.toString() || 'unknown';
    byPlan[planName] = (byPlan[planName] || 0) + mrr;
  }

  return { total, byStatus, byPlan };
}
```

## MRR Movement Tracking

### MRR Components

```
New MRR:
  Customer subscribed for the first time this period.
  Source: customer.subscription.created webhook where customer has no prior subscriptions.

Expansion MRR:
  Existing customer increased their MRR (upgrade, add seats, add-on).
  Source: customer.subscription.updated webhook where new MRR > old MRR.

Contraction MRR:
  Existing customer decreased their MRR (downgrade, remove seats).
  Source: customer.subscription.updated webhook where new MRR < old MRR.

Churned MRR:
  Customer's subscription ended (cancelled, expired, failed payment).
  Source: customer.subscription.deleted webhook.

Reactivation MRR:
  Previously-churned customer resubscribed.
  Source: customer.subscription.created webhook where customer has prior churned subscriptions.
```

### Tracking MRR Movements via Webhooks

```typescript
// Webhook handler for MRR tracking
async function handleSubscriptionWebhook(event: Stripe.Event) {
  const subscription = event.data.object as Stripe.Subscription;
  const previousAttributes = event.data.previous_attributes as any;
  const currentMRR = calculateSubscriptionMRR(subscription);

  switch (event.type) {
    case 'customer.subscription.created': {
      const hasHistory = await customerHasPriorSubscription(subscription.customer);
      if (hasHistory) {
        // Reactivation
        recordMRRMovement('reactivation', currentMRR, subscription);
      } else {
        // New
        recordMRRMovement('new', currentMRR, subscription);
      }
      break;
    }

    case 'customer.subscription.updated': {
      if (previousAttributes?.items || previousAttributes?.discount) {
        const previousMRR = calculatePreviousMRR(subscription, previousAttributes);
        const delta = currentMRR - previousMRR;

        if (delta > 0) {
          recordMRRMovement('expansion', delta, subscription);
        } else if (delta < 0) {
          recordMRRMovement('contraction', Math.abs(delta), subscription);
        }
      }
      break;
    }

    case 'customer.subscription.deleted': {
      recordMRRMovement('churn', currentMRR, subscription);
      break;
    }
  }
}
```

## MRR Growth Rate

```
MRR Growth Rate = (MRR_end - MRR_start) / MRR_start * 100

Monthly growth rate benchmarks:
  Early stage (< $10K MRR): 15-30% MoM is good
  Growth stage ($10K-100K MRR): 10-20% MoM is good
  Scale stage ($100K-1M MRR): 5-10% MoM is good
  Mature ($1M+ MRR): 3-5% MoM is good

Quick Ratio = (New MRR + Expansion MRR) / (Contraction MRR + Churned MRR)
  > 4.0: Very healthy (growing fast, low churn)
  2.0-4.0: Healthy (sustainable growth)
  1.0-2.0: Concerning (growth barely exceeds losses)
  < 1.0: Shrinking (losing more than gaining)
```

## MRR Dashboard Queries

### Current MRR (Stripe API)

```typescript
// Quick MRR calculation without fetching all subscriptions
// Uses Stripe's billing portal data or manual calculation
async function quickMRR(stripe: Stripe): Promise<number> {
  const now = Math.floor(Date.now() / 1000);
  const thirtyDaysAgo = now - (30 * 24 * 60 * 60);

  // Get all paid invoices in the last 30 days
  const invoices = await stripe.invoices.list({
    status: 'paid',
    created: { gte: thirtyDaysAgo },
    limit: 100,
  });

  // Sum subscription invoice totals (exclude one-time charges)
  let revenue = 0;
  for (const invoice of invoices.data) {
    if (invoice.subscription) {
      revenue += invoice.total;
    }
  }

  return revenue; // This is approximate -- actual MRR needs subscription-level calculation
}
```

### MRR Over Time (Monthly Snapshots)

```
To track MRR over time, store monthly snapshots:

Schema:
  mrr_snapshots:
    id: uuid
    date: date (first of month)
    total_mrr: integer (cents)
    new_mrr: integer
    expansion_mrr: integer
    contraction_mrr: integer
    churned_mrr: integer
    reactivation_mrr: integer
    active_subscriptions: integer
    trial_subscriptions: integer
    past_due_subscriptions: integer

Capture on the 1st of each month (or use a cron job).
```

## Common MRR Calculation Mistakes

```
1. Including one-time charges in MRR
   MRR is RECURRING revenue only. Setup fees, one-time purchases,
   and credits should not be included.

2. Not normalizing annual plans
   A $1,200/year subscription is $100 MRR, not $1,200 MRR.
   Always divide by the billing period.

3. Including cancelled-but-not-yet-expired subscriptions
   If a user cancels but their period hasn't ended, they're still
   contributing MRR until the period end date. Include them.

4. Double-counting trial + paid
   If a trial user converts to paid mid-month, don't count both.
   The trial MRR replaces with paid MRR at conversion.

5. Ignoring discounts
   A $100/month plan with a 50% coupon is $50 MRR, not $100.
   Always apply active discounts.

6. Counting past_due as churned
   Past due means payment failed but subscription is still active.
   Include in MRR (with a separate "at-risk MRR" metric).
   Only count as churn when subscription actually cancels.

7. Using invoice totals instead of subscription amounts
   Invoices may include prorated charges, credits, or one-time items.
   Calculate MRR from subscription items, not invoice totals.
```

## Alerting Rules

```
Set up alerts for these MRR events:

Critical:
  - MRR drops > 5% in a single day (investigate immediately)
  - 3+ enterprise customers churn in a week
  - Payment failure rate exceeds 10% of active subscriptions

Warning:
  - MRR growth rate drops below historical average for 2 consecutive weeks
  - New MRR < Churned MRR for 2 consecutive weeks (net negative)
  - Quick Ratio drops below 2.0

Informational:
  - New milestone reached (next $10K MRR increment)
  - Largest single new subscription or expansion
  - 100th/500th/1000th customer milestone
```
