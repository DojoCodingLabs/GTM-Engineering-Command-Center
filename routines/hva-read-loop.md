---
name: hva-read-loop
description: "Hourly HVA read loop — pulls per-creative insights, runs CLEAR via the scorer, and acts per the account's autonomy mode"
---

# HVA Read Loop Routine

## Overview

The always-on, scheduled read mechanism of the HVA Loop. Every hour it pulls per-creative Meta insights for active HVA campaigns, runs the deterministic CLEAR scorer (`scripts/hva-score.py`), and acts per the account's `hva.autonomy` mode — cut fast, scale slow. It is the cloud sibling of the on-demand `/hva-review` command and the `scripts/hva-watch.sh` local watch loop: **same Desk, same scorer, same autonomy gate**, different cadence.

This routine reads by **impression volume**, not calendar time — the hourly cadence is just how often it *checks* whether a creative has crossed a Read-Ladder rung.

## Schedule

- **Frequency**: Hourly (configurable; HVA wants frequent reads because decision volume accrues in hours)
- **Cron expression**: `0 * * * *`
- **Runtime**: ~1–3 minutes per active campaign

## What It Does

### Step 0: Fit-Boundary hard-block (the safety gate)
Before reading, re-check the Fit Boundary hard gates (`skills/high-velocity-advertising/rules/guardrails.md` Part 2) — most importantly **clean tracking / EMQ ≥ 8**. If a hard gate has regressed (e.g. CAPI broke), **skip the cycle and alert** — a dirty feed makes the whole loop fast-and-wrong. This is the one place the routine hard-blocks rather than warns.

### Step 1: Read (per creative, by volume)
For each active HVA campaign in `.gtm/hva/`, pull per-ad insights (`meta ads insights get --adset-id … --level ad`), normalize Meta's `actions` into `conversions` (the qualifying CAPI event) and `micro_conversions`, set the `clean` flag per row, and save the snapshot to `.gtm/hva/{campaign}/reads/`.

### Step 2: Decide (run the scorer)
Run `scripts/hva-score.py` with `.gtm/config.json`. The decision JSON gives per-creative `verdict`, `triggering_signal`, `clock`, `q_value`, and the resolved `autonomy_action`.

### Step 3: Act (per `autonomy_action`)
- `recommend` mode → write decisions, **alert** with recommendations, touch nothing.
- `cut-auto` → auto-pause losers (`meta ads ad update --status PAUSED`); recommend scales.
- `full-auto` → auto-pause losers + bounded auto-scale winners (≤ `max_daily_budget_increase_pct`/day, within `scale_bid_cap_multiple` bid cap).
Verify CLI exit codes (`0/3/4`); on `3` alert "refresh ACCESS_TOKEN", on `4` retry once with backoff. Append every action to `.gtm/hva/{campaign}/audit.md` and `decisions.json`.

### Step 4: Compound
For any `confirmed-winner`, promote to the Vault (`/hva-vault promote`). For any `fatigue-refresh` on a Vault winner, flag a family-breed. Recompute priors if the winners library changed.

### Step 5: Alert on significant findings
Alert if: a winner was confirmed (or auto-scaled), a creative was auto-paused, the Fit Boundary hard-blocked, EMQ regressed below 8, or CLI auth failed.

## Setup Instructions

### Prerequisites
1. `.gtm/config.json` with `targets.target_cpa` and `hva.*` set (run `/hva` Phase 0 once).
2. At least one active HVA campaign deployed in the concept-per-ad shape.
3. `meta` CLI, `python3`, and CAPI live with EMQ ≥ 8.

### Create the Routine
```bash
/schedule create "HVA Read Loop" \
  --cron "0 * * * *" \
  --command "For each active campaign in .gtm/hva/: re-check the Fit Boundary hard gates (skip+alert if EMQ<8 or CAPI broke); pull per-ad insights; run scripts/hva-score.py with .gtm/config.json; act per hva.autonomy (recommend=alert only, cut-auto=auto-pause, full-auto=auto-pause+bounded auto-scale); log to .gtm/hva/{campaign}/audit.md; promote confirmed-winners to the Vault; alert on confirmations, auto-pauses, or data-quality stops." \
  --description "Hourly HVA Desk read + decide + act, gated by hva.autonomy"
```

### Customize
Edit `.gtm/routines/config.json`:
```json
{
  "routines": [
    {
      "name": "hva-read-loop",
      "cron": "0 * * * *",
      "enabled": true,
      "options": {
        "campaigns": "all",
        "hard_block_on_emq_below": 8,
        "alert_on_auto_pause": true,
        "alert_on_confirmed_winner": true,
        "respect_autonomy_mode": true
      }
    }
  ]
}
```

## Troubleshooting
- **EMQ below 8 / CAPI broken**: the routine hard-blocks and alerts. Fix the feed (`skills/meta-ads/rules/pixel-setup.md`) before reads resume — deciding on a dirty feed is the failure mode HVA exists to kill.
- **`target_cpa` missing**: the scorer exits non-zero. Set `targets.target_cpa` in `.gtm/config.json`.
- **Exit code 3 every cycle**: `ACCESS_TOKEN` expired — run `meta auth status` and refresh.
- **Nothing happening in recommend mode**: that is correct — `recommend` never writes. Switch to `cut-auto` once you trust the cuts.
- **Too many auto-pauses**: tighten the feed quality or review `target_cpa`; check the audit log for the triggering signals.

## Related
- `/hva-review` — manual, on-demand read (same Desk)
- `scripts/hva-watch.sh` — local continuous watch loop (same Desk)
- `/hva-vault` — promote winners, breed families
- `agents/hva-desk.md` — the decision/action contract this routine executes
