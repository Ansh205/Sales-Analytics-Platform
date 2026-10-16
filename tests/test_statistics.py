"""
test_statistics.py

Unit Tests for Statistical Hypothesis Testing Module and Calculation Integrity.
"""

import json
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from scripts.ml.statistical_analysis import (
    compute_group_descriptives,
    perform_mann_whitney_u_test,
    perform_welch_t_test,
    evaluate_category_subgroups,
)


class TestStatisticalAnalysis(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        # Group 1: High profit (low discount)
        self.g1 = pd.Series(np.random.normal(loc=50.0, scale=20.0, size=200))
        # Group 2: Negative profit (high discount)
        self.g2 = pd.Series(np.random.normal(loc=-40.0, scale=35.0, size=150))

    def test_group_descriptives_calculation(self):
        """Verify descriptive metrics calculation on sample data."""
        desc = compute_group_descriptives(self.g1, "Test Group 1")
        self.assertEqual(desc["sample_size"], 200)
        self.assertAlmostEqual(desc["mean"], float(self.g1.mean()), places=4)
        self.assertAlmostEqual(desc["median"], float(self.g1.median()), places=4)
        self.assertGreater(desc["std_dev"], 0.0)
        self.assertGreater(desc["iqr"], 0.0)
        self.assertEqual(desc["loss_orders_count"], int((self.g1 < 0).sum()))

    def test_welch_t_test_results(self):
        """Verify Welch's t-test computes correct mean diff, df, CI, and Cohen's d."""
        res = perform_welch_t_test(self.g1, self.g2, "G1", "G2")

        # Mean difference should be positive
        self.assertGreater(res["mean_difference"], 0.0)
        self.assertGreater(res["t_statistic"], 0.0)
        self.assertLess(res["p_value"], 0.001)
        self.assertTrue(res["significant_at_alpha_0_05"])

        # Check CI brackets the mean difference
        self.assertLess(res["ci_lower_95"], res["mean_difference"])
        self.assertGreater(res["ci_upper_95"], res["mean_difference"])

        # Check Cohen's d is positive and large
        self.assertGreater(res["cohens_d"], 1.0)

    def test_mann_whitney_u_test(self):
        """Verify non-parametric Mann-Whitney U test execution."""
        res = perform_mann_whitney_u_test(self.g1, self.g2, "G1", "G2")
        self.assertIn("u_statistic", res)
        self.assertIn("p_value", res)
        self.assertLess(res["p_value"], 0.001)
        self.assertTrue(res["significant_at_alpha_0_05"])

    def test_small_sample_and_edge_cases(self):
        """Verify handling of small sample sizes and minimal variability."""
        small_g1 = pd.Series([10.0, 10.0, 10.0])
        small_g2 = pd.Series([5.0, 5.0, 5.0])
        res = perform_welch_t_test(small_g1, small_g2, "S1", "S2")
        self.assertIsInstance(res, dict)
        self.assertEqual(res["mean_difference"], 5.0)

    def test_category_subgroups_bonferroni(self):
        """Verify subgroup analysis calculates Bonferroni adjusted alpha correctly."""
        df_sub = pd.DataFrame({
            "Category": ["Furniture"] * 50 + ["Technology"] * 50,
            "Discount": [0.1] * 25 + [0.5] * 25 + [0.1] * 25 + [0.5] * 25,
            "Profit": [40.0] * 25 + [-30.0] * 25 + [100.0] * 25 + [-50.0] * 25,
        })
        subgroup_results = evaluate_category_subgroups(df_sub, threshold=0.20, alpha=0.05)
        self.assertEqual(len(subgroup_results), 2)
        # Bonferroni alpha = 0.05 / 2 = 0.025
        for s in subgroup_results:
            self.assertAlmostEqual(s["bonferroni_alpha"], 0.025, places=4)
            self.assertTrue(s["significant_after_bonferroni"])

    def test_saved_statistical_results_artifact(self):
        """Verify the generated statistical results artifact exists and is consistent."""
        artifact_path = Path("reports/statistical_hypothesis_results.json")
        self.assertTrue(artifact_path.exists(), "statistical_hypothesis_results.json not found")

        with open(artifact_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("welch_t_test", data)
        self.assertIn("descriptives", data)
        self.assertIn("subgroup_category_analysis", data)

        welch = data["welch_t_test"]
        self.assertTrue(welch["significant_at_alpha_0_05"])
        self.assertGreater(welch["t_statistic"], 10.0)
        self.assertLess(welch["p_value"], 1e-10)


if __name__ == "__main__":
    unittest.main()
