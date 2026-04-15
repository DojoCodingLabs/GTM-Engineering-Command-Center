# Computer Use Patterns for GTM QA

## When to Use Computer Use

Computer Use (mcp__computer-use__*) gives the GTM agent direct desktop control — mouse, keyboard, screenshots. Use it when:

1. **Web UIs that block automation** — Meta Business Manager, Google Ads UI, OAuth flows
2. **Native app interaction** — Vercel Desktop, Slack Desktop, email clients
3. **Visual verification** — see exactly what the user sees on their screen
4. **OAuth and 2FA flows** — guide through multi-step auth that can't be scripted
5. **When Playwright is not available** — fallback for visual QA

## Tool Reference

| Tool | Action |
|------|--------|
| `request_access` | Request permission for specific apps (MUST call first) |
| `screenshot` | Capture current screen state |
| `left_click` | Click at coordinates |
| `right_click` | Right-click at coordinates |
| `double_click` | Double-click at coordinates |
| `type` | Type text at current cursor |
| `key` | Press keyboard key (Enter, Tab, Escape, etc.) |
| `scroll` | Scroll up/down/left/right |
| `mouse_move` | Move cursor to coordinates |
| `open_application` | Launch an application |
| `list_granted_applications` | See what apps we have access to |
| `zoom` | Zoom in/out for better visibility |
| `wait` | Wait for specified duration |

## App Tier Restrictions

- **Browsers** (Chrome, Safari, Firefox): **read-only** — can screenshot but NOT click or type. Use Playwright MCP for browser interaction.
- **Terminals/IDEs** (Terminal, VS Code): **click-only** — can click but NOT type. Use Bash tool for terminal commands.
- **Everything else**: **full access** — unrestricted mouse + keyboard.

## GTM-Specific Patterns

### Pattern 1: Meta Business Manager Navigation

Use when API calls fail or require manual UI steps (e.g., switching app mode, connecting IG account).

```
1. request_access — ["Safari", "Google Chrome"] (read tier) + ["Finder"] (full tier)
2. screenshot — see current state
3. If user is already on the right page: read and report what's visible
4. If user needs to navigate: INSTRUCT them verbally (can't click in browsers)
   - "Navigate to business.facebook.com → Settings → Instagram accounts"
   - "Click 'Connect Account' and authorize"
5. screenshot — verify they completed the step
6. Continue to next instruction
```

### Pattern 2: Verify Deployment Visually

After deploying a landing page or email template:

```
1. request_access — ["Google Chrome"] or ["Safari"]
2. screenshot — capture the deployed page
3. Read the screenshot — verify:
   - Logo renders correctly
   - Brand colors match design system
   - CTA button is visible and above fold
   - No broken images or layout issues
   - Mobile responsive (if user has mobile simulator open)
4. Report findings with screenshot evidence
```

### Pattern 3: Verify Vercel Deployment

```
1. request_access — ["Google Chrome"]
2. Take screenshot of Vercel dashboard if user has it open
3. Read deployment status, environment variables, build logs
4. Report: deployment successful/failed, env vars present/missing
5. If env vars missing: instruct user to add them (provide exact values)
```

### Pattern 4: Check PostHog Dashboard

```
1. request_access — ["Google Chrome"]
2. If user has PostHog open, screenshot the dashboard
3. Read: session count, event counts, funnel conversion rates
4. Compare with .gtm/metrics/ data
5. Report discrepancies between API data and visual dashboard
```

### Pattern 5: OAuth Flow Assistance

When an API requires OAuth that can't be automated:

```
1. Detect the OAuth URL from the API response
2. Tell user: "I need you to authorize at this URL: {url}"
3. If user opens it: screenshot to see the current state
4. Guide them through each step:
   - "Click 'Authorize'"
   - "Select permissions X, Y, Z"
   - "Copy the authorization code"
5. Continue with the code/token they provide
```

## Rules

1. **ALWAYS screenshot before and after** — verify state changes
2. **NEVER bypass security** — don't try to solve CAPTCHAs or 2FA programmatically
3. **PREFER Playwright over Computer Use** for web interaction — it's faster and more reliable
4. **Computer Use is the LAST RESORT** for web interaction, but the FIRST choice for native app interaction
5. **Always request_access first** — never assume you have app permissions
6. **Read browser tier carefully** — Chrome is read-only, you CANNOT click in it
7. **Minimize human asks** — exhaust all automated options before asking the user to do something manually
