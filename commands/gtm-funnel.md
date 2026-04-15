---
name: gtm-funnel
description: "Map the full AARRR funnel with health scores"
argument-hint: ""
---

# AARRR Funnel Mapping Command

You are the funnel-diagnostician agent in mapping mode. You will run the stack-detector to discover all lifecycle events across the project's integrations, map them to AARRR funnel stages, score each stage, identify gaps, and save a funnel snapshot.

## Phase 1: Discover All Lifecycle Events

Run the stack-detector logic across the project codebase to find every user lifecycle event.

### 1.1: PostHog Events

Search the codebase for PostHog event tracking calls:
- `posthog.capture(` — custom events
- `posthog.identify(` — user identification
- `posthog.group(` — group analytics
- `posthog.onFeatureFlags(` — feature flag checks
- Search for event name strings passed to capture calls

Also check PostHog config for:
- Autocapture enabled/disabled
- Session recording enabled
- Feature flags in use

### 1.2: Meta Pixel Events

Search for Facebook/Meta Pixel events:
- `fbq('track',` — standard events (PageView, Lead, Purchase, AddToCart, etc.)
- `fbq('trackCustom',` — custom events
- Server-side CAPI events (in Edge Functions or API routes)

### 1.3: Stripe Events

Search for Stripe integration points:
- `stripe.checkout.sessions.create` — checkout initiation
- `stripe.subscriptions` — subscription lifecycle
- Webhook handlers for `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`

### 1.4: Email Events

Search for email sending triggers:
- Resend/SendGrid/Postmark API calls
- Email template references
- Transactional vs. marketing email distinction
- Drip/sequence triggers

### 1.5: Custom Analytics

Search for any other tracking:
- `gtag(` — Google Analytics
- `plausible(` — Plausible Analytics
- `amplitude.track(` — Amplitude
- Custom event buses or logging
- `window.dataLayer.push` — GTM data layer

### 1.6: Auth Events

Search for authentication lifecycle:
- Signup/registration handlers
- Login events
- Password reset
- Email verification
- OAuth callbacks
- Session management

### 1.7: Product Events

Search for product-specific lifecycle events:
- Onboarding completion steps
- Feature adoption events
- Content creation/consumption events
- Collaboration/sharing events
- Settings/profile completion

Present all discovered events in a comprehensive table:
```
| Event | Source | Location in Code | AARRR Stage | Status |
|-------|--------|-----------------|-------------|--------|
| $pageview | PostHog | auto-capture | Acquisition | Active |
| sign_up | PostHog | src/auth/signup.tsx:42 | Activation | Active |
| Lead | Meta Pixel | src/utils/tracking.ts:18 | Acquisition | Active |
| checkout.session.completed | Stripe | supabase/functions/stripe-webhook | Revenue | Active |
| ... | ... | ... | ... | ... |
```

## Phase 2: Map Events to AARRR Stages

Organize all discovered events into the five AARRR stages:

### Acquisition (Awareness + First Visit)
Events that represent a user discovering and visiting the product:
- Page views, landing page visits
- Ad clicks, organic search arrivals
- Social media referrals
- Direct traffic

### Activation (First Value Experience)
Events that represent a user getting value for the first time:
- Account creation / signup
- Onboarding completion
- First key action (first course started, first project created, etc.)
- Email verification
- Profile completion

### Retention (Repeat Usage)
Events that represent a user coming back:
- Repeat logins
- Feature usage over time
- Content consumption patterns
- Notification interactions
- Session frequency

### Revenue (Monetization)
Events that represent a user paying:
- Checkout initiation
- Purchase/subscription completion
- Upgrade events
- Payment method added
- Invoice paid

### Referral (Viral Growth)
Events that represent a user bringing others:
- Referral link generation
- Invite sent
- Social share
- Review/testimonial submission
- Referral conversion (invited user signs up)

## Phase 3: Score Each Stage

For each AARRR stage, calculate a health score (0-100) based on:

1. **Event Coverage** (0-30 points): Are the right events being tracked?
   - 30: All critical events tracked with properties
   - 20: Most events tracked, some gaps
   - 10: Basic tracking only
   - 0: No tracking for this stage

2. **Data Quality** (0-30 points): Is the data reliable?
   - 30: Events fire correctly, have useful properties, are consistent
   - 20: Events exist but missing key properties or inconsistent naming
   - 10: Events exist but unreliable (no validation, missing on some paths)
   - 0: No data or completely broken tracking

3. **Conversion Metrics** (0-40 points): What are the actual conversion rates?
   - Use data from `.gtm/metrics/` snapshots if available
   - Use industry benchmarks if no data exists
   - Score relative to benchmarks for the product category

## Phase 4: Identify Gaps

For each AARRR stage, identify what is missing:

### Critical Gaps (Must Fix)
- Missing tracking for key lifecycle events
- No conversion measurement between stages
- Broken or inactive tracking code

### Important Gaps (Should Fix)
- Missing event properties (e.g., tracking signup but not signup source)
- No A/B testing infrastructure
- No cohort analysis capability

### Enhancement Gaps (Nice to Have)
- No referral program at all
- No automated retention emails
- No upsell/upgrade prompts
- No NPS or satisfaction tracking

Present gaps as a checklist:
```
ACQUISITION:
  [x] Page view tracking
  [x] UTM parameter capture
  [ ] Ad click-through tracking (MISSING -- no server-side CAPI)
  [ ] Organic search tracking (MISSING -- no GSC integration)

ACTIVATION:
  [x] Signup event
  [x] Onboarding start
  [ ] Onboarding completion (MISSING -- no completion event)
  [ ] Time-to-first-value measurement (MISSING)

RETENTION:
  [ ] No retention email sequences (CRITICAL GAP)
  [ ] No push notification system
  [x] Session tracking via PostHog

REVENUE:
  [x] Stripe checkout integration
  [x] Subscription webhook handlers
  [ ] Free-to-paid conversion tracking (MISSING -- no explicit event)

REFERRAL:
  [ ] No referral program (CRITICAL GAP)
  [ ] No share/invite functionality
  [ ] No referral tracking
```

## Phase 5: Save Funnel Snapshot

Create the `.gtm/funnel/` directory if it does not exist.

Save to `.gtm/funnel/funnel-{YYYY-MM-DD}.json`:

```json
{
  "date": "{ISO date}",
  "version": "1.0",
  "stages": {
    "acquisition": {
      "score": 72,
      "events": ["$pageview", "Lead", "utm_capture"],
      "gaps": ["No server-side CAPI", "No GSC integration"],
      "metrics": {"weekly_visitors": 10000, "top_source": "meta_paid"}
    },
    "activation": {
      "score": 58,
      "events": ["sign_up", "onboarding_start"],
      "gaps": ["No onboarding_complete event", "No time-to-value tracking"],
      "metrics": {"signup_rate": 0.25}
    },
    "retention": {
      "score": 35,
      "events": ["session_start"],
      "gaps": ["No retention emails", "No re-engagement system"],
      "metrics": {"dau_mau": 0.08}
    },
    "revenue": {
      "score": 65,
      "events": ["checkout_completed", "subscription_created"],
      "gaps": ["No free-to-paid tracking"],
      "metrics": {"mrr": 2400, "monthly_churn": 0.07}
    },
    "referral": {
      "score": 12,
      "events": [],
      "gaps": ["No referral program", "No share functionality", "No invite system"],
      "metrics": {"k_factor": 0}
    }
  },
  "total_events_discovered": 42,
  "tracking_sources": ["posthog", "meta_pixel", "stripe", "custom"],
  "critical_gaps": ["No retention emails", "No referral program"]
}
```

Save a human-readable funnel map to `.gtm/funnel/funnel-{YYYY-MM-DD}.md`:

```markdown
# AARRR Funnel Map -- {date}

## Funnel Visualization

ACQUISITION  [=========================] 72/100
  Events: $pageview, Lead, utm_capture
  Gap: No server-side CAPI

ACTIVATION   [====================]      58/100
  Events: sign_up, onboarding_start
  Gap: No onboarding_complete event

RETENTION    [============]              35/100  <-- WEAKEST
  Events: session_start
  Gap: No retention emails, no re-engagement

REVENUE      [======================]    65/100
  Events: checkout_completed, subscription_created
  Gap: No free-to-paid tracking

REFERRAL     [====]                      12/100  <-- CRITICAL
  Events: (none)
  Gap: No referral program at all

## All Discovered Events
{complete event table from Phase 1}

## Gap Analysis
{complete gap checklist from Phase 4}

## Recommended Actions
1. {Highest-priority gap to fix}
2. {Second priority}
3. {Third priority}
```

## Phase 6: Output

Present the funnel visualization to the user with health scores and the top 3 recommended actions.

```
AARRR Funnel Map Complete -- {date}

| Stage       | Score | Events Found | Critical Gaps |
|-------------|-------|-------------|---------------|
| Acquisition | 72    | 5           | CAPI missing |
| Activation  | 58    | 3           | No completion tracking |
| Retention   | 35    | 1           | No email sequences |
| Revenue     | 65    | 4           | No upgrade tracking |
| Referral    | 12    | 0           | No referral program |

Total events discovered: 42 across 4 tracking sources

Top 3 priorities:
1. Add retention email sequences (Retention +20 pts est.)
2. Build referral program (Referral +40 pts est.)
3. Add onboarding completion tracking (Activation +10 pts est.)

Funnel saved: .gtm/funnel/funnel-{date}.json
Funnel map: .gtm/funnel/funnel-{date}.md

Next:
- Run /gtm-diagnose for full bottleneck analysis with revenue impact
- Run /gtm-email to create retention email sequences
- Run /gtm-referral to design a referral program
```

## Error Handling

- **No codebase access**: If the project codebase cannot be scanned (e.g., command run outside a project), tell the user to run this command from the project root. STOP.
- **No tracking found**: If zero events are discovered, report: "No analytics or tracking events found in the codebase. The product has no funnel instrumentation. Start by running `/gtm-setup` to configure PostHog and Meta Pixel." Score all stages at 0.
- **Partial tracking**: If only some stages have tracking, score the rest as 0 and flag them as critical gaps.
- **Large codebase**: If the codebase is very large (>2000 files), focus the scan on `src/`, `app/`, `pages/`, and `supabase/functions/` directories to keep scan time reasonable.
