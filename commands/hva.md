---
name: hva
description: "Run the High-Velocity Advertising loop: fit-check, forge, deploy, read, decide (cut or compound), vault"
argument-hint: "campaign-name [$budget/day] (e.g. spring-tripwire $80/day)"
---

# HVA — High-Velocity Advertising Loop

You orchestrate the **HVA engine**: creative discovery at machine speed, without destroying signal quality. This is a *standalone engine* parallel to `/gtm`. One company can run both — **match the engine to the conversion, not to the excitement.**

Read `skills/high-velocity-advertising/SKILL.md` first. Run the phases below with an explicit human gate between each (mirrors the `/gtm` lifecycle). The Loop is: **Forge → Deploy → Read → Decide (cut or compound) → Refeed.**

## Phase 0 — Fit check (the router) 🚦
Before anything, score the account against the **Fit Boundary** (`skills/high-velocity-advertising/rules/guardrails.md` Part 2).
1. Read `.gtm/config.json`. If `hva.*` / `targets.target_cpa` are absent, self-provision the `targets` + `hva` config blocks (defaults from `SKILL.md`; ask the operator for `target_cpa` and `primary_event`) and persist them.
2. Score the hard gates: conversion speed, ticket size, **tracking quality (CAPI live, EMQ ≥ 8)**, budget, plus the soft dimensions.
3. **Decision:**
   - Any hard gate fails → **do not run HVA.** Name the failed gate and route to the opposite motion: "This account fits the slow-craft motion — run `/gtm` (and `/gtm-plan`, `/gtm-diagnose`)." Stop here.
   - All hard gates pass → announce "Fit: RUN HVA" with any soft warnings, and continue.

> Gate: "Account fits HVA. Proceed to Forge? (yes / route to /gtm / abort)"

## Phase 1 — Forge 🔨
Run `/hva-forge {campaign}` to generate a diverse, hypothesis-tagged concept batch (≤5 per ad set), reading Vault priors if present. Optionally pre-test with `/gtm-neurotest`. Output: `.gtm/hva/{campaign}/creatives/` + `manifest.json`.

> Gate: "Approve this creative batch? (approve / regenerate / select)"

## Phase 2 — Lint + Deploy (PAUSED) 🚀
1. Run `/hva-lint {campaign}` on the intended structure. Fix any **fail** before deploying (clean data, ≤5 creatives/ad set, funded ad set, Meta hygiene).
2. Deploy via the **campaign-operator** (`/gtm-deploy`) in the **HVA shape**: one concept per ad, ≤5 ads in **one consolidated, adequately funded ad set** (so `insights get --ad-id` reads each creative). Fund the ad set to reach decision volume in hours. Everything **PAUSED** until the operator confirms.

> Gate: "Structure is clean and deployed PAUSED. Activate? (activate / keep paused / edit)"

## Phase 3 — Read + Decide (The Desk) 📊
Run `/hva-review {campaign}` to read by impression volume and apply CLEAR via the deterministic scorer. The Desk acts per `hva.autonomy`:
- `recommend` (default): presents cut/scale calls; you approve each.
- `cut-auto`: auto-pauses losers; recommends scales.
- `full-auto`: auto-pauses and bounded auto-scales.

Set up the always-on reads if the operator wants them: the hourly cloud routine (`routines/hva-read-loop.md`) and/or the local watch loop (`scripts/hva-watch.sh`). Every action is logged to `.gtm/hva/{campaign}/audit.md`.

> Gate (recommend mode): approve each cut/scale before any write.

## Phase 4 — Compound (The Vault) 🏦
Run `/hva-vault promote <ad_id>` for every `confirmed-winner`. On `fatigue-refresh`, run `/hva-vault families <winner_id>` to breed variants. Recompute `/hva-vault priors` so the next Forge batch starts smarter. Update `.gtm/MEMORY.md` with new winning angles.

## The loop continues
Forge → Deploy → Read → Decide → Vault → (sharper priors) → Forge. Cut fast on a bad leading signal; scale slow, only after the true-conversion clock and replication confirm. The Vault is where the moat accrues — bank it while the window is open.

## Notes
- HVA is Meta-first (where CAPI, the learning phase, and per-ad insights exist). The skill notes the extension path to other channels.
- HVA does not replace the existing DCO deploy path — it adds a concept-per-ad shape alongside it.
- If at any point EMQ drops below 8 or CAPI breaks, **stop deciding** — a dirty feed makes you fast and wrong.
