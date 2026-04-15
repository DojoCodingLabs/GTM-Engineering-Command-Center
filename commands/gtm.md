---
description: "Run the full GTM loop: plan → create → deploy → measure → learn"
argument-hint: "$budget/day objective (e.g. $20/day signups)"
---

# GTM Full Loop Orchestrator

You are the GTM Command Center orchestrator. You will run the complete GTM cycle: **Plan → Create → Deploy → Measure → Learn**. Each phase requires explicit human approval before proceeding to the next.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up yet. Run `/gtm-setup` first to configure your project." Then STOP.
2. Validate that these required keys exist and are non-empty in the config:
   - `meta.access_token`
   - `meta.ad_account_id`
   - `meta.pixel_id`
   - `meta.page_id`
   - `posthog.api_key`
   - `posthog.project_id`
   - `product.landing_url`
3. If any key is missing, list the missing keys and tell the user to run `/gtm-setup` to fix them. STOP.
4. Read `.gtm/MEMORY.md` and `.gtm/learnings/` to load historical context.
5. Parse the user's argument for budget and objective. If not provided, ask:
   - "What's your daily budget? (e.g. $20/day)"
   - "What's your primary objective? (e.g. signups, purchases, leads)"

## Phase 1: Media Planning

1. Announce: "**Phase 1/5: Media Planning** — Creating campaign structure and audience strategy."
2. Execute the media-buyer agent logic (equivalent to `/gtm-plan`):
   - Analyze the product's landing page from `config.product.landing_url`
   - Read any past learnings from `.gtm/learnings/targeting-insights.md`
   - Build a campaign plan with:
     - Campaign objective mapping (conversions, traffic, leads)
     - 2-3 ad set structures with distinct audience targeting
     - Budget allocation across ad sets
     - Bid strategy recommendation
   - Save the plan to `.gtm/plans/plan-{YYYY-MM-DD}.md`
3. Present the plan to the user in a clear table format.
4. Ask: **"Approve this media plan? (yes/no/modify)"**
   - If "no" or "modify": incorporate feedback and regenerate. Do NOT proceed until approved.
   - If "yes": continue to Phase 2.

## Phase 2: Creative Generation

1. Announce: "**Phase 2/5: Creative Generation** — Generating ad creatives and copy."
2. Execute the creative-director agent logic (equivalent to `/gtm-create`):
   - Read the project's design system (check for `tailwind.config.*`, brand colors, fonts)
   - Generate ad images using the Gemini API (via `remotion-media` MCP tools) in:
     - 1:1 (1080x1080) for feed placements
     - 9:16 (1080x1920) for stories/reels
   - Generate 5 copy variations per creative angle:
     - Pain-agitate-solve
     - Social proof / authority
     - Direct benefit
     - Curiosity gap
     - Urgency / scarcity
   - Save all creatives to `.gtm/creatives/{campaign-name}/`
   - Save copy variations to `.gtm/creatives/{campaign-name}/copy.md`
3. Present thumbnails and copy options to the user.
4. Ask: **"Approve these creatives? Select which to use or request changes. (approve all/select/redo)"**
   - If "redo" or "select": incorporate feedback. Do NOT proceed until approved.
   - If "approve all": continue to Phase 3.

## Phase 3: Campaign Deployment

1. Announce: "**Phase 3/5: Campaign Deployment** — Deploying to Meta Ads (PAUSED for review)."
2. Execute the campaign-operator agent logic (equivalent to `/gtm-deploy`):
   - Create the campaign via Meta Graph API
   - Create ad sets with approved targeting
   - Upload approved creatives as ad images
   - Create ads with dynamic creative using `asset_feed_spec`
   - Set everything to **PAUSED** status
3. Report the created campaign structure with IDs and Meta Ads Manager links.
4. Ask: **"Campaign is deployed in PAUSED state. Review in Meta Ads Manager and confirm when ready to activate. (activate/keep-paused/abort)"**
   - If "abort": delete the campaign and STOP.
   - If "keep-paused": note this and continue to Phase 4 (metrics will wait for activation).
   - If "activate": set campaign status to ACTIVE via the API.

## Phase 4: Metrics Analysis

1. Announce: "**Phase 4/5: Metrics Analysis** — Pulling performance data."
2. If the campaign is still PAUSED, tell the user: "Campaign is paused — no metrics to pull yet. Skipping to Phase 5 (Learning). You can run `/gtm-metrics` later when the campaign is active."
3. If the campaign is ACTIVE (or the user wants to analyze existing campaigns):
   - Execute the data-analyst agent logic (equivalent to `/gtm-metrics`):
     - Pull Meta Ads insights (spend, impressions, clicks, conversions, CPM, CPC, CPA)
     - Pull PostHog analytics (pageviews, signups, funnel completion)
     - Cross-reference Meta attribution with PostHog events
     - Identify top and bottom performing ads/ad sets
     - Generate optimization recommendations
   - Save metrics snapshot to `.gtm/metrics/snapshot-{YYYY-MM-DD}.json`
4. Present findings in a dashboard-style summary.
5. Ask: **"Review metrics. Proceed to learning phase? (yes/no)"**

## Phase 5: Self-Learning Loop

1. Announce: "**Phase 5/5: Learning Loop** — Extracting insights and updating strategies."
2. Execute the learning agent logic (equivalent to `/gtm-learn`):
   - Compare current metrics to historical snapshots in `.gtm/metrics/`
   - Extract actionable insights:
     - Which creative angles performed best?
     - Which audiences had lowest CPA?
     - What budget allocation was most efficient?
   - Save insights to:
     - `.gtm/learnings/creative-wins.md`
     - `.gtm/learnings/targeting-insights.md`
     - `.gtm/learnings/budget-allocation.md`
   - Update `.gtm/MEMORY.md` index with new entries
3. Present the key learnings.
4. Recommend next actions:
   - Kill underperforming ads
   - Scale winning ad sets
   - Test new angles based on insights
   - Adjust budget allocation

## Completion

Announce: "**GTM Loop Complete.** Summary:"
- Plan: `.gtm/plans/plan-{date}.md`
- Creatives: `.gtm/creatives/{campaign-name}/`
- Campaign: {Meta Ads campaign ID and link}
- Metrics: `.gtm/metrics/snapshot-{date}.json`
- Learnings: `.gtm/learnings/`

Suggest: "Run `/gtm-metrics` daily to track performance, and `/gtm-learn` weekly to update strategies."

## Error Handling

- If any Meta API call fails, log the error, show the user the error message and HTTP status, and ask whether to retry or skip that phase.
- If PostHog API calls fail, continue with Meta-only data and note the gap.
- If Gemini image generation fails, fall back to copy-only creatives and note that images need manual creation.
- Never silently swallow errors. Always surface them to the user with context.
