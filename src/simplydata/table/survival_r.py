"""The R calls behind the survival words of phase S3b-3 (survival and person-time).

Each function hands numbers that a word has already checked to an R package and gives back R's own
numbers. Nothing is calculated here: the functions write the R call, pass the values and read the result.
The packages are checked with need_r() but never attached (every call names its package, survival::survfit),
so no package can hide a function of another.

* risk_curves: survival::survfit() with a factor event (Aalen-Johansen), for find_risk_over_time and
  draw_risk_curves with competing_with=.
* grays_test: cmprsk::cuminc()$Tests, for compare_survival(value=, competing_with=).
* fine_gray: cmprsk::crr(), for explain_survival(test_method="fine-gray").
* survival_regression: survival::survreg(dist=), for explain_survival(distribution=).
* restricted_means: summary(survival::survfit(), rmean=), and rmst_difference: survRM2::rmst2(), for
  average_time_up_to=.
* life_table: KMsurv::lifetab(), for find_survival_over_time(test_method="life table").
* adjusted_curves: adjustedCurves::adjustedsurv(method = "direct"), for allowing_for= on
  find_survival_over_time and draw_survival_curves.
(The proportional-hazards check and Harrell's C of explain_survival are in survival.py, cox_zph.)
"""

from __future__ import annotations

import numpy as np

SURVIVAL = ("survival",)


def _call(code, packages, what, python_note=None, **values):
    """r_call with the packages checked (need_r) but not attached: every call here names its package."""
    from .._r import need_r, r_call

    need_r(packages, what, python_note)
    return r_call(code, what=what, python_note=python_note, **values)


def _codes(groups):
    """Group labels as text for R, in simplydata's order (factor levels kept as given)."""
    return np.array([str(g) for g in groups], dtype=object)


# ---------------------------------------------------------------- find_risk_over_time, draw_risk_curves
def risk_curves(time, state, kinds, groups=None, levels=None, at=None):
    """The chance of each kind of event by each time, R survival::survfit(Surv(time, factor(state))) ~ g)
    (Aalen-Johansen, log-scale 95 % intervals as R's default). state: 0 = followed without an event
    (censored), 1, 2, ... = the kinds of event, in the order of kinds. at: the times to read (summary(times=,
    extend = TRUE)); None reads every event time."""
    values = {"time": np.asarray(time, dtype=float), "state": np.asarray(state, dtype=float)}
    labels = ", ".join(f"'k{i}'" for i in range(1, len(kinds) + 1))
    code = (f"st <- factor(state, levels = 0:{len(kinds)}, labels = c('censored', {labels})); ")
    if groups is not None:
        values["g"], values["g_levels"] = _codes(groups), np.array([str(v) for v in levels], dtype=object)
        code += "g <- factor(g, levels = g_levels); f <- survival::survfit(survival::Surv(time, st) ~ g); "
    else:
        code += "f <- survival::survfit(survival::Surv(time, st) ~ 1); "
    if at is not None:
        values["at"] = np.asarray(at, dtype=float)
        code += "s <- summary(f, times = at, extend = TRUE); "
    else:
        code += "s <- summary(f); "
    # the columns by their place in f$states (summary() does not always name them)
    code += ("k <- match(paste0('k', 1:" + str(len(kinds)) + "), f$states); s0 <- match('(s0)', f$states); "
             "list(time = s$time, at_risk = unname(s$n.risk[, s0]), "
             "events = unname(s$n.event[, k, drop = FALSE]), risk = unname(s$pstate[, k, drop = FALSE]), "
             "low = unname(s$lower[, k, drop = FALSE]), high = unname(s$upper[, k, drop = FALSE]), "
             "strata = if (is.null(s$strata)) character(0) else sub('^g=', '', as.character(s$strata)))")
    out = _call(code, SURVIVAL, "The chance of each kind of event over time (R survival::survfit, Aalen-Johansen)",
                python_note="statsmodels CumIncidenceRight gives the same estimates, without intervals", **values)
    n = len(np.atleast_1d(out["time"]))
    shaped = {k: np.asarray(out[k], dtype=float).reshape(n, len(kinds), order="F") if n else np.zeros((0, len(kinds)))
              for k in ("events", "risk", "low", "high")}
    return dict(time=np.atleast_1d(np.asarray(out["time"], dtype=float)),
                at_risk=np.atleast_1d(np.asarray(out["at_risk"], dtype=float)),
                strata=[str(s) for s in np.atleast_1d(out["strata"])] if out["strata"] is not None else [], **shaped)


def grays_test(time, state, groups, levels, strata=None):
    """Gray's test of the chance of each kind of event between groups: R cmprsk::cuminc(ftime, fstatus, group,
    strata, cencode = 0)$Tests. Gives {kind code: (statistic, p, df)}."""
    values = {"time": np.asarray(time, dtype=float), "state": np.asarray(state, dtype=float),
              "g": _codes(groups), "g_levels": np.array([str(v) for v in levels], dtype=object)}
    code = "g <- factor(g, levels = g_levels); "
    if strata is not None:
        values["s"] = _codes(strata)
        code += "t <- cmprsk::cuminc(time, state, g, strata = s, cencode = 0)$Tests; "
    else:
        code += "t <- cmprsk::cuminc(time, state, g, cencode = 0)$Tests; "
    code += "list(kind = rownames(t), stat = unname(t[, 'stat']), p = unname(t[, 'pv']), df = unname(t[, 'df']))"
    out = _call(code, ("cmprsk",), "Gray's test (R cmprsk::cuminc)",
                python_note="no Python package gives Gray's test", **values)
    kinds = [int(float(k)) for k in np.atleast_1d(out["kind"])]
    return {k: (float(s), float(p), int(round(float(d)))) for k, s, p, d in
            zip(kinds, np.atleast_1d(out["stat"]), np.atleast_1d(out["p"]), np.atleast_1d(out["df"]))}


# ---------------------------------------------------------------- explain_survival
def fine_gray(time, state, x):
    """The Fine-Gray model of the chance of the event of state 1 (others are competing), R cmprsk::crr(ftime,
    fstatus, cov1, failcode = 1, cencode = 0), with crr's sandwich standard errors and 95 % intervals."""
    x = np.asarray(x, dtype=float)
    values = {"time": np.asarray(time, dtype=float), "state": np.asarray(state, dtype=float), "x": x}
    code = ("x <- matrix(x, ncol = " + str(x.shape[1]) + "); "
            "m <- cmprsk::crr(time, state, x, failcode = 1, cencode = 0); s <- summary(m, digits = 15); "
            "list(beta = unname(s$coef[, 1]), se = unname(s$coef[, 3]), z = unname(s$coef[, 4]), "
            "p = unname(s$coef[, 5]), ratio = unname(s$conf.int[, 1]), low = unname(s$conf.int[, 3]), "
            "high = unname(s$conf.int[, 4]), converged = isTRUE(m$converged), n = m$n)")
    out = _call(code, ("cmprsk",), "The Fine-Gray model (R cmprsk::crr)",
                python_note="no Python package gives the Fine-Gray model", **values)
    return {k: (np.atleast_1d(np.asarray(v, dtype=float)) if k not in ("converged",) else bool(np.atleast_1d(v)[0]))
            for k, v in out.items()}


R_DISTRIBUTIONS = {"weibull": "weibull", "exponential": "exponential", "lognormal": "lognormal",
                   "log-logistic": "loglogistic"}


def survival_regression(time, event, x, distribution):
    """A parametric (accelerated failure time) model, R survival::survreg(Surv(time, event) ~ x, dist =). The
    time ratios and their Wald 95 % intervals are R's exp(coef) and exp(confint); for Weibull also the shape,
    1 / survreg's scale (survreg's help: shape = 1 / scale)."""
    x = np.asarray(x, dtype=float)
    values = {"time": np.asarray(time, dtype=float), "event": np.asarray(event, dtype=bool), "x": x}
    dist = R_DISTRIBUTIONS[distribution]
    code = ("x <- matrix(x, ncol = " + str(x.shape[1]) + "); "
            f"m <- survival::survreg(survival::Surv(time, event) ~ x, dist = '{dist}'); "
            "t <- summary(m)$table; k <- 2:(ncol(x) + 1); ci <- exp(stats::confint(m)); "
            "list(beta = unname(t[k, 1]), se = unname(t[k, 2]), z = unname(t[k, 3]), p = unname(t[k, 4]), "
            "ratio = unname(exp(stats::coef(m)[k])), low = unname(ci[k, 1]), high = unname(ci[k, 2]), "
            "scale = m$scale, shape = 1 / m$scale, aic = stats::AIC(m), "
            "converged = m$iter < survival::survreg.control()$maxiter)")
    out = _call(code, SURVIVAL, "The parametric survival model (R survival::survreg)",
                python_note="statsmodels has no parametric survival regression", **values)
    return {k: (np.atleast_1d(np.asarray(v, dtype=float)) if k != "converged" else bool(np.atleast_1d(v)[0]))
            for k, v in out.items()}


# ---------------------------------------------------------------- average_time_up_to=
def restricted_means(time, event, groups, levels, up_to):
    """The average time without the event in the first up_to time units of each group (restricted mean
    survival time), R summary(survival::survfit(Surv(time, event) ~ g), rmean = up_to)$table."""
    values = {"time": np.asarray(time, dtype=float), "event": np.asarray(event, dtype=bool),
              "g": _codes(groups), "g_levels": np.array([str(v) for v in levels], dtype=object),
              "tau": float(up_to)}
    code = ("g <- factor(g, levels = g_levels); "
            "t <- summary(survival::survfit(survival::Surv(time, event) ~ g), rmean = tau)$table; "
            "if (is.null(dim(t))) t <- t(as.matrix(t)); "
            "list(rmean = unname(t[, 'rmean']), se = unname(t[, 'se(rmean)']))")
    out = _call(code, SURVIVAL, "The average time without the event (R survival::survfit, rmean =)",
                python_note="statsmodels gives no restricted mean", **values)
    return np.atleast_1d(np.asarray(out["rmean"], dtype=float)), np.atleast_1d(np.asarray(out["se"], dtype=float))


def rmst_difference(time, event, arm, up_to):
    """The difference and ratio of the restricted mean survival times of two groups (arm 1 against arm 0),
    R survRM2::rmst2(time, status, arm, tau = up_to) (unadjusted.result: estimate, 95 % interval, p)."""
    values = {"time": np.asarray(time, dtype=float), "event": np.asarray(event, dtype=float),
              "arm": np.asarray(arm, dtype=float), "tau": float(up_to)}
    code = ("r <- survRM2::rmst2(time, event, arm, tau = tau); u <- r$unadjusted.result; "
            "list(estimate = unname(u[, 1]), low = unname(u[, 2]), high = unname(u[, 3]), p = unname(u[, 4]), "
            "arm0 = unname(r$RMST.arm0$rmst), arm1 = unname(r$RMST.arm1$rmst))")
    out = _call(code, ("survRM2",), "The difference in average time without the event (R survRM2::rmst2)",
                python_note="no Python package gives the restricted mean survival time difference", **values)
    return {k: np.atleast_1d(np.asarray(v, dtype=float)) for k, v in out.items()}


# ---------------------------------------------------------------- method="life table"
def life_table(starts, n_rows, lost, events):
    """The actuarial life table, R KMsurv::lifetab(tis, ninit, nlost, nevent): tis are the interval starts with
    NA at the end (the last interval is open)."""
    values = {"tis": np.append(np.asarray(starts, dtype=float), np.nan), "ninit": float(n_rows),
              "nlost": np.asarray(lost, dtype=float), "nevent": np.asarray(events, dtype=float)}
    code = ("t <- KMsurv::lifetab(tis, ninit, nlost, nevent); "
            "list(nsubs = t$nsubs, nlost = t$nlost, nrisk = t$nrisk, nevent = t$nevent, surv = t$surv, "
            "se_surv = t$se.surv, hazard = t$hazard, se_hazard = t$se.hazard)")
    out = _call(code, ("KMsurv",), "The actuarial life table (R KMsurv::lifetab)",
                python_note="no Python package gives the actuarial life table", **values)
    return {k: np.atleast_1d(np.asarray(v, dtype=float)) for k, v in out.items()}


# ---------------------------------------------------------------- allowing_for= on the curve words
def adjusted_curves(time, event, groups, levels, columns, at=None):
    """Survival curves adjusted for other columns by direct adjustment: R adjustedCurves::adjustedsurv(method =
    "direct", conf_int = TRUE) over a Cox model coxph(Surv(time, event) ~ group + columns, x = TRUE). Each
    row's curve is predicted as if in each group, then averaged over all rows. columns: {name: (values, is_text)}.
    Also the adjusted median of each group (adjusted_surv_quantile). at: the times to read, or None for every
    event time."""
    values = {"time": np.asarray(time, dtype=float), "event": np.asarray(event, dtype=float),
              "g": _codes(groups), "g_levels": np.array([str(v) for v in levels], dtype=object)}
    parts = ["time = time", "event = event", "group = factor(g, levels = g_levels)"]
    for i, (_, (column, is_text)) in enumerate(columns.items()):
        values[f"c{i}"] = _codes(column) if is_text else np.asarray(column, dtype=float)
        parts.append(f"c{i} = " + (f"factor(c{i})" if is_text else f"c{i}"))
    terms = " + ".join(["group"] + [f"c{i}" for i in range(len(columns))])
    times = ""
    if at is not None:
        values["at"] = np.asarray(at, dtype=float)
        times = ", times = at"
    code = (f"d <- data.frame({', '.join(parts)}); "
            f"m <- survival::coxph(survival::Surv(time, event) ~ {terms}, data = d, x = TRUE); "
            "a <- adjustedCurves::adjustedsurv(data = d, variable = 'group', ev_time = 'time', event = 'event', "
            f"method = 'direct', outcome_model = m, conf_int = TRUE{times}); "
            "q <- adjustedCurves::adjusted_surv_quantile(a, p = 0.5); "
            "list(time = a$adj$time, survival = a$adj$surv, group = as.character(a$adj$group), "
            "low = a$adj$ci_lower, high = a$adj$ci_upper, median_group = as.character(q$group), "
            "median = q$q_surv, rows = nrow(d))")
    out = _call(code, ("adjustedCurves", "riskRegression"),
                "Survival curves adjusted for other columns (R adjustedCurves::adjustedsurv)",
                python_note="no Python package gives directly adjusted survival curves", **values)
    return {k: (np.atleast_1d(np.asarray(v, dtype=float)) if k not in ("group", "median_group")
                else [str(g) for g in np.atleast_1d(v)]) for k, v in out.items()}


# ---------------------------------------------------------------- explain_survival(followed_from=) with tied starts
def cox_start_stop(time, event, x, entry, strata=None):
    """The Cox model of start-stop rows, R survival::coxph(Surv(start, stop, event) ~ x, ties = "efron"). Used
    when a row starts at an event time: R does not count that row as at risk at that event (the follow-up is
    (start, stop]), while statsmodels PHReg(entry=) does, which would count a person split into two rows twice."""
    x = np.asarray(x, dtype=float)
    values = {"time": np.asarray(time, dtype=float), "event": np.asarray(event, dtype=bool), "x": x,
              "start": np.asarray(entry, dtype=float)}
    rhs = "x"
    if strata is not None:
        values["s"] = _codes(strata)
        rhs += " + survival::strata(s)"
    code = ("x <- matrix(x, ncol = " + str(x.shape[1]) + "); "
            f"m <- survival::coxph(survival::Surv(start, time, event) ~ {rhs}, ties = 'efron'); "
            "list(beta = unname(stats::coef(m)), var = unname(stats::vcov(m)), loglik0 = m$loglik[1], "
            "loglik = m$loglik[2], converged = m$iter < survival::coxph.control()$iter.max)")
    out = _call(code, SURVIVAL, "The Cox model of rows that start at an event time (R survival::coxph)",
                python_note="statsmodels PHReg counts a row as at risk at an event time equal to its start, which R "
                            "does not", **values)
    k = x.shape[1]
    beta = np.atleast_1d(np.asarray(out["beta"], dtype=float))
    if not np.all(np.isfinite(beta)):
        from .._errors import SimplydataError

        raise SimplydataError("The model cannot be fitted: two of the terms say the same thing "
                              "(or a term has the same value in every row with an event).")
    return dict(beta=beta,
                var=np.asarray(out["var"], dtype=float).reshape(k, k),
                loglik0=float(np.asarray(out["loglik0"]).reshape(-1)[0]),
                loglik=float(np.asarray(out["loglik"]).reshape(-1)[0]),
                converged=bool(np.atleast_1d(out["converged"])[0]), x=x - x.mean(axis=0))
