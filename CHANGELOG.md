# Changes

Each release lists what was added, changed or fixed. When a word is renamed, the old word keeps
working for one release and prints a one-line note with its new name.

## Unreleased

More statistics, each checked against R.

### Methods come from established packages

simplydata now calls SciPy and statsmodels for its methods instead of writing them out:
p-value adjustment, Welch's ANOVA, the log-rank test, Kaplan-Meier, the Cox model, linear,
logistic and Poisson models, mixed-model errors, polynomial fits, LOWESS, the line band, PCA,
Cramer's V, the summary measures, and the gamma, Gumbel and von Mises fits. The answers are the
same as before, except that logistic and Poisson standard errors now come from the converged
estimates (R uses the step before), so they agree with R to about 3e-5.

- statsmodels is now required (`pip install "simplydata[stats]"` still works).
- Standard errors of fitted distributions come from statsmodels' numerical Hessian
  (`approx_hess3`); they may move by up to a few in a million (about 3e-6) from before.
- A smoothing spline needs at least 5 different x values (SciPy's spline; it was 4).
- Python 3.11 or newer, and SciPy 1.16 or newer (its quantiles are exact).
- `compare_shape_to` calls SciPy `goodness_of_fit` again; most shapes take a few seconds
  with `samples=9999`, Weibull and t longer (a note says so before a long run).

### One sentence for every p-value

Every test now says its p-value in the same sentence, as a count of studies: "If there were truly
no difference, a difference this big or bigger would turn up in about 3 of 100 studies like this
one (p = 0.031)." Below 0.001 it says "fewer than 1 in 1000 studies"; from 0.05 it adds "This does
not show that there is no difference." Each test words its own "nothing there" ("If the groups were
truly alike", "If B were truly not higher than A", "If there were truly no link", "If the values truly
came from a bell shape" ...). This replaces "unlikely to be chance" / "could easily be chance", which
reads as the chance that chance did it, a common misreading of p-values. The words that list many
p-values (model terms, the strongest correlations, Cox hazard ratios) use a short form: "about 3 of
100 studies would show this much if there were truly none (p = 0.031)"; adjusted p-values in
`compare_each_pair` are printed as "Holm-adjusted p = 0.023". The effect and its interval now come
first, the p-value sentence on its own line after it. The count of studies is the p-value rounded;
nothing is computed anew.

### One-sided tests and Kendall's tau

- `sides=1, higher=...` (or its mirror `lower=...`) tests in one direction only, chosen before
  seeing the data: `compare_averages(..., sides=1, higher="B")` or `lower="A"` (two groups: Welch,
  Student, Mann-Whitney, Yuen, Brunner-Munzel), `compare_before_after(..., sides=1, higher="after")`
  or `lower="before"`, `compare_average_to(..., sides=1, higher="average")` or `lower="average"`,
  `compare_percent_to(..., sides=1, higher="percent")` or `lower="percent"`, and
  `correlation_between("hours", "marks", sides=1, higher="positive")` (or `"negative"`). Giving both
  `higher=` and `lower=`, or a word the test does not know, is a friendly error. The interval is then
  one-sided too ("at least 1.2"), and the sentence says what the test does and does not look for.
  R's and SciPy's `alternative="greater"` / `"less"` work as well, with the translation printed.
  Each is checked against R `t.test`, `wilcox.test`, `binom.test` and `cor.test` with `alternative =`.
- `correlation_between(..., method="kendall")`: Kendall's tau-b (SciPy `kendalltau`, as R
  `cor.test(method = "kendall")`).

### More tests to choose with test=

- `compare_averages`: `test="yuen"` (20 % trimmed averages, SciPy, as R `WRS2::yuen`),
  `"brunner-munzel"` (SciPy, as R `brunnermunzel.test`), `"alexander-govern"` (SciPy, as R
  `onewaytests::ag.test`) and `"median"` (Mood's median test, SciPy, as R `chisq.test` on the counts
  above the overall median).
- `compare_spreads`: `test="ansari"` and `"mood"` (SciPy, as R `ansari.test`, `mood.test`), and
  `"f"` (R `var.test`, with the interval of the ratio of the variances).
- `compare_counts`: `test="g"` (G-test, SciPy, as R `DescTools::GTest`), and for 2 x 2 tables
  `"barnard"` and `"boschloo"` (R `Exact::exact.test`; SciPy's versions use another two-sided rule
  and give other p-values).
- `compare_before_after`: `test="sign"` (statsmodels `sign_test`, as R `DescTools::SignTest`).
- `compare_shape_to`: `test="lilliefors"` (R `nortest::lillie.test`; statsmodels' p-value
  approximation differs from R's), `"dagostino"` (SciPy `normaltest`, as R `fBasics::dagoTest`) and
  `"jarque-bera"` (SciPy, as R `tseries::jarque.bera.test`). A distribution with fixed numbers can
  be the shape: `compare_shape_to("marks", sdata.distribution("normal", average=60,
  standard_deviation=15))` gives the one-sample Kolmogorov-Smirnov test (SciPy `ks_1samp`, as R
  `ks.test(x, "pnorm", 60, 15)`), and `test="cramer-von-mises"` the Cramer-von Mises test (SciPy, as
  R `goftest::cvm.test`).
- `percent_of(..., interval_by=)` and `compare_percent_to(..., interval_by=)`: the interval of a
  percent can be `"exact"` (Clopper-Pearson, the default), `"wilson"` or `"agresti-coull"`
  (statsmodels `proportion_confint`, as R `DescTools::BinomCI`). `interval_by=` is the same word
  as on `correlation_between`; `method=` still works, with a note.

### Pairs after a test

- `compare_each_pair(..., test=)` gains `"games-howell"` (R `rstatix::games_howell_test`, for groups
  with different spreads, with simultaneous intervals), `"scheffe"` and `"lsd"` (R
  `DescTools::ScheffeTest`, `PostHocTest(method = "lsd")`; LSD is not adjusted and says so), and for
  ranks `"dunn"` (R `FSA::dunnTest(method = "holm")`) and `"conover"` (R
  `PMCMRplus::kwAllPairsConoverTest`, Holm).
- `compare_each_pair(..., against="A")`: Dunnett's test of every group against one control group
  (SciPy `stats.dunnett`, as R `multcomp::glht(mcp(group = "Dunnett"))`; both use random numbers,
  so simplydata seeds SciPy's, `seed=1`, printed).
- `add_adjusted_p_value_column(method=)` gains `"hochberg"` and `"hommel"` (statsmodels
  `multipletests`, as R `p.adjust`).
- `compare_each_pair(..., show="letters")`: a compact letter display, one row per group; groups
  that share a letter have an adjusted p-value of 0.05 or more between them (R
  `multcompView::multcompLetters`). Works with every `test=`.

### Shuffling and the bootstrap

- `p_value_by="shuffling"` on `compare_averages` (2 groups), `compare_before_after` (numbers) and
  `correlation_between` (2 columns): the p-value from shuffling the group labels, swapping the two
  values within rows, or shuffling one column against the other, `shuffles=9999` times with
  `seed=1` (SciPy `permutation_test`, as R `perm::permTS`). When there are no more arrangements
  than shuffles, every one is counted and the p-value is exact; the sentence says which.
- `correlation_between(..., interval_by="bootstrap")`: a 95 % BCa bootstrap interval of r
  (SciPy `bootstrap`, `resamples=9999`, `seed=1`, as R `boot::boot.ci`), with a note below 20
  values that bootstrap intervals are often too narrow.

### Intervals for summaries

- `interval=95` on `average_of` (t interval, as R `t.test`), `median_of` and `percentile_of`
  (exact interval from the order of the values, SciPy `quantile_test`, as R
  `DescTools::MedianCI(method = "exact")`) and `standard_deviation_of` (R `DescTools::VarCI`,
  square-rooted). They then give back a table with the value, the interval and the count.
- `table.interval_of("marks", "median", for_each="class")`: a bootstrap interval for any summary
  (any one-number `summary_of` measure, or a function of your own); `method="bootstrap"` (BCa),
  `"percentile bootstrap"` or `"reverse percentile bootstrap"` (R's `type = "basic"`; the older
  value `"basic bootstrap"` still works, with a note).
- `summary_of(show=[...])` gains `"harmonic mean"` (SciPy `hmean`, as R `psych::harmonic.mean`)
  and `"winsorized average"` (20 % at each end, SciPy `mstats.winsorize`, as R `WRS2::winmean`).
- `percentile_of(..., method=)`: R's nine rules, by R's number or NumPy's name (NumPy
  `percentile`, as R `quantile(type =)`).
- `table.add_z_score_column("marks_z", from_column="marks", for_each="subject")`: SciPy
  `zscore(ddof=1)`, as R `scale()`.

### Equivalence and non-inferiority

- `same_within=5` (or `[-3, 5]`) on `compare_averages` (2 groups, Welch), `compare_before_after`
  and `compare_average_to`: two one-sided tests (statsmodels `ttost_ind`, `ttost_paired`,
  `DescrStatsW.ttost_mean`, as R `TOSTER::t_TOST`), with the 90 % interval. The answer is one of
  three: the same within the margin, different, or the data cannot tell.
- `same_within=5, not_lower="B"` is a non-inferiority test: is B lower than the other side by no
  more than the margin? (statsmodels `CompareMeans`, as R `t.test(mu = ..., alternative = ...)`).
  `not_higher="B"` is its mirror, for outcomes where lower is better (pain). The words say the
  claim that is tested, which `higher="B"` did not; `sides=1, higher="B"` with `same_within=`
  still works and a note gives the new spelling.

### Power

- `how_many_needed` / `chance_to_find(test="compare_counts", percents=[30, 15])`: two percents
  (statsmodels `power_proportions_2indep` for the power; R `power.prop.test` for the number
  needed).
- `same_within=5, spread=10`: power and numbers for two one-sided tests (R
  `TOSTER::power_t_TOST`).
- `how_many_needed(interval_width=4, spread=10)`: the number needed for a 95 % interval of an
  average of that width (R `presize::prec_mean`).
- `based_on="ranks"` says plainly that no package gives rank-test power.

### Lessons and the 30 days

- Lesson 14 starts with the effect and its 95 % interval (`average_of(..., interval=95)`, then the
  first sentence of `compare_averages`), then shows where a p-value comes from by shuffling the
  labels (`p_value_by="shuffling"`) before the formula p-value, and ends with `compare_matched` on
  three measurements of the same patients.
- The lesson "Risks, diagnostic tests and agreement" is the optional life-science lesson. The
  30-day guide finds it by its title, so its number follows the lessons before it (22 once the
  lesson "Working with a model" is in).
- The core words of this release come back in the 30-day warm-ups exactly 3 and 7 days after the
  day that teaches them, and in the final test from memory (`spaced=` questions in the guide).

### More from Part A: shifts, trends, bigger tables, correlations

- `compare_averages(..., based_on="ranks")` with two groups also prints the Hodges-Lehmann shift
  with its 95 % interval (R `wilcox.test(conf.int = TRUE)`, the same exact/approximate choice as
  the test).
- `compare_average_to(..., test="z", standard_deviation=15)`: the z-test with a known standard
  deviation (R `BSDA::z.test()`; statsmodels' ztest uses the sample's own spread).
- `compare_averages(..., test="jonckheere", in_order=[...])`: the Jonckheere-Terpstra trend test
  (statsmodels, as R `clinfun::jonckheere.test()`; tie handling differs slightly).
- `compare_matched(..., test="page")`: Page's trend test along the column order (SciPy, as R
  `crank::page.trend.test()`).
- `compare_counts`: `test="trend", in_order=[...]` (Cochran-Armitage, R `prop.trend.test()`);
  `test="fisher"` on bigger tables (100,000 seeded random tables in SciPy; `p_value_by="exact"`
  counts every table in R `fisher.test()`); `p_value_by="shuffling"` for the chi-square test
  (SciPy, as R `chisq.test(simulate.p.value = TRUE)`); `show="cells"` with the standardized
  residuals (statsmodels, as R `chisq.test()$stdres`).
- `compare_each_pair(..., matched_by="patient")`: each pair compared within the same patients
  (paired t-tests, or Wilcoxon signed-rank with `based_on="ranks"`, Holm-adjusted; as R
  `pairwise.t.test(paired = TRUE)` / `pairwise.wilcox.test(paired = TRUE)`).
- `correlation_between` with two columns now prints every r with its 95 % interval: Pearson from
  SciPy, Spearman and Kendall from R `DescTools` (Fisher's z). New `method="somers"` and
  `method="gamma"` (R `DescTools::SomersDelta()`, `GoodmanKruskalGamma()`, with intervals) and
  `allowing_for="height"` for the partial correlation (R `ppcor::pcor.test()`).
- New `table.compare_correlations(...)`: two correlations in two groups (Fisher's z) or two
  correlations that share a column (Steiger's z), with Zou's interval (R `cocor`).
- `count_each(..., interval=95)`: simultaneous Sison-Glaz intervals for the percents (statsmodels,
  as R `DescTools::MultinomCI()`).
- `show_rows_with_outliers` / `remove_rows_with_outliers(rule="grubbs" | "dixon" | "rosner")`:
  outlier tests from R `outliers` and `EnvStats`.

### Risks and rates

- `table.compare_risks("died", for_each="treatment", against="usual care")`: the risk in each group
  (exact interval), then the risk difference with Newcombe's score interval and what it means out
  of 100, the number needed to treat (NNTB or NNTH, with its interval through infinity when the
  difference's interval includes 0), the risk ratio and the odds ratio (Wald intervals on the log
  scale, with a note when the outcome is common), and the p-value (chi-square with Yates'
  correction, as R `prop.test()`). statsmodels `proportion_confint`, `confint_proportions_2indep`,
  `Table2x2`; checked against R `binom.test`, `DescTools::BinomDiffCI`, `epitools::riskratio` /
  `oddsratio`, `epiR::epi.2by2`. `p_value_by="exact"`: Fisher's exact test and the conditional
  odds ratio (SciPy, as R `fisher.test()`).
- `allowing_for="age_group"`: Mantel-Haenszel odds ratio and risk ratio with the Breslow-Day check
  (statsmodels `StratifiedTable`, as R `mantelhaen.test()`, `DescTools::BreslowDayTest()`; the
  interval of the pooled risk ratio from R `epiR::epi.2by2()`).
- `same_within=15` (percentage points): two one-sided tests of two risks (statsmodels
  `tost_proportions_2indep`, as R `TOSTER::twoprop_test()`); with `sides=1` and `higher=` or
  `lower=`, non-inferiority. `sides=1` alone gives the one-sided test (R `prop.test(alternative =)`).
- `table.compare_rates("infections", time="patient_days", for_each="ward")` and
  `table.rate_of(...)`: rates per 1000 with exact intervals, the rate ratio with the exact
  conditional test (statsmodels `confint_poisson`, `test_poisson_2indep`) and R's exact interval
  of the ratio (`poisson.test()`); `same_within=1.25` for a ratio margin (statsmodels
  `tost_poisson_2indep`, as two one-sided R `poisson.test(r =)`).
- `sdata.compare_risks(events=[20, 30], out_of=[60, 60])` and `sdata.compare_rates(events=[15, 30],
  time=[1200, 1100])` from given counts.

### Diagnostic tests

- `table.compare_to_truth("rapid_test", truth="infected")`: of 1000 people like these, how many
  the test finds and misses, sensitivity, specificity and the predictive values with exact
  intervals (statsmodels), the likelihood ratios and diagnostic odds ratio from R
  `epiR::epi.tests()`; `prevalence=1` shows the predictive values where 1 % have it.
- With a column of numbers (`"crp"`): the ROC analysis from R pROC: the AUC with DeLong's
  interval, the best cut-off by Youden's index and the answer there; `cut_off=` chooses one.
  Higher scores count as positive (`positive_when="lower"` turns it round; pROC's automatic
  direction is not used, because it hides a test that works the wrong way round).
- `table.compare_accuracy("crp", "procalcitonin", truth="infected")`: DeLong's test of two AUCs
  on the same people (R `pROC::roc.test()`), with the interval of the difference.
- `sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)`, or
  `sdata.compare_to_truth(sensitivity=90, specificity=95, prevalence=1)` for the base-rate question.
- New example table `clinic`: 200 made-up patients with a rapid test, CRP and procalcitonin,
  ratings by a nurse and a doctor, two blood-pressure devices, pain scores and hospital infections.
- The counts "of 1000", the number needed to treat and the predictive values at another
  prevalence are display arithmetic on the packages' results (shares written as counts).

### Agreement and reliability

- `table.agreement_between("nurse_rating", "doctor_rating")`: Cohen's kappa with its interval, z
  and p, and the raw agreement beside it (statsmodels `cohens_kappa`, as R `irr::kappa2()` and
  `psych::cohen.kappa()`); `weights="linear"` / `"quadratic"` with `in_order=` for ordered
  categories. Three or more columns: Fleiss' kappa (statsmodels; z and p from R
  `irr::kappam.fleiss()`). Columns of numbers: the intraclass correlation from R `irr::icc()`,
  two-way, absolute agreement, one rater by default (`raters=`, `kind=`, `of=` choose the form,
  which is always named, with Koo and Li's guide words beside the interval).
  `method="krippendorff"` (R `irr::kripp.alpha()`) and `method="lin"` (R `DescTools::CCC()`).
- `table.limits_of_agreement("device_a", "device_b")`: Bland-Altman limits of agreement with the
  intervals of the average difference and of both limits (R `BlandAltmanLeh::bland.altman.stats()`),
  and Lin's concordance correlation.
- `table.reliability_of(["q1", "q2", "q3", "q4", "q5"])`: Cronbach's alpha with Feldt's interval
  and the alpha without each item (R `psych::alpha()`, `psych::alpha.ci()`).
- Every agreement word says that agreement is not correlation.

### Charts of tests

- `chart.trade_off_curve(score="crp", truth="infected")`: the ROC curve from R pROC, with the AUC
  and its DeLong interval in the legend and the best cut-off marked; several scores give one curve
  each.
- `chart.difference_dots(x="device_a", y="device_b")`: the Bland-Altman chart: dots and average
  difference from statsmodels `mean_diff_plot`, the limits and their shaded intervals from R
  `BlandAltmanLeh` (statsmodels' own limits use the standard deviation with n in the divisor, so
  they differ a little from R's).
- `chart.forest_plot(x="estimate", y="measure")`: each row of a result table as a dot with its
  interval, with a line at no effect (0, or 1 on a log scale for ratios).
- Their field names (`roc_curve`, `bland_altman`, `interval_dots`, `forestplot`) point to these words.

### Test titles

The help titles of the tests no longer ask "or could it be chance?" (which invites reading the
p-value as the chance that chance did it); they ask "really different?", in line with the
p-value sentence.

### Yes/no and category columns before and after

`compare_before_after` now looks at the kind of column, and the sentence says which test that
gives. Two yes/no columns (yes/no, True/False or 0/1): McNemar's test with continuity correction
(statsmodels `mcnemar`, as R `mcnemar.test`), with the change in the percent and its 95 % interval
from R `exact2x2::mcnemarExactDP`; `p_value_by="exact"` gives the exact binomial test on the rows
that changed (as R `exact2x2::exact2x2(paired = TRUE)`). Two columns of three or more categories:
Bowker's test of symmetry (statsmodels `SquareTable.symmetry`, as R `mcnemar.test` on the k x k
table).

### New tests

- `table.compare_matched("week_0", "week_4", "week_8")`: three or more measurements of the same
  rows. Numbers: the Friedman test (SciPy, as R `friedman.test`), with Kendall's W and its
  bootstrap interval from R `effectsize::kendalls_w` (R seed 1); `test="quade"`: the Quade test (R
  `quade.test`). Yes/no columns: Cochran's Q (statsmodels, as R `DescTools::CochranQTest`). With two
  columns it is `compare_before_after`.
- `table.compare_shapes("marks", for_each="class")`: do the groups differ in the whole shape of
  their values? Two groups: the two-sample Kolmogorov-Smirnov test (SciPy `ks_2samp`, exact as R
  `ks.test`; with tied values R's exact p-value, which SciPy does not give, comes from R). Three or
  more: the Anderson-Darling k-sample test (SciPy `anderson_ksamp`, as R `kSamples::ad.test`
  version 2), with a p-value from shuffling the group labels 9999 times (seed 1).
- `table.check_random_order("marks", sorted_by=None)`: the runs test above and below the
  median (statsmodels, as R `randtests::runs.test`, which leaves out values equal to the median; so
  does simplydata, and says so). Next to `check_steady`; the earlier name `compare_to_random_order`
  still works, with a note.
- `sdata.compare_averages(averages=, standard_deviations=, counts=, names=)`: Welch's t-test (SciPy
  `ttest_ind_from_stats`, as R `BSDA::tsum.test`, whose interval of the difference simplydata uses)
  or, for three or more groups, Welch's ANOVA (statsmodels `anova_generic`, the same as R
  `oneway.test` on the rows), from the summary numbers of a paper or report. `names=` names the
  groups (as on `add_group_column`; `groups=` still works, with a note).
- `sdata.compare_counts([[20, 40], [30, 30]])`: `compare_counts` on a table of counts.

### Effect sizes with their intervals, from R effectsize

- Every effect size now comes with its 95 % interval: Hedges' g, Cohen's d and d_z, omega-squared,
  the rank-biserial correlations (also per pair in `compare_each_pair`), rank epsilon-squared
  (bootstrap interval, R seed 1), and the intervals of Cramer's V and Cohen's w. They come from R
  effectsize (`simplydata[r]`); simplydata's own formulas are removed. Cramer's V (SciPy), Cohen's w
  and Cohen's h (statsmodels) still come from Python.
- Without R the test runs as before; the effect size from R is left empty and one line says how to
  add it.
- `how_many_needed` and `chance_to_find` call statsmodels' power classes (`TTestIndPower`,
  `TTestPower`, `FTestAnovaPower`, `GofChisquarePower`, and their `solve_power`) instead of
  simplydata's own formulas, with the same numbers as R `power.t.test()` (strict = FALSE) and pwr;
  correlations call R `pwr::pwr.r.test` (`simplydata[r]`). The exact number needed now agrees with
  R to about 1e-4 (R's own search precision); the rounded-up number is unchanged.

### R itself, for what only R gives: `simplydata[r]`

Where no Python package gives R's answers, simplydata now runs R's own code through rpy2.
Install once: `pip install "simplydata[r]"`, R from https://cran.r-project.org, and in R
`install.packages(c("vegan", "survival", "mice"))`. Without R these words print what to install
(and name the Python alternative, with its different numbers); there is no fallback of our own.

- `add_clusters()` with k-means: R `kmeans(nstart = 25)` after `set.seed(seed)`.
- `add_nmds()`: R `vegan::metaMDS()`, at least `tries=` starts and up to 100 until the best
  map repeats.
- `compare_profiles()`: R `vegan::adonis2()`, `betadisper()` and `permutest()`; the p-values
  are now exactly R's for the same seed.
- `explain_survival()`: the proportional-hazards check is R `survival::cox.zph()`; without R
  the model is still fitted and a note says how to add the check.
- Smoothing splines with `smoothness="auto"`: R `smooth.spline()` chooses the smoothness (a
  number for `smoothness=` needs no R).
- `explain(..., empty_cells="multiple imputation")`: the results are pooled by R
  `mice::pool()` (Barnard-Rubin degrees of freedom).
- R's warnings are passed on as plain notes, such as
  `Note from R (vegan): some squared distances are negative and changed to zero.`
- Lessons 16, 17 and 18 (and day 17 of the 30-day guide) have a "Needs R" box.

### Fitting

- `table.fit_line(x=, y=)` is the main name of the straight-line fit, the same word as
  `chart.fit_line`; `fit_straight_line` still works for one release, with a note.
- `table.fit_curve(x=, y=, degree=2)` fits a polynomial by least squares (R
  `lm(y ~ poly(x, 2, raw = TRUE))`), with an interval for each term; `weights=` and `for_each=`.
- `table.fit_formula` takes `between=` (limits for the values to find, as R
  `nls(algorithm = "port")`), `weights=`, `for_each=`, `search="whole range"` (differential
  evolution, seed 1, then a least-squares polish) and `method=`, and gives standard errors,
  t, p-values, 95 % intervals, the residual standard error and AIC, as R `nls()`.
- `table.add_predicted_column("population = a * exp(b * (year - 2000))")` fits a formula and adds
  its value for every row (or takes the values of a fit with `using=`).
- On charts: `chart.fit_formula(...)` draws the fitted formula for each colour group and
  `chart.curve(...)` draws any formula of x, or a distribution.

### Finding and solving

- `sdata.find_smallest` and `sdata.find_biggest` find where a formula is smallest or biggest:
  on a range (Brent's method, R `optimize()`), from a start (Nelder-Mead, R `optim()`), with limits
  (L-BFGS-B), under rules (SLSQP; linear programming with HiGHS when everything is a straight line,
  with the value of one more of each rule; `whole_numbers=True` for mixed-integer programming), or
  over the whole range (differential evolution). The method is always printed, never switched
  silently.
- `sdata.solve` finds every solution of an equation in a range (R `uniroot()` on each sign change),
  all roots of a polynomial, complex ones too (R `polyroot()`), and solves sets of equations
  (R `nleqslv`), exactly when they are linear.
- `known=` takes the values of a `fit_formula` result, so a fitted curve can be solved or
  searched straight away.

### Values between points

- `table.values_at(column, at={"year": [2001, 2003]})` estimates a column between the known
  points: `joined_by="straight lines"` (R `approx()`), `"smooth curve"` (natural cubic spline),
  `"curve without overshoot"` (PCHIP), `"steps"` or `"nearest"`, or `smoothness="auto"` for a
  smoothing spline (R `smooth.spline()`); in two or more directions (bilinear on a full grid,
  triangles or a thin-plate spline for scattered points). `outside=` says what happens beyond the
  known points.
- `table.map_of(column, across=["east", "north"])` fills an evenly spaced map, ready for a contour
  map or heatmap.
- `fill_empty_cells(with_the="curve between neighbours")` and `"curve without overshoot"`;
  `chart.lines(joined_by=...)` and `chart.smooth_line(method="spline")`.

### Distributions

- `sdata.distribution("normal", average=50, standard_deviation=10)` for 26 named distributions
  (R's parameters with plain names; R's own names work too) and any other SciPy distribution.
  Its words: `chance` (above=, below=, at_most=, at_least=, between=, or exactly a count),
  `density_at`, `percentile`, `cut_off`, `middle_range`, `average`, `median`,
  `standard_deviation`, `variance`, `summary`, `random_numbers`, `chart`, `table` and
  `parameters`. Each sentence prints the R call that gives the same answer.
- `table.fit_distribution` and `nums.fit_distribution` fit by maximum likelihood (as R
  `MASS::fitdistr`) and give back the fitted distribution; `table.compare_distributions` ranks
  several by AIC, with the goodness-of-fit statistics of R `fitdistrplus::gofstat()`.
- `table.compare_shape_to(column, "gamma")` checks any smooth shape: the Anderson-Darling test with
  a Monte Carlo p-value that allows for the fitting (seed 1). `"normal"` keeps Shapiro-Wilk.
  `samples=` (9999 by default) sets how many simulated samples are refitted. They are refitted
  all at once with the exact likelihood equations, so most shapes take a second or two (Weibull
  went from about a minute to under a second, with the same p-value); t, Cauchy and F are still
  refitted one by one, and a short note says so before a run expected to take more than 10 seconds.
- On charts: `chart.fit_distribution("gamma")` over a histogram or density, and
  `chart.qq_dots(column, distribution="gamma")`.

### Names from other tools

- Names that people bring from pandas, NumPy, SciPy, R, matplotlib and ggplot2 (`sdata.minimize`,
  `sdata.curve_fit`, `sdata.pnorm`, `table.groupby`, `table.merge`, `chart.hist`, `chart.axhline`
  and about 400 more) never run: each says "In simplydata this is ..." with the word to use.
  `sdata.help("minimize")` explains them too.

### Dictionary

- `docs/manual/simplydataDictionary.pdf`: every word A to Z (one entry per word, with a part for
  each object that has it, such as `fit_line` on tables and charts), each with its meaning, a short
  example, its main options, the names other tools use for it, related words and the page of the
  manual that explains it (a link that opens the manual there), plus the lesson that teaches it.
  Its last part, "Coming from another tool?", turns every name from other tools and every old name
  into the simplydata word. It is made from the code by `docs/make_dictionary.py`; building the
  manual (`python docs/make_manual.py`) builds the dictionary too, with the manual's page numbers,
  and a test fails if a word has no page or the pages come from an older manual.

### 30 days of simplydata

- `sdata.start_30_days(track="python")` starts a course of 30 days of about an hour each:
  `track="python"` for people who already write some Python (about two lessons a day, review days
  on days 7, 14, 21 and 28, then an eight-day project of their own), `track="beginner"` for people
  who have never programmed (three days of just enough Python first, then about one lesson a day
  and a small project). Both cover all 20 lessons and end with a final test from memory.
- `sdata.today()` shows the day to do next: a 5-minute warm-up of questions on earlier days
  (yesterday, about three days ago, about a week ago; review days mix the whole course), what to do
  (the lesson, the manual's sections and the words to look up) and a task to do without looking
  back. A missed day is never lost: `today()` carries on where you stopped, says so kindly if you
  have fallen behind the calendar, and `today(follow_calendar=True)` jumps to the calendar's day.
- `sdata.day(5)` shows any day (`sdata.day()` lists all 30 with ticks), `sdata.answers(5)` gives
  the warm-up answers and a worked answer to the task, and `sdata.next_day()` goes on now.
- The progress (track, start date and the date each day was opened) is kept only in a small file
  on your computer, `~/.simplydata/progress.json` (`SIMPLYDATA_PROGRESS_FILE` chooses another);
  nothing is sent anywhere.
- `docs/manual/simplydata_30_days.pdf`: the same days on paper, with a calendar to tick for each
  track, one page per day (warm-up questions with lines for the answers, the manual's page for each
  lesson, section and word, and the task) and the answers at the back. It is made by
  `docs/make_30_days.py` from the same source as `sdata.today()` (`simplydata/learn_days.py`), and
  building the manual builds it too. Every piece of code in the days runs in the tests.
- Lesson 1, `sdata.lesson()` and `sdata.help()` say that the 30 days exist; `sdata.help("course")`
  and `sdata.help("tutorial")` point to `start_30_days`.

### Not in this release

Robust (outlier-resistant) curve fitting, gradients given by hand, profile-likelihood intervals
for formula fits, mixtures and truncated distributions, distributions of several variables, and
slopes and areas under splines.

### Models

- `table.explain(column, using=[...])` explains one column from several others: a linear model
  by least squares (multiple regression), with `"a * b"` for an interaction and text columns as
  groups. `outcome="yes or no"` is logistic regression, `outcome="counts"` Poisson regression
  (`"counts (overdispersed)"` quasi-Poisson), `grouped_by=` a mixed model with a random intercept
  per group, and `empty_cells="multiple imputation"` fills empty cells 20 times and pools the
  answers with Rubin's rules.
- `table.add_predicted_column` adds what the model expects for each row.

### Patterns across columns

- `add_principal_components` and `principal_components_of` (PCA), `add_clusters` (k-means or
  hierarchical), `distances_between_rows` (Bray-Curtis, Euclidean, Jaccard, Manhattan),
  `add_nmds` (non-metric multidimensional scaling) and `compare_profiles` (PERMANOVA, with a
  check of the spread of each group).

### Survival

- `survival_over_time` (Kaplan-Meier), `compare_survival` (log-rank test), `explain_survival`
  (Cox model, with a proportional-hazards check) and `chart.survival_curves` (with confidence
  bands, censoring ticks and a number-at-risk table).

### Planning a study

- `sdata.how_many_needed` and `sdata.chance_to_find`: power analysis for the averages, counts and
  correlation tests.

### More tests and summaries

- `compare_spreads` (Levene's test centred on medians, Bartlett or Fligner-Killeen),
  `compare_each_pair(..., test="tukey")` (Tukey's honest significant difference),
  `compare_counts_to` (chi-square goodness of fit) and `compare_percent_to` (exact binomial test).
- `percentile_of`, `most_common_of`, and new `summary_of(show=...)` measures: geometric mean,
  skewness, kurtosis, coefficient of variation, median absolute deviation, trimmed average, most
  common value and any percentile.
- Formulas know `exp`, `sin`, `cos`, `tan`, `pi` and special functions: `erf`, `erfc`, `gamma`,
  `lgamma`, `digamma`, `beta` and `besselJ`.

### Charts

- `colour_scale` chooses the colours for numbers (heatmaps, contour maps, dots coloured by a
  number): named colour-blind-safe scales, your own colours, `middle=`, `log=True`, `steps=` and
  `between=`.
- `transparency=` on every chart type (also survival curves) and `thickness=` on lines.
- `tick_format_x` / `tick_format_y` (percent, thousands, decimals, scientific, dates), and
  `ticks_x(every=...)` / `ticks_y(how_many=...)` for tick spacing, also by year, month or week.
- Histogram options: `show="percent"` or `"density"`, `stacked=`, `steps=`, `cumulative=` and
  `bin_width=`.
- `line_with_slope` (for 1:1 lines), `qq_dots` (Q-Q plots), `cumulative_share` (ECDF) and
  `font_name`.

### Choosing parts by position

- Printed tables number their rows from 1 (`show`, `show_first_rows`, `show_last_rows`, `print`,
  notebooks), so the last row of a 54-row table is row 54; `show_rows_with_outliers` shows each row
  with its number in the whole table. Only the display changes: `as_pandas()` keeps pandas' own
  index.
- `table.keep_rows_by_position(10, to=20)` and `remove_rows_by_position`: rows by their place,
  counting from 1 with both ends included (rows 10 to 20 are 11 rows), `to="last"`, `step=` for every
  n-th row and a list such as `[1, 5, 9]` (as pandas `iloc` and Polars `slice`/`gather_every`).
  `keep_columns_by_position` and `remove_columns_by_position` do the same for columns and say which
  columns they were.
- `table.row(3)` gives one row as a dict, `table.cell_at(row=3, column="marks")` one cell, and
  `table.reverse_rows()` turns the table upside down.
- `keep_columns` and `remove_columns` take a run of names (`keep_columns("hours", to="height")`),
  `kind="number"` (or `"text"`, `"date"`, `"true/false"`), `starts_with=`, `ends_with=`, `contains=`
  and `pattern=`.
- `replace_values` takes the `keep_rows` conditions: `replace_values("marks", above=100,
  with_value=100)`.
- Numbers: `nums.keep_numbers_by_position(3, to=8)`, `remove_numbers_by_position`, and
  `nums.replace_numbers(-999, with_value=None)` or `replace_numbers(above=100, with_value=100)`.
- Grids: `keep_rows_by_position`, `keep_columns_by_position`, `remove_rows_by_position`,
  `remove_columns_by_position` (a block is two steps) and `grid.replace_numbers`. `grid.keep_numbers`
  explains why a grid cannot drop single numbers.
- `"last"` is a position everywhere, also in `nums.number_at`, `grid.row`, `grid.column` and
  `grid.number_at`.
- `table[...]`, `table.marks` and loops over a table explain the words to use instead;
  `iloc`, `iat`, `select_dtypes`, `clip`, `np.where` and other names point to the new words.
- Lesson 10 teaches choosing by position, with a task to do from memory.
- Not yet: setting one cell by position, positions of matching numbers (argwhere, argmax), clip as
  one word, random fractions and sampling with replacement, grid diagonals and flips, unions of
  column choices, nested columns.

### Also

- Example tables `school`, `meadow` and `trial`; lessons 16 to 20; the new words are also taught
  in lessons 3, 5, 6, 11, 12 and 14. Lessons 19 and 20 end with a task that asks you to recall
  the words without looking back.
- The optional extra `stats` (statsmodels), needed only for mixed models and multiple
  imputation.
- Panel letters on a page no longer cover the panel titles of a chart made with
  `one_chart_per`.
- `chart.all_dots` drawn over `boxes` or `violins` uses dark grey dots (or, in colour groups, a
  dark rim), so the dots no longer vanish into boxes of the same colour; `colour=` still wins.

## 0.1.0 (2026-11-12)

The first release: charts, tables, numbers and statistical tests in one small vocabulary.

### Charts

- About 70 words over matplotlib and seaborn: `bars`, `lines`, `dots`, `histogram`, `boxes`,
  `violins`, `heatmap`, `pie`, `error_bars`, `fit_line`, `smooth_line`, `density` and more.
- Titles, labels, legends, ranges, log scales, lines and shaded bands, notes with arrows,
  second y-axis, zoom insets, polar and 3D charts, animation.
- Panels: `sdata.grid(a, b, letters=True)` and `one_chart_per(down=, across=, per_row=)`.
- Months and weekdays in calendar order; `label_legend`, `names_on_dots`, `band`.
- Saving for journals: `chart.size(width=17, height=8, unit="cm")` (inches, cm, mm or pixels)
  gives a file of exactly that size, and `chart.save("figure.tif", resolution=600)` sets the dots
  per inch.
- Charts say how many rows with empty cells they left out; `chart.empty_cells()` shows where
  the gaps are.

### Tables

- Tables on pandas or Polars (through narwhals), with `undo()` and `start_again()`.
- Reading CSV, Excel, whole folders and web addresses; decimal commas and codes such as "NA";
  Word, SPSS and Stata files with the `files` extra.
- Choosing rows, including written conditions: `keep_rows("marks > 50 and class == 'A'")`.
  An empty cell never meets a condition.
- Cleaning: `remove_rows_with_empty_cells`, `fill_empty_cells` (also
  `with_the="line between neighbours"`), `add_is_empty_column`, outliers by Tukey's rule.
- Dates (`make_dates(order=)`, parts of dates, days between dates, `after=`/`before=`), text
  (split, join), rolling averages, previous values and changes, shares per group.
- Summaries: `average_of`, `summary_of`, totals per week, month or year (`every=`), cross
  tables and correlation tables.

### Numbers

- `sdata.numbers`, `sdata.number_grid` and `sdata.random_numbers` over NumPy, with plain words
  and `undo()`.

### Statistical tests

- `compare_averages` (Welch's t-test or Welch's ANOVA; rank tests on request),
  `compare_each_pair` (Holm-adjusted), `compare_before_after`, `compare_average_to`,
  `compare_counts` (chi-square, or Fisher's exact test), `compare_shape_to`,
  `fit_straight_line`, `fit_formula`, adjusted p-values.
- Effect sizes: Hedges' g, omega-squared, Cramér's V. Results checked against R 4.6.2.

### Learning

- `sdata.lesson(1)` to `sdata.lesson(15)`, `sdata.words()`, `sdata.help("word")`,
  `sdata.example()` tables (marks, weather, fruit, growth, island, shop), worked solutions.
- A cheat sheet (`docs/cheatsheet.md`) and a manual (`docs/manual/simplydata_manual.pdf`),
  both made from the code.
