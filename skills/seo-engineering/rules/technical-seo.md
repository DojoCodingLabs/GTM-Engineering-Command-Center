# Technical SEO -- Crawlability, Indexability, and Performance

## Crawlability

### How Search Engines Crawl

```
Googlebot discovers pages through:
  1. Sitemap.xml (explicitly submitted list of URLs)
  2. Internal links (following links from known pages)
  3. External links (backlinks from other sites)
  4. Google Search Console URL inspection (manual submission)

Crawl budget = number of pages Google will crawl per visit.
Small sites (<10K pages): crawl budget is rarely an issue.
Large sites (>100K pages): crawl budget optimization is critical.
```

### Internal Linking Architecture

```
Good structure (flat, connected):
  Homepage (depth 0)
  ├── /courses/ (depth 1) — linked from homepage nav
  │   ├── /courses/blockchain (depth 2) — linked from /courses/
  │   ├── /courses/web3 (depth 2)
  │   └── /courses/defi (depth 2)
  ├── /blog/ (depth 1) — linked from homepage nav
  │   ├── /blog/learn-solidity (depth 2) — links to /courses/blockchain
  │   └── /blog/web3-career (depth 2) — links to /courses/web3
  └── /pricing/ (depth 1) — linked from homepage nav

Rules:
  - Every important page should be reachable within 3 clicks from homepage
  - Use descriptive anchor text (not "click here")
  - Link from high-authority pages to pages you want to rank
  - Blog posts should link to relevant product pages
  - Product pages should link to related blog posts
  - Use breadcrumbs for hierarchical navigation (also helps schema)
```

### Canonical URLs

Canonical tags tell Google which version of a duplicate page is the "original."

```html
<!-- On the page you want indexed -->
<link rel="canonical" href="https://example.com/blog/learn-solidity" />

<!-- Common duplicate scenarios to canonicalize -->
https://example.com/blog/learn-solidity
https://example.com/blog/learn-solidity/       (trailing slash)
https://example.com/blog/learn-solidity?ref=twitter  (URL parameters)
https://www.example.com/blog/learn-solidity    (www vs non-www)
http://example.com/blog/learn-solidity         (http vs https)

All should canonical to ONE version (usually https, non-www, no trailing slash, no params).
```

### noindex and nofollow

```html
<!-- noindex: don't show this page in search results -->
<meta name="robots" content="noindex" />
Use for: admin pages, search results pages, thank-you pages, staging environments

<!-- nofollow: don't follow links on this page -->
<meta name="robots" content="nofollow" />
Use for: login pages, user-generated content pages with unvetted links

<!-- Combine: don't index AND don't follow links -->
<meta name="robots" content="noindex, nofollow" />
Use for: internal tools, preview pages, authenticated-only content
```

### Redirect Rules

```
301 (Permanent): Page has permanently moved
  Old URL → New URL (passes ~90% of link equity)
  Use for: URL restructuring, domain migration, content consolidation

302 (Temporary): Page is temporarily at a different URL
  Temp URL → Original URL (passes no link equity)
  Use for: A/B tests, maintenance pages, temporary promotions

Redirect chains: A → B → C → D
  Problem: Each hop loses ~10% of link equity and slows crawling
  Fix: Always redirect directly from origin to final destination (A → D)

Redirect loops: A → B → A
  Problem: Infinite loop, page becomes inaccessible
  Fix: Audit all redirects before deployment, use redirect mapping spreadsheet
```

## Core Web Vitals Deep Dive

### LCP (Largest Contentful Paint) -- Target: < 2.5s

```
What triggers LCP:
  - <img> element
  - <video> poster image
  - Background image via url()
  - Block-level text element (h1, p, etc.)

Common LCP problems and fixes:

1. Large unoptimized images
   Fix: Use next/image or manual srcset with WebP/AVIF format
   <img src="hero.webp" srcset="hero-400.webp 400w, hero-800.webp 800w,
        hero-1200.webp 1200w" sizes="(max-width: 768px) 100vw, 50vw"
        loading="eager" fetchpriority="high" width="1200" height="628" />

2. Render-blocking CSS/JS
   Fix: Inline critical CSS, defer non-critical JS
   <link rel="preload" href="/critical.css" as="style" />
   <script defer src="/non-critical.js"></script>

3. Slow server response (TTFB > 800ms)
   Fix: CDN, server-side caching, edge rendering
   Headers: Cache-Control: public, max-age=3600, s-maxage=86400

4. Client-side rendering delay (SPA)
   Fix: SSR/SSG for landing pages, prerender critical above-fold content
   For Vite: use vite-plugin-ssr or prerender plugin
   For Next.js: use getStaticProps or generateStaticParams
```

### INP (Interaction to Next Paint) -- Target: < 200ms

```
INP measures the delay between user interaction and visual response.

Common INP problems:
1. Heavy JavaScript execution blocking main thread
   Fix: Break long tasks into smaller chunks using requestIdleCallback or setTimeout
   Fix: Use web workers for computation-heavy operations

2. Large DOM (>1,500 nodes)
   Fix: Virtualize long lists (react-virtual, tanstack-virtual)
   Fix: Lazy load off-screen content

3. Hydration blocking (React/Next.js)
   Fix: Use React.lazy and Suspense for non-critical components
   Fix: Use streaming SSR (Next.js App Router does this automatically)
```

### CLS (Cumulative Layout Shift) -- Target: < 0.1

```
CLS measures unexpected layout shifts during page load.

Common CLS causes and fixes:
1. Images without dimensions
   Fix: ALWAYS set width and height attributes on <img> tags
   <img src="hero.webp" width="1200" height="628" alt="..." />

2. Fonts causing FOUT/FOIT
   Fix: font-display: swap + preload font files
   <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin />
   @font-face { font-display: swap; }

3. Dynamic content injected above viewport
   Fix: Reserve space with min-height or aspect-ratio
   .ad-slot { min-height: 250px; }
   .hero-image { aspect-ratio: 16/9; }

4. Third-party embeds (ads, social widgets, chat)
   Fix: Use contain-intrinsic-size or min-height containers
   .chat-widget { contain-intrinsic-size: 0 400px; content-visibility: auto; }
```

## Page Speed Optimization Checklist

```
Images:
  [ ] All images in WebP or AVIF format
  [ ] Responsive srcset for multiple sizes
  [ ] Above-fold images: loading="eager" fetchpriority="high"
  [ ] Below-fold images: loading="lazy"
  [ ] Image dimensions set in HTML (width/height)

JavaScript:
  [ ] Non-critical JS deferred or lazy loaded
  [ ] Code split by route (dynamic imports)
  [ ] Third-party scripts loaded async
  [ ] No unused JavaScript (tree shaking enabled)
  [ ] Bundle size < 200KB gzipped total

CSS:
  [ ] Critical CSS inlined in <head>
  [ ] Non-critical CSS loaded asynchronously
  [ ] No unused CSS (PurgeCSS or Tailwind purge)
  [ ] CSS file < 50KB gzipped

Fonts:
  [ ] Self-hosted (no Google Fonts CDN -- adds DNS lookup)
  [ ] font-display: swap on all @font-face
  [ ] Preloaded in <head>
  [ ] Subset to used characters only (for non-Latin, custom fonts)

Server:
  [ ] CDN for static assets
  [ ] Gzip or Brotli compression enabled
  [ ] HTTP/2 or HTTP/3 enabled
  [ ] Cache-Control headers set correctly
  [ ] TTFB < 800ms globally, < 200ms from CDN edge
```

## Hreflang for Multi-Language Sites

```html
<!-- On the Spanish version of a page -->
<link rel="alternate" hreflang="es" href="https://example.com/es/blog/aprender-solidity" />
<link rel="alternate" hreflang="en" href="https://example.com/blog/learn-solidity" />
<link rel="alternate" hreflang="x-default" href="https://example.com/blog/learn-solidity" />

Rules:
  - Every page must reference ALL language versions (including itself)
  - x-default = fallback for unmatched languages
  - Use ISO 639-1 language codes (es, en, pt) optionally with region (es-CO, pt-BR)
  - Hreflang tags must be reciprocal (page A references B, B must reference A)
```

## Structured Data Validation

```
Tools:
  1. Google Rich Results Test: https://search.google.com/test/rich-results
     - Tests specific URLs for valid schema markup
     - Shows which rich results are eligible

  2. Schema.org Validator: https://validator.schema.org/
     - General JSON-LD validation

  3. Google Search Console > Enhancements
     - Shows schema errors across your entire site
     - Alerts on new issues
```

## AI Crawler Readiness

AI retrieval crawlers (OAI-SearchBot, Claude-SearchBot, PerplexityBot) behave differently from traditional search crawlers. Most critically: **they do not execute JavaScript**.

### SSR Is Table Stakes

```
AI crawler rendering capabilities:

| Crawler | Executes JS? | Follows redirects? | Reads robots.txt? |
|---------|-------------|-------------------|-------------------|
| Googlebot | Yes (headless Chrome) | Yes | Yes |
| OAI-SearchBot | No | Yes | Yes |
| Claude-SearchBot | No | Yes | Yes |
| PerplexityBot | No | Limited | Yes |
| Bingbot | Partially | Yes | Yes |

Implication:
  - SPA-only sites (React/Vue without SSR) are INVISIBLE to AI retrieval crawlers
  - Content rendered only via client-side JavaScript will never be cited by AI
  - SSR or SSG is mandatory for any page targeting AI citations
  - Even hybrid apps must ensure SEO-critical pages render on the server
```

### TTFB Requirements

AI crawlers have aggressive timeout thresholds. If your server does not respond quickly, the crawler abandons the request and moves to the next candidate:

```
TTFB targets for AI crawler compatibility:

| Threshold | Result |
|-----------|--------|
| < 400ms | Optimal -- all crawlers will wait |
| 400-500ms | Borderline -- some crawlers may abandon |
| > 500ms | Likely abandoned by AI retrieval crawlers |
| > 800ms | Problematic even for traditional search crawlers |

How to achieve < 400ms TTFB:
  1. CDN with edge caching for static/SSG pages
  2. Server-side caching (Redis, Varnish) for SSR pages
  3. Database query optimization (indexes, connection pooling)
  4. Edge rendering (Vercel Edge, Cloudflare Workers)
  5. Prerender and cache pages that AI crawlers hit most
```

### What AI Crawlers Cannot See

```
Invisible to AI retrieval:
  - Content behind authentication (login walls)
  - Content behind paywalls
  - Content loaded via client-side JavaScript after page load
  - Content inside iframes from different origins
  - Content in images/PDFs (unless also present as HTML text)
  - Content injected by browser extensions or client-side scripts
  - Lazy-loaded content below the fold (some crawlers only read initial HTML)

Visible to AI retrieval:
  - Server-rendered HTML (SSR/SSG)
  - Static HTML files
  - Content in the initial HTML response
  - Text content in semantic HTML elements (p, h1-h6, li, td, blockquote)
  - Schema markup in JSON-LD script tags
  - Meta tags in the document head
```

## The Balanced robots.txt

The traditional robots.txt is no longer sufficient. AI crawlers come in two categories, and they require different treatment:

### Retrieval vs Training Crawlers

```
RETRIEVAL CRAWLERS (allow -- these drive citations):
  OAI-SearchBot     -- OpenAI's search crawler (powers ChatGPT browse)
  ChatGPT-User      -- ChatGPT browsing on behalf of a user
  Claude-SearchBot   -- Anthropic's search retrieval crawler
  PerplexityBot     -- Perplexity's retrieval crawler
  Applebot-Extended -- Apple Intelligence retrieval
  Bingbot           -- Bing (powers Copilot's retrieval index)

TRAINING CRAWLERS (optional block -- content scraping for model training):
  GPTBot            -- OpenAI's training data crawler
  ClaudeBot         -- Anthropic's training data crawler
  CCBot             -- Common Crawl (used by many AI training sets)
  Google-Extended   -- Google's AI training crawler
  Bytespider        -- ByteDance/TikTok training crawler
```

### Recommended Configuration

```
# === AI RETRIEVAL CRAWLERS (ALLOW) ===
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

# === AI TRAINING CRAWLERS (BLOCK) ===
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Bytespider
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

**Critical**: Blocking `GPTBot` does NOT block `OAI-SearchBot`. They are separate crawlers. You can block training while allowing retrieval.

## IndexNow

IndexNow is an instant URL notification protocol supported by Bing, Yandex, and several AI retrieval indexes. Instead of waiting for crawlers to discover your updated pages, you push a notification that tells them "this URL has changed."

### Why It Matters for AI Visibility

```
Traditional crawl discovery:
  Page updated → Wait 1-7 days → Crawler discovers change → Re-indexes → Available for retrieval

With IndexNow:
  Page updated → Instant notification → Re-indexed within minutes → Available for retrieval

For AI citations, speed matters because:
  1. AI systems inject "2026" into 28.1% of queries (freshness is a signal)
  2. Faster re-indexing = faster citation eligibility after content refresh
  3. Bing powers many AI retrieval indexes (Copilot, ChatGPT via Bing)
```

### Implementation

```bash
# 1. Generate an IndexNow API key (any random string, 8-128 hex chars)
# 2. Place the key file at your site root: https://example.com/{key}.txt
# 3. The file content should be the key itself

# 4. Submit URL updates via HTTP GET or POST:
curl "https://api.indexnow.org/IndexNow?url=https://example.com/updated-page&key=YOUR_KEY"

# 5. For batch updates (POST):
curl -X POST "https://api.indexnow.org/IndexNow" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "example.com",
    "key": "YOUR_KEY",
    "urlList": [
      "https://example.com/page-1",
      "https://example.com/page-2",
      "https://example.com/page-3"
    ]
  }'
```

### When to Trigger IndexNow

- After publishing a new page
- After updating an existing page (content refresh)
- After changing meta tags, schema markup, or page structure
- After fixing broken pages or resolving 404 errors
- Integrate into your CI/CD pipeline for automatic submission on deploy

## Schema for AI Citation

Schema markup helps AI systems understand your content's structure and authority. While traditional SEO uses schema for rich results, AI citation requires specific schema patterns:

### Required Schema Types

**Article (on every content page):**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Page Title That Matches Target Query",
  "datePublished": "2026-04-14T00:00:00Z",
  "dateModified": "2026-04-14T00:00:00Z",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://example.com/team/author"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Brand Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  }
}
```

**FAQPage (on pages with Q&A content):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question phrased as user would ask it?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Direct answer in 40-60 words for featured snippet, then expanded context."
      }
    }
  ]
}
```

**Organization (on homepage, with sameAs for knowledge graph):**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Brand Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://twitter.com/brand",
    "https://github.com/brand",
    "https://linkedin.com/company/brand",
    "https://www.wikidata.org/wiki/QXXXXXXX",
    "https://www.crunchbase.com/organization/brand"
  ]
}
```

**Product/Offer (on pricing and product pages):**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Clear product description",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
```

### Schema Rules for AI

1. **datePublished and dateModified are mandatory** -- AI systems use these as freshness signals
2. **sameAs links on Organization connect your brand to the knowledge graph** -- Include Wikidata, Crunchbase, social profiles
3. **author information builds topical authority** -- Link to author pages with their credentials
4. **FAQPage schema gets extracted with high fidelity** -- AI systems love structured Q&A
5. **Keep schema accurate** -- Outdated or inaccurate schema erodes trust in the retrieval index
