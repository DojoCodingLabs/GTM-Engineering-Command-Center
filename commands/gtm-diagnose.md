---
name: gtm-diagnose
description: "Find the biggest revenue bottleneck in your AARRR funnel"
argument-hint: ""
---

# Funnel Diagnosis Command

You are the funnel-diagnostician agent. You will read all available data sources, score each AARRR funnel stage, identify the biggest revenue bottleneck, correlate it with cross-channel data, and prescribe the top 3 actions with expected revenue impact.

## Phase 1: Read All Data Sources

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Read `.gtm/funnel/` directory for any existing funnel snapshots.
3. Read `.gtm/metrics/` directory for all available metrics snapshots (Meta Ads, PostHog, Stripe, email, SEO).
4. Read `.gtm/learnings/` directory for accumulated insights.
5. Read `.gtm/MEMORY.md` for historical context.
6. Read `.gtm/experiments/` for any active or completed experiment results.
7. Load product context from `config.product` (name, pricing, target audience).

If fewer than 2 data sources have data, warn: "Limited data available. Diagnosis will rely on qualitative signals. Run `/gtm-metrics` and `/gtm-funnel` first for a more accurate diagnosis."

## Phase 2: Score Each AARRR Stage (0-100)

For each funnel stage, compute a health score from 0 (critical) to 100 (excellent) using available data.

### 2.1: Acquisition (How do users find you?)

Data sources to check:
- Meta Ads: impressions, clicks, CTR, CPC, landing page view rate
- PostHog: total unique visitors, traffic sources breakdown, UTM attribution
- SEO: organic traffic volume, ranking positions (if `.gtm/seo/` exists)
- Email: list growth rate, new subscribers per week

Scoring rubric:
| Score Range | Criteria |
|-------------|----------|
| 80-100 | Multiple active channels, growing traffic week-over-week, CTR above industry avg |
| 60-79 | At least one paid channel active, stable traffic, CTR at or near industry avg |
| 40-59 | Only organic/referral traffic, no paid channels, or paid with high CPC |
| 20-39 | Declining traffic, single source dependency, high bounce rates |
| 0-19 | Near-zero traffic, no active channels, broken tracking |

### 2.2: Activation (Do users have a good first experience?)

Data sources to check:
- PostHog: signup conversion rate, onboarding completion rate, time-to-first-value
- Meta Ads: landing page view rate vs. signup rate
- Product events: first key action completed (if tracked)

Scoring rubric:
| Score Range | Criteria |
|-------------|----------|
| 80-100 | >40% visitor-to-signup, >60% onboarding completion, clear time-to-value |
| 60-79 | 20-40% signup rate, 40-60% onboarding completion |
| 40-59 | 10-20% signup rate, incomplete onboarding flow, unclear first-value moment |
| 20-39 | <10% signup rate, high drop-off during onboarding |
| 0-19 | No signup flow, broken onboarding, no activation tracking |

### 2.3: Retention (Do users come back?)

Data sources to check:
- PostHog: DAU/MAU ratio, retention curves, cohort analysis
- Email: engagement rates on retention emails (if tracked)
- Product events: repeat usage patterns

Scoring rubric:
| Score Range | Criteria |
|-------------|----------|
| 80-100 | DAU/MAU >20%, flat or improving retention curves, strong week-2+ retention |
| 60-79 | DAU/MAU 10-20%, moderate retention, some drop-off after week 1 |
| 40-59 | DAU/MAU 5-10%, steep early drop-off, no retention mechanisms |
| 20-39 | DAU/MAU <5%, most users churn within first week |
| 0-19 | No retention data, no re-engagement systems, ghost-town product |

### 2.4: Revenue (Do users pay?)

Data sources to check:
- Stripe: MRR, conversion rate from free to paid, ARPU, churn rate
- PostHog: purchase/upgrade events
- Product pricing structure from config

Scoring rubric:
| Score Range | Criteria |
|-------------|----------|
| 80-100 | Growing MRR, <5% monthly churn, healthy LTV:CAC ratio (>3:1) |
| 60-79 | Stable MRR, 5-10% churn, LTV:CAC 2-3:1 |
| 40-59 | Low conversion to paid, 10-15% churn, LTV:CAC ~1:1 |
| 20-39 | Declining revenue, >15% churn, CAC exceeds LTV |
| 0-19 | No revenue, no pricing, or broken payment flow |

### 2.5: Referral (Do users tell others?)

Data sources to check:
- PostHog: referral events, share events, invite events
- Product: referral program existence (detected during setup)
- Organic mentions, word-of-mouth signals

Scoring rubric:
| Score Range | Criteria |
|-------------|----------|
| 80-100 | Active referral program, K-factor >0.5, viral loops working |
| 60-79 | Referral program exists, K-factor 0.2-0.5, some organic sharing |
| 40-59 | No formal program but some organic referrals, share buttons exist |
| 20-39 | No referral tracking, no share mechanisms |
| 0-19 | No referral program, no organic sharing, no viral potential designed |

## Phase 3: Identify the Bottleneck

1. Rank the 5 AARRR stages by score (lowest first).
2. The lowest-scoring stage is the primary bottleneck.
3. If two stages are within 5 points of each other, check which one has higher upstream volume (fix the one that leaks the most absolute users).
4. Calculate the "leak rate" at each stage: what percentage of users drop off between this stage and the previous one.

Present the funnel as a visual waterfall:
```
ACQUISITION  [============================] 85/100  -- 10,000 visitors/week
     |
     v  (25% convert)
ACTIVATION   [====================]         62/100  -- 2,500 signups/week
     |
     v  (30% retained)
RETENTION    [============]                 38/100  -- 750 active users  <-- BOTTLENECK
     |
     v  (8% pay)
REVENUE      [===============]              48/100  -- 60 paying users
     |
     v  (2% refer)
REFERRAL     [=======]                      22/100  -- 1 referral/week
```

## Phase 4: Correlate with Cross-Channel Data

For the identified bottleneck, dig deeper:

1. **If Acquisition is the bottleneck**:
   - Which channels are underperforming? Compare Meta vs. organic vs. email vs. SEO
   - Is the issue reach (not enough impressions) or efficiency (high CPC/low CTR)?
   - Are there untapped channels?

2. **If Activation is the bottleneck**:
   - Compare activation rates by traffic source (Meta users vs. organic users)
   - Is the landing page misaligned with ad messaging?
   - Where exactly do users drop off in onboarding?

3. **If Retention is the bottleneck**:
   - Which cohorts retain best (by signup source, by feature used)?
   - Is there an engagement loop or habit trigger?
   - Are retention emails being sent? What are their open/click rates?

4. **If Revenue is the bottleneck**:
   - What is the free-to-paid conversion rate by cohort?
   - Is pricing clear? Is there a trial period?
   - Are there upsell or upgrade prompts?

5. **If Referral is the bottleneck**:
   - Does a referral program exist? What is the incentive?
   - Are there natural share moments in the product?
   - What is the K-factor?

## Phase 5: Prescribe Top 3 Actions

For each of the top 3 recommended actions, provide:

```
ACTION 1: {Title}
Target Stage: {AARRR stage}
Current Score: {X}/100
Expected Impact: {quantified — e.g., "+15 points to Retention score", "reduce CPA by 20%"}
Revenue Impact: {estimated — e.g., "$X/month additional revenue at current conversion rates"}
Effort: Low/Medium/High
Timeline: {days/weeks to implement}
How to execute:
  1. {Step 1}
  2. {Step 2}
  3. {Step 3}
Related command: /gtm-{command} to execute this action
```

Prioritize actions by: (Expected Revenue Impact) / (Effort x Timeline).

## Phase 6: Save Diagnosis

Save the diagnosis to `.gtm/funnel/diagnosis-{YYYY-MM-DD}.json`:

```json
{
  "date": "{ISO date}",
  "scores": {
    "acquisition": {"score": 85, "visitors_weekly": 10000},
    "activation": {"score": 62, "signup_rate": 0.25},
    "retention": {"score": 38, "dau_mau": 0.08},
    "revenue": {"score": 48, "conversion_to_paid": 0.08},
    "referral": {"score": 22, "k_factor": 0.02}
  },
  "bottleneck": "retention",
  "bottleneck_score": 38,
  "actions": [
    {"title": "...", "stage": "retention", "expected_impact": "...", "effort": "medium"}
  ],
  "data_sources_used": ["meta_ads", "posthog", "stripe"]
}
```

Update `.gtm/MEMORY.md` with a one-line diagnosis summary.

## Phase 7: Output

Present the complete diagnosis:

```
AARRR Funnel Diagnosis -- {date}

| Stage       | Score | Health | Key Metric |
|-------------|-------|--------|------------|
| Acquisition | 85    | Good   | 10K visitors/wk |
| Activation  | 62    | Fair   | 25% signup rate |
| Retention   | 38    | Poor   | 8% DAU/MAU |    <-- BOTTLENECK
| Revenue     | 48    | Fair   | 8% free-to-paid |
| Referral    | 22    | Critical | K=0.02 |

Primary Bottleneck: RETENTION (score: 38/100)
Estimated Revenue Leak: $X/month

Top 3 Actions:
1. {action} -- Expected: +$X/month [Effort: Low, Timeline: 1 week]
2. {action} -- Expected: +$X/month [Effort: Medium, Timeline: 2 weeks]
3. {action} -- Expected: +$X/month [Effort: High, Timeline: 1 month]

Diagnosis saved: .gtm/funnel/diagnosis-{date}.json

Next: Run the recommended /gtm-{command} to address the bottleneck.
```

## Error Handling

- **No data at all**: If no metrics snapshots, no PostHog data, and no Meta data exist, tell the user: "No data sources available for diagnosis. Run `/gtm-setup` to configure integrations and `/gtm-metrics` to pull initial data." STOP.
- **Partial data**: Score stages that have data, mark others as "Unknown (no data)" with score null. Still identify the bottleneck among scored stages.
- **Stale data**: If the newest data is older than 14 days, warn: "Data is {X} days old. Diagnosis may not reflect current state. Run `/gtm-metrics` for fresh data."
- **Conflicting signals**: If data sources disagree (e.g., Meta reports high conversions but PostHog shows low signups), note the discrepancy and use the more conservative number for scoring.
