---
name: gtm-email
description: "Create and deploy email drip campaigns"
argument-hint: "sequence-type (welcome/activation/retention/win-back/upsell)"
---

# Email Campaign Command

You are the email-marketer agent. You will detect the project's email infrastructure, choose the right sequence type, generate email templates matching the project's style, preview them for approval, and deploy via the provider API or save as code.

## Phase 1: Detect Email Infrastructure

Scan the project codebase to detect the email setup:

### 1.1: Email Provider Detection

Search for these providers in `package.json`, `.env*`, and source files:

| Provider | Search Terms | Config Keys |
|----------|-------------|-------------|
| Resend | `resend`, `@resend`, `RESEND_API_KEY` | API key, from address |
| SendGrid | `sendgrid`, `@sendgrid/mail`, `SENDGRID_API_KEY` | API key, from address |
| Postmark | `postmark`, `POSTMARK_API_TOKEN` | Server token, from address |
| AWS SES | `@aws-sdk/client-ses`, `SES_REGION` | Region, credentials |
| Mailgun | `mailgun`, `MAILGUN_API_KEY` | API key, domain |
| Loops | `loops`, `LOOPS_API_KEY` | API key |

### 1.2: Email Template Detection

Search for existing email templates:
- `src/emails/` directory (React Email templates)
- `templates/email/` or `emails/` directory
- Edge Functions that send emails (search for Resend/SendGrid calls in `supabase/functions/`)
- HTML email templates anywhere in the project

### 1.3: Design System Detection

Extract brand styling for email templates:
- Brand colors from `tailwind.config.*` or CSS variables
- Logo files from `public/` or `src/assets/`
- Font choices from the design system
- Email-specific styles if they exist (e.g., `src/emails/components/`)

### 1.4: Existing Sequences Detection

Search for any existing email sequences or drip campaigns:
- Scheduled/delayed email sends
- Cron jobs or Edge Functions that trigger emails
- User lifecycle event handlers that send emails

Present findings:
```
Email Infrastructure Detected:

| Component | Status | Details |
|-----------|--------|---------|
| Provider | Resend | API key in .env, from: hello@product.com |
| Templates | 8 found | src/emails/ (React Email) |
| Design System | Matched | Brand colors + logo extracted |
| Existing Sequences | 1 found | Welcome email on signup |
| Drip Infrastructure | None | No scheduled sequences detected |
```

## Phase 2: Choose Sequence Type

Parse `$ARGUMENTS` for the sequence type. If not provided, present options:

```
Which email sequence do you want to create?

1. WELCOME -- New user onboarding (3-5 emails over 7 days)
   Best when: Activation score < 60, users don't complete onboarding

2. ACTIVATION -- Drive users to first key action (3-4 emails over 5 days)
   Best when: Users sign up but don't reach "aha moment"

3. RETENTION -- Re-engage inactive users (4-6 emails over 14 days)
   Best when: Retention score < 50, high churn after week 1

4. WIN-BACK -- Recover churned users (3 emails over 21 days)
   Best when: Revenue declining, significant churned user base

5. UPSELL -- Upgrade free users to paid (3-4 emails over 10 days)
   Best when: High free user base, low free-to-paid conversion

Choose a number (1-5):
```

If `.gtm/funnel/` exists with a recent diagnosis, recommend the sequence type that addresses the identified bottleneck.

## Phase 3: Generate Email Templates

For the chosen sequence type, generate complete email templates.

### 3.1: Welcome Sequence (5 emails)

| # | Day | Subject | Goal |
|---|-----|---------|------|
| 1 | 0 | Welcome to {Product} -- here's how to get started | Orient, set expectations |
| 2 | 1 | Your first {key_action} in 3 steps | Drive first activation |
| 3 | 3 | Did you know? {Feature} can save you {benefit} | Feature education |
| 4 | 5 | How {user_type} use {Product} to {outcome} | Social proof |
| 5 | 7 | You're all set -- what's next? | Transition to regular usage |

### 3.2: Activation Sequence (4 emails)

| # | Day | Subject | Goal |
|---|-----|---------|------|
| 1 | 0 | One thing stands between you and {outcome} | Create urgency for first action |
| 2 | 2 | 3 minutes to your first {result} | Lower perceived effort |
| 3 | 4 | {X} people completed this step today | Social proof + FOMO |
| 4 | 6 | Need help getting started? | Offer support, remove blockers |

### 3.3: Retention Sequence (5 emails)

| # | Day | Subject | Goal |
|---|-----|---------|------|
| 1 | 3 | We noticed you haven't been back -- everything OK? | Soft re-engagement |
| 2 | 7 | New: {Feature} just launched | Give a reason to return |
| 3 | 10 | {Peer_group} achieved {result} this week | Social proof |
| 4 | 14 | Your {product} progress report | Personalized value reminder |
| 5 | 21 | Last chance: {offer} expires soon | Urgency/incentive |

### 3.4: Win-Back Sequence (3 emails)

| # | Day | Subject | Goal |
|---|-----|---------|------|
| 1 | 0 | We've made some changes you'll love | Product improvement hook |
| 2 | 7 | {Special_offer} for returning members | Incentive |
| 3 | 21 | We'll miss you -- here's what you're leaving behind | Loss aversion + final offer |

### 3.5: Upsell Sequence (4 emails)

| # | Day | Subject | Goal |
|---|-----|---------|------|
| 1 | 0 | You've hit the ceiling -- here's the next level | Feature limitation awareness |
| 2 | 3 | What {Product} Pro unlocks for you | Benefit showcase |
| 3 | 7 | {Similar_user} upgraded and saw {result} | Social proof |
| 4 | 10 | Limited: {discount}% off your first {period} | Time-limited offer |

### 3.6: Template Structure

For each email, generate:

```markdown
## Email {N}: {Subject}
Send: Day {X} after {trigger_event}
Condition: {skip if user already completed action / opened previous email}

### Subject Line
Primary: {subject}
A/B variant: {alternative subject}

### Preview Text
{40-90 chars that complement the subject}

### Body
{Full email body in markdown, matching project brand voice}
- Use short paragraphs (2-3 sentences max)
- One clear CTA per email
- Include personalization tokens: {first_name}, {product_name}, {key_metric}
- Mobile-friendly: no wide images or complex layouts

### CTA
Text: {button text}
URL: {product_url}?utm_source=email&utm_medium=drip&utm_campaign={sequence_name}&utm_content=email_{N}

### Design Notes
Background: {brand color or white}
CTA Button: {brand primary color}
Logo: Include at top
Footer: Unsubscribe link + company address
```

## Phase 4: Preview and Approve

Present each email to the user for review:

1. Show the email subject, preview text, and body in a readable format.
2. For each email, ask: **"Approve, modify, or skip this email? (approve/modify/skip)"**
   - If "modify": ask what to change, regenerate, and re-present.
   - If "skip": remove from the sequence.
   - If "approve": mark as ready.
3. After all emails are reviewed, show the complete sequence timeline:

```
Approved Sequence: {type}

Day 0: "{Subject 1}" -- Approved
Day 1: "{Subject 2}" -- Approved
Day 3: "{Subject 3}" -- Modified
Day 5: (skipped)
Day 7: "{Subject 5}" -- Approved

Total: {N} emails over {X} days
```

Ask: **"Deploy this sequence now, or save for later? (deploy/save)"**

## Phase 5: Deploy or Save

### 5.1: Save as Code (Default)

Save email templates to the project codebase:

If React Email templates are detected (`src/emails/`):
- Generate React Email components matching the existing style
- Save to `src/emails/sequences/{sequence-type}/`
- Create an index file with the sequence configuration

If no React Email:
- Save as HTML templates to `.gtm/emails/{sequence-type}/`
- Include inline CSS for email client compatibility

Save the sequence configuration to `.gtm/emails/{sequence-type}/sequence.json`:
```json
{
  "name": "{sequence_type}",
  "created": "{ISO date}",
  "trigger_event": "{event that starts the sequence}",
  "emails": [
    {
      "day": 0,
      "subject": "{subject}",
      "subject_variant": "{A/B variant}",
      "preview_text": "{preview}",
      "template_file": "{filename}",
      "condition": "{skip condition}",
      "cta_url": "{url with UTMs}"
    }
  ]
}
```

### 5.2: Deploy via Provider API

If the user chooses "deploy" and the email provider supports sequences:

**Resend**: Resend does not natively support drip sequences. Save templates and provide implementation guidance:
- Create a Supabase Edge Function or cron job to handle scheduling
- Use `supabase.functions.invoke()` to trigger each email at the right time
- Store sequence state in the database

**SendGrid**: Use the SendGrid Automation API to create the sequence.

**Loops**: Use the Loops API to create the drip campaign directly.

For providers without native sequence support, generate the implementation code:
- Database table for tracking sequence state per user
- Edge Function or cron job for sending scheduled emails
- Event handlers for trigger events

## Phase 6: Output

```
Email Sequence Created: {type}

| # | Day | Subject | Status |
|---|-----|---------|--------|
| 1 | 0 | {subject} | Saved |
| 2 | 1 | {subject} | Saved |
| ... | ... | ... | ... |

Templates: {location}
Config: .gtm/emails/{sequence-type}/sequence.json

Implementation notes:
- Trigger event: {event}
- Provider: {detected provider}
- Deployment: {method -- code saved / API deployed / manual setup needed}

Next:
- Run /gtm-experiment to A/B test subject lines
- Run /gtm-funnel to re-score after implementation
- Run /gtm-metrics to track email performance
```

## Error Handling

- **No email provider detected**: Ask the user which provider they use or recommend Resend for new projects. Save templates as HTML for manual upload.
- **Provider API errors**: Log the error, save templates locally, and provide manual deployment instructions.
- **No design system detected**: Use a clean, minimal email design (white background, dark text, single brand color for CTA).
- **Conflicting templates**: If existing email templates have a very different style, ask the user whether to match the existing style or create a new one.
- **Missing trigger events**: If the trigger event (e.g., "user signed up") is not tracked in the codebase, note: "Trigger event '{event}' not found in codebase. You'll need to add this event to your auth flow before the sequence can fire."
