#!/usr/bin/env python3
"""HVA Desk scorer — the deterministic decision engine of Layer 3.

Reads Meta insights (per-ad = per-concept rows) and emits a cut/hold/scale
verdict per creative, with the triggering CLEAR signal and a Benjamini-Hochberg
q-value for any winner claim. Stdlib only (no numpy/scipy) so it runs anywhere
the plugin's Python does.

Contract: skills/high-velocity-advertising/rules/the-desk.md
Tests:    scripts/tests/test_hva_score.py  (python3 -m unittest discover scripts/tests)

The scorer NEVER calls the Meta CLI. It only decides. The hva-desk agent acts on
the decision. Keeping decision and action separate is what makes the decision
reproducible and testable in isolation.

CLI:
    hva-score.py INSIGHTS.json [--config .gtm/config.json] [--target-cpa N]
                 [--autonomy recommend|cut-auto|full-auto] [--out OUT.json]
    INSIGHTS may be "-" to read from stdin.
"""
import argparse
import json
import math
import statistics
import sys

DEFAULTS = {
    "target_cpa": None,
    "kill_multiple": 3.0,
    "bh_alpha": 0.10,
    "frequency_ceiling": 3.0,
    "ctr_margin": 0.6,
    "hard_read_spend_multiple": 2.0,
    "autonomy": "recommend",
    "scale_bid_cap_multiple": 0.7,
    "max_daily_budget_increase_pct": 20,
}


# --------------------------------------------------------------------------- #
# Statistics primitives
# --------------------------------------------------------------------------- #
def normal_cdf(z):
    """Standard normal CDF via the error function (stdlib)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def two_proportion_z_pvalue(x_i, n_i, x_rest, n_rest):
    """One-sided two-proportion z-test: P(rate_i > rate_rest).

    Returns the upper-tail p-value. No evidence (1.0) when a group is empty or
    the pooled variance is zero.
    """
    if n_i <= 0 or n_rest <= 0:
        return 1.0
    p_i = x_i / n_i
    p_rest = x_rest / n_rest
    p_pool = (x_i + x_rest) / (n_i + n_rest)
    se = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n_i + 1.0 / n_rest))
    if se == 0.0:
        return 1.0
    z = (p_i - p_rest) / se
    return 1.0 - normal_cdf(z)


def benjamini_hochberg(pvalues):
    """Benjamini-Hochberg adjusted q-values, returned in the original order.

    q_(i) = min over ranks r >= i of (k / r) * p_(r), clamped to <= 1.0.
    """
    k = len(pvalues)
    if k == 0:
        return []
    order = sorted(range(k), key=lambda i: pvalues[i])
    q_sorted = [0.0] * k
    running_min = 1.0
    for rank in range(k, 0, -1):  # k down to 1
        idx = order[rank - 1]
        raw = (k / rank) * pvalues[idx]
        running_min = min(running_min, raw)
        q_sorted[rank - 1] = min(running_min, 1.0)
    q = [0.0] * k
    for rank in range(1, k + 1):
        q[order[rank - 1]] = q_sorted[rank - 1]
    return q


# --------------------------------------------------------------------------- #
# Normalization helpers
# --------------------------------------------------------------------------- #
def _norm_ctr(row):
    """Return CTR as a fraction. Accepts fraction (0.02) or percent (2.0)."""
    if row.get("ctr") is not None:
        ctr = float(row["ctr"])
        return ctr / 100.0 if ctr > 1.0 else ctr
    imps = float(row.get("impressions", 0) or 0)
    clicks = float(row.get("clicks", 0) or 0)
    return clicks / imps if imps > 0 else 0.0


def _is_below_average(row):
    q = str(row.get("quality_ranking", "")).lower()
    return q.startswith("below_average")


def rung_for(impressions, spend, target_cpa, hard_spend_multiple):
    hard_spend = (target_cpa or 0) * hard_spend_multiple
    if impressions >= 5000 or (target_cpa and spend >= hard_spend):
        return "hard"
    if impressions >= 2000:
        return "second"
    if impressions >= 1000:
        return "first"
    return "below-first"


def resolve_action(verdict, autonomy):
    """The ONLY place autonomy is applied. Pause automates a tier before scale."""
    if verdict == "cut":
        return "auto-pause" if autonomy in ("cut-auto", "full-auto") else "recommend-pause"
    if verdict == "scale":
        return "auto-scale" if autonomy == "full-auto" else "recommend-scale"
    return "hold"


# --------------------------------------------------------------------------- #
# The decision
# --------------------------------------------------------------------------- #
def _score_one(row, ctx):
    cfg = ctx["cfg"]
    target = cfg["target_cpa"]
    imps = float(row.get("impressions", 0) or 0)
    spend = float(row.get("spend", 0.0) or 0.0)
    conv = float(row.get("conversions", 0) or 0)
    micro = float(row.get("micro_conversions", 0) or 0)
    freq = float(row.get("frequency", 0.0) or 0.0)
    ctr = ctx["ctr"][row["ad_id"]]
    clean = row.get("clean", ctx["default_clean"])
    cpa = (spend / conv) if conv > 0 else None
    rung = rung_for(imps, spend, target, cfg["hard_read_spend_multiple"])
    qval = ctx["qmap"].get(row["ad_id"])

    def out(verdict, signal, reason, clock="none", q=None):
        return {
            "ad_id": row["ad_id"],
            "name": row.get("name", row["ad_id"]),
            "rung": rung,
            "verdict": verdict,
            "triggering_signal": signal,
            "reason": reason,
            "clock": clock,
            "q_value": q,
            "metrics": {
                "impressions": imps, "spend": round(spend, 2), "ctr": round(ctr, 5),
                "cpa": (round(cpa, 2) if cpa is not None else None), "conv": conv,
            },
            "autonomy_action": resolve_action(verdict, cfg["autonomy"]),
        }

    # C — clean gate (runs first; no clean feed, no decision)
    if not clean:
        return out("hold", "dirty-feed",
                   "No CAPI/server-side truth for this row — cannot decide on platform-only data.")

    # E — economics kill (fast clock)
    if target and spend >= cfg["kill_multiple"] * target and conv == 0:
        return out("cut", "economics-3x-cpa-zero-conv",
                   f"Spent ${spend:.2f} (>={cfg['kill_multiple']}x target CPA ${target:.2f}) "
                   f"with 0 qualifying events.", clock="fast")

    # L — leading-indicator cuts (fast clock)
    if imps >= 5000 and micro == 0 and conv == 0:
        return out("cut", "5k-impressions-zero-action",
                   f"{int(imps)} impressions, zero meaningful post-click action.", clock="fast")

    median_ctr = ctx["median_ctr"]
    if imps >= 2000 and median_ctr > 0 and ctr < cfg["ctr_margin"] * median_ctr and _is_below_average(row):
        return out("cut", "bad-hook-ctr",
                   f"CTR {ctr:.3%} is far below batch median {median_ctr:.3%} with below-average "
                   f"quality ranking — kill or rewrite the hook.", clock="fast")

    # Hard read — slow-clock scale path and hard-read diagnostics
    if rung == "hard":
        if conv > 0 and cpa is not None and cpa <= target:
            # A — slow clock confirms economics. R — replication must also confirm.
            if qval is not None and qval <= cfg["bh_alpha"]:
                return out("scale", "confirmed-winner",
                           f"CPA ${cpa:.2f} <= target ${target:.2f}, confirmed by Benjamini-Hochberg "
                           f"(q={qval:.3f} <= {cfg['bh_alpha']}).", clock="slow", q=qval)
            return out("hold", "awaiting-replication",
                       f"Good economics (CPA ${cpa:.2f}) but not yet replication-confirmed "
                       f"(q={qval if qval is None else round(qval, 3)} > {cfg['bh_alpha']}). "
                       f"Probable multiple-comparisons ghost — do not bet budget yet.",
                       clock="slow", q=qval)
        if conv > 0 and cpa is not None and cpa > target:
            if freq >= cfg["frequency_ceiling"]:
                return out("hold", "fatigue-refresh",
                           f"Frequency {freq:.1f} >= {cfg['frequency_ceiling']} and CPA ${cpa:.2f} "
                           f"rising above target — refresh creative / build variants.")
            return out("hold", "cpa-above-target",
                       f"CPA ${cpa:.2f} above target ${target:.2f}; not scale-eligible.")
        if conv == 0 and micro > 0:
            return out("hold", "fix-price-checkout-trust",
                       "Meaningful micro-conversions but weak purchase — fix price, checkout, trust, or offer.")
        return out("hold", "insufficient-signal", "Hard read reached without a decisive signal.")

    # Second-rung diagnostics (2k–5k impressions)
    if imps >= 2000:
        if median_ctr > 0 and ctr > median_ctr and micro == 0:
            return out("hold", "fix-landing-or-offer",
                       "Strong CTR but weak post-click action — the creative works; fix the landing page or offer.")
        if micro > 0 and conv == 0:
            return out("hold", "fix-price-checkout-trust",
                       "Good micro-conversions, weak purchase — fix price, checkout, trust, or offer.")

    # Fatigue at any rung
    if freq >= cfg["frequency_ceiling"] and conv > 0 and cpa is not None and cpa > target:
        return out("hold", "fatigue-refresh",
                   f"Frequency {freq:.1f} rising with CPA ${cpa:.2f} above target — refresh creative.")

    if rung == "below-first":
        return out("hold", "insufficient-signal",
                   f"{int(imps)} impressions — below the first read rung; let it accrue volume.")
    return out("hold", "insufficient-signal", "No CLEAR signal has fired yet.")


def score_batch(creatives, config):
    """Score a batch of per-creative insights rows. Returns {summary, creatives}."""
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in (config or {}).items() if v is not None})
    if not cfg.get("target_cpa"):
        raise ValueError(
            "target_cpa is required; set targets.target_cpa in config or pass --target-cpa. "
            "CLEAR-E and the Read Ladder are spend-relative to your CAC.")
    rows = creatives.get("creatives", creatives) if isinstance(creatives, dict) else creatives
    rows = [dict(r) for r in rows]
    for i, r in enumerate(rows):
        r.setdefault("ad_id", f"row-{i}")

    default_clean = bool(config.get("clean", True)) if isinstance(config, dict) else True

    # Per-creative CTR + batch median CTR.
    ctr_map = {r["ad_id"]: _norm_ctr(r) for r in rows}
    ctr_vals = [ctr_map[r["ad_id"]] for r in rows if float(r.get("impressions", 0) or 0) > 0]
    median_ctr = statistics.median(ctr_vals) if ctr_vals else 0.0

    # CLEAR-R: Benjamini-Hochberg across the batch (each creative vs the rest).
    total_conv = sum(float(r.get("conversions", 0) or 0) for r in rows)
    total_imps = sum(float(r.get("impressions", 0) or 0) for r in rows)
    pvals, ids = [], []
    for r in rows:
        x_i = float(r.get("conversions", 0) or 0)
        n_i = float(r.get("impressions", 0) or 0)
        p = two_proportion_z_pvalue(x_i, n_i, total_conv - x_i, total_imps - n_i)
        pvals.append(p)
        ids.append(r["ad_id"])
    qs = benjamini_hochberg(pvals)
    qmap = dict(zip(ids, qs))

    ctx = {"cfg": cfg, "ctr": ctr_map, "median_ctr": median_ctr,
           "qmap": qmap, "default_clean": default_clean}

    scored = [_score_one(r, ctx) for r in rows]
    counts = {"cut": 0, "hold": 0, "scale": 0}
    for s in scored:
        counts[s["verdict"]] += 1

    return {
        "summary": {
            "k": len(rows),
            "baseline_rate": round(total_conv / total_imps, 5) if total_imps > 0 else 0.0,
            "bh_alpha": cfg["bh_alpha"],
            "autonomy": cfg["autonomy"],
            "target_cpa": cfg["target_cpa"],
            "counts": counts,
        },
        "creatives": scored,
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
            cfg.update(raw.get("hva", {}))
            targets = raw.get("targets", {})
            if targets.get("target_cpa") is not None:
                cfg["target_cpa"] = targets["target_cpa"]
        except (OSError, ValueError) as e:
            print(f"warning: could not read config {path}: {e}", file=sys.stderr)
    for k, v in overrides.items():
        if v is not None:
            cfg[k] = v
    return cfg


def main(argv=None):
    ap = argparse.ArgumentParser(description="HVA Desk scorer — CLEAR + Read Ladder + Benjamini-Hochberg.")
    ap.add_argument("insights", help='insights JSON file, or "-" for stdin')
    ap.add_argument("--config", help="path to .gtm/config.json")
    ap.add_argument("--target-cpa", type=float, dest="target_cpa")
    ap.add_argument("--autonomy", choices=["recommend", "cut-auto", "full-auto"])
    ap.add_argument("--out", help="write decision JSON here (default: stdout)")
    args = ap.parse_args(argv)

    text = sys.stdin.read() if args.insights == "-" else open(args.insights).read()
    insights = json.loads(text)
    cfg = _load_config(args.config, {"target_cpa": args.target_cpa, "autonomy": args.autonomy})

    if cfg.get("target_cpa") is None:
        print("error: target_cpa is required (set targets.target_cpa in config or pass --target-cpa). "
              "CLEAR-E and the hard read are spend-relative to your CAC.", file=sys.stderr)
        return 2

    result = score_batch(insights, cfg)
    out_text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out_text + "\n")
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
