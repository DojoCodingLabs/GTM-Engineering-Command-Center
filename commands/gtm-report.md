---
name: gtm-report
description: "Generate unified weekly GTM performance report across all channels"
argument-hint: ""
---

# Unified Weekly GTM Performance Report

You are the data-analyst agent in reporting mode. You will aggregate all campaign data from the past week across ALL channels, compare it to previous periods, track AARRR funnel health trends, calculate cross-channel attribution, and produce a comprehensive weekly report.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Determine which data sources are configured:
   - Meta Ads, Google Ads, Stripe, email provider, PostHog, SEO
3. Test API connectivity for each configured source. If expired, STOP and prompt for refresh.
4. Read all existing metrics snapshots from `.gtm/metrics/` for historical comparison.
5. Read all deployment records from `.gtm/campaigns/`.
6. Read `.gtm/funnel/` for AARRR funnel history (for trend comparison).
7. Read `.gtm/experiments/` for active experiment status updates.

## Phase 1: Pull This Week's Data

### 1.1: Meta Ads -- Weekly Totals + Daily Breakdown

```
GET .../insights?fields=spend,impressions,reach,clicks,unique_clicks,cpc,cpm,ctr,
    actions,cost_per_action_type,conversions,purchase_roas,frequency
    &date_preset=last_7d
```

Plus daily breakdown (`time_increment=1`) for trend charts.

### 1.2: Google Ads -- Weekly Totals (if configured)

Pull campaign-level metrics: spend, impressions, clicks, conversions, CPC, CPA.
Pull search term report for top converting keywords.

### 1.3: Stripe -- Revenue Metrics (if configured)

- MRR, new subscribers, churned subscribers, net revenue
- Revenue by source (if attributable)
- LTV calculation, LTV:CAC ratio

### 1.4: Email -- Sequence Performance (if configured)

- Per-sequence metrics: sent, delivered, opened, clicked, converted, unsubscribed
- Best/worst performing emails by open rate and click rate
- Sequence completion rates

### 1.5: SEO/Organic -- Traffic + Rankings (if data available)

- Organic pageviews and visitors (from PostHog, filtered by non-paid UTMs)
- Search performance (if GSC data available)
- Content performance for deployed SEO content

### 1.6: PostHog -- Product Metrics

- Total signups, activations, purchases (from all sources)
- Funnel completion rates by source
- Session metrics (DAU, WAU, retention)

## Phase 2: Pull Previous Period Data

### 2.1: Last Week (for week-over-week comparison)

For each data source, pull the previous 7-day period for comparison. Alternatively, read the most recent snapshot from `.gtm/metrics/` that is 7+ days old.

### 2.2: Historical Trend

Read all snapshots in `.gtm/metrics/` and extract weekly aggregates to show trends over time (up to 8 weeks if available).

## Phase 3: Calculate Unified Unit Economics

Compute metrics across ALL channels:

| Metric | This Week | Last Week | Change | Target |
|--------|-----------|-----------|--------|--------|
| **Revenue** | | | | |
| MRR | ${X} | ${Y} | {+/-}% | |
| New Customers | {X} | {Y} | {+/-}% | |
| Churn Rate | X% | Y% | {+/-}pp | <5% |
| LTV | ${X} | ${Y} | {+/-}% | |
| Net Revenue | ${X} | ${Y} | {+/-}% | |
| **Acquisition (All Channels)** | | | | |
| Total Spend | ${X} | ${Y} | {+/-}% | |
| Total Conversions | {X} | {Y} | {+/-}% | |
| Blended CAC | ${X} | ${Y} | {+/-}% | |
| LTV:CAC | X:1 | Y:1 | {+/-} | >3:1 |
| **Meta Ads** | | | | |
| Spend | ${X} | ${Y} | {+/-}% | |
| CPM | ${X} | ${Y} | {+/-}% | |
| CPC | ${X} | ${Y} | {+/-}% | |
| CTR | X% | Y% | {+/-}pp | >1.5% |
| CPA | ${X} | ${Y} | {+/-}% | |
| ROAS | Xx | Yx | {+/-} | >2x |
| Frequency | X | Y | {+/-} | <3.0 |
| **Google Ads** (if configured) | | | | |
| Spend | ${X} | ${Y} | {+/-}% | |
| CPC | ${X} | ${Y} | {+/-}% | |
| CPA | ${X} | ${Y} | {+/-}% | |
| ROAS | Xx | Yx | {+/-} | |
| **Email** | | | | |
| Open Rate | X% | Y% | {+/-}pp | >25% |
| Click Rate | X% | Y% | {+/-}pp | >3% |
| Conversion Rate | X% | Y% | {+/-}pp | |
| Unsubscribe Rate | X% | Y% | {+/-}pp | <0.5% |
| **Organic/SEO** | | | | |
| Organic Visitors | {X} | {Y} | {+/-}% | |
| Organic Conversions | {X} | {Y} | {+/-}% | |
| Avg. Position | X | Y | {+/-} | |

## Phase 4: Cross-Channel Attribution Table

```
Cross-Channel Attribution (Last 7 Days):

| Channel | Spend | Conv | CPA | Revenue | ROAS | % of Total Conv |
|---------|-------|------|-----|---------|------|-----------------|
| Meta Ads | ${X} | {N} | ${X} | ${X} | {X}x | X% |
| Google Ads | ${X} | {N} | ${X} | ${X} | {X}x | X% |
| Email | $0 | {N} | $0 | ${X} | -- | X% |
| Organic/SEO | $0 | {N} | $0 | ${X} | -- | X% |
| Direct | $0 | {N} | $0 | ${X} | -- | X% |
| Referral | $0 | {N} | $0 | ${X} | -- | X% |
| TOTAL | ${X} | {N} | ${X} | ${X} | {X}x | 100% |

Attribution Notes:
- Meta reports {X} conversions vs. PostHog's {Y} (delta: {diff})
- {explanation of discrepancy}
```

## Phase 5: AARRR Funnel Health Trend

If funnel data exists in `.gtm/funnel/`, show week-over-week trend:

```
AARRR Funnel Health -- Week-over-Week:

| Stage | This Week | Last Week | 2 Weeks Ago | Trend |
|-------|-----------|-----------|-------------|-------|
| Acquisition | 85 | 82 | 78 | Improving |
| Activation | 62 | 60 | 55 | Improving |
| Retention | 38 | 35 | 35 | Stable |
| Revenue | 48 | 45 | 42 | Improving |
| Referral | 22 | 20 | 20 | Stable |

Current Bottleneck: RETENTION (38/100) -- unchanged for 3 weeks
Biggest Improvement: ACQUISITION (+7 points over 2 weeks)
```

If no funnel history exists, note: "AARRR trend unavailable. Run `/gtm-funnel` to establish baseline."

## Phase 6: Top Performers Analysis

### 6.1: Best Creatives (Across All Channels)

```
Top 5 Assets by CPA:
| Rank | Asset | Channel | Spend | Conv | CPA | CTR |
|------|-------|---------|-------|------|-----|-----|
| 1 | {name} | Meta | ${X} | {X} | ${X} | X% |
| 2 | {name} | Email | $0 | {X} | $0 | X% |
| 3 | {name} | Google | ${X} | {X} | ${X} | X% |
```

### 6.2: Best Audiences / Segments

Rank ad sets and email segments by conversion efficiency.

### 6.3: Worst Performers

Identify bottom 5 assets/campaigns that should be paused or rotated.

### 6.4: Creative Fatigue Alerts

Flag assets where:
- Frequency >3.0 (Meta)
- CTR dropped >20% week-over-week
- CPA increased >30% week-over-week
- Open rate dropped >15% (Email)

## Phase 7: Experiment Status

If active experiments exist in `.gtm/experiments/`:

```
Active Experiments:
| Experiment | Channel | Runtime | Progress | Trend | Status |
|-----------|---------|---------|----------|-------|--------|
| {name} | Meta | {days}d | {X}% | +12% | Promising |
| {name} | Email | {days}d | {X}% | -3% | Flat |
| {name} | Landing | {days}d | 100% | +18% | SIGNIFICANT -- decide! |
```

## Phase 8: Trend Analysis

If 2+ weeks of historical data are available:

### 8.1: Multi-Week Trend Table

```
| Week | Total Spend | Total Conv | Blended CPA | MRR | ROAS |
|------|------------|-----------|-------------|-----|------|
| W-4 | ${X} | {X} | ${X} | ${X} | {X}x |
| W-3 | ${X} | {X} | ${X} | ${X} | {X}x |
| W-2 | ${X} | {X} | ${X} | ${X} | {X}x |
| W-1 | ${X} | {X} | ${X} | ${X} | {X}x |
```

### 8.2: Account Health Assessment

Based on trends, classify:
- **Scaling**: Spend up, CPA stable or decreasing, MRR growing
- **Optimizing**: Spend stable, CPA decreasing, efficiency improving
- **Fatiguing**: Spend stable, CPA increasing, frequency rising
- **Declining**: Spend up, CPA up, ROAS down, churn rising
- **Learning**: Not enough data (<2 weeks)

## Phase 9: Generate Report

Save the report to `.gtm/metrics/report-{YYYY-MM-DD}.md`:

```markdown
# GTM Weekly Report -- Week of {start_date} to {end_date}

## Executive Summary
{3-4 sentences: total spend, conversions, revenue, MRR, CAC trend, key wins, key concerns}

## Revenue Health
{Stripe metrics table}

## Cross-Channel Attribution
{Attribution table from Phase 4}

## Channel Performance

### Meta Ads
{Campaign table, top/bottom performers}

### Google Ads (if applicable)
{Performance summary}

### Email
{Sequence performance table}

### Organic/SEO
{Traffic and conversion summary}

## AARRR Funnel Health
{Funnel trend table from Phase 5}

## Top Performing Assets
{Table from Phase 6.1}

## Underperformers (Action Required)
{Table from Phase 6.3}

## Creative Fatigue Alerts
{List from Phase 6.4, or "None"}

## Active Experiments
{Table from Phase 7}

## Trend Analysis
{Content from Phase 8}

## Recommendations for Next Week
1. {Budget action: scale/cut/hold per channel}
2. {Creative action: new angles, refresh, rotate}
3. {Email action: new sequence, subject line tests}
4. {SEO action: new content, technical fixes}
5. {Targeting action: narrow, expand, exclude}
6. {Experiment action: launch, conclude, pivot}

## Attribution Notes
{Discrepancies between channels and first-party data}
{Data quality notes}

---
Generated by GTM Command Center on {timestamp}
```

## Phase 10: Output

Present the report summary (executive summary + key metrics + top 3 recommendations).

Tell the user:
```
Weekly report saved: .gtm/metrics/report-{date}.md
Full metrics snapshot: .gtm/metrics/snapshot-{date}.json

Next steps:
- Run /gtm-learn to extract and save strategic insights
- Run /gtm-create to generate fresh creatives for fatigued assets
- Run /gtm-experiment --check-all to review experiment results
- Run /gtm-diagnose to update funnel bottleneck analysis
```

## Error Handling

- **Not enough data**: If <7 days of active spend, note: "Partial week data ({X} days). Metrics may not be representative."
- **No previous period**: Skip week-over-week changes. Note: "First weekly report -- no comparison data."
- **Token expired**: STOP and prompt for refresh.
- **Any channel unavailable**: Generate report with available data and clearly note gaps.
- **Zero spend**: Report: "No active spend this week." Suggest deploying or activating.
- **Stripe unavailable**: Skip revenue section. Note: "Revenue data unavailable -- configure Stripe in /gtm-setup."
