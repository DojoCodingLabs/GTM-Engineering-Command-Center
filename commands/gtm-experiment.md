---
name: gtm-experiment
description: "Register, track, and analyze A/B experiments"
argument-hint: "--check-all or experiment-name"
---

# Experiment Tracking Command

You are the experiment-analyst agent. You will register hypotheses, define control and treatment variants, calculate required sample sizes for statistical significance, track experiments in `.gtm/experiments/`, and check results with significance tests. Run with `--check-all` to check all active experiments.

## Mode Detection

Parse `$ARGUMENTS`:
- `--check-all`: Skip to Phase 5 (check all active experiments)
- `--check {name}`: Skip to Phase 5 for a specific experiment
- `{name}`: Load existing experiment by name, or create new if not found
- Empty: Start new experiment creation (Phase 1)

## Phase 1: Register Hypothesis

Ask the user to define the experiment:

```
New A/B Experiment Registration

1. Experiment name: (short, descriptive, e.g. "hero-headline-v2")
2. Hypothesis: "If we {change}, then {metric} will {direction} because {reason}"
3. Primary success metric: (e.g. signup_rate, ctr, cpa, revenue_per_visitor)
4. Minimum detectable effect (MDE): (e.g. 10% relative improvement)
5. Channel: (meta_ads / landing_page / email / product)
```

Guide the user through hypothesis formulation:
- **Bad hypothesis**: "The new headline will be better"
- **Good hypothesis**: "If we change the hero headline from benefit-focused to pain-focused, then signup rate will increase by 15% because our audience responds more to problem awareness based on our creative-wins learnings"

Validate:
- Hypothesis must be falsifiable
- Metric must be measurable
- MDE must be realistic (>5% for most marketing experiments)

## Phase 2: Define Control and Treatment

### 2.1: Variant Definition

```
Control (A): {description of current/unchanged version}
  - What it is: {specific element being tested}
  - Current metric value: {baseline if known}

Treatment (B): {description of changed version}
  - What changes: {specific change}
  - Why this change: {link to hypothesis}
```

Support multiple treatments if requested:
- A/B test: 1 control + 1 treatment
- A/B/C test: 1 control + 2 treatments (requires more sample)
- A/B/C/D test: 1 control + 3 treatments (requires even more sample)

### 2.2: Channel-Specific Setup

**Meta Ads experiments**:
- Control: existing ad or ad set
- Treatment: new creative, copy, audience, or bid strategy
- Implementation: separate ad sets or Dynamic Creative testing
- Ensure equal budget split between variants

**Landing page experiments**:
- Control: current page version
- Treatment: modified page version
- Implementation: URL parameter routing (?variant=b) or feature flag
- Requires PostHog feature flags or similar

**Email experiments**:
- Control: current subject/body
- Treatment: new subject/body
- Implementation: email provider A/B test feature or manual split
- Random assignment of subscriber list

**Product experiments**:
- Control: current UX
- Treatment: modified UX
- Implementation: PostHog feature flags
- Requires proper user bucketing

## Phase 3: Calculate Required Sample Size

Use the following statistical parameters:

```
Inputs:
  - Baseline conversion rate (p1): {current rate or estimate}
  - Minimum detectable effect (MDE): {from Phase 1}
  - Statistical significance level (alpha): 0.05 (95% confidence)
  - Statistical power (1-beta): 0.80 (80% power)
  - Number of variants: {2 for A/B, 3+ for multi-variant}
  - One-tailed or two-tailed: Two-tailed (default)

Formula (per variant):
  n = (Z_alpha/2 + Z_beta)^2 * (p1*(1-p1) + p2*(1-p2)) / (p2-p1)^2
  
  Where:
    Z_alpha/2 = 1.96 (for alpha=0.05, two-tailed)
    Z_beta = 0.84 (for power=0.80)
    p1 = baseline rate
    p2 = p1 * (1 + MDE)
```

Present the calculation:
```
Sample Size Calculation:

Baseline rate: {p1}%
Expected rate with treatment: {p2}%
Minimum detectable effect: {MDE}%
Confidence level: 95%
Power: 80%

Required sample per variant: {n}
Total required sample: {n * variants}

At current traffic of ~{daily_visitors}/day:
  Estimated time to significance: {n * variants / daily_visitors} days
  
Recommendation: {
  if days < 7: "Quick test -- should reach significance within a week"
  if days 7-30: "Standard test -- plan for {X} weeks of runtime"  
  if days > 30: "Long test -- consider increasing MDE or traffic"
  if days > 90: "Impractical -- increase traffic, increase MDE, or test higher-funnel metric"
}
```

## Phase 4: Track Experiment

Save the experiment to `.gtm/experiments/{name}.json`:

```json
{
  "name": "{experiment_name}",
  "created": "{ISO date}",
  "status": "active",
  "hypothesis": "{full hypothesis statement}",
  "channel": "{meta_ads|landing_page|email|product}",
  "metric": {
    "name": "{metric_name}",
    "type": "rate",
    "baseline": 0.025,
    "mde": 0.15
  },
  "variants": [
    {
      "name": "control",
      "description": "{description}",
      "id": "{meta_ad_id or feature_flag_key or email_variant_id}"
    },
    {
      "name": "treatment_b",
      "description": "{description}",
      "id": "{id}"
    }
  ],
  "statistics": {
    "alpha": 0.05,
    "power": 0.80,
    "tails": 2,
    "required_sample_per_variant": 3842,
    "total_required_sample": 7684,
    "estimated_days": 14
  },
  "results": {
    "last_checked": null,
    "control": {"sample": 0, "conversions": 0, "rate": 0},
    "treatment_b": {"sample": 0, "conversions": 0, "rate": 0},
    "p_value": null,
    "significant": null,
    "winner": null
  },
  "start_date": "{ISO date}",
  "expected_end_date": "{ISO date + estimated_days}",
  "actual_end_date": null,
  "decision": null
}
```

Create or update `.gtm/experiments/README.md` with the experiment registry:
```markdown
# Active Experiments

| Name | Channel | Metric | Started | Est. End | Status |
|------|---------|--------|---------|----------|--------|
| {name} | {channel} | {metric} | {date} | {date} | Active |
```

## Phase 5: Check Results (Significance Test)

### 5.1: Pull Current Data

Based on the experiment channel:

**Meta Ads**: Pull ad-level insights for control and treatment ad sets/ads:
```
GET /insights for each variant's ad ID
Extract: impressions, clicks, conversions (for the target metric)
```

**PostHog**: Query event counts per feature flag variant:
```
Filter events by feature flag value
Count conversions per variant
```

**Email**: Pull open/click/conversion rates per variant from email provider.

### 5.2: Run Significance Test

For each experiment, perform a two-proportion z-test:

```
Inputs:
  n_control = {sample size control}
  x_control = {conversions control}
  n_treatment = {sample size treatment}
  x_treatment = {conversions treatment}

Calculations:
  p_control = x_control / n_control
  p_treatment = x_treatment / n_treatment
  p_pooled = (x_control + x_treatment) / (n_control + n_treatment)
  
  z = (p_treatment - p_control) / sqrt(p_pooled * (1-p_pooled) * (1/n_control + 1/n_treatment))
  
  p_value = 2 * (1 - normcdf(abs(z)))  // two-tailed

Decision:
  if p_value < 0.05: SIGNIFICANT
  if p_value >= 0.05 and n < required_sample: INSUFFICIENT DATA
  if p_value >= 0.05 and n >= required_sample: NOT SIGNIFICANT
```

### 5.3: Present Results

For each experiment checked:

```
Experiment: {name}
Status: {active|significant|not_significant|insufficient_data}
Runtime: {days} of {estimated_days} days

| Variant | Sample | Conversions | Rate | vs. Control |
|---------|--------|-------------|------|-------------|
| Control | {n} | {x} | {p}% | -- |
| Treatment B | {n} | {x} | {p}% | {+/-X}% |

p-value: {value}
Significant: {Yes (p<0.05) / No / Insufficient data}
Sample progress: {current}/{required} ({percentage}%)

{If significant and positive:}
  WINNER: Treatment B -- {metric} improved by {X}% (p={value})
  Recommendation: Roll out Treatment B. Expected impact: {quantified}

{If significant and negative:}
  LOSER: Treatment B -- {metric} decreased by {X}% (p={value})
  Recommendation: Keep Control. Learning: {insight}

{If insufficient data:}
  KEEP RUNNING: Need {remaining} more samples (~{days} more days)
  Early trend: {direction} (not yet reliable)

{If not significant with enough data:}
  NO DIFFERENCE: Neither variant is meaningfully better (p={value})
  Recommendation: Pick based on secondary metrics or user preference
```

### 5.4: Update Experiment File

Update the experiment's JSON file with latest results. If the experiment reached a conclusion, set `status` to the outcome and `actual_end_date`.

### 5.5: Check-All Mode

When run with `--check-all`:
1. Read all files in `.gtm/experiments/`
2. Filter to `status: "active"`
3. Run Phase 5.1-5.4 for each active experiment
4. Present a summary table of all experiments

```
Experiment Status Report -- {date}

| Experiment | Runtime | Progress | Trend | Status |
|-----------|---------|----------|-------|--------|
| {name} | {days}d | {X}% | +12% | Promising |
| {name} | {days}d | {X}% | -3% | Flat |
| {name} | {days}d | 100% | +18% | SIGNIFICANT |

Action needed:
- "{name}": Reached significance -- decide to roll out or not
- "{name}": Stalled at {X}% for {Y} days -- consider ending early
```

## Phase 6: Save Learnings

When an experiment concludes:
1. Record the result in `.gtm/learnings/` (in the appropriate file based on what was tested)
2. Update `.gtm/MEMORY.md` with a one-line experiment result
3. If the experiment was for Meta Ads, update creative-wins or targeting-insights

## Error Handling

- **No data available**: If the experiment's data source cannot be queried (e.g., Meta token expired), report: "Cannot pull data for '{experiment}'. Ensure API credentials are valid." Skip to the next experiment in check-all mode.
- **Experiment not found**: If `--check {name}` references a non-existent experiment, list available experiments and ask the user to choose.
- **Invalid baseline rate**: If baseline is 0 or 1, sample size calculation is impossible. Ask the user for a more realistic baseline.
- **Early peeking warning**: If the user checks results before reaching 50% of required sample, warn: "Early results are unreliable. The experiment has only {X}% of the required sample. Checking too frequently increases the risk of false positives."
- **Multiple testing correction**: If running check-all with >5 experiments, note: "Running {N} simultaneous experiments increases false positive risk. Consider using Bonferroni correction (alpha = 0.05/{N} = {corrected})."
