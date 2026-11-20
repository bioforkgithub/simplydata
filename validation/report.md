# simplydata reliability report

Made by `python validation/make_report.py` on 2026-11-20. Generated: do not edit by hand.

Each simplydata word is run on real, published data and compared with the published answer, with the package simplydata uses underneath called directly, and with R. Each "same underneath" box of the manual is run next to its word and compared too. How it works, and the datasets with their licences: [validation/README.md](README.md).

**773 checks passed, 0 failed, 0 skipped** (skipped: R or an R package is not installed on this computer).

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
| b | R | 2.98221907127508 | 2.98221907127508 | relative 1e-09 | pass |
| c | R | 0.48141318844625 | 0.48141318844625 | relative 1e-09 | pass |
| d | R | 7.79295829369992 | 7.79295829369992 | relative 1e-09 | pass |
| ED10 | R | 1.46370565552037 | 1.46370565552037 | relative 1e-09 | pass |
| ED50 | R | 3.05795496654805 | 3.05795496654805 | relative 1e-09 | pass |
| ED90 | R | 6.38864005353004 | 6.38864005353004 | relative 1e-09 | pass |
| ED50 95 % CI low | R | 2.67052620764518 | 2.67052620764518 | relative 1e-09 | pass |

Note: Python has no dose-response package with drc's ED intervals, so R drc itself is the second calculation. Ritz et al. (2015) analyse these data with the same LL.4 model.

### `table.fit_dose_response outcome="yes or no"`

**Bliss's beetles: LD50 from the logistic curve on log dose (yes or no)** (published; data: Bliss beetles)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| LD50 | Dobson & Barnett (2008) | 59.1181676197406 | 59.1186543855778 | within 0.01 (printed rounding) | pass |
| LD50 | statsmodels GLM (binomial, logit) on log10 dose | 59.1181676197406 | 59.1181676064851 | relative 1e-06 | pass |
| LD50 | R | 59.1181676197406 | 59.1181676064854 | relative 1e-06 | pass |

Note: The 2 parameter log-logistic curve with binomial errors is logistic regression on log dose, so its LD50 is the published fit's; the tolerance allows the printed 3 decimals of the fit.

### `fit_dose_response`

**the drawn ryegrass curve is drc's** (real data; data: ryegrass (drc))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | R | 301 | 301 | relative 1e-09 | pass |
| curve at the highest dose | R | 0.48946869915202 | 0.48946869915202 | relative 1e-09 | pass |
| curve at dose 0 | R | 7.79295829369992 | 7.79295829369992 | relative 1e-09 | pass |

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

### `table.fit_curve of_kind="michaelis-menten"`

**Puromycin (treated): a Michaelis-Menten curve** (published; data: Puromycin (treated))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Vm | Bates & Watts (1988) | 212.683742870014 | 212.7 | within 0.05 (printed rounding) | pass |
| K | Bates & Watts (1988) | 0.0641212812688425 | 0.06412 | within 5e-06 (printed rounding) | pass |
| Vm | R | 212.683742870014 | 212.683707271206 | relative 1e-05 | pass |
| K | R | 0.0641212812688425 | 0.0641212257944682 | relative 1e-05 | pass |

Note: R nls() stops at a relative offset of 1e-5, so it agrees to about 1e-5.

### `table.fit_line method="standardised major axis"`

**leaf lifespan against leaf mass per area: standardised major axis (log10)** (real data; data: leaflife (smatr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.31503061916202 | 1.31503061916202 | relative 1e-09 | pass |
| intercept | R | -2.69880047584921 | -2.69880047584921 | relative 1e-09 | pass |
| slope 95 % CI low | R | 1.09626126001275 | 1.09626126001275 | relative 1e-09 | pass |

Note: Warton et al. (2006) fit these data on log scales; the slope is about 1.3.

### `table.fit_line method="deming", y_error_over_x_error=`

**creatinine in plasma against serum: Deming line with y_error_over_x_error=4** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.01786319565374 | 1.01786319565374 | relative 1e-09 | pass |
| slope standard error | R | 0.0341143809499105 | 0.0341143809499105 | relative 1e-09 | pass |

Note: mcr's error.ratio is the error variance of x over that of y, so 4 here is 1 / 4 there. tests/test_s3a2_lines.py checks the direction against R deming::deming(xstd =, ystd =) too.

### `table.fit_line method="passing-bablok"`

**creatinine in plasma against serum: Passing-Bablok line** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.08800890272179 | 1.08800890272179 | relative 1e-09 | pass |
| intercept | R | -0.11717286443298 | -0.11717286443298 | relative 1e-09 | pass |
| slope 95 % CI high | R | 1.17300462437155 | 1.17300462437155 | relative 1e-09 | pass |

### `table.fit_line method="theil-sen"`

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

### `draw_smooth_line method="loess", with_confidence_band=`

**the drawn loess curve of drivers killed or seriously injured is R's** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| points | R | 200 | 200 | relative 1e-09 | pass |
| curve at the first month | R | 1644.03914048406 | 1644.03914048406 | relative 1e-09 | pass |
| curve at the last month | R | 1323.4857369989 | 1323.4857369989 | relative 1e-09 | pass |

### `table.add_smoothed_column method="loess", interval=`

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

### `table.find_survival_over_time method="life table"`

**method="life table": the actuarial life table of breast feeding (Klein & Moeschberger section 5.4)** (real data; data: bfeed (KMsurv))

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
| chi-square | R | 3.37646071064618 | 3.3538346973481 | relative 0.01 | pass |

Note: R survdiff takes no start times, so the R check is the score test of coxph(..., ties = "breslow"), the nearest R test; here it differs from the log-rank test by 0.7 % (3.354 against 3.376). The log-rank test counted out step by step in R (observed minus expected events and their hypergeometric variance at each death, with a row at risk when its start < t <= its stop) gives statsmodels' number, so statsmodels is checked to 1e-12 and R's score test to 1e-2.

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
| age | R | 0.0305363149141718 | 0.0305363149141718 | relative 1e-06 | pass |
| surgery | R | -0.773327645300477 | -0.773327645300477 | relative 1e-06 | pass |
| transplant | R | 0.0160956052965218 | 0.0160956052965218 | relative 1e-06 | pass |

Note: 36 rows start at a death time (each patient's second row starts at the transplant). R does not count such a row as at risk at that death, statsmodels PHReg(entry=) does (the patient would count twice), so simplydata fits these data with R coxph and says so.

### `table.explain_survival competing_with=`

**competing_with=: cause-specific hazard ratios of a plasma cell malignancy, death counted as the end of follow-up** (real data; data: mgus2 (survival))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| age | statsmodels PHReg | 0.0130385698370914 | 0.0130385698370916 | relative 1e-06 | pass |
| men vs women | statsmodels PHReg | -0.0251377892665885 | -0.0251377892665881 | relative 1e-06 | pass |
| age | R | 0.0130385698370914 | 0.0130385698249726 | relative 1e-06 | pass |
| men vs women | R | -0.0251377892665885 | -0.025137789294278 | relative 1e-06 | pass |

### `table.explain_survival method="fine-gray"`

**method="fine-gray": subdistribution hazard ratios of a plasma cell malignancy, death competing** (real data; data: mgus2 (survival))

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
| log estimate | Viechtbauer (2010), JSS 36(3) | -0.714532348365101 | -0.7145 | within 5e-05 (printed rounding) | pass |
| tau squared | Viechtbauer (2010), JSS 36(3) | 0.313243325980895 | 0.3132 | within 5e-05 (printed rounding) | pass |
| I squared % | Viechtbauer (2010), JSS 36(3) | 92.2213860749656 | 92.22 | within 0.005 (printed rounding) | pass |
| Q | Viechtbauer (2010), JSS 36(3) | 152.233008082373 | 152.233 | within 5e-05 (printed rounding) | pass |
| estimate | R | 0.489420936788213 | 0.489420936788213 | relative 1e-08 | pass |
| low | R | 0.330072245409142 | 0.330072245409142 | relative 1e-08 | pass |
| high | R | 0.725698257573092 | 0.725698257573092 | relative 1e-08 | pass |
| p-value | R | 0.00192001508513394 | 0.00192001508513394 | relative 1e-08 | pass |
| tau squared | R | 0.313243325980895 | 0.313243325980895 | relative 1e-08 | pass |
| I squared % | R | 92.2213860749656 | 92.2213860749656 | relative 1e-08 | pass |
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
| filled odds ratio | R | 1.19061641886529 | 1.19061641886529 | relative 1e-06 | pass |

Note: Egger's test from R meta (metabias, method "Egger"), a second package; trim and fill from metafor (estimator L0, side estimated).

### `table.combine_studies interval_by=`

**interval_by=: BCG trials, the normal (z) interval** (published; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| log low | Viechtbauer (2010), JSS 36(3) | -1.06689767574005 | -1.0669 | within 5e-05 (printed rounding) | pass |
| log high | Viechtbauer (2010), JSS 36(3) | -0.36216702099015 | -0.3622 | within 5e-05 (printed rounding) | pass |
| estimate | R | 0.489420936788213 | 0.489420936788213 | relative 1e-08 | pass |
| low | R | 0.344074293400216 | 0.344074293400216 | relative 1e-08 | pass |
| high | R | 0.69616608378248 | 0.69616608378248 | relative 1e-08 | pass |
| p-value | R | 7.05426734852055e-05 | 7.05426734852055e-05 | relative 1e-08 | pass |

### `table.combine_studies method=`

**method=: BCG trials, DerSimonian-Laird** (published; data: BCG trials (metadat))

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

**method=: BCG trials, Paule-Mandel** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 0.489206589341719 | 0.489206589341719 | relative 1e-06 | pass |
| low | R | 0.329851325671957 | 0.329851325671957 | relative 1e-06 | pass |
| high | R | 0.725548355968616 | 0.725548355968616 | relative 1e-06 | pass |
| p-value | R | 0.00191966702866362 | 0.00191966702866362 | relative 1e-06 | pass |
| tau squared | R | 0.318093711863015 | 0.318093711863015 | relative 1e-06 | pass |

Note: Paule-Mandel is found by iteration, so the numbers agree to metafor's own tolerance.

**method=: BCG trials, a common effect** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 0.650323619619482 | 0.650323619619482 | relative 1e-08 | pass |
| low | R | 0.600699026085764 | 0.600699026085764 | relative 1e-08 | pass |
| high | R | 0.704047770795957 | 0.704047770795957 | relative 1e-08 | pass |
| p-value | R | 2.28862930697324e-26 | 2.28862930697324e-26 | relative 1e-08 | pass |

### `table.combine_studies method="Mantel-Haenszel"`

**method="Mantel-Haenszel": BCG trials, risk ratios** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | statsmodels StratifiedTable (riskratio_pooled) | 0.635267185077769 | 0.635267185077769 | relative 1e-08 | pass |
| estimate | R | 0.635267185077769 | 0.635267185077769 | relative 1e-08 | pass |
| low | R | 0.588128729691417 | 0.588128729691417 | relative 1e-08 | pass |
| high | R | 0.686183782670126 | 0.686183782670126 | relative 1e-08 | pass |
| p-value | R | 8.91137967074168e-31 | 8.91137967074168e-31 | relative 1e-08 | pass |

### `table.combine_studies method="Peto"`

**method="Peto": BCG trials, odds ratios** (real data; data: BCG trials (metadat))

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
| Q between | R | 1.86144614123119 | 1.86144614123119 | relative 1e-08 | pass |
| p between | R | 0.394268523294979 | 0.39426852329498 | relative 1e-08 | pass |
| random | R | 0.378717597960143 | 0.378717597960143 | relative 1e-08 | pass |
| random tau2 | R | 0.392526549118408 | 0.392526549118408 | relative 1e-08 | pass |

Note: Each subgroup has its own between-study variance; the test of their difference uses each subgroup's estimate with its normal (z) standard error, as RevMan and R meta do (the next case checks it against meta), not metafor's rma(mods = ~ alloc), which shares one variance.

**for_each_group_in=: BCG trials by allocation, against R meta's test of subgroup differences** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Q between | R | 1.86144614123119 | 1.86144614123119 | relative 0.0001 | pass |
| p between | R | 0.394268523294979 | 0.394268523294979 | relative 0.0001 | pass |

Note: R meta (each subgroup its own between-study variance, REML) is a second package; meta's REML stops at its own tolerance, so the numbers agree to about 1e-5.

### `table.combine_studies using=`

**using=: BCG trials, meta-regression on latitude** (real data; data: BCG trials (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | -0.0291016609280148 | -0.0291016609280148 | relative 1e-08 | pass |
| low | R | -0.0471531327109005 | -0.0471531327109005 | relative 1e-08 | pass |
| p-value | R | 0.00456554558895661 | 0.00456554558895661 | relative 1e-08 | pass |

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
| estimate | R | -0.537108258566786 | -0.537108258566786 | relative 1e-08 | pass |
| low | R | -1.25032220922694 | -1.25032220922694 | relative 1e-08 | pass |
| first study | R | -0.355169640940107 | -0.355169640940107 | relative 1e-08 | pass |

Note: metafor's Hedges' g (exact correction, large-sample variance) is the reference; statsmodels' effectsize_smd uses an approximate correction and another variance, so it differs slightly.

### `table.combine_studies show="ratios of averages"`

**show="ratios of averages": Curtis 1998, the log response ratio of plant mass under raised CO2** (real data; data: Curtis 1998 (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| estimate | R | 1.28912315941624 | 1.28912315941624 | relative 1e-06 | pass |
| tau squared | R | 0.0257714790311439 | 0.0257714790311439 | relative 1e-06 | pass |

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
| estimate | R | 0.233032270431239 | 0.233032270431239 | relative 1e-08 | pass |
| low | R | 0.199562768428072 | 0.199562768428072 | relative 1e-08 | pass |

### `draw_funnel_plot`

**passive smoking: each study's odds ratio and standard error** (real data; data: passive smoking (metadat))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first odds ratio | R | 1.18 | 1.18 | relative 1e-08 | pass |
| first standard error | R | 0.137028776120449 | 0.137028776120449 | relative 1e-08 | pass |
| last standard error | R | 0.257719821942313 | 0.257719821942313 | relative 1e-08 | pass |

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

### `table.add_log_ratio_columns method="alr"`

**method="alr": mite, every species over the first one** (real data; data: mite (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| alr row 1 second | R | -1.22377543162212 | -1.22377543162212 | relative 1e-09 | pass |
| alr row 5 last | R | -1.58699631979019 | -1.58699631979019 | relative 1e-09 | pass |

### `table.add_log_ratio_columns method="ilr"`

**method="ilr": mite, isometric log ratios** (real data; data: mite (vegan))

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

### `table.explain_profiles_of method="canonical correspondence"`

**method="canonical correspondence": varespec, CCA with Al, P and K** (real data; data: varespec and varechem (vegan))

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

### `table.find_correlation_between_profiles method="procrustes"`

**method="procrustes": varespec and varechem** (real data; data: varespec and varechem (vegan))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Procrustes correlation | R | 0.616575031599296 | 0.616575031599296 | relative 1e-09 | pass |
| p | R | 0.001 | 0.001 | relative 1e-09 | pass |

### `table.compare_profiles_of method="anosim"`

**method="anosim": dune by management** (real data; data: dune (vegan))

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
| LD1 % of trace | R | 68.6 | 68.6 | relative 0.004 | pass |
| LD2 % of trace | R | 29.9 | 30 | relative 0.004 | pass |
| leave-one-out % correct | R | 95 | 95 | relative 0.004 | pass |
| LD1 row 1 size | R | 1.53886934430206 | 1.53886934430206 | relative 0.004 | pass |

Note: The shares are read from the printout (one decimal; within one unit of the last printed digit, as simplydata reads MASS's own four-decimal print); R's side computes MASS's proportion of trace (svd squared over their sum, as print.lda does) rounded the same way. The design check found 0.686, 0.300 and 0.014, and 95 % correct.

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
| `table.fit_dose_response` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_dose_response` | R + Python | polars | result | relative 1e-09 | pass |
| `fit_dose_response` | R + matplotlib | pandas | chart | relative 1e-06 | pass |
| `table.find_best_power_of` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.find_best_power_of` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line method="theil-sen"` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.fit_line method="theil-sen"` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line method="standardised major axis"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line method="standardised major axis"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line method="deming", y_error_over_x_error=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line method="deming", y_error_over_x_error=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line method="passing-bablok"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line method="passing-bablok"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line with_bends=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line with_bends=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line changes_at=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.fit_line changes_at=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.fit_curve of_kind="logistic growth"` | SciPy | pandas | result | relative 1e-05 | pass |
| `table.fit_curve of_kind="logistic growth"` | SciPy | polars | result | relative 1e-05 | pass |
| `table.explain for_percentile=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain for_percentile=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain changes_at=` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain changes_at=` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.add_smoothed_column method="loess", interval=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.add_smoothed_column method="loess", interval=` | R + Python | polars | result | relative 1e-09 | pass |
| `draw_smooth_line method="loess", with_confidence_band=` | R + matplotlib | pandas | chart | relative 1e-09 | pass |
| `table.find_columns_that_predict` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_columns_that_predict` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_group_levels_of` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_group_levels_of` | R + Python | polars | result | relative 1e-06 | pass |
| `draw_interaction_lines` | seaborn | pandas | chart | relative 1e-09 | pass |
| `table.explain spread_changes_with=` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.explain spread_changes_with=` | R + Python | polars | result | relative 1e-05 | pass |
| `table.explain neighbours_alike_in_order_of=` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.explain neighbours_alike_in_order_of=` | R + Python | polars | result | relative 1e-05 | pass |
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
| `table.find_survival_over_time method="life table"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_survival_over_time method="life table"` | R + Python | polars | result | relative 1e-09 | pass |
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
| `table.explain_survival method="fine-gray"` | R + Python | pandas | result | relative 1e-07 | pass |
| `table.explain_survival method="fine-gray"` | R + Python | polars | result | relative 1e-07 | pass |
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
| `table.combine_studies method=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies method=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies method="Mantel-Haenszel"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies method="Mantel-Haenszel"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies method="Peto"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies method="Peto"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies interval_by=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies interval_by=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies for_each_group_in=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies for_each_group_in=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.combine_studies using=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.combine_studies using=` | R + Python | polars | result | relative 1e-09 | pass |
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
| `table.add_log_ratio_columns method="alr"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns method="alr"` | R + Python | polars | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns method="ilr"` | R + Python | pandas | table | relative 1e-09 | pass |
| `table.add_log_ratio_columns method="ilr"` | R + Python | polars | table | relative 1e-09 | pass |
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
| `table.explain_profiles_of method="canonical correspondence"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain_profiles_of method="canonical correspondence"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain_profiles_of allowing_for=` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain_profiles_of allowing_for=` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles method="procrustes"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_correlation_between_profiles method="procrustes"` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_profiles_of method="anosim"` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_profiles_of method="anosim"` | R + Python | polars | result | relative 1e-09 | pass |
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
- `table.fit_dose_response` (1): the 4 parameter log-logistic curve, the usual one in ecotoxicology (drc's LL.4); of_kind= chooses another.
- `table.fit_dose_response` (2): the ED50 with its delta-method interval: drc's ED() gives no interval unless asked (interval = "none" is its default).
- `fit_dose_response` (1): the 4 parameter log-logistic curve (drc's LL.4), as table.fit_dose_response.
- `fit_dose_response` (2): the curve is drawn over 300 doses spaced evenly on a log scale (and dose 0), so it stays smooth on a log dose axis too; the ED50 and its delta-method interval go in the legend.
- `table.find_best_power_of` (1): the power's 95 % interval from the profile likelihood (alpha=0.05); without alpha= SciPy gives no interval.
- `table.fit_line method="theil-sen"` (1): SciPy's alpha= is the confidence level (0.95), not the error rate.
- `table.fit_line method="theil-sen"` (2): the intercept is median(y) - slope * median(x) (Conover; SciPy's default); R mblm takes the median of y - slope * x instead.
- `table.fit_line method="standardised major axis"` (1): smatr's own 95 % intervals (Warton et al. 2006); method="major axis" is method = "MA".
- `table.fit_line method="deming", y_error_over_x_error=` (1): mcr's error.ratio is the error variance of x over that of y, the other way round from y_error_over_x_error=, so it gets 1 / 4.
- `table.fit_line method="deming", y_error_over_x_error=` (2): mcr's analytical intervals; its default (bootstrap) is random and differs from run to run.
- `table.fit_line method="passing-bablok"` (1): Passing and Bablok's own rank-based intervals (mcr's "analytical" for PaBa); mcr's default bootstrap is random.
- `table.fit_line with_bends=` (1): a continuous line: it bends, it does not jump (segmented's model); seed 1 fixes segmented's random restarts.
- `table.fit_line with_bends=` (2): Davies' test of "no bend at all": the bend's own p-value is not valid, because the data chose where it is.
- `table.fit_line changes_at=` (1): the change starts at the point itself: rows at 10 or later count as after.
- `table.fit_curve of_kind="logistic growth"` (1): start values: simplydata takes them from R's self-starting model (stats::getInitial()), or searches the whole range without R; the least-squares answer is the same.
- `table.explain for_percentile=` (1): R quantreg's exact simplex (Barrodale-Roberts); statsmodels QuantReg gives the same line to about 1e-7 but none of R's standard errors.
- `table.explain for_percentile=` (2): standard errors by "nid" for every number of rows (R's default below 1001 rows is "rank", intervals only).
- `table.explain changes_at=` (1): the change starts at the point itself: rows at 10 or later count as after.
- `table.add_smoothed_column method="loess", interval=` (1): R loess's own defaults: span 0.75 (smoothness=), local curves of degree 2, no robustness steps.
- `table.add_smoothed_column method="loess", interval=` (2): the band uses loess's own degrees of freedom, as R's predict.loess intervals do.
- `draw_smooth_line method="loess", with_confidence_band=` (1): R loess's own defaults: span 0.75, local curves of degree 2, no robustness steps (not lowess).
- `table.find_columns_that_predict` (1): the random split into 10 parts is made in R itself (with_seed=1 is set.seed(1)), so R's own random numbers give the same parts.
- `table.find_columns_that_predict` (2): the lasso (alpha = 1) with 10 parts; method="elastic net" is alpha = 0.5.
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
- `table.find_survival_over_time method="life table"` (1): the intervals start at the times given, and the last one is open (NA).
- `table.find_survival_over_time method="life table"` (2): simplydata counts the rows lost and with the event in each interval; lifetab does the rest, with the actuarial assumption (lost rows count as followed for half the interval).
- `table.find_survival_over_time allowing_for=` (1): direct adjustment: each row's curve is predicted as if in each group and averaged over all rows, never the curve of an "average" row; conf_int = TRUE (adjustedCurves' own default is FALSE).
- `table.find_survival_over_time followed_from=` (1): each row is at risk only after its start (left truncation, R Surv(start, stop, event)).
- `table.find_survival_over_time average_time_up_to=` (1): rmean = 700, the horizon you name: without it survival's print uses its own upper limit.
- `table.compare_survival allowing_for=` (1): strata=: the groups are compared within each stratum and the results added up, as R survdiff(... + strata()).
- `table.compare_survival followed_from=` (1): entry=: each row counts as at risk only after its start. R survdiff takes no start times; the nearest R check, the score test of coxph(Surv(start, stop, event) ~ group, ties = "breslow"), agrees closely but not always exactly (validation/report.md).
- `table.compare_survival average_time_up_to=` (1): arm 1 is the second group in sorted order, so the difference is the second minus the first.
- `table.compare_survival average_time_up_to=` (2): tau = 700, the horizon you name: survRM2's own default is the shortest of the groups' last times.
- `table.compare_survival competing_with=` (1): the event asked about is code 1 and the competing event code 2; other values are censored (code 0).
- `table.compare_survival competing_with=` (2): Gray's test of the chance of each event over time (cmprsk::cuminc), not a log-rank test with the competing event censored.
- `table.explain_survival allowing_for=` (1): strata=: each treatment group has its own baseline risk (R coxph(... + strata(treatment))), so there is no hazard ratio for it.
- `table.explain_survival followed_from=` (1): entry=: each row is at risk only after its start (R coxph(Surv(start, stop, event) ~ ...)). statsmodels counts a row as at risk at an event time equal to its start and R does not, so when a row starts at an event time (one person split into rows) simplydata fits the model with R coxph, and says so.
- `table.explain_survival competing_with=` (1): cause-specific: a Cox model of the event asked about, with the competing event counted as the end of follow-up (the risk at any moment among those still free of both events).
- `table.explain_survival method="fine-gray"` (1): Fine and Gray's model with crr's robust (sandwich) standard errors; failcode is the event asked about.
- `table.explain_survival distribution=` (1): the accelerated failure time model of survreg: time ratios exp(coefficient), never hazard ratios.
- `draw_survival_curves followed_from=` (1): entry=: each row is at risk only after its start (delayed entry).
- `draw_survival_curves allowing_for=` (1): direct adjustment: each row's curve predicted in each group, then averaged over all rows.
- `draw_risk_curves competing_with=` (1): the competing event is a state of its own (Aalen-Johansen), never counted as censored.
- `table.combine_studies` (1): risk ratios for counts, and a study with no events in either group left out (drop00 = TRUE), as Cochrane reviews do; show= chooses odds ratios or risk differences.
- `table.combine_studies` (2): random effects with REML, metafor's default and the best of the usual estimators of the between-study spread (Veroniki et al. 2016).
- `table.combine_studies` (3): Hartung-Knapp intervals and p-values with the ad hoc rule: never narrower than the normal (z) interval; interval_by="normal" gives the classic interval.
- `table.combine_studies` (4): the result shown back as a ratio, with the prediction interval (t with k - 1 degrees of freedom under Hartung-Knapp).
- `draw_funnel_plot` (1): the pseudo 95 % limits: SciPy's 95 % interval around the combined effect at the largest standard error (lognorm for ratios, so on the log scale); with the top of the funnel at the combined effect both limits are straight lines, as metafor funnel() draws them.
- `draw_funnel_plot` (2): the line is the combined effect of combine_studies (random effects, REML).
- `draw_funnel_plot` (3): ratios on a log scale, with the standard error of the log ratio downwards (0 at the top).
- `table.combine_studies estimates=` (1): a column with "ratio" in its name is combined on the log scale; metafor conv.wald() turns each estimate and its 95 % interval into a log ratio and its variance (estimates_are_ratios= decides otherwise).
- `table.combine_studies estimates=` (2): the combined effect shown back as a ratio.
- `table.combine_studies method=` (1): DerSimonian-Laird's between-study spread (metafor "DL"); "Paule-Mandel" is "PM" and "common effect" is "EE" (metafor 4 renamed "FE").
- `table.combine_studies method="Mantel-Haenszel"` (1): Mantel-Haenszel weights, a common-effect method: there is no between-study spread and no prediction interval (compare_risks(allowing_for=) gives the same from raw rows).
- `table.combine_studies method="Peto"` (1): Peto's one-step odds ratio, a common-effect method for rare events; it gives odds ratios only.
- `table.combine_studies interval_by=` (1): the normal (z) interval and p-value, as in older meta-analyses; the default is Hartung-Knapp (test = "adhoc").
- `table.combine_studies for_each_group_in=` (1): each subgroup its own random-effects model, with its own between-study spread; for this test each subgroup's estimate with its normal (z) standard error, as RevMan and R meta do (the subgroups' own intervals stay Hartung-Knapp).
- `table.combine_studies for_each_group_in=` (2): the test of the difference between the subgroup estimates (a common-effect meta-regression on the subgroup), not metafor's rma(mods = ~ group), which assumes one spread for all.
- `table.combine_studies using=` (1): a meta-regression: the slope of the log risk ratio per unit of each column, with Hartung-Knapp intervals; R-squared says how much of the between-study spread the columns account for.
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
- `table.add_log_ratio_columns method="alr"` (1): the reference is the column named in against= ("sul1", the 5th), R compositions::alr(ivar =).
- `table.add_log_ratio_columns method="ilr"` (1): the default basis of R compositions::ilr(); another basis (scikit-bio's) gives other numbers but the same distances between rows, and the printout says so.
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
- `table.explain_profiles_of method="canonical correspondence"` (1): CCA on the counts themselves (chi-square distances), so no measure=.
- `table.explain_profiles_of method="canonical correspondence"` (2): CCA's adjusted R squared comes from permutations (vegan), after set.seed.
- `table.explain_profiles_of allowing_for=` (1): a partial analysis: site is taken into account first (vegan Condition()) and not tested, the same meaning allowing_for= has on the other words.
- `table.find_correlation_between_profiles` (1): measurements (not counts) in second= get straight-line distances after each column is put on the same scale; counts would get measure=.
- `table.find_correlation_between_profiles` (2): the Pearson Mantel correlation with 999 permutations after set.seed(1).
- `table.find_correlation_between_profiles method="procrustes"` (1): PROTEST on the first two principal coordinates of each set: the Procrustes correlation and its permutation p-value.
- `table.compare_profiles_of method="anosim"` (1): Clarke's ANOSIM R from ranked distances, 999 permutations after set.seed(1).
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
| [ryegrass (drc)](https://doi.org/10.1371/journal.pone.0146021) | root length of perennial ryegrass at 7 concentrations of ferulic acid (24 rows) | Inderjit, Streibig, J. C. & Olofsdotter, M. (2002). Joint action of phenolic acid mixtures and its significance in allelopathy research. Physiologia Plantarum 114, 422-428. Analysed in Ritz, C., Baty, F., Streibig, J. C. & Gerhard, D. (2015). Dose-response analysis using R. PLoS ONE 10, e0146021. Shipped with the R package drc. | The article (Ritz et al. 2015) is CC BY 4.0; the data are shipped with drc (GPL-2 or later). Not stored here: read from the installed drc package, so it needs R. |
| [Bliss beetles](https://doi.org/10.1111/j.1744-7348.1935.tb07713.x) | flour beetles killed after five hours of carbon disulphide at 8 doses (log10 mg per litre) | Bliss, C. I. (1935). The calculation of the dosage-mortality curve. Annals of Applied Biology 22, 134-167. Logistic fit printed in Dobson, A. J. & Barnett, A. G. (2008). An Introduction to Generalized Linear Models, 3rd ed., section 7.3. | Facts published in 1935 (24 numbers), typed from the paper; not covered by copyright. |
| [poisons (boot)](https://doi.org/10.1111/j.2517-6161.1964.tb00553.x) | survival times of 48 animals: 3 poisons x 4 treatments, 4 animals each | Box, G. E. P. & Cox, D. R. (1964). An analysis of transformations. Journal of the Royal Statistical Society B 26, 211-252 (Table 1; the power found is about -0.75, the reciprocal suggested). Shipped with the R package boot. | Facts published in 1964; the copy in boot is GPL (Unlimited). Not stored here: read from boot, so it needs R. |
| [NIST Rat42](https://www.itl.nist.gov/div898/strd/nls/data/ratkowsky2.shtml) | pasture yield against growing time (9 points); certified 3 parameter logistic fit (NIST StRD, higher difficulty) | Ratkowsky, D. A. (1983). Nonlinear Regression Modeling. New York: Marcel Dekker, pp. 61 and 88. In: NIST StRD, Nonlinear Regression, dataset Rat42. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST Misra1a](https://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml) | monomolecular absorption (14 points); certified fit of y = b1 (1 - exp(-b2 x)) (NIST StRD, lower difficulty) | Misra, D., NIST (1978). Dental research monomolecular adsorption study. In: NIST StRD, Nonlinear Regression, dataset Misra1a. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [NIST BoxBOD](https://www.itl.nist.gov/div898/strd/nls/data/boxbod.shtml) | biochemical oxygen demand against incubation time (6 points); certified fit of y = b1 (1 - exp(-b2 x)) (NIST StRD, higher difficulty) | Box, G. P., Hunter, W. G. & Hunter, J. S. (1978). Statistics for Experimenters. New York: Wiley, pp. 483-487. In: NIST StRD, Nonlinear Regression, dataset BoxBOD. | Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged. |
| [Puromycin (treated)](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/Puromycin.html) | reaction velocity against substrate concentration for the enzyme treated with Puromycin (12 rows) | Treloar, M. A. (1974). Effects of Puromycin on galactosyltransferase in Golgi membranes. M.Sc. thesis, University of Toronto. Fit printed in Bates, D. M. & Watts, D. G. (1988). Nonlinear Regression Analysis and Its Applications. New York: Wiley, section 2.3 (Vm 212.7, K 0.06412). Copy from R's datasets package (Puromycin). | Published facts; the copy in R's datasets package is GPL-2 \| GPL-3. |
| [leaflife (smatr)](https://cran.r-project.org/package=smatr) | leaf mass per area and leaf lifespan of 67 plant species at four sites (log10 of both) | Wright, I. J., Westoby, M. & Reich, P. B. (2002). Convergence towards higher leaf mass per area in dry and nutrient-poor habitats has different consequences for leaf life span. Journal of Ecology 90, 534-543. Used in Warton, D. I. et al. (2006). Bivariate line-fitting methods for allometry. Biological Reviews 81, 259-291. Shipped with the R package smatr. | GPL-2 (smatr). Not stored here: read from smatr, so it needs R. |
| [creatinine (mcr)](https://cran.r-project.org/package=mcr) | creatinine measured in serum and in plasma of the same samples (108 complete pairs) | Shipped with the R package mcr (Manuilova, E., Schuetzenmeister, A. & Model, F., Roche Diagnostics), the package's method-comparison example. | GPL-3 (mcr). Not stored here: read from mcr, so it needs R. |
| [stagnant (segmented)](https://doi.org/10.1093/biomet/58.3.525) | log band height against log flow rate of water over a stagnant band (28 points) | Bacon, D. W. & Watts, D. G. (1971). Estimating the transition between two intersecting straight lines. Biometrika 58, 525-534. Shipped with the R package segmented. | Facts published in 1971; the copy in segmented is GPL. Not stored here: read from segmented, so it needs R. |
| [Seatbelts](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/UKDriverDeaths.html) | drivers killed or seriously injured in Great Britain each month, 1969-1984; the seat-belt law from February 1983 (month 170) | Harvey, A. C. & Durbin, J. (1986). The effects of seat belt legislation on British road casualties: a case study in structural time series modelling. Journal of the Royal Statistical Society A 149, 187-227. Copy from R's datasets package (Seatbelts). | Official UK road casualty counts published in the paper; the copy in R's datasets package is GPL-2 \| GPL-3. |
| [Engel food expenditure](https://www.statsmodels.org/stable/datasets/generated/engel.html) | household income and food expenditure of 235 Belgian working-class households (1857) | Engel, E. (1857). Die Productions- und Consumptionsverhaeltnisse des Koenigreichs Sachsen. Analysed with quantile regression in Koenker, R. & Bassett, G. (1982). Robust tests for heteroscedasticity based on regression quantiles. Econometrica 50, 43-61. Copy in statsmodels (statsmodels.datasets.engel). | Public domain (published 1857). Not stored here: read from statsmodels. |
| [Dialyzer (nlme)](https://cran.r-project.org/package=nlme) | ultrafiltration rate of 20 high-flux haemodialyzers at 7 transmembrane pressures, at two blood flow rates (140 rows) | Vonesh, E. F. & Carter, R. L. (1992). Mixed-effects nonlinear regression for unbalanced repeated measures. Biometrics 48, 1-17. Analysed with variance functions in Pinheiro, J. C. & Bates, D. M. (2000). Mixed-Effects Models in S and S-PLUS. Springer, section 5.2. Shipped with the R package nlme. | GPL (nlme). Not stored here: read from nlme, so it needs R. |
| [Lake Huron](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/LakeHuron.html) | annual level of Lake Huron in feet, 1875-1972 | Brockwell, P. J. & Davis, R. A. (1991). Time Series and Forecasting Methods, 2nd ed. Springer, pp. 328-329 (from the US Army Corps of Engineers). Copy from R's datasets package (LakeHuron). | US Government measurements (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. |
| [swiss](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/swiss.html) | fertility and five social measures of 47 French-speaking provinces of Switzerland in about 1888 | Mosteller, F. & Tukey, J. W. (1977). Data Analysis and Regression. Addison-Wesley, pp. 549-551 (from the Office of Population Research, Princeton, 1976). Copy from R's datasets package (swiss). | Official 1888 statistics (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. |
| [birthwt (MASS)](https://cran.r-project.org/package=MASS) | 189 births at Baystate Medical Center, Springfield, Massachusetts (1986): low birth weight, the mother's age, weight and smoking | Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Shipped with the R package MASS (Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed.). | GPL-2 \| GPL-3 (MASS). Not stored here: read from MASS, so it needs R. |
| [warpbreaks](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/warpbreaks.html) | the number of warp breaks per loom for two wools (A, B) at three tensions (L, M, H), 9 looms each | Tippett, L. H. C. (1950). Technological Applications of Statistics. Wiley, p. 106. Copy from R's datasets package (warpbreaks). | Published 1950 (facts). The copy in R's datasets package is GPL-2 \| GPL-3. |
| [sleepstudy (lme4)](https://doi.org/10.18637/jss.v067.i01) | average reaction time of 18 truck drivers on each of 10 days of sleep deprivation (180 rows) | Belenky, G. et al. (2003). Patterns of performance degradation and restoration during sleep restriction and subsequent recovery. Journal of Sleep Research 12, 1-12. Analysed in Bates, D., Maechler, M., Bolker, B. & Walker, S. (2015). Fitting linear mixed-effects models using lme4. Journal of Statistical Software 67(1) (CC BY). Shipped with the R package lme4. | GPL (>= 2) (lme4). Not stored here: read from lme4, so it needs R. |
| [rat liver glycogen](https://www.worldcat.org/title/biometry/oclc/7203719) | glycogen in the livers of 6 rats, 2 on each of 3 treatments (control, glucose, glucose and fructose), 3 preparations per liver and 2 readings per preparation (36 rows) | Sokal, R. R. & Rohlf, F. J. (1981). Biometry, 2nd ed. Freeman, Box 10.1 (nested ANOVA: treatments SS 1557.56 on 2 df, rats within treatments SS 797.67 on 3 df, F = 2.929); the same analysis in Crawley, M. J. (2007). The R Book. Wiley, chapter 11. | Facts published in the book (36 numbers), typed from it; not covered by copyright. |
| [iris](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/iris.html) | sepal and petal length and width of 50 flowers of each of three iris species | Anderson, E. (1935). The irises of the Gaspe Peninsula. Bulletin of the American Iris Society 59, 2-5; Fisher, R. A. (1936). The use of multiple measurements in taxonomic problems. Annals of Eugenics 7, 179-188. Copy from R's datasets package (iris). | Published 1935 (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. |
| [udca (survival)](https://cran.r-project.org/package=survival) | 170 patients with primary biliary cirrhosis in a trial of ursodeoxycholic acid: dates of entry, last follow-up and death | Lindor, K. D. et al. (1994). Ursodeoxycholic acid in the treatment of primary biliary cirrhosis. Gastroenterology 106, 1284-1290. Shipped with R's survival package (udca). | LGPL (>= 2) (survival). Not stored here: read from survival, so it needs R. |
| [mgus2 (survival)](https://cran.r-project.org/package=survival) | 1384 patients with monoclonal gammopathy: months to progression to a plasma cell malignancy (pcm) or death without it | Kyle, R. A. et al. (2002). A long-term study of prognosis in monoclonal gammopathy of undetermined significance. New England Journal of Medicine 346, 564-569; the competing-risks example of Therneau, T. M., "Multi-state models and competing risks" (survival vignette). Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published data in an LGPL package; stored with the first event of each patient (outcome pcm, death or censored, as the vignette builds it). |
| [lung (survival)](https://cran.r-project.org/package=survival) | 228 patients with advanced lung cancer (NCCTG): days to death or the end of follow-up, age, sex and ECOG performance score | Loprinzi, C. L. et al. (1994). Prospective evaluation of prognostic variables from patient-completed questionnaires. Journal of Clinical Oncology 12, 601-607. Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published trial data in an LGPL package; stored with its numbers unchanged (status recoded to died yes/no, sex to male/female). |
| [bfeed (KMsurv)](https://cran.r-project.org/package=KMsurv) | 927 first-born children of the National Longitudinal Survey of Youth: weeks of breast feeding and whether it was ended | Klein, J. P. & Moeschberger, M. L. (2003). Survival Analysis: Techniques for Censored and Truncated Data, 2nd ed. Springer, section 1.14 and the life table of section 5.4. Shipped with the R package KMsurv. | GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R. |
| [Channing House (KMsurv)](https://cran.r-project.org/package=KMsurv) | residents of Channing House, a retirement centre in Palo Alto: age (months) on entry and at death or the end of the study (the 4 rows that left on the day they came are left out) | Hyde, J. (1980). Testing survival with incomplete observations. In Biostatistics Casebook, Wiley; Klein & Moeschberger (2003), section 4.6 (delayed entry). Shipped with the R package KMsurv. | GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R. |
| [veteran (survival)](https://cran.r-project.org/package=survival) | 137 men in the Veterans' Administration lung cancer trial: standard or test chemotherapy, cell type, Karnofsky score, days to death | Kalbfleisch, J. D. & Prentice, R. L. (2002). The Statistical Analysis of Failure Time Data, 2nd ed. Wiley. Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published trial data in an LGPL package; stored (treatment 1/2 written as standard/test). |
| [Stanford heart transplant (survival)](https://cran.r-project.org/package=survival) | 103 patients waiting for a heart transplant, as start-stop rows (one row before and one after a transplant): age, earlier surgery, transplant | Crowley, J. & Hu, M. (1977). Covariance analysis of heart transplant survival data. Journal of the American Statistical Association 72, 27-36; analysed in Therneau, T. M. & Grambsch, P. M. (2000). Modeling Survival Data. Springer, section 3.7. Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2). | Published data in an LGPL package; stored with its numbers unchanged. |
| [larynx (KMsurv)](https://cran.r-project.org/package=KMsurv) | 90 men with cancer of the larynx: stage, age, months to death | Kardaun, O. (1983). Statistical survival analysis of male larynx-cancer patients: a case study. Statistica Neerlandica 37, 103-125; Klein & Moeschberger (2003), chapter 12 (parametric models). Shipped with the R package KMsurv. | GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R. |
| [BCG trials (metadat)](https://doi.org/10.18637/jss.v036.i03) | 13 trials of the BCG vaccine against tuberculosis: cases among the vaccinated and the unvaccinated, the absolute latitude of the place and how people were put into the groups | Colditz, G. A. et al. (1994). Efficacy of BCG vaccine in the prevention of tuberculosis: meta-analysis of the published literature. JAMA 271, 698-702. Analysed in Viechtbauer, W. (2010). Conducting meta-analyses in R with the metafor package. Journal of Statistical Software 36(3), 1-48 (CC BY 3.0). Shipped with the R package metadat (dat.bcg); a copy is the practice table bcg. | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [passive smoking (metadat)](https://doi.org/10.1136/bmj.315.7114.980) | 37 studies of lung cancer in non-smoking women whose husbands smoked: the odds ratio of each study with its 95 % interval | Hackshaw, A. K., Law, M. R. & Wald, N. J. (1997). The accumulated evidence on lung cancer and environmental tobacco smoke. BMJ 315, 980-988 (pooled excess risk 24 %, 95 % CI 13 % to 36 %). Shipped with the R package metadat (dat.hackshaw1998); a copy is the practice table passive_smoking. | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [Normand 1999 (metadat)](https://cran.r-project.org/package=metadat) | 9 trials of specialist stroke rehabilitation: average length of hospital stay (days), its standard deviation and the patients in each group | Normand, S.-L. T. (1999). Meta-analysis: formulating, evaluating, combining, and reporting. Statistics in Medicine 18, 321-359. Shipped with the R package metadat (dat.normand1999). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [Curtis 1998 (metadat)](https://cran.r-project.org/package=metadat) | 102 experiments on the growth of woody plants under raised and ambient CO2: average biomass, its standard deviation and the plants in each group | Curtis, P. S. & Wang, X. (1998). A meta-analysis of elevated CO2 effects on woody plant mass, form, and physiology. Oecologia 113, 299-313; the log response ratio of Hedges, L. V., Gurevitch, J. & Curtis, P. S. (1999). Ecology 80, 1150-1156. Shipped with the R package metadat (dat.curtis1998). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [Hart 1999 (metadat)](https://cran.r-project.org/package=metadat) | 6 trials of warfarin against placebo in atrial fibrillation: strokes and patient-years in each group | Hart, R. G., Benavente, O., McBride, R. & Pearce, L. A. (1999). Antithrombotic therapy to prevent stroke in patients with atrial fibrillation: a meta-analysis. Annals of Internal Medicine 131, 492-501. Shipped with the R package metadat (dat.hart1999). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [McDaniel 1994 (metadat)](https://cran.r-project.org/package=metadat) | 160 studies of the correlation between employment interview ratings and job performance, with the number of people in each | McDaniel, M. A., Whetzel, D. L., Schmidt, F. L. & Maurer, S. D. (1994). The validity of employment interviews: a comprehensive review and meta-analysis. Journal of Applied Psychology 79, 599-616. Shipped with the R package metadat (dat.mcdaniel1994). | The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat (installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same published numbers. |
| [BCI (vegan)](https://doi.org/10.1126/science.1066854) | Trees counted in 50 one-hectare plots of the Barro Colorado Island forest plot, Panama: 225 species | Condit, R. et al. (2002). Beta-diversity in tropical forest trees. Science 295, 666-669. Shipped with the R package vegan (BCI). | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [mite (vegan)](https://doi.org/10.1007/BF00714196) | Oribatid mites counted in 70 soil cores of a peat bog: 35 species (whole counts with many zeros), and the microtopography of each core (Topo: blanket or hummock) | Borcard, D. & Legendre, P. (1994). Environmental control and spatial structure in ecological communities: an example using oribatid mites (Acari, Oribatei). Environmental and Ecological Statistics 1, 37-61. Shipped with the R package vegan (mite, mite.env). | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [dune (vegan)](https://cran.r-project.org/package=vegan) | 20 meadow plots in the Netherlands: the cover of 30 plant species, and how each meadow was managed (Management) and the thickness of the soil's A1 horizon | Jongman, R. H., ter Braak, C. J. F. & van Tongeren, O. F. R. (1987, 1995). Data Analysis in Community and Landscape Ecology. Pudoc / Cambridge University Press. Shipped with the R package vegan (dune, dune.env). | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [varespec and varechem (vegan)](https://doi.org/10.2307/3236351) | 24 lichen pastures in Finnish Lapland: the cover of 44 plant and lichen species and 14 soil measurements (N, P, K ...) | Väre, H., Ohtonen, R. & Oksanen, J. (1995). Effects of reindeer grazing on understorey vegetation in dry Pinus sylvestris forests. Journal of Vegetation Science 6, 523-530. Shipped with the R package vegan (varespec, varechem); analysed in Oksanen, J. (2015). Multivariate analysis of ecological communities in R: vegan tutorial. | Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R. |
| [crabs (MASS)](https://doi.org/10.1071/ZO9740417) | 200 Leptograpsus crabs from Western Australia: five shell measurements, two colour forms and both sexes (four groups of 50) | Campbell, N. A. & Mahon, R. J. (1974). A multivariate study of variation in two species of rock crab of genus Leptograpsus. Australian Journal of Zoology 22, 417-425; Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed., section 12.1. Shipped with the R package MASS. | GPL-2 \| GPL-3 (MASS, which comes with R); read from the installed package, so it needs R. |
| [wg93 (ca)](https://doi.org/10.18637/jss.v020.i03) | 871 answers of the 1993 International Social Survey Programme (West Germany) to four questions on science and the environment (A to D, answers 1 to 5) | Greenacre, M. (2007). Correspondence Analysis in Practice, 2nd ed. Chapman & Hall/CRC; Nenadić, O. & Greenacre, M. (2007). Correspondence analysis in R, with two- and three-dimensional graphics: the ca package. Journal of Statistical Software 20(3) (CC BY). Shipped with the R package ca (wg93). | GPL (>= 2) (ca); read from the installed package, so it needs R. |
