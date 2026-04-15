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
