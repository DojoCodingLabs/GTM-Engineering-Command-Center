---
name: meta-ads
description: Meta Ads API expertise — campaign structure, Advantage+ Creative, targeting, pixel/CAPI, Graph API patterns
---

# Meta Ads API & Campaign Management

Build, launch, and manage Meta advertising campaigns programmatically via the Graph API. This skill covers the full stack from campaign creation to conversion tracking.

## Campaign Hierarchy

```
Ad Account (act_XXXXX)
  └── Campaign (objective: OUTCOME_SALES, OUTCOME_LEADS, OUTCOME_TRAFFIC, etc.)
       └── Ad Set (targeting, budget, schedule, optimization_goal)
            └── Ad (creative: asset_feed_spec with dynamic creative)
```

Every entity is created via `POST /<parent_id>/<edge>` and managed via `POST /<entity_id>`.

## Campaign Objectives (API v21.0+)

| Objective | Use when | optimization_goal |
|-----------|----------|-------------------|
| `OUTCOME_SALES` | Driving purchases, signups with payment | `OFFSITE_CONVERSIONS` |
| `OUTCOME_LEADS` | Lead gen forms, newsletter signups | `LEAD_GENERATION` or `OFFSITE_CONVERSIONS` |
| `OUTCOME_TRAFFIC` | Website visits, landing page views | `LINK_CLICKS` or `LANDING_PAGE_VIEWS` |
| `OUTCOME_AWARENESS` | Brand reach, video views | `REACH` or `THRUPLAY` |
| `OUTCOME_ENGAGEMENT` | Post engagement, page likes | `POST_ENGAGEMENT` |
| `OUTCOME_APP_PROMOTION` | App installs | `APP_INSTALLS` |

## Advantage+ Creative (Dynamic Creative)

**Always use Advantage+ Creative.** Never create ads with single-copy `object_story_spec`. Always use `asset_feed_spec` with `is_dynamic_creative: true` on the ad set.

### Asset Feed Spec Structure

```json
{
  "asset_feed_spec": {
    "bodies": [
      {"text": "Primary text variation 1"},
      {"text": "Primary text variation 2"},
      {"text": "Primary text variation 3"},
      {"text": "Primary text variation 4"},
      {"text": "Primary text variation 5"}
    ],
    "titles": [
      {"text": "Headline variation 1"},
      {"text": "Headline variation 2"},
      {"text": "Headline variation 3"},
      {"text": "Headline variation 4"},
      {"text": "Headline variation 5"}
    ],
    "descriptions": [
      {"text": "Description variation 1"},
      {"text": "Description variation 2"},
      {"text": "Description variation 3"},
      {"text": "Description variation 4"},
      {"text": "Description variation 5"}
    ],
    "images": [
      {"hash": "<image_hash_square_1x1>"},
      {"hash": "<image_hash_vertical_9x16>"}
    ],
    "link_urls": [
      {"website_url": "https://example.com/landing?utm_source=meta&utm_medium=paid"}
    ],
    "call_to_action_types": ["SIGN_UP"],
    "ad_formats": ["SINGLE_IMAGE"]
  }
}
```

### Image Upload (Required Before Ad Creation)

Images MUST be uploaded via the `adimages` endpoint to get an `image_hash`. Never use `image_url` in `link_data` -- it causes error 1443050.

```bash
curl -F "filename=@square.jpg" \
  "https://graph.facebook.com/v21.0/act_XXXXX/adimages?access_token=TOKEN"
```

Response provides `{"hash": "abc123..."}` -- use this hash in `asset_feed_spec.images`.

### Required Image Formats

Always provide at least two aspect ratios:
- **1:1 (Square)** -- 1080x1080px minimum. Used in Feed placements.
- **9:16 (Vertical)** -- 1080x1920px minimum. Used in Stories/Reels.

Optional but recommended:
- **1.91:1 (Landscape)** -- 1200x628px. Used in right column and some Feed placements.

## Targeting

### Interest/Behavior Targeting

```json
{
  "targeting": {
    "geo_locations": {
      "countries": ["CO", "MX", "AR"],
      "location_types": ["home"]
    },
    "age_min": 25,
    "age_max": 45,
    "genders": [0],
    "flexible_spec": [
      {
        "interests": [
          {"id": "6003139266461", "name": "Entrepreneurship"},
          {"id": "6003017386864", "name": "Software engineering"}
        ]
      }
    ],
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed", "video_feeds"],
    "instagram_positions": ["stream", "story", "reels"]
  }
}
```

### Custom Audiences

```json
{
  "targeting": {
    "custom_audiences": [{"id": "AUDIENCE_ID"}],
    "excluded_custom_audiences": [{"id": "PURCHASERS_AUDIENCE_ID"}]
  }
}
```

Types: Website visitors (pixel), Customer lists (email/phone upload), App activity, Video viewers, Lead form openers.

### Lookalike Audiences

Created from a source custom audience:
```bash
POST /act_XXXXX/customaudiences
{
  "name": "Lookalike - Purchasers 1%",
  "subtype": "LOOKALIKE",
  "origin_audience_id": "SOURCE_AUDIENCE_ID",
  "lookalike_spec": {
    "ratio": 0.01,
    "country": "CO"
  }
}
```

## Budget Optimization

### CBO (Campaign Budget Optimization)
- Budget set at campaign level, Meta distributes across ad sets
- Best when: 3+ ad sets, testing multiple audiences, mature campaigns
- Set `daily_budget` or `lifetime_budget` on the campaign
- Ad sets can have `bid_strategy` overrides

### ABO (Ad Set Budget Optimization)
- Budget set at each ad set individually
- Best when: testing specific audiences, need precise budget control, early testing
- Set `daily_budget` on each ad set
- Requires `is_adset_budget_sharing_enabled: false` (or omit campaign budget)

### Decision Tree
```
Need precise control per audience? → ABO
Testing 3+ audiences simultaneously? → CBO
Budget under $50/day total? → ABO (CBO can't distribute well with small budgets)
Scaling a winner? → CBO with proven ad sets
```

## Pixel & CAPI Setup

### Browser Pixel
Track client-side events via the Meta Pixel JavaScript SDK:
```javascript
fbq('track', 'Lead', { currency: 'USD', value: 0.00 });
fbq('track', 'Purchase', { currency: 'USD', value: 29.99 });
fbq('track', 'CompleteRegistration');
```

Environment variable: `VITE_META_PIXEL_ID` for frontend, `META_PIXEL_ID` for backend.

### Conversions API (CAPI)
Server-side event tracking for reliable attribution (bypasses ad blockers):

```typescript
// Edge Function: send server event to Meta CAPI
const response = await fetch(
  `https://graph.facebook.com/v21.0/${PIXEL_ID}/events?access_token=${TOKEN}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      data: [{
        event_name: 'Purchase',
        event_time: Math.floor(Date.now() / 1000),
        action_source: 'website',
        event_source_url: 'https://example.com/thank-you',
        user_data: {
          em: [sha256(email)],  // SHA256 hashed
          client_ip_address: req.headers.get('x-forwarded-for'),
          client_user_agent: req.headers.get('user-agent'),
          fbc: cookies.get('_fbc'),  // Click ID
          fbp: cookies.get('_fbp')   // Browser ID
        },
        custom_data: {
          currency: 'USD',
          value: 29.99
        }
      }]
    })
  }
);
```

### Dual Tracking (Pixel + CAPI)
Use `event_id` deduplication to prevent double-counting:
```javascript
// Frontend (Pixel)
const eventId = crypto.randomUUID();
fbq('track', 'Purchase', { value: 29.99, currency: 'USD' }, { eventID: eventId });

// Backend (CAPI) -- same event_id
{ event_name: 'Purchase', event_id: eventId, ... }
```

## Authentication

### System User Tokens
- Created in Business Manager > Business Settings > System Users
- Must use a **live-mode** app (not development mode)
- Token scopes needed: `ads_management`, `ads_read`, `business_management`
- Error 1885183 = token from dev-mode app. Fix: go live first (only needs Privacy Policy URL for business-type apps)

### Token in Environment
```bash
META_ACCESS_TOKEN=EAAxxxxxxx       # System User token (server-side only)
META_AD_ACCOUNT_ID=act_XXXXX       # Always prefixed with act_
META_PIXEL_ID=XXXXXXXXXX           # 15-16 digit pixel ID
META_APP_ID=XXXXXXXXXX             # App ID from developers.facebook.com
META_APP_SECRET=xxxxxxxx           # App secret (server-side only)
```
