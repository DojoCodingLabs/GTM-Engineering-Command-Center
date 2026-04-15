---
name: gtm-metrics
description: "Pull and analyze metrics from Meta, Stripe, Email, SEO, and Google Ads"
argument-hint: "--auto (for routine mode) or channel (meta/stripe/email/seo/google/all)"
---

# Unified Metrics Analysis Command

You are the data-analyst agent. You will pull performance data from all configured channels -- Meta Ads, Stripe, email provider, SEO/organic, and Google Ads -- cross-reference attribution, build a unified dashboard, and generate optimization recommendations.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Determine which data sources are configured:
   - `meta.access_token` + `meta.ad_account_id` -> Meta Ads insights available
   - `posthog.personal_api_key` + `posthog.project_id` -> PostHog analytics available
   - `stripe.secret_key` -> Stripe revenue data available
   - `email.api_key` + `email.provider` -> Email metrics available
   - `google_ads.customer_id` -> Google Ads insights available
3. Test each configured API's connectivity.
4. If `--auto` flag is present (routine mode): skip interactive prompts, pull all available data, save snapshot, check thresholds, and output alerts only.
5. Load existing deployment records from `.gtm/campaigns/` to know which campaigns to query.
   - If no deployment records exist, query accounts directly for all active/recent campaigns.

## Phase 1: Pull Meta Ads Insights

If Meta Ads is configured:

### 1.1: Account-Level Overview

```
GET https://graph.facebook.com/{api_version}/{ad_account_id}/insights
  ?fields=spend,impressions,clicks,cpc,cpm,ctr,actions,cost_per_action_type,conversions,purchase_roas
  &date_preset=last_7d
  &access_token={token}
```

### 1.2: Campaign-Level Breakdown

```
GET https://graph.facebook.com/{api_version}/{ad_account_id}/insights
  ?fields=campaign_id,campaign_name,spend,impressions,clicks,cpc,cpm,ctr,actions,cost_per_action_type,conversions
  &level=campaign
  &date_preset=last_7d
  &filtering=[{"field":"campaign.delivery_info","operator":"IN","value":["active","completed","recently_completed"]}]
  &access_token={token}
```

### 1.3: Ad Set and Ad Level Breakdowns

Pull per-campaign ad set and ad level metrics for detailed analysis.

### 1.4: Parse Actions

Extract from Meta's action arrays:
- `link_click`, `landing_page_view`, `lead`, `purchase`
- `offsite_conversion.fb_pixel_lead`, `offsite_conversion.fb_pixel_purchase`

Calculate derived metrics:
- **CPA** = spend / conversions
- **ROAS** = revenue / spend
- **Landing Page View Rate** = landing_page_views / clicks
- **Conversion Rate** = conversions / landing_page_views

## Phase 2: Pull Stripe Revenue Data

If Stripe is configured:

### 2.1: MRR Calculation

Query Stripe API for active subscriptions:
- List all active subscriptions
- Sum monthly recurring revenue
- Calculate MRR growth vs. previous period

### 2.2: Churn Rate

- Count subscriptions canceled in the period
- Calculate monthly churn rate: canceled / active at period start
- Calculate revenue churn: lost MRR / starting MRR

### 2.3: LTV Estimation

- Average revenue per user (ARPU): MRR / active subscribers
- Estimated LTV: ARPU / monthly churn rate
- LTV:CAC ratio: LTV / CPA (from Meta or blended)

### 2.4: New Revenue Attribution

- New customers in the period
- Revenue from new customers
- Revenue from existing customers (upgrades, expansions)
- Refunds and disputes

Present Stripe metrics:
```
Stripe Revenue Metrics (last 7 days):

| Metric | Value | vs. Last Week |
|--------|-------|---------------|
| MRR | $X | {+/-}% |
| New Customers | {N} | {+/-}% |
| Churn Rate | X% | {+/-}pp |
| ARPU | $X | {+/-}% |
| LTV | $X | {+/-}% |
| LTV:CAC | X:1 | {+/-} |
| Net Revenue | $X | {+/-}% |
```

## Phase 3: Pull Email Metrics

If an email provider is configured:

### 3.1: Provider-Specific Metrics

**Resend**: Query Resend API for email stats:
- Sent, delivered, opened, clicked, bounced
- Per-email and per-sequence performance

**SendGrid**: Query SendGrid Stats API:
- Delivered, opens, clicks, bounces, unsubscribes
- Engagement rates by campaign/automation

**Postmark**: Query Postmark Stats API:
- Similar metrics per message stream

### 3.2: Email Performance Summary

```
Email Metrics (last 7 days):

| Sequence | Sent | Delivered | Opened | Clicked | Conv |
|----------|------|-----------|--------|---------|------|
| Welcome | {N} | {N} ({%}) | {N} ({%}) | {N} ({%}) | {N} ({%}) |
| Activation | {N} | {N} ({%}) | {N} ({%}) | {N} ({%}) | {N} ({%}) |
| Retention | {N} | {N} ({%}) | {N} ({%}) | {N} ({%}) | {N} ({%}) |

Overall:
  Open Rate: {X}% (industry avg: 20-30%)
  Click Rate: {X}% (industry avg: 2-5%)
  Unsubscribe Rate: {X}% (should be <0.5%)
```

## Phase 4: Pull SEO/Organic Metrics

If PostHog or Google Search Console data is available:

### 4.1: Organic Traffic

Query PostHog for non-paid traffic:
- Filter: `$utm_source != "meta"` AND `$utm_source != "google_ads"`
- Pageviews, unique visitors, sessions
- Top landing pages by organic traffic

### 4.2: Search Performance (if GSC configured)

If Google Search Console API access is available:
- Total impressions, clicks, average position
- Top queries by clicks
- Top pages by clicks
- Click-through rate from search

### 4.3: SEO Content Performance

If `.gtm/seo/content/` was deployed:
- Track page views for each SEO content piece
- Compare to pre-deployment baseline (if available)

Present:
```
SEO/Organic Metrics (last 7 days):

| Metric | Value | vs. Last Week |
|--------|-------|---------------|
| Organic Visitors | {N} | {+/-}% |
| Top Organic Page | {page} | {N} views |
| Avg. Time on Page | {X}s | {+/-}% |
| Organic Conversions | {N} | {+/-}% |
```

## Phase 5: Pull Google Ads Metrics

If Google Ads is configured:

- Campaign-level spend, impressions, clicks, conversions
- Search term report (top converting keywords)
- Quality Score distribution
- CPC, CPA, ROAS

## Phase 6: Pull PostHog Analytics

If PostHog is configured:

### 6.1: Event Counts

Query PostHog for key events:
- Pageviews (with UTM filters for each paid channel)
- Signup events
- Purchase/upgrade events
- Custom conversion events

### 6.2: UTM-Filtered Funnels

For each paid channel, query the full funnel:
```
Ad Click -> Page View -> Signup -> Activation -> Purchase
```

Calculate step-by-step conversion rates per channel.

### 6.3: Cross-Channel Attribution

Compare each channel's reported conversions with PostHog's first-party data.

## Phase 7: Unified Dashboard

Combine all data sources into a single dashboard view:

```
GTM Unified Dashboard -- {date range}

REVENUE:  ${mrr}/mo MRR  |  {N} new customers  |  {X}% churn
SPEND:    ${total} across all channels
BLENDED:  ${cpa} CPA  |  {X}x ROAS

Cross-Channel Performance:
| Channel | Spend | Impressions | Clicks | Conv | CPA | Revenue | ROAS |
|---------|-------|-------------|--------|------|-----|---------|------|
| Meta Ads | ${X} | {N} | {N} | {N} | ${X} | ${X} | {X}x |
| Google Ads | ${X} | {N} | {N} | {N} | ${X} | ${X} | {X}x |
| Email | $0 | -- | {N} clicks | {N} | $0 | ${X} | -- |
| Organic/SEO | $0 | {N} | {N} | {N} | $0 | ${X} | -- |
| Direct | $0 | -- | -- | {N} | $0 | ${X} | -- |
| TOTAL | ${X} | {N} | {N} | {N} | ${X} | ${X} | {X}x |

Cross-Channel Attribution:
| Metric | Meta Reports | Google Reports | PostHog (first-party) | Delta |
|--------|-------------|----------------|----------------------|-------|
| Conversions | {X} | {X} | {X} | {diff} |
| Revenue | ${X} | ${X} | ${X} (Stripe) | {diff} |

Top Performer: {channel} -- CPA ${X}, ROAS {X}x
Worst Performer: {channel} -- CPA ${X}, ROAS {X}x
```

### 7.1: Winner/Loser Analysis

Rank all ads/ad sets/emails by primary KPI. Identify:
- **Top 20%**: Scale these
- **Bottom 20%**: Kill or rotate these
- **Creative fatigue signals**: Frequency >3.0, declining CTR, rising CPA

### 7.2: Optimization Recommendations

Generate channel-specific and cross-channel recommendations:

**Budget Recommendations**:
- Shift budget toward highest-ROAS channel
- Kill underperforming campaigns/sequences

**Creative Recommendations**:
- Winning angles to scale
- Fatigued creatives to replace

**Channel-Specific**:
- Meta: targeting, placement, bid adjustments
- Email: subject line, send time, sequence length
- SEO: content updates, new keyword targets
- Outreach: reply rate improvements

## Phase 8: Save Metrics Snapshot

Save the unified metrics to `.gtm/metrics/snapshot-{YYYY-MM-DD}.json`:

```json
{
  "date": "{ISO date}",
  "period": "last_7d",
  "meta": { "spend": 0, "campaigns": [...] },
  "stripe": { "mrr": 0, "churn_rate": 0, "new_customers": 0, "ltv": 0 },
  "email": { "sent": 0, "opened": 0, "clicked": 0, "converted": 0 },
  "seo": { "organic_visitors": 0, "organic_conversions": 0 },
  "google_ads": { "spend": 0, "conversions": 0 },
  "posthog": { "meta_pageviews": 0, "meta_signups": 0, "funnel_rates": {} },
  "unified": {
    "total_spend": 0,
    "total_conversions": 0,
    "blended_cpa": 0,
    "total_revenue": 0,
    "blended_roas": 0
  },
  "attribution_comparison": {},
  "recommendations": []
}
```

## Phase 9: Threshold Check (Auto Mode)

If `--auto` flag is present, check these thresholds against 7-day averages:

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPA increase | >30% vs. 7d avg | ALERT |
| CTR decrease | >25% vs. 7d avg | ALERT |
| Daily spend | >20% over budget | ALERT |
| Email bounce rate | >5% | ALERT |
| Churn rate | >2x monthly avg | ALERT |
| Campaign auto-paused | Any | ALERT |

Save alerts to `.gtm/routines/alerts/alert-{YYYY-MM-DD}.json`.

## Output

```
GTM Metrics Dashboard -- {date range}

{Unified dashboard from Phase 7}

Snapshot saved: .gtm/metrics/snapshot-{date}.json
{Alerts if any}

Next: Run /gtm-learn to save insights, or /gtm-report for a full weekly report.
```

## Error Handling

- **Meta token expired**: Detect error code 190, prompt for new token, STOP.
- **Meta rate limiting**: Wait and retry with backoff (30s, 60s, 120s).
- **Stripe unavailable**: Continue without revenue data. Note: "Stripe data unavailable."
- **Email provider unavailable**: Continue without email data. Note gap.
- **PostHog unavailable**: Continue with channel-native data only. Note: "PostHog data unavailable -- cross-attribution skipped."
- **No campaign data**: Report: "No active campaigns with spend found."
- **Auto mode errors**: Log errors but do not stop. Report partial data with gaps noted.
