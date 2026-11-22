"""The reliability study for phase S3c-2, hidden factors: table.find_hidden_factors_behind (R psych) and
table.check_hidden_factors (R lavaan).

The data are the nine mental ability tests of Holzinger & Swineford (1939), published test scores (facts). The
cases read them from R lavaan, where the nine-test version is published (the practice table ability_tests is made up,
with the same columns, and nothing is copied into validation/data). The
confirmatory model is the three-factor model of the lavaan paper (Rosseel 2012, Journal of Statistical Software
48(2)), whose fit is printed there; the exploratory cases are checked against R psych itself and, for maximum
likelihood, against base R factanal and statsmodels Factor (the parts each column does not share do not depend on
the rotation). The design (section 6) named Harman's 24 tests (Harman74.cor) and ability.cov for the exploratory
cases; both are correlation or covariance matrices, and find_hidden_factors_behind takes rows, not a matrix, so they
cannot be run through the word: an owner decision recorded in the PR. cases.py loads this file at its end and calls
add_to().
"""

from __future__ import annotations

import numpy as np
import pandas as pd

HS = "Holzinger & Swineford 1939 (lavaan)"
R_DATA_FACTORS = {
    HS: (("lavaan",), (
        "d <- lavaan::HolzingerSwineford1939; list(school = as.character(d$school), x1 = d$x1, x2 = d$x2, "
        "x3 = d$x3, x4 = d$x4, x5 = d$x5, x6 = d$x6, x7 = d$x7, x8 = d$x8, x9 = d$x9)")),
}
COLUMNS = '["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]'
MEASURED_BY = '{"visual": ["x1", "x2", "x3"], "textual": ["x4", "x5", "x6"], "speed": ["x7", "x8", "x9"]}'
ROSSEEL = "Rosseel (2012), JSS 48(2)"
FRAME = "d <- data.frame(x1, x2, x3, x4, x5, x6, x7, x8, x9)\n"
MODEL = 'model <- "visual =~ x1 + x2 + x3; textual =~ x4 + x5 + x6; speed =~ x7 + x8 + x9"\n'


def _datasets(Dataset):
    return [
        Dataset(HS, "",
                "301 seventh- and eighth-grade pupils of two schools near Chicago (Pasteur and Grant-White) in 1937: "
                "the scores of nine mental ability tests (visual perception, cubes, lozenges, paragraph comprehension, "
                "sentence completion, word meaning, speeded addition, speeded counting of dots, speeded "
                "discrimination of straight and curved capitals)",
                "Holzinger, K. J. & Swineford, F. (1939). A study in factor analysis: the stability of a bi-factor "
                "solution. Supplementary Educational Monographs 48. University of Chicago. The nine-test version and "
                "the three-factor model with its fit are in Rosseel, Y. (2012). lavaan: an R package for structural "
                "equation modeling. Journal of Statistical Software 48(2), 1-36 (CC BY 3.0). Shipped with the R "
                "package lavaan (HolzingerSwineford1939).",
                "Published test scores (1939, facts). Read here from R lavaan (its copy is GPL (>= 2)), so the "
                "cases need R. The practice table ability_tests is made up, with the same columns.",
                "https://doi.org/10.18637/jss.v048.i02"),
    ]


def _cases(Case):
    loadings = """
        r = sdata.table(data).find_hidden_factors_behind(""" + COLUMNS + """{more}).as_pandas().set_index("column")
        {{"x1 on factor 2": r.loc["x1", "factor 2"], "x4 on factor 1": r.loc["x4", "factor 1"],
         "x7 on factor 3": r.loc["x7", "factor 3"], "x9 on factor 2": r.loc["x9", "factor 2"],
         "x9 on factor 3": r.loc["x9", "factor 3"], "shared part of x1": r.loc["x1", "shared part"],
         "shared part of x9": r.loc["x9", "shared part"], "factors": len([c for c in r.columns if
                                                                          c.startswith("factor ")])}}
    """
    psych_loadings = """
        L <- unclass(f$loadings)
        list(`x1 on factor 2` = L[1, 2], `x4 on factor 1` = L[4, 1], `x7 on factor 3` = L[7, 3],
             `x9 on factor 2` = L[9, 2], `x9 on factor 3` = L[9, 3], `shared part of x1` = f$communality[[1]],
             `shared part of x9` = f$communality[[9]], factors = ncol(L))
    """
    own = """
        r = sdata.table(data).find_hidden_factors_behind(""" + COLUMNS + """, how_many=3, test_method="maximum likelihood",
                                                         rotation="varimax").as_pandas()
        out = {f"own part of x{i}": v for i, v in enumerate(r["own part"], 1)}
        out.update({"x1 on factor 2": r["factor 2"][0], "x4 on factor 1": r["factor 1"][3],
                    "x7 on factor 3": r["factor 3"][6], "x9 on factor 3": r["factor 3"][8]})
        out
    """
    fit = """
        r = sdata.table(data).check_hidden_factors({call}).as_pandas().set_index("term")
        {{"chi-square": r.loc["chi-square", "estimate"], "degrees of freedom": r.loc["chi-square", "degrees of freedom"],
         "CFI": r.loc["CFI", "estimate"], "TLI": r.loc["TLI", "estimate"], "RMSEA": r.loc["RMSEA", "estimate"],
         "RMSEA 90 % CI low": r.loc["RMSEA", "90 % CI low"], "RMSEA 90 % CI high": r.loc["RMSEA", "90 % CI high"],
         "SRMR": r.loc["SRMR", "estimate"]{more}}}
    """
    lavaan_fit = """
        m <- lavaan::fitMeasures(f)
        list(`chi-square` = m[["chisq"]], `degrees of freedom` = m[["df"]], CFI = m[["cfi"]], TLI = m[["tli"]],
             RMSEA = m[["rmsea"]], `RMSEA 90 % CI low` = m[["rmsea.ci.lower"]],
             `RMSEA 90 % CI high` = m[["rmsea.ci.upper"]], SRMR = m[["srmr"]]{more})
    """
    return [
        Case("table.find_hidden_factors_behind",
             "nine ability tests: parallel analysis, minres, oblimin (the defaults)", HS, "real data",
             ours=loadings.format(more=""),
             r=FRAME + """
                 set.seed(1)
                 pa <- psych::fa.parallel(d, fm = "minres", fa = "fa", plot = FALSE)
                 f <- psych::fa(d, nfactors = pa$nfact, fm = "minres", rotate = "oblimin")
             """ + psych_loadings, r_packages=("psych", "GPArotation"), r_tolerance=1e-8,
             note="Parallel analysis finds the three factors of Holzinger and Swineford's design (visual, verbal and "
                  "speed); x9 goes with two of them, as the modification indices of the confirmatory model also "
                  "show."),
        Case("table.find_hidden_factors_behind", "how_many=: three factors asked for, no parallel analysis", HS,
             "real data",
             ours=loadings.format(more=", how_many=3"),
             r=FRAME + """
                 set.seed(1)
                 f <- psych::fa(d, nfactors = 3, fm = "minres", rotate = "oblimin")
             """ + psych_loadings, r_packages=("psych", "GPArotation"), r_tolerance=1e-8,
             note="The oblimin rotation of GPArotation starts from random numbers, so both sides set R's seed first "
                  "(unseeded, the loadings change in the sixth digit from run to run)."),
        Case("table.find_hidden_factors_behind", "rotation=: promax, with principal axis factoring", HS,
             "real data",
             ours=loadings.format(more=', how_many=3, test_method="principal axis", rotation="promax"'),
             r=FRAME + """
                 f <- psych::fa(d, nfactors = 3, fm = "pa", rotate = "promax")
             """ + psych_loadings, r_packages=("psych", "GPArotation"), r_tolerance=1e-8),
        Case("table.find_hidden_factors_behind", "test_method=: maximum likelihood with varimax, as R factanal", HS,
             "real data", ours=own,
             parent="""
                 from statsmodels.multivariate.factor import Factor
                 f = Factor(data[[f"x{i}" for i in range(1, 10)]].to_numpy(dtype=float), n_factor=3,
                            method="ml").fit(maxiter=100000, tol=1e-14)
                 {f"own part of x{i}": v for i, v in enumerate(f.uniqueness, 1)}
             """, parent_label="statsmodels Factor (method=\"ml\"), run to 1e-14", parent_tolerance=1e-5,
             r=FRAME + """
                 f <- stats::factanal(d, factors = 3, rotation = "varimax",
                                      control = list(opt = list(maxit = 100000, factr = 1)))
                 u <- as.numeric(f$uniquenesses); L <- unclass(f$loadings)
                 c(stats::setNames(as.list(u), paste("own part of", names(f$uniquenesses))),
                   list(`x1 on factor 2` = L[1, 2], `x4 on factor 1` = L[4, 1], `x7 on factor 3` = L[7, 3],
                        `x9 on factor 3` = L[9, 3]))
             """, r_tolerance=1e-5,
             note="The part of each column the factors do not share (the uniqueness) does not depend on the "
                  "rotation and is checked against base R factanal and statsmodels; the varimax loadings are checked "
                  "against factanal (the same factor order and signs here). Both references are run to convergence "
                  "(factanal's optim with factr = 1, statsmodels to 1e-14); they then agree with simplydata (R "
                  "psych::fa(fm = \"ml\") with its own stopping rule) to 3e-6, so the check allows 1e-5. With their "
                  "default stopping rules the three differed by up to 1.6e-5, and the check allowed 1e-3."),
        Case("table.check_hidden_factors", "the three-factor model of the lavaan paper", HS, "published",
             ours=fit.format(call="measured_by=" + MEASURED_BY, more=""),
             published={"chi-square": (85.306, 5e-4, ROSSEEL), "degrees of freedom": (24, 0, "exact"),
                        "CFI": (0.931, 5e-4, ROSSEEL), "TLI": (0.896, 5e-4, ROSSEEL), "RMSEA": (0.092, 5e-4, ROSSEEL),
                        "RMSEA 90 % CI low": (0.071, 5e-4, ROSSEEL), "RMSEA 90 % CI high": (0.114, 5e-4, ROSSEEL),
                        "SRMR": (0.065, 5e-4, ROSSEEL)},
             r=FRAME + MODEL + "f <- lavaan::cfa(model, data = d, estimator = \"ML\")\n" + lavaan_fit.format(more=""),
             r_packages=("lavaan",), r_tolerance=1e-8,
             note="Rosseel (2012) prints the fit of this model to three decimals; the p-value of the chi-square test "
                  "is below 0.001 there too."),
        Case("table.check_hidden_factors", "formula=: the speed factor explained by the visual one (lavaan sem)", HS,
             "real data",
             ours="""
                 r = sdata.table(data).check_hidden_factors(formula="visual =~ x1 + x2 + x3; speed =~ x7 + x8 + x9; "
                                                                    "speed ~ visual").as_pandas().set_index("term")
                 {"path": r.loc["speed explained by visual", "estimate"],
                  "its standard error": r.loc["speed explained by visual", "standard error"],
                  "chi-square": r.loc["chi-square", "estimate"], "CFI": r.loc["CFI", "estimate"]}
             """,
             r=FRAME + """
                 model <- "visual =~ x1 + x2 + x3; speed =~ x7 + x8 + x9; speed ~ visual"
                 f <- lavaan::sem(model, data = d, estimator = "ML")
                 s <- lavaan::standardizedSolution(f); r <- s[s$op == "~", ]
                 m <- lavaan::fitMeasures(f)
                 list(path = r$est.std, `its standard error` = r$se, `chi-square` = m[["chisq"]], CFI = m[["cfi"]])
             """, r_packages=("lavaan",), r_tolerance=1e-8),
        Case("table.check_hidden_factors", "empty cells: 30 visual-perception scores taken out, full information", HS,
             "real data",
             ours="""
                 data = data.copy()
                 data.loc[data.index[:30], "x1"] = np.nan
                 r = sdata.table(data).check_hidden_factors(measured_by=""" + MEASURED_BY + """).as_pandas()
                 r = r.set_index("term")
                 {"chi-square": r.loc["chi-square", "estimate"], "x1 loading": r.loc["visual measured by x1", "estimate"],
                  "CFI": r.loc["CFI", "estimate"]}
             """,
             r=FRAME + MODEL + """
                 d$x1[1:30] <- NA
                 f <- lavaan::cfa(model, data = d, estimator = "ML", missing = "ml")
                 s <- lavaan::standardizedSolution(f); m <- lavaan::fitMeasures(f)
                 list(`chi-square` = m[["chisq"]], `x1 loading` = s$est.std[1], CFI = m[["cfi"]])
             """, r_packages=("lavaan",), r_tolerance=1e-8,
             note="Real data with 30 cells emptied on purpose (the first 30 rows of x1): every row stays in, as with "
                  "lavaan's missing = \"ml\"; lavaan's own default would leave the 30 rows out."),
    ]


def add_to(namespace) -> None:
    """Add the S3c-2 dataset and cases to cases.py, and teach its load() the dataset read from R lavaan."""
    import dataclasses

    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    for c in _cases(Case):
        head = c.title.split(":")[0]
        option = head if head.endswith("=") and " " not in head else ""
        ours_r = ("lavaan",) if c.word == "table.check_hidden_factors" else ("psych", "GPArotation")
        namespace["CASES"].append(dataclasses.replace(c, ours_r=ours_r, option=option))
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_FACTORS.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_FACTORS:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_FACTORS[name]
            need_r(packages, f"the {name} data")  # checked, not attached: the code names its package
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: (np.asarray(v, dtype=float) if np.asarray(v).dtype.kind in "iuf" else list(v))
                                 for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
