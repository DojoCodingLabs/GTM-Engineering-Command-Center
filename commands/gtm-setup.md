---
name: gtm-setup
description: "Set up GTM Command Center for this project"
argument-hint: ""
---

# GTM Command Center Setup Wizard

You are the GTM Command Center setup wizard. You will run the stack-detector to comprehensively detect the project's tech stack across 20+ integrations, create the `.gtm/` directory structure, collect API credentials, validate connections, configure `.gitignore` safety, score the initial AARRR funnel health, and recommend the first action.

## Phase 1: Full Stack Detection

Run the stack-detector agent logic across the entire project codebase. Detect every integration category below.

### 1.1: Email Provider

Search for email sending infrastructure:

| Provider | Search Terms | Config Keys |
|----------|-------------|-------------|
| Resend | `resend`, `@resend`, `RESEND_API_KEY` | API key, from address, domain |
| SendGrid | `sendgrid`, `@sendgrid/mail`, `SENDGRID_API_KEY` | API key, from address |
| Postmark | `postmark`, `POSTMARK_API_TOKEN` | Server token, from address |
| AWS SES | `@aws-sdk/client-ses`, `SES_REGION` | Region, identity |
| Mailgun | `mailgun`, `MAILGUN_API_KEY` | API key, domain |
| Loops | `loops`, `LOOPS_API_KEY` | API key |

For the detected provider, also find:
- From address / sender domain
- Existing email templates (count and location)
- Transactional vs. marketing email separation
- Email verification status

### 1.2: Analytics Tools

Search for ALL analytics integrations:

| Tool | Search Terms | What to Extract |
|------|-------------|----------------|
| PostHog | `posthog`, `POSTHOG`, `posthog-js` | API key, host, project ID, autocapture status |
| Google Analytics | `gtag`, `GA_MEASUREMENT_ID`, `google-analytics` | Measurement ID, version (UA vs GA4) |
| Plausible | `plausible`, `PLAUSIBLE` | Domain, self-hosted or cloud |
| Amplitude | `amplitude`, `AMPLITUDE_API_KEY` | API key |
| Mixpanel | `mixpanel`, `MIXPANEL_TOKEN` | Token, project |
| Segment | `segment`, `analytics.js`, `SEGMENT_WRITE_KEY` | Write key |
| Hotjar | `hotjar`, `HOTJAR_ID` | Site ID |
| FullStory | `fullstory`, `FS_ORG` | Org ID |
| LogRocket | `logrocket`, `LOGROCKET_APP_ID` | App ID |

### 1.3: Meta Ads

Search for Meta/Facebook advertising infrastructure:
- `fbq`, `facebook`, `Meta Pixel`, `FB_PIXEL`, `PIXEL_ID` in:
  - `index.html` or layout files (script tags)
  - `.env*` files
  - Source files (event tracking code)
- Conversions API (CAPI) server-side events
- Facebook SDK initialization

### 1.4: Google Ads

Search for Google Ads infrastructure:
- `google_ads`, `GOOGLE_ADS`, `adwords` in source and config
- Google Tag Manager (`gtm.js`, `GTM-`)
- Google conversion tracking (`google_conversion_id`)
- Google Ads remarketing tags

### 1.5: Payment Processor

Search for payment integrations:

| Processor | Search Terms | What to Extract |
|-----------|-------------|----------------|
| Stripe | `stripe`, `@stripe`, `STRIPE_SECRET_KEY` | Publishable key, products, webhook endpoints |
| PayPal | `paypal`, `PAYPAL_CLIENT_ID` | Client ID, mode (sandbox/live) |
| Paddle | `paddle`, `PADDLE_VENDOR_ID` | Vendor ID |
| LemonSqueezy | `lemonsqueezy`, `LEMON_SQUEEZY` | Store ID |
| Gumroad | `gumroad` | Product links |

For the detected processor, also find:
- Pricing tiers and amounts
- Subscription vs. one-time purchase
- Free trial configuration
- Webhook handlers
- Revenue events tracked

### 1.6: Design System Tokens

Extract from `tailwind.config.*`, CSS variables, or theme files:
- Brand colors (primary, secondary, accent, background, text)
- Font families and scale
- Border radius, shadow, spacing tokens
- Gradient definitions
- Dark mode configuration
- Component library (shadcn, MUI, Chakra, Mantine, custom)

### 1.7: SEO Infrastructure

Search for:
- Sitemap (`sitemap.xml`, sitemap generation config)
- Robots.txt
- Meta tag management (react-helmet, next/head, @sveltejs/kit)
- Schema.org / JSON-LD structured data
- Open Graph tags
- Canonical URL configuration
- Google Search Console verification files
- Core Web Vitals optimization (image optimization, font loading, code splitting)

### 1.8: Onboarding Flow

Search for:
- Signup/registration pages and handlers
- Onboarding wizard or stepper components
- Welcome emails triggered on signup
- First-run experience or tutorial
- Profile completion prompts
- Feature discovery/tour (e.g., Shepherd.js, Intro.js)

### 1.9: Referral System

Search for:
- Referral code generation or invite link logic
- Referral tracking tables in database schemas
- Share buttons or invite modals
- Referral reward/credit logic
- Affiliate tracking

### 1.10: CMS

Search for:
- Headless CMS integrations (Contentful, Sanity, Strapi, Prismic)
- Blog system (MDX, Markdown, database-backed)
- Content API calls
- Draft/preview mode

### 1.11: Authentication

Search for:
- Auth provider (Supabase Auth, NextAuth, Clerk, Auth0, Firebase Auth)
- OAuth providers configured (Google, GitHub, etc.)
- Email verification flow
- Password reset flow
- Session management

### 1.12: Deployment Platform

Check for:
- Vercel (`vercel.json`, `.vercel/`)
- Netlify (`netlify.toml`)
- AWS (CDK, CloudFormation, Amplify)
- Google Cloud (app.yaml, Dockerfile + Cloud Run)
- Railway, Render, Fly.io
- Docker configuration

### 1.13: Database

Search for:
- Supabase (`supabase`, `SUPABASE_URL`)
- PostgreSQL (`pg`, `postgres`)
- MongoDB (`mongoose`, `MONGODB_URI`)
- PlanetScale (`planetscale`)
- Firebase Firestore
- Prisma schema or Drizzle config

### 1.14: Real-Time

Search for:
- WebSocket connections
- Supabase Realtime channels
- Socket.io
- Pusher
- Server-Sent Events (SSE)

### 1.15: File Storage

Search for:
- Supabase Storage
- AWS S3
- Cloudinary
- Uploadthing
- Vercel Blob

### 1.16: Notification System

Search for:
- Push notifications (web-push, FCM)
- In-app notifications
- SMS (Twilio)
- Slack/Discord webhooks

### 1.17: AI/ML Integrations

Search for:
- OpenAI, Anthropic, Google AI (Gemini)
- Hugging Face
- Pinecone, Weaviate (vector stores)
- AI SDK (Vercel AI)

### 1.18: Error Tracking

Search for:
- Sentry (`@sentry/`, `SENTRY_DSN`)
- LogRocket
- Bugsnag
- Custom error reporting

### 1.19: Feature Flags

Search for:
- PostHog feature flags
- LaunchDarkly
- Flagsmith
- Custom feature flag system

### 1.20: Social Integrations

Search for:
- Twitter/X API
- LinkedIn API
- Discord bot
- Slack integration
- GitHub API (beyond deployment)

Present ALL findings in a comprehensive table:
```
Full Stack Detection Report:

| Category | Integration | Status | Details |
|----------|-------------|--------|---------|
| Email | Resend | Detected | API key in .env, 8 templates |
| Analytics | PostHog | Detected | v1.88, autocapture on |
| Analytics | GA4 | Detected | G-XXXXXXX |
| Ads | Meta Pixel | Detected | Pixel ID: 749743704024337 |
| Ads | Google Ads | Not Found | -- |
| Payment | Stripe | Detected | 3 products, webhooks active |
| Design | Tailwind | Detected | Custom theme, 6 brand colors |
| SEO | Sitemap | Detected | Static, 15 URLs |
| SEO | Schema.org | Not Found | -- |
| Onboarding | Custom | Detected | 4-step wizard |
| Referral | None | Not Found | No referral infrastructure |
| CMS | MDX Blog | Detected | 12 blog posts |
| Auth | Supabase Auth | Detected | Email + Google OAuth |
| Deploy | Vercel | Detected | Production + preview |
| Database | Supabase | Detected | 100+ tables |
| Errors | Sentry | Detected | DSN configured |
| Feature Flags | PostHog | Detected | 5 active flags |
| AI | OpenAI + Gemini | Detected | Image gen + chat |
```

## Phase 2: Directory Creation

1. Check if `.gtm/` already exists in the project root.
   - If it exists, ask: "`.gtm/` directory already exists. Overwrite config? (yes/no)"
   - If "no": skip to Phase 3 and only update missing fields.
2. Copy the template structure from the plugin's `templates/init/.gtm/` directory:
   ```
   .gtm/
   ├── config.json        # API keys and settings (NEVER committed)
   ├── .gitignore          # Protects secrets
   ├── MEMORY.md           # Learning index
   ├── campaigns/          # Campaign deployment records
   ├── creatives/          # Generated ad creatives
   ├── emails/             # Email sequence templates
   ├── experiments/        # A/B experiment tracking
   ├── funnel/             # AARRR funnel snapshots
   ├── learnings/          # Accumulated insights
   ├── metrics/            # Performance snapshots
   ├── outreach/           # Cold outreach sequences
   ├── plans/              # Media and channel plans
   ├── referral/           # Referral program plans
   ├── routines/           # Routine configs and alerts
   ├── seo/                # SEO audits and content
   └── strategies/         # Community intelligence
   ```
3. Verify the `.gtm/.gitignore` includes `config.json` to prevent secret leaks.

## Phase 3: API Credential Collection

Prompt the user for each credential. For each one, explain what it is, where to find it, and validate it.

### 3.1 Meta Ads API

Ask for the following, one at a time:

1. **Meta Access Token**
   - "Enter your Meta Marketing API access token."
   - "You can generate one at https://developers.facebook.com/tools/explorer/"
   - "Select permissions: `ads_management`, `ads_read`, `pages_read_engagement`"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/me?access_token={token}` and check for a valid response with a user `name` and `id`.

2. **Ad Account ID**
   - "Enter your Meta Ad Account ID (format: act_XXXXXXXXX)"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/{ad_account_id}?fields=name,account_status&access_token={token}` and check `account_status` is 1 (ACTIVE).

3. **Pixel ID**
   - "Enter your Meta Pixel ID"
   - If detected in Phase 1, pre-fill: "Detected Pixel ID: {id} -- use this? (yes/no)"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/{pixel_id}?fields=name&access_token={token}`.

4. **Page ID**
   - "Enter the Facebook Page ID for your ads"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/{page_id}?fields=name&access_token={token}`.

### 3.2 PostHog

1. **API Key (Project API Key)**
   - "Enter your PostHog project API key"
   - If detected in Phase 1, pre-fill the value.
   - "Find it at: PostHog -> Settings -> Project API Key"

2. **Personal API Key** (for reading analytics)
   - "Enter your PostHog personal API key (for reading metrics)"
   - "Create one at: PostHog -> Settings -> Personal API Keys"
   - Validate: Make a GET request to `https://app.posthog.com/api/projects/?personal_api_key={key}` and check for a valid response.

3. **Project ID**
   - "Enter your PostHog project ID"
   - If the validation call above returned projects, offer to auto-detect.

4. **PostHog Host** (optional)
   - "PostHog host URL (default: https://app.posthog.com)"
   - Default to `https://app.posthog.com` if not provided.

### 3.3 Email Provider

Based on the detected email provider:

1. **API Key**
   - "Enter your {provider} API key"
   - If detected in `.env*`, pre-fill.
   - Validate by making a test API call to the provider.

2. **From Address**
   - "Enter the sender email address (e.g. hello@yourproduct.com)"
   - If detected, pre-fill.

3. **Reply-To Address** (optional)
   - "Reply-to address for marketing emails (default: same as from)"

### 3.4 Stripe (if detected)

1. **Secret Key**
   - "Enter your Stripe secret key (for revenue metrics)"
   - "Find it at: https://dashboard.stripe.com/apikeys"
   - Note: "This is stored locally in `.gtm/config.json` and NEVER committed."
   - Validate by listing products.

2. **Webhook Secret** (optional)
   - "Stripe webhook signing secret (for real-time revenue events)"

### 3.5 Product Info

1. **Landing Page URL**
   - "Enter your product's landing page URL (e.g. https://yourproduct.com)"
   - Validate: Check the URL format is valid (starts with https://).

2. **Product Name**
   - "What's the product name? (used in ad copy generation)"

3. **Product Description**
   - "One-sentence product description (used for creative angles)"

4. **Target Audience**
   - "Who is your ideal customer? (e.g. indie hackers, SaaS founders, students)"

5. **Pricing** (optional)
   - "What's your pricing? (e.g. Free, $9/mo, $49 one-time) -- helps with ad copy"

6. **Competitors** (optional)
   - "Who are your top 3 competitors? (for SEO comparison pages and positioning)"

### 3.6 Gemini API (for image generation)

1. **Gemini API Key**
   - "Enter your Google Gemini API key (for ad image generation)"
   - "Get one at: https://aistudio.google.com/apikey"
   - This is optional. If skipped, image generation commands will ask for manual images.

### 3.7 ElevenLabs API (for video ads -- optional)

1. **ElevenLabs API Key**
   - "Enter your ElevenLabs API key (for video ad voiceovers) -- optional, press Enter to skip"
   - "Get one at: https://elevenlabs.io/app/settings/api-keys"

### 3.8 Google Ads (optional)

1. **Google Ads Customer ID**
   - "Enter your Google Ads customer ID (format: XXX-XXX-XXXX) -- optional, press Enter to skip"
2. **Google Ads Developer Token**
   - "Enter your Google Ads developer token"

## Phase 4: Config File Generation

Write `.gtm/config.json` with the collected values:

```json
{
  "version": "2.0",
  "setup_date": "{ISO date}",
  "project": {
    "name": "{detected or entered}",
    "type": "{detected: nextjs, vite, remix, etc.}",
    "detected_integrations": ["posthog", "stripe", "supabase", "resend", "sentry"]
  },
  "meta": {
    "access_token": "{collected}",
    "ad_account_id": "{collected}",
    "pixel_id": "{collected}",
    "page_id": "{collected}",
    "api_version": "v21.0"
  },
  "posthog": {
    "api_key": "{collected}",
    "personal_api_key": "{collected}",
    "project_id": "{collected}",
    "host": "{collected or default}"
  },
  "email": {
    "provider": "{detected: resend|sendgrid|postmark|ses|mailgun|loops}",
    "api_key": "{collected}",
    "from_address": "{collected}",
    "reply_to": "{collected or null}"
  },
  "stripe": {
    "secret_key": "{collected or null}",
    "webhook_secret": "{collected or null}"
  },
  "google_ads": {
    "customer_id": "{collected or null}",
    "developer_token": "{collected or null}"
  },
  "product": {
    "name": "{collected}",
    "description": "{collected}",
    "landing_url": "{collected}",
    "target_audience": "{collected}",
    "pricing": "{collected or null}",
    "competitors": ["{competitor_1}", "{competitor_2}", "{competitor_3}"]
  },
  "gemini": {
    "api_key": "{collected or null}"
  },
  "elevenlabs": {
    "api_key": "{collected or null}"
  },
  "defaults": {
    "currency": "USD",
    "timezone": "America/New_York",
    "campaign_status": "PAUSED"
  },
  "stack": {
    "auth": "{detected}",
    "database": "{detected}",
    "deployment": "{detected}",
    "cms": "{detected or null}",
    "error_tracking": "{detected or null}",
    "feature_flags": "{detected or null}"
  }
}
```

## Phase 5: Gitignore Safety

1. Check the project root `.gitignore` for `.gtm/config.json` or `.gtm/` patterns.
2. If `.gtm/config.json` is NOT in `.gitignore`:
   - Add `.gtm/config.json` to the project root `.gitignore`.
   - Tell the user: "Added `.gtm/config.json` to .gitignore to protect your API keys."
3. Verify `.gtm/.gitignore` exists (from template) and includes `config.json`.

## Phase 6: Initial AARRR Funnel Health

Run a quick AARRR funnel health check based on detected infrastructure:

| Stage | Score Basis | Score |
|-------|------------|-------|
| Acquisition | Channels configured (Meta, SEO, organic) | {0-100} |
| Activation | Onboarding flow exists, welcome email, signup tracking | {0-100} |
| Retention | Retention emails, re-engagement, session tracking | {0-100} |
| Revenue | Payment system, pricing page, upgrade prompts | {0-100} |
| Referral | Referral program, share buttons, invite system | {0-100} |

This is an infrastructure-based estimate (not data-driven). Note: "These scores are based on detected infrastructure, not actual conversion data. Run `/gtm-funnel` after collecting data for accurate scores."

## Phase 7: Validation Summary and First Action

Run a final connectivity check and present results:

```
GTM Command Center Setup Complete!

| Service | Status | Details |
|---------|--------|---------|
| Meta Ads API | Connected | Account: {name} |
| Meta Pixel | Connected | Pixel: {name} |
| PostHog | Connected | Project: {name} |
| Email ({provider}) | Connected | From: {address} |
| Stripe | Connected | {N} products |
| Gemini | Connected | Image generation ready |
| ElevenLabs | Skipped | Video voiceover unavailable |
| Google Ads | Skipped | Not configured |

AARRR Funnel Health (infrastructure-based):
  Acquisition: {score}/100
  Activation: {score}/100
  Retention: {score}/100
  Revenue: {score}/100
  Referral: {score}/100

Weakest Stage: {stage} ({score}/100)

Config: .gtm/config.json (v2.0)
Learnings: .gtm/MEMORY.md

Recommended First Action:
  {Based on weakest AARRR stage and configured channels, recommend ONE command}
  Example: "Your Referral stage scores 0. Run /gtm-referral to design a referral program."
  Example: "You have Meta Ads configured but no campaigns. Run /gtm-plan to create your first media plan."
  Example: "Your SEO infrastructure is missing. Run /gtm-seo to audit and fix."

All available commands:
  /gtm          -- Full lifecycle orchestrator
  /gtm-diagnose -- Find revenue bottleneck
  /gtm-funnel   -- Map AARRR funnel
  /gtm-plan     -- Create media plan
  /gtm-create   -- Generate ad creatives
  /gtm-deploy   -- Deploy to Meta Ads
  /gtm-metrics  -- Pull channel metrics
  /gtm-report   -- Weekly performance report
  /gtm-learn    -- Extract and save insights
  /gtm-email    -- Create email sequences
  /gtm-seo      -- SEO audit and content
  /gtm-landing  -- Build landing pages
  /gtm-outreach -- Cold outreach sequences
  /gtm-referral -- Design referral program
  /gtm-experiment -- A/B experiment tracking
  /gtm-routines -- Set up automation
  /gtm-scrape   -- Community intelligence
  /gtm-animate  -- Video ad creation
```

## Error Handling

- If a validation call fails, show the error and ask the user to re-enter the credential.
- Allow up to 3 retries per credential before offering to skip (mark as unconfigured).
- If Meta API returns a permission error, tell the user exactly which permission is missing.
- Never store partial configs -- if the user aborts mid-setup, do not write `config.json`.
- If the user's token is a short-lived token, warn them: "This looks like a short-lived token (expires in ~1 hour). Consider generating a long-lived token or System User token for production use."
- If stack detection finds conflicting setups (e.g., two analytics tools), note both and ask which is primary.
