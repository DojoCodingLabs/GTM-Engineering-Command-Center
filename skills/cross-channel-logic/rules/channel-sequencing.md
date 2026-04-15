# Channel Sequencing -- 5 Cross-Channel Templates with Implementation Details

## Sequence Design Principles

```
1. Each channel should serve ONE primary role in the sequence
2. Handoffs between channels must be tracked (UTM parameters)
3. Every sequence has a measurable goal at each stage
4. Sequences should adapt based on user behavior (not rigid timelines)
5. Budget allocation follows the sequence priority (don't underfund critical steps)
```

## Sequence 1: Google Search → Meta Retargeting → Email Nurture

**Best for**: B2B SaaS, high-intent keywords exist, $3K-10K/month budget

```
Stage 1: Google Search (Capture Intent)
  Budget: 50% of total
  Campaigns:
    - Branded search (exact match on brand name)
    - Non-branded high-intent ("best [category]", "[category] for [use case]")
    - Competitor terms ("[competitor] alternative")
  Goal: Drive traffic to landing page, capture signups
  Tracking: GCLID capture on landing page, GTM conversion tag

  ↓ Visitor lands but doesn't convert ↓

Stage 2: Meta Retargeting (Re-engage)
  Budget: 30% of total
  Audiences:
    - Website visitors last 14 days (exclude converters)
    - Landing page visitors who didn't sign up
    - Blog readers who visited pricing page
  Creative: Different angle from search ad (social proof, demo video, case study)
  Goal: Bring visitors back to convert
  Tracking: Meta Pixel custom audience + UTM source=meta&medium=retargeting

  ↓ User signs up (from search or retargeting) ↓

Stage 3: Email Nurture (Activate + Convert)
  Budget: 20% of total (email provider costs + time)
  Sequence:
    - Day 0: Welcome + quick start guide
    - Day 2: Key feature tutorial
    - Day 5: Customer success story
    - Day 7: Activation check (branch based on behavior)
    - Day 10-14: Trial-to-paid sequence (if applicable)
  Goal: Activate user, convert to paid
  Tracking: Email opens/clicks, PostHog activation events

Implementation timeline: 2-3 weeks
Expected CPA: 30-50% lower than single-channel
```

## Sequence 2: Content/SEO → Email Capture → Meta Lookalike

**Best for**: Early-stage, limited budget (<$3K/month), strong content capability

```
Stage 1: Content + SEO (Build Audience)
  Budget: 20% (content creation, no paid spend)
  Activities:
    - Publish 2-4 SEO-optimized blog posts per month
    - Target long-tail, informational keywords
    - Include lead magnets (checklists, templates, mini-courses)
  Goal: Organic traffic + email list growth
  Tracking: Google Search Console rankings, PostHog pageviews

  ↓ Reader engages with content ↓

Stage 2: Email Capture (Convert Readers to Leads)
  Budget: 10% (email tooling)
  Mechanisms:
    - Exit-intent popup on blog posts ("Get the full guide")
    - Inline content upgrades (code snippet → "Download complete template")
    - Newsletter signup in blog sidebar/footer
    - Gated resources (ebooks, whitepapers, tool access)
  Sequence:
    - Day 0: Deliver lead magnet
    - Day 2: Related educational content
    - Day 5: Product introduction ("Here's how we solve this")
    - Day 7: Social proof + CTA
    - Day 10: Direct conversion offer
  Goal: Build email list of qualified leads
  Tracking: Email signups, sequence completion, activation

  ↓ Email list reaches 1,000+ contacts ↓

Stage 3: Meta Lookalike (Scale with Paid)
  Budget: 70% (activate only when list is ready)
  Audiences:
    - Upload email list → Create custom audience
    - Lookalike 1% of email subscribers (best quality)
    - Lookalike 1% of converters/paid users (if available)
  Creative: Same content angles that worked organically
  Goal: Find more people like your organic audience, at scale
  Tracking: Meta Pixel, UTM params, PostHog attribution

Implementation timeline: 3-6 months (content takes time)
Expected CPA: 40-60% lower than cold Meta ads (better audience quality)
```

## Sequence 3: Meta Prospecting → Google Display → Email Activation

**Best for**: Consumer apps, visual products, strong creative, $5K-20K/month budget

```
Stage 1: Meta Prospecting (Generate Awareness)
  Budget: 50% of total
  Campaigns:
    - Interest-based targeting (3-5 ad sets with different interests)
    - Lookalike audiences (if data available)
    - Broad targeting with Advantage+ (let Meta's algorithm find users)
  Creative: Video ads (60-90 seconds), carousel ads, UGC-style content
  Goal: Drive landing page visits, capture pixel data
  Tracking: Meta Pixel events (ViewContent, Lead, CompleteRegistration)

  ↓ Non-converters need another touchpoint ↓

Stage 2: Google Display Retargeting (Multi-Platform Presence)
  Budget: 20% of total
  Audiences:
    - Remarketing list from website visitors (all)
    - Similar audiences from converter list
  Placements: Google Display Network (3M+ websites)
  Creative: Responsive display ads matching Meta creative angles
  Goal: Stay top-of-mind, reinforce brand across multiple platforms
  Tracking: Google Ads conversion tag, UTM params

  ↓ User signs up from any touchpoint ↓

Stage 3: Email Activation (Convert Signups to Active Users)
  Budget: 30% (email infrastructure + content)
  Sequence (aggressive, short):
    - Immediate: Welcome + "Start here" CTA
    - 6 hours: "Quick win" tutorial (if not activated)
    - Day 1: Video walkthrough
    - Day 2: Social proof + community invite
    - Day 3: "Need help?" personal email
  Goal: Activate within 72 hours
  Tracking: PostHog activation events, email engagement

Implementation timeline: 2 weeks for initial launch
Expected CPA: Higher than search (awareness channel), but builds retargeting audiences
```

## Sequence 4: LinkedIn → Email → Meta Retargeting (B2B Enterprise)

**Best for**: B2B with $5K+ ACV, decision-makers on LinkedIn, $10K+/month budget

```
Stage 1: LinkedIn Ads (Reach Decision-Makers)
  Budget: 40% of total
  Campaigns:
    - Sponsored content (thought leadership articles)
    - Lead gen forms (capture leads without leaving LinkedIn)
    - Message ads to specific job titles (use sparingly)
  Targeting:
    - Job title: CTO, VP Engineering, Director of Engineering
    - Company size: 50-500 employees
    - Industry: Technology, Financial Services
  Goal: Generate Marketing Qualified Leads (MQLs)
  Tracking: LinkedIn Insight Tag, UTM params, lead gen form submissions

  ↓ Lead captured (email from LinkedIn lead form or website) ↓

Stage 2: Email Nurture (Educate and Qualify)
  Budget: 20% of total
  Sequence (longer cycle, B2B):
    - Day 0: Thank you + case study download
    - Day 3: Industry-specific content
    - Day 7: ROI calculator or benchmark report
    - Day 14: Webinar or demo invitation
    - Day 21: Direct outreach from sales (if engaged)
    - Day 30: Follow-up with new content
  Goal: Move leads from MQL to SQL
  Tracking: Email engagement, demo bookings, pipeline creation

  ↓ Engaged leads who haven't booked demo ↓

Stage 3: Meta Retargeting (Multi-Channel Presence)
  Budget: 40% of total
  Audiences:
    - Upload email list of engaged leads → custom audience
    - Website visitors from LinkedIn traffic
  Creative: Case studies, demo previews, social proof (enterprise logos)
  Goal: Stay visible while email nurture works, drive demo bookings
  Tracking: Meta Pixel, UTM params

Implementation timeline: 3-4 weeks
Expected CPA: $100-500 per MQL (B2B Enterprise), $500-2000 per SQL
```

## Sequence 5: Community → Organic Social → Paid Amplification (PLG)

**Best for**: Developer tools, open-source, product-led growth, community-driven

```
Stage 1: Community Building (Foundation)
  Budget: 10% (tooling only, mostly human effort)
  Activities:
    - Discord/Slack community (answer questions, share updates)
    - GitHub presence (issues, PRs, documentation)
    - Technical blog (tutorials, deep dives)
    - Stack Overflow answers (seed authority)
  Goal: Build 500+ engaged community members
  Tracking: Community member count, DAU, message volume

  ↓ Community reaches critical mass ↓

Stage 2: Organic Social Distribution
  Budget: 10% (content creation)
  Channels:
    - Twitter/X: Dev threads, product updates, memes
    - Reddit: Genuine contributions to relevant subreddits (not promotional)
    - Hacker News: Launch posts, Show HN, technical articles
    - YouTube: Tutorial videos, live coding sessions
    - LinkedIn: Professional dev content
  Strategy: Community members amplify content naturally
  Goal: Viral moments driving signups
  Tracking: Social referral traffic, UTM params, PostHog attribution

  ↓ Identified high-performing content/angles ↓

Stage 3: Paid Amplification (Scale What Works)
  Budget: 80% (activate only after organic validation)
  Channels:
    - Meta: Boost top-performing organic posts
    - Google: Target search terms discovered from community questions
    - YouTube: Promote best tutorial videos
    - Twitter/X ads: Amplify viral dev threads
  Creative: Same content that performed organically (proven messaging)
  Goal: 10x the reach of proven organic content
  Tracking: Full UTM suite, ad platform pixels, PostHog

Implementation timeline: 3-9 months (community takes time)
Expected CPA: Lowest of all sequences (organic validation reduces waste)
```

## Sequence Selection Guide

```
Budget < $3K/month → Sequence 2 (Content-led) or Sequence 5 (Community)
Budget $3K-10K/month → Sequence 1 (Search + Retargeting) or Sequence 3 (Meta + Display)
Budget $10K+/month → Sequence 4 (LinkedIn B2B) or run Sequence 1 + 3 simultaneously

B2B with ACV > $5K → Sequence 4 (LinkedIn-led)
B2C or low ACV → Sequence 3 (Meta-led) or Sequence 5 (Community-led)
Strong content team → Sequence 2 (Content-led) feeding into Sequence 1
Developer audience → Sequence 5 (Community-led)
Visual product → Sequence 3 (Meta-led with video)
```
