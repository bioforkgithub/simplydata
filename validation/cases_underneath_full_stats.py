"""The reliability study for the families for 100 % plan, batches 3-4 (approved by Manish 2026-11-28): the scipy.stats
tests, summaries, bins, best powers, distances, sensitivity and censored fits of plan section 2.2, each run on real,
published data.

cases_underneath.py loads this file and adds the cases. Each new option value is compared with the SciPy function its
box names and, where base R (or R survival) does the same thing in a few plain lines, with R. The datasets are the
study's own (validation/README.md): NIST's Michelson measurements of the speed of light, mtcars, iris, warpbreaks,
lung (R survival) and the hedenfalk p-values (R qvalue); the Ishigami function's Sobol' indices are published in
closed form (Saltelli et al. 2010).

The simplydata side reads its results only with simplydata words (get_cell_at, get_column ...).
"""

from __future__ import annotations

import textwrap

MICHELSON = "NIST Michelso"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts if part and part.strip())
SUMMARY = """
    s = sdata.table(data).find_summary_of("y", show=["{measure}"])
    {{"value": s.get_cell_at(row=1, column="{measure}")}}
"""


def _summary(Case, measure, title, parent, parent_label, r="", tolerance=1e-12, r_tolerance=1e-10, option=None,
             needs=()):
    """A find_summary_of(show=) case on Michelson's measurements; option= is the label of the measure's box in the
    manual ("power mean p"), the measure's own name when it takes no number."""
    return Case("table.find_summary_of", f"Michelson's speed of light (NIST): {title}", MICHELSON, "real data",
                option=f'show="{option or measure}"',
                ours=SUMMARY.format(measure=measure),
                parent="from scipy import stats\ny = data[\"y\"].to_numpy(float)\n" + parent,
                parent_label=parent_label, parent_tolerance=tolerance, r=r, r_tolerance=r_tolerance, needs=needs)


def _summaries(Case):
    return [
        _summary(Case, "geometric standard deviation", "the geometric standard deviation",
                 '{"value": stats.gstd(y)}', "SciPy stats.gstd", r="list(value = exp(sd(log(y))))"),
        _summary(Case, "power mean 3", "the power mean of order 3", '{"value": stats.pmean(y, 3)}',
                 "SciPy stats.pmean", r="list(value = mean(y^3)^(1/3))", option="power mean p"),

        _summary(Case, "l-skewness", "the L-skewness (the third L-moment ratio)",
                 '{"value": stats.lmoment(y, order=3)}', "SciPy stats.lmoment",
                 r="x <- sort(y); n <- length(x); i <- 0:(n - 1); b0 <- mean(x); b1 <- sum(i * x) / (n * (n - 1)); "
                   "b2 <- sum(i * (i - 1) * x) / (n * (n - 1) * (n - 2)); "
                   "list(value = (6 * b2 - 6 * b1 + b0) / (2 * b1 - b0))", r_tolerance=1e-7, option="l-skewness"),

        _summary(Case, "l-moment 2", "the second L-moment", '{"value": stats.lmoment(y, order=2)}',
                 "SciPy stats.lmoment",
                 r="x <- sort(y); n <- length(x); b1 <- sum((0:(n - 1)) * x) / (n * (n - 1)); "
                   "list(value = 2 * b1 - mean(x))", r_tolerance=1e-9, option="l-moment k"),
        _summary(Case, "central moment 3", "the third central moment", '{"value": stats.moment(y, order=3)}',
                 "SciPy stats.moment", r="list(value = mean((y - mean(y))^3))", r_tolerance=1e-8,
                 option="central moment k"),
        _summary(Case, "expectile 90", "the 90 % expectile", '{"value": stats.expectile(y, alpha=0.9)}',
                 "SciPy stats.expectile",
                 r="f <- function(t) 0.9 * sum(pmax(y - t, 0)) - 0.1 * sum(pmax(t - y, 0)); "
                   "list(value = uniroot(f, range(y), tol = 1e-13)$root)", r_tolerance=1e-10, option="expectile p"),
        _summary(Case, "average between 299.8 and 299.9", "the average of the values from 299.8 to 299.9",
                 '{"value": stats.tmean(y, (299.8, 299.9))}', "SciPy stats.tmean",
                 r="list(value = mean(y[y >= 299.8 & y <= 299.9]))", option="average between a and b"),
        _summary(Case, "standard deviation between 299.8 and 299.9", "the standard deviation of the values from "
                 "299.8 to 299.9", '{"value": stats.tstd(y, (299.8, 299.9))}', "SciPy stats.tstd",
                 r="list(value = sd(y[y >= 299.8 & y <= 299.9]))", r_tolerance=1e-9, option="average between a and b"),
        _summary(Case, "smallest from 299.9", "the smallest value of at least 299.9",
                 '{"value": stats.tmin(y, lowerlimit=299.9)}', "SciPy stats.tmin",
                 r="list(value = min(y[y >= 299.9]))", option="smallest from a"),
        _summary(Case, "differential entropy", "the differential entropy",
                 '{"value": stats.differential_entropy(y)}', "SciPy stats.differential_entropy"),
        _summary(Case, "percentile rank 299.875", "the percentile rank of 299.875 (the inverse of R type 7)",
                 '{"value": float(stats.estimated_cdf(y, 299.875)) * 100}', "SciPy stats.estimated_cdf",
                 r="list(value = 100 * uniroot(function(p) quantile(y, p, type = 7, names = FALSE) - 299.875, "
                   "c(0, 1), tol = 1e-14)$root)", r_tolerance=1e-8, option="percentile rank v",
                 needs=(("scipy", "1.18"),)),
        _summary(Case, "percent at or below 299.9", "the percent of values at or below 299.9",
                 '{"value": stats.percentileofscore(y, 299.9, kind="weak")}', "SciPy stats.percentileofscore",
                 r="list(value = 100 * mean(y <= 299.9))", option="percent at or below v"),
        _summary(Case, "sigma-clipped average 2", "the average after clipping at 2 standard deviations",
                 '{"value": stats.sigmaclip(y, 2, 2).clipped.mean()}', "SciPy stats.sigmaclip",
                 r="x <- y; repeat { m <- mean(x); s <- sqrt(mean((x - m)^2)); "
                   "k <- x[x >= m - 2 * s & x <= m + 2 * s]; "
                   "if (length(k) == length(x)) break; x <- k }; list(value = mean(x))", r_tolerance=1e-10,
                 option="sigma-clipped average"),
    ]


MTCARS_BINS = """
    import numpy as np
    from scipy import stats
    edges = np.arange(1, 7, 1.0)  # wt runs from 1.513 to 5.424: bins 1 wide from 1 to 6
"""


def _cumulants(Case):
    """The k-statistics on mtcars' fuel use (SciPy kstat works from power sums, which lose digits on values that differ
    only in their fourth digit, as Michelson's do)."""
    def one(measure, title, parent, r, option):
        return Case("table.find_summary_of", f"mtcars: {title} of fuel use", "mtcars", "real data",
                    option=f'show="{option}"',
                    ours=f"""
                        s = sdata.table(data).find_summary_of("mpg", show=["{measure}"])
                        {{"value": s.get_cell_at(row=1, column="{measure}")}}
                    """,
                    parent="from scipy import stats\ny = data[\"mpg\"].to_numpy(float)\n" + parent,
                    parent_label="SciPy stats.kstat" if "kstatvar" not in parent else "SciPy stats.kstatvar",
                    parent_tolerance=1e-12, r=r, r_tolerance=1e-10)

    return [
        one("cumulant 2", "the second k-statistic (the variance)", '{"value": stats.kstat(y, 2)}',
            "list(value = var(mpg))", "cumulant k"),
        one("cumulant 3", "the third k-statistic", '{"value": stats.kstat(y, 3)}',
            "y <- mpg; n <- length(y); list(value = n^2 / ((n - 1) * (n - 2)) * mean((y - mean(y))^3))", "cumulant k"),
        one("cumulant variance 2", "the variance of the second k-statistic", '{"value": stats.kstatvar(y, 2)}', "",
            "cumulant variance k"),
    ]


def _circular(Case):
    return [
        Case("table.find_summary_of", "turtles: the circular average and spread of 10 homing directions (degrees)",
             "turtles (circular)", "real data", option='show="circular average"',
             ours="""
                 s = sdata.table(data).find_summary_of("arrival", show=["circular average in degrees",
                                                                        "circular variance in degrees"])
                 {"average": s.get_cell_at(row=1, column="circular average in degrees"),
                  "variance": s.get_cell_at(row=1, column="circular variance in degrees")}
             """,
             parent="""
                 from scipy import stats
                 a = data["arrival"].to_numpy(float)
                 {"average": stats.circmean(a, high=360, low=0), "variance": stats.circvar(a, high=360, low=0)}
             """, parent_label="SciPy stats.circmean, stats.circvar",
             r="""
                 a <- arrival * pi / 180; m <- atan2(mean(sin(a)), mean(cos(a))) * 180 / pi
                 list(average = m %% 360, variance = 1 - sqrt(mean(sin(a))^2 + mean(cos(a))^2))
             """, r_tolerance=1e-10,
             note="The circular variance is 1 minus the mean resultant length, as R circular::var.circular."),
    ]


def _bins(Case):
    return [
        Case("table.find_summary_of", "mtcars: the average fuel use in bins of 1000 lb of weight", "mtcars",
             "real data", option="in_bins_of=",
             ours="""
                 s = sdata.table(data).find_summary_of("mpg", show=["average"], in_bins_of={"wt": 1})
                 {"first": s.get_cell_at(row=1, column="average"), "last": s.get_cell_at(row=5, column="average"),
                  "bins": s.count_rows()}
             """,
             parent=_code(MTCARS_BINS, """
                 found = stats.binned_statistic(data["wt"], data["mpg"], "mean", bins=edges).statistic
                 {"first": found[0], "last": found[4], "bins": int((~np.isnan(found)).sum())}
             """), parent_label="SciPy stats.binned_statistic",
             r="""
                 m <- tapply(mpg, cut(wt, 1:6, right = FALSE, include.lowest = TRUE), mean)
                 list(first = unname(m[1]), last = unname(m[5]), bins = sum(!is.na(m)))
             """, r_tolerance=1e-12),
        Case("table.find_summary_of", "mtcars: the average fuel use in bins of weight and horsepower", "mtcars",
             "real data", option="in_bins_of= two columns",
             ours="""
                 s = sdata.table(data).find_summary_of("mpg", show=["average", "count"],
                                                       in_bins_of={"wt": 1, "hp": 100})
                 {"first": s.get_cell_at(row=1, column="average"), "cells": s.count_rows()}
             """,
             parent=_code(MTCARS_BINS, """
                 found = stats.binned_statistic_2d(data["wt"], data["hp"], data["mpg"], "mean",
                                                   bins=[edges, np.arange(0, 500, 100.0)]).statistic
                 {"first": found[~np.isnan(found)][0], "cells": int((~np.isnan(found)).sum())}
             """), parent_label="SciPy stats.binned_statistic_2d",
             r="""
                 m <- tapply(mpg, list(cut(wt, 1:6, right = FALSE, include.lowest = TRUE),
                                       cut(hp, c(0, 100, 200, 300, 400), right = FALSE, include.lowest = TRUE)), mean)
                 list(first = t(m)[!is.na(t(m))][1], cells = sum(!is.na(m)))
             """, r_tolerance=1e-12),
        Case("table.find_summary_of", "mtcars: the running count of the cars in bins of weight", "mtcars",
             "real data", option='show="running count"',
             ours="""
                 s = sdata.table(data).find_summary_of("wt", show=["running count"], in_bins_of={"wt": 1})
                 {"after 3 bins": s.get_cell_at(row=3, column="running count"),
                  "after 5 bins": s.get_cell_at(row=5, column="running count")}
             """,
             parent=_code(MTCARS_BINS, """
                 running = stats.cumfreq(data["wt"], numbins=5, defaultreallimits=(1, 6)).cumcount
                 {"after 3 bins": running[2], "after 5 bins": running[4]}
             """), parent_label="SciPy stats.cumfreq",
             r="""
                 k <- table(cut(wt, 1:6, right = FALSE, include.lowest = TRUE))
                 list(`after 3 bins` = cumsum(k)[[3]], `after 5 bins` = cumsum(k)[[5]])
             """, r_tolerance=1e-12),
        Case("table.find_summary_of", "mtcars: the share of the cars in each bin of weight", "mtcars",
             "real data", option='show="share of values"',
             ours="""
                 s = sdata.table(data).find_summary_of("wt", show=["share of values"], in_bins_of={"wt": 1})
                 {"bin 2": s.get_cell_at(row=2, column="share of values"),
                  "bin 3": s.get_cell_at(row=3, column="share of values")}
             """,
             parent=_code(MTCARS_BINS, """
                 share = stats.relfreq(data["wt"], numbins=5, defaultreallimits=(1, 6)).frequency
                 {"bin 2": share[1], "bin 3": share[2]}
             """), parent_label="SciPy stats.relfreq",
             r="""
                 k <- prop.table(table(cut(wt, 1:6, right = FALSE, include.lowest = TRUE)))
                 list(`bin 2` = k[[2]], `bin 3` = k[[3]])
             """, r_tolerance=1e-12),
    ]


TWO_SPECIES = """
    t = sdata.table(data)
    t.keep_rows_where("Species", is_one_of=["versicolor", "virginica"])
"""
TWO_SPECIES_DF = """
    from scipy import stats
    a = data.loc[data["Species"] == "versicolor", "Sepal.Width"].to_numpy(float)
    b = data.loc[data["Species"] == "virginica", "Sepal.Width"].to_numpy(float)
"""


def _tests(Case):
    return [
        Case("table.compare_averages_of", "Fisher's iris: the sepal widths of versicolor and virginica, the "
             "Wilcoxon rank-sum test", "iris", "real data", option='test_method="wilcoxon rank sum"',
             ours=_code(TWO_SPECIES, """
                 r = t.compare_averages_of("Sepal.Width", for_each_group_in="Species", test_method="wilcoxon rank sum")
                 {"z": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """),
             parent=_code(TWO_SPECIES_DF, """
                 found = stats.ranksums(a, b)
                 {"z": found.statistic, "p-value": found.pvalue}
             """), parent_label="SciPy stats.ranksums",
             r="""
                 a <- Sepal.Width[Species == "versicolor"]; b <- Sepal.Width[Species == "virginica"]
                 r <- rank(c(a, b)); n1 <- length(a); n2 <- length(b)
                 z <- (sum(r[1:n1]) - n1 * (n1 + n2 + 1) / 2) / sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
                 list(z = z, `p-value` = 2 * pnorm(-abs(z)))
             """, r_tolerance=1e-12,
             note="SciPy ranksums leaves out the tie correction that R wilcox.test(exact = FALSE) makes, so R is "
                  "written out as the plain rank-sum z."),
        Case("table.compare_averages_of", "Fisher's iris: the Baumgartner-Weiss-Schindler test of the sepal widths",
             "iris", "real data", option='test_method="baumgartner-weiss-schindler"',
             ours=_code(TWO_SPECIES, """
                 r = t.compare_averages_of("Sepal.Width", for_each_group_in="Species",
                                           test_method="baumgartner-weiss-schindler")
                 {"B": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """),
             parent=_code(TWO_SPECIES_DF, """
                 import numpy as np
                 found = stats.bws_test(a, b, method=stats.PermutationMethod(n_resamples=9999,
                                                                               rng=np.random.default_rng(1)))
                 {"B": found.statistic, "p-value": found.pvalue}
             """), parent_label="SciPy stats.bws_test"),
        Case("table.compare_shapes_of", "Fisher's iris: do the sepal widths of versicolor and virginica differ in "
             "shape (Cramer-von Mises)?", "iris", "real data", option='test_method="cramer-von mises"',
             ours=_code(TWO_SPECIES, """
                 r = t.compare_shapes_of("Sepal.Width", for_each_group_in="Species", test_method="cramer-von mises")
                 {"T": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """),
             parent=_code(TWO_SPECIES_DF, """
                 found = stats.cramervonmises_2samp(a, b)
                 {"T": found.statistic, "p-value": found.pvalue}
             """), parent_label="SciPy stats.cramervonmises_2samp"),
        Case("table.compare_shapes_of", "Fisher's iris: the Epps-Singleton test of the sepal widths", "iris",
             "real data", option='test_method="epps-singleton"',
             ours=_code(TWO_SPECIES, """
                 r = t.compare_shapes_of("Sepal.Width", for_each_group_in="Species", test_method="epps-singleton")
                 {"W2": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """),
             parent=_code(TWO_SPECIES_DF, """
                 found = stats.epps_singleton_2samp(a, b)
                 {"W2": found.statistic, "p-value": found.pvalue}
             """), parent_label="SciPy stats.epps_singleton_2samp"),
        Case("table.compare_shape_to", "Michelson's speed of light (NIST): D'Agostino's skewness test", MICHELSON,
             "real data", option='test_method="skewness"',
             ours="""
                 r = sdata.table(data).compare_shape_to("y", "normal", test_method="skewness")
                 {"z": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 found = stats.skewtest(data["y"])
                 {"z": found.statistic, "p-value": found.pvalue}
             """, parent_label="SciPy stats.skewtest"),
        Case("table.compare_shape_to", "Michelson's speed of light (NIST): the Anscombe-Glynn kurtosis test",
             MICHELSON, "real data", option='test_method="kurtosis"',
             ours="""
                 r = sdata.table(data).compare_shape_to("y", "normal", test_method="kurtosis")
                 {"z": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 found = stats.kurtosistest(data["y"])
                 {"z": found.statistic, "p-value": found.pvalue}
             """, parent_label="SciPy stats.kurtosistest"),
        Case("table.compare_counts_to", "mtcars: are the cars spread evenly over 3, 4 and 5 gears (G-test)?",
             "mtcars", "real data", option='test_method="g"',
             ours="""
                 r = sdata.table(data).compare_counts_to("gear", test_method="g")
                 {"G": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 seen = data["gear"].value_counts().sort_index().to_numpy(float)
                 found = stats.power_divergence(seen, lambda_="log-likelihood")
                 {"G": found.statistic, "p-value": found.pvalue}
             """, parent_label="SciPy stats.power_divergence",
             r="""
                 o <- as.numeric(table(gear)); e <- rep(sum(o) / length(o), length(o))
                 g <- 2 * sum(o * log(o / e))
                 list(G = g, `p-value` = pchisq(g, length(o) - 1, lower.tail = FALSE))
             """, r_tolerance=1e-12),
        Case("table.compare_spreads_of", "warpbreaks: do the breaks spread differently at the three tensions "
             "(O'Brien's test)?", "warpbreaks", "real data", option='test_method="o\'brien"',
             ours="""
                 r = sdata.table(data).compare_spreads_of("breaks", for_each_group_in="tension", test_method="o'brien")
                 {"F": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 groups = [g["breaks"].to_numpy(float) for _, g in data.groupby("tension")]
                 found = stats.f_oneway(*stats.obrientransform(*groups))
                 {"F": found.statistic, "p-value": found.pvalue}
             """, parent_label="SciPy stats.obrientransform, then stats.f_oneway",
             r="""
                 score <- function(x) { n <- length(x); m <- mean(x); v <- var(x)
                                        ((n - 1.5) * n * (x - m)^2 - 0.5 * v * (n - 1)) / ((n - 1) * (n - 2)) }
                 ob <- ave(as.numeric(breaks), tension, FUN = score)
                 a <- anova(lm(ob ~ factor(tension)))
                 list(F = a$`F value`[1], `p-value` = a$`Pr(>F)`[1])
             """, r_tolerance=1e-10),
        Case("table.find_correlation_between", "mtcars: Chatterjee's xi of fuel use given weight", "mtcars",
             "real data", option='test_method="chatterjee xi"',
             ours="""
                 {"xi": sdata.table(data).find_correlation_between("wt", "mpg", test_method="chatterjee xi")}
             """,
             parent="""
                 from scipy import stats
                 {"xi": stats.chatterjeexi(data["wt"], data["mpg"]).statistic}
             """, parent_label="SciPy stats.chatterjeexi"),
        Case("table.find_correlation_between", "mtcars: the weighted Kendall's tau of weight and fuel use", "mtcars",
             "real data", option='test_method="weighted kendall"',
             ours="""
                 {"tau": sdata.table(data).find_correlation_between("wt", "mpg", test_method="weighted kendall")}
             """,
             parent="""
                 from scipy import stats
                 {"tau": stats.weightedtau(data["wt"], data["mpg"]).statistic}
             """, parent_label="SciPy stats.weightedtau"),
        Case("table.find_correlation_between", "mtcars: the multiscale graph correlation of weight and fuel use",
             "mtcars", "real data", option='test_method="multiscale graph"',
             ours="""
                 {"MGC": sdata.table(data).find_correlation_between("wt", "mpg", test_method="multiscale graph")}
             """,
             parent="""
                 import numpy as np
                 from scipy import stats
                 x, y = data["wt"].to_numpy(float), data["mpg"].to_numpy(float)
                 {"MGC": stats.multiscale_graphcorr(x, y, reps=1000, random_state=np.random.default_rng(1)).statistic}
             """, parent_label="SciPy stats.multiscale_graphcorr", parent_tolerance=1e-10),
        Case("table.compare_rates", "lung (R survival): deaths per day of follow-up in men and women, the E-test",
             "lung (survival)", "real data", option='test_method="e-test"',
             ours="""
                 t = sdata.table(data.assign(death=(data["died"] == "yes").astype(int)))
                 r = t.compare_rates("death", time="time", for_each_group_in="sex", against="female",
                                     test_method="e-test")
                 {"z": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 d = data.assign(death=(data["died"] == "yes").astype(int)).groupby("sex")[["death", "time"]].sum()
                 found = stats.poisson_means_test(int(d.loc["male", "death"]), d.loc["male", "time"],
                                                  int(d.loc["female", "death"]), d.loc["female", "time"])
                 {"z": found.statistic, "p-value": found.pvalue}
             """, parent_label="SciPy stats.poisson_means_test"),
        Case("table.find_interval_of", "Michelson's speed of light (NIST): the Bayesian interval of the average",
             MICHELSON, "real data", option='test_method="bayesian"',
             ours="""
                 i = sdata.table(data).find_interval_of("y", "average", test_method="bayesian")
                 {"low": i.get_cell_at(row=1, column="average of y 95 % CI low"),
                  "high": i.get_cell_at(row=1, column="average of y 95 % CI high")}
             """,
             parent="""
                 from scipy import stats
                 average = stats.bayes_mvs(data["y"], alpha=0.95)[0]
                 {"low": average.minmax[0], "high": average.minmax[1]}
             """, parent_label="SciPy stats.bayes_mvs",
             r="""
                 ci <- t.test(y)$conf.int
                 list(low = ci[1], high = ci[2])
             """, r_tolerance=1e-12,
             note="With Jeffreys' prior the credible interval of the average is the t interval (R t.test)."),
        Case("table.combine_studies", "the first 20 gene p-values of Hedenfalk et al. (2001), combined by Fisher's "
             "method", "hedenfalk (qvalue)", "real data", option="p_values=",
             ours="""
                 t = sdata.table(data.head(20).assign(gene=range(20)))
                 r = t.combine_studies(names="gene", p_values="p", test_method="fisher")
                 {"chi-square": r.get_cell_at(row=1, column="statistic"),
                  "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 found = stats.combine_pvalues(data["p"].head(20), method="fisher")
                 {"chi-square": found.statistic, "p-value": found.pvalue}
             """, parent_label="SciPy stats.combine_pvalues",
             r="""
                 q <- p[1:20]; x <- -2 * sum(log(q))
                 list(`chi-square` = x, `p-value` = pchisq(x, 2 * length(q), lower.tail = FALSE))
             """, r_tolerance=1e-12),
    ]


def _powers_and_distances(Case):
    return [
        Case("table.find_best_power_of", "mtcars: the Box-Cox log-likelihood of the log of fuel use", "mtcars",
             "real data", option='show="log-likelihood"',
             ours="""
                 p = sdata.table(data).find_best_power_of("mpg", show="log-likelihood")
                 {"at 0": p.get_cell_at(row=21, column="log-likelihood"),
                  "at 1": p.get_cell_at(row=31, column="log-likelihood")}
             """,
             parent="""
                 from scipy import stats
                 {"at 0": stats.boxcox_llf(0.0, data["mpg"]), "at 1": stats.boxcox_llf(1.0, data["mpg"])}
             """, parent_label="SciPy stats.boxcox_llf",
             r="""
                 llf <- function(l) { yt <- if (l == 0) log(mpg) else (mpg^l - 1) / l
                                      (l - 1) * sum(log(mpg)) - length(mpg) / 2 * log(mean((yt - mean(yt))^2)) }
                 list(`at 0` = llf(0), `at 1` = llf(1))
             """, r_tolerance=1e-12),
        Case("table.find_best_power_of", "mtcars: how straight the normal plot of fuel use is for each power",
             "mtcars", "real data", option='show="normal plot correlation"',
             ours="""
                 p = sdata.table(data).find_best_power_of("mpg", show="normal plot correlation")
                 {"at -1": p.get_cell_at(row=11, column="normal plot correlation"),
                  "at 0.5": p.get_cell_at(row=26, column="normal plot correlation")}
             """,
             parent="""
                 from scipy import stats
                 powers, found = stats.boxcox_normplot(data["mpg"], -2, 2, N=41)
                 {"at -1": found[10], "at 0.5": found[25]}
             """, parent_label="SciPy stats.boxcox_normplot"),
        Case("table.find_best_power_of", "mtcars: the Box-Cox power of fuel use with the straightest normal plot",
             "mtcars", "real data", option='show="best by normal plot"',
             ours="""
                 p = sdata.table(data).find_best_power_of("mpg", show="best by normal plot")
                 {"power": p.get_cell_at(row=1, column="power")}
             """,
             parent="""
                 from scipy import stats
                 {"power": stats.boxcox_normmax(data["mpg"], method="pearsonr")}
             """, parent_label="SciPy stats.boxcox_normmax", parent_tolerance=1e-9),
        Case("table.find_best_power_of", "Michelson's speed of light (NIST): the Tukey lambda shape with the "
             "straightest probability plot", MICHELSON, "real data", option='test_method="tukey lambda"',
             ours="""
                 p = sdata.table(data).find_best_power_of("y", test_method="tukey lambda")
                 {"lambda": p.get_cell_at(row=1, column="lambda")}
             """,
             parent="""
                 from scipy import stats
                 {"lambda": stats.ppcc_max(data["y"])}
             """, parent_label="SciPy stats.ppcc_max", parent_tolerance=1e-9),
        Case("table.compare_distributions_for", "Fisher's iris: the Wasserstein distance between the sepal lengths "
             "of the species", "iris", "real data", option='show="wasserstein distance"',
             ours="""
                 r = sdata.table(data).compare_distributions_for("Sepal.Length", for_each_group_in="Species",
                                                                 show="wasserstein distance")
                 {"setosa-versicolor": r.get_cell_at(row=1, column="wasserstein distance"),
                  "versicolor-virginica": r.get_cell_at(row=3, column="wasserstein distance")}
             """,
             parent="""
                 from scipy import stats
                 s, v, g = (data.loc[data["Species"] == k, "Sepal.Length"]
                            for k in ("setosa", "versicolor", "virginica"))
                 {"setosa-versicolor": stats.wasserstein_distance(s, v),
                  "versicolor-virginica": stats.wasserstein_distance(v, g)}
             """, parent_label="SciPy stats.wasserstein_distance",
             r="""
                 w <- function(a, b) mean(abs(sort(a) - sort(b)))
                 s <- Sepal.Length[Species == "setosa"]; v <- Sepal.Length[Species == "versicolor"]
                 g <- Sepal.Length[Species == "virginica"]
                 list(`setosa-versicolor` = w(s, v), `versicolor-virginica` = w(v, g))
             """, r_tolerance=1e-12,
             note="With 50 flowers of each species the distance is the average gap between the sorted values."),
        Case("table.compare_distributions_for", "Fisher's iris: the energy distance between the sepal lengths of the "
             "species", "iris", "real data", option='show="energy distance"',
             ours="""
                 r = sdata.table(data).compare_distributions_for("Sepal.Length", for_each_group_in="Species",
                                                                 show="energy distance")
                 {"setosa-versicolor": r.get_cell_at(row=1, column="energy distance")}
             """,
             parent="""
                 from scipy import stats
                 s, v = (data.loc[data["Species"] == k, "Sepal.Length"] for k in ("setosa", "versicolor"))
                 {"setosa-versicolor": stats.energy_distance(s, v)}
             """, parent_label="SciPy stats.energy_distance",
             r="""
                 e <- function(a, b) sqrt(2 * mean(abs(outer(a, b, "-"))) - mean(abs(outer(a, a, "-")))
                                          - mean(abs(outer(b, b, "-"))))
                 list(`setosa-versicolor` = e(Sepal.Length[Species == "setosa"], Sepal.Length[Species == "versicolor"]))
             """, r_tolerance=1e-10),
    ]


def _sensitivity_and_censoring(Case):
    return [
        Case("sdata.find_sensitivity_of", "the Ishigami function: Sobol' indices against their exact values",
             "closed form (no data)", "published",
             ours="""
                 import math
                 r = sdata.find_sensitivity_of("sin(x1) + 7*sin(x2)**2 + 0.1*x3**4*sin(x1)",
                                               ranges={n: [-math.pi, math.pi] for n in ("x1", "x2", "x3")},
                                               how_many=16384)
                 {"S1 x1": r.get_cell_at(row=1, column="first-order index"),
                  "S1 x2": r.get_cell_at(row=2, column="first-order index"),
                  "ST x3": r.get_cell_at(row=3, column="total index")}
             """,
             published={"S1 x1": (0.3139, 0.01, "Saltelli et al. (2010), Ishigami a = 7, b = 0.1"),
                        "S1 x2": (0.4424, 0.01, "Saltelli et al. (2010)"),
                        "ST x3": (0.2437, 0.01, "Saltelli et al. (2010)")},
             parent="""
                 import math
                 import numpy as np
                 from scipy import stats
                 def f(x):
                     return (np.sin(x[0]) + 7 * np.sin(x[1]) ** 2 + 0.1 * x[2] ** 4 * np.sin(x[0])).reshape(1, -1)
                 found = stats.sobol_indices(func=f, n=16384, dists=[stats.uniform(-math.pi, 2 * math.pi)] * 3,
                                             rng=np.random.default_rng(1))
                 {"S1 x1": found.first_order.ravel()[0], "S1 x2": found.first_order.ravel()[1],
                  "ST x3": found.total_order.ravel()[2]}
             """, parent_label="SciPy stats.sobol_indices", parent_tolerance=1e-10,
             note="The indices come from a quasi-random sample, so they match the exact values to about 2 decimals."),
        Case("sdata.find_sensitivity_of", "mtcars: does weight or horsepower matter more for fuel use, over the "
             "cars' own ranges (the straight line of R lm(mpg ~ wt + hp))?", "mtcars", "real data",
             ours="""
                 ranges = {"wt": [data["wt"].min(), data["wt"].max()], "hp": [data["hp"].min(), data["hp"].max()]}
                 r = sdata.find_sensitivity_of("37.22727012 - 3.877830742*wt - 0.03177294704*hp", ranges=ranges,
                                               how_many=8192)
                 {"S1 wt": r.get_cell_at(row=1, column="first-order index"),
                  "S1 hp": r.get_cell_at(row=2, column="first-order index")}
             """,
             published={"S1 wt": (0.7399, 0.01, "a straight line: b^2 var(x) / the sum over both, var = range^2 / 12"),
                        "S1 hp": (0.2601, 0.01, "the same formula")},
             parent="""
                 import numpy as np
                 from scipy import stats
                 def f(x):
                     return (37.22727012 - 3.877830742 * x[0] - 0.03177294704 * x[1]).reshape(1, -1)
                 dists = [stats.uniform(data["wt"].min(), np.ptp(data["wt"])), stats.uniform(data["hp"].min(),
                                                                                        np.ptp(data["hp"]))]
                 found = stats.sobol_indices(func=f, n=8192, dists=dists, rng=np.random.default_rng(1)).first_order
                 {"S1 wt": found.ravel()[0], "S1 hp": found.ravel()[1]}
             """, parent_label="SciPy stats.sobol_indices", parent_tolerance=1e-10,
             note="The line's numbers are R lm(mpg ~ wt + hp) on mtcars; the exact indices of a straight line with "
                  "inputs spread evenly come from its formula."),
        Case("table.fit_distribution_to", "lung (R survival): a Weibull fit to the survival times, the living "
             "censored", "lung (survival)", "real data", option="censored_by=",
             ours="""
                 t = sdata.table(data)
                 t.add_group_column("still_alive", rules={'died == "no"': "yes"}, otherwise="no")
                 fit = t.fit_distribution_to("time", "weibull", censored_by="still_alive")
                 p = fit.show_parameters()
                 {"shape": p["shape"], "scale": p["scale"]}
             """,
             parent="""
                 from scipy import stats
                 seen = data.loc[data["died"] == "yes", "time"].to_numpy(float)
                 alive = data.loc[data["died"] == "no", "time"].to_numpy(float)
                 c, _, scale = stats.weibull_min.fit(stats.CensoredData(uncensored=seen, right=alive), floc=0)
                 {"shape": c, "scale": scale}
             """, parent_label="SciPy weibull_min.fit(CensoredData)", parent_tolerance=1e-4,
             r="""
                 f <- survival::survreg(survival::Surv(time, died == "yes") ~ 1, dist = "weibull")
                 list(shape = 1 / f$scale, scale = exp(unname(coef(f))))
             """, r_packages=("survival",), r_tolerance=1e-5,
             note="SciPy's search stops near the maximum; simplydata polishes it, so the fits agree to 4 or 5 digits."),
    ]


def cases(Case):
    return (_summaries(Case) + _cumulants(Case) + _circular(Case) + _bins(Case) + _tests(Case)
            + _powers_and_distances(Case)
            + _sensitivity_and_censoring(Case))
