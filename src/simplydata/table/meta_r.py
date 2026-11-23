"""The R calls behind combine_studies (phase S3b-1): one R program around metafor.

Nothing is calculated here: the function hands the columns that combine_studies has already checked to R
metafor and gives back metafor's own numbers. metafor is checked with need_r() but never attached (every call
names its package, metafor::rma), so it cannot hide a function of another package.

* metafor::escalc() makes each study's effect and its variance (risk ratio, odds ratio, risk difference, rate
  ratio, Hedges' g, difference or ratio of averages, Fisher's z of a correlation); metafor::conv.wald() turns an
  estimate with its confidence interval into the same.
* metafor::rma() combines them (REML, DerSimonian-Laird, Paule-Mandel or a common effect; Hartung-Knapp with the
  ad hoc rule, test = "adhoc", or the normal interval, test = "z"); metafor::rma.mh() and metafor::rma.peto()
  give Mantel-Haenszel and Peto.
* predict() gives the combined effect with its interval and the prediction interval, confint() the intervals of
  tau-squared and I-squared, weights() each study's weight in percent.
* metafor::regtest(model = "lm") gives the classic Egger test (predictor = "sei") or Peters' test (predictor =
  "ninv"); metafor::trimfill() the trim-and-fill what-if.
* for_each_group_in=: rma() in each subgroup (each with its own tau-squared), then the test of the difference
  between the subgroup estimates, rma(estimates, sei = ..., mods = ~ factor(group), method = "EE").
* using=: a meta-regression, rma(yi, vi, mods = X).
* every rma() with an iterative tau-squared (REML, Paule-Mandel) gets control = list(tol = 1e-10, threshold = 1e-10, maxiter = 1000):
  metafor's default stopping rule (1e-5) left the Paule-Mandel tau-squared of the BCG trials 7.9e-5 short of the
  converged value (simplydata_tests FINDINGS A7); only the stopping rule changes, not the method.
"""

from __future__ import annotations

import numpy as np

# The R program. Inputs: route, measure, method, test, tfname, drop00 and the columns of the route; has_group, grp,
# grp_levels; has_mods, X; small, peters. Every number of the answer is made here, in R.
PROGRAM = r"""
tf <- switch(tfname, exp = exp, ztor = metafor::transf.ztor, none = NULL)
ni <- NULL; corrected <- 0; dz <- logical(0)
if (route == "counts") {
  e <- metafor::escalc(measure = measure, ai = a1, n1i = n1, ci = a2, n2i = n2, drop00 = drop00)
  ni <- n1 + n2
  dz <- (a1 == 0 & a2 == 0) | (a1 == n1 & a2 == n2)
  zero <- a1 == 0 | a1 == n1 | a2 == 0 | a2 == n2
  corrected <- if (measure == "RD") sum(zero) else if (measure == "PETO") 0 else sum(zero & !dz)
} else if (route == "rates") {
  e <- metafor::escalc(measure = "IRR", x1i = x1, t1i = t1, x2i = x2, t2i = t2, drop00 = TRUE)
  dz <- x1 == 0 & x2 == 0
  corrected <- sum((x1 == 0 | x2 == 0) & !dz)
} else if (route == "averages") {
  e <- metafor::escalc(measure = measure, m1i = m1, sd1i = s1, n1i = c1, m2i = m2, sd2i = s2, n2i = c2)
  ni <- c1 + c2
} else if (route == "intervals") {
  e <- if (ratio) metafor::conv.wald(out = est, ci.lb = lo, ci.ub = hi, level = level, transf = log) else
    metafor::conv.wald(out = est, ci.lb = lo, ci.ub = hi, level = level)
} else if (route == "errors") {
  e <- metafor::escalc(measure = "GEN", yi = if (ratio) log(est) else est, sei = se)
} else {
  e <- metafor::escalc(measure = "ZCOR", ri = r, ni = n)
  ni <- n
}
yi <- as.numeric(e$yi); vi <- as.numeric(e$vi); ok <- !is.na(yi) & !is.na(vi)
k_all <- length(yi); ids <- seq_len(k_all)
s <- if (is.null(tf)) summary(e) else summary(e, transf = tf)
out <- list(study = as.numeric(s$yi), study_low = as.numeric(s$ci.lb), study_high = as.numeric(s$ci.ub),
            study_se = sqrt(vi), corrected = corrected, double_zero = which(dz & !ok),
            version = as.character(utils::packageVersion("metafor")))
shown <- function(p) list(est = as.numeric(p$pred), low = as.numeric(p$ci.lb), high = as.numeric(p$ci.ub),
                          pi_low = if (is.null(p$pi.lb)) NA_real_ else as.numeric(p$pi.lb),
                          pi_high = if (is.null(p$pi.ub)) NA_real_ else as.numeric(p$pi.ub),
                          pi_dist = if (is.null(p$pi.dist)) "" else as.character(p$pi.dist),
                          pi_df = if (is.null(p$pi.ddf)) NA_real_ else as.numeric(p$pi.ddf))
predicted <- function(f) if (is.null(tf)) stats::predict(f) else stats::predict(f, transf = tf)
# a tighter stopping rule than metafor's default (tol and threshold 1e-5) for the iterative estimators of tau^2
# (REML, Paule-Mandel): the same method, run until it has converged (data-and-fixes, finding A7)
ctl <- list(tol = 1e-10, threshold = 1e-10, maxiter = 1000); iterative <- method %in% c("REML", "PM")
fit_on <- function(i, how = test) {
  if (method == "MH") {
    if (route == "rates") return(metafor::rma.mh(x1i = x1[i], t1i = t1[i], x2i = x2[i], t2i = t2[i], measure = "IRR",
                                                 slab = ids[i]))
    return(metafor::rma.mh(ai = a1[i], n1i = n1[i], ci = a2[i], n2i = n2[i], measure = measure, slab = ids[i]))
  }
  if (method == "PETO") return(metafor::rma.peto(ai = a1[i], n1i = n1[i], ci = a2[i], n2i = n2[i], slab = ids[i]))
  j <- i[ok[i]]
  if (length(j) == 1) return(metafor::rma(yi[j], vi[j], method = "EE", test = "z", slab = ids[j]))
  metafor::rma(yi[j], vi[j], method = method, test = how, slab = ids[j], control = if (iterative) ctl else list())
}
about <- function(f) {
  kk <- if (!is.null(f$k.yi)) f$k.yi else f$k  # rma.mh and rma.peto keep tables without an effect in k
  r <- list(beta = as.numeric(f$b)[1], se = as.numeric(f$se)[1], p = as.numeric(f$pval)[1],
            stat = as.numeric(f$zval)[1], df = if (is.null(f$ddf) || is.na(f$ddf[1])) NA_real_ else as.numeric(f$ddf[1]),
            k = kk, Q = as.numeric(f$QE), Q_df = kk - f$p, Q_p = as.numeric(f$QEp),
            I2 = if (is.null(f$I2)) NA_real_ else as.numeric(f$I2),
            tau2 = if (is.null(f$tau2)) NA_real_ else as.numeric(f$tau2),
            tau2_low = NA_real_, tau2_high = NA_real_, tau_low = NA_real_, tau_high = NA_real_,
            I2_low = NA_real_, I2_high = NA_real_)
  if (inherits(f, "rma.uni") && f$method != "EE" && f$k > 1) {
    ci <- tryCatch(stats::confint(f)$random, error = function(err) NULL)
    if (!is.null(ci)) {
      r$tau2_low <- ci[1, 2]; r$tau2_high <- ci[1, 3]; r$tau_low <- ci[2, 2]; r$tau_high <- ci[2, 3]
      r$I2_low <- ci[3, 2]; r$I2_high <- ci[3, 3]
    }
  }
  r$tau <- sqrt(r$tau2)
  r$tau_factor <- if (tfname == "exp") exp(r$tau) else NA_real_
  c(r, shown(predicted(f)))
}
weights_of <- function(f) {
  w <- stats::weights(f); all <- rep(NA_real_, k_all); all[as.integer(names(w))] <- as.numeric(w); all
}
if (has_mods) {
  fit <- metafor::rma(yi, vi, mods = X, method = method, test = test, slab = ids,
                      control = if (iterative) ctl else list())
  out$weights <- weights_of(fit)
  b <- as.numeric(fit$b)
  out$mods <- list(beta = b, se = as.numeric(fit$se), low = as.numeric(fit$ci.lb), high = as.numeric(fit$ci.ub),
                   p = as.numeric(fit$pval), df = if (is.null(fit$ddf) || is.na(fit$ddf[1])) NA_real_ else
                     as.numeric(fit$ddf[1]),
                   shown = if (is.null(tf) || tfname != "exp") b else exp(b),
                   shown_low = if (is.null(tf) || tfname != "exp") as.numeric(fit$ci.lb) else exp(as.numeric(fit$ci.lb)),
                   shown_high = if (is.null(tf) || tfname != "exp") as.numeric(fit$ci.ub) else exp(as.numeric(fit$ci.ub)),
                   R2 = if (is.null(fit$R2)) NA_real_ else as.numeric(fit$R2), tau2 = as.numeric(fit$tau2),
                   QM = as.numeric(fit$QM), QM_df = as.numeric(fit$QMdf[1]), QM_p = as.numeric(fit$QMp),
                   Q = as.numeric(fit$QE), Q_df = fit$k - fit$p, Q_p = as.numeric(fit$QEp), k = fit$k)
} else {
  fit <- fit_on(ids)
  out$weights <- weights_of(fit)
  out$all <- about(fit)
  if (has_group) {
    fits <- lapply(grp_levels, function(g) fit_on(which(grp == g)))
    found <- lapply(fits, function(f) { a <- about(f); a$weights <- weights_of(f); a })
    names(found) <- grp_levels
    out$groups <- found
    # the test of the difference between subgroups uses each subgroup's estimate with its normal (z) standard
    # error, as RevMan and R meta do, also when the subgroups' own intervals are Hartung-Knapp
    zfits <- if (test == "z") fits else lapply(grp_levels, function(g) fit_on(which(grp == g), "z"))
    est <- sapply(zfits, function(f) as.numeric(f$b)[1])
    sei <- sapply(zfits, function(f) as.numeric(f$se)[1])
    lev <- factor(grp_levels, levels = grp_levels)
    between <- metafor::rma(est, sei = sei, mods = ~ lev, method = "EE")
    out$between <- list(Q = as.numeric(between$QM), df = as.numeric(between$QMdf[1]), p = as.numeric(between$QMp))
  }
  if (small && sum(ok) >= 10) {
    # Peters' test: weighted by 1 / (1 / (events) + 1 / (non-events)) of both groups together (Peters et al.
    # 2006), so these are given as vi; the predictor is 1 / n
    pv <- if (peters) 1 / (a1 + a2) + 1 / (n1 - a1 + n2 - a2) else NULL
    rt <- if (peters) metafor::regtest(yi[ok], vi = pv[ok], ni = ni[ok], model = "lm", predictor = "ninv") else
      metafor::regtest(yi[ok], vi[ok], model = "lm", predictor = "sei")
    out$egger <- list(stat = as.numeric(rt$zval), df = as.numeric(rt$dfs), p = as.numeric(rt$pval))
    if (inherits(fit, "rma.uni")) {
      filled <- metafor::trimfill(fit)
      out$trimfill <- c(list(k0 = as.numeric(filled$k0), side = as.character(filled$side),
                             test = as.character(filled$test)), shown(predicted(filled)))
    }
  }
}
out
"""


def combine(route, values, measure, method, test, transform, drop00=True, group=None, levels=None, mods=None,
            small=True, peters=False):
    """R metafor for combine_studies; values holds the route's columns (a1, n1, a2, n2 / x1, t1, x2, t2 / m1, s1,
    c1, m2, s2, c2 / est, lo, hi, level, ratio / est, se, ratio / r, n). transform: "exp" (ratios), "ztor"
    (correlations) or "none". group/levels: the subgroup of each study and the subgroups in order; mods: a matrix
    of the meta-regression's columns."""
    from .._r import need_r, r_call

    need_r(("metafor",), "Combining studies (R metafor)",
           "statsmodels has fixed and random effects (DerSimonian-Laird, Paule-Mandel) but no REML, no prediction "
           "interval, no Egger or trim-and-fill, no meta-regression and no Peto, so simplydata uses R metafor")
    given = {"route": route, "measure": measure, "method": method, "test": test, "tfname": transform,
             "drop00": bool(drop00), "has_group": group is not None, "has_mods": mods is not None,
             "small": bool(small), "peters": bool(peters)}
    for name, value in values.items():
        given[name] = value if isinstance(value, (bool, str)) else np.asarray(value, dtype=float)
    if group is not None:
        given["grp"] = np.array([str(g) for g in group], dtype=object)
        given["grp_levels"] = np.array([str(g) for g in levels], dtype=object)
    if mods is not None:
        given["X"] = np.asarray(mods, dtype=float).reshape(len(mods), -1)
    return r_call(PROGRAM, what="Combining studies (R metafor)", source="metafor", note_words=_note_words, **given)


def _note_words(note):
    """metafor's notes that combine_studies says in its own words (studies left out, the test chosen for one
    study) are not repeated."""
    quiet = ("Studies with NAs omitted", "Some yi/vi values are NA", "Setting argument test=",
             "Cannot estimate tau^2", "Some yi/vi values")
    return "" if any(q in note for q in quiet) else note
