---
name: gtm-routines
description: "Manage autonomous cloud routines for GTM automation"
argument-hint: "list | setup | status"
---

# GTM Routines Manager

You manage autonomous cloud routines for the GTM Command Center. Routines are Claude Code cloud workflows that run on a schedule without human intervention, pulling metrics, checking experiments, and generating reports automatically.

## What Are Routines?

Routines are scheduled Claude Code sessions that run in the cloud. They execute a predefined command or workflow on a cron schedule, save their output to `.gtm/`, and optionally alert you when something needs attention.

Each routine:
- Runs as a Claude Code cloud session (via `/schedule`)
- Has a cron schedule (e.g., daily at 9 AM, weekly on Monday)
- Executes one or more GTM commands
- Saves output to `.gtm/` directory
- Can send alerts via configured channels (Slack, email)

## Built-In Routine Templates

### 1. Daily Metrics Pull

**Schedule**: Every day at 9:00 AM (your timezone)
**What it does**:
- Runs `/gtm-metrics --auto` to pull all channel metrics
- Saves snapshot to `.gtm/metrics/snapshot-{date}.json`
- Checks threshold breaches:
  - CPA increased >30% vs. 7-day average
  - CTR dropped >25% vs. 7-day average
  - Daily spend exceeded budget by >20%
  - Campaign was auto-paused by Meta
- If any threshold is breached, generates an alert

**Setup command**:
```
/schedule create "Daily GTM Metrics" \
  --cron "0 9 * * *" \
  --command "/gtm-metrics --auto" \
  --description "Pull metrics from all channels and check thresholds"
```

**Alert format**:
```
ALERT: GTM Metrics Threshold Breach

Campaign: {name}
Metric: CPA
Current: $12.50 (was $8.30 yesterday)
Change: +50%
Threshold: >30%

Recommended action: Check creative fatigue or audience saturation.
Run /gtm-learn for full analysis.
```

See `routines/daily-metrics-pull.md` for full documentation.

### 2. Weekly Optimization

**Schedule**: Every Monday at 10:00 AM
**What it does**:
- Runs `/gtm-learn` to extract insights from the past week
- Runs `/gtm-diagnose` to identify the current funnel bottleneck
- Runs `/gtm-report` to generate the weekly performance report
- Compiles a weekly optimization brief with recommended actions

**Setup command**:
```
/schedule create "Weekly GTM Optimization" \
  --cron "0 10 * * 1" \
  --command "Run /gtm-learn, then /gtm-diagnose, then /gtm-report. Compile findings into a weekly optimization brief at .gtm/reports/weekly-{date}.md" \
  --description "Weekly learning loop, diagnosis, and report generation"
```

See `routines/weekly-optimization.md` for full documentation.

### 3. PR Conversion Check

**Schedule**: Triggered on GitHub PR events (when files in landing/email paths change)
**What it does**:
- Detects which landing pages or email templates were modified
- Checks that conversion tracking is complete:
  - PostHog events present on CTA clicks
  - Meta Pixel events firing on page load and conversion
  - UTM parameters preserved through the flow
  - Form submission events tracked
- Reports missing tracking as PR comments

**Setup command**:
```
/schedule create "PR Conversion Check" \
  --trigger "github:pull_request" \
  --filter "paths:src/pages/landing/**,src/emails/**,app/(marketing)/**" \
  --command "Check all modified landing pages and email templates for complete conversion tracking. Report any missing PostHog events, Meta Pixel events, or UTM parameters." \
  --description "Verify conversion tracking completeness on landing/email PRs"
```

See `routines/pr-conversion-check.md` for full documentation.

### 4. Experiment Monitor

**Schedule**: Every day at 6:00 PM
**What it does**:
- Runs `/gtm-experiment --check-all` to check all active experiments
- For any experiment that has reached statistical significance:
  - Generates a results summary
  - Creates an alert with the winner and recommended action
- For experiments running longer than 2x estimated duration:
  - Flags as "stalled" and recommends ending early
- Updates `.gtm/experiments/README.md` with current status

**Setup command**:
```
/schedule create "Experiment Monitor" \
  --cron "0 18 * * *" \
  --command "/gtm-experiment --check-all" \
  --description "Check all active experiments for statistical significance"
```

See `routines/experiment-monitor.md` for full documentation.

## Mode: List

If `$ARGUMENTS` contains "list":

1. Check for configured schedules using `/schedule list` (or equivalent)
2. Read `.gtm/routines/` directory for routine configs
3. Present:

```
GTM Routines Status:

| Routine | Schedule | Last Run | Status | Next Run |
|---------|----------|----------|--------|----------|
| Daily Metrics | 9 AM daily | 2026-04-14 09:00 | OK | 2026-04-15 09:00 |
| Weekly Optimization | Mon 10 AM | 2026-04-14 10:00 | OK | 2026-04-21 10:00 |
| PR Conversion Check | PR trigger | 2026-04-13 14:22 | OK | (on next PR) |
| Experiment Monitor | 6 PM daily | 2026-04-14 18:00 | OK | 2026-04-15 18:00 |

Recent alerts: 1 (CPA threshold breach on 2026-04-13)
```

## Mode: Setup

If `$ARGUMENTS` contains "setup":

Walk the user through setting up all 4 routines:

1. Check prerequisites:
   - `.gtm/config.json` exists and is valid
   - Claude Code `/schedule` command is available
   - Required API credentials are configured

2. For each routine, ask: **"Set up {routine_name}? (yes/skip)"**
   - If yes: run the setup command
   - If skip: continue to next

3. After all routines are set up, present the summary table.

4. Create `.gtm/routines/config.json` to track routine metadata:
```json
{
  "routines": [
    {
      "name": "daily-metrics-pull",
      "schedule_id": "{from /schedule}",
      "cron": "0 9 * * *",
      "enabled": true,
      "thresholds": {
        "cpa_increase_pct": 30,
        "ctr_decrease_pct": 25,
        "budget_overspend_pct": 20
      }
    }
  ],
  "alerts": {
    "channel": "console",
    "slack_webhook": null,
    "email": null
  }
}
```

## Mode: Status

If `$ARGUMENTS` contains "status":

1. Read `.gtm/routines/config.json`
2. Check each routine's last run log
3. Report any failures or missed runs
4. Show recent alerts

## Error Handling

- **`/schedule` not available**: If the schedule command is not available, explain: "Cloud routines require Claude Code's `/schedule` feature. The routine templates are saved in `routines/` for reference. You can manually run the commands on your preferred schedule."
- **Missing config**: If `.gtm/config.json` is missing, direct to `/gtm-setup`.
- **Routine failure**: If a routine's last run failed, show the error and suggest fixes.
- **Alert channel not configured**: Default to saving alerts in `.gtm/routines/alerts/` as JSON files. Offer to set up Slack or email alerts.
