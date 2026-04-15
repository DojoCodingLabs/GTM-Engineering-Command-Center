---
name: gtm-seo
description: "SEO/GEO audit and content generation"
argument-hint: ""
---

# SEO/GEO Audit and Content Generation Command

You are the seo-engineer agent. You will audit the project's SEO infrastructure, perform a technical audit, analyze content gaps for high-intent keywords, generate optimized content, and save results to `.gtm/seo/`.

## Phase 1: Read Project SEO Infrastructure

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Load product context from `config.product` (name, description, landing_url, target_audience).
3. Scan the project codebase for SEO infrastructure:

### 1.1: Meta Tags and Head Management

Search for:
- `<title>` tags or `document.title` assignments
- `<meta name="description"` tags
- `<meta property="og:` Open Graph tags
- `<meta name="twitter:` Twitter Card tags
- Head management libraries: `react-helmet`, `next/head`, `@sveltejs/kit`
- Dynamic meta tag generation

### 1.2: Sitemap

Search for:
- `sitemap.xml` in `public/` or generated routes
- Sitemap generation configuration (next-sitemap, vite-plugin-sitemap)
- Dynamic sitemap generation in API routes

### 1.3: Robots.txt

Search for:
- `robots.txt` in `public/`
- Dynamic robots.txt generation
- Disallow rules that might block important pages

### 1.4: Structured Data (Schema.org)

Search for:
- `application/ld+json` script tags
- Schema.org markup in components
- JSON-LD generation utilities

### 1.5: Technical SEO

Check for:
- Server-side rendering (SSR) or static site generation (SSG)
- Client-side-only rendering (SPA without SSR -- bad for SEO)
- Canonical URL configuration
- Hreflang tags (if multilingual)
- Image alt text patterns
- Internal linking structure

### 1.6: Analytics

Check for:
- Google Search Console integration
- Google Analytics / GA4
- PostHog with UTM tracking
- Bing Webmaster Tools

Present findings:
```
SEO Infrastructure Audit:

| Component | Status | Details |
|-----------|--------|---------|
| Meta Tags | Partial | Title on 12/20 pages, description on 5/20 |
| Open Graph | Missing | No OG tags found |
| Sitemap | Present | public/sitemap.xml (static, 15 URLs) |
| Robots.txt | Present | Allows all crawlers |
| Schema.org | Missing | No structured data |
| Rendering | SSR | Next.js with SSR enabled |
| Canonical URLs | Missing | No canonical tags |
| Image Alt Text | Partial | 40% of images have alt text |
| GSC Integration | Unknown | No verification file found |
```

## Phase 2: Technical Audit

For each technical SEO factor, assess and score:

### 2.1: Core Web Vitals Assessment

Analyze the codebase for performance signals:
- Large bundle sizes (check build output or `package.json` dependencies)
- Image optimization (next/image, lazy loading, WebP/AVIF)
- Font loading strategy (font-display, preload)
- JavaScript bundle splitting
- CSS delivery (critical CSS, unused CSS)

Note: Actual CWV scores require a live site test. Provide codebase-level assessment and recommend running PageSpeed Insights on the live URL.

### 2.2: Crawlability Issues

Check for:
- JavaScript-rendered content without SSR fallback
- Orphan pages (no internal links pointing to them)
- Redirect chains
- 404 pages without proper handling
- Deep page depth (>3 clicks from homepage)

### 2.3: Indexability Issues

Check for:
- `noindex` meta tags on important pages
- Robots.txt blocking important paths
- Missing canonical URLs (duplicate content risk)
- Thin content pages (<300 words)
- Pages behind authentication (not indexable)

### 2.4: Mobile Friendliness

Check for:
- Viewport meta tag
- Responsive design (Tailwind breakpoints, media queries)
- Touch target sizes
- Mobile-specific layouts

Score each area:
```
Technical SEO Scores:

| Area | Score | Issues |
|------|-------|--------|
| Core Web Vitals (est.) | 65/100 | Large bundle, no image optimization |
| Crawlability | 80/100 | 2 orphan pages found |
| Indexability | 45/100 | No canonical URLs, 5 thin pages |
| Mobile | 90/100 | Good responsive design |
| Schema Markup | 0/100 | No structured data |
| Meta Tags | 35/100 | Missing on 60% of pages |
```

## Phase 3: Content Gap Analysis

Identify high-intent keywords the project should target but currently does not.

### 3.1: Keyword Research

Based on the product description and target audience, generate keyword clusters:

**Transactional Keywords** (high purchase intent):
- "{product_category} tool"
- "{product_category} software"
- "{product_category} platform"
- "best {product_category}"
- "{competitor} alternative"
- "{product_name} pricing"

**Informational Keywords** (awareness):
- "how to {problem_product_solves}"
- "what is {product_category}"
- "{problem} guide"
- "{product_category} tutorial"
- "{product_category} best practices"

**Comparison Keywords** (evaluation):
- "{product} vs {competitor}"
- "{product_category} comparison"
- "top {N} {product_category} tools {year}"
- "{product} review"

### 3.2: Content Inventory

Scan existing pages in the project:
- List all routes/pages
- Assess word count per page
- Identify which keywords each page targets (if any)
- Find keyword cannibalization (multiple pages targeting same keyword)

### 3.3: Gap Identification

Cross-reference keyword clusters against existing content:

```
Content Gap Analysis:

| Keyword Cluster | Search Intent | Existing Page | Gap |
|----------------|---------------|---------------|-----|
| "{product} vs {competitor}" | Comparison | None | CREATE comparison page |
| "how to {problem}" | Informational | Blog post (thin) | EXPAND to 2000+ words |
| "best {category} tools" | Transactional | None | CREATE listicle |
| "{product} pricing" | Transactional | /pricing (exists) | OPTIMIZE meta tags |
| "{category} FAQ" | Informational | None | CREATE FAQ with schema |
```

## Phase 4: Generate Content

For each identified gap, generate optimized content:

### 4.1: Comparison Pages

Generate "{Product} vs {Competitor}" pages:
- Feature comparison table
- Pricing comparison
- Use case recommendations
- FAQ section
- Schema markup (FAQPage)

### 4.2: FAQ Pages

Generate FAQ content with:
- 10-15 questions based on common user queries
- Detailed answers (150-300 words each)
- FAQPage schema markup (JSON-LD)
- Internal links to relevant product pages

### 4.3: Schema Markup

Generate JSON-LD structured data for:
- Organization schema (homepage)
- Product schema (product pages)
- FAQPage schema (FAQ pages)
- BreadcrumbList schema (all pages)
- Article schema (blog posts)
- HowTo schema (tutorial pages)

### 4.4: Meta Tag Templates

For pages missing meta tags, generate:
- Title tags (50-60 characters, keyword-rich)
- Meta descriptions (150-160 characters, with CTA)
- Open Graph tags (title, description, image)
- Twitter Card tags

### 4.5: Sitemap Updates

If the sitemap is static or incomplete:
- Generate an updated sitemap.xml including all discoverable routes
- Set appropriate `changefreq` and `priority` values
- Include `lastmod` dates

## Phase 5: Save Results

Save all outputs to `.gtm/seo/`:

### 5.1: Audit Report

Save to `.gtm/seo/audit-{YYYY-MM-DD}.md`:
```markdown
# SEO Audit Report -- {date}

## Infrastructure Status
{table from Phase 1}

## Technical Scores
{table from Phase 2}

## Content Gaps
{table from Phase 3}

## Recommendations (Priority Order)
1. {Critical fix}
2. {High-priority fix}
3. {Medium-priority fix}
...

## Generated Content
{list of generated files}
```

### 5.2: Generated Content Files

Save generated content to `.gtm/seo/content/`:
- `comparison-{competitor}.md` -- Comparison page content
- `faq.md` -- FAQ page content
- `schema-{page}.json` -- Schema markup per page
- `meta-tags.json` -- Meta tag recommendations per page
- `sitemap-updated.xml` -- Updated sitemap

### 5.3: Optionally Commit to Codebase

Ask the user: **"Apply these SEO improvements directly to the codebase? (yes/no/select)"**

If "yes" or "select":
- Add schema markup JSON-LD to relevant page components
- Update meta tags in head management
- Add/update sitemap.xml
- Add robots.txt improvements

If "no":
- Leave everything in `.gtm/seo/` for manual implementation

## Phase 6: Output

```
SEO Audit Complete -- {date}

Technical Score: {X}/100
Content Score: {X}/100
Overall SEO Health: {X}/100

Critical Issues:
- {issue 1}
- {issue 2}

Content Generated:
- {N} comparison pages
- {N} FAQ entries with schema
- {N} meta tag updates
- {N} schema markup files
- Updated sitemap.xml

Files saved: .gtm/seo/
Audit report: .gtm/seo/audit-{date}.md

Next:
- Apply changes to codebase (say "apply")
- Run /gtm-experiment to A/B test title tags
- Run /gtm-metrics to track organic traffic changes
```

## Error Handling

- **No pages found**: If the project has no indexable pages (pure SPA with no SSR), warn: "This project uses client-side rendering only. Search engines cannot crawl JavaScript-rendered content. Consider adding SSR or pre-rendering for SEO." Still generate meta tag recommendations.
- **No product URL**: If `config.product.landing_url` is not set, ask for it. Technical audit requires a live URL for some checks.
- **Large site**: If >100 pages are found, focus the content gap analysis on the top 20 highest-traffic pages and the homepage.
- **Competitor unknown**: If no competitors are specified, ask the user: "Who are your top 3 competitors? (for comparison page generation)"
- **No search tools**: If web search is unavailable for keyword research, use product context and common patterns to estimate keyword clusters. Note: "Keyword volume data unavailable without search tools. Recommendations are based on intent patterns."
