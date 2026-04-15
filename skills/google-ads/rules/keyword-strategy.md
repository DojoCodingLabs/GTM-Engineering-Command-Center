# Google Ads Keyword Strategy -- Match Types, Research, and Bid Optimization

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

Target competitor brand names (legally allowed, but controversial):

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
