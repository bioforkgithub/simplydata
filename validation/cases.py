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
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged.",
            "https://www.itl.nist.gov/div898/strd/lls/data/Norris.shtml"),
    Dataset("NIST Michelso", "nist/Michelso.dat",
            "100 measurements of the speed of light in air by Michelson (1879); certified mean and standard deviation",
            "Dorsey, E. N. (1944). The Velocity of Light. Transactions of the American Philosophical Society 34(1), "
            "1-110, Table 22. In: NIST StRD, Univariate Summary Statistics, dataset Michelso.",
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged.",
            "https://www.itl.nist.gov/div898/strd/univ/michelso.html"),
    Dataset("NIST Mavro", "nist/Mavro.dat",
            "50 filter transmittance measurements by R. Mavrodineanu (NIST); certified mean and standard deviation",
            "Mavrodineanu, R., NIST. Filter transmittance data. In: NIST StRD, Univariate Summary Statistics, "
            "dataset Mavro.",
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged.",
            "https://www.itl.nist.gov/div898/strd/univ/mavro.html"),
    Dataset("NIST NumAcc4", "nist/NumAcc4.dat",
            "1001 nine-digit numbers that differ only in the last digit; constructed by NIST to test accuracy "
            "(higher difficulty); certified mean 10000000.2 exactly",
            "Simon, S. D. & Lesage, J. P. (1989). Assessing the accuracy of ANOVA calculations in statistical "
            "software. Computational Statistics & Data Analysis 8, 325-332. In: NIST StRD, dataset NumAcc4.",
            "Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored unchanged.",
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
    Dataset("Galton's sweet peas", "galton_peas.csv",
            "7 parent sweet-pea seed diameters (hundredths of an inch), each with the average and the standard "
            "deviation of the diameters of its offspring seeds",
            "Galton, F. (1877). Typical laws of heredity. Nature 15, 492-495, 512-514, 532-533. Used for weighted "
            "least squares in Weisberg, S. (2014). Applied Linear Regression, 4th ed., Wiley, section 7.1. Copy from "
            "the R package alr4 (galtonpeas).",
            "Published 1877 (public domain); the alr4 copy is GPL (>= 2).",
            "https://cran.r-project.org/package=alr4"),
    Dataset("Orobanche seeds", "crowder_seeds.csv",
            "21 plates of seeds of two Orobanche varieties (O73, O75) on bean or cucumber root extract: the seeds "
            "that germinated, out of the seeds on the plate",
            "Crowder, M. J. (1978). Beta-binomial anova for proportions. Applied Statistics 27(1), 34-37. Copy from "
            "the R package agridat (crowder.seeds; Wright, K.), through Rdatasets.",
            "The published counts (facts from a 1978 paper); the agridat copy is MIT licensed.",
            "https://cran.r-project.org/package=agridat"),
    Dataset("infert", "infert.csv",
            "248 women in 83 matched sets (1 or 2 cases of secondary infertility, each with 2 controls matched on "
            "age, parity and education): earlier spontaneous and induced abortions",
            "Trichopoulos, D., Handanos, N., Danezis, J., Kalandidi, A. & Kalapothaki, V. (1976). Induced abortion "
            "and secondary infertility. British Journal of Obstetrics and Gynaecology 83, 645-650. Copy from R's "
            "datasets package (infert).",
            "Published 1976; R's datasets copy is GPL-2 | GPL-3.",
            "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/infert.html"),
    Dataset("birthwt", "birthwt.csv",
            "189 births at Baystate Medical Center, Springfield, Massachusetts (1986): low birth weight (below 2.5 "
            "kg) and the mother's age, weight, smoking, race and history",
            "Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Copy from the R package MASS "
            "(birthwt; Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed. Springer).",
            "The MASS copy is GPL-2 | GPL-3.",
            "https://cran.r-project.org/package=MASS"),
    Dataset("stackloss", "stackloss.csv",
            "21 days of a plant oxidising ammonia to nitric acid: air flow, cooling water temperature, acid "
            "concentration and the ammonia lost (stack loss)",
            "Brownlee, K. A. (1965). Statistical Theory and Methodology in Science and Engineering, 2nd ed. Wiley, "
            "pp. 491-500. Copy from R's datasets package (stackloss).",
            "Published 1960/1965; R's datasets copy is GPL-2 | GPL-3.",
            "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/stackloss.html"),
    Dataset("mtcars", "mtcars.csv",
            "32 cars (1973-74 models): fuel use (miles per gallon) and 10 design and performance measures",
            "Henderson, H. V. & Velleman, P. F. (1981). Building multiple regression models interactively. "
            "Biometrics 37, 391-411 (data from Motor Trend, 1974). Copy from R's datasets package (mtcars).",
            "Published 1974 and 1981; R's datasets copy is GPL-2 | GPL-3.",
            "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/mtcars.html"),
    Dataset("VerbAgg", "verbagg.csv",
            "verbal aggression: 316 people each answered 24 items (would they curse, scold or shout in a "
            "frustrating situation?), yes or no; people and items are crossed",
            "De Boeck, P. & Wilson, M. (2004). Explanatory Item Response Models. Springer (data collected by "
            "Vansteelandt, 2000). Copy from the R package lme4 (VerbAgg).",
            "The lme4 copy is GPL (>= 2).",
            "https://cran.r-project.org/package=lme4"),
    Dataset("NMES 1988", "nmes1988.csv",
            "4406 people aged 66 and over in the US National Medical Expenditure Survey 1987/88: physician office "
            "visits, hospital stays, self-rated health, chronic conditions, gender, years of school and private "
            "insurance (7 of the 19 columns)",
            "Deb, P. & Trivedi, P. K. (1997). Demand for medical care by the elderly: a finite mixture approach. "
            "Journal of Applied Econometrics 12, 313-336. Analysed with hurdle and zero-inflated models in Zeileis, "
            "A., Kleiber, C. & Jackman, S. (2008). Regression models for count data in R. Journal of Statistical "
            "Software 27(8), 1-25. Copy from the R package AER (NMES1988), through Rdatasets.",
            "A US Government survey (public domain); the AER copy is GPL-2 | GPL-3; the JSS article is CC BY.",
            "https://www.jstatsoft.org/v027/i08"),
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
    option: str = ""              # the option the case checks ("weights="); empty for the word itself
    ours_r: tuple | None = None   # R packages simplydata's own side runs (None: it needs no R); skipped without them


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
         note="These data are paired: each patient took both drugs, and Student (1908) analysed the difference "
              "within each patient (the paired case below). This case treats the two drugs as two separate groups "
              "only to check the arithmetic of the two-group (Welch) test against SciPy and R; it is not the right "
              "analysis of these data. Student printed the standard deviations with n in the divisor (1.70 and "
              "1.90); simplydata, NumPy with ddof=1, and R use n - 1 (1.79 and 2.00), a documented choice. "
              "simplydata's difference is drug 1 minus drug 2, so Student's +1.58 is -1.58 here."),
    Case("table.compare_before_and_after", "two drugs in the same 10 patients (paired t-test, as Student analysed "
                                           "them)", "Student's sleep data", "published",
         ours="""
             wide = data.pivot(index="ID", columns="group", values="extra").reset_index()
             r = sdata.table(wide).compare_before_and_after("drug 1", "drug 2").as_pandas().iloc[0]
             {"average change": r["average change"], "t": r["statistic"],
              "degrees of freedom": r["degrees of freedom"], "p-value": r["p-value"]}
         """,
         # Student (1908) prints the average difference within patients, +1.58 hours (drug 2 minus drug 1)
         published={"average change": (1.58, 0.005, "Student (1908)")},
         parent="""
             from scipy import stats
             wide = data.pivot(index="ID", columns="group", values="extra")
             t = stats.ttest_rel(wide["drug 2"], wide["drug 1"])
             {"average change": (wide["drug 2"] - wide["drug 1"]).mean(), "t": t.statistic,
              "degrees of freedom": t.df, "p-value": t.pvalue}
         """, parent_label="SciPy stats.ttest_rel",
         r="""
             t <- t.test(extra[group == "drug 2"][order(ID[group == "drug 2"])],
                         extra[group == "drug 1"][order(ID[group == "drug 1"])], paired = TRUE)
             list(t = unname(t$statistic), `degrees of freedom` = unname(t$parameter), `p-value` = t$p.value)
         """,
         note="Student also printed the standard deviation of the differences, 1.17, with n in the divisor; with "
              "n - 1 it is 1.23. simplydata does not print it, so it is not compared."),
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
             {"points": len(x), "area under the drawn curve": float(np.sum(np.diff(x) * (y[1:] + y[:-1]) / 2))}
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


# ---------------------------------------------------------------- S3a-1: explain() grows (one case per option)
def _rows(result, part=None):
    """The rows of explain()'s result table by their term (and part, for the two-part models): r["hours"]["effect"].
    The cases run with it as _rows."""
    frame = result.as_pandas()
    if part is not None:
        frame = frame[frame["part"] == part]
    return {r["term"]: r for r in frame.to_dict("records")}


CASES += [
    Case("table.explain", "weighted least squares: offspring diameter from the parent's, each row weighted by "
                          "1 / its variance", "Galton's sweet peas", "real data", option="weights=",
         ours="""
             r = _rows(sdata.table(data.assign(w=1 / data["sd"] ** 2)).explain("progeny", using=["parent"],
                                                                                         weights="w"))
             {"slope": r["parent"]["effect"], "slope standard error": r["parent"]["standard error"],
              "intercept": r["(intercept)"]["effect"]}
         """,
         parent="""
             import statsmodels.api as sm
             f = sm.WLS(data["progeny"], sm.add_constant(data["parent"]), weights=1 / data["sd"] ** 2).fit()
             {"slope": f.params.iloc[1], "slope standard error": f.bse.iloc[1], "intercept": f.params.iloc[0]}
         """, parent_label="statsmodels WLS",
         r="""
             f <- summary(lm(progeny ~ parent, weights = 1 / sd^2))
             list(slope = coef(f)[2, 1], `slope standard error` = coef(f)[2, 2], intercept = coef(f)[1, 1])
         """,
         note="Weisberg (2014, section 7.1) fits this weighted line; the numbers are checked against statsmodels "
              "and R rather than the book's printed table."),
    Case("table.explain", "quasi-binomial: seeds that germinated out of seeds, by variety and root extract",
         "Orobanche seeds", "real data", option='outcome="yes or no (overdispersed)"',
         ours="""
             r = _rows(sdata.table(data).explain("germ", using=["gen * extract"],
                                                         outcome="yes or no (overdispersed)", out_of="n"))
             {"extract": r["extract (cucumber)"]["log odds ratio"],
              "extract standard error": r["extract (cucumber)"]["standard error"],
              "interaction standard error": r["gen (O75) : extract (cucumber)"]["standard error"],
              "interaction p-value": r["gen (O75) : extract (cucumber)"]["p-value"]}
         """,
         parent="""
             import statsmodels.api as sm
             X = sm.add_constant(pd.DataFrame({"g": (data["gen"] == "O75") * 1.0, "e": (data["extract"] == "cucumber") * 1.0}))
             X["ge"] = X["g"] * X["e"]
             f = sm.GLM(data["germ"] / data["n"], X, family=sm.families.Binomial(), var_weights=data["n"]).fit(scale="X2")
             {"extract": f.params.iloc[2], "extract standard error": f.bse.iloc[2],
              "interaction standard error": f.bse.iloc[3]}
         """, parent_label="statsmodels GLM (Binomial, scale X2)", parent_tolerance=1e-7,
         r="""
             s <- summary(glm(cbind(germ, n - germ) ~ gen * extract, family = quasibinomial))$coefficients
             list(extract = s[3, 1], `extract standard error` = s[3, 2], `interaction standard error` = s[4, 2],
                  `interaction p-value` = s[4, 4])
         """, r_tolerance=1e-6,
         note="Crowder (1978) fitted a beta-binomial model; the quasi-binomial fit of the same data (Collett 2003, "
              "Modelling Binary Data) is checked here against statsmodels and R."),
    Case("table.explain", "conditional logistic regression: infertility and earlier abortions in matched sets",
         "infert", "real data", option="matched_by=",
         ours="""
             r = _rows(sdata.table(data).explain("case", using=["spontaneous", "induced"], outcome="yes or no",
                                                         matched_by="stratum"))
             {"spontaneous": r["spontaneous"]["log odds ratio"], "induced": r["induced"]["log odds ratio"],
              "spontaneous standard error": r["spontaneous"]["standard error"],
              "induced standard error": r["induced"]["standard error"]}
         """,
         parent="""
             from statsmodels.discrete.conditional_models import ConditionalLogit
             f = ConditionalLogit(data["case"], data[["spontaneous", "induced"]], groups=data["stratum"]).fit(
                 method="newton", disp=0)
             {"spontaneous": f.params.iloc[0], "induced": f.params.iloc[1],
              "spontaneous standard error": f.bse.iloc[0], "induced standard error": f.bse.iloc[1]}
         """, parent_label="statsmodels ConditionalLogit", parent_tolerance=1e-7,
         r="""
             suppressPackageStartupMessages(library(survival))  # clogit calls coxph() and strata() by their plain names
             s <- summary(survival::clogit(case ~ spontaneous + induced + strata(stratum), method = "exact"))
             list(spontaneous = s$coefficients[1, 1], induced = s$coefficients[2, 1],
                  `spontaneous standard error` = s$coefficients[1, 3], `induced standard error` = s$coefficients[2, 3])
         """, r_packages=("survival",), r_tolerance=1e-6,
         note="The model of R's ?clogit example; R and statsmodels both use the exact conditional likelihood."),
    Case("table.explain", "risk ratio of low birth weight for smokers equals the 2 x 2 table's", "birthwt", "real data",
         option='show="risk ratios"',
         ours="""
             one = _rows(sdata.table(data).explain("low", using=["smoke"], outcome="yes or no",
                                                           show="risk ratios"))
             two = _rows(sdata.table(data).explain("low", using=["smoke", "age"], outcome="yes or no",
                                                           show="risk ratios"))
             {"risk ratio, smoking alone": one["smoke"]["risk ratio"], "log risk ratio with age": two["smoke"]["log risk ratio"],
              "standard error with age": two["smoke"]["standard error"]}
         """,
         parent="""
             import statsmodels.api as sm
             from statsmodels.stats.contingency_tables import Table2x2
             t = Table2x2([[((data["smoke"] == s) & (data["low"] == v)).sum() for v in (1, 0)] for s in (1, 0)])
             f = sm.GLM(data["low"], sm.add_constant(data[["smoke", "age"]]), family=sm.families.Poisson()).fit(
                 cov_type="HC0", tol=1e-12)
             {"risk ratio, smoking alone": t.riskratio, "log risk ratio with age": f.params.iloc[1],
              "standard error with age": f.bse.iloc[1]}
         """, parent_label="statsmodels Table2x2 and GLM (Poisson, HC0)", parent_tolerance=1e-6,
         r="""
             m <- glm(low ~ smoke + age, family = poisson)
             list(`log risk ratio with age` = coef(m)[2],
                  `standard error with age` = sqrt(diag(sandwich::vcovHC(m, type = "HC0")))[2])
         """, r_packages=("sandwich",), r_tolerance=1e-6,
         note="With one yes/no column, the modified Poisson risk ratio is the risk ratio of the 2 x 2 table "
              "(Zou 2004), here from statsmodels' Table2x2."),
    Case("table.explain", "log-binomial risk ratio of low birth weight", "birthwt", "real data",
         option='method="log-binomial"',
         ours="""
             r = _rows(sdata.table(data).explain("low", using=["smoke", "age"], outcome="yes or no",
                                                         show="risk ratios", method="log-binomial"))
             {"log risk ratio": r["smoke"]["log risk ratio"], "standard error": r["smoke"]["standard error"]}
         """,
         r="""
             m <- glm(low ~ smoke + age, family = binomial(link = "log"))
             list(`log risk ratio` = coef(m)[2], `standard error` = sqrt(diag(vcov(m)))[2])
         """, r_tolerance=1e-5),
    Case("table.explain", "Huber's robust regression of stack loss", "stackloss", "real data",
         option="giving_outliers_less_weight=",
         ours="""
             r = _rows(sdata.table(data).explain("stack_loss", using=["air_flow", "water_temp", "acid_conc"],
                                                         giving_outliers_less_weight=True))
             {"air flow": r["air_flow"]["effect"], "water temperature": r["water_temp"]["effect"],
              "acid concentration": r["acid_conc"]["effect"], "intercept": r["(intercept)"]["effect"],
              "air flow standard error": r["air_flow"]["standard error"]}
         """,
         parent="""
             import statsmodels.api as sm
             X = sm.add_constant(data[["air_flow", "water_temp", "acid_conc"]])
             f = sm.RLM(data["stack_loss"], X, M=sm.robust.norms.HuberT()).fit(scale_est="mad", cov="H1",
                                                                               maxiter=200, tol=1e-10)
             {"air flow": f.params.iloc[1], "water temperature": f.params.iloc[2], "acid concentration": f.params.iloc[3],
              "intercept": f.params.iloc[0], "air flow standard error": f.bse.iloc[1]}
         """, parent_label="statsmodels RLM (HuberT)",
         r="""
             m <- MASS::rlm(stack_loss ~ air_flow + water_temp + acid_conc, acc = 1e-12, maxit = 200)
             list(`air flow` = coef(m)[2], `water temperature` = coef(m)[3], `acid concentration` = coef(m)[4],
                  intercept = coef(m)[1])
         """, r_packages=("MASS",), r_tolerance=1e-5,
         note="Venables & Ripley (2002, chapter 6) fit rlm() to these data. The estimates agree with R to the "
              "stopping rules of the two fits; the standard errors are statsmodels' (Huber's H1), which differ from "
              "R's summary(rlm) in the third digit, so R's are not compared."),
    Case("table.explain", "a natural spline with 3 knots through the 36 Norris calibration points", "NIST Norris",
         "real data", option="with_knots=",
         ours="""
             r = _rows(sdata.table(data).explain("y", using=["x"], curve_for="x", with_knots=3))
             {"F of the whole curve": r["x (whole curve)"]["statistic"], "intercept": r["(intercept)"]["effect"]}
         """,
         parent="""
             import statsmodels.api as sm
             from patsy import dmatrix
             knots = np.quantile(data["x"], [0.25, 0.5, 0.75])
             B = np.asarray(dmatrix("cr(x, knots=knots, constraints='center') - 1", {"x": data["x"], "knots": knots}))
             f = sm.OLS(data["y"].to_numpy(), sm.add_constant(B)).fit()
             {"F of the whole curve": f.fvalue}
         """, parent_label="patsy cr() and statsmodels OLS",
         r="""
             f <- lm(y ~ splines::ns(x, df = 4))
             list(`F of the whole curve` = summary(f)$fstatistic[1])
         """, r_tolerance=1e-8,
         note="The spline's own coefficients differ between patsy and R's ns() (another basis of the same curves); "
              "the test of the whole curve and the fitted values are the same, so those are compared."),
    Case("table.explain", "standardised effects of weight, horsepower and gearbox on fuel use", "mtcars", "real data",
         option='show="standardised effects"',
         ours="""
             r = _rows(sdata.table(data).explain("mpg", using=["wt", "hp", "am"], show="standardised effects"))
             {"weight": r["wt"]["effect"], "horsepower": r["hp"]["effect"], "gearbox": r["am"]["effect"],
              "weight 95 % CI low": r["wt"]["95 % CI low"]}
         """,
         parent="""
             import statsmodels.api as sm
             z = (data[["mpg", "wt", "hp", "am"]] - data[["mpg", "wt", "hp", "am"]].mean()) / data[["mpg", "wt", "hp", "am"]].std()
             f = sm.OLS(z["mpg"], sm.add_constant(z[["wt", "hp", "am"]])).fit()
             {"weight": f.params.iloc[1], "horsepower": f.params.iloc[2], "gearbox": f.params.iloc[3],
              "weight 95 % CI low": f.conf_int().iloc[1, 0]}
         """, parent_label="statsmodels OLS on z-scores",
         r="""
             e <- effectsize::standardize_parameters(lm(mpg ~ wt + hp + am), method = "refit")
             list(weight = e$Std_Coefficient[2], horsepower = e$Std_Coefficient[3], gearbox = e$Std_Coefficient[4],
                  `weight 95 % CI low` = e$CI_low[2])
         """, r_packages=("effectsize",), r_tolerance=1e-8),
    Case("table.explain", "bootstrap intervals of the air-flow effect on stack loss", "stackloss", "real data",
         option='interval_by="bootstrap"',
         ours="""
             r = _rows(sdata.table(data).explain("stack_loss", using=["air_flow"], interval_by="bootstrap",
                                                         resamples=9999, with_seed=1))
             {"95 % CI low": r["air_flow"]["95 % CI low"], "95 % CI high": r["air_flow"]["95 % CI high"]}
         """,
         parent="""
             import statsmodels.api as sm
             from scipy import stats
             X, y = sm.add_constant(data["air_flow"]).to_numpy(), data["stack_loss"].to_numpy()
             res = stats.bootstrap((np.arange(len(y)),), lambda i: sm.OLS(y[i], X[i]).fit().params, n_resamples=9999,
                                   method="BCa", vectorized=False, rng=np.random.default_rng(1))
             {"95 % CI low": res.confidence_interval.low[1], "95 % CI high": res.confidence_interval.high[1]}
         """, parent_label="SciPy stats.bootstrap (BCa)",
         r="""
             set.seed(1)
             b <- boot::boot(data.frame(y = stack_loss, x = air_flow), function(d, i) coef(lm(y ~ x, data = d[i, ]))[2],
                             R = 9999)
             ci <- boot::boot.ci(b, type = "bca")$bca
             list(`95 % CI low` = ci[4], `95 % CI high` = ci[5])
         """, r_packages=("boot",), r_tolerance=0.05,
         note="R draws other random rows than SciPy, so R is a check of the same method within Monte Carlo error "
              "(5 %); SciPy with the same seed gives the same interval exactly."),
    Case("table.explain", "profile-likelihood intervals of a logistic regression of low birth weight", "birthwt",
         "real data", option='interval_by="profile"', ours_r=(),
         ours="""
             r = _rows(sdata.table(data).explain("low", using=["smoke", "age", "lwt"], outcome="yes or no",
                                                         interval_by="profile"))
             {"smoke low": np.log(r["smoke"]["95 % CI low"]), "smoke high": np.log(r["smoke"]["95 % CI high"]),
              "lwt low": np.log(r["lwt"]["95 % CI low"])}
         """,
         r="""
             ci <- confint(glm(low ~ smoke + age + lwt, family = binomial))
             list(`smoke low` = ci[2, 1], `smoke high` = ci[2, 2], `lwt low` = ci[4, 1])
         """, r_tolerance=1e-6,
         note="simplydata runs R's confint() itself (statsmodels has no profile intervals); this case checks that "
              "the model R gets is the model explain() fits, from the formula side."),
    Case("table.explain", "likelihood-ratio tests in a logistic regression of low birth weight", "birthwt",
         "real data", option='p_value_by="likelihood ratio"',
         ours="""
             r = _rows(sdata.table(data).explain("low", using=["smoke", "age", "lwt"], outcome="yes or no",
                                                         p_value_by="likelihood ratio"))
             {"smoke": r["smoke"]["p-value"], "age": r["age"]["p-value"], "lwt": r["lwt"]["p-value"]}
         """,
         parent="""
             import statsmodels.api as sm
             from scipy import stats
             X = sm.add_constant(data[["smoke", "age", "lwt"]])
             full = sm.GLM(data["low"], X, family=sm.families.Binomial()).fit()
             out = {}
             for c in ("smoke", "age", "lwt"):
                 small = sm.GLM(data["low"], X.drop(columns=c), family=sm.families.Binomial()).fit()
                 out[c] = stats.chi2.sf(small.deviance - full.deviance, 1)
             out
         """, parent_label="statsmodels GLM refits and SciPy chi2", parent_tolerance=1e-8,
         r="""
             d <- drop1(glm(low ~ smoke + age + lwt, family = binomial), test = "LRT")
             list(smoke = d[["Pr(>Chi)"]][2], age = d[["Pr(>Chi)"]][3], lwt = d[["Pr(>Chi)"]][4])
         """, r_tolerance=1e-7),
    Case("table.explain", "Nagelkerke's and Tjur's pseudo R squared of a logistic regression of low birth weight",
         "birthwt", "real data",
         ours="""
             import contextlib, io, re
             printed = io.StringIO()
             with contextlib.redirect_stdout(printed):
                 sdata.table(data).explain("low", using=["smoke", "age", "lwt"], outcome="yes or no")
             found = re.search(r"Nagelkerke ([0-9.]+), Tjur ([0-9.]+)", printed.getvalue())
             {"Nagelkerke": float(found.group(1)), "Tjur": float(found.group(2))}
         """,
         r="""
             m <- glm(low ~ smoke + age + lwt, family = binomial)
             list(Nagelkerke = performance::r2_nagelkerke(m)[[1]], Tjur = performance::r2_tjur(m)[[1]])
         """, r_packages=("performance",), r_tolerance=0.01,
         note="The two measures are printed with 3 decimals, so the check allows that rounding (1 % here)."),
    Case("table.explain", "people and items crossed: verbal aggression (yes or no) from anger and gender",
         "VerbAgg", "real data", option="crossed_with=", ours_r=("lme4",),
         ours="""
             r = _rows(sdata.table(data).explain("r2", using=["anger", "gender", "btype"], outcome="yes or no",
                                                         grouped_by="id", crossed_with="item"))
             {"anger": r["anger"]["log odds ratio"], "anger standard error": r["anger"]["standard error"],
              "gender": r["gender (M)"]["log odds ratio"]}
         """,
         r="""
             id <- factor(as.character(id)); item <- factor(as.character(item))
             m <- lme4::glmer(r2 == "Y" ~ anger + gender + btype + (1 | id) + (1 | item), family = binomial)
             list(anger = lme4::fixef(m)[2], `anger standard error` = sqrt(diag(as.matrix(vcov(m))))[2],
                  gender = lme4::fixef(m)[3])
         """, r_packages=("lme4",), r_tolerance=1e-6,
         note="simplydata runs lme4 itself (statsmodels cannot fit crossed groupings); this case checks the model "
              "R gets from explain() against R's own formula. simplydata hands the groups to R as text, so their "
              "order is that of text (\"1\", \"10\", \"100\" ...); R's reference does the same. A user's own R "
              "run on the whole-number ids orders them as numbers, and its glmer standard errors (from a numerical "
              "Hessian) then differ in the fourth digit."),
    Case("table.explain", "two-step (hurdle) model of physician office visits", "NMES 1988", "published",
         option='outcome="counts in two steps"', ours_r=("pscl",),
         ours="""
             t = sdata.table(data).explain("visits", using=["hospital", "health", "chronic", "gender", "school",
                                                            "insurance"], outcome="counts in two steps that vary a lot")
             c, z = _rows(t, "count"), _rows(t, "more than 0")
             {"count: hospital": c["hospital"]["log ratio"], "count: health poor": c["health (poor)"]["log ratio"],
              "count: chronic": c["chronic"]["log ratio"], "count: chronic standard error": c["chronic"]["standard error"],
              "zero: chronic": z["chronic"]["log ratio"], "zero: insurance": z["insurance (yes)"]["log ratio"],
              "zero: insurance standard error": z["insurance (yes)"]["standard error"]}
         """,
         # Zeileis, Kleiber & Jackman (2008), summary(fm_hurdle0), printed with 6 decimals
         published={"count: hospital": (0.211898, 5e-7, "Zeileis et al. (2008)"),
                    "count: health poor": (0.315958, 5e-7, "Zeileis et al. (2008)"),
                    "count: chronic": (0.126421, 5e-7, "Zeileis et al. (2008)"),
                    "count: chronic standard error": (0.012452, 5e-7, "Zeileis et al. (2008)"),
                    "zero: chronic": (0.535213, 5e-7, "Zeileis et al. (2008)"),
                    "zero: insurance": (0.747120, 5e-7, "Zeileis et al. (2008)"),
                    "zero: insurance standard error": (0.100880, 5e-7, "Zeileis et al. (2008)")},
         note="The paper's model fm_hurdle0: a negative binomial count part and a logistic zero hurdle, the same "
              "columns in both."),
    Case("table.explain", "zero-inflated negative binomial model of physician office visits, the zero part with its "
                          "own columns", "NMES 1988", "published",
         option='outcome="counts with many zeros that vary a lot"', ours_r=("pscl",),
         ours="""
             t = sdata.table(data).explain("visits", using=["hospital", "health", "chronic", "gender", "school",
                                                            "insurance"], outcome="counts with many zeros that vary a lot",
                                           zero_part_using=["hospital", "chronic", "insurance", "school", "gender"])
             c, z = _rows(t, "count"), _rows(t, "extra zeros")
             {"count: hospital": c["hospital"]["log ratio"], "count: health poor": c["health (poor)"]["log ratio"],
              "zero: hospital": z["hospital"]["log ratio"], "zero: chronic": z["chronic"]["log ratio"],
              "zero: gender male": z["gender (male)"]["log ratio"]}
         """,
         # Zeileis, Kleiber & Jackman (2008), Table 2, fm_zinb, printed with 3 decimals
         published={"count: hospital": (0.201, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "count: health poor": (0.285, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: hospital": (-0.800, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: chronic": (-1.248, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: gender male": (0.648, 5e-4, "Zeileis et al. (2008), Table 2")},
         parent="""
             import statsmodels.api as sm
             from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP
             X = sm.add_constant(pd.DataFrame({"h": data["hospital"], "p": data["health"] == "poor",
                                               "e": data["health"] == "excellent", "c": data["chronic"],
                                               "m": data["gender"] == "male", "s": data["school"],
                                               "i": data["insurance"] == "yes"}).astype(float))
             Z = X[["const", "h", "c", "i", "s", "m"]]
             model = ZeroInflatedNegativeBinomialP(data["visits"], X, exog_infl=Z, p=2)
             f = model.fit(start_params=model.fit(method="bfgs", maxiter=2000, disp=0).params, method="newton",
                           maxiter=100, disp=0)
             {"count: hospital": f.params.iloc[7], "zero: hospital": f.params.iloc[1], "zero: chronic": f.params.iloc[2]}
         """, parent_label="statsmodels ZeroInflatedNegativeBinomialP", parent_tolerance=1e-4,
         note="The paper's model fm_zinb (the zero part without health). simplydata runs R pscl itself, for its "
              "standard errors; statsmodels gives the same estimates."),
    Case("table.explain", "two-step (hurdle) model whose zero part has its own columns", "NMES 1988", "published",
         option="zero_part_using=", ours_r=("pscl",),
         ours="""
             t = sdata.table(data).explain("visits", using=["hospital", "health", "chronic", "gender", "school",
                                                            "insurance"], outcome="hurdle that vary a lot",
                                           zero_part_using=["hospital", "chronic", "insurance", "school", "gender"])
             z = _rows(t, "more than 0")
             {"zero: intercept": z["(intercept)"]["log ratio"], "zero: hospital": z["hospital"]["log ratio"],
              "zero: chronic": z["chronic"]["log ratio"], "zero: insurance": z["insurance (yes)"]["log ratio"],
              "zero: school": z["school"]["log ratio"], "zero: gender male": z["gender (male)"]["log ratio"]}
         """,
         # Zeileis, Kleiber & Jackman (2008), Table 2 and section 3.7, fm_hurdle's zero hurdle, printed with 3 decimals
         published={"zero: intercept": (0.016, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: hospital": (0.318, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: chronic": (0.548, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: insurance": (0.746, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: school": (0.057, 5e-4, "Zeileis et al. (2008), Table 2"),
                    "zero: gender male": (-0.419, 5e-4, "Zeileis et al. (2008), Table 2")},
         parent="""
             import statsmodels.api as sm
             Z = sm.add_constant(pd.DataFrame({"h": data["hospital"], "c": data["chronic"], "i": data["insurance"] == "yes",
                                               "s": data["school"], "m": data["gender"] == "male"}).astype(float))
             f = sm.Logit((data["visits"] > 0).astype(float), Z).fit(disp=0)
             {"zero: intercept": f.params.iloc[0], "zero: hospital": f.params.iloc[1], "zero: chronic": f.params.iloc[2],
              "zero: insurance": f.params.iloc[3], "zero: school": f.params.iloc[4], "zero: gender male": f.params.iloc[5]}
         """, parent_label="statsmodels Logit (the first step on its own)", parent_tolerance=1e-6,
         note="The first step of a hurdle model is a logistic regression of zero or not, so statsmodels' Logit "
              "gives the same numbers as pscl's zero hurdle."),
]


# ---------------------------------------------------------------- S3a-2: lines and curves (validation/cases_lines.py)
def _add_lines_and_curves():
    import importlib.util

    spec = importlib.util.spec_from_file_location("simplydata_validation_lines", HERE / "cases_lines.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.add_to(globals())


_add_lines_and_curves()


# ---------------------------------------------------------------- S3a-3: checking and comparing (validation/cases_checking.py)
def _add_checking_and_comparing():
    import importlib.util

    spec = importlib.util.spec_from_file_location("simplydata_validation_checking", HERE / "cases_checking.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.add_to(globals())


_add_checking_and_comparing()


# ---------------------------------------------------------------- S3b-3: survival and person-time (validation/cases_survival.py)
def _add_survival_and_person_time():
    import importlib.util

    spec = importlib.util.spec_from_file_location("simplydata_validation_survival", HERE / "cases_survival.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.add_to(globals())


_add_survival_and_person_time()
