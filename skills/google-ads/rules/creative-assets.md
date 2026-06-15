# Google Ads Creative & Assets — RSAs, YouTube, SaaS, Demand Gen

Atlas Part VIII + Part IX doctrine. As bidding and keyword control automate, creative becomes the primary differentiation lever — and on browse surfaces (Demand Gen, YouTube, Discover) creative IS the targeting mechanism, not a dressing on top of it.

> **Pipeline contrast — read this first.** Search RSAs are **TEXT-ONLY**: no images, no aspect-ratio rules, just headlines/descriptions/paths. PMax, Demand Gen, and YouTube asset groups **DO need image + video assets** (sizes in the asset table at the bottom). Do not build an image pipeline for Search; do not ship a text-only asset group to Demand Gen.

> **Hybrid execution.** Reading current ads/assets and pruning by performance is a READ/AUDIT job → `google-ads-open-cli` (read-only; see `skills/google-ads/rules/gads-cli.md`). Creating or updating ads, asset groups, and assets is a WRITE/DEPLOY job → Google Ads REST API `:mutate` endpoints via curl (no first-party CLI mutates). New ads/asset groups deploy **PAUSED by default**.

> **MICROS.** Any cost you read while pruning creative comes back as `cost_micros`. 1,000,000 micros = $1. Divide by 1e6 before reasoning about dollars — an asset showing `cost_micros: 4200000000` cost $4,200, not $4.2B.

## Responsive Search Ad Construction

The RSA assembly engine only earns its keep when the 15 headlines and 4 descriptions are **genuinely distinct angles**, not near-duplicates with a synonym swapped. Feed it duplicates and the combinations it tests are all the same ad. Feed it real angles and it finds the message-match per query.

### The angle matrix — 15 headlines, 4 descriptions

| Slot | Angle bucket | What goes here |
|------|--------------|----------------|
| Headlines 1–5 | Core offer / benefit | The literal offer, primary benefit, what they get |
| Headlines 6–10 | Pain-point hooks + emotional triggers | The problem, the frustration, the cost of inaction |
| Headlines 11–15 | Authority proof + risk reversals | Proof, numbers, guarantees, "cancel anytime", credentials |
| Descriptions 1–4 | Detailed benefit **paired with** urgency CTA | Each description = one concrete benefit + one time/scarcity CTA |

Write across all three headline buckets deliberately. An RSA that is 15 variations of the offer line has no pain angle and no proof angle to assemble against intent.

### Character limits (hard caps — the API rejects overflow)

| Asset | Limit |
|-------|-------|
| Headline | 30 chars |
| Description | 90 chars |
| Path (Path 1 / Path 2 display URL) | 15 chars each |

### Pin sparingly

Pinning forces an asset into a fixed position. **Pin only critical offers or compliance/legal statements to position 1.** Pinning everything turns the RSA back into an Expanded Text Ad and kills the combinatorial testing you bought into.

```
PIN POLICY:
  Compliance/legal disclaimer required in view   → pin to H1 (or D1)
  Must-show offer (e.g. "FDA-cleared", price)     → pin to H1
  Everything else                                 → leave unpinned, let it test
  Pinning 10+ assets                              → you have disabled RSA testing
```

### Ad Strength is a weak signal — do not chase "Excellent"

Ad Strength rewards *quantity and diversity of assets*, not *conversion quality*. **Do not sacrifice strong, proven copy to bump a "Good" to "Excellent."** A tightly-written ad at "Good" routinely beats a diluted ad at "Excellent." Prune the wrong way and you are optimizing a vanity meter.

Prune by **asset-level reporting**, not by the Strength label:

```
READ path (google-ads-open-cli) — pull per-asset performance, then cut losers:
  google-ads-open-cli query <customer-id> \
    "SELECT ad_group_ad_asset_view.field_type, asset.text_asset.text, \
            metrics.impressions, metrics.clicks, metrics.conversions, metrics.cost_micros \
     FROM ad_group_ad_asset_view \
     WHERE segments.date DURING LAST_30_DAYS \
     ORDER BY metrics.cost_micros DESC" --format compact
```

`field_type` distinguishes HEADLINE vs DESCRIPTION; `performance_label` (LOW / GOOD / BEST / PENDING) is Google's own per-asset verdict — cut LOW assets that have served enough impressions, swap in a fresh angle. The swap is a **WRITE** (`:mutate` on the ad's asset list via curl) — the CLI cannot edit ads.

**WHITEHAT | 10/10** — Multi-angle RSA testing is standard practice inside Google's native creative framework; pruning by your own asset-level data is pure measurement-driven hygiene.

## YouTube Creative for Info Products

Aleric Heck of AdOutreach (states he has spent $7.7M+ on his own YouTube ads) reports the structure that actually wins:

```
HYBRID AI STRUCTURE (6 of his top 10 ads use it):
  0–8s    AI-generated hook  → captures attention
  8s+     CUT to a real person → builds trust
```

The data point operators miss: **fully-AI ads were his WORST performers.** AI captures attention but does not build trust — and trust is what converts an info-product viewer. AI for the hook, a real human for the pitch.

### Structure and length

```
SWEET SPOT: 2–3 minutes
ARC:        hook → value → CTA

The opening hook is NOT copywriting — it is an audience-SELECTION FILTER.
  Who stays past the hook teaches Google what a "good viewer" looks like.
  A hook that filters hard (names the niche, the pain, the buyer) trains the
  algorithm on the right audience even before any conversion fires.
```

### Settings that matter

- **Turn OFF connected-TV (CTV) screens for conversion campaigns.** TV-screen viewers don't click/convert the way mobile/desktop do; leaving CTV on inflates view volume and starves conversion signal. This is a campaign **WRITE** setting (`:mutate` via curl), not a creative choice.

### Micro-VSL (the paid-social crossover format)

A **micro-VSL** is a 30–90s compressed video sales letter. Reportedly drives **3–5x ROAS on paid social**, often mass-produced with AI avatars and voice clones to spin many variations cheaply.

```
MICRO-VSL CADENCE:
  Mass-produce variations (AI avatar + voice clone for volume)
  Run them
  Kill the bottom 70% after 48–72h
  Scale the survivors
```

**GRAYHAT | 5/10** — AI avatars / voice clones to mass-produce micro-VSL variations are allowed and effective, but drift fast toward misrepresentation if the avatar implies a real endorser or the voice clones a real person without consent; watch policy drift.

## Creative for SaaS

SaaS video runs a **problem → agitate → demo → validate** arc, and it must show the **actual interface in motion** — not a logo wall, not stock B-roll.

| Time | Beat | Content |
|------|------|---------|
| 0–5s | Friction hook | Name the pain: *"Why is pipeline forecasting so slow?"* |
| ~5–20s | Fast visual demo | Real product, real screens, moving — the feature solving the pain |
| ~20s+ | ROI validation + CTA | Proof/numbers, then free-trial or demo CTA |

Show the product working. The demo IS the proof; a SaaS ad that never shows the interface is asking for trust it hasn't earned.

**WHITEHAT | 10/10** — Demo-first SaaS explainers demonstrate real product utility and aid the buyer's decision; the most defensible creative you can run.

**GRAYHAT | 8/10** — Simulated interface animations (rendered/animated UI instead of screen capture) are common and acceptable, but must reflect **real capabilities** and not overpromise features that don't ship; the moment the animation shows something the product can't do, it crosses into deceptive content.

**BLACKHAT | 1/10** — Documented so you recognize it — never deploy: deepfake testimonial voiceovers and AI-faked endorsements fabricate a person vouching for the product. Violates deceptive-content policy and invites account bans plus legal exposure.

## Demand Gen Creative = Paid Social, Not Search

Atlas Part IX doctrine. Demand Gen spans YouTube, Shorts, Discover, Gmail, and Maps — Google's social-like **browse** engine. The single biggest failure mode is bringing search-first habits into a visual-first environment.

> **On browse surfaces, creative IS the targeting mechanism.** You are not matching a query — there is no query. The creative selects the audience: who stops scrolling, who watches, who clicks is what teaches the system who to show it to next. A weak visual targets nobody.

### Match the offer to the surface temperature

Browse traffic is **cold**. The offer must be low-friction or the surface punishes you.

```
RIGHT for browse (low-friction, creative-led):
  Quizzes          → "Which forecasting method is leaking your pipeline?"
  Cheatsheets      → one-pager lead magnet
  Short VSLs       → 30–90s micro-VSL
  Webinar clips    → a 45s excerpt, not the full registration ask

WRONG for browse (high-friction, forced):
  Hard demo / sales application as the first ask
  → produces weak lead quality OR policy trouble (info-product lead forms
     get flagged when cold traffic is funneled into aggressive asks)
```

Forcing cold browse traffic straight into a hard demo or application is the classic mistake — it yields low-quality leads and invites policy scrutiny. Lower the first ask; let the funnel warm them.

**WHITEHAT | 10/10** — Treating Demand Gen like paid social with creative-led audience selection and lower-friction offers is the correct model; matching offer friction to surface temperature is exactly how the channel is meant to run.

## Asset Requirements — Search vs. Asset-Group Surfaces

The line that drives the creative pipeline:

| Surface | Format | Images needed? | Video needed? |
|---------|--------|----------------|---------------|
| Search (RSA) | **TEXT-ONLY** | No — no image or aspect-ratio rules at all | No |
| Performance Max | Asset group | **Yes** | Yes (or Google auto-generates) |
| Demand Gen | Asset group | **Yes** | Yes (recommended) |
| YouTube | Video campaign | Thumbnail | **Yes — video is the ad** |

### Image asset sizes for asset-group surfaces (PMax / Demand Gen)

| Ratio | Pixels | Use |
|-------|--------|-----|
| Landscape 1.91:1 | 1200×628 | Primary landscape placement |
| Square 1:1 | 1200×1200 | Square placements |
| Portrait 4:5 | 960×1200 | Vertical / mobile-first placements |

Plus video for YouTube/Demand Gen (and PMax, which will auto-generate video from your assets if you don't supply one — supply one; auto-generated video underperforms).

### Auditing what's live (READ path)

```bash
# Inventory current assets on the account (read-only)
google-ads-open-cli assets <customer-id> --type IMAGE
google-ads-open-cli assets <customer-id> --type YOUTUBE_VIDEO
google-ads-open-cli ads <customer-id> --ad-group <ad-group-id>   # see live RSA copy
```

Uploading new images/video and attaching them to ads or asset groups is a **WRITE** — Google Ads REST API `:mutate` (asset creation + asset-group/ad-group-ad linking) via curl, deploying **PAUSED by default**. The read CLI inventories and reports; it never creates assets. Full GAQL recipes and the upload/mutate shapes live in `skills/google-ads/rules/gads-cli.md`.
