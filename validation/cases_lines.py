"""The reliability study for phase S3a-2, lines and curves: fit_dose_response (table and chart),
find_best_power_of, fit_line(test_method=, y_error_over_x_error=, with_bends=, changes_at=), fit_curve(of_kind=),
explain(for_percentile=, changes_at=) and add_smoothed_column(test_method="loess").

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own
DATASETS and CASES and teaches load() the datasets read from R packages or from statsmodels (not stored here:
their licence is the package's, GPL, so they are read where they are published).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# datasets read from an R package at run time: name -> (R packages, R code giving a named list of columns)
R_DATA = {
    "ryegrass (drc)": (("drc",), "list(conc = drc::ryegrass$conc, rootl = drc::ryegrass$rootl)"),
    "poisons (boot)": (("boot",), "p <- boot::poisons; list(time = p$time, poison = as.character(p$poison), "
                                  "treat = as.character(p$treat))"),
    "stagnant (segmented)": (("segmented",), "e <- new.env(); utils::data('stagnant', package = 'segmented', envir = e); "
                                             "list(x = e$stagnant$x, y = e$stagnant$y)"),
    "leaflife (smatr)": (("smatr",), "list(lma = log10(smatr::leaflife$lma), longev = log10(smatr::leaflife$longev))"),
    "creatinine (mcr)": (("mcr",), "d <- stats::na.omit(mcr::creatinine); list(serum = d$serum.crea, "
                                   "plasma = d$plasma.crea)"),
}


def _datasets(Dataset):
    nist = ("Public domain in the United States (a work of the US Government, 17 U.S.C. 105); numbers stored "
            "unchanged.")
    return [
        Dataset("ryegrass (drc)", "",
                "root length of perennial ryegrass at 7 concentrations of ferulic acid (24 rows)",
                "Inderjit, Streibig, J. C. & Olofsdotter, M. (2002). Joint action of phenolic acid mixtures and its "
                "significance in allelopathy research. Physiologia Plantarum 114, 422-428. Analysed in Ritz, C., "
                "Baty, F., Streibig, J. C. & Gerhard, D. (2015). Dose-response analysis using R. PLoS ONE 10, "
                "e0146021. Shipped with the R package drc.",
                "The article (Ritz et al. 2015) is CC BY 4.0; the data are shipped with drc (GPL-2 or later). Not "
                "stored here: read from the installed drc package, so it needs R.",
                "https://doi.org/10.1371/journal.pone.0146021"),
        Dataset("Bliss beetles", "bliss.csv",
                "flour beetles killed after five hours of carbon disulphide at 8 doses (log10 mg per litre)",
                "Bliss, C. I. (1935). The calculation of the dosage-mortality curve. Annals of Applied Biology 22, "
                "134-167. Logistic fit printed in Dobson, A. J. & Barnett, A. G. (2008). An Introduction to "
                "Generalized Linear Models, 3rd ed., section 7.3.",
                "Facts published in 1935 (24 numbers), typed from the paper; not covered by copyright.",
                "https://doi.org/10.1111/j.1744-7348.1935.tb07713.x"),
        Dataset("poisons (boot)", "",
                "survival times of 48 animals: 3 poisons x 4 treatments, 4 animals each",
                "Box, G. E. P. & Cox, D. R. (1964). An analysis of transformations. Journal of the Royal "
                "Statistical Society B 26, 211-252 (Table 1; the power found is about -0.75, the reciprocal "
                "suggested). Shipped with the R package boot.",
                "Facts published in 1964; the copy in boot is GPL (Unlimited). Not stored here: read from boot, "
                "so it needs R.",
                "https://doi.org/10.1111/j.2517-6161.1964.tb00553.x"),
        Dataset("NIST Rat42", "nist/Rat42.dat",
                "pasture yield against growing time (9 points); certified 3 parameter logistic fit (NIST StRD, "
                "higher difficulty)",
                "Ratkowsky, D. A. (1983). Nonlinear Regression Modeling. New York: Marcel Dekker, pp. 61 and 88. "
                "In: NIST StRD, Nonlinear Regression, dataset Rat42.", nist,
                "https://www.itl.nist.gov/div898/strd/nls/data/ratkowsky2.shtml"),
        Dataset("NIST Misra1a", "nist/Misra1a.dat",
                "monomolecular absorption (14 points); certified fit of y = b1 (1 - exp(-b2 x)) (NIST StRD, lower "
                "difficulty)",
                "Misra, D., NIST (1978). Dental research monomolecular adsorption study. In: NIST StRD, Nonlinear "
                "Regression, dataset Misra1a.", nist,
                "https://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml"),
        Dataset("NIST BoxBOD", "nist/BoxBOD.dat",
                "biochemical oxygen demand against incubation time (6 points); certified fit of y = b1 (1 - "
                "exp(-b2 x)) (NIST StRD, higher difficulty)",
                "Box, G. P., Hunter, W. G. & Hunter, J. S. (1978). Statistics for Experimenters. New York: Wiley, "
                "pp. 483-487. In: NIST StRD, Nonlinear Regression, dataset BoxBOD.", nist,
                "https://www.itl.nist.gov/div898/strd/nls/data/boxbod.shtml"),
        Dataset("NIST Filip", "nist/Filip.dat",
                "82 observations; certified polynomial of degree 10 (NIST StRD linear regression, higher "
                "difficulty: the powers of x are nearly in proportion)",
                "Filippelli, A., NIST. In: NIST StRD, Linear Regression, dataset Filip.", nist,
                "https://www.itl.nist.gov/div898/strd/lls/data/Filip.shtml"),
        Dataset("NIST Longley", "nist/Longley.dat",
                "16 years of US macroeconomic data (1947-1962): total employment and six predictors that move almost "
                "together; certified multiple regression (NIST StRD linear regression, higher difficulty)",
                "Longley, J. W. (1967). An appraisal of least squares programs for the electronic computer from the "
                "viewpoint of the user. Journal of the American Statistical Association 62, 819-841. In: NIST StRD, "
                "Linear Regression, dataset Longley.", nist,
                "https://www.itl.nist.gov/div898/strd/lls/data/Longley.shtml"),
        *[Dataset(f"NIST {name}", f"nist/{name}.dat",
                  f"21 points (x = 0 to 20) {what}; certified polynomial of "
                  "degree 5 (NIST StRD linear regression, higher difficulty)",
                  f"Wampler, R. H. (1970). A report on the accuracy of some widely used least squares computer "
                  f"programs. Journal of the American Statistical Association 65, 549-565. In: NIST StRD, Linear "
                  f"Regression, dataset {name}.", nist,
                  f"https://www.itl.nist.gov/div898/strd/lls/data/{name}.shtml")
          for name, what in {"Wampler1": "exactly on y = 1 + x + x^2 + x^3 + x^4 + x^5 (certified standard errors 0)",
                             "Wampler2": "exactly on y = 1 + 0.1 x + 0.01 x^2 + ... + 0.00001 x^5",
                             "Wampler3": "on y = 1 + x + ... + x^5 plus noise (residual standard deviation 2360)",
                             "Wampler4": "on y = 1 + x + ... + x^5 plus larger noise (residual standard deviation "
                                         "236,000)",
                             "Wampler5": "on y = 1 + x + ... + x^5 plus noise far larger than the curve (residual "
                                         "standard deviation 23,600,000)"}.items()],
        Dataset("NIST Roszman1", "nist/Roszman1.dat",
                "quantum defects in iodine atoms (25 points); certified fit of y = b1 - b2 x - arctan(b3 / (x - b4)) "
                "/ pi (NIST StRD, average difficulty)",
                "Roszman, L., NIST (year not given). Quantum Defects for Sulfur I Atom. In: NIST StRD, Nonlinear Regression, "
                "dataset Roszman1.", nist,
                "https://www.itl.nist.gov/div898/strd/nls/data/roszman1.shtml"),
        Dataset("Puromycin (treated)", "puromycin.csv",
                "reaction velocity against substrate concentration for the enzyme treated with Puromycin (12 rows)",
                "Treloar, M. A. (1974). Effects of Puromycin on galactosyltransferase in Golgi membranes. M.Sc. "
                "thesis, University of Toronto. Fit printed in Bates, D. M. & Watts, D. G. (1988). Nonlinear "
                "Regression Analysis and Its Applications. New York: Wiley, section 2.3 (Vm 212.7, K 0.06412). "
                "Copy from R's datasets package (Puromycin).",
                "Published facts; the copy in R's datasets package is GPL-2 | GPL-3.",
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/Puromycin.html"),
        Dataset("stagnant (segmented)", "",
                "log band height against log flow rate of water over a stagnant band (28 points)",
                "Bacon, D. W. & Watts, D. G. (1971). Estimating the transition between two intersecting straight "
                "lines. Biometrika 58, 525-534. Shipped with the R package segmented.",
                "Facts published in 1971; the copy in segmented is GPL. Not stored here: read from segmented, so "
                "it needs R.",
                "https://doi.org/10.1093/biomet/58.3.525"),
        Dataset("leaflife (smatr)", "",
                "leaf mass per area and leaf lifespan of 67 plant species at four sites (log10 of both)",
                "Wright, I. J., Westoby, M. & Reich, P. B. (2002). Convergence towards higher leaf mass per area "
                "in dry and nutrient-poor habitats has different consequences for leaf life span. Journal of "
                "Ecology 90, 534-543. Used in Warton, D. I. et al. (2006). Bivariate line-fitting methods for "
                "allometry. Biological Reviews 81, 259-291. Shipped with the R package smatr.",
                "GPL-2 (smatr). Not stored here: read from smatr, so it needs R.",
                "https://cran.r-project.org/package=smatr"),
        Dataset("creatinine (mcr)", "",
                "creatinine measured in serum and in plasma of the same samples (108 complete pairs)",
                "Shipped with the R package mcr (Manuilova, E., Schuetzenmeister, A. & Model, F., Roche "
                "Diagnostics), the package's method-comparison example.",
                "GPL-3 (mcr). Not stored here: read from mcr, so it needs R.",
                "https://cran.r-project.org/package=mcr"),
        Dataset("Seatbelts", "seatbelts.csv",
                "drivers killed or seriously injured in Great Britain each month, 1969-1984; the seat-belt law "
                "from February 1983 (month 170)",
                "Harvey, A. C. & Durbin, J. (1986). The effects of seat belt legislation on British road casualties: "
                "a case study in structural time series modelling. Journal of the Royal Statistical Society A 149, "
                "187-227. Copy from R's datasets package (Seatbelts).",
                "Official UK road casualty counts published in the paper; the copy in R's datasets package is "
                "GPL-2 | GPL-3.",
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/UKDriverDeaths.html"),
        Dataset("Engel food expenditure", "",
                "household income and food expenditure of 235 Belgian working-class households (1857)",
                "Engel, E. (1857). Die Productions- und Consumptionsverhaeltnisse des Koenigreichs Sachsen. "
                "Analysed with quantile regression in Koenker, R. & Bassett, G. (1982). Robust tests for "
                "heteroscedasticity based on regression quantiles. Econometrica 50, 43-61. Copy in statsmodels "
                "(statsmodels.datasets.engel).",
                "Public domain (published 1857). Not stored here: read from statsmodels.",
                "https://www.statsmodels.org/stable/datasets/generated/engel.html"),
    ]


def read_certified_nonlinear(file: str, data_dir) -> dict[str, float]:
    """The certified values of a NIST StRD nonlinear file: b1, b2 ... and the residual sum of squares."""
    import re

    text = (data_dir / file).read_text(encoding="ascii")
    found = {name: float(value) for name, value in
             re.findall(r"^\s*(b\d+)\s*=\s*\S+\s+\S+\s+(-?\d\.\d+E[-+]\d+)", text, flags=re.M)}
    found["residual sum of squares"] = float(re.search(r"Residual Sum of Squares:\s+(\S+)", text).group(1))
    return found


def read_certified_polynomial(file: str, data_dir) -> dict[str, float]:
    """The certified estimates B0, B1 ... and their standard deviations of a NIST StRD linear file."""
    import re

    text = (data_dir / file).read_text(encoding="ascii")
    found = {}
    for name, value, sd in re.findall(r"^\s*B(\d+)\s+(\S+)\s+(\S+)\s*$", text, flags=re.M):
        found[f"b{name}"] = float(value)
        found[f"b{name} standard error"] = float(sd)
    return found


# NIST Wampler1, 3, 4 and 5: simplydata agrees with the certified values to about 8 to 9 digits on these numbers (NIST
# asks 9). Tested 2026-11-22: no existing least-squares routine gets them all past 9 digits without losing digits on
# Filip or Wampler5 (on the raw powers: LAPACK gelsd, gelsy and gelss through SciPy lstsq, NumPy's QR as R lm() fits
# them; on the mapped powers: NumPy Polynomial.fit). So they are reported as explained differences, not hidden.
WAMPLER_LIMIT = ("the fit runs on x mapped onto [-1, 1] and is turned back into the raw powers 1, x, ... x^5, which "
                 "adds rounding of about 1e-9 relative (a limit of double precision); where the points lie exactly on "
                 "the curve NIST certifies 0, so the LRE measures that rounding itself. How many digits are reached "
                 "varies with the computer's linear-algebra library (on GitHub's runners down to 8.4 on Wampler1 and "
                 "7.1 on Wampler5)")
# Every estimate and standard error of these four is listed: how many digits they reach varies with the computer's
# linear-algebra library (BLAS/LAPACK), from about 8.4 (Wampler1, macOS) and 7.1 (Wampler5, Ubuntu and Windows) on
# GitHub's runners to about 9 on Windows here, so which numbers fall short depends on the machine.
_TERMS = tuple(f"b{j}" for j in range(6)) + tuple(f"b{j} standard error" for j in range(6))
EXPLAINED_WAMPLER = {name: _TERMS for name in ("Wampler1", "Wampler3", "Wampler4", "Wampler5")}


def _cases(Case, data_dir):
    def cert(file, name):
        return (read_certified_nonlinear(file, data_dir)[name], "lre:6", "NIST certified")

    rat42, misra, boxbod = ("nist/Rat42.dat", "nist/Misra1a.dat", "nist/BoxBOD.dat")
    cases = [
        # ---- fit_dose_response: ryegrass (Ritz et al. 2015) against R drc; Bliss (1935) against the published fit
        Case("table.fit_dose_response", "ryegrass root length and ferulic acid: LL.4 curve and ED10, ED50, ED90",
             "ryegrass (drc)", "real data", ours_r=("drc",),
             ours="""
                 r = sdata.table(data).fit_dose_response(x="conc", y="rootl", doses_for_effect=[10, 50, 90])
                 t = r.as_pandas().set_index("term")["estimate"]
                 low = r.as_pandas().set_index("term")["95 % CI low"]
                 {"b": t["b (steepness)"], "c": t["c (lower limit)"], "d": t["d (upper limit)"], "ED10": t["ED10"],
                  "ED50": t["ED50"], "ED90": t["ED90"], "ED50 95 % CI low": low["ED50"]}
             """,
             parent="""
                 from scipy.optimize import curve_fit
                 def ll4(x, b, c, d, e):
                     with np.errstate(divide="ignore"):
                         return c + (d - c) / (1 + np.exp(b * (np.log(x) - np.log(e))))
                 (b, c, d, e), _ = curve_fit(ll4, data["conc"], data["rootl"], p0=[3, 0.5, 7.8, 3],
                                             xtol=1e-15, ftol=1e-15, gtol=1e-15, maxfev=100000)
                 {"b": b, "c": c, "d": d, "ED10": e * (10 / 90) ** (1 / b), "ED50": e, "ED90": e * 9 ** (1 / b)}
             """, parent_label="SciPy curve_fit of the LL.4 curve, to 1e-15 (an independent fit)",
             parent_tolerance=2e-6,
             r="""
                 m <- drc::drm(rootl ~ conc, fct = drc::LL.4(), control = drc::drmc(relTol = 1e-15))
                 e <- drc::ED(m, c(10, 50, 90), interval = "delta", display = FALSE)
                 list(b = coef(m)[1], c = coef(m)[2], d = coef(m)[3], ED10 = e[1, 1], ED50 = e[2, 1], ED90 = e[3, 1],
                      `ED50 95 % CI low` = e[2, 3])
             """, r_packages=("drc",), r_tolerance=1e-9,
             note="Python has no dose-response package with drc's ED intervals, so R drc itself gives the intervals; "
                  "SciPy curve_fit, run to 1e-15, is the independent fit of the curve. The optimum is flat (the "
                  "residual sum of squares of the two fits agrees to 1e-12), so the estimates agree to about 1e-6. "
                  "drc's default stopping rule (relTol 1e-7) stopped 1e-6 to 1.4e-5 short; simplydata asks for "
                  "1e-15. Ritz et al. (2015) analyse these data with the same LL.4 model."),
        Case("table.fit_dose_response", "Bliss's beetles: LD50 from the logistic curve on log dose (yes or no)",
             "Bliss beetles", "published", option='outcome="yes or no"', ours_r=("drc",),
             ours="""
                 data = data.assign(dose=10 ** data["log10_dose"])
                 r = sdata.table(data).fit_dose_response(x="dose", y="killed", outcome="yes or no", out_of="beetles")
                 {"LD50": r.as_pandas().set_index("term").loc["ED50", "estimate"]}
             """,
             # Dobson & Barnett (2008) print the logistic fit on log10 dose: -60.717 + 34.270 x, so LD50 = 10^(60.717 / 34.270)
             published={"LD50": (10 ** (60.717 / 34.270), 0.01, "Dobson & Barnett (2008)")},
             parent="""
                 import statsmodels.api as sm
                 X = sm.add_constant(data["log10_dose"])
                 g = sm.GLM(np.column_stack([data["killed"], data["beetles"] - data["killed"]]), X,
                            family=sm.families.Binomial()).fit()
                 {"LD50": 10 ** (-g.params["const"] / g.params["log10_dose"])}
             """, parent_label="statsmodels GLM (binomial, logit) on log10 dose", parent_tolerance=1e-6,
             r="""
                 g <- glm(cbind(killed, beetles - killed) ~ log10_dose, family = binomial)
                 list(LD50 = 10^(-coef(g)[1] / coef(g)[2]))
             """, r_tolerance=1e-6,
             note="The 2 parameter log-logistic curve with binomial errors is logistic regression on log dose, so "
                  "its LD50 is the published fit's; the tolerance allows the printed 3 decimals of the fit."),
        Case("fit_dose_response", "the drawn ryegrass curve is drc's", "ryegrass (drc)", "real data", ours_r=("drc",),
             ours="""
                 from simplydata._underneath.check import chart_facts
                 ax = sdata.chart(data).draw_dots(x="conc", y="rootl").fit_dose_response()._render().axes[0]
                 x, y = chart_facts(ax)["lines"][0]
                 {"points": len(x), "curve at the highest dose": y[-1], "curve at dose 0": y[0]}
             """,
             r="""
                 m <- drc::drm(rootl ~ conc, fct = drc::LL.4(), control = drc::drmc(relTol = 1e-15))
                 list(points = 301, `curve at the highest dose` = predict(m, data.frame(conc = max(conc))),
                      `curve at dose 0` = predict(m, data.frame(conc = 0)))
             """, r_packages=("drc",), r_tolerance=1e-9),
        # ---- find_best_power_of: Box & Cox (1964) poisons
        Case("table.find_best_power_of", "Box and Cox's poisons: the power for the two-way model", "poisons (boot)",
             "published", option="using=", ours_r=("car",),
             ours="""
                 r = sdata.table(data).find_best_power_of("time", using=["poison", "treat"]).as_pandas().iloc[0]
                 {"power": r["power"], "95 % CI low": r["95 % CI low"], "simple power": r["simple power"]}
             """,
             published={"power": (-0.75, 0.01, "Box & Cox (1964)"), "simple power": (-1.0, 0.0, "Box & Cox (1964)")},
             r="""
                 s <- summary(car::powerTransform(lm(time ~ poison + treat)))$result
                 list(power = s[1, 1], `95 % CI low` = s[1, 3], `simple power` = s[1, 2])
             """, r_packages=("car",), r_tolerance=1e-6,
             note="Box and Cox print a power of about -0.75 and suggest the reciprocal (power -1), the rate of dying."),
        Case("table.find_best_power_of", "the power of the poisons survival times on their own", "poisons (boot)",
             "real data",
             ours="""
                 r = sdata.table(data).find_best_power_of("time").as_pandas().iloc[0]
                 {"power": r["power"], "95 % CI low": r["95 % CI low"]}
             """,
             parent="""
                 from scipy import stats
                 _, power, (low, high) = stats.boxcox(data["time"], alpha=0.05)
                 {"power": power, "95 % CI low": low}
             """, parent_label="SciPy stats.boxcox(alpha=0.05)", parent_tolerance=1e-9,
             r="""
                 list(power = unname(car::powerTransform(time ~ 1)$lambda))
             """, r_packages=("car",), r_tolerance=1e-4,
             note="car::powerTransform maximises the same likelihood with another optimiser (to about 1e-5)."),
        # ---- fit_curve(of_kind=): NIST certified nonlinear fits and Bates & Watts's Puromycin
        Case("table.fit_curve", "Rat42: a logistic growth curve (NIST certified)", "NIST Rat42", "published", option='of_kind="logistic growth"',
             ours="""
                 r = sdata.table(data).fit_curve(x="x", y="y", of_kind="logistic growth").as_pandas().set_index("term")
                 e = r["estimate"]
                 {"b1": e["Asym"], "b2": e["xmid"] / e["scal"], "b3": 1 / e["scal"],
                  "residual sum of squares": r["residual standard error"].iloc[0] ** 2 * (r["rows"].iloc[0] - 3)}
             """,
             published={n: cert(rat42, n) for n in ("b1", "b2", "b3", "residual sum of squares")},
             note="NIST writes the curve as b1 / (1 + exp(b2 - b3 x)): b1 is Asym, b2 is xmid / scal and b3 is "
                  "1 / scal of R's SSlogis."),
        *[Case("table.fit_curve", f"{name}: a rise to a limit (NIST certified)", f"NIST {name}", "published", option='of_kind="rise to a limit"',
               ours="""
                   r = sdata.table(data).fit_curve(x="x", y="y", of_kind="rise to a limit").as_pandas().set_index("term")
                   e = r["estimate"]
                   {"b1": e["Asym"], "b2": np.exp(e["lrc"]),
                    "residual sum of squares": r["residual standard error"].iloc[0] ** 2 * (r["rows"].iloc[0] - 2)}
               """,
               published={n: cert(file, n) for n in ("b1", "b2", "residual sum of squares")},
               note="NIST writes the curve as b1 (1 - exp(-b2 x)): b1 is Asym and b2 is exp(lrc) of R's SSasympOrig.")
          for name, file in (("Misra1a", misra), ("BoxBOD", boxbod))],
        Case("table.fit_curve", "Filip: a polynomial of degree 10 whose powers are nearly in proportion (NIST certified)",
             "NIST Filip", "published",
             ours="""
                 r = sdata.table(data).fit_curve(x="x", y="y", of_degree=10).as_pandas()
                 {**{f"b{j}": v for j, v in enumerate(r["estimate"])},
                  **{f"b{j} standard error": v for j, v in enumerate(r["standard error"])}}
             """,
             published={n: (v, "lre", "NIST certified")
                        for n, v in read_certified_polynomial("nist/Filip.dat", data_dir).items()},
             note="The hardest NIST linear problem (condition number of the powers 1.8e15). simplydata fits on x mapped "
                  "onto [-1, 1] and turns the answer back into the raw powers with statsmodels t_test(); a QR fit on "
                  "the raw powers (simplydata 0.2.0) gave no standard errors for b5 to b10, and R lm() drops two "
                  "terms."),
        *[Case("table.fit_curve", f"{name}: a polynomial of degree 5, {what} (NIST certified)",
               f"NIST {name}", "published",
               ours="""
                   r = sdata.table(data).fit_curve(x="x", y="y", of_degree=5)
                   {**{f"b{j}": v for j, v in enumerate(r.get_column("estimate"))},
                    **{f"b{j} standard error": v for j, v in enumerate(r.get_column("standard error"))}}
               """,
               published={n: (v, "lre", "NIST certified")
                          for n, v in read_certified_polynomial(f"nist/{name}.dat", data_dir).items()},
               explained={n: WAMPLER_LIMIT for n in EXPLAINED_WAMPLER.get(name, ())},
               note="simplydata fits the powers of x mapped onto [-1, 1] (what makes Filip exact) and turns the answer "
                    "back into the raw powers with statsmodels t_test(). Where NIST certifies 0 (Wampler1 and Wampler2 "
                    "lie exactly on the curve), the LRE counts the digits of 0 that agree. A number listed as an "
                    "explained difference may fall a little short of 9 digits; the reason is given with it.")
          for name, what in {"Wampler1": "points exactly on the curve",
                             "Wampler2": "points exactly on a curve with small coefficients",
                             "Wampler3": "with noise", "Wampler4": "with large noise",
                             "Wampler5": "with noise far larger than the curve"}.items()],
        Case("table.explain", "Longley: six predictors that move almost together (NIST certified)",
             "NIST Longley", "published",
             ours="""
                 r = sdata.table(data).explain("y", using=["x1", "x2", "x3", "x4", "x5", "x6"])
                 {**{f"b{j}": v for j, v in enumerate(r.get_column("effect"))},
                  **{f"b{j} standard error": v for j, v in enumerate(r.get_column("standard error"))}}
             """,
             published={n: (v, "lre", "NIST certified")
                        for n, v in read_certified_polynomial("nist/Longley.dat", data_dir).items()},
             note="The standard errors use R summary.lm()'s inv(R) inv(R)' from the QR factor; statsmodels' own "
                  "inv(R'R) after its QR fit gave only 7.97 to 9.42 digits here."),
        Case("table.fit_formula", "Roszman1: a formula with arctan, from NIST's start 1 (NIST certified)",
             "NIST Roszman1", "published",
             ours="""
                 r = sdata.table(data).fit_formula("y = b1 - b2 * x - arctan(b3 / (x - b4)) / pi",
                                                   start={"b1": 0.1, "b2": -0.00001, "b3": 1000, "b4": -100}).as_pandas().iloc[0]
                 {"b1": r["b1"], "b2": r["b2"], "b3": r["b3"], "b4": r["b4"],
                  "residual sum of squares": r["residual standard error"] ** 2 * r["degrees of freedom"]}
             """,
             published={n: cert("nist/Roszman1.dat", n) for n in ("b1", "b2", "b3", "b4", "residual sum of squares")},
             note="arctan is NumPy's arctan in the formula reader."),
        Case("table.fit_curve", "Puromycin (treated): a Michaelis-Menten curve", "Puromycin (treated)", "published", option='of_kind="michaelis-menten"',
             ours="""
                 r = sdata.table(data).fit_curve(x="conc", y="rate", of_kind="michaelis-menten").as_pandas()
                 e = r.set_index("term")["estimate"]
                 {"Vm": e["Vm"], "K": e["K"]}
             """,
             published={"Vm": (212.7, 0.05, "Bates & Watts (1988)"), "K": (0.06412, 0.000005, "Bates & Watts (1988)")},
             r="""
                 f <- nls(rate ~ SSmicmen(conc, Vm, K))
                 list(Vm = coef(f)[1], K = coef(f)[2])
             """, r_tolerance=1e-5,
             note="R nls() stops at a relative offset of 1e-5, so it agrees to about 1e-5."),
        # ---- fit_line(method=): leaflife (SMA), creatinine (Deming, Passing-Bablok), Anscombe (Theil-Sen)
        Case("table.fit_line", "leaf lifespan against leaf mass per area: standardised major axis (log10)",
             "leaflife (smatr)", "real data", option='test_method="standardised major axis"', ours_r=("smatr",),
             ours="""
                 r = sdata.table(data).fit_line(x="lma", y="longev", test_method="standardised major axis").as_pandas().iloc[0]
                 {"slope": r["slope"], "intercept": r["intercept"], "slope 95 % CI low": r["slope 95 % CI low"]}
             """,
             r="""
                 k <- smatr::sma(longev ~ lma)$coef[[1]]
                 list(slope = k[2, 1], intercept = k[1, 1], `slope 95 % CI low` = k[2, 2])
             """, r_packages=("smatr",), r_tolerance=1e-9,
             note="Warton et al. (2006) fit these data on log scales; the slope is about 1.3."),
        Case("table.fit_line", "creatinine in plasma against serum: Deming line with y_error_over_x_error=4",
             "creatinine (mcr)", "real data", option='test_method="deming", y_error_over_x_error=', ours_r=("mcr",),
             ours="""
                 r = sdata.table(data).fit_line(x="serum", y="plasma", test_method="deming",
                                                y_error_over_x_error=4).as_pandas().iloc[0]
                 {"slope": r["slope"], "slope standard error": r["slope standard error"]}
             """,
             r="""
                 m <- mcr::mcreg(serum, plasma, error.ratio = 1 / 4, method.reg = "Deming", method.ci = "analytical")
                 list(slope = m@para[2, "EST"], `slope standard error` = m@para[2, "SE"])
             """, r_packages=("mcr",), r_tolerance=1e-9,
             note="mcr's error.ratio is the error variance of x over that of y, so 4 here is 1 / 4 there. "
                  "tests/test_s3a2_lines.py checks the direction against R deming::deming(xstd =, ystd =) too."),
        Case("table.fit_line", "creatinine in plasma against serum: Passing-Bablok line", "creatinine (mcr)",
             "real data", option='test_method="passing-bablok"', ours_r=("mcr",),
             ours="""
                 r = sdata.table(data).fit_line(x="serum", y="plasma", test_method="passing-bablok").as_pandas().iloc[0]
                 {"slope": r["slope"], "intercept": r["intercept"], "slope 95 % CI high": r["slope 95 % CI high"]}
             """,
             r="""
                 m <- mcr::mcreg(serum, plasma, method.reg = "PaBa", method.ci = "analytical")
                 list(slope = m@para[2, "EST"], intercept = m@para[1, "EST"], `slope 95 % CI high` = m@para[2, "UCI"])
             """, r_packages=("mcr",), r_tolerance=1e-9),
        Case("table.fit_line", "Anscombe's set 3 (one outlier): the Theil-Sen line", "Anscombe's quartet",
             "real data", option='test_method="theil-sen"',
             ours="""
                 r = sdata.table(data).fit_line(x="x3", y="y3", test_method="theil-sen").as_pandas().iloc[0]
                 {"slope": r["slope"], "intercept": r["intercept"], "slope 95 % CI low": r["slope 95 % CI low"]}
             """,
             parent="""
                 from scipy import stats
                 f = stats.theilslopes(data["y3"], data["x3"], alpha=0.95, method="separate")
                 {"slope": f.slope, "intercept": f.intercept, "slope 95 % CI low": f.low_slope}
             """, parent_label="SciPy stats.theilslopes", parent_tolerance=1e-12,
             r="""
                 f <- deming::theilsen(y3 ~ x3)
                 list(slope = unname(coef(f)[2]))
             """, r_packages=("deming",), r_tolerance=1e-9,
             note="The outlier pulls the least-squares slope to 0.500; the Theil-Sen slope stays near 0.345, the "
                  "slope of the other ten points."),
        # ---- fit_line(with_bends=): Bacon & Watts (1971)
        Case("table.fit_line", "Bacon and Watts's stagnant band: a line with one bend", "stagnant (segmented)",
             "real data", option="with_bends=", ours_r=("segmented",),
             ours="""
                 r = sdata.table(data).fit_line(x="x", y="y", with_bends=1).as_pandas().iloc[0]
                 {"bend 1": r["bend 1"], "slope 1": r["slope 1"], "slope 2": r["slope 2"],
                  "Davies p-value": r["Davies p-value"]}
             """,
             r="""
                 o <- lm(y ~ x)
                 s <- segmented::segmented(o, seg.Z = ~ x, npsi = 1, control = segmented::seg.control(seed = 1))
                 sl <- segmented::slope(s, digits = 15)$x
                 list(`bend 1` = s$psi[1, 2], `slope 1` = sl[1, 1], `slope 2` = sl[2, 1],
                      `Davies p-value` = segmented::davies.test(o, seg.Z = ~ x)$p.value)
             """, r_packages=("segmented",), r_tolerance=1e-9,
             note="Bacon and Watts fit a smooth transition; segmented fits the sharp bend, so R is the reference."),
        # ---- changes_at=: the British seat-belt law (Harvey & Durbin 1986)
        Case("table.fit_line", "drivers killed or seriously injured: the line changes at the seat-belt law",
             "Seatbelts", "real data", option="changes_at=",
             ours="""
                 r = sdata.table(data).fit_line(x="month", y="drivers", changes_at=170).as_pandas().iloc[0]
                 {"level change": r["level change"], "slope change": r["slope change"],
                  "level change standard error": r["level change standard error"]}
             """,
             parent="""
                 import statsmodels.formula.api as smf
                 d = data.assign(after=(data["month"] >= 170) * 1.0)
                 d = d.assign(since=d["after"] * (d["month"] - 170))
                 f = smf.ols("drivers ~ month + after + since", d).fit()
                 {"level change": f.params["after"], "slope change": f.params["since"],
                  "level change standard error": f.bse["after"]}
             """, parent_label="statsmodels OLS with the two change columns", parent_tolerance=1e-9,
             r="""
                 after <- as.numeric(month >= 170); since <- after * (month - 170)
                 f <- summary(lm(drivers ~ month + after + since))$coefficients
                 list(`level change` = f[3, 1], `slope change` = f[4, 1], `level change standard error` = f[3, 2])
             """, r_tolerance=1e-9,
             note="A plain interrupted time series without the season, to check the arithmetic; Harvey and Durbin "
                  "model the season and the trend too."),
        Case("table.explain", "drivers killed (counts): the rate ratio of the jump at the seat-belt law",
             "Seatbelts", "real data", option="changes_at=",
             ours="""
                 r = sdata.table(data).explain("DriversKilled", using=["month"], outcome="counts",
                                               changes_at={"month": 170}).as_pandas().set_index("term")
                 ratio = r.columns[0]  # the rate ratios
                 {"jump": r.loc["after month 170", ratio], "slope change": r.loc["month since 170", ratio]}
             """,
             parent="""
                 import statsmodels.api as sm
                 import statsmodels.formula.api as smf
                 d = data.assign(after=(data["month"] >= 170) * 1.0)
                 d = d.assign(since=d["after"] * (d["month"] - 170))
                 f = smf.glm("DriversKilled ~ month + after + since", d, family=sm.families.Poisson()).fit()
                 {"jump": np.exp(f.params["after"]), "slope change": np.exp(f.params["since"])}
             """, parent_label="statsmodels GLM (Poisson) with the two change columns", parent_tolerance=1e-7,
             r="""
                 after <- as.numeric(month >= 170); since <- after * (month - 170)
                 f <- glm(DriversKilled ~ month + after + since, family = poisson)
                 list(jump = exp(coef(f)[3]), `slope change` = exp(coef(f)[4]))
             """, r_tolerance=1e-7),
        # ---- explain(for_percentile=): Engel's food expenditure
        Case("table.explain", "Engel's food expenditure: the 90th percentile line", "Engel food expenditure",
             "real data", option="for_percentile=", ours_r=("quantreg",),
             ours="""
                 r = sdata.table(data).explain("foodexp", using=["income"], for_percentile=90).as_pandas()
                 r = r.set_index("term")
                 {"intercept": r.loc["(intercept)", "estimate"], "income": r.loc["income", "estimate"],
                  "income standard error": r.loc["income", "standard error"]}
             """,
             parent="""
                 import statsmodels.formula.api as smf
                 f = smf.quantreg("foodexp ~ income", data).fit(q=0.9)
                 {"intercept": f.params["Intercept"], "income": f.params["income"]}
             """, parent_label="statsmodels QuantReg (estimates only: its standard errors are not R's)",
             parent_tolerance=1e-5,
             r="""
                 s <- summary(quantreg::rq(foodexp ~ income, tau = 0.9), se = "nid")$coefficients
                 list(intercept = s[1, 1], income = s[2, 1], `income standard error` = s[2, 2])
             """, r_packages=("quantreg",), r_tolerance=1e-9,
             note="statsmodels solves by iteratively reweighted least squares and R quantreg by the exact simplex; "
                  "the lines agree to about 1e-7."),
        # ---- method="loess"
        Case("draw_smooth_line", "the drawn loess curve of drivers killed or seriously injured is R's", "Seatbelts",
             "real data", option='test_method="loess", with_confidence_band=', ours_r=(),
             ours="""
                 from simplydata._underneath.check import chart_facts
                 ax = (sdata.chart(data).draw_dots(x="month", y="drivers")
                       .draw_smooth_line(test_method="loess", with_confidence_band=True)._render().axes[0])
                 x, y = chart_facts(ax)["lines"][0]
                 {"points": len(x), "curve at the first month": y[0], "curve at the last month": y[-1]}
             """,
             r="""
                 m <- stats::loess(drivers ~ month, span = 0.75, degree = 2)
                 list(points = 200, `curve at the first month` = stats::predict(m, data.frame(month = min(month))),
                      `curve at the last month` = stats::predict(m, data.frame(month = max(month))))
             """, r_tolerance=1e-9),
        Case("table.add_smoothed_column", "drivers killed or seriously injured, smoothed by loess with its band",
             "Seatbelts", "real data", option='test_method="loess", interval=', ours_r=(),
             ours="""
                 r = sdata.table(data).add_smoothed_column("trend", from_column="drivers", sorted_by="month",
                                                           test_method="loess", interval=95).as_pandas()
                 {"first": r["trend"].iloc[0], "last": r["trend"].iloc[-1],
                  "first band low": r["trend 95 % CI low"].iloc[0]}
             """,
             r="""
                 m <- loess(drivers ~ month, span = 0.75, degree = 2)
                 p <- predict(m, se = TRUE)
                 q <- qt(0.975, m$one.delta^2 / m$two.delta)
                 list(first = p$fit[1], last = p$fit[length(p$fit)], `first band low` = p$fit[1] - q * p$se.fit[1])
             """, r_tolerance=1e-9),
    ]
    return cases


def add_to(namespace) -> None:
    """Add the S3a-2 datasets and cases to cases.py, and teach its load() the datasets read from R or
    statsmodels."""
    Dataset, Case, data_dir = namespace["Dataset"], namespace["Case"], namespace["DATA"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    namespace["CASES"].extend(_cases(Case, data_dir))
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA:
            from simplydata._r import r_call

            packages, code = R_DATA[name]
            found = r_call(code, packages=packages, what=f"the {name} data")
            return pd.DataFrame({k: (np.asarray(v, dtype=float) if np.asarray(v).dtype.kind in "iuf" else list(v))
                                 for k, v in found.items()})
        if name == "Engel food expenditure":
            import statsmodels.api as sm

            return sm.datasets.engel.load_pandas().data
        return plain_load(name)

    namespace["load"] = load
