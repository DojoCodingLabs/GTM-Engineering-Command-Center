# Attribution Models -- When to Use Each Model and Implementation

## Why Attribution Matters

Attribution answers: "Which marketing activities drove this conversion?" The answer changes dramatically depending on which model you use. Wrong attribution = wrong budget allocation = wasted money.

## Attribution Model Comparison

### First-Touch Attribution

```
Definition: 100% credit goes to the first touchpoint in the customer journey.

Example:
  Touch 1: Google Search → Blog post (GETS 100% CREDIT)
  Touch 2: Meta retargeting ad → Landing page
  Touch 3: Email drip → Signs up
  Touch 4: Direct → Purchases

What it answers: "What channels bring new people into the funnel?"

When to use:
  - You want to understand top-of-funnel acquisition
  - You're investing in awareness channels and need to justify them
  - Your funnel is short (< 3 touchpoints on average)
  - You're comparing awareness channels against each other

When NOT to use:
  - For budget allocation across the full funnel
  - When retargeting and email drive most conversions
  - For ROAS calculations (over-credits awareness, under-credits conversion)

Implementation:
  - Store the first UTM parameters with the user record at signup
  - Never overwrite first_touch UTM when user returns via new source
  - PostHog: use $initial_utm_source person property
```

### Last-Touch Attribution

```
Definition: 100% credit goes to the last touchpoint before conversion.

Example:
  Touch 1: Google Search → Blog post
  Touch 2: Meta retargeting ad → Landing page
  Touch 3: Email drip → Signs up
  Touch 4: Direct → Purchases (GETS 100% CREDIT)

What it answers: "What channels close deals?"

When to use:
  - Default for most small businesses (simplest to implement)
  - You want to optimize the bottom of the funnel
  - Your conversion event is the immediate goal (not long-term value)
  - Platform-reported conversions use last-touch (or last-click variant)

When NOT to use:
  - When awareness channels are critical (they'll be invisible)
  - When email nurture is a key part of conversion (direct gets credit)
  - For justifying top-of-funnel investment

Implementation:
  - Store the most recent UTM parameters at time of conversion
  - PostHog: filter by UTM properties on the conversion event itself
  - Platform attribution (Meta, Google) uses this by default
```

### Last Non-Direct Touch

```
Definition: 100% credit to the last touchpoint that wasn't direct/organic.

Example:
  Touch 1: Google Search → Blog post
  Touch 2: Meta retargeting ad → Landing page
  Touch 3: Email drip → Signs up (GETS 100% CREDIT)
  Touch 4: Direct → Purchases

What it answers: "What marketing effort actually drove the conversion?"

When to use:
  - Best default for most SaaS companies
  - Filters out "direct" visits that are actually returning from a marketing touchpoint
  - Better reflects marketing's actual contribution than pure last-touch

When NOT to use:
  - When direct traffic is genuinely a conversion channel (branded recognition)
  - When you need to credit awareness channels

Implementation:
  - Store UTM params on every visit, but only update "attribution" when source is not "direct"
  - If conversion happens on a direct visit, credit the previous non-direct visit
```

### Linear Attribution

```
Definition: Equal credit distributed across all touchpoints.

Example (4 touchpoints, $100 revenue):
  Touch 1: Google Search → $25 credit
  Touch 2: Meta retargeting → $25 credit
  Touch 3: Email drip → $25 credit
  Touch 4: Direct → $25 credit

What it answers: "What's the overall contribution of each channel?"

When to use:
  - Longer sales cycles (B2B, 30+ days)
  - Multiple channels are genuinely important
  - You want a balanced view without bias toward first or last
  - Reporting to stakeholders who manage different channels

When NOT to use:
  - Short sales cycles (under 7 days, 1-2 touchpoints)
  - When one channel is clearly dominant
  - For tactical budget decisions (too democratic, doesn't identify winners)

Implementation:
  - Track all touchpoints with timestamps
  - At conversion, divide revenue equally among all touchpoints
  - Requires a touchpoint log per user (PostHog session data or custom table)
```

### Time-Decay Attribution

```
Definition: More credit goes to touchpoints closer to conversion.

Example (4 touchpoints, $100 revenue, 7-day half-life):
  Touch 1 (28 days ago): Google Search → $6 credit
  Touch 2 (14 days ago): Meta retargeting → $13 credit
  Touch 3 (3 days ago): Email drip → $31 credit
  Touch 4 (today): Direct → $50 credit

What it answers: "What's the most impactful recent activity?"

When to use:
  - Long sales cycles with many touchpoints
  - You believe recent interactions are more influential than older ones
  - B2B with 30-90 day cycles
  - Seasonal businesses where timing matters

When NOT to use:
  - Short sales cycles (not enough time difference between touches)
  - When awareness is critical and needs credit (awareness touches are oldest)

Implementation:
  - Track all touchpoints with timestamps
  - Apply exponential decay function: credit = base * 2^(-days_ago/half_life)
  - Typical half-life: 7 days (B2C), 14 days (B2B), 30 days (enterprise)
```

### Data-Driven (Algorithmic) Attribution

```
Definition: Machine learning assigns credit based on actual conversion data.

How it works:
  - Analyzes thousands of conversion paths
  - Identifies which touchpoints actually impact conversion probability
  - Assigns credit proportional to measured impact

What it answers: "What is each channel's actual causal impact on conversion?"

When to use:
  - 300+ conversions per month (minimum for reliable ML)
  - Available as Google Ads default attribution model
  - When you have sufficient data for statistical significance
  - For mature ad accounts with multi-channel data

When NOT to use:
  - Fewer than 300 conversions/month (insufficient data for ML)
  - New products or channels (no historical data to learn from)
  - When you need a simple, explainable model for stakeholders

Implementation:
  - Google Ads: select "Data-driven" as conversion action attribution model
  - For custom: requires significant engineering (Markov chain or Shapley value models)
  - PostHog does not have built-in algorithmic attribution (use Google's)
```

## Attribution Model Selection Guide

```
Monthly conversions < 50?
  → Use Last Non-Direct Touch (simplest, most practical)

Monthly conversions 50-300?
  → Use Linear or Time-Decay (balanced view)

Monthly conversions 300+?
  → Use Data-Driven (Google Ads) + Last Non-Direct Touch (internal)

Sales cycle < 7 days?
  → Last-Touch or Last Non-Direct Touch

Sales cycle 7-30 days?
  → Linear or Time-Decay (7-day half-life)

Sales cycle 30-90 days?
  → Time-Decay (14-day half-life) or Linear

Reporting to CMO/board?
  → Linear (fair to all channels) or Data-Driven (most accurate)

Reporting for budget allocation?
  → Last Non-Direct Touch (actionable) or Data-Driven (if available)
```

## Multi-Platform Attribution Challenges

### The Double-Counting Problem

```
Meta reports 100 conversions from Meta ads.
Google reports 80 conversions from Google ads.
Your actual total conversions: 120.

Why? Both platforms claim credit for the same conversions (different touchpoints in the same journey).

Solution:
  1. Use a centralized attribution source (PostHog, your own database)
  2. Platform-reported numbers are useful for optimization within that platform
  3. For total budget allocation, use your centralized data
  4. Never add platform-reported conversions together (sum > actual)
```

### The iOS Privacy Problem

```
Since iOS 14.5 (App Tracking Transparency):
  - ~30-40% of iOS users opt out of tracking
  - Meta Pixel loses visibility on these users
  - Conversion reporting is delayed and modeled
  - Attribution window shortened to 7 days (was 28)

Mitigation:
  1. Implement Meta CAPI (server-side tracking, not affected by iOS)
  2. Use Google Enhanced Conversions
  3. Track conversions server-side (your database is the source of truth)
  4. Accept that platform-reported conversions are estimates, not exact counts
  5. Use incrementality testing (on/off tests) to measure true channel impact
```

## UTM Implementation for Attribution

```
Every marketing touchpoint must have UTM parameters:

Standard UTM fields:
  utm_source: The platform (meta, google, email, linkedin)
  utm_medium: The channel type (paid, cpc, organic, email)
  utm_campaign: The campaign name (spring-launch-2026)
  utm_content: The creative/variant (video-v1, carousel-a)
  utm_term: The keyword (for search only)

Storage:
  1. Capture UTMs on every page visit (first AND last touch)
  2. Store with user record (first_utm_source, last_utm_source)
  3. Store full touchpoint log for multi-touch analysis
  4. Never overwrite first-touch data

PostHog automatically captures:
  $utm_source, $utm_medium, $utm_campaign, $utm_content, $utm_term
  $initial_utm_source (first touch — person property, set once)
```
