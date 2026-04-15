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
