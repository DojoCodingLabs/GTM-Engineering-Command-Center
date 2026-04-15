# Advantage+ Creative (Dynamic Creative) -- API Format

Advantage+ Creative lets Meta's algorithm test all combinations of your creative assets (images, headlines, body text, descriptions) and serve the best-performing combination to each user.

## Required Setup

### Ad Set Level

The ad set MUST have `is_dynamic_creative: true`:

```bash
POST /act_XXXXX/adsets
{
  "name": "US - Interest Targeting - Dynamic",
  "campaign_id": "CAMPAIGN_ID",
  "daily_budget": 5000,  # in cents ($50.00)
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "promoted_object": {"pixel_id": "PIXEL_ID", "custom_event_type": "LEAD"},
  "targeting": { ... },
  "is_dynamic_creative": true,
  "status": "PAUSED",
  "start_time": "2026-04-15T00:00:00-0500"
}
```

### Ad Level -- asset_feed_spec

The ad creative MUST use `asset_feed_spec`, never `object_story_spec`:

```bash
POST /act_XXXXX/ads
{
  "name": "Dynamic Creative - Pain Angle",
  "adset_id": "ADSET_ID",
  "status": "PAUSED",
  "creative": {
    "asset_feed_spec": {
      "bodies": [
        {"text": "Still spending weekends on manual deployments? Ship faster with automated CI/CD pipelines that just work. Join 2,400 engineers who already made the switch."},
        {"text": "Your competitors deploy 10x a day. You deploy once a week. The gap is growing. Close it with our battle-tested deployment platform."},
        {"text": "3 things killing your engineering velocity:\n1. Manual deployments\n2. Flaky tests\n3. No observability\n\nWe fix all three. Start your free trial today."},
        {"text": "Maria was deploying once a month. After switching to our platform, her team ships daily. Zero downtime. Zero stress. Here's how she did it."},
        {"text": "Imagine deploying with confidence every single time. No more 2am rollbacks. No more broken builds. Just clean, automated releases. That's what 2,400 teams already experience."}
      ],
      "titles": [
        {"text": "Deploy 10x Faster, Starting Today"},
        {"text": "Stop Manual Deployments Forever"},
        {"text": "2,400 Teams Ship Daily With This"},
        {"text": "Your CI/CD Pipeline Is Broken"},
        {"text": "Free Trial: Automated Deployments"}
      ],
      "descriptions": [
        {"text": "Set up in 4 minutes. No credit card required."},
        {"text": "Trusted by 2,400 engineering teams worldwide."},
        {"text": "14-day free trial. Full access. Cancel anytime."},
        {"text": "Zero-downtime deployments, guaranteed."},
        {"text": "From commit to production in under 3 minutes."}
      ],
      "images": [
        {"hash": "abc123square1x1hash"},
        {"hash": "def456vertical9x16hash"}
      ],
      "videos": [],
      "link_urls": [
        {"website_url": "https://example.com/start?utm_source=meta&utm_medium=paid&utm_campaign=deploy_pain"}
      ],
      "call_to_action_types": ["SIGN_UP"],
      "ad_formats": ["SINGLE_IMAGE"]
    },
    "object_story_spec": {
      "page_id": "PAGE_ID",
      "instagram_actor_id": "INSTAGRAM_ACCOUNT_ID"
    }
  }
}
```

## Image Upload Workflow

Images MUST be uploaded first to get an `image_hash`. Never use `image_url`.

### Step 1: Upload Image

```bash
curl -X POST \
  -F "filename=@creative-square-1080x1080.jpg" \
  "https://graph.facebook.com/v21.0/act_XXXXX/adimages?access_token=TOKEN"
```

Response:
```json
{
  "images": {
    "creative-square-1080x1080.jpg": {
      "hash": "abc123square1x1hash",
      "url": "https://scontent.xx.fbcdn.net/..."
    }
  }
}
```

### Step 2: Use Hash in asset_feed_spec

```json
"images": [
  {"hash": "abc123square1x1hash"},
  {"hash": "def456vertical9x16hash"}
]
```

### Required Aspect Ratios

Always upload at least two formats:
- **1:1 (1080x1080)** -- Feed placements on Facebook and Instagram
- **9:16 (1080x1920)** -- Stories and Reels on both platforms

### Image Specifications
- Format: JPG or PNG
- Max file size: 30MB
- Min resolution: 1080px on shortest side
- No more than 20% text overlay (not enforced but affects delivery)

## Asset Limits per Ad

| Asset Type | Minimum | Maximum | Recommended |
|------------|---------|---------|-------------|
| Bodies (primary text) | 1 | 5 | 5 |
| Titles (headlines) | 1 | 5 | 5 |
| Descriptions | 1 | 5 | 5 |
| Images | 1 | 10 | 2-3 (different ratios) |
| Videos | 0 | 10 | 1-2 |
| Link URLs | 1 | 1 | 1 |
| CTA types | 1 | 1 | 1 |

## Required Fields Checklist

Every Advantage+ Creative ad MUST have:
- [ ] `is_dynamic_creative: true` on the ad set
- [ ] `asset_feed_spec` (not `object_story_spec` for creative content)
- [ ] At least 1 body, 1 title, 1 description
- [ ] At least 1 image hash (uploaded via adimages endpoint)
- [ ] Exactly 1 link_url
- [ ] Exactly 1 call_to_action_types value
- [ ] `page_id` in `object_story_spec` (identifies the Facebook Page)
- [ ] `instagram_actor_id` in `object_story_spec` (required for Instagram placements)

## Retrieving Performance Breakdown

To see which combination is winning:

```bash
GET /AD_ID/insights?fields=impressions,clicks,conversions,cost_per_action_type
  &breakdowns=body_asset,title_asset,description_asset,image_asset
  &date_preset=last_7d
```

This shows performance per asset, helping you identify winners and losers.

## Common Errors

| Error Code | Cause | Fix |
|------------|-------|-----|
| 1443050 | Using `image_url` instead of `image_hash` | Upload via adimages endpoint, use hash |
| 100 | Missing required field in asset_feed_spec | Check all required fields above |
| 1487390 | `object_story_spec` used instead of `asset_feed_spec` | Switch to asset_feed_spec format |
| 1815946 | Missing `instagram_actor_id` | Add Instagram account ID to object_story_spec |

## Entity Clustering Warning (April 2026)

Andromeda's Entity Clustering system groups visually similar creatives as a single retrieval entity. This fundamentally changes how `asset_feed_spec` text variations work.

**The problem:** If you upload 1 image and provide 5 body texts + 5 titles + 5 descriptions, Advantage+ Creative will generate up to 125 combinations. But since they ALL share the same visual, Andromeda treats them as **1 Entity ID** = **1 retrieval ticket** in the auction.

```
50 ads with same image + different text = 1 retrieval ticket
5 ads with different images + same text = 5 retrieval tickets
```

**What "real diversity" means now:**
- Different images (not crops/filters of the same image -- genuinely different visuals)
- Different video content (different hooks, different footage, different pacing)
- Different formats (static image vs. video vs. carousel = different entity types)
- Different visual compositions (faces vs. no faces, dark vs. light, close-up vs. wide)

**Practical approach:** Use `asset_feed_spec` text variations for copy optimization within a single visual entity. But create SEPARATE ads for each visually distinct creative. Don't rely on text variations alone to provide creative diversity.

## ASC+ (Advantage+ Shopping Campaigns)

ASC+ is now the dominant campaign type for ecommerce, capturing 62% of ecom spend with 22% higher ROAS than manual campaigns.

### ASC+ Structure

```json
{
  "objective": "OUTCOME_SALES",
  "buying_type": "AUCTION",
  "special_ad_categories": [],
  "smart_promotion_type": "GUIDED_CREATION",
  "is_budget_schedule_enabled": false
}
```

### Budget Allocation

- **60-70%** of total ad budget goes to ASC+
- **20-30%** to CBO testing campaign for creative discovery
- **10-15%** to dedicated retargeting

### Existing Customer Budget Cap

Set the existing customer percentage cap at **10-15%** in ASC+ settings. This prevents Meta from spending acquisition budget on existing customers who would convert anyway. Without this cap, ASC+ will over-index on easy conversions (existing customers) at the expense of new customer acquisition.

### Catalog Ads with Design Rules

Catalog ads with Design Rules produce **+31% ROAS** and critically, they do NOT reset learning phase when updated. You can iterate on catalog creative rules without losing optimization data.

### Video Catalog Ads

Video Catalog Ads are treated as a **different entity type** by Andromeda. Adding video catalog ads to an ASC+ campaign effectively doubles your retrieval tickets compared to static catalog alone. Always include both formats.

## Optimization Event Ladder

Start new campaigns with a lower-funnel-but-higher-volume event, then graduate up:

1. **Start with Add to Cart (ATC) optimization** -- Higher volume event, exits learning phase 2-3x faster than Purchase optimization
2. **Once stable (50+ ATC events/week, consistent CPA):** Switch to Purchase optimization
3. **Never start with Purchase optimization** on a cold campaign -- insufficient signal density causes erratic delivery

This is especially critical for ASC+ campaigns where the algorithm needs fast feedback loops.

## Cost Cap Graduation

After a campaign exits the learning phase with Highest Volume (Lowest Cost) bid strategy:

1. **Graduate to Cost Cap** -- Set cost cap at 1.2x your current CPA
2. This creates a "Hunger Games" dynamic among your ads -- only the most efficient survive
3. Gradually tighten the cost cap as performance stabilizes
4. **Never start a new campaign with Cost Cap** -- the algorithm needs unconstrained learning first

The graduation sequence: **Highest Volume → Cost Cap → Bid Cap (for catch-all only)**
