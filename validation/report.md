# simplydata reliability report

Made by `python validation/make_report.py` on 2026-11-20. Generated: do not edit by hand.

Each simplydata word is run on real, published data and compared with the published answer, with the package simplydata uses underneath called directly, and with R. Each "same underneath" box of the manual is run next to its word and compared too. How it works, and the datasets with their licences: [validation/README.md](README.md).

**242 checks passed, 0 failed, 0 skipped** (skipped: R or an R package is not installed on this computer).

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

**leaf lifespan against leaf mass per area: standardised major axis (log10)** (real data; data: leaflife (smatr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.31503061916202 | 1.31503061916202 | relative 1e-09 | pass |
| intercept | R | -2.69880047584921 | -2.69880047584921 | relative 1e-09 | pass |
| slope 95 % CI low | R | 1.09626126001275 | 1.09626126001275 | relative 1e-09 | pass |

Note: Warton et al. (2006) fit these data on log scales; the slope is about 1.3.

**creatinine in plasma against serum: Deming line with y_error_over_x_error=4** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.01786319565374 | 1.01786319565374 | relative 1e-09 | pass |
| slope standard error | R | 0.0341143809499105 | 0.0341143809499105 | relative 1e-09 | pass |

Note: mcr's error.ratio is the error variance of x over that of y, so 4 here is 1 / 4 there. tests/test_s3a2_lines.py checks the direction against R deming::deming(xstd =, ystd =) too.

**creatinine in plasma against serum: Passing-Bablok line** (real data; data: creatinine (mcr))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 1.08800890272179 | 1.08800890272179 | relative 1e-09 | pass |
| intercept | R | -0.11717286443298 | -0.11717286443298 | relative 1e-09 | pass |
| slope 95 % CI high | R | 1.17300462437155 | 1.17300462437155 | relative 1e-09 | pass |

**Anscombe's set 3 (one outlier): the Theil-Sen line** (real data; data: Anscombe's quartet)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | SciPy stats.theilslopes | 0.345555555555556 | 0.345555555555556 | relative 1e-12 | pass |
| intercept | SciPy stats.theilslopes | 4 | 4 | relative 1e-12 | pass |
| slope 95 % CI low | SciPy stats.theilslopes | 0.345 | 0.345 | relative 1e-12 | pass |
| slope | R | 0.345555555555556 | 0.345555555555556 | relative 1e-09 | pass |

Note: The outlier pulls the least-squares slope to 0.500; the Theil-Sen slope stays near 0.345, the slope of the other ten points.

**Bacon and Watts's stagnant band: a line with one bend** (real data; data: stagnant (segmented))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| bend 1 | R | 0.0411057840039521 | 0.0411057840039521 | relative 1e-09 | pass |
| slope 1 | R | -0.422076814237938 | -0.422076814237938 | relative 1e-09 | pass |
| slope 2 | R | -1.02056754477954 | -1.02056754477954 | relative 1e-09 | pass |
| Davies p-value | R | 1.29088012334937e-17 | 1.29088012334937e-17 | relative 1e-09 | pass |

Note: Bacon and Watts fit a smooth transition; segmented fits the sharp bend, so R is the reference.

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

### `table.find_best_power_of`

**Box and Cox's poisons: the power for the two-way model** (published; data: poisons (boot))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | Box & Cox (1964) | -0.750162301479962 | -0.75 | within 0.01 (printed rounding) | pass |
| simple power | Box & Cox (1964) | -1 | -1 | within 0 (printed rounding) | pass |
| power | R | -0.750162301479962 | -0.750162301479962 | relative 1e-06 | pass |
| 95 % CI low | R | -1.13693054540593 | -1.13693054540593 | relative 1e-06 | pass |
| simple power | R | -1 | -1 | relative 1e-06 | pass |

Note: Box and Cox print a power of about -0.75 and suggest the reciprocal (power -1), the rate of dying.

**the power of the poisons survival times on their own** (real data; data: poisons (boot))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| power | SciPy stats.boxcox(alpha=0.05) | -0.360158452952329 | -0.360158452952329 | relative 1e-09 | pass |
| 95 % CI low | SciPy stats.boxcox(alpha=0.05) | -0.961993862358215 | -0.961993862358215 | relative 1e-09 | pass |
| power | R | -0.360158452952329 | -0.360158410727 | relative 0.0001 | pass |

Note: car::powerTransform maximises the same likelihood with another optimiser (to about 1e-5).

### `table.fit_curve`

**Rat42: a logistic growth curve (NIST certified)** (published; data: NIST Rat42)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| b1 | NIST certified | 72.4622375422844 | 72.462237576 | at least 6 digits (LRE 9.3) | pass |
| b2 | NIST certified | 2.61807684203404 | 2.6180768402 | at least 6 digits (LRE 9.2) | pass |
| b3 | NIST certified | 0.0673592001448143 | 0.067359200066 | at least 6 digits (LRE 8.9) | pass |
| residual sum of squares | NIST certified | 8.05652293381132 | 8.0565229338 | at least 6 digits (LRE 11.9) | pass |

Note: NIST writes the curve as b1 / (1 + exp(b2 - b3 x)): b1 is Asym, b2 is xmid / scal and b3 is 1 / scal of R's SSlogis.

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

**Puromycin (treated): a Michaelis-Menten curve** (published; data: Puromycin (treated))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Vm | Bates & Watts (1988) | 212.683742870014 | 212.7 | within 0.05 (printed rounding) | pass |
| K | Bates & Watts (1988) | 0.0641212812688425 | 0.06412 | within 5e-06 (printed rounding) | pass |
| Vm | R | 212.683742870014 | 212.683707271206 | relative 1e-05 | pass |
| K | R | 0.0641212812688425 | 0.0641212257944682 | relative 1e-05 | pass |

Note: R nls() stops at a relative offset of 1e-5, so it agrees to about 1e-5.

### `table.explain`

**drivers killed (counts): the rate ratio of the jump at the seat-belt law** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| jump | statsmodels GLM (Poisson) with the two change columns | 0.724689274189852 | 0.724689274189852 | relative 1e-07 | pass |
| slope change | statsmodels GLM (Poisson) with the two change columns | 1.0154100777643 | 1.0154100777643 | relative 1e-07 | pass |
| jump | R | 0.724689274189852 | 0.724689274189851 | relative 1e-07 | pass |
| slope change | R | 1.0154100777643 | 1.0154100777643 | relative 1e-07 | pass |

**Engel's food expenditure: the 90th percentile line** (real data; data: Engel food expenditure)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| intercept | statsmodels QuantReg (estimates only: its standard errors are not R's) | 67.3508720801297 | 67.3508508634295 | relative 1e-05 | pass |
| income | statsmodels QuantReg (estimates only: its standard errors are not R's) | 0.686299480371905 | 0.686299496768461 | relative 1e-05 | pass |
| intercept | R | 67.3508720801297 | 67.3508720801297 | relative 1e-09 | pass |
| income | R | 0.686299480371905 | 0.686299480371905 | relative 1e-09 | pass |
| income standard error | R | 0.0284907223757293 | 0.0284907223757293 | relative 1e-09 | pass |

Note: statsmodels solves by iteratively reweighted least squares and R quantreg by the exact simplex; the lines agree to about 1e-7.

### `table.add_smoothed_column`

**drivers killed or seriously injured, smoothed by loess with its band** (real data; data: Seatbelts)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| first | R | 1644.03914048406 | 1644.03914048406 | relative 1e-09 | pass |
| last | R | 1323.4857369989 | 1323.4857369989 | relative 1e-09 | pass |
| first band low | R | 1511.97714881285 | 1511.97714881285 | relative 1e-09 | pass |

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
| `table.fit_dose_response` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_dose_response` | R + Python | polars | result | relative 1e-09 | pass |
| `fit_dose_response` | R + matplotlib | pandas | chart | relative 1e-06 | pass |
| `table.find_best_power_of` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.find_best_power_of` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line (method="theil-sen")` | SciPy | pandas | result | relative 1e-09 | pass |
| `table.fit_line (method="theil-sen")` | SciPy | polars | result | relative 1e-09 | pass |
| `table.fit_line (method="standardised major axis")` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line (method="standardised major axis")` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line (method="deming", y_error_over_x_error=)` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line (method="deming", y_error_over_x_error=)` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line (method="passing-bablok")` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line (method="passing-bablok")` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line (with_bends=)` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.fit_line (with_bends=)` | R + Python | polars | result | relative 1e-09 | pass |
| `table.fit_line (changes_at=)` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.fit_line (changes_at=)` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.fit_curve (of_kind="logistic growth")` | SciPy | pandas | result | relative 1e-05 | pass |
| `table.fit_curve (of_kind="logistic growth")` | SciPy | polars | result | relative 1e-05 | pass |
| `table.explain (for_percentile=)` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.explain (for_percentile=)` | R + Python | polars | result | relative 1e-09 | pass |
| `table.explain (changes_at=)` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.explain (changes_at=)` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.add_smoothed_column (method="loess", interval=)` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.add_smoothed_column (method="loess", interval=)` | R + Python | polars | result | relative 1e-09 | pass |
| `draw_smooth_line (method="loess", with_confidence_band=)` | R + matplotlib | pandas | chart | relative 1e-09 | pass |

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
- `table.fit_dose_response` (1): the 4 parameter log-logistic curve, the usual one in ecotoxicology (drc's LL.4); of_kind= chooses another.
- `table.fit_dose_response` (2): the ED50 with its delta-method interval: drc's ED() gives no interval unless asked (interval = "none" is its default).
- `fit_dose_response` (1): the 4 parameter log-logistic curve (drc's LL.4), as table.fit_dose_response.
- `fit_dose_response` (2): the curve is drawn over 300 doses spaced evenly on a log scale (and dose 0), so it stays smooth on a log dose axis too; the ED50 and its delta-method interval go in the legend.
- `table.find_best_power_of` (1): the power's 95 % interval from the profile likelihood (alpha=0.05); without alpha= SciPy gives no interval.
- `table.fit_line (method="theil-sen")` (1): SciPy's alpha= is the confidence level (0.95), not the error rate.
- `table.fit_line (method="theil-sen")` (2): the intercept is the median of y - slope * x (Conover; SciPy's default); R mblm takes the median of the pair intercepts instead.
- `table.fit_line (method="standardised major axis")` (1): smatr's own 95 % intervals (Warton et al. 2006); method="major axis" is method = "MA".
- `table.fit_line (method="deming", y_error_over_x_error=)` (1): mcr's error.ratio is the error variance of x over that of y, the other way round from y_error_over_x_error=, so it gets 1 / 4.
- `table.fit_line (method="deming", y_error_over_x_error=)` (2): mcr's analytical intervals; its default (bootstrap) is random and differs from run to run.
- `table.fit_line (method="passing-bablok")` (1): Passing and Bablok's own rank-based intervals (mcr's "analytical" for PaBa); mcr's default bootstrap is random.
- `table.fit_line (with_bends=)` (1): a continuous line: it bends, it does not jump (segmented's model).
- `table.fit_line (with_bends=)` (2): Davies' test of "no bend at all": the bend's own p-value is not valid, because the data chose where it is.
- `table.fit_line (changes_at=)` (1): the change starts at the point itself: rows at 10 or later count as after.
- `table.fit_curve (of_kind="logistic growth")` (1): start values: simplydata takes them from R's self-starting model (stats::getInitial()), or searches the whole range without R; the least-squares answer is the same.
- `table.explain (for_percentile=)` (1): R quantreg's exact simplex (Barrodale-Roberts); statsmodels QuantReg gives the same line to about 1e-7 but none of R's standard errors.
- `table.explain (for_percentile=)` (2): standard errors by "nid" for every number of rows (R's default below 1001 rows is "rank", intervals only).
- `table.explain (changes_at=)` (1): the change starts at the point itself: rows at 10 or later count as after.
- `table.add_smoothed_column (method="loess", interval=)` (1): R loess's own defaults: span 0.75 (smoothness=), local curves of degree 2, no robustness steps.
- `table.add_smoothed_column (method="loess", interval=)` (2): the band uses loess's own degrees of freedom, as R's predict.loess intervals do.
- `draw_smooth_line (method="loess", with_confidence_band=)` (1): R loess's own defaults: span 0.75, local curves of degree 2, no robustness steps (not lowess).

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
