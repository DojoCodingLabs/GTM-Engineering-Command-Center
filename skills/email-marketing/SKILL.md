---
name: email-marketing
description: Email marketing automation — drip sequences, deliverability, template patterns, provider APIs (Resend, SendGrid, Postmark)
---

# Email Marketing Automation

Design, build, and optimize email marketing flows for SaaS GTM. This skill covers drip sequence architecture, deliverability engineering, template design patterns, and provider API integration.

## Email Marketing Architecture

```
Email System
  ├── Transactional Emails (account confirmations, password resets, receipts)
  │   └── Triggered by user actions, must send immediately
  ├── Marketing Emails (newsletters, announcements, product updates)
  │   └── Sent to segments on a schedule
  ├── Drip Sequences (automated multi-email flows)
  │   └── Triggered by events, sent on a delay schedule
  └── Lifecycle Emails (onboarding, activation, retention, win-back)
      └── Triggered by user state changes or inactivity
```

## Core Sequences Every SaaS Needs

### 1. Welcome Sequence (Trigger: user signs up)

```
Day 0 (immediate): Welcome + quick-start guide
Day 1: Key feature highlight + "try this" CTA
Day 3: Social proof (testimonials, case studies)
Day 5: "Need help?" with support links + community invite
Day 7: Activation check — if not activated, branch to re-engagement
```

### 2. Activation Sequence (Trigger: signup but no key action)

```
Day 2: "You're 1 step away" — focus on the activation action
Day 4: Video walkthrough of the core feature
Day 7: Success story of someone who activated
Day 10: Direct offer — "Reply to this email and I'll help you set up"
Day 14: Final nudge — "Is [Product] right for you?"
```

### 3. Trial-to-Paid Sequence (Trigger: trial started)

```
Day 0: Trial confirmation + what to expect
Day 3: Feature highlight #1 (most valuable)
Day 5: Feature highlight #2 + comparison to alternatives
Day 7 (mid-trial): Progress check + premium feature preview
Day 10: Customer success story + ROI data
Day 12 (2 days before): Urgency — "Your trial ends in 2 days"
Day 13 (1 day before): Last chance — clear pricing, FAQ
Day 14 (expiry): "Your trial has ended" — extend offer or discount
Day 16 (grace): "We saved your data" — final conversion attempt
```

### 4. Retention/Engagement Sequence (Trigger: no login for 7+ days)

```
Day 7 inactive: "We miss you" + new feature announcement
Day 14 inactive: "Here's what you're missing" + activity digest
Day 21 inactive: Re-engagement offer (discount, extended trial)
Day 30 inactive: "Is everything okay?" — personal outreach feel
Day 45 inactive: Win-back offer (significant discount)
Day 60 inactive: Final email — "Should we close your account?"
```

### 5. Upsell/Expansion Sequence (Trigger: usage threshold reached)

```
Day 0: "You're hitting limits" — data on their usage
Day 2: Feature comparison (current plan vs next tier)
Day 5: ROI calculator or case study of upgrade
Day 7: Limited-time upgrade offer
Day 10: Follow-up if no action taken
```

## Key Metrics

| Metric | Healthy Range | Action if Below |
|--------|--------------|----------------|
| Open Rate | 25-45% | Fix subject lines, sender name, send time |
| Click Rate | 3-8% | Fix CTA, content relevance, design |
| Reply Rate | 1-3% | More personal tone, ask questions |
| Unsubscribe Rate | <0.5% per email | Reduce frequency, improve segmentation |
| Bounce Rate | <2% | Clean list, verify emails at signup |
| Spam Complaint Rate | <0.1% | Critical — fix immediately or domain gets blacklisted |

## Segmentation Strategy

### Behavioral Segments

| Segment | Criteria | Use For |
|---------|----------|---------|
| Power Users | 5+ logins/week, multiple features used | Upsell, referral asks, testimonial requests |
| Engaged | 2-4 logins/week | Feature education, community building |
| At Risk | 1 login/week, declining | Re-engagement, value reminders |
| Dormant | 0 logins for 14+ days | Win-back sequences |
| Churned | Cancelled or expired | Win-back with offers |

### Lifecycle Segments

| Segment | Stage | Primary Goal |
|---------|-------|-------------|
| New Signups | Onboarding | Activation (complete key action) |
| Activated | Using product | Engagement + habit formation |
| Trial Users | Pre-payment | Conversion to paid |
| Paying Customers | Retention | Expansion + advocacy |
| Churned | Lost | Win-back |

### Enrich Segments with the Persona Substrate + SDV Forecasts

Behavioral and lifecycle segments above tell you *what* a user is doing; the **shared persona substrate** (`.gtm/personas/`, `schemas/persona.schema.json`) and **SDV forecasts** (`.gtm/sdv/forecasts/*.forecast.yml`) tell you *what they object to* and *what price they tolerate* — build the persona once, consume it here. Cross the two axes:

- **Persona objections → which email handles which objection.** Each persona carries `pain_points`, and each SDV forecast carries structured `top_objections[]` (segment + objection + severity + `blocker_tier` B0/B1/B2 + `revenue_at_risk`). Map the highest-severity objection *for the persona(s) in a segment* to a specific email: the email that names and dissolves that exact objection. A B0 demand-blocker for a paying persona earns its own dedicated email; a B2 polish objection is a PS line. This is the routing rule — **one SDV-discovered objection, one email that answers it** — not generic benefit copy.
- **Price tolerance → offer framing per persona.** A persona's `price_sensitivity` (`low`/`medium`/`high`) and any SDV `willingness_to_pay` band (Van Westendorp / Gabor-Granger range) set how an upsell/trial-to-paid email frames price: lead with value and a guarantee for high-sensitivity personas (and the lower offer tier), lead with the premium outcome for low-sensitivity personas. Never send the same discount framing to a `low` and a `high` `price_sensitivity` segment.
- **Revenue weighting.** Prioritize sequence build order by the persona's `revenue_pct` and the objection's `revenue_at_risk` — handle the objection costing the most revenue first.

If `.gtm/personas/` is empty, recommend `/gtm-personas derive`; if no SDV forecast exists yet, recommend `/gtm-validate` to discover objections before writing the objection-handling emails (the forecast's `top_objections[]` is the input, not a guess).

## A/B Testing Framework

### What to Test (Priority Order)

1. **Subject line** — 40% impact on opens
2. **Send time** — 20% impact on opens
3. **CTA button text and placement** — 30% impact on clicks
4. **Email length** — varies by audience
5. **Personalization level** — first name, company, usage data
6. **From name** — "Juan from Dojo" vs "Dojo Coding" vs "Dojo Team"

### Statistical Requirements

- Minimum 1,000 recipients per variant
- Run for at least 24 hours (captures all time zones)
- 95% confidence level before declaring winner
- Test one variable at a time
