# simplydata reliability report

Made by `python validation/make_report.py` on 2026-11-20. Generated: do not edit by hand.

Each simplydata word is run on real, published data and compared with the published answer, with the package simplydata uses underneath called directly, and with R. Each "same underneath" box of the manual is run next to its word and compared too. How it works, and the datasets with their licences: [validation/README.md](README.md).

**269 checks passed, 0 failed, 0 skipped** (skipped: R or an R package is not installed on this computer).

## Setup

| | |
|---|---|
| system | Windows 11 (AMD64) |
| Python | 3.12.10 |
| simplydata | 0.1.0 (imported from src/simplydata of this copy) |
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
| slope standard error | statsmodels WLS | 0.0381548260706374 | 0.0381548260706378 | relative 1e-09 | pass |
| intercept | statsmodels WLS | 12.7964165214901 | 12.7964165214901 | relative 1e-09 | pass |
| slope | R | 0.204801163243055 | 0.204801163243058 | relative 1e-09 | pass |
| slope standard error | R | 0.0381548260706374 | 0.0381548260706375 | relative 1e-09 | pass |
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

### `table.explain method="log-binomial"`

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
| 95 % CI low | R | 0.638744784688276 | 0.650788189386304 | relative 0.05 | pass |
| 95 % CI high | R | 1.17896864783934 | 1.17581758089783 | relative 0.05 | pass |

Note: R draws other random rows than SciPy, so R is a check of the same method within Monte Carlo error (5 %); SciPy with the same seed gives the same interval exactly.

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
| Nagelkerke | R | 0.085 | 0.085063735572079 | relative 0.01 | pass |
| Tjur | R | 0.058 | 0.058487286125848 | relative 0.01 | pass |

Note: The two measures are printed with 3 decimals, so the check allows that rounding (1 % here).

### `table.explain crossed_with=`

**people and items crossed: verbal aggression (yes or no) from anger and gender** (real data; data: VerbAgg)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| anger | R | 0.0574460971215786 | 0.0574458848078184 | relative 0.001 | pass |
| anger standard error | R | 0.0168528280463522 | 0.0168451180133759 | relative 0.001 | pass |
| gender | R | 0.320646326996743 | 0.320648193677949 | relative 0.001 | pass |

Note: simplydata runs lme4 itself (statsmodels cannot fit crossed groupings); this case checks the model R gets from explain() against R's own formula. lme4 works out a glmer's standard errors from a numerical Hessian, which moves in the fourth digit with how the columns are passed (a model matrix or a formula), hence 1e-3.

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

## 2. The same underneath (the manual's boxes)

Each box's library code is run next to the simplydata word and compared. Table words run on a pandas and on a Polars table.

| word | compared with | table | how | tolerance | result |
|---|---|---|---|---|---|
| `draw_bars` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_histogram` | seaborn | pandas | chart | relative 1e-09 | pass |
| `draw_dots` | seaborn | pandas | chart | relative 1e-09 | pass |
| `trade_off_curve` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.keep_rows_where` | pandas | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_where` | Polars | pandas | table | relative 1e-09 | pass |
| `table.keep_rows_where` | pandas | polars | table | relative 1e-09 | pass |
| `table.keep_rows_where` | Polars | polars | table | relative 1e-09 | pass |
| `table.find_average_of` | pandas | pandas | table | relative 1e-09 | pass |
| `table.find_average_of` | Polars | pandas | table | relative 1e-09 | pass |
| `table.find_average_of` | pandas | polars | table | relative 1e-09 | pass |
| `table.find_average_of` | Polars | polars | table | relative 1e-09 | pass |
| `nums.find_median` | NumPy | pandas | value | relative 1e-12 | pass |
| `table.compare_averages_of` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.fit_line` | SciPy | polars | result | relative 1e-09 | pass |
| `dist.find_chance_that_value` | SciPy | pandas | value | relative 1e-12 | pass |
| `table.explain weights=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain weights=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.explain outcome="yes or no (overdispersed)"` | statsmodels | pandas | result | relative 1e-08 | pass |
| `table.explain outcome="yes or no (overdispersed)"` | statsmodels | polars | result | relative 1e-08 | pass |
| `table.explain matched_by=` | statsmodels | pandas | result | relative 1e-06 | pass |
| `table.explain matched_by=` | statsmodels | polars | result | relative 1e-06 | pass |
| `table.explain show="risk ratios"` | statsmodels | pandas | result | relative 1e-06 | pass |
| `table.explain show="risk ratios"` | statsmodels | polars | result | relative 1e-06 | pass |
| `table.explain method="log-binomial"` | statsmodels | pandas | result | relative 1e-06 | pass |
| `table.explain method="log-binomial"` | statsmodels | polars | result | relative 1e-06 | pass |
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
| `table.explain outcome="counts with many zeros that vary a lot"` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.explain outcome="counts with many zeros that vary a lot"` | R + Python | polars | result | relative 1e-05 | pass |
| `table.explain outcome="counts in two steps"` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.explain outcome="counts in two steps"` | R + Python | polars | result | relative 1e-05 | pass |
| `table.explain zero_part_using=` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.explain zero_part_using=` | R + Python | polars | result | relative 1e-05 | pass |

How each kind is compared:

- **value**: the number the word gives, against the library's number
- **table**: the table the word gives, against the library's table (values and column order)
- **result**: the numbers in simplydata's result table (statistic, degrees of freedom, p-value ...) against the library's result
- **chart**: the chart's data (bars, dots, lines, labels, limits ...), not its pixels

## Choices simplydata makes

Where simplydata's default differs from the package underneath, it is listed here, so a difference is never hidden. The manual shows each one as a numbered mark in the code.

- `draw_bars` (1): simplydata draws no error bars unless you ask (error=); seaborn's own default draws a bootstrap 95 % interval on each bar.
- `draw_histogram` (1): simplydata makes 10 bins unless you say with_bins=; seaborn's own default chooses the number of bins from the data.
- `trade_off_curve` (1): higher scores count as positive (direction = "<"); positive_when="lower" turns it round.
- `trade_off_curve` (2): the AUC and its 95 % interval by DeLong's method, written in the legend.
- `trade_off_curve` (3): the best cut-off by Youden's index (the most found cases minus false alarms) is marked with a dot.
- `table.keep_rows_where` (1): is_above= means strictly above (>); use is_at_least= for >=. Rows with an empty cell in "marks" are left out, as in pandas and Polars.
- `table.find_average_of` (1): groups stay in the order they first appear (sort=False, maintain_order=True); empty cells are skipped, as pandas and Polars do (NumPy's mean would give nan).
- `nums.find_median` (1): empty values are skipped (np.nanmedian); NumPy's np.median would give nan.
- `table.compare_averages_of` (1): Welch's t-test, which does not assume both groups have the same spread; SciPy's own default (equal_var=True) is Student's t-test, which does.
- `table.fit_line` (1): the 95 % interval of the slope uses the t distribution with n - 2 degrees of freedom, as R's confint(lm(...)).
- `dist.find_chance_that_value` (1): the chance above a value is the survival function sf(), not 1 - cdf(): it stays accurate far out in the tail.
- `table.explain weights=` (1): precision weights, as R lm(weights =): statsmodels WLS; for the other outcomes GLM(var_weights=). Not freq_weights, which would change the degrees of freedom.
- `table.explain outcome="yes or no (overdispersed)"` (1): quasi-binomial as R glm(family = quasibinomial): the shares, with the tries as var_weights and the Pearson dispersion (scale="X2"). A two-column endog would give statsmodels another dispersion.
- `table.explain matched_by=` (1): conditional logistic regression with the exact conditional likelihood, as R survival::clogit() (its default method = "exact"); no intercept, each pair compared only with itself.
- `table.explain matched_by=` (2): fitted by Newton's method to the end; statsmodels' default (BFGS) stops a little short of the best estimates.
- `table.explain show="risk ratios"` (1): modified Poisson regression (Zou 2004): a Poisson model for the 0/1 column with robust (HC0) standard errors, as R glm(family = poisson) with sandwich::vcovHC(type = "HC0"); it always converges, where log-binomial (method="log-binomial") often does not.
- `table.explain method="log-binomial"` (1): a binomial model with a log link, as R glm(family = binomial(link = "log")); when it does not converge (a predicted chance reaches 1), simplydata says so and points to the default modified Poisson regression.
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

## Datasets

| dataset | what | source | licence |
|---|---|---|---|
| [NIST Norris](https://www.itl.nist.gov/div898/strd/lls/data/Norris.shtml) | 36 observations of ozone monitor calibration; certified straight-line fit (NIST StRD, lower difficulty) | Norris, J., NIST. Calibration of Ozone Monitors. In: NIST Statistical Reference Datasets (StRD), Linear Regression, dataset Norris. National Institute of Standards and Technology. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [Anscombe's quartet](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/anscombe.html) | four sets of 11 (x, y) pairs with the same straight-line fit | Anscombe, F. J. (1973). Graphs in statistical analysis. The American Statistician 27(1), 17-21. Copy from R's datasets package (anscombe). | The 88 published numbers, as in R's datasets package (GPL-2 \| GPL-3). |
| [NIST Michelso](https://www.itl.nist.gov/div898/strd/univ/michelso.html) | 100 measurements of the speed of light in air by Michelson (1879); certified mean and standard deviation | Dorsey, E. N. (1944). The Velocity of Light. Transactions of the American Philosophical Society 34(1), 1-110, Table 22. In: NIST StRD, Univariate Summary Statistics, dataset Michelso. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Mavro](https://www.itl.nist.gov/div898/strd/univ/mavro.html) | 50 filter transmittance measurements by R. Mavrodineanu (NIST); certified mean and standard deviation | Mavrodineanu, R., NIST. Filter transmittance data. In: NIST StRD, Univariate Summary Statistics, dataset Mavro. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST NumAcc4](https://www.itl.nist.gov/div898/strd/univ/numacc4.html) | 1001 nine-digit numbers that differ only in the last digit; constructed by NIST to test accuracy (higher difficulty); certified mean 10000000.2 exactly | Simon, S. D. & Lesage, J. P. (1989). Assessing the accuracy of ANOVA calculations in statistical software. Computational Statistics & Data Analysis 8, 325-332. In: NIST StRD, dataset NumAcc4. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [Student's sleep data](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/sleep.html) | extra hours of sleep for 10 patients with each of two drugs | Cushny, A. R. & Peebles, A. R. (1905). The action of optical isomers. II. Hyoscines. Journal of Physiology 32, 501-510. Analysed by Student (1908). The probable error of a mean. Biometrika 6(1), 1-25. Copy from R's datasets package (sleep). | Public domain (published 1905 and 1908); the copy in R's datasets package is GPL-2 \| GPL-3. |
| [aSAH (pROC)](https://cran.r-project.org/package=pROC) | 113 patients with aneurysmal subarachnoid haemorrhage: outcome and the biomarker s100b | Turck, N. et al. (2010). A multiparameter panel method for outcome prediction following aneurysmal subarachnoid hemorrhage. Intensive Care Medicine 36, 107-115. Shipped with R's pROC package (Robin, X. et al. (2011). BMC Bioinformatics 12, 77). | GPL-3 or later (pROC). Not stored here: read from the installed pROC package, so it needs R. |
| made-up | small made-up tables for edge cases (empty cells, no rows left, an exact line) | simplydata's validation/cases.py. | Same as simplydata (see LICENSE). |
| [standard normal table](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3671.htm) | the area under the standard normal curve from 0 to z, to 5 decimals (no data: a published table) | NIST/SEMATECH e-Handbook of Statistical Methods, section 1.3.6.7.1, Cumulative Distribution Function of the Standard Normal Distribution. | Public domain in the United States (a work of the US Government); one number is quoted, nothing stored. |
| [Galton's sweet peas](https://cran.r-project.org/package=alr4) | 7 parent sweet-pea seed diameters (hundredths of an inch), each with the average and the standard deviation of the diameters of its offspring seeds | Galton, F. (1877). Typical laws of heredity. Nature 15, 492-495, 512-514, 532-533. Used for weighted least squares in Weisberg, S. (2014). Applied Linear Regression, 4th ed., Wiley, section 7.1. Copy from the R package alr4 (galtonpeas). | Published 1877 (public domain); the alr4 copy is GPL (>= 2). |
| [Orobanche seeds](https://cran.r-project.org/package=agridat) | 21 plates of seeds of two Orobanche varieties (O73, O75) on bean or cucumber root extract: the seeds that germinated, out of the seeds on the plate | Crowder, M. J. (1978). Beta-binomial anova for proportions. Applied Statistics 27(1), 34-37. Copy from the R package agridat (crowder.seeds; Wright, K.), through Rdatasets. | The published counts (facts from a 1978 paper); the agridat copy is MIT licensed. |
| [infert](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/infert.html) | 248 women in 83 matched sets (1 or 2 cases of secondary infertility, each with 2 controls matched on age, parity and education): earlier spontaneous and induced abortions | Trichopoulos, D., Handanos, N., Danezis, J., Kalandidi, A. & Kalapothaki, V. (1976). Induced abortion and secondary infertility. British Journal of Obstetrics and Gynaecology 83, 645-650. Copy from R's datasets package (infert). | Published 1976; R's datasets copy is GPL-2 \| GPL-3. |
| [birthwt](https://cran.r-project.org/package=MASS) | 189 births at Baystate Medical Center, Springfield, Massachusetts (1986): low birth weight (below 2.5 kg) and the mother's age, weight, smoking, race and history | Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Copy from the R package MASS (birthwt; Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed. Springer). | The MASS copy is GPL-2 \| GPL-3. |
| [stackloss](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/stackloss.html) | 21 days of a plant oxidising ammonia to nitric acid: air flow, cooling water temperature, acid concentration and the ammonia lost (stack loss) | Brownlee, K. A. (1965). Statistical Theory and Methodology in Science and Engineering, 2nd ed. Wiley, pp. 491-500. Copy from R's datasets package (stackloss). | Published 1960/1965; R's datasets copy is GPL-2 \| GPL-3. |
| [mtcars](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/mtcars.html) | 32 cars (1973-74 models): fuel use (miles per gallon) and 10 design and performance measures | Henderson, H. V. & Velleman, P. F. (1981). Building multiple regression models interactively. Biometrics 37, 391-411 (data from Motor Trend, 1974). Copy from R's datasets package (mtcars). | Published 1974 and 1981; R's datasets copy is GPL-2 \| GPL-3. |
| [VerbAgg](https://cran.r-project.org/package=lme4) | verbal aggression: 316 people each answered 24 items (would they curse, scold or shout in a frustrating situation?), yes or no; people and items are crossed | De Boeck, P. & Wilson, M. (2004). Explanatory Item Response Models. Springer (data collected by Vansteelandt, 2000). Copy from the R package lme4 (VerbAgg). | The lme4 copy is GPL (>= 2). |
| [NMES 1988](https://www.jstatsoft.org/v027/i08) | 4406 people aged 66 and over in the US National Medical Expenditure Survey 1987/88: physician office visits, hospital stays, self-rated health, chronic conditions, gender, years of school and private insurance (7 of the 19 columns) | Deb, P. & Trivedi, P. K. (1997). Demand for medical care by the elderly: a finite mixture approach. Journal of Applied Econometrics 12, 313-336. Analysed with hurdle and zero-inflated models in Zeileis, A., Kleiber, C. & Jackman, S. (2008). Regression models for count data in R. Journal of Statistical Software 27(8), 1-25. Copy from the R package AER (NMES1988), through Rdatasets. | A US Government survey (public domain); the AER copy is GPL-2 \| GPL-3; the JSS article is CC BY. |
