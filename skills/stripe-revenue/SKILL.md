---
name: stripe-revenue
description: Stripe revenue intelligence — MRR tracking, cohort analysis, LTV calculation, churn diagnostics from Stripe API
---

# Stripe Revenue Intelligence

Extract, calculate, and analyze revenue metrics from the Stripe API. This skill covers MRR computation, cohort analysis, LTV calculation, and churn diagnostics for SaaS businesses.

## Stripe API Fundamentals for Revenue

### Key Objects

| Object | What It Represents | Key Fields |
|--------|--------------------|-----------|
| `Customer` | A paying or trial user | `id`, `email`, `created`, `metadata` |
| `Subscription` | Recurring billing relationship | `status`, `current_period_start/end`, `items`, `cancel_at` |
| `Invoice` | A billing event | `total`, `status`, `paid`, `period_start/end`, `subscription` |
| `PaymentIntent` | A payment attempt | `amount`, `status`, `created`, `customer` |
| `Charge` | A completed payment | `amount`, `paid`, `refunded`, `customer` |
| `Price` | A pricing configuration | `unit_amount`, `recurring.interval`, `product` |
| `Product` | What you sell | `name`, `metadata`, `active` |

### Subscription Statuses

| Status | Meaning | Count as Active? |
|--------|---------|-----------------|
| `trialing` | In free trial period | Yes (for activation metrics) |
| `active` | Paying and current | Yes |
| `past_due` | Payment failed, retrying | Yes (grace period) |
| `unpaid` | All retries failed | No |
| `canceled` | User cancelled | No |
| `incomplete` | First payment failed | No |
| `incomplete_expired` | First payment expired | No |
| `paused` | Subscription paused | No |

### Authentication

```bash
STRIPE_SECRET_KEY=sk_live_XXXXXX     # Server-side only, never in frontend
STRIPE_PUBLISHABLE_KEY=pk_live_XXXXX # Safe for frontend
STRIPE_WEBHOOK_SECRET=whsec_XXXXXX   # For webhook signature verification
```

## MRR Calculation

### Basic MRR Formula

```
MRR = Sum of (subscription.items[].price.unit_amount * quantity)
      for all subscriptions where status in ['active', 'trialing', 'past_due']
      normalized to monthly
```

### Normalization Rules

| Billing Interval | Normalization |
|-----------------|---------------|
| Monthly | amount as-is |
| Quarterly | amount / 3 |
| Semi-annual | amount / 6 |
| Annual | amount / 12 |
| Weekly | amount * 4.33 |

### MRR Components

```
New MRR:        MRR from customers who subscribed this month
Expansion MRR:  MRR increase from upgrades, add-ons, quantity increases
Contraction MRR: MRR decrease from downgrades, quantity decreases
Churned MRR:    MRR lost from cancelled subscriptions
Reactivation MRR: MRR from previously-churned customers who resubscribed

Net New MRR = New + Expansion + Reactivation - Contraction - Churned
```

### Fetching Active Subscriptions

```bash
# List all active subscriptions (paginate with starting_after)
GET /v1/subscriptions?status=active&limit=100

# Include trialing and past_due for complete MRR picture
GET /v1/subscriptions?status=active&limit=100
GET /v1/subscriptions?status=trialing&limit=100
GET /v1/subscriptions?status=past_due&limit=100
```

### MRR Calculation Algorithm

```
For each subscription:
  1. Sum all subscription items: item.price.unit_amount * item.quantity
  2. Normalize to monthly based on price.recurring.interval
  3. Apply any discount (subscription.discount or coupon)
  4. Add to running MRR total

Discount handling:
  - percent_off: MRR * (1 - percent_off / 100)
  - amount_off: MRR - (amount_off / interval_months)
  - Check coupon.duration: 'forever', 'once', 'repeating'
```

## Key Revenue Metrics

| Metric | Formula | Healthy Range (SaaS) |
|--------|---------|---------------------|
| MRR Growth Rate | (MRR_now - MRR_prev) / MRR_prev | 10-20% MoM (early), 5-10% (growth) |
| Net Revenue Retention | (MRR_start + expansion - contraction - churn) / MRR_start | >100% (best-in-class >120%) |
| Gross Churn Rate | Churned MRR / Starting MRR | <5% monthly, <3% ideal |
| ARPU | Total MRR / Active Subscribers | Trending up = good |
| LTV | ARPU / Monthly Churn Rate | >3x CAC minimum |
| LTV:CAC Ratio | LTV / CAC | 3:1 minimum, 5:1+ ideal |
| CAC Payback Period | CAC / (ARPU * Gross Margin) | <12 months |
| Quick Ratio | (New + Expansion) / (Contraction + Churn) | >4 = very healthy |
| Trial-to-Paid Rate | Paid conversions / Trial starts | 15-30% |

## Webhook Events for Real-Time Tracking

| Event | What Happened | Action |
|-------|---------------|--------|
| `customer.subscription.created` | New subscription started | Track new MRR |
| `customer.subscription.updated` | Plan change, quantity change | Track expansion/contraction |
| `customer.subscription.deleted` | Subscription cancelled | Track churned MRR |
| `invoice.paid` | Payment succeeded | Confirm revenue |
| `invoice.payment_failed` | Payment failed | Alert, track at-risk MRR |
| `customer.subscription.trial_will_end` | Trial ending in 3 days | Trigger conversion email |
| `checkout.session.completed` | Checkout completed | Track new customer |

## Churn Analysis

### Churn Types

| Type | Signal | Intervention |
|------|--------|-------------|
| Voluntary | Customer cancels via UI/support | Exit survey, save offer, win-back sequence |
| Involuntary | Payment fails, card expires | Dunning emails, card update prompts, retry logic |
| Downgrade | Customer moves to cheaper plan | Understand why, improve value prop |
| Trial Churn | Trial expires without conversion | Better onboarding, trial extension offer |

### Involuntary Churn Prevention

Stripe's Smart Retries handle some of this, but supplement with:

1. **Pre-dunning**: Email 7 days before card expires (use `customer.source.expiring` event)
2. **Failed payment**: Email immediately with card update link
3. **Retry 1** (Day 1): Automatic Stripe retry
4. **Retry 2** (Day 3): Email "action required" with urgency
5. **Retry 3** (Day 5): Email "last chance" before service interruption
6. **Final** (Day 7): Pause/cancel subscription, send win-back email

## Environment Variables

```bash
STRIPE_SECRET_KEY=sk_live_XXXXXX          # For API calls
STRIPE_WEBHOOK_SECRET=whsec_XXXXXX        # For webhook verification
STRIPE_PUBLISHABLE_KEY=pk_live_XXXXXX     # For frontend (Checkout, Elements)
```
