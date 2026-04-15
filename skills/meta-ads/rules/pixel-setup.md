# Pixel & CAPI Setup Guide

## Overview

Accurate conversion tracking requires dual implementation:
1. **Meta Pixel** (client-side JavaScript) -- Fires in the browser
2. **Conversions API (CAPI)** (server-side) -- Fires from your backend

Both send events to the same Pixel ID. Meta deduplicates using `event_id`.

## Environment Variables

### Frontend (Browser Pixel)
```bash
VITE_META_PIXEL_ID=123456789012345
```
This is a build-time variable. Changing it requires a redeploy (Vercel/Netlify rebuild).

### Backend (CAPI Edge Function)
```bash
META_PIXEL_ID=123456789012345
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxx
META_API_VERSION=v21.0
```
These are runtime variables. Set in your Edge Function environment (Supabase Vault, Vercel env vars, etc.).

## Step 1: Find Your Pixel ID

1. Go to **Meta Events Manager**: https://business.facebook.com/events_manager2
2. Select your Pixel (or create one)
3. The Pixel ID is the 15-16 digit number shown under the pixel name

**Important**: Verify the pixel in Events Manager, not via the API. The API `GET /act_XXXXX/adspixels` may return pixels from other business accounts you have access to. Always confirm in Events Manager that the pixel belongs to the correct ad account.

## Step 2: Install Browser Pixel

### Base Code (add to index.html or layout)

```html
<script>
  !function(f,b,e,v,n,t,s)
  {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '%VITE_META_PIXEL_ID%');
  fbq('track', 'PageView');
</script>
```

### React Integration (with consent management)

```typescript
// src/lib/meta-pixel.ts
const PIXEL_ID = import.meta.env.VITE_META_PIXEL_ID;

export function initPixel() {
  if (!PIXEL_ID || typeof window === 'undefined') return;
  // Initialize pixel (base code should already be in index.html)
  if (window.fbq) {
    window.fbq('init', PIXEL_ID);
    window.fbq('track', 'PageView');
  }
}

export function trackEvent(eventName: string, params?: Record<string, unknown>, eventId?: string) {
  if (!window.fbq) return;
  const options = eventId ? { eventID: eventId } : undefined;
  window.fbq('track', eventName, params, options);
}

export function trackCustomEvent(eventName: string, params?: Record<string, unknown>, eventId?: string) {
  if (!window.fbq) return;
  const options = eventId ? { eventID: eventId } : undefined;
  window.fbq('trackCustom', eventName, params, options);
}
```

### Standard Events to Track

| Event | When to fire | Parameters |
|-------|-------------|------------|
| `PageView` | Every page load | (automatic with base code) |
| `Lead` | Form submission, signup | `{ value: 0, currency: 'USD' }` |
| `CompleteRegistration` | Account created | `{ value: 0, currency: 'USD' }` |
| `Purchase` | Payment completed | `{ value: 29.99, currency: 'USD' }` |
| `InitiateCheckout` | Started checkout | `{ value: 29.99, currency: 'USD' }` |
| `ViewContent` | Viewed pricing/product page | `{ content_name: 'Pricing' }` |
| `AddToCart` | Selected plan/product | `{ value: 29.99, currency: 'USD' }` |

## Step 3: Implement CAPI (Server-Side)

### Edge Function Template

```typescript
// supabase/functions/meta-capi/index.ts
import { serve } from 'https://deno.land/std@0.224.0/http/server.ts';

const PIXEL_ID = Deno.env.get('META_PIXEL_ID');
const ACCESS_TOKEN = Deno.env.get('META_ACCESS_TOKEN');
const API_VERSION = Deno.env.get('META_API_VERSION') || 'v21.0';

serve(async (req: Request) => {
  if (!PIXEL_ID || !ACCESS_TOKEN) {
    return new Response('Missing Meta configuration', { status: 500 });
  }

  const { event_name, event_id, user_data, custom_data, event_source_url } = await req.json();

  const payload = {
    data: [{
      event_name,
      event_time: Math.floor(Date.now() / 1000),
      event_id,  // Must match the eventID from browser pixel
      action_source: 'website',
      event_source_url,
      user_data: {
        em: user_data.email ? [await sha256(user_data.email.toLowerCase().trim())] : undefined,
        ph: user_data.phone ? [await sha256(user_data.phone.replace(/\D/g, ''))] : undefined,
        fn: user_data.first_name ? [await sha256(user_data.first_name.toLowerCase().trim())] : undefined,
        ln: user_data.last_name ? [await sha256(user_data.last_name.toLowerCase().trim())] : undefined,
        client_ip_address: req.headers.get('x-forwarded-for')?.split(',')[0]?.trim(),
        client_user_agent: req.headers.get('user-agent'),
        fbc: user_data.fbc,  // _fbc cookie value
        fbp: user_data.fbp,  // _fbp cookie value
        external_id: user_data.external_id ? [await sha256(user_data.external_id)] : undefined,
      },
      custom_data: custom_data || {},
    }],
  };

  const response = await fetch(
    `https://graph.facebook.com/${API_VERSION}/${PIXEL_ID}/events?access_token=${ACCESS_TOKEN}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }
  );

  const result = await response.json();
  return new Response(JSON.stringify(result), {
    status: response.ok ? 200 : 400,
    headers: { 'Content-Type': 'application/json' },
  });
});

async function sha256(value: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(value);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
```

## Step 4: Deduplication

Both Pixel and CAPI will send the same event. Meta deduplicates using `event_id` + `event_name` within a 48-hour window.

### Implementation Pattern

```typescript
// When an event occurs (e.g., signup):
const eventId = crypto.randomUUID();

// 1. Fire browser pixel
trackEvent('Lead', { value: 0, currency: 'USD' }, eventId);

// 2. Fire CAPI
await fetch('/api/meta-capi', {
  method: 'POST',
  body: JSON.stringify({
    event_name: 'Lead',
    event_id: eventId,
    user_data: { email: user.email, fbp: getCookie('_fbp'), fbc: getCookie('_fbc') },
    event_source_url: window.location.href,
  }),
});
```

## Step 5: Verify Setup

### In Events Manager

1. Go to **Events Manager** > Select your Pixel
2. Check **Overview** tab for incoming events
3. Look for both "Browser" and "Server" badges on each event
4. Green checkmark = deduplication working

### Test Events Tool

1. Events Manager > **Test Events** tab
2. Enter your website URL
3. Perform actions (signup, purchase)
4. Events should appear in real-time with source labels

### Common Verification Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Events show in Pixel Helper but not Events Manager | Pixel ID mismatch | Verify VITE_META_PIXEL_ID matches Events Manager |
| CAPI events not appearing | Wrong access token or pixel ID | Check META_ACCESS_TOKEN has correct permissions |
| "Duplicate" events (no dedup badge) | event_id doesn't match | Ensure same eventId is sent to both Pixel and CAPI |
| Events delayed by hours | Normal for CAPI | Server events can take up to 1 hour to appear |
| No events after redeploy | VITE_ var not rebuilt | Redeploy with correct VITE_META_PIXEL_ID |
