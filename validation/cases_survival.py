"""The reliability study for phase S3b-3, survival and person-time: add_time_and_event_columns, find_risk_over_time,
draw_risk_curves, and the new options of find_survival_over_time (at_time_points=, method="life table",
allowing_for=, followed_from=, average_time_up_to=), compare_survival (allowing_for=, followed_from=,
average_time_up_to=, competing_with=), explain_survival (allowing_for=, followed_from=, competing_with=,
method="fine-gray", distribution=) and draw_survival_curves (followed_from=, allowing_for=).

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own
DATASETS and CASES and teaches load() the datasets read from R packages (KMsurv's and survival's udca are read
where they are published; the four survival datasets stored here are copies from R's survival package, LGPL).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# datasets read from an R package at run time: name -> (R packages, R code giving a named list of columns)
R_DATA_SURVIVAL = {
    "bfeed (KMsurv)": (("KMsurv",), "utils::data('bfeed', package = 'KMsurv', envir = environment()); d <- bfeed; list(duration = d$duration, delta = d$delta)"),
    "Channing House (KMsurv)": (("KMsurv",), "utils::data('channing', package = 'KMsurv', envir = environment()); d <- channing; d <- d[d$age > d$ageentry, ]; "
                                             "list(ageentry = d$ageentry, age = d$age, death = d$death, "
                                             "gender = ifelse(d$gender == 1, 'male', 'female'))"),
    "larynx (KMsurv)": (("KMsurv",), "utils::data('larynx', package = 'KMsurv', envir = environment()); d <- larynx; list(stage = paste('stage', d$stage), time = d$time, "
                                     "age = d$age, delta = d$delta)"),
    "udca (survival)": (("survival",), "d <- survival::udca; f <- function(x) ifelse(is.na(x), '', format(x)); "
                                       "list(entry_dt = f(d$entry.dt), last_dt = f(d$last.dt), "
                                       "death_dt = f(d$death.dt))"),
}


def _datasets(Dataset):
    survival_copy = "Copy from R's survival package (Therneau, T. M.), which is LGPL (>= 2)."
    return [
        Dataset("lung (survival)", "lung.csv",
                "228 patients with advanced lung cancer (NCCTG): days to death or the end of follow-up, age, sex and "
                "ECOG performance score",
                "Loprinzi, C. L. et al. (1994). Prospective evaluation of prognostic variables from patient-completed "
                "questionnaires. Journal of Clinical Oncology 12, 601-607. " + survival_copy,
                "Published trial data in an LGPL package; stored with its numbers unchanged (status recoded to "
                "died yes/no, sex to male/female).",
                "https://cran.r-project.org/package=survival"),
        Dataset("veteran (survival)", "veteran.csv",
                "137 men in the Veterans' Administration lung cancer trial: standard or test chemotherapy, cell type, "
                "Karnofsky score, days to death",
                "Kalbfleisch, J. D. & Prentice, R. L. (2002). The Statistical Analysis of Failure Time Data, 2nd ed. "
                "Wiley. " + survival_copy,
                "Published trial data in an LGPL package; stored (treatment 1/2 written as standard/test).",
                "https://cran.r-project.org/package=survival"),
        Dataset("Stanford heart transplant (survival)", "heart.csv",
                "103 patients waiting for a heart transplant, as start-stop rows (one row before and one after a "
                "transplant): age, earlier surgery, transplant",
                "Crowley, J. & Hu, M. (1977). Covariance analysis of heart transplant survival data. Journal of the "
                "American Statistical Association 72, 27-36; analysed in Therneau, T. M. & Grambsch, P. M. (2000). "
                "Modeling Survival Data. Springer, section 3.7. " + survival_copy,
                "Published data in an LGPL package; stored with its numbers unchanged.",
                "https://cran.r-project.org/package=survival"),
        Dataset("mgus2 (survival)", "mgus2.csv",
                "1384 patients with monoclonal gammopathy: months to progression to a plasma cell malignancy (pcm) "
                "or death without it",
                "Kyle, R. A. et al. (2002). A long-term study of prognosis in monoclonal gammopathy of undetermined "
                "significance. New England Journal of Medicine 346, 564-569; the competing-risks example of "
                "Therneau, T. M., \"Multi-state models and competing risks\" (survival vignette). " + survival_copy,
                "Published data in an LGPL package; stored with the first event of each patient (outcome pcm, death "
                "or censored, as the vignette builds it).",
                "https://cran.r-project.org/package=survival"),
        Dataset("bfeed (KMsurv)", "",
                "927 first-born children of the National Longitudinal Survey of Youth: weeks of breast feeding and "
                "whether it was ended",
                "Klein, J. P. & Moeschberger, M. L. (2003). Survival Analysis: Techniques for Censored and Truncated "
                "Data, 2nd ed. Springer, section 1.14 and the life table of section 5.4. Shipped with the R package "
                "KMsurv.",
                "GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R.",
                "https://cran.r-project.org/package=KMsurv"),
        Dataset("Channing House (KMsurv)", "",
                "residents of Channing House, a retirement centre in Palo Alto: age (months) on entry and at death "
                "or the end of the study (the 4 rows that left on the day they came are left out)",
                "Hyde, J. (1980). Testing survival with incomplete observations. In Biostatistics Casebook, Wiley; "
                "Klein & Moeschberger (2003), section 4.6 (delayed entry). Shipped with the R package KMsurv.",
                "GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R.",
                "https://cran.r-project.org/package=KMsurv"),
        Dataset("larynx (KMsurv)", "",
                "90 men with cancer of the larynx: stage, age, months to death",
                "Kardaun, O. (1983). Statistical survival analysis of male larynx-cancer patients: a case study. "
                "Statistica Neerlandica 37, 103-125; Klein & Moeschberger (2003), chapter 12 (parametric models). "
                "Shipped with the R package KMsurv.",
                "GPL-3 (KMsurv). Not stored here: read from KMsurv, so it needs R.",
                "https://cran.r-project.org/package=KMsurv"),
        Dataset("udca (survival)", "",
                "170 patients with primary biliary cirrhosis in a trial of ursodeoxycholic acid: dates of entry, last "
                "follow-up and death",
                "Lindor, K. D. et al. (1994). Ursodeoxycholic acid in the treatment of primary biliary cirrhosis. "
                "Gastroenterology 106, 1284-1290. Shipped with R's survival package (udca).",
                "LGPL (>= 2) (survival). Not stored here: read from survival, so it needs R.",
                "https://cran.r-project.org/package=survival"),
    ]


def _cases(Case):
    lung_km = """
        s <- summary(survival::survfit(survival::Surv(time, died == "yes") ~ sex), times = c(180, 365))
        list(`female at 180` = s$surv[1], `female at 365` = s$surv[2], `male at 365` = s$surv[4],
             `male at 365, low` = s$lower[4])
    """
    mgus_states = 'st <- factor(outcome, levels = c("censored", "pcm", "death")); '
    return [
        # ---- S06 person-time
        Case("table.add_time_and_event_columns", "person-years and deaths in the UDCA trial, from its dates",
             "udca (survival)", "real data",
             ours="""
                 t = sdata.table(data)
                 for c in ("entry_dt", "last_dt", "death_dt"):
                     t.turn_into_dates(c)
                 t.add_time_and_event_columns(from_date="entry_dt", to_date="last_dt", event_date="death_dt",
                                              unit="years")
                 r = t.as_pandas()
                 {"person-years": r["time"].sum(), "deaths": r["event"].sum(), "rows": r["time"].notna().sum()}
             """,
             r="""
                 s <- as.Date(entry_dt); l <- as.Date(last_dt); d <- as.Date(ifelse(death_dt == "", NA, death_dt))
                 end <- pmin(d, l, na.rm = TRUE)
                 list(`person-years` = sum(as.numeric(difftime(end, s, units = "days"))) / 365.25,
                      deaths = sum(!is.na(d) & d <= l), rows = length(s))
             """, r_packages=(), r_tolerance=1e-12,
             note="Base R date arithmetic (difftime) with a year of 365.25 days, as R Epi cal.yr() and Stata stset "
                  "scale(365.25). A death after the last follow-up date counts as no event."),
        # ---- P14 competing risks
        Case("table.find_risk_over_time", "the chance of a plasma cell malignancy by 10 years, death competing "
                                          "(women)", "mgus2 (survival)", "real data", ours_r=("survival",),
             ours="""
                 r = sdata.table(data).find_risk_over_time(time="etime", event="outcome", value="pcm",
                                                           competing_with="death", for_each_group_in="sex",
                                                           at_time_points=[120]).as_pandas()
                 r = r[(r["sex"] == "F") & (r["event"] == "pcm")].iloc[0]
                 {"risk by 120 months": r["risk"], "low": r["95 % CI low"]}
             """,
             parent="""
                 import numpy as np
                 from statsmodels.duration.survfunc import CumIncidenceRight
                 f = data[data["sex"] == "F"]
                 c = CumIncidenceRight(f["etime"], f["outcome"].map({"censored": 0, "pcm": 1, "death": 2}))
                 {"risk by 120 months": c.cinc[0][np.searchsorted(c.times, 120, side="right") - 1]}
             """, parent_label="statsmodels CumIncidenceRight", parent_tolerance=1e-9,
             r=mgus_states + """
                 s <- summary(survival::survfit(survival::Surv(etime, st) ~ sex), times = 120)
                 list(`risk by 120 months` = s$pstate[1, 2], low = s$lower[1, 2])
             """, r_packages=("survival",), r_tolerance=1e-9),
        Case("draw_risk_curves", "the chance of death over time in the NCCTG lung cancer trial (women): 1 minus "
                                 "Kaplan-Meier", "lung (survival)", "real data",
             ours="""
                 from simplydata._underneath.check import chart_facts
                 ax = sdata.chart(data).draw_risk_curves(time="time", event="died", colour="sex")._render().axes[0]
                 x, y = chart_facts(ax)["lines"][0]
                 {"risk at the 11th step": y[11], "risk at the end": y[-1]}
             """,
             r="""
                 s <- survival::survfit(survival::Surv(time, died == "yes") ~ 1, subset = sex == "female")
                 e <- s$surv[s$n.event > 0]
                 list(`risk at the 11th step` = 1 - e[11], `risk at the end` = 1 - tail(s$surv, 1))
             """, r_packages=("survival",), r_tolerance=1e-12),
        Case("draw_risk_curves", "competing_with=: the drawn risk of a plasma cell malignancy is R's "
                                 "Aalen-Johansen estimate", "mgus2 (survival)", "real data",
             option="competing_with=", ours_r=("survival",),
             ours="""
                 from simplydata._underneath.check import chart_facts
                 ax = sdata.chart(data).draw_risk_curves(time="etime", event="outcome", value="pcm",
                                                         competing_with="death")._render().axes[0]
                 x, y = chart_facts(ax)["lines"][0]
                 {"risk at the 51st time": y[51], "time of the 51st step": x[51]}
             """,
             r=mgus_states + """
                 f <- survival::survfit(survival::Surv(etime, st) ~ 1); s <- summary(f)
                 list(`risk at the 51st time` = s$pstate[51, 2], `time of the 51st step` = s$time[51])
             """, r_packages=("survival",), r_tolerance=1e-9),
        # ---- P06
        Case("table.find_survival_over_time", "at_time_points=: survival at 180 and 365 days in the NCCTG lung "
                                              "cancer trial", "lung (survival)", "real data", option="at_time_points=",
             ours="""
                 r = sdata.table(data).find_survival_over_time(time="time", event="died", for_each_group_in="sex",
                                                               at_time_points=[180, 365]).as_pandas()
                 v = {(g, t): (s, lo) for g, t, s, lo in zip(r["sex"], r["time"], r["survival"], r["95 % CI low"])}
                 {"female at 180": v[("female", 180)][0], "female at 365": v[("female", 365)][0],
                  "male at 365": v[("male", 365)][0], "male at 365, low": v[("male", 365)][1]}
             """,
             parent="""
                 import numpy as np
                 from statsmodels.duration.survfunc import SurvfuncRight
                 out = {}
                 for sex, t in (("female", 180), ("female", 365), ("male", 365)):
                     g = data[data["sex"] == sex]
                     f = SurvfuncRight(g["time"], g["died"] == "yes")
                     out[f"{sex} at {t}"] = f.surv_prob[np.searchsorted(f.surv_times, t, side="right") - 1]
                 out
             """, parent_label="statsmodels SurvfuncRight", parent_tolerance=1e-12,
             r=lung_km, r_packages=("survival",), r_tolerance=1e-9),
        Case("table.find_survival_over_time", 'method="life table": the actuarial life table of breast feeding '
                                              "(Klein & Moeschberger section 5.4)", "bfeed (KMsurv)", "real data",
             option='method="life table"', ours_r=("KMsurv",),
             ours="""
                 r = sdata.table(data).find_survival_over_time(time="duration", event="delta", method="life table",
                     at_time_points=[0, 2, 3, 5, 7, 11, 17, 25, 37, 53]).as_pandas()
                 r = r[r["interval start"] == 7].iloc[0]
                 {"survival at 7 weeks": r["survival at the start"], "effective at risk": r["effective at risk"],
                  "hazard": r["hazard"]}
             """,
             r="""
                 tis <- c(0, 2, 3, 5, 7, 11, 17, 25, 37, 53, NA)
                 k <- findInterval(duration, tis[1:10])
                 t <- KMsurv::lifetab(tis, length(duration), tabulate(k[delta == 0], 10), tabulate(k[delta == 1], 10))
                 list(`survival at 7 weeks` = t$surv[5], `effective at risk` = t$nrisk[5], hazard = t$hazard[5])
             """, r_packages=("KMsurv",), r_tolerance=1e-12,
             note="The intervals of the K&M example; lifetab gets the counts simplydata makes from the rows."),
        Case("table.find_survival_over_time", "allowing_for=: survival at one year by sex, adjusted for age and "
                                              "ECOG score (direct adjustment)", "lung (survival)", "real data",
             option="allowing_for=", ours_r=("survival", "adjustedCurves", "riskRegression"),
             ours="""
                 r = sdata.table(data).find_survival_over_time(time="time", event="died", for_each_group_in="sex",
                     allowing_for=["age", "ph.ecog"], at_time_points=[365]).as_pandas().set_index("sex")
                 {"female": r.loc["female", "survival"], "male": r.loc["male", "survival"]}
             """,
             r="""
                 d <- na.omit(data.frame(time = time, event = as.numeric(died == "yes"), group = factor(sex),
                                         age = age, ecog = ph.ecog))
                 m <- survival::coxph(survival::Surv(time, event) ~ group + age + ecog, data = d, x = TRUE)
                 a <- adjustedCurves::adjustedsurv(data = d, variable = "group", ev_time = "time", event = "event",
                                                   method = "direct", outcome_model = m, conf_int = TRUE, times = 365)
                 list(female = a$adj$surv[1], male = a$adj$surv[2])
             """, r_packages=("survival", "adjustedCurves", "riskRegression"), r_tolerance=1e-9,
             note="adjustedCurves' own default is conf_int = FALSE; simplydata asks for the intervals."),
        Case("table.find_survival_over_time", "followed_from=: survival to age 80 of Channing House residents who "
                                              "entered at different ages (delayed entry)", "Channing House (KMsurv)",
             "real data", option="followed_from=",
             ours="""
                 r = sdata.table(data).find_survival_over_time(time="age", event="death", followed_from="ageentry",
                                                               at_time_points=[960]).as_pandas().iloc[0]
                 {"survival at 960 months": r["survival"], "at risk": r["at risk"]}
             """,
             parent="""
                 import numpy as np
                 from statsmodels.duration.survfunc import SurvfuncRight
                 f = SurvfuncRight(data["age"], data["death"], entry=data["ageentry"])
                 {"survival at 960 months": f.surv_prob[np.searchsorted(f.surv_times, 960, side="right") - 1]}
             """, parent_label="statsmodels SurvfuncRight(entry=)", parent_tolerance=1e-12,
             r="""
                 s <- summary(survival::survfit(survival::Surv(ageentry, age, death) ~ 1), times = 960)
                 list(`survival at 960 months` = s$surv, `at risk` = s$n.risk)
             """, r_packages=("survival",), r_tolerance=1e-9),
        Case("table.find_survival_over_time", "average_time_up_to=: the average days alive in the first year, by "
                                              "sex", "lung (survival)", "real data",
             option="average_time_up_to=", ours_r=("survival",),
             ours="""
                 r = sdata.table(data).find_survival_over_time(time="time", event="died", for_each_group_in="sex",
                                                               average_time_up_to=365).as_pandas().set_index("sex")
                 {"male": r.loc["male", "average time without the event"],
                  "male standard error": r.loc["male", "standard error"]}
             """,
             r="""
                 t <- summary(survival::survfit(survival::Surv(time, died == "yes") ~ sex), rmean = 365)$table
                 list(male = t[2, "rmean"], `male standard error` = t[2, "se(rmean)"])
             """, r_packages=("survival",), r_tolerance=1e-9,
             note="survRM2::rmst2 gives the same per-group values (241.495, se 10.358 for men)."),
        # ---- P09, P10, P12, P14 on compare_survival
        Case("table.compare_survival", "allowing_for=: chemotherapy compared within each cell type (stratified "
                                       "log-rank)", "veteran (survival)", "real data", option="allowing_for=",
             ours="""
                 r = sdata.table(data).compare_survival(time="time", event="status", for_each_group_in="trt",
                                                        allowing_for="celltype").as_pandas().iloc[0]
                 {"chi-square": r["statistic"], "p": r["p-value"]}
             """,
             parent="""
                 from statsmodels.duration.survfunc import survdiff
                 chi, p = survdiff(data["time"], data["status"], data["trt"], strata=data["celltype"])
                 {"chi-square": chi, "p": p}
             """, parent_label="statsmodels survdiff(strata=)", parent_tolerance=1e-12,
             r="""
                 s <- survival::survdiff(survival::Surv(time, status) ~ trt + survival::strata(celltype))
                 list(`chi-square` = s$chisq, p = stats::pchisq(s$chisq, 1, lower.tail = FALSE))
             """, r_packages=("survival",), r_tolerance=1e-9),
        Case("table.compare_survival", "followed_from=: women and men of Channing House, followed from their age "
                                       "on entry", "Channing House (KMsurv)", "real data", option="followed_from=",
             ours="""
                 r = sdata.table(data).compare_survival(time="age", event="death", for_each_group_in="gender",
                                                        followed_from="ageentry").as_pandas().iloc[0]
                 {"chi-square": r["statistic"]}
             """,
             parent="""
                 from statsmodels.duration.survfunc import survdiff
                 chi, p = survdiff(data["age"], data["death"], data["gender"], entry=data["ageentry"])
                 {"chi-square": chi}
             """, parent_label="statsmodels survdiff(entry=)", parent_tolerance=1e-12,
             r="""
                 m <- survival::coxph(survival::Surv(ageentry, age, death) ~ gender, ties = "exact")
                 list(`chi-square` = unname(m$score))
             """, r_packages=("survival",), r_tolerance=1e-9,
             note="R survdiff takes no start times. The log-rank test with delayed entry is the score test of a Cox "
                  "model with exact ties, coxph(..., ties = \"exact\") (3.376460710701 against statsmodels' "
                  "3.376460710646); with Breslow ties the score test differs by 0.7 % (3.354), so the exact one is "
                  "the check, to 1e-9. summary() of an exact-ties fit has no score test, so it is read from "
                  "coxph()$score."),
        Case("table.compare_survival", "average_time_up_to=: the difference in average days alive in the first "
                                       "year, men minus women", "lung (survival)", "real data",
             option="average_time_up_to=", ours_r=("survRM2",),
             ours="""
                 r = sdata.table(data).compare_survival(time="time", event="died", for_each_group_in="sex",
                                                        average_time_up_to=365).as_pandas().iloc[0]
                 {"difference": r["difference in average time"], "low": r["difference 95 % CI low"],
                  "p": r["difference p-value"]}
             """,
             r="""
                 r <- survRM2::rmst2(time, as.numeric(died == "yes"), as.numeric(sex == "male"), tau = 365)
                 u <- r$unadjusted.result
                 list(difference = u[1, 1], low = u[1, 2], p = u[1, 4])
             """, r_packages=("survRM2",), r_tolerance=1e-9),
        Case("table.compare_survival", "competing_with=: Gray's test of a plasma cell malignancy between women "
                                       "and men, death competing", "mgus2 (survival)", "real data",
             option="competing_with=", ours_r=("cmprsk",),
             ours="""
                 r = sdata.table(data).compare_survival(time="etime", event="outcome", value="pcm",
                     competing_with="death", for_each_group_in="sex").as_pandas().iloc[0]
                 {"chi-square": r["statistic"], "p": r["p-value"]}
             """,
             r="""
                 s <- match(outcome, c("pcm", "death")); s[is.na(s)] <- 0
                 t <- cmprsk::cuminc(etime, s, sex, cencode = 0)$Tests
                 list(`chi-square` = t["1", "stat"], p = t["1", "pv"])
             """, r_packages=("cmprsk",), r_tolerance=1e-9),
        # ---- P09, P10, P13, P14, P15 on explain_survival
        Case("table.explain_survival", "allowing_for=: chemotherapy and Karnofsky score, each cell type with its "
                                       "own baseline (stratified Cox)", "veteran (survival)", "real data",
             option="allowing_for=",
             ours="""
                 r = sdata.table(data).explain_survival(time="time", event="status", using=["trt", "karno"],
                                                        allowing_for="celltype").as_pandas().set_index("term")
                 {"test vs standard": r.loc["trt: test vs standard", "coefficient"], "karno": r.loc["karno", "coefficient"]}
             """,
             parent="""
                 from statsmodels.duration.hazard_regression import PHReg
                 x = data[["karno"]].assign(test=(data["trt"] == "test").astype(float))
                 m = PHReg(data["time"], x[["test", "karno"]], status=data["status"], ties="efron",
                           strata=data["celltype"]).fit()
                 {"test vs standard": m.params[0], "karno": m.params[1]}
             """, parent_label="statsmodels PHReg(strata=)", parent_tolerance=1e-6,
             r="""
                 m <- survival::coxph(survival::Surv(time, status) ~ trt + karno + survival::strata(celltype))
                 list(`test vs standard` = stats::coef(m)[1], karno = stats::coef(m)[2])
             """, r_packages=("survival",), r_tolerance=1e-6),
        Case("table.explain_survival", "followed_from=: the Stanford heart transplant, start-stop rows split at "
                                       "the transplant", "Stanford heart transplant (survival)", "real data",
             option="followed_from=", ours_r=("survival",),
             ours="""
                 r = sdata.table(data).explain_survival(time="stop", event="event", using=["age", "surgery", "transplant"],
                                                        followed_from="start").as_pandas().set_index("term")
                 {"age": r.loc["age", "coefficient"], "surgery": r.loc["surgery", "coefficient"],
                  "transplant": r.loc["transplant", "coefficient"]}
             """,
             r="""
                 m <- survival::coxph(survival::Surv(start, stop, event) ~ age + surgery + transplant)
                 list(age = stats::coef(m)[1], surgery = stats::coef(m)[2], transplant = stats::coef(m)[3])
             """, r_packages=("survival",), r_tolerance=1e-6,
             note="36 rows start at a death time (each patient's second row starts at the transplant). R does not "
                  "count such a row as at risk at that death, statsmodels PHReg(entry=) does (the patient would "
                  "count twice), so simplydata fits these data with R coxph and says so."),
        Case("table.explain_survival", "competing_with=: cause-specific hazard ratios of a plasma cell "
                                       "malignancy, death counted as the end of follow-up", "mgus2 (survival)",
             "real data", option="competing_with=",
             ours="""
                 r = sdata.table(data).explain_survival(time="etime", event="outcome", value="pcm",
                     competing_with="death", using=["age", "sex"]).as_pandas().set_index("term")
                 {"age": r.loc["age", "coefficient"], "men vs women": r.loc["sex: M vs F", "coefficient"]}
             """,
             parent="""
                 from statsmodels.duration.hazard_regression import PHReg
                 x = data[["age"]].assign(m=(data["sex"] == "M").astype(float))
                 m = PHReg(data["etime"], x, status=data["outcome"] == "pcm", ties="efron").fit()
                 {"age": m.params[0], "men vs women": m.params[1]}
             """, parent_label="statsmodels PHReg", parent_tolerance=1e-6,
             r="""
                 m <- survival::coxph(survival::Surv(etime, outcome == "pcm") ~ age + sex)
                 list(age = stats::coef(m)[1], `men vs women` = stats::coef(m)[2])
             """, r_packages=("survival",), r_tolerance=1e-6),
        Case("table.explain_survival", 'method="fine-gray": subdistribution hazard ratios of a plasma cell '
                                       "malignancy, death competing", "mgus2 (survival)", "real data",
             option='method="fine-gray"', ours_r=("cmprsk",),
             ours="""
                 r = sdata.table(data).explain_survival(time="etime", event="outcome", value="pcm",
                     competing_with="death", using=["age", "sex"], method="fine-gray").as_pandas().set_index("term")
                 {"age": r.loc["age", "coefficient"], "men vs women": r.loc["sex: M vs F", "coefficient"]}
             """,
             r="""
                 s <- match(outcome, c("pcm", "death")); s[is.na(s)] <- 0
                 m <- cmprsk::crr(etime, s, cbind(age, as.numeric(sex == "M")), failcode = 1, cencode = 0)
                 list(age = m$coef[1], `men vs women` = m$coef[2])
             """, r_packages=("cmprsk",), r_tolerance=1e-7,
             note="survival::finegray() with a weighted coxph agrees to about 3 digits (-0.0173, -0.2598), the "
                  "check recorded in tests/test_s3b3_survival.py."),
        Case("table.explain_survival", "distribution=: a Weibull model of larynx cancer by stage and age (time "
                                       "ratios)", "larynx (KMsurv)", "real data", option="distribution=",
             ours_r=("survival",),
             ours="""
                 r = sdata.table(data).explain_survival(time="time", event="delta", using=["stage", "age"],
                                                        distribution="weibull").as_pandas().set_index("term")
                 {"stage 4": r.loc["stage: stage 4 vs stage 1", "coefficient"], "age": r.loc["age", "coefficient"]}
             """,
             r="""
                 m <- survival::survreg(survival::Surv(time, delta) ~ factor(stage) + age, dist = "weibull")
                 list(`stage 4` = stats::coef(m)[4], age = stats::coef(m)[5])
             """, r_packages=("survival",), r_tolerance=1e-6),
        # ---- the curve words
        Case("draw_survival_curves", "followed_from=: the drawn curve of Channing House is the delayed-entry "
                                     "Kaplan-Meier curve", "Channing House (KMsurv)", "real data",
             option="followed_from=",
             ours="""
                 from simplydata._underneath.check import chart_facts
                 ax = sdata.chart(data).draw_survival_curves(time="age", event="death", followed_from="ageentry",
                                                             with_censor_marks=False)._render().axes[0]
                 x, y = chart_facts(ax)["lines"][0]
                 {"survival at the 41st death time": y[41]}
             """,
             r="""
                 s <- survival::survfit(survival::Surv(ageentry, age, death) ~ 1)
                 list(`survival at the 41st death time` = s$surv[s$n.event > 0][41])
             """, r_packages=("survival",), r_tolerance=1e-9),
        Case("draw_survival_curves", "allowing_for=: the drawn curves by sex are adjusted for age and ECOG "
                                     "score", "lung (survival)", "real data", option="allowing_for=",
             ours_r=("survival", "adjustedCurves", "riskRegression"),
             ours="""
                 from simplydata._underneath.check import chart_facts
                 ax = sdata.chart(data).draw_survival_curves(time="time", event="died", colour="sex",
                                                             allowing_for=["age", "ph.ecog"])._render().axes[0]
                 x, y = chart_facts(ax)["lines"][0]
                 {"female, 21st point": y[20]}
             """,
             r="""
                 d <- na.omit(data.frame(time = time, event = as.numeric(died == "yes"), group = factor(sex),
                                         age = age, ecog = ph.ecog))
                 m <- survival::coxph(survival::Surv(time, event) ~ group + age + ecog, data = d, x = TRUE)
                 a <- adjustedCurves::adjustedsurv(data = d, variable = "group", ev_time = "time", event = "event",
                                                   method = "direct", outcome_model = m, conf_int = TRUE)
                 list(`female, 21st point` = a$adj$surv[a$adj$group == "female"][21])
             """, r_packages=("survival", "adjustedCurves", "riskRegression"), r_tolerance=1e-9),
    ]


def add_to(namespace) -> None:
    """Add the S3b-3 datasets and cases to cases.py, and teach its load() the datasets read from R."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    namespace["CASES"].extend(_cases(Case))
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_SURVIVAL.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_SURVIVAL:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_SURVIVAL[name]
            need_r(packages, f"the {name} data")  # checked, not attached: the code names its package
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: (np.asarray(v, dtype=float) if np.asarray(v).dtype.kind in "iuf" else list(v))
                                 for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
