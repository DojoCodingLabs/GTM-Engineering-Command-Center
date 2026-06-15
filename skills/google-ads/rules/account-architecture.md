# Google Ads Account Architecture

Architecture doctrine first (Atlas Part II), then the campaign-type reference. Structure decides whether Smart Bidding has enough signal density to optimize; everything downstream inherits the choices made here. See also `rules/smart-bidding.md` (bid strategy per pillar) and `rules/performance-max.md` (PMax containment).

> Money note: every budget below is set as `amountMicros` in the REST API (1,000,000 micros = $1). All audit reads come from the read-only CLI (`skills/google-ads/rules/gads-cli.md`); all writes go through the `:mutate` REST endpoints via curl and default to status PAUSED.

## The Death of SKAGs & the Rise of Hagakure

The Single-Keyword-Ad-Group era is over for any account on Smart Bidding. Exact is no longer exact, broad is the default, and granularity now *starves* the algorithm of conversion density instead of controlling it. Roughly 9 of 10 performance marketers favor consolidated, thematic structures. A minority (e.g. Disco Sloth) still defends SKAGs for tiny, low-data, manual-CPC accounts needing strict Quality Score and ad-copy alignment -- defensible only where chance dominates outcomes.

**Hagakure method** (Think with Google) -- the consolidated default:

| Rule | Detail |
| :---- | :---- |
| Group by landing-page theme | Ad groups organized around the destination URL, not individual keywords |
| One URL per ad group | A theme = a page; do not mix destinations in one ad group |
| Match types | Broad + phrase (let Smart Bidding find queries), fenced by aggressive negatives |
| RSA assets | Many assets per ad group so Google has combinations to test |
| Earns-its-own-ad-group threshold | A URL/theme above ~3,000 impressions/week graduates to a dedicated ad group; everything below consolidates |
| Catch-all | One DSA / AI-Max ad group to sweep low-volume URLs no keyword targets |

Operating rule (Jyll Saskin Gales): **start consolidated, split only when goal, budget, bid strategy, geography, or materially different audience intent genuinely differ.** Splitting for any other reason fragments the signal.

**WHITEHAT | 10/10** — Thematic Hagakure grouping uses Google's native consolidation to concentrate conversion data without manipulating queries.
**GRAYHAT | 4/10** — Stuffing exact + phrase + broad duplicates of the same term into one campaign "for coverage" cannibalizes budget, muddies reporting, and rarely helps.

## Brand vs Non-Brand Isolation

Atlas Law 2. Mixing brand and non-brand in one campaign lets the bidder chase cheap branded queries to satisfy a blended tROAS/tCPA -- inflating reported performance, hiding weak non-brand terms, and burning budget on traffic that would have converted organically.

The fix: a **dedicated brand campaign** (often manual CPC with strict max-bid caps so Google can't charge premium auction rates for your own name) **+ brand exclusions on every non-brand and automated campaign** (Search, PMax, Demand Gen, AI Max). A tight brand campaign commonly runs ~1,200% ROAS on ~5-7% of budget -- which is exactly why it must be reported *separately*, never smeared across the account. Apply PMax brand exclusions per `rules/performance-max.md`.

**WHITEHAT | 10/10** — Pillar-based brand separation produces transparent reporting and budget control under standard guidelines.

## The Intent Ladder (4-5 lanes)

Isolate distinct intent lanes so incompatible journeys are not force-fit into one bid target. Minimum four lanes; a fifth for SaaS. Lanes never share budget across the ladder.

| Lane | Who | Bidding posture |
| :---- | :---- | :---- |
| 1. Brand | Your own name | Manual CPC, max-bid caps, high ROAS / low CPC |
| 2. Non-brand high intent | Outcome / mechanism / evaluation queries | tCPA, phrase + broad |
| 3. Broad discovery + expansion | Queries manual research misses | Broad + Smart Bidding, fenced by aggressive negatives |
| 4. Competitor / conquest | Comparison & alternative queries | Own campaign, never shares core non-brand budget |
| 5. SaaS only: company-size / use-case clusters | SMB self-serve vs enterprise RFP behave nothing alike | Bid separately |

**Info-product analog** of the ladder: pain-aware → mechanism-aware → competitor → outcome clusters, instead of a single buy-now campaign. Not officially prescribed; this is how operators reconcile thematic consolidation with real funnel differences.

## The Five-Pillar Funnel Budget Matrix

Steady-state allocation (Atlas Part II). For new accounts use the phased version below first.

| Pillar | Budget share | Bidding & match |
| :---- | :---- | :---- |
| 1. Brand protection | 5-7% | Manual CPC, exact match |
| 2. High-intent product | 50-60% | tCPA, phrase + broad |
| 3. Competitor conquest | 15-20% | tCPA, exact + phrase |
| 4. Problem-aware | 10-15% | Maximize Conversions, broad |
| 5. Remarketing / nurture | 10% | Maximize Conversions, audience lists |

Budget shares are set as `amountMicros` on each campaign budget (a 5% pillar of a $20k/mo account = $1,000/mo = 1000000000 micros). Audit current pillar split: `google-ads-open-cli campaign-budgets <id>` and `google-ads-open-cli campaigns <id> --status ENABLED` (read-only; see `skills/google-ads/rules/gads-cli.md`).

## Benchmark Anchors

Directional sanity checks, **not** targets -- wide source variance (Atlas Appendix A). Cost values are dollars (CLI stats report `cost_micros`; divide by 1e6).

| Vertical & model | Avg CPC | Cost / lead | LP CVR | Target deeper CVR |
| :---- | :---- | :---- | :---- | :---- |
| SMB B2B SaaS (self-serve) | $3.00-5.50 | $70-100 | 3-5% | 3-5% freemium→paid |
| Mid-market B2B SaaS | $5.50-12.00 | $150-400 demo | 2.5-4.5% | 13-22% MQL→SQL |
| Enterprise B2B SaaS | $15-50+ | $800-1,300+ SQL | 1.5-3% | 16-30% opp→won |
| Low-ticket info product | $1.00-2.50 | $15-30 capture | 8-15% | 5-10% tripwire |
| High-ticket info product | $4.00-8.00 | $50-120 application | 4-8% | 15-25% call booked |

## Phased Budget

Scale in stages as conversion data stabilizes -- the inverse of running full-funnel from day one (Atlas Part XIV). Override the steady-state matrix until you reach the relevant phase.

| Phase | Monthly spend | Allocation |
| :---- | :---- | :---- |
| 1 | ≤ $10k | ~90% bottom-of-funnel Search -- capture immediate intent, establish baselines |
| 2 | $10k-30k | ~70% Search / 30% PMax; add Customer Match lists (+ Standard Shopping for physical goods) |
| 3 | $30k+ | Layer in YouTube / Demand Gen at ~15-20% for demand creation |

## Contrarian / Rep-Defiance (structural)

Reps are incentivized toward platform spend, not your efficiency. Use them for implementation details and product availability -- **not** channel mix or budget recommendations in your market (Atlas Part XV). The structural divergences:

| Google rep advice | What operators do structurally |
| :---- | :---- |
| Enable auto-apply recommendations | Turn auto-apply OFF -- it opts you into broad match / expansion that lift CPA |
| Let PMax handle branded search | Apply account-level brand exclusions so PMax chases new customers, not cheap brand demand |
| Trust optimization score | Ignore it as a performance metric -- a 50%-growth account hitting tROAS scored just 72.8% |

**WHITEHAT | 9/10** — Disabling auto-apply and aggressive brand-negativing are sustainable contrarian controls.
**WHITEHAT | 8/10** — Ignoring rep bidding/channel advice unless your CRM data agrees is a sound operator hedge.

(Bid-cap and under-bidding divergences are bidding-layer, not structural -- see `rules/smart-bidding.md`.)

---

# Campaign Types -- Deep Dive

## Search Campaigns

Search campaigns show text ads on Google Search results pages when users search for your keywords. This is the highest-intent channel in digital advertising.

### When to Use Search

- You have a product people actively search for
- You want bottom-of-funnel, high-intent traffic
- You need measurable, direct-response results
- Your target CPA allows for CPC of $1-10+ (varies by vertical)

### Search Campaign Structure

```
Search Campaign
  ├── Ad Group: [Core Feature Keywords]
  │   ├── Keywords: "learn solidity", "solidity tutorial", "blockchain course"
  │   └── RSA: Headlines mention solidity/blockchain, descriptions mention outcomes
  ├── Ad Group: [Competitor Keywords]
  │   ├── Keywords: "codecademy alternative", "[competitor] vs"
  │   └── RSA: Headlines position against competitor, descriptions highlight differentiators
  ├── Ad Group: [Problem Keywords]
  │   ├── Keywords: "how to get web3 job", "blockchain developer salary"
  │   └── RSA: Headlines address the problem, descriptions show your solution
  └── Ad Group: [Brand Keywords]
      ├── Keywords: "[your brand name]", "[brand] login", "[brand] pricing"
      └── RSA: Brand headlines, navigation-focused descriptions
```

### Responsive Search Ads (RSA)

RSAs are the only text ad format available. Provide multiple headlines and descriptions, Google tests combinations.

```
Required:
  - 3-15 headlines (30 chars each) -- aim for 8-10
  - 2-4 descriptions (90 chars each) -- aim for 4
  - Final URL
  - Display path (2 fields, 15 chars each)

Pinning rules:
  - Pin your brand or key message to position 1 to ensure it always shows
  - Pin a CTA to position 2 or 3
  - Leave remaining positions unpinned for Google to optimize
  - Never pin all positions -- defeats the purpose of RSAs
```

### RSA Headline Best Practices

```
Slot 1 (pin): Include keyword + value prop
  "Learn Solidity in 30 Days"
  "Master Smart Contract Dev"

Slot 2 (pin): Differentiator or social proof
  "4,500+ Developers Trained"
  "Project-Based Learning"

Slots 3-10 (unpinned): Mix of:
  - Features: "Hands-On Projects", "Expert Mentors"
  - Benefits: "Get Hired in Web3", "Build Real DApps"
  - Urgency: "Limited Spots Available", "Start This Week"
  - Trust: "Money-Back Guarantee", "Free Community Access"
  - Price/offer: "Start for Free", "50% Off First Month"
```

## Display Campaigns

Display campaigns show image/video ads across 3M+ websites in the Google Display Network. Lower intent than Search but massive reach and cheaper CPMs.

### When to Use Display

- Brand awareness at scale
- Retargeting website visitors
- Lookalike/similar audience prospecting
- Product launches where search volume doesn't exist yet

### Display Targeting Options

| Targeting Type | How It Works | Best For |
|---------------|--------------|----------|
| Custom Segments | Users who searched specific terms on Google | Prospecting with intent signals |
| In-Market Audiences | Users actively researching a category | Mid-funnel prospecting |
| Affinity Audiences | Users with long-term interests | Top-of-funnel awareness |
| Remarketing Lists | Your website visitors, app users, customer lists | Retargeting (highest ROAS) |
| Similar Audiences | Users similar to your remarketing lists | Scaled prospecting |
| Topics | Websites about specific topics | Contextual targeting |
| Placements | Specific websites you choose | High-control, niche reach |

### Responsive Display Ads

```
Required assets:
  - Landscape image: 1200x628 (1.91:1)
  - Square image: 1200x1200 (1:1)
  - Logo: 1200x1200 (square) + 1200x300 (landscape)
  - Headlines: up to 5 (30 chars)
  - Long headline: 1 (90 chars)
  - Descriptions: up to 5 (90 chars)
  - Business name
  - Final URL
```

## Performance Max (PMax) -- Detailed

### Asset Group Best Practices

```
Headlines (provide 10-15):
  - 5 short (< 15 chars): "Start Free", "Learn Web3", "Join 4,500+ Devs"
  - 5 medium (15-25 chars): "Master Smart Contracts", "Build Real DApps Today"
  - 5 long (25-30 chars): "Launch Your Web3 Career Now", "From Zero to Blockchain Dev"

Long Headlines (provide 5):
  - "Join 4,500+ Developers Who Learned Blockchain Development with Us"
  - "The Fastest Path from Coding Beginner to Web3 Professional"

Descriptions (provide 5):
  - Focus on outcomes, not features
  - Include numbers and social proof
  - Address objections ("No prior blockchain experience needed")
  - Include a soft CTA ("Start your free trial today")
```

### PMax Audience Signals

Audience signals are suggestions, not restrictions. Google will expand beyond them.

```json
{
  "audience_signals": [
    {
      "type": "CUSTOM_SEGMENT",
      "custom_segments": [
        {"search_terms": ["learn solidity", "blockchain developer course", "web3 bootcamp"]}
      ]
    },
    {
      "type": "IN_MARKET",
      "in_market_audiences": ["Education/Computer Programming Courses"]
    },
    {
      "type": "REMARKETING",
      "remarketing_lists": ["All Website Visitors - 90d", "Trial Users"]
    }
  ]
}
```

### PMax Brand Exclusions

PMax will bid on your branded keywords by default, cannibalizing your (cheaper) branded Search campaigns.

```
To add brand exclusions:
  1. Google Ads > Tools > Brand Lists
  2. Create a brand list with your brand terms
  3. Apply to PMax campaign settings
  4. Monitor: if branded impressions still leak through, add more variations
```

### PMax vs Search Cannibalization

```
Scenario: You run both PMax and Search campaigns
Problem: PMax steals branded traffic that Search would capture cheaper

Solution:
  1. Run branded Search campaign at all times (with exact match keywords)
  2. Add brand exclusions to PMax
  3. Compare CPA: if PMax CPA is 2x+ Search CPA for same keywords, PMax is cannibalizing
  4. Review Insights tab > Search term categories to find overlap
```

## Demand Gen Campaigns

Demand Gen replaced Discovery campaigns. Runs on YouTube (Home, Shorts, Watch Next), Discover feed, and Gmail.

### When to Use Demand Gen

- Visual products where images/video tell the story
- Younger audiences (YouTube, Discover skew younger)
- Upper-to-mid funnel awareness with engagement optimization
- Competitor to Meta's News Feed ads

### Demand Gen vs PMax

| Feature | Demand Gen | PMax |
|---------|-----------|------|
| Control | More (audience, placement) | Less (Google decides) |
| Reporting | Placement-level | Limited |
| Surfaces | YouTube, Discover, Gmail | All Google surfaces |
| Best for | Brand awareness, top-funnel | Full-funnel automation |
| Bid strategies | Max clicks, max conversions, tCPA | Max conversions, tCPA, tROAS |

## Campaign Type Decision Tree

```
Do you have conversion tracking set up?
├── No → Set it up first. No campaign type works without it.
└── Yes
    ├── Do people actively search for what you sell?
    │   ├── Yes → Start with Search (highest intent, most measurable)
    │   └── No → Start with PMax or Demand Gen (create demand)
    ├── Budget under $3,000/month?
    │   └── Focus on Search only. Spread too thin = learn nothing.
    ├── Budget $3,000-10,000/month?
    │   └── Search (60%) + PMax or Display retargeting (40%)
    └── Budget $10,000+/month?
        └── Search (40%) + PMax (30%) + Display retargeting (15%) + Demand Gen (15%)
```

## Negative Keywords

Negative keywords prevent your ads from showing on irrelevant searches. Critical for Search and PMax.

### Must-Have Negative Keywords (Every Account)

```
Account-level negatives:
  - free (unless you offer a free tier)
  - cheap, cheapest
  - torrent, pirate, crack, hack
  - job, jobs, career, hiring, salary (unless you're a job board)
  - review, reviews, reddit (often low-intent browsers)
  - [competitor name] login, [competitor] support (their customers, not yours)
  - DIY, homemade (low commercial intent)
```

### Negative Keyword Match Types

```
Broad negative: -free → blocks "free coding course", "best free tutorial"
Phrase negative: -"free trial" → blocks "free trial coding", but allows "trial free"
Exact negative: -[free coding course] → blocks only "free coding course"

Rule of thumb:
  - Use broad negatives for clearly irrelevant terms
  - Use phrase negatives for specific bad queries
  - Use exact negatives only when broad/phrase would block good traffic
```
