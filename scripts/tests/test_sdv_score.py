"""Tests for the SDV scorer (scripts/sdv-score.py).

The scorer is the deterministic decision engine behind Synthetic Demand Validation.
Each test pins one rule from skills/synthetic-demand/ — making the scientific-integrity
guardrails (§1–§10 of the SDV plan) literally testable conditions, the same way
test_hva_score.py pins each CLEAR rule.

Governing law (skills/synthetic-demand/SKILL.md):
    "Rank, don't score. Never ask a synthetic respondent for a number."

Run: python3 -m unittest discover scripts/tests
"""
import importlib.util
import math
import os
import unittest

# Load the hyphenated CLI module by path (matches scripts/hva-score.py / neuro-score.py naming).
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_PATH = os.path.join(_HERE, "..", "sdv-score.py")
_spec = importlib.util.spec_from_file_location("sdv_score", _MODULE_PATH)
sdv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sdv)


def good_elicitation(pmf, method="FLR"):
    """A construct reading that respects the two-step free-text protocol (§4)."""
    return {
        "pmf": pmf,
        "elicitation_method": method,
        "react_call_saw_scale": False,
        "map_call_separate": True,
        "samples": 3,
    }


# ---------------------------------------------------------------------------
# pmf primitives + the demand_score formula
# ---------------------------------------------------------------------------
class TestPmfPrimitives(unittest.TestCase):
    def test_pmf_mean_on_1_to_5_scale(self):
        # all mass on point 5 -> mean 5; uniform -> mean 3
        self.assertAlmostEqual(sdv.pmf_mean([0, 0, 0, 0, 1]), 5.0, places=6)
        self.assertAlmostEqual(sdv.pmf_mean([0.2] * 5), 3.0, places=6)

    def test_validate_pmf_rejects_bad_length_and_sum(self):
        with self.assertRaises(ValueError):
            sdv.validate_pmf([0.5, 0.5])          # wrong length
        with self.assertRaises(ValueError):
            sdv.validate_pmf([0.3, 0.3, 0.3, 0.3, 0.3])  # sums to 1.5
        with self.assertRaises(ValueError):
            sdv.validate_pmf([-0.1, 0.2, 0.4, 0.3, 0.2])  # negative mass
        sdv.validate_pmf([0.05, 0.35, 0.45, 0.12, 0.03])  # valid -> no raise

    def test_is_degenerate_pmf_flags_one_hot(self):
        # one-hot / near-delta = the signature of "asked for a number" (§4)
        self.assertTrue(sdv.is_degenerate_pmf([0, 0, 1, 0, 0]))
        self.assertTrue(sdv.is_degenerate_pmf([0.0, 0.0, 0.98, 0.02, 0.0]))
        self.assertFalse(sdv.is_degenerate_pmf([0.05, 0.35, 0.45, 0.12, 0.03]))


class TestDemandScore(unittest.TestCase):
    def test_known_answer_with_renormalized_subset(self):
        # only two constructs measured -> weights renormalize over the subset
        # w_pi = .35/.50 = .70 ; w_appeal = .15/.50 = .30
        # 100*(.70*(4-1)/4 + .30*(3-1)/4) = 100*(.525 + .15) = 67.5
        means = {"purchase_intent": 4.0, "appeal": 3.0}
        score = sdv.demand_score(means, sdv.DEFAULT_WEIGHTS)
        self.assertAlmostEqual(score, 67.5, places=4)

    def test_wtp_is_excluded_from_the_blend(self):
        # willingness_to_pay is a price, not a 0-1 construct (§ construct-battery)
        means = {"purchase_intent": 4.0, "willingness_to_pay": 499.0}
        score = sdv.demand_score(means, sdv.DEFAULT_WEIGHTS)
        # only purchase_intent contributes -> 100*(1.0*(4-1)/4) = 75.0
        self.assertAlmostEqual(score, 75.0, places=4)

    def test_full_uniform_battery_midpoint(self):
        means = {k: 3.0 for k in
                 ["purchase_intent", "appeal", "comprehension",
                  "differentiation", "believability", "price_fairness", "share_intent"]}
        self.assertAlmostEqual(sdv.demand_score(means, sdv.DEFAULT_WEIGHTS), 50.0, places=4)


# ---------------------------------------------------------------------------
# §4 — FLR provenance must be machine-checkable, not prose
# ---------------------------------------------------------------------------
class TestElicitationProvenance(unittest.TestCase):
    def test_valid_flr_record_passes(self):
        sdv.validate_elicitation(good_elicitation([0.05, 0.35, 0.45, 0.12, 0.03]))

    def test_dlr_as_primary_is_rejected(self):
        rec = good_elicitation([0.05, 0.35, 0.45, 0.12, 0.03], method="DLR")
        with self.assertRaises(ValueError):
            sdv.validate_elicitation(rec)

    def test_one_hot_pmf_is_rejected_as_number_elicited(self):
        with self.assertRaises(ValueError):
            sdv.validate_elicitation(good_elicitation([0, 0, 1, 0, 0]))

    def test_missing_two_step_flags_rejected(self):
        rec = good_elicitation([0.05, 0.35, 0.45, 0.12, 0.03])
        rec["react_call_saw_scale"] = True   # the free-text call saw the scale -> invalid
        with self.assertRaises(ValueError):
            sdv.validate_elicitation(rec)
        rec2 = good_elicitation([0.05, 0.35, 0.45, 0.12, 0.03])
        rec2["map_call_separate"] = False
        with self.assertRaises(ValueError):
            sdv.validate_elicitation(rec2)


# ---------------------------------------------------------------------------
# Comparative scaling — the headline signal
# ---------------------------------------------------------------------------
class TestComparativeScaling(unittest.TestCase):
    def test_best_worst_share_known_answer(self):
        shares = sdv.best_worst_share(best={"V1": 3, "V2": 1},
                                      worst={"V1": 0, "V2": 2},
                                      appeared={"V1": 4, "V2": 4})
        self.assertAlmostEqual(shares["V1"], 0.75, places=6)
        self.assertAlmostEqual(shares["V2"], -0.25, places=6)

    def test_win_rate_known_answer(self):
        wr = sdv.win_rate(wins={"V1": 3, "V2": 1}, participated={"V1": 4, "V2": 4})
        self.assertAlmostEqual(wr["V1"], 0.75, places=6)
        self.assertAlmostEqual(wr["V2"], 0.25, places=6)

    def test_kendall_tau_identical_and_reversed(self):
        self.assertAlmostEqual(sdv.kendall_tau(["a", "b", "c"], ["a", "b", "c"]), 1.0, places=6)
        self.assertAlmostEqual(sdv.kendall_tau(["a", "b", "c"], ["c", "b", "a"]), -1.0, places=6)


# ---------------------------------------------------------------------------
# §6 — rank_stability must be a real estimate, not a 1-resample coin flip
# ---------------------------------------------------------------------------
class TestRankStability(unittest.TestCase):
    def test_one_resample_is_indeterminate_not_stable(self):
        out = sdv.rank_stability([["V1", "V2", "V3"]])
        self.assertEqual(out["status"], "indeterminate")

    def test_fewer_than_five_is_indeterminate(self):
        out = sdv.rank_stability([["V1", "V2"]] * 4)
        self.assertEqual(out["status"], "indeterminate")

    def test_five_consistent_resamples_are_stable(self):
        out = sdv.rank_stability([["V1", "V2", "V3"]] * 5)
        self.assertEqual(out["status"], "stable")
        self.assertAlmostEqual(out["top_hold_fraction"], 1.0, places=6)

    def test_flipping_top_is_unstable(self):
        rankings = [["V1", "V2"], ["V2", "V1"], ["V1", "V2"], ["V2", "V1"], ["V1", "V2"]]
        out = sdv.rank_stability(rankings)
        self.assertEqual(out["status"], "unstable")


# ---------------------------------------------------------------------------
# §1 — verdict is comparative-FIRST; absolute can only make it more conservative
# §2/§5 — no absolute go/no-go below F3
# ---------------------------------------------------------------------------
class TestVerdictComparativeFirst(unittest.TestCase):
    def test_f0_stable_winner_high_absolute_cannot_deploy(self):
        v = sdv.get_verdict(rank=1, rank_stability="stable",
                            demand_score_relative=85, tier="F0")
        self.assertNotEqual(v, "DEPLOY")
        self.assertEqual(v, "TEST")

    def test_f3_calibrated_stable_winner_high_absolute_deploys(self):
        v = sdv.get_verdict(rank=1, rank_stability="stable",
                            demand_score_relative=85, tier="F3", calibration_valid=True)
        self.assertEqual(v, "DEPLOY")

    def test_high_absolute_with_unstable_rank_never_outranks_a_stable_winner(self):
        # unstable ranking = a tie; a strong absolute number must not mint a DEPLOY
        v = sdv.get_verdict(rank=1, rank_stability="unstable",
                            demand_score_relative=90, tier="F3", calibration_valid=True)
        self.assertNotEqual(v, "DEPLOY")

    def test_absolute_only_makes_more_conservative(self):
        # stable winner but very weak absolute demand -> SKIP (absolute drags it down)
        v = sdv.get_verdict(rank=1, rank_stability="stable",
                            demand_score_relative=30, tier="F3", calibration_valid=True)
        self.assertEqual(v, "SKIP")

    def test_non_winner_caps_below_deploy(self):
        v = sdv.get_verdict(rank=2, rank_stability="stable",
                            demand_score_relative=85, tier="F3", calibration_valid=True)
        self.assertNotEqual(v, "DEPLOY")

    def test_indeterminate_caps_at_test(self):
        v = sdv.get_verdict(rank=1, rank_stability="indeterminate",
                            demand_score_relative=85, tier="F3", calibration_valid=True)
        self.assertEqual(v, "TEST")


# ---------------------------------------------------------------------------
# §5 — intent->behavior discount; 1.0 only when F3 calibration justifies it
# ---------------------------------------------------------------------------
class TestIntentBehaviorDiscount(unittest.TestCase):
    def test_uncalibrated_tiers_use_conservative_default(self):
        self.assertAlmostEqual(sdv.intent_behavior_discount("F0"), 0.5, places=6)
        self.assertAlmostEqual(sdv.intent_behavior_discount("F2"), 0.5, places=6)

    def test_f3_without_calibration_still_discounts(self):
        # F3 detected but no fitted map handed in -> must NOT be 1.0
        self.assertLess(sdv.intent_behavior_discount("F3", calibration=None), 1.0)

    def test_f3_with_valid_calibration_can_lift(self):
        cal = {"valid": True, "learned_discount": 0.8}
        self.assertAlmostEqual(sdv.intent_behavior_discount("F3", calibration=cal), 0.8, places=6)


# ---------------------------------------------------------------------------
# Fidelity tier detection + CI width (lower tier => wider)
# ---------------------------------------------------------------------------
class TestFidelity(unittest.TestCase):
    def test_tier_is_highest_satisfied_trigger(self):
        self.assertEqual(sdv.detect_tier({}), "F0")
        self.assertEqual(sdv.detect_tier({"personas": True}), "F1")
        self.assertEqual(sdv.detect_tier({"personas": True, "customer_language": True}), "F2")
        self.assertEqual(sdv.detect_tier(
            {"personas": True, "customer_language": True, "conversion_data": True}), "F3")

    def test_lower_tier_is_wider(self):
        wide = sdv.ci_width("F0", familiarity=0.5, effective_samples=9)
        tight = sdv.ci_width("F3", familiarity=0.5, effective_samples=9)
        self.assertGreater(wide, tight)

    def test_low_familiarity_widens(self):
        unfamiliar = sdv.ci_width("F1", familiarity=0.1, effective_samples=9)
        familiar = sdv.ci_width("F1", familiarity=0.9, effective_samples=9)
        self.assertGreater(unfamiliar, familiar)


# ---------------------------------------------------------------------------
# Autonomy resolution — spending is human-gated, like HVA scaling
# ---------------------------------------------------------------------------
class TestAutonomyResolution(unittest.TestCase):
    def test_deploy_never_auto_acts(self):
        self.assertEqual(sdv.resolve_action("DEPLOY", "full-auto"), "recommend-deploy")

    def test_skip_can_auto_archive_at_higher_autonomy(self):
        self.assertEqual(sdv.resolve_action("SKIP", "recommend"), "recommend-archive")
        self.assertEqual(sdv.resolve_action("SKIP", "cut-auto"), "auto-archive")

    def test_test_and_iterate_hold(self):
        self.assertEqual(sdv.resolve_action("TEST", "full-auto"), "hold")
        self.assertEqual(sdv.resolve_action("ITERATE", "full-auto"), "hold")


# ---------------------------------------------------------------------------
# §8 — no cross-surface comparison
# ---------------------------------------------------------------------------
class TestCrossSurfaceGuard(unittest.TestCase):
    def test_ranking_across_surfaces_raises(self):
        variants = [{"id": "V1", "surface": "ad_creative"},
                    {"id": "V2", "surface": "offer"}]
        with self.assertRaises(ValueError):
            sdv.assert_single_surface(variants)

    def test_same_surface_is_ok(self):
        variants = [{"id": "V1", "surface": "ad_creative"},
                    {"id": "V2", "surface": "ad_creative"}]
        self.assertEqual(sdv.assert_single_surface(variants), "ad_creative")


# ---------------------------------------------------------------------------
# §7 — positivity-bias defenses are auditable; missing ones derate
# ---------------------------------------------------------------------------
class TestPositivityGuards(unittest.TestCase):
    def test_missing_defenses_produce_warnings(self):
        priming = {"skeptic_stance_applied": False, "budget_salience_applied": True,
                   "do_nothing_option_present": True, "comparative_mode": True}
        warnings = sdv.positivity_warnings(priming, n_variants=3)
        self.assertTrue(any("skeptic" in w for w in warnings))

    def test_single_variant_requires_do_nothing_reference(self):
        priming = {"skeptic_stance_applied": True, "budget_salience_applied": True,
                   "do_nothing_option_present": False, "comparative_mode": False}
        warnings = sdv.positivity_warnings(priming, n_variants=1)
        self.assertTrue(any("do-nothing" in w or "status-quo" in w for w in warnings))

    def test_clean_priming_no_warnings(self):
        priming = {"skeptic_stance_applied": True, "budget_salience_applied": True,
                   "do_nothing_option_present": True, "comparative_mode": True}
        self.assertEqual(sdv.positivity_warnings(priming, n_variants=3), [])


# ---------------------------------------------------------------------------
# Integration — score_forecast ties it together and refuses an F0 absolute verdict
# ---------------------------------------------------------------------------
class TestScoreForecast(unittest.TestCase):
    def _three_creative_forecast(self, tier="F0"):
        def variant(vid, pi, appeal):
            return {
                "id": vid,
                "surface": "ad_creative",
                "constructs": {
                    "purchase_intent": good_elicitation(pi),
                    "appeal": good_elicitation(appeal),
                },
                "priming": {"skeptic_stance_applied": True, "budget_salience_applied": True,
                            "do_nothing_option_present": True, "comparative_mode": True},
            }
        return {
            "surface": "ad_creative",
            "tier": tier,
            "familiarity": 0.6,
            "comparison": {
                "method": "best_worst",
                "best": {"V1": 4, "V2": 1, "V3": 0},
                "worst": {"V1": 0, "V2": 1, "V3": 4},
                "appeared": {"V1": 5, "V2": 5, "V3": 5},
                "resamples": [["V1", "V2", "V3"]] * 5,
            },
            "variants": [
                variant("V1", [0.02, 0.08, 0.20, 0.45, 0.25], [0.02, 0.08, 0.20, 0.45, 0.25]),
                variant("V2", [0.10, 0.25, 0.40, 0.20, 0.05], [0.10, 0.25, 0.40, 0.20, 0.05]),
                variant("V3", [0.30, 0.35, 0.25, 0.08, 0.02], [0.30, 0.35, 0.25, 0.08, 0.02]),
            ],
        }

    def test_ranks_variants_and_flags_directional_at_f0(self):
        out = sdv.score_forecast(self._three_creative_forecast("F0"), {})
        # V1 is the comparative winner
        ranked = out["ranking"]
        self.assertEqual(ranked[0]["id"], "V1")
        # F0 => no DEPLOY for anyone; absolute is labeled directional
        self.assertTrue(all(v["verdict"] != "DEPLOY" for v in out["variants"]))
        self.assertTrue(out["fidelity"]["directional"])
        # absolute field carries the relative/uncalibrated label below F3
        self.assertIn("demand_score_relative", out["variants"][0])

    def test_rejects_number_elicited_variant(self):
        fc = self._three_creative_forecast("F0")
        fc["variants"][0]["constructs"]["purchase_intent"]["pmf"] = [0, 0, 1, 0, 0]
        with self.assertRaises(ValueError):
            sdv.score_forecast(fc, {})


# ---------------------------------------------------------------------------
# Phase 3 — price sensitivity (Van Westendorp + Gabor-Granger), offers only
# ---------------------------------------------------------------------------
class TestVanWestendorp(unittest.TestCase):
    def _symmetric_curves(self):
        # Symmetric so the crossings land on clean round numbers.
        prices = [200, 250, 300]
        return {
            "too_cheap":      {200: 0.6, 250: 0.4, 300: 0.2},  # descending
            "cheap":          {200: 0.8, 250: 0.6, 300: 0.4},  # descending
            "expensive":      {200: 0.2, 250: 0.4, 300: 0.6},  # ascending
            "too_expensive":  {200: 0.0, 250: 0.2, 300: 0.4},  # ascending
        }, prices

    def test_pmc_is_too_cheap_meets_expensive(self):
        curves, _ = self._symmetric_curves()
        out = sdv.van_westendorp_crossings(curves)
        self.assertAlmostEqual(out["pmc"], 250.0, places=2)  # too_cheap==expensive at 250

    def test_opp_is_too_cheap_meets_too_expensive(self):
        curves, _ = self._symmetric_curves()
        out = sdv.van_westendorp_crossings(curves)
        # too_cheap: .6/.4/.2 ; too_expensive: 0/.2/.4 -> cross where .6-2k == ... at 300 both .2? no.
        # too_cheap(300)=.2, too_expensive(300)=.4 -> crossing just below 300
        self.assertTrue(250 <= out["opp"] <= 300)

    def test_acceptable_range_is_pmc_to_pme(self):
        curves, _ = self._symmetric_curves()
        out = sdv.van_westendorp_crossings(curves)
        self.assertEqual(out["acceptable_range"], [out["pmc"], out["pme"]])
        self.assertLessEqual(out["acceptable_range"][0], out["acceptable_range"][1])


class TestGaborGranger(unittest.TestCase):
    def test_revenue_max_price_is_argmax_of_price_times_conversion(self):
        curve = {199: 0.10, 299: 0.08, 499: 0.05, 699: 0.03, 999: 0.02}
        out = sdv.gabor_granger_revenue_index(curve)
        # revenue_index: 19.9, 23.92, 24.95, 20.97, 19.98 -> peak at 499
        self.assertEqual(out["revenue_max_price"], 499)
        peak = next(p for p in out["demand_curve"] if p["price"] == 499)
        self.assertAlmostEqual(peak["revenue_index"], 24.95, places=2)

    def test_demand_curve_is_sorted_by_price(self):
        curve = {999: 0.02, 199: 0.10, 499: 0.05}
        out = sdv.gabor_granger_revenue_index(curve)
        prices = [p["price"] for p in out["demand_curve"]]
        self.assertEqual(prices, sorted(prices))


class TestMonotonicity(unittest.TestCase):
    def test_nonincreasing_conversion_is_clean(self):
        self.assertTrue(sdv.is_monotonic_nonincreasing([0.10, 0.08, 0.05, 0.03]))

    def test_increasing_conversion_is_flagged(self):
        # demand rising with price = noise, not a real curve
        self.assertFalse(sdv.is_monotonic_nonincreasing([0.05, 0.08, 0.03]))


if __name__ == "__main__":
    unittest.main()
