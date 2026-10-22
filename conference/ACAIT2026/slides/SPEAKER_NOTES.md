# Speaker notes: approximately 15 minutes

Language: English. The 16-slide main deck contains 13 substantive slides, a title, selected references, and credits. Rehearse at approximately 110–120 words per minute, allowing pauses at the figures. Timings below total about 15 minutes.

## 1. Title — 0:00–0:25

Good morning. I am Shilin Ou from Duke Kunshan University. This work, with Luyao Zhang and Ming-Chun Huang, studies the relationship between fossil fuel prices and the financing cost of energy projects. We combine price forecasting, inflation prediction, and regional WACC analysis. The aim is to understand which patterns appear across regions and technologies, and how reliably those patterns transfer to later scenario years.

## 2. Financing conditions — 0:25–1:30

Renewable energy is often discussed in terms of equipment cost and technical performance. Financing is another important part of project economics. Wind and solar projects typically require substantial investment before they begin producing electricity. Investors and lenders need to recover that investment over many years.

The weighted average cost of capital, or WACC, combines the return required on debt with the return required on equity. The debt term includes the tax treatment of interest, and the leverage ratio determines the relative weight of the two sources. When financing becomes more expensive, a project generally needs more revenue to remain attractive.

Earlier energy-system studies show that regional financing assumptions can change modeled investment and decarbonization pathways. This motivates looking beyond a single global financing assumption.

## 3. Price signals and financing channels — 1:30–2:35

How might fossil fuel prices matter for renewable-project finance? There are several possible channels, and their directions need not be identical.

At the macroeconomic level, energy-price changes can affect inflation and the interest-rate environment. Those conditions matter for borrowing costs. At the project level, higher fossil fuel prices can change the relative competitiveness of renewable generation. Contract arrangements, counterparty risk, and investors' expectations can also matter.

The diagram summarizes these mechanisms as motivation for the analysis. Our comparison focuses on China, Europe, and the Middle East. These regions differ in energy-market exposure and institutional arrangements. We examine how the price and inflation inputs fit their WACC scenarios, then use additional diagnostics to assess the stability of the relationships.

## 4. Data — 2:35–3:35

The analysis connects three kinds of data. Historical monthly coal, oil, and natural gas prices supply the first forecasting stage. Macroeconomic indicators, including inflation, growth, unemployment, and interest-rate information, supply the regional inflation stage.

The WACC targets come from the model projections published by Calcaterra and colleagues. We align the regional inputs to a common monthly frame from 2026 to 2035, with 120 rows per region.

An important distinction is that these WACC values are future scenarios. They are not realized financing observations for the coming decade. The technology set includes renewables and other generation options, with coal and gas serving as conventional comparisons. This lets us organize the analysis consistently across regions, fuels, and technologies.

## 5. Framework — 3:35–4:45

The workflow has three stages. First, a sequence model produces a fuel-price path. It combines convolutional and recurrent representations with attention, followed by Gaussian-process smoothing.

Second, a regional inflation predictor combines an LSTM with a feed-forward network. We average five model outputs to reduce sensitivity to initialization. Price forecasts and inflation forecasts then supply the WACC stage.

Third, AutoGluon fits a regression for each combination of region, fuel, and technology. There are three regions, three fuels, and nine technology targets, giving 81 combinations. In each original regression, a single fuel-price variable and an inflation covariate are used together.

We also retain a separate set of chronological diagnostics. That separation is useful because fitting a projected path and predicting a later part of that path are different evaluation tasks.

## 6. Fuel-price model — 4:45–5:40

This slide gives a little more detail on the first stage. The sequence model uses a 12-month input window. Sine and cosine features represent the month of the year without creating a discontinuity between December and January.

The convolutional layer extracts local patterns. The recurrent layers represent temporal dependencies, and attention weights the resulting sequence representation. The Gaussian process then smooths the predicted path with an RBF kernel.

This provides a convenient forecast path for the downstream analysis. The Gaussian-process variance is conditional on that path, so a full uncertainty analysis would also need to account for uncertainty from the neural model and the later stages. The paper appendix records the implementation settings.

## 7. Archived oil-price comparison — 5:40–6:40

Here is the archived comparison for oil prices. The solid dark line is the actual series, and the blue line is the saved LSTM-GPR output. The other curves show selected comparison models.

Recomputing the metrics from the saved workbook gives an R-squared of 0.963 and a mean absolute percentage error of about 1.86 percent for LSTM-GPR. Its RMSE is approximately 2.416 dollars per barrel. It has the smallest errors among the archived outputs in that comparison.

There are 47 monthly observations in the saved 2021–2024 comparison. The repository preserves these outputs and a separate fixed-origin baseline exercise. Keeping those records separate makes the provenance of the reported comparison clear, rather than combining forecasts produced under different evaluation settings.

## 8. WACC fits and chronological checks — 6:40–7:40

For the WACC stage, the original AutoGluon implementation uses bagging and stacking to combine candidate models. It reports R-squared, MAPE, and RMSE on the same input rows used for fitting. Those metrics therefore describe in-sample fit.

The additional checks use cleaned regional inputs and simpler OLS or Ridge specifications. We train on 2026 through 2032 and test on 2033 through 2035. Rolling-origin folds provide another view of later-year stability.

A useful benchmark is a time trend. Both fuel forecasts and WACC scenarios can contain smooth trends. We therefore ask whether adding fuel prices and inflation supplies information beyond the passage of time. That comparison helps us interpret the regional fit results that follow.

## 9. Regional fit — 7:40–8:40

The original specifications show clear differences in average fit. Europe has a mean R-squared of about 0.670, China about 0.650, and the Middle East about 0.547. Percentage errors are also larger for the Middle Eastern specifications.

These numbers tell us how closely the joint fuel-price and inflation inputs fit the projected WACC series. They do not tell us how many basis points WACC changes when a fuel price increases. We estimate that kind of response separately in the sensitivity diagnostics.

The regional ordering gives us a starting point for comparing model behavior and financing contexts. To assess whether it generalizes, we need to look at technology differences and at the chronological tests.

## 10. Technology fit — 8:40–9:30

The heatmap averages the original fits across the three fuels for each region and technology. Darker cells indicate a stronger fit. The pattern for solar and wind is visible across the regional comparisons.

Averaging across all regions and fuels, solar has an R-squared of about 0.718, offshore wind about 0.706, and onshore wind about 0.700. The remaining technologies average around 0.58.

This suggests that a common modeling specification does not behave equally across technologies. It supports keeping the technology dimension in the analysis rather than reporting one pooled result for the entire energy sector. It also motivates investigating which technology-specific assumptions drive the differences.

## 11. Chronological checks — 9:30–10:50

The later-year checks give a more selective picture. The bars compare average holdout percentage errors for a time trend alone against a specification with fuel price, inflation, and a trend. Adding the extra variables does not consistently improve the average error.

The counts on the right report how often the extra inputs improve out-of-sample R-squared over the time trend. The counts are eight out of 27 for China, six for Europe, and six for the Middle East in the Ridge diagnostics.

This is a useful result in itself: the value of an energy-price signal depends on the region, technology, and specification. A small MAPE also needs context. When the held-out WACC values vary over a narrow range, a model can have a small percentage error while failing to beat a simple reference prediction. The benchmark comparison should therefore accompany the fit statistics.

## 12. Historical transmission diagnostics — 10:50–11:50

We also examine whether energy-price changes contain information about later macroeconomic conditions in historical data. The tests use changes in annual macroeconomic targets and log changes in annual fuel prices.

The displayed results include links between coal-price changes and China's real interest rate at one- and two-year lags, between gas-price changes and China's real interest rate at one year, and between gas-price changes and European inflation at two years.

These are selected exploratory diagnostics, with unadjusted p-values. The full tested set is available with the code. They help assess the plausibility of the macroeconomic channels in the motivation diagram. Establishing a project-level WACC effect would require richer financial observations and an appropriate identification design.

## 13. Regional financing questions — 11:50–13:00

The regional contexts suggest different next scenarios. For Europe, imported energy exposure and policy credibility motivate examining predictable revenue arrangements and risk-transfer instruments. For China, international spillovers interact with domestic energy-pricing rules and public financing. For oil-dependent economies, financing capacity and domestic pricing institutions matter for diversification.

These questions draw on the literature as well as the structure of our comparison. The present regressions do not estimate the effect of implementing a particular policy. Instead, they organize the assumptions that a more explicit financing-policy scenario would need.

The next analytical step is to connect these assumptions to project-level evidence and then to investment or energy-system outcomes. That would help translate a financing comparison into decisions about deployment, affordability, and risk allocation.

## 14. References — 13:00–13:20

These are four central references behind the study: work on regional financing constraints, the WACC scenario data, recurrent inflation forecasting, and renewable-energy finance policy. The complete checked bibliography is included with the paper and source package.

## 15. Credits — 13:20–13:45

I would like to acknowledge my coauthors and corresponding authors, Luyao Zhang and Ming-Chun Huang, and the funding and travel support listed here. These credits, author notes, and affiliations match the checked paper. The preparation statement also records the assistance used in the revision and LaTeX workflow.

## 16. Closing and exchange — 13:45–15:00

I will close with three points. First, the workflow connects fuel-price forecasts, inflation, and WACC scenarios in a reproducible comparison. Second, the original fits vary across regions and technologies, with solar and wind showing the strongest average fits. Third, chronological checks show that the added value of fuel-price signals is limited to a subset of specifications, which makes benchmarking an essential part of the interpretation.

The code and materials are available through the first QR code. The second links to the companion dataset snapshot. Corrected diagnostics and editable LaTeX sources are in the repository. My email is also shown here, and I would welcome discussion about project-level financing data, uncertainty propagation, and regional policy scenarios.

Thank you for listening. I look forward to your questions.

