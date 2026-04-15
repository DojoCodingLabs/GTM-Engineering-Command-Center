# Funnel Analysis Patterns

## Standard Acquisition Funnel

The core GTM funnel tracks users from first visit through payment:

```
Visit (landing page) → Signup → Onboarding → Plan Selection → Payment
```

### API-Based Funnel

```bash
POST /api/projects/:project_id/insights/
{
  "name": "Full Acquisition Funnel - Last 30 Days",
  "filters": {
    "insight": "FUNNELS",
    "events": [
      {
        "id": "$pageview",
        "order": 0,
        "name": "Landing Page Visit",
        "properties": [
          {"key": "$current_url", "value": "/landing", "operator": "icontains"}
        ]
      },
      {
        "id": "user_signed_up",
        "order": 1,
        "name": "Signup"
      },
      {
        "id": "onboarding_completed",
        "order": 2,
        "name": "Onboarding Complete"
      },
      {
        "id": "plan_selected",
        "order": 3,
        "name": "Plan Selected"
      },
      {
        "id": "payment_completed",
        "order": 4,
        "name": "Payment"
      }
    ],
    "funnel_window_days": 14,
    "funnel_viz_type": "steps",
    "date_from": "-30d",
    "breakdown": "$utm_source",
    "breakdown_type": "event"
  }
}
```

### HogQL Funnel Query

For more control, use HogQL with windowFunnel:

```sql
SELECT
  source,
  countIf(steps >= 1) AS visits,
  countIf(steps >= 2) AS signups,
  countIf(steps >= 3) AS onboarded,
  countIf(steps >= 4) AS plan_selected,
  countIf(steps >= 5) AS paid,
  round(countIf(steps >= 2) / countIf(steps >= 1) * 100, 1) AS visit_to_signup_pct,
  round(countIf(steps >= 5) / countIf(steps >= 1) * 100, 1) AS visit_to_paid_pct
FROM (
  SELECT
    person_id,
    argMin(properties.$utm_source, timestamp) AS source,
    windowFunnel(14 * 86400)(
      toUnixTimestamp(timestamp),
      event = '$pageview' AND properties.$current_url LIKE '%/landing%',
      event = 'user_signed_up',
      event = 'onboarding_completed',
      event = 'plan_selected',
      event = 'payment_completed'
    ) AS steps
  FROM events
  WHERE timestamp > now() - interval 30 day
  GROUP BY person_id
)
GROUP BY source
ORDER BY visits DESC
```

## Funnel Variations

### By UTM Campaign

Track which specific campaigns drive the most conversions:

```bash
{
  "filters": {
    "insight": "FUNNELS",
    "events": [ /* same funnel steps */ ],
    "breakdown": "$utm_campaign",
    "breakdown_type": "event",
    "funnel_window_days": 14,
    "date_from": "-30d"
  }
}
```

### By Country

Compare funnel performance across LATAM markets:

```bash
{
  "filters": {
    "insight": "FUNNELS",
    "events": [ /* same funnel steps */ ],
    "breakdown": "$geoip_country_code",
    "breakdown_type": "event",
    "funnel_window_days": 14,
    "date_from": "-30d"
  }
}
```

### By Device Type

Identify if mobile users convert differently than desktop:

```bash
{
  "filters": {
    "insight": "FUNNELS",
    "events": [ /* same funnel steps */ ],
    "breakdown": "$device_type",
    "breakdown_type": "event",
    "funnel_window_days": 14,
    "date_from": "-30d"
  }
}
```

## Time-to-Convert Analysis

How long does it take users to move through the funnel?

```sql
SELECT
  round(avg(signup_delay_hours), 1) AS avg_hours_to_signup,
  round(avg(payment_delay_hours), 1) AS avg_hours_to_payment,
  round(median(signup_delay_hours), 1) AS median_hours_to_signup,
  round(median(payment_delay_hours), 1) AS median_hours_to_payment
FROM (
  SELECT
    person_id,
    dateDiff('hour',
      min(if(event = '$pageview' AND properties.$current_url LIKE '%/landing%', timestamp, NULL)),
      min(if(event = 'user_signed_up', timestamp, NULL))
    ) AS signup_delay_hours,
    dateDiff('hour',
      min(if(event = '$pageview' AND properties.$current_url LIKE '%/landing%', timestamp, NULL)),
      min(if(event = 'payment_completed', timestamp, NULL))
    ) AS payment_delay_hours
  FROM events
  WHERE timestamp > now() - interval 30 day
    AND event IN ('$pageview', 'user_signed_up', 'payment_completed')
  GROUP BY person_id
  HAVING signup_delay_hours IS NOT NULL
)
```

## Drop-Off Analysis

Identify where users abandon the funnel:

```sql
SELECT
  'Visit → Signup' AS step,
  countIf(reached_signup = 0 AND reached_visit = 1) AS dropped,
  round(countIf(reached_signup = 0 AND reached_visit = 1) / countIf(reached_visit = 1) * 100, 1) AS drop_pct
FROM (
  SELECT
    person_id,
    max(if(event = '$pageview' AND properties.$current_url LIKE '%/landing%', 1, 0)) AS reached_visit,
    max(if(event = 'user_signed_up', 1, 0)) AS reached_signup,
    max(if(event = 'onboarding_completed', 1, 0)) AS reached_onboarding,
    max(if(event = 'payment_completed', 1, 0)) AS reached_payment
  FROM events
  WHERE timestamp > now() - interval 30 day
  GROUP BY person_id
)

UNION ALL

SELECT
  'Signup → Onboarding' AS step,
  countIf(reached_onboarding = 0 AND reached_signup = 1) AS dropped,
  round(countIf(reached_onboarding = 0 AND reached_signup = 1) / countIf(reached_signup = 1) * 100, 1) AS drop_pct
FROM ( /* same subquery */ )

UNION ALL

SELECT
  'Onboarding → Payment' AS step,
  countIf(reached_payment = 0 AND reached_onboarding = 1) AS dropped,
  round(countIf(reached_payment = 0 AND reached_onboarding = 1) / countIf(reached_onboarding = 1) * 100, 1) AS drop_pct
FROM ( /* same subquery */ )
```

## Funnel Benchmarks

| Step | Healthy conversion rate | Red flag |
|------|------------------------|----------|
| Visit to Signup | 5-15% | Below 3% |
| Signup to Onboarding Complete | 40-70% | Below 30% |
| Onboarding to Plan Selection | 20-40% | Below 15% |
| Plan Selection to Payment | 30-60% | Below 20% |
| Overall Visit to Payment | 1-5% | Below 0.5% |

These benchmarks are for B2B SaaS / EdTech with freemium model. Adjust based on your vertical and pricing.

## Funnel Window Configuration

`funnel_window_days` defines how long a user has to complete the funnel:

| Product type | Recommended window |
|-------------|-------------------|
| Impulse purchase (<$50) | 3-7 days |
| Considered purchase ($50-500) | 14 days |
| Enterprise / High-ticket (>$500) | 30-60 days |
| Free trial conversion | Trial length + 7 days |

Setting the window too wide inflates conversion rates with non-causal correlations. Too narrow misses legitimate delayed conversions.
