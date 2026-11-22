"""Build the simplydata manual (docs/manual/simplydata_manual.tex and .pdf) from the code.

Everything in the manual comes from simplydata itself: the lessons, their solutions and the
word list from simplydata/learn.py (LESSONS, HELP_EXAMPLES, GROUPS), each word's options and
text from its docstring and signature, and the practice tables from simplydata.data. Only
three things are written by hand: the short "Getting started" text below, UNDERNEATH (which
library each word uses) and docs/manual/ideas.tex (the data science ideas).

    python docs/make_manual.py            # write the .tex, run every example, compile the PDF
    python docs/make_manual.py --tex      # only write the .tex (fast; no LaTeX needed)
    python docs/make_manual.py --no-run   # write the .tex and compile, without running the examples again
    python docs/make_manual.py --no-run --underneath-figures   # the same, but draw the pictures of the
                                          # "same underneath" boxes first (R words need R)

Each word with a tested entry in simplydata._underneath gets a grey box "The same underneath" after its
example: the same job in the package underneath, made from that entry, with one picture for chart words.
The one-line "Underneath" field is read from the entry's code; words without an entry yet keep the name
in GROUP_UNDERNEATH / UNDERNEATH below.

Compiling the manual also builds the dictionary (docs/manual/simplydataDictionary.pdf, made by
docs/make_dictionary.py) and the guide "30 days of simplydata" (docs/manual/simplydata_30_days.pdf,
made by docs/make_30_days.py), so their page numbers always match the manual. The LaTeX build files go
to a scratch folder; set SIMPLYDATA_LATEX_DIR to choose another one.

Building the PDF needs a LaTeX system with pdflatex (MiKTeX or TeX Live). It runs every
lesson example and every solution, saves their charts in docs/manual/figures/ and what they
print in docs/manual/output/, then compiles the PDF three times (for the page numbers).
The .tex has no dates in it, so it only changes when the code changes; a test
(tests/test_learn.py) fails if docs/manual/simplydata_manual.tex is out of date.
"""

from __future__ import annotations

import contextlib
import inspect
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import simplydata
from simplydata import learn
from simplydata.data import EXAMPLES

HERE = Path(__file__).resolve().parent
MANUAL = HERE / "manual"
TEX = MANUAL / "simplydata_manual.tex"
PDF = MANUAL / "simplydata_manual.pdf"
FIGURES = MANUAL / "figures"
OUTPUT = MANUAL / "output"

MAX_OUTPUT_LINES = 40  # longer printed output is cut, with a line that says how much was left out
IMAGE_TYPES = ("png", "pdf", "svg", "jpg", "jpeg", "tif", "tiff", "gif")

# ---------------------------------------------------------------- which library is underneath
# One line per group: what most of its words use. A word whose library differs, or is worth
# naming more exactly, is in UNDERNEATH. make() stops with a message if a word has neither.
GROUP_UNDERNEATH = {
    "Lines and shading": "matplotlib",
    "Words on the chart": "matplotlib",
    "Axes": "matplotlib",
    "Colours and look": "matplotlib",
    "Order of groups": "pandas (a stable sort of the rows, so every chart type, colour and panel follows the order)",
    "Tables: start and look": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Choose columns": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Choose rows": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Empty cells": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Distributions": "SciPy (scipy.stats frozen distributions: cdf, sf, ppf, isf, pdf, pmf, stats, rvs)",
    "Fix columns": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Sort and new columns": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Dates and text": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Row after row": "narwhals (shift, rolling_mean and over with order_by=, so each group keeps its own rows)",
    "Summaries": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Join and reshape": "narwhals, which runs the step in pandas or Polars (whichever holds the table)",
    "Undo and finish": "simplydata itself: it keeps every version of the table",
    "Numbers: make and look": "NumPy",
    "Numbers: maths in words": "NumPy",
    "Numbers: choose, sort and fill": "NumPy",
    "Numbers: summaries": "NumPy (functions that skip empty values, such as nanmean)",
    "Grids of numbers": "NumPy (a two-dimensional array)",
    "Numbers: undo and finish": "simplydata itself: it keeps every version of the numbers",
    "Waves and systems": "SciPy (signal.lti / dlti, step, impulse, lsim, freqresp, freqz, cont2discrete, tf2ss, tf2zpk); "
               "the formula read with Python's ast and NumPy polynomials; rise time, settling time, overshoot and "
               "margins from python-control (step_info, stability_margins: simplydata[systems])",
    "Help": "plain Python: simplydata reads its own word list and docstrings",
    "30 days of simplydata": "plain Python: the days are in simplydata/learn_days.py, and the progress is a small "
                             "JSON file on your computer (json, pathlib)",
}
UNDERNEATH = {
    # help
    "sdata.show_packages_used": "Python's importlib.metadata (versions and home pages) and each package's own "
                                "requested reference; for R, utils::citation() and packageVersion() through rpy2",
    # start, show and save
    "sdata.chart": "pandas reads the file (Polars for big files); the chart is drawn with matplotlib and seaborn",
    "sdata.get_example": "pandas (read_csv of a small file inside simplydata)",
    "show": "matplotlib (pyplot.show)",
    "save": "matplotlib (Figure.savefig); Pillow writes .gif animations",
    "get_numbers_drawn": "matplotlib (the drawn artists: Line2D.get_xydata, PathCollection.get_offsets, BarContainer, "
                         "LineCollection.get_segments, fill_between paths, QuadMesh arrays, Wedge)",
    # chart types
    "draw_bars": "seaborn (barplot; countplot for show=\"count\")",
    "draw_lines": "seaborn (lineplot); SciPy (interpolate) for joined_by= curves",
    "draw_dots": "seaborn (scatterplot)",
    "draw_area": "matplotlib (fill_between, or stackplot with stacked=True)",
    "draw_histogram": "seaborn (histplot)",
    "draw_boxes": "seaborn (boxplot)",
    "draw_violins": "seaborn (violinplot)",
    "draw_heatmap": "seaborn (heatmap); SciPy (scipy.cluster.hierarchy) for cluster=True",
    "draw_pie": "matplotlib (Axes.pie)",
    "draw_polar": "matplotlib (polar axes)",
    "draw_contour": "matplotlib (contourf); SciPy (interpolate.griddata) for scattered points",
    "draw_surface": "matplotlib (mplot3d plot_surface); SciPy (interpolate.griddata) for scattered points",
    "draw_dots_3d": "matplotlib (mplot3d scatter)",
    "draw_band": "matplotlib (fill_between)",
    "draw_map_of_empty_cells": "pandas finds the empty cells (isna); matplotlib (imshow) draws the grid",
    "write_names_on_dots": "matplotlib (annotate), with simplydata choosing a free place for each name",
    # statistics
    "show=": "seaborn (the estimator of barplot and lineplot)",
    "error=": "seaborn (errorbar=\"sd\" or \"se\"); the confidence interval from the t distribution (SciPy)",
    "draw_error_bars": "pandas (group averages) and matplotlib (errorbar); SciPy for the t-based confidence interval",
    "fit_line": "SciPy (stats.linregress); the confidence band from statsmodels OLS, drawn with matplotlib",
    "fit_curve": "statsmodels (least squares on the powers of x), drawn with matplotlib",
    "draw_smooth_line": "statsmodels (lowess with R lowess()'s default delta, 1 % of the x range) or SciPy (make_smoothing_spline, for "
                   "test_method=\"spline\"; smoothness=\"auto\" lets R smooth.spline choose it and needs R); the other "
                   "methods as nums.smooth (SciPy, pandas; \"median\" R runmed); drawn with matplotlib",
    "draw_density": "seaborn (kdeplot)",
    "trade_off_curve": "R pROC (roc, coords, ci.auc; simplydata[r]), drawn with matplotlib",
    "difference_dots": "statsmodels (graphics.agreement.mean_diff_plot) for the dots; R "
                       "BlandAltmanLeh::bland.altman.stats for the limits and their intervals (simplydata[r])",
    "forest_plot": "matplotlib (errorbar), from the interval columns of a result table; on combine_studies' result "
                   "squares (scatter), diamonds (fill) and the prediction interval (plot)",
    "draw_qq_dots": "SciPy (stats.probplot, against a fitted scipy.stats distribution for distribution=) for the points "
               "and the line; matplotlib draws them",
    "draw_cumulative_share": "seaborn (ecdfplot)",
    "draw_count_bars": "seaborn (countplot)",
    "draw_all_dots": "seaborn (swarmplot; stripplot for groups of more than 100 dots)",
    "draw_side_histograms": "matplotlib (hist), with NumPy choosing the bins",
    "sdata.draw_all_pairs": "seaborn (scatterplot, histplot and kdeplot)",
    # several charts
    "draw_one_chart_for_each_group_in": "matplotlib (a grid of subplots)",
    "sdata.put_side_by_side": "matplotlib (subplots)",
    "sdata.put_one_above_other": "matplotlib (subplots)",
    "sdata.put_in_rows_and_columns": "matplotlib (subplots)",
    "add_zoom_box": "matplotlib (inset_axes and indicate_inset_zoom)",
    "animate": "matplotlib (animation) and Pillow (the .gif file)",
    # tables
    "sdata.table": "pandas or Polars read the file; narwhals lets every table word run on both",
    "table.show": "pandas or Polars (printing the table)",
    "table.get_column": "NumPy (a column of numbers becomes sdata.numbers)",
    "table.fill_empty_cells_in": "narwhals; NumPy (interp) for the line between neighbours; SciPy (CubicSpline, "
                              "PchipInterpolator) for the curves",
    "table.turn_into_dates": "pandas (to_datetime) or Polars (str.strptime), trying the date formats in a fixed order",
    "table.split_column": "pandas (str.split) or Polars (str.splitn), whichever holds the table",
    "table.add_rolling_column": "narwhals (rolling_mean, rolling_sum, rolling_std with over(order_by=)); "
                                "pandas or Polars rolling for median, smallest and biggest",
    "table.find_summary_of": "narwhals (group summaries); SciPy (stats: gmean, variation, median_abs_deviation, "
                        "trim_mean, mode, skew, kurtosis, hmean, mstats.winsorize, and the t distribution for the "
                        "confidence interval)",
    "table.find_interval_of": "SciPy (stats.bootstrap, BCa, percentile or basic)",
    "table.add_z_score_column": "SciPy (stats.zscore with ddof=1, as R scale())",
    "table.find_average_of": "narwhals (group means); SciPy (stats.ttest_1samp confidence_interval for interval=); "
                        "statsmodels (DescrStatsW for weights=)",
    "table.find_median_of": "narwhals (group medians); SciPy (stats.quantile_test confidence_interval for interval=); "
                            "NumPy (repeat and median, or percentile(weights=)) for weights=",
    "table.find_standard_deviation_of": "narwhals (group standard deviations); R DescTools::VarCI for interval= "
                                   "(simplydata[r]); statsmodels DescrStatsW and NumPy cov(aweights=) for weights=",
    "table.find_percent_of_rows_where": "narwhals; SciPy (stats.binomtest, the Clopper-Pearson exact interval)",
    "table.compare_spreads_of": "SciPy (stats.levene with center=\"median\", stats.bartlett, stats.fligner)",
    "table.compare_counts_to": "SciPy (stats.chisquare)",
    "table.compare_percent_to": "SciPy (stats.binomtest, the Clopper-Pearson exact interval)",
    "table.find_percentile_of": "narwhals (quantile with linear interpolation, as R quantile type 7); NumPy (percentile "
                           "with test_method=, R's nine types; repeat or percentile(weights=) for weights=); SciPy "
                           "(stats.quantile_test for interval=)",
    "table.find_most_common_of": "narwhals (value counts per group)",
    "table.add_adjusted_p_value_column": "statsmodels (stats.multitest.multipletests: Holm, Bonferroni, "
                                         "Benjamini-Hochberg, Benjamini-Yekutieli, Hochberg and Hommel, as R p.adjust()); "
                                         "R qvalue::qvalue for test_method=\"storey\" and \"local fdr\" (Bioconductor, "
                                         "simplydata[r])",
    "table.add_rows_from": "pandas (concat) or Polars (concat), whichever holds the table",
    "table.find_correlation_between": "SciPy (stats.pearsonr, spearmanr or kendalltau; permutation_test and bootstrap "
                                 "for p_value_by=\"shuffling\" and interval_by=\"bootstrap\"); R DescTools (SpearmanRho, "
                                 "KendallTauB, SomersDelta, GoodmanKruskalGamma) for intervals, R cor.test for Spearman's p-value "
                                 "below 1290 rows without ties (AS 89), ppcor::pcor.test for "
                                 "allowing_for= (simplydata[r]); pandas DataFrame.cov for show=\"covariance\"; "
                                 "statsmodels MICEData and R miceadds::micombine.cor for empty_cells=\"multiple "
                                 "imputation\"",
    "table.compare_correlations": "SciPy (stats.pearsonr); R cocor (cocor.indep.groups, cocor.dep.groups.overlap; "
                                  "simplydata[r])",
    "table.compare_averages_of": "SciPy (stats.ttest_ind with equal_var=False; mannwhitneyu, kruskal) and "
                              "statsmodels (stats.oneway.anova_oneway for Welch's ANOVA; weightstats.ttost_ind "
                              "and CompareMeans for same_within=; nonparametric.jonckheere_terpstra); SciPy "
                              "permutation_test for p_value_by=\"shuffling\"; R wilcox.test for the Hodges-Lehmann "
                              "shift and for the exact Mann-Whitney p-value with tied values (simplydata[r]); R afex::aov_ez for matched_by= (repeated measures, "
                              "Greenhouse-Geisser; needs R); statsmodels OLS on the log scale for period= (the "
                              "2 x 2 crossover, EMA model)",
    "table.compare_each_pair_of": "SciPy (stats.ttest_ind or mannwhitneyu, tukey_hsd, dunnett), with Holm's correction "
                               "from statsmodels (multipletests); R wilcox.test for exact Mann-Whitney p-values with "
                               "tied values; R rstatix::games_howell_test, "
                               "DescTools::ScheffeTest and PostHocTest, FSA::dunnTest, "
                               "PMCMRplus::kwAllPairsConoverTest and multcompView::multcompLetters for "
                               "show=\"letters\" (simplydata[r]); SciPy ttest_rel and wilcoxon for matched_by=, "
                               "R PMCMRplus::frdAllPairsNemenyiTest and frdAllPairsConoverTest after Friedman "
                               "(test_method=); SciPy chi2_contingency or fisher_exact, statsmodels confint_proportions_2indep "
                               "for based_on=\"percents\"",
    "table.compare_before_and_after": "SciPy (stats.ttest_rel or stats.wilcoxon); statsmodels (contingency_tables.mcnemar "
                                  "for yes/no columns, SquareTable.symmetry for categories, sign_test); R "
                                  "exact2x2::mcnemarExactDP for the change in percent (simplydata[r]); "
                                  "statsmodels ttost_paired for same_within=; SciPy permutation_test for "
                                  "p_value_by=\"shuffling\"",
    "table.compare_matched_columns": "SciPy (stats.friedmanchisquare); statsmodels (contingency_tables.cochrans_q for yes/no "
                             "columns); SciPy page_trend_test; R stats::quade.test and effectsize::kendalls_w "
                             "(simplydata[r])",
    "table.compare_shapes_of": "SciPy (stats.ks_2samp; stats.anderson_ksamp with a PermutationMethod); R ks.test for "
                            "the exact p-value with tied values (simplydata[r])",
    "table.check_if_random_order": "statsmodels (sandbox.stats.runs.Runs, runs_test, as runstest_1samp)",
    "sdata.compare_averages": "SciPy (stats.ttest_ind_from_stats); statsmodels (stats.oneway.anova_generic); R "
                              "BSDA::tsum.test for the interval of the difference (simplydata[r])",
    "sdata.compare_counts": "SciPy (stats.chi2_contingency, fisher_exact; contingency.association), as "
                            "table.compare_counts_of",
    # risks, rates and diagnostic tests
    "table.compare_risks": "statsmodels (proportion_confint, confint_proportions_2indep with Newcombe's interval, "
                           "Table2x2, StratifiedTable for allowing_for=, tost_proportions_2indep for same_within=); "
                           "SciPy (chi2_contingency, fisher_exact, contingency.odds_ratio); R epiR::epi.2by2 for the "
                           "interval of the Mantel-Haenszel risk ratio and prop.test for one-sided p-values, and "
                           "epiR::epi.2by2 for show=\"attributable fractions\" (simplydata[r])",
    "table.compare_rates": "statsmodels (stats.rates: confint_poisson, test_poisson_2indep, tost_poisson_2indep); R "
                           "poisson.test for the exact interval of the rate ratio, and epiR::epi.indirectadj for "
                           "standard_rates= (observed / expected; simplydata[r])",
    "table.rate_of": "narwhals (sums per group); statsmodels (stats.rates.confint_poisson, exact); R "
                     "epiR::epi.directadj for standard_population= (simplydata[r])",
    "table.compare_balanced_groups_of": "R WeightIt (weightit, lm_weightit), MatchIt (matchit, match.data) with "
                                        "sandwich::vcovCL and lmtest, and cobalt::bal.tab (simplydata[r])",
    "sdata.compare_risks": "statsmodels and SciPy, as table.compare_risks",
    "sdata.compare_rates": "statsmodels and R poisson.test, as table.compare_rates",
    "table.compare_to_truth": "statsmodels (proportion_confint, exact); R epiR::epi.tests for the likelihood ratios, "
                              "and pROC (roc, ci.auc, coords) for a score column (simplydata[r])",
    "table.compare_accuracy": "R pROC::roc.test (DeLong) and ci.auc (simplydata[r])",
    "sdata.compare_to_truth": "statsmodels (proportion_confint) and R epiR::epi.tests, as table.compare_to_truth",
    "table.agreement_between": "statsmodels (inter_rater.cohens_kappa, fleiss_kappa); R irr::kappam.fleiss for the p-value of Fleiss' kappa, psych::ICC, icr::krippalpha and DescTools::CCC (simplydata[r])",
    "table.limits_of_agreement": "R BlandAltmanLeh::bland.altman.stats and DescTools::CCC (simplydata[r])",
    "table.reliability_of": "R psych::alpha and psych::alpha.ci (simplydata[r])",
    "table.compare_average_to": "SciPy (stats.ttest_1samp or stats.wilcoxon); statsmodels "
                                "(DescrStatsW.ttost_mean for same_within=); R BSDA::z.test for test_method=\"z\" (simplydata[r])",
    "table.compare_counts_of": "SciPy (stats.chi2_contingency, or fisher_exact with test_method=\"fisher\", with a seeded "
                            "MonteCarloMethod for bigger tables; contingency.association for Cramer's V); statsmodels "
                            "Table(shift_zeros=False).standardized_resids for show=\"cells\"; R fisher.test, "
                            "prop.trend.test and Exact::exact.test for test_method=\"barnard\" / \"boschloo\" "
                            "(simplydata[r])",
    "table.show_rows_with_outliers": "narwhals (quartiles, average and standard deviation per group); R "
                                     "outliers::grubbs.test, dixon.test and EnvStats::rosnerTest for the test rules "
                                     "(simplydata[r])",
    "table.remove_rows_with_outliers": "narwhals, as show_rows_with_outliers; R outliers and EnvStats for the test "
                                       "rules (simplydata[r])",
    "table.count_each": "narwhals (counts per value); statsmodels (multinomial_proportions_confint, Sison-Glaz, for "
                        "interval=)",
    "table.compare_shape_to": "SciPy (stats.shapiro for normal, normaltest, jarque_bera, ks_1samp, cramervonmises; "
                              "for other shapes stats.goodness_of_fit, Anderson-Darling with a Monte Carlo p-value); "
                              "R nortest::lillie.test for test_method=\"lilliefors\"; R circular::rayleigh.test on a "
                              "circle (full_turn=; simplydata[r])",
    # fitting
    "table.fit_line": "SciPy (stats.linregress)",
    "table.fit_curve": "statsmodels (WLS by QR on the powers of x, as R lm(y ~ poly(x, raw = TRUE)))",
    "table.fit_formula": "SciPy (optimize.curve_fit; optimize.differential_evolution for search=\"whole range\")",
    "fit_formula": "SciPy (optimize.curve_fit, as table.fit_formula), drawn with matplotlib",
    "fit_distribution": "SciPy (scipy.stats, maximum likelihood as table.fit_distribution_to), drawn with matplotlib",
    "draw_curve": "NumPy (the formula on a grid of x values) or scipy.stats (a distribution), drawn with matplotlib",
    # finding and solving
    "sdata.find_where_smallest": "SciPy (optimize.minimize_scalar, minimize, linprog and milp with HiGHS, "
                           "differential_evolution and other global searches)",
    "sdata.find_where_biggest": "SciPy (the same as find_smallest, on minus the formula)",
    "sdata.solve": "SciPy (optimize.brentq, root_scalar, root) and NumPy (polynomial roots, linalg.solve)",
    # values between points
    "table.values_at": "NumPy (interp) and SciPy (interpolate: CubicSpline, PchipInterpolator, Akima1DInterpolator, "
                       "make_smoothing_spline, griddata, RegularGridInterpolator, RBFInterpolator); "
                       "smoothness=\"auto\" lets R smooth.spline choose the smoothness (needs R)",
    "table.make_map_of": "SciPy (interpolate: RegularGridInterpolator, griddata, RBFInterpolator)",
    # distributions
    "sdata.distribution": "SciPy (scipy.stats frozen distributions)",
    "table.fit_distribution_to": "SciPy (scipy.stats .fit and optimize, maximum likelihood; closed forms where they "
                              "exist) and statsmodels (numdiff.approx_hess3, for the standard errors); for \"kernel density\" SciPy "
                              "gaussian_kde with statsmodels bw_silverman",
    "table.compare_distributions_for": "SciPy (scipy.stats, maximum likelihood; Anderson-Darling, Kolmogorov-Smirnov and "
                                   "Cramer-von Mises statistics)",
    "nums.find_spectrum": "SciPy (signal.periodogram, signal.welch); R lomb::lsp for uneven times (simplydata[r])",
    "table.find_spectrum_of": "SciPy (signal.periodogram, signal.welch); R lomb::lsp for uneven times (simplydata[r])",
    "table.check_steady_over_time": "R (urca::ur.df or tseries::adf.test, and tseries::kpss.test, through rpy2: simplydata[r])",
    "table.find_autocorrelation_of": "statsmodels (tsa.stattools acf, pacf method ywm, acovf, acorr_ljungbox), as R acf, "
                                     "pacf, Box.test; for nearby places (x=, y=) R spdep::moran.mc (needs R)",
    "table.add_trend_and_season": "statsmodels (STL with R's settings, seasonal_decompose, OLS with season effects); "
                                  "R stats::stl(s.window = \"periodic\") for a fixed season (simplydata[r])",
    "table.find_trend_of": "SciPy (stats.theilslopes); R trend::mk.test, smk.test, sea.sens.slope (simplydata[r])",
    "sdata.make_run_of_dates": "pandas (Timestamp, DateOffset)",
    "table.add_missing_dates": "pandas (dates by DateOffset; concat), as reindex / Polars upsample",
    "table.add_smoothed_column": "SciPy (ndimage.convolve1d, gaussian_filter1d, signal.savgol_filter, whittaker_henderson, "
                                 "wiener), pandas (rolling, ewm), statsmodels (lowess); R stats::runmed for the median "
                                 "(simplydata[r])",
    "nums.smooth": "as table.add_smoothed_column",
    "nums.remove_trend": "SciPy (signal.detrend)",
    "nums.keep_each_frequency_that": "SciPy (signal.butter, cheby1, cheby2, ellip, bessel as sos; iirpeak; sosfiltfilt, sosfilt)",
    "nums.remove_each_frequency_that": "SciPy (as keep_each_frequency_that; iirnotch, iircomb)",
    "table.add_filtered_column": "SciPy (as nums.keep_each_frequency_that)",
    "nums.find_each_peak_that": "SciPy (signal.find_peaks, peak_prominences, peak_widths)",
    "nums.find_each_dip_that": "SciPy (signal.find_peaks on minus the numbers)",
    "table.find_each_peak_that": "SciPy (signal.find_peaks, peak_prominences, peak_widths)",
    "table.find_each_dip_that": "SciPy (signal.find_peaks on minus the column)",
    "nums.take_fourier_transform": "SciPy (fft.rfft, fft.fft)",
    "sdata.find_inverse_fourier_transform": "SciPy (fft.irfft, fft.ifft)",
    "nums.find_envelope": "SciPy (signal.hilbert)",
    "nums.convolve_with": "SciPy (signal.convolve)",
    "nums.deconvolve_by": "SciPy (signal.deconvolve)",
    "nums.change_time_step": "SciPy (signal.resample, resample_poly, decimate)",
    "sdata.make_wave": "SciPy (signal.square, sawtooth, chirp, gausspulse, unit_impulse) and NumPy sin",
    "sdata.make_window_shape": "SciPy (signal.get_window)",
    "table.add_envelope_column": "SciPy (signal.hilbert)",
    "sdata.frequency_filter": "SciPy (the designs of nums.keep_each_frequency_that; sosfreqz, sos2zpk, sosfilt)",
    "system.step_response": "SciPy (signal.step, dstep); python-control (step_info) for the rise time, settling time "
                            "and overshoot (simplydata[systems])",
    "system.frequency_response": "SciPy (signal.freqresp, freqz); python-control (stability_margins) for the gain and "
                                 "phase margins (simplydata[systems])",
    "sticks": "matplotlib (vlines and plot)",
    "autocorrelation_bars": "statsmodels (as table.find_autocorrelation_of), drawn with matplotlib",
    "cross_correlation_bars": "statsmodels (as table.find_correlation_between with rows_back=), drawn with matplotlib",
    "lag_dots": "pandas (shift), drawn with matplotlib",
    "trend_and_season": "statsmodels (as table.add_trend_and_season), drawn with matplotlib",
    "forecast": "R (as table.forecast, through rpy2: simplydata[r]), drawn with matplotlib",
    "spectrum": "SciPy (as table.find_spectrum_of; lomb-scargle from R lomb), drawn with matplotlib",
    "spectrum_over_time": "SciPy (signal.spectrogram), drawn with matplotlib (pcolormesh)",
    "peak_dots": "SciPy (as table.find_each_peak_that), drawn with matplotlib",
    "table.forecast": "R (forecast::naive, snaive, meanf, rwf; stats::HoltWinters, stats::arima, forecast::auto.arima "
                      "for order=\"automatic\"; forecast::forecast and accuracy, through rpy2: simplydata[r])",
    "nums.forecast": "R (as table.forecast, through rpy2: simplydata[r])",
    "table.compare_forecasts_for": "R (forecast::accuracy on each method's forecast, through rpy2: simplydata[r])",
    "table.find_change_points_in": "R (changepoint::cpt.mean and cpt.meanvar, PELT; stats::mad; through rpy2: simplydata[r])",
    "nums.find_autocorrelation": "statsmodels (tsa.stattools acf, pacf method ywm, acovf, acorr_ljungbox), as R acf, pacf, Box.test",
    "nums.fit_distribution": "SciPy (scipy.stats and optimize, as table.fit_distribution_to)",
    # models
    "table.explain": "statsmodels (OLS; GLM for yes/no and counts, as R glm; MixedLM for grouped_by=; GEE for "
                     "effects=\"for the whole population\", as R geepack::geeglm; MICEData to fill in empty cells; "
                     "eval_measures aic and bic and McFadden's pseudo R squared, as R AIC, BIC and "
                     "performance::r2_mcfadden); R mgcv::gam for curve_for= (needs R); "
                     "R itself (needs R) for lme4::glmer, lme4::lmer with own_slope_for=, lmerTest for "
                     "p_value_by=\"satterthwaite\", geepack for within_groups=\"in time order\" and GEE with out_of=, car::Anova and "
                     "effectsize for table_of_tests=, sandwich::vcovHC for robust_errors=True with yes/no and counts, and mice::pool for "
                     "multiple imputation; R performance::r2_nakagawa for the R squared of every grouped_by= model; "
                     "statsmodels WLS and GLM(var_weights=) for weights=, RLM for giving_outliers_less_weight=, "
                     "ConditionalLogit for matched_by=, GLM(cov_type=\"HC0\") for risk ratios; patsy cr for "
                     "with_knots=; SciPy bootstrap for interval_by=\"bootstrap\"; R stats::confint for "
                     "interval_by=\"profile\", lme4 for crossed_with=, pscl::zeroinfl and pscl::hurdle for the "
                     "zero outcomes; statsmodels stats.mediation.Mediation for through= (as R mediation::mediate)",
    "table.add_predicted_column": "statsmodels (the same model as table.explain; get_prediction for interval= and for_new_rows=)",
    "table.find_model_averages_of": "R emmeans (emmeans::emmeans and pairs, Tukey's adjustment; lme4 and pbkrtest for "
                               "grouped_by=; MASS, nnet, betareg and pscl for the other outcomes), on the model of "
                               "table.explain (needs R)",
    "table.check_model_of": "statsmodels (OLSInfluence, GLMInfluence, MixedLM, ProbPlot and lowess), the pictures of R "
                         "plot(lm), plot(glm) and plot(lmer) with qqnorm(ranef), drawn with matplotlib; R lme4::glmer "
                         "for yes/no and counts with grouped_by=; statsmodels variance_inflation_factor (least "
                         "squares) or R car::vif (GLMs, group columns) for the variance inflation factors; with "
                         "test_method=\"bayesian\" R rstanarm (posterior_predict, prior_PD) and stats::density",
    "table.show_rows_that_pull_model": "statsmodels (OLSInfluence, GLMInfluence), as R cooks.distance, hatvalues and "
                                 "rstudent; R lme4 influence() and cooks.distance() for whole groups with grouped_by=",
    "table.compare_models": "statsmodels (OLS compare_f_test; GLM deviances and log-likelihoods with SciPy's chi-square "
                            "and F; MixedLM refitted by maximum likelihood; eval_measures aic and bic), as R anova(m0, "
                            "m1), lmtest::lrtest, AIC and BIC; R for glmer, betareg and zeroinfl models",
    # patterns across columns
    "table.add_principal_components": "statsmodels (multivariate.pca.PCA, by singular value decomposition)",
    "table.find_principal_components_of": "statsmodels (multivariate.pca.PCA, by singular value decomposition)",
    "table.add_clusters": "R stats::kmeans (k-means; needs R) or SciPy (cluster.hierarchy, for "
                          "test_method=\"hierarchical\"); the silhouette width from R cluster::silhouette",
    "table.find_distances_between_rows": "SciPy (spatial.distance.pdist); R vegan::vegdist for the Aitchison, "
                                         "robust Aitchison and Hellinger distances",
    "table.add_nmds": "R vegan::metaMDS on vegan::vegdist distances (needs R)",
    "table.compare_profiles_of": "R vegan::adonis2 or anosim, betadisper and permutest; simper for "
                                 "show=\"contributions\" (needs R)",
    # survival
    "table.find_survival_over_time": "statsmodels (duration.SurvfuncRight, Kaplan-Meier with Greenwood errors)",
    "table.compare_survival": "statsmodels (duration.survdiff, the log-rank test)",
    "table.explain_survival": "statsmodels (duration.PHReg, the Cox model with Efron ties) and R "
                              "survival::cox.zph for the proportional-hazards check (needs R); statsmodels MICEData, "
                              "R survival::coxph and mice::pool for empty_cells=\"multiple imputation\"",
    "draw_survival_curves": "statsmodels (Kaplan-Meier, as table.find_survival_over_time), drawn with matplotlib",
    # planning a study
    "sdata.find_how_many_needed": "statsmodels (stats.power: TTestIndPower, TTestPower, FTestAnovaPower, "
                             "GofChisquarePower, solve_power); R pwr::pwr.r.test, power.prop.test, "
                             "TOSTER::power_t_TOST and presize::prec_mean (simplydata[r])",
    "sdata.find_chance_of_finding": "statsmodels (stats.power classes; proportion.power_proportions_2indep for percents=); "
                            "R pwr::pwr.r.test and TOSTER::power_t_TOST (simplydata[r])",
    "table.save": "pandas (to_excel, to_csv ...) or Polars, whichever holds the table",
    "table.start_chart": "matplotlib and seaborn (the chart is drawn from a pandas copy of the table)",
    "table.as_pandas": "pandas",
    "table.as_polars": "Polars",
    # numbers
    "sdata.make_random_numbers": "NumPy (random.default_rng)",
    "nums.find_percentile": "NumPy (nanpercentile, the usual \"linear\" method, as pandas and R)",
    "nums.turn_into_table": "pandas",
    "nums.start_chart": "matplotlib and seaborn, from a pandas table with one column called value",
    "nums.save": "pandas (to_csv, to_excel ...)",
    "nums.keep_random_numbers": "NumPy (random.default_rng)",
    "nums.fill_empty_numbers": "NumPy (interp for the line between neighbours)",
    # S3a-2: lines and curves (each also has a tested entry in simplydata._underneath)
    "table.fit_dose_response": "R drc (drm, ED with delta-method intervals, EDcomp, noEffect)",
    "fit_dose_response": "R drc (drm, ED), drawn with matplotlib",
    "table.find_best_power_of": "SciPy (stats.boxcox, stats.yeojohnson); R car::powerTransform with using=",
    # S3a-3: checking and comparing (each also has a tested entry in simplydata._underneath)
    "table.find_columns_that_predict": "R glmnet (cv.glmnet, coef at lambda.1se)",
    "table.find_group_levels_of": "R lme4 (ranef with condVar, coef)",
    "draw_interaction_lines": "pandas (averages), SciPy (t intervals), drawn with seaborn and matplotlib",
    # S3b-3: survival and person-time (each also has a tested entry in simplydata._underneath)
    "table.add_time_and_event_columns": "pandas and NumPy date arithmetic (a year of 365.25 days)",
    "table.find_risk_over_time": "R survival (survfit with a factor event, Aalen-Johansen); statsmodels "
                                 "(SurvfuncRight) with one kind of event",
    "draw_risk_curves": "as table.find_risk_over_time, drawn with matplotlib",
    # S3b-1: combining studies (each also has a tested entry in simplydata._underneath)
    "table.combine_studies": "R metafor (escalc or conv.wald, rma with REML and Hartung-Knapp, rma.mh, rma.peto, "
                             "predict, confint, regtest, trimfill)",
    "draw_funnel_plot": "matplotlib (scatter, plot), the funnel limits from SciPy (stats.norm / stats.lognorm "
                        "interval)",
    # S3c-1: communities and resistomes (each also has a tested entry in simplydata._underneath)
    "table.add_diversity_columns": "R vegan (specnumber, diversity, renyi, estimateR, rarefy; needs R)",
    "table.add_log_ratio_columns": "R zCompositions (cmultRepl, GBM) and compositions (clr, alr, ilr); vegan "
                                   "decostand for a pseudocount (needs R)",
    "table.add_principal_coordinates": "R stats::cmdscale on vegan::vegdist distances (needs R)",
    "table.explain_profiles_of": "R vegan (dbrda, rda, cca, RsquareAdj, anova by margin; needs R)",
    "table.find_correlation_between_profiles": "R vegan (mantel, protest; needs R)",
    "table.add_axes_that_separate_groups": "R MASS (lda, predict, lda with CV = TRUE; needs R)",
    "table.add_correspondence_axes": "R vegan::cca (CA) or ca::mjca (MCA; needs R)",
    "draw_richness_curves": "R vegan::rarecurve (needs R), drawn with matplotlib",
    "draw_cluster_tree": "SciPy (cluster.hierarchy linkage, dendrogram, cophenet), drawn with matplotlib; vegan "
                         "vegdist for the Aitchison and Hellinger distances",
    # S3c-2: hidden factors (each also has a tested entry in simplydata._underneath)
    "table.find_hidden_factors_behind": "R psych (fa.parallel, fa with minres and oblimin, KMO) with GPArotation",
    "table.check_hidden_factors": "R lavaan (cfa or sem with maximum likelihood, fitMeasures, standardizedSolution, "
                                  "modindices)",
    # S3c-3: directions, places and extremes (each also has a tested entry in simplydata._underneath)
    "table.find_average_direction_of": "SciPy (stats.circmean, circstd, circvar, directional_stats)",
    "table.find_variogram_of": "R gstat (variogram, fit.variogram, variogramLine; needs R)",
    "table.find_return_levels_of": "R extRemes (fevd, return.level, ci.fevd with the profile likelihood, "
                                   "extremalindex; needs R)",
    "draw_variogram": "R gstat (variogram, fit.variogram, variogramLine; needs R), drawn with matplotlib",
    "draw_threshold_check": "R extRemes (mrlplot, threshrange.plot; needs R), drawn with matplotlib",
    # S3d-1: planning and surveys (each also has a tested entry in simplydata._underneath)
    "sdata.make_design_table": "R agricolae (design.crd, design.rcbd, design.ab, design.lsd, design.split with "
                               "kinds = \"Mersenne-Twister\"; needs R)",
    "sdata.make_random_assignments": "R blockrand (blockrand, with set.seed(kind = \"Mersenne-Twister\"); needs R)",
    "table.use_survey_design": "R survey (svydesign, degf; then svymean, svytotal, svyquantile, svyciprop, svyby, "
                               "svyglm, svyttest, svychisq; needs R)",
    "draw_answer_bars": "pandas (value_counts), drawn with matplotlib (barh)",
}

# ---------------------------------------------------------------- hand-written text
GETTING_STARTED = r"""
\unchapter{Welcome}{start:welcome}

\textbf{simplydata} gives you one small vocabulary of plain English words for working with data:
reading a table, cleaning it, summing it up, testing a difference and drawing a chart. Underneath,
the work is done by the libraries that scientists use every day: pandas and Polars for tables,
NumPy for numbers, SciPy for statistics, and matplotlib and seaborn for charts. You learn the
words; simplydata picks the right call in the right library, with the right settings.

\begin{lstlisting}[style=py]
import simplydata as sdata

table = sdata.table(sdata.get_example("marks"))   # or your own: sdata.table("marks.xlsx")
table.keep_rows_where("marks", is_above=50)
table.find_average_of("marks", for_each_group_in="class")   # says the answer in a sentence
table.save("good_marks.xlsx")

chart = table.start_chart()                         # or sdata.chart(table)
chart.draw_bars(x="class", y="marks", error="standard error")
chart.write_title_on_top("Good marks in each class")
chart.save("marks.png")
\end{lstlisting}

The program reads like a list of instructions, one step on each line. A table, a chart and a list
of numbers are separate objects, as in pandas, NumPy and matplotlib: one cleaned table can feed
many charts, and several charts can share one page.

\section*{Who this manual is for}
Everyone who wants to learn data science with Python: school pupils, students, teachers and
researchers. You do not need to know Python first. Every word is simple enough for a child to read,
and every result names the technical term (``Welch's t-test'', ``linear regression'') so that you
can write it up in a report or a paper.

\section*{How this manual is built}
\begin{description}[style=nextline,leftmargin=1.2em]
  \item[{\hyperref[part:lessons]{Part II: Lessons}}] @LESSON_COUNT@ short lessons that teach the whole
    of simplydata in a day. Each lesson shows code you can run, says what every line does, shows
    the real chart and output it makes, and ends with tasks to try yourself.
  \item[{\hyperref[part:dictionary]{Part III: Dictionary of words}}] Every word, with what it does,
    its options, an example you can run and the library it uses underneath.
  \item[{\hyperref[part:ideas]{Part IV: Data science ideas}}] The ideas behind the numbers in plain
    words: average and median, standard deviation and standard error, confidence intervals,
    p-values, effect sizes, and a guide to which statistical test to use when.
  \item[{\hyperref[part:solutions]{Part V: Solutions}}] A worked solution for every
    ``Try it yourself'' task.
\end{description}
Everything in this manual is made from simplydata's own code by \code{docs/make\_manual.py}: the
examples were run to make the charts and the printed output you see, so they are exactly what you
will get.

\unchapter{Install and first steps}{start:install}

\section*{Install}
\begin{lstlisting}[style=plain]
pip install simplydata            # coming soon
pip install simplydata[fast]      # adds Polars, the fast engine for big data
\end{lstlisting}

\section*{Where to type the code}
Any place that runs Python works. In \textbf{Jupyter}, \textbf{VS Code} or \textbf{Spyder}, a chart
appears by itself when you write \code{chart} on the last line of a cell. In a script,
\code{chart.show()} opens it in a window, and \code{chart.save("name.png")} always saves it as a file.

\section*{simplydata teaches itself}
\begin{lstlisting}[style=py]
import simplydata as sdata
sdata.show_lesson()                      # lists the lessons
sdata.show_lesson(1)                     # the first lesson
sdata.show_lesson(1, solutions=True)     # the first lesson, with worked solutions to its tasks
sdata.show_all_words()                       # every word, with a short example
sdata.help("draw_bars")                  # one word: what it does, its options and an example
sdata.get_example()                     # the made-up tables you can practise with
sdata.start_30_days()               # or learn it in 30 days of about an hour,
sdata.show_today()                       # ... with sdata.show_today() each day
sdata.show_packages_used()               # the packages that did the work, and how to cite them
\end{lstlisting}
Rather learn an hour a day? \code{sdata.start\_30\_days()} spreads the everyday lessons over 30 days, each with
a warm-up of questions on earlier days and a task, and a project of your own at the end
(\code{track="beginner"} starts with just enough Python). The printable guide,
\href{simplydata_30_days.pdf}{\code{simplydata\_30\_days.pdf}}, has the same days on paper.

\section*{Cite the packages underneath}
simplydata does its work with pandas, Polars, NumPy, SciPy, statsmodels, matplotlib, seaborn and R,
and their authors ask to be cited. At the end of a script simplydata prints a short list of the
packages your words used, with their versions and references; \code{sdata.show\_packages\_used()}
gives the full references and a sentence for your methods, and
\code{sdata.show\_packages\_used(save\_as="references.bib")} saves them as BibTeX. The list is not
printed in Jupyter or an interactive session; \code{sdata.show\_packages\_used(at\_end=False)} or the
environment variable \code{SIMPLYDATA\_NO\_CITE\_LIST=1} switches it off.

\section*{Your own data}
\code{sdata.table("my\_file.xlsx")} and \code{sdata.chart("my\_file.xlsx")} read Excel, CSV, TSV,
Parquet and JSON files. They also take a pandas or Polars table you already have, or a small table
typed by hand: \code{sdata.table(\{"name": ["Asha", "Ben"], "height": [144, 152]\})}. Your file is
never changed: only \code{table.save(...)} writes a file.

\section*{When something goes wrong}
simplydata explains its errors in plain words. Misspell a column and it says which columns there
are and which one you probably meant. Ask for a word that does not exist and \code{sdata.help}
suggests the nearest one. A missing word can be requested on GitHub, at
\url{https://github.com/bioforkgithub/simplydata/issues}.

\unchapter{How the words are built}{start:grammar}

A line of simplydata reads like an instruction you say to the program: the thing (a chart, a
table, numbers), then a verb that says what it should do, then the details as options:
\code{table.keep\_rows\_where("marks", is\_above=50)}, \code{chart.draw\_bars(x="class", y="marks")}.
A longer word is fine when it makes the line clearer read aloud. A few rules make the words easy to
guess. If you know one word of a pattern, you can usually guess its siblings.

\begin{center}
\small
\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.33\textwidth}>{\raggedright\arraybackslash}X@{}}
\toprule
\textbf{Pattern} & \textbf{Examples}\\
\midrule
\textbf{verb + thing} changes a table or numbers; a small word at the end joins the first input
  & \code{keep\_rows\_where}, \code{remove\_columns}, \code{fill\_empty\_cells\_in}, \code{add\_column},
    \code{keep\_each\_number\_that}\\
\textbf{get\_} takes one piece out; \textbf{take\_} does maths on every number; \textbf{make\_} makes
something new; \textbf{turn\_into\_} gives the same data as another kind
  & \code{get\_column}, \code{take\_log}, \code{make\_random\_numbers}, \code{turn\_into\_numbers}\\
\textbf{draw\_ + chart type}
  & \code{chart.draw\_bars(...)}, \code{chart.draw\_histogram(...)}, \code{chart.draw\_dots(...)}\\
\textbf{verb + thing + where} places or sets something on a chart
  & \code{write\_title\_on\_top}, \code{label\_y}, \code{draw\_line\_at\_y}, \code{put\_legend\_at\_bottom},
    \code{set\_range\_y}, \code{use\_colour}\\
\textbf{find\_ + measure + \_of} sums up one column; \textbf{find\_ + relation + \_between} links two;
\textbf{compare\_ + measure + \_of} tests groups, \textbf{\_to} tests against one value
  & \code{find\_average\_of}, \code{find\_median\_of}, \code{find\_correlation\_between},
    \code{compare\_averages\_of}, \code{compare\_average\_to}\\
\textbf{show\_ / hide\_ + thing} looks without changing
  & \code{show\_first\_rows}, \code{show\_grid}, \code{hide\_legend}, \code{show\_steps}\\
\textbf{as\_ + library} hands the data on; \textbf{save} writes a file
  & \code{as\_pandas}, \code{as\_polars}, \code{as\_numpy}; \code{table.save("clean.xlsx")}\\
\bottomrule
\end{tabularx}
\end{center}

\begin{itemize}
  \item \textbf{One option name, one meaning, everywhere:} \code{for\_each\_group\_in=} (groups),
    \code{colour=} (one colour, or a colour per group), conditions that start with \code{is\_}
    (\code{is\_above=}, \code{is\_one\_of=}, \code{is\_between=[low, high]}), \code{between=[low, high]}
    for a span, switches that start with \code{with\_} (\code{with\_dots=True}, \code{with\_seed=1}),
    \code{from\_column=}, \code{with\_value=}, \code{biggest\_first=}, \code{per\_row=}, \code{labelled=},
    \code{fast=}.
  \item \textbf{Measure names are the same wherever they appear:} \code{"average"}, \code{"median"},
    \code{"total"}, \code{"count"}, \code{"smallest"}, \code{"biggest"}, \code{"standard deviation"},
    \code{"standard error"}, \code{"confidence interval"}.
  \item \textbf{Axes are x and y.} Anything that belongs to one axis ends in \code{\_x} or \code{\_y}:
    \code{label\_y}, \code{set\_range\_x}, \code{use\_log\_scale\_y}.
  \item \textbf{The word names the idea}, and the printed answer names the technical term, so you can
    follow (and write) the Methods section of a paper.
  \item \textbf{Order does not matter} on a chart: after the chart type, write the other steps in any
    order. Both \code{colour} and \code{color}, \code{grey} and \code{gray} work.
  \item \textbf{Every change can be taken back}: tables and numbers remember each step, so
    \code{undo()}, \code{show\_steps()} and \code{start\_again()} always work.
  \item \textbf{Old names keep working for one release.} A word that was renamed still runs and
    prints one line, once, with its new name; \code{sdata.help("old\_name")} points to the new word.
\end{itemize}
"""

# Family of chapters in the dictionary: chosen from the kind of the words in each group.
FAMILY_TITLES = {
    "chart": ("Chart words", "Steps on a chart: \\code{chart = sdata.chart(table)}, then "
                             "\\code{chart.draw\\_bars(...)}. Words that start with \\code{sdata.} are called on "
                             "simplydata itself, and words that end in \\code{=} are options inside a chart step."),
    "table": ("Table words", "Steps on a table: \\code{table = sdata.table(...)}, then "
                             "\\code{table.keep\\_rows\\_where(...)}. Table words work the same on pandas and Polars tables. "
                             "Words that start with \\code{sdata.} (finding and solving, planning a study) are "
                             "called on simplydata itself, and words that start with \\code{dist.} are steps on "
                             "a distribution: \\code{dist = sdata.distribution(\"normal\")}."),
    "numbers": ("Number words", "Steps on numbers, \\code{nums = sdata.numbers([12, 15, 9, 20, 14])}, "
                                "on grids of numbers, \\code{grid = sdata.number\\_grid([[3, 5, 2], [8, 6, 4]])}, "
                                "and on systems, \\code{system = sdata.system(\"1 / (s**2 + 2*s + 5)\")}."),
    "help": ("Help words", "Words that teach simplydata."),
}


# ---------------------------------------------------------------- LaTeX text
_UNICODE = {
    "°": r"\textdegree{}", "²": r"\textsuperscript{2}", "³": r"\textsuperscript{3}", "⁴": r"\textsuperscript{4}", "·": r"\textperiodcentered{}",
    "×": r"\texttimes{}", "−": r"\textminus{}", "±": r"\textpm{}", "–": "--", "—": "---", "…": r"\dots{}",
    "≈": r"$\approx$", "µ": r"\textmu{}", "é": r"\'e", "’": "'", "‘": "`", "“": "``", "”": "''",
    "á": r"\'a", "í": r"\'{\i}", "ä": r"\"a", "ö": r"\"o", "ü": r"\"u", "ñ": r"\~n", "ß": r"\ss{}", "Ø": r"\O{}", "χ": r"$\chi$",
    "š": r"\v{s}",
}
_SPECIAL = {
    "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#",
    "^": r"\textasciicircum{}", "_": r"\_", "%": r"\%", "~": r"\textasciitilde{}",
    "<": r"\textless{}", ">": r"\textgreater{}", "|": r"\textbar{}", '"': r"\textquotedbl{}",
}


def esc(text: str) -> str:
    """Escape plain text for LaTeX: special characters and the few non-ASCII ones we use."""
    out = []
    for ch in str(text):
        if ch in _SPECIAL:
            out.append(_SPECIAL[ch])
        elif ch in _UNICODE:
            out.append(_UNICODE[ch])
        elif ord(ch) > 126:
            raise ValueError(f"Add {ch!r} (U+{ord(ch):04X}) to _UNICODE in docs/make_manual.py")
        else:
            out.append(ch)
    text = "".join(out)
    return text.replace("--", "-{}-").replace("``", "`{}`").replace("''", "'{}'")


def code(text: str) -> str:
    """Inline code: typewriter font, escaped. A long piece may break after a dot, comma or
    underscore, so it never sticks out into the margin."""
    text = esc(text)
    for mark in (".", ",", r"\_"):
        text = text.replace(mark, mark + r"\allowbreak{}")
    return r"\code{" + text + "}"


# Code inside prose: a call such as chart.draw_bars(...), an option such as show="median", a
# "quoted value", a dotted or underscored name (table.save, keep_rows_where) or a file ending (.xlsx).
_CALL = re.compile(r"(?<![\w.])[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\(")
_OPTION = re.compile(r"(?<![\w.])[a-z_][a-z0-9_]*=(?!=)")
_QUOTED = re.compile(r'"[^"\n]*"')
_NAME = re.compile(r"(?<![\w.])(?:(?:sdata|chart|table|nums|grid|page)\.\w+(?:\(\))?|[A-Za-z]\w*_\w*(?:\(\))?)")
_ENDING = re.compile(r"(?<![\w])\.(?:png|pdf|svg|jpg|tif|gif|xlsx|csv|tsv|parquet|json)\b")


def _balanced(text: str, start: int, open_ch: str, close_ch: str) -> int | None:
    """Index just after the bracket that closes the one at text[start], quotes respected."""
    depth, quote = 0, None
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def _code_span(text: str, i: int) -> int | None:
    """If a piece of code starts at text[i], the index where it ends; else None."""
    m = _CALL.match(text, i)
    if m:
        end = _balanced(text, m.end() - 1, "(", ")")
        if end:
            return end
    m = _OPTION.match(text, i)
    if m:
        j = m.end()
        if j < len(text) and text[j] == '"':
            close = text.find('"', j + 1)
            return close + 1 if close > 0 else j
        if j < len(text) and text[j] == "[":
            return _balanced(text, j, "[", "]") or j
        value = re.match(r"[\w.\-]*", text[j:])
        return j + len(value.group(0).rstrip("."))
    for pattern in (_QUOTED, _NAME, _ENDING):
        m = pattern.match(text, i)
        if m:
            return m.end()
    return None


def rich(text: str) -> str:
    """Prose with the pieces of code in it set in typewriter font."""
    out, plain, i = [], [], 0
    while i < len(text):
        end = _code_span(text, i) if (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")) else None
        if end:
            out.append(esc("".join(plain)))
            plain = []
            out.append(code(text[i:end]))
            i = end
        else:
            plain.append(text[i])
            i += 1
    out.append(esc("".join(plain)))
    return "".join(out)


def label(key: str) -> str:
    """A LaTeX label for a word: "table.keep_rows_where" -> "word:table.keep-rows"."""
    return "word:" + key.replace("_", "-").replace("=", "-eq")


def listing(source: str, style: str = "py") -> str:
    return f"\\begin{{lstlisting}}[style={style}]\n{source.rstrip()}\n\\end{{lstlisting}}"


# ---------------------------------------------------------------- figures and printed output
_SAVE = re.compile(r'\.save\("([^"]+)"')


def saved_images(source: str) -> list[tuple[str, str]]:
    """(stem, type) of each picture the code saves, once per name: a chart saved as .png and .pdf
    is one picture."""
    seen, found = set(), []
    for name in _SAVE.findall(source):
        stem, _, kind = name.rpartition(".")
        if kind.lower() in IMAGE_TYPES and stem not in seen:
            seen.add(stem)
            found.append((stem, kind.lower()))
    return found


def figure_files(prefix: str, source: str) -> list[str]:
    """The files (relative to docs/manual) that hold the pictures of one example."""
    return [f"figures/{prefix}_{stem}.{'png' if kind == 'gif' else 'pdf'}" for stem, kind in saved_images(source)]


def figure_block(prefix: str, source: str, caption: str, width: float, height: float,
                 numbered: bool = True) -> str:
    """The pictures an example saved, side by side, with a caption that names the files."""
    files = figure_files(prefix, source)
    if not files:
        return ""
    names = [f"{stem}.{kind}" for stem, kind in saved_images(source)]
    each = width if len(files) == 1 else min(width, 0.96 / len(files))
    pics = "\\hfill".join(
        f"\\includegraphics[width={each:.2f}\\textwidth,height={height:.2f}\\textheight,keepaspectratio]{{{f}}}"
        for f in files)
    what = " and ".join(code(n) for n in names)
    gif = any(n.endswith(".gif") for n in names)
    note = " (the last picture of the animation)" if gif else ""
    star = "" if numbered else "*"
    return ("\\begin{center}\\begin{minipage}{\\linewidth}\\centering\n" + pics
            + f"\n\\captionof{star}{{figure}}{{" + caption + " " + what + note
            + ".}\n\\end{minipage}\\end{center}")


def output_block(prefix: str) -> str:
    return f"\\printedoutput{{output/{prefix}.txt}}"


def _lesson_prefix(number: int, part: int) -> str:
    return f"lesson{number:02d}_example{part}"


def _solution_prefix(number: int, task: int) -> str:
    return f"solution{number:02d}_task{task}"


def jobs() -> list[tuple[str, str]]:
    """(prefix, code) for every lesson example and every solution: what the build runs."""
    found = []
    for number in range(1, len(learn.LESSONS) + 1):
        for part, source in enumerate(learn.lesson_code(number), start=1):
            found.append((_lesson_prefix(number, part), source))
        for task, (source, _) in enumerate(learn.lesson_solutions(number), start=1):
            found.append((_solution_prefix(number, task), source))
    return found


# ---------------------------------------------------------------- the parts of the book
HEADER = """\
% ---------------------------------------------------------------------------------------------
% The simplydata manual. This file is made by docs/make_manual.py from simplydata's own code.
% Do not edit it by hand: change simplydata/learn.py, a docstring, docs/manual/preamble.tex or
% docs/manual/ideas.tex, then run   python docs/make_manual.py
% ---------------------------------------------------------------------------------------------"""


def _preamble() -> str:
    return HEADER + "\n" + (MANUAL / "preamble.tex").read_text(encoding="utf-8").strip()


def _title_page() -> str:
    return r"""
\begin{titlepage}
\begin{tikzpicture}[remember picture,overlay]
  \fill[brand] (current page.north west) rectangle ([yshift=-9.5cm]current page.north east);
\end{tikzpicture}
\vspace*{1.2cm}
{\color{white}\sffamily
{\fontsize{46}{50}\selectfont\bfseries simplydata\par}
\vspace{0.5cm}
{\LARGE simple words for data science\par}
\vspace{0.4cm}
{\large The manual: lessons, every word, the ideas behind them, and solutions\par}}
\vspace{3.2cm}
{\sffamily\Large\bfseries\color{brand} Learn basic Python, and simplydata takes you from your first table to publication-ready statistics, in plain words, with every number checked against the field's standard tools.\par}
\vspace{1.2cm}
\begin{lstlisting}[style=title]
import simplydata as sdata

table = sdata.table(sdata.get_example("marks"))
table.compare_averages_of("marks", for_each_group_in="class")
chart = table.start_chart()
chart.draw_boxes(x="class", y="marks")
chart.save("marks.png")
\end{lstlisting}
\vfill
{\sffamily
\textbf{Version @VERSION@}\\[0.3em]
Open source (MIT licence): \url{https://github.com/bioforkgithub/simplydata}\\[0.3em]
Made from the code by \code{docs/make\_manual.py}; every example in it was run to make its chart.\par}
\end{titlepage}
""".replace("@VERSION@", esc(simplydata.__version__))


def _practice_tables() -> str:
    lines = [r"\unchapter{The practice tables}{start:tables}",
             "All the examples use small made-up tables that come with simplydata, so they run "
             "anywhere without a file. Every number in them is invented. Get one with "
             + code('sdata.get_example("marks")') + ", and list them all with " + code("sdata.get_example()") + "."]
    for name, (about, columns) in EXAMPLES.items():
        lines.append(f"\\section*{{{esc(name)}}}")
        lines.append(rich(about) + " " + code(f'sdata.get_example("{name}")'))
        lines.append("\\begin{center}\\small")
        lines.append(r"\begin{tabularx}{\textwidth}{@{}>{\ttfamily}l>{\raggedright\arraybackslash}X@{}}")
        lines.append(r"\toprule \textrm{\textbf{Column}} & \textbf{What it holds}\\ \midrule")
        for column, meaning in columns.items():
            lines.append(f"{esc(column)} & {rich(meaning)}\\\\")
        lines.append(r"\bottomrule\end{tabularx}\end{center}")
    return "\n".join(lines)


def _lesson(number: int, aliases_lookup) -> str:
    les = learn.LESSONS[number - 1]
    out = [f"\\chapter{{{esc(les['title'])}}}\\label{{lesson:{number}}}"]
    out.append(r"\begin{learnbox}")
    out.append(r"\begin{itemize}")
    out += [f"  \\item {rich(item)}" for item in les["learn"]]
    out.append(r"\end{itemize}")
    out.append(r"\end{learnbox}")
    if les.get("needs_r"):
        out.append(r"\begin{needsr}" + rich(les["needs_r"]) + r"\end{needsr}")
    parts = les["parts"]
    for i, (intro, steps) in enumerate(parts, start=1):
        heading = "Example" if len(parts) == 1 else f"Example {i}"
        out.append(f"\\section*{{{heading}}}")
        out.append(rich(intro))
        source = "\n".join(c for c, _ in steps)
        out.append(listing(source))
        out.append(r"\whateachline")
        out.append(r"\begin{lineexplain}")
        for line_no, (_, explain) in enumerate(steps, start=1):
            if explain:
                out.append(f"  \\item[{line_no}] {rich(explain)}")
        out.append(r"\end{lineexplain}")
        prefix = _lesson_prefix(number, i)
        out.append(output_block(prefix))
        fig = figure_block(prefix, source, f"Lesson {number}, {heading.lower()}:", 0.72, 0.36)
        if fig:
            out.append(fig)
    if les.get("notes"):
        out.append(r"\begin{goodtoknow}")
        out.append(r"\begin{itemize}")
        out += [f"  \\item {rich(note)}" for note in les["notes"]]
        out.append(r"\end{itemize}")
        out.append(r"\end{goodtoknow}")
    out.append(r"\begin{tryit}")
    out.append(r"\begin{enumerate}")
    out += [f"  \\item {rich(task)}" for task in les["task"]]
    out.append(r"\end{enumerate}")
    out.append(f"Worked solutions: page~\\pageref{{solutions:{number}}}, "
               f"or type {code(f'sdata.show_lesson({number}, solutions=True)')}.")
    out.append(r"\end{tryit}")
    words = []
    for word in les["words"]:
        key = learn._lookup(word)
        words.append(f"\\hyperref[{label(key)}]{{{code(learn._call_form(key))}}}")
    out.append(r"\par\noindent{\small\sffamily\textbf{Words in this lesson:} " + ", ".join(words) + ".\\par}")
    return "\n".join(out)


def _options_table(key: str) -> str:
    """The options in the brackets, as sdata.help shows them: "needed", "normally ..." or nothing
    (no fixed value: the text above says what it does)."""
    func = learn._function(key)
    if func is None:
        return ""
    params = [p for p in inspect.signature(func).parameters.values()
              if p.name != "self" and p.kind is not p.VAR_KEYWORD
              and not (p.kind is p.VAR_POSITIONAL and p.name == "extra")]
    if not params:
        return r"\wordfield{Options}{none: just write the empty brackets.}"
    rows = []
    for p in params:
        if p.kind is p.VAR_POSITIONAL:
            rows.append((p.name + "...", "as many as you like, separated by commas"))
        elif p.default is p.empty:
            rows.append((p.name, "needed"))
        elif p.default is None or type(p.default).__name__ == "_NotGiven":
            rows.append((p.name + "=", ""))
        else:
            normal = f'"{p.default}"' if isinstance(p.default, str) else repr(p.default)
            rows.append((p.name + "=", "normally " + code(normal)))
    body = "\n".join(f"{code(name)} & {what}\\\\" for name, what in rows)
    return ("\\wordfield{Options}{}\\par\\nopagebreak\n\\begin{optiontable}\n" + body + "\n\\end{optiontable}")


def _doc_text(doc: str) -> str:
    """A docstring as LaTeX: paragraphs of prose, with lines that are only code set as code."""
    paragraphs = []
    for block in doc.split("\n\n"):
        pieces, prose = [], []
        for line in block.splitlines():
            stripped = line.strip()
            columns = re.search(r"\S( {3,})\S", stripped)
            if columns and "(with sdata.get_example" not in stripped:
                # a line set out in two columns: code on the left, what it means on the right
                if prose:
                    pieces.append(rich(" ".join(prose)))
                    prose = []
                left, right = stripped[: columns.start(1)], stripped[columns.end(1):]
                pieces.append(r"\codeline{" + esc(left) + r"}\enspace " + rich(" ".join(right.split())))
                continue
            if re.match(r"^(?:sdata|chart|table|nums|grid|page)\.\w+\(|^\w+ = ", stripped):
                if prose:
                    pieces.append(rich(" ".join(prose)))
                    prose = []
                m = re.match(r"^(.*?)\s*(\(with sdata\.example\(.*\))?$", stripped)
                main, with_table = m.group(1), m.group(2)
                text = r"\codeline{" + esc(main) + "}"
                if with_table:
                    text += " " + rich(with_table)
                pieces.append(text)
            else:
                prose.append(stripped)
        if prose:
            pieces.append(rich(" ".join(prose)))
        paragraphs.append("\\\\\n".join(pieces))
    return "\n\n".join(p for p in paragraphs if p)


def _underneath(key: str) -> str:
    """The library a word uses, in words, from the tables above: for words without a tested entry in
    simplydata._underneath yet (until phase U3 every word has one)."""
    if key in UNDERNEATH:
        return UNDERNEATH[key]
    group = learn._group_of(key)
    if group in GROUP_UNDERNEATH:
        return GROUP_UNDERNEATH[group]
    raise KeyError(f'Say which library "{key}" uses: add it to UNDERNEATH in docs/make_manual.py')


# ---------------------------------------------------------------- the same underneath (tested entries)
def underneath_entry(key: str):
    """The tested entry of a word in simplydata._underneath, or None."""
    from simplydata._underneath import UNDERNEATH as TESTED

    return TESTED.get(key)


def underneath_name(key: str) -> str:
    """The one-line "Underneath" field as LaTeX: read from the tested code where the word has an entry
    ("seaborn barplot()"), else the name from the tables above."""
    from simplydata._underneath import library_calls

    entry = underneath_entry(key)
    if entry is None:
        return rich(_underneath(key))
    if entry.compare == "none":
        return rich(entry.note)
    parts = [esc(library) + " " + ", ".join(code(c) for c in calls) for library, calls in library_calls(entry) if calls]
    return r" \textperiodcentered{} ".join(parts)


def underneath_figure(key: str) -> str:
    """The file (relative to docs/manual) of the one picture a chart word's box shows. An option entry's key
    ('draw_smooth_line test_method="loess", ...') has spaces, quotes and commas: each run of them becomes one _."""
    import re

    return "figures/underneath_" + re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_") + ".pdf"


_HOW = {"value": "the number", "table": "the table", "result": "the numbers of the result table"}
# what each chart fact is, in words, for the "Checked:" line
_FACT_WORDS = {"bars": "the bars", "bar_colour_groups": "which bars share a colour", "dots": "the dots",
               "dot_size_shares": "the dot sizes", "dot_colour_groups": "which dots share a colour",
               "lines": "the lines", "labels": "the axis labels", "ticks": "the tick labels", "legend": "the legend",
               "limits": "the axis ranges", "scales": "the axis scales", "panels": "the number of panels"}


def _checked(entry) -> str:
    """What the test compares, in words, built from the entry itself."""
    if entry.compare != "chart":
        return _HOW[entry.compare]
    facts = [_FACT_WORDS[f] for f in entry.check]
    if entry.legend_numbers:
        facts.append("the numbers in the legend")
    listed = facts[0] if len(facts) == 1 else ", ".join(facts[:-1]) + " and " + facts[-1]
    return listed + " (the chart's data, not its pixels)"


def _same_underneath(key: str, entry=None) -> str:
    """The grey box "The same underneath" (and, for a chart word, the one picture both programs draw). entry= an
    option's own entry: its box says which option it shows."""
    from simplydata._underneath import R_LABEL

    entry = entry or underneath_entry(key)
    if entry is None:
        return ""
    if entry.compare == "none":
        return r"\undertext{\textit{Nothing underneath:} " + rich(entry.note) + "}"
    out = []
    if entry.compare == "chart":
        out.append(r"\begin{center}\begin{minipage}{\linewidth}\centering" + "\n"
                   + r"\includegraphics[width=0.52\textwidth,height=0.26\textheight,keepaspectratio]"
                   + "{" + underneath_figure(entry.key) + "}\n"
                   + r"\captionof*{figure}{The chart simplydata draws. The code below draws the same "
                   + esc(_FACT_WORDS[entry.check[0]].replace("the ", "", 1)) + ", without simplydata's paper look.}" + "\n" + r"\end{minipage}\end{center}")
    badges = "".join(r"\libbadge{" + esc(library) + "}" for library in entry.code)
    out.append(r"\needspace{10\baselineskip}\begin{underneathbox}{" + badges + "}")
    if entry.option:
        out.append(r"\undertext{\textbf{With " + code(entry.option) + "}: the same job with this option.}")
    for library, language, source in entry.blocks():
        if language == "r":
            out.append(r"\underlib{" + esc(R_LABEL) + "}")
            out.append(listing(source, "underr"))
        else:
            shown = library + (" (with what R gives back)" if entry.uses_r else "")
            out.append(r"\underlib{" + esc(shown) + "}")
            out.append(listing(source, "under"))
    if entry.choices:
        out.append(r"\undertext{\textbf{simplydata chooses}}")
        for number, choice in enumerate(entry.choices, start=1):
            out.append(r"\undertext{" + f"({number}) " + rich(choice) + "}")
    if entry.python_note:
        out.append(r"\undertext{\textit{In Python only:} " + rich(entry.python_note) + "}")
    if entry.also:
        out.append(r"\undertext{" + rich(entry.also) + "}")
    engines = " (on a pandas and on a Polars table)" if key.startswith("table.") else ""
    out.append(r"\undertext{\textit{Checked:} a test runs both and compares " + esc(_checked(entry) + engines)
               + ".}")
    out.append(r"\end{underneathbox}")
    return "\n".join(out)


def _word_entry(key: str, aliases: dict) -> str:
    title = learn._call_form(key)
    out = [f"\\wordentry{{{esc(title)}}}{{{label(key)}}}"]
    if key in aliases:
        start = {"table": "table", "numbers": "nums", "grid": "grid"}.get(learn._kind(key), "chart")
        other = ", ".join(code(f"{start}.{a}()") for a in aliases[key])
        out.append(f"\\wordfield{{Also written}}{{{other}}}")
    if key in learn.OPTIONS:
        opt = learn.OPTIONS[key]
        out.append(rich(opt["about"]))
        out.append("")
        out.append(rich(opt["text"]))
        out.append("")
        works = ", ".join(f"\\hyperref[{label(w)}]{{{code(f'chart.{w}()')}}}" for w in opt["words"])
        out.append(f"\\wordfield{{Works in}}{{{works}}}")
    else:
        out.append(_doc_text(inspect.getdoc(learn._function(key)) or ""))
        out.append("")
        out.append(_options_table(key))
    if key in learn.EXTRA_NOTES:
        out.append("")
        out.append(r"\wordfield{Good to know}{" + rich(learn.EXTRA_NOTES[key]) + "}")
    out.append("")
    basis = basis_keys(key)
    if basis:
        out.append(r"\wordfield{Why this method}{\hyperref[" + basis_label(basis[0]) + r"]{How simplydata chooses "
                   r"methods}, page \pageref{" + basis_label(basis[0]) + "}: the default, the evidence and the checks.}")
    out.append(r"\wordfield{Underneath}{" + underneath_name(key) + "}")
    table = learn._example_table(key)
    where = f"(it uses the practice table {code(table)})" if table else ""
    out.append(r"\wordfield{Example you can run}{" + where + "}\\par\\nopagebreak")
    out.append(listing(learn.HELP_EXAMPLES[key]))
    box = _same_underneath(key)
    if box:
        out.append(box)
    from simplydata._underneath import option_entries

    for entry in option_entries(key):  # an option that changes what the word calls underneath: a box of its own
        out.append(_same_underneath(key, entry))
    return "\n".join(out)


def basis_keys(key: str) -> list[str]:
    """The entries of simplydata._method_basis for a word: its own, then its options'."""
    from simplydata._method_basis import BASIS

    return [k for k in BASIS if k == key or k.startswith(key + " ")]


def basis_label(key: str) -> str:
    """A LaTeX label for an entry of the appendix "How simplydata chooses methods"."""
    return "basis:" + re.sub(r"[^A-Za-z0-9.:-]+", "-", key.replace("_", "-").replace("=", "-eq")).strip("-")


def _link(ref) -> str:
    """A reference's DOI or URL as a link, escaped for LaTeX."""
    import urllib.parse

    if ref.doi:
        target = "https://doi.org/" + urllib.parse.quote(ref.doi, safe="/:().-_")
        shown = "doi:" + esc(ref.doi)
    else:
        target, shown = ref.url, esc(ref.url)
    target = target.replace("%", r"\%").replace("#", r"\#")
    return r"\href{" + target + "}{" + shown + "}"


def _method_basis() -> str:
    """The appendix "How simplydata chooses methods", made from simplydata._method_basis, as
    docs/how_simplydata_chooses.md is (docs/make_method_basis.py)."""
    import importlib.util

    from simplydata._method_basis import BASIS, EVIDENCE, PRINCIPLE_REFERENCES, PRINCIPLES, REFERENCES

    spec = importlib.util.spec_from_file_location("make_method_basis", HERE / "make_method_basis.py")
    make_method_basis = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(make_method_basis)

    counts = {kind: sum(b.evidence == kind for b in BASIS.values()) for kind in EVIDENCE}
    out = [r"\unchapter{How simplydata chooses methods}{basis}",
           "simplydata often chooses a method, an option value or a setting for you. This appendix gives, for each "
           f"of the {len(BASIS)} choices, what simplydata chooses, what else you can ask for, why (the principle and "
           "the published evidence), and what simplydata checks in your data before it uses the method. "
           f"{counts['published']} defaults rest on published guidelines or method comparisons, "
           f"{counts['convention']} follow the convention of the package named so that results match it, and "
           f"{counts['starting value']} are simplydata's own starting values, each changed with the option named. "
           "Every DOI was looked up in Crossref; references without a DOI were checked at their URL. The defaults of "
           "the later batches were read by an independent reviewer when they were designed, and in November 2026 "
           "every entry, with its references, was checked again by independent reviewers acting as hostile "
           "statistical referees; their findings were applied. The same text is in "
           + code("docs/how_simplydata_chooses.md") + ".",
           r"\unsection{The five principles}{basis:principles}",
           r"\begin{enumerate}"]
    for key, text in PRINCIPLES.items():
        refs = "; ".join(esc(REFERENCES[r].short) for r in PRINCIPLE_REFERENCES[key])
        out.append(r"\item \textbf{" + key + ".} " + rich(text) + (f" ({refs})" if refs else ""))
    out.append(r"\end{enumerate}")
    for group, keys in make_method_basis.grouped():
        name = re.sub(r"[^A-Za-z0-9]+", "-", group)
        out.append(f"\\unsection{{{esc(group)}}}{{basis-group:{name}}}")
        for key in keys:
            b = BASIS[key]
            word, _, option = key.partition(" ")
            title = code(word if word.endswith("=") else learn._call_form(word)) + (" " + code(option) if option else "")
            out.append(r"\par\needspace{6\baselineskip}\vspace{0.7em}\phantomsection\label{" + basis_label(key) + "}"
                       r"\noindent{\sffamily\bfseries\color{brand}" + title + r"}\par\nopagebreak")
            out.append(r"\wordfield{Default}{" + rich(b.default) + "}")
            out.append(r"\wordfield{Alternatives}{" + rich(b.alternatives) + "}")
            kind = "" if b.evidence == "published" else r" \textit{Basis: " + esc(b.evidence) + ".}"
            out.append(r"\wordfield{Why (" + b.principle + ")}{" + rich(b.why) + kind + "}")
            if b.checks:
                out.append(r"\wordfield{Checks}{" + rich(b.checks) + "}")
            if b.references:
                out.append(r"\wordfield{References}{" + "; ".join(esc(REFERENCES[r].short) for r in b.references) + "}")
            out.append(r"\wordfield{In the dictionary}{\hyperref[" + label(word) + r"]{page \pageref{" + label(word)
                       + "}}}")
    out.append(r"\unsection{References}{basis:references}")
    out.append(r"\begingroup\small\raggedright")
    used = {r for b in BASIS.values() for r in b.references} | {r for v in PRINCIPLE_REFERENCES.values() for r in v}
    for key in sorted(used, key=lambda k: (REFERENCES[k].text.lower(), k)):
        ref = REFERENCES[key]
        out.append(r"\par\noindent\hangindent=1.5em " + esc(ref.text) + " " + _link(ref))
    out.append(r"\par\endgroup")
    return "\n".join(out)


def _family(keys: list[str]) -> str | None:
    """Which chapter a group belongs to. A group with table words is a table group even when it has
    a chart word too (draw_survival_curves); a group of sdata words only (finding and solving, planning
    a study) stays in the chapter before it, so no chapter starts twice."""
    kinds = {learn._kind(k) for k in keys} - {"sdata"}
    if not kinds:
        return "help" if "sdata.help" in keys else None
    if "table" in kinds:
        return "table"
    if kinds & {"chart", "option"}:
        return "chart"
    return "numbers"


def _dictionary(aliases: dict) -> str:
    out = []
    current = None
    for group, keys in learn.GROUPS:
        family = _family(keys)
        if family is not None and family != current:
            current = family
            title, intro = FAMILY_TITLES[family]
            out.append(f"\\unchapter{{{title}}}{{family:{family}}}")
            out.append(intro)
        out.append(f"\\unsection{{{esc(group)}}}{{group:{esc(group.replace(' ', '-').replace(':', '').replace(',', ''))}}}")
        for key in keys:
            out.append(_word_entry(key, aliases))
    return "\n".join(out)


def _solutions() -> str:
    out = [r"\unchapter{Solutions to the tasks}{solutions}",
           "One worked solution for each ``Try it yourself'' task. There is often more than one good "
           "answer: if yours runs and answers the question, it is right. Each solution runs on its own "
           "and was run to make the chart and output shown. In Python, "
           + code("sdata.show_lesson(3, solutions=True)") + " prints the solutions of lesson 3."]
    for number, les in enumerate(learn.LESSONS, start=1):
        out.append(f"\\unsection{{Lesson {number}: {esc(les['title'])}}}{{solutions:{number}}}")
        for task_no, (task, (source, explain)) in enumerate(zip(les["task"], learn.lesson_solutions(number)), start=1):
            out.append(f"\\solutiontask{{{task_no}}}{{{rich(task)}}}")
            out.append(listing(source))
            prefix = _solution_prefix(number, task_no)
            out.append(output_block(prefix))
            fig = figure_block(prefix, source, f"Lesson {number}, task {task_no}:", 0.52, 0.30, numbered=False)
            if fig:
                out.append(fig)
            out.append(f"\\solutionanswer{{{rich(explain)}}}")
        out.append(f"\\par\\noindent{{\\small\\sffamily\\hyperref[lesson:{number}]{{Back to lesson {number}}}}}")
    return "\n".join(out)


def _index(aliases: dict) -> str:
    entries = []
    for key in learn._all_keys():
        entries.append((learn._word(key).lower(), learn._call_form(key), key))
        start = {"table": "table", "numbers": "nums", "grid": "grid"}.get(learn._kind(key), "chart")
        for alias in aliases.get(key, []):
            entries.append((alias.lower(), f"{start}.{alias}()", key))
    entries.sort(key=lambda e: (e[0].strip("="), e[1]))
    lines = [r"\unchapter{Index of words}{index}",
             "Every word and option, A to Z, with the page of its dictionary entry. Other spellings of a "
             "word (such as " + code("chart.use_color()") + " for " + code("chart.use_colour()") + ") point to the same entry.",
             r"\begin{multicols}{2}\small\raggedright\setlength{\parskip}{0.1em}"]
    for _, shown, key in entries:
        lines.append(f"\\indexline{{{label(key)}}}{{{esc(shown)}}}")
    lines.append(r"\end{multicols}")
    return "\n".join(lines)


def in_words(number: int) -> str:
    """A count in words ("twenty"), so that hand-written sentences follow the code."""
    ones = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
            "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
            "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    if number < 20:
        return ones[number]
    if number < 100:
        return tens[number // 10] + ("" if number % 10 == 0 else "-" + ones[number % 10])
    return str(number)


def make() -> str:
    """The whole manual as LaTeX text. Runs nothing, so it is quick and always the same."""
    aliases = learn._aliases()
    for key in learn._all_keys():  # every word must say which library it uses
        _underneath(key)
    body = [
        _preamble(),
        r"\begin{document}",
        r"\frontmatter",
        _title_page(),
        r"\tableofcontents",
        r"\mainmatter",
        r"\part{Getting started}\label{part:start}",
        GETTING_STARTED.strip().replace("@LESSON_COUNT@", in_words(len(learn.LESSONS)).capitalize()),
        _practice_tables(),
        r"\part{Lessons}\label{part:lessons}",
        r"\lessonchapters",
    ]
    body += [_lesson(n, aliases) for n in range(1, len(learn.LESSONS) + 1)]
    body += [
        r"\otherchapters",
        r"\part{Dictionary of words}\label{part:dictionary}",
        r"\unchapter{How to read the dictionary}{dictionary:how}",
        "Each entry gives the word as you type it, what it does (in the words of "
        + code('sdata.help("word")') + "), the options you can put in its brackets and what they "
        "normally are, the library that does the work underneath, and an example you can run as it is. "
        "The same entries are in Python: " + code('sdata.help("draw_bars")') + ". The words come in the same "
        "groups as " + code("sdata.show_all_words()") + "; the \\hyperref[index]{index of words} at the end of the "
        "book lists them A to Z.",
        "Some entries end with a grey box, \\textbf{The same underneath}. It shows the same job written in the "
        "package simplydata uses: pandas and then Polars for tables, NumPy for numbers, seaborn or matplotlib "
        "for charts, SciPy or statsmodels for statistics, and R where simplydata runs R for you. The box is for "
        "readers who know one of these packages or want to learn it; if you are learning simplydata, you can "
        "skip it. Each setting that simplydata chooses for you is marked in the code with a number, (1), (2) "
        "and so on, and explained under the code. A test runs the code in each box next to the simplydata word "
        "and checks that both give the same result, so the box cannot drift from simplydata. simplydata runs "
        "its table steps on pandas and Polars through narwhals; narwhals is only the link between the two and "
        "is not shown.",
        _dictionary(aliases),
        r"\part{Data science ideas}\label{part:ideas}",
        r"\input{ideas}",
        r"\part{Solutions}\label{part:solutions}",
        _solutions(),
        r"\part{How simplydata chooses methods}\label{part:basis}",
        _method_basis(),
        r"\backmatter",
        _index(aliases),
        r"\end{document}",
    ]
    return "\n\n".join(body) + "\n"


# ---------------------------------------------------------------- running the examples
def _work_folder() -> Path:
    """Scratch space for the build: SIMPLYDATA_WORK_DIR if set (so parallel builds do not share
    one folder), else F:\\claude_work if it exists (keeps the project folder small), else the
    system's temporary folder."""
    if os.environ.get("SIMPLYDATA_WORK_DIR"):
        base = Path(os.environ["SIMPLYDATA_WORK_DIR"])
        base.mkdir(parents=True, exist_ok=True)
        return base
    base = Path(r"F:\claude_work\scratch\simplydata")
    if not base.parent.exists():
        base = Path(tempfile.gettempdir()) / "simplydata_manual"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _as_pdf(source: str) -> str:
    """Save pictures as PDF (sharp at any size) instead of PNG; animations stay .gif."""
    def swap(m):
        stem, _, kind = m.group(1).rpartition(".")
        if kind.lower() in IMAGE_TYPES and kind.lower() != "gif":
            return f'.save("{stem}.pdf"'
        return m.group(0)
    return _SAVE.sub(swap, source)


def _last_frame(gif: Path, png: Path) -> None:
    from PIL import Image

    with Image.open(gif) as im:
        im.seek(im.n_frames - 1)
        im.convert("RGB").save(png, optimize=True)


def _clean_output(text: str) -> str:
    lines = [line.rstrip().replace("\t", "    ") for line in text.strip("\n").splitlines()]
    if len(lines) > MAX_OUTPUT_LINES:
        cut = len(lines) - (MAX_OUTPUT_LINES - 2)
        lines = lines[: MAX_OUTPUT_LINES - 2] + ["", f"... ({cut} more lines)"]
    return "\n".join(lines) + "\n" if lines else ""


def run_examples() -> None:
    """Run every lesson example and solution; keep their pictures and printed output."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.environ["SOURCE_DATE_EPOCH"] = "0"  # no dates in the PDF pictures: they only change with the chart
    for folder in (FIGURES, OUTPUT):  # empty them (the folders stay: a synced folder may be locked)
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.iterdir():
            old.unlink()
    work = _work_folder() / "examples"
    if work.exists():
        shutil.rmtree(work)
    start = Path.cwd()
    for prefix, source in jobs():
        folder = work / prefix
        folder.mkdir(parents=True)
        os.chdir(folder)
        printed = io.StringIO()
        try:
            with contextlib.redirect_stdout(printed), warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec(compile(_as_pdf(source), f"<{prefix}>", "exec"), {"__name__": "__main__"})
        finally:
            plt.close("all")
            os.chdir(start)
        text = _clean_output(printed.getvalue())
        if text:
            (OUTPUT / f"{prefix}.txt").write_text(text, encoding="utf-8")
        for (stem, kind), target in zip(saved_images(source), figure_files(prefix, source)):
            if kind == "gif":
                _last_frame(folder / f"{stem}.gif", MANUAL / target)
            else:
                shutil.copyfile(folder / f"{stem}.pdf", MANUAL / target)
        print(f"  ran {prefix}")
    run_underneath_figures()


def run_underneath_figures() -> None:
    """Draw the one picture of each chart word's "same underneath" box, from simplydata's side (the test
    checks that the library code draws the same chart). R words need R."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from simplydata._underneath import UNDERNEATH as TESTED
    from simplydata._underneath.check import run_ours

    os.environ["SOURCE_DATE_EPOCH"] = "0"
    FIGURES.mkdir(parents=True, exist_ok=True)
    for key, entry in TESTED.items():
        if entry.compare != "chart":
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            chart, _ = run_ours(entry)
            chart.save(str(MANUAL / underneath_figure(key)))
        plt.close("all")
        print(f"  drew {underneath_figure(key)}")


def latex_folder() -> Path:
    """Where LaTeX writes its build files (.aux, .log ...): SIMPLYDATA_LATEX_DIR, else the scratch space."""
    build = Path(os.environ.get("SIMPLYDATA_LATEX_DIR") or _work_folder() / "latex")
    build.mkdir(parents=True, exist_ok=True)
    return build


def compile_pdf() -> Path:
    build = latex_folder()
    env = dict(os.environ, SOURCE_DATE_EPOCH="0", FORCE_SOURCE_DATE="1")
    for run in range(3):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={build}", TEX.name],
            cwd=MANUAL, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            log = (build / "simplydata_manual.log").read_text(encoding="utf-8", errors="replace")
            print(log[-4000:])
            raise SystemExit(f"pdflatex failed (run {run + 1}); the full log is in {build}")
    shutil.copyfile(build / "simplydata_manual.pdf", PDF)
    return build


def main(argv: list[str]) -> None:
    MANUAL.mkdir(exist_ok=True)
    TEX.write_text(make(), encoding="utf-8")
    print(f"Wrote {TEX}")
    if "--tex" in argv:
        return
    if "--no-run" not in argv:  # --no-run: compile with the pictures and output already there
        print("Running every lesson example and solution ...")
        run_examples()
    elif "--underneath-figures" in argv:  # --no-run --underneath-figures: draw only the boxes' pictures
        run_underneath_figures()
    print("Compiling the PDF ...")
    build = compile_pdf()
    print(f"Wrote {PDF}")
    import make_dictionary  # the dictionary takes its page numbers from the manual just compiled

    make_dictionary.build(build)
    import make_30_days  # and so does the 30-day guide

    make_30_days.build(build)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main(sys.argv[1:])
