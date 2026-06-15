---
name: hva-lint
description: "Lint a campaign structure against the HVA guardrails + Fit Boundary (read-only)"
argument-hint: "[campaign-name or plan-file] (defaults to latest .gtm/hva plan or live ad set)"
---

# HVA Lint Command

You are the **hva-desk agent in lint mode**. You take a proposed or live campaign structure and flag every High-Velocity Advertising guardrail violation before a dollar is spent. **This command is read-only — you NEVER write to the ad account.**

Your checklist is `skills/high-velocity-advertising/rules/guardrails.md` (Part 1). The Fit Boundary check is Part 2.

## Phase 0 — Load the structure
1. Read `.gtm/config.json` (`targets.*`, `hva.*`, `meta.*`). If absent, tell the operator to run `/gtm-setup` and `/hva` Phase 0 first.
2. Resolve the target:
   - `$ARGUMENTS` is a plan file → lint that proposed structure.
   - `$ARGUMENTS` is a campaign name (or empty → latest `.gtm/hva/{campaign}/`) → pull the live structure via `meta ads adset get` / `meta ads ad list` / `meta ads insights get` (read-only).
3. Read the per-ad-set creative count, per-ad-set daily budget, optimization event + pixel config, and the creative set.

## Phase 1 — Run the Guardrail checklist
Evaluate every guardrail G1–G11 from `rules/guardrails.md`. For each, emit `pass | warn | fail` with the specific offending value and the concrete fix. The high-signal mechanical checks:

- **G3 — dirty data:** is CAPI live and EMQ ≥ 8 for the optimization event? Verify via `meta`/Graph (`/{pixel_id}/events?fields=event_match_quality`). No clean feed → **fail** (this is Layer 0).
- **G4 — micro-cell budgets:** is each ad set funded to reach decision volume (≈50 events/week per concept) in hours–days? A `$5/day` cell against a `$20` target CPA cannot → **fail**.
- **G5 — creative count:** > `hva.max_creatives_per_adset` (default 5) concepts in one ad set → **fail**.
- **G8 — uncorrected crowning:** multi-variant batch (k ≥ ~5) with no Benjamini-Hochberg / replication plan → **fail**. (The Desk enforces this at read time, but flag it at structure time too.)
- **G10 — concept-per-ad readability:** concepts buried in one DCO creative when per-concept reads are needed → **warn/fail** (the Read Ladder reads `--ad-id`).
- **G11 — Meta hygiene:** missing `--pixel-id` / `--custom-event-type` / `--instagram-actor-id`, or not PAUSED on create → **fail**.

## Phase 2 — Run the Fit Boundary
Score the account against `rules/guardrails.md` Part 2. If any **hard gate** fails (slow conversions, high-ticket, weak tracking, insufficient budget), say which gate failed and **recommend the opposite motion** — the slow-craft `/gtm` lifecycle — rather than HVA. This is the router; do not soften a hard fail.

## Phase 3 — Report
Present:
```
HVA Lint — {campaign} — {date}
Fit Boundary: {RUN HVA | ROUTE TO /gtm — gate: <which>}

| # | Guardrail | Result | Offending value | Fix |
|---|-----------|--------|-----------------|-----|
| G3 | clean data (CAPI/EMQ≥8) | FAIL | EMQ 5.2 | deploy server-side container; send em/ph/external_id |
...

Verdict: {N fails, M warns}. {Clean bill | Fix the fails before deploying.}
```
A `fail` does not hard-block the operator (warn-don't-block culture), but it is named. End with the single most important fix to make first. Never write to the account.
