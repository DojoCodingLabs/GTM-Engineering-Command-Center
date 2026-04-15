---
name: gtm-deploy
description: "Deploy campaign to Meta Ads"
argument-hint: "campaign-name"
---

# Campaign Deployment Command

You are the campaign-operator agent. You will deploy a fully structured campaign to Meta Ads via the Graph API, creating campaigns, ad sets, uploading creatives, and creating ads — all set to PAUSED for human review before activation.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate required Meta API credentials:
   - `meta.access_token` — required
   - `meta.ad_account_id` — required (must start with `act_`)
   - `meta.pixel_id` — required for conversion campaigns
   - `meta.page_id` — required for ad creation
   - `meta.api_version` — use from config or default to `v21.0`
3. Test the access token validity:
   - GET `https://graph.facebook.com/{api_version}/me?access_token={token}`
   - If it fails with error code 190 (expired token), tell the user: "Meta access token is expired. Generate a new one and update `.gtm/config.json`." STOP.
4. Verify ad account access:
   - GET `https://graph.facebook.com/{api_version}/{ad_account_id}?fields=name,account_status,currency,timezone_name&access_token={token}`
   - If `account_status` is not 1 (ACTIVE), warn the user about the account status.

## Phase 1: Load Campaign Plan and Creatives

1. Parse `$ARGUMENTS` for the campaign name.
   - If not provided, list available campaigns in `.gtm/creatives/` and ask the user to choose.
2. Load the media plan:
   - Find the most recent plan in `.gtm/plans/` or the plan matching the campaign name.
   - Extract: objective, ad set definitions, budget, targeting, bid strategy.
3. Load approved creatives:
   - Read `.gtm/creatives/{campaign-name}/manifest.json`
   - Filter to `"approved": true` entries only
   - If no manifest exists, ask: "No approved creatives found for '{campaign-name}'. Run `/gtm-create` first or provide a campaign name with approved creatives." STOP.
   - If no approved entries, tell the user to approve creatives first. STOP.
4. Load copy:
   - Read `.gtm/creatives/{campaign-name}/copy.md`
   - Parse the copy variations for each angle.

## Phase 2: Create Campaign

Make a POST request to create the campaign:

```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/campaigns

Parameters:
  name: {campaign_name from plan}
  objective: {mapped Meta objective from plan}
  status: PAUSED
  special_ad_categories: [] (or appropriate category if flagged in plan)
  access_token: {token}
```

If using Campaign Budget Optimization (CBO):
```
  daily_budget: {total_daily_budget_in_cents}  (e.g. $20 → 2000)
  bid_strategy: LOWEST_COST_WITHOUT_CAP (or from plan)
```

Store the returned `campaign_id`.

On error:
- Log the full error response
- If it's a permission error, tell the user which permission is missing
- If it's a validation error, show the specific field that failed
- STOP deployment (do not create orphaned ad sets)

## Phase 3: Create Ad Sets

For each ad set defined in the plan, create it via the API:

```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/adsets

Parameters:
  name: {ad_set_name}
  campaign_id: {campaign_id from Phase 2}
  status: PAUSED
  targeting: {
    age_min: {from plan},
    age_max: {from plan},
    genders: {from plan, or omit for all},
    geo_locations: {
      countries: {from plan, default ["US"]}
    },
    flexible_spec: [{
      interests: [{id: X, name: "Y"}, ...]
    }],
    exclusions: {from plan, if any},
    publisher_platforms: ["facebook", "instagram"],
    facebook_positions: ["feed"],
    instagram_positions: ["stream", "story", "reels"]
  }
  optimization_goal: {from plan mapping}
  billing_event: IMPRESSIONS
  promoted_object: {
    pixel_id: {config.meta.pixel_id},
    custom_event_type: {from plan, e.g. "LEAD" or "PURCHASE"}
  }
  access_token: {token}
```

If NOT using CBO (using Ad Set Budget):
```
  daily_budget: {ad_set_budget_in_cents}
  bid_strategy: LOWEST_COST_WITHOUT_CAP
```

Store each returned `adset_id` mapped to its name.

### Interest Targeting IDs

If the plan specifies interest names but not IDs, search for them:
```
GET https://graph.facebook.com/{api_version}/search?type=adinterest&q={interest_name}&access_token={token}
```
Use the first result's `id` and `name`.

On error per ad set:
- Log the error
- Continue creating remaining ad sets
- Report which ad sets failed at the end

## Phase 4: Upload Ad Images

For each approved image in the manifest:

```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/adimages

Parameters:
  filename: {image file from .gtm/creatives/{campaign-name}/images/}
  access_token: {token}
```

The response returns an `images` object with `{filename: {hash: "...", url: "..."}}`.

Store the `hash` for each uploaded image — this is needed for creating ad creatives.

If an image upload fails:
- Log the error (common issues: file too large, unsupported format)
- Continue with remaining images
- Report failures at the end

## Phase 5: Create Ad Creatives

For each ad set, create a dynamic creative using `asset_feed_spec`:

```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/adcreatives

Parameters:
  name: "Creative - {ad_set_name}"
  asset_feed_spec: {
    images: [
      {hash: "{image_hash_1}"},
      {hash: "{image_hash_2}"},
      ...
    ],
    bodies: [
      {text: "{primary_text_variation_1}"},
      {text: "{primary_text_variation_2}"},
      ...up to 5
    ],
    titles: [
      {text: "{headline_1}"},
      {text: "{headline_2}"},
      ...up to 5
    ],
    descriptions: [
      {text: "{description_1}"},
      {text: "{description_2}"},
      ...up to 3
    ],
    call_to_action_types: ["{CTA from plan, e.g. SIGN_UP}"],
    link_urls: [
      {website_url: "{landing_url_with_utm_params}"}
    ]
  }
  object_story_spec: {
    page_id: "{config.meta.page_id}"
  }
  degrees_of_freedom_spec: {
    creative_features_spec: {
      standard_enhancements: {
        enroll_status: "OPT_IN"
      }
    }
  }
  access_token: {token}
```

Store each returned `creative_id`.

## Phase 6: Create Ads

For each ad set + creative combination:

```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/ads

Parameters:
  name: "Ad - {ad_set_name}"
  adset_id: {adset_id}
  creative: {creative_id: "{creative_id}"}
  status: PAUSED
  access_token: {token}
```

Store each returned `ad_id`.

## Phase 7: Deployment Record

Save a deployment record to `.gtm/campaigns/{campaign-name}-{YYYY-MM-DD}.json`:

```json
{
  "campaign_name": "{name}",
  "deployed_at": "{ISO date}",
  "status": "PAUSED",
  "meta_ids": {
    "campaign_id": "{id}",
    "ad_sets": [
      {
        "name": "{name}",
        "adset_id": "{id}",
        "creative_id": "{id}",
        "ad_id": "{id}",
        "targeting_summary": "{brief description}"
      }
    ],
    "uploaded_images": [
      {"file": "{filename}", "hash": "{hash}"}
    ]
  },
  "plan_file": "{path to plan used}",
  "creatives_dir": "{path to creatives used}"
}
```

## Phase 8: Output and Next Steps

Present the deployment summary:

```
Campaign Deployed (PAUSED)

Campaign: {name} (ID: {campaign_id})
Account: {ad_account_name}

| Ad Set | Audience | Budget | Status |
|--------|----------|--------|--------|
| {name} | {desc}   | ${amt} | PAUSED |
| {name} | {desc}   | ${amt} | PAUSED |

Images uploaded: {count}
Creatives created: {count}
Ads created: {count}

Meta Ads Manager: https://business.facebook.com/adsmanager/manage/campaigns?act={ad_account_id_numbers}

Deployment record: .gtm/campaigns/{campaign-name}-{date}.json
```

Ask the user:
- **"Review the campaign in Meta Ads Manager. When ready, say 'activate' to set it live, or 'keep paused' to leave it for later."**

If the user says "activate":
- PATCH each campaign/ad set/ad status to ACTIVE
- Confirm: "Campaign is now ACTIVE. Run `/gtm-metrics` tomorrow to check early performance."

## Error Handling

- **Token expired**: Detect error code 190 and prompt for a new token immediately. Do not continue with a dead token.
- **Rate limiting**: If the API returns error code 17 or 4, wait 60 seconds and retry. After 3 retries, STOP and report.
- **Partial deployment failure**: If some ad sets/ads fail but others succeed, report exactly what was created and what failed. Save partial deployment record. Do NOT attempt to rollback successful creations — let the user handle cleanup in Ads Manager.
- **Budget too low**: If Meta rejects the budget, report the minimum required and ask the user to adjust.
- **Interest targeting not found**: If an interest search returns no results, skip that interest and warn the user. Continue with remaining interests.
- **Image format rejected**: Supported formats are JPG and PNG, max 30MB. If rejected, report the specific file and reason.
