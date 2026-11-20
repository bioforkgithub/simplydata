"""explain() grows (S3a-1): the options that change how one model is fitted or reported.

Called from ModelWords.explain (models.py). Nothing is calculated here by simplydata itself: each
function hands the rows explain() has already checked to statsmodels, SciPy, patsy or R and reads
the result. Each choice is checked against R in tests/test_s3a_explain.py.

* weights="precision": precision weights, as R lm(weights =) and glm(weights =): statsmodels WLS
  for numbers and GLM(var_weights=) for the other outcomes. Rows with weight 0 are left out first,
  as R counts them (statsmodels would keep them in the degrees of freedom).
* outcome="yes or no (overdispersed)" with out_of=: quasi-binomial, statsmodels GLM on the shares
  with the tries as var_weights and the Pearson dispersion (scale="X2"), as R glm(family =
  quasibinomial). (A two-column endog gives another dispersion in statsmodels, so it is not used.)
* matched_by="set" with outcome="yes or no": conditional logistic regression, statsmodels
  ConditionalLogit (the exact conditional likelihood), as R survival::clogit(method = "exact").
* show="risk ratios": modified Poisson regression (Zou 2004), statsmodels GLM(Poisson) with
  cov_type="HC0", as R glm(family = poisson) with sandwich::vcovHC(type = "HC0");
  method="log-binomial": statsmodels GLM(Binomial(link=Log())), as R glm(family = binomial(link =
  "log")).
* giving_outliers_less_weight=True: Huber M-estimation, statsmodels RLM(HuberT(), scale_est="mad",
  cov="H1"), as R MASS::rlm() (k = 1.345, MAD scale).
* with_knots=3 with curve_for="hours": a natural cubic spline with 3 inner knots at the quantiles,
  the patsy basis cr(x, knots=..., constraints="center") with the knots placed as R ns() places them
  (quantiles of all the values), the same curves as R splines::ns(x, df = 4).
* show="standardised effects": every number column (and the outcome for numbers) turned into
  z-scores and the model fitted again, as R effectsize::standardize_parameters(method = "refit").
* interval_by="bootstrap": SciPy stats.bootstrap (BCa) with the rows drawn again whole, each time
  refitting the statsmodels model; interval_by="profile": R stats::confint() of the glm (profile
  likelihood); p_value_by="likelihood ratio": each column left out in turn and the deviances
  compared, as R drop1(m, test = "LRT").
* Nagelkerke's and Tjur's pseudo R squared for yes/no: statsmodels pseudo_rsquared("cs") scaled to
  reach 1, and the average chance among yes minus among no, as R performance::r2_nagelkerke() and
  r2_tjur().
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from .._errors import SimplydataError
from .stat_tests import _list_words, _num
from .summaries import _p_clause

Z95 = 1.959963984540054

# show=: which result to show. "odds ratios" is the usual yes/no result.
SHOW = ("odds ratios", "risk ratios", "standardised effects")
SHOW_SPELLINGS = {"standardized effects": "standardised effects", "standardised": "standardised effects",
                  "standardized": "standardised effects", "odds ratio": "odds ratios", "risk ratio": "risk ratios",
                  "relative risks": "risk ratios", "relative risk": "risk ratios",
                  "effects per standard deviation": "standardised effects"}
# method=: how the model is worked out (for now: how risk ratios are found)
METHODS = ("modified poisson", "log-binomial")
METHOD_SPELLINGS = {"modified poisson": "modified poisson", "poisson": "modified poisson",
                    "log binomial": "log-binomial", "log-binomial": "log-binomial"}
# interval_by=: how the 95 % intervals of the effects are worked out
INTERVAL_BY = ("wald", "profile", "bootstrap")
INTERVAL_SPELLINGS = {"profile likelihood": "profile", "profile-likelihood": "profile", "wald": "wald",
                      "bootstrap": "bootstrap", "bca": "bootstrap", "profile": "profile"}
LIKELIHOOD_RATIO = "likelihood ratio"
LR_SPELLINGS = ("likelihood ratio", "likelihood-ratio", "lr", "lrt")
WEIGHT_BELOW = 1.0  # rows whose Huber weight is below 1 were given less weight
KNOTS = range(1, 11)
COMMON_YES = 0.10  # above this share of yes, an odds ratio is far from the risk ratio


def read_choice(option, value, choices, spellings, example):
    """A text option, with its other spellings; a friendly error with the choices otherwise."""
    if value is None:
        return None
    text = value.strip().lower() if isinstance(value, str) else value
    text = spellings.get(text, text)
    if text not in choices:
        listed = ", ".join(f'"{c}"' for c in choices)
        raise SimplydataError(f'{option}= is one of {listed}, not {value!r}.\nFor example, {example}')
    return text


# ---------------------------------------------------------------------------- weights
def read_weights(name, raw, kinds, keep):
    """The weights on the rows kept, after leaving out rows with weight 0 (as R): (weights, keep, left out)."""
    if kinds[name] != "number":
        raise SimplydataError(f'weights="{name}" needs a column of numbers (how much each row counts); "{name}" '
                              "holds text.")
    w = raw[name].astype(float)
    bad = keep & (w < 0)
    if bad.any():
        raise SimplydataError(f'weights="{name}" has {int(bad.sum())} negative values; a weight says how much a row '
                              "counts, so it is 0 or more.")
    zero = keep & (w == 0)
    keep = keep & ~zero
    return w[keep], keep, int(zero.sum())


def weights_line(name, zero):
    left = (f" {zero} {'row' if zero == 1 else 'rows'} with weight 0 {'was' if zero == 1 else 'were'} left out "
            "first, as R does (they add nothing, and R does not count them in the degrees of freedom)." if zero else "")
    return (f'Weights: each row counts as much as its value in "{name}" says (precision weights: a row with weight 2 '
            f"counts like a row whose spread is half as large, as R lm(..., weights = {name}) and glm(..., weights = "
            f"{name}); not frequency weights).{left}")


# ---------------------------------------------------------------------------- splines (with_knots=)
def spline_basis(values, knots, name=""):
    """The natural cubic spline basis with knots inner knots at the quantiles of values, without its constant:
    patsy cr(x, knots=..., constraints="center"), whose curves are those of R splines::ns(x, df = knots + 1).
    The knots are placed as R ns() places them, at the quantiles of all the values (NumPy quantile, R's type 7);
    patsy's own df= takes the quantiles of the distinct values (mgcv's rule), which gives other curves."""
    from patsy import dmatrix

    x = np.asarray(values, dtype=float)
    inner = np.quantile(x, np.linspace(0, 1, knots + 2)[1:-1])
    if len(np.unique(inner)) < knots or inner.min() <= x.min() or inner.max() >= x.max():
        raise SimplydataError(f'"{name}" has too many repeated values to place {knots} different knots between its '
                              "smallest and largest value; use fewer, for example with_knots=2.")
    basis = dmatrix("cr(x, knots=inner, constraints='center') - 1", {"x": x, "inner": inner}, return_type="matrix")
    return np.asarray(basis, dtype=float)


def check_knots(with_knots, curve_for):
    if with_knots is None:
        return None
    if curve_for is None:
        raise SimplydataError('with_knots= goes with curve_for=, the column that follows a curve: '
                              'table.explain("marks", using=["hours", "breakfast"], curve_for="hours", with_knots=3).')
    if isinstance(with_knots, bool) or not isinstance(with_knots, (int, np.integer)) or with_knots not in KNOTS:
        raise SimplydataError(f"with_knots= is a whole number from 1 to 10 (the points where the pieces of the curve "
                              f"join), not {with_knots!r}; 3 is a good start.")
    return int(with_knots)


# ---------------------------------------------------------------------------- standardised effects
def standardise(raw, keep, names):
    """Each number column of names as z-scores on the rows kept (mean 0, standard deviation 1 with n - 1, as R
    scale() and effectsize); gives back the new raw values and each column's mean and standard deviation."""
    out, spread = dict(raw), {}  # [D] z-scores before the statsmodels refit (tests/test_no_own_methods.py)
    for name in names:
        values = raw[name].astype(float)
        used = values[keep]
        mean, sd = float(np.mean(used)), float(np.std(used, ddof=1))
        if not sd > 0:
            raise SimplydataError(f'"{name}" has the same value in every row used, so it has no standard deviation '
                                  "to standardise by.")
        out[name] = (values - mean) / sd
        spread[name] = sd
    return out, spread


def standardised_lines(model):
    """The line that says what one standard deviation is, and the Greenland sentence."""
    spread = model["standardised"]
    shown = _list_words(f'"{name}" {_num(sd)}' for name, sd in spread.items())
    return [f"One standard deviation, in these rows: {shown}.",
            "Note: standardised effects depend on how spread out the values are in this sample, so they are not a "
            "measure of importance and cannot be compared across studies with other spreads (Greenland, "
            "Schlesselman & Criqui 1986)."]


# ---------------------------------------------------------------------------- robust regression (Huber)
def fit_huber(X, y):
    """statsmodels RLM with Huber's weights (k = 1.345), the scale by the MAD, Huber's H1 covariance: R MASS::rlm()."""
    import statsmodels.api as sm

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = sm.RLM(y, X, M=sm.robust.norms.HuberT()).fit(scale_est="mad", cov="H1", maxiter=200, tol=1e-10)
    return {"beta": np.asarray(result.params, dtype=float), "cov": np.asarray(result.cov_params(), dtype=float),
            "fitted": np.asarray(result.fittedvalues, dtype=float), "scale": float(result.scale),
            "weights": np.asarray(result.weights, dtype=float), "df": len(y) - X.shape[1]}


def huber_lines(model, rows):
    """The rows given less weight, by their row number in the whole table (from 1)."""
    weights = model["fit"]["weights"]
    low = np.flatnonzero(weights < WEIGHT_BELOW - 1e-9)
    if not len(low):
        return ["No row was given less weight: no value is far from the model."]
    order = low[np.argsort(weights[low])]
    shown = ", ".join(f"row {rows[i] + 1} (weight {weights[i]:.2f})" for i in order[:8])
    more = f", and {len(order) - 8} more" if len(order) > 8 else ""
    return [f"Rows given less weight ({len(order)} of {len(weights)}; 1 is full weight): {shown}{more}."]


# ---------------------------------------------------------------------------- conditional logistic regression
def fit_conditional_logit(X, y, sets):
    """statsmodels ConditionalLogit (the exact conditional likelihood), as R survival::clogit(method = "exact")."""
    from statsmodels.discrete.conditional_models import ConditionalLogit

    model = ConditionalLogit(y, X, groups=sets)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        first = model.fit(method="bfgs", maxiter=1000, disp=0)
        result = model.fit(start_params=first.params, method="newton", maxiter=100, disp=0)
    k = X.shape[1]
    return {"beta": np.asarray(result.params, dtype=float), "cov": np.asarray(result.cov_params(), dtype=float),
            "loglik": float(result.llf), "llnull": float(model.loglike(np.zeros(k))), "model": model}


def informative_sets(y, sets):
    """Sets with at least one case and one control (the others add nothing to the conditional likelihood)."""
    keep = np.zeros(len(y), dtype=bool)
    for s in dict.fromkeys(sets.tolist()):
        here = sets == s
        if 0 < y[here].sum() < here.sum():
            keep |= here
    return keep


def constant_within_sets(X, labels, sets):
    """The model columns that do not change within any set: their effect cannot be estimated."""
    out = []
    for j in range(X.shape[1]):
        if all(np.ptp(X[sets == s, j]) == 0 for s in dict.fromkeys(sets.tolist())):
            out.append(labels[j])
    return out


# ---------------------------------------------------------------------------- risk ratios
def fit_risk_ratios(X, y, method):
    """Modified Poisson (statsmodels GLM Poisson, HC0) or log-binomial (GLM Binomial with a log link)."""
    import statsmodels.api as sm

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with np.errstate(all="ignore"):
            if method == "modified poisson":
                result = sm.GLM(y, X, family=sm.families.Poisson()).fit(method="IRLS", tol=1e-12, maxiter=100,
                                                                         cov_type="HC0")
            else:
                result = sm.GLM(y, X, family=sm.families.Binomial(link=sm.families.links.Log())).fit(
                    method="IRLS", tol=1e-12, maxiter=200)
    fitted = np.asarray(result.fittedvalues, dtype=float)
    if method == "log-binomial" and (not result.converged or not np.all(np.isfinite(result.params))
                                     or np.any(fitted >= 1 - 1e-9)):
        raise SimplydataError(
            'The log-binomial model did not converge: with a log link some predicted chances reach 1 or more, which '
            "often happens with this model (R glm(family = binomial(link = \"log\")) stops too). Leave out method= to "
            'get risk ratios by modified Poisson regression, which always converges: show="risk ratios".')
    out = {"beta": np.asarray(result.params, dtype=float), "cov": np.asarray(result.cov_params(), dtype=float),
           "fitted": fitted, "df": len(y) - X.shape[1], "converged": bool(result.converged),
           "loglik": float(result.llf), "llnull": float(result.llnull), "deviance": float(result.deviance),
           "null_deviance": float(result.null_deviance)}
    if method == "modified poisson":
        out["robust"] = True
    else:
        out["link"] = "log"
    return out


def common_yes_note(share):
    return (f"Note: {round(share * 100)} % of the rows are yes, so an odds ratio is not a risk ratio here (it is "
            "further from 1); show=\"risk ratios\" gives risk ratios.")


# ---------------------------------------------------------------------------- Nagelkerke and Tjur
def other_pseudo(result, y):
    """(Nagelkerke, Tjur) of a logistic regression on 0/1 rows: statsmodels' Cox-Snell pseudo R squared scaled by
    its largest possible value, and the average fitted chance among yes minus among no."""
    n = len(y)  # [D] display arithmetic on statsmodels' output (tests/test_no_own_methods.py)
    cox_snell = float(result.pseudo_rsquared(kind="cs"))
    nagelkerke = cox_snell / (1 - math.exp(2 * float(result.llnull) / n))
    fitted = np.asarray(result.fittedvalues, dtype=float)
    tjur = float(np.mean(fitted[y == 1]) - np.mean(fitted[y == 0]))
    return nagelkerke, tjur


# ---------------------------------------------------------------------------- likelihood-ratio p-values
def lr_p_values(model, refit):
    """A likelihood-ratio p-value for each one-column term not inside an interaction (as R drop1(m, test = "LRT"));
    NaN for the intercept, group columns with several columns and terms inside an interaction. refit(X) gives the
    deviance of the model fitted to the columns of X."""
    from scipy import stats

    terms, owner, X = model["terms"], np.asarray(model["owner"]), model["X"]
    out = np.full(X.shape[1], math.nan)
    full = model["fit"]["deviance"]
    for index, term in enumerate(terms):
        columns = np.flatnonzero(owner == index)
        if len(columns) != 1 or any(set(term) < set(other) for other in terms):
            continue
        change = refit(np.delete(X, columns, axis=1)) - full
        out[columns[0]] = float(stats.chi2.sf(max(change, 0.0), 1))
    return out


# ---------------------------------------------------------------------------- bootstrap intervals
def bootstrap_effects(model, refit, resamples, seed):
    """BCa 95 % intervals of every effect from SciPy stats.bootstrap: the rows are drawn again whole (with
    replacement) resamples times, and refit(rows) fits the same statsmodels model to them."""
    from scipy import stats

    from .resampling import check_seed_and_count

    check_seed_and_count(seed, resamples, "resamples")
    n = model["n"]

    def statistic(rows):
        return refit(np.asarray(rows, dtype=int))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with np.errstate(all="ignore"):
            result = stats.bootstrap((np.arange(n),), statistic, n_resamples=int(resamples), confidence_level=0.95,
                                     method="BCa", vectorized=False, rng=np.random.default_rng(int(seed)))
    return (np.asarray(result.confidence_interval.low, dtype=float),
            np.asarray(result.confidence_interval.high, dtype=float))


def bootstrap_line(resamples, seed, n):
    few = (" With fewer than 20 rows the bootstrap interval is often too narrow; treat it as a rough guide."
           if n < 20 else "")
    return (f"Intervals: 95 % bootstrap intervals (bias-corrected and accelerated, BCa): the {n} rows were drawn "
            f"again at random, whole and with replacement, {int(resamples)} times (with_seed={int(seed)}), and the "
            "model was fitted to each new table (SciPy stats.bootstrap, as R boot::boot.ci(type = \"bca\") on "
            "car::Boot()). The p-values are the model's usual ones." + few)


# ---------------------------------------------------------------------------- p-value sentences
def p_words(p, null):
    return _p_clause(p, null)


__all__ = ["SHOW", "METHODS", "INTERVAL_BY", "read_choice", "read_weights", "weights_line", "spline_basis",
           "check_knots", "standardise", "standardised_lines", "fit_huber", "huber_lines", "fit_conditional_logit",
           "informative_sets", "constant_within_sets", "fit_risk_ratios", "common_yes_note", "other_pseudo",
           "lr_p_values", "bootstrap_effects", "bootstrap_line"]
