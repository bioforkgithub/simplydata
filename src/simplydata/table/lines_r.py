"""The R calls behind the line and curve words of phase S3a-2 ("lines and curves").

Each function hands numbers that the word has already checked to an R package and gives back R's
own numbers. Nothing is calculated here: the functions write the R call, pass the values and read
the result.

* dose_response: drc::drm() with drc::ED(interval = "delta"), drc::EDcomp() and drc::noEffect(),
  for table.fit_dose_response and chart.fit_dose_response.
* bends: segmented::segmented() with confint(), slope() and segmented::davies.test(), for
  fit_line(with_bends=).
* two_error_line: smatr::sma() (standardised major axis, major axis) and mcr::mcreg() (Deming,
  Passing-Bablok), for fit_line(method=).
* loess: stats::loess() and predict(se = TRUE), for method="loess" of add_smoothed_column and
  draw_smooth_line.
* percentile_lines: quantreg::rq() with summary(se = "nid"), for explain(for_percentile=).
* self_start: stats::getInitial() of R's self-starting models (SSlogis ...), for the start values
  of fit_curve(of_kind=).
* power_transform: car::powerTransform() with summary() and testTransform(), for
  find_best_power_of(using=).
"""

from __future__ import annotations

import numpy as np

# drc's of_kind= words -> the drc function
DRC_KINDS = {"4 parameter log-logistic": "LL.4", "3 parameter log-logistic": "LL.3",
             "5 parameter log-logistic": "LL.5", "2 parameter log-logistic": "LL.2", "weibull": "W1.4"}

# R warnings that say nothing to the user: drc's search for the best curve tries impossible values
_QUIET_NOTES = ("NaNs produced", "NAs introduced by coercion")


def _call(code, packages, **options):
    """r_call with the packages checked (need_r) but not attached: every call here names its package (drc::drm),
    and attaching drc would hide stats::gaussian (drc has its own gaussian()) from later R calls such as mgcv's."""
    from .._r import need_r, r_call

    need_r(packages, options.get("what", "This"), options.get("python_note"))
    return r_call(code, **options)


def _drop_quiet(note: str) -> str:
    return "" if any(q in note for q in _QUIET_NOTES) else note


def dose_response(dose, response, kind, percents, trials=None, groups=None):
    """R drc::drm(response ~ dose, fct = LL.4() ...) and drc::ED(m, percents, interval = "delta").

    trials= (yes or no): response is the number of yes out of trials; drm(yes / trials ~ dose,
    weights = trials, type = "binomial"). groups= (for_each_group_in=): one curve per group in one model,
    drm(..., curveid = g), with drc::EDcomp() for the ratios of the ED50s and their tests.
    Gives back the parameter table, the ED table, drc::noEffect() and (with groups) the ratios."""

    fct = DRC_KINDS[kind]
    values = {"x": np.asarray(dose, dtype=float), "y": np.asarray(response, dtype=float),
              "p": np.asarray(percents, dtype=float)}
    left, extra = "y", ""
    if trials is not None:
        values["n"] = np.asarray(trials, dtype=float)
        left, extra = "y / n", ", weights = n, type = 'binomial'"
    curve = ""
    if groups is not None:
        values["g"] = np.asarray(groups, dtype=object)
        curve = ", curveid = g"
    code = ("d <- data.frame(x = x, y = y" + (", n = n" if trials is not None else "")
            + (", g = factor(g, levels = unique(g))" if groups is not None else "") + "); "
            f"m <- drc::drm({left} ~ x{curve}, data = d, fct = drc::{fct}(){extra}); "
            "s <- summary(m)$coefficients; "
            "e <- drc::ED(m, p, interval = 'delta', display = FALSE); "
            "ne <- drc::noEffect(m); ci <- stats::confint(m); "
            "rse <- if (is.null(summary(m)$rseMat)) NA_real_ else summary(m)$rseMat[1, 1]; "
            "out <- list(names = rownames(s), estimate = unname(s[, 1]), se = unname(s[, 2]), t = unname(s[, 3]), "
            "p = unname(s[, 4]), ed_names = rownames(e), ed = unname(e[, 1]), ed_se = unname(e[, 2]), "
            "ed_low = unname(e[, 3]), ed_high = unname(e[, 4]), df = stats::df.residual(m), rse = rse, "
            "no_effect = unname(ne[1]), no_effect_df = unname(ne[2]), no_effect_p = unname(ne[3]), "
            "loglik = as.numeric(stats::logLik(m)), n = nrow(d), low = unname(ci[, 1]), high = unname(ci[, 2])); ")
    if groups is not None:
        code += ("if (nlevels(d$g) > 1) { r1 <- drc::EDcomp(m, c(50, 50), interval = 'delta', display = FALSE); "
                 "r2 <- drc::EDcomp(m, c(50, 50), display = FALSE); "
                 "out$ratio_names <- rownames(r1); out$ratio <- unname(r1[, 1]); out$ratio_low <- unname(r1[, 2]); "
                 "out$ratio_high <- unname(r1[, 3]); out$ratio_se <- unname(r2[, 2]); out$ratio_p <- unname(r2[, 4]) }; ")
    code += "out"
    return _call(code, ("drc",), source="drc",
                  what="Dose-response curves (R drc::drm() and drc::ED())",
                  python_note="no Python package fits dose-response curves with drc's ED intervals",
                  note_words=_drop_quiet, **values)


def dose_response_curve(dose, response, kind, at, trials=None):
    """The fitted dose-response curve at the doses in at (R predict() of drc::drm()), for the chart twin."""

    fct = DRC_KINDS[kind]
    values = {"x": np.asarray(dose, dtype=float), "y": np.asarray(response, dtype=float),
              "at": np.asarray(at, dtype=float)}
    left, extra = "y", ""
    if trials is not None:
        values["n"] = np.asarray(trials, dtype=float)
        left, extra = "y / n", ", weights = n, type = 'binomial'"
    code = ("d <- data.frame(x = x, y = y" + (", n = n" if trials is not None else "") + "); "
            f"m <- drc::drm({left} ~ x, data = d, fct = drc::{fct}(){extra}); "
            "e <- drc::ED(m, 50, interval = 'delta', display = FALSE); "
            "list(fitted = unname(stats::predict(m, newdata = data.frame(x = at))), ed50 = unname(e[1, 1]), "
            "ed50_low = unname(e[1, 3]), ed50_high = unname(e[1, 4]))")
    return _call(code, ("drc",), source="drc", what="A dose-response curve (R drc::drm())",
                  python_note="no Python package fits dose-response curves with drc's ED intervals",
                  note_words=_drop_quiet, **values)


SEGMENTED_SEED = 1  # segmented restarts its search from bootstrap samples; this seed makes it the same every time


def bends(x, y, how_many):
    """R segmented::segmented(lm(y ~ x), seg.Z = ~ x, npsi = how_many): the bend points with confint()
    (delta method), the slopes of each piece with slope(), the line's intercept, and
    segmented::davies.test() of "no bend at all"."""

    code = ("d <- data.frame(x = x, y = y); o <- stats::lm(y ~ x, data = d); "
            "dv <- segmented::davies.test(o, seg.Z = ~ x); "
            f"s <- segmented::segmented(o, seg.Z = ~ x, npsi = {int(how_many)}, "
            f"control = segmented::seg.control(seed = {SEGMENTED_SEED})); "
            "if (!inherits(s, 'segmented')) { list(found = FALSE, davies_p = dv$p.value, "
            "davies_at = unname(dv$statistic)) } else { "
            "ci <- stats::confint(s, digits = 15); sl <- segmented::slope(s, digits = 15)$x; it <- segmented::intercept(s, digits = 15)$x; "
            "ss <- summary(s); "
            "list(found = TRUE, psi = unname(s$psi[, 'Est.']), psi_se = unname(s$psi[, 'St.Err']), "
            "psi_low = unname(ci[, 2]), psi_high = unname(ci[, 3]), slope = unname(sl[, 1]), "
            "slope_se = unname(sl[, 2]), slope_low = unname(sl[, 4]), slope_high = unname(sl[, 5]), "
            "intercept = unname(it[, 1]), sigma = ss$sigma, r2 = ss$r.squared, df = s$df.residual, "
            "davies_p = dv$p.value, davies_at = unname(dv$statistic)) }")
    return _call(code, ("segmented",), source="segmented",
                  what="A line with bends (R segmented::segmented())",
                  python_note="no Python package estimates bend points with segmented's intervals and Davies' test",
                  x=np.asarray(x, dtype=float), y=np.asarray(y, dtype=float))


def two_error_line(x, y, method, y_error_over_x_error=1.0):
    """A line for two measures that both carry error: R smatr::sma(y ~ x, method = "SMA" or "MA") or
    R mcr::mcreg(x, y, method.reg = "Deming" or "PaBa", method.ci = "analytical"). mcr's error.ratio is the
    error variance of x (the reference method) over that of y, so it gets 1 / y_error_over_x_error."""

    values = {"x": np.asarray(x, dtype=float), "y": np.asarray(y, dtype=float)}
    if method in ("standardised major axis", "major axis"):
        r_method = "SMA" if method == "standardised major axis" else "MA"
        code = (f"f <- smatr::sma(y ~ x, data = data.frame(x = x, y = y), method = '{r_method}'); "
                "k <- f$coef[[1]]; "
                "list(intercept = k[1, 1], intercept_low = k[1, 2], intercept_high = k[1, 3], slope = k[2, 1], "
                "slope_low = k[2, 2], slope_high = k[2, 3], r2 = unname(f$r2[[1]]), p = unname(f$pval[[1]]), "
                "n = unname(f$n[[1]]))")
        return _call(code, ("smatr",), source="smatr::sma",
                      what=f"A {method} line (R smatr::sma())",
                      python_note="no Python package fits standardised or major axis lines with smatr's intervals",
                      **values)
    values["ratio"] = np.asarray([1.0 / float(y_error_over_x_error)])
    r_method = "Deming" if method == "deming" else "PaBa"
    code = (f"m <- mcr::mcreg(x, y, error.ratio = ratio, method.reg = '{r_method}', method.ci = 'analytical'); "
            "k <- m@para; "
            "list(intercept = k[1, 'EST'], intercept_se = k[1, 'SE'], intercept_low = k[1, 'LCI'], "
            "intercept_high = k[1, 'UCI'], slope = k[2, 'EST'], slope_se = k[2, 'SE'], slope_low = k[2, 'LCI'], "
            "slope_high = k[2, 'UCI'], error_ratio = m@error.ratio)")
    return _call(code, ("mcr",), source="mcr::mcreg",
                  what=f"A {'Deming' if method == 'deming' else 'Passing-Bablok'} line (R mcr::mcreg())",
                  python_note="no Python package fits Deming or Passing-Bablok lines with mcr's intervals", **values)


def loess(x, y, span, at, level=0.95):
    """R stats::loess(y ~ x, span =, degree = 2) and predict(m, newdata, se = TRUE); the band's t quantile
    uses loess's own degrees of freedom, one.delta^2 / two.delta, as R's predict.loess intervals do."""

    code = ("m <- stats::loess(y ~ x, data = data.frame(x = x, y = y), span = span, degree = 2); "
            "p <- stats::predict(m, newdata = data.frame(x = at), se = TRUE); "
            "q <- stats::qt((1 + level) / 2, m$one.delta^2 / m$two.delta); "
            "list(fit = unname(p$fit), se = unname(p$se.fit), low = unname(p$fit - q * p$se.fit), "
            "high = unname(p$fit + q * p$se.fit), df = m$one.delta^2 / m$two.delta, "
            "enp = m$enp, sigma = m$s)")
    return _call(code, (), what="A loess curve (R stats::loess())", source="stats::loess",
                  python_note='statsmodels lowess has no standard errors; method="lowess" works without R',
                  x=np.asarray(x, dtype=float), y=np.asarray(y, dtype=float), at=np.asarray(at, dtype=float),
                  span=np.asarray([float(span)]), level=np.asarray([float(level)]))


def percentile_lines(X, y, taus):
    """R quantreg::rq(y ~ 0 + X, tau = each of taus) (Barrodale-Roberts simplex) with summary(se = "nid")
    (the Hendricks-Koenker sandwich, which allows the spread to change with x): estimates, standard errors,
    t, p for each tau."""

    code = ("out <- list(); for (i in seq_along(taus)) { f <- quantreg::rq(y ~ 0 + X, tau = taus[i]); "
            "s <- summary(f, se = 'nid')$coefficients; "
            "out[[paste0('t', i)]] <- list(beta = unname(s[, 1]), se = unname(s[, 2]), t = unname(s[, 3]), "
            "p = unname(s[, 4]), df = length(y) - ncol(X), unique = !isTRUE(attr(f, 'nonunique'))) }; out")
    return _call(code, ("quantreg",), source="quantreg::rq",
                  what="Percentile lines (R quantreg::rq())",
                  python_note="statsmodels QuantReg gives the same lines up to about 1e-7, but none of the standard "
                              "errors R's quantreg gives",
                  X=np.asarray(X, dtype=float), y=np.asarray(y, dtype=float), taus=np.asarray(taus, dtype=float))


# fit_curve(of_kind=) -> R's self-starting model and its parameter names
SELF_START = {"logistic growth": ("SSlogis", ("Asym", "xmid", "scal")),
              "4 parameter logistic": ("SSfpl", ("A", "B", "xmid", "scal")),
              "michaelis-menten": ("SSmicmen", ("Vm", "K")),
              "rise to a limit": ("SSasympOrig", ("Asym", "lrc")),
              "rise or fall to a limit": ("SSasymp", ("Asym", "R0", "lrc")),
              "gompertz growth": ("SSgompertz", ("Asym", "b2", "b3")),
              "weibull growth": ("SSweibull", ("Asym", "Drop", "lrc", "pwr")),
              "two exponentials": ("SSbiexp", ("A1", "lrc1", "A2", "lrc2"))}


def self_start(kind, x, y) -> dict | None:
    """R stats::getInitial() of the self-starting model: start values found by R's own rules; None when R
    cannot find any (the word then searches the whole range)."""

    model, names = SELF_START[kind]
    code = (f"tryCatch(as.list(stats::getInitial(y ~ stats::{model}(x, {', '.join(names)}), "
            "data = data.frame(x = x, y = y))), error = function(e) NULL)")
    found = _call(code, (), what="Start values for a growth curve (R stats::getInitial())", source="stats::getInitial",
                   x=np.asarray(x, dtype=float), y=np.asarray(y, dtype=float))
    if not found:
        return None
    return {k: float(np.atleast_1d(v)[0]) for k, v in found.items()}


def power_transform(X, y, family):
    """R car::powerTransform(lm(y ~ 0 + X), family = "bcPower" or "yjPower"): the power by maximum
    likelihood, its rounded power and Wald interval (summary()), and the likelihood-ratio tests of
    power 0 and power 1 (car::testTransform())."""

    code = (f"m <- stats::lm(y ~ 0 + X); f <- car::powerTransform(m, family = '{family}'); "
            "s <- summary(f)$result; t0 <- car::testTransform(f, 0); t1 <- car::testTransform(f, 1); "
            "list(power = unname(s[1, 1]), rounded = unname(s[1, 2]), low = unname(s[1, 3]), high = unname(s[1, 4]), "
            "lr0 = unname(t0[1, 1]), p0 = as.numeric(t0[1, 'pval']), "
            "lr1 = unname(t1[1, 1]), p1 = as.numeric(t1[1, 'pval']))")
    return _call(code, ("car",), source="car::powerTransform",
                  what="The best power for a model's outcome (R car::powerTransform())",
                  python_note="SciPy stats.boxcox finds the power for one column on its own (without using=)",
                  X=np.asarray(X, dtype=float), y=np.asarray(y, dtype=float))
