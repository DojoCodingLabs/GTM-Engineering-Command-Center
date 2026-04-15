# Email Template Patterns -- Modular Design, Responsive Layout, and CTA Placement

## Template Architecture

### Modular Email System

Build emails from reusable modules, not monolithic templates. Each module is a self-contained block.

```
Email Template = Header + [Content Modules] + Footer

Header Module:
  ├── Logo (linked to homepage)
  ├── Navigation links (optional, keep to 2-3 max)
  └── Preview text override

Content Modules (pick 2-4 per email):
  ├── Hero Image Block
  ├── Text Block (heading + body + optional CTA)
  ├── Feature Block (icon + heading + description)
  ├── Testimonial Block (quote + name + photo)
  ├── Stats Block (3-4 metrics in a row)
  ├── CTA Block (button + optional supporting text)
  ├── Two-Column Block (image + text side by side)
  ├── Card Grid Block (2-3 cards in a row)
  └── Divider Block (horizontal rule or spacing)

Footer Module:
  ├── Social links
  ├── Unsubscribe link (legally required)
  ├── Physical address (CAN-SPAM requirement)
  ├── Preference center link
  └── "Why you received this" explanation
```

### Email Width Standards

```
Maximum width: 600px (universal compatibility)
Content padding: 20px left/right (content area = 560px)
Mobile: 100% width, stacked layout

Why 600px?
  - Gmail clips emails wider than ~640px
  - Outlook rendering engine uses Word's HTML renderer (yes, really)
  - Preview panes on desktop are typically 600-700px wide
  - Mobile devices show full-width, so 600px works on all screens
```

## Responsive Email Patterns

### The Single-Column Layout

Best for: most emails. Highest compatibility across email clients.

```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center" style="padding: 0 16px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0"
             style="max-width: 600px; width: 100%;">
        <!-- Content rows here -->
        <tr>
          <td style="padding: 24px 20px; font-family: -apple-system, BlinkMacSystemFont,
                      'Segoe UI', Roboto, sans-serif; font-size: 16px; line-height: 1.5;
                      color: #333333;">
            <h1 style="margin: 0 0 16px; font-size: 24px; color: #111111;">
              Headline here
            </h1>
            <p style="margin: 0 0 24px;">
              Body text here. Keep paragraphs short -- 2-3 sentences max.
            </p>
            <a href="https://example.com" style="display: inline-block; padding: 12px 24px;
               background-color: #C980FC; color: #ffffff; text-decoration: none;
               border-radius: 6px; font-weight: 600;">
              Call to Action
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
```

### Two-Column to Single-Column (Responsive)

```html
<!--[if mso]>
<table role="presentation" width="600" cellpadding="0" cellspacing="0">
<tr><td width="280" valign="top">
<![endif]-->
<div style="display: inline-block; width: 100%; max-width: 280px; vertical-align: top;">
  <!-- Left column content -->
</div>
<!--[if mso]>
</td><td width="280" valign="top">
<![endif]-->
<div style="display: inline-block; width: 100%; max-width: 280px; vertical-align: top;">
  <!-- Right column content -->
</div>
<!--[if mso]>
</td></tr></table>
<![endif]-->
```

### Dark Mode Support

```html
<!-- Add meta tag for dark mode support -->
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">

<style>
  :root { color-scheme: light dark; }

  @media (prefers-color-scheme: dark) {
    .email-body { background-color: #1a1a2e !important; }
    .email-text { color: #e0e0e0 !important; }
    .email-heading { color: #ffffff !important; }
    .email-card { background-color: #16213e !important; }
    /* Logo: provide a light version for dark mode */
    .logo-light { display: none !important; }
    .logo-dark { display: block !important; }
  }
</style>
```

### Font Stack

```css
/* Primary font stack (cross-client compatible) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, sans-serif;

/* Why this order:
   -apple-system: macOS/iOS system font (San Francisco)
   BlinkMacSystemFont: Chrome on macOS
   Segoe UI: Windows
   Roboto: Android, Chrome OS
   Helvetica Neue: Older macOS
   Arial: Universal fallback
   sans-serif: Final fallback
*/

/* Never use web fonts as primary -- many email clients block them */
/* Google Fonts work in: Apple Mail, iOS Mail, Android native, Thunderbird */
/* Google Fonts DON'T work in: Gmail, Outlook (all versions), Yahoo */
```

## CTA Button Patterns

### The Bulletproof Button

Works in every email client including Outlook:

```html
<!-- Bulletproof button using VML for Outlook -->
<table role="presentation" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
  <tr>
    <td style="border-radius: 6px; background-color: #C980FC;" align="center">
      <!--[if mso]>
      <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml"
                   href="https://example.com"
                   style="height:44px;width:200px;v-text-anchor:middle;"
                   arcsize="14%" stroke="false" fillcolor="#C980FC">
        <w:anchorlock/>
        <center>
      <![endif]-->
      <a href="https://example.com"
         style="display: inline-block; padding: 12px 24px; color: #ffffff;
                font-family: -apple-system, sans-serif; font-size: 16px;
                font-weight: 600; text-decoration: none; border-radius: 6px;
                background-color: #C980FC; line-height: 1;">
        Start Free Trial
      </a>
      <!--[if mso]>
        </center>
      </v:roundrect>
      <![endif]-->
    </td>
  </tr>
</table>
```

### CTA Text Patterns

```
First-person works better than second-person:
  "Start my free trial" > "Start your free trial"  (+90% CTR in tests)
  "Get my report" > "Get the report"
  "Claim my spot" > "Register now"

Action-specific beats generic:
  "Deploy my first contract" > "Get started"
  "Watch the 2-min demo" > "Learn more"
  "Join 4,500 developers" > "Sign up"

Adding value/urgency selectively:
  "Start free trial (no credit card)" — removes objection
  "Upgrade now — save 20%" — clear incentive
  "Book my demo (15 min)" — sets expectation
```

### CTA Placement Rules

```
1. Primary CTA: Above the fold (within first 300px of content)
2. Secondary CTA: After the main value proposition (middle of email)
3. Final CTA: At the bottom (for skimmers who scroll past)

Rules:
  - ONE primary CTA per email (one action, one button)
  - Secondary CTA can be text link, not button
  - Never put 2 buttons of equal visual weight next to each other
  - Button width: 200-300px on desktop, full-width on mobile
  - Button height: 44px minimum (touch target)
  - Whitespace around CTA: 24px minimum on all sides
```

## Image Guidelines

```
Hero image:
  - Width: 600px (full-width of email)
  - Height: 200-400px
  - File size: <150KB (many clients block large images)
  - Format: PNG for graphics, JPEG for photos
  - Alt text: ALWAYS include descriptive alt text

Inline images:
  - Width: match column width (280px for half-width)
  - File size: <100KB each
  - Total email image weight: <500KB

Icons:
  - Use inline SVG or small PNGs
  - 32x32 or 48x48px for feature icons
  - Provide alt text or aria-hidden="true" for decorative icons

Rules:
  - Always set width and height attributes (prevents CLS in email clients)
  - Many corporate email clients block images by default
  - Emails must make sense WITHOUT images (use alt text as content)
  - Never use background images for critical content (Outlook ignores CSS backgrounds)
  - Host images on a CDN, never embed as base64 (increases email size, triggers spam)
```

## Plain Text Version

Every HTML email must have a plain text alternative. Not optional.

```
Why:
  - Some users prefer plain text
  - Some corporate filters flag HTML-only emails
  - Improves deliverability score
  - Accessibility for screen readers

Format:
  HEADLINE
  =========

  Body paragraph here. Keep lines under 80 characters
  for readability in plain text email clients.

  [Call to Action] → https://example.com/link

  ---
  You received this because you signed up at example.com.
  Unsubscribe: https://example.com/unsubscribe?token=XXX
```
