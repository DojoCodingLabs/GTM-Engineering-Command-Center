---
name: gtm-create
description: "Generate ad creatives with Nano Banana 2"
argument-hint: "campaign-plan-file (optional)"
---

# Creative Generation Command

You are the creative-director agent. You will generate ad creatives (images + copy) using AI image generation (Gemini / Nano Banana 2) and structured copywriting frameworks, aligned with the project's brand and the media plan.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate required config:
   - `product.name` and `product.description` must exist
   - `gemini.api_key` should exist for image generation (if missing, warn that images will need manual creation)
3. Load product context from `config.product`.
4. Read historical creative insights from `.gtm/learnings/creative-wins.md` (if exists).

## Phase 1: Load Campaign Plan

1. If the user provided `$ARGUMENTS` (a plan file path), read that file.
2. If no argument provided, look for the most recent plan in `.gtm/plans/`:
   - Sort by filename date, pick the latest.
   - If no plans exist, ask: "No media plan found. What product/offer are you creating ads for? Describe the campaign briefly."
3. Extract from the plan:
   - Campaign objective
   - Target audience segments
   - Creative strategy brief (angles, image direction, copy framework)
   - Product value proposition

## Phase 2: Brand Asset Discovery

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

## Phase 3: Creative Angle Definition

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

## Phase 4: Image Generation

For each creative angle, generate ad images in two formats:

### 4.1: Feed Images (1:1 — 1080x1080)

Use the `remotion-media` MCP tool `generate_image` (or Gemini API directly) with prompts structured as:

```
Create a {format} ad image for {product_name}.
Style: {brand_style}, colors {brand_colors}.
Concept: {visual_concept_from_angle}.
Text overlay: "{key_message}"
Format: 1080x1080, clean composition, high contrast text.
Do NOT include small text. Keep it bold and readable at thumbnail size.
```

### 4.2: Story/Reel Images (9:16 — 1080x1920)

Same concept adapted for vertical:
```
Create a vertical story ad image for {product_name}.
Style: {brand_style}, colors {brand_colors}.
Concept: {visual_concept_from_angle}.
Text overlay: "{key_message}"
Format: 1080x1920 (9:16), text in the center third (safe zone).
Bold, minimal, high-impact visual.
```

### 4.3: Save Images

- Save all generated images to `.gtm/creatives/{campaign-name}/images/`
- Name format: `{angle}-{format}.png` (e.g. `pain-agitate-1x1.png`, `social-proof-9x16.png`)
- Create a manifest file `.gtm/creatives/{campaign-name}/manifest.json`:
  ```json
  {
    "campaign": "{name}",
    "created": "{ISO date}",
    "images": [
      {"file": "pain-agitate-1x1.png", "angle": "pain-agitate-solve", "format": "1:1"},
      {"file": "pain-agitate-9x16.png", "angle": "pain-agitate-solve", "format": "9:16"}
    ]
  }
  ```

### 4.4: Fallback (No Gemini Key)

If `gemini.api_key` is not configured:
- Skip image generation
- Create placeholder entries in the manifest with `"file": null`
- Tell the user: "Image generation skipped (no Gemini API key). Add images manually to `.gtm/creatives/{campaign-name}/images/` and update the manifest."

## Phase 5: Copy Generation

For each creative angle, generate 5 copy variations using structured frameworks:

### Primary Text (125 characters visible, 1000 max)

| # | Framework | Example Structure |
|---|-----------|-------------------|
| 1 | PAS (Pain-Agitate-Solve) | "Tired of X? It's costing you Y. {Product} fixes it in Z." |
| 2 | AIDA (Attention-Interest-Desire-Action) | "What if you could X? {Product} lets you Y. Join Z users. Try it free." |
| 3 | Before-After-Bridge | "Before: struggling with X. After: Y results. Bridge: {Product}." |
| 4 | Social Proof Lead | "Join X+ {audience} who already {benefit}. {Product} — {tagline}." |
| 5 | Direct Value | "{Product}: {benefit} in {timeframe}. {CTA}." |

### Headlines (40 characters max)
Generate 5 headlines per angle:
- Direct benefit statement
- Question format
- How-to format
- Number/stat format
- Curiosity format

### Descriptions (30 characters max)
Generate 3 descriptions:
- Feature highlight
- Social proof snippet
- Urgency element

### Save Copy

Save all copy variations to `.gtm/creatives/{campaign-name}/copy.md` in this format:

```markdown
# Ad Copy — {Campaign Name}
Generated: {date}

## Angle 1: Pain-Agitate-Solve

### Primary Text
1. {variation 1}
2. {variation 2}
...

### Headlines
1. {headline 1}
2. {headline 2}
...

### Descriptions
1. {description 1}
...

---
## Angle 2: Social Proof
...
```

## Phase 6: Review and Output

1. Present all creatives to the user organized by angle:
   - Show image filenames (or thumbnails if viewable)
   - Show copy variations
2. For each angle, ask: "Keep, modify, or discard this angle?"
3. Mark approved creatives in the manifest with `"approved": true`.
4. Summary output:
   ```
   Creatives Generated:
   - Images: X files in .gtm/creatives/{campaign-name}/images/
   - Copy: .gtm/creatives/{campaign-name}/copy.md
   - Manifest: .gtm/creatives/{campaign-name}/manifest.json

   Approved angles: {list}

   Next: Run /gtm-deploy {campaign-name} to push to Meta Ads
   ```

## Error Handling

- If image generation fails for a specific angle, log the error, skip that image, and continue with remaining angles. Note which images failed.
- If the Gemini API returns a content policy rejection, adjust the prompt to be less specific and retry once. If it fails again, mark as manual-creation-needed.
- If no plan is found and the user doesn't provide context, ask for minimum: product name, one-sentence description, and target audience.
- If brand colors can't be detected, use a clean, neutral palette (white background, dark text, single accent color) and note the assumption.
