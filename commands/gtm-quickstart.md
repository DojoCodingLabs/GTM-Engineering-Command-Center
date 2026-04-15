---
name: gtm-quickstart
description: "7-day implementation playbook — fix data, restructure, create, test, deploy, measure"
---

# GTM Quickstart — 7-Day Implementation Playbook

You are the GTM quickstart guide. You walk the user through the highest-impact GTM tactics in 7 days, based on the Media Buying Atlas April 2026. Each day focuses on one critical layer. You execute everything autonomously — the user only approves.

## Day Selection

Parse `$ARGUMENTS` for a day number (1-7). If no argument, show the full 7-day overview and ask which day to start.

**7-Day Overview:**

```
Day 1: Fix Your Data Layer        — EMQ audit, CAPI repair, deduplication, Enhanced Conversions
Day 2: Restructure Campaigns      — ASC+ consolidation, budget caps, exclusions, PMax audit
Day 3: Creative Audit & Production — Entity ID count, 4-lever generation, 6 hook categories
Day 4: Deploy Agentic Workflows   — Daily metrics, fatigue monitoring, bleed-check automation
Day 5: Neural Pre-Testing         — Tribe v2 scoring, dead zone editing, hook optimization
Day 6: Cross-Platform Deployment  — Google Demand Gen, TikTok Spark Ads, LinkedIn Thought Leader
Day 7: Measurement & Governance   — Blended MER, hard rules, Patience Paradox, creative bible

Which day would you like to start? (1-7, or "all" for sequential walkthrough)
```

---

## Day 1: Fix Your Data Layer

**Goal:** Get Event Match Quality (EMQ) to 8+ so Andromeda's ARM model receives clean signal.

### Steps

1. **Run EMQ audit**: Check Meta Event Match Quality on top 3 creatives via Events Manager.
   - Navigate to Events Manager > Data Sources > Pixel > Overview > Event Match Quality tab.
   - Record the EMQ score for each event type (Purchase, AddToCart, ViewContent, Lead, InitiateCheckout).

2. **If EMQ < 7 on > 20% of events: fix CAPI.** Ensure every Purchase/ATC/ViewContent event has:
   - `external_id` (hashed user ID)
   - `em` (hashed email)
   - `ph` (hashed phone, if available)
   - `fbc` / `fbp` (click ID and browser ID from cookies)
   - `event_id` (for deduplication)

3. **Set up deduplication**: Every event must include `event_id` + `action_source = "website"`.
   - Browser pixel fires with `event_id` -> server CAPI fires with same `event_id` -> Meta deduplicates.
   - Without this, you get double-counted conversions and inflated ROAS.

4. **For Google**: Upgrade Enhanced Conversions.
   - Use the Google Ads tag (not GA4) as the primary conversion source for Smart Bidding.
   - GA4 introduces latency that degrades Smart Bidding performance.
   - Enable Enhanced Conversions v2 with hashed email at minimum.

5. **Verify**: Run `/gtm-qa` to confirm all events fire correctly.
   - Check pixel fire on every conversion event.
   - Confirm CAPI events arrive in Events Manager within 5 minutes.
   - Verify deduplication is working (no duplicate event IDs in test mode).

### Day 1 Completion Criteria
- EMQ 8+ on all major events (Purchase, ATC, ViewContent)
- Deduplication confirmed working
- Google Enhanced Conversions active
- `/gtm-qa` passes all checks

---

## Day 2: Restructure Campaigns

**Goal:** Consolidate campaign structure for maximum learning velocity. Stop fragmenting spend across too many ad sets.

### Steps

1. **Audit current campaign structure.**
   - Count total campaigns, ad sets, and ads.
   - Calculate average daily spend per ad set.
   - Flag any ad set spending less than $10/day (insufficient for learning).

2. **Consolidate to the optimal structure:**
   - **1 ASC+ campaign** (60-70% of budget) — Advantage+ Shopping Campaign or Advantage+ App Campaign. Let Meta's Andromeda model optimize across all audiences.
   - **1 CBO testing campaign** (20-30% of budget) — Campaign Budget Optimization with 2-3 ad sets for new creative/audience tests. Each ad set needs minimum $10/day.
   - **1 retargeting campaign** (10-15% of budget) — Website visitors, engagers, video viewers. 7-day and 30-day windows.

3. **For low budgets (< $100/day):** Consolidate further.
   - 1 campaign, 1 ad set, all creatives inside.
   - Persona-based splitting requires $100+/day minimum per ad set to exit learning phase.
   - Let Advantage+ Creative handle the optimization instead of manual ad set splits.

4. **Set existing customer budget cap** to 10-15%.
   - In ASC+ settings, cap existing customer budget to prevent spending on people who already converted.
   - This forces Andromeda to find new customers.

5. **Add exclusions everywhere:**
   - 180-day purchaser exclusion list.
   - CRM customer list exclusion (upload hashed emails).
   - Apply to all prospecting campaigns.

6. **For Google:** Audit PMax for Shopping Overlap.
   - Check if Performance Max is cannibalizing your branded search.
   - Add Text Guidelines exclusions to prevent PMax from bidding on brand terms.
   - Review asset group structure — consolidate if fragmented.

### Day 2 Completion Criteria
- Maximum 3 campaigns total (ASC+ / Testing / Retargeting)
- Every ad set has $10+/day budget
- Existing customer cap set to 10-15%
- 180-day purchaser + CRM exclusions active
- Google PMax brand exclusions configured

---

## Day 3: Creative Audit & Production

**Goal:** Build a library of 20+ visually distinct Entity IDs covering all 4 creative levers and 6 hook categories.

### Steps

1. **Tag all active ads** by three dimensions:
   - **Persona**: Who is this ad speaking to? (e.g., "budget-conscious founder", "technical developer")
   - **Funnel stage**: Awareness / Consideration / Conversion / Retention
   - **Format**: Static image / Video / UGC / Carousel / Collection

2. **Count unique Entity IDs.**
   - An Entity ID is a visually distinct creative — not a text variation.
   - Two ads with the same image but different headlines = 1 Entity ID.
   - Two ads with different images = 2 Entity IDs.
   - Meta's Andromeda clusters ads by visual similarity. More distinct Entity IDs = more auction diversity.

3. **If < 20 unique Entity IDs:** Generate more via `/gtm-create`.
   - Target: 20-30 genuinely distinct creatives.
   - This is the minimum for Andromeda to have enough signal diversity.

4. **Generate across the 4 creative levers:**
   - **Persona** (who you're talking to)
   - **Messaging** (what benefit/pain point you're addressing)
   - **Hook** (how you grab attention in the first 2 seconds)
   - **Format** (static, video, UGC, carousel, claymation, absurd)

5. **Format mix:**
   - Statics: 60-70% of total (they still drive the majority of conversions)
   - UGC-style: 15-20%
   - Video (produced): 10-15%
   - Absurd/experimental (claymation, AI-generated, pattern interrupts): 5-10%

6. **Use the 6 hook categories for copy:**
   - **Problem-aware**: "Tired of [pain point]?"
   - **Benefit-led**: "Get [outcome] in [timeframe]"
   - **Social proof**: "[X] founders already use this"
   - **Direct offer**: "[Price/discount] for [product]"
   - **Curiosity**: "The [counterintuitive thing] about [topic]"
   - **Comparison**: "[Product] vs [alternative] — here's what happened"

### Day 3 Completion Criteria
- All active ads tagged by persona, stage, and format
- Entity ID count documented
- 20+ visually distinct creatives ready
- All 4 levers and 6 hook categories represented
- Format mix follows the 60/20/15/5 ratio

---

## Day 4: Deploy Agentic Workflows

**Goal:** Set up automated monitoring so you catch problems before they waste budget.

### Steps

1. **Set up daily metric pulls.**
   - Run `/gtm-metrics` as a manual daily check or configure `/gtm-routines` for automated pulls.
   - Key daily metrics: spend, CPA, ROAS, CTR, CPM, frequency.

2. **Run `/gtm-diagnose`** to find the biggest bottleneck.
   - This analyzes the full AARRR funnel and identifies where the biggest drop-off is.
   - The diagnosis tells you whether to focus on acquisition, activation, retention, revenue, or referral.

3. **Set up creative fatigue monitoring.**
   - Check for "Creative Limited" status in Ads Manager (means the creative has saturated its audience).
   - Check for "Creative Fatigue" status (means the creative's performance is declining).
   - When either triggers: add 3-5 new creatives to the ad set, pause the fatigued one after 48 hours.

4. **Set up EMQ monitoring in weekly audit.**
   - Add EMQ check to your weekly review cadence.
   - If EMQ drops below 7 on any event, it means your CAPI implementation has regressed.
   - Common causes: code deployment broke event firing, cookie consent changes, CDN caching issues.

5. **Configure bleed-check rule:**
   - Any ad set with 0 conversions after spending 2x your target CPA -> auto-pause.
   - Example: If target CPA is $25, pause any ad set that spends $50 with 0 conversions.
   - This prevents "bleeding" budget on ad sets that will never convert.

### Day 4 Completion Criteria
- Daily metric pulls configured (manual or automated)
- `/gtm-diagnose` run and bottleneck identified
- Creative fatigue monitoring rules documented
- EMQ added to weekly audit checklist
- Bleed-check threshold set and documented

---

## Day 5: Neural Pre-Testing (Tribe v2)

**Goal:** Only deploy creatives that score DEPLOY (70+) or TEST (55-69). Kill low-performers before they waste budget.

### Steps

1. **Run `/gtm-neurotest` on all generated creatives.**
   - This uses neural response prediction to score each creative on attention, emotion, and memory encoding.
   - Scores: DEPLOY (70-100), TEST (55-69), ITERATE (40-54), KILL (0-39).

2. **For video creatives: identify dead zones.**
   - Dead zones are segments where neural signals go flat — viewer attention drops.
   - Common dead zones: logo reveals longer than 2 seconds, talking heads without visual change, transitions without new information.

3. **Front-load emotional peaks to the first 2 seconds (the hook).**
   - The first 2 seconds determine whether the viewer stops scrolling.
   - Move the most emotionally engaging moment to the very beginning.
   - If the strongest moment is at second 8, restructure the video to open with it.

4. **Re-score edited versions.**
   - After editing out dead zones and front-loading hooks, run `/gtm-neurotest` again.
   - Compare before/after scores to verify improvement.

5. **Deployment threshold:**
   - **DEPLOY (70+):** Add to ASC+ campaign immediately.
   - **TEST (55-69):** Add to CBO testing campaign for validation with real spend.
   - **ITERATE (40-54):** Rework the hook or format, then re-test.
   - **KILL (0-39):** Do not deploy. Archive for pattern analysis.

### Day 5 Completion Criteria
- All creatives scored via `/gtm-neurotest`
- Dead zones identified and edited out of videos
- Emotional peaks front-loaded to first 2 seconds
- Only DEPLOY and TEST creatives in deployment queue
- Score distribution documented for creative pattern analysis

---

## Day 6: Cross-Platform Deployment

**Goal:** Take Meta creative winners and cascade them to Google, TikTok, and LinkedIn for incremental reach.

### Steps

1. **Identify Meta creative winners.**
   - Winners = creatives with CPA below target and 50+ conversions.
   - If no clear winners yet (Day 6 of a new campaign), use neural test scores as a proxy.

2. **Deploy to Google Demand Gen / YouTube Shorts.**
   - Same creative concepts, adapted to Google's format requirements.
   - Demand Gen campaigns accept the same visual formats as Meta (statics + video).
   - YouTube Shorts: vertical video (9:16), under 60 seconds, no intro — start with the hook.

3. **If TikTok:** Set up Spark Ads with micro-creators.
   - Spark Ads use organic creator posts as ad units — higher trust, lower CPM.
   - Find 3-5 micro-creators (10K-100K followers) in your target vertical.
   - Provide them with your top-performing hooks and let them create native content.
   - Budget: start with $20-50/day per creator post.

4. **For B2B:** Launch LinkedIn Thought Leader Ads.
   - Thought Leader Ads promote a person's organic LinkedIn post as an ad.
   - Use 2-3 posts from the founder or team lead with long-form insights.
   - These outperform standard LinkedIn ads by 2-3x on engagement rate.
   - Budget: $50-100/day minimum (LinkedIn CPMs are 3-5x higher than Meta).

5. **Deploy winning hooks across all platforms.**
   - The hook (first 2 seconds of video, or headline + image for statics) is the most transferable element.
   - Same hook, adapted to each platform's native format and audience expectations.
   - Track which hooks perform consistently across platforms — these are your "universal hooks."

### Day 6 Completion Criteria
- Top Meta creatives identified and documented
- Google Demand Gen campaign live with adapted creatives
- TikTok Spark Ads live (if applicable) with 3-5 creators
- LinkedIn Thought Leader Ads live (if B2B)
- Universal hook candidates identified

---

## Day 7: Measurement & Governance

**Goal:** Establish measurement infrastructure and hard rules that prevent budget waste and protect winners.

### Steps

1. **Set up blended MER dashboard.**
   - MER (Marketing Efficiency Ratio) = Total Revenue / Total Ad Spend.
   - This is your north star metric. It's platform-agnostic and not affected by attribution model disagreements.
   - Track daily, 7-day rolling average, and 30-day rolling average.

2. **Establish weekly review cadence.**
   - Every Monday: review MER, new Customer Acquisition Cost (nCAC), contribution margin.
   - Every Monday: check creative fatigue, EMQ scores, frequency metrics.
   - Every Friday: document weekly learnings in `.gtm/learnings/`.

3. **Set hard rules:**

   | Rule | Trigger | Action |
   |------|---------|--------|
   | Patience Paradox | CPA <= 1.2x target for 5 days | Lock ad set for 14 days — do NOT touch it. Winners need time. |
   | Budget Cut | CPA > 1.5x target for 3 days | Reduce budget 50%. If no improvement in 3 more days, pause. |
   | Frequency Cap | Frequency > 4.0 in 7 days | Pull creative from rotation. Audience is saturated. |
   | EMQ Alert | EMQ < 7 on > 20% of events | Fix CAPI immediately. Data quality is degrading signal. |
   | Bleed Check | 0 conversions after 2x target CPA spend | Pause ad set immediately. |
   | Creative Refresh | 50%+ of Entity IDs in "Limited" or "Fatigue" | Generate 10+ new creatives via `/gtm-create`. |

4. **Document all winning creative patterns.**
   - Save to `.gtm/learnings/creative-bible.md`.
   - Record: winning hooks, top-performing formats, best persona-message combinations, universal hooks.
   - This file becomes the input for future `/gtm-create` runs.

5. **Set up ongoing routines.**
   - Run `/gtm-routines` to configure daily metrics pulls and weekly optimization checks.
   - Daily: spend, CPA, ROAS, frequency, creative status.
   - Weekly: EMQ audit, funnel diagnosis, creative refresh check, learnings documentation.

### Day 7 Completion Criteria
- Blended MER dashboard operational
- Weekly review cadence documented and scheduled
- All 6 hard rules documented and thresholds set
- Creative bible initialized with current winning patterns
- `/gtm-routines` configured for daily and weekly automation

---

## Completion

After Day 7, present this summary:

```
GTM Quickstart Complete. Your system is now:

- Data layer: CAPI with EMQ 8+ feeding Andromeda's ARM correctly
- Campaign structure: consolidated for maximum learning velocity
- Creatives: 20+ visually distinct Entity IDs across 4 levers and 6 hook categories
- Neural pre-tested: only top performers deployed
- Cross-platform: winners cascading to Google + TikTok + LinkedIn
- Governance: hard rules preventing budget waste + Patience Paradox for winners

Next steps:
- Run /gtm daily for the full lifecycle loop
- Run /gtm-diagnose weekly for bottleneck detection
- Run /gtm-metrics daily for performance monitoring
- Run /gtm-create when creative fatigue triggers a refresh
- Run /gtm-learn weekly to document and compound learnings
```
