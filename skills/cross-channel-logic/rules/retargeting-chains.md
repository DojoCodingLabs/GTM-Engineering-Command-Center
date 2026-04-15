# Retargeting Chains -- Building Audiences Across Meta, Google, and Email

## Retargeting Architecture

```
Retargeting works by building audiences from known user behaviors,
then showing those audiences specific ads designed for their stage.

Data Flow:
  Website Visit (PostHog + Pixel)
    → Custom Audience (Meta/Google)
      → Retargeting Ad (stage-appropriate creative)
        → Conversion or Next Stage

The chain progresses users through increasingly specific audiences
with increasingly direct messaging.
```

## Meta Custom Audiences

### Audience Types

| Type | Source | Refresh | Min Size |
|------|--------|---------|----------|
| Website Custom | Meta Pixel events | Real-time | 100 |
| Customer List | Email/phone upload | Manual upload | 100 |
| Video Viewers | Video ad engagement | Automatic | 100 |
| Lead Form | Lead form openers/submitters | Automatic | 100 |
| App Activity | App SDK events | Automatic | 100 |
| Instagram Engagement | Profile/post interactions | Automatic | 100 |
| Facebook Page | Page followers/engagers | Automatic | 100 |

### Website Custom Audience (Pixel-Based)

```
API: POST /act_XXXXX/customaudiences
{
  "name": "Website Visitors - Last 30 Days",
  "subtype": "WEBSITE",
  "rule": {
    "inclusions": {
      "operator": "or",
      "rules": [
        {
          "event_sources": [{"id": "PIXEL_ID", "type": "pixel"}],
          "retention_seconds": 2592000,
          "filter": {
            "operator": "and",
            "filters": [
              {
                "field": "url",
                "operator": "i_contains",
                "value": "/"
              }
            ]
          }
        }
      ]
    }
  }
}
```

### Audience Segmentation Strategy

Build these audiences in order of specificity:

```
Tier 1 (Broadest): All website visitors
  - Last 180 days
  - Exclude converters
  - Use for: broad retargeting, brand reinforcement
  - Creative: educational content, product overview

Tier 2: Engaged visitors
  - Visited 2+ pages OR spent 30+ seconds
  - Last 90 days, exclude converters
  - Use for: mid-funnel retargeting
  - Creative: specific features, social proof

Tier 3: High-intent visitors
  - Visited pricing page OR started signup
  - Last 30 days, exclude converters
  - Use for: bottom-funnel retargeting
  - Creative: urgency, special offers, testimonials

Tier 4: Cart/signup abandoners
  - Started checkout/signup but didn't complete
  - Last 14 days
  - Use for: recovery campaigns
  - Creative: "Forgot something?", incentive to complete

Tier 5: Recent converters (for upsell)
  - Purchased or signed up in last 30 days
  - Exclude from acquisition campaigns
  - Use for: upsell, cross-sell, community building
  - Creative: advanced features, upgrade offers
```

### Customer List Upload

```
Upload hashed email/phone data for custom audiences:

API: POST /act_XXXXX/customaudiences
{
  "name": "Email List - Active Subscribers",
  "subtype": "CUSTOM",
  "customer_file_source": "USER_PROVIDED_ONLY"
}

Then add users:
POST /AUDIENCE_ID/users
{
  "payload": {
    "schema": ["EMAIL_SHA256"],
    "data": [
      ["5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"],
      ["d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"]
    ]
  }
}

Rules:
  - Emails MUST be SHA256 hashed (lowercase, trimmed)
  - Phone numbers must include country code
  - Minimum 100 records for audience to populate
  - Match rate typically 30-60% (not all emails match Meta accounts)
  - Refresh monthly to keep audience current
```

### Lookalike Audiences from Custom Audiences

```
Create lookalikes from your best-performing audiences:

API: POST /act_XXXXX/customaudiences
{
  "name": "Lookalike 1% - Paid Customers (CO)",
  "subtype": "LOOKALIKE",
  "origin_audience_id": "SOURCE_AUDIENCE_ID",
  "lookalike_spec": {
    "ratio": 0.01,
    "country": "CO"
  }
}

Lookalike percentages:
  1% → Most similar to source, smallest audience, highest quality
  2% → Slightly broader, still good quality
  3-5% → Broader reach, lower precision
  5-10% → Very broad, use with strong creative and smart bidding

Source audience priority (best to worst):
  1. Paying customers (highest value signal)
  2. Trial users who activated (demonstrated product interest)
  3. All signups (includes non-activators, lower signal)
  4. Website visitors (weakest signal, largest source)

Minimum source size: 100 (1,000+ recommended for quality)
```

## Google Ads Remarketing Lists

### Remarketing from Google Ads Tag

```
Google automatically builds remarketing lists from your tag:
  - All website visitors
  - Specific page visitors (URL rules)
  - Converters (for similar audiences and exclusions)

Create custom lists via Google Ads:
  Audience Manager > Your Data Segments > New Segment

Rules:
  - "Visitors of a page" with URL contains "/pricing"
  - "Visitors of a page" with URL contains "/signup" 
    AND NOT "Visitors of a page" with URL contains "/thank-you"
  - Membership duration: 30, 60, 90, 180, 365 days
```

### RLSA (Remarketing Lists for Search Ads)

```
Show different search ads to people who have already visited your site:

Use cases:
  1. Bid higher for past visitors searching your keywords
     (they already know you, more likely to convert)

  2. Expand to broader keywords for past visitors
     (safe to bid on "coding course" for someone who visited your blockchain page)

  3. Show different ad copy to returners
     "Welcome back - complete your signup" vs "Learn blockchain development"

Implementation:
  - Add remarketing audience to search campaign as "Observation" (bid adjustment)
  - Set +50% to +200% bid adjustment for past visitors
  - OR use as "Targeting" to show ads ONLY to past visitors (powerful for broad keywords)
```

## Cross-Platform Retargeting Chain

### The Full Retargeting Sequence

```
Day 0: User visits from Google Search ad → Cookie by Meta Pixel + Google tag
  Enters: "All Visitors" audience (Meta + Google)

Day 1-3: Meta retargeting ad (social proof creative)
  "Join 4,500 developers building on blockchain"
  Landing: Main landing page

Day 4-7: Google Display retargeting ad (feature highlight)
  Responsive display ad across 3M+ websites
  Landing: Feature-specific landing page

Day 7-14: Meta retargeting ad (urgency/offer creative)
  "Free trial ends in 7 days" or "Limited spots in next cohort"
  Landing: Signup page with offer

Day 14+: Email retargeting (if email captured)
  If email captured but no conversion:
  Send targeted email sequence based on pages visited

Day 30: If no conversion, move to suppression list
  Stop retargeting (avoid fatigue)
  Add to "cold" audience for future reactivation
```

### Frequency Capping

```
Critical: Without frequency caps, retargeting becomes stalking.

Recommended caps:
  Meta: 3-5 impressions per person per week
    Set at ad set level: use "Frequency Cap" in ad set settings
    If not available, monitor frequency metric and pause at 5+

  Google Display: 3-5 impressions per person per day
    Set at campaign level: "Frequency capping" in campaign settings
    Recommended: 3 impressions per day, 15 per week

  Total across platforms: no more than 10 impressions per week
    Hard to enforce across platforms, but monitor and adjust
```

## Audience Exclusion Strategy

```
Every retargeting campaign MUST exclude certain audiences:

Exclude from ALL acquisition/retargeting:
  - Existing paying customers (waste of spend)
  - Recent converters (just signed up, let email handle them)

Exclude from Tier 1 (broad retargeting):
  - People already in Tier 3 or 4 (higher-intent audiences)
  - People who converted (obviously)

Exclude from email retargeting:
  - Unsubscribed users (legal requirement)
  - Users who complained/reported spam

Exclusion implementation:
  Meta: "excluded_custom_audiences" field on ad set targeting
  Google: "Exclusions" in audience targeting
  Email: Suppression list in email provider

The exclusion hierarchy prevents:
  1. Wasting money showing ads to existing customers
  2. Multiple retargeting campaigns competing for the same user
  3. Ad fatigue from over-exposure
```

## Retargeting Creative Strategy

```
The creative MUST match the audience's awareness level:

Tier 1 (All visitors) → Educational/Awareness creative
  - "What is blockchain development?"
  - Blog post promotion
  - Product overview video

Tier 2 (Engaged visitors) → Consideration creative
  - Feature comparisons
  - Customer testimonials
  - "See how Maria learned Solidity in 30 days"

Tier 3 (High-intent visitors) → Conversion creative
  - "Ready to start? Get 20% off your first month"
  - Direct signup CTA
  - Limited-time offer (if genuine)

Tier 4 (Abandoners) → Recovery creative
  - "Forgot something? Your spot is still reserved"
  - Address common objection (pricing, time commitment)
  - Incentive to complete (discount, free month)

Tier 5 (Existing customers) → Expansion creative
  - "Unlock advanced courses"
  - "Invite a friend, get a free month"
  - New feature announcement

NEVER use Tier 3/4 creative for Tier 1 audiences.
NEVER use Tier 1 creative for Tier 4 audiences.
Match the message to the moment.
```

## Measurement

```
Key retargeting metrics:

1. ROAS by retargeting tier:
   Tier 3-4 should have 3-10x ROAS (high intent)
   Tier 1-2 should have 1-3x ROAS (awareness)

2. Incremental conversions:
   Would these users have converted without retargeting?
   Test: pause retargeting for 2 weeks, compare conversion rate
   Expected: 10-30% of retargeting conversions are truly incremental

3. Frequency vs conversion:
   Plot conversion rate by frequency
   Usually: conversions peak at frequency 3-5, drop after 7

4. View-through conversions:
   Users who SAW the ad but didn't click, then converted later
   Include in reporting but weigh at 10-20% of click-through conversions
```
