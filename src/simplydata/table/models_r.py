"""The R calls behind the model words that no Python package gives with R's numbers.

Each function here hands the rows of a model that explain() has already checked (the dict made
by ModelWords._fit_model) to R and gives back R's own numbers:

* emmeans_table: adjusted averages and their pairwise differences, R emmeans::emmeans() and
  pairs() (Tukey's adjustment), for model_averages_of.
* satterthwaite: a linear mixed model with Satterthwaite t-tests, R lmerTest::lmer() with
  summary(), contest() and its intervals, for explain(..., p_value_by="satterthwaite").
* mixed_r: lme4::lmer() or glmer() with own slopes, (1 + x | g), for own_slope_for= when
  statsmodels does not give lme4's answer (yes/no and counts).
* geeglm: R geepack::geeglm() itself, for effects="for the whole population" when the
  correlation within groups is "in time order" (statsmodels' AR-1 estimator differs from
  geepack's).
* repeated_anova: R afex::aov_ez(), for compare_averages(..., matched_by=).

Nothing is calculated here: the functions write the R call, pass the values and read the result.
"""

from __future__ import annotations

import numpy as np

FAMILIES = {"lm": None, "binomial": "binomial", "poisson": "poisson", "mixed": None, "glmm": None}


def r_data(model, names=None):
    """The model's rows for R: the values (as R variables) and the R code that makes the data frame d.

    Number columns stay numbers; group columns become factors with the groups in simplydata's
    order (the first is the baseline, as in explain()). Columns get safe names v0, v1, ...;
    the outcome is y and the groups of grouped_by= are g. names= gives back the safe name of
    each column."""
    variables = model["variables"]
    safe = {v: f"v{i}" for i, v in enumerate(variables)}
    values = {"y": np.asarray(model["y"], dtype=float)}
    parts = ["y = y"]
    for v in variables:
        key = safe[v]
        if model["kinds"][v] == "group":
            values[key] = np.array([str(x) for x in model["data"][v]], dtype=object)
            values[key + "_levels"] = np.array([str(x) for x in model["levels"][v]], dtype=object)
            parts.append(f"{key} = factor({key}, levels = {key}_levels)")
        else:
            values[key] = np.asarray(model["data"][v], dtype=float)
            parts.append(f"{key} = {key}")
    if model.get("groups") is not None:
        values["g"] = np.asarray(model["groups"], dtype=object)
        parts.append("g = factor(g)")
    code = f"d <- data.frame({', '.join(parts)}); "
    if names is not None:
        names.update(safe)
    return values, code


def r_terms(model, safe):
    """The right-hand side of the R formula, term by term as explain() reads using=."""
    return " + ".join(":".join(safe[v] for v in term) for term in model["terms"])


def r_fit(model, safe, slopes=()):
    """R code that fits the same model as m: lm(), glm(), lme4::lmer() or lme4::glmer()."""
    rhs = r_terms(model, safe)
    kind = model["kind"]
    family = "binomial" if model["outcome"] == "yes or no" else "poisson"
    if kind in ("mixed", "glmm"):
        random = "(1 | g)" if not slopes else f"(1 + {' + '.join(safe[s] for s in slopes)} | g)"
        if kind == "mixed":
            return f"m <- lme4::lmer(y ~ {rhs} + {random}, data = d, REML = TRUE); "
        return f"m <- lme4::glmer(y ~ {rhs} + {random}, data = d, family = {family}); "
    if kind == "lm":
        return f"m <- stats::lm(y ~ {rhs}, data = d); "
    return f"m <- stats::glm(y ~ {rhs}, data = d, family = {family}); "


def emmeans_table(model, for_each):
    """R emmeans::emmeans(m, specs = for_each, type = "response") and pairs(..., adjust = "tukey")
    with summary(infer = c(TRUE, TRUE)): one dict for the averages, one for the pairs."""
    from .._r import r_call

    safe = {}
    values, code = r_data(model, safe)
    packages = ("emmeans", "lme4") if model["kind"] in ("mixed", "glmm") else ("emmeans",)
    if model["kind"] == "mixed":
        packages += ("pbkrtest",)
    code += r_fit(model, safe)
    code += (f"e <- emmeans::emmeans(m, specs = '{safe[for_each]}', type = 'response'); "
             "a <- as.data.frame(summary(e)); "
             "p <- as.data.frame(summary(graphics::pairs(e, adjust = 'tukey'), infer = c(TRUE, TRUE))); "
             "low <- function(t) t[[grep('LCL|lower', names(t))[1]]]; "
             "high <- function(t) t[[grep('UCL|upper', names(t))[1]]]; "
             "stat <- function(t) t[[grep('^(t|z)[.]ratio$', names(t))[1]]]; "
             "list(level = as.character(a[[1]]), average = a[[2]], se = a$SE, df = a$df, low = low(a), high = high(a), "
             "contrast = as.character(p$contrast), difference = p[[2]], pse = p$SE, pdf = p$df, plow = low(p), "
             "phigh = high(p), stat = stat(p), p = p$p.value)")
    out = r_call(code, packages=packages, source="emmeans",
                 what="Model averages and their pairs (R emmeans::emmeans() and pairs())",
                 python_note="no Python package gives emmeans' averages over a reference grid; "
                             "explain() gives each group's difference from the first group without R", **values)
    return {key: (np.atleast_1d(value) if value is not None else value) for key, value in out.items()}


def lmer_r(model, slopes=(), satterthwaite=False, tested=()):
    """A linear mixed model fitted by R itself on explain()'s model matrix X: lme4::lmer(REML = TRUE)
    with (1 | g) or own slopes (1 + x | g), slopes= being the columns of X that get them; with
    satterthwaite=True through R lmerTest::lmer(), whose summary() gives Satterthwaite t-tests, contest(confint = TRUE) their intervals, and contest(joint = TRUE) the
    F test for each whole group column in tested (term index, its model columns)."""
    from .._r import r_call

    X = np.asarray(model["X"], dtype=float)
    k = X.shape[1]
    values = {"y": np.asarray(model["y"], dtype=float), "X": X, "g": np.asarray(model["groups"], dtype=object)}
    random = "(1 | g)"
    if slopes:
        values["Z"] = X[:, list(slopes)]
        random = "(1 + Z | g)"
    fit = "lmerTest::lmer" if satterthwaite else "lme4::lmer"
    code = f"g <- factor(g); m <- {fit}(y ~ 0 + X + {random}, REML = TRUE); "
    code += ("vc <- as.data.frame(lme4::VarCorr(m)); "
             "out <- list(beta = unname(lme4::fixef(m)), cov = unname(as.matrix(stats::vcov(m))), "
             "fitted = unname(stats::fitted(m)), is_cor = !is.na(vc$var2), vcov = vc$vcov, sdcor = vc$sdcor, "
             "loglik = as.numeric(stats::logLik(m)), singular = lme4::isSingular(m), "
             "trouble = length(m@optinfo$conv$lme4$messages) > 0); ")
    if satterthwaite:
        code += ("ci <- t(sapply(seq_len(ncol(L)), function(i) unlist(lmerTest::contest(m, L[i, ], confint = TRUE, "
                 "joint = FALSE)[c('df', 'lower', 'upper', 'Pr(>|t|)')]))); "
                 "out$df <- unname(ci[, 1]); out$low <- unname(ci[, 2]); out$high <- unname(ci[, 3]); "
                 "out$p <- unname(ci[, 4]); "
                 "out$f <- numeric(0); out$numdf <- numeric(0); out$dendf <- numeric(0); out$fp <- numeric(0); "
                 "for (t in unique(tested_term)) { cols <- tested_col[tested_term == t]; "
                 "a <- lmerTest::contest(m, L[cols, , drop = FALSE], joint = TRUE); "
                 "out$f <- c(out$f, a[['F value']]); out$numdf <- c(out$numdf, a$NumDF); "
                 "out$dendf <- c(out$dendf, a$DenDF); out$fp <- c(out$fp, a[['Pr(>F)']]) }; ")
        values["L"] = np.eye(k)
        pairs = [(t, c + 1) for t, cols in tested for c in cols]
        values["tested_term"] = np.array([float(t) for t, _ in pairs] or [-1.0])
        values["tested_col"] = np.array([float(c) for _, c in pairs] or [1.0])
        if not pairs:
            code = code.replace("for (t in unique(tested_term))", "for (t in integer(0))")
    code += "out"
    packages = ("lme4", "lmerTest") if satterthwaite else ("lme4",)
    what = ("Satterthwaite p-values for a mixed model (R lmerTest)" if satterthwaite else
            "A mixed model with its own slope for each group (R lme4::lmer())")
    note = ("explain() without p_value_by= gives Wald z-tests from statsmodels without R" if satterthwaite else
            "statsmodels MixedLM(re_formula=) fits own slopes too, but does not reliably reach lme4's answer")
    out = r_call(code, packages=packages, source="lmerTest" if satterthwaite else "lme4", what=what,
                 python_note=note, **values)
    return out


def geeglm_r(model, corstr):
    """R geepack::geeglm() itself (the rows in each group in table order), for the working
    correlation "ar1"; gives back the effects, their robust (sandwich) covariance, the correlation
    and the scale."""
    from .._r import r_call

    values = {"y": np.asarray(model["y"], dtype=float), "X": np.asarray(model["X"], dtype=float),
              "g": np.asarray(model["groups"], dtype=object)}
    family = {"numbers": "gaussian", "yes or no": "binomial", "counts": "poisson"}[model["outcome"]]
    # geeglm needs the rows of each group together; order() keeps each group's rows in table order
    code = ("g <- factor(g, levels = unique(g)); o <- order(g); d <- data.frame(y = y[o], g = g[o]); "
            "d$X <- X[o, , drop = FALSE]; "
            f"m <- geepack::geeglm(y ~ 0 + X, id = g, data = d, family = {family}, corstr = '{corstr}'); "
            "fitted <- numeric(length(o)); fitted[o] <- stats::fitted(m); "
            "list(beta = unname(stats::coef(m)), cov = unname(as.matrix(stats::vcov(m))), fitted = fitted, "
            "alpha = unname(unlist(m$geese$alpha)), scale = unname(unlist(m$geese$gamma)))")
    return r_call(code, packages=("geepack",), source="geepack::geeglm",
                  what='Effects for the whole population with correlation "in time order" (R geepack::geeglm())',
                  python_note='within_groups="alike" or "independent" works without R (statsmodels GEE)', **values)


def repeated_anova(y, ids, within, between):
    """R afex::aov_ez() itself: a repeated-measures (or mixed) ANOVA with the Greenhouse-Geisser
    correction and generalised eta-squared, anova(correction = "GG", es = "ges"); Mauchly's test and
    the GG epsilons from summary(). within= and between= map safe names to their values."""
    from .._r import r_call

    values = {"y": np.asarray(y, dtype=float), "id": np.asarray(ids, dtype=object)}
    parts = ["y = y", "id = id"]
    for name, data in {**within, **between}.items():
        values[name] = np.asarray(data, dtype=object)
        parts.append(f"{name} = {name}")
    w = ", ".join(f"'{n}'" for n in within)
    b = ", ".join(f"'{n}'" for n in between)
    code = (f"d <- data.frame({', '.join(parts)}, stringsAsFactors = TRUE); "
            f"a <- afex::aov_ez(id = 'id', dv = 'y', data = d, within = c({w})"
            + (f", between = c({b})" if between else "") + "); "
            "t <- anova(a, correction = 'GG', es = 'ges'); "
            "s <- suppressWarnings(summary(a)); sph <- s$sphericity.tests; adj <- s$pval.adjustments; "
            "list(term = rownames(t), numdf = t[['num Df']], dendf = t[['den Df']], f = t$F, ges = t$ges, "
            "p = t[['Pr(>F)']], sph_term = if (length(sph)) rownames(sph) else character(0), "
            "sph_w = if (length(sph)) unname(sph[, 1]) else numeric(0), "
            "sph_p = if (length(sph)) unname(sph[, 2]) else numeric(0), "
            "gg_term = if (length(adj)) rownames(adj) else character(0), "
            "gg = if (length(adj)) unname(adj[, 'GG eps']) else numeric(0), subjects = nrow(a$data$wide))")
    out = r_call(code, packages=("afex",), source="afex::aov_ez",
                 what="A repeated-measures ANOVA (R afex::aov_ez())",
                 python_note="statsmodels AnovaRM has no Greenhouse-Geisser correction and no between-subject "
                             "columns", **values)
    return out
