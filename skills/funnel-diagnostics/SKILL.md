---
name: funnel-diagnostics
description: Funnel diagnostics engine — bottleneck detection, cross-data correlation, AARRR benchmarks by vertical
---

# Funnel Diagnostics Engine

Diagnose conversion bottlenecks by cross-referencing data from PostHog, Stripe, Meta Ads, Google Ads, and email platforms. This skill provides the inference rules that power automated funnel analysis.

## The AARRR Framework

```
Acquisition → Activation → Revenue → Retention → Referral

Each stage has:
  - A defining event (what counts as completing this stage)
  - A conversion rate to the next stage
  - Benchmarks by vertical
  - Diagnostic patterns when rates are below benchmark
```

### Stage Definitions

| Stage | Defining Event | What It Measures |
|-------|---------------|-----------------|
| Acquisition | User visits site (unique visitor) | Can you attract people? |
| Activation | User completes key action (signup + first value moment) | Do they "get it"? |
| Revenue | User pays (first payment) | Will they pay? |
| Retention | User returns (active in week 2+) | Do they stay? |
| Referral | User invites others (share, invite, review) | Do they spread? |

## Diagnostic Process

### Step 1: Map the Funnel

Identify the specific events for each AARRR stage in the target product:

```
Example (Coding Bootcamp):
  Acquisition: $pageview on /landing (UTM-tagged)
  Activation: onboarding_completed
  Revenue: payment_completed (Stripe checkout.session.completed)
  Retention: course_lesson_completed in week 2+
  Referral: referral_link_shared or invite_sent
```

### Step 2: Pull Conversion Rates

For each stage transition, calculate the conversion rate over the last 30 days:

```
Acquisition → Activation:  visitors → activated / visitors
Activation → Revenue:      activated → paid / activated
Revenue → Retention:       paid → retained_week4 / paid
Retention → Referral:      retained → referred / retained
```

### Step 3: Compare to Benchmarks

See the AARRR benchmarks rule file for industry-specific benchmarks.

### Step 4: Identify the Bottleneck

The stage with the largest gap between actual and benchmark performance is the bottleneck. Focus all optimization effort here.

### Step 5: Apply Diagnostic Patterns

Each bottleneck has specific diagnostic patterns. See the bottleneck-patterns rule file.

## Data Sources for Diagnosis

| Data Source | What It Provides | Key Signals |
|-------------|-----------------|-------------|
| PostHog | User behavior, funnels, session recordings | Drop-off points, rage clicks, dead clicks |
| Stripe | Revenue, subscriptions, churn | MRR, trial conversion, payment failures |
| Meta Ads | Ad performance, audience quality | CPA, CTR, CPM, frequency |
| Google Ads | Search intent, keyword performance | Quality Score, impression share, CPC |
| Email Provider | Engagement, sequence performance | Open rate, click rate, unsubscribe rate |
| Google Search Console | Organic visibility | CTR, position, impressions |

## Cross-Data Correlation

### The Correlation Matrix

When diagnosing a bottleneck, correlate data across sources to identify root cause:

```
High CPA + Low CVR = Landing page problem (traffic quality is fine, page doesn't convert)
High CPA + High CVR = Targeting problem (converting users are expensive to reach)
Low CPA + Low CVR = Misaligned offer (cheap traffic but wrong audience)
Low CPA + High CVR = Working well (scale this)

High Open Rate + Low Click Rate = Email content problem (subject line works, body doesn't)
Low Open Rate + Any Click Rate = Deliverability or subject line problem
High Click Rate + Low CVR = Landing page problem (email works, page doesn't)
```

## Severity Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| Critical | Conversion rate <50% of benchmark AND >$1000/month at stake | Fix immediately, pause spend if needed |
| High | Conversion rate 50-75% of benchmark | Fix this week |
| Medium | Conversion rate 75-90% of benchmark | Fix this month |
| Low | Conversion rate 90-100% of benchmark | Optimize when bandwidth allows |
| None | At or above benchmark | Monitor, don't touch |

## Reporting Template

### Weekly Funnel Health Report

```
FUNNEL HEALTH: [DATE RANGE]

Stage          | Actual | Benchmark | Status    | Trend
Acquisition    | 2,400  | --        | --        | +12% WoW
Acq → Act      | 18%    | 20-30%    | Medium    | Flat
Act → Revenue  | 3.2%   | 5-10%     | Critical  | -0.8% WoW
Rev → Retain   | 72%    | 70-80%    | Healthy   | +2% WoW
Retain → Refer | 4%     | 5-15%     | Medium    | Flat

BOTTLENECK: Activation → Revenue
ROOT CAUSE: [diagnosis from patterns]
PRESCRIPTION: [from prescription rules]
```
