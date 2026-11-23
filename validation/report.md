# simplydata reliability report

Made by `python validation/make_report.py` on 2026-11-23. Generated: do not edit by hand.

Each simplydata word is run on real, published data and compared with the published answer, with the package simplydata uses underneath called directly, and with R. Each "same underneath" box of the manual is run next to its word and compared too. How it works, and the datasets with their licences: [validation/README.md](README.md).

**2751 checks passed, 7 explained differences, 0 failed, 3 skipped** (skipped: R or an R package is not installed on this computer, or, for 3, the data may not be passed on and no file was given; an explained difference falls short of its tolerance for a stated reason, a limit of precision, and is listed with that reason).

## Setup

| | |
|---|---|
| system | Windows 11 (AMD64) |
| Python | 3.12.10 |
| simplydata | 0.2.0 (imported from src/simplydata of this copy) |
| pandas | 3.1.1 |
| polars | 2.1.0 |
| narwhals | 2.28.0 |
| numpy | 2.5.4 |
| scipy | 1.18.1 |
| statsmodels | 0.15.0 |
| matplotlib | 3.11.2 |
| seaborn | 0.13.2 |
| rpy2 | 3.6.9 |
| R | 4.6.2 (2026-10-29 ucrt) |

## 1. Published and real data

Kinds: *published* = real data with a published or certified answer; *real data* = real data, compared with the parent package and R; *made-up* = a made-up edge case (empty cells, no rows left, an exact line) that no real dataset tests.

### `table.fit_line`

**straight line through 36 ozone calibration points** (published; data: NIST Norris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | NIST certified | 1.00211681802045 | 1.00211681802045 | at least 9 digits (LRE 14.4) | pass |
| intercept | NIST certified | -0.262323073773985 | -0.262323073774029 | at least 9 digits (LRE 12.8) | pass |
| slope standard error | NIST certified | 0.000429796848200648 | 0.000429796848199937 | at least 9 digits (LRE 11.8) | pass |
| intercept standard error | NIST certified | 0.232818234301538 | 0.232818234301152 | at least 9 digits (LRE 11.8) | pass |
| R squared | NIST certified | 0.999993745883712 | 0.999993745883712 | at least 9 digits (LRE 15.0) | pass |
| slope | SciPy stats.linregress | 1.00211681802045 | 1.00211681802045 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | -0.262323073773985 | -0.262323073773985 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.000429796848200648 | 0.000429796848200648 | relative 1e-09 | pass |
| intercept standard error | SciPy stats.linregress | 0.232818234301538 | 0.232818234301538 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.999993745883712 | 0.999993745883712 | relative 1e-09 | pass |
| slope | R | 1.00211681802045 | 1.00211681802045 | relative 1e-09 | pass |
| intercept | R | -0.262323073773985 | -0.262323073774117 | relative 1e-09 | pass |
| slope standard error | R | 0.000429796848200648 | 0.00042979684819994 | relative 1e-09 | pass |
| intercept standard error | R | 0.232818234301538 | 0.232818234301154 | relative 1e-09 | pass |
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
| R squared | Anscombe (1973) | 0.666242033727484 | 0.667 | within 0.001 (printed rounding) | pass |
| slope | SciPy stats.linregress | 0.5 | 0.5 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | 3.00090909090909 | 3.00090909090909 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.117963745967641 | 0.117963745967641 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.666242033727484 | 0.666242033727484 | relative 1e-09 | pass |

Note: The paper prints the fit rounded (3 + 0.5 x); its sets agree with it to within about one unit of the last printed digit, so the check allows the printed rounding plus that much.

**Anscombe's set 3: the same line through four different patterns** (published; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | Anscombe (1973) | 0.499727272727273 | 0.5 | within 0.001 (printed rounding) | pass |
| intercept | Anscombe (1973) | 3.00245454545455 | 3 | within 0.01 (printed rounding) | pass |
| slope standard error | Anscombe (1973) | 0.117877662221002 | 0.118 | within 0.001 (printed rounding) | pass |
| R squared | Anscombe (1973) | 0.666324041066559 | 0.667 | within 0.001 (printed rounding) | pass |
| slope | SciPy stats.linregress | 0.499727272727273 | 0.499727272727273 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | 3.00245454545455 | 3.00245454545455 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.117877662221002 | 0.117877662221002 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.666324041066559 | 0.666324041066559 | relative 1e-09 | pass |

Note: The paper prints the fit rounded (3 + 0.5 x); its sets agree with it to within about one unit of the last printed digit, so the check allows the printed rounding plus that much.

**Anscombe's set 4: the same line through four different patterns** (published; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | Anscombe (1973) | 0.499909090909091 | 0.5 | within 0.001 (printed rounding) | pass |
| intercept | Anscombe (1973) | 3.00172727272727 | 3 | within 0.01 (printed rounding) | pass |
| slope standard error | Anscombe (1973) | 0.117818941729685 | 0.118 | within 0.001 (printed rounding) | pass |
| R squared | Anscombe (1973) | 0.666707256898466 | 0.667 | within 0.001 (printed rounding) | pass |
| slope | SciPy stats.linregress | 0.499909090909091 | 0.499909090909091 | relative 1e-09 | pass |
| intercept | SciPy stats.linregress | 3.00172727272727 | 3.00172727272727 | relative 1e-09 | pass |
| slope standard error | SciPy stats.linregress | 0.117818941729685 | 0.117818941729685 | relative 1e-09 | pass |
| R squared | SciPy stats.linregress | 0.666707256898466 | 0.666707256898466 | relative 1e-09 | pass |

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
| slope | statsmodels WLS | 0.204801163243055 | 0.204801163243055 | relative 1e-09 | pass |
| slope standard error | statsmodels WLS | 0.0381548260706377 | 0.0381548260706378 | relative 1e-09 | pass |
| intercept | statsmodels WLS | 12.7964165214901 | 12.7964165214901 | relative 1e-09 | pass |
| slope | R | 0.204801163243055 | 0.204801163243058 | relative 1e-09 | pass |
| slope standard error | R | 0.0381548260706377 | 0.0381548260706375 | relative 1e-09 | pass |
| intercept | R | 12.7964165214901 | 12.7964165214901 | relative 1e-09 | pass |

Note: Weisberg (2014, section 7.1) fits this weighted line; the numbers are checked against statsmodels and R rather than the book's printed table.

### `table.explain outcome="yes or no (overdispersed)"`

**quasi-binomial: seeds that germinated out of seeds, by variety and root extract** (real data; data: Orobanche seeds)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| extract | statsmodels GLM (Binomial, scale X2) | 0.540078166603429 | 0.540078166603428 | relative 1e-07 | pass |
| extract standard error | statsmodels GLM (Binomial, scale X2) | 0.340867231336386 | 0.340867231336386 | relative 1e-07 | pass |
| interaction standard error | statsmodels GLM (Binomial, scale X2) | 0.418124932214023 | 0.418124932214023 | relative 1e-07 | pass |
| extract | R | 0.540078166603429 | 0.540078166603428 | relative 1e-06 | pass |
| extract standard error | R | 0.340867231336386 | 0.340867231340939 | relative 1e-06 | pass |
| interaction standard error | R | 0.418124932214023 | 0.418124932215663 | relative 1e-06 | pass |
| interaction p-value | R | 0.0801390217137065 | 0.080139021714788 | relative 1e-06 | pass |

Note: Crowder (1978) fitted a beta-binomial model; the quasi-binomial fit of the same data (Collett 2003, Modelling Binary Data) is checked here against statsmodels and R.

### `table.explain matched_by=`

**conditional logistic regression: infertility and earlier abortions in matched sets** (real data; data: infert)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| spontaneous | statsmodels ConditionalLogit | 1.98587551668241 | 1.98587551668241 | relative 1e-07 | pass |
| induced | statsmodels ConditionalLogit | 1.40901163187936 | 1.40901163187936 | relative 1e-07 | pass |
| spontaneous standard error | statsmodels ConditionalLogit | 0.352443539729635 | 0.352443543187006 | relative 1e-07 | pass |
| induced standard error | statsmodels ConditionalLogit | 0.360712432546398 | 0.360712438256113 | relative 1e-07 | pass |
| spontaneous | R | 1.98587551668241 | 1.98587551667772 | relative 1e-06 | pass |
| induced | R | 1.40901163187936 | 1.40901163187514 | relative 1e-06 | pass |
| spontaneous standard error | R | 0.352443539729635 | 0.35244353980717 | relative 1e-06 | pass |
| induced standard error | R | 0.360712432546398 | 0.360712436248923 | relative 1e-06 | pass |

Note: The model of R's ?clogit example; R and statsmodels both use the exact conditional likelihood.

### `table.explain show="risk ratios"`

**risk ratio of low birth weight for smokers equals the 2 x 2 table's** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| risk ratio, smoking alone | statsmodels Table2x2 and GLM (Poisson, HC0) | 1.6076421248835 | 1.6076421248835 | relative 1e-06 | pass |
| log risk ratio with age | statsmodels Table2x2 and GLM (Poisson, HC0) | 0.460730395503193 | 0.460730395503193 | relative 1e-06 | pass |
| standard error with age | statsmodels Table2x2 and GLM (Poisson, HC0) | 0.213624213081043 | 0.213624213081042 | relative 1e-06 | pass |
| log risk ratio with age | R | 0.460730395503193 | 0.460730390124031 | relative 1e-06 | pass |
| standard error with age | R | 0.213624213081043 | 0.213624320441299 | relative 1e-06 | pass |

Note: With one yes/no column, the modified Poisson risk ratio is the risk ratio of the 2 x 2 table (Zou 2004), here from statsmodels' Table2x2.

### `table.explain test_method="log-binomial"`

**log-binomial risk ratio of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| log risk ratio | R | 0.444051519404953 | 0.444052356626726 | relative 1e-05 | pass |
| standard error | R | 0.2125706249025 | 0.212571063773311 | relative 1e-05 | pass |

### `table.explain giving_outliers_less_weight=`

**Huber's robust regression of stack loss** (real data; data: stackloss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| air flow | statsmodels RLM (HuberT) | 0.829384334599657 | 0.829384334599655 | relative 1e-09 | pass |
| water temperature | statsmodels RLM (HuberT) | 0.926065966198336 | 0.926065966198341 | relative 1e-09 | pass |
| acid concentration | statsmodels RLM (HuberT) | -0.127846724945884 | -0.127846724945884 | relative 1e-09 | pass |
| intercept | statsmodels RLM (HuberT) | -41.0264983523996 | -41.0264983523997 | relative 1e-09 | pass |
| air flow standard error | statsmodels RLM (HuberT) | 0.11100521335458 | 0.11100521335458 | relative 1e-09 | pass |
| air flow | R | 0.829384334599657 | 0.829385770253742 | relative 1e-05 | pass |
| water temperature | R | 0.926065966198336 | 0.926059415549027 | relative 1e-05 | pass |
| acid concentration | R | -0.127846724945884 | -0.12784631796544 | relative 1e-05 | pass |
| intercept | R | -41.0264983523996 | -41.0264853732949 | relative 1e-05 | pass |

Note: Venables & Ripley (2002, chapter 6) fit rlm() to these data. The estimates agree with R to the stopping rules of the two fits; the standard errors are statsmodels' (Huber's H1), which differ from R's summary(rlm) in the third digit, so R's are not compared.

### `table.explain with_knots=`

**a natural spline with 3 knots through the 36 Norris calibration points** (real data; data: NIST Norris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| F of the whole curve | patsy cr() and statsmodels OLS | 1309424.66989213 | 1309424.66989214 | relative 1e-09 | pass |
| F of the whole curve | R | 1309424.66989213 | 1309424.66989228 | relative 1e-08 | pass |

Note: The spline's own coefficients differ between patsy and R's ns() (another basis of the same curves); the test of the whole curve and the fitted values are the same, so those are compared.

### `table.explain show="standardised effects"`

**standardised effects of weight, horsepower and gearbox on fuel use** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| weight | statsmodels OLS on z-scores | -0.467328325133065 | -0.467328325133064 | relative 1e-09 | pass |
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
| 95 % CI low | SciPy stats.bootstrap (BCa) | 0.638744784688276 | 0.638744784688276 | relative 1e-09 | pass |
| 95 % CI high | SciPy stats.bootstrap (BCa) | 1.17896864783934 | 1.17896864783934 | relative 1e-09 | pass |
| 95 % CI low | R | 0.638744784688276 | 0.617466087556167 | within 4 Monte Carlo SE (0.0783) | pass |
| 95 % CI high | R | 1.17896864783934 | 1.17339381682502 | within 4 Monte Carlo SE (0.00853) | pass |

Note: R draws other random rows than SciPy, so R checks the same method within its Monte Carlo error: R boot runs 10 times (seeds 1 to 10, 9999 resamples each); the reference is their average, and the difference may be 4 Monte Carlo standard errors, from the spread of R's 10 runs (simplydata's one run of 9999 resamples is taken to vary as much as one of R's). SciPy with the same seed gives the same interval exactly.

### `table.explain interval_by="profile"`

**profile-likelihood intervals of a logistic regression of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| smoke low | R | 0.0326710772426011 | 0.0326710772426011 | relative 1e-06 | pass |
| smoke high | R | 1.31383593363347 | 1.31383593363347 | relative 1e-06 | pass |
| lwt low | R | -0.0249706001060748 | -0.0249706001060748 | relative 1e-06 | pass |

Note: simplydata runs R's confint() itself (statsmodels has no profile intervals); this case checks that the model R gets is the model explain() fits, from the formula side.

### `table.explain p_value_by="likelihood ratio"`

**likelihood-ratio tests in a logistic regression of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| smoke | statsmodels GLM refits and SciPy chi2 | 0.0393884378670746 | 0.0393884378670746 | relative 1e-08 | pass |
| age | statsmodels GLM refits and SciPy chi2 | 0.226723754237082 | 0.226723754237073 | relative 1e-08 | pass |
| lwt | statsmodels GLM refits and SciPy chi2 | 0.036003504929209 | 0.036003504929209 | relative 1e-08 | pass |
| smoke | R | 0.0393884378670746 | 0.0393884378670747 | relative 1e-07 | pass |
| age | R | 0.226723754237082 | 0.226723754237081 | relative 1e-07 | pass |
| lwt | R | 0.036003504929209 | 0.0360035049292096 | relative 1e-07 | pass |

### `table.explain`

**Nagelkerke's and Tjur's pseudo R squared of a logistic regression of low birth weight** (real data; data: birthwt)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Nagelkerke | R | 0.0850637355720789 | 0.085063735572079 | relative 1e-09 | pass |
| Tjur | R | 0.0584872861258487 | 0.058487286125848 | relative 1e-09 | pass |

Note: The printout gives the two measures with 3 decimals; the check takes them at full precision from the same statsmodels fit and the same function explain() prints them with (and checks that the printout is their rounding), so it is not limited by the printed rounding.

**Longley: six predictors that move almost together (NIST certified)** (published; data: NIST Longley)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | -3482258.63459781 | -3482258.63459582 | at least 9 digits (LRE 12.2) | pass |
| b0 standard error | NIST certified | 890420.3836076 | 890420.383607373 | at least 9 digits (LRE 12.6) | pass |
| b1 | NIST certified | 15.0618722715538 | 15.0618722713733 | at least 9 digits (LRE 10.9) | pass |
| b1 standard error | NIST certified | 84.9149257747983 | 84.9149257747669 | at least 9 digits (LRE 12.4) | pass |
| b2 | NIST certified | -0.0358191792926458 | -0.035819179292591 | at least 9 digits (LRE 11.8) | pass |
| b2 standard error | NIST certified | 0.0334910077722505 | 0.0334910077722432 | at least 9 digits (LRE 12.7) | pass |
| b3 | NIST certified | -2.02022980381739 | -2.02022980381683 | at least 9 digits (LRE 12.6) | pass |
| b3 standard error | NIST certified | 0.488399681651751 | 0.488399681651699 | at least 9 digits (LRE 13.0) | pass |
| b4 | NIST certified | -1.03322686717365 | -1.03322686717359 | at least 9 digits (LRE 13.2) | pass |
| b4 standard error | NIST certified | 0.214274163161705 | 0.214274163161675 | at least 9 digits (LRE 12.8) | pass |
| b5 | NIST certified | -0.0511041056536771 | -0.0511041056535807 | at least 9 digits (LRE 11.7) | pass |
| b5 standard error | NIST certified | 0.226073200069399 | 0.22607320006937 | at least 9 digits (LRE 12.9) | pass |
| b6 | NIST certified | 1829.15146461458 | 1829.15146461355 | at least 9 digits (LRE 12.3) | pass |
| b6 standard error | NIST certified | 455.478499142331 | 455.478499142212 | at least 9 digits (LRE 12.6) | pass |

Note: The standard errors use R summary.lm()'s inv(R) inv(R)' from the QR factor; statsmodels' own inv(R'R) after its QR fit gave only 7.97 to 9.42 digits here.

### `table.explain crossed_with=`

**people and items crossed: verbal aggression (yes or no) from anger and gender** (real data; data: VerbAgg)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| anger | R | 0.0574460971215786 | 0.0574460971215786 | relative 1e-06 | pass |
| anger standard error | R | 0.0168528280463522 | 0.0168528280463522 | relative 1e-06 | pass |
| gender | R | 0.320646326996743 | 0.320646326996743 | relative 1e-06 | pass |

Note: simplydata runs lme4 itself (statsmodels cannot fit crossed groupings); this case checks the model R gets from explain() against R's own formula. simplydata hands the groups to R as text, so their order is that of text ("1", "10", "100" ...); R's reference does the same. A user's own R run on the whole-number ids orders them as numbers, and its glmer standard errors (from a numerical Hessian) then differ in the fourth digit.

### `table.explain outcome="counts in two steps"`

**two-step (hurdle) model of physician office visits** (published; data: NMES 1988)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count: hospital | Zeileis et al. (2008) | 0.211898197949242 | 0.211898 | within 5e-07 (printed rounding) | pass |
| count: health poor | Zeileis et al. (2008) | 0.315957574199259 | 0.315958 | within 5e-07 (printed rounding) | pass |
| count: chronic | Zeileis et al. (2008) | 0.126420588812089 | 0.126421 | within 5e-07 (printed rounding) | pass |
| count: chronic standard error | Zeileis et al. (2008) | 0.012452306903594 | 0.012452 | within 5e-07 (printed rounding) | pass |
| zero: chronic | Zeileis et al. (2008) | 0.535212638440467 | 0.535213 | within 5e-07 (printed rounding) | pass |
| zero: insurance | Zeileis et al. (2008) | 0.747119812959578 | 0.74712 | within 5e-07 (printed rounding) | pass |
| zero: insurance standard error | Zeileis et al. (2008) | 0.100879503174147 | 0.10088 | within 5e-07 (printed rounding) | pass |

Note: The paper's model fm_hurdle0: a negative binomial count part and a logistic zero hurdle, the same columns in both.

### `table.explain outcome="counts with many zeros that vary a lot"`

**zero-inflated negative binomial model of physician office visits, the zero part with its own columns** (published; data: NMES 1988)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| count: hospital | Zeileis et al. (2008), Table 2 | 0.201476829498611 | 0.201 | within 0.0005 (printed rounding) | pass |
| count: health poor | Zeileis et al. (2008), Table 2 | 0.285132769246968 | 0.285 | within 0.0005 (printed rounding) | pass |
| zero: hospital | Zeileis et al. (2008), Table 2 | -0.800464995130227 | -0.8 | within 0.0005 (printed rounding) | pass |
| zero: chronic | Zeileis et al. (2008), Table 2 | -1.24789708597442 | -1.248 | within 0.0005 (printed rounding) | pass |
| zero: gender male | Zeileis et al. (2008), Table 2 | 0.647660217015313 | 0.648 | within 0.0005 (printed rounding) | pass |
| count: hospital | statsmodels ZeroInflatedNegativeBinomialP | 0.201476829498611 | 0.201476841187623 | relative 0.0001 | pass |
| zero: hospital | statsmodels ZeroInflatedNegativeBinomialP | -0.800464995130227 | -0.800490700364435 | relative 0.0001 | pass |
| zero: chronic | statsmodels ZeroInflatedNegativeBinomialP | -1.24789708597442 | -1.24793581168842 | relative 0.0001 | pass |

Note: The paper's model fm_zinb (the zero part without health). simplydata runs R pscl itself, for its standard errors; statsmodels gives the same estimates.

### `table.explain zero_part_using=`

**two-step (hurdle) model whose zero part has its own columns** (published; data: NMES 1988)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| zero: intercept | Zeileis et al. (2008), Table 2 | 0.015940173828489 | 0.016 | within 0.0005 (printed rounding) | pass |
| zero: hospital | Zeileis et al. (2008), Table 2 | 0.318434481481659 | 0.318 | within 0.0005 (printed rounding) | pass |
| zero: chronic | Zeileis et al. (2008), Table 2 | 0.54783250793305 | 0.548 | within 0.0005 (printed rounding) | pass |
| zero: insurance | Zeileis et al. (2008), Table 2 | 0.745720049336331 | 0.746 | within 0.0005 (printed rounding) | pass |
| zero: school | Zeileis et al. (2008), Table 2 | 0.0570728152414011 | 0.057 | within 0.0005 (printed rounding) | pass |
| zero: gender male | Zeileis et al. (2008), Table 2 | -0.419147791025234 | -0.419 | within 0.0005 (printed rounding) | pass |
| zero: intercept | statsmodels Logit (the first step on its own) | 0.015940173828489 | 0.0159401718063211 | relative 1e-06 | pass |
| zero: hospital | statsmodels Logit (the first step on its own) | 0.318434481481659 | 0.318434494004322 | relative 1e-06 | pass |
| zero: chronic | statsmodels Logit (the first step on its own) | 0.54783250793305 | 0.547832508738329 | relative 1e-06 | pass |
| zero: insurance | statsmodels Logit (the first step on its own) | 0.745720049336331 | 0.745720049922439 | relative 1e-06 | pass |
| zero: school | statsmodels Logit (the first step on its own) | 0.0570728152414011 | 0.0570728147518849 | relative 1e-06 | pass |
| zero: gender male | statsmodels Logit (the first step on its own) | -0.419147791025234 | -0.419147791543225 | relative 1e-06 | pass |

Note: The first step of a hurdle model is a logistic regression of zero or not, so statsmodels' Logit gives the same numbers as pscl's zero hurdle.

### `table.fit_dose_response`

**ryegrass root length and ferulic acid: LL.4 curve and ED10, ED50, ED90** (real data; data: ryegrass (drc))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 2.98222857654905 | 2.98222867450264 | relative 2e-06 | pass |
| c | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 0.481409615436097 | 0.481409945390997 | relative 2e-06 | pass |
| d | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 7.79296184541836 | 7.79296232712923 | relative 2e-06 | pass |
| ED10 | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 1.46370952427383 | 1.46370922446201 | relative 2e-06 | pass |
| ED50 | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 3.05795586800834 | 3.05795516764472 | relative 2e-06 | pass |
| ED90 | SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit) | 6.38862693424495 | 6.38862531645388 | relative 2e-06 | pass |
| b | R | 2.98222857654905 | 2.98222857654905 | relative 1e-09 | pass |
| c | R | 0.481409615436097 | 0.481409615436097 | relative 1e-09 | pass |
| d | R | 7.79296184541836 | 7.79296184541836 | relative 1e-09 | pass |
| ED10 | R | 1.46370952427383 | 1.46370952427383 | relative 1e-09 | pass |
| ED50 | R | 3.05795586800834 | 3.05795586800834 | relative 1e-09 | pass |
| ED90 | R | 6.38862693424495 | 6.38862693424495 | relative 1e-09 | pass |
| ED50 95 % CI low | R | 2.6705274583185 | 2.6705274583185 | relative 1e-09 | pass |

Note: Python has no dose-response package with drc's ED intervals, so R drc itself gives the intervals; SciPy curve_fit, run to 1e-15, is the independent fit of the curve. The optimum is flat (the residual sum of squares of the two fits agrees to 1e-12), so the estimates agree to about 1e-6. drc's default stopping rule (relTol 1e-7) stopped 1e-6 to 1.4e-5 short; simplydata asks for 1e-15. Ritz et al. (2015) analyse these data with the same LL.4 model.

### `table.fit_dose_response outcome="yes or no"`

**Bliss's beetles: LD50 from the logistic curve on log dose (yes or no)** (published; data: Bliss beetles)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| LD50 | Dobson & Barnett (2008) | 59.1181877103261 | 59.1186543855778 | within 0.01 (printed rounding) | pass |
| LD50 | statsmodels GLM (binomial, logit) on log10 dose | 59.1181877103261 | 59.1181676064851 | relative 1e-06 | pass |
| LD50 | R | 59.1181877103261 | 59.1181676064854 | relative 1e-06 | pass |

Note: The 2 parameter log-logistic curve with binomial errors is logistic regression on log dose, so its LD50 is the published fit's; the tolerance allows the printed 3 decimals of the fit.

### `fit_dose_response`

**the drawn ryegrass curve is drc's** (real data; data: ryegrass (drc))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | R | 301 | 301 | relative 1e-09 | pass |
| curve at the highest dose | R | 0.489464966416387 | 0.489464966416387 | relative 1e-09 | pass |
| curve at dose 0 | R | 7.79296184541836 | 7.79296184541836 | relative 1e-09 | pass |

### `table.find_best_power_of using=`

**Box and Cox's poisons: the power for the two-way model** (published; data: poisons (boot))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | Box & Cox (1964) | -0.750162301479962 | -0.75 | within 0.01 (printed rounding) | pass |
| simple power | Box & Cox (1964) | -1 | -1 | within 0 (printed rounding) | pass |
| power | R | -0.750162301479962 | -0.750162301479962 | relative 1e-06 | pass |
| 95 % CI low | R | -1.13693054540593 | -1.13693054540593 | relative 1e-06 | pass |
| simple power | R | -1 | -1 | relative 1e-06 | pass |

Note: Box and Cox print a power of about -0.75 and suggest the reciprocal (power -1), the rate of dying.

### `table.find_best_power_of`

**the power of the poisons survival times on their own** (real data; data: poisons (boot))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | SciPy stats.boxcox(alpha=0.05) | -0.360158452952329 | -0.360158452952329 | relative 1e-09 | pass |
| 95 % CI low | SciPy stats.boxcox(alpha=0.05) | -0.961993862358215 | -0.961993862358215 | relative 1e-09 | pass |
| power | R | -0.360158452952329 | -0.360158410727 | relative 0.0001 | pass |

Note: car::powerTransform maximises the same likelihood with another optimiser (to about 1e-5).

### `table.fit_curve of_kind="logistic growth"`

**Rat42: a logistic growth curve (NIST certified)** (published; data: NIST Rat42)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 72.4622375422844 | 72.462237576 | at least 6 digits (LRE 9.3) | pass |
| b2 | NIST certified | 2.61807684203404 | 2.6180768402 | at least 6 digits (LRE 9.2) | pass |
| b3 | NIST certified | 0.0673592001448143 | 0.067359200066 | at least 6 digits (LRE 8.9) | pass |
| residual sum of squares | NIST certified | 8.05652293381132 | 8.0565229338 | at least 6 digits (LRE 11.9) | pass |

Note: NIST writes the curve as b1 / (1 + exp(b2 - b3 x)): b1 is Asym, b2 is xmid / scal and b3 is 1 / scal of R's SSlogis.

### `table.fit_curve of_kind="rise to a limit"`

**Misra1a: a rise to a limit (NIST certified)** (published; data: NIST Misra1a)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 238.942128834901 | 238.94212918 | at least 6 digits (LRE 8.8) | pass |
| b2 | NIST certified | 0.000550156432727615 | 0.00055015643181 | at least 6 digits (LRE 8.8) | pass |
| residual sum of squares | NIST certified | 0.124551388944408 | 0.12455138894 | at least 6 digits (LRE 10.5) | pass |

Note: NIST writes the curve as b1 (1 - exp(-b2 x)): b1 is Asym and b2 is exp(lrc) of R's SSasympOrig.

**BoxBOD: a rise to a limit (NIST certified)** (published; data: NIST BoxBOD)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 213.809410866175 | 213.80940889 | at least 6 digits (LRE 8.0) | pass |
| b2 | NIST certified | 0.54723746243967 | 0.54723748542 | at least 6 digits (LRE 7.4) | pass |
| residual sum of squares | NIST certified | 1168.00887655556 | 1168.0088766 | at least 6 digits (LRE 10.4) | pass |

Note: NIST writes the curve as b1 (1 - exp(-b2 x)): b1 is Asym and b2 is exp(lrc) of R's SSasympOrig.

### `table.fit_curve`

**Filip: a polynomial of degree 10 whose powers are nearly in proportion (NIST certified)** (published; data: NIST Filip)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | -1467.48961422976 | -1467.4896142298 | at least 9 digits (LRE 13.5) | pass |
| b0 standard error | NIST certified | 298.084530995529 | 298.084530995537 | at least 9 digits (LRE 13.6) | pass |
| b1 | NIST certified | -2772.17959193334 | -2772.17959193342 | at least 9 digits (LRE 13.6) | pass |
| b1 standard error | NIST certified | 559.779865474936 | 559.77986547495 | at least 9 digits (LRE 13.6) | pass |
| b2 | NIST certified | -2316.37108160886 | -2316.37108160893 | at least 9 digits (LRE 13.5) | pass |
| b2 standard error | NIST certified | 466.477572127785 | 466.477572127796 | at least 9 digits (LRE 13.6) | pass |
| b3 | NIST certified | -1127.97394098368 | -1127.97394098372 | at least 9 digits (LRE 13.4) | pass |
| b3 standard error | NIST certified | 227.204274477746 | 227.204274477751 | at least 9 digits (LRE 13.6) | pass |
| b4 | NIST certified | -354.478233703336 | -354.478233703349 | at least 9 digits (LRE 13.4) | pass |
| b4 standard error | NIST certified | 71.647866087591 | 71.6478660875927 | at least 9 digits (LRE 13.6) | pass |
| b5 | NIST certified | -75.1242017393729 | -75.1242017393757 | at least 9 digits (LRE 13.4) | pass |
| b5 standard error | NIST certified | 15.2897178747396 | 15.28971787474 | at least 9 digits (LRE 13.6) | pass |
| b6 | NIST certified | -10.8753180355338 | -10.8753180355343 | at least 9 digits (LRE 13.4) | pass |
| b6 standard error | NIST certified | 2.23691159816028 | 2.23691159816033 | at least 9 digits (LRE 13.6) | pass |
| b7 | NIST certified | -1.06221498588942 | -1.06221498588947 | at least 9 digits (LRE 13.4) | pass |
| b7 standard error | NIST certified | 0.221624321934222 | 0.221624321934227 | at least 9 digits (LRE 13.6) | pass |
| b8 | NIST certified | -0.0670191154593381 | -0.0670191154593408 | at least 9 digits (LRE 13.4) | pass |
| b8 standard error | NIST certified | 0.0142363763154721 | 0.0142363763154724 | at least 9 digits (LRE 13.6) | pass |
| b9 | NIST certified | -0.00246781078275468 | -0.00246781078275479 | at least 9 digits (LRE 13.4) | pass |
| b9 standard error | NIST certified | 0.000535617408889808 | 0.000535617408889821 | at least 9 digits (LRE 13.6) | pass |
| b10 | NIST certified | -4.02962525080386e-05 | -4.02962525080404e-05 | at least 9 digits (LRE 13.4) | pass |
| b10 standard error | NIST certified | 8.96632837373847e-06 | 8.96632837373868e-06 | at least 9 digits (LRE 13.6) | pass |

Note: The hardest NIST linear problem (condition number of the powers 1.8e15). simplydata fits on x mapped onto [-1, 1] and turns the answer back into the raw powers with statsmodels t_test(); a QR fit on the raw powers (simplydata 0.2.0) gave no standard errors for b5 to b10, and R lm() drops two terms.

**Wampler1: a polynomial of degree 5, points exactly on the curve (NIST certified)** (published; data: NIST Wampler1)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 1.00000000058208 | 1 | at least 9 digits (LRE 9.2) | pass |
| b0 standard error | NIST certified | 1.55712885651003e-09 | 0 | at least 9 digits (LRE 8.8) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b1 | NIST certified | 0.999999999708962 | 1 | at least 9 digits (LRE 9.5) | pass |
| b1 standard error | NIST certified | 1.70994272613356e-09 | 0 | at least 9 digits (LRE 8.8) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b2 | NIST certified | 0.999999999949068 | 1 | at least 9 digits (LRE 10.3) | pass |
| b2 standard error | NIST certified | 5.63826368184418e-10 | 0 | at least 9 digits (LRE 9.2) | pass |
| b3 | NIST certified | 1.00000000001637 | 1 | at least 9 digits (LRE 10.8) | pass |
| b3 standard error | NIST certified | 7.34137964780744e-11 | 0 | at least 9 digits (LRE 10.1) | pass |
| b4 | NIST certified | 0.999999999998805 | 1 | at least 9 digits (LRE 11.9) | pass |
| b4 standard error | NIST certified | 4.08443101427947e-12 | 0 | at least 9 digits (LRE 11.4) | pass |
| b5 | NIST certified | 1.00000000000003 | 1 | at least 9 digits (LRE 13.6) | pass |
| b5 standard error | NIST certified | 8.12628999836708e-14 | 0 | at least 9 digits (LRE 13.1) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler2: a polynomial of degree 5, points exactly on a curve with small coefficients (NIST certified)** (published; data: NIST Wampler2)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 1.00000000000001 | 1 | at least 9 digits (LRE 13.9) | pass |
| b0 standard error | NIST certified | 3.12641750882078e-14 | 0 | at least 9 digits (LRE 13.5) | pass |
| b1 | NIST certified | 0.0999999999999968 | 0.1 | at least 9 digits (LRE 13.5) | pass |
| b1 standard error | NIST certified | 3.43323858890304e-14 | 0 | at least 9 digits (LRE 13.5) | pass |
| b2 | NIST certified | 0.00999999999999818 | 0.01 | at least 9 digits (LRE 12.7) | pass |
| b2 standard error | NIST certified | 1.13205572040932e-14 | 0 | at least 9 digits (LRE 13.9) | pass |
| b3 | NIST certified | 0.00100000000000043 | 0.001 | at least 9 digits (LRE 12.4) | pass |
| b3 standard error | NIST certified | 1.47400889617114e-15 | 0 | at least 9 digits (LRE 14.8) | pass |
| b4 | NIST certified | 9.99999999999711e-05 | 0.0001 | at least 9 digits (LRE 12.5) | pass |
| b4 standard error | NIST certified | 8.20075781347625e-17 | 0 | at least 9 digits (LRE 15.0) | pass |
| b5 | NIST certified | 1.00000000000006e-05 | 1e-05 | at least 9 digits (LRE 13.2) | pass |
| b5 standard error | NIST certified | 1.63160391167578e-18 | 0 | at least 9 digits (LRE 15.0) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler3: a polynomial of degree 5, with noise (NIST certified)** (published; data: NIST Wampler3)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 1.0000000015134 | 1 | at least 9 digits (LRE 8.8) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b0 standard error | NIST certified | 2152.32624678175 | 2152.3262467817 | at least 9 digits (LRE 13.6) | pass |
| b1 | NIST certified | 0.999999999592546 | 1 | at least 9 digits (LRE 9.4) | pass |
| b1 standard error | NIST certified | 2363.55173469686 | 2363.55173469681 | at least 9 digits (LRE 13.7) | pass |
| b2 | NIST certified | 0.999999999919964 | 1 | at least 9 digits (LRE 10.1) | pass |
| b2 standard error | NIST certified | 779.3435243316 | 779.343524331583 | at least 9 digits (LRE 13.7) | pass |
| b3 | NIST certified | 1.00000000002228 | 1 | at least 9 digits (LRE 10.7) | pass |
| b3 standard error | NIST certified | 101.475507550352 | 101.47550755035 | at least 9 digits (LRE 13.8) | pass |
| b4 | NIST certified | 0.999999999998442 | 1 | at least 9 digits (LRE 11.8) | pass |
| b4 standard error | NIST certified | 5.64566512170763 | 5.64566512170752 | at least 9 digits (LRE 13.7) | pass |
| b5 | NIST certified | 1.00000000000003 | 1 | at least 9 digits (LRE 13.5) | pass |
| b5 standard error | NIST certified | 0.112324854679314 | 0.112324854679312 | at least 9 digits (LRE 13.7) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler4: a polynomial of degree 5, with large noise (NIST certified)** (published; data: NIST Wampler4)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 1.00000000023283 | 1 | at least 9 digits (LRE 9.6) | pass |
| b0 standard error | NIST certified | 215232.624678172 | 215232.62467817 | at least 9 digits (LRE 14.1) | pass |
| b1 | NIST certified | 1.00000000008731 | 1 | at least 9 digits (LRE 10.1) | pass |
| b1 standard error | NIST certified | 236355.173469681 | 236355.173469681 | at least 9 digits (LRE 15.0) | pass |
| b2 | NIST certified | 0.999999999829015 | 1 | at least 9 digits (LRE 9.8) | pass |
| b2 standard error | NIST certified | 77934.3524331584 | 77934.3524331583 | at least 9 digits (LRE 14.8) | pass |
| b3 | NIST certified | 1.00000000003229 | 1 | at least 9 digits (LRE 10.5) | pass |
| b3 standard error | NIST certified | 10147.550755035 | 10147.550755035 | at least 9 digits (LRE 14.6) | pass |
| b4 | NIST certified | 0.999999999997922 | 1 | at least 9 digits (LRE 11.7) | pass |
| b4 standard error | NIST certified | 564.566512170752 | 564.566512170752 | at least 9 digits (LRE 15.0) | pass |
| b5 | NIST certified | 1.00000000000004 | 1 | at least 9 digits (LRE 13.4) | pass |
| b5 standard error | NIST certified | 11.2324854679312 | 11.2324854679312 | at least 9 digits (LRE 15.0) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

**Wampler5: a polynomial of degree 5, with noise far larger than the curve (NIST certified)** (published; data: NIST Wampler5)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b0 | NIST certified | 1.00000001234002 | 1 | at least 9 digits (LRE 7.9) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b0 standard error | NIST certified | 21523262.4678171 | 21523262.467817 | at least 9 digits (LRE 14.2) | pass |
| b1 | NIST certified | 1.00000001394073 | 1 | at least 9 digits (LRE 7.9) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b1 standard error | NIST certified | 23635517.3469681 | 23635517.3469681 | at least 9 digits (LRE 15.0) | pass |
| b2 | NIST certified | 0.999999991876393 | 1 | at least 9 digits (LRE 8.1) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b2 standard error | NIST certified | 7793435.24331584 | 7793435.24331583 | at least 9 digits (LRE 14.8) | pass |
| b3 | NIST certified | 1.00000000125374 | 1 | at least 9 digits (LRE 8.9) | explained difference – precision limit: the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and 7.1 on Wampler5) |
| b3 standard error | NIST certified | 1014755.0755035 | 1014755.0755035 | at least 9 digits (LRE 14.6) | pass |
| b4 | NIST certified | 0.999999999925702 | 1 | at least 9 digits (LRE 10.1) | pass |
| b4 standard error | NIST certified | 56456.6512170752 | 56456.6512170752 | at least 9 digits (LRE 15.0) | pass |
| b5 | NIST certified | 1.0000000000015 | 1 | at least 9 digits (LRE 11.8) | pass |
| b5 standard error | NIST certified | 1123.24854679312 | 1123.24854679312 | at least 9 digits (LRE 15.0) | pass |

Note: simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an explained difference may fall a little short of 9 digits; the reason is given with it.

### `table.fit_formula`

**Roszman1: a formula with arctan, from NIST's start 1 (NIST certified)** (published; data: NIST Roszman1)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 0.201968683219875 | 0.20196866396 | at least 6 digits (LRE 7.0) | pass |
| b2 | NIST certified | -6.19535497072178e-06 | -6.1953516256e-06 | at least 6 digits (LRE 6.3) | pass |
| b3 | NIST certified | 1204.45561337731 | 1204.4556708 | at least 6 digits (LRE 7.3) | pass |
| b4 | NIST certified | -181.34264115481 | -181.34269537 | at least 6 digits (LRE 6.5) | pass |
| residual sum of squares | NIST certified | 0.000494848473309717 | 0.00049484847331 | at least 6 digits (LRE 12.2) | pass |

Note: arctan is NumPy's arctan in the formula reader.

**Puromycin (treated): Vm and K of the Michaelis-Menten formula** (published; data: Puromycin (treated))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Vm | Bates & Watts (1988) | 212.683742080229 | 212.7 | within 0.05 (printed rounding) | pass |
| K | Bates & Watts (1988) | 0.0641212799902884 | 0.06412 | within 5e-06 (printed rounding) | pass |
| Vm | SciPy curve_fit (Levenberg-Marquardt) | 212.683742080229 | 212.683742080229 | relative 1e-07 | pass |
| K | SciPy curve_fit (Levenberg-Marquardt) | 0.0641212799902884 | 0.0641212799902884 | relative 1e-07 | pass |
| standard error of K | SciPy curve_fit (Levenberg-Marquardt) | 0.00828094786209176 | 0.00828094786209176 | relative 1e-07 | pass |
| Vm | R | 212.683742080229 | 212.683743267832 | relative 1e-06 | pass |
| K | R | 0.0641212799902884 | 0.0641212818951466 | relative 1e-06 | pass |
| standard error of K | R | 0.00828094786209176 | 0.00828094945561312 | relative 1e-06 | pass |

### `table.fit_curve of_kind="michaelis-menten"`

**Puromycin (treated): a Michaelis-Menten curve** (published; data: Puromycin (treated))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Vm | Bates & Watts (1988) | 212.683742870014 | 212.7 | within 0.05 (printed rounding) | pass |
| K | Bates & Watts (1988) | 0.0641212812688425 | 0.06412 | within 5e-06 (printed rounding) | pass |
| Vm | R | 212.683742870014 | 212.683707271206 | relative 1e-05 | pass |
| K | R | 0.0641212812688425 | 0.0641212257944682 | relative 1e-05 | pass |

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
| bend 1 | R | 0.0411057845664149 | 0.0411057845664149 | relative 1e-09 | pass |
| slope 1 | R | -0.422076814406333 | -0.422076814406333 | relative 1e-09 | pass |
| slope 2 | R | -1.02056754500006 | -1.02056754500006 | relative 1e-09 | pass |
| Davies p-value | R | 1.29088012334937e-17 | 1.29088012334937e-17 | relative 1e-09 | pass |

Note: Bacon and Watts fit a smooth transition; segmented fits the sharp bend, so R is the reference.

### `table.fit_line changes_at=`

**drivers killed or seriously injured: the line changes at the seat-belt law** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| level change | statsmodels OLS with the two change columns | -457.768100628468 | -457.768100628468 | relative 1e-09 | pass |
| slope change | statsmodels OLS with the two change columns | 19.2016179865776 | 19.2016179865776 | relative 1e-09 | pass |
| level change standard error | statsmodels OLS with the two change columns | 107.180651134372 | 107.180651134372 | relative 1e-09 | pass |
| level change | R | -457.768100628468 | -457.768100628468 | relative 1e-09 | pass |
| slope change | R | 19.2016179865776 | 19.2016179865777 | relative 1e-09 | pass |
| level change standard error | R | 107.180651134372 | 107.180651134372 | relative 1e-09 | pass |

Note: A plain interrupted time series without the season, to check the arithmetic; Harvey and Durbin model the season and the trend too.

### `table.explain changes_at=`

**drivers killed (counts): the rate ratio of the jump at the seat-belt law** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| jump | statsmodels GLM (Poisson) with the two change columns | 0.724689274189852 | 0.724689274189852 | relative 1e-07 | pass |
| slope change | statsmodels GLM (Poisson) with the two change columns | 1.0154100777643 | 1.0154100777643 | relative 1e-07 | pass |
| jump | R | 0.724689274189852 | 0.724689274189851 | relative 1e-07 | pass |
| slope change | R | 1.0154100777643 | 1.0154100777643 | relative 1e-07 | pass |

### `table.explain for_percentile=`

**Engel's food expenditure: the 90th percentile line** (real data; data: Engel food expenditure)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| intercept | statsmodels QuantReg (estimates only: its standard errors are not R's) | 67.3508720801297 | 67.3508508634295 | relative 1e-05 | pass |
| income | statsmodels QuantReg (estimates only: its standard errors are not R's) | 0.686299480371905 | 0.686299496768461 | relative 1e-05 | pass |
| intercept | R | 67.3508720801297 | 67.3508720801297 | relative 1e-09 | pass |
| income | R | 0.686299480371905 | 0.686299480371905 | relative 1e-09 | pass |
| income standard error | R | 0.0284907223757293 | 0.0284907223757293 | relative 1e-09 | pass |

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
| ratio | R | 0.923535209227047 | 0.923535209227047 | relative 1e-05 | pass |
| ratio low | R | 0.673968669673266 | 0.673968669673266 | relative 1e-05 | pass |
| ratio high | R | 1.26551473541868 | 1.26551473541868 | relative 1e-05 | pass |

### `table.explain neighbours_alike_in_order_of=`

**neighbours_alike_in_order_of=: the level of Lake Huron, a linear trend with AR(1) errors** (real data; data: Lake Huron)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| trend | R | -0.0194345899710192 | -0.0194345899710192 | relative 1e-05 | pass |
| standard error | R | 0.0126641385232237 | 0.0126641385232237 | relative 1e-05 | pass |
| phi | R | 0.824767412940849 | 0.824767412940849 | relative 1e-05 | pass |

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
| weight of the biggest | statsmodels OLS and eval_measures.aicc | 0.98503186334779 | 0.98503186334779 | relative 1e-09 | pass |
| AICc of Fertility ~ Education | R | 348.980436348024 | 348.980436348024 | relative 1e-09 | pass |
| weight of the biggest | R | 0.98503186334779 | 0.985031863347791 | relative 1e-09 | pass |

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
| Breusch-Pagan | statsmodels het_breuschpagan, het_white | 7.4268883603395 | 7.42688836033877 | relative 1e-09 | pass |
| Breusch-Pagan p | statsmodels het_breuschpagan, het_white | 0.006425635749869 | 0.00642563574987162 | relative 1e-09 | pass |
| White | statsmodels het_breuschpagan, het_white | 7.95553731022983 | 7.95553731022923 | relative 1e-09 | pass |
| Breusch-Pagan | R | 7.4268883603395 | 7.42688836033926 | relative 1e-08 | pass |
| Breusch-Pagan p | R | 0.006425635749869 | 0.00642563574986985 | relative 1e-08 | pass |
| White | R | 7.95553731022983 | 7.95553731022942 | relative 1e-08 | pass |

### `table.check_model_of outcome="yes or no"`

**outcome="yes or no": Hosmer-Lemeshow test and Brier score, low birth weight** (real data; data: birthwt (MASS))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Hosmer-Lemeshow | R | 7.22544929206197 | 7.22544929206197 | relative 1e-06 | pass |
| Hosmer-Lemeshow p | R | 0.512515395932266 | 0.512515395932266 | relative 1e-06 | pass |
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
| last | R | 37.0159513613634 | 37.0159513613634 | relative 1e-10 | pass |
| last high | R | 48.236154076259 | 48.236154076259 | relative 1e-10 | pass |

### `draw_interaction_lines`

**the averages of warp breaks for each wool at each tension** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| A at L | pandas mean, SciPy t.interval | 44.5555555555556 | 44.5555555555556 | relative 1e-09 | pass |
| B at H | pandas mean, SciPy t.interval | 18.7777777777778 | 18.7777777777778 | relative 1e-09 | pass |
| A at L, interval low | pandas mean, SciPy t.interval | 30.6444099497916 | 30.6444099497916 | relative 1e-09 | pass |
| A at L | R | 44.5555555555556 | 44.5555555555556 | relative 1e-12 | pass |
| B at H | R | 18.7777777777778 | 18.7777777777778 | relative 1e-12 | pass |
| A at L, interval low | R | 30.6444099497916 | 30.6444099497915 | relative 1e-12 | pass |

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
| F | Sokal & Rohlf (1981), Box 10.1 | 2.92895946510657 | 2.929 | within 0.0005 (printed rounding) | pass |
| treatment SS | Sokal & Rohlf (1981), Box 10.1 | 1557.55555555556 | 1557.56 | within 0.005 (printed rounding) | pass |
| rats SS | Sokal & Rohlf (1981), Box 10.1 | 797.666666666665 | 797.67 | within 0.005 (printed rounding) | pass |
| F | R | 2.92895946510657 | 2.92895946510657 | relative 1e-10 | pass |
| treatment SS | R | 1557.55555555556 | 1557.55555555556 | relative 1e-10 | pass |
| rats SS | R | 797.666666666665 | 797.666666666665 | relative 1e-10 | pass |

Note: The book's three-level table (rats, preparations, readings) tests treatments against rats with the same F as the two-level table here, because the design is balanced.

### `table.compare_averages_of for_each_group_in= with a list of columns`

**a list of columns: MANOVA of sepal and petal length across species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Pillai | statsmodels MANOVA | 0.988500527043348 | 0.988500527043348 | relative 1e-09 | pass |
| F | statsmodels MANOVA | 71.8287954469352 | 71.8287954469352 | relative 1e-09 | pass |
| Wilks | statsmodels MANOVA | 0.0398783132489411 | 0.0398783132489411 | relative 1e-09 | pass |
| Pillai | R | 0.988500527043348 | 0.98850052704333 | relative 1e-10 | pass |
| F | R | 71.8287954469352 | 71.8287954469326 | relative 1e-10 | pass |
| Wilks | R | 0.0398783132489411 | 0.0398783132489476 | relative 1e-10 | pass |

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
| age | statsmodels PHReg | 0.0130385698370914 | 0.0130385698370916 | relative 1e-06 | pass |
| men vs women | statsmodels PHReg | -0.0251377892665885 | -0.0251377892665881 | relative 1e-06 | pass |
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
| tau squared | Viechtbauer (2010), JSS 36(3) | 0.313243258136793 | 0.3132 | within 5e-05 (printed rounding) | pass |
| I squared % | Viechtbauer (2010), JSS 36(3) | 92.2213845212761 | 92.22 | within 0.005 (printed rounding) | pass |
| Q | Viechtbauer (2010), JSS 36(3) | 152.233008082373 | 152.233 | within 5e-05 (printed rounding) | pass |
| estimate | R | 0.489420939826016 | 0.48942093982603 | relative 1e-08 | pass |
| low | R | 0.330072248483585 | 0.330072248483599 | relative 1e-08 | pass |
| high | R | 0.725698259822329 | 0.725698259822339 | relative 1e-08 | pass |
| p-value | R | 0.00192001509605724 | 0.0019200150960573 | relative 1e-08 | pass |
| tau squared | R | 0.313243258136793 | 0.313243258136486 | relative 1e-08 | pass |
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
| low | R | 0.344074306106719 | 0.344074306106776 | relative 1e-08 | pass |
| high | R | 0.696166066715505 | 0.696166066715428 | relative 1e-08 | pass |
| p-value | R | 7.05425810168428e-05 | 7.05425810164237e-05 | relative 1e-08 | pass |

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
| p-value | R | 6.462924304704e-05 | 6.462924304704e-05 | relative 1e-08 | pass |
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
| p-value | R | 2.28862930697324e-26 | 2.28862930697324e-26 | relative 1e-08 | pass |

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
| p between | R | 0.394268758883901 | 0.394268758885585 | relative 1e-08 | pass |
| random | R | 0.378717511421929 | 0.378717511421398 | relative 1e-08 | pass |
| random tau2 | R | 0.392528006891838 | 0.392528006900774 | relative 1e-08 | pass |

Note: Each subgroup has its own between-study variance; the test of their difference uses each subgroup's estimate with its normal (z) standard error, as RevMan and R meta do (the next case checks it against meta), not metafor's rma(mods = ~ alloc), which shares one variance.

**for_each_group_in=: BCG trials by allocation, against R meta's test of subgroup differences** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Q between | R | 1.86144494616318 | 1.86144614123119 | relative 0.0001 | pass |
| p between | R | 0.394268758883901 | 0.394268523294979 | relative 0.0001 | pass |

Note: R meta (each subgroup its own between-study variance, REML) is a second package; meta's REML stops at its own tolerance, so the numbers agree to about 1e-5.

### `table.combine_studies using=`

**using=: BCG trials, meta-regression on latitude** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | -0.029101725011181 | -0.0291017250116429 | relative 1e-08 | pass |
| low | R | -0.0471529230265921 | -0.0471529230250808 | relative 1e-08 | pass |
| p-value | R | 0.00456505154515336 | 0.00456505154159259 | relative 1e-08 | pass |

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
| estimate | R | -0.537108258432977 | -0.537108258432961 | relative 1e-08 | pass |
| low | R | -1.25032220906533 | -1.25032220906531 | relative 1e-08 | pass |
| first study | R | -0.355169640940107 | -0.355169640940107 | relative 1e-08 | pass |

Note: metafor's Hedges' g (exact correction, large-sample variance) is the reference; statsmodels' effectsize_smd uses an approximate correction and another variance, so it differs slightly.

### `table.combine_studies show="ratios of averages"`

**show="ratios of averages": Curtis 1998, the log response ratio of plant mass under raised CO2** (real data; data: Curtis 1998 (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 1.28912239792386 | 1.28912239791847 | relative 1e-06 | pass |
| tau squared | R | 0.0257701366505266 | 0.0257701366410135 | relative 1e-06 | pass |

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
| power | R | 0.477840985940913 | 0.47784098594094 | relative 1e-09 | pass |

### `sdata.find_how_many_needed using=`

**using=: rows for a model of 3 columns, f squared 0.15** (real data; data: pwr manual and vignette)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| rows (exact) | R | 76.7058265578061 | 76.7058265599653 | relative 1e-06 | pass |
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
| values per group (before rounding) | R | 259.160977758531 | 259.160977698426 | relative 1e-09 | pass |

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
| PCo2 row 70 | R | 0.017998420475276 | 0.017998420475276 | relative 1e-08 | pass |

### `table.explain_profiles_of`

**varespec and varechem: db-RDA on Bray-Curtis with N, P and K** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| adjusted R squared | R | 0.0753000177198457 | 0.0753000177198457 | relative 1e-09 | pass |
| R squared | R | 0.195913058886822 | 0.195913058886822 | relative 1e-09 | pass |
| p N | R | 0.171 | 0.171 | relative 1e-09 | pass |
| p P | R | 0.265 | 0.265 | relative 1e-09 | pass |
| p K | R | 0.496 | 0.496 | relative 1e-09 | pass |
| F N | R | 1.53157846888647 | 1.53157846888647 | relative 1e-09 | pass |

Note: The design check found adjusted R squared 0.0753 and marginal p-values 0.171, 0.265 and 0.496.

### `table.explain_profiles_of measure="hellinger"`

**measure="hellinger": varespec and varechem, RDA with N, P and K** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| adjusted R squared | R | 0.0824713297170607 | 0.0824713297170607 | relative 1e-09 | pass |
| F all | R | 1.68911219341243 | 1.68911219341243 | relative 1e-09 | pass |
| p all | R | 0.048 | 0.048 | relative 1e-09 | pass |

Note: The design check found adjusted R squared 0.0825.

### `table.explain_profiles_of test_method="canonical correspondence"`

**test_method="canonical correspondence": varespec, CCA with Al, P and K** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| R squared | R | 0.309204040714597 | 0.309204040714597 | relative 1e-09 | pass |
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
| pseudo-F | R | 9.84780309008329 | 9.84780309008329 | relative 1e-09 | pass |
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
| LD1 row 1 size | R | 1.53886934430206 | 1.53886934430206 | relative 1e-09 | pass |

Note: simplydata takes the shares of the trace from MASS's own print (4 decimals, as print.lda rounds them), so R's side rounds svd^2 / sum(svd^2) the same way and they must agree exactly; the leave-one-out share and the scores are compared unrounded. (Before, the check read the one-decimal printout and allowed 0.4 %.) The design check found 0.686, 0.300 and 0.014, and 95 % correct.

### `table.add_correspondence_axes`

**varespec: correspondence analysis (CA)** (published; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| CA1 % | Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083 | 25.2 | 25.2 | within 0.05 (printed rounding) | pass |
| CA2 % | Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083 | 17.1 | 17.1 | within 0.05 (printed rounding) | pass |
| CA1 % | R | 25.2 | 25.2 | relative 1e-09 | pass |
| CA2 % | R | 17.1 | 17.1 | relative 1e-09 | pass |
| CA1 row 1 size | R | 0.108121658834308 | 0.108121658834308 | relative 1e-09 | pass |

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
| x1 on factor 2 | R | 0.591615557668105 | 0.591615557668105 | relative 1e-08 | pass |
| x4 on factor 1 | R | 0.8461030106398 | 0.8461030106398 | relative 1e-08 | pass |
| x7 on factor 3 | R | 0.73654365372812 | 0.73654365372812 | relative 1e-08 | pass |
| x9 on factor 2 | R | 0.382277778281328 | 0.382277778281328 | relative 1e-08 | pass |
| x9 on factor 3 | R | 0.456359959460632 | 0.456359959460632 | relative 1e-08 | pass |
| shared part of x1 | R | 0.476754007780132 | 0.476754007780132 | relative 1e-08 | pass |
| shared part of x9 | R | 0.46046138351728 | 0.46046138351728 | relative 1e-08 | pass |
| factors | R | 3 | 3 | relative 1e-08 | pass |

Note: Parallel analysis finds the three factors of Holzinger and Swineford's design (visual, verbal and speed); x9 goes with two of them, as the modification indices of the confirmatory model also show.

### `table.find_hidden_factors_behind how_many=`

**how_many=: three factors asked for, no parallel analysis** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x1 on factor 2 | R | 0.591615227616589 | 0.591615227616589 | relative 1e-08 | pass |
| x4 on factor 1 | R | 0.846102782504001 | 0.846102782504001 | relative 1e-08 | pass |
| x7 on factor 3 | R | 0.736544152684085 | 0.736544152684085 | relative 1e-08 | pass |
| x9 on factor 2 | R | 0.382275730401818 | 0.382275730401818 | relative 1e-08 | pass |
| x9 on factor 3 | R | 0.456359717134763 | 0.456359717134763 | relative 1e-08 | pass |
| shared part of x1 | R | 0.476754007780132 | 0.476754007780132 | relative 1e-08 | pass |
| shared part of x9 | R | 0.46046138351728 | 0.46046138351728 | relative 1e-08 | pass |
| factors | R | 3 | 3 | relative 1e-08 | pass |

Note: The oblimin rotation of GPArotation starts from random numbers, so both sides set R's seed first (unseeded, the loadings change in the sixth digit from run to run).

### `table.find_hidden_factors_behind rotation=`

**rotation=: promax, with principal axis factoring** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| x1 on factor 2 | R | 0.0390228442789629 | 0.0390228442789629 | relative 1e-08 | pass |
| x4 on factor 1 | R | 0.849737553166453 | 0.849737553166453 | relative 1e-08 | pass |
| x7 on factor 3 | R | -0.226409506419214 | -0.226409506419214 | relative 1e-08 | pass |
| x9 on factor 2 | R | 0.476602216003329 | 0.476602216003329 | relative 1e-08 | pass |
| x9 on factor 3 | R | 0.344044301672691 | 0.344044301672691 | relative 1e-08 | pass |
| shared part of x1 | R | 0.476914814044882 | 0.476914814044882 | relative 1e-08 | pass |
| shared part of x9 | R | 0.460820618036742 | 0.460820618036742 | relative 1e-08 | pass |
| factors | R | 3 | 3 | relative 1e-08 | pass |

### `table.find_hidden_factors_behind test_method=`

**test_method=: maximum likelihood with varimax, as R factanal** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| own part of x1 | statsmodels Factor (method="ml"), run to 1e-14 | 0.512529527173443 | 0.512528119648074 | relative 1e-05 | pass |
| own part of x2 | statsmodels Factor (method="ml"), run to 1e-14 | 0.7487351603869 | 0.748735965229153 | relative 1e-05 | pass |
| own part of x3 | statsmodels Factor (method="ml"), run to 1e-14 | 0.542773290729761 | 0.542774175087915 | relative 1e-05 | pass |
| own part of x4 | statsmodels Factor (method="ml"), run to 1e-14 | 0.279193093920192 | 0.279192868139681 | relative 1e-05 | pass |
| own part of x5 | statsmodels Factor (method="ml"), run to 1e-14 | 0.242877320676015 | 0.242877134812998 | relative 1e-05 | pass |
| own part of x6 | statsmodels Factor (method="ml"), run to 1e-14 | 0.30521585555841 | 0.305215969175691 | relative 1e-05 | pass |
| own part of x7 | statsmodels Factor (method="ml"), run to 1e-14 | 0.502207221916071 | 0.502208468235662 | relative 1e-05 | pass |
| own part of x8 | statsmodels Factor (method="ml"), run to 1e-14 | 0.468550489794599 | 0.468549619219853 | relative 1e-05 | pass |
| own part of x9 | statsmodels Factor (method="ml"), run to 1e-14 | 0.543247686483436 | 0.543246565615491 | relative 1e-05 | pass |
| own part of x1 | R | 0.512529527173443 | 0.512528062226372 | relative 1e-05 | pass |
| own part of x2 | R | 0.7487351603869 | 0.748735775103766 | relative 1e-05 | pass |
| own part of x3 | R | 0.542773290729761 | 0.542774360019842 | relative 1e-05 | pass |
| own part of x4 | R | 0.279193093920192 | 0.279193042201536 | relative 1e-05 | pass |
| own part of x5 | R | 0.242877320676015 | 0.24287729927771 | relative 1e-05 | pass |
| own part of x6 | R | 0.30521585555841 | 0.305215788139909 | relative 1e-05 | pass |
| own part of x7 | R | 0.502207221916071 | 0.502208589419742 | relative 1e-05 | pass |
| own part of x8 | R | 0.468550489794599 | 0.468549571047053 | relative 1e-05 | pass |
| own part of x9 | R | 0.543247686483436 | 0.543246719036652 | relative 1e-05 | pass |
| x1 on factor 2 | R | 0.622657847373776 | 0.622659197498638 | relative 1e-05 | pass |
| x4 on factor 1 | R | 0.826999673867174 | 0.826999686293563 | relative 1e-05 | pass |
| x7 on factor 3 | R | 0.695873917746766 | 0.695872958542921 | relative 1e-05 | pass |
| x9 on factor 3 | R | 0.5236179828285 | 0.523618567249351 | relative 1e-05 | pass |

Note: The part of each column the factors do not share (the uniqueness) does not depend on the rotation and is checked against base R factanal and statsmodels; the varimax loadings are checked against factanal (the same factor order and signs here). Both references are run to convergence (factanal's optim with factr = 1, statsmodels to 1e-14); they then agree with simplydata (R psych::fa(fm = "ml") with its own stopping rule) to 3e-6, so the check allows 1e-5. With their default stopping rules the three differed by up to 1.6e-5, and the check allowed 1e-3.

### `table.check_hidden_factors`

**the three-factor model of the lavaan paper** (published; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | Rosseel (2012), JSS 48(2) | 85.3055217699727 | 85.306 | within 0.0005 (printed rounding) | pass |
| degrees of freedom | exact | 24 | 24 | within 0 | pass |
| CFI | Rosseel (2012), JSS 48(2) | 0.930559651799336 | 0.931 | within 0.0005 (printed rounding) | pass |
| TLI | Rosseel (2012), JSS 48(2) | 0.895839477699004 | 0.896 | within 0.0005 (printed rounding) | pass |
| RMSEA | Rosseel (2012), JSS 48(2) | 0.0921214845101686 | 0.092 | within 0.0005 (printed rounding) | pass |
| RMSEA 90 % CI low | Rosseel (2012), JSS 48(2) | 0.0714184904399382 | 0.071 | within 0.0005 (printed rounding) | pass |
| RMSEA 90 % CI high | Rosseel (2012), JSS 48(2) | 0.113678016811963 | 0.114 | within 0.0005 (printed rounding) | pass |
| SRMR | Rosseel (2012), JSS 48(2) | 0.0652050571843865 | 0.065 | within 0.0005 (printed rounding) | pass |
| chi-square | R | 85.3055217699727 | 85.3055217699727 | relative 1e-08 | pass |
| degrees of freedom | R | 24 | 24 | relative 1e-08 | pass |
| CFI | R | 0.930559651799336 | 0.930559651799336 | relative 1e-08 | pass |
| TLI | R | 0.895839477699004 | 0.895839477699004 | relative 1e-08 | pass |
| RMSEA | R | 0.0921214845101686 | 0.0921214845101686 | relative 1e-08 | pass |
| RMSEA 90 % CI low | R | 0.0714184904399382 | 0.0714184904399382 | relative 1e-08 | pass |
| RMSEA 90 % CI high | R | 0.113678016811963 | 0.113678016811963 | relative 1e-08 | pass |
| SRMR | R | 0.0652050571843865 | 0.0652050571843865 | relative 1e-08 | pass |

Note: Rosseel (2012) prints the fit of this model to three decimals; the p-value of the chi-square test is below 0.001 there too.

**empty cells: 30 visual-perception scores taken out, full information** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| chi-square | R | 87.401846969425 | 87.401846969425 | relative 1e-08 | pass |
| x1 loading | R | 0.791634162191103 | 0.791634162191103 | relative 1e-08 | pass |
| CFI | R | 0.927941793738212 | 0.927941793738212 | relative 1e-08 | pass |

Note: Real data with 30 cells emptied on purpose (the first 30 rows of x1): every row stays in, as with lavaan's missing = "ml"; lavaan's own default would leave the 30 rows out.

### `table.check_hidden_factors formula=`

**formula=: the speed factor explained by the visual one (lavaan sem)** (real data; data: Holzinger & Swineford 1939 (lavaan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| path | R | 0.460317218924394 | 0.460317218924394 | relative 1e-08 | pass |
| its standard error | R | 0.0741697801385859 | 0.0741697801385859 | relative 1e-08 | pass |
| chi-square | R | 47.4133581632698 | 47.4133581632698 | relative 1e-08 | pass |
| CFI | R | 0.879367051234156 | 0.879367051234156 | relative 1e-08 | pass |

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
| Moran's I | R | 0.116566169069248 | 0.116566169069248 | relative 1e-09 | pass |

Note: Over 3 km great-circle and grid distances hardly differ, so Moran's I is close to the grid's 0.1191.

### `table.find_variogram_of`

**meuse: the spherical variogram of log zinc** (published; data: meuse (sp))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| nugget | gstat vignette (Pebesma) | 0.0506597095446436 | 0.0507 | within 5e-05 (printed rounding) | pass |
| partial sill | gstat vignette (Pebesma) | 0.590605107555405 | 0.5906 | within 5e-05 (printed rounding) | pass |
| range | gstat vignette (Pebesma) | 897.001083383488 | 897 | within 0.5 (printed rounding) | pass |
| nugget | R | 0.0506597095446436 | 0.0506597095446436 | relative 1e-07 | pass |
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
| location | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 3.87474985624041 | 3.87 | within 0.005 (printed rounding) | pass |
| scale | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | 0.19804395808428 | 0.198 | within 0.0005 (printed rounding) | pass |
| shape | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 3.4.1 | -0.0501095351295167 | -0.05 | within 0.0005 (printed rounding) | pass |
| location | SciPy genextreme.fit run to 1e-14 (shape c = -xi) | 3.87474985624041 | 3.87474985806358 | relative 1e-06 | pass |
| scale | SciPy genextreme.fit run to 1e-14 (shape c = -xi) | 0.19804395808428 | 0.198043958635516 | relative 1e-06 | pass |
| shape | SciPy genextreme.fit run to 1e-14 (shape c = -xi) | -0.0501095351295167 | -0.0501095460971942 | relative 1e-06 | pass |
| location | R | 3.87474985624041 | 3.87474985509283 | relative 1e-06 | pass |
| scale | R | 0.19804395808428 | 0.198043956945225 | relative 1e-06 | pass |
| shape | R | -0.0501095351295167 | -0.0501095325366495 | relative 1e-06 | pass |

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
| scale | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 4.4.1 | 7.44026894085537 | 7.44 | within 0.005 (printed rounding) | pass |
| shape | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, 4.4.1 | 0.18449906745455 | 0.184 | within 0.0005 (printed rounding) | pass |
| scale | R | 7.44026894085537 | 7.44025220565683 | relative 0.0001 | pass |
| shape | R | 0.18449906745455 | 0.184497962931526 | relative 0.0001 | pass |

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
| forecast for 1961-01 | R | 445.634898647403 | 445.634898647403 | relative 1e-09 | pass |
| 95 % low | R | 423.085050384673 | 423.085050384673 | relative 1e-09 | pass |
| 95 % high | R | 468.184746910132 | 468.184746910132 | relative 1e-09 | pass |
| forecast for 1961-12 | R | 465.507571636887 | 465.507571636887 | relative 1e-09 | pass |

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
| pi0 | Storey & Tibshirani (2003), PNAS 100:9440-9445 | 0.669926026474838 | 0.67 | within 0.005 (printed rounding) | pass |
| pi0 | R | 0.669926026474838 | 0.669926026474838 | relative 1e-09 | pass |
| q-values below 0.05 | R | 162 | 162 | relative 1e-09 | pass |
| first q-value | R | 0.0881916317044274 | 0.0881916317044274 | relative 1e-09 | pass |

Note: pi0 is read back from the table as the q-value of the largest p-value divided by that p-value (qvalue's last q-value is pi0 times it). The paper finds 160 genes at q < 0.05 on its own p-values; qvalue's copy of the p-values gives 162.

### `table.add_adjusted_p_value_column test_method="local fdr"`

**test_method="local fdr": Hedenfalk's 3170 genes, the local false discovery rate** (real data; data: hedenfalk (qvalue))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| below 0.05 | R | 85 | 85 | relative 1e-09 | pass |
| first | R | 0.168270194881541 | 0.168270194881541 | relative 1e-09 | pass |
| smallest | R | 0.00656991586563179 | 0.00656991586563179 | relative 1e-09 | pass |

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
| 95 % CI high | R | 87.0814854544509 | 87.0814854544509 | relative 1e-09 | pass |

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
| meals | R | -3.11062899440932 | -3.11062899440932 | relative 1e-09 | pass |
| meals standard error | R | 0.275765488815877 | 0.275765488815877 | relative 1e-09 | pass |
| ell p-value | R | 0.193873946007251 | 0.193873946007251 | relative 1e-09 | pass |
| intercept | R | 823.857925625165 | 823.857925625165 | relative 1e-09 | pass |

### `table.compare_averages_of after use_survey_design()`

**the stratified api sample: API 2000 with and without an award** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| difference | R | 44.6874939550245 | 44.6874939550245 | relative 1e-09 | pass |
| t | R | 2.3036073198213 | 2.3036073198213 | relative 1e-09 | pass |
| p-value | R | 0.0222935238150612 | 0.0222935238150612 | relative 1e-09 | pass |

### `table.compare_counts_of after use_survey_design()`

**the stratified api sample: awards by school type (Rao-Scott)** (real data; data: api stratified sample (survey))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| F | R | 14.1694081180078 | 14.1694081180078 | relative 1e-09 | pass |
| p-value | R | 2.08210867642841e-06 | 2.08210867642845e-06 | relative 1e-09 | pass |
| design degrees of freedom | R | 371.371769351819 | 371.371769351819 | relative 1e-09 | pass |

### `table.compare_balanced_groups_of`

**lalonde: weighting, the effect for everyone (ATE)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| effect | R | 224.676308271439 | 224.676308271439 | relative 1e-09 | pass |
| standard error | R | 876.193185532072 | 876.193185532072 | relative 1e-09 | pass |
| p-value | R | 0.797624033422354 | 0.797624033422354 | relative 1e-09 | pass |

Note: The randomised NSW experiment found 1794 dollars (Dehejia & Wahba 1999); the survey comparison group is very unlike the trained men, so balancing on these columns does not recover it fully.

**lalonde: the balance table (standardised differences, cobalt)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| race black before | R | 1.67082635003592 | 1.67082635003592 | relative 1e-09 | pass |
| race black after | R | 0.130249813461065 | 0.130249813461065 | relative 1e-09 | pass |
| re74 after | R | -0.273989428670678 | -0.273989428670678 | relative 1e-09 | pass |

### `table.compare_balanced_groups_of test_method="matching"`

**test_method="matching": lalonde, 1:1 nearest neighbour, the effect among the trained men (ATT)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| effect | R | 894.367480270274 | 894.367480270274 | relative 1e-09 | pass |
| standard error | R | 705.229764061618 | 705.229764061618 | relative 1e-09 | pass |

Note: The MatchIt vignette's own analysis of lalonde: ATT 894, clustered standard error 705.

**test_method="matching": lalonde, with a caliper of 0.2 standard deviations of the logit (match_within=0.2)** (real data; data: lalonde)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| effect | R | 1770.60290641026 | 1770.60290641026 | relative 1e-09 | pass |
| standard error | R | 924.234347046261 | 924.234347046261 | relative 1e-09 | pass |

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
| indirect effect | statsmodels Mediation (with_seed=1) | -0.0163155082561465 | -0.0163155082561465 | relative 1e-09 | pass |
| indirect low | statsmodels Mediation (with_seed=1) | -0.0457537091325962 | -0.0457537091325962 | relative 1e-09 | pass |
| total effect | statsmodels Mediation (with_seed=1) | -0.0554964945177591 | -0.0554964945177591 | relative 1e-09 | pass |
| indirect effect | R | -0.0163155082561465 | -0.0157446450289038 | within 4 Monte Carlo SE (0.00185) | pass |
| total effect | R | -0.0554964945177591 | -0.0560093450307453 | within 4 Monte Carlo SE (0.00584) | pass |

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
| wt 95 % low | R | -5.17810665610188 | -5.17810665610188 | relative 1e-09 | pass |
| wt 95 % high | R | -2.54937525696019 | -2.54937525696019 | relative 1e-09 | pass |
| hp | R | -0.0317827715959909 | -0.0317827715959909 | relative 1e-09 | pass |
| sigma | R | 2.66823086364635 | 2.66823086364635 | relative 1e-09 | pass |
| wt R-hat | R | 1.00142396006417 | 1.00142396006417 | relative 1e-09 | pass |

Note: lm() gives -3.88 for wt and -0.0318 for hp; the posterior medians are close to them because rstanarm's priors are weak here.

### `table.explain test_method="bayesian", grouped_by=`

**test_method="bayesian", grouped_by=: sleepstudy, reaction time over days (rstanarm stan_glmer)** (real data; data: sleepstudy (lme4))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Days | R | 10.4335236539881 | 10.4335236539881 | relative 1e-09 | pass |
| Days 95 % low | R | 8.86591025068702 | 8.86591025068702 | relative 1e-09 | pass |
| Days 95 % high | R | 12.026372436322 | 12.026372436322 | relative 1e-09 | pass |
| intercept | R | 250.900430665805 | 250.900430665805 | relative 1e-09 | pass |

Note: lme4's REML estimates are 251.4 and 10.47 (Bates et al. 2015); the posterior medians are close.

### `table.check_model_of test_method="bayesian"`

**test_method="bayesian": mtcars, the posterior predictive check of fuel use from weight** (real data; data: mtcars)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| data density at point 100 | R | 0.060520300921311 | 0.060520300921311 | relative 1e-09 | pass |
| set 3 at point 100 | R | 0.0250130477338937 | 0.0250130477338937 | relative 1e-09 | pass |
| set 50 at point 200 | R | 0.0327979199969546 | 0.0327979199969546 | relative 1e-09 | pass |
| grid end | R | 37.0622730135304 | 37.0622730135304 | relative 1e-09 | pass |

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
| p-value | R | 0.0690494519399047 | 0.0690494519399045 | relative 1e-10 | pass |
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
| PC2 of row 1 | statsmodels PCA (SVD) | 0.478423832124897 | 0.478423832124899 | relative 1e-09 | pass |
| PC1 of row 150 | statsmodels PCA (SVD) | 0.957448488427992 | 0.957448488427994 | relative 1e-09 | pass |
| PC1 of row 1 | R | -2.25714117564812 | -2.25714117564812 | relative 1e-09 | pass |
| PC2 of row 1 | R | 0.478423832124897 | 0.4784238321249 | relative 1e-09 | pass |
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
| curve at the highest concentration | R | 200.968851192381 | 200.968851985722 | relative 1e-06 | pass |
| curve at the lowest | R | 50.5659785739787 | 50.565977711308 | relative 1e-06 | pass |

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
| NMDS2 of plot 1 | R | -0.71582776131882 | -0.71582776131882 | relative 1e-09 | pass |
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
| its Cook's distance | R | 0.69199991633951 | 0.691999916339509 | relative 1e-09 | pass |
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
| BP | R | 0.880722470178817 | 0.880722470178814 | relative 1e-09 | pass |
| p | R | 0.64380381454434 | 0.643803814544341 | relative 1e-09 | pass |

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
| p | residuals of statsmodels OLS, SciPy pearsonr (the definition) | 1.11964713620002e-06 | 1.11964713620001e-06 | relative 1e-09 | pass |
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
| `table.as_pandas` | Polars | pandas | table | relative 1e-09 | pass |
| `table.as_pandas` | Polars | polars | table | relative 1e-09 | pass |
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
| `table.start_again` | - | - | none | relative 0 | pass |
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
| [checks against R (no published example)](https://doi.org/10.1186/1471-2288-11-94) | no data: the inputs are written in the code, and R (or SciPy with the same seed) is the reference; used where no published worked example was read | simplydata's reliability study. Simulation checks follow Arnold, B. F., Hogan, D. R., Colford, J. M. & Hubbard, A. E. (2011). Simulation methods to estimate design power. BMC Medical Research Methodology 11, 94. | No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored. |
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
