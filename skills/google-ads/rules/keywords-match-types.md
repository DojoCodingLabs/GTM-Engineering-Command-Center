# Google Ads Keywords & Match Types -- Strategy, Research, and the Broad-Match Era

> Channel: Google Ads. Layers **Atlas Part VI** (broad-match era doctrine) onto the keyword reference below. READ/MEASURE (search-term pulls, n-gram mining, keyword stats) runs through the read-only `google-ads-open-cli` — recipes in `skills/google-ads/rules/gads-cli.md`. WRITE/DEPLOY (adding negatives, building conquesting campaigns) uses the Google Ads REST API `:mutate` endpoints via curl; no first-party CLI mutates. All money is in **micros** (1,000,000 = $1). All campaign writes default to **PAUSED**.

## Keyword Match Types

### Match Type Comparison

| Type | Syntax | Example Keyword | Will Match | Won't Match |
|------|--------|----------------|------------|-------------|
| Broad | `learn solidity` | "solidity tutorial", "blockchain programming course", "web3 coding" | — |
| Phrase | `"learn solidity"` | "learn solidity online", "best way to learn solidity" | "solidity learn", "is solidity hard to learn" |
| Exact | `[learn solidity]` | "learn solidity", "learning solidity" (close variants) | "learn solidity online", "best solidity course" |

### Match Type Strategy by Stage

```
New campaign (week 1-2):
  Start with exact match + phrase match on your highest-intent keywords.
  This gives you data without wasting budget on irrelevant broad matches.

Growing campaign (week 3-8):
  Add phrase match versions of working exact match keywords.
  Monitor search term reports weekly for new keyword ideas.

Scaled campaign (week 8+):
  Test broad match on your best-performing themes WITH smart bidding.
  Broad match only works well with Target CPA or Maximize Conversions.
  Never use broad match with Manual CPC -- you'll waste budget.
```

### The Broad Match + Smart Bidding Rule

Broad match has changed significantly. With smart bidding (Target CPA, Maximize Conversions), Google uses broad match as a signal to find relevant searches you didn't anticipate. Without smart bidding, broad match is a budget drain.

```
Broad match + Manual CPC = Budget waste (Google matches too loosely)
Broad match + Smart bidding = Discovery engine (Google bids low on risky matches)
Exact match + Manual CPC = Maximum control, limited reach
Phrase match + Smart bidding = Best balance for most accounts
```

## When Broad Match Wins (and When It Bleeds You)

Atlas Part VI doctrine. Google has shifted targeting from exact keyword matching to semantic intent matching. The question is no longer which match type you prefer — it is whether your signals and negatives are strong enough to let broad match work.

Broad beats phrase/exact **only** when all three are present:

```
1. Clean conversion tracking (no broken tags, no double-counting, primary actions correct)
2. First-party signals feeding the account (Enhanced Conversions, Customer Match, GA4 audiences)
3. Value-based bidding (tROAS / Max Conversion Value, not just Max Clicks)
```

With poor tracking or a thin budget, broad match is the **fastest way to burn budget** on low-intent traffic. The algorithm has no truth data to steer toward, so it explores indiscriminately.

### The conversion-volume threshold

Broad match needs truth data before it behaves. Do not switch a theme to broad until it has crossed the learning floor:

```
~30-50 conversions  → practical floor before broad behaves (Sarah Stemen)
60+ conversions     → most successful PMax accounts had crossed this (Optmyzr)
```

Below that floor, stay on exact + phrase. The 2026 match-type trend (Optmyzr's 30,000-account study): exact has shed ~10 points of spend share since 2022, broad is now the dominant match type by budget, and **phrase still leads on conversion rate** in both e-commerce and lead-gen. Translation: broad scales spend, phrase converts, exact controls — none is obsolete.

### Split broad and exact on tight budgets

On constrained budgets, broad in the same campaign as exact will **starve exact of delivery** — it hogs shared budget and prevents your highest-intent keywords from getting real volume. The 2026 structural move (Jyll Saskin Gales): prefer exact OR broad, often in **separate campaigns**, and stop treating phrase as the dependable Goldilocks middle.

```
TIGHT BUDGET STRUCTURE:
  Campaign A — Exact match, high-intent terms, own budget, tROAS/tCPA
  Campaign B — Broad match, discovery themes, own budget, capped, value-based bidding
  → Broad cannot cannibalize exact's delivery; each budget expresses its own intent
```

**WHITEHAT | 9/10** — Splitting broad and exact when budgets are tight keeps broad from starving exact and lets each budget express its intent.

## Keyword Research Process

### Step 1: Seed Keywords

Start with 3-5 core terms that describe what you sell:

```
Seed examples (coding bootcamp):
  - "coding bootcamp"
  - "learn programming"
  - "web development course"
  - "software engineering training"
  - "blockchain developer"
```

### Step 2: Expand with Intent Layers

For each seed, create variants across all 4 intent types:

```
Seed: "coding bootcamp"

Informational:
  "what is a coding bootcamp"
  "coding bootcamp vs self-taught"
  "how long is a coding bootcamp"
  "are coding bootcamps worth it"

Commercial:
  "best coding bootcamps 2026"
  "coding bootcamp reviews"
  "top 10 coding bootcamps"
  "coding bootcamp comparison"

Transactional:
  "enroll coding bootcamp"
  "coding bootcamp free trial"
  "coding bootcamp pricing"
  "coding bootcamp discount"

Navigational:
  "[brand] coding bootcamp"
  "[brand] login"
  "[brand] reviews"
```

### Step 3: Competitor Keywords

Target competitor brand names (legally allowed, but controversial). See **Competitor Conquesting: Ethics & Execution** below for the full doctrine before you deploy.

```
Strategy:
  "[competitor] alternative"  → Your ad: "Looking for a [Competitor] Alternative?"
  "[competitor] vs"           → Your ad: "Why Developers Switch to [Your Brand]"
  "[competitor] pricing"      → Your ad: "More Value at Half the Price"
  "[competitor] reviews"      → Your ad: "See Why We're Rated #1"

Rules:
  - Never use competitor trademarks in your ad text (policy violation)
  - You CAN use competitor names as keywords
  - Expect higher CPC (lower Quality Score since your page isn't about them)
  - Best for brands with strong differentiation vs the competitor
```

### Step 4: Long-Tail Keywords

Long-tail keywords (3-5+ words) have lower volume but higher intent and lower competition:

```
Short-tail (expensive, competitive):
  "coding bootcamp" -- 50K searches/month, $15 CPC

Long-tail (cheaper, higher intent):
  "coding bootcamp for career changers online" -- 500 searches/month, $3 CPC
  "blockchain developer bootcamp with job guarantee" -- 200 searches/month, $4 CPC
  "learn solidity smart contract development" -- 300 searches/month, $2 CPC
```

For accounts under $5K/month, focus exclusively on long-tail keywords.

## Search Term Report Analysis

Review the Search Terms Report weekly. This shows actual queries that triggered your ads.

### Triage Process

```
For each search term in the report:

1. High intent, converting → Add as exact match keyword
2. High intent, not converting yet → Keep, add to monitoring list
3. Relevant but low intent → Add as phrase match with lower bid
4. Irrelevant → Add as negative keyword immediately
5. Competitor name → Evaluate: worth the CPC? Add negative if not
```

### Red Flags in Search Terms

```
Warning signs that your keyword strategy needs fixing:
  - 50%+ of spend going to search terms you didn't explicitly target
  - Average CPC rising month over month with flat conversion rate
  - Top search terms are informational ("what is", "how to") but you want transactional
  - Competitor terms eating >20% of budget with 0 conversions
  - Single keyword consuming >40% of budget (over-concentration risk)
```

## Mine N-Grams (the search-terms report is degrading)

Atlas Part VI doctrine. Google's own help docs state the search-terms report only includes terms used by **"a significant number of people."** Everything below that threshold — and there is a long tail of it under broad match — never surfaces cleanly in the UI. The degradation bites hardest in broad-match and AI-assisted accounts, exactly where you most need to see where money goes.

The defense is **n-gram aggregation**: pull the raw search-terms data via GAQL, then aggregate clicks/cost/conversions across recurring 1-, 2-, and 3-word patterns. Build negatives from **performance data, not guesswork**.

```
CADENCE:
  Weekly       — standard accounts
  Daily        — high-spend accounts (broad match + value bidding)

N-GRAM PROCESS:
  1. Pull all search terms (last 30-90d) with clicks, cost_micros, conversions
  2. Tokenize each term into 1-word, 2-word, 3-word grams
  3. Aggregate cost_micros (÷ 1,000,000 = $) and conversions per gram
  4. Rank grams by spend with zero/low conversions
  5. Add the worst non-converting grams as negative keywords
```

> **MICROS:** the search-term/keyword stats return `cost_micros`. 1,000,000 micros = $1. Divide every `cost_micros` by 1e6 before you reason about dollars — a gram showing `cost_micros: 187000000000` is $187,000, not $187B.

Why this is non-optional — GrowthSpree's B2B Ads Waste report (43 enterprise accounts, $31.2M spend):

```
  - Average 36.1% of spend (~$11.3M) wasted on non-converting search terms
  - Waste driven mostly by unmonitored broad-match keywords
  - One generic broad keyword: 0.009% CVR across ~63,000 clicks
  - A single unmonitored broad keyword burned $187,000 over 12 months
```

### Pulling the data (READ path — `google-ads-open-cli`)

This is a READ/MEASURE operation, so it runs through the read-only CLI. The exact GAQL recipes for the search-terms view, n-gram pulls, and keyword-stats live in **`skills/google-ads/rules/gads-cli.md`** — use those queries, do not hand-roll. Shape:

```bash
# Raw search-terms pull for n-gram aggregation (READ-ONLY)
google-ads-open-cli query <customer-id> \
  "SELECT search_term_view.search_term, metrics.clicks, metrics.cost_micros, metrics.conversions \
   FROM search_term_view \
   WHERE segments.date DURING LAST_30_DAYS \
   ORDER BY metrics.cost_micros DESC" --format compact
```

Adding the resulting negatives is a **WRITE** operation — it does NOT go through the CLI. Negative-keyword creation uses the Google Ads REST API `:mutate` endpoints via curl (no first-party CLI mutates). New negative-keyword campaigns/ad-groups deploy **PAUSED by default**.

**WHITEHAT | 10/10** — N-gram waste aggregation analyzes your own account data to eliminate wasted spend; pure measurement-driven hygiene.

## Competitor Conquesting: Ethics & Execution

Atlas Part VI doctrine. Bidding on competitor terms is standard for SaaS and info products — but **how** you do it is the line between fair-use advantage and instant suspension.

### What to target

```
TARGET (comparison intent — high value):
  "[competitor] alternative"   → buyers actively evaluating a switch
  "[competitor] vs [other]"    → comparison shoppers, late funnel
  "[competitor] pricing"       → price-sensitive, ready to move

AVOID as primary (bare brand intent — low value):
  "[competitor]"  alone        → most searchers want a login/support page
                                  → high CPC, low CVR, low Quality Score
```

### Execution rules

```
1. Run conquesting in its OWN campaign (isolate budget + Quality Score drag)
2. NEVER use Dynamic Keyword Insertion (DKI) in competitor campaigns
   → auto-inserting a trademarked name into a headline = instant policy violation
3. Keep competitor trademarks OUT of ad copy entirely
4. Send traffic to an OBJECTIVE, SOURCED comparison page — not a generic lander
   → real feature/price comparison, cited claims, not "we're #1" fluff
```

Deploy path: the conquesting campaign is a **WRITE/DEPLOY** action — built via the Google Ads REST API `:mutate` endpoints via curl (the read CLI cannot create campaigns), and it launches **PAUSED by default** for review before spend.

**WHITEHAT | 9/10** — Comparison and alternative bidding is permissible under fair-use guidelines when trademarks stay out of ad copy and it runs in its own campaign.

**GRAYHAT | 5/10** — Bidding bare competitor names to intercept login or support traffic is allowed in many auctions but yields poor Quality Scores and frustrates users; watch for policy drift.

**BLACKHAT | 1/10** — Documented so you recognize it — never deploy: trademark DKI headline exploitation dynamically inserts a competitor's brand into your headline; it violates trademark policy and invites suspension.

## The AI-Era Nuance: Exact No Longer Fences Broad

Atlas Part VI doctrine. A subtlety most teams get wrong in 2026: **exact match no longer fences broad as cleanly as you assume**, especially around AI Max and AI Overviews.

Ginny Marvin clarified (reported by Search Engine Land) that:

```
  - Exact keywords do NOT serve ads in AI Overviews
  - Exact keywords no longer reliably PREVENT broad-match keywords from
    triggering in AI Overviews
```

The old mental model — "I own this query with an exact keyword, so broad won't poach it" — breaks down. Strict keyword-ownership logic matters less. What matters more now:

```
1. Negatives          — your real fence; performance-driven (see n-gram mining above)
2. Landing-page align  — relevance, not keyword tokens, governs where AI surfaces you
3. Campaign-level goal separation — keep broad-discovery and exact-control campaigns
                          structurally distinct so their goals don't blur
```

Practical consequence: stop relying on match-type hierarchy to route traffic. Route it with negatives, page alignment, and campaign separation instead.

## Bid Strategy by Keyword Type

| Keyword Type | Bid Strategy | Target CPA Multiple |
|-------------|-------------|-------------------|
| Brand (own name) | Manual CPC or Max Conversions | 0.3-0.5x target CPA |
| Brand (competitor) | Target CPA | 1.5-2x target CPA (expect higher) |
| Exact match, high intent | Target CPA | 1x target CPA |
| Phrase match, commercial | Target CPA | 1.2x target CPA |
| Broad match, discovery | Target CPA or Max Conversions | 1.5x target CPA |
| Long-tail, transactional | Manual CPC (if low volume) | 0.5-0.8x target CPA |

## Quality Score Optimization by Keyword

### Low Quality Score Diagnosis

```
QS 1-3: "Poor"
  Likely cause: Keyword is not relevant to your ad or landing page
  Fix: Create a tightly themed ad group with this keyword + relevant ad copy

QS 4-5: "Below Average"
  Likely cause: Ad copy doesn't include the keyword, or landing page is generic
  Fix: Add keyword to at least 2 headlines, create dedicated landing page

QS 6-7: "Average"
  Likely cause: Everything is okay but not optimized
  Fix: Test new ad copy with stronger CTAs, improve page load speed

QS 8-10: "Above Average"
  No action needed. Focus optimization effort on lower QS keywords.
```

### Ad Group Granularity

The key to high Quality Score is tightly themed ad groups:

```
BAD: One ad group with 50 keywords
  "learn coding", "blockchain course", "python tutorial", "web3 jobs"
  → Ad copy can't be relevant to all of these
  → Quality Score: 3-5

GOOD: Multiple ad groups with 5-10 related keywords each
  Ad Group 1: "learn coding", "coding course", "coding tutorial"
  Ad Group 2: "blockchain course", "blockchain training", "learn blockchain"
  Ad Group 3: "web3 jobs", "web3 career", "web3 developer salary"
  → Ad copy tailored to each theme
  → Quality Score: 7-9
```

## Keyword Lifecycle Management

### Monthly Keyword Audit

```
1. Pull all keywords with impressions > 0 in last 30 days
2. Sort by cost descending
3. For each keyword:
   - Conversions > 0 and CPA < target? → Keep, consider increasing bid
   - Impressions > 1000 but 0 conversions? → Pause (unless brand)
   - CPA > 2x target? → Lower bid 20% or pause
   - QS < 5? → Rewrite ads, check landing page relevance
   - Impression share < 50%? → Budget or bid limited, increase if CPA allows
4. Check for missing keywords: Search terms converting but not in account → Add them
5. Check for cannibalization: Multiple ad groups competing for same term → Consolidate
```

### Keyword Performance Tiers

```
Tier 1 (Stars): CPA < target, volume > 10 conversions/month
  Action: Maximize impression share, increase bids, expand match types

Tier 2 (Potential): CPA at target, volume 3-10 conversions/month
  Action: Maintain bids, test new ad copy to improve CVR

Tier 3 (Test): CPA 1-2x target, volume 1-3 conversions/month
  Action: Give more time, check search terms for relevance

Tier 4 (Drain): CPA > 2x target or 0 conversions after significant spend
  Action: Pause, add as negative if irrelevant terms triggered it
```
