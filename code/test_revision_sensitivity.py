"""Check economic units against a known log-linear data-generating process."""
import math
import unittest

import numpy as np
import pandas as pd

from revision_experiments import LinearRegressor


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


if __name__ == "__main__":
    unittest.main()
