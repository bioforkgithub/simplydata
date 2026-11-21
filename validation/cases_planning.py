"""The reliability study for phase S3b-2, planning a study: the new routes of sdata.find_how_many_needed and
sdata.find_chance_of_finding (a percent's interval, survival by Schoenfeld and Freedman, regression with Cohen's f²,
logistic regression, clusters, rank tests and other distributions by simulation, and your own simulation).

There are no data here: the published answers are worked examples printed in manuals and papers (facts, not covered
by copyright), and each case also runs the package underneath (statsmodels, SciPy) or R itself. cases.py loads this
file at its end and calls add_to(), which adds the sources as datasets that load() gives as None.
"""

from __future__ import annotations

GPOWER = "G*Power 3.1 manual"
STATA = "Stata power manuals"
PRESIZE = "presize paper (JOSS)"
PWR = "pwr manual and vignette"
BLAND = "Bland, sample size in cluster trials"
CHECKS = "checks against R (no published example)"
NO_DATA = (GPOWER, STATA, PRESIZE, PWR, BLAND, CHECKS)


def _datasets(Dataset):
    facts = "No data: published worked examples (facts); only the numbers printed there are quoted, nothing is stored."
    return [
        Dataset(GPOWER, "", "worked examples of the G*Power manual: logistic regression with one normal column "
                            "(chapter 29.4) and the multiple-regression F test (chapter 13.3.1, Cohen 1988 example 9.1)",
                "Faul, F., Erdfelder, E., Buchner, A. & Lang, A.-G. G*Power 3.1 manual (2023), sections 13.3.1 and "
                "29.4; Faul et al. (2009). Behavior Research Methods 41, 1149-1160; Cohen, J. (1988). Statistical "
                "Power Analysis for the Behavioral Sciences, 2nd ed., p. 424.", facts,
                "https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower"),
        Dataset(STATA, "", "worked examples of the Stata power manuals: the log-rank test by Schoenfeld's and by "
                           "Freedman's formula, and two averages in clusters",
                "StataCorp. Stata Power, Precision, and Sample-Size Reference Manual: [PSS-2] power logrank, "
                "examples 1, 2 and 5 (example 5 from Machin, D. et al. (2009). Sample Size Tables for Clinical "
                "Studies, 3rd ed., p. 91); [PSS-2] power twomeans, cluster, example 1 (from Ahn, C., Heo, M. & "
                "Zhang, S. (2015). Sample Size Calculations for Clustered and Longitudinal Outcomes in Clinical "
                "Research, p. 37).", facts, "https://www.stata.com/manuals/pss-2powerlogrank.pdf"),
        Dataset(PRESIZE, "", "the worked example of presize's paper: the values needed for a 95 % Wilson interval of "
                             "a percent near 15 % that is 5 points wide",
                "Haynes, A. G., Lenz, A., Stalder, O. & Limacher, A. (2021). presize: An R-package for precision-based "
                "sample size calculation in clinical research. Journal of Open Source Software 6(60), 3118 (CC BY "
                "4.0).", facts, "https://doi.org/10.21105/joss.03118"),
        Dataset(PWR, "", "the pwr.f2.test example of the pwr vignette (Kutner et al., exercise 8.43): two columns "
                         "added, R squared 0.3, significance 0.001",
                "Champely, S. et al. pwr: Basic Functions for Power Analysis, vignette (pwr.f2.test); Kutner, M. H., "
                "Nachtsheim, C. J., Neter, J. & Li, W. (2005). Applied Linear Statistical Models, 5th ed., "
                "exercise 8.43.", facts, "https://cran.r-project.org/package=pwr"),
        Dataset(CHECKS, "", "no data: the inputs are written in the code, and R (or SciPy with the same seed) is the "
                            "reference; used where no published worked example was read",
                "simplydata's reliability study. Simulation checks follow Arnold, B. F., Hogan, D. R., Colford, J. M. "
                "& Hubbard, A. E. (2011). Simulation methods to estimate design power. BMC Medical Research "
                "Methodology 11, 94.", facts, "https://doi.org/10.1186/1471-2288-11-94"),
        Dataset(BLAND, "", "the design effect of a cluster trial with 30 people in each cluster and ICC 0.05",
                "Bland, J. M. Sample size in guidelines trials (University of York), section \"Sample size in "
                "cluster randomized studies\"; Kerry, S. M. & Bland, J. M. (1998). BMJ 316, 549.", facts,
                "https://www-users.york.ac.uk/~mb55/clust/bupa.htm"),
    ]


def _cases(Case):
    needed, chance = "sdata.find_how_many_needed", "sdata.find_chance_of_finding"
    first = "\n                 r = {call}.as_pandas().iloc[0]"
    return [
        # ---- the two words themselves (formulas as before S3b-2)
        Case(needed, "two averages, a medium difference (d = 0.5), 80 % power", CHECKS, "real data",
             ours=first.format(call="sdata.find_how_many_needed(effect_size=0.5, power=0.8)") + """
                 {"values per group (exact)": r["values per group (exact)"]}
             """,
             parent="""
                 from statsmodels.stats.power import TTestIndPower
                 {"values per group (exact)": TTestIndPower().solve_power(effect_size=0.5, power=0.8, alpha=0.025,
                                                                          alternative="larger")}
             """, parent_label="statsmodels TTestIndPower", parent_tolerance=1e-9,
             r="""
                 list(`values per group (exact)` = power.t.test(delta = 0.5, sd = 1, power = 0.8)$n)
             """, r_tolerance=1e-6,
             note="The formula route of before S3b-2, checked against R power.t.test() (whose root search stops at "
                  "about 6 digits)."),
        Case(chance, "two averages, d = 0.5, 30 values in each group", CHECKS, "real data",
             ours=first.format(call="sdata.find_chance_of_finding(effect_size=0.5, values_per_group=30)") + """
                 {"power": r["power"]}
             """,
             r="""
                 list(power = power.t.test(n = 30, delta = 0.5, sd = 1)$power)
             """, r_tolerance=1e-9),
        Case(needed, "using=: rows for a model of 3 columns, f squared 0.15", PWR, "real data",
             ours=first.format(call='sdata.find_how_many_needed(for_test="explain", effect_size=0.15, using=["temperature", '
                                    '"salinity", "depth"])') + """
                 {"rows (exact)": r["rows (exact)"], "rows": r["rows"]}
             """,
             r="""
                 v <- pwr::pwr.f2.test(u = 3, f2 = 0.15, sig.level = 0.05, power = 0.8)$v
                 list(`rows (exact)` = v + 3 + 1, rows = ceiling(v + 3 + 1))
             """, r_packages=("pwr",), r_tolerance=1e-6),
        Case(needed, "based_on=: Mann-Whitney, d = 0.5, the values needed by simulation", CHECKS, "real data",
             ours=first.format(call='sdata.find_how_many_needed(effect_size=0.5, based_on="ranks")') + """
                 {"values per group": r["values per group"], "power with that many": r["power with that many"]}
             """,
             parent="""
                 from scipy import stats
                 rng = np.random.default_rng(1)
                 def test(x, y, axis=-1):
                     return stats.mannwhitneyu(x, y, axis=axis, method="asymptotic", use_continuity=True).pvalue
                 r = stats.power(test, (rng.standard_normal, lambda size: rng.normal(0.5, 1, size)), (68, 68),
                                 significance=0.05, n_resamples=10000, batch=1000)
                 {"values per group": 68, "power with that many": float(r.power)}
             """, parent_label="SciPy stats.power at 68 (the same seed)", parent_tolerance=1e-12,
             note="SciPy with the same seed gives the same power at the number found; the t-test needs 64, and the "
                  "Mann-Whitney test about 5 % more (asymptotic relative efficiency 0.955)."),
        # ---- U06: a percent's interval
        Case(needed, "interval_width=: a 95 % Wilson interval of a percent near 15 % that is 5 points wide", PRESIZE,
             "published",
             ours=first.format(call="sdata.find_how_many_needed(interval_width=5, percents=[15])") + """
                 {"values (exact)": r["values (exact)"], "values": r["values"]}
             """,
             published={"values (exact)": (783.4897, 5e-5, "Haynes et al. (2021), JOSS"),
                        "values": (784, 0, "Haynes et al. (2021), JOSS")},
             r="""
                 n <- presize::prec_prop(p = 0.15, conf.width = 0.05, method = "wilson")$n
                 list(`values (exact)` = n, values = ceiling(n))
             """, r_packages=("presize",), r_tolerance=1e-9, ours_r=("presize",)),
        # ---- U13: survival
        Case(needed, "for_test=: events for a hazard ratio of 0.5 (log-rank, Schoenfeld)", STATA, "published",
             ours=first.format(call='sdata.find_how_many_needed(for_test="compare_survival", effect_size=0.5)') + """
                 {"events (exact)": r["events (exact)"], "events": r["events"]}
             """,
             published={"events": (66, 0, "Stata [PSS-2] power logrank, example 2")},
             r="""
                 d <- gsDesign::nEvents(hr = 0.5, alpha = 0.05, beta = 0.2, ratio = 1, sided = 2)
                 list(`events (exact)` = d, events = ceiling(d))
             """, r_packages=("gsDesign",), r_tolerance=1e-9, ours_r=("gsDesign",)),
        Case(needed, "for_test=: events for survival 50 % against 60 % (hazard ratio log 0.5 / log 0.6 = 1.36), one-sided", STATA,
             "published",
             ours=first.format(call='sdata.find_how_many_needed(for_test="compare_survival", '
                                    'effect_size=float(np.log(0.5) / np.log(0.6)), sides=1)') + """
                 {"events (exact)": r["events (exact)"], "events": r["events"]}
             """,
             published={"events": (266, 0, "Stata [PSS-2] power logrank, example 5 (Machin et al. 2009, p. 91)")},
             r="""
                 d <- gsDesign::nEvents(hr = log(0.5) / log(0.6), alpha = 0.05, beta = 0.2, ratio = 1, sided = 1)
                 list(`events (exact)` = d, events = ceiling(d))
             """, r_packages=("gsDesign",), r_tolerance=1e-9, ours_r=("gsDesign",)),
        Case(needed, "for_test=: events and people for a hazard ratio of 0.7, 30 % and 40 % with the event", STATA,
             "real data",
             ours=first.format(call='sdata.find_how_many_needed(for_test="compare_survival", effect_size=0.7, '
                                    'percents=[30, 40])') + """
                 {"events (exact)": r["events (exact)"], "people in all": r["people in all"],
                  "power with that many": r["power with that many"]}
             """,
             r="""
                 d <- gsDesign::nEvents(hr = 0.7, alpha = 0.05, beta = 0.2, ratio = 1, sided = 2)
                 n <- powerSurvEpi::ssizeEpi.default(power = 0.8, theta = 0.7, p = 0.5, psi = 0.35, rho2 = 0)
                 list(`events (exact)` = d, `people in all` = n,
                      `power with that many` = gsDesign::nEvents(hr = 0.7, alpha = 0.05, sided = 2, n = ceiling(d)))
             """, r_packages=("gsDesign", "powerSurvEpi"), r_tolerance=1e-9, ours_r=("gsDesign", "powerSurvEpi"),
             note="No published example with people was found for a hazard ratio of 0.7; R gsDesign and powerSurvEpi "
                  "are called directly."),
        Case(needed, "test_method=: Freedman's formula, hazard ratio 0.5, everyone followed to the event", STATA,
             "published",
             ours=first.format(call='sdata.find_how_many_needed(for_test="compare_survival", effect_size=0.5, '
                                    'percents=[100, 100], test_method="freedman")') + """
                 {"people per group": r["people per group"]}
             """,
             published={"people per group": (36, 0, "Stata [PSS-2] power logrank, example 1")},
             r="""
                 n <- powerSurvEpi::ssizeCT.default(power = 0.8, k = 1, pE = 1, pC = 1, RR = 0.5, alpha = 0.05)
                 list(`people per group` = n[[1]])
             """, r_packages=("powerSurvEpi",), r_tolerance=1e-9, ours_r=("powerSurvEpi",)),
        # ---- U09: regression
        Case(chance, "using=: power of the F test for 5 columns, R squared 0.10, 95 rows", GPOWER, "published",
             ours=first.format(call='sdata.find_chance_of_finding(for_test="explain", effect_size=0.1 / 0.9, using=5, '
                                    'values_per_group=95)') + """
                 {"power": r["power"]}
             """,
             published={"power": (0.673586, 5e-7, "G*Power manual 13.3.1 (Cohen 1988, example 9.1)")},
             parent="""
                 from statsmodels.stats.power import FTestPowerF2
                 {"power": FTestPowerF2().power(effect_size=0.1 / 0.9, df_num=5, df_denom=95 - 5 - 1, alpha=0.05)}
             """, parent_label="statsmodels FTestPowerF2", parent_tolerance=1e-12,
             r="""
                 list(power = pwr::pwr.f2.test(u = 5, v = 89, f2 = 0.1 / 0.9, sig.level = 0.05)$power)
             """, r_packages=("pwr",), r_tolerance=1e-9),
        Case(needed, "against=: rows for 2 columns added to 1, R squared 0.3, significance 0.001", PWR, "published",
             ours=first.format(call='sdata.find_how_many_needed(for_test="compare_models", effect_size=0.3 / 0.7, '
                                    'using=["x1"], against=["x1", "x2", "x3"], significance=0.001)') + """
                 {"rows (exact)": r["rows (exact)"]}
             """,
             published={"rows (exact)": (49.88971 + 3 + 1, 5e-5, "pwr vignette, pwr.f2.test (v = 49.88971)")},
             r="""
                 v <- pwr::pwr.f2.test(u = 2, f2 = 0.3 / 0.7, sig.level = 0.001, power = 0.8)$v
                 list(`rows (exact)` = v + 3 + 1)
             """, r_packages=("pwr",), r_tolerance=1e-6,
             note="The rows are pwr's v (the denominator degrees of freedom) plus the 3 columns of the bigger model "
                  "plus 1; pwr's root search stops at about 6 digits."),
        # ---- U11: logistic regression
        Case(needed, "outcome=: logistic regression, odds ratio 1.5 per standard deviation, 50 % at the average, "
                     "power 0.95", GPOWER, "published",
             ours=first.format(call='sdata.find_how_many_needed(for_test="explain", outcome="yes or no", using=["x"], '
                                    'percents=[50], effect_size=1.5, power=0.95)') + """
                 {"values (exact)": r["values (exact)"], "values": r["values"]}
             """,
             published={"values": (337, 0, "G*Power manual 29.4 (Demidenko 2007 with variance correction)")},
             r="""
                 r <- pwrss::power.z.logistic(base.prob = 0.5, odds.ratio = 1.5, power = 0.95, alpha = 0.05,
                                              distribution = "normal", method = "demidenko(vc)", ceil.n = FALSE,
                                              verbose = 0)
                 list(`values (exact)` = r$n, values = ceiling(r$n))
             """, r_packages=("pwrss",), r_tolerance=1e-9, ours_r=("pwrss",),
             note="The G*Power manual prints 337 with the variance correction, 355 without it and 317 by Hsieh et "
                  "al. (1998); simplydata uses the first, as G*Power does."),
        # ---- U15: clusters
        Case(needed, "in_clusters_of=: two averages in clusters of 20, ICC 0.025", STATA, "published",
             ours=first.format(call="sdata.find_how_many_needed(difference=1.1, spread=3.67, in_clusters_of=20, "
                                    "alike_within_clusters=0.025)") + """
                 {"clusters per group": r["clusters per group"], "values in whole clusters": r["values in whole clusters"],
                  "values per group (before rounding)": r["values per group if independent (exact)"]
                                                        * r["design effect"]}
             """,
             published={"clusters per group": (13, 0, "Stata [PSS-2] power twomeans, cluster, example 1"),
                        "values in whole clusters": (260, 0, "Stata [PSS-2] power twomeans, cluster, example 1")},
             r="""
                 e <- epiR::epi.sscompc(treat = 1.1, control = 0, sigma = 3.67, n = NA, power = 0.8, r = 1,
                                        design = 1 + (20 - 1) * 0.025, sided.test = 2, nfractional = TRUE,
                                        conf.level = 0.95)
                 list(`values per group (before rounding)` = e$n.treat)
             """, r_packages=("epiR",), r_tolerance=0.01,
             note="epiR multiplies by the same design effect but starts from the normal (z) formula, which needs a "
                  "little less than the t-test (257.7 against 259.2 values per group); the check allows 1 %. This "
                  "design effect is simplydata's own arithmetic, pending the owner's approval."),
        Case(needed, "in_clusters_of=: the design effect of clusters of 30 with ICC 0.05", BLAND, "published",
             ours=first.format(call="sdata.find_how_many_needed(effect_size=0.5, in_clusters_of=30, "
                                    "alike_within_clusters=0.05)") + """
                 {"design effect": r["design effect"]}
             """,
             published={"design effect": (2.45, 5e-3, "Bland, Sample size in guidelines trials")}),
        # ---- U07: rank tests by simulation
        Case(chance, "based_on=: Mann-Whitney power, d = 0.5, 64 values in each group, by simulation", CHECKS,
             "real data",
             ours=first.format(call='sdata.find_chance_of_finding(effect_size=0.5, values_per_group=64, '
                                    'based_on="ranks")') + """
                 {"power": r["power"]}
             """,
             parent="""
                 from scipy import stats
                 rng = np.random.default_rng(1)
                 def test(x, y, axis=-1):
                     return stats.mannwhitneyu(x, y, axis=axis, method="asymptotic", use_continuity=True).pvalue
                 r = stats.power(test, (rng.standard_normal, lambda size: rng.normal(0.5, 1, size)), (64, 64),
                                 significance=0.05, n_resamples=10000, batch=1000)
                 {"power": float(r.power)}
             """, parent_label="SciPy stats.power (the same seed)", parent_tolerance=1e-12,
             r="""
                 set.seed(1)
                 p <- replicate(10000, stats::wilcox.test(stats::rnorm(64), stats::rnorm(64, 0.5))$p.value)
                 list(power = mean(p < 0.05))
             """, r_tolerance=0.03,
             note="R draws its own random numbers, so the check allows the Monte Carlo error of both (about 0.8 "
                  "percentage points each); SciPy with the same seed gives the same number."),
        # ---- U16: other distributions and your own function
        Case(chance, "drawing_from=: Welch's t-test on two lognormal groups of 20, by simulation", CHECKS,
             "real data",
             ours="""
                 a = sdata.distribution("lognormal", log_average=0, log_standard_deviation=1)
                 b = sdata.distribution("lognormal", log_average=0.5, log_standard_deviation=1)
                 r = sdata.find_chance_of_finding(drawing_from=[a, b], values_per_group=20).as_pandas().iloc[0]
                 {"power": r["power"]}
             """,
             r="""
                 set.seed(1)
                 p <- replicate(10000, stats::t.test(stats::rlnorm(20, 0, 1), stats::rlnorm(20, 0.5, 1))$p.value)
                 list(power = mean(p < 0.05))
             """, r_tolerance=0.06,
             note="R draws its own random numbers; at a power near 23 % the Monte Carlo error of each is about 0.8 "
                  "percentage points, so the check allows 6 % of the power."),
        Case(chance, "by_running=: logistic regression simulated with statsmodels, against R pwrss", CHECKS,
             "real data",
             ours="""
                 import statsmodels.api as sm
                 def one_study(seed):
                     rng = np.random.default_rng(seed)
                     x = rng.standard_normal(150)
                     y = rng.random(150) < 1 / (1 + np.exp(-np.log(1.5) * x))
                     return sm.Logit(y.astype(float), sm.add_constant(x)).fit(disp=0).pvalues[1]
                 r = sdata.find_chance_of_finding(by_running=one_study, tries=2000).as_pandas().iloc[0]
                 {"power": r["power"]}
             """,
             r="""
                 r <- pwrss::power.z.logistic(base.prob = 0.5, odds.ratio = 1.5, n = 150, alpha = 0.05,
                                              distribution = "normal", method = "demidenko(vc)", verbose = 0)
                 list(power = r$power)
             """, r_packages=("pwrss",), r_tolerance=0.06,
             note="2000 simulated studies (Wald test of statsmodels Logit) against the formula of R pwrss: the "
                  "Monte Carlo error is about 1 percentage point, and the formula is an approximation, so the check "
                  "allows 6 % of the power."),
    ]


def add_to(namespace) -> None:
    """Add the S3b-2 sources and cases to cases.py; load() gives None for the sources (they hold no data)."""
    import dataclasses

    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    for c in _cases(Case):
        head = c.title.split(":")[0]
        option = head if head.endswith("=") and " " not in head else ""
        namespace["CASES"].append(dataclasses.replace(c, option=option))
    plain_load = namespace["load"]

    def load(name: str):
        if name in NO_DATA:
            return None
        return plain_load(name)

    namespace["load"] = load
