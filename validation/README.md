# How we check simplydata

simplydata does no statistics of its own: every word calls an established package (pandas, Polars,
NumPy, SciPy, statsmodels, matplotlib, seaborn, or R through rpy2). So the question is whether each word
calls it the right way, with the right settings. This folder answers that question in public, so anyone
can rerun it.

**The report:** [report.md](report.md), with every check, what it was compared with, the tolerance, and
whether it passed, plus the system, Python, package and R versions it was run with.

## Rerun it

From a copy of the repository (`pip install -e ".[test]"` first; add `".[test,r]"` and R for the R parts):

```
python validation/make_report.py                       # writes validation/report.md
python validation/make_report.py --check               # checks only: exit code 1 if any check fails
                                                       # (the report goes to the temporary folder, or --out)
python validation/make_report.py --check --require-r   # and a skipped R part counts as a failure
```

Where R, rpy2 or an R package is missing, the R parts are skipped and the report says so. CI runs the
report on every setup with `SIMPLYDATA_REQUIRE_R=1`, so there a missing R fails instead. The test suite
runs the same checks (`tests/test_underneath.py`, `tests/test_validation.py`) on Windows, macOS and Linux
with Python 3.11 to 3.13 for every change.

## What is checked

1. **Real data with published answers** (`cases.py`). Each word runs on real data, and what it gives is
   compared with
   - the **published answer**: certified values from the NIST Statistical Reference Datasets, or the
     numbers printed in the paper (allowing for their printed rounding);
   - the **parent package** called directly, at a tight tolerance;
   - **R**, as an independent second calculation, where R is installed.

   NIST certified values are compared by the log relative error (LRE): the number of significant digits
   that agree. A word must match at least 9 digits; for the nonlinear (curve) problems, at least 6, the
   level at which statistical software is judged on them (McCullough 1999).
   Made-up data are used only for edge cases that no real dataset tests (empty cells, no rows left, an
   exact line), and the report labels them *made-up*.

2. **The same underneath** (`src/simplydata/_underneath/`). The manual shows, for each word, the same
   job written in the package underneath. Each of those boxes is run next to the word and compared:
   numbers to a stated tolerance, tables by values and column order (on a pandas and on a Polars table),
   and charts by their data (bars, dots, lines, labels, limits), never by pixels.

3. **Choices simplydata makes.** Where simplydata's default differs from the package underneath (for
   example Welch's t-test where SciPy's `ttest_ind` assumes equal spreads, or 10 histogram bins), the report lists it, so a difference is never hidden.

This first version covers ten words, one of each kind: `draw_bars`, `draw_histogram`, `draw_dots`,
`table.keep_rows_where`, `table.find_average_of`, `table.compare_averages_of`, `table.fit_line`,
`nums.find_median`, `dist.find_chance_that_value` and the R word `trade_off_curve`. More words are
added with each release; a word counts as done only when its checks pass. The sleep data also check
`table.compare_before_and_after`, the paired test Student himself used for them.

## Datasets

Only openly licensed data are stored in `data/`; the rest are read from where they are published.

| dataset | file | source | licence |
|---|---|---|---|
| NIST StRD Norris (straight line, 36 points) | `data/nist/Norris.dat` | Norris, J., NIST. Calibration of Ozone Monitors. NIST Statistical Reference Datasets, Linear Regression. https://www.itl.nist.gov/div898/strd/lls/data/Norris.shtml | Public domain in the US (US Government work, 17 U.S.C. 105); stored with its numbers unchanged |
| NIST StRD Michelso (Michelson's speed of light, 100 values) | `data/nist/Michelso.dat` | Dorsey, E. N. (1944). The Velocity of Light. Transactions of the American Philosophical Society 34(1), 1-110, Table 22. NIST StRD, Univariate Summary Statistics. https://www.itl.nist.gov/div898/strd/univ/michelso.html | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Mavro (filter transmittance, 50 values) | `data/nist/Mavro.dat` | Mavrodineanu, R., NIST. NIST StRD, Univariate Summary Statistics. https://www.itl.nist.gov/div898/strd/univ/mavro.html | Public domain in the US; stored with its numbers unchanged |
| NIST StRD NumAcc4 (1001 constructed values) | `data/nist/NumAcc4.dat` | Simon, S. D. & Lesage, J. P. (1989). Assessing the accuracy of ANOVA calculations in statistical software. Computational Statistics & Data Analysis 8, 325-332. NIST StRD. https://www.itl.nist.gov/div898/strd/univ/numacc4.html | Public domain in the US; stored with its numbers unchanged |
| Student's sleep data | `data/sleep.csv` | Cushny, A. R. & Peebles, A. R. (1905). The action of optical isomers. II. Hyoscines. Journal of Physiology 32, 501-510; analysed by Student (1908). The probable error of a mean. Biometrika 6(1), 1-25. Copy from R's `datasets::sleep` | Public domain (published 1905 and 1908); R's copy is GPL-2 \| GPL-3 |
| Anscombe's quartet | `data/anscombe.csv` | Anscombe, F. J. (1973). Graphs in statistical analysis. The American Statistician 27(1), 17-21. Copy from R's `datasets::anscombe` | The published numbers, as in R's datasets package (GPL-2 \| GPL-3) |
| aSAH | not stored | Turck, N. et al. (2010). Intensive Care Medicine 36, 107-115; shipped with the R package pROC (Robin, X. et al. (2011). BMC Bioinformatics 12, 77) | GPL-3 or later (pROC); read from the installed pROC package, so it needs R |
| NIST StRD Rat42 (logistic growth, 9 points) | `data/nist/Rat42.dat` | Ratkowsky, D. A. (1983). Nonlinear Regression Modeling. NIST StRD, Nonlinear Regression. https://www.itl.nist.gov/div898/strd/nls/data/ratkowsky2.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Misra1a (rise to a limit, 14 points) | `data/nist/Misra1a.dat` | Misra, D., NIST (1978). Dental research monomolecular adsorption study. NIST StRD, Nonlinear Regression. https://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD BoxBOD (rise to a limit, 6 points) | `data/nist/BoxBOD.dat` | Box, G. P., Hunter, W. G. & Hunter, J. S. (1978). Statistics for Experimenters, pp. 483-487. NIST StRD, Nonlinear Regression. https://www.itl.nist.gov/div898/strd/nls/data/boxbod.shtml | Public domain in the US; stored with its numbers unchanged |
| Bliss's beetles (8 doses) | `data/bliss.csv` | Bliss, C. I. (1935). The calculation of the dosage-mortality curve. Annals of Applied Biology 22, 134-167; fit printed in Dobson & Barnett (2008), An Introduction to Generalized Linear Models, 3rd ed. | Facts published in 1935, typed from the paper |
| Puromycin, treated (12 rows) | `data/puromycin.csv` | Treloar, M. A. (1974), M.Sc. thesis, University of Toronto; fit printed in Bates, D. M. & Watts, D. G. (1988). Nonlinear Regression Analysis and Its Applications. Copy from R's `datasets::Puromycin` | Published facts; R's copy is GPL-2 \| GPL-3 |
| Seatbelts (UK drivers killed or seriously injured, monthly 1969-1984) | `data/seatbelts.csv` | Harvey, A. C. & Durbin, J. (1986). Journal of the Royal Statistical Society A 149, 187-227. Copy from R's `datasets::Seatbelts` | Official counts published in the paper; R's copy is GPL-2 \| GPL-3 |
| ryegrass | not stored | Inderjit et al. (2002), Physiologia Plantarum 114, 422-428; Ritz, C. et al. (2015). Dose-response analysis using R. PLoS ONE 10, e0146021; shipped with R's drc | Article CC BY 4.0; data GPL-2 (drc); read from drc, so it needs R |
| poisons | not stored | Box, G. E. P. & Cox, D. R. (1964). An analysis of transformations. JRSS B 26, 211-252; shipped with R's boot | Published facts; read from boot, so it needs R |
| stagnant | not stored | Bacon, D. W. & Watts, D. G. (1971). Biometrika 58, 525-534; shipped with R's segmented | Published facts; read from segmented (GPL), so it needs R |
| leaflife | not stored | Wright, I. J., Westoby, M. & Reich, P. B. (2002). Journal of Ecology 90, 534-543; shipped with R's smatr | GPL-2 (smatr); read from smatr, so it needs R |
| creatinine | not stored | The method-comparison example of R's mcr (Roche Diagnostics) | GPL-3 (mcr); read from mcr, so it needs R |
| Engel food expenditure | not stored | Engel, E. (1857); Koenker, R. & Bassett, G. (1982). Econometrica 50, 43-61; copy in statsmodels | Public domain (1857); read from statsmodels |
| Standard normal table | not stored | NIST/SEMATECH e-Handbook of Statistical Methods, 1.3.6.7.1. https://www.itl.nist.gov/div898/handbook/eda/section3/eda3671.htm | Public domain in the US; one number quoted |

The same list, with what each dataset holds, is at the end of the report.

## Files

- `make_report.py`: builds the report (one command, above).
- `cases.py`: the cases on real data, the datasets with their licences and citations, and the edge cases.
- `cases_lines.py`: the same for the lines and curves of phase S3a-2 (loaded by `cases.py`).
- `data/`: the stored datasets.
- `report.md`: the last report made and committed.
