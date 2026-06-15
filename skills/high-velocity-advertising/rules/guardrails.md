# Guardrails & the Fit Boundary

The failure modes HVA exists to kill, expressed as the `/hva-lint` checklist, plus the Fit Boundary scoring rubric that powers the Phase-0 router. A fast engine pointed at the wrong account, or run with a broken structure, is just a faster way to lose money.

---

## Part 1 — The Guardrails (the `/hva-lint` checklist)

`/hva-lint` takes a proposed (or live) campaign structure and flags every violation below. Each is a discrete, checkable condition. Lint is **read-only** — it never writes to the ad account.

| # | Guardrail | Check | Why it kills you |
|---|---|---|---|
| G1 | **No calendar-time thinking** | Any kill/scale rule expressed in hours/days instead of impressions or spend. | "It's only been 48 hours" pauses winners and funds losers. Read by volume. |
| G2 | **No first-window ROAS as a kill trigger** | A rule that cuts on first-window ROAS. | First-window ROAS is noise; iOS undercount makes it worse. Use leading indicators + the slow clock. |
| G3 | **No killing on dirty data** | Optimization event lacks CAPI / EMQ < 8 / pixel-only. | Platform undercounts ~20–30%; dirty-feed kills pause profitable ad sets. Layer 0 is a gate. |
| G4 | **No micro-cell budgets** | Any ad set funded below the per-concept decision-volume floor (e.g. `$5/day` cells). | Micro-cells take weeks to reach 50 events; they never resolve. Fund each concept to decision volume in hours. |
| G5 | **≤5 creatives per ad set** | More than `max_creatives_per_adset` (default 5) concepts in one ad set. | Past ~5, signal fragments and per-creative learning slows. The algorithm starves on redundancy. |
| G6 | **No near-duplicate flooding** | Many visually near-identical creatives (Andromeda entity clustering treats them as one). | Variety is the edge; duplication wastes the slot. See `the-foundry.md`. |
| G7 | **No learning-phase resets** | A workflow that edits budget/targeting/creative mid-flight repeatedly. | Constant edits reset the learning phase; the ad set never exits learning. |
| G8 | **No uncorrected winner crowning** | A multi-variant batch (k ≥ ~5) with no Benjamini-Hochberg / replication plan. | Crowning one winner of many is a coin flip (`1-(1-α)^k`). Correct before betting budget. |
| G9 | **No spend-velocity-as-truth** | A rule that reads early spend share as creative quality. | Divergent delivery — the algorithm funded a cheap audience, not the better creative. Confirm with the slow clock + lift tests. |
| G10 | **Concept-per-ad readability** | Creatives packed into one DCO `asset_feed_spec` when per-concept reads are required. | The Read Ladder reads per concept; bury concepts in one creative and `insights get --ad-id` can't resolve them. Deploy one concept per ad, ≤5 ads in one funded ad set. |
| G11 | **Required Meta hygiene** | Missing `--pixel-id`, `--custom-event-type`, `--instagram-actor-id`; not PAUSED on create. | Inherited from `agents/campaign-operator.md` Critical Rules — without these, Meta optimizes for impressions, not conversions. |

`/hva-lint` output: a table of `pass | warn | fail` per guardrail with the specific offending value, then the concrete fix. Any `fail` blocks a clean bill of health; the operator may proceed anyway (warn-don't-block, per the plugin's hook culture), but the failures are named.

---

## Part 2 — The Fit Boundary (the Phase-0 router)

HVA is a tool with a domain. Before the loop runs, score the account against the boundary. The check **warns and routes** — it never silently blocks in interactive use (the cloud routine MAY hard-block).

### Scoring rubric

Score each dimension. HVA fit = the account clears every gate. A single hard fail routes to the opposite motion.

| Dimension | HVA-fit (run HVA) | Anti-fit (run the opposite motion) | Weight |
|---|---|---|---|
| **Conversion speed** | Minutes to a few days from click to qualifying event | Weeks to months (long sales cycle) | hard gate |
| **Conversion value / ticket** | Low-to-mid ticket, high volume (DTC, app, info product, low-friction lead gen) | High-ticket B2B, enterprise, considered purchase | hard gate |
| **Tracking quality** | CAPI live, EMQ ≥ 8, qualifying event fires server-side | Weak/offline/delayed tracking, lead quality only knowable from CRM/sales | hard gate (this is Layer 0) |
| **Budget** | Large enough to hit decision volume (≈50 events/ad set/week, per concept) in hours–days | Low-budget; cells can't reach volume for weeks | hard gate |
| **Audience size** | Broad enough that ≤5 funded concepts get delivery | Tiny/niche audience, frequency spikes immediately | soft |
| **Creative variation** | Strong, inexhaustible angle/format variety available | One look, one claim, regulated/limited creative | soft |
| **Category** | Unregulated or lightly regulated | Heavily regulated (collides with constant creative churn) | soft |

### The router decision

- **All hard gates pass** → run HVA. Note any soft warnings (they shape the Foundry and budget, not the go/no-go).
- **Any hard gate fails** → **do not run HVA.** Recommend the **opposite motion**, the slow-craft `/gtm` lifecycle: a small number of high-craft concepts, reads measured in weeks, lead quality scored by *sales* (closed-won in the CRM) not by the platform's lead cost, and the feedback loop running through revenue data. Say which gate failed and why, then point the operator at `/gtm` (and `/gtm-plan`, `/gtm-diagnose`).

> One company can run both engines. A high-ticket B2B motion and a DTC tripwire can live in the same account on different campaigns. **Match the engine to the conversion, not to the excitement.**

### In the routine

`routines/hva-read-loop.md` re-runs the fit check before each read cycle and **hard-blocks** (skips the cycle, alerts) if a hard gate has regressed — e.g. CAPI broke and EMQ fell below 8, which would make the whole loop fast-and-wrong (G3 + Layer 0).
