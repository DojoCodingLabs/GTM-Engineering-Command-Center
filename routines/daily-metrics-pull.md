---
name: daily-metrics-pull
description: "Daily routine that pulls metrics from all channels and alerts on threshold breaches"
---

# Daily Metrics Pull Routine

## Overview

This routine runs every day at 9:00 AM, automatically pulling metrics from all configured channels (Meta Ads, Stripe, email, SEO, Google Ads), saving a snapshot, and alerting when key thresholds are breached. It runs without human intervention as a Claude Code cloud workflow.

## Schedule

- **Frequency**: Daily
- **Time**: 9:00 AM (configured timezone, default: America/New_York)
- **Cron expression**: `0 9 * * *`
- **Runtime**: ~2-5 minutes depending on number of channels

## What It Does

### Step 1: Pull Metrics

Executes `/gtm-metrics --auto` which:
1. Reads `.gtm/config.json` and `.env.gtm` for configured channels
2. Pulls data from each configured source:
   - **Meta Ads**: via `meta ads insights get --no-input --output json` (CLI). Account spend, campaign performance, ad-level metrics
   - **Stripe**: MRR, new customers, churn, revenue
   - **Email**: Open rates, click rates, conversion rates per sequence
   - **PostHog**: Pageviews, signups, funnel completion by source
   - **Google Ads**: Spend, conversions, CPA (if configured)
3. Saves unified snapshot to `.gtm/metrics/snapshot-{YYYY-MM-DD}.json`

The Meta CLI's exit codes are honored at the routine level:
- `0` — continue
- `3` — token expired/invalid → emit a high-severity alert and skip Meta metrics for this run
- `4` — Meta API error → backoff 30s, retry once; if still failing, emit a medium-severity alert and proceed without Meta metrics

### Step 2: Check Thresholds

Compares today's metrics against the 7-day rolling average. Triggers alerts for:

| Metric | Threshold | Severity |
|--------|-----------|----------|
| CPA increase | >30% vs. 7-day avg | High |
| CTR decrease | >25% vs. 7-day avg | High |
| Daily spend | >20% over budget | Medium |
| Campaign auto-paused by Meta | Any | High |
| Email bounce rate | >5% | Medium |
| Stripe churn spike | >2x monthly avg | High |
| Conversion rate drop | >20% vs. 7-day avg | High |
| ROAS below breakeven | <1.0x | Critical |

### Step 3: Generate Alerts

If any threshold is breached, the routine generates an alert:

```json
{
  "date": "2026-04-14T09:00:00Z",
  "severity": "high",
  "metric": "CPA",
  "channel": "meta_ads",
  "campaign": "Dojo - signups - 2026-04-01",
  "current_value": 12.50,
  "average_value": 8.30,
  "change_pct": 50.6,
  "threshold_pct": 30,
  "recommended_action": "Check creative fatigue or audience saturation. Run /gtm-learn for analysis."
}
```

Alerts are saved to `.gtm/routines/alerts/alert-{YYYY-MM-DD}.json`.

### Step 4: Save Daily Summary

Appends a one-line daily summary to `.gtm/routines/daily-log.md`:

```
| 2026-04-14 | $140 spent | 12 conv | $11.67 CPA | 1 alert (CPA +51%) |
```

## Setup Instructions

### Prerequisites

1. `.gtm/config.json` must exist with at least one channel configured
2. Claude Code `/schedule` command must be available
3. API credentials must be valid (especially Meta access token -- check expiry)

### Create the Routine

```bash
# Using Claude Code /schedule command:
/schedule create "Daily GTM Metrics" \
  --cron "0 9 * * *" \
  --command "/gtm-metrics --auto" \
  --description "Pull metrics from all channels, save snapshot, check thresholds"
```

### Configure Thresholds

Edit `.gtm/routines/config.json` to customize thresholds:

```json
{
  "routines": [
    {
      "name": "daily-metrics-pull",
      "cron": "0 9 * * *",
      "enabled": true,
      "thresholds": {
        "cpa_increase_pct": 30,
        "ctr_decrease_pct": 25,
        "budget_overspend_pct": 20,
        "email_bounce_rate_pct": 5,
        "churn_spike_multiplier": 2,
        "conversion_rate_drop_pct": 20,
        "roas_floor": 1.0
      }
    }
  ]
}
```

### Configure Alert Delivery

By default, alerts are saved to `.gtm/routines/alerts/`. Optionally configure delivery:

```json
{
  "alerts": {
    "channel": "console",
    "slack_webhook": "https://hooks.slack.com/services/...",
    "email": "your@email.com"
  }
}
```

## Troubleshooting

- **Meta `ACCESS_TOKEN` expired (CLI exit code 3)**: The routine logs an error, emits a high-severity alert, and skips Meta metrics. Refresh the System User token in Meta Business Manager and update `.env.gtm`. Validate with `meta auth status`.
- **`meta: command not found`**: The Ads CLI is not installed. Run `/gtm-setup` to reinstall, or `uv tool install meta-ads` directly.
- **Meta API error (CLI exit code 4)**: Routine retries once after 30s. If still failing, surfaces a medium-severity alert. Likely transient; investigate via `/gtm-metrics meta` interactively.
- **Routine not running**: Verify with `/schedule list`. Check that the routine is enabled in config.
- **Too many alerts**: Increase thresholds in `config.json` to reduce noise. Consider widening the rolling average window.
- **Stale snapshots**: If snapshots stop appearing, check `meta auth status` and other API health endpoints first.

## Related Commands

- `/gtm-metrics` -- Manual metrics pull (interactive mode)
- `/gtm-routines status` -- Check routine status
- `/gtm-report` -- Full weekly report (more detailed than daily snapshot)
