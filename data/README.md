# Data: sources, provenance and derived artifacts

This directory contains **observed historical commodity and macroeconomic inputs**, **published projection data**, **archived original-model outputs**, and **new diagnostic reanalysis**. These categories must not be confused. In particular, 2026–2035 WACC and inflation scenarios are *projections*, not realized observations; their later-year temporal holdouts are internal robustness checks, not verification against future ground truth.

## Reproduction-ready data inventory

| Location | Data role | Interpretation |
| --- | --- | --- |
| `Average_oil_price.xlsx`, `Average_Coal_Price.xlsx`, `Average_Gas_price.xlsx` | Historical fuel prices derived from World Bank commodity data | Source inputs for Stage 1 and annual transmission diagnostics |
| `comprehensive_economic_data.xlsx` | Historical regional macroeconomic indicators | Stage 2 input and transmission diagnostics |
| `CalcaterraEtAl_2024_NatEner_data_ED_fig22.csv` | Published scenario data from Calcaterra et al. (2024) | Upstream financing projection source; retain attribution |
| `China_WACC.xlsx`, `Euope_WACC.xlsx`, `Middle_EAST_WACC.xlsx` | Original region-level WACC workbooks | Source snapshot (original spelling retained deliberately) |
| `inflation_forecasts_2026_2035.xlsx` | Annual forecast inflation by region | Used to correct region-specific forecast covariates |
| `Accuracy_Prediction-Model.xlsx`, `Result.xlsx` | Archived original-model comparison / fits | Do not label these independent clean-room retraining results |
| `revision_cleaned/*.xlsx` | Corrected 2026-01 to 2035-12 monthly regional panels | Derived, reproducible diagnostics inputs |
| `revision_results/*.csv` | Independent forecast checks, holdout / rolling metrics, sensitivities, transmission diagnostics | Versioned derived results; regenerate with `code/revision_experiments.py` |

## Provenance and use

The principal upstream economic-finance model is Calcaterra et al. (2024), *Nature Energy*, DOI [10.1038/s41560-024-01606-7](https://doi.org/10.1038/s41560-024-01606-7). Historical commodity prices originate from the World Bank commodity-price collection. Users must observe upstream dataset licenses and attribution requirements; the repository does not assign new rights to third-party data.

The corrected panel uses a common 120-month horizon (2026-01 through 2035-12), aligns annual regional inflation forecasts by calendar year, preserves original workbooks, and reports the corrections separately. Europe and Middle East forecast inflation values were corrected from a prior use of China's inflation series. Archived AutoGluon fit values are **not** retrained using these cleaned inputs; OLS/Ridge diagnostics are separately labeled.

To regenerate diagnostics, run `python code/revision_experiments.py` from repository root after installing `code/requirements-revision.txt`. See [`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md) for validation and caveats. **Running the pipeline overwrites derived files**. The legacy data dictionary below includes historically referenced notebook-generated intermediate outputs that may not be committed to this repository; check file existence before relying on them.

## Data Dictionary

| **Variable Name**                         | **Data Type** | **Description**                                  | **Source File**           | **Unit** | **Range**                  | **Remarks**                                      |
|-------------------------------------------|---------------|--------------------------------------------------|---------------------------|----------|----------------------------|--------------------------------------------------|
| Year_month                                | String        | Time period in Year-Month format                 | Average_Coal_Price.xlsx   | N/A      | 1960 to 2024        | Time period of coal price data                  |
| Coal, Australian Coal                     | Float         | Price of Australian Coal                         | Average_Coal_Price.xlsx   | $/mt     | Varies by month and year   | Coal price in Australian market                 |
| South African ** Average Coal Price       | Float         | Price of South African Coal                      | Average_Coal_Price.xlsx   | $/mt     | Varies by month and year   | Coal price in South African market              |
| Year_Month                                | String        | Time period in Year-Month format                 | Average_Gas_price.xlsx    | N/A      | 1960M01 to present         | Time period of gas price data                   |
| Natural gas, US                           | Float         | Natural gas price in the US                      | Average_Gas_price.xlsx    | $/mmbtu  | Varies by month and year   | Price of natural gas in US market               |
| Year_Month                                | String        | Time period in Year-Month format                 | Average_oil_price.xlsx    | N/A      | 1960M01 to present         | Time period of oil price data                   |
| Oil Price, US                             | Float         | Price of oil in the US                           | Average_oil_price.xlsx    | $/bbl    | Varies by month and year   | Price of oil in US market                       |
| Date                                      | String        | Date of prediction                               | coal_price_predictions_with_confidence_intervals2.xlsx | N/A      | Future dates starting from 2025 | Monthly predictions of coal prices              |
| Prediction                                | Float         | Predicted coal price                             | coal_price_predictions_with_confidence_intervals2.xlsx | $/mt     | Varies based on prediction date | Predicted price of coal                         |
| CI Lower                                  | Float         | Lower bound of the 95% confidence interval for coal price | coal_price_predictions_with_confidence_intervals2.xlsx | $/mt     | Varies based on prediction date | Lower bound of the confidence interval for the prediction |
| CI Upper                                  | Float         | Upper bound of the 95% confidence interval for coal price | coal_price_predictions_with_confidence_intervals2.xlsx | $/mt     | Varies based on prediction date | Upper bound of the confidence interval for the prediction |
| Date                                      | String        | Date of prediction                               | natural_gas_price_predictions_with_confidence_intervals.xlsx | N/A      | Future dates starting from 2025 | Monthly predictions of natural gas prices       |
| Prediction                                | Float         | Predicted natural gas price                      | natural_gas_price_predictions_with_confidence_intervals.xlsx | $/mmbtu  | Varies based on prediction date | Predicted price of natural gas                  |
| CI Lower                                  | Float         | Lower bound of the 95% confidence interval for natural gas price | natural_gas_price_predictions_with_confidence_intervals.xlsx | $/mmbtu  | Varies based on prediction date | Lower bound of the confidence interval for the prediction |
| CI Upper                                  | Float         | Upper bound of the 95% confidence interval for natural gas price | natural_gas_price_predictions_with_confidence_intervals.xlsx | $/mmbtu  | Varies based on prediction date | Upper bound of the confidence interval for the prediction |
| Date                                      | String        | Date of prediction                               | oil-predictions_with_confidence_intervals.xlsx | N/A      | Future dates starting from 2025 | Monthly predictions of oil prices               |
| Prediction                                | Float         | Predicted oil price                              | oil-predictions_with_confidence_intervals.xlsx | $/bbl    | Varies based on prediction date | Predicted price of oil                          |
| CI Lower                                  | Float         | Lower bound of the 95% confidence interval for oil price | oil-predictions_with_confidence_intervals.xlsx | $/bbl    | Varies based on prediction date | Lower bound of the confidence interval for the prediction |
| CI Upper                                  | Float         | Upper bound of the 95% confidence interval for oil price | oil-predictions_with_confidence_intervals.xlsx | $/bbl    | Varies based on prediction date | Upper bound of the confidence interval for the prediction |
| Region                                    | String        | Geographical region for the scenario             | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | Africa, etc.                | Region for each scenario                        |
| Scenario                                  | String        | Scenario type for the model                      | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | CoC-reference, etc.         | Scenario type for each region                  |
| Variable                                  | String        | Model variable                                   | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | Onshore, etc.               | The variable for each region and scenario       |
| Year                                      | Integer       | Year of the prediction                           | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | Year     | 2020, 2025, 2030, etc.      | Year for which the data is predicted           |
| scengroup                                 | String        | The grouping of the scenario                     | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | NDC, etc.                   | The scenario group                              |
| IMACLIM                                   | Float         | Prediction based on the IMACLIM model            | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | Varies by year and scenario | Prediction from the IMACLIM model              |
| IMAGE                                     | Float         | Prediction based on the IMAGE model              | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | Varies by year and scenario | Prediction from the IMAGE model                |
| WITCH                                     | Float         | Prediction based on the WITCH model              | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | Varies by year and scenario | Prediction from the WITCH model                |
| maxwacc                                   | Float         | Maximum value for the weighted average cost of capital | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | Varies by year and scenario | Maximum value for the weighted average cost of capital |
| minwacc                                   | Float         | Minimum value for the weighted average cost of capital | CalcaterraEtAl_2024_NatEner_data_ED_fig22.xlsx | N/A      | Varies by year and scenario | Minimum value for the weighted average cost of capital |
| Region                                    | String        | Region where the energy project is located       | Result.xlsx               | N/A      | Transition Countries, etc.  | Geographical region for energy project evaluation |
| Energy                                    | String        | Type of energy                                   | Result.xlsx               | N/A      | Oil, Gas, Coal              | Type of energy for the project                  |
| Project                                   | String        | Type of energy project                           | Result.xlsx               | N/A      | Onshore, CCS, Nuclear, etc. | Type of energy project                          |
| R²                                        | Float         | Coefficient of determination (R squared) for the energy project | Result.xlsx               | N/A      | 0 to 1                     | Goodness of fit for the model                   |
| RMSE                                      | Float         | Root Mean Square Error for the energy project    | Result.xlsx               | N/A      | Positive values            | Measures the accuracy of the model              |
| MAE                                       | Float         | Mean Absolute Error for the energy project       | Result.xlsx               | N/A      | Positive values            | Measures the average magnitude of errors        |
| Year                                      | Integer       | Year of prediction                               | China+_WACC_And_Predicted_Price.xlsx | Year     | 2020, 2025, 2030, etc.      | Year for which the data is predicted           |
| Scenario                                  | String        | Scenario type for the model                      | China+_WACC_And_Predicted_Price.xlsx | N/A      | CoC-reference, etc.         | Scenario type for each region                  |
| Onshore                                   | Float         | WACC or predicted price for onshore projects     | China+_WACC_And_Predicted_Price.xlsx | N/A      | Varies by year and scenario | WACC or predicted price for onshore projects   |
| Offshore                                  | Float         | WACC or predicted price for offshore projects    | China+_WACC_And_Predicted_Price.xlsx | N/A      | Varies by year and scenario | WACC or predicted price for offshore projects  |
| Nuclear                                   | Float         | WACC or predicted price for nuclear projects     | China+_WACC_And_Predicted_Price.xlsx | N/A      | Varies by year and scenario | WACC or predicted price for nuclear projects    |
| CCS                                       | Float         | WACC or predicted price for CCS projects         | China+_WACC_And_Predicted_Price.xlsx | N/A      | Varies by year and scenario | WACC or predicted price for CSS projects    |

