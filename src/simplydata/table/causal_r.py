"""The R calls of compare_balanced_groups_of (phase S3d-2): propensity scores, weighting, matching and the balance
table, from R WeightIt, MatchIt and cobalt. simplydata puts the columns in and words the answer; every number comes
from R.

* the propensity score: R stats::glm(group ~ allowing_for columns, family = binomial), the model WeightIt and MatchIt
  fit themselves (method = "glm", distance = "glm").
* method="weighting": R WeightIt::weightit(method = "glm", estimand = "ATE" or "ATT", focal =) and
  WeightIt::lm_weightit(outcome ~ group), whose M-estimation standard errors allow for the estimated weights
  (Greifer, the WeightIt documentation). statsmodels TreatmentEffect.ipw gives the same estimate on lalonde with a
  standard error 15 % larger (design decision 22), so the numbers come from WeightIt.
* method="matching": R MatchIt::matchit(method = "nearest", distance = "glm", estimand = "ATT"), 1:1 nearest
  neighbour without replacement (MatchIt's default); with match_within= a caliper in standard deviations of the
  logit of the propensity score (link = "linear.logit", Austin 2011). The effect is lm(outcome ~ group, weights =)
  on the matched rows with standard errors clustered on the matched pairs (sandwich::vcovCL(cluster = ~subclass),
  lmtest::coeftest), as the MatchIt vignette "Estimating Effects After Matching" does.
* the balance table: R cobalt::bal.tab(un = TRUE, binary = "std", continuous = "std"): standardised differences
  before and after, for every column (text columns: each value), with cobalt's choice of the standard deviation
  (pooled for everyone, the focal group's for one group).
"""

from __future__ import annotations

import numpy as np

PACKAGES_WEIGHTING = ("WeightIt", "cobalt")
PACKAGES_MATCHING = ("MatchIt", "cobalt", "sandwich", "lmtest")
NOTE = "no Python package gives these standard errors and balance tables as WeightIt, MatchIt and cobalt do"

_FRAME = ("d <- data.frame(t = t, y = y); for (i in seq_along(xn)) d[[xn[i]]] <- get(xn[i]); "
          "f <- stats::as.formula(paste(\"t ~\", paste(xn, collapse = \" + \"))); "
          "ps <- stats::fitted(stats::glm(f, data = d, family = stats::binomial())); ")
_BALANCE = ("bt <- cobalt::bal.tab(fit_obj, un = TRUE, binary = \"std\", continuous = \"std\"); bb <- bt$Balance; "
            "bb <- bb[bb$Type != \"Distance\", , drop = FALSE]; ")
_R_WEIGHTING = (_FRAME +
                "fit_obj <- WeightIt::weightit(f, data = d, method = \"glm\", estimand = est, "
                "focal = if (est == \"ATT\") 1 else NULL); "
                "m <- WeightIt::lm_weightit(y ~ t, data = d, weightit = fit_obj); "
                "co <- summary(m)$coefficients; ci <- stats::confint(m, level = level); " + _BALANCE +
                "list(estimate = co[\"t\", 1], se = co[\"t\", 2], stat = co[\"t\", 3], p = co[\"t\", 4], "
                "low = ci[\"t\", 1], high = ci[\"t\", 2], ps = ps, weights = fit_obj$weights, "
                "rows = rownames(bb), before = bb$Diff.Un, after = bb$Diff.Adj, dist = \"z\", df = NA_real_)")
_R_MATCHING = (_FRAME +
               "fit_obj <- if (is.na(cal)) MatchIt::matchit(f, data = d, method = \"nearest\", distance = \"glm\", "
               "estimand = \"ATT\") else MatchIt::matchit(f, data = d, method = \"nearest\", distance = \"glm\", "
               "link = \"linear.logit\", caliper = cal, estimand = \"ATT\"); "
               "md <- MatchIt::match.data(fit_obj); "
               "m <- stats::lm(y ~ t, data = md, weights = weights); "
               "V <- sandwich::vcovCL(m, cluster = ~subclass); co <- lmtest::coeftest(m, vcov. = V); "
               "ci <- lmtest::coefci(m, vcov. = V, level = level); " + _BALANCE +
               "nn <- summary(fit_obj)$nn; "
               "list(estimate = co[\"t\", 1], se = co[\"t\", 2], stat = co[\"t\", 3], p = co[\"t\", 4], "
               "low = ci[\"t\", 1], high = ci[\"t\", 2], ps = ps, matched = fit_obj$weights, "
               "rows = rownames(bb), before = bb$Diff.Un, after = bb$Diff.Adj, dist = \"t\", "
               "df = m$df.residual, unmatched = nn[\"Unmatched\", ])")


def balance(method, effect, y, t, columns, level, caliper=None):
    """{estimate, se, stat, p, low, high, ps, weights or matched, rows, before, after, dist, df[, unmatched]}.

    t: 1 for the focal (or compared) group, 0 for the other; columns: {"x1": values, ...} (numbers or text)."""
    from .._r import r_call

    names = list(columns)
    if method == "weighting":
        code, packages = _R_WEIGHTING, PACKAGES_WEIGHTING
        what = "Weighting by the propensity score (R WeightIt::weightit(), lm_weightit(), cobalt::bal.tab())"
    else:
        code, packages = _R_MATCHING, PACKAGES_MATCHING
        what = "Matching on the propensity score (R MatchIt::matchit(), cobalt::bal.tab())"
    found = r_call(code, packages=packages, what=what, python_note=NOTE,
                   source="WeightIt" if method == "weighting" else "MatchIt",
                   t=np.asarray(t, dtype=float), y=np.asarray(y, dtype=float), xn=names,
                   est="ATE" if effect == "everyone" else "ATT", level=level / 100,
                   cal=float("nan") if caliper is None else float(caliper), **columns)
    out = {}
    for key, value in found.items():
        if key in ("rows", "dist"):
            out[key] = [str(v) for v in np.atleast_1d(value)]
        else:
            out[key] = np.asarray(value, dtype=float).ravel()
    return out
