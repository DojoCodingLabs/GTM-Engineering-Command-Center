# Common HogQL Patterns for GTM Analytics

HogQL is PostHog's SQL dialect built on ClickHouse. Use it for queries that go beyond the built-in insight types.

## Running HogQL via API

```bash
POST /api/projects/:project_id/query/
{
  "query": {
    "kind": "HogQLQuery",
    "query": "SELECT count() FROM events WHERE timestamp > now() - interval 7 day"
  }
}
```

## UTM Attribution Queries

### Signups by UTM Source (Last 30 Days)

```sql
SELECT
  properties.$utm_source AS source,
  properties.$utm_medium AS medium,
  count() AS signups
FROM events
WHERE event = 'user_signed_up'
  AND timestamp > now() - interval 30 day
GROUP BY source, medium
ORDER BY signups DESC
LIMIT 20
```

### Full UTM Breakdown by Campaign

```sql
SELECT
  properties.$utm_source AS source,
  properties.$utm_medium AS medium,
  properties.$utm_campaign AS campaign,
  properties.$utm_content AS content,
  count() AS conversions,
  count(DISTINCT person_id) AS unique_users
FROM events
WHERE event = 'user_signed_up'
  AND timestamp > now() - interval 30 day
  AND properties.$utm_source IS NOT NULL
GROUP BY source, medium, campaign, content
ORDER BY conversions DESC
LIMIT 50
```

### First-Touch Attribution

Attribute conversions to the first UTM source the user ever had:

```sql
SELECT
  first_source,
  count() AS conversions
FROM (
  SELECT
    person_id,
    argMin(properties.$utm_source, timestamp) AS first_source
  FROM events
  WHERE event = 'user_signed_up'
    AND timestamp > now() - interval 30 day
  GROUP BY person_id
)
WHERE first_source IS NOT NULL
GROUP BY first_source
ORDER BY conversions DESC
```

### Last-Touch Attribution

Attribute conversions to the most recent UTM source before conversion:

```sql
SELECT
  last_source,
  count() AS conversions
FROM (
  SELECT
    person_id,
    argMax(properties.$utm_source, timestamp) AS last_source
  FROM events
  WHERE timestamp > now() - interval 30 day
    AND properties.$utm_source IS NOT NULL
  GROUP BY person_id
  HAVING person_id IN (
    SELECT DISTINCT person_id FROM events WHERE event = 'payment_completed' AND timestamp > now() - interval 30 day
  )
)
WHERE last_source IS NOT NULL
GROUP BY last_source
ORDER BY conversions DESC
```

## Event Counts by Date

### Daily Event Volume

```sql
SELECT
  toDate(timestamp) AS day,
  event,
  count() AS total
FROM events
WHERE event IN ('user_signed_up', 'payment_completed', 'onboarding_completed')
  AND timestamp > now() - interval 30 day
GROUP BY day, event
ORDER BY day ASC, event
```

### Hourly Distribution (find best hours to run ads)

```sql
SELECT
  toHour(timestamp) AS hour_utc,
  count() AS signups
FROM events
WHERE event = 'user_signed_up'
  AND timestamp > now() - interval 30 day
GROUP BY hour_utc
ORDER BY hour_utc
```

### Day-of-Week Distribution

```sql
SELECT
  toDayOfWeek(timestamp) AS day_of_week,
  CASE toDayOfWeek(timestamp)
    WHEN 1 THEN 'Monday'
    WHEN 2 THEN 'Tuesday'
    WHEN 3 THEN 'Wednesday'
    WHEN 4 THEN 'Thursday'
    WHEN 5 THEN 'Friday'
    WHEN 6 THEN 'Saturday'
    WHEN 7 THEN 'Sunday'
  END AS day_name,
  count() AS signups
FROM events
WHERE event = 'user_signed_up'
  AND timestamp > now() - interval 90 day
GROUP BY day_of_week, day_name
ORDER BY day_of_week
```

## Property Filtering

### Filter by Country

```sql
SELECT
  properties.$geoip_country_code AS country,
  count() AS events
FROM events
WHERE event = 'user_signed_up'
  AND timestamp > now() - interval 30 day
  AND properties.$geoip_country_code IN ('CO', 'MX', 'AR', 'CL', 'PE')
GROUP BY country
ORDER BY events DESC
```

### Filter by Device Type

```sql
SELECT
  properties.$device_type AS device,
  count() AS signups,
  round(count() / (SELECT count() FROM events WHERE event = 'user_signed_up' AND timestamp > now() - interval 30 day) * 100, 1) AS pct
FROM events
WHERE event = 'user_signed_up'
  AND timestamp > now() - interval 30 day
GROUP BY device
ORDER BY signups DESC
```

### Filter by Landing Page

```sql
SELECT
  properties.$current_url AS page,
  count() AS pageviews,
  count(DISTINCT person_id) AS unique_visitors
FROM events
WHERE event = '$pageview'
  AND timestamp > now() - interval 30 day
  AND properties.$current_url LIKE '%/landing%'
GROUP BY page
ORDER BY pageviews DESC
LIMIT 20
```

## User Segmentation

### Users Who Signed Up But Never Completed Onboarding

```sql
SELECT
  person_id,
  min(timestamp) AS signup_date,
  argMin(properties.$utm_source, timestamp) AS source
FROM events
WHERE event = 'user_signed_up'
  AND timestamp > now() - interval 30 day
  AND person_id NOT IN (
    SELECT DISTINCT person_id FROM events WHERE event = 'onboarding_completed'
  )
GROUP BY person_id
ORDER BY signup_date DESC
LIMIT 100
```

### Power Users (Most Active in Last 7 Days)

```sql
SELECT
  person_id,
  count() AS total_events,
  count(DISTINCT toDate(timestamp)) AS active_days,
  min(timestamp) AS first_event,
  max(timestamp) AS last_event
FROM events
WHERE timestamp > now() - interval 7 day
  AND event NOT IN ('$pageview', '$pageleave', '$autocapture')
GROUP BY person_id
HAVING active_days >= 5
ORDER BY total_events DESC
LIMIT 50
```

### Conversion Rate by Cohort Week

```sql
SELECT
  toStartOfWeek(signup_date) AS cohort_week,
  count() AS total_signups,
  countIf(converted = 1) AS conversions,
  round(countIf(converted = 1) / count() * 100, 1) AS conversion_pct
FROM (
  SELECT
    person_id,
    min(if(event = 'user_signed_up', timestamp, NULL)) AS signup_date,
    max(if(event = 'payment_completed', 1, 0)) AS converted
  FROM events
  WHERE timestamp > now() - interval 90 day
    AND event IN ('user_signed_up', 'payment_completed')
  GROUP BY person_id
  HAVING signup_date IS NOT NULL
)
GROUP BY cohort_week
ORDER BY cohort_week DESC
```

## Session Analysis

### Average Session Duration by Source

```sql
SELECT
  properties.$utm_source AS source,
  round(avg($session_duration), 0) AS avg_duration_seconds,
  count() AS sessions
FROM sessions
WHERE min_timestamp > now() - interval 30 day
  AND properties.$utm_source IS NOT NULL
GROUP BY source
HAVING sessions > 10
ORDER BY avg_duration_seconds DESC
```

### Pages Per Session by Source

```sql
SELECT
  properties.$utm_source AS source,
  round(avg(pageview_count), 1) AS avg_pages,
  count() AS sessions
FROM sessions
WHERE min_timestamp > now() - interval 30 day
  AND properties.$utm_source IS NOT NULL
GROUP BY source
HAVING sessions > 10
ORDER BY avg_pages DESC
```

## Performance Tips

- Use `toDate(timestamp)` instead of `DATE(timestamp)` -- ClickHouse native function
- Filter on `timestamp` first (it's the partition key) -- dramatically speeds queries
- Use `count(DISTINCT person_id)` sparingly on large datasets -- expensive operation
- Add `LIMIT` to all exploratory queries -- unbounded queries can timeout
- Use `IN` instead of `OR` for multiple value checks
- Prefer `argMin`/`argMax` over subqueries for first/last value lookups
