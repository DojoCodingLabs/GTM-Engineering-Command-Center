"""Tests for the unified two-stage Pre-Flight gate scorer (scripts/preflight-score.py).

The pre-flight gate BLENDS neuro-testing (Tribe v2: attention/memory — CC-BY-NC) and SDV
(intent/price — MIT) into one DEPLOY/TEST/ITERATE/SKIP verdict. This scorer is stdlib-only,
MIT, and NEVER imports neuro code — it composes two JSON score artifacts off disk.

The guardrails it must enforce (SDV plan §2/§3):
  - neuro is consumed as a within-batch RANK only, never an absolute composite;
  - neuro contributes nothing when the batch < 2 (its absolute is raw/uninterpretable);
  - the blend is a decision MATRIX, not a weighted average — neuro can only make a verdict
    MORE conservative (downgrade) or annotate the lever, never mint/upgrade a DEPLOY.

Run: python3 -m unittest discover scripts/tests
"""
import importlib.util
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_PATH = os.path.join(_HERE, "..", "preflight-score.py")
_spec = importlib.util.spec_from_file_location("preflight_score", _MODULE_PATH)
pf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pf)

_ORDER = ("SKIP", "ITERATE", "TEST", "DEPLOY")


class TestNeuroBand(unittest.TestCase):
    def test_tertiles_for_batch_of_six(self):
        self.assertEqual(pf.neuro_band(1, 6), "strong")
        self.assertEqual(pf.neuro_band(2, 6), "strong")
        self.assertEqual(pf.neuro_band(3, 6), "mid")
        self.assertEqual(pf.neuro_band(5, 6), "weak")
        self.assertEqual(pf.neuro_band(6, 6), "weak")

    def test_single_creative_neuro_is_invalid(self):
        # §2: a lone creative's neuro composite is raw/un-normalized -> uninterpretable
        self.assertIsNone(pf.neuro_band(1, 1))

    def test_ranks_from_composites(self):
        ranks = pf.ranks_from_composites({"V1": 80, "V2": 50, "V3": 90})
        self.assertEqual(ranks, {"V3": 1, "V1": 2, "V2": 3})


class TestBlendMatrix(unittest.TestCase):
    def test_strong_neuro_keeps_a_deploy(self):
        self.assertEqual(pf.blend("DEPLOY", "strong"), ("DEPLOY", "none"))

    def test_weak_neuro_downgrades_deploy_and_blames_the_visual(self):
        # demand is strong but attention lags -> fix the creative execution, don't scale yet
        self.assertEqual(pf.blend("DEPLOY", "weak"), ("ITERATE", "visual"))

    def test_strong_neuro_low_demand_blames_the_offer(self):
        # grabs attention but no demand -> ITERATE the OFFER, not the visual
        self.assertEqual(pf.blend("ITERATE", "strong"), ("ITERATE", "offer"))

    def test_test_with_weak_neuro_drops_to_iterate(self):
        self.assertEqual(pf.blend("TEST", "weak"), ("ITERATE", "both"))

    def test_neuro_never_upgrades_the_verdict(self):
        for v in _ORDER:
            for band in ("strong", "mid", "weak", None):
                out, _ = pf.blend(v, band)
                self.assertLessEqual(_ORDER.index(out), _ORDER.index(v),
                                     f"neuro upgraded {v} ({band}) -> {out}")

    def test_sdv_only_path_keeps_sdv_verdict(self):
        self.assertEqual(pf.blend("DEPLOY", None), ("DEPLOY", "none"))
        self.assertEqual(pf.blend("ITERATE", None), ("ITERATE", "offer"))


class TestResolveAction(unittest.TestCase):
    def test_deploy_never_auto(self):
        self.assertEqual(pf.resolve_action("DEPLOY", "none", "full-auto"), "recommend-deploy")

    def test_skip_auto_archives_at_higher_autonomy(self):
        self.assertEqual(pf.resolve_action("SKIP", "none", "cut-auto"), "auto-archive")
        self.assertEqual(pf.resolve_action("SKIP", "none", "recommend"), "recommend-archive")

    def test_iterate_holds(self):
        self.assertEqual(pf.resolve_action("ITERATE", "visual", "full-auto"), "hold")


class TestPreflightIntegration(unittest.TestCase):
    def _sdv(self, verdicts):
        return {"summary": {"autonomy": "recommend"},
                "variants": [{"id": vid, "verdict": v} for vid, v in verdicts.items()]}

    def test_sdv_only_when_no_neuro(self):
        out = pf.preflight(self._sdv({"V1": "DEPLOY", "V2": "SKIP"}), neuro=None)
        self.assertTrue(any("neuro stage skipped" in c.lower() for c in out["caveats"]))
        v1 = next(c for c in out["creatives"] if c["id"] == "V1")
        self.assertEqual(v1["verdict"], "DEPLOY")

    def test_single_creative_neuro_is_ignored_with_caveat(self):
        out = pf.preflight(self._sdv({"V1": "DEPLOY"}), neuro={"V1": 80.0})
        self.assertTrue(any("neuro-absolute-invalid" in c for c in out["caveats"]))
        self.assertEqual(out["creatives"][0]["verdict"], "DEPLOY")  # SDV-only, unchanged

    def test_blend_depends_on_rank_not_absolute_composite(self):
        # Same creative, same composite 80, but different batch composition -> different band.
        sdv = self._sdv({"A": "DEPLOY", "B": "DEPLOY", "C": "DEPLOY"})
        # batch 1: A=80 is the LOWEST -> weak -> A downgraded to ITERATE/visual
        low = pf.preflight(sdv, neuro={"A": 80, "B": 95, "C": 99})
        a_low = next(c for c in low["creatives"] if c["id"] == "A")
        # batch 2: A=80 is the HIGHEST -> strong -> A keeps DEPLOY
        high = pf.preflight(sdv, neuro={"A": 80, "B": 40, "C": 30})
        a_high = next(c for c in high["creatives"] if c["id"] == "A")
        self.assertEqual(a_low["verdict"], "ITERATE")
        self.assertEqual(a_high["verdict"], "DEPLOY")

    def test_high_neuro_low_demand_iterates_the_offer(self):
        sdv = self._sdv({"A": "ITERATE", "B": "SKIP", "C": "SKIP"})
        out = pf.preflight(sdv, neuro={"A": 99, "B": 50, "C": 40})
        a = next(c for c in out["creatives"] if c["id"] == "A")
        self.assertEqual((a["verdict"], a["lever"]), ("ITERATE", "offer"))


if __name__ == "__main__":
    unittest.main()
