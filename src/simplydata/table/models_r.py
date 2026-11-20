"""The R calls behind the model words that no Python package gives with R's numbers.

Each function here hands the rows of a model that explain() has already checked (the dict made
by ModelWords._fit_model) to R and gives back R's own numbers:

* emmeans_table: adjusted averages and their pairwise differences, R emmeans::emmeans() and
  pairs() (Tukey's adjustment), for find_model_averages_of.
* satterthwaite: a linear mixed model with Satterthwaite t-tests, R lmerTest::lmer() with
  summary(), contest() and its intervals, for explain(..., p_value_by="satterthwaite").
* mixed_r: lme4::lmer() or glmer() with own slopes, (1 + x | g), for own_slope_for= when
  statsmodels does not give lme4's answer (yes/no and counts).
* geeglm: R geepack::geeglm() itself, for effects="for the whole population" when the
  correlation within groups is "in time order" (statsmodels' AR-1 estimator differs from
  geepack's).
* repeated_anova: R afex::aov_ez(), for compare_averages_of(..., matched_by=).

Nothing is calculated here: the functions write the R call, pass the values and read the result.
"""

from __future__ import annotations

import numpy as np


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
    if model["kind"] in ("ordered", "multinom"):  # the outcome's groups as a factor, lowest (or baseline) first
        values["y_levels"] = np.array(model["groups_of_outcome"], dtype=object)
        parts = ["y = factor(y_levels[y + 1], levels = y_levels)"]
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
    inner = (model.get("grouping") or {}).get("inner_groups")
    if inner is not None:  # groups inside groups: h, numbered within g by R itself, (1 | g/h)
        values["h"] = np.asarray(inner, dtype=object)
        parts.append("h = factor(h)")
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
        if (model.get("grouping") or {}).get("inner_groups") is not None:
            random = "(1 | g/h)"
        if kind == "mixed":
            return f"m <- lme4::lmer(y ~ {rhs} + {random}, data = d, REML = TRUE); "
        return f"m <- lme4::glmer(y ~ {rhs} + {random}, data = d, family = {family}); "
    other = {"lm": f"stats::lm(y ~ {rhs}, data = d)",
             "quasipoisson": f"stats::glm(y ~ {rhs}, data = d, family = quasipoisson)",
             "negbin": f"MASS::glm.nb(y ~ {rhs}, data = d)",
             "gamma": f"stats::glm(y ~ {rhs}, data = d, family = Gamma(link = 'log'))",
             "shares": f"betareg::betareg(y ~ {rhs}, data = d)",
             "zeros": f"pscl::zeroinfl(y ~ {rhs} | {rhs}, data = d, dist = 'poisson')",
             "ordered": f"MASS::polr(y ~ {rhs}, data = d, Hess = TRUE)",
             "multinom": f"nnet::multinom(y ~ {rhs}, data = d, trace = FALSE)"}
    if kind in other:
        return f"m <- {other[kind]}; "
    return f"m <- stats::glm(y ~ {rhs}, data = d, family = {family}); "


# the R packages each kind of model needs, besides stats
FIT_PACKAGES = {"mixed": ("lme4",), "glmm": ("lme4",), "negbin": ("MASS",), "shares": ("betareg",),
                "zeros": ("pscl",), "ordered": ("MASS",), "multinom": ("nnet",)}


def emmeans_table(model, for_each):
    """R emmeans::emmeans(m, specs = for_each, type = "response") and pairs(..., adjust = "tukey")
    with summary(infer = c(TRUE, TRUE)): one dict for the averages, one for the pairs."""
    from .._r import r_call

    safe = {}
    values, code = r_data(model, safe)
    packages = ("emmeans",) + FIT_PACKAGES.get(model["kind"], ())
    if model["kind"] == "mixed":
        packages += ("pbkrtest",)
    code += r_fit(model, safe)
    v = safe[for_each]
    if model["kind"] in ("ordered", "multinom"):  # the chance of each of the outcome's groups
        code += f"e <- emmeans::emmeans(m, specs = ~ {v} | y, mode = 'prob'); "
    else:
        code += f"e <- emmeans::emmeans(m, specs = '{v}', type = 'response'); "
    code += ("a <- as.data.frame(summary(e)); "
             "p <- as.data.frame(summary(graphics::pairs(e, adjust = 'tukey', parens = NULL), "
             "infer = c(TRUE, TRUE))); "
             "dfm <- sub('^Degrees-of-freedom method: ', '', grep('^Degrees-of-freedom method', "
             "attr(summary(e), 'mesg'), value = TRUE)); "
             "low <- function(t) t[[grep('LCL|lower', names(t))[1]]]; "
             "high <- function(t) t[[grep('UCL|upper', names(t))[1]]]; "
             "stat <- function(t) t[[grep('^(t|z)[.]ratio$', names(t))[1]]]; "
             "value <- function(t, skip) t[[setdiff(names(t), skip)[1]]]; "
             "cls <- function(t) if ('y' %in% names(t)) as.character(t$y) else character(0); "
             f"list(level = as.character(a${v}), average = value(a, c('{v}', 'y')), se = a$SE, df = a$df, "
             "low = low(a), high = high(a), cls = cls(a), "
             "contrast = as.character(p$contrast), difference = value(p, c('contrast', 'y')), pse = p$SE, "
             "pdf = p$df, plow = low(p), phigh = high(p), stat = stat(p), p = p$p.value, pcls = cls(p), "
             "ratio = any(grepl(' / ', p$contrast)), df_method = dfm)")
    out = r_call(code, packages=packages, source="emmeans",
                 what="Model averages and their pairs (R emmeans::emmeans() and pairs())",
                 python_note="no Python package gives emmeans' averages over a reference grid; "
                             "explain() gives each group's difference from the first group without R", **values)
    found = {key: (np.atleast_1d(value) if value is not None else value) for key, value in out.items()}
    # the degrees-of-freedom method emmeans used (Kenward-Roger up to emm_options(pbkrtest.limit = 3000) rows,
    # then Satterthwaite or asymptotic), as R's own summary says; "" when it names none
    method = found.get("df_method")
    found["df_method"] = str(method[0]) if method is not None and len(method) else ""
    return found


def nakagawa_code(k, slopes, fitter, options, left="y", offset="", extra=()):
    """R code giving performance::r2_nakagawa() (conditional, marginal) for a mixed model with own slopes.
    performance needs the slope columns by name to find their variance (Johnson's extension), so the same model
    is fitted once more with the columns of X named x1, x2, ... (X's first column is the intercept)."""
    xs = [f"x{j}" for j in range(1, k)]
    columns = "".join(f"d2${name} <- {name}; " for name in extra)
    formula = f"{left} ~ {' + '.join(xs) or '1'}{offset} + (1 + {' + '.join(f'x{j}' for j in slopes)} | g)"
    return ("tryCatch({ d2 <- as.data.frame(X[, -1, drop = FALSE]); names(d2) <- paste0('x', seq_len(ncol(X) - 1)); "
            f"d2$y <- y; d2$g <- g; {columns}m2 <- suppressWarnings(suppressMessages({fitter}({formula}, data = d2"
            f"{options}))); suppressWarnings(suppressMessages(unname(unlist(performance::r2_nakagawa(m2))))) }}, "
            "error = function(e) c(NA_real_, NA_real_))")


def nakagawa_r(model):
    """R performance::r2_nakagawa() of a random-intercept mixed model, (1 | g) or (1 | g/h), refitted by
    R lme4::lmer(REML = TRUE) on the same rows: (conditional, marginal), NaN where performance gives none."""
    from .._r import r_call

    safe = {}
    values, code = r_data(model, safe)
    # the lmer refit inside tryCatch too: if lme4 refuses the model, there is no R squared, not an error
    code += ("list(r2 = tryCatch({ " + r_fit(model, safe) + "suppressWarnings(suppressMessages(unname(unlist("
             "performance::r2_nakagawa(m))))) }, error = function(e) c(NA_real_, NA_real_)))")
    out = r_call(code, packages=("lme4", "performance"), source="performance::r2_nakagawa",
                 what="R squared for mixed models (R performance::r2_nakagawa())", **values)
    return np.atleast_1d(out["r2"]).astype(float)


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
    crossed = (model.get("grouping") or {}).get("crossed_groups")
    if crossed is not None:  # crossed_with=: a second grouping, crossed with the first, (1 | g) + (1 | c)
        values["c"] = np.asarray(crossed, dtype=object)
        random += " + (1 | c)"
    fit = "lmerTest::lmer" if satterthwaite else "lme4::lmer"
    code = f"g <- factor(g); {'c <- factor(c); ' if crossed is not None else ''}m <- {fit}(y ~ 0 + X + {random}, REML = TRUE); "
    # VarCorr() lists the groupings by their number of groups; g's rows first, then c's, then the residual
    code += ("vc <- as.data.frame(lme4::VarCorr(m)); vc <- rbind(vc[vc$grp == 'g', ], vc[vc$grp == 'c', ], "
             "vc[vc$grp == 'Residual', ]); "
             "out <- list(beta = unname(lme4::fixef(m)), cov = unname(as.matrix(stats::vcov(m))), "
             "fitted = unname(stats::fitted(m)), is_cor = !is.na(vc$var2), vcov = vc$vcov, sdcor = vc$sdcor, "
             "loglik = as.numeric(stats::logLik(m)), values = attr(stats::logLik(m), 'df'), "
             "singular = lme4::isSingular(m), trouble = length(m@optinfo$conv$lme4$messages) > 0); ")
    if slopes and crossed is None:  # R squared with own slopes (Nakagawa, Johnson's extension): R performance itself
        code += "out$nakagawa <- " + nakagawa_code(k, slopes, "lme4::lmer", ", REML = TRUE") + "; "
    elif crossed is not None:  # crossed groups: performance::r2_nakagawa() of this fit
        code += ("out$nakagawa <- tryCatch(suppressWarnings(suppressMessages(unname(unlist("
                 "performance::r2_nakagawa(m))))), error = function(e) c(NA_real_, NA_real_)); "
                 "out$crossed <- vc$vcov[vc$grp == 'c'][1]; ")
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
    if slopes or crossed is not None:
        packages += ("performance",)
    what = ("Satterthwaite p-values for a mixed model (R lmerTest)" if satterthwaite else
            "A mixed model with crossed groups (R lme4::lmer())" if crossed is not None else
            "A mixed model with its own slope for each group (R lme4::lmer())")
    if crossed is not None and not satterthwaite:
        note = "statsmodels MixedLM fits one grouping (or groups inside groups), not two crossed ones"
        out = r_call(code, packages=packages, source="lme4", what=what, python_note=note, **values)
        return out
    note = ("explain() without p_value_by= gives Wald z-tests from statsmodels without R" if satterthwaite else
            "statsmodels MixedLM(re_formula=) fits own slopes too, but does not reliably reach lme4's answer")
    out = r_call(code, packages=packages, source="lmerTest" if satterthwaite else "lme4", what=what,
                 python_note=note, **values)
    return out


def geeglm_r(model, corstr, exposure=None, trials=None, link=None):
    """R geepack::geeglm() itself (the rows in each group in table order), for the working
    correlation "ar1" and for successes out of tries (cbind(yes, tries - yes)); exposure= adds
    offset(log(time)), link= another link for yes or no. Gives back the effects, their robust
    (sandwich) covariance, the correlation and the scale."""
    from .._r import r_call

    values = {"y": np.asarray(model["y"], dtype=float), "X": np.asarray(model["X"], dtype=float),
              "g": np.asarray(model["groups"], dtype=object)}
    family = {"numbers": "stats::gaussian", "yes or no": "stats::binomial", "counts": "stats::poisson"}[model["outcome"]]
    if link:
        family = f"{family}(link = '{link}')"
    left, offset, extra = "y", "", ""
    if trials is not None:
        left, values["n"], extra = "cbind(y, n - y)", np.asarray(trials, dtype=float), "d$n <- n[o]; "
    if exposure is not None:
        offset, values["t"] = " + offset(log(t))", np.asarray(exposure, dtype=float)
        extra += "d$t <- t[o]; "
    # geeglm needs the rows of each group together; order() keeps each group's rows in table order
    code = ("g <- factor(g, levels = unique(g)); o <- order(g); d <- data.frame(y = y[o], g = g[o]); "
            f"d$X <- X[o, , drop = FALSE]; {extra}"
            f"m <- geepack::geeglm({left} ~ 0 + X{offset}, id = g, data = d, family = {family}, "
            f"corstr = '{corstr}'); "
            "fitted <- numeric(length(o)); fitted[o] <- stats::fitted(m); "
            "list(beta = unname(stats::coef(m)), cov = unname(as.matrix(stats::vcov(m))), fitted = fitted, "
            "alpha = unname(unlist(m$geese$alpha)), scale = unname(unlist(m$geese$gamma)))")
    return r_call(code, packages=("geepack",), source="geepack::geeglm",
                  what=('Effects for the whole population with correlation "in time order" (R geepack::geeglm())'
                        if corstr == "ar1" else
                        "Effects for the whole population for successes out of tries (R geepack::geeglm())"),
                  python_note=('within_groups="alike" or "independent" works without R (statsmodels GEE)'
                               if corstr == "ar1" else
                               "statsmodels GEE with weights gives other numbers than geepack's cbind(yes, no)"),
                  **values)


def repeated_anova(y, ids, within, between, note_words=None):
    """R afex::aov_ez() itself: a repeated-measures (or mixed) ANOVA with the Greenhouse-Geisser
    correction and generalised eta-squared, anova(correction = "GG", es = "ges"); Mauchly's test and
    the GG epsilons from summary(). within= and between= map safe names to their values; note_words= puts
    afex's notes back into the user's words (the groups go to R as codes)."""
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
            "gg = if (length(adj)) unname(adj[, 'GG eps']) else numeric(0), subjects = nrow(a$data$wide), "
            # the rows afex analysed (people with a missing group left out, repeated rows averaged): long_y and,
            # per column, long_<name>
            "long_y = a$data$long$y"
            + "".join(f", long_{n} = as.character(a$data$long${n})" for n in {**within, **between}) + ")")
    out = r_call(code, packages=("afex",), source="afex::aov_ez",
                 what="A repeated-measures ANOVA (R afex::aov_ez())",
                 python_note="statsmodels AnovaRM has no Greenhouse-Geisser correction and no between-subject "
                             "columns", note_words=note_words, **values)
    return out


def group_influence(model):
    """R lme4 influence(m, groups = "g") and cooks.distance(): how much the fixed effects move when
    each whole group is left out and the model refitted (lmer or glmer), one value per group."""
    from .._r import r_call

    safe = {}
    values, code = r_data(model, safe)
    code += r_fit(model, safe)
    code += ("inf <- stats::influence(m, groups = 'g'); cd <- stats::cooks.distance(inf); "
             "list(group = as.character(inf$deleted), cooks = unname(as.numeric(cd)))")
    return r_call(code, packages=("lme4",), source="lme4::influence",
                  what="Groups that pull a mixed model (R lme4 influence() and cooks.distance())",
                  python_note="statsmodels gives no influence measures for mixed models; show_rows_that_pull_model() "
                              "without grouped_by= works without R", **values)


def gam_r(model, smooth):
    """R mgcv::gam() itself (method = "REML"), the columns of smooth as s(); the rest of the formula as
    explain() reads using=. Gives back R summary.gam()'s parametric and smooth tables and the fit."""
    from .._r import r_call

    safe = {}
    values, code = r_data(model, safe)
    rhs = " + ".join(f"s({safe[term[0]]})" if len(term) == 1 and term[0] in smooth else ":".join(safe[v] for v in term)
                     for term in model["terms"])
    # stats:: so that an attached package with its own gaussian() (drc) cannot take its place
    family = {"numbers": "stats::gaussian", "yes or no": "stats::binomial", "counts": "stats::poisson"}[model["outcome"]]
    code += (f"m <- mgcv::gam(y ~ {rhs}, data = d, family = {family}, method = 'REML'); s <- summary(m); "
             "list(beta = unname(s$p.table[, 1]), se = unname(s$p.table[, 2]), stat = unname(s$p.table[, 3]), "
             "p = unname(s$p.table[, 4]), edf = unname(s$s.table[, 1]), sstat = unname(s$s.table[, 3]), "
             "sp = unname(s$s.table[, 4]), sname = rownames(s$s.table), rsq = s$r.sq, dev = s$dev.expl, "
             "df_resid = m$df.residual, aic = stats::AIC(m), bic = stats::BIC(m))")
    out = r_call(code, packages=("mgcv",), source="mgcv::gam", what="A smooth curve in a model (R mgcv::gam())",
                 python_note="statsmodels GLMGam chooses the smoothness another way and gives other numbers",
                 **values)
    # each row of R's smooth table by its own name, s(v1), back to the column it belongs to (R's rows follow the
    # formula, not curve_for=)
    back = {f"s({key})": v for v, key in safe.items()}
    out["sname"] = [back[str(name)] for name in np.atleast_1d(out["sname"])]
    return out


def vif_r(model):
    """R car::vif() of the model explain() fits (lm or glm, refitted in R on the same rows): one value per
    column, the generalised VIF with its df and GVIF^(1/(2 df)) when a column has several model columns."""
    from .._r import r_call

    safe = {}
    values, code = r_data(model, safe)
    code += r_fit(model, safe)
    code += ("v <- car::vif(m); if (is.matrix(v)) list(names = rownames(v), vif = unname(v[, 1]), df = unname(v[, 2]), "
             "adj = unname(v[, 3])) else list(names = names(v), vif = unname(v), df = rep(1, length(v)), "
             "adj = rep(NA_real_, length(v)))")
    out = r_call(code, packages=("car",) + FIT_PACKAGES.get(model["kind"], ()), source="car::vif",
                 what="Variance inflation factors (R car::vif())",
                 python_note="statsmodels variance_inflation_factor gives car's numbers only for least squares "
                             "with one model column per column", **values)
    back = {s: v for v, s in safe.items()}
    out["names"] = [back.get(str(n), str(n)) for n in np.atleast_1d(out["names"])]
    return out


def robust_cov(model):
    """R sandwich::vcovHC(m, type = "HC3") of the GLM explain() fitted (refitted in R on the same model
    matrix, offset and tries); statsmodels' GLM gives HC0 when HC3 is asked for."""
    from .._r import r_call

    fit, kind = model["fit"], model["kind"]
    values = {"y": np.asarray(model["y"], dtype=float), "X": np.asarray(model["X"], dtype=float)}
    left, offset = "y", ""
    if fit.get("trials") is not None:
        left, values["n"] = "cbind(y, n - y)", np.asarray(fit["trials"], dtype=float)
    if fit.get("exposure") is not None:
        offset, values["t"] = " + offset(log(t))", np.asarray(fit["exposure"], dtype=float)
    link = fit.get("link")
    family = {"binomial": f"binomial(link = '{link or 'logit'}')", "poisson": f"poisson(link = '{link or 'log'}')",
              "quasipoisson": "quasipoisson", "gamma": f"Gamma(link = '{link or 'log'}')"}
    if kind == "negbin":
        code = f"m <- MASS::glm.nb({left} ~ 0 + X{offset}); "
        packages = ("sandwich", "MASS")
    else:
        code = f"m <- stats::glm({left} ~ 0 + X{offset}, family = {family[kind]}); "
        packages = ("sandwich",)
    code += "unname(as.matrix(sandwich::vcovHC(m, type = 'HC3')))"
    out = r_call(code, packages=packages, source="sandwich::vcovHC",
                 what="Robust standard errors for a GLM (R sandwich::vcovHC(type = \"HC3\"))",
                 python_note="robust_errors=True works without R for outcome=\"numbers\" (statsmodels); statsmodels' GLM "
                             "gives only HC0, which is smaller with few rows", **values)
    k = model["X"].shape[1]
    return np.asarray(out, dtype=float).reshape(k, k)


def profile_intervals(model):
    """R stats::confint() of the GLM explain() fitted (refitted in R on the same model matrix, offset and tries):
    95 % profile-likelihood intervals of each effect, on the log scale (R 4.4 moved them from MASS into stats)."""
    from .._r import r_call

    fit, kind = model["fit"], model["kind"]
    values = {"y": np.asarray(model["y"], dtype=float), "X": np.asarray(model["X"], dtype=float)}
    left, offset = "y", ""
    if fit.get("trials") is not None:
        left, values["n"] = "cbind(y, n - y)", np.asarray(fit["trials"], dtype=float)
    if fit.get("exposure") is not None:
        offset, values["t"] = " + offset(log(t))", np.asarray(fit["exposure"], dtype=float)
    link = fit.get("link")
    family = {"binomial": f"stats::binomial(link = '{link or 'logit'}')",
              "poisson": f"stats::poisson(link = '{link or 'log'}')"}
    if kind == "negbin":
        code = f"m <- MASS::glm.nb({left} ~ 0 + X{offset}); "
        packages = ("MASS",)
    else:
        code = f"m <- stats::glm({left} ~ 0 + X{offset}, family = {family[kind]}); "
        packages = ()
    code += "unname(as.matrix(suppressMessages(stats::confint(m, level = 0.95))))"
    out = r_call(code, packages=packages, source="stats::confint",
                 what="Profile-likelihood intervals (R stats::confint() of a glm)",
                 python_note="statsmodels gives Wald intervals only (the default interval_by=\"wald\")", **values)
    k = model["X"].shape[1]
    out = np.asarray(out, dtype=float).reshape(k, 2)
    return out[:, 0], out[:, 1]
