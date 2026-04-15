---
name: gtm-qa
description: Run autonomous QA verification on any GTM deployment — pixel fires, funnel walkthroughs, mobile testing, performance audits, email rendering
---

# GTM QA — Autonomous Verification

You are the GTM QA command. You verify that GTM deployments actually work by testing in real browsers. You use Playwright, Computer Use, and direct HTTP checks to validate every aspect of a deployment.

**Rule: Never declare success without verification. Never report "I can't verify" — use every tool available.**

## Arguments

- `/gtm-qa` — Auto-detect what was recently deployed and QA it
- `/gtm-qa landing` — QA landing page(s)
- `/gtm-qa campaign` — QA ad campaign deployment (landing URLs, pixel, creatives)
- `/gtm-qa email` — QA email templates (rendering, links, tracking)
- `/gtm-qa seo` — QA SEO content (schema markup, meta tags, content quality)
- `/gtm-qa funnel` — Full funnel walkthrough from ad click to payment
- `/gtm-qa all` — Run all QA suites

## Phase 0: Tool Detection

Before running any QA:

1. Check for Playwright MCP: attempt to use `mcp__plugin_playwright_playwright__browser_navigate`
   - If available: primary tool for all web QA
   - If not available: note it, fall back to alternatives

2. Check for Computer Use: attempt to use `mcp__computer-use__screenshot`
   - If available: use for visual verification and native app interaction
   - If not available: note it, fall back to HTTP checks only

3. Check for other tools:
   - `curl` via Bash: always available for HTTP checks
   - WebFetch: always available for HTML analysis
   - `node`: check if available for running scripts

4. Report available tools: "QA running with: Playwright + Computer Use + HTTP" or "QA running with: HTTP only (install Playwright MCP for full verification)"

## Phase 1: Read Deployment Context

1. Read `.gtm/config.json` — get pixel_id, PostHog key, landing_url, design_tokens
2. Read `.gtm/campaigns/` — latest campaign records with landing URLs, ad IDs
3. Read `.gtm/creatives/` — latest creative assets
4. Check `git log --oneline -10` — any recent landing page or email commits?
5. If no argument provided, auto-detect what was most recently deployed and select the appropriate QA suite.

## Phase 2: Execute QA Suites

Dispatch the qa-engineer agent with the appropriate test suite. The agent runs the full verification checklist from `skills/browser-qa/SKILL.md`.

### Landing Page QA (when `landing` or auto-detected)

1. Navigate to landing URL
2. Check: page loads (HTTP 200, < 3s)
3. Check: no console errors
4. Check: Meta Pixel fires (PageView)
5. Check: PostHog $pageview fires
6. Check: UTM params captured
7. Check: cookie consent works
8. Check: CTA visible and clickable
9. Check: mobile responsive (375px, 768px)
10. Check: SEO meta tags present (title, description, og:*)
11. Check: Core Web Vitals pass (LCP < 2.5s)
12. Screenshot: desktop, mobile, tablet

### Campaign QA (when `campaign` or auto-detected)

1. For each ad in latest campaign:
   - Verify landing URL resolves (HTTP 200)
   - Verify UTM parameters in URL
   - Navigate to landing URL
   - Verify pixel fires with correct pixel ID
   - Verify creative images exist in Meta (via Graph API)
2. Verify campaign pixel ID matches config pixel ID
3. Verify ad set targeting matches plan

### Email QA (when `email` or auto-detected)

1. Fetch email HTML preview from provider API
2. Render in browser (600px desktop, 375px mobile)
3. Screenshot both viewports
4. Verify all images load
5. Verify all links resolve (HTTP 200)
6. Verify UTM parameters on all links
7. Verify unsubscribe link present
8. Verify no links point to localhost/staging

### SEO QA (when `seo` or auto-detected)

1. Navigate to content page
2. Verify JSON-LD structured data is valid
3. Verify heading hierarchy (single h1, logical h2/h3)
4. Verify meta description length (120-160 chars)
5. Verify canonical URL set
6. Verify OG image resolves
7. Check page for thin content (> 500 words)

### Full Funnel QA (when `funnel`)

1. Navigate to landing page with ad UTMs
2. Accept cookie consent
3. Verify: PageView fires (Pixel + PostHog)
4. Click CTA
5. Complete signup flow (if test env available)
6. Verify: CompleteRegistration fires
7. Verify: PostHog signup event fires
8. Navigate to pricing page
9. Verify: pricing displays correctly
10. Verify: checkout link works (don't complete payment)
11. Report: full funnel walkthrough results

## Phase 3: Generate Report

Present results as a structured table:

```
GTM QA Report — {date}

Target: {what was verified}
Tools used: {Playwright, Computer Use, HTTP}

| Check              | Status | Details                         |
|--------------------|--------|---------------------------------|
| Page Load          | PASS   | 1.2s LCP, 0 errors              |
| Meta Pixel         | PASS   | PageView + CompleteRegistration  |
| PostHog            | PASS   | $pageview + signup events        |
| Mobile (375px)     | WARN   | CTA below fold                  |
| UTM Tracking       | PASS   | All params captured              |
| Performance        | PASS   | LCP 1.2s, TTFB 340ms            |

Issues: 1 warning, 0 failures
Verdict: APPROVED with recommendations
```

Save report to `.gtm/qa/report-{date}.md`

## Phase 4: Verdict

- **All PASS**: "Deployment verified. All checks passed."
- **WARN only**: "Deployment approved with warnings. Recommended improvements: {list}"
- **Any FAIL**: "Deployment NOT verified. Critical issues found: {list}. Fix before activating."

If FAIL, provide the exact fix for each issue — file path, code change, or command to run.

## Error Handling

- If Playwright MCP is not available: fall back to curl + WebFetch + Computer Use
- If a page requires authentication: skip the auth-gated checks, report them as SKIPPED
- If a URL returns 403/5xx: report as FAIL with the HTTP status code
- If an image fails to load: report the broken URL
- Never silently skip any check — always report as PASS, WARN, FAIL, or SKIPPED
