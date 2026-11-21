"""The R calls of the survey words (phase S3d-1): every number comes from R survey (Lumley).

The design is made once per call with survey::svydesign(ids = ~clusters or ~1, strata = ~strata, weights = ~weights,
fpc = ~population_sizes, nest = TRUE), with options(survey.lonely.psu = "adjust") (survey's default "fail" stops
when a stratum has only one cluster; "adjust" centres that cluster at the average of all, the conservative choice
Lumley recommends). Then:

* averages and totals: svymean / svytotal (svyby for groups), intervals confint(df = degf(design)): t on the design's
  degrees of freedom, not survey's normal default;
* percentiles: svyquantile(qrule = "math", ci = TRUE, df = degf(design)) (Woodruff's interval);
* percents: svyciprop(method = "logit") (its df is degf(design));
* estimated numbers of rows: svytotal of a column of ones; group shares svymean(~factor(group));
* models: svyglm (gaussian; quasibinomial for yes or no; quasipoisson for counts), confint() on the model's
  residual degrees of freedom as summary() uses;
* two averages: svyttest; counts between groups: svychisq (Rao-Scott F).
"""

from __future__ import annotations

import numpy as np

PACKAGES = ("survey",)
WHAT = "Survey-weighted answers (R survey)"
PYTHON_NOTE = ("Python has no package for design-based standard errors that matches R survey (statsmodels has "
               "weights but no strata, clusters or population sizes)")

_DESIGN = """
op <- options(survey.lonely.psu = "adjust")
dat <- data.frame(sd_row = seq_len(sd_n))
if (!is.null(sd_w)) dat$sd_w <- sd_w
if (!is.null(sd_s)) dat$sd_s <- sd_s
if (!is.null(sd_c)) dat$sd_c <- sd_c
if (!is.null(sd_f)) dat$sd_f <- sd_f
if (!is.null(y)) dat$y <- y
if (!is.null(g)) dat$g <- g
d <- survey::svydesign(ids = if (is.null(sd_c)) ~1 else ~sd_c, strata = if (is.null(sd_s)) NULL else ~sd_s,
                       weights = if (is.null(sd_w)) NULL else ~sd_w, fpc = if (is.null(sd_f)) NULL else ~sd_f,
                       data = dat, nest = TRUE)
df <- survey::degf(d)
"""

_FACTS = _DESIGN + """
pop <- if (is.null(sd_f)) NA_real_ else max(d$fpc$popsize)
lonely <- if (is.null(sd_s)) 0 else sum(table(d$strata[, 1][!duplicated(d$cluster[, 1])]) == 1)
out <- list(df = df, strata = if (is.null(sd_s)) 1 else length(unique(sd_s)),
            clusters = if (is.null(sd_c)) sd_n else length(unique(paste(sd_s, sd_c))),
            lonely = lonely, popsize = pop)
options(op)
out
"""

_ESTIMATE = _DESIGN + """
if (sd_what == "count") d <- stats::update(d, y = rep(1, sd_n))
grouped <- !is.null(g)
if (sd_what %in% c("mean", "total", "count")) {
  fn <- if (sd_what == "mean") survey::svymean else survey::svytotal
  m <- if (grouped) survey::svyby(~y, ~g, d, fn, na.rm = TRUE) else fn(~y, d, na.rm = TRUE)
  ci <- stats::confint(m, df = df)
  out <- list(est = as.numeric(stats::coef(m)), se = as.numeric(survey::SE(m)), low = as.numeric(ci[, 1]),
              high = as.numeric(ci[, 2]), grp = if (grouped) as.character(m$g) else NA_character_)
} else if (sd_what == "quantile") {
  if (grouped) {
    m <- survey::svyby(~y, ~g, d, survey::svyquantile, quantiles = q, qrule = "math", ci = TRUE,
                       vartype = c("se", "ci"), df = df, na.rm = TRUE)
    out <- list(est = as.numeric(m$y), se = as.numeric(m$se.y), low = as.numeric(m$ci_l), high = as.numeric(m$ci_u),
                grp = as.character(m$g))
  } else {
    m <- survey::svyquantile(~y, d, quantiles = q, qrule = "math", ci = TRUE, df = df, na.rm = TRUE)$y
    out <- list(est = m[1, 1], se = m[1, 4], low = m[1, 2], high = m[1, 3], grp = NA_character_)
  }
} else if (sd_what == "prop") {
  if (grouped) {
    m <- survey::svyby(~y, ~g, d, survey::svyciprop, vartype = c("se", "ci"), method = "logit", df = df,
                       na.rm = TRUE)
    out <- list(est = as.numeric(stats::coef(m)), se = as.numeric(survey::SE(m)), low = as.numeric(m$ci_l),
                high = as.numeric(m$ci_u), grp = as.character(m$g))
  } else {
    m <- survey::svyciprop(~y, d, method = "logit", na.rm = TRUE)
    ci <- attr(m, "ci")
    out <- list(est = as.numeric(stats::coef(m)), se = as.numeric(survey::SE(m)), low = as.numeric(ci[1]),
                high = as.numeric(ci[2]), grp = NA_character_)
  }
} else if (sd_what == "share") {
  m <- survey::svymean(~factor(g), d, na.rm = TRUE)
  ci <- stats::confint(m, df = df)
  out <- list(est = as.numeric(stats::coef(m)), se = as.numeric(survey::SE(m)), low = as.numeric(ci[, 1]),
              high = as.numeric(ci[, 2]), grp = sub("^factor\\\\(g\\\\)", "", names(stats::coef(m))))
}
out$df <- df
options(op)
out
"""

_GLM = _DESIGN + """
for (i in seq_along(xn)) dat[[paste0("sd_x", i)]] <- get(paste0("sd_x", i))
d <- survey::svydesign(ids = if (is.null(sd_c)) ~1 else ~sd_c, strata = if (is.null(sd_s)) NULL else ~sd_s,
                       weights = if (is.null(sd_w)) NULL else ~sd_w, fpc = if (is.null(sd_f)) NULL else ~sd_f,
                       data = dat, nest = TRUE)
f <- stats::as.formula(paste("y ~", paste0("sd_x", seq_along(xn), collapse = " + ")))
fam <- switch(family, gaussian = stats::gaussian(), quasibinomial = stats::quasibinomial(),
              quasipoisson = stats::quasipoisson())
fit <- survey::svyglm(f, design = d, family = fam, na.action = stats::na.omit)
s <- summary(fit)$coefficients
ci <- stats::confint(fit)
out <- list(term = rownames(s), est = as.numeric(s[, 1]), se = as.numeric(s[, 2]), stat = as.numeric(s[, 3]),
            p = as.numeric(s[, 4]), low = as.numeric(ci[, 1]), high = as.numeric(ci[, 2]),
            df = as.numeric(fit$df.residual), n = as.numeric(nrow(stats::model.frame(fit))))
options(op)
out
"""

_TTEST = _DESIGN + """
r <- survey::svyttest(y ~ g, d)
out <- list(t = unname(r$statistic), df = unname(r$parameter), p = unname(r$p.value), diff = unname(r$estimate),
            low = r$conf.int[1], high = r$conf.int[2], levels = levels(factor(g)))
options(op)
out
"""

_CHISQ = _DESIGN + """
r <- survey::svychisq(~y + g, d)
out <- list(f = unname(r$statistic), ndf = unname(r$parameter[1]), ddf = unname(r$parameter[2]), p = unname(r$p.value))
options(op)
out
"""


def _call(code, design, n, source, **values):
    from .._r import need_r, r_call

    need_r(PACKAGES, WHAT, PYTHON_NOTE)  # checked, not attached: every call names survey::
    return r_call(code, packages=(), what=WHAT, python_note=PYTHON_NOTE, source=source,
                  sd_n=float(n), sd_w=design.get("weights"), sd_s=design.get("strata"), sd_c=design.get("clusters"),
                  sd_f=design.get("population_sizes"), **{"y": None, "g": None, **values})


def facts(design, n):
    found = _call(_FACTS, design, n, "survey::svydesign")
    return {k: float(np.asarray(v, dtype=float).ravel()[0]) for k, v in found.items()}


def estimate(design, n, what, y=None, g=None, q=None):
    """{est, se, low, high, grp, df} arrays from R survey for one estimate (or one per group)."""
    source = {"mean": "survey::svymean", "total": "survey::svytotal", "count": "survey::svytotal",
              "quantile": "survey::svyquantile", "prop": "survey::svyciprop", "share": "survey::svymean"}[what]
    found = _call(_ESTIMATE, design, n, source, sd_what=what, y=y, g=g, q=None if q is None else float(q))
    out = {k: np.atleast_1d(np.asarray(found[k], dtype=float)) for k in ("est", "se", "low", "high")}
    out["grp"] = [str(v) for v in np.atleast_1d(found["grp"])]
    out["df"] = float(np.asarray(found["df"], dtype=float).ravel()[0])
    return out


def glm(design, n, y, columns, values, family):
    extra = {f"sd_x{i}": v for i, v in enumerate(values, 1)}
    found = _call(_GLM, design, n, "survey::svyglm", y=y, xn=np.array(columns, dtype=object), family=family, **extra)
    out = {k: np.atleast_1d(np.asarray(found[k], dtype=float)) for k in ("est", "se", "stat", "p", "low", "high")}
    # R names the terms sd_x1, sd_x2b ... (the column's place, then a level): back to the table's own names
    names = {f"sd_x{i}": c for i, c in enumerate(columns, 1)}
    terms = []
    for term in (str(v) for v in np.atleast_1d(found["term"])):
        key = max((k for k in names if term.startswith(k) and not term[len(k):].isdigit()), key=len, default=None)
        terms.append(names[key] + term[len(key):] if key else term)
    out["term"] = terms
    out["df"] = float(np.asarray(found["df"], dtype=float).ravel()[0])
    out["n"] = int(np.asarray(found["n"], dtype=float).ravel()[0])
    return out


def ttest(design, n, y, g):
    found = _call(_TTEST, design, n, "survey::svyttest", y=y, g=g)
    out = {k: float(np.asarray(found[k], dtype=float).ravel()[0]) for k in ("t", "df", "p", "diff", "low", "high")}
    out["levels"] = [str(v) for v in np.atleast_1d(found["levels"])]
    return out


def chisq(design, n, y, g):
    found = _call(_CHISQ, design, n, "survey::svychisq", y=y, g=g)
    return {k: float(np.asarray(v, dtype=float).ravel()[0]) for k, v in found.items()}
