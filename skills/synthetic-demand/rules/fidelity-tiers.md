# Capability Detection & Fidelity Tiers

## Core Principle

**Never claim more certainty than the evidence supports.** SDV probes each project read-only, declares a
**fidelity tier** (F0–F3), and sizes both its confidence intervals *and* the claims it is allowed to make to
match. With nothing detected it runs the paper's zero-shot method and says so plainly — the forecast is
labeled **directional**. As real GTM signal appears (personas, customer language, analytics, conversion
data), the tier climbs, the bands tighten, and only at **F3** does SDV earn the right to make an absolute
go/no-go call.

This is the answer to "capability-agnostic": the plugin adapts to whatever the project exposes, and the tier
is the forecast's **honesty header**.

> **The F-axis is fidelity, not the Read-Ladder.** Tiers are **F0/F1/F2/F3** (renamed from the SRD source's
> T0–T3) so they never collide with HVA's Read-Ladder rungs. **+SSR** is **orthogonal** — it swaps FLR for
> true SSR elicitation at *any* tier and never changes which tier you are in. Objection severity rides a
> separate **B**-axis (B0/B1/B2, `rules/objection-mining.md`), so none of the three clash.

This file owns **capability detection (Step 1)**, **the tier ladder (Step 2)**, and **familiarity + CI sizing
(Step 5)**. The F3 outcome-map fitting (intent→behavior discount, the synthetic→actual map, the F3 evidence
floor) lives in `rules/calibration.md` — this file points at it but does **not** duplicate it.

## Step 1 — Capability Detection (read-only)

Detection is **READ-ONLY**: never write to, transact against, or call out to an external service while probing.
SDV does not ship its own auditor — it **reuses the GTM Command Center's own skills** to look at what the
project already exposes:

| Probe skill | What it reads | Feeds |
|-------------|---------------|-------|
| `skills/stack-detection/` | installed SDKs, env keys, integrations present in the repo (PostHog/GA, Stripe, Meta, embeddings provider) | tier triggers + +SSR |
| `skills/stripe-revenue/` | whether real order/subscription/conversion data is reachable | F3 trigger |
| `skills/posthog-analytics/` | analytics SDK + events, funnels, session feedback / survey text | F2 + F3 triggers |
| `skills/meta-ads/` (the `meta ads` CLI) | live ad CVR / ROAS from delivered campaigns | F3 trigger |

### Detection map

| Signal | How it is detected (via the probe skills) | Unlocks |
|--------|--------------------------------------------|---------|
| **Personas** | `.gtm/personas/` present, **or** an external `srd/personas.yml` is found | **F1** |
| **Customer language** | reviews / testimonials / support threads / ad comments / PostHog session feedback text | **F2** |
| **Analytics** | PostHog or GA SDK + events wired in code (via `stack-detection` / `posthog-analytics`) | **F2** |
| **Real conversion data** | Meta ad CVR/ROAS (`meta ads` CLI), Stripe orders/subscriptions, or PostHog funnels | **F3** |
| **Embeddings key** | an embeddings provider key present in env/config (via `stack-detection`) | **+SSR** (orthogonal) |

Record what was found in `calibration_metadata.detected_capabilities`. The selected tier is the **highest**
whose trigger is satisfied — with **+SSR riding on top of whatever tier you land in**, never instead of it.

These capability flags map **exactly** onto the scorer's `detect_tier()` keys
(`scripts/sdv-score.py`): `conversion_data` → F3 · `customer_language` **or** `analytics` → F2 ·
`personas` → F1 · else F0. Pass the same flags you detected here as `forecast.capabilities` and the scorer
will derive the identical tier. (You may also set `forecast.tier` explicitly; it takes precedence.)

## Step 2 — The Fidelity Tier Ladder

| Tier | Auto-detected trigger | Behavior | CI width | Allowed claim |
|------|----------------------|----------|----------|---------------|
| **F0 Cold-start** | nothing detected | Zero-shot FLR; ensembled generic→domain anchors | **Widest** (`tier_factor 1.0`) | **Ranking only**; any absolute is **"directional"** |
| **F1 Persona-grounded** | `.gtm/personas/` or `srd/personas.yml` | Reuse real personas as the panel; segment-weighted aggregation | Wide (`0.8`) | Ranking + relative; absolute still **soft** |
| **F2 Data-anchored** | customer language **or** analytics | Anchors & objections from real buyer language; behavioral proxies | Medium (`0.6`) | Ranking + **better-grounded** absolute |
| **F3 Outcome-calibrated** | real conversion data (Meta CVR / Stripe / PostHog) | Fit synthetic→actual map; learned intent→behavior discount (`rules/calibration.md`) | **Tight** (`0.4`) | **Absolute go/no-go enabled** (with the F3 evidence floor) |
| **+SSR** | embeddings provider/key in env | Swaps FLR mapping for true SSR — at *any* tier above | (sharper readings) | does **not** change the tier or its allowed claim |

**A forecast below F3 that presents a confident absolute verdict is INVALID.** It must **lead with the
ranking** and caveat any absolute as directional. This is not a guideline you can forget — the scorer enforces
it twice:

- `get_verdict()` applies a **tier ceiling**: unless `tier == "F3"` *and* the F3 calibration map is valid, the
  verdict is capped at **TEST** — a non-F3 forecast literally **cannot mint DEPLOY**, no matter how high the
  comparative or absolute score.
- `score_forecast()` sets `fidelity.directional = (tier != "F3")` and labels the absolute field
  `demand_score_relative` ("uncalibrated — directional only") rather than `demand_score_calibrated` until an
  F3 map is fitted.

So the tier ladder is the contract, and the deterministic scorer is the bailiff. The honesty is structural,
not stylistic.

## Step 5 — Familiarity & Confidence Intervals

Estimate a **`familiarity_score` (0–1)**: how much reliable prior the model plausibly has for *this* buyer and
*this* category. This is the paper's own boundary — "usefulness is bounded by the knowledge domains in training
data." It runs **high** for mainstream consumer / dev-tooling buyers, and **low** for a novel niche, a
regional buyer, or anything past the model's cutoff.

Confidence-interval width is sized from three inputs (wider on **any** of them):

```
CI_width  ∝  tier_factor (F0 widest → F3 tightest)
          ×  (1 − familiarity_score)        # unfamiliar domain ⇒ wider
          ÷  √(effective_samples)           # more samples ⇒ tighter
```

`tier_factor` values match the scorer's `DEFAULTS` exactly: **F0 = 1.0, F1 = 0.8, F2 = 0.6, F3 = 0.4**
(`ci_width()` in `scripts/sdv-score.py`, default `effective_samples = 9`). When `familiarity_score` is **low**,
do three things together: **widen the bands**, **label the forecast "directional,"** and **recommend a real
human test before any large bet.** Honesty here is a feature — it tells the user precisely when *not* to trust
the synthetic panel.

### Out-of-distribution caveat

The paper's ~85% (FLR) / ~90% (SSR) reliability was established on personal-care surveys. **GTM surfaces — ad
creatives, offers, LATAM / regional pricing — are out-of-distribution versus Maier et al.'s domain until
confirmed locally at F3.** A high `familiarity_score` narrows the bands but does **not** make the surface
in-distribution; only F3 outcome calibration (`rules/calibration.md`) does. Until then, cite the paper's figure
as "reported on the paper's domain," never as a guarantee for GTM, and keep the directional label on.

## What Each Tier May Conclude (GTM-themed)

- **F0 / F1 (creative duel):** "Creative V2 is preferred over V1, stable across resamples. Absolute purchase
  intent is **directional only** — rank, don't trust the level."
- **F2 (offer):** "Offer V2 wins; objections cluster on price and proof, drawn from real review language;
  absolute demand is **better-grounded** but still pre-calibration."
- **F3 (price):** "Offer V2 wins; **calibrated** est. conversion 4.1% at $499 (90% CI 3.4–4.8%); revenue-max
  price $499. **Ship V2.**" — the only tier permitted to say "ship."

## Common Mistakes

1. **Presenting a confident absolute verdict below F3.** Lead with the ranking; caveat absolutes as
   directional. The scorer caps you at TEST anyway — don't let the prose over-claim what the math won't.
2. **Treating +SSR as a tier.** +SSR is orthogonal: it sharpens elicitation but never promotes you to a higher
   fidelity tier or unlocks an absolute call.
3. **Ignoring `familiarity_score`.** A confident forecast in an unfamiliar, regional, or post-cutoff domain is
   a trap — widen, label directional, recommend a human test.
4. **Forgetting the out-of-distribution caveat for GTM surfaces.** Ad/offer/pricing surfaces are OOD vs the
   paper until F3-confirmed locally; a tight band from high familiarity is not the same as a calibrated band.
5. **Calling an external service during detection.** Detection is read-only — probe via the GTM skills; never
   write or transact while sniffing capabilities.
6. **Hand-mapping a tier that disagrees with the scorer.** Your detected capability flags must round-trip
   through `detect_tier()`; if they don't, the artifact and the bailiff disagree and the forecast is unsound.
