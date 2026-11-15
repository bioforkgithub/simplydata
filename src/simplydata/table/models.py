"""Models that explain one column from several others. They never change the table
(except add_predicted_column, which adds one column and can be undone).

table.explain("marks", using=["hours", "breakfast"]) fits one model and prints, for each
column used, how big its effect is, with a 95 % confidence interval and a p-value in plain
words. It gives back a table with one row per term (the model-level values are printed).

Choices (the same defaults as R, so results can be checked there):

* using=: column names. A column of numbers gets a slope. A text (or True/False) column is a
  group column: each group is compared with the first group in sorted order, the baseline
  (dummy coding, as R treatment contrasts). "hours * breakfast" means both columns and their
  interaction, as in an R formula; "hours : breakfast" means the interaction only. The
  coding of a group column inside an interaction follows R's rule (full coding when the rest
  of the term is not in the model), so the columns are the same as R model.matrix().
* outcome="numbers": linear model by least squares (R lm()), t-based 95 % intervals,
  R squared, adjusted R squared and the overall F test (R summary.lm()).
* outcome="yes or no": logistic regression (R glm(family = binomial)), fitted by iteratively
  reweighted least squares. Odds ratios with 95 % Wald intervals (R confint.default()) and
  Wald z p-values (R summary.glm()). The model as a whole: likelihood-ratio test against the
  model with no columns.
* outcome="counts": Poisson regression (R glm(family = poisson)), rate ratios. When the
  residual deviance is more than 1.5 times its degrees of freedom a note says the counts
  vary more than Poisson allows and suggests outcome="counts (overdispersed)": quasi-Poisson
  (R glm(family = quasipoisson)), the same rate ratios with standard errors scaled by the
  Pearson dispersion, t-based p-values as R summary.glm(), Wald intervals as
  R confint.default(). simplydata never switches by itself. outcome="counts that vary a lot":
  negative binomial, as R MASS::glm.nb(): theta by maximum likelihood (statsmodels
  NegativeBinomial), then the GLM with theta held for the standard errors, as glm.nb reports
  them. outcome="positive numbers": Gamma GLM with a log link (R glm(family = Gamma(link =
  "log"))), t-tests and the Pearson dispersion as R summary.glm(). time= adds log(time) as an
  offset (rates); out_of= fits successes out of trials (R cbind(yes, no)).
* Group columns with 3 or more groups (and interactions with them) also get one test for the
  whole column, as R drop1(): an F test for least squares and quasi-Poisson
  (drop1(test = "F")), a likelihood-ratio chi-square test for logistic and Poisson models
  (drop1(test = "Chisq")). Like drop1(), a column that is also part of an interaction is not
  tested alone. (This equals car::Anova() type II when there are no interactions.)
* grouped_by="school": linear mixed model with a random intercept for each group, fitted by
  REML (R lme4::lmer(REML = TRUE)): statsmodels MixedLM finds the two variances, and the fixed
  effects and their standard errors follow by generalised least squares, as lme4 fixef() and
  vcov(). P-values are Wald z-tests and intervals Wald intervals
  (R confint(method = "Wald")); R lmerTest gives Satterthwaite
  t-tests instead, which give slightly larger p-values when there are few groups. Group
  columns with 3 or more groups get a Wald chi-square test. The share of the differences
  that lies between the groups is the intraclass correlation (ICC). With outcome="yes or no"
  or "counts", grouped_by= fits a generalised linear mixed model with R lme4::glmer() itself
  (Laplace approximation; simplydata[r] and R), odds or rate ratios with Wald intervals.
* empty_cells="multiple imputation": empty cells in number columns are filled in 20 times by
  chained equations with predictive mean matching (statsmodels MICEData, 5 donors as R
  mice()), the model is fitted to each filled-in table, and the results are pooled with
  Rubin's rules, with the Barnard-Rubin degrees of freedom (as R mice::pool()). The filling
  is random: seed= fixes it.

Notes, never silent switches: residuals not bell-shaped (least squares), strongly linked
columns (variance inflation factor above 5), too few rows (or too few yes/no events) per
effect, complete separation (logistic), overdispersion (Poisson).
"""

from __future__ import annotations

import contextlib
import io
import itertools
import math
import warnings

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, column_error, friendly
from .stat_tests import _label, _list_words, _num, _shape_notes, _skipped_note, _whole
from .summaries import _p_words

OUTCOMES = ("numbers", "yes or no", "counts", "counts (overdispersed)", "counts that vary a lot", "positive numbers")
COUNT_OUTCOMES = ("counts", "counts (overdispersed)", "counts that vary a lot")
OUTCOMES = OUTCOMES + ("ordered groups", "groups", "shares", "counts with many zeros")
# link=: the first link of each outcome is the default (R's default for that family)
LINKS = {"yes or no": ("logit", "probit", "cloglog"), "counts": ("log", "identity", "sqrt"),
         "positive numbers": ("log", "inverse", "identity")}
EMPTY_CELLS = ("leave out", "multiple imputation")
# options for grouped_by=: p-values of a mixed model, the kind of effects, the correlation within groups (GEE)
P_VALUE_BY = {"wald": "wald", "wald z": "wald", "z": "wald", "satterthwaite": "satterthwaite",
              "few groups": "satterthwaite"}
EFFECTS = ("for the average group", "for the whole population")
EFFECT_SPELLINGS = {"average group": "for the average group", "mixed": "for the average group",
                    "whole population": "for the whole population", "population": "for the whole population",
                    "gee": "for the whole population"}
WITHIN_GROUPS = {"alike": "exchangeable", "in time order": "ar1", "independent": "independence"}
WITHIN_SPELLINGS = {"exchangeable": "alike", "ar1": "in time order", "ar-1": "in time order",
                    "independence": "independent"}
IMPUTATIONS = 20  # filled-in tables for multiple imputation
PMM_DONORS = 5  # as R mice() predictive mean matching
BURN_IN, BETWEEN = 10, 3  # imputation cycles before the first filled-in table, and between tables
VIF_LIMIT = 5.0
ROWS_PER_EFFECT = 10
OVERDISPERSION = 1.5
Z95 = 1.959963984540054
YES_NO_PAIRS = (("yes", "no"), ("true", "false"), ("1", "0"), ("1.0", "0.0"), ("y", "n"))
EXAMPLE = 'with sdata.example("school"): table.explain("marks", using=["hours", "breakfast"])'
INTERCEPT = "(intercept)"
KINDS = {"numbers": "lm", "yes or no": "binomial", "counts": "poisson", "counts (overdispersed)": "quasipoisson",
         "counts that vary a lot": "negbin", "positive numbers": "gamma"}
RATIO_WORDS = {"yes or no": "odds ratio", "counts": "rate ratio", "counts (overdispersed)": "rate ratio",
               "counts that vary a lot": "rate ratio", "positive numbers": "ratio of averages"}


def _exp(x) -> float:
    """exp() that gives infinity instead of an error for a huge value (complete separation)."""
    return math.exp(x) if x < 709 else math.inf


def _missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _sort_key(value):
    return (str(type(value)), value)


def _quoted(name) -> str:
    return f'"{name}"'


def _r_name(name: str) -> str:
    plain = name.replace("_", "").replace(".", "").isalnum() and not name[0].isdigit()
    return name if plain else f"`{name}`"


def _quiet(func, *args):
    """Run func without printing (the filled-in tables of multiple imputation)."""
    with contextlib.redirect_stdout(io.StringIO()):
        return func(*args)


# ---------------------------------------------------------------------------- reading using=
def _read_using(step: str, using, columns) -> tuple[list[tuple], list[str]]:
    """using= as a list of terms (tuples of column names, in R order) and the R formula pieces."""
    if isinstance(using, str):
        items = [using]
    elif isinstance(using, (list, tuple)) and using:
        items = list(using)
    else:
        raise SimplydataError(f"{step}() needs using= with the columns that explain it.\nFor example, {EXAMPLE}")
    terms, pieces = [], []
    for item in items:
        if not isinstance(item, str) or not item.strip():
            raise SimplydataError(f"Each column in using= is a name in quotes, not {item!r}.\nFor example, {EXAMPLE}")
        text = item.strip()
        if text in columns:
            parts, kind = [text], "main"
        elif "*" in text:
            parts, kind = [p.strip().strip("`") for p in text.split("*")], "cross"
        elif ":" in text:
            parts, kind = [p.strip().strip("`") for p in text.split(":")], "only"
        else:
            parts, kind = [text.strip("`")], "main"
        for part in parts:
            if part not in columns:
                raise column_error(part, columns)
        if len(set(parts)) < len(parts):
            raise SimplydataError(f'"{item}" names the same column twice.')
        sign = " * " if kind == "cross" else ":"
        pieces.append(sign.join(_r_name(p) for p in parts))
        if kind == "cross":
            for size in range(1, len(parts) + 1):
                terms.extend(itertools.combinations(parts, size))
        else:
            terms.append(tuple(parts))
    unique, seen = [], set()
    for term in terms:
        if frozenset(term) not in seen:
            seen.add(frozenset(term))
            unique.append(term)
    unique.sort(key=len)  # R puts main effects first, then two-way, then three-way terms
    return unique, pieces


def _design(data: dict, kinds: dict, levels: dict, terms: list[tuple]):
    """The model matrix exactly as R model.matrix() with treatment contrasts.

    Gives back X, the column labels, which term owns each column (-1 for the intercept)
    and, per column, its parts (label, (group column, group) or None) for the sentences."""
    n = len(next(iter(data.values()))) if data else 0
    term_set = {frozenset(t) for t in terms}
    columns, labels, owner, parts_of = [np.ones(n)], [INTERCEPT], [-1], [[]]
    for index, term in enumerate(terms):
        pieces = []
        for name in term:
            if kinds[name] == "number":
                pieces.append([(name, data[name], None)])
                continue
            rest = frozenset(term) - {name}
            used = levels[name] if (rest and rest not in term_set) else levels[name][1:]
            values = data[name]
            pieces.append([(f"{name} ({_label(level)})", np.array([v == level for v in values], dtype=float),
                            (name, level)) for level in used])
        for combo in itertools.product(*reversed(pieces)):  # the first column varies fastest, as R
            combo = combo[::-1]
            vector = np.ones(n)
            for _, values, _ in combo:
                vector = vector * values
            columns.append(vector)
            labels.append(" : ".join(c[0] for c in combo))
            owner.append(index)
            parts_of.append([(c[0], c[2]) for c in combo])
    return np.column_stack(columns), labels, np.array(owner), parts_of


# ---------------------------------------------------------------------------- the fits
def _least_squares(X, y):
    """Least squares (R lm()) with statsmodels OLS: beta, unscaled covariance, fitted values, RSS."""
    from statsmodels.regression.linear_model import OLS

    result = OLS(y, X).fit(method="qr")
    return (np.asarray(result.params), np.asarray(result.normalized_cov_params), np.asarray(result.fittedvalues),
            float(result.ssr))


def _glm(X, y, kind, scale=None, exposure=None, trials=None, alpha=None, link=None):
    """A GLM with statsmodels GLM, fitted by IRLS as R glm.fit(): binomial (logit), Poisson (log),
    negative binomial with a known alpha = 1 / theta (log), or Gamma (log). exposure= is the
    person-time (R offset = log(time)); trials= the number of tries for successes out of trials
    (R cbind(successes, failures))."""
    import statsmodels.api as sm

    links = sm.families.links
    chosen = {"probit": links.Probit, "cloglog": links.CLogLog, "identity": links.Identity, "sqrt": links.Sqrt,
              "inverse": links.InversePower, "log": links.Log, "logit": links.Logit}.get(link)
    if kind == "binomial":
        family = sm.families.Binomial(link=chosen()) if chosen else sm.families.Binomial()
    elif kind == "gamma" and chosen:
        family = sm.families.Gamma(link=chosen())
    elif kind == "poisson" and chosen:
        family = sm.families.Poisson(link=chosen())
    elif kind == "negbin":
        family = sm.families.NegativeBinomial(alpha=alpha)
    elif kind == "gamma":
        family = sm.families.Gamma(link=sm.families.links.Log())
    else:
        family = sm.families.Poisson()
    endog = y if trials is None else np.column_stack([y, trials - y])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # perfect separation and step warnings: the notes say it in words
        with np.errstate(all="ignore"):
            return sm.GLM(endog, X, family=family, exposure=exposure).fit(method="IRLS", tol=1e-10, maxiter=50,
                                                                         scale=scale)


def _negative_binomial(X, y, exposure=None):
    """R MASS::glm.nb(): theta by maximum likelihood (statsmodels NegativeBinomial, NB2), then the
    GLM with that theta held, whose standard errors are the ones glm.nb reports."""
    from statsmodels.discrete.discrete_model import NegativeBinomial

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with np.errstate(all="ignore"):
            full = NegativeBinomial(y, X, exposure=exposure, loglike_method="nb2").fit(
                method="bfgs", maxiter=1000, gtol=1e-10, disp=0)
            full = NegativeBinomial(y, X, exposure=exposure, loglike_method="nb2").fit(
                start_params=full.params, method="newton", maxiter=100, disp=0)
    alpha = float(full.params[-1])
    return alpha, full


def _glmer(X, y, groups, family, slopes=()):
    """A generalised linear mixed model with a random intercept per group: R lme4::glmer() itself
    (Laplace approximation, R's defaults), on the same model matrix as explain() builds."""
    from .._r import r_call

    random = "(1 + Z | g)" if slopes else "(1 | g)"
    extra = {"Z": np.asarray(X, dtype=float)[:, list(slopes)]} if slopes else {}
    out = r_call(
        f"m <- lme4::glmer(y ~ 0 + X + {random}, family = {family}); vc <- as.data.frame(lme4::VarCorr(m)); "
        "list(beta = unname(lme4::fixef(m)), cov = unname(as.matrix(stats::vcov(m))), "
        "between = as.numeric(lme4::VarCorr(m)$g[1]), is_cor = !is.na(vc$var2), vcov = vc$vcov, "
        "sdcor = vc$sdcor, loglik = as.numeric(stats::logLik(m)), "
        "aic = stats::AIC(m), fitted = unname(stats::fitted(m)), singular = lme4::isSingular(m), "
        "trouble = length(m@optinfo$conv$lme4$messages) > 0)",
        packages=("lme4",), what="A mixed model for yes/no or counts (R lme4::glmer())",
        python_note="statsmodels has only Bayesian approximations for these (BinomialBayesMixedGLM), which give "
                    "other numbers",
        y=np.asarray(y, dtype=float), X=np.asarray(X, dtype=float), g=np.asarray(groups, dtype=object), **extra)
    k = X.shape[1]
    return {"beta": np.asarray(out["beta"], dtype=float),
            "cov": np.asarray(out["cov"], dtype=float).reshape(k, k),
            "fitted": np.asarray(out["fitted"], dtype=float), "between": float(out["between"][0]),
            "loglik": float(out["loglik"][0]), "aic": float(out["aic"][0]), "family": family,
            "singular": bool(out["singular"][0]), "trouble": bool(out["trouble"][0]),
            "converged": not bool(out["trouble"][0]), "parts": _variance_parts(out, len(slopes))}


def _variance_parts(out, slopes):
    """lme4 VarCorr() as R's as.data.frame() gives it, read by position: the variance of each group's
    starting level, of each own slope, and the correlations between them."""
    is_cor = np.atleast_1d(out["is_cor"]).astype(bool)
    vcov, sdcor = np.atleast_1d(out["vcov"]).astype(float), np.atleast_1d(out["sdcor"]).astype(float)
    k = slopes + 1
    variances = vcov[:k]
    correlations = [float(sdcor[i]) for i in range(k, len(vcov)) if is_cor[i]]
    return {"variances": [float(v) for v in variances], "correlations": correlations}


def _gee(X, y, groups, outcome, corr):
    """Effects for the whole population: statsmodels GEE with a robust (sandwich) covariance, the
    scale without a degrees-of-freedom correction (ddof_scale=0), as R geepack::geeglm()."""
    import statsmodels.api as sm

    family = {"numbers": sm.families.Gaussian(), "yes or no": sm.families.Binomial(),
              "counts": sm.families.Poisson()}[outcome]
    structure = sm.cov_struct.Exchangeable() if corr == "exchangeable" else sm.cov_struct.Independence()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = sm.GEE(y, X, groups=groups, family=family, cov_struct=structure).fit(
            maxiter=200, ctol=1e-10, ddof_scale=0)
    alpha = float(np.atleast_1d(structure.dep_params)[0]) if corr == "exchangeable" else 0.0
    return {"beta": np.asarray(result.params), "cov": np.asarray(result.cov_robust),
            "fitted": np.asarray(result.fittedvalues), "alpha": alpha, "scale": float(result.scale),
            "trouble": any("converge" in str(w.message).lower() for w in caught)}


# ---------------------------------------------------------------------------- the words
class ModelWords:
    # ------------------------------------------------------------------ gathering the data
    def _model_parts(self, step, column, using, outcome, grouped_by, empty_cells, time=None, out_of=None):
        """Check every input and gather the columns (empty cells kept, as masks)."""
        self._need_name(step, "the column to explain", column, EXAMPLE)
        self._need_columns(column)
        self._check_choice(step, "outcome", outcome, OUTCOMES)
        self._check_choice(step, "empty_cells", empty_cells, EMPTY_CELLS)
        terms, pieces = _read_using(step, using, self._columns)
        variables = list(dict.fromkeys(name for term in terms for name in term))
        if column in variables:
            raise SimplydataError(f'"{column}" cannot both be explained and be in using=.\nFor example, {EXAMPLE}')
        if grouped_by is not None:
            self._need_name(step, "grouped_by=", grouped_by, EXAMPLE)
            self._need_columns(grouped_by)
            if grouped_by == column or grouped_by in variables:
                raise SimplydataError(f'"{grouped_by}" cannot be the grouped_by= column and also be explained or '
                                      "be in using=.")
            if outcome not in ("numbers", "yes or no", "counts"):
                raise SimplydataError(
                    f'grouped_by= works with outcome="numbers", "yes or no" or "counts", not "{outcome}". For counts '
                    'that vary more than Poisson allows, use outcome="counts": the groups take up some of that '
                    "extra spread."
                )
            if empty_cells != "leave out":
                raise SimplydataError(
                    'empty_cells="multiple imputation" cannot be used with grouped_by= yet: filling in empty cells '
                    'would need to respect the groups. Use the default empty_cells="leave out".'
                )
        for option, value in (("time=", time), ("out_of=", out_of)):
            if value is None:
                continue
            self._need_name(step, option, value, EXAMPLE)
            self._need_columns(value)
            if value == column or value in variables or value == grouped_by:
                raise SimplydataError(f'"{value}" cannot be {option} and also be explained, in using= or grouped_by=.')
        if time is not None and outcome not in COUNT_OUTCOMES:
            raise SimplydataError(f'time= (the time each row was followed) is for counts: outcome="counts", '
                                  f'"counts (overdispersed)" or "counts that vary a lot", not "{outcome}".')
        if out_of is not None and outcome != "yes or no":
            raise SimplydataError('out_of= (the number of tries in each row) goes with outcome="yes or no": the '
                                  'column to explain then holds the number of yes out of that many tries.')
        if (time is not None or out_of is not None) and (grouped_by is not None or empty_cells != "leave out"):
            raise SimplydataError("time= and out_of= cannot be used with grouped_by= or multiple imputation yet.")
        frame = self._frame
        names = [column] + variables + ([grouped_by] if grouped_by is not None else [])
        names += [v for v in (time, out_of) if v is not None]
        raw, missing, kinds = {}, {}, {}
        for name in names:
            dtype = frame.schema[name]
            if dtype.is_temporal():
                raise SimplydataError(f'"{name}" holds dates or times, which {step}() cannot use. Make a number '
                                      "from them first, for example with table.add_date_part_column().")
            if dtype.is_numeric():
                values = frame[name].cast(nw.Float64).to_numpy().astype(float)
                raw[name], missing[name], kinds[name] = values, np.isnan(values), "number"
            else:
                values = frame[name].to_list()
                gone = np.array([_missing(v) for v in values], dtype=bool)
                raw[name], missing[name], kinds[name] = np.array(values, dtype=object), gone, "group"
        if grouped_by is not None:
            kinds[grouped_by] = "group"
        return terms, pieces, variables, raw, missing, kinds

    @staticmethod
    def _outcome_values(column, outcome, values, kind):
        """The outcome as floats (yes = 1) and the words saying which value counts as yes."""
        if outcome != "yes or no":
            if kind != "number":
                hint = ' For a yes/no column use outcome="yes or no".' if len(set(values.tolist())) == 2 else ""
                raise SimplydataError(f'outcome="{outcome}" needs "{column}" to hold numbers; it holds text.{hint}')
            y = values.astype(float)
            if outcome == "positive numbers":
                if np.any(y <= 0):
                    raise SimplydataError(f'outcome="positive numbers" needs numbers above 0 in "{column}"; '
                                          f"{int((y <= 0).sum())} are 0 or below.")
            elif outcome != "numbers" and (np.any(y < 0) or np.any(y != np.round(y))):
                raise SimplydataError(f'outcome="{outcome}" needs whole numbers of 0 or more in "{column}" (counts).')
            if outcome == "numbers" and set(np.unique(y).tolist()) == {0.0, 1.0}:
                print(f'Note: "{column}" holds only 0 and 1; for a yes/no outcome use outcome="yes or no".')
            return y, None
        distinct = sorted(set(values.tolist()), key=_sort_key)
        if len(distinct) != 2:
            found = ("only " + _list_words(f'"{_label(v)}"' for v in distinct)) if len(distinct) < 2 else (
                f"{len(distinct)} different values")
            raise SimplydataError(f'outcome="yes or no" needs "{column}" to hold exactly 2 different values; it has '
                                  f"{found}.")
        lowered = {str(v).strip().lower(): v for v in distinct}
        yes = None
        for word, other in YES_NO_PAIRS:
            if set(lowered) == {word, other}:
                yes = lowered[word]
                why = f'counted as yes: "{column}" = "{_label(yes)}"'
        if yes is None:
            yes = distinct[1]
            why = (f'counted as yes: "{column}" = "{_label(yes)}" (the second value in sorted order, as R; '
                   f'"{_label(distinct[0])}" is no)')
        return np.array([v == yes for v in values], dtype=float), why

    @staticmethod
    def _successes(column, out_of, raw, kinds, keep):
        """Successes out of trials: the yes counts, the words, and the trials (R cbind(yes, no))."""
        if kinds[column] != "number" or kinds[out_of] != "number":
            raise SimplydataError(f'With out_of=, "{column}" holds the number of yes and "{out_of}" the number of '
                                  "tries, both as numbers.")
        y, trials = raw[column][keep].astype(float), raw[out_of][keep].astype(float)
        if np.any(y < 0) or np.any(y != np.round(y)) or np.any(trials != np.round(trials)):
            raise SimplydataError(f'"{column}" and "{out_of}" need whole numbers of 0 or more.')
        if np.any(y > trials):
            raise SimplydataError(f'"{column}" is more than "{out_of}" in {int((y > trials).sum())} rows; the number '
                                  "of yes cannot be more than the number of tries.")
        if np.any(trials <= 0):
            raise SimplydataError(f'"{out_of}" needs at least 1 try in every row.')
        return y, f'counted as yes: the number in "{column}" out of "{out_of}" tries', trials

    # ------------------------------------------------------------------ fitting one model
    @staticmethod
    def _fit_one(kind, X, y, groups=None, family="binomial", exposure=None, trials=None, link=None, grouping=None):
        grouping = grouping or {}
        if kind == "gee":
            from .models_r import geeglm_r

            if grouping["corr"] == "ar1":  # statsmodels' AR-1 estimator differs from geepack's: R itself
                out = geeglm_r(grouping["model"], "ar1")
                k = X.shape[1]
                return {"beta": np.asarray(out["beta"], dtype=float),
                        "cov": np.asarray(out["cov"], dtype=float).reshape(k, k),
                        "fitted": np.asarray(out["fitted"], dtype=float),
                        "alpha": float(np.atleast_1d(out["alpha"])[0]),
                        "scale": float(np.atleast_1d(out["scale"])[0]) if grouping["outcome"] == "numbers" else 1.0,
                        "trouble": False}
            return _gee(X, y, groups, grouping["outcome"], grouping["corr"])
        if kind == "mixed" and (grouping.get("slope_cols") or grouping.get("satterthwaite")):
            from .models_r import lmer_r

            out = lmer_r(grouping["model"], grouping.get("slope_cols", ()), grouping.get("satterthwaite"),
                         grouping.get("tested", ()))
            k = X.shape[1]
            parts = _variance_parts(out, len(grouping.get("slope_cols", ())))
            vcov = np.atleast_1d(out["vcov"]).astype(float)
            fit = {"beta": np.asarray(out["beta"], dtype=float),
                   "cov": np.asarray(out["cov"], dtype=float).reshape(k, k),
                   "fitted": np.asarray(out["fitted"], dtype=float), "between": parts["variances"][0],
                   "within": float(vcov[-1]), "trouble": bool(np.atleast_1d(out["trouble"])[0]),
                   "singular": bool(np.atleast_1d(out["singular"])[0]), "parts": parts, "by_r": True}
            if grouping.get("satterthwaite"):
                fit["satt"] = {key: np.atleast_1d(out[key]).astype(float) for key in
                               ("df", "low", "high", "p", "f", "numdf", "dendf", "fp")}
            return fit
        if kind == "lm":
            beta, unscaled, fitted, rss = _least_squares(X, y)
            df = len(y) - X.shape[1]
            return {"beta": beta, "cov": unscaled * (rss / df), "fitted": fitted, "rss": rss, "df": df}
        if kind == "mixed":
            from statsmodels.regression.mixed_linear_model import MixedLM
            from statsmodels.tools.sm_exceptions import ConvergenceWarning

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                # Powell first, then L-BFGS: reaches the REML optimum as closely as lme4 does
                result = MixedLM(y, X, groups=groups).fit(reml=True, method=["powell", "lbfgs"])
            trouble = any(issubclass(w.category, ConvergenceWarning) for w in caught) or not result.converged
            between, within = max(float(np.asarray(result.cov_re)[0, 0]), 0.0), float(result.scale)
            # lme4 vcov(): the fixed-effects block of the information alone (statsmodels' cov_params()
            # inverts the whole Hessian, variances included, which gives slightly different errors)
            k = X.shape[1]
            hessian = result.model.hessian(result.params_object)
            hessian = hessian[0] if isinstance(hessian, tuple) else hessian
            return {"beta": np.asarray(result.fe_params), "cov": np.linalg.inv(-np.asarray(hessian)[:k, :k]),
                    "fitted": np.asarray(result.fittedvalues), "between": between, "within": within,
                    "trouble": trouble}
        if kind == "glmm":
            return _glmer(X, y, groups, family, grouping.get("slope_cols", ()))
        alpha, full = (None, None)
        if kind == "negbin":
            alpha, full = _negative_binomial(X, y, exposure)
        family = {"binomial": "binomial", "negbin": "negbin", "gamma": "gamma"}.get(kind, "poisson")
        result = _glm(X, y, family, scale="X2" if kind in ("quasipoisson", "gamma") else None, exposure=exposure,
                      trials=trials, alpha=alpha, link=link)
        df = len(y) - X.shape[1]
        out = {"beta": np.asarray(result.params), "cov": np.asarray(result.cov_params()),
               "fitted": np.asarray(result.fittedvalues), "deviance": float(result.deviance),
               "null_deviance": float(result.null_deviance), "df": df, "converged": bool(result.converged),
               "loglik": float(result.llf), "aic": float(result.aic)}
        if kind in ("quasipoisson", "gamma"):
            out["dispersion"] = float(result.scale)
        if kind == "negbin":  # as R glm.nb: the log-likelihood and AIC count theta as one more value
            out.update(alpha=alpha, theta=1 / alpha, loglik=float(full.llf),
                       aic=float(-2 * full.llf + 2 * (X.shape[1] + 1)))
        out.update(exposure=exposure, trials=trials, link=link)
        return out

    def _fit_model(self, step, column, outcome, grouped_by, terms, variables, raw, kinds, keep, time=None,
                   out_of=None, link=None, grouping=None):
        """Fit the model on the rows in keep; a dict with everything the printing needs."""
        n = int(keep.sum())
        if n == 0:
            raise SimplydataError(f"{step}() found no rows with a value in every column it needs.")
        exposure = trials = None
        if out_of is not None:
            y, yes_words, trials = self._successes(column, out_of, raw, kinds, keep)
        else:
            y, yes_words = self._outcome_values(column, outcome, raw[column][keep], kinds[column])
        if time is not None:
            if kinds[time] != "number":
                raise SimplydataError(f'time= needs "{time}" to hold numbers (the time each row was followed).')
            exposure = raw[time][keep].astype(float)
            if np.any(exposure <= 0):
                raise SimplydataError(f'time= needs times above 0 in "{time}"; {int((exposure <= 0).sum())} are 0 '
                                      "or below.")
        data = {name: raw[name][keep] for name in variables}
        levels = {}
        for name in variables:
            if kinds[name] == "group":
                found = sorted(set(data[name].tolist()), key=_sort_key)
                if len(found) < 2:
                    which = f' ("{_label(found[0])}")' if found else ""
                    raise SimplydataError(f'The group column "{name}" has only one group{which} in the rows used, so '
                                          "it cannot explain anything. Leave it out of using=.")
                levels[name] = found
        X, labels, owner, parts_of = _design(data, kinds, levels, terms)
        p = X.shape[1]
        if n <= p:
            raise SimplydataError(f"{step}() needs more rows ({n}) than values to estimate ({p}). "
                                  "Use fewer columns in using=, or groups with more rows.")
        if np.linalg.matrix_rank(X) < p:
            raise SimplydataError(self._rank_problem(X, labels))
        kind, groups = KINDS[outcome], None
        if grouped_by is not None:
            kind = "mixed" if outcome == "numbers" else "glmm"
            groups = np.array([_label(g) for g in raw[grouped_by][keep]], dtype=object)
            if len(set(groups.tolist())) < 2:
                raise SimplydataError(f'grouped_by="{grouped_by}" needs at least 2 groups.')
            self._need_statsmodels()
        model = dict(kind=kind, X=X, y=y, labels=labels, owner=owner, parts_of=parts_of, terms=terms, levels=levels,
                     kinds=kinds, n=n, yes_words=yes_words, groups=groups, keep=keep, outcome=outcome,
                     variables=variables, column=column, time=time, out_of=out_of, link=link, data=data)
        grouping = dict(grouping or {})
        if grouped_by is not None and grouping:
            if grouping.get("effects") == "for the whole population":
                kind = model["kind"] = "gee"
            slopes = grouping.get("slopes") or []
            grouping["slope_cols"] = [labels.index(name) for name in slopes]
            grouping.update(model=model, outcome=outcome, tested=self._tested_terms(terms, owner))
            model["grouping"] = {key: value for key, value in grouping.items() if key != "model"}
        model["fit"] = self._fit_one(kind, X, y, groups, family="binomial" if outcome == "yes or no" else "poisson",
                                     exposure=exposure, trials=trials, link=link, grouping=grouping)
        return model

    @staticmethod
    def _need_statsmodels():
        try:
            import statsmodels  # noqa: F401
        except ImportError:
            raise SimplydataError('This needs the statsmodels package: pip install "simplydata[stats]"') from None

    @staticmethod
    def _rank_problem(X, labels) -> str:
        """Name the columns that can be made exactly from the others."""
        bad = []
        for j in range(1, X.shape[1]):
            others = np.delete(X, j, axis=1)
            coef, *_ = np.linalg.lstsq(others, X[:, j], rcond=None)
            if np.allclose(others @ coef, X[:, j], atol=1e-9 * max(1.0, float(np.abs(X[:, j]).max()))):
                bad.append(labels[j])
        named = _list_words(_quoted(b) for b in bad) if bad else "some columns"
        return (f"The model cannot separate the effects of {named}: one can be made exactly from the others "
                "(for example the same thing measured twice, or a combination of groups with no rows). "
                "Leave one of them out of using=.")

    # ------------------------------------------------------------------ numbers per term
    @staticmethod
    def _coefficients(model):
        """Per model column: estimate, standard error, statistic, df, p and 95 % CI (log scale for ratios)."""
        from scipy import stats

        fit, kind = model["fit"], model["kind"]
        beta = fit["beta"]
        se = np.sqrt(np.diag(fit["cov"]))
        stat = beta / se
        if "satt" in fit:  # R lmerTest: Satterthwaite t-tests and intervals, each with its own df
            satt = fit["satt"]
            return dict(beta=beta, se=se, stat=stat, p=satt["p"], low=satt["low"], high=satt["high"], name="t",
                        df=satt["df"])
        if kind in ("lm", "quasipoisson", "gamma"):
            df = float(fit["df"])
            p = 2 * stats.t.sf(np.abs(stat), df)
            q = float(stats.t.ppf(0.975, df)) if kind == "lm" else Z95  # quasi-Poisson: R confint.default()
            low, high = beta - q * se, beta + q * se
            name, dfs = "t", np.full(len(beta), df)
        else:
            p = 2 * stats.norm.sf(np.abs(stat))
            low, high = beta - Z95 * se, beta + Z95 * se
            name, dfs = "z", np.full(len(beta), math.nan)
        return dict(beta=beta, se=se, stat=stat, p=p, low=low, high=high, name=name, df=dfs)

    @staticmethod
    def _tested_terms(terms, owner):
        """(term index, its model columns) for the terms with more than one column that are not part of an
        interaction, as R drop1() picks them."""
        out = []
        for index, term in enumerate(terms):
            columns = np.flatnonzero(owner == index)
            if len(columns) >= 2 and not any(set(term) < set(other) for other in terms):
                out.append((index, [int(c) for c in columns]))
        return out

    @staticmethod
    def _whole_column_tests(model):
        """One test per term with more than one column, as R drop1() (mixed models: Wald chi-square)."""
        from scipy import stats

        terms, owner, kind, fit = model["terms"], model["owner"], model["kind"], model["fit"]
        X, y = model["X"], model["y"]
        out = []
        if "satt" in fit:  # R lmerTest contest(joint = TRUE): an F test with Satterthwaite df per column
            satt = fit["satt"]
            for i, (index, _) in enumerate(model["grouping"]["tested"]):
                out.append(dict(term=" : ".join(terms[index]), name="F", stat=float(satt["f"][i]),
                                df=float(satt["numdf"][i]), df2=float(satt["dendf"][i]), p=float(satt["fp"][i]),
                                test="F test (Satterthwaite)"))
            return out
        for index, term in enumerate(terms):
            columns = np.flatnonzero(owner == index)
            if len(columns) < 2 or any(set(term) < set(other) for other in terms):
                continue  # one column (its own t or z test is the same), or part of an interaction, as R drop1()
            label = " : ".join(term)
            k = len(columns)
            if kind in ("mixed", "glmm", "gee"):
                b = fit["beta"][columns]
                chi = float(b @ np.linalg.solve(fit["cov"][np.ix_(columns, columns)], b))
                out.append(dict(term=label, name="chi-square", stat=chi, df=float(k), p=float(stats.chi2.sf(chi, k)),
                                test="Wald chi-square test"))
                continue
            reduced = np.delete(X, columns, axis=1)
            if kind == "lm":
                rss0 = _least_squares(reduced, y)[3]
                f = ((rss0 - fit["rss"]) / k) / (fit["rss"] / fit["df"])
                out.append(dict(term=label, name="F", stat=f, df=float(k), df2=float(fit["df"]),
                                p=float(stats.f.sf(f, k, fit["df"])), test="F test"))
                continue
            family = {"binomial": "binomial", "negbin": "negbin", "gamma": "gamma"}.get(kind, "poisson")
            # as R drop1(): the smaller model refitted with the same family (glm.nb: theta held)
            smaller = _glm(reduced, y, family, exposure=fit.get("exposure"), trials=fit.get("trials"),
                           alpha=fit.get("alpha"), link=fit.get("link"))
            change = float(smaller.deviance) - fit["deviance"]
            if kind in ("quasipoisson", "gamma"):
                f = (change / k) / (fit["deviance"] / fit["df"])  # as R drop1(test = "F")
                out.append(dict(term=label, name="F", stat=f, df=float(k), df2=float(fit["df"]),
                                p=float(stats.f.sf(f, k, fit["df"])), test="F test"))
            else:
                out.append(dict(term=label, name="chi-square", stat=change, df=float(k),
                                p=float(stats.chi2.sf(change, k)), test="likelihood-ratio test"))
        return out

    @staticmethod
    def _effect_name(outcome):
        return RATIO_WORDS.get(outcome, "effect")

    def _term_table(self, model, coef, tests, extra=None, more_rows=()):
        """The result table: one row per model column, then one per whole-column test."""
        effect = self._effect_name(model["outcome"])
        if model.get("link"):
            effect = f"effect ({model['link']} scale)"
        ratio = effect != "effect" and not model.get("link")
        rows = []
        for j, label in enumerate(model["labels"]):
            b, low, high = (float(coef["beta"][j]), float(coef["low"][j]), float(coef["high"][j]))
            row = {"term": label}
            if ratio:
                row.update({effect: _exp(b), "95 % CI low": _exp(low), "95 % CI high": _exp(high),
                            f"log {effect}": b})
            else:
                row.update({effect: b, "95 % CI low": low, "95 % CI high": high})
            row.update({"standard error": float(coef["se"][j]), "statistic name": coef["name"],
                        "statistic": float(coef["stat"][j]), "degrees of freedom": float(coef["df"][j]),
                        "p-value": float(coef["p"][j])})
            if extra:
                row.update({key: float(values[j]) for key, values in extra.items()})
            rows.append(row)
        for test in tests:
            row = {key: math.nan for key in rows[0]}
            row.update({"term": f"{test['term']} (whole column)", "statistic name": test["name"],
                        "statistic": test["stat"], "degrees of freedom": test["df"], "p-value": test["p"]})
            rows.append(row)
        for more in more_rows:
            row = {key: math.nan for key in rows[0]}
            row.update(more)
            rows.append(row)
        keys = list(dict.fromkeys(k for r in rows for k in r))
        data = {key: [r.get(key, math.nan) for r in rows] for key in keys}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ sentences
    @staticmethod
    def _term_sentence(model, j, beta, low, high, p) -> str:
        column, outcome = model["column"], model["outcome"]
        parts = model["parts_of"][j]
        words = _p_words(p)
        has_groups = any(model["kinds"][v] == "group" for v in model["variables"])
        at_base = " and every group column is at its baseline" if has_groups else ""
        if model["labels"][j] == INTERCEPT and model.get("link"):
            return (f"  intercept: {_num(beta)}, on the {model['link']} scale, when every number column is "
                    f"0{at_base}.")
        if model["labels"][j] == INTERCEPT:
            if outcome == "numbers":
                return f'  intercept: {_num(beta)}, the expected "{column}" when every number column is 0{at_base}.'
            what = ("odds of yes" if outcome == "yes or no" else f'expected "{column}"' if
                    outcome == "positive numbers" else "expected count")
            if model.get("time"):
                what += f' per 1 of "{model["time"]}"'
            return f"  intercept: {_num(_exp(beta))}, the {what} when every number column is 0{at_base}."
        if outcome == "numbers":
            interval = f"95 % CI {_num(low)} to {_num(high)}"
            if len(parts) == 1 and parts[0][1] is None:
                name = parts[0][0]
                more = "more" if beta >= 0 else "less"
                return (f'  {name}: each 1 more "{name}" goes with {_num(abs(beta))} {more} "{column}" '
                        f"({interval}); {words}.")
            if len(parts) == 1:
                var, level = parts[0][1]
                way = "higher" if beta >= 0 else "lower"
                return (f'  {var} "{_label(level)}" against "{_label(model["levels"][var][0])}": "{column}" is '
                        f"{_num(abs(beta))} {way} ({interval}); {words}.")
            return (f"  {model['labels'][j]} (interaction): {_num(beta)} ({interval}), how much the effect of one "
                    f"changes with the other; {words}.")
        thing = ("the odds of yes" if outcome == "yes or no" else f'the expected "{column}"' if
                 outcome == "positive numbers" else "the expected count")
        if model.get("link"):  # another link than the default: effects add on that scale
            scale = {"probit": "the probit of yes", "cloglog": "the complementary log-log of yes",
                     "identity": f'the expected "{column}"', "sqrt": "the square root of the expected count",
                     "inverse": f'1 / the expected "{column}"', "log": f'the log of the expected "{column}"'}[
                model["link"]]
            interval = f"95 % CI {_num(low)} to {_num(high)}"
            if len(parts) == 1 and parts[0][1] is None:
                return (f'  {parts[0][0]}: each 1 more "{parts[0][0]}" changes {scale} by {_num(beta)} ({interval}); '
                        f"{words}.")
            return f"  {model['labels'][j]}: changes {scale} by {_num(beta)} ({interval}); {words}."
        if model.get("time"):
            thing = "the rate (count per time)"
        ratio = _exp(beta)
        interval = f"95 % CI {_num(_exp(low))} to {_num(_exp(high))}"
        if len(parts) == 1 and parts[0][1] is None:
            name = parts[0][0]
            return f'  {name}: each 1 more "{name}" multiplies {thing} by {_num(ratio)} ({interval}); {words}.'
        if len(parts) == 1:
            var, level = parts[0][1]
            return (f'  {var} "{_label(level)}" against "{_label(model["levels"][var][0])}": {thing} is '
                    f"{_num(ratio)} times as high ({interval}); {words}.")
        return (f"  {model['labels'][j]} (interaction): {_num(ratio)} ({interval}), how many times the effect of one "
                f"is multiplied by the other; {words}.")

    def _print_terms(self, model, coef, rows_text):
        what = {"lm": "effect", "mixed": "effect", "binomial": "odds ratio", "poisson": "rate ratio",
                "quasipoisson": "rate ratio", "negbin": "rate ratio", "gamma": "ratio of averages",
                "glmm": "odds ratio" if model["outcome"] == "yes or no" else "rate ratio",
                "gee": RATIO_WORDS.get(model["outcome"], "effect")}[model["kind"]]
        if model.get("link"):
            what = f"effect ({model['link']} scale)"
        variables = _list_words(_quoted(v) for v in model["variables"])
        print(f'Explaining "{model["column"]}" from {variables} ({rows_text}). Each {what} below holds the other '
              "columns fixed:")
        for j in range(len(model["labels"])):
            print(self._term_sentence(model, j, coef["beta"][j], coef["low"][j], coef["high"][j], coef["p"][j]))

    def _report(self, model, pieces, grouped_by):
        """Print everything about one fitted model; gives back (coefficients, whole-column tests)."""
        from scipy import stats

        coef = self._coefficients(model)
        tests = self._whole_column_tests(model)
        fit, kind, n, column = model["fit"], model["kind"], model["n"], model["column"]
        formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
        offset = f", offset = log({_r_name(model['time'])})" if model.get("time") else ""
        if model.get("out_of"):
            formula = (f"cbind({_r_name(column)}, {_r_name(model['out_of'])} - {_r_name(column)}) ~ "
                       + " + ".join(pieces))
        self._print_terms(model, coef, f"{n} rows")
        for test in tests:
            extra = f" and {_whole(test['df2'])}" if "df2" in test else ""
            print(f'  {test["term"]}, all groups together: {test["test"]} ({test["name"]} = {_num(test["stat"])}, '
                  f"df = {_whole(test['df'])}{extra}); {_p_words(test['p'])}.")
        if kind == "lm":
            print(f"Method: linear model by least squares, as R lm({formula}).")
        elif kind == "binomial":
            family_text = f'binomial(link = "{model["link"]}")' if model.get("link") else "binomial"
            print(f"Method: {'logistic' if not model.get('link') else model['link']} regression, as R glm({formula}, "
                  f"family = {family_text}); {model['yes_words']}. "
                  "Wald 95 % intervals and z-tests, as R confint.default() and summary().")
        elif kind == "poisson":
            family_text = f'poisson(link = "{model["link"]}")' if model.get("link") else "poisson"
            print(f"Method: Poisson regression, as R glm({formula}, family = {family_text}{offset}). Wald 95 % intervals "
                  "and "
                  "z-tests, as R confint.default() and summary().")
        elif kind == "negbin":
            print(f"Method: negative binomial regression for counts that vary more than Poisson allows, as R "
                  f"MASS::glm.nb({formula}{offset}) (theta = {_num(fit['theta'])} by maximum likelihood; statsmodels). "
                  "Wald 95 % intervals and z-tests, as R confint.default() and summary().")
        elif kind == "gamma":
            print(f"Method: Gamma regression with a {model.get('link') or 'log'} link for positive, skewed numbers, "
                  f'as R glm({formula}, family = Gamma(link = "{model.get("link") or "log"}")): each effect '
                  f"{'multiplies the average' if not model.get('link') else 'adds on that scale'} (dispersion "
                  f"{_num(fit['dispersion'])}); t-tests as R summary(), Wald 95 % intervals as R confint.default().")
        elif kind == "quasipoisson":
            print(f"Method: quasi-Poisson regression, as R glm({formula}, family = quasipoisson{offset}): Poisson "
                  "rate "
                  f"ratios with standard errors widened for counts that vary more than Poisson allows (dispersion "
                  f"{_num(fit['dispersion'])}); t-tests as R summary(), Wald 95 % intervals as R confint.default().")
        elif kind == "glmm":
            family = fit["family"]
            what = "logistic" if family == "binomial" else "Poisson"
            yes = f"; {model['yes_words']}" if model["yes_words"] else ""
            random, own = self._random_words(model, grouped_by)
            print(f'Method: {what} mixed model with {own} for each "{grouped_by}", run in R: '
                  f"lme4::glmer({formula} + {random}, family = {family}) with the Laplace approximation{yes}. Wald "
                  "95 % intervals and z-tests, as R summary().")
        elif kind == "gee":
            grouping = model["grouping"]
            corr = grouping["corr"]
            family = {"numbers": "gaussian", "yes or no": "binomial", "counts": "poisson"}[model["outcome"]]
            words = {"exchangeable": 'rows in the same group alike ("exchangeable")',
                     "ar1": 'neighbouring rows in a group more alike than distant ones ("AR-1", rows in table order)',
                     "independence": 'rows treated as independent ("independence")'}[corr]
            how = "R geepack itself" if corr == "ar1" else "statsmodels GEE"
            yes = f"; {model['yes_words']}" if model["yes_words"] else ""
            print(f'Method: generalised estimating equations (GEE) for effects for the whole population, with the '
                  f'rows grouped by "{grouped_by}" and {words}, as R geepack::geeglm({formula}, id = '
                  f"{_r_name(grouped_by)}, family = {family}, corstr = \"{corr}\") ({how}){yes}. Robust "
                  "(sandwich) standard errors, Wald 95 % intervals and z-tests.")
        else:
            random, own = self._random_words(model, grouped_by)
            by_r = " in R" if fit.get("by_r") else ""
            fitter = "lmerTest::lmer" if "satt" in fit else "lme4::lmer"
            print(f'Method: linear mixed model with {own} for each "{grouped_by}", fitted by REML{by_r}, as R '
                  f"{fitter}({formula} + {random}).")
        k = model["X"].shape[1] - 1
        if kind == "lm":
            y = model["y"]
            r2 = 1 - fit["rss"] / float(((y - y.mean()) ** 2).sum())
            adj = 1 - (1 - r2) * (n - 1) / fit["df"]
            line = (f"R squared = {r2:.3f} (adjusted {adj:.3f}): the model explains about {round(r2 * 100)} % of the "
                    f'differences in "{column}".')
            if k > 0:
                f = (r2 / k) / ((1 - r2) / fit["df"])
                p = float(stats.f.sf(f, k, fit["df"]))
                line += f" The model as a whole (F = {_num(f)}, df = {k} and {fit['df']}): {_p_words(p)}."
            print(line)
        elif kind == "gee":
            groups = len(set(model["groups"].tolist()))
            corr = model["grouping"]["corr"]
            line = f'{groups} groups in "{grouped_by}".'
            if corr != "independence":
                line += f" Working correlation between rows of a group: {_num(fit['alpha'])}."
            if model["outcome"] == "numbers":
                line += f" Scale (variance) {_num(fit['scale'])}."
            print(line + " The effects are averages over the whole population of groups, not for one group.")
            if groups < 20:
                print(f"Note: only {groups} groups; robust standard errors need many groups (at least 20 or so) and "
                      "may be too small with fewer.")
            if fit.get("trouble"):
                print("Note: statsmodels warned that the fit did not settle fully; check the results.")
        elif kind == "glmm":
            groups = len(set(model["groups"].tolist()))
            scale = "log-odds" if fit["family"] == "binomial" else "log"
            print(f'{groups} groups in "{grouped_by}". Variance between groups {_num(fit["between"])} (on the {scale} '
                  f"scale). AIC = {_num(fit['aic'])}.")
            self._print_slopes(model, scale)
            fit = dict(fit, singular=fit["singular"] and not (model.get("grouping") or {}).get("slopes"))
            if fit["singular"]:
                print(f'Note: the variance between groups is about 0 (R calls this a singular fit): the groups in '
                      f'"{grouped_by}" differ no more than chance, so the model is the same as without grouped_by=.')
            if groups < 5:
                print(f"Note: only {groups} groups; with fewer than 5 the variance between groups is poorly estimated.")
            if fit["trouble"]:
                print("Note: R lme4 warned that the fit did not settle fully; check the results or use fewer columns.")
        elif kind != "mixed":
            null = fit["null_deviance"]
            line = (f"Residual deviance {_num(fit['deviance'])} on {fit['df']} df (with no columns: {_num(null)} on "
                    f"{n - 1} df).")
            if kind not in ("quasipoisson", "gamma") and k > 0:
                change = null - fit["deviance"]
                p = float(stats.chi2.sf(change, k))
                aic = fit["aic"]
                line += (f" The model as a whole (likelihood-ratio chi-square = {_num(change)}, df = {k}): "
                         f"{_p_words(p)}. AIC = {_num(aic)}.")
            print(line)
        else:
            between, within = fit["between"], fit["within"]
            icc = between / (between + within)
            groups = len(set(model["groups"].tolist()))
            if (model.get("grouping") or {}).get("slopes"):
                print(f'{groups} groups in "{grouped_by}". Variance of the starting levels between groups '
                      f"{_num(between)} (where the number columns are 0), within groups {_num(within)}.")
                fit = dict(fit, singular=False)
            else:
                print(f'{groups} groups in "{grouped_by}". Variance between groups {_num(between)}, within groups '
                      f'{_num(within)}: about {round(icc * 100)} % of the differences in "{column}" that the columns '
                      f"do not explain lies between the groups (intraclass correlation, ICC = {icc:.3f}).")
            self._print_slopes(model, None)
            if "satt" in fit:
                print("P-values: t-tests with Satterthwaite degrees of freedom and their 95 % intervals, run in R "
                      "(lmerTest summary() and contest()); safer than Wald z-tests when there are few groups.")
            else:
                print("P-values: Wald z-tests, with Wald 95 % intervals (standard errors as R vcov(), intervals as R "
                      'confint(method = "Wald")); p_value_by="satterthwaite" gives Satterthwaite t-tests (R '
                      "lmerTest) instead, which give slightly larger p-values when there are few groups.")
            if between <= 1e-6 * within or fit.get("singular"):
                print(f'Note: the variance between groups is about 0 (R calls this a singular fit): the groups in '
                      f'"{grouped_by}" differ no more than chance, so the model is the same as without grouped_by=.')
            if groups < 5:
                print(f"Note: only {groups} groups; with fewer than 5 the variance between groups is poorly estimated.")
            if fit["trouble"]:
                print("Note: the fit did not settle fully (statsmodels warned about convergence); check the results "
                      "or use fewer columns.")
        for note in self._model_notes(model):
            print(note)
        self._closing(coef["p"][1:])
        return coef, tests

    @staticmethod
    def _random_words(model, grouped_by):
        """The R random-effects term and its words: (1 | g), or (1 + x | g) with own slopes."""
        slopes = (model.get("grouping") or {}).get("slopes") or []
        if not slopes:
            return f"(1 | {_r_name(grouped_by)})", "a random intercept (its own starting level)"
        named = _list_words(_quoted(s) for s in slopes)
        return (f"(1 + {' + '.join(_r_name(s) for s in slopes)} | {_r_name(grouped_by)})",
                f"its own starting level and its own slope for {named}")

    @staticmethod
    def _print_slopes(model, scale):
        """The variance of each own slope and the correlations, when there are own slopes."""
        slopes = (model.get("grouping") or {}).get("slopes") or []
        parts = model["fit"].get("parts")
        if not slopes or not parts:
            return
        on = f" (on the {scale} scale)" if scale else ""
        pieces = [f'"{name}" {_num(v)}' for name, v in zip(slopes, parts["variances"][1:])]
        line = f"Variance of the own slopes between groups{on}: {_list_words(pieces)}."
        if parts["correlations"]:
            line += (" Correlation of starting level and slope: "
                     + ", ".join(_num(c) for c in parts["correlations"]) + ".")
        print(line)
        if any(abs(c) > 0.99 for c in parts["correlations"]) or model["fit"].get("singular"):
            print("Note: a correlation of about 1 or -1, or a variance of about 0 (R calls this a singular fit), "
                  "means the data cannot tell the slopes apart; the model without own_slope_for= may be enough.")

    @staticmethod
    def _closing(p_values):
        if any(p >= 0.05 for p in p_values):
            print("A large p-value does not show that there is no effect, only that the data cannot tell. "
                  "A link does not show that one thing causes the other.")
        else:
            print("A link does not show that one thing causes the other.")

    @staticmethod
    def _model_notes(model) -> list[str]:
        notes = []
        kind, fit, n = model["kind"], model["fit"], model["n"]
        X, labels = model["X"], model["labels"]
        effects = X.shape[1] - 1
        if kind == "lm":
            residuals = model["y"] - fit["fitted"]
            for note in _shape_notes([("this model", residuals)], what="the residuals (distances from the model)"):
                notes.append(note.replace('a safer test here: based_on="ranks".',
                                          "the p-values and confidence intervals may be off."))
        if kind == "binomial":
            trials = fit.get("trials")
            total = len(model["y"]) if trials is None else float(np.sum(trials))
            events = int(min(model["y"].sum(), total - model["y"].sum()))
            if effects and events / effects < ROWS_PER_EFFECT:
                notes.append(f"Note: only {events} rows in the smaller of yes and no for {effects} effects; with fewer "
                             f"than {ROWS_PER_EFFECT} per effect the results are unstable. Use fewer columns.")
            mu = fit["fitted"]
            if np.any(mu < 1e-8) or np.any(mu > 1 - 1e-8) or not fit["converged"]:
                notes.append("Note: some rows are predicted as certainly yes or certainly no (complete separation; R "
                             'warns "fitted probabilities numerically 0 or 1 occurred"), so the odds ratios and their '
                             "intervals cannot be trusted. Use fewer columns or merge groups.")
        elif effects and n / effects < ROWS_PER_EFFECT:
            notes.append(f"Note: only {n} rows for {effects} effects; with fewer than {ROWS_PER_EFFECT} rows per "
                         "effect the results are unstable. Use fewer columns.")
        if kind == "poisson" and fit["df"] > 0:
            ratio = fit["deviance"] / fit["df"]
            if ratio > OVERDISPERSION:
                notes.append(f"Note: the counts vary more than a Poisson model allows (residual deviance / df = "
                             f"{_num(ratio)}, above {OVERDISPERSION}), so the intervals are too narrow and the "
                             'p-values too small. Safer: outcome="counts that vary a lot" (negative binomial) or '
                             'outcome="counts (overdispersed)" (quasi-Poisson).')
        main = [j for j in range(1, X.shape[1]) if len(model["parts_of"][j]) == 1]
        if len(main) >= 2:
            with np.errstate(all="ignore"):
                corr = np.corrcoef(X[:, main], rowvar=False)
            if np.all(np.isfinite(corr)):
                try:
                    vif = np.diag(np.linalg.inv(corr))
                except np.linalg.LinAlgError:
                    vif = np.full(len(main), np.inf)
                high = [(labels[j], v) for j, v in zip(main, vif) if v > VIF_LIMIT]
                if high:
                    named = _list_words(f'"{name}" ({_num(v)})' for name, v in high)
                    notes.append(f"Note: some columns are strongly linked with the others (variance inflation factor "
                                 f"above {VIF_LIMIT:g}: {named}), so their separate effects are hard to tell apart and "
                                 "their intervals are wide. Consider leaving one out.")
        return notes

    # ------------------------------------------------------------------ explain
    @friendly
    def explain(self, column=None, using=None, outcome="numbers", grouped_by=None, empty_cells="leave out", seed=1,
                time=None, out_of=None, in_order=None, link=None, test_type=None, own_slope_for=None,
                p_value_by="wald", effects="for the average group", within_groups="alike"):
        """Explain one column from several others with a model, and say how big each effect is.

        table.explain("marks", using=["hours", "breakfast"])   (with sdata.example("school"))
        outcome="numbers" (the default): linear model by least squares (R lm()).
        outcome="yes or no": logistic regression, odds ratios (R glm(family = binomial)).
        outcome="counts": Poisson regression, rate ratios (R glm(family = poisson));
        outcome="counts (overdispersed)": quasi-Poisson (R glm(family = quasipoisson));
        outcome="counts that vary a lot": negative binomial (R MASS::glm.nb()).
        outcome="positive numbers": Gamma regression with a log link, for positive, skewed numbers
        such as times or amounts (R glm(family = Gamma(link = "log"))); effects multiply the average.
        time="years" with counts: rates, the count per unit of time (R offset = log(years)).
        out_of="tries" with outcome="yes or no": the column holds the number of yes out of that many
        tries (R glm(cbind(yes, tries - yes) ~ ..., family = binomial)).
        outcome="ordered groups": ordered logistic regression (R MASS::polr()); give the order of
        text groups, lowest first, with in_order=["low", "middle", "high"]. outcome="groups":
        multinomial logistic regression, each group against the first (R nnet::multinom()).
        outcome="shares": beta regression for shares between 0 and 1 (R betareg). outcome="counts
        with many zeros": zero-inflated Poisson regression (R pscl::zeroinfl()). link= (experts):
        "probit" or "cloglog" for yes or no, "identity" or "sqrt" for counts, "inverse" or
        "identity" for positive numbers; the effects are then on that scale, not ratios.
        test_type="type 2" adds a table with one test for each column (an ANOVA table): "type 2"
        (the usual choice, R car::Anova(type = 2)), "type 3" (sum-to-zero coding, R
        car::Anova(type = 3)) or "in order" (R anova(); the order of using= matters), with partial
        eta-squared for numbers (R effectsize).
        A text column in using= is a group column: each group is compared with the first group
        in sorted order (the baseline). "hours * breakfast" adds both columns and their
        interaction (does the effect of hours depend on breakfast?).
        grouped_by="school": a mixed model with its own starting level for each school
        (R lme4::lmer()), for rows that belong together. own_slope_for="hours" gives each school
        its own slope for hours too (R lme4::lmer() itself, (1 + hours | school)).
        p_value_by="satterthwaite" (or "few groups") gives t-tests with Satterthwaite degrees of
        freedom (R lmerTest) instead of Wald z-tests. effects="for the whole population" fits
        GEE instead (statsmodels, as R geepack::geeglm()): effects averaged over all groups, with
        within_groups="alike" (the default), "in time order" (rows in table order, R geepack) or
        "independent". empty_cells="multiple imputation"
        fills in empty cells 20 times (R mice()) instead of leaving those rows out; seed= fixes
        the random filling. Prints each effect with its 95 % confidence interval and p-value in
        words, and how well the model fits; gives back a table with one row per term.
        A link does not show that one thing causes the other.
        """
        step = "explain"
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise SimplydataError("seed= is a whole number that fixes the random filling-in, for example seed=1.")
        terms, pieces, variables, raw, missing, kinds = self._model_parts(
            step, column, using, outcome, grouped_by, empty_cells, time=time, out_of=out_of)
        names = [column] + variables + ([grouped_by] if grouped_by is not None else [])
        names += [v for v in (time, out_of) if v is not None]
        self._check_link(step, outcome, link, grouped_by, empty_cells)
        grouping = self._check_grouping(step, outcome, grouped_by, own_slope_for, p_value_by, effects, within_groups,
                                        variables, kinds)
        if outcome in ("ordered groups", "groups", "shares", "counts with many zeros"):
            if grouped_by is not None or empty_cells != "leave out":
                raise SimplydataError(f'outcome="{outcome}" cannot be used with grouped_by= or multiple imputation '
                                      "yet.")
            keep = ~np.any([missing[nm] for nm in names], axis=0)
            _skipped_note(int((~keep).sum()), names)
            return self._explain_more(step, column, outcome, terms, pieces, variables, raw, kinds, keep, in_order)
        if in_order is not None:
            raise SimplydataError('in_order= gives the order of the groups for outcome="ordered groups".')
        if empty_cells == "multiple imputation":
            return self._explain_imputed(step, column, outcome, terms, pieces, variables, raw, missing, kinds, seed)
        keep = ~np.any([missing[nm] for nm in names], axis=0)
        _skipped_note(int((~keep).sum()), names)
        model = self._fit_model(step, column, outcome, grouped_by, terms, variables, raw, kinds, keep, time=time,
                                out_of=out_of, link=None if link in (None, LINKS.get(outcome, (None,))[0]) else link,
                                grouping=grouping)
        if test_type is not None:
            from .anova_tables import read_test_type

            test_type = read_test_type(test_type)
            if time is not None or out_of is not None or model.get("link"):
                raise SimplydataError("test_type= cannot be used with time=, out_of= or link= yet.")
        coef, tests = self._report(model, pieces, grouped_by)
        more = []
        if test_type is not None:
            from .anova_tables import report

            more = report(model, test_type)
        return self._term_table(model, coef, tests, more_rows=more)

    @staticmethod
    def _check_grouping(step, outcome, grouped_by, own_slope_for, p_value_by, effects, within_groups, variables,
                        kinds):
        """Check own_slope_for=, p_value_by=, effects= and within_groups=; a dict for the fit (empty: the usual)."""
        text = str(p_value_by).strip().lower() if isinstance(p_value_by, str) else p_value_by
        if text not in P_VALUE_BY:
            raise SimplydataError(f'p_value_by= is "wald" (the default, Wald z-tests) or "satterthwaite" (also '
                                  f'"few groups": t-tests as R lmerTest), not {p_value_by!r}.')
        p_value_by = P_VALUE_BY[text]
        text = str(effects).strip().lower() if isinstance(effects, str) else effects
        effects = EFFECT_SPELLINGS.get(text, text)
        if effects not in EFFECTS:
            raise SimplydataError(f'effects= is "for the average group" (the default, a mixed model) or "for the '
                                  f'whole population" (GEE), not {effects!r}.')
        text = str(within_groups).strip().lower() if isinstance(within_groups, str) else within_groups
        within = WITHIN_SPELLINGS.get(text, text)
        if within not in WITHIN_GROUPS:
            raise SimplydataError(f'within_groups= is "alike" (the default), "in time order" or "independent", not '
                                  f"{within_groups!r}.")
        slopes = [own_slope_for] if isinstance(own_slope_for, str) else own_slope_for
        given = [name for name, used in (("own_slope_for=", slopes is not None),
                                         ('p_value_by="satterthwaite"', p_value_by != "wald"),
                                         ('effects="for the whole population"', effects != EFFECTS[0]),
                                         ("within_groups=", within != "alike")) if used]
        if grouped_by is None:
            if given:
                raise SimplydataError(f"{_list_words(given)} {'goes' if len(given) == 1 else 'go'} with grouped_by=, "
                                      'for rows that belong together, for example grouped_by="school".')
            return {}
        if within != "alike" and effects == EFFECTS[0]:
            raise SimplydataError('within_groups= goes with effects="for the whole population" (GEE); a mixed model '
                                  "takes the likeness of rows in a group from its own starting level.")
        if effects == EFFECTS[1]:
            if slopes is not None or p_value_by != "wald":
                raise SimplydataError('own_slope_for= and p_value_by= are for the mixed model (effects="for the '
                                      'average group"), not for GEE.')
            return {"effects": effects, "corr": WITHIN_GROUPS[within]}
        if p_value_by == "satterthwaite" and outcome != "numbers":
            raise SimplydataError('p_value_by="satterthwaite" is for outcome="numbers"; mixed models for yes/no and '
                                  "counts give Wald z-tests, as R lme4::glmer().")
        if slopes is not None:
            if not isinstance(slopes, (list, tuple)) or not slopes or not all(isinstance(v, str) for v in slopes):
                raise SimplydataError('own_slope_for= is a number column in using=, for example own_slope_for="hours".')
            for name in slopes:
                if name not in variables:
                    raise SimplydataError(f'own_slope_for="{name}" needs "{name}" in using= too: each group gets its '
                                          "own slope around the common one.")
                if kinds[name] != "number":
                    raise SimplydataError(f'own_slope_for="{name}": "{name}" holds groups; own slopes are for number '
                                          "columns.")
        if slopes is None and p_value_by == "wald":
            return {}
        return {"effects": effects, "slopes": list(slopes or []), "satterthwaite": p_value_by == "satterthwaite"}

    @staticmethod
    def _check_link(step, outcome, link, grouped_by, empty_cells):
        if link is None:
            return
        allowed = LINKS.get(outcome)
        if not allowed:
            raise SimplydataError(f'link= works with outcome="yes or no", "counts" or "positive numbers", not '
                                  f'"{outcome}".')
        if link not in allowed:
            raise SimplydataError(f'link= for outcome="{outcome}" is one of {_list_words(repr(a) for a in allowed)} '
                                  f'("{allowed[0]}" is the default), not {link!r}.')
        if link != allowed[0] and (grouped_by is not None or empty_cells != "leave out"):
            raise SimplydataError("link= cannot be used with grouped_by= or multiple imputation yet.")

    def _explain_more(self, step, column, outcome, terms, pieces, variables, raw, kinds, keep, in_order):
        """Ordered groups, groups, shares, counts with many zeros (table/models_more.py)."""
        from .models_more import explain_more, outcome_codes

        n = int(keep.sum())
        if n == 0:
            raise SimplydataError(f"{step}() found no rows with a value in every column it needs.")
        y, groups = outcome_codes(column, outcome, raw[column][keep], kinds[column], in_order)
        data = {name: raw[name][keep] for name in variables}
        levels = {}
        for name in variables:
            if kinds[name] == "group":
                found = sorted(set(data[name].tolist()), key=_sort_key)
                if len(found) < 2:
                    raise SimplydataError(f'The group column "{name}" has only one group in the rows used, so it '
                                          "cannot explain anything. Leave it out of using=.")
                levels[name] = found
        X, labels, owner, parts_of = _design(data, kinds, levels, terms)
        if n <= X.shape[1]:
            raise SimplydataError(f"{step}() needs more rows ({n}) than values to estimate ({X.shape[1]}).")
        if np.linalg.matrix_rank(X) < X.shape[1]:
            raise SimplydataError(self._rank_problem(X, labels))
        model = dict(X=X, y=y, n=n, labels=labels, owner=owner, parts_of=parts_of, levels=levels, kinds=kinds,
                     variables=variables, groups_of_outcome=groups)
        return explain_more(self, step, column, outcome, pieces, model)

    # ------------------------------------------------------------------ multiple imputation
    def _explain_imputed(self, step, column, outcome, terms, pieces, variables, raw, missing, kinds, seed):
        from scipy import stats

        self._need_statsmodels()
        import pandas as pd
        from statsmodels.imputation.mice import MICEData

        names = [column] + variables
        size = len(raw[column])
        text_cols = [nm for nm in names if kinds[nm] == "group" and nm != column]
        number_cols = [nm for nm in names if kinds[nm] == "number"]
        text_gap = np.any([missing[nm] for nm in text_cols], axis=0) if text_cols else np.zeros(size, dtype=bool)
        filled_cols = list(dict.fromkeys(number_cols + [column]))
        every_gap = np.all([missing[nm] for nm in filled_cols], axis=0)
        keep = ~text_gap & ~every_gap
        if text_gap.any():
            print(f"Note: {int(text_gap.sum())} rows with an empty cell in a text column "
                  f"({_list_words(_quoted(g) for g in text_cols)}) were left out: multiple imputation here fills in "
                  "number columns (and a yes/no outcome) only.")
        if every_gap.any():
            _skipped_note(int((every_gap & ~text_gap).sum()), filled_cols)
        gaps = np.any([missing[nm][keep] for nm in filled_cols], axis=0)
        rows_with_gaps = int(gaps.sum())
        if rows_with_gaps == 0:
            print("There are no empty cells to fill in, so this is the ordinary fit.")
            model = self._fit_model(step, column, outcome, None, terms, variables, raw, kinds, keep)
            coef, tests = self._report(model, pieces, None)
            return self._term_table(model, coef, tests)
        work = {nm: raw[nm][keep] for nm in names}
        yes_words = None
        if outcome == "yes or no":  # filled in as 0 and 1
            given = ~missing[column][keep]
            mapped, yes_words = self._outcome_values(column, outcome, work[column][given], kinds[column])
            yes_value = work[column][given][int(np.argmax(mapped))]
            outcome_numbers = np.array([math.nan if _missing(v) else float(v == yes_value) for v in work[column]])
        else:
            outcome_numbers = work[column].astype(float)
        frame, safe = {}, {}
        for i, nm in enumerate(names):
            key = f"v{i}"
            if nm == column or kinds[nm] == "number":
                frame[key] = outcome_numbers if nm == column else work[nm].astype(float)
                safe[nm] = key
            else:
                levels = sorted(set(work[nm].tolist()), key=_sort_key)
                for j, level in enumerate(levels[1:]):
                    frame[f"{key}_{j}"] = np.array([v == level for v in work[nm]], dtype=float)
        imputer = MICEData(pd.DataFrame(frame), k_pmm=PMM_DONORS, rng=seed)
        filled = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            imputer.update_all(BURN_IN)
            for _ in range(IMPUTATIONS):
                imputer.update_all(BETWEEN)
                filled.append(imputer.data.copy())
        fit_kinds = dict(kinds)
        fit_kinds[column] = "number" if outcome != "yes or no" else "group"
        estimates, variances, model = [], [], None
        every_row = np.ones(len(filled[0]), dtype=bool)
        for data in filled:
            filled_raw = dict(work)
            for nm, key in safe.items():
                filled_raw[nm] = data[key].to_numpy(dtype=float)
            if outcome == "yes or no":
                filled_raw[column] = np.where(filled_raw[column] > 0.5, "yes", "no").astype(object)
            model = _quiet(self._fit_model, step, column, outcome, None, terms, variables, filled_raw, fit_kinds,
                           every_row)
            estimates.append(model["fit"]["beta"])
            variances.append(np.diag(model["fit"]["cov"]))
        m = IMPUTATIONS
        from .._r import r_call

        # Rubin's rules with Barnard-Rubin degrees of freedom: R mice::pool.scalar() for each coefficient
        pooled = r_call("res <- lapply(seq_len(ncol(q)), function(j) mice::pool.scalar(q[, j], u[, j], n = n, k = k)); "
                        "list(qbar = sapply(res, `[[`, 'qbar'), t = sapply(res, `[[`, 't'), "
                        "df = sapply(res, `[[`, 'df'), "
                        "lambda = sapply(res, function(r) (1 + 1 / r$m) * r$b / r$t))",
                        packages=("mice",), source="mice::pool",
                        what="Pooling the filled-in tables (R mice::pool())",
                        python_note="statsmodels MICE pools with Rubin's rules but without the Barnard-Rubin "
                                    "degrees of freedom, so its p-values differ",
                        q=np.array(estimates), u=np.array(variances), n=float(model["n"]),
                        k=float(model["X"].shape[1]))
        qbar, se = np.asarray(pooled["qbar"], dtype=float), np.sqrt(np.asarray(pooled["t"], dtype=float))
        df, lam = np.asarray(pooled["df"], dtype=float), np.asarray(pooled["lambda"], dtype=float)
        stat = qbar / se
        p = 2 * stats.t.sf(np.abs(stat), df)
        tq = stats.t.ppf(0.975, df)
        coef = dict(beta=qbar, se=se, stat=stat, p=p, low=qbar - tq * se, high=qbar + tq * se, name="t", df=df)
        self._print_terms(model, coef, f"{model['n']} rows, {rows_with_gaps} of them with empty cells filled in")
        formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
        call = {"numbers": f"lm({formula})", "yes or no": f"glm({formula}, family = binomial)",
                "counts": f"glm({formula}, family = poisson)",
                "counts (overdispersed)": f"glm({formula}, family = quasipoisson)",
                "counts that vary a lot": f"MASS::glm.nb({formula})",
                "positive numbers": f'glm({formula}, family = Gamma(link = "log"))'}[outcome]
        if yes_words:
            print(f"Outcome {yes_words}.")
        print(f"Method: multiple imputation by chained equations (predictive mean matching with {PMM_DONORS} donors, "
              f"seed={seed}): the empty cells were filled in {m} times, the model was fitted to each of the {m} "
              "filled-in tables, and the results were pooled with Rubin's rules (t-based intervals with Barnard-Rubin "
              f"degrees of freedom), as R pool(with(mice(...), {call})).")
        print(f"The filling-in adds uncertainty: up to {round(float(np.max(lam)) * 100)} % of the variance of an "
              "effect comes from the differences between the filled-in tables. Tests for whole group columns are not "
              "pooled here.")
        self._closing(p[1:])
        return self._term_table(model, coef, [], extra={"share of variance from empty cells": lam})

    # ------------------------------------------------------------------ add_predicted_column
    @friendly
    def add_predicted_column(self, column=None, using=None, outcome="numbers", name=None, grouped_by=None,
                             start=None, between=None, weights=None, for_each=None):
        """Add a column with the value the model predicts for each row.

        table.add_predicted_column("marks", using=["hours", "breakfast"])   (with sdata.example("school"))
        The same model as explain() with the same options: outcome="numbers" gives the fitted
        value (R fitted(lm(...))), outcome="yes or no" the chance of yes from 0 to 1 and
        outcome="counts" the expected count (R fitted(glm(...))). With grouped_by= the
        prediction includes each group's own level (R fitted(lmer(...))). Rows with an empty
        cell in a column used stay empty. Undo with table.undo().

        A formula with one = sign is fitted as table.fit_formula() (with its options start=,
        between=, weights= and for_each=) and its value is added for every row, also rows
        whose left-hand column is empty (as R predict(nls(...), newdata)):
        table.add_predicted_column("population = a * exp(b * (year - 2000))", for_each="country")
        using= a fit_formula() result takes its values instead of fitting again.
        """
        step = "add_predicted_column"
        if isinstance(column, str) and "=" in column:
            if outcome != "numbers" or grouped_by is not None:
                raise SimplydataError("outcome= and grouped_by= are for a model from explain(); a formula is fitted "
                                      "by nonlinear least squares, as table.fit_formula().")
            return self._add_formula_column(column, using, name, start, between, weights, for_each)
        given = [k for k, v in (("start", start), ("between", between), ("weights", weights),
                                ("for_each", for_each)) if v is not None]
        if given:
            raise SimplydataError(
                f"{', '.join(k + '=' for k in given)} {'is' if len(given) == 1 else 'are'} for a formula, such as "
                'table.add_predicted_column("population = a * exp(b * (year - 2000))", for_each="country").\n'
                'For a model from explain() use using= and grouped_by=, for example '
                'table.add_predicted_column("marks", using=["hours", "breakfast"]).'
            )
        terms, pieces, variables, raw, missing, kinds = self._model_parts(
            step, column, using, outcome, grouped_by, "leave out")
        names = [column] + variables + ([grouped_by] if grouped_by is not None else [])
        if name is None:
            name = f"predicted {column}"
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f'{step}() needs the new column\'s name in quotes, for example name="predicted".')
        if name in self._columns:
            raise SimplydataError(f'There is already a column called "{name}". Choose another name with name=.')
        keep = ~np.any([missing[nm] for nm in names], axis=0)
        model = self._fit_model(step, column, outcome, grouped_by, terms, variables, raw, kinds, keep)
        values = [None] * len(keep)
        for i, v in zip(np.flatnonzero(keep), model["fit"]["fitted"]):
            values[i] = float(v)
        base = nw.maybe_reset_index(self._frame)
        new = nw.new_series(name, values, nw.Float64, backend=base.implementation)
        what = {"numbers": "the fitted value", "yes or no": "the chance of yes (0 to 1)",
                "counts": "the expected count", "counts (overdispersed)": "the expected count",
                "counts that vary a lot": "the expected count", "positive numbers": "the expected value"}[outcome]
        how = {"lm": "least squares", "binomial": "logistic regression", "poisson": "Poisson regression",
               "quasipoisson": "quasi-Poisson regression", "mixed": "linear mixed model",
               "negbin": "negative binomial regression", "gamma": "Gamma regression",
               "glmm": "generalised linear mixed model"}[model["kind"]]
        empty = len(keep) - model["n"]
        yes = f"; {model['yes_words']}" if model["yes_words"] else ""
        print(f'Added "{name}": {what} of "{column}" from {_list_words(_quoted(v) for v in variables)} '
              f"({how}, {model['n']} rows{yes})." + (f" {empty} rows with an empty cell stay empty." if empty else ""))
        return self._change(f'add predicted column "{name}" ({column} from {", ".join(pieces)}, {outcome})',
                            base.with_columns(new))
