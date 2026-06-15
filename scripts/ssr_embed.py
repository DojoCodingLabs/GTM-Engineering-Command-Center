#!/usr/bin/env python3
"""ssr_embed.py — Semantic Similarity Rating (SSR) mapping helper for GTM Synthetic Demand Validation.

OPTIONAL. This is the ONLY piece of SDV that touches external infrastructure. It is auto-invoked
by /gtm-validate (via the demand-forecaster agent) *only* when an embeddings provider is detected.
When it is absent or fails, the prediction layer falls back to prompt-only FLR
(see skills/synthetic-demand/rules/elicitation-methods.md) — nothing here is required for SDV to work.
Like sdv-score.py, this file is stdlib-only and MIT, and carries NO dependency on Tribe v2 (CC-BY-NC).

What it does (per Maier et al. 2025, eq. 7-9):
  Given a synthetic respondent's free-text reaction and one or more anchor sets (5 statements each,
  one per Likert point), it embeds them, computes cosine similarity, subtracts the per-set minimum
  similarity (the epsilon-floor that controls variance), applies an optional temperature, normalizes
  to a probability mass function over the 1-5 Likert scale, and averages across anchor sets.

Dependencies: Python 3 standard library only (no numpy, no SDK). Calls an OpenAI-compatible
/v1/embeddings endpoint via urllib.

Configuration (environment):
  OPENAI_API_KEY            API key (or SDV_EMBEDDINGS_API_KEY)
  SDV_EMBEDDINGS_MODEL      model id (default: text-embedding-3-small)
  SDV_EMBEDDINGS_BASE_URL   base url (default: https://api.openai.com/v1)

Usage:
  echo '{"reaction":"...", "anchor_sets":[["...","...","...","...","..."]]}' | python3 ssr_embed.py

Input JSON (stdin):
  {
    "reaction": "I'd probably try it if it's cheap, but $500 feels steep.",
    "anchor_sets": [["definitely not","probably not","unsure","probably yes","definitely yes"], ...],
    "epsilon": 0.0,          # optional, default 0.0
    "temperature": 1.0,      # optional, default 1.0 (paper's rule-of-thumb)
    "model": "text-embedding-3-small"  # optional override
  }
  (anchor_sets may also be a single flat list of 5 statements.)

Output JSON (stdout):
  success:  {"ok": true,  "pmf": [p1,p2,p3,p4,p5], "n_sets": N, "model": "..."}
  failure:  {"ok": false, "error": "...", "fallback": "FLR"}   (and non-zero exit code)

Exit codes: 0 success · 1 no provider / call failed (fall back to FLR) · 2 bad input.
"""

import json
import math
import os
import sys
import urllib.error
import urllib.request


def _env(*names, default=None):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


def embed(texts, model, base_url, api_key):
    """Return a list of embedding vectors for `texts` via an OpenAI-compatible endpoint."""
    url = base_url.rstrip("/") + "/embeddings"
    payload = json.dumps({"input": texts, "model": model}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    # Preserve input order (OpenAI returns an "index" per item).
    items = sorted(data["data"], key=lambda d: d.get("index", 0))
    return [it["embedding"] for it in items]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def pmf_for_set(reaction_vec, anchor_vecs, epsilon, temperature):
    """One anchor set (5 vectors) -> a length-5 pmf."""
    sims = [cosine(reaction_vec, av) for av in anchor_vecs]
    m = min(sims)
    raw = [max(s - m, 0.0) + epsilon for s in sims]  # eq. 8: subtract min similarity, add epsilon
    total = sum(raw)
    if total <= 0:
        p = [1.0 / len(raw)] * len(raw)
    else:
        p = [x / total for x in raw]
    if temperature and temperature != 1.0:  # eq. 9: p(r,T) ∝ p(r)^(1/T)
        powered = [pi ** (1.0 / temperature) for pi in p]
        s = sum(powered)
        p = [pi / s for pi in powered] if s > 0 else p
    return p


def main():
    try:
        cfg = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": "invalid JSON input: %s" % e, "fallback": "FLR"}))
        return 2

    reaction = cfg.get("reaction")
    anchor_sets = cfg.get("anchor_sets")
    if not reaction or not anchor_sets:
        print(json.dumps({"ok": False, "error": "missing 'reaction' or 'anchor_sets'", "fallback": "FLR"}))
        return 2

    # Allow a single flat 5-statement list as shorthand for one set.
    if anchor_sets and isinstance(anchor_sets[0], str):
        anchor_sets = [anchor_sets]
    if any(len(s) != 5 for s in anchor_sets):
        print(json.dumps({"ok": False, "error": "each anchor set must have exactly 5 statements", "fallback": "FLR"}))
        return 2

    api_key = _env("OPENAI_API_KEY", "SDV_EMBEDDINGS_API_KEY")
    if not api_key:
        print(json.dumps({"ok": False, "error": "no embeddings provider configured (set OPENAI_API_KEY)", "fallback": "FLR"}))
        return 1

    model = cfg.get("model") or _env("SDV_EMBEDDINGS_MODEL", default="text-embedding-3-small")
    base_url = _env("SDV_EMBEDDINGS_BASE_URL", default="https://api.openai.com/v1")
    epsilon = float(cfg.get("epsilon", 0.0))
    temperature = float(cfg.get("temperature", 1.0))

    # Embed the reaction once + every anchor across all sets in a single batched call.
    flat_anchors = [a for s in anchor_sets for a in s]
    try:
        vecs = embed([reaction] + flat_anchors, model, base_url, api_key)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
        print(json.dumps({"ok": False, "error": "embeddings call failed: %s" % e, "fallback": "FLR"}))
        return 1

    reaction_vec = vecs[0]
    anchor_vecs = vecs[1:]

    # Average the per-set pmfs.
    acc = [0.0] * 5
    idx = 0
    for s in anchor_sets:
        set_vecs = anchor_vecs[idx:idx + 5]
        idx += 5
        p = pmf_for_set(reaction_vec, set_vecs, epsilon, temperature)
        acc = [a + pi for a, pi in zip(acc, p)]
    n = len(anchor_sets)
    pmf = [round(a / n, 6) for a in acc]

    print(json.dumps({"ok": True, "pmf": pmf, "n_sets": n, "model": model}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
