---
name: hva-review
description: "Read live creatives by impression volume, run CLEAR, and emit cut/scale/hold calls per creative"
argument-hint: "[campaign-name or adset-id] (defaults to latest .gtm/hva campaign)"
---

# HVA Review Command

You are the **hva-desk agent**. This is the on-demand read mechanism of the HVA Loop — the operator runs it whenever they want a read. (The same Desk also runs on a schedule via `routines/hva-read-loop.md` and continuously via `scripts/hva-watch.sh`; all three invoke the same scorer and the same autonomy gate.)

Follow the `hva-desk` agent workflow exactly. Read `skills/high-velocity-advertising/rules/the-desk.md` first.

## What this command does
1. **Phase 0 — Preconditions.** Read `.gtm/config.json` (`targets.target_cpa` required; `hva.autonomy`). Confirm the Fit Boundary hard gates pass (especially clean tracking / EMQ ≥ 8). Resolve scope from `$ARGUMENTS` (campaign name or ad-set id; default = latest `.gtm/hva/{campaign}/`).
2. **Phase 1 — Read.** Pull per-creative insights with `meta ads insights get --adset-id … --level ad`, normalize Meta's `actions` into `conversions` (qualifying CAPI event) and `micro_conversions`, set `clean` per row, save the snapshot under `.gtm/hva/{campaign}/reads/`.
3. **Phase 2 — Decide.** Run the scorer — never improvise the math:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hva-score.py \
     .gtm/hva/$CAMPAIGN/reads/snapshot-*.json --config .gtm/config.json \
     --out .gtm/hva/$CAMPAIGN/reads/decision-$(date +%Y%m%dT%H%M).json
   ```
4. **Phase 3 — Act per `autonomy_action`.** `recommend` mode → present recommendations, write nothing. `cut-auto` → auto-pause losers, recommend scales. `full-auto` → auto-pause and bounded auto-scale. Verify CLI exit codes. Log every action to `.gtm/hva/{campaign}/audit.md` + `decisions.json`.
5. **Phase 4 — Compound.** Hand confirmed winners to `/hva-vault`; flag fatigued winners for family breeding.

## Output
Present the autonomy mode, then a per-creative table:
```
HVA Review — {campaign} — {date} — autonomy: {mode}

| Creative | Rung | Verdict | Signal | Action | imp | spend | CPA | q |
|----------|------|---------|--------|--------|-----|-------|-----|---|
| pain-claymation | hard | CUT | economics-3x-cpa-zero-conv | recommend-pause | 9000 | $72 | — | — |
| founder-story | hard | SCALE | confirmed-winner | recommend-scale | 6500 | $520 | $10 | 0.03 |

Executed: {…}   Awaiting approval: {…}   Held: {…}
```
Name the triggering signal for every call. If a creative is `dirty-feed`, stop and surface the data-quality problem instead of deciding (Rule 4). If the Fit Boundary regressed, route to `/gtm`.

## Running it continuously
For the always-on local watch loop (volume-triggered reads every `hva.read_cadence_minutes`):
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/hva-watch.sh "$CAMPAIGN" "$ADSET_ID"
```
The watch loop calls this same Desk → scorer → autonomy gate on each tick. To schedule the hourly cloud version, see `routines/hva-read-loop.md`.
