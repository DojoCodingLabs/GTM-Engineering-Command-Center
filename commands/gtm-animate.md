---
name: gtm-animate
description: "Create animated video ads with Remotion"
argument-hint: "campaign-name"
---

# Animated Video Ad Command

You are the creative-director agent in video mode. You will create short-form animated video ads (15 seconds, vertical 9:16) using the Remotion Superpowers plugin, applying brand styling, kinetic typography, and AI-generated voiceover.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Validate required config:
   - `product.name` — required for script/copy
   - `product.description` — required for script/copy
   - `elevenlabs.api_key` — recommended for voiceover (warn if missing, skip voiceover)
3. Check that the `remotion-superpowers` plugin is available:
   - Verify that `remotion-media` MCP tools are accessible (generate_image, generate_speech, etc.)
   - If not available, tell the user: "Remotion Superpowers plugin is required for video ad creation. Install it first." STOP.
4. Load product context from `config.product`.
5. Read creative insights from `.gtm/learnings/creative-wins.md` (if exists) for winning angles.

## Phase 1: Load Campaign Context

1. Parse `$ARGUMENTS` for the campaign name.
   - If not provided, list available campaigns in `.gtm/creatives/` and ask.
2. Load the campaign's creative assets:
   - Read `.gtm/creatives/{campaign-name}/manifest.json` (if exists)
   - Read `.gtm/creatives/{campaign-name}/copy.md` (if exists)
3. If no campaign creatives exist, ask the user:
   - "What's the key message for this video ad?"
   - "What's the CTA (call to action)?"
4. Read the project's brand assets (same detection as `/gtm-create`):
   - Tailwind config for colors, fonts
   - Logo files
   - Gradient definitions

## Phase 2: Video Script Development

Create a 15-second video ad script. The structure follows the hook-body-CTA formula:

### 2.1: Script Template

```
SCENE 1 (0-3s): THE HOOK
  Visual: {Attention-grabbing opening — bold text animation or striking visual}
  Text: "{Hook line — provocative question or bold statement}"
  Audio: {Sound effect or first word of voiceover}

SCENE 2 (3-7s): THE PROBLEM
  Visual: {Visual representation of the pain point}
  Text: "{Problem statement — what the audience struggles with}"
  Audio: {Voiceover continues}

SCENE 3 (7-11s): THE SOLUTION
  Visual: {Product showcase or benefit demonstration}
  Text: "{Product name + key benefit}"
  Audio: {Voiceover — how the product solves the problem}

SCENE 4 (11-15s): THE CTA
  Visual: {Logo + CTA button animation + URL}
  Text: "{CTA text — Sign Up Free, Try It Now, etc.}"
  Audio: {Voiceover — clear call to action}
```

### 2.2: Generate 3 Script Variations

Based on the top-performing creative angles (from learnings or campaign copy):

1. **Pain-Point Hook**: Opens with the problem ("Still doing X manually?")
2. **Result Hook**: Opens with the outcome ("Join 1,000+ {audience} who...")
3. **Curiosity Hook**: Opens with intrigue ("The secret to X that nobody talks about")

Present all 3 scripts to the user. Ask which to produce (or produce all).

## Phase 3: Visual Asset Generation

For each approved script, generate the visual assets:

### 3.1: Background Images/Graphics

Use the `remotion-media` MCP `generate_image` tool for each scene:

```
Scene 1 (Hook): Bold gradient background with brand colors ({primary_color} to {secondary_color})
Scene 2 (Problem): Visual metaphor for the pain point, dark/frustrated mood
Scene 3 (Solution): Product screenshot or benefit visualization, bright/positive mood
Scene 4 (CTA): Clean background with brand gradient, space for logo and CTA button
```

Generate at 1080x1920 (9:16 vertical) resolution.

### 3.2: Brand Elements

Extract from the project's design system:
- **Primary gradient**: Use brand colors for background gradients
- **Logo**: Use detected logo file
- **Font style**: Match the project's font mood (modern, bold, minimal, etc.)
- **CTA button style**: Match the product's button design

### 3.3: Kinetic Typography Settings

Define text animation parameters:
- **Hook text**: Large, bold, center-screen. Animation: scale-in or typewriter effect.
- **Problem text**: Medium, center. Animation: fade-in with subtle slide.
- **Solution text**: Large, with product name highlighted in brand accent color. Animation: pop-in.
- **CTA text**: Large, with animated button below. Animation: pulse or glow effect.

Typography specs:
```
font-family: {from tailwind config or "Inter"}
hook-size: 64px, bold, uppercase
body-size: 48px, semibold
cta-size: 56px, bold
text-color: white (on dark backgrounds) or dark (on light backgrounds)
highlight-color: {brand accent color}
```

## Phase 4: Voiceover Generation

### 4.1: Generate Voiceover Script

From the scene scripts, create a continuous voiceover text:
```
"{Hook line}. {Problem expansion}. {Solution with product name}. {CTA — visit URL or action}."
```

Total voiceover should be ~35-40 words for 15 seconds (comfortable speaking pace).

### 4.2: Generate Audio

If ElevenLabs is configured (`elevenlabs.api_key` exists in config):

Use the `remotion-superpowers` ElevenLabs MCP tools:
1. List available voices with `search_voices` or `list_models`
2. Select a voice appropriate for the brand:
   - Professional/authoritative for B2B
   - Friendly/energetic for B2C
   - Ask user preference if unclear
3. Generate the voiceover using `text_to_speech`:
   - Model: `eleven_multilingual_v2` (or latest available)
   - Speed: 1.0x (natural pace for 15s)
4. Save the audio file to `.gtm/creatives/{campaign-name}/video/voiceover-{variation}.mp3`

### 4.3: Fallback (No ElevenLabs)

If ElevenLabs is not configured:
- Use the `remotion-media` MCP `generate_speech` tool as a fallback
- If no TTS is available, skip voiceover and note: "Voiceover skipped — add manually or configure ElevenLabs API key in `.gtm/config.json`"
- The video will be text-only with background music

## Phase 5: Background Music

Use the `remotion-media` MCP `generate_music` tool:

```
Generate a 15-second background track.
Mood: {energetic/calm/inspiring/dramatic — based on ad tone}
Genre: {electronic/ambient/corporate — based on brand}
Tempo: Medium-fast for ads
No vocals. Clean, modern production.
```

Save to `.gtm/creatives/{campaign-name}/video/music-{variation}.mp3`

If music generation is unavailable, use `generate_sound_effect` for a simple audio bed, or skip and note that background music needs to be added manually.

## Phase 6: Remotion Composition

Use the Remotion Superpowers plugin to compose the final video.

### 6.1: Create the Remotion Project

Invoke the `remotion-superpowers` `create-video` or `create-short` skill:

Composition spec:
```
Duration: 15 seconds (450 frames at 30fps)
Resolution: 1080x1920 (9:16 vertical)
FPS: 30

Scenes:
  Scene 1 (frames 0-90):
    - Background: {generated image or gradient}
    - Text: "{hook}" with scale-in animation
    - Audio: voiceover start

  Scene 2 (frames 90-210):
    - Background: {generated image}
    - Text: "{problem}" with fade-in from bottom
    - Audio: voiceover continues

  Scene 3 (frames 210-330):
    - Background: {generated image}
    - Text: "{solution}" with pop-in, product name in accent color
    - Audio: voiceover continues

  Scene 4 (frames 330-450):
    - Background: brand gradient
    - Logo: centered, subtle animation
    - CTA: "{cta text}" with pulse animation
    - CTA Button: rounded rectangle with brand color, text inside
    - Audio: voiceover CTA + music swell

Transitions: Smooth crossfade (15 frames) between scenes
Background music: {generated track}, volume at 30% under voiceover
```

### 6.2: Add Captions (Optional)

If voiceover was generated, use the `remotion-superpowers` `add-captions` skill:
- Style: TikTok-style word-by-word animated captions
- Position: Bottom third of frame (safe zone)
- Font: Bold, with background highlight for readability

### 6.3: Render to MP4

Render the composition to MP4:
- Codec: H.264
- Quality: High (CRF 18-20)
- Output: `.gtm/creatives/{campaign-name}/video/{variation-name}.mp4`

## Phase 7: Output

Save all video assets to `.gtm/creatives/{campaign-name}/video/`:
```
video/
├── {variation-1}.mp4           # Final rendered video
├── {variation-2}.mp4           # Second variation (if produced)
├── voiceover-{variation}.mp3   # Voiceover audio
├── music-{variation}.mp3       # Background music
├── script.md                   # Video scripts
└── assets/                     # Generated images used in scenes
    ├── scene1-hook.png
    ├── scene2-problem.png
    ├── scene3-solution.png
    └── scene4-cta.png
```

Update the campaign manifest (`.gtm/creatives/{campaign-name}/manifest.json`) to include video entries:
```json
{
  "file": "video/{variation-name}.mp4",
  "type": "video",
  "format": "9:16",
  "duration": "15s",
  "angle": "{creative_angle}",
  "has_voiceover": true,
  "has_music": true,
  "approved": false
}
```

Present the result:
```
Video Ad Created:
- File: .gtm/creatives/{campaign-name}/video/{name}.mp4
- Duration: 15s | Format: 9:16 (1080x1920)
- Voiceover: {Yes/Skipped}
- Music: {Yes/Skipped}
- Captions: {Yes/Skipped}

Script:
{Display the script used}

Review the video and mark as approved.
Then run /gtm-deploy {campaign-name} to upload to Meta Ads.
```

## Error Handling

- **Remotion plugin not available**: Tell the user to install the `remotion-superpowers` plugin. Provide: "Run `claude plugin install remotion-superpowers` to install." STOP.
- **ElevenLabs unavailable**: Skip voiceover, produce text-only video with music. Note: "Voiceover skipped. Add ElevenLabs API key to `.gtm/config.json` for AI voiceover."
- **Music generation fails**: Produce video without music. Note: "Background music skipped. Add music manually in post-production."
- **Image generation fails**: Use solid brand-color backgrounds with text overlays only. Note which scenes used fallback.
- **Render fails**: Show the Remotion error, suggest checking Node.js version and ffmpeg installation. Common fix: `npx remotion upgrade`
- **File too large for Meta**: Meta video ads max 4GB, recommended <100MB. If output is too large, suggest reducing quality or duration.
