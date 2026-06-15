# Evidence base — the receipts

Why each CLEAR rule and Read-Ladder threshold is where it is. These are the empirical anchors; the scorer's defaults trace back to them. When an operator asks "why 5,000 impressions?" or "why correct for multiple comparisons?", the answer is here.

## Learning phase — read by volume, not calendar

Ad sets generally need about **50 optimization events per ad set per week** to exit the learning phase; below that, delivery stays volatile and results are not indicative of long-term performance. The real variable is **conversion volume per optimization unit, not elapsed time.** This is why the Read Ladder is denominated in impressions and spend, and why "it's only been 48 hours" (G1) is not a valid reason to wait or to kill.

→ Drives: the Read Ladder rungs; CLEAR-A's two clocks; G1 (no calendar-time thinking); G4 (no micro-cells — a `$5/day` cell can take weeks to reach 50 events).

## Signal loss — the platform undercounts

Platform-reported conversions undercount real conversions by roughly **20–30%** since iOS 14.5, so kill rules built on platform-only data routinely pause profitable ad sets. Clean server-side data is the **precondition**, which is why it sits at Layer 0 as a *gate* rather than as one item in the moat list.

→ Drives: CLEAR-C (the clean gate, evaluated first); Layer 0; G3 (no killing on dirty data); the routine's hard-block when EMQ regresses below 8.

## Creative count — signal fragments past ~5

Past about **five creatives per ad set**, signal fragments and per-creative learning slows. The algorithm rewards variety and starves on redundancy.

→ Drives: Layer 2 ("≤5 creatives per ad set"); `max_creatives_per_adset` default 5; G5; G6 (no near-duplicate flooding).

## Divergent delivery — spend velocity is not creative truth

At scale, platform A/B tests show clear **audience imbalance across variants** — the creative effect is confounded with audience composition — while conversion-lift tests do not. Configuration choices (for example, manual placement) reduce it. So: read creative signal **inside one stable ad set** where delivery is far more comparable, and use **lift tests** for any causal "why it won." The ad the algorithm funds early may be the one it found a cheap audience for, not the better creative.

→ Drives: Layer 2 ("test inside one stable ad set"); the HVA concept-per-ad shape (G10); G9 (no spend-velocity-as-truth); the "high spend + early conversion = *candidate*, not winner" rule in the Diagnostic Table.

## Multiple comparisons — a hundred tests, a near-certain false winner

Testing `k` variants inflates the chance of at least one false winner to `1 - (1 - α)^k`. At the standard threshold this is a coin flip by roughly **fourteen variants** and **near-certain by a hundred**. Correct with **Benjamini-Hochberg** before believing any winner.

→ Drives: CLEAR-R; the `awaiting-replication` verdict; the scorer's B-H q-value gate before any `scale`; G8 (no uncorrected winner crowning).

| α | k | P(≥1 false winner) = 1−(1−α)^k |
|---|---|---|
| 0.05 | 1 | 5% |
| 0.05 | 14 | ~51% |
| 0.05 | 100 | ~99.4% |

## Naming, for the record

The framework is **High-Velocity Advertising (HVA)**, not High-Frequency Advertising — in-platform *frequency* already names how often one person sees an ad, and the collision confuses operators. (Repeated from `SKILL.md` because it is the single most common naming error.)
