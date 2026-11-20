"""The R calls behind the checking and comparing words of phase S3a-3.

Each function hands numbers that the word has already checked to an R package and gives back R's
own numbers. Nothing is calculated here: the functions write the R call, pass the values and read
the result. The packages are checked with need_r() but never attached (every call names its package,
nlme::gls), so no package can hide a function of another (the lesson of S3a-2: drc's gaussian()).

* gls: nlme::gls() with varIdent() / varPower() and corAR1() / corCAR1(), next to the plain gls() and
  anova(), for explain(spread_changes_with=, neighbours_alike_in_order_of=).
* lasso: glmnet::cv.glmnet() with the penalty lambda.1se, for find_columns_that_predict.
* left_out_rows: boot::cv.glm(K = 10) of each model, for compare_models(check_on_left_out_rows=True).
* hosmer: performance::performance_hosmer(n_bins = 10), for check_model_of(outcome="yes or no").
* model_contrasts: emmeans::emmeans() with contrast(), joint_tests() and at=, for
  find_model_averages_of(comparing=, within_each_group_in=, over_range_of=).
* group_levels: lme4::ranef(condVar = TRUE) and coef(), for find_group_levels_of.
* nested_anova: stats::aov(y ~ group + Error(unit)) and the lme4 variances, for
  compare_averages_of(grouped_by=).
"""

from __future__ import annotations

import numpy as np

from .models_r import FIT_PACKAGES, r_data, r_fit


def _call(code, packages, **options):
    """r_call with the packages checked (need_r) but not attached: every call here names its package."""
    from .._r import need_r, r_call

    need_r(packages, options.get("what", "This"), options.get("python_note"))
    return r_call(code, **options)


def _flat(out):
    return {k: (np.atleast_1d(v) if v is not None and not isinstance(v, dict) else v) for k, v in out.items()}


# ---------------------------------------------------------------- explain(spread_changes_with=, neighbours_...)
def gls(model, spread=None, spread_kind=None, order=None, order_kind=None):
    """R nlme::gls(method = "REML") with the variance and correlation structures, and the plain gls() on the same
    rows, compared by anova(m0, m) (the same effects, so the REML fits can be compared).

    spread: the values of spread_changes_with= (spread_kind "group": varIdent(form = ~ 1 | s); "number":
    varPower(form = ~ s)). order: the values of neighbours_alike_in_order_of= (order_kind "even": whole steps,
    corAR1(form = ~ t); "uneven": corCAR1(form = ~ t))."""
    safe = {}
    values, code = r_data(model, safe)
    rhs = " + ".join(":".join(safe[v] for v in term) for term in model["terms"])
    extra = []
    if spread is not None:
        if spread_kind == "group":
            values["s"] = np.array([str(v) for v in spread], dtype=object)
            values["s_levels"] = np.array(sorted(set(values["s"].tolist())), dtype=object)
            code += "d$s <- factor(s, levels = s_levels); "
            extra.append("weights = nlme::varIdent(form = ~ 1 | s)")
        else:
            values["s"] = np.asarray(spread, dtype=float)
            code += "d$s <- s; "
            extra.append("weights = nlme::varPower(form = ~ s)")
    if order is not None:
        values["t"] = np.asarray(order, dtype=float)
        code += "d$t <- t; "
        extra.append("correlation = nlme::" + ("corAR1" if order_kind == "even" else "corCAR1") + "(form = ~ t)")
    code += (f"m0 <- nlme::gls(y ~ {rhs}, data = d, method = 'REML'); "
             f"m <- nlme::gls(y ~ {rhs}, data = d, method = 'REML', {', '.join(extra)}); "
             "tt <- summary(m)$tTable; "
             "ci <- tryCatch(nlme::intervals(m, which = 'coef')$coef, error = function(e) NULL); "
             "vc <- tryCatch(nlme::intervals(m, which = 'var-cov'), error = function(e) NULL); "
             "a <- stats::anova(m0, m); "
             "out <- list(beta = unname(tt[, 1]), se = unname(tt[, 2]), t = unname(tt[, 3]), p = unname(tt[, 4]), "
             "low = if (is.null(ci)) rep(NA_real_, nrow(tt)) else unname(ci[, 1]), "
             "high = if (is.null(ci)) rep(NA_real_, nrow(tt)) else unname(ci[, 3]), "
             "df = m$dims$N - m$dims$p, sigma = m$sigma, aic = stats::AIC(m), aic0 = stats::AIC(m0), "
             "bic = stats::BIC(m), loglik = as.numeric(stats::logLik(m)), "
             "lr = a$L.Ratio[2], lr_df = a$df[2] - a$df[1], lr_p = a$`p-value`[2], "
             "fitted = unname(stats::fitted(m)), n = m$dims$N); ")
    if spread is not None:
        code += ("v <- stats::coef(m$modelStruct$varStruct, unconstrained = FALSE, allCoef = TRUE); "
                 "out$spread_names <- names(v); out$spread <- unname(v); "
                 "vi <- if (is.null(vc) || is.null(vc$varStruct)) NULL else vc$varStruct; "
                 "out$spread_ci_names <- if (is.null(vi)) character(0) else rownames(vi); "
                 "out$spread_low <- if (is.null(vi)) numeric(0) else unname(vi[, 1]); "
                 "out$spread_high <- if (is.null(vi)) numeric(0) else unname(vi[, 3]); ")
    if order is not None:
        code += ("out$phi <- unname(stats::coef(m$modelStruct$corStruct, unconstrained = FALSE)); "
                 "ci2 <- if (is.null(vc) || is.null(vc$corStruct)) NULL else vc$corStruct; "
                 "out$phi_low <- if (is.null(ci2)) NA_real_ else unname(ci2[1, 1]); "
                 "out$phi_high <- if (is.null(ci2)) NA_real_ else unname(ci2[1, 3]); ")
    code += "out"
    return _flat(_call(code, ("nlme",), source="nlme::gls",
                       what="A model whose spread changes or whose neighbouring rows are alike (R nlme::gls())",
                       python_note="statsmodels has GLSAR (iterated, not likelihood) and no variance functions, so "
                                   "the model comes from R nlme", **values))


# ---------------------------------------------------------------- find_columns_that_predict
def lasso(X, y, family, alpha, seed):
    """R glmnet::cv.glmnet(x, y, family =, alpha =, nfolds = 10) after set.seed(seed); the effects at
    lambda.1se and lambda.min (coef()), and the cross-validated error at each (cvm, cvsd)."""
    values = {"x": np.asarray(X, dtype=float), "y": np.asarray(y, dtype=float), "a": float(alpha),
              "seed": float(seed), "fam": family}
    code = ("set.seed(seed); "
            "f <- glmnet::cv.glmnet(x, y, family = fam, alpha = a, nfolds = 10); "
            "b1 <- as.numeric(stats::coef(f, s = 'lambda.1se')); bm <- as.numeric(stats::coef(f, s = 'lambda.min')); "
            "i1 <- which(f$lambda == f$lambda.1se); im <- which(f$lambda == f$lambda.min); "
            "list(beta = b1, beta_min = bm, lambda = f$lambda.1se, lambda_min = f$lambda.min, "
            "cvm = f$cvm[i1], cvsd = f$cvsd[i1], cvm_min = f$cvm[im], measure = unname(f$name), "
            "kept = sum(b1[-1] != 0), lambdas = length(f$lambda), "
            "version = as.character(utils::packageVersion('glmnet')))")
    return _flat(_call(code, ("glmnet",), source="glmnet::cv.glmnet",
                       what="Choosing columns with the lasso (R glmnet::cv.glmnet())",
                       python_note="Python has no cross-validated lasso for these models outside scikit-learn, which "
                                   "simplydata leaves out", **values))


# ---------------------------------------------------------------- compare_models(check_on_left_out_rows=True)
def left_out_rows(models, seed, parts=10):
    """R boot::cv.glm(d, m, K = parts) of each model after the same set.seed(seed), so every model is checked on the
    same split: delta[1] (the error on the left-out rows) and delta[2] (adjusted), with the error on the rows the
    model was fitted to (the same cost, mean((y - fitted)^2))."""
    first = models[0]
    values = {"y": np.asarray(first["y"], dtype=float), "seed": float(seed), "K": float(parts)}
    family = {"numbers": "stats::gaussian", "yes or no": "stats::binomial", "counts": "stats::poisson"}[first["outcome"]]
    code = "d <- data.frame(y = y); "
    for i, model in enumerate(models):
        values[f"X{i}"] = np.asarray(model["X"][:, 1:], dtype=float)
    code += "out <- list(delta1 = numeric(0), delta2 = numeric(0), inside = numeric(0)); "
    for i, model in enumerate(models):
        has = model["X"].shape[1] > 1
        rhs = f"X{i}" if has else "1"
        code += (f"d$X{i} <- X{i}; " if has else "")
        code += (f"m <- stats::glm(y ~ {rhs}, data = d, family = {family}); set.seed(seed); "
                 "cv <- boot::cv.glm(d, m, K = K); "
                 "out$delta1 <- c(out$delta1, cv$delta[1]); out$delta2 <- c(out$delta2, cv$delta[2]); "
                 "out$inside <- c(out$inside, mean((y - stats::fitted(m))^2)); ")
    code += "out$version <- as.character(utils::packageVersion('boot')); out"
    return _flat(_call(code, ("boot",), source="boot::cv.glm",
                       what="Checking a model on rows it did not see (R boot::cv.glm())",
                       python_note="statsmodels has no k-fold cross-validation; R boot gives it with R's own random "
                                   "split", **values))


# ---------------------------------------------------------------- check_model_of(outcome="yes or no")
def hosmer(X, y, bins=10):
    """R performance::performance_hosmer(m, n_bins = bins) of the logistic model glm(y ~ 0 + X, binomial):
    chi-square, df and p-value."""
    values = {"X": np.asarray(X, dtype=float), "y": np.asarray(y, dtype=float), "bins": float(bins)}
    code = ("m <- stats::glm(y ~ 0 + X, family = stats::binomial); "
            "h <- performance::performance_hosmer(m, n_bins = bins); "
            "list(chisq = unname(h$chisq), df = unname(h$df), p = unname(h$p.value))")
    return _flat(_call(code, ("performance",), source="performance::performance_hosmer",
                       what="The Hosmer-Lemeshow test (R performance::performance_hosmer())",
                       python_note="no Python package gives the Hosmer-Lemeshow test; the calibration picture and "
                                   "the Brier score need no R", **values))


# ---------------------------------------------------------------- find_model_averages_of(comparing=, ...)
EMMEANS_METHODS = {"each pair": "pairwise", "each with the first": "trt.vs.ctrl", "each with the next": "consec",
                   "each with the average": "eff", "trend": "poly"}


def model_contrasts(model, for_each, levels, method=None, weights=None, by=None, at=None):
    """R emmeans on the model explain() fits (r_fit). levels: the groups of for_each in the order wanted (the
    factor is made with them, so "each with the first" compares with levels[0]).

    method: an emmeans method name (EMMEANS_METHODS), or None with weights= {name: [w, ...]} (contrast(method =
    list(...)); Helmert and own weights). by: the column of within_each_group_in= (emmeans(m, ~ v | b), and
    joint_tests(m) and joint_tests(m, by = "b")). at: (column, values) of over_range_of= (emmeans(m, ~ x, at =
    list(x = values)), with ~ x | v when for_each is given)."""
    safe = {}
    values, code = r_data(model, safe)
    packages = ("emmeans",) + FIT_PACKAGES.get(model["kind"], ())
    if model["kind"] == "mixed":
        packages += ("pbkrtest",)
    if for_each is not None and levels is not None:
        v = safe[for_each]
        values["wanted"] = np.array([str(x) for x in levels], dtype=object)
        code += f"d${v} <- factor(as.character(d${v}), levels = wanted); "
    code += r_fit(model, safe).replace("family = binomial", "family = stats::binomial").replace(
        "family = poisson", "family = stats::poisson")
    scale = "" if model["outcome"] == "numbers" else ", type = 'response'"
    helpers = ("low <- function(t) t[[grep('LCL|lower', names(t))[1]]]; "
               "high <- function(t) t[[grep('UCL|upper', names(t))[1]]]; "
               "stat <- function(t) { i <- grep('^(t|z)[.]ratio$', names(t)); if (length(i)) t[[i[1]]] else "
               "rep(NA_real_, nrow(t)) }; "
               "value <- function(t, skip) t[[setdiff(names(t), skip)[1]]]; "
               "adj <- function(s) { m <- grep('^P value adjustment', attr(s, 'mesg'), value = TRUE); "
               "if (length(m)) sub('[.]$', '', sub('^P value adjustment: ', '', m[1])) else 'none' }; "
               "dfm <- function(s) { m <- grep('^Degrees-of-freedom method', attr(s, 'mesg'), value = TRUE); "
               "if (length(m)) sub('^Degrees-of-freedom method: ', '', m[1]) else '' }; ")
    code += helpers
    if at is not None:
        name, grid = at
        x = safe[name]
        values["grid"] = np.asarray(grid, dtype=float)
        spec = f"~ {x}" if for_each is None else f"~ {x} | {safe[for_each]}"
        skip = f"'{x}'" if for_each is None else f"'{x}', '{safe[for_each]}'"
        group = "character(0)" if for_each is None else f"as.character(a${safe[for_each]})"
        code += (f"e <- emmeans::emmeans(m, specs = {spec}, at = list({x} = grid){scale}); s <- summary(e); "
                 "a <- as.data.frame(s); "
                 f"list(x = a${x}, group = {group}, average = value(a, c({skip})), se = a$SE, df = a$df, "
                 "low = low(a), high = high(a), df_method = dfm(s))")
        return _flat(_call(code, packages, source="emmeans",
                           what="Model averages across a range (R emmeans::emmeans(at =))",
                           python_note="no Python package gives emmeans' averages over a reference grid", **values))
    v = safe[for_each]
    spec = f"~ {v}" if by is None else f"~ {v} | {safe[by]}"
    code += f"e <- emmeans::emmeans(m, specs = {spec}{scale}); se <- summary(e); a <- as.data.frame(se); "
    if method is not None:
        code += f"cn <- emmeans::contrast(e, method = '{method}'); "
    else:
        names = list(weights)
        values["wnames"] = np.array(names, dtype=object)
        values["wmatrix"] = np.array([[float(w) for w in weights[n]] for n in names], dtype=float)
        code += ("wl <- lapply(seq_len(nrow(wmatrix)), function(i) wmatrix[i, ]); names(wl) <- wnames; "
                 "cn <- emmeans::contrast(e, method = wl); ")
    code += ("sc <- summary(cn, infer = c(TRUE, TRUE)); p <- as.data.frame(sc); "
             f"out <- list(level = as.character(a${v}), average = value(a, c('{v}'"
             + (f", '{safe[by]}'" if by is not None else "") + ")), se = a$SE, df = a$df, low = low(a), high = high(a), "
             "contrast = as.character(p$contrast), difference = value(p, c('contrast'"
             + (f", '{safe[by]}'" if by is not None else "") + ")), pse = p$SE, pdf = p$df, plow = low(p), "
             "phigh = high(p), stat = stat(p), p = p$p.value, adjust = adj(sc), df_method = dfm(se), "
             "ratio = any(grepl(' / ', p$contrast)) || 'ratio' %in% names(p) || 'odds.ratio' %in% names(p)); ")
    if by is not None:
        b = safe[by]
        code += (f"out$level_by <- as.character(a${b}); out$contrast_by <- as.character(p${b}); "
                 "jt <- as.data.frame(emmeans::joint_tests(m)); "
                 "out$joint_term <- as.character(jt[[1]]); out$joint_f <- jt$F.ratio; out$joint_df1 <- jt$df1; "
                 "out$joint_df2 <- jt$df2; out$joint_p <- jt$p.value; "
                 f"jb <- as.data.frame(emmeans::joint_tests(m, by = '{b}')); "
                 f"jb <- jb[jb[[1]] == '{v}', , drop = FALSE]; "
                 f"out$within_by <- as.character(jb${b}); out$within_f <- jb$F.ratio; out$within_df1 <- jb$df1; "
                 "out$within_df2 <- jb$df2; out$within_p <- jb$p.value; ")
    code += "out"
    out = _call(code, packages, source="emmeans",
                what="Model averages and their comparisons (R emmeans::emmeans() and contrast())",
                python_note="no Python package gives emmeans' averages over a reference grid; explain() gives each "
                            "group's difference from the first group without R", **values)
    found = _flat(out)
    found["safe"] = safe
    return found


# ---------------------------------------------------------------- find_group_levels_of
def group_levels(model, slopes=()):
    """R lme4::lmer() (or glmer()) as explain(grouped_by=) fits it, then ranef(m, condVar = TRUE) (each group's
    own level and slopes, with their conditional standard deviations) and coef(m) (the group's own line)."""
    safe = {}
    values, code = r_data(model, safe)
    code += r_fit(model, safe, slopes).replace("family = binomial", "family = stats::binomial").replace(
        "family = poisson", "family = stats::poisson")
    code += ("r <- lme4::ranef(m, condVar = TRUE)$g; pv <- attr(r, 'postVar'); "
             "sds <- t(sapply(seq_len(dim(pv)[3]), function(i) sqrt(diag(as.matrix(pv[, , i]))))); "
             "if (ncol(r) == 1) sds <- matrix(sds, ncol = 1); "
             "cf <- stats::coef(m)$g; "
             "list(groups = rownames(r), names = colnames(r), level = unname(as.matrix(r)), sd = unname(sds), "
             "own = unname(as.matrix(cf[, colnames(r), drop = FALSE])), "
             "fixed = unname(lme4::fixef(m)[colnames(r)]), singular = lme4::isSingular(m))")
    names = {"(Intercept)": "(Intercept)"}
    names.update({v: k for k, v in safe.items()})
    packages = ("lme4",)
    out = _call(code, packages, source="lme4::ranef", what="Each group's own level (R lme4::ranef())",
                python_note="statsmodels MixedLM gives the levels for random intercepts, but its conditional "
                            "variances differ from lme4's, so the intervals come from R", **values)
    found = _flat(out)
    found["names"] = [names.get(str(n), str(n)) for n in found["names"]]
    k = len(found["names"])
    for key in ("level", "sd", "own"):
        found[key] = np.asarray(found[key], dtype=float).reshape(-1, k) if k > 1 else \
            np.asarray(found[key], dtype=float).reshape(-1, 1)
    return found


# ---------------------------------------------------------------- compare_averages_of(grouped_by=)
def nested_anova(y, group, unit):
    """R stats::aov(y ~ group + Error(unit)) (the group tested against the variation between units), and the
    variances between units and within them from lme4::lmer(y ~ group + (1 | unit)) (REML)."""
    values = {"y": np.asarray(y, dtype=float), "gr": np.array(group, dtype=object), "u": np.array(unit, dtype=object)}
    code = ("d <- data.frame(y = y, gr = factor(gr, levels = unique(gr)), u = factor(u, levels = unique(u))); "
            "a <- summary(stats::aov(y ~ gr + Error(u), data = d)); "
            "top <- a[['Error: u']][[1]]; low <- a[['Error: Within']][[1]]; "
            "m <- lme4::lmer(y ~ gr + (1 | u), data = d, REML = TRUE); vc <- as.data.frame(lme4::VarCorr(m)); "
            "list(f = top[['F value']][1], df1 = top$Df[1], df2 = top$Df[2], p = top[['Pr(>F)']][1], "
            "ss_group = top[['Sum Sq']][1], ss_units = top[['Sum Sq']][2], ms_group = top[['Mean Sq']][1], "
            "ms_units = top[['Mean Sq']][2], df_within = low$Df[nrow(low)], ss_within = low[['Sum Sq']][nrow(low)], "
            "ms_within = low[['Mean Sq']][nrow(low)], var_units = vc$vcov[1], var_within = vc$vcov[2])")
    return _flat(_call(code, ("lme4",), source="stats::aov", what="A nested ANOVA (R aov(y ~ group + Error(unit)))",
                       python_note="statsmodels has no Error() strata", **values))
