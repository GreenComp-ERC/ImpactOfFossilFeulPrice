#!/usr/bin/env python3
"""Revision experiments for the fossil-fuel-price / WACC paper.

This script implements the reviewer-facing fixes:

1. Build cleaned WACC inputs with region-specific inflation forecasts.
2. Restrict all regions to the common 2026-2035 horizon.
3. Re-evaluate Stage 3 with strict time holdout and rolling-origin tests.
4. Estimate price-shock sensitivity with log-linear elasticities.
5. Run lightweight Granger-style transmission diagnostics on historical data.
6. Summarize the existing Stage 1 forecast comparison under consistent metrics.

The implementation intentionally depends only on pandas, numpy, and openpyxl so
it can run in a minimal reproduction environment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
CLEAN_DIR = DATA_DIR / "revision_cleaned"
RESULT_DIR = DATA_DIR / "revision_results"

PROJECTS = [
    "Onshore",
    "Offshore",
    "Nuclear",
    "CCS",
    "Coal",
    "Gas",
    "Solar",
    "Hydro",
    "Biomass",
]

TRANSITION_PROJECTS = [
    "Onshore",
    "Offshore",
    "Solar",
    "Hydro",
    "Biomass",
    "Nuclear",
    "CCS",
]

FUEL_COLUMNS = ["Coal Price", "Gas Price", "Oil Price"]


@dataclass(frozen=True)
class RegionSpec:
    region: str
    raw_file: str
    inflation_column: str
    cleaned_file: str


REGIONS = [
    RegionSpec("China", "China_WACC.xlsx", "China", "China_WACC_2026_2035_cleaned.xlsx"),
    RegionSpec(
        "Europe",
        "Euope_WACC.xlsx",
        "European Union",
        "Europe_WACC_2026_2035_cleaned.xlsx",
    ),
    RegionSpec(
        "Middle East",
        "Middle_EAST_WACC.xlsx",
        "Middle East & North Africa",
        "Middle_East_WACC_2026_2035_cleaned.xlsx",
    ),
]


def ensure_dirs() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = out.columns.astype(str).str.strip()
    return out


def build_cleaned_wacc_inputs() -> pd.DataFrame:
    """Create region-specific, horizon-aligned WACC files."""
    inflation = clean_columns(pd.read_excel(DATA_DIR / "inflation_forecasts_2026_2035.xlsx"))
    required_inflation = ["Year", *(spec.inflation_column for spec in REGIONS)]
    missing_inflation = [name for name in required_inflation if name not in inflation.columns]
    if missing_inflation:
        raise ValueError(f"Inflation forecast workbook is missing columns: {missing_inflation}")
    inflation["Year"] = pd.to_numeric(inflation["Year"], errors="raise").astype(int)
    if inflation["Year"].duplicated().any():
        raise ValueError("Inflation forecasts must contain exactly one row per year.")

    expected_months = pd.date_range("2026-01-01", "2035-12-01", freq="MS")
    reports = []
    for spec in REGIONS:
        raw_path = DATA_DIR / spec.raw_file
        raw = clean_columns(pd.read_excel(raw_path))
        if "Month" not in raw.columns or "inflation rate" not in raw.columns:
            raise ValueError(f"{spec.raw_file} must include Month and inflation rate.")
        raw["Month"] = pd.to_datetime(raw["Month"], errors="coerce")
        if raw["Month"].isna().any():
            raise ValueError(f"{spec.raw_file} contains invalid monthly timestamps.")
        if raw["Month"].duplicated().any():
            raise ValueError(f"{spec.raw_file} contains duplicate months.")
        raw["Year"] = raw["Month"].dt.year

        old_inflation = raw[["Month", "inflation rate"]].copy()

        fixed = raw.merge(
            inflation[["Year", spec.inflation_column]],
            on="Year",
            how="left",
            validate="many_to_one",
        )
        fixed["inflation rate"] = fixed[spec.inflation_column]
        fixed = fixed.drop(columns=[spec.inflation_column])
        fixed = fixed[(fixed["Month"] >= "2026-01-01") & (fixed["Month"] <= "2035-12-01")]
        fixed = fixed.sort_values("Month").reset_index(drop=True)

        output_columns = ["Month"] + PROJECTS + FUEL_COLUMNS + ["inflation rate"]
        missing = [col for col in output_columns if col not in fixed.columns]
        if missing:
            raise ValueError(f"{spec.raw_file} is missing required columns: {missing}")
        fixed = fixed[output_columns]
        if not pd.DatetimeIndex(fixed["Month"]).equals(expected_months):
            raise ValueError(f"{spec.raw_file} does not cover each month from 2026-01 to 2035-12.")
        if not np.isfinite(fixed[output_columns[1:]].to_numpy(dtype=float)).all():
            raise ValueError(f"{spec.raw_file} has missing or non-finite numeric inputs after cleaning.")

        # Match original inflation by calendar month, not by position in the raw workbook.
        old_common = fixed[["Month"]].merge(
            old_inflation, on="Month", how="left", validate="one_to_one"
        )
        if old_common["inflation rate"].isna().any():
            raise ValueError(f"{spec.raw_file} has missing original inflation observations.")
        diff = fixed["inflation rate"].to_numpy() - old_common["inflation rate"].to_numpy()

        cleaned_path = CLEAN_DIR / spec.cleaned_file
        fixed.to_excel(cleaned_path, index=False)

        reports.append(
            {
                "Region": spec.region,
                "Raw File": spec.raw_file,
                "Cleaned File": str(cleaned_path.relative_to(REPO_ROOT)),
                "Raw Rows": len(raw),
                "Cleaned Rows": len(fixed),
                "Start": fixed["Month"].min().strftime("%Y-%m"),
                "End": fixed["Month"].max().strftime("%Y-%m"),
                "Original First Inflation": float(old_common["inflation rate"].iloc[0]),
                "Fixed First Inflation": float(fixed["inflation rate"].iloc[0]),
                "Mean Abs Inflation Correction": float(np.nanmean(np.abs(diff))),
                "Missing Values After Fix": int(fixed.isna().sum().sum()),
            }
        )

    report_df = pd.DataFrame(reports)
    report_df.to_csv(RESULT_DIR / "input_cleaning_report.csv", index=False)
    return report_df


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return fractional MAPE; all-zero targets have undefined MAPE."""
    denom = np.where(np.abs(y_true) < 1e-12, np.nan, np.abs(y_true))
    errors = np.abs((y_true - y_pred) / denom)
    return float(np.nanmean(errors)) if np.any(np.isfinite(errors)) else float("nan")


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot <= 1e-18:
        return float("nan")
    return 1.0 - ss_res / ss_tot


def regression_metrics(y_true: Iterable[float], y_pred: Iterable[float]) -> dict[str, float]:
    y = np.asarray(list(y_true), dtype=float)
    pred = np.asarray(list(y_pred), dtype=float)
    if y.ndim != 1 or pred.ndim != 1 or len(y) == 0 or len(y) != len(pred):
        raise ValueError("Metric inputs must be nonempty, one-dimensional, and equal in length.")
    if not np.isfinite(y).all() or not np.isfinite(pred).all():
        raise ValueError("Metric inputs contain non-finite values.")
    return {
        "R2": r2_score(y, pred),
        "MAPE": mape(y, pred),
        "RMSE": rmse(y, pred),
        "MAE": mae(y, pred),
    }


class LinearRegressor:
    """Small standardized linear/ridge regressor with intercept."""

    def __init__(self, alpha: float = 0.0):
        if not np.isfinite(alpha) or alpha < 0:
            raise ValueError("Ridge regularization alpha must be nonnegative and finite.")
        self.alpha = alpha
        self.x_mean: np.ndarray | None = None
        self.x_std: np.ndarray | None = None
        self.beta: np.ndarray | None = None

    def fit(self, x: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> "LinearRegressor":
        x_arr = np.asarray(x, dtype=float)
        y_arr = np.asarray(y, dtype=float)
        if x_arr.ndim != 2 or y_arr.ndim != 1 or len(x_arr) != len(y_arr) or len(y_arr) < 2:
            raise ValueError("Training inputs must be a 2D feature matrix and matching target.")
        if x_arr.shape[1] < 1 or not np.isfinite(x_arr).all() or not np.isfinite(y_arr).all():
            raise ValueError("Training inputs must be nonempty, finite numeric values.")
        self.x_mean = np.nanmean(x_arr, axis=0)
        self.x_std = np.nanstd(x_arr, axis=0)
        self.x_std[self.x_std < 1e-12] = 1.0
        x_scaled = (x_arr - self.x_mean) / self.x_std
        design = np.column_stack([np.ones(len(x_scaled)), x_scaled])
        penalty = np.eye(design.shape[1]) * self.alpha
        penalty[0, 0] = 0.0
        self.beta = np.linalg.pinv(design.T @ design + penalty) @ design.T @ y_arr
        return self

    def predict(self, x: pd.DataFrame | np.ndarray) -> np.ndarray:
        if self.beta is None or self.x_mean is None or self.x_std is None:
            raise RuntimeError("Model must be fitted before prediction.")
        x_arr = np.asarray(x, dtype=float)
        if x_arr.ndim != 2 or x_arr.shape[1] != len(self.x_mean):
            raise ValueError("Prediction features must match the fitted feature dimensions.")
        if not np.isfinite(x_arr).all():
            raise ValueError("Prediction features must be finite.")
        x_scaled = (x_arr - self.x_mean) / self.x_std
        design = np.column_stack([np.ones(len(x_scaled)), x_scaled])
        return design @ self.beta

    def coefficient_original_units(self, feature_index: int) -> float:
        """Return a slope with the feature standardization reversed."""
        if self.beta is None or self.x_std is None:
            raise RuntimeError("Model must be fitted before reading coefficients.")
        return float(self.beta[feature_index + 1] / self.x_std[feature_index])


def add_time_index(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["time_index"] = np.arange(len(out), dtype=float)
    return out


def make_modeling_frame(df: pd.DataFrame, target: str, fuel: str, spec: str) -> tuple[pd.DataFrame, list[str], str]:
    base = add_time_index(df[["Month", target, fuel, "inflation rate"]].dropna())
    if spec == "time_only":
        return base, ["time_index"], target
    if spec == "inflation_trend":
        return base, ["inflation rate", "time_index"], target
    if spec == "level":
        return base, [fuel, "inflation rate"], target
    if spec == "level_trend":
        return base, [fuel, "inflation rate", "time_index"], target
    if spec == "diff":
        diffed = base.copy()
        for col in [target, fuel, "inflation rate"]:
            diffed[col] = diffed[col].diff()
        diffed = diffed.dropna().reset_index(drop=True)
        diffed["time_index"] = np.arange(len(diffed), dtype=float)
        return diffed, [fuel, "inflation rate"], target
    raise ValueError(f"Unknown feature specification: {spec}")


def run_stage3_holdout() -> pd.DataFrame:
    """Train on 2026-2032 and test on 2033-2035."""
    rows = []
    model_specs = {"OLS": 0.0, "Ridge_alpha_1": 1.0}
    feature_specs = ["time_only", "inflation_trend", "level", "level_trend", "diff"]

    for spec in REGIONS:
        df = clean_columns(pd.read_excel(CLEAN_DIR / spec.cleaned_file))
        df["Month"] = pd.to_datetime(df["Month"])
        for target in PROJECTS:
            for fuel in FUEL_COLUMNS:
                for feature_spec in feature_specs:
                    frame, features, label = make_modeling_frame(df, target, fuel, feature_spec)
                    train_mask = frame["Month"] <= "2032-12-01"
                    test_mask = frame["Month"] >= "2033-01-01"
                    train = frame.loc[train_mask]
                    test = frame.loc[test_mask]
                    if len(train) < 12 or len(test) < 6:
                        continue
                    for model_name, alpha in model_specs.items():
                        model = LinearRegressor(alpha=alpha).fit(train[features], train[label])
                        pred = model.predict(test[features])
                        metrics = regression_metrics(test[label], pred)
                        rows.append(
                            {
                                "Region": spec.region,
                                "Project": target,
                                "Fuel": fuel,
                                "Feature Spec": feature_spec,
                                "Model": model_name,
                                "Train Rows": len(train),
                                "Test Rows": len(test),
                                **metrics,
                            }
                        )

    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "stage3_holdout_metrics.csv", index=False)
    return out


def run_stage3_rolling() -> pd.DataFrame:
    """Rolling-origin tests using the next calendar year as the test fold."""
    rows = []
    feature_specs = ["time_only", "inflation_trend", "level_trend", "diff"]

    for spec in REGIONS:
        df = clean_columns(pd.read_excel(CLEAN_DIR / spec.cleaned_file))
        df["Month"] = pd.to_datetime(df["Month"])
        for target in PROJECTS:
            for fuel in FUEL_COLUMNS:
                for feature_spec in feature_specs:
                    frame, features, label = make_modeling_frame(df, target, fuel, feature_spec)
                    for train_end_year in range(2030, 2035):
                        test_year = train_end_year + 1
                        train_mask = frame["Month"] <= f"{train_end_year}-12-01"
                        test_mask = (
                            (frame["Month"] >= f"{test_year}-01-01")
                            & (frame["Month"] <= f"{test_year}-12-01")
                        )
                        train = frame.loc[train_mask]
                        test = frame.loc[test_mask]
                        if len(train) < 24 or len(test) < 6:
                            continue
                        model = LinearRegressor(alpha=1.0).fit(train[features], train[label])
                        pred = model.predict(test[features])
                        metrics = regression_metrics(test[label], pred)
                        rows.append(
                            {
                                "Region": spec.region,
                                "Project": target,
                                "Fuel": fuel,
                                "Feature Spec": feature_spec,
                                "Model": "Ridge_alpha_1",
                                "Train End Year": train_end_year,
                                "Test Year": test_year,
                                "Train Rows": len(train),
                                "Test Rows": len(test),
                                **metrics,
                            }
                        )

    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "stage3_rolling_metrics.csv", index=False)
    return out


def run_stage3_sensitivity() -> pd.DataFrame:
    """Estimate log-linear price elasticities and 10% price-shock deltas."""
    rows = []
    for spec in REGIONS:
        df = clean_columns(pd.read_excel(CLEAN_DIR / spec.cleaned_file))
        df["Month"] = pd.to_datetime(df["Month"])
        df = add_time_index(df)
        for target in PROJECTS:
            for fuel in FUEL_COLUMNS:
                subset = df[[target, fuel, "inflation rate", "time_index"]].dropna().copy()
                subset = subset[(subset[target] > 0) & (subset[fuel] > 0)]
                if len(subset) < 24:
                    continue
                x = pd.DataFrame(
                    {
                        "log_price": np.log(subset[fuel]),
                        "inflation rate": subset["inflation rate"],
                        "time_index": subset["time_index"],
                    }
                )
                y = np.log(subset[target])
                model = LinearRegressor(alpha=0.0).fit(x, y)
                pred = model.predict(x)
                elasticity = model.coefficient_original_units(0)
                mean_wacc = float(subset[target].mean())
                shock_10pct_bp = math.expm1(elasticity * math.log(1.10)) * mean_wacc * 10000.0
                rows.append(
                    {
                        "Region": spec.region,
                        "Project": target,
                        "Fuel": fuel,
                        "Elasticity_LogPrice": elasticity,
                        "Mean WACC": mean_wacc,
                        "10pct Price Shock WACC Delta bp": shock_10pct_bp,
                        "InSample Log R2": r2_score(np.asarray(y), pred),
                        "Rows": len(subset),
                        "Transition Project": target in TRANSITION_PROJECTS,
                    }
                )

    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "stage3_price_elasticities.csv", index=False)
    return out


def load_oil_prices() -> pd.DataFrame:
    columns = ["Date", "Crude_oil_average", "Crude_oil_Brent", "Crude_oil_Dubai", "Crude_oil_WTI"]
    df = pd.read_excel(
        DATA_DIR / "Average_oil_price.xlsx",
        sheet_name="Sheet1",
        skiprows=3,
        header=None,
        names=columns,
        na_values=["...", "...", "-", "nan", ""],
    )
    df["Date"] = pd.to_datetime(df["Date"].astype(str).str.replace("M", "-", regex=False), errors="coerce")
    df["Price"] = pd.to_numeric(df["Crude_oil_average"], errors="coerce")
    return df[["Date", "Price"]].dropna().sort_values("Date").reset_index(drop=True)


def load_coal_prices() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "Average_Coal_Price.xlsx", sheet_name="Sheet2", header=2)
    df = df.iloc[:, :3].copy()
    df.columns = ["Date", "Coal_Australian", "Coal_SouthAfrican"]
    df["Date"] = pd.to_datetime(df["Date"].astype(str).str.replace("M", "-", regex=False), errors="coerce")
    for col in ["Coal_Australian", "Coal_SouthAfrican"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Price"] = df[["Coal_Australian", "Coal_SouthAfrican"]].mean(axis=1)
    return df[["Date", "Price"]].dropna().sort_values("Date").reset_index(drop=True)


def load_gas_prices() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "Average_Gas_price.xlsx", sheet_name="Sheet3", header=2)
    df = df.iloc[:, :6].copy()
    df.columns = ["Date", "Gas_US", "Gas_Europe", "Gas_Japan", "Gas_Index", "Average_Gas_Price"]
    df["Date"] = pd.to_datetime(df["Date"].astype(str).str.replace("M", "-", regex=False), errors="coerce")
    df["Price"] = pd.to_numeric(df["Average_Gas_Price"], errors="coerce")
    return df[["Date", "Price"]].dropna().sort_values("Date").reset_index(drop=True)


def summarize_stage1_existing_accuracy() -> pd.DataFrame:
    """Compute consistent metrics for the existing comparison workbook."""
    accuracy_path = DATA_DIR / "Accuracy_Prediction-Model.xlsx"
    raw = pd.read_excel(accuracy_path, header=1)
    raw.columns = raw.columns.astype(str).str.strip()
    raw["Actual"] = pd.to_numeric(raw["Actual"], errors="coerce")

    rows = []
    for model_col in ["LSTM-GRP", "Sarima", "XGBoost", "LightGBM"]:
        if model_col not in raw.columns:
            continue
        pred = pd.to_numeric(raw[model_col], errors="coerce")
        mask = raw["Actual"].notna() & pred.notna()
        metrics = regression_metrics(raw.loc[mask, "Actual"], pred.loc[mask])
        rows.append(
            {
                "Model": model_col.replace("LSTM-GRP", "LSTM-GPR"),
                "Rows": int(mask.sum()),
                "Near Exact Months abs_error_lt_0.01": int(
                    np.sum(np.abs(raw.loc[mask, "Actual"].to_numpy() - pred.loc[mask].to_numpy()) < 0.01)
                ),
                **metrics,
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "stage1_existing_accuracy_metrics.csv", index=False)
    return out


def run_stage1_strict_baselines() -> pd.DataFrame:
    """Fixed-origin recursive oil-price baselines from 2021 through 2024."""
    prices = load_oil_prices()
    prices = prices[(prices["Date"] >= "1982-01-01") & (prices["Date"] <= "2024-12-01")]
    train = prices[prices["Date"] <= "2020-12-01"].copy()
    test = prices[(prices["Date"] >= "2021-01-01") & (prices["Date"] <= "2024-12-01")].copy()

    if len(train) < 120 or len(test) == 0:
        raise ValueError("Insufficient oil-price data for strict baseline evaluation.")

    def recursive_random_walk() -> np.ndarray:
        return np.repeat(train["Price"].iloc[-1], len(test))

    def recursive_seasonal_naive() -> np.ndarray:
        history = train["Price"].tolist()
        preds = []
        for _ in range(len(test)):
            pred = history[-12]
            preds.append(pred)
            history.append(pred)
        return np.asarray(preds)

    def recursive_drift() -> np.ndarray:
        first = float(train["Price"].iloc[0])
        last = float(train["Price"].iloc[-1])
        monthly_drift = (last - first) / max(len(train) - 1, 1)
        return np.asarray([last + monthly_drift * (step + 1) for step in range(len(test))])

    def ets_additive_seasonal_trend() -> np.ndarray:
        """A dependency-free ETS-style additive seasonal trend baseline."""
        train_copy = train.copy()
        train_copy["month"] = train_copy["Date"].dt.month
        monthly_mean = train_copy.groupby("month")["Price"].mean()
        global_mean = float(train_copy["Price"].mean())
        seasonal = {month: float(monthly_mean.get(month, global_mean) - global_mean) for month in range(1, 13)}

        last_year_avg = float(train_copy["Price"].tail(12).mean())
        prev_year_avg = float(train_copy["Price"].iloc[-24:-12].mean())
        monthly_trend = (last_year_avg - prev_year_avg) / 12.0
        level = last_year_avg

        preds = []
        for step, date in enumerate(test["Date"], start=1):
            pred = level + monthly_trend * step + seasonal[date.month]
            preds.append(pred)
        return np.asarray(preds)

    def recursive_lag_ridge(lag: int = 12) -> np.ndarray:
        full_train = train.reset_index(drop=True)
        x_rows = []
        y_vals = []
        for i in range(lag, len(full_train)):
            window = full_train["Price"].iloc[i - lag : i].to_numpy()
            date = full_train["Date"].iloc[i]
            month = date.month
            x_rows.append(
                np.concatenate(
                    [
                        window,
                        [
                            math.sin(2 * math.pi * month / 12),
                            math.cos(2 * math.pi * month / 12),
                            i / 12.0,
                        ],
                    ]
                )
            )
            y_vals.append(full_train["Price"].iloc[i])

        model = LinearRegressor(alpha=10.0).fit(np.asarray(x_rows), np.asarray(y_vals))
        history = full_train["Price"].tolist()
        preds = []
        start_idx = len(full_train)
        for step, date in enumerate(test["Date"]):
            window = np.asarray(history[-lag:])
            month = date.month
            x = np.concatenate(
                [
                    window,
                    [
                        math.sin(2 * math.pi * month / 12),
                        math.cos(2 * math.pi * month / 12),
                        (start_idx + step) / 12.0,
                    ],
                ]
            )
            pred = float(model.predict(x.reshape(1, -1))[0])
            preds.append(pred)
            history.append(pred)
        return np.asarray(preds)

    forecasts = {
        "RandomWalk_FixedOrigin": recursive_random_walk(),
        "SeasonalNaive12_FixedOrigin": recursive_seasonal_naive(),
        "Drift_FixedOrigin": recursive_drift(),
        "ETS_AdditiveSeasonalTrend": ets_additive_seasonal_trend(),
        "Lag12_Ridge_Recursive": recursive_lag_ridge(),
    }

    metrics_rows = []
    forecast_rows = test[["Date", "Price"]].rename(columns={"Price": "Actual"}).copy()
    for name, pred in forecasts.items():
        forecast_rows[name] = pred
        metrics_rows.append({"Model": name, "Rows": len(test), **regression_metrics(test["Price"], pred)})

    forecast_rows.to_csv(RESULT_DIR / "stage1_strict_oil_baseline_forecasts.csv", index=False)
    out = pd.DataFrame(metrics_rows)
    out.to_csv(RESULT_DIR / "stage1_strict_oil_baseline_metrics.csv", index=False)
    return out


def annualize_fuel_prices() -> pd.DataFrame:
    loaders = {
        "Coal Price": load_coal_prices,
        "Gas Price": load_gas_prices,
        "Oil Price": load_oil_prices,
    }
    pieces = []
    for fuel, loader in loaders.items():
        df = loader()
        df["year"] = df["Date"].dt.year
        annual = df.groupby("year", as_index=False)["Price"].mean()
        annual = annual.rename(columns={"Price": fuel})
        pieces.append(annual)
    merged = pieces[0]
    for piece in pieces[1:]:
        merged = merged.merge(piece, on="year", how="outer")
    return merged.sort_values("year")


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for incomplete beta, adapted for p-value output."""
    max_iter = 200
    eps = 3e-12
    fpmin = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def f_sf(f_stat: float, dfn: int, dfd: int) -> float:
    if not np.isfinite(f_stat) or f_stat < 0 or dfn <= 0 or dfd <= 0:
        return float("nan")
    x = (dfn * f_stat) / (dfn * f_stat + dfd)
    cdf = regularized_beta(x, dfn / 2.0, dfd / 2.0)
    return max(0.0, min(1.0, 1.0 - cdf))


def granger_f_test(y: np.ndarray, x: np.ndarray, lags: int) -> tuple[float, float, int, int, int]:
    """Manual Granger-style F-test: y_t on y lags vs y and x lags."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if y.ndim != 1 or x.ndim != 1 or len(y) != len(x) or lags < 1:
        raise ValueError("Granger inputs must be aligned one-dimensional series with positive lags.")
    n = len(y)
    if n <= 2 * lags + 4:
        return float("nan"), float("nan"), lags, 0, 0

    y_dep = y[lags:]
    y_lags = [y[lags - i - 1 : n - i - 1] for i in range(lags)]
    x_lags = [x[lags - i - 1 : n - i - 1] for i in range(lags)]
    restricted = np.column_stack([np.ones(len(y_dep)), *y_lags])
    unrestricted = np.column_stack([np.ones(len(y_dep)), *y_lags, *x_lags])
    # Construct lagged rows BEFORE dropping missing observations; removing them
    # first would incorrectly treat nonadjacent calendar years as adjacent.
    valid_rows = np.isfinite(y_dep) & np.isfinite(unrestricted).all(axis=1)
    y_dep = y_dep[valid_rows]
    restricted = restricted[valid_rows]
    unrestricted = unrestricted[valid_rows]

    if len(y_dep) <= 2 * lags + 4:
        return float("nan"), float("nan"), lags, lags, len(y_dep) - unrestricted.shape[1]
    beta_r = np.linalg.pinv(restricted) @ y_dep
    beta_u = np.linalg.pinv(unrestricted) @ y_dep
    resid_r = y_dep - restricted @ beta_r
    resid_u = y_dep - unrestricted @ beta_u
    ssr_r = float(np.sum(resid_r**2))
    ssr_u = float(np.sum(resid_u**2))
    df_num = lags
    df_den = len(y_dep) - unrestricted.shape[1]
    if ssr_u <= 1e-18 or df_den <= 0:
        return float("nan"), float("nan"), lags, df_num, df_den
    f_stat = ((ssr_r - ssr_u) / df_num) / (ssr_u / df_den)
    return f_stat, f_sf(f_stat, df_num, df_den), lags, df_num, df_den


def run_transmission_diagnostics() -> pd.DataFrame:
    fuels = annualize_fuel_prices()
    rows = []
    targets = {
        "Inflation": "FP_CPI_TOTL_ZG",
        "Real Interest Rate": "FR_INR_RINR",
    }
    for spec in REGIONS:
        macro = pd.read_excel(DATA_DIR / "comprehensive_economic_data.xlsx", sheet_name=spec.inflation_column)
        macro.columns = macro.columns.astype(str).str.strip()
        merged = macro.merge(fuels, on="year", how="inner").sort_values("year")
        for target_name, target_col in targets.items():
            if target_col not in merged.columns:
                rows.append(
                    {
                        "Region": spec.region,
                        "Target": target_name,
                        "Fuel": "ALL",
                        "Lags": np.nan,
                        "N": int(len(merged)),
                        "F Statistic": np.nan,
                        "P Value": np.nan,
                        "Note": f"Column {target_col} unavailable in macro data",
                    }
                )
                continue

            y = pd.to_numeric(merged[target_col], errors="coerce").diff().to_numpy()
            for fuel in FUEL_COLUMNS:
                x = np.log(pd.to_numeric(merged[fuel], errors="coerce")).diff().to_numpy()
                for lags in [1, 2]:
                    f_stat, p_val, used_lags, df_num, df_den = granger_f_test(y, x, lags)
                    rows.append(
                        {
                            "Region": spec.region,
                            "Target": target_name,
                            "Fuel": fuel,
                            "Lags": used_lags,
                            "N": int(np.sum(np.isfinite(y) & np.isfinite(x))),
                            "F Statistic": f_stat,
                            "P Value": p_val,
                            "DF Num": df_num,
                            "DF Den": df_den,
                            "Note": "First-differenced target; log-differenced fuel price",
                        }
                    )
    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "transmission_granger_diagnostics.csv", index=False)
    return out


def write_markdown_summary(
    cleaning: pd.DataFrame,
    stage1_existing: pd.DataFrame,
    stage1_strict: pd.DataFrame,
    holdout: pd.DataFrame,
    rolling: pd.DataFrame,
    sensitivity: pd.DataFrame,
    granger: pd.DataFrame,
) -> Path:
    summary_path = RESULT_DIR / "REVISION_EXPERIMENT_SUMMARY.md"

    holdout_summary = (
        holdout.groupby(["Region", "Feature Spec", "Model"], as_index=False)
        .agg(Mean_R2=("R2", "mean"), Median_R2=("R2", "median"), Mean_MAPE=("MAPE", "mean"), Mean_RMSE=("RMSE", "mean"))
        .sort_values(["Region", "Feature Spec", "Model"])
    )
    rolling_summary = (
        rolling.groupby(["Region", "Feature Spec"], as_index=False)
        .agg(
            Mean_R2=("R2", "mean"),
            Median_R2=("R2", "median"),
            Mean_MAPE=("MAPE", "mean"),
            Total_Folds=("R2", "size"),
            Valid_R2_Folds=("R2", "count"),
        )
        .sort_values(["Region", "Feature Spec"])
    )
    holdout_incremental = []
    for (region, project, fuel, model), group in holdout.groupby(["Region", "Project", "Fuel", "Model"]):
        values = {row["Feature Spec"]: row["R2"] for _, row in group.iterrows()}
        if "level_trend" in values and "time_only" in values:
            holdout_incremental.append(
                {
                    "Region": region,
                    "Project": project,
                    "Fuel": fuel,
                    "Model": model,
                    "LevelTrend minus TimeOnly R2": values["level_trend"] - values["time_only"],
                }
            )
    incremental_df = pd.DataFrame(holdout_incremental)
    if not incremental_df.empty:
        incremental_summary = (
            incremental_df.groupby(["Region", "Model"], as_index=False)
            .agg(
                Mean_Incremental_R2=("LevelTrend minus TimeOnly R2", "mean"),
                Median_Incremental_R2=("LevelTrend minus TimeOnly R2", "median"),
                Positive_Count=("LevelTrend minus TimeOnly R2", lambda x: int(np.sum(x > 0))),
                Total=("LevelTrend minus TimeOnly R2", "count"),
            )
            .sort_values(["Region", "Model"])
        )
    else:
        incremental_summary = pd.DataFrame()
    top_sensitivity = (
        sensitivity[sensitivity["Transition Project"]]
        .assign(abs_elasticity=lambda x: x["Elasticity_LogPrice"].abs())
        .sort_values("abs_elasticity", ascending=False)
        .head(12)
        .drop(columns=["abs_elasticity"])
    )
    granger_sig = granger[(granger["P Value"].notna()) & (granger["P Value"] < 0.10)].sort_values("P Value")

    def md_table(df: pd.DataFrame, max_rows: int = 20) -> str:
        if df.empty:
            return "_No rows._"
        shown = df.head(max_rows).copy()
        for col in shown.select_dtypes(include=[float]).columns:
            shown[col] = shown[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
        shown = shown.fillna("")
        headers = [str(col) for col in shown.columns]
        rows = [[str(value) for value in row] for row in shown.to_numpy()]
        widths = [
            max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i])
            for i in range(len(headers))
        ]

        def fmt_row(values: list[str]) -> str:
            return "| " + " | ".join(values[i].ljust(widths[i]) for i in range(len(values))) + " |"

        separator = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
        return "\n".join([fmt_row(headers), separator, *(fmt_row(row) for row in rows)])

    text = f"""# Revision Experiment Summary

Generated by `code/revision_experiments.py`.

## Input fixes

The raw WACC files are preserved. Cleaned, region-specific inputs were written to `data/revision_cleaned/`.

{md_table(cleaning)}

## Stage 1 forecast checks

Existing workbook metrics are renamed from LSTM-GRP to LSTM-GPR for terminology consistency. The near-exact-count column is included because very small errors can indicate that the original comparison should be documented as a strict time split.

{md_table(stage1_existing)}

Fixed-origin recursive baselines for oil prices, trained only through 2020 and forecast through 2024:

{md_table(stage1_strict)}

## Stage 3 holdout

Train period: 2026-01 to 2032-12. Test period: 2033-01 to 2035-12.

{md_table(holdout_summary, max_rows=60)}

Incremental out-of-sample R2 of adding fuel price and inflation to a time trend:

{md_table(incremental_summary, max_rows=20)}

## Rolling-origin robustness

Each fold trains through one year and tests the following calendar year.

{md_table(rolling_summary, max_rows=40)}

## Price-shock sensitivity

Log-linear elasticities estimate scenario sensitivity, not causal effects. The 10% shock column converts elasticity into an average WACC basis-point change around the sample mean.

{md_table(top_sensitivity, max_rows=20)}

## Transmission diagnostics

The Granger-style tests use first-differenced macro targets and log-differenced annual fuel prices. These are mechanism diagnostics, not causal identification.

{md_table(granger_sig, max_rows=30)}

## Recommended manuscript use

- Use holdout/rolling metrics for model evaluation, not the old train-set evaluation.
- Use elasticities or 10% price-shock deltas when discussing sensitivity. Do not interpret R2 as effect size.
- Describe the Granger results as preliminary transmission diagnostics.
- Keep the phrase LSTM-GPR throughout the manuscript.
"""
    summary_path.write_text(text, encoding="utf-8")
    return summary_path


def main() -> None:
    ensure_dirs()
    cleaning = build_cleaned_wacc_inputs()
    stage1_existing = summarize_stage1_existing_accuracy()
    stage1_strict = run_stage1_strict_baselines()
    holdout = run_stage3_holdout()
    rolling = run_stage3_rolling()
    sensitivity = run_stage3_sensitivity()
    granger = run_transmission_diagnostics()
    summary_path = write_markdown_summary(
        cleaning=cleaning,
        stage1_existing=stage1_existing,
        stage1_strict=stage1_strict,
        holdout=holdout,
        rolling=rolling,
        sensitivity=sensitivity,
        granger=granger,
    )
    print(f"Revision experiments complete. Summary: {summary_path}")


if __name__ == "__main__":
    main()
