# GTM Routines

Routines are autonomous Claude Code cloud workflows that run on a schedule without human intervention. They automate the repetitive parts of the GTM lifecycle -- pulling metrics, checking experiments, generating reports -- so you can focus on strategy and creative decisions.

## How Routines Work

1. **Scheduled execution**: Routines run on a cron schedule (daily, weekly) or on event triggers (GitHub PRs). They use Claude Code's `/schedule` command to register as cloud workflows.

2. **Autonomous operation**: When a routine runs, it executes one or more GTM commands in sequence, saves output to `.gtm/`, and generates alerts when thresholds are breached or actions are needed.

3. **Human-in-the-loop alerts**: Routines never make destructive changes (pausing campaigns, changing budgets, rolling out experiments). They analyze and recommend -- you decide.

4. **Persistent state**: All routine output is saved to `.gtm/` directories (metrics snapshots, reports, alerts, experiment results). This data feeds into future runs and manual commands.

## Available Routines

| Routine | Schedule | Purpose | Documentation |
|---------|----------|---------|---------------|
| **Daily Metrics Pull** | 9 AM daily | Pull all channel metrics, check thresholds, alert on anomalies | [daily-metrics-pull.md](./daily-metrics-pull.md) |
| **Weekly Optimization** | Mon 10 AM | Learning loop + diagnosis + weekly report | [weekly-optimization.md](./weekly-optimization.md) |
| **PR Conversion Check** | GitHub PR trigger | Verify tracking completeness on landing/email changes | [pr-conversion-check.md](./pr-conversion-check.md) |
| **Experiment Monitor** | 6 PM daily | Check active experiments for statistical significance | [experiment-monitor.md](./experiment-monitor.md) |

## Quick Setup

### 1. Verify Prerequisites

```bash
# Ensure GTM Command Center is configured
/gtm-setup

# Ensure at least one metrics source is working
/gtm-metrics
```

### 2. Set Up All Routines

The easiest way to set up all routines:

```bash
/gtm-routines setup
```

This walks you through each routine and asks whether to enable it.

### 3. Manual Setup (Per Routine)

```bash
# Daily metrics
/schedule create "Daily GTM Metrics" --cron "0 9 * * *" --command "/gtm-metrics --auto"

# Weekly optimization
/schedule create "Weekly GTM Optimization" --cron "0 10 * * 1" --command "Run /gtm-learn, /gtm-diagnose, /gtm-report. Compile into weekly brief."

# Experiment monitor
/schedule create "Experiment Monitor" --cron "0 18 * * *" --command "/gtm-experiment --check-all"

# PR conversion check
/schedule create "PR Conversion Check" --trigger "github:pull_request" --filter "paths:src/pages/landing/**,src/emails/**"
```

### 4. Check Status

```bash
/gtm-routines list    # See all routines and their last run
/gtm-routines status  # Detailed status with recent alerts
```

## Configuration

All routine configuration lives in `.gtm/routines/config.json`:

```json
{
  "routines": [
    {
      "name": "daily-metrics-pull",
      "schedule_id": "sched_abc123",
      "cron": "0 9 * * *",
      "enabled": true,
      "thresholds": {
        "cpa_increase_pct": 30,
        "ctr_decrease_pct": 25,
        "budget_overspend_pct": 20,
        "email_bounce_rate_pct": 5,
        "churn_spike_multiplier": 2,
        "roas_floor": 1.0
      }
    },
    {
      "name": "weekly-optimization",
      "schedule_id": "sched_def456",
      "cron": "0 10 * * 1",
      "enabled": true,
      "options": {
        "skip_learn_if_no_new_data": true,
        "alert_on_bottleneck_change": true
      }
    },
    {
      "name": "experiment-monitor",
      "schedule_id": "sched_ghi789",
      "cron": "0 18 * * *",
      "enabled": true,
      "options": {
        "significance_level": 0.05,
        "stall_multiplier": 2.0
      }
    },
    {
      "name": "pr-conversion-check",
      "trigger": "github:pull_request",
      "enabled": true,
      "options": {
        "check_posthog": true,
        "check_meta_pixel": true,
        "check_utm": true,
        "check_seo": true
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

## Alert Channels

By default, alerts are saved as JSON files in `.gtm/routines/alerts/`. You can configure additional delivery:

| Channel | Config Key | Description |
|---------|-----------|-------------|
| Console | `"console"` | Saved to `.gtm/routines/alerts/` (default) |
| Slack | `"slack_webhook"` | Posts to a Slack channel via webhook |
| Email | `"email"` | Sends alert email (requires email provider) |

## File Structure

```
.gtm/routines/
  config.json           # Routine configuration and thresholds
  daily-log.md          # One-line daily metrics summaries
  experiment-log.md     # Daily experiment check summaries
  alerts/               # Alert JSON files
    alert-2026-04-14.json
    alert-2026-04-12.json
  errors/               # Error logs from failed routine runs
    error-2026-04-13.json
```

## Without /schedule

If Claude Code's `/schedule` command is not available in your environment, you can still use routines manually:

1. **Daily**: Run `/gtm-metrics` each morning
2. **Weekly**: Run `/gtm-learn`, then `/gtm-diagnose`, then `/gtm-report` each Monday
3. **Experiments**: Run `/gtm-experiment --check-all` each evening
4. **PRs**: Run `/gtm-funnel` before merging landing page PRs

The routine templates in this directory serve as documentation for what each automated workflow does, even if you run them manually.

## Related Commands

| Command | Purpose |
|---------|---------|
| `/gtm-routines setup` | Interactive setup for all routines |
| `/gtm-routines list` | Show all routines and their status |
| `/gtm-routines status` | Detailed status with recent alerts and errors |
| `/gtm-metrics --auto` | What the daily metrics routine executes |
| `/gtm-experiment --check-all` | What the experiment monitor executes |
