---
name: stack-detection
description: Stack detection engine — provider fingerprints, framework detection, integration mapping for GTM capability assessment
---

# Stack Detection Engine

Automatically detect a project's technology stack, integrations, and GTM capabilities by scanning the codebase. This skill provides the fingerprinting patterns used by the GTM setup command to assess what's already available and what needs to be added.

## Detection Process

```
Stack Detection Pipeline:
  1. Framework Detection → What frontend/backend framework is in use?
  2. Provider Fingerprints → Which services are integrated?
  3. Integration Mapping → What GTM capabilities exist?
  4. Gap Analysis → What's missing for full GTM automation?
```

## Framework Detection Summary

| Framework | Primary Signal | Config File | Package Manager |
|-----------|---------------|-------------|----------------|
| Next.js | `next.config.*` | `next.config.js/mjs/ts` | npm/yarn/pnpm |
| Vite + React | `vite.config.*` + `react` in deps | `vite.config.ts` | npm/yarn/pnpm |
| Remix | `@remix-run/*` in deps | `remix.config.js` | npm/yarn/pnpm |
| SvelteKit | `@sveltejs/kit` in deps | `svelte.config.js` | npm/yarn/pnpm |
| Nuxt | `nuxt` in deps | `nuxt.config.ts` | npm/yarn/pnpm |
| Astro | `astro` in deps | `astro.config.*` | npm/yarn/pnpm |
| Django | `django` in requirements | `settings.py` | pip/pipenv/poetry |
| Rails | `rails` in Gemfile | `config/application.rb` | bundler |
| Laravel | `laravel/framework` in composer | `config/app.php` | composer |
| Express | `express` in deps | — | npm/yarn/pnpm |

## Provider Detection Summary

| Provider | Category | Primary Fingerprint |
|----------|----------|-------------------|
| Stripe | Payments | `stripe` or `@stripe/*` in deps |
| Supabase | Auth/DB | `@supabase/supabase-js` in deps |
| Firebase | Auth/DB | `firebase` or `firebase-admin` in deps |
| PostHog | Analytics | `posthog-js` or `posthog-node` in deps |
| Mixpanel | Analytics | `mixpanel-browser` in deps |
| Segment | Analytics | `@segment/analytics-next` in deps |
| Resend | Email | `resend` in deps |
| SendGrid | Email | `@sendgrid/mail` in deps |
| Postmark | Email | `postmark` in deps |
| Meta Pixel | Ads | `fbq(` in source or `PIXEL_ID` env var |
| Google Ads | Ads | `gtag(` in source or `AW-` conversion ID |
| Vercel | Hosting | `vercel.json` or `.vercel/` directory |
| Netlify | Hosting | `netlify.toml` or `_redirects` |
| Cloudflare | CDN/Hosting | `wrangler.toml` or `_worker.js` |
| Clerk | Auth | `@clerk/*` in deps |
| Auth0 | Auth | `@auth0/*` in deps |
| Mux | Video | `@mux/*` in deps |
| Algolia | Search | `algoliasearch` in deps |
| Sentry | Monitoring | `@sentry/*` in deps |
| LaunchDarkly | Feature Flags | `launchdarkly-*` in deps |

## GTM Capability Matrix

Each detected integration maps to specific GTM capabilities:

```
Stripe detected → Revenue tracking, cohort analysis, LTV calculation, churn measurement
PostHog detected → Funnel analysis, user behavior, session recordings, A/B testing
Meta Pixel detected → Retargeting audiences, conversion tracking, CAPI potential
Google Ads detected → Search intent data, conversion tracking, keyword performance
Resend detected → Email sequences, deliverability data, engagement tracking
Supabase detected → User data for segmentation, event triggers, custom audiences
```

## Gap Analysis Output

After scanning, produce a GTM readiness report:

```
GTM READINESS REPORT
====================

Framework: Vite + React + TypeScript
Hosting: Vercel

DETECTED INTEGRATIONS:
  [x] Stripe (payments) → Revenue tracking ready
  [x] Supabase (auth/db) → User segmentation ready
  [x] PostHog (analytics) → Funnel analysis ready
  [x] Resend (email) → Email sequences ready
  [x] Meta Pixel (ads) → Retargeting ready

MISSING FOR FULL GTM:
  [ ] Google Ads tag → No search conversion tracking
  [ ] Meta CAPI → Server-side tracking (bypasses ad blockers)
  [ ] Schema markup → No rich results in search
  [ ] Sitemap → Not auto-generated
  [ ] Open Graph tags → Social sharing metadata missing

GTM CAPABILITY SCORE: 7/10

RECOMMENDATIONS (priority order):
  1. Add Meta CAPI for reliable conversion attribution
  2. Add Google Ads gtag for search campaign tracking
  3. Add JSON-LD schema for rich search results
  4. Generate sitemap for SEO crawlability
```

## Detection Rules

### Confidence Levels

| Confidence | Criteria | Example |
|-----------|----------|---------|
| Confirmed | Package in deps + config file + env var | Stripe in package.json + STRIPE_SECRET_KEY in .env |
| High | Package in deps + usage in source | `posthog-js` in deps + `posthog.capture()` in source |
| Medium | Package in deps only | `resend` in package.json but no usage found |
| Low | Env var only (no package) | `SENDGRID_API_KEY` in .env but no sendgrid package |
| Inferred | Code patterns without explicit package | `fetch('https://api.stripe.com/...')` without stripe SDK |

### Priority Detection Order

1. Package manifest (package.json, requirements.txt, Gemfile, etc.)
2. Configuration files (next.config.js, .env, etc.)
3. Import statements in source code
4. Environment variable names
5. HTML/template patterns (script tags, meta tags)
