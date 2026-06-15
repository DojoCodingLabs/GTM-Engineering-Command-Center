"""Tests for the HVA Desk scorer (scripts/hva-score.py).

The scorer is the deterministic decision engine behind The Desk (Layer 3).
Each test pins one rule from skills/high-velocity-advertising/rules/the-desk.md,
making "each CLEAR rule a testable condition" literally true.

Run: python3 -m unittest discover scripts/tests
"""
import importlib.util
import os
import unittest

# Load the hyphenated CLI module by path (matches scripts/neuro-score.py naming).
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_PATH = os.path.join(_HERE, "..", "hva-score.py")
_spec = importlib.util.spec_from_file_location("hva_score", _MODULE_PATH)
hva = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hva)


def cfg(**over):
    base = {
        "target_cpa": 20.0,
        "kill_multiple": 3.0,
        "bh_alpha": 0.10,
        "frequency_ceiling": 3.0,
        "hard_read_spend_multiple": 2.0,
        "ctr_margin": 0.6,
        "autonomy": "recommend",
        "scale_bid_cap_multiple": 0.7,
        "max_daily_budget_increase_pct": 20,
    }
    base.update(over)
    return base


def verdict_for(out, ad_id):
    for c in out["creatives"]:
        if c["ad_id"] == ad_id:
            return c
    raise AssertionError(f"{ad_id} not in output")


# ---------------------------------------------------------------------------
# Statistics primitives
# ---------------------------------------------------------------------------
class TestNormalCdf(unittest.TestCase):
    def test_center_is_half(self):
        self.assertAlmostEqual(hva.normal_cdf(0.0), 0.5, places=6)

    def test_upper_quantiles(self):
        self.assertAlmostEqual(hva.normal_cdf(1.6448536), 0.95, places=3)
        self.assertAlmostEqual(hva.normal_cdf(-1.959964), 0.025, places=3)


class TestTwoProportionZ(unittest.TestCase):
    def test_higher_rate_gives_small_pvalue(self):
        # creative far better than the rest -> strong evidence -> tiny one-sided p
        p = hva.two_proportion_z_pvalue(x_i=120, n_i=6000, x_rest=60, n_rest=12000)
        self.assertLess(p, 0.001)

    def test_equal_rates_give_half(self):
        p = hva.two_proportion_z_pvalue(x_i=50, n_i=5000, x_rest=100, n_rest=10000)
        self.assertAlmostEqual(p, 0.5, places=2)

    def test_zero_n_is_no_evidence(self):
        self.assertEqual(hva.two_proportion_z_pvalue(x_i=0, n_i=0, x_rest=10, n_rest=1000), 1.0)


class TestBenjaminiHochberg(unittest.TestCase):
    def test_known_qvalues(self):
        pvals = [0.001, 0.008, 0.039, 0.041, 0.042]
        q = hva.benjamini_hochberg(pvals)
        expected = [0.005, 0.02, 0.042, 0.042, 0.042]
        for got, exp in zip(q, expected):
            self.assertAlmostEqual(got, exp, places=4)

    def test_qvalues_clamped_to_one(self):
        q = hva.benjamini_hochberg([0.9, 0.95])
        self.assertTrue(all(v <= 1.0 for v in q))


# ---------------------------------------------------------------------------
# CLEAR — C: the clean gate
# ---------------------------------------------------------------------------
class TestCleanGate(unittest.TestCase):
    def test_dirty_feed_holds_regardless_of_metrics(self):
        # Would be a screaming cut on economics, but the feed is dirty -> no decision.
        rows = [{"ad_id": "a", "impressions": 9000, "spend": 200.0,
                 "conversions": 0, "micro_conversions": 0, "clean": False}]
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "a")
        self.assertEqual(v["verdict"], "hold")
        self.assertEqual(v["triggering_signal"], "dirty-feed")


# ---------------------------------------------------------------------------
# CLEAR — E: economics kill (fast clock)
# ---------------------------------------------------------------------------
class TestEconomicsKill(unittest.TestCase):
    def test_three_x_cpa_zero_conversions_cuts(self):
        rows = [{"ad_id": "a", "impressions": 4000, "spend": 65.0,  # 3.25x of $20
                 "conversions": 0, "micro_conversions": 2, "clean": True}]
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "a")
        self.assertEqual(v["verdict"], "cut")
        self.assertEqual(v["triggering_signal"], "economics-3x-cpa-zero-conv")
        self.assertEqual(v["clock"], "fast")

    def test_below_three_x_does_not_economics_kill(self):
        rows = [{"ad_id": "a", "impressions": 1500, "spend": 40.0,  # 2x, not yet 3x
                 "conversions": 0, "micro_conversions": 1, "clean": True}]
        out = hva.score_batch(rows, cfg())
        self.assertNotEqual(verdict_for(out, "a")["triggering_signal"],
                            "economics-3x-cpa-zero-conv")


# ---------------------------------------------------------------------------
# CLEAR — L: leading indicators / Diagnostic Table
# ---------------------------------------------------------------------------
class TestLeadingIndicators(unittest.TestCase):
    def test_5k_impressions_zero_action_cuts(self):
        rows = [{"ad_id": "a", "impressions": 5200, "spend": 30.0,  # 1.5x, not economics-kill
                 "conversions": 0, "micro_conversions": 0, "clean": True}]
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "a")
        self.assertEqual(v["verdict"], "cut")
        self.assertEqual(v["triggering_signal"], "5k-impressions-zero-action")

    def test_bad_hook_ctr_cuts(self):
        # Focal has terrible CTR vs batch median and below-average quality ranking.
        rows = [
            {"ad_id": "focal", "impressions": 2500, "spend": 25.0, "ctr": 0.003,
             "conversions": 0, "micro_conversions": 0, "quality_ranking": "below_average",
             "clean": True},
            {"ad_id": "x", "impressions": 2500, "spend": 25.0, "ctr": 0.020,
             "conversions": 1, "micro_conversions": 5, "clean": True},
            {"ad_id": "y", "impressions": 2500, "spend": 25.0, "ctr": 0.022,
             "conversions": 1, "micro_conversions": 6, "clean": True},
        ]
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "focal")
        self.assertEqual(v["verdict"], "cut")
        self.assertEqual(v["triggering_signal"], "bad-hook-ctr")

    def test_strong_ctr_weak_micro_holds_and_blames_funnel(self):
        # Strong CTR, zero micro-conversions -> the creative works, the funnel leaks.
        rows = [
            {"ad_id": "focal", "impressions": 3000, "spend": 30.0, "ctr": 0.030,
             "conversions": 0, "micro_conversions": 0, "quality_ranking": "above_average",
             "clean": True},
            {"ad_id": "x", "impressions": 3000, "spend": 30.0, "ctr": 0.010,
             "conversions": 0, "micro_conversions": 0, "clean": True},
        ]
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "focal")
        self.assertEqual(v["verdict"], "hold")
        self.assertEqual(v["triggering_signal"], "fix-landing-or-offer")

    def test_fatigue_refresh_holds(self):
        rows = [{"ad_id": "a", "impressions": 8000, "spend": 200.0, "frequency": 3.4,
                 "conversions": 5, "micro_conversions": 40, "clean": True}]  # cpa $40 > $20
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "a")
        self.assertEqual(v["verdict"], "hold")
        self.assertEqual(v["triggering_signal"], "fatigue-refresh")


# ---------------------------------------------------------------------------
# CLEAR — A + R: asymmetry (slow clock) and replication (Benjamini-Hochberg)
# ---------------------------------------------------------------------------
class TestScaleAndReplication(unittest.TestCase):
    def test_confirmed_winner_scales(self):
        # Strong, real uplift in a small batch -> survives B-H -> scale.
        rows = [
            {"ad_id": "win", "impressions": 6000, "spend": 1200.0,
             "conversions": 120, "micro_conversions": 300, "clean": True},  # rate .02, cpa $10
            {"ad_id": "b", "impressions": 6000, "spend": 600.0,
             "conversions": 30, "micro_conversions": 80, "clean": True},   # rate .005
            {"ad_id": "c", "impressions": 6000, "spend": 600.0,
             "conversions": 30, "micro_conversions": 80, "clean": True},   # rate .005
        ]
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "win")
        self.assertEqual(v["verdict"], "scale")
        self.assertEqual(v["triggering_signal"], "confirmed-winner")
        self.assertEqual(v["clock"], "slow")
        self.assertIsNotNone(v["q_value"])
        self.assertLessEqual(v["q_value"], cfg()["bh_alpha"])

    def test_multiple_comparisons_ghost_does_not_scale(self):
        # One modest "winner" among 100 with good economics but no real edge:
        # must NOT scale; lands on awaiting-replication.
        rows = [{"ad_id": "ghost", "impressions": 5000, "spend": 650.0,
                 "conversions": 65, "micro_conversions": 120, "clean": True}]  # cpa $10, rate .013
        for i in range(99):
            rows.append({"ad_id": f"n{i}", "impressions": 5000, "spend": 1000.0,
                         "conversions": 50, "micro_conversions": 100, "clean": True})  # rate .010
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "ghost")
        self.assertNotEqual(v["verdict"], "scale")
        self.assertEqual(v["verdict"], "hold")
        self.assertEqual(v["triggering_signal"], "awaiting-replication")


# ---------------------------------------------------------------------------
# Read Ladder rungs
# ---------------------------------------------------------------------------
class TestReadLadder(unittest.TestCase):
    def test_below_first_rung_holds(self):
        rows = [{"ad_id": "a", "impressions": 400, "spend": 6.0,
                 "conversions": 0, "micro_conversions": 0, "clean": True}]
        out = hva.score_batch(rows, cfg())
        v = verdict_for(out, "a")
        self.assertEqual(v["verdict"], "hold")
        self.assertEqual(v["rung"], "below-first")

    def test_first_rung_boundary(self):
        on = hva.score_batch([{"ad_id": "a", "impressions": 1000, "spend": 5.0,
                               "conversions": 0, "micro_conversions": 0, "clean": True}], cfg())
        below = hva.score_batch([{"ad_id": "a", "impressions": 999, "spend": 5.0,
                                  "conversions": 0, "micro_conversions": 0, "clean": True}], cfg())
        self.assertEqual(verdict_for(on, "a")["rung"], "first")
        self.assertEqual(verdict_for(below, "a")["rung"], "below-first")

    def test_second_rung_boundary(self):
        out = hva.score_batch([{"ad_id": "a", "impressions": 2000, "spend": 10.0,
                                "conversions": 0, "micro_conversions": 0, "clean": True}], cfg())
        self.assertEqual(verdict_for(out, "a")["rung"], "second")

    def test_spend_based_hard_rung(self):
        # Low impressions but >= 2x target CPA spent -> hard read via the spend trigger.
        out = hva.score_batch([{"ad_id": "a", "impressions": 1200, "spend": 45.0,  # 2.25x of $20
                                "conversions": 0, "micro_conversions": 0, "clean": True}], cfg())
        self.assertEqual(verdict_for(out, "a")["rung"], "hard")

    def test_just_below_hard_spend_stays_first(self):
        # 1.75x target CPA at first-rung impressions must NOT escalate to hard (contract: 2x).
        out = hva.score_batch([{"ad_id": "a", "impressions": 1200, "spend": 35.0,  # 1.75x of $20
                                "conversions": 0, "micro_conversions": 0, "clean": True}], cfg())
        self.assertEqual(verdict_for(out, "a")["rung"], "first")


class TestConfigGuards(unittest.TestCase):
    def test_score_batch_requires_target_cpa(self):
        rows = [{"ad_id": "a", "impressions": 100, "spend": 1.0, "clean": True}]
        with self.assertRaises(ValueError):
            hva.score_batch(rows, {})
        with self.assertRaises(ValueError):
            hva.score_batch(rows, {"target_cpa": None})


# ---------------------------------------------------------------------------
# Autonomy action resolution — the single place autonomy is applied
# ---------------------------------------------------------------------------
class TestAutonomyResolution(unittest.TestCase):
    def _cut_row(self):
        return [{"ad_id": "a", "impressions": 4000, "spend": 65.0,
                 "conversions": 0, "micro_conversions": 0, "clean": True}]

    def test_cut_recommend_mode_recommends_pause(self):
        out = hva.score_batch(self._cut_row(), cfg(autonomy="recommend"))
        self.assertEqual(verdict_for(out, "a")["autonomy_action"], "recommend-pause")

    def test_cut_auto_mode_auto_pauses(self):
        out = hva.score_batch(self._cut_row(), cfg(autonomy="cut-auto"))
        self.assertEqual(verdict_for(out, "a")["autonomy_action"], "auto-pause")

    def test_scale_full_auto_auto_scales(self):
        rows = [
            {"ad_id": "win", "impressions": 6000, "spend": 1200.0,
             "conversions": 120, "micro_conversions": 300, "clean": True},
            {"ad_id": "b", "impressions": 6000, "spend": 600.0,
             "conversions": 30, "micro_conversions": 80, "clean": True},
            {"ad_id": "c", "impressions": 6000, "spend": 600.0,
             "conversions": 30, "micro_conversions": 80, "clean": True},
        ]
        out = hva.score_batch(rows, cfg(autonomy="full-auto"))
        self.assertEqual(verdict_for(out, "win")["autonomy_action"], "auto-scale")

    def test_scale_cut_auto_only_recommends_scale(self):
        rows = [
            {"ad_id": "win", "impressions": 6000, "spend": 1200.0,
             "conversions": 120, "micro_conversions": 300, "clean": True},
            {"ad_id": "b", "impressions": 6000, "spend": 600.0,
             "conversions": 30, "micro_conversions": 80, "clean": True},
            {"ad_id": "c", "impressions": 6000, "spend": 600.0,
             "conversions": 30, "micro_conversions": 80, "clean": True},
        ]
        out = hva.score_batch(rows, cfg(autonomy="cut-auto"))
        self.assertEqual(verdict_for(out, "win")["autonomy_action"], "recommend-scale")


# ---------------------------------------------------------------------------
# Batch summary
# ---------------------------------------------------------------------------
class TestSummary(unittest.TestCase):
    def test_summary_counts_and_autonomy(self):
        rows = [{"ad_id": "a", "impressions": 4000, "spend": 65.0,
                 "conversions": 0, "micro_conversions": 0, "clean": True}]
        out = hva.score_batch(rows, cfg(autonomy="cut-auto"))
        self.assertEqual(out["summary"]["autonomy"], "cut-auto")
        self.assertEqual(out["summary"]["counts"]["cut"], 1)
        self.assertEqual(out["summary"]["k"], 1)


if __name__ == "__main__":
    unittest.main()
