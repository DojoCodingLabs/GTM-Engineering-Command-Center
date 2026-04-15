# Integration Mapping -- How Detected Stack Maps to GTM Capabilities

## The Capability Matrix

Every detected integration enables specific GTM capabilities. This file maps integrations to actionable GTM operations.

## Capability Categories

```
1. Revenue Intelligence — Can we track and analyze revenue?
2. User Behavior — Can we track what users do in the product?
3. Funnel Analysis — Can we build and measure conversion funnels?
4. Ad Platform Integration — Can we track ad conversions and build audiences?
5. Email Automation — Can we send drip sequences and lifecycle emails?
6. SEO Readiness — Can the site rank in search engines?
7. A/B Testing — Can we run experiments?
8. Session Recording — Can we watch user sessions?
```

## Integration to Capability Map

### Stripe → Revenue Intelligence

```
Capabilities unlocked:
  [x] MRR calculation (subscriptions API)
  [x] MRR growth components (new, expansion, contraction, churn)
  [x] Cohort revenue analysis (by signup month)
  [x] LTV calculation (ARPU / churn rate)
  [x] LTV:CAC ratio (with ad spend data)
  [x] Trial-to-paid conversion tracking (subscription events)
  [x] Churn analysis (voluntary vs involuntary)
  [x] Payment failure monitoring (invoice.payment_failed webhook)
  [x] Revenue by plan/product
  [x] Customer count and growth

Data extraction:
  - Subscriptions list API → active MRR
  - Invoices API → historical revenue
  - Customer API → cohort assignment
  - Webhook events → real-time updates

Missing without Stripe:
  - No automated revenue tracking
  - Manual spreadsheet-based MRR calculation
  - Cannot compute LTV:CAC automatically
```

### PostHog → User Behavior + Funnel Analysis + A/B Testing + Session Recording

```
Capabilities unlocked:
  [x] Event tracking (custom events + autocapture)
  [x] Funnel construction and analysis
  [x] Retention curves (Day 1, 7, 30)
  [x] Cohort analysis (behavioral segments)
  [x] Session recordings (see what users actually do)
  [x] Heatmaps (click patterns)
  [x] A/B testing (feature flags + experiments)
  [x] Feature flag management
  [x] User segmentation (properties and behaviors)
  [x] HogQL queries (custom SQL analytics)
  [x] UTM attribution (built-in properties)

Data extraction:
  - REST API → insights, funnels, cohorts
  - HogQL → custom queries
  - Session recordings → qualitative analysis
  - Feature flags → experiment results

Missing without PostHog (or equivalent):
  - No funnel analysis
  - No session recordings
  - No A/B testing infrastructure
  - Cannot diagnose where users drop off
  - Cannot correlate features with retention
```

### Meta Pixel → Ad Retargeting + Conversion Tracking

```
Capabilities unlocked:
  [x] Conversion tracking (Lead, Purchase, CompleteRegistration events)
  [x] Retargeting audiences (website visitors last 30/60/90 days)
  [x] Custom audiences (specific page visitors, event performers)
  [x] Lookalike audiences (based on converters)
  [x] Dynamic creative optimization (Meta tests creative combos)
  [x] Attribution (which ads drove which conversions)

Additional with CAPI:
  [x] Server-side conversion tracking (bypasses ad blockers)
  [x] Better attribution accuracy (+20-30% more conversions tracked)
  [x] Event deduplication (pixel + CAPI with same event_id)

Missing without Meta Pixel:
  - Cannot track Meta ad conversions
  - Cannot build retargeting audiences
  - Cannot create lookalike audiences
  - Meta ads run blind (no optimization signal)
```

### Google Ads Tag → Search Intent + Conversion Tracking

```
Capabilities unlocked:
  [x] Search conversion tracking (which keywords drive signups)
  [x] Enhanced conversions (hashed user data for better matching)
  [x] Offline conversion import (CRM closed deals attributed to ads)
  [x] GCLID tracking (click-level attribution)
  [x] Remarketing lists (RLSA — retarget searchers)
  [x] Cross-device attribution
  [x] Smart bidding optimization signal

Missing without Google Ads tag:
  - Cannot track search ad conversions
  - Smart bidding has no signal (bids blind)
  - Cannot use RLSA for search retargeting
  - Cannot import offline conversions
```

### Resend/SendGrid/Postmark → Email Automation

```
Capabilities unlocked:
  [x] Transactional email delivery
  [x] Email template rendering
  [x] Delivery tracking (sent, delivered, bounced)
  [x] Engagement tracking (opened, clicked)
  [x] Bounce management
  [x] Webhook events for email lifecycle

Additional capabilities by provider:
  Resend: React Email templates, modern DX
  SendGrid: Marketing automation, contact lists, dynamic templates
  Postmark: Message streams (separate transactional/marketing), highest deliverability

Drip sequence capability:
  - Basic: Can send individual emails (sequence logic must be in your app)
  - SendGrid: Has built-in automation flows
  - Resend/Postmark: Sequences require external orchestration (your app, n8n, or similar)

Missing without email provider:
  - No automated onboarding sequences
  - No trial-ending reminders
  - No lifecycle email automation
  - Cannot nurture leads from ads
  - Cannot send product updates
```

### Supabase/Firebase → User Identity + Data

```
Capabilities unlocked:
  [x] User identity for cross-platform tracking
  [x] User properties for segmentation (plan, signup date, features used)
  [x] Real-time event triggers (database triggers)
  [x] Custom audience building (query users by properties)
  [x] Edge Functions for server-side processing (Supabase)
  [x] Push notifications (Firebase)
  [x] A/B testing via Remote Config (Firebase)

GTM-specific uses:
  - Query users by signup source for custom Meta audiences
  - Trigger emails based on database events
  - Store GCLID/fbclid with user record for offline conversion import
  - Build segments for targeted campaigns
```

## Gap Analysis Logic

### Minimum Viable GTM Stack

```
For a SaaS running paid acquisition, these are the minimum integrations:

Required (non-negotiable):
  [?] Payment provider (Stripe/Paddle/LemonSqueezy)     → Revenue tracking
  [?] Analytics (PostHog/Mixpanel/Amplitude)             → Behavior tracking
  [?] Email provider (Resend/SendGrid/Postmark)          → Lifecycle emails
  [?] At least one ad pixel (Meta/Google)                → Conversion tracking

Strongly recommended:
  [?] Both Meta Pixel AND Google Ads tag                 → Full paid channel coverage
  [?] Meta CAPI (server-side tracking)                   → Reliable attribution
  [?] Session recording (PostHog/Hotjar/FullStory)       → Qualitative diagnosis
  [?] A/B testing (PostHog/LaunchDarkly/Statsig)         → Optimization

Nice to have:
  [?] Schema markup (JSON-LD)                            → Rich search results
  [?] Sitemap generation                                 → SEO crawlability
  [?] Open Graph meta tags                               → Social sharing
  [?] Error monitoring (Sentry)                          → Correlate errors with conversion drops
```

### Gap Severity Levels

```
Critical gap (blocks GTM entirely):
  - No payment provider → Cannot track revenue
  - No analytics → Cannot measure anything
  - No email → Cannot nurture or retain

High gap (blocks specific channels):
  - No Meta Pixel → Cannot run Meta ads effectively
  - No Google Ads tag → Cannot run search ads effectively
  - No email sequences → Leaking activated users

Medium gap (limits optimization):
  - No session recordings → Cannot diagnose qualitatively
  - No A/B testing → Cannot optimize systematically
  - No CAPI → Losing 20-30% conversion attribution

Low gap (polish):
  - No schema markup → Missing rich results
  - No sitemap → SEO crawl efficiency
  - No error monitoring → Blind to technical issues affecting conversion
```

## Generating Recommendations

After detection, recommendations follow this priority:

```
1. Fix critical gaps first (any missing required integration)
2. Fix high gaps for active channels (if running Meta ads, Meta Pixel is critical)
3. Address medium gaps for optimization (session recordings, A/B testing)
4. Suggest low gaps as nice-to-haves (schema, sitemap)

Each recommendation includes:
  - What to add (specific package/integration)
  - Why (what capability it unlocks)
  - Effort estimate (hours to implement)
  - Impact (what metrics improve)
```

## Stack Compatibility Matrix

```
Some integrations pair better with certain frameworks:

Next.js:
  Best: Vercel hosting, PostHog (next plugin), Clerk (next auth), Stripe
  Good: Supabase, Sentry (@sentry/nextjs), Resend
  Note: Server Components require careful tracking implementation

Vite + React:
  Best: Vercel/Netlify hosting, PostHog (react), Supabase, Stripe
  Good: Resend (server-side only), Sentry (@sentry/react)
  Note: SPA needs prerendering for SEO pages

Astro:
  Best: Vercel/Netlify/Cloudflare, any analytics (island-loaded)
  Good: Stripe (API routes), Resend (API routes)
  Note: Best for content/SEO sites, analytics load as islands

SvelteKit:
  Best: Vercel/Cloudflare, PostHog, Stripe, Resend
  Note: Smallest bundle sizes, great Core Web Vitals
```
