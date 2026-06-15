#!/usr/bin/env python3
"""SDV scorer — the deterministic decision engine of Synthetic Demand Validation.

Reads a demand forecast (per-variant construct pmfs + a comparative-ranking block)
and emits a comparative ranking + a DEPLOY/TEST/ITERATE/SKIP verdict per variant.
Stdlib only (no numpy) so it runs anywhere the plugin's Python does, and — critically —
so it carries NO dependency on Tribe v2 (CC-BY-NC). This file is MIT.

Governing law (skills/synthetic-demand/SKILL.md):
    "Rank, don't score. Never ask a synthetic respondent for a number."

The science lives in code, not prose. These guardrails are enforced here, each pinned
by a test in scripts/tests/test_sdv_score.py:

  §1  Comparative-FIRST: rank + rank_stability drive the verdict; the absolute
      demand_score is a SECONDARY gate that can only make a verdict more conservative,
      never mint a DEPLOY. Below F3 the absolute field is `demand_score_relative`
      ("uncalibrated — directional only").
  §4  FLR provenance is machine-checked: DLR-as-primary and one-hot / near-delta pmfs
      (the signature of "asked for a number") are REJECTED.
  §5  intent->behavior discount is 0.5 below F3, and 1.0 only when an F3 calibration
      map justifies it.
  §6  rank_stability needs >= 5 resamples; fewer is "indeterminate"; a flipping top is
      "unstable" (carries the HVA Benjamini-Hochberg "don't bet on a ghost" discipline).
  §7  positivity-bias defenses are auditable; missing ones derate confidence.
  §8  no cross-surface comparison.

Contract: skills/synthetic-demand/SKILL.md + skills/synthetic-demand/rules/
Tests:    scripts/tests/test_sdv_score.py  (python3 -m unittest discover scripts/tests)

The scorer NEVER polls a model and NEVER acts. It only decides. The demand-forecaster
agent elicits the reactions and acts on the decision. Keeping elicitation, decision, and
action separate is what makes the decision reproducible and testable in isolation.

CLI:
    sdv-score.py FORECAST.json [--config .gtm/config.json]
                 [--autonomy recommend|cut-auto|full-auto] [--out OUT.json]
    FORECAST may be "-" to read from stdin.
"""
import argparse
import json
import math
import sys

# Construct-battery default weights (skills/synthetic-demand/rules/construct-battery.md).
# willingness_to_pay is a price, not a 0-1 construct, so it never enters the blend.
DEFAULT_WEIGHTS = {
    "purchase_intent": 0.35,
    "price_fairness": 0.15,
    "appeal": 0.15,
    "comprehension": 0.10,
    "differentiation": 0.10,
    "believability": 0.10,
    "share_intent": 0.05,
}

DEFAULTS = {
    "autonomy": "recommend",
    "deploy_threshold": 70.0,
    "test_threshold": 55.0,
    "iterate_threshold": 40.0,
    "min_resamples": 5,
    "stable_hold_fraction": 0.9,
    "stable_min_tau": 0.5,
    "degenerate_pmf_max": 0.95,     # max single-point mass before a pmf looks number-elicited
    "default_discount": 0.5,        # Juster-scale-inspired intent->behavior haircut below F3
    "tier_factor": {"F0": 1.0, "F1": 0.8, "F2": 0.6, "F3": 0.4},
}

VALID_SURFACES = ("ad_creative", "offer", "copy", "feature")
_VERDICT_ORDER = ("SKIP", "ITERATE", "TEST", "DEPLOY")


# --------------------------------------------------------------------------- #
# pmf primitives + the demand_score formula
# --------------------------------------------------------------------------- #
def pmf_mean(pmf):
    """Mean of a length-5 pmf on the 1..5 Likert scale."""
    return sum((i + 1) * p for i, p in enumerate(pmf))


def validate_pmf(pmf):
    """A construct distribution must be a length-5 pmf summing to ~1.0 with no negatives."""
    if len(pmf) != 5:
        raise ValueError(f"pmf must have exactly 5 points, got {len(pmf)}")
    if any(p < 0 for p in pmf):
        raise ValueError(f"pmf has negative mass: {pmf}")
    if abs(sum(pmf) - 1.0) > 0.02:
        raise ValueError(f"pmf must sum to ~1.0 (+/-0.02), got {sum(pmf)}")


def pmf_entropy(pmf):
    return -sum(p * math.log(p) for p in pmf if p > 0)


def is_degenerate_pmf(pmf, max_mass=DEFAULTS["degenerate_pmf_max"]):
    """A near-delta pmf is the signature of 'asked for a number' (§4)."""
    return max(pmf) >= max_mass


def demand_score(means, weights):
    """Composite Demand Score 0-100 over the measured construct subset (§construct-battery).

    demand_score = 100 * Σ( w_c * (mean_c - 1) / 4 ), weights renormalized over whatever
    subset was measured. willingness_to_pay is a price and is excluded from the blend.
    """
    measured = {c: m for c, m in means.items()
                if c in weights and c != "willingness_to_pay"}
    total_w = sum(weights[c] for c in measured)
    if total_w <= 0:
        return 0.0
    return 100.0 * sum((weights[c] / total_w) * (measured[c] - 1.0) / 4.0 for c in measured)


# --------------------------------------------------------------------------- #
# §4 — FLR provenance: validity must live in the artifact, not just the prose
# --------------------------------------------------------------------------- #
def validate_elicitation(rec):
    """Reject readings that silently revert to the ~26% DLR failure mode.

    A reading is only trustworthy if it came from (a) a free-text reaction generated
    WITHOUT the Likert scale in context, then (b) a SEPARATE mapping call. DLR-as-primary
    and one-hot pmfs (asking for a number then one-hot-ing it) are rejected.
    """
    pmf = rec.get("pmf")
    if pmf is None:
        raise ValueError("elicitation record missing 'pmf'")
    validate_pmf(pmf)
    method = str(rec.get("elicitation_method", "")).upper()
    if method not in ("FLR", "SSR"):
        raise ValueError(
            f"elicitation_method must be FLR or SSR (got {method!r}); "
            "DLR-as-primary recovers only ~26% reliability — never ask for a number.")
    if rec.get("react_call_saw_scale") is not False:
        raise ValueError(
            "react_call_saw_scale must be false: the free-text reaction call must NOT see "
            "the Likert scale (it is mapped to a pmf in a separate step).")
    if rec.get("map_call_separate") is not True:
        raise ValueError("map_call_separate must be true: mapping happens in a separate call.")
    if is_degenerate_pmf(pmf):
        raise ValueError(
            f"pmf {pmf} is near one-hot — the signature of a number-elicited rating, not a "
            "free-text-derived distribution. Re-elicit with the two-step FLR/SSR protocol.")


# --------------------------------------------------------------------------- #
# Comparative scaling — the headline signal
# --------------------------------------------------------------------------- #
def best_worst_share(best, worst, appeared):
    """best_worst_share(V) = (times best - times worst) / times appeared, in [-1, 1]."""
    out = {}
    for v in appeared:
        n = appeared[v]
        out[v] = ((best.get(v, 0) - worst.get(v, 0)) / n) if n else 0.0
    return out


def win_rate(wins, participated):
    """win_rate(V) = duels won / duels participated."""
    return {v: (wins.get(v, 0) / participated[v] if participated[v] else 0.0)
            for v in participated}


def bradley_terry(pair_wins, iterations=100):
    """Bradley-Terry strengths from pairwise win counts {(A,B): wins_of_A_over_B}.

    Returns a normalized strength per variant via the standard MM update.
    """
    players = set()
    for a, b in pair_wins:
        players.update((a, b))
    if not players:
        return {}
    strength = {p: 1.0 for p in players}
    wins = {p: 0.0 for p in players}
    games = {}  # (i, j) ordered pair -> count of games between i and j
    for (a, b), w in pair_wins.items():
        wins[a] += w
        games[(a, b)] = games.get((a, b), 0.0) + w
        games[(b, a)] = games.get((b, a), 0.0) + w
    for _ in range(iterations):
        new = {}
        for p in players:
            denom = 0.0
            for q in players:
                if q == p:
                    continue
                n = games.get((p, q), 0.0)
                if n:
                    denom += n / (strength[p] + strength[q])
            new[p] = wins[p] / denom if denom > 0 else strength[p]
        s = sum(new.values())
        strength = {p: (new[p] / s if s else new[p]) for p in players}
    return strength


def kendall_tau(rank_a, rank_b):
    """Kendall's tau-a between two orderings of the same items."""
    items = list(rank_a)
    pos_b = {x: i for i, x in enumerate(rank_b)}
    pos_a = {x: i for i, x in enumerate(rank_a)}
    n = len(items)
    if n < 2:
        return 1.0
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            x, y = items[i], items[j]
            a_order = pos_a[x] - pos_a[y]
            b_order = pos_b[x] - pos_b[y]
            if a_order * b_order > 0:
                concordant += 1
            elif a_order * b_order < 0:
                discordant += 1
    total = n * (n - 1) / 2
    return (concordant - discordant) / total if total else 1.0


def rank_stability(rankings, min_resamples=DEFAULTS["min_resamples"],
                   hold_fraction=DEFAULTS["stable_hold_fraction"],
                   min_tau=DEFAULTS["stable_min_tau"]):
    """Real stability estimate (§6) — not a boolean from one resample.

    Fewer than `min_resamples` -> 'indeterminate'. Otherwise report the fraction of
    resamples whose #1 matches the modal #1 and the mean pairwise Kendall tau; a lead
    within resample noise is 'unstable' (a tie), mirroring HVA's q>alpha discipline.
    """
    n = len(rankings)
    if n < min_resamples:
        return {"status": "indeterminate", "n_resamples": n,
                "top_hold_fraction": None, "mean_kendall_tau": None,
                "reason": f"only {n} resample(s); need >= {min_resamples} to judge stability"}
    tops = [r[0] for r in rankings if r]
    modal_top = max(set(tops), key=tops.count)
    top_hold = tops.count(modal_top) / len(tops)
    taus = [kendall_tau(rankings[i], rankings[i + 1]) for i in range(n - 1)]
    mean_tau = sum(taus) / len(taus) if taus else 1.0
    stable = top_hold >= hold_fraction and mean_tau >= min_tau
    return {"status": "stable" if stable else "unstable",
            "n_resamples": n, "modal_top": modal_top,
            "top_hold_fraction": round(top_hold, 4),
            "mean_kendall_tau": round(mean_tau, 4)}


# --------------------------------------------------------------------------- #
# Calibration + fidelity
# --------------------------------------------------------------------------- #
def detect_tier(capabilities):
    """Highest fidelity tier whose trigger is satisfied (calibration.md)."""
    if capabilities.get("conversion_data"):
        return "F3"
    if capabilities.get("customer_language") or capabilities.get("analytics"):
        return "F2"
    if capabilities.get("personas"):
        return "F1"
    return "F0"


def intent_behavior_discount(tier, calibration=None, default=DEFAULTS["default_discount"]):
    """Convert stated intent to estimated action (§5).

    Below F3 (or F3 without a valid fitted map) apply the conservative default haircut.
    1.0 is only ever returned when an F3 calibration map justifies it.
    """
    if tier == "F3" and calibration and calibration.get("valid"):
        return float(calibration.get("learned_discount", default))
    return default


def ci_width(tier, familiarity, effective_samples,
             tier_factor=None):
    """Relative CI width: wider for lower tiers, unfamiliar domains, fewer samples."""
    tf = (tier_factor or DEFAULTS["tier_factor"]).get(tier, 1.0)
    n = max(1, effective_samples)
    return tf * (1.0 + (1.0 - familiarity)) / math.sqrt(n)


# --------------------------------------------------------------------------- #
# Price sensitivity (offers only) — Van Westendorp + Gabor-Granger
# --------------------------------------------------------------------------- #
def _crossing(curve_a, curve_b, prices):
    """Price where two cumulative curves meet (linear interpolation on the sign change)."""
    diffs = [curve_a.get(p, 0.0) - curve_b.get(p, 0.0) for p in prices]
    for p, d in zip(prices, diffs):
        if abs(d) < 1e-9:
            return float(p)
    for i in range(len(prices) - 1):
        d0, d1 = diffs[i], diffs[i + 1]
        if d0 * d1 < 0:
            p0, p1 = prices[i], prices[i + 1]
            return p0 + (p1 - p0) * (d0 / (d0 - d1))
    return float(prices[0]) if abs(diffs[0]) <= abs(diffs[-1]) else float(prices[-1])


def van_westendorp_crossings(curves):
    """Van Westendorp PSM crossings from the four cumulative price curves.

    curves = {"too_cheap","cheap","expensive","too_expensive"} -> {price: fraction}.
    too_cheap/cheap descend with price; expensive/too_expensive ascend. Returns the four
    crossings and the acceptable range [PMC, PME] (rules/price-sensitivity.md).
    """
    prices = sorted({p for c in curves.values() for p in c})
    pmc = _crossing(curves["too_cheap"], curves["expensive"], prices)       # lower bound
    pme = _crossing(curves["cheap"], curves["too_expensive"], prices)       # upper bound
    opp = _crossing(curves["too_cheap"], curves["too_expensive"], prices)   # optimal price point
    ipp = _crossing(curves["cheap"], curves["expensive"], prices)           # indifference price point
    return {"pmc": pmc, "pme": pme, "opp": opp, "ipp": ipp,
            "acceptable_range": [pmc, pme]}


def gabor_granger_revenue_index(price_conversion):
    """Gabor-Granger: revenue_index(p) = p * est_conversion(p); argmax = revenue-max price."""
    items = sorted(price_conversion.items())
    curve = [{"price": p, "est_conversion": c, "revenue_index": round(p * c, 4)}
             for p, c in items]
    best = max(curve, key=lambda x: x["revenue_index"]) if curve else None
    return {"demand_curve": curve,
            "revenue_max_price": best["price"] if best else None}


def is_monotonic_nonincreasing(values):
    """A real demand curve never rises with price; rising est_conversion is noise to flag."""
    return all(values[i] >= values[i + 1] for i in range(len(values) - 1))


# --------------------------------------------------------------------------- #
# §1 — the verdict: comparative-first, absolute only sharpens conservatively
# --------------------------------------------------------------------------- #
def _idx(verdict):
    return _VERDICT_ORDER.index(verdict)


def get_verdict(rank, rank_stability, demand_score_relative, tier,
                calibration_valid=False, cfg=None):
    """DEPLOY/TEST/ITERATE/SKIP as the MINIMUM of three independent ceilings.

    The ranking is the headline; the absolute score and the fidelity tier can only pull
    the verdict DOWN, never up. Only a stable comparative winner at F3-with-calibration can
    reach DEPLOY. (rank_stability is the string status from rank_stability()['status'].)
    """
    cfg = {**DEFAULTS, **(cfg or {})}
    is_winner = (rank == 1)

    # Comparative ceiling — only a stable winner can reach DEPLOY.
    if rank_stability == "stable" and is_winner:
        comparative = "DEPLOY"
    else:
        comparative = "TEST"  # non-winner, unstable (tie), or indeterminate

    # Absolute ceiling — secondary; can only make things more conservative.
    s = demand_score_relative
    if s >= cfg["deploy_threshold"]:
        absolute = "DEPLOY"
    elif s >= cfg["test_threshold"]:
        absolute = "TEST"
    elif s >= cfg["iterate_threshold"]:
        absolute = "ITERATE"
    else:
        absolute = "SKIP"

    # Tier ceiling — no absolute go/no-go below F3 (§2/§5).
    tier_ceiling = "DEPLOY" if (tier == "F3" and calibration_valid) else "TEST"

    return _VERDICT_ORDER[min(_idx(comparative), _idx(absolute), _idx(tier_ceiling))]


def resolve_action(verdict, autonomy):
    """The ONLY place autonomy is applied. Spending (DEPLOY) is always human-gated."""
    if verdict == "SKIP":
        return "auto-archive" if autonomy in ("cut-auto", "full-auto") else "recommend-archive"
    if verdict == "DEPLOY":
        return "recommend-deploy"  # never auto — deploying spends money, mirrors HVA scaling
    return "hold"


# --------------------------------------------------------------------------- #
# §7 / §8 — auditable guards
# --------------------------------------------------------------------------- #
def positivity_warnings(priming, n_variants):
    """Surface missing anti-positivity defenses so confidence can be derated (§7)."""
    w = []
    if not priming.get("skeptic_stance_applied"):
        w.append("skeptic-stance missing — synthetic respondents over-rate without it")
    if not priming.get("budget_salience_applied"):
        w.append("budget-salience missing — price not made concrete against the wallet")
    if not priming.get("comparative_mode") and n_variants > 1:
        w.append("comparative-mode off — forced choice suppresses uniform 5/5 inflation")
    if n_variants == 1 and not priming.get("do_nothing_option_present"):
        w.append("single-variant run without a do-nothing / status-quo reference")
    return w


def assert_single_surface(variants):
    """No cross-surface comparison (§8): a demand_score of 70 on a 4-construct copy subset
    is not the same evidentiary thing as 70 on the 7-construct offer battery."""
    surfaces = {v.get("surface") for v in variants}
    if len(surfaces) > 1:
        raise ValueError(
            f"cannot compare across surfaces {sorted(surfaces)} — demand_scores are only "
            "comparable within a single surface (different construct subsets/weights).")
    return surfaces.pop() if surfaces else None


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def _surface_weights(surface, override):
    """Per-surface construct weights (construct-battery.md reweighting)."""
    if override:
        return dict(override)
    w = dict(DEFAULT_WEIGHTS)
    if surface == "ad_creative":
        w = {"purchase_intent": 0.30, "appeal": 0.25, "comprehension": 0.20,
             "differentiation": 0.15, "share_intent": 0.10}
    elif surface == "copy":
        w = {"purchase_intent": 0.30, "comprehension": 0.30,
             "believability": 0.25, "appeal": 0.15}
    return w


def _ranking_from_comparison(comp):
    """Return (ordered_variant_ids, score_map, instrument)."""
    method = comp.get("method", "best_worst")
    if method == "win_rate":
        scores = win_rate(comp["wins"], comp["participated"])
    elif method == "bradley_terry":
        scores = bradley_terry({tuple(k.split("|")): v
                                for k, v in comp["pair_wins"].items()})
    else:
        scores = best_worst_share(comp["best"], comp["worst"], comp["appeared"])
    ordered = sorted(scores, key=lambda v: scores[v], reverse=True)
    return ordered, scores, method


def score_forecast(forecast, config):
    """Score a demand forecast. Returns {summary, fidelity, ranking, variants}."""
    cfg = {**DEFAULTS, **{k: v for k, v in (config or {}).items() if v is not None}}
    autonomy = cfg.get("autonomy", "recommend")

    variants = forecast["variants"]
    surface = assert_single_surface(variants) or forecast.get("surface")
    if surface not in VALID_SURFACES:
        raise ValueError(f"surface must be one of {VALID_SURFACES}, got {surface!r}")
    weights = _surface_weights(surface, forecast.get("weights"))

    tier = forecast.get("tier") or detect_tier(forecast.get("capabilities", {}))
    familiarity = float(forecast.get("familiarity", 0.5))
    calibration = forecast.get("calibration")
    calib_valid = bool(tier == "F3" and calibration and calibration.get("valid"))

    # Comparative ranking — the headline.
    comp = forecast["comparison"]
    ordered, comp_scores, instrument = _ranking_from_comparison(comp)
    stability = rank_stability(comp.get("resamples", []),
                               min_resamples=cfg["min_resamples"])
    rank_of = {vid: i + 1 for i, vid in enumerate(ordered)}

    scored = []
    for v in variants:
        means = {}
        for cname, rec in v["constructs"].items():
            validate_elicitation(rec)  # §4: rejects number-elicited readings
            means[cname] = pmf_mean(rec["pmf"])
        dscore = demand_score(means, weights)
        rank = rank_of.get(v["id"], len(ordered) + 1)
        verdict = get_verdict(rank, stability["status"], dscore, tier,
                              calibration_valid=calib_valid, cfg=cfg)
        warnings = positivity_warnings(v.get("priming", {}), len(variants))
        score_label = "demand_score_calibrated" if calib_valid else "demand_score_relative"
        scored.append({
            "id": v["id"],
            "surface": surface,
            "rank": rank,
            "comparative_score": round(comp_scores.get(v["id"], 0.0), 4),
            score_label: round(dscore, 1),
            "absolute_status": "calibrated" if calib_valid else "uncalibrated — directional only",
            "verdict": verdict,
            "autonomy_action": resolve_action(verdict, autonomy),
            "construct_means": {k: round(val, 3) for k, val in means.items()},
            "confidence_warnings": warnings,
        })

    scored.sort(key=lambda s: s["rank"])
    counts = {k: 0 for k in _VERDICT_ORDER}
    for s in scored:
        counts[s["verdict"]] += 1

    return {
        "summary": {
            "surface": surface,
            "instrument": instrument,
            "tier": tier,
            "autonomy": autonomy,
            "counts": counts,
            "winner": ordered[0] if ordered else None,
        },
        "fidelity": {
            "tier": tier,
            "directional": tier != "F3",
            "rank_stability": stability,
            "ci_width": round(ci_width(tier, familiarity,
                                       int(forecast.get("effective_samples", 9))), 4),
            "intent_behavior_discount": intent_behavior_discount(tier, calibration),
            "familiarity": familiarity,
        },
        "ranking": [{"id": vid, "rank": i + 1, "comparative_score": round(comp_scores[vid], 4)}
                    for i, vid in enumerate(ordered)],
        "variants": scored,
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _load_config(path, overrides):
    cfg = {}
    if path:
        try:
            with open(path) as f:
                raw = json.load(f)
            cfg.update(raw.get("sdv", {}))
        except (OSError, ValueError) as e:
            print(f"warning: could not read config {path}: {e}", file=sys.stderr)
    for k, v in overrides.items():
        if v is not None:
            cfg[k] = v
    return cfg


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="SDV scorer — comparative-first demand validation (rank, don't score).")
    ap.add_argument("forecast", help='forecast JSON file, or "-" for stdin')
    ap.add_argument("--config", help="path to .gtm/config.json")
    ap.add_argument("--autonomy", choices=["recommend", "cut-auto", "full-auto"])
    ap.add_argument("--out", help="write decision JSON here (default: stdout)")
    args = ap.parse_args(argv)

    text = sys.stdin.read() if args.forecast == "-" else open(args.forecast).read()
    forecast = json.loads(text)
    cfg = _load_config(args.config, {"autonomy": args.autonomy})

    try:
        result = score_forecast(forecast, cfg)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    out_text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out_text + "\n")
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
