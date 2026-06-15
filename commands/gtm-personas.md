---
name: gtm-personas
description: "Author, list, or derive the shared synthetic-persona substrate (.gtm/personas/)"
argument-hint: "list | author | derive [--from-srd]"
---

# GTM Personas Command

You manage the project's **shared synthetic-persona substrate** at `.gtm/personas/`. The governing principle is **build the persona once, consume everywhere**: a single set of persona objects feeds the SDV demand panel, media-buyer targeting (lookalike seeds, PostHog cohorts, interest stacks), and email lifecycle segmentation. Each persona is one JSON file conforming to `schemas/persona.schema.json` — the GTM-minimal projection (9 SDV-relevant fields + optional `skepticism`) of the richer product persona.

> **Fidelity awareness.** Personas are not cosmetic. The moment `.gtm/personas/` holds at least one valid persona, an SDV run is promoted from **F0 cold-start** (zero-shot, ranking-only, directional) to **F1 persona-grounded** (real personas reused as the panel, segment-weighted aggregation). See `skills/synthetic-demand/rules/fidelity-tiers.md`. The demand-forecaster (`agents/demand-forecaster.md`) is the **primary consumer**; authoring personas tangibly tightens every forecast.

Parse `$ARGUMENTS` for the mode: `list`, `author`, or `derive` (default `derive` when the substrate is empty, else `list`). `--from-srd` forces the SRD interop path in any mode.

## Mode: list

1. Glob `.gtm/personas/*.json`. If none exist, say so and recommend `/gtm-personas derive`.
2. Read each file and validate it against `schemas/persona.schema.json`. Flag any file missing a required field.
3. Present the substrate as a table:

```
Persona substrate: .gtm/personas/ ({N} personas)  →  SDV tier floor: F1 (persona-grounded)

| ID  | Age | Location          | Income      | user_pct | revenue_pct | price_sens | skepticism |
|-----|-----|-------------------|-------------|----------|-------------|------------|------------|
| P01 | 28  | Bogota, Colombia  | $800/month  | 45%      | 30%         | high       | high       |
| P02 | 41  | Austin, USA       | $9k/month   | 20%      | 50%         | low        | medium     |
| ...                                                                                          |
```

4. **Consistency check (report, do not silently fix):** sum `user_pct` across all personas and sum `revenue_pct`. Each sum should be **approximately 100%** (the schema documents this; it is a substrate-level invariant, not a per-file one). If either sum is off by more than ~5 points, flag it: `user_pct sums to 82% — substrate is incomplete or weights drift; rebalance before relying on volume-weighted SDV.`

## Mode: author

Interactively (or from `$ARGUMENTS`) collect the 9 SDV-relevant fields for one persona and write it to `.gtm/personas/<id>.json`.

1. Pick the next sequential `id` (`P01`, `P02`, ...) by scanning existing files.
2. Collect, in this order: `age`, `income`, `location`, `goals`, `pain_points`, `monthly_spend`, `user_pct`, `revenue_pct`, `price_sensitivity` (`low`/`medium`/`high`), and optionally `skepticism`.
   - When `skepticism` is omitted, leave it out — the SDV panel applies the default skeptic stance. Never default a respondent **below** the skeptic baseline.
   - When `price_sensitivity` is genuinely unknown, default it to `medium` and note the assumption.
3. Validate against `schemas/persona.schema.json` before writing. Write pretty-printed JSON to `.gtm/personas/<id>.json`.
4. Re-run the **consistency check** from `list` mode and warn if `user_pct` / `revenue_pct` sums now drift from ~100%.

## Mode: derive (the workhorse)

Derive a starter panel of 3-6 personas from whatever the project already exposes, then hand off to `author`-style validation. Derivation is **read-only** discovery followed by a single write per persona.

### Step 1 — Read the GTM sources (in order)

1. **`.gtm/config.json` → `config.product.target_audience`** (and `name`, `description`, `pricing`). This is the seed description of who the product is for. Split it into distinct buyer segments — usually the description already implies 2-4 (e.g. "career switchers in LATAM and US-based bootcamp grads" → at least two personas with different `location`, `income`, `price_sensitivity`).
2. **`.gtm/learnings/targeting-insights.md`** (if it exists). Promote *learned* truth over guesses: its **Top Audiences** and **Demographic Insights** sections sharpen `location`/`age`/`user_pct`; **Audience Exclusions** tell you which segments NOT to author; **Behavioral Insights** inform `price_sensitivity`. A persona grounded in realized targeting data is worth more than one invented from the config string.
3. **Detected customer language** — the same corpora SDV uses to climb to F2: reviews, testimonials, support threads, ad comments, and PostHog session feedback (probe via `skills/posthog-analytics/` and `skills/stack-detection/`, read-only). Pull verbatim phrasing into `goals` and `pain_points` so the persona speaks in the customer's own words. Note where language was found — it both grounds the persona and pre-positions a later SDV run for F2 data-anchored anchors.

### Step 2 — Synthesize the panel

- Author one persona per distinct segment. Give each a specific `age` (not a range) and a concrete `location`.
- Set `user_pct` and `revenue_pct` so that, **across the whole panel, each sums to approximately 100%**. Skew `revenue_pct` toward the segments that actually pay (a small high-`income`, low-`price_sensitivity` segment often carries outsized `revenue_pct` — that imbalance is exactly what revenue-weighted SDV ranking needs).
- Infer `price_sensitivity` from `income`, `monthly_spend`, region, and any pricing-objection language. Set `skepticism` only when the source signals it (e.g. "too good to be true" review language → `high`); otherwise omit and let the skeptic default apply.

### Step 3 — Validate and persist

For each persona: validate against `schemas/persona.schema.json`, then write to `.gtm/personas/<id>.json`. Finish with the `list` table and the consistency check.

## Interop: external `srd/personas.yml` (read-only projection)

If an external **`srd/personas.yml`** exists (the SRD framework is installed), or `--from-srd` is passed, **read it and project it DOWN** into the GTM shape. The two schemas are deliberately different: SRD's is the rich product persona (lifecycle, journeys, churn, scores); GTM's is the 9-field demand/targeting minimal. **Never write SRD's schema, and never write back into `srd/personas.yml`.**

Projection map (SRD field → GTM field):

| GTM (`persona.schema.json`) | SRD (`srd/personas.yml`)                  |
|-----------------------------|-------------------------------------------|
| `id`                        | `persona.id`                              |
| `age`                       | `persona.identity.age`                    |
| `income`                    | `persona.wallet_profile.income`           |
| `location`                  | `persona.identity.location`               |
| `goals`                     | `persona.identity.goals`                  |
| `pain_points`               | `persona.identity.pain_points`            |
| `monthly_spend`             | `persona.wallet_profile.monthly_spend`    |
| `user_pct`                  | `persona.wallet_profile.user_pct`         |
| `revenue_pct`               | `persona.wallet_profile.revenue_pct`      |
| `price_sensitivity`         | `persona.price_sensitivity` (optional in SRD; default `medium`) |
| `skepticism` (optional)     | `persona.skepticism` (optional in SRD)    |

**Trim everything else** — `lifecycle`, `primary_journeys`, `churn_risk_moments`, `scores`, `conversion_trigger`, `tech_stack`, `plan_progression`, etc. are product-internal and out of GTM's lane. Validate each projected object against `schemas/persona.schema.json` and write to `.gtm/personas/<id>.json`, preserving the SRD `id`.

> If `srd/personas.yml` is the source of truth, treat `.gtm/personas/` as a **derived cache**: re-project rather than hand-editing, so the GTM substrate never drifts from SRD. GTM never **requires** SRD installed — without it, the `derive` path above is fully sufficient.

## Output

```
Persona substrate updated: .gtm/personas/ ({N} personas)

Source: {config.product.target_audience | targeting-insights | customer language | srd/personas.yml projection}
SDV fidelity floor: F1 (persona-grounded) — was F0 cold-start
Consistency: user_pct sum ≈ {X}%  ·  revenue_pct sum ≈ {Y}%  [OK | drift flagged]

Consumers now grounded:
- demand-forecaster (SDV panel) — primary; F0 → F1, segment-weighted, objection revenue-at-risk by revenue_pct
- media-buyer — lookalike seeds / PostHog cohorts / interest stacks reference these persona objects
- email-marketer — lifecycle segments enriched with persona objections + price tolerance

Next:
- /gtm-validate <variants> — run an SDV forecast now grounded at F1 on this panel
- /gtm-plan — media-buyer reads these personas as targeting seeds
```

## Error Handling

- **No `.gtm/config.json`**: ask the user to run `/gtm-setup` first, or accept an inline audience description to derive from.
- **Empty `config.product.target_audience`**: fall back to `config.product.description`, customer language, and any `targeting-insights.md`; if all are empty, switch to `author` mode and collect fields interactively.
- **Validation failure**: report the exact field and constraint that failed (`user_pct must be 0-100`, `id must match ^P[0-9]{2,}$`); never write an invalid persona to the substrate.
- **`user_pct` / `revenue_pct` sums drift from ~100%**: warn but do not silently rescale — drift usually means a segment is missing; surface it so the user decides.
- **Malformed `srd/personas.yml`**: project the personas that parse, list the ones that did not, and never write back into the SRD file.
