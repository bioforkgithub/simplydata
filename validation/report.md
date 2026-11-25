# simplydata reliability report

Made by `python validation/make_report.py` on 2026-11-25. Generated: do not edit by hand.

Each simplydata word is run on real, published data and compared with the published answer, with the package simplydata uses underneath called directly, and with R. Each "same underneath" box of the manual is run next to its word and compared too. How it works, and the datasets with their licences: [validation/README.md](README.md); which words are compared here, which in the separate test study (simplydata_tests) and which have nothing to compare: its section "Which words are compared, and where".

**5662 checks passed, 9 explained differences, 0 failed, 3 skipped** (skipped: R or an R package is not installed on this computer, or, for 3, the data may not be passed on and no file was given; an explained difference falls short of its tolerance for a stated reason, a limit of precision, and is listed with that reason).

## Setup

| | |
|---|---|
| system | Linux 7.0.0-1020-azure (x86_64) |
| Python | 3.12.16 |
| simplydata | 0.2.0 (imported from src/simplydata of this copy) |
| pandas | 3.1.1 |
| polars | 2.2.0 |
| narwhals | 2.29.0 |
| numpy | 2.5.5 |
| scipy | 1.18.1 |
| statsmodels | 0.15.0 |
| matplotlib | 3.11.2 |
| seaborn | 0.13.2 |
| control | 0.10.2 |
| rpy2 | 3.6.9 |
| R | 4.6.2 (2026-10-29) |

## 1. Published and real data

Kinds: *published* = real data with a published or certified answer; *real data* = real data, compared with the parent package and R; *made-up* = a made-up edge case (empty cells, no rows left, an exact line) that no real dataset tests; *closed form* = no data at all: a word that makes something from a formula (a system, a wave, a window shape) checked against the answer worked out by hand from that formula (and against the parent package and R).

### `table.fit_line`

**straight line through 36 ozone calibration points** (published; data: NIST Norris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | NIST certified | 1.00211681802045 | 1.00211681802045 | at least 9 digits (LRE 14.4) | pass |
| intercept | NIST certified | -0.262323073774041 | -0.262323073774029 | at least 9 digits (LRE 13.3) | pass |
| slope standard error | NIST certified | 0.000429796848185389 | 0.000429796848199937 | at least 9 digits (LRE 10.5) | pass |
| intercept standard error | NIST certified | 0.232818234293272 | 0.232818234301152 | at least 9 digits (LRE 10.5) | pass |
| R squared | NIST certified | 0.999993745883712 | 0.999993745883712 | at least 9 digits (LRE 15.0) | pass |
| slope | SciPy stats.linregress | 1.00211681802045 | 1.00211681802045 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | -0.262323073774041 | -0.262323073774041 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.000429796848185389 | 0.000429796848185389 | relative 1e-09 | pass |
| intercept standard error | SciPy stats.linregress | 0.232818234293272 | 0.232818234293272 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.999993745883712 | 0.999993745883712 | relative 1e-09 | pass |
| slope | R | 1.00211681802045 | 1.00211681802045 | relative 1e-09 | pass |
| intercept | R | -0.262323073774041 | -0.26232307377373 | relative 1e-09 | pass |
| slope standard error | R | 0.000429796848185389 | 0.000429796848199947 | relative 1e-09 | pass |
| intercept standard error | R | 0.232818234293272 | 0.232818234301158 | relative 1e-09 | pass |
| R squared | R | 0.999993745883712 | 0.999993745883712 | relative 1e-09 | pass |

**Anscombe's set 1: the same line through four different patterns** (published; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | Anscombe (1973) | 0.500090909090909 | 0.5 | within 0.001 (printed rounding) | pass |
| intercept | Anscombe (1973) | 3.00009090909091 | 3 | within 0.01 (printed rounding) | pass |
| slope standard error | Anscombe (1973) | 0.117905500595634 | 0.118 | within 0.001 (printed rounding) | pass |
| R squared | Anscombe (1973) | 0.666542459508775 | 0.667 | within 0.001 (printed rounding) | pass |
| slope | SciPy stats.linregress | 0.500090909090909 | 0.500090909090909 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | 3.00009090909091 | 3.00009090909091 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.117905500595634 | 0.117905500595634 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.666542459508775 | 0.666542459508775 | relative 1e-09 | pass |

Note: The paper prints the fit rounded (3 + 0.5 x); its sets agree with it to within about one unit of the last printed digit, so the check allows the printed rounding plus that much.

**Anscombe's set 2: the same line through four different patterns** (published; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | Anscombe (1973) | 0.5 | 0.5 | within 0.001 (printed rounding) | pass |
| intercept | Anscombe (1973) | 3.00090909090909 | 3 | within 0.01 (printed rounding) | pass |
| slope standard error | Anscombe (1973) | 0.117963745967641 | 0.118 | within 0.001 (printed rounding) | pass |
| R squared | Anscombe (1973) | 0.666242033727485 | 0.667 | within 0.001 (printed rounding) | pass |
| slope | SciPy stats.linregress | 0.5 | 0.5 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | 3.00090909090909 | 3.00090909090909 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.117963745967641 | 0.117963745967641 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.666242033727485 | 0.666242033727485 | relative 1e-09 | pass |

Note: The paper prints the fit rounded (3 + 0.5 x); its sets agree with it to within about one unit of the last printed digit, so the check allows the printed rounding plus that much.

**Anscombe's set 3: the same line through four different patterns** (published; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | Anscombe (1973) | 0.499727272727273 | 0.5 | within 0.001 (printed rounding) | pass |
| intercept | Anscombe (1973) | 3.00245454545454 | 3 | within 0.01 (printed rounding) | pass |
| slope standard error | Anscombe (1973) | 0.117877662221002 | 0.118 | within 0.001 (printed rounding) | pass |
| R squared | Anscombe (1973) | 0.66632404106656 | 0.667 | within 0.001 (printed rounding) | pass |
| slope | SciPy stats.linregress | 0.499727272727273 | 0.499727272727273 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | 3.00245454545454 | 3.00245454545454 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.117877662221002 | 0.117877662221002 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.66632404106656 | 0.66632404106656 | relative 1e-09 | pass |

Note: The paper prints the fit rounded (3 + 0.5 x); its sets agree with it to within about one unit of the last printed digit, so the check allows the printed rounding plus that much.

**Anscombe's set 4: the same line through four different patterns** (published; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | Anscombe (1973) | 0.499909090909091 | 0.5 | within 0.001 (printed rounding) | pass |
| intercept | Anscombe (1973) | 3.00172727272727 | 3 | within 0.01 (printed rounding) | pass |
| slope standard error | Anscombe (1973) | 0.117818941729686 | 0.118 | within 0.001 (printed rounding) | pass |
| R squared | Anscombe (1973) | 0.666707256898465 | 0.667 | within 0.001 (printed rounding) | pass |
| slope | SciPy stats.linregress | 0.499909090909091 | 0.499909090909091 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | 3.00172727272727 | 3.00172727272727 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.117818941729686 | 0.117818941729686 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.666707256898465 | 0.666707256898465 | relative 1e-09 | pass |

Note: The paper prints the fit rounded (3 + 0.5 x); its sets agree with it to within about one unit of the last printed digit, so the check allows the printed rounding plus that much.

**points exactly on y = 2 x + 1** (made-up; data: made-up)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | exact | 2 | 2 | within 1e-12 | pass |
| intercept | exact | 1 | 1 | within 1e-12 | pass |
| R squared | exact | 1 | 1 | within 1e-12 | pass |

### `table.find_average_of`

**average of Michelson's 100 speed-of-light measurements** (published; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 299.8524 | 299.8524 | at least 9 digits (LRE 15.0) | pass |
| mean | pandas Series.mean | 299.8524 | 299.8524 | relative 1e-09 | pass |
| mean | R | 299.8524 | 299.8524 | relative 1e-09 | pass |

**average of 50 filter transmittance measurements** (published; data: NIST Mavro)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 2.001856 | 2.001856 | at least 9 digits (LRE 15.0) | pass |
| mean | pandas Series.mean | 2.001856 | 2.001856 | relative 1e-09 | pass |
| mean | R | 2.001856 | 2.001856 | relative 1e-09 | pass |

**average of 1001 nine-digit numbers that differ only in the last digit** (published; data: NIST NumAcc4)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 10000000.2 | 10000000.2 | at least 9 digits (LRE 15.0) | pass |
| mean | pandas Series.mean | 10000000.2 | 10000000.2 | relative 1e-09 | pass |
| mean | R | 10000000.2 | 10000000.2 | relative 1e-09 | pass |

**an empty cell is skipped** (made-up; data: made-up)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NumPy nanmean | 4 | 4 | relative 1e-15 | pass |

### `nums.find_median`

**median of Michelson's 100 speed-of-light measurements** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| median | NumPy nanmedian | 299.85 | 299.85 | relative 1e-15 | pass |
| median | R | 299.85 | 299.85 | relative 1e-15 | pass |

Note: NIST certifies no median; the median is checked against NumPy and R on the same data.

**median of 50 filter transmittance measurements** (real data; data: NIST Mavro)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| median | NumPy nanmedian | 2.0018 | 2.0018 | relative 1e-15 | pass |
| median | R | 2.0018 | 2.0018 | relative 1e-15 | pass |

Note: NIST certifies no median; the median is checked against NumPy and R on the same data.

**median of NumAcc4 (exact by construction: 500 values .1 below and 500 .1 above 10000000.2)** (published; data: NIST NumAcc4)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| median | NIST NumAcc4 description (exact by construction) | 10000000.2 | 10000000.2 | within 1e-09 (printed rounding) | pass |
| median | NumPy nanmedian | 10000000.2 | 10000000.2 | relative 1e-15 | pass |

### `table.compare_averages_of`

**two drugs, extra hours of sleep (Welch's t-test)** (published; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average in drug 1 | Student (1908) | 0.75 | 0.75 | within 0.005 (printed rounding) | pass |
| average in drug 2 | Student (1908) | 2.33 | 2.33 | within 0.005 (printed rounding) | pass |
| difference | Student (1908) | -1.58 | -1.58 | within 0.005 (printed rounding) | pass |
| average in drug 1 | SciPy stats.ttest_ind(equal_var=False) | 0.75 | 0.75 | relative 1e-09 | pass |
| average in drug 2 | SciPy stats.ttest_ind(equal_var=False) | 2.33 | 2.33 | relative 1e-09 | pass |
| difference | SciPy stats.ttest_ind(equal_var=False) | -1.58 | -1.58 | relative 1e-09 | pass |
| t | SciPy stats.ttest_ind(equal_var=False) | -1.86081346748685 | -1.86081346748685 | relative 1e-09 | pass |
| degrees of freedom | SciPy stats.ttest_ind(equal_var=False) | 17.7764735161785 | 17.7764735161785 | relative 1e-09 | pass |
| p-value | SciPy stats.ttest_ind(equal_var=False) | 0.0793941401873583 | 0.0793941401873583 | relative 1e-09 | pass |
| t | R | -1.86081346748685 | -1.86081346748685 | relative 1e-09 | pass |
| degrees of freedom | R | 17.7764735161785 | 17.7764735161785 | relative 1e-09 | pass |
| p-value | R | 0.0793941401873583 | 0.0793941401873582 | relative 1e-09 | pass |

Note: These data are paired: each patient took both drugs, and Student (1908) analysed the difference within each patient (the paired case below). This case treats the two drugs as two separate groups only to check the arithmetic of the two-group (Welch) test against SciPy and R; it is not the right analysis of these data. Student printed the standard deviations with n in the divisor (1.70 and 1.90); simplydata, NumPy with ddof=1, and R use n - 1 (1.79 and 2.00), a documented choice. simplydata's difference is drug 1 minus drug 2, so Student's +1.58 is -1.58 here.

### `table.compare_before_and_after`

**two drugs in the same 10 patients (paired t-test, as Student analysed them)** (published; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average change | Student (1908) | 1.58 | 1.58 | within 0.005 (printed rounding) | pass |
| average change | SciPy stats.ttest_rel | 1.58 | 1.58 | relative 1e-09 | pass |
| t | SciPy stats.ttest_rel | 4.06212768338204 | 4.06212768338204 | relative 1e-09 | pass |
| degrees of freedom | SciPy stats.ttest_rel | 9 | 9 | relative 1e-09 | pass |
| p-value | SciPy stats.ttest_rel | 0.00283289019738427 | 0.00283289019738427 | relative 1e-09 | pass |
| t | R | 4.06212768338204 | 4.06212768338204 | relative 1e-09 | pass |
| degrees of freedom | R | 9 | 9 | relative 1e-09 | pass |
| p-value | R | 0.00283289019738427 | 0.00283289019738427 | relative 1e-09 | pass |

Note: Student also printed the standard deviation of the differences, 1.17, with n in the divisor; with n - 1 it is 1.23. simplydata does not print it, so it is not compared.

### `draw_bars`

**bar heights are Student's two averages** (published; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bar 1 | Student (1908) | 0.75 | 0.75 | within 0.005 (printed rounding) | pass |
| bar 2 | Student (1908) | 2.33 | 2.33 | within 0.005 (printed rounding) | pass |
| bar 1 | seaborn barplot | 0.75 | 0.75 | relative 1e-09 | pass |
| bar 2 | seaborn barplot | 2.33 | 2.33 | relative 1e-09 | pass |

### `draw_histogram`

**Michelson's speed of light in 10 bins** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bin 1 | NumPy histogram (bins=10) | 2 | 2 | relative 1e-09 | pass |
| bin 2 | NumPy histogram (bins=10) | 0 | 0 | relative 1e-09 | pass |
| bin 3 | NumPy histogram (bins=10) | 7 | 7 | relative 1e-09 | pass |
| bin 4 | NumPy histogram (bins=10) | 11 | 11 | relative 1e-09 | pass |
| bin 5 | NumPy histogram (bins=10) | 27 | 27 | relative 1e-09 | pass |
| bin 6 | NumPy histogram (bins=10) | 25 | 25 | relative 1e-09 | pass |
| bin 7 | NumPy histogram (bins=10) | 10 | 10 | relative 1e-09 | pass |
| bin 8 | NumPy histogram (bins=10) | 11 | 11 | relative 1e-09 | pass |
| bin 9 | NumPy histogram (bins=10) | 6 | 6 | relative 1e-09 | pass |
| bin 10 | NumPy histogram (bins=10) | 1 | 1 | relative 1e-09 | pass |
| first edge | NumPy histogram (bins=10) | 299.62 | 299.62 | relative 1e-09 | pass |
| last edge | NumPy histogram (bins=10) | 300.07 | 300.07 | relative 1e-09 | pass |
| bin 1 | R | 2 | 2 | relative 1e-09 | pass |
| bin 2 | R | 0 | 0 | relative 1e-09 | pass |
| bin 3 | R | 7 | 7 | relative 1e-09 | pass |
| bin 4 | R | 11 | 11 | relative 1e-09 | pass |
| bin 5 | R | 27 | 27 | relative 1e-09 | pass |
| bin 6 | R | 25 | 25 | relative 1e-09 | pass |
| bin 7 | R | 10 | 10 | relative 1e-09 | pass |
| bin 8 | R | 11 | 11 | relative 1e-09 | pass |
| bin 9 | R | 6 | 6 | relative 1e-09 | pass |
| bin 10 | R | 1 | 1 | relative 1e-09 | pass |

### `draw_dots`

**the 36 Norris calibration points** (real data; data: NIST Norris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | the data themselves (every point drawn once) | 36 | 36 | relative 1e-09 | pass |
| sum of x | the data themselves (every point drawn once) | 15090.4 | 15090.4 | relative 1e-09 | pass |
| sum of y | the data themselves (every point drawn once) | 15112.9 | 15112.9 | relative 1e-09 | pass |

### `trade_off_curve`

**ROC curve of s100b for a poor outcome** (real data; data: aSAH (pROC))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | R | 51 | 51 | relative 1e-09 | pass |
| area under the drawn curve | R | 0.731368563685637 | 0.731368563685637 | relative 1e-09 | pass |

Note: The area under the drawn curve (trapezoids) must equal pROC's AUC: the curve has every point.

### `table.keep_rows_where`

**Michelson's measurements above 299.9 (in thousands of km per second)** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows kept | pandas boolean indexing | 23 | 23 | relative 1e-12 | pass |
| sum kept | pandas boolean indexing | 6899.09 | 6899.09 | relative 1e-12 | pass |
| smallest kept | pandas boolean indexing | 299.91 | 299.91 | relative 1e-12 | pass |
| rows kept | R | 23 | 23 | relative 1e-12 | pass |
| sum kept | R | 6899.09 | 6899.09 | relative 1e-12 | pass |
| smallest kept | R | 299.91 | 299.91 | relative 1e-12 | pass |

**an empty cell is not above 2, and no row is left when none is above 50** (made-up; data: made-up)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows kept | pandas boolean indexing | 2 | 2 | exact | pass |
| sum kept | pandas boolean indexing | 10 | 10 | exact | pass |
| rows when none is above | pandas boolean indexing | 0 | 0 | exact | pass |

### `dist.find_chance_that_value`

**chance above 1.96 in the standard normal distribution** (published; data: standard normal table)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chance above 1.96 | NIST/SEMATECH e-Handbook, table 1.3.6.7.1 | 0.0249978951482204 | 0.025 | within 5e-06 (printed rounding) | pass |
| chance above 1.96 | SciPy stats.norm.sf | 0.0249978951482204 | 0.0249978951482204 | relative 1e-14 | pass |
| chance above 1.96 | R | 0.0249978951482204 | 0.0249978951482204 | relative 1e-14 | pass |

Note: No data: the published value is the standard normal table (5 decimals).

### `table.explain weights=`

**weighted least squares: offspring diameter from the parent's, each row weighted by 1 / its variance** (real data; data: Galton's sweet peas)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | statsmodels WLS | 0.204801163243056 | 0.204801163243056 | relative 1e-09 | pass |
| slope standard error | statsmodels WLS | 0.0381548260706377 | 0.0381548260706378 | relative 1e-09 | pass |
| intercept | statsmodels WLS | 12.7964165214901 | 12.7964165214901 | relative 1e-09 | pass |
| slope | R | 0.204801163243056 | 0.204801163243057 | relative 1e-09 | pass |
| slope standard error | R | 0.0381548260706377 | 0.0381548260706376 | relative 1e-09 | pass |
| intercept | R | 12.7964165214901 | 12.7964165214901 | relative 1e-09 | pass |

Note: Weisberg (2014, section 7.1) fits this weighted line; the numbers are checked against statsmodels and R rather than the book's printed table.

### `table.explain outcome="yes or no (overdispersed)"`

**quasi-binomial: seeds that germinated out of seeds, by variety and root extract** (real data; data: Orobanche seeds)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| extract | statsmodels GLM (Binomial, scale X2) | 0.540078166603428 | 0.540078166603428 | relative 1e-07 | pass |
| extract standard error | statsmodels GLM (Binomial, scale X2) | 0.340867231336386 | 0.340867231336386 | relative 1e-07 | pass |
| interaction standard error | statsmodels GLM (Binomial, scale X2) | 0.418124932214023 | 0.418124932214023 | relative 1e-07 | pass |
| extract | R | 0.540078166603428 | 0.540078166603429 | relative 1e-06 | pass |
| extract standard error | R | 0.340867231336386 | 0.340867231340939 | relative 1e-06 | pass |
| interaction standard error | R | 0.418124932214023 | 0.418124932215663 | relative 1e-06 | pass |
| interaction p-value | R | 0.0801390217137059 | 0.0801390217147883 | relative 1e-06 | pass |

Note: Crowder (1978) fitted a beta-binomial model; the quasi-binomial fit of the same data (Collett 2003, Modelling Binary Data) is checked here against statsmodels and R.

### `table.explain matched_by=`

**conditional logistic regression: infertility and earlier abortions in matched sets** (real data; data: infert)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| spontaneous | statsmodels ConditionalLogit | 1.98587551668241 | 1.98587551668241 | relative 1e-07 | pass |
| induced | statsmodels ConditionalLogit | 1.40901163187936 | 1.40901163187936 | relative 1e-07 | pass |
| spontaneous standard error | statsmodels ConditionalLogit | 0.352443539645452 | 0.352443543187006 | relative 1e-07 | pass |
| induced standard error | statsmodels ConditionalLogit | 0.360712433692957 | 0.360712438256113 | relative 1e-07 | pass |
| spontaneous | R | 1.98587551668241 | 1.98587551667772 | relative 1e-06 | pass |
| induced | R | 1.40901163187936 | 1.40901163187514 | relative 1e-06 | pass |
| spontaneous standard error | R | 0.352443539645452 | 0.35244353980717 | relative 1e-06 | pass |
| induced standard error | R | 0.360712433692957 | 0.360712436248923 | relative 1e-06 | pass |

Note: The model of R's ?clogit example; R and statsmodels both use the exact conditional likelihood.

### `table.explain show="risk ratios"`

**risk ratio of low birth weight for smokers equals the 2 x 2 table's** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| risk ratio, smoking alone | statsmodels Table2x2 and GLM (Poisson, HC0) | 1.6076421248835 | 1.6076421248835 | relative 1e-06 | pass |
| log risk ratio with age | statsmodels Table2x2 and GLM (Poisson, HC0) | 0.460730395503193 | 0.460730395503193 | relative 1e-06 | pass |
| standard error with age | statsmodels Table2x2 and GLM (Poisson, HC0) | 0.213624213081043 | 0.213624213081043 | relative 1e-06 | pass |
| log risk ratio with age | R | 0.460730395503193 | 0.460730390124031 | relative 1e-06 | pass |
| standard error with age | R | 0.213624213081043 | 0.2136243204413 | relative 1e-06 | pass |

Note: With one yes/no column, the modified Poisson risk ratio is the risk ratio of the 2 x 2 table (Zou 2004), here from statsmodels' Table2x2.

### `table.explain test_method="log-binomial"`

**log-binomial risk ratio of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| log risk ratio | R | 0.444051519404953 | 0.444052356626725 | relative 1e-05 | pass |
| standard error | R | 0.2125706249025 | 0.212571063773311 | relative 1e-05 | pass |

### `table.explain giving_outliers_less_weight=`

**Huber's robust regression of stack loss** (real data; data: stackloss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| air flow | statsmodels RLM (HuberT) | 0.829384334599656 | 0.829384334599656 | relative 1e-09 | pass |
| water temperature | statsmodels RLM (HuberT) | 0.926065966198343 | 0.926065966198346 | relative 1e-09 | pass |
| acid concentration | statsmodels RLM (HuberT) | -0.127846724945884 | -0.127846724945885 | relative 1e-09 | pass |
| intercept | statsmodels RLM (HuberT) | -41.0264983523997 | -41.0264983523998 | relative 1e-09 | pass |
| air flow standard error | statsmodels RLM (HuberT) | 0.111005213354579 | 0.11100521335458 | relative 1e-09 | pass |
| air flow | R | 0.829384334599656 | 0.829385770253742 | relative 1e-05 | pass |
| water temperature | R | 0.926065966198343 | 0.92605941554903 | relative 1e-05 | pass |
| acid concentration | R | -0.127846724945884 | -0.12784631796544 | relative 1e-05 | pass |
| intercept | R | -41.0264983523997 | -41.0264853732949 | relative 1e-05 | pass |

Note: Venables & Ripley (2002, chapter 6) fit rlm() to these data. The estimates agree with R to the stopping rules of the two fits; the standard errors are statsmodels' (Huber's H1), which differ from R's summary(rlm) in the third digit, so R's are not compared.

### `table.explain with_knots=`

**a natural spline with 3 knots through the 36 Norris calibration points** (real data; data: NIST Norris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| F of the whole curve | patsy cr() and statsmodels OLS | 1309424.66989212 | 1309424.66989217 | relative 1e-09 | pass |
| F of the whole curve | R | 1309424.66989212 | 1309424.66989218 | relative 1e-08 | pass |

Note: The spline's own coefficients differ between patsy and R's ns() (another basis of the same curves); the test of the whole curve and the fitted values are the same, so those are compared.

### `table.explain show="standardised effects"`

**standardised effects of weight, horsepower and gearbox on fuel use** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| weight | statsmodels OLS on z-scores | -0.467328325133065 | -0.467328325133065 | relative 1e-09 | pass |
| horsepower | statsmodels OLS on z-scores | -0.426359898323383 | -0.426359898323383 | relative 1e-09 | pass |
| gearbox | statsmodels OLS on z-scores | 0.17251723761303 | 0.17251723761303 | relative 1e-09 | pass |
| weight 95 % CI low | statsmodels OLS on z-scores | -0.768278926188221 | -0.768278926188221 | relative 1e-09 | pass |
| weight | R | -0.467328325133065 | -0.467328325133065 | relative 1e-08 | pass |
| horsepower | R | -0.426359898323383 | -0.426359898323383 | relative 1e-08 | pass |
| gearbox | R | 0.17251723761303 | 0.17251723761303 | relative 1e-08 | pass |
| weight 95 % CI low | R | -0.768278926188221 | -0.768278926188221 | relative 1e-08 | pass |

### `table.explain interval_by="bootstrap"`

**bootstrap intervals of the air-flow effect on stack loss** (real data; data: stackloss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 95 % CI low | SciPy stats.bootstrap (BCa) | 0.638744784688277 | 0.638744784688277 | relative 1e-09 | pass |
| 95 % CI high | SciPy stats.bootstrap (BCa) | 1.17896864783934 | 1.17896864783934 | relative 1e-09 | pass |
| 95 % CI low | R | 0.638744784688277 | 0.617466087556167 | within 4 Monte Carlo SE (0.0783) | pass |
| 95 % CI high | R | 1.17896864783934 | 1.17339381682502 | within 4 Monte Carlo SE (0.00853) | pass |

Note: R draws other random rows than SciPy, so R checks the same method within its Monte Carlo error: R boot runs 10 times (seeds 1 to 10, 9999 resamples each); the reference is their average, and the difference may be 4 Monte Carlo standard errors, from the spread of R's 10 runs (simplydata's one run of 9999 resamples is taken to vary as much as one of R's). SciPy with the same seed gives the same interval exactly.

### `table.explain interval_by="profile"`

**profile-likelihood intervals of a logistic regression of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| smoke low | R | 0.032671077242603 | 0.032671077242603 | relative 1e-06 | pass |
| smoke high | R | 1.31383593363347 | 1.31383593363347 | relative 1e-06 | pass |
| lwt low | R | -0.0249706001060748 | -0.0249706001060748 | relative 1e-06 | pass |

Note: simplydata runs R's confint() itself (statsmodels has no profile intervals); this case checks that the model R gets is the model explain() fits, from the formula side.

### `table.explain p_value_by="likelihood ratio"`

**likelihood-ratio tests in a logistic regression of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| smoke | statsmodels GLM refits and SciPy chi2 | 0.0393884378670759 | 0.0393884378670759 | relative 1e-08 | pass |
| age | statsmodels GLM refits and SciPy chi2 | 0.226723754237082 | 0.226723754237077 | relative 1e-08 | pass |
| lwt | statsmodels GLM refits and SciPy chi2 | 0.03600350492921 | 0.0360035049292094 | relative 1e-08 | pass |
| smoke | R | 0.0393884378670759 | 0.0393884378670747 | relative 1e-07 | pass |
| age | R | 0.226723754237082 | 0.226723754237081 | relative 1e-07 | pass |
| lwt | R | 0.03600350492921 | 0.0360035049292096 | relative 1e-07 | pass |

### `table.explain`

**Nagelkerke's and Tjur's pseudo R squared of a logistic regression of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Nagelkerke | R | 0.0850637355720787 | 0.085063735572079 | relative 1e-09 | pass |
| Tjur | R | 0.058487286125849 | 0.058487286125848 | relative 1e-09 | pass |

Note: The printout gives the two measures with 3 decimals; the check takes them at full precision from the same statsmodels fit and the same function explain() prints them with (and checks that the printout is their rounding), so it is not limited by the printed rounding.

**Longley: six predictors that move almost together (NIST certified)** (published; data: NIST Longley)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | -3482258.63459792 | -3482258.63459582 | at least 9 digits (LRE 12.2) | pass |
| b0 standard error | NIST certified | 890420.383607341 | 890420.383607373 | at least 9 digits (LRE 13.4) | pass |
| b1 | NIST certified | 15.0618722715518 | 15.0618722713733 | at least 9 digits (LRE 10.9) | pass |
| b1 standard error | NIST certified | 84.9149257747738 | 84.9149257747669 | at least 9 digits (LRE 13.1) | pass |
| b2 | NIST certified | -0.035819179292647 | -0.035819179292591 | at least 9 digits (LRE 11.8) | pass |
| b2 standard error | NIST certified | 0.0334910077722407 | 0.0334910077722432 | at least 9 digits (LRE 13.1) | pass |
| b3 | NIST certified | -2.02022980381741 | -2.02022980381683 | at least 9 digits (LRE 12.5) | pass |
| b3 standard error | NIST certified | 0.488399681651607 | 0.488399681651699 | at least 9 digits (LRE 12.7) | pass |
| b4 | NIST certified | -1.03322686717365 | -1.03322686717359 | at least 9 digits (LRE 13.2) | pass |
| b4 standard error | NIST certified | 0.214274163161642 | 0.214274163161675 | at least 9 digits (LRE 12.8) | pass |
| b5 | NIST certified | -0.051104105653695 | -0.0511041056535807 | at least 9 digits (LRE 11.7) | pass |
| b5 standard error | NIST certified | 0.226073200069334 | 0.22607320006937 | at least 9 digits (LRE 12.8) | pass |
| b6 | NIST certified | 1829.15146461464 | 1829.15146461355 | at least 9 digits (LRE 12.2) | pass |
| b6 standard error | NIST certified | 455.478499142198 | 455.478499142212 | at least 9 digits (LRE 13.5) | pass |

Note: The standard errors use R summary.lm()'s inv(R) inv(R)' from the QR factor; statsmodels' own inv(R'R) after its QR fit gave only 7.97 to 9.42 digits here.

### `table.explain crossed_with=`

**people and items crossed: verbal aggression (yes or no) from anger and gender** (real data; data: VerbAgg)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| anger | R | 0.0574458838988813 | 0.0574458838988813 | relative 1e-06 | pass |
| anger standard error | R | 0.0168463055675871 | 0.0168463055675871 | relative 1e-06 | pass |
| gender | R | 0.320648189300347 | 0.320648189300347 | relative 1e-06 | pass |

Note: simplydata runs lme4 itself (statsmodels cannot fit crossed groupings); this case checks the model R gets from explain() against R's own formula. simplydata hands the groups to R as text, so their order is that of text ("1", "10", "100" ...); R's reference does the same. A user's own R run on the whole-number ids orders them as numbers, and its glmer standard errors (from a numerical Hessian) then differ in the fourth digit.

### `table.explain outcome="counts in two steps"`

**two-step (hurdle) model of physician office visits** (published; data: NMES 1988)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count: hospital | Zeileis et al. (2008) | 0.211898197949242 | 0.211898 | within 5e-07 (printed rounding) | pass |
| count: health poor | Zeileis et al. (2008) | 0.315957574199259 | 0.315958 | within 5e-07 (printed rounding) | pass |
| count: chronic | Zeileis et al. (2008) | 0.126420588812089 | 0.126421 | within 5e-07 (printed rounding) | pass |
| count: chronic standard error | Zeileis et al. (2008) | 0.0124523069035939 | 0.012452 | within 5e-07 (printed rounding) | pass |
| zero: chronic | Zeileis et al. (2008) | 0.535212638440462 | 0.535213 | within 5e-07 (printed rounding) | pass |
| zero: insurance | Zeileis et al. (2008) | 0.747119812959575 | 0.74712 | within 5e-07 (printed rounding) | pass |
| zero: insurance standard error | Zeileis et al. (2008) | 0.100879503174149 | 0.10088 | within 5e-07 (printed rounding) | pass |

Note: The paper's model fm_hurdle0: a negative binomial count part and a logistic zero hurdle, the same columns in both.

### `table.explain outcome="counts with many zeros that vary a lot"`

**zero-inflated negative binomial model of physician office visits, the zero part with its own columns** (published; data: NMES 1988)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count: hospital | Zeileis et al. (2008), Table 2 | 0.201476829498611 | 0.201 | within 0.0005 (printed rounding) | pass |
| count: health poor | Zeileis et al. (2008), Table 2 | 0.285132769246967 | 0.285 | within 0.0005 (printed rounding) | pass |
| zero: hospital | Zeileis et al. (2008), Table 2 | -0.800464995130165 | -0.8 | within 0.0005 (printed rounding) | pass |
| zero: chronic | Zeileis et al. (2008), Table 2 | -1.24789708597445 | -1.248 | within 0.0005 (printed rounding) | pass |
| zero: gender male | Zeileis et al. (2008), Table 2 | 0.647660217015324 | 0.648 | within 0.0005 (printed rounding) | pass |
| count: hospital | statsmodels ZeroInflatedNegativeBinomialP | 0.201476829498611 | 0.201476841187623 | relative 0.0001 | pass |
| zero: hospital | statsmodels ZeroInflatedNegativeBinomialP | -0.800464995130165 | -0.800490700364435 | relative 0.0001 | pass |
| zero: chronic | statsmodels ZeroInflatedNegativeBinomialP | -1.24789708597445 | -1.24793581168842 | relative 0.0001 | pass |

Note: The paper's model fm_zinb (the zero part without health). simplydata runs R pscl itself, for its standard errors; statsmodels gives the same estimates.

### `table.explain zero_part_using=`

**two-step (hurdle) model whose zero part has its own columns** (published; data: NMES 1988)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| zero: intercept | Zeileis et al. (2008), Table 2 | 0.0159401738285058 | 0.016 | within 0.0005 (printed rounding) | pass |
| zero: hospital | Zeileis et al. (2008), Table 2 | 0.318434481481662 | 0.318 | within 0.0005 (printed rounding) | pass |
| zero: chronic | Zeileis et al. (2008), Table 2 | 0.54783250793305 | 0.548 | within 0.0005 (printed rounding) | pass |
| zero: insurance | Zeileis et al. (2008), Table 2 | 0.745720049336323 | 0.746 | within 0.0005 (printed rounding) | pass |
| zero: school | Zeileis et al. (2008), Table 2 | 0.0570728152413954 | 0.057 | within 0.0005 (printed rounding) | pass |
| zero: gender male | Zeileis et al. (2008), Table 2 | -0.419147791025234 | -0.419 | within 0.0005 (printed rounding) | pass |
| zero: intercept | statsmodels Logit (the first step on its own) | 0.0159401738285058 | 0.0159401718063209 | relative 1e-06 | pass |
| zero: hospital | statsmodels Logit (the first step on its own) | 0.318434481481662 | 0.318434494004322 | relative 1e-06 | pass |
| zero: chronic | statsmodels Logit (the first step on its own) | 0.54783250793305 | 0.547832508738329 | relative 1e-06 | pass |
| zero: insurance | statsmodels Logit (the first step on its own) | 0.745720049336323 | 0.745720049922439 | relative 1e-06 | pass |
| zero: school | statsmodels Logit (the first step on its own) | 0.0570728152413954 | 0.0570728147518849 | relative 1e-06 | pass |
| zero: gender male | statsmodels Logit (the first step on its own) | -0.419147791025234 | -0.419147791543225 | relative 1e-06 | pass |

Note: The first step of a hurdle model is a logistic regression of zero or not, so statsmodels' Logit gives the same numbers as pscl's zero hurdle.

### `table.fit_dose_response`

**ryegrass root length and ferulic acid: LL.4 curve and ED10, ED50, ED90** (real data; data: ryegrass (drc))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 2.98222857655474 | 2.98222867449863 | relative 2e-06 | pass |
| c | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 0.481409615432056 | 0.481409945466304 | relative 2e-06 | pass |
| d | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 7.79296184542426 | 7.79296232719357 | relative 2e-06 | pass |
| ED10 | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 1.46370952427292 | 1.46370922438271 | relative 2e-06 | pass |
| ED50 | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 3.05795586800215 | 3.05795516748209 | relative 2e-06 | pass |
| ED90 | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 6.38862693422303 | 6.38862531612046 | relative 2e-06 | pass |
| b | R | 2.98222857655474 | 2.98222857655474 | relative 1e-09 | pass |
| c | R | 0.481409615432056 | 0.481409615432056 | relative 1e-09 | pass |
| d | R | 7.79296184542426 | 7.79296184542426 | relative 1e-09 | pass |
| ED10 | R | 1.46370952427292 | 1.46370952427292 | relative 1e-09 | pass |
| ED50 | R | 3.05795586800215 | 3.05795586800215 | relative 1e-09 | pass |
| ED90 | R | 6.38862693422303 | 6.38862693422303 | relative 1e-09 | pass |
| ED50 95 % CI low | R | 2.67052745830929 | 2.67052745830929 | relative 1e-09 | pass |

Note: Python has no dose-response package with drc's ED intervals, so R drc itself gives the intervals; SciPy curve_fit, run to 1e-15, is the independent fit of the curve. The optimum is flat (the residual sum of squares of the two fits agrees to 1e-12), so the estimates agree to about 1e-6. drc's default stopping rule (relTol 1e-7) stopped 1e-6 to 1.4e-5 short; simplydata asks for 1e-15. Ritz et al. (2015) analyse these data with the same LL.4 model.

### `table.fit_dose_response outcome="yes or no"`

**Bliss's beetles: LD50 from the logistic curve on log dose (yes or no)** (published; data: Bliss beetles)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| LD50 | Dobson & Barnett (2008) | 59.1181877103869 | 59.1186543855778 | within 0.01 (printed rounding) | pass |
| LD50 | statsmodels GLM (binomial, logit) on log10 dose | 59.1181877103869 | 59.118167606485 | relative 1e-06 | pass |
| LD50 | R | 59.1181877103869 | 59.1181676064854 | relative 1e-06 | pass |

Note: The 2 parameter log-logistic curve with binomial errors is logistic regression on log dose, so its LD50 is the published fit's; the tolerance allows the printed 3 decimals of the fit.

### `fit_dose_response`

**the drawn ryegrass curve is drc's** (real data; data: ryegrass (drc))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | R | 301 | 301 | relative 1e-09 | pass |
| curve at the highest dose | R | 0.489464966412203 | 0.489464966412203 | relative 1e-09 | pass |
| curve at dose 0 | R | 7.79296184542426 | 7.79296184542426 | relative 1e-09 | pass |

### `table.find_best_power_of using=`

**Box and Cox's poisons: the power for the two-way model** (published; data: poisons (boot))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | Box & Cox (1964) | -0.750162301479909 | -0.75 | within 0.01 (printed rounding) | pass |
| simple power | Box & Cox (1964) | -1 | -1 | within 0 (printed rounding) | pass |
| power | R | -0.750162301479909 | -0.750162301479909 | relative 1e-06 | pass |
| 95 % CI low | R | -1.13693054535237 | -1.13693054535237 | relative 1e-06 | pass |
| simple power | R | -1 | -1 | relative 1e-06 | pass |

Note: Box and Cox print a power of about -0.75 and suggest the reciprocal (power -1), the rate of dying.

### `table.find_best_power_of`

**the power of the poisons survival times on their own** (real data; data: poisons (boot))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | SciPy stats.boxcox(alpha=0.05) | -0.360158442078502 | -0.360158442078502 | relative 1e-09 | pass |
| 95 % CI low | SciPy stats.boxcox(alpha=0.05) | -0.961993862358217 | -0.961993862358217 | relative 1e-09 | pass |
| power | R | -0.360158442078502 | -0.360158410727371 | relative 0.0001 | pass |

Note: car::powerTransform maximises the same likelihood with another optimiser (to about 1e-5).

### `table.fit_curve of_kind="logistic growth"`

**Rat42: a logistic growth curve (NIST certified)** (published; data: NIST Rat42)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 72.4622374345916 | 72.462237576 | at least 6 digits (LRE 8.7) | pass |
| b2 | NIST certified | 2.61807684336174 | 2.6180768402 | at least 6 digits (LRE 8.9) | pass |
| b3 | NIST certified | 0.0673592003257281 | 0.067359200066 | at least 6 digits (LRE 8.4) | pass |
| residual sum of squares | NIST certified | 8.05652293381126 | 8.0565229338 | at least 6 digits (LRE 11.9) | pass |

Note: NIST writes the curve as b1 / (1 + exp(b2 - b3 x)): b1 is Asym, b2 is xmid / scal and b3 is 1 / scal of R's SSlogis.

### `table.fit_curve of_kind="rise to a limit"`

**Misra1a: a rise to a limit (NIST certified)** (published; data: NIST Misra1a)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 238.942128882798 | 238.94212918 | at least 6 digits (LRE 8.9) | pass |
| b2 | NIST certified | 0.000550156432601245 | 0.00055015643181 | at least 6 digits (LRE 8.8) | pass |
| residual sum of squares | NIST certified | 0.1245513889444 | 0.12455138894 | at least 6 digits (LRE 10.5) | pass |

Note: NIST writes the curve as b1 (1 - exp(-b2 x)): b1 is Asym and b2 is exp(lrc) of R's SSasympOrig.

**BoxBOD: a rise to a limit (NIST certified)** (published; data: NIST BoxBOD)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 213.809411675878 | 213.80940889 | at least 6 digits (LRE 7.9) | pass |
| b2 | NIST certified | 0.547237453159843 | 0.54723748542 | at least 6 digits (LRE 7.2) | pass |
| residual sum of squares | NIST certified | 1168.00887655557 | 1168.0088766 | at least 6 digits (LRE 10.4) | pass |

Note: NIST writes the curve as b1 (1 - exp(-b2 x)): b1 is Asym and b2 is exp(lrc) of R's SSasympOrig.

### `table.fit_curve`

**Filip: a polynomial of degree 10 whose powers are nearly in proportion (NIST certified)** (published; data: NIST Filip)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | -1467.48961422975 | -1467.4896142298 | at least 9 digits (LRE 13.5) | pass |
| b0 standard error | NIST certified | 298.08453099553 | 298.084530995537 | at least 9 digits (LRE 13.6) | pass |
| b1 | NIST certified | -2772.17959193334 | -2772.17959193342 | at least 9 digits (LRE 13.5) | pass |
| b1 standard error | NIST certified | 559.779865474937 | 559.77986547495 | at least 9 digits (LRE 13.6) | pass |
| b2 | NIST certified | -2316.37108160886 | -2316.37108160893 | at least 9 digits (LRE 13.5) | pass |
| b2 standard error | NIST certified | 466.477572127786 | 466.477572127796 | at least 9 digits (LRE 13.7) | pass |
| b3 | NIST certified | -1127.97394098368 | -1127.97394098372 | at least 9 digits (LRE 13.5) | pass |
| b3 standard error | NIST certified | 227.204274477746 | 227.204274477751 | at least 9 digits (LRE 13.7) | pass |
| b4 | NIST certified | -354.478233703337 | -354.478233703349 | at least 9 digits (LRE 13.5) | pass |
| b4 standard error | NIST certified | 71.6478660875912 | 71.6478660875927 | at least 9 digits (LRE 13.7) | pass |
| b5 | NIST certified | -75.1242017393732 | -75.1242017393757 | at least 9 digits (LRE 13.5) | pass |
| b5 standard error | NIST certified | 15.2897178747397 | 15.28971787474 | at least 9 digits (LRE 13.7) | pass |
| b6 | NIST certified | -10.8753180355339 | -10.8753180355343 | at least 9 digits (LRE 13.4) | pass |
| b6 standard error | NIST certified | 2.23691159816028 | 2.23691159816033 | at least 9 digits (LRE 13.7) | pass |
| b7 | NIST certified | -1.06221498588943 | -1.06221498588947 | at least 9 digits (LRE 13.4) | pass |
| b7 standard error | NIST certified | 0.221624321934223 | 0.221624321934227 | at least 9 digits (LRE 13.7) | pass |
| b8 | NIST certified | -0.0670191154593385 | -0.0670191154593408 | at least 9 digits (LRE 13.5) | pass |
| b8 standard error | NIST certified | 0.0142363763154721 | 0.0142363763154724 | at least 9 digits (LRE 13.7) | pass |
| b9 | NIST certified | -0.0024678107827547 | -0.00246781078275479 | at least 9 digits (LRE 13.4) | pass |
| b9 standard error | NIST certified | 0.00053561740888981 | 0.000535617408889821 | at least 9 digits (LRE 13.7) | pass |
| b10 | NIST certified | -4.02962525080388e-05 | -4.02962525080404e-05 | at least 9 digits (LRE 13.4) | pass |
| b10 standard error | NIST certified | 8.96632837373851e-06 | 8.96632837373868e-06 | at least 9 digits (LRE 13.7) | pass |

Note: The hardest NIST linear problem (condition number of the powers 1.8e15). simplydata fits on x mapped onto [-1, 1] and turns the answer back into the raw powers with statsmodels t_test(); a QR fit on the raw powers (simplydata 0.2.0) gave no standard errors for b5 to b10, and R lm() drops two terms.

**Wampler1: a polynomial of degree 5, points exactly on the curve (NIST certified)** (published; data: NIST Wampler1)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 0.999999998195563 | 1 | at least 9 digits (LRE 8.7) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b0 standard error | NIST certified | 1.17536756270587e-09 | 0 | at least 9 digits (LRE 8.9) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b1 | NIST certified | 1.00000000096043 | 1 | at least 9 digits (LRE 9.0) | pass |
| b1 standard error | NIST certified | 1.29071605473089e-09 | 0 | at least 9 digits (LRE 8.9) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b2 | NIST certified | 0.9999999997126 | 1 | at least 9 digits (LRE 9.5) | pass |
| b2 standard error | NIST certified | 4.2559305313212e-10 | 0 | at least 9 digits (LRE 9.4) | pass |
| b3 | NIST certified | 1.00000000003502 | 1 | at least 9 digits (LRE 10.5) | pass |
| b3 standard error | NIST certified | 5.5414935427256e-11 | 0 | at least 9 digits (LRE 10.3) | pass |
| b4 | NIST certified | 0.999999999998107 | 1 | at least 9 digits (LRE 11.7) | pass |
| b4 standard error | NIST certified | 3.0830510308914e-12 | 0 | at least 9 digits (LRE 11.5) | pass |
| b5 | NIST certified | 1.00000000000004 | 1 | at least 9 digits (LRE 13.4) | pass |
| b5 standard error | NIST certified | 6.13396741656262e-14 | 0 | at least 9 digits (LRE 13.2) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler2: a polynomial of degree 5, points exactly on a curve with small coefficients (NIST certified)** (published; data: NIST Wampler2)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 0.999999999999975 | 1 | at least 9 digits (LRE 13.6) | pass |
| b0 standard error | NIST certified | 2.09772532092002e-14 | 0 | at least 9 digits (LRE 13.7) | pass |
| b1 | NIST certified | 0.100000000000016 | 0.1 | at least 9 digits (LRE 12.8) | pass |
| b1 standard error | NIST certified | 2.30359237062298e-14 | 0 | at least 9 digits (LRE 13.6) | pass |
| b2 | NIST certified | 0.00999999999999468 | 0.01 | at least 9 digits (LRE 12.3) | pass |
| b2 standard error | NIST certified | 7.5957287940429e-15 | 0 | at least 9 digits (LRE 14.1) | pass |
| b3 | NIST certified | 0.00100000000000068 | 0.001 | at least 9 digits (LRE 12.2) | pass |
| b3 standard error | NIST certified | 9.89012432292142e-16 | 0 | at least 9 digits (LRE 15.0) | pass |
| b4 | NIST certified | 9.99999999999629e-05 | 0.0001 | at least 9 digits (LRE 12.4) | pass |
| b4 standard error | NIST certified | 5.50244401700223e-17 | 0 | at least 9 digits (LRE 15.0) | pass |
| b5 | NIST certified | 1.00000000000007e-05 | 1e-05 | at least 9 digits (LRE 13.1) | pass |
| b5 standard error | NIST certified | 1.09475360522959e-18 | 0 | at least 9 digits (LRE 15.0) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler3: a polynomial of degree 5, with noise (NIST certified)** (published; data: NIST Wampler3)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 0.999999999825377 | 1 | at least 9 digits (LRE 9.8) | pass |
| b0 standard error | NIST certified | 2152.32624678175 | 2152.3262467817 | at least 9 digits (LRE 13.6) | pass |
| b1 | NIST certified | 1.00000000026193 | 1 | at least 9 digits (LRE 9.6) | pass |
| b1 standard error | NIST certified | 2363.55173469686 | 2363.55173469681 | at least 9 digits (LRE 13.6) | pass |
| b2 | NIST certified | 0.999999999843567 | 1 | at least 9 digits (LRE 9.8) | pass |
| b2 standard error | NIST certified | 779.343524331603 | 779.343524331583 | at least 9 digits (LRE 13.6) | pass |
| b3 | NIST certified | 1.00000000002319 | 1 | at least 9 digits (LRE 10.6) | pass |
| b3 standard error | NIST certified | 101.475507550352 | 101.47550755035 | at least 9 digits (LRE 13.6) | pass |
| b4 | NIST certified | 0.999999999998682 | 1 | at least 9 digits (LRE 11.9) | pass |
| b4 standard error | NIST certified | 5.64566512170767 | 5.64566512170752 | at least 9 digits (LRE 13.6) | pass |
| b5 | NIST certified | 1.00000000000003 | 1 | at least 9 digits (LRE 13.6) | pass |
| b5 standard error | NIST certified | 0.112324854679315 | 0.112324854679312 | at least 9 digits (LRE 13.6) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler4: a polynomial of degree 5, with large noise (NIST certified)** (published; data: NIST Wampler4)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 0.999999997729901 | 1 | at least 9 digits (LRE 8.6) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b0 standard error | NIST certified | 215232.624678169 | 215232.62467817 | at least 9 digits (LRE 14.6) | pass |
| b1 | NIST certified | 1.00000000162981 | 1 | at least 9 digits (LRE 8.8) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b1 standard error | NIST certified | 236355.173469681 | 236355.173469681 | at least 9 digits (LRE 14.7) | pass |
| b2 | NIST certified | 0.999999999457941 | 1 | at least 9 digits (LRE 9.3) | pass |
| b2 standard error | NIST certified | 77934.3524331584 | 77934.3524331583 | at least 9 digits (LRE 15.0) | pass |
| b3 | NIST certified | 1.00000000007071 | 1 | at least 9 digits (LRE 10.2) | pass |
| b3 standard error | NIST certified | 10147.550755035 | 10147.550755035 | at least 9 digits (LRE 14.6) | pass |
| b4 | NIST certified | 0.999999999996129 | 1 | at least 9 digits (LRE 11.4) | pass |
| b4 standard error | NIST certified | 564.566512170752 | 564.566512170752 | at least 9 digits (LRE 15.0) | pass |
| b5 | NIST certified | 1.00000000000008 | 1 | at least 9 digits (LRE 13.1) | pass |
| b5 standard error | NIST certified | 11.2324854679312 | 11.2324854679312 | at least 9 digits (LRE 15.0) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler5: a polynomial of degree 5, with noise far larger than the curve (NIST certified)** (published; data: NIST Wampler5)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 0.999999973806553 | 1 | at least 9 digits (LRE 7.6) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b0 standard error | NIST certified | 21523262.467817 | 21523262.467817 | at least 9 digits (LRE 15.0) | pass |
| b1 | NIST certified | 1.00000008297502 | 1 | at least 9 digits (LRE 7.1) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b1 standard error | NIST certified | 23635517.3469681 | 23635517.3469681 | at least 9 digits (LRE 14.7) | pass |
| b2 | NIST certified | 0.999999966697942 | 1 | at least 9 digits (LRE 7.5) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b2 standard error | NIST certified | 7793435.24331584 | 7793435.24331583 | at least 9 digits (LRE 15.0) | pass |
| b3 | NIST certified | 1.00000000457021 | 1 | at least 9 digits (LRE 8.3) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b3 standard error | NIST certified | 1014755.0755035 | 1014755.0755035 | at least 9 digits (LRE 14.6) | pass |
| b4 | NIST certified | 0.999999999745376 | 1 | at least 9 digits (LRE 9.6) | pass |
| b4 standard error | NIST certified | 56456.6512170752 | 56456.6512170752 | at least 9 digits (LRE 15.0) | pass |
| b5 | NIST certified | 1.00000000000496 | 1 | at least 9 digits (LRE 11.3) | pass |
| b5 standard error | NIST certified | 1123.24854679312 | 1123.24854679312 | at least 9 digits (LRE 15.0) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

### `table.fit_formula`

**Roszman1: a formula with arctan, from NIST's start 1 (NIST certified)** (published; data: NIST Roszman1)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 0.201968663359997 | 0.20196866396 | at least 6 digits (LRE 8.5) | pass |
| b2 | NIST certified | -6.19535143127122e-06 | -6.1953516256e-06 | at least 6 digits (LRE 7.5) | pass |
| b3 | NIST certified | 1204.45567009957 | 1204.4556708 | at least 6 digits (LRE 9.2) | pass |
| b4 | NIST certified | -181.342697724813 | -181.34269537 | at least 6 digits (LRE 7.9) | pass |
| residual sum of squares | NIST certified | 0.000494848473309689 | 0.00049484847331 | at least 6 digits (LRE 12.2) | pass |

Note: arctan is NumPy's arctan in the formula reader.

**Puromycin (treated): Vm and K of the Michaelis-Menten formula** (published; data: Puromycin (treated))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Vm | Bates & Watts (1988) | 212.683742080229 | 212.7 | within 0.05 (printed rounding) | pass |
| K | Bates & Watts (1988) | 0.0641212799902884 | 0.06412 | within 5e-06 (printed rounding) | pass |
| Vm | SciPy curve_fit (Levenberg-Marquardt) | 212.683742080229 | 212.683742080229 | relative 1e-07 | pass |
| K | SciPy curve_fit (Levenberg-Marquardt) | 0.0641212799902884 | 0.0641212799902884 | relative 1e-07 | pass |
| standard error of K | SciPy curve_fit (Levenberg-Marquardt) | 0.00828094786209176 | 0.00828094786209176 | relative 1e-07 | pass |
| Vm | R | 212.683742080229 | 212.683743233544 | relative 1e-06 | pass |
| K | R | 0.0641212799902884 | 0.0641212817850238 | relative 1e-06 | pass |
| standard error of K | R | 0.00828094786209176 | 0.00828094957102507 | relative 1e-06 | pass |

### `table.fit_curve of_kind="michaelis-menten"`

**Puromycin (treated): a Michaelis-Menten curve** (published; data: Puromycin (treated))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Vm | Bates & Watts (1988) | 212.683742750122 | 212.7 | within 0.05 (printed rounding) | pass |
| K | Bates & Watts (1988) | 0.0641212810909031 | 0.06412 | within 5e-06 (printed rounding) | pass |
| Vm | R | 212.683742750122 | 212.683707477025 | relative 1e-05 | pass |
| K | R | 0.0641212810909031 | 0.0641212261151318 | relative 1e-05 | pass |

Note: R nls() stops at a relative offset of 1e-5, so it agrees to about 1e-5.

### `table.fit_line test_method="standardised major axis"`

**leaf lifespan against leaf mass per area: standardised major axis (log10)** (real data; data: leaflife (smatr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.31503061916202 | 1.31503061916202 | relative 1e-09 | pass |
| intercept | R | -2.69880047584921 | -2.69880047584921 | relative 1e-09 | pass |
| slope 95 % CI low | R | 1.09626126001275 | 1.09626126001275 | relative 1e-09 | pass |

Note: Warton et al. (2006) fit these data on log scales; the slope is about 1.3.

### `table.fit_line test_method="deming", y_error_over_x_error=`

**creatinine in plasma against serum: Deming line with y_error_over_x_error=4** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.01786319565374 | 1.01786319565374 | relative 1e-09 | pass |
| slope standard error | R | 0.0341143809499105 | 0.0341143809499105 | relative 1e-09 | pass |

Note: mcr's error.ratio is the error variance of x over that of y, so 4 here is 1 / 4 there. tests/test_s3a2_lines.py checks the direction against R deming::deming(xstd =, ystd =) too.

### `table.fit_line test_method="passing-bablok"`

**creatinine in plasma against serum: Passing-Bablok line** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.08800890272179 | 1.08800890272179 | relative 1e-09 | pass |
| intercept | R | -0.11717286443298 | -0.11717286443298 | relative 1e-09 | pass |
| slope 95 % CI high | R | 1.17300462437155 | 1.17300462437155 | relative 1e-09 | pass |

### `table.fit_line test_method="theil-sen"`

**Anscombe's set 3 (one outlier): the Theil-Sen line** (real data; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | SciPy stats.theilslopes | 0.345555555555556 | 0.345555555555556 | relative 1e-12 | pass |
| intercept | SciPy stats.theilslopes | 4 | 4 | relative 1e-12 | pass |
| slope 95 % CI low | SciPy stats.theilslopes | 0.345 | 0.345 | relative 1e-12 | pass |
| slope | R | 0.345555555555556 | 0.345555555555556 | relative 1e-09 | pass |

Note: The outlier pulls the least-squares slope to 0.500; the Theil-Sen slope stays near 0.345, the slope of the other ten points.

### `table.fit_line with_bends=`

**Bacon and Watts's stagnant band: a line with one bend** (real data; data: stagnant (segmented))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bend 1 | R | 0.0411057838717026 | 0.0411057838717026 | relative 1e-09 | pass |
| slope 1 | R | -0.422076814198344 | -0.422076814198344 | relative 1e-09 | pass |
| slope 2 | R | -1.02056754472769 | -1.02056754472769 | relative 1e-09 | pass |
| Davies p-value | R | 1.2908801233492e-17 | 1.2908801233492e-17 | relative 1e-09 | pass |

Note: Bacon and Watts fit a smooth transition; segmented fits the sharp bend, so R is the reference.

### `table.fit_line changes_at=`

**drivers killed or seriously injured: the line changes at the seat-belt law** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| level change | statsmodels OLS with the two change columns | -457.768100628469 | -457.768100628469 | relative 1e-09 | pass |
| slope change | statsmodels OLS with the two change columns | 19.2016179865778 | 19.2016179865778 | relative 1e-09 | pass |
| level change standard error | statsmodels OLS with the two change columns | 107.180651134372 | 107.180651134372 | relative 1e-09 | pass |
| level change | R | -457.768100628469 | -457.768100628469 | relative 1e-09 | pass |
| slope change | R | 19.2016179865778 | 19.2016179865777 | relative 1e-09 | pass |
| level change standard error | R | 107.180651134372 | 107.180651134372 | relative 1e-09 | pass |

Note: A plain interrupted time series without the season, to check the arithmetic; Harvey and Durbin model the season and the trend too.

### `table.explain changes_at=`

**drivers killed (counts): the rate ratio of the jump at the seat-belt law** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| jump | statsmodels GLM (Poisson) with the two change columns | 0.724689274189852 | 0.724689274189851 | relative 1e-07 | pass |
| slope change | statsmodels GLM (Poisson) with the two change columns | 1.0154100777643 | 1.0154100777643 | relative 1e-07 | pass |
| jump | R | 0.724689274189852 | 0.724689274189851 | relative 1e-07 | pass |
| slope change | R | 1.0154100777643 | 1.0154100777643 | relative 1e-07 | pass |

### `table.explain for_percentile=`

**Engel's food expenditure: the 90th percentile line** (real data; data: Engel food expenditure)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| intercept | statsmodels QuantReg (estimates only: its standard errors are not R's) | 67.3508720801297 | 67.3508508860644 | relative 1e-05 | pass |
| income | statsmodels QuantReg (estimates only: its standard errors are not R's) | 0.686299480371905 | 0.686299496750445 | relative 1e-05 | pass |
| intercept | R | 67.3508720801297 | 67.3508720801297 | relative 1e-09 | pass |
| income | R | 0.686299480371905 | 0.686299480371905 | relative 1e-09 | pass |
| income standard error | R | 0.0284907223757292 | 0.0284907223757292 | relative 1e-09 | pass |

Note: statsmodels solves by iteratively reweighted least squares and R quantreg by the exact simplex; the lines agree to about 1e-7.

### `draw_smooth_line test_method="loess", with_confidence_band=`

**the drawn loess curve of drivers killed or seriously injured is R's** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | R | 200 | 200 | relative 1e-09 | pass |
| curve at the first month | R | 1644.03914048406 | 1644.03914048406 | relative 1e-09 | pass |
| curve at the last month | R | 1323.4857369989 | 1323.4857369989 | relative 1e-09 | pass |

### `table.add_smoothed_column test_method="loess", interval=`

**drivers killed or seriously injured, smoothed by loess with its band** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | R | 1644.03914048406 | 1644.03914048406 | relative 1e-09 | pass |
| last | R | 1323.4857369989 | 1323.4857369989 | relative 1e-09 | pass |
| first band low | R | 1511.97714881285 | 1511.97714881285 | relative 1e-09 | pass |

### `table.explain spread_changes_with=`

**spread_changes_with=: the spread of the ultrafiltration rate grows with pressure (varPower)** (real data; data: Dialyzer (nlme))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 19.6065136226626 | 19.6065136226626 | relative 1e-05 | pass |
| standard error | R | 0.926865072914266 | 0.926865072914266 | relative 1e-05 | pass |
| power | R | 0.290039657383882 | 0.290039657383882 | relative 1e-05 | pass |

Note: R nlme::gls() is the reference: statsmodels has no variance functions. nlme's optimiser stops at its own tolerance, so the numbers agree to about 1e-6.

**spread_changes_with=: a spread of its own for each blood flow rate (varIdent), with its interval** (real data; data: Dialyzer (nlme))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| ratio | R | 0.92353520930555 | 0.92353520930555 | relative 1e-05 | pass |
| ratio low | R | 0.679167845136216 | 0.679167845136216 | relative 1e-05 | pass |
| ratio high | R | 1.2558269490158 | 1.2558269490158 | relative 1e-05 | pass |

### `table.explain neighbours_alike_in_order_of=`

**neighbours_alike_in_order_of=: the level of Lake Huron, a linear trend with AR(1) errors** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| trend | R | -0.0194345899644702 | -0.0194345899644702 | relative 1e-05 | pass |
| standard error | R | 0.0126641385380824 | 0.0126641385380824 | relative 1e-05 | pass |
| phi | R | 0.824767413181072 | 0.824767413181072 | relative 1e-05 | pass |

### `table.find_columns_that_predict`

**lasso: which social measures predict fertility (1888)** (real data; data: swiss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Education | R | -0.546450922371341 | -0.546450922371341 | relative 1e-09 | pass |
| Infant.Mortality | R | 0.888743058811173 | 0.888743058811173 | relative 1e-09 | pass |
| penalty | R | 1.53712315186009 | 1.53712315186009 | relative 1e-09 | pass |

Note: R glmnet with the same seed is the reference (the random split is made in R). No published lasso fit of these data is used: a cross-validated penalty depends on the random split. The tests also check the effects against statsmodels' elastic net at the same penalty (to about 0.5 %, glmnet's convergence threshold).

### `table.compare_models using=[[...], [...]]`

**using=[[...], ...]: three models of fertility, AICc and Akaike weights** (real data; data: swiss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| AICc of Fertility ~ Education | statsmodels OLS and eval_measures.aicc | 348.980436348024 | 348.980436348024 | relative 1e-09 | pass |
| weight of the biggest | statsmodels OLS and eval_measures.aicc | 0.985031863347791 | 0.985031863347791 | relative 1e-09 | pass |
| AICc of Fertility ~ Education | R | 348.980436348024 | 348.980436348024 | relative 1e-09 | pass |
| weight of the biggest | R | 0.985031863347791 | 0.98503186334779 | relative 1e-09 | pass |

### `table.compare_models check_on_left_out_rows=True`

**check_on_left_out_rows=True: low birth weight from age, weight and smoking (Brier score in 10 parts)** (real data; data: birthwt (MASS))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| left out | R | 0.212566042141893 | 0.212566042141893 | relative 1e-10 | pass |
| bias-corrected | R | 0.212082848900463 | 0.212082848900463 | relative 1e-10 | pass |

Note: R boot::cv.glm with the same seed is the reference: the split is made by R's own random numbers.

### `table.check_model_of`

**Breusch-Pagan and White tests of the NIST Norris line** (real data; data: NIST Norris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Breusch-Pagan | statsmodels het_breuschpagan, het_white | 7.4268883603388 | 7.42688836034022 | relative 1e-09 | pass |
| Breusch-Pagan p | statsmodels het_breuschpagan, het_white | 0.00642563574987153 | 0.00642563574986645 | relative 1e-09 | pass |
| White | statsmodels het_breuschpagan, het_white | 7.95553731022935 | 7.95553731023029 | relative 1e-09 | pass |
| Breusch-Pagan | R | 7.4268883603388 | 7.42688836033886 | relative 1e-08 | pass |
| Breusch-Pagan p | R | 0.00642563574987153 | 0.00642563574987129 | relative 1e-08 | pass |
| White | R | 7.95553731022935 | 7.95553731022924 | relative 1e-08 | pass |

### `table.check_model_of outcome="yes or no"`

**outcome="yes or no": Hosmer-Lemeshow test and Brier score, low birth weight** (real data; data: birthwt (MASS))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Hosmer-Lemeshow | R | 7.22544929206198 | 7.22544929206198 | relative 1e-06 | pass |
| Hosmer-Lemeshow p | R | 0.512515395932265 | 0.512515395932265 | relative 1e-06 | pass |
| Brier | R | 0.202650010245525 | 0.202650010245525 | relative 1e-06 | pass |

### `table.find_model_averages_of comparing="each with the first"`

**comparing="each with the first": each tension against the low one** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| M minus L | R | -10 | -10 | relative 1e-06 | pass |
| H minus L | R | -14.7222222222222 | -14.7222222222222 | relative 1e-06 | pass |
| p H minus L | R | 0.000383446958904465 | 0.000383446958904465 | relative 1e-06 | pass |

Note: R emmeans is the reference. Dunnett's p-values (dunnettx) come from a close approximation of the multivariate t, so they agree to about 1e-6.

### `table.find_model_averages_of within_each_group_in=`

**within_each_group_in=: the interaction test and tension within each wool** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| interaction F | R | 4.189 | 4.189 | relative 1e-09 | pass |
| tension within A | R | 10.312 | 10.312 | relative 1e-09 | pass |

### `table.find_model_averages_of over_range_of=`

**over_range_of=: model fertility across education** (real data; data: swiss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | R | 78.0090728159598 | 78.0090728159598 | relative 1e-10 | pass |
| last | R | 37.0159513613633 | 37.0159513613633 | relative 1e-10 | pass |
| last high | R | 48.2361540762589 | 48.2361540762589 | relative 1e-10 | pass |

### `draw_interaction_lines`

**the averages of warp breaks for each wool at each tension** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| A at L | pandas mean, SciPy t.interval | 44.5555555555556 | 44.5555555555556 | relative 1e-09 | pass |
| B at H | pandas mean, SciPy t.interval | 18.7777777777778 | 18.7777777777778 | relative 1e-09 | pass |
| A at L, interval low | pandas mean, SciPy t.interval | 30.6444099497916 | 30.6444099497916 | relative 1e-09 | pass |
| A at L | R | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| B at H | R | 18.7777777777778 | 18.7777777777778 | relative 1e-12 | pass |
| A at L, interval low | R | 30.6444099497916 | 30.6444099497916 | relative 1e-12 | pass |

### `table.find_group_levels_of`

**each driver's own starting reaction time and slope over days** (real data; data: sleepstudy (lme4))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| level of 308 | R | 2.25855094990116 | 2.25855094990116 | relative 1e-06 | pass |
| slope of 308 | R | 9.1989757655659 | 9.1989757655659 | relative 1e-06 | pass |
| own slope of 308 | R | 19.6662617251619 | 19.6662617251619 | relative 1e-06 | pass |

### `table.compare_averages_of grouped_by=`

**grouped_by=: nested ANOVA of liver glycogen, rats inside treatments** (published; data: rat liver glycogen)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| F | Sokal & Rohlf (1981), Box 10.1 | 2.92895946510655 | 2.929 | within 0.0005 (printed rounding) | pass |
| treatment SS | Sokal & Rohlf (1981), Box 10.1 | 1557.55555555556 | 1557.56 | within 0.005 (printed rounding) | pass |
| rats SS | Sokal & Rohlf (1981), Box 10.1 | 797.666666666671 | 797.67 | within 0.005 (printed rounding) | pass |
| F | R | 2.92895946510655 | 2.92895946510655 | relative 1e-10 | pass |
| treatment SS | R | 1557.55555555556 | 1557.55555555556 | relative 1e-10 | pass |
| rats SS | R | 797.666666666671 | 797.666666666671 | relative 1e-10 | pass |

Note: The book's three-level table (rats, preparations, readings) tests treatments against rats with the same F as the two-level table here, because the design is balanced.

### `table.compare_averages_of for_each_group_in= with a list of columns`

**a list of columns: MANOVA of sepal and petal length across species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Pillai | statsmodels MANOVA | 0.988500527043341 | 0.988500527043341 | relative 1e-09 | pass |
| F | statsmodels MANOVA | 71.8287954469342 | 71.8287954469342 | relative 1e-09 | pass |
| Wilks | statsmodels MANOVA | 0.0398783132489484 | 0.0398783132489484 | relative 1e-09 | pass |
| Pillai | R | 0.988500527043341 | 0.988500527043341 | relative 1e-10 | pass |
| F | R | 71.8287954469342 | 71.8287954469341 | relative 1e-10 | pass |
| Wilks | R | 0.0398783132489484 | 0.0398783132489471 | relative 1e-10 | pass |

### `table.add_time_and_event_columns`

**person-years and deaths in the UDCA trial, from its dates** (real data; data: udca (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| person-years | R | 557.664613278576 | 557.664613278576 | relative 1e-12 | pass |
| deaths | R | 11 | 11 | relative 1e-12 | pass |
| rows | R | 170 | 170 | relative 1e-12 | pass |

Note: Base R date arithmetic (difftime) with a year of 365.25 days, as R Epi cal.yr() and Stata stset scale(365.25). A death after the last follow-up date counts as no event.

### `table.find_risk_over_time`

**the chance of a plasma cell malignancy by 10 years, death competing (women)** (real data; data: mgus2 (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| risk by 120 months | statsmodels CumIncidenceRight | 0.0738856643759262 | 0.0738856643759262 | relative 1e-09 | pass |
| risk by 120 months | R | 0.0738856643759262 | 0.0738856643759262 | relative 1e-09 | pass |
| low | R | 0.0555247328325098 | 0.0555247328325098 | relative 1e-09 | pass |

### `draw_risk_curves`

**the chance of death over time in the NCCTG lung cancer trial (women): 1 minus Kaplan-Meier** (real data; data: lung (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| risk at the 11th step | R | 0.134830680747682 | 0.134830680747682 | relative 1e-12 | pass |
| risk at the end | R | 0.916785556486642 | 0.916785556486642 | relative 1e-12 | pass |

### `draw_risk_curves competing_with=`

**competing_with=: the drawn risk of a plasma cell malignancy is R's Aalen-Johansen estimate** (real data; data: mgus2 (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| risk at the 51st time | R | 0.0289632492410418 | 0.0289632492410418 | relative 1e-09 | pass |
| time of the 51st step | R | 51 | 51 | relative 1e-09 | pass |

### `table.find_survival_over_time at_time_points=`

**at_time_points=: survival at 180 and 365 days in the NCCTG lung cancer trial** (real data; data: lung (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| female at 180 | statsmodels SurvfuncRight | 0.842401705587783 | 0.842401705587783 | relative 1e-12 | pass |
| female at 365 | statsmodels SurvfuncRight | 0.526463030185906 | 0.526463030185906 | relative 1e-12 | pass |
| male at 365 | statsmodels SurvfuncRight | 0.336087834639378 | 0.336087834639378 | relative 1e-12 | pass |
| female at 180 | R | 0.842401705587783 | 0.842401705587783 | relative 1e-09 | pass |
| female at 365 | R | 0.526463030185906 | 0.526463030185906 | relative 1e-09 | pass |
| male at 365 | R | 0.336087834639378 | 0.336087834639379 | relative 1e-09 | pass |
| male at 365, low | R | 0.260900503789725 | 0.260900503789725 | relative 1e-09 | pass |

### `table.find_survival_over_time test_method="life table"`

**test_method="life table": the actuarial life table of breast feeding (Klein & Moeschberger section 5.4)** (real data; data: bfeed (KMsurv))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| survival at 7 weeks | R | 0.627647159449448 | 0.627647159449448 | relative 1e-12 | pass |
| effective at risk | R | 561.5 | 561.5 | relative 1e-12 | pass |
| hazard | R | 0.0537475345167653 | 0.0537475345167653 | relative 1e-12 | pass |

Note: The intervals of the K&M example; lifetab gets the counts simplydata makes from the rows.

### `table.find_survival_over_time allowing_for=`

**allowing_for=: survival at one year by sex, adjusted for age and ECOG score (direct adjustment)** (real data; data: lung (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| female | R | 0.524876838929801 | 0.524876838929801 | relative 1e-09 | pass |
| male | R | 0.33744610511966 | 0.33744610511966 | relative 1e-09 | pass |

Note: adjustedCurves' own default is conf_int = FALSE; simplydata asks for the intervals.

### `table.find_survival_over_time followed_from=`

**followed_from=: survival to age 80 of Channing House residents who entered at different ages (delayed entry)** (real data; data: Channing House (KMsurv))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| survival at 960 months | statsmodels SurvfuncRight(entry=) | 0.565869628031309 | 0.565869628031309 | relative 1e-12 | pass |
| survival at 960 months | R | 0.565869628031309 | 0.565869628031309 | relative 1e-09 | pass |
| at risk | R | 193 | 193 | relative 1e-09 | pass |

### `table.find_survival_over_time average_time_up_to=`

**average_time_up_to=: the average days alive in the first year, by sex** (real data; data: lung (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| male | R | 241.495085192057 | 241.495085192057 | relative 1e-09 | pass |
| male standard error | R | 10.3582264910969 | 10.3582264910969 | relative 1e-09 | pass |

Note: survRM2::rmst2 gives the same per-group values (241.495, se 10.358 for men).

### `table.compare_survival allowing_for=`

**allowing_for=: chemotherapy compared within each cell type (stratified log-rank)** (real data; data: veteran (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | statsmodels survdiff(strata=) | 0.701743346844315 | 0.701743346844315 | relative 1e-12 | pass |
| p | statsmodels survdiff(strata=) | 0.402198523780676 | 0.402198523780676 | relative 1e-12 | pass |
| chi-square | R | 0.701743346844315 | 0.701743346844319 | relative 1e-09 | pass |
| p | R | 0.402198523780676 | 0.402198523780674 | relative 1e-09 | pass |

### `table.compare_survival followed_from=`

**followed_from=: women and men of Channing House, followed from their age on entry** (real data; data: Channing House (KMsurv))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | statsmodels survdiff(entry=) | 3.37646071064618 | 3.37646071064618 | relative 1e-12 | pass |
| chi-square | R | 3.37646071064618 | 3.37646071064618 | relative 1e-09 | pass |

Note: R survdiff takes no start times. The log-rank test with delayed entry is the score test of a Cox model with exact ties, coxph(..., ties = "exact") (3.376460710701 against statsmodels' 3.376460710646); with Breslow ties the score test differs by 0.7 % (3.354), so the exact one is the check, to 1e-9. summary() of an exact-ties fit has no score test, so it is read from coxph()$score.

### `table.compare_survival average_time_up_to=`

**average_time_up_to=: the difference in average days alive in the first year, men minus women** (real data; data: lung (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| difference | R | -55.9703243399798 | -55.9703243399798 | relative 1e-09 | pass |
| low | R | -85.2877123026282 | -85.2877123026282 | relative 1e-09 | pass |
| p | R | 0.000182706461311161 | 0.000182706461311161 | relative 1e-09 | pass |

### `table.compare_survival competing_with=`

**competing_with=: Gray's test of a plasma cell malignancy between women and men, death competing** (real data; data: mgus2 (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | R | 1.19450782507551 | 1.19450782507551 | relative 1e-09 | pass |
| p | R | 0.274422156788004 | 0.274422156788004 | relative 1e-09 | pass |

### `table.explain_survival allowing_for=`

**allowing_for=: chemotherapy and Karnofsky score, each cell type with its own baseline (stratified Cox)** (real data; data: veteran (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| test vs standard | statsmodels PHReg(strata=) | 0.232834676889496 | 0.232834676889496 | relative 1e-06 | pass |
| karno | statsmodels PHReg(strata=) | -0.0358011230001631 | -0.0358011230001631 | relative 1e-06 | pass |
| test vs standard | R | 0.232834676889496 | 0.232834676889496 | relative 1e-06 | pass |
| karno | R | -0.0358011230001631 | -0.0358011230001631 | relative 1e-06 | pass |

### `table.explain_survival followed_from=`

**followed_from=: the Stanford heart transplant, start-stop rows split at the transplant** (real data; data: Stanford heart transplant (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| age | R | 0.0305363149141719 | 0.0305363149141719 | relative 1e-06 | pass |
| surgery | R | -0.773327645300476 | -0.773327645300476 | relative 1e-06 | pass |
| transplant | R | 0.0160956052965236 | 0.0160956052965236 | relative 1e-06 | pass |

Note: 36 rows start at a death time (each patient's second row starts at the transplant). R does not count such a row as at risk at that death, statsmodels PHReg(entry=) does (the patient would count twice), so simplydata fits these data with R coxph and says so.

### `table.explain_survival competing_with=`

**competing_with=: cause-specific hazard ratios of a plasma cell malignancy, death counted as the end of follow-up** (real data; data: mgus2 (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| age | statsmodels PHReg | 0.0130385698370914 | 0.0130385698370915 | relative 1e-06 | pass |
| men vs women | statsmodels PHReg | -0.0251377892665885 | -0.0251377892665887 | relative 1e-06 | pass |
| age | R | 0.0130385698370914 | 0.0130385698249726 | relative 1e-06 | pass |
| men vs women | R | -0.0251377892665885 | -0.025137789294278 | relative 1e-06 | pass |

### `table.explain_survival test_method="fine-gray"`

**test_method="fine-gray": subdistribution hazard ratios of a plasma cell malignancy, death competing** (real data; data: mgus2 (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| age | R | -0.0173381534946792 | -0.0173381534946792 | relative 1e-07 | pass |
| men vs women | R | -0.260038237884128 | -0.260038237884128 | relative 1e-07 | pass |

Note: survival::finegray() with a weighted coxph agrees to about 3 digits (-0.0173, -0.2598), the check recorded in tests/test_s3b3_survival.py.

### `table.explain_survival distribution=`

**distribution=: a Weibull model of larynx cancer by stage and age (time ratios)** (real data; data: larynx (KMsurv))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| stage 4 | R | -1.54407608393946 | -1.54407608393946 | relative 1e-06 | pass |
| age | R | -0.0174636707215005 | -0.0174636707215005 | relative 1e-06 | pass |

### `draw_survival_curves followed_from=`

**followed_from=: the drawn curve of Channing House is the delayed-entry Kaplan-Meier curve** (real data; data: Channing House (KMsurv))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| survival at the 41st death time | R | 0.583568706215935 | 0.583568706215935 | relative 1e-09 | pass |

### `draw_survival_curves allowing_for=`

**allowing_for=: the drawn curves by sex are adjusted for age and ECOG score** (real data; data: lung (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| female, 21st point | R | 0.9121266265218 | 0.9121266265218 | relative 1e-09 | pass |

### `table.combine_studies`

**BCG trials: risk ratios, random effects (REML) with Hartung-Knapp** (published; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| log estimate | Viechtbauer (2010), JSS 36(3) | -0.714532342158168 | -0.7145 | within 5e-05 (printed rounding) | pass |
| tau squared | Viechtbauer (2010), JSS 36(3) | 0.313243258136794 | 0.3132 | within 5e-05 (printed rounding) | pass |
| I squared % | Viechtbauer (2010), JSS 36(3) | 92.2213845212761 | 92.22 | within 0.005 (printed rounding) | pass |
| Q | Viechtbauer (2010), JSS 36(3) | 152.233008082373 | 152.233 | within 5e-05 (printed rounding) | pass |
| estimate | R | 0.489420939826016 | 0.48942093982603 | relative 1e-08 | pass |
| low | R | 0.330072248483585 | 0.330072248483599 | relative 1e-08 | pass |
| high | R | 0.725698259822328 | 0.725698259822339 | relative 1e-08 | pass |
| p-value | R | 0.00192001509605724 | 0.00192001509605729 | relative 1e-08 | pass |
| tau squared | R | 0.313243258136794 | 0.313243258136486 | relative 1e-08 | pass |
| I squared % | R | 92.2213845212761 | 92.2213845212691 | relative 1e-08 | pass |
| Q | R | 152.233008082373 | 152.233008082373 | relative 1e-08 | pass |

Note: The published numbers are the estimate, tau-squared, I-squared and Q, which Hartung-Knapp does not change; its interval is checked against R metafor itself.

**BCG trials: Peters' test of small-study effects (risk ratios from counts)** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| t | R | -1.27018944288669 | -1.27018944288669 | relative 1e-06 | pass |
| p-value | R | 0.230226874722668 | 0.230226874722668 | relative 1e-06 | pass |

Note: R meta's Peters test (Peters et al. 2006), a second package: simplydata runs metafor::regtest() with Peters' weights and 1 / n as the predictor.

**passive smoking: Egger's test and trim and fill** (real data; data: passive smoking (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| t | R | 2.38241441660256 | 2.38241441660256 | relative 1e-06 | pass |
| p-value | R | 0.0227641997034067 | 0.0227641997034067 | relative 1e-06 | pass |
| studies added | R | 7 | 7 | relative 1e-06 | pass |
| filled odds ratio | R | 1.19061633771497 | 1.1906163377131 | relative 1e-06 | pass |

Note: Egger's test from R meta (metabias, method "Egger"), a second package; trim and fill from metafor (estimator L0, side estimated).

### `table.combine_studies interval_by=`

**interval_by=: BCG trials, the normal (z) interval** (published; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| log low | Viechtbauer (2010), JSS 36(3) | -1.06689763881052 | -1.0669 | within 5e-05 (printed rounding) | pass |
| log high | Viechtbauer (2010), JSS 36(3) | -0.362167045505816 | -0.3622 | within 5e-05 (printed rounding) | pass |
| estimate | R | 0.489420939826016 | 0.48942093982603 | relative 1e-08 | pass |
| low | R | 0.344074306106718 | 0.344074306106776 | relative 1e-08 | pass |
| high | R | 0.696166066715505 | 0.696166066715427 | relative 1e-08 | pass |
| p-value | R | 7.05425810168428e-05 | 7.05425810164229e-05 | relative 1e-08 | pass |

### `table.combine_studies test_method=`

**test_method=: BCG trials, DerSimonian-Laird** (published; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| tau squared | Viechtbauer (2010), JSS 36(3) | 0.308760262862376 | 0.3088 | within 5e-05 (printed rounding) | pass |
| estimate | statsmodels combine_effects (DerSimonian-Laird) | 0.489624150463619 | 0.489624150463619 | relative 1e-08 | pass |
| low | statsmodels combine_effects (DerSimonian-Laird) | 0.344919135222476 | 0.344919135222476 | relative 1e-08 | pass |
| high | statsmodels combine_effects (DerSimonian-Laird) | 0.695037718225147 | 0.695037718225147 | relative 1e-08 | pass |
| estimate | R | 0.489624150463619 | 0.489624150463619 | relative 1e-08 | pass |
| low | R | 0.344919135222476 | 0.344919135222476 | relative 1e-08 | pass |
| high | R | 0.695037718225147 | 0.695037718225147 | relative 1e-08 | pass |
| p-value | R | 6.46292430470396e-05 | 6.46292430470396e-05 | relative 1e-08 | pass |
| tau squared | R | 0.308760262862376 | 0.308760262862376 | relative 1e-08 | pass |

Note: The study's log risk ratios are written out for statsmodels (the parent check), which has no escalc; simplydata itself takes them from R metafor.

**test_method=: BCG trials, Paule-Mandel** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 0.489207691105033 | 0.489207691104199 | relative 1e-08 | pass |
| low | R | 0.329856231622529 | 0.329856231621683 | relative 1e-08 | pass |
| high | R | 0.7255408329232 | 0.725540832922586 | relative 1e-08 | pass |
| p-value | R | 0.00191927183128081 | 0.001919271831278 | relative 1e-08 | pass |
| tau squared | R | 0.318068452185901 | 0.318068452205024 | relative 1e-08 | pass |

Note: Paule-Mandel is found by iteration. simplydata runs metafor to 1e-10 (its default, 1e-5, left tau squared 7.9e-5 short) and the reference to 1e-12, so they agree to 1e-8.

**test_method=: BCG trials, a common effect** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 0.650323619619482 | 0.650323619619482 | relative 1e-08 | pass |
| low | R | 0.600699026085764 | 0.600699026085764 | relative 1e-08 | pass |
| high | R | 0.704047770795957 | 0.704047770795957 | relative 1e-08 | pass |
| p-value | R | 2.2886293069732e-26 | 2.2886293069732e-26 | relative 1e-08 | pass |

### `table.combine_studies test_method="mantel-haenszel"`

**test_method="mantel-haenszel": BCG trials, risk ratios** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | statsmodels StratifiedTable (riskratio_pooled) | 0.635267185077769 | 0.635267185077769 | relative 1e-08 | pass |
| estimate | R | 0.635267185077769 | 0.635267185077769 | relative 1e-08 | pass |
| low | R | 0.588128729691417 | 0.588128729691417 | relative 1e-08 | pass |
| high | R | 0.686183782670126 | 0.686183782670126 | relative 1e-08 | pass |
| p-value | R | 8.91137967074168e-31 | 8.91137967074168e-31 | relative 1e-08 | pass |

### `table.combine_studies test_method="peto"`

**test_method="peto": BCG trials, odds ratios** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 0.622229482760703 | 0.622229482760703 | relative 1e-08 | pass |
| low | R | 0.574568103455868 | 0.574568103455868 | relative 1e-08 | pass |
| high | R | 0.673844452707929 | 0.673844452707929 | relative 1e-08 | pass |
| p-value | R | 1.83807338632167e-31 | 1.83807338632167e-31 | relative 1e-08 | pass |

### `table.combine_studies for_each_group_in=`

**for_each_group_in=: BCG trials by how people were allocated** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Q between | R | 1.86144494616318 | 1.86144494615464 | relative 1e-08 | pass |
| p between | R | 0.3942687588839 | 0.394268758885585 | relative 1e-08 | pass |
| random | R | 0.378717511421929 | 0.378717511421398 | relative 1e-08 | pass |
| random tau2 | R | 0.392528006891837 | 0.392528006900774 | relative 1e-08 | pass |

Note: Each subgroup has its own between-study variance; the test of their difference uses each subgroup's estimate with its normal (z) standard error, as RevMan and R meta do (the next case checks it against meta), not metafor's rma(mods = ~ alloc), which shares one variance.

**for_each_group_in=: BCG trials by allocation, against R meta's test of subgroup differences** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Q between | R | 1.86144494616318 | 1.8614461412312 | relative 0.0001 | pass |
| p between | R | 0.3942687588839 | 0.394268523294979 | relative 0.0001 | pass |

Note: R meta (each subgroup its own between-study variance, REML) is a second package; meta's REML stops at its own tolerance, so the numbers agree to about 1e-5.

### `table.combine_studies using=`

**using=: BCG trials, meta-regression on latitude** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | -0.029101725011181 | -0.0291017250116429 | relative 1e-08 | pass |
| low | R | -0.0471529230265922 | -0.0471529230250807 | relative 1e-08 | pass |
| p-value | R | 0.00456505154515336 | 0.0045650515415926 | relative 1e-08 | pass |

### `table.combine_studies estimates=`

**estimates=: passive smoking, odds ratios with their 95 % intervals** (published; data: passive smoking (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | Hackshaw et al. (1997), BMJ 315:980 | 1.23848509565452 | 1.24 | within 0.005 (printed rounding) | pass |
| low | Hackshaw et al. (1997), BMJ 315:980 | 1.12922353518157 | 1.13 | within 0.005 (printed rounding) | pass |
| high | Hackshaw et al. (1997), BMJ 315:980 | 1.35831860067612 | 1.36 | within 0.005 (printed rounding) | pass |
| estimate | R | 1.23848509565452 | 1.23848509565452 | relative 1e-08 | pass |
| low | R | 1.12922353518157 | 1.12922353518157 | relative 1e-08 | pass |
| high | R | 1.35831860067612 | 1.35831860067612 | relative 1e-08 | pass |

Note: The paper's excess risk of 24 % (95 % CI 13 % to 36 %) is the pooled odds ratio 1.24 (1.13 to 1.36).

### `table.combine_studies averages=`

**averages=: Normand 1999, standardised differences (Hedges' g)** (real data; data: Normand 1999 (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | -0.537108258432976 | -0.537108258432961 | relative 1e-08 | pass |
| low | R | -1.25032220906533 | -1.25032220906531 | relative 1e-08 | pass |
| first study | R | -0.355169640940107 | -0.355169640940107 | relative 1e-08 | pass |

Note: metafor's Hedges' g (exact correction, large-sample variance) is the reference; statsmodels' effectsize_smd uses an approximate correction and another variance, so it differs slightly.

### `table.combine_studies show="ratios of averages"`

**show="ratios of averages": Curtis 1998, the log response ratio of plant mass under raised CO2** (real data; data: Curtis 1998 (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 1.28912239792386 | 1.28912239791847 | relative 1e-06 | pass |
| tau squared | R | 0.0257701366505267 | 0.0257701366410135 | relative 1e-06 | pass |

### `table.combine_studies time=`

**time=: Hart 1999, rate ratios of stroke with warfarin** (real data; data: Hart 1999 (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 0.361745007398934 | 0.361745007398934 | relative 1e-08 | pass |
| low | R | 0.237639349238557 | 0.237639349238557 | relative 1e-08 | pass |
| high | R | 0.55066406635666 | 0.55066406635666 | relative 1e-08 | pass |

### `table.combine_studies correlations=`

**correlations=: McDaniel 1994, interview ratings and job performance** (real data; data: McDaniel 1994 (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 0.233032253056143 | 0.233032253056107 | relative 1e-08 | pass |
| low | R | 0.199562756261728 | 0.199562756261703 | relative 1e-08 | pass |

### `draw_funnel_plot`

**passive smoking: each study's odds ratio and standard error** (real data; data: passive smoking (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first odds ratio | R | 1.18 | 1.18 | relative 1e-08 | pass |
| first standard error | R | 0.137028776120449 | 0.137028776120449 | relative 1e-08 | pass |
| last standard error | R | 0.257719821942313 | 0.257719821942313 | relative 1e-08 | pass |

### `sdata.find_how_many_needed`

**two averages, a medium difference (d = 0.5), 80 % power** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| values per group (exact) | statsmodels TTestIndPower | 63.7657641232832 | 63.7657641232832 | relative 1e-09 | pass |
| values per group (exact) | R | 63.7657641232832 | 63.7657637142739 | relative 1e-06 | pass |

Note: The formula route of before S3b-2, checked against R power.t.test() (whose root search stops at about 6 digits).

### `sdata.find_chance_of_finding`

**two averages, d = 0.5, 30 values in each group** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | R | 0.477840985940913 | 0.477840985940939 | relative 1e-09 | pass |

### `sdata.find_how_many_needed using=`

**using=: rows for a model of 3 columns, f squared 0.15** (real data; data: pwr manual and vignette)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows (exact) | R | 76.705826557806 | 76.7058265599653 | relative 1e-06 | pass |
| rows | R | 77 | 77 | relative 1e-06 | pass |

### `sdata.find_how_many_needed based_on=`

**based_on=: Mann-Whitney, d = 0.5, the values needed by simulation** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| values per group | SciPy stats.power at 68 (the same seed) | 68 | 68 | relative 1e-12 | pass |
| power with that many | SciPy stats.power at 68 (the same seed) | 0.8099 | 0.8099 | relative 1e-12 | pass |

Note: SciPy with the same seed gives the same power at the number found; the t-test needs 64, and the Mann-Whitney test about 5 % more (asymptotic relative efficiency 0.955).

### `sdata.find_how_many_needed interval_width=`

**interval_width=: a 95 % Wilson interval of a percent near 15 % that is 5 points wide** (published; data: presize paper (JOSS))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| values (exact) | Haynes et al. (2021), JOSS | 783.489733552826 | 783.4897 | within 5e-05 (printed rounding) | pass |
| values | Haynes et al. (2021), JOSS | 784 | 784 | within 0 (printed rounding) | pass |
| values (exact) | R | 783.489733552826 | 783.489733552826 | relative 1e-09 | pass |
| values | R | 784 | 784 | relative 1e-09 | pass |

### `sdata.find_how_many_needed for_test=`

**for_test=: events for a hazard ratio of 0.5 (log-rank, Schoenfeld)** (published; data: Stata power manuals)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| events | Stata [PSS-2] power logrank, example 2 | 66 | 66 | within 0 (printed rounding) | pass |
| events (exact) | R | 65.3456592588709 | 65.3456592588709 | relative 1e-09 | pass |
| events | R | 66 | 66 | relative 1e-09 | pass |

**for_test=: events for survival 50 % against 60 % (hazard ratio log 0.5 / log 0.6 = 1.36), one-sided** (published; data: Stata power manuals)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| events | Stata [PSS-2] power logrank, example 5 (Machin et al. 2009, p. 91) | 266 | 266 | within 0 (printed rounding) | pass |
| events (exact) | R | 265.472189653188 | 265.472189653188 | relative 1e-09 | pass |
| events | R | 266 | 266 | relative 1e-09 | pass |

**for_test=: events and people for a hazard ratio of 0.7, 30 % and 40 % with the event** (real data; data: Stata power manuals)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| events (exact) | R | 246.787104547358 | 246.787104547358 | relative 1e-09 | pass |
| people in all | R | 706 | 706 | relative 1e-09 | pass |
| power with that many | R | 0.800338066556873 | 0.800338066556873 | relative 1e-09 | pass |

Note: No published example with people was found for a hazard ratio of 0.7; R gsDesign and powerSurvEpi are called directly.

### `sdata.find_how_many_needed test_method=`

**test_method=: Freedman's formula, hazard ratio 0.5, everyone followed to the event** (published; data: Stata power manuals)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| people per group | Stata [PSS-2] power logrank, example 1 | 36 | 36 | within 0 (printed rounding) | pass |
| people per group | R | 36 | 36 | relative 1e-09 | pass |

### `sdata.find_chance_of_finding using=`

**using=: power of the F test for 5 columns, R squared 0.10, 95 rows** (published; data: G*Power 3.1 manual)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | G*Power manual 13.3.1 (Cohen 1988, example 9.1) | 0.673585770818647 | 0.673586 | within 5e-07 (printed rounding) | pass |
| power | statsmodels FTestPowerF2 | 0.673585770818647 | 0.673585770818647 | relative 1e-12 | pass |
| power | R | 0.673585770818647 | 0.673585770914399 | relative 1e-09 | pass |

### `sdata.find_how_many_needed against=`

**against=: rows for 2 columns added to 1, R squared 0.3, significance 0.001** (published; data: pwr manual and vignette)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows (exact) | pwr vignette, pwr.f2.test (v = 49.88971) | 53.8897053377435 | 53.88971 | within 5e-05 (printed rounding) | pass |
| rows (exact) | R | 53.8897053377435 | 53.8897050419808 | relative 1e-06 | pass |

Note: The rows are pwr's v (the denominator degrees of freedom) plus the 3 columns of the bigger model plus 1; pwr's root search stops at about 6 digits.

### `sdata.find_how_many_needed outcome=`

**outcome=: logistic regression, odds ratio 1.5 per standard deviation, 50 % at the average, power 0.95** (published; data: G*Power 3.1 manual)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| values | G*Power manual 29.4 (Demidenko 2007 with variance correction) | 337 | 337 | within 0 (printed rounding) | pass |
| values (exact) | R | 336.86477920999 | 336.86477920999 | relative 1e-09 | pass |
| values | R | 337 | 337 | relative 1e-09 | pass |

Note: The G*Power manual prints 337 with the variance correction, 355 without it and 317 by Hsieh et al. (1998); simplydata uses the first, as G*Power does.

### `sdata.find_how_many_needed in_clusters_of=`

**in_clusters_of=: two averages in clusters of 20, ICC 0.025** (published; data: Stata power manuals)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| clusters per group | Stata [PSS-2] power twomeans, cluster, example 1 | 13 | 13 | within 0 (printed rounding) | pass |
| values in whole clusters | Stata [PSS-2] power twomeans, cluster, example 1 | 260 | 260 | within 0 (printed rounding) | pass |
| values per group (before rounding) | R | 259.160977758531 | 259.160977698409 | relative 1e-09 | pass |

Note: The same design (R power.t.test for independent values, times the design effect 1 + (m - 1) ICC of Donner & Klar 2000) worked out in R, so the two must agree to 1e-9; the published Stata answer is the independent check. (R epiR::epi.sscompc(design =) multiplies by the same design effect but starts from the normal (z) formula: 257.7 against 259.2 values per group, a different method, so it is no longer used as the reference.) This design effect is simplydata's own arithmetic, pending the owner's approval.

**in_clusters_of=: the design effect of clusters of 30 with ICC 0.05** (published; data: Bland, sample size in cluster trials)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| design effect | Bland, Sample size in guidelines trials | 2.45 | 2.45 | within 0.005 (printed rounding) | pass |

### `sdata.find_chance_of_finding based_on=`

**based_on=: Mann-Whitney power, d = 0.5, 64 values in each group, by simulation** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | SciPy stats.power (the same seed) | 0.7792 | 0.7792 | relative 1e-12 | pass |
| power | R | 0.7792 | 0.7843 | within 4 Monte Carlo SE (0.0233) | pass |

Note: R draws its own random numbers, so the difference may be 4 Monte Carlo standard errors of the difference of two simulated shares of 10000 studies each (sqrt(2 p (1 - p) / 10000), about 0.6 percentage points); SciPy with the same seed gives the same number exactly.

### `sdata.find_chance_of_finding drawing_from=`

**drawing_from=: Welch's t-test on two lognormal groups of 20, by simulation** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | SciPy stats.power (the same seed) | 0.2213 | 0.2213 | relative 1e-12 | pass |
| power | R | 0.2213 | 0.2182 | within 4 Monte Carlo SE (0.0234) | pass |

Note: SciPy with the same seed gives the same number exactly. R draws its own random numbers, so the difference may be 4 Monte Carlo standard errors of the difference of two simulated shares of 10000 studies each (at a power near 23 %, about 0.6 percentage points).

### `sdata.find_chance_of_finding by_running=`

**by_running=: logistic regression simulated with statsmodels, against R pwrss** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | the same 2000 studies (seeds 1 to 2000), counted directly | 0.6675 | 0.6675 | exact | pass |
| power | R | 0.6675 | 0.657955359447415 | within 4 Monte Carlo SE (0.0421) | pass |

Note: The same 2000 studies (seeds 1 to 2000) counted directly give the same share exactly. Against the formula of R pwrss (Demidenko's, an approximation with no Monte Carlo error) the difference may be 4 Monte Carlo standard errors of simplydata's share of 2000 studies (sqrt(p (1 - p) / 2000), about 1.1 percentage points).

### `table.add_diversity_columns`

**BCI: richness, Shannon and Simpson of the first three plots** (real data; data: BCI (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| richness plot 1 | R | 93 | 93 | relative 1e-12 | pass |
| richness plot 2 | R | 84 | 84 | relative 1e-12 | pass |
| richness plot 3 | R | 90 | 90 | relative 1e-12 | pass |
| Shannon plot 1 | R | 4.01841166223236 | 4.01841166223236 | relative 1e-12 | pass |
| Shannon plot 2 | R | 3.84847116819842 | 3.84847116819842 | relative 1e-12 | pass |
| Shannon plot 3 | R | 3.81405950494229 | 3.81405950494229 | relative 1e-12 | pass |
| Simpson plot 1 | R | 0.974629304846939 | 0.974629304846939 | relative 1e-12 | pass |
| Simpson plot 2 | R | 0.968339278636544 | 0.968339278636544 | relative 1e-12 | pass |
| Simpson plot 3 | R | 0.964607755785585 | 0.964607755785585 | relative 1e-12 | pass |

Note: vegan's own help computes these on BCI (Shannon 4.018, 3.848 and 3.814; Simpson 0.975, 0.968 and 0.965 for the first three plots); the check is against vegan itself.

### `table.add_diversity_columns at_total_count=`

**at_total_count=: BCI, the expected richness in 20 trees** (real data; data: BCI (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rarefied plot 1 | R | 16.3614744200566 | 16.3614744200566 | relative 1e-12 | pass |
| rarefied plot 2 | R | 15.6698282771649 | 15.6698282771649 | relative 1e-12 | pass |
| rarefied plot 3 | R | 15.3012286569057 | 15.3012286569057 | relative 1e-12 | pass |

Note: vegan's rarefy help example: 16.361, 15.670 and 15.301 for the first three plots.

### `table.add_diversity_columns show="chao1"`

**show="chao1": BCI, the bias-corrected Chao1 of the first three plots** (real data; data: BCI (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Chao1 plot 1 | R | 117.473684210526 | 117.473684210526 | relative 1e-12 | pass |
| Chao1 plot 2 | R | 117.214285714286 | 117.214285714286 | relative 1e-12 | pass |
| Chao1 plot 3 | R | 141.230769230769 | 141.230769230769 | relative 1e-12 | pass |
| Chao1 SE plot 1 | R | 11.5837848486587 | 11.5837848486587 | relative 1e-12 | pass |
| Chao1 SE plot 2 | R | 15.91895263909 | 15.91895263909 | relative 1e-12 | pass |
| Chao1 SE plot 3 | R | 23.0014048932778 | 23.0014048932778 | relative 1e-12 | pass |

### `table.add_diversity_columns show="hill numbers"`

**show="hill numbers": BCI, Hill numbers of order 1 and 2** (real data; data: BCI (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| q1 plot 1 | R | 55.612703881371 | 55.612703881371 | relative 1e-12 | pass |
| q1 plot 2 | R | 46.9212736331505 | 46.9212736331505 | relative 1e-12 | pass |
| q1 plot 3 | R | 45.3340998301171 | 45.3340998301171 | relative 1e-12 | pass |
| q2 plot 1 | R | 39.4155538098979 | 39.4155538098979 | relative 1e-12 | pass |
| q2 plot 2 | R | 31.584877315974 | 31.584877315974 | relative 1e-12 | pass |
| q2 plot 3 | R | 28.2547779095822 | 28.2547779095822 | relative 1e-12 | pass |

Note: Hill number 1 is exp(Shannon) and 2 the inverse Simpson index (Jost 2006).

### `draw_richness_curves`

**BCI: the first plot's curve** (real data; data: BCI (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| second point | R | 7 | 7 | relative 1e-09 | pass |
| richness there | R | 6.53946132072767 | 6.53946132072767 | relative 1e-09 | pass |
| richness at the end | R | 93 | 93 | relative 1e-09 | pass |

### `table.add_log_ratio_columns`

**mite: clr of 35 mite species, zeros replaced by estimated small values** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| clr row 1 first | R | 2.65706131913279 | 2.65706131913279 | relative 1e-09 | pass |
| clr row 2 last | R | -0.55753809836574 | -0.55753809836574 | relative 1e-09 | pass |
| clr row 70 first | R | 1.74464633225449 | 1.74464633225449 | relative 1e-09 | pass |

### `table.add_log_ratio_columns test_method="alr"`

**test_method="alr": mite, every species over the first one** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| alr row 1 second | R | -1.22377543162212 | -1.22377543162212 | relative 1e-09 | pass |
| alr row 5 last | R | -1.58699631979019 | -1.58699631979019 | relative 1e-09 | pass |

### `table.add_log_ratio_columns test_method="ilr"`

**test_method="ilr": mite, isometric log ratios** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| ilr1 row 1 | R | -0.865339906349492 | -0.865339906349492 | relative 1e-09 | pass |
| ilr34 row 3 | R | -0.207481584794687 | -0.207481584794687 | relative 1e-09 | pass |

### `table.add_log_ratio_columns zeros_replaced_by="adding 1"`

**zeros_replaced_by="adding 1": mite, clr after adding 1** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| clr row 1 first | R | 1.97156110116333 | 1.97156110116333 | relative 1e-09 | pass |
| clr row 9 fifth | R | -0.111212933047999 | -0.111212933047999 | relative 1e-09 | pass |

### `table.add_principal_coordinates`

**dune: PCoA of the Bray-Curtis distances** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| PCo1 row 1 | R | -0.354731824459132 | -0.354731824459132 | relative 1e-09 | pass |
| PCo2 row 20 | R | 0.157530053284472 | 0.157530053284472 | relative 1e-09 | pass |
| PCo1 % of positive | R | 37.4 | 37.4 | relative 1e-09 | pass |
| PCo1 % (vegan, ape) | R | 39.9 | 39.9 | relative 1e-09 | pass |
| negative eigenvalues | R | 5 | 5 | relative 1e-09 | pass |

Note: The shares are read from the printout (one decimal) and compared with R rounded the same way; the design check found 37.4 % of the positive eigenvalues, 39.9 % in vegan and ape, and 5 negative eigenvalues.

### `table.add_principal_coordinates measure="aitchison"`

**measure="aitchison": mite, PCoA of the Aitchison distances** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| PCo1 row 1 | R | 2.69778157533697 | 2.69778157533697 | relative 1e-08 | pass |
| PCo2 row 70 | R | 0.0179984204752759 | 0.0179984204752759 | relative 1e-08 | pass |

### `table.explain_profiles_of`

**varespec and varechem: db-RDA on Bray-Curtis with N, P and K** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| adjusted R squared | R | 0.0753000177198457 | 0.0753000177198457 | relative 1e-09 | pass |
| R squared | R | 0.195913058886822 | 0.195913058886822 | relative 1e-09 | pass |
| p N | R | 0.171 | 0.171 | relative 1e-09 | pass |
| p P | R | 0.265 | 0.265 | relative 1e-09 | pass |
| p K | R | 0.496 | 0.496 | relative 1e-09 | pass |
| F N | R | 1.53157846888648 | 1.53157846888648 | relative 1e-09 | pass |

Note: The design check found adjusted R squared 0.0753 and marginal p-values 0.171, 0.265 and 0.496.

### `table.explain_profiles_of measure="hellinger"`

**measure="hellinger": varespec and varechem, RDA with N, P and K** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| adjusted R squared | R | 0.0824713297170609 | 0.0824713297170609 | relative 1e-09 | pass |
| F all | R | 1.68911219341243 | 1.68911219341243 | relative 1e-09 | pass |
| p all | R | 0.048 | 0.048 | relative 1e-09 | pass |

Note: The design check found adjusted R squared 0.0825.

### `table.explain_profiles_of test_method="canonical correspondence"`

**test_method="canonical correspondence": varespec, CCA with Al, P and K** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| R squared | R | 0.309204040714596 | 0.309204040714596 | relative 1e-09 | pass |
| F all | R | 2.98403637676605 | 2.98403637676605 | relative 1e-09 | pass |
| p Al | R | 0.001 | 0.001 | relative 1e-09 | pass |

Note: The model of Oksanen's vegan tutorial (cca(varespec ~ Al + P + K, varechem)).

### `table.explain_profiles_of allowing_for=`

**allowing_for=: dune, management after allowing for the A1 horizon** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| adjusted R squared | R | 0.173990481006338 | 0.173990481006338 | relative 1e-09 | pass |
| F | R | 2.48275565065661 | 2.48275565065661 | relative 1e-09 | pass |
| p | R | 0.004 | 0.004 | relative 1e-09 | pass |

### `table.find_correlation_between_profiles`

**varespec and varechem: Mantel test** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Mantel r | R | 0.304745412697958 | 0.304745412697958 | relative 1e-09 | pass |
| p | R | 0.001 | 0.001 | relative 1e-09 | pass |

Note: The design check found r 0.305 (p 0.001).

### `table.find_correlation_between_profiles test_method="procrustes"`

**test_method="procrustes": varespec and varechem** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Procrustes correlation | R | 0.616575031599296 | 0.616575031599296 | relative 1e-09 | pass |
| p | R | 0.001 | 0.001 | relative 1e-09 | pass |

### `table.compare_profiles_of test_method="anosim"`

**test_method="anosim": dune by management** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| ANOSIM R | R | 0.257870590096504 | 0.257870590096504 | relative 1e-09 | pass |
| p | R | 0.011 | 0.011 | relative 1e-09 | pass |

Note: The example of vegan's anosim help; the design check found R 0.258.

### `table.compare_profiles_of show="contributions"`

**show="contributions": dune by management (SIMPER)** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first average contribution | R | 0.0613738749701877 | 0.0613738749701877 | relative 1e-09 | pass |
| first ratio | R | 1.79491078781329 | 1.79491078781329 | relative 1e-09 | pass |
| first cumulative share | R | 0.0982427057995617 | 0.0982427057995617 | relative 1e-09 | pass |

### `table.compare_profiles_of measure="aitchison"`

**measure="aitchison": mite by microtopography (PERMANOVA)** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| pseudo-F | R | 9.8478030900833 | 9.8478030900833 | relative 1e-09 | pass |
| R squared | R | 0.126500719341915 | 0.126500719341915 | relative 1e-09 | pass |
| p | R | 0.001 | 0.001 | relative 1e-09 | pass |

### `table.find_distances_between_rows measure="aitchison"`

**measure="aitchison": mite, cores 1, 2 and 70** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1 to 2 | R | 7.52901680609539 | 7.52901680609539 | relative 1e-09 | pass |
| 1 to 70 | R | 10.6620447965476 | 10.6620447965476 | relative 1e-09 | pass |

### `table.add_clusters how_many="automatic"`

**how_many="automatic": dune, Bray-Curtis, average linkage** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| clusters | R | 2 | 2 | exact | pass |
| size of cluster 1 | R | 16 | 16 | exact | pass |

### `table.add_clusters measure=`

**measure=: dune, Bray-Curtis, average linkage, 3 clusters** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average silhouette width | R | 0.285531716383304 | 0.285531716383304 | relative 1e-09 | pass |
| width of row 1 | R | 0.328489278246084 | 0.328489278246084 | relative 1e-09 | pass |

Note: The design check found an average width of 0.286.

### `draw_cluster_tree`

**dune: Bray-Curtis, average linkage** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top join | R | 0.786468856919626 | 0.786468856919626 | relative 1e-09 | pass |
| lowest join | R | 0.227272727272727 | 0.227272727272727 | relative 1e-09 | pass |

### `table.add_axes_that_separate_groups`

**crabs: four groups (colour form and sex) from five measurements** (real data; data: crabs (MASS))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| LD1 share of trace | R | 0.6861 | 0.6861 | relative 1e-09 | pass |
| LD2 share of trace | R | 0.2995 | 0.2995 | relative 1e-09 | pass |
| LD3 share of trace | R | 0.0144 | 0.0144 | relative 1e-09 | pass |
| leave-one-out % correct | R | 95 | 95 | relative 1e-09 | pass |
| LD1 row 1 size | R | 1.53886934430205 | 1.53886934430205 | relative 1e-09 | pass |

Note: simplydata takes the shares of the trace from MASS's own print (4 decimals, as print.lda rounds them), so R's side rounds svd^2 / sum(svd^2) the same way and they must agree exactly; the leave-one-out share and the scores are compared unrounded. (Before, the check read the one-decimal printout and allowed 0.4 %.) The design check found 0.686, 0.300 and 0.014, and 95 % correct.

### `table.add_correspondence_axes`

**varespec: correspondence analysis (CA)** (published; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| CA1 % | Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083 | 25.2 | 25.2 | within 0.05 (printed rounding) | pass |
| CA2 % | Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083 | 17.1 | 17.1 | within 0.05 (printed rounding) | pass |
| CA1 % | R | 25.2 | 25.2 | relative 1e-09 | pass |
| CA2 % | R | 17.1 | 17.1 | relative 1e-09 | pass |
| CA1 row 1 size | R | 0.108121658834307 | 0.108121658834307 | relative 1e-09 | pass |

Note: The tutorial gives the eigenvalues (0.5249 and 0.3568 of 2.083); the printout gives their shares.

**wg93: multiple correspondence analysis (MCA) of questions A to D** (published; data: wg93 (ca))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| axis 1 % | Nenadić & Greenacre (2007), JSS 20(3), and Greenacre (2007): adjusted inertia of wg93 A to D | 44.9 | 44.9 | within 0.05 (printed rounding) | pass |
| axis 2 % | Nenadić & Greenacre (2007), JSS 20(3), and Greenacre (2007): adjusted inertia of wg93 A to D | 34.2 | 34.2 | within 0.05 (printed rounding) | pass |
| axis 1 % | R | 44.9 | 44.9 | relative 1e-09 | pass |
| axis 2 % | R | 34.2 | 34.2 | relative 1e-09 | pass |

### `table.add_correspondence_axes show="numbers"`

**show="numbers": varespec, the eigenvalues and the total inertia** (published; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| CA1 eigenvalue | Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083 | 0.524931994280495 | 0.5249 | within 5e-05 (printed rounding) | pass |
| CA2 eigenvalue | Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083 | 0.356798023083954 | 0.3568 | within 5e-05 (printed rounding) | pass |
| total inertia | Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083 | 2.08319828789077 | 2.083 | within 0.0005 (printed rounding) | pass |
| CA1 eigenvalue | R | 0.524931994280495 | 0.524931994280495 | relative 1e-10 | pass |
| CA2 eigenvalue | R | 0.356798023083954 | 0.356798023083954 | relative 1e-10 | pass |
| total inertia | R | 2.08319828789077 | 2.08319828789077 | relative 1e-10 | pass |

Note: The eigenvalues and the total inertia are vegan's own (summary(eigenvals()) and tot.chi), given back as numbers; the tutorial prints them to 4 and 3 decimals.

### `table.find_hidden_factors_behind`

**nine ability tests: parallel analysis, minres, oblimin (the defaults)** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x1 on factor 2 | R | 0.591615227616584 | 0.591615227616584 | relative 1e-08 | pass |
| x4 on factor 1 | R | 0.846102782503992 | 0.846102782503992 | relative 1e-08 | pass |
| x7 on factor 3 | R | 0.736544152684073 | 0.736544152684073 | relative 1e-08 | pass |
| x9 on factor 2 | R | 0.382275730401817 | 0.382275730401817 | relative 1e-08 | pass |
| x9 on factor 3 | R | 0.456359717134766 | 0.456359717134766 | relative 1e-08 | pass |
| shared part of x1 | R | 0.476754007780125 | 0.476754007780125 | relative 1e-08 | pass |
| shared part of x9 | R | 0.460461383517286 | 0.460461383517286 | relative 1e-08 | pass |
| factors | R | 3 | 3 | relative 1e-08 | pass |

Note: Parallel analysis finds the three factors of Holzinger and Swineford's design (visual, verbal and speed); x9 goes with two of them, as the modification indices of the confirmatory model also show.

### `table.find_hidden_factors_behind how_many=`

**how_many=: three factors asked for, no parallel analysis** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x1 on factor 2 | R | 0.591615227616584 | 0.591615227616584 | relative 1e-08 | pass |
| x4 on factor 1 | R | 0.846102782503992 | 0.846102782503992 | relative 1e-08 | pass |
| x7 on factor 3 | R | 0.736544152684073 | 0.736544152684073 | relative 1e-08 | pass |
| x9 on factor 2 | R | 0.382275730401817 | 0.382275730401817 | relative 1e-08 | pass |
| x9 on factor 3 | R | 0.456359717134766 | 0.456359717134766 | relative 1e-08 | pass |
| shared part of x1 | R | 0.476754007780125 | 0.476754007780125 | relative 1e-08 | pass |
| shared part of x9 | R | 0.460461383517286 | 0.460461383517286 | relative 1e-08 | pass |
| factors | R | 3 | 3 | relative 1e-08 | pass |

Note: The oblimin rotation of GPArotation starts from random numbers, so both sides set R's seed first (unseeded, the loadings change in the sixth digit from run to run).

### `table.find_hidden_factors_behind rotation=`

**rotation=: promax, with principal axis factoring** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x1 on factor 2 | R | 0.0390228442789628 | 0.0390228442789628 | relative 1e-08 | pass |
| x4 on factor 1 | R | 0.849737553166453 | 0.849737553166453 | relative 1e-08 | pass |
| x7 on factor 3 | R | -0.226409506419214 | -0.226409506419214 | relative 1e-08 | pass |
| x9 on factor 2 | R | 0.47660221600333 | 0.47660221600333 | relative 1e-08 | pass |
| x9 on factor 3 | R | 0.344044301672691 | 0.344044301672691 | relative 1e-08 | pass |
| shared part of x1 | R | 0.476914814044883 | 0.476914814044883 | relative 1e-08 | pass |
| shared part of x9 | R | 0.460820618036742 | 0.460820618036742 | relative 1e-08 | pass |
| factors | R | 3 | 3 | relative 1e-08 | pass |

### `table.find_hidden_factors_behind test_method=`

**test_method=: maximum likelihood with varimax, as R factanal** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| own part of x1 | statsmodels Factor (method="ml"), run to 1e-14 | 0.512529527173444 | 0.512528190285928 | relative 1e-05 | pass |
| own part of x2 | statsmodels Factor (method="ml"), run to 1e-14 | 0.7487351603869 | 0.748735797058768 | relative 1e-05 | pass |
| own part of x3 | statsmodels Factor (method="ml"), run to 1e-14 | 0.542773290729758 | 0.542774348932094 | relative 1e-05 | pass |
| own part of x4 | statsmodels Factor (method="ml"), run to 1e-14 | 0.279193093920193 | 0.279192902262968 | relative 1e-05 | pass |
| own part of x5 | statsmodels Factor (method="ml"), run to 1e-14 | 0.242877320676014 | 0.242877268495408 | relative 1e-05 | pass |
| own part of x6 | statsmodels Factor (method="ml"), run to 1e-14 | 0.305215855558411 | 0.305215955458636 | relative 1e-05 | pass |
| own part of x7 | statsmodels Factor (method="ml"), run to 1e-14 | 0.502207221916073 | 0.502208273948145 | relative 1e-05 | pass |
| own part of x8 | statsmodels Factor (method="ml"), run to 1e-14 | 0.468550489794598 | 0.46854957939809 | relative 1e-05 | pass |
| own part of x9 | statsmodels Factor (method="ml"), run to 1e-14 | 0.543247686483438 | 0.543246712755349 | relative 1e-05 | pass |
| own part of x1 | R | 0.512529527173444 | 0.512528062225809 | relative 1e-05 | pass |
| own part of x2 | R | 0.7487351603869 | 0.748735775106279 | relative 1e-05 | pass |
| own part of x3 | R | 0.542773290729758 | 0.542774360019973 | relative 1e-05 | pass |
| own part of x4 | R | 0.279193093920193 | 0.279193042201229 | relative 1e-05 | pass |
| own part of x5 | R | 0.242877320676014 | 0.242877299279511 | relative 1e-05 | pass |
| own part of x6 | R | 0.305215855558411 | 0.305215788140177 | relative 1e-05 | pass |
| own part of x7 | R | 0.502207221916073 | 0.502208589415889 | relative 1e-05 | pass |
| own part of x8 | R | 0.468550489794598 | 0.468549571050821 | relative 1e-05 | pass |
| own part of x9 | R | 0.543247686483438 | 0.543246719035281 | relative 1e-05 | pass |
| x1 on factor 2 | R | 0.622657847373775 | 0.622659197499037 | relative 1e-05 | pass |
| x4 on factor 1 | R | 0.826999673867174 | 0.826999686293857 | relative 1e-05 | pass |
| x7 on factor 3 | R | 0.695873917746764 | 0.695872958545316 | relative 1e-05 | pass |
| x9 on factor 3 | R | 0.523617982828501 | 0.52361856724954 | relative 1e-05 | pass |

Note: The part of each column the factors do not share (the uniqueness) does not depend on the rotation and is checked against base R factanal and statsmodels; the varimax loadings are checked against factanal (the same factor order and signs here). Both references are run to convergence (factanal's optim with factr = 1, statsmodels to 1e-14); they then agree with simplydata (R psych::fa(fm = "ml") with its own stopping rule) to 3e-6, so the check allows 1e-5. With their default stopping rules the three differed by up to 1.6e-5, and the check allowed 1e-3.

### `table.check_hidden_factors`

**the three-factor model of the lavaan paper** (published; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | Rosseel (2012), JSS 48(2) | 85.3055217699732 | 85.306 | within 0.0005 (printed rounding) | pass |
| degrees of freedom | exact | 24 | 24 | within 0 | pass |
| CFI | Rosseel (2012), JSS 48(2) | 0.930559651799336 | 0.931 | within 0.0005 (printed rounding) | pass |
| TLI | Rosseel (2012), JSS 48(2) | 0.895839477699003 | 0.896 | within 0.0005 (printed rounding) | pass |
| RMSEA | Rosseel (2012), JSS 48(2) | 0.092121484510169 | 0.092 | within 0.0005 (printed rounding) | pass |
| RMSEA 90 % CI low | Rosseel (2012), JSS 48(2) | 0.0714184904399386 | 0.071 | within 0.0005 (printed rounding) | pass |
| RMSEA 90 % CI high | Rosseel (2012), JSS 48(2) | 0.113678016811963 | 0.114 | within 0.0005 (printed rounding) | pass |
| SRMR | Rosseel (2012), JSS 48(2) | 0.0652050571843865 | 0.065 | within 0.0005 (printed rounding) | pass |
| chi-square | R | 85.3055217699732 | 85.3055217699732 | relative 1e-08 | pass |
| degrees of freedom | R | 24 | 24 | relative 1e-08 | pass |
| CFI | R | 0.930559651799336 | 0.930559651799336 | relative 1e-08 | pass |
| TLI | R | 0.895839477699003 | 0.895839477699003 | relative 1e-08 | pass |
| RMSEA | R | 0.092121484510169 | 0.092121484510169 | relative 1e-08 | pass |
| RMSEA 90 % CI low | R | 0.0714184904399386 | 0.0714184904399386 | relative 1e-08 | pass |
| RMSEA 90 % CI high | R | 0.113678016811963 | 0.113678016811963 | relative 1e-08 | pass |
| SRMR | R | 0.0652050571843865 | 0.0652050571843865 | relative 1e-08 | pass |

Note: Rosseel (2012) prints the fit of this model to three decimals; the p-value of the chi-square test is below 0.001 there too.

**empty cells: 30 visual-perception scores taken out, full information** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | R | 87.4018469694271 | 87.4018469694271 | relative 1e-08 | pass |
| x1 loading | R | 0.791634162191103 | 0.791634162191103 | relative 1e-08 | pass |
| CFI | R | 0.92794179373821 | 0.92794179373821 | relative 1e-08 | pass |

Note: Real data with 30 cells emptied on purpose (the first 30 rows of x1): every row stays in, as with lavaan's missing = "ml"; lavaan's own default would leave the 30 rows out.

### `table.check_hidden_factors formula=`

**formula=: the speed factor explained by the visual one (lavaan sem)** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| path | R | 0.460317218924395 | 0.460317218924395 | relative 1e-08 | pass |
| its standard error | R | 0.0741697800420569 | 0.0741697800420569 | relative 1e-08 | pass |
| chi-square | R | 47.4133581632695 | 47.4133581632695 | relative 1e-08 | pass |
| CFI | R | 0.879367051234157 | 0.879367051234157 | relative 1e-08 | pass |

### `table.find_average_direction_of`

**turtles: the average direction of 10 homing turtles** (real data; data: turtles (circular))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average direction | SciPy circmean, directional_stats, circstd | 317.235319509156 | 317.235319509156 | relative 1e-09 | pass |
| resultant length | SciPy circmean, directional_stats, circstd | 0.818649629673879 | 0.818649629673878 | relative 1e-09 | pass |
| circular standard deviation (degrees) | SciPy circmean, directional_stats, circstd | 36.2460083554047 | 36.2460083554047 | relative 1e-09 | pass |
| average direction | R | 317.235319509156 | 317.235319509155 | relative 1e-09 | pass |
| resultant length | R | 0.818649629673879 | 0.818649629673878 | relative 1e-09 | pass |
| circular standard deviation (degrees) | R | 36.2460083554047 | 36.2460083554047 | relative 1e-09 | pass |

Note: R circular gives the mean as -42.76 degrees; shown here from 0 to 360 (317.24), as simplydata gives it. R sd.circular gives radians; shown here in degrees.

**ICU arrivals: the average time of day of 254 arrivals (full_turn=24)** (real data; data: ICU arrivals (circular))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average hour | R | 17.2579169214614 | 17.2579169214614 | relative 1e-09 | pass |
| resultant length | R | 0.317302854340033 | 0.317302854340033 | relative 1e-09 | pass |

Note: R circular gives -6.74 hours, the same time of day as 17.26 (about 17:16).

### `table.compare_shape_to shape="even around the circle"`

**shape="even around the circle": turtles, the Rayleigh test** (real data; data: turtles (circular))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| resultant length | R | 0.818649629673878 | 0.818649629673878 | relative 1e-09 | pass |
| p-value | R | 0.000305399546463319 | 0.000305399546463319 | relative 1e-09 | pass |

Note: Without units = "degrees" R circular reads the degrees as radians and gives p = 0.15 instead of 0.0003 (the trap simplydata avoids by always giving the units).

**shape="even around the circle": ICU arrivals by hour (full_turn=24)** (real data; data: ICU arrivals (circular))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| resultant length | R | 0.317302854340033 | 0.317302854340033 | relative 1e-09 | pass |
| p-value | R | 7.83046086664025e-12 | 7.83046086664025e-12 | relative 1e-09 | pass |

### `table.find_autocorrelation_of x=`

**x=: meuse, Moran's I of log zinc with 1 / distance weights** (real data; data: meuse (sp))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Moran's I | R | 0.11912624765924 | 0.11912624765924 | relative 1e-09 | pass |
| p-value (999 shuffles, seed 1) | R | 0.001 | 0.001 | relative 1e-09 | pass |

Note: Moran's I from ape::Moran.I on the 1 / distance weights (ape scales each row to 1 itself): 0.1191, the number of the design's check; the p-value from spdep::moran.mc.

### `table.find_autocorrelation_of nearest=`

**nearest=: meuse, Moran's I of log zinc with the 8 nearest samples** (real data; data: meuse (sp))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Moran's I | R | 0.489606337219415 | 0.489606337219415 | relative 1e-09 | pass |

Note: With only the 8 nearest neighbours Moran's I is 0.49 instead of 0.12: the weights change the answer.

### `table.find_autocorrelation_of on_globe=`

**on_globe=: meuse in longitude and latitude, great-circle 1 / distance** (real data; data: meuse in longitude and latitude (sp, sf))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Moran's I | R | 0.116566169069327 | 0.116566169069327 | relative 1e-09 | pass |

Note: Over 3 km great-circle and grid distances hardly differ, so Moran's I is close to the grid's 0.1191.

### `table.find_variogram_of`

**meuse: the spherical variogram of log zinc** (published; data: meuse (sp))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| nugget | gstat vignette (Pebesma) | 0.0506597095446437 | 0.0507 | within 5e-05 (printed rounding) | pass |
| partial sill | gstat vignette (Pebesma) | 0.590605107555405 | 0.5906 | within 5e-05 (printed rounding) | pass |
| range | gstat vignette (Pebesma) | 897.001083383488 | 897 | within 0.5 (printed rounding) | pass |
| nugget | R | 0.0506597095446437 | 0.0506597095446437 | relative 1e-07 | pass |
| partial sill | R | 0.590605107555405 | 0.590605107555405 | relative 1e-07 | pass |
| range | R | 897.001083383488 | 897.001083383488 | relative 1e-07 | pass |
| first bin semivariance | R | 0.123447934906159 | 0.123447934906159 | relative 1e-07 | pass |

Note: The gstat vignette fits vgm(1, "Sph", 900, 1) and prints nugget 0.0507, partial sill 0.5906 and range 897; simplydata lets gstat choose its own start values and reaches the same fit.

### `draw_variogram`

**meuse: the dots and the curve of the variogram of log zinc** (real data; data: meuse (sp))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| last bin distance | R | 1543.20248199968 | 1543.20248199968 | relative 1e-07 | pass |
| last bin semivariance | R | 0.574822734067877 | 0.574822734067877 | relative 1e-07 | pass |
| curve at its end | R | 0.641264817100048 | 0.641264817100048 | relative 1e-07 | pass |

### `table.find_return_levels_of`

**Port Pirie: the 10- and 100-year sea levels** (published; data: Port Pirie (ismev))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 10-year level | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 4.29621194427233 | 4.3 | within 0.005 (printed rounding) | pass |
| 100-year level | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 4.68840379269535 | 4.69 | within 0.005 (printed rounding) | pass |
| 100-year normal 95 % CI low | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 4.37712539022629 | 4.38 | within 0.005 (printed rounding) | pass |
| 100-year normal 95 % CI high | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 4.9996821951644 | 5 | within 0.005 (printed rounding) | pass |
| 10-year level | R | 4.29621194427233 | 4.29621194427233 | relative 1e-09 | pass |
| 100-year level | R | 4.68840379269535 | 4.68840379269535 | relative 1e-09 | pass |
| 100-year normal 95 % CI low | R | 4.37712539022629 | 4.37712539022629 | relative 1e-09 | pass |
| 100-year normal 95 % CI high | R | 4.9996821951644 | 4.9996821951644 | relative 1e-09 | pass |

**Port Pirie: the profile-likelihood interval of the 100-year level** (real data; data: Port Pirie (ismev))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 100-year profile 95 % CI low | R | 4.49498373639485 | 4.49498373639485 | relative 1e-09 | pass |
| 100-year profile 95 % CI high | R | 5.25740791573094 | 5.25740791573094 | relative 1e-09 | pass |

Note: The same grid simplydata asks extRemes for (200 levels from the lower normal end to two widths above the upper one), so the ends agree to 1e-9. How close a 200-point grid comes to the exact profile ends is the next case.

**Port Pirie: the profile-likelihood interval of the 100-year level, against the exact profile** (real data; data: Port Pirie (ismev))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 100-year profile 95 % CI low | R | 4.49498373639485 | 4.49043681083534 | relative 0.0025 | pass |
| 100-year profile 95 % CI high | R | 5.25740791573094 | 5.2607045714823 | relative 0.0025 | pass |

Note: The exact ends: the profile log-likelihood of the 100-year level (the GEV written with the level as a parameter, Coles 2001, section 3.3.3) maximised over the other two at each level, and the level where it falls by half the chi-square 95 % point found by root finding (uniroot, to 1e-12). extRemes reads the ends off its grid, so simplydata's ends may lie one grid step (0.0093 here, 1/200 of the range searched; 0.2 % of the level) from the exact ones: the tolerance is that step, a stated limit of the grid, not of the fit. A finer grid takes minutes for the threshold fits.

### `table.fit_distribution_to distribution="gev"`

**distribution="gev": Port Pirie, the GEV parameters** (published; data: Port Pirie (ismev))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| location | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 3.87474985466404 | 3.87 | within 0.005 (printed rounding) | pass |
| scale | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 0.198043956699285 | 0.198 | within 0.0005 (printed rounding) | pass |
| shape | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | -0.0501095297651447 | -0.05 | within 0.0005 (printed rounding) | pass |
| location | SciPy genextreme.fit run to 1e-14 (shape c = -xi) | 3.87474985466404 | 3.87474985805047 | relative 1e-06 | pass |
| scale | SciPy genextreme.fit run to 1e-14 (shape c = -xi) | 0.198043956699285 | 0.198043958575381 | relative 1e-06 | pass |
| shape | SciPy genextreme.fit run to 1e-14 (shape c = -xi) | -0.0501095297651447 | -0.0501095462385828 | relative 1e-06 | pass |
| location | R | 3.87474985466404 | 3.87474985509283 | relative 1e-06 | pass |
| scale | R | 0.198043956699285 | 0.198043956945225 | relative 1e-06 | pass |
| shape | R | -0.0501095297651447 | -0.0501095325366495 | relative 1e-06 | pass |

Note: SciPy's own fit stops a little short of the maximum (by up to 8e-5 here), so simplydata polishes it. Both references are run to 1e-14 (SciPy's fit with a tighter Nelder-Mead, R extRemes with optim's reltol 1e-14) and agree with simplydata to 1e-6; the shape, near 0, is the least precise (2e-7 relative). Before, the default fits were the references, at 5e-3 and 1e-4.

### `table.find_return_levels_of values_above=`

**values_above=: Coles's daily rain above 30 mm, the 100-year level** (published; data: Coles rain (ismev))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 100-year level | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 4.4.1 | 106.342764250305 | 106.3 | within 0.05 (printed rounding) | pass |
| 100-year level | R | 106.342764250305 | 106.342764250305 | relative 1e-09 | pass |
| 100-year normal 95 % CI low | R | 65.6222317218689 | 65.6222317218689 | relative 1e-09 | pass |
| 100-year normal 95 % CI high | R | 147.063296778741 | 147.063296778741 | relative 1e-09 | pass |

Note: Coles fits sigma 7.44 and xi 0.184 above 30 mm; simplydata gives them in its printout (7.44, 0.184). The R reference is fevd run to reltol 1e-14; with optim's default stopping rule the 100-year level stopped 1e-6 to 9e-6 short, so simplydata asks for reltol 1e-12.

### `table.fit_distribution_to distribution="generalised pareto"`

**distribution="generalised pareto": Coles rain, the amounts above 30 mm** (published; data: Coles rain (ismev))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| scale | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 4.4.1 | 7.44026904808288 | 7.44 | within 0.005 (printed rounding) | pass |
| shape | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 4.4.1 | 0.184499047010465 | 0.184 | within 0.0005 (printed rounding) | pass |
| scale | R | 7.44026904808288 | 7.44025220565683 | relative 0.0001 | pass |
| shape | R | 0.184499047010465 | 0.184497962931526 | relative 0.0001 | pass |

### `draw_threshold_check`

**Coles's daily rain: the mean excess and the shape from 20 to 40 mm** (real data; data: Coles rain (ismev))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first mean excess | R | 7.9434264827261 | 7.9434264827261 | relative 1e-09 | pass |
| first threshold shown | R | 20.7515151515152 | 20.7515151515152 | relative 1e-09 | pass |
| shape at 20 | R | 0.132361500062607 | 0.132361500062607 | relative 1e-09 | pass |
| shape at 40 | R | 0.0133913561116982 | 0.0133913561116982 | relative 1e-09 | pass |

Note: Coles (2001, 4.4.1, Figures 4.1 and 4.2) reads both panels as settling from about 30 mm.

### `table.find_percentile_of weights=`

**weights=: Quetelet's chest sizes, the 10th and 90th percentiles from counts** (real data; data: Quetelet's chest sizes)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 10th percentile | NumPy percentile of the repeated rows | 37 | 37 | relative 1e-09 | pass |
| 90th percentile | NumPy percentile of the repeated rows | 42 | 42 | relative 1e-09 | pass |
| 10th percentile | R | 37 | 37 | relative 1e-12 | pass |
| 90th percentile | R | 42 | 42 | relative 1e-12 | pass |

Note: R quantile(rep(x, w)) is R's definition of frequency weights (as Hmisc::wtd.quantile(normwt = FALSE)).

### `table.find_percentile_of weight_kind="analytic"`

**weight_kind="analytic": Quetelet's chest sizes, the weighted inverted CDF** (real data; data: Quetelet's chest sizes)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 25th percentile | NumPy percentile(weights=, method="inverted_cdf") | 38 | 38 | relative 1e-09 | pass |
| 90th percentile | NumPy percentile(weights=, method="inverted_cdf") | 42 | 42 | relative 1e-09 | pass |
| 25th percentile | R | 38 | 38 | relative 1e-12 | pass |
| 90th percentile | R | 42 | 42 | relative 1e-12 | pass |

Note: R has no weighted quantile in base R; the R side writes out the inverted CDF (Hyndman & Fan 1996, definition 1, with weights), the rule survey::svyquantile(qrule = "math") documents (survey itself is not run here).

### `table.find_median_of weights=`

**weights=: Quetelet's chest sizes, the median girth from counts** (real data; data: Quetelet's chest sizes)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| median | NumPy median of the repeated rows | 40 | 40 | relative 1e-09 | pass |
| median | R | 40 | 40 | relative 1e-12 | pass |

### `table.find_correlation_between show="covariance"`

**show="covariance": mtcars, fuel use, weight and horsepower** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| variance of mpg | pandas DataFrame.cov | 36.3241028225806 | 36.3241028225806 | relative 1e-09 | pass |
| mpg with wt | pandas DataFrame.cov | -5.11668467741936 | -5.11668467741936 | relative 1e-09 | pass |
| mpg with hp | pandas DataFrame.cov | -320.732056451613 | -320.732056451613 | relative 1e-09 | pass |
| wt with hp | pandas DataFrame.cov | 44.1926612903226 | 44.1926612903226 | relative 1e-09 | pass |
| variance of mpg | R | 36.3241028225806 | 36.3241028225806 | relative 1e-12 | pass |
| mpg with wt | R | -5.11668467741936 | -5.11668467741935 | relative 1e-12 | pass |
| mpg with hp | R | -320.732056451613 | -320.732056451613 | relative 1e-12 | pass |
| wt with hp | R | 44.1926612903226 | 44.1926612903226 | relative 1e-12 | pass |

### `table.forecast order="automatic"`

**order="automatic": the air passengers, the order auto.arima chooses and the forecast** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| forecast for 1961-01 | R | 445.634901393398 | 445.634901393398 | relative 1e-09 | pass |
| 95 % low | R | 423.085052944875 | 423.085052944875 | relative 1e-09 | pass |
| 95 % high | R | 468.184749841921 | 468.184749841921 | relative 1e-09 | pass |
| forecast for 1961-12 | R | 465.507584080752 | 465.507584080752 | relative 1e-09 | pass |

Note: auto.arima chooses ARIMA(2,1,1)(0,1,0)[12] for the raw passengers (forecast 9.0.2).

**order="automatic": the log air passengers, the airline model of Box and Jenkins** (published; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| p | Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G) | 0 | 0 | within 0 (printed rounding) | pass |
| d | Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G) | 1 | 1 | within 0 (printed rounding) | pass |
| q | Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G) | 1 | 1 | within 0 (printed rounding) | pass |
| seasonal p | Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G) | 0 | 0 | within 0 (printed rounding) | pass |
| seasonal d | Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G) | 1 | 1 | within 0 (printed rounding) | pass |
| seasonal q | Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G) | 1 | 1 | within 0 (printed rounding) | pass |
| p | R | 0 | 0 | relative 1e-09 | pass |
| d | R | 1 | 1 | relative 1e-09 | pass |
| q | R | 1 | 1 | relative 1e-09 | pass |
| seasonal p | R | 0 | 0 | relative 1e-09 | pass |
| seasonal d | R | 1 | 1 | relative 1e-09 | pass |
| seasonal q | R | 1 | 1 | relative 1e-09 | pass |
| ma1 | R | -0.401828016755777 | -0.401828016755777 | relative 1e-09 | pass |
| sma1 | R | -0.556944838448378 | -0.556944838448378 | relative 1e-09 | pass |

Note: The order is Box and Jenkins's airline model; the two estimates are checked against R (exact maximum likelihood: ma1 -0.402, sma1 -0.557), as Box and Jenkins estimated them another way.

### `table.add_adjusted_p_value_column test_method="storey"`

**test_method="storey": Hedenfalk's 3170 genes, Storey's q-values** (published; data: hedenfalk (qvalue))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| pi0 | Storey & Tibshirani (2003), PNAS 100:9440-9445 | 0.669926026474841 | 0.67 | within 0.005 (printed rounding) | pass |
| pi0 | R | 0.669926026474841 | 0.669926026474842 | relative 1e-09 | pass |
| q-values below 0.05 | R | 162 | 162 | relative 1e-09 | pass |
| first q-value | R | 0.0881916317044278 | 0.0881916317044278 | relative 1e-09 | pass |

Note: pi0 is read back from the table as the q-value of the largest p-value divided by that p-value (qvalue's last q-value is pi0 times it). The paper finds 160 genes at q < 0.05 on its own p-values; qvalue's copy of the p-values gives 162.

### `table.add_adjusted_p_value_column test_method="local fdr"`

**test_method="local fdr": Hedenfalk's 3170 genes, the local false discovery rate** (real data; data: hedenfalk (qvalue))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| below 0.05 | R | 85 | 85 | relative 1e-09 | pass |
| first | R | 0.168270194881528 | 0.168270194881528 | relative 1e-09 | pass |
| smallest | R | 0.00656991586563362 | 0.00656991586563362 | relative 1e-09 | pass |

### `table.compare_each_pair_of matched_by=, test_method="nemenyi"`

**matched_by=, test_method="nemenyi": rounding first base, three routes** (real data; data: rounding first base)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| narrow angle vs round out | R | 0.637427167018665 | 0.637427167018665 | relative 1e-09 | pass |
| narrow angle vs wide angle | R | 0.0613707592551845 | 0.0613707592551845 | relative 1e-09 | pass |
| round out vs wide angle | R | 0.00440982044545224 | 0.00440982044545224 | relative 1e-09 | pass |

Note: The same p-values (0.637, 0.061, 0.0044) come from scikit-posthocs posthoc_nemenyi_friedman.

### `table.compare_each_pair_of matched_by=, test_method="conover"`

**matched_by=, test_method="conover": rounding first base, Holm-adjusted** (real data; data: rounding first base)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| narrow angle vs round out | R | 0.30120902143937 | 0.30120902143937 | relative 1e-09 | pass |
| narrow angle vs wide angle | R | 0.0245657146957979 | 0.0245657146957979 | relative 1e-09 | pass |
| round out vs wide angle | R | 0.00207436042825609 | 0.00207436042825609 | relative 1e-09 | pass |

Note: PMCMRplus's own default adjustment is single-step (0.547, 0.0007, 0.024) and scikit-posthocs adjusts nothing (0.301, 0.0007, 0.012); simplydata names Holm.

### `table.compare_each_pair_of based_on="percents"`

**based_on="percents": Fleiss's smokers in four groups of patients** (real data; data: smokers (Fleiss))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1 vs 4 | R | 0.118564819859551 | 0.118564819859551 | relative 1e-09 | pass |
| 2 vs 4 | R | 0.0932172826883022 | 0.0932172826883023 | relative 1e-09 | pass |
| 3 vs 4 | R | 0.123768049716158 | 0.123768049716157 | relative 1e-09 | pass |
| 1 vs 2 | R | 1 | 1 | relative 1e-09 | pass |

Note: R pairwise.prop.test() uses Yates' correction and Holm by default, as simplydata does (without the correction 1 vs 4 would be 0.057 instead of 0.119).

**based_on="percents": Fleiss's smokers, Fisher's exact test for each pair** (real data; data: smokers (Fleiss))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1 vs 4 | R | 0.0749681614262827 | 0.0749681614262828 | relative 1e-09 | pass |
| 3 vs 4 | R | 0.0961238627259427 | 0.0961238627259427 | relative 1e-09 | pass |

### `sdata.make_random_assignments`

**permuted blocks: every block holds both groups equally often** (published; data: designs (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| largest imbalance within a block | exact | 0 | 0 | within 0 | pass |
| first group (A = 1) | R | 0 | 0 | exact | pass |
| places in the first list | R | 60 | 60 | exact | pass |

Note: Schulz & Grimes (2002): a permuted block holds every group equally often; R blockrand gives the same list for the same seed.

### `sdata.make_design_table`

**Yates' standard order of a 2 x 2 x 2 factorial** (published; data: designs (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| standard order of ab | exact | 4 | 4 | within 0 | pass |
| standard order of c | exact | 5 | 5 | within 0 | pass |
| plots | exact | 16 | 16 | within 0 | pass |
| first plot's a | R | 1 | 1 | exact | pass |
| plots | R | 16 | 16 | exact | pass |

Note: Montgomery (2017): (1), a, b, ab, c, ac, bc, abc, the order of R expand.grid().

### `sdata.make_design_table of_kind="randomised blocks"`

**of_kind="randomised blocks": each block holds every combination once** (published; data: designs (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| largest count of a combination in a block | exact | 1 | 1 | within 0 | pass |
| smallest count of a combination in a block | exact | 1 | 1 | within 0 | pass |
| first plot's b | R | 0 | 0 | exact | pass |

### `sdata.make_design_table of_kind="latin square"`

**of_kind="latin square": each level once in every row and column** (published; data: designs (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| levels in every row | exact | 4 | 4 | within 0 | pass |
| levels in every column | exact | 4 | 4 | within 0 | pass |
| first plot is A | R | 0 | 0 | exact | pass |

### `sdata.make_design_table of_kind="split plot"`

**of_kind="split plot": one irrigation per whole plot, every variety in it** (published; data: designs (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| irrigations in a whole plot | exact | 1 | 1 | within 0 | pass |
| varieties in a whole plot | exact | 3 | 3 | within 0 | pass |
| first part is A | R | 0 | 0 | exact | pass |

### `table.keep_random_rows for_each_group_in=`

**for_each_group_in=: 10 schools of each type from the api sample** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| elementary schools | pandas groupby().sample() | 10 | 10 | exact | pass |
| high schools | pandas groupby().sample() | 10 | 10 | exact | pass |
| total score | pandas groupby().sample() | 19998 | 19998 | exact | pass |

### `table.keep_random_rows percent=`

**percent=: 10 % of each school type from the api sample** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas groupby().sample(frac=) | 20 | 20 | exact | pass |
| middle schools | pandas groupby().sample(frac=) | 5 | 5 | exact | pass |
| total score | pandas groupby().sample(frac=) | 13619 | 13619 | exact | pass |

### `table.count_empty_cells_in show="patterns"`

**show="patterns": nhanes, the patterns of van Buuren & Groothuis-Oudshoorn** (published; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| complete rows | exact | 13 | 13 | within 0 | pass |
| rows with 3 empty cells | exact | 7 | 7 | within 0 | pass |
| patterns | exact | 5 | 5 | within 0 | pass |
| rows with 1 empty cell | exact | 4 | 4 | within 0 | pass |
| complete rows | R | 13 | 13 | exact | pass |
| rows with 3 empty cells | R | 7 | 7 | exact | pass |
| patterns | R | 5 | 5 | exact | pass |
| rows with 1 empty cell | R | 4 | 4 | exact | pass |

### `table.count_each columns=, in_order=`

**columns=, in_order=: the professional challenges survey, all 565 answers** (published; data: professional challenges (HH))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| agree | exact | 230 | 230 | within 0 | pass |
| strongly agree | exact | 283 | 283 | within 0 | pass |
| percent in top two | R | 90.7964601769911 | 90.7964601769912 | relative 1e-12 | pass |
| percent no opinion | R | 4.7787610619469 | 4.7787610619469 | relative 1e-12 | pass |

Note: Heiberger & Robbins (2014) publish the counts; the percents are R prop.table().

### `draw_answer_bars`

**the professional challenges survey: the middle answer split across 0** (published; data: professional challenges (HH))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bars | exact | 5 | 5 | within 0 | pass |
| left end | R | -6.8141592920354 | -6.8141592920354 | relative 1e-12 | pass |
| middle bar starts at | R | -2.38938053097345 | -2.38938053097345 | relative 1e-12 | pass |

Note: Heiberger & Robbins (2014): diverging bars centred on the middle answer.

### `table.use_survey_design`

**the stratified api sample: 197 degrees of freedom (200 schools, 3 strata)** (published; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| degrees of freedom | exact | 197 | 197 | within 0 | pass |
| degrees of freedom | R | 197 | 197 | exact | pass |

### `table.find_average_of after use_survey_design()`

**the stratified api sample: the mean API 2000 (Lumley 2010)** (published; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | Lumley (2010), Complex Surveys, and the R survey help (api) | 662.287363159321 | 662.29 | within 0.005 (printed rounding) | pass |
| standard error | Lumley (2010), Complex Surveys, and the R survey help (api) | 9.40894080278458 | 9.4089 | within 5e-05 (printed rounding) | pass |
| mean | R | 662.287363159321 | 662.287363159321 | relative 1e-09 | pass |
| standard error | R | 9.40894080278458 | 9.40894080278458 | relative 1e-09 | pass |
| 95 % CI low | R | 643.732188272086 | 643.732188272086 | relative 1e-09 | pass |

**the one-stage cluster sample: the mean API 2000 (Lumley 2010)** (published; data: api cluster sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | Lumley (2010), Complex Surveys, and the R survey help (api) | 644.169398907104 | 644.17 | within 0.005 (printed rounding) | pass |
| standard error | Lumley (2010), Complex Surveys, and the R survey help (api) | 23.542240693781 | 23.542 | within 0.0005 (printed rounding) | pass |
| degrees of freedom | Lumley (2010), Complex Surveys, and the R survey help (api) | 14 | 14 | within 0 (printed rounding) | pass |
| mean | R | 644.169398907104 | 644.169398907104 | relative 1e-09 | pass |
| standard error | R | 23.542240693781 | 23.542240693781 | relative 1e-09 | pass |

### `table.find_total_of after use_survey_design()`

**the stratified api sample: the total enrolment (Lumley 2010)** (published; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | Lumley (2010), Complex Surveys, and the R survey help (api) | 3687177.53243828 | 3687178 | within 0.5 (printed rounding) | pass |
| standard error | Lumley (2010), Complex Surveys, and the R survey help (api) | 114641.71610078 | 114642 | within 0.5 (printed rounding) | pass |
| total | R | 3687177.53243828 | 3687177.53243828 | relative 1e-09 | pass |
| standard error | R | 114641.71610078 | 114641.71610078 | relative 1e-09 | pass |
| 95 % CI high | R | 3913260.05715701 | 3913260.05715701 | relative 1e-09 | pass |

### `table.find_median_of after use_survey_design()`

**the stratified api sample: the median API 2000 and Woodruff's interval** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| median | R | 668 | 668 | relative 1e-09 | pass |
| 95 % CI low | R | 642 | 642 | relative 1e-09 | pass |
| 95 % CI high | R | 694 | 694 | relative 1e-09 | pass |
| standard error | R | 13.1840557881618 | 13.1840557881618 | relative 1e-09 | pass |

### `table.find_percentile_of after use_survey_design()`

**the stratified api sample: the 90th percentile of API 2000** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| percentile 90 | R | 836 | 836 | relative 1e-09 | pass |
| 95 % CI low | R | 806 | 806 | relative 1e-09 | pass |

### `table.find_percent_of_rows_where after use_survey_design()`

**the stratified api sample: the percent of schools that met their target** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| percent | R | 82.7948011001957 | 82.7948011001957 | relative 1e-09 | pass |
| 95 % CI low | R | 77.4539654351568 | 77.4539654351568 | relative 1e-09 | pass |
| 95 % CI high | R | 87.0814854544508 | 87.0814854544508 | relative 1e-09 | pass |

### `table.count_rows after use_survey_design()`

**the stratified api sample: the schools with an award in California** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| schools with an award | R | 3957.56995391846 | 3957.56995391846 | relative 1e-09 | pass |
| standard error | R | 213.110254631354 | 213.110254631354 | relative 1e-09 | pass |
| percent with an award | R | 63.8936064050578 | 63.8936064050578 | relative 1e-09 | pass |

### `table.explain after use_survey_design()`

**the stratified api sample: API 2000 from English learners and free meals** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| meals | R | -3.11062899440931 | -3.11062899440931 | relative 1e-09 | pass |
| meals standard error | R | 0.275765488815881 | 0.275765488815881 | relative 1e-09 | pass |
| ell p-value | R | 0.193873946007243 | 0.193873946007243 | relative 1e-09 | pass |
| intercept | R | 823.857925625161 | 823.857925625161 | relative 1e-09 | pass |

### `table.compare_averages_of after use_survey_design()`

**the stratified api sample: API 2000 with and without an award** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| difference | R | 44.687493955025 | 44.687493955025 | relative 1e-09 | pass |
| t | R | 2.30360731982132 | 2.30360731982132 | relative 1e-09 | pass |
| p-value | R | 0.02229352381506 | 0.02229352381506 | relative 1e-09 | pass |

### `table.compare_counts_of after use_survey_design()`

**the stratified api sample: awards by school type (Rao-Scott)** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| F | R | 14.1694081180078 | 14.1694081180078 | relative 1e-09 | pass |
| p-value | R | 2.08210867642843e-06 | 2.08210867642845e-06 | relative 1e-09 | pass |
| design degrees of freedom | R | 371.371769351819 | 371.371769351819 | relative 1e-09 | pass |

### `table.compare_balanced_groups_of`

**lalonde: weighting, the effect for everyone (ATE)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| effect | R | 224.676308271437 | 224.676308271437 | relative 1e-09 | pass |
| standard error | R | 876.193185586486 | 876.193185586486 | relative 1e-09 | pass |
| p-value | R | 0.797624033434651 | 0.797624033434651 | relative 1e-09 | pass |

Note: The randomised NSW experiment found 1794 dollars (Dehejia & Wahba 1999); the survey comparison group is very unlike the trained men, so balancing on these columns does not recover it fully.

**lalonde: the balance table (standardised differences, cobalt)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| race black before | R | 1.67082635003592 | 1.67082635003592 | relative 1e-09 | pass |
| race black after | R | 0.130249813461061 | 0.130249813461061 | relative 1e-09 | pass |
| re74 after | R | -0.273989428670679 | -0.273989428670679 | relative 1e-09 | pass |

### `table.compare_balanced_groups_of test_method="matching"`

**test_method="matching": lalonde, 1:1 nearest neighbour, the effect among the trained men (ATT)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| effect | R | 894.367480270271 | 894.367480270271 | relative 1e-09 | pass |
| standard error | R | 705.229764061617 | 705.229764061617 | relative 1e-09 | pass |

Note: The MatchIt vignette's own analysis of lalonde: ATT 894, clustered standard error 705.

**test_method="matching": lalonde, with a caliper of 0.2 standard deviations of the logit (match_within=0.2)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| effect | R | 1770.60290641026 | 1770.60290641026 | relative 1e-09 | pass |
| standard error | R | 924.234347046258 | 924.234347046258 | relative 1e-09 | pass |

### `table.compare_risks show="attributable fractions"`

**show="attributable fractions": dry cat food and urinary disease (Willeberg 1977)** (real data; data: dry cat food and FLUTD)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| AF among the exposed | R | 0.750470161919178 | 0.750470161919178 | relative 1e-09 | pass |
| AF low | R | 0.329128862567194 | 0.329128862567194 | relative 1e-09 | pass |
| AF high | R | 0.907213547250137 | 0.907213547250137 | relative 1e-09 | pass |
| PAF | R | 0.54200622805274 | 0.54200622805274 | relative 1e-09 | pass |

Note: epiR's help prints 75.05 % (32.91 to 90.72) among the exposed and 54.20 % in the population.

**show="attributable fractions": the preventable fraction is 1 minus the risk ratio (groups swapped)** (real data; data: dry cat food and FLUTD)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| preventable fraction | R | 0.750470161919178 | 0.750470161919178 | relative 1e-09 | pass |

Note: The definition 1 - risk ratio (Rothman, Greenland & Lash 2008), in base R.

### `table.rate_of standard_population=`

**standard_population=: Down syndrome by birth order, adjusted for the mother's age** (real data; data: Down syndrome by birth order)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| adjusted, first born | R | 92.3045255331994 | 92.3045255331994 | relative 1e-09 | pass |
| low, first born | R | 80.4417498507042 | 80.4417498507042 | relative 1e-09 | pass |
| high, first born | R | 105.763345749261 | 105.763345749261 | relative 1e-09 | pass |
| adjusted, fifth or later | R | 75.5290074452568 | 75.5290074452568 | relative 1e-09 | pass |
| crude, fifth or later | R | 167.114186413617 | 167.114186413617 | relative 1e-09 | pass |

Note: R epitools::ageadjust.direct is a separate package from epiR, which simplydata runs; the epitools help gives 92.3 (80.4 to 105.8) per 100,000 for the first born.

### `table.compare_rates standard_rates=`

**standard_rates=: Down syndrome by birth order against the pooled rates (SMR)** (real data; data: Down syndrome by birth order)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| observed / expected, first born | R | 1.89677486668325 | 1.89677486668325 | relative 1e-09 | pass |
| expected, first born | R | 217.210807269096 | 217.210807269096 | relative 1e-09 | pass |
| low, first born | R | 1.7180200935985 | 1.7180200935985 | relative 1e-09 | pass |
| p, first born | R | 6.870289653213e-32 | 6.870289653213e-32 | relative 1e-09 | pass |
| observed / expected, fifth or later | R | 1.75926671135108 | 1.75926671135108 | relative 1e-09 | pass |

Note: The ratio and the expected count from R epitools::ageadjust.indirect (a separate package from epiR); its log-normal interval differs, so the exact interval and p-value come from R poisson.test(). The standard rates are the table's own pooled rates, worked out in the case code.

### `table.explain through=`

**through=: JOBS II, the workshop, job-search confidence and depression** (real data; data: JOBS II (mediation))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| indirect effect | statsmodels Mediation (with_seed=1) | -0.0163155082561466 | -0.0163155082561466 | relative 1e-09 | pass |
| indirect low | statsmodels Mediation (with_seed=1) | -0.0457537091325962 | -0.0457537091325962 | relative 1e-09 | pass |
| total effect | statsmodels Mediation (with_seed=1) | -0.0554964945177594 | -0.0554964945177594 | relative 1e-09 | pass |
| indirect effect | R | -0.0163155082561466 | -0.0157446450289033 | within 4 Monte Carlo SE (0.00185) | pass |
| total effect | R | -0.0554964945177594 | -0.0560093450307454 | within 4 Monte Carlo SE (0.00584) | pass |

Note: For two linear models without an interaction the indirect effect is the product of the two coefficients and the total effect the coefficient of treat without job_seek (base R lm): the exact values the simulation (1000 draws) estimates, so the difference may be 4 Monte Carlo standard errors of simplydata's mean of 1000 draws. statsmodels with the same seed gives the same numbers exactly. R mediation::mediate(sims = 1000) gave -0.0159 (-0.0422 to 0.0105) here; Tingley et al. (2014) analyse the same data.

### `table.compare_averages_of period=`

**period=: bioequivalence reference dataset A (18 subjects, balanced)** (published; data: bioequivalence reference datasets)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| (all) | the data file named by SIMPLYDATA_SCHUTZ2014_FILE (not shipped; see DATA_LICENSES.md) | | | | skipped: needs the data file named by SIMPLYDATA_SCHUTZ2014_FILE (not shipped; see DATA_LICENSES.md), which is not given here |

Note: R lm() gives NA for the sequence (subject lies within it), as the EMA model expects.

**period=: bioequivalence reference dataset B (18 subjects, a large CV)** (published; data: bioequivalence reference datasets)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| (all) | the data file named by SIMPLYDATA_SCHUTZ2014_FILE (not shipped; see DATA_LICENSES.md) | | | | skipped: needs the data file named by SIMPLYDATA_SCHUTZ2014_FILE (not shipped; see DATA_LICENSES.md), which is not given here |

Note: R lm() gives NA for the sequence (subject lies within it), as the EMA model expects.

**period=: bioequivalence reference dataset C (13 subjects, unbalanced)** (published; data: bioequivalence reference datasets)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| (all) | the data file named by SIMPLYDATA_SCHUTZ2014_FILE (not shipped; see DATA_LICENSES.md) | | | | skipped: needs the data file named by SIMPLYDATA_SCHUTZ2014_FILE (not shipped; see DATA_LICENSES.md), which is not given here |

Note: R lm() gives NA for the sequence (subject lies within it), as the EMA model expects.

### `table.find_correlation_between empty_cells="multiple imputation"`

**empty_cells="multiple imputation": airquality, ozone and temperature (37 empty ozone cells)** (real data; data: airquality (R datasets))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| r | R | 0.666261392680928 | 0.668350258433025 | within 4 Monte Carlo SE (0.0165) | pass |

Note: R mice fills in with its own random draws, so the check is within the simulation error: R runs 10 times (seeds 1 to 10, 20 filled-in tables each), the reference is their average, and the difference may be 4 Monte Carlo standard errors, from the spread of R's runs (simplydata's one run of 20 tables is taken to vary as much as one of R's). The pooling itself is checked exactly in the same underneath.

### `table.explain_survival empty_cells="multiple imputation"`

**empty_cells="multiple imputation": lung cancer survival, with empty Karnofsky and weight-loss cells** (real data; data: lung with weight loss (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| hazard ratio sex | R | 0.602376904402302 | 0.6022641172295 | within 4 Monte Carlo SE (0.000835) | pass |
| hazard ratio ph.karno | R | 0.986281926886541 | 0.986241140925825 | within 4 Monte Carlo SE (0.000409) | pass |

Note: R mice with the event and the Nelson-Aalen hazard as predictors (White & Royston 2009) and its own random draws: R runs 10 times (seeds 1 to 10), the reference is their average, and the difference may be 4 Monte Carlo standard errors from the spread of R's runs.

### `table.compare_averages_of test_method="bayesian"`

**test_method="bayesian": Student's sleep data, the two drugs as two groups** (real data; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Bayes factor | SciPy quad of the JZS integral (Rouder et al. 2009, eq. 1) | 1.26592514957762 | 1.26592514964692 | relative 0.0001 | pass |
| Bayes factor | R | 1.26592514957762 | 1.26592514957762 | relative 1e-09 | pass |
| difference | R | -1.14640684760213 | -1.14640684760213 | relative 1e-09 | pass |
| 95 % low | R | -2.8850915447883 | -2.8850915447883 | relative 1e-09 | pass |
| 95 % high | R | 0.349075298827598 | 0.349075298827598 | relative 1e-09 | pass |

Note: BayesFactor's documentation gives 1.27 for this Bayes factor; the interval is checked with the same seed (same draws), its Monte Carlo error in the tests.

### `table.compare_before_and_after test_method="bayesian"`

**test_method="bayesian": Student's sleep data, each patient on both drugs** (real data; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Bayes factor | SciPy quad of the JZS integral (Rouder et al. 2009, eq. 1) | 17.2588802677725 | 17.2588802678108 | relative 0.0001 | pass |
| Bayes factor | R | 17.2588802677725 | 17.2588802677725 | relative 1e-09 | pass |
| average change | R | 1.41993408368893 | 1.41993408368893 | relative 1e-09 | pass |
| 95 % low | R | 0.479925518899774 | 0.479925518899774 | relative 1e-09 | pass |
| 95 % high | R | 2.29588000036818 | 2.29588000036818 | relative 1e-09 | pass |

Note: BayesFactor's documentation gives 17.26 for this paired Bayes factor (the example of ttestBF's help).

### `table.compare_average_to test_method="bayesian"`

**test_method="bayesian": Student's sleep data, drug 1 against 1 extra hour** (real data; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Bayes factor | SciPy quad of the JZS integral (Rouder et al. 2009, eq. 1), r = 1 | 0.254785902547741 | 0.254785902553349 | relative 0.0001 | pass |
| Bayes factor | R | 0.254785902547741 | 0.254785902547741 | relative 1e-09 | pass |
| difference | R | -0.21846272718357 | -0.21846272718357 | relative 1e-09 | pass |
| 95 % low | R | -1.36155600574835 | -1.36155600574835 | relative 1e-09 | pass |
| 95 % high | R | 0.907255893891201 | 0.907255893891201 | relative 1e-09 | pass |

Note: The Bayes factor is R's own ttestBF(x, mu = 1); the interval is that of the average minus 1, from ttestBF(x - 1), because BayesFactor's posterior() leaves mu = out.

### `table.find_correlation_between test_method="bayesian"`

**test_method="bayesian": mtcars, fuel use and weight** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Bayes factor | R | 13286626.3086362 | 13286626.3086362 | relative 1e-09 | pass |
| r | R | -0.816883822203406 | -0.816883822203406 | relative 1e-09 | pass |
| 95 % low | R | -0.903442066641586 | -0.903442066641586 | relative 1e-09 | pass |
| 95 % high | R | -0.664500941992188 | -0.664500941992188 | relative 1e-09 | pass |

Note: The design check of 2026-11-20 gave a Bayes factor of 1.3 x 10^7 for this pair (BayesFactor 0.9.12-4.8).

### `table.compare_counts_of test_method="bayesian"`

**test_method="bayesian": mtcars, gearbox (automatic or manual) by engine shape** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Bayes factor | the Gunel-Dickey closed form, independent multinomial, a = 1 (SciPy gammaln) | 0.631316369587394 | 0.631316369587392 | relative 0.0001 | pass |
| Bayes factor | R | 0.631316369587394 | 0.631316369587394 | relative 1e-09 | pass |
| share manual, straight | R | 0.501015289003796 | 0.501015289003796 | relative 1e-09 | pass |
| 95 % low | R | 0.272572770475845 | 0.272572770475845 | relative 1e-09 | pass |

Note: simplydata orders the groups as text ("V-shaped" before "straight"), so the R table lists them in that order too.

### `table.explain test_method="bayesian"`

**test_method="bayesian": mtcars, fuel use from weight and horsepower (rstanarm stan_glm)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| wt | R | -3.85951737319436 | -3.85951737319436 | relative 1e-09 | pass |
| wt 95 % low | R | -5.17810665610186 | -5.17810665610186 | relative 1e-09 | pass |
| wt 95 % high | R | -2.54937525695996 | -2.54937525695996 | relative 1e-09 | pass |
| hp | R | -0.0317827715959909 | -0.0317827715959909 | relative 1e-09 | pass |
| sigma | R | 2.66823086364637 | 2.66823086364637 | relative 1e-09 | pass |
| wt R-hat | R | 1.00142834570208 | 1.00142834570208 | relative 1e-09 | pass |

Note: lm() gives -3.88 for wt and -0.0318 for hp; the posterior medians are close to them because rstanarm's priors are weak here.

### `table.explain test_method="bayesian", grouped_by=`

**test_method="bayesian", grouped_by=: sleepstudy, reaction time over days (rstanarm stan_glmer)** (real data; data: sleepstudy (lme4))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Days | R | 10.4856060274156 | 10.4856060274156 | relative 1e-09 | pass |
| Days 95 % low | R | 8.92680673314495 | 8.92680673314495 | relative 1e-09 | pass |
| Days 95 % high | R | 12.0693679134866 | 12.0693679134866 | relative 1e-09 | pass |
| intercept | R | 250.176303391735 | 250.176303391735 | relative 1e-09 | pass |

Note: lme4's REML estimates are 251.4 and 10.47 (Bates et al. 2015); the posterior medians are close.

### `table.check_model_of test_method="bayesian"`

**test_method="bayesian": mtcars, the posterior predictive check of fuel use from weight** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| data density at point 100 | R | 0.060520300921314 | 0.060520300921314 | relative 1e-09 | pass |
| set 3 at point 100 | R | 0.0250130477338933 | 0.0250130477338933 | relative 1e-09 | pass |
| set 50 at point 200 | R | 0.0327979199969501 | 0.0327979199969501 | relative 1e-09 | pass |
| grid end | R | 37.0622730135315 | 37.0622730135315 | relative 1e-09 | pass |

Note: The picture's lines are R stats::density() of the data and of each set made up by posterior_predict(), on one grid from the smallest to the largest value.

### `table.show_first_rows`

**the first 3 of Fisher's 150 iris flowers, numbered from 1** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows shown | pandas head | 3 | 3 | relative 1e-12 | pass |
| first row number | pandas head | 1 | 1 | relative 1e-12 | pass |
| sepal length total | pandas head | 14.7 | 14.7 | relative 1e-12 | pass |

### `table.describe_columns`

**the columns of Fisher's iris data: averages and kinds** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average sepal length | pandas mean (rounded to 2 decimals, as printed) and nunique | 5.84 | 5.84 | relative 1e-12 | pass |
| average petal width | pandas mean (rounded to 2 decimals, as printed) and nunique | 1.2 | 1.2 | relative 1e-12 | pass |
| species | pandas mean (rounded to 2 decimals, as printed) and nunique | 3 | 3 | relative 1e-12 | pass |
| columns | pandas mean (rounded to 2 decimals, as printed) and nunique | 5 | 5 | relative 1e-12 | pass |
| average sepal length | R | 5.84 | 5.84 | relative 1e-12 | pass |
| species | R | 3 | 3 | relative 1e-12 | pass |

### `table.keep_columns`

**two of the 11 columns of mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas column selection | 2 | 2 | exact | pass |
| total mpg | pandas column selection | 642.9 | 642.9 | exact | pass |
| total hp | pandas column selection | 4694 | 4694 | exact | pass |

### `table.rename_column`

**mpg renamed in mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas rename | 642.9 | 642.9 | exact | pass |
| columns | pandas rename | 12 | 12 | exact | pass |

### `table.sort_by`

**NHANES body mass index, biggest first, empty cells last** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first bmi | pandas sort_values (stable) | 35.3 | 35.3 | exact | pass |
| first empty row | pandas sort_values (stable) | 16 | 16 | exact | pass |
| age of the first row | pandas sort_values (stable) | 1 | 1 | exact | pass |

### `table.keep_rows_by_position`

**rows 10 to 20 of mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas iloc | 11 | 11 | relative 1e-12 | pass |
| total mpg | pandas iloc | 218.1 | 218.1 | relative 1e-12 | pass |
| rows | R | 11 | 11 | relative 1e-12 | pass |
| total mpg | R | 218.1 | 218.1 | relative 1e-12 | pass |

### `table.fill_empty_cells_in`

**NHANES body mass index: the 9 empty cells filled with the median** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas fillna with the median | 665.75 | 665.75 | relative 1e-12 | pass |
| empty cells left | pandas fillna with the median | 0 | 0 | relative 1e-12 | pass |
| total | R | 665.75 | 665.75 | relative 1e-12 | pass |

### `table.turn_into_numbers`

**mtcars miles per gallon written with decimal commas, read back as numbers** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | the published numbers themselves | 642.9 | 642.9 | relative 1e-12 | pass |
| empty cells | the published numbers themselves | 0 | 0 | relative 1e-12 | pass |

### `table.add_column`

**mtcars horsepower per 1000 lb** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas division | 1450.70914531099 | 1450.70914531099 | relative 1e-12 | pass |
| first | pandas division | 41.9847328244275 | 41.9847328244275 | relative 1e-12 | pass |
| total | R | 1450.70914531099 | 1450.70914531099 | relative 1e-12 | pass |
| first | R | 41.9847328244275 | 41.9847328244275 | relative 1e-12 | pass |

### `table.add_group_column`

**mtcars cars put into four fuel-use groups (cut at 15, 20 and 25 mpg)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| A | pandas cut(right=False) | 6 | 6 | exact | pass |
| B | pandas cut(right=False) | 8 | 8 | exact | pass |
| C | pandas cut(right=False) | 13 | 13 | exact | pass |
| D | pandas cut(right=False) | 5 | 5 | exact | pass |
| A | R | 6 | 6 | exact | pass |
| B | R | 8 | 8 | exact | pass |
| C | R | 13 | 13 | exact | pass |
| D | R | 5 | 5 | exact | pass |

### `table.find_summary_of`

**sepal length of each iris species: average, standard deviation, count** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average setosa | pandas groupby().agg() | 5.006 | 5.006 | relative 1e-12 | pass |
| sd setosa | pandas groupby().agg() | 0.352489687213451 | 0.352489687213451 | relative 1e-12 | pass |
| count setosa | pandas groupby().agg() | 50 | 50 | relative 1e-12 | pass |
| average virginica | pandas groupby().agg() | 6.588 | 6.588 | relative 1e-12 | pass |
| sd virginica | pandas groupby().agg() | 0.635879593274432 | 0.635879593274432 | relative 1e-12 | pass |
| count virginica | pandas groupby().agg() | 50 | 50 | relative 1e-12 | pass |
| average setosa | R | 5.006 | 5.006 | relative 1e-12 | pass |
| sd setosa | R | 0.352489687213451 | 0.352489687213451 | relative 1e-12 | pass |
| average virginica | R | 6.588 | 6.588 | relative 1e-12 | pass |
| sd virginica | R | 0.635879593274432 | 0.635879593274432 | relative 1e-12 | pass |

### `table.join_with`

**mtcars joined with a small table of cylinder labels (all rows of mtcars kept)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas merge(how="left") | 32 | 32 | exact | pass |
| empty sizes | pandas merge(how="left") | 14 | 14 | exact | pass |
| total size | pandas merge(how="left") | 25 | 25 | exact | pass |

### `table.add_z_score_column`

**z-scores of iris sepal length within each species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | SciPy zscore(ddof=1) | 0.266674468530131 | 0.266674468530131 | relative 1e-10 | pass |
| last | SciPy zscore(ddof=1) | -1.08196584271116 | -1.08196584271116 | relative 1e-10 | pass |
| sum of squares | SciPy zscore(ddof=1) | 147 | 147 | relative 1e-10 | pass |
| first | R | 0.266674468530131 | 0.266674468530131 | relative 1e-10 | pass |
| last | R | -1.08196584271116 | -1.08196584271116 | relative 1e-10 | pass |
| sum of squares | R | 147 | 147 | relative 1e-10 | pass |

### `table.save`

**iris saved as CSV and read back** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas to_csv(index=False) | 150 | 150 | relative 1e-12 | pass |
| total petal length | pandas to_csv(index=False) | 563.7 | 563.7 | relative 1e-12 | pass |
| columns | pandas to_csv(index=False) | 5 | 5 | relative 1e-12 | pass |

### `table.save in_sheet=`

**iris saved as one Excel sheet for each species and read back with sheet="all"** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sheets | pandas ExcelWriter (openpyxl), read_excel(sheet_name=None) | 3 | 3 | relative 1e-12 | pass |
| rows | pandas ExcelWriter (openpyxl), read_excel(sheet_name=None) | 150 | 150 | relative 1e-12 | pass |
| total petal length | pandas ExcelWriter (openpyxl), read_excel(sheet_name=None) | 563.7 | 563.7 | relative 1e-12 | pass |
| columns | pandas ExcelWriter (openpyxl), read_excel(sheet_name=None) | 6 | 6 | relative 1e-12 | pass |

### `table.as_pandas`

**iris given back as pandas, from a Polars table** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars to_pandas | 150 | 150 | relative 1e-12 | pass |
| total sepal width | Polars to_pandas | 458.6 | 458.6 | relative 1e-12 | pass |

### `table.as_polars`

**iris given back as Polars, from a pandas table** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars from_pandas | 150 | 150 | relative 1e-12 | pass |
| total sepal width | Polars from_pandas | 458.6 | 458.6 | relative 1e-12 | pass |

### `table.remove_extra_spaces_in`

**the names of the 32 mtcars cars with extra spaces put in, cleaned** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| names as published | the published names themselves | 32 | 32 | exact | pass |

### `table.replace_values_in`

**warpbreaks: wool A renamed** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| wool A | pandas mask | 27 | 27 | exact | pass |
| B | pandas mask | 27 | 27 | exact | pass |

### `table.add_missing_dates`

**AirPassengers with three months taken out: the months put back** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas date_range and reindex | 144 | 144 | relative 1e-12 | pass |
| empty cells | pandas date_range and reindex | 3 | 3 | relative 1e-12 | pass |
| total | pandas date_range and reindex | 39905 | 39905 | relative 1e-12 | pass |

### `table.add_rolling_column`

**AirPassengers: the total of the last 12 months** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| last | pandas rolling(12).sum() | 5714 | 5714 | relative 1e-12 | pass |
| first full | pandas rolling(12).sum() | 1520 | 1520 | relative 1e-12 | pass |
| empty | pandas rolling(12).sum() | 11 | 11 | relative 1e-12 | pass |
| last | R | 5714 | 5714 | relative 1e-12 | pass |
| first full | R | 1520 | 1520 | relative 1e-12 | pass |
| empty | R | 11 | 11 | relative 1e-12 | pass |

### `table.show_rows_with_outliers`

**mtcars horsepower: outliers within each number of cylinders (Tukey)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows found | pandas quantile (linear) and Tukey's rule | 1 | 1 | exact | pass |
| sum of row numbers | pandas quantile (linear) and Tukey's rule | 30 | 30 | exact | pass |

### `sdata.table`

**Fisher's iris data read from a CSV file** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas read_csv(sep=None) | 150 | 150 | relative 1e-12 | pass |
| total petal width | pandas read_csv(sep=None) | 179.9 | 179.9 | relative 1e-12 | pass |

### `sdata.get_example`

**the practice table bcg has the shape of the published trials in R metadat (dat.bcg)** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| trials | R metadat dat.bcg (the published trials) | 13 | 13 | exact | pass |
| kinds of allocation | R metadat dat.bcg (the published trials) | 3 | 3 | exact | pass |
| earliest year | R metadat dat.bcg (the published trials) | 1948 | 1948 | exact | pass |
| latest year | R metadat dat.bcg (the published trials) | 1980 | 1980 | exact | pass |

Note: Since 2026-11-22 the practice table bcg is made up (DATA_LICENSES.md): it keeps the published trials' columns, number of trials, kinds of allocation and span of years, but not their counts. The counts themselves are checked against metadat in the combine_studies cases.

### `sdata.chart`

**the 36 Norris calibration points on a new chart** (real data; data: NIST Norris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | seaborn scatterplot | 36 | 36 | relative 1e-12 | pass |
| sum of y | seaborn scatterplot | 15112.9 | 15112.9 | relative 1e-12 | pass |

### `table.start_chart`

**Student's sleep data: a chart of drug 2 only, started from the table** (published; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bar | Student (1908) | 2.33 | 2.33 | within 0.005 (printed rounding) | pass |
| bar | seaborn barplot | 2.33 | 2.33 | relative 1e-09 | pass |
| bars | seaborn barplot | 1 | 1 | relative 1e-09 | pass |

### `sdata.numbers`

**Michelson's 100 measurements as numbers** (published; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 299.8524 | 299.8524 | within 1e-09 (printed rounding) | pass |
| mean | NumPy array | 299.8524 | 299.8524 | exact | pass |
| count | NumPy array | 100 | 100 | exact | pass |

### `sdata.number_grid`

**the 600 iris measurements as a grid of 150 rows and 4 columns** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy reshape (row after row) | 150 | 150 | relative 1e-12 | pass |
| total of column 3 | NumPy reshape (row after row) | 563.7 | 563.7 | relative 1e-12 | pass |
| row 2 column 1 | NumPy reshape (row after row) | 4.9 | 4.9 | relative 1e-12 | pass |

### `sdata.distribution`

**chance of at most 1.96 in the standard normal distribution** (published; data: standard normal table)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chance at most 1.96 | NIST/SEMATECH e-Handbook, table 1.3.6.7.1 | 0.97500210485178 | 0.975 | within 5e-06 (printed rounding) | pass |
| chance at most 1.96 | SciPy stats.norm.cdf | 0.97500210485178 | 0.97500210485178 | relative 1e-14 | pass |
| chance at most 1.96 | R | 0.97500210485178 | 0.97500210485178 | relative 1e-14 | pass |

Note: No data: the published value is the standard normal table (5 decimals).

### `sdata.make_random_numbers`

**random numbers shaped like Michelson's measurements (their average and standard deviation), seed 1** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | NumPy default_rng(1).normal | 299.879704796333 | 299.879704796333 | relative 1e-12 | pass |
| total | NumPy default_rng(1).normal | 29984.6583865972 | 29984.6583865972 | relative 1e-12 | pass |

Note: Random numbers have no published answer; the check is that the same seed gives NumPy's numbers.

### `sdata.make_run_of_dates`

**the 144 months of the AirPassengers series** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dates | the dates of the published series | 144 | 144 | exact | pass |
| same as the series | the dates of the published series | 144 | 144 | exact | pass |

### `nums.find_average`

**average of Michelson's 100 speed-of-light measurements** (published; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 299.8524 | 299.8524 | at least 9 digits (LRE 15.0) | pass |
| mean | NumPy nanmean | 299.8524 | 299.8524 | relative 1e-15 | pass |
| mean | R | 299.8524 | 299.8524 | relative 1e-14 | pass |

### `nums.find_percentile`

**90th percentile of Michelson's measurements** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| percentile 90 | NumPy nanpercentile (linear) | 299.96 | 299.96 | relative 1e-15 | pass |
| percentile 90 | R | 299.96 | 299.96 | relative 1e-14 | pass |

### `nums.keep_each_number_that`

**Michelson's measurements above 299.9** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| kept | NumPy boolean indexing | 23 | 23 | relative 1e-12 | pass |
| total | NumPy boolean indexing | 6899.09 | 6899.09 | relative 1e-12 | pass |
| kept | R | 23 | 23 | relative 1e-12 | pass |
| total | R | 6899.09 | 6899.09 | relative 1e-12 | pass |

### `dist.find_percentile`

**the 97.5th percentile of the standard normal distribution** (published; data: standard normal table)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| percentile 97.5 | NIST/SEMATECH e-Handbook, table 1.3.6.7.1 | 1.95996398454005 | 1.96 | within 0.005 (printed rounding) | pass |
| percentile 97.5 | SciPy stats.norm.ppf | 1.95996398454005 | 1.95996398454005 | relative 1e-14 | pass |
| percentile 97.5 | R | 1.95996398454005 | 1.95996398454005 | relative 1e-14 | pass |

Note: No data: the published value is the standard normal table.

### `table.compare_spreads_of`

**warpbreaks: do the breaks spread differently at the three tensions?** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| F | SciPy levene(center="median") | 2.81804766589445 | 2.81804766589445 | relative 1e-10 | pass |
| p-value | SciPy levene(center="median") | 0.0690494519399047 | 0.0690494519399047 | relative 1e-10 | pass |
| df 2 | SciPy levene(center="median") | 51 | 51 | relative 1e-10 | pass |
| F | R | 2.81804766589445 | 2.81804766589445 | relative 1e-10 | pass |
| p-value | R | 0.0690494519399047 | 0.0690494519399046 | relative 1e-10 | pass |
| df 2 | R | 51 | 51 | relative 1e-10 | pass |

Note: R's check is the Brown-Forsythe test written out: a one-way ANOVA of the distances from each group's median, which is what car::leveneTest() computes.

### `table.compare_percent_to`

**birthwt: is the percent of low birth weights 30 %?** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| low births | SciPy binomtest (Clopper-Pearson interval) | 59 | 59 | relative 1e-10 | pass |
| p-value | SciPy binomtest (Clopper-Pearson interval) | 0.750908765167366 | 0.750908765167366 | relative 1e-10 | pass |
| CI low | SciPy binomtest (Clopper-Pearson interval) | 24.6888559603843 | 24.6888559603843 | relative 1e-10 | pass |
| CI high | SciPy binomtest (Clopper-Pearson interval) | 38.3454564815498 | 38.3454564815498 | relative 1e-10 | pass |
| p-value | R | 0.750908765167366 | 0.750908765167366 | relative 1e-08 | pass |
| CI low | R | 24.6888559603843 | 24.6888559603843 | relative 1e-08 | pass |
| CI high | R | 38.3454564815498 | 38.3454564815498 | relative 1e-08 | pass |

### `table.add_principal_components`

**principal components of Fisher's four iris measurements** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| PC1 of row 1 | statsmodels PCA (SVD) | -2.25714117564812 | -2.25714117564812 | relative 1e-09 | pass |
| PC2 of row 1 | statsmodels PCA (SVD) | 0.478423832124898 | 0.478423832124899 | relative 1e-09 | pass |
| PC1 of row 150 | statsmodels PCA (SVD) | 0.957448488427992 | 0.957448488427994 | relative 1e-09 | pass |
| PC1 of row 1 | R | -2.25714117564812 | -2.25714117564812 | relative 1e-09 | pass |
| PC2 of row 1 | R | 0.478423832124898 | 0.478423832124899 | relative 1e-09 | pass |
| PC1 of row 150 | R | 0.957448488427992 | 0.957448488427993 | relative 1e-09 | pass |

### `table.add_predicted_column`

**mtcars: fuel use predicted from weight and horsepower** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | statsmodels OLS fittedvalues | 23.5723294033092 | 23.5723294033089 | relative 1e-10 | pass |
| last | statsmodels OLS fittedvalues | 22.9836494315066 | 22.9836494315063 | relative 1e-10 | pass |
| first | R | 23.5723294033092 | 23.5723294033093 | relative 1e-10 | pass |
| last | R | 22.9836494315066 | 22.9836494315066 | relative 1e-10 | pass |

### `save`

**mtcars: average fuel use for 4, 6 and 8 cylinders, saved as a picture** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| width (inches) | matplotlib savefig | 8 | 8 | relative 1e-12 | pass |
| height (inches) | matplotlib savefig | 6 | 6 | relative 1e-12 | pass |
| 4 cylinders | matplotlib savefig | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |
| 4 cylinders | R | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |

### `write_title_on_top`

**Fisher's iris: the average sepal length of each species, with a title** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| title as written | matplotlib set_title | 1 | 1 | relative 1e-12 | pass |
| setosa | matplotlib set_title | 5.006 | 5.006 | relative 1e-12 | pass |
| setosa | R | 5.006 | 5.006 | relative 1e-12 | pass |

### `label_x`

**mtcars: fuel use against weight, the x axis named** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| label as written | matplotlib set_xlabel | 1 | 1 | exact | pass |
| dots | matplotlib set_xlabel | 32 | 32 | exact | pass |

### `label_y`

**mtcars: fuel use against weight, the y axis named** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| label as written | matplotlib set_ylabel | 1 | 1 | exact | pass |
| dots | matplotlib set_ylabel | 32 | 32 | exact | pass |

### `rotate_labels_x`

**mtcars: the 32 car names under their bars, stood up** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| angle of the first name | matplotlib set_rotation | 90 | 90 | exact | pass |
| names | matplotlib set_rotation | 32 | 32 | exact | pass |
| names lined up by their right end | matplotlib set_rotation | 32 | 32 | exact | pass |

### `write_caption_at_bottom`

**Fisher's iris: bars with the source written under them** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| caption written | matplotlib annotate | 1 | 1 | relative 1e-12 | pass |
| virginica | matplotlib annotate | 5.552 | 5.552 | relative 1e-12 | pass |
| virginica | R | 5.552 | 5.552 | relative 1e-12 | pass |

### `use_font_size`

**Fisher's iris: bars with all their words in size 16** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| title | exact | 18.6666666666667 | 18.6666666666667 | within 1e-09 | pass |
| x label | exact | 17.3333333333333 | 17.3333333333333 | within 1e-09 | pass |
| tick labels | exact | 14.6666666666667 | 14.6666666666667 | within 1e-09 | pass |
| title | matplotlib rc_context | 18.6666666666667 | 18.6666666666667 | relative 1e-12 | pass |
| x label | matplotlib rc_context | 17.3333333333333 | 17.3333333333333 | relative 1e-12 | pass |
| tick labels | matplotlib rc_context | 14.6666666666667 | 14.6666666666667 | relative 1e-12 | pass |

Note: simplydata's normal sizes are 12 (text), 14 (title), 13 (axis labels) and 11 (tick labels); use_font_size(16) multiplies each by 16 / 12.

### `use_colour`

**Fisher's iris: every bar dark green** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| red | exact | 0 | 0 | within 0 | pass |
| green | exact | 100 | 100 | within 0 | pass |
| blue | exact | 0 | 0 | within 0 | pass |
| red | seaborn barplot(color=, saturation=1) | 0 | 0 | exact | pass |
| green | seaborn barplot(color=, saturation=1) | 100 | 100 | exact | pass |
| blue | seaborn barplot(color=, saturation=1) | 0 | 0 | exact | pass |

Note: darkgreen is #006400 in the CSS colour names matplotlib uses.

### `use_colours`

**warpbreaks: the two wools in navy and orange** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| navy bars | seaborn barplot(palette=) | 4 | 4 | exact | pass |
| orange bars | seaborn barplot(palette=) | 4 | 4 | exact | pass |
| first bar navy | seaborn barplot(palette=) | 1 | 1 | exact | pass |

### `put_legend_at_bottom`

**warpbreaks: lines of the two wools, the legend below** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| legends on the figure | matplotlib fig.legend | 1 | 1 | exact | pass |
| legends on the chart | matplotlib fig.legend | 0 | 0 | exact | pass |
| place | matplotlib fig.legend | 8 | 8 | exact | pass |
| entries | matplotlib fig.legend | 2 | 2 | exact | pass |

### `put_legend_on_left`

**warpbreaks: lines of the two wools, the legend on the left** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| legends on the figure | matplotlib fig.legend | 1 | 1 | exact | pass |
| legends on the chart | matplotlib fig.legend | 0 | 0 | exact | pass |
| place | matplotlib fig.legend | 6 | 6 | exact | pass |
| entries | matplotlib fig.legend | 2 | 2 | exact | pass |

### `order_x`

**warpbreaks: the tensions in the order high, medium, low** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first bar (H) | seaborn barplot(order=) | 21.6666666666667 | 21.6666666666667 | relative 1e-12 | pass |
| last bar (L) | seaborn barplot(order=) | 36.3888888888889 | 36.3888888888889 | relative 1e-12 | pass |
| first name | seaborn barplot(order=) | 1 | 1 | relative 1e-12 | pass |
| first bar (H) | R | 21.6666666666667 | 21.6666666666667 | relative 1e-12 | pass |
| last bar (L) | R | 36.3888888888889 | 36.3888888888889 | relative 1e-12 | pass |

### `use_style`

**Fisher's iris: bars in the presentation style** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| title | exact | 20 | 20 | within 0 | pass |
| x label | exact | 18 | 18 | within 0 | pass |
| tick labels | exact | 15 | 15 | within 0 | pass |
| title | matplotlib rc_context | 20 | 20 | exact | pass |
| x label | matplotlib rc_context | 18 | 18 | exact | pass |
| tick labels | matplotlib rc_context | 15 | 15 | exact | pass |

Note: The sizes of simplydata's presentation style: 20 for titles, 18 for axis labels, 15 for tick labels.

### `hide_legend`

**warpbreaks: lines of the two wools, without a legend** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| legends | matplotlib Legend.remove | 0 | 0 | exact | pass |
| lines with points | matplotlib Legend.remove | 2 | 2 | exact | pass |

### `draw_lines`

**warpbreaks: the average breaks at each tension, one line for each wool** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| wool A at L | seaborn lineplot(errorbar=None) | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| wool A at H | seaborn lineplot(errorbar=None) | 24.5555555555556 | 24.5555555555556 | relative 1e-12 | pass |
| wool B at M | seaborn lineplot(errorbar=None) | 28.7777777777778 | 28.7777777777778 | relative 1e-12 | pass |
| wool A at L | R | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| wool A at H | R | 24.5555555555556 | 24.5555555555556 | relative 1e-12 | pass |
| wool B at M | R | 28.7777777777778 | 28.7777777777778 | relative 1e-12 | pass |

### `draw_boxes`

**Fisher's iris: the sepal lengths of each species as boxes** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| boxes | seaborn boxplot | 3 | 3 | relative 1e-12 | pass |
| setosa median | seaborn boxplot | 5 | 5 | relative 1e-12 | pass |
| virginica median | seaborn boxplot | 6.5 | 6.5 | relative 1e-12 | pass |
| boxes | R | 3 | 3 | relative 1e-12 | pass |
| setosa median | R | 5 | 5 | relative 1e-12 | pass |
| virginica median | R | 6.5 | 6.5 | relative 1e-12 | pass |

Note: Each box is drawn as two whiskers, two caps, the median line and the far values, in that order, so the 5th line is the first median.

### `draw_all_dots`

**Fisher's iris: all 150 petal lengths as dots over boxes** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | seaborn swarmplot | 150 | 150 | relative 1e-12 | pass |
| total of the values | seaborn swarmplot | 563.7 | 563.7 | relative 1e-12 | pass |
| dark grey dots | seaborn swarmplot | 150 | 150 | relative 1e-12 | pass |
| dots | R | 150 | 150 | relative 1e-12 | pass |
| total of the values | R | 563.7 | 563.7 | relative 1e-12 | pass |

### `draw_violins`

**Fisher's iris: each violin stops at the longest sepal of its species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top of the setosa violin | exact | 5.8 | 5.8 | within 1e-12 | pass |
| top of the versicolor violin | exact | 7 | 7 | within 1e-12 | pass |
| top of the virginica violin | exact | 7.9 | 7.9 | within 1e-12 | pass |
| top of the setosa violin | seaborn violinplot(cut=0) | 5.8 | 5.8 | relative 1e-12 | pass |
| top of the versicolor violin | seaborn violinplot(cut=0) | 7 | 7 | relative 1e-12 | pass |
| top of the virginica violin | seaborn violinplot(cut=0) | 7.9 | 7.9 | relative 1e-12 | pass |
| top of the setosa violin | R | 5.8 | 5.8 | relative 1e-12 | pass |
| top of the versicolor violin | R | 7 | 7 | relative 1e-12 | pass |
| top of the virginica violin | R | 7.9 | 7.9 | relative 1e-12 | pass |

Note: The longest sepals in Fisher's table are 5.8, 7.0 and 7.9 cm.

### `show=`

**mtcars: the median fuel use for 4, 6 and 8 cylinders** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 4 cylinders | seaborn barplot(estimator="median") | 26 | 26 | relative 1e-12 | pass |
| 6 cylinders | seaborn barplot(estimator="median") | 19.7 | 19.7 | relative 1e-12 | pass |
| 8 cylinders | seaborn barplot(estimator="median") | 15.2 | 15.2 | relative 1e-12 | pass |
| 4 cylinders | R | 26 | 26 | relative 1e-12 | pass |
| 6 cylinders | R | 19.7 | 19.7 | relative 1e-12 | pass |
| 8 cylinders | R | 15.2 | 15.2 | relative 1e-12 | pass |

### `error=`

**mtcars: average fuel use with standard deviation bars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top of the 4-cylinder bar | seaborn barplot(errorbar="sd") | 31.1734640160578 | 31.1734640160578 | relative 1e-12 | pass |
| bottom of it | seaborn barplot(errorbar="sd") | 22.1538087112149 | 22.1538087112149 | relative 1e-12 | pass |
| top of the 4-cylinder bar | R | 31.1734640160578 | 31.1734640160578 | relative 1e-12 | pass |
| bottom of it | R | 22.1538087112149 | 22.1538087112149 | relative 1e-12 | pass |

### `write_numbers_on_bars`

**warpbreaks: the total breaks at each tension written on the bars** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers written | matplotlib bar_label | 3 | 3 | exact | pass |
| biggest | matplotlib bar_label | 655 | 655 | exact | pass |
| smallest | matplotlib bar_label | 390 | 390 | exact | pass |
| numbers written | R | 3 | 3 | exact | pass |
| biggest | R | 655 | 655 | exact | pass |
| smallest | R | 390 | 390 | exact | pass |

### `fit_line`

**mtcars: the straight line of fuel use on weight** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| line at the lightest car | SciPy linregress | 29.1989406778126 | 29.1989406778126 | relative 1e-12 | pass |
| line at the heaviest car | SciPy linregress | 8.29671235689424 | 8.29671235689424 | relative 1e-12 | pass |
| line at the lightest car | R | 29.1989406778126 | 29.1989406778126 | relative 1e-10 | pass |
| line at the heaviest car | R | 8.29671235689424 | 8.29671235689422 | relative 1e-10 | pass |

### `draw_qq_dots`

**Michelson's 100 measurements of the speed of light against the normal curve** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | SciPy probplot | 100 | 100 | relative 1e-12 | pass |
| slope of the line | SciPy probplot | 0.0796319729937114 | 0.0796319729937032 | relative 1e-12 | pass |
| smallest value | SciPy probplot | 299.62 | 299.62 | relative 1e-12 | pass |
| dots | R | 100 | 100 | relative 1e-12 | pass |
| smallest value | R | 299.62 | 299.62 | relative 1e-12 | pass |

Note: R's qqnorm() puts the dots at slightly different places (Blom's, not Filliben's), so only the count and the values themselves are checked against R.

### `set_range_y`

**mtcars: average fuel use on an axis from 0 to 40** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bottom of the y axis | exact | 0 | 0 | within 0 | pass |
| top of the y axis | exact | 40 | 40 | within 0 | pass |
| bottom of the y axis | matplotlib set_ylim | 0 | 0 | exact | pass |
| top of the y axis | matplotlib set_ylim | 40 | 40 | exact | pass |

### `draw_line_at_y`

**mtcars: a line at the average fuel use, 20.09 miles per gallon** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| line at | matplotlib axhline | 20.090625 | 20.090625 | exact | pass |
| label written | matplotlib axhline | 1 | 1 | exact | pass |
| line at | R | 20.090625 | 20.090625 | relative 1e-12 | pass |

### `shade_between_y`

**mtcars: the middle half of the fuel use shaded (the quartiles 15.425 and 22.8)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bottom of the band | matplotlib axhspan | 15.425 | 15.425 | relative 1e-12 | pass |
| height of the band | matplotlib axhspan | 7.375 | 7.375 | relative 1e-12 | pass |
| width (share of the chart) | matplotlib axhspan | 1 | 1 | relative 1e-12 | pass |
| bottom of the band | R | 15.425 | 15.425 | relative 1e-12 | pass |
| height of the band | R | 7.375 | 7.375 | relative 1e-12 | pass |

### `use_log_scale_y`

**warpbreaks: lines of the two wools on a log scale** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| log scale | matplotlib set_yscale("log") | 1 | 1 | relative 1e-12 | pass |
| bottom of the y axis | matplotlib set_yscale("log") | 17.52208300845 | 17.52208300845 | relative 1e-12 | pass |
| top of the y axis | matplotlib set_yscale("log") | 42.8898398220214 | 42.8898398220214 | relative 1e-12 | pass |

### `draw_line_at_x`

**mtcars: a line at a weight of 3,500 lb** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| line at | exact | 3.5 | 3.5 | within 0 | pass |
| line at | matplotlib axvline | 3.5 | 3.5 | exact | pass |
| label written | matplotlib axvline | 1 | 1 | exact | pass |

### `write_ticks_y_as`

**birthwt: the share of low birth weights for each race, written as percents** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| labels with % | matplotlib PercentFormatter | 10 | 10 | relative 1e-12 | pass |
| labels | matplotlib PercentFormatter | 10 | 10 | relative 1e-12 | pass |
| race 1 | matplotlib PercentFormatter | 0.239583333333333 | 0.239583333333333 | relative 1e-12 | pass |
| race 1 | R | 0.239583333333333 | 0.239583333333333 | relative 1e-12 | pass |

### `set_size`

**mtcars: a chart 12 cm wide and 9 cm high** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| width (inches) | exact | 4.7244094488189 | 4.7244094488189 | within 1e-12 | pass |
| height (inches) | exact | 3.54330708661417 | 3.54330708661417 | within 1e-12 | pass |
| width (inches) | matplotlib figsize | 4.7244094488189 | 4.7244094488189 | relative 1e-12 | pass |
| height (inches) | matplotlib figsize | 3.54330708661417 | 3.54330708661417 | relative 1e-12 | pass |

Note: An inch is 2.54 cm.

### `write_note`

**mtcars: the lightest car named on the chart** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| note written | matplotlib annotate | 1 | 1 | exact | pass |
| dots | matplotlib annotate | 32 | 32 | exact | pass |

### `draw_heatmap`

**warpbreaks: the average breaks for each wool and tension as coloured cells** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells | seaborn heatmap | 6 | 6 | relative 1e-12 | pass |
| wool A, tension L | seaborn heatmap | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| wool B, tension H | seaborn heatmap | 18.7777777777778 | 18.7777777777778 | relative 1e-12 | pass |
| numbers written | seaborn heatmap | 6 | 6 | relative 1e-12 | pass |
| cells | R | 6 | 6 | relative 1e-12 | pass |
| wool A, tension L | R | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| wool B, tension H | R | 18.7777777777778 | 18.7777777777778 | relative 1e-12 | pass |

### `draw_one_chart_for_each_group_in`

**Fisher's iris: one small chart of petal against sepal length for each species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| panels | exact | 3 | 3 | within 0 | pass |
| dots in the first | exact | 50 | 50 | within 0 | pass |
| dots in the last | exact | 50 | 50 | within 0 | pass |
| panels | matplotlib subplots(sharex, sharey) | 3 | 3 | exact | pass |
| dots in the first | matplotlib subplots(sharex, sharey) | 50 | 50 | exact | pass |
| dots in the last | matplotlib subplots(sharex, sharey) | 50 | 50 | exact | pass |
| width (inches) | matplotlib subplots(sharex, sharey) | 13 | 13 | exact | pass |

### `sdata.put_side_by_side`

**mtcars: bars and boxes of fuel use side by side, on the same y range** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| panels | matplotlib subfigures | 2 | 2 | relative 1e-12 | pass |
| width (inches) | matplotlib subfigures | 12 | 12 | relative 1e-12 | pass |
| top of the y axis | matplotlib subfigures | 35.075 | 35.075 | relative 1e-12 | pass |
| 4 cylinders | matplotlib subfigures | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |
| 4 cylinders | R | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |

### `sdata.put_one_above_other`

**Fisher's iris: dots above a histogram** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| panels | matplotlib subfigures | 2 | 2 | exact | pass |
| height (inches) | matplotlib subfigures | 9 | 9 | exact | pass |
| dots | matplotlib subfigures | 150 | 150 | exact | pass |
| bars | matplotlib subfigures | 10 | 10 | exact | pass |

### `sdata.put_in_rows_and_columns`

**Fisher's iris: histograms of the four measurements, two in a row** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| panels | exact | 4 | 4 | within 0 | pass |
| flowers in the last histogram | exact | 150 | 150 | within 0 | pass |
| panels | matplotlib subfigures | 4 | 4 | exact | pass |
| width (inches) | matplotlib subfigures | 12 | 12 | exact | pass |
| height (inches) | matplotlib subfigures | 9 | 9 | exact | pass |
| flowers in the last histogram | matplotlib subfigures | 150 | 150 | exact | pass |

### `sdata.draw_all_pairs`

**Fisher's iris: every measurement against every other, by species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| panels and diagonal axes | exact | 20 | 20 | within 0 | pass |
| dots in the second panel | exact | 150 | 150 | within 0 | pass |
| panels with dots | exact | 12 | 12 | within 0 | pass |
| panels and diagonal axes | seaborn scatterplot and kdeplot | 20 | 20 | exact | pass |
| dots in the second panel | seaborn scatterplot and kdeplot | 150 | 150 | exact | pass |
| panels with dots | seaborn scatterplot and kdeplot | 12 | 12 | exact | pass |

Note: 4 columns make 16 panels; each of the 4 on the diagonal also has a second y-axis for its curves.

### `add_second_y`

**mtcars: fuel use as a line and horsepower as bars on a second y-axis** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 4 cylinders | matplotlib twinx and bar | 82.6363636363636 | 82.6363636363636 | relative 1e-12 | pass |
| 6 cylinders | matplotlib twinx and bar | 122.285714285714 | 122.285714285714 | relative 1e-12 | pass |
| 8 cylinders | matplotlib twinx and bar | 209.214285714286 | 209.214285714286 | relative 1e-12 | pass |
| 4 cylinders | R | 82.6363636363636 | 82.6363636363636 | relative 1e-12 | pass |
| 6 cylinders | R | 122.285714285714 | 122.285714285714 | relative 1e-12 | pass |
| 8 cylinders | R | 209.214285714286 | 209.214285714286 | relative 1e-12 | pass |

### `animate`

**mtcars: average fuel use by cylinders, one picture for each number of gears (the last: 5)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 4 cylinders | seaborn barplot of the last frame | 28.2 | 28.2 | relative 1e-12 | pass |
| 8 cylinders | seaborn barplot of the last frame | 15.4 | 15.4 | relative 1e-12 | pass |
| named by its gear | seaborn barplot of the last frame | 1 | 1 | relative 1e-12 | pass |
| 4 cylinders | R | 28.2 | 28.2 | relative 1e-12 | pass |
| 8 cylinders | R | 15.4 | 15.4 | relative 1e-12 | pass |

Note: Shown as a still picture, an animated chart is its last frame.

### `fit_formula`

**Puromycin (treated): the Michaelis-Menten curve through the dots** (real data; data: Puromycin (treated))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| curve at the highest concentration | SciPy curve_fit | 200.968851192381 | 200.968851192381 | relative 1e-07 | pass |
| curve at the lowest | SciPy curve_fit | 50.5659785739787 | 50.5659785739787 | relative 1e-07 | pass |
| curve at the highest concentration | R | 200.968851192381 | 200.968851972334 | relative 1e-06 | pass |
| curve at the lowest | R | 50.5659785739787 | 50.5659777693516 | relative 1e-06 | pass |

### `table.find_trend_of`

**the level of Lake Huron, 1875-1972: Mann-Kendall test and Sen's slope** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope per year | SciPy theilslopes | -0.0251249999999999 | -0.0251249999999999 | relative 1e-10 | pass |
| slope 95 % CI low | SciPy theilslopes | -0.034929577464789 | -0.034929577464789 | relative 1e-10 | pass |
| slope per year | R | -0.0251249999999999 | -0.0251249999999999 | relative 1e-09 | pass |
| slope 95 % CI low | R | -0.034929577464789 | -0.034929577464789 | relative 1e-09 | pass |
| z | R | -5.15982522603039 | -5.15982522603039 | relative 1e-09 | pass |
| p-value | R | 2.47180483772576e-07 | 2.47180483772576e-07 | relative 1e-09 | pass |

Note: The years run 1875 to 1972 without a gap, so the slope per year equals R's slope per reading.

### `table.find_each_peak_that`

**the air passengers, 1949-1960: the peaks at least 6 months apart** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| highest peak | Box & Jenkins (1976): July 1960 | 622 | 622 | within 0 (printed rounding) | pass |
| peaks | SciPy find_peaks(distance=6) | 15 | 15 | exact | pass |
| first peak (row) | SciPy find_peaks(distance=6) | 7 | 7 | exact | pass |
| highest peak | SciPy find_peaks(distance=6) | 622 | 622 | exact | pass |

### `table.add_nmds`

**the dune meadows (vegan): an NMDS map of the 20 plots** (real data; data: dune (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| NMDS1 of plot 1 | R | -0.840545506144764 | -0.840545506144764 | relative 1e-09 | pass |
| NMDS2 of plot 1 | R | -0.715827761318819 | -0.715827761318819 | relative 1e-09 | pass |
| NMDS1 of plot 20 | R | 1.04240523654323 | 1.04240523654323 | relative 1e-09 | pass |

### `table.compare_matched_columns`

**rounding first base: 22 players, three routes (Friedman test)** (published; data: rounding first base)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | R friedman.test help (Hollander & Wolfe 1973) | 11.1428571428571 | 11.143 | within 0.0005 (printed rounding) | pass |
| p-value | R friedman.test help (Hollander & Wolfe 1973) | 0.00380504077551138 | 0.003805 | within 5e-07 (printed rounding) | pass |
| chi-square | SciPy friedmanchisquare | 11.1428571428571 | 11.1428571428571 | relative 1e-12 | pass |
| degrees of freedom | SciPy friedmanchisquare | 2 | 2 | relative 1e-12 | pass |
| p-value | SciPy friedmanchisquare | 0.00380504077551138 | 0.00380504077551138 | relative 1e-12 | pass |
| chi-square | R | 11.1428571428571 | 11.1428571428571 | relative 1e-10 | pass |
| degrees of freedom | R | 2 | 2 | relative 1e-10 | pass |
| p-value | R | 0.00380504077551138 | 0.00380504077551136 | relative 1e-10 | pass |

### `show`

**mtcars: average fuel use for 4, 6 and 8 cylinders, shown** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 4 cylinders | matplotlib plt.show | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |
| 8 cylinders | matplotlib plt.show | 15.1 | 15.1 | relative 1e-12 | pass |
| 4 cylinders | R | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |
| 8 cylinders | R | 15.1 | 15.1 | relative 1e-12 | pass |

### `draw_area`

**Seatbelts: UK drivers killed in each month of the year, averaged over 1969-84** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| January | matplotlib fill_between | 120.8125 | 120.8125 | relative 1e-12 | pass |
| December | matplotlib fill_between | 158.25 | 158.25 | relative 1e-12 | pass |
| months | matplotlib fill_between | 12 | 12 | relative 1e-12 | pass |
| January | R | 120.8125 | 120.8125 | relative 1e-12 | pass |
| December | R | 158.25 | 158.25 | relative 1e-12 | pass |
| months | R | 12 | 12 | relative 1e-12 | pass |

### `draw_pie`

**mtcars: the share of cars with 4, 6 and 8 cylinders** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slices | matplotlib pie | 3 | 3 | exact | pass |
| largest share (%) | matplotlib pie | 44 | 44 | exact | pass |
| slices | R | 3 | 3 | exact | pass |
| largest share (%) | R | 44 | 44 | exact | pass |

### `draw_polar`

**Seatbelts: drivers killed by month, round the year like a clock** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | matplotlib polar axes | 192 | 192 | relative 1e-12 | pass |
| angle of the first dot | matplotlib polar axes | 0.523598775598299 | 0.523598775598299 | relative 1e-12 | pass |
| zero at | matplotlib polar axes | 1.5707963267949 | 1.5707963267949 | relative 1e-12 | pass |
| direction | matplotlib polar axes | -1 | -1 | relative 1e-12 | pass |
| dots | R | 192 | 192 | relative 1e-12 | pass |
| angle of the first dot | R | 0.523598775598299 | 0.523598775598299 | relative 1e-12 | pass |
| zero at | R | 1.5707963267949 | 1.5707963267949 | relative 1e-12 | pass |
| direction | R | -1 | -1 | relative 1e-12 | pass |

### `draw_contour`

**mtcars: fuel use over weight and horsepower, a scattered map joined up** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bands | SciPy griddata + matplotlib contourf | 21 | 21 | relative 1e-12 | pass |
| scale low | SciPy griddata + matplotlib contourf | 10 | 10 | relative 1e-12 | pass |
| scale high | SciPy griddata + matplotlib contourf | 35 | 35 | relative 1e-12 | pass |

Note: The bands and the lines between them both count among the shapes.

### `draw_surface`

**mtcars: fuel use over weight and horsepower as a 3D surface** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| pieces | SciPy griddata + matplotlib plot_surface | 1362 | 1362 | relative 1e-12 | pass |
| highest piece | SciPy griddata + matplotlib plot_surface | 33.1369568013048 | 33.1369568013048 | relative 1e-12 | pass |
| lowest piece | SciPy griddata + matplotlib plot_surface | 10.4623295241982 | 10.4623295241982 | relative 1e-12 | pass |

### `draw_dots_3d`

**Fisher's iris: sepal length, sepal width and petal length in 3D** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | matplotlib 3D scatter | 150 | 150 | relative 1e-12 | pass |
| groups | matplotlib 3D scatter | 3 | 3 | relative 1e-12 | pass |
| z of the first dot | matplotlib 3D scatter | 1.4 | 1.4 | relative 1e-12 | pass |
| dots | R | 150 | 150 | relative 1e-12 | pass |
| groups | R | 3 | 3 | relative 1e-12 | pass |
| z of the first dot | R | 1.4 | 1.4 | relative 1e-12 | pass |

### `draw_band`

**Lake Huron: the level each year, with a band 1 foot either side** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| lowest edge | matplotlib fill_between | 574.96 | 574.96 | relative 1e-12 | pass |
| highest edge | matplotlib fill_between | 582.86 | 582.86 | relative 1e-12 | pass |
| lowest edge | R | 574.96 | 574.96 | relative 1e-12 | pass |
| highest edge | R | 582.86 | 582.86 | relative 1e-12 | pass |

### `draw_map_of_empty_cells`

**NHANES (mice): where the 27 empty cells of 25 people are** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| empty cells | pandas isna + matplotlib imshow | 27 | 27 | exact | pass |
| rows | pandas isna + matplotlib imshow | 25 | 25 | exact | pass |
| bmi empty | pandas isna + matplotlib imshow | 9 | 9 | exact | pass |
| empty cells | R | 27 | 27 | exact | pass |
| rows | R | 25 | 25 | exact | pass |
| bmi empty | R | 9 | 9 | exact | pass |

### `sticks`

**Lake Huron: the level of each year as a stick** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sticks | matplotlib vlines | 98 | 98 | relative 1e-12 | pass |
| last height | matplotlib vlines | 579.96 | 579.96 | relative 1e-12 | pass |
| width | matplotlib vlines | 1.5 | 1.5 | relative 1e-12 | pass |
| sticks | R | 98 | 98 | relative 1e-12 | pass |
| last height | R | 579.96 | 579.96 | relative 1e-12 | pass |

### `draw_error_bars`

**Fisher's iris: sepal length of each species with its standard deviation** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| setosa standard deviation | pandas std + matplotlib errorbar | 0.352489687213452 | 0.352489687213452 | relative 1e-12 | pass |
| virginica standard deviation | pandas std + matplotlib errorbar | 0.635879593274432 | 0.635879593274432 | relative 1e-12 | pass |
| setosa standard deviation | R | 0.352489687213452 | 0.352489687213451 | relative 1e-12 | pass |
| virginica standard deviation | R | 0.635879593274432 | 0.635879593274432 | relative 1e-12 | pass |

### `fit_curve`

**mtcars: a curve with one bend through fuel use against weight** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| at the lightest car | NumPy Polynomial.fit | 32.3671767556685 | 32.3671767556684 | relative 1e-09 | pass |
| at the heaviest car | NumPy Polynomial.fit | 11.8089767010943 | 11.8089767010943 | relative 1e-09 | pass |
| at the lightest car | R | 32.3671767556685 | 32.3671767556684 | relative 1e-09 | pass |
| at the heaviest car | R | 11.8089767010943 | 11.8089767010943 | relative 1e-09 | pass |

### `fit_distribution`

**Michelson's 100 speeds of light: a normal curve fitted over the histogram** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| curve at the smallest value | SciPy norm.fit (maximum likelihood) | 0.289033106728029 | 0.289033106728029 | relative 1e-09 | pass |
| curve at the largest value | SciPy norm.fit (maximum likelihood) | 0.495394920832253 | 0.495394920832253 | relative 1e-09 | pass |
| curve at the smallest value | R | 0.289033106728029 | 0.28903310672792 | relative 1e-09 | pass |
| curve at the largest value | R | 0.495394920832253 | 0.495394920832065 | relative 1e-09 | pass |

Note: Maximum likelihood: the standard deviation divides by n (as R MASS::fitdistr()).

### `draw_curve`

**Fisher's iris: a normal curve (average 5.8, standard deviation 0.8) over the sepal lengths** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| curve at the smallest value | SciPy norm.pdf | 4.64307361830172 | 4.64307361830172 | relative 1e-09 | pass |
| curve at the largest value | SciPy norm.pdf | 0.858882257786118 | 0.858882257786118 | relative 1e-09 | pass |
| curve at the smallest value | R | 4.64307361830172 | 4.6430736183017 | relative 1e-09 | pass |
| curve at the largest value | R | 0.858882257786118 | 0.85888225778612 | relative 1e-09 | pass |

### `draw_density`

**Fisher's iris: a density curve of petal length for each species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| curves | seaborn kdeplot(common_norm=False) | 3 | 3 | relative 1e-12 | pass |
| peak of setosa | seaborn kdeplot(common_norm=False) | 2.38267851730682 | 2.38267851730682 | relative 1e-12 | pass |
| peak of virginica | seaborn kdeplot(common_norm=False) | 0.63822195173954 | 0.63822195173954 | relative 1e-12 | pass |

Note: Each curve has area 1 on its own; R's density() uses another bandwidth rule, so R is not asked.

### `draw_count_bars`

**mtcars: how many cars have 3, 4 and 5 gears** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 3 gears | seaborn countplot | 15 | 15 | exact | pass |
| 4 gears | seaborn countplot | 12 | 12 | exact | pass |
| 5 gears | seaborn countplot | 5 | 5 | exact | pass |
| 3 gears | R | 15 | 15 | exact | pass |
| 4 gears | R | 12 | 12 | exact | pass |
| 5 gears | R | 5 | 5 | exact | pass |

### `draw_side_histograms`

**Fisher's iris: sepal length against width, with a histogram on each side** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| small charts | matplotlib inset_axes + hist | 2 | 2 | relative 1e-12 | pass |
| corners of the top histogram | matplotlib inset_axes + hist | 37 | 37 | relative 1e-12 | pass |
| height of the top histogram | matplotlib inset_axes + hist | 28 | 28 | relative 1e-12 | pass |

### `draw_cumulative_share`

**warpbreaks: the share of looms with 30 breaks or fewer, for each wool** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| wool A at 30 or fewer | seaborn ecdfplot | 0.666666666666667 | 0.666666666666667 | relative 1e-12 | pass |
| wool B at 30 or fewer | seaborn ecdfplot | 0.777777777777778 | 0.777777777777778 | relative 1e-12 | pass |
| wool A at 30 or fewer | R | 0.666666666666667 | 0.666666666666667 | relative 1e-12 | pass |
| wool B at 30 or fewer | R | 0.777777777777778 | 0.777777777777778 | relative 1e-12 | pass |

### `draw_line_with_slope`

**mtcars: a line falling 5 miles per gallon for each 1000 lb, through (3, 20)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | matplotlib axline | -5 | -5 | exact | pass |
| through x | matplotlib axline | 3 | 3 | exact | pass |
| through y | matplotlib axline | 20 | 20 | exact | pass |
| dots | matplotlib axline | 32 | 32 | exact | pass |

### `shade_between_x`

**Lake Huron: the 1930s shaded behind the yearly levels** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| band starts | matplotlib axvspan | 1930 | 1930 | exact | pass |
| band width | matplotlib axvspan | 10 | 10 | exact | pass |
| years drawn | matplotlib axvspan | 98 | 98 | exact | pass |
| years drawn | R | 98 | 98 | exact | pass |

### `write_names_on_dots`

**mtcars: the names of the seven 6-cylinder cars next to their dots** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| names at their own dot | pandas: the 6-cylinder cars | 7 | 7 | exact | pass |
| names written | pandas: the 6-cylinder cars | 7 | 7 | exact | pass |
| names written | R | 7 | 7 | exact | pass |

Note: Where each name goes is simplydata's own search; the case checks every car is named at its dot.

### `use_font`

**Fisher's iris: bars with every word in DejaVu Serif** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| words in DejaVu Serif | matplotlib rc_context(font.family) | 3 | 3 | relative 1e-12 | pass |
| setosa | matplotlib rc_context(font.family) | 5.006 | 5.006 | relative 1e-12 | pass |
| setosa | R | 5.006 | 5.006 | relative 1e-12 | pass |

### `set_range_x`

**mtcars: fuel use against weight, the x-axis from 0** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x from | matplotlib set_xlim | 0 | 0 | relative 1e-12 | pass |
| x to | matplotlib set_xlim | 5.61955 | 5.61955 | relative 1e-12 | pass |
| x from | R | 0 | 0 | relative 1e-12 | pass |
| x to | R | 5.61955 | 5.61955 | relative 1e-12 | pass |

Note: The top end stays where matplotlib put it: 5 % of the range past the heaviest car.

### `use_log_scale_x`

**mtcars: fuel use against horsepower on a log scale** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| log x | matplotlib set_xscale | 1 | 1 | relative 1e-12 | pass |
| x from | matplotlib set_xscale | 47.3752233507531 | 47.3752233507531 | relative 1e-12 | pass |
| x to | matplotlib set_xscale | 367.702751943293 | 367.702751943293 | relative 1e-12 | pass |
| log x | R | 1 | 1 | relative 1e-12 | pass |
| x from | R | 47.3752233507531 | 47.375223350753 | relative 1e-12 | pass |
| x to | R | 367.702751943293 | 367.702751943292 | relative 1e-12 | pass |

Note: On a log scale matplotlib adds 5 % of the range of log10(x) at each end.

### `put_ticks_x`

**Fisher's iris: ticks under setosa and virginica only** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first tick | matplotlib set_xticks | 0 | 0 | exact | pass |
| second tick | matplotlib set_xticks | 2 | 2 | exact | pass |
| ticks | matplotlib set_xticks | 2 | 2 | exact | pass |
| first name setosa | matplotlib set_xticks | 1 | 1 | exact | pass |

### `put_ticks_y`

**mtcars: fuel use bars with ticks at 0, 10, 20 and 30** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| ticks | matplotlib set_yticks | 4 | 4 | relative 1e-12 | pass |
| top tick | matplotlib set_yticks | 30 | 30 | relative 1e-12 | pass |
| 4 cylinders | matplotlib set_yticks | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |
| 4 cylinders | R | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |

### `rotate_labels_y`

**mtcars: the 32 car names beside sideways bars, turned 30 degrees** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| angle | matplotlib set_rotation | 30 | 30 | exact | pass |
| names | matplotlib set_rotation | 32 | 32 | exact | pass |
| names turned about their end | matplotlib set_rotation | 32 | 32 | exact | pass |
| names | R | 32 | 32 | exact | pass |

### `write_ticks_x_as`

**birthwt: birth weights (grams) written with a comma for thousands** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| names with a comma | matplotlib StrMethodFormatter | 6 | 6 | exact | pass |
| names with decimals | matplotlib StrMethodFormatter | 0 | 0 | exact | pass |
| names | matplotlib StrMethodFormatter | 7 | 7 | exact | pass |

### `flip_x`

**stackloss: stack loss against air flow, the x-axis turned round** (real data; data: stackloss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| left or bottom end | matplotlib invert_xaxis | 81.5 | 81.5 | relative 1e-12 | pass |
| right or top end | matplotlib invert_xaxis | 48.5 | 48.5 | relative 1e-12 | pass |

### `flip_y`

**stackloss: stack loss against air flow, the y-axis turned round** (real data; data: stackloss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| left or bottom end | matplotlib invert_yaxis | 43.75 | 43.75 | relative 1e-12 | pass |
| right or top end | matplotlib invert_yaxis | 5.25 | 5.25 | relative 1e-12 | pass |

### `use_colour_scale`

**warpbreaks: average breaks for each wool and tension in magma colours** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| magma | seaborn heatmap(cmap=) | 1 | 1 | relative 1e-12 | pass |
| scale low | seaborn heatmap(cmap=) | 18.7777777777778 | 18.7777777777778 | relative 1e-12 | pass |
| scale high | seaborn heatmap(cmap=) | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| wool A, tension L | seaborn heatmap(cmap=) | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| magma | R | 1 | 1 | relative 1e-12 | pass |
| scale low | R | 18.7777777777778 | 18.7777777777778 | relative 1e-12 | pass |
| scale high | R | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| wool A, tension L | R | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |

### `show_grid`

**Fisher's iris: sepal length against width, grid lines both ways** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| lines along x | matplotlib grid(True, axis="both") | 1 | 1 | exact | pass |
| lines along y | matplotlib grid(True, axis="both") | 1 | 1 | exact | pass |
| dots | matplotlib grid(True, axis="both") | 150 | 150 | exact | pass |
| dots | R | 150 | 150 | exact | pass |

### `hide_grid`

**Fisher's iris: sepal length against width, no grid lines** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| lines along x | matplotlib grid(False) | 0 | 0 | exact | pass |
| lines along y | matplotlib grid(False) | 0 | 0 | exact | pass |
| dots | matplotlib grid(False) | 150 | 150 | exact | pass |
| dots | R | 150 | 150 | exact | pass |

### `put_legend_at_top`

**warpbreaks: lines of the two wools, the legend above** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| legends on the figure | matplotlib fig.legend | 1 | 1 | exact | pass |
| place | matplotlib fig.legend | 9 | 9 | exact | pass |
| columns | matplotlib fig.legend | 2 | 2 | exact | pass |
| entries | matplotlib fig.legend | 2 | 2 | exact | pass |

### `put_legend_on_right`

**warpbreaks: lines of the two wools, the legend on the right** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| legends on the figure | matplotlib fig.legend | 1 | 1 | exact | pass |
| place | matplotlib fig.legend | 7 | 7 | exact | pass |
| columns | matplotlib fig.legend | 1 | 1 | exact | pass |
| entries | matplotlib fig.legend | 2 | 2 | exact | pass |

### `show_legend`

**warpbreaks: lines of the two wools, the legend hidden and shown again** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| legends | seaborn lineplot legend | 1 | 1 | exact | pass |
| entries | seaborn lineplot legend | 2 | 2 | exact | pass |
| entries | R | 2 | 2 | exact | pass |

### `label_legend`

**Fisher's iris: the legend of the species named "Iris species"** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| named as asked | matplotlib Legend.set_title | 1 | 1 | exact | pass |
| entries | matplotlib Legend.set_title | 3 | 3 | exact | pass |
| entries | R | 3 | 3 | exact | pass |

### `label_colour_bar`

**mtcars: the colour bar of a fuel-use map named "Miles per gallon"** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| named as asked | matplotlib Colorbar.set_label | 1 | 1 | relative 1e-12 | pass |
| scale low | matplotlib Colorbar.set_label | 10 | 10 | relative 1e-12 | pass |

### `order_y`

**Fisher's iris: sideways bars, virginica at the top** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top name virginica | seaborn barplot(order=) | 1 | 1 | relative 1e-12 | pass |
| bar at the top | seaborn barplot(order=) | 2.974 | 2.974 | relative 1e-12 | pass |
| top name virginica | R | 1 | 1 | relative 1e-12 | pass |
| bar at the top | R | 2.974 | 2.974 | relative 1e-12 | pass |

### `order_legend`

**warpbreaks: bars of the two wools, wool B first** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first entry B | seaborn barplot(hue_order=) | 1 | 1 | relative 1e-12 | pass |
| first bar (wool B, tension L) | seaborn barplot(hue_order=) | 28.2222222222222 | 28.2222222222222 | relative 1e-12 | pass |
| first entry B | R | 1 | 1 | relative 1e-12 | pass |
| first bar (wool B, tension L) | R | 28.2222222222222 | 28.2222222222222 | relative 1e-12 | pass |

### `add_zoom_box`

**mtcars: fuel use against weight, with the cars of 2.5 to 3.5 (1000 lb) close up** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| box from x | matplotlib inset_axes | 2.5 | 2.5 | relative 1e-12 | pass |
| box to x | matplotlib inset_axes | 3.5 | 3.5 | relative 1e-12 | pass |
| dots in view | matplotlib inset_axes | 13 | 13 | relative 1e-12 | pass |
| box width (share of the chart) | matplotlib inset_axes | 0.39 | 0.39 | relative 1e-12 | pass |
| dots in view | R | 13 | 13 | exact | pass |

### `forest_plot`

**warpbreaks: Tukey's differences between the three tensions, as a forest plot** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| smallest difference | statsmodels pairwise_tukeyhsd | 4.72222222222222 | 4.72222222222222 | relative 1e-09 | pass |
| largest difference | statsmodels pairwise_tukeyhsd | 14.7222222222222 | 14.7222222222222 | relative 1e-09 | pass |
| line of no effect at | statsmodels pairwise_tukeyhsd | 0 | 0 | relative 1e-09 | pass |
| rows | statsmodels pairwise_tukeyhsd | 3 | 3 | relative 1e-09 | pass |
| smallest difference | R | 4.72222222222222 | 4.72222222222222 | relative 1e-09 | pass |
| largest difference | R | 14.7222222222222 | 14.7222222222222 | relative 1e-09 | pass |
| rows | R | 3 | 3 | relative 1e-09 | pass |

Note: The dots of the forest plot are the differences between the averages of each pair of tensions.

### `nums.show`

**all 100 of Michelson's measurements shown** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers shown | pandas (every value) | 100 | 100 | relative 1e-12 | pass |
| total shown | pandas (every value) | 29985.24 | 29985.24 | relative 1e-12 | pass |
| numbers shown | R | 100 | 100 | relative 1e-12 | pass |
| total shown | R | 29985.24 | 29985.24 | relative 1e-12 | pass |

### `nums.show_first_numbers`

**the first 5 months of AirPassengers shown** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers shown | pandas head | 5 | 5 | exact | pass |
| total shown | pandas head | 612 | 612 | exact | pass |
| total shown | R | 612 | 612 | exact | pass |

### `nums.show_last_numbers`

**the 12 months of 1960 in AirPassengers shown** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers shown | pandas tail | 12 | 12 | exact | pass |
| total shown | pandas tail | 5714 | 5714 | exact | pass |
| total shown | R | 5714 | 5714 | exact | pass |

### `nums.get_number_at`

**the first and the last month of AirPassengers, counting from 1** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| month 1 | NumPy [ ] (from 0) | 112 | 112 | exact | pass |
| month 144 | NumPy [ ] (from 0) | 432 | 432 | exact | pass |
| last | NumPy [ ] (from 0) | 432 | 432 | exact | pass |
| month 1 | R | 112 | 112 | exact | pass |
| month 144 | R | 432 | 432 | exact | pass |

### `nums.count`

**NHANES body mass index: 25 places, empty ones included** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count | NumPy size | 25 | 25 | exact | pass |
| count | R | 25 | 25 | exact | pass |

### `nums.count_empty_numbers`

**the empty cells of NHANES body mass index** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| empty | NumPy isnan | 9 | 9 | exact | pass |
| empty | R | 9 | 9 | exact | pass |

### `nums.add`

**1 added to NHANES body mass index: the empty cells stay empty** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy + | 441 | 441 | relative 1e-12 | pass |
| empty | NumPy + | 9 | 9 | relative 1e-12 | pass |
| total | R | 441 | 441 | relative 1e-12 | pass |
| empty | R | 9 | 9 | relative 1e-12 | pass |

### `nums.subtract`

**Michelson's measurements less 299 (thousand km/s)** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy - | 85.24 | 85.24 | relative 1e-12 | pass |
| first | NumPy - | 0.850000000000023 | 0.850000000000023 | relative 1e-12 | pass |
| total | R | 85.24 | 85.24 | relative 1e-12 | pass |
| first | R | 0.850000000000023 | 0.850000000000023 | relative 1e-12 | pass |

### `nums.times`

**mtcars weights from thousands of pounds to pounds** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total pounds | NumPy * | 102952 | 102952 | relative 1e-12 | pass |
| heaviest | NumPy * | 5424 | 5424 | relative 1e-12 | pass |
| total pounds | R | 102952 | 102952 | relative 1e-12 | pass |
| heaviest | R | 5424 | 5424 | relative 1e-12 | pass |

### `nums.divide_by`

**mtcars horsepower per thousand pounds, car by car** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy / | 1450.70914531099 | 1450.70914531099 | relative 1e-12 | pass |
| biggest | NumPy / | 93.8375350140056 | 93.8375350140056 | relative 1e-12 | pass |
| empty | NumPy / | 0 | 0 | relative 1e-12 | pass |
| total | R | 1450.70914531099 | 1450.70914531099 | relative 1e-12 | pass |
| biggest | R | 93.8375350140056 | 93.8375350140056 | relative 1e-12 | pass |

### `nums.raise_to_power`

**iris sepal lengths squared** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy power | 5223.85 | 5223.85 | relative 1e-12 | pass |
| total | R | 5223.85 | 5223.85 | relative 1e-12 | pass |

### `nums.take_square_root`

**square roots of mtcars engine sizes** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy sqrt | 468.214849084027 | 468.214849084027 | relative 1e-12 | pass |
| first | NumPy sqrt | 12.6491106406735 | 12.6491106406735 | relative 1e-12 | pass |
| total | R | 468.214849084027 | 468.214849084027 | relative 1e-12 | pass |
| first | R | 12.6491106406735 | 12.6491106406735 | relative 1e-12 | pass |

### `nums.take_absolute_value`

**how far each of Michelson's measurements lies from their average** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total distance | NumPy abs | 6.1239999999998 | 6.1239999999998 | relative 1e-12 | pass |
| biggest | NumPy abs | 0.232399999999984 | 0.232399999999984 | relative 1e-12 | pass |
| total distance | R | 6.1239999999998 | 6.1239999999998 | relative 1e-12 | pass |
| biggest | R | 0.232399999999984 | 0.232399999999984 | relative 1e-12 | pass |

### `nums.round_to`

**mtcars miles per gallon to whole numbers: 21.5 and 15.5 go to the even neighbour** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy round (halves to even) | 640 | 640 | exact | pass |
| Toyota Corona (21.5) | NumPy round (halves to even) | 22 | 22 | exact | pass |
| total | R | 640 | 640 | exact | pass |
| Toyota Corona (21.5) | R | 22 | 22 | exact | pass |

### `nums.take_log`

**natural logs of the 144 AirPassengers months** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy log | 798.073338028589 | 798.073338028589 | relative 1e-12 | pass |
| first | NumPy log | 4.71849887129509 | 4.71849887129509 | relative 1e-12 | pass |
| total | R | 798.073338028589 | 798.07333802859 | relative 1e-12 | pass |
| first | R | 4.71849887129509 | 4.71849887129509 | relative 1e-12 | pass |

### `nums.take_exp`

**e to the power of each iris petal width** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy exp | 649.475073422466 | 649.475073422466 | relative 1e-12 | pass |
| total | R | 649.475073422466 | 649.475073422466 | relative 1e-12 | pass |

### `nums.turn_into_running_total`

**AirPassengers added up month by month** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| after 12 months | pandas cumsum | 1520 | 1520 | exact | pass |
| after 144 months | pandas cumsum | 40363 | 40363 | exact | pass |
| after 12 months | R | 1520 | 1520 | exact | pass |
| after 144 months | R | 40363 | 40363 | exact | pass |

### `nums.remove_each_number_that`

**NHANES body mass index below 25 removed: the empty cells stay** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| left | NumPy boolean indexing | 19 | 19 | relative 1e-12 | pass |
| empty left | NumPy boolean indexing | 9 | 9 | relative 1e-12 | pass |
| total | NumPy boolean indexing | 290.8 | 290.8 | relative 1e-12 | pass |
| left | R | 19 | 19 | relative 1e-12 | pass |
| empty left | R | 9 | 9 | relative 1e-12 | pass |
| total | R | 290.8 | 290.8 | relative 1e-12 | pass |

### `nums.keep_first_numbers`

**the 12 months of 1949 in AirPassengers** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| kept | NumPy [:12] | 12 | 12 | exact | pass |
| total | NumPy [:12] | 1520 | 1520 | exact | pass |
| total | R | 1520 | 1520 | exact | pass |

### `nums.keep_last_numbers`

**the 12 months of 1960 in AirPassengers** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| kept | NumPy [-12:] | 12 | 12 | exact | pass |
| total | NumPy [-12:] | 5714 | 5714 | exact | pass |
| total | R | 5714 | 5714 | exact | pass |

### `nums.keep_random_numbers`

**10 of Michelson's measurements picked at random (seed 1)** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| kept | NumPy default_rng choice, kept in order | 10 | 10 | relative 1e-12 | pass |
| total | NumPy default_rng choice, kept in order | 2998.46 | 2998.46 | relative 1e-12 | pass |
| first kept | NumPy default_rng choice, kept in order | 300.07 | 300.07 | relative 1e-12 | pass |

### `nums.remove_duplicate_numbers`

**the different values among Michelson's measurements, in first-seen order** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| different | pandas drop_duplicates | 30 | 30 | relative 1e-12 | pass |
| total | pandas drop_duplicates | 8995.56 | 8995.56 | relative 1e-12 | pass |
| third | pandas drop_duplicates | 299.9 | 299.9 | relative 1e-12 | pass |
| different | R | 30 | 30 | relative 1e-12 | pass |
| total | R | 8995.56 | 8995.56 | relative 1e-12 | pass |
| third | R | 299.9 | 299.9 | relative 1e-12 | pass |

### `nums.remove_empty_numbers`

**NHANES cholesterol without its empty cells** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| left | NumPy isnan | 15 | 15 | relative 1e-12 | pass |
| total | NumPy isnan | 2871 | 2871 | relative 1e-12 | pass |
| left | R | 15 | 15 | relative 1e-12 | pass |
| total | R | 2871 | 2871 | relative 1e-12 | pass |

### `nums.keep_numbers_by_position`

**months 13 to 24 (1950) of AirPassengers** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| kept | NumPy [12:24] | 12 | 12 | exact | pass |
| total | NumPy [12:24] | 1676 | 1676 | exact | pass |
| kept | R | 12 | 12 | exact | pass |
| total | R | 1676 | 1676 | exact | pass |

### `nums.remove_numbers_by_position`

**AirPassengers without its first year** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| left | NumPy delete | 132 | 132 | exact | pass |
| total | NumPy delete | 38843 | 38843 | exact | pass |
| left | R | 132 | 132 | exact | pass |
| total | R | 38843 | 38843 | exact | pass |

### `nums.replace_each_number_that`

**NHANES body mass index above 30 set to 30: the empty cells stay empty** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy where | 416.4 | 416.4 | relative 1e-12 | pass |
| empty | NumPy where | 9 | 9 | relative 1e-12 | pass |
| biggest | NumPy where | 30 | 30 | relative 1e-12 | pass |
| total | R | 416.4 | 416.4 | relative 1e-12 | pass |
| empty | R | 9 | 9 | relative 1e-12 | pass |
| biggest | R | 30 | 30 | relative 1e-12 | pass |

### `nums.fill_empty_numbers`

**NHANES body mass index: gaps filled on the line between neighbours** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas interpolate (inside) | 612.85 | 612.85 | relative 1e-12 | pass |
| empty left | pandas interpolate (inside) | 1 | 1 | relative 1e-12 | pass |
| total | R | 612.85 | 612.85 | relative 1e-12 | pass |
| empty left | R | 1 | 1 | relative 1e-12 | pass |

### `nums.sort`

**NHANES body mass index biggest first, the empty cells last** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | pandas sort_values (empty last) | 35.3 | 35.3 | exact | pass |
| 16th | pandas sort_values (empty last) | 20.4 | 20.4 | exact | pass |
| empty at the end | pandas sort_values (empty last) | 9 | 9 | exact | pass |
| first | R | 35.3 | 35.3 | exact | pass |
| 16th | R | 20.4 | 20.4 | exact | pass |
| empty at the end | R | 9 | 9 | exact | pass |

### `nums.reverse`

**AirPassengers from the last month back** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | NumPy [::-1] | 432 | 432 | exact | pass |
| last | NumPy [::-1] | 112 | 112 | exact | pass |
| first | R | 432 | 432 | exact | pass |
| last | R | 112 | 112 | exact | pass |

### `nums.find_total`

**the total of NHANES body mass index, empty cells skipped** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | NumPy nansum | 425 | 425 | relative 1e-12 | pass |
| total | R | 425 | 425 | relative 1e-12 | pass |

### `nums.find_smallest`

**the smallest NHANES body mass index, empty cells skipped** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| smallest | NumPy nanmin | 20.4 | 20.4 | exact | pass |
| smallest | R | 20.4 | 20.4 | exact | pass |

### `nums.find_biggest`

**the biggest NHANES body mass index, empty cells skipped** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| biggest | NumPy nanmax | 35.3 | 35.3 | exact | pass |
| biggest | R | 35.3 | 35.3 | exact | pass |

### `nums.find_standard_deviation`

**the standard deviation of NHANES cholesterol, empty cells skipped** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| standard deviation | NumPy nanstd (ddof=1) | 45.2150417449769 | 45.2150417449769 | relative 1e-12 | pass |
| standard deviation | R | 45.2150417449769 | 45.2150417449769 | relative 1e-12 | pass |

### `nums.count_each`

**how many mtcars cars have 4, 6 and 8 cylinders** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first number | pandas value_counts | 8 | 8 | exact | pass |
| its count | pandas value_counts | 14 | 14 | exact | pass |
| its percent | pandas value_counts | 43.8 | 43.8 | exact | pass |
| count of 6 | pandas value_counts | 7 | 7 | exact | pass |
| its count | R | 14 | 14 | exact | pass |
| count of 6 | R | 7 | 7 | exact | pass |

### `nums.make_number_grid`

**AirPassengers as a grid of 12 years by 12 months** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy reshape (row after row) | 12 | 12 | exact | pass |
| all Julys | NumPy reshape (row after row) | 4216 | 4216 | exact | pass |
| 1955 | NumPy reshape (row after row) | 3408 | 3408 | exact | pass |
| rows | R | 12 | 12 | exact | pass |
| all Julys | R | 4216 | 4216 | exact | pass |
| 1955 | R | 3408 | 3408 | exact | pass |

### `grid.count_rows`

**the 150 iris flowers as rows of a grid** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy shape | 150 | 150 | exact | pass |
| rows | R | 150 | 150 | exact | pass |

### `grid.count_columns`

**the 4 iris measurements as columns of a grid** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | NumPy shape | 4 | 4 | exact | pass |
| columns | R | 4 | 4 | exact | pass |

### `grid.find_shape`

**the shape of the iris measurements as a grid** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy shape | 150 | 150 | exact | pass |
| columns | NumPy shape | 4 | 4 | exact | pass |
| rows | R | 150 | 150 | exact | pass |
| columns | R | 4 | 4 | exact | pass |

### `grid.show_first_rows`

**the first 3 iris flowers of the grid shown** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers shown | NumPy [:3] | 12 | 12 | relative 1e-12 | pass |
| total shown | NumPy [:3] | 29.1 | 29.1 | relative 1e-12 | pass |
| total shown | R | 29.1 | 29.1 | relative 1e-12 | pass |

### `grid.show_last_rows`

**the last 3 iris flowers of the grid shown** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers shown | NumPy [-3:] | 12 | 12 | relative 1e-12 | pass |
| total shown | NumPy [-3:] | 49.8 | 49.8 | relative 1e-12 | pass |
| total shown | R | 49.8 | 49.8 | relative 1e-12 | pass |

### `grid.get_number_at`

**the petal length of the last iris flower, counting from 1** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| row 150, column 3 | NumPy [ ] (from 0) | 5.1 | 5.1 | exact | pass |
| row 1, column 1 | NumPy [ ] (from 0) | 5.1 | 5.1 | exact | pass |
| row 150, column 3 | R | 5.1 | 5.1 | exact | pass |
| row 1, column 1 | R | 5.1 | 5.1 | exact | pass |

### `grid.get_row`

**the four measurements of the first iris flower** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | NumPy [0] | 4 | 4 | relative 1e-12 | pass |
| total | NumPy [0] | 10.2 | 10.2 | relative 1e-12 | pass |
| numbers | R | 4 | 4 | relative 1e-12 | pass |
| total | R | 10.2 | 10.2 | relative 1e-12 | pass |

### `grid.get_column`

**the 150 iris petal lengths, column 3 of the grid** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | NumPy [:, 2] | 150 | 150 | relative 1e-12 | pass |
| total | NumPy [:, 2] | 563.7 | 563.7 | relative 1e-12 | pass |
| numbers | R | 150 | 150 | relative 1e-12 | pass |
| total | R | 563.7 | 563.7 | relative 1e-12 | pass |

### `grid.get_all_numbers`

**all 600 iris measurements as one list, row by row** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | NumPy ravel (row by row) | 600 | 600 | relative 1e-12 | pass |
| total | NumPy ravel (row by row) | 2078.7 | 2078.7 | relative 1e-12 | pass |
| fifth | NumPy ravel (row by row) | 4.9 | 4.9 | relative 1e-12 | pass |
| numbers | R | 600 | 600 | relative 1e-12 | pass |
| total | R | 2078.7 | 2078.7 | relative 1e-12 | pass |
| fifth | R | 4.9 | 4.9 | relative 1e-12 | pass |

### `grid.keep_rows_by_position`

**rows 51 to 100 of the iris grid: the versicolor flowers** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy [50:100] | 50 | 50 | relative 1e-12 | pass |
| total sepal length | NumPy [50:100] | 296.8 | 296.8 | relative 1e-12 | pass |
| rows | R | 50 | 50 | relative 1e-12 | pass |
| total sepal length | R | 296.8 | 296.8 | relative 1e-12 | pass |

### `grid.keep_columns_by_position`

**columns 3 to 4 of the iris grid: the petals** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | NumPy [:, 2:4] | 2 | 2 | relative 1e-12 | pass |
| total | NumPy [:, 2:4] | 743.6 | 743.6 | relative 1e-12 | pass |
| columns | R | 2 | 2 | relative 1e-12 | pass |
| total | R | 743.6 | 743.6 | relative 1e-12 | pass |

### `grid.remove_rows_by_position`

**the iris grid without its first 50 rows (setosa)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy delete | 100 | 100 | relative 1e-12 | pass |
| total petal length | NumPy delete | 490.6 | 490.6 | relative 1e-12 | pass |
| rows | R | 100 | 100 | relative 1e-12 | pass |
| total petal length | R | 490.6 | 490.6 | relative 1e-12 | pass |

### `grid.remove_columns_by_position`

**columns 1 and 3 (the lengths) removed from the iris grid** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | NumPy delete | 2 | 2 | relative 1e-12 | pass |
| total of the widths | NumPy delete | 638.5 | 638.5 | relative 1e-12 | pass |
| columns | R | 2 | 2 | relative 1e-12 | pass |
| total of the widths | R | 638.5 | 638.5 | relative 1e-12 | pass |

### `grid.replace_each_number_that`

**iris measurements below 1 cm set to 0 where they are** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy where | 150 | 150 | relative 1e-12 | pass |
| total | NumPy where | 2066.4 | 2066.4 | relative 1e-12 | pass |
| petal width total | NumPy where | 167.6 | 167.6 | relative 1e-12 | pass |
| rows | R | 150 | 150 | relative 1e-12 | pass |
| total | R | 2066.4 | 2066.4 | relative 1e-12 | pass |
| petal width total | R | 167.6 | 167.6 | relative 1e-12 | pass |

### `grid.swap_rows_and_columns`

**the iris grid turned round: 4 rows of 150 flowers** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | NumPy .T | 4 | 4 | exact | pass |
| columns | NumPy .T | 150 | 150 | exact | pass |
| row 3, column 150 | NumPy .T | 5.1 | 5.1 | exact | pass |
| rows | R | 4 | 4 | exact | pass |
| columns | R | 150 | 150 | exact | pass |
| row 3, column 150 | R | 5.1 | 5.1 | exact | pass |

### `nums.turn_into_table`

**Michelson's measurements as a table of one column** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas DataFrame | 1 | 1 | relative 1e-12 | pass |
| total | pandas DataFrame | 29985.24 | 29985.24 | relative 1e-12 | pass |

### `nums.start_chart`

**a histogram of Michelson's measurements, started from the numbers** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bars | seaborn histplot (10 bins) | 10 | 10 | exact | pass |
| numbers counted | seaborn histplot (10 bins) | 100 | 100 | exact | pass |
| tallest | seaborn histplot (10 bins) | 27 | 27 | exact | pass |
| bars | R | 10 | 10 | exact | pass |
| numbers counted | R | 100 | 100 | exact | pass |

### `nums.save`

**Michelson's measurements saved as CSV and read back** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas to_csv and read_csv | 100 | 100 | relative 1e-12 | pass |
| total | pandas to_csv and read_csv | 29985.24 | 29985.24 | relative 1e-12 | pass |
| columns | pandas to_csv and read_csv | 1 | 1 | relative 1e-12 | pass |

### `nums.as_numpy`

**Michelson's measurements handed on as a NumPy array** (real data; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | NumPy array | 100 | 100 | exact | pass |
| total | NumPy array | 29985.24 | 29985.24 | exact | pass |
| numbers | R | 100 | 100 | relative 1e-12 | pass |
| total | R | 29985.24 | 29985.24 | relative 1e-12 | pass |

### `nums.smooth`

**the level of Lake Huron, 1875-1972: a centred moving average of 5 years** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| empty at the ends | pandas rolling(5, center=True).mean() | 4 | 4 | relative 1e-12 | pass |
| third year | pandas rolling(5, center=True).mean() | 580.76 | 580.76 | relative 1e-12 | pass |
| year 50 | pandas rolling(5, center=True).mean() | 577.64 | 577.64 | relative 1e-12 | pass |
| empty at the ends | R | 4 | 4 | relative 1e-12 | pass |
| third year | R | 580.76 | 580.76 | relative 1e-12 | pass |
| year 50 | R | 577.64 | 577.64 | relative 1e-12 | pass |

### `nums.remove_trend`

**the level of Lake Huron without its straight-line fall** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first year | SciPy signal.detrend | 0.202164502164351 | 0.202164502164351 | relative 1e-09 | pass |
| last year | SciPy signal.detrend | 2.12967223252963 | 2.12967223252963 | relative 1e-09 | pass |
| total | SciPy signal.detrend | 2.27373675443232e-13 | 2.27373675443232e-13 | relative 1e-09 | pass |
| first year | R | 0.202164502164351 | 0.20216450216436 | relative 1e-09 | pass |
| last year | R | 2.12967223252963 | 2.12967223252941 | relative 1e-09 | pass |

### `table.add_trend_and_season`

**the air passengers: trend, season and rest by STL (season window 7)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| trend, January 1949 | statsmodels STL with R stl()'s settings | 122.536917649433 | 122.536917649433 | relative 1e-09 | pass |
| season, July 1955 | statsmodels STL with R stl()'s settings | 73.1963038772656 | 73.1963038772656 | relative 1e-09 | pass |
| rest, December 1960 | statsmodels STL with R stl()'s settings | -12.4649554950755 | -12.4649554950755 | relative 1e-09 | pass |
| trend, January 1949 | R | 122.536917649433 | 122.536917649433 | relative 1e-09 | pass |
| season, July 1955 | R | 73.1963038772656 | 73.1963038772656 | relative 1e-09 | pass |
| rest, December 1960 | R | -12.4649554950755 | -12.4649554950755 | relative 1e-09 | pass |

### `nums.find_autocorrelation`

**the level of Lake Huron: correlation with itself 1 and 2 years back** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows back | statsmodels acf and acorr_ljungbox | 19 | 19 | relative 1e-12 | pass |
| 1 year back | statsmodels acf and acorr_ljungbox | 0.831911210352453 | 0.831911210352453 | relative 1e-12 | pass |
| 2 years back | statsmodels acf and acorr_ljungbox | 0.609937103589568 | 0.609937103589568 | relative 1e-12 | pass |
| Ljung-Box statistic | statsmodels acf and acorr_ljungbox | 192.258700438571 | 192.258700438571 | relative 1e-12 | pass |
| rows back | R | 19 | 19 | relative 1e-12 | pass |
| 1 year back | R | 0.831911210352453 | 0.831911210352453 | relative 1e-12 | pass |
| 2 years back | R | 0.609937103589568 | 0.609937103589568 | relative 1e-12 | pass |
| Ljung-Box statistic | R | 192.258700438571 | 192.258700438571 | relative 1e-12 | pass |

### `table.check_steady_over_time`

**the level of Lake Huron: the ADF and KPSS tests around one level** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| ADF statistic | R | -2.50692013839604 | -2.50692013839604 | relative 1e-09 | pass |
| ADF p-value | R | 0.117094492257189 | 0.117094492257189 | relative 1e-09 | pass |
| KPSS statistic | R | 0.995290114411602 | 0.995290114411602 | relative 1e-09 | pass |

### `table.find_change_points_in`

**the level of Lake Huron: where its average jumps (PELT, MBIC)** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| pieces | R | 8 | 8 | relative 1e-12 | pass |
| first piece ends | R | 1888 | 1888 | relative 1e-12 | pass |
| average of the first piece | R | 580.926428571429 | 580.926428571429 | relative 1e-12 | pass |

### `nums.forecast`

**the air passengers: Holt-Winters forecast of 1961 with its 95 % interval** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| January 1961 | R | 453.497721751319 | 453.497721751319 | relative 1e-09 | pass |
| January 1961, 95 % low | R | 428.415266965018 | 428.415266965018 | relative 1e-09 | pass |
| December 1961 | R | 469.531518789794 | 469.531518789794 | relative 1e-09 | pass |

### `table.compare_forecasts_for`

**the air passengers: four methods checked on 1960** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| best MASE | R | 0.379783839708431 | 0.379783839708431 | relative 1e-09 | pass |
| worst MASE | R | 2.49589490968801 | 2.49589490968801 | relative 1e-09 | pass |
| best MAE | R | 11.5644179191217 | 11.5644179191217 | relative 1e-09 | pass |

### `nums.find_each_peak_that`

**the drivers killed or seriously injured: the peaks at least 6 months apart** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| peaks | SciPy find_peaks(distance=6) and peak_widths | 21 | 21 | relative 1e-12 | pass |
| first peak | SciPy find_peaks(distance=6) and peak_widths | 5 | 5 | relative 1e-12 | pass |
| its width | SciPy find_peaks(distance=6) and peak_widths | 0.744939271255061 | 0.744939271255061 | relative 1e-12 | pass |
| peaks | R | 21 | 21 | exact | pass |
| first peak | R | 5 | 5 | exact | pass |

Note: pracma::findpeaks keeps the higher of two close peaks first, as SciPy's distance= does.

**the yearly sunspot numbers: the solar maxima of at least 100** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| peaks | SciPy signal.find_peaks | 17 | 17 | exact | pass |
| first position | SciPy signal.find_peaks | 28 | 28 | exact | pass |
| sum of positions | SciPy signal.find_peaks | 3156 | 3156 | exact | pass |
| highest | SciPy signal.find_peaks | 190.2 | 190.2 | exact | pass |
| peaks | R | 17 | 17 | exact | pass |
| first position | R | 28 | 28 | exact | pass |
| sum of positions | R | 3156 | 3156 | exact | pass |
| highest | R | 190.2 | 190.2 | exact | pass |

Note: R: the readings higher than both neighbours, written out in base R.

### `nums.find_each_dip_that`

**the level of Lake Huron: the lowest years, dips at least 5 years apart** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dips | SciPy find_peaks on minus the level | 13 | 13 | exact | pass |
| lowest dip | SciPy find_peaks on minus the level | 575.96 | 575.96 | exact | pass |
| first dip | SciPy find_peaks on minus the level | 5 | 5 | exact | pass |

**the yearly sunspot numbers: the solar minima of at most 5** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dips | SciPy signal.find_peaks on minus the numbers | 11 | 11 | relative 1e-12 | pass |
| first position | SciPy signal.find_peaks on minus the numbers | 12 | 12 | relative 1e-12 | pass |
| sum of positions | SciPy signal.find_peaks on minus the numbers | 1432 | 1432 | relative 1e-12 | pass |
| biggest stands out by | SciPy signal.find_peaks on minus the numbers | 154.4 | 154.4 | relative 1e-12 | pass |

### `table.find_each_dip_that`

**the air passengers: the dips at least 6 months apart** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dips | SciPy find_peaks on minus the passengers | 15 | 15 | exact | pass |
| first dip | SciPy find_peaks on minus the passengers | 5 | 5 | exact | pass |
| lowest dip | SciPy find_peaks on minus the passengers | 104 | 104 | exact | pass |

**the yearly sunspot numbers: the years of the solar minima of at most 5** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dips | SciPy signal.find_peaks on minus the numbers | 11 | 11 | exact | pass |
| first year | SciPy signal.find_peaks on minus the numbers | 1711 | 1711 | exact | pass |
| last year | SciPy signal.find_peaks on minus the numbers | 1954 | 1954 | exact | pass |

### `table.find_spectrum_of`

**the level of Lake Huron: the periodogram, per year** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| frequencies | SciPy signal.periodogram | 50 | 50 | relative 1e-09 | pass |
| power at 1 / 98 per year | SciPy signal.periodogram | 50.5962422380123 | 50.5962422380123 | relative 1e-09 | pass |
| power at 10 / 98 per year | SciPy signal.periodogram | 0.000959006180129825 | 0.000959006180129825 | relative 1e-09 | pass |
| power at 1 / 98 per year | R | 50.5962422380123 | 50.596242238018 | relative 1e-09 | pass |
| power at 10 / 98 per year | R | 0.000959006180129825 | 0.000959006180134383 | relative 1e-09 | pass |

Note: R spec.pgram is two-sided and has no row for frequency 0, so its first value is SciPy's second, halved.

**the yearly sunspot numbers: the strongest cycle and the periodogram** (published; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| strongest cycle (years) | Hathaway (2015): 11.0 years on average | 11.0357142857143 | 11 | within 0.5 (printed rounding) | pass |
| strongest cycle (years) | SciPy signal.periodogram | 11.0357142857143 | 11.0357142857143 | relative 1e-09 | pass |
| power of the 11-year cycle | SciPy signal.periodogram | 135012.909731365 | 135012.909731365 | relative 1e-09 | pass |
| total power | SciPy signal.periodogram | 504015.031132686 | 504015.031132686 | relative 1e-09 | pass |
| strongest cycle (years) | R | 11.0357142857143 | 11.0357142857143 | relative 1e-09 | pass |
| power of the 11-year cycle | R | 135012.909731365 | 135012.909731365 | relative 1e-09 | pass |
| total power | R | 504015.031132686 | 504015.031132686 | relative 1e-09 | pass |

Note: R spec.pgram gives half the one-sided power and leaves out frequency 0 (whose power is 0 here up to rounding); with 309 readings there is no top frequency to treat apart.

### `nums.find_spectrum`

**the drivers killed or seriously injured: the yearly cycle in the periodogram** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power at 1 / 12 per month | SciPy signal.periodogram | 4998897.58613393 | 4998897.58613393 | relative 1e-09 | pass |
| power at 1 / 12 per month | R | 4998897.58613393 | 4998897.58613393 | relative 1e-09 | pass |

Note: 192 months: frequency 16 / 192 is once a year.

**the yearly sunspot numbers as numbers: the periodogram, one reading a year** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| frequencies | SciPy signal.periodogram | 155 | 155 | relative 1e-09 | pass |
| power at 1 / 103 years | SciPy signal.periodogram | 43837.7956506015 | 43837.7956506015 | relative 1e-09 | pass |
| total power | SciPy signal.periodogram | 504015.031132686 | 504015.031132686 | relative 1e-09 | pass |
| power at 1 / 103 years | R | 43837.7956506015 | 43837.7956506016 | relative 1e-09 | pass |
| total power | R | 504015.031132686 | 504015.031132686 | relative 1e-09 | pass |

### `spectrum`

**the drawn periodogram of the Lake Huron level is SciPy's** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | SciPy signal.periodogram | 49 | 49 | relative 1e-09 | pass |
| first power drawn | SciPy signal.periodogram | 50.5962422380123 | 50.5962422380123 | relative 1e-09 | pass |
| labels | SciPy signal.periodogram | 3 | 3 | relative 1e-09 | pass |

**the yearly sunspot numbers: the periodogram the chart draws** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | SciPy signal.periodogram | 154 | 154 | relative 1e-09 | pass |
| first power | SciPy signal.periodogram | 11952.1212354268 | 11952.1212354268 | relative 1e-09 | pass |
| total power | SciPy signal.periodogram | 504015.031132686 | 504015.031132686 | relative 1e-09 | pass |
| points | R | 154 | 154 | relative 1e-09 | pass |
| first power | R | 11952.1212354268 | 11952.1212354268 | relative 1e-09 | pass |
| total power | R | 504015.031132686 | 504015.031132686 | relative 1e-09 | pass |

Note: The chart leaves out frequency 0 (log scale).

### `spectrum_over_time`

**the drivers killed or seriously injured: spectrum over time in pieces of 48 months** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells | SciPy signal.spectrogram | 175 | 175 | relative 1e-09 | pass |
| first cell (decibels) | SciPy signal.spectrogram | 48.1376306384409 | 48.1376306384409 | relative 1e-09 | pass |

**the yearly sunspot numbers in pieces of 64 years: the heat map** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells | SciPy signal.spectrogram | 264 | 264 | relative 1e-09 | pass |
| first cell (dB) | SciPy signal.spectrogram | 31.5414549131363 | 31.5414549131363 | relative 1e-09 | pass |
| total (dB) | SciPy signal.spectrogram | 6255.24770167516 | 6255.24770167516 | relative 1e-09 | pass |

### `nums.keep_each_frequency_that`

**the Lake Huron level: cycles slower than 10 years kept** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first year | SciPy butter and sosfiltfilt | 580.383339492162 | 580.383339492162 | relative 1e-09 | pass |
| year 50 | SciPy butter and sosfiltfilt | 577.644110448839 | 577.644110448839 | relative 1e-09 | pass |

**the yearly sunspot numbers: the cycles slower than 20 years** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | SciPy signal.butter and sosfiltfilt | 4.72252326731995 | 4.72252326731995 | relative 1e-09 | pass |
| 1957 (position 258) | SciPy signal.butter and sosfiltfilt | 94.262193180326 | 94.262193180326 | relative 1e-09 | pass |
| total | SciPy signal.butter and sosfiltfilt | 15321.7510272055 | 15321.7510272055 | relative 1e-09 | pass |

### `nums.remove_each_frequency_that`

**the drivers killed or seriously injured: the yearly cycle notched out** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first month | SciPy iirnotch and filtfilt | 1629.5699959513 | 1629.5699959513 | relative 1e-09 | pass |
| month 100 | SciPy iirnotch and filtfilt | 1594.19196944698 | 1594.19196944698 | relative 1e-09 | pass |

**the yearly sunspot numbers without the 9 to 14-year band** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | SciPy signal.butter and sosfiltfilt | 1.70756638994537 | 1.70756638994537 | relative 1e-09 | pass |
| 1957 (position 258) | SciPy signal.butter and sosfiltfilt | 141.812213467464 | 141.812213467464 | relative 1e-09 | pass |
| total | SciPy signal.butter and sosfiltfilt | 15396.2757035565 | 15396.2757035565 | relative 1e-09 | pass |

### `table.add_filtered_column`

**the Lake Huron level: a column of the cycles slower than 10 years** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1875 | SciPy butter and sosfiltfilt | 580.383339492162 | 580.383339492162 | relative 1e-09 | pass |
| 1924 | SciPy butter and sosfiltfilt | 577.644110448839 | 577.644110448839 | relative 1e-09 | pass |

Note: The years are one apart, so keep_below=0.1 keeps the cycles longer than 10 years.

### `sdata.frequency_filter`

**the filter of keep_below=10 at 200 readings a second is R signal's** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| gain at 10 | exact: a Butterworth filter passes 1 / sqrt(2) at its cutoff | 0.707106781186548 | 0.707106781186548 | within 1e-12 (exact formula) | pass |
| numerator total / denominator total | exact: a low-pass filter passes frequency 0 whole (gain 1 at z = 1) | 1.00000000000009 | 1 | within 1e-12 (exact formula) | pass |
| b0 | SciPy signal.butter (as numerator and denominator) | 0.000416599204406599 | 0.000416599204406599 | relative 1e-09 | pass |
| a1 | SciPy signal.butter (as numerator and denominator) | -3.18063854887472 | -3.18063854887472 | relative 1e-09 | pass |
| a4 | SciPy signal.butter (as numerator and denominator) | 0.43826514226198 | 0.43826514226198 | relative 1e-09 | pass |
| b0 | R | 0.000416599204406599 | 0.000416599204406599 | relative 1e-09 | pass |
| a1 | R | -3.18063854887472 | -3.18063854887472 | relative 1e-09 | pass |
| a4 | R | 0.43826514226198 | 0.43826514226198 | relative 1e-09 | pass |

Note: A filter has no data: the Butterworth design of order 4 at a tenth of the top frequency. The coefficients are compared with SciPy and R signal; the two gains with their exact values.

**the low-pass filter of the sunspot cases (below 0.05 a year): its poles** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| poles | SciPy signal.butter | 4 | 4 | relative 1e-09 | pass |
| smallest distance | SciPy signal.butter | 0.745534401139538 | 0.745534401139538 | relative 1e-09 | pass |
| biggest distance | SciPy signal.butter | 0.887975078375119 | 0.887975078375118 | relative 1e-09 | pass |
| steady gain | SciPy signal.butter | 1.00000000000009 | 1 | relative 1e-09 | pass |
| poles | R | 4 | 4 | relative 1e-09 | pass |
| smallest distance | R | 0.745534401139538 | 0.745534401139538 | relative 1e-09 | pass |
| biggest distance | R | 0.887975078375119 | 0.887975078375119 | relative 1e-09 | pass |

Note: R: Butterworth's poles and the bilinear transform written out in base R.

### `nums.find_envelope`

**the Lake Huron level about its average: the envelope** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first year | SciPy signal.hilbert | 3.17450363547566 | 3.17450363547566 | relative 1e-09 | pass |
| year 50 | SciPy signal.hilbert | 2.05123982484622 | 2.05123982484622 | relative 1e-09 | pass |
| first year | R | 3.17450363547566 | 3.17450363547566 | relative 1e-09 | pass |
| year 50 | R | 2.05123982484622 | 2.05123982484622 | relative 1e-09 | pass |

**the yearly sunspot numbers: the envelope of the solar cycle** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | SciPy signal.hilbert | 25.2468371760035 | 25.2468371760035 | relative 1e-09 | pass |
| 1957 (position 258) | SciPy signal.hilbert | 196.927165296085 | 196.927165296085 | relative 1e-09 | pass |
| total | SciPy signal.hilbert | 19786.6446978571 | 19786.6446978571 | relative 1e-09 | pass |
| first | R | 25.2468371760035 | 25.2468371760031 | relative 1e-09 | pass |
| 1957 (position 258) | R | 196.927165296085 | 196.927165296085 | relative 1e-09 | pass |
| total | R | 19786.6446978571 | 19786.6446978571 | relative 1e-09 | pass |

Note: R: the analytic signal written out with base R fft (as gsignal::hilbert).

### `table.add_envelope_column`

**the drivers killed or seriously injured: the envelope column** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first month | SciPy signal.hilbert | 1692.00337821708 | 1692.00337821708 | relative 1e-09 | pass |
| month 100 | SciPy signal.hilbert | 1405.68102486951 | 1405.68102486951 | relative 1e-09 | pass |
| first month | R | 1692.00337821708 | 1692.00337821708 | relative 1e-09 | pass |
| month 100 | R | 1405.68102486951 | 1405.68102486951 | relative 1e-09 | pass |

**the yearly sunspot numbers: the envelope as a new column, by year** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1957 (row 258) | SciPy signal.hilbert | 196.927165296085 | 196.927165296085 | relative 1e-09 | pass |
| last | SciPy signal.hilbert | 39.9516118079954 | 39.9516118079954 | relative 1e-09 | pass |
| total | SciPy signal.hilbert | 19786.6446978571 | 19786.6446978571 | relative 1e-09 | pass |
| 1957 (row 258) | R | 196.927165296085 | 196.927165296085 | relative 1e-09 | pass |
| last | R | 39.9516118079954 | 39.951611807996 | relative 1e-09 | pass |
| total | R | 19786.6446978571 | 19786.6446978571 | relative 1e-09 | pass |

Note: The phase (show="phase") is not compared here: the sunspot phase has a step of exactly half a turn, where the last digit of the Fourier transform decides whether unwrapping adds or takes off 360 degrees.

### `nums.take_fourier_transform`

**the Lake Huron level: the size and phase of the first frequencies** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| frequencies | SciPy fft.rfft | 50 | 50 | relative 1e-12 | pass |
| size at 0 | SciPy fft.rfft | 56742.4 | 56742.4 | relative 1e-12 | pass |
| size at 1 / 98 | SciPy fft.rfft | 49.7917249115031 | 49.7917249115031 | relative 1e-12 | pass |
| phase at 1 / 98 | SciPy fft.rfft | -46.2957869207093 | -46.2957869207093 | relative 1e-12 | pass |
| size at 0 | R | 56742.4 | 56742.4 | relative 1e-10 | pass |
| size at 1 / 98 | R | 49.7917249115031 | 49.7917249115039 | relative 1e-10 | pass |
| phase at 1 / 98 | R | -46.2957869207093 | -46.2957869207089 | relative 1e-10 | pass |

**the yearly sunspot numbers: size and phase of the 11-year wave** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| size at 28 / 309 | NumPy fft.rfft | 4567.21956484423 | 4567.21956484423 | relative 1e-09 | pass |
| phase at 28 / 309 | NumPy fft.rfft | -164.067910640384 | -164.067910640384 | relative 1e-09 | pass |
| total of the sizes | NumPy fft.rfft | 74053.1000175372 | 74053.1000175372 | relative 1e-09 | pass |
| size at 28 / 309 | R | 4567.21956484423 | 4567.21956484423 | relative 1e-09 | pass |
| phase at 28 / 309 | R | -164.067910640384 | -164.067910640384 | relative 1e-09 | pass |
| total of the sizes | R | 74053.1000175372 | 74053.1000175372 | relative 1e-09 | pass |

### `sdata.find_inverse_fourier_transform`

**the Lake Huron level there and back** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count | the data themselves | 98 | 98 | relative 1e-12 | pass |
| first year | the data themselves | 580.38 | 580.38 | relative 1e-12 | pass |
| last year | the data themselves | 579.96 | 579.96 | relative 1e-12 | pass |

**the yearly sunspot numbers there and back** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | the numbers themselves | 309 | 309 | relative 1e-12 | pass |
| 1957 (position 258) | the numbers themselves | 190.2 | 190.2 | relative 1e-12 | pass |
| total | the numbers themselves | 15373.4 | 15373.4 | relative 1e-12 | pass |
| numbers | R | 309 | 309 | relative 1e-12 | pass |
| 1957 (position 258) | R | 190.2 | 190.2 | relative 1e-12 | pass |
| total | R | 15373.4 | 15373.4 | relative 1e-12 | pass |

### `nums.convolve_with`

**the air passengers convolved with the weights 1, 2, 1** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count | NumPy convolve (full) | 146 | 146 | relative 1e-12 | pass |
| first | NumPy convolve (full) | 112 | 112 | relative 1e-12 | pass |
| number 100 | NumPy convolve (full) | 1361 | 1361 | relative 1e-12 | pass |
| count | R | 146 | 146 | relative 1e-09 | pass |
| first | R | 112 | 111.999999999989 | relative 1e-09 | pass |
| number 100 | R | 1361 | 1361 | relative 1e-09 | pass |

**the yearly sunspot numbers, weighted with 0.5, 0.3 and 0.2** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | NumPy convolve | 311 | 311 | relative 1e-12 | pass |
| third | NumPy convolve | 12.3 | 12.3 | relative 1e-12 | pass |
| total | NumPy convolve | 15373.4 | 15373.4 | relative 1e-12 | pass |
| numbers | R | 311 | 311 | relative 1e-09 | pass |
| third | R | 12.3 | 12.3 | relative 1e-09 | pass |
| total | R | 15373.4 | 15373.4 | relative 1e-09 | pass |

### `nums.deconvolve_by`

**the air passengers divided by 1 + 0.5 z^-1** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count | SciPy signal.deconvolve | 143 | 143 | relative 1e-12 | pass |
| first | SciPy signal.deconvolve | 112 | 112 | relative 1e-12 | pass |
| number 100 | SciPy signal.deconvolve | 219.573468074553 | 219.573468074553 | relative 1e-12 | pass |
| count | R | 143 | 143 | relative 1e-09 | pass |
| first | R | 112 | 112 | relative 1e-09 | pass |
| number 100 | R | 219.573468074553 | 219.573468074553 | relative 1e-09 | pass |

Note: Dividing by 1 + 0.5 z^-1 is the recursive filter y[t] = x[t] - 0.5 y[t - 1].

**the yearly sunspot numbers divided by 1 - 0.5 z (polynomial division)** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | SciPy signal.deconvolve | 308 | 308 | relative 1e-12 | pass |
| last | SciPy signal.deconvolve | 38.0335261670098 | 38.0335261670098 | relative 1e-12 | pass |
| total | SciPy signal.deconvolve | 30702.966473833 | 30702.966473833 | relative 1e-12 | pass |
| numbers | R | 308 | 308 | relative 1e-09 | pass |
| last | R | 38.0335261670098 | 38.0335261670098 | relative 1e-09 | pass |
| total | R | 30702.966473833 | 30702.966473833 | relative 1e-09 | pass |

### `nums.change_time_step`

**the air passengers every two months (Fourier resampling)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count | SciPy signal.resample | 72 | 72 | relative 1e-09 | pass |
| first | SciPy signal.resample | 196.468128462929 | 196.468128462929 | relative 1e-09 | pass |
| number 30 | SciPy signal.resample | 193.571238670015 | 193.571238670015 | relative 1e-09 | pass |

**the yearly sunspot numbers, one reading every 2 years (Fourier)** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numbers | SciPy signal.resample | 154 | 154 | relative 1e-09 | pass |
| first | SciPy signal.resample | 6.93686411930335 | 6.93686411930335 | relative 1e-09 | pass |
| total | SciPy signal.resample | 7661.82394822006 | 7661.82394822006 | relative 1e-09 | pass |

### `sdata.make_wave`

**a square wave of 5 cycles a second, 100 readings 0.01 seconds apart** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | exact: worked out by hand from the formula | 1 | 1 | within 0 (exact formula) | pass |
| number 11 | exact: worked out by hand from the formula | -1 | -1 | within 0 (exact formula) | pass |
| total | exact: worked out by hand from the formula | 0 | 0 | within 0 (exact formula) | pass |
| first | SciPy signal.square | 1 | 1 | exact | pass |
| number 11 | SciPy signal.square | -1 | -1 | exact | pass |
| total | SciPy signal.square | 0 | 0 | exact | pass |

Note: Each cycle is 20 readings: 10 high, then 10 low.

**a sine wave of 5 cycles per second, 100 readings 0.01 apart** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| readings | NumPy sin | 100 | 100 | relative 1e-12 | pass |
| third | NumPy sin | 0.587785252292473 | 0.587785252292473 | relative 1e-12 | pass |
| biggest | NumPy sin | 1 | 1 | relative 1e-12 | pass |
| total of squares | NumPy sin | 50 | 50 | relative 1e-12 | pass |
| readings | R | 100 | 100 | relative 1e-12 | pass |
| third | R | 0.587785252292473 | 0.587785252292473 | relative 1e-12 | pass |
| biggest | R | 1 | 1 | relative 1e-12 | pass |
| total of squares | R | 50 | 50 | relative 1e-12 | pass |

### `sdata.make_window_shape`

**the symmetric Hann window of 64 weights** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | exact: worked out by hand from the formula | 0 | 0 | within 1e-15 (exact formula) | pass |
| total | exact: worked out by hand from the formula: (64 - 1) / 2 | 31.5 | 31.5 | within 1e-12 (exact formula) | pass |
| first | NumPy hanning | 0 | 0 | relative 1e-12 | pass |
| number 32 | NumPy hanning | 0.999378460609461 | 0.999378460609461 | relative 1e-12 | pass |
| total | NumPy hanning | 31.5 | 31.5 | relative 1e-12 | pass |
| number 32 | R | 0.999378460609461 | 0.999378460609461 | relative 1e-12 | pass |
| total | R | 31.5 | 31.5 | relative 1e-12 | pass |
| weights | NumPy hanning | 64 | 64 | relative 1e-12 | pass |
| second | NumPy hanning | 0.0024846123172993 | 0.0024846123172993 | relative 1e-12 | pass |
| total | NumPy hanning | 31.5 | 31.5 | relative 1e-12 | pass |
| weights | R | 64 | 64 | relative 1e-12 | pass |
| second | R | 0.0024846123172993 | 0.0024846123172993 | relative 1e-12 | pass |
| total | R | 31.5 | 31.5 | relative 1e-12 | pass |

### `sdata.system`

**2 / (2 s^2 + 4 s + 10) is written as 1 / (s^2 + 2 s + 5)** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top | exact: worked out by hand from the formula | 1 | 1 | within 1e-15 (exact formula) | pass |
| s | exact: worked out by hand from the formula | 2 | 2 | within 1e-15 (exact formula) | pass |
| constant | exact: worked out by hand from the formula | 5 | 5 | within 1e-15 (exact formula) | pass |

**a system from its poles -1 and -2, zero -3 and gain 2** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numerator, s^0 | python-control zpk | 6 | 6 | relative 1e-12 | pass |
| numerator, s^1 | python-control zpk | 2 | 2 | relative 1e-12 | pass |
| denominator, s^1 | python-control zpk | 3 | 3 | relative 1e-12 | pass |
| denominator, s^0 | python-control zpk | 2 | 2 | relative 1e-12 | pass |
| numerator, s^0 | R | 6 | 6 | relative 1e-12 | pass |
| numerator, s^1 | R | 2 | 2 | relative 1e-12 | pass |
| denominator, s^1 | R | 3 | 3 | relative 1e-12 | pass |
| denominator, s^0 | R | 2 | 2 | relative 1e-12 | pass |

### `system.step_response`

**1 / (s^2 + 2 s + 5): the step response against its closed form** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| at time 10 / 199 x 31 | exact: 0.2 (1 - exp(-t) (cos 2t + sin 2t / 2)) | 0.241558177249802 | 0.241558177249802 | within 1e-07 (exact formula) | pass |
| at time 10 | exact: 0.2 (1 - exp(-t) (cos 2t + sin 2t / 2)) | 0.199992149855585 | 0.199992149855585 | within 1e-07 (exact formula) | pass |
| at time 10 / 199 x 31 | SciPy signal.step | 0.241558177249802 | 0.241558177249802 | relative 1e-12 | pass |
| at time 10 | SciPy signal.step | 0.199992149855585 | 0.199992149855585 | relative 1e-12 | pass |

Note: SciPy's step response solves the system numerically, so it agrees with the formula to about 1e-8.

**1 / (s^2 + 2 s + 5): the answer to a step, 0 to 5 seconds** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| at 1.5 | python-control step_response | 0.241030623862586 | 0.241030623862586 | relative 1e-08 | pass |
| at 5 | python-control step_response | 0.201497282439427 | 0.201497282439427 | relative 1e-08 | pass |
| total | python-control step_response | 1.93984483430892 | 1.93984483430892 | relative 1e-08 | pass |
| at 1.5 | R | 0.241030623862586 | 0.241030623862586 | relative 1e-08 | pass |
| at 5 | R | 0.201497282439427 | 0.201497282439427 | relative 1e-08 | pass |
| total | R | 1.93984483430892 | 1.93984483430892 | relative 1e-08 | pass |

Note: R: the step response written out from the poles and residues of the formula.

### `system.impulse_response`

**1 / (s^2 + 2 s + 5): the impulse response against its closed form** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| at time 10 / 199 x 31 | exact: exp(-t) sin(2t) / 2 | 0.00273906139735492 | 0.00273906139735484 | within 1e-07 (exact formula) | pass |
| at time 10 | exact: exp(-t) sin(2t) / 2 | 2.07238251300142e-05 | 2.07238251300142e-05 | within 1e-07 (exact formula) | pass |
| at time 10 / 199 x 31 | SciPy signal.impulse | 0.00273906139735492 | 0.00273906139735492 | relative 1e-12 | pass |
| at time 10 | SciPy signal.impulse | 2.07238251300142e-05 | 2.07238251300142e-05 | relative 1e-12 | pass |

**1 / (s^2 + 2 s + 5): the answer to a kick, 0 to 5 seconds** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| at 0.5 | python-control impulse_response | 0.255188975772286 | 0.255188975772286 | relative 1e-08 | pass |
| at 2 | python-control impulse_response | -0.0512110400283368 | -0.0512110400283368 | relative 1e-08 | pass |
| total | python-control impulse_response | 0.360101948231805 | 0.360101948231806 | relative 1e-08 | pass |
| at 0.5 | R | 0.255188975772286 | 0.255188975772286 | relative 1e-08 | pass |
| at 2 | R | -0.0512110400283368 | -0.0512110400283369 | relative 1e-08 | pass |
| total | R | 0.360101948231805 | 0.360101948231806 | relative 1e-08 | pass |

### `system.response_to`

**a first-order lag 1 / (5 s + 1) fed the level of Lake Huron, year by year** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| output after 1 year | SciPy signal.lsim(interp=False) | 105.205045528601 | 105.205045528601 | relative 1e-09 | pass |
| output in 1972 | SciPy signal.lsim(interp=False) | 578.682841342042 | 578.682841342042 | relative 1e-09 | pass |
| output after 1 year | R | 105.205045528601 | 105.205045528601 | relative 1e-09 | pass |
| output in 1972 | R | 578.682841342042 | 578.682841342042 | relative 1e-09 | pass |

Note: With each input held for a year, the lag is exactly y[t] = a y[t - 1] + (1 - a) x[t - 1], a = exp(-1 / 5).

**a first-order system (time constant 5 years) answering the sunspot numbers** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1957 (row 258) | python-control sample_system (zoh) and forced_response | 67.4058432652337 | 67.4058432652337 | relative 1e-09 | pass |
| last | python-control sample_system (zoh) and forced_response | 47.1249787683812 | 47.1249787683812 | relative 1e-09 | pass |
| total | python-control sample_system (zoh) and forced_response | 15157.6527023422 | 15157.6527023422 | relative 1e-09 | pass |
| 1957 (row 258) | R | 67.4058432652337 | 67.4058432652337 | relative 1e-09 | pass |
| last | R | 47.1249787683812 | 47.1249787683812 | relative 1e-09 | pass |
| total | R | 15157.6527023422 | 15157.6527023422 | relative 1e-09 | pass |

Note: Each input holds until the next year (zero order hold), as simplydata's response_to does; R gives the exact answer of that, written out year by year.

### `system.frequency_response`

**1 / (s^2 + 2 s + 5) at 1 radian per second** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| gain at 1 | exact: worked out by hand from the formula: 1 / sqrt(16 + 4) | 0.223606797749979 | 0.223606797749979 | within 1e-12 (exact formula) | pass |
| phase at 1 | exact: worked out by hand from the formula: -atan(2 / 4) in degrees | -26.565051177078 | -26.565051177078 | within 1e-10 (exact formula) | pass |
| gain at 1 | R | 0.223606797749979 | 0.223606797749979 | relative 1e-12 | pass |
| phase at 1 | R | -26.565051177078 | -26.565051177078 | relative 1e-12 | pass |

**1 / (s^2 + 2 s + 5): gain and phase from 0.1 to 10 radians a second** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| gain at 1 | python-control (the formula at s = i w) | 0.223606797749979 | 0.223606797749979 | relative 1e-09 | pass |
| phase at 3.16 (degrees) | python-control (the formula at s = i w) | -128.328818101456 | -128.328818101456 | relative 1e-09 | pass |
| gain at 10 (dB) | python-control (the formula at s = i w) | -39.7428135887783 | -39.7428135887783 | relative 1e-09 | pass |
| gain at 1 | R | 0.223606797749979 | 0.223606797749979 | relative 1e-09 | pass |
| phase at 3.16 (degrees) | R | -128.328818101456 | -128.328818101456 | relative 1e-09 | pass |
| gain at 10 (dB) | R | -39.7428135887783 | -39.7428135887783 | relative 1e-09 | pass |

### `system.poles`

**1 / (s^2 + 2 s + 5): poles -1 +/- 2i** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| real part | exact: worked out by hand from the formula | -1 | -1 | within 1e-12 (exact formula) | pass |
| damping ratio | exact: worked out by hand from the formula | 0.447213595499958 | 0.447213595499958 | within 1e-12 (exact formula) | pass |
| natural frequency | exact: worked out by hand from the formula | 2.23606797749979 | 2.23606797749979 | within 1e-12 (exact formula) | pass |
| real part | R | -1 | -1 | relative 1e-12 | pass |
| damping ratio | R | 0.447213595499958 | 0.447213595499958 | relative 1e-12 | pass |
| natural frequency | R | 2.23606797749979 | 2.23606797749979 | relative 1e-12 | pass |

**(s^2 + 4 s + 13) / (s^3 + 3 s^2 + 7 s + 5): the poles -1 and -1 +/- 2i** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| poles | python-control poles | 3 | 3 | relative 1e-09 | pass |
| biggest imaginary part | python-control poles | 2 | 2 | relative 1e-09 | pass |
| total of the real parts | python-control poles | -3 | -3 | relative 1e-09 | pass |
| smallest damping ratio | python-control poles | 0.447213595499958 | 0.447213595499958 | relative 1e-09 | pass |
| poles | R | 3 | 3 | relative 1e-09 | pass |
| biggest imaginary part | R | 2 | 2 | relative 1e-09 | pass |
| total of the real parts | R | -3 | -3 | relative 1e-09 | pass |
| smallest damping ratio | R | 0.447213595499958 | 0.447213595499958 | relative 1e-09 | pass |

### `system.zeros`

**(s + 1) / (s^2 + 2 s + 5): one zero at -1** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| zeros | exact: worked out by hand from the formula | 1 | 1 | within 0 (exact formula) | pass |
| real part | exact: worked out by hand from the formula | -1 | -1 | within 1e-12 (exact formula) | pass |

**(s^2 + 4 s + 13) / (s^3 + 3 s^2 + 7 s + 5): the zeros -2 +/- 3i** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| zeros | python-control zeros | 2 | 2 | relative 1e-09 | pass |
| biggest imaginary part | python-control zeros | 3 | 3 | relative 1e-09 | pass |
| distance from 0 | python-control zeros | 3.60555127546399 | 3.60555127546399 | relative 1e-09 | pass |
| zeros | R | 2 | 2 | relative 1e-09 | pass |
| biggest imaginary part | R | 3 | 2.99999999999999 | relative 1e-09 | pass |
| distance from 0 | R | 3.60555127546399 | 3.60555127546399 | relative 1e-09 | pass |

### `system.is_stable`

**1 / (s^2 + 4) rings for ever: poles on the axis are not stable** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| stable (1 = yes) | exact: worked out by hand from the formula: poles +/- 2i | 0 | 0 | within 0 (exact formula) | pass |
| 1 / (s + 1) stable | exact: worked out by hand from the formula: pole -1 | 1 | 1 | within 0 (exact formula) | pass |

**1 / (s^2 + 2 s + 5) is stable; 1 / (s^2 - s + 2) is not** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| stable one | python-control poles | 1 | 1 | exact | pass |
| unstable one | python-control poles | 0 | 0 | exact | pass |
| stable one | R | 1 | 1 | exact | pass |
| unstable one | R | 0 | 0 | exact | pass |

### `system.steady_gain`

**1 / (s^2 + 2 s + 5) settles at 0.2** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| steady gain | exact: worked out by hand from the formula: 1 / 5 | 0.2 | 0.2 | within 1e-15 (exact formula) | pass |
| steady gain | R | 0.2 | 0.2 | relative 1e-12 | pass |

**(s^2 + 4 s + 13) / (s^3 + 3 s^2 + 7 s + 5) settles at 13 / 5** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| steady gain | python-control dcgain | 2.6 | 2.6 | relative 1e-12 | pass |
| steady gain | R | 2.6 | 2.6 | relative 1e-12 | pass |

### `system.in_steps`

**1 / (s + 1) in steps of 0.1 (zero order hold)** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top | exact: worked out by hand from the formula: 1 - exp(-0.1) | 0.0951625819640405 | 0.0951625819640405 | within 1e-12 (exact formula) | pass |
| pole | exact: worked out by hand from the formula: exp(-0.1) | 0.90483741803596 | 0.90483741803596 | within 1e-12 (exact formula) | pass |
| top | R | 0.0951625819640405 | 0.0951625819640404 | relative 1e-09 | pass |
| pole | R | 0.90483741803596 | 0.904837418035959 | relative 1e-09 | pass |

**1 / (s^2 + 2 s + 5) in steps of 0.1 (zero order hold)** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| distance of the poles from 0 | python-control sample_system (zoh) | 0.90483741803596 | 0.90483741803596 | relative 1e-09 | pass |
| real part of the poles | python-control sample_system (zoh) | 0.886800911797208 | 0.886800911797208 | relative 1e-09 | pass |
| steady gain | python-control sample_system (zoh) | 0.2 | 0.2 | relative 1e-09 | pass |
| distance of the poles from 0 | R | 0.90483741803596 | 0.90483741803596 | relative 1e-09 | pass |
| real part of the poles | R | 0.886800911797208 | 0.886800911797208 | relative 1e-09 | pass |
| steady gain | R | 0.2 | 0.2 | relative 1e-09 | pass |

### `system.then`

**1 / (s + 1), then 1 / (s + 2): 1 / (s^2 + 3 s + 2)** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| s | exact: worked out by hand from the formula | 3 | 3 | within 1e-15 (exact formula) | pass |
| constant | exact: worked out by hand from the formula | 2 | 2 | within 1e-15 (exact formula) | pass |

**1 / (s^2 + 2 s + 5), then 1 / (s + 3)** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| denominator, s^2 | python-control series | 5 | 5 | relative 1e-12 | pass |
| denominator, s^1 | python-control series | 11 | 11 | relative 1e-12 | pass |
| denominator, s^0 | python-control series | 15 | 15 | relative 1e-12 | pass |
| numerator, s^0 | python-control series | 1 | 1 | relative 1e-12 | pass |
| denominator, s^2 | R | 5 | 5 | relative 1e-12 | pass |
| denominator, s^1 | R | 11 | 11 | relative 1e-12 | pass |
| denominator, s^0 | R | 15 | 15 | relative 1e-12 | pass |
| numerator, s^0 | R | 1 | 1 | relative 1e-12 | pass |

### `system.add`

**1 / (s + 1) and 1 / (s + 2) side by side: (2 s + 3) / (s^2 + 3 s + 2)** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top s | exact: worked out by hand from the formula | 2 | 2 | within 1e-15 (exact formula) | pass |
| top constant | exact: worked out by hand from the formula | 3 | 3 | within 1e-15 (exact formula) | pass |

**1 / (s^2 + 2 s + 5) and 1 / (s + 3) side by side** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| numerator, s^2 | python-control parallel | 1 | 1 | relative 1e-12 | pass |
| numerator, s^1 | python-control parallel | 3 | 3 | relative 1e-12 | pass |
| numerator, s^0 | python-control parallel | 8 | 8 | relative 1e-12 | pass |
| denominator, s^0 | python-control parallel | 15 | 15 | relative 1e-12 | pass |
| numerator, s^2 | R | 1 | 1 | relative 1e-12 | pass |
| numerator, s^1 | R | 3 | 3 | relative 1e-12 | pass |
| numerator, s^0 | R | 8 | 8 | relative 1e-12 | pass |
| denominator, s^0 | R | 15 | 15 | relative 1e-12 | pass |

### `system.with_feedback`

**1 / (s^2 + 2 s + 5) in a loop: 1 / (s^2 + 2 s + 6)** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| constant | exact: worked out by hand from the formula | 6 | 6 | within 1e-15 (exact formula) | pass |

**10 / (s + 10) with 1 / (0.1 s + 1) in the feedback path** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| steady gain | python-control feedback | 0.5 | 0.5 | relative 1e-09 | pass |
| poles | python-control feedback | 2 | 2 | relative 1e-09 | pass |
| biggest distance of a pole from 0 | python-control feedback | 14.142135623731 | 14.142135623731 | relative 1e-09 | pass |
| steady gain | R | 0.5 | 0.5 | relative 1e-09 | pass |
| poles | R | 2 | 2 | relative 1e-09 | pass |
| biggest distance of a pole from 0 | R | 14.142135623731 | 14.1421356237312 | relative 1e-09 | pass |

### `system.table`

**(s + 1) / (s^2 + 2 s + 5) as numbers, and in state space** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| top s^2 | exact: worked out by hand from the formula | 0 | 0 | within 0 (exact formula) | pass |
| rows of A, B, C, D | 4 + 2 + 2 + 1 numbers | 9 | 9 | within 0 (exact formula) | pass |

### `system.chart`

**the Bode chart of 1 / (s^2 + 2 s + 5): its first gain is SciPy's** (closed form; data: closed form (no data))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first gain minus its closed form | exact: 20 log10 \|1 / (5 - w^2 + 2iw)\| at the first frequency drawn | 3.5527136788005e-15 | 0 | within 1e-09 (exact formula) | pass |
| frequencies | SciPy signal.freqresp | 200 | 200 | relative 1e-12 | pass |
| first gain (decibels) | SciPy signal.freqresp | -13.9689819049622 | -13.9689819049622 | relative 1e-12 | pass |

### `autocorrelation_bars`

**the drawn sticks for the Lake Huron level are statsmodels' acf** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sticks | statsmodels acf | 19 | 19 | relative 1e-12 | pass |
| 1 year back | statsmodels acf | 0.831911210352453 | 0.831911210352453 | relative 1e-12 | pass |
| 1 year back | R | 0.831911210352453 | 0.831911210352453 | relative 1e-12 | pass |

**the yearly sunspot numbers: the correlation with 1 to 24 years back** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bars | statsmodels acf | 24 | 24 | relative 1e-09 | pass |
| 1 year back | statsmodels acf | 0.820201294420022 | 0.820201294420022 | relative 1e-09 | pass |
| 11 years back | statsmodels acf | 0.650290819840704 | 0.650290819840704 | relative 1e-09 | pass |
| 24 years back | statsmodels acf | 0.0449620792585651 | 0.0449620792585651 | relative 1e-09 | pass |
| bars | R | 24 | 24 | relative 1e-09 | pass |
| 1 year back | R | 0.820201294420022 | 0.820201294420022 | relative 1e-09 | pass |
| 11 years back | R | 0.650290819840704 | 0.650290819840703 | relative 1e-09 | pass |
| 24 years back | R | 0.0449620792585651 | 0.0449620792585652 | relative 1e-09 | pass |

### `cross_correlation_bars`

**drivers killed or injured and front-seat passengers: the drawn shift 0** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sticks | R | 25 | 25 | relative 1e-12 | pass |
| shift 0 | R | 0.888826368428162 | 0.888826368428162 | relative 1e-12 | pass |
| shift 1 | R | 0.614104086165664 | 0.614104086165664 | relative 1e-12 | pass |

Note: A stick at shift s pairs the first column at month t with the second at month t + s: R's lag -s.

**US inflation and unemployment: shifts of -4 to 4 quarters** (real data; data: US inflation and unemployment)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bars | the cross-correlation written out in NumPy (as R ccf) | 9 | 9 | relative 1e-09 | pass |
| shift -4 | the cross-correlation written out in NumPy (as R ccf) | 0.0644056902275019 | 0.0644056902275018 | relative 1e-09 | pass |
| shift 0 | the cross-correlation written out in NumPy (as R ccf) | 0.0650151415619891 | 0.0650151415619891 | relative 1e-09 | pass |
| shift 4 | the cross-correlation written out in NumPy (as R ccf) | 0.337623557792578 | 0.337623557792578 | relative 1e-09 | pass |
| bars | R | 9 | 9 | relative 1e-09 | pass |
| shift -4 | R | 0.0644056902275019 | 0.0644056902275019 | relative 1e-09 | pass |
| shift 0 | R | 0.0650151415619891 | 0.0650151415619891 | relative 1e-09 | pass |
| shift 4 | R | 0.337623557792578 | 0.337623557792577 | relative 1e-09 | pass |

### `lag_dots`

**the Lake Huron level against the year before** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | pandas shift(1) | 97 | 97 | exact | pass |
| first dot x | pandas shift(1) | 580.38 | 580.38 | exact | pass |
| first dot y | pandas shift(1) | 581.86 | 581.86 | exact | pass |

**the yearly sunspot numbers against the year before** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | NumPy (the pairs themselves) | 308 | 308 | relative 1e-12 | pass |
| sum of the year before | NumPy (the pairs themselves) | 15370.5 | 15370.5 | relative 1e-12 | pass |
| sum of the year itself | NumPy (the pairs themselves) | 15368.4 | 15368.4 | relative 1e-12 | pass |
| dots | R | 308 | 308 | relative 1e-12 | pass |
| sum of the year before | R | 15370.5 | 15370.5 | relative 1e-12 | pass |
| sum of the year itself | R | 15368.4 | 15368.4 | relative 1e-12 | pass |

### `peak_dots`

**the drivers killed or seriously injured: a dot on each peak at least 6 months apart** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | SciPy find_peaks(distance=6) | 21 | 21 | exact | pass |
| first dot (month) | SciPy find_peaks(distance=6) | 5 | 5 | exact | pass |
| highest | SciPy find_peaks(distance=6) | 2654 | 2654 | exact | pass |

**the yearly sunspot numbers: dots on the maxima of at least 150** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | SciPy signal.find_peaks | 5 | 5 | exact | pass |
| first year | SciPy signal.find_peaks | 1778 | 1778 | exact | pass |
| sum of years | SciPy signal.find_peaks | 9650 | 9650 | exact | pass |
| highest | SciPy signal.find_peaks | 190.2 | 190.2 | exact | pass |
| dots | R | 5 | 5 | exact | pass |
| first year | R | 1778 | 1778 | exact | pass |
| sum of years | R | 9650 | 9650 | exact | pass |
| highest | R | 190.2 | 190.2 | exact | pass |

### `forecast`

**the drawn forecast of the air passengers is R's** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| months drawn | R | 12 | 12 | relative 1e-09 | pass |
| January 1961 | R | 453.497721751319 | 453.497721751319 | relative 1e-09 | pass |
| December 1961 | R | 469.531518789794 | 469.531518789794 | relative 1e-09 | pass |

**El Nino sea temperatures: the next 12 months by Holt-Winters, drawn after the line** (real data; data: El Nino sea surface temperatures)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| forecast points | R | 12 | 12 | relative 1e-09 | pass |
| first month | R | 23.8701353286347 | 23.8701353286347 | relative 1e-09 | pass |
| twelfth month | R | 21.9750442568466 | 21.9750442568466 | relative 1e-09 | pass |

Note: simplydata runs R HoltWinters through forecast::forecast; the reference is HoltWinters' own predict() in base R.

### `trend_and_season`

**the air passengers in four panels: the drawn trend is R stl()'s trend** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| panels | statsmodels STL with R stl()'s settings | 4 | 4 | relative 1e-09 | pass |
| trend, January 1949 | statsmodels STL with R stl()'s settings | 122.536917649433 | 122.536917649433 | relative 1e-09 | pass |
| trend, December 1960 | statsmodels STL with R stl()'s settings | 495.992096826481 | 495.992096826481 | relative 1e-09 | pass |
| trend, January 1949 | R | 122.536917649433 | 122.536917649433 | relative 1e-09 | pass |
| trend, December 1960 | R | 495.992096826481 | 495.992096826481 | relative 1e-09 | pass |

**El Nino sea temperatures: the trend panel (season window 7)** (real data; data: El Nino sea surface temperatures)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| trend points | R | 732 | 732 | relative 1e-09 | pass |
| first trend | R | 21.4686598246004 | 21.4686598246003 | relative 1e-09 | pass |
| total trend | R | 16901.7872632438 | 16901.7872632438 | relative 1e-09 | pass |
| first season | R | 1.23199147829935 | 1.23199147829935 | relative 1e-09 | pass |

### `table.compare_counts_to`

**mtcars: are the cars spread evenly over 3, 4 and 5 gears?** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | SciPy stats.chisquare | 4.9375 | 4.9375 | relative 1e-12 | pass |
| p-value | SciPy stats.chisquare | 0.0846906561847805 | 0.0846906561847805 | relative 1e-12 | pass |
| chi-square | R | 4.9375 | 4.9375 | relative 1e-12 | pass |
| p-value | R | 0.0846906561847805 | 0.0846906561847805 | relative 1e-12 | pass |

### `table.compare_shapes_of`

**Fisher's iris: do the sepal lengths of the three species differ in shape?** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| T | SciPy stats.anderson_ksamp(midrank=True) | 51.2306560743079 | 51.2306560743079 | relative 1e-12 | pass |

Note: SciPy's midrank version is version 2 of R kSamples::ad.test(), which gives T.AD = 51.231 here.

### `table.compare_shapes_of two groups`

**Student's sleep data: do the two drugs differ in shape (tied values)?** (real data; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| D | SciPy stats.ks_2samp | 0.4 | 0.4 | relative 1e-12 | pass |
| D | R | 0.4 | 0.4 | relative 1e-12 | pass |
| p-value | R | 0.396826084132586 | 0.396826084132586 | relative 1e-12 | pass |

### `table.check_if_random_order`

**Lake Huron: do the yearly levels come in a random order?** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| z | statsmodels Runs.runs_test(correction=False) | -5.88932072818723 | -5.88932072818723 | relative 1e-12 | pass |
| runs | statsmodels Runs.runs_test(correction=False) | 21 | 21 | relative 1e-12 | pass |
| z | R | -5.88932072818723 | -5.88932072818723 | relative 1e-12 | pass |
| runs | R | 21 | 21 | relative 1e-12 | pass |

Note: The R code is the runs test of R randtests::runs.test(), written out in base R.

### `table.compare_correlations`

**Fisher's iris: sepal and petal length, setosa against versicolor** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| r in setosa | SciPy stats.pearsonr | 0.267175758868757 | 0.267175758868757 | relative 1e-12 | pass |
| r in setosa | R | 0.267175758868757 | 0.267175758868757 | relative 1e-10 | pass |
| z | R | -3.43436203811973 | -3.43436203811973 | relative 1e-10 | pass |
| p-value | R | 0.00059395033066556 | 0.00059395033066556 | relative 1e-10 | pass |

### `sdata.compare_averages`

**Student's sleep data: Welch's t-test from each drug's average, standard deviation and count** (real data; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| t | SciPy stats.ttest_ind on the rows (Welch) | -1.86081346748685 | -1.86081346748685 | relative 1e-09 | pass |
| degrees of freedom | SciPy stats.ttest_ind on the rows (Welch) | 17.7764735161785 | 17.7764735161785 | relative 1e-09 | pass |
| 95 % CI low | SciPy stats.ttest_ind on the rows (Welch) | -3.36548323071171 | -3.36548323071171 | relative 1e-09 | pass |
| t | R | -1.86081346748685 | -1.86081346748685 | relative 1e-09 | pass |
| degrees of freedom | R | 17.7764735161785 | 17.7764735161785 | relative 1e-09 | pass |
| 95 % CI low | R | -3.36548323071171 | -3.36548323071171 | relative 1e-09 | pass |

Note: The summary numbers give the same test as the rows (R t.test()).

### `sdata.compare_counts`

**dry cat food and FLUTD: the 2 x 2 table of counts** (real data; data: dry cat food and FLUTD)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | SciPy stats.chi2_contingency (Yates) | 6.85358978891301 | 6.85358978891301 | relative 1e-12 | pass |
| p-value | SciPy stats.chi2_contingency (Yates) | 0.00884633510871052 | 0.00884633510871052 | relative 1e-12 | pass |
| chi-square | R | 6.85358978891301 | 6.85358978891301 | relative 1e-10 | pass |
| p-value | R | 0.00884633510871052 | 0.0088463351087105 | relative 1e-10 | pass |

### `sdata.compare_risks`

**dry cat food and FLUTD: the risk ratio of dry food against other food** (real data; data: dry cat food and FLUTD)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| risk ratio | statsmodels Table2x2 | 4.00753676470588 | 4.00753676470588 | relative 1e-12 | pass |
| 95 % CI low | statsmodels Table2x2 | 1.43073388022936 | 1.43073388022936 | relative 1e-12 | pass |
| risk ratio | R | 4.00753676470588 | 4.00753676470588 | relative 1e-09 | pass |
| 95 % CI low | R | 1.43073388022936 | 1.43073388022936 | relative 1e-09 | pass |
| p-value | R | 0.00884633510871052 | 0.0088463351087105 | relative 1e-09 | pass |

### `sdata.compare_rates`

**Hart 1999: strokes per patient-year with warfarin and with placebo, the first trial** (real data; data: Hart 1999 (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rate ratio | statsmodels test_poisson_2indep(method="exact-cond") | 0.456480183509621 | 0.456480183509621 | relative 1e-10 | pass |
| p-value | statsmodels test_poisson_2indep(method="exact-cond") | 0.0578533500241171 | 0.0578533500241171 | relative 1e-10 | pass |
| rate ratio | R | 0.456480183509621 | 0.456480183509621 | relative 1e-09 | pass |
| 95 % CI high | R | 1.05880349446899 | 1.05880349446899 | relative 1e-09 | pass |
| p-value | R | 0.0578533500241171 | 0.0578533500241171 | relative 1e-09 | pass |

### `table.compare_to_truth`

**birthwt: the mother's smoking as a marker of a low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sensitivity | statsmodels proportion_confint(method="beta") | 0.508474576271186 | 0.508474576271186 | relative 1e-12 | pass |
| 95 % CI low | statsmodels proportion_confint(method="beta") | 0.374982549734976 | 0.374982549734976 | relative 1e-12 | pass |
| sensitivity | R | 0.508474576271186 | 0.508474576271186 | relative 1e-09 | pass |
| 95 % CI low | R | 0.374982549734976 | 0.374982549734976 | relative 1e-09 | pass |

### `table.compare_to_truth a column of numbers`

**aSAH: the AUC of s100b for a poor outcome** (real data; data: aSAH (pROC))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| AUC | R | 0.731368563685637 | 0.731368563685637 | relative 1e-12 | pass |
| 95 % CI low | R | 0.630118211761623 | 0.630118211761623 | relative 1e-12 | pass |

Note: Robin et al. (2011) show the same curve in pROC's paper (AUC 0.731).

### `table.compare_accuracy`

**birthwt: the mother's weight against her age as a marker of a low birth weight (lower scores count)** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| difference | R | 0.060560625814863 | 0.060560625814863 | relative 1e-10 | pass |
| z | R | 1.03645617956146 | 1.03645617956146 | relative 1e-10 | pass |
| p-value | R | 0.299989372716979 | 0.299989372716979 | relative 1e-10 | pass |

### `sdata.compare_to_truth`

**birthwt: smoking against a low birth weight, from the four counts** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| specificity | the shares of the counts (pandas) | 0.661538461538462 | 0.661538461538462 | relative 1e-12 | pass |
| positive likelihood ratio | the shares of the counts (pandas) | 1.50231124807396 | 1.50231124807396 | relative 1e-12 | pass |
| positive likelihood ratio | R | 1.50231124807396 | 1.50231124807396 | relative 1e-09 | pass |
| its 95 % CI low | R | 1.06140381342675 | 1.06140381342675 | relative 1e-09 | pass |

### `table.agreement_between`

**wg93: how alike do the same people answer questions A and B?** (real data; data: wg93 (ca))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| kappa | statsmodels cohens_kappa | 0.124036695399308 | 0.124036695399308 | relative 1e-12 | pass |
| z | statsmodels cohens_kappa | 7.32211646048832 | 7.32211646048832 | relative 1e-12 | pass |
| kappa | R | 0.124036695399308 | 0.124036695399308 | relative 1e-12 | pass |

### `table.agreement_between columns of numbers`

**creatinine: serum and plasma measurements of the same samples (ICC)** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| ICC | R | 0.944475141076693 | 0.944475141076693 | relative 1e-12 | pass |
| 95 % CI low | R | 0.919789592912614 | 0.919789592912614 | relative 1e-12 | pass |

### `table.limits_of_agreement`

**creatinine: serum minus plasma, the Bland-Altman limits** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| lower limit | NumPy mean and standard deviation (n - 1) | -0.314264236170878 | -0.314264236170878 | relative 1e-12 | pass |
| upper limit | NumPy mean and standard deviation (n - 1) | 0.298893865800508 | 0.298893865800508 | relative 1e-12 | pass |
| lower limit | R | -0.314264236170878 | -0.314264236170878 | relative 1e-12 | pass |
| upper limit | R | 0.298893865800508 | 0.298893865800508 | relative 1e-12 | pass |
| upper limit 95 % CI high | R | 0.350573900861587 | 0.350573900861587 | relative 1e-12 | pass |

### `table.reliability_of`

**Holzinger & Swineford: Cronbach's alpha of the three visual tests** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| alpha | NumPy, Cronbach's formula | 0.626117131884981 | 0.626117131884981 | relative 1e-12 | pass |
| alpha | R | 0.626117131884981 | 0.626117131884981 | relative 1e-12 | pass |
| 95 % CI low | R | 0.546503337102635 | 0.546503337102635 | relative 1e-12 | pass |

### `difference_dots`

**creatinine: serum minus plasma against their average, with the limits** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| dots | NumPy differences, mean and standard deviation (n - 1) | 108 | 108 | relative 1e-12 | pass |
| average difference | NumPy differences, mean and standard deviation (n - 1) | -0.00768518518518518 | -0.00768518518518518 | relative 1e-12 | pass |
| lower limit | NumPy differences, mean and standard deviation (n - 1) | -0.314264236170878 | -0.314264236170878 | relative 1e-12 | pass |
| first dot up | NumPy differences, mean and standard deviation (n - 1) | 0.0299999999999999 | 0.0299999999999999 | relative 1e-12 | pass |
| lower limit | R | -0.314264236170878 | -0.314264236170878 | relative 1e-12 | pass |
| average difference | R | -0.00768518518518518 | -0.00768518518518518 | relative 1e-12 | pass |

### `sdata.find_where_smallest`

**Michelson: the value closest to all 100 measurements (least squares) is their mean** (published; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 299.852399999994 | 299.8524 | within 1e-08 (printed rounding) | pass |
| mean | SciPy optimize.minimize_scalar(method="bounded", xatol=1e-10) | 299.852399999994 | 299.8524 | relative 1e-12 | pass |
| mean | R | 299.852399999994 | 299.8524 | relative 1e-11 | pass |

Note: The mean of the measurements makes the sum of squared distances smallest.

**Rosenbrock's valley from (-1.2, 1) by Nelder-Mead** (published; data: Rosenbrock's valley)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x | Rosenbrock (1960) | 0.999999999975851 | 1 | within 0.0001 (printed rounding) | pass |
| y | Rosenbrock (1960) | 0.999999999951727 | 1 | within 0.0001 (printed rounding) | pass |
| x | SciPy optimize.minimize (Nelder-Mead, run to 1e-10) | 0.999999999975851 | 0.999999999975851 | relative 1e-06 | pass |
| y | SciPy optimize.minimize (Nelder-Mead, run to 1e-10) | 0.999999999951727 | 0.999999999951727 | relative 1e-06 | pass |
| x | R | 0.999999999975851 | 0.999999941145949 | relative 0.001 | pass |
| y | R | 0.999999999951727 | 0.999999901357752 | relative 0.001 | pass |

Note: Nelder-Mead stops by its own rule: SciPy run to 1e-10 agrees to 1e-6; R optim's Nelder-Mead stops near the valley floor and agrees to 1e-3, the size of the step at which it stops.

### `sdata.find_where_biggest`

**Michelson: minus the sum of squared distances is biggest at the mean** (published; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 299.852399999994 | 299.8524 | within 1e-08 (printed rounding) | pass |
| mean | SciPy optimize.minimize_scalar on minus the formula | 299.852399999994 | 299.8524 | relative 1e-12 | pass |
| mean | R | 299.852399999994 | 299.8524 | relative 1e-11 | pass |

**the Wyndor Glass product mix (a linear program)** (published; data: Wyndor Glass linear program)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x1 | Hillier & Lieberman (2015) | 2 | 2 | within 1e-09 (printed rounding) | pass |
| x2 | Hillier & Lieberman (2015) | 6 | 6 | within 1e-09 (printed rounding) | pass |
| profit | Hillier & Lieberman (2015) | 36 | 36 | within 1e-09 (printed rounding) | pass |
| shadow price of plant 2 | Hillier & Lieberman (2015) | 1.5 | 1.5 | within 1e-09 (printed rounding) | pass |
| shadow price of plant 3 | Hillier & Lieberman (2015) | 1 | 1 | within 1e-09 (printed rounding) | pass |
| x1 | SciPy optimize.linprog (HiGHS) | 2 | 2 | relative 1e-09 | pass |
| x2 | SciPy optimize.linprog (HiGHS) | 6 | 6 | relative 1e-09 | pass |
| profit | SciPy optimize.linprog (HiGHS) | 36 | 36 | relative 1e-09 | pass |
| shadow price of plant 2 | SciPy optimize.linprog (HiGHS) | 1.5 | 1.5 | relative 1e-09 | pass |
| shadow price of plant 3 | SciPy optimize.linprog (HiGHS) | 1 | 1 | relative 1e-09 | pass |

### `sdata.solve`

**Michelson: the value from which the 100 measurements add up to 0 is their mean** (published; data: NIST Michelso)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| mean | NIST certified | 299.8524 | 299.8524 | within 1e-08 (printed rounding) | pass |
| solutions | exact | 1 | 1 | within 0 | pass |
| mean | SciPy optimize.brentq | 299.8524 | 299.8524 | relative 1e-12 | pass |
| mean | R | 299.8524 | 299.8524 | relative 1e-12 | pass |

**Newton's cubic x^3 - 2x = 5 between 0 and 3** (published; data: Newton's cubic)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x | Newton (1669), as printed by Ypma (1995) | 2.09455148154233 | 2.09455148 | within 5e-09 (printed rounding) | pass |
| solutions | exact | 1 | 1 | within 0 | pass |
| x | SciPy optimize.brentq | 2.09455148154233 | 2.09455148154233 | relative 1e-12 | pass |
| solutions | SciPy optimize.brentq | 1 | 1 | relative 1e-12 | pass |
| x | R | 2.09455148154233 | 2.09455148154233 | relative 1e-12 | pass |
| solutions | R | 1 | 1 | relative 1e-12 | pass |

### `table.values_at`

**Lake Huron: the level halfway between two years, and before the first year** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1900.5 | NumPy interp | 579.07 | 579.07 | relative 1e-12 | pass |
| 1950.25 | NumPy interp | 578.5275 | 578.5275 | relative 1e-12 | pass |
| empty | NumPy interp | 1 | 1 | relative 1e-12 | pass |
| 1900.5 | R | 579.07 | 579.07 | relative 1e-12 | pass |
| 1950.25 | R | 578.5275 | 578.5275 | relative 1e-12 | pass |
| empty | R | 1 | 1 | relative 1e-12 | pass |

**the yearly sunspot numbers between the years, by straight lines** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 1700.5 | NumPy interp | 8 | 8 | relative 1e-12 | pass |
| 1850.25 | NumPy interp | 66.075 | 66.075 | relative 1e-12 | pass |
| 2007.9 | NumPy interp | 3.35999999999958 | 3.35999999999958 | relative 1e-12 | pass |
| 1700.5 | R | 8 | 8 | relative 1e-12 | pass |
| 1850.25 | R | 66.075 | 66.075 | relative 1e-12 | pass |
| 2007.9 | R | 3.35999999999958 | 3.35999999999958 | relative 1e-12 | pass |

### `table.make_map_of`

**Fisher's iris: petal length over a map of sepal length and width (flat triangles)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| middle of the map | SciPy interpolate.griddata(method="linear") | 5.02 | 5.02 | relative 1e-12 | pass |
| places | SciPy interpolate.griddata(method="linear") | 25 | 25 | relative 1e-12 | pass |
| empty | SciPy interpolate.griddata(method="linear") | 15 | 15 | relative 1e-12 | pass |

Note: Several flowers share a place; their average is used, as SciPy needs distinct points.

**the yearly sunspot numbers at 5 evenly spaced years** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| places | NumPy interp on linspace | 5 | 5 | relative 1e-12 | pass |
| second place | NumPy interp on linspace | 92.5 | 92.5 | relative 1e-12 | pass |
| total | NumPy interp on linspace | 142.2 | 142.2 | relative 1e-12 | pass |
| places | R | 5 | 5 | relative 1e-12 | pass |
| second place | R | 92.5 | 92.5 | relative 1e-12 | pass |
| total | R | 142.2 | 142.2 | relative 1e-12 | pass |

### `table.compare_distributions_for`

**mtcars: horsepower, the lognormal fit among four** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| AIC | SciPy lognorm.fit(floc=0) and kstest | 358.626271880694 | 358.626271880694 | relative 1e-09 | pass |
| Kolmogorov-Smirnov statistic | SciPy lognorm.fit(floc=0) and kstest | 0.133573478600718 | 0.133573478600718 | relative 1e-09 | pass |
| AIC | R | 358.626271880694 | 358.626271880694 | relative 1e-09 | pass |
| Kolmogorov-Smirnov statistic | R | 0.133573478600718 | 0.133573478600719 | relative 1e-09 | pass |

Note: The R code is the closed-form lognormal fit of R MASS::fitdistr() and the statistic of R fitdistrplus::gofstat(), written out in base R.

### `nums.fit_distribution`

**mtcars: a gamma distribution fitted to horsepower** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| shape | SciPy gamma.fit(floc=0) | 4.86044202024079 | 4.86044202024079 | relative 1e-09 | pass |
| rate | SciPy gamma.fit(floc=0) | 0.0331346707813603 | 0.0331346707813603 | relative 1e-09 | pass |
| shape | R | 4.86044202024079 | 4.86045501592241 | relative 0.0001 | pass |
| rate | R | 0.0331346707813603 | 0.0331347694005732 | relative 0.0001 | pass |

Note: R fitdistr is given horsepower in hundreds (its search starts badly on the raw scale) and stops at its own tolerance, so it agrees to 4 digits.

### `dist.find_density_at`

**mtcars: the height of a normal curve shaped like fuel use, at 20 miles per gallon** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| density at 20 | SciPy stats.norm.pdf | 0.0661856015711465 | 0.0661856015711465 | relative 1e-14 | pass |
| density at 20 | R | 0.0661856015711465 | 0.0661856015711465 | relative 1e-12 | pass |

### `dist.find_cut_off`

**the value with a 2.5 % chance above it in the standard normal distribution** (published; data: standard normal table)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cut-off | NIST/SEMATECH e-Handbook, table 1.3.6.7.1 | 1.95996398454005 | 1.96 | within 0.005 (printed rounding) | pass |
| cut-off | SciPy stats.norm.isf | 1.95996398454005 | 1.95996398454005 | relative 1e-14 | pass |
| cut-off | R | 1.95996398454005 | 1.95996398454005 | relative 1e-14 | pass |

Note: No data: the published value is the standard normal table.

### `dist.find_middle_range`

**the middle 95 % of the standard normal distribution** (published; data: standard normal table)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| low | NIST/SEMATECH e-Handbook, table 1.3.6.7.1 | -1.95996398454005 | -1.96 | within 0.005 (printed rounding) | pass |
| high | NIST/SEMATECH e-Handbook, table 1.3.6.7.1 | 1.95996398454005 | 1.96 | within 0.005 (printed rounding) | pass |
| low | SciPy stats.norm.ppf and isf | -1.95996398454005 | -1.95996398454005 | relative 1e-14 | pass |
| high | SciPy stats.norm.ppf and isf | 1.95996398454005 | 1.95996398454005 | relative 1e-14 | pass |
| low | R | -1.95996398454005 | -1.95996398454005 | relative 1e-14 | pass |
| high | R | 1.95996398454005 | 1.95996398454005 | relative 1e-14 | pass |

Note: No data: the published value is the standard normal table.

### `dist.find_average`

**mtcars: the average of a gamma distribution shaped like horsepower (moments)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average | SciPy stats.gamma.mean | 146.6875 | 146.6875 | relative 1e-14 | pass |
| average | R | 146.6875 | 146.6875 | relative 1e-12 | pass |

Note: The shape and rate come from the average and variance of horsepower, so the average is theirs.

### `dist.find_median`

**mtcars: the median of a gamma distribution shaped like horsepower** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| median | SciPy stats.gamma.median | 136.154678864025 | 136.154678864025 | relative 1e-14 | pass |
| median | R | 136.154678864025 | 136.154678864025 | relative 1e-10 | pass |

### `dist.find_standard_deviation`

**mtcars: the standard deviation of a gamma distribution shaped like horsepower** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| standard deviation | SciPy stats.gamma.std | 68.5628684893206 | 68.5628684893206 | relative 1e-14 | pass |
| standard deviation | R | 68.5628684893206 | 68.5628684893206 | relative 1e-12 | pass |

### `dist.find_variance`

**mtcars: the variance of a gamma distribution shaped like horsepower** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| variance | SciPy stats.gamma.var | 4700.86693548387 | 4700.86693548387 | relative 1e-14 | pass |
| variance | R | 4700.86693548387 | 4700.86693548387 | relative 1e-12 | pass |

Note: Shaped by its moments, the distribution has the variance of horsepower itself.

### `dist.show_summary`

**mtcars: the skewness and excess kurtosis of a gamma distribution shaped like horsepower** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| skewness | SciPy stats.gamma.stats(moments="mvsk") | 0.934815420391248 | 0.934815420391248 | relative 1e-14 | pass |
| excess kurtosis | SciPy stats.gamma.stats(moments="mvsk") | 1.3108198053019 | 1.3108198053019 | relative 1e-14 | pass |
| skewness | R | 0.934815420391248 | 0.934815420391248 | relative 1e-12 | pass |
| excess kurtosis | R | 1.3108198053019 | 1.3108198053019 | relative 1e-12 | pass |

### `dist.make_random_numbers`

**mtcars: random numbers from a normal curve shaped like fuel use, seed 1** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | SciPy stats.norm.rvs with NumPy default_rng(1) | 22.1734429731977 | 22.1734429731977 | relative 1e-12 | pass |
| total | SciPy stats.norm.rvs with NumPy default_rng(1) | 637.00996748002 | 637.00996748002 | relative 1e-12 | pass |

Note: Random numbers have no published answer; the check is that the same seed gives SciPy's numbers.

### `dist.draw_chart`

**mtcars: the curve of a normal distribution shaped like fuel use** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first x | SciPy ppf and pdf on 200 places (matplotlib draws them) | 1.46595542183908 | 1.46595542183908 | relative 1e-12 | pass |
| last x | SciPy ppf and pdf on 200 places (matplotlib draws them) | 38.7152945781609 | 38.7152945781609 | relative 1e-12 | pass |
| points | SciPy ppf and pdf on 200 places (matplotlib draws them) | 200 | 200 | relative 1e-12 | pass |
| highest | SciPy ppf and pdf on 200 places (matplotlib draws them) | 0.0661851037414739 | 0.0661851037414739 | relative 1e-12 | pass |
| first x | R | 1.46595542183908 | 1.46595542183908 | relative 1e-12 | pass |
| last x | R | 38.7152945781609 | 38.7152945781609 | relative 1e-12 | pass |

### `dist.turn_into_table`

**mtcars: a normal distribution shaped like fuel use, as a table** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average | pandas mean and std | 20.090625 | 20.090625 | relative 1e-14 | pass |
| standard deviation | pandas mean and std | 6.0269480520891 | 6.0269480520891 | relative 1e-14 | pass |
| average | R | 20.090625 | 20.090625 | relative 1e-12 | pass |
| standard deviation | R | 6.0269480520891 | 6.0269480520891 | relative 1e-12 | pass |

### `table.find_principal_components_of`

**Fisher's iris: the principal components of the four measurements** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| PC1 standard deviation | NumPy linalg.svd | 1.70836114932762 | 1.70836114932762 | relative 1e-12 | pass |
| PC1 share (%) | NumPy linalg.svd | 72.9624454132999 | 72.9624454132999 | relative 1e-12 | pass |
| PC1 weight of petal length | NumPy linalg.svd | 0.580413095796295 | 0.580413095796295 | relative 1e-12 | pass |
| PC1 standard deviation | R | 1.70836114932762 | 1.70836114932762 | relative 1e-12 | pass |
| PC1 share (%) | R | 72.9624454132999 | 72.9624454132999 | relative 1e-12 | pass |
| PC1 weight of petal length | R | 0.580413095796295 | 0.580413095796295 | relative 1e-12 | pass |

Note: The sign of a component is arbitrary, so the weight is compared without its sign.

### `table.show_last_rows`

**the last 3 of Fisher's 150 iris flowers, numbered 148 to 150** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows shown | pandas tail | 3 | 3 | relative 1e-12 | pass |
| first row number | pandas tail | 148 | 148 | relative 1e-12 | pass |
| sepal length total | pandas tail | 18.6 | 18.6 | relative 1e-12 | pass |
| rows shown | R | 3 | 3 | relative 1e-12 | pass |
| first row number | R | 148 | 148 | relative 1e-12 | pass |
| sepal length total | R | 18.6 | 18.6 | relative 1e-12 | pass |

### `table.show`

**all 144 months of AirPassengers shown, numbered from 1** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows shown | pandas (every row) | 144 | 144 | exact | pass |
| last row number | pandas (every row) | 144 | 144 | exact | pass |
| total passengers | pandas (every row) | 40363 | 40363 | exact | pass |
| rows shown | R | 144 | 144 | exact | pass |
| total passengers | R | 40363 | 40363 | exact | pass |

### `table.get_column_names`

**the 12 column names of mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas columns | 12 | 12 | exact | pass |
| mpg is second | pandas columns | 1 | 1 | exact | pass |

### `table.get_column`

**NHANES body mass index taken out as numbers, with its 9 empty cells** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| values | pandas to_numpy | 25 | 25 | relative 1e-12 | pass |
| empty | pandas to_numpy | 9 | 9 | relative 1e-12 | pass |
| total | pandas to_numpy | 425 | 425 | relative 1e-12 | pass |
| values | R | 25 | 25 | relative 1e-12 | pass |
| empty | R | 9 | 9 | relative 1e-12 | pass |
| total | R | 425 | 425 | relative 1e-12 | pass |

### `table.get_row`

**the first NHANES person: an age and three empty cells** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| age group | pandas iloc[0] | 1 | 1 | exact | pass |
| empty cells | pandas iloc[0] | 3 | 3 | exact | pass |
| age group | R | 1 | 1 | exact | pass |
| empty cells | R | 3 | 3 | exact | pass |

### `table.get_cell_at`

**the horsepower of the third car in mtcars (Datsun 710)** (published; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| hp | Henderson & Velleman (1981) | 93 | 93 | within 0 (printed rounding) | pass |
| hp | pandas iloc[2] | 93 | 93 | exact | pass |
| hp | R | 93 | 93 | exact | pass |

### `table.remove_columns`

**mtcars without the car names** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas drop(columns=) | 11 | 11 | relative 1e-12 | pass |
| total mpg | pandas drop(columns=) | 642.9 | 642.9 | relative 1e-12 | pass |

### `table.keep_columns_by_position`

**columns 2 to 4 of mtcars (mpg, cyl, disp)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas iloc[:, 1:4] | 3 | 3 | relative 1e-12 | pass |
| total disp | pandas iloc[:, 1:4] | 7383.1 | 7383.1 | relative 1e-12 | pass |
| columns | R | 3 | 3 | relative 1e-12 | pass |
| total disp | R | 7383.1 | 7383.1 | relative 1e-12 | pass |

### `table.remove_columns_by_position`

**mtcars without its first column (the car names)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas drop(columns=) | 11 | 11 | exact | pass |
| mpg is first | pandas drop(columns=) | 1 | 1 | exact | pass |

### `table.remove_rows_where`

**NHANES: people with a body mass index below 25 removed (empty cells stay)** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows left | pandas boolean indexing | 19 | 19 | relative 1e-12 | pass |
| empty left | pandas boolean indexing | 9 | 9 | relative 1e-12 | pass |
| total | pandas boolean indexing | 290.8 | 290.8 | relative 1e-12 | pass |
| rows left | R | 19 | 19 | relative 1e-12 | pass |
| empty left | R | 9 | 9 | relative 1e-12 | pass |
| total | R | 290.8 | 290.8 | relative 1e-12 | pass |

### `table.keep_first_rows`

**the first 10 cars of mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas head | 10 | 10 | relative 1e-12 | pass |
| total mpg | pandas head | 203.7 | 203.7 | relative 1e-12 | pass |
| rows | R | 10 | 10 | relative 1e-12 | pass |
| total mpg | R | 203.7 | 203.7 | relative 1e-12 | pass |

### `table.keep_last_rows`

**the last 10 cars of mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas tail | 10 | 10 | relative 1e-12 | pass |
| total mpg | pandas tail | 203.3 | 203.3 | relative 1e-12 | pass |
| rows | R | 10 | 10 | relative 1e-12 | pass |
| total mpg | R | 203.3 | 203.3 | relative 1e-12 | pass |

### `table.remove_rows_by_position`

**mtcars without its first and last car** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas drop(index=) | 30 | 30 | relative 1e-12 | pass |
| total mpg | pandas drop(index=) | 600.5 | 600.5 | relative 1e-12 | pass |
| rows | R | 30 | 30 | relative 1e-12 | pass |
| total mpg | R | 600.5 | 600.5 | relative 1e-12 | pass |

### `table.reverse_rows`

**AirPassengers turned upside down: the last month first** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | pandas iloc[::-1] | 432 | 432 | exact | pass |
| last | pandas iloc[::-1] | 112 | 112 | exact | pass |
| first | R | 432 | 432 | exact | pass |
| last | R | 112 | 112 | exact | pass |

### `table.remove_duplicate_rows`

**mtcars: the first car of each number of cylinders** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas drop_duplicates | 3 | 3 | relative 1e-12 | pass |
| total mpg | pandas drop_duplicates | 62.5 | 62.5 | relative 1e-12 | pass |
| rows | R | 3 | 3 | relative 1e-12 | pass |
| total mpg | R | 62.5 | 62.5 | relative 1e-12 | pass |

### `table.keep_biggest_rows`

**mtcars: the 3 most powerful cars for each number of cylinders (in 8 cylinders two cars tie at 245 hp for third place)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas sort_values (stable) and groupby().head() | 9 | 9 | exact | pass |
| total hp | pandas sort_values (stable) and groupby().head() | 1584 | 1584 | exact | pass |
| first hp | pandas sort_values (stable) and groupby().head() | 113 | 113 | exact | pass |
| third 8-cylinder hp | pandas sort_values (stable) and groupby().head() | 245 | 245 | exact | pass |
| row of the third 8-cylinder car | pandas sort_values (stable) and groupby().head() | 7 | 7 | exact | pass |
| total hp | R | 1584 | 1584 | exact | pass |
| first hp | R | 113 | 113 | exact | pass |
| third 8-cylinder hp | R | 245 | 245 | exact | pass |
| row of the third 8-cylinder car | R | 7 | 7 | exact | pass |

### `table.keep_smallest_rows`

**mtcars: the 3 thirstiest cars for each number of cylinders** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas sort_values (stable) and groupby().head() | 9 | 9 | relative 1e-12 | pass |
| total mpg | pandas sort_values (stable) and groupby().head() | 154.9 | 154.9 | relative 1e-12 | pass |
| first mpg | pandas sort_values (stable) and groupby().head() | 21.4 | 21.4 | relative 1e-12 | pass |
| total mpg | R | 154.9 | 154.9 | relative 1e-12 | pass |
| first mpg | R | 21.4 | 21.4 | relative 1e-12 | pass |

### `table.remove_rows_with_outliers`

**mtcars horsepower: Tukey's outliers within each number of cylinders removed** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows left | pandas quantile (linear) and Tukey's rule | 31 | 31 | exact | pass |
| total hp | pandas quantile (linear) and Tukey's rule | 4519 | 4519 | exact | pass |
| rows left | R | 31 | 31 | exact | pass |
| total hp | R | 4519 | 4519 | exact | pass |

### `table.remove_rows_with_empty_cells_in`

**NHANES: the people without a body mass index removed** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows left | pandas dropna(subset=) | 16 | 16 | relative 1e-12 | pass |
| total | pandas dropna(subset=) | 425 | 425 | relative 1e-12 | pass |
| rows left | R | 16 | 16 | relative 1e-12 | pass |
| total | R | 425 | 425 | relative 1e-12 | pass |

### `table.add_is_empty_column`

**NHANES: which people have no cholesterol value** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| empty | pandas isna | 10 | 10 | exact | pass |
| rows | pandas isna | 25 | 25 | exact | pass |
| empty | R | 10 | 10 | exact | pass |
| rows | R | 25 | 25 | exact | pass |

### `table.turn_into_text`

**mtcars miles per gallon written as text** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells reading 21.0 | pandas astype(str) | 2 | 2 | exact | pass |
| cells reading 10.4 | pandas astype(str) | 2 | 2 | exact | pass |

### `table.turn_into_dates`

**the 144 months of AirPassengers read as dates** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first year | pandas to_datetime | 1949 | 1949 | exact | pass |
| last year | pandas to_datetime | 1960 | 1960 | exact | pass |
| last month | pandas to_datetime | 12 | 12 | exact | pass |
| first year | R | 1949 | 1949 | exact | pass |
| last year | R | 1960 | 1960 | exact | pass |
| last month | R | 12 | 12 | exact | pass |

### `table.turn_into_lowercase`

**warpbreaks: the wool types written in small letters** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| a | pandas str.lower | 27 | 27 | exact | pass |
| b | pandas str.lower | 27 | 27 | exact | pass |
| a | R | 27 | 27 | exact | pass |
| b | R | 27 | 27 | exact | pass |

### `table.turn_into_uppercase`

**iris: the species written in capital letters** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| SETOSA | pandas str.upper | 50 | 50 | exact | pass |
| VIRGINICA | pandas str.upper | 50 | 50 | exact | pass |
| SETOSA | R | 50 | 50 | exact | pass |
| VIRGINICA | R | 50 | 50 | exact | pass |

### `table.round_numbers_in`

**mtcars weights rounded to 1 decimal** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas round | 102.7 | 102.7 | relative 1e-12 | pass |
| first | pandas round | 2.6 | 2.6 | relative 1e-12 | pass |

### `table.change_column`

**mtcars miles per gallon changed into kilometres per litre** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas multiplication | 273.3250776 | 273.3250776 | relative 1e-12 | pass |
| cars | pandas multiplication | 32 | 32 | relative 1e-12 | pass |
| total | R | 273.3250776 | 273.3250776 | relative 1e-12 | pass |

### `table.add_rank_column`

**mtcars cars ranked by fuel use, ties sharing the best place** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first car | pandas rank(method="min") | 13 | 13 | exact | pass |
| sum of places | pandas rank(method="min") | 521 | 521 | exact | pass |
| first car | R | 13 | 13 | exact | pass |
| sum of places | R | 521 | 521 | exact | pass |

### `table.add_column_with_part_of_date`

**AirPassengers: the weekday of the first day of each month (1 is Monday)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas dt.dayofweek + 1 | 578 | 578 | exact | pass |
| first | pandas dt.dayofweek + 1 | 6 | 6 | exact | pass |
| total | R | 578 | 578 | exact | pass |
| first | R | 6 | 6 | exact | pass |

### `table.add_column_with_part_of_text`

**mtcars: the make of each car, the text before the first space** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Merc | pandas str.extract | 7 | 7 | exact | pass |
| Toyota | pandas str.extract | 2 | 2 | exact | pass |
| empty | pandas str.extract | 1 | 1 | exact | pass |
| Merc | R | 7 | 7 | exact | pass |
| Toyota | R | 2 | 2 | exact | pass |
| empty | R | 1 | 1 | exact | pass |

### `table.split_column`

**mtcars car names split into the make and the rest** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Merc | pandas str.split(n=1) | 7 | 7 | exact | pass |
| no type | pandas str.split(n=1) | 1 | 1 | exact | pass |
| columns | pandas str.split(n=1) | 13 | 13 | exact | pass |

### `table.replace_text_in`

**mtcars: Merc written out as Mercedes in the car names** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| with Mercedes | pandas str.replace(regex=False) | 7 | 7 | exact | pass |
| Mercedes 240D | pandas str.replace(regex=False) | 1 | 1 | exact | pass |
| with Mercedes | R | 7 | 7 | exact | pass |
| Mercedes 240D | R | 1 | 1 | exact | pass |

### `table.add_previous_value_column`

**AirPassengers: each month beside the month before** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| empty | pandas shift(1) | 1 | 1 | exact | pass |
| total | pandas shift(1) | 39931 | 39931 | exact | pass |
| row 2 | pandas shift(1) | 112 | 112 | exact | pass |
| empty | R | 1 | 1 | exact | pass |
| total | R | 39931 | 39931 | exact | pass |
| row 2 | R | 112 | 112 | exact | pass |

### `table.add_change_column`

**AirPassengers: the change from the month before, in percent** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| last | pandas shift(1) | 10.7692307692308 | 10.7692307692308 | relative 1e-12 | pass |
| total | pandas shift(1) | 216.910059911928 | 216.910059911928 | relative 1e-12 | pass |
| empty | pandas shift(1) | 1 | 1 | relative 1e-12 | pass |
| last | R | 10.7692307692308 | 10.7692307692308 | relative 1e-12 | pass |
| total | R | 216.910059911928 | 216.910059911928 | relative 1e-12 | pass |
| empty | R | 1 | 1 | relative 1e-12 | pass |

### `table.find_smallest_of`

**the shortest sepal of each iris species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| setosa | pandas groupby().min() | 4.3 | 4.3 | exact | pass |
| versicolor | pandas groupby().min() | 4.9 | 4.9 | exact | pass |
| virginica | pandas groupby().min() | 4.9 | 4.9 | exact | pass |
| setosa | R | 4.3 | 4.3 | exact | pass |
| versicolor | R | 4.9 | 4.9 | exact | pass |
| virginica | R | 4.9 | 4.9 | exact | pass |

### `table.find_biggest_of`

**the most powerful car in mtcars (Maserati Bora, 335 hp)** (published; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| hp | Henderson & Velleman (1981) | 335 | 335 | within 0 (printed rounding) | pass |
| hp | pandas max | 335 | 335 | exact | pass |
| hp | R | 335 | 335 | exact | pass |

### `table.find_standard_deviation_of`

**the spread of petal length in each iris species (n - 1)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| setosa | pandas groupby().std(ddof=1) | 0.173663996480184 | 0.173663996480184 | relative 1e-12 | pass |
| versicolor | pandas groupby().std(ddof=1) | 0.469910977239958 | 0.469910977239958 | relative 1e-12 | pass |
| virginica | pandas groupby().std(ddof=1) | 0.551894695663984 | 0.551894695663984 | relative 1e-12 | pass |
| setosa | R | 0.173663996480184 | 0.173663996480184 | relative 1e-12 | pass |
| versicolor | R | 0.469910977239958 | 0.469910977239958 | relative 1e-12 | pass |
| virginica | R | 0.551894695663984 | 0.551894695663983 | relative 1e-12 | pass |

### `table.count_different_values_in`

**NHANES: how many different body mass index values (empty cells not counted)** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| different values | pandas nunique | 16 | 16 | exact | pass |
| different values | R | 16 | 16 | exact | pass |

### `table.find_most_common_of`

**the most common number of cylinders in mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| most common | pandas mode | 8 | 8 | exact | pass |
| most common | R | 8 | 8 | exact | pass |

### `table.find_interval_of`

**mtcars miles per gallon: the average with a 95 % BCa bootstrap interval** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average | SciPy stats.bootstrap (BCa, 9999 resamples, seed 1) | 20.090625 | 20.090625 | relative 1e-12 | pass |
| low | SciPy stats.bootstrap (BCa, 9999 resamples, seed 1) | 18.225 | 18.225 | relative 1e-12 | pass |
| high | SciPy stats.bootstrap (BCa, 9999 resamples, seed 1) | 22.3451879927405 | 22.3451879927405 | relative 1e-12 | pass |

Note: R boot::boot.ci() draws other random rows, so only SciPy, with the same seed, gives the same interval.

### `table.add_rows_from`

**Fisher's iris data put under itself** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas concat | 300 | 300 | relative 1e-12 | pass |
| total petal width | pandas concat | 359.8 | 359.8 | relative 1e-12 | pass |
| rows | R | 300 | 300 | relative 1e-12 | pass |
| total petal width | R | 359.8 | 359.8 | relative 1e-12 | pass |

### `table.gather_into_rows`

**iris sepal length and width turned into rows** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas melt | 300 | 300 | relative 1e-12 | pass |
| total | pandas melt | 1335.1 | 1335.1 | relative 1e-12 | pass |
| columns | pandas melt | 5 | 5 | relative 1e-12 | pass |
| rows | R | 300 | 300 | relative 1e-12 | pass |
| total | R | 1335.1 | 1335.1 | relative 1e-12 | pass |

### `table.spread_into_columns`

**Student's sleep data: one row for each patient, a column for each drug** (published; data: Student's sleep data)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| average drug 2 | Student (1908) | 2.33 | 2.33 | within 0.005 (printed rounding) | pass |
| patients | pandas pivot | 10 | 10 | relative 1e-12 | pass |
| average drug 2 | pandas pivot | 2.33 | 2.33 | relative 1e-12 | pass |
| patient 1 drug 1 | pandas pivot | 0.7 | 0.7 | relative 1e-12 | pass |
| average drug 2 | R | 2.33 | 2.33 | relative 1e-12 | pass |
| patient 1 drug 1 | R | 0.7 | 0.7 | relative 1e-12 | pass |

### `table.swap_rows_and_columns`

**mtcars miles per gallon and horsepower, one column for each of the 32 cars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas set_index().T | 33 | 33 | exact | pass |
| rows | pandas set_index().T | 2 | 2 | exact | pass |
| Mazda RX4 mpg | pandas set_index().T | 21 | 21 | exact | pass |
| Volvo 142E hp | pandas set_index().T | 109 | 109 | exact | pass |
| rows | R | 2 | 2 | exact | pass |
| Mazda RX4 mpg | R | 21 | 21 | exact | pass |
| Volvo 142E hp | R | 109 | 109 | exact | pass |

### `table.make_copy`

**Fisher's iris: a copy keeps all 150 flowers after the table keeps the 50 setosa** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| table rows | pandas copy() | 50 | 50 | relative 1e-12 | pass |
| copy rows | pandas copy() | 150 | 150 | relative 1e-12 | pass |
| copy sepal length total | pandas copy() | 876.5 | 876.5 | relative 1e-12 | pass |
| table rows | R | 50 | 50 | relative 1e-12 | pass |
| copy rows | R | 150 | 150 | relative 1e-12 | pass |
| copy sepal length total | R | 876.5 | 876.5 | relative 1e-12 | pass |

### `table.count_empty_cells_in columns=`

**NHANES: the empty cells of bmi, hyp and chl (9, 8 and 10)** (published; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bmi | van Buuren & Groothuis-Oudshoorn (2011) | 9 | 9 | within 0 (printed rounding) | pass |
| hyp | van Buuren & Groothuis-Oudshoorn (2011) | 8 | 8 | within 0 (printed rounding) | pass |
| chl | van Buuren & Groothuis-Oudshoorn (2011) | 10 | 10 | within 0 (printed rounding) | pass |
| bmi | pandas isna().sum() | 9 | 9 | exact | pass |
| hyp | pandas isna().sum() | 8 | 8 | exact | pass |
| chl | pandas isna().sum() | 10 | 10 | exact | pass |
| columns shown | pandas isna().sum() | 3 | 3 | exact | pass |
| bmi | R | 9 | 9 | exact | pass |
| hyp | R | 8 | 8 | exact | pass |
| chl | R | 10 | 10 | exact | pass |

### `sdata.run_sql`

**mtcars saved as a CSV file and summed up by DuckDB: cars, average mpg and the most horsepower for each number of cylinders** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| 4 cylinders: cars | DuckDB (the same SELECT on the same file) | 11 | 11 | relative 1e-12 | pass |
| 4 cylinders: average mpg | DuckDB (the same SELECT on the same file) | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |
| 4 cylinders: most hp | DuckDB (the same SELECT on the same file) | 113 | 113 | relative 1e-12 | pass |
| 6 cylinders: cars | DuckDB (the same SELECT on the same file) | 7 | 7 | relative 1e-12 | pass |
| 6 cylinders: average mpg | DuckDB (the same SELECT on the same file) | 19.7428571428571 | 19.7428571428571 | relative 1e-12 | pass |
| 6 cylinders: most hp | DuckDB (the same SELECT on the same file) | 175 | 175 | relative 1e-12 | pass |
| 8 cylinders: cars | DuckDB (the same SELECT on the same file) | 14 | 14 | relative 1e-12 | pass |
| 8 cylinders: average mpg | DuckDB (the same SELECT on the same file) | 15.1 | 15.1 | relative 1e-12 | pass |
| 8 cylinders: most hp | DuckDB (the same SELECT on the same file) | 335 | 335 | relative 1e-12 | pass |
| 4 cylinders: cars | R | 11 | 11 | relative 1e-12 | pass |
| 6 cylinders: cars | R | 7 | 7 | relative 1e-12 | pass |
| 8 cylinders: cars | R | 14 | 14 | relative 1e-12 | pass |
| 4 cylinders: average mpg | R | 26.6636363636364 | 26.6636363636364 | relative 1e-12 | pass |
| 6 cylinders: average mpg | R | 19.7428571428571 | 19.7428571428571 | relative 1e-12 | pass |
| 8 cylinders: average mpg | R | 15.1 | 15.1 | relative 1e-12 | pass |
| 4 cylinders: most hp | R | 113 | 113 | relative 1e-12 | pass |
| 6 cylinders: most hp | R | 175 | 175 | relative 1e-12 | pass |
| 8 cylinders: most hp | R | 335 | 335 | relative 1e-12 | pass |

### `table.run_sql`

**iris: the average sepal length and the flowers of each species, by SQL** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| setosa: average sepal length | DuckDB (register, then the same SELECT) | 5.006 | 5.006 | relative 1e-12 | pass |
| setosa: flowers | DuckDB (register, then the same SELECT) | 50 | 50 | relative 1e-12 | pass |
| versicolor: average sepal length | DuckDB (register, then the same SELECT) | 5.936 | 5.936 | relative 1e-12 | pass |
| versicolor: flowers | DuckDB (register, then the same SELECT) | 50 | 50 | relative 1e-12 | pass |
| virginica: average sepal length | DuckDB (register, then the same SELECT) | 6.588 | 6.588 | relative 1e-12 | pass |
| virginica: flowers | DuckDB (register, then the same SELECT) | 50 | 50 | relative 1e-12 | pass |
| setosa: average sepal length | R | 5.006 | 5.006 | relative 1e-12 | pass |
| versicolor: average sepal length | R | 5.936 | 5.936 | relative 1e-12 | pass |
| virginica: average sepal length | R | 6.588 | 6.588 | relative 1e-12 | pass |
| setosa: flowers | R | 50 | 50 | relative 1e-12 | pass |
| versicolor: flowers | R | 50 | 50 | relative 1e-12 | pass |
| virginica: flowers | R | 50 | 50 | relative 1e-12 | pass |

**iris: the average sepal length and the flowers of each species, by SQL (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| setosa: average sepal length | DuckDB (register, then the same SELECT) | 5.006 | 5.006 | relative 1e-12 | pass |
| setosa: flowers | DuckDB (register, then the same SELECT) | 50 | 50 | relative 1e-12 | pass |
| versicolor: average sepal length | DuckDB (register, then the same SELECT) | 5.936 | 5.936 | relative 1e-12 | pass |
| versicolor: flowers | DuckDB (register, then the same SELECT) | 50 | 50 | relative 1e-12 | pass |
| virginica: average sepal length | DuckDB (register, then the same SELECT) | 6.588 | 6.588 | relative 1e-12 | pass |
| virginica: flowers | DuckDB (register, then the same SELECT) | 50 | 50 | relative 1e-12 | pass |

### `table.add_column counted_in=`

**AirPassengers: whole weeks from January 1949 to the start of each month** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total weeks | pandas (end - start) / pd.Timedelta(weeks=1), whole weeks | 44685 | 44685 | exact | pass |
| February | pandas (end - start) / pd.Timedelta(weeks=1), whole weeks | 4 | 4 | exact | pass |
| last month | pandas (end - start) / pd.Timedelta(weeks=1), whole weeks | 621 | 621 | exact | pass |
| total weeks | R | 44685 | 44685 | exact | pass |
| February | R | 4 | 4 | exact | pass |
| last month | R | 621 | 621 | exact | pass |

**AirPassengers: whole weeks from January 1949 to the start of each month (a Polars table)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total weeks | Polars (end - start).dt.total_days() // 7 | 44685 | 44685 | exact | pass |
| February | Polars (end - start).dt.total_days() // 7 | 4 | 4 | exact | pass |
| last month | Polars (end - start).dt.total_days() // 7 | 621 | 621 | exact | pass |

### `table.add_group_column into_equal_groups=`

**mtcars miles per gallon in four equal groups (quarters)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cars in quarter 1 | pandas qcut(4) | 8 | 8 | exact | pass |
| cars in quarter 2 | pandas qcut(4) | 9 | 9 | exact | pass |
| cars in quarter 3 | pandas qcut(4) | 8 | 8 | exact | pass |
| cars in quarter 4 | pandas qcut(4) | 7 | 7 | exact | pass |
| quarter of each car (sum of row x quarter) | pandas qcut(4) | 1303 | 1303 | exact | pass |
| cars in quarter 1 | R | 8 | 8 | exact | pass |
| cars in quarter 2 | R | 9 | 9 | exact | pass |
| cars in quarter 3 | R | 8 | 8 | exact | pass |
| cars in quarter 4 | R | 7 | 7 | exact | pass |
| quarter of each car (sum of row x quarter) | R | 1303 | 1303 | exact | pass |

**mtcars miles per gallon in four equal groups (quarters) (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cars in quarter 1 | Polars qcut(4) | 8 | 8 | exact | pass |
| cars in quarter 2 | Polars qcut(4) | 9 | 9 | exact | pass |
| cars in quarter 3 | Polars qcut(4) | 8 | 8 | exact | pass |
| cars in quarter 4 | Polars qcut(4) | 7 | 7 | exact | pass |
| quarter of each car (sum of row x quarter) | Polars qcut(4) | 1303 | 1303 | exact | pass |

### `table.add_missing_combinations_of`

**mtcars: the one missing pair of cylinders and gears (8 cylinders, 4 gears) added as a row** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas MultiIndex.from_product, merge(indicator=True), concat, sort_values (stable) | 33 | 33 | exact | pass |
| empty mpg | pandas MultiIndex.from_product, merge(indicator=True), concat, sort_values (stable) | 1 | 1 | exact | pass |
| row of the new pair | pandas MultiIndex.from_product, merge(indicator=True), concat, sort_values (stable) | 31 | 31 | exact | pass |
| its cylinders | pandas MultiIndex.from_product, merge(indicator=True), concat, sort_values (stable) | 8 | 8 | exact | pass |
| its gears | pandas MultiIndex.from_product, merge(indicator=True), concat, sort_values (stable) | 4 | 4 | exact | pass |
| rows | R | 33 | 33 | exact | pass |
| empty mpg | R | 1 | 1 | exact | pass |
| row of the new pair | R | 31 | 31 | exact | pass |
| its cylinders | R | 8 | 8 | exact | pass |
| its gears | R | 4 | 4 | exact | pass |

**mtcars: the one missing pair of cylinders and gears (8 cylinders, 4 gears) added as a row (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars join(how="cross"), join(how="anti"), concat, sort | 33 | 33 | exact | pass |
| empty mpg | Polars join(how="cross"), join(how="anti"), concat, sort | 1 | 1 | exact | pass |
| row of the new pair | Polars join(how="cross"), join(how="anti"), concat, sort | 31 | 31 | exact | pass |
| its cylinders | Polars join(how="cross"), join(how="anti"), concat, sort | 8 | 8 | exact | pass |
| its gears | Polars join(how="cross"), join(how="anti"), concat, sort | 4 | 4 | exact | pass |

### `table.add_rank_column when_tied=`

**mtcars: each car's place for fuel use within its number of cylinders, ties sharing the average place** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sum of places | pandas groupby().rank(method="average") | 199 | 199 | exact | pass |
| Mazda RX4 | pandas groupby().rank(method="average") | 2.5 | 2.5 | exact | pass |
| Mazda RX4 Wag | pandas groupby().rank(method="average") | 2.5 | 2.5 | exact | pass |
| sum of row x place | pandas groupby().rank(method="average") | 3436 | 3436 | exact | pass |
| sum of places | R | 199 | 199 | exact | pass |
| Mazda RX4 | R | 2.5 | 2.5 | exact | pass |
| Mazda RX4 Wag | R | 2.5 | 2.5 | exact | pass |
| sum of row x place | R | 3436 | 3436 | exact | pass |

**mtcars: each car's place for fuel use within its number of cylinders, ties sharing the average place (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sum of places | Polars rank("average").over() | 199 | 199 | exact | pass |
| Mazda RX4 | Polars rank("average").over() | 2.5 | 2.5 | exact | pass |
| Mazda RX4 Wag | Polars rank("average").over() | 2.5 | 2.5 | exact | pass |
| sum of row x place | Polars rank("average").over() | 3436 | 3436 | exact | pass |

### `table.add_row_number_column`

**mtcars: the cars numbered from the least powerful within each number of cylinders (ties keep the table's order)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| biggest number | pandas sort_values (stable), groupby().cumcount() + 1 | 14 | 14 | exact | pass |
| sum of row x number | pandas sort_values (stable), groupby().cumcount() + 1 | 3754 | 3754 | exact | pass |
| biggest number | R | 14 | 14 | exact | pass |
| sum of row x number | R | 3754 | 3754 | exact | pass |

**mtcars: the cars numbered from the least powerful within each number of cylinders (ties keep the table's order) (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| biggest number | Polars int_range(1, len() + 1).over(order_by=) | 14 | 14 | exact | pass |
| sum of row x number | Polars int_range(1, len() + 1).over(order_by=) | 3754 | 3754 | exact | pass |

### `table.add_row_summary_column`

**iris: the average of the four measurements of each flower** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas mean(axis=1) | 519.675 | 519.675 | relative 1e-12 | pass |
| first flower | pandas mean(axis=1) | 2.55 | 2.55 | relative 1e-12 | pass |
| last flower | pandas mean(axis=1) | 3.95 | 3.95 | relative 1e-12 | pass |
| total | R | 519.675 | 519.675 | relative 1e-12 | pass |
| first flower | R | 2.55 | 2.55 | relative 1e-12 | pass |
| last flower | R | 3.95 | 3.95 | relative 1e-12 | pass |

**iris: the average of the four measurements of each flower (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | Polars mean_horizontal | 519.675 | 519.675 | relative 1e-12 | pass |
| first flower | Polars mean_horizontal | 2.55 | 2.55 | relative 1e-12 | pass |
| last flower | Polars mean_horizontal | 3.95 | 3.95 | relative 1e-12 | pass |

### `table.add_running_column`

**Seatbelts: drivers killed in Great Britain so far each year, month by month** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | pandas sort_values (stable), groupby().cumsum() | 144099 | 144099 | exact | pass |
| December 1969 | pandas sort_values (stable), groupby().cumsum() | 1402 | 1402 | exact | pass |
| December 1984 | pandas sort_values (stable), groupby().cumsum() | 1228 | 1228 | exact | pass |
| January 1970 | pandas sort_values (stable), groupby().cumsum() | 125 | 125 | exact | pass |
| total | R | 144099 | 144099 | exact | pass |
| December 1969 | R | 1402 | 1402 | exact | pass |
| December 1984 | R | 1228 | 1228 | exact | pass |
| January 1970 | R | 125 | 125 | exact | pass |

**Seatbelts: drivers killed in Great Britain so far each year, month by month (a Polars table)** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| total | Polars cum_sum().over(order_by=) | 144099 | 144099 | exact | pass |
| December 1969 | Polars cum_sum().over(order_by=) | 1402 | 1402 | exact | pass |
| December 1984 | Polars cum_sum().over(order_by=) | 1228 | 1228 | exact | pass |
| January 1970 | Polars cum_sum().over(order_by=) | 125 | 125 | exact | pass |

### `table.add_zeros_in_front_of`

**Seatbelts: the month of the year written with two digits (01 to 12)** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells reading 01 | pandas astype(str).str.zfill(2) | 16 | 16 | exact | pass |
| cells reading 09 | pandas astype(str).str.zfill(2) | 16 | 16 | exact | pass |
| cells reading 10 | pandas astype(str).str.zfill(2) | 16 | 16 | exact | pass |
| cells reading 12 | pandas astype(str).str.zfill(2) | 16 | 16 | exact | pass |
| cells two long | pandas astype(str).str.zfill(2) | 192 | 192 | exact | pass |
| cells reading 01 | R | 16 | 16 | exact | pass |
| cells reading 09 | R | 16 | 16 | exact | pass |
| cells reading 10 | R | 16 | 16 | exact | pass |
| cells reading 12 | R | 16 | 16 | exact | pass |
| cells two long | R | 192 | 192 | exact | pass |

**Seatbelts: the month of the year written with two digits (01 to 12) (a Polars table)** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells reading 01 | Polars cast(pl.String).str.zfill(2) | 16 | 16 | exact | pass |
| cells reading 09 | Polars cast(pl.String).str.zfill(2) | 16 | 16 | exact | pass |
| cells reading 10 | Polars cast(pl.String).str.zfill(2) | 16 | 16 | exact | pass |
| cells reading 12 | Polars cast(pl.String).str.zfill(2) | 16 | 16 | exact | pass |
| cells two long | Polars cast(pl.String).str.zfill(2) | 192 | 192 | exact | pass |

### `table.change_column in_rows_where=`

**warpbreaks: the tension written as "high breakage" in the rows with 40 breaks or more** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| high breakage | pandas loc[condition, column] = value | 9 | 9 | exact | pass |
| L | pandas loc[condition, column] = value | 11 | 11 | exact | pass |
| M | pandas loc[condition, column] = value | 17 | 17 | exact | pass |
| H | pandas loc[condition, column] = value | 17 | 17 | exact | pass |
| high breakage | R | 9 | 9 | exact | pass |
| L | R | 11 | 11 | exact | pass |
| M | R | 17 | 17 | exact | pass |
| H | R | 17 | 17 | exact | pass |

**warpbreaks: the tension written as "high breakage" in the rows with 40 breaks or more (a Polars table)** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| high breakage | Polars when().then().otherwise() | 9 | 9 | exact | pass |
| L | Polars when().then().otherwise() | 11 | 11 | exact | pass |
| M | Polars when().then().otherwise() | 17 | 17 | exact | pass |
| H | Polars when().then().otherwise() | 17 | 17 | exact | pass |

### `table.change_time_zone_in`

**AirPassengers: midnight at the start of each month on the Oslo clock, 1949-1960, on the UTC clock (Norway kept summer time in 1959 and 1960; the IANA time zone database)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| months at 22:00 UTC (summer time) | pandas dt.tz_localize("Europe/Oslo").dt.tz_convert("UTC") | 12 | 12 | exact | pass |
| months at 23:00 UTC | pandas dt.tz_localize("Europe/Oslo").dt.tz_convert("UTC") | 132 | 132 | exact | pass |
| sum of row x hour | pandas dt.tz_localize("Europe/Oslo").dt.tz_convert("UTC") | 238530 | 238530 | exact | pass |
| months at 22:00 UTC (summer time) | R | 12 | 12 | exact | pass |
| months at 23:00 UTC | R | 132 | 132 | exact | pass |
| sum of row x hour | R | 238530 | 238530 | exact | pass |

**AirPassengers: midnight at the start of each month on the Oslo clock, 1949-1960, on the UTC clock (Norway kept summer time in 1959 and 1960; the IANA time zone database) (a Polars table)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| months at 22:00 UTC (summer time) | Polars dt.replace_time_zone().dt.convert_time_zone("UTC") | 6 | 6 | exact | pass |
| months at 23:00 UTC | Polars dt.replace_time_zone().dt.convert_time_zone("UTC") | 138 | 138 | exact | pass |
| sum of row x hour | Polars dt.replace_time_zone().dt.convert_time_zone("UTC") | 240075 | 240075 | exact | pass |

**AirPassengers: midnight at the start of each month on the New York clock, 1949-1960, on the UTC clock (US summer time; the IANA time zone database)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| months at 04:00 UTC (summer time) | pandas dt.tz_localize("America/New_York").dt.tz_convert("UTC") | 66 | 66 | exact | pass |
| months at 05:00 UTC | pandas dt.tz_localize("America/New_York").dt.tz_convert("UTC") | 78 | 78 | exact | pass |
| sum of row x hour | pandas dt.tz_localize("America/New_York").dt.tz_convert("UTC") | 47148 | 47148 | exact | pass |
| months at 04:00 UTC (summer time) | R | 66 | 66 | exact | pass |
| months at 05:00 UTC | R | 78 | 78 | exact | pass |
| sum of row x hour | R | 47148 | 47148 | exact | pass |

**AirPassengers: midnight at the start of each month on the New York clock, 1949-1960, on the UTC clock (US summer time; the IANA time zone database) (a Polars table)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| months at 04:00 UTC (summer time) | Polars dt.replace_time_zone("America/New_York").dt.convert_time_zone("UTC") | 66 | 66 | exact | pass |
| months at 05:00 UTC | Polars dt.replace_time_zone("America/New_York").dt.convert_time_zone("UTC") | 78 | 78 | exact | pass |
| sum of row x hour | Polars dt.replace_time_zone("America/New_York").dt.convert_time_zone("UTC") | 47148 | 47148 | exact | pass |

**AirPassengers: a column that already carries the America/New_York zone (midnight at the start of each month, 1949-1960), its day of the month, then the same moments on the UTC clock** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first of the month in New York | pandas dt.day and dt.tz_convert("UTC") | 144 | 144 | exact | pass |
| months at 04:00 UTC (summer time) | pandas dt.day and dt.tz_convert("UTC") | 66 | 66 | exact | pass |
| months at 05:00 UTC | pandas dt.day and dt.tz_convert("UTC") | 78 | 78 | exact | pass |
| sum of row x hour | pandas dt.day and dt.tz_convert("UTC") | 47148 | 47148 | exact | pass |
| first of the month in New York | R | 144 | 144 | exact | pass |
| months at 04:00 UTC (summer time) | R | 66 | 66 | exact | pass |
| months at 05:00 UTC | R | 78 | 78 | exact | pass |
| sum of row x hour | R | 47148 | 47148 | exact | pass |

**AirPassengers: a column that already carries the America/New_York zone (midnight at the start of each month, 1949-1960), its day of the month, then the same moments on the UTC clock (a Polars table)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first of the month in New York | Polars dt.day() and dt.convert_time_zone("UTC") | 144 | 144 | exact | pass |
| months at 04:00 UTC (summer time) | Polars dt.day() and dt.convert_time_zone("UTC") | 66 | 66 | exact | pass |
| months at 05:00 UTC | Polars dt.day() and dt.convert_time_zone("UTC") | 78 | 78 | exact | pass |
| sum of row x hour | Polars dt.day() and dt.convert_time_zone("UTC") | 47148 | 47148 | exact | pass |

### `table.round_dates_in`

**AirPassengers: the first day of each month taken back to the Monday of its week** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| still the first of the month | pandas: the date minus its dt.dayofweek in days | 19 | 19 | exact | pass |
| all Mondays | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 1: 1948-12-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 2: 1949-01-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 3: 1949-02-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 4: 1949-03-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 5: 1949-04-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 6: 1949-05-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 7: 1949-06-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 8: 1949-08-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 9: 1949-08-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 10: 1949-09-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 11: 1949-10-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 12: 1949-11-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 13: 1949-12-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 14: 1950-01-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 15: 1950-02-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 16: 1950-03-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 17: 1950-05-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 18: 1950-05-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 19: 1950-06-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 20: 1950-07-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 21: 1950-08-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 22: 1950-09-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 23: 1950-10-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 24: 1950-11-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 25: 1951-01-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 26: 1951-01-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 27: 1951-02-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 28: 1951-03-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 29: 1951-04-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 30: 1951-05-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 31: 1951-06-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 32: 1951-07-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 33: 1951-08-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 34: 1951-10-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 35: 1951-10-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 36: 1951-11-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 37: 1951-12-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 38: 1952-01-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 39: 1952-02-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 40: 1952-03-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 41: 1952-04-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 42: 1952-05-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 43: 1952-06-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 44: 1952-07-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 45: 1952-09-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 46: 1952-09-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 47: 1952-10-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 48: 1952-12-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 49: 1952-12-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 50: 1953-01-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 51: 1953-02-23 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 52: 1953-03-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 53: 1953-04-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 54: 1953-06-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 55: 1953-06-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 56: 1953-07-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 57: 1953-08-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 58: 1953-09-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 59: 1953-10-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 60: 1953-11-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 61: 1953-12-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 62: 1954-02-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 63: 1954-03-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 64: 1954-03-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 65: 1954-04-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 66: 1954-05-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 67: 1954-06-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 68: 1954-07-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 69: 1954-08-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 70: 1954-09-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 71: 1954-11-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 72: 1954-11-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 73: 1954-12-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 74: 1955-01-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 75: 1955-02-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 76: 1955-03-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 77: 1955-04-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 78: 1955-05-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 79: 1955-06-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 80: 1955-08-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 81: 1955-08-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 82: 1955-09-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 83: 1955-10-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 84: 1955-11-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 85: 1955-12-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 86: 1956-01-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 87: 1956-02-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 88: 1956-03-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 89: 1956-04-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 90: 1956-05-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 91: 1956-06-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 92: 1956-07-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 93: 1956-08-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 94: 1956-10-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 95: 1956-10-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 96: 1956-11-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 97: 1956-12-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 98: 1957-01-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 99: 1957-02-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 100: 1957-04-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 101: 1957-04-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 102: 1957-05-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 103: 1957-07-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 104: 1957-07-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 105: 1957-08-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 106: 1957-09-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 107: 1957-10-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 108: 1957-11-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 109: 1957-12-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 110: 1958-01-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 111: 1958-02-24 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 112: 1958-03-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 113: 1958-04-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 114: 1958-05-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 115: 1958-06-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 116: 1958-07-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 117: 1958-09-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 118: 1958-09-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 119: 1958-10-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 120: 1958-12-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 121: 1958-12-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 122: 1959-01-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 123: 1959-02-23 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 124: 1959-03-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 125: 1959-04-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 126: 1959-06-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 127: 1959-06-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 128: 1959-07-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 129: 1959-08-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 130: 1959-09-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 131: 1959-10-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 132: 1959-11-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 133: 1959-12-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 134: 1960-02-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 135: 1960-02-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 136: 1960-03-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 137: 1960-04-25 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 138: 1960-05-30 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 139: 1960-06-27 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 140: 1960-08-01 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 141: 1960-08-29 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 142: 1960-09-26 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 143: 1960-10-31 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| row 144: 1960-11-28 | pandas: the date minus its dt.dayofweek in days | 1 | 1 | exact | pass |
| still the first of the month | R | 19 | 19 | exact | pass |
| row 1: 1948-12-27 | R | 1 | 1 | exact | pass |
| row 2: 1949-01-31 | R | 1 | 1 | exact | pass |
| row 3: 1949-02-28 | R | 1 | 1 | exact | pass |
| row 4: 1949-03-28 | R | 1 | 1 | exact | pass |
| row 5: 1949-04-25 | R | 1 | 1 | exact | pass |
| row 6: 1949-05-30 | R | 1 | 1 | exact | pass |
| row 7: 1949-06-27 | R | 1 | 1 | exact | pass |
| row 8: 1949-08-01 | R | 1 | 1 | exact | pass |
| row 9: 1949-08-29 | R | 1 | 1 | exact | pass |
| row 10: 1949-09-26 | R | 1 | 1 | exact | pass |
| row 11: 1949-10-31 | R | 1 | 1 | exact | pass |
| row 12: 1949-11-28 | R | 1 | 1 | exact | pass |
| row 13: 1949-12-26 | R | 1 | 1 | exact | pass |
| row 14: 1950-01-30 | R | 1 | 1 | exact | pass |
| row 15: 1950-02-27 | R | 1 | 1 | exact | pass |
| row 16: 1950-03-27 | R | 1 | 1 | exact | pass |
| row 17: 1950-05-01 | R | 1 | 1 | exact | pass |
| row 18: 1950-05-29 | R | 1 | 1 | exact | pass |
| row 19: 1950-06-26 | R | 1 | 1 | exact | pass |
| row 20: 1950-07-31 | R | 1 | 1 | exact | pass |
| row 21: 1950-08-28 | R | 1 | 1 | exact | pass |
| row 22: 1950-09-25 | R | 1 | 1 | exact | pass |
| row 23: 1950-10-30 | R | 1 | 1 | exact | pass |
| row 24: 1950-11-27 | R | 1 | 1 | exact | pass |
| row 25: 1951-01-01 | R | 1 | 1 | exact | pass |
| row 26: 1951-01-29 | R | 1 | 1 | exact | pass |
| row 27: 1951-02-26 | R | 1 | 1 | exact | pass |
| row 28: 1951-03-26 | R | 1 | 1 | exact | pass |
| row 29: 1951-04-30 | R | 1 | 1 | exact | pass |
| row 30: 1951-05-28 | R | 1 | 1 | exact | pass |
| row 31: 1951-06-25 | R | 1 | 1 | exact | pass |
| row 32: 1951-07-30 | R | 1 | 1 | exact | pass |
| row 33: 1951-08-27 | R | 1 | 1 | exact | pass |
| row 34: 1951-10-01 | R | 1 | 1 | exact | pass |
| row 35: 1951-10-29 | R | 1 | 1 | exact | pass |
| row 36: 1951-11-26 | R | 1 | 1 | exact | pass |
| row 37: 1951-12-31 | R | 1 | 1 | exact | pass |
| row 38: 1952-01-28 | R | 1 | 1 | exact | pass |
| row 39: 1952-02-25 | R | 1 | 1 | exact | pass |
| row 40: 1952-03-31 | R | 1 | 1 | exact | pass |
| row 41: 1952-04-28 | R | 1 | 1 | exact | pass |
| row 42: 1952-05-26 | R | 1 | 1 | exact | pass |
| row 43: 1952-06-30 | R | 1 | 1 | exact | pass |
| row 44: 1952-07-28 | R | 1 | 1 | exact | pass |
| row 45: 1952-09-01 | R | 1 | 1 | exact | pass |
| row 46: 1952-09-29 | R | 1 | 1 | exact | pass |
| row 47: 1952-10-27 | R | 1 | 1 | exact | pass |
| row 48: 1952-12-01 | R | 1 | 1 | exact | pass |
| row 49: 1952-12-29 | R | 1 | 1 | exact | pass |
| row 50: 1953-01-26 | R | 1 | 1 | exact | pass |
| row 51: 1953-02-23 | R | 1 | 1 | exact | pass |
| row 52: 1953-03-30 | R | 1 | 1 | exact | pass |
| row 53: 1953-04-27 | R | 1 | 1 | exact | pass |
| row 54: 1953-06-01 | R | 1 | 1 | exact | pass |
| row 55: 1953-06-29 | R | 1 | 1 | exact | pass |
| row 56: 1953-07-27 | R | 1 | 1 | exact | pass |
| row 57: 1953-08-31 | R | 1 | 1 | exact | pass |
| row 58: 1953-09-28 | R | 1 | 1 | exact | pass |
| row 59: 1953-10-26 | R | 1 | 1 | exact | pass |
| row 60: 1953-11-30 | R | 1 | 1 | exact | pass |
| row 61: 1953-12-28 | R | 1 | 1 | exact | pass |
| row 62: 1954-02-01 | R | 1 | 1 | exact | pass |
| row 63: 1954-03-01 | R | 1 | 1 | exact | pass |
| row 64: 1954-03-29 | R | 1 | 1 | exact | pass |
| row 65: 1954-04-26 | R | 1 | 1 | exact | pass |
| row 66: 1954-05-31 | R | 1 | 1 | exact | pass |
| row 67: 1954-06-28 | R | 1 | 1 | exact | pass |
| row 68: 1954-07-26 | R | 1 | 1 | exact | pass |
| row 69: 1954-08-30 | R | 1 | 1 | exact | pass |
| row 70: 1954-09-27 | R | 1 | 1 | exact | pass |
| row 71: 1954-11-01 | R | 1 | 1 | exact | pass |
| row 72: 1954-11-29 | R | 1 | 1 | exact | pass |
| row 73: 1954-12-27 | R | 1 | 1 | exact | pass |
| row 74: 1955-01-31 | R | 1 | 1 | exact | pass |
| row 75: 1955-02-28 | R | 1 | 1 | exact | pass |
| row 76: 1955-03-28 | R | 1 | 1 | exact | pass |
| row 77: 1955-04-25 | R | 1 | 1 | exact | pass |
| row 78: 1955-05-30 | R | 1 | 1 | exact | pass |
| row 79: 1955-06-27 | R | 1 | 1 | exact | pass |
| row 80: 1955-08-01 | R | 1 | 1 | exact | pass |
| row 81: 1955-08-29 | R | 1 | 1 | exact | pass |
| row 82: 1955-09-26 | R | 1 | 1 | exact | pass |
| row 83: 1955-10-31 | R | 1 | 1 | exact | pass |
| row 84: 1955-11-28 | R | 1 | 1 | exact | pass |
| row 85: 1955-12-26 | R | 1 | 1 | exact | pass |
| row 86: 1956-01-30 | R | 1 | 1 | exact | pass |
| row 87: 1956-02-27 | R | 1 | 1 | exact | pass |
| row 88: 1956-03-26 | R | 1 | 1 | exact | pass |
| row 89: 1956-04-30 | R | 1 | 1 | exact | pass |
| row 90: 1956-05-28 | R | 1 | 1 | exact | pass |
| row 91: 1956-06-25 | R | 1 | 1 | exact | pass |
| row 92: 1956-07-30 | R | 1 | 1 | exact | pass |
| row 93: 1956-08-27 | R | 1 | 1 | exact | pass |
| row 94: 1956-10-01 | R | 1 | 1 | exact | pass |
| row 95: 1956-10-29 | R | 1 | 1 | exact | pass |
| row 96: 1956-11-26 | R | 1 | 1 | exact | pass |
| row 97: 1956-12-31 | R | 1 | 1 | exact | pass |
| row 98: 1957-01-28 | R | 1 | 1 | exact | pass |
| row 99: 1957-02-25 | R | 1 | 1 | exact | pass |
| row 100: 1957-04-01 | R | 1 | 1 | exact | pass |
| row 101: 1957-04-29 | R | 1 | 1 | exact | pass |
| row 102: 1957-05-27 | R | 1 | 1 | exact | pass |
| row 103: 1957-07-01 | R | 1 | 1 | exact | pass |
| row 104: 1957-07-29 | R | 1 | 1 | exact | pass |
| row 105: 1957-08-26 | R | 1 | 1 | exact | pass |
| row 106: 1957-09-30 | R | 1 | 1 | exact | pass |
| row 107: 1957-10-28 | R | 1 | 1 | exact | pass |
| row 108: 1957-11-25 | R | 1 | 1 | exact | pass |
| row 109: 1957-12-30 | R | 1 | 1 | exact | pass |
| row 110: 1958-01-27 | R | 1 | 1 | exact | pass |
| row 111: 1958-02-24 | R | 1 | 1 | exact | pass |
| row 112: 1958-03-31 | R | 1 | 1 | exact | pass |
| row 113: 1958-04-28 | R | 1 | 1 | exact | pass |
| row 114: 1958-05-26 | R | 1 | 1 | exact | pass |
| row 115: 1958-06-30 | R | 1 | 1 | exact | pass |
| row 116: 1958-07-28 | R | 1 | 1 | exact | pass |
| row 117: 1958-09-01 | R | 1 | 1 | exact | pass |
| row 118: 1958-09-29 | R | 1 | 1 | exact | pass |
| row 119: 1958-10-27 | R | 1 | 1 | exact | pass |
| row 120: 1958-12-01 | R | 1 | 1 | exact | pass |
| row 121: 1958-12-29 | R | 1 | 1 | exact | pass |
| row 122: 1959-01-26 | R | 1 | 1 | exact | pass |
| row 123: 1959-02-23 | R | 1 | 1 | exact | pass |
| row 124: 1959-03-30 | R | 1 | 1 | exact | pass |
| row 125: 1959-04-27 | R | 1 | 1 | exact | pass |
| row 126: 1959-06-01 | R | 1 | 1 | exact | pass |
| row 127: 1959-06-29 | R | 1 | 1 | exact | pass |
| row 128: 1959-07-27 | R | 1 | 1 | exact | pass |
| row 129: 1959-08-31 | R | 1 | 1 | exact | pass |
| row 130: 1959-09-28 | R | 1 | 1 | exact | pass |
| row 131: 1959-10-26 | R | 1 | 1 | exact | pass |
| row 132: 1959-11-30 | R | 1 | 1 | exact | pass |
| row 133: 1959-12-28 | R | 1 | 1 | exact | pass |
| row 134: 1960-02-01 | R | 1 | 1 | exact | pass |
| row 135: 1960-02-29 | R | 1 | 1 | exact | pass |
| row 136: 1960-03-28 | R | 1 | 1 | exact | pass |
| row 137: 1960-04-25 | R | 1 | 1 | exact | pass |
| row 138: 1960-05-30 | R | 1 | 1 | exact | pass |
| row 139: 1960-06-27 | R | 1 | 1 | exact | pass |
| row 140: 1960-08-01 | R | 1 | 1 | exact | pass |
| row 141: 1960-08-29 | R | 1 | 1 | exact | pass |
| row 142: 1960-09-26 | R | 1 | 1 | exact | pass |
| row 143: 1960-10-31 | R | 1 | 1 | exact | pass |
| row 144: 1960-11-28 | R | 1 | 1 | exact | pass |

**AirPassengers: the first day of each month taken back to the Monday of its week (a Polars table)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| still the first of the month | Polars dt.truncate("1w") | 19 | 19 | exact | pass |
| all Mondays | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 1: 1948-12-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 2: 1949-01-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 3: 1949-02-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 4: 1949-03-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 5: 1949-04-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 6: 1949-05-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 7: 1949-06-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 8: 1949-08-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 9: 1949-08-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 10: 1949-09-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 11: 1949-10-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 12: 1949-11-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 13: 1949-12-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 14: 1950-01-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 15: 1950-02-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 16: 1950-03-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 17: 1950-05-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 18: 1950-05-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 19: 1950-06-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 20: 1950-07-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 21: 1950-08-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 22: 1950-09-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 23: 1950-10-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 24: 1950-11-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 25: 1951-01-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 26: 1951-01-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 27: 1951-02-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 28: 1951-03-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 29: 1951-04-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 30: 1951-05-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 31: 1951-06-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 32: 1951-07-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 33: 1951-08-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 34: 1951-10-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 35: 1951-10-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 36: 1951-11-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 37: 1951-12-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 38: 1952-01-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 39: 1952-02-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 40: 1952-03-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 41: 1952-04-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 42: 1952-05-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 43: 1952-06-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 44: 1952-07-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 45: 1952-09-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 46: 1952-09-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 47: 1952-10-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 48: 1952-12-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 49: 1952-12-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 50: 1953-01-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 51: 1953-02-23 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 52: 1953-03-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 53: 1953-04-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 54: 1953-06-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 55: 1953-06-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 56: 1953-07-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 57: 1953-08-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 58: 1953-09-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 59: 1953-10-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 60: 1953-11-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 61: 1953-12-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 62: 1954-02-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 63: 1954-03-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 64: 1954-03-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 65: 1954-04-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 66: 1954-05-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 67: 1954-06-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 68: 1954-07-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 69: 1954-08-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 70: 1954-09-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 71: 1954-11-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 72: 1954-11-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 73: 1954-12-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 74: 1955-01-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 75: 1955-02-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 76: 1955-03-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 77: 1955-04-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 78: 1955-05-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 79: 1955-06-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 80: 1955-08-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 81: 1955-08-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 82: 1955-09-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 83: 1955-10-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 84: 1955-11-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 85: 1955-12-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 86: 1956-01-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 87: 1956-02-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 88: 1956-03-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 89: 1956-04-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 90: 1956-05-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 91: 1956-06-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 92: 1956-07-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 93: 1956-08-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 94: 1956-10-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 95: 1956-10-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 96: 1956-11-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 97: 1956-12-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 98: 1957-01-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 99: 1957-02-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 100: 1957-04-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 101: 1957-04-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 102: 1957-05-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 103: 1957-07-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 104: 1957-07-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 105: 1957-08-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 106: 1957-09-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 107: 1957-10-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 108: 1957-11-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 109: 1957-12-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 110: 1958-01-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 111: 1958-02-24 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 112: 1958-03-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 113: 1958-04-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 114: 1958-05-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 115: 1958-06-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 116: 1958-07-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 117: 1958-09-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 118: 1958-09-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 119: 1958-10-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 120: 1958-12-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 121: 1958-12-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 122: 1959-01-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 123: 1959-02-23 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 124: 1959-03-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 125: 1959-04-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 126: 1959-06-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 127: 1959-06-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 128: 1959-07-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 129: 1959-08-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 130: 1959-09-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 131: 1959-10-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 132: 1959-11-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 133: 1959-12-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 134: 1960-02-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 135: 1960-02-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 136: 1960-03-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 137: 1960-04-25 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 138: 1960-05-30 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 139: 1960-06-27 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 140: 1960-08-01 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 141: 1960-08-29 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 142: 1960-09-26 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 143: 1960-10-31 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |
| row 144: 1960-11-28 | Polars dt.truncate("1w") | 1 | 1 | exact | pass |

### `table.round_dates_in to_the=`

**ICU arrivals: 254 arrival times rounded to the nearest hour (59 are exactly half past, which go up)** (real data; data: ICU arrivals (circular))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sum of hours | pandas (time + 30 minutes).dt.floor("h") (half way up) | 3542 | 3542 | exact | pass |
| next day | pandas (time + 30 minutes).dt.floor("h") (half way up) | 4 | 4 | exact | pass |
| sum of row x hour | pandas (time + 30 minutes).dt.floor("h") (half way up) | 443501 | 443501 | exact | pass |
| on the hour | pandas (time + 30 minutes).dt.floor("h") (half way up) | 1 | 1 | exact | pass |
| sum of hours | R | 3542 | 3542 | exact | pass |
| next day | R | 4 | 4 | exact | pass |
| sum of row x hour | R | 443501 | 443501 | exact | pass |
| on the hour | R | 1 | 1 | exact | pass |

Note: R round.POSIXt(x, "hours") also sends a time exactly half way up.

**ICU arrivals: 254 arrival times rounded to the nearest hour (59 are exactly half past, which go up) (a Polars table)** (real data; data: ICU arrivals (circular))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| sum of hours | Polars dt.round("1h") | 3542 | 3542 | exact | pass |
| next day | Polars dt.round("1h") | 4 | 4 | exact | pass |
| sum of row x hour | Polars dt.round("1h") | 443501 | 443501 | exact | pass |
| on the hour | Polars dt.round("1h") | 1 | 1 | exact | pass |

### `table.turn_into_text written_like=`

**AirPassengers: the 144 months written as day.month.year** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells | pandas dt.strftime("%d.%m.%Y") | 144 | 144 | exact | pass |
| row 1: 01.01.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 2: 01.02.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 3: 01.03.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 4: 01.04.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 5: 01.05.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 6: 01.06.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 7: 01.07.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 8: 01.08.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 9: 01.09.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 10: 01.10.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 11: 01.11.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 12: 01.12.1949 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 13: 01.01.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 14: 01.02.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 15: 01.03.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 16: 01.04.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 17: 01.05.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 18: 01.06.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 19: 01.07.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 20: 01.08.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 21: 01.09.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 22: 01.10.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 23: 01.11.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 24: 01.12.1950 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 25: 01.01.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 26: 01.02.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 27: 01.03.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 28: 01.04.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 29: 01.05.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 30: 01.06.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 31: 01.07.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 32: 01.08.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 33: 01.09.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 34: 01.10.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 35: 01.11.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 36: 01.12.1951 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 37: 01.01.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 38: 01.02.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 39: 01.03.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 40: 01.04.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 41: 01.05.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 42: 01.06.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 43: 01.07.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 44: 01.08.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 45: 01.09.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 46: 01.10.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 47: 01.11.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 48: 01.12.1952 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 49: 01.01.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 50: 01.02.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 51: 01.03.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 52: 01.04.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 53: 01.05.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 54: 01.06.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 55: 01.07.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 56: 01.08.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 57: 01.09.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 58: 01.10.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 59: 01.11.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 60: 01.12.1953 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 61: 01.01.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 62: 01.02.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 63: 01.03.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 64: 01.04.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 65: 01.05.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 66: 01.06.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 67: 01.07.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 68: 01.08.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 69: 01.09.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 70: 01.10.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 71: 01.11.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 72: 01.12.1954 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 73: 01.01.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 74: 01.02.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 75: 01.03.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 76: 01.04.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 77: 01.05.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 78: 01.06.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 79: 01.07.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 80: 01.08.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 81: 01.09.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 82: 01.10.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 83: 01.11.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 84: 01.12.1955 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 85: 01.01.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 86: 01.02.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 87: 01.03.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 88: 01.04.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 89: 01.05.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 90: 01.06.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 91: 01.07.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 92: 01.08.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 93: 01.09.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 94: 01.10.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 95: 01.11.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 96: 01.12.1956 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 97: 01.01.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 98: 01.02.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 99: 01.03.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 100: 01.04.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 101: 01.05.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 102: 01.06.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 103: 01.07.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 104: 01.08.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 105: 01.09.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 106: 01.10.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 107: 01.11.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 108: 01.12.1957 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 109: 01.01.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 110: 01.02.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 111: 01.03.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 112: 01.04.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 113: 01.05.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 114: 01.06.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 115: 01.07.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 116: 01.08.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 117: 01.09.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 118: 01.10.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 119: 01.11.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 120: 01.12.1958 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 121: 01.01.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 122: 01.02.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 123: 01.03.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 124: 01.04.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 125: 01.05.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 126: 01.06.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 127: 01.07.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 128: 01.08.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 129: 01.09.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 130: 01.10.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 131: 01.11.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 132: 01.12.1959 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 133: 01.01.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 134: 01.02.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 135: 01.03.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 136: 01.04.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 137: 01.05.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 138: 01.06.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 139: 01.07.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 140: 01.08.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 141: 01.09.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 142: 01.10.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 143: 01.11.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 144: 01.12.1960 | pandas dt.strftime("%d.%m.%Y") | 1 | 1 | exact | pass |
| cells | R | 144 | 144 | exact | pass |
| row 1: 01.01.1949 | R | 1 | 1 | exact | pass |
| row 2: 01.02.1949 | R | 1 | 1 | exact | pass |
| row 3: 01.03.1949 | R | 1 | 1 | exact | pass |
| row 4: 01.04.1949 | R | 1 | 1 | exact | pass |
| row 5: 01.05.1949 | R | 1 | 1 | exact | pass |
| row 6: 01.06.1949 | R | 1 | 1 | exact | pass |
| row 7: 01.07.1949 | R | 1 | 1 | exact | pass |
| row 8: 01.08.1949 | R | 1 | 1 | exact | pass |
| row 9: 01.09.1949 | R | 1 | 1 | exact | pass |
| row 10: 01.10.1949 | R | 1 | 1 | exact | pass |
| row 11: 01.11.1949 | R | 1 | 1 | exact | pass |
| row 12: 01.12.1949 | R | 1 | 1 | exact | pass |
| row 13: 01.01.1950 | R | 1 | 1 | exact | pass |
| row 14: 01.02.1950 | R | 1 | 1 | exact | pass |
| row 15: 01.03.1950 | R | 1 | 1 | exact | pass |
| row 16: 01.04.1950 | R | 1 | 1 | exact | pass |
| row 17: 01.05.1950 | R | 1 | 1 | exact | pass |
| row 18: 01.06.1950 | R | 1 | 1 | exact | pass |
| row 19: 01.07.1950 | R | 1 | 1 | exact | pass |
| row 20: 01.08.1950 | R | 1 | 1 | exact | pass |
| row 21: 01.09.1950 | R | 1 | 1 | exact | pass |
| row 22: 01.10.1950 | R | 1 | 1 | exact | pass |
| row 23: 01.11.1950 | R | 1 | 1 | exact | pass |
| row 24: 01.12.1950 | R | 1 | 1 | exact | pass |
| row 25: 01.01.1951 | R | 1 | 1 | exact | pass |
| row 26: 01.02.1951 | R | 1 | 1 | exact | pass |
| row 27: 01.03.1951 | R | 1 | 1 | exact | pass |
| row 28: 01.04.1951 | R | 1 | 1 | exact | pass |
| row 29: 01.05.1951 | R | 1 | 1 | exact | pass |
| row 30: 01.06.1951 | R | 1 | 1 | exact | pass |
| row 31: 01.07.1951 | R | 1 | 1 | exact | pass |
| row 32: 01.08.1951 | R | 1 | 1 | exact | pass |
| row 33: 01.09.1951 | R | 1 | 1 | exact | pass |
| row 34: 01.10.1951 | R | 1 | 1 | exact | pass |
| row 35: 01.11.1951 | R | 1 | 1 | exact | pass |
| row 36: 01.12.1951 | R | 1 | 1 | exact | pass |
| row 37: 01.01.1952 | R | 1 | 1 | exact | pass |
| row 38: 01.02.1952 | R | 1 | 1 | exact | pass |
| row 39: 01.03.1952 | R | 1 | 1 | exact | pass |
| row 40: 01.04.1952 | R | 1 | 1 | exact | pass |
| row 41: 01.05.1952 | R | 1 | 1 | exact | pass |
| row 42: 01.06.1952 | R | 1 | 1 | exact | pass |
| row 43: 01.07.1952 | R | 1 | 1 | exact | pass |
| row 44: 01.08.1952 | R | 1 | 1 | exact | pass |
| row 45: 01.09.1952 | R | 1 | 1 | exact | pass |
| row 46: 01.10.1952 | R | 1 | 1 | exact | pass |
| row 47: 01.11.1952 | R | 1 | 1 | exact | pass |
| row 48: 01.12.1952 | R | 1 | 1 | exact | pass |
| row 49: 01.01.1953 | R | 1 | 1 | exact | pass |
| row 50: 01.02.1953 | R | 1 | 1 | exact | pass |
| row 51: 01.03.1953 | R | 1 | 1 | exact | pass |
| row 52: 01.04.1953 | R | 1 | 1 | exact | pass |
| row 53: 01.05.1953 | R | 1 | 1 | exact | pass |
| row 54: 01.06.1953 | R | 1 | 1 | exact | pass |
| row 55: 01.07.1953 | R | 1 | 1 | exact | pass |
| row 56: 01.08.1953 | R | 1 | 1 | exact | pass |
| row 57: 01.09.1953 | R | 1 | 1 | exact | pass |
| row 58: 01.10.1953 | R | 1 | 1 | exact | pass |
| row 59: 01.11.1953 | R | 1 | 1 | exact | pass |
| row 60: 01.12.1953 | R | 1 | 1 | exact | pass |
| row 61: 01.01.1954 | R | 1 | 1 | exact | pass |
| row 62: 01.02.1954 | R | 1 | 1 | exact | pass |
| row 63: 01.03.1954 | R | 1 | 1 | exact | pass |
| row 64: 01.04.1954 | R | 1 | 1 | exact | pass |
| row 65: 01.05.1954 | R | 1 | 1 | exact | pass |
| row 66: 01.06.1954 | R | 1 | 1 | exact | pass |
| row 67: 01.07.1954 | R | 1 | 1 | exact | pass |
| row 68: 01.08.1954 | R | 1 | 1 | exact | pass |
| row 69: 01.09.1954 | R | 1 | 1 | exact | pass |
| row 70: 01.10.1954 | R | 1 | 1 | exact | pass |
| row 71: 01.11.1954 | R | 1 | 1 | exact | pass |
| row 72: 01.12.1954 | R | 1 | 1 | exact | pass |
| row 73: 01.01.1955 | R | 1 | 1 | exact | pass |
| row 74: 01.02.1955 | R | 1 | 1 | exact | pass |
| row 75: 01.03.1955 | R | 1 | 1 | exact | pass |
| row 76: 01.04.1955 | R | 1 | 1 | exact | pass |
| row 77: 01.05.1955 | R | 1 | 1 | exact | pass |
| row 78: 01.06.1955 | R | 1 | 1 | exact | pass |
| row 79: 01.07.1955 | R | 1 | 1 | exact | pass |
| row 80: 01.08.1955 | R | 1 | 1 | exact | pass |
| row 81: 01.09.1955 | R | 1 | 1 | exact | pass |
| row 82: 01.10.1955 | R | 1 | 1 | exact | pass |
| row 83: 01.11.1955 | R | 1 | 1 | exact | pass |
| row 84: 01.12.1955 | R | 1 | 1 | exact | pass |
| row 85: 01.01.1956 | R | 1 | 1 | exact | pass |
| row 86: 01.02.1956 | R | 1 | 1 | exact | pass |
| row 87: 01.03.1956 | R | 1 | 1 | exact | pass |
| row 88: 01.04.1956 | R | 1 | 1 | exact | pass |
| row 89: 01.05.1956 | R | 1 | 1 | exact | pass |
| row 90: 01.06.1956 | R | 1 | 1 | exact | pass |
| row 91: 01.07.1956 | R | 1 | 1 | exact | pass |
| row 92: 01.08.1956 | R | 1 | 1 | exact | pass |
| row 93: 01.09.1956 | R | 1 | 1 | exact | pass |
| row 94: 01.10.1956 | R | 1 | 1 | exact | pass |
| row 95: 01.11.1956 | R | 1 | 1 | exact | pass |
| row 96: 01.12.1956 | R | 1 | 1 | exact | pass |
| row 97: 01.01.1957 | R | 1 | 1 | exact | pass |
| row 98: 01.02.1957 | R | 1 | 1 | exact | pass |
| row 99: 01.03.1957 | R | 1 | 1 | exact | pass |
| row 100: 01.04.1957 | R | 1 | 1 | exact | pass |
| row 101: 01.05.1957 | R | 1 | 1 | exact | pass |
| row 102: 01.06.1957 | R | 1 | 1 | exact | pass |
| row 103: 01.07.1957 | R | 1 | 1 | exact | pass |
| row 104: 01.08.1957 | R | 1 | 1 | exact | pass |
| row 105: 01.09.1957 | R | 1 | 1 | exact | pass |
| row 106: 01.10.1957 | R | 1 | 1 | exact | pass |
| row 107: 01.11.1957 | R | 1 | 1 | exact | pass |
| row 108: 01.12.1957 | R | 1 | 1 | exact | pass |
| row 109: 01.01.1958 | R | 1 | 1 | exact | pass |
| row 110: 01.02.1958 | R | 1 | 1 | exact | pass |
| row 111: 01.03.1958 | R | 1 | 1 | exact | pass |
| row 112: 01.04.1958 | R | 1 | 1 | exact | pass |
| row 113: 01.05.1958 | R | 1 | 1 | exact | pass |
| row 114: 01.06.1958 | R | 1 | 1 | exact | pass |
| row 115: 01.07.1958 | R | 1 | 1 | exact | pass |
| row 116: 01.08.1958 | R | 1 | 1 | exact | pass |
| row 117: 01.09.1958 | R | 1 | 1 | exact | pass |
| row 118: 01.10.1958 | R | 1 | 1 | exact | pass |
| row 119: 01.11.1958 | R | 1 | 1 | exact | pass |
| row 120: 01.12.1958 | R | 1 | 1 | exact | pass |
| row 121: 01.01.1959 | R | 1 | 1 | exact | pass |
| row 122: 01.02.1959 | R | 1 | 1 | exact | pass |
| row 123: 01.03.1959 | R | 1 | 1 | exact | pass |
| row 124: 01.04.1959 | R | 1 | 1 | exact | pass |
| row 125: 01.05.1959 | R | 1 | 1 | exact | pass |
| row 126: 01.06.1959 | R | 1 | 1 | exact | pass |
| row 127: 01.07.1959 | R | 1 | 1 | exact | pass |
| row 128: 01.08.1959 | R | 1 | 1 | exact | pass |
| row 129: 01.09.1959 | R | 1 | 1 | exact | pass |
| row 130: 01.10.1959 | R | 1 | 1 | exact | pass |
| row 131: 01.11.1959 | R | 1 | 1 | exact | pass |
| row 132: 01.12.1959 | R | 1 | 1 | exact | pass |
| row 133: 01.01.1960 | R | 1 | 1 | exact | pass |
| row 134: 01.02.1960 | R | 1 | 1 | exact | pass |
| row 135: 01.03.1960 | R | 1 | 1 | exact | pass |
| row 136: 01.04.1960 | R | 1 | 1 | exact | pass |
| row 137: 01.05.1960 | R | 1 | 1 | exact | pass |
| row 138: 01.06.1960 | R | 1 | 1 | exact | pass |
| row 139: 01.07.1960 | R | 1 | 1 | exact | pass |
| row 140: 01.08.1960 | R | 1 | 1 | exact | pass |
| row 141: 01.09.1960 | R | 1 | 1 | exact | pass |
| row 142: 01.10.1960 | R | 1 | 1 | exact | pass |
| row 143: 01.11.1960 | R | 1 | 1 | exact | pass |
| row 144: 01.12.1960 | R | 1 | 1 | exact | pass |

**AirPassengers: the 144 months written as day.month.year (a Polars table)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells | Polars dt.to_string("%d.%m.%Y") | 144 | 144 | exact | pass |
| row 1: 01.01.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 2: 01.02.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 3: 01.03.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 4: 01.04.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 5: 01.05.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 6: 01.06.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 7: 01.07.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 8: 01.08.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 9: 01.09.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 10: 01.10.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 11: 01.11.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 12: 01.12.1949 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 13: 01.01.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 14: 01.02.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 15: 01.03.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 16: 01.04.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 17: 01.05.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 18: 01.06.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 19: 01.07.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 20: 01.08.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 21: 01.09.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 22: 01.10.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 23: 01.11.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 24: 01.12.1950 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 25: 01.01.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 26: 01.02.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 27: 01.03.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 28: 01.04.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 29: 01.05.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 30: 01.06.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 31: 01.07.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 32: 01.08.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 33: 01.09.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 34: 01.10.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 35: 01.11.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 36: 01.12.1951 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 37: 01.01.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 38: 01.02.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 39: 01.03.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 40: 01.04.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 41: 01.05.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 42: 01.06.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 43: 01.07.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 44: 01.08.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 45: 01.09.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 46: 01.10.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 47: 01.11.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 48: 01.12.1952 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 49: 01.01.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 50: 01.02.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 51: 01.03.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 52: 01.04.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 53: 01.05.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 54: 01.06.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 55: 01.07.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 56: 01.08.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 57: 01.09.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 58: 01.10.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 59: 01.11.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 60: 01.12.1953 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 61: 01.01.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 62: 01.02.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 63: 01.03.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 64: 01.04.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 65: 01.05.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 66: 01.06.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 67: 01.07.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 68: 01.08.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 69: 01.09.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 70: 01.10.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 71: 01.11.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 72: 01.12.1954 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 73: 01.01.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 74: 01.02.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 75: 01.03.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 76: 01.04.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 77: 01.05.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 78: 01.06.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 79: 01.07.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 80: 01.08.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 81: 01.09.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 82: 01.10.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 83: 01.11.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 84: 01.12.1955 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 85: 01.01.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 86: 01.02.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 87: 01.03.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 88: 01.04.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 89: 01.05.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 90: 01.06.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 91: 01.07.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 92: 01.08.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 93: 01.09.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 94: 01.10.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 95: 01.11.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 96: 01.12.1956 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 97: 01.01.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 98: 01.02.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 99: 01.03.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 100: 01.04.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 101: 01.05.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 102: 01.06.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 103: 01.07.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 104: 01.08.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 105: 01.09.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 106: 01.10.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 107: 01.11.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 108: 01.12.1957 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 109: 01.01.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 110: 01.02.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 111: 01.03.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 112: 01.04.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 113: 01.05.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 114: 01.06.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 115: 01.07.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 116: 01.08.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 117: 01.09.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 118: 01.10.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 119: 01.11.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 120: 01.12.1958 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 121: 01.01.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 122: 01.02.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 123: 01.03.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 124: 01.04.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 125: 01.05.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 126: 01.06.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 127: 01.07.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 128: 01.08.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 129: 01.09.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 130: 01.10.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 131: 01.11.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 132: 01.12.1959 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 133: 01.01.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 134: 01.02.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 135: 01.03.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 136: 01.04.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 137: 01.05.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 138: 01.06.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 139: 01.07.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 140: 01.08.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 141: 01.09.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 142: 01.10.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 143: 01.11.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |
| row 144: 01.12.1960 | Polars dt.to_string("%d.%m.%Y") | 1 | 1 | exact | pass |

### `table.turn_into_categories`

**warpbreaks: tension put in the order high, medium, low, then sorted by it** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first tension is H | pandas Categorical(ordered=True), sort_values (stable) | 1 | 1 | exact | pass |
| sum of row x breaks | pandas Categorical(ordered=True), sort_values (stable) | 46250 | 46250 | exact | pass |
| first tension is H | R | 1 | 1 | exact | pass |
| sum of row x breaks | R | 46250 | 46250 | exact | pass |

**warpbreaks: tension put in the order high, medium, low, then sorted by it (a Polars table)** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first tension is H | Polars pl.Enum, sort | 1 | 1 | exact | pass |
| sum of row x breaks | Polars pl.Enum, sort | 46250 | 46250 | exact | pass |

### `table.clean_column_names`

**Hackshaw's passive smoking studies: "odds ratio 95 % CI low" and the other names made plain** (real data; data: passive smoking (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas str.replace, str.normalize("NFKD"), str.lower on the column names | 4 | 4 | exact | pass |
| column 1: study | pandas str.replace, str.normalize("NFKD"), str.lower on the column names | 1 | 1 | exact | pass |
| column 2: odds_ratio | pandas str.replace, str.normalize("NFKD"), str.lower on the column names | 1 | 1 | exact | pass |
| column 3: odds_ratio_95_percent_ci_low | pandas str.replace, str.normalize("NFKD"), str.lower on the column names | 1 | 1 | exact | pass |
| column 4: odds_ratio_95_percent_ci_high | pandas str.replace, str.normalize("NFKD"), str.lower on the column names | 1 | 1 | exact | pass |
| columns | R | 4 | 4 | exact | pass |
| column 1: study | R | 1 | 1 | exact | pass |
| column 2: odds_ratio | R | 1 | 1 | exact | pass |
| column 3: odds_ratio_95_percent_ci_low | R | 1 | 1 | exact | pass |
| column 4: odds_ratio_95_percent_ci_high | R | 1 | 1 | exact | pass |

**Hackshaw's passive smoking studies: "odds ratio 95 % CI low" and the other names made plain (a Polars table)** (real data; data: passive smoking (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Polars rename (re.sub, unicodedata) | 4 | 4 | exact | pass |
| column 1: study | Polars rename (re.sub, unicodedata) | 1 | 1 | exact | pass |
| column 2: odds_ratio | Polars rename (re.sub, unicodedata) | 1 | 1 | exact | pass |
| column 3: odds_ratio_95_percent_ci_low | Polars rename (re.sub, unicodedata) | 1 | 1 | exact | pass |
| column 4: odds_ratio_95_percent_ci_high | Polars rename (re.sub, unicodedata) | 1 | 1 | exact | pass |

### `table.keep_first_rows for_each_group_in=`

**mtcars: the two cars with the best fuel use for each number of cylinders** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas sort_values (stable), groupby().head(2) | 6 | 6 | exact | pass |
| row 1: Toyota Corolla | pandas sort_values (stable), groupby().head(2) | 1 | 1 | exact | pass |
| row 2: Fiat 128 | pandas sort_values (stable), groupby().head(2) | 1 | 1 | exact | pass |
| row 3: Hornet 4 Drive | pandas sort_values (stable), groupby().head(2) | 1 | 1 | exact | pass |
| row 4: Mazda RX4 | pandas sort_values (stable), groupby().head(2) | 1 | 1 | exact | pass |
| row 5: Pontiac Firebird | pandas sort_values (stable), groupby().head(2) | 1 | 1 | exact | pass |
| row 6: Hornet Sportabout | pandas sort_values (stable), groupby().head(2) | 1 | 1 | exact | pass |
| rows | R | 6 | 6 | exact | pass |
| row 1: Toyota Corolla | R | 1 | 1 | exact | pass |
| row 2: Fiat 128 | R | 1 | 1 | exact | pass |
| row 3: Hornet 4 Drive | R | 1 | 1 | exact | pass |
| row 4: Mazda RX4 | R | 1 | 1 | exact | pass |
| row 5: Pontiac Firebird | R | 1 | 1 | exact | pass |
| row 6: Hornet Sportabout | R | 1 | 1 | exact | pass |

**mtcars: the two cars with the best fuel use for each number of cylinders (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars sort, filter(int_range(len()).over() < 2) | 6 | 6 | exact | pass |
| row 1: Toyota Corolla | Polars sort, filter(int_range(len()).over() < 2) | 1 | 1 | exact | pass |
| row 2: Fiat 128 | Polars sort, filter(int_range(len()).over() < 2) | 1 | 1 | exact | pass |
| row 3: Hornet 4 Drive | Polars sort, filter(int_range(len()).over() < 2) | 1 | 1 | exact | pass |
| row 4: Mazda RX4 | Polars sort, filter(int_range(len()).over() < 2) | 1 | 1 | exact | pass |
| row 5: Pontiac Firebird | Polars sort, filter(int_range(len()).over() < 2) | 1 | 1 | exact | pass |
| row 6: Hornet Sportabout | Polars sort, filter(int_range(len()).over() < 2) | 1 | 1 | exact | pass |

### `table.keep_groups_where`

**mtcars: only the numbers of cylinders whose cars average 19 mpg or more** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas groupby().filter() | 18 | 18 | relative 1e-12 | pass |
| total mpg | pandas groupby().filter() | 431.5 | 431.5 | relative 1e-12 | pass |
| rows | R | 18 | 18 | relative 1e-12 | pass |
| total mpg | R | 431.5 | 431.5 | relative 1e-12 | pass |

**mtcars: only the numbers of cylinders whose cars average 19 mpg or more (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars filter(mean().over() >= 19) | 18 | 18 | relative 1e-12 | pass |
| total mpg | Polars filter(mean().over() >= 19) | 431.5 | 431.5 | relative 1e-12 | pass |

### `table.remove_groups_where`

**mtcars: the numbers of cylinders whose cars average under 19 mpg removed** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas groupby().filter() | 18 | 18 | relative 1e-12 | pass |
| total mpg | pandas groupby().filter() | 431.5 | 431.5 | relative 1e-12 | pass |
| rows | R | 18 | 18 | relative 1e-12 | pass |
| total mpg | R | 431.5 | 431.5 | relative 1e-12 | pass |

**mtcars: the numbers of cylinders whose cars average under 19 mpg removed (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars filter(~(mean().over() < 19)) | 18 | 18 | relative 1e-12 | pass |
| total mpg | Polars filter(~(mean().over() < 19)) | 431.5 | 431.5 | relative 1e-12 | pass |

### `table.keep_rows_found_in`

**warpbreaks: the looms run at low or high tension (a list with a repeat)** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas isin | 36 | 36 | exact | pass |
| total breaks | pandas isin | 1045 | 1045 | exact | pass |
| sum of row x breaks | pandas isin | 16616 | 16616 | exact | pass |
| rows | R | 36 | 36 | exact | pass |
| total breaks | R | 1045 | 1045 | exact | pass |
| sum of row x breaks | R | 16616 | 16616 | exact | pass |

**warpbreaks: the looms run at low or high tension (a list with a repeat) (a Polars table)** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars join(how="semi") | 36 | 36 | exact | pass |
| total breaks | Polars join(how="semi") | 1045 | 1045 | exact | pass |
| sum of row x breaks | Polars join(how="semi") | 16616 | 16616 | exact | pass |

### `table.remove_rows_found_in`

**warpbreaks: the looms run at low tension removed** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas ~isin | 36 | 36 | exact | pass |
| total breaks | pandas ~isin | 865 | 865 | exact | pass |
| sum of row x breaks | pandas ~isin | 15626 | 15626 | exact | pass |
| rows | R | 36 | 36 | exact | pass |
| total breaks | R | 865 | 865 | exact | pass |
| sum of row x breaks | R | 15626 | 15626 | exact | pass |

**warpbreaks: the looms run at low tension removed (a Polars table)** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars join(how="anti") | 36 | 36 | exact | pass |
| total breaks | Polars join(how="anti") | 865 | 865 | exact | pass |
| sum of row x breaks | Polars join(how="anti") | 15626 | 15626 | exact | pass |

### `table.keep_rows_where capitals_matter=`

**iris: the flowers whose species is SETOSA, capitals not mattering** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas str.lower() == | 50 | 50 | relative 1e-12 | pass |
| total sepal length | pandas str.lower() == | 250.3 | 250.3 | relative 1e-12 | pass |
| rows | R | 50 | 50 | relative 1e-12 | pass |
| total sepal length | R | 250.3 | 250.3 | relative 1e-12 | pass |

**iris: the flowers whose species is SETOSA, capitals not mattering (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars str.to_lowercase() == | 50 | 50 | relative 1e-12 | pass |
| total sepal length | Polars str.to_lowercase() == | 250.3 | 250.3 | relative 1e-12 | pass |

### `table.make_one_table_for_each_group_in`

**iris: one table for each of the three species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| tables | pandas groupby(sort=False) | 3 | 3 | relative 1e-12 | pass |
| setosa: flowers | pandas groupby(sort=False) | 50 | 50 | relative 1e-12 | pass |
| versicolor: flowers | pandas groupby(sort=False) | 50 | 50 | relative 1e-12 | pass |
| virginica: flowers | pandas groupby(sort=False) | 50 | 50 | relative 1e-12 | pass |
| setosa: total petal length | pandas groupby(sort=False) | 73.1 | 73.1 | relative 1e-12 | pass |
| versicolor: total petal length | pandas groupby(sort=False) | 213 | 213 | relative 1e-12 | pass |
| virginica: total petal length | pandas groupby(sort=False) | 277.6 | 277.6 | relative 1e-12 | pass |
| tables | R | 3 | 3 | relative 1e-12 | pass |
| setosa: flowers | R | 50 | 50 | relative 1e-12 | pass |
| versicolor: flowers | R | 50 | 50 | relative 1e-12 | pass |
| virginica: flowers | R | 50 | 50 | relative 1e-12 | pass |
| setosa: total petal length | R | 73.1 | 73.1 | relative 1e-12 | pass |
| versicolor: total petal length | R | 213 | 213 | relative 1e-12 | pass |
| virginica: total petal length | R | 277.6 | 277.6 | relative 1e-12 | pass |

**iris: one table for each of the three species (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| tables | Polars partition_by(as_dict=True) | 3 | 3 | relative 1e-12 | pass |
| setosa: flowers | Polars partition_by(as_dict=True) | 50 | 50 | relative 1e-12 | pass |
| versicolor: flowers | Polars partition_by(as_dict=True) | 50 | 50 | relative 1e-12 | pass |
| virginica: flowers | Polars partition_by(as_dict=True) | 50 | 50 | relative 1e-12 | pass |
| setosa: total petal length | Polars partition_by(as_dict=True) | 73.1 | 73.1 | relative 1e-12 | pass |
| versicolor: total petal length | Polars partition_by(as_dict=True) | 213 | 213 | relative 1e-12 | pass |
| virginica: total petal length | Polars partition_by(as_dict=True) | 277.6 | 277.6 | relative 1e-12 | pass |

### `table.move_columns`

**mtcars: horsepower and weight moved to the front** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas df[columns in the new order] | 12 | 12 | exact | pass |
| column 1: hp | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 2: wt | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 3: model | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 4: mpg | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 5: cyl | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 6: disp | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 7: drat | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 8: qsec | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 9: vs | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 10: am | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 11: gear | pandas df[columns in the new order] | 1 | 1 | exact | pass |
| column 12: carb | pandas df[columns in the new order] | 1 | 1 | exact | pass |

**mtcars: horsepower and weight moved to the front (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Polars select(columns in the new order) | 12 | 12 | exact | pass |
| column 1: hp | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 2: wt | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 3: model | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 4: mpg | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 5: cyl | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 6: disp | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 7: drat | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 8: qsec | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 9: vs | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 10: am | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 11: gear | Polars select(columns in the new order) | 1 | 1 | exact | pass |
| column 12: carb | Polars select(columns in the new order) | 1 | 1 | exact | pass |

### `table.rename_columns`

**mtcars: mpg and hp given longer names** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas rename(columns=) | 12 | 12 | exact | pass |
| total horsepower | pandas rename(columns=) | 4694 | 4694 | exact | pass |
| column 1: model | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 2: miles_per_gallon | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 3: cyl | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 4: disp | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 5: horsepower | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 6: drat | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 7: wt | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 8: qsec | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 9: vs | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 10: am | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 11: gear | pandas rename(columns=) | 1 | 1 | exact | pass |
| column 12: carb | pandas rename(columns=) | 1 | 1 | exact | pass |

**mtcars: mpg and hp given longer names (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Polars rename | 12 | 12 | exact | pass |
| total horsepower | Polars rename | 4694 | 4694 | exact | pass |
| column 1: model | Polars rename | 1 | 1 | exact | pass |
| column 2: miles_per_gallon | Polars rename | 1 | 1 | exact | pass |
| column 3: cyl | Polars rename | 1 | 1 | exact | pass |
| column 4: disp | Polars rename | 1 | 1 | exact | pass |
| column 5: horsepower | Polars rename | 1 | 1 | exact | pass |
| column 6: drat | Polars rename | 1 | 1 | exact | pass |
| column 7: wt | Polars rename | 1 | 1 | exact | pass |
| column 8: qsec | Polars rename | 1 | 1 | exact | pass |
| column 9: vs | Polars rename | 1 | 1 | exact | pass |
| column 10: am | Polars rename | 1 | 1 | exact | pass |
| column 11: gear | Polars rename | 1 | 1 | exact | pass |
| column 12: carb | Polars rename | 1 | 1 | exact | pass |

### `table.count_columns`

**the 12 columns of mtcars (the car names and 11 measurements)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Henderson & Velleman (1981): 11 variables, with the car names | 12 | 12 | within 0 (printed rounding) | pass |
| columns | pandas shape[1] | 12 | 12 | exact | pass |

**the 12 columns of mtcars (the car names and 11 measurements) (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Polars width | 12 | 12 | exact | pass |

### `table.remove_columns_that_are_all_empty`

**NHANES: the 9 people without a body mass index; their bmi column, all empty, removed** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas dropna(axis=1, how="all") | 3 | 3 | exact | pass |
| column 1: age | pandas dropna(axis=1, how="all") | 1 | 1 | exact | pass |
| column 2: hyp | pandas dropna(axis=1, how="all") | 1 | 1 | exact | pass |
| column 3: chl | pandas dropna(axis=1, how="all") | 1 | 1 | exact | pass |
| columns | R | 3 | 3 | exact | pass |
| column 1: age | R | 1 | 1 | exact | pass |
| column 2: hyp | R | 1 | 1 | exact | pass |
| column 3: chl | R | 1 | 1 | exact | pass |

**NHANES: the 9 people without a body mass index; their bmi column, all empty, removed (a Polars table)** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Polars select(columns with null_count() < height) | 3 | 3 | exact | pass |
| column 1: age | Polars select(columns with null_count() < height) | 1 | 1 | exact | pass |
| column 2: hyp | Polars select(columns with null_count() < height) | 1 | 1 | exact | pass |
| column 3: chl | Polars select(columns with null_count() < height) | 1 | 1 | exact | pass |

### `table.remove_rows_that_are_all_empty`

**NHANES body mass index, hypertension and cholesterol: the 7 people with none of the three removed** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows left | pandas dropna(how="all") | 18 | 18 | exact | pass |
| total cholesterol | pandas dropna(how="all") | 2871 | 2871 | exact | pass |
| empty bmi left | pandas dropna(how="all") | 2 | 2 | exact | pass |
| rows left | R | 18 | 18 | exact | pass |
| total cholesterol | R | 2871 | 2871 | exact | pass |
| empty bmi left | R | 2 | 2 | exact | pass |

**NHANES body mass index, hypertension and cholesterol: the 7 people with none of the three removed (a Polars table)** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows left | Polars filter(~all_horizontal(is_null())) | 18 | 18 | exact | pass |
| total cholesterol | Polars filter(~all_horizontal(is_null())) | 2871 | 2871 | exact | pass |
| empty bmi left | Polars filter(~all_horizontal(is_null())) | 2 | 2 | exact | pass |

### `table.sort_by biggest_first=`

**mtcars sorted by cylinders (fewest first), then by miles per gallon (most first)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas sort_values(ascending=[True, False], kind="stable") | 32 | 32 | exact | pass |
| row 1: Toyota Corolla | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 2: Fiat 128 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 3: Honda Civic | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 4: Lotus Europa | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 5: Fiat X1-9 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 6: Porsche 914-2 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 7: Merc 240D | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 8: Datsun 710 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 9: Merc 230 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 10: Toyota Corona | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 11: Volvo 142E | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 12: Hornet 4 Drive | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 13: Mazda RX4 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 14: Mazda RX4 Wag | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 15: Ferrari Dino | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 16: Merc 280 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 17: Valiant | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 18: Merc 280C | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 19: Pontiac Firebird | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 20: Hornet Sportabout | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 21: Merc 450SL | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 22: Merc 450SE | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 23: Ford Pantera L | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 24: Dodge Challenger | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 25: Merc 450SLC | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 26: AMC Javelin | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 27: Maserati Bora | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 28: Chrysler Imperial | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 29: Duster 360 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 30: Camaro Z28 | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 31: Cadillac Fleetwood | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| row 32: Lincoln Continental | pandas sort_values(ascending=[True, False], kind="stable") | 1 | 1 | exact | pass |
| rows | R | 32 | 32 | exact | pass |
| row 1: Toyota Corolla | R | 1 | 1 | exact | pass |
| row 2: Fiat 128 | R | 1 | 1 | exact | pass |
| row 3: Honda Civic | R | 1 | 1 | exact | pass |
| row 4: Lotus Europa | R | 1 | 1 | exact | pass |
| row 5: Fiat X1-9 | R | 1 | 1 | exact | pass |
| row 6: Porsche 914-2 | R | 1 | 1 | exact | pass |
| row 7: Merc 240D | R | 1 | 1 | exact | pass |
| row 8: Datsun 710 | R | 1 | 1 | exact | pass |
| row 9: Merc 230 | R | 1 | 1 | exact | pass |
| row 10: Toyota Corona | R | 1 | 1 | exact | pass |
| row 11: Volvo 142E | R | 1 | 1 | exact | pass |
| row 12: Hornet 4 Drive | R | 1 | 1 | exact | pass |
| row 13: Mazda RX4 | R | 1 | 1 | exact | pass |
| row 14: Mazda RX4 Wag | R | 1 | 1 | exact | pass |
| row 15: Ferrari Dino | R | 1 | 1 | exact | pass |
| row 16: Merc 280 | R | 1 | 1 | exact | pass |
| row 17: Valiant | R | 1 | 1 | exact | pass |
| row 18: Merc 280C | R | 1 | 1 | exact | pass |
| row 19: Pontiac Firebird | R | 1 | 1 | exact | pass |
| row 20: Hornet Sportabout | R | 1 | 1 | exact | pass |
| row 21: Merc 450SL | R | 1 | 1 | exact | pass |
| row 22: Merc 450SE | R | 1 | 1 | exact | pass |
| row 23: Ford Pantera L | R | 1 | 1 | exact | pass |
| row 24: Dodge Challenger | R | 1 | 1 | exact | pass |
| row 25: Merc 450SLC | R | 1 | 1 | exact | pass |
| row 26: AMC Javelin | R | 1 | 1 | exact | pass |
| row 27: Maserati Bora | R | 1 | 1 | exact | pass |
| row 28: Chrysler Imperial | R | 1 | 1 | exact | pass |
| row 29: Duster 360 | R | 1 | 1 | exact | pass |
| row 30: Camaro Z28 | R | 1 | 1 | exact | pass |
| row 31: Cadillac Fleetwood | R | 1 | 1 | exact | pass |
| row 32: Lincoln Continental | R | 1 | 1 | exact | pass |

**mtcars sorted by cylinders (fewest first), then by miles per gallon (most first) (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars sort(descending=[False, True], maintain_order=True) | 32 | 32 | exact | pass |
| row 1: Toyota Corolla | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 2: Fiat 128 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 3: Honda Civic | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 4: Lotus Europa | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 5: Fiat X1-9 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 6: Porsche 914-2 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 7: Merc 240D | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 8: Datsun 710 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 9: Merc 230 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 10: Toyota Corona | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 11: Volvo 142E | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 12: Hornet 4 Drive | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 13: Mazda RX4 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 14: Mazda RX4 Wag | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 15: Ferrari Dino | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 16: Merc 280 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 17: Valiant | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 18: Merc 280C | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 19: Pontiac Firebird | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 20: Hornet Sportabout | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 21: Merc 450SL | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 22: Merc 450SE | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 23: Ford Pantera L | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 24: Dodge Challenger | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 25: Merc 450SLC | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 26: AMC Javelin | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 27: Maserati Bora | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 28: Chrysler Imperial | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 29: Duster 360 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 30: Camaro Z28 | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 31: Cadillac Fleetwood | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |
| row 32: Lincoln Continental | Polars sort(descending=[False, True], maintain_order=True) | 1 | 1 | exact | pass |

### `table.split_into_rows`

**mtcars: each word of a car's name on its own row** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas str.split, explode | 66 | 66 | relative 1e-12 | pass |
| Merc | pandas str.split, explode | 7 | 7 | relative 1e-12 | pass |
| total mpg | pandas str.split, explode | 1325.9 | 1325.9 | relative 1e-12 | pass |
| row 1: Mazda | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 2: RX4 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 3: Mazda | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 4: RX4 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 5: Wag | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 6: Datsun | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 7: 710 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 8: Hornet | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 9: 4 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 10: Drive | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 11: Hornet | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 12: Sportabout | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 13: Valiant | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 14: Duster | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 15: 360 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 16: Merc | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 17: 240D | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 18: Merc | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 19: 230 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 20: Merc | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 21: 280 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 22: Merc | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 23: 280C | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 24: Merc | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 25: 450SE | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 26: Merc | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 27: 450SL | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 28: Merc | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 29: 450SLC | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 30: Cadillac | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 31: Fleetwood | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 32: Lincoln | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 33: Continental | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 34: Chrysler | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 35: Imperial | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 36: Fiat | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 37: 128 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 38: Honda | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 39: Civic | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 40: Toyota | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 41: Corolla | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 42: Toyota | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 43: Corona | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 44: Dodge | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 45: Challenger | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 46: AMC | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 47: Javelin | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 48: Camaro | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 49: Z28 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 50: Pontiac | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 51: Firebird | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 52: Fiat | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 53: X1-9 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 54: Porsche | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 55: 914-2 | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 56: Lotus | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 57: Europa | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 58: Ford | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 59: Pantera | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 60: L | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 61: Ferrari | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 62: Dino | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 63: Maserati | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 64: Bora | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 65: Volvo | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 66: 142E | pandas str.split, explode | 1 | 1 | relative 1e-12 | pass |
| rows | R | 66 | 66 | relative 1e-12 | pass |
| Merc | R | 7 | 7 | relative 1e-12 | pass |
| total mpg | R | 1325.9 | 1325.9 | relative 1e-12 | pass |
| row 1: Mazda | R | 1 | 1 | relative 1e-12 | pass |
| row 2: RX4 | R | 1 | 1 | relative 1e-12 | pass |
| row 3: Mazda | R | 1 | 1 | relative 1e-12 | pass |
| row 4: RX4 | R | 1 | 1 | relative 1e-12 | pass |
| row 5: Wag | R | 1 | 1 | relative 1e-12 | pass |
| row 6: Datsun | R | 1 | 1 | relative 1e-12 | pass |
| row 7: 710 | R | 1 | 1 | relative 1e-12 | pass |
| row 8: Hornet | R | 1 | 1 | relative 1e-12 | pass |
| row 9: 4 | R | 1 | 1 | relative 1e-12 | pass |
| row 10: Drive | R | 1 | 1 | relative 1e-12 | pass |
| row 11: Hornet | R | 1 | 1 | relative 1e-12 | pass |
| row 12: Sportabout | R | 1 | 1 | relative 1e-12 | pass |
| row 13: Valiant | R | 1 | 1 | relative 1e-12 | pass |
| row 14: Duster | R | 1 | 1 | relative 1e-12 | pass |
| row 15: 360 | R | 1 | 1 | relative 1e-12 | pass |
| row 16: Merc | R | 1 | 1 | relative 1e-12 | pass |
| row 17: 240D | R | 1 | 1 | relative 1e-12 | pass |
| row 18: Merc | R | 1 | 1 | relative 1e-12 | pass |
| row 19: 230 | R | 1 | 1 | relative 1e-12 | pass |
| row 20: Merc | R | 1 | 1 | relative 1e-12 | pass |
| row 21: 280 | R | 1 | 1 | relative 1e-12 | pass |
| row 22: Merc | R | 1 | 1 | relative 1e-12 | pass |
| row 23: 280C | R | 1 | 1 | relative 1e-12 | pass |
| row 24: Merc | R | 1 | 1 | relative 1e-12 | pass |
| row 25: 450SE | R | 1 | 1 | relative 1e-12 | pass |
| row 26: Merc | R | 1 | 1 | relative 1e-12 | pass |
| row 27: 450SL | R | 1 | 1 | relative 1e-12 | pass |
| row 28: Merc | R | 1 | 1 | relative 1e-12 | pass |
| row 29: 450SLC | R | 1 | 1 | relative 1e-12 | pass |
| row 30: Cadillac | R | 1 | 1 | relative 1e-12 | pass |
| row 31: Fleetwood | R | 1 | 1 | relative 1e-12 | pass |
| row 32: Lincoln | R | 1 | 1 | relative 1e-12 | pass |
| row 33: Continental | R | 1 | 1 | relative 1e-12 | pass |
| row 34: Chrysler | R | 1 | 1 | relative 1e-12 | pass |
| row 35: Imperial | R | 1 | 1 | relative 1e-12 | pass |
| row 36: Fiat | R | 1 | 1 | relative 1e-12 | pass |
| row 37: 128 | R | 1 | 1 | relative 1e-12 | pass |
| row 38: Honda | R | 1 | 1 | relative 1e-12 | pass |
| row 39: Civic | R | 1 | 1 | relative 1e-12 | pass |
| row 40: Toyota | R | 1 | 1 | relative 1e-12 | pass |
| row 41: Corolla | R | 1 | 1 | relative 1e-12 | pass |
| row 42: Toyota | R | 1 | 1 | relative 1e-12 | pass |
| row 43: Corona | R | 1 | 1 | relative 1e-12 | pass |
| row 44: Dodge | R | 1 | 1 | relative 1e-12 | pass |
| row 45: Challenger | R | 1 | 1 | relative 1e-12 | pass |
| row 46: AMC | R | 1 | 1 | relative 1e-12 | pass |
| row 47: Javelin | R | 1 | 1 | relative 1e-12 | pass |
| row 48: Camaro | R | 1 | 1 | relative 1e-12 | pass |
| row 49: Z28 | R | 1 | 1 | relative 1e-12 | pass |
| row 50: Pontiac | R | 1 | 1 | relative 1e-12 | pass |
| row 51: Firebird | R | 1 | 1 | relative 1e-12 | pass |
| row 52: Fiat | R | 1 | 1 | relative 1e-12 | pass |
| row 53: X1-9 | R | 1 | 1 | relative 1e-12 | pass |
| row 54: Porsche | R | 1 | 1 | relative 1e-12 | pass |
| row 55: 914-2 | R | 1 | 1 | relative 1e-12 | pass |
| row 56: Lotus | R | 1 | 1 | relative 1e-12 | pass |
| row 57: Europa | R | 1 | 1 | relative 1e-12 | pass |
| row 58: Ford | R | 1 | 1 | relative 1e-12 | pass |
| row 59: Pantera | R | 1 | 1 | relative 1e-12 | pass |
| row 60: L | R | 1 | 1 | relative 1e-12 | pass |
| row 61: Ferrari | R | 1 | 1 | relative 1e-12 | pass |
| row 62: Dino | R | 1 | 1 | relative 1e-12 | pass |
| row 63: Maserati | R | 1 | 1 | relative 1e-12 | pass |
| row 64: Bora | R | 1 | 1 | relative 1e-12 | pass |
| row 65: Volvo | R | 1 | 1 | relative 1e-12 | pass |
| row 66: 142E | R | 1 | 1 | relative 1e-12 | pass |

**mtcars: each word of a car's name on its own row (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars str.split, explode | 66 | 66 | relative 1e-12 | pass |
| Merc | Polars str.split, explode | 7 | 7 | relative 1e-12 | pass |
| total mpg | Polars str.split, explode | 1325.9 | 1325.9 | relative 1e-12 | pass |
| row 1: Mazda | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 2: RX4 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 3: Mazda | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 4: RX4 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 5: Wag | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 6: Datsun | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 7: 710 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 8: Hornet | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 9: 4 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 10: Drive | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 11: Hornet | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 12: Sportabout | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 13: Valiant | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 14: Duster | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 15: 360 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 16: Merc | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 17: 240D | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 18: Merc | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 19: 230 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 20: Merc | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 21: 280 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 22: Merc | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 23: 280C | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 24: Merc | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 25: 450SE | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 26: Merc | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 27: 450SL | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 28: Merc | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 29: 450SLC | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 30: Cadillac | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 31: Fleetwood | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 32: Lincoln | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 33: Continental | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 34: Chrysler | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 35: Imperial | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 36: Fiat | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 37: 128 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 38: Honda | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 39: Civic | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 40: Toyota | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 41: Corolla | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 42: Toyota | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 43: Corona | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 44: Dodge | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 45: Challenger | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 46: AMC | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 47: Javelin | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 48: Camaro | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 49: Z28 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 50: Pontiac | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 51: Firebird | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 52: Fiat | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 53: X1-9 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 54: Porsche | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 55: 914-2 | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 56: Lotus | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 57: Europa | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 58: Ford | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 59: Pantera | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 60: L | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 61: Ferrari | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 62: Dino | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 63: Maserati | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 64: Bora | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 65: Volvo | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |
| row 66: 142E | Polars str.split, explode | 1 | 1 | relative 1e-12 | pass |

### `table.gather_into_rows starts_with=`

**iris: the two sepal columns (names starting with "Sepal.") turned into rows** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas melt | 300 | 300 | relative 1e-12 | pass |
| columns | pandas melt | 5 | 5 | relative 1e-12 | pass |
| total cm | pandas melt | 1335.1 | 1335.1 | relative 1e-12 | pass |
| Sepal.Width rows | pandas melt | 150 | 150 | relative 1e-12 | pass |
| row 151 | pandas melt | 3.5 | 3.5 | relative 1e-12 | pass |
| rows | R | 300 | 300 | relative 1e-12 | pass |
| total cm | R | 1335.1 | 1335.1 | relative 1e-12 | pass |
| Sepal.Width rows | R | 150 | 150 | relative 1e-12 | pass |
| row 151 | R | 3.5 | 3.5 | relative 1e-12 | pass |

**iris: the two sepal columns (names starting with "Sepal.") turned into rows (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars unpivot(on=cs.starts_with()) | 300 | 300 | relative 1e-12 | pass |
| columns | Polars unpivot(on=cs.starts_with()) | 5 | 5 | relative 1e-12 | pass |
| total cm | Polars unpivot(on=cs.starts_with()) | 1335.1 | 1335.1 | relative 1e-12 | pass |
| Sepal.Width rows | Polars unpivot(on=cs.starts_with()) | 150 | 150 | relative 1e-12 | pass |
| row 151 | Polars unpivot(on=cs.starts_with()) | 3.5 | 3.5 | relative 1e-12 | pass |

### `table.spread_into_columns show=`

**warpbreaks: the total breaks for each wool (rows) and tension (columns)** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas pivot_table(aggfunc="sum") | 4 | 4 | exact | pass |
| wool A, tension L | pandas pivot_table(aggfunc="sum") | 401 | 401 | exact | pass |
| wool A, tension M | pandas pivot_table(aggfunc="sum") | 216 | 216 | exact | pass |
| wool A, tension H | pandas pivot_table(aggfunc="sum") | 221 | 221 | exact | pass |
| wool B, tension L | pandas pivot_table(aggfunc="sum") | 254 | 254 | exact | pass |
| wool B, tension M | pandas pivot_table(aggfunc="sum") | 259 | 259 | exact | pass |
| wool B, tension H | pandas pivot_table(aggfunc="sum") | 169 | 169 | exact | pass |
| wool A, tension L | R | 401 | 401 | exact | pass |
| wool A, tension M | R | 216 | 216 | exact | pass |
| wool A, tension H | R | 221 | 221 | exact | pass |
| wool B, tension L | R | 254 | 254 | exact | pass |
| wool B, tension M | R | 259 | 259 | exact | pass |
| wool B, tension H | R | 169 | 169 | exact | pass |

**warpbreaks: the total breaks for each wool (rows) and tension (columns) (a Polars table)** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Polars pivot(aggregate_function="sum") | 4 | 4 | exact | pass |
| wool A, tension L | Polars pivot(aggregate_function="sum") | 401 | 401 | exact | pass |
| wool A, tension M | Polars pivot(aggregate_function="sum") | 216 | 216 | exact | pass |
| wool A, tension H | Polars pivot(aggregate_function="sum") | 221 | 221 | exact | pass |
| wool B, tension L | Polars pivot(aggregate_function="sum") | 254 | 254 | exact | pass |
| wool B, tension M | Polars pivot(aggregate_function="sum") | 259 | 259 | exact | pass |
| wool B, tension H | Polars pivot(aggregate_function="sum") | 169 | 169 | exact | pass |

### `table.spread_into_yes_no_columns`

**iris: a yes/no column for each species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas get_dummies(prefix_sep=": ") | 8 | 8 | exact | pass |
| yes in Species: setosa | pandas get_dummies(prefix_sep=": ") | 50 | 50 | exact | pass |
| yes in Species: versicolor | pandas get_dummies(prefix_sep=": ") | 50 | 50 | exact | pass |
| yes in Species: virginica | pandas get_dummies(prefix_sep=": ") | 50 | 50 | exact | pass |
| row 51 is versicolor | pandas get_dummies(prefix_sep=": ") | 1 | 1 | exact | pass |
| yes in Species: setosa | R | 50 | 50 | exact | pass |
| yes in Species: versicolor | R | 50 | 50 | exact | pass |
| yes in Species: virginica | R | 50 | 50 | exact | pass |
| row 51 is versicolor | R | 1 | 1 | exact | pass |

**iris: a yes/no column for each species (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | Polars to_dummies(separator=": ") | 8 | 8 | exact | pass |
| yes in Species: setosa | Polars to_dummies(separator=": ") | 50 | 50 | exact | pass |
| yes in Species: versicolor | Polars to_dummies(separator=": ") | 50 | 50 | exact | pass |
| yes in Species: virginica | Polars to_dummies(separator=": ") | 50 | 50 | exact | pass |
| row 51 is versicolor | Polars to_dummies(separator=": ") | 1 | 1 | exact | pass |

### `table.join_with keep="every combination"`

**mtcars: every car paired with both kinds of gearbox (64 rows)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas merge(how="cross") | 64 | 64 | relative 1e-12 | pass |
| total mpg | pandas merge(how="cross") | 1285.8 | 1285.8 | relative 1e-12 | pass |
| row 1: Mazda RX4 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 2: Mazda RX4 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 3: Mazda RX4 Wag / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 4: Mazda RX4 Wag / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 5: Datsun 710 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 6: Datsun 710 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 7: Hornet 4 Drive / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 8: Hornet 4 Drive / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 9: Hornet Sportabout / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 10: Hornet Sportabout / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 11: Valiant / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 12: Valiant / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 13: Duster 360 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 14: Duster 360 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 15: Merc 240D / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 16: Merc 240D / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 17: Merc 230 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 18: Merc 230 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 19: Merc 280 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 20: Merc 280 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 21: Merc 280C / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 22: Merc 280C / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 23: Merc 450SE / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 24: Merc 450SE / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 25: Merc 450SL / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 26: Merc 450SL / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 27: Merc 450SLC / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 28: Merc 450SLC / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 29: Cadillac Fleetwood / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 30: Cadillac Fleetwood / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 31: Lincoln Continental / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 32: Lincoln Continental / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 33: Chrysler Imperial / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 34: Chrysler Imperial / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 35: Fiat 128 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 36: Fiat 128 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 37: Honda Civic / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 38: Honda Civic / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 39: Toyota Corolla / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 40: Toyota Corolla / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 41: Toyota Corona / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 42: Toyota Corona / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 43: Dodge Challenger / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 44: Dodge Challenger / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 45: AMC Javelin / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 46: AMC Javelin / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 47: Camaro Z28 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 48: Camaro Z28 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 49: Pontiac Firebird / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 50: Pontiac Firebird / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 51: Fiat X1-9 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 52: Fiat X1-9 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 53: Porsche 914-2 / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 54: Porsche 914-2 / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 55: Lotus Europa / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 56: Lotus Europa / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 57: Ford Pantera L / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 58: Ford Pantera L / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 59: Ferrari Dino / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 60: Ferrari Dino / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 61: Maserati Bora / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 62: Maserati Bora / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 63: Volvo 142E / automatic | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 64: Volvo 142E / manual | pandas merge(how="cross") | 1 | 1 | relative 1e-12 | pass |
| rows | R | 64 | 64 | relative 1e-12 | pass |
| total mpg | R | 1285.8 | 1285.8 | relative 1e-12 | pass |
| row 1: Mazda RX4 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 2: Mazda RX4 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 3: Mazda RX4 Wag / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 4: Mazda RX4 Wag / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 5: Datsun 710 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 6: Datsun 710 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 7: Hornet 4 Drive / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 8: Hornet 4 Drive / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 9: Hornet Sportabout / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 10: Hornet Sportabout / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 11: Valiant / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 12: Valiant / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 13: Duster 360 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 14: Duster 360 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 15: Merc 240D / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 16: Merc 240D / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 17: Merc 230 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 18: Merc 230 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 19: Merc 280 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 20: Merc 280 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 21: Merc 280C / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 22: Merc 280C / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 23: Merc 450SE / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 24: Merc 450SE / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 25: Merc 450SL / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 26: Merc 450SL / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 27: Merc 450SLC / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 28: Merc 450SLC / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 29: Cadillac Fleetwood / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 30: Cadillac Fleetwood / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 31: Lincoln Continental / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 32: Lincoln Continental / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 33: Chrysler Imperial / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 34: Chrysler Imperial / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 35: Fiat 128 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 36: Fiat 128 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 37: Honda Civic / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 38: Honda Civic / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 39: Toyota Corolla / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 40: Toyota Corolla / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 41: Toyota Corona / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 42: Toyota Corona / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 43: Dodge Challenger / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 44: Dodge Challenger / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 45: AMC Javelin / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 46: AMC Javelin / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 47: Camaro Z28 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 48: Camaro Z28 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 49: Pontiac Firebird / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 50: Pontiac Firebird / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 51: Fiat X1-9 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 52: Fiat X1-9 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 53: Porsche 914-2 / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 54: Porsche 914-2 / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 55: Lotus Europa / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 56: Lotus Europa / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 57: Ford Pantera L / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 58: Ford Pantera L / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 59: Ferrari Dino / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 60: Ferrari Dino / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 61: Maserati Bora / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 62: Maserati Bora / manual | R | 1 | 1 | relative 1e-12 | pass |
| row 63: Volvo 142E / automatic | R | 1 | 1 | relative 1e-12 | pass |
| row 64: Volvo 142E / manual | R | 1 | 1 | relative 1e-12 | pass |

**mtcars: every car paired with both kinds of gearbox (64 rows) (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars join(how="cross") | 64 | 64 | relative 1e-12 | pass |
| total mpg | Polars join(how="cross") | 1285.8 | 1285.8 | relative 1e-12 | pass |
| row 1: Mazda RX4 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 2: Mazda RX4 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 3: Mazda RX4 Wag / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 4: Mazda RX4 Wag / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 5: Datsun 710 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 6: Datsun 710 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 7: Hornet 4 Drive / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 8: Hornet 4 Drive / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 9: Hornet Sportabout / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 10: Hornet Sportabout / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 11: Valiant / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 12: Valiant / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 13: Duster 360 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 14: Duster 360 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 15: Merc 240D / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 16: Merc 240D / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 17: Merc 230 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 18: Merc 230 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 19: Merc 280 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 20: Merc 280 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 21: Merc 280C / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 22: Merc 280C / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 23: Merc 450SE / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 24: Merc 450SE / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 25: Merc 450SL / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 26: Merc 450SL / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 27: Merc 450SLC / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 28: Merc 450SLC / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 29: Cadillac Fleetwood / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 30: Cadillac Fleetwood / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 31: Lincoln Continental / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 32: Lincoln Continental / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 33: Chrysler Imperial / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 34: Chrysler Imperial / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 35: Fiat 128 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 36: Fiat 128 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 37: Honda Civic / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 38: Honda Civic / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 39: Toyota Corolla / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 40: Toyota Corolla / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 41: Toyota Corona / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 42: Toyota Corona / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 43: Dodge Challenger / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 44: Dodge Challenger / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 45: AMC Javelin / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 46: AMC Javelin / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 47: Camaro Z28 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 48: Camaro Z28 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 49: Pontiac Firebird / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 50: Pontiac Firebird / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 51: Fiat X1-9 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 52: Fiat X1-9 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 53: Porsche 914-2 / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 54: Porsche 914-2 / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 55: Lotus Europa / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 56: Lotus Europa / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 57: Ford Pantera L / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 58: Ford Pantera L / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 59: Ferrari Dino / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 60: Ferrari Dino / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 61: Maserati Bora / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 62: Maserati Bora / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 63: Volvo 142E / automatic | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |
| row 64: Volvo 142E / manual | Polars join(how="cross") | 1 | 1 | relative 1e-12 | pass |

### `table.join_with match=`

**AirPassengers: each month joined to the start of its quarter (January, April, July, October) when that is at most 40 days before** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas merge_asof(direction="backward", tolerance=40 days) | 144 | 144 | exact | pass |
| empty | pandas merge_asof(direction="backward", tolerance=40 days) | 48 | 48 | exact | pass |
| total | pandas merge_asof(direction="backward", tolerance=40 days) | 27042 | 27042 | exact | pass |
| February 1949 | pandas merge_asof(direction="backward", tolerance=40 days) | 112 | 112 | exact | pass |
| sum of row x value | pandas merge_asof(direction="backward", tolerance=40 days) | 2401719 | 2401719 | exact | pass |
| rows | R | 144 | 144 | exact | pass |
| empty | R | 48 | 48 | exact | pass |
| total | R | 27042 | 27042 | exact | pass |
| February 1949 | R | 112 | 112 | exact | pass |
| sum of row x value | R | 2401719 | 2401719 | exact | pass |

**AirPassengers: each month joined to the start of its quarter (January, April, July, October) when that is at most 40 days before (a Polars table)** (real data; data: AirPassengers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars join_asof(strategy="backward", tolerance=40 days) | 144 | 144 | exact | pass |
| empty | Polars join_asof(strategy="backward", tolerance=40 days) | 48 | 48 | exact | pass |
| total | Polars join_asof(strategy="backward", tolerance=40 days) | 27042 | 27042 | exact | pass |
| February 1949 | Polars join_asof(strategy="backward", tolerance=40 days) | 112 | 112 | exact | pass |
| sum of row x value | Polars join_asof(strategy="backward", tolerance=40 days) | 2401719 | 2401719 | exact | pass |

### `table.join_with using=`

**iris joined to a table of the species' average petal length, named "kind" there** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas merge(left_on=, right_on=, validate="many_to_one") | 150 | 150 | relative 1e-12 | pass |
| columns | pandas merge(left_on=, right_on=, validate="many_to_one") | 6 | 6 | relative 1e-12 | pass |
| total | pandas merge(left_on=, right_on=, validate="many_to_one") | 563.7 | 563.7 | relative 1e-12 | pass |
| row 150 | pandas merge(left_on=, right_on=, validate="many_to_one") | 5.552 | 5.552 | relative 1e-12 | pass |
| column 1: Sepal.Length | pandas merge(left_on=, right_on=, validate="many_to_one") | 1 | 1 | relative 1e-12 | pass |
| column 2: Sepal.Width | pandas merge(left_on=, right_on=, validate="many_to_one") | 1 | 1 | relative 1e-12 | pass |
| column 3: Petal.Length | pandas merge(left_on=, right_on=, validate="many_to_one") | 1 | 1 | relative 1e-12 | pass |
| column 4: Petal.Width | pandas merge(left_on=, right_on=, validate="many_to_one") | 1 | 1 | relative 1e-12 | pass |
| column 5: Species | pandas merge(left_on=, right_on=, validate="many_to_one") | 1 | 1 | relative 1e-12 | pass |
| column 6: species_petal_length | pandas merge(left_on=, right_on=, validate="many_to_one") | 1 | 1 | relative 1e-12 | pass |
| rows | R | 150 | 150 | relative 1e-12 | pass |
| total | R | 563.7 | 563.7 | relative 1e-12 | pass |
| row 150 | R | 5.552 | 5.552 | relative 1e-12 | pass |

**iris joined to a table of the species' average petal length, named "kind" there (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars join(left_on=, right_on=, validate="m:1") | 150 | 150 | relative 1e-12 | pass |
| columns | Polars join(left_on=, right_on=, validate="m:1") | 6 | 6 | relative 1e-12 | pass |
| total | Polars join(left_on=, right_on=, validate="m:1") | 563.7 | 563.7 | relative 1e-12 | pass |
| row 150 | Polars join(left_on=, right_on=, validate="m:1") | 5.552 | 5.552 | relative 1e-12 | pass |
| column 1: Sepal.Length | Polars join(left_on=, right_on=, validate="m:1") | 1 | 1 | relative 1e-12 | pass |
| column 2: Sepal.Width | Polars join(left_on=, right_on=, validate="m:1") | 1 | 1 | relative 1e-12 | pass |
| column 3: Petal.Length | Polars join(left_on=, right_on=, validate="m:1") | 1 | 1 | relative 1e-12 | pass |
| column 4: Petal.Width | Polars join(left_on=, right_on=, validate="m:1") | 1 | 1 | relative 1e-12 | pass |
| column 5: Species | Polars join(left_on=, right_on=, validate="m:1") | 1 | 1 | relative 1e-12 | pass |
| column 6: species_petal_length | Polars join(left_on=, right_on=, validate="m:1") | 1 | 1 | relative 1e-12 | pass |

### `table.fill_empty_cells_from`

**NHANES: the 9 empty body mass index cells filled with the average of the person's age group** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| empty left | pandas fillna from the other table's matching row (set_index, reindex) | 0 | 0 | relative 1e-12 | pass |
| total | pandas fillna from the other table's matching row (set_index, reindex) | 667.347142857143 | 667.347142857143 | relative 1e-12 | pass |
| first person | pandas fillna from the other table's matching row (set_index, reindex) | 28.3714285714286 | 28.3714285714286 | relative 1e-12 | pass |
| sum of row x bmi | pandas fillna from the other table's matching row (set_index, reindex) | 8916.40428571428 | 8916.40428571428 | relative 1e-12 | pass |
| empty left | R | 0 | 0 | relative 1e-12 | pass |
| total | R | 667.347142857143 | 667.347142857143 | relative 1e-12 | pass |
| first person | R | 28.3714285714286 | 28.3714285714286 | relative 1e-12 | pass |
| sum of row x bmi | R | 8916.40428571428 | 8916.40428571428 | relative 1e-12 | pass |

**NHANES: the 9 empty body mass index cells filled with the average of the person's age group (a Polars table)** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| empty left | Polars join(how="left"), coalesce | 0 | 0 | relative 1e-12 | pass |
| total | Polars join(how="left"), coalesce | 667.347142857143 | 667.347142857143 | relative 1e-12 | pass |
| first person | Polars join(how="left"), coalesce | 28.3714285714286 | 28.3714285714286 | relative 1e-12 | pass |
| sum of row x bmi | Polars join(how="left"), coalesce | 8916.40428571428 | 8916.40428571428 | relative 1e-12 | pass |

### `table.find_summary_of show=`

**NHANES body mass index by age group: the first and last filled values, the biggest and the smallest** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| age group 1: first | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 20.4 | 20.4 | exact | pass |
| age group 1: biggest | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 35.3 | 35.3 | exact | pass |
| age group 1: smallest | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 20.4 | 20.4 | exact | pass |
| age group 1: last | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 27.5 | 27.5 | exact | pass |
| age group 2: first | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 22.7 | 22.7 | exact | pass |
| age group 2: biggest | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 28.7 | 28.7 | exact | pass |
| age group 2: smallest | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 22 | 22 | exact | pass |
| age group 2: last | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 27.4 | 27.4 | exact | pass |
| age group 3: first | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 21.7 | 21.7 | exact | pass |
| age group 3: biggest | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 27.2 | 27.2 | exact | pass |
| age group 3: smallest | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 21.7 | 21.7 | exact | pass |
| age group 3: last | pandas groupby().agg(["first", "max", "min", "last"]) (empty cells skipped) | 24.9 | 24.9 | exact | pass |
| age group 1: first | R | 20.4 | 20.4 | exact | pass |
| age group 1: biggest | R | 35.3 | 35.3 | exact | pass |
| age group 1: smallest | R | 20.4 | 20.4 | exact | pass |
| age group 1: last | R | 27.5 | 27.5 | exact | pass |
| age group 2: first | R | 22.7 | 22.7 | exact | pass |
| age group 2: biggest | R | 28.7 | 28.7 | exact | pass |
| age group 2: smallest | R | 22 | 22 | exact | pass |
| age group 2: last | R | 27.4 | 27.4 | exact | pass |
| age group 3: first | R | 21.7 | 21.7 | exact | pass |
| age group 3: biggest | R | 27.2 | 27.2 | exact | pass |
| age group 3: smallest | R | 21.7 | 21.7 | exact | pass |
| age group 3: last | R | 24.9 | 24.9 | exact | pass |

**NHANES body mass index by age group: the first and last filled values, the biggest and the smallest (a Polars table)** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| age group 1: first | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 20.4 | 20.4 | exact | pass |
| age group 1: biggest | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 35.3 | 35.3 | exact | pass |
| age group 1: smallest | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 20.4 | 20.4 | exact | pass |
| age group 1: last | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 27.5 | 27.5 | exact | pass |
| age group 2: first | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 22.7 | 22.7 | exact | pass |
| age group 2: biggest | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 28.7 | 28.7 | exact | pass |
| age group 2: smallest | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 22 | 22 | exact | pass |
| age group 2: last | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 27.4 | 27.4 | exact | pass |
| age group 3: first | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 21.7 | 21.7 | exact | pass |
| age group 3: biggest | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 27.2 | 27.2 | exact | pass |
| age group 3: smallest | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 21.7 | 21.7 | exact | pass |
| age group 3: last | Polars group_by().agg(drop_nulls().first(), max(), min(), last()) | 24.9 | 24.9 | exact | pass |

### `table.as_list`

**mtcars given back as a list of 32 rows, one dict for each car** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas to_dict("records") | 32 | 32 | exact | pass |
| keys in a row | pandas to_dict("records") | 12 | 12 | exact | pass |
| total hp | pandas to_dict("records") | 4694 | 4694 | exact | pass |
| total wt | pandas to_dict("records") | 102.952 | 102.952 | exact | pass |
| row 1: Mazda RX4 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 2: Mazda RX4 Wag | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 3: Datsun 710 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 4: Hornet 4 Drive | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 5: Hornet Sportabout | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 6: Valiant | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 7: Duster 360 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 8: Merc 240D | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 9: Merc 230 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 10: Merc 280 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 11: Merc 280C | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 12: Merc 450SE | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 13: Merc 450SL | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 14: Merc 450SLC | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 15: Cadillac Fleetwood | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 16: Lincoln Continental | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 17: Chrysler Imperial | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 18: Fiat 128 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 19: Honda Civic | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 20: Toyota Corolla | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 21: Toyota Corona | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 22: Dodge Challenger | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 23: AMC Javelin | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 24: Camaro Z28 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 25: Pontiac Firebird | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 26: Fiat X1-9 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 27: Porsche 914-2 | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 28: Lotus Europa | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 29: Ford Pantera L | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 30: Ferrari Dino | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 31: Maserati Bora | pandas to_dict("records") | 1 | 1 | exact | pass |
| row 32: Volvo 142E | pandas to_dict("records") | 1 | 1 | exact | pass |

**mtcars given back as a list of 32 rows, one dict for each car (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | Polars to_dicts() | 32 | 32 | exact | pass |
| keys in a row | Polars to_dicts() | 12 | 12 | exact | pass |
| total hp | Polars to_dicts() | 4694 | 4694 | exact | pass |
| total wt | Polars to_dicts() | 102.952 | 102.952 | exact | pass |
| row 1: Mazda RX4 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 2: Mazda RX4 Wag | Polars to_dicts() | 1 | 1 | exact | pass |
| row 3: Datsun 710 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 4: Hornet 4 Drive | Polars to_dicts() | 1 | 1 | exact | pass |
| row 5: Hornet Sportabout | Polars to_dicts() | 1 | 1 | exact | pass |
| row 6: Valiant | Polars to_dicts() | 1 | 1 | exact | pass |
| row 7: Duster 360 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 8: Merc 240D | Polars to_dicts() | 1 | 1 | exact | pass |
| row 9: Merc 230 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 10: Merc 280 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 11: Merc 280C | Polars to_dicts() | 1 | 1 | exact | pass |
| row 12: Merc 450SE | Polars to_dicts() | 1 | 1 | exact | pass |
| row 13: Merc 450SL | Polars to_dicts() | 1 | 1 | exact | pass |
| row 14: Merc 450SLC | Polars to_dicts() | 1 | 1 | exact | pass |
| row 15: Cadillac Fleetwood | Polars to_dicts() | 1 | 1 | exact | pass |
| row 16: Lincoln Continental | Polars to_dicts() | 1 | 1 | exact | pass |
| row 17: Chrysler Imperial | Polars to_dicts() | 1 | 1 | exact | pass |
| row 18: Fiat 128 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 19: Honda Civic | Polars to_dicts() | 1 | 1 | exact | pass |
| row 20: Toyota Corolla | Polars to_dicts() | 1 | 1 | exact | pass |
| row 21: Toyota Corona | Polars to_dicts() | 1 | 1 | exact | pass |
| row 22: Dodge Challenger | Polars to_dicts() | 1 | 1 | exact | pass |
| row 23: AMC Javelin | Polars to_dicts() | 1 | 1 | exact | pass |
| row 24: Camaro Z28 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 25: Pontiac Firebird | Polars to_dicts() | 1 | 1 | exact | pass |
| row 26: Fiat X1-9 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 27: Porsche 914-2 | Polars to_dicts() | 1 | 1 | exact | pass |
| row 28: Lotus Europa | Polars to_dicts() | 1 | 1 | exact | pass |
| row 29: Ford Pantera L | Polars to_dicts() | 1 | 1 | exact | pass |
| row 30: Ferrari Dino | Polars to_dicts() | 1 | 1 | exact | pass |
| row 31: Maserati Bora | Polars to_dicts() | 1 | 1 | exact | pass |
| row 32: Volvo 142E | Polars to_dicts() | 1 | 1 | exact | pass |

### `table.check_if_same_as`

**mtcars against itself, and against mtcars with the weights rounded to 1 decimal** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| same as itself | pandas equals | 1 | 1 | exact | pass |
| same after rounding wt | pandas equals | 0 | 0 | exact | pass |
| same as itself | R | 1 | 1 | exact | pass |
| same after rounding wt | R | 0 | 0 | exact | pass |

**mtcars against itself, and against mtcars with the weights rounded to 1 decimal (a Polars table)** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| same as itself | Polars equals | 1 | 1 | exact | pass |
| same after rounding wt | Polars equals | 0 | 0 | exact | pass |

### `table.show_duplicate_rows`

**iris: flower 143 repeats flower 102 exactly** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows that repeat | pandas duplicated(keep=False) | 2 | 2 | exact | pass |
| different rows | pandas duplicated(keep=False) | 1 | 1 | exact | pass |
| extra copies | pandas duplicated(keep=False) | 1 | 1 | exact | pass |
| rows that repeat | R | 2 | 2 | exact | pass |
| extra copies | R | 1 | 1 | exact | pass |
| different rows | R | 1 | 1 | exact | pass |

**iris: flower 143 repeats flower 102 exactly (a Polars table)** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows that repeat | Polars is_duplicated() | 2 | 2 | exact | pass |
| different rows | Polars is_duplicated() | 1 | 1 | exact | pass |
| extra copies | Polars is_duplicated() | 1 | 1 | exact | pass |

### `table.show_rows_with_empty_cells_in`

**NHANES: the people with at least one empty cell** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows with an empty cell | pandas isna().any(axis=1) | 12 | 12 | exact | pass |
| rows | pandas isna().any(axis=1) | 25 | 25 | exact | pass |
| rows with an empty cell | R | 12 | 12 | exact | pass |
| rows | R | 25 | 25 | exact | pass |

**NHANES: the people with at least one empty cell (a Polars table)** (real data; data: nhanes (mice))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows with an empty cell | Polars any_horizontal(is_null()) | 12 | 12 | exact | pass |
| rows | Polars any_horizontal(is_null()) | 25 | 25 | exact | pass |

### `table.count_rows with_totals=`

**warpbreaks: looms for each wool and tension, with the totals** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| columns | pandas crosstab(margins=True, margins_name="(total)") | 5 | 5 | exact | pass |
| A, L | pandas crosstab(margins=True, margins_name="(total)") | 9 | 9 | exact | pass |
| A, M | pandas crosstab(margins=True, margins_name="(total)") | 9 | 9 | exact | pass |
| A, H | pandas crosstab(margins=True, margins_name="(total)") | 9 | 9 | exact | pass |
| A, (total) | pandas crosstab(margins=True, margins_name="(total)") | 27 | 27 | exact | pass |
| B, L | pandas crosstab(margins=True, margins_name="(total)") | 9 | 9 | exact | pass |
| B, M | pandas crosstab(margins=True, margins_name="(total)") | 9 | 9 | exact | pass |
| B, H | pandas crosstab(margins=True, margins_name="(total)") | 9 | 9 | exact | pass |
| B, (total) | pandas crosstab(margins=True, margins_name="(total)") | 27 | 27 | exact | pass |
| (total), L | pandas crosstab(margins=True, margins_name="(total)") | 18 | 18 | exact | pass |
| (total), M | pandas crosstab(margins=True, margins_name="(total)") | 18 | 18 | exact | pass |
| (total), H | pandas crosstab(margins=True, margins_name="(total)") | 18 | 18 | exact | pass |
| (total), (total) | pandas crosstab(margins=True, margins_name="(total)") | 54 | 54 | exact | pass |
| A, H | R | 9 | 9 | exact | pass |
| A, L | R | 9 | 9 | exact | pass |
| A, M | R | 9 | 9 | exact | pass |
| A, (total) | R | 27 | 27 | exact | pass |
| B, H | R | 9 | 9 | exact | pass |
| B, L | R | 9 | 9 | exact | pass |
| B, M | R | 9 | 9 | exact | pass |
| B, (total) | R | 27 | 27 | exact | pass |
| (total), H | R | 18 | 18 | exact | pass |
| (total), L | R | 18 | 18 | exact | pass |
| (total), M | R | 18 | 18 | exact | pass |
| (total), (total) | R | 54 | 54 | exact | pass |

Note: R addmargins() names its totals "Sum"; simplydata and pandas (margins_name) call them "(total)". The R names are changed to "(total)" before the numbers are compared.

### `table.save in_table=`

**mtcars saved twice into an SQLite file (two tables) and read back** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas to_sql, read_sql_query (sqlite3) | 32 | 32 | relative 1e-12 | pass |
| columns | pandas to_sql, read_sql_query (sqlite3) | 12 | 12 | relative 1e-12 | pass |
| total hp | pandas to_sql, read_sql_query (sqlite3) | 4694 | 4694 | relative 1e-12 | pass |
| total wt | pandas to_sql, read_sql_query (sqlite3) | 102.952 | 102.952 | relative 1e-12 | pass |
| row 3 | pandas to_sql, read_sql_query (sqlite3) | 1 | 1 | relative 1e-12 | pass |

### `table.show_differences_from`

**mtcars with horsepower capped at 200, against mtcars** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| cells that differ | pandas compare | 7 | 7 | exact | pass |
| rows that differ | pandas compare | 7 | 7 | exact | pass |
| cells that differ | R | 7 | 7 | exact | pass |
| rows that differ | R | 7 | 7 | exact | pass |

### `get_numbers_drawn`

**Anscombe's first set: the drawn fitted line is the least-squares line** (published; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope of the drawn line | Anscombe (1973) | 0.500090909090909 | 0.5001 | within 0.0001 (printed rounding) | pass |
| dots drawn | Anscombe (1973) | 11 | 11 | within 0 (printed rounding) | pass |
| slope of the drawn line | statsmodels OLS | 0.500090909090909 | 0.500090909090909 | relative 1e-09 | pass |
| dots drawn | statsmodels OLS | 11 | 11 | relative 1e-09 | pass |

Note: The numbers come back from what matplotlib drew; Anscombe prints the slope 0.500 (0.5001).

### `table.repeat_each_row_by`

**Down syndrome cases in Michigan: one row per case** (real data; data: Down syndrome by birth order)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | pandas index.repeat | 2754 | 2754 | exact | pass |
| first birth order rows | pandas index.repeat | 412 | 412 | exact | pass |

### `table.show_rows_that_pull_model`

**stackloss: the rows with a Cook's distance above 4/n** (published; data: stackloss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first row | Daniel & Wood (1980): observation 21 is the most influential | 21 | 21 | within 0 (printed rounding) | pass |
| first row | R | 21 | 21 | relative 1e-09 | pass |
| its Cook's distance | R | 0.691999916339513 | 0.69199991633951 | relative 1e-09 | pass |
| rows found | R | 1 | 1 | relative 1e-09 | pass |

### `sdata.get_example from_r_package=`

**lung from R survival: the dataset as R ships it** (real data; data: lung with weight loss (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows | R | 228 | 228 | exact | pass |
| time of the first row | R | 306 | 306 | exact | pass |
| age of the first row | R | 74 | 74 | exact | pass |

### `table.check_model_of show="numbers"`

**show="numbers": mtcars mpg ~ wt + hp, the Breusch-Pagan test** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| BP | R | 0.880722470178803 | 0.880722470178814 | relative 1e-09 | pass |
| p | R | 0.643803814544345 | 0.643803814544341 | relative 1e-09 | pass |

### `table.find_correlation_between show="result table"`

**show="result table": mtcars mpg and wt** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| r | R | -0.867659376517228 | -0.867659376517228 | relative 1e-09 | pass |
| low | R | -0.933826413284994 | -0.933826413284994 | relative 1e-09 | pass |
| high | R | -0.744087196460113 | -0.744087196460113 | relative 1e-09 | pass |
| p | R | 1.29395870135051e-10 | 1.29395870135052e-10 | relative 1e-09 | pass |

### `table.find_correlation_between allowing_for=, show="result table"`

**allowing_for=, show="result table": mtcars mpg and wt, allowing for hp** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| partial r | residuals of statsmodels OLS, SciPy pearsonr (the definition) | -0.751204904961865 | -0.751204904961865 | relative 1e-09 | pass |
| t | residuals of statsmodels OLS, SciPy pearsonr (the definition) | -6.12869521981042 | -6.12869521981042 | relative 1e-09 | pass |
| p | residuals of statsmodels OLS, SciPy pearsonr (the definition) | 1.11964713620002e-06 | 1.11964713620003e-06 | relative 1e-09 | pass |
| rows | residuals of statsmodels OLS, SciPy pearsonr (the definition) | 32 | 32 | relative 1e-09 | pass |
| partial r | R | -0.751204904961865 | -0.751204904961865 | relative 1e-09 | pass |
| t | R | -6.12869521981042 | -6.12869521981042 | relative 1e-09 | pass |
| p | R | 1.11964713620002e-06 | 1.11964713620002e-06 | relative 1e-09 | pass |
| rows | R | 32 | 32 | relative 1e-09 | pass |

Note: simplydata gives back R ppcor's own numbers; the residual route is the definition, as a check.

### `trade_off_curve get_numbers_drawn()`

**aSAH, s100b for a poor outcome: the best cut-off from chart.get_numbers_drawn()** (real data; data: aSAH (pROC))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| best cut-off | R | 0.205 | 0.205 | relative 1e-12 | pass |
| sensitivity there | R | 0.634146341463415 | 0.634146341463415 | relative 1e-12 | pass |

Note: The cut-off written next to the marked dot is R pROC's coords("best", best.method = "youden") threshold, given back in the value column of get_numbers_drawn().

### `table.add_filtered_column both_ways=False`

**both_ways=False: the yearly sunspot numbers, a forward low-pass filter** (real data; data: yearly sunspot numbers)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | SciPy signal.butter and sosfilt | 0.002082996022033 | 0.002082996022033 | relative 1e-09 | pass |
| 1957 (position 258) | SciPy signal.butter and sosfilt | 80.1854664925231 | 80.1854664925231 | relative 1e-09 | pass |
| total | SciPy signal.butter and sosfilt | 14994.8382962056 | 14994.8382962056 | relative 1e-09 | pass |

### `system.table form="state space"`

**form="state space": 1 / (s^2 + 2 s + 5) in controller form** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| A row 1, column 1 | SciPy signal.tf2ss | -2 | -2 | relative 1e-12 | pass |
| A row 1, column 2 | SciPy signal.tf2ss | -5 | -5 | relative 1e-12 | pass |
| A row 2, column 1 | SciPy signal.tf2ss | 1 | 1 | relative 1e-12 | pass |
| C column 2 | SciPy signal.tf2ss | 1 | 1 | relative 1e-12 | pass |
| A row 1, column 1 | R | -2 | -2 | relative 1e-12 | pass |
| A row 1, column 2 | R | -5 | -5 | relative 1e-12 | pass |
| A row 2, column 1 | R | 1 | 1 | relative 1e-12 | pass |
| C column 2 | R | 1 | 1 | relative 1e-12 | pass |

### `system.chart show="step"`

**show="step": 1 / (s^2 + 2 s + 5), the step response drawn from 0 to 5** (real data; data: checks against R (no published example))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | python-control step_response | 200 | 200 | relative 1e-08 | pass |
| highest point | python-control step_response | 0.241560775010704 | 0.241560775010704 | relative 1e-08 | pass |
| last point | python-control step_response | 0.201497282439427 | 0.201497282439427 | relative 1e-08 | pass |
| points | R | 200 | 200 | relative 1e-08 | pass |
| highest point | R | 0.241560775010704 | 0.241560775010704 | relative 1e-08 | pass |
| last point | R | 0.201497282439427 | 0.201497282439427 | relative 1e-08 | pass |

## 2. The same underneath (the manual's boxes)

Each box's library code is run next to the simplydata word and compared. Table words run on a pandas and on a Polars table.

| word | compared with | table | how | tolerance | result |
|---|---|---|---|---|---|
| `draw_bars` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_histogram` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_dots` | seaborn | pandas | chart | relative 1e-09 | pass |
| `trade_off_curve` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `save` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `write_title_on_top` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `label_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `label_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `rotate_labels_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `write_caption_at_bottom` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `use_font_size` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `use_colour` | seaborn | pandas | chart | relative 1e-09 | pass |
| `use_colours` | seaborn | pandas | chart | relative 1e-09 | pass |
| `put_legend_at_bottom` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `order_x` | pandas | pandas | chart | relative 1e-09 | pass |
| `use_style` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `hide_legend` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `put_legend_on_left` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_lines` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_boxes` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_all_dots` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_violins` | seaborn | pandas | chart | relative 1e-09 | pass |
| `show=` | seaborn | pandas | chart | relative 1e-09 | pass |
| `error=` | seaborn | pandas | chart | relative 1e-09 | pass |
| `write_numbers_on_bars` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `fit_line` | SciPy | pandas | chart | relative 1e-09 | pass |
| `draw_qq_dots` | SciPy | pandas | chart | relative 1e-09 | pass |
| `set_range_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_line_at_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `shade_between_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `use_log_scale_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_line_at_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `write_ticks_y_as` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `set_size` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `write_note` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_heatmap` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_one_chart_for_each_group_in` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `sdata.put_side_by_side` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `sdata.put_one_above_other` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `sdata.put_in_rows_and_columns` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `sdata.draw_all_pairs` | seaborn | pandas | chart | relative 1e-09 | pass |
| `add_second_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `animate` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `fit_formula` | SciPy | pandas | chart | relative 1e-07 | pass |
| `show` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_area` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_pie` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_polar` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_contour` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_surface` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_dots_3d` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_band` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_map_of_empty_cells` | pandas | pandas | chart | relative 1e-09 | pass |
| `sticks` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_error_bars` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `fit_curve` | NumPy | pandas | chart | relative 1e-08 | pass |
| `fit_distribution` | SciPy | pandas | chart | relative 1e-09 | pass |
| `draw_curve` | SciPy | pandas | chart | relative 1e-09 | pass |
| `draw_density` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_count_bars` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_side_histograms` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_cumulative_share` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_line_with_slope` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `shade_between_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `write_names_on_dots` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `use_font` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `set_range_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `use_log_scale_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `put_ticks_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `put_ticks_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `rotate_labels_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `write_ticks_x_as` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `flip_x` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `flip_y` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `use_colour_scale` | seaborn | pandas | chart | relative 1e-09 | pass |
| `show_grid` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `hide_grid` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `put_legend_at_top` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `put_legend_on_right` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `show_legend` | seaborn | pandas | chart | relative 1e-09 | pass |
| `label_legend` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `label_colour_bar` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `order_y` | pandas | pandas | chart | relative 1e-09 | pass |
| `order_legend` | pandas | pandas | chart | relative 1e-09 | pass |
| `add_zoom_box` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `forest_plot` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.keep_rows_where` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_where` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_where` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_rows_where` | Polars | polars | table | relative 1e-09 | pass |
| `table.find_average_of` | pandas | pandas | table | relative 1e-09 | pass |
| `table.find_average_of` | Polars | pandas | table | relative 1e-09 | pass |
| `table.find_average_of` | pandas | polars | table | relative 1e-09 | pass |
| `table.find_average_of` | Polars | polars | table | relative 1e-09 | pass |
| `table.show_first_rows` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.show_first_rows` | pandas | polars | printed | relative 1e-09 | pass |
| `table.describe_columns` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.describe_columns` | pandas | polars | printed | relative 1e-09 | pass |
| `table.keep_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_columns` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_columns` | Polars | polars | table | relative 1e-09 | pass |
| `table.rename_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.rename_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.rename_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.rename_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.sort_by` | pandas | pandas | table | relative 1e-09 | pass |
| `table.sort_by` | Polars | pandas | table | relative 1e-09 | pass |
| `table.sort_by` | pandas | polars | table | relative 1e-09 | pass |
| `table.sort_by` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_rows_by_position` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_by_position` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_by_position` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_rows_by_position` | Polars | polars | table | relative 1e-09 | pass |
| `table.fill_empty_cells_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.fill_empty_cells_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.fill_empty_cells_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.fill_empty_cells_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.turn_into_numbers` | pandas | pandas | table | relative 1e-09 | pass |
| `table.turn_into_numbers` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_group_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_group_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_group_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_group_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.find_summary_of` | pandas | pandas | table | relative 1e-09 | pass |
| `table.find_summary_of` | Polars | pandas | table | relative 1e-09 | pass |
| `table.find_summary_of` | pandas | polars | table | relative 1e-09 | pass |
| `table.find_summary_of` | Polars | polars | table | relative 1e-09 | pass |
| `table.join_with` | pandas | pandas | table | relative 1e-09 | pass |
| `table.join_with` | Polars | pandas | table | relative 1e-09 | pass |
| `table.join_with` | pandas | polars | table | relative 1e-09 | pass |
| `table.join_with` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_z_score_column` | pandas | pandas | table | relative 1e-12 | pass |
| `table.add_z_score_column` | Polars | pandas | table | relative 1e-12 | pass |
| `table.add_z_score_column` | pandas | polars | table | relative 1e-12 | pass |
| `table.add_z_score_column` | Polars | polars | table | relative 1e-12 | pass |
| `table.undo` | - | - | none | relative 0 | pass |
| `table.show_steps` | - | - | none | relative 0 | pass |
| `table.save` | pandas | pandas | table | relative 1e-09 | pass |
| `table.save` | Polars | pandas | table | relative 1e-09 | pass |
| `table.save` | pandas | polars | table | relative 1e-09 | pass |
| `table.save` | Polars | polars | table | relative 1e-09 | pass |
| `table.save in_sheet=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.save in_sheet=` | pandas | polars | table | relative 1e-09 | pass |
| `table.as_pandas` | Polars | pandas | table | relative 1e-09 | pass |
| `table.as_pandas` | Polars | polars | table | relative 1e-09 | pass |
| `table.make_copy` | pandas | pandas | table | relative 1e-09 | pass |
| `table.make_copy` | Polars | pandas | table | relative 1e-09 | pass |
| `table.make_copy` | pandas | polars | table | relative 1e-09 | pass |
| `table.make_copy` | Polars | polars | table | relative 1e-09 | pass |
| `table.as_polars` | pandas | pandas | table | relative 1e-09 | pass |
| `table.as_polars` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_extra_spaces_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_extra_spaces_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_extra_spaces_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_extra_spaces_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.replace_values_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.replace_values_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.replace_values_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.replace_values_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_missing_dates` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_missing_dates` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_missing_dates` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_missing_dates` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_rolling_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_rolling_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_rolling_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_rolling_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.show_rows_with_outliers` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.show_rows_with_outliers` | pandas | polars | printed | relative 1e-09 | pass |
| `table.show_last_rows` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.show_last_rows` | pandas | polars | printed | relative 1e-09 | pass |
| `table.show` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.show` | pandas | polars | printed | relative 1e-09 | pass |
| `table.get_column_names` | pandas | pandas | value | relative 0 | pass |
| `table.get_column_names` | Polars | pandas | value | relative 0 | pass |
| `table.get_column_names` | pandas | polars | value | relative 0 | pass |
| `table.get_column_names` | Polars | polars | value | relative 0 | pass |
| `table.get_column` | pandas | pandas | value | relative 0 | pass |
| `table.get_column` | Polars | pandas | value | relative 0 | pass |
| `table.get_column` | pandas | polars | value | relative 0 | pass |
| `table.get_column` | Polars | polars | value | relative 0 | pass |
| `table.get_row` | pandas | pandas | value | relative 0 | pass |
| `table.get_row` | Polars | pandas | value | relative 0 | pass |
| `table.get_row` | pandas | polars | value | relative 0 | pass |
| `table.get_row` | Polars | polars | value | relative 0 | pass |
| `table.get_cell_at` | pandas | pandas | value | relative 0 | pass |
| `table.get_cell_at` | Polars | pandas | value | relative 0 | pass |
| `table.get_cell_at` | pandas | polars | value | relative 0 | pass |
| `table.get_cell_at` | Polars | polars | value | relative 0 | pass |
| `table.remove_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_columns` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_columns` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_columns_by_position` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_columns_by_position` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_columns_by_position` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_columns_by_position` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_columns_by_position` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_columns_by_position` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_columns_by_position` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_columns_by_position` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_rows_where` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_where` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_where` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_rows_where` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_first_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_first_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_first_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_first_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_last_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_last_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_last_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_last_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_rows_by_position` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_by_position` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_by_position` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_rows_by_position` | Polars | polars | table | relative 1e-09 | pass |
| `table.reverse_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.reverse_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.reverse_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.reverse_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_duplicate_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_duplicate_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_duplicate_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_duplicate_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_biggest_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_biggest_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_biggest_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_biggest_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_smallest_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_smallest_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_smallest_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_smallest_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_rows_with_outliers` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_with_outliers` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_with_outliers` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_rows_with_outliers` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_rows_with_empty_cells_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_with_empty_cells_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_with_empty_cells_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_rows_with_empty_cells_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_is_empty_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_is_empty_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_is_empty_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_is_empty_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.turn_into_text` | pandas | pandas | table | relative 1e-09 | pass |
| `table.turn_into_text` | Polars | pandas | table | relative 1e-09 | pass |
| `table.turn_into_text` | pandas | polars | table | relative 1e-09 | pass |
| `table.turn_into_text` | Polars | polars | table | relative 1e-09 | pass |
| `table.turn_into_dates` | pandas | pandas | table | relative 1e-09 | pass |
| `table.turn_into_dates` | Polars | pandas | table | relative 1e-09 | pass |
| `table.turn_into_dates` | pandas | polars | table | relative 1e-09 | pass |
| `table.turn_into_dates` | Polars | polars | table | relative 1e-09 | pass |
| `table.turn_into_lowercase` | pandas | pandas | table | relative 1e-09 | pass |
| `table.turn_into_lowercase` | Polars | pandas | table | relative 1e-09 | pass |
| `table.turn_into_lowercase` | pandas | polars | table | relative 1e-09 | pass |
| `table.turn_into_lowercase` | Polars | polars | table | relative 1e-09 | pass |
| `table.turn_into_uppercase` | pandas | pandas | table | relative 1e-09 | pass |
| `table.turn_into_uppercase` | Polars | pandas | table | relative 1e-09 | pass |
| `table.turn_into_uppercase` | pandas | polars | table | relative 1e-09 | pass |
| `table.turn_into_uppercase` | Polars | polars | table | relative 1e-09 | pass |
| `table.round_numbers_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.round_numbers_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.round_numbers_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.round_numbers_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.change_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.change_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.change_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.change_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_rank_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_rank_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_rank_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_rank_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_date` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_date` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_date` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_date` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_text` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_text` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_text` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_column_with_part_of_text` | Polars | polars | table | relative 1e-09 | pass |
| `table.split_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.split_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.split_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.split_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.replace_text_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.replace_text_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.replace_text_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.replace_text_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_previous_value_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_previous_value_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_previous_value_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_previous_value_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_change_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_change_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_change_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_change_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.find_smallest_of` | pandas | pandas | table | relative 1e-09 | pass |
| `table.find_smallest_of` | Polars | pandas | table | relative 1e-09 | pass |
| `table.find_smallest_of` | pandas | polars | table | relative 1e-09 | pass |
| `table.find_smallest_of` | Polars | polars | table | relative 1e-09 | pass |
| `table.find_biggest_of` | pandas | pandas | value | relative 0 | pass |
| `table.find_biggest_of` | Polars | pandas | value | relative 0 | pass |
| `table.find_biggest_of` | pandas | polars | value | relative 0 | pass |
| `table.find_biggest_of` | Polars | polars | value | relative 0 | pass |
| `table.find_standard_deviation_of` | pandas | pandas | table | relative 1e-12 | pass |
| `table.find_standard_deviation_of` | Polars | pandas | table | relative 1e-12 | pass |
| `table.find_standard_deviation_of` | pandas | polars | table | relative 1e-12 | pass |
| `table.find_standard_deviation_of` | Polars | polars | table | relative 1e-12 | pass |
| `table.count_different_values_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.count_different_values_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.count_different_values_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.count_different_values_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.find_most_common_of` | pandas | pandas | value | relative 0 | pass |
| `table.find_most_common_of` | Polars | pandas | value | relative 0 | pass |
| `table.find_most_common_of` | pandas | polars | value | relative 0 | pass |
| `table.find_most_common_of` | Polars | polars | value | relative 0 | pass |
| `table.find_interval_of` | SciPy | pandas | table | relative 1e-12 | pass |
| `table.find_interval_of` | SciPy | polars | table | relative 1e-12 | pass |
| `table.add_rows_from` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_rows_from` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_rows_from` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_rows_from` | Polars | polars | table | relative 1e-09 | pass |
| `table.gather_into_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.gather_into_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.gather_into_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.gather_into_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.spread_into_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.spread_into_columns` | Polars | pandas | table | relative 1e-09 | pass |
| `table.spread_into_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.spread_into_columns` | Polars | polars | table | relative 1e-09 | pass |
| `table.swap_rows_and_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.swap_rows_and_columns` | Polars | pandas | table | relative 1e-09 | pass |
| `table.swap_rows_and_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.swap_rows_and_columns` | Polars | polars | table | relative 1e-09 | pass |
| `table.start_again` | - | - | none | relative 0 | pass |
| `table.keep_rows_found_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_found_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_found_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_rows_found_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_rows_found_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_found_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_found_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_rows_found_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.clean_column_names` | pandas | pandas | table | relative 1e-09 | pass |
| `table.clean_column_names` | Polars | pandas | table | relative 1e-09 | pass |
| `table.clean_column_names` | pandas | polars | table | relative 1e-09 | pass |
| `table.clean_column_names` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_rows_that_are_all_empty` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_that_are_all_empty` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_rows_that_are_all_empty` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_rows_that_are_all_empty` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_columns_that_are_all_empty` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_columns_that_are_all_empty` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_columns_that_are_all_empty` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_columns_that_are_all_empty` | Polars | polars | table | relative 1e-09 | pass |
| `table.show_duplicate_rows` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.show_duplicate_rows` | Polars | pandas | printed | relative 1e-09 | pass |
| `table.show_duplicate_rows` | pandas | polars | printed | relative 1e-09 | pass |
| `table.show_duplicate_rows` | Polars | polars | printed | relative 1e-09 | pass |
| `table.add_row_summary_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_row_summary_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_row_summary_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_row_summary_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.turn_into_categories` | pandas | pandas | table | relative 1e-09 | pass |
| `table.turn_into_categories` | Polars | pandas | table | relative 1e-09 | pass |
| `table.turn_into_categories` | pandas | polars | table | relative 1e-09 | pass |
| `table.turn_into_categories` | Polars | polars | table | relative 1e-09 | pass |
| `table.split_into_rows` | pandas | pandas | table | relative 1e-09 | pass |
| `table.split_into_rows` | Polars | pandas | table | relative 1e-09 | pass |
| `table.split_into_rows` | pandas | polars | table | relative 1e-09 | pass |
| `table.split_into_rows` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_running_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_running_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_running_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_running_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_row_number_column` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_row_number_column` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_row_number_column` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_row_number_column` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_groups_where` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_groups_where` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_groups_where` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_groups_where` | Polars | polars | table | relative 1e-09 | pass |
| `table.remove_groups_where` | pandas | pandas | table | relative 1e-09 | pass |
| `table.remove_groups_where` | Polars | pandas | table | relative 1e-09 | pass |
| `table.remove_groups_where` | pandas | polars | table | relative 1e-09 | pass |
| `table.remove_groups_where` | Polars | polars | table | relative 1e-09 | pass |
| `table.join_with using=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.join_with using=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.join_with using=` | pandas | polars | table | relative 1e-09 | pass |
| `table.join_with using=` | Polars | polars | table | relative 1e-09 | pass |
| `table.spread_into_columns show=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.spread_into_columns show=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.spread_into_columns show=` | pandas | polars | table | relative 1e-09 | pass |
| `table.spread_into_columns show=` | Polars | polars | table | relative 1e-09 | pass |
| `table.change_column in_rows_where=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.change_column in_rows_where=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.change_column in_rows_where=` | pandas | polars | table | relative 1e-09 | pass |
| `table.change_column in_rows_where=` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_first_rows for_each_group_in=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_first_rows for_each_group_in=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_first_rows for_each_group_in=` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_first_rows for_each_group_in=` | Polars | polars | table | relative 1e-09 | pass |
| `table.count_columns` | pandas | pandas | value | relative 1e-09 | pass |
| `table.count_columns` | Polars | pandas | value | relative 1e-09 | pass |
| `table.count_columns` | pandas | polars | value | relative 1e-09 | pass |
| `table.count_columns` | Polars | polars | value | relative 1e-09 | pass |
| `table.rename_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.rename_columns` | Polars | pandas | table | relative 1e-09 | pass |
| `table.rename_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.rename_columns` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_missing_combinations_of` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_missing_combinations_of` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_missing_combinations_of` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_missing_combinations_of` | Polars | polars | table | relative 1e-09 | pass |
| `table.round_dates_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.round_dates_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.round_dates_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.round_dates_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.change_time_zone_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.change_time_zone_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.change_time_zone_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.change_time_zone_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.spread_into_yes_no_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.spread_into_yes_no_columns` | Polars | pandas | table | relative 1e-09 | pass |
| `table.spread_into_yes_no_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.spread_into_yes_no_columns` | Polars | polars | table | relative 1e-09 | pass |
| `table.fill_empty_cells_from` | pandas | pandas | table | relative 1e-09 | pass |
| `table.fill_empty_cells_from` | Polars | pandas | table | relative 1e-09 | pass |
| `table.fill_empty_cells_from` | pandas | polars | table | relative 1e-09 | pass |
| `table.fill_empty_cells_from` | Polars | polars | table | relative 1e-09 | pass |
| `table.keep_rows_where capitals_matter=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_where capitals_matter=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_where capitals_matter=` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_rows_where capitals_matter=` | Polars | polars | table | relative 1e-09 | pass |
| `table.count_rows with_totals=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.count_rows with_totals=` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_rank_column when_tied=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_rank_column when_tied=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_rank_column when_tied=` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_rank_column when_tied=` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_group_column into_equal_groups=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_group_column into_equal_groups=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_group_column into_equal_groups=` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_group_column into_equal_groups=` | Polars | polars | table | relative 1e-09 | pass |
| `table.turn_into_text written_like=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.turn_into_text written_like=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.turn_into_text written_like=` | pandas | polars | table | relative 1e-09 | pass |
| `table.turn_into_text written_like=` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_column counted_in=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_column counted_in=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_column counted_in=` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_column counted_in=` | Polars | polars | table | relative 1e-09 | pass |
| `table.round_dates_in to_the=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.round_dates_in to_the=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.round_dates_in to_the=` | pandas | polars | table | relative 1e-09 | pass |
| `table.round_dates_in to_the=` | Polars | polars | table | relative 1e-09 | pass |
| `table.add_zeros_in_front_of` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_zeros_in_front_of` | Polars | pandas | table | relative 1e-09 | pass |
| `table.add_zeros_in_front_of` | pandas | polars | table | relative 1e-09 | pass |
| `table.add_zeros_in_front_of` | Polars | polars | table | relative 1e-09 | pass |
| `table.move_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.move_columns` | Polars | pandas | table | relative 1e-09 | pass |
| `table.move_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.move_columns` | Polars | polars | table | relative 1e-09 | pass |
| `table.show_rows_with_empty_cells_in` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.show_rows_with_empty_cells_in` | Polars | pandas | printed | relative 1e-09 | pass |
| `table.show_rows_with_empty_cells_in` | pandas | polars | printed | relative 1e-09 | pass |
| `table.show_rows_with_empty_cells_in` | Polars | polars | printed | relative 1e-09 | pass |
| `table.show_differences_from` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.show_differences_from` | pandas | polars | printed | relative 1e-09 | pass |
| `table.check_if_same_as` | pandas | pandas | value | relative 1e-09 | pass |
| `table.check_if_same_as` | Polars | pandas | value | relative 1e-09 | pass |
| `table.check_if_same_as` | pandas | polars | value | relative 1e-09 | pass |
| `table.check_if_same_as` | Polars | polars | value | relative 1e-09 | pass |
| `table.run_sql` | DuckDB | pandas | table | relative 1e-09 | pass |
| `table.run_sql` | DuckDB | polars | table | relative 1e-09 | pass |
| `sdata.run_sql` | DuckDB | pandas | table | relative 1e-09 | pass |
| `table.make_one_table_for_each_group_in` | pandas | pandas | table | relative 1e-09 | pass |
| `table.make_one_table_for_each_group_in` | Polars | pandas | table | relative 1e-09 | pass |
| `table.make_one_table_for_each_group_in` | pandas | polars | table | relative 1e-09 | pass |
| `table.make_one_table_for_each_group_in` | Polars | polars | table | relative 1e-09 | pass |
| `table.as_list` | pandas | pandas | value | relative 1e-09 | pass |
| `table.as_list` | Polars | pandas | value | relative 1e-09 | pass |
| `table.as_list` | pandas | polars | value | relative 1e-09 | pass |
| `table.as_list` | Polars | polars | value | relative 1e-09 | pass |
| `table.find_summary_of show=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.find_summary_of show=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.find_summary_of show=` | pandas | polars | table | relative 1e-09 | pass |
| `table.find_summary_of show=` | Polars | polars | table | relative 1e-09 | pass |
| `table.sort_by biggest_first=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.sort_by biggest_first=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.sort_by biggest_first=` | pandas | polars | table | relative 1e-09 | pass |
| `table.sort_by biggest_first=` | Polars | polars | table | relative 1e-09 | pass |
| `table.gather_into_rows starts_with=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.gather_into_rows starts_with=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.gather_into_rows starts_with=` | pandas | polars | table | relative 1e-09 | pass |
| `table.gather_into_rows starts_with=` | Polars | polars | table | relative 1e-09 | pass |
| `table.join_with match=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.join_with match=` | Polars | pandas | table | relative 1e-09 | pass |
| `table.join_with match=` | pandas | polars | table | relative 1e-09 | pass |
| `table.join_with match=` | Polars | polars | table | relative 1e-09 | pass |
| `table.join_with keep="every combination"` | pandas | pandas | table | relative 1e-09 | pass |
| `table.join_with keep="every combination"` | Polars | pandas | table | relative 1e-09 | pass |
| `table.join_with keep="every combination"` | pandas | polars | table | relative 1e-09 | pass |
| `table.join_with keep="every combination"` | Polars | polars | table | relative 1e-09 | pass |
| `table.save in_table=` | pandas | pandas | table | relative 1e-09 | pass |
| `table.save in_table=` | pandas | polars | table | relative 1e-09 | pass |
| `nums.find_median` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.find_average` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.find_percentile` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.keep_each_number_that` | NumPy | pandas | value | relative 0 | pass |
| `nums.show` | NumPy | pandas | printed | relative 1e-09 | pass |
| `nums.show_first_numbers` | NumPy | pandas | printed | relative 1e-09 | pass |
| `nums.show_last_numbers` | NumPy | pandas | printed | relative 1e-09 | pass |
| `nums.get_number_at` | NumPy | pandas | value | relative 0 | pass |
| `nums.count` | NumPy | pandas | value | relative 0 | pass |
| `nums.count_empty_numbers` | NumPy | pandas | value | relative 0 | pass |
| `nums.add` | NumPy | pandas | value | relative 0 | pass |
| `nums.subtract` | NumPy | pandas | value | relative 0 | pass |
| `nums.times` | NumPy | pandas | value | relative 0 | pass |
| `nums.divide_by` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.raise_to_power` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.take_square_root` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.take_absolute_value` | NumPy | pandas | value | relative 0 | pass |
| `nums.round_to` | NumPy | pandas | value | relative 0 | pass |
| `nums.take_log` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.take_exp` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.turn_into_running_total` | NumPy | pandas | value | relative 0 | pass |
| `nums.remove_each_number_that` | NumPy | pandas | value | relative 0 | pass |
| `nums.keep_first_numbers` | NumPy | pandas | value | relative 0 | pass |
| `nums.keep_last_numbers` | NumPy | pandas | value | relative 0 | pass |
| `nums.keep_random_numbers` | NumPy | pandas | value | relative 0 | pass |
| `nums.remove_duplicate_numbers` | pandas | pandas | value | relative 0 | pass |
| `nums.remove_empty_numbers` | NumPy | pandas | value | relative 0 | pass |
| `nums.keep_numbers_by_position` | NumPy | pandas | value | relative 0 | pass |
| `nums.remove_numbers_by_position` | NumPy | pandas | value | relative 0 | pass |
| `nums.replace_each_number_that` | NumPy | pandas | value | relative 0 | pass |
| `nums.fill_empty_numbers` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.fill_empty_numbers` | pandas | pandas | value | relative 1e-12 | pass |
| `nums.sort` | NumPy | pandas | value | relative 0 | pass |
| `nums.reverse` | NumPy | pandas | value | relative 0 | pass |
| `nums.find_total` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.find_smallest` | NumPy | pandas | value | relative 0 | pass |
| `nums.find_biggest` | NumPy | pandas | value | relative 0 | pass |
| `nums.find_standard_deviation` | NumPy | pandas | value | relative 1e-12 | pass |
| `nums.count_each` | pandas | pandas | table | relative 1e-09 | pass |
| `nums.make_number_grid` | NumPy | pandas | value | relative 0 | pass |
| `grid.count_rows` | NumPy | pandas | value | relative 0 | pass |
| `grid.count_columns` | NumPy | pandas | value | relative 0 | pass |
| `grid.find_shape` | NumPy | pandas | value | relative 0 | pass |
| `grid.show_first_rows` | NumPy | pandas | printed | relative 1e-09 | pass |
| `grid.show_last_rows` | NumPy | pandas | printed | relative 1e-09 | pass |
| `grid.get_number_at` | NumPy | pandas | value | relative 0 | pass |
| `grid.get_row` | NumPy | pandas | value | relative 0 | pass |
| `grid.get_column` | NumPy | pandas | value | relative 0 | pass |
| `grid.get_all_numbers` | NumPy | pandas | value | relative 0 | pass |
| `grid.keep_rows_by_position` | NumPy | pandas | value | relative 0 | pass |
| `grid.keep_columns_by_position` | NumPy | pandas | value | relative 0 | pass |
| `grid.remove_rows_by_position` | NumPy | pandas | value | relative 0 | pass |
| `grid.remove_columns_by_position` | NumPy | pandas | value | relative 0 | pass |
| `grid.replace_each_number_that` | NumPy | pandas | value | relative 0 | pass |
| `grid.swap_rows_and_columns` | NumPy | pandas | value | relative 0 | pass |
| `nums.undo` | - | - | none | relative 0 | pass |
| `nums.show_steps` | - | - | none | relative 0 | pass |
| `nums.start_again` | - | - | none | relative 0 | pass |
| `nums.turn_into_table` | pandas | pandas | table | relative 1e-09 | pass |
| `nums.start_chart` | seaborn | pandas | chart | relative 1e-09 | pass |
| `nums.save` | pandas | pandas | table | relative 1e-09 | pass |
| `nums.as_numpy` | NumPy | pandas | value | relative 0 | pass |
| `table.compare_averages_of` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.fit_line` | SciPy | polars | result | relative 1e-09 | pass |
| `dist.find_chance_that_value` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.find_percentile` | SciPy | pandas | value | relative 1e-12 | pass |
| `table.compare_spreads_of` | SciPy | pandas | result | relative 1e-10 | pass |
| `table.compare_spreads_of` | SciPy | polars | result | relative 1e-10 | pass |
| `table.compare_percent_to` | SciPy | pandas | result | relative 1e-10 | pass |
| `table.compare_percent_to` | SciPy | polars | result | relative 1e-10 | pass |
| `table.add_principal_components` | statsmodels | pandas | table | relative 1e-09 | pass |
| `table.add_principal_components` | statsmodels | polars | table | relative 1e-09 | pass |
| `table.add_predicted_column` | statsmodels | pandas | table | relative 1e-09 | pass |
| `table.add_predicted_column` | statsmodels | polars | table | relative 1e-09 | pass |
| `table.find_trend_of` | R + SciPy | pandas | result | relative 1e-09 | pass |
| `table.find_trend_of` | R + SciPy | polars | result | relative 1e-09 | pass |
| `table.find_each_peak_that` | SciPy | pandas | table | relative 1e-09 | pass |
| `table.find_each_peak_that` | SciPy | polars | table | relative 1e-09 | pass |
| `table.add_nmds` | R + pandas | pandas | table | relative 1e-09 | pass |
| `table.add_nmds` | R + pandas | polars | table | relative 1e-09 | pass |
| `table.fit_formula` | SciPy | pandas | result | relative 1e-07 | pass |
| `table.fit_formula` | SciPy | polars | result | relative 1e-07 | pass |
| `table.compare_matched_columns` | R + SciPy | pandas | result | relative 1e-09 | pass |
| `table.compare_matched_columns` | R + SciPy | polars | result | relative 1e-09 | pass |
| `table.compare_counts_to` | SciPy | pandas | result | relative 1e-10 | pass |
| `table.compare_counts_to` | SciPy | polars | result | relative 1e-10 | pass |
| `table.compare_shapes_of` | SciPy | pandas | result | relative 1e-12 | pass |
| `table.compare_shapes_of` | SciPy | polars | result | relative 1e-12 | pass |
| `table.compare_shapes_of two groups` | R + SciPy | pandas | result | relative 1e-09 | pass |
| `table.compare_shapes_of two groups` | R + SciPy | polars | result | relative 1e-09 | pass |
| `table.check_if_random_order` | statsmodels | pandas | result | relative 1e-12 | pass |
| `table.check_if_random_order` | statsmodels | polars | result | relative 1e-12 | pass |
| `table.compare_correlations` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_correlations` | R + Python | polars | result | relative 1e-09 | pass |
| `sdata.compare_averages` | R + SciPy | pandas | result | relative 1e-09 | pass |
| `sdata.compare_counts` | SciPy | pandas | result | relative 1e-10 | pass |
| `sdata.compare_risks` | statsmodels | pandas | result | relative 1e-10 | pass |
| `sdata.compare_rates` | R + statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_to_truth` | statsmodels | pandas | result | relative 1e-10 | pass |
| `table.compare_to_truth` | statsmodels | polars | result | relative 1e-10 | pass |
| `table.compare_to_truth a column of numbers` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_to_truth a column of numbers` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_accuracy` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_accuracy` | R + Python | polars | result | relative 1e-09 | pass |
| `sdata.compare_to_truth` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.agreement_between` | statsmodels | pandas | result | relative 1e-10 | pass |
| `table.agreement_between` | statsmodels | polars | result | relative 1e-10 | pass |
| `table.agreement_between columns of numbers` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.agreement_between columns of numbers` | R + Python | polars | result | relative 1e-09 | pass |
| `table.limits_of_agreement` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.limits_of_agreement` | R + Python | polars | result | relative 1e-09 | pass |
| `table.reliability_of` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.reliability_of` | R + Python | polars | result | relative 1e-09 | pass |
| `difference_dots` | R + statsmodels | pandas | chart | relative 1e-09 | pass |
| `sdata.find_where_smallest` | SciPy | pandas | result | relative 1e-12 | pass |
| `sdata.find_where_biggest` | SciPy | pandas | result | relative 1e-12 | pass |
| `sdata.solve` | SciPy | pandas | table | relative 1e-12 | pass |
| `table.values_at` | pandas | pandas | table | relative 1e-12 | pass |
| `table.values_at` | pandas | polars | table | relative 1e-12 | pass |
| `table.make_map_of` | SciPy | pandas | table | relative 1e-12 | pass |
| `table.make_map_of` | SciPy | polars | table | relative 1e-12 | pass |
| `table.compare_distributions_for` | SciPy | pandas | result | relative 1e-07 | pass |
| `table.compare_distributions_for` | SciPy | polars | result | relative 1e-07 | pass |
| `nums.fit_distribution` | SciPy | pandas | result | relative 1e-10 | pass |
| `dist.find_density_at` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.find_cut_off` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.find_middle_range` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.find_average` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.find_median` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.find_standard_deviation` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.find_variance` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.show_summary` | SciPy | pandas | result | relative 1e-12 | pass |
| `dist.make_random_numbers` | SciPy | pandas | value | relative 1e-12 | pass |
| `dist.draw_chart` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `dist.turn_into_table` | pandas | pandas | table | relative 1e-12 | pass |
| `dist.show_parameters` | - | - | none | relative 0 | pass |
| `table.find_principal_components_of` | statsmodels | pandas | table | relative 1e-09 | pass |
| `table.find_principal_components_of` | statsmodels | polars | table | relative 1e-09 | pass |
| `table.use_survey_design` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.use_survey_design` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain weights=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain weights=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.explain outcome="yes or no (overdispersed)"` | statsmodels | pandas | result | relative 1e-08 | pass |
| `table.explain outcome="yes or no (overdispersed)"` | statsmodels | polars | result | relative 1e-08 | pass |
| `table.explain matched_by=` | statsmodels | pandas | result | relative 1e-06 | pass |
| `table.explain matched_by=` | statsmodels | polars | result | relative 1e-06 | pass |
| `table.explain show="risk ratios"` | statsmodels | pandas | result | relative 1e-06 | pass |
| `table.explain show="risk ratios"` | statsmodels | polars | result | relative 1e-06 | pass |
| `table.explain test_method="log-binomial"` | statsmodels | pandas | result | relative 1e-06 | pass |
| `table.explain test_method="log-binomial"` | statsmodels | polars | result | relative 1e-06 | pass |
| `table.explain giving_outliers_less_weight=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain giving_outliers_less_weight=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.explain with_knots=` | patsy and statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain with_knots=` | patsy and statsmodels | polars | result | relative 1e-09 | pass |
| `table.explain show="standardised effects"` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain show="standardised effects"` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.explain interval_by="bootstrap"` | SciPy and statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain interval_by="bootstrap"` | SciPy and statsmodels | polars | result | relative 1e-09 | pass |
| `table.explain interval_by="profile"` | R + Python | pandas | result | relative 1e-07 | pass |
| `table.explain interval_by="profile"` | R + Python | polars | result | relative 1e-07 | pass |
| `table.explain p_value_by="likelihood ratio"` | statsmodels and SciPy | pandas | result | relative 1e-08 | pass |
| `table.explain p_value_by="likelihood ratio"` | statsmodels and SciPy | polars | result | relative 1e-08 | pass |
| `table.explain crossed_with=` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.explain crossed_with=` | R + Python | polars | result | relative 1e-06 | pass |
| `table.explain outcome="counts with many zeros that vary a lot"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain outcome="counts with many zeros that vary a lot"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain outcome="counts in two steps"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain outcome="counts in two steps"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain zero_part_using=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain zero_part_using=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_dose_response` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_dose_response` | R + Python | polars | result | relative 1e-09 | pass |
| `fit_dose_response` | R + matplotlib | pandas | chart | relative 1e-06 | pass |
| `table.find_best_power_of` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.find_best_power_of` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line test_method="theil-sen"` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.fit_line test_method="theil-sen"` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line test_method="standardised major axis"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line test_method="standardised major axis"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line test_method="deming", y_error_over_x_error=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line test_method="deming", y_error_over_x_error=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line test_method="passing-bablok"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line test_method="passing-bablok"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line with_bends=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line with_bends=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line changes_at=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.fit_line changes_at=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.fit_curve of_kind="logistic growth"` | SciPy | pandas | result | relative 1e-06 | pass |
| `table.fit_curve of_kind="logistic growth"` | SciPy | polars | result | relative 1e-06 | pass |
| `table.explain for_percentile=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain for_percentile=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain changes_at=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain changes_at=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.add_smoothed_column test_method="loess", interval=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.add_smoothed_column test_method="loess", interval=` | R + Python | polars | result | relative 1e-09 | pass |
| `draw_smooth_line test_method="loess", with_confidence_band=` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.find_columns_that_predict` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_columns_that_predict` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_group_levels_of` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_group_levels_of` | R + Python | polars | result | relative 1e-06 | pass |
| `draw_interaction_lines` | seaborn | pandas | chart | relative 1e-09 | pass |
| `table.explain spread_changes_with=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain spread_changes_with=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain neighbours_alike_in_order_of=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain neighbours_alike_in_order_of=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_models using=[[...], [...]]` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_models using=[[...], [...]]` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.compare_models check_on_left_out_rows=True` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_models check_on_left_out_rows=True` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_model_averages_of comparing="each with the first"` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_model_averages_of comparing="each with the first"` | R + Python | polars | result | relative 1e-06 | pass |
| `table.find_model_averages_of within_each_group_in=` | R + Python | pandas | result | relative 1e-08 | pass |
| `table.find_model_averages_of within_each_group_in=` | R + Python | polars | result | relative 1e-08 | pass |
| `table.find_model_averages_of over_range_of=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_model_averages_of over_range_of=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_averages_of grouped_by=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of grouped_by=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_averages_of for_each_group_in= with a list of columns` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of for_each_group_in= with a list of columns` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.add_time_and_event_columns` | pandas | pandas | table | relative 1e-09 | pass |
| `table.add_time_and_event_columns` | pandas | polars | table | relative 1e-09 | pass |
| `table.find_risk_over_time` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_risk_over_time` | R + Python | polars | result | relative 1e-09 | pass |
| `draw_risk_curves` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.find_survival_over_time at_time_points=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.find_survival_over_time at_time_points=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.find_survival_over_time test_method="life table"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_survival_over_time test_method="life table"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_survival_over_time allowing_for=` | R + Python | pandas | result | relative 1e-08 | pass |
| `table.find_survival_over_time allowing_for=` | R + Python | polars | result | relative 1e-08 | pass |
| `table.find_survival_over_time followed_from=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.find_survival_over_time followed_from=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.find_survival_over_time average_time_up_to=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_survival_over_time average_time_up_to=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_survival allowing_for=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_survival allowing_for=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.compare_survival followed_from=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_survival followed_from=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.compare_survival average_time_up_to=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_survival average_time_up_to=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_survival competing_with=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_survival competing_with=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain_survival allowing_for=` | statsmodels | pandas | result | relative 1e-07 | pass |
| `table.explain_survival allowing_for=` | statsmodels | polars | result | relative 1e-07 | pass |
| `table.explain_survival followed_from=` | statsmodels | pandas | result | relative 1e-07 | pass |
| `table.explain_survival followed_from=` | statsmodels | polars | result | relative 1e-07 | pass |
| `table.explain_survival competing_with=` | statsmodels | pandas | result | relative 1e-07 | pass |
| `table.explain_survival competing_with=` | statsmodels | polars | result | relative 1e-07 | pass |
| `table.explain_survival test_method="fine-gray"` | R + Python | pandas | result | relative 1e-07 | pass |
| `table.explain_survival test_method="fine-gray"` | R + Python | polars | result | relative 1e-07 | pass |
| `table.explain_survival distribution=` | R + Python | pandas | result | relative 1e-07 | pass |
| `table.explain_survival distribution=` | R + Python | polars | result | relative 1e-07 | pass |
| `draw_survival_curves followed_from=` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `draw_survival_curves allowing_for=` | R + matplotlib | pandas | chart | relative 1e-08 | pass |
| `draw_risk_curves competing_with=` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.combine_studies` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies` | R + Python | polars | result | relative 1e-09 | pass |
| `draw_funnel_plot` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.combine_studies estimates=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies estimates=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies test_method=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies test_method=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies test_method="mantel-haenszel"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies test_method="mantel-haenszel"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies test_method="peto"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies test_method="peto"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies interval_by=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies interval_by=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies for_each_group_in=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies for_each_group_in=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies using=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies using=` | R + Python | polars | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed` | statsmodels | pandas | result | relative 1e-09 | pass |
| `sdata.find_chance_of_finding` | statsmodels | pandas | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed interval_width=` | R + Python | pandas | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed for_test=` | R + Python | pandas | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed test_method=` | R + Python | pandas | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed using=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed outcome=` | R + Python | pandas | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed in_clusters_of=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `sdata.find_how_many_needed based_on=` | SciPy | pandas | result | relative 1e-09 | pass |
| `sdata.find_chance_of_finding drawing_from=` | SciPy | pandas | result | relative 1e-09 | pass |
| `sdata.find_chance_of_finding by_running=` | Python | pandas | result | relative 1e-12 | pass |
| `table.add_diversity_columns` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_diversity_columns` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_diversity_columns at_total_count=` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_diversity_columns at_total_count=` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_diversity_columns show="chao1"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_diversity_columns show="chao1"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_diversity_columns show="hill numbers"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_diversity_columns show="hill numbers"` | R + Python | polars | table | relative 1e-09 | pass |
| `draw_richness_curves` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.add_log_ratio_columns` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns test_method="alr"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns test_method="alr"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns test_method="ilr"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns test_method="ilr"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns zeros_replaced_by="adding 1"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns zeros_replaced_by="adding 1"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_principal_coordinates` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_principal_coordinates` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_principal_coordinates measure="aitchison"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_principal_coordinates measure="aitchison"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.explain_profiles_of` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain_profiles_of` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain_profiles_of measure="hellinger"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain_profiles_of measure="hellinger"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain_profiles_of test_method="canonical correspondence"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain_profiles_of test_method="canonical correspondence"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain_profiles_of allowing_for=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain_profiles_of allowing_for=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles test_method="procrustes"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles test_method="procrustes"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_profiles_of test_method="anosim"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_profiles_of test_method="anosim"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_profiles_of show="contributions"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_profiles_of show="contributions"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_profiles_of measure="aitchison"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_profiles_of measure="aitchison"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_distances_between_rows measure="aitchison"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.find_distances_between_rows measure="aitchison"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_clusters how_many="automatic"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_clusters how_many="automatic"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_clusters measure=` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_clusters measure=` | R + Python | polars | table | relative 1e-09 | pass |
| `draw_cluster_tree` | SciPy | pandas | chart | relative 1e-09 | pass |
| `table.add_axes_that_separate_groups` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_axes_that_separate_groups` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_correspondence_axes` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_correspondence_axes` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_correspondence_axes show="numbers"` | R + Python | pandas | result | relative 1e-10 | pass |
| `table.add_correspondence_axes show="numbers"` | R + Python | polars | result | relative 1e-10 | pass |
| `table.find_hidden_factors_behind` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_hidden_factors_behind` | R + Python | polars | result | relative 1e-06 | pass |
| `table.find_hidden_factors_behind how_many=` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_hidden_factors_behind how_many=` | R + Python | polars | result | relative 1e-06 | pass |
| `table.find_hidden_factors_behind test_method=` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_hidden_factors_behind test_method=` | R + Python | polars | result | relative 1e-06 | pass |
| `table.find_hidden_factors_behind rotation=` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_hidden_factors_behind rotation=` | R + Python | polars | result | relative 1e-06 | pass |
| `table.check_hidden_factors` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.check_hidden_factors` | R + Python | polars | result | relative 1e-06 | pass |
| `table.check_hidden_factors formula=` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.check_hidden_factors formula=` | R + Python | polars | result | relative 1e-06 | pass |
| `table.find_average_direction_of` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.find_average_direction_of` | SciPy | polars | result | relative 1e-09 | pass |
| `table.compare_shape_to shape="even around the circle"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_shape_to shape="even around the circle"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_autocorrelation_of x=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_autocorrelation_of x=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_autocorrelation_of nearest=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_autocorrelation_of nearest=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_autocorrelation_of on_globe=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_autocorrelation_of on_globe=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_variogram_of` | R + Python | pandas | result | relative 1e-07 | pass |
| `table.find_variogram_of` | R + Python | polars | result | relative 1e-07 | pass |
| `draw_variogram` | R + matplotlib | pandas | chart | relative 1e-07 | pass |
| `table.find_return_levels_of` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_return_levels_of` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_return_levels_of values_above=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_return_levels_of values_above=` | R + Python | polars | result | relative 1e-09 | pass |
| `draw_threshold_check` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.fit_distribution_to distribution="gev"` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.fit_distribution_to distribution="gev"` | R + Python | polars | result | relative 1e-06 | pass |
| `table.fit_distribution_to distribution="generalised pareto"` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.fit_distribution_to distribution="generalised pareto"` | R + Python | polars | result | relative 1e-05 | pass |
| `table.find_percentile_of weights=` | NumPy | pandas | value | relative 1e-12 | pass |
| `table.find_percentile_of weights=` | NumPy | polars | value | relative 1e-12 | pass |
| `table.find_percentile_of weight_kind="analytic"` | NumPy | pandas | value | relative 1e-12 | pass |
| `table.find_percentile_of weight_kind="analytic"` | NumPy | polars | value | relative 1e-12 | pass |
| `table.find_median_of weights=` | NumPy | pandas | value | relative 1e-12 | pass |
| `table.find_median_of weights=` | NumPy | polars | value | relative 1e-12 | pass |
| `table.find_correlation_between show="covariance"` | pandas | pandas | table | relative 1e-12 | pass |
| `table.find_correlation_between show="covariance"` | pandas | polars | table | relative 1e-12 | pass |
| `table.forecast order="automatic"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.forecast order="automatic"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.add_adjusted_p_value_column test_method="storey"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_adjusted_p_value_column test_method="storey"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_adjusted_p_value_column test_method="local fdr"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_adjusted_p_value_column test_method="local fdr"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.compare_each_pair_of matched_by=, test_method="nemenyi"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_each_pair_of matched_by=, test_method="nemenyi"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_each_pair_of matched_by=, test_method="conover"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_each_pair_of matched_by=, test_method="conover"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_each_pair_of based_on="percents"` | SciPy and statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_each_pair_of based_on="percents"` | SciPy and statsmodels | polars | result | relative 1e-09 | pass |
| `sdata.make_random_assignments` | R + Python | pandas | table | relative 1e-12 | pass |
| `sdata.make_design_table` | R + Python | pandas | table | relative 1e-12 | pass |
| `sdata.make_design_table of_kind="randomised blocks"` | R + Python | pandas | table | relative 1e-12 | pass |
| `sdata.make_design_table of_kind="latin square"` | R + Python | pandas | table | relative 1e-12 | pass |
| `sdata.make_design_table of_kind="split plot"` | R + Python | pandas | table | relative 1e-12 | pass |
| `table.keep_random_rows for_each_group_in=` | pandas | pandas | table | relative 1e-12 | pass |
| `table.keep_random_rows for_each_group_in=` | pandas | polars | table | relative 1e-12 | pass |
| `table.keep_random_rows percent=` | pandas | pandas | table | relative 1e-12 | pass |
| `table.keep_random_rows percent=` | pandas | polars | table | relative 1e-12 | pass |
| `table.count_empty_cells_in show="patterns"` | pandas | pandas | table | relative 1e-12 | pass |
| `table.count_empty_cells_in show="patterns"` | pandas | polars | table | relative 1e-12 | pass |
| `table.count_empty_cells_in columns=` | pandas | pandas | printed | relative 1e-09 | pass |
| `table.count_empty_cells_in columns=` | pandas | polars | printed | relative 1e-09 | pass |
| `table.count_each columns=, in_order=` | pandas and NumPy | pandas | result | relative 1e-12 | pass |
| `table.count_each columns=, in_order=` | pandas and NumPy | polars | result | relative 1e-12 | pass |
| `draw_answer_bars` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.find_average_of after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_average_of after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_total_of after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_total_of after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_median_of after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_median_of after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_percentile_of after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_percentile_of after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_percent_of_rows_where after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_percent_of_rows_where after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.count_rows after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.count_rows after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_averages_of after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_counts_of after use_survey_design()` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_counts_of after use_survey_design()` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_balanced_groups_of` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_balanced_groups_of` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_balanced_groups_of test_method="matching"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_balanced_groups_of test_method="matching"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_risks show="attributable fractions"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_risks show="attributable fractions"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.rate_of standard_population=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.rate_of standard_population=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_rates standard_rates=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_rates standard_rates=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain through=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain through=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.compare_averages_of period=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of period=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between empty_cells="multiple imputation"` | R + Python | pandas | value | relative 1e-09 | pass |
| `table.find_correlation_between empty_cells="multiple imputation"` | R + Python | polars | value | relative 1e-09 | pass |
| `table.compare_averages_of test_method="bayesian"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of test_method="bayesian"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_before_and_after test_method="bayesian"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_before_and_after test_method="bayesian"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_average_to test_method="bayesian"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_average_to test_method="bayesian"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between test_method="bayesian"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_correlation_between test_method="bayesian"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_counts_of test_method="bayesian"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_counts_of test_method="bayesian"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain test_method="bayesian"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain test_method="bayesian"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain test_method="bayesian", grouped_by=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain test_method="bayesian", grouped_by=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.check_model_of test_method="bayesian"` | R + Python | pandas | value | relative 1e-09 | pass |
| `table.check_model_of test_method="bayesian"` | R + Python | polars | value | relative 1e-09 | pass |
| `get_numbers_drawn` | matplotlib | pandas | table | relative 1e-09 | pass |
| `table.repeat_each_row_by` | pandas | pandas | table | relative 1e-09 | pass |
| `table.repeat_each_row_by` | Polars | pandas | table | relative 1e-09 | pass |
| `table.repeat_each_row_by` | pandas | polars | table | relative 1e-09 | pass |
| `table.repeat_each_row_by` | Polars | polars | table | relative 1e-09 | pass |
| `table.show_rows_that_pull_model` | statsmodels | pandas | table | relative 1e-09 | pass |
| `table.show_rows_that_pull_model` | statsmodels | polars | table | relative 1e-09 | pass |
| `sdata.get_example from_r_package=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.check_model_of show="numbers"` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.check_model_of show="numbers"` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between show="result table"` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.find_correlation_between show="result table"` | SciPy | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between allowing_for=, show="result table"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_correlation_between allowing_for=, show="result table"` | R + Python | polars | result | relative 1e-09 | pass |
| `trade_off_curve get_numbers_drawn()` | R + Python | pandas | result | relative 1e-12 | pass |
| `nums.smooth` | SciPy | pandas | value | relative 1e-12 | pass |
| `nums.remove_trend` | SciPy | pandas | value | relative 1e-12 | pass |
| `table.add_trend_and_season` | statsmodels | pandas | table | relative 1e-09 | pass |
| `table.add_trend_and_season` | statsmodels | polars | table | relative 1e-09 | pass |
| `nums.find_autocorrelation` | statsmodels | pandas | table | relative 1e-09 | pass |
| `table.check_steady_over_time` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.check_steady_over_time` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_change_points_in` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.find_change_points_in` | R + Python | polars | table | relative 1e-09 | pass |
| `nums.forecast` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.compare_forecasts_for` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.compare_forecasts_for` | R + Python | polars | table | relative 1e-09 | pass |
| `nums.find_each_peak_that` | SciPy | pandas | table | relative 1e-12 | pass |
| `nums.find_each_dip_that` | SciPy | pandas | table | relative 1e-12 | pass |
| `table.find_each_dip_that` | SciPy | pandas | table | relative 1e-09 | pass |
| `table.find_each_dip_that` | SciPy | polars | table | relative 1e-09 | pass |
| `table.find_spectrum_of` | SciPy | pandas | table | relative 1e-09 | pass |
| `table.find_spectrum_of` | SciPy | polars | table | relative 1e-09 | pass |
| `nums.find_spectrum` | SciPy | pandas | table | relative 1e-09 | pass |
| `nums.keep_each_frequency_that` | SciPy | pandas | value | relative 1e-09 | pass |
| `nums.remove_each_frequency_that` | SciPy | pandas | value | relative 1e-09 | pass |
| `table.add_filtered_column` | SciPy | pandas | table | relative 1e-09 | pass |
| `table.add_filtered_column` | SciPy | polars | table | relative 1e-09 | pass |
| `sdata.frequency_filter` | SciPy | pandas | table | relative 1e-09 | pass |
| `nums.find_envelope` | SciPy | pandas | value | relative 1e-09 | pass |
| `table.add_envelope_column` | SciPy | pandas | table | relative 1e-09 | pass |
| `table.add_envelope_column` | SciPy | polars | table | relative 1e-09 | pass |
| `nums.take_fourier_transform` | SciPy | pandas | table | relative 1e-12 | pass |
| `sdata.find_inverse_fourier_transform` | SciPy | pandas | value | relative 1e-12 | pass |
| `nums.convolve_with` | SciPy | pandas | value | relative 1e-12 | pass |
| `nums.deconvolve_by` | SciPy | pandas | value | relative 1e-12 | pass |
| `nums.change_time_step` | SciPy | pandas | value | relative 1e-09 | pass |
| `sdata.make_wave` | SciPy | pandas | value | relative 1e-12 | pass |
| `sdata.make_window_shape` | SciPy | pandas | value | relative 1e-12 | pass |
| `sdata.system` | SciPy | pandas | table | relative 1e-12 | pass |
| `system.step_response` | SciPy | pandas | table | relative 1e-09 | pass |
| `system.impulse_response` | SciPy | pandas | table | relative 1e-09 | pass |
| `system.response_to` | SciPy | pandas | table | relative 1e-09 | pass |
| `system.frequency_response` | SciPy | pandas | table | relative 1e-09 | pass |
| `system.poles` | SciPy | pandas | table | relative 1e-12 | pass |
| `system.zeros` | SciPy | pandas | table | relative 1e-12 | pass |
| `system.is_stable` | SciPy | pandas | value | relative 0 | pass |
| `system.steady_gain` | NumPy | pandas | value | relative 1e-12 | pass |
| `system.in_steps` | SciPy | pandas | table | relative 1e-09 | pass |
| `system.then` | NumPy | pandas | table | relative 1e-12 | pass |
| `system.add` | NumPy | pandas | table | relative 1e-12 | pass |
| `system.with_feedback` | NumPy | pandas | table | relative 1e-12 | pass |
| `system.table` | SciPy | pandas | table | relative 1e-12 | pass |
| `autocorrelation_bars` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `cross_correlation_bars` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `lag_dots` | matplotlib | pandas | chart | relative 1e-12 | pass |
| `peak_dots` | matplotlib | pandas | chart | relative 1e-12 | pass |
| `spectrum` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `spectrum_over_time` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `trend_and_season` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `forecast` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `system.chart` | matplotlib | pandas | chart | relative 1e-09 | pass |
| `sdata.table` | pandas | pandas | table | relative 1e-09 | pass |
| `sdata.get_example` | pandas | pandas | table | relative 1e-09 | pass |
| `sdata.chart` | seaborn | pandas | chart | relative 1e-09 | pass |
| `table.start_chart` | seaborn | pandas | chart | relative 1e-09 | pass |
| `table.start_chart` | seaborn | polars | chart | relative 1e-09 | pass |
| `sdata.numbers` | NumPy | pandas | value | relative 0 | pass |
| `sdata.number_grid` | NumPy | pandas | value | relative 0 | pass |
| `sdata.distribution` | SciPy | pandas | value | relative 1e-12 | pass |
| `sdata.make_random_numbers` | NumPy | pandas | value | relative 0 | pass |
| `sdata.make_run_of_dates` | pandas | pandas | table | relative 1e-09 | pass |
| `sdata.help` | - | - | none | relative 0 | pass |
| `sdata.show_all_words` | - | - | none | relative 0 | pass |
| `sdata.show_day` | - | - | none | relative 0 | pass |
| `sdata.show_lesson` | - | - | none | relative 0 | pass |
| `sdata.show_packages_used` | - | - | none | relative 0 | pass |
| `sdata.start_30_days` | - | - | none | relative 0 | pass |
| `sdata.show_today` | - | - | none | relative 0 | pass |
| `sdata.show_answers` | - | - | none | relative 0 | pass |
| `sdata.go_to_next_day` | - | - | none | relative 0 | pass |

How each kind is compared:

- **value**: the number the word gives, against the library's number
- **table**: the table the word gives, against the library's table (values and column order)
- **result**: the numbers in simplydata's result table (statistic, degrees of freedom, p-value ...) against the library's result
- **chart**: the chart's data (bars, dots, lines, labels, limits ...), not its pixels
- **printed**: for words that show something and give nothing back: every line the library code prints appears, in the same order, in what the word prints (spaces at the ends of lines left out)
- **none** (16 words: `table.undo`, `table.show_steps`, `table.start_again`, `nums.undo`, `nums.show_steps`, `nums.start_again`, `dist.show_parameters`, `sdata.help`, `sdata.show_all_words`, `sdata.show_day`, `sdata.show_lesson`, `sdata.show_packages_used`, `sdata.start_30_days`, `sdata.show_today`, `sdata.show_answers`, `sdata.go_to_next_day`): help, learning, undo and show-steps words. They print help, a lesson, the packages used or the steps taken, or put a table back as it was; they compute no number, so there is nothing to compare them with. Their box is run to show that it runs.

## Choices simplydata makes

Where simplydata's default differs from the package underneath, it is listed here, so a difference is never hidden. The manual shows each one as a numbered mark in the code.

- `draw_bars` (1): simplydata draws no error bars unless you ask (error=); seaborn's own default draws a bootstrap 95 % interval on each bar.
- `draw_histogram` (1): simplydata makes 10 bins unless you say with_bins=; seaborn's own default chooses the number of bins from the data.
- `trade_off_curve` (1): higher scores count as positive (direction = "<"); positive_when="lower" turns it round.
- `trade_off_curve` (2): the AUC and its 95 % interval by DeLong's method, written in the legend.
- `trade_off_curve` (3): the best cut-off by Youden's index (the most found cases minus false alarms) is marked with a dot.
- `save` (1): a chart is 8 x 6 inches unless set_size() says otherwise; matplotlib's own default is 6.4 x 4.8.
- `save` (2): 300 dots per inch, with the empty edges trimmed: sharp enough for a journal. quality="high" saves at 600, resolution= at any value; a .tif file is packed without loss (LZW).
- `write_title_on_top` (1): one chart gets the title of its axes; a figure with several panels gets one title over them all (fig.suptitle), in bold.
- `label_x` (1): on a figure with several panels the panels' own x labels are cleared and one label is written under them all (fig.supxlabel).
- `label_y` (1): on a figure with several panels the panels' own y labels are cleared and one label is written beside them all (fig.supylabel).
- `rotate_labels_x` (1): a turned name is lined up by its right end (its left end for a negative angle), so it ends just under its own bar; matplotlib's own default centres it, and long names then drift sideways.
- `rotate_labels_x` (2): the name turns about that end (rotation mode "anchor"), so it stays next to its tick.
- `write_caption_at_bottom` (1): the caption hangs 4 points under the x-axis label, so it moves down when the labels are turned or grow; on a figure with several panels it is the figure's bottom line instead (fig.supxlabel).
- `write_caption_at_bottom` (2): in smaller letters (0.8 of the text size: 9.6 points in simplydata's paper look, where text is 12), slightly faded, so it reads as a note, not a label.
- `use_font_size` (1): all the words grow together: in the normal paper look the sizes are 12 for text, 14 for the title, 13 for the axis labels and 11 for tick labels and the legend, and use_font_size(18) multiplies each by 18 / 12, so the title stays the biggest. In another style each grows by 18 over that style's text size (18 / 15 in "school").
- `use_colour` (1): the exact colour asked for (saturation=1); seaborn's own default (0.75) makes bar colours a little duller than the name says.
- `use_colours` (1): the groups get the colours in the order they first appear in the table (order_legend() changes it); seaborn sorts the names of some columns first.
- `use_colours` (2): the exact colours asked for (saturation=1), not seaborn's slightly duller ones.
- `put_legend_at_bottom` (1): one row of entries (up to 6 in a row) under the x-axis label, outside the chart, so it covers no data; a label shared by several panels becomes the legend's heading.
- `order_x` (1): the rows are put in that order with a stable sort, and seaborn draws the groups in the order they appear, so every chart type, colour and later step follows it; groups left out come after the ones named. seaborn's order= does the same for one call.
- `use_style` (1): "school" is bigger words and thicker lines, for a classroom screen; "presentation" is bigger still, "dark" puts light words and brighter colours on a dark background, and "paper" is the normal look.
- `hide_legend` (1): the legend of every panel (and of a second y-axis) is removed; show_legend() brings it back.
- `put_legend_on_left` (1): outside the chart on the left, beside the y-axis label, so it covers no data; on a figure with several panels the shared y label goes back to the panels on the left.
- `draw_lines` (1): each point is the average of its rows (here 6 pupils), with no band around the line unless you ask (error=); seaborn's own default shades a bootstrap 95 % interval.
- `draw_boxes` (1): without groups the boxes get simplydata's first colour (Okabe-Ito blue, safe for colour-blind readers); colour= or use_colour() choose others.
- `draw_boxes` (2): the exact colour (saturation=1), not seaborn's slightly duller one.
- `draw_all_dots` (1): simplydata draws on a matplotlib Figure of its own, not on pyplot's current figure, so a chart never lands on another one; seaborn works out the sideways spread of a swarm when the picture is drawn (shown or saved).
- `draw_all_dots` (2): up to 100 dots in a group are packed side by side (a swarm); above that they are spread at random (seaborn stripplot, with the random numbers fixed so the chart is the same every time).
- `draw_all_dots` (3): over boxes or violins the dots are dark grey, so they stand out; colour= still chooses your own.
- `draw_violins` (1): each violin stops at the smallest and the largest value (cut=0), so it never shows values that cannot happen, such as marks below 0; seaborn's own default runs the curve on past them.
- `draw_violins` (2): simplydata's first colour, exactly (saturation=1), not seaborn's slightly duller one.
- `show=` (1): the word becomes seaborn's estimator: "average" is "mean", "median" is "median", "total" is "sum", "smallest" and "biggest" are "min" and "max", "standard deviation" is "std"; "count" counts the rows (seaborn countplot).
- `error=` (1): "standard deviation" is seaborn's "sd" and "standard error" its "se", both with n - 1; "confidence interval" is the t interval of the mean (as R t.test()), not seaborn's bootstrap.
- `error=` (2): short caps at the ends of each error bar.
- `write_numbers_on_bars` (1): each value just above its bar, with a comma for thousands and no decimals unless with_decimals= asks; stacked bars get the number in the middle of each piece, and with error bars it sits past the end of the error bar.
- `write_numbers_on_bars` (2): a little more room above the bars, so the numbers stay inside the chart.
- `fit_line` (1): the line is drawn only over the range of x in the data, never past it.
- `draw_qq_dots` (1): SciPy places the dots at Filliben's positions; R's qqnorm() uses slightly different ones.
- `draw_qq_dots` (2): the straight line is the least-squares line through the dots (as SciPy gives it); R's qqline() goes through the quartiles instead.
- `set_range_y` (1): None keeps that end where matplotlib put it (set_range_y(None, 100)); a flipped axis stays flipped.
- `draw_line_at_y` (1): a grey dashed line, 1.5 points wide, drawn above the bars and below the dots (zorder 2.5).
- `draw_line_at_y` (2): the label sits just outside the right edge, so it never covers a bar or a dot, in the legend's size of letters.
- `shade_between_y` (1): a light grey band (alpha 0.2), behind everything else on the chart (zorder 0), so the data stay in front of it.
- `use_log_scale_y` (1): the scale is set before drawing, so the axis ranges are worked out on the log scale and later ticks and ranges are not undone by it.
- `draw_line_at_x` (1): a grey dashed line, 1.5 points wide, in front of bars and behind dots (zorder 2.5).
- `draw_line_at_x` (2): the label stands up along the line, near the top, on its left side, on a soft box in the chart's background colour so the line does not cross the words.
- `write_ticks_y_as` (1): the numbers are already percents (out of 100); out_of=1 is for shares, so 0.25 shows as 25 %.
- `set_size` (1): matplotlib measures in inches, so centimetres are divided by 2.54 (millimetres by 25.4); in pixels the saved picture has exactly that many pixels at any resolution.
- `write_note` (1): the note sits just above the place, on a soft background in the chart's own colour, so it stays readable over lines and bars.
- `draw_heatmap` (1): each cell is the average of its rows; the rows and columns keep the order they appear in (month names in calendar order).
- `draw_heatmap` (2): the numbers are written plainly: whole numbers without decimals, others to about 3 significant digits, never as 1.2e+02.
- `draw_heatmap` (3): numbers on both sides of 0 get blue below and red above, with white at 0 (the scale goes equally far both ways); otherwise the viridis colours, safe for colour-blind readers. use_colour_scale() chooses others.
- `draw_one_chart_for_each_group_in` (1): about 4 x 3.3 inches for each small chart (here 3 across, 1 down), unless set_size() says otherwise.
- `draw_one_chart_for_each_group_in` (2): the small charts share their axis ranges, so they can be compared at a glance; same_x=False or same_y=False lets each choose its own.
- `draw_one_chart_for_each_group_in` (3): each small chart is named by its group, in the order the groups appear in the table.
- `sdata.put_side_by_side` (1): each chart gets 3/4 of its own size (8 x 6 inches becomes 6 x 4.5), side by side.
- `sdata.put_side_by_side` (2): each chart is drawn in a part of the figure of its own (a SubFigure), so its title, labels and legend stay with it and never land on its neighbour.
- `sdata.put_side_by_side` (3): same_y=True gives every chart the y range that holds all their data.
- `sdata.put_one_above_other` (1): each chart gets 3/4 of its own size (8 x 6 inches becomes 6 x 4.5), one above the other.
- `sdata.put_one_above_other` (2): each chart is drawn in a part of the figure of its own (a SubFigure), so its title, labels and legend stay with it.
- `sdata.put_in_rows_and_columns` (1): each chart gets 3/4 of its own size, in rows of per_row= charts, and a title adds half an inch.
- `sdata.put_in_rows_and_columns` (2): each chart is drawn as it would be on its own: a histogram has 10 bins and its y label in small letters (count).
- `sdata.put_in_rows_and_columns` (3): the page's title goes over every chart, in bold and a little bigger than their own titles.
- `sdata.draw_all_pairs` (1): every number column (here 3) against every other, about 2.4 inches a column, plus room for the legend.
- `sdata.draw_all_pairs` (2): the diagonal shows each column on its own: a density curve for each group when colour= makes groups (common_norm=False: every curve has area 1), a histogram without groups; it sits on a second y-axis so the row keeps its own scale.
- `sdata.draw_all_pairs` (3): smaller, slightly see-through dots without rims, so crowded panels stay readable.
- `add_second_y` (1): one value for each name on the x-axis, the average of its rows (as the line under it), placed above that name.
- `add_second_y` (2): the new layer gets the first colour of the set that the chart does not use yet, and its axis, label and tick numbers are written in that colour.
- `add_second_y` (3): the first chart is kept in front of the new bars.
- `animate` (1): every picture keeps the axis ranges of the chart with all the data, so the bars do not jump about, and is named by its value.
- `animate` (2): 0.8 seconds for each picture (seconds_per_frame=), saved as a .gif at 100 dots per inch.
- `animate` (3): one picture for each value, smallest first (month names in calendar order); keep=True keeps the values before it in each picture.
- `fit_formula` (1): every value to find starts at 1 unless start= says otherwise.
- `fit_formula` (2): Levenberg-Marquardt, as R nls(), with tight stopping rules; between= limits switch to SciPy's trust region method.
- `draw_area` (1): several rows at the same x are averaged, as in draw_lines(): here the 3 cities of each month.
- `draw_area` (2): the space under the line is filled down to 0 in the same colour, see-through (alpha 0.35), so areas of several groups show through each other.
- `draw_pie` (1): one slice per label, the total of its values, in the order the labels first appear (without values= each slice counts the rows).
- `draw_pie` (2): each slice is named and shows its share in whole percents.
- `draw_pie` (3): the first slice starts at 12 o'clock and the slices go round clockwise, like a clock; matplotlib's own default starts at 3 o'clock and goes anticlockwise.
- `draw_polar` (1): a compass: 0 at the top (north) and round clockwise, because the column is named like a direction (wind_direction, bearing, heading) or full_turn= is given; other angles start on the right and go anticlockwise, the way maths measures them.
- `draw_polar` (2): the angles are in degrees and are turned into radians for matplotlib (full_turn=24 reads hours, full_turn=12 months).
- `draw_polar` (3): the legend sits outside the circle, on its right.
- `draw_contour` (1): every east goes with every north here (a full grid), so the heights are drawn as they are; scattered points are first joined onto a 100 x 100 grid with straight lines in between (SciPy griddata, method="linear").
- `draw_contour` (2): about 10 bands, in the viridis colours (safe for colour-blind readers); use_colour_scale() chooses others.
- `draw_contour` (3): a line along the edge of every band, so neighbouring bands stay apart.
- `draw_surface` (1): a full grid (every east with every north) is drawn as it is; scattered points are first joined onto a 100 x 100 grid (SciPy griddata, straight lines in between).
- `draw_dots_3d` (1): words (or a number column with 8 values or fewer) give each group its own colour, in the order the groups appear; a number column with more values gets a colour scale and a colour bar instead.
- `draw_band` (1): one band per group, in its group's colour and in the order the groups appear, each named in the legend.
- `draw_band` (2): light bands (alpha 0.25, transparency=0.75) with no edge line, so lines drawn on top stay clear.
- `draw_map_of_empty_cells` (1): a cell is empty when it is missing or holds only spaces, as in the table words.
- `draw_map_of_empty_cells` (2): one strip per column and one line per row, the first row at the top; empty cells in vermilion on light grey (Okabe-Ito, safe for colour-blind readers).
- `draw_map_of_empty_cells` (3): under each column, how many of its cells are empty.
- `sticks` (1): each value is a thin stick (1.5 points) from 0, with a small dot on top; thickness= sets the width.
- `sticks` (2): a thin line marks 0, behind the sticks, so values below 0 hang down from it.
- `draw_error_bars` (1): the standard deviation with n - 1 (pandas std), empty cells skipped; "standard error" divides it by the square root of n, "confidence interval" is the t interval of the mean.
- `draw_error_bars` (2): on dots a short wide dash marks each average, and the bars end in caps.
- `fit_curve` (1): a curve with one bend (degree 2) unless of_degree= says otherwise, fitted by least squares on the powers of x mapped onto -1 to 1, which keeps big x values accurate: simplydata runs statsmodels WLS on them (the engine of table.fit_curve); NumPy's Polynomial.fit, shown here, gives the same curve.
- `fit_curve` (2): the curve is drawn only over the range of x in the data, never past it.
- `fit_distribution` (1): the values are found by maximum likelihood, as R MASS::fitdistr(): for the normal distribution simplydata works them out directly (the average, and the standard deviation dividing by n, not n - 1), which equals stats.norm.fit. They are printed once.
- `fit_distribution` (2): the curve runs over the x range of the histogram, at 200 points.
- `fit_distribution` (3): over a histogram of counts the curve is scaled to the bars: density x number of values x bar width (x 100 x bar width for percents; a density histogram needs no scaling).
- `draw_curve` (1): the curve runs over the x range of what is drawn (between= sets it), at 200 points (steps=).
- `draw_curve` (2): over a histogram of counts the density is scaled to the bars (x number of values x bar width), and a note says so.
- `draw_density` (1): each group's curve has an area of 1 on its own (common_norm=False), so a small group is not squashed flat; seaborn's own default shares one area between all the groups.
- `draw_count_bars` (1): the exact colours (saturation=1), not seaborn's slightly duller ones.
- `draw_side_histograms` (1): two thin histograms just outside the chart, along the top (x) and the right (y), sharing the chart's axes so each bar lines up with its dots.
- `draw_side_histograms` (2): the bins follow NumPy's "auto" rule (at most 50); with colour groups each group is an outline, so they stay readable where they overlap.
- `draw_cumulative_share` (1): the y-axis is named in words, "share at or below", not seaborn's "Proportion".
- `draw_line_with_slope` (1): through 0, 0 unless through= or intercept= says otherwise, right across the chart: a grey dashed line, 1.5 points wide, above bars and below dots (zorder 2.5).
- `draw_line_with_slope` (2): labelled= names the line in the legend, after any groups already there.
- `shade_between_x` (1): a light grey band (alpha 0.2) from the bottom of the chart to the top, between the two x values.
- `write_names_on_dots` (1): each name goes just right of its dot (2 points past the dot's edge: 5.5 points from its middle in the paper look); where it would cover another name or dot, or leave the chart, it tries left, above, below and then the corners. Here Chen (at the right edge) and Dina (next to Ben's name) go left. A name with no free place is left out, and a line says how many.
- `write_names_on_dots` (2): each name sits on a soft background in the chart's own colour, so it stays readable over lines.
- `use_font` (1): the font is matplotlib's font.family for every word of the chart, used while it is drawn and saved, so your other charts keep theirs.
- `set_range_x` (1): None keeps that end where matplotlib put it; a flipped axis stays flipped.
- `put_ticks_x` (1): a name is looked up among the names under the bars, which seaborn puts at 0, 1, 2 ..., and keeps its name; numbers are used as they are.
- `rotate_labels_y` (1): each name turns about its right end (rotation mode "anchor"), the end next to the axis, so it stays beside its own bar; matplotlib's own default turns it about its middle.
- `write_ticks_x_as` (1): a comma between the thousands and no decimals unless with_decimals= asks (1,000, not 1000.0).
- `use_colour_scale` (1): the colours run from the smallest value to the biggest; between=[low, high] fixes the ends (values beyond get the end colours), log=True spreads them on a log scale and steps= cuts the scale into bands (LogNorm, BoundaryNorm). A two-sided scale such as "blue to red" with middle=0 goes equally far on both sides.
- `show_grid` (1): lines in both directions; simplydata's normal paper look draws only the lines across the chart, from the y-axis.
- `put_legend_at_top` (1): the chart's title becomes the legend's heading, so the two never sit on top of each other, and the group name moves to the front of the row.
- `put_legend_at_top` (2): one row of entries (up to 6 in a row) above the chart, outside it, so it covers no data.
- `put_legend_on_right` (1): outside the chart on the right, so it covers no data; on a figure with several panels one legend holds the entries of them all.
- `label_legend` (1): the legend of every panel (and of a second y-axis) gets the name, and a legend moved outside by put_legend_... keeps it; label_legend("") leaves the name out.
- `order_y` (1): the rows are put in that order with a stable sort, and seaborn draws the groups in the order they appear, the first at the top; groups left out come after the ones named.
- `order_legend` (1): the rows are put in that order with a stable sort, so the legend, the colours and the bars side by side all follow it; groups left out come after the ones named.
- `order_legend` (2): the first group named gets the first colour.
- `add_zoom_box` (1): the box sits in the top right corner (where= chooses another), 0.39 of the chart wide and 0.4 high.
- `add_zoom_box` (2): the chart's own drawing steps run again inside the box, so it shows exactly what the chart shows, without its legend and axis labels.
- `forest_plot` (1): the first row at the top, as in a table.
- `forest_plot` (2): a ratio (the column, or every row's name, says "ratio") gets a log scale and a dashed line at 1, no effect; other results a plain scale with the line at 0. log_scale= and line_at= choose.
- `forest_plot` (3): the x label names the interval's level and the line.
- `table.keep_rows_where` (1): is_above= means strictly above (>); use is_at_least= for >=. Rows with an empty cell in "marks" are left out, as in pandas and Polars.
- `table.find_average_of` (1): one row for each group, the groups sorted (English, Maths, Science), with rows whose group cell is empty as a group of their own, last; empty cells in "marks" are skipped, as pandas and Polars do (NumPy's mean would give nan).
- `table.show_first_rows` (1): the rows are numbered from 1, the way people count; pandas numbers them from 0. Only what is shown changes: as_pandas() still gives the table with pandas' own row labels.
- `table.describe_columns` (1): numbers are written for people: whole numbers without .0, others rounded to 2 decimals.
- `table.describe_columns` (2): text columns get the number of different values (empty cells left out), number columns the smallest, biggest and average (empty cells left out, as pandas does).
- `table.sort_by` (1): rows that tie keep the order they had (a stable sort); pandas' own default sort (quicksort) does not promise that.
- `table.sort_by` (2): empty cells go last, also when the biggest come first (Polars' own default puts them first).
- `table.keep_rows_by_position` (1): rows are counted from 1 and both ends are kept, so rows 10 to 20 are 11 rows: Python's 9:20 (it counts from 0 and leaves out the end); in Polars, 11 rows from row 9.
- `table.fill_empty_cells_in` (1): the median of the filled cells of the whole column (the empty cells left out).
- `table.turn_into_numbers` (1): a comma between groups of three digits is a thousands mark: 1,200 is twelve hundred.
- `table.turn_into_numbers` (2): any other single comma is a decimal comma: 12,5 is twelve and a half.
- `table.turn_into_numbers` (3): a cell that is not a number after that becomes empty, as pd.to_numeric(errors="coerce"); simplydata says how many and shows up to 3 of them. Blank text is simply empty.
- `table.add_group_column` (1): a value exactly on a cut goes into the higher group: a mark of 61 is a B (right=False, left_closed=True); pandas and Polars put it in the lower group by default.
- `table.find_summary_of` (1): one row for each group, the groups sorted (A, B, C); rows with an empty group cell form a group of their own, shown last (dropna=False).
- `table.find_summary_of` (2): the standard deviation of a sample (n - 1), as pandas, Polars and R sd(); NumPy's own default is n.
- `table.join_with` (1): a column found in both tables (other than using=) keeps its name in this table and gets "_other" in the other table's copy.
- `table.add_z_score_column` (1): the standard deviation of a sample (n - 1, ddof=1), as R scale(); SciPy's zscore uses n unless told ddof=1.
- `table.save` (1): no row labels are written (index=False): the file holds only your columns.
- `table.save in_sheet=` (1): mode="a" adds the sheet to the Excel file that is there and keeps its other sheets; if_sheet_exists="replace" replaces a sheet of the same name (simplydata prints that it did). A file that does not exist yet is made with pandas ExcelWriter and that one sheet.
- `table.make_copy` (1): the copy keeps the steps so far, so backup.undo() and backup.show_steps() work on it; pandas df.copy() keeps only the data.
- `table.add_missing_dates` (1): the table comes back sorted by the groups, then the dates; the group's name is copied into the new rows, and rows with an empty group cell are a group of their own (dropna=False).
- `table.add_missing_dates` (2): each group's own run, from its first to its last date: no rows are added before or after (between= adds them).
- `table.add_rolling_column` (1): the window follows sorted_by=, but the rows keep their place in the table (assign lines the values up by row).
- `table.add_rolling_column` (2): the window is this row and the 2 rows before it, within each city; the first 2 rows of each city stay empty until the window is full.
- `table.show_rows_with_outliers` (1): the quartiles of each class by pandas' (and R's type 7) linear method; rows with an empty class are a group of their own (dropna=False).
- `table.show_rows_with_outliers` (2): Tukey's rule, the one box plots use: below Q1 - 1.5 x IQR or above Q3 + 1.5 x IQR.
- `table.show_rows_with_outliers` (3): each row is shown with its place in the whole table, counted from 1, so remove_rows_by_position() can follow.
- `table.show_last_rows` (1): each row is numbered with its place in the whole table, counted from 1: the last 3 of 54 rows are 52, 53 and 54, the numbers keep_rows_by_position() takes.
- `table.show` (1): the rows are numbered from 1, the way people count; pandas numbers them from 0.
- `table.show` (2): every row and every column is shown (up to 1,000 rows); pandas on its own shows the first and last 5 of these 180 rows with "..." between.
- `table.get_row` (1): rows are counted from 1, so row 45 is Python's position 44.
- `table.get_row` (2): an empty cell becomes None, on both engines (pandas gives nan, Polars None); row 45 has no sales.
- `table.get_cell_at` (1): rows are counted from 1, so row 3 is Python's position 2.
- `table.keep_columns_by_position` (1): columns are counted from 1 at the left and both ends are kept, so columns 1 to 3 are Python's 0:3.
- `table.remove_columns_by_position` (1): columns are counted from 1 at the left and both ends are removed, so columns 2 to 3 are Python's 1:3.
- `table.remove_rows_where` (1): a row whose cell is empty is never removed by a comparison: the 10 rows without sales stay. In pandas an empty cell is never below 300; in Polars the comparison gives null, which is made False first (without it Polars' filter would drop those rows too).
- `table.remove_rows_by_position` (1): rows are counted from 1, so rows 12 and 40 are Python's positions 11 and 39.
- `table.remove_duplicate_rows` (1): the first row of each name is kept and the rows stay in their order; Polars' own default keeps any one of them, in any order.
- `table.keep_biggest_rows` (1): exactly 4 rows: when rows tie at the cut, the ones higher up in the table are kept (a stable sort). Here English and Maths each have two 4th-best marks; a note says so.
- `table.keep_biggest_rows` (2): the groups come in order (English, Maths, Science), biggest first within each.
- `table.keep_smallest_rows` (1): exactly 3 rows: when rows tie at the cut, the one higher up in the table is kept (a stable sort). Here Maths has two marks of 47 at the cut; a note says so.
- `table.keep_smallest_rows` (2): the groups come in order (English, Maths, Science), smallest first within each.
- `table.remove_rows_with_outliers` (1): the quartiles of each school by the linear method (pandas' default, R's type 7); Polars' own default is "nearest", which would remove 5 rows here instead of 4.
- `table.remove_rows_with_outliers` (2): Tukey's rule, the one box plots use: below Q1 - 1.5 x IQR or above Q3 + 1.5 x IQR.
- `table.remove_rows_with_outliers` (3): rows with an empty cell stay: the 19 pupils without a sleep value are not outliers.
- `table.remove_rows_with_empty_cells_in` (1): a cell of only spaces counts as empty, as a missing one does; pandas' dropna() would keep it.
- `table.add_is_empty_column` (1): empty means missing, NaN or blank text ("" or only spaces); pandas' isna() finds only the missing one.
- `table.turn_into_text` (1): dates are written year-month-day (2026-01-01), with the time of day only when some date has one; Polars' own cast to text would add 00:00:00.000000 to every cell.
- `table.turn_into_dates` (1): each cell gets the first way of writing that fits, day first before month first: 03/04/2026 is 3 April, and 12/25/2026 can only be 25 December. simplydata's list holds 26 ways (dots, dashes, month names, times of day); these 3 are the ones these cells need.
- `table.turn_into_dates` (2): a cell that fits none of them becomes empty (errors="coerce", strict=False); simplydata says how many and shows one ("soon").
- `table.add_rank_column` (1): rows that tie share the best place and the next place is skipped, as in sports tables (1, 2, 2, 4); pandas' own default gives both 2.5.
- `table.add_rank_column` (2): the biggest value gets place 1 (biggest_first=False gives it to the smallest).
- `table.add_column_with_part_of_date` (1): 1 is Monday and 7 is Sunday, as the ISO 8601 standard and Polars count; pandas counts Monday as 0.
- `table.add_column_with_part_of_text` (1): the text before the first comma ("Big Market", not "Big Market , east"); a cell without a comma gives an empty cell, and simplydata says how many.
- `table.add_column_with_part_of_text` (2): spaces at the ends of the part are removed ("Big Market " becomes "Big Market"), and a part that is blank becomes empty.
- `table.split_column` (1): at most as many pieces as names in into=: the last keeps the rest of the text ("Lee Park"), and a cell with fewer pieces gives an empty cell ("Cara" has no rest). simplydata says how many of each.
- `table.split_column` (2): the new columns take the place of the old one; spaces at the ends of each piece are removed ("Dev   Shah" gives "Shah", not "  Shah").
- `table.replace_text_in` (1): the old text is plain text, not a pattern: "." is a full stop, not "any character"; and it is replaced everywhere it appears (Polars' replace() changes only the first).
- `table.add_previous_value_column` (1): "the row before" follows sorted_by=, but the rows keep their place in the table (here sorted by temperature; assign lines the values up by row).
- `table.add_previous_value_column` (2): within each city; the first month of each city has no row before it and stays empty.
- `table.add_change_column` (1): the previous value is the one before in order of sorted_by= (year), within each country; the rows keep their place, and the first year of each country stays empty.
- `table.add_change_column` (2): in_percent=True is (this - previous) / previous x 100, and a previous value of 0 gives an empty cell (pandas and Polars would give inf).
- `table.find_smallest_of` (1): one row for each city, the cities sorted A to Z (Polars' group_by gives them in any order).
- `table.find_standard_deviation_of` (1): the standard deviation of a sample (divide by n - 1), as pandas, Polars and R sd(); NumPy's own default divides by n.
- `table.find_standard_deviation_of` (2): one row for each class, the classes sorted A to Z.
- `table.count_different_values_in` (1): empty cells are not counted as a value (pandas' nunique() leaves them out; Polars' n_unique() would count the empty value once); a note says how many there were (19).
- `table.count_different_values_in` (2): one row for each school, the schools sorted A to Z.
- `table.find_most_common_of` (1): when values tie (1 and 3 each turn up twice), the smallest is given and a note names the others; empty cells are skipped. pandas' mode() is sorted; Polars' mode() comes in any order.
- `table.find_interval_of` (1): the bias-corrected and accelerated (BCa) bootstrap interval, the usual choice; "percentile bootstrap" and "reverse percentile bootstrap" are the others.
- `table.find_interval_of` (2): 9999 resamples (resamples= changes it).
- `table.find_interval_of` (3): NumPy's random generator with seed 1 (with_seed=), printed, so the same call gives the same interval.
- `table.add_rows_from` (1): columns are matched by their names, so the other table's columns may come in any order; pandas' concat matches them by name itself, Polars' needs them put in the same order first (select(df.columns)).
- `table.gather_into_rows` (1): every other column stays beside each value, and the new columns are called "column" and "value" (names_to=, values_to= change them; pandas' own names are "variable" and "value").
- `table.spread_into_columns` (1): rows and new columns stay in the order they first appear (Jan, Feb ...; Sunnyvale first), on both engines; pandas' pivot sorts them (Apr, Aug ...; Frostby first).
- `table.swap_rows_and_columns` (1): the first column (here "name") names the new columns, because it holds text with no repeat and no empty cell, and the old column names go in a first column called "column"; pandas' plain .T and Polars' transpose() would number the columns instead.
- `table.keep_rows_found_in` (1): a semi join: no column comes in from the other table and no row is repeated, however often a name appears there; the rows keep their order, and an empty key is never found.
- `table.remove_rows_found_in` (1): an anti join: the rows whose name is not in the other table stay, in their order; a row with an empty key is never found, so it stays.
- `table.clean_column_names` (1): the rule of R janitor::clean_names(): % becomes percent and # number, letters such as ø and é become plain letters, every run of other signs one "_", small letters; a name that starts with a digit gets an x in front and a repeated name _2. Unlike janitor, pH becomes ph, not p_h.
- `table.remove_rows_that_are_all_empty` (1): a row goes only when every cell is empty; an empty cell is a missing value or text of only spaces (pandas and Polars count "   " as filled).
- `table.remove_columns_that_are_all_empty` (1): a column goes only when every cell is empty (a missing value or text of only spaces); a table whose every cell is empty is refused rather than left with no columns.
- `table.show_duplicate_rows` (1): every copy is shown, the first one too (keep=False), each with its row number counted from 1, and two empty cells count as the same; the table does not change.
- `table.add_row_summary_column` (1): empty cells are left out of each row's summary, as pandas (skipna) and Polars do; a row with every cell empty gets an empty cell, also for show="total" (pandas sum(min_count=1); Polars sum_horizontal alone would give 0).
- `table.turn_into_categories` (1): a value that is not in in_order= stops the word with its name (pandas Categorical would turn it into an empty cell without a word; Polars Enum refuses it too); without in_order= the order is the one in which the values first appear.
- `table.split_into_rows` (1): the separator is plain text, not a pattern; a cell without it stays one row, and an empty cell stays one row with an empty cell.
- `table.add_running_column` (1): the sum follows sorted_by= (here the date) while the rows keep their place in the table;
- `table.add_running_column` (2): an empty cell stays empty and is left out of the rows after it (for show="average" too, whose pandas expanding().mean() would carry the average on).
- `table.add_row_number_column` (1): numbers start at 1, as table.show() counts (pandas cumcount() starts at 0), in the order of sorted_by=, while the rows keep their place.
- `table.keep_groups_where` (1): whole groups stay or go, in their places; empty cells are left out of each summary, and a group whose summary cannot be worked out (every cell empty) is left out.
- `table.remove_groups_where` (1): whole groups go, the others stay in their places; a group whose summary cannot be worked out is never removed.
- `table.join_with using=` (1): check_that= runs pandas' and Polars' own validate= and, when a key repeats, says which values repeat and in which table, before anything is joined;
- `table.join_with using=` (2): the key keeps this table's name only (pandas keeps both columns; Polars drops the other's).
- `table.spread_into_columns show=` (1): rows and new columns stay in the order they first appear (pandas pivot_table sorts them);
- `table.spread_into_columns show=` (2): a day and fruit that never appear together stay an empty cell for every show= (Polars gives 0 for a total or count of no rows).
- `table.change_column in_rows_where=` (1): the condition is read on the values before the change, and a row it cannot check (an empty cell) keeps its value, with a note.
- `table.keep_first_rows for_each_group_in=` (1): the rows keep their order in the table (Polars group_by().head() would put each group's rows together), and an empty group cell is a group of its own.
- `table.add_missing_combinations_of` (1): the rows come out sorted by the key columns, and every row already there stays as it is: a combination that is there twice keeps both rows (pandas' reindex would refuse it), and a row with an empty key stays, at the end.
- `table.change_time_zone_in` (1): a clock time that never happened (the hour skipped when summer time starts) or happened twice (when it ends) becomes an empty cell, with a note, instead of stopping the whole column (the pandas and Polars default) or being moved without a word.
- `table.spread_into_yes_no_columns` (1): the new columns are True/False, A to Z, after the others, and the column itself stays; empty cells get a column of their own called "fruit: (empty)" on both engines (pandas dummy_na=True names it "fruit: nan", Polars "fruit: null").
- `table.fill_empty_cells_from` (1): only empty cells take a value (text of only spaces counts as empty); a filled cell never changes, and a key that is in the other table twice stops the word with its name, so it is never unclear which row fills.
- `table.count_rows with_totals=` (1): each total is worked out from the rows themselves, as pandas margins=True does (for an average, the average of all the rows, not of the cells); Polars has no margins, so simplydata works out each total with group_by().agg() on both engines. The total row and column are called "(total)"; rows with an empty key stay, as "(empty)", and count in the totals (pandas leaves them out; this table has none).
- `table.add_group_column into_equal_groups=` (1): the groups are numbered 1 (the smallest values) to 4, counted from 1 as everywhere in simplydata (pandas labels=False counts from 0), or named with names=; the cut points are printed.
- `table.turn_into_text written_like=` (1): the example date is turned into the % codes by a fixed table of its parts (a four-digit year, the number above 12 as the day, month and weekday names); an example whose day is 12 or less is refused, because then the day cannot be told from the month.
- `table.add_column counted_in=` (1): whole units, counted towards zero, as for days: 1 hour 59 minutes is 1 hour (Polars total_hours(); pandas gives 1.98 until it is truncated).
- `table.round_dates_in to_the=` (1): a time exactly half way goes up (10:30 becomes 11:00), as Polars dt.round() does; pandas dt.round() would send it to the even hour (10:00), so the two engines would differ.
- `table.add_zeros_in_front_of` (1): zeros go in front until the text has to_length= characters; a longer text is never cut, a minus or plus sign stays in front, and an empty cell stays empty (str.zfill in pandas and Polars).
- `table.show_rows_with_empty_cells_in` (1): a row is shown when any of its cells (or of the columns= named) is empty, with its row number counted from 1; text of only spaces counts as empty too, and the table does not change.
- `table.show_differences_from` (1): rows are compared in order (row 3 with row 3), and two empty cells count as the same (pandas compare); tables with other columns or another number of rows are not compared cell by cell, and simplydata says how they differ. Polars tables go through pandas compare.
- `table.check_if_same_as` (1): the same means the same columns in the same order, the same rows, the same values and the same kinds (pandas and Polars equals); two empty cells count as the same.
- `table.run_sql` (1): DuckDB runs with no extensions loaded or installed on their own and no access to files or the web, the settings locked, and only one SELECT is run: a query can never fetch, install or write anything;
- `table.run_sql` (2): inside the query the table is called data, and a Polars table comes back as Polars (.pl()); without DuckDB the word stops with the install line (no other SQL engine is used).
- `sdata.run_sql` (1): DuckDB reads the files on this computer, with no extensions loaded or installed on their own (so no web or cloud address can be read), the settings locked, and only one SELECT is run; an address such as https:// or s3:// is refused before DuckDB sees it.
- `table.make_one_table_for_each_group_in` (1): the groups come in the order they are first seen and the rows keep their order; rows with an empty cell in the column make a group of their own (dropna=False), and with one column each table is found by the value itself: tables["Station B"].
- `table.find_summary_of show=` (1): "first" and "last" are the first and last filled value in the order of the rows (pandas groupby first() and last() skip empty cells; Polars drop_nulls() then first() and last()): sort first with sort_by for another order.
- `table.sort_by biggest_first=` (1): a list gives each column its own direction, one True or False for each; pandas' ascending= is the opposite (ascending=[True, False]), Polars' descending= the same; rows that tie keep their order.
- `table.gather_into_rows starts_with=` (1): starts_with=, ends_with= and matches_pattern= choose the columns by their names exactly as keep_columns does (capital letters matter), in table order; one way at a time.
- `table.join_with match=` (1): both tables are sorted stably by the date first, as merge_asof and join_asof need, and the rows go back to this table's order afterwards; a pandas table runs through Polars join_asof too, so ties, repeated dates and empty keys are handled by one rule on both engines;
- `table.join_with match=` (2): "nearest before" takes the last row at or before each date (backward), "nearest after" the first at or after (forward), "nearest" either; within= is the furthest it looks (tolerance), and keep="matching rows" leaves out the rows with nothing near enough.
- `table.save in_table=` (1): in_table= replaces that one table and keeps the other tables of the file (if_exists="replace"), with no row labels (index=False); a .duckdb file is written by DuckDB, with no extensions.
- `nums.find_median` (1): empty values are skipped (np.nanmedian); NumPy's np.median would give nan.
- `nums.find_average` (1): empty values are skipped (np.nanmean); NumPy's np.mean would give nan.
- `nums.find_percentile` (1): NumPy's usual "linear" method, the same as pandas' quantile and R's quantile(type = 7); empty values are skipped (nanpercentile).
- `nums.keep_each_number_that` (1): is_above= means strictly above (>); is_at_least= is >=. An empty value is never above a number, so it goes too (only is_empty=True keeps empty values).
- `nums.show` (1): every number is shown, however many there are (threshold=sys.maxsize); NumPy's own print shortens a list of more than 1000 numbers to its ends with "..." in the middle.
- `nums.show` (2): the numbers are written with commas between them, like a Python list; NumPy's print leaves out the commas.
- `nums.show_first_numbers` (1): the numbers are written with commas between them, like a Python list; NumPy's print leaves out the commas. threshold=sys.maxsize keeps a long list whole, as in show().
- `nums.show_last_numbers` (1): the numbers are written with commas between them, like a Python list; NumPy's print leaves out the commas. threshold=sys.maxsize keeps a long list whole, as in show().
- `nums.get_number_at` (1): positions count from 1, the way people count and the way charts number the x axis: 2 is the second number. NumPy's [ ] counts from 0, so the same number is values[1].
- `nums.count` (1): empty values are counted too: count() is how many places there are. The filled ones alone are count() minus count_empty_numbers(), as np.count_nonzero(~np.isnan(values)).
- `nums.divide_by` (1): dividing by 0 has no answer, so the number becomes empty (nan) and a note says how many; NumPy gives inf (or nan for 0 / 0) with a warning.
- `nums.raise_to_power` (1): whole numbers to a minus power are worked out as decimals; NumPy's np.power on whole numbers stops with an error instead.
- `nums.raise_to_power` (2): 0 to a minus power means dividing by 0, so it becomes empty (nan) with a note; NumPy gives inf. A negative number to a power with decimals, such as 0.5, becomes empty too.
- `nums.round_to` (1): a number exactly halfway goes to the even neighbour (0.5 to 0, 1.5 and 2.5 to 2), as NumPy, pandas and R's round() do, so a run of halves does not push a total up. Excel and the way taught at school round halves away from 0.
- `nums.take_log` (1): the log only exists for numbers above 0, so 0 and negative numbers become empty (nan) with a note; NumPy gives -inf for 0 and nan for a negative number, with a warning.
- `nums.turn_into_running_total` (1): an empty value stays empty and is skipped in the total (1, empty, 3, 6), as pandas cumsum() does. NumPy's cumsum would make every total after it empty, and nancumsum would fill the empty place with the total so far.
- `nums.remove_each_number_that` (1): is_below= means strictly below (<). An empty value is never below a number, so it stays; only is_empty=True removes empty values. values[values >= 10] would drop it.
- `nums.keep_random_numbers` (1): NumPy's random generator (default_rng) with the seed you give, picking without repeats; the old np.random.seed() gives another pick.
- `nums.keep_random_numbers` (2): the numbers kept stay in their order in the list; rng.choice alone gives them in the order they were drawn.
- `nums.remove_duplicate_numbers` (1): each number is kept once, in its first place, and the order stays as it was; empty values count as one value, so the first empty one stays. NumPy's np.unique would sort the numbers instead.
- `nums.keep_numbers_by_position` (1): positions count from 1 and both ends are kept: positions 2 to 4 are three numbers. NumPy counts from 0 and leaves out the end, so the same numbers are values[1:4].
- `nums.remove_numbers_by_position` (1): positions count from 1 and both ends go: positions 2 and 3 are removed. NumPy counts from 0, so they are places 1 and 2.
- `nums.replace_each_number_that` (1): is_above= means strictly above (>). An empty value matches no condition, so it stays empty; only is_empty=True picks the empty values.
- `nums.fill_empty_numbers` (1): each gap is filled on the straight line between the values just before and just after it, spaced by position (linear interpolation).
- `nums.fill_empty_numbers` (2): empty values at the start or the end have a neighbour on one side only, so they stay empty, with a note; np.interp alone would copy the first and last values outward.
- `nums.sort` (1): empty values go last, smallest first or biggest first; np.sort(values)[::-1] would put them first.
- `nums.find_total` (1): empty values are skipped (np.nansum), with a note saying how many; NumPy's np.sum would give nan.
- `nums.find_smallest` (1): empty values are skipped (np.nanmin), with a note saying how many; NumPy's np.min would give nan.
- `nums.find_biggest` (1): empty values are skipped (np.nanmax), with a note saying how many; NumPy's np.max would give nan.
- `nums.find_standard_deviation` (1): the sample standard deviation, dividing by n - 1 (ddof=1), as pandas .std() and R sd(); NumPy's own default divides by n.
- `nums.find_standard_deviation` (2): empty values are skipped (np.nanstd), with a note saying how many; np.std would give nan.
- `nums.count_each` (1): empty values are counted as a value of their own (dropna=False), so the percents are out of all the numbers; pandas' value_counts() leaves them out by default.
- `nums.count_each` (2): percents are rounded to 1 decimal place.
- `nums.count_each` (3): the biggest count comes first; equal counts go smallest number first, with the empty values last, so the order is the same every time.
- `nums.make_number_grid` (1): the numbers fill the grid row after row (NumPy's order "C"): 1 2 3, then 4 5 6.
- `grid.show_first_rows` (1): the numbers are written with commas, like Python lists of rows; NumPy's print leaves out the commas. threshold=sys.maxsize keeps a long grid whole, as in show().
- `grid.show_last_rows` (1): the numbers are written with commas, like Python lists of rows; NumPy's print leaves out the commas. threshold=sys.maxsize keeps a long grid whole, as in show().
- `grid.get_number_at` (1): rows and columns count from 1: row 2, column 3 is the bottom right number here. NumPy counts from 0, so it is g[1, 2].
- `grid.get_row` (1): rows count from 1: get_row(2) is the second row from the top, NumPy g[1]. It comes back as new numbers (a copy), so changing them leaves the grid as it was.
- `grid.get_column` (1): columns count from 1 at the left: get_column(2) is NumPy g[:, 1]. It comes back as new numbers (a copy), so changing them leaves the grid as it was.
- `grid.get_all_numbers` (1): the numbers are read row by row (NumPy's order "C"): 3 5 2, then 8 6 4. Column by column would be g.ravel(order="F").
- `grid.keep_rows_by_position` (1): rows count from 1 and both ends are kept: rows 2 to 3 are two rows. NumPy counts from 0 and leaves out the end, so the same rows are g[1:3].
- `grid.keep_columns_by_position` (1): columns count from 1 at the left and both ends are kept: columns 2 to 4 are three columns, NumPy g[:, 1:4].
- `grid.remove_rows_by_position` (1): rows count from 1: row 1 is the top row, NumPy's row 0.
- `grid.remove_columns_by_position` (1): columns count from 1 at the left: from column 1 with step=2 removes columns 1, 3 and 5, NumPy's columns 0, 2 and 4.
- `grid.replace_each_number_that` (1): the numbers are changed where they are, so the grid keeps its rows and columns (np.where); g[g < 4] would give a flat list instead. An empty value matches no condition, so it stays empty.
- `nums.turn_into_table` (1): the column is called "value" unless you give name=, such as turn_into_table(name="marks").
- `nums.start_chart` (1): the numbers become a table with one column called "value", so chart words name it: draw_histogram(x="value").
- `nums.save` (1): the numbers are written as one column called "value", without row numbers (index=False), so the file reads back as it was.
- `nums.as_numpy` (1): a copy of the numbers as they are now, so changing the array leaves the simplydata numbers as they were.
- `table.compare_averages_of` (1): Welch's t-test, which does not assume both groups have the same spread; SciPy's own default (equal_var=True) is Student's t-test, which does.
- `table.fit_line` (1): the 95 % interval of the slope uses the t distribution with n - 2 degrees of freedom, as R's confint(lm(...)).
- `dist.find_chance_that_value` (1): the chance above a value is the survival function sf(), not 1 - cdf(): it stays accurate far out in the tail.
- `dist.find_percentile` (1): the percent is turned into a share (95 % is 0.95). Above the middle simplydata asks for the value with 5 % above it (isf), which stays accurate far out in the upper tail; below the middle it uses ppf(). For counts it is the smallest count with at least that share at or below it, as R qbinom().
- `table.compare_spreads_of` (1): Levene's test centred on each group's median (the Brown-Forsythe test), the default of SciPy and of R car::leveneTest(); it copes well with values that are not bell-shaped.
- `table.compare_percent_to` (1): the exact binomial test, as R binom.test(); empty cells are left out first.
- `table.compare_percent_to` (2): the exact (Clopper-Pearson) 95 % interval of the percent; interval_by= takes "wilson" or "agresti-coull".
- `table.compare_percent_to` (3): the effect size is Cohen's h, the difference between the two shares on the arcsine scale.
- `table.add_principal_components` (1): only rows with a number in every column are used; the other rows get empty PC cells.
- `table.add_principal_components` (2): every number column is put on the same scale first (mean 0, standard deviation with n - 1), as R prcomp(scale. = TRUE); same_scale=False only centres them (mean 0), as prcomp(scale. = FALSE).
- `table.add_principal_components` (3): the sign of a component is arbitrary and differs between computers, so each one is turned so its biggest weight is positive: the same scores on every computer.
- `table.add_predicted_column` (1): the same model as explain(): least squares for numbers (R fitted(lm(...))); outcome= chooses the others (logistic for yes or no; Poisson, quasi-Poisson or negative binomial for counts; Gamma for positive numbers).
- `table.add_predicted_column` (2): rows with an empty cell in a column the model uses are left out of the fit and stay empty (assign lines the fitted values up by row).
- `table.find_trend_of` (1): the Mann-Kendall test with its continuity correction, run in R itself (trend::mk.test).
- `table.find_trend_of` (2): Sen's slope is the median of the slopes between every pair of readings, with its 95 % interval (SciPy theilslopes gives the same numbers as R trend::sens.slope).
- `table.find_trend_of` (3): readings one calendar month apart give the slope per month, and 12 times it per year.
- `table.find_each_peak_that` (1): apart= is in units of sorted_by, so it becomes a number of readings (0.05 / 0.005 = 10) for SciPy's distance=. simplydata rounds that number to 9 decimals first: 0.05 / 0.005 is 10.000000000000002 in floating point, and SciPy rounds distance= up, to 11 readings, which can lose a peak.
- `table.find_each_peak_that` (2): each peak's width is measured halfway down its prominence (as R pracma::findpeaks), and written in units of sorted_by.
- `table.find_each_peak_that` (3): positions and bases count from 1, as the rows do.
- `table.add_nmds` (1): with_seed=1 is R's own set.seed(1), so the random starts are the same every time.
- `table.add_nmds` (2): at least 20 random starts, and more (up to 100) until the best map has been found twice.
- `table.add_nmds` (3): the counts are used as they are (autotransform = FALSE); vegan's own default may take square roots first, which changes the map without saying so.
- `table.fit_formula` (1): names that are not columns (a, b) are the values to find, and each starts at 1 unless start= says otherwise.
- `table.fit_formula` (2): Levenberg-Marquardt with tight stopping rules, as R nls(); between= limits switch to SciPy's trust region method (method="trf").
- `table.fit_formula` (3): each interval is the value plus and minus t (n - 2 degrees of freedom here) standard errors; R's confint() on nls profiles the likelihood and can differ a little.
- `table.compare_matched_columns` (1): the bootstrap interval of Kendall's W uses R's own random numbers after set.seed(1), so it is the same every time.
- `table.compare_matched_columns` (2): Kendall's W: how alike the rows rank the columns, from 0 (no common order) to 1 (every row the same), with a two-sided 95 % interval.
- `table.compare_matched_columns` (3): the Friedman test, which compares the ranks within each row, so it needs no bell shape (as R friedman.test()); rows with an empty cell are skipped first.
- `table.compare_counts_to` (1): each share of expected= is matched to its value by name and turned into an expected count (share times the rows with a value); SciPy's own default, without expected counts, is the same count for every value.
- `table.compare_counts_to` (2): the effect size is Cohen's w, the distance between the counted and the expected shares (statsmodels chisquare_effectsize).
- `table.compare_shapes_of` (1): three or more groups get the Anderson-Darling k-sample test in its midrank version, which allows for tied values, as R kSamples::ad.test() version 2.
- `table.compare_shapes_of` (2): the p-value comes from shuffling the group labels 9999 times with NumPy's generator seeded with 1 (with_seed=1), so the same seed gives the same p-value; SciPy's own default reads it from a table and caps it at 0.001 and 0.25.
- `table.compare_shapes_of two groups` (1): with tied values the exact p-value comes from R ks.test(), which allows for the ties; SciPy's exact p-value assumes there are none.
- `table.compare_shapes_of two groups` (2): the exact distribution while the two groups make fewer than 10000 pairs of values, as R ks.test(); larger groups use the normal approximation.
- `table.check_if_random_order` (1): each value is above or below the median; values equal to the median (one here) are left out, as R randtests::runs.test() does.
- `table.check_if_random_order` (2): the normal approximation without a continuity correction, the same numbers as R randtests::runs.test(); statsmodels' own default adds one below 50 values, as here.
- `table.compare_correlations` (1): Fisher's z test for the p-value and Zou's interval for the difference; cocor's own default runs every test it knows.
- `sdata.compare_averages` (1): Welch's t-test, which does not assume both groups have the same spread; test_method="student" assumes they do (equal_var=True, var.equal = TRUE).
- `sdata.compare_counts` (1): the chi-square test of independence with Yates' continuity correction for a 2 x 2 table, as R chisq.test().
- `sdata.compare_counts` (2): Cramer's V from the counts without the continuity correction, so it does not shrink with Yates' correction.
- `sdata.compare_risks` (1): the interval of the risk difference is Newcombe's score interval, as R DescTools::BinomDiffCI(method = "score"); statsmodels' own default is another interval (Agresti-Caffo).
- `sdata.compare_risks` (2): the p-value is the chi-square test with Yates' correction, as R prop.test(); p_value_by="exact" gives Fisher's exact test.
- `sdata.compare_rates` (1): without against=, the first group given in names= (here ward B) is the one compared against; the ratio is ward A's rate over ward B's, with R poisson.test()'s exact interval.
- `sdata.compare_rates` (2): the exact conditional test of the rate ratio, as R poisson.test(); statsmodels' own default is a score test.
- `table.compare_to_truth` (1): "yes" in the truth column and "positive" in the test column count as having it and as a positive result; without such words the second value in sorted order counts, as R takes the second level; positive= chooses.
- `table.compare_to_truth` (2): each share gets the exact Clopper-Pearson interval, as R epiR::epi.tests(method = "exact"); statsmodels' own default is the normal-curve interval.
- `table.compare_to_truth a column of numbers` (1): higher scores count as positive (direction = "<"), said before the curve is made; pROC's own default guesses the direction from the data, which flatters a score that works the wrong way round. positive_when="lower" turns it round.
- `table.compare_to_truth a column of numbers` (2): DeLong's interval of the AUC.
- `table.compare_accuracy` (1): higher scores count as positive for both scores (direction = "<"), said before the curves are made, so neither curve is turned round on its own.
- `table.compare_accuracy` (2): DeLong's test for two curves on the same people (paired = TRUE).
- `sdata.compare_to_truth` (1): the four counts are laid out as epiR reads them: the test result in the rows (positive first) and the truth in the columns (has it first).
- `sdata.compare_to_truth` (2): method = "exact": the shares get exact intervals; the likelihood ratios get epiR's intervals on the log scale.
- `table.agreement_between` (1): a square table of counts with every category either rater used, in sorted order, so a category only one rater used ("severe" here) still counts.
- `table.agreement_between` (2): Cohen's kappa without weights, as R irr::kappa2(); near_misses="linear" or "quadratic" counts near misses as partly right (wt="linear", "quadratic").
- `table.agreement_between columns of numbers` (1): two-way, absolute agreement: the raters are a sample of many possible raters, and a rater who always reads higher counts against agreement (ICC(A,1), Shrout and Fleiss ICC(2,1)); irr's own default is the one-way model with consistency.
- `table.agreement_between columns of numbers` (2): the agreement of one rater, not of the average of the raters (of="average of raters").
- `table.limits_of_agreement` (1): the difference is the first column minus the second; the limits are the average difference plus and minus 1.96 standard deviations (with n - 1), each with its t interval.
- `table.limits_of_agreement` (2): Lin's concordance correlation beside the limits, with its interval on Fisher's z scale.
- `table.reliability_of` (1): raw alpha with the items as they are (check.keys = FALSE): an item scored the other way round is not turned round without saying so.
- `table.reliability_of` (2): Feldt's 95 % interval (psych::alpha.ci()).
- `difference_dots` (1): the limits of agreement come from R, with the standard deviation on n - 1, as table.limits_of_agreement() gives them.
- `difference_dots` (2): statsmodels draws the dots and the average difference; sd_limit=0 leaves out its own limits, whose standard deviation uses n.
- `sdata.find_where_smallest` (1): one name with a range: Brent's method on the range, as R optimize(); the method is decided by what you give (start=, rules=, search=) and printed.
- `sdata.find_where_smallest` (2): a tolerance of 1e-10, as R optimize(tol = 1e-10); SciPy's own default stops at 1e-5.
- `sdata.find_where_biggest` (1): a straight-line formula with straight-line rules is a linear program, solved exactly (HiGHS, as R lpSolve::lp(), except that lp() takes every name to be 0 or more, see (2)); the biggest value is the smallest value of minus the formula, and a rule with >= is turned into <= by changing its signs.
- `sdata.find_where_biggest` (2): the names may be any number unless a rule or between= limits them: simplydata passes bounds=(None, None), while SciPy linprog's own default (0, None) and R lp() take every name to be 0 or more; here y may go down to -1, which gives 13 instead of 12.
- `sdata.solve` (1): the range is cut into 1000 steps and every step where the two sides cross is searched, so every solution that crosses is found (as R rootSolve::uniroot.all()), not only one.
- `sdata.solve` (2): Brent's method in each step with a tolerance of 1e-12, as R uniroot(tol = 1e-12); SciPy's own default (2e-12) gives the same roots here.
- `table.values_at` (1): several values at the same place (country A in 2002) are averaged first, as R approx(ties = mean).
- `table.values_at` (2): straight lines between neighbours (NumPy interp, as R approx()), and places outside the known points stay empty, as R approx(rule = 1); NumPy's own default carries the end value on, which outside="nearest end" gives.
- `table.make_map_of` (1): the known points form a full grid (every east with every north), so they are read as a grid; scattered points are joined by flat triangles instead (SciPy griddata, as R interp::interp()).
- `table.make_map_of` (2): straight lines along each direction (bilinear interpolation, RegularGridInterpolator's method="linear").
- `table.make_map_of` (3): steps= evenly spaced places from the smallest to the biggest known value of each column, every combination, the first column changing slowest.
- `table.compare_distributions_for` (1): each distribution is fitted by maximum likelihood; the families for positive values start at 0 (floc=0), as R MASS::fitdistr() and fitdistrplus fit them, not with SciPy's own extra location.
- `table.compare_distributions_for` (2): AIC counts only the parameters that were fitted, and the rows are sorted by it, smallest (best) first.
- `nums.fit_distribution` (1): maximum likelihood with the gamma starting at 0 (floc=0), as R MASS::fitdistr(x, "gamma"); SciPy's own fit also moves the start.
- `nums.fit_distribution` (2): the second parameter is the rate (1 / SciPy's scale), as R's dgamma(shape, rate).
- `dist.find_density_at` (1): the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).
- `dist.find_cut_off` (1): the value with a chance above it is the inverse survival function isf(), not ppf(1 - chance): it stays accurate far out in the tail (1 - 1e-9 cannot be stored exactly). with_chance_below= uses ppf().
- `dist.find_middle_range` (1): equal tails: half of what is left (2.5 % here) is cut off at each end, not the shortest range.
- `dist.find_average` (1): the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).
- `dist.find_median` (1): the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).
- `dist.find_standard_deviation` (1): the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).
- `dist.find_variance` (1): the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).
- `dist.show_summary` (1): the kurtosis is the excess kurtosis (0 for the normal distribution), as SciPy gives it.
- `dist.make_random_numbers` (1): NumPy's generator (PCG64) seeded with with_seed=1, so the same seed gives the same numbers; R's rnorm() uses another generator, so its numbers differ.
- `dist.draw_chart` (1): the curve runs from the 0.1 % point to the 99.9 % point (the ends of the possible values where they are closer), at 200 evenly spaced places.
- `dist.turn_into_table` (1): one row with the parameters under their plain names (R's names, shape and rate; underscores become spaces), not SciPy's (a, scale); parameters not given are left out.
- `table.find_principal_components_of` (1): every number column is put on the same scale first (mean 0, standard deviation with n - 1), as R prcomp(scale. = TRUE); same_scale=False leaves the columns as they are.
- `table.find_principal_components_of` (2): the standard deviation of each component divides by n - 1, as R prcomp()$sdev.
- `table.find_principal_components_of` (3): the sign of a component is arbitrary and differs between computers, so each one is turned so its biggest weight is positive.
- `table.use_survey_design` (1): a stratum with only one cluster is centred at the overall average (survey.lonely.psu = "adjust"); survey's own default stops with an error.
- `table.use_survey_design` (2): clusters are counted within their stratum (nest = TRUE): a district that turns up in two school types is two clusters; without it survey refuses these data.
- `table.use_survey_design` (3): the intervals use t on the design's degrees of freedom (degf(design), here 159), not survey's own normal-curve confint().
- `table.explain weights=` (1): precision weights, as R lm(weights =): statsmodels WLS; for the other outcomes GLM(var_weights=). Not freq_weights, which would change the degrees of freedom.
- `table.explain outcome="yes or no (overdispersed)"` (1): quasi-binomial as R glm(family = quasibinomial): the shares, with the tries as var_weights and the Pearson dispersion (scale="X2"). A two-column endog would give statsmodels another dispersion.
- `table.explain matched_by=` (1): conditional logistic regression with the exact conditional likelihood, as R survival::clogit() (its default method = "exact"); no intercept, each pair compared only with itself.
- `table.explain matched_by=` (2): fitted by Newton's method to the end; statsmodels' default (BFGS) stops a little short of the best estimates.
- `table.explain show="risk ratios"` (1): modified Poisson regression (Zou 2004): a Poisson model for the 0/1 column with robust (HC0) standard errors, as R glm(family = poisson) with sandwich::vcovHC(type = "HC0"); it always converges, where log-binomial (test_method="log-binomial") often does not.
- `table.explain test_method="log-binomial"` (1): a binomial model with a log link, as R glm(family = binomial(link = "log")); when it does not converge (a predicted chance reaches 1), simplydata says so and points to the default modified Poisson regression.
- `table.explain giving_outliers_less_weight=` (1): Huber's weights with k = 1.345, the default of statsmodels and of R MASS::rlm().
- `table.explain giving_outliers_less_weight=` (2): the scale by the median absolute deviation and Huber's H1 covariance; R's summary(rlm) uses a slightly different small-sample correction, so its standard errors differ in the third digit.
- `table.explain with_knots=` (1): the knots at the quantiles of all the values, as R splines::ns() places them; patsy's own df= would take the quantiles of the distinct values (mgcv's rule) and give another curve.
- `table.explain with_knots=` (2): a natural cubic spline without its constant (constraints="center"): the same curves as R lm(marks ~ splines::ns(hours, df = 4) + breakfast), so the fitted values and the other effects are R's.
- `table.explain show="standardised effects"` (1): z-scores with the standard deviation of n - 1 (pandas' std(), R's sd()), on the rows the model uses.
- `table.explain show="standardised effects"` (2): the model fitted again on the z-scores, as R effectsize::standardize_parameters(method = "refit"); group columns stay as they are, and the outcome is standardised only for numbers.
- `table.explain interval_by="bootstrap"` (1): the rows are drawn again whole (case resampling), and the same model is fitted to each new table.
- `table.explain interval_by="bootstrap"` (2): BCa intervals (bias-corrected and accelerated), as R boot::boot.ci(type = "bca"); with_seed= fixes the random draws.
- `table.explain interval_by="profile"` (1): profile-likelihood intervals, R's confint() of a glm (in stats since R 4.4; before, in MASS); safer than Wald intervals with few rows or effects far from 1.
- `table.explain p_value_by="likelihood ratio"` (1): each column left out in turn and the deviances compared (chi-square, 1 df), as R drop1(m, test = "LRT"); a group column is tested whole, and a column inside an interaction is not tested alone.
- `table.explain crossed_with=` (1): two groupings crossed with each other, (1 \| school) + (1 \| class), fitted by REML as lme4's default; statsmodels MixedLM takes one grouping (or groups inside groups), so R fits it.
- `table.explain outcome="counts with many zeros that vary a lot"` (1): zero-inflated negative binomial regression with a logistic zero part and the same columns in both parts, pscl::zeroinfl(dist = "negbin")'s defaults.
- `table.explain outcome="counts in two steps"` (1): a hurdle model: a logistic part for zero or not (pscl's binomial zero part, the textbook form) and a Poisson part cut off at 1 for the counts above 0.
- `table.explain zero_part_using=` (1): the zero part gets its own columns, pscl's y ~ x \| z; without zero_part_using= both parts use the columns of using=.
- `table.fit_dose_response` (1): the 4 parameter log-logistic curve, the usual one in ecotoxicology (drc's LL.4); of_kind= chooses another.
- `table.fit_dose_response` (2): the ED50 with its delta-method interval: drc's ED() gives no interval unless asked (interval = "none" is its default).
- `table.fit_dose_response` (3): a tighter stopping rule than drc's default (relTol 1e-7), so that the fit has converged; the method is the same.
- `fit_dose_response` (1): the 4 parameter log-logistic curve (drc's LL.4), with the same tighter stopping rule, as table.fit_dose_response.
- `fit_dose_response` (2): the curve is drawn over 300 doses spaced evenly on a log scale (and dose 0), so it stays smooth on a log dose axis too; the ED50 and its delta-method interval go in the legend.
- `table.find_best_power_of` (1): the power's 95 % interval from the profile likelihood (alpha=0.05); without alpha= SciPy gives no interval.
- `table.fit_line test_method="theil-sen"` (1): SciPy's alpha= is the confidence level (0.95), not the error rate.
- `table.fit_line test_method="theil-sen"` (2): the intercept is median(y) - slope * median(x) (Conover; SciPy's default); R mblm takes the median of y - slope * x instead.
- `table.fit_line test_method="standardised major axis"` (1): smatr's own 95 % intervals (Warton et al. 2006); test_method="major axis" is method = "MA".
- `table.fit_line test_method="deming", y_error_over_x_error=` (1): mcr's error.ratio is the error variance of x over that of y, the other way round from y_error_over_x_error=, so it gets 1 / 4.
- `table.fit_line test_method="deming", y_error_over_x_error=` (2): mcr's analytical intervals; its default (bootstrap) is random and differs from run to run.
- `table.fit_line test_method="passing-bablok"` (1): Passing and Bablok's own rank-based intervals (mcr's "analytical" for PaBa); mcr's default bootstrap is random.
- `table.fit_line with_bends=` (1): a continuous line: it bends, it does not jump (segmented's model); seed 1 fixes segmented's random restarts.
- `table.fit_line with_bends=` (2): Davies' test of "no bend at all": the bend's own p-value is not valid, because the data chose where it is.
- `table.fit_line changes_at=` (1): the change starts at the point itself: rows at 10 or later count as after.
- `table.fit_curve of_kind="logistic growth"` (1): start values: simplydata takes them from R's self-starting model (stats::getInitial()), or searches the whole range without R; the least-squares answer is the same.
- `table.explain for_percentile=` (1): R quantreg's exact simplex (Barrodale-Roberts); statsmodels QuantReg gives the same line to about 1e-7 but none of R's standard errors.
- `table.explain for_percentile=` (2): standard errors by "nid" for every number of rows (R's default below 1001 rows is "rank", intervals only).
- `table.explain changes_at=` (1): the change starts at the point itself: rows at 10 or later count as after.
- `table.add_smoothed_column test_method="loess", interval=` (1): R loess's own defaults: span 0.75 (smoothness=), local curves of degree 2, no robustness steps.
- `table.add_smoothed_column test_method="loess", interval=` (2): the band uses loess's own degrees of freedom, as R's predict.loess intervals do.
- `draw_smooth_line test_method="loess", with_confidence_band=` (1): R loess's own defaults: span 0.75, local curves of degree 2, no robustness steps (not lowess).
- `table.find_columns_that_predict` (1): the random split into 10 parts is made in R itself (with_seed=1 is set.seed(1)), so R's own random numbers give the same parts.
- `table.find_columns_that_predict` (2): the lasso (alpha = 1) with 10 parts; test_method="elastic net" is alpha = 0.5.
- `table.find_columns_that_predict` (3): the penalty is lambda.1se, the largest within one standard error of the best (fewer columns, steadier); simplydata names it, so a change of glmnet's default cannot change the answer.
- `table.find_group_levels_of` (1): condVar = TRUE: each level comes with its conditional variance; without it ranef() gives no uncertainty.
- `table.find_group_levels_of` (2): the 95 % interval is the level plus and minus 1.96 conditional standard deviations, as lattice::dotplot(ranef(m, condVar = TRUE)) draws it.
- `draw_interaction_lines` (1): 95 % t intervals of each average, as R t.test(); seaborn's own default is a bootstrap interval, which changes from run to run.
- `draw_interaction_lines` (2): the groups are moved a little apart (dodged) so their bars do not hide each other.
- `table.explain spread_changes_with=` (1): REML, nlme's default, for the effects.
- `table.explain spread_changes_with=` (2): a group column gives each group its own spread (varIdent); a number column would give a spread that grows as a power of it (varPower).
- `table.explain neighbours_alike_in_order_of=` (1): evenly spaced values give the AR(1) correlation (corAR1), each step one step apart; uneven gaps give corCAR1, which allows for the size of each gap.
- `table.compare_models using=[[...], [...]]` (1): every value estimated counts, the residual spread too, as R logLik(); statsmodels' own aic leaves it out (a difference of 2).
- `table.compare_models using=[[...], [...]]` (2): AICc when there are fewer than 40 rows per value estimated (Burnham & Anderson 2002), else AIC.
- `table.compare_models check_on_left_out_rows=True` (1): with_seed=1 is set.seed(1) in R, so R's own random numbers make the parts.
- `table.compare_models check_on_left_out_rows=True` (2): K = 10 parts: cv.glm's own default leaves out one row at a time.
- `table.find_model_averages_of comparing="each with the first"` (1): each group against the first group (in sorted order, or the first of in_order=).
- `table.find_model_averages_of comparing="each with the first"` (2): emmeans' own adjustment for this method (dunnettx), printed by simplydata.
- `table.find_model_averages_of within_each_group_in=` (1): the interaction test comes first (emmeans joint_tests()), and the comparisons within each group after it: compare the groups with the interaction test, not by which simple effects have small p-values (Gelman & Stern 2006).
- `table.find_model_averages_of over_range_of=` (1): 50 evenly spaced values from the smallest to the largest hours.
- `table.find_model_averages_of over_range_of=` (2): the other columns as emmeans holds them: numbers at their average, groups counted equally.
- `table.compare_averages_of grouped_by=` (1): the treatment is tested against the variation between rats (Error(rat)), not between readings: the readings of one rat are not independent.
- `table.compare_averages_of for_each_group_in= with a list of columns` (1): Pillai's trace first, the one R summary(manova()) prints by default and the safest when groups differ in size or spread.
- `table.add_time_and_event_columns` (1): follow-up ends at the first of the end dates; an empty date does not end it.
- `table.add_time_and_event_columns` (2): the event counts when its date came first or on the same day as the others.
- `table.find_risk_over_time` (1): the first level of the factor is the censored state (followed without either event); the competing event is a state of its own, never counted as censored.
- `table.find_risk_over_time` (2): survfit with a factor event gives the Aalen-Johansen estimate and its log-scale 95 % interval.
- `draw_risk_curves` (1): with nothing competing, the chance of having had the event is 1 minus the Kaplan-Meier curve, from 0 at time 0 to the last time followed (R plot(survfit(...), fun = "event")).
- `table.find_survival_over_time at_time_points=` (1): the curve is flat between event times, so the survival at 365 is the one of the last event time at or before 365 (R summary(survfit(), times =)).
- `table.find_survival_over_time test_method="life table"` (1): the intervals start at the times given, and the last one is open (NA).
- `table.find_survival_over_time test_method="life table"` (2): simplydata counts the rows lost and with the event in each interval; lifetab does the rest, with the actuarial assumption (lost rows count as followed for half the interval).
- `table.find_survival_over_time allowing_for=` (1): direct adjustment: each row's curve is predicted as if in each group and averaged over all rows, never the curve of an "average" row; conf_int = TRUE (adjustedCurves' own default is FALSE).
- `table.find_survival_over_time followed_from=` (1): each row is at risk only after its start (left truncation, R Surv(start, stop, event)).
- `table.find_survival_over_time average_time_up_to=` (1): rmean = 700, the horizon you name: without it survival's print uses its own upper limit.
- `table.compare_survival allowing_for=` (1): strata=: the groups are compared within each stratum and the results added up, as R survdiff(... + strata()).
- `table.compare_survival followed_from=` (1): entry=: each row counts as at risk only after its start. R survdiff takes no start times; the same test in R is the score test of coxph(Surv(start, stop, event) ~ group, ties = "exact") (coxph()$score), which agrees to about 1e-11 (validation/report.md).
- `table.compare_survival average_time_up_to=` (1): arm 1 is the second group in sorted order, so the difference is the second minus the first.
- `table.compare_survival average_time_up_to=` (2): tau = 700, the horizon you name: survRM2's own default is the shortest of the groups' last times.
- `table.compare_survival competing_with=` (1): the event asked about is code 1 and the competing event code 2; other values are censored (code 0).
- `table.compare_survival competing_with=` (2): Gray's test of the chance of each event over time (cmprsk::cuminc), not a log-rank test with the competing event censored.
- `table.explain_survival allowing_for=` (1): strata=: each treatment group has its own baseline risk (R coxph(... + strata(treatment))), so there is no hazard ratio for it.
- `table.explain_survival followed_from=` (1): entry=: each row is at risk only after its start (R coxph(Surv(start, stop, event) ~ ...)). statsmodels counts a row as at risk at an event time equal to its start and R does not, so when a row starts at an event time (one person split into rows) simplydata fits the model with R coxph, and says so.
- `table.explain_survival competing_with=` (1): cause-specific: a Cox model of the event asked about, with the competing event counted as the end of follow-up (the risk at any moment among those still free of both events).
- `table.explain_survival test_method="fine-gray"` (1): Fine and Gray's model with crr's robust (sandwich) standard errors; failcode is the event asked about.
- `table.explain_survival distribution=` (1): the accelerated failure time model of survreg: time ratios exp(coefficient), never hazard ratios.
- `draw_survival_curves followed_from=` (1): entry=: each row is at risk only after its start (delayed entry).
- `draw_survival_curves allowing_for=` (1): direct adjustment: each row's curve predicted in each group, then averaged over all rows.
- `draw_risk_curves competing_with=` (1): the competing event is a state of its own (Aalen-Johansen), never counted as censored.
- `table.combine_studies` (1): risk ratios for counts, and a study with no events in either group left out (drop00 = TRUE), as Cochrane reviews do; show= chooses odds ratios or risk differences.
- `table.combine_studies` (2): random effects with REML, metafor's default and the best of the usual estimators of the between-study spread (Veroniki et al. 2016).
- `table.combine_studies` (3): Hartung-Knapp intervals and p-values with the ad hoc rule: never narrower than the normal (z) interval; interval_by="normal" gives the classic interval.
- `table.combine_studies` (4): the result shown back as a ratio, with the prediction interval (t with k - 1 degrees of freedom under Hartung-Knapp).
- `table.combine_studies` (5): a tighter stopping rule than metafor's default (1e-5) for the iterative between-study spread (REML, Paule-Mandel), so that it has converged; the method is the same.
- `draw_funnel_plot` (1): the pseudo 95 % limits: SciPy's 95 % interval around the combined effect at the largest standard error (lognorm for ratios, so on the log scale); with the top of the funnel at the combined effect both limits are straight lines, as metafor funnel() draws them.
- `draw_funnel_plot` (2): the line is the combined effect of combine_studies (random effects, REML).
- `draw_funnel_plot` (3): ratios on a log scale, with the standard error of the log ratio downwards (0 at the top).
- `table.combine_studies estimates=` (1): a column with "ratio" in its name is combined on the log scale; metafor conv.wald() turns each estimate and its 95 % interval into a log ratio and its variance (estimates_are_ratios= decides otherwise).
- `table.combine_studies estimates=` (2): the combined effect shown back as a ratio.
- `table.combine_studies test_method=` (1): DerSimonian-Laird's between-study spread (metafor "DL"); "paule-mandel" is "PM" and "common effect" is "EE" (metafor 4 renamed "FE").
- `table.combine_studies test_method="mantel-haenszel"` (1): Mantel-Haenszel weights, a common-effect method: there is no between-study spread and no prediction interval (compare_risks(allowing_for=) gives the same from raw rows).
- `table.combine_studies test_method="peto"` (1): Peto's one-step odds ratio, a common-effect method for rare events; it gives odds ratios only.
- `table.combine_studies interval_by=` (1): the normal (z) interval and p-value, as in older meta-analyses; the default is Hartung-Knapp (test = "adhoc").
- `table.combine_studies for_each_group_in=` (1): each subgroup its own random-effects model, with its own between-study spread; for this test each subgroup's estimate with its normal (z) standard error, as RevMan and R meta do (the subgroups' own intervals stay Hartung-Knapp).
- `table.combine_studies for_each_group_in=` (2): the test of the difference between the subgroup estimates (a common-effect meta-regression on the subgroup), not metafor's rma(mods = ~ group), which assumes one spread for all.
- `table.combine_studies using=` (1): a meta-regression: the slope of the log risk ratio per unit of each column, with Hartung-Knapp intervals; R-squared says how much of the between-study spread the columns account for.
- `sdata.find_how_many_needed` (1): a two-sided test counts only the chance of finding the difference in the right direction, as R power.t.test() (strict = FALSE): one side at half the significance level.
- `sdata.find_how_many_needed` (2): the number is rounded UP to a whole number.
- `sdata.find_chance_of_finding` (1): one side at half the significance level, as R power.t.test() (strict = FALSE).
- `sdata.find_how_many_needed interval_width=` (1): the Wilson interval, given by name: presize's method= is a list of four and it warns when none is chosen.
- `sdata.find_how_many_needed for_test=` (1): events first, by Schoenfeld's (1983) formula for the log-rank test, two groups of the same size.
- `sdata.find_how_many_needed for_test=` (2): people = events / the share of everyone expected to have the event (Schoenfeld; Hsieh & Lavori 2000), with the group a 0/1 column half of the people have (p = 0.5).
- `sdata.find_how_many_needed test_method=` (1): Freedman's (1982) formula, two groups of the same size (k = 1); the first percent is the group whose hazard is effect_size= times the second's.
- `sdata.find_how_many_needed using=` (1): FTestPowerF2, statsmodels' class with the degrees of freedom named the right way round (as R pwr::pwr.f2.test(), Cohen 1988 chapter 9).
- `sdata.find_how_many_needed using=` (2): the rows are the denominator degrees of freedom plus the columns plus 1.
- `sdata.find_how_many_needed outcome=` (1): one bell-shaped (normal) column; the odds ratio is per standard deviation of it, and percents= is the percent with the outcome at its average.
- `sdata.find_how_many_needed outcome=` (2): Demidenko's (2007) formula with the variance correction: 337 in the G*Power manual's example, as G*Power gives (Hsieh's formula gives 317).
- `sdata.find_how_many_needed in_clusters_of=` (1): the design effect 1 + (m - 1) x ICC (Donner & Klar 2000): simplydata's own arithmetic, the one line it adds to the package's answer.
- `sdata.find_how_many_needed in_clusters_of=` (2): the independent number times the design effect, rounded up; then whole clusters.
- `sdata.find_how_many_needed based_on=` (1): seeded (with_seed=1), so the answer repeats.
- `sdata.find_how_many_needed based_on=` (2): the very test compare_averages_of(based_on="ranks") runs: Mann-Whitney, exact below 50 values in each group, else the normal approximation with continuity correction.
- `sdata.find_how_many_needed based_on=` (3): significance given (SciPy's default is 0.01), 10000 tries drawn 1000 at a time; simplydata reads such powers for a range of numbers and takes the smallest that reaches power= (here 68).
- `sdata.find_chance_of_finding drawing_from=` (1): seeded (with_seed=1, tries=10000, drawn 1000 at a time), so the answer repeats.
- `sdata.find_chance_of_finding drawing_from=` (2): the test compare_averages_of runs: Welch's t-test (based_on="ranks" gives Mann-Whitney).
- `sdata.find_chance_of_finding by_running=` (1): your function, run once per seed: 1, 2, ... 500 (with_seed=1, tries=500).
- `sdata.find_chance_of_finding by_running=` (2): the p-values below significance= are counted, as SciPy stats.power counts them.
- `table.add_diversity_columns` (1): Shannon with the natural log (vegan's base = exp(1)); scikit-bio changed its default base from 2 to e in 0.6.1, so older numbers may be in bits.
- `table.add_diversity_columns` (2): Simpson as 1 - the sum of squared shares (the Gini-Simpson index): the chance that two counts drawn at random are of different kinds.
- `table.add_diversity_columns at_total_count=` (1): rarefaction as the expected richness in a sample of that many counts (Hurlbert 1971), not a random subsample, so the answer is the same every time.
- `table.add_diversity_columns at_total_count=` (2): a row with fewer counts than that in all gets an empty cell (vegan gives its observed richness), and the printout names it.
- `table.add_diversity_columns show="chao1"` (1): the bias-corrected Chao1 (Chao 1987) with its standard error, as vegan::estimateR gives it; it needs raw counts, because it leans on the kinds seen once or twice.
- `table.add_diversity_columns show="hill numbers"` (1): Hill numbers of order 0, 1 and 2 (richness, exp(Shannon), inverse Simpson): each is a number of equally common kinds, so they can be compared directly (Jost 2006).
- `draw_richness_curves` (1): about 50 points on the shortest curve: the step is a 50th of the smallest row total.
- `draw_richness_curves` (2): the curves are vegan's own (rarecurve with tidy = TRUE): the expected richness of vegan::rarefy at each step, up to each row's total.
- `draw_richness_curves` (3): a dotted line at the smallest row total: richness can be compared at or below it.
- `table.add_log_ratio_columns` (1): zeros replaced by estimated small values: zCompositions' Bayesian-multiplicative replacement (GBM), which estimates each from the data and keeps the ratios of the other parts; only when there are zeros.
- `table.add_log_ratio_columns` (2): z.delete = FALSE: no column is deleted (cmultRepl's default deletes columns that are more than 80 % zeros, with only a message); simplydata refuses columns with fewer than 2 values above 0 instead, with the line that merges them.
- `table.add_log_ratio_columns` (3): clr: the log of each value over the row's geometric mean, R compositions::clr.
- `table.add_log_ratio_columns test_method="alr"` (1): the reference is the column named in against= ("sul1", the 5th), R compositions::alr(ivar =).
- `table.add_log_ratio_columns test_method="ilr"` (1): the default basis of R compositions::ilr(); another basis (scikit-bio's) gives other numbers but the same distances between rows, and the printout says so.
- `table.add_log_ratio_columns zeros_replaced_by="adding 1"` (1): 1 added to every count before the logs (vegan's pseudocount), only when there are zeros; the printout says the answer depends on the 1 you added.
- `table.add_principal_coordinates` (1): classical scaling of the Bray-Curtis distances, R stats::cmdscale with the eigenvalues, so the printout can say how many are negative.
- `table.add_principal_coordinates` (2): each axis turned so its biggest value is positive: the sign of an axis is arbitrary, and this gives the same answer on every computer.
- `table.add_principal_coordinates measure="aitchison"` (1): zeros replaced by estimated small values first (GBM, no column deleted), as vegdist refuses zeros for the Aitchison distance.
- `table.add_principal_coordinates measure="aitchison"` (2): the Aitchison distance: the straight-line distance between the rows' clr log ratios.
- `table.add_principal_coordinates measure="aitchison"` (3): each axis turned so its biggest value is positive.
- `table.explain_profiles_of` (1): distance-based RDA on Bray-Curtis distances, the same distance as compare_profiles_of.
- `table.explain_profiles_of` (2): the adjusted R squared first (Peres-Neto et al. 2006): the unadjusted one grows with every column.
- `table.explain_profiles_of` (3): 999 permutations after set.seed(1).
- `table.explain_profiles_of measure="hellinger"` (1): RDA on the Hellinger-transformed counts (square roots of the shares; Legendre & Gallagher 2001), never on raw counts.
- `table.explain_profiles_of measure="hellinger"` (2): each column tested after all the others (by = "margin"), so the order of using= does not matter; anova's own default tests in sequence.
- `table.explain_profiles_of test_method="canonical correspondence"` (1): CCA on the counts themselves (chi-square distances), so no measure=.
- `table.explain_profiles_of test_method="canonical correspondence"` (2): CCA's adjusted R squared comes from permutations (vegan), after set.seed.
- `table.explain_profiles_of allowing_for=` (1): a partial analysis: site is taken into account first (vegan Condition()) and not tested, the same meaning allowing_for= has on the other words.
- `table.find_correlation_between_profiles` (1): measurements (not counts) in second= get straight-line distances after each column is put on the same scale; counts would get measure=.
- `table.find_correlation_between_profiles` (2): the Pearson Mantel correlation with 999 permutations after set.seed(1).
- `table.find_correlation_between_profiles test_method="procrustes"` (1): PROTEST on the first two principal coordinates of each set: the Procrustes correlation and its permutation p-value.
- `table.compare_profiles_of test_method="anosim"` (1): Clarke's ANOSIM R from ranked distances, 999 permutations after set.seed(1).
- `table.compare_profiles_of show="contributions"` (1): SIMPER without permutation p-values (permutations = 0): Warton et al. 2012 show they mislead; the table is a description, not a test.
- `table.compare_profiles_of measure="aitchison"` (1): zeros replaced by estimated small values (GBM, no column deleted), then the Aitchison distance.
- `table.find_distances_between_rows measure="aitchison"` (1): zeros replaced by estimated small values first (GBM, no column deleted); vegdist refuses zeros for this distance.
- `table.find_distances_between_rows measure="aitchison"` (2): the Aitchison distance: the straight-line distance between the rows' clr log ratios.
- `table.add_clusters how_many="automatic"` (1): average linkage, simplydata's choice for Bray-Curtis distances (Ward assumes straight lines).
- `table.add_clusters how_many="automatic"` (2): the average silhouette width (R cluster::silhouette) for 2 to 10 clusters.
- `table.add_clusters how_many="automatic"` (3): the number with the largest width; on a tie, the fewer clusters.
- `table.add_clusters how_many="automatic"` (4): the clusters numbered 1, 2, 3 in the order they first appear in the table.
- `table.add_clusters measure=` (1): the counts as they are (no rescaling) for Bray-Curtis distances.
- `table.add_clusters measure=` (2): average linkage, chosen for Bray-Curtis (Ward is refused with it), the same as draw_cluster_tree.
- `draw_cluster_tree` (1): average linkage for Bray-Curtis distances, the same choice as table.add_clusters, so the tree matches the clusters.
- `table.add_axes_that_separate_groups` (1): MASS's default prior chances: the group shares in the data.
- `table.add_axes_that_separate_groups` (2): each axis turned so its biggest value is positive.
- `table.add_correspondence_axes` (1): correspondence analysis as ter Braak's CA in vegan (cca with no explaining columns).
- `table.add_correspondence_axes` (2): row scores with scaling = "sites" (vegan's default is "species").
- `table.add_correspondence_axes` (3): each axis turned so its biggest value is positive.
- `table.add_correspondence_axes show="numbers"` (1): each axis's eigenvalue and share of the inertia as vegan's summary(eigenvals()) gives them.
- `table.add_correspondence_axes show="numbers"` (2): the total inertia is vegan's tot.chi, the sum of all the eigenvalues.
- `table.find_hidden_factors_behind` (1): with_seed=1: parallel analysis compares the data with random data, and the oblimin rotation starts from random numbers too, so R's random numbers are seeded and the answer repeats.
- `table.find_hidden_factors_behind` (2): how_many="automatic": parallel analysis (Horn 1965) keeps the factors that stand out more than in random data of the same size; the 'eigenvalue above 1' rule finds too many (Zwick & Velicer 1986).
- `table.find_hidden_factors_behind` (3): test_method="minres", psych's default: it gives an answer where maximum likelihood can fail (base R factanal uses maximum likelihood).
- `table.find_hidden_factors_behind` (4): rotation="oblimin" (through GPArotation): the factors may correlate, as they usually do in real data (base R factanal uses varimax, which keeps them uncorrelated).
- `table.find_hidden_factors_behind how_many=` (1): a number of factors chosen by you: no parallel analysis (the seed is still set, for the oblimin rotation).
- `table.find_hidden_factors_behind test_method=` (1): maximum likelihood, as base R factanal fits; "principal axis" is psych's fm = "pa".
- `table.find_hidden_factors_behind rotation=` (1): varimax (stats::varimax, as R factanal uses) keeps the factors uncorrelated; "promax" lets them correlate, "none" leaves them unrotated.
- `table.check_hidden_factors` (1): maximum likelihood; with empty cells simplydata adds missing = "ml", which uses every value given, where lavaan's own default ("listwise") would leave those rows out without a word.
- `table.check_hidden_factors formula=` (1): formula= takes the model in lavaan's own syntax and runs lavaan::sem(), so hidden factors can explain each other (a structural equation model).
- `table.check_hidden_factors formula=` (2): the paths are shown standardised (both sides on a scale of standard deviations), as the loadings are.
- `table.find_average_direction_of` (1): the average from 0 up to the full turn; R circular::mean.circular gives the same direction from -180 to 180.
- `table.find_average_direction_of` (2): the circular standard deviation sqrt(-2 ln R), in the units of the column, as R sd.circular (which gives radians).
- `table.compare_shape_to shape="even around the circle"` (1): the units are always given to R circular, which reads plain numbers as radians without a word.
- `table.find_autocorrelation_of x=` (1): every pair of places is a neighbour (all pairs, not a distance band).
- `table.find_autocorrelation_of x=` (2): weights 1 / distance, each row's weights summing to 1 (row-standardised): nearer pairs count more.
- `table.find_autocorrelation_of x=` (3): a permutation p-value from 999 shuffles after set.seed(1), one-sided (nearby places more alike), spdep's default.
- `table.find_autocorrelation_of nearest=` (1): each place's k nearest places count alike, the others not at all, each row's weights summing to 1.
- `table.find_autocorrelation_of on_globe=` (1): longitude and latitude as places on the earth (crs 4326): great-circle distances in km.
- `table.find_variogram_of` (1): gstat's own bins: up to a third of the diagonal of the area, in 15 bins.
- `table.find_variogram_of` (2): the spherical curve, fitted with gstat's own start values (vgm with no numbers) and its default weighted least squares (fit.method = 7).
- `draw_variogram` (1): the fitted curve at 200 distances up to the largest bin, from gstat::variogramLine.
- `table.find_return_levels_of` (1): the GEV by maximum likelihood (extRemes's default method).
- `table.find_return_levels_of` (2): profile-likelihood intervals (Coles 2001, section 3.3.3): the normal approximation of return.level() is too narrow and too symmetric for long return periods; the search range starts at the normal interval (R extRemes needs one).
- `table.find_return_levels_of values_above=` (1): the readings per year from the dates: daily readings are time.units = "days" (365.25 a year).
- `table.find_return_levels_of values_above=` (2): profile-likelihood intervals (Coles 2001, section 3.3.3): the normal approximation of return.level() is too narrow and too symmetric for long return periods; the search range starts at the normal interval (R extRemes needs one).
- `table.find_return_levels_of values_above=` (3): a tighter stopping rule for optim (reltol 1e-12) than its default, so that the fit has converged; the method is the same.
- `draw_threshold_check` (1): the mean excess at extRemes::mrlplot's own 100 thresholds, drawn from the lowest to the highest threshold asked for.
- `draw_threshold_check` (2): the shape at 10 thresholds from the lowest to the highest, as extRemes::threshrange.plot.
- `table.fit_distribution_to distribution="gev"` (1): the shape kept in the sign of extRemes and Coles (xi); SciPy's genextreme, which simplydata uses for the numbers, takes c = -xi.
- `table.fit_distribution_to distribution="generalised pareto"` (1): the shape in the sign of extRemes, Coles and SciPy's genpareto (xi), with the threshold at 0: the values are the amounts above a threshold.
- `table.find_percentile_of weights=` (1): frequency weights: each row repeated as often as its weight, so weights of 1 change nothing (as R quantile(rep(x, w)) and Hmisc::wtd.quantile).
- `table.find_percentile_of weights=` (2): the linear rule (R type 7), the same test_method= as without weights.
- `table.find_percentile_of weight_kind="analytic"` (1): the weighted inverted CDF, the only NumPy rule with weights (as R survey::svyquantile(qrule = "math")): a step, not a line between values.
- `table.find_median_of weights=` (1): frequency weights: each row repeated as often as its weight (weight_kind="analytic" gives the weighted inverted CDF instead).
- `table.find_correlation_between show="covariance"` (1): divide by n - 1, each pair on the rows where both columns have a number (as R cov(use = "pairwise.complete.obs"); R's default gives NA with an empty cell, and NumPy cov reads rows as the variables).
- `table.forecast order="automatic"` (1): every order is tried (stepwise = FALSE, approximation = FALSE) for series of up to 1,000 readings; auto.arima's own quicker defaults can choose another order on long or seasonal series.
- `table.add_adjusted_p_value_column test_method="storey"` (1): qvalue's own defaults: the share of true nulls (pi0) estimated by the smoother over lambda = 0.05 to 0.95 (Storey & Tibshirani 2003), not set to 1 as in Benjamini-Hochberg.
- `table.add_adjusted_p_value_column test_method="local fdr"` (1): qvalue's local false discovery rate with its defaults (pi0 from the smoother), in a column named "local false discovery rate", not "adjusted p": it belongs to one test.
- `table.compare_each_pair_of matched_by=, test_method="nemenyi"` (1): Nemenyi's test allows for all the pairs itself (the studentized range): no Holm on top, and the printout says not to adjust again.
- `table.compare_each_pair_of matched_by=, test_method="conover"` (1): Holm's adjustment, as for Conover's test after Kruskal-Wallis; PMCMRplus's own default is "single-step" and scikit-posthocs adjusts nothing, so their numbers differ.
- `table.compare_each_pair_of based_on="percents"` (1): each pair gets the 2 x 2 chi-square test with Yates' correction that compare_counts_of uses (the default of R prop.test and pairwise.prop.test); test_method="fisher" gives Fisher's exact test.
- `table.compare_each_pair_of based_on="percents"` (2): Holm's adjustment for the number of pairs, as R pairwise.prop.test().
- `sdata.make_random_assignments` (1): R's generator named in full (Mersenne-Twister, Inversion, Rejection): sample() changed in R 3.6.0, so the same seed gives another list in older R.
- `sdata.make_random_assignments` (2): real block sizes, divided by the number of groups for blockrand (which counts in multiples of it); without in_blocks_of= simplydata chooses 2 and 3 times the number of groups, of random sizes.
- `sdata.make_design_table` (1): R's own generator (kinds = "Mersenne-Twister"), not agricolae's default "Super-Duper", so with_seed= gives the layout an R user gets after set.seed().
- `sdata.make_design_table` (2): the standard order is R expand.grid() order: the first factor changes fastest (Yates' order).
- `sdata.make_design_table of_kind="randomised blocks"` (1): each repeat is a block holding every combination once, in its own random order (agricolae design.ab(design = "rcbd")).
- `sdata.make_design_table of_kind="latin square"` (1): agricolae design.lsd: each level once in every row and every column, rows and columns in random order.
- `sdata.make_design_table of_kind="split plot"` (1): whole plots in randomised blocks (agricolae design.split(design = "rcbd")), the factor named in whole_plots= on the whole plots.
- `table.keep_random_rows for_each_group_in=` (1): the rows keep their order in the table (sort_index()); a group with n rows or fewer is kept whole, with a note (pandas stops with an error).
- `table.keep_random_rows percent=` (1): pandas rounds each group's share; a group whose share rounds to no row still gets one row (a stratified sample keeps every stratum).
- `table.count_empty_cells_in show="patterns"` (1): an empty cell is a missing value, NaN or text of only spaces (as count_empty_cells_in); the patterns are sorted by how many cells they leave empty, then by how many rows have them (R mice::md.pattern() sorts by its own rule and turns the columns round).
- `table.count_empty_cells_in columns=` (1): an empty cell is a missing value, NaN or text of only spaces; pandas isna() counts only the missing values and NaN.
- `table.count_each columns=, in_order=` (1): percents out of the answers given (empty cells left out), and no averages of the answers: the steps between them need not be equal.
- `table.count_each columns=, in_order=` (2): the median answer is a real answer, the inverted CDF (R quantile(type = 1)), never a value between two.
- `draw_answer_bars` (1): diverging bars (Heiberger & Robbins 2014): the answers below the middle to the left of 0, the middle answer split half and half across 0, and the first question at the top.
- `table.find_average_of after use_survey_design()` (1): the 95 % interval uses t on the design's degrees of freedom (degf(design), here 197), not survey's own normal-curve confint().
- `table.find_total_of after use_survey_design()` (1): the 95 % interval uses t on the design's degrees of freedom (degf(design), here 197), not survey's own normal-curve confint().
- `table.find_median_of after use_survey_design()` (1): the population median by the weighted inverted CDF (qrule = "math", as find_percentile_of(weight_kind="analytic")), with Woodruff's interval on the design's degrees of freedom.
- `table.find_percentile_of after use_survey_design()` (1): as find_median_of under a survey design: qrule = "math" and Woodruff's interval on the design's degrees of freedom.
- `table.find_percent_of_rows_where after use_survey_design()` (1): survey's logit interval (svyciprop(method = "logit")), which stays between 0 and 100 %, on the design's degrees of freedom; the share is shown in percent.
- `table.count_rows after use_survey_design()` (1): the estimated number in the population is survey's total of a column of ones (the sum of the weights); in_percent=True gives each group's share, svymean(~factor(group)).
- `table.explain after use_survey_design()` (1): survey::svyglm with the family of outcome= (gaussian; quasibinomial for yes or no; quasipoisson for counts) and its own t tests and intervals on the model's residual degrees of freedom.
- `table.compare_averages_of after use_survey_design()` (1): the design-based t test of survey::svyttest() for two groups; more groups go to explain().
- `table.compare_counts_of after use_survey_design()` (1): the Rao-Scott corrected chi-square as an F test (survey::svychisq()'s default statistic = "F").
- `table.compare_balanced_groups_of` (1): weighting by the inverse of the propensity score from logistic regression, for everyone (ATE), unless effect_for= names a group (ATT).
- `table.compare_balanced_groups_of` (2): the effect from WeightIt's lm_weightit(), whose M-estimation standard errors allow for the estimated weights (statsmodels TreatmentEffect.ipw gives the same estimate with a larger error).
- `table.compare_balanced_groups_of` (3): standardised differences for every column, text columns too (binary = "std"), with the guide 0.1; never p-values for balance (Austin 2009).
- `table.compare_balanced_groups_of test_method="matching"` (1): 1:1 nearest-neighbour matching on the propensity score without replacement, MatchIt's default; match_within= adds a caliper in standard deviations of the logit of the score (Austin 2011).
- `table.compare_balanced_groups_of test_method="matching"` (2): standard errors clustered on the matched pairs, as the MatchIt vignette does.
- `table.compare_risks show="attributable fractions"` (1): the risk-based fractions of a cohort (method = "cohort.count"), with the intervals epiR gives for one table (among the exposed, from the score interval of the risk ratio; in the population, from the exact intervals of the two risks; epiR's names end in .wald all the same); crude, not adjusted for other columns.
- `table.rate_of standard_population=` (1): "whole table": the standard population is the person-time of all rows in each band.
- `table.rate_of standard_population=` (2): direct standardisation with Fay & Feuer's gamma interval (epiR, the same as epitools::ageadjust.direct()).
- `table.compare_rates standard_rates=` (1): the standard rates are read per per= units of time (1000 here) and divided by it for epiR, which wants rates per one unit.
- `table.compare_rates standard_rates=` (2): observed / expected with the exact Poisson interval; the p-value from R poisson.test(observed, expected).
- `table.explain through=` (1): least squares for a column of numbers, logistic regression for yes or no; the exposure coded 0 and 1 (against= is 0).
- `table.explain through=` (2): 1000 quasi-Bayesian simulations, as R mediation::mediate(sims = 1000), with_seed=1; effects averaged over the two exposure levels.
- `table.compare_averages_of period=` (1): the sequence is each subject's formulation in the first period.
- `table.compare_averages_of period=` (2): the EMA (2010) model with all effects fixed, on the log scale.
- `table.compare_averages_of period=` (3): the 90 % interval, the same as two one-sided tests at 5 % each; the ratio and its interval taken back from logs.
- `table.find_correlation_between empty_cells="multiple imputation"` (1): Fisher's z of each filled-in table pooled with Rubin's rules and taken back to r (van Buuren 2018, section 5.2).
- `table.compare_averages_of test_method="bayesian"` (1): the JZS prior of medium width (a Cauchy prior on the effect size, r = 0.707; Rouder et al. 2009), BayesFactor's default; prior_width= changes it.
- `table.compare_averages_of test_method="bayesian"` (2): with_seed=1: R's set.seed() before BayesFactor::posterior() (10,000 draws), so the interval is the same on every run; the Bayes factor itself is worked out without random draws.
- `table.compare_before_and_after test_method="bayesian"` (1): the change is after minus before (x = after, y = before), with the JZS prior of medium width.
- `table.compare_before_and_after test_method="bayesian"` (2): with_seed=1: R's set.seed() before BayesFactor::posterior() (10,000 draws), so the interval is the same on every run; the Bayes factor itself is worked out without random draws.
- `table.compare_average_to test_method="bayesian"` (1): x - 5 rather than mu = 5: BayesFactor's posterior() leaves mu = out (its draws are those of mu = 0), while its Bayes factor takes mu away inside; so the Bayes factor is the same and the posterior is that of the average minus 5.
- `table.compare_average_to test_method="bayesian"` (2): with_seed=1: R's set.seed() before BayesFactor::posterior() (10,000 draws), so the interval is the same on every run; the Bayes factor itself is worked out without random draws.
- `table.find_correlation_between test_method="bayesian"` (1): the stretched beta prior of medium width 1/3 (BayesFactor's default; JASP's default of 1 gives other Bayes factors).
- `table.find_correlation_between test_method="bayesian"` (2): with_seed=1: R's set.seed() before BayesFactor::posterior() (10,000 draws), so the interval is the same on every run; the Bayes factor itself is worked out without random draws.
- `table.compare_counts_of test_method="bayesian"` (1): independent multinomial sampling with each group's total fixed: the groups are the rows (fixedMargin = "rows"), with the Gunel-Dickey prior of concentration 1 (BayesFactor's default).
- `table.compare_counts_of test_method="bayesian"` (2): with_seed=1: R's set.seed() before BayesFactor::posterior() (10,000 draws), so the interval is the same on every run; the Bayes factor itself is worked out without random draws.
- `table.explain test_method="bayesian"` (1): rstanarm's defaults written out: 4 chains of 2000 iterations (1000 warm-up), its weakly informative priors scaled to the data (printed from prior_summary()), seed = with_seed and cores = 1 (no worker processes).
- `table.explain test_method="bayesian"` (2): the posterior median and the central 95 % interval (posterior_interval()); R-hat, bulk and tail effective sample sizes from the posterior package (rank-normalised, Vehtari et al. 2021), not the older Rhat and n_eff of rstanarm's summary().
- `table.explain test_method="bayesian", grouped_by=` (1): a mixed model with its own starting level for each school, (1 \| school), rstanarm's decov prior for the group spread; otherwise as explain(test_method="bayesian").
- `table.check_model_of test_method="bayesian"` (1): 50 sets of made-up values from the fitted model (posterior_predict(draws = 50)), as bayesplot's pp_check() shows by default.
- `table.check_model_of test_method="bayesian"` (2): each set and the data as a density on one grid from the smallest to the largest value, R stats::density() with its bw.nrd0 bandwidth, the rule bayesplot::ppc_dens_overlay uses through ggplot2; the lines are drawn with matplotlib.
- `table.show_rows_that_pull_model` (1): rows with a Cook's distance above 4 / (number of rows), a rule of thumb (Bollen & Jackman 1985), biggest first, numbered from 1 in the whole table (empty cells included).
- `sdata.get_example from_r_package=` (1): R itself loads the dataset (utils::data, from the data file that holds it: lung is kept in "cancer"); groups (factors) become text and R's NA empty cells; row names that carry information become a first column "row name".
- `table.check_model_of show="numbers"` (1): Koenker's studentised Breusch-Pagan test (robust=True, as R lmtest::bptest's default), which does not assume bell-shaped errors.
- `table.find_correlation_between show="result table"` (1): the 95 % interval of Pearson's r from Fisher's z, as SciPy pearsonr and R cor.test.
- `table.find_correlation_between allowing_for=, show="result table"` (1): the partial correlation of R ppcor::pcor.test(): the link left after taking out what both columns share with the third; its statistic is t (z for Kendall) and it gives no interval.
- `trade_off_curve get_numbers_drawn()` (1): the best cut-off by Youden's index, R pROC::coords("best", best.method = "youden"); its threshold is the value of the marked dot, its sensitivity the dot's y.
- `nums.smooth` (1): a moving average of 5 readings centred on each one (window=5); the weights add up to 1.
- `nums.smooth` (2): the first and last 2 readings have no full window, so they are left empty, as R stats::filter(x, rep(1 / 5, 5), sides = 2) (ends="empty"; "shorter windows" and "mirror" fill them).
- `nums.remove_trend` (1): the least-squares straight line through the readings, one step apart, is taken away, as R residuals(lm(x ~ seq_along(x))); test_method="average" takes away the average only.
- `table.add_trend_and_season` (1): repeats_every="year" with monthly readings is a cycle of 12 readings.
- `table.add_trend_and_season` (2): R stl()'s settings: a season window of 7 cycles (season_window=), a season of degree 0, and R's trend span (23), low-pass span (13) and jumps worked out from the cycle; statsmodels' own defaults differ and give other numbers.
- `table.add_trend_and_season` (3): 2 inner passes and no robustness passes, as R stl(robust = FALSE) (robust=True: 1 and 15).
- `nums.find_autocorrelation` (1): rows back 1 to 10 x log10(n), as R acf's lag.max (30 for 1,000 readings).
- `nums.find_autocorrelation` (2): each correlation divides by n, not by the number of pairs, as R acf (adjusted=False).
- `nums.find_autocorrelation` (3): the band is +/- qnorm(0.975) / sqrt(n), the dashed lines of R plot.acf; the Ljung-Box test runs up to the last rows back.
- `table.check_steady_over_time` (1): trunc((n - 1)^(1/3)) rows back in the test regression, the rule of tseries::adf.test.
- `table.check_steady_over_time` (2): around="level" asks about one steady level, so the Dickey-Fuller regression has a constant and no trend (urca type = "drift"): tseries::adf.test always allows a trend, so a column that rises steadily would pass it as steady.
- `table.check_steady_over_time` (3): MacKinnon's p-value (urca::punitroot), with N the number of rows in the test regression.
- `table.find_change_points_in` (1): the readings are divided by the noise size s = mad(diff(x)) / sqrt(2) first: cpt.mean assumes noise with a standard deviation of 1, and changepoint itself does not scale. Taking s from the differences between neighbours keeps the jumps from inflating it. This is simplydata's own choice.
- `table.find_change_points_in` (2): the PELT search with R's own MBIC penalty (penalty="bic", "aic" or "hannan-quinn" instead).
- `nums.forecast` (1): test_method="exponential smoothing" is Holt-Winters as R stats::HoltWinters fits it: a level, a trend and a season that is added (trend=True, season="added"), the weights chosen by R.
- `nums.forecast` (2): 95 % prediction intervals (interval=95), from forecast::forecast.
- `table.compare_forecasts_for` (1): each method is fitted on all but the last 12 readings (check_on_last=12) and forecasts them.
- `table.compare_forecasts_for` (2): the held-back readings are given to forecast::accuracy as a series with 12 readings a cycle, so MASE divides the average error by that of the same season last time inside the fitted readings (the last value without repeats_every=); given as plain numbers, accuracy would scale by the last value.
- `table.compare_forecasts_for` (3): the methods are ranked by MASE, best first.
- `nums.find_each_peak_that` (1): each peak's width is measured halfway down its prominence: SciPy peak_widths(rel_height=0.5), as MATLAB findpeaks("WidthReference", "halfprom"); in readings (in units of time with time_step=).
- `nums.find_each_peak_that` (2): positions and bases count from 1.
- `nums.find_each_dip_that` (1): the dips are the peaks of minus the numbers, so is_at_most=2 becomes SciPy's height=-2 (as R pracma::findpeaks(-x) for dips without flat bottoms); widths are measured halfway down.
- `nums.find_each_dip_that` (2): positions and bases count from 1; the value is the number itself, not minus it.
- `table.find_each_dip_that` (1): the dips are the peaks of minus the readings: is_at_most=-1 becomes SciPy's height=1.
- `table.find_each_dip_that` (2): apart= is in units of sorted_by, so it becomes a number of readings (0.035 / 0.005 = 7). simplydata rounds it to 9 decimals first: in floating point it is 7.000000000000001, which SciPy rounds up to 8 readings, and 3 of the dips here would be lost.
- `table.find_spectrum_of` (1): sorted_by="time" gives the time between readings (0.005), so the frequencies are per second.
- `table.find_spectrum_of` (2): the periodogram as SciPy makes it: the average taken away, no taper, one-sided and scaled so that power x frequency step adds up to the variance; that is 2 x R spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)$spec at every frequency but the top one.
- `nums.find_spectrum` (1): without time_step= the readings are one step apart, so the frequencies are cycles per reading.
- `nums.find_spectrum` (2): the one-sided periodogram, scaled so that power x frequency step adds up to the variance (2 x R spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)$spec, except at the top frequency).
- `nums.keep_each_frequency_that` (1): a Butterworth filter of steepness 4 (the filter order), made as second-order sections so it stays stable; as R signal::butter(4, 10 / 100).
- `nums.keep_each_frequency_that` (2): run forwards and backwards (both_ways=True), so nothing moves in time; the ends follow SciPy (odd reflection, steady start, as MATLAB filtfilt), which differs from R signal::filtfilt near the ends.
- `nums.remove_each_frequency_that` (1): one frequency is removed by a notch filter whose width is 1 (width=1), so its quality factor is 50 / 1.
- `nums.remove_each_frequency_that` (2): run forwards and backwards (both_ways=True), so nothing moves in time.
- `table.add_filtered_column` (1): the readings are filtered in order of sorted_by="time", whatever the order of the rows, and the time between them (0.005 seconds) makes keep_below=10 mean 10 cycles per second; each row keeps its own filtered value.
- `table.add_filtered_column` (2): a Butterworth filter of steepness 4, as second-order sections (R signal::butter(4, 10 / 100)).
- `table.add_filtered_column` (3): run forwards and backwards (both_ways=True), so nothing moves in time.
- `sdata.frequency_filter` (1): the filter of add_filtered_column(keep_below=10): Butterworth, steepness 4, as second-order sections.
- `sdata.frequency_filter` (2): its formula in z comes from the sections (sos2tf), highest power first (system.table() shows it).
- `table.add_envelope_column` (1): the envelope is the size of the analytic signal from the Hilbert transform, worked out on the readings in order of sorted_by=, whatever the order of the rows; each row keeps its own value.
- `nums.take_fourier_transform` (1): show="half": the frequencies from 0 up to the highest the readings can show (rfft); show="all" gives every frequency, negative ones too (fft).
- `nums.take_fourier_transform` (2): the phase is in degrees, as R Arg(fft(x)) * 180 / pi.
- `sdata.find_inverse_fourier_transform` (1): the number of readings is remembered from the transform: an odd count (5) cannot be told from the half spectrum, and irfft's own default would give 4 numbers.
- `nums.convolve_with` (1): keep="all": every overlap, n + m - 1 numbers, as R convolve(x, rev(y), type = "open"); "same" keeps the middle n, "overlap" only full overlaps.
- `nums.change_time_step` (1): the new number of readings fills the same time: n x old step / new step (1,000 readings become 500).
- `nums.change_time_step` (2): test_method="fourier": SciPy resample, which treats the recording as repeating; "polyphase" (resample_poly) and "filter then keep" (decimate) are the other methods.
- `sdata.make_wave` (1): the times start at 0 and go up by time_step=.
- `sdata.make_wave` (2): a square wave is high (1) for half of each cycle (high_share=0.5) and low (-1) for the rest.
- `sdata.make_window_shape` (1): the symmetric window (as R gsignal::hann and NumPy hanning); SciPy get_window's own default is the periodic one used inside spectra (periodic=True).
- `sdata.system` (1): the coefficients are divided by the first one of the bottom, so it is 1, as SciPy's TransferFunction keeps them (1 / (s**2 + 2*s + 5)).
- `system.step_response` (1): 200 times, evenly spaced from 0 to until= (how_many=200).
- `system.impulse_response` (1): 200 times, evenly spaced from 0 to until= (how_many=200).
- `system.response_to` (1): the times come from the time step the input numbers remember (0.05), starting at 0.
- `system.response_to` (2): the system starts at rest and each input value holds until the next time (interp=False, a zero order hold), as R control::lsim; SciPy's own default joins the inputs by straight lines.
- `system.frequency_response` (1): 200 frequencies spaced evenly on a log scale, in radians per second (unit=).
- `system.frequency_response` (2): the phase is unwrapped, so it runs on past -180 degrees (to -270 here) without jumping back to +180.
- `system.poles` (1): the damping ratio and natural frequency of each pole, as R control::damp (for a system in steps worked out from log(pole) / time step).
- `system.is_stable` (1): stable means every pole has a real part below 0 (inside the unit circle in steps); poles on the edge, such as +/- 2i here, are not stable, because the output never settles.
- `system.steady_gain` (1): the formula at s = 0 (z = 1 in steps), as R control::dcgain.
- `system.in_steps` (1): test_method="zero order hold": the input stays constant between steps, as R control::c2d(sys, 0.1).
- `system.then` (1): in series the formulas multiply, top by top and bottom by bottom, as R control::series.
- `system.add` (1): side by side the outputs add, so the formulas add over a common bottom, as R control::parallel.
- `system.with_feedback` (1): negative feedback through 1 (the output itself): G / (1 + G), as R control::feedback(sys, 1); sign="positive" gives G / (1 - G).
- `system.table` (1): form="transfer function": one row per power, highest first, with the top padded with zeros to the length of the bottom.
- `autocorrelation_bars` (1): rows back 1 to 10 x log10(n), as R acf (21 for 144 months); each correlation divides by n.
- `autocorrelation_bars` (2): the dashed band is +/- qnorm(0.975) / sqrt(n), as the dashed lines of R plot(acf(x)).
- `cross_correlation_bars` (1): a stick at shift s pairs the first column at row t with the second at row t + s (R ccf's lag -s), so a high stick at shift 6 means the second follows the first 6 rows later.
- `cross_correlation_bars` (2): the dashed band is +/- qnorm(0.975) / sqrt(n), as R plot(ccf(a, b)).
- `lag_dots` (1): each value against the value k rows earlier, in the order of sorted_by=; the first k rows have no partner and are left out. Each rows_back= gets its own colour.
- `lag_dots` (2): the dashed 1:1 line runs from the smallest to the biggest value shown, as R lag.plot(diag = TRUE).
- `peak_dots` (1): the peaks of table.find_each_peak_that: apart= is in units of x, so 0.035 / 0.005 = 7 readings, rounded to 9 decimals first (in floating point it is 7.000000000000001, which SciPy would round up to 8 and lose 3 peaks).
- `spectrum` (1): the periodogram of table.find_spectrum_of: one-sided, no taper, scaled so the powers add up to the variance; the time step (0.005) gives frequencies per second.
- `spectrum` (2): frequency 0 (the average) is left out, and the power is on a log scale (log_scale=True).
- `spectrum` (3): the 3 frequencies with the biggest powers (frequency 0 left out) are labelled with how often they repeat; they can be neighbours on one peak.
- `spectrum_over_time` (1): pieces of window=100 readings with a Hann window (window_shape=), each with its own periodogram.
- `spectrum_over_time` (2): the pieces overlap by half and each piece's average is taken away first.
- `spectrum_over_time` (3): the power is shown in decibels (10 x log10), on viridis colours; each piece sits at its middle time.
- `trend_and_season` (1): the parts are those of table.add_trend_and_season: STL with R stl()'s settings (season window 7, season of degree 0, R's spans and jumps), on a cycle of 12 months.
- `trend_and_season` (2): four panels sharing x, top to bottom: the column itself, its trend, its season and the rest, the rest drawn as sticks from 0, as R plot(stl(...)) (which names the first panel "data").
- `forecast` (1): the numbers of table.forecast: Holt-Winters as R stats::HoltWinters fits it (a level, a trend and an added season, repeats_every="year" = 12 months).
- `forecast` (2): the band is the 95 % prediction interval (interval=95), from forecast::forecast.
- `forecast` (3): the months carry on after the last one, one month apart.
- `system.chart` (1): show="bode": 200 frequencies SciPy picks from the poles and zeros (findfreqs), in radians per second (unit=).
- `system.chart` (2): two panels sharing a log x-axis: the gain in decibels above, the phase in degrees below, unwrapped so it runs on past -180 degrees.
- `sdata.table` (1): the separator is guessed from the file (sep=None), so a file with ; or tabs between the values is read too; separator= sets it yourself.
- `sdata.get_example` (1): a column of dates is read as dates (parse_dates=), so date words work on it at once.
- `sdata.numbers` (1): the end you give is included (0, 25, 50, 75, 100): simplydata counts how many steps fit (with a little room for rounding) and multiplies. np.arange(0, 125, 25) gives the same here, but with a decimal step np.arange can overshoot the end: np.arange(1, 1.4, 0.1) has 1.4 in it.
- `sdata.number_grid` (1): the list is cut into rows, row after row (NumPy's order "C"): 1 2 3, then 4 5 6.
- `sdata.distribution` (1): the parameters have plain names (tries=, chance=), turned into SciPy's (n, p); R's names (size=, prob=) work too.
- `sdata.make_random_numbers` (1): NumPy's random generator (default_rng) with the seed you give, the way NumPy recommends; the old np.random.seed() gives other numbers.
- `sdata.make_random_numbers` (2): both ends are included, like rolling a dice (endpoint=True); NumPy's own default leaves out 6.
- `sdata.make_run_of_dates` (1): each month is counted from the first date, so the dates stay on the 30th, or on the month's last day when it is shorter (30 January, 28 February, 30 March, 30 April). pandas' date_range(freq=DateOffset(months=1)) steps from the date before instead and stays on the 28th; R's seq(by = "month") runs over into March.

## Datasets

| dataset | what | source | licence |
|---|---|---|---|
| [NIST Norris](https://www.itl.nist.gov/div898/strd/lls/data/Norris.shtml) | 36 observations of ozone monitor calibration; certified straight-line fit (NIST StRD, lower difficulty) | Norris, J., NIST. Calibration of Ozone Monitors. In: NIST Statistical Reference Datasets (StRD), Linear Regression, dataset Norris. National Institute of Standards and Technology. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [Anscombe's quartet](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/anscombe.html) | four sets of 11 (x, y) pairs with the same straight-line fit | Anscombe, F. J. (1973). Graphs in statistical analysis. The American Statistician 27(1), 17-21. Copy from R's datasets package (anscombe). | The 88 published numbers, as in R's datasets package (GPL-2 \| GPL-3). Not stored here: read from the installed R package, so it needs R. |
| [NIST Michelso](https://www.itl.nist.gov/div898/strd/univ/michelso.html) | 100 measurements of the speed of light in air by Michelson (1879); certified mean and standard deviation | Dorsey, E. N. (1944). The Velocity of Light. Transactions of the American Philosophical Society 34(1), 1-110, Table 22. In: NIST StRD, Univariate Summary Statistics, dataset Michelso. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Mavro](https://www.itl.nist.gov/div898/strd/univ/mavro.html) | 50 filter transmittance measurements by R. Mavrodineanu (NIST); certified mean and standard deviation | Mavrodineanu, R., NIST. Filter transmittance data. In: NIST StRD, Univariate Summary Statistics, dataset Mavro. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST NumAcc4](https://www.itl.nist.gov/div898/strd/univ/numacc4.html) | 1001 nine-digit numbers that differ only in the last digit; constructed by NIST to test accuracy (higher difficulty); certified mean 10000000.2 exactly | Simon, S. D. & Lesage, J. P. (1989). Assessing the accuracy of ANOVA calculations in statistical software. Computational Statistics & Data Analysis 8, 325-332. In: NIST StRD, dataset NumAcc4. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [Student's sleep data](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/sleep.html) | extra hours of sleep for 10 patients with each of two drugs | Cushny, A. R. & Peebles, A. R. (1905). The action of optical isomers. II. Hyoscines. Journal of Physiology 32, 501-510. Analysed by Student (1908). The probable error of a mean. Biometrika 6(1), 1-25. Copy from R's datasets package (sleep). | Public domain (published 1905 and 1908); the copy in R's datasets package is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [aSAH (pROC)](https://cran.r-project.org/package=pROC) | 113 patients with aneurysmal subarachnoid haemorrhage: outcome and the biomarker s100b | Turck, N. et al. (2010). A multiparameter panel method for outcome prediction following aneurysmal subarachnoid hemorrhage. Intensive Care Medicine 36, 107-115. Shipped with R's pROC package (Robin, X. et al. (2011). BMC Bioinformatics 12, 77). | GPL-3 or later (pROC). Not stored here: read from the installed pROC package, so it needs R. |
| made-up | small made-up tables for edge cases (empty cells, no rows left, an exact line) | simplydata's validation/cases.py. | Same as simplydata (see LICENSE). |
| [standard normal table](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3671.htm) | the area under the standard normal curve from 0 to z, to 5 decimals (no data: a published table) | NIST/SEMATECH e-Handbook of Statistical Methods, section 1.3.6.7.1, Cumulative Distribution Function of the Standard Normal Distribution. | Public domain in the United States (a work of the US Government); one number is quoted, nothing stored. |
| [Galton's sweet peas](https://cran.r-project.org/package=alr4) | 7 parent sweet-pea seed diameters (hundredths of an inch), each with the average and the standard deviation of the diameters of its offspring seeds | Galton, F. (1877). Typical laws of heredity. Nature 15, 492-495, 512-514, 532-533. Used for weighted least squares in Weisberg, S. (2014). Applied Linear Regression, 4th ed., Wiley, section 7.1. Copy from the R package alr4 (galtonpeas). | Published 1877 (public domain); the alr4 copy is GPL (>= 2). Not stored here: read from the installed R package, so it needs R. |
| [Orobanche seeds](https://cran.r-project.org/package=agridat) | 21 plates of seeds of two Orobanche varieties (O73, O75) on bean or cucumber root extract: the seeds that germinated, out of the seeds on the plate | Crowder, M. J. (1978). Beta-binomial anova for proportions. Applied Statistics 27(1), 34-37. Copy from the R package agridat (crowder.seeds; Wright, K.), through Rdatasets. | The published counts (facts from a 1978 paper); the agridat copy is MIT licensed. |
| [infert](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/infert.html) | 248 women in 83 matched sets (1 or 2 cases of secondary infertility, each with 2 controls matched on age, parity and education): earlier spontaneous and induced abortions | Trichopoulos, D., Handanos, N., Danezis, J., Kalandidi, A. & Kalapothaki, V. (1976). Induced abortion and secondary infertility. British Journal of Obstetrics and Gynaecology 83, 645-650. Copy from R's datasets package (infert). | Published 1976; R's datasets copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [birthwt](https://cran.r-project.org/package=MASS) | 189 births at Baystate Medical Center, Springfield, Massachusetts (1986): low birth weight (below 2.5 kg) and the mother's age, weight, smoking, race and history | Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Copy from the R package MASS (birthwt; Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed. Springer). | The MASS copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [stackloss](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/stackloss.html) | 21 days of a plant oxidising ammonia to nitric acid: air flow, cooling water temperature, acid concentration and the ammonia lost (stack loss) | Brownlee, K. A. (1965). Statistical Theory and Methodology in Science and Engineering, 2nd ed. Wiley, pp. 491-500. Copy from R's datasets package (stackloss). | Published 1960/1965; R's datasets copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [mtcars](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/mtcars.html) | 32 cars (1973-74 models): fuel use (miles per gallon) and 10 design and performance measures | Henderson, H. V. & Velleman, P. F. (1981). Building multiple regression models interactively. Biometrics 37, 391-411 (data from Motor Trend, 1974). Copy from R's datasets package (mtcars). | Published 1974 and 1981; R's datasets copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [VerbAgg](https://cran.r-project.org/package=lme4) | verbal aggression: 316 people each answered 24 items (would they curse, scold or shout in a frustrating situation?), yes or no; people and items are crossed | De Boeck, P. & Wilson, M. (2004). Explanatory Item Response Models. Springer (data collected by Vansteelandt, 2000). Copy from the R package lme4 (VerbAgg). | The lme4 copy is GPL (>= 2). Not stored here: read from the installed R package, so it needs R. |
| [NMES 1988](https://www.jstatsoft.org/v027/i08) | 4406 people aged 66 and over in the US National Medical Expenditure Survey 1987/88: physician office visits, hospital stays, self-rated health, chronic conditions, gender, years of school and private insurance (7 of the 19 columns) | Deb, P. & Trivedi, P. K. (1997). Demand for medical care by the elderly: a finite mixture approach. Journal of Applied Econometrics 12, 313-336. Analysed with hurdle and zero-inflated models in Zeileis, A., Kleiber, C. & Jackman, S. (2008). Regression models for count data in R. Journal of Statistical Software 27(8), 1-25. Copy from the R package AER (NMES1988), through Rdatasets. | A US Government survey (public domain); the AER copy is GPL-2 \| GPL-3; the JSS article is CC BY. Not stored here: read from the installed R package, so it needs R. |
| [ryegrass (drc)](https://doi.org/10.1371/journal.pone.0146021) | root length of perennial ryegrass at 7 concentrations of ferulic acid (24 rows) | Inderjit, Streibig, J. C. & Olofsdotter, M. (2002). Joint action of phenolic acid mixtures and its significance in allelopathy research. Physiologia Plantarum 114, 422-428. Analysed in Ritz, C., Baty, F., Streibig, J. C. & Gerhard, D. (2015). Dose-response analysis using R. PLoS ONE 10, e0146021. Shipped with the R package drc. | The article (Ritz et al. 2015) is CC BY 4.0; the data are shipped with drc (GPL-2 or later). Not stored here: read from the installed drc package, so it needs R. |
| [Bliss beetles](https://doi.org/10.1111/j.1744-7348.1935.tb07713.x) | flour beetles killed after five hours of carbon disulphide at 8 doses (log10 mg per litre) | Bliss, C. I. (1935). The calculation of the dosage-mortality curve. Annals of Applied Biology 22, 134-167. Logistic fit printed in Dobson, A. J. & Barnett, A. G. (2008). An Introduction to Generalized Linear Models, 3rd ed., section 7.3. | Facts published in 1935 (24 numbers), typed from the paper; not covered by copyright. |
| [poisons (boot)](https://doi.org/10.1111/j.2517-6161.1964.tb00553.x) | survival times of 48 animals: 3 poisons x 4 treatments, 4 animals each | Box, G. E. P. & Cox, D. R. (1964). An analysis of transformations. Journal of the Royal Statistical Society B 26, 211-252 (Table 1; the power found is about -0.75, the reciprocal suggested). Shipped with the R package boot. | Facts published in 1964; the copy in boot is GPL (Unlimited). Not stored here: read from boot, so it needs R. |
| [NIST Rat42](https://www.itl.nist.gov/div898/strd/nls/data/ratkowsky2.shtml) | pasture yield against growing time (9 points); certified 3 parameter logistic fit (NIST StRD, higher difficulty) | Ratkowsky, D. A. (1983). Nonlinear Regression Modeling. New York: Marcel Dekker, pp. 61 and 88. In: NIST StRD, Nonlinear Regression, dataset Rat42. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Misra1a](https://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml) | monomolecular absorption (14 points); certified fit of y = b1 (1 - exp(-b2 x)) (NIST StRD, lower difficulty) | Misra, D., NIST (1978). Dental research monomolecular adsorption study. In: NIST StRD, Nonlinear Regression, dataset Misra1a. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST BoxBOD](https://www.itl.nist.gov/div898/strd/nls/data/boxbod.shtml) | biochemical oxygen demand against incubation time (6 points); certified fit of y = b1 (1 - exp(-b2 x)) (NIST StRD, higher difficulty) | Box, G. P., Hunter, W. G. & Hunter, J. S. (1978). Statistics for Experimenters. New York: Wiley, pp. 483-487. In: NIST StRD, Nonlinear Regression, dataset BoxBOD. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Filip](https://www.itl.nist.gov/div898/strd/lls/data/Filip.shtml) | 82 observations; certified polynomial of degree 10 (NIST StRD linear regression, higher difficulty: the powers of x are nearly in proportion) | Filippelli, A., NIST. In: NIST StRD, Linear Regression, dataset Filip. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Wampler1](https://www.itl.nist.gov/div898/strd/lls/data/Wampler1.shtml) | 21 points (x = 0 to 20) exactly on y = 1 + x + x^2 + x^3 + x^4 + x^5 (certified standard errors 0); certified polynomial of degree 5 (NIST StRD linear regression, higher difficulty) | Wampler, R. H. (1970). A report on the accuracy of some widely used least squares computer programs. Journal of the American Statistical Association 65, 549-565. In: NIST StRD, Linear Regression, dataset Wampler1. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Wampler2](https://www.itl.nist.gov/div898/strd/lls/data/Wampler2.shtml) | 21 points (x = 0 to 20) exactly on y = 1 + 0.1 x + 0.01 x^2 + ... + 0.00001 x^5; certified polynomial of degree 5 (NIST StRD linear regression, higher difficulty) | Wampler, R. H. (1970). A report on the accuracy of some widely used least squares computer programs. Journal of the American Statistical Association 65, 549-565. In: NIST StRD, Linear Regression, dataset Wampler2. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Wampler3](https://www.itl.nist.gov/div898/strd/lls/data/Wampler3.shtml) | 21 points (x = 0 to 20) on y = 1 + x + ... + x^5 plus noise (residual standard deviation 2360); certified polynomial of degree 5 (NIST StRD linear regression, higher difficulty) | Wampler, R. H. (1970). A report on the accuracy of some widely used least squares computer programs. Journal of the American Statistical Association 65, 549-565. In: NIST StRD, Linear Regression, dataset Wampler3. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Wampler4](https://www.itl.nist.gov/div898/strd/lls/data/Wampler4.shtml) | 21 points (x = 0 to 20) on y = 1 + x + ... + x^5 plus larger noise (residual standard deviation 236,000); certified polynomial of degree 5 (NIST StRD linear regression, higher difficulty) | Wampler, R. H. (1970). A report on the accuracy of some widely used least squares computer programs. Journal of the American Statistical Association 65, 549-565. In: NIST StRD, Linear Regression, dataset Wampler4. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Wampler5](https://www.itl.nist.gov/div898/strd/lls/data/Wampler5.shtml) | 21 points (x = 0 to 20) on y = 1 + x + ... + x^5 plus noise far larger than the curve (residual standard deviation 23,600,000); certified polynomial of degree 5 (NIST StRD linear regression, higher difficulty) | Wampler, R. H. (1970). A report on the accuracy of some widely used least squares computer programs. Journal of the American Statistical Association 65, 549-565. In: NIST StRD, Linear Regression, dataset Wampler5. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Longley](https://www.itl.nist.gov/div898/strd/lls/data/Longley.shtml) | 16 years of US macroeconomic data (1947-1962): total employment and six predictors that move almost together; certified multiple regression (NIST StRD linear regression, higher difficulty) | Longley, J. W. (1967). An appraisal of least squares programs for the electronic computer from the viewpoint of the user. Journal of the American Statistical Association 62, 819-841. In: NIST StRD, Linear Regression, dataset Longley. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Roszman1](https://www.itl.nist.gov/div898/strd/nls/data/roszman1.shtml) | quantum defects in iodine atoms (25 points); certified fit of y = b1 - b2 x - arctan(b3 / (x - b4)) / pi (NIST StRD, average difficulty) | Roszman, L., NIST (year not given). Quantum Defects for Sulfur I Atom. In: NIST StRD, Nonlinear Regression, dataset Roszman1. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [Puromycin (treated)](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/Puromycin.html) | reaction velocity against substrate concentration for the enzyme treated with Puromycin (12 rows) | Treloar, M. A. (1974). Effects of Puromycin on galactosyltransferase in Golgi membranes. M.Sc. thesis, University of Toronto. Fit printed in Bates, D. M. & Watts, D. G. (1988). Nonlinear Regression Analysis and Its Applications. New York: Wiley, section 2.3 (Vm 212.7, K 0.06412). Copy from R's datasets package (Puromycin). | Published facts; the copy in R's datasets package is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [leaflife (smatr)](https://cran.r-project.org/package=smatr) | leaf mass per area and leaf lifespan of 67 plant species at four sites (log10 of both) | Wright, I. J., Westoby, M. & Reich, P. B. (2002). Convergence towards higher leaf mass per area in dry and nutrient-poor habitats has different consequences for leaf life span. Journal of Ecology 90, 534-543. Used in Warton, D. I. et al. (2006). Bivariate line-fitting methods for allometry. Biological Reviews 81, 259-291. Shipped with the R package smatr. | GPL-2 (smatr). Not stored here: read from smatr, so it needs R. |
| [creatinine (mcr)](https://cran.r-project.org/package=mcr) | creatinine measured in serum and in plasma of the same samples (108 complete pairs) | Shipped with the R package mcr (Manuilova, E., Schuetzenmeister, A. & Model, F., Roche Diagnostics), the package's method-comparison example. | GPL-3 (mcr). Not stored here: read from mcr, so it needs R. |
| [stagnant (segmented)](https://doi.org/10.1093/biomet/58.3.525) | log band height against log flow rate of water over a stagnant band (28 points) | Bacon, D. W. & Watts, D. G. (1971). Estimating the transition between two intersecting straight lines. Biometrika 58, 525-534. Shipped with the R package segmented. | Facts published in 1971; the copy in segmented is GPL. Not stored here: read from segmented, so it needs R. |
| [Seatbelts](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/UKDriverDeaths.html) | drivers killed or seriously injured in Great Britain each month, 1969-1984; the seat-belt law from February 1983 (month 170) | Harvey, A. C. & Durbin, J. (1986). The effects of seat belt legislation on British road casualties: a case study in structural time series modelling. Journal of the Royal Statistical Society A 149, 187-227. Copy from R's datasets package (Seatbelts). | Official UK road casualty counts published in the paper; the copy in R's datasets package is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [Engel food expenditure](https://www.statsmodels.org/stable/datasets/generated/engel.html) | household income and food expenditure of 235 Belgian working-class households (1857) | Engel, E. (1857). Die Productions- und Consumptionsverhaeltnisse des Koenigreichs Sachsen. Analysed with quantile regression in Koenker, R. & Bassett, G. (1982). Robust tests for heteroscedasticity based on regression quantiles. Econometrica 50, 43-61. Copy in statsmodels (statsmodels.datasets.engel). | Public domain (published 1857). Not stored here: read from statsmodels. |
| [Dialyzer (nlme)](https://cran.r-project.org/package=nlme) | ultrafiltration rate of 20 high-flux haemodialyzers at 7 transmembrane pressures, at two blood flow rates (140 rows) | Vonesh, E. F. & Carter, R. L. (1992). Mixed-effects nonlinear regression for unbalanced repeated measures. Biometrics 48, 1-17. Analysed with variance functions in Pinheiro, J. C. & Bates, D. M. (2000). Mixed-Effects Models in S and S-PLUS. Springer, section 5.2. Shipped with the R package nlme. | GPL (nlme). Not stored here: read from nlme, so it needs R. |
| [Lake Huron](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/LakeHuron.html) | annual level of Lake Huron in feet, 1875-1972 | Brockwell, P. J. & Davis, R. A. (1991). Time Series and Forecasting Methods, 2nd ed. Springer, pp. 328-329 (from the US Army Corps of Engineers). Copy from R's datasets package (LakeHuron). | US Government measurements (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [swiss](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/swiss.html) | fertility and five social measures of 47 French-speaking provinces of Switzerland in about 1888 | Mosteller, F. & Tukey, J. W. (1977). Data Analysis and Regression. Addison-Wesley, pp. 549-551 (from the Office of Population Research, Princeton, 1976). Copy from R's datasets package (swiss). | Official 1888 statistics (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [birthwt (MASS)](https://cran.r-project.org/package=MASS) | 189 births at Baystate Medical Center, Springfield, Massachusetts (1986): low birth weight, the mother's age, weight and smoking | Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Shipped with the R package MASS (Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed.). | GPL-2 \| GPL-3 (MASS). Not stored here: read from MASS, so it needs R. |
| [warpbreaks](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/warpbreaks.html) | the number of warp breaks per loom for two wools (A, B) at three tensions (L, M, H), 9 looms each | Tippett, L. H. C. (1950). Technological Applications of Statistics. Wiley, p. 106. Copy from R's datasets package (warpbreaks). | Published 1950 (facts). The copy in R's datasets package is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [sleepstudy (lme4)](https://doi.org/10.18637/jss.v067.i01) | average reaction time of 18 truck drivers on each of 10 days of sleep deprivation (180 rows) | Belenky, G. et al. (2003). Patterns of performance degradation and restoration during sleep restriction and subsequent recovery. Journal of Sleep Research 12, 1-12. Analysed in Bates, D., Maechler, M., Bolker, B. & Walker, S. (2015). Fitting linear mixed-effects models using lme4. Journal of Statistical Software 67(1) (CC BY). Shipped with the R package lme4. | GPL (>= 2) (lme4). Not stored here: read from lme4, so it needs R. |
| [rat liver glycogen](https://www.worldcat.org/title/biometry/oclc/7203719) | glycogen in the livers of 6 rats, 2 on each of 3 treatments (control, glucose, glucose and fructose), 3 preparations per liver and 2 readings per preparation (36 rows) | Sokal, R. R. & Rohlf, F. J. (1981). Biometry, 2nd ed. Freeman, Box 10.1 (nested ANOVA: treatments SS 1557.56 on 2 df, rats within treatments SS 797.67 on 3 df, F = 2.929); the same analysis in Crawley, M. J. (2007). The R Book. Wiley, chapter 11. | Facts published in the book (36 numbers), typed from it; not covered by copyright. |
| [iris](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/iris.html) | sepal and petal length and width of 50 flowers of each of three iris species | Anderson, E. (1935). The irises of the Gaspe Peninsula. Bulletin of the American Iris Society 59, 2-5; Fisher, R. A. (1936). The use of multiple measurements in taxonomic problems. Annals of Eugenics 7, 179-188. Copy from R's datasets package (iris). | Published 1935 (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [udca (survival)](https://cran.r-project.org/package=survival) | 170 patients with primary biliary cirrhosis in a trial of ursodeoxycholic acid: dates of entry, last follow-up and death | Lindor, K. D. et al. (1994). Ursodeoxycholic acid in the treatment of primary biliary cirrhosis. Gastroenterology 106, 1284-1290. Shipped with R's survival package (udca). | LGPL (>= 2) (survival). Not stored here: read from survival, so it needs R. |
| [mgus2 (survival)](https://cran.r-project.org/package=survival) | 1384 patients with monoclonal gammopathy: months to progression to a plasma cell malignancy (pcm) or death without it | Kyle, R. A. et al. (2002). A long-term study of prognosis in monoclonal gammopathy of undetermined significance. New England Journal of Medicine 346, 564-569; the competing-risks example of Therneau, T. M., "Multi-state models and competing risks" (survival vignette). Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published data in an LGPL package. Not stored here: read from the installed R package, so it needs R. |
| [lung (survival)](https://cran.r-project.org/package=survival) | 228 patients with advanced lung cancer (NCCTG): days to death or the end of follow-up, age, sex and ECOG performance score | Loprinzi, C. L. et al. (1994). Prospective evaluation of prognostic variables from patient-completed questionnaires. Journal of Clinical Oncology 12, 601-607. Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published trial data in an LGPL package. Not stored here: read from the installed R package, so it needs R. |
| [bfeed (KMsurv)](https://cran.r-project.org/package=KMsurv) | 927 first-born children of the National Longitudinal Survey of Youth: weeks of breast feeding and whether it was ended | Klein, J. P. & Moeschberger, M. L. (2003). Survival Analysis: Techniques for Censored and Truncated Data, 2nd ed. Springer, section 1.14 and the life table of section 5.4. Shipped with the R package KMsurv. | GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R. |
| [Channing House (KMsurv)](https://cran.r-project.org/package=KMsurv) | residents of Channing House, a retirement centre in Palo Alto: age (months) on entry and at death or the end of the study (the 4 rows that left on the day they came are left out) | Hyde, J. (1980). Testing survival with incomplete observations. In Biostatistics Casebook, Wiley; Klein & Moeschberger (2003), section 4.6 (delayed entry). Shipped with the R package KMsurv. | GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R. |
| [veteran (survival)](https://cran.r-project.org/package=survival) | 137 men in the Veterans' Administration lung cancer trial: standard or test chemotherapy, cell type, Karnofsky score, days to death | Kalbfleisch, J. D. & Prentice, R. L. (2002). The Statistical Analysis of Failure Time Data, 2nd ed. Wiley. Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published trial data in an LGPL package. Not stored here: read from the installed R package, so it needs R. |
| [Stanford heart transplant (survival)](https://cran.r-project.org/package=survival) | 103 patients waiting for a heart transplant, as start-stop rows (one row before and one after a transplant): age, earlier surgery, transplant | Crowley, J. & Hu, M. (1977). Covariance analysis of heart transplant survival data. Journal of the American Statistical Association 72, 27-36; analysed in Therneau, T. M. & Grambsch, P. M. (2000). Modeling Survival Data. Springer, section 3.7. Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published data in an LGPL package. Not stored here: read from the installed R package, so it needs R. |
| [larynx (KMsurv)](https://cran.r-project.org/package=KMsurv) | 90 men with cancer of the larynx: stage, age, months to death | Kardaun, O. (1983). Statistical survival analysis of male larynx-cancer patients: a case study. Statistica Neerlandica 37, 103-125; Klein & Moeschberger (2003), chapter 12 (parametric models). Shipped with the R package KMsurv. | GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R. |
| [BCG trials (metadat)](https://doi.org/10.18637/jss.v036.i03) | 13 trials of the BCG vaccine against tuberculosis: cases among the vaccinated and the unvaccinated, the absolute latitude of the place and how people were put into the groups | Colditz, G. A. et al. (1994). Efficacy of BCG vaccine in the prevention of tuberculosis: meta-analysis of the published literature. JAMA 271, 698-702. Analysed in Viechtbauer, W. (2010). Conducting meta-analyses in R with the metafor package. Journal of Statistical Software 36(3), 1-48 (CC BY 3.0). Shipped with the R package metadat (dat.bcg); a copy is the practice table bcg. | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [passive smoking (metadat)](https://doi.org/10.1136/bmj.315.7114.980) | 37 studies of lung cancer in non-smoking women whose husbands smoked: the odds ratio of each study with its 95 % interval | Hackshaw, A. K., Law, M. R. & Wald, N. J. (1997). The accumulated evidence on lung cancer and environmental tobacco smoke. BMJ 315, 980-988 (pooled excess risk 24 %, 95 % CI 13 % to 36 %). Shipped with the R package metadat (dat.hackshaw1998); a copy is the practice table passive_smoking. | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [Normand 1999 (metadat)](https://cran.r-project.org/package=metadat) | 9 trials of specialist stroke rehabilitation: average length of hospital stay (days), its standard deviation and the patients in each group | Normand, S.-L. T. (1999). Meta-analysis: formulating, evaluating, combining, and reporting. Statistics in Medicine 18, 321-359. Shipped with the R package metadat (dat.normand1999). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [Curtis 1998 (metadat)](https://cran.r-project.org/package=metadat) | 102 experiments on the growth of woody plants under raised and ambient CO2: average biomass, its standard deviation and the plants in each group | Curtis, P. S. & Wang, X. (1998). A meta-analysis of elevated CO2 effects on woody plant mass, form, and physiology. Oecologia 113, 299-313; the log response ratio of Hedges, L. V., Gurevitch, J. & Curtis, P. S. (1999). Ecology 80, 1150-1156. Shipped with the R package metadat (dat.curtis1998). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [Hart 1999 (metadat)](https://cran.r-project.org/package=metadat) | 6 trials of warfarin against placebo in atrial fibrillation: strokes and patient-years in each group | Hart, R. G., Benavente, O., McBride, R. & Pearce, L. A. (1999). Antithrombotic therapy to prevent stroke in patients with atrial fibrillation: a meta-analysis. Annals of Internal Medicine 131, 492-501. Shipped with the R package metadat (dat.hart1999). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [McDaniel 1994 (metadat)](https://cran.r-project.org/package=metadat) | 160 studies of the correlation between employment interview ratings and job performance, with the number of people in each | McDaniel, M. A., Whetzel, D. L., Schmidt, F. L. & Maurer, S. D. (1994). The validity of employment interviews: a comprehensive review and meta-analysis. Journal of Applied Psychology 79, 599-616. Shipped with the R package metadat (dat.mcdaniel1994). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [checks against R (no published example)](https://doi.org/10.1186/1471-2288-11-94) | no data: the inputs are written in the code, and R (or SciPy with the same seed, or python-control) is the reference; used where no published worked example was read | simplydata's reliability study. Simulation checks follow Arnold, B. F., Hogan, D. R., Colford, J. M. & Hubbard, A. E. (2011). Simulation methods to estimate design power. BMC Medical Research Methodology 11, 94. | No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored. |
| [pwr manual and vignette](https://cran.r-project.org/package=pwr) | the pwr.f2.test example of the pwr vignette (Kutner et al., exercise 8.43): two columns added, R squared 0.3, significance 0.001 | Champely, S. et al. pwr: Basic Functions for Power Analysis, vignette (pwr.f2.test); Kutner, M. H., Nachtsheim, C. J., Neter, J. & Li, W. (2005). Applied Linear Statistical Models, 5th ed., exercise 8.43. | No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored. |
| [presize paper (JOSS)](https://doi.org/10.21105/joss.03118) | the worked example of presize's paper: the values needed for a 95 % Wilson interval of a percent near 15 % that is 5 points wide | Haynes, A. G., Lenz, A., Stalder, O. & Limacher, A. (2021). presize: An R-package for precision-based sample size calculation in clinical research. Journal of Open Source Software 6(60), 3118 (CC BY 4.0). | No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored. |
| [Stata power manuals](https://www.stata.com/manuals/pss-2powerlogrank.pdf) | worked examples of the Stata power manuals: the log-rank test by Schoenfeld's and by Freedman's formula, and two averages in clusters | StataCorp. Stata Power, Precision, and Sample-Size Reference Manual: [PSS-2] power logrank, examples 1, 2 and 5 (example 5 from Machin, D. et al. (2009). Sample Size Tables for Clinical Studies, 3rd ed., p. 91); [PSS-2] power twomeans, cluster, example 1 (from Ahn, C., Heo, M. & Zhang, S. (2015). Sample Size Calculations for Clustered and Longitudinal Outcomes in Clinical Research, p. 37). | No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored. |
| [G*Power 3.1 manual](https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower) | worked examples of the G*Power manual: logistic regression with one normal column (chapter 29.4) and the multiple-regression F test (chapter 13.3.1, Cohen 1988 example 9.1) | Faul, F., Erdfelder, E., Buchner, A. & Lang, A.-G. G*Power 3.1 manual (2023), sections 13.3.1 and 29.4; Faul et al. (2009). Behavior Research Methods 41, 1149-1160; Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences, 2nd ed., p. 424. | No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored. |
| [Bland, sample size in cluster trials](https://www-users.york.ac.uk/~mb55/clust/bupa.htm) | the design effect of a cluster trial with 30 people in each cluster and ICC 0.05 | Bland, J. M. Sample size in guidelines trials (University of York), section "Sample size in cluster randomized studies"; Kerry, S. M. & Bland, J. M. (1998). BMJ 316, 549. | No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored. |
| [BCI (vegan)](https://doi.org/10.1126/science.1066854) | Trees counted in 50 one-hectare plots of the Barro Colorado Island forest plot, Panama: 225 species | Condit, R. et al. (2002). Beta-diversity in tropical forest trees. Science 295, 666-669. Shipped with the R package vegan (BCI). | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [mite (vegan)](https://doi.org/10.1007/BF00714196) | Oribatid mites counted in 70 soil cores of a peat bog: 35 species (whole counts with many zeros), and the microtopography of each core (Topo: blanket or hummock) | Borcard, D. & Legendre, P. (1994). Environmental control and spatial structure in ecological communities: an example using oribatid mites (Acari, Oribatei). Environmental and Ecological Statistics 1, 37-61. Shipped with the R package vegan (mite, mite.env). | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [dune (vegan)](https://cran.r-project.org/package=vegan) | 20 meadow plots in the Netherlands: the cover of 30 plant species, and how each meadow was managed (Management) and the thickness of the soil's A1 horizon | Jongman, R. H., ter Braak, C. J. F. & van Tongeren, O. F. R. (1987, 1995). Data Analysis in Community and Landscape Ecology. Pudoc / Cambridge University Press. Shipped with the R package vegan (dune, dune.env). | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [varespec and varechem (vegan)](https://doi.org/10.2307/3236351) | 24 lichen pastures in Finnish Lapland: the cover of 44 plant and lichen species and 14 soil measurements (N, P, K ...) | Väre, H., Ohtonen, R. & Oksanen, J. (1995). Effects of reindeer grazing on understorey vegetation in dry Pinus sylvestris forests. Journal of Vegetation Science 6, 523-530. Shipped with the R package vegan (varespec, varechem); analysed in Oksanen, J. (2015). Multivariate analysis of ecological communities in R: vegan tutorial. | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [crabs (MASS)](https://doi.org/10.1071/ZO9740417) | 200 Leptograpsus crabs from Western Australia: five shell measurements, two colour forms and both sexes (four groups of 50) | Campbell, N. A. & Mahon, R. J. (1974). A multivariate study of variation in two species of rock crab of genus Leptograpsus. Australian Journal of Zoology 22, 417-425; Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed., section 12.1. Shipped with the R package MASS. | GPL-2 \| GPL-3 (MASS, which comes with R); read from the installed package, so it needs R. |
| [wg93 (ca)](https://doi.org/10.18637/jss.v020.i03) | 871 answers of the 1993 International Social Survey Programme (West Germany) to four questions on science and the environment (A to D, answers 1 to 5) | Greenacre, M. (2007). Correspondence Analysis in Practice, 2nd ed. Chapman & Hall/CRC; Nenadić, O. & Greenacre, M. (2007). Correspondence analysis in R, with two- and three-dimensional graphics: the ca package. Journal of Statistical Software 20(3) (CC BY). Shipped with the R package ca (wg93). | GPL (>= 2) (ca); read from the installed package, so it needs R. |
| [Holzinger & Swineford 1939 (lavaan)](https://doi.org/10.18637/jss.v048.i02) | 301 seventh- and eighth-grade pupils of two schools near Chicago (Pasteur and Grant-White) in 1937: the scores of nine mental ability tests (visual perception, cubes, lozenges, paragraph comprehension, sentence completion, word meaning, speeded addition, speeded counting of dots, speeded discrimination of straight and curved capitals) | Holzinger, K. J. & Swineford, F. (1939). A study in factor analysis: the stability of a bi-factor solution. Supplementary Educational Monographs 48. University of Chicago. The nine-test version and the three-factor model with its fit are in Rosseel, Y. (2012). lavaan: an R package for structural equation modeling. Journal of Statistical Software 48(2), 1-36 (CC BY 3.0). Shipped with the R package lavaan (HolzingerSwineford1939). | Published test scores (1939, facts). Read here from R lavaan (its copy is GPL (>= 2)), so the cases need R. The practice table ability_tests is made up, with the same columns. |
| [turtles (circular)](https://doi.org/10.1007/s002650100396) | the directions from which 10 green sea turtles, displaced to the open sea, came back to Ascension Island (degrees) | Luschi, P. et al. (2001). Testing the navigational abilities of ocean migrants: displacement experiments on green sea turtles (Chelonia mydas). Behavioral Ecology and Sociobiology 50, 528-534. Shipped with the R package circular (turtles; Agostinelli & Lund). | GPL-2 (circular); read from the installed package, so it needs R. |
| [ICU arrivals (circular)](https://cran.r-project.org/package=circular) | the time of day (24-hour clock) at which 254 patients arrived at an intensive care unit over about 12 months | Cox, D. R. & Lewis, P. A. W. (1966). The Statistical Analysis of Series of Events. Methuen, pp. 254-255; Fisher, N. I. (1993). Statistical Analysis of Circular Data. Cambridge University Press, data set B.1. Shipped with the R package circular (fisherB1c). | GPL-2 (circular); read from the installed package, so it needs R. |
| [meuse (sp)](https://cran.r-project.org/package=sp) | 155 topsoil samples in the flood plain of the river Meuse near Stein (NL): where each was taken (x, y in metres, RD New) and its zinc in mg/kg | Rikken, M. G. J. & Van Rijn, R. P. G. (1993). Soil pollution with heavy metals: an inquiry into spatial variation, cost of mapping and the risk evaluation of copper, cadmium, lead and zinc in the floodplains of the Meuse west of Stein. Doctoraalveldwerkverslag, Utrecht University. Shipped with the R package sp (meuse); its variogram is the gstat vignette's example (Pebesma 2004, Computers & Geosciences 30, 683-691). | GPL-2 \| GPL-3 (sp); read from the installed package, so it needs R. |
| [meuse in longitude and latitude (sp, sf)](https://doi.org/10.32614/RJ-2018-009) | the same 155 meuse samples, their places turned from the Dutch grid (RD New, EPSG 28992) into longitude and latitude (EPSG 4326) by R sf::st_transform | As meuse (sp) above; the transformation by PROJ through R sf (Pebesma, E. (2018). Simple Features for R. The R Journal 10(1), 439-446). | GPL-2 \| GPL-3 (sp); read from the installed package and transformed there, so it needs R. |
| [Port Pirie (ismev)](https://doi.org/10.1007/978-1-4471-3675-0) | the highest sea level of each year at Port Pirie, South Australia, 1923-1987 (metres) | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, Springer, section 3.4.1. Shipped with the R package ismev (portpirie); simplydata's practice table sea_levels is made up after it. | GPL (>= 2) (ismev); read from the installed package, so it needs R. |
| [Coles rain (ismev)](https://doi.org/10.1007/978-1-4471-3675-0) | 17,531 daily rainfall totals at one site in south-west England, 1914-1962 (mm) | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, Springer, section 4.4.1. Shipped with the R package ismev (rain). | GPL (>= 2) (ismev); read from the installed package, so it needs R. |
| [Quetelet's chest sizes](https://cran.r-project.org/package=HistData) | the chest girth (inches) of 5738 Scottish soldiers, as a table of counts: 16 girths and how many soldiers had each | Quetelet, A. (1846). Lettres a S.A.R. le Duc Regnant de Saxe-Cobourg et Gotha, sur la theorie des probabilites. Hayez, Brussels; Stigler, S. M. (1986). The History of Statistics. Harvard University Press. The same counts as R HistData's ChestSizes. | Published 1817 and 1846 (facts); numbers stored unchanged. |
| [AirPassengers](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/AirPassengers.html) | the monthly totals of international airline passengers (thousands), 1949-1960 | Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G). Copy from R's datasets package (AirPassengers). | Published 1976 (facts); R's datasets copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [hedenfalk (qvalue)](https://doi.org/10.1073/pnas.1530509100) | 3170 p-values of genes compared between BRCA1 and BRCA2 breast tumours | Hedenfalk, I. et al. (2001). Gene-expression profiles in hereditary breast cancer. New England Journal of Medicine 344, 539-548; the p-values of Storey & Tibshirani (2003), PNAS 100, 9440-9445, as R qvalue ships them (hedenfalk). | LGPL (qvalue); read from the installed package, so it needs R. |
| [rounding first base](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/friedman.test.html) | the times (seconds) of 22 baseball players running to second base by three routes (round out, narrow angle, wide angle): each player ran all three | Hollander, M. & Wolfe, D. A. (1973). Nonparametric Statistical Methods. Wiley, p. 140; the example of R's friedman.test help (RoundingTimes; Friedman chi-squared 11.143, which these numbers give). | Published 1973 (facts); numbers stored unchanged. |
| [smokers (Fleiss)](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/pairwise.prop.test.html) | smokers among patients with lung cancer in four groups: counts out of totals | Fleiss, J. L. (1981). Statistical Methods for Rates and Proportions, 2nd ed. Wiley, p. 139; the example of R's prop.test and pairwise.prop.test help. | Published 1981 (facts); numbers stored unchanged. |
| [designs (no data)](https://doi.org/10.1016/S0140-6736(02)07683-3) | no data: a randomisation list and a design table are made, and their published properties checked (blocks hold every group equally often; Yates' standard order) | Schulz, K. F. & Grimes, D. A. (2002). Generation of allocation sequences in randomised trials: chance, not choice. The Lancet 359, 515-519; Montgomery, D. C. (2017). Design and Analysis of Experiments, 9th ed. Wiley, the standard order of a 2^k design. | No data stored (facts of the methods). |
| [api stratified sample (survey)](https://cran.r-project.org/package=survey) | 200 California schools sampled at random within school type (100 elementary, 50 middle, 50 high): the Academic Performance Index of 2000 and 1999, enrolment, free meals, English learners, the sampling weight (pw) and the number of schools of each type (fpc) | California Department of Education, Academic Performance Index 2000; the stratified sample of R's survey package (apistrat; Lumley, T. (2010). Complex Surveys: A Guide to Analysis Using R. Wiley). | Public data of the California Department of Education; the survey package copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [nhanes (mice)](https://doi.org/10.18637/jss.v045.i03) | 25 people of the US National Health and Nutrition Examination Survey: age group, body mass index, hypertension and cholesterol, with empty cells | Schafer, J. L. (1997). Analysis of Incomplete Multivariate Data. Chapman & Hall, p. 237; the nhanes data of R mice and its patterns in van Buuren, S. & Groothuis-Oudshoorn, K. (2011). mice: Multivariate Imputation by Chained Equations in R. Journal of Statistical Software 45(3). | A US Government survey (public domain); the mice copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [professional challenges (HH)](https://doi.org/10.18637/jss.v057.i05) | 565 answers to a survey question on professional challenges, from strongly disagree to strongly agree, in total and by employment sector, race, gender and more (counts of each answer) | Heiberger, R. M. & Robbins, N. B. (2014). Design of Diverging Stacked Bar Charts for Likert Scales and Other Applications. Journal of Statistical Software 57(5); R HH (ProfChal). | The JSS article is CC BY; the HH copy is GPL (>= 2). Not stored here: read from the installed R package, so it needs R. |
| [api cluster sample (survey)](https://cran.r-project.org/package=survey) | 183 California schools in 15 school districts sampled at random (a one-stage cluster sample): the Academic Performance Index of 2000, enrolment, the weight (pw) and the number of districts (fpc) | California Department of Education, Academic Performance Index 2000; R's survey package (apiclus1; Lumley 2010). | Public data of the California Department of Education; the survey package copy is GPL-2 \| GPL-3. Not stored here: read from the installed R package, so it needs R. |
| [lalonde](https://doi.org/10.1080/01621459.1999.10473858) | 614 men: 185 in the National Supported Work job training and 429 from a population survey (PSID), with age, schooling, race, marriage, degree and earnings in 1974, 1975 and 1978 | LaLonde, R. J. (1986). Evaluating the econometric evaluations of training programs with experimental data. American Economic Review 76, 604-620; Dehejia, R. H. & Wahba, S. (1999). Journal of the American Statistical Association 94, 1053-1062. As shipped by the R package MatchIt (lalonde). | Public study data (US Department of Labor NSW); the MatchIt copy is GPL (>= 2). The practice table job_training is made up, with the same columns. Not stored here: read from the installed R package, so it needs R. |
| [dry cat food and FLUTD](https://cran.r-project.org/package=epiR) | a cross-sectional study of dry cat food and feline lower urinary tract disease: 13 of 2176 cats on dry food and 5 of 3354 on other food had the disease | Willeberg, P. (1977). Animal disease information processing: epidemiologic analyses of the feline urologic syndrome. Acta Veterinaria Scandinavica 18 (Suppl. 64), 1-48; the first example of R epiR::epi.2by2. | Published counts (facts); stored unchanged. |
| [Down syndrome by birth order](https://cran.r-project.org/package=epitools) | Down syndrome cases and live births in Michigan by birth order and mother's age (6 x 6 bands) | Selvin, S. (2004). Statistical Analysis of Epidemiologic Data, 3rd ed. Oxford University Press; the example of R epitools::ageadjust.direct (Fay & Feuer 1997, Statistics in Medicine 16, 791-801). | Published counts (facts); stored unchanged. |
| [JOBS II (mediation)](https://doi.org/10.18637/jss.v059.i05) | 899 unemployed workers in a randomised job-search workshop: treatment, job-search confidence, depression six months later, economic hardship, sex and age (6 of the columns) | Vinokur, A. D., Price, R. H. & Schul, Y. (1995). American Journal of Community Psychology 23, 39-74; Tingley, D. et al. (2014). mediation: R Package for Causal Mediation Analysis. Journal of Statistical Software 59(5). As shipped by the R package mediation (jobs). | Human-subject records distributed by ICPSR (study 2739), whose terms do not allow passing them on, and GPL (>= 2) in the R package mediation. Not stored here: read from the installed mediation package, so it needs R. (The practice table job_search is made up, with the same columns.) |
| [bioequivalence reference datasets](https://doi.org/10.1208/s12248-014-9661-0) | three 2 x 2 crossover bioequivalence studies (AUC of a test and a reference formulation): A, 18 subjects (Sauter et al. 1992); B, 18 subjects (Clayton & Leslie 1981); C, 13 subjects (B with subjects removed, unbalanced) | Schütz, H., Labes, D. & Fuglsang, A. (2014). Reference Datasets for 2-Treatment, 2-Sequence, 2-Period Bioequivalence Studies. The AAPS Journal 16, 1292-1297, supplementary data sets A, B and C (PMC4389751). | (c) AAPS 2014, with no open licence for the article or its supplementary files, so not shipped (DATA_LICENSES.md). simplydata was tested on them on 2026-11-21 (all three ratios and 90 % intervals equal to Table II at its 2 printed decimals of percent, and to R lm() to 1e-9). To rerun the cases, save the data as a CSV file (columns dataset, subject, period, formulation, auc) and name it in the environment variable SIMPLYDATA_SCHUTZ2014_FILE; without it they are skipped. |
| [airquality (R datasets)](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/airquality.html) | daily air quality in New York, May to September 1973: ozone (37 empty cells), solar radiation (7 empty), wind and temperature | Chambers, J. M. et al. (1983). Graphical Methods for Data Analysis. Wadsworth; data from the New York State Department of Conservation and the National Weather Service. R's datasets package. | Public data; R's datasets package is GPL-2 \| GPL-3; read from R, so it needs R. |
| [lung with weight loss (survival)](https://doi.org/10.1200/JCO.1994.12.3.601) | 228 patients with advanced lung cancer: survival time, status, age, sex, Karnofsky score (empty cells) and weight loss (14 empty cells) | Loprinzi, C. L. et al. (1994). Journal of Clinical Oncology 12, 601-607. As shipped by the R package survival (lung). | LGPL (>= 2) (survival); read from the installed package, so it needs R. |
| closed form (no data) | no data: systems, waves and window shapes made from a formula, checked against the answer worked out by hand from the same formula | The formulas are worked out for the check in simplydata's validation/cases_underneath_signals.py. | No data, so no licence; the worked answers are the same as simplydata's (see LICENSE). |
| [yearly sunspot numbers](https://www.statsmodels.org/stable/datasets/generated/sunspots.html) | 309 yearly mean sunspot numbers (Wolf's relative numbers), 1700 to 2008 | NOAA National Geophysical Data Center, yearly sunspot numbers (compiled from the Royal Observatory of Belgium, SIDC). Copy from statsmodels (statsmodels.datasets.sunspots). The solar cycle of about 11 years: Schwabe, H. (1844). Astronomische Nachrichten 21, 233-236; its average length 11.0 years: Hathaway, D. H. (2015). The solar cycle. Living Reviews in Solar Physics 12, 4. | Public domain (a US Government work), as statsmodels states for this dataset. Not stored here: read from the installed statsmodels. |
| [US inflation and unemployment](https://www.statsmodels.org/stable/datasets/generated/macrodata.html) | 203 quarters of the US economy, 1959 to 2009: inflation and the unemployment rate (2 of 14 columns) | Federal Reserve Bank of St. Louis (FRED) and the US Bureau of Labor Statistics, compiled by S. Seabold. Copy from statsmodels (statsmodels.datasets.macrodata). | Public domain (a US Government work), as statsmodels states for this dataset. Not stored here: read from the installed statsmodels. |
| [El Nino sea surface temperatures](https://www.statsmodels.org/stable/datasets/generated/elnino.html) | 732 monthly averages of the sea surface temperature (degrees Celsius) of the Pacific between 0 and 10 degrees south and 90 and 80 degrees west (Nino 1+2), January 1950 to December 2010 | NOAA Climate Prediction Center, ERSST v3b, Nino 1+2 index. Copy from statsmodels (statsmodels.datasets.elnino). | Public domain (a US Government work), as statsmodels states for this dataset. Not stored here: read from the installed statsmodels. |
| [Newton's cubic](https://doi.org/10.1137/1037125) | the cubic x^3 - 2x - 5 = 0, Newton's own example for his method; its root 2.09455148 | Newton, I. (1669). De analysi per aequationes numero terminorum infinitas, published by Wallis, J. (1685). A Treatise of Algebra, chapter 94; the root to 8 decimals as in Ypma, T. J. (1995). Historical development of the Newton-Raphson method. SIAM Review 37(4), 531-551. | No data: a published worked example (facts); only the numbers printed there are quoted, nothing is stored. |
| [Rosenbrock's valley](https://doi.org/10.1093/comjnl/3.3.175) | Rosenbrock's function 100 (y - x^2)^2 + (1 - x)^2 from the start (-1.2, 1); its smallest value 0, at x = 1, y = 1 | Rosenbrock, H. H. (1960). An automatic method for finding the greatest or least value of a function. The Computer Journal 3(3), 175-184. | No data: a published worked example (facts); only the numbers printed there are quoted, nothing is stored. |
| [Wyndor Glass linear program](https://www.mheducation.com/) | the Wyndor Glass Co. product mix: largest 3 x1 + 5 x2 with x1 <= 4, 2 x2 <= 12, 3 x1 + 2 x2 <= 18; the answer x1 = 2, x2 = 6, profit 36, shadow prices 0, 1.5 and 1 | Hillier, F. S. & Lieberman, G. J. Introduction to Operations Research (10th ed., 2015), sections 3.1 and 4.7, McGraw-Hill. | No data: a published worked example (facts); only the numbers printed there are quoted, nothing is stored. |
