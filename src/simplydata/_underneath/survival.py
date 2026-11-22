"""Survival and person-time (phase S3b-3): the new words add_time_and_event_columns, find_risk_over_time and
draw_risk_curves (ENTRIES), and one entry for each new option of find_survival_over_time, compare_survival,
explain_survival and draw_survival_curves (OPTION_ENTRIES, keyed by word and option).
"""

from . import Entry

SENTENCE = "simplydata also writes the result as sentences, with the p-value in words, and names the method."
TRIAL = """
    df = sdata.get_example("trial")
    days = df["days"].to_numpy(dtype=float)
    ev = (df["died"] == "yes").to_numpy()
    treatment = df["treatment"].to_numpy(dtype=object)
    age = df["age"].to_numpy(dtype=float)
"""
NEW_MEDICINE = """
    df = sdata.get_example("trial")
    g = df[df["treatment"] == "new medicine"]
    days = g["days"].to_numpy(dtype=float)
    ev = (g["died"] == "yes").to_numpy()
"""
ADMISSIONS = """
    df = sdata.get_example("admissions")
    end = df[["first_esbl", "discharged"]].min(axis=1)
    time = (end - df["admitted"]).dt.days.to_numpy(dtype=float)
    state = (df["first_esbl"] <= df["discharged"]).map({True: "first_esbl", False: "discharged"}).to_numpy(dtype=object)
    ward = df["ward"].to_numpy(dtype=object)
"""
ADMISSIONS_TABLE = """
            table = sdata.table(sdata.get_example("admissions"))
            table.add_time_and_event_columns(from_date="admitted", event_date="first_esbl", competing_with="discharged")
"""
NOTHING_IN_PYTHON = "no Python package gives it: statsmodels has none of these, so the numbers come from R."

ENTRIES = [
    Entry(
        word="table.add_time_and_event_columns",
        data="admissions",
        ours="""
            table = sdata.table(sdata.get_example("admissions"))
            table.add_time_and_event_columns(from_date="admitted", to_date="discharged", event_date="first_esbl")
            table.keep_columns(*["time", "event"])
        """,
        code={"pandas": """
            df = sdata.get_example("admissions")
            # add_time_and_event_columns(from_date="admitted", to_date="discharged", event_date="first_esbl")
            end = df[["first_esbl", "discharged"]].min(axis=1)                    # (1)
            df["time"] = (end - df["admitted"]).dt.days
            df["event"] = (df["first_esbl"] <= df["discharged"]).astype(int)      # (2)
            df[["time", "event"]]
        """},
        compare="table",
        choices=("follow-up ends at the first of the end dates; an empty date does not end it.",
                 "the event counts when its date came first or on the same day as the others."),
        also="simplydata also counts weeks, months (30.4375 days) and years (365.25 days), leaves rows whose event "
             "came before the start empty (prevalent cases), takes until= (the end of the study) and competing "
             "dates (competing_with=), and prints the person-time.",
    ),
    Entry(
        word="table.find_risk_over_time",
        data="admissions",
        ours=ADMISSIONS_TABLE + """
            result = table.find_risk_over_time(time="time", event="event", value="first_esbl",
                                               competing_with="discharged", for_each_group_in="ward", at_time_points=[30])
            result.keep_rows_where("ward", is_equal_to="surgery").keep_rows_where("event", is_equal_to="first_esbl")
        """,
        code={
            "R": """
                # find_risk_over_time(time="time", event="event", value="first_esbl",
                #                     competing_with="discharged", for_each_group_in="ward", at_time_points=[30])
                st <- factor(state, levels = c("still followed", "first_esbl", "discharged"))  # (1)
                f <- survival::survfit(survival::Surv(time, st) ~ ward)                        # (2)
                s <- summary(f, times = 30, extend = TRUE)
                k <- match("first_esbl", f$states)
                list(risk = s$pstate[2, k], low = s$lower[2, k], high = s$upper[2, k])
            """,
            "Python": """
                {"risk": risk, "95 % CI low": low, "95 % CI high": high}
            """,
        },
        r_inputs=ADMISSIONS,
        r_packages=("survival",),
        compare="result",
        fields=("risk", "95 % CI low", "95 % CI high"),
        tolerance=1e-9,
        choices=("the first level of the factor is the censored state (followed without either event); the "
                 "competing event is a state of its own, never counted as censored.",
                 "survfit with a factor event gives the Aalen-Johansen estimate and its log-scale 95 % interval."),
        python_note="statsmodels CumIncidenceRight gives the same estimates without intervals, so the numbers come "
                    "from R.",
        also="simplydata also prints how many rows of every other value counted as still followed, and what 1 minus "
             "Kaplan-Meier would wrongly give.",
    ),
    Entry(
        word="draw_risk_curves",
        data="trial",
        ours="""
            chart = sdata.chart(sdata.get_example("trial"))
            chart.draw_risk_curves(time="days", event="died", colour="treatment")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            from statsmodels.duration.survfunc import SurvfuncRight
            df = sdata.get_example("trial")
            # draw_risk_curves(time="days", event="died", colour="treatment")
            fig, ax = plt.subplots()
            for name, g in df.groupby("treatment"):
                f = SurvfuncRight(g["days"], g["died"] == "yes")
                s = np.r_[1, f.surv_prob, f.surv_prob[-1]]
                ax.step(np.r_[0, f.surv_times, g["days"].max()], 1 - s, where="post")  # (1)
        """},
        compare="chart",
        check=("lines",),
        choices=("with nothing competing, the chance of having had the event is 1 minus the Kaplan-Meier curve, "
                 "from 0 at time 0 to the last time followed (R plot(survfit(...), fun = \"event\")).",),
        also="simplydata also draws the Aalen-Johansen curves of R survfit with competing_with=, the 95 % band with "
             "with_confidence_band=True, a legend and the axis labels.",
    ),
]


OPTION_ENTRIES = [
    Entry(
        word="table.find_survival_over_time",
        option="at_time_points=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            result = table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                   at_time_points=[365, 730])
            result.keep_rows_where("treatment", is_equal_to="new medicine").keep_rows_where("time", is_equal_to=365)
        """,
        code={"statsmodels": """
            import numpy as np
            from statsmodels.duration.survfunc import SurvfuncRight
            df = sdata.get_example("trial")
            g = df[df["treatment"] == "new medicine"]
            # find_survival_over_time(..., at_time_points=[365, 730])
            f = SurvfuncRight(g["days"], g["died"] == "yes")
            i = np.searchsorted(f.surv_times, 365, side="right") - 1      # (1)
            {"survival": f.surv_prob[i]}
        """},
        compare="result",
        fields=("survival",),
        choices=("the curve is flat between event times, so the survival at 365 is the one of the last event time "
                 "at or before 365 (R summary(survfit(), times =)).",),
        also="simplydata also gives the 95 % interval, the number still followed and the events by then, and leaves "
             "a time after a group's last follow-up empty.",
    ),
    Entry(
        word="table.find_survival_over_time",
        option='test_method="life table"',
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            result = table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                   test_method="life table", at_time_points=[0, 365, 730])
            result.keep_rows_where("treatment", is_equal_to="new medicine").keep_rows_where("interval start",
                                                                                is_equal_to=365)
        """,
        code={
            "R": """
                # find_survival_over_time(..., test_method="life table", at_time_points=[0, 365, 730])
                # days, ev: the new-medicine rows of sdata.get_example("trial")
                tis <- c(0, 365, 730, NA)                                             # (1)
                k <- findInterval(days, tis[1:3])
                t <- KMsurv::lifetab(tis, length(days), tabulate(k[!ev], 3), tabulate(k[ev], 3))  # (2)
                list(surv = t$surv[2], nrisk = t$nrisk[2], hazard = t$hazard[2])
            """,
            "Python": """
                {"survival at the start": surv, "effective at risk": nrisk, "hazard": hazard}
            """,
        },
        r_inputs=NEW_MEDICINE,
        r_packages=("KMsurv",),
        compare="result",
        fields=("survival at the start", "effective at risk", "hazard"),
        choices=("the intervals start at the times given, and the last one is open (NA).",
                 "simplydata counts the rows lost and with the event in each interval; lifetab does the rest, with "
                 "the actuarial assumption (lost rows count as followed for half the interval)."),
        python_note=NOTHING_IN_PYTHON,
        also="simplydata also checks that the first interval starts at 0 and prints the table interval by interval.",
    ),
    Entry(
        word="table.find_survival_over_time",
        option="allowing_for=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            result = table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                   allowing_for=["age"], at_time_points=[365])
            result.keep_rows_where("treatment", is_equal_to="usual care")
        """,
        code={
            "R": """
                # find_survival_over_time(..., allowing_for=["age"], at_time_points=[365])
                d <- data.frame(time = days, event = as.numeric(ev), group = factor(treatment), age = age)
                m <- survival::coxph(survival::Surv(time, event) ~ group + age, data = d, x = TRUE)
                a <- adjustedCurves::adjustedsurv(data = d, variable = "group", ev_time = "time",
                  event = "event", method = "direct", outcome_model = m, conf_int = TRUE, times = 365)  # (1)
                list(surv = a$adj$surv[2], low = a$adj$ci_lower[2])
            """,
            "Python": """
                {"survival": surv, "95 % CI low": low}
            """,
        },
        r_inputs=TRIAL,
        r_packages=("survival", "adjustedCurves", "riskRegression"),
        compare="result",
        fields=("survival", "95 % CI low"),
        tolerance=1e-8,
        choices=("direct adjustment: each row's curve is predicted as if in each group and averaged over all rows, "
                 "never the curve of an \"average\" row; conf_int = TRUE (adjustedCurves' own default is FALSE).",),
        python_note="statsmodels PHReg predicts one row's curve; averaging them would be simplydata's own method, "
                    "so the numbers come from R adjustedCurves.",
        also="simplydata also prints the adjusted medians and says what direct adjustment means.",
    ),
    Entry(
        word="table.find_survival_over_time",
        option="followed_from=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            table.add_column("joined", "days / 4 + 0.1")
            result = table.find_survival_over_time(time="days", event="died", followed_from="joined")
            result.keep_rows_by_position([21])
        """,
        code={"statsmodels": """
            from statsmodels.duration.survfunc import SurvfuncRight
            df = sdata.get_example("trial")
            # find_survival_over_time(time="days", event="died", followed_from="joined")
            f = SurvfuncRight(df["days"], df["died"] == "yes", entry=df["days"] / 4 + 0.1)  # (1)
            {"survival": f.surv_prob[20], "at risk": f.n_risk[20]}
        """},
        compare="result",
        fields=("survival", "at risk"),
        choices=("each row is at risk only after its start (left truncation, R Surv(start, stop, event)).",),
        also="simplydata also gives the 95 % interval, the median and a note when few rows are followed at the "
             "start.",
    ),
    Entry(
        word="table.find_survival_over_time",
        option="average_time_up_to=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            result = table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                   average_time_up_to=700)
            result.keep_rows_where("treatment", is_equal_to="usual care")
        """,
        code={
            "R": """
                # find_survival_over_time(..., average_time_up_to=700)
                f <- survival::survfit(survival::Surv(days, ev) ~ treatment)
                t <- summary(f, rmean = 700)$table                                  # (1)
                list(rmean = t[2, "rmean"], se = t[2, "se(rmean)"])
            """,
            "Python": """
                {"average time without the event": rmean, "standard error": se}
            """,
        },
        r_inputs=TRIAL,
        r_packages=("survival",),
        compare="result",
        fields=("average time without the event", "standard error"),
        choices=("rmean = 700, the horizon you name: without it survival's print uses its own upper limit.",),
        python_note="statsmodels gives no restricted mean, so the numbers come from R survival.",
        also="simplydata also refuses a horizon after the shortest follow-up of the groups.",
    ),
    Entry(
        word="table.compare_survival",
        option="allowing_for=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            table.add_group_column("older", from_column="age", cut_at=[71], names=["70 or under", "over 70"])
            table.compare_survival(time="days", event="died", for_each_group_in="treatment", allowing_for="older")
        """,
        code={"statsmodels": """
            from statsmodels.duration.survfunc import survdiff
            df = sdata.get_example("trial")
            # compare_survival(..., allowing_for="older")
            chi, p = survdiff(df["days"], df["died"] == "yes", df["treatment"],
                              strata=df["age"] > 70)                              # (1)
            {"statistic": chi, "p-value": p}
        """},
        compare="result",
        fields=("statistic", "p-value"),
        choices=("strata=: the groups are compared within each stratum and the results added up, as R survdiff(... "
                 "+ strata()).",),
        also="simplydata also refuses a number column in allowing_for= (one stratum per value) and prints the "
             "observed and expected events. " + SENTENCE,
    ),
    Entry(
        word="table.compare_survival",
        option="followed_from=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            table.add_column("joined", "days / 4 + 0.1")
            table.compare_survival(time="days", event="died", for_each_group_in="treatment", followed_from="joined")
        """,
        code={"statsmodels": """
            from statsmodels.duration.survfunc import survdiff
            df = sdata.get_example("trial")
            # compare_survival(..., followed_from="joined")
            chi, p = survdiff(df["days"], df["died"] == "yes", df["treatment"],
                              entry=df["days"] / 4 + 0.1)                               # (1)
            {"statistic": chi, "p-value": p}
        """},
        compare="result",
        fields=("statistic", "p-value"),
        choices=("entry=: each row counts as at risk only after its start. R survdiff takes no start times; the "
                 "same test in R is the score test of coxph(Surv(start, stop, event) ~ group, ties = \"exact\") "
                 "(coxph()$score), which agrees to about 1e-11 (validation/report.md).",),
        also=SENTENCE,
    ),
    Entry(
        word="table.compare_survival",
        option="average_time_up_to=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            table.compare_survival(time="days", event="died", for_each_group_in="treatment", average_time_up_to=700)
        """,
        code={
            "R": """
                # compare_survival(..., average_time_up_to=700)
                arm <- as.numeric(treatment == "usual care")                      # (1)
                r <- survRM2::rmst2(days, as.numeric(ev), arm, tau = 700)         # (2)
                u <- r$unadjusted.result
                list(difference = u[1, 1], low = u[1, 2], p = u[1, 4], ratio = u[2, 1])
            """,
            "Python": """
                {"difference in average time": difference, "difference 95 % CI low": low,
                 "difference p-value": p, "ratio of average times": ratio}
            """,
        },
        r_inputs=TRIAL,
        r_packages=("survRM2",),
        compare="result",
        fields=("difference in average time", "difference 95 % CI low", "difference p-value",
                "ratio of average times"),
        choices=("arm 1 is the second group in sorted order, so the difference is the second minus the first.",
                 "tau = 700, the horizon you name: survRM2's own default is the shortest of the groups' last times."),
        python_note="no Python package gives the restricted mean survival time difference, so it comes from R "
                    "survRM2.",
        also="simplydata also runs the log-rank test first and prints each group's average time. " + SENTENCE,
    ),
    Entry(
        word="table.compare_survival",
        option="competing_with=",
        data="admissions",
        ours=ADMISSIONS_TABLE + """
            table.compare_survival(time="time", event="event", value="first_esbl", competing_with="discharged",
                                   for_each_group_in="ward")
        """,
        code={
            "R": """
                # compare_survival(..., value="first_esbl", competing_with="discharged")
                s <- match(state, c("first_esbl", "discharged"))                   # (1)
                t <- cmprsk::cuminc(time, s, ward, cencode = 0)$Tests             # (2)
                list(stat = t["1", "stat"], p = t["1", "pv"])
            """,
            "Python": """
                {"statistic": stat, "p-value": p}
            """,
        },
        r_inputs=ADMISSIONS,
        r_packages=("cmprsk",),
        compare="result",
        fields=("statistic", "p-value"),
        choices=("the event asked about is code 1 and the competing event code 2; other values are censored "
                 "(code 0).",
                 "Gray's test of the chance of each event over time (cmprsk::cuminc), not a log-rank test with the "
                 "competing event censored."),
        python_note="no Python package gives Gray's test, so it comes from R cmprsk.",
        also="simplydata also prints how every other value was counted and the competing event's own test. "
             + SENTENCE,
    ),
    Entry(
        word="table.explain_survival",
        option="allowing_for=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            result = table.explain_survival(time="days", event="died", using=["age"], allowing_for="treatment")
            result
        """,
        code={"statsmodels": """
            from statsmodels.duration.hazard_regression import PHReg
            df = sdata.get_example("trial")
            # explain_survival(time="days", event="died", using=["age"], allowing_for="treatment")
            m = PHReg(df["days"], df[["age"]], status=df["died"] == "yes", ties="efron",
                      strata=df["treatment"]).fit()                                   # (1)
            {"coefficient": m.params[0], "standard error": m.bse[0]}
        """},
        compare="result",
        fields=("coefficient", "standard error"),
        tolerance=1e-7,
        choices=("strata=: each treatment group has its own baseline risk (R coxph(... + strata(treatment))), so "
                 "there is no hazard ratio for it.",),
        also="simplydata also refuses a number column in allowing_for=, adds Harrell's C and the proportional-hazards "
             "check with R. " + SENTENCE,
    ),
    Entry(
        word="table.explain_survival",
        option="followed_from=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            table.add_column("joined", "days / 4 + 0.1")
            result = table.explain_survival(time="days", event="died", using=["age"], followed_from="joined")
            result
        """,
        code={"statsmodels": """
            from statsmodels.duration.hazard_regression import PHReg
            df = sdata.get_example("trial")
            # explain_survival(time="days", event="died", using=["age"], followed_from="joined")
            m = PHReg(df["days"], df[["age"]], status=df["died"] == "yes", ties="efron",
                      entry=df["days"] / 4 + 0.1).fit()                                     # (1)
            {"coefficient": m.params[0], "standard error": m.bse[0]}
        """},
        compare="result",
        fields=("coefficient", "standard error"),
        tolerance=1e-7,
        choices=("entry=: each row is at risk only after its start (R coxph(Surv(start, stop, event) ~ ...)). "
                 "statsmodels counts a row as at risk at an event time equal to its start and R does not, so when a "
                 "row starts at an event time (one person split into rows) simplydata fits the model with R "
                 "coxph, and says so.",),
        also=SENTENCE,
    ),
    Entry(
        word="table.explain_survival",
        option="competing_with=",
        data="admissions",
        ours=ADMISSIONS_TABLE + """
            result = table.explain_survival(time="time", event="event", value="first_esbl",
                                            competing_with="discharged", using=["age"])
            result
        """,
        code={"statsmodels": """
            from statsmodels.duration.hazard_regression import PHReg
            df = sdata.get_example("admissions")
            # explain_survival(..., value="first_esbl", competing_with="discharged", using=["age"])
            end = df[["first_esbl", "discharged"]].min(axis=1)
            had = df["first_esbl"] <= df["discharged"]                                # (1)
            m = PHReg((end - df["admitted"]).dt.days, df[["age"]], status=had, ties="efron").fit()
            {"coefficient": m.params[0], "standard error": m.bse[0]}
        """},
        compare="result",
        fields=("coefficient", "standard error"),
        tolerance=1e-7,
        choices=("cause-specific: a Cox model of the event asked about, with the competing event counted as the "
                 "end of follow-up (the risk at any moment among those still free of both events).",),
        also="simplydata also prints how every other value was counted and points to test_method=\"fine-gray\" for the "
             "chance of the event by each time. " + SENTENCE,
    ),
    Entry(
        word="table.explain_survival",
        option='test_method="fine-gray"',
        data="admissions",
        ours=ADMISSIONS_TABLE + """
            result = table.explain_survival(time="time", event="event", value="first_esbl",
                                            competing_with="discharged", using=["age"], test_method="fine-gray")
            result
        """,
        code={
            "R": """
                # explain_survival(..., value="first_esbl", competing_with="discharged", using=["age"],
                #                  test_method="fine-gray")
                s <- match(state, c("first_esbl", "discharged"))
                m <- cmprsk::crr(time, s, cbind(age), failcode = 1, cencode = 0)   # (1)
                list(coef = m$coef[1], se = sqrt(m$var[1, 1]))
            """,
            "Python": """
                {"coefficient": coef, "standard error": se}
            """,
        },
        r_inputs=ADMISSIONS + """
    age = df["age"].to_numpy(dtype=float)
""",
        r_packages=("cmprsk",),
        compare="result",
        fields=("coefficient", "standard error"),
        tolerance=1e-7,
        choices=("Fine and Gray's model with crr's robust (sandwich) standard errors; failcode is the event asked "
                 "about.",),
        python_note="no Python package gives the Fine-Gray model, so it comes from R cmprsk.",
        also="simplydata also says that a subdistribution hazard ratio gives the direction of the effect on the "
             "chance of the event, not its size. " + SENTENCE,
    ),
    Entry(
        word="table.explain_survival",
        option="distribution=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            result = table.explain_survival(time="days", event="died", using=["age"], distribution="weibull")
            result
        """,
        code={
            "R": """
                # explain_survival(time="days", event="died", using=["age"], distribution="weibull")
                m <- survival::survreg(survival::Surv(days, ev) ~ age, dist = "weibull")  # (1)
                list(ratio = exp(coef(m)[2]), low = exp(confint(m)[2, 1]))
            """,
            "Python": """
                {"time ratio": ratio, "95 % CI low": low}
            """,
        },
        r_inputs=TRIAL,
        r_packages=("survival",),
        compare="result",
        fields=("time ratio", "95 % CI low"),
        tolerance=1e-7,
        choices=("the accelerated failure time model of survreg: time ratios exp(coefficient), never hazard "
                 "ratios.",),
        python_note="statsmodels has no parametric survival regression, so the numbers come from R survival.",
        also="simplydata also prints the Weibull shape (1 / survreg's scale) in words and the AIC. " + SENTENCE,
    ),
    Entry(
        word="draw_survival_curves",
        option="followed_from=",
        data="trial",
        ours="""
            table = sdata.table(sdata.get_example("trial"))
            table.add_column("joined", "days / 4 + 0.1")
            chart = table.start_chart()
            chart.draw_survival_curves(time="days", event="died", followed_from="joined", with_censor_marks=False)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            from statsmodels.duration.survfunc import SurvfuncRight
            df = sdata.get_example("trial")
            # draw_survival_curves(time="days", event="died", followed_from="joined")
            f = SurvfuncRight(df["days"], df["died"] == "yes", entry=df["days"] / 4 + 0.1)   # (1)
            fig, ax = plt.subplots()
            ax.step(np.r_[0, f.surv_times, df["days"].max()], np.r_[1, f.surv_prob, f.surv_prob[-1]], where="post")
        """},
        compare="chart",
        check=("lines",),
        choices=("entry=: each row is at risk only after its start (delayed entry).",),
        also="simplydata also draws the censor marks, the 95 % band and the number at risk counted from each row's "
             "start.",
    ),
    Entry(
        word="draw_survival_curves",
        option="allowing_for=",
        data="trial",
        ours="""
            chart = sdata.chart(sdata.get_example("trial"))
            chart.draw_survival_curves(time="days", event="died", colour="treatment", allowing_for=["age"])
        """,
        code={
            "R": """
                # draw_survival_curves(time="days", event="died", colour="treatment", allowing_for=["age"])
                d <- data.frame(time = days, event = as.numeric(ev), group = factor(treatment), age = age)
                m <- survival::coxph(survival::Surv(time, event) ~ group + age, data = d, x = TRUE)
                a <- adjustedCurves::adjustedsurv(data = d, variable = "group", ev_time = "time",
                  event = "event", method = "direct", outcome_model = m, conf_int = TRUE)  # (1)
                list(t = a$adj$time, s = a$adj$surv, g = as.integer(a$adj$group))
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                for k in (1, 2):
                    ax.step(t[g == k], s[g == k], where="post")
            """,
        },
        r_inputs=TRIAL,
        r_packages=("survival", "adjustedCurves", "riskRegression"),
        compare="chart",
        check=("lines",),
        tolerance=1e-8,
        choices=("direct adjustment: each row's curve predicted in each group, then averaged over all rows.",),
        python_note="statsmodels PHReg predicts one row's curve; averaging them would be simplydata's own method, "
                    "so the curves come from R adjustedCurves.",
        also="simplydata also draws the 95 % band with with_confidence_band=True and refuses the number-at-risk "
             "table (adjusted curves have none).",
    ),
    Entry(
        word="draw_risk_curves",
        option="competing_with=",
        data="admissions",
        ours=ADMISSIONS_TABLE + """
            chart = table.start_chart()
            chart.draw_risk_curves(time="time", event="event", value="first_esbl", competing_with="discharged")
        """,
        code={
            "R": """
                # draw_risk_curves(time="time", event="event", value="first_esbl", competing_with="discharged")
                st <- factor(state, levels = c("still followed", "first_esbl", "discharged"))  # (1)
                f <- survival::survfit(survival::Surv(time, st) ~ 1)
                s <- summary(f)
                list(t = s$time, r = s$pstate[, match("first_esbl", f$states)], end = max(time))
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                import numpy as np
                fig, ax = plt.subplots()
                ax.step(np.r_[0, t, end], np.r_[0, r, r[-1]], where="post")
            """,
        },
        r_inputs=ADMISSIONS,
        r_packages=("survival",),
        compare="chart",
        check=("lines",),
        tolerance=1e-9,
        choices=("the competing event is a state of its own (Aalen-Johansen), never counted as censored.",),
        python_note="statsmodels CumIncidenceRight gives the same estimates without intervals; simplydata draws "
                    "R's, with the band.",
        also="simplydata also draws one curve per group with colour=, the 95 % band and a legend.",
    ),
]


ENTRIES = ENTRIES + OPTION_ENTRIES
