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
