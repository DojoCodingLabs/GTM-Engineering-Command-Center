---
name: cross-channel-logic
description: Cross-channel GTM orchestration — channel sequencing, attribution models, retargeting chains, multi-touch journeys
---

# Cross-Channel GTM Logic

Orchestrate multi-channel go-to-market sequences that coordinate paid ads, organic search, email, and social across the customer journey. This skill covers channel sequencing, attribution modeling, and retargeting chain construction.

## The Multi-Channel Reality

No customer converts on a single touchpoint. The average SaaS conversion requires 6-8 touches across 2-3 channels over 14-30 days:

```
Typical Journey:
  Touch 1: Google Search (informational query) → Blog post
  Touch 2: Meta retargeting ad → Landing page (bounces)
  Touch 3: Google Search (branded query) → Homepage
  Touch 4: Email drip (captured from blog) → Feature highlight
  Touch 5: Meta retargeting ad → Landing page (signs up for trial)
  Touch 6: Email onboarding sequence → Activation
  Touch 7: Email trial-ending → Converts to paid
```

## Channel Roles

Each channel plays a specific role in the journey. Using a channel for the wrong role wastes budget.

| Channel | Primary Role | Secondary Role | Poor Use |
|---------|-------------|---------------|----------|
| Google Search (non-brand) | Acquisition (intent capture) | Awareness | Retargeting |
| Google Search (branded) | Conversion (high intent) | Measurement | Awareness |
| Meta Ads (prospecting) | Awareness, acquisition | Interest generation | Direct conversion |
| Meta Ads (retargeting) | Conversion, nurture | Re-engagement | Cold prospecting |
| Email (drip) | Nurture, conversion | Retention, reactivation | Cold acquisition |
| Email (newsletter) | Retention, thought leadership | Brand awareness | Direct selling |
| SEO Content | Acquisition (organic) | Authority building | Quick conversion |
| YouTube | Awareness, education | Trust building | Direct response |
| LinkedIn (organic) | Authority, recruitment | B2B leads | Consumer acquisition |
| LinkedIn (ads) | B2B lead gen | Account-based marketing | Consumer products |

## Channel Sequencing Templates

### Template 1: Content-Led Acquisition (Low Budget)

Best for: Early-stage, <$2K/month ad spend, strong content team.

```
Phase 1 (Weeks 1-4): SEO Content
  Publish 8-12 high-intent blog posts targeting long-tail keywords
  ↓
Phase 2 (Weeks 5-8): Email Capture
  Add lead magnets to top-performing blog posts
  Build welcome + nurture email sequences
  ↓
Phase 3 (Weeks 9-12): Paid Amplification
  Boost top blog posts with Meta Ads ($10-20/day)
  Retarget blog readers with conversion-focused ads
  ↓
Phase 4 (Ongoing): Flywheel
  SEO drives organic → Email nurtures → Meta retargets → Conversion
```

### Template 2: Paid-First Acquisition (Growth Budget)

Best for: Growth-stage, $5K+/month ad spend, need fast results.

```
Week 1-2: Google Search
  Launch branded + high-intent non-branded search campaigns
  Capture bottom-of-funnel demand
  ↓
Week 3-4: Meta Prospecting
  Launch interest-based and lookalike campaigns on Meta
  Drive awareness and landing page visits
  ↓
Week 5-6: Meta Retargeting
  Retarget website visitors from both Google and Meta
  Retarget email list with conversion-focused creative
  ↓
Week 7-8: Email Integration
  Capture trial signups into activation email sequence
  Non-converters enter nurture sequence → feed back into retargeting
  ↓
Ongoing: Full Loop
  Google (intent) → Meta (awareness) → Meta (retargeting) → Email (nurture) → Conversion
```

### Template 3: Community-Led Growth

Best for: Developer tools, open source, community-driven products.

```
Phase 1: Content + Community
  Publish technical tutorials + documentation
  Build Discord/Slack community
  ↓
Phase 2: Organic Social
  Share content on Twitter/X, LinkedIn, Reddit, Hacker News
  Community members amplify
  ↓
Phase 3: Email Digest
  Weekly community highlights email
  Feature spotlights, user stories
  ↓
Phase 4: Light Paid
  Retarget website visitors (Google Display + Meta)
  Promote community events with paid social
```

## Cross-Channel Data Flow

```
                    ┌─────────────┐
                    │  PostHog     │
                    │  (behavior)  │
                    └──────┬──────┘
                           │
    ┌──────────┬───────────┼───────────┬──────────┐
    │          │           │           │          │
┌───┴───┐ ┌───┴───┐ ┌─────┴────┐ ┌───┴───┐ ┌───┴───┐
│ Meta  │ │Google │ │  Email   │ │Stripe │ │  SEO  │
│  Ads  │ │  Ads  │ │Provider  │ │       │ │ (GSC) │
└───────┘ └───────┘ └──────────┘ └───────┘ └───────┘
```

### UTM Strategy for Attribution

Every paid touchpoint must carry UTM parameters:

```
utm_source:   Platform (meta, google, email, linkedin)
utm_medium:   Channel type (paid, cpc, social, email, organic)
utm_campaign: Campaign name (spring-launch-2026, retargeting-q2)
utm_content:  Creative variant (video-a, carousel-b, email-day3)
utm_term:     Keyword (for search only)
```

### UTM Naming Convention

```
[source]_[medium]_[campaign-name]_[content-variant]

Examples:
  meta_paid_bootcamp-launch-q2_video-testimonial-v1
  google_cpc_brand-search_exact-match
  email_drip_welcome-sequence_day3-feature
  linkedin_paid_enterprise-demo_case-study-a
```

## Budget Allocation Across Channels

### Stage-Based Allocation

| Company Stage | Search | Meta/Social | Email | SEO/Content |
|---------------|--------|-------------|-------|-------------|
| Pre-Product-Market Fit | 40% | 30% | 10% | 20% |
| Post-PMF, Pre-Scale | 30% | 35% | 15% | 20% |
| Growth | 25% | 35% | 20% | 20% |
| Scale | 20% | 30% | 25% | 25% |

These are starting points. Adjust based on CAC by channel after 30+ days of data.
