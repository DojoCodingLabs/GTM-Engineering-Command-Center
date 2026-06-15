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

Google is a **hybrid channel**. There is no first-party CLI that mutates. So this route splits cleanly in two:

- **READ / MEASURE / VERIFY** → the `google-ads-open-cli` (a Node binary, **READ-ONLY**). Full reference: `skills/google-ads/rules/gads-cli.md`.
- **WRITE / DEPLOY** → the Google Ads REST `:mutate` endpoints via `curl`. The 5-call deploy flow lives in `agents/campaign-operator.md` ("Google Ads Deployment").

This route delegates the writes to the **`campaign-operator` agent** and uses the read CLI for credential smoke-tests and post-deploy verification. State the split out loud at every step — never let the operator assume one binary does both. Distilled from `knowledge/google-ads-atlas-2026.md` (cite as "Atlas Part X").

> **MONEY IS IN MICROS.** 1,000,000 micros = $1. Every budget is `amountMicros`; every stat `cost_micros ÷ 1e6` for dollars. A $50/day budget is `50000000`, not `50` and not `5000`. This is the Google analog of Meta's "cents" gotcha — and worse, because the multiplier is a million.

### B.1: Validate Google CLI + Credentials

Configuration sources:
- `.env.gtm` -- `GOOGLE_ADS_ACCESS_TOKEN`, `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID` (gitignored, secret). These also feed the REST write path (`Authorization: Bearer`, `developer-token` headers).
- `.gtm/config.json` -- `google_ads.customer_id` (10 digits, no dashes), `google_ads.developer_token`, `google_ads.conversion_action_ids.primary`, `google_ads.cli_version` (non-secret).

Pre-flight (read path — the CLI auths and smoke-tests; it never writes):

```bash
# 1. Read CLI installed
command -v google-ads-open-cli >/dev/null 2>&1 || { echo "google-ads-open-cli not installed. Run /gtm-setup."; exit 1; }

# 2. Auth smoke test — `customers` is the cheapest authenticated read.
#    This is a DIFFERENT binary from `meta` — do NOT assume Meta's literal 0/3/4 codes.
#    Classify by stderr regex (see skills/google-ads/rules/gads-cli.md §6).
ERR=$(mktemp)
google-ads-open-cli customers --format compact >/tmp/gads_customers.json 2>"$ERR"
if [ $? -ne 0 ]; then
  if grep -qiE 'auth|token|credential|unauthenticated|permission' "$ERR"; then
    echo "AUTH ERROR: Google Ads credentials invalid/expired. Re-run 'google-ads-open-cli auth login' (or refresh GOOGLE_ADS_ACCESS_TOKEN in CI)."; cat "$ERR" >&2; exit 3
  else
    echo "API ERROR: backoff + retry once, then alert."; cat "$ERR" >&2; exit 4
  fi
fi

# 3. Confirm the target customer is reachable (10 digits, dashes stripped).
CUSTOMER_ID=$(jq -r '.google_ads.customer_id' .gtm/config.json)
google-ads-open-cli customer "$CUSTOMER_ID" --format compact | jq -e '.customer.id' >/dev/null \
  || { echo "Target customer $CUSTOMER_ID not accessible. Check GOOGLE_ADS_LOGIN_CUSTOMER_ID (MCC) and config."; exit 1; }

# 4. HALT IF NO PRIMARY CONVERSION ACTION (Atlas Law 2 / Part 6 — signal beats structure).
#    Deploying Smart Bidding with no primary conversion action teaches the engine nothing
#    and burns budget on the cheapest junk. Verify the configured primary action is ENABLED.
PRIMARY=$(jq -r '.google_ads.conversion_action_ids.primary // empty' .gtm/config.json)
[ -z "$PRIMARY" ] && { echo "HALT: google_ads.conversion_action_ids.primary missing in .gtm/config.json. No primary conversion action = no signal. Configure conversion tracking first (see skills/google-ads/rules/conversion-tracking.md). Atlas Law 2."; exit 1; }
google-ads-open-cli conversion-actions "$CUSTOMER_ID" --format compact \
  | jq -e --arg p "$PRIMARY" 'select((.conversionAction.id|tostring) == $p and .conversionAction.status == "ENABLED")' >/dev/null \
  || { echo "HALT: primary conversion action $PRIMARY not found or not ENABLED. Smart Bidding will fly blind. Atlas Law 2."; exit 1; }
```

If any check fails, **stop**. Surface the specific failure. Never deploy with broken auth or a missing primary conversion action — exit 3 = auth (re-login), exit 4 = API (backoff+retry once), and a missing/disabled primary action is a hard HALT (Atlas Law 2). Mirror Route A's stop-on-broken-auth stance: the read CLI preempts a doomed REST write with a clear human-readable message.

### B.2: Load Campaign Plan and RSA Copy

1. If `$ARGUMENTS` contains a campaign name, load that campaign.
2. Otherwise, list available Google plans in `.gtm/plans/` and ask the user to choose.
3. Load the media plan from `.gtm/plans/` — pull campaign structure, bidding strategy (Atlas Part 5: default `MAXIMIZE_CONVERSIONS` until ~30 conv/mo, then tCPA/tROAS), daily budget (in dollars — you convert to micros at write time), match types, and the keyword list.
4. Load the RSA copy from the **creative-director** output at `.gtm/creatives/{campaign-name}/copy.md` — Responsive Search Ad assets: up to 15 headlines (30 char), 4 descriptions (90 char). Filter to `"approved": true` in the manifest.
5. Resolve the brand term(s) for the brand-exclusion negative (Atlas Law 2 / Part 4: isolate brand — every non-brand campaign gets a brand-term negative so the engine cannot backfill cheap branded demand).

### B.3: Deploy via campaign-operator (REST `:mutate`, all PAUSED)

**Hybrid, stated explicitly:** the writes below are **REST `curl` against `googleads.googleapis.com/.../:mutate`** — the read CLI cannot mutate. After the writes land, the operator **self-verifies with `google-ads-open-cli`** (B.4). Two tools, one flow.

Hand off to the `campaign-operator` agent. It executes the 5-call flow (full payloads in `agents/campaign-operator.md`). **Ordering is load-bearing: budget must exist before the campaign can reference it.**

| # | Resource | Endpoint | Yields | Notes |
|---|---|---|---|---|
| 1 | Budget | `campaignBudgets:mutate` | `BUDGET_RESOURCE` (`customers/{cid}/campaignBudgets/{id}`) | `amountMicros` — **$50/day = `50000000`**. Create FIRST. |
| 2 | Campaign | `campaigns:mutate` | `CAMPAIGN_ID` | `status: PAUSED`; `advertisingChannelType: SEARCH`; bidding strategy from plan; `campaignBudget: $BUDGET_RESOURCE`. |
| 3 | Ad group | `adGroups:mutate` | `ADGROUP_ID` | `status: PAUSED`; `type: SEARCH_STANDARD`; references `$CAMPAIGN_ID`. |
| 4 | Keywords + brand exclusion | `adGroupCriteria:mutate` (positives) + `campaignCriteria:mutate` (brand negative) | criteria IDs | Positive keywords with match types from plan. **Brand-term negative** applied at the campaign level so non-brand cannot eat brand demand (Atlas Law 2). |
| 5 | RSA | `adGroupAds:mutate` | `AD_ID` | `status: PAUSED`; `responsiveSearchAd` with headlines + descriptions from creative-director; `finalUrls` carry UTMs. |

All five calls use the same headers: `Authorization: Bearer $GOOGLE_ADS_ACCESS_TOKEN`, `developer-token: $GOOGLE_ADS_DEVELOPER_TOKEN`, `Content-Type: application/json`. **Everything PAUSED** (Atlas: all writes default PAUSED for human review). The campaign references the primary conversion action validated in B.1 — Smart Bidding without it is blind (Atlas Law 2).

For each `:mutate` call, check the HTTP body for `results[].resourceName` (success) vs `error` (failure). On a `401/UNAUTHENTICATED` → auth, re-mint the access token. On `429/RESOURCE_EXHAUSTED` or `5xx` → backoff 30s, retry once, then stop. Do not roll back partial successes (the budget and campaign may already exist) — record what landed and report.

> Brand exclusion on non-brand and automated campaigns. **WHITEHAT | 9/10** — aggressive brand exclusions and negatives keep automated campaigns from backfilling easy brand demand (Atlas tactic scoring, Part 4). It is pure account hygiene with zero policy exposure.

### B.4: Verify Deployment (read CLI)

Verification is the **read path** — `google-ads-open-cli`, never a re-mutate. Confirm what the REST writes actually produced:

```bash
CID="$CUSTOMER_ID"

# Campaign: PAUSED, channel SEARCH, budget + bidding strategy correct
google-ads-open-cli campaign "$CID" "$CAMPAIGN_ID" --format compact | jq .

# Ad group: PAUSED, references the campaign
google-ads-open-cli ad-groups "$CID" --campaign "$CAMPAIGN_ID" --format compact | jq .

# Keywords: positives present with correct match types
google-ads-open-cli keywords "$CID" --campaign "$CAMPAIGN_ID" --format compact | jq .

# Brand exclusion: confirm the brand-term NEGATIVE exists at campaign level
google-ads-open-cli negative-keywords "$CID" --format compact \
  | jq -e --arg b "$BRAND_TERM" 'select(.campaignCriterion.keyword.text // .sharedCriterion.keyword.text | ascii_downcase | contains($b|ascii_downcase))' \
  || echo "WARN: brand-exclusion negative for '$BRAND_TERM' NOT found — non-brand can backfill brand demand (Atlas Law 2). Re-run B.3 step 4."

# RSA present and PAUSED
google-ads-open-cli ads "$CID" --campaign "$CAMPAIGN_ID" --format compact | jq .
```

Verification checklist:
- [ ] Campaign `status == PAUSED`, `advertisingChannelType == SEARCH`
- [ ] Campaign budget `amountMicros` matches plan (÷1e6 = the dollar figure)
- [ ] Bidding strategy matches plan (Atlas Part 5 — `MAXIMIZE_CONVERSIONS` default)
- [ ] Ad group `status == PAUSED`, references the campaign
- [ ] Keywords present with correct match types
- [ ] **Brand-exclusion negative present** at campaign level (Atlas Law 2)
- [ ] RSA `status == PAUSED`, UTMs present on `finalUrls`
- [ ] Campaign optimizes toward the primary conversion action (B.1)

### B.5: Save Deployment Record

Save to `.gtm/campaigns/google-{campaign-name}-{YYYY-MM-DD}.json`:

```json
{
  "campaign_name": "Campaign Name",
  "channel": "google",
  "created_at": "2026-06-14T12:00:00Z",
  "status": "PAUSED",
  "deployed_via": "google-ads-rest-mutate",
  "read_via": "google-ads-open-cli",
  "cli_version": "<from .gtm/config.json google_ads.cli_version>",
  "customer_id": "1234567890",
  "google_ids": {
    "budget_resource": "customers/1234567890/campaignBudgets/XXXXXXXXXX",
    "campaign_id": "XXXXXXXXXX",
    "ad_groups": [
      {
        "ad_group_id": "XXXXXXXXXX",
        "ad_group_name": "Ad Group Name",
        "rsa_ad_id": "XXXXXXXXXX",
        "keyword_count": 12,
        "match_types": ["PHRASE", "EXACT"]
      }
    ]
  },
  "bidding_strategy": "MAXIMIZE_CONVERSIONS",
  "conversion_action": "customers/1234567890/conversionActions/<primary>",
  "daily_budget_micros": 50000000,
  "brand_exclusion": "BrandTerm",
  "utm_params": {
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "campaign-name"
  },
  "plan_file": ".gtm/plans/campaign-name-2026-06-14.md"
}
```

This record is the data-analyst's source of truth for `/gtm-metrics` and `/gtm-learn`. `read_via` tells downstream routines to query state with `google-ads-open-cli`, not to expect a write CLI.

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

If "activate" for Google (hybrid — REST `:mutate`, the read CLI cannot flip status):
- PATCH campaign → ad group → ad up to `ENABLED` via REST `:mutate` with `updateMask`. Same headers as B.3. Order matters: enable the campaign, then ad group, then ad.

```bash
# Campaign → ENABLED (resourceName from the B.5 record; updateMask=status)
curl -s -X POST "https://googleads.googleapis.com/v17/customers/${CUSTOMER_ID}/campaigns:mutate" \
  -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
  -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"operations":[{"update":{"resourceName":"customers/'"${CUSTOMER_ID}"'/campaigns/'"${CAMPAIGN_ID}"'","status":"ENABLED"},"updateMask":"status"}]}' | jq .

# Repeat for adGroups:mutate (resourceName customers/{cid}/adGroups/{id}) and
# adGroupAds:mutate (resourceName customers/{cid}/adGroupAds/{adGroupId}~{adId}), each updateMask=status.
```

- Then re-read with `google-ads-open-cli campaign "$CUSTOMER_ID" "$CAMPAIGN_ID" --format compact` to confirm `status == ENABLED`.
- Confirm to the user: **"Campaign flipped to ENABLED — but Google must review it first. Ads do NOT serve until review clears (typically 24-48h). `status: ENABLED` is not the same as serving."** Update the B.5 record `status` to `ENABLED` (note: serving is review-gated). Run `/gtm-metrics` after review clears, not tomorrow-guaranteed.

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

### Google Ads (Route B) — channel-specific

- **Budget in dollars, not micros**: The single most expensive Google mistake. `amountMicros` is **micros** — `$50/day = 50000000`, not `50`. If you pass `50` you bid a budget of $0.00005 and nothing serves; if you pass dollars where micros are expected anywhere downstream you misreport by 1,000,000×. **Always `× 1e6` on write, `÷ 1e6` on read.** If the REST call returns a budget validation error (`amountMicros` below the account minimum), the figure is in micros — convert before reporting it.
- **Budget-before-campaign ordering**: `campaigns:mutate` will fail with an invalid/missing `campaignBudget` resource if you create the campaign before the budget. Always run `campaignBudgets:mutate` (call 1) first and capture `BUDGET_RESOURCE` before call 2. If you see a campaign-create error referencing the budget resourceName, you ran them out of order — create the budget, then retry the campaign.
- **Google review-pending state**: `status: ENABLED` ≠ serving. Google reviews new campaigns/ads (typically **24-48h**) before they serve. A campaign can read `ENABLED` and still show zero impressions because review has not cleared. Do not treat an activated-but-non-serving campaign as broken for the first 48h; check `ad_group_ad.policy_summary.approval_status` via GAQL (`google-ads-open-cli query`) before declaring a delivery problem.
- **Auth vs API (read CLI)**: `google-ads-open-cli` is a different binary from `meta` — do NOT key off Meta's literal exit codes. Classify by stderr regex (`/auth|token|credential|unauthenticated|permission/i` → re-run `google-ads-open-cli auth login`; else backoff + retry once). See `skills/google-ads/rules/gads-cli.md` §6.
- **Missing primary conversion action**: HALT before any write (Atlas Law 2). Smart Bidding with no ENABLED primary conversion action teaches the engine nothing and chases the cheapest junk. Configure conversion tracking (`skills/google-ads/rules/conversion-tracking.md`) first.
