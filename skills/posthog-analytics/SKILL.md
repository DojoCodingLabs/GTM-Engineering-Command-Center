---
name: posthog-analytics
description: PostHog API expertise for GTM dashboards — REST API, HogQL, funnels, cohorts, UTM attribution
---

# PostHog Analytics for GTM

Build and manage analytics dashboards, funnels, and cohort analyses programmatically via the PostHog API. This skill covers the REST API, HogQL query patterns, and GTM-specific dashboard construction.

## Authentication

All API requests require a personal API key or project API key:

```bash
# Headers for all requests
Authorization: Bearer phx_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Content-Type: application/json
```

**Base URL format:** `https://us.posthog.com` (US) or `https://eu.posthog.com` (EU)

**Project ID:** Required for most endpoints. Found in PostHog > Project Settings.

## Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/projects/:id/dashboards/` | GET/POST | List or create dashboards |
| `/api/projects/:id/insights/` | GET/POST | List or create insights (charts) |
| `/api/projects/:id/insights/trend/` | POST | Run trend query |
| `/api/projects/:id/insights/funnel/` | POST | Run funnel query |
| `/api/projects/:id/cohorts/` | GET/POST | List or create cohorts |
| `/api/projects/:id/events/` | GET | List captured events |
| `/api/projects/:id/persons/` | GET | List persons with properties |
| `/api/projects/:id/query/` | POST | Run HogQL queries |
| `/api/projects/:id/feature_flags/` | GET/POST | Manage feature flags |

## Dashboard Creation

### Create a Dashboard

```bash
POST /api/projects/:project_id/dashboards/
{
  "name": "GTM Campaign Performance",
  "description": "Tracks paid acquisition funnel and campaign ROI",
  "filters": {},
  "restriction_level": 21,
  "tags": ["gtm", "paid-acquisition"]
}
```

### Add Insight Tiles to a Dashboard

After creating insights, link them to a dashboard:

```bash
PATCH /api/projects/:project_id/dashboards/:dashboard_id/
{
  "tiles": [
    {
      "insight": INSIGHT_ID,
      "layouts": {
        "sm": {"x": 0, "y": 0, "w": 6, "h": 5},
        "xs": {"x": 0, "y": 0, "w": 1, "h": 5}
      }
    }
  ]
}
```

### Layout Grid
- Dashboard uses a 12-column grid (`sm` breakpoint)
- `w`: width in columns (1-12), `h`: height in rows, `x`/`y`: position
- Standard sizes: full-width = `w:12, h:8`, half = `w:6, h:5`, quarter = `w:3, h:5`

## Insight Types

### Trend Insight (Time Series)

```bash
POST /api/projects/:project_id/insights/
{
  "name": "Daily Signups by UTM Source",
  "filters": {
    "insight": "TRENDS",
    "events": [
      {
        "id": "user_signed_up",
        "type": "events",
        "math": "total",
        "properties": []
      }
    ],
    "breakdown": "$utm_source",
    "breakdown_type": "event",
    "date_from": "-30d",
    "interval": "day"
  }
}
```

### Funnel Insight

```bash
POST /api/projects/:project_id/insights/
{
  "name": "Signup to Payment Funnel",
  "filters": {
    "insight": "FUNNELS",
    "events": [
      {"id": "$pageview", "order": 0, "properties": [{"key": "$current_url", "value": "/landing", "operator": "icontains"}]},
      {"id": "user_signed_up", "order": 1},
      {"id": "onboarding_completed", "order": 2},
      {"id": "plan_selected", "order": 3},
      {"id": "payment_completed", "order": 4}
    ],
    "funnel_window_days": 14,
    "funnel_viz_type": "steps",
    "date_from": "-30d",
    "breakdown": "$utm_source",
    "breakdown_type": "event"
  }
}
```

### Retention Insight

```bash
POST /api/projects/:project_id/insights/
{
  "name": "Weekly Retention by Cohort",
  "filters": {
    "insight": "RETENTION",
    "target_entity": {"id": "$pageview", "type": "events"},
    "returning_entity": {"id": "$pageview", "type": "events"},
    "retention_type": "retention_first_time",
    "period": "Week",
    "total_intervals": 8,
    "date_from": "-60d"
  }
}
```

## HogQL Queries

HogQL is PostHog's SQL dialect built on ClickHouse. Use it for custom analyses that go beyond built-in insights.

### Running a HogQL Query

```bash
POST /api/projects/:project_id/query/
{
  "query": {
    "kind": "HogQLQuery",
    "query": "SELECT properties.$utm_source AS source, count() AS signups FROM events WHERE event = 'user_signed_up' AND timestamp > now() - interval 30 day GROUP BY source ORDER BY signups DESC LIMIT 20"
  }
}
```

### Key HogQL Tables

| Table | Contains |
|-------|----------|
| `events` | All tracked events with properties |
| `persons` | User profiles with properties |
| `sessions` | Session-level data with duration, pages, etc. |
| `groups` | Group analytics (companies, organizations) |
| `cohort_people` | Which persons belong to which cohorts |
| `session_replay_events` | Session replay metadata |

### Key Event Properties

| Property | Description |
|----------|-------------|
| `$current_url` | Page URL where event fired |
| `$referrer` | Referrer URL |
| `$utm_source` | UTM source parameter |
| `$utm_medium` | UTM medium parameter |
| `$utm_campaign` | UTM campaign parameter |
| `$utm_content` | UTM content parameter |
| `$utm_term` | UTM term parameter |
| `$browser` | Browser name |
| `$device_type` | Desktop, Mobile, Tablet |
| `$os` | Operating system |
| `$geoip_country_code` | Country code (ISO) |
| `$geoip_city_name` | City name |

## Cohort Creation

### Property-Based Cohort

```bash
POST /api/projects/:project_id/cohorts/
{
  "name": "Paid Acquisition Users (Last 30d)",
  "is_static": false,
  "groups": [
    {
      "properties": [
        {
          "key": "$utm_medium",
          "value": ["paid", "cpc", "cpm"],
          "operator": "exact",
          "type": "person"
        },
        {
          "key": "$initial_utm_source",
          "value": "meta",
          "operator": "exact",
          "type": "person"
        }
      ],
      "days": 30
    }
  ]
}
```

### Behavioral Cohort

```bash
POST /api/projects/:project_id/cohorts/
{
  "name": "Activated Users (completed onboarding)",
  "is_static": false,
  "groups": [
    {
      "action_id": null,
      "event_id": "onboarding_completed",
      "days": 90,
      "count": 1,
      "count_operator": "gte"
    }
  ]
}
```

## GTM Dashboard Recipes

### Standard GTM Dashboard Tiles

1. **Signup Volume by Source** -- Trend, daily, breakdown by `$utm_source`
2. **Acquisition Funnel** -- Funnel: visit > signup > onboarding > activation > payment
3. **CAC by Campaign** -- HogQL joining event data with spend data
4. **Geo Distribution** -- Trend, breakdown by `$geoip_country_code`
5. **Device Split** -- Trend, breakdown by `$device_type`
6. **Landing Page Performance** -- Trend, breakdown by `$current_url` filtered to `/landing*`
7. **Weekly Retention** -- Retention chart, first-time retention, 8-week window
8. **Conversion Rate Over Time** -- HogQL: signups / unique visitors per day
