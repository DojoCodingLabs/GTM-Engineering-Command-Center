---
name: weekly-optimization
description: "Weekly routine that runs learning loop, diagnosis, and generates a weekly report"
---

# Weekly Optimization Routine

## Overview

This routine runs every Monday at 10:00 AM, executing a complete optimization cycle: extracting learnings from the past week, diagnosing the current funnel bottleneck, and generating a comprehensive weekly report. It compiles all findings into a single weekly optimization brief.

## Schedule

- **Frequency**: Weekly
- **Day**: Monday
- **Time**: 10:00 AM (configured timezone)
- **Cron expression**: `0 10 * * 1`
- **Runtime**: ~5-10 minutes depending on data volume

## What It Does

### Step 1: Learning Loop (`/gtm-learn`)

1. Loads the latest metrics snapshot(s) from `.gtm/metrics/`
2. Compares current performance to historical data
3. Extracts structured insights in three categories:
   - **Creative wins**: Which angles, copy, visuals work best
   - **Targeting insights**: Which audiences convert most efficiently
   - **Budget allocation**: Optimal spend levels and patterns
4. Saves insights to `.gtm/learnings/` files (appends, never overwrites)
5. Updates `.gtm/MEMORY.md` with new learnings index

### Step 2: Funnel Diagnosis (`/gtm-diagnose`)

1. Reads all available data sources (Meta, Stripe, email, SEO, PostHog)
2. Scores each AARRR stage (0-100):
   - Acquisition, Activation, Retention, Revenue, Referral
3. Identifies the primary revenue bottleneck
4. Calculates the revenue leak at the bottleneck
5. Prescribes top 3 actions with expected impact
6. Saves diagnosis to `.gtm/funnel/diagnosis-{date}.json`

### Step 3: Weekly Report (`/gtm-report`)

1. Aggregates all channel data for the past 7 days
2. Calculates week-over-week changes
3. Builds cross-channel attribution table
4. Identifies top and bottom performers
5. Checks for creative fatigue signals
6. Updates AARRR funnel health trend
7. Generates recommendations
8. Saves report to `.gtm/metrics/report-{date}.md`

### Step 4: Compile Weekly Brief

Combines outputs from all three steps into a single optimization brief:

Save to `.gtm/reports/weekly-brief-{YYYY-MM-DD}.md`:

```markdown
# Weekly GTM Optimization Brief -- Week of {date}

## Quick Stats
- Total spend: ${X} | Conversions: {N} | Blended CPA: ${X} | MRR: ${X}

## This Week's Key Learnings
1. {Most impactful learning from /gtm-learn}
2. {Second most impactful}
3. {Third}

## Funnel Bottleneck
- Current: {stage} ({score}/100)
- Change from last week: {+/-X} points
- Top action: {prescribed action with expected impact}

## Cross-Channel Performance Summary
| Channel | Spend | Conv | CPA | WoW Change |
|---------|-------|------|-----|------------|
{summary table}

## Recommended Actions This Week
1. {Action with highest expected impact}
2. {Second priority action}
3. {Third priority action}

## Active Experiments
{Status of each active experiment}

## Full Reports
- Learnings: .gtm/learnings/
- Diagnosis: .gtm/funnel/diagnosis-{date}.json
- Weekly Report: .gtm/metrics/report-{date}.md
```

### Step 5: Alert on Significant Findings

Generate an alert if:
- Funnel bottleneck changed from last week (new bottleneck identified)
- An experiment reached statistical significance
- Revenue metrics crossed critical thresholds (MRR decline, churn spike)
- A new high-confidence learning contradicts a previous one

## Setup Instructions

### Prerequisites

1. `.gtm/config.json` must exist with channels configured
2. At least 1 week of metrics data in `.gtm/metrics/`
3. Claude Code `/schedule` command available

### Create the Routine

```bash
/schedule create "Weekly GTM Optimization" \
  --cron "0 10 * * 1" \
  --command "Run /gtm-learn, then /gtm-diagnose, then /gtm-report. Compile all findings into a weekly optimization brief at .gtm/reports/weekly-brief-{date}.md. Alert if bottleneck changed or experiments reached significance." \
  --description "Weekly learning loop, diagnosis, and report generation"
```

### Customize

Edit `.gtm/routines/config.json`:

```json
{
  "routines": [
    {
      "name": "weekly-optimization",
      "cron": "0 10 * * 1",
      "enabled": true,
      "options": {
        "skip_learn_if_no_new_data": true,
        "alert_on_bottleneck_change": true,
        "alert_on_experiment_significance": true,
        "include_competitor_check": false
      }
    }
  ]
}
```

## Troubleshooting

- **No metrics data**: The routine will warn "No metrics snapshots found" and skip the learning loop. Ensure `/gtm-metrics` has been run at least once.
- **Stale data**: If all snapshots are older than 14 days, the routine will warn about data staleness.
- **Routine takes too long**: If many channels are configured and data is large, the routine may take 10+ minutes. This is normal for the first run.
- **API failures**: Individual channel failures do not stop the routine. The report will note which channels had errors.

## Related Commands

- `/gtm-learn` -- Manual learning loop
- `/gtm-diagnose` -- Manual funnel diagnosis
- `/gtm-report` -- Manual weekly report
- `/gtm-routines status` -- Check routine execution status
