---
name: google-ads
description: Google Ads API patterns — campaign types, keyword strategy, conversion tracking, Performance Max, bid strategies
---

# Google Ads API & Campaign Management

Build, launch, and manage Google Ads campaigns programmatically via the Google Ads API. This skill covers Search, Display, Performance Max, conversion tracking, keyword strategy, and bid optimization.

## Campaign Hierarchy

```
Google Ads Account (customer ID: XXX-XXX-XXXX)
  └── Campaign (campaign_type, bidding_strategy, budget)
       └── Ad Group (keywords, targeting, CPC bids)
            └── Ad (responsive search ad, responsive display ad, etc.)
                 └── Extensions (sitelinks, callouts, structured snippets)
```

Every entity is managed via the Google Ads API (`googleads.googleapis.com/vXX/`) using mutate operations.

## Campaign Types

| Type | API Value | Best For |
|------|-----------|----------|
| Search | `SEARCH` | Intent-based acquisition, bottom-of-funnel |
| Display | `DISPLAY_NETWORK` | Awareness, retargeting, broad reach |
| Performance Max | `PERFORMANCE_MAX` | Full-funnel automation, all Google surfaces |
| Video | `VIDEO` | YouTube pre-roll, discovery, awareness |
| Shopping | `SHOPPING` | E-commerce product listings |
| Demand Gen | `DEMAND_GEN` | Discovery, Gmail, YouTube Shorts |
| App | `MULTI_CHANNEL` | App installs across Search, Display, YouTube |

## Performance Max (PMax)

PMax is Google's AI-driven campaign type that runs across all Google surfaces: Search, Display, YouTube, Gmail, Maps, Discover. It requires asset groups instead of traditional ad groups.

### Asset Group Structure

```
Performance Max Campaign
  └── Asset Group (equivalent to ad group)
       ├── Headlines (3-15, max 30 chars each)
       ├── Long Headlines (1-5, max 90 chars)
       ├── Descriptions (2-5, max 90 chars)
       ├── Images (min 3: landscape 1200x628, square 1200x1200, portrait 960x1200)
       ├── Logos (min 1: square 1200x1200, landscape 1200x300)
       ├── Videos (optional but recommended, 10s+ horizontal)
       ├── Final URL
       └── Audience Signals (your targeting hints, not restrictions)
```

### Key PMax Rules

1. **Audience signals are hints, not targeting**: Google uses them as starting points but expands beyond them
2. **Minimum 1 conversion action required**: PMax will not run without conversion tracking
3. **Budget minimum**: $50/day recommended for sufficient learning data
4. **Cannibalization risk**: PMax can steal branded search traffic -- use brand exclusions
5. **Limited reporting**: You see asset-level performance but not keyword-level or placement-level

## Bidding Strategies

| Strategy | API Value | When to Use |
|----------|-----------|-------------|
| Maximize Conversions | `MAXIMIZE_CONVERSIONS` | Default for lead gen. Let Google find cheapest conversions. |
| Target CPA | `TARGET_CPA` | After 30+ conversions/month. Set your target cost per acquisition. |
| Maximize Conversion Value | `MAXIMIZE_CONVERSION_VALUE` | E-commerce with variable order values. |
| Target ROAS | `TARGET_ROAS` | After 50+ conversions/month with value tracking. |
| Maximize Clicks | `MAXIMIZE_CLICKS` | Top-of-funnel traffic campaigns only. |
| Manual CPC | `MANUAL_CPC` | Tight budget control, small accounts, early testing. |
| Enhanced CPC | `MANUAL_CPC` + `enhanced_cpc_enabled` | Manual with Google's adjustment layer. |

### Bidding Strategy Progression

```
New account, no conversion data:
  Start: Manual CPC or Maximize Clicks (gather data)
  After 15+ conversions/month: Switch to Maximize Conversions
  After 30+ conversions/month: Switch to Target CPA
  After 50+ conversions with values: Switch to Target ROAS
```

## Conversion Tracking

### Google Tag (gtag.js)

```html
<!-- Global site tag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-XXXXXXXXX');
</script>
```

### Event Tracking

```javascript
// Lead form submission
gtag('event', 'conversion', {
  send_to: 'AW-XXXXXXXXX/AbC123',
  value: 25.00,
  currency: 'USD'
});

// Purchase
gtag('event', 'purchase', {
  send_to: 'AW-XXXXXXXXX/DeF456',
  value: 99.00,
  currency: 'USD',
  transaction_id: 'ORDER-12345'
});
```

### Enhanced Conversions

Server-side conversion data for better attribution (similar to Meta CAPI):

```javascript
gtag('set', 'user_data', {
  email: 'user@example.com',        // Hashed automatically by gtag
  phone_number: '+1234567890',
  address: {
    first_name: 'John',
    last_name: 'Doe',
    city: 'Bogota',
    region: 'DC',
    country: 'CO'
  }
});
```

### Offline Conversion Import

Upload offline conversions (CRM closed deals, phone calls) via API:

```
POST /customers/{customer_id}/offlineConversionAdjustments:mutate
{
  "conversions": [{
    "gclid": "CjwKCAjw...",
    "conversion_action": "customers/123/conversionActions/456",
    "conversion_date_time": "2026-04-14 12:00:00-05:00",
    "conversion_value": 500.00,
    "currency_code": "USD"
  }]
}
```

## Quality Score

Quality Score (1-10) directly impacts your CPC and ad position. Three components:

| Component | Weight | How to Improve |
|-----------|--------|---------------|
| Expected CTR | ~33% | Write compelling ads, use exact match keywords |
| Ad Relevance | ~33% | Include keywords in headlines/descriptions |
| Landing Page Experience | ~33% | Fast load, mobile-friendly, relevant content |

### Quality Score Impact on CPC

```
Ad Rank = Bid x Quality Score

QS 10: You pay ~50% less than QS 5 for the same position
QS 3: You pay ~300% more than QS 10 for the same position
QS below 4: Google may not show your ad at all
```

## Authentication

### OAuth 2.0 Setup

```bash
GOOGLE_ADS_DEVELOPER_TOKEN=XXXXXXXXXX      # From Google Ads API Center
GOOGLE_ADS_CLIENT_ID=XXXXX.apps.google     # OAuth client ID
GOOGLE_ADS_CLIENT_SECRET=XXXXXX            # OAuth client secret
GOOGLE_ADS_REFRESH_TOKEN=1//XXXXXX         # Long-lived refresh token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=XXX-XXX-XXXX  # MCC account ID (if using manager)
GOOGLE_ADS_CUSTOMER_ID=XXX-XXX-XXXX        # Target ad account
```

### API Rate Limits

- Basic access: 15,000 requests/day, 1,500 operations/mutate
- Standard access: 100,000 requests/day
- Reporting: 10 concurrent report requests
- Mutate operations: max 5,000 operations per request
