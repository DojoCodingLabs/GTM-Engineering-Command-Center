---
name: gtm-report
description: "Generate weekly GTM performance report"
argument-hint: ""
---

# Weekly GTM Performance Report

You are the data-analyst agent in reporting mode. You will aggregate all campaign data from the past week, compare it to previous periods, identify trends, calculate unit economics, and produce a comprehensive weekly report.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate required credentials:
   - `meta.access_token` — required
   - `meta.ad_account_id` — required
   - `posthog.personal_api_key` — recommended (warn if missing)
3. Test Meta access token validity. If expired, STOP and prompt for refresh.
4. Read all existing metrics snapshots from `.gtm/metrics/` for historical comparison.
5. Read all deployment records from `.gtm/campaigns/` to know the full campaign inventory.

## Phase 1: Pull This Week's Data

### 1.1: Meta Ads — Weekly Totals

```
GET https://graph.facebook.com/{api_version}/{ad_account_id}/insights
  ?fields=spend,impressions,reach,clicks,unique_clicks,cpc,cpm,ctr,
          actions,cost_per_action_type,conversions,purchase_roas,frequency
  &date_preset=last_7d
  &access_token={token}
```

### 1.2: Meta Ads — Daily Breakdown

```
GET https://graph.facebook.com/{api_version}/{ad_account_id}/insights
  ?fields=spend,impressions,clicks,actions,cost_per_action_type
  &date_preset=last_7d
  &time_increment=1
  &access_token={token}
```

This gives day-by-day data for trend charts.

### 1.3: Meta Ads — Campaign Level

Pull per-campaign metrics with the same fields as the weekly totals.

### 1.4: Meta Ads — Top/Bottom Ads

Pull ad-level metrics and sort by CPA (or CTR for traffic campaigns) to identify the top 5 and bottom 5 performing ads.

### 1.5: PostHog — Weekly Events

If PostHog is configured, pull:
- Total pageviews from Meta traffic (utm_source=meta)
- Signup/purchase events from Meta traffic
- Funnel completion rates
- Session duration and bounce rate (if available)

## Phase 2: Pull Previous Period Data

### 2.1: Last Week (for week-over-week comparison)

```
GET https://graph.facebook.com/{api_version}/{ad_account_id}/insights
  ?fields=spend,impressions,clicks,actions,cost_per_action_type
  &time_range={"since":"{8_days_ago}","until":"{1_day_ago}"}
  &access_token={token}
```

Alternatively, read the most recent snapshot from `.gtm/metrics/` that is 7+ days old.

### 2.2: Historical Trend

Read all snapshots in `.gtm/metrics/` and extract weekly aggregates to show trends over time (up to 8 weeks if available).

## Phase 3: Calculate Unit Economics

Compute the following metrics:

| Metric | Formula | This Week | Last Week | Change |
|--------|---------|-----------|-----------|--------|
| Total Spend | Sum of all campaign spend | ${X} | ${Y} | {+/-}% |
| Total Conversions | Sum of target actions | {X} | {Y} | {+/-}% |
| CAC (Customer Acquisition Cost) | Total spend / Total conversions | ${X} | ${Y} | {+/-}% |
| ROAS (Return on Ad Spend) | Revenue / Spend | {X}x | {Y}x | {+/-}% |
| CPM (Cost per 1000 impressions) | (Spend / Impressions) * 1000 | ${X} | ${Y} | {+/-}% |
| CPC (Cost per Click) | Spend / Clicks | ${X} | ${Y} | {+/-}% |
| CTR (Click-Through Rate) | Clicks / Impressions | {X}% | {Y}% | {+/-}pp |
| Conversion Rate | Conversions / Clicks | {X}% | {Y}% | {+/-}pp |
| Frequency | Impressions / Reach | {X} | {Y} | {+/-} |

If the product has known pricing (from `config.product.pricing`), also calculate:
- **LTV:CAC Ratio** (if LTV is estimable)
- **Payback Period** (months to recover CAC)
- **Break-even ROAS**

## Phase 4: Top Performers Analysis

### 4.1: Best Creatives

Rank all ads by primary KPI and present the top 5:

```
Top 5 Ads by CPA:
| Rank | Ad Name | Angle | Spend | Conv | CPA | CTR |
|------|---------|-------|-------|------|-----|-----|
| 1    | {name}  | {angle}| ${X} | {X}  |${X} | X%  |
| 2    | ...     |       |       |      |     |     |
```

### 4.2: Best Audiences

Rank ad sets by CPA:
```
Top Audiences:
| Rank | Ad Set | Audience | CPA | Conv Rate | Spend |
|------|--------|----------|-----|-----------|-------|
| 1    | {name} | {desc}   | ${X}| X%        | ${X}  |
```

### 4.3: Worst Performers

Identify the bottom 5 ads/ad sets that should be paused or rotated.

### 4.4: Creative Fatigue Alerts

Flag any ad or ad set where:
- Frequency > 3.0
- CTR dropped > 20% week-over-week
- CPA increased > 30% week-over-week

## Phase 5: Trend Analysis

If historical data is available (2+ weeks), analyze:

### 5.1: Spend Trend
```
Week | Spend | Conv | CPA | ROAS
W-4  | ${X}  | {X}  | ${X}| {X}x
W-3  | ${X}  | {X}  | ${X}| {X}x
W-2  | ${X}  | {X}  | ${X}| {X}x
W-1  | ${X}  | {X}  | ${X}| {X}x
```

### 5.2: Direction Assessment

Based on trends, classify the account health:
- **Scaling**: Spend up, CPA stable or decreasing
- **Optimizing**: Spend stable, CPA decreasing
- **Fatiguing**: Spend stable, CPA increasing
- **Declining**: Spend up, CPA up, ROAS down
- **Learning**: Not enough data for trends (<2 weeks)

## Phase 6: Generate Report

Save the report to `.gtm/metrics/report-{YYYY-MM-DD}.md`:

```markdown
# GTM Weekly Report — Week of {start_date} to {end_date}

## Executive Summary
{2-3 sentence overview: total spend, total conversions, CAC trend, top-line performance}

## Key Metrics
| Metric | This Week | Last Week | Change | Target |
|--------|-----------|-----------|--------|--------|
{table from Phase 3}

## Campaign Performance
{table from Phase 1}

## Top Performing Creatives
{table from Phase 4.1}

## Top Performing Audiences
{table from Phase 4.2}

## Underperformers (Action Required)
{table from Phase 4.3}

## Creative Fatigue Alerts
{list from Phase 4.4, or "None"}

## Trend Analysis
{content from Phase 5}

## Recommendations for Next Week
1. {Budget action: scale/cut/hold per campaign}
2. {Creative action: new angles, refresh, rotate}
3. {Targeting action: narrow, expand, exclude}
4. {Technical action: pixel, landing page, tracking}

## Attribution Notes
{Any discrepancies between Meta and PostHog data}
{Data quality notes}

---
Generated by GTM Command Center on {timestamp}
```

## Phase 7: Output

Present the report summary to the user (key metrics table + top 3 recommendations).

Tell the user:
```
Weekly report saved: .gtm/metrics/report-{date}.md
Full metrics snapshot: .gtm/metrics/snapshot-{date}.json

Next steps:
- Run /gtm-learn to extract and save strategic insights
- Run /gtm-create to generate fresh creatives for fatigued ads
- Run /gtm-deploy to launch new ad variations
```

## Error Handling

- **Not enough data**: If the account has < 7 days of active spend, note: "Partial week data ({X} days of spend). Metrics may not be representative."
- **No previous period**: If no historical data exists for comparison, skip week-over-week changes and note: "First weekly report — no comparison data available yet."
- **Meta token expired**: STOP and prompt for refresh.
- **PostHog unavailable**: Generate Meta-only report and note the gap.
- **Zero spend**: If total spend is $0, report: "No active spend this week. All campaigns may be paused." Suggest running `/gtm-deploy` or activating paused campaigns.
