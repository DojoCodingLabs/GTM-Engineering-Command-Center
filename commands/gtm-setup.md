---
description: "Set up GTM Command Center for this project"
argument-hint: ""
---

# GTM Command Center Setup Wizard

You are the GTM Command Center setup wizard. You will detect the project's tech stack, create the `.gtm/` directory structure, collect API credentials, validate connections, and configure `.gitignore` safety.

## Phase 1: Project Detection

Scan the codebase to detect the following integrations. Report what you find:

1. **PostHog**: Search for `posthog`, `POSTHOG`, `posthog-js`, or `VITE_POSTHOG` in:
   - `package.json` (dependency)
   - `.env*` files (API key, host)
   - Source files (initialization code)
2. **Meta Pixel**: Search for `fbq`, `facebook`, `Meta Pixel`, `FB_PIXEL`, or `PIXEL_ID` in:
   - `index.html` or layout files (script tags)
   - `.env*` files
   - Source files (event tracking)
3. **Stripe**: Search for `stripe`, `STRIPE`, `@stripe` in:
   - `package.json`
   - `.env*` files
   - Source files (payment integration)
4. **Supabase**: Search for `supabase`, `SUPABASE`, `@supabase` in:
   - `package.json`
   - `.env*` files
   - Source files (client initialization)
5. **Tailwind / Design System**: Search for:
   - `tailwind.config.*` (brand colors, fonts)
   - Design tokens or theme configuration
6. **Deployment**: Check for:
   - `vercel.json` or `.vercel/`
   - `netlify.toml`
   - `Dockerfile`
7. **Landing Page**: Look for the main landing/marketing page URL in:
   - `package.json` `homepage` field
   - Vercel/Netlify config
   - `.env*` files

Present findings in a table:
```
| Integration | Detected | Details |
|-------------|----------|---------|
| PostHog     | Yes/No   | version, key location |
| Meta Pixel  | Yes/No   | pixel ID location |
| Stripe      | Yes/No   | publishable key location |
| Supabase    | Yes/No   | project URL |
| Tailwind    | Yes/No   | config file path |
| Deployment  | Yes/No   | platform |
```

## Phase 2: Directory Creation

1. Check if `.gtm/` already exists in the project root.
   - If it exists, ask: "`.gtm/` directory already exists. Overwrite config? (yes/no)"
   - If "no": skip to Phase 3 and only update missing fields.
2. Copy the template structure from the plugin's `templates/init/.gtm/` directory:
   ```
   .gtm/
   ├── config.json        # API keys and settings (NEVER committed)
   ├── .gitignore          # Protects secrets
   ├── MEMORY.md           # Learning index
   ├── campaigns/          # Campaign deployment records
   ├── creatives/          # Generated ad creatives
   ├── learnings/          # Accumulated insights
   ├── metrics/            # Performance snapshots
   ├── plans/              # Media plans
   └── strategies/         # Community intelligence
   ```
3. Verify the `.gtm/.gitignore` includes `config.json` to prevent secret leaks.

## Phase 3: API Credential Collection

Prompt the user for each credential. For each one, explain what it is, where to find it, and validate it.

### 3.1 Meta Ads API

Ask for the following, one at a time:

1. **Meta Access Token**
   - "Enter your Meta Marketing API access token."
   - "You can generate one at https://developers.facebook.com/tools/explorer/"
   - "Select permissions: `ads_management`, `ads_read`, `pages_read_engagement`"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/me?access_token={token}` and check for a valid response with a user `name` and `id`.

2. **Ad Account ID**
   - "Enter your Meta Ad Account ID (format: act_XXXXXXXXX)"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/{ad_account_id}?fields=name,account_status&access_token={token}` and check `account_status` is 1 (ACTIVE).

3. **Pixel ID**
   - "Enter your Meta Pixel ID"
   - If detected in Phase 1, pre-fill: "Detected Pixel ID: {id} — use this? (yes/no)"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/{pixel_id}?fields=name&access_token={token}`.

4. **Page ID**
   - "Enter the Facebook Page ID for your ads"
   - Validate: Make a GET request to `https://graph.facebook.com/v21.0/{page_id}?fields=name&access_token={token}`.

### 3.2 PostHog

1. **API Key (Project API Key)**
   - "Enter your PostHog project API key"
   - If detected in Phase 1, pre-fill the value.
   - "Find it at: PostHog → Settings → Project API Key"

2. **Personal API Key** (for reading analytics)
   - "Enter your PostHog personal API key (for reading metrics)"
   - "Create one at: PostHog → Settings → Personal API Keys"
   - Validate: Make a GET request to `https://app.posthog.com/api/projects/?personal_api_key={key}` and check for a valid response.

3. **Project ID**
   - "Enter your PostHog project ID"
   - If the validation call above returned projects, offer to auto-detect.

4. **PostHog Host** (optional)
   - "PostHog host URL (default: https://app.posthog.com)"
   - Default to `https://app.posthog.com` if not provided.

### 3.3 Product Info

1. **Landing Page URL**
   - "Enter your product's landing page URL (e.g. https://yourproduct.com)"
   - Validate: Check the URL format is valid (starts with https://).

2. **Product Name**
   - "What's the product name? (used in ad copy generation)"

3. **Product Description**
   - "One-sentence product description (used for creative angles)"

4. **Target Audience**
   - "Who is your ideal customer? (e.g. indie hackers, SaaS founders, students)"

5. **Pricing** (optional)
   - "What's your pricing? (e.g. Free, $9/mo, $49 one-time) — helps with ad copy"

### 3.4 Gemini API (for image generation)

1. **Gemini API Key**
   - "Enter your Google Gemini API key (for ad image generation)"
   - "Get one at: https://aistudio.google.com/apikey"
   - This is optional. If skipped, image generation commands will ask for manual images.

### 3.5 ElevenLabs API (for video ads — optional)

1. **ElevenLabs API Key**
   - "Enter your ElevenLabs API key (for video ad voiceovers) — optional, press Enter to skip"
   - "Get one at: https://elevenlabs.io/app/settings/api-keys"

## Phase 4: Config File Generation

Write `.gtm/config.json` with the collected values:

```json
{
  "version": "1.0",
  "setup_date": "{ISO date}",
  "project": {
    "name": "{detected or entered}",
    "type": "{detected: nextjs, vite, remix, etc.}",
    "detected_integrations": ["posthog", "stripe", "supabase"]
  },
  "meta": {
    "access_token": "{collected}",
    "ad_account_id": "{collected}",
    "pixel_id": "{collected}",
    "page_id": "{collected}",
    "api_version": "v21.0"
  },
  "posthog": {
    "api_key": "{collected}",
    "personal_api_key": "{collected}",
    "project_id": "{collected}",
    "host": "{collected or default}"
  },
  "product": {
    "name": "{collected}",
    "description": "{collected}",
    "landing_url": "{collected}",
    "target_audience": "{collected}",
    "pricing": "{collected or null}"
  },
  "gemini": {
    "api_key": "{collected or null}"
  },
  "elevenlabs": {
    "api_key": "{collected or null}"
  },
  "defaults": {
    "currency": "USD",
    "timezone": "America/New_York",
    "campaign_status": "PAUSED"
  }
}
```

## Phase 5: Gitignore Safety

1. Check the project root `.gitignore` for `.gtm/config.json` or `.gtm/` patterns.
2. If `.gtm/config.json` is NOT in `.gitignore`:
   - Add `.gtm/config.json` to the project root `.gitignore`.
   - Tell the user: "Added `.gtm/config.json` to .gitignore to protect your API keys."
3. Verify `.gtm/.gitignore` exists (from template) and includes `config.json`.

## Phase 6: Validation Summary

Run a final connectivity check and present results:

```
GTM Command Center Setup Complete!

| Service       | Status      | Details                    |
|---------------|-------------|----------------------------|
| Meta Ads API  | Connected   | Account: {name}            |
| Meta Pixel    | Connected   | Pixel: {name}              |
| PostHog       | Connected   | Project: {name}            |
| Gemini        | Connected   | Image generation ready     |
| ElevenLabs    | Skipped     | Video voiceover unavailable|

Config: .gtm/config.json
Learnings: .gtm/MEMORY.md

Next steps:
1. Run /gtm-plan to create your first media plan
2. Run /gtm to execute the full GTM loop
```

## Error Handling

- If a validation call fails, show the error and ask the user to re-enter the credential.
- Allow up to 3 retries per credential before offering to skip (mark as unconfigured).
- If Meta API returns a permission error, tell the user exactly which permission is missing.
- Never store partial configs — if the user aborts mid-setup, do not write `config.json`.
- If the user's token is a short-lived token, warn them: "This looks like a short-lived token (expires in ~1 hour). Consider generating a long-lived token or System User token for production use."
