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

This route delegates to the **`campaign-operator` agent**, which uses the official `meta ads` CLI for vanilla CRUD and falls back to raw Graph API only for advanced patterns (lookalikes, custom audiences, ASC+, Post ID relaunching, EMQ — see `agents/campaign-operator.md` for the full fallback list).

Full CLI reference: `skills/meta-ads/rules/ads-cli.md`.

### A.1: Validate Meta CLI + Credentials

Configuration sources:
- `.env.gtm` -- `ACCESS_TOKEN`, `AD_ACCOUNT_ID`, `BUSINESS_ID` (gitignored, secret)
- `.gtm/config.json` -- `meta.pixel_id`, `meta.page_id`, `meta.instagram_actor_id`, `meta.cli_version` (non-secret IDs)

Pre-flight:

```bash
# 1. CLI installed
command -v meta >/dev/null 2>&1 || { echo "meta CLI not installed. Run /gtm-setup."; exit 1; }

# 2. Token valid + scopes sufficient
meta auth status
[ $? -eq 3 ] && { echo "ACCESS_TOKEN invalid/expired. Refresh in Business Manager."; exit 3; }

# 3. Ad account active
meta ads adaccount get "$AD_ACCOUNT_ID" --output json | jq -e '.account_status == 1' >/dev/null \
  || { echo "Ad account is not ACTIVE."; exit 1; }
```

If any check fails, **stop**. Surface the specific failure and instructions. Never attempt deploy with broken auth — the CLI returns exit code 3, but the agent should preempt that with a clear human-readable message.

### A.2: Load Campaign Plan and Creatives

1. If `$ARGUMENTS` contains a campaign name, load that campaign.
2. Otherwise, list available campaigns in `.gtm/creatives/` and ask the user to choose.
3. Load the media plan from `.gtm/plans/`.
4. Load approved creatives from the manifest (filter to `"approved": true`).
5. Load copy from `.gtm/creatives/{campaign-name}/copy.md`.

### A.3: Deploy via campaign-operator

Hand off to the `campaign-operator` agent. It executes the 4-call flow:

1. `meta ads campaign create` → `CAMPAIGN_ID`
2. `meta ads adset create "$CAMPAIGN_ID"` → `ADSET_ID`
3. `meta ads creative create` → `CREATIVE_ID` (image upload implicit)
4. `meta ads ad create "$ADSET_ID" --creative-id "$CREATIVE_ID"` → `AD_ID`

For each call, verify exit code:
- `0` → continue
- `3` → stop, surface auth-refresh guidance
- `4` → backoff 30s, retry once, then stop

### A.4: Verify Deployment

```bash
meta ads campaign get "$CAMPAIGN_ID" --output json | jq .
meta ads adset    get "$ADSET_ID"    --output json | jq .
meta ads ad       get "$AD_ID"       --output json | jq .
```

Confirm: status PAUSED, objective matches plan, ad set has `pixel_id` set, creative has 5/5/5 variations.

### A.5: Save Deployment Record

Save to `.gtm/campaigns/{campaign-name}-{YYYY-MM-DD}.json` with all Meta IDs and `deployed_via: "meta-ads-cli"` plus `cli_version` from `.gtm/config.json`.

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
