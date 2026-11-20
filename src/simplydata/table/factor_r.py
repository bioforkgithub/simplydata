"""The R calls behind the hidden-factor words (phase S3c-2): R psych (with GPArotation) and R lavaan.

Nothing is calculated here: the functions hand the rows that the words have already checked to R and give back
R's own numbers. The packages are checked with need_r() but never attached (every call names its package,
psych::fa, lavaan::cfa), so they cannot hide a function of another package.

* explore(): find_hidden_factors_behind. After set.seed(with_seed) (parallel analysis simulates data, and the
  oblimin rotation of GPArotation starts from random numbers too: unseeded, its loadings change in the sixth
  digit from run to run, checked with psych 2.6.9 and GPArotation 2026.8.2),
  psych::fa.parallel(fa = "fa") chooses how many factors (Horn's parallel analysis) when how_many="automatic"; psych::fa() fits them (minres, ml or principal axis) and
  rotates them (oblimin and promax through GPArotation and psych, varimax through GPArotation); psych::KMO()
  gives the Kaiser-Meyer-Olkin measure.
* confirm(): check_hidden_factors. lavaan::cfa() for measured_by= and lavaan::sem() for formula=, maximum
  likelihood, with missing = "ml" (every value given is used) when the rows have empty cells;
  lavaan::fitMeasures(), lavaan::standardizedSolution() and lavaan::modindices().
"""

from __future__ import annotations

import numpy as np

EXPLORE = r"""
# psych::fa() rotates through GPArotation::oblimin() and GPArotation::Varimax() (promax is psych's own)
x <- as.data.frame(x); colnames(x) <- cols
k <- how_many
suggested <- NA_real_
set.seed(seed)  # parallel analysis simulates data, and the oblimin rotation starts from random numbers too
if (how_many == 0) {
  pa <- psych::fa.parallel(x, fm = fm, fa = "fa", plot = FALSE)
  suggested <- as.numeric(pa$nfact)
  k <- suggested
}
out <- list(suggested = suggested, kmo = as.numeric(psych::KMO(x)$MSA),
            version = as.character(utils::packageVersion("psych")))
if (!is.na(k) && k >= 1) {
  f <- psych::fa(x, nfactors = k, fm = fm, rotate = rotate)
  v <- f$Vaccounted
  out$k <- k
  out$loadings <- unclass(f$loadings)
  out$communality <- as.numeric(f$communality)
  out$uniqueness <- as.numeric(f$uniquenesses)
  out$phi <- if (is.null(f$Phi)) NA_real_ else unclass(f$Phi)
  out$ss <- as.numeric(v["SS loadings", ])
  out$share <- as.numeric(v["Proportion Var", ])
  out$cumulative <- if ("Cumulative Var" %in% rownames(v)) as.numeric(v["Cumulative Var", ]) else
    as.numeric(v["Proportion Var", ])
}
out
"""

CONFIRM = r"""
d <- as.data.frame(x); colnames(d) <- cols
fit <- if (route == "cfa") lavaan::cfa(model, data = d, estimator = "ML", missing = miss) else
  lavaan::sem(model, data = d, estimator = "ML", missing = miss)
if (!lavaan::lavInspect(fit, "converged")) {
  list(converged = FALSE)
} else {
  fm <- lavaan::fitMeasures(fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "rmsea.ci.lower",
                                  "rmsea.ci.upper", "srmr"))
  s <- lavaan::standardizedSolution(fit)
  mi <- tryCatch(lavaan::modindices(fit, sort. = TRUE), error = function(e) NULL)
  out <- list(converged = TRUE, fit = as.numeric(fm), n = as.numeric(lavaan::lavInspect(fit, "nobs")),
              lhs = as.character(s$lhs), op = as.character(s$op), rhs = as.character(s$rhs),
              est = as.numeric(s$est.std), se = as.numeric(s$se), p = as.numeric(s$pvalue),
              low = as.numeric(s$ci.lower), high = as.numeric(s$ci.upper),
              version = as.character(utils::packageVersion("lavaan")))
  if (!is.null(mi) && nrow(mi) > 0) {
    out$mi_lhs <- as.character(mi$lhs); out$mi_op <- as.character(mi$op); out$mi_rhs <- as.character(mi$rhs)
    out$mi <- as.numeric(mi$mi)
  }
  out
}
"""


def explore(x, columns, how_many, fm, rotate, seed):
    """R psych for find_hidden_factors_behind: x is the complete rows (a matrix), how_many 0 for parallel
    analysis. Gives back psych's numbers as a dict."""
    from .._r import need_r, r_call

    need_r(("psych", "GPArotation"), "Finding hidden factors (R psych)",
           "statsmodels Factor has principal-axis and maximum-likelihood factor analysis with varimax or promax, "
           "but no minres, no oblimin and no parallel analysis, so simplydata uses R psych")
    return r_call(EXPLORE, what="Finding hidden factors (R psych)", source="psych", note_words=_psych_words,
                  x=np.asarray(x, dtype=float), cols=np.array(columns, dtype=object), how_many=float(how_many),
                  fm=fm, rotate=rotate, seed=float(seed))


def confirm(x, columns, model, route, missing):
    """R lavaan for check_hidden_factors: x holds the used columns (empty cells as NaN), model is lavaan
    syntax, route "cfa" (measured_by=) or "sem" (formula=), missing "listwise" or "ml"."""
    from .._r import need_r, r_call

    need_r(("lavaan",), "Checking hidden factors (R lavaan)",
           "Python's semopy is not on conda-forge and statsmodels has no confirmatory factor analysis, so "
           "simplydata uses R lavaan")
    return r_call(CONFIRM, what="Checking hidden factors (R lavaan)", source="lavaan", note_words=_lavaan_words,
                  x=np.asarray(x, dtype=float), cols=np.array(columns, dtype=object), model=model, route=route,
                  miss=missing)


def _psych_words(note):
    """psych's warnings said plainly; its messages about loading GPArotation are not repeated."""
    lower = note.lower()
    if "heywood" in lower:
        return ("a column's shared part reached 1 or more (a Heywood case): the fit is not to be trusted. Try "
                "fewer factors, or leave out the column with the largest shared part.")
    if "loading required namespace" in lower:
        return ""
    return note


def _lavaan_words(note):
    """lavaan's warnings said plainly."""
    lower = note.lower()
    if "not identified" in lower or "could not be inverted" in lower or "could not compute standard errors" in lower:
        return ("lavaan could not work out the standard errors: the model may not be identified (too few columns "
                "for a hidden factor, or a path that the data cannot pin down). lavaan said: " + note.strip())
    if "variances are negative" in lower or "not positive definite" in lower:
        return ("lavaan found a negative variance or a correlation above 1 (a Heywood case): the model does not "
                "suit these data. lavaan said: " + note.strip())
    if "some cases are empty" in lower:
        return ""  # said by the word itself
    return note
