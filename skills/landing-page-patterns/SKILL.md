---
name: landing-page-patterns
description: Landing page conversion patterns — hero layouts, social proof, CTA optimization, design system integration
---

# Landing Page Conversion Patterns

Design and build high-converting landing pages using proven layout patterns, social proof techniques, CTA optimization, and integration with existing design systems. This skill provides actionable blueprints, not theory.

## Landing Page Architecture

```
Landing Page Structure (top to bottom)
  ├── Hero Section (above the fold — 5 seconds to hook)
  │   ├── Headline (primary value proposition)
  │   ├── Subheadline (supporting detail or objection handling)
  │   ├── Primary CTA (the one action you want)
  │   └── Hero Visual (product screenshot, video, illustration)
  ├── Social Proof Bar (logos, user count, rating)
  ├── Problem/Pain Section (agitate the problem)
  ├── Solution Section (your product as the answer)
  ├── Features/Benefits (3-4 key differentiators)
  ├── Social Proof Deep (testimonials, case studies)
  ├── Pricing (if applicable)
  ├── FAQ (objection handling)
  ├── Final CTA (repeat the hero CTA)
  └── Footer (trust signals, legal, navigation)
```

## Conversion Benchmarks by Page Type

| Page Type | Good CVR | Great CVR | Elite CVR |
|-----------|----------|-----------|-----------|
| SaaS Free Trial | 3-5% | 5-10% | 10-20% |
| Lead Gen (form) | 5-10% | 10-20% | 20-40% |
| E-commerce Product | 2-3% | 3-5% | 5-10% |
| Webinar Registration | 15-25% | 25-40% | 40-60% |
| Newsletter Signup | 2-5% | 5-10% | 10-25% |
| Freemium Signup | 5-8% | 8-15% | 15-30% |

## The 5-Second Test

Every landing page must pass the 5-second test. A new visitor should understand within 5 seconds:
1. **What** you offer
2. **Who** it's for
3. **Why** they should care
4. **What to do** next (CTA)

If any of these is unclear above the fold, the page will underperform regardless of what's below.

## Headline Formulas That Convert

### Formula 1: Outcome + Timeframe
```
"Build Production-Ready Smart Contracts in 30 Days"
"Launch Your SaaS in 2 Weeks with AI-Powered Development"
```

### Formula 2: [Do Thing] Without [Pain Point]
```
"Learn Blockchain Development Without Quitting Your Day Job"
"Scale Your Startup Without Hiring a Marketing Team"
```

### Formula 3: The Only [Category] That [Differentiator]
```
"The Only Coding Bootcamp That Guarantees a Job in Web3"
"The Only GTM Tool That Deploys Campaigns From Your Terminal"
```

### Formula 4: Question That Implies the Answer
```
"What If You Could Ship Features 10x Faster?"
"Ready to Stop Wasting $50K/Year on Ads That Don't Convert?"
```

## Mobile-First Requirements

Landing pages receive 60-80% mobile traffic from paid ads. Every element must work at 375px:

| Element | Desktop | Mobile |
|---------|---------|--------|
| Hero headline | 40-56px | 28-36px |
| Subheadline | 18-24px | 16-18px |
| CTA button | 48px height | 48px height (same -- touch target) |
| Hero image | Side-by-side with text | Below text, full width |
| Feature grid | 3-4 columns | 1 column, stacked |
| Testimonials | Side-by-side cards | Horizontal scroll or stacked |
| Form fields | Multi-column | Single column |

### Mobile CTA Rules

- Sticky CTA bar at bottom of screen after scrolling past hero
- Button must be full-width (or nearly) on mobile
- Minimum 48px touch target height
- Thumb-friendly position (bottom 1/3 of screen)

## Page Speed Requirements

| Metric | Target | Impact |
|--------|--------|--------|
| Time to Interactive | < 3.5s | Every 1s delay = 7% conversion loss |
| First Contentful Paint | < 1.8s | Users see "something" quickly |
| Total Page Weight | < 1.5MB | Critical for mobile/LATAM connections |
| Above-fold images | < 200KB total | Use WebP/AVIF, lazy load below-fold |
| JavaScript bundle | < 200KB gzipped | Code split, defer non-critical |

## Form Optimization

### Field Count Impact on Conversion

| Fields | Relative CVR | When to Use |
|--------|-------------|-------------|
| 1 (email only) | 100% baseline | Newsletter, free tool, top-of-funnel |
| 2 (email + name) | 85% | Free trial, community access |
| 3-4 (+ company, role) | 65% | B2B lead gen, demo requests |
| 5-7 (+ phone, size) | 40% | Enterprise, high-value leads |
| 8+ | 25% | Only for extremely qualified leads |

### Form UX Rules

- Labels above fields (not placeholder-as-label)
- Inline validation (not on submit)
- Progress indicator for multi-step forms
- Auto-focus first field on page load
- Mobile: use appropriate input types (`type="email"`, `type="tel"`)
- Never require fields you don't actually need

## A/B Testing Priority

Test these elements in order of impact:

1. **Headline** (30-50% lift potential)
2. **CTA text and color** (10-30% lift)
3. **Hero image/video** (10-25% lift)
4. **Social proof placement** (5-15% lift)
5. **Form length** (10-40% lift for lead gen)
6. **Page layout** (5-20% lift)

### Minimum Traffic for Testing

- 100 conversions per variant minimum for reliable results
- At $50 CPA and 5% CVR, you need ~2,000 visitors per variant
- Run tests for at least 7 days to capture day-of-week effects
