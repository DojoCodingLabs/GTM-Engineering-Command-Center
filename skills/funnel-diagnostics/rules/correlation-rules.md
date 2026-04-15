# Correlation Rules -- Cross-Referencing PostHog + Stripe + Meta + Email Data

## The Correlation Framework

No single data source tells the full story. Diagnosis requires cross-referencing multiple signals. This file defines the correlation rules used to identify root causes.

## Data Source Map

### What Each Source Tells You

```
PostHog:
  - User behavior (pageviews, clicks, feature usage)
  - Funnel conversion rates
  - Session recordings (qualitative)
  - A/B test results
  - Cohort analysis (behavioral segments)

Stripe:
  - Revenue (MRR, ARPU, LTV)
  - Subscription lifecycle (trial, active, churned)
  - Payment success/failure rates
  - Plan distribution (which plans are popular)
  - Upgrade/downgrade patterns

Meta Ads:
  - Campaign performance (CPA, CTR, CPM, ROAS)
  - Audience quality signals
  - Creative performance
  - Frequency and fatigue
  - Audience overlap

Google Ads:
  - Keyword performance (CPC, CTR, Quality Score)
  - Search intent data (what people are searching for)
  - Impression share (market coverage)
  - Conversion tracking (attributed to keywords)

Email Provider (Resend/SendGrid/Postmark):
  - Delivery rates
  - Open/click rates per email
  - Sequence completion rates
  - Unsubscribe rates
  - Bounce rates

Google Search Console:
  - Organic keyword rankings
  - Organic CTR by query
  - Impressions and clicks by page
  - Core Web Vitals field data
```

## Cross-Source Correlation Rules

### Rule 1: Ad Quality vs Landing Page Quality

```
IF: Meta CTR > 1.5% AND Landing page CVR < 2%
THEN: Landing page problem, not ad problem

Verification:
  - PostHog: bounce rate > 60% on landing page
  - PostHog: average time on page < 15 seconds
  - PostHog: session recordings show confusion or immediate exit

IF: Meta CTR < 0.8% AND Landing page CVR > 5%
THEN: Ad creative or targeting problem, not landing page problem

Verification:
  - Meta: frequency > 3 (audience fatigued)
  - Meta: CPM > 2x benchmark (audience too narrow)
  - Meta: creative has been running > 21 days (creative fatigue)
```

### Rule 2: Traffic Quality Assessment

```
IF: CPA from Meta is 2x CPA from Google Search
THEN: Meta traffic is lower quality for this offer

Verification:
  - PostHog: compare activation rates by utm_source
  - Meta users: lower activation %, lower retention
  - Google users: higher activation %, higher retention

Possible explanations:
  - Meta reaches awareness-stage users (need more nurturing)
  - Google Search captures intent-stage users (ready to act)
  - Not a problem if Meta TOFU feeds Google BOFU (attribution lag)

IF: CPA from Meta < CPA from Google AND activation rate is same
THEN: Meta is more efficient for this offer. Scale Meta.
```

### Rule 3: Email Engagement vs Product Engagement

```
IF: Email open rate > 40% AND email click rate > 5% AND activation rate < 20%
THEN: Users engage with email but not with the product. Onboarding problem.

Verification:
  - PostHog: users who open emails have same activation as those who don't
  - Email links lead to the right pages (not broken URLs)
  - Product itself has UX issues independent of email quality

IF: Email open rate < 15% AND activation rate for email-engaged users > 40%
THEN: Deliverability problem. Emails aren't reaching users.

Verification:
  - Email provider: bounce rate, spam complaint rate
  - Check SPF/DKIM/DMARC records
  - Test deliverability with mail-tester.com
```

### Rule 4: Revenue vs Engagement Correlation

```
IF: Feature usage is high AND trial-to-paid < 10%
THEN: Value is clear but price is the objection. Pricing problem.

Verification:
  - Stripe: checkout page visits >> completed payments
  - PostHog: pricing page heatmap shows hesitation
  - Exit surveys or chat logs mention price

IF: Feature usage is low AND trial-to-paid > 20%
THEN: Only highly motivated users convert. Need to lower activation barrier.

Verification:
  - PostHog: power users convert, casual users churn
  - Product complexity is high (steep learning curve)
  - Small, self-selected group of converts (not scalable)
```

### Rule 5: Organic vs Paid Acquisition Quality

```
IF: Organic traffic has 2x activation rate vs paid traffic
THEN: Organic users have higher intent. Invest more in SEO.

Verification:
  - PostHog: segment by utm_medium (organic vs paid)
  - Google Search Console: which organic queries drive signups?
  - Stripe: compare LTV of organic vs paid cohorts

IF: Paid traffic has equal activation but 3x volume
THEN: Paid is scalable even at lower efficiency. Keep scaling.

Verification:
  - CAC for paid still below 1/3 of LTV
  - Paid CPA is stable (not rising with volume)
```

### Rule 6: Churn Root Cause Attribution

```
IF: Churn spikes in Month 2 AND most churned users had low feature usage in Month 1
THEN: Activation failure. Users never found the core value.

Verification:
  - PostHog: feature_used correlation with retention
  - Identify the "aha moment" feature: which features predict retention?
  - Churned users missed 2+ key features

IF: Churn spikes after price increase AND usage metrics are stable
THEN: Price sensitivity. The new price exceeds perceived value.

Verification:
  - Stripe: churn timing correlates with price change date
  - Cancellation reasons mention pricing
  - Downgrade rate also increased (confirms price issue)

IF: Churn is steady 5%/month AND evenly distributed across cohorts
THEN: Normal churn. Focus on acquisition and expansion, not churn reduction.

Verification:
  - No single cause dominates cancellation reasons
  - Churn rate stable for 3+ months
  - Product improvements don't correlate with churn changes
```

## Correlation Analysis Process

### Step 1: Gather Data

```
Pull these datasets for the analysis period (usually last 30 days):

From PostHog:
  - Signup funnel (visit → signup → activation → payment)
  - Feature usage by cohort
  - Session recordings for drop-off points
  - Retention curve (Day 1, 7, 14, 30)

From Stripe:
  - MRR and MRR components (new, expansion, churn)
  - Trial-to-paid conversion rate
  - Payment failure rate
  - Plan distribution

From Meta/Google Ads:
  - CPA, CTR, CPM, ROAS by campaign
  - Spend by campaign
  - Audience size and frequency

From Email:
  - Open rate, click rate by sequence
  - Sequence completion rate
  - Unsubscribe rate

From Google Search Console (if applicable):
  - Organic traffic and keywords
  - CTR by page
```

### Step 2: Normalize Timeframes

```
All data must be aligned to the same time period.
Use 30-day rolling windows for trend analysis.
Use weekly snapshots for granular diagnostics.

Account for attribution delays:
  - Meta: conversions may report 1-7 days after the ad click
  - Google: conversions may report 1-30 days after click
  - Email: opens/clicks within 24-48 hours of send
  - Stripe: revenue at time of payment, not at time of signup
```

### Step 3: Apply Correlation Rules

```
For each funnel stage with below-benchmark performance:
  1. Identify the stage (Acquisition, Activation, Revenue, Retention, Referral)
  2. Pull data from ALL relevant sources for that stage
  3. Apply the correlation rules above
  4. Confirm with qualitative data (session recordings, customer feedback)
  5. Assign root cause
  6. Prescribe fix from bottleneck-patterns.md
```

### Step 4: Prioritize by Impact

```
Impact = (traffic at that stage) x (conversion gap vs benchmark) x (revenue per conversion)

Example:
  Stage: Trial-to-Paid
  Traffic: 500 trial signups/month
  Current CVR: 8%
  Benchmark CVR: 15%
  Revenue per conversion: $30/month MRR

  Impact = 500 x (15% - 8%) x $30 = 500 x 0.07 x $30 = $1,050 MRR/month at stake

This quantifies each bottleneck in dollar terms, making prioritization objective.
```

## Anti-Patterns

```
1. Single-source diagnosis: "CTR is low so the ad is bad"
   → Check landing page quality, audience targeting, and creative freshness too.

2. Survivorship bias: "Our paid users love us (4.8 NPS)"
   → Of course they do. The unhappy ones already churned. Look at churned user feedback.

3. Averages hiding segments: "Average CPA is $15"
   → One campaign has $5 CPA, another has $50. Average is meaningless.

4. Correlation without causation: "Users who use feature X retain better"
   → Maybe they retain because they're power users who would retain anyway.
   Test: prompt non-users to try feature X. If retention improves, it's causal.

5. Vanity metrics: "We got 10,000 signups this month!"
   → How many activated? How many paid? How many retained? Signups alone mean nothing.
```
