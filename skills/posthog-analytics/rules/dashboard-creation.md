# Dashboard Creation via PostHog API

## Create a Dashboard

```bash
POST /api/projects/:project_id/dashboards/
Content-Type: application/json
Authorization: Bearer phx_XXXXX

{
  "name": "GTM Campaign Performance - April 2026",
  "description": "Tracks paid acquisition funnel from ad click through payment",
  "filters": {},
  "restriction_level": 21,
  "tags": ["gtm", "paid-acquisition", "2026-q2"]
}
```

Response returns the dashboard ID for linking insights.

### restriction_level Values

| Value | Meaning |
|-------|---------|
| 21 | Everyone in the project can edit |
| 37 | Only dashboard creator and admins can edit |

## Create Insights and Link to Dashboard

### Step 1: Create an Insight

```bash
POST /api/projects/:project_id/insights/
{
  "name": "Daily Signups by UTM Source",
  "description": "Tracks signup events broken down by acquisition source",
  "filters": {
    "insight": "TRENDS",
    "events": [
      {
        "id": "user_signed_up",
        "type": "events",
        "math": "total"
      }
    ],
    "breakdown": "$utm_source",
    "breakdown_type": "event",
    "date_from": "-30d",
    "interval": "day"
  },
  "dashboards": [DASHBOARD_ID]
}
```

Including `"dashboards": [DASHBOARD_ID]` automatically creates a tile on the dashboard.

### Step 2: Configure Tile Layout

After creating insights, adjust the layout:

```bash
PATCH /api/projects/:project_id/dashboards/:dashboard_id/
{
  "tiles": [
    {
      "id": TILE_ID,
      "layouts": {
        "sm": {"x": 0, "y": 0, "w": 6, "h": 5, "minW": 3, "minH": 3},
        "xs": {"x": 0, "y": 0, "w": 1, "h": 5}
      }
    },
    {
      "id": TILE_ID_2,
      "layouts": {
        "sm": {"x": 6, "y": 0, "w": 6, "h": 5, "minW": 3, "minH": 3},
        "xs": {"x": 0, "y": 5, "w": 1, "h": 5}
      }
    }
  ]
}
```

### Grid System

The dashboard uses a 12-column responsive grid:

```
sm breakpoint (desktop):
┌──────────────────────────────────────────────────┐
│  w=6, x=0     │  w=6, x=6                       │
│  Half-width    │  Half-width                     │
├──────────────────────────────────────────────────┤
│  w=12, x=0                                      │
│  Full-width                                      │
├──────────────────────────────────────────────────┤
│  w=4, x=0  │  w=4, x=4  │  w=4, x=8            │
│  Third      │  Third     │  Third                │
└──────────────────────────────────────────────────┘
```

### Standard Tile Sizes

| Purpose | Width (w) | Height (h) | Description |
|---------|-----------|------------|-------------|
| KPI card | 3 | 3 | Single number metric |
| Half chart | 6 | 5 | Line chart, bar chart |
| Full chart | 12 | 6 | Funnel, wide trend |
| Full table | 12 | 8 | Detailed data table |

## GTM Dashboard Template

Here is a complete recipe for building a standard GTM performance dashboard:

### Row 1: KPI Cards (y=0)

```bash
# Tile 1: Total Signups This Month
POST /api/projects/:project_id/insights/
{
  "name": "Total Signups (MTD)",
  "filters": {
    "insight": "TRENDS",
    "events": [{"id": "user_signed_up", "type": "events", "math": "total"}],
    "date_from": "-30d",
    "display": "BoldNumber"
  },
  "dashboards": [DASHBOARD_ID]
}
# Layout: x=0, y=0, w=3, h=3

# Tile 2: Conversion Rate
# Layout: x=3, y=0, w=3, h=3

# Tile 3: Cost Per Lead (manual/formula)
# Layout: x=6, y=0, w=3, h=3

# Tile 4: Total Spend (manual entry or imported)
# Layout: x=9, y=0, w=3, h=3
```

### Row 2: Funnel (y=3)

```bash
# Tile 5: Acquisition Funnel
POST /api/projects/:project_id/insights/
{
  "name": "Acquisition Funnel",
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
    "date_from": "-30d"
  },
  "dashboards": [DASHBOARD_ID]
}
# Layout: x=0, y=3, w=12, h=6
```

### Row 3: Trends (y=9)

```bash
# Tile 6: Daily Signups by Source
# Layout: x=0, y=9, w=6, h=5

# Tile 7: Geo Distribution
POST /api/projects/:project_id/insights/
{
  "name": "Signups by Country",
  "filters": {
    "insight": "TRENDS",
    "events": [{"id": "user_signed_up", "type": "events", "math": "total"}],
    "breakdown": "$geoip_country_code",
    "breakdown_type": "event",
    "date_from": "-30d",
    "display": "WorldMap"
  },
  "dashboards": [DASHBOARD_ID]
}
# Layout: x=6, y=9, w=6, h=5
```

### Row 4: Device & Retention (y=14)

```bash
# Tile 8: Device Split
# Layout: x=0, y=14, w=4, h=5

# Tile 9: Weekly Retention
POST /api/projects/:project_id/insights/
{
  "name": "Weekly Retention",
  "filters": {
    "insight": "RETENTION",
    "target_entity": {"id": "user_signed_up", "type": "events"},
    "returning_entity": {"id": "$pageview", "type": "events"},
    "retention_type": "retention_first_time",
    "period": "Week",
    "total_intervals": 8,
    "date_from": "-60d"
  },
  "dashboards": [DASHBOARD_ID]
}
# Layout: x=4, y=14, w=8, h=5
```

## Display Types

| Value | Visual |
|-------|--------|
| `ActionsLineGraph` | Line chart (default for trends) |
| `ActionsBar` | Bar chart |
| `ActionsBarValue` | Horizontal bar chart |
| `ActionsPie` | Pie/donut chart |
| `ActionsTable` | Data table |
| `BoldNumber` | Single large number (KPI) |
| `WorldMap` | Geographic map |
| `FunnelViz` | Funnel visualization (default for funnels) |

## Dashboard Sharing

```bash
# Make dashboard public (shareable link)
PATCH /api/projects/:project_id/dashboards/:dashboard_id/sharing/
{
  "enabled": true
}
```

The response includes a `access_token` that generates a public URL:
```
https://us.posthog.com/shared_dashboard/ACCESS_TOKEN
```
