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
python validation/make_report.py            # writes validation/report.md
python validation/make_report.py --check    # the same, and exit code 1 if any check fails
```

Where R, rpy2 or an R package is missing, the R parts are skipped and the report says so. The test suite
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
   that agree. A word must match at least 9 digits.
   Made-up data are used only for edge cases that no real dataset tests (empty cells, no rows left, an
   exact line), and the report labels them *made-up*.

2. **The same underneath** (`src/simplydata/_underneath/`). The manual shows, for each word, the same
   job written in the package underneath. Each of those boxes is run next to the word and compared:
   numbers to a stated tolerance, tables by values and column order (on a pandas and on a Polars table),
   and charts by their data (bars, dots, lines, labels, limits), never by pixels.

3. **Choices simplydata makes.** Where simplydata's default differs from the package underneath (for
   example Welch's test, or 10 histogram bins), the report lists it, so a difference is never hidden.

This first version covers ten words, one of each kind: `draw_bars`, `draw_histogram`, `draw_dots`,
`table.keep_rows_where`, `table.find_average_of`, `table.compare_averages_of`, `table.fit_line`,
`nums.find_median`, `dist.find_chance_that_value` and the R word `trade_off_curve`. More words are
added with each release; a word counts as done only when its checks pass.

## Datasets

Only openly licensed data are stored in `data/`; the rest are read from where they are published.

| dataset | file | source | licence |
|---|---|---|---|
| NIST StRD Norris (straight line, 36 points) | `data/nist/Norris.dat` | Norris, J., NIST. Calibration of Ozone Monitors. NIST Statistical Reference Datasets, Linear Regression. https://www.itl.nist.gov/div898/strd/lls/data/Norris.shtml | Public domain in the US (US Government work, 17 U.S.C. 105); stored unchanged |
| NIST StRD Michelso (Michelson's speed of light, 100 values) | `data/nist/Michelso.dat` | Dorsey, E. N. (1944). The Velocity of Light. Transactions of the American Philosophical Society 34(1), 1-110, Table 22. NIST StRD, Univariate Summary Statistics. https://www.itl.nist.gov/div898/strd/univ/michelso.html | Public domain in the US; stored unchanged |
| NIST StRD Mavro (filter transmittance, 50 values) | `data/nist/Mavro.dat` | Mavrodineanu, R., NIST. NIST StRD, Univariate Summary Statistics. https://www.itl.nist.gov/div898/strd/univ/mavro.html | Public domain in the US; stored unchanged |
| NIST StRD NumAcc4 (1001 constructed values) | `data/nist/NumAcc4.dat` | Simon, S. D. & Lesage, J. P. (1989). Assessing the accuracy of ANOVA calculations in statistical software. Computational Statistics & Data Analysis 8, 325-332. NIST StRD. https://www.itl.nist.gov/div898/strd/univ/numacc4.html | Public domain in the US; stored unchanged |
| Student's sleep data | `data/sleep.csv` | Cushny, A. R. & Peebles, A. R. (1905). The action of optical isomers. II. Hyoscines. Journal of Physiology 32, 501-510; analysed by Student (1908). The probable error of a mean. Biometrika 6(1), 1-25. Copy from R's `datasets::sleep` | Public domain (published 1905 and 1908); R's copy is GPL-2 \| GPL-3 |
| Anscombe's quartet | `data/anscombe.csv` | Anscombe, F. J. (1973). Graphs in statistical analysis. The American Statistician 27(1), 17-21. Copy from R's `datasets::anscombe` | The published numbers, as in R's datasets package (GPL-2 \| GPL-3) |
| aSAH | not stored | Turck, N. et al. (2010). Intensive Care Medicine 36, 107-115; shipped with the R package pROC (Robin, X. et al. (2011). BMC Bioinformatics 12, 77) | GPL-3 or later (pROC); read from the installed pROC package, so it needs R |
| Standard normal table | not stored | NIST/SEMATECH e-Handbook of Statistical Methods, 1.3.6.7.1. https://www.itl.nist.gov/div898/handbook/eda/section3/eda3671.htm | Public domain in the US; one number quoted |

The same list, with what each dataset holds, is at the end of the report.

## Files

- `make_report.py`: builds the report (one command, above).
- `cases.py`: the cases on real data, the datasets with their licences and citations, and the edge cases.
- `data/`: the stored datasets.
- `report.md`: the last report made and committed.
