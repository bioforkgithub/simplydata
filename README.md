# simplydata

[![PyPI](https://img.shields.io/pypi/v/simplydata)](https://pypi.org/project/simplydata/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24210045.svg)](https://doi.org/10.5281/zenodo.24210045)

**Simple words for data science in Python.** One small vocabulary you can learn in a day,
built on matplotlib, seaborn, pandas, Polars, NumPy, SciPy and statsmodels (with narwhals linking
pandas and Polars), and on R through rpy2 for the methods only R has, so you don't have to learn
them first.

> Status: early development (charts, tables, numbers, statistical tests, fitting and distributions ready). The word list may still change: an old word keeps working for one release and prints a one-line note with its new name.

Install: `pip install simplydata`

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

```
pip install simplydata            # needs Python 3.11 or newer
pip install "simplydata[fast]"    # adds Polars, the fast engine for big data
pip install "simplydata[files]"   # adds reading Word, SPSS and Stata files
pip install "simplydata[systems]" # adds python-control: rise time, settling time and margins of systems
pip install "simplydata[r]"       # adds rpy2, the bridge from Python to R (install R itself from https://cran.r-project.org)
```

The `[r]` extra also needs R (https://cran.r-project.org) and, in R,
`install.packages(...)` with the R packages listed under "What simplydata covers" below. On Windows with
Python 3.13, rpy2 has no ready-made wheel; set `RPY2_CFFI_MODE=ABI` first (in PowerShell:
`$env:RPY2_CFFI_MODE = "ABI"`, in cmd: `set RPY2_CFFI_MODE=ABI`), then run the pip line.

## Learn it in a day

simplydata teaches itself. Open Python and type:

```python
import simplydata as sdata
sdata.show_lesson(1)
```

There are twenty-eight short lessons. Lessons 1 to 8 teach charts, from your first chart to
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
first, then comparisons within groups and against a control. Each
lesson has an example you can run, says what every line does, explains the idea behind it
(average or median, standard deviation or standard error, p-values) and ends with a small task
to try yourself.

- `sdata.show_lesson()` lists the lessons
- `sdata.show_all_words()` lists every word, with an example (also on the first pages of the [dictionary](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydataDictionary.pdf))
- `sdata.help("draw_bars")` explains one word: what it does, its options and an example
  (table and number words too: `sdata.help("keep_rows_where")`, `sdata.help("find_average")`)
- `sdata.get_example()` lists the made-up tables to practise with (marks, weather, fruit, growth, sensor, visitors, river, shop, school, meadow, trial, clinic, island; shop has dates and empty cells)
- `sdata.show_lesson(3, solutions=True)` adds a worked solution to each "Try it yourself" task

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
all twenty-eight lessons with the real charts and output they make, every word explained (its options,
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

## What simplydata covers

These are the packages simplydata gives plain words for, and every R package it calls.

| Area | Python packages |
|---|---|
| Tables | pandas; Polars (`simplydata[fast]`, with pyarrow); narwhals, so the same words work on both; openpyxl for Excel files; python-docx and pyreadstat for Word, SPSS and Stata files (`simplydata[files]`) |
| Numbers and arrays | NumPy |
| Charts | matplotlib and seaborn |
| Statistics | SciPy (`scipy.stats` for tests and distributions; `scipy.special`) and statsmodels (Welch's ANOVA, ANOVA tables, corrections for many tests, lowess smoothing) |
| Models | statsmodels (regression, logistic, Poisson, negative binomial, Gamma, ordered, multinomial (MNLogit) and mixed models, GEE, Cox models and survival curves, multiple imputation) |
| Patterns across many columns | SciPy (`scipy.spatial` for distances, `scipy.cluster` for clustering) and statsmodels (PCA) |
| Fitting, finding and values between points | SciPy (`scipy.optimize` and `scipy.interpolate`) |
| Time series, cycles and filters | SciPy (`scipy.signal` for spectra, filters, peaks and the analytic signal; `scipy.fft` for the Fourier transform) |
| Systems | python-control (`simplydata[systems]`): rise time, settling time, overshoot and stability margins of a system |
| The bridge to R | rpy2 (`simplydata[r]`) |

R packages, used where Python has no method of its own:

| Area | R package | What simplydata uses it for |
|---|---|---|
| Statistics | stats (comes with R) | k-means clustering, smoothing splines, and the linear models behind ANOVA tables |
| Statistics | car | ANOVA tables for each column of a model; variance inflation factors |
| Statistics | effectsize | effect sizes with their 95 % intervals (Hedges' g, omega-squared, rank-biserial, Cramer's V, Kendall's W ...) and partial eta-squared |
| Statistics | pwr | power and sample size for ANOVA, chi-square tests, correlations and two percents |
| Statistics | TOSTER | power of two one-sided tests (`same_within=` in `find_how_many_needed`) |
| Statistics | presize | how many values give a confidence interval of a chosen width |
| Statistics | Exact | Barnard's and Boschloo's tests of a 2 x 2 table |
| Statistics | exact2x2 | the exact interval of the change in percent in McNemar's test |
| Statistics | nortest | the Lilliefors test of a bell shape |
| Statistics | BSDA | the z-test, and the t-test from averages and standard deviations alone |
| Statistics | DescTools | intervals of medians, quantiles, variances and percents; Scheffe and other pair tests; Spearman's, Kendall's, Somers' and Goodman-Kruskal measures with intervals; Lin's concordance |
| Statistics | rstatix | the Games-Howell pair test |
| Statistics | FSA | Dunn's pair test |
| Statistics | PMCMRplus | Conover's pair test |
| Statistics | multcompView | the letters that mark groups that do not differ |
| Statistics | ppcor | partial correlation (`allowing_for=`) |
| Statistics | cocor | comparing two correlations |
| Statistics | outliers | Grubbs' and Dixon's outlier tests |
| Statistics | EnvStats | Rosner's outlier test |
| Risks and diagnostic tests | epiR | the Mantel-Haenszel risk ratio; likelihood ratios of a diagnostic test |
| Risks and diagnostic tests | pROC | trade-off (ROC) curves, the area under them and its interval, and comparing two scores |
| Agreement | irr | the intraclass correlation, Krippendorff's alpha and the p-value of Fleiss' kappa |
| Agreement | psych | Cronbach's alpha and its interval |
| Agreement | BlandAltmanLeh | limits of agreement of two devices |
| Statistics | afex | repeated-measures ANOVA |
| Models | lme4 | mixed models for yes/no and counts; linear mixed models with `own_slope_for=` or `p_value_by="satterthwaite"`; which groups pull a mixed model |
| Models | lmerTest | Satterthwaite p-values for mixed models |
| Models | pbkrtest | Kenward-Roger degrees of freedom for model averages from mixed models |
| Models | emmeans | model averages and their pairs |
| Models | performance | R squared for mixed models |
| Models | MASS | negative binomial and ordered models, when R needs to refit them |
| Models | nnet | models for outcomes with several groups, when R needs to refit them |
| Models | betareg | beta regression for shares |
| Models | pscl | zero-inflated counts |
| Models | geepack | effects for the whole population (GEE) with `within_groups="in time order"` or `out_of=`; other GEE is statsmodels |
| Models | mgcv | smooth curves in a model (GAM) |
| Models | sandwich | robust standard errors |
| Models | mice | pooling the filled-in tables of multiple imputation |
| Survival | survival | the proportional-hazards check of a Cox model |
| Patterns across many columns | vegan | NMDS, PERMANOVA and its spread check (the distances are SciPy `pdist`) |
| Time series | stats (comes with R) | the seasonal split of a series (STL) and the running median |
| Time series | trend | the Mann-Kendall trend test and Sen's slope |
| Time series | tseries | whether a series stays steady (ADF and KPSS tests) |
| Time series | forecast | forecasts and how far off they were on held-back readings |
| Time series | changepoint | the points where the average of a series jumps to a new level |
| Cycles | lomb | the Lomb-Scargle spectrum of readings at uneven times |

To use the words that need R, install R from https://cran.r-project.org, then
`pip install "simplydata[r]"`, then in R `install.packages(...)` with the packages above.
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

> Victor, M. P. simplydata: simple words for data science in Python. Zenodo. https://doi.org/10.5281/zenodo.24210045

This DOI always points to the latest version; each release also has its own DOI on Zenodo. GitHub's "Cite this repository" button gives the same citation in other formats.

## Licence

MIT.
