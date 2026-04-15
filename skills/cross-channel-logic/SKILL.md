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

## TikTok (April 2026)

TikTok has matured into a serious paid acquisition channel, no longer just a brand awareness play.

### Key Metrics
- **CPMs: $4-12** (25-40% cheaper than Meta across most verticals)
- **Engagement: 5x Instagram** on comparable content
- **ROAS: 1.4x median** for DTC ecommerce
- **TikTok Shop GMV Max:** 10%+ conversion rates for products with strong visual appeal

### Spark Ads (The TikTok Advantage)

Spark Ads boost existing organic TikTok content (yours or a creator's) as paid ads. They outperform standard TikTok ads on every metric:
- **142% higher engagement** than standard in-feed ads
- **43% higher conversion rate**
- **4% lower CPM**

Spark Ads preserve the organic post's engagement metrics (likes, comments, shares), creating a compounding effect where paid amplification improves organic reach.

### Best Use Cases
- Visual products with strong "unboxing" or "before/after" potential
- Audiences under 35 (TikTok skews younger than Meta)
- Products that benefit from demonstration or tutorial-style content
- Markets where Meta CPMs are high and TikTok inventory is underpriced

## TikTok --> Meta --> Google Funnel

The dominant cross-platform strategy for 2026. Produces **15-20% lower blended CAC** compared to Meta-only campaigns.

### The Flow

```
TikTok (Discovery)
  Cheap CPMs, high engagement, visual-first content
  → User sees product/brand, engages but doesn't buy
  ↓
Meta (Retargeting)
  Retarget TikTok visitors within 24 hours
  → Social proof, testimonials, direct offer creative
  → Conversion-optimized landing page
  ↓
Google (Intent Capture)
  Branded search captures users who saw TikTok/Meta ads
  → High-intent, ready to buy
  → Lowest CPA of all three channels
```

### Budget Allocation Ramp

**Starting allocation:** 70-75% Meta / 20-25% TikTok / 5% Google
**Scale target:** 40-50% Meta / 40-50% TikTok / 10% Google (as TikTok proves ROI)

Scale TikTok budget gradually as you prove ROAS. Never shift more than 10% of budget between channels in a single week.

## LinkedIn Thought Leader Ads (April 2026)

Thought Leader Ads let you boost an individual's organic LinkedIn post as a paid ad. The performance gap vs. standard LinkedIn ads is massive.

### Performance Data
| Metric | Thought Leader Ads | Standard LinkedIn Ads | Difference |
|--------|-------------------|----------------------|------------|
| Median CTR | 2.68% | 0.42% | 6.4x higher |
| Median CPC | $2.29 | $13.23 | 77% cheaper |
| Engagement | High (comments, shares) | Low (mostly impressions) | Qualitative leap |

### Best Practices
- **Long-form posts: 1,000-1,500 characters** perform best (LinkedIn rewards depth)
- **CTA in the bottom 25%** of the post, not the top (earn attention before asking)
- **Use the founder or subject matter expert's profile**, not the company page
- **Topic: insights and opinions**, not product pitches. The ad looks like organic content.
- Best for: B2B SaaS, professional services, recruiting, thought leadership positioning

## X.com (Twitter)

X.com offers the cheapest CPMs in major social advertising but with a more limited (and polarized) audience.

### Key Facts
- **CPMs: $2-7** (cheapest of all major platforms)
- **560M+ Monthly Active Users**
- **Best verticals:** Crypto/web3, tech, developer tools, fintech, politics
- **Role:** Supplementary channel, not primary. Use for brand awareness and community building.
- **Ad formats:** Promoted posts, video ads, website cards
- Limited targeting compared to Meta -- interest and keyword targeting only, no pixel-based lookalikes

### When to Use X.com
- Your target audience is active on X (tech, crypto, finance, media)
- You need cheap impressions to supplement a Meta/Google primary strategy
- You're running a PR/brand play and want social proof (follower count, engagement)
- You have organic X content that performs well and want to amplify it

## Cross-Platform Creative Reuse

The most efficient creative workflow starts with Meta and cascades winners everywhere.

### The Cascade

```
Step 1: Find winners in Meta Advantage+ testing
  → Run 50-200 creatives, identify top 5-10 by ROAS/CPA
  ↓
Step 2: Adapt winners for other platforms
  → Google Demand Gen: Use winning images/videos as responsive display assets
  → YouTube Shorts: Recut winning Meta video ads to 15-60 seconds
  → TikTok Spark Ads: Reshoot winning concepts as native TikTok content
  → LinkedIn: Adapt winning messaging angles for long-form thought leader posts
  ↓
Step 3: Meta generates creative intelligence
  Winners from Meta tell you which angles, hooks, and visuals resonate.
  Apply those insights to ALL channels, even organic content.
```

### Format Adaptation Guide
| Meta Format | Google Demand Gen | YouTube Shorts | TikTok |
|-------------|------------------|----------------|--------|
| 1:1 Image | Responsive display | N/A | N/A |
| 9:16 Video | Video asset | Direct reuse (trim to 60s) | Reshoot as native |
| Carousel | Discovery carousel | N/A | N/A |
| UGC-style | N/A | Direct reuse | Spark Ad boost |
