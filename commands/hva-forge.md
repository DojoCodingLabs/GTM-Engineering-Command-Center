---
name: hva-forge
description: "Forge a diverse batch of creative hypotheses for the HVA Foundry — variety over duplication, hypothesis-tagged"
argument-hint: "campaign-name [count] (e.g. spring-tripwire 8)"
---

# HVA Forge Command

You are the **creative-director agent in HVA Foundry mode** (Layer 1). You generate an inexhaustible supply of *genuinely distinct* concepts — the fatigue-defeating edge. You do not reinvent creative generation; you reuse `agents/creative-director.md` and add HVA's diversity discipline + hypothesis tagging.

Read `skills/high-velocity-advertising/rules/the-foundry.md` first.

## Phase 0 — Context + priors
1. Read `.gtm/config.json` (brand tokens, product, `targets.primary_event`) and the project's `tailwind.config.*` for brand tokens (as `creative-director` does).
2. Read `.gtm/hva/vault/priors.json` if it exists — confirmed-winner angles get higher generation weight, dead angles lower (the Loop's refeed). **Always include exploratory concepts outside the winning cluster** so the Foundry doesn't collapse onto a local maximum.
3. Determine `count` from `$ARGUMENTS` (default 5 — the per-ad-set cap; never exceed `hva.max_creatives_per_adset` for a single ad set's batch).

## Phase 1 — Diversify across the taxonomy
Generate concepts that vary in *meaning*, not just pixels. Spread the batch across the taxonomy axes (`rules/the-foundry.md`): **hook, pain, offer, proof, format, creator style, objection, demo angle**. Two concepts that differ only in headline are ONE concept to Andromeda — reject near-duplicates (Guardrail G6). Each concept should be able to win for a *different reason*.

Use `creative-director`'s pipeline for the actual assets: image generation, the copy frameworks (PAS / AIDA / Before-After-Bridge), and Andromeda entity diversity ("visually distinct: persona, format, style"). Produce both **1:1 (1080×1080)** and **9:16 (1080×1920)** per concept.

## Phase 2 — Tag every concept
Write `.gtm/hva/{campaign}/creatives/manifest.json` — one entry per concept:
```json
{ "concepts": [
  { "slug": "founder-story-vsl", "files": ["feed-1080x1080.png","story-1080x1920.png"],
    "hypothesis": { "hook":"social-proof", "pain":"manual-busywork", "offer":"7-day-trial",
                    "proof":"founder-demo", "format":"VSL", "creator_style":"founder-direct",
                    "objection":"is-it-real", "demo_angle":"one-click-setup" },
    "entity_diversity_note": "distinct persona + format vs. batchmates" }
] }
```
The tags are what let the Desk attribute a win to an *angle* and the Vault breed families. A win with no tagged hypothesis is a number; with one it is a lesson.

## Phase 3 — Pre-test (optional but recommended)
Offer to run `/gtm-neurotest` on the batch to kill weak concepts before they cost a dollar. Record each concept's `neuro_score` back into the manifest. Below-threshold concepts are flagged for iteration, not deployed.

## Phase 4 — Handoff
Report the batch as a table (slug, hook, format, proof, neuro score) and confirm diversity coverage across the taxonomy. The batch is now ready for deployment as **one concept per ad, ≤5 ads in one funded ad set** (the HVA Structure shape — see `rules/guardrails.md` G10). Point the operator at `/gtm-deploy` (campaign-operator) for the PAUSED deploy, then `/hva-review` to start reading.
