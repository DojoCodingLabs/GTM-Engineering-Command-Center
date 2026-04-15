---
name: pr-conversion-check
description: "GitHub PR trigger that checks conversion tracking completeness on landing/email changes"
---

# PR Conversion Check Routine

## Overview

This routine triggers on GitHub pull requests that modify landing pages or email templates. It checks that all conversion tracking is complete and properly configured, then reports any gaps as PR comments. This prevents deploying marketing pages without proper analytics.

## Trigger

- **Event**: GitHub Pull Request (opened, synchronized)
- **File filter**: Only triggers when PR modifies files matching:
  - `src/pages/landing/**`
  - `src/pages/marketing/**`
  - `app/(marketing)/**`
  - `src/emails/**`
  - `src/components/landing/**`
  - `pages/landing/**`
  - Any file path containing `landing`, `marketing`, or `email` in a page/route context
- **Branch**: Any branch targeting `develop` or `main`

## What It Does

### Step 1: Identify Modified Files

1. Read the PR diff to identify which files were added or modified
2. Categorize files:
   - **Landing pages**: New or modified marketing/landing page components
   - **Email templates**: New or modified email templates
   - **Shared components**: Marketing-specific shared components

### Step 2: Check Landing Page Tracking

For each modified landing page file, verify:

#### PostHog Events
- [ ] Page view tracking present (`posthog.capture('$pageview')` or autocapture configured)
- [ ] CTA click events tracked (`posthog.capture('cta_click', { page, button, variant })`)
- [ ] Form submission events tracked (`posthog.capture('form_submit', { page, form_type })`)
- [ ] Scroll depth tracking (optional but recommended)

#### Meta Pixel Events
- [ ] `ViewContent` event fires on page load with content_name and content_category
- [ ] `Lead` event fires on form submission (for lead gen pages)
- [ ] `CompleteRegistration` event fires on signup (for signup pages)
- [ ] `AddToCart` or `InitiateCheckout` for purchase flows

#### UTM Parameters
- [ ] Internal links preserve UTM parameters
- [ ] CTA links include appropriate UTM tags
- [ ] Form submissions capture and forward UTM data

#### Conversion Tracking
- [ ] At least one conversion event is defined per page
- [ ] Conversion event matches the page's stated goal
- [ ] Event properties include enough context for attribution

### Step 3: Check Email Template Tracking

For each modified email template, verify:

#### Link Tracking
- [ ] All links include UTM parameters: `utm_source=email`, `utm_medium=drip`, `utm_campaign={sequence}`, `utm_content={email_number}`
- [ ] CTA link points to a valid URL
- [ ] No hardcoded URLs (should use config or constants)

#### Open Tracking
- [ ] Email provider's open tracking is enabled (pixel or provider-level)
- [ ] No images that could break open tracking

#### Unsubscribe
- [ ] Unsubscribe link is present in the footer
- [ ] List-Unsubscribe header is configured

### Step 4: Check Landing Page Quality

Beyond tracking, also check:

#### SEO Basics
- [ ] Page has a `<title>` tag
- [ ] Page has a `<meta name="description">` tag
- [ ] Page has Open Graph tags
- [ ] Images have alt text

#### Responsive Design
- [ ] No fixed pixel widths that could overflow on mobile
- [ ] Touch targets are at least 44px on mobile
- [ ] Content is readable at 375px width

#### Performance
- [ ] Images use next/image or lazy loading
- [ ] No unnecessarily large dependencies imported

### Step 5: Generate Report

Produce a checklist report:

```markdown
## GTM Conversion Tracking Check

### Landing Page: `src/pages/landing/campaign-spring.tsx`

**Tracking Completeness: 7/10**

| Check | Status | Details |
|-------|--------|---------|
| PostHog pageview | PASS | Autocapture enabled |
| PostHog CTA click | PASS | `cta_click` event on line 42 |
| PostHog form submit | FAIL | No form submission event found |
| Meta ViewContent | PASS | `fbq('track', 'ViewContent')` on line 15 |
| Meta Lead | FAIL | No Lead event on form submission |
| UTM preservation | PASS | UTM params forwarded to signup |
| SEO title | PASS | Title tag present |
| SEO description | FAIL | Meta description missing |
| OG tags | PASS | og:title and og:image present |
| Responsive | PASS | No fixed widths detected |

**Action Required:**
1. Add PostHog form submission tracking (line ~65, near form onSubmit)
2. Add Meta Pixel Lead event on form submission
3. Add `<meta name="description">` tag

### Email: `src/emails/sequences/welcome/email-2.tsx`

**Tracking Completeness: 4/5**

| Check | Status | Details |
|-------|--------|---------|
| UTM parameters | PASS | All links have UTMs |
| CTA URL valid | PASS | Points to /dashboard |
| Unsubscribe link | PASS | Present in footer |
| No hardcoded URLs | FAIL | Line 23: hardcoded "https://dojo.com" |
| Link tracking | PASS | Provider tracking enabled |

**Action Required:**
1. Replace hardcoded URL on line 23 with config-based URL
```

### Step 6: Post as PR Comment

Post the report as a GitHub PR comment. If all checks pass, post a brief success message. If any checks fail, post the full report with action items.

**All passing:**
```
GTM Conversion Check: All 10/10 checks passed for 2 modified files.
```

**Some failing:**
```
GTM Conversion Check: 7/10 checks passed. 3 issues found -- see details below.
{full report}
```

## Setup Instructions

### Prerequisites

1. GitHub repository with CI/CD access
2. `.gtm/config.json` with product configuration
3. Claude Code `/schedule` command with GitHub trigger support

### Create the Routine

```bash
/schedule create "PR Conversion Check" \
  --trigger "github:pull_request" \
  --filter "paths:src/pages/landing/**,src/emails/**,app/(marketing)/**,src/components/landing/**" \
  --command "Read the PR diff. For each modified landing page or email template, check conversion tracking completeness: PostHog events, Meta Pixel events, UTM parameters, SEO basics. Post a checklist report as a PR comment." \
  --description "Verify conversion tracking on landing page and email PRs"
```

### Customize Checks

Edit `.gtm/routines/config.json`:

```json
{
  "routines": [
    {
      "name": "pr-conversion-check",
      "trigger": "github:pull_request",
      "enabled": true,
      "options": {
        "check_posthog": true,
        "check_meta_pixel": true,
        "check_utm": true,
        "check_seo": true,
        "check_responsive": false,
        "check_performance": false,
        "fail_pr_on_missing_tracking": false,
        "file_patterns": [
          "src/pages/landing/**",
          "src/emails/**",
          "app/(marketing)/**"
        ]
      }
    }
  ]
}
```

## Troubleshooting

- **Routine not triggering**: Verify the file filter patterns match your project's structure. Check that the GitHub trigger is properly configured.
- **False positives**: If the routine flags tracking that exists in a parent component (not in the modified file), add an allowlist in the config.
- **Too noisy**: Set `fail_pr_on_missing_tracking: false` to make the report informational rather than blocking.

## Related Commands

- `/gtm-funnel` -- Full codebase tracking audit
- `/gtm-seo` -- SEO audit (more comprehensive than PR check)
- `/gtm-landing` -- Build new landing pages with tracking included
