# Meta Ads API Gotchas -- Hard-Won Lessons

Every item on this list represents a real error encountered during development. Follow these rules to avoid hours of debugging.

## 1. Always asset_feed_spec, Never Single-Copy object_story_spec

**Wrong:**
```json
{
  "creative": {
    "object_story_spec": {
      "page_id": "PAGE_ID",
      "link_data": {
        "message": "Single body text",
        "link": "https://example.com",
        "name": "Single headline"
      }
    }
  }
}
```

**Right:** Use `asset_feed_spec` with multiple bodies/titles/descriptions. Even if you only have one variation, wrap it in the dynamic creative format. This future-proofs the ad and lets Meta optimize placement-level rendering.

## 2. Always is_dynamic_creative: true

Setting `is_dynamic_creative: true` on the ad set is mandatory when using `asset_feed_spec`. Without it, Meta rejects the creative format. This flag tells Meta to mix and match your assets.

```json
// On the ad set
{ "is_dynamic_creative": true }
```

## 3. Always Upload Images via adimages Endpoint for image_hash

Images must be uploaded to the ad account's image library first. You get back an `image_hash` which you then reference in the creative.

```bash
# Upload
curl -F "filename=@image.jpg" \
  "https://graph.facebook.com/v21.0/act_XXXXX/adimages?access_token=TOKEN"

# Use the returned hash
"images": [{"hash": "returned_image_hash"}]
```

Never try to use a URL directly in the image field. The image_hash is how Meta's CDN serves the creative efficiently.

## 4. Never image_url in link_data (Error 1443050)

If you see error code 1443050, you tried to use `image_url` in a `link_data` object. This field existed in older API versions but is no longer supported with dynamic creative.

**Wrong:**
```json
"link_data": { "image_url": "https://example.com/image.jpg" }
```

**Right:**
```json
"images": [{"hash": "abc123def456"}]
```

## 5. Always Include Square (1:1) AND Vertical (9:16)

Meta serves ads across Feed (1:1), Stories (9:16), and Reels (9:16). If you only provide one aspect ratio:
- Missing 9:16: Your ad won't serve in Stories/Reels (50%+ of impressions)
- Missing 1:1: Your ad renders poorly in Feed

Upload at minimum:
- 1080x1080 (1:1 square)
- 1080x1920 (9:16 vertical)

## 6. Always Include instagram_actor_id

Even if you only want to run on Facebook, include the Instagram account ID. Without it:
- Ads fail to create if Instagram placements are selected (even by Advantage+)
- You lose access to Reels and Stories inventory
- Error code 1815946

```json
"object_story_spec": {
  "page_id": "FACEBOOK_PAGE_ID",
  "instagram_actor_id": "INSTAGRAM_ACCOUNT_ID"
}
```

Find your Instagram account ID: Business Manager > Business Settings > Instagram Accounts.

## 7. System User Tokens from Live-Mode Apps Only (Error 1885183)

If you see error 1885183 ("This app is in development mode"), your System User token was generated from an app that hasn't gone live.

**Fix:**
1. Go to developers.facebook.com > Your App
2. Toggle from "Development" to "Live" mode
3. You only need a Privacy Policy URL to go live for business-type apps
4. Regenerate the System User token after going live

Development-mode tokens can only access data from app administrators. Live-mode tokens can access all ad accounts the System User has permission for.

## 8. Business-Type Apps Go Live with Just Privacy Policy URL

For apps that only manage ads (no user-facing login), you don't need App Review:
1. Set app type to "Business" during creation
2. Add a Privacy Policy URL (can be a simple page on your site)
3. Toggle to Live mode
4. No special permissions review needed for `ads_management` scope

## 9. Verify Pixel in Events Manager, Not API List

The API endpoint `GET /act_XXXXX/adspixels` may return pixels from shared business accounts, partner accounts, or historical pixels. This causes confusion.

**Always verify your pixel by:**
1. Going to https://business.facebook.com/events_manager2
2. Selecting the correct ad account in the top-left dropdown
3. Confirming the Pixel ID matches your environment variable
4. Checking that test events appear when you fire them

## 10. VITE_ Vars Need Redeploy After Change

`VITE_` prefixed environment variables are injected at build time by Vite, not at runtime. If you change `VITE_META_PIXEL_ID`:
- On Vercel: trigger a new deployment
- On Netlify: clear cache and redeploy
- Locally: restart the dev server

**Symptoms of stale VITE_ vars:**
- Pixel events going to the old pixel
- `import.meta.env.VITE_META_PIXEL_ID` returning the old value
- "No events received" in Events Manager for the new pixel

## 11. Composio MCP Too Limited for Writes -- Use Direct Graph API

The Composio MCP server for Meta Ads provides read-only access to campaign data. It cannot:
- Create campaigns, ad sets, or ads
- Upload images
- Modify budgets or targeting
- Create custom audiences

For any write operation, use the Graph API directly via `fetch()` or `curl`. Composio is useful for reading campaign performance data only.

## 12. is_adset_budget_sharing_enabled Required When No Campaign Budget

When using ABO (ad set-level budgets) with no campaign budget, some API versions require explicitly setting:

```json
// On the campaign
{
  "is_adset_budget_sharing_enabled": false
}
```

Or simply omit all budget fields from the campaign. The error manifests as a vague "invalid parameter" if the campaign has conflicting budget signals.

## Quick Diagnostic Checklist

When an ad fails to create, check in this order:

1. Is `is_dynamic_creative: true` set on the ad set?
2. Are images uploaded via `adimages` endpoint (not URL)?
3. Is `instagram_actor_id` present?
4. Is the token from a live-mode app?
5. Is the pixel ID correct (verified in Events Manager)?
6. Are budget fields consistent (CBO on campaign OR ABO on ad sets, not both)?
7. Does the `promoted_object` match the campaign objective?
8. Are all required `asset_feed_spec` fields present (bodies, titles, descriptions, images, link_urls, call_to_action_types)?

## Rate Limits

- Standard: 200 calls per hour per ad account for most endpoints
- Batch API: up to 50 requests per batch call
- Image uploads: separate rate limit, generally more generous
- If rate limited: wait 60 seconds, then retry with exponential backoff
- Use `x-business-use-case-usage` response header to monitor remaining capacity
