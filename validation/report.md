# simplydata reliability report

Made by `python validation/make_report.py` on 2026-11-20. Generated: do not edit by hand.

Each simplydata word is run on real, published data and compared with the published answer, with the package simplydata uses underneath called directly, and with R. Each "same underneath" box of the manual is run next to its word and compared too. How it works, and the datasets with their licences: [validation/README.md](README.md).

**223 checks passed, 0 failed, 0 skipped** (skipped: R or an R package is not installed on this computer).

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

**a list of columns: MANOVA of sepal and petal length across species** (real data; data: iris)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Pillai | statsmodels MANOVA | 0.988500527043348 | 0.988500527043348 | relative 1e-09 | pass |
| F | statsmodels MANOVA | 71.8287954469352 | 71.8287954469352 | relative 1e-09 | pass |
| Wilks | statsmodels MANOVA | 0.0398783132489411 | 0.0398783132489411 | relative 1e-09 | pass |
| Pillai | R | 0.988500527043348 | 0.98850052704333 | relative 1e-10 | pass |
| F | R | 71.8287954469352 | 71.8287954469326 | relative 1e-10 | pass |
| Wilks | R | 0.0398783132489411 | 0.0398783132489476 | relative 1e-10 | pass |

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

### `table.explain`

**spread_changes_with=: the spread of the ultrafiltration rate grows with pressure (varPower)** (real data; data: Dialyzer (nlme))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| slope | R | 19.6065136226626 | 19.6065136226626 | relative 1e-05 | pass |
| standard error | R | 0.926865072914266 | 0.926865072914266 | relative 1e-05 | pass |
| power | R | 0.290039657383882 | 0.290039657383882 | relative 1e-05 | pass |

Note: R nlme::gls() is the reference: statsmodels has no variance functions. nlme's optimiser stops at its own tolerance, so the numbers agree to about 1e-6.

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

### `table.compare_models`

**using=[[...], ...]: three models of fertility, AICc and Akaike weights** (real data; data: swiss)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| AICc smallest | statsmodels OLS and eval_measures.aicc | 348.980436348024 | 348.980436348024 | relative 1e-09 | pass |
| weight of the biggest | statsmodels OLS and eval_measures.aicc | 0.98503186334779 | 0.98503186334779 | relative 1e-09 | pass |
| AICc smallest | R | 348.980436348024 | 348.980436348024 | relative 1e-09 | pass |
| weight of the biggest | R | 0.98503186334779 | 0.985031863347791 | relative 1e-09 | pass |

**check_on_left_out_rows=True: low birth weight from age, weight and smoking (Brier score in 10 parts)** (real data; data: birthwt (MASS))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| left out | R | 0.212566042141893 | 0.212566042141893 | relative 1e-10 | pass |
| adjusted | R | 0.212082848900463 | 0.212082848900463 | relative 1e-10 | pass |

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

**outcome="yes or no": Hosmer-Lemeshow test and Brier score, low birth weight** (real data; data: birthwt (MASS))

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| Hosmer-Lemeshow | R | 7.22544929206197 | 7.22544929206197 | relative 1e-06 | pass |
| Hosmer-Lemeshow p | R | 0.512515395932266 | 0.512515395932266 | relative 1e-06 | pass |
| Brier | R | 0.202650010245525 | 0.202650010245525 | relative 1e-06 | pass |

### `table.find_model_averages_of`

**comparing="each with the first": each tension against the low one** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| M minus L | R | -10 | -10 | relative 1e-06 | pass |
| H minus L | R | -14.7222222222222 | -14.7222222222222 | relative 1e-06 | pass |
| p H minus L | R | 0.000383446958904465 | 0.000383446958904465 | relative 1e-06 | pass |

Note: R emmeans is the reference. Dunnett's p-values (dunnettx) come from a close approximation of the multivariate t, so they agree to about 1e-6.

**within_each_group_in=: the interaction test and tension within each wool** (real data; data: warpbreaks)

| number | compared with | simplydata | reference | tolerance | result |
|---|---|---|---|---|---|
| interaction F | R | 4.189 | 4.189 | relative 1e-09 | pass |
| tension within A | R | 10.312 | 10.312 | relative 1e-09 | pass |

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
| `table.find_columns_that_predict` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_columns_that_predict` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_group_levels_of` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_group_levels_of` | R + Python | polars | result | relative 1e-06 | pass |
| `draw_interaction_lines` | seaborn | pandas | chart | relative 1e-09 | pass |
| `table.explain (spread_changes_with="school")` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.explain (spread_changes_with="school")` | R + Python | polars | result | relative 1e-05 | pass |
| `table.explain (neighbours_alike_in_order_of="year")` | R + Python | pandas | result | relative 1e-05 | pass |
| `table.explain (neighbours_alike_in_order_of="year")` | R + Python | polars | result | relative 1e-05 | pass |
| `table.compare_models (using=[[...], [...]])` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_models (using=[[...], [...]])` | statsmodels | polars | result | relative 1e-09 | pass |
| `table.compare_models (check_on_left_out_rows=True)` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_models (check_on_left_out_rows=True)` | R + Python | polars | result | relative 1e-09 | pass |
| `table.find_model_averages_of (comparing="each with the first")` | R + Python | pandas | result | relative 1e-06 | pass |
| `table.find_model_averages_of (comparing="each with the first")` | R + Python | polars | result | relative 1e-06 | pass |
| `table.find_model_averages_of (within_each_group_in="breakfast")` | R + Python | pandas | result | relative 1e-08 | pass |
| `table.find_model_averages_of (within_each_group_in="breakfast")` | R + Python | polars | result | relative 1e-08 | pass |
| `table.find_model_averages_of (over_range_of="hours")` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.find_model_averages_of (over_range_of="hours")` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_averages_of (grouped_by="rat")` | R + Python | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of (grouped_by="rat")` | R + Python | polars | result | relative 1e-09 | pass |
| `table.compare_averages_of (for_each_group_in= with a list of columns)` | statsmodels | pandas | result | relative 1e-09 | pass |
| `table.compare_averages_of (for_each_group_in= with a list of columns)` | statsmodels | polars | result | relative 1e-09 | pass |

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
- `table.find_columns_that_predict` (1): the random split into 10 parts is made in R itself (with_seed=1 is set.seed(1)), so R's own random numbers give the same parts.
- `table.find_columns_that_predict` (2): the lasso (alpha = 1) with 10 parts; method="elastic net" is alpha = 0.5.
- `table.find_columns_that_predict` (3): the penalty is lambda.1se, the largest within one standard error of the best (fewer columns, steadier); simplydata names it, so a change of glmnet's default cannot change the answer.
- `table.find_group_levels_of` (1): condVar = TRUE: each level comes with its conditional variance; without it ranef() gives no uncertainty.
- `table.find_group_levels_of` (2): the 95 % interval is the level plus and minus 1.96 conditional standard deviations, as lattice::dotplot(ranef(m, condVar = TRUE)) draws it.
- `draw_interaction_lines` (1): 95 % t intervals of each average, as R t.test(); seaborn's own default is a bootstrap interval, which changes from run to run.
- `draw_interaction_lines` (2): the groups are moved a little apart (dodged) so their bars do not hide each other.
- `table.explain (spread_changes_with="school")` (1): REML, nlme's default, for the effects.
- `table.explain (spread_changes_with="school")` (2): a group column gives each group its own spread (varIdent); a number column would give a spread that grows as a power of it (varPower).
- `table.explain (neighbours_alike_in_order_of="year")` (1): evenly spaced values give the AR(1) correlation (corAR1), each step one step apart; uneven gaps give corCAR1, which allows for the size of each gap.
- `table.compare_models (using=[[...], [...]])` (1): every value estimated counts, the residual spread too, as R logLik(); statsmodels' own aic leaves it out (a difference of 2).
- `table.compare_models (using=[[...], [...]])` (2): AICc when there are fewer than 40 rows per value estimated (Burnham & Anderson 2002), else AIC.
- `table.compare_models (check_on_left_out_rows=True)` (1): with_seed=1 is set.seed(1) in R, so R's own random numbers make the parts.
- `table.compare_models (check_on_left_out_rows=True)` (2): K = 10 parts: cv.glm's own default leaves out one row at a time.
- `table.find_model_averages_of (comparing="each with the first")` (1): each group against the first group (in sorted order, or the first of in_order=).
- `table.find_model_averages_of (comparing="each with the first")` (2): emmeans' own adjustment for this method (dunnettx), printed by simplydata.
- `table.find_model_averages_of (within_each_group_in="breakfast")` (1): the interaction test comes first (emmeans joint_tests()), and the comparisons within each group after it: compare the groups with the interaction test, not by which simple effects have small p-values (Gelman & Stern 2006).
- `table.find_model_averages_of (over_range_of="hours")` (1): 50 evenly spaced values from the smallest to the largest hours.
- `table.find_model_averages_of (over_range_of="hours")` (2): the other columns as emmeans holds them: numbers at their average, groups counted equally.
- `table.compare_averages_of (grouped_by="rat")` (1): the treatment is tested against the variation between rats (Error(rat)), not between readings: the readings of one rat are not independent.
- `table.compare_averages_of (for_each_group_in= with a list of columns)` (1): Pillai's trace first, the one R summary(manova()) prints by default and the safest when groups differ in size or spread.

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
| [Dialyzer (nlme)](https://cran.r-project.org/package=nlme) | ultrafiltration rate of 20 high-flux haemodialyzers at 7 transmembrane pressures, at two blood flow rates (140 rows) | Vonesh, E. F. & Carter, R. L. (1992). Mixed-effects nonlinear regression for unbalanced repeated measures. Biometrics 48, 1-17. Analysed with variance functions in Pinheiro, J. C. & Bates, D. M. (2000). Mixed-Effects Models in S and S-PLUS. Springer, section 5.2. Shipped with the R package nlme. | GPL (nlme). Not stored here: read from nlme, so it needs R. |
| [Lake Huron](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/LakeHuron.html) | annual level of Lake Huron in feet, 1875-1972 | Brockwell, P. J. & Davis, R. A. (1991). Time Series and Forecasting Methods, 2nd ed. Springer, pp. 328-329 (from the US Army Corps of Engineers). Copy from R's datasets package (LakeHuron). | US Government measurements (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. |
| [swiss](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/swiss.html) | fertility and five social measures of 47 French-speaking provinces of Switzerland in about 1888 | Mosteller, F. & Tukey, J. W. (1977). Data Analysis and Regression. Addison-Wesley, pp. 549-551 (from the Office of Population Research, Princeton, 1976). Copy from R's datasets package (swiss). | Official 1888 statistics (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. |
| [birthwt (MASS)](https://cran.r-project.org/package=MASS) | 189 births at Baystate Medical Center, Springfield, Massachusetts (1986): low birth weight, the mother's age, weight and smoking | Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Shipped with the R package MASS (Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed.). | GPL-2 \| GPL-3 (MASS). Not stored here: read from MASS, so it needs R. |
| [warpbreaks](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/warpbreaks.html) | the number of warp breaks per loom for two wools (A, B) at three tensions (L, M, H), 9 looms each | Tippett, L. H. C. (1950). Technological Applications of Statistics. Wiley, p. 106. Copy from R's datasets package (warpbreaks). | Published 1950 (facts). The copy in R's datasets package is GPL-2 \| GPL-3. |
| [sleepstudy (lme4)](https://doi.org/10.18637/jss.v067.i01) | average reaction time of 18 truck drivers on each of 10 days of sleep deprivation (180 rows) | Belenky, G. et al. (2003). Patterns of performance degradation and restoration during sleep restriction and subsequent recovery. Journal of Sleep Research 12, 1-12. Analysed in Bates, D., Maechler, M., Bolker, B. & Walker, S. (2015). Fitting linear mixed-effects models using lme4. Journal of Statistical Software 67(1) (CC BY). Shipped with the R package lme4. | GPL (>= 2) (lme4). Not stored here: read from lme4, so it needs R. |
| [rat liver glycogen](https://www.worldcat.org/title/biometry/oclc/7203719) | glycogen in the livers of 6 rats, 2 on each of 3 treatments (control, glucose, glucose and fructose), 3 preparations per liver and 2 readings per preparation (36 rows) | Sokal, R. R. & Rohlf, F. J. (1981). Biometry, 2nd ed. Freeman, Box 10.1 (nested ANOVA: treatments SS 1557.56 on 2 df, rats within treatments SS 797.67 on 3 df, F = 2.929); the same analysis in Crawley, M. J. (2007). The R Book. Wiley, chapter 11. | Facts published in the book (36 numbers), typed from it; not covered by copyright. |
| [iris](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/iris.html) | sepal and petal length and width of 50 flowers of each of three iris species | Anderson, E. (1935). The irises of the Gaspe Peninsula. Bulletin of the American Iris Society 59, 2-5; Fisher, R. A. (1936). The use of multiple measurements in taxonomic problems. Annals of Eugenics 7, 179-188. Copy from R's datasets package (iris). | Published 1935 (public domain). The copy in R's datasets package is GPL-2 \| GPL-3. |
