"""Check economic units against a known log-linear data-generating process."""
import math
import unittest

import numpy as np
import pandas as pd

from revision_experiments import LinearRegressor, granger_f_test, mape, regression_metrics


class SensitivityUnitsTest(unittest.TestCase):
    def test_elasticity_matches_known_response_to_ten_percent_price_change(self):
        rng = np.random.default_rng(42)
        n = 120
        log_price = rng.normal(4.0, 0.13, n)
        inflation = rng.normal(2.0, 0.5, n)
        time = np.arange(n, dtype=float)
        x = pd.DataFrame({"log_price": log_price, "inflation": inflation, "time": time})
        # The economic elasticity is 0.3, irrespective of the spread of prices.
        y = -4.0 + 0.3 * log_price + 0.02 * inflation - 0.0001 * time
        model = LinearRegressor().fit(x, y)
        elasticity = model.coefficient_original_units(0)
        self.assertAlmostEqual(elasticity, 0.3, places=10)
        shocked = x.copy()
        shocked["log_price"] += math.log(1.1)
        predicted_ratio = np.exp(model.predict(shocked) - model.predict(x))
        np.testing.assert_allclose(predicted_ratio, 1.1 ** 0.3, rtol=1e-10)
        original_wacc = 0.08
        calculated_bp = math.expm1(elasticity * math.log(1.1)) * original_wacc * 10000
        known_bp = ((1.1 ** 0.3) - 1) * 800
        self.assertAlmostEqual(calculated_bp, known_bp, places=9)


class ReproducibilityGuardrailsTest(unittest.TestCase):
    def test_metrics_reject_unaligned_or_nonfinite_inputs(self):
        with self.assertRaises(ValueError):
            regression_metrics([1.0, 2.0], [1.0])
        with self.assertRaises(ValueError):
            regression_metrics([1.0, np.nan], [1.0, 2.0])
        with self.assertRaises(ValueError):
            regression_metrics([], [])

    def test_zero_target_mape_is_explicitly_undefined(self):
        self.assertTrue(math.isnan(mape(np.zeros(3), np.ones(3))))
        self.assertAlmostEqual(mape(np.array([1.0, 2.0]), np.array([1.1, 1.8])), 0.1)

    def test_regressor_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            LinearRegressor(alpha=-1.0)
        with self.assertRaises(ValueError):
            LinearRegressor().fit(np.array([[1.0], [np.nan]]), np.array([0.1, 0.2]))
        model = LinearRegressor().fit(np.array([[1.0], [2.0], [3.0]]), np.array([2.0, 4.0, 6.0]))
        with self.assertRaises(ValueError):
            model.predict(np.ones((3, 2)))

    def test_granger_retains_calendar_lags_across_missing_years(self):
        rng = np.random.default_rng(19)
        n, lags = 90, 2
        x = rng.normal(size=n)
        y = 0.3 * np.roll(x, 1) + rng.normal(scale=0.5, size=n)
        x[20] = np.nan
        y[35] = np.nan
        result = granger_f_test(y, x, lags)
        dep = y[lags:]
        rest = np.column_stack([np.ones(n - lags), y[1:-1], y[:-2]])
        full = np.column_stack([rest, x[1:-1], x[:-2]])
        valid = np.isfinite(dep) & np.isfinite(full).all(axis=1)
        dep, rest, full = dep[valid], rest[valid], full[valid]
        ssr_r = np.sum((dep - rest @ (np.linalg.pinv(rest) @ dep)) ** 2)
        ssr_u = np.sum((dep - full @ (np.linalg.pinv(full) @ dep)) ** 2)
        df_den = len(dep) - full.shape[1]
        expected_f = ((ssr_r - ssr_u) / lags) / (ssr_u / df_den)
        self.assertAlmostEqual(result[0], expected_f, places=9)
        self.assertEqual(result[4], df_den)
        self.assertTrue(0 <= result[1] <= 1)

    def test_granger_rejects_mismatched_series(self):
        with self.assertRaises(ValueError):
            granger_f_test(np.ones(20), np.ones(19), 1)
        with self.assertRaises(ValueError):
            granger_f_test(np.ones(20), np.ones(20), 0)


if __name__ == "__main__":
    unittest.main()
