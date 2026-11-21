"""Planning a study (phase S3b-2): the two power words, find_how_many_needed and find_chance_of_finding, and one
entry for each option that changes what they call (keyed by word and option): a percent's interval (R presize),
survival (R gsDesign, powerSurvEpi), regression (statsmodels FTestPowerF2), logistic regression (R pwrss), clusters
(the design effect), rank tests and your own distributions by simulation (SciPy stats.power) and your own function.
"""

from . import Entry

NEEDED = "sdata.find_how_many_needed"
CHANCE = "sdata.find_chance_of_finding"
SENTENCE = "simplydata also says the answer in a sentence that names the effect's scale, and rounds the number UP."
NUMBERS_IN_CODE = """
    import numpy as np
    one = np.array([1.0])  # the numbers are written in the R code
"""
NO_SURVIVAL = "Python has no power calculation for survival (statsmodels has none), so the numbers come from R."


ENTRIES = [
    Entry(
        word=NEEDED,
        ours="""
            result = sdata.find_how_many_needed(effect_size=0.5, power=0.8)
            result
        """,
        code={"statsmodels": """
            import math
            from statsmodels.stats.power import TTestIndPower
            # find_how_many_needed(effect_size=0.5, power=0.8)
            exact = TTestIndPower().solve_power(effect_size=0.5, power=0.8,
                                                alpha=0.05 / 2,           # (1)
                                                alternative="larger")
            {"values per group (exact)": exact,
             "values per group": math.ceil(exact)}                     # (2)
        """},
        compare="result",
        fields=("values per group (exact)", "values per group"),
        tolerance=1e-9,
        choices=("a two-sided test counts only the chance of finding the difference in the right direction, as R "
                 "power.t.test() (strict = FALSE): one side at half the significance level.",
                 "the number is rounded UP to a whole number."),
        also=SENTENCE + " It also names Cohen's rough size and warns that compare_averages_of uses Welch's t-test.",
    ),
    Entry(
        word=CHANCE,
        ours="""
            result = sdata.find_chance_of_finding(effect_size=0.5, values_per_group=30)
            result
        """,
        code={"statsmodels": """
            from statsmodels.stats.power import TTestIndPower
            # find_chance_of_finding(effect_size=0.5, values_per_group=30)
            power = TTestIndPower().solve_power(effect_size=0.5, nobs1=30, power=None,
                                                alpha=0.05 / 2,           # (1)
                                                alternative="larger")
            {"power": power}
        """},
        compare="result",
        fields=("power",),
        tolerance=1e-9,
        choices=("one side at half the significance level, as R power.t.test() (strict = FALSE).",),
        also=SENTENCE + " Below 80 % it points to find_how_many_needed.",
    ),
    # ------------------------------------------------------------ options of find_how_many_needed
    Entry(
        word=NEEDED, option="interval_width=",
        ours="""
            result = sdata.find_how_many_needed(interval_width=10, percents=[30])
            result
        """,
        code={"R": """
            # find_how_many_needed(interval_width=10, percents=[30])
            n <- presize::prec_prop(p = 0.3, conf.width = 0.10,
                                    method = "wilson")$n                # (1)
            list(exact = n, n = ceiling(n))
        """, "Python": """
            {"values (exact)": exact, "values": n}
        """},
        r_inputs=NUMBERS_IN_CODE, r_packages=("presize",), compare="result", fields=("values (exact)", "values"),
        tolerance=1e-9,
        choices=("the Wilson interval, given by name: presize's method= is a list of four and it warns when none is "
                 "chosen.",),
        python_note="Python has no function for the values needed for a percent's interval.",
        also="simplydata also takes the width in percentage points and says the answer in a sentence.",
    ),
    Entry(
        word=NEEDED, option="for_test=",
        ours="""
            result = sdata.find_how_many_needed(for_test="compare_survival", effect_size=0.7, percents=[30, 40])
            result
        """,
        code={"R": """
            # find_how_many_needed(for_test="compare_survival", effect_size=0.7, percents=[30, 40])
            d <- gsDesign::nEvents(hr = 0.7, alpha = 0.05, beta = 0.2,
                                   ratio = 1, sided = 2)                  # (1)
            n <- powerSurvEpi::ssizeEpi.default(power = 0.8, theta = 0.7,
                   p = 0.5, psi = mean(c(0.3, 0.4)), rho2 = 0)           # (2)
            list(d = d, events = ceiling(d), people = n)
        """, "Python": """
            {"events (exact)": d, "events": events, "people in all": people}
        """},
        r_inputs=NUMBERS_IN_CODE, r_packages=("gsDesign", "powerSurvEpi"), compare="result",
        fields=("events (exact)", "events", "people in all"), tolerance=1e-9,
        choices=("events first, by Schoenfeld's (1983) formula for the log-rank test, two groups of the same size.",
                 "people = events / the share of everyone expected to have the event (Schoenfeld; Hsieh & Lavori "
                 "2000), with the group a 0/1 column half of the people have (p = 0.5)."),
        python_note=NO_SURVIVAL,
        also="simplydata also says the hazard ratio in words, prints the events before the people, and notes that "
             "drop-out and recruitment time are not planned.",
    ),
    Entry(
        word=NEEDED, option="test_method=",
        ours="""
            result = sdata.find_how_many_needed(for_test="compare_survival", effect_size=0.7, percents=[30, 40],
                                                test_method="freedman")
            result
        """,
        code={"R": """
            # find_how_many_needed(for_test="compare_survival", ..., test_method="freedman")
            n <- powerSurvEpi::ssizeCT.default(power = 0.8, k = 1, pE = 0.3,
                   pC = 0.4, RR = 0.7, alpha = 0.05)                      # (1)
            list(n = n[1])
        """, "Python": """
            {"people per group": n}
        """},
        r_inputs=NUMBERS_IN_CODE, r_packages=("powerSurvEpi",), compare="result", fields=("people per group",),
        tolerance=1e-9,
        choices=("Freedman's (1982) formula, two groups of the same size (k = 1); the first percent is the group "
                 "whose hazard is effect_size= times the second's.",),
        python_note=NO_SURVIVAL,
        also="simplydata also says the answer in a sentence and gives the power with that many people.",
    ),
    Entry(
        word=NEEDED, option="using=",
        ours="""
            result = sdata.find_how_many_needed(for_test="explain", effect_size=0.15, using=["temperature", "salinity",
                                                "depth"])
            result
        """,
        code={"statsmodels": """
            import math
            from statsmodels.stats.power import FTestPowerF2
            # find_how_many_needed(for_test="explain", effect_size=0.15, using=[3 columns])
            v = FTestPowerF2().solve_power(effect_size=0.15, df_num=3,
                                           df_denom=None, alpha=0.05,
                                           power=0.8)                     # (1)
            rows = v + 3 + 1                                              # (2)
            {"rows (exact)": rows, "rows": math.ceil(rows)}
        """},
        compare="result", fields=("rows (exact)", "rows"), tolerance=1e-9,
        choices=("FTestPowerF2, statsmodels' class with the degrees of freedom named the right way round (as R "
                 "pwr::pwr.f2.test(), Cohen 1988 chapter 9).",
                 "the rows are the denominator degrees of freedom plus the columns plus 1."),
        also="simplydata also names the columns in the sentence, takes against= for the columns in one model and "
             "not the other (as compare_models), and gives Cohen's rough size for f².",
    ),
    Entry(
        word=NEEDED, option="outcome=",
        ours="""
            result = sdata.find_how_many_needed(for_test="explain", outcome="yes or no", using=["dose"], percents=[50],
                                                effect_size=1.5, power=0.95)
            result
        """,
        code={"R": """
            # find_how_many_needed(for_test="explain", outcome="yes or no", ...)
            r <- pwrss::power.z.logistic(base.prob = 0.5, odds.ratio = 1.5,
                   power = 0.95, alpha = 0.05, distribution = "normal",   # (1)
                   method = "demidenko(vc)",                               # (2)
                   ceil.n = FALSE, verbose = 0)
            list(n = r$n)
        """, "Python": """
            {"values (exact)": n}
        """},
        r_inputs=NUMBERS_IN_CODE, r_packages=("pwrss",), compare="result", fields=("values (exact)",),
        tolerance=1e-9,
        choices=("one bell-shaped (normal) column; the odds ratio is per standard deviation of it, and percents= is "
                 "the percent with the outcome at its average.",
                 "Demidenko's (2007) formula with the variance correction: 337 in the G*Power manual's example, as "
                 "G*Power gives (Hsieh's formula gives 317)."),
        python_note="Python has no power calculation for logistic regression.",
        also="simplydata also says the odds ratio in words, shows how to turn an odds ratio per unit into one per "
             "standard deviation, and gives the power with that many values.",
    ),
    Entry(
        word=NEEDED, option="in_clusters_of=",
        ours="""
            result = sdata.find_how_many_needed(effect_size=0.5, in_clusters_of=20, alike_within_clusters=0.05)
            result
        """,
        code={"statsmodels": """
            import math
            from statsmodels.stats.power import TTestIndPower
            # find_how_many_needed(effect_size=0.5, in_clusters_of=20, alike_within_clusters=0.05)
            n = TTestIndPower().solve_power(effect_size=0.5, power=0.8,
                                            alpha=0.05 / 2, alternative="larger")
            design = 1 + (20 - 1) * 0.05                                  # (1)
            values = math.ceil(n * design)                                # (2)
            {"design effect": design, "values per group": values,
             "clusters per group": math.ceil(values / 20)}
        """},
        compare="result", fields=("design effect", "values per group", "clusters per group"), tolerance=1e-9,
        choices=("the design effect 1 + (m - 1) x ICC (Donner & Klar 2000): simplydata's own arithmetic, the one "
                 "line it adds to the package's answer.",
                 "the independent number times the design effect, rounded up; then whole clusters."),
        also="simplydata also says what one cluster counts as, adds a note when there are fewer than about 10 "
             "clusters in each group, and works the same way on compare_counts and find_chance_of_finding (the "
             "values divided by the design effect).",
    ),
    Entry(
        word=NEEDED, option="based_on=",
        ours="""
            result = sdata.find_how_many_needed(effect_size=0.5, based_on="ranks")
            result
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            # find_how_many_needed(effect_size=0.5, based_on="ranks"): the power at 68
            rng = np.random.default_rng(1)                                # (1)
            def test(x, y, axis=-1):
                return stats.mannwhitneyu(x, y, axis=axis, method="asymptotic",
                                          use_continuity=True).pvalue     # (2)
            r = stats.power(test, (rng.standard_normal, lambda size: rng.normal(0.5, 1, size)),
                            (68, 68), significance=0.05, n_resamples=10000,
                            batch=1000)                                   # (3)
            {"values per group": 68, "power with that many": r.power}
        """},
        compare="result", fields=("values per group", "power with that many"), tolerance=1e-9,
        choices=("seeded (with_seed=1), so the answer repeats.",
                 "the very test compare_averages_of(based_on=\"ranks\") runs: Mann-Whitney, exact below 50 values in "
                 "each group, else the normal approximation with continuity correction.",
                 "significance given (SciPy's default is 0.01), 10000 tries drawn 1000 at a time; simplydata reads "
                 "such powers for a range of numbers and takes the smallest that reaches power= (here 68)."),
        also="simplydata also starts its search at the t-test answer, prints the Monte Carlo error as a 95 % "
             "interval (statsmodels proportion_confint, Wilson), and simulates Wilcoxon's signed-rank test for "
             "compare_before_and_after.",
    ),
    # ------------------------------------------------------------ options of find_chance_of_finding
    Entry(
        word=CHANCE, option="drawing_from=",
        ours="""
            a = sdata.distribution("lognormal", log_average=0, log_standard_deviation=1)
            b = sdata.distribution("lognormal", log_average=0.5, log_standard_deviation=1)
            result = sdata.find_chance_of_finding(drawing_from=[a, b], values_per_group=20)
            result
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            # find_chance_of_finding(drawing_from=[a, b], values_per_group=20)
            rng = np.random.default_rng(1)                                # (1)
            a = stats.lognorm(s=1, scale=np.exp(0))
            b = stats.lognorm(s=1, scale=np.exp(0.5))
            def test(x, y, axis=-1):
                return stats.ttest_ind(x, y, equal_var=False, axis=axis).pvalue  # (2)
            r = stats.power(test, (lambda size: a.rvs(size=size, random_state=rng),
                                   lambda size: b.rvs(size=size, random_state=rng)),
                            (20, 20), significance=0.05, n_resamples=10000, batch=1000)
            {"power": r.power}
        """},
        compare="result", fields=("power",), tolerance=1e-9,
        choices=("seeded (with_seed=1, tries=10000, drawn 1000 at a time), so the answer repeats.",
                 "the test compare_averages_of runs: Welch's t-test (based_on=\"ranks\" gives Mann-Whitney)."),
        also="simplydata also gives a power curve for a list of values_per_group= (one row each), prints the Monte "
             "Carlo error as a 95 % interval, and simulates compare_before_and_after (one distribution of the changes) "
             "and compare_spreads_of (Levene's test).",
    ),
    Entry(
        word=CHANCE, option="by_running=",
        ours="""
            import numpy as np
            from scipy import stats
            def one_study(seed):
                rng = np.random.default_rng(seed)
                return stats.ttest_ind(rng.normal(0, 1, 20), rng.normal(0.8, 1, 20)).pvalue
            result = sdata.find_chance_of_finding(by_running=one_study, tries=500)
            result
        """,
        code={"Python": """
            import numpy as np
            from scipy import stats
            # find_chance_of_finding(by_running=one_study, tries=500)
            def one_study(seed):
                rng = np.random.default_rng(seed)
                return stats.ttest_ind(rng.normal(0, 1, 20), rng.normal(0.8, 1, 20)).pvalue
            p = [one_study(seed) for seed in range(1, 501)]               # (1)
            found = sum(v < 0.05 for v in p)                              # (2)
            {"p-values below significance": found, "power": found / 500}
        """},
        compare="result", fields=("p-values below significance", "power"), tolerance=1e-12,
        choices=("your function, run once per seed: 1, 2, ... 500 (with_seed=1, tries=500).",
                 "the p-values below significance= are counted, as SciPy stats.power counts them."),
        also="simplydata also silences the printing of simplydata words inside your function, refuses a function "
             "that gives the same p-value every time (it ignores its seed), and prints the Monte Carlo error.",
    ),
]
