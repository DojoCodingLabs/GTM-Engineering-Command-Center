---
name: google-ads
description: Google Ads expertise — read/measure via the google-ads-open CLI + REST :mutate deploy, signal-first architecture (Hagakure, brand isolation, intent ladder, 5-pillar budget), Performance Max control + Moran feeder, Smart Bidding migration ladder, Enhanced Conversions + Consent Mode v2 + GCLID-to-CRM, broad-match-era keywords + n-gram mining, AI Max for Search, RSA/YouTube creative, policy/reinstatement. Ethical scores (whitehat/grayhat/blackhat 1-10) from the Google Ads Atlas 2026.
---

# Google Ads API & Campaign Management

In 2026 Google Ads is a signal-architecture discipline, not keyword management (Atlas Part I). The gap between an average advertiser and a sophisticated operator is not setup, bids, or even creative — it is the quality of the conversion truth fed back into the machine. Hyper-granular legacy Search structures are now a hidden cost; the winners run consolidated structures, broad match paired with Smart Bidding, and an obsessive focus on offline conversion imports, Enhanced Conversions, Customer Match, and value-based bidding. For info products and SaaS this matters more than for e-commerce, because the revenue event sits several stages downstream of the click — optimize to a proxy event (form fill, free trial, webinar reg) without sending the real outcome back and Google will find you an endless supply of junk.

## Default Tooling

Execution is **HYBRID**. There is no first-party CLI that mutates Google Ads, so reads and writes use different paths — always be explicit which one a step is on.

- **Read / measure / audit → `google-ads-open-cli`** (a Node 18+ CLI, **READ-ONLY**). Full command reference: `rules/gads-cli.md`. Install `npm install -g google-ads-open-cli`; output is pretty JSON (`--format compact` for one line).
- **Campaign WRITES / deploys → Google Ads REST `:mutate` endpoints via `curl`.** No first-party CLI mutates; every create/update/delete is a `POST …:mutate` call against `googleads.googleapis.com/vXX/`.

**Use the CLI for:** account hierarchy, customers, campaigns/ad-groups/ads/keywords/negatives, audiences/user-lists, assets/extensions, conversion-actions, budgets, billing, change-status, all `*-stats` reporting, and raw GAQL (`query <id> "SELECT …"`).

**Use REST `:mutate` for:** creating/updating/pausing campaigns, budgets, ad groups, RSAs, keywords, negatives, asset groups, audience signals, bid strategies, conversion actions, and offline conversion / Enhanced Conversion uploads.

> **MONEY IS IN MICROS.** 1,000,000 micros = $1. Budgets are `amountMicros`; every stat `cost_micros ÷ 1e6` = dollars. This is the Google analog of Meta's "cents" trap — divide before you report, multiply before you mutate.
>
> **ALL campaign writes default to status `PAUSED`.** Launch is a separate, deliberate `:mutate`.

## The Five Laws of 2026 Google Ads

From Atlas Part I — the operating system, not slogans.

| # | Law |
| :---- | :---- |
| 1 | **Signal beats structure.** The account that feeds the cleanest conversion truth wins. Offline imports, Enhanced Conversions for Leads, and value-based bidding are the OS now — manual bid tinkering is a rounding error next to data quality. |
| 2 | **Isolate brand or lie to yourself.** Mixed brand/non-brand inflates reported ROAS and mis-teaches the bidder. A dedicated brand campaign plus brand exclusions on every non-brand and automated campaign is non-negotiable. PMax backfills 10–42% of its reported conversions from your own brand if you let it. |
| 3 | **PMax for lead gen is guilty until proven innocent.** Left alone it finds the cheapest, lowest-quality lead possible. Only CRM-stage feedback, exclusions, audience inputs, geo, and schedule controls make it honest. Low CPLs are a hypothesis to test against pipeline, never a result. |
| 4 | **Browse surfaces shape demand; Search captures it.** Treat Demand Gen and YouTube like paid social, not watered-down Search. They need creative-led selection and low-friction offers. Forcing cold browse into a hard demo/application ask produces weak quality or policy trouble. |
| 5 | **Automate selectively, never on a rep's say-so.** Adopt Smart Bidding, AI Max, and PMax only after signal hygiene is in place. Keep Max Clicks / exact / manual alive longer than a rep would prefer if the data integrity isn't there. Use reps for product availability, not budget allocation. |

## How to Read the Ethical Scores

Every tactic in this skill carries a classification and a 1–10 score (Atlas judgment, not Google's labels):

- **WHITEHAT (8–10)** — fully compliant, sustainable, no deception. Safe to scale; the backbone of a durable account.
- **GRAYHAT (4–7)** — exploits gaps, auction mechanics, or unenforced edges. Allowed or unpoliced but ethically ambiguous; watch for policy drift and reputational cost.
- **BLACKHAT (1–3)** — violates policy, deceives users, or causes harm. Documented for recognition only — never deploy. High suspension and consumer-harm risk.

This skill documents every tactic neutrally with its score; the operator decides. It does NOT inherit the `gtm-atlas` hub's "only recommend Tier 1–2" default.

## The Cross-Surface Map

Each Google surface plays a distinct funnel role. Confusing those roles is the most common and most expensive mistake (Atlas Part I).

| Surface | Funnel role | Good at | 2026 risk |
| :---- | :---- | :---- | :---- |
| Search (brand) | Capture, defend | Highest ROAS, protects margin | Letting PMax cannibalize it |
| Search (non-brand) | Capture intent | High-intent demand, evaluation queries | Broad-match waste without negatives |
| Performance Max | Capture + light prospecting | Volume, cross-inventory reach | Junk leads, brand backfill, opacity |
| AI Max for Search | Enhanced capture | Query expansion, dynamic copy & URLs | Off-brand expansion, lost control |
| Demand Gen | Create & shape demand | Social-style browse reach | Treated like Search; Display spam |
| YouTube | Warm, pre-qualify | Lowers downstream Search CPA | Last-click ROAS misjudges it |
| Display | Prospect, remarket | Cheap reach | Spam leads in lead gen |
| Shopping | Capture (physical goods) | Product-feed intent | Mostly ineligible for digital goods |
| App | Acquire app users | Install & in-app scale | Optimizing to installs, not value |

## Campaign Hierarchy

```
Google Ads Account (customer ID: XXX-XXX-XXXX)
  └── Campaign (campaign_type, bidding_strategy, budget)
       └── Ad Group (keywords, targeting, CPC bids)
            └── Ad (responsive search ad, responsive display ad, etc.)
                 └── Extensions (sitelinks, callouts, structured snippets)
```

Reads traverse this with `account-hierarchy`/`campaigns`/`ad-groups`/`ads`. Writes hit `POST /customers/{id}/<resource>:mutate`. PMax replaces ad groups with **asset groups**:

```
Performance Max Campaign
  └── Asset Group (equivalent to ad group)
       ├── Headlines (3-15, max 30 chars each)
       ├── Long Headlines (1-5, max 90 chars)
       ├── Descriptions (2-5, max 90 chars)
       ├── Images (min 3: landscape 1200x628, square 1200x1200, portrait 960x1200)
       ├── Logos (min 1: square 1200x1200, landscape 1200x300)
       ├── Videos (optional but recommended, 10s+ horizontal)
       ├── Final URL
       └── Audience Signals (your targeting hints, not restrictions)
```

## Account Architecture

Isolate distinct intent lanes so incompatible journeys are not force-fit into one bid target. Build at minimum four lanes, plus a fifth for SaaS (Atlas Part II):

- **Brand** — defends your own name at high ROAS / low CPC; isolated from everything.
- **Non-brand high-intent** — outcome, mechanism, and evaluation queries with real purchase intent.
- **Broad discovery & expansion** — broad match + Smart Bidding to find queries manual research misses, fenced by aggressive negatives.
- **Competitor & conquesting** — comparison/alternative queries in their own campaign, never sharing budget with core non-brand.
- **SaaS only: company-size / use-case clusters** — SMB self-serve demo queries behave nothing like enterprise RFP queries; bid separately.

Steady-state budget split (the five-pillar funnel matrix):

| Pillar | Budget share | Bidding & match |
| :---- | :---- | :---- |
| 1. Brand protection | 5–7% | Manual CPC, exact match |
| 2. High-intent product | 50–60% | tCPA, phrase + broad match |
| 3. Competitor conquest | 15–20% | tCPA, exact + phrase match |
| 4. Problem-aware | 10–15% | Maximize Conversions, broad match |
| 5. Remarketing & nurture | 10% | Maximize Conversions, audience lists |

→ `rules/account-architecture.md`

## Smart Bidding Migration Ladder

Climb deliberately; each rung is a data prerequisite for the next. Do not jump to tROAS without value data (Atlas Part IV).

```
Manual CPC
  └─→ Maximize Clicks            (gather traffic + early conversion data)
       └─→ Maximize Conversions  (volume-stable, no value data yet)
            └─→ tCPA             (~30 conv/mo per campaign)
                 └─→ Maximize Conversion Value
                      └─→ tROAS  (~60 days of value data + ≥2 distinct conversion values)
```

When you set a target, **start at 70–80% of the trailing achieved target** (looser CPA / lower ROAS than current actuals), then tighten — set it at the goal on day one and the bidder chokes volume.

→ `rules/smart-bidding.md`

## Conversion Tracking & Privacy

- **Enhanced Conversions for Leads** — SHA-256 hashed first-party identifiers; target a **40–65% match rate** (advance only above 40%).
- **Consent Mode v2** — the four signals: `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization` (Advanced mode for conversion modeling).
- **GCLID → CRM offline loop** — capture GCLID at click, store on the lead, import the closed-won outcome back via `offlineConversion`/`conversionAdjustment` `:mutate` so the bidder optimizes to revenue, not form fills.

→ `rules/conversion-tracking.md`

## Performance Max Control

PMax is **guilty until proven innocent** for lead gen — left alone it harvests the cheapest junk lead it can find. Distinguish the three control mechanisms:

- **Brand exclusions** — account-level lists that stop PMax backfilling conversions from your own brand searches (verify branded share trends toward zero).
- **Negatives** — query/placement exclusions (account-level negative lists, campaign negatives).
- **Restrictions** — audience signals, geo, schedule, URL/feed constraints that shape where PMax spends.

**Moran feeder:** starve PMax of branded and easy traffic upstream (dedicated brand + non-brand Search capture it first), so PMax is forced to do genuine prospecting on what's left.

→ `rules/performance-max.md`

## Keywords in the Broad-Match Era

Broad match **wins when the conversion signal is clean** and bleeds you when it isn't — it inherits the quality of your Smart Bidding feedback. The search-terms report is degrading, so **mine n-grams**: tokenize search terms, rank waste by spend-with-no-conversion, and push losers to negatives weekly (daily on high spend). In the AI era, **exact no longer fences broad** — AI Overviews and close-variant matching mean an exact keyword can still trigger on loosely related queries, so negatives do the fencing exact used to.

→ `rules/keywords-match-types.md`

## AI Max for Search

Cautious optimism. AI Max layers query expansion, dynamic copy, and dynamic URLs onto Search. The base rate is 84% neutral-or-negative, so **partial adoption is the worst outcome** — half-on, no guardrails produces off-brand drift with none of the upside. Run it as a **contained, incrementally-measured experiment**: one well-structured campaign, all three features on, full guardrails (brand restrictions, URL exclusions, text guidelines), evaluated at the account level. Kill it if account-level CPL or CAC worsens after 2–4 weeks.

→ `rules/ai-max-search.md`

## Creative Strategy

- **RSA** — supply the full asset pool: **15 headlines, 4 descriptions**; pin sparingly, include the keyword theme in headlines for relevance.
- **YouTube** — hybrid AI hook (AI-generated open) into a 2–3 minute human creative; tCPA-seed around $8 with 15% increments.
- **SaaS** — demo-first: lead with the product in motion, not a talking-head promise.

→ `rules/creative-assets.md`

## SaaS & Info-Product Motions

**SaaS — three motions:** self-serve, free-trial, demo-led. **Info products — three funnel shapes:** webinar funnel, paid-community trial, tripwire/book. The unifying rule: **bid to SQL or booked-call, not form-fill or application.** A webinar registration, free-trial start, or cheap form fill is not a sale — optimize to the downstream truth via offline imports or Google will flood you with proxy events that never convert.

→ Atlas Parts X (info products) & XI (SaaS)

## Cross-Surface Orchestration & Incrementality

Phase budget by spend level (Atlas Part XIV) — early money concentrates almost entirely on bottom-of-funnel capture before expanding into demand creation:

- **Phase 1 (≤ $10k/mo)** — ~90% BOFU Search (brand + high-intent non-brand). Fix measurement first.
- **Phase 2 ($10–30k/mo)** — ~70/30 Search / PMax once downstream feedback keeps automation honest.
- **Phase 3 ($30k+/mo)** — add YouTube / Demand Gen at 15–20% for demand creation.

**Incrementality over attribution:** geo holdouts, Conversion Lift experiments, and MER/MMM, not last-click platform ROAS. Reject any platform-reported win that does not survive CRM or causal-lift scrutiny.

## Policy & Compliance

Enforcement is industrial: Google ran **~39.2M account suspensions in 2024**. Trigger categories cluster around income/earnings claims, before-and-after, and sensitive verticals. Know the reinstatement framework before you scale anything risky, and never run multiple accounts to evade a suspension.

→ `rules/policy-compliance.md`

## The Ethical Matrix

Every tactic in this skill is scored 1–10 inline. The full Unified Ethical Ranking Matrix — every documented tactic, its class, and its rationale in one table — is **Atlas Part XVI**.

## Implementation Playbook

The staged sequence from Atlas Part XVII — do not skip ahead; measurement is the prerequisite for everything downstream.

- **Stage 1 — Foundation (weeks 1–4):** fix measurement (Enhanced Conversions web + Leads, Consent Mode v2, GCLID→CRM; advance only above 40% match) → isolate brand (dedicated campaign + exclusions everywhere) → consolidate to thematic Hagakure, kill SKAGs, build negative lists.
- **Stage 2 — Signal & bidding (weeks 4–12):** climb the bid ladder to SQL / purchase via offline imports → install the script stack (Mike Rhodes PMax script + n-gram analyzer; review search terms weekly, daily on high spend) → stabilize low-volume accounts with micro-conversion values.
- **Stage 3 — Expansion (month 3+):** add demand creation (YouTube + Demand Gen) → run AI Max as a contained, guardrailed experiment evaluated at account level → prove incrementality (geo holdouts, lift experiments) before pouring in budget.

## Authentication

`google-ads-open-cli` auth: `google-ads-open-cli auth login --developer-token=… --client-id=… --client-secret=…`, OR env vars `GOOGLE_ADS_ACCESS_TOKEN` / `GOOGLE_ADS_DEVELOPER_TOKEN` / `GOOGLE_ADS_LOGIN_CUSTOMER_ID`. Creds are stored at `~/.config/google-ads-open-cli/credentials.json`.

REST `:mutate` and full OAuth env:

```bash
GOOGLE_ADS_DEVELOPER_TOKEN=XXXXXXXXXX      # From Google Ads API Center
GOOGLE_ADS_CLIENT_ID=XXXXX.apps.google     # OAuth client ID
GOOGLE_ADS_CLIENT_SECRET=XXXXXX            # OAuth client secret
GOOGLE_ADS_REFRESH_TOKEN=1//XXXXXX         # Long-lived refresh token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=XXX-XXX-XXXX  # MCC account ID (if using manager)
GOOGLE_ADS_CUSTOMER_ID=XXX-XXX-XXXX        # Target ad account
```

**Exit handling (read CLI):** capture stderr. If non-zero and stderr matches `/auth|token|credential|unauthenticated|permission/i` → auth error, tell the operator to re-run `google-ads-open-cli auth login`. Otherwise → API error: back off and retry once. (This binary is NOT the Meta CLI — do not assume Meta's literal 0/3/4 exit codes.)

**API rate limits:**

- Basic access: 15,000 requests/day, 1,500 operations/mutate
- Standard access: 100,000 requests/day
- Reporting: 10 concurrent report requests
- Mutate operations: max 5,000 operations per request

## Knowledge Base

Full tactic detail lives in `knowledge/google-ads-atlas-2026.md` (18 Parts + Appendices A–D). Cite as "Atlas Part X". Read it when you need:

- **Full tactic detail and execution steps** — any Part beyond the distillation here.
- **Benchmarks** — Appendix A (CPC, CPL, CVR by vertical and SaaS stage; directional only).
- **The ethical matrix** — Part XVI, the full Unified Ethical Ranking.
- **Named-practitioner sources** — Appendix C (who said what, with attribution).

## Rules Reference

- `rules/gads-cli.md` — `google-ads-open-cli` full read-only command reference (primary measurement tool)
- `rules/account-architecture.md` — intent ladder, Hagakure consolidation, five-pillar budget, brand isolation
- `rules/performance-max.md` — PMax control levers, brand exclusions vs negatives vs restrictions, Moran feeder
- `rules/smart-bidding.md` — the migration ladder, 70–80% target rule, value-based bidding for low-volume
- `rules/conversion-tracking.md` — Enhanced Conversions, Consent Mode v2, GCLID→CRM offline loop
- `rules/keywords-match-types.md` — broad-match-era strategy, n-gram waste mining, negatives discipline
- `rules/ai-max-search.md` — AI Max contained-experiment protocol and guardrails
- `rules/creative-assets.md` — RSA asset construction, YouTube hooks, SaaS demo-first creative
- `rules/policy-compliance.md` — enforcement triggers, reinstatement framework, cloaking (documented, not endorsed)
