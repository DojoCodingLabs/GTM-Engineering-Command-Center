---
name: gtm-deploy
description: "Deploy campaign assets to Meta Ads, Google Ads, email provider, or codebase"
argument-hint: "campaign-name or channel (meta/google/email/code)"
---

# Campaign Deployment Command

You are the campaign-operator agent. You will deploy approved assets to the appropriate channel -- Meta Ads via Graph API, Google Ads API, email provider API, or git commit for codebase assets (landing pages, SEO content). All deployments default to PAUSED for human review before activation.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Parse `$ARGUMENTS` for campaign name or channel specification.
3. Detect which assets exist and determine the appropriate deployment channel.

## Phase 0.5: Channel Routing

Determine the deployment channel by reading available assets:

### Auto-Detection Logic

1. Read `.gtm/creatives/` for ad creative manifests (images + copy) -> **Meta Ads**
2. Read `.gtm/emails/` for email sequence configs -> **Email Provider**
3. Read `.gtm/seo/content/` for SEO content files -> **Codebase (git commit)**
4. Read `.gtm/outreach/` for outreach sequences -> **Save for manual use**
5. Check for landing page components ready to write -> **Codebase (git commit)**

If `$ARGUMENTS` specifies a channel explicitly:
- `meta` -> Meta Ads deployment only
- `google` -> Google Ads deployment only
- `email` -> Email provider deployment only
- `code` -> Codebase deployment (git commit)
- `all` -> Deploy all available assets to their respective channels

If only Meta assets exist, **default to Meta Ads** (backward compatible).

If multiple asset types exist:
```
Multiple asset types found. Deploy which channels?

1. Meta Ads -- {N} creatives ready
2. Email -- {sequence_type} sequence ({N} templates)
3. Codebase -- {N} files (landing page + SEO content)
4. All channels

Select (1-4):
```

## Route A: Meta Ads Deployment

### A.1: Validate Meta API Credentials

- `meta.access_token` -- required
- `meta.ad_account_id` -- required (must start with `act_`)
- `meta.pixel_id` -- required for conversion campaigns
- `meta.page_id` -- required for ad creation
- `meta.api_version` -- use from config or default to `v21.0`

Test the access token validity:
- GET `https://graph.facebook.com/{api_version}/me?access_token={token}`
- If it fails with error code 190 (expired token), tell the user: "Meta access token is expired. Generate a new one and update `.gtm/config.json`." STOP.

Verify ad account access:
- GET `https://graph.facebook.com/{api_version}/{ad_account_id}?fields=name,account_status,currency,timezone_name&access_token={token}`
- If `account_status` is not 1 (ACTIVE), warn the user.

### A.2: Load Campaign Plan and Creatives

1. If `$ARGUMENTS` contains a campaign name, load that campaign.
2. Otherwise, list available campaigns in `.gtm/creatives/` and ask the user to choose.
3. Load the media plan from `.gtm/plans/`.
4. Load approved creatives from the manifest (filter to `"approved": true`).
5. Load copy from `.gtm/creatives/{campaign-name}/copy.md`.

### A.3: Create Campaign

POST to create the campaign:
```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/campaigns

Parameters:
  name: {campaign_name from plan}
  objective: {mapped Meta objective from plan}
  status: PAUSED
  special_ad_categories: [] (or appropriate category)
  access_token: {token}
```

If using Campaign Budget Optimization (CBO):
```
  daily_budget: {total_daily_budget_in_cents}
  bid_strategy: LOWEST_COST_WITHOUT_CAP
```

Store the returned `campaign_id`.

### A.4: Create Ad Sets

For each ad set in the plan:
```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/adsets

Parameters:
  name: {ad_set_name}
  campaign_id: {campaign_id}
  status: PAUSED
  targeting: {from plan}
  optimization_goal: {from plan}
  billing_event: IMPRESSIONS
  promoted_object: {pixel_id, custom_event_type}
  access_token: {token}
```

Search for interest targeting IDs if needed:
```
GET https://graph.facebook.com/{api_version}/search?type=adinterest&q={name}&access_token={token}
```

### A.5: Upload Ad Images

For each approved image:
```
POST https://graph.facebook.com/{api_version}/{ad_account_id}/adimages
```

Store image hashes for creative creation.

### A.6: Create Ad Creatives

Create dynamic creatives using `asset_feed_spec` with uploaded images and copy variations.

### A.7: Create Ads

Create ads linking ad sets to creatives, all set to PAUSED.

### A.8: Save Deployment Record

Save to `.gtm/campaigns/{campaign-name}-{YYYY-MM-DD}.json` with all Meta IDs.

## Route B: Google Ads Deployment

### B.1: Validate Google Ads Credentials

- `google_ads.customer_id` -- required
- `google_ads.developer_token` -- required

### B.2: Create Campaign Structure

Use Google Ads API to create:
- Campaign with budget and bidding strategy
- Ad groups with keyword targets
- Ads with approved copy and landing URLs
- All set to PAUSED

### B.3: Save Deployment Record

Save to `.gtm/campaigns/google-{campaign-name}-{YYYY-MM-DD}.json`.

## Route C: Email Provider Deployment

### C.1: Validate Email Credentials

- `email.provider` -- detected provider
- `email.api_key` -- required
- `email.from_address` -- required

### C.2: Deploy Templates

Based on the detected provider:

**Resend**: Save templates as code (Resend does not support native sequences):
- Generate Supabase Edge Function or cron job for scheduling
- Save implementation code for review
- Note: "Resend requires custom scheduling logic. Templates saved as code."

**SendGrid**: Use SendGrid Automation API:
- Create automation with email sequence
- Set trigger event
- Save in PAUSED/draft state

**Loops**: Use Loops API:
- Create drip campaign
- Upload templates
- Set triggers

**Generic/Other**: Save templates as HTML files with deployment instructions.

### C.3: Save Deployment Record

Save to `.gtm/campaigns/email-{sequence-type}-{YYYY-MM-DD}.json`.

## Route D: Codebase Deployment (Git Commit)

### D.1: Identify Files to Write

Collect all codebase assets:
- Landing page components from `/gtm-landing`
- SEO content from `.gtm/seo/content/`
- Schema markup files
- Sitemap updates
- Email template code (if React Email)

### D.2: Preview Changes

List all files that will be created or modified:
```
Codebase Changes:

New files:
  src/pages/landing/campaign-{name}.tsx
  src/emails/sequences/welcome/email-1.tsx
  public/sitemap.xml (updated)

Modified files:
  src/routes.ts (new route added)

Total: {N} new files, {M} modified files
```

Ask: **"Write these files to the codebase? (yes/preview/no)"**

### D.3: Write Files

If approved:
- Write all new files to the codebase
- Modify existing files as needed
- Do NOT commit -- leave changes staged for the user to review

Tell the user:
```
Files written to codebase. Changes are NOT committed.

Review the changes:
  git diff --stat
  npm run dev  (to preview)

When ready, commit with:
  git add {files}
  git commit -m "feat: add {campaign} landing page and SEO content"
```

### D.4: Save Deployment Record

Save to `.gtm/campaigns/code-{campaign-name}-{YYYY-MM-DD}.json`.

## Phase 1: Deployment Summary (All Routes)

Present the unified deployment summary:

```
Deployment Complete

| Channel | Assets | Status | Details |
|---------|--------|--------|---------|
| Meta Ads | {N} creatives | PAUSED | Campaign ID: {id} |
| Email | {N} templates | Draft | Provider: {name} |
| Codebase | {N} files | Written | Not committed |
| Google Ads | {N} ads | PAUSED | Campaign ID: {id} |

Meta Ads Manager: https://business.facebook.com/adsmanager/manage/campaigns?act={id}

Deployment records: .gtm/campaigns/
```

Ask the user for each channel:
- **"Review and confirm. Activate? (activate {channel} / keep-paused / abort {channel})"**

If "activate" for Meta:
- PATCH each campaign/ad set/ad status to ACTIVE
- Confirm: "Campaign is now ACTIVE. Run `/gtm-metrics` tomorrow to check early performance."

If "activate" for email:
- Enable the sequence/automation in the provider
- Confirm: "Email sequence is now ACTIVE."

## Error Handling

- **Token expired**: Detect error code 190 and prompt for a new token immediately.
- **Rate limiting**: If the API returns error code 17 or 4, wait 60 seconds and retry. After 3 retries, STOP.
- **Partial deployment failure**: Report exactly what was created and what failed. Save partial deployment record. Do NOT attempt to rollback successful creations.
- **Budget too low**: If Meta rejects the budget, report the minimum required.
- **Interest targeting not found**: Skip and warn.
- **Image format rejected**: Supported formats are JPG and PNG, max 30MB.
- **Email provider error**: Save templates locally and provide manual deployment instructions.
- **No approved assets**: If no assets are marked as approved, tell the user to run `/gtm-create` first.
- **Channel not configured**: If a channel's credentials are missing, skip it and suggest `/gtm-setup`.
