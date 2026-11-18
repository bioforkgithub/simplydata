"""The reliability study's cases: real, published data first; made-up data only for edge cases.

Each case runs a simplydata word on a dataset and compares what it gives with
  * the published answer, where there is one (NIST certified values, numbers printed in the paper),
    allowing for the printed rounding, and
  * the parent package called directly (NumPy, pandas, SciPy, statsmodels, seaborn) and, where R is
    installed, R.
The datasets, their licences and how to cite them are in DATASETS (and in validation/README.md).

kind = "published"  real data with a published or certified answer
       "real data"  real data from a published source, compared with the parent package and R
       "made-up"    made-up data for an edge case no real dataset tests (labelled as such in the report)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


# ---------------------------------------------------------------- the datasets
@dataclass(frozen=True)
class Dataset:
    name: str
    file: str            # under validation/data/ ("" when it is not stored)
    what: str
    source: str          # how to cite it
    licence: str
    url: str


DATASETS = {d.name: d for d in [
    Dataset("NIST Norris", "nist/Norris.dat",
            "36 observations of ozone monitor calibration; certified straight-line fit (NIST StRD, lower difficulty)",
            "Norris, J., NIST. Calibration of Ozone Monitors. In: NIST Statistical Reference Datasets (StRD), "
            "Linear Regression, dataset Norris. National Institute of Standards and Technology.",
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); stored unchanged.",
            "https://www.itl.nist.gov/div898/strd/lls/data/Norris.shtml"),
    Dataset("NIST Michelso", "nist/Michelso.dat",
            "100 measurements of the speed of light in air by Michelson (1879); certified mean and standard deviation",
            "Dorsey, E. N. (1944). The Velocity of Light. Transactions of the American Philosophical Society 34(1), "
            "1-110, Table 22. In: NIST StRD, Univariate Summary Statistics, dataset Michelso.",
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); stored unchanged.",
            "https://www.itl.nist.gov/div898/strd/univ/michelso.html"),
    Dataset("NIST Mavro", "nist/Mavro.dat",
            "50 filter transmittance measurements by R. Mavrodineanu (NIST); certified mean and standard deviation",
            "Mavrodineanu, R., NIST. Filter transmittance data. In: NIST StRD, Univariate Summary Statistics, "
            "dataset Mavro.",
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); stored unchanged.",
            "https://www.itl.nist.gov/div898/strd/univ/mavro.html"),
    Dataset("NIST NumAcc4", "nist/NumAcc4.dat",
            "1001 nine-digit numbers that differ only in the last digit; constructed by NIST to test accuracy "
            "(higher difficulty); certified mean 10000000.2 exactly",
            "Simon, S. D. & Lesage, J. P. (1989). Assessing the accuracy of ANOVA calculations in statistical "
            "software. Computational Statistics & Data Analysis 8, 325-332. In: NIST StRD, dataset NumAcc4.",
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); stored unchanged.",
            "https://www.itl.nist.gov/div898/strd/univ/numacc4.html"),
    Dataset("Student's sleep data", "sleep.csv",
            "extra hours of sleep for 10 patients with each of two drugs",
            "Cushny, A. R. & Peebles, A. R. (1905). The action of optical isomers. II. Hyoscines. Journal of "
            "Physiology 32, 501-510. Analysed by Student (1908). The probable error of a mean. Biometrika 6(1), "
            "1-25. Copy from R's datasets package (sleep).",
            "Public domain (published 1905 and 1908); the copy in R's datasets package is GPL-2 | GPL-3.",
            "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/sleep.html"),
    Dataset("Anscombe's quartet", "anscombe.csv",
            "four sets of 11 (x, y) pairs with the same straight-line fit",
            "Anscombe, F. J. (1973). Graphs in statistical analysis. The American Statistician 27(1), 17-21. "
            "Copy from R's datasets package (anscombe).",
            "The 88 published numbers, as in R's datasets package (GPL-2 | GPL-3).",
            "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/anscombe.html"),
    Dataset("aSAH (pROC)", "",
            "113 patients with aneurysmal subarachnoid haemorrhage: outcome and the biomarker s100b",
            "Turck, N. et al. (2010). A multiparameter panel method for outcome prediction following aneurysmal "
            "subarachnoid hemorrhage. Intensive Care Medicine 36, 107-115. Shipped with R's pROC package "
            "(Robin, X. et al. (2011). BMC Bioinformatics 12, 77).",
            "GPL-3 or later (pROC). Not stored here: read from the installed pROC package, so it needs R.",
            "https://cran.r-project.org/package=pROC"),
    Dataset("standard normal table", "",
            "the area under the standard normal curve from 0 to z, to 5 decimals (no data: a published table)",
            "NIST/SEMATECH e-Handbook of Statistical Methods, section 1.3.6.7.1, Cumulative Distribution Function "
            "of the Standard Normal Distribution.",
            "Public domain in the United States (a work of the US Government); one number is quoted, nothing stored.",
            "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3671.htm"),
    Dataset("made-up", "", "small made-up tables for edge cases (empty cells, no rows left, an exact line)",
            "simplydata's validation/cases.py.", "Same as simplydata (see LICENSE).", ""),
]}


def read_nist(file: str) -> tuple[np.ndarray, dict[str, float]]:
    """The data (one column per variable) and the certified values of a NIST StRD file."""
    lines = (DATA / file).read_text(encoding="ascii").splitlines()
    first, last = map(int, re.search(r"Data\s*[:(]\s*lines\s+(\d+)\s+to\s+(\d+)", "\n".join(lines)).groups())
    data = np.array([[float(v) for v in line.split()] for line in lines[first - 1:last]])
    text = "\n".join(lines[:first - 1])
    certified = {}
    number = r"(-?\d+\.\d+(?:E[-+]?\d+)?)"
    for name, pattern in [("mean", rf"Sample Mean\s+ybar:\s+{number}"),
                          ("standard deviation", rf"Sample Standard Deviation \(denom\. = n-1\)\s+s:\s+{number}"),
                          ("intercept", rf"\n\s+B0\s+{number}\s+{number}"),
                          ("slope", rf"\n\s+B1\s+{number}\s+{number}"),
                          ("R squared", rf"R-Squared\s+{number}"),
                          ("residual standard deviation", rf"Standard Deviation\s+{number}\n")]:
        m = re.search(pattern, text, flags=re.I)
        if m:
            certified[name] = float(m.group(1))
            if name in ("intercept", "slope"):
                certified[f"{name} standard error"] = float(m.group(2))
    return data, certified


def load(name: str) -> pd.DataFrame:
    """A dataset as a pandas table: NIST files get columns y (and x)."""
    d = DATASETS[name]
    if d.file.endswith(".dat"):
        data, _ = read_nist(d.file)
        return pd.DataFrame(data, columns=["y", "x"][: data.shape[1]])
    if d.file.endswith(".csv"):
        table = pd.read_csv(DATA / d.file)
        if name == "Student's sleep data":
            table["group"] = "drug " + table["group"].astype(str)
        return table
    if name == "aSAH (pROC)":
        from simplydata._r import r_call

        found = r_call("list(outcome = as.character(pROC::aSAH$outcome), s100b = pROC::aSAH$s100b)",
                       packages=("pROC",), what="the aSAH data of pROC")
        return pd.DataFrame({"outcome": list(found["outcome"]), "s100b": np.asarray(found["s100b"], dtype=float)})
    raise KeyError(name)


def certified(name: str) -> dict[str, float]:
    return read_nist(DATASETS[name].file)[1]


# ---------------------------------------------------------------- the cases
@dataclass(frozen=True)
class Check:
    """One number compared with a reference."""

    name: str
    reference: str        # what it is compared with: "NIST certified", "Student (1908)", "NumPy", "R" ...
    tolerance: float      # absolute, unless relative=True
    relative: bool = False


@dataclass(frozen=True)
class Case:
    word: str
    title: str
    dataset: str
    kind: str
    ours: str                     # simplydata code; data = the dataset; ends with a dict of numbers
    published: dict = field(default_factory=dict)   # name -> (value, absolute tolerance, source)
    parent: str = ""              # Python code with the parent package; ends with a dict of numbers
    parent_label: str = ""
    parent_tolerance: float = 1e-9
    r: str = ""                   # R code (columns of data come in as vectors); ends with a named list
    r_packages: tuple = ()
    r_tolerance: float = 1e-9
    note: str = ""


def _cert(dataset: str, name: str, digits: str) -> tuple:
    """A NIST certified value, read from the file; the tolerance is relative to it (see make_report)."""
    return (certified(dataset)[name], digits, "NIST certified")


CASES = [
    # ---- fit_line: NIST Norris (certified to 15 digits) and Anscombe (1973)
    Case("table.fit_line", "straight line through 36 ozone calibration points", "NIST Norris", "published",
         ours="""
             r = sdata.table(data).fit_line(x="x", y="y").as_pandas().iloc[0]
             {"slope": r["slope"], "intercept": r["intercept"], "slope standard error": r["slope standard error"],
              "intercept standard error": r["intercept standard error"], "R squared": r["R squared"]}
         """,
         published={n: _cert("NIST Norris", n, "lre") for n in
                    ("slope", "intercept", "slope standard error", "intercept standard error", "R squared")},
         parent="""
             from scipy import stats
             f = stats.linregress(data["x"], data["y"])
             {"slope": f.slope, "intercept": f.intercept, "slope standard error": f.stderr,
              "intercept standard error": f.intercept_stderr, "R squared": f.rvalue ** 2}
         """, parent_label="SciPy stats.linregress",
         r="""
             f <- summary(lm(y ~ x))
             list(slope = coef(f)[2, 1], intercept = coef(f)[1, 1], `slope standard error` = coef(f)[2, 2],
                  `intercept standard error` = coef(f)[1, 2], `R squared` = f$r.squared)
         """),
    *[Case("table.fit_line", f"Anscombe's set {i}: the same line through four different patterns",
           "Anscombe's quartet", "published",
           ours=f"""
               r = sdata.table(data).fit_line(x="x{i}", y="y{i}").as_pandas().iloc[0]
               {{"slope": r["slope"], "intercept": r["intercept"], "slope standard error": r["slope standard error"],
                "R squared": r["R squared"]}}
           """,
           # Anscombe (1973) prints: y = 3 + 0.5 x, standard error of the slope 0.118, multiple R squared 0.667
           published={"slope": (0.5, 0.001, "Anscombe (1973)"),
                      "intercept": (3.0, 0.01, "Anscombe (1973)"),
                      "slope standard error": (0.118, 0.001, "Anscombe (1973)"),
                      "R squared": (0.667, 0.001, "Anscombe (1973)")},
           parent=f"""
               from scipy import stats
               f = stats.linregress(data["x{i}"], data["y{i}"])
               {{"slope": f.slope, "intercept": f.intercept, "slope standard error": f.stderr,
                "R squared": f.rvalue ** 2}}
           """, parent_label="SciPy stats.linregress",
           note="The paper prints the fit rounded (3 + 0.5 x); its sets agree with it to within about one unit "
                "of the last printed digit, so the check allows the printed rounding plus that much.")
      for i in (1, 2, 3, 4)],
    # ---- find_average_of: NIST univariate (certified mean)
    *[Case("table.find_average_of", f"average of {what}", name, "published",
           ours="""
               {"mean": sdata.table(data).find_average_of("y")}
           """,
           published={"mean": _cert(name, "mean", "lre")},
           parent="""
               {"mean": data["y"].mean()}
           """, parent_label="pandas Series.mean",
           r="""
               list(mean = mean(y))
           """)
      for name, what in (("NIST Michelso", "Michelson's 100 speed-of-light measurements"),
                         ("NIST Mavro", "50 filter transmittance measurements"),
                         ("NIST NumAcc4", "1001 nine-digit numbers that differ only in the last digit"))],
    # ---- find_median: no certified medians; NumPy and R on the same certified data, and one exact by construction
    *[Case("nums.find_median", f"median of {what}", name, "real data",
           ours="""
               {"median": sdata.numbers(data["y"].tolist()).find_median()}
           """,
           parent="""
               import numpy as np
               {"median": np.nanmedian(data["y"].to_numpy())}
           """, parent_label="NumPy nanmedian", parent_tolerance=1e-15,
           r="""
               list(median = median(y))
           """, r_tolerance=1e-15,
           note="NIST certifies no median; the median is checked against NumPy and R on the same data.")
      for name, what in (("NIST Michelso", "Michelson's 100 speed-of-light measurements"),
                         ("NIST Mavro", "50 filter transmittance measurements"))],
    Case("nums.find_median", "median of NumAcc4 (exact by construction: 500 values .1 below and 500 .1 above "
                             "10000000.2)", "NIST NumAcc4", "published",
         ours="""
             {"median": sdata.numbers(data["y"].tolist()).find_median()}
         """,
         published={"median": (10000000.2, 1e-9, "NIST NumAcc4 description (exact by construction)")},
         parent="""
             import numpy as np
             {"median": np.nanmedian(data["y"].to_numpy())}
         """, parent_label="NumPy nanmedian", parent_tolerance=1e-15),
    # ---- compare_averages_of: Student's sleep data
    Case("table.compare_averages_of", "two drugs, extra hours of sleep (Welch's t-test)", "Student's sleep data",
         "published",
         ours="""
             r = sdata.table(data).compare_averages_of("extra", for_each_group_in="group").as_pandas().iloc[0]
             {"average in drug 1": r["average in drug 1"], "average in drug 2": r["average in drug 2"],
              "difference": r["difference"], "t": r["statistic"], "degrees of freedom": r["degrees of freedom"],
              "p-value": r["p-value"]}
         """,
         # Student (1908) prints the averages +0.75 and +2.33 hours and their difference 1.58 (drug 2 minus drug 1)
         published={"average in drug 1": (0.75, 0.005, "Student (1908)"),
                    "average in drug 2": (2.33, 0.005, "Student (1908)"),
                    "difference": (-1.58, 0.005, "Student (1908)")},
         parent="""
             from scipy import stats
             a = data.loc[data["group"] == "drug 1", "extra"]
             b = data.loc[data["group"] == "drug 2", "extra"]
             t = stats.ttest_ind(a, b, equal_var=False)
             {"average in drug 1": a.mean(), "average in drug 2": b.mean(), "difference": a.mean() - b.mean(),
              "t": t.statistic, "degrees of freedom": t.df, "p-value": t.pvalue}
         """, parent_label="SciPy stats.ttest_ind(equal_var=False)",
         r="""
             t <- t.test(extra[group == "drug 1"], extra[group == "drug 2"])
             list(t = unname(t$statistic), `degrees of freedom` = unname(t$parameter), `p-value` = t$p.value)
         """,
         note="Student printed the standard deviations with n in the divisor (1.70 and 1.90); simplydata, NumPy "
              "with ddof=1, and R use n - 1 (1.79 and 2.00). This is a documented choice, not a difference in "
              "the data. simplydata's difference is drug 1 minus drug 2, so Student's +1.58 is -1.58 here."),
    # ---- the chart words, on real data: the drawn numbers against the parent package
    Case("draw_bars", "bar heights are Student's two averages", "Student's sleep data", "published",
         ours="""
             from simplydata._underneath.check import chart_facts
             ax = sdata.chart(data).draw_bars(x="group", y="extra")._render().axes[0]
             {"bar 1": chart_facts(ax)["bars"][0][3], "bar 2": chart_facts(ax)["bars"][1][3]}
         """,
         published={"bar 1": (0.75, 0.005, "Student (1908)"), "bar 2": (2.33, 0.005, "Student (1908)")},
         parent="""
             import matplotlib.pyplot as plt
             import seaborn as sns
             from simplydata._underneath.check import chart_facts
             fig, ax = plt.subplots()
             sns.barplot(data, x="group", y="extra", errorbar=None, ax=ax)
             {"bar 1": chart_facts(ax)["bars"][0][3], "bar 2": chart_facts(ax)["bars"][1][3]}
         """, parent_label="seaborn barplot"),
    Case("draw_histogram", "Michelson's speed of light in 10 bins", "NIST Michelso", "real data",
         ours="""
             from simplydata._underneath.check import chart_facts
             ax = sdata.chart(data).draw_histogram(x="y")._render().axes[0]
             bars = chart_facts(ax)["bars"]
             {f"bin {i + 1}": b[3] for i, b in enumerate(bars)} | {"first edge": bars[0][0],
                                                                   "last edge": bars[-1][0] + bars[-1][2]}
         """,
         parent="""
             import numpy as np
             counts, edges = np.histogram(data["y"], bins=10)
             {f"bin {i + 1}": c for i, c in enumerate(counts)} | {"first edge": edges[0], "last edge": edges[-1]}
         """, parent_label="NumPy histogram (bins=10)",
         r="""
             h <- hist(y, breaks = seq(min(y), max(y), length.out = 11), plot = FALSE, right = FALSE,
                       include.lowest = TRUE)
             counts <- h$counts
             out <- as.list(counts)
             names(out) <- paste("bin", seq_along(counts))
             out
         """),
    Case("draw_dots", "the 36 Norris calibration points", "NIST Norris", "real data",
         ours="""
             from simplydata._underneath.check import chart_facts
             ax = sdata.chart(data).draw_dots(x="x", y="y")._render().axes[0]
             dots = chart_facts(ax)["dots"]
             {"dots": len(dots), "sum of x": sum(d[0] for d in dots), "sum of y": sum(d[1] for d in dots)}
         """,
         parent="""
             {"dots": len(data), "sum of x": data["x"].sum(), "sum of y": data["y"].sum()}
         """, parent_label="the data themselves (every point drawn once)"),
    # ---- the R word: real published data, against R pROC itself
    Case("trade_off_curve", "ROC curve of s100b for a poor outcome", "aSAH (pROC)", "real data",
         ours="""
             from simplydata._underneath.check import chart_facts
             ax = sdata.chart(data).trade_off_curve(score="s100b", truth="outcome",
                                                    positive="Poor")._render().axes[0]
             x, y = chart_facts(ax)["lines"][0]
             {"points": len(x), "area under the drawn curve": float(np.trapezoid(y, x))}
         """,
         r="""
             r <- pROC::roc(as.numeric(outcome == "Poor"), s100b, levels = c(0, 1), direction = "<", quiet = TRUE)
             p <- pROC::coords(r, "all", ret = c("specificity", "sensitivity"), transpose = FALSE)
             list(points = nrow(p), `area under the drawn curve` = as.numeric(pROC::auc(r)))
         """, r_packages=("pROC",), r_tolerance=1e-9,
         note="The area under the drawn curve (trapezoids) must equal pROC's AUC: the curve has every point."),
    # ---- keep_rows_where: real data, against pandas and R
    Case("table.keep_rows_where", "Michelson's measurements above 299.9 (in thousands of km per second)",
         "NIST Michelso", "real data",
         ours="""
             kept = sdata.table(data).keep_rows_where("y", is_above=299.9).as_pandas()
             {"rows kept": len(kept), "sum kept": kept["y"].sum(), "smallest kept": kept["y"].min()}
         """,
         parent="""
             kept = data[data["y"] > 299.9]
             {"rows kept": len(kept), "sum kept": kept["y"].sum(), "smallest kept": kept["y"].min()}
         """, parent_label="pandas boolean indexing", parent_tolerance=1e-12,
         r="""
             kept <- y[y > 299.9]
             list(`rows kept` = length(kept), `sum kept` = sum(kept), `smallest kept` = min(kept))
         """, r_tolerance=1e-12),
    # ---- made-up edge cases
    Case("table.find_average_of", "an empty cell is skipped", "made-up", "made-up",
         ours="""
             data = pd.DataFrame({"y": [1.0, None, 3.0, 8.0]})
             {"mean": sdata.table(data).find_average_of("y")}
         """,
         parent="""
             import numpy as np
             {"mean": np.nanmean([1.0, np.nan, 3.0, 8.0])}
         """, parent_label="NumPy nanmean", parent_tolerance=1e-15),
    Case("table.keep_rows_where", "an empty cell is not above 2, and no row is left when none is above 50", "made-up",
         "made-up",
         ours="""
             data = pd.DataFrame({"a": [1.0, None, 3.0, 7.0]})
             kept = sdata.table(data).keep_rows_where("a", is_above=2).as_pandas()
             none = sdata.table(data).keep_rows_where("a", is_above=50).as_pandas()
             {"rows kept": len(kept), "sum kept": kept["a"].sum(), "rows when none is above": len(none)}
         """,
         parent="""
             data = pd.DataFrame({"a": [1.0, None, 3.0, 7.0]})
             kept = data[data["a"] > 2]
             {"rows kept": len(kept), "sum kept": kept["a"].sum(), "rows when none is above": len(data[data["a"] > 50])}
         """, parent_label="pandas boolean indexing", parent_tolerance=0.0),
    Case("table.fit_line", "points exactly on y = 2 x + 1", "made-up", "made-up",
         ours="""
             data = pd.DataFrame({"x": [1.0, 2, 3, 4], "y": [3.0, 5, 7, 9]})
             r = sdata.table(data).fit_line(x="x", y="y").as_pandas().iloc[0]
             {"slope": r["slope"], "intercept": r["intercept"], "R squared": r["R squared"]}
         """,
         published={"slope": (2.0, 1e-12, "exact"), "intercept": (1.0, 1e-12, "exact"),
                    "R squared": (1.0, 1e-12, "exact")}),
    Case("dist.find_chance_that_value", "chance above 1.96 in the standard normal distribution",
         "standard normal table", "published",
         ours="""
             {"chance above 1.96": sdata.distribution("normal", average=0, standard_deviation=1)
                                    .find_chance_that_value(is_above=1.96)}
         """,
         # NIST/SEMATECH e-Handbook 1.3.6.7.1: the area from 0 to 1.96 is 0.47500, so above 1.96 is 0.5 - 0.47500
         published={"chance above 1.96": (0.025, 0.000005, "NIST/SEMATECH e-Handbook, table 1.3.6.7.1")},
         parent="""
             from scipy import stats
             {"chance above 1.96": stats.norm.sf(1.96)}
         """, parent_label="SciPy stats.norm.sf", parent_tolerance=1e-14,
         r="""
             list(`chance above 1.96` = pnorm(1.96, lower.tail = FALSE))
         """, r_tolerance=1e-14,
         note="No data: the published value is the standard normal table (5 decimals)."),
]
