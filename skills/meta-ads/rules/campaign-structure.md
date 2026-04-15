# Campaign Structure -- Objectives, Promoted Objects, and Hierarchy

## Objective Decision Tree

```
What is your primary business goal?
│
├── Drive purchases/signups with payment
│   └── OUTCOME_SALES
│       optimization_goal: OFFSITE_CONVERSIONS
│       promoted_object: { pixel_id, custom_event_type: "PURCHASE" }
│
├── Collect leads (email, phone, form fill)
│   ├── Using Meta Lead Forms?
│   │   └── OUTCOME_LEADS
│   │       optimization_goal: LEAD_GENERATION
│   │       promoted_object: { page_id }
│   └── Using your own landing page?
│       └── OUTCOME_LEADS
│           optimization_goal: OFFSITE_CONVERSIONS
│           promoted_object: { pixel_id, custom_event_type: "LEAD" }
│
├── Drive website traffic
│   ├── Want any click?
│   │   └── OUTCOME_TRAFFIC
│   │       optimization_goal: LINK_CLICKS
│   │       promoted_object: { pixel_id }  (or omit)
│   └── Want quality visits (page fully loads)?
│       └── OUTCOME_TRAFFIC
│           optimization_goal: LANDING_PAGE_VIEWS
│           promoted_object: { pixel_id }
│
├── Build awareness / reach
│   ├── Maximize unique reach?
│   │   └── OUTCOME_AWARENESS
│   │       optimization_goal: REACH
│   └── Video views?
│       └── OUTCOME_AWARENESS
│           optimization_goal: THRUPLAY
│
├── Drive app installs
│   └── OUTCOME_APP_PROMOTION
│       optimization_goal: APP_INSTALLS
│       promoted_object: { application_id, object_store_url }
│
└── Increase engagement (likes, comments, shares)
    └── OUTCOME_ENGAGEMENT
        optimization_goal: POST_ENGAGEMENT
```

## Campaign Creation API

```bash
POST /act_XXXXX/campaigns
{
  "name": "LATAM - Coding Bootcamp - Conversions - 2026-Q2",
  "objective": "OUTCOME_LEADS",
  "special_ad_categories": [],
  "buying_type": "AUCTION",
  "status": "PAUSED",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
}
```

### Naming Convention

```
[GEO] - [Product/Offer] - [Objective] - [Date/Period]
```
Examples:
- "CO+MX - Bootcamp Launch - Conversions - 2026-Q2"
- "LATAM - Free Trial - Leads - Apr 2026"
- "US - Enterprise Demo - Traffic - Week 15"

## Ad Set Creation

```bash
POST /act_XXXXX/adsets
{
  "name": "CO - 25-35 - Tech Interests - ABO $30",
  "campaign_id": "CAMPAIGN_ID",
  "daily_budget": 3000,
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "promoted_object": {
    "pixel_id": "PIXEL_ID",
    "custom_event_type": "LEAD"
  },
  "targeting": {
    "geo_locations": {"countries": ["CO"]},
    "age_min": 25,
    "age_max": 35,
    "flexible_spec": [
      {"interests": [{"id": "6003139266461", "name": "Entrepreneurship"}]}
    ],
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed"],
    "instagram_positions": ["stream", "story", "reels"]
  },
  "is_dynamic_creative": true,
  "status": "PAUSED",
  "start_time": "2026-04-15T00:00:00-0500"
}
```

### Ad Set Naming Convention

```
[Country] - [Age Range] - [Audience Description] - [Budget Type] $[Amount]
```
Examples:
- "CO - 25-35 - Tech Interests - ABO $30"
- "MX - 28-45 - Lookalike Purchasers 1% - CBO"
- "LATAM - 22-40 - Broad (no targeting) - ABO $50"

## promoted_object Setup

The `promoted_object` tells Meta what conversion event to optimize for.

### For Pixel Events (Website Conversions)

```json
{
  "promoted_object": {
    "pixel_id": "123456789",
    "custom_event_type": "LEAD"
  }
}
```

Valid `custom_event_type` values:
- `LEAD` -- Form submission, signup (no payment)
- `COMPLETE_REGISTRATION` -- Account creation
- `PURCHASE` -- Payment completed
- `ADD_TO_CART` -- Added item to cart
- `INITIATE_CHECKOUT` -- Started checkout process
- `SUBSCRIBE` -- Subscription started
- `CONTENT_VIEW` -- Viewed key content (lower-funnel page)
- Custom events: any custom event name you fire via `fbq('trackCustom', 'EventName')`

### For Lead Forms

```json
{
  "promoted_object": {
    "page_id": "PAGE_ID"
  }
}
```

### For App Installs

```json
{
  "promoted_object": {
    "application_id": "APP_ID",
    "object_store_url": "https://play.google.com/store/apps/details?id=com.example"
  }
}
```

## Budget Configuration

### CBO (Campaign Budget Optimization)

Set budget on the campaign, Meta distributes across ad sets:

```json
// On the campaign:
{
  "daily_budget": 10000,  // $100/day in cents, distributed across ad sets
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
}

// On each ad set: do NOT set daily_budget
// Optionally set minimum/maximum spend limits:
{
  "daily_min_spend_target": 2000,  // At least $20/day to this ad set
  "daily_spend_cap": 5000          // No more than $50/day to this ad set
}
```

### ABO (Ad Set Budget Optimization)

Set budget on each ad set individually:

```json
// On the campaign: do NOT set daily_budget
// On each ad set:
{
  "daily_budget": 3000  // $30/day in cents
}
```

**Important**: When using ABO, the campaign must either have no budget fields or explicitly set `is_adset_budget_sharing_enabled: false`. Omitting this causes confusing errors.

## Bid Strategies

| Strategy | API Value | When to use |
|----------|-----------|------------|
| Lowest cost | `LOWEST_COST_WITHOUT_CAP` | Default. Get most conversions for your budget. |
| Cost cap | `COST_CAP` | Set max CPA. Use `bid_amount` on ad set. May limit spend. |
| Bid cap | `LOWEST_COST_WITH_BID_CAP` | Hard ceiling per auction. Advanced only. |
| Minimum ROAS | `LOWEST_COST_WITH_MIN_ROAS` | E-commerce with known ROAS targets. |

### Recommendation

Start with `LOWEST_COST_WITHOUT_CAP`. Only switch to `COST_CAP` after you have 50+ conversions and know your target CPA. Bid caps are almost never needed for sub-$1000/day budgets.

## Full-Funnel Campaign Structure

For mature ad accounts spending $200+/day:

```
Campaign 1: OUTCOME_AWARENESS (10% of budget)
  └── Ad Set: Broad targeting, video creative
      Goal: Build audience for retargeting

Campaign 2: OUTCOME_LEADS (70% of budget)
  └── Ad Set 1: Interest targeting - Angle A
  └── Ad Set 2: Lookalike 1% of converters - Angle B
  └── Ad Set 3: Broad targeting - Angle C
      Goal: Drive signups/leads

Campaign 3: OUTCOME_LEADS - Retargeting (20% of budget)
  └── Ad Set 1: Website visitors last 30d (exclude converters)
  └── Ad Set 2: Video viewers 75%+ (exclude converters)
  └── Ad Set 3: Lead form openers who didn't submit
      Goal: Convert warm audiences
```

## Audience Exclusions

Always exclude converters from acquisition campaigns:

```json
{
  "targeting": {
    "excluded_custom_audiences": [
      {"id": "EXISTING_CUSTOMERS_AUDIENCE_ID"},
      {"id": "RECENT_CONVERTERS_AUDIENCE_ID"}
    ]
  }
}
```

Create custom audiences for exclusions:
- All purchasers (lifetime)
- All leads (last 90 days)
- All registrations (last 30 days)
