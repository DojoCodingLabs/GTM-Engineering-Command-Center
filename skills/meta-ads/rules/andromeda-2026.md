# Andromeda Retrieval System & Entity Clustering -- Deep Dive (April 2026)

## How Andromeda Works

Andromeda is Meta's ad retrieval system that replaced the legacy interest-based matching engine. It uses computer vision and behavioral modeling to match ads to users across 3B+ daily active people.

### The Pipeline

```
Step 1: ENTITY SCANNING (Computer Vision)
  Every ad creative is scanned and assigned an Entity ID based on:
  - Visual pixels (composition, colors, faces, objects)
  - Hook pacing (first 3 seconds of video, visual rhythm)
  - Emotional tone (positive, urgent, aspirational, fear-based)
  - Text overlays (text detected in images/videos, NOT the ad copy fields)
  Result: Each visually unique creative = 1 Entity ID

Step 2: RETRIEVAL (Andromeda)
  When a user opens Facebook/Instagram, Andromeda selects ~1,000 candidate ads:
  - Scans all active Entity IDs across all advertisers
  - Matches entities to user's latent intent signals (browsing history,
    engagement patterns, purchase behavior, cross-app activity)
  - Each Entity ID gets ONE retrieval ticket per auction
  Result: ~1,000 candidate ads pulled from millions

Step 3: RANKING (ARM - Adaptive Ranking Model)
  ARM ranks the ~1,000 candidates based on predicted conversion probability:
  - Reads advertiser's conversion data quality FIRST (EMQ score)
  - Then evaluates creative relevance to this specific user
  - Higher EMQ = deeper ARM model version = better ranking signals
  Result: Final ranked list, top ads enter the auction

Step 4: AUCTION
  Standard second-price auction with bid strategy applied:
  - Highest Volume (Lowest Cost): No ceiling, maximize conversions
  - Cost Cap: Caps average CPA, may limit delivery
  - Bid Cap: Hard ceiling per auction, maximum control
  Result: Winning ad shown to the user
```

## Entity Clustering Mechanics

Entity Clustering is the most impactful change Andromeda introduced. It groups visually similar ads as a single retrieval entity.

### What Creates a UNIQUE Entity ID

Each of these produces a genuinely different Entity ID:
- **Different image** (not a crop or filter -- a fundamentally different visual)
- **Different video** (different footage, different hook, different pacing)
- **Different format** (static image vs. video vs. carousel = 3 different entity types)
- **Different visual composition** (person vs. product-only, dark vs. light, close-up vs. wide)
- **Different text overlay in the image/video** (Andromeda reads baked-in text, not ad copy fields)

### What Does NOT Create a Unique Entity ID

These are all treated as the SAME entity:
- Same image with different ad copy text (bodies, titles, descriptions)
- Same image with different color filter or slight crop
- Same video with different thumbnail
- Same creative with different targeting or budget

### The Math

```
50 ads with same image + different copy = 1 Entity ID = 1 retrieval ticket
50 ads with different images + same copy = 50 Entity IDs = 50 retrieval tickets

Which strategy gets 50x more chances in the auction? The second one.
```

### Required Entity Volume

Top performers maintain **50-200 visually distinct Entity IDs active per week**. This gives Andromeda enough creative diversity to find winning audience pockets across the full 3B+ user base.

```
Minimum viable: 50 Entity IDs/week (small advertisers, <$500/day)
Growth target: 100-150 Entity IDs/week ($500-$5,000/day)
Scale target: 200+ Entity IDs/week ($5,000+/day)
```

## The 4 Creative Levers for Unique Entity IDs

Each lever produces a fundamentally different visual, guaranteeing a unique Entity ID:

### 1. Persona
WHO is shown in the creative.
- Founder talking to camera
- Customer testimonial
- Employee/team shot
- Product-only (no people)
- UGC-style creator content
- Illustrated character

Each person or visual subject = different entity.

### 2. Messaging
What EMOTION or angle the visual communicates.
- Pain/frustration (before state)
- Transformation (before → after)
- Aspiration (dream outcome)
- Social proof (numbers, logos, crowd)
- Urgency (scarcity, countdown, limited)
- Authority (awards, press, credentials)

Same person + different emotional framing = different visual composition = different entity.

### 3. Hook
The first 3 seconds of video or the dominant visual element of a static ad.
- Text-heavy hook ("Did you know...?")
- Face-to-camera hook (person starts talking immediately)
- Product demo hook (show the product in action)
- Contrast hook (ugly before → beautiful after)
- Pattern interrupt hook (unexpected visual that stops scrolling)

Different hooks = different pacing = different entity.

### 4. Format
The structural format of the ad.
- Static image (1:1, 9:16)
- Short video (15-30 seconds)
- Long video (60-90 seconds)
- Carousel (3-10 cards)
- Collection ad
- Catalog ad (static)
- Video Catalog Ad (different entity type from static catalog)

Each format = guaranteed different entity type.

### Lever Multiplication

```
3 Personas × 3 Messaging angles × 3 Hooks × 4 Formats = 108 unique Entity IDs

This is achievable with a focused creative production sprint.
```

## ARM (Adaptive Ranking Model) -- Deep Dive

ARM is the second stage of the pipeline, and its behavior depends entirely on your conversion data quality.

### How ARM Uses EMQ

```
EMQ 8-10 (Full ARM Model):
  - Cross-device behavioral matching
  - Purchase intent prediction from browsing patterns
  - Lookalike expansion to untapped audience segments
  - Real-time bid optimization based on user's session context
  - Deep funnel prediction (will this user LTV > $X?)

EMQ 5-7 (Partial ARM Model):
  - Basic demographic matching
  - Interest-based predictions
  - Limited cross-device tracking
  - Standard bid optimization
  - No deep funnel prediction

EMQ <5 (Surface ARM Model):
  - Broad demographic targeting only
  - No behavioral matching
  - No lookalike expansion
  - Essentially manual targeting performance
```

### Critical Insight: Identical Creative, Different Results

Two advertisers running the EXACT same creative will get completely different results if their EMQ scores differ. The advertiser with EMQ 9 gets the full ARM model ranking their creative. The advertiser with EMQ 5 gets surface-level ranking. The creative is identical -- the data quality determines the outcome.

**This means:** Fixing your CAPI/EMQ is a higher-ROI activity than creating new creative, if your EMQ is below 7.

## Impact Data (Confect.io Study)

The most comprehensive study of Andromeda's impact on ad performance:

### Study Parameters
- **$834M in ad spend** analyzed
- **3,014 advertisers** across verticals
- **1M+ ads** evaluated
- **115.7B impressions** measured
- Period: Q4 2025 through Q1 2026 (Andromeda rollout)

### Results by Price Segment
| Segment | ROAS Change | Why |
|---------|-------------|-----|
| Mid-priced products | +12-18% | Best Entity diversity, clear product differentiation |
| Budget products | +3-7% | High competition, hard to differentiate visually |
| Luxury products | -17% | Andromeda favors broad appeal; luxury is niche by definition |
| Discount-heavy | -35% | Entity IDs get clustered with competitor discount ads |
| Overall average | -7% | Transition period drag, expected to normalize |

### Key Takeaway
Andromeda rewards advertisers who produce high volumes of visually distinct creative. It penalizes those who rely on audience targeting alone or who produce homogeneous creative.

## Ad Lifecycle Under Andromeda

### The New Lifecycle Curve

```
Performance
    ▲
    │   ╱╲
    │  ╱  ╲
    │ ╱    ╲────────────── plateau/decline
    │╱
    └──────────────────────→ Time
    W1    W2    W3    W4

    Peak: Week 1 (previously weeks 2-3)
    Plateau: Week 2-3 (previously weeks 4-6)
    Decline: Week 3-4 (previously weeks 6-8+)
```

### Implications
- **Creative rotation every 2-4 weeks is mandatory** (previously 6-8 weeks was acceptable)
- Top performers run **395 live ads simultaneously** (Confect.io study)
- Bottom performers run **297 live ads** -- 33% fewer, correlating with lower ROAS
- Your creative production pipeline velocity is now your primary competitive moat

### Production Cadence

```
For $1,000-5,000/day spend:
  - Produce 10-20 new visually distinct creatives per week
  - Retire 10-20 fatigued creatives per week
  - Maintain 50-100 active Entity IDs at all times

For $5,000-50,000/day spend:
  - Produce 30-50 new creatives per week
  - Maintain 150-300 active Entity IDs at all times
  - Dedicated creative team or agency relationship required
```

## Post-Click Experience Under Andromeda

Andromeda doesn't just change ad delivery -- it changes what happens after the click.

### Findings
- **Broad category landing pages:** -24% ROAS (user lands on a general page, has to navigate to find what the ad promised)
- **Specific product pages:** Gained ROAS (user sees exactly what the ad showed, can make an immediate decision)
- **Users need immediate decision clarity** -- Andromeda delivers ads to users with high latent intent, but that intent is fragile. If the landing page doesn't match the ad's promise within 3 seconds, the user bounces.

### Landing Page Rules
1. **Landing page must match the ad's visual** -- If the ad shows a specific product, the landing page must show that product above the fold
2. **One CTA per landing page** -- Don't give Andromeda-delivered users a choice. They clicked for a reason; give them the action.
3. **Load time under 2 seconds** -- Andromeda users have higher intent but lower patience. Every second above 2s costs 7% conversion rate.
4. **Mobile-first** -- 78% of Andromeda-delivered clicks are mobile. If your landing page isn't optimized for thumb scrolling, you're losing most of your traffic.