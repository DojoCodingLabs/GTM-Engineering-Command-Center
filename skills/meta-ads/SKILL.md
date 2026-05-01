---
name: meta-ads
description: Meta Ads expertise — official `meta ads` CLI (April 2026), campaign structure, Advantage+ Creative, DCO via plural flags, targeting, pixel/CAPI, Graph API patterns for advanced fallbacks
---

# Meta Ads API & Campaign Management

Build, launch, and manage Meta advertising campaigns programmatically. This skill covers the full stack from campaign creation to conversion tracking.

## Default Tooling: `meta ads` CLI

As of plugin v1.5.0, the **primary tool for all Meta Marketing API operations is the official `meta ads` CLI** (Meta, April 2026). Full reference: `rules/ads-cli.md`.

**Use the CLI for:** campaigns, ad sets, ads, creatives (including DCO with plural flags), insights pulls, datasets/pixels, catalogs, account/page lookups.

**Fall back to raw Graph API only for:**
- Custom audiences (hashed lists), lookalikes
- Interest/behavior targeting (`flexible_spec`)
- Detailed age/gender targeting beyond country-level
- ASC+ / Advantage+ Shopping advanced settings (`existing_customer_budget_percentage`)
- Post ID relaunching (`effective_object_story_id`)
- EMQ telemetry (`/{pixel_id}/events?fields=event_match_quality`)
- Advanced `asset_feed_spec` JSON shapes the CLI's flags don't express

The Graph API examples below in this skill remain valid as **conceptual reference** and **fallback patterns** for the items above. For routine deploy/insight work, prefer the CLI commands documented in `rules/ads-cli.md`.

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

## Andromeda & Entity Clustering (April 2026)

Meta's Andromeda retrieval system uses computer vision to scan every creative and assign Entity IDs based on visual pixels, hook pacing, emotional tone, and text overlays. It groups visually similar ads as ONE retrieval ticket. This means 50 ads with the same image but different text = 1 Entity ID = 1 chance in the retrieval lottery.

**Key implications:**
- Minor text variations are dead as a testing strategy. Real diversity requires different images, videos, and formats.
- You need **50-200 visually distinct Entity IDs per week** to give Andromeda enough diversity to find winners.
- There are **4 creative levers** that produce unique Entity IDs: **Persona** (who is shown), **Messaging** (what emotion/angle), **Hook** (first 3 seconds/visual), **Format** (static, video, carousel, UGC).
- Top performers run **395 live ads simultaneously** -- 33% more than bottom performers (Confect.io study: $834M spend, 3,014 advertisers, 1M ads, 115.7B impressions).
- **Broad targeting + high creative diversity = 49% higher ROAS** than lookalike targeting. Let Andromeda find your audience through creative signals, not targeting restrictions.

See: `rules/andromeda-2026.md` for the full Andromeda deep-dive.

## ARM (Adaptive Ranking Model)

ARM is the second stage of Meta's ad delivery pipeline. After Andromeda retrieves ~1,000 candidate ads, ARM ranks them based on predicted conversion probability.

**Critical insight:** ARM reads your conversion data quality BEFORE evaluating your creative. Two advertisers can run identical creative and get ranked by completely different ARM model versions based on their data quality.

- **EMQ 8-10** unlocks the full ARM model -- deep behavioral signals, cross-device tracking, full lookalike expansion.
- **EMQ <7** = surface-level ranking only -- ARM uses basic demographic and interest signals, ignoring the rich conversion patterns that drive efficient delivery.
- Weak EMQ effectively caps your ad performance regardless of creative quality.

## Event Match Quality (EMQ)

EMQ measures how well your conversion events can be matched back to a specific Meta user. Higher EMQ = better attribution = ARM unlocks more powerful ranking.

**Required parameters for EMQ 8-10:**
- `external_id` (hashed email or phone)
- `em` (hashed email)
- `ph` (hashed phone)
- `fbp` / `fbc` (Meta browser/click cookies)
- `ct` (city)
- `client_user_agent`

**5-Minute EMQ Audit:**
1. Open Meta Event Debugger on your top 3 winning creatives
2. Check every `Purchase` event for ALL required parameters above
3. If EMQ <7 on >20% of events, ARM is crippled and your ads are underperforming regardless of creative quality
4. **Fix:** Deploy a server-side CAPI container (Stape or Weld) to ensure all parameters are sent reliably

## Creative Fatigue Indicator (New April 2026)

Meta introduced two new delivery statuses in April 2026:

- **"Creative Limited"** -- Visual similarity detected by Andromeda. Delivery is reduced BEFORE launch because the creative is too similar to existing ads. This is a pre-launch gate.
- **"Creative Fatigue"** -- Audience pool exhausted for this visual. The ad has been seen too many times by the available audience.

**Critical detail:** Fatigue counts ALL exposures across your entire Page, not just within a single ad set. Fatigued organic posts also affect paid delivery. If you posted the same visual organically and it saturated your audience, paid promotion of similar visuals will be throttled.

## Ad Lifecycle Compression

Andromeda has compressed the effective lifespan of ads:

- Ads now **peak in week 1** and rapidly plateau (previously peak was weeks 2-3).
- **Creative rotation every 2-4 weeks is mandatory** (down from the previous 6-8 week cycle).
- Top performers run 395 live ads simultaneously, maintaining constant creative freshness.
- The implication: your creative production pipeline is now your #1 competitive advantage, not your targeting or bid strategy.

## ASC+ (Advantage+ Shopping Campaigns)

ASC+ is the dominant campaign type for ecommerce, now capturing **62% of ecom spend** with a **22% ROAS improvement** over manual campaigns.

**Optimal campaign structure:**
- **1 ASC+ campaign** (60-70% of budget) -- Primary scaling vehicle
- **1 CBO testing campaign** (20-30% of budget) -- Creative testing and audience discovery
- **1 Retargeting campaign** (10-15% of budget) -- Website visitors, cart abandoners, past purchasers

**Existing customer budget cap:** Set to **10-15%** in ASC+ settings. This prevents Meta from spending your acquisition budget on people who would buy anyway.

## Attribution Upheaval (March 2026)

Meta redefined attribution in March 2026:

- **Click-through** now means outbound link clicks only (previously included all clicks).
- **7-day and 28-day view-through attribution windows deprecated.**
- Reported CPAs appear **15-30% higher** than before the change (same performance, different measurement).
- **Source of truth:** Use **blended MER** (Marketing Efficiency Ratio = total ad spend / total revenue) instead of platform-reported ROAS. Every platform over-claims credit.

## Rules Reference

- `rules/andromeda-2026.md` -- Deep-dive on Andromeda retrieval, Entity Clustering, ARM ranking
- `rules/flood-underbid.md` -- Contrarian testing method from $80M+ operators
- `rules/campaign-structure.md` -- Objectives, hierarchy, and post-Andromeda campaign architecture
- `rules/advantage-plus-creative.md` -- Dynamic creative API format + Entity Clustering warnings
- `rules/pixel-setup.md` -- Pixel and CAPI implementation
- `rules/api-gotchas.md` -- Common API errors and fixes
