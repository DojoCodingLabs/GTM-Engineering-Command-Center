# Optional SRD Interop — Interoperate, Don't Duplicate

## Core Principle — the coupling is INVERTED

This file is the **optional** bridge between SDV and the external **SRD framework** plugin
([github.com/DojoCodingLabs/srd-framework](https://github.com/DojoCodingLabs/srd-framework)). It is the
*only* place in this skill where SRD is a first-class concern, and even here the relationship is
deliberately one-sided:

> **GTM owns its outputs and never depends on SRD. The coupling is inverted versus the source.**

In the source framing, the demand layer was a *consumer* of SRD's journeys and gap-audit. Here that arrow
is reversed. SDV **reads** a couple of SRD files when they happen to exist (a courtesy upgrade to its
panel and its calibration), **emits** its own GTM-owned artifacts regardless, and exposes one **thin,
optional adapter** that SRD — or a human — may read if they like. Nothing in the core loop (`SKILL.md`,
steps 1–10) waits on SRD, imports SRD, or writes into SRD's formats.

The proof obligation is concrete and testable: **an identical SDV run must complete using only `.gtm/`
when no SRD is present.** If removing `srd/` changes the verdict, the firewall has leaked.

The governing law still rules this bridge — interop never becomes a back door for a number:

> **Rank, don't score. Never ask a synthetic respondent for a number.**

## When this file applies (and when it does nothing)

| Situation | What happens |
|---|---|
| **SRD absent** (the common case) | This file is a no-op. SDV runs F0→F3 on `.gtm/` alone. Nothing below fires. |
| **SRD present** | SDV *may* read two SRD inputs (panel, calibration) and *may* export one adapter. All of it is additive and optional — never load-bearing. |

There is no configuration that makes SRD **required**. The absence path is not a degraded path; it is the
reference path. The presence path only ever *adds* grounding.

## Step A — Detection (READ-ONLY, both signals required)

Detection mirrors the read-only discipline of `rules/fidelity-tiers.md` Step 1: **never write to, transact
against, or call out to SRD while probing.** Two independent signals must **both** be present before any
interop behavior is considered:

1. **The plugin is installed** — an `srd-framework` plugin is present in the environment.
2. **The project opted in** — an `srd/` directory exists in the project root.

```
srd_interop_available  =  plugin_installed("srd-framework")  AND  exists("srd/")
```

Requiring both prevents a globally-installed plugin from silently coupling a project that never asked for
it. Record the outcome (and which of `srd/personas.yml`, `srd/conversion-pairs`, etc. were seen) in
`calibration_metadata.detected_capabilities.srd_interop` — alongside the GTM capability flags, never
replacing them. If either signal is missing, `srd_interop_available = false` and the rest of this file is
inert.

## Step B — What GTM may READ from SRD (a courtesy upgrade, never a dependency)

When (and only when) `srd_interop_available`, SDV may read **exactly two** things from SRD. Both are
*reads* that improve grounding; neither is required for the tier they touch — `.gtm/` satisfies the same
trigger on its own.

### B.1 — `srd/personas.yml` → the 9-field GTM persona panel (F1)

SDV may read `srd/personas.yml` and **project it down** to the GTM panel the elicitor already consumes
(`rules/elicitation-methods.md`, Step 1). The projection is lossy on purpose: SDV keeps only the
**9 fields** its persona panel uses and discards the rest of SRD's persona shape.

| # | GTM persona-panel field | What it conditions |
|---|---|---|
| 1 | `age` | demographics (an axis the paper found *does* replicate) |
| 2 | `location` | demographics / regional pricing reality |
| 3 | `income` | demographics (the second replicating axis) |
| 4 | `goals` | psychographics / JTBD — what they're hiring the offer to do |
| 5 | `pain_points` | psychographics / JTBD |
| 6 | `jtbd` | the job the offer is hired for |
| 7 | `monthly_spend` | wallet reality — what the price actually means to this wallet |
| 8 | `budget_pressure` | wallet reality — do-nothing salience |
| 9 | `segment_revenue_pct` | segment weighting for aggregation **and** revenue-at-risk |

This is the **same** panel SDV builds from `.gtm/personas/`. SRD's file is just an *alternate source* for
it — exactly the substitution already noted across `SKILL.md`, `fidelity-tiers.md`, and
`elicitation-methods.md` ("read `.gtm/personas/`, **or** an external `srd/personas.yml`"). Reading it
satisfies the **F1** trigger; so does `.gtm/personas/`. SRD is never the only way to reach F1.

> **Precedence.** If both exist, `.gtm/personas/` wins — GTM's own panel is canonical and SRD fills gaps,
> never overrides. Record the source in the panel provenance so the forecast says where its people came
> from.

### B.2 — SRD conversion pairs → F3 calibration (read at F3 only)

At **F3**, and only at F3, SDV may read SRD's recorded conversion pairs as **additional**
`(synthetic_signal, actual_conversion)` training pairs for the outcome-calibration map `g`
(`rules/calibration.md`, Step 3). They are appended to `.gtm/sdv/calibration/`, tagged by surface, and
subject to **every** F3 guardrail without exception:

- they obey the surface firewall — an SRD product-checkout pair is an **`offer`/checkout-CVR** pair and is
  **never** pooled into a creative's CTR map;
- they count toward, but cannot *bypass*, the evidence floor (minimum pairs across ≥K distinct outcome
  levels, held-out residual, calibration CI not spanning the verdict boundary);
- they are recomputed the *same* way the scorer would today — never a stale hand-entered number.

SRD pairs **enrich** the calibration; they never *unlock* F3 by themselves. If the only conversion
evidence in the project is SRD's, the GTM evidence floor in `rules/calibration.md` §5 still governs
whether F3's absolute go/no-go is earned. Capability-detected-F3 with too few/too-flat pairs — SRD's
included — stays **F2-with-pending-calibration**.

## Step C — What GTM EMITS (its own artifacts, always, SRD or not)

SDV writes **its own** objection ledger regardless of SRD. The Phase-6 GTM-owned artifact is the
**revenue-at-risk ledger** at:

```
.gtm/sdv/revenue-at-risk.md
```

This is the B0/B1/B2 blocker ledger from `rules/objection-mining.md`, sorted by `revenue_at_risk`, written
by the funnel-diagnostician. It is **GTM-native**: the B-axis (B = Blocker) deliberately replaces SRD's
`D0/D1/D2` naming, and the ledger lives under `.gtm/`, not under `srd/`. It is produced whether or not SRD
is installed — the absence path and the presence path write the **same** file to the **same** place.

**What GTM explicitly does NOT do:**

- **Does NOT write into `srd/gap-audit.md`'s format.** GTM never adopts SRD's gap-audit schema as its
  output. Its native output is `.gtm/sdv/revenue-at-risk.md`, in GTM's own B-tier shape.
- **Does NOT reimplement SRD's journeys, gap-audit, or guardian.** Those are SRD's disciplines. SDV has
  its own (panel, elicitation, comparative ranking, construct battery, price sweep, objection mining,
  calibration) and does not duplicate SRD's.

## Step D — The thin adapter (optional, one-way, SRD-readable)

When `srd_interop_available`, SDV *may* additionally expose a **thin adapter** so SRD (or a user) can
*read* GTM's demand findings — a one-way courtesy export, never a write into SRD's internal formats:

- It is a **projection of the already-written** `.gtm/sdv/revenue-at-risk.md` — B-tier objections as
  demand-tagged fix items SRD's gap-audit *can choose to* consume. (See `objection-mining.md` → "Optional
  Phase-7 interop with SRD.")
- It is **derived, not primary.** The canonical artifact is and remains `.gtm/sdv/revenue-at-risk.md`. The
  adapter is a read-view on top of it; deleting the adapter loses nothing GTM owns.
- It is **one-way out.** GTM emits a thing SRD may read. GTM does not read SRD's gap-audit back, does not
  write into SRD's files, and does not let SRD's presence change any GTM verdict.

If a user never wires the adapter into SRD, nothing breaks — the GTM ledger stands on its own.

## The F3 "actual conversion" adapter, per surface (with the SRD seam called out)

This restates the surface-level calibration adapter from `rules/calibration.md`, marking exactly where the
**optional** SRD seam attaches. The GTM bindings are primary; SRD is an add-on the **offer** surface may
*also* draw on.

| Surface | Calibrates against (GTM-primary "actual conversion") | Optional SRD seam |
|---|---|---|
| **`ad_creative`** | Meta / Google ad **CVR · CTR · ROAS** (`/gtm-metrics` snapshots) | — none — creative outcomes are GTM-owned ad data |
| **`offer`** | **checkout CVR** (Stripe / PostHog funnel) | *(interop)* SRD **product checkout** conversion, appended as additional `offer`/checkout-CVR pairs |
| **`copy`** | downstream conversion of the page the copy is on (PostHog / GA) | — none — |

The SRD product-checkout signal is **only** ever an `offer`-surface, checkout-CVR pair. It never crosses
into the creative or copy maps — same §8 / §6 surface firewall that forbids cross-surface `demand_score`
comparison forbids cross-surface calibration. Remove SRD and the offer surface still calibrates against
Stripe/PostHog checkout CVR exactly as before.

## The absence-path guarantee (the test that keeps us honest)

Restating the obligation as an acceptance test, because it is the whole point of this file:

> **Run SDV on a project with no `srd-framework` plugin and no `srd/` directory. The forecast — its
> fidelity tier, its comparative ranking, its `demand_score`, its B0/B1/B2 ledger at
> `.gtm/sdv/revenue-at-risk.md`, and its F3 calibration where earned — completes identically using only
> `.gtm/`.**

If any of those depend on SRD being present, the inversion has been violated and the bridge is a coupling.
SRD presence may only ever *add* (an alternate persona source, extra calibration pairs, a readable
adapter). It may never *subtract* and may never *gate*.

## Common Mistakes

1. **Letting SRD become a dependency.** SDV must complete on `.gtm/` alone. If removing `srd/` changes the
   verdict, this bridge has leaked into the core loop — fix it.
2. **Detecting on one signal.** Both the installed `srd-framework` plugin **and** a project `srd/`
   directory are required. A globally-installed plugin must not couple a project that never opted in.
3. **Writing into `srd/gap-audit.md`'s format.** GTM emits `.gtm/sdv/revenue-at-risk.md` in its own
   B-tier shape. The adapter is a one-way read-view, not a write into SRD's schema.
4. **Reimplementing SRD's journeys / gap-audit / guardian.** Those are SRD's disciplines; SDV has its own
   and does not duplicate them.
5. **Pooling SRD product-checkout pairs into a creative map.** SRD checkout is an `offer`/checkout-CVR
   signal only — never cross the surface firewall.
6. **Unlocking F3 on SRD pairs alone.** SRD pairs enrich calibration; they don't bypass the GTM evidence
   floor (`rules/calibration.md` §5). Too few / too flat ⇒ stay F2-with-pending-calibration.
7. **Treating SRD's persona file as canonical over `.gtm/personas/`.** GTM's own panel wins; `srd/personas.yml`
   is an alternate source projected to the 9-field panel, and it fills gaps — it never overrides.
8. **Calling out to SRD during detection.** Detection is read-only: probe for presence, never transact.
