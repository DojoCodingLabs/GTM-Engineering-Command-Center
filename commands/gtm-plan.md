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

Map the objective to Google Ads campaign goals (Search-first; Google plans KEYWORDS / INTENT, not audiences):
| User Objective | Google Campaign | Bid Strategy (gate-aware) | Primary Conversion Action |
|----------------|-----------------|---------------------------|---------------------------|
| signups | Search (non-brand high-intent) | MAXIMIZE_CONVERSIONS until ~30 conv/mo → TARGET_CPA | signup / free-trial |
| purchases | Search + PMax feeder | MAXIMIZE_CONVERSIONS → TARGET_CPA → tROAS (≥60d value data) | purchase |
| leads | Search (problem + category) | MAXIMIZE_CONVERSIONS until ~30 conv/mo → TARGET_CPA | lead form / demo request |
| traffic | Search (broad discovery) | MAXIMIZE_CLICKS (`targetSpend`) only until conversion data exists | n/a (clicks) |
| app_installs | App / Demand Gen | MAXIMIZE_CONVERSIONS (install) | app install |

Bidding API fields are GATED on the migration ladder (Atlas Part IV) — never plan a rung the account has not earned. The campaign-operator enforces these gates at deploy. Full ladder in the Google Ads Plan block below and `skills/google-ads/rules/smart-bidding.md`.

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

> **CONTRAST — Meta plans AUDIENCES, Google plans KEYWORDS / INTENT.** Steps 2-3 above are Meta's audience-segment analysis. When **Google is selected**, do NOT run audience-segment analysis for Google; run the keyword / intent-ladder analysis below instead. (Meta planning logic is unchanged.)

### Google Ads — Keyword / Intent Analysis (run only if Google selected)

This is a READ/MEASURE step. It uses the read-only `google-ads-open-cli` (recipes in `skills/google-ads/rules/gads-cli.md`); it never writes. Money returns in **micros** — divide every `cost_micros` by 1,000,000 for dollars.

**Path A — account already exists (you have a customer ID):** mine real demand before inventing it.
- Pull existing search terms (last 30-90d) to see what queries actually trigger spend and convert:
  ```bash
  google-ads-open-cli query <customer-id> \
    "SELECT search_term_view.search_term, metrics.clicks, metrics.cost_micros, metrics.conversions \
     FROM search_term_view WHERE segments.date DURING LAST_90_DAYS \
     ORDER BY metrics.cost_micros DESC" --format compact
  ```
- Pull current keyword performance + match types and impression share to find gaps:
  ```bash
  google-ads-open-cli keyword-stats <customer-id> --start <YYYY-MM-DD> --end <YYYY-MM-DD>
  google-ads-open-cli keywords <customer-id>          # existing keywords + match types
  google-ads-open-cli negative-keywords <customer-id> # existing negatives / shared sets
  ```
- N-gram the search terms (tokenize into 1/2/3-grams, roll up cost ÷ 1e6 and conversions) to seed both new keyword themes AND the negative list. Full recipe: `skills/google-ads/rules/gads-cli.md` §7a.
- Normalized exit handling for the read CLI: capture stderr; if non-zero and stderr matches `/auth|token|credential|unauthenticated|permission/i` → auth error, tell the operator to re-run `google-ads-open-cli auth login`; else → API error (backoff + one retry). (This is a different binary from Meta's — do not assume Meta's literal exit codes.)

**Path B — no account / no history yet:** derive intent from `product.landing_url` and competitors.
- Extract the value prop, feature nouns, outcome verbs, and category terms from the landing page → these become **category** and **problem** keyword seeds.
- Derive **competitor** seeds from named competitors (`{competitor} alternative`, `{competitor} vs`, `{competitor} pricing`).
- Derive **brand** seeds from `product.name`.
- Expand each seed across the 4 intent types (informational / commercial / transactional / navigational) per `skills/google-ads/rules/keywords-match-types.md` Step 2.

**Output of this phase:** a keyword set bucketed into the five intent lanes (brand / high-intent product / competitor / problem-aware / remarketing), each lane tagged with a candidate match type. This bucketing — not audience segments — is what feeds the Google plan block.

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

> **Meta plans AUDIENCES. Google plans KEYWORDS / INTENT.** The Meta block above splits by audience segment; this block splits by INTENT THEME. Build it from the Phase 2 keyword/intent buckets, not from audience personas. Cross-ref `agents/media-buyer.md` (Google Ads Planning) and `skills/google-ads/rules/keywords-match-types.md`. All money below is in **micros** (budget = `amountMicros`, 1,000,000 = $1). All campaign writes deploy **PAUSED**.

#### Structure: one campaign per intent lane → one ad group per tight keyword theme

Google's hierarchy is `Campaign (1 intent lane + budget + bid strategy) → Ad Group (1 tight keyword theme) → RSA`. Each intent lane is its OWN campaign with its OWN budget and bid strategy — lanes never share budget (Atlas Part II intent ladder). Inside a lane, split into ad groups BY INTENT THEME (one tight 5-10 keyword theme per ad group) — this is what drives Quality Score; a 50-keyword ad group tanks it (`keywords-match-types.md`, Ad Group Granularity).

```
Campaign: Brand (Pillar 1)
  └── Ad Group: {product_name} core        → [product_name], [product_name pricing]
  └── Ad Group: {product_name} login/nav   → [product_name login], [product_name app]
Campaign: High-Intent Product (Pillar 2)
  └── Ad Group: {outcome} theme            → "{outcome} software", "{outcome} tool"
  └── Ad Group: {use_case} theme           → "{category} for {use_case}"
Campaign: Competitor Conquest (Pillar 3 — ISOLATED budget + QS drag)
  └── Ad Group: {competitor} alternative   → "{competitor} alternative", "{competitor} vs"
Campaign: Problem-Aware (Pillar 4)
  └── Ad Group: {pain_point} theme         → "how to {solve_problem}", "{pain_point} solution"
Campaign: Remarketing / Nurture (Pillar 5)
  └── Ad Group: site visitors / cart       → audience lists, RLSA / Demand Gen
```

#### Keyword tiers + match types (the intent ladder)

Five lanes, one campaign each, no cross-lane budget sharing. Cross-ref `agents/media-buyer.md` (Keyword Tiers) and `skills/google-ads/rules/keywords-match-types.md`:

| Lane (Pillar) | Intent | Keyword tier | Default match type | Notes |
|---------------|--------|--------------|--------------------|-------|
| 1. Brand | Navigational, own name | `{product_name}`, `{product_name} pricing` | Exact `[ ]` | Cheap, defends SERP, isolate from QS drag |
| 2. High-intent product | Transactional / outcome | `{outcome} software`, `{category} for {use_case}` | Phrase `" "` + Broad (Smart Bidding only) | Phrase converts best; broad only past the conv floor |
| 3. Competitor | Comparison / switch | `{competitor} alternative`, `{competitor} vs` | Exact + Phrase | OWN campaign; NO DKI; trademarks OUT of ad copy |
| 4. Problem-aware | Informational | `how to {solve_problem}`, `{pain_point} solution` | Broad (Smart Bidding) | Needs strong landing page; expect lower CVR |
| 5. Remarketing | Re-engage | n/a — audience lists | n/a | RLSA / Demand Gen, not keywords |

Match-type doctrine (broad-match era): **broad scales spend, phrase converts, exact controls — none is obsolete.** Broad match ONLY with Smart Bidding (Target CPA / Max Conversions); broad + Manual CPC = budget drain. On tight budgets, do NOT mix broad and exact in one campaign — broad starves exact of delivery; split them into separate campaigns (`keywords-match-types.md`).

#### Bidding strategy — GATED on the conversion-migration ladder (Atlas Part IV)

Plan the bid strategy each lane has EARNED — climb one rung at a time, never skip. The campaign-operator enforces these gates at deploy:

| Rung / Strategy | Gate (the migration ladder) | API field |
|-----------------|-----------------------------|-----------|
| Maximize Clicks | No conversion data yet; exit ASAP once clicks/CTR exist | `targetSpend` |
| Maximize Conversions | Conversion tracking live, below the tCPA gate | `maximizeConversions` |
| Target CPA | **~30 conv/mo/campaign** (the tCPA gate — below it Smart Bidding starves) | `targetCpa` (`targetCpaMicros`, micros) |
| Target ROAS / Max Conv Value | **~60 days of value data AND ≥2 distinct conversion values** | `maximizeConversionValue` → `targetRoas` |

`targetCpaMicros` IS micros (1e6 = $1); `targetRoas` is a raw multiplier (`4.0` = 400%), NOT micros. Set the initial tCPA/tROAS at 70-80% of trailing actual (looser, keeps delivery open), then tighten ~10%/2-week hold. Most new/thin Google plans start lanes 2 and 4 on `maximizeConversions` because they have not crossed the 30-conversion gate; brand (lane 1) can sit on Manual CPC or Max Clicks with strict caps. Full ladder: `skills/google-ads/rules/smart-bidding.md`.

#### Negative-keyword + brand-exclusion plan (hand the operator the list)

Negatives are the real fence in the broad-match era — not match-type hierarchy (`keywords-match-types.md`, AI-Era Nuance). Plan them up front:

- **Account-level negative list** (always, unless the product genuinely offers it): `free`, `tutorial`, `course`, `salary`, `jobs`, `review`, `download`, `cracked`, `torrent`.
- **Cross-lane brand exclusions:** add `{product_name}` as a NEGATIVE in lanes 2-4 so brand traffic stays in the brand campaign (clean attribution, no inflated non-brand conversions). Add competitor names as negatives in lanes 1, 2, 4 so only the competitor campaign serves on them.
- **N-gram-driven negatives:** once data exists, mine the search-terms report (Phase 2 Path A) and add the worst non-converting grams. Avg 36% of spend is wasted on unmonitored broad terms (`keywords-match-types.md`, N-gram mining).
- **Deploy path:** adding negatives is a WRITE — it does NOT go through the read CLI. Negative-keyword creation uses the Google Ads REST API `:mutate` endpoints via curl (no first-party CLI mutates); new negative campaigns/ad-groups deploy PAUSED.

**WHITEHAT | 10/10** — N-gram waste aggregation and brand-exclusion negatives analyze your own account data to cut wasted spend; pure measurement-driven hygiene.

**WHITEHAT | 9/10** — Competitor "alternative"/"vs" bidding in its own campaign with trademarks kept out of ad copy is permissible fair-use; isolate the budget and Quality Score drag.

**BLACKHAT | 1/10** — Documented so you recognize it — never deploy: Dynamic Keyword Insertion that auto-inserts a competitor's trademarked name into your headline is an instant trademark-policy violation. Never enable DKI in a competitor campaign.

#### RSA + URL per ad group

Each ad group gets one Responsive Search Ad: 15 headlines (30 char), 4 descriptions (90 char, ≥2 with a CTA), final URL = `config.product.landing_url` with `?utm_source=google&utm_medium=cpc&utm_campaign={campaign}&utm_term={keyword}`. Pin the brand/keyword theme into ≥2 headlines to lift Quality Score. Cross-ref `agents/media-buyer.md` (RSA Structure).

> **Budget split:** the five-pillar internal allocation for the Google daily budget lives in Phase 4. Cross-channel split between Meta and Google follows `agents/media-buyer.md` Channel Budget Allocation.

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

Meta Ads Breakdown (by AUDIENCE):
| Ad Set | Audience | Daily Budget | % |
|--------|----------|-------------|---|
| AS1 | {desc} | ${amount} | X% |
| AS2 | {desc} | ${amount} | X% |
| AS3 | {desc} | ${amount} | X% |

Google Ads Breakdown (by INTENT LANE — five-pillar split, Atlas Part II):
| Pillar / Campaign | Intent lane | Daily Budget | % | Bidding + match |
|-------------------|-------------|-------------|---|-----------------|
| 1. Brand protection | own name | ${amount} | 5-7% | Manual CPC, exact |
| 2. High-intent product | outcome / category | ${amount} | 50-60% | tCPA, phrase + broad |
| 3. Competitor conquest | alternative / vs | ${amount} | 15-20% | tCPA, exact + phrase |
| 4. Problem-aware | how-to / pain | ${amount} | 10-15% | Max Conversions, broad |
| 5. Remarketing / nurture | site / cart lists | ${amount} | 10% | Max Conversions, audiences |
```

> **Google budget is in micros at deploy** — each daily `${amount}` becomes `amountMicros` (× 1,000,000) on the campaign budget. The percentages above are a steady-state starting allocation. For a NEW/thin account, override with the PHASED split (Atlas Part XIV): Phase 1 (≤$10k/mo) ~90% into Pillar 2 bottom-funnel Search to set baselines; Phase 2 ($10-30k) ~70% Search / 30% PMax + Customer Match; Phase 3 ($30k+) layer YouTube / Demand Gen at ~15-20% for the demand-creation lane. Do not fund competitor/problem-aware lanes until the high-intent lane has crossed its conversion floor.

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

If Google Ads is selected, add the Google-native KPIs (keyword/auction metrics Meta has no analog for):

| Google KPI | Target | Benchmark / Note |
|------------|--------|------------------|
| Search Impression Share (SIS) | ≥ 65% brand, ≥ 40% non-brand | `search_impression_share`; low SIS = budget- or rank-limited |
| Search Lost IS (budget) | < 10% | If high, budget caps delivery — raise budget before bids |
| Search Lost IS (rank) | < 20% | If high, Quality Score / bid is the limiter, not budget |
| Quality Score (avg) | ≥ 7/10 | Driven by tight ad-group themes + RSA keyword pinning + page relevance |
| Search CPC | $X | Google's per-CLICK metric — contrast Meta's CPM (per-1000-impression) |
| Cost / conversion (CPA) | ≤ target | `cost_micros ÷ 1e6 ÷ conversions`; the migration-ladder gate watches this |

> **CPC vs CPM is the channel contrast in one line:** Google = pay-per-CLICK on active search intent (track SIS + Quality Score + CPC); Meta = pay-per-CPM on interrupt audiences (track CPM + CTR). Do not benchmark Google CPC against Meta CPM — different units. All Google cost figures arrive as `cost_micros`; divide by 1,000,000 for dollars.

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
