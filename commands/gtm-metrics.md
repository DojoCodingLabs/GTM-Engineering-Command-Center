---
description: "Pull and analyze campaign metrics from Meta + PostHog"
argument-hint: ""
---

# Metrics Analysis Command

You are the data-analyst agent. You will pull campaign performance data from Meta Ads and PostHog, cross-reference attribution, identify winners and losers, and generate actionable optimization recommendations.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate required credentials:
   - `meta.access_token` — required for Meta Ads insights
   - `meta.ad_account_id` — required
   - `posthog.personal_api_key` — required for PostHog analytics (warn if missing, continue with Meta-only)
   - `posthog.project_id` — required for PostHog
   - `posthog.host` — required for PostHog API calls
3. Test Meta access token:
   - GET `https://graph.facebook.com/{api_version}/me?access_token={token}`
   - If expired, tell the user to refresh and STOP.
4. Load existing deployment records from `.gtm/campaigns/` to know which campaigns to query.
   - If no deployment records exist, query the ad account directly for all active/recent campaigns.

## Phase 1: Pull Meta Ads Insights

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

### 1.3: Ad Set-Level Breakdown

For each campaign of interest:
```
GET https://graph.facebook.com/{api_version}/{campaign_id}/insights
  ?fields=adset_id,adset_name,spend,impressions,clicks,cpc,cpm,ctr,actions,cost_per_action_type,frequency
  &level=adset
  &date_preset=last_7d
  &access_token={token}
```

### 1.4: Ad-Level Breakdown

```
GET https://graph.facebook.com/{api_version}/{campaign_id}/insights
  ?fields=ad_id,ad_name,spend,impressions,clicks,cpc,cpm,ctr,actions,cost_per_action_type
  &level=ad
  &date_preset=last_7d
  &access_token={token}
```

### 1.5: Parse Actions

Meta returns actions as an array of `{action_type, value}` objects. Extract:
- `link_click` — link clicks
- `landing_page_view` — actual page loads
- `lead` — leads (if objective is lead gen)
- `purchase` — purchases (if objective is sales)
- `offsite_conversion.fb_pixel_lead` — pixel-tracked leads
- `offsite_conversion.fb_pixel_purchase` — pixel-tracked purchases
- `app_custom_event.*` — custom conversion events

Calculate derived metrics:
- **CPA** = spend / conversions (for the target action type)
- **ROAS** = revenue / spend (if purchase value available)
- **Landing Page View Rate** = landing_page_views / clicks
- **Conversion Rate** = conversions / landing_page_views

## Phase 2: Pull PostHog Analytics

If PostHog credentials are configured:

### 2.1: Event Counts

Use the PostHog API or PostHog MCP tools to query:

```
POST {posthog_host}/api/projects/{project_id}/query
Headers:
  Authorization: Bearer {personal_api_key}
Body:
{
  "query": {
    "kind": "EventsQuery",
    "select": ["event", "count()"],
    "where": ["timestamp >= now() - interval 7 day"],
    "groupBy": ["event"],
    "orderBy": ["count() DESC"]
  }
}
```

Focus on key events:
- `$pageview` (with UTM filters for Meta traffic)
- Signup events (`user_signed_up`, `sign_up`, or custom)
- Purchase events (`purchase`, `checkout_completed`, or custom)
- Any custom conversion events

### 2.2: UTM-Filtered Funnel

Query pageviews and conversions filtered by `utm_source=meta`:
```
Filter: properties.$utm_source = "meta"
```

This gives the PostHog view of Meta-attributed traffic, independent of Meta's pixel attribution.

### 2.3: Funnel Conversion Rate

If funnel steps are known (landing page → signup → activation → purchase):
- Query each step filtered by Meta UTM parameters
- Calculate step-by-step drop-off rates

## Phase 3: Cross-Reference Attribution

Compare Meta's reported conversions with PostHog's:

```
| Metric          | Meta Reports | PostHog Reports | Delta |
|-----------------|-------------|-----------------|-------|
| Link Clicks     | {X}         | Pageviews: {Y}  | {diff}|
| Conversions     | {X}         | Signups: {Y}    | {diff}|
| Conv. Rate      | {X%}        | {Y%}            | {diff}|
```

Common discrepancies and explanations:
- Meta over-reports: Attribution window (7-day click, 1-day view) vs. PostHog's last-touch
- PostHog under-reports: Ad blockers preventing PostHog from loading
- Click vs. pageview gap: Slow landing page or bot traffic

## Phase 4: Winner/Loser Analysis

### 4.1: Identify Winners

Rank all ads/ad sets by the primary KPI (CPA for conversions, CTR for traffic):

**Top Performers** (best 20%):
- Which creative angle is winning?
- Which audience segment has the lowest CPA?
- Which placement is most efficient?

**Bottom Performers** (worst 20%):
- Which ads are spending without converting?
- Which audiences have the highest CPA?
- Are there ad sets still in learning phase?

### 4.2: Statistical Significance

For comparison of ad variations:
- Calculate if the difference is statistically significant (need ~100+ conversions for reliable data)
- If still in learning phase (<50 optimization events), note: "Insufficient data — wait {X} more days before making decisions."

### 4.3: Creative Fatigue Check

Look for signs of creative fatigue:
- Frequency > 3.0 (same person seeing ad 3+ times)
- CTR declining over the period
- CPA increasing while spend is stable

## Phase 5: Optimization Recommendations

Based on the analysis, generate specific, actionable recommendations:

### Budget Recommendations
- "Increase budget on Ad Set X by Y% — it has the lowest CPA at $Z"
- "Decrease budget on Ad Set X — CPA is 3x above target"
- "Kill Ad Y — $X spent with 0 conversions"

### Creative Recommendations
- "The {angle} creative is winning — create more variations of this angle"
- "Ad creative fatigue detected on {ad} (frequency: X). Rotate new creatives."
- "Test video creative — image-only ads show declining CTR"

### Targeting Recommendations
- "Narrow age range on Ad Set X to {range} — that segment converts best"
- "Expand to lookalike audiences based on {X} converters"
- "Exclude {audience} — high impressions but zero conversions"

### Technical Recommendations
- "Landing page view rate is low (X%) — check page load speed"
- "Meta/PostHog attribution gap is large (X%) — verify pixel is firing correctly"
- "High bounce rate from Meta traffic — review landing page relevance to ad messaging"

## Phase 6: Save Metrics Snapshot

Save the complete metrics data to `.gtm/metrics/snapshot-{YYYY-MM-DD}.json`:

```json
{
  "date": "{ISO date}",
  "period": "last_7d",
  "meta": {
    "account_spend": {total},
    "campaigns": [
      {
        "id": "{id}",
        "name": "{name}",
        "spend": {amount},
        "impressions": {count},
        "clicks": {count},
        "cpm": {value},
        "cpc": {value},
        "ctr": {value},
        "conversions": {count},
        "cpa": {value},
        "ad_sets": [...]
      }
    ]
  },
  "posthog": {
    "meta_pageviews": {count},
    "meta_signups": {count},
    "meta_purchases": {count},
    "funnel_rates": {...}
  },
  "attribution_comparison": {...},
  "recommendations": ["{list of recommendations}"]
}
```

If a snapshot for today already exists, append a counter: `snapshot-{YYYY-MM-DD}-02.json`

## Phase 7: Dashboard Output

Present findings in a clear dashboard format:

```
GTM Metrics Dashboard — {date range}

SPEND: ${total}  |  IMPRESSIONS: {X}  |  CLICKS: {X}  |  CONVERSIONS: {X}

| Campaign | Spend | CPM | CPC | CTR | Conv | CPA | Status |
|----------|-------|-----|-----|-----|------|-----|--------|
| {name}   | ${X}  | ${X}| ${X}| X%  | {X}  | ${X}| {rec}  |

Top Performer: {ad/adset name} — CPA ${X}
Worst Performer: {ad/adset name} — CPA ${X}

Key Recommendations:
1. {recommendation}
2. {recommendation}
3. {recommendation}

Snapshot saved: .gtm/metrics/snapshot-{date}.json
Next: Run /gtm-learn to save insights, or /gtm-report for a full weekly report.
```

## Error Handling

- **Meta token expired**: Detect error code 190, prompt for new token, STOP.
- **Meta rate limiting**: If error code 17 or 4, wait and retry (up to 3 times with backoff: 30s, 60s, 120s).
- **PostHog unavailable**: Continue with Meta-only data. Clearly note: "PostHog data unavailable — showing Meta-only metrics. Cross-attribution analysis skipped."
- **No campaign data**: If no campaigns have run or all are paused with zero spend, report: "No active campaigns with spend data found. Deploy a campaign with `/gtm-deploy` first."
- **Incomplete data**: If some metrics are missing (e.g. no conversion tracking), note which metrics are unavailable and why (likely pixel not configured for that event).
