---
name: experiment-monitor
description: "Daily routine that checks all active experiments for statistical significance"
---

# Experiment Monitor Routine

## Overview

This routine runs every day at 6:00 PM, checking all active A/B experiments for statistical significance. When an experiment reaches significance, it generates an alert with the winner and recommended action. It also flags stalled experiments that have run longer than expected.

## Schedule

- **Frequency**: Daily
- **Time**: 6:00 PM (configured timezone)
- **Cron expression**: `0 18 * * *`
- **Runtime**: ~1-3 minutes depending on number of active experiments

## What It Does

### Step 1: Load Active Experiments

1. Read all files in `.gtm/experiments/` directory
2. Filter to experiments with `"status": "active"`
3. For each active experiment, load its configuration:
   - Hypothesis and metric
   - Control and treatment variants
   - Required sample size
   - Start date and estimated end date
   - Channel and data source

### Step 2: Pull Current Data

For each active experiment, pull the latest data from its channel:

**Meta Ads experiments**:
- Pull ad-level insights for control and treatment variants
- Extract impressions, clicks, and conversions for the target metric

**Email experiments**:
- Query email provider for open/click/conversion rates per variant
- Or check PostHog for variant-tagged events

**Landing page experiments**:
- Query PostHog for conversion events filtered by feature flag variant
- Or query by URL parameter variant

**Product experiments**:
- Query PostHog feature flag exposure and conversion events

### Step 3: Run Significance Tests

For each experiment, perform a two-proportion z-test:

```
p_control = conversions_control / sample_control
p_treatment = conversions_treatment / sample_treatment
p_pooled = (conv_control + conv_treatment) / (sample_control + sample_treatment)

z = (p_treatment - p_control) / sqrt(p_pooled * (1 - p_pooled) * (1/n_control + 1/n_treatment))
p_value = 2 * (1 - normcdf(abs(z)))
```

Classify each experiment:
- **SIGNIFICANT (p < 0.05)**: Experiment has a clear winner
- **INSUFFICIENT DATA**: Sample size below required, keep running
- **NOT SIGNIFICANT**: Reached required sample but no meaningful difference
- **STALLED**: Running >2x estimated duration without reaching significance

### Step 4: Update Experiment Files

Update each experiment's `.json` file with:
- Latest sample sizes and conversion counts per variant
- Current p-value
- Status change (if applicable)
- `last_checked` timestamp

### Step 5: Generate Alerts

**Significance reached (winner found)**:
```json
{
  "type": "experiment_significant",
  "severity": "high",
  "experiment": "hero-headline-v2",
  "winner": "treatment_b",
  "metric": "signup_rate",
  "improvement": "+18.5%",
  "p_value": 0.023,
  "confidence": "97.7%",
  "recommended_action": "Roll out Treatment B (pain-focused headline). Expected impact: +$2,400/month revenue at current traffic.",
  "decision_needed": true
}
```

**Significant negative result (treatment worse)**:
```json
{
  "type": "experiment_significant_negative",
  "severity": "medium",
  "experiment": "pricing-page-v3",
  "winner": "control",
  "metric": "conversion_rate",
  "decline": "-12.3%",
  "p_value": 0.041,
  "recommended_action": "Keep control. Learning: Removing the free tier option reduces conversions."
}
```

**Experiment stalled**:
```json
{
  "type": "experiment_stalled",
  "severity": "low",
  "experiment": "email-subject-test",
  "runtime_days": 28,
  "estimated_days": 14,
  "sample_progress": "62%",
  "recommended_action": "Consider ending early -- insufficient traffic for this MDE. Either increase traffic to the experiment or accept a larger MDE."
}
```

### Step 6: Update Registry

Update `.gtm/experiments/README.md` with current status:

```markdown
# Experiment Registry
Last checked: {date}

## Active Experiments

| Name | Channel | Metric | Started | Progress | Trend | Status |
|------|---------|--------|---------|----------|-------|--------|
| hero-headline-v2 | landing | signup_rate | Apr 1 | 100% | +18% | SIGNIFICANT |
| email-subject-test | email | open_rate | Mar 28 | 62% | +3% | Running |
| retarget-audience | meta | cpa | Apr 7 | 45% | -8% | Running |

## Completed Experiments

| Name | Result | Winner | Impact | Completed |
|------|--------|--------|--------|-----------|
| cta-button-color | Significant | Treatment A | +12% CTR | Mar 25 |
| pricing-layout | Not significant | -- | No impact | Mar 18 |
```

### Step 7: Save Daily Summary

Append to `.gtm/routines/experiment-log.md`:

```
| 2026-04-14 18:00 | 3 active | 1 significant (hero-headline-v2) | 0 stalled |
```

## Setup Instructions

### Prerequisites

1. At least one active experiment registered via `/gtm-experiment`
2. `.gtm/experiments/` directory with experiment JSON files
3. API credentials for the experiment's data source
4. Claude Code `/schedule` command available

### Create the Routine

```bash
/schedule create "Experiment Monitor" \
  --cron "0 18 * * *" \
  --command "/gtm-experiment --check-all" \
  --description "Check all active A/B experiments for statistical significance"
```

### Customize

Edit `.gtm/routines/config.json`:

```json
{
  "routines": [
    {
      "name": "experiment-monitor",
      "cron": "0 18 * * *",
      "enabled": true,
      "options": {
        "significance_level": 0.05,
        "stall_multiplier": 2.0,
        "alert_on_significance": true,
        "alert_on_stall": true,
        "alert_on_early_trends": false,
        "min_sample_for_trend": 100
      }
    }
  ]
}
```

### Alert Configuration

Alerts are saved to `.gtm/routines/alerts/`. To receive immediate notifications:

```json
{
  "alerts": {
    "experiment_significant": {
      "channel": "slack",
      "slack_webhook": "https://hooks.slack.com/services/..."
    },
    "experiment_stalled": {
      "channel": "console"
    }
  }
}
```

## Statistical Notes

### Sample Size Requirements

The monitor uses these defaults for significance testing:
- Alpha (significance level): 0.05 (95% confidence)
- Power: 0.80 (80% chance of detecting a real effect)
- Test type: Two-tailed (detects both improvements and degradations)

### Multiple Testing Warning

If running 5+ simultaneous experiments, the routine will note: "Running {N} experiments increases false positive risk. Consider Bonferroni correction (alpha = 0.05/{N})." Enable this correction in config if needed.

### Early Peeking

The monitor checks daily but does NOT adjust for multiple comparisons over time (sequential testing). This is intentional -- the 50% sample threshold prevents most early-peeking problems. For critical experiments, consider using sequential testing methods.

## Troubleshooting

- **No experiments found**: The routine will silently complete if `.gtm/experiments/` is empty or has no active experiments.
- **Cannot pull data**: If the experiment's data source is unavailable (e.g., Meta token expired), the routine logs an error and skips that experiment.
- **Wrong sample counts**: Verify that the experiment's variant IDs in the JSON match the actual ad IDs, feature flag keys, or email variant identifiers.
- **Experiment stuck at 0%**: The data source is likely not returning data for the variant IDs. Check that the experiment is actually running and tracking events.

## Related Commands

- `/gtm-experiment` -- Register new experiments or check specific ones
- `/gtm-experiment --check-all` -- Manual check of all experiments
- `/gtm-learn` -- Extract learnings from concluded experiments
- `/gtm-routines status` -- Check routine execution history
