"""explain() for outcomes with more than one number per effect: ordered groups, groups, shares and
counts with many zeros. Called from ModelWords.explain (models.py); never changes the table.

Choices (each checked against R in tests/test_s2_more_outcomes.py):

* outcome="ordered groups": proportional-odds (ordered logistic) regression, statsmodels
  OrderedModel (logit), = R MASS::polr(). Each effect is an odds ratio of being in a higher
  group; the cut-points between the groups (statsmodels transform_threshold_params, = polr's
  zeta) are printed in a short block of their own. The order of the groups comes from
  in_order= (text) or from the numbers.
* outcome="groups": multinomial logistic regression, statsmodels MNLogit, = R nnet::multinom().
  One block per group, each compared with the baseline (the first group in sorted order, as R).
* outcome="shares": beta regression for shares between 0 and 1, R betareg::betareg() itself
  (logit link for the average share, constant precision); statsmodels BetaModel gives the same
  estimates but other standard errors.
* outcome="counts with many zeros": zero-inflated Poisson regression, R pscl::zeroinfl() itself
  (the same columns in both parts, logit zero part); statsmodels gives other standard errors.
  A zero can come two ways: an extra zero (the thing could not happen there) or a count that
  happened to be 0. The printout has one block for each part. outcome="counts with many zeros
  that vary a lot": the same with a negative binomial count part, pscl::zeroinfl(dist = "negbin").
* outcome="counts in two steps" (a hurdle model; "hurdle" is another spelling): first zero or not
  (a logistic part for "more than 0"), then how many among the counts above 0 (a Poisson count
  part cut off at 1), R pscl::hurdle(dist = "poisson", zero.dist = "binomial") itself; "counts in
  two steps that vary a lot" has a negative binomial count part (dist = "negbin"). pscl's
  binomial zero part is the textbook form; statsmodels' HurdleCountModel has no logit zero part.
* zero_part_using=["distance"]: the columns of the zero part (pscl's y ~ x | z) for the
  zero-inflated and the two-step outcomes; without it, the same columns as using=.
"""

from __future__ import annotations

import math
import warnings

import narwhals as nw
import numpy as np

from .._errors import SimplydataError
from .stat_tests import _label, _list_words, _num, _skipped_note
from .summaries import _p_clause

Z95 = 1.959963984540054
ZERO_OUTCOMES = ("counts with many zeros", "counts with many zeros that vary a lot", "counts in two steps",
                 "counts in two steps that vary a lot")
MORE_OUTCOMES = ("ordered groups", "groups", "shares") + ZERO_OUTCOMES


def _sort_key(value):
    return (str(type(value)), value)


def _exp(x) -> float:
    """exp() that gives infinity instead of an error for a huge value (a part that runs away)."""
    return math.exp(x) if x < 709 else math.inf


# ---------------------------------------------------------------------------- the outcome column
def outcome_codes(column, outcome, values, kind, in_order):
    """(codes 0..K-1 or numbers, level names) for the outcome column."""
    if outcome in ("ordered groups", "groups"):
        found = sorted(set(values.tolist()), key=_sort_key)
        if outcome == "ordered groups" and kind != "number":
            if in_order is None:
                raise SimplydataError(
                    f'outcome="ordered groups" needs the order of the groups in "{column}", lowest first, for '
                    f'example in_order={[_label(v) for v in found]!r} put in the right order.')
            order = list(in_order)
            missing = [_label(v) for v in found if v not in order]
            if missing:
                raise SimplydataError(f"in_order= does not have {_list_words(repr(m) for m in missing)}, which "
                                      f'{"is" if len(missing) == 1 else "are"} in "{column}".')
            found = [v for v in order if v in set(values.tolist())]
        if len(found) < 3:
            raise SimplydataError(f'outcome="{outcome}" needs 3 or more groups in "{column}"; it has '
                                  f'{len(found)}. For 2 groups use outcome="yes or no".')
        place = {v: i for i, v in enumerate(found)}
        return np.array([place[v] for v in values], dtype=float), [_label(v) for v in found]
    if kind != "number":
        raise SimplydataError(f'outcome="{outcome}" needs "{column}" to hold numbers; it holds text.')
    y = values.astype(float)
    if outcome == "shares":
        if np.any(y <= 0) or np.any(y >= 1):
            hint = (" They look like percents: divide by 100 first, for example with "
                    "table.add_column(\"share\", \"forest / 100\").") if np.all((y > 0) & (y < 100)) else ""
            raise SimplydataError(f'outcome="shares" needs shares above 0 and below 1 in "{column}".{hint}')
        return y, None
    if np.any(y < 0) or np.any(y != np.round(y)):
        raise SimplydataError(f'outcome="{outcome}" needs whole numbers of 0 or more in "{column}".')
    if not np.any(y == 0):
        other = "counts that vary a lot" if "vary a lot" in outcome else "counts"
        raise SimplydataError(f'"{column}" has no zeros, so there are no zeros to model and outcome="{outcome}" does '
                              f'not fit; use outcome="{other}".')
    if outcome.startswith("counts in two steps") and np.all(y == 0):
        raise SimplydataError(f'"{column}" holds only zeros, so there are no counts above 0 for the second step.')
    return y, None


# ---------------------------------------------------------------------------- the fits
def _quietly(fit):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with np.errstate(all="ignore"):
            return fit()


def fit_ordered(X, y):
    """statsmodels OrderedModel (logit), = R polr: slopes, their covariance, cut-points."""
    from statsmodels.miscmodels.ordinal_model import OrderedModel

    model = OrderedModel(y, X[:, 1:], distr="logit")  # no intercept: the cut-points take its place
    first = _quietly(lambda: model.fit(method="bfgs", disp=0, maxiter=5000, gtol=1e-10))
    result = _quietly(lambda: model.fit(start_params=first.params, method="newton", disp=0, maxiter=100))
    k = X.shape[1] - 1
    params = np.asarray(result.params, dtype=float)
    cuts = np.asarray(model.transform_threshold_params(params), dtype=float)[1:-1]
    return {"beta": params[:k], "cov": np.asarray(result.cov_params(), dtype=float)[:k, :k], "cuts": cuts,
            "loglik": float(result.llf), "aic": float(result.aic), "bic": float(result.bic),
            "pseudo": float(result.prsquared)}


def fit_groups(X, y):
    """statsmodels MNLogit, = R nnet::multinom: one coefficient column per group after the first."""
    from statsmodels.discrete.discrete_model import MNLogit

    result = _quietly(lambda: MNLogit(y, X).fit(method="newton", disp=0, maxiter=200))
    params = np.asarray(result.params, dtype=float)  # p x (K - 1)
    bse = np.asarray(result.bse, dtype=float)
    return {"beta": params, "se": bse, "loglik": float(result.llf), "aic": float(result.aic), "bic": float(result.bic),
            "pseudo": float(result.prsquared)}


def fit_shares(X, y):
    """R betareg::betareg(y ~ 0 + X) itself: mean coefficients (logit), their errors, the precision."""
    from .._r import r_call

    out = r_call("b <- betareg::betareg(y ~ 0 + X); s <- summary(b)$coefficients; "
                 "list(beta = unname(s$mean[, 1]), se = unname(s$mean[, 2]), phi = unname(s$precision[1, 1]), "
                 "loglik = as.numeric(stats::logLik(b)), aic = stats::AIC(b), bic = stats::BIC(b), "
                 "pseudo = b$pseudo.r.squared)",
                 packages=("betareg",), what="Beta regression for shares (R betareg::betareg())",
                 python_note="statsmodels BetaModel gives the same estimates but other standard errors",
                 y=np.asarray(y, dtype=float), X=np.asarray(X, dtype=float))
    return {"beta": np.asarray(out["beta"], dtype=float), "se": np.asarray(out["se"], dtype=float),
            "phi": float(out["phi"][0]), "loglik": float(out["loglik"][0]), "aic": float(out["aic"][0]),
            "bic": float(out["bic"][0]), "pseudo": float(out["pseudo"][0])}


def fit_zeros(X, y, Z=None, dist="poisson", hurdle=False):
    """R pscl::zeroinfl(y ~ 0 + X | 0 + Z, dist = dist) itself, or pscl::hurdle(..., zero.dist = "binomial") with
    hurdle=True: the count part, the zero part (Z = X when not given) and, for "negbin", theta."""
    from .._r import r_call

    Z = X if Z is None else Z
    fitter = "pscl::hurdle" if hurdle else "pscl::zeroinfl"
    zero_dist = ", zero.dist = 'binomial'" if hurdle else ""
    theta = "theta = unname(z$theta[1]), " if dist == "negbin" else "theta = NA_real_, "
    out = r_call(f"z <- {fitter}(y ~ 0 + X | 0 + Z, dist = '{dist}'{zero_dist}); s <- summary(z)$coefficients; "
                 "k <- ncol(X); "
                 "list(count = unname(s$count[seq_len(k), 1]), count_se = unname(s$count[seq_len(k), 2]), "
                 f"zero = unname(s$zero[, 1]), zero_se = unname(s$zero[, 2]), {theta}"
                 "loglik = as.numeric(stats::logLik(z)), aic = stats::AIC(z), bic = stats::BIC(z), "
                 f"null = as.numeric(stats::logLik({fitter}(y ~ 1 | 1, dist = '{dist}'{zero_dist}))))",
                 packages=("pscl",), what=("Counts in two steps (R pscl::hurdle())" if hurdle else
                                           "Zero-inflated counts (R pscl::zeroinfl())"),
                 python_note=("statsmodels' HurdleCountModel has no logistic zero part (pscl's default)" if hurdle else
                              "statsmodels ZeroInflatedPoisson and ZeroInflatedNegativeBinomialP give the same "
                              "estimates but other standard errors"),
                 y=np.asarray(y, dtype=float), X=np.asarray(X, dtype=float), Z=np.asarray(Z, dtype=float))
    return {key: np.asarray(out[key], dtype=float) for key in ("count", "count_se", "zero", "zero_se")} | {
        "loglik": float(out["loglik"][0]), "aic": float(out["aic"][0]), "bic": float(out["bic"][0]),
        "theta": float(np.atleast_1d(out["theta"])[0]),
        "pseudo": 1 - float(out["loglik"][0]) / float(out["null"][0])}  # McFadden, as R performance::r2_mcfadden()


# ---------------------------------------------------------------------------- words
def _who(model, j):
    """'each 1 more "hours"' / '"breakfast" "yes" against "no"' / 'hours : breakfast (interaction)'."""
    parts = model["parts_of"][j]
    if len(parts) == 1 and parts[0][1] is None:
        return f'each 1 more "{parts[0][0]}"', True
    if len(parts) == 1:
        var, level = parts[0][1]
        return f'"{var}" "{_label(level)}" against "{_label(model["levels"][var][0])}"', False
    return f"{model['labels'][j]} (interaction)", None


NONE = "it truly made no difference"  # the p-value clause of each term (W2)


def _sentence(model, j, b, se, thing):
    from scipy import stats

    p = float(2 * stats.norm.sf(abs(b / se))) if se > 0 else math.nan
    ratio, low, high = _exp(b), _exp(b - Z95 * se), _exp(b + Z95 * se)
    who, numeric = _who(model, j)
    interval = f"95 % CI {_num(low)} to {_num(high)}"
    if numeric:
        text = f"  {who} multiplies {thing} by {_num(ratio)} ({interval}); {_p_clause(p, NONE)}."
    elif numeric is False:
        verb = "are" if thing.startswith("the odds") else "is"
        text = f"  {who}: {thing} {verb} {_num(ratio)} times as high ({interval}); {_p_clause(p, NONE)}."
    else:
        text = (f"  {who}: {_num(ratio)} ({interval}), how many times the effect of one is multiplied by the "
                f"other; {_p_clause(p, NONE)}.")
    return text, p, ratio, low, high


def _rows(model, beta, se, effect, start, extra):
    """Result rows for terms start..; extra holds fixed columns (part, group)."""
    from scipy import stats

    rows = []
    for j in range(start, len(model["labels"])):
        b, s = float(beta[j - start] if start else beta[j]), float(se[j - start] if start else se[j])
        z = b / s if s > 0 else math.nan
        row = dict(extra)
        row.update({"term": model["labels"][j], effect: _exp(b), "95 % CI low": _exp(b - Z95 * s),
                    "95 % CI high": _exp(b + Z95 * s), f"log {effect}": b, "standard error": s,
                    "statistic name": "z", "statistic": z, "p-value": float(2 * stats.norm.sf(abs(z)))})
        rows.append(row)
    return rows


def explain_more(words, step, column, outcome, pieces, model):
    """Fit and print one model for the four outcomes; gives back the result table."""
    X, y, n = model["X"], model["y"], model["n"]
    formula = f"{column} ~ " + " + ".join(pieces)
    variables = _list_words(f'"{v}"' for v in model["variables"])
    rows = []
    if outcome == "ordered groups":
        fit = fit_ordered(X, y)
        se = np.sqrt(np.diag(fit["cov"]))
        groups = model["groups_of_outcome"]
        thing = f'the odds of a higher "{column}"'
        print(f'Explaining "{column}" ({" < ".join(groups)}) from {variables} ({n} rows). Each odds ratio below '
              "holds the other columns fixed:")
        for j in range(1, len(model["labels"])):
            print(_sentence(model, j, fit["beta"][j - 1], se[j - 1], thing)[0])
        cuts = ", ".join(f"{a} | {b} {_num(c)}" for a, b, c in zip(groups[:-1], groups[1:], fit["cuts"]))
        print(f"Cut-points between the groups (log-odds, when every number column is 0): {cuts}.")
        print(f"Method: proportional-odds (ordered logistic) regression, as R MASS::polr({formula}) (statsmodels "
              "OrderedModel): one odds ratio per column for being in a higher group, the same at every cut-point. "
              "Wald 95 % intervals and z-tests.")
        print(fit_line(fit, "mcfadden"))
        rows = _rows(model, fit["beta"], se, "odds ratio", 1, {})
        for (a, b), c in zip(zip(groups[:-1], groups[1:]), fit["cuts"]):
            rows.append({"term": f"cut-point {a} | {b}", "log odds ratio": float(c)})
    elif outcome == "groups":
        fit = fit_groups(X, y)
        groups = model["groups_of_outcome"]
        base = groups[0]
        print(f'Explaining which "{column}" a row is in ({_list_words(groups)}) from {variables} ({n} rows). Each '
              f'group is compared with "{base}" (the baseline); each odds ratio holds the other columns fixed.')
        for g, name in enumerate(groups[1:]):
            print(f'Being "{name}" rather than "{base}":')
            thing = f'the odds of "{name}" rather than "{base}"'
            for j in range(1, len(model["labels"])):
                print(_sentence(model, j, fit["beta"][j, g], fit["se"][j, g], thing)[0])
            rows += _rows(model, fit["beta"][:, g], fit["se"][:, g], "odds ratio", 0, {"group": name})
        print(f"Method: multinomial logistic regression, as R nnet::multinom({formula}) (statsmodels MNLogit). "
              "Wald 95 % intervals and z-tests.")
        print(fit_line(fit, "mcfadden"))
    elif outcome == "shares":
        fit = fit_shares(X, y)
        thing = 'the odds of the share (share / (1 - share))'
        print(f'Explaining the share "{column}" from {variables} ({n} rows). Each odds ratio below holds the other '
              "columns fixed:")
        for j in range(1, len(model["labels"])):
            print(_sentence(model, j, fit["beta"][j], fit["se"][j], thing)[0])
        print(f"Precision {_num(fit['phi'])}: how tightly the shares gather around their average (bigger is "
              "tighter).")
        print(f"Method: beta regression for shares between 0 and 1, run in R: betareg::betareg({formula}) (logit "
              "link, the same precision for every row). Wald 95 % intervals and z-tests.")
        print(fit_line(fit, "ferrari"))
        rows = _rows(model, fit["beta"], fit["se"], "odds ratio", 0, {})
    else:
        rows = _explain_zeros(model, outcome, formula, variables, column, X, y, n)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    data = {k: [r.get(k, math.nan) if k not in ("term", "group", "part") else r.get(k) for r in rows] for k in keys}
    return words._new_table(nw.from_dict(data, backend=words._frame.implementation))


def _explain_zeros(model, outcome, formula, variables, column, X, y, n):
    """The zero-inflated and the two-step (hurdle) counts: two blocks, one per part, and the result rows."""
    hurdle = outcome.startswith("counts in two steps")
    dist = "negbin" if outcome.endswith("vary a lot") else "poisson"
    zero_model = model.get("zero_model") or model
    zero_formula = ""
    if model.get("zero_model") is not None:
        zero_formula = " | " + " + ".join(model["zero_pieces"])
    fit = fit_zeros(X, y, zero_model["X"], dist=dist, hurdle=hurdle)
    zeros = int((y == 0).sum())
    zero_names = _list_words(f'"{v}"' for v in zero_model["variables"])
    if hurdle:
        print(f'Explaining "{column}" from {variables} ({n} rows, {zeros} of them 0) in two steps: first whether '
              "the count is 0 or more than 0, then how many, among the counts above 0:")
        print(f"Zero or not (the first step, from {zero_names}; odds of a count above 0):")
        for j in range(1, len(zero_model["labels"])):
            print(_sentence(zero_model, j, fit["zero"][j], fit["zero_se"][j], "the odds of a count above 0")[0])
        print("How many, when not zero (the second step; each rate ratio holds the other columns fixed):")
        for j in range(1, len(model["labels"])):
            print(_sentence(model, j, fit["count"][j], fit["count_se"][j], "the expected count")[0])
    else:
        print(f'Explaining "{column}" from {variables} ({n} rows, {zeros} of them 0). A 0 can come two ways: an '
              "extra zero (where it could not happen at all) or a count that happened to be 0, so the model has "
              "two parts:")
        print("How many, where it can happen (the count part; each rate ratio holds the other columns fixed):")
        for j in range(1, len(model["labels"])):
            print(_sentence(model, j, fit["count"][j], fit["count_se"][j], "the expected count")[0])
        print(f"Extra zeros (the zero part, from {zero_names}; odds of being an extra zero):")
        for j in range(1, len(zero_model["labels"])):
            print(_sentence(zero_model, j, fit["zero"][j], fit["zero_se"][j], "the odds of an extra zero")[0])
    if dist == "negbin":
        print(f"Theta {_num(fit['theta'])}: how much the counts vary beyond Poisson (the smaller, the more they vary; "
              "a very large theta means they vary no more than Poisson allows).")
    same = "" if model.get("zero_model") is not None else " (the same columns in both parts)"
    kind = "negative binomial" if dist == "negbin" else "Poisson"
    if hurdle:
        print(f"Method: a two-step (hurdle) model, run in R: pscl::hurdle({formula}{zero_formula}, dist = \"{dist}\", "
              f"zero.dist = \"binomial\"){same}: a logistic model for zero or not, and a {kind} model cut off at 1 "
              "for the counts above 0. Wald 95 % intervals and z-tests.")
    else:
        print(f"Method: zero-inflated {kind} regression, run in R: pscl::zeroinfl({formula}{zero_formula}, dist = "
              f"\"{dist}\"){same}. Wald 95 % intervals and z-tests.")
    print(fit_line(fit, "mcfadden"))
    zero_part = "zero or not" if hurdle else "extra zeros"
    return (_rows(model, fit["count"], fit["count_se"], "ratio", 0, {"part": "count"})
            + _rows(zero_model, fit["zero"], fit["zero_se"], "ratio", 0, {"part": zero_part}))


# a measure of fit: (its words on the "How well it fits:" line, its method on the Method line)
PSEUDO_WORDS = {
    "mcfadden": ("pseudo R squared {v} (0 = no better than no columns)",
                 "McFadden's pseudo R squared (1 - log-likelihood / log-likelihood with no columns) as R "
                 "performance::r2_mcfadden()"),
    "ferrari": ("pseudo R squared {v} (how closely the fitted shares follow the real ones)",
                "the pseudo R squared of beta regression (the squared correlation of the fitted and the observed "
                "shares on the logit scale) as R betareg and performance::r2()"),
}


def fit_line(fit, pseudo=None, start="", which="", method=""):
    """The fit block of an explain printout, two lines: in plain words how well it fits (an R squared when
    there is one, AIC and BIC), then the Method line with the R calls that give the same numbers.

    start and method are the words and the method of the R squared, when the caller has one; pseudo names one of
    PSEUDO_WORDS instead. A pseudo R squared is never read as "explains X %": it does not mean that."""
    if pseudo and fit.get("pseudo") is not None and np.isfinite(fit["pseudo"]):
        words, how = PSEUDO_WORDS[pseudo]
        start, method = words.format(v=f"{fit['pseudo']:.3f}"), how
    start = f"{start}. " if start else ""
    method = f"{method}; " if method else ""
    return (f"How well it fits: {start}AIC {_num(fit['aic'])}, BIC {_num(fit['bic'])}: smaller is better, but only "
            f"to compare models of the same rows (compare_models).\n"
            f"Method: {method}AIC and BIC{which} as R AIC(), BIC().")


def check_rows(step, n, p):
    if n <= p:
        raise SimplydataError(f"{step}() needs more rows ({n}) than values to estimate ({p}).")


__all__ = ["MORE_OUTCOMES", "ZERO_OUTCOMES", "outcome_codes", "explain_more", "check_rows", "_skipped_note"]
