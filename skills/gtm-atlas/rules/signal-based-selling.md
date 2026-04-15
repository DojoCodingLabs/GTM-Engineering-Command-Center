# Signal-Based Selling

## Core Principle

Instead of spray-and-pray outreach, monitor buying signals and engage prospects at the moment of highest intent. Signal-based selling converts 5-10x better than cold outreach because you reach people who already have the problem AND the budget/authority to solve it.

## Signal Categories and Workflows

### Funding Signals

**What:** Company raised a round, received a grant, or announced revenue milestone.
**Why it matters:** They have budget. Post-funding, companies invest in tools and hires aggressively for 6-12 months.

**Sources:**
- Crunchbase (API or RSS feed for target categories)
- PitchBook (for larger rounds)
- TechCrunch / local LATAM tech news (manual but high quality)
- LinkedIn posts from founders announcing raises

**Clay Workflow:**
```
Trigger: New funding round in target sector
  → Enrich: Get founder/CTO email + LinkedIn via Apollo
  → Filter: Series Seed-B only (earlier = no budget, later = locked in)
  → Score: +30 for funding, +20 if sector match, +10 if LATAM
  → Route: Score >50 → personal email sequence
           Score 30-50 → LinkedIn connection + message
           Score <30 → add to newsletter audience
```

**Outreach template:**
```
Subject: Congrats on the round, [Name]

Saw the news about [Company]'s [round size] raise. Congrats -- 
[specific thing about what they're building] is exactly what 
[market] needs right now.

Quick question: as you scale the team post-raise, how are you 
handling [specific problem your product solves]?

We help companies like [similar company] [specific result]. 
Happy to share what's worked for them if useful.

[Your name]
```

### Hiring Signals

**What:** Company posted a job for a role that your product replaces or supports.
**Why it matters:** If they're hiring a "Growth Marketing Manager," they have a growth problem. If they're hiring a "DevOps Engineer," they have an infrastructure problem. Your product might solve the problem faster than a hire.

**Sources:**
- LinkedIn Jobs API (via Clay or custom scraper)
- Indeed/Glassdoor RSS feeds for specific job titles
- Company career pages (monitor with Visualping or custom scraper)
- AngelList/Wellfound for startup roles

**Clay Workflow:**
```
Trigger: Job posting matches keywords (e.g., "DevOps", "Platform Engineer")
  → Enrich: Get hiring manager or CTO contact info
  → Filter: Company size 20-500 (too small = no budget, too large = bureaucracy)
  → Score: +25 for job match, +15 if urgency language ("immediately", "ASAP")
  → Route: Personal outreach within 48 hours of posting
```

**Outreach template:**
```
Subject: Re: Your [Job Title] opening

[Name], I noticed [Company] is hiring a [Job Title]. That's 
usually a sign that [pain point the role addresses] is becoming 
a bottleneck.

What if you could solve that problem before you even fill the 
position? [Product] does [specific thing the hire would do], 
and our customers typically see results within [timeframe].

Would it make sense to chat for 15 minutes this week? Even if 
you still hire for the role, [Product] makes them 3x more effective 
from day one.
```

### Tech Stack Signals

**What:** Company adopted a technology that's complementary to yours or a competitor.
**Why it matters:** If they just adopted Stripe, they're processing payments. If they just adopted HubSpot, they're investing in marketing. Their tech choices reveal their priorities.

**Sources:**
- BuiltWith (technology adoption tracking)
- Wappalyzer (browser extension data)
- G2 reviews (companies reviewing competitors)
- GitHub repos (public code reveals stack choices)

**Clay Workflow:**
```
Trigger: Company adopted [complementary technology]
  → Enrich: Get decision-maker contact (VP Eng, CTO, Head of Product)
  → Filter: Adoption date within last 90 days (they're still implementing)
  → Score: +20 for complementary tech, +30 for competitor adoption
  → Route: Personalized outreach referencing the specific integration
```

### Content Signals

**What:** Prospect engaged with problem-related content -- searched keywords, read competitor comparisons, attended a webinar.
**Why it matters:** They're actively researching solutions. This is mid-funnel intent.

**Sources:**
- Google Search Console (keywords driving traffic to your site)
- Bombora / 6sense (B2B intent data platforms)
- PostHog (track which pages they visit, what they search on your site)
- Social media monitoring (mentions of problem keywords on LinkedIn/Twitter)
- G2 / Capterra (buyers comparing products in your category)

**Workflow:**
```
Trigger: Prospect viewed pricing page + 2 blog posts in 7 days
  → Internal: Flag as high-intent in CRM
  → Action: Personalized email within 24 hours
  → If no response in 3 days: LinkedIn connection request
  → If still no response: Retargeting ad with case study
```

### Social Signals

**What:** Prospect posted about their problem on social media, complained about a competitor, or asked for recommendations.
**Why it matters:** Active pain, publicly expressed. Highest-intent signal.

**Sources:**
- LinkedIn keyword monitoring (set up saved searches for problem-related terms)
- Twitter/X search for problem keywords
- Reddit monitoring for relevant subreddits
- Facebook/Slack groups in your vertical

**Response protocol:**
1. Engage genuinely first (comment with value, not a pitch)
2. If they respond positively, DM with a relevant resource (not a sales pitch)
3. If they engage with the resource, offer a conversation
4. Never pitch in public comments -- it destroys credibility

### Trigger Events

**What:** Organizational changes that create buying windows -- new leadership, expansion, regulation changes, competitor acquisition.
**Why it matters:** Change creates urgency. New leaders want quick wins. Expansion requires new tools. Regulations force compliance purchases.

**Sources:**
- LinkedIn alerts for leadership changes at target accounts
- Google Alerts for company news
- Industry news for regulatory changes
- Crunchbase for M&A activity

**Timing:** Reach out within 2 weeks of the trigger event. After 30 days, the window closes as they've either found a solution or deprioritized.

## Lead Scoring Model

Combine signals for a composite score:

```
Signal Score = Sum of:
  Funding signal:    +30 points
  Hiring signal:     +25 points
  Tech stack signal: +20 points
  Content signal:    +15 points
  Social signal:     +35 points (highest intent)
  Trigger event:     +20 points

ICP Fit Score = Sum of:
  Company size match:    +15 points
  Industry match:        +15 points
  Geography match:       +10 points
  Role/title match:      +10 points

Total Score = Signal Score + ICP Fit Score

Routing:
  80-100: Immediate personal outreach (within 24 hours)
  50-79:  Automated but personalized email sequence
  30-49:  Add to retargeting + newsletter
  0-29:   Monitor only, don't reach out
```

## Tool Stack

| Tool | Purpose | Cost (approx) |
|------|---------|---------------|
| Clay | Signal orchestration, enrichment waterfall | $150-500/mo |
| Apollo | Email/phone enrichment, sequences | $50-400/mo |
| Phantombuster | LinkedIn scraping, social automation | $50-200/mo |
| BuiltWith | Tech stack detection | $300-500/mo |
| LinkedIn Sales Navigator | Contact discovery, saved searches | $100/mo |
| Crunchbase | Funding data | $50-350/mo |
| Google Alerts | News monitoring | Free |
| PostHog | Website visitor tracking | Free-$450/mo |

For early-stage: Clay + Apollo + Google Alerts covers 80% of signal detection for under $300/month.
