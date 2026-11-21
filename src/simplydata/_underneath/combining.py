"""Combining studies (phase S3b-1): the new words combine_studies and draw_funnel_plot (ENTRIES), and one entry
for each option of combine_studies that changes what it calls in R metafor (keyed by word and option).
"""

from . import Entry

BCG = """
    bcg = sdata.get_example("bcg")
    e1 = bcg["tb_vaccinated"].to_numpy(dtype=float)
    n1 = bcg["vaccinated"].to_numpy(dtype=float)
    e2 = bcg["tb_unvaccinated"].to_numpy(dtype=float)
    n2 = bcg["unvaccinated"].to_numpy(dtype=float)
    latitude = bcg["latitude"].to_numpy(dtype=float)
    allocation = bcg["allocation"].to_numpy(dtype=object)
"""
SMOKING = """
    smoking = sdata.get_example("passive_smoking")
    est = smoking["odds ratio"].to_numpy(dtype=float)
    lo = smoking["odds ratio 95 % CI low"].to_numpy(dtype=float)
    hi = smoking["odds ratio 95 % CI high"].to_numpy(dtype=float)
"""
CALL = 'names="trial", events=["tb_vaccinated", "tb_unvaccinated"], out_of=["vaccinated", "unvaccinated"]'
OURS = """
    table = sdata.table(sdata.get_example("bcg"))
    result = table.combine_studies({call}{more})
    result.as_pandas().query("`row kind` == '{kind}'")
"""
COMBINED = ("estimate", "estimate 95 % CI low", "estimate 95 % CI high", "p-value")
PYTHON = """
    {"estimate": b, "estimate 95 % CI low": low, "estimate 95 % CI high": high, "p-value": p}
"""
NOTE = ("statsmodels has fixed and random effects (DerSimonian-Laird, Paule-Mandel) but no REML, no prediction "
        "interval, no Egger or trim-and-fill, no meta-regression and no Peto, so the numbers come from R metafor.")
ALSO = ("simplydata also says the combined effect, the prediction interval, tau (as a factor for ratios) and "
        "I-squared in words, gives each p-value as a count of sets of studies, and adds the notes on small-study "
        "effects from 10 studies.")


def _ours(more="", kind="combined"):
    return OURS.format(call=CALL, more=more, kind=kind)


ENTRIES = [
    Entry(
        word="table.combine_studies",
        data="bcg",
        ours=_ours(),
        code={
            "R": """
                # combine_studies(names="trial", events=[...], out_of=[...])
                e <- metafor::escalc(measure = "RR", ai = e1, n1i = n1, ci = e2,
                                     n2i = n2, drop00 = TRUE)                    # (1)
                f <- metafor::rma(yi, vi, data = e, method = "REML",          # (2)
                                  test = "adhoc")                              # (3)
                p <- predict(f, transf = exp)                                  # (4)
                list(b = p$pred, low = p$ci.lb, high = p$ci.ub, p = f$pval,
                     tau2 = f$tau2, I2 = f$I2, pi_low = p$pi.lb, pi_high = p$pi.ub)
            """,
            "Python": PYTHON,
        },
        r_inputs=BCG,
        r_packages=("metafor",),
        compare="result",
        fields=COMBINED,
        tolerance=1e-9,
        choices=("risk ratios for counts, and a study with no events in either group left out (drop00 = TRUE), as "
                 "Cochrane reviews do; show= chooses odds ratios or risk differences.",
                 "random effects with REML, metafor's default and the best of the usual estimators of the "
                 "between-study spread (Veroniki et al. 2016).",
                 "Hartung-Knapp intervals and p-values with the ad hoc rule: never narrower than the normal (z) "
                 "interval; interval_by=\"normal\" gives the classic interval.",
                 "the result shown back as a ratio, with the prediction interval (t with k - 1 degrees of freedom "
                 "under Hartung-Knapp)."),
        python_note=NOTE,
        also=ALSO,
    ),
    Entry(
        word="draw_funnel_plot",
        data="bcg",
        ours=f"""
            table = sdata.table(sdata.get_example("bcg"))
            result = table.combine_studies({CALL})
            chart = result.start_chart()
            chart.draw_funnel_plot(x="estimate", y="standard error")
        """,
        code={
            "R": """
                # draw_funnel_plot(x="estimate", y="standard error"), after combine_studies
                e <- metafor::escalc(measure = "RR", ai = e1, n1i = n1, ci = e2,
                                     n2i = n2, drop00 = TRUE)
                f <- metafor::rma(yi, vi, data = e, test = "adhoc")
                list(rr = exp(e$yi), se = sqrt(e$vi), centre = exp(f$b[1]))
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                from scipy import stats
                fig, ax = plt.subplots()
                ax.scatter(rr, se)                                         # each study
                top = float(se.max())
                low, high = stats.lognorm.interval(0.95, s=top, scale=centre)  # (1)
                ax.plot([low, centre, high], [top, 0.0, top], linestyle="--")
                ax.axvline(centre)                                       # (2)
                ax.set_ylim(top * 1.05, 0.0)
                ax.set_xscale("log")                                        # (3)
            """,
        },
        r_inputs=BCG,
        r_packages=("metafor",),
        compare="chart",
        check=("dots", "lines"),
        tolerance=1e-9,
        choices=("the pseudo 95 % limits: SciPy's 95 % interval around the combined effect at the largest standard "
                 "error (lognorm for ratios, so on the log scale); with the top of the funnel at the combined effect "
                 "both limits are straight lines, as metafor funnel() draws them.",
                 "the line is the combined effect of combine_studies (random effects, REML).",
                 "ratios on a log scale, with the standard error of the log ratio downwards (0 at the top)."),
        python_note="matplotlib draws it; the studies' effects come from combine_studies, which needs R metafor.",
        also="simplydata also prints how to read the funnel, and why missing corners are not proof of publication "
             "bias.",
        ours_r=("metafor",),
    ),
]


def _option(option, more, r_fit, python_note=NOTE, choices=(), kind="combined", fields=COMBINED, code_python=PYTHON,
            r_inputs=BCG, data="bcg", ours=None, also=ALSO, tolerance=1e-9):
    return Entry(word="table.combine_studies", option=option, data=data, ours=ours or _ours(more, kind),
                 code={"R": r_fit, "Python": code_python}, r_inputs=r_inputs, r_packages=("metafor",),
                 compare="result", fields=fields, tolerance=tolerance, choices=choices, python_note=python_note,
                 also=also)


OPTION_ENTRIES = [
    _option("estimates=", "", """
        # combine_studies(names="study", estimates="odds ratio")
        e <- metafor::conv.wald(out = est, ci.lb = lo, ci.ub = hi,
                                level = 95, transf = log)                 # (1)
        f <- metafor::rma(yi, vi, data = e, method = "REML", test = "adhoc")
        p <- predict(f, transf = exp)                                      # (2)
        list(b = p$pred, low = p$ci.lb, high = p$ci.ub, p = f$pval)
    """, choices=("a column with \"ratio\" in its name is combined on the log scale; metafor conv.wald() turns each "
                  "estimate and its 95 % interval into a log ratio and its variance (estimates_are_ratios= decides "
                  "otherwise).",
                  "the combined effect shown back as a ratio."),
        r_inputs=SMOKING, data="passive_smoking",
        ours="""
            table = sdata.table(sdata.get_example("passive_smoking"))
            result = table.combine_studies(names="study", estimates="odds ratio")
            result.as_pandas().query("`row kind` == 'combined'")
        """),
    _option("test_method=", ', test_method="DerSimonian-Laird"', """
        # combine_studies(..., test_method="DerSimonian-Laird")
        e <- metafor::escalc(measure = "RR", ai = e1, n1i = n1, ci = e2, n2i = n2)
        f <- metafor::rma(yi, vi, data = e, method = "DL",                # (1)
                          test = "adhoc")
        p <- predict(f, transf = exp)
        list(b = p$pred, low = p$ci.lb, high = p$ci.ub, p = f$pval)
    """, choices=("DerSimonian-Laird's between-study spread (metafor \"DL\"); \"Paule-Mandel\" is \"PM\" and "
                  "\"common effect\" is \"EE\" (metafor 4 renamed \"FE\").",)),
    _option('test_method="Mantel-Haenszel"', ', test_method="Mantel-Haenszel"', """
        # combine_studies(..., test_method="Mantel-Haenszel")
        f <- metafor::rma.mh(ai = e1, n1i = n1, ci = e2, n2i = n2,
                             measure = "RR")                              # (1)
        p <- predict(f, transf = exp)
        list(b = p$pred, low = p$ci.lb, high = p$ci.ub, p = f$pval)
    """, choices=("Mantel-Haenszel weights, a common-effect method: there is no between-study spread and no "
                  "prediction interval (compare_risks(allowing_for=) gives the same from raw rows).",)),
    _option('test_method="Peto"', ', test_method="Peto"', """
        # combine_studies(..., test_method="Peto")
        f <- metafor::rma.peto(ai = e1, n1i = n1, ci = e2, n2i = n2)       # (1)
        p <- predict(f, transf = exp)
        list(b = p$pred, low = p$ci.lb, high = p$ci.ub, p = f$pval)
    """, choices=("Peto's one-step odds ratio, a common-effect method for rare events; it gives odds ratios only.",)),
    _option("interval_by=", ', interval_by="normal"', """
        # combine_studies(..., interval_by="normal")
        e <- metafor::escalc(measure = "RR", ai = e1, n1i = n1, ci = e2, n2i = n2)
        f <- metafor::rma(yi, vi, data = e, method = "REML", test = "z")    # (1)
        p <- predict(f, transf = exp)
        list(b = p$pred, low = p$ci.lb, high = p$ci.ub, p = f$pval)
    """, choices=("the normal (z) interval and p-value, as in older meta-analyses; the default is Hartung-Knapp "
                  "(test = \"adhoc\").",)),
    _option("for_each_group_in=", ', for_each_group_in="allocation"', """
        # combine_studies(..., for_each_group_in="allocation")
        e <- metafor::escalc(measure = "RR", ai = e1, n1i = n1, ci = e2, n2i = n2)
        g <- c("alternate", "random", "systematic")
        f <- lapply(g, function(x) metafor::rma(yi, vi, data = e,
                    subset = allocation == x, test = "z"))                # (1)
        b <- sapply(f, function(m) m$b[1]); s <- sapply(f, function(m) m$se)
        q <- metafor::rma(b, sei = s, mods = ~ factor(g), method = "EE")  # (2)
        list(Q = q$QM, p = q$QMp)
    """, kind="subgroup difference", fields=("Q", "p-value"),
        code_python="""
        {"Q": Q, "p-value": p}
    """, choices=("each subgroup its own random-effects model, with its own between-study spread; for this test each "
                  "subgroup's estimate with its normal (z) standard error, as RevMan and R meta do (the subgroups' own "
                  "intervals stay Hartung-Knapp).",
                  "the test of the difference between the subgroup estimates (a common-effect meta-regression on "
                  "the subgroup), not metafor's rma(mods = ~ group), which assumes one spread for all.")),
    _option("using=", ', using=["latitude"]', """
        # combine_studies(..., using=["latitude"])
        e <- metafor::escalc(measure = "RR", ai = e1, n1i = n1, ci = e2, n2i = n2)
        f <- metafor::rma(yi, vi, mods = ~ latitude, data = e,            # (1)
                          method = "REML", test = "adhoc")
        list(b = f$b[2], low = f$ci.lb[2], high = f$ci.ub[2], p = f$pval[2])
    """, kind="meta-regression' and study != 'intercept",
        choices=("a meta-regression: the slope of the log risk ratio per unit of each column, with Hartung-Knapp "
                 "intervals; R-squared says how much of the between-study spread the columns account for.",)),
]

ENTRIES = ENTRIES + OPTION_ENTRIES
