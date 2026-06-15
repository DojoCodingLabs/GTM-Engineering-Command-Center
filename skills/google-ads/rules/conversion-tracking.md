# Google Ads Conversion Tracking -- Setup, Enhanced Conversions, and Offline Import

## Conversion Tracking Architecture

```
Conversion Tracking Stack:
  ├── Client-Side (gtag.js)
  │   ├── Page-level tag (tracks pageviews, sets cookies)
  │   ├── Event tags (tracks form submissions, button clicks, purchases)
  │   └── Enhanced conversions (sends hashed user data for better matching)
  ├── Server-Side (Google Ads API)
  │   ├── Offline conversion import (CRM data, phone calls, in-store)
  │   └── Enhanced conversions for leads (GCLID + offline conversion)
  └── Google Tag Manager (GTM)
      ├── Container manages all tags, triggers, variables
      └── Server-side GTM container for first-party tracking
```

## Setting Up Conversion Actions

### Step 1: Create Conversion Action via API

```bash
POST /customers/{customer_id}/conversionActions:mutate
{
  "operations": [{
    "create": {
      "name": "Trial Signup",
      "category": "SIGNUP",
      "type": "WEBPAGE",
      "status": "ENABLED",
      "value_settings": {
        "default_value": 25.0,
        "default_currency_code": "USD",
        "always_use_default_value": false
      },
      "counting_type": "ONE_PER_CLICK",
      "attribution_model_type": "GOOGLE_SEARCH_ATTRIBUTION",
      "click_through_lookback_window_days": 30,
      "view_through_lookback_window_days": 1
    }
  }]
}
```

### Conversion Action Categories

| Category | API Value | Use When |
|----------|-----------|----------|
| Purchase | `PURCHASE` | Completed transaction with payment |
| Signup | `SIGNUP` | Account creation, free trial start |
| Lead | `LEAD` | Form submission, demo request |
| Page view | `PAGE_VIEW` | Key page visited (pricing, features) |
| Download | `DOWNLOAD` | App install, resource download |
| Add to cart | `ADD_TO_CART` | E-commerce cart addition |
| Begin checkout | `BEGIN_CHECKOUT` | Checkout process started |
| Subscribe | `SUBSCRIBE` | Newsletter or recurring subscription |
| Contact | `CONTACT` | Phone call, chat, email click |

### Counting Types

```
ONE_PER_CLICK: Count one conversion per ad click, even if user converts multiple times
  Use for: Signups, lead forms, demo requests (one per person matters)

MANY_PER_CLICK: Count every conversion from the same ad click
  Use for: Purchases, downloads (each one has value)
```

## Client-Side Implementation

### Basic gtag.js Setup

```html
<!-- Install on every page -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-CONVERSION_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-CONVERSION_ID');
</script>
```

### Event-Based Conversion Tracking

```javascript
// Lead form submission
function trackLeadSubmission() {
  gtag('event', 'conversion', {
    send_to: 'AW-CONVERSION_ID/CONVERSION_LABEL',
    value: 25.00,
    currency: 'USD'
  });
}

// Trial signup
function trackTrialSignup(email) {
  gtag('event', 'conversion', {
    send_to: 'AW-CONVERSION_ID/TRIAL_LABEL',
    value: 50.00,
    currency: 'USD'
  });
}

// Purchase
function trackPurchase(orderId, value) {
  gtag('event', 'conversion', {
    send_to: 'AW-CONVERSION_ID/PURCHASE_LABEL',
    value: value,
    currency: 'USD',
    transaction_id: orderId  // Prevents duplicate counting
  });
}
```

### SPA (Single Page Application) Tracking

For React/Vite/Next.js SPAs, fire conversion events on route changes and form submissions, not page loads:

```typescript
// React hook for Google Ads conversion tracking
function useGoogleAdsConversion() {
  const trackConversion = (conversionLabel: string, value?: number, transactionId?: string) => {
    if (typeof window.gtag !== 'function') return;

    const params: Record<string, unknown> = {
      send_to: `AW-${GOOGLE_ADS_ID}/${conversionLabel}`,
    };

    if (value !== undefined) {
      params.value = value;
      params.currency = 'USD';
    }

    if (transactionId) {
      params.transaction_id = transactionId;
    }

    window.gtag('event', 'conversion', params);
  };

  return { trackConversion };
}
```

## Enhanced Conversions

Enhanced conversions send hashed first-party data (email, phone, address) to Google for better conversion matching. Critical when cookies are blocked.

### Enhanced Conversions for Web

```javascript
// Set user data BEFORE the conversion event
gtag('set', 'user_data', {
  email: userEmail,              // gtag hashes automatically with SHA256
  phone_number: userPhone,       // Include country code: +1234567890
  address: {
    first_name: firstName,
    last_name: lastName,
    street: streetAddress,
    city: city,
    region: stateOrProvince,     // 2-letter code
    postal_code: postalCode,
    country: countryCode         // 2-letter ISO code
  }
});

// Then fire the conversion
gtag('event', 'conversion', {
  send_to: 'AW-CONVERSION_ID/LABEL',
  value: 50.00,
  currency: 'USD'
});
```

### Enhanced Conversions for Leads

For B2B or long sales cycles where the conversion happens offline (CRM):

```
Flow:
  1. User clicks Google ad → lands on your site → GCLID stored in cookie
  2. User submits lead form → you capture email + GCLID
  3. Store GCLID with the lead in your CRM
  4. When lead converts to customer (days/weeks later):
     Upload offline conversion with GCLID via API
  5. Google matches the conversion to the original ad click
```

## Offline Conversion Import

### Via Google Ads API

```bash
POST /customers/{customer_id}/offlineUserDataJobs:mutate
{
  "operations": [{
    "create": {
      "type": "STORE_SALES_UPLOAD_FIRST_PARTY",
      "external_id": 12345,
      "customer_match_user_list_metadata": {
        "user_list_id": "USER_LIST_ID"
      }
    }
  }]
}

# Then add conversion data
POST /offlineUserDataJobs/{job_id}:addOperations
{
  "operations": [{
    "create": {
      "user_identifiers": [{
        "hashed_email": "SHA256_HASH_OF_EMAIL"
      }],
      "transaction_attribute": {
        "conversion_action": "customers/123/conversionActions/456",
        "transaction_date_time": "2026-04-14 12:00:00-05:00",
        "transaction_amount": {
          "value": 500.0,
          "currency_code": "USD"
        }
      }
    }
  }]
}
```

### GCLID-Based Import

```bash
POST /customers/{customer_id}/conversionAdjustments:upload
{
  "conversions": [{
    "gclid": "CjwKCAjw...",
    "conversion_action": "customers/123/conversionActions/456",
    "conversion_date_time": "2026-04-14 15:30:00-05:00",
    "conversion_value": 500.00,
    "currency_code": "USD"
  }],
  "partial_failure": true
}
```

### GCLID Capture Best Practice

```javascript
// Capture GCLID from URL on landing page
function captureGclid() {
  const urlParams = new URLSearchParams(window.location.search);
  const gclid = urlParams.get('gclid');

  if (gclid) {
    // Store in cookie (90 days, matches Google's lookback window)
    document.cookie = `gclid=${gclid}; max-age=${90 * 24 * 60 * 60}; path=/; SameSite=Lax`;

    // Also store in localStorage as backup
    localStorage.setItem('gclid', gclid);
    localStorage.setItem('gclid_timestamp', Date.now().toString());
  }
}

// Include GCLID when user submits a form
function getStoredGclid(): string | null {
  // Try cookie first
  const match = document.cookie.match(/gclid=([^;]+)/);
  if (match) return match[1];

  // Fallback to localStorage
  const stored = localStorage.getItem('gclid');
  const timestamp = localStorage.getItem('gclid_timestamp');
  if (stored && timestamp) {
    const age = Date.now() - parseInt(timestamp);
    if (age < 90 * 24 * 60 * 60 * 1000) return stored; // Within 90 days
  }

  return null;
}
```

## Enhanced Conversions for Leads

> Atlas Part V — "the single highest-return work in the entire Atlas." First-party, consent-aware, server-side signal is the prerequisite for every advanced tactic (value-based bidding, AI Max, broad-match).

Enhanced Conversions for Leads (ECL) hashes the lead email with **SHA-256** and matches it to signed-in Google users **even when the GCLID expired or was never captured**. This is what lets a closed-won deal months later still credit the click that started it — it does not depend on a cookie surviving.

**WHITEHAT | 10/10** — Hashing first-party data the user volunteered and matching it to consenting signed-in users is the model Google built ECL for; no policy exposure.

**Match-rate targets (B2B SaaS):**

| Match rate | Read |
|------------|------|
| 40–65% | Healthy. Target band for B2B SaaS. |
| 30–40% | Acceptable; check phone normalization and address fields. |
| **< 30%** | **Field-mapping problem.** Email not normalized (trim + lowercase before hash), wrong column mapped, or hashes double-encoded. Fix mapping before scaling spend. |

**Enable ECL (account-level diagnostics — READ via CLI; toggle is a WRITE via the Customer settings UI/API):**

```bash
# READ-ONLY audit: confirm ECL-capable conversion actions exist and their counts
# Reference: skills/google-ads/rules/gads-cli.md
google-ads-open-cli conversion-actions <customer_id> --format compact

# Pull lead-action volume to sanity-check whether modeling/ECL will even engage
google-ads-open-cli query <customer_id> \
  "SELECT conversion_action.name, metrics.all_conversions
   FROM conversion_action WHERE conversion_action.category = 'LEAD'"
```

The hashed-payload upload itself is the **offline import / `offlineUserDataJobs`** flow already documented above (hashed_email identifier). ECL = that loop, keyed on email instead of GCLID.

## Consent Mode v2 Mechanics

Mandatory for **EEA and UK** traffic since **March 2024**. Without it, remarketing lists stop populating and modeled conversions stop reporting for that traffic. It governs four parameters:

| Param | Controls |
|-------|----------|
| `ad_storage` | Advertising cookies (read/write). |
| `analytics_storage` | Site analytics cookies. |
| `ad_user_data` | Whether user data is sent to Google for ads. |
| `ad_personalization` | Whether remarketing / personalized lists populate. |

**Basic vs Advanced:**

- **Basic** — tags do not load at all until consent is granted. No signal from deniers.
- **Advanced** — when a user denies, tags **do not read/write advertising cookies** but send **cookieless pings** (timestamp, user agent, ad-click context). Google's models use these to reconstruct lost conversions.

**Modeling threshold:** roughly **700 ad clicks over 7 days per country + domain** before modeling engages. Below that, denied traffic is simply lost — no model to fill the gap.

```html
<!-- Default to denied BEFORE gtag config; flip to granted on consent grant -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {
    ad_storage: 'denied',
    analytics_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    wait_for_update: 500
  });
</script>
<!-- ... AW- config loads here ... -->
<script>
  // CMP callback when user accepts
  function onConsentAccepted() {
    gtag('consent', 'update', {
      ad_storage: 'granted',
      analytics_storage: 'granted',
      ad_user_data: 'granted',
      ad_personalization: 'granted'
    });
  }
</script>
```

### Recovery numbers, stated honestly

Google's headline **"up to 70%" recovery is a ceiling for high-volume properties, not a default.** Plan against the realistic figures:

| Setup | Realistic recovery |
|-------|--------------------|
| Modeling alone (Advanced Consent Mode, nothing else) | **~17% median** conversion lift |
| Enhanced Conversions + Advanced Consent Mode + server-side tagging (sGTM) | **30–50%** recovery |
| Google's marketing headline | "up to 70%" — high-volume ceiling only |

**WHITEHAT | 10/10** — Server-side tagging with explicit consent verification and Advanced Consent Mode respect user choice under GDPR and the DMA.

**GRAYHAT | 6/10** — Cross-domain cookie syncing to build audiences across unaffiliated sites bypasses modern browser privacy controls; allowed in places but watch for policy drift and CMP/regulator scrutiny.

**BLACKHAT | 1/10** — Documented so you recognize it — never deploy. Consent-faking scripts that pass `granted` when the user opted out violate privacy law and Google policy and invite immediate account suspension.

## Server-Side Tagging (sGTM)

Run the tagging server on a **private first-party subdomain** (e.g. `tracking.yourbrand.com`) so requests are same-site:

- **Bypasses Safari Intelligent Tracking Prevention (ITP)** and browser ad blockers — first-party cookies set server-side get full lifetimes, not ITP's 7-day cap.
- **Forwards the `gcs` and `gcd` consent strings** to the server before dispatching, so consent state travels with the payload.
- **Dispatches hashed payloads via the Conversions API** (server-to-server), not from the browser — payloads survive ad blockers and cookie purges.

```
Browser ── first-party request ──► tracking.yourbrand.com (sGTM container)
                                         │  reads gcs/gcd consent strings
                                         │  hashes email/phone (SHA-256)
                                         └─► Google Ads Conversions API (server-side)
```

This is the infrastructure layer that turns the 30–50% recovery band above from aspiration into reality; ECL and Consent Mode v2 underdeliver without it.

## The CRM Offline Conversion Import Loop

For long-cycle SaaS and high-ticket funnels, web-tag tracking cannot connect a click today to a closed-won sale months later. The industry-standard fix is the **GCLID-to-CRM loop**:

```
1. Capture GCLID in a hidden form field  ──►  save to CRM lead record
2. Deal advances: MQL → SQL → Opportunity → Closed-Won
3. At each milestone, upload that stage back to Google (GCLID + value)
   via conversionAdjustments:upload / offlineUserDataJobs (see API blocks above)
4. Google credits the original ad click with real pipeline outcomes
```

**Hidden form field — captures GCLID for the CRM (uses the `getStoredGclid()` helper above):**

```html
<input type="hidden" name="gclid" id="gclid_field" />
<script>document.getElementById('gclid_field').value = getStoredGclid() || '';</script>
```

**Window math — GCLIDs expire after 90 days.** Widen attribution to at least a **30-day click / 90-day conversion** window so the loop can fire before the GCLID dies:

```bash
# value_settings live on the conversion action; widen via :mutate (WRITE — defaults below are PAUSED-safe metadata, not campaign state)
POST /customers/{customer_id}/conversionActions:mutate
{
  "operations": [{
    "update": {
      "resource_name": "customers/{customer_id}/conversionActions/{id}",
      "click_through_lookback_window_days": 90,
      "view_through_lookback_window_days": 30
    },
    "update_mask": "click_through_lookback_window_days,view_through_lookback_window_days"
  }]
}
```

**Stage values (demo-led SaaS) — money is in dollars here at the conversion-action level; the API's `transaction_amount.value` is also a decimal dollar value, NOT micros:**

| Stage | Import value |
|-------|--------------|
| MQL | $10–50 |
| SQL | $100–500 |
| Closed-Won | Actual deal value |

This matches how mature HubSpot and Salesforce integrations are implemented in the field, and feeds value-based bidding the real revenue gradient.

**Why it pays (directional, mostly self-reported — treat as direction, not guarantee):**

| Source | Result |
|--------|--------|
| Involve Digital | ~3x more pipeline at ~31% lower CPL for B2B SaaS running offline conversion tracking. |
| GrowthSpree | Attribution coverage 25–40% (default setups) → **85–95%** with full implementation in 30 days; SQL volume +30–50% at the same spend by day 90. |

**WHITEHAT | 10/10** — Importing real revenue and pipeline outcomes is the operational core of value-based bidding and the foundation of a defensible account.

## Conversion Tracking Debugging

### Common Issues and Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| 0 conversions but tracking code present | Wrong Conversion ID or Label | Verify in Google Ads > Tools > Conversions |
| Duplicate conversions | Missing `transaction_id` on purchases | Always pass unique transaction_id |
| Conversion count doesn't match actual signups | Counting type wrong | Switch to ONE_PER_CLICK for signups |
| Conversions show with 24-48h delay | Normal for enhanced conversions | Wait 72h before debugging |
| "Unverified" status in Google Ads | Tag not firing on conversion page | Use Google Tag Assistant to verify |
| Conversions attributed to wrong campaign | Attribution model mismatch | Check attribution settings in conversion action |

### Verification Tools

```
1. Google Tag Assistant (Chrome extension)
   - Shows which tags fire on the page
   - Shows conversion parameters being sent
   - Identifies misconfigured tags

2. Google Ads > Tools > Conversions > [Action] > Diagnostics
   - Shows tag coverage percentage
   - Shows recent conversion data
   - Flags configuration issues

3. Real-time check:
   - Open your site with ?gclid=test123 in the URL
   - Complete the conversion action
   - Check Google Ads conversion diagnostics within 4 hours
   - Enhanced conversions may take up to 48 hours to verify
```

### Attribution Models

| Model | How It Credits | Best For |
|-------|---------------|----------|
| Data-driven | ML-based, distributes credit based on actual impact | Default, best for most accounts |
| Last click | 100% to last-clicked ad | Simple accounts, single campaign |
| First click | 100% to first-clicked ad | Understanding acquisition channels |
| Linear | Equal credit to all touchpoints | Understanding full journey |
| Time decay | More credit to recent touchpoints | Long sales cycles |
| Position-based | 40% first, 40% last, 20% middle | Balanced view |

**Recommendation**: Use data-driven attribution (Google's default). Only switch if you have <300 conversions/month, in which case use last-click.

## Cross-Platform Deduplication

When tracking conversions with both Google Ads and Meta Pixel:

```
Rule: Use the same transaction_id/event_id across both platforms

Google Ads:
  gtag('event', 'conversion', {
    send_to: 'AW-123/LABEL',
    transaction_id: 'ORDER-12345'
  });

Meta Pixel:
  fbq('track', 'Purchase', { value: 99 }, { eventID: 'ORDER-12345' });

PostHog:
  posthog.capture('purchase', { transaction_id: 'ORDER-12345', value: 99 });

This prevents double-counting when both platforms claim the same conversion.
```
