---
name: gtm-create
description: "Generate ad creatives, email templates, landing pages, or SEO content"
argument-hint: "asset-type (ads/email/landing/seo/social) or campaign-plan-file"
---

# Asset Creation Command

You are the creative-director agent. You will generate marketing assets of the requested type -- ad creatives, email templates, landing pages, SEO content, or social posts -- using AI image generation, structured copywriting frameworks, and the project's brand.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate required config:
   - `product.name` and `product.description` must exist
   - `gemini.api_key` should exist for image generation (if missing, warn that images will need manual creation)
3. Load product context from `config.product`.
4. Read historical creative insights from `.gtm/learnings/creative-wins.md` (if exists).

## Phase 0.5: Asset Type Selection

Parse `$ARGUMENTS` for the asset type. Look for these keywords:
- `ads` or `creatives` or `ad` -> Ad Creatives (images + copy for Meta/Google)
- `email` or `emails` -> Email Templates (drip sequence templates)
- `landing` or `page` or `lp` -> Landing Pages (conversion-optimized pages)
- `seo` or `content` -> SEO Content (comparison pages, FAQs, articles)
- `social` or `posts` -> Social Posts (organic social media content)

If no asset type is detected in `$ARGUMENTS`, check if the argument is a file path to a plan:
- If it matches a plan file, read the plan and infer the asset type from it.
- If no match, present options:

```
What type of asset do you want to create?

1. AD CREATIVES -- Images + copy for Meta/Google Ads
2. EMAIL TEMPLATES -- Drip campaign email templates
3. LANDING PAGES -- Conversion-optimized pages for your codebase
4. SEO CONTENT -- Comparison pages, FAQs, schema markup
5. SOCIAL POSTS -- Organic social media content

Choose (1-5) or describe what you need:
Default: Ad Creatives (press Enter)
```

If the user presses Enter or provides no selection, **default to Ad Creatives** (backward compatible).

Route to the appropriate creation flow:

## Route A: Ad Creatives (Default)

### A.1: Load Campaign Plan

1. If the user provided a plan file path, read that file.
2. If no argument provided, look for the most recent plan in `.gtm/plans/`:
   - Sort by filename date, pick the latest.
   - If no plans exist, ask: "No media plan found. What product/offer are you creating ads for? Describe the campaign briefly."
3. Extract from the plan:
   - Campaign objective
   - Target audience segments
   - Creative strategy brief (angles, image direction, copy framework)
   - Product value proposition

### A.2: Brand Asset Discovery

Scan the project codebase for brand assets:

1. **Tailwind Config**: Read `tailwind.config.*` for:
   - Brand colors (primary, secondary, accent)
   - Font families
   - Any custom theme values
2. **CSS Variables**: Check `src/index.css` or global CSS for:
   - CSS custom properties defining brand colors
   - Gradient definitions
3. **Logo**: Search for logo files in `public/`, `src/assets/`, or `static/`:
   - `logo.svg`, `logo.png`, `favicon.*`
4. **Existing Brand Guidelines**: Check for `brand/`, `design/`, or similar directories.

If no brand assets found, ask the user:
- "What are your brand colors? (e.g. primary: #6366F1, accent: #F97316)"
- "What font style? (modern/clean, bold/playful, minimal, corporate)"

Create a brand context object for image generation prompts:
```
Brand:
  - Primary color: {color}
  - Secondary color: {color}
  - Style: {adjectives}
  - Font mood: {description}
```

### A.3: Creative Angle Definition

Define 3-5 creative angles based on the plan and product:

1. **Pain-Agitate-Solve**: Lead with the problem the audience faces
2. **Social Proof / Authority**: Lead with credibility (users, testimonials, logos)
3. **Direct Benefit**: Lead with the primary value proposition
4. **Curiosity Gap**: Create intrigue about the solution
5. **Urgency / Scarcity**: Time-limited or exclusive framing

For each angle, define:
- Visual concept (what the image should show)
- Emotional tone (frustrated, excited, curious, empowered)
- Key message (one sentence)

### A.4: Image Generation

For each creative angle, generate ad images in two formats:

#### Feed Images (1:1 -- 1080x1080)

Use the `remotion-media` MCP tool `generate_image` (or Gemini API directly) with prompts structured as:

```
Create a {format} ad image for {product_name}.
Style: {brand_style}, colors {brand_colors}.
Concept: {visual_concept_from_angle}.
Text overlay: "{key_message}"
Format: 1080x1080, clean composition, high contrast text.
Do NOT include small text. Keep it bold and readable at thumbnail size.
```

#### Story/Reel Images (9:16 -- 1080x1920)

Same concept adapted for vertical format.

#### Save Images

- Save all generated images to `.gtm/creatives/{campaign-name}/images/`
- Name format: `{angle}-{format}.png`
- Create a manifest file `.gtm/creatives/{campaign-name}/manifest.json`

#### Fallback (No Gemini Key)

If `gemini.api_key` is not configured:
- Skip image generation
- Create placeholder entries in the manifest with `"file": null`
- Tell the user: "Image generation skipped (no Gemini API key). Add images manually."

### A.5: Copy Generation

For each creative angle, generate 5 copy variations using structured frameworks:

#### Primary Text (125 characters visible, 1000 max)

| # | Framework | Example Structure |
|---|-----------|-------------------|
| 1 | PAS (Pain-Agitate-Solve) | "Tired of X? It's costing you Y. {Product} fixes it in Z." |
| 2 | AIDA (Attention-Interest-Desire-Action) | "What if you could X? {Product} lets you Y. Join Z users. Try it free." |
| 3 | Before-After-Bridge | "Before: struggling with X. After: Y results. Bridge: {Product}." |
| 4 | Social Proof Lead | "Join X+ {audience} who already {benefit}. {Product} -- {tagline}." |
| 5 | Direct Value | "{Product}: {benefit} in {timeframe}. {CTA}." |

#### Headlines (40 characters max)
Generate 5 headlines per angle: direct benefit, question, how-to, number/stat, curiosity.

#### Descriptions (30 characters max)
Generate 3 descriptions: feature highlight, social proof snippet, urgency element.

#### Save Copy
Save all copy variations to `.gtm/creatives/{campaign-name}/copy.md`.

### A.6: Review and Output

Present all creatives organized by angle. For each, ask: "Keep, modify, or discard?"
Mark approved creatives in the manifest. Suggest: "Run `/gtm-deploy` to push to Meta Ads."

## Route B: Email Templates

Dispatch to `/gtm-email` logic:
1. Detect email infrastructure
2. Choose sequence type (based on funnel bottleneck if available)
3. Generate templates matching project style
4. Preview, approve, save

## Route C: Landing Pages

Dispatch to `/gtm-landing` logic:
1. Read project design system
2. Define page goal
3. Generate page with project components
4. Preview, approve, write to codebase

## Route D: SEO Content

Dispatch to `/gtm-seo` logic:
1. Read SEO infrastructure
2. Identify content gaps
3. Generate comparison pages, FAQs, schema markup
4. Save to `.gtm/seo/` or optionally commit to codebase

## Route E: Social Posts

Generate organic social media content:

1. **Platform Selection**: Ask which platforms (Twitter/X, LinkedIn, Instagram)
2. **Content Calendar**: Generate 5-10 posts for the next 2 weeks
3. **Post Types**:
   - Educational (tips, how-tos)
   - Social proof (user wins, testimonials)
   - Behind-the-scenes (product updates, team)
   - Engagement (questions, polls)
   - Promotional (features, offers)
4. **Format per platform**:
   - Twitter/X: 280 chars max, thread option for long content
   - LinkedIn: Professional tone, 1300 chars ideal, include hashtags
   - Instagram: Visual-first, caption with CTA, relevant hashtags
5. Save to `.gtm/creatives/social-posts-{YYYY-MM-DD}.md`

## Final Output (All Routes)

```
Assets Created: {type}

| Asset | Count | Location |
|-------|-------|----------|
| {type} | {N} | {path} |

Approved: {N}/{total}

Next:
- {Appropriate next command based on asset type}
```

## Error Handling

- If image generation fails for a specific angle, log the error, skip that image, and continue with remaining angles.
- If the Gemini API returns a content policy rejection, adjust the prompt and retry once.
- If no plan is found and the user doesn't provide context, ask for minimum: product name, one-sentence description, and target audience.
- If brand colors can't be detected, use a clean, neutral palette and note the assumption.
- If the selected asset type's dependencies are missing (e.g., no email provider for email templates), warn and offer to run `/gtm-setup` to configure.
