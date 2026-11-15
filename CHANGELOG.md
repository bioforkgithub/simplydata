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

### Signals and time series (first words)

- `table.spectrum_of("signal", sorted_by="time")` and `nums.spectrum_of(time_step=0.01)`: which repeating
  cycles a column holds and how strong each is. method="periodogram" (SciPy; 2 x R `spec.pgram` with
  taper 0, so the powers add up to the variance), "welch" (window= readings per piece) or
  "lomb-scargle" for uneven times (R `lomb::lsp` itself, needs `simplydata[r]`). show="power",
  "decibels" or "amplitude"; between= keeps a frequency range; for_each= one spectrum per group.
  `time_step=` is the time between readings (`sampling_rate=` and `fs=` are accepted).
- `table.check_steady("signal", sorted_by="time")`: does a column stay steady over time, or wander?
  The ADF and KPSS tests together, run in R (`tseries::adf.test`, `tseries::kpss.test`), with R's
  table p-values ("below 0.01", "above 0.1" when outside the tables). around="straight line" checks
  steadiness around a trend. Needs `simplydata[r]`.
- `table.autocorrelation_of("signal", sorted_by="time")` and `nums.autocorrelation_of(rows_back=10)`: how much
  a column is like itself some rows back, with the noise band of R `plot.acf` (band="white noise", or
  "bartlett" as R `ci.type = "ma"`), show="correlation" (R `acf`), "partial" (R `pacf`) or "covariance",
  and the Ljung-Box test of all of them together (R `Box.test(type = "Ljung-Box")`). From statsmodels.
- `table.correlation_between("a", "b", rows_back=12, sorted_by="date")`: the cross-correlation for shifts -12 to
  12 (statsmodels `ccf`, as R `ccf` with the sign of the lag reversed), and which column follows the other.
- `table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year")`: adds the trend, the season and
  the rest as three columns. method="loess" (R `stl`: statsmodels STL with R's settings; season_window="fixed" runs
  R `stl(s.window = "periodic")` itself), "moving averages" (R `decompose`, season "added" or "multiplied") or
  "straight line" (one statsmodels least-squares fit of the line and the season effects, as R `lm`).
- `table.trend_of("visitors", sorted_by="month")`: Sen's slope with its 95 % interval (SciPy `theilslopes`, as R
  `trend::sens.slope`) and the Mann-Kendall test (R `trend::mk.test` itself); repeats_every= gives the seasonal test
  and slope (R `trend::smk.test`, `trend::sea.sens.slope`). Without R the slope is still given.
- `table.forecast("visitors", sorted_by="month", steps_ahead=12, repeats_every="year")` and `nums.forecast(...)`:
  the next values with a 95 % prediction interval (interval=; columns "forecast 95 % prediction low" / "high"),
  the time column carried on. method="exponential smoothing"
  (R `HoltWinters`, with trend= and season "added" or "multiplied"), "last value", "same season last time",
  "average", "straight on" ("drift" and "line from first to last" accepted) (R `forecast::naive`, `snaive`, `meanf`, `rwf(drift = TRUE)`) or "arima" with order=
  and seasonal_order= (R `arima(method = "ML")`). check_on_last=12 holds back the last rows and measures the
  error (R `forecast::accuracy`: MAE, RMSE, MAPE, MASE); show="model" gives the fitted weights or estimates. A
  Ljung-Box test says whether the leftover errors look like noise. All in R itself (statsmodels' exponential
  smoothing and SARIMAX give other numbers). Needs `simplydata[r]`.
- `table.compare_forecasts("visitors", sorted_by="month", repeats_every="year")`: each method fitted on all but
  the last rows and ranked by MASE on them (R `forecast::accuracy`). Needs `simplydata[r]`.
- `table.find_change_points("nitrate", sorted_by="date", for_each="station")`: where the average (or, with
  change="average and spread", also the spread) jumps, by R `changepoint::cpt.mean` / `cpt.meanvar` (PELT,
  penalty="mbic" as R); one row per piece with its average. Needs `simplydata[r]`.
- `sdata.dates("2026-01-01", to="2026-12-31", every="day")` (or how_many=; every="month", "15 minutes", "2 weeks"
  ...): a one-column table of regular dates. Month steps count from the first date, so a run from the 31st stays
  on the month's last day (pandas DateOffset; R's seq(by = "month") overflows instead).
- `table.add_missing_dates("date", every="day", for_each="station")`: a row for every missing date (empty cells),
  between= to extend the run; every= found from the most common step when not given.
- `table.add_rolling_column` gains window="7 days" (a window of time, pandas rolling("7D")), centre=True (R stats::filter(sides = 2)), and show= "variance",
  "skewness", "kurtosis", "percentile" (percent=), "count", "correlation" and "covariance" (two columns). window="all"
  (from the first row, pandas expanding) is accepted with a note: running values are planned as their own word,
  add_running_column.
- `nums.smooth(method=..., window=...)` and `table.add_smoothed_column(...)`: "moving average" (weights=, ends=
  "empty"/"shorter windows"/"mirror"; R stats::filter), "median" (R runmed itself, Tukey's end rule; needs
  simplydata[r]), "savitzky-golay" (R signal::sgolayfilt), "exponential" (newest_weight=, alpha=, span=,
  half_life=, com=), "gaussian" (width=), "lowess", "spline", "whittaker" (SciPy 1.17 or newer, so Python 3.12 or newer) and "wiener", from SciPy, pandas and
  statsmodels.
- `nums.remove_trend()` (breaks= for a separate line per piece; SciPy detrend, as R residuals(lm(x ~ t))).
- `nums.keep_frequencies(below=10, time_step=0.005)` / `remove_frequencies(...)` and `table.add_filtered_column(...)`:
  low-pass, high-pass, band, band-stop, notch (equal_to=, width=; and_multiples= for a comb) and peak filters.
  method= "butterworth", "chebyshev", "chebyshev 2", "elliptic" or "bessel"; steepness= the order; both_ways=True
  runs forwards and backwards (SciPy sosfiltfilt; MATLAB's ends rule), both_ways=False forwards only (as R
  signal::filter).
- `find_peaks` / `find_dips` on numbers and tables (at_least= / at_most=, apart=, stands_out_by=, wide_at_least=;
  SciPy find_peaks, positions as R pracma::findpeaks).
- `nums.fourier_transform()` and `sdata.inverse_fourier_transform(table)` (SciPy fft, as R fft), `nums.envelope()`
  (SciPy hilbert, as R gsignal::hilbert), `nums.convolve_with` / `deconvolve_by` (as R convolve, pracma::deconv),
  `nums.change_time_step(to=)` (SciPy resample, resample_poly, decimate), `sdata.wave(...)` and
  `sdata.window_shape(...)` (SciPy; as R gsignal).
- `.wav` sound files: `sdata.numbers("call.wav", channel=1)` reads the readings (as R tuneR::readWave) and the numbers
  remember their time step; `nums.save("tone.wav", bits=16)` writes one (SciPy io.wavfile).
- `table.add_envelope_column("signal_envelope", from_column="signal", ...)` (show="envelope", "phase" or
  "frequency"; SciPy hilbert, as R gsignal::hilbert; the new column's name is needed, as on every
  add_..._column word), `sinc(x)` in formulas (as NumPy), and `show_filter=True` on the filter words (the
  filter's Bode chart, titled "run forwards once", and the line that saves it:
  `sdata.frequency_filter(keep_below=10, time_step=0.005).chart().save("filter.png")`).
- Linear systems: `sdata.system("1 / (s**2 + 2*s + 5)")` (or numerator= / denominator=, poles= / zeros= / gain=,
  the matrices a=, b=, c=, d=; z and time_step= for a system in steps; R's num= / den= and A= to D= are
  accepted, but not together with the main spelling) with `step_response(until=, how_many=, time_points=)`
  (rise time, settling time, overshoot), `impulse_response`, `response_to(inputs, time_points=)`,
  `frequency_response(between=, how_many=, unit=)` (columns gain, "gain (decibels)", "phase (degrees)"; the gain
  and phase margins; unit="radians per second" or "cycles per second", "hertz" accepted), `poles` (real part,
  imaginary part, distance from 0, damping ratio, natural frequency), `zeros`, `is_stable`, `steady_gain`,
  `in_steps(time_step=, method=)`, `then`, `add` (side by side, outputs added), `with_feedback(through=, sign=)`,
  `table(form=)` ("power of s" or "power of z", numerator, denominator; "real part" and "imaginary part" for
  poles and zeros) and `chart(show="bode" | "step" | "impulse" | "poles and zeros" | "nyquist", between=, until=,
  unit=)` (an option a chart does not use is refused). sdata.system(poles=, gain=) says that gain= is the number
  in front of the formula, not the steady gain. SciPy signal (lti, dlti, step, lsim, freqresp, freqz,
  cont2discrete, tf2ss), checked against R control, signal and by hand.
- `sdata.frequency_filter(keep_below=10, time_step=0.005)`: the filter of add_filtered_column as a system in steps.
- Chart words: `sticks` (a stem chart), `autocorrelation_bars`, `cross_correlation_bars`, `lag_dots`,
  `trend_and_season` (four panels: the column, its trend, season and rest), `forecast` (dashed line and interval
  band after the lines), `spectrum`, `spectrum_over_time` (SciPy spectrogram) and `peak_dots`. They draw the
  numbers of the table words. The five that draw something other than the column against time take the column
  first and `sorted_by=`, as their table words do: `chart.spectrum("signal", sorted_by="time")`,
  `chart.cross_correlation_bars("signal", "vibration", sorted_by="time")`; x= and y= still work, with a note.
- `add_smoothed_column` without a name adds "<column>_smoothed" (as "_filtered"); `nums.spectrum_of(method=
  "lomb-scargle")` takes the times as `time_points=`.
- Lessons on time series (dates, missing days, time windows, smoothing and trend), forecasts checked on held-back
  months, cycles (spectra, filters, peaks and dips; Welch and check_steady as "more" parts) and, optional, linear
  systems (starting from the filter of the cycles lesson; the Bode chart, margins and systems in steps as "more"
  parts). They come after the lessons of S1 and S2, found by title, so they become lessons 23 to 26. The 30-day
  beginner track gives them a day of their own.
- `chart.smooth_line(method=...)` takes the methods of `nums.smooth` ("moving average", "median",
  "savitzky-golay", "exponential", "gaussian", "whittaker", "wiener") for evenly spaced x.
- New practice table `visitors`: monthly visitors to two made-up museums, 2014 to 2025.
- New practice table `river`: daily water level and nitrate at two made-up stations, 2024 to 2025, with
  missing days and a few empty cells.
- New practice table `sensor`: five seconds of a made-up sensor at 200 readings per second.

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
