---
name: gtm-learn
description: "Review metrics, save learnings, update strategies"
argument-hint: ""
---

# Self-Learning Loop Command

You are the learning agent. You will pull the latest metrics, compare them to historical data, extract actionable insights, save them as persistent learnings, and update the GTM memory index so future campaigns benefit from accumulated knowledge.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Read `.gtm/MEMORY.md` to understand the current state of learnings.
3. Read all files in `.gtm/learnings/` to load existing insights.
4. Read all metrics snapshots from `.gtm/metrics/` sorted by date (newest first).
   - If no snapshots exist, tell the user: "No metrics data found. Run `/gtm-metrics` first to pull campaign data." Then STOP.

## Phase 1: Load Latest Metrics

1. Read the most recent snapshot from `.gtm/metrics/snapshot-*.json`.
2. If it is older than 24 hours, suggest: "Latest snapshot is from {date}. Run `/gtm-metrics` first for fresh data? (yes/no)"
   - If "yes": tell the user to run `/gtm-metrics` first and come back.
   - If "no": proceed with existing data.
3. Parse the snapshot for:
   - Campaign-level metrics (spend, conversions, CPA, CTR, ROAS)
   - Ad set-level metrics (audience performance)
   - Ad-level metrics (creative performance)
   - Recommendations from the snapshot (if any)

## Phase 2: Historical Comparison

Load previous snapshots and compare:

### 2.1: CPA Trend

```
| Period | CPA | Change | Notes |
|--------|-----|--------|-------|
| {date} | ${X}| —      | Baseline |
| {date} | ${X}| {+/-}% | {context} |
| Latest | ${X}| {+/-}% | {context} |
```

### 2.2: Creative Performance Over Time

For each creative angle that has appeared across multiple snapshots:
- Has CTR improved or declined?
- Has CPA improved or declined?
- Is there a fatigue signal (frequency increase + CTR decline)?

### 2.3: Audience Performance Over Time

For each audience segment across snapshots:
- Which audiences consistently outperform?
- Which audiences started strong but fatigued?
- Are there untested audience segments worth trying?

### 2.4: Budget Efficiency

- Has scaling budget increased CPA (diminishing returns)?
- Is there an optimal daily spend level for this account?
- Which campaigns give the best marginal return on the next dollar?

## Phase 3: Extract Insights

Analyze the data and extract structured insights in three categories:

### 3.1: Creative Wins

What creative approaches work for this product?

Extract insights like:
- "Pain-agitate-solve angle outperforms direct-benefit by X% on CPA"
- "Images with product screenshots outperform abstract graphics"
- "Short primary text (<100 chars) gets higher CTR than long copy"
- "Questions in headlines outperform statements by X%"
- "9:16 creatives in stories/reels have X% lower CPA than feed-only"

Format each insight as:
```
- **Insight**: {finding}
  - Evidence: {data point}
  - Confidence: High/Medium/Low (based on sample size)
  - Action: {what to do with this insight}
```

### 3.2: Targeting Insights

What audiences convert for this product?

Extract insights like:
- "Ages {range} convert at {X}x the rate of other ages"
- "Interest '{name}' has the lowest CPA at ${X}"
- "Broad targeting outperforms narrow interests by X% (algorithm learning)"
- "Retargeting has {X}x higher conversion rate than prospecting"
- "Lookalike audiences reach diminishing returns above {X}%"

### 3.3: Budget Allocation Insights

How should spend be distributed?

Extract insights like:
- "CPA stays stable up to ${X}/day, then increases"
- "Campaign X should get {X}% of budget based on efficiency"
- "Optimal ad set budget is ${X}-${Y}/day for learning phase"
- "Weekend spend efficiency is X% {better/worse} than weekdays"
- "Morning placements outperform evening by X%"

## Phase 4: Save Learnings

Update or create the learning files:

### 4.1: Creative Wins

Write to `.gtm/learnings/creative-wins.md`:

```markdown
# Creative Learnings
Last updated: {date}

## Winning Angles
{list of creative angles ranked by performance}

## Copy Insights
{what copy approaches work}

## Visual Insights
{what visual approaches work}

## Format Insights
{which ad formats/placements work}

## Fatigue History
{which creatives fatigued and when}
```

**Important**: Do NOT overwrite existing entries. Append new insights with dates. If an insight contradicts a previous one, note both with their dates and data — patterns change over time.

### 4.2: Targeting Insights

Write to `.gtm/learnings/targeting-insights.md`:

```markdown
# Targeting Learnings
Last updated: {date}

## Top Audiences
{ranked list of best-performing audience segments}

## Audience Exclusions
{audiences that consistently underperform — avoid in future campaigns}

## Demographic Insights
{age, gender, location patterns}

## Behavioral Insights
{time-of-day, device, placement patterns}
```

### 4.3: Budget Allocation

Write to `.gtm/learnings/budget-allocation.md`:

```markdown
# Budget Allocation Learnings
Last updated: {date}

## Optimal Spend Levels
{per-campaign and per-ad-set recommendations}

## Scaling Thresholds
{where diminishing returns kick in}

## Efficiency Patterns
{day-of-week, time-of-day patterns}

## Historical Budget vs. CPA
| Daily Budget | CPA | ROAS | Period |
|-------------|-----|------|--------|
{table of historical data points}
```

## Phase 5: Update MEMORY.md

Update `.gtm/MEMORY.md` to index all learnings:

```markdown
# GTM Learning Index

## Campaign Learnings
- [{date}] {one-line summary of campaign insight}
- [{date}] {one-line summary}

## Creative Insights
- [{date}] {one-line summary of creative insight}
- [{date}] {one-line summary}

## Targeting Insights
- [{date}] {one-line summary of targeting insight}
- [{date}] {one-line summary}

## API Notes
- [{date}] {any API behavior notes, rate limits hit, workarounds found}

## Community Strategies
<!-- Auto-populated by /gtm-scrape -->
```

Preserve existing entries. Append new ones at the top of each section (reverse chronological).

## Phase 6: Strategy Update

Based on the accumulated learnings, generate an updated strategy recommendation:

```
Learning Loop Complete — {date}

New Insights Saved: {count}
  - Creative: {count}
  - Targeting: {count}
  - Budget: {count}

Key Strategic Shifts:
1. {Most impactful finding and recommended action}
2. {Second most impactful finding}
3. {Third finding}

Files Updated:
  - .gtm/learnings/creative-wins.md
  - .gtm/learnings/targeting-insights.md
  - .gtm/learnings/budget-allocation.md
  - .gtm/MEMORY.md

Suggested Next Actions:
- /gtm-create — Generate new creatives based on winning angles
- /gtm-plan — Build a new plan incorporating these learnings
- /gtm-deploy — Deploy optimized campaign
```

## Phase 7: Confidence Scoring

For each insight, assign a confidence level:

| Confidence | Criteria |
|------------|----------|
| **High** | 100+ conversions, consistent across 2+ weeks, statistically significant |
| **Medium** | 50-100 conversions, consistent across 1+ week |
| **Low** | <50 conversions, or single snapshot, or contradicted by earlier data |

Low-confidence insights should be flagged as "hypothesis — needs more data" and tested in the next campaign cycle.

## Error Handling

- **No metrics snapshots**: Tell the user to run `/gtm-metrics` first. STOP.
- **Only one snapshot**: Generate insights but note "Single data point — all insights are Low confidence. Run the learning loop again after accumulating more data."
- **Conflicting insights**: When new data contradicts old learnings, keep both entries with dates and data. Flag the conflict: "Previous insight ({date}): X. Current data suggests: Y. Recommend testing to resolve."
- **File write errors**: If a learning file can't be written, output the insights to the console so the user can save them manually.
- **Stale data**: If the newest snapshot is older than 14 days, warn: "Data is {X} days old. Campaign conditions may have changed significantly. Run `/gtm-metrics` for current data."
