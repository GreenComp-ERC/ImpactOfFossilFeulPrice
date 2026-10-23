"""Artifact integrity tests for committed datasets and diagnostic outputs.

These tests validate expected shapes, keys and economic units. They do not
claim independent reruns of neural-network or AutoGluon training.
"""
from __future__ import annotations

import math
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class ArtifactIntegrityTest(unittest.TestCase):
    def test_required_source_assets_are_present(self):
        assets = [
            "Average_oil_price.xlsx",
            "Average_Coal_Price.xlsx",
            "Average_Gas_price.xlsx",
            "China_WACC.xlsx",
            "Euope_WACC.xlsx",
            "Middle_EAST_WACC.xlsx",
            "comprehensive_economic_data.xlsx",
            "inflation_forecasts_2026_2035.xlsx",
            "Accuracy_Prediction-Model.xlsx",
        ]
        for name in assets:
            with self.subTest(asset=name):
                self.assertTrue((DATA / name).is_file(), f"Missing input: data/{name}")

    def test_cleaned_panels_cover_exactly_120_distinct_months(self):
        names = [
            "China_WACC_2026_2035_cleaned.xlsx",
            "Europe_WACC_2026_2035_cleaned.xlsx",
            "Middle_East_WACC_2026_2035_cleaned.xlsx",
        ]
        expected = pd.date_range("2026-01-01", periods=120, freq="MS")
        for name in names:
            with self.subTest(panel=name):
                df = pd.read_excel(DATA / "revision_cleaned" / name)
                dates = pd.to_datetime(df["Month"])
                self.assertTrue(pd.DatetimeIndex(dates).equals(expected))
                self.assertFalse(df["Month"].duplicated().any())
                self.assertEqual(len(df), 120)
                numeric = df.drop(columns=["Month"]).to_numpy(dtype=float)
                self.assertTrue(np.isfinite(numeric).all())

    def test_stage3_output_granularity_and_unique_keys(self):
        checks = {
            "stage3_holdout_metrics.csv": (
                810, ["Region", "Project", "Fuel", "Feature Spec", "Model"]
            ),
            "stage3_rolling_metrics.csv": (
                1620, ["Region", "Project", "Fuel", "Feature Spec", "Model", "Test Year"]
            ),
            "stage3_price_elasticities.csv": (
                81, ["Region", "Project", "Fuel"]
            ),
        }
        for filename, (expected, key_columns) in checks.items():
            with self.subTest(output=filename):
                df = pd.read_csv(DATA / "revision_results" / filename)
                self.assertEqual(len(df), expected)
                self.assertFalse(df.duplicated(subset=key_columns).any())
                self.assertEqual(
                    set(df["Region"]), {"China", "Europe", "Middle East"}
                )

    def test_saved_sensitivity_basis_points_are_consistent_with_elasticity(self):
        df = pd.read_csv(DATA / "revision_results" / "stage3_price_elasticities.csv")
        self.assertEqual(len(df), 81)
        expected = np.expm1(df["Elasticity_LogPrice"] * math.log(1.1))
        expected *= df["Mean WACC"] * 10_000.0
        np.testing.assert_allclose(
            df["10pct Price Shock WACC Delta bp"].to_numpy(dtype=float),
            expected,
            atol=1e-8,
            rtol=1e-10,
        )

    def test_reported_transmission_p_values_are_probabilities(self):
        df = pd.read_csv(DATA / "revision_results" / "transmission_granger_diagnostics.csv")
        reported = df["P Value"].dropna()
        self.assertTrue(reported.between(0.0, 1.0).all())


if __name__ == "__main__":
    unittest.main()
