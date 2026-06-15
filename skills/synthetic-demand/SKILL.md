---
name: synthetic-demand
description: Synthetic Demand Validation (SDV) — predict purchase intent, price tolerance, and objections for ad creatives, offers, and landing copy by eliciting free-text reactions from a synthetic persona panel and mapping them to Likert distributions. Comparative ranking is the headline signal. Use for "will this convert", "which variant wins", "is $X the right price", "pre-test this creative/offer/copy before spend".
---

# Synthetic Demand Validation (SDV)

SDV is the **demand-side** pre-flight for the GTM Command Center. Your existing neuro-testing (Tribe v2) predicts whether the brain will *notice, feel, and remember* a creative. SDV predicts the question neuro-testing cannot answer: **"would this persona actually buy it, at this price — and which variant wins?"**

It turns a project's audience into a **pollable synthetic consumer panel** and measures reaction to a concept (ad creative, offer, or landing copy), returning a forecast you can act on before a dollar is spent.

## The governing law (state it once, obey it everywhere)

> **Rank, don't score. Never ask a synthetic respondent for a number.**

Both halves are load-bearing and both are enforced in code (`scripts/sdv-score.py`), not just prose:

- **Never ask for a number.** Asking an LLM "rate your purchase intent 1–5" collapses to a safe "3/4" and recovers only ~26% of human reliability. Instead, elicit a **brief free-text reaction in character**, then map it to a Likert *distribution* in a **separate** step. The scorer rejects any reading whose pmf is near one-hot — the signature of a number that was elicited and softmaxed.
- **Rank, don't score.** The reliable result is a *ranking* (the paper's ρ≈90% is a ranking metric); absolute scores are anchor-dependent and only trustworthy once locally calibrated. So comparative duels are the headline, and the absolute `demand_score` can only ever make a verdict *more conservative*, never mint a DEPLOY.

## Provenance (and its limits)

Built on, and deliberately extending past, **Maier et al. 2025** (PyMC Labs × Colgate-Palmolive), *"LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings."* Their finding: direct number-asking recovers ~26% of human test–retest reliability; **free-text → Likert mapping recovers ~85% (FLR) to ~90% (SSR)**.

> **Out-of-distribution caveat.** Those figures were established on the paper's stimuli and constructs (personal-care surveys). GTM surfaces — ad creatives, offers, LATAM pricing — are out-of-distribution until locally confirmed at **F3** calibration. The ~90% requires the *full* protocol (two-step elicitation, ensembled anchors, comparative ranking); it does not transfer to shortcuts or new domains for free. Cite the figure as "reported on the paper's domain," never as a guarantee for GTM.

## The Core Loop

1. **Detect capabilities → declare a fidelity tier** (F0–F3). See `rules/fidelity-tiers.md`.
2. **Assemble the panel** — read `.gtm/personas/` if present; consume an external `srd/personas.yml` if found; else generate a lightweight panel (note it as generated).
3. **Assemble the stimulus** — one or more variants of the concept, per surface. See `rules/stimulus-design.md` (Phase 3+).
4. **Elicit** — each persona gives a free-text reaction, mapped to a pmf (FLR by default; SSR when embeddings are detected, via `scripts/ssr_embed.py`). See `rules/elicitation-methods.md`.
5. **Rank comparatively** — best-worst / pairwise duels are the PRIMARY signal. See `rules/comparative-scaling.md`.
6. **Score the battery** — the measured construct subset → composite `demand_score`. See `rules/construct-battery.md`.
7. **Sweep price** (offers only, Phase 3) — Van Westendorp + Gabor-Granger. See `rules/price-sensitivity.md`.
8. **Calibrate** — at F3, fit synthetic→actual against real Meta/Stripe/PostHog conversion. See `rules/calibration.md`.
9. **Mine objections** — structured reasons-not-to-buy → B0/B1/B2 blockers with revenue at risk. See `rules/objection-mining.md`.
10. **Decide + write artifacts** — run `scripts/sdv-score.py`, write the forecast to `.gtm/sdv/forecasts/`.

Steps 4–6, 9, and 10 ship in v1.8.0 (Phases 0–1). Step 7 (price) ships in Phase 3; step 8 outcome-calibration deepens through Phases 6–7.

## Surfaces (and what NOT to compare)

| Surface | What it tests | Construct subset (see `rules/construct-battery.md`) |
|---|---|---|
| `ad_creative` | a rendered creative + hook | purchase_intent, appeal, comprehension, differentiation, share_intent |
| `offer` | a full offer stack + visible price | the full battery incl. willingness_to_pay via a price test |
| `copy` | a headline / landing block | purchase_intent, comprehension, believability, appeal |

A `demand_score` of 70 on the 4-construct `copy` subset is **not** the same evidentiary thing as 70 on the 7-construct `offer` battery. The scorer raises if you try to rank across surfaces. `feature` exists in the construct table as a future seam but is not a wired surface.

## Fidelity tiers (the forecast's honesty header)

| Tier | Auto-detected trigger | What it may claim |
|---|---|---|
| **F0 Cold-start** | nothing detected | **Ranking only**; absolute is "directional" |
| **F1 Persona-grounded** | `.gtm/personas/` (or `srd/personas.yml`) | ranking + relative; absolute still soft |
| **F2 Data-anchored** | customer language / analytics text | ranking + better-grounded absolute |
| **F3 Outcome-calibrated** | real conversion data (Meta CVR / Stripe / PostHog) | **absolute go/no-go enabled** (with the evidence floor in `rules/calibration.md`) |
| **+SSR** | embeddings provider/key | swaps FLR mapping for true SSR at any tier |

`F` = **Fidelity** (renamed from the source's T0–T3 so it never collides with HVA's Read-Ladder rungs). Objection severity uses a separate **B**-axis (B0/B1/B2), so the two never clash. A forecast below F3 that presents a confident absolute verdict is **invalid** — lead with the ranking.

Confidence-interval width follows: `CI_width ∝ tier_factor (F0 widest → F3 tightest) × (1 − familiarity) ÷ √(effective_samples)`.

## The deterministic scorer

All decision math lives in `scripts/sdv-score.py` (stdlib-only, MIT, **no Tribe v2 dependency**), pinned by `scripts/tests/test_sdv_score.py`. The scorer never polls a model and never acts — it only decides. The `demand-forecaster` agent elicits reactions and acts on the decision. Verdicts use one vocabulary across SDV and the (Phase 2) unified gate: **DEPLOY / TEST / ITERATE / SKIP**.

## Quality standards (every forecast must pass)

1. Each construct distribution is a valid pmf (length 5, sums to ~1.0) — the scorer enforces it.
2. Each reading records its elicitation provenance (`elicitation_method`, `react_call_saw_scale: false`, `map_call_separate: true`); number-elicited (one-hot) pmfs are rejected.
3. Comparative ranking is reported with a `rank_stability` flag computed from **≥5 resamples**; an unstable top is a tie, never a winner.
4. `demand_score` is reconstructable from construct means × the recorded weights.
5. No absolute go/no-go below F3; the absolute field is labeled `demand_score_relative` until then.
6. Objections are structured (segment + severity + frequency), not prose; B0 items carry revenue at risk.
7. Anti-positivity defenses (skeptic stance, budget salience, do-nothing option, comparative mode) are recorded; missing ones derate confidence.
8. The forecast states its own caveats and its fidelity tier — never present a directional read as a verdict.

## Rules reference

- `rules/elicitation-methods.md` — FLR (default, prompt-only) · SSR (optional, embeddings) · the 3-step protocol · anti-positivity stack
- `rules/comparative-scaling.md` — best-worst & pairwise duels · aggregation · rank stability (the accuracy spine)
- `rules/anchor-sets.md` — 5-statement anchors · auto-generation · ensembling · data-derivation
- `rules/construct-battery.md` — the 8 constructs · per-surface weights · composite Demand Score
- `rules/fidelity-tiers.md` — capability detection · F0–F3 · familiarity · CI sizing
- `rules/calibration.md` — intent→behavior discount · the F3 evidence floor · synthetic→actual map
- `rules/objection-mining.md` — structured objections/drivers · B0/B1/B2 · revenue at risk
- `rules/srd-interop.md` — **optional** SRD bridge · read-only detection · inverted coupling (GTM never depends on SRD)

## Relationship to neuro-testing and HVA

SDV is the demand half of a two-stage pre-flight. The unified gate (`/gtm-validate`, Phase 2) composes the **outputs** of `neuro-score.py` (attention/memory — CC-BY-NC) and `sdv-score.py` (intent/price — MIT) without ever importing neuro code, so SDV runs fully standalone when Tribe v2 is absent. Where HVA's CLEAR governs spend *after* launch on real money, SDV governs *which concept earns the launch* on synthetic demand. See `skills/neuro-testing/` and `skills/high-velocity-advertising/`.
