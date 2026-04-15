---
name: browser-qa
description: Browser-based QA and autonomous verification — Playwright, Chrome DevTools MCP, Computer Use for visual testing, pixel verification, funnel walkthroughs, and overcoming web UI blockers
---

# Browser QA & Autonomous Verification

This skill enables the GTM agent to **see, interact with, and verify** real browser experiences. The agent uses browser tools to QA its own work, verify tracking fires correctly, test signup flows end-to-end, and overcome blockers that have no CLI/API path.

## Tool Hierarchy (Pick the Right Tool)

Always use the most efficient tool for the job:

| Task | Tool | Why |
|------|------|-----|
| Verify pixel fires, check network requests | Playwright (headless) | Fast, scriptable, can inspect network layer |
| Visual screenshot comparison | Playwright screenshot + Read | Headless, pixel-perfect, no setup overhead |
| Test full signup/checkout flow | Playwright end-to-end | Automated form filling, navigation, assertions |
| Interact with web UIs that block API access | Computer Use (mcp__computer-use__*) | Click real buttons, fill real forms, handle OAuth popups |
| Inspect live DOM, console errors, performance | Playwright evaluate + console | Access to browser APIs, performance metrics |
| Verify mobile responsiveness | Playwright with viewport override | Test at 375px, 390px, 768px |
| Read what's on screen when other tools fail | Computer Use screenshot | Last resort visual inspection |

## Playwright Patterns

### Verify Meta Pixel Fires

```javascript
// Navigate to landing page and intercept network requests
const pixelRequests = [];
page.on('request', req => {
  if (req.url().includes('facebook.com/tr')) pixelRequests.push(req);
});
await page.goto(landingUrl);
// Check PageView fired
const pageViewFired = pixelRequests.some(r => r.url().includes('ev=PageView'));

// Simulate signup and check CompleteRegistration
await page.fill('[data-testid="email-input"]', 'test@example.com');
await page.click('[data-testid="signup-button"]');
const regFired = pixelRequests.some(r => r.url().includes('ev=CompleteRegistration'));
```

### Verify PostHog Events

```javascript
// Intercept PostHog capture calls
const posthogEvents = [];
page.on('request', req => {
  if (req.url().includes('/e/') || req.url().includes('/capture')) {
    try {
      const body = JSON.parse(req.postData());
      posthogEvents.push(...(body.batch || [body]));
    } catch {}
  }
});
await page.goto(url);
// Check specific event fired
const hasEvent = posthogEvents.some(e => e.event === '$pageview');
```

### Test Landing Page Performance

```javascript
// Get Core Web Vitals
const metrics = await page.evaluate(() => {
  return new Promise(resolve => {
    new PerformanceObserver(list => {
      const entries = {};
      list.getEntries().forEach(e => entries[e.name] = e.value || e.startTime);
      resolve(entries);
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  });
});
// LCP should be < 2.5s for good score
```

### Screenshot Mobile Viewports

```javascript
// Test critical viewports
const viewports = [
  { width: 375, height: 812, name: 'iPhone SE' },
  { width: 390, height: 844, name: 'iPhone 14' },
  { width: 768, height: 1024, name: 'iPad' },
  { width: 1440, height: 900, name: 'Desktop' }
];
for (const vp of viewports) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  await page.goto(url);
  await page.screenshot({ path: `.gtm/qa/${vp.name}.png`, fullPage: true });
}
```

### Verify UTM Parameters Persist Through Signup

```javascript
// Land with UTMs
await page.goto(url + '?utm_source=meta&utm_medium=paid&utm_campaign=test');
// Complete signup flow
await page.click('[data-testid="signup-cta"]');
// Check UTMs are stored
const storedUtm = await page.evaluate(() => {
  return localStorage.getItem('utm_params') || sessionStorage.getItem('utm_params');
});
```

## Computer Use Patterns

Use Computer Use (mcp__computer-use__*) when you need to interact with native apps or web UIs that resist automation:

### When to Use Computer Use

1. **Meta Business Manager** — OAuth flows, app mode toggles, account settings that have no API
2. **Google Ads Manager** — Manual campaign review, settings that require UI interaction
3. **Vercel Dashboard** — Redeploy, check env vars, review deployment logs
4. **Email provider dashboards** — Check deliverability reports, domain verification
5. **Any web UI that blocks programmatic access** — OAuth popups, CAPTCHA flows, 2FA

### Computer Use Workflow

```
1. request_access — List applications needed (Chrome, Safari, etc.)
2. screenshot — See current state before acting
3. left_click / type / key — Interact with UI elements
4. screenshot — Verify action completed
5. Repeat until goal achieved
```

### Important Computer Use Rules

- Chrome is **read-only tier** — can screenshot but not click/type. Use Playwright for Chrome interaction.
- For web forms: prefer Playwright. Use Computer Use only for native app UIs or OAuth flows.
- Always screenshot BEFORE and AFTER actions to verify state.
- If a browser shows a CAPTCHA or 2FA prompt, ask the user to complete it — don't try to bypass.

## QA Verification Checklist

After any GTM asset deployment (landing page, email, ad), run this verification:

### Landing Page QA
- [ ] Page loads in < 3 seconds (LCP)
- [ ] No console errors on load
- [ ] Meta Pixel PageView fires (check network requests)
- [ ] PostHog $pageview captures (check /e/ or /capture requests)
- [ ] UTM parameters are captured and stored
- [ ] CTA button is visible and clickable
- [ ] Mobile responsive at 375px (no horizontal scroll, CTA visible)
- [ ] OG meta tags present (og:title, og:description, og:image)
- [ ] Signup flow completes without errors
- [ ] CompleteRegistration event fires on signup

### Email QA
- [ ] Template renders correctly (preview via provider API or browser)
- [ ] Links point to correct URLs with UTM parameters
- [ ] Unsubscribe link works
- [ ] Images load (not blocked, correct dimensions)
- [ ] Subject line and preview text are set

### Ad Creative QA
- [ ] Landing URL resolves (no 404)
- [ ] UTM parameters are in the landing URL
- [ ] Pixel fires on the landing page
- [ ] Landing page matches ad angle/messaging

### Tracking QA (Cross-Channel)
- [ ] Meta Pixel events fire for each funnel step
- [ ] PostHog events fire for each funnel step
- [ ] Event IDs match between Pixel and CAPI (deduplication)
- [ ] Stripe checkout includes attribution metadata
- [ ] GA4 events fire (if configured)

## Overcoming Blockers

The QA agent should NEVER report "I can't do this because there's no API." Instead:

1. **Try the API/CLI first** — fastest path
2. **Try Playwright** — headless browser automation
3. **Try Chrome DevTools MCP** — if available, for DOM inspection
4. **Try Computer Use** — for native UI interaction
5. **Try web scraping** — WebFetch for read-only data
6. **Only then ask the user** — as absolute last resort, with a specific ask (not vague "help me")

The agent should always exhaust all available tools before asking for human help.
