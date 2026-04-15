---
description: "Create a media plan for paid campaigns"
argument-hint: "$budget/day objective (e.g. $20/day signups)"
---

# Media Planning Command

You are the media-buyer agent. You will create a detailed, actionable media plan for paid ad campaigns based on the user's budget, objective, product context, and historical learnings.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate that `meta.access_token`, `meta.ad_account_id`, and `product.landing_url` exist in the config.
   - If any are missing, list them and tell the user to run `/gtm-setup`. STOP.
3. Load product context from `config.product` (name, description, target_audience, pricing).
4. Read historical learnings:
   - `.gtm/learnings/targeting-insights.md` (if exists)
   - `.gtm/learnings/budget-allocation.md` (if exists)
   - `.gtm/learnings/creative-wins.md` (if exists)
5. Read past plans from `.gtm/plans/` to avoid repeating failed strategies.
6. Read past metrics snapshots from `.gtm/metrics/` for benchmark data.

## Phase 1: Parse Budget and Objective

Parse the user's argument string `$ARGUMENTS` for:
- **Daily budget**: Extract the dollar amount (e.g. "$20/day" → 20)
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

## Phase 3: Campaign Structure

Design the campaign architecture:

### Campaign Level
- **Name**: `{product_name} - {objective} - {date}`
- **Objective**: Mapped from Phase 1
- **Budget Type**: Campaign Budget Optimization (CBO) recommended for budgets > $30/day; Ad Set Budget (ABO) for smaller budgets
- **Special Ad Categories**: Flag if product is housing, credit, employment, or politics

### Ad Set Level (2-3 ad sets)

For each ad set, define:
- **Name**: Descriptive (e.g. "Interest - SaaS Founders 25-45")
- **Targeting**:
  - Age range
  - Gender (if relevant)
  - Locations (default: US, unless specified)
  - Interests / behaviors / custom audiences
  - Exclusions (existing customers if pixel data available)
- **Placements**: Start with Advantage+ (automatic), or specify:
  - Facebook Feed, Instagram Feed, Instagram Stories, Instagram Reels
  - Recommend against Audience Network for small budgets
- **Budget**: Allocation percentage of daily budget
- **Bid Strategy**: Lowest cost (default) or cost cap if CPA target specified
- **Schedule**: Start date, no end date (evergreen until paused)
- **Optimization Event**: From objective mapping

### Ad Level (per ad set)
- **Format**: Dynamic Creative recommended (Meta tests combinations automatically)
- **Creative slots**: 3-5 images, 5 primary text variations, 3 headlines, 2 descriptions
- **CTA Button**: Mapped from objective (Sign Up, Learn More, Shop Now, etc.)
- **URL**: `config.product.landing_url` with UTM parameters:
  - `utm_source=meta`
  - `utm_medium=paid`
  - `utm_campaign={campaign_name}`
  - `utm_content={ad_set_name}`

## Phase 4: Budget Allocation

Present the budget breakdown:

```
Daily Budget: ${budget}

| Ad Set | Audience | Daily Budget | % |
|--------|----------|-------------|---|
| AS1    | {desc}   | ${amount}   | X%|
| AS2    | {desc}   | ${amount}   | X%|
| AS3    | {desc}   | ${amount}   | X%|
```

Include recommendations:
- Minimum viable budget per ad set (typically $5-10/day for meaningful learning)
- Expected learning phase duration (typically 3-7 days, ~50 optimization events)
- If budget is too low for the number of ad sets, reduce to 2 or recommend increasing

## Phase 5: Creative Strategy Brief

For each ad set, outline the creative approach:
- **Angles to test**: (pain point, benefit, social proof, curiosity, urgency)
- **Image direction**: What the visuals should communicate
- **Copy framework**: Which copywriting formula to use per variation
- **Headline approach**: Direct vs. curiosity-driven

This brief will be passed to `/gtm-create` for execution.

## Phase 6: KPI Targets

Set benchmark KPIs based on objective and historical data:

| Metric | Target | Industry Avg |
|--------|--------|-------------|
| CPM    | $X     | $5-15       |
| CTR    | X%     | 1-2%        |
| CPC    | $X     | $0.50-2.00  |
| CPA    | $X     | Varies      |
| ROAS   | Xx     | 2-4x        |

If historical data exists in `.gtm/metrics/`, use those benchmarks instead of industry averages.

## Phase 7: Save and Output

1. Save the complete plan to `.gtm/plans/plan-{YYYY-MM-DD}.md` with all details above.
2. If a plan for today already exists, append a counter: `plan-{YYYY-MM-DD}-02.md`
3. Present a clean summary to the user with the campaign structure visualization.
4. Suggest next steps:
   - "Run `/gtm-create` to generate creatives for this plan"
   - "Or run `/gtm` to execute the full loop"

## Error Handling

- If the daily budget is less than $5, warn: "Meta requires a minimum of ~$1/day per ad set. With ${budget}/day, recommend a single ad set."
- If the objective doesn't map to a Meta objective, ask the user to clarify.
- If no historical learnings exist, note: "No past campaign data found. Using industry benchmarks. Data will improve after the first campaign cycle."
- If the product landing page URL is unreachable, warn but continue with available context.
