# The Vault — the compounding moat

Layer 4 of the Stack, and the only layer competitors cannot copy from a thread. The CLEAR signals commoditize — the moment everyone reads them, the edge competes away, exactly as latency arbitrage did once every desk had a fiber line. So the defensibility is pushed, by design, into **the system you assemble and the first-party data you accumulate.** Build the loop while the window is open. Bank the moat where it cannot be tweeted.

`/hva-vault` manages it. The Vault lives at `.gtm/hva/vault/`.

## What the Vault is

Four assets that compound:

1. **Winners library** (`winners/`) — every confirmed winner (slow-clock + Benjamini-Hochberg confirmed; see `the-desk.md`), indexed by its tagged hypothesis (angle, hook, format, proof) plus its CLEAR-confirmed economics and B-H q-value. Not "this image did well" but "this *angle* won, at this CPA, confirmed at q=0.03."
2. **Creative families** (`families/`) — variants bred from a confirmed winner when it fatigues. Same winning angle, new execution. Fatigue (`fatigue-refresh` from the Desk) is the trigger; the family is the response. This is how a winner's life extends past its first decay.
3. **Cross-campaign priors** (`priors.json`) — the distilled weights the Foundry reads before generating (see `the-foundry.md`). Winning angles up, dead angles down, carried across campaigns so Campaign B starts smarter than Campaign A did.
4. **Proprietary judgment + first-party data** — the accumulated record of what won, where, and why, plus the CAPI/CRM conversion data underneath it. This is the part that is genuinely yours.

## Schema

`winners/{id}.json`:
```json
{
  "id": "2026-06-founder-story-v2",
  "campaign": "spring-tripwire",
  "hypothesis": { "hook": "social-proof", "pain": "manual-busywork", "offer": "7-day-trial",
                  "proof": "founder-demo", "format": "VSL", "creator_style": "founder-direct" },
  "confirmed": { "cpa": 10.4, "target_cpa": 20, "q_value": 0.03, "impressions": 6500, "conversions": 52 },
  "promoted_at": "2026-06-14",
  "source_files": [".gtm/hva/spring-tripwire/creatives/founder-story/..."],
  "status": "active",            // active | fatiguing | retired
  "families": ["2026-06-founder-story-v2-fam1"]
}
```

`priors.json`:
```json
{
  "angle_weights": { "social-proof": 1.4, "comparison": 1.1, "direct-offer": 0.7 },
  "format_weights": { "VSL": 1.3, "static": 0.9 },
  "retired": ["curiosity-claymation"],
  "updated_at": "2026-06-14"
}
```

## Promotion rule (what earns a place)

A creative is promoted to the Vault **only** when the Desk returns `verdict: scale, triggering_signal: confirmed-winner` — i.e. it cleared the slow clock (true-conversion economics at or below target CPA) **and** survived Benjamini-Hochberg at the configured FDR. A creative that merely looked good, or won on a leading signal, does not enter. The Vault must hold *confirmed* edges only, or the priors poison the Foundry. Promote the truth, not the mirage — and never breed a family off a divergently-delivered win (see `the-desk.md` G9 / `evidence-base.md`).

## Fatigue rotation

When a Vault winner later returns `fatigue-refresh` (frequency rising + CPA rising), `/hva-vault`:
1. marks the winner `fatiguing`,
2. hands its winning hypothesis back to `/hva-forge` to breed a **family** (same angle, fresh execution),
3. records the family under the parent winner,
4. retires the parent when its replacements confirm.

This is the systematic answer to "creative fatigue is the #1 scaling killer": the winning *angle* is preserved as an asset even as individual executions die.

## Why it stops mattering — and why that's fine

The edge from reading the signals competes away. The Vault is the bet that, by then, your accumulated system and data are the durable advantage. That is high-frequency trading done correctly: a market maker's discipline, not a gambler's velocity. The signals were always going to commoditize. The Vault is what you keep.
