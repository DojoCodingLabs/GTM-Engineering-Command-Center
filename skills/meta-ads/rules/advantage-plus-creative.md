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
