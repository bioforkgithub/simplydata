# simplydata

[![PyPI](https://img.shields.io/pypi/v/simplydata)](https://pypi.org/project/simplydata/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24210045.svg)](https://doi.org/10.5281/zenodo.24210045)

**Learn basic Python, and simplydata takes you from your first table to publication-ready statistics, in plain words, with every number checked against the field's standard tools.**

*simplydata is a package that is easy for a beginner, honest with a reviewer, and [safe for patient data](#privacy-your-data-stays-on-your-computer), all at once.*

**Simple words for data science in Python.** One small vocabulary you can learn in a day,
built on matplotlib, seaborn, pandas, Polars, NumPy, SciPy and statsmodels (with narwhals linking
pandas and Polars), and on R through rpy2 for the methods only R has, so you don't have to learn
them first.

## What simplydata handles

**398 words (commands) in 48 groups, with 373 different options, on top of 14 Python packages and
86 R packages that it runs (plus R's own `stats`, and 8 more used only to check its answers), checked by 1316 reliability checks.** Every word hands the work to
an established package; simplydata chooses the settings, prints the answer in words and names the
method it used. Words that need an extra say so: `pip install "simplydata[fast]"`, `[files]`,
`[systems]` or `[r]` (the R words also need R itself; see [Using the words that need R](#using-the-words-that-need-r)).

### How much simplydata reduces the problem

Approximate, counted on 2026-11-21.

| | With the packages underneath | With simplydata |
|---|---|---|
| Names to learn | about 10,650 functions: about 5,460 in the Python packages (SciPy about 1,750, pandas 850, Polars 815, matplotlib 745, NumPy 660, statsmodels 545, seaborn 100; each package's public API) and about 5,190 exported by the R packages simplydata ran that day, with R's `stats` (R `getNamespaceExports`; before the community packages were added) | 771 names: 398 commands and 373 options, about 93 % fewer |
| Packages and languages | 86 packages (14 Python, 72 R), in Python and R | 1 package, in basic Python |
| Code per task | 1163 lines and 1221 function calls in the 180 tasks of the manual's "same underneath" boxes (median 6 lines a task); this library code is the bare minimum, without the plain-sentence result or the checks | 520 lines and 634 calls (median 3 lines a task), about 55 % fewer lines; recount with `python validation/count_reduction.py` |
| Choosing the method | you choose, from the package's documentation | the recommended default, with its published basis: see [How simplydata chooses methods](#how-simplydata-chooses-methods) |

### Packages underneath

Python packages:

| Package | What simplydata does with it | Needs |
|---|---|---|
| pandas | the tables behind `sdata.table`: reading files, choosing rows and columns, cleaning, grouping, joining and reshaping (`keep_rows_where`, `fill_empty_cells_in`, `join_with`, `turn_columns_into_rows`); `table.as_pandas()` hands the table back | built in |
| Polars | the same table words on a fast engine for big data: `sdata.table(..., fast=True)`, `table.as_polars()` | [fast] |
| pyarrow | Parquet files (`sdata.table("file.parquet")`, `table.save("clean.parquet")`) and passing tables between Polars and pandas | [fast] |
| narwhals | lets every table word run on pandas or Polars alike | built in |
| NumPy | the number words: `sdata.numbers`, `sdata.number_grid`, maths in words (`take_log`, `turn_into_running_total`), random numbers, `nums.as_numpy()` | built in |
| SciPy | tests (t-tests, ANOVA, rank tests, chi-square, Fisher, Kolmogorov-Smirnov, Shapiro-Wilk), 28 named distributions (with the GEV and generalised Pareto curves of extremes) and any other `scipy.stats` one (`sdata.distribution`), fitting and solving (`fit_formula`, `solve`, `find_where_smallest`), values between points (`values_at`, `make_map_of`), bootstrap intervals (`find_interval_of`), the average direction of directions or times of day (`find_average_direction_of`), distances and clusters, spectra, filters, peaks, the Hilbert envelope and the Fourier transform (`find_spectrum_of`, `add_filtered_column`, `find_each_peak_that`, `find_envelope`), linear systems (`sdata.system`) | built in |
| statsmodels (with its formula helper patsy) | models in `explain`: linear, logistic, Poisson, negative binomial, Gamma, ordered, multinomial, mixed models, GEE, robust regression, conditional logistic; Welch's ANOVA, corrections for many tests, kappa, exact intervals of percents and rates (`rate_of`, `compare_to_truth`), PCA, lowess and STL (`add_trend_and_season`), power of regression and of two percents, multiple-imputation fits | built in |
| matplotlib | every chart's canvas (`sdata.chart`), pie, polar, contour, surface and 3D charts, titles, axes, legends, several charts on one page, `animate` | built in |
| seaborn | bars, lines, dots, histograms, boxes, violins, heatmaps, density curves, count bars and cumulative shares (`draw_bars`, `draw_lines`, `draw_boxes`, `draw_violins`, `draw_heatmap`, `draw_density`), with averages and error bars (`show="average", error="standard error"`) |
| openpyxl | reading and saving Excel files (`sdata.table("file.xlsx", sheet="all")`, `table.save("clean.xlsx")`) | built in |
| python-docx, pyreadstat | reading tables from Word files (`table_number=`) and from SPSS and Stata files | [files] |
| python-control | rise time, settling time and overshoot of `system.step_response()`; gain and phase margins of `system.frequency_response()` | [systems] |
| rpy2 | the bridge to R: runs the R package itself and brings the answer back | [r] |

R packages that simplydata runs, where Python has no method of its own or none that gives R's answer (all need `[r]` and R):

| Package | What simplydata does with it | Needs |
|---|---|---|
| stats (comes with R) | k-means (`add_clusters`), smoothing splines (`draw_smooth_line(method="spline")`), the fixed-season STL and the running median, profile-likelihood intervals (`explain(interval_by="profile")`), exact Fisher tests of big tables, the Quade test, R's self-starting curves (`fit_curve(of_kind="logistic growth")`), Holt-Winters and ARIMA forecasts (`forecast`) | [r] |
| car, effectsize | ANOVA tables (`explain(test_type="type 2")`), variance inflation factors (`check_model_of`), the best power of a model's leftovers (`find_best_power_of(using=)`); effect sizes with intervals (Hedges' g, omega-squared, partial eta-squared, Kendall's W, Cramer's V, standardised effects) | [r] |
| lme4, lmerTest, pbkrtest, performance | mixed models for numbers, yes/no and counts (`explain(grouped_by=, own_slope_for=, crossed_with=)`), Satterthwaite and Kenward-Roger degrees of freedom, each group's own level (`find_group_levels_of`), groups that pull the model (`show_rows_that_pull_model`), Nakagawa's R squared | [r] |
| emmeans, afex, nlme | model averages and their pairs (`find_model_averages_of`); repeated-measures ANOVA (`compare_averages_of(matched_by=)`); generalised least squares with unequal spread or AR(1) neighbours (`explain(spread_changes_with=, neighbours_alike_in_order_of=)`) | [r] |
| MASS, nnet, betareg, pscl | negative binomial, ordered and multinomial models when R refits them; axes that separate groups, LDA (`add_axes_that_separate_groups`); beta regression for shares (`explain(outcome="shares")`); zero-inflated and hurdle counts (`outcome="counts with many zeros"`, `"counts in two steps"`) | [r] |
| WeightIt, MatchIt, cobalt, lmtest | groups made alike in other columns before they are compared: propensity scores, weighting and matching, with the balance table (`compare_balanced_groups_of`, `method="matching"`, `match_within=`) | [r] |
| geepack, mgcv, sandwich, quantreg | GEE with rows in time order (`explain(effects="for the whole population", within_groups="in time order")`); smooth curves in a model, GAM (`explain(curve_for=)`); robust standard errors of GLMs (`robust_errors=True`); quantile regression (`explain(for_percentile=90)`) | [r] |
| mice, miceadds, glmnet, boot | pooling multiple imputation (`explain(empty_cells="multiple imputation")`, also `explain_survival` and, with miceadds, `find_correlation_between`); the lasso and elastic net (`find_columns_that_predict`); checking models on left-out rows (`compare_models(check_on_left_out_rows=True)`) | [r] |
| drc, segmented, smatr, mcr | dose-response curves and ED50 (`fit_dose_response`); lines that bend (`fit_line(with_bends=1)`); standardised major axis lines (`fit_line(method="standardised major axis")`); Deming and Passing-Bablok lines for comparing two methods (`fit_line(method="deming")`) | [r] |
| pwr, TOSTER, presize, gsDesign, powerSurvEpi, pwrss | sample size and power (`sdata.find_how_many_needed`, `sdata.find_chance_of_finding`) for ANOVA, chi-square, correlations, equivalence, interval width, survival (Schoenfeld, Freedman) and logistic regression | [r] |
| Exact, exact2x2, BSDA, nortest | Barnard's and Boschloo's tests (`compare_counts_of(test="barnard")`); the exact interval of McNemar's test; the z-test and the t-test from averages alone (`sdata.compare_averages`); the Lilliefors test (`compare_shape_to(test="lilliefors")`) | [r] |
| DescTools, rstatix, FSA, PMCMRplus, multcompView | intervals of medians, quantiles and percents; Scheffe, Games-Howell, Dunn's and Conover's pair tests (`compare_each_pair_of(test=)`), and Nemenyi's and Conover's after Friedman's test (`compare_each_pair_of(matched_by=, test="nemenyi")`); letters for groups that do not differ (`show="letters"`); Somers', Goodman-Kruskal and Lin's measures | [r] |
| ppcor, cocor, outliers, EnvStats | partial correlation (`find_correlation_between(allowing_for=)`); comparing two correlations (`compare_correlations`); Grubbs', Dixon's and Rosner's outlier tests (`show_rows_with_outliers(rule="grubbs")`) | [r] |
| epiR, pROC | Mantel-Haenszel risk ratios (`compare_risks(allowing_for=)`), attributable fractions (`compare_risks(show="attributable fractions")`), directly and indirectly standardised rates (`rate_of(standard_population=)`, `compare_rates(standard_rates=)`) and likelihood ratios of a diagnostic test (`compare_to_truth`); ROC curves, AUC and DeLong's test (`compare_to_truth`, `compare_accuracy`, `chart.trade_off_curve`) | [r] |
| irr, psych, BlandAltmanLeh | ICC, Krippendorff's alpha, Fleiss' kappa p-value (`agreement_between`); Cronbach's alpha (`reliability_of`); exploratory factor analysis with parallel analysis and the KMO (`find_hidden_factors_behind`); Bland-Altman limits (`limits_of_agreement`, `chart.difference_dots`) | [r] |
| GPArotation, lavaan | the oblimin rotation of psych's factor analysis (`find_hidden_factors_behind`); confirmatory factor analysis and models with paths between hidden factors, with CFI, TLI, RMSEA and SRMR (`check_hidden_factors`) | [r] |
| survival, cmprsk, adjustedCurves, riskRegression, KMsurv, survRM2 | the Cox proportional-hazards check and Harrell's C, parametric survival models (`explain_survival(distribution="weibull")`), conditional logistic regression, Aalen-Johansen risks (`find_risk_over_time`); Gray's test and Fine-Gray models (`competing_with=`); adjusted survival curves (`find_survival_over_time(allowing_for=)`); life tables (`method="life table"`); restricted mean survival time (`compare_survival(average_time_up_to=)`) | [r] |
| metafor | meta-analysis (`combine_studies`): random and common effects, Hartung-Knapp, subgroups, meta-regression, Egger's and Peters' tests, trim and fill; `chart.forest_plot`, `chart.draw_funnel_plot` | [r] |
| vegan | NMDS (`add_nmds`); PERMANOVA and its spread check, ANOSIM and SIMPER (`compare_profiles_of(method="anosim")`, `show="contributions"`); diversity: richness, Shannon, Simpson, Chao1, Hill numbers and rarefaction (`add_diversity_columns`, `chart.draw_richness_curves`); Aitchison and Hellinger distances; PCoA (`add_principal_coordinates`); RDA, db-RDA and CCA (`explain_profiles_of`); Mantel and Procrustes (`find_correlation_between_profiles`); correspondence analysis (`add_correspondence_axes`) | [r] |
| zCompositions, compositions | zeros replaced by estimated small values, then log ratios: clr, alr, ilr (`add_log_ratio_columns`) | [r] |
| cluster, ca | silhouette widths of clusters (`add_clusters(show="silhouette")`); multiple correspondence analysis of text columns (`add_correspondence_axes`) | [r] |
| circular | the Rayleigh test: is there a preferred direction, or are the directions spread evenly around the circle (`compare_shape_to(shape="even around the circle", full_turn=360)`), always with the units given | [r] |
| spdep, sf | Moran's I: are the values of nearby places alike, with 1 / distance or nearest-neighbour weights and a permutation p-value (`find_autocorrelation_of(x=, y=)`, `on_globe=True` for longitude and latitude) | [r] |
| gstat | the variogram and its fitted curve: range, nugget and sill (`find_variogram_of`, `chart.draw_variogram`) | [r] |
| extRemes | return levels with profile-likelihood intervals: GEV for yearly maxima, generalised Pareto above a threshold (`find_return_levels_of(once_in=[10, 100])`, `values_above=`); the extremal index; the threshold check (`chart.draw_threshold_check`) | [r] |
| qvalue | Storey's q-values and the local false discovery rate for many tests, such as genes (`add_adjusted_p_value_column(method="storey")`, `method="local fdr"`); from Bioconductor (in R: `install.packages("BiocManager")`, then install qvalue with it) | [r] |
| agricolae | design tables for experiments: every combination in random order, randomised blocks, latin squares and split plots (`sdata.make_design_table`) | [r] |
| blockrand | randomisation lists in random blocks, one list for each centre (`sdata.make_random_assignments`); CRAN only | [r] |
| survey | survey-weighted averages, totals, percentiles, percents, population counts, models and tests with strata, clusters and population sizes (`table.use_survey_design`) | [r] |
| BayesFactor | Bayes factors with credible intervals instead of p-values, for two averages, before and after, one average, a correlation and a table of counts (`bayesian=True`, `prior_width=`) | [r] |
| rstanarm, rstan, posterior | Bayesian models and mixed models with their priors, credible intervals, R-hat and effective draws (`explain(bayesian=True)`), and the posterior and prior predictive checks (`check_model_of(bayesian=True)`, `show="prior check"`); rstanarm is large (about 400 MB with Stan) and comes ready-made for Windows, macOS and Linux (Posit's package manager) | [r] |
| trend, tseries, urca, forecast, changepoint, lomb | the Mann-Kendall test and Sen's slope (`find_trend_of`); ADF and KPSS tests (`check_steady_over_time`); forecasts and their check on held-back readings (`forecast`, `compare_forecasts_for`), with the ARIMA order chosen by auto.arima (`order="automatic"`); change points (`find_change_points_in`); the Lomb-Scargle spectrum of uneven readings (`find_spectrum_of(method="lomb-scargle")`) | [r] |

R packages used only to check simplydata's answers, in the tests and the
[reliability study](https://github.com/bioforkgithub/simplydata/blob/main/validation/report.md); no word runs them,
so you never need them:

| Package | What the checks use it for |
|---|---|
| deming | a second check of the Deming line of `fit_line(method="deming")`, next to mcr |
| epitools | a second package for directly and indirectly standardised rates (`ageadjust.direct`, `ageadjust.indirect`) that `rate_of(standard_population=)` and `compare_rates(standard_rates=)` are checked against |
| AICcmodavg | the AICc table and Akaike weights that `compare_models(using=[[...], [...]])` is checked against |
| meta, metadat | a second meta-analysis package, and the published study data (BCG vaccine, passive smoking), that `combine_studies` is checked against |
| ismev, sp | the published data of Coles (2001: Port Pirie sea levels, daily rain) and the meuse soil samples that `find_return_levels_of`, `find_autocorrelation_of(x=, y=)` and `find_variogram_of` are checked against |
| ape | a second Moran's I (`ape::Moran.I`) that `find_autocorrelation_of(x=, y=)` is checked against |

Many printouts also name the R function that gives the same answer ("as R zoo::na.spline"); those are pointers for
R users, not packages simplydata needs.

### By task

| Task | What you can do | Example words |
|---|---|---|
| Reading and saving tables | read Excel (one sheet or all), CSV, TSV, Parquet, JSON, Word, SPSS and Stata files, several files at once or a file on the web; save as Excel, CSV, TSV, Parquet or JSON | `sdata.table("data/*.csv")`, `sdata.table("file.xlsx", sheet="all")`, `table.save("clean.xlsx")` |
| Looking and choosing | see the first rows and each column; keep or remove columns and rows by condition, position, random draw (within each group too) or biggest values | `show_first_rows`, `describe_columns`, `keep_rows_where`, `keep_columns`, `keep_random_rows`, `keep_biggest_rows` |
| Cleaning | turn text into numbers or dates, fix spaces and case, replace values, round, remove duplicates, show or remove outliers | `turn_into_numbers`, `turn_into_dates`, `remove_extra_spaces_in`, `replace_values_in`, `remove_duplicate_rows`, `show_rows_with_outliers` |
| Empty cells (missing data) | count them, find which are empty together (patterns), map them, remove rows, fill with a value, average, median, neighbour, a straight line or a smooth curve; fill missing dates; multiple imputation in a model, a Cox model or a correlation | `count_empty_cells_in`, `draw_map_of_empty_cells`, `fill_empty_cells_in(with_the="line between neighbours")`, `add_missing_dates`, `explain(empty_cells="multiple imputation")` |
| New columns, dates and text | groups from numbers, ranks, z-scores, parts of dates and text, rolling values, previous values and changes | `add_group_column`, `add_rank_column`, `add_z_score_column`, `add_column_with_part_of_date`, `split_column`, `add_rolling_column`, `add_change_column` |
| Reshaping and joining | join two tables, stack rows, turn columns into rows and back, undo any step | `join_with`, `add_rows_from`, `turn_columns_into_rows`, `turn_rows_into_columns`, `undo`, `show_steps` |
| Summaries | counts, averages, medians, totals, percentiles, standard deviations (weighted too), intervals for any summary (bootstrap), correlations (Pearson, Spearman, Kendall, partial) and covariances; answers on a scale (Likert items) | `count_each`, `find_summary_of`, `find_percentile_of`, `find_interval_of`, `find_correlation_between` |
| Charts | bars, lines, dots, area, histograms, boxes, violins, heatmaps, pie, polar, contour, surface, 3D dots, bands, sticks, density, Q-Q dots, all pairs, survival and risk curves, forest and funnel plots, richness curves, cluster trees, variograms, threshold checks, compass charts, diverging bars of answers on a scale, spectra; lines, labels, axes, colours, legends, side by side, animation | `draw_bars`, `draw_boxes`, `draw_heatmap`, `draw_contour`, `draw_qq_dots`, `sdata.draw_all_pairs`, `draw_richness_curves`, `draw_cluster_tree`, `draw_one_chart_for_each_group_in`, `animate` |
| Comparing groups (tests) | two or more averages (Welch, Student, ANOVA, Yuen, Brunner-Munzel, rank tests), pairs of groups (Holm, Tukey, Games-Howell, Dunn, Dunnett, pairs of percents), before and after, repeated measures (Friedman with Nemenyi or Conover after it, repeated-measures ANOVA), spreads, shapes, counts (chi-square, Fisher, G-test, trend), percents, equivalence and non-inferiority, many tests at once (Holm, Benjamini-Hochberg, Storey's q-values); Bayes factors and credible intervals (`bayesian=True`) | `compare_averages_of`, `compare_each_pair_of`, `compare_before_and_after`, `compare_matched_columns`, `compare_spreads_of`, `compare_counts_of`, `compare_percent_to`, `add_adjusted_p_value_column` |
| Relationships and models | linear, logistic, Poisson, negative binomial, Gamma, ordered, multinomial, beta, zero-inflated and hurdle models; mixed models and GEE; GAMs, splines, quantile and robust regression; GLS; interrupted time series; Bayesian models with their priors and predictive checks; model averages, checks, comparisons and the lasso | `explain(outcome="yes or no")`, `explain(grouped_by="school")`, `explain(curve_for="hours")`, `explain(for_percentile=90)`, `find_model_averages_of`, `check_model_of`, `compare_models`, `find_columns_that_predict` |
| Lines, curves and dose-response | straight lines (least squares, Theil-Sen, major axis, Deming, Passing-Bablok), lines that bend, polynomial and named curves (logistic growth, Michaelis-Menten, Gompertz ...), any formula, dose-response curves with ED50 | `fit_line`, `fit_line(with_bends=1)`, `fit_curve(of_kind="michaelis-menten")`, `fit_formula`, `fit_dose_response` |
| Counts, yes/no, risks and rates | risk difference, risk and odds ratios, number needed to treat, Mantel-Haenszel, attributable fractions; rates per 1000 person-days and rate ratios; age-standardised rates and observed / expected (SMR) | `compare_risks`, `rate_of`, `compare_rates` |
| Cause and effect from observational data | groups made alike by weighting or matching on the propensity score, with the balance table and the assumptions printed; mediation (how much of an effect goes through another column); the bioequivalence crossover | `compare_balanced_groups_of`, `explain(through=)`, `compare_averages_of(period=)` |
| Diagnostic tests | sensitivity, specificity, predictive values, likelihood ratios; ROC curves, AUC and the best cut-off; comparing two scores | `compare_to_truth`, `compare_accuracy`, `chart.trade_off_curve` |
| Agreement and method comparison | kappa, ICC, Krippendorff's alpha, Lin's concordance, Bland-Altman limits, Cronbach's alpha | `agreement_between`, `limits_of_agreement`, `reliability_of`, `chart.difference_dots` |
| Survival and competing risks | Kaplan-Meier curves and median times, log-rank tests, Cox models, parametric models, life tables, restricted mean time, competing risks (Aalen-Johansen, Gray, Fine-Gray), adjusted curves, delayed entry | `find_survival_over_time`, `compare_survival`, `explain_survival`, `find_risk_over_time`, `add_time_and_event_columns`, `draw_survival_curves` |
| Combining studies (meta-analysis) | combine counts, estimates, averages, rates or correlations; heterogeneity, prediction interval, subgroups, meta-regression, small-study effects | `combine_studies`, `forest_plot`, `draw_funnel_plot` |
| Planning a study | sample size and power for averages, counts, percents, correlations, regression, survival, equivalence, interval width and clustered designs; power by simulation | `sdata.find_how_many_needed`, `sdata.find_chance_of_finding` |
| Planning an experiment and surveys | design tables (full factorial, randomised blocks, latin square, split plot), randomisation lists in random blocks for each centre, stratified random samples; survey-weighted averages, totals, percentiles, percents, population counts, models and tests (strata, clusters, population sizes) | `sdata.make_design_table`, `sdata.make_random_assignments`, `keep_random_rows(for_each_group_in=)`, `use_survey_design` |
| Distributions | 28 named distributions (normal to von Mises, GEV and generalised Pareto, binomial to hypergeometric) and any SciPy one: chances, percentiles, random numbers; fit one to a column and compare several by AIC | `sdata.distribution`, `find_chance_that_value`, `fit_distribution_to`, `compare_distributions_for` |
| Time series and forecasting | runs of dates, smoothing, trend tests and Sen's slope, trend and season split, autocorrelation, steadiness tests, change points, forecasts (with the ARIMA order chosen automatically) and their checks | `make_run_of_dates`, `add_smoothed_column`, `find_trend_of`, `add_trend_and_season`, `check_steady_over_time`, `find_change_points_in`, `forecast` |
| Signals, cycles and filters | peaks and dips, spectra (periodogram, Welch, Lomb-Scargle), spectrograms, low-, high- and band-pass and notch filters, envelopes, Fourier transforms, waves and windows, convolution | `find_each_peak_that`, `find_spectrum_of`, `spectrum_over_time`, `add_filtered_column`, `find_envelope`, `take_fourier_transform`, `sdata.make_wave` |
| Systems | linear systems from a formula, poles and zeros or matrices; step, impulse and frequency responses, stability, margins, feedback | `sdata.system`, `step_response`, `frequency_response`, `is_stable`, `with_feedback` |
| Fitting, finding and solving | the lowest or highest point of a function, solutions of equations, values between known points, maps across two columns | `sdata.find_where_smallest`, `sdata.solve`, `values_at`, `make_map_of` |
| Patterns across many columns, communities and resistomes | principal components, clusters with silhouettes, distances (Bray-Curtis, Jaccard, Aitchison, Hellinger), diversity and rarefaction, log ratios, NMDS, PCoA, PERMANOVA, ANOSIM, SIMPER, RDA and CCA, Mantel and Procrustes, LDA, correspondence analysis | `add_principal_components`, `add_clusters`, `find_distances_between_rows`, `add_diversity_columns`, `add_log_ratio_columns`, `add_nmds`, `add_principal_coordinates`, `compare_profiles_of`, `explain_profiles_of`, `find_correlation_between_profiles`, `add_axes_that_separate_groups`, `add_correspondence_axes` |
| Hidden factors (questionnaires, test batteries) | how many hidden factors lie behind many columns and which columns go with which (parallel analysis, minres, oblimin); whether a model of hidden factors written down beforehand fits the data, and paths between factors | `find_hidden_factors_behind`, `check_hidden_factors` |
| Directions, places and extremes | the average direction of currents, winds or times of day, and the Rayleigh test; Moran's I for nearby places; variograms; return levels (the 100-year sea level) from yearly maxima or from values above a threshold, with profile-likelihood intervals, and the threshold check | `find_average_direction_of`, `compare_shape_to(shape="even around the circle")`, `find_autocorrelation_of(x=, y=)`, `find_variogram_of`, `find_return_levels_of`, `chart.draw_threshold_check` |
| Numbers and grids | lists and grids of numbers without a table: maths, choosing, sorting, filling, summaries | `sdata.numbers`, `nums.find_average`, `sdata.number_grid`, `grid.swap_rows_and_columns` |
| Learning and citing | every word with an example, help for one word, lessons, the 30-day course, the packages to cite | `sdata.show_all_words`, `sdata.help`, `sdata.show_lesson`, `sdata.start_30_days`, `sdata.show_packages_used` |
| Coming next (not on main yet) | the next statistics phase (S3d) | planned |

### Across the sciences

| Field | Examples of what simplydata does |
|---|---|
| Biology and ecology | growth curves (`fit_curve(of_kind="logistic growth")`); thousands of genes tested at once, with Storey's q-values (`add_adjusted_p_value_column(method="storey")`, practice table "many_tests"); species diversity and rarefaction (`add_diversity_columns`, `chart.draw_richness_curves`); whether nearby plots are alike (Moran's I, `find_autocorrelation_of(x=, y=)`) and a variogram of it (`find_variogram_of`); animal headings and homing directions (`find_average_direction_of`, the Rayleigh test); species make-up of plots: Bray-Curtis distances, NMDS, PCoA, PERMANOVA, ANOSIM, SIMPER and RDA (`find_distances_between_rows`, `add_nmds`, `add_principal_coordinates`, `compare_profiles_of`, `explain_profiles_of`); clusters and principal components; allometric lines (`fit_line(method="standardised major axis")`); mixed models for plots within sites (`explain(grouped_by=)`); the log response ratio across studies (`combine_studies(show="ratios of averages")`) |
| Medicine and epidemiology, including antimicrobial resistance | resistome gene counts: diversity, log ratios and PCoA (`add_diversity_columns`, `add_log_ratio_columns`, `add_principal_coordinates`, practice table "resistome"); risk and odds ratios, number needed to treat (`compare_risks`); infections per 1000 patient-days by ward (`rate_of`, `compare_rates`); time to first ESBL carriage with discharge as a competing event (`find_risk_over_time`, practice table "admissions"); Kaplan-Meier, Cox and Fine-Gray models; diagnostic accuracy and ROC curves (`compare_to_truth`, `compare_accuracy`); matched case-control sets (`explain(matched_by=)`); an interrupted time series around a change in practice (`explain(changes_at=)`); meta-analysis (`combine_studies`); sample size for a trial (`find_how_many_needed(test="compare_survival")`); treated and untreated patients made alike before they are compared (`compare_balanced_groups_of`, practice table "job_training"); attributable fractions and age-standardised death rates (`compare_risks(show="attributable fractions")`, `rate_of(standard_population=)`, practice table "deaths_by_age"); bioequivalence of two formulations (`compare_averages_of(period=)`, practice table "drug_levels") |
| Physics and engineering | step and frequency responses, stability and margins of a system (`sdata.system`); filters, spectra, peaks and envelopes of a sensor signal (`add_filtered_column`, `find_spectrum_of`, `find_each_peak_that`); fitting any formula (`fit_formula`); solving equations (`sdata.solve`); calibration lines checked against NIST certified values |
| Chemistry | calibration lines (`fit_line`); enzyme kinetics (`fit_curve(of_kind="michaelis-menten")`); EC50 and LD50 from dose-response curves (`fit_dose_response`); comparing two measurement methods (`fit_line(method="passing-bablok")`, `limits_of_agreement`) |
| Earth and marine science | the average current or wind direction and the Rayleigh test (`find_average_direction_of`, `compare_shape_to(shape="even around the circle", full_turn=360)`, practice table "stations"); whether metals in sediment are alike at nearby stations (`find_autocorrelation_of(x=, y=, on_globe=True)`); variograms (`find_variogram_of`, `chart.draw_variogram`); the 100-year sea level from yearly maxima (`find_return_levels_of`, the real Port Pirie data, practice table "sea_levels"); how much temperature and salinity explain the make-up of samples (`explain_profiles_of`), and whether genes and water chemistry vary together (`find_correlation_between_profiles`); trends with the Mann-Kendall test and Sen's slope, seasonal too (`find_trend_of`); trend and season split (`add_trend_and_season`); jumps in nitrate at river stations (`find_change_points_in`); spectra of unevenly spaced readings (`find_spectrum_of(method="lomb-scargle")`); maps and contours from scattered points (`make_map_of`, `draw_contour`); forecasts (`forecast`); models with AR(1) neighbours (`explain(neighbours_alike_in_order_of=)`) |
| Climate and hydrology | return levels of rain, floods, storm surges and heat from yearly maxima or from every value above a threshold, with profile-likelihood intervals (`find_return_levels_of(values_above=30, sorted_by="date")`, practice table "rain"); choosing the threshold (`chart.draw_threshold_check`); the extremal index for values that come in runs; times of day and seasons on a circle (`find_average_direction_of(full_turn=24)`) |
| Social science and psychology | questionnaire reliability (`reliability_of`); hidden factors behind questionnaire items, explored and checked (`find_hidden_factors_behind`, `check_hidden_factors`); agreement between raters (`agreement_between`); ordered answers (`explain(outcome="ordered groups")`); subjects crossed with items (`explain(crossed_with=)`); repeated measures (`compare_averages_of(matched_by=)`, `compare_matched_columns`); adjusted group averages (`find_model_averages_of`); power for a planned study (`find_chance_of_finding`) |
| Education | pupils in classes in schools (`explain(grouped_by=["school", "class"])`); comparing classes (`compare_averages_of`, `compare_each_pair_of`); the course itself: lessons, the 30-day course and plain words for teaching charts, tables and statistics (`sdata.show_lesson`, `sdata.start_30_days`) |

Every number comes from the package named above, and is checked against it and against R in the public
[reliability study](https://github.com/bioforkgithub/simplydata/blob/main/validation/report.md); the
[manual](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.pdf) has every word, with its
"same underneath" code for the words that have it.

## Why simplydata exists: the learning philosophy

Learning to program is hard for many people, and data science adds a second hurdle: the names. In a study across
several countries, first-year students averaged 22.9 out of 110 on a programming task (McCracken et al. 2001), and
about one in three students still fails a first programming course (Watson & Li 2014). Even experienced data
scientists say they must "know all the function names and class names correctly and have another browser open to
search for help" (Chattopadhyay et al. 2020). For a researcher who wants to analyse data, much of the effort goes into
remembering how each library spells things, not into the science. simplydata was written to remove that effort.

The design follows what the research on learning and on programming languages says:

- **Everyday words are easier than invented ones.** Novices find common English words with a known meaning the most
  intuitive, and languages with English-like keywords are learned more accurately than ones with arbitrary keywords
  (Stefik & Siebert 2013). Full words are understood faster than abbreviations (Lawrie et al. 2007; Hofmeister et al.
  2017). So simplydata uses words such as `keep_rows_where`, `find_average_of` and `draw_bars`.
- **People describe tasks on whole sets of data, as queries** ("the rows where marks are above 50"), not as loops
  (Pane, Ratanamahatana & Myers 2001). simplydata's words follow that way of speaking.
- **No one guesses a name nobody told them.** Two people pick the same name for the same thing less than one time in
  five (Furnas et al. 1987). So every word is built from a short list of verbs and glue words that can be learned once,
  every name is scored for how familiar its words are, and typing a name from another tool (or a near miss) points
  to the right word.
- **Working memory is small** (Miller 1956; Cowan 2001), and effort spent searching for the means competes with
  learning (Sweller 1988). One small, consistent vocabulary with sensible defaults lowers that load; most people keep
  the default they are given (Johnson & Goldstein 2003), so the defaults are the recommended methods.
- **Worked examples teach better than problem solving alone** (Sweller & Cooper 1985). The lessons and the 30-day
  guide start from a worked example, then fade it, then ask for your own call.
- **Readable error messages shorten debugging** (Becker et al. 2019; Denny, Prather & Becker 2020). simplydata's
  messages say what went wrong, how to fix it, and give the corrected call.
- **English-like code can mislead**: AppleScript was easy to read but hard to write, because its English hid fixed
  rules (Cook 2007), and novices tend to believe the computer understands what they mean (Pea 1986). simplydata
  therefore stays plain Python (object, dot, word, options) with a closed set of words, and it is a bridge, not a
  wall: like Hedy, which leads learners step by step to real Python (Hermans 2020), every simplydata word shows the
  pandas, Polars, NumPy, SciPy, statsmodels or R code it runs underneath, so you can move on to those libraries
  whenever you want.
- **Trust comes from checking.** simplydata does not compute statistics itself: every number comes from the
  established package, and a public reliability study compares each word with that package, with R and with
  published certified values.

### References

- Becker, B. A., et al. (2019). Compiler error messages considered unhelpful. *ITiCSE Working Group Reports*. https://doi.org/10.1145/3344429.3372508
- Chattopadhyay, S., Prasad, I., Henley, A. Z., Sarma, A., & Barik, T. (2020). What's wrong with computational notebooks? *CHI '20*. https://doi.org/10.1145/3313831.3376729
- Cook, W. R. (2007). AppleScript. *Proceedings of the third ACM SIGPLAN conference on History of Programming Languages (HOPL III)*. https://doi.org/10.1145/1238844.1238845
- Cowan, N. (2001). The magical number 4 in short-term memory. *Behavioral and Brain Sciences*, 24(1), 87-114. https://doi.org/10.1017/S0140525X01003922
- Denny, P., Prather, J., & Becker, B. A. (2020). Error message readability and novice debugging performance. *ITiCSE '20*. https://doi.org/10.1145/3341525.3387384
- Furnas, G. W., Landauer, T. K., Gomez, L. M., & Dumais, S. T. (1987). The vocabulary problem in human-system communication. *Communications of the ACM*, 30(11), 964-971. https://doi.org/10.1145/32206.32212
- Hermans, F. (2020). Hedy: a gradual language for programming education. *ICER '20*, 259-270. https://doi.org/10.1145/3372782.3406262
- Hofmeister, J., Siegmund, J., & Holt, D. V. (2017). Shorter identifier names take longer to comprehend. *SANER 2017*. https://doi.org/10.1109/SANER.2017.7884623
- Johnson, E. J., & Goldstein, D. (2003). Do defaults save lives? *Science*, 302, 1338-1339. https://doi.org/10.1126/science.1091721
- Lawrie, D., Morrell, C., Feild, H., & Binkley, D. (2007). Effective identifier names for comprehension and memory. *Innovations in Systems and Software Engineering*, 3(4), 303-318. https://doi.org/10.1007/s11334-007-0031-2
- McCracken, M., et al. (2001). A multi-national, multi-institutional study of assessment of programming skills of first-year CS students. *ACM SIGCSE Bulletin*, 33(4), 125-180. https://doi.org/10.1145/572139.572181
- Miller, G. A. (1956). The magical number seven, plus or minus two. *Psychological Review*, 63(2), 81-97. https://doi.org/10.1037/h0043158
- Pane, J. F., Ratanamahatana, C. A., & Myers, B. A. (2001). Studying the language and structure in non-programmers' solutions to programming problems. *International Journal of Human-Computer Studies*, 54(2), 237-264. https://doi.org/10.1006/ijhc.2000.0410
- Pea, R. D. (1986). Language-independent conceptual "bugs" in novice programming. *Journal of Educational Computing Research*, 2(1), 25-36. https://doi.org/10.2190/689T-1R2A-X4W4-29J2
- Stefik, A., & Siebert, S. (2013). An empirical investigation into programming language syntax. *ACM Transactions on Computing Education*, 13(4), 19. https://doi.org/10.1145/2534973
- Sweller, J. (1988). Cognitive load during problem solving: effects on learning. *Cognitive Science*, 12(2), 257-285. https://doi.org/10.1207/s15516709cog1202_4
- Sweller, J., & Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving in learning algebra. *Cognition and Instruction*, 2(1), 59-89. https://doi.org/10.1207/s1532690xci0201_3
- Watson, C., & Li, F. W. B. (2014). Failure rates in introductory programming revisited. *ITiCSE '14*, 39-44. https://doi.org/10.1145/2591708.2591749

> Status: early development (charts, tables, numbers, statistical tests, fitting and distributions ready). The word list may still change: an old word keeps working for one release and prints a one-line note with its new name.

Install (recommended): `conda install -c conda-forge simplydata` (or `mamba` / `micromamba` in place of `conda`); also `pip install simplydata`. See [Install](#install).

```python
import simplydata as sdata

table = sdata.table(sdata.get_example("marks"))            # a made-up table; your own: sdata.table("marks.xlsx")
table.keep_rows_where("marks", is_above=50)
table.find_average_of("marks", for_each_group_in="class")  # says the answer in a sentence
table.save("good_marks.xlsx")

chart = table.start_chart()                                # or sdata.chart(table)
chart.draw_bars(x="class", y="marks", error="standard error")
chart.write_title_on_top("Good marks in each class")
chart.label_y("Marks")
chart.save("marks.png")
```

Tables, charts and numbers are separate objects, as in pandas, Polars, NumPy and matplotlib:
one cleaned table can feed many charts, and charts go side by side with
`sdata.put_in_rows_and_columns(a, b, with_letters=True)` (panels A, B, C ... as in papers).

## Install

**Recommended: conda, mamba or micromamba** (from conda-forge). They install Python, simplydata and, when you want
them, R and its packages in one environment, which is the easiest way on Windows, macOS and Linux alike. All three
read the same conda-forge packages; use whichever you have.

```
conda create -n simplydata -c conda-forge simplydata        # a new environment called "simplydata"
conda activate simplydata

mamba create -n simplydata -c conda-forge simplydata        # the same with mamba (faster)
micromamba create -n simplydata -c conda-forge simplydata   # the same with micromamba (small, no base install)
```

Extras, in the same environment (replace `conda` with `mamba` or `micromamba` if you use those):

```
conda install -c conda-forge polars pyarrow           # Polars, the fast engine for big data
conda install -c conda-forge python-docx pyreadstat   # reading Word, SPSS and Stata files
conda install -c conda-forge control                  # rise time, settling time and margins of systems
conda install -c conda-forge rpy2 r-base              # R and the bridge to it, for the methods only R has
```

> The conda-forge package is in review (submitted 2026-11-20). Until `conda install -c conda-forge simplydata`
> finds it, create the environment with conda and install simplydata into it with pip:
> `conda create -n simplydata -c conda-forge python=3.12 rpy2 r-base` then `conda activate simplydata` and
> `pip install simplydata`.

**Also possible: pip** (needs Python 3.11 or newer):

```
pip install simplydata
pip install "simplydata[fast]"    # adds Polars, the fast engine for big data
pip install "simplydata[files]"   # adds reading Word, SPSS and Stata files
pip install "simplydata[systems]" # adds python-control: rise time, settling time and margins of systems
pip install "simplydata[r]"       # adds rpy2, the bridge from Python to R (install R itself from https://cran.r-project.org)
```

With pip, the `[r]` extra also needs R (https://cran.r-project.org) and, in R,
`install.packages(...)` with the R packages listed under "Packages underneath" above. On Windows with
Python 3.13, rpy2 has no ready-made wheel; set `RPY2_CFFI_MODE=ABI` first (in PowerShell:
`$env:RPY2_CFFI_MODE = "ABI"`, in cmd: `set RPY2_CFFI_MODE=ABI`), then run the pip line. With conda, mamba or
micromamba this step is not needed: rpy2 and R come ready-built from conda-forge, and the R packages too
(for example `conda install -c conda-forge r-vegan r-metafor r-lme4`).

## Privacy: your data stays on your computer

simplydata is made for sensitive data too, such as patient records and surveillance data. "Safe for patient
data" at the top of this page means the promises below, and automatic tests check each of them on every change.

- **Nothing is sent anywhere.** simplydata has no telemetry, no analytics, no update checks and no crash reports.
  It never uploads, sends or logs your data.
- **The only network use is one you ask for:** `sdata.table("https://...")` downloads the table at a web address
  you give: one request for that file, with none of your data. It follows the address on only to another https
  address. Everything else, R included, runs fully offline.
- **Files are written only where you ask:** `table.save(...)`, `chart.save(...)`, `nums.save(...)` and
  `save_as=`. R draws into nothing, never into an `Rplots.pdf`. `sdata.start_30_days()` keeps the dates of your
  learning days in `.simplydata/progress.json` in your home folder (no data). Temporary files are deleted at once:
  an SPSS file read from a web address, and R's own session folder when Python ends.
- **What simplydata prints goes to your own screen.** The list of packages at the end of a script names packages
  and versions only, never a value or a column name.
- **Checked on every change.** [tests/test_privacy.py](https://github.com/bioforkgithub/simplydata/blob/main/tests/test_privacy.py)
  scans the source for network code and for R code that names a network, install or file-writing function
  (simplydata also refuses to run such R code), and the whole test suite runs with Python's network connections
  blocked.

The packages underneath keep their own caches, such as matplotlib's list of fonts; these hold no data. To report a
security or privacy problem, see [SECURITY.md](https://github.com/bioforkgithub/simplydata/blob/main/SECURITY.md).

## Learn it in a day

simplydata teaches itself. Open Python and type:

```python
import simplydata as sdata
sdata.show_lesson(1)
```

There are thirty-six short lessons. Lessons 1 to 8 teach charts, from your first chart to
animations. Lessons 9 to 12 teach tables: looking at your data, choosing rows and columns,
cleaning it, and summing it up. Lesson 13 teaches numbers (lists and grids of numbers), and
lesson 14 the statistical tests: is a difference real, and how big is it? Lesson 15 puts it
all together, from a question and a file to a figure with panels A and B and a saved table.
Lessons 16 to 22 go further: models (multiple, logistic, Poisson and mixed regression, multiple
imputation), patterns across many columns (PCA, clustering, Bray-Curtis distances, NMDS,
PERMANOVA), survival curves and Cox models, power analysis, fitting curves and formulas,
finding the smallest or biggest value and solving equations, distributions and chances,
values between the points you measured, working with a model (checking it, comparing two
models and predicting with an interval), and risks, diagnostic tests and agreement. Lessons 23 to 26 cover time series (dates, missing
days, time windows, smoothing and trend), forecasts checked on held-back months, cycles in a
recording (spectra, filters, peaks, and whether a series stays steady) and, optional, linear
systems (step and frequency responses, feedback). Lesson 27 goes beyond the average line: a model
that gives outliers less weight. Lesson 28 shows effects that depend on each other: the interaction picture
first, then comparisons within groups and against a control. Lesson 29 is more survival: dates turned
into time and event columns, survival at chosen times, and the chance of an event when another can come
first. Lesson 30 combines studies (a meta-analysis): the combined effect, how much the
studies differ, and the forest and funnel plots. Lessons 31 and 32 read a community or resistome table:
diversity at the same total count, then log ratios, PCoA and how much temperature and salinity explain. Lesson
33 follows a coastal station: the average direction of its currents, whether nearby stations have alike zinc
(Moran's I), and the 100-year sea level at Port Pirie (real data). Lesson 34 plans an experiment and a
survey: a design table in randomised blocks, a randomisation list in random blocks for each hospital, and
a stratified random sample of real California schools. Lesson 35 asks about cause and effect in observational
data: a job-training study made alike by weighting and by matching, with the balance table first, and how much of a
workshop's effect on depression went through job-search confidence (mediation). Lesson 36 gives Bayesian answers: a Bayes factor for two
wards, a credible interval for a change in pain, and a Bayesian model with its prior and its
predictive check. Each
lesson has an example you can run, says what every line does, explains the idea behind it
(average or median, standard deviation or standard error, p-values) and ends with a small task
to try yourself.

- `sdata.show_lesson()` lists the lessons
- `sdata.show_all_words()` lists every word, with an example (also on the first pages of the [dictionary](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydataDictionary.pdf))
- `sdata.help("draw_bars")` explains one word: what it does, its options and an example
  (table and number words too: `sdata.help("keep_rows_where")`, `sdata.help("find_average")`)
- `sdata.get_example()` lists the made-up tables to practise with (marks, weather, fruit, growth, sensor, visitors, river, shop, school, meadow, trial, clinic, island; shop has dates and empty cells)
- `sdata.show_lesson(3, solutions=True)` adds a worked solution to each "Try it yourself" task
- `sdata.show_packages_used()` lists the packages that did the work behind your words (pandas, SciPy, R packages ...), with versions and the references their authors ask for; a short list is also printed at the end of a script

## Or learn it in 30 days

Rather learn an hour a day? simplydata has a 30-day course built in:

```python
import simplydata as sdata
sdata.start_30_days()                  # you already write some Python
sdata.start_30_days(track="beginner")  # you have never programmed: starts with just enough Python
sdata.show_today()                     # every day: the day to do next
```

Each day starts with a 5-minute warm-up of questions on earlier days (answered from memory, which
fixes words better than reading them again), then the lesson to work through, and ends with a task
to do without looking back. Review days mix the whole course, the last week is a project of your
own, and day 29 is a final test from memory. The 30 days teach the everyday work (tables, charts,
summaries, tests, models, fitted curves and everyday time series); the manual is the complete
reference, and a day points to it for the rest (forecasts, spectra and filters, systems, risks and
diagnostic tests). Missed a day? `sdata.show_today()` carries on where you
stopped. `sdata.show_answers()` gives the answers, `sdata.show_day()` the whole calendar, and `sdata.go_to_next_day()`
goes on now. Your progress is kept only on your computer, in `~/.simplydata/progress.json`.

**[30 days of simplydata (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_30_days.pdf)**
is the same course on paper: a calendar to tick for each track, one page per day with the page of
the manual for each lesson and word, and the answers at the back.

## Manual

**[The simplydata manual (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.pdf)** has everything in one book:
all thirty-six lessons with the real charts and output they make, every word explained (its options,
an example you can run and the library that does the work underneath), the data science ideas
behind the numbers (average or median, standard deviation or standard error, confidence intervals,
p-values, effect sizes, and which statistical test to use when), and a worked solution for every
task.

**[The simplydata dictionary (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydataDictionary.pdf)** opens with every word at a glance, group by group, then lists every word A to Z, with its meaning, an example and the page of the manual that explains it, and turns names from other tools (`groupby`, `iloc`, `hist`, `curve_fit` ...) into simplydata words.

The manual is made from the code by `python docs/make_manual.py` (it needs a LaTeX system with
`pdflatex`), so it never goes out of date: a test fails if
[docs/manual/simplydata_manual.tex](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.tex) no longer matches the code. The same command builds the dictionary and the 30-day guide,
with the page numbers of the manual it has just compiled.

## Tables

Plain words for looking at data, cleaning it and summing it up, on pandas or Polars:

```python
table = sdata.table(sdata.get_example("marks"))                # or sdata.table("marks.xlsx")
table.keep_rows_where("marks", is_above=50)
table.sort_by("marks", biggest_first=True)
table.find_average_of("marks", for_each_group_in="class")      # says the answer in a sentence
table.compare_averages_of("marks", for_each_group_in="class")  # real difference, or chance?
table.undo()                                                   # take the last step back
table.save("good_marks.xlsx")
chart = table.start_chart()                                    # draw it
```

## Numbers

Plain words over NumPy for lists and grids of numbers:

```python
nums = sdata.numbers([12, 15, 9, 20, 14])
bigger = nums * 2                        # symbols make new numbers
nums.keep_each_number_that(is_above=10)  # words change the numbers you have ...
nums.undo()                              # ... and can be taken back
nums.find_average()
grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
grid.find_total(for_each="row")
```

## Choosing parts

Rows, columns and numbers by their place, counting from 1 the way the printed row numbers do,
with both ends included:

```python
table = sdata.table(sdata.get_example("marks"))
table.keep_rows_by_position(10, to=20)                                 # rows 10 to 20 (pandas df.iloc[9:20])
table.keep_rows_by_position(1, step=2)                                 # every 2nd row
table.keep_columns("hours", to="height")                               # a run of columns by name
table.keep_columns(of_kind="number")                                   # every number column
table.get_cell_at(row=3, column="marks")                               # one cell
table.replace_values_in("marks", is_above=90, with_value=90)
grid = sdata.numbers(1, to=24).make_number_grid(columns=6)
grid.keep_rows_by_position(2, to=3).keep_columns_by_position(1, to=3)  # a block
```

## More statistics

Models, patterns across many columns, survival and planning a study, each checked against R:

```python
school = sdata.table(sdata.get_example("school"))
school.explain("marks", using=["hours", "sleep", "breakfast"])  # multiple regression
school.explain("passed", using=["hours"], outcome="yes or no")  # logistic regression
school.explain("marks", using=["hours"], grouped_by="school")   # mixed model

meadow = sdata.table(sdata.get_example("meadow"))
meadow.add_principal_components(how_many=2)                     # PCA
meadow.add_nmds(measure="bray-curtis")                          # NMDS map
meadow.compare_profiles_of(for_each_group_in="grazed")          # PERMANOVA

trial = sdata.table(sdata.get_example("trial"))
trial.compare_survival(time="days", event="died", for_each_group_in="treatment") # log-rank test
trial.compare_risks("died", for_each_group_in="treatment", against="usual care") # risk ratio, NNT
sdata.find_how_many_needed(effect_size=0.5)                     # power analysis

clinic = sdata.table(sdata.get_example("clinic"))
clinic.compare_to_truth("rapid_test", truth="infected")         # sensitivity, specificity
clinic.compare_to_truth("crp", truth="infected")                # ROC curve, AUC
```

## Fitting, finding and distributions

Fit a line, a curve or your own formula; find the best value; solve an equation; ask a
distribution for chances; estimate values between the points you measured:

```python
growth = sdata.table(sdata.get_example("growth"))
growth.fit_formula("population = a * exp(b * (year - 2000))", for_each_group_in="country")  # as R nls()
growth.values_at("population", at={"year": [2001, 2011]}, for_each_group_in="country")      # as R approx()

sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5])                                 # -3, at x = 2 (as R optimize())
sdata.solve("x**3 - 2*x = 5", between=[0, 3])                                               # x = 2.09455 (as R uniroot())

dist = sdata.distribution("normal", average=50, standard_deviation=10)
dist.find_chance_that_value(is_above=80)                                                    # 0.135 %, and the R call: pnorm(...)
school = sdata.table(sdata.get_example("school"))
school.compare_distributions_for("days_absent", distributions=("poisson", "negative binomial"))
```

Coming from another tool? Its names point to the simplydata word and never run:
`sdata.minimize` says "In simplydata this is sdata.find_where_smallest(...)", `table.groupby` points to
`for_each_group_in=`, `chart.hist` to `chart.draw_histogram`.

## How simplydata works

simplydata does not implement statistical methods itself. Every calculation is done by
established, peer-reviewed packages: Python packages (SciPy, statsmodels, pandas, NumPy and
others), and R packages through rpy2 where Python has none. simplydata translates simple words
into those calls, with the right settings, and says in the result which method was used. What we
test is that translation: each answer is checked against the package underneath and against R.

### How we check simplydata

The [reliability report](https://github.com/bioforkgithub/simplydata/blob/main/validation/report.md) runs simplydata words on real, published data (NIST
certified values, Student's sleep data, Anscombe's quartet ...) and compares each answer with the
published one, with the package underneath called directly, and with R. It lists the tolerance of
every check, the package versions it ran with, and every setting where simplydata's default differs
from the package's own. Anyone can rerun it with one command: `python validation/make_report.py`
([how it works and the datasets](https://github.com/bioforkgithub/simplydata/blob/main/validation/README.md)). For the words that have it, the manual also
shows the same job written in the package underneath, in a grey box that a test runs and checks.

### How simplydata chooses methods

- Defaults follow published guidelines and method comparisons where they exist; the manual cites them for each
  word.
- Where methods disagree, simplydata prefers the one that is valid under fewer assumptions (Welch's t-test
  rather than Student's, for example).
- Where the evidence is balanced, simplydata matches the field's standard software, and says so; where studies
  prefer another method, the table names it.
- simplydata checks the data, and refuses or warns when a method does not fit it.
- Every printout names the method used, and every default can be changed with an option.
- The defaults of each batch were checked by an independent review when they were designed, and every entry of
  the table below, with its references, was checked again by independent hostile reviewers in November 2026.

[How simplydata chooses methods](docs/how_simplydata_chooses.md) gives all 318 defaults: for each, the default,
the alternatives, why it was chosen, what simplydata checks in the data, and its references (each DOI checked in
Crossref). The manual has the same table as its last part.

## Using the words that need R

The packages behind every word, and which need R, are in [What simplydata handles](#packages-underneath).
To use the words that need R, install R from https://cran.r-project.org, then
`pip install "simplydata[r]"`, then in R `install.packages(...)` with the R packages listed there.
Every other word works without R. A word that needs R and cannot find it, or a package, stops with
a friendly message that says what to install.

## Ideas behind it

- **Talk to the program.** Each line reads like an instruction you say to the program: the thing,
  what it should do, then the details: `table.keep_rows_where("marks", is_above=50)`,
  `chart.write_title_on_top(...)`, `chart.draw_line_at_y(50)`.
- **What + where.** A few place words repeat everywhere: `top`, `bottom`, `x`, `y`, `at`, `between`.
- **Old names keep working for one release.** A renamed word still runs and says, once, what it is
  called now.
- **Guess a word from its sibling.** `keep_rows_where` and `keep_first_rows`, `show_first_rows`;
  `find_average_of` and `show="average"`; `label_x` and `label_colour_bar`.
- **The word names the idea.** `error="standard error"`, `fit_line(with_confidence_band=True)`,
  `compare_averages_of` (and the result says "Welch's t-test" for when you write it up).
- **Order doesn't matter.** Write the steps in any order; simplydata draws them correctly.
- **Friendly errors.** Misspell a column and simplydata tells you what you probably meant.
- **Your old words still help.** Names from pandas, NumPy, SciPy, R and matplotlib (`groupby`,
  `curve_fit`, `pnorm`, `hist`) point to the simplydata word, so the first guess is never a dead end.

The full design is in [PLAN.md](https://github.com/bioforkgithub/simplydata/blob/main/PLAN.md).

## Changes and contributing

What changed in each release is in [CHANGELOG.md](https://github.com/bioforkgithub/simplydata/blob/main/CHANGELOG.md). Contributions are welcome:
[CONTRIBUTING.md](https://github.com/bioforkgithub/simplydata/blob/main/CONTRIBUTING.md) explains how to suggest a word, report a problem or add code.

## How to cite

If simplydata helps your work, please cite the archived software:

> bioforkgithub. simplydata: simple words for data science in Python. Zenodo. https://doi.org/10.5281/zenodo.24210045

This DOI always points to the latest version; each release also has its own DOI on Zenodo. GitHub's "Cite this repository" button gives the same citation in other formats.

## Licence

MIT.
