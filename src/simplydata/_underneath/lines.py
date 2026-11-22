"""Lines and curves (phase S3a-2): the new words fit_dose_response (table and chart) and find_best_power_of, and
one entry for each new option of fit_line, fit_curve, explain, add_smoothed_column and draw_smooth_line
(keyed by word and option, as in models.py: "table.fit_line with_bends=").
"""

from . import Entry

SENTENCE = "simplydata also writes the result as sentences, with the p-value in words, and names the method."
CHEMICAL_A = """
    tox = sdata.get_example("toxicity")
    a = tox[tox["chemical"] == "A"]
    concentration = a["concentration"].to_numpy(dtype=float)
    root_length = a["root_length"].to_numpy(dtype=float)
"""
FLASK_A = """
    culture = sdata.get_example("culture")
    a = culture[culture["flask"] == "A"]
    hour = a["hour"].to_numpy(dtype=float)
    density = a["density"].to_numpy(dtype=float)
"""
MARKS = """
    marks_table = sdata.get_example("marks")
    hours = marks_table["hours"].to_numpy(dtype=float)
    marks = marks_table["marks"].to_numpy(dtype=float)
"""

ENTRIES = [
    Entry(
        word="table.fit_dose_response",
        data="toxicity",
        ours="""
            table = sdata.table(sdata.get_example("toxicity"))
            table.keep_rows_where("chemical", is_equal_to="A")
            table.fit_dose_response(x="concentration", y="root_length").keep_rows_where("term", is_equal_to="ED50")
        """,
        code={
            "R": """
                # fit_dose_response(x="concentration", y="root_length")
                # concentration and root_length: chemical A of sdata.get_example("toxicity")
                m <- drc::drm(root_length ~ concentration, fct = drc::LL.4())   # (1)
                e <- drc::ED(m, 50, interval = "delta", display = FALSE)       # (2)
                list(estimate = e[1, 1], se = e[1, 2], low = e[1, 3], high = e[1, 4])
            """,
            "Python": """
                {"estimate": estimate, "standard error": se, "95 % CI low": low, "95 % CI high": high}
            """,
        },
        r_inputs=CHEMICAL_A,
        r_packages=("drc",),
        compare="result",
        fields=("estimate", "standard error", "95 % CI low", "95 % CI high"),
        tolerance=1e-9,
        choices=("the 4 parameter log-logistic curve, the usual one in ecotoxicology (drc's LL.4); "
                 "of_kind= chooses another.",
                 "the ED50 with its delta-method interval: drc's ED() gives no interval unless asked "
                 "(interval = \"none\" is its default)."),
        python_note="Python has no dose-response package with drc's ED intervals: SciPy curve_fit fits the curve "
                    "but gives no ED50 interval, so the numbers come from R.",
        also="simplydata also prints the upper and lower limits, a test of no dose effect (drc::noEffect) and a "
             "note when an ED lies outside the doses tested. " + SENTENCE,
    ),
    Entry(
        word="fit_dose_response",
        data="toxicity",
        ours="""
            tox = sdata.get_example("toxicity")
            chart = sdata.chart(tox[tox["chemical"] == "A"])
            chart.draw_dots(x="concentration", y="root_length").fit_dose_response()
        """,
        code={
            "R": """
                # fit_dose_response()
                m <- drc::drm(root_length ~ concentration, fct = drc::LL.4())    # (1)
                low_dose <- min(concentration[concentration > 0])
                at <- c(0, exp(seq(log(low_dose), log(max(concentration)), length.out = 300)))  # (2)
                e <- drc::ED(m, 50, interval = "delta", display = FALSE)
                list(at = at, fitted = unname(predict(m, newdata = data.frame(concentration = at))),
                     ed50 = e[1, 1], low = e[1, 3], high = e[1, 4])
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.plot(at, fitted)          # the fitted curve
            """,
        },
        r_inputs=CHEMICAL_A,
        r_packages=("drc",),
        compare="chart",
        check=("lines",),
        legend_pattern=r"ED50 (\S+) \(95 % CI (\S+) to (\S+)\)",
        legend_numbers=("ed50", "low", "high"),
        tolerance=1e-6,
        choices=("the 4 parameter log-logistic curve (drc's LL.4), as table.fit_dose_response.",
                 "the curve is drawn over 300 doses spaced evenly on a log scale (and dose 0), so it stays smooth on "
                 "a log dose axis too; the ED50 and its delta-method interval go in the legend."),
        python_note="Python has no dose-response package with drc's ED intervals, so the curve comes from R.",
        also="simplydata also fits one curve per colour group and labels each with its ED50.",
    ),
    Entry(
        word="table.find_best_power_of",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            table.find_best_power_of("days")
        """,
        code={"SciPy": """
            from scipy import stats
            df = sdata.get_example("trial")
            # find_best_power_of("days")
            _, power, (low, high) = stats.boxcox(df["days"].dropna(), alpha=0.05)   # (1)
            {"power": power, "95 % CI low": low, "95 % CI high": high}
        """},
        compare="result",
        fields=("power", "95 % CI low", "95 % CI high"),
        tolerance=1e-9,
        choices=("the power's 95 % interval from the profile likelihood (alpha=0.05); without alpha= SciPy gives "
                 "no interval.",),
        also="simplydata also names the simple power inside the interval (such as the square root), says whether "
             "log and no change are inside it, and with using= asks R car::powerTransform() for the model's power. "
             + SENTENCE,
    ),
]


OPTION_ENTRIES = [
    Entry(
        word="table.fit_line",
        option='test_method="theil-sen"',
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.fit_line(x="hours", y="marks", test_method="theil-sen")
        """,
        code={"SciPy": """
            from scipy import stats
            df = sdata.get_example("marks")
            # fit_line(x="hours", y="marks", test_method="theil-sen")
            fit = stats.theilslopes(df["marks"], df["hours"], alpha=0.95,      # (1)
                                    method="separate")                        # (2)
            {"slope": fit.slope, "intercept": fit.intercept,
             "slope 95 % CI low": fit.low_slope, "slope 95 % CI high": fit.high_slope}
        """},
        compare="result",
        fields=("slope", "intercept", "slope 95 % CI low", "slope 95 % CI high"),
        choices=("SciPy's alpha= is the confidence level (0.95), not the error rate.",
                 "the intercept is median(y) - slope * median(x) (Conover; SciPy's default); R mblm takes the "
                 "median of y - slope * x instead."),
        also="test_method=\"siegel\" is SciPy stats.siegelslopes(method=\"hierarchical\") in the same way. " + SENTENCE,
    ),
    Entry(
        word="table.fit_line",
        option='test_method="standardised major axis"',
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.fit_line(x="hours", y="marks", test_method="standardised major axis")
        """,
        code={
            "R": """
                # fit_line(x="hours", y="marks", test_method="standardised major axis")
                f <- smatr::sma(marks ~ hours, method = "SMA")       # (1)
                k <- f$coef[[1]]
                list(slope = k[2, 1], low = k[2, 2], high = k[2, 3], intercept = k[1, 1])
            """,
            "Python": """
                {"slope": slope, "slope 95 % CI low": low, "slope 95 % CI high": high, "intercept": intercept}
            """,
        },
        r_inputs=MARKS,
        r_packages=("smatr",),
        compare="result",
        fields=("slope", "slope 95 % CI low", "slope 95 % CI high", "intercept"),
        choices=("smatr's own 95 % intervals (Warton et al. 2006); test_method=\"major axis\" is method = \"MA\".",),
        python_note="Python has no standardised major axis line with smatr's intervals, so the numbers come from R.",
        also="simplydata also says which question the line answers and tests the correlation. " + SENTENCE,
    ),
    Entry(
        word="table.fit_line",
        option='test_method="deming", y_error_over_x_error=',
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.fit_line(x="hours", y="marks", test_method="deming", y_error_over_x_error=4)
        """,
        code={
            "R": """
                # fit_line(x="hours", y="marks", test_method="deming", y_error_over_x_error=4)
                m <- mcr::mcreg(hours, marks, error.ratio = 1 / 4,          # (1)
                                method.reg = "Deming", method.ci = "analytical")   # (2)
                list(slope = m@para[2, "EST"], se = m@para[2, "SE"], intercept = m@para[1, "EST"])
            """,
            "Python": """
                {"slope": slope, "slope standard error": se, "intercept": intercept}
            """,
        },
        r_inputs=MARKS,
        r_packages=("mcr",),
        compare="result",
        fields=("slope", "slope standard error", "intercept"),
        choices=("mcr's error.ratio is the error variance of x over that of y, the other way round from "
                 "y_error_over_x_error=, so it gets 1 / 4.",
                 "mcr's analytical intervals; its default (bootstrap) is random and differs from run to run."),
        python_note="Python has no Deming line with mcr's intervals, so the numbers come from R.",
        also="simplydata also says which question the line answers. " + SENTENCE,
    ),
    Entry(
        word="table.fit_line",
        option='test_method="passing-bablok"',
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.fit_line(x="hours", y="marks", test_method="passing-bablok")
        """,
        code={
            "R": """
                # fit_line(x="hours", y="marks", test_method="passing-bablok")
                m <- mcr::mcreg(hours, marks, method.reg = "PaBa",
                                method.ci = "analytical")          # (1)
                list(slope = m@para[2, "EST"], low = m@para[2, "LCI"], intercept = m@para[1, "EST"])
            """,
            "Python": """
                {"slope": slope, "slope 95 % CI low": low, "intercept": intercept}
            """,
        },
        r_inputs=MARKS,
        r_packages=("mcr",),
        compare="result",
        fields=("slope", "slope 95 % CI low", "intercept"),
        choices=("Passing and Bablok's own rank-based intervals (mcr's \"analytical\" for PaBa); mcr's default "
                 "bootstrap is random.",),
        python_note="Python has no Passing-Bablok line with mcr's intervals, so the numbers come from R.",
        also="simplydata also warns below 30 pairs and refuses fewer than 10. " + SENTENCE,
    ),
    Entry(
        word="table.fit_line",
        option="with_bends=",
        data="culture",
        ours="""
            table = sdata.table(sdata.get_example("culture"))
            table.keep_rows_where("flask", is_equal_to="A")
            table.fit_line(x="hour", y="density", with_bends=1)
        """,
        code={
            "R": """
                # fit_line(x="hour", y="density", with_bends=1)
                o <- lm(density ~ hour)
                s <- segmented::segmented(o, seg.Z = ~ hour, npsi = 1,
                                          control = segmented::seg.control(seed = 1))   # (1)
                sl <- segmented::slope(s, digits = 15)$hour
                list(bend = s$psi[1, "Est."], before = sl[1, 1], after = sl[2, 1],
                     davies = segmented::davies.test(o, seg.Z = ~ hour)$p.value)   # (2)
            """,
            "Python": """
                {"bend 1": bend, "slope 1": before, "slope 2": after, "Davies p-value": davies}
            """,
        },
        r_inputs=FLASK_A,
        r_packages=("segmented",),
        compare="result",
        fields=("bend 1", "slope 1", "slope 2", "Davies p-value"),
        tolerance=1e-9,
        choices=("a continuous line: it bends, it does not jump (segmented's model); seed 1 fixes segmented's "
                 "random restarts.",
                 "Davies' test of \"no bend at all\": the bend's own p-value is not valid, because the data chose "
                 "where it is."),
        python_note="Python has no segmented regression with the bend's interval and Davies' test, so the numbers "
                    "come from R.",
        also="simplydata also prints the bend's 95 % interval and each slope's. " + SENTENCE,
    ),
    Entry(
        word="table.fit_line",
        option="changes_at=",
        data="culture",
        ours="""
            table = sdata.table(sdata.get_example("culture"))
            table.keep_rows_where("flask", is_equal_to="A")
            table.fit_line(x="hour", y="density", changes_at=10)
        """,
        code={"statsmodels": """
            import statsmodels.formula.api as smf
            df = sdata.get_example("culture").query("flask == 'A'")
            # fit_line(x="hour", y="density", changes_at=10)
            df = df.assign(after=(df["hour"] >= 10) * 1.0)               # (1)
            df = df.assign(since=df["after"] * (df["hour"] - 10))
            fit = smf.ols("density ~ hour + after + since", df).fit()
            {"level change": fit.params["after"], "slope change": fit.params["since"],
             "level change p-value": fit.pvalues["after"]}
        """},
        compare="result",
        fields=("level change", "slope change", "level change p-value"),
        choices=("the change starts at the point itself: rows at 10 or later count as after.",),
        also="simplydata also prints the lag-1 autocorrelation of the leftovers (statsmodels acf), which an "
             "interrupted time series must check (Bernal et al. 2017). " + SENTENCE,
    ),
    Entry(
        word="table.fit_curve",
        option='of_kind="logistic growth"',
        data="culture",
        ours="""
            table = sdata.table(sdata.get_example("culture"))
            table.keep_rows_where("flask", is_equal_to="A")
            table.fit_curve(x="hour", y="density", of_kind="logistic growth")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import optimize
            df = sdata.get_example("culture").query("flask == 'A'")
            # fit_curve(x="hour", y="density", of_kind="logistic growth")
            def logistic(x, Asym, xmid, scal):                  # R's SSlogis
                return Asym / (1 + np.exp((xmid - x) / scal))
            found, cov = optimize.curve_fit(logistic, df["hour"], df["density"],
                                            p0=[1, 10, 2], method="lm")    # (1)
            {"estimate": found[0], "standard error": np.sqrt(cov[0, 0])}
        """},
        compare="result",
        fields=("estimate", "standard error"),
        tolerance=1e-5,
        choices=("start values: simplydata takes them from R's self-starting model (stats::getInitial()), or "
                 "searches the whole range without R; the least-squares answer is the same.",),
        also="simplydata also writes the formula, says what each value means and gives its 95 % interval. "
             + SENTENCE,
    ),
    Entry(
        word="table.explain",
        option="for_percentile=",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.explain("marks", using=["hours"], for_percentile=90)
        """,
        code={
            "R": """
                # explain("marks", using=["hours"], for_percentile=90)
                f <- quantreg::rq(marks ~ hours, tau = 0.9)           # (1)
                s <- summary(f, se = "nid")$coefficients             # (2)
                list(estimate = s[1, 1], se = s[1, 2], p = s[1, 4])
            """,
            "Python": """
                {"estimate": estimate, "standard error": se, "p-value": p}
            """,
        },
        r_inputs=MARKS,
        r_packages=("quantreg",),
        compare="result",
        fields=("estimate", "standard error", "p-value"),
        choices=("R quantreg's exact simplex (Barrodale-Roberts); statsmodels QuantReg gives the same line to "
                 "about 1e-7 but none of R's standard errors.",
                 "standard errors by \"nid\" for every number of rows (R's default below 1001 rows is \"rank\", "
                 "intervals only)."),
        python_note="statsmodels QuantReg gives the same lines but other standard errors, so the numbers come "
                    "from R.",
        also="simplydata also says what a percentile line is and gives one block per percentile. " + SENTENCE,
    ),
    Entry(
        word="table.explain",
        option="changes_at=",
        data="culture",
        ours="""
            table = sdata.table(sdata.get_example("culture"))
            table.keep_rows_where("flask", is_equal_to="A")
            table.explain("density", using=["hour"], changes_at={"hour": 10}).keep_rows_where(
                "term", is_equal_to="after hour 10")
        """,
        code={"statsmodels": """
            import statsmodels.formula.api as smf
            df = sdata.get_example("culture").query("flask == 'A'")
            # explain("density", using=["hour"], changes_at={"hour": 10})
            df = df.assign(after=(df["hour"] >= 10) * 1.0)               # (1)
            df = df.assign(since=df["after"] * (df["hour"] - 10))
            fit = smf.ols("density ~ hour + after + since", df).fit()
            {"effect": fit.params["after"], "standard error": fit.bse["after"], "p-value": fit.pvalues["after"]}
        """},
        compare="result",
        fields=("effect", "standard error", "p-value"),
        choices=("the change starts at the point itself: rows at 10 or later count as after.",),
        also="simplydata also works for counts (outcome=\"counts\", time=) and prints the lag-1 autocorrelation "
             "of the leftovers. " + SENTENCE,
    ),
    Entry(
        word="table.add_smoothed_column",
        option='test_method="loess", interval=',
        data="culture",
        ours="""
            table = sdata.table(sdata.get_example("culture"))
            table.keep_rows_where("flask", is_equal_to="A")
            table.add_smoothed_column("smooth", from_column="density", sorted_by="hour", test_method="loess",
                                      interval=95)
        """,
        code={
            "R": """
                # add_smoothed_column("smooth", from_column="density", test_method="loess", interval=95)
                m <- stats::loess(density ~ hour, span = 0.75, degree = 2)     # (1)
                p <- stats::predict(m, se = TRUE)
                q <- stats::qt(0.975, m$one.delta^2 / m$two.delta)            # (2)
                list(fit = p$fit[1], low = p$fit[1] - q * p$se.fit[1])
            """,
            "Python": """
                {"smooth": fit, "smooth 95 % CI low": low}
            """,
        },
        r_inputs=FLASK_A,
        r_packages=(),  # base R (stats) only
        compare="result",
        fields=("smooth", "smooth 95 % CI low"),
        choices=("R loess's own defaults: span 0.75 (smoothness=), local curves of degree 2, no robustness steps.",
                 "the band uses loess's own degrees of freedom, as R's predict.loess intervals do."),
        python_note="statsmodels lowess has no standard errors and fits local straight lines with robustness steps, "
                    "so loess comes from R.",
        also="simplydata also adds the band's high end and says how loess differs from lowess.",
    ),
    Entry(
        word="draw_smooth_line",
        option='test_method="loess", with_confidence_band=',
        data="culture",
        ours="""
            culture = sdata.get_example("culture")
            chart = sdata.chart(culture[culture["flask"] == "A"]).draw_dots(x="hour", y="density")
            chart.draw_smooth_line(test_method="loess", with_confidence_band=True)
        """,
        code={
            "R": """
                # draw_smooth_line(test_method="loess", with_confidence_band=True)
                m <- stats::loess(density ~ hour, span = 0.75, degree = 2)          # (1)
                at <- seq(min(hour), max(hour), length.out = 200)
                list(at = at, fitted = unname(stats::predict(m, newdata = data.frame(hour = at))))
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.plot(at, fitted)     # the band is predict(se = TRUE) +/- t x se, shaded
            """,
        },
        r_inputs=FLASK_A,
        r_packages=(),  # base R (stats) only
        compare="chart",
        check=("lines",),
        tolerance=1e-9,
        choices=("R loess's own defaults: span 0.75, local curves of degree 2, no robustness steps (not lowess).",),
        python_note="statsmodels lowess has no confidence band, so loess comes from R.",
        also="simplydata also draws one line per colour group.",
    ),
]

ENTRIES = ENTRIES + OPTION_ENTRIES
