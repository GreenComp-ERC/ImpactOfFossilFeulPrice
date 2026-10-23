# Reproducibility protocol

## Research scope

**Study:** Fossil Fuel Prices and Capital Cost: A Machine Learning Driven Study on Energy Transition. The code provides a transparent pipeline for scenario-based fossil-fuel price forecasting, regional inflation predictions, and weighted average cost of capital (WACC) analysis. This source repository is an artifact, not a new publication or proof of causal identification.

**Maintainers' workflow:** This personal repository is the contribution staging location; after review, selected code-only changes can be contributed to the `GreenComp-ERC` organization. The original author records and external source attributions must be preserved.

## Two distinct tiers of reproduction

| Tier | Objective | Scope | Evidence status |
| --- | --- | --- | --- |
| A: Diagnostic replication | Regenerate cleaned data, saved forecast checks, strict fixed-origin baselines, WACC holdout/rolling checks, shock sensitivities and Granger-style transmission diagnostics | `code/revision_experiments.py` and `data/` files | Deterministic analysis with pinned NumPy, pandas and openpyxl; tests exercise core arithmetic and data guards |
| B: Original model retraining | Retrain CNN/LSTM/GRU+GPR, recurrent inflation ensemble, and AutoGluon regressions | Historical `code/*.ipynb` and original data | **Not asserted**: exact original model checkpoints, training origins, environment and end-to-end rerun have not been re-established |

The source of `Impact_FossilFuel.ipynb` has been made region-selectable and its per-project AutoGluon model directories isolated. The historical default remains Middle East, and the original `time_limit=600` seconds, `best_quality` preset, and model hyperparameter configuration are preserved. Newly trained model checkpoints are deliberately written to untracked `outputs/`, not to this repository's archived results. The original notebook execution-log cells were cleared following portability corrections; earlier logs remain retrievable in Git history.

An earlier saved 2021–2024 LSTM-GPR forecast comparison is retained as a historical benchmark, **not** a verified uniformly trained fixed-origin comparison. The separate fixed-origin baselines use data no later than 2020 for training.

## Minimal reproducibility commands

Requirements: Python **3.11**, spreadsheet files under `data/`, and sufficient RAM for pandas. From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
python -m pip install -r code/requirements-revision.txt
python -m unittest discover -s code -p 'test_*.py' -v
python code/revision_experiments.py
```

If no graphical environment is available, the diagnostic command does not require a display or TensorFlow. To inspect existing results **without overwriting them**, first make a clean checkout or temporary worktree. The command writes to both `data/revision_cleaned/` and `data/revision_results/` and should not be run over files that need to be retained as an immutable audit record.

## Input–output lineage

| Stage | Input | Generated outputs |
| --- | --- | --- |
| Inflation correction | `data/inflation_forecasts_2026_2035.xlsx` and `data/{China_WACC,Euope_WACC,Middle_EAST_WACC}.xlsx` | `data/revision_cleaned/*cleaned.xlsx`, `data/revision_results/input_cleaning_report.csv` |
| Historical Stage 1 check | `data/Accuracy_Prediction-Model.xlsx` | `data/revision_results/stage1_existing_accuracy_metrics.csv` |
| Strict oil-price baselines | `data/Average_oil_price.xlsx` | `data/revision_results/stage1_strict_oil_baseline_{forecasts,metrics}.csv` |
| WACC validation | Region-specific cleaned workbooks | `data/revision_results/stage3_{holdout,rolling}_metrics.csv` |
| Price sensitivity | Region-specific cleaned workbooks | `data/revision_results/stage3_price_elasticities.csv` |
| Annual transmission diagnostics | `data/comprehensive_economic_data.xlsx` and commodity spreadsheets | `data/revision_results/transmission_granger_diagnostics.csv` |
| Reporting | Generated data frames | `data/revision_results/REVISION_EXPERIMENT_SUMMARY.md` |

The original workbooks remain unchanged. The WACC cleaned workbook covers **every month from 2026-01 through 2035-12** across China, Europe, and the Middle East; the region inflation workbook uses **annual** 2026–2035 scenarios and is merged many-to-one by year. Validation and sensitivity outputs use these projections, so later-year holdouts assess *internal scenario consistency*, not future observed predictive accuracy.

## Scientific integrity checks

- Report WACC as a decimal level (e.g., 0.08 for 8%); convert to basis points by multiplying differences by 10,000.
- The elasticity of log(WACC) with respect to log(fuel price) must reverse any feature standardization; `expm1(beta * log(1.1))` converts a 10% price-level shock to a proportional WACC change.
- Use separate train and test time windows; do not interpret in-sample AutoGluon fit as out-of-sample validation.
- The sequential bootstrap or GPR uncertainty of earlier stages is **not** fully propagated into Stage 3 results.
- Granger diagnostics remove missing observations **only after** constructing calendar-aligned lagged rows, to avoid collapsing absent years; results have no multiplicity correction and cannot establish causation.
- Preserve region name conventions and historical datasets; corrections should be documented rather than overwriting source records.

## Validation and contribution

`code/test_revision_sensitivity.py` checks known-coefficient elasticity and basis-point units, nonfinite/misaligned metric inputs, regressor dimensions, and time-series lag alignment with missing observations. Automated CI can run those tests separately from the original neural training. A clean complete run of `code/revision_experiments.py` is required before declaring regenerated outputs equivalent to the archived CSVs; numerical deltas must be reviewed and documented.

**Limitations:** the primary modeling notebooks were developed under a historical environment and retain research-specific implementation choices; the complete original training provenance has not been independently reconstructed. The existing archival results are not a guarantee that a new model training attempt would yield the same parameters or metrics.

**Licensing:** no explicit software LICENSE file is present in the current repository. The rights holder should select and add an appropriate license before inviting third-party reuse; do not assume MIT, Apache-2.0 or CC licensing from the presence of public files.

## References and credit

The upstream study cites World Bank price datasets and Calcaterra et al. (2024) for energy-finance modeling; see `data/README.md` and `CITATION.cff` for provenance and the official research record. OpenAI Codex assisted reference checking, consistency edits, figure-label corrections and sensitivity-code changes; the authors remain accountable for scientific claims and verification.
