# Playwright Patterns for GTM QA

## Setup

Playwright is available via the `mcp__plugin_playwright_playwright__*` MCP tools. These provide browser automation without needing to install Playwright locally.

### Available Playwright MCP Tools

| Tool | Use For |
|------|---------|
| `browser_navigate` | Go to a URL |
| `browser_snapshot` | Get DOM accessibility tree (structured) |
| `browser_take_screenshot` | Visual screenshot (PNG) |
| `browser_click` | Click an element |
| `browser_fill_form` | Fill form fields |
| `browser_type` | Type text into focused element |
| `browser_press_key` | Press keyboard keys |
| `browser_evaluate` | Execute JavaScript in page context |
| `browser_console_messages` | Get console log/error/warn output |
| `browser_network_requests` | Get network request log |
| `browser_select_option` | Select dropdown option |
| `browser_hover` | Hover over element |
| `browser_wait_for` | Wait for element/network/timeout |
| `browser_resize` | Change viewport size |
| `browser_navigate_back` | Go back |
| `browser_close` | Close browser |
| `browser_tabs` | List open tabs |
| `browser_run_code` | Run Playwright code directly |

### Alternative: Bash + npx playwright

If Playwright MCP is not available, use direct Playwright via Bash:

```bash
npx playwright test --headed  # Run existing test files
npx playwright codegen        # Record interactions
```

Or write inline scripts:

```bash
npx -y playwright-core install chromium
node -e "
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://example.com');
  // ... verification logic
  await browser.close();
})();
"
```

## Common QA Patterns

### Pattern 1: Verify Pixel + Analytics Fire on Page Load

```
1. browser_navigate → landing page URL with UTMs
2. browser_wait_for → wait for page load
3. browser_network_requests → filter for:
   - facebook.com/tr (Meta Pixel)
   - /e/ or /capture (PostHog)
   - google-analytics.com or analytics.google.com (GA4)
4. browser_console_messages → check for errors
5. Report: which tracking tools fired, which didn't
```

### Pattern 2: Test Full Signup Flow

```
1. browser_navigate → landing page
2. browser_click → CTA button
3. browser_fill_form → email, password fields
4. browser_click → submit
5. browser_wait_for → redirect to dashboard/onboarding
6. browser_network_requests → check CompleteRegistration event fired
7. browser_snapshot → verify we're on the right page
8. Report: flow completed successfully or failed at step N
```

### Pattern 3: Mobile Responsiveness Check

```
1. browser_resize → 375x812 (iPhone SE)
2. browser_navigate → landing page
3. browser_take_screenshot → save as mobile-375.png
4. browser_snapshot → check for horizontal overflow indicators
5. browser_evaluate → document.body.scrollWidth > window.innerWidth
6. browser_resize → 768x1024 (iPad)
7. browser_take_screenshot → save as tablet-768.png
8. Report: responsive issues found or all viewports pass
```

### Pattern 4: Landing Page Performance Audit

```
1. browser_navigate → landing page
2. browser_evaluate → performance.getEntriesByType('navigation')[0]
3. Extract: domContentLoaded, loadComplete, TTFB
4. browser_evaluate → Get LCP via PerformanceObserver
5. browser_evaluate → Get CLS via PerformanceObserver
6. browser_console_messages → count errors and warnings
7. Report: Core Web Vitals scores, pass/fail per metric
```

### Pattern 5: Verify Email Template Rendering

```
1. Fetch email HTML from provider API (Resend/SendGrid preview)
2. Write HTML to temp file
3. browser_navigate → file:///tmp/email-preview.html
4. browser_take_screenshot → full page screenshot
5. browser_resize → 375px → mobile screenshot
6. browser_evaluate → check all images load, all links valid
7. Report: visual preview + broken links/images
```

### Pattern 6: Competitor Landing Page Analysis

```
1. browser_navigate → competitor URL
2. browser_take_screenshot → full page screenshot
3. browser_snapshot → extract heading hierarchy, CTA text, value props
4. browser_evaluate → extract meta tags, schema markup
5. browser_network_requests → identify their analytics/ad tools
6. Report: competitor positioning, tools used, conversion elements
```

## Error Recovery

If Playwright MCP tools are not available (not installed, not connected):

1. Check if `mcp__plugin_playwright_playwright__browser_navigate` exists
2. If not, fall back to Computer Use (mcp__computer-use__*) for screenshots
3. If Computer Use not available, fall back to WebFetch for HTML analysis
4. If nothing works, report what tools are needed and how to install them

Never silently skip QA — always report what was checked and what couldn't be checked.
