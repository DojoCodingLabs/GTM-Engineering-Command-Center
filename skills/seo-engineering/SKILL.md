---
name: seo-engineering
description: SEO engineering — technical SEO, content strategy, schema markup (JSON-LD), GEO optimization for AI citations
---

# SEO Engineering

Engineer search visibility through technical optimization, content strategy, structured data, and generative engine optimization (GEO). This skill covers the full SEO stack from crawlability to AI citation optimization.

## SEO Architecture

```
SEO System
  ├── Technical SEO (how search engines crawl and index your site)
  │   ├── Core Web Vitals (LCP, INP, CLS)
  │   ├── Crawlability (sitemap, robots.txt, internal linking)
  │   ├── Indexability (canonical URLs, noindex, hreflang)
  │   └── Site Architecture (URL structure, breadcrumbs, pagination)
  ├── Content SEO (what you publish and how it ranks)
  │   ├── Keyword Research (intent mapping, volume, difficulty)
  │   ├── Content Clusters (pillar pages + supporting articles)
  │   ├── Programmatic SEO (templated pages at scale)
  │   └── Content Freshness (update cadence, topical authority)
  ├── Schema Markup (structured data for rich results)
  │   ├── Organization, Product, FAQ, HowTo, BreadcrumbList
  │   ├── Article, Course, SoftwareApplication
  │   └── Review, AggregateRating, VideoObject
  └── GEO (Generative Engine Optimization)
      ├── AI Citation Optimization (ChatGPT, Claude, Perplexity)
      ├── Entity-first content architecture
      └── Structured knowledge format
```

## Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5-4.0s | > 4.0s |
| INP (Interaction to Next Paint) | < 200ms | 200-500ms | > 500ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1-0.25 | > 0.25 |

### Framework-Specific Optimizations

| Framework | LCP Fix | INP Fix | CLS Fix |
|-----------|---------|---------|---------|
| Next.js | Use `next/image` with priority, SSR above-fold | React Server Components, reduce client JS | Reserve space with `width`/`height` on images |
| Vite/React (SPA) | SSG/prerender critical pages, lazy load below-fold | Code split routes, defer non-critical JS | Fixed layout containers, font-display: swap |
| Astro | Static by default (good), optimize images | Minimal JS by design (good) | Use Astro Image component |

## URL Structure Best Practices

```
Good:
  /blog/how-to-learn-solidity
  /courses/blockchain-fundamentals
  /tools/smart-contract-auditor
  /pricing

Bad:
  /blog/post/12345
  /p?id=abc123
  /courses/course-detail?slug=blockchain
  /page/about-us/company/info
```

Rules:
- Lowercase, hyphens (never underscores or camelCase)
- 3-5 words max per slug
- Include primary keyword
- No dates in evergreen content URLs
- Flat hierarchy (max 3 levels deep)

## Sitemap Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-04-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/blog/learn-solidity</loc>
    <lastmod>2026-04-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

### Sitemap Rules

- Maximum 50,000 URLs per sitemap file (use sitemap index for more)
- Only include canonical URLs (no duplicates, no redirects)
- Update `lastmod` only when content actually changes
- Exclude noindex pages, paginated pages, search results
- Submit via Google Search Console and reference in robots.txt

## robots.txt Template

```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /dashboard/
Disallow: /settings/
Disallow: /admin/
Disallow: /_next/data/
Disallow: /auth/

Sitemap: https://example.com/sitemap.xml
```

## Keyword Research Framework

### Intent Classification

| Intent | Signal Words | Content Type | Conversion Potential |
|--------|-------------|-------------|---------------------|
| Informational | how to, what is, guide, tutorial | Blog posts, guides | Low (top of funnel) |
| Navigational | [brand name], login, pricing | Homepage, product pages | Medium |
| Commercial | best, vs, review, comparison, top 10 | Comparison pages, listicles | High |
| Transactional | buy, signup, free trial, discount, pricing | Landing pages, pricing | Highest |

### Content Cluster Model

```
Pillar Page: "Complete Guide to Smart Contract Development"
  ├── Cluster: "Solidity Tutorial for Beginners" → links to pillar
  ├── Cluster: "Smart Contract Security Best Practices" → links to pillar
  ├── Cluster: "Testing Smart Contracts with Hardhat" → links to pillar
  ├── Cluster: "Smart Contract Design Patterns" → links to pillar
  └── Cluster: "Deploying Smart Contracts to Mainnet" → links to pillar
```

Each cluster page links back to the pillar. The pillar links to all clusters. This creates topical authority.

## Environment Variables

```bash
GOOGLE_SEARCH_CONSOLE_SITE=https://example.com  # Verified property URL
GOOGLE_SITE_VERIFICATION=XXXXXXXXXXXX            # Meta tag verification code
```

## Measurement

### Key SEO Metrics

| Metric | Source | Frequency |
|--------|--------|-----------|
| Organic Traffic | Google Analytics / PostHog | Weekly |
| Keyword Rankings | Google Search Console | Weekly |
| Indexed Pages | Google Search Console | Monthly |
| Core Web Vitals | PageSpeed Insights API | Monthly |
| Backlink Profile | Ahrefs / Moz API | Monthly |
| AI Citation Rate | Manual checks + Perplexity | Monthly |

## Citation Science (April 2026)

Research from the SEO/GEO Atlas (7 independent passes, April 2026) reveals that AI citation is predictable and engineerable. The following 12-point checklist determines whether a page will be cited by ChatGPT, Perplexity, Google AI Overviews, or Claude.

### The 12-Point Citation Checklist

Every page targeting AI citation must pass these checks:

1. **Retrieval Rank** -- Position 0 in retrieval = 58% citation probability. Position 10 = 14%. Rank in the retrieval index is the single strongest predictor of citation. Optimize for traditional search ranking first.
2. **Title-Query Alignment** -- Pages where the title aligns with the query at 50%+ see a 2.2x citation lift. Titles must mirror the exact phrasing users (and AI fan-out queries) use.
3. **Focused Scope** -- 500-2,000 words with 7-20 subheadings. Focused pages beat "ultimate guides." AI systems prefer extractable, self-contained answers over sprawling content.
4. **The Ski Ramp** -- 44.2% of all citations come from the first 30% of a page. Front-load the highest-density, most quotable information at the top.
5. **Optimal Passage Length** -- 134-167 words per section (between H2/H3 headings). 120-180 words is the sweet spot for ChatGPT-style extraction.
6. **Definitive Language** -- Use authoritative, declarative statements. "X is the leading..." not "X might be considered..."
7. **Q&A Format** -- Question headings with direct answers in the first sentence. AI systems extract Q&A pairs with high fidelity.
8. **Entity Density** -- Target 20.6% proper noun density (named people, companies, products, technologies). Web average is 5-8%. High entity density signals factual, citable content.
9. **Balanced Tone** -- Avoid promotional or hyperbolic language. AI systems prefer neutral, authoritative content. A balanced perspective actually increases citation probability.
10. **Simpler Writing** -- Grade level 16 (Flesch-Kincaid). Academic-level clarity without unnecessary complexity. Readable but substantive.
11. **Source Citations** -- Include outbound references to authoritative sources with specific data. AI systems prefer content that itself cites sources.
12. **Freshness Signals** -- Visible datePublished and dateModified. AI systems inject "2026" into 28.1% of fan-out queries, so dated content gets filtered out.

### The Bimodal Reality

Only 15% of retrieved pages ever get cited. Citation is bimodal: pages are either always-cited or never-cited. There is almost no middle ground. Passing the 12-point checklist moves a page from the "never" category to "always."

## Platform-Specific Optimization

Each AI platform has different source biases, content preferences, and citation patterns. Optimize for the platform your audience uses most.

### ChatGPT

- **Source bias**: Wikipedia (48%), Reddit (13%), YouTube (9%)
- **Content format**: 120-180 word sections, straight H2 headings, no fancy formatting
- **Naming**: Names brands in 36% of responses
- **Strategy**: Mirror Wikipedia's neutral encyclopedic tone. Use clear H2 headings that match common queries. Keep sections self-contained and extractable.

### Google AI Overviews

- **Source bias**: YouTube (23%), Reddit (21%), established publishers
- **Content format**: Schema-dense pages, Google top-10 rank required as prerequisite
- **Strategy**: You must already rank in Google's top 10 to be eligible for AI Overviews. Add Article schema with datePublished/dateModified, FAQPage schema, and Organization schema with sameAs links.

### Perplexity

- **Source bias**: Reddit (47%), academic/white-paper format content
- **Content format**: Data tables, numbered lists, statistical citations
- **Strategy**: Write in a white-paper format with explicit data tables. Perplexity heavily favors content that looks like research. Include statistical claims with source attributions.

### Claude

- **Source bias**: Favors deep structural content, technical documentation
- **Content format**: Detailed, well-organized technical content
- **Naming**: Names brands in 46% of responses (vs ChatGPT's 36%)
- **Strategy**: Deeper structural content with clear hierarchies. Claude citations favor pages that demonstrate domain expertise through comprehensive coverage.

### The 11% Overlap Problem

Only 11% of domains are cited by BOTH ChatGPT and Google AI Overviews. Optimizing for one does not guarantee visibility on the other. Platform-specific pages or content variations may be necessary for full coverage.

## AI Crawlers and robots.txt

AI systems use two types of crawlers: **retrieval crawlers** (fetch pages to answer queries in real-time) and **training crawlers** (fetch pages to train models). The recommended strategy is to allow retrieval crawlers (they drive citations) while optionally blocking training crawlers.

### The Balanced robots.txt Configuration

```
# === AI RETRIEVAL CRAWLERS (ALLOW -- these drive citations) ===
User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Applebot-Extended
Allow: /

# === AI TRAINING CRAWLERS (OPTIONAL BLOCK -- your content, your choice) ===
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Google-Extended
Disallow: /

# === STANDARD SEARCH CRAWLERS (ALLOW) ===
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: *
Allow: /
Disallow: /api/
Disallow: /dashboard/
Disallow: /admin/
Disallow: /auth/

Sitemap: https://example.com/sitemap.xml
```

**Key distinction**: `OAI-SearchBot` (retrieval, drives citations) vs `GPTBot` (training). `Claude-SearchBot` (retrieval) vs `ClaudeBot` (training). Blocking training crawlers does NOT affect your citation visibility.

## The LATAM GEO Arbitrage

For products targeting Latin America (like DojoOS), there is a 12-24 month arbitrage window in AI-driven search.

### The Global Spanish Problem

AI models collapse all Spanish-speaking markets into a single "Global Spanish" bucket. A query about "bootcamps de programacion en Costa Rica" returns the same results as "bootcamps de programacion en Mexico" -- even though the markets, prices, regulations, and audience are completely different.

### The Hreflang Opportunity

Proper hreflang tagging (es-CR, es-MX, es-CO, es-AR) is massive arbitrage:
- Forces AI systems to recognize market-specific content
- Creates differentiated entities per country in the knowledge graph
- Extremely low competition (almost nobody in LATAM is doing GEO-specific optimization)
- Costa Rica is a Tier-3 market for AI citations -- virtually no competition

### The Window

- 12-24 months before larger competitors catch up
- First-mover advantage in LATAM GEO compounds (each citation increases future citation probability)
- 43% of non-English fan-out queries are actually in English (the "Global English Gatekeeper" effect), so English content targeting LATAM keywords also gets cited

### Implementation

1. Create country-specific landing pages with proper hreflang tags
2. Include country-specific entities (local companies, local regulations, local salary data)
3. Register the brand entity on Wikidata with country-specific claims
4. Submit to Bing Webmaster Tools (Bing powers many AI retrieval indexes)

## Knowledge Base

- `skills/seo-engineering/rules/content-strategy.md` -- Keyword research, content clusters, programmatic SEO
- `skills/seo-engineering/rules/technical-seo.md` -- Crawlability, indexability, Core Web Vitals
- `skills/seo-engineering/rules/geo-optimization.md` -- GEO patterns, AI citation optimization
- `knowledge/seo-geo-atlas-2026.md` -- SEO/GEO/AEO/LLM Visibility Atlas April 2026: Citation science, platform architecture, AI crawler configuration, LATAM GEO arbitrage, 90-day action plan. 2,221 lines from 7 independent research passes.
