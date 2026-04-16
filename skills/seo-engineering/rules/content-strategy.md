# SEO Content Strategy -- Keyword Research, Content Clusters, and Programmatic SEO

## Keyword Research Process

### Step 1: Seed Topic Discovery

Start with your product's core value propositions and expand:

```
Product: Coding bootcamp for Web3/blockchain developers

Core topics:
  - Learn Solidity
  - Smart contract development
  - Blockchain developer career
  - Web3 bootcamp
  - DeFi development
  - NFT programming

Adjacent topics (bring in wider audience):
  - Career change to tech
  - Remote developer jobs
  - Learn to code (general)
  - Cryptocurrency fundamentals
  - Startup technical co-founder
```

### Step 2: Keyword Qualification Matrix

For each keyword, evaluate on 4 axes:

| Axis | Score 1 (Poor) | Score 3 (Okay) | Score 5 (Excellent) |
|------|---------------|----------------|-------------------|
| Volume | <50 searches/month | 100-1,000/month | >1,000/month |
| Difficulty | DR 80+ (first page is Wikipedia, major brands) | DR 40-60 | DR <40 (achievable) |
| Intent Match | Informational only, no purchase intent | Mixed intent | Transactional or high commercial |
| Business Relevance | Tangentially related | Related to product category | Directly about your product/need |

Priority: Keywords scoring 12+ (out of 20) are worth pursuing.

### Step 3: Intent Mapping

```
For each qualified keyword, classify intent and assign content type:

"learn solidity" → Informational → Tutorial/Guide (blog)
"best blockchain bootcamp" → Commercial → Comparison page (blog/landing)
"solidity developer salary" → Informational → Data-driven article (blog)
"web3 bootcamp pricing" → Transactional → Pricing page
"dojo coding vs codecademy" → Commercial → Comparison landing page
"enroll blockchain course" → Transactional → Product page / checkout

Rule: Match content type to intent. Don't write a blog post for a transactional keyword.
Don't create a landing page for an informational keyword.
```

## Content Cluster Architecture

### The Hub-and-Spoke Model

```
Pillar Page (Hub): "The Complete Guide to Smart Contract Development" (3,000-5,000 words)
  │
  ├── Spoke 1: "Solidity Tutorial for Beginners" (1,500-2,500 words)
  │   └── Links to pillar, links to spokes 2,3
  ├── Spoke 2: "Smart Contract Security Best Practices" (1,500-2,500 words)
  │   └── Links to pillar, links to spokes 1,4
  ├── Spoke 3: "Testing Smart Contracts with Hardhat" (1,500-2,500 words)
  │   └── Links to pillar, links to spokes 1,5
  ├── Spoke 4: "Smart Contract Audit Checklist" (1,500-2,500 words)
  │   └── Links to pillar, links to spokes 2,5
  └── Spoke 5: "Deploying Smart Contracts to Ethereum Mainnet" (1,500-2,500 words)
      └── Links to pillar, links to spokes 3,4

Linking rules:
  - Every spoke links to the pillar (in the first 200 words)
  - The pillar links to every spoke (table of contents or inline)
  - Spokes link to 2-3 other spokes (related content only)
  - External links: 2-3 per article to authoritative sources
```

### Cluster Planning Template

```
CLUSTER: [Topic]
PILLAR: [Pillar page title] — [Target keyword] — [Search volume] — [Difficulty]

SPOKES:
  1. [Title] — [Target keyword] — [Volume] — [Difficulty] — [Word count] — [Status]
  2. [Title] — [Target keyword] — [Volume] — [Difficulty] — [Word count] — [Status]
  3. [Title] — [Target keyword] — [Volume] — [Difficulty] — [Word count] — [Status]
  ...

INTERNAL LINKS:
  Pillar → Spokes 1-N (all)
  Spoke 1 → Pillar + Spokes 2,3
  Spoke 2 → Pillar + Spokes 1,4
  ...

EXTERNAL LINKS:
  Pillar → [Authoritative source 1], [Authoritative source 2]

CONVERSION PATH:
  Spoke (informational) → Pillar (educational) → Product page (transactional)
```

## Content Production Standards

### Article Structure

```
Every SEO article must include:

1. Title (H1): Contains primary keyword, 50-60 characters
2. Meta description: 150-160 characters, includes keyword, has CTA
3. Introduction (100-200 words):
   - Hook: surprising fact, question, or pain point
   - Promise: what the reader will learn/achieve
   - Credibility: why you're qualified to write this
4. Table of contents: For articles >1,500 words
5. Body sections (H2/H3):
   - Each H2 targets a secondary keyword or addresses a key question
   - Include at least one image, table, or code block per major section
   - Paragraphs: 2-4 sentences max (scannability)
6. Conclusion: Summarize key takeaways + CTA
7. FAQ section: 3-5 questions in FAQ schema format
```

### Content Freshness Strategy

```
Evergreen content (courses, tutorials, guides):
  - Review and update every 6 months
  - Update the publication date only when substantial changes are made
  - Don't update for minor grammar fixes (Google can tell)

Time-sensitive content (industry reports, comparisons, salary data):
  - Update quarterly or when significant changes occur
  - Always include the year in the title: "Best Web3 Bootcamps (2026)"
  - Set a calendar reminder to update

Signal to Google that content is fresh:
  - Update <lastmod> in sitemap when content changes
  - Change the meta description
  - Add new sections or data points
  - Update internal links to newer related content
```

## Programmatic SEO

### What It Is

Programmatic SEO generates pages at scale from structured data. Instead of writing 500 individual pages, you create a template and populate it with data.

### Pattern 1: Location Pages

```
Template: "[Service] in [City] -- [Brand]"
Data source: list of 200 cities

Generated pages:
  /web3-bootcamp/bogota → "Web3 Bootcamp in Bogota -- Dojo Coding"
  /web3-bootcamp/medellin → "Web3 Bootcamp in Medellin -- Dojo Coding"
  /web3-bootcamp/mexico-city → "Web3 Bootcamp in Mexico City -- Dojo Coding"

Each page includes:
  - City-specific intro (generated or handwritten for top 20 cities)
  - Local job market data (from API or database)
  - Testimonials from students in that city
  - Local events or meetups
  - Shared product features section
```

### Pattern 2: Comparison Pages

```
Template: "[Product] vs [Competitor] -- Honest Comparison [Year]"
Data source: list of 20 competitors

Generated pages:
  /compare/dojo-vs-codecademy → "Dojo Coding vs Codecademy -- Honest Comparison 2026"
  /compare/dojo-vs-udemy → "Dojo Coding vs Udemy -- Honest Comparison 2026"

Each page includes:
  - Feature comparison table (from structured data)
  - Pricing comparison
  - Unique strengths of each platform (handwritten)
  - Who should choose which
  - Student testimonials comparing the two
```

### Pattern 3: Tool/Resource Pages

```
Template: "[Topic] [Resource Type] -- Free [Tool/Calculator/Template]"
Data source: tools database

Generated pages:
  /tools/solidity-gas-calculator → "Solidity Gas Calculator -- Free Tool"
  /tools/smart-contract-generator → "Smart Contract Generator -- Free Template"

These pages:
  - Provide genuine utility (not thin content)
  - Capture email addresses ("Get results emailed to you")
  - Link to related paid content
  - Build backlinks naturally (people link to useful tools)
```

### Programmatic SEO Quality Rules

```
DO:
  - Ensure each page has unique, valuable content (not just city name swapped)
  - Add at least 300-500 words of unique content per page
  - Include unique data points (local stats, reviews, market data)
  - Interlink programmatic pages with editorial content
  - Noindex pages with thin or duplicate content until improved

DON'T:
  - Generate thousands of pages with only the city/keyword name changed
  - Use AI-generated content without human review and enrichment
  - Create pages for keywords with 0 search volume
  - Forget to add pages to sitemap
  - Skip canonical tags (programmatic pages are prone to duplication)
```

## Content Calendar

### Monthly Production Cadence

```
Week 1: Research + Planning
  - Pull keyword data for next month's topics
  - Update content cluster map
  - Assign topics to writers

Week 2-3: Production
  - Draft articles (aim for 2-4 per month for small teams)
  - Include original images, screenshots, or data visualizations
  - Internal link planning

Week 4: Publishing + Distribution
  - Publish with proper schema, meta tags, and internal links
  - Share on social channels
  - Add to email newsletter
  - Submit to Google Search Console for indexing

Ongoing:
  - Monitor rankings weekly (Google Search Console)
  - Update top-performing content monthly
  - Identify content gaps from competitor analysis quarterly
```

## Citation-Grade Content Engineering

The SEO/GEO Atlas (April 2026) identifies 12 content characteristics that predict whether a page will be cited by AI systems. Apply this checklist to every page targeting AI visibility.

### The 12-Point Checklist

```
For every page targeting AI citation, verify:

1. [ ] RETRIEVAL RANK -- Page ranks in top 10 for its primary query
       (Position 0 = 58% citation probability, position 10 = 14%)

2. [ ] TITLE-QUERY ALIGNMENT -- Title mirrors the exact phrasing of target queries
       (50%+ alignment = 2.2x citation lift)

3. [ ] FOCUSED SCOPE -- 500-2,000 words with 7-20 subheadings
       (Focused pages beat "ultimate guides" for AI citation)

4. [ ] SKI RAMP -- First 30% of page contains highest-density information
       (44.2% of citations come from first 30% of content)

5. [ ] PASSAGE LENGTH -- 134-167 words per section between H2/H3 headings
       (120-180 word sweet spot for ChatGPT-style extraction)

6. [ ] DEFINITIVE LANGUAGE -- Uses authoritative, declarative statements
       ("X is the leading..." not "X might be considered...")

7. [ ] Q&A FORMAT -- Question headings with direct answers in first sentence
       (AI systems extract Q&A pairs with highest fidelity)

8. [ ] ENTITY DENSITY -- 20.6% proper noun density (named people, companies, products)
       (Web average is 5-8%; high entity density = citable content)

9. [ ] BALANCED TONE -- Neutral, authoritative, not promotional
       (AI systems down-rank hyperbolic or salesy content)

10. [ ] READABILITY -- Grade level ~16 (Flesch-Kincaid)
        (Academic clarity without unnecessary complexity)

11. [ ] SOURCE CITATIONS -- Outbound references to authoritative sources with data
        (AI systems prefer content that itself cites sources)

12. [ ] FRESHNESS SIGNALS -- Visible datePublished and dateModified
        (28.1% of fan-out queries auto-inject "2026")
```

### Applying the Checklist

- Score each page 0-12 (one point per passing criterion)
- Pages scoring 9+ are in the "always-cited" category
- Pages scoring 6-8 need targeted improvements
- Pages scoring below 6 need structural rewrites
- Only 15% of retrieved pages ever get cited -- the checklist is what separates the 15% from the 85%

## The Ski Ramp Rule

Research shows 44.2% of all AI citations come from the first 30% of a page's content. This means the opening section of any page is disproportionately important for AI visibility.

### How to Front-Load

```
Page structure for citation optimization:

FIRST 30% (the "Ski Ramp" -- where 44.2% of citations come from):
  1. Definitive opening statement (1-2 sentences answering the core query)
  2. Key facts / data points (the most quotable numbers)
  3. Comparison table or summary table (if applicable)
  4. TL;DR or "Key Takeaways" section with 3-5 bullet points

MIDDLE 40% (supporting depth):
  5. Detailed breakdown by subtopic (H2 sections)
  6. Evidence, examples, case studies
  7. Step-by-step processes (if applicable)

FINAL 30% (context and discovery):
  8. FAQ section (Q&A format with schema)
  9. Related topics and internal links
  10. Methodology, sources, update history
```

### Anti-Patterns

- **Burying the lede**: Starting with background history instead of the answer
- **Long introductions**: 300+ word intros before the substantive content begins
- **Saving the best for last**: Putting the most interesting data at the bottom
- **Progressive disclosure**: Forcing users to read sequentially to reach the key insight

## Optimal Passage Structure

AI retrieval systems extract content in passages (chunks between headings). Research shows optimal passage length varies by platform:

### Length Targets

| Context | Optimal Length | Why |
|---------|---------------|-----|
| Between H2 headings | 120-180 words | ChatGPT extraction window |
| Between H3 headings | 134-167 words | Highest citation probability zone |
| FAQ answers | 40-60 words (featured snippet) + 100-150 words (expanded) | Two-tier: snippet + depth |
| Comparison table cells | 15-30 words per cell | Structured extraction |
| Opening definition | 1-2 sentences (25-50 words) | Direct answer extraction |

### Section Structure Template

```markdown
## [Question or Topic as H2]

[Direct answer in 1-2 sentences -- the "quotable statement." 25-50 words.]

[Supporting context paragraph. Include one specific data point or named entity.
Expand on the answer with evidence or nuance. 50-70 words.]

[Practical application paragraph. Connect to the reader's situation. Include
a specific example, recommendation, or next step. 40-60 words.]

Total: ~134-167 words between this H2 and the next.
```

### What NOT to Do

- Sections over 300 words between headings (too long for extraction)
- Sections under 50 words between headings (too thin, looks low-quality)
- Multiple topics crammed into one section (breaks topical coherence)
- Sections that are just lists without any prose (AI needs context around data)

## Entity Density

AI systems determine content authority partly through entity density -- the ratio of named entities (proper nouns) to total content.

### Target: 20.6% Entity Density

The web average is 5-8% proper noun density. Pages cited by AI systems average 20.6%. This means approximately 1 in 5 words should be a named entity:

```
Low entity density (5%):
"The platform helps users learn to code. It has various courses
and features that make learning easier. Users can track their progress."

High entity density (20%+):
"Dojo Coding's Pathways module uses Supabase for real-time progress
tracking. Students in Costa Rica and Mexico complete Solidity and
TypeScript courses, with certifications verified on Ethereum."
```

### Entity Types to Include

- **People**: Founders, instructors, industry experts
- **Companies**: Your brand, competitors, partners, clients
- **Products**: Specific product names, features, technologies
- **Technologies**: Programming languages, frameworks, protocols
- **Places**: Cities, countries, regions (especially for LATAM targeting)
- **Institutions**: Universities, organizations, regulatory bodies
- **Events**: Conferences, launches, industry milestones

### How to Increase Entity Density

1. Replace generic terms with specific names ("a coding platform" -> "Dojo Coding")
2. Include competitor names in comparison content
3. Reference specific technologies by name (not "a database" but "Supabase" or "PostgreSQL")
4. Add geographic entities for local targeting
5. Cite specific sources by name ("according to a16z's State of Crypto 2026 report")

## Content Refresh Cadence

AI systems weight freshness heavily. 28.1% of fan-out queries auto-inject the current year. Stale content loses citation eligibility rapidly.

### Refresh Tiers

| Content Type | Refresh Cycle | What to Update |
|-------------|---------------|----------------|
| Comparison pages ("X vs Y") | Every 30 days | Pricing, features, latest version, date in title |
| "Best of" listicles | Every 30 days | Rankings, new entries, remove defunct products |
| Data/statistics pages | Every 30 days | Latest numbers, source dates, trend lines |
| Tutorial/how-to guides | Every 90 days | Version numbers, deprecated methods, new approaches |
| Evergreen definitions | Every 180 days | Relevance check, new examples, related terms |
| Company/product pages | Every 90 days | Updated metrics, new features, team changes |

### What a "Refresh" Includes

```
Minimum viable refresh (15 minutes per page):
  1. Update dateModified in schema markup and visible on page
  2. Update the year in the title (if applicable)
  3. Verify all external links still work
  4. Add 1-2 new data points or examples
  5. Remove any outdated information

Full refresh (1-2 hours per page):
  1. Everything in minimum refresh, plus:
  2. Rewrite the opening 30% (ski ramp) with latest data
  3. Add a new section addressing recent developments
  4. Update comparison tables with current pricing/features
  5. Re-run through the 12-point citation checklist
  6. Check citation performance across 4 AI platforms
```

### Automation

- Set calendar reminders for top 10 pages on 30-day cycles
- Use a content inventory spreadsheet tracking last refresh date per page
- Monitor AI citation drops as a trigger for unscheduled refreshes
- Automate dateModified updates in your CMS or build system
