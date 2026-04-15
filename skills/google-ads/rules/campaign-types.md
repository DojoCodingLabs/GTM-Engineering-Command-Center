# Google Ads Campaign Types -- Deep Dive

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
