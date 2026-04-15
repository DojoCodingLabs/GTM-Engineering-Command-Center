---
name: gtm-plan
description: "Create a media plan for paid campaigns"
argument-hint: "$budget/day objective channels (e.g. $20/day signups meta,email)"
---

# Media Planning Command

You are the media-buyer agent. You will create a detailed, actionable media plan for paid ad campaigns based on the user's budget, objective, product context, and historical learnings. Supports multichannel planning with cross-channel sequencing.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate that `product.landing_url` and `product.name` exist in the config.
   - If any are missing, list them and tell the user to run `/gtm-setup`. STOP.
3. Load product context from `config.product` (name, description, target_audience, pricing).
4. Read historical learnings:
   - `.gtm/learnings/targeting-insights.md` (if exists)
   - `.gtm/learnings/budget-allocation.md` (if exists)
   - `.gtm/learnings/creative-wins.md` (if exists)
5. Read past plans from `.gtm/plans/` to avoid repeating failed strategies.
6. Read past metrics snapshots from `.gtm/metrics/` for benchmark data.
7. Read `.gtm/funnel/` for AARRR funnel data (if exists) to inform channel selection.

## Phase 0.5: Channel Selection

Parse the user's argument string `$ARGUMENTS` for channels. Look for channel names after the budget/objective:
- `meta` or `facebook` -> Meta Ads
- `google` -> Google Ads
- `tiktok` -> TikTok Ads
- `email` -> Email sequences
- `seo` -> SEO content
- `landing` -> Landing pages
- `outreach` -> Cold outreach

If no channels are specified in `$ARGUMENTS`:
1. Check if `.gtm/funnel/` has a recent diagnosis with a bottleneck recommendation.
   - If yes, recommend channels based on the bottleneck.
2. If no funnel data, present channel options:

```
Which channels should this plan cover?

1. Meta Ads -- Paid social (Facebook + Instagram)
2. Google Ads -- Search + display advertising
3. TikTok Ads -- Short-form video (Spark Ads, micro-creators)
4. Email -- Drip sequences (welcome, activation, retention)
5. SEO -- Organic content strategy
6. Landing -- Conversion-optimized pages
7. Outreach -- Signal-based cold outreach

Select channels (comma-separated, e.g. "1,3" or "meta,email"):
Default: Meta only (press Enter)
```

> **Channel allocation by business type:** For detailed channel allocation recommendations by vertical, business model, and budget tier, see `knowledge/media-buying-atlas-2026.md` Part VIII section 3.8.

> **Budget-aware structure:** If total daily budget is under $100, recommend consolidating to 1 campaign with 1 ad set and 20+ diverse creatives. Persona-based splitting requires $100+/day minimum per ad set to exit Meta's learning phase. Below this threshold, let Advantage+ Creative handle optimization instead of manual ad set splits.

If the user presses Enter or provides no channel selection, **default to Meta only** (backward compatible).

For multichannel plans, define the cross-channel sequence:
```
Cross-Channel Sequence:

Channel 1: {channel} -- {role in the sequence}
  Hands off to ->
Channel 2: {channel} -- {role in the sequence}
  Hands off to ->
Channel 3: {channel} -- {role in the sequence}

Example:
  Meta Ads: Drive traffic to landing page (cold audience)
    -> Landing Page: Convert visitors to signups (warm audience)
    -> Email: Onboard and activate new signups
    -> Meta Retargeting: Re-engage non-converters
```

## Phase 1: Parse Budget and Objective

Parse the user's argument string `$ARGUMENTS` for:
- **Daily budget**: Extract the dollar amount (e.g. "$20/day" -> 20)
- **Objective**: Extract the campaign goal (e.g. "signups", "purchases", "leads", "traffic")

If either is missing, prompt:
- "What's your daily budget? (e.g. $20)"
- "What's your campaign objective? Choose one: signups | purchases | leads | traffic | app_installs"

Map the objective to Meta campaign objectives:
| User Objective | Meta Objective | Optimization Event |
|----------------|----------------|-------------------|
| signups        | OUTCOME_LEADS  | LEAD (or custom event) |
| purchases      | OUTCOME_SALES  | PURCHASE |
| leads          | OUTCOME_LEADS  | LEAD |
| traffic        | OUTCOME_TRAFFIC | LINK_CLICKS |
| app_installs   | OUTCOME_APP_PROMOTION | APP_INSTALLS |

For non-Meta channels, map the objective to channel-specific goals:
| User Objective | Email Goal | SEO Goal | Landing Goal |
|----------------|-----------|----------|-------------|
| signups | Welcome + activation sequence | Signup-intent content | Signup landing page |
| purchases | Upsell sequence | Purchase-intent content | Sales landing page |
| leads | Lead nurture sequence | Informational content | Lead gen landing page |

## Phase 2: Product & Market Analysis

1. Analyze the product's landing page:
   - What is the value proposition?
   - What is the CTA (call to action)?
   - What pricing model is used?
   - What social proof exists?
2. Based on `config.product.target_audience`, define 2-3 distinct audience segments:
   - **Broad**: Interest-based targeting (wide net)
   - **Lookalike**: If pixel has conversion data, recommend lookalike audiences
   - **Retargeting**: Website visitors who didn't convert (if pixel is active)
3. If historical learnings exist, factor in:
   - Which audiences had the lowest CPA?
   - Which placements performed best?
   - What time-of-day patterns emerged?

## Phase 3: Campaign Structure (Per Channel)

### Meta Ads Plan

Design the campaign architecture:

#### Campaign Level
- **Name**: `{product_name} - {objective} - {date}`
- **Objective**: Mapped from Phase 1
- **Budget Type**: Campaign Budget Optimization (CBO) recommended for budgets > $30/day; Ad Set Budget (ABO) for smaller budgets
- **Special Ad Categories**: Flag if product is housing, credit, employment, or politics

#### Ad Set Level (2-3 ad sets)

For each ad set, define:
- **Name**: Descriptive (e.g. "Interest - SaaS Founders 25-45")
- **Targeting**: Age range, gender, locations, interests/behaviors, exclusions
- **Placements**: Start with Advantage+ (automatic), or specify
- **Budget**: Allocation percentage of daily budget
- **Bid Strategy**: Lowest cost (default) or cost cap if CPA target specified
- **Schedule**: Start date, no end date (evergreen until paused)
- **Optimization Event**: From objective mapping

#### Ad Level (per ad set)
- **Format**: Dynamic Creative recommended
- **Creative slots**: 3-5 images, 5 primary text variations, 3 headlines, 2 descriptions
- **CTA Button**: Mapped from objective
- **URL**: `config.product.landing_url` with UTM parameters

### Google Ads Plan (if selected)

- Campaign type (Search, Display, Performance Max)
- Keyword targets (from SEO research or user input)
- Ad group structure
- Budget allocation between Meta and Google

### Email Plan (if selected)

- Sequence type based on objective and bottleneck
- Email cadence (timing between emails)
- Subject line strategy
- CTA alignment with paid ads messaging
- Trigger events

### SEO Plan (if selected)

- Content priorities based on gap analysis
- Target keywords per content piece
- Publishing cadence
- Internal linking strategy

### Landing Page Plan (if selected)

- Page goal aligned with campaign objective
- Section structure
- CTA alignment with ad messaging
- A/B test variant plan

### Outreach Plan (if selected)

- ICP definition based on product context
- Signal sources to monitor
- Sequence length and cadence
- Personalization strategy

## Phase 4: Budget Allocation

Present the budget breakdown across all channels:

```
Total Daily Budget: ${budget}

| Channel | Daily Budget | % | Role in Sequence |
|---------|-------------|---|-----------------|
| Meta Ads | ${amount} | X% | Acquisition |
| Google Ads | ${amount} | X% | Search capture |
| Email | $0 (infra cost) | -- | Activation/retention |
| SEO | $0 (content cost) | -- | Organic acquisition |
| Landing | $0 (one-time) | -- | Conversion |
| Outreach | $0 (tool cost) | -- | Direct outreach |

Meta Ads Breakdown:
| Ad Set | Audience | Daily Budget | % |
|--------|----------|-------------|---|
| AS1 | {desc} | ${amount} | X% |
| AS2 | {desc} | ${amount} | X% |
| AS3 | {desc} | ${amount} | X% |
```

Include recommendations:
- Minimum viable budget per ad set (typically $5-10/day for meaningful learning)
- Expected learning phase duration (typically 3-7 days, ~50 optimization events)
- If budget is too low for the number of ad sets, reduce to 2 or recommend increasing

## Phase 5: Creative Strategy Brief

For each channel, outline the creative approach:

### Meta/Google Ads Creative Brief
- **Angles to test**: (pain point, benefit, social proof, curiosity, urgency)
- **Image direction**: What the visuals should communicate
- **Copy framework**: Which copywriting formula to use per variation
- **Headline approach**: Direct vs. curiosity-driven

### Email Creative Brief
- **Subject line strategy**: Personalization, curiosity, benefit-driven
- **Body tone**: Match product brand voice
- **CTA style**: Consistent with ads for cross-channel coherence

### Content/SEO Creative Brief
- **Topic priorities**: Based on gap analysis
- **Format**: Long-form, comparison, FAQ, how-to
- **Keywords**: Primary and secondary per piece

This brief will be passed to the appropriate `/gtm-create`, `/gtm-email`, `/gtm-seo`, or `/gtm-landing` commands for execution.

## Phase 6: KPI Targets

Set benchmark KPIs based on objective and historical data:

| Metric | Target | Industry Avg |
|--------|--------|-------------|
| CPM    | $X     | $5-15       |
| CTR    | X%     | 1-2%        |
| CPC    | $X     | $0.50-2.00  |
| CPA    | $X     | Varies      |
| ROAS   | Xx     | 2-4x        |
| Email Open Rate | X% | 20-30% |
| Email Click Rate | X% | 2-5% |
| Landing Conv. Rate | X% | 2-5% |

If historical data exists in `.gtm/metrics/`, use those benchmarks instead of industry averages.

## Phase 7: Save and Output

1. Save the complete plan to `.gtm/plans/plan-{YYYY-MM-DD}.md` with all details above.
2. If a plan for today already exists, append a counter: `plan-{YYYY-MM-DD}-02.md`
3. Present a clean summary to the user with the campaign structure visualization.
4. Suggest next steps based on selected channels:
   - "Run `/gtm-create` to generate ad creatives for this plan"
   - "Run `/gtm-email` to create email sequences"
   - "Run `/gtm-seo` to generate SEO content"
   - "Run `/gtm-landing` to build the landing page"
   - "Run `/gtm-outreach` to build outreach sequences"
   - "Or run `/gtm` to execute the full lifecycle"

## Error Handling

- If the daily budget is less than $5, warn: "Meta requires a minimum of ~$1/day per ad set. With ${budget}/day, recommend a single ad set."
- If the objective doesn't map to a Meta objective, ask the user to clarify.
- If no historical learnings exist, note: "No past campaign data found. Using industry benchmarks. Data will improve after the first campaign cycle."
- If the product landing page URL is unreachable, warn but continue with available context.
- If a selected channel has no configured credentials, warn and offer to skip that channel or run `/gtm-setup` to configure it.
