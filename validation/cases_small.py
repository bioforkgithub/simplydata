"""The reliability study for phase S3c-4, small additions to known words: weighted percentiles and medians
(find_percentile_of / find_median_of with weights=), the covariance table (find_correlation_between(show="covariance")),
the automatic ARIMA order (forecast(order="automatic")), Storey's q-values and the local false discovery rate
(add_adjusted_p_value_column(test_method="storey" | "local fdr")), Nemenyi's and Conover's tests after Friedman's
(compare_each_pair_of(matched_by=, test_method=)) and pairwise comparisons of percents (compare_each_pair_of(based_on=
"percents")).

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own DATASETS
and CASES and teaches load() the dataset read from R (hedenfalk: qvalue's data, LGPL, read where it is published).

Published answers: Storey & Tibshirani (2003) for the hedenfalk pi0 (0.67); Box & Jenkins (1976) for the order of the
airline model on the log of the air passengers. The other numbers are checked against R (and NumPy or pandas): the
same packages simplydata runs, or base R by definition.
"""

from __future__ import annotations

import textwrap

import numpy as np
import pandas as pd

R_DATA_SMALL = {
    "hedenfalk (qvalue)": (("qvalue",), 'e <- new.env(); utils::data("hedenfalk", package = "qvalue", envir = e); '
                                        "list(p = as.numeric(e$hedenfalk$p))"),
}
OURS_R = {"table.forecast": ("forecast",), "table.add_adjusted_p_value_column": ("qvalue",)}
BOX_JENKINS = ("Box, G. E. P. & Jenkins, G. M. (1976), Time Series Analysis: Forecasting and Control, revised ed., "
               "Holden-Day: the airline model ARIMA(0,1,1)(0,1,1)12 of the log passengers (series G)")
STOREY = "Storey & Tibshirani (2003), PNAS 100:9440-9445"
ROUNDING = """
    long = data.melt(id_vars="player", value_vars=["round_out", "narrow_angle", "wide_angle"], var_name="method",
                     value_name="time")
"""
SMOKERS = """
    rows = [{"group": str(g), "smoker": "yes"} for g, s in zip(data["group"], data["smokers"]) for _ in range(s)]
    rows += [{"group": str(g), "smoker": "no"} for g, s, n in zip(data["group"], data["smokers"], data["patients"])
             for _ in range(n - s)]
"""


def _join(*parts) -> str:
    """Pieces of case code, each dedented, as one block."""
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts)


def _datasets(Dataset):
    return [
        Dataset("Quetelet's chest sizes", "chest_sizes.csv",
                "the chest girth (inches) of 5738 Scottish soldiers, as a table of counts: 16 girths and how many "
                "soldiers had each",
                "Quetelet, A. (1846). Lettres a S.A.R. le Duc Regnant de Saxe-Cobourg et Gotha, sur la theorie des "
                "probabilites. Hayez, Brussels; Stigler, S. M. (1986). The History of Statistics. Harvard University "
                "Press. The same counts as R HistData's ChestSizes.",
                "Published 1817 and 1846 (facts); numbers stored unchanged.",
                "https://cran.r-project.org/package=HistData"),
        Dataset("AirPassengers", "air_passengers.csv",
                "the monthly totals of international airline passengers (thousands), 1949-1960",
                f"{BOX_JENKINS}. Copy from R's datasets package (AirPassengers).",
                "Published 1976 (facts); R's datasets copy is GPL-2 | GPL-3.",
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/AirPassengers.html"),
        # families for 100 %, batch 21 (approved by Manish 2026-11-28): places spread over a large part of the
        # earth, for find_regions_around_points(longitude=, latitude=)
        Dataset("state.center (R datasets)", "state_center.csv",
                "the longitude and latitude of the centres of the 50 US states (Alaska and Hawaii placed off the "
                "coast, as R documents)",
                "U.S. Department of Commerce, Bureau of the Census (1977). Statistical Abstract of the United States; "
                "and (1977) County and City Data Book. Copy from R's datasets package (state.center).",
                "Published 1977 (facts); R's datasets copy is GPL-2 | GPL-3.",
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/state.html"),
        Dataset("hedenfalk (qvalue)", "", "3170 p-values of genes compared between BRCA1 and BRCA2 breast tumours",
                "Hedenfalk, I. et al. (2001). Gene-expression profiles in hereditary breast cancer. New England Journal "
                "of Medicine 344, 539-548; the p-values of Storey & Tibshirani (2003), PNAS 100, 9440-9445, as R "
                "qvalue ships them (hedenfalk).",
                "LGPL (qvalue); read from the installed package, so it needs R.",
                "https://doi.org/10.1073/pnas.1530509100"),
        Dataset("rounding first base", "rounding_first_base.csv",
                "the times (seconds) of 22 baseball players running to second base by three routes (round out, "
                "narrow angle, wide angle): each player ran all three",
                "Hollander, M. & Wolfe, D. A. (1973). Nonparametric Statistical Methods. Wiley, p. 140; the example "
                "of R's friedman.test help (RoundingTimes; Friedman chi-squared 11.143, which these numbers give).",
                "Published 1973 (facts); numbers stored unchanged.",
                "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/friedman.test.html"),
        Dataset("smokers (Fleiss)", "smokers.csv",
                "smokers among patients with lung cancer in four groups: counts out of totals",
                "Fleiss, J. L. (1981). Statistical Methods for Rates and Proportions, 2nd ed. Wiley, p. 139; the "
                "example of R's prop.test and pairwise.prop.test help.",
                "Published 1981 (facts); numbers stored unchanged.",
                "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/pairwise.prop.test.html"),
    ]


def _cases(Case):
    return [
        # ---------------------------------------------------------------- A14: weighted percentiles
        Case("table.find_percentile_of", "weights=: Quetelet's chest sizes, the 10th and 90th percentiles from counts",
             "Quetelet's chest sizes", "real data",
             ours="""
                 t = sdata.table(data)
                 {"10th percentile": t.find_percentile_of("chest", 10, weights="count"),
                  "90th percentile": t.find_percentile_of("chest", 90, weights="count")}
             """,
             parent="""
                 import numpy as np
                 rows = np.repeat(data["chest"].to_numpy(), data["count"].to_numpy())
                 {"10th percentile": np.percentile(rows, 10), "90th percentile": np.percentile(rows, 90)}
             """, parent_label="NumPy percentile of the repeated rows",
             r="""
                 q <- stats::quantile(rep(chest, count), c(0.1, 0.9))
                 list(`10th percentile` = q[[1]], `90th percentile` = q[[2]])
             """, r_tolerance=1e-12,
             note="R quantile(rep(x, w)) is R's definition of frequency weights (as Hmisc::wtd.quantile(normwt = FALSE))."),
        Case("table.find_percentile_of", 'weight_kind="analytic": Quetelet\'s chest sizes, the weighted inverted CDF',
             "Quetelet's chest sizes", "real data",
             ours="""
                 t = sdata.table(data)
                 {"25th percentile": t.find_percentile_of("chest", 25, weights="count", weight_kind="analytic"),
                  "90th percentile": t.find_percentile_of("chest", 90, weights="count", weight_kind="analytic")}
             """,
             parent="""
                 import numpy as np
                 x, w = data["chest"].to_numpy(dtype=float), data["count"].to_numpy(dtype=float)
                 {"25th percentile": np.percentile(x, 25, weights=w, method="inverted_cdf"),
                  "90th percentile": np.percentile(x, 90, weights=w, method="inverted_cdf")}
             """, parent_label="NumPy percentile(weights=, method=\"inverted_cdf\")",
             r="""
                 o <- order(chest); f <- cumsum(count[o]) / sum(count)
                 list(`25th percentile` = chest[o][which(f >= 0.25)[1]], `90th percentile` = chest[o][which(f >= 0.9)[1]])
             """, r_tolerance=1e-12,
             note="R has no weighted quantile in base R; the R side writes out the inverted CDF (Hyndman & Fan 1996, "
                  "definition 1, with weights), the rule survey::svyquantile(qrule = \"math\") documents (survey "
                  "itself is not run here)."),
        Case("table.find_median_of", "weights=: Quetelet's chest sizes, the median girth from counts",
             "Quetelet's chest sizes", "real data",
             ours="""
                 {"median": sdata.table(data).find_median_of("chest", weights="count")}
             """,
             parent="""
                 import numpy as np
                 {"median": np.median(np.repeat(data["chest"].to_numpy(), data["count"].to_numpy()))}
             """, parent_label="NumPy median of the repeated rows",
             r="""
                 list(median = stats::median(rep(chest, count)))
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- A25: covariance matrix
        Case("table.find_correlation_between", 'show="covariance": mtcars, fuel use, weight and horsepower',
             "mtcars", "real data",
             ours="""
                 r = sdata.table(data).find_correlation_between("mpg", "wt", "hp", show="covariance").as_pandas()
                 {"variance of mpg": r["mpg"][0], "mpg with wt": r["wt"][0], "mpg with hp": r["hp"][0],
                  "wt with hp": r["hp"][1]}
             """,
             parent="""
                 c = data[["mpg", "wt", "hp"]].cov()
                 {"variance of mpg": c.loc["mpg", "mpg"], "mpg with wt": c.loc["mpg", "wt"],
                  "mpg with hp": c.loc["mpg", "hp"], "wt with hp": c.loc["wt", "hp"]}
             """, parent_label="pandas DataFrame.cov",
             r="""
                 c <- stats::cov(cbind(mpg, wt, hp), use = "pairwise.complete.obs")
                 list(`variance of mpg` = c[1, 1], `mpg with wt` = c[1, 2], `mpg with hp` = c[1, 3], `wt with hp` = c[2, 3])
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- AA11: automatic ARIMA order
        Case("table.forecast", 'order="automatic": the air passengers, the order auto.arima chooses and the forecast',
             "AirPassengers", "real data",
             ours="""
                 t = sdata.table(data)
                 t.turn_into_dates("month")
                 r = t.forecast("passengers", sorted_by="month", test_method="arima", order="automatic", repeats_every=12)
                 r = r.as_pandas()
                 {"forecast for 1961-01": r["forecast"][0], "95 % low": r["forecast 95 % prediction low"][0],
                  "95 % high": r["forecast 95 % prediction high"][0], "forecast for 1961-12": r["forecast"][11]}
             """,
             r="""
                 fit <- forecast::auto.arima(stats::ts(passengers, frequency = 12), stepwise = FALSE,
                                             approximation = FALSE)
                 f <- forecast::forecast(fit, h = 12, level = 95)
                 list(`forecast for 1961-01` = f$mean[1], `95 % low` = f$lower[1], `95 % high` = f$upper[1],
                      `forecast for 1961-12` = f$mean[12])
             """, r_packages=("forecast",), r_tolerance=1e-9,
             note="auto.arima chooses ARIMA(2,1,1)(0,1,0)[12] for the raw passengers (forecast 9.0.2)."),
        Case("table.forecast", 'order="automatic": the log air passengers, the airline model of Box and Jenkins',
             "AirPassengers", "published",
             ours="""
                 import re
                 data = data.assign(log_passengers=np.log(data["passengers"]))
                 t = sdata.table(data)
                 t.turn_into_dates("month")
                 r = t.forecast("log_passengers", sorted_by="month", test_method="arima", order="automatic",
                                repeats_every=12, show="model").as_pandas()
                 f = t.forecast("log_passengers", sorted_by="month", test_method="arima", order="automatic",
                                repeats_every=12).as_pandas()
                 p, d, q, sp, sd, sq = (int(v) for v in re.findall(r"\\d+", f["method"][0])[:6])
                 {"p": p, "d": d, "q": q, "seasonal p": sp, "seasonal d": sd, "seasonal q": sq,
                  "ma1": r["estimate"][0], "sma1": r["estimate"][1]}
             """,
             published={"p": (0, 0, BOX_JENKINS), "d": (1, 0, BOX_JENKINS), "q": (1, 0, BOX_JENKINS),
                        "seasonal p": (0, 0, BOX_JENKINS), "seasonal d": (1, 0, BOX_JENKINS),
                        "seasonal q": (1, 0, BOX_JENKINS)},
             r="""
                 fit <- forecast::auto.arima(stats::ts(log(passengers), frequency = 12), stepwise = FALSE,
                                             approximation = FALSE)
                 a <- fit$arma
                 list(p = a[1], d = a[6], q = a[2], `seasonal p` = a[3], `seasonal d` = a[7], `seasonal q` = a[4],
                      ma1 = unname(fit$coef["ma1"]), sma1 = unname(fit$coef["sma1"]))
             """, r_packages=("forecast",), r_tolerance=1e-9,
             note="The order is Box and Jenkins's airline model; the two estimates are checked against R (exact "
                  "maximum likelihood: ma1 -0.402, sma1 -0.557), as Box and Jenkins estimated them another way."),
        # ---------------------------------------------------------------- G03: q-values and local FDR
        Case("table.add_adjusted_p_value_column", 'test_method="storey": Hedenfalk\'s 3170 genes, Storey\'s q-values',
             "hedenfalk (qvalue)", "published",
             ours="""
                 r = sdata.table(data).add_adjusted_p_value_column(from_column="p", test_method="storey").as_pandas()
                 q = r["p (Storey q-value)"].to_numpy()
                 last = int(np.argmax(r["p"].to_numpy()))
                 {"pi0": q[last] / r["p"][last], "q-values below 0.05": int((q < 0.05).sum()), "first q-value": q[0]}
             """,
             published={"pi0": (0.67, 0.005, STOREY)},
             r="""
                 q <- qvalue::qvalue(p)
                 list(pi0 = q$pi0, `q-values below 0.05` = sum(q$qvalues < 0.05), `first q-value` = q$qvalues[1])
             """, r_packages=("qvalue",), r_tolerance=1e-9,
             note="pi0 is read back from the table as the q-value of the largest p-value divided by that p-value "
                  "(qvalue's last q-value is pi0 times it). The paper finds 160 genes at q < 0.05 on its own p-values; "
                  "qvalue's copy of the p-values gives 162."),
        Case("table.add_adjusted_p_value_column", 'test_method="local fdr": Hedenfalk\'s 3170 genes, the local false '
                                                  "discovery rate", "hedenfalk (qvalue)", "real data",
             ours="""
                 r = sdata.table(data).add_adjusted_p_value_column(from_column="p", test_method="local fdr").as_pandas()
                 l = r["local false discovery rate"].to_numpy()
                 {"below 0.05": int((l < 0.05).sum()), "first": l[0], "smallest": l.min()}
             """,
             r="""
                 l <- qvalue::qvalue(p)$lfdr
                 list(`below 0.05` = sum(l < 0.05), first = l[1], smallest = min(l))
             """, r_packages=("qvalue",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- G09: Nemenyi and Conover after Friedman
        Case("table.compare_each_pair_of", 'matched_by=, test_method="nemenyi": rounding first base, three routes',
             "rounding first base", "real data",
             ours=_join(ROUNDING, """
                 r = sdata.table(long).compare_each_pair_of("time", for_each_group_in="method", matched_by="player",
                                                            test_method="nemenyi").as_pandas()
                 {"narrow angle vs round out": r["p-value (adjusted)"][0],
                  "narrow angle vs wide angle": r["p-value (adjusted)"][1],
                  "round out vs wide angle": r["p-value (adjusted)"][2]}
             """),
             r="""
                 y <- c(narrow_angle, round_out, wide_angle)
                 g <- factor(rep(c("narrow_angle", "round_out", "wide_angle"), each = length(player)))
                 p <- PMCMRplus::frdAllPairsNemenyiTest(y, g, factor(rep(player, 3)))$p.value
                 list(`narrow angle vs round out` = p[1, 1], `narrow angle vs wide angle` = p[2, 1],
                      `round out vs wide angle` = p[2, 2])
             """, r_packages=("PMCMRplus",), r_tolerance=1e-9,
             note="The same p-values (0.637, 0.061, 0.0044) come from scikit-posthocs posthoc_nemenyi_friedman."),
        Case("table.compare_each_pair_of", 'matched_by=, test_method="conover": rounding first base, Holm-adjusted',
             "rounding first base", "real data",
             ours=_join(ROUNDING, """
                 r = sdata.table(long).compare_each_pair_of("time", for_each_group_in="method", matched_by="player",
                                                            test_method="conover").as_pandas()
                 {"narrow angle vs round out": r["p-value (adjusted)"][0],
                  "narrow angle vs wide angle": r["p-value (adjusted)"][1],
                  "round out vs wide angle": r["p-value (adjusted)"][2]}
             """),
             r="""
                 y <- c(narrow_angle, round_out, wide_angle)
                 g <- factor(rep(c("narrow_angle", "round_out", "wide_angle"), each = length(player)))
                 p <- PMCMRplus::frdAllPairsConoverTest(y, g, factor(rep(player, 3)), p.adjust.method = "holm")$p.value
                 list(`narrow angle vs round out` = p[1, 1], `narrow angle vs wide angle` = p[2, 1],
                      `round out vs wide angle` = p[2, 2])
             """, r_packages=("PMCMRplus",), r_tolerance=1e-9,
             note="PMCMRplus's own default adjustment is single-step (0.547, 0.0007, 0.024) and scikit-posthocs "
                  "adjusts nothing (0.301, 0.0007, 0.012); simplydata names Holm."),
        # ---------------------------------------------------------------- D13: pairwise comparisons of percents
        Case("table.compare_each_pair_of", 'based_on="percents": Fleiss\'s smokers in four groups of patients',
             "smokers (Fleiss)", "real data",
             ours=_join(SMOKERS, """
                 r = sdata.table(pd.DataFrame(rows)).compare_each_pair_of("smoker", for_each_group_in="group",
                                                                         based_on="percents", value="yes").as_pandas()
                 {"1 vs 4": r["p-value (Holm)"][2], "2 vs 4": r["p-value (Holm)"][4], "3 vs 4": r["p-value (Holm)"][5],
                  "1 vs 2": r["p-value (Holm)"][0]}
             """),
             r="""
                 p <- stats::pairwise.prop.test(smokers, patients)$p.value
                 list(`1 vs 4` = p[3, 1], `2 vs 4` = p[3, 2], `3 vs 4` = p[3, 3], `1 vs 2` = p[1, 1])
             """, r_tolerance=1e-9,
             note="R pairwise.prop.test() uses Yates' correction and Holm by default, as simplydata does (without the "
                  "correction 1 vs 4 would be 0.057 instead of 0.119)."),
        Case("table.compare_each_pair_of", 'based_on="percents": Fleiss\'s smokers, Fisher\'s exact test for each pair',
             "smokers (Fleiss)", "real data",
             ours=_join(SMOKERS, """
                 r = sdata.table(pd.DataFrame(rows)).compare_each_pair_of("smoker", for_each_group_in="group",
                                                                         based_on="percents", test_method="fisher").as_pandas()
                 {"1 vs 4": r["p-value (Holm)"][2], "3 vs 4": r["p-value (Holm)"][5]}
             """),
             r="""
                 x <- cbind(smokers, patients - smokers); rownames(x) <- group
                 r <- rstatix::pairwise_fisher_test(x, p.adjust.method = "holm")
                 list(`1 vs 4` = r$p.adj[3], `3 vs 4` = r$p.adj[6])
             """, r_packages=("rstatix",), r_tolerance=1e-9),
    ]


def add_to(namespace) -> None:
    """Add the S3c-4 datasets and cases to cases.py, and teach its load() the dataset read from R."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    import dataclasses

    cases = []
    for c in _cases(Case):
        head = c.title.split(":")[0]
        option = head if "=" in head else ""
        ours_r = OURS_R.get(c.word)
        if 'test_method="nemenyi"' in c.title or 'test_method="conover"' in c.title:
            ours_r = ("PMCMRplus",)
        cases.append(dataclasses.replace(c, ours_r=ours_r, option=option))
    namespace["CASES"].extend(cases)
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_SMALL.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_SMALL:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_SMALL[name]
            need_r(packages, f"the {name} data")
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
