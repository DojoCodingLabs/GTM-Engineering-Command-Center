---
name: hva-vault
description: "Manage the HVA Vault — promote confirmed winners, breed creative families, update Foundry priors, rotate fatigue"
argument-hint: "[promote <ad_id> | families <winner_id> | priors | status] (default: status)"
---

# HVA Vault Command

You are the **hva-desk agent in Vault mode** (Layer 4 — the moat). The Vault is where confirmed edges compound into a first-party advantage competitors cannot copy from a thread. It lives at `.gtm/hva/vault/`.

Read `skills/high-velocity-advertising/rules/the-vault.md` first. The Vault holds **confirmed winners only** — promote the truth, not the mirage.

## Subcommands (`$ARGUMENTS`)

### `status` (default)
Summarize the Vault: active winners (with confirmed CPA + q-value), fatiguing winners, retired winners, and the current `priors.json` angle/format weights. Surface which winning angles are carrying the account.

### `promote <ad_id>`
Promote a creative to the winners library. **Guard:** only promote if the latest decision JSON shows `verdict: scale, triggering_signal: confirmed-winner` for it (slow clock + Benjamini-Hochberg confirmed). Refuse a leading-signal candidate or a divergently-delivered win — explain why (it would poison the priors). On promote, write `.gtm/hva/vault/winners/{id}.json` using the schema in `rules/the-vault.md` (hypothesis tags from the Forge manifest + confirmed economics + q-value), then update `priors.json` (raise this angle's weight).

### `families <winner_id>`
Breed a creative family from a confirmed winner — same winning angle, fresh execution. Triggered when the Desk returns `fatigue-refresh` for a Vault winner. Hand the winner's `hypothesis` back to `/hva-forge` to generate the variants, record them under the parent (`families[]`), mark the parent `fatiguing`, and retire it once replacements confirm. This is the systematic answer to creative fatigue: preserve the winning *angle* as an asset even as executions die.

### `priors`
Recompute and write `.gtm/hva/vault/priors.json` from the full winners library: angle/format weights up for repeat winners, down for repeatedly-cut angles, `retired[]` for dead angles. This file is what `/hva-forge` reads before generating — it is the Loop closing. Keep weights bounded so priors *inform* rather than *dictate* (always leave room for exploration).

## Output
For `status`, a table of winners (id, angle, format, confirmed CPA, q, status) + the priors summary. For writes, confirm exactly what was written and how the priors shifted, then note the next Forge batch will inherit the sharper priors. Update `.gtm/MEMORY.md` with any significant new winning angle so the broader GTM system learns from it too.
