# The Foundry — creative supply that outruns fatigue

Layer 1 of the Stack. The Foundry's job is an **inexhaustible supply of genuinely distinct concepts** — not variations of one idea. This is the fatigue-defeating edge: when winners decay (and they all do), the operator with a deeper, more diverse pipeline replaces them faster than the crowd.

`/hva-forge` is the entry point. It does **not** reinvent creative generation — it reuses the plugin's existing Foundry and adds HVA's diversity discipline and hypothesis tagging on top.

## Reuse, don't rebuild

| Need | Existing plugin asset |
|---|---|
| Image generation, copy frameworks (PAS / AIDA / Before-After-Bridge), 5×5×5 | `agents/creative-director.md` |
| Andromeda entity diversity ("20+ visually distinct creatives; never 5 variants of one image") | `agents/creative-director.md` + `skills/meta-ads/rules/andromeda-2026.md` |
| Pre-deployment neural pre-test (kill weak concepts before spend) | `/gtm-neurotest` + `skills/neuro-testing/` |
| Tactic library, case studies, ethical ratings | `knowledge/gtm-creativity-atlas-2026.md` |
| Brand tokens (color, font, logo) | `creative-director` reads `tailwind.config.*` + `.gtm/config.json` |

The Foundry's contribution over plain `/gtm-create` is **variety as a measured constraint** and **hypothesis tagging** so the Desk's reads become learnings, not just verdicts.

## The diversity taxonomy

A batch is diverse only if its concepts vary along *meaning*, not just pixels. Each concept is tagged with a hypothesis on these axes (stored in the batch `manifest.json`):

- **Hook** — the first 3 seconds / first line (problem-aware, benefit-led, social proof, direct offer, curiosity, comparison).
- **Pain** — the specific problem named.
- **Offer** — the promise / mechanism / deal.
- **Proof** — testimonial, data, demo, authority, UGC.
- **Format** — static, UGC video, carousel, meme, claymation, VSL, screen-record demo.
- **Creator style** — persona, age, environment, voice.
- **Objection** — the specific doubt the concept answers.
- **Demo angle** — what the product is shown doing.

**Rule: variety over near-duplication.** Two concepts that differ only in headline are *one* concept to Andromeda's entity clustering — they waste a slot and fragment signal. Aim for concepts that could each win for a *different reason*, so a win teaches you something transferable.

## Output contract

`/hva-forge` writes to `.gtm/hva/{campaign}/creatives/`:
- the rendered assets (1:1 `1080×1080` and 9:16 `1080×1920`, per `campaign-operator` requirements),
- `manifest.json` — one entry per concept: `{ ad_id_slug, hypothesis: {hook, pain, offer, proof, format, creator_style, objection, demo_angle}, files, neuro_score?, entity_diversity_note }`.

The manifest's hypothesis tags are what let the Desk attribute a win to an *angle* and the Vault breed families from it (see `the-vault.md`). A win with no tagged hypothesis is a number; a win with one is a lesson.

## Sharper priors (the refeed)

Before generating, `/hva-forge` reads `.gtm/hva/vault/priors.json` (written by `/hva-vault`). Confirmed-winner angles raise their generation weight; repeatedly-cut angles lower theirs. This is the Loop closing: every cycle's learnings re-enter the Foundry as sharper priors, so the supply gets *smarter*, not only faster. Priors inform, they do not dictate — always include exploratory concepts outside the current winning cluster, or the Foundry collapses onto a local maximum and fatigues as one.
