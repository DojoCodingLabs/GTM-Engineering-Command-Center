# Elicitation Methods

## Core Principle

> **Rank, don't score. Never ask a synthetic respondent for a number.**

This is the governing law of SDV, and the half that this file enforces. Asking an LLM "rate your
purchase intent for this offer 1–5" collapses to a safe "3/4" and recovers only ~26% of human
reliability (the paper's DLR result). Instead: elicit a **brief free-text reaction in character** to
the GTM surface — an `ad_creative`, an `offer`, or a piece of `copy` — then map that text to a
distribution over the Likert scale in a *separate* step. This is the single most important rule in SDV.

It is not a stylistic preference; it lives in the artifact. The deterministic scorer
(`scripts/sdv-score.py`) **rejects** any reading whose pmf is near one-hot — the tell-tale signature of
a number that was elicited and softmaxed. See "What the scorer enforces" below.

## The Three Methods (and which to use)

| Method | What it is | Reliability (paper) | Needs embeddings? | When SDV uses it |
|--------|-----------|---------------------|-------------------|------------------|
| **DLR** Direct Likert Rating | Ask for the integer directly | KS 0.26, ρ≈26%, dist. useless | No | **Never** as a primary signal (baseline only) |
| **FLR** Follow-up Likert Rating | Free-text → LLM-as-Likert-expert maps it | KS 0.72, ρ≈85% | No | **Default** (prompt-only, zero setup) |
| **SSR** Semantic Similarity Rating | Free-text → embed → cosine to anchors → pmf | KS 0.88, ρ≈90% | Yes | **Optional** (auto-enabled if embeddings detected, the **+SSR** upgrade) |

> **Out-of-distribution caveat.** These figures are *reported on the paper's domain* (Maier et al.
> 2025 — personal-care surveys). GTM surfaces — ad creatives, offers, LATAM info-product pricing — are
> **out-of-distribution until F3-calibrated**. The ranking holds far better across domains than the
> absolute, but cite the numbers as "reported on the paper's domain," never as a guarantee for GTM.

SDV defaults to **FLR** because it needs no external infrastructure and still vastly outperforms DLR.
When an embeddings provider is detected, SDV upgrades to **SSR** (the **+SSR** tier modifier, via
`scripts/ssr_embed.py`) for the extra fidelity. Both produce the same artifact: a **per-respondent
probability mass function (pmf)** over the 5 Likert points, per construct.

## FLR Protocol (default, prompt-only)

Run this per respondent, per construct, per variant. It is a **three-step, two-call** protocol — the
react call and the map call are deliberately separated so the persona never sees the scale it will be
mapped onto.

### Step 1 — Prime the persona (richer than the paper)

The paper conditioned on demographics only — and gender/region/ethnicity didn't replicate. SDV
conditions on everything the persona panel already carries (read from `.gtm/personas/`, or an external
`srd/personas.yml`), because that's what actually drives info-product / B2B purchase. Build a system
prompt from the persona:

- **Demographics**: age, location, income (the two axes — age & income — the paper found *do* replicate).
- **Psychographics / JTBD**: goals, pain points, the job they're hiring this offer to do.
- **Wallet reality**: monthly_spend, budget pressure, what the price actually means to them (a $497
  LATAM info-product offer lands very differently on a $1,200/mo wallet than a $12,000/mo one).
- **Stance**: "You are skeptical by default. You have alternatives, including doing nothing. You guard
  your money. You are not trying to be agreeable."

This skeptic + budget framing is the primary defense against positivity bias (see below).

### Step 2 — Elicit the free-text reaction

Show the stimulus (the creative, offer stack, or landing block — text and/or image). Ask the
construct's question in-character. Request a **brief (1–3 sentence) honest reaction**, not a rating.
**The persona must never see the Likert scale in this call.** Example for purchase_intent on a $497
offer:

> "You've just landed on this page. Reacting honestly as yourself — would you actually buy it at $497?
> Say what you're thinking in a sentence or two."

A good reaction sounds like a real person: *"$497 is steep for a coach I've never heard of. If there
were a guarantee or proof it worked for someone like me, maybe — but right now I'd keep scrolling."*

The same shape works for a 9:16 creative hook (*"would this stop your thumb?"*) or a landing headline
(*"does this make you want to read on, or bounce?"*) — react first, never rate.

### Step 3 — Map text → pmf (the "Likert-rating expert" pass)

In a **separate** call/turn, act as a rating expert and map the reaction to a pmf over 1–5 using the
construct's anchor set (`anchor-sets.md`). **You MUST give the expert examples of what each rating's
language looks like** — the paper found that without examples the distribution comes out unrealistically
narrow. Output a distribution, not a point: e.g. `[0.05, 0.35, 0.45, 0.12, 0.03]`, not "2".

The mapping is soft on purpose: ambiguous reactions ("I'd probably try it if it's cheap") legitimately
spread probability across adjacent points. Preserving that spread is what reproduces realistic human
distributions — and what keeps the pmf from looking one-hot to the scorer.

## SSR Protocol (optional, the +SSR upgrade when embeddings detected)

Replace Step 3 with embedding similarity (the react call in Step 2 is unchanged — it still never sees
the scale):

1. Embed the free-text reaction and each of the 5 anchor statements (and ensemble sets).
2. Response likelihood of point *r* ∝ cosine(reaction, anchor_r) − min_r cosine (the ε-floor subtraction
   the paper uses to control variance).
3. Normalize to a pmf; optionally apply temperature `T` to control "smearing" (paper: ε=0, T=1 as the
   rule-of-thumb default).
4. Average pmfs across the anchor ensemble.

This is the *only* part of SDV that touches external infra. `scripts/ssr_embed.py` is stdlib-only and
MIT-licensed. If the embeddings call fails or no provider is configured, **fall back to FLR cleanly** —
never error out, just drop the **+SSR** modifier and record `elicitation_method: FLR`.

## Sampling & Variance Control

- Take **≥3 samples per respondent per construct** (the paper used n=2; more is better for stable pmfs).
- Use a non-trivial temperature (~0.7–1.0) so samples actually vary; average the resulting pmfs.
- Aggregate respondent pmfs into a segment pmf, **weighted by persona `user_pct`** (and `revenue_pct`
  for a revenue-weighted view). Report both the mean and a confidence interval (`calibration.md`).

## Defeating Positivity Bias

Synthetic consumers over-rate everything — every creative is a winner, every offer is a yes — unless
actively constrained. Stack these, and record which ones fired (missing defenses derate the forecast's
confidence):

1. **Skeptic stance** in the system prompt, verbatim: *"You are skeptical by default. You have
   alternatives, including doing nothing. You guard your money. You are not trying to be agreeable."*
2. **Budget salience** — make the price concrete against their wallet ("$497 is ~X% of your monthly income").
3. **The do-nothing option** — always remind them that *not buying* and *keeping the status quo* are valid.
4. **Moment-of-truth framing** for behavioral proxies — "card in hand, on the checkout page right now."
5. **Comparative mode** (`comparative-scaling.md`) — forcing a choice between variants naturally
   suppresses uniform 5/5 inflation, because they must discriminate. This is also why ranking is the
   headline signal, not the absolute score.

## What the scorer enforces (validity lives in the artifact, not the prose)

The two-step protocol is **machine-checkable**, and `scripts/sdv-score.py` checks it. Every reading must
carry its elicitation provenance, or it is rejected:

| Field | Required value | Why |
|-------|----------------|-----|
| `elicitation_method` | `FLR` or `SSR` | DLR is never a valid primary signal |
| `react_call_saw_scale` | `false` | proves the persona reacted in free text, blind to the Likert scale |
| `map_call_separate` | `true` | proves the text→pmf mapping was a separate call, not the same turn |

On top of these flags, the scorer **rejects near-one-hot pmfs as "number-elicited"**: a distribution
like `[0, 0, 0.97, 0.03, 0]` is the signature of a number that was asked for and softmaxed, and it fails
validation no matter what the provenance fields claim. A legitimate FLR/SSR pmf carries real spread
across adjacent points. This is the enforcement teeth behind "never ask for a number" — the rule is in
code, not just here.

## Common Mistakes

1. **Asking for the number** (DLR). The cardinal sin. Always free-text first.
2. **Skipping the examples** in the mapping step → narrow, unrealistic distributions.
3. **Letting the react call see the scale** → the persona pre-rates, and `react_call_saw_scale` must
   then be `true`, which the scorer treats as invalid.
4. **Collapsing to a point estimate** too early. Keep the pmf until the very end; one-hot pmfs are rejected.
5. **Unprimed personas** → everything rates 4–5. Prime skeptic + budget every time.
6. **n=1 sampling** → noisy, non-reproducible pmfs. Use ≥3.
7. **Erroring when embeddings are absent** instead of falling back to FLR (dropping the +SSR upgrade).
