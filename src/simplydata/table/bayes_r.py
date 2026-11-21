"""The R calls of phase S3d-3 (Bayesian methods). simplydata puts the numbers in and words the answer; every number
comes from the R package.

The light route (Bayes factors and posteriors for the simple tests), R BayesFactor (Morey & Rouder):

* t_test(): BayesFactor::ttestBF() for two groups, two matched columns (paired = TRUE) or one column against a
  value, with the JZS prior (a Cauchy prior on the effect size, Rouder et al. 2009) of width rscale ("medium" 0.707,
  "wide" 1, "ultrawide" 1.414, or a number), then BayesFactor::posterior(iterations = 10000) after set.seed(), and
  the posterior's 2.5 %, 50 % and 97.5 % quantiles from coda's summary(). BayesFactor's posterior() of a one-sample
  test ignores mu = (checked with BayesFactor 0.9.12-4.8: the draws are the same as with mu = 0), so a column
  against a value is given to ttestBF() as x - value (what ttestBF does inside for its Bayes factor; the Bayes factor
  is the same, and the posterior is that of the difference from the value).
* correlation(): BayesFactor::correlationBF() with the stretched beta prior of width rscale ("medium" 1/3, "wide"
  1/sqrt(3), "ultrawide" 1; Ly, Verhagen & Wagenmakers 2016), and its posterior of rho.
* counts(): BayesFactor::contingencyTableBF(sampleType = "indepMulti", fixedMargin = "rows") with the groups as rows
  (each group's total fixed by the design; Gunel & Dickey 1974, prior concentration 1), and the posterior of each
  group's shares (omega).

The heavy route (Bayesian models), R rstanarm (Goodrich, Gabry, Ali & Brilleman) on Stan: stan_glm() and
stan_glmer() with 4 chains of 2000 iterations (1000 warm-up), seed = with_seed, cores = 1 (no worker processes and
no sockets), rstanarm's default weakly informative priors scaled to the data (printed from prior_summary()); the
posterior median and the central 95 % interval (posterior_interval()); rank-normalised R-hat and bulk and tail
effective sample sizes from the posterior package (Vehtari et al. 2021); divergent transitions and maximum tree
depth from rstan. rstanarm's models are compiled when the package is built, so nothing is compiled or written while
simplydata runs (checked: no new file in R's temporary folder, the working folder or the home folder).
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError

DRAWS = 10000  # BayesFactor posterior draws (design Z01-Z02)
CHAINS, ITERATIONS, WARMUP = 4, 2000, 1000  # rstanarm's defaults, written out (design Z03-Z06); warm-up is half
PREDICTED_DRAWS = 50  # posterior predictive draws in the picture (bayesplot's pp_check shows 50 by default)
LIGHT_PACKAGES = ("BayesFactor",)
HEAVY_PACKAGES = ("rstanarm", "rstan", "posterior")
LIGHT_NOTE = "without R, leave out bayesian=True for the usual test with its p-value"
HEAVY_NOTE = ("rstanarm is a large optional R package (about 400 MB with Stan); in R: install.packages(\"rstanarm\", "
              "type = \"binary\") where a ready-made build exists (Windows, macOS; Linux from Posit's public package "
              "manager). Without it, leave out bayesian=True for the usual model")

SEED_R = 'set.seed(seed, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection"); '
_QUANTILES = 'c("2.5%", "50%", "97.5%")'


def _light_call(code, what, **values):
    from .._r import r_call

    return r_call(code, packages=LIGHT_PACKAGES, what=what, python_note=LIGHT_NOTE, source="BayesFactor", **values)


def _three(value):
    return [float(v) for v in np.asarray(value, dtype=float).ravel()]


def t_test(kind, x, y=None, value=None, width="medium", seed=1):
    """{bf, bf_against, error, width, est: [low, middle, high], effect: [low, middle, high]} from R BayesFactor.

    kind: "two groups" (x, y: the groups), "matched" (x after, y before: paired = TRUE) or "one" (x against value)."""
    if kind == "two groups":
        call, par = "BayesFactor::ttestBF(x = x, y = y, paired = FALSE, rscale = width)", "beta (x - y)"
        values = dict(x=x, y=y)
    elif kind == "matched":
        call, par = "BayesFactor::ttestBF(x = x, y = y, paired = TRUE, rscale = width)", "mu"
        values = dict(x=x, y=y)
    else:  # posterior() ignores mu=, so the column is shifted by the value here (see the module text)
        call, par = "BayesFactor::ttestBF(x = x - value, rscale = width)", "mu"
        values = dict(x=x, value=float(value))
    code = (f"b <- {call}; " + SEED_R
            + f"p <- BayesFactor::posterior(b, iterations = {DRAWS}, progress = FALSE); q <- summary(p)$quantiles; "
            "list(bf = BayesFactor::extractBF(b)$bf, bf_against = BayesFactor::extractBF(1 / b)$bf, "
            "error = BayesFactor::extractBF(b)$error, width = unname(b@numerator[[1]]@prior$rscale), "
            f"est = unname(q['{par}', {_QUANTILES}]), effect = unname(q['delta', {_QUANTILES}]))")
    found = _light_call(code, "The Bayes factor t-test (R BayesFactor::ttestBF())", width=width, seed=int(seed),
                        **values)
    return {"bf": float(np.ravel(found["bf"])[0]), "bf_against": float(np.ravel(found["bf_against"])[0]),
            "error": float(np.ravel(found["error"])[0]), "width": float(np.ravel(found["width"])[0]),
            "est": _three(found["est"]), "effect": _three(found["effect"])}


def correlation(a, b, width="medium", seed=1):
    """{bf, bf_against, error, width, rho: [low, middle, high]} from R BayesFactor::correlationBF()."""
    code = ("b <- BayesFactor::correlationBF(y = a, x = b, rscale = width); " + SEED_R
            + f"p <- BayesFactor::posterior(b, iterations = {DRAWS}, progress = FALSE); q <- summary(p)$quantiles; "
            "list(bf = BayesFactor::extractBF(b)$bf, bf_against = BayesFactor::extractBF(1 / b)$bf, "
            "error = BayesFactor::extractBF(b)$error, width = unname(b@numerator[[1]]@prior$rscale), "
            f"rho = unname(q['rho', {_QUANTILES}]))")
    found = _light_call(code, "The Bayes factor for a correlation (R BayesFactor::correlationBF())", a=a, b=b,
                        width=width, seed=int(seed))
    return {"bf": float(np.ravel(found["bf"])[0]), "bf_against": float(np.ravel(found["bf_against"])[0]),
            "error": float(np.ravel(found["error"])[0]), "width": float(np.ravel(found["width"])[0]),
            "rho": _three(found["rho"])}


def counts(values, groups, value_order, group_order, seed=1):
    """{bf, bf_against, error, share: {(group, value): [low, middle, high]}} from R
    BayesFactor::contingencyTableBF(sampleType = "indepMulti", fixedMargin = "rows"), groups as rows."""
    code = ("tab <- table(factor(g, levels = g_levels), factor(v, levels = v_levels)); "
            "b <- BayesFactor::contingencyTableBF(tab, sampleType = 'indepMulti', fixedMargin = 'rows'); " + SEED_R
            + f"p <- BayesFactor::posterior(b, iterations = {DRAWS}, progress = FALSE); q <- summary(p)$quantiles; "
            "w <- q[grep('^omega', rownames(q)), , drop = FALSE]; "
            "list(bf = BayesFactor::extractBF(b)$bf, bf_against = BayesFactor::extractBF(1 / b)$bf, "
            "error = BayesFactor::extractBF(b)$error, names = rownames(w), "
            "low = unname(w[, '2.5%']), middle = unname(w[, '50%']), high = unname(w[, '97.5%']))")
    found = _light_call(code, "The Bayes factor for a table of counts (R BayesFactor::contingencyTableBF())",
                        v=np.array([str(v) for v in values], dtype=object),
                        g=np.array([str(v) for v in groups], dtype=object),
                        v_levels=np.array([str(v) for v in value_order], dtype=object),
                        g_levels=np.array([str(v) for v in group_order], dtype=object), seed=int(seed))
    import re

    share = {}
    for name, low, mid, high in zip(np.atleast_1d(found["names"]), _three(found["low"]), _three(found["middle"]),
                                    _three(found["high"])):
        i, j = (int(n) for n in re.findall(r"\d+", str(name)))  # omega[group row, value column], from 1
        share[(group_order[i - 1], value_order[j - 1])] = [low, mid, high]
    return {"bf": float(np.ravel(found["bf"])[0]), "bf_against": float(np.ravel(found["bf_against"])[0]),
            "error": float(np.ravel(found["error"])[0]), "share": share}


# ---------------------------------------------------------------- the heavy route: rstanarm
FAMILIES = {"numbers": "stats::gaussian()", "yes or no": "stats::binomial()", "counts": "stats::poisson()"}
RATIO_OUTCOMES = {"yes or no": "odds ratio", "counts": "rate ratio"}


def _stan_fit(model, seed, prior_only=False):
    """R code that fits the model with rstanarm (stan_glm, or stan_glmer with grouped_by=), and the values."""
    from .models_r import r_data, r_terms

    safe = {}
    values, code = r_data(model, safe)
    rhs = r_terms(model, safe) or "1"
    family = FAMILIES[model["outcome"]]
    common = (f"data = d, family = {family}, chains = {CHAINS}L, iter = {ITERATIONS}L, seed = seed, refresh = 0, "
              f"cores = 1L{', prior_PD = TRUE' if prior_only else ''}")
    if model.get("groups") is not None:
        code += f"m <- rstanarm::stan_glmer(y ~ {rhs} + (1 | g), {common}); fixed <- names(rstanarm::fixef(m)); "
    else:
        code += f"m <- rstanarm::stan_glm(y ~ {rhs}, {common}); fixed <- names(stats::coef(m)); "
    values["seed"] = int(seed)
    return code, values


_DIAGNOSTICS = ("s <- posterior::summarise_draws(posterior::as_draws_array(as.array(m)), 'rhat', 'ess_bulk', "
                "'ess_tail'); ")


def _rstan_notes(note):
    """rstan's own warnings about R-hat and ESS are said again by simplydata, with what to do; others pass on."""
    words = note.lower()
    if "effective samples size" in words or "r-hat" in words or "rhat" in words or "divergent" in words \
            or "treedepth" in words or "maximum tree depth" in words or "pairs()" in words:
        return ""
    return note


def stan_model(model, seed):
    """The Bayesian model of explain(..., bayesian=True), from R rstanarm: estimates and intervals of each model column
    (ratios for yes/no and counts), sigma, the group spreads, R-hat and effective sizes of every parameter,
    divergences, the prior in rstanarm's own words."""
    from .._r import r_call

    code, values = _stan_fit(model, seed)
    ratio = model["outcome"] in RATIO_OUTCOMES
    est = "exp(est)" if ratio else "est"
    ci = "exp(ci)" if ratio else "ci"
    code += ("est <- if (!is.null(m$glmod)) rstanarm::fixef(m) else stats::coef(m); "
             "ci <- rstanarm::posterior_interval(m, prob = 0.95, pars = fixed); " + _DIAGNOSTICS
             + f"out <- list(names = fixed, est = unname({est}), low = unname({ci}[, 1]), high = unname({ci}[, 2]), "
             "par = s$variable, rhat = s$rhat, ess_bulk = s$ess_bulk, ess_tail = s$ess_tail, "
             "divergent = rstan::get_num_divergent(m$stanfit), treedepth = rstan::get_num_max_treedepth(m$stanfit), "
             "draws = rstanarm::nsamples(m), rows = stats::nobs(m), "
             "prior = utils::capture.output(print(rstanarm::prior_summary(m)))); "
             "if (stats::family(m)$family == 'gaussian') { out$sigma <- unname(stats::sigma(m)); "
             "out$sigma_ci <- unname(rstanarm::posterior_interval(m, prob = 0.95, pars = 'sigma')[1, ]) }; "
             "if (!is.null(m$glmod)) { vc <- as.data.frame(rstanarm::VarCorr(m)); out$group_sd <- vc$sdcor[vc$grp == 'g'] }; "
             "out")
    what = ("The Bayesian mixed model (R rstanarm::stan_glmer())" if model.get("groups") is not None
            else "The Bayesian model (R rstanarm::stan_glm())")
    found = r_call(code, packages=HEAVY_PACKAGES, what=what, python_note=HEAVY_NOTE, source="rstanarm",
                   note_words=_rstan_notes, **values)
    return _read_fit(found)


def _read_fit(found):
    out = {"names": [str(n) for n in np.atleast_1d(found["names"])],
           "par": [str(n) for n in np.atleast_1d(found["par"])],
           "draws": int(np.ravel(found["draws"])[0]), "rows": int(np.ravel(found["rows"])[0]),
           "divergent": int(np.ravel(found["divergent"])[0]), "treedepth": int(np.ravel(found["treedepth"])[0]),
           "prior": [str(line) for line in np.atleast_1d(found["prior"])]}
    for key in ("est", "low", "high", "rhat", "ess_bulk", "ess_tail"):
        out[key] = np.asarray(found[key], dtype=float).ravel()
    if found.get("sigma") is not None:
        out["sigma"] = float(np.ravel(found["sigma"])[0])
        out["sigma_ci"] = _three(found["sigma_ci"])
    if found.get("group_sd") is not None:
        out["group_sd"] = float(np.ravel(found["group_sd"])[0])
    return out


def predictive_check(model, seed, prior_only=False):
    """The values for the posterior (or, with prior_only=True, the prior) predictive picture: the model fitted by
    rstanarm (prior_PD = TRUE for the prior), PREDICTED_DRAWS sets of made-up values (posterior_predict(draws =,
    seed =)), and for number outcomes the density of the observed values and of each made-up set on one grid (R
    stats::density(), the bandwidth rule bw.nrd0 that bayesplot's ppc_dens_overlay uses through ggplot2); for yes/no
    and counts, the count of each value in the data and the median and 90 % interval of its count in the made-up sets
    (as bayesplot::ppc_bars, prob = 0.9). Also R-hat, effective sizes and divergences, and the prior."""
    from .._r import r_call

    code, values = _stan_fit(model, seed, prior_only=prior_only)
    code += (f"yrep <- rstanarm::posterior_predict(m, draws = {PREDICTED_DRAWS}L, seed = seed); " + _DIAGNOSTICS
             + "out <- list(par = s$variable, rhat = s$rhat, ess_bulk = s$ess_bulk, ess_tail = s$ess_tail, "
             "divergent = rstan::get_num_divergent(m$stanfit), treedepth = rstan::get_num_max_treedepth(m$stanfit), "
             "draws = rstanarm::nsamples(m), rows = stats::nobs(m), names = fixed, est = numeric(0), low = numeric(0), "
             "high = numeric(0), prior = utils::capture.output(print(rstanarm::prior_summary(m)))); "
             "if (stats::family(m)$family == 'gaussian') { "
             "r <- range(c(d$y, yrep)); dy <- stats::density(d$y, from = r[1], to = r[2], n = 256L); "
             "out$grid <- dy$x; out$observed <- dy$y; "
             "out$made <- t(apply(yrep, 1, function(v) stats::density(v, from = r[1], to = r[2], n = 256L)$y)) "
             "} else { lv <- sort(unique(c(d$y, as.vector(yrep)))); "
             "out$grid <- lv; out$observed <- as.vector(table(factor(d$y, levels = lv))); "
             "k <- t(apply(yrep, 1, function(v) as.vector(table(factor(v, levels = lv))))); "
             "if (length(lv) == 1L) k <- t(k); "
             "out$made <- t(apply(k, 2, stats::quantile, probs = c(0.05, 0.5, 0.95), names = FALSE)) }; "
             "out")
    what = "The prior predictive check (R rstanarm, prior_PD = TRUE)" if prior_only else \
        "The posterior predictive check (R rstanarm::posterior_predict())"
    found = r_call(code, packages=HEAVY_PACKAGES, what=what, python_note=HEAVY_NOTE, source="rstanarm",
                   note_words=_rstan_notes, **values)
    out = _read_fit(found)
    out["grid"] = np.asarray(found["grid"], dtype=float).ravel()
    out["observed"] = np.asarray(found["observed"], dtype=float).ravel()
    made = np.asarray(found["made"], dtype=float)
    out["made"] = made.reshape(-1, len(out["grid"])) if model["outcome"] == "numbers" else made.reshape(len(out["grid"]), 3)
    return out


def need_heavy(what="A Bayesian model"):
    """Raise RMissing with the install line unless rstanarm, rstan and posterior are installed."""
    from .._r import need_r

    need_r(HEAVY_PACKAGES, f"{what} (R rstanarm)", HEAVY_NOTE)


def width_value(width):
    """prior_width= as R BayesFactor takes it: "medium", "wide", "ultrawide" or a number above 0."""
    if isinstance(width, str):
        key = width.strip().lower().replace("ultra wide", "ultrawide").replace("ultra-wide", "ultrawide")
        if key in ("medium", "wide", "ultrawide"):
            return key
    elif isinstance(width, (int, float, np.integer, np.floating)) and not isinstance(width, bool) and width > 0 \
            and np.isfinite(width):
        return float(width)
    raise SimplydataError(f'prior_width= takes "medium" (the default), "wide", "ultrawide" (BayesFactor\'s names) or '
                          f"a number above 0, such as prior_width=0.5; it got {width!r}.")
