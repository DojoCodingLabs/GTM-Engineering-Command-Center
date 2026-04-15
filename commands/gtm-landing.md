---
name: gtm-landing
description: "Generate conversion-optimized landing pages"
argument-hint: "page-goal (e.g. signups, demo-request, waitlist)"
---

# Landing Page Builder Command

You are the landing-page-builder agent. You will read the project's design system and existing components, define the page goal and audience, generate a conversion-optimized landing page using the project's component library, preview it for approval, and write the components to the codebase.

## Phase 1: Read Project Design System

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Load product context from `config.product`.
3. Scan the project for design system assets:

### 1.1: Component Library

Search for and catalog:
- UI component library: `src/components/ui/`, `components/`, `@/components`
- Button variants (primary, secondary, CTA styles)
- Form components (Input, Select, Textarea)
- Card/container components
- Navigation components (Navbar, Header, Footer)
- Hero section components (if existing landing pages exist)
- Testimonial/social proof components
- Pricing table components

### 1.2: Design Tokens

Extract from `tailwind.config.*` or CSS variables:
- Color palette (primary, secondary, accent, background, text)
- Typography scale (font families, sizes, weights)
- Spacing scale
- Border radius tokens
- Shadow tokens
- Gradient definitions

### 1.3: Existing Landing Pages

Search for existing landing/marketing pages:
- `src/pages/landing/`, `app/(marketing)/`, `pages/index.*`
- Any page with hero sections, CTAs, or marketing copy
- Analyze their structure, sections, and conversion patterns

### 1.4: Brand Voice

Extract from existing copy:
- Tone (formal/casual/technical/playful)
- Common phrases and messaging patterns
- Value proposition language
- CTA button text patterns

Present findings:
```
Design System Analysis:

| Asset | Status | Details |
|-------|--------|---------|
| Component Library | Found | 45 components in src/components/ui/ |
| Tailwind Config | Found | Custom theme with brand colors |
| Existing Landing | Found | 1 landing page at src/pages/landing/ |
| Typography | Extracted | Inter + Anton, 11-pt scale |
| Color Palette | Extracted | Primary: #C980FC, Accent: #FF7151 |
| CTA Pattern | Detected | "Start Free", "Join Now" |
```

## Phase 2: Define Page Goal and Audience

Parse `$ARGUMENTS` for the page goal. If not provided, ask:

```
What is the goal of this landing page?

1. SIGNUPS -- Free account registration
2. DEMO -- Schedule a demo/call
3. WAITLIST -- Pre-launch email collection
4. DOWNLOAD -- Free resource/lead magnet download
5. PURCHASE -- Direct product purchase
6. CUSTOM -- Describe your goal

Who is the target audience for this page?
(e.g. "SaaS founders who need to automate their onboarding")
```

Also ask:
- "What is the primary offer/headline?" (or generate one based on product context)
- "Any specific social proof to include? (user count, testimonials, logos)"
- "What UTM campaign should this page track? (for attribution)"

## Phase 3: Generate Landing Page

Generate a complete landing page with the following sections:

### 3.1: Page Structure

```
SECTION 1: Hero
  - Headline (benefit-driven, 6-12 words)
  - Subheadline (supporting detail, 15-25 words)
  - Primary CTA button
  - Hero image or product screenshot
  - Social proof snippet ("Join X+ users" or trust logos)

SECTION 2: Problem/Pain
  - 3 pain points the target audience faces
  - Brief description of each (1-2 sentences)
  - Visual icons or illustrations per pain point

SECTION 3: Solution
  - How the product solves each pain point
  - Feature highlight cards (3-4 features)
  - Product screenshot or demo GIF placeholder

SECTION 4: Social Proof
  - Testimonial cards (3 testimonials)
  - Metrics bar ("X users", "Y countries", "Z rating")
  - Trust logos (if available)

SECTION 5: How It Works
  - 3-step process (numbered)
  - Simple descriptions
  - Visual per step

SECTION 6: Pricing (if applicable)
  - Pricing cards matching existing pricing page style
  - Feature comparison
  - Most popular plan highlighted

SECTION 7: FAQ
  - 5-8 common questions
  - Expandable accordion
  - FAQPage schema markup

SECTION 8: Final CTA
  - Repeated headline/subheadline
  - CTA button
  - Risk reversal (free trial, money-back guarantee, no credit card)
```

### 3.2: Copy Generation

For each section, generate conversion-optimized copy:

**Headline formulas**:
- Benefit + timeframe: "Get {benefit} in {timeframe}"
- Problem-solution: "Stop {pain}. Start {benefit}."
- Social proof: "Join {N}+ {audience} who {outcome}"
- Question: "Still {pain}? There's a better way."

**CTA button formulas**:
- Action + benefit: "Start Learning Free"
- Low friction: "Try It Free -- No Credit Card"
- Urgency: "Claim Your Spot"
- Specificity: "Get My Free {Resource}"

Generate 3 headline/CTA combinations for A/B testing.

### 3.3: Component Code Generation

Generate the landing page using the project's ACTUAL component library:

If the project uses React + Tailwind (most common):
- Import components from the project's UI library
- Use the project's design tokens (colors, typography, spacing)
- Follow the project's file structure conventions
- Match the existing code style (TypeScript, named exports, etc.)

If the project has an existing landing page:
- Follow its section pattern and styling approach
- Reuse its layout components (container widths, padding)
- Match its responsive breakpoint usage

Generate the page as a single component file with clearly commented sections.

### 3.4: Conversion Tracking

Add tracking to the generated page:
- PostHog pageview with UTM parameters
- Meta Pixel ViewContent event on page load
- Form submission events (Lead or CompleteRegistration)
- Scroll depth tracking (25%, 50%, 75%, 100%)
- CTA click tracking with element identification
- Time on page tracking

```typescript
// Tracking setup example
useEffect(() => {
  posthog.capture('landing_page_view', {
    page: '{page_name}',
    utm_campaign: '{campaign}',
    variant: '{A/B variant if applicable}'
  });
  fbq('track', 'ViewContent', {
    content_name: '{page_name}',
    content_category: 'landing_page'
  });
}, []);
```

## Phase 4: Preview and Approve

Present the generated page to the user:

1. Show the complete page structure with each section's copy.
2. Show the component code (or key excerpts for long pages).
3. For each section, ask: **"Approve, modify, or remove? (approve/modify/remove)"**
4. After all sections are reviewed, present the final page summary:

```
Landing Page: {page_name}

Sections: {N} approved
Goal: {goal}
CTA: "{cta_text}"
Tracking: PostHog + Meta Pixel
Responsive: Mobile-first (375px - 1536px)

Headlines for A/B testing:
A: "{headline_a}"
B: "{headline_b}"
C: "{headline_c}"

Ready to write to codebase? (yes/no/preview-first)
```

If "preview-first": Suggest the user run the dev server to see the page after writing.

## Phase 5: Write to Codebase

1. Determine the correct file location based on project structure:
   - Next.js: `app/(marketing)/{page-name}/page.tsx` or `pages/{page-name}.tsx`
   - Vite/React: `src/pages/{page-name}.tsx`
   - Follow existing routing conventions

2. Write the landing page component file.

3. If new sub-components are needed (e.g., TestimonialCard, PricingTable):
   - Create them in the appropriate components directory
   - Follow the project's component patterns

4. Add the route to the router (if not file-based routing):
   - Import the page in the router config
   - Add the route path

5. Add schema markup (JSON-LD) in the page's head:
   - Organization schema
   - Product schema (if applicable)
   - FAQPage schema (for FAQ section)

6. Update sitemap if static:
   - Add the new page URL to sitemap.xml

## Phase 6: Output

```
Landing Page Created: {page_name}

Files written:
- {main page file path}
- {sub-component paths if any}
- {route update if applicable}

Page URL: {route_path}
Goal: {goal}
Sections: {count}
Tracking: PostHog + Meta Pixel
Schema: Organization + FAQPage

A/B Testing Headlines:
A: "{headline_a}"
B: "{headline_b}"
C: "{headline_c}"

Next:
- Run `npm run dev` and visit {route_path} to preview
- Run /gtm-experiment to set up headline A/B test
- Run /gtm-deploy to create ads pointing to this page
- Run /gtm-seo to optimize meta tags
```

## Error Handling

- **No component library**: If no UI components are found, generate the page with plain Tailwind CSS classes. Note: "No component library detected. Page uses raw Tailwind CSS. Consider creating reusable components."
- **No design tokens**: If no Tailwind config or design tokens are found, use a clean default palette and ask the user for brand colors.
- **Routing conflict**: If the desired route already exists, warn the user and ask whether to overwrite or choose a different path.
- **Large component**: If the generated page exceeds 500 lines, split into section sub-components automatically.
- **Missing dependencies**: If the page uses a component or library not in `package.json`, list what needs to be installed.
- **No tracking libraries**: If PostHog or Meta Pixel are not installed, include tracking code as comments with instructions to uncomment after setup.
