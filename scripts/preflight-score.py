#!/usr/bin/env python3
"""Pre-Flight gate scorer — the deterministic blend of the unified two-stage pre-flight.

Combines neuro-testing (Tribe v2: attention/emotion/memory) and SDV (purchase intent /
price / objections) into ONE DEPLOY/TEST/ITERATE/SKIP verdict per ad creative, the way
/gtm-validate runs it. This file is stdlib-only and MIT and **never imports neuro code** —
the license firewall is structural: it reads two JSON score artifacts off disk (the SDV
scorer's output and a normalized neuro composite map) and composes their OUTPUTS only.
When the neuro artifact is absent (Tribe v2 not installed, or CC-BY-NC disallowed), the
gate degrades to an SDV-only verdict.

Contract: skills/synthetic-demand/rules/preflight-matrix.md
Tests:    scripts/tests/test_preflight_score.py

The two load-bearing guardrails (SDV plan §2/§3):

  §2  Neuro is consumed as a within-batch RANK only. neuro-score.py min-max normalizes its
      composite ACROSS the batch and returns a RAW value for a single creative, so a neuro
      "70" is not a property of the creative — it is an artifact of batch composition.
      Therefore: a creative's band comes from its rank among the batch; with batch < 2 neuro
      contributes NOTHING (caveat "neuro-absolute-invalid").

  §3  The blend is a decision MATRIX, not a weighted average. Two separately-validated models
      measuring different constructs have no validated linear combination, so there is no
      blended 0-100 crossing a DEPLOY line. Neuro can only make the SDV verdict MORE
      conservative (downgrade) or set the lever (what to fix) — it can never upgrade it.

CLI:
    preflight-score.py BLEND.json [--config .gtm/config.json] [--autonomy ...] [--out OUT.json]
    BLEND.json = {"sdv": <sdv-score output>, "neuro": {"<id>": composite, ...}}  (neuro optional)
"""
import argparse
import json
import math
import sys

_ORDER = ("SKIP", "ITERATE", "TEST", "DEPLOY")


def ranks_from_composites(neuro_map):
    """Map {id: composite} -> {id: 1-based rank} (higher composite = better = rank 1)."""
    ordered = sorted(neuro_map, key=lambda k: neuro_map[k], reverse=True)
    return {vid: i + 1 for i, vid in enumerate(ordered)}


def neuro_band(rank, n):
    """Within-batch tertile band from a 1-based rank. None when the batch is too small (§2)."""
    if n < 2:
        return None
    pos = (rank - 1) / (n - 1)  # 0.0 = best, 1.0 = worst
    if pos <= 1.0 / 3.0:
        return "strong"
    if pos >= 2.0 / 3.0:
        return "weak"
    return "mid"


def blend(sdv_verdict, band):
    """The decision MATRIX (§3). Returns (verdict, lever).

    Lever = what to fix: none · visual (creative execution) · offer (offer/copy/proof) · both.
    Invariant: neuro never UPGRADES the SDV verdict — it only holds, downgrades, or labels.
    """
    if band is None:  # SDV-only (no neuro stage)
        return sdv_verdict, ("offer" if sdv_verdict in ("TEST", "ITERATE") else "none")
    weak = band == "weak"
    if sdv_verdict == "DEPLOY":
        # strong demand but weak attention -> strengthen the visual before scaling
        return ("ITERATE", "visual") if weak else ("DEPLOY", "none")
    if sdv_verdict == "TEST":
        return ("ITERATE", "both") if weak else ("TEST", "offer")
    if sdv_verdict == "ITERATE":
        # grabs attention but demand is weak -> fix the OFFER, not the visual
        return ("ITERATE", "both") if weak else ("ITERATE", "offer")
    return ("SKIP", "none")  # demand is dead; attention cannot rescue it


def resolve_action(verdict, lever, autonomy):
    """The ONLY place autonomy is applied. Deploying spends money -> always human-gated.

    Extends hva-score.py's resolve_action(verdict, autonomy) with a `lever` arg (a new
    function, not a copy); the reused part is the autonomy semantics.
    """
    if verdict == "DEPLOY":
        return "recommend-deploy"
    if verdict == "SKIP":
        return "auto-archive" if autonomy in ("cut-auto", "full-auto") else "recommend-archive"
    return "hold"


def preflight(sdv_result, neuro=None, config=None):
    """Blend an SDV score artifact with an optional neuro composite map into one verdict set."""
    cfg = config or {}
    autonomy = cfg.get("autonomy") or sdv_result.get("summary", {}).get("autonomy", "recommend")
    variants = sdv_result["variants"]
    caveats = []

    band_of = {}
    if not neuro:
        caveats.append("neuro stage skipped (model artifact absent) — SDV-only verdict")
    elif len(neuro) < 2:
        caveats.append("neuro-absolute-invalid: a single creative's neuro composite is raw and "
                       "batch-relative, so it is uninterpretable — SDV-only verdict")
    else:
        n = len(neuro)
        ranks = ranks_from_composites(neuro)
        band_of = {vid: neuro_band(ranks[vid], n) for vid in neuro}

    creatives = []
    for v in variants:
        vid = v["id"]
        band = band_of.get(vid)
        verdict, lever = blend(v["verdict"], band)
        creatives.append({
            "id": vid,
            "sdv_verdict": v["verdict"],
            "neuro_band": band,
            "verdict": verdict,
            "lever": lever,
            "action": resolve_action(verdict, lever, autonomy),
        })

    counts = {k: 0 for k in _ORDER}
    for c in creatives:
        counts[c["verdict"]] += 1
    return {
        "summary": {
            "autonomy": autonomy,
            "neuro_stage": "active" if band_of else "skipped",
            "counts": counts,
        },
        "caveats": caveats,
        "creatives": creatives,
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
        description="Pre-Flight gate scorer — blends neuro (rank) + SDV (verdict) into one decision.")
    ap.add_argument("blend", help='blend JSON {"sdv": <sdv output>, "neuro": {id: composite}}, or "-"')
    ap.add_argument("--config", help="path to .gtm/config.json")
    ap.add_argument("--autonomy", choices=["recommend", "cut-auto", "full-auto"])
    ap.add_argument("--out", help="write decision JSON here (default: stdout)")
    args = ap.parse_args(argv)

    text = sys.stdin.read() if args.blend == "-" else open(args.blend).read()
    payload = json.loads(text)
    if "sdv" not in payload:
        print("error: blend input must contain an 'sdv' score artifact", file=sys.stderr)
        return 2
    cfg = _load_config(args.config, {"autonomy": args.autonomy})

    result = preflight(payload["sdv"], payload.get("neuro"), cfg)
    out_text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out_text + "\n")
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
