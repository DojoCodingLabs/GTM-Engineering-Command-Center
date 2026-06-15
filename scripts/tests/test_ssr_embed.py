"""Tests for the optional SSR mapping helper (scripts/ssr_embed.py).

ssr_embed.py is the ONLY part of SDV that touches external infra. These tests pin its
pure math (cosine, eq.8/9 pmf) and — most importantly — its graceful-fallback contract:
when no embeddings provider is configured or the call fails, it must emit
{"ok": false, "fallback": "FLR"} and a non-zero exit code, NEVER raise.

Run: python3 -m unittest discover scripts/tests
"""
import importlib.util
import io
import json
import math
import os
import unittest
from contextlib import redirect_stdout

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_PATH = os.path.join(_HERE, "..", "ssr_embed.py")
_spec = importlib.util.spec_from_file_location("ssr_embed", _MODULE_PATH)
ssr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ssr)


def run_main(stdin_text, env=None):
    """Run main() with a given stdin and env, capturing (exit_code, parsed_json)."""
    import sys
    old_stdin, old_environ = sys.stdin, dict(os.environ)
    # Isolate the embeddings env so a real local key never leaks into the test.
    for k in ("OPENAI_API_KEY", "SDV_EMBEDDINGS_API_KEY",
              "SDV_EMBEDDINGS_MODEL", "SDV_EMBEDDINGS_BASE_URL"):
        os.environ.pop(k, None)
    if env:
        os.environ.update(env)
    sys.stdin = io.StringIO(stdin_text)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            code = ssr.main()
    finally:
        sys.stdin = old_stdin
        os.environ.clear()
        os.environ.update(old_environ)
    return code, json.loads(buf.getvalue())


class TestCosine(unittest.TestCase):
    def test_identical_vectors_is_one(self):
        self.assertAlmostEqual(ssr.cosine([1, 2, 3], [1, 2, 3]), 1.0, places=6)

    def test_orthogonal_is_zero(self):
        self.assertAlmostEqual(ssr.cosine([1, 0], [0, 1]), 0.0, places=6)

    def test_zero_vector_is_zero(self):
        self.assertEqual(ssr.cosine([0, 0], [1, 1]), 0.0)


class TestPmfForSet(unittest.TestCase):
    def test_pmf_sums_to_one_and_peaks_at_most_similar(self):
        # reaction is identical to anchor index 3 (point 4) -> that point gets the mass
        reaction = [0, 0, 0, 1]
        anchors = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0.5, 0.5]]
        p = ssr.pmf_for_set(reaction, anchors, epsilon=0.0, temperature=1.0)
        self.assertAlmostEqual(sum(p), 1.0, places=6)
        self.assertEqual(p.index(max(p)), 3)

    def test_temperature_changes_shape(self):
        reaction = [0.9, 0.1]
        anchors = [[1, 0], [0.8, 0.2], [0.6, 0.4], [0.4, 0.6], [0, 1]]
        flat = ssr.pmf_for_set(reaction, anchors, 0.0, 1.0)
        sharp = ssr.pmf_for_set(reaction, anchors, 0.0, 0.5)  # T<1 sharpens
        self.assertAlmostEqual(sum(sharp), 1.0, places=6)
        self.assertNotEqual([round(x, 4) for x in flat], [round(x, 4) for x in sharp])


class TestFallbackContract(unittest.TestCase):
    VALID = json.dumps({
        "reaction": "Looks useful but $500 is steep.",
        "anchor_sets": [["no", "probably not", "unsure", "probably", "yes"]],
    })

    def test_no_provider_falls_back_to_flr_exit_1(self):
        code, out = run_main(self.VALID, env=None)
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])
        self.assertEqual(out["fallback"], "FLR")

    def test_bad_json_is_exit_2(self):
        code, out = run_main("{not json", env={"OPENAI_API_KEY": "x"})
        self.assertEqual(code, 2)
        self.assertEqual(out["fallback"], "FLR")

    def test_wrong_anchor_length_is_exit_2(self):
        bad = json.dumps({"reaction": "hi", "anchor_sets": [["a", "b", "c"]]})
        code, out = run_main(bad, env={"OPENAI_API_KEY": "x"})
        self.assertEqual(code, 2)

    def test_missing_fields_is_exit_2(self):
        code, out = run_main(json.dumps({"reaction": "hi"}), env={"OPENAI_API_KEY": "x"})
        self.assertEqual(code, 2)

    def test_embeddings_failure_falls_back(self):
        # Provider configured but the call raises -> still a clean FLR fallback, exit 1.
        import urllib.error

        def boom(*a, **k):
            raise urllib.error.URLError("network down")

        orig = ssr.embed
        ssr.embed = boom
        try:
            code, out = run_main(self.VALID, env={"OPENAI_API_KEY": "test-key"})
        finally:
            ssr.embed = orig
        self.assertEqual(code, 1)
        self.assertEqual(out["fallback"], "FLR")


if __name__ == "__main__":
    unittest.main()
