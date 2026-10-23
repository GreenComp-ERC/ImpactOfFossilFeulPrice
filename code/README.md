# Reproducible analysis

This directory contains the computational workflow for **Fossil Fuel Prices and Capital Cost: A Machine Learning Driven Study on Energy Transition** (Ou, Zhang, and Huang). It distinguishes the original three-stage model notebooks from later verification and sensitivity diagnostics. Both parts are research artifacts; **the diagnostic reanalysis does not amount to rerunning or validating the original neural-network and AutoGluon training**.

## Quick start: auditable diagnostics

From the root of this checkout:

```bash
python3.11 -m venv .venv
source .venv/bin/activate              # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -r code/requirements-revision.txt
python -m unittest discover -s code -p "test_*.py" -v
python code/revision_experiments.py
```

The diagnostic dependencies are deliberately minimal and pinned. The command reads checked-in spreadsheets in `data/` and writes cleaned workbooks to `data/revision_cleaned/` and CSV/Markdown outputs to `data/revision_results/`. **It overwrites those generated paths**; use a separate working branch or clean checkout when comparing against archived outputs. No manuscript files are needed or generated.

The complete analysis performs (1) regional inflation-input corrections, (2) saved Stage 1 accuracy-workbook remeasurement, (3) independent fixed-origin oil baseline experiments, (4) Stage 3 time holdout and rolling-origin OLS/Ridge checks, (5) log-linear WACC price-shock sensitivity, and (6) Granger-style preliminary transmission diagnostics. The executable script is [`revision_experiments.py`](revision_experiments.py); the unit tests are [`test_revision_sensitivity.py`](test_revision_sensitivity.py).

## Three original modeling stages

| Stage | Source | Function | Output / evidence boundary |
| --- | --- | --- | --- |
| Input preparation | [`Price_Data_Processing.ipynb`](Price_Data_Processing.ipynb), [`WACC_Data_processing.ipynb`](WACC_Data_processing.ipynb) | Historical commodity prices; scenario WACC processing | Intermediate inputs; some cells reflect the original workstation layout |
| 1: fuel-price forecasting | [`Price_Prediction.ipynb`](Price_Prediction.ipynb) | CNN / LSTM / GRU with GPR refinement | Forecast artifact; archived model-comparison workbook has incomplete common-origin provenance |
| 2: inflation | [`Prediction_Inflation.ipynb`](Prediction_Inflation.ipynb) | Recurrent model ensemble with country/region inputs | Annual 2026–2035 inflation scenarios |
| 3: WACC | [`Impact_FossilFuel.ipynb`](Impact_FossilFuel.ipynb) | AutoGluon regional / fuel / project regressions | Archived model-fit results; **in-sample** and not equal to independent holdout performance |

The original modeling notebooks have substantially heavier requirements (TensorFlow/Keras, scikit-learn, AutoGluon, Matplotlib, and Jupyter) than the minimal diagnostic environment. Their exact historical training environment is not fully locked or reconstructed, so running the diagnostic environment **does not guarantee** reproducibility of the neural-network training runs. Historical notebook outputs remain archival evidence.

## Data and execution notes

- Input spreadsheets and outputs are indexed in [`../data/README.md`](../data/README.md).
- Run notebooks from the repository root or `code/` where supported; `Price_Prediction.ipynb` and `Prediction_Inflation.ipynb` resolve `data/` relative to those locations rather than using personal desktop paths.
- The intentionally preserved original notebook names and raw input filenames include legacy spelling (for example `Euope_WACC.xlsx`). **Do not rename without updating all references and tests.**
- Region-specific forecast inflation is aligned on year and checked against every calendar month in the 2026–2035 panel. Code now refuses duplicate months, missing panel values, and ambiguous annual inflation keys instead of silently producing numbers.
- Corrected elasticity conversion uses a coefficient in **original log-price units**, then computes `mean_WACC * expm1(elasticity * log(1.1)) * 10000` basis points. A synthetic-data test verifies the units.
- The Granger-style diagnostics are exploratory association checks (not causal identification), and p-values are not adjusted for multiple comparisons. Missing calendar observations must not be compressed into adjacent lags.
- Forecast scenarios for years after the observed sample are **not realized outcomes**. Sensitivity checks and time-series validation address model interpretation, not identification of causal effects.

## Results and scope

The current `data/revision_results/` directory stores **archived generated diagnostic results**. The updated script validates additional input invariants and corrects lag handling under missing data. Re-run the script before assuming the tracked CSVs and newly generated outputs are byte-identical. The prior published numbers must not be silently replaced without checking changes and adjusting accompanying interpretations.

The reproducibility scope and source dependencies are further described in [`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md). Cite the linked research record via [`../CITATION.cff`](../CITATION.cff); see the original [system configuration notebook](System%20Configuration%20Report.ipynb) for historical execution details.

## Attribution

Research: Shilin Ou, Luyao Zhang, and Ming-Chun Huang (Duke Kunshan University). Data sources and upstream research include World Bank commodity statistics and the Calcaterra et al. (2024) financing dataset, subject to their original provenance and terms. OpenAI Codex contributed editorial and diagnostic-code assistance; the human authors remain responsible for model assumptions, code, evidence, and conclusions.
