# Provider Fingerprints -- Exact Patterns to Detect 20+ Integrations

## Detection Strategy

Detection uses a multi-signal approach. A single signal (like a package name) gives moderate confidence. Multiple signals (package + env var + usage) give high confidence.

## Payment Providers

### Stripe

```
Package signals:
  - "stripe" in dependencies (Node SDK)
  - "@stripe/stripe-js" in dependencies (frontend)
  - "@stripe/react-stripe-js" in dependencies (React Elements)
  - "stripe" in requirements.txt (Python SDK)

Config signals:
  - STRIPE_SECRET_KEY or STRIPE_PUBLISHABLE_KEY in .env
  - sk_live_ or sk_test_ patterns in env values
  - pk_live_ or pk_test_ patterns in frontend code

Code signals:
  - import Stripe from 'stripe'
  - import { loadStripe } from '@stripe/stripe-js'
  - stripe.checkout.sessions.create
  - stripe.subscriptions.create
  - webhook: checkout.session.completed

GTM capability: Full revenue tracking, subscription analytics, MRR calculation, cohort analysis, churn measurement, LTV computation
```

### PayPal

```
Package signals:
  - "@paypal/checkout-server-sdk" in dependencies
  - "@paypal/react-paypal-js" in dependencies

Config signals:
  - PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET in .env

Code signals:
  - PayPalButtons component in JSX
  - paypal.Buttons.render

GTM capability: Transaction tracking, limited subscription analytics
```

### Paddle

```
Package signals:
  - "@paddle/paddle-js" in dependencies
  - "paddle-sdk" in dependencies

Config signals:
  - PADDLE_VENDOR_ID, PADDLE_API_KEY in .env

Code signals:
  - Paddle.Checkout.open
  - paddle.webhooks

GTM capability: Revenue tracking, subscription analytics (similar to Stripe)
```

### LemonSqueezy

```
Package signals:
  - "@lemonsqueezy/lemonsqueezy.js" in dependencies

Config signals:
  - LEMONSQUEEZY_API_KEY in .env

GTM capability: Revenue tracking, basic subscription analytics
```

## Analytics Providers

### PostHog

```
Package signals:
  - "posthog-js" in dependencies (frontend)
  - "posthog-node" in dependencies (backend)

Config signals:
  - POSTHOG_API_KEY or NEXT_PUBLIC_POSTHOG_KEY in .env
  - phc_ prefix on API key values

Code signals:
  - posthog.capture('event_name')
  - posthog.identify(userId)
  - usePostHog() hook
  - PostHogProvider component

GTM capability: Full funnel analysis, session recordings, A/B testing, feature flags, user behavior tracking, cohort analysis, HogQL queries
```

### Mixpanel

```
Package signals:
  - "mixpanel-browser" in dependencies (frontend)
  - "mixpanel" in dependencies (backend)

Config signals:
  - MIXPANEL_TOKEN in .env

Code signals:
  - mixpanel.track('event')
  - mixpanel.identify(userId)

GTM capability: Funnel analysis, retention charts, user segmentation
```

### Segment

```
Package signals:
  - "@segment/analytics-next" in dependencies
  - "analytics-node" in dependencies

Config signals:
  - SEGMENT_WRITE_KEY in .env

Code signals:
  - analytics.track('event')
  - analytics.identify(userId)
  - analytics.page()

GTM capability: Data routing hub (connects to 300+ downstream tools)
```

### Google Analytics 4

```
Package signals:
  - "ga-4-react" or "@next/third-parties" in dependencies
  - No dedicated package required (uses gtag.js)

Config signals:
  - GOOGLE_ANALYTICS_ID or GA_MEASUREMENT_ID in .env
  - G-XXXXXXXXXX pattern in config

Code signals:
  - gtag('event', ...) in source
  - Script src containing googletagmanager.com/gtag
  - google analytics snippet in HTML head

GTM capability: Basic funnel analysis, traffic source attribution, audience demographics
```

### Amplitude

```
Package signals:
  - "@amplitude/analytics-browser" in dependencies
  - "amplitude-js" in dependencies (legacy)

Config signals:
  - AMPLITUDE_API_KEY in .env

Code signals:
  - amplitude.track('event')
  - amplitude.identify(userId)

GTM capability: Funnel analysis, user behavior, retention, cohort analysis
```

## Email Providers

### Resend

```
Package signals:
  - "resend" in dependencies

Config signals:
  - RESEND_API_KEY in .env
  - re_ prefix on API key values

Code signals:
  - import { Resend } from 'resend'
  - resend.emails.send()

GTM capability: Transactional email, email sequence delivery, engagement tracking
```

### SendGrid

```
Package signals:
  - "@sendgrid/mail" in dependencies
  - "@sendgrid/client" in dependencies

Config signals:
  - SENDGRID_API_KEY in .env
  - SG. prefix on API key values

Code signals:
  - import sgMail from '@sendgrid/mail'
  - sgMail.send()

GTM capability: Transactional + marketing email, contact management, automation
```

### Postmark

```
Package signals:
  - "postmark" in dependencies

Config signals:
  - POSTMARK_SERVER_TOKEN or POSTMARK_API_TOKEN in .env

Code signals:
  - import { ServerClient } from 'postmark'
  - client.sendEmail()

GTM capability: Transactional email (highest deliverability), message streams
```

### Mailchimp

```
Package signals:
  - "@mailchimp/mailchimp_marketing" in dependencies

Config signals:
  - MAILCHIMP_API_KEY in .env

GTM capability: Marketing email, audience management, basic automation
```

## Ad Platform Tracking

### Meta Pixel

```
Package signals:
  - "react-facebook-pixel" in dependencies (optional)
  - No npm package required (uses script tag)

Config signals:
  - META_PIXEL_ID or VITE_META_PIXEL_ID in .env
  - FACEBOOK_PIXEL_ID in .env

Code signals:
  - fbq('init', ...) in source
  - fbq('track', 'Purchase', ...)
  - Script src containing connect.facebook.net/en_US/fbevents.js
  - _fbp or _fbc cookie references

GTM capability: Retargeting audiences, conversion tracking, CAPI integration potential
```

### Google Ads Tag

```
Config signals:
  - GOOGLE_ADS_ID or AW-XXXXXXXXX pattern in config
  - GOOGLE_CONVERSION_ID in .env

Code signals:
  - gtag('event', 'conversion', { send_to: 'AW-...' })
  - Script src containing googletagmanager.com/gtag
  - gclid capture in JavaScript

GTM capability: Search/display conversion tracking, remarketing lists, offline conversion import
```

### TikTok Pixel

```
Code signals:
  - ttq.track('event') in source
  - Script containing analytics.tiktok.com
  - TIKTOK_PIXEL_ID in .env

GTM capability: TikTok retargeting, conversion tracking
```

## Auth Providers

### Supabase

```
Package signals:
  - "@supabase/supabase-js" in dependencies
  - "@supabase/auth-helpers-nextjs" in dependencies
  - "@supabase/ssr" in dependencies

Config signals:
  - SUPABASE_URL or NEXT_PUBLIC_SUPABASE_URL in .env
  - SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY in .env

GTM capability: User data for segmentation, event triggers, auth for tracking identity
```

### Firebase

```
Package signals:
  - "firebase" in dependencies (frontend)
  - "firebase-admin" in dependencies (backend)

Config signals:
  - FIREBASE_API_KEY, FIREBASE_PROJECT_ID in .env

GTM capability: User auth, Firestore data, push notifications, A/B testing (Remote Config)
```

### Clerk

```
Package signals:
  - "@clerk/nextjs" or "@clerk/clerk-react" in dependencies

Config signals:
  - CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY in .env

GTM capability: User identity, organization data, session tracking
```

### Auth0

```
Package signals:
  - "@auth0/auth0-react" or "@auth0/nextjs-auth0" in dependencies

Config signals:
  - AUTH0_DOMAIN, AUTH0_CLIENT_ID in .env

GTM capability: User identity, multi-tenant segmentation
```

## Hosting/Deployment

### Vercel

```
File signals:
  - vercel.json in root
  - .vercel/ directory
  - VERCEL_URL in .env

GTM capability: Deployment automation, preview URLs for testing, edge functions, analytics
```

### Netlify

```
File signals:
  - netlify.toml in root
  - _redirects or _headers files

GTM capability: Deployment, forms, edge functions, basic analytics
```

## Monitoring

### Sentry

```
Package signals:
  - "@sentry/react" or "@sentry/nextjs" or "@sentry/node" in dependencies

Config signals:
  - SENTRY_DSN in .env

GTM capability: Error tracking (correlate errors with conversion drops), performance monitoring
```

## Detection Priority Order

When scanning a codebase, check in this order for maximum efficiency:

```
1. package.json (or requirements.txt, Gemfile, etc.) — fastest, most reliable
2. .env and .env.example files — reveals integrations even without packages
3. Config files (next.config.js, vite.config.ts, etc.) — framework-level integrations
4. src/ directory imports — confirms active usage
5. HTML templates/index.html — script tags for tracking pixels
```
