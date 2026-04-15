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
