# Reproducibility code change record — October 23, 2026

This record documents **code and artifact-integrity improvements** to the personal development repository. No manuscript sources were changed or introduced by this revision.

## Scientific and engineering changes

- `code/revision_experiments.py`: validate uniqueness and monthly continuity of WACC panels, annual inflation keys, and numeric inputs; align the archived inflation comparison by month rather than implicitly trusting row order.
- `code/revision_experiments.py`: reject misaligned or nonfinite metric/regression inputs; document undefined all-zero-target MAPE instead of producing an uninformative runtime warning.
- `code/revision_experiments.py`: preserve true calendar lags when missing observations are present in exploratory Granger-style transmission tests. Lag rows are formed *before* filtering incomplete observations, rather than joining nonadjacent years.
- `code/Price_Prediction.ipynb` and `code/Prediction_Inflation.ipynb`: remove machine-specific working-directory assumptions in favor of discovering checked-in `data/` from the repository root or `code/` directory.
- `code/test_revision_sensitivity.py`: add known-parameter elasticity, unit conversion, finite-input and missing-lag tests; `code/test_artifact_integrity.py` checks archived output keys, 120-month coverage, 81 price sensitivities, and correct basis-point calculations.
- `.github/workflows/reproducibility.yml`: run tests, notebook JSON checks and complete diagnostic regeneration under a pinned minimal Python 3.11 environment; save derived artifacts for review.
- Documentation: introduce a two-tier reproduction protocol and separate observed inputs from scenario projections, archived fits, and independently rerunnable diagnostic results.

## Interpretation and evidence limits

The original saved LSTM–GPR comparison and AutoGluon fits were **not retrained** in this revision. A successful regenerated diagnostic suite is not a verification of those original training checkpoints. Existing CSV outputs remain archived snapshots; differences after a fresh rerun must be examined and accepted explicitly before updating any manuscript.

## Outstanding publication-quality items

- Formal historical environment and model-checkpoint provenance for the original training notebooks.
- Strictly common training origins for historical model-to-model forecasting comparisons.
- Independent confirmation of external data licenses and repository code license selection by rights holders.
- Confirmation of numerical equality/tolerance between archived diagnostics and regenerated outputs on independent hardware, especially where missing-data Granger lag handling alters the effective sample.
