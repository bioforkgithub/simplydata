"""Survival: how long until something happens, when some rows were followed only part of the way.

time= is the column with the time until the event, or until the end of follow-up for rows
where the event did not happen (they are "censored": we only know the event had not
happened by then). event= is the column that says whether the event happened: yes/no,
True/False or 1/0, and the printed sentence says which value counts as the event. value= names the
value that is the event when the column holds other words ("relapse" and "alive").

Methods (the same defaults as R's survival package, so results can be checked there):

* find_survival_over_time: the Kaplan-Meier estimate (R survfit(Surv(time, event) ~ group)),
  from statsmodels SurvfuncRight.
  At each time with events, survival is multiplied by (1 - events / at risk); "at risk"
  counts the rows with a time at or after that moment (events come before censoring at a
  tied time, as in R). 95 % confidence intervals on the log scale (R's default
  conf.type = "log"): S x exp(-/+ 1.96 se), se of log S from Greenwood's formula
  sqrt(sum(d / (n (n - d)))), the top end cut at 1. The median time and its 95 % CI are
  read where the curve and the two edges of the band first reach 0.5 or below, with R's
  rule for a curve that sits exactly on 0.5 (the middle of that time and the next drop).
  at_time_points= reads the curve at chosen times (R summary(survfit(), times =, extend = TRUE), but empty
  after a group's last follow-up); method="life table" gives the actuarial life table (R KMsurv::lifetab);
  average_time_up_to= the restricted mean survival time (R summary(survfit(), rmean =)); allowing_for= curves
  adjusted for other columns by direct adjustment (R adjustedCurves::adjustedsurv(method = "direct")).
* compare_survival: the log-rank test (R survdiff(), rho = 0), from statsmodels survdiff.
  At each event time the events are shared out over the groups in proportion to the rows
  at risk (the expected events); the chi-square compares observed and expected with their
  hypergeometric variance, on (groups - 1) degrees of freedom. allowing_for= stratifies it (R survdiff(... +
  strata())); average_time_up_to= adds the difference in restricted mean survival time (R survRM2::rmst2);
  value= with competing_with= gives Gray's test (R cmprsk::cuminc()$Tests).
* explain_survival: the Cox proportional hazards model (R coxph()), with Efron's method for
  tied event times (R's default), from statsmodels PHReg(ties="efron"). Hazard ratios exp(coefficient) with 95 % Wald intervals, Wald z p-values, and the
  likelihood-ratio test of the whole model (2 x the gain in log partial likelihood, df =
  number of coefficients). A text (or True/False) column becomes groups compared with the
  first group in sorted order, as R does with a factor.
  Proportional-hazards check: R survival::cox.zph() itself (transform = "km"), through
  rpy2 (pip install "simplydata[r]" and R); no Python package gives R's numbers. A note is
  printed when a term has p < 0.05. The same R call gives Harrell's C (survival::concordance()). Without R the
  model is still fitted and a note says how to add the check.
  allowing_for= stratifies (PHReg(strata=)); followed_from= gives each row its start time (PHReg(entry=), R
  Surv(start, stop, event)); competing_with= gives the cause-specific model; method="fine-gray" the Fine-Gray
  model (R cmprsk::crr); distribution= a parametric model with time ratios (R survival::survreg).
"""

from __future__ import annotations

import contextlib
import io
import math
import warnings

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .stat_tests import _label, _list_words, _num, _p_shown, _skipped_note, _whole
from .summaries import _p_clause, _p_sentence

Z95 = 1.959963984540054  # qnorm(0.975)
EVENT_WORDS = {"yes": True, "no": False, "true": True, "false": False, "1": True, "0": False}
EXAMPLE = 'with sdata.get_example("trial"): table.{word}(time="days", event="died"{more})'
COX_STEPS = 20  # R coxph.control(iter.max = 20)
# words that usually mean "no event" (followed without it): used only to suggest a value= in a message
CENSOR_WORDS = {"alive", "censored", "censor", "no", "none", "still followed", "0", "false", "lost", "free",
                "event-free", "no event"}
MANY_STRATA = 20  # more strata than this: a note (many strata waste information)
METHODS = ("kaplan-meier", "life table")
METHOD_SPELLINGS = {"km": "kaplan-meier", "kaplan meier": "kaplan-meier", "kaplan_meier": "kaplan-meier",
                    "lifetable": "life table", "life-table": "life table", "life_table": "life table",
                    "actuarial": "life table", "actuarial life table": "life table"}
MODEL_METHODS = ("cox", "fine-gray")
MODEL_SPELLINGS = {"cause-specific": "cox", "cause specific": "cox", "cause_specific": "cox", "coxph": "cox",
                   "fine gray": "fine-gray", "finegray": "fine-gray", "fine_gray": "fine-gray", "crr": "fine-gray"}
DISTRIBUTIONS = ("weibull", "exponential", "lognormal", "log-logistic")
DISTRIBUTION_SPELLINGS = {"log-normal": "lognormal", "log normal": "lognormal", "loglogistic": "log-logistic",
                          "log logistic": "log-logistic"}


# ---------------------------------------------------------------------------- reading the columns
def is_empty(value) -> bool:
    """An empty cell: missing, NaN, or text that is only spaces."""
    if value is None:
        return True
    if isinstance(value, (float, np.floating)) and math.isnan(value):
        return True
    return isinstance(value, str) and not value.strip()


def _is_number(v) -> bool:
    return isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, (bool, np.bool_))


def _key(v):
    """A cell as a key to compare: numbers as floats (1 and 1.0 are one value), text without outer spaces."""
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if _is_number(v):
        return float(v)
    if isinstance(v, str):
        return v.strip()
    return v


def _kinds(keys) -> list:
    return sorted(set(keys), key=lambda k: (str(type(k)), k))


def value_text(k) -> str:
    """A value of the event column as written in a sentence: "relapse" in quotes, numbers plain."""
    if isinstance(k, bool):
        return str(k)
    if isinstance(k, float):
        return _whole(k)
    return f'"{k}"'


def _literal(k) -> str:
    """A value as Python code, for a call to copy: "relapse", 2, True."""
    if isinstance(k, float) and k.is_integer():
        return str(int(k))
    if isinstance(k, str):
        return '"' + k.replace('"', '\\"') + '"'
    return repr(k)


def kinds_error(column, kinds, time=None, value=None, step=None) -> SimplydataError:
    """S3b-L6: an event column with three or more kinds of outcome is never read as yes/no. The message shows
    the find_risk_over_time call (the chance of one event when another can come first)."""
    shown = _list_words(value_text(k) for k in kinds[:8]) + (" ..." if len(kinds) > 8 else "")
    events = [k for k in kinds if not (isinstance(k, str) and k.lower() in CENSOR_WORDS) and k not in (0.0, False)]
    first = value if value is not None else (events[0] if events else kinds[-1])
    other = next((k for k in events if k != first), next(k for k in kinds if k != first))
    start = (f"{step}() needs competing_with= here: the" if step else "The")
    return SimplydataError(
        f'{start} event column "{column}" has {len(kinds)} kinds of outcome ({shown}). When one kind can come '
        "first and stop another from happening (death before relapse), counting it as the end of follow-up makes 1 "
        f"minus the survival curve too high. To find the chance of {value_text(first)} when {value_text(other)} can "
        f'come first:\n  table.find_risk_over_time(time="{time or "time"}", event="{column}", value={_literal(first)}, '
        f"competing_with={_literal(other)})")


def read_event(values, column: str, value=None, time=None):
    """The event column as True/False (True = the event happened), and words saying which value
    counts as the event. values: a list without empty cells. value=: the value that is the event, for a
    column of two other words or numbers."""
    keys = [_key(v) for v in values]
    kinds = _kinds(keys)
    if value is not None:
        want = _key(value)
        if want not in kinds:
            raise SimplydataError(f'value={_literal(want)} is not in the event column "{column}"; it has '
                                  f"{_list_words(value_text(k) for k in kinds[:8])}.")
        if len(kinds) > 2:
            raise kinds_error(column, kinds, time, want)
        return np.array([k == want for k in keys], dtype=bool), value_text(want)
    if all(isinstance(v, (bool, np.bool_)) for v in values):
        return np.array([bool(v) for v in values], dtype=bool), "True"
    if all(_is_number(v) for v in values):
        found = sorted({float(v) for v in values})
        if set(found) <= {0.0, 1.0}:
            return np.array([float(v) == 1.0 for v in values], dtype=bool), "1"
        if len(found) >= 3:
            raise kinds_error(column, kinds, time)
        shown = ", ".join(_num(v) for v in found[:6])
        raise SimplydataError(
            f'The event column "{column}" has numbers other than 0 and 1 ({shown}).\n'
            "It should say whether the event happened: 1/0, yes/no or True/False"
            + (f", or name the value that is the event: value={_literal(found[-1])}." if len(found) == 2 else ".")
        )
    if all(isinstance(v, str) for v in values):
        words = {v.strip().lower() for v in values}
        if words <= set(EVENT_WORDS):
            out = np.array([EVENT_WORDS[v.strip().lower()] for v in values], dtype=bool)
            yes = [v.strip() for v in values if EVENT_WORDS[v.strip().lower()]]
            if not yes:
                yes = ["yes" if words & {"yes", "no"} else "true" if words & {"true", "false"} else "1"]
            return out, f'"{yes[0]}"'
        if len(kinds) >= 3:
            raise kinds_error(column, kinds, time)
        other = sorted(words - set(EVENT_WORDS))[:4]
        pick = next((k for k in kinds if k.lower() not in CENSOR_WORDS), kinds[-1])
        raise SimplydataError(
            f'The event column "{column}" should say whether the event happened (yes/no, True/False or 1/0), '
            f"but it also has {_list_words(repr(o) for o in other)}.\n"
            f"Name the value that is the event (value={pick!r}), change the values first, for example with "
            "table.replace_values_in(...), or use another column."
        )
    kinds_found = sorted({type(v).__name__ for v in values})
    raise SimplydataError(
        f'The event column "{column}" holds a mix of things ({", ".join(kinds_found)}). '
        "It should say whether the event happened: yes/no, True/False or 1/0."
    )


def read_states(values, column, value, competing_with, time, step):
    """The event column with competing events: 0 = followed without any of the named events (censored), 1 = the
    event of value=, 2, 3, ... = the events of competing_with= in the order given. Also the names of the events
    (value first) and how many rows of each other value count as still followed."""
    example = f'table.{step}(time="{time}", event="{column}", value="relapse", competing_with="death")'
    if value is None:
        raise SimplydataError(f'{step}() needs value= with competing_with=: the value of "{column}" that is the '
                              f"event you ask about.\nFor example, {example}")
    named_competing = list(competing_with) if isinstance(competing_with, (list, tuple)) else [competing_with]
    if not named_competing:
        raise SimplydataError(f"competing_with= needs one value (or a list).\nFor example, {example}")
    keys = [_key(v) for v in values]
    kinds = _kinds(keys)
    named = [_key(value)] + [_key(c) for c in named_competing]
    for n in named:
        if n not in kinds:
            raise SimplydataError(f'{_literal(n)} is not in the event column "{column}"; it has '
                                  f"{_list_words(value_text(k) for k in kinds[:8])}.")
    if len(set(named)) < len(named):
        raise SimplydataError("The same value is given twice (in value= and competing_with=, or twice in "
                              "competing_with=). Give each kind of event once.")
    state = np.zeros(len(keys), dtype=int)
    for i, n in enumerate(named, start=1):
        state[np.array([k == n for k in keys], dtype=bool)] = i
    others = [(k, sum(1 for x in keys if x == k)) for k in kinds if k not in named]
    return state, [value_text(n) for n in named], others


def others_sentence(others, column) -> str:
    """How every other value of the event column was counted (review 5.3: a forgotten competing event shows)."""
    if not others:
        return f'Every row of "{column}" had one of these events.'
    parts = [f"{value_text(k)}: {n} {'row' if n == 1 else 'rows'}" for k, n in others]
    return f'Counted as still followed without these events (censored) in "{column}": {_list_words(parts)}.'


def check_time(values, column: str):
    """The time column as floats: numbers, none below 0."""
    if not all(_is_number(v) for v in values):
        raise SimplydataError(
            f'The time column "{column}" should hold numbers (the time until the event or the end of '
            "follow-up), but it holds other things."
        )
    times = np.asarray(values, dtype=float)
    if (times < 0).any():
        raise SimplydataError(
            f'The time column "{column}" has {int((times < 0).sum())} values below 0. A time until an event '
            "cannot be negative; check those rows."
        )
    return times


def check_entry(values, times, column: str, time: str, rows):
    """followed_from=: the time each row's follow-up started (on the clock of time=), below its time."""
    if not all(_is_number(v) for v in values):
        raise SimplydataError(f'followed_from="{column}" should hold numbers: the time each row\'s follow-up '
                              f'started, on the same clock as "{time}".')
    entries = np.asarray(values, dtype=float)
    bad = np.flatnonzero(entries >= times)
    if len(bad):
        shown = ", ".join(str(rows[i] + 1) for i in bad[:8]) + (" ..." if len(bad) > 8 else "")
        raise SimplydataError(f'"{column}" (followed_from=) must be before "{time}" in every row; it is not in '
                              f"{len(bad)} {'row' if len(bad) == 1 else 'rows'} (row {shown}, counting from 1).")
    return entries


def _need(step, option, value, example):
    if not isinstance(value, str):
        raise SimplydataError(f"{step}() needs {option} as a column name in quotes.\nFor example, {example}")


def _pct(x) -> str:
    """A share written as a percent with one decimal ("64.5 %"), by Python's own % format (display only)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{float(x):.1%}".replace("%", " %")


def _choice(step, option, value, choices, spellings):
    name = value.strip().lower() if isinstance(value, str) else value
    name = spellings.get(name, name)
    if name not in choices:
        raise choice_error(step, option, value, list(choices))
    return name


def time_points(step, at, option="at_time_points"):
    """at_time_points=: one time or a list of times, numbers of 0 or more, sorted (said when they were not)."""
    if isinstance(at, (str, bytes)) or not hasattr(at, "__iter__"):
        points = [at]
    else:
        points = list(at.to_list() if hasattr(at, "to_list") else at)
    if not points or not all(_is_number(p) for p in points):
        raise SimplydataError(f"{option}= needs numbers on the time= clock, for example {option}=[365, 730].")
    values = np.asarray(points, dtype=float)
    if (values < 0).any():
        raise SimplydataError(f"{option}= has a time below 0; times start at 0.")
    if len(set(values.tolist())) < len(values):
        raise SimplydataError(f"{option}= has the same time twice; give each time once.")
    if (np.diff(values) < 0).any():
        print(f"Note: the times of {option}= are read in order: {', '.join(_whole(v) for v in np.sort(values))}.")
    return np.sort(values)


# ---------------------------------------------------------------------------- the calculations
def kaplan_meier(time, event, entry=None) -> dict:
    """Kaplan-Meier estimate as R survfit() (conf.type = "log"), from statsmodels SurvfuncRight.

    At each event time: time, at_risk, events, censored (since the previous event time, up
    to and including this time, as R summary(survfit)), survival, se (of log survival,
    Greenwood), low, high. Also at every distinct time (all_time, all_survival, all_low,
    all_high), the censored times with their survival, and the last time (end). entry: the time each row's
    follow-up started (delayed entry, R Surv(start, stop, event)); a row is at risk at t when entry < t <= time."""
    from statsmodels.duration.survfunc import SurvfuncRight

    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=bool)
    all_time, inverse = np.unique(time, return_inverse=True)
    deaths = np.bincount(inverse, weights=event.astype(float), minlength=len(all_time))
    lost = np.bincount(inverse, weights=(~event).astype(float), minlength=len(all_time))
    if entry is None:
        at_risk = (deaths + lost)[::-1].cumsum()[::-1]
    else:  # counting: the rows whose follow-up covers the time
        entry = np.asarray(entry, dtype=float)
        at_risk = np.array([float(((time >= t) & (entry < t)).sum()) for t in all_time])
    # survival and its Greenwood standard error at each event time from statsmodels, then
    # carried to every distinct time (the curve is flat between event times)
    survival, se = np.ones(len(all_time)), np.zeros(len(all_time))
    if event.any():
        fit = SurvfuncRight(time, event.astype(float), entry=entry)
        place = np.searchsorted(fit.surv_times, all_time, side="right") - 1
        seen = place >= 0
        with np.errstate(divide="ignore", invalid="ignore"):
            log_se = np.where(fit.surv_prob > 0, fit.surv_prob_se / fit.surv_prob, np.inf)
        survival[seen], se[seen] = fit.surv_prob[place[seen]], log_se[place[seen]]
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        low = survival * np.exp(-Z95 * se)
        high = np.minimum(1.0, survival * np.exp(Z95 * se))
    gone = (survival == 0) | ~np.isfinite(se)
    low[gone], high[gone] = np.nan, np.nan
    keep = deaths > 0
    censored = np.diff(np.concatenate([[0.0], np.cumsum(lost)[keep]]))
    return dict(
        time=all_time[keep], at_risk=at_risk[keep], events=deaths[keep], censored=censored,
        survival=survival[keep], se=se[keep], low=low[keep], high=high[keep],
        all_time=all_time, all_at_risk=at_risk, all_survival=survival, all_low=low, all_high=high,
        censor_time=all_time[lost > 0], censor_survival=survival[lost > 0],
        end=float(time.max()) if len(time) else 0.0, n=len(time), total_events=int(event.sum()),
    )


def _first_half(values, times):
    """R survmean's minmin(): the first time the curve is at 0.5 or below (with R's tolerance);
    exactly on 0.5 gives the middle of that time and the next time it drops."""
    tolerance = math.sqrt(np.finfo(float).eps)
    keep = ~np.isnan(values) & (values < 0.5 + tolerance)
    if not keep.any():
        return math.nan
    x, y = times[keep], values[keep]
    if abs(y[0] - 0.5) < tolerance and (y < y[0]).any():
        return float((x[0] + x[np.argmax(y < y[0])]) / 2)
    return float(x[0])


def median_time(km) -> tuple[float, float, float]:
    """Median survival time with its 95 % CI, as R print(survfit()); nan = not reached."""
    t = km["all_time"]
    return (_first_half(km["all_survival"], t), _first_half(km["all_low"], t), _first_half(km["all_high"], t))


def log_rank(time, event, codes, k, entry=None, strata=None):
    """Log-rank test as R survdiff(rho = 0): observed, expected, chi-square, df.

    The chi-square comes from statsmodels survdiff (with strata= for a stratified test and entry= for rows
    followed from a later start). The observed and expected events per group are only counted for the
    printout (expected = sum over event times of events x share of the rows at risk in that group, within
    each stratum). Groups with no expected events are left out of the test, as R does, and df counts only the
    groups that are left."""
    from statsmodels.duration.survfunc import survdiff

    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=bool)
    codes = np.asarray(codes)
    start = np.full(len(time), -np.inf) if entry is None else np.asarray(entry, dtype=float)
    layers = np.zeros(len(time), dtype=int) if strata is None else np.asarray(strata)
    observed = np.array([(event & (codes == j)).sum() for j in range(k)], dtype=float)
    expected = np.zeros(k)
    for layer in np.unique(layers):
        inside = layers == layer
        for t in np.unique(time[event & inside]):
            risk = inside & (time >= t) & (start < t)
            n_j = np.array([(risk & (codes == j)).sum() for j in range(k)], dtype=float)
            expected += float((event & inside & (time == t)).sum()) * n_j / n_j.sum()
    # as R survdiff: a group with no expected events (no row at risk at any event time) is left
    # out; its rows are in no risk set, so leaving them out changes nothing else
    used = expected > 0
    keep = used[codes]
    df = int(used.sum()) - 1
    if df < 1:
        return observed, expected, math.nan, 0
    options = {}
    if strata is not None:
        options["strata"] = layers[keep]
    if entry is not None:
        options["entry"] = start[keep]
    try:
        chi, _ = survdiff(time[keep], event[keep].astype(float), codes[keep], **options)
        chi = float(chi)
    except np.linalg.LinAlgError:  # e.g. every event in one group at a time when only it is at risk
        chi, df = math.nan, 0
    return observed, expected, chi, df


def _same_terms_error():
    return SimplydataError("The model cannot be fitted: two of the terms say the same thing "
                           "(or a term has the same value in every row with an event).")


def cox_fit(time, event, x, strata=None, entry=None) -> dict:
    """Cox model with Efron's ties, statsmodels PHReg (as R coxph()); strata= gives each stratum its own
    baseline (R + strata()), entry= each row its start time (R Surv(start, stop, event))."""
    from statsmodels.duration.hazard_regression import PHReg

    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=bool)
    x = np.asarray(x, dtype=float)
    x = x - x.mean(axis=0)  # as R: centring changes no result, but keeps exp() in range
    model = PHReg(time, x, status=event.astype(float), ties="efron", strata=strata,
                  entry=None if entry is None else np.asarray(entry, dtype=float))
    with warnings.catch_warnings(), np.errstate(all="ignore"):
        warnings.simplefilter("ignore")
        try:
            result = model.fit(maxiter=COX_STEPS)
            var = np.asarray(result.cov_params())
        except np.linalg.LinAlgError:
            raise _same_terms_error() from None
    beta = np.asarray(result.params)
    if not np.all(np.isfinite(var)):
        raise _same_terms_error()
    # settled: the score is (close to) zero at the answer
    converged = bool(np.all(np.isfinite(beta)) and np.max(np.abs(model.score(beta))) < 1e-4)
    return dict(beta=beta, var=var, loglik0=float(model.loglike(np.zeros(x.shape[1]))), loglik=float(result.llf),
                converged=converged, x=x)


def cox_zph(time, event, fit, terms, strata=None, entry=None) -> dict:
    """R survival::cox.zph(fit) (transform = "km"), through R: (chi-square, df, p) for each
    term, then GLOBAL; and Harrell's C of the same fit, survival::concordance() with its standard error.
    terms: a list of column-index lists, one per term; each term goes into R as one matrix, so R tests it as
    one term. strata: the stratum of each row (+ survival::strata()); entry: the start times (Surv(start, stop,
    event)). Raises RMissing when R is not ready."""
    from .._r import r_call

    x = np.asarray(fit["x"], dtype=float)
    values = {f"m{i}": x[:, cols] for i, cols in enumerate(terms)}
    formula = " + ".join(values)
    if strata is not None:
        values["s"] = np.array([str(v) for v in strata], dtype=object)
        formula += " + survival::strata(s)"
    surv = "survival::Surv(time, event)"
    if entry is not None:
        values["start"] = np.asarray(entry, dtype=float)
        surv = "survival::Surv(start, time, event)"
    found = r_call(
        f"fit <- survival::coxph({surv} ~ {formula}, ties = 'efron'); "
        "cc <- survival::concordance(fit); "
        "list(zph = survival::cox.zph(fit, transform = 'km')$table, c = cc$concordance, c_se = sqrt(cc$var))",
        packages=("survival",), source="survival::cox.zph",
        what="The proportional-hazards check (R survival::cox.zph())",
        python_note="lifelines proportional_hazard_test is a similar check but gives different numbers",
        time=np.asarray(time, dtype=float), event=np.asarray(event, dtype=bool), **values)
    table = np.asarray(found["zph"], dtype=float)
    table = table.reshape(len(terms) + 1, 3, order="F") if table.ndim == 1 else table
    return dict(table=[(float(chi), int(round(df)), float(p)) for chi, df, p in table],
                c=float(np.asarray(found["c"]).reshape(-1)[0]), c_se=float(np.asarray(found["c_se"]).reshape(-1)[0]))


def _ratio(log_value) -> float:
    """exp() that gives infinity instead of an error for a coefficient heading to infinity
    (all events in one group: complete separation)."""
    try:
        return math.exp(log_value)
    except OverflowError:
        return math.inf


def _show(value) -> str:
    """A median time for a sentence: "not reached" when there is none."""
    if math.isnan(value):
        return "not reached"
    return f"{value:.6g}"


def _surv(time, event, yes, entry=None) -> str:
    """The R Surv() call for a sentence: Surv(days, died == "yes") for a text event column."""
    status = f"{event} == {yes}" if yes.startswith('"') else event
    return f"Surv({entry}, {time}, {status})" if entry else f"Surv({time}, {status})"


def group_order(keys):
    """Group names A to Z (numbers by size), as the other test words sort them."""
    return sorted(set(keys), key=lambda k: (str(type(k)), k))


def _r_vector(values) -> str:
    return "c(" + ", ".join(_whole(v) for v in values) + ")"


# ---------------------------------------------------------------------------- the words
class SurvivalWords:
    def _survival_data(self, step, time, event, extra=(), example="", value=None, followed_from=None):
        """time (floats), event (bools), the used columns as lists, the value that counts as the event, and the
        start times of followed_from= (None without it). Rows with an empty cell in any of these columns are
        skipped with a note (an empty start time is refused: silence would hide a data error)."""
        times, kept, entries, rows = self._survival_rows(step, time, event, extra, example, followed_from)
        events, yes = read_event(kept[event], event, value, time)
        return times, events, kept, yes, entries

    def _survival_rows(self, step, time, event, extra, example, followed_from=None):
        _need(step, "time=", time, example)
        _need(step, "event=", event, example)
        if followed_from is not None:
            _need(step, "followed_from=", followed_from, example)
            if followed_from in (time, event):
                raise SimplydataError(f'"{followed_from}" cannot be both followed_from= and time= or event=.')
        columns = list(dict.fromkeys([time, event] + list(extra) + ([followed_from] if followed_from else [])))
        self._need_columns(*columns)
        if time == event:
            raise SimplydataError(f'"{time}" cannot be both time= and event=.\nFor example, {example}')
        values = {c: self._frame[c].to_list() for c in columns}
        n = len(self._frame)
        if followed_from is not None:
            empty = [i for i in range(n) if is_empty(values[followed_from][i])]
            if empty:
                raise SimplydataError(f'followed_from="{followed_from}" has {len(empty)} empty '
                                      f"{'cell' if len(empty) == 1 else 'cells'}. Each row needs the time its "
                                      "follow-up started (0 for rows followed from the start).")
        keep = [i for i in range(n) if not any(is_empty(values[c][i]) for c in columns)]
        _skipped_note(n - len(keep), [c for c in columns if any(is_empty(v) for v in values[c])])
        if not keep:
            raise SimplydataError(f"{step}() found no rows with {_list_words(repr(c) for c in columns)} all filled in.")
        kept = {c: [values[c][i] for i in keep] for c in columns}
        times = check_time(kept[time], time)
        entries = check_entry(kept[followed_from], times, followed_from, time, keep) if followed_from else None
        return times, kept, entries, keep

    @staticmethod
    def _event_sentence(event, yes, events, time, followed_from=None):
        start = f'from their "{followed_from}" ' if followed_from else ""
        return (f'The event is "{event}" = {yes} ({int(events.sum())} of {len(events)} rows); the other rows count as '
                f'followed {start}without the event until their "{time}" (censored).')

    @staticmethod
    def _group_codes(keys):
        order = group_order(keys)
        place = {k: i for i, k in enumerate(order)}
        return [_label(k) for k in order], np.array([place[k] for k in keys])

    def _check_for_each(self, step, for_each, time, event, example):
        _need(step, "for_each_group_in=", for_each, example)
        if for_each in (time, event):
            raise SimplydataError(f'"{for_each}" cannot be both for_each_group_in= and time= or event=.\nFor example, {example}')

    def _allowing(self, step, allowing_for, taken, stratify, example):
        """allowing_for= as a list of column names, checked: not one of the other columns, and (where it
        stratifies) no number columns (review: a number column would give one stratum per value)."""
        if allowing_for is None:
            return []
        columns = [allowing_for] if isinstance(allowing_for, str) else allowing_for
        if not isinstance(columns, (list, tuple)) or not columns or not all(isinstance(c, str) for c in columns):
            raise SimplydataError(f"allowing_for= needs a column name or a list of them.\nFor example, {example}")
        columns = list(columns)
        self._need_columns(*columns)
        for c in columns:
            if c in taken:
                raise SimplydataError(f'"{c}" cannot be in allowing_for= and also in time=, event=, using= or '
                                      "for_each_group_in=. Give each column one job.")
        if stratify:
            for c in columns:
                cells = [v for v in self._frame[c].to_list() if not is_empty(v)]
                if cells and all(_is_number(v) for v in cells):
                    raise SimplydataError(
                        f'allowing_for="{c}" holds numbers. allowing_for= gives each group of "{c}" its own baseline '
                        f"risk (a stratum), so a number column would give one stratum per value. To take a number "
                        f'into account, put it in using=:\n  table.{step}(..., using=[..., "{c}"])\n'
                        f'If the numbers are codes for groups (centre 1, 2, 3), make them text first: '
                        f'table.turn_into_text("{c}").')
        return columns

    @staticmethod
    def _strata(kept, columns):
        """The stratum of each row: the combination of the allowing_for= columns, and its name."""
        labels = [" / ".join(_label(kept[c][i]) for c in columns) for i in range(len(kept[columns[0]]))]
        names = group_order(labels)
        place = {k: i for i, k in enumerate(names)}
        return np.array([place[k] for k in labels]), names

    # ------------------------------------------------------------------ find_survival_over_time
    @friendly(renamed={"for_each": "for_each_group_in"}, others={"at_times": "at_time_points"})
    def find_survival_over_time(self, time=None, event=None, for_each_group_in=None, at_time_points=None,
                                method="kaplan-meier", allowing_for=None, followed_from=None,
                                average_time_up_to=None, value=None):
        """The share still without the event over time (Kaplan-Meier), with the median time.

        table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment")   (with sdata.get_example("trial"))
        time= is the time until the event or the end of follow-up; event= says whether the
        event happened (yes/no, True/False or 1/0; value="relapse" names the value that is the event).
        for_each_group_in= gives one curve per group.
        Prints the median time (by when half have had the event) with its 95 % CI per group,
        or says it was not reached, as R print(survfit(Surv(days, died == "yes") ~ treatment)).
        Gives back a table with one row per event time: the group, time, at risk, events,
        censored (since the previous row), survival and its 95 % CI (log scale, R's
        default), as R summary(survfit(...)). Draw the curves with chart.draw_survival_curves(...).
        An event column with three or more kinds (relapse, death, alive) is refused: use
        table.find_risk_over_time(...) for the chance of one event when another can come first.

        More: at_time_points=[365, 730] reads the survival at those times, one row per group and time
        (at_times= works too); a time after a group's last follow-up is left empty ("not followed that long").
        method="life table" gives the actuarial life table, with at_time_points= as the starts of the
        intervals, beginning at 0 (R KMsurv::lifetab; rows lost in an interval count as followed for half of
        it). average_time_up_to=365 gives, per group, the average time spent without the event in the first
        365 time units (the restricted mean survival time, R summary(survfit(), rmean = 365)).
        allowing_for=["age", "sex"] (with for_each_group_in=) gives curves adjusted for those columns: each
        row's curve is predicted as if in each group, then averaged over all rows (direct adjustment, R
        adjustedCurves; needs R), never the curve of an "average" row. followed_from="entry_age" gives each
        row the time its follow-up started (delayed entry: the row counts as at risk only after it).
        """
        step = "find_survival_over_time"
        example = EXAMPLE.format(word=step, more=', for_each_group_in="treatment"')
        method = _choice(step, "method", method, METHODS, METHOD_SPELLINGS)
        if for_each_group_in is not None:
            self._check_for_each(step, for_each_group_in, time, event, example)
        points = time_points(step, at_time_points) if at_time_points is not None else None
        allowing = self._allowing(step, allowing_for, {time, event, for_each_group_in}, False, example)
        asked = [o for o, v in (("method=\"life table\"", method == "life table"), ("allowing_for=", allowing),
                                ("average_time_up_to=", average_time_up_to is not None),
                                ("followed_from=", followed_from is not None)) if v]
        if len(asked) > 1:
            raise SimplydataError(f"{step}() answers one of these at a time: {_list_words(asked)}. Ask them in "
                                  "separate calls.")
        if method == "life table" and points is None:
            raise SimplydataError(f'method="life table" needs at_time_points=: the starts of the intervals, '
                                  f'beginning at 0.\nFor example, table.{step}(time="days", event="died", '
                                  'method="life table", at_time_points=[0, 365, 730])')
        if average_time_up_to is not None and points is not None:
            raise SimplydataError("average_time_up_to= and at_time_points= ask different questions; give one.")
        if allowing and not for_each_group_in:
            raise SimplydataError(f"allowing_for= needs for_each_group_in=: the curves of the groups are adjusted "
                                  f'for the other columns.\nFor example, table.{step}(time="days", event="died", '
                                  'for_each_group_in="treatment", allowing_for=["age"])')
        extra = ([for_each_group_in] if for_each_group_in else []) + allowing
        times, events, kept, yes, entries = self._survival_data(step, time, event, extra, example, value,
                                                                followed_from)
        if for_each_group_in:
            names, codes = self._group_codes(kept[for_each_group_in])
        else:
            names, codes = [None], np.zeros(len(times), dtype=int)
        print(self._event_sentence(event, yes, events, time, followed_from))
        if allowing:
            return self._adjusted_survival(time, event, yes, times, events, kept, names, codes, for_each_group_in,
                                           allowing, points)
        if method == "life table":
            return self._life_table(time, event, yes, times, events, names, codes, for_each_group_in, points)
        if average_time_up_to is not None:
            return self._restricted_means(step, time, event, yes, times, events, names, codes, for_each_group_in,
                                          average_time_up_to)
        if points is not None:
            return self._survival_at(time, event, yes, times, events, entries, names, codes, for_each_group_in,
                                     points, followed_from)
        columns = ["time", "at risk", "events", "censored", "survival", "95 % CI low", "95 % CI high"]
        keys = ("time", "at_risk", "events", "censored", "survival", "low", "high")
        out = {c: [] for c in ([for_each_group_in] if for_each_group_in else []) + columns}
        print("Median time until the event (by then half have had it), with its 95 % CI:")
        shaky = []
        for j, name in enumerate(names):
            rows = codes == j
            km = kaplan_meier(times[rows], events[rows], None if entries is None else entries[rows])
            if for_each_group_in:
                out[for_each_group_in] += [name] * len(km["time"])
            for c, key in zip(columns, keys):
                out[c] += [int(v) if c in ("at risk", "events", "censored") else float(v) for v in km[key]]
            if entries is not None and len(km["at_risk"]) and km["at_risk"][0] < 10:
                shaky.append((name, int(km["at_risk"][0])))
            med, low, high = median_time(km)
            who = f"{name}: " if for_each_group_in else ""
            count = f"{km['n']} rows, {km['total_events']} events"
            if not km["total_events"]:
                print(f"  {who}no events ({count}), so the median was not reached.")
            elif math.isnan(med):
                print(f"  {who}the median was not reached ({count}): more than half were still without the event "
                      f"at the end of follow-up (survival {_num(km['survival'][-1])} after the last event).")
            else:
                print(f'  {who}median "{time}" {_show(med)} (95 % CI {_show(low)} to {_show(high)}; {count}).')
        group = for_each_group_in if for_each_group_in else "1"
        print(f"Method: Kaplan-Meier estimate with 95 % confidence intervals on the log scale (Greenwood), "
              f"as R survfit({_surv(time, event, yes, followed_from)} ~ {group}).")
        if entries is not None and np.isin(entries[entries > 0], times).any():
            print("Note: some rows start where other rows end, as when one person's follow-up is split into rows by "
                  "a column that changes over time. Kaplan-Meier with start times is meant for rows that join late "
                  "(delayed entry); curves of groups of a column that changes over time are not the survival of "
                  "fixed groups. explain_survival(..., followed_from=) is the way to study such a column.")
        for name, n in shaky:
            who = f'"{name}": ' if name is not None else ""
            print(f"Note: {who}only {n} {'row was' if n == 1 else 'rows were'} followed at the first event, so the "
                  "start of the curve is shaky where few rows were followed (delayed entry).")
        return self._new_table(nw.from_dict(out, backend=self._frame.implementation))

    def _survival_at(self, time, event, yes, times, events, entries, names, codes, for_each, points, followed_from):
        """find_survival_over_time(at_time_points=): the Kaplan-Meier survival read at the times asked."""
        columns = ["time", "at risk", "events by then", "survival", "95 % CI low", "95 % CI high"]
        out = {c: [] for c in ([for_each] if for_each else []) + columns}
        print("Survival (the share still without the event) at the times asked, with its 95 % CI:")
        after = []
        for j, name in enumerate(names):
            rows = codes == j
            t, e = times[rows], events[rows]
            start = np.full(len(t), -np.inf) if entries is None else entries[rows]
            km = kaplan_meier(t, e, None if entries is None else entries[rows])
            who = f"{name}, " if for_each else ""
            for point in points:
                place = int(np.searchsorted(km["all_time"], point, side="right")) - 1
                at_risk = int(((t >= point) & (start < point)).sum())
                if point > km["end"]:
                    s = low = high = math.nan
                    after.append((name, point, km["end"]))
                    print(f'  {who}at "{time}" {_whole(point)}: not followed that long (the last "{time}" is '
                          f"{_whole(km['end'])}), so it is left empty.")
                else:
                    if place < 0:
                        s, low, high = 1.0, 1.0, 1.0
                    else:
                        s, low, high = (float(km["all_survival"][place]), float(km["all_low"][place]),
                                        float(km["all_high"][place]))
                    print(f'  {who}at "{time}" {_whole(point)}: {_pct(s)} still without the event (95 % CI '
                          f"{_pct(low)} to {_pct(high)}; {at_risk} still followed).")
                if for_each:
                    out[for_each].append(name)
                out["time"].append(float(point))
                out["at risk"].append(at_risk)
                out["events by then"].append(int((e & (t <= point)).sum()))
                out["survival"].append(s)
                out["95 % CI low"].append(low)
                out["95 % CI high"].append(high)
        group = for_each if for_each else "1"
        print(f"Method: Kaplan-Meier estimate read at those times, with 95 % confidence intervals on the log scale "
              f"(Greenwood), as R summary(survfit({_surv(time, event, yes, followed_from)} ~ {group}), times = "
              f"{_r_vector(points)}, extend = TRUE).")
        if after:
            print("Note: after a group's last follow-up the survival is left empty; R's extend = TRUE would carry the "
                  "last value on, which no row was followed long enough to show.")
        return self._new_table(nw.from_dict(out, backend=self._frame.implementation))

    def _life_table(self, time, event, yes, times, events, names, codes, for_each, points):
        """find_survival_over_time(method="life table"): the actuarial life table of R KMsurv::lifetab. simplydata
        counts the rows that start each interval, are lost (followed without the event to a time in it) or have
        the event in it; lifetab does the rest."""
        from .survival_r import life_table

        if points[0] != 0:
            raise SimplydataError("The intervals of a life table start at 0: at_time_points= are the starts of the "
                                  "intervals, for example at_time_points=[0, 365, 730, 1095].")
        columns = ["interval start", "interval end", "at start", "lost", "events", "effective at risk",
                   "survival at the start", "standard error of survival", "hazard", "standard error of hazard"]
        out = {c: [] for c in ([for_each] if for_each else []) + columns}
        print('Actuarial life table: rows lost in an interval count as followed for half of it (the actuarial '
              'assumption), so "effective at risk" is the number at the start minus half the lost rows.')
        ends = list(points[1:]) + [math.nan]
        for j, name in enumerate(names):
            rows = codes == j
            t, e = times[rows], events[rows]
            place = np.searchsorted(points, t, side="right") - 1  # the interval of each row (counting)
            lost = np.bincount(place[~e], minlength=len(points)).astype(float)
            had = np.bincount(place[e], minlength=len(points)).astype(float)
            lt = life_table(points, len(t), lost, had)
            if for_each:
                print(f"  {name}:")
                out[for_each] += [name] * len(points)
            for i, start in enumerate(points):
                end = "end" if math.isnan(ends[i]) else _whole(ends[i])
                print(f"    {_whole(start)} to {end}: {int(lt['nsubs'][i])} at the start, {int(lt['nlost'][i])} lost, "
                      f"{int(lt['nevent'][i])} with the event; effective at risk {_num(lt['nrisk'][i])}; survival at "
                      f"the start {_num(lt['surv'][i])}.")
            out["interval start"] += [float(p) for p in points]
            out["interval end"] += [float(v) for v in ends]
            for c, key in (("at start", "nsubs"), ("lost", "nlost"), ("events", "nevent")):
                out[c] += [int(v) for v in lt[key]]
            for c, key in (("effective at risk", "nrisk"), ("survival at the start", "surv"),
                           ("standard error of survival", "se_surv"), ("hazard", "hazard"),
                           ("standard error of hazard", "se_hazard")):
                out[c] += [float(v) for v in lt[key]]
        print(f"Method: actuarial life table with intervals starting at {_list_words(_whole(p) for p in points)} (the "
              f'last open), as R KMsurv::lifetab(tis, ninit, nlost, nevent) on the counts of "{time}" and "{event}" = '
              f"{yes}.")
        return self._new_table(nw.from_dict(out, backend=self._frame.implementation))

    def _up_to(self, step, up_to, times, codes, names):
        """average_time_up_to=: a number above 0, at most the last follow-up time of the group followed the
        shortest (survRM2 needs every group followed that long)."""
        if isinstance(up_to, bool) or not _is_number(up_to) or not up_to > 0:
            raise SimplydataError(f"average_time_up_to= needs a time above 0 on the time= clock, for example "
                                  "average_time_up_to=365.")
        last = [float(times[codes == j].max()) for j in range(len(names))]
        largest = min(last)
        if float(up_to) > largest:
            shortest = names[int(np.argmin(last))]
            who = f' (the last follow-up of "{shortest}")' if shortest is not None else " (the last follow-up)"
            raise SimplydataError(f"average_time_up_to= can be at most {_whole(largest)}{who}: every group must be "
                                  f"followed that long. Try average_time_up_to={_whole(largest)} or less.")
        return float(up_to)

    def _restricted_means(self, step, time, event, yes, times, events, names, codes, for_each, up_to):
        """find_survival_over_time(average_time_up_to=): the restricted mean survival time of each group."""
        from .survival_r import restricted_means

        up_to = self._up_to(step, up_to, times, codes, names)
        labels = [name if name is not None else "all rows" for name in names]
        groups = [labels[c] for c in codes]
        rmean, se = restricted_means(times, events, groups, labels, up_to)
        print(f'The average time without the event in the first {_whole(up_to)} "{time}" (restricted mean survival '
              "time, RMST):")
        for name, m, s in zip(names, rmean, se):
            who = f"{name} " if for_each else "the rows "
            print(f'  {who}spent on average {_num(m)} of the first {_whole(up_to)} "{time}" without the event '
                  f"(standard error {_num(s)}).")
        group = for_each if for_each else "1"
        print(f"Method: the area under the Kaplan-Meier curve up to {_whole(up_to)}, as R "
              f"summary(survfit({_surv(time, event, yes)} ~ {group}), rmean = {_whole(up_to)})$table.")
        out = {for_each: list(names)} if for_each else {}
        out.update({"up to": [up_to] * len(names), "average time without the event": [float(v) for v in rmean],
                    "standard error": [float(v) for v in se]})
        return self._new_table(nw.from_dict(out, backend=self._frame.implementation))

    def _adjusted_survival(self, time, event, yes, times, events, kept, names, codes, for_each, allowing, points):
        """find_survival_over_time(allowing_for=): survival curves adjusted by direct adjustment (adjustedCurves)."""
        from .survival_r import adjusted_curves

        columns = {c: (kept[c], not all(_is_number(v) for v in kept[c])) for c in allowing}
        if points is not None:
            late = points[points >= times.max()]
            if len(late):
                print(f"Note: {_list_words(_whole(p) for p in late)} {'is' if len(late) == 1 else 'are'} not before "
                      f'the last "{time}" ({_whole(times.max())}); adjusted curves are not carried past it, so '
                      f"{'it is' if len(late) == 1 else 'they are'} left out.")
                points = points[points < times.max()]
                if not len(points):
                    raise SimplydataError(f'Every time in at_time_points= is at or after the last "{time}" '
                                          f"({_whole(times.max())}); give earlier times.")
        found = adjusted_curves(times, events.astype(float), [names[c] for c in codes], names, columns, at=points)
        shown = _list_words(f'"{c}"' for c in allowing)
        print(f'Curves adjusted for {shown}: each row\'s curve was predicted as if it were in each "{for_each}" '
              f"group, then averaged over all {int(found['rows'][0])} rows (direct adjustment). They are not the "
              'curves of an "average" row with the average of each column.')
        medians = dict(zip(found["median_group"], found["median"]))
        print("Adjusted median time until the event:")
        for name in names:
            m = medians.get(str(name), math.nan)
            print(f'  {name}: {"not reached" if math.isnan(m) else _num(m)}.')
        terms = " + ".join([for_each] + allowing)
        print(f"Method: direct adjustment over a Cox model, as R adjustedCurves::adjustedsurv(variable = "
              f'"{for_each}", method = "direct", outcome_model = coxph({_surv(time, event, yes)} ~ {terms}, x = TRUE), '
              "conf_int = TRUE) (95 % intervals from the standard errors of riskRegression).")
        out = {for_each: list(found["group"]), "time": [float(v) for v in found["time"]],
               "survival": [float(v) for v in found["survival"]], "95 % CI low": [float(v) for v in found["low"]],
               "95 % CI high": [float(v) for v in found["high"]]}
        return self._new_table(nw.from_dict(out, backend=self._frame.implementation))

    # ------------------------------------------------------------------ compare_survival
    @friendly(renamed={"for_each": "for_each_group_in"})
    def compare_survival(self, time=None, event=None, for_each_group_in=None, allowing_for=None, followed_from=None,
                         average_time_up_to=None, value=None, competing_with=None):
        """Do the groups really differ in the time until the event? (log-rank test)

        table.compare_survival(time="days", event="died", for_each_group_in="treatment")   (with sdata.get_example("trial"))
        The log-rank test, as R survdiff(Surv(days, died == "yes") ~ treatment): at each event
        time the events are shared out over the groups by how many rows are at risk in each,
        and the observed events are compared with these expected ones over the whole
        follow-up. Prints the answer in words and the observed vs expected events per group;
        gives back a one-row table of results.

        More: allowing_for="centre" compares the groups within each centre and adds the results up (the
        stratified log-rank test, R survdiff(... + strata(centre))); a column of text only.
        followed_from="entry_day" gives each row the time its follow-up started (R has no survdiff for this;
        the same test in R is the score test of coxph(Surv(entry_day, days, died) ~ group, ties = "exact")).
        average_time_up_to=365 adds the average time without the event in the first 365 time units in each
        group and, for two groups, their difference and ratio (R survRM2::rmst2): easier to read than a hazard
        ratio, and right when hazards are not proportional. value="relapse", competing_with="death" gives
        Gray's test of the chance of relapse when death can come first (R cmprsk::cuminc).
        """
        step = "compare_survival"
        example = EXAMPLE.format(word=step, more=', for_each_group_in="treatment"')
        self._check_for_each(step, for_each_group_in, time, event, example)
        allowing = self._allowing(step, allowing_for, {time, event, for_each_group_in}, True, example)
        if competing_with is not None:
            if followed_from is not None or average_time_up_to is not None:
                raise SimplydataError("competing_with= (Gray's test) works without followed_from= and "
                                      "average_time_up_to=.")
            return self._grays_test(step, time, event, value, competing_with, for_each_group_in, allowing, example)
        if allowing and followed_from is not None:
            raise SimplydataError("compare_survival() takes allowing_for= or followed_from=, not both at once: "
                                  "statsmodels' stratified log-rank test cannot use start times. Compare within "
                                  "each group with table.keep_rows_where(...) first, or use explain_survival(..., "
                                  "allowing_for=, followed_from=).")
        if average_time_up_to is not None and (allowing or followed_from is not None):
            raise SimplydataError("average_time_up_to= works without allowing_for= and followed_from= (R survRM2 "
                                  "takes neither).")
        times, events, kept, yes, entries = self._survival_data(step, time, event, [for_each_group_in] + allowing,
                                                                example, value, followed_from)
        names, codes = self._group_codes(kept[for_each_group_in])
        k = len(names)
        if k < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each_group_in}"; it found only "{names[0]}".')
        if not events.any():
            raise SimplydataError(f'{step}() found no events ("{event}" = {yes}) in any group, so there is nothing '
                                  "to compare.")
        from scipy import stats

        strata, strata_names = self._strata(kept, allowing) if allowing else (None, [])
        observed, expected, chi, df = log_rank(times, events, codes, k, entry=entries, strata=strata)
        p = float(stats.chi2.sf(chi, df)) if df > 0 else math.nan
        print(self._event_sentence(event, yes, events, time, followed_from))
        within = ""
        if allowing:
            shown = _list_words(f'"{c}"' for c in allowing)
            within = f' within each {shown} group'
            print(f"Allowing for {shown}: the groups are compared within each of its {len(strata_names)} groups and "
                  "the results added up (stratified log-rank test).")
        counts = _list_words(f"{n} {_whole(o)} vs {_num(e)}" for n, o, e in zip(names, observed, expected))
        print(f'Events in each "{for_each_group_in}" group, observed vs expected if all groups were alike{within}: '
              f"{counts}.")
        print(_p_sentence(p, f"the groups truly had the same time until the event{within}",
                          "differences this big or bigger", "that the groups are alike"))
        rhs = for_each_group_in + "".join(f" + strata({c})" for c in allowing)
        if followed_from:
            print(f"Test: log-rank test with each row followed from its \"{followed_from}\" (chi-square = {_num(chi)}, "
                  f"df = {df}); R survdiff() takes no start times; the same test in R is the score test of "
                  f"coxph({_surv(time, event, yes, followed_from)} ~ {for_each_group_in}, ties = \"exact\"), "
                  "coxph()$score.")
        else:
            label = "stratified log-rank test" if allowing else "log-rank test"
            print(f"Test: {label} (chi-square = {_num(chi)}, df = {df}), as R survdiff({_surv(time, event, yes)} ~ "
                  f"{rhs}); it compares the whole curves, giving every event time the same weight.")
        left_out = [n for n, e in zip(names, expected) if not e > 0]
        if left_out:
            verb, them = ("is", "it has") if len(left_out) == 1 else ("are", "they have")
            quoted = _list_words('"' + n + '"' for n in left_out)
            print(f"Note: {quoted} {verb} left out of the test: {them} no rows still followed "
                  "at any event time, so no expected events (R survdiff leaves such groups out too).")
        if allowing:
            self._strata_notes(strata, strata_names, events, allowing)
        test = ("stratified log-rank test" if allowing else
                "log-rank test with start times" if followed_from else "log-rank test")
        row = {"test": test,
               "what it compares": f'the time until "{event}" = {yes} in each "{for_each_group_in}" ({", ".join(names)})',
               "statistic name": "chi-square", "statistic": chi, "degrees of freedom": float(df), "p-value": p}
        for j, name in enumerate(names):
            row[f"count in {name}"] = int((codes == j).sum())
            row[f"events in {name}"] = int(observed[j])
            row[f"expected events in {name}"] = float(expected[j])
        if average_time_up_to is not None:
            row.update(self._compare_restricted_means(step, time, event, yes, times, events, names, codes,
                                                      average_time_up_to))
        return self._result_table(row)

    @staticmethod
    def _strata_notes(strata, strata_names, events, allowing):
        empty = [strata_names[s] for s in range(len(strata_names)) if not events[strata == s].any()]
        if empty:
            print(f"Note: {_list_words(repr(n) for n in empty[:6])} of {_list_words(repr(c) for c in allowing)} "
                  f"{'has' if len(empty) == 1 else 'have'} no events, so {'it adds' if len(empty) == 1 else 'they add'} "
                  "nothing to the result.")
        if len(strata_names) > MANY_STRATA:
            print(f"Note: {len(strata_names)} groups in allowing_for=: with many small groups each compares only a "
                  "few rows, which wastes information. Fewer, larger groups (or a number column in using=) may be "
                  "better.")

    def _compare_restricted_means(self, step, time, event, yes, times, events, names, codes, up_to):
        """compare_survival(average_time_up_to=): each group's restricted mean survival time and, for two groups,
        their difference and ratio with R survRM2::rmst2 (arm 1 = the second group)."""
        from .survival_r import restricted_means, rmst_difference

        up_to = self._up_to(step, up_to, times, codes, names)
        if len(names) != 2:
            rmean, se = restricted_means(times, events, [names[c] for c in codes], names, up_to)
            print(f'The average time without the event in the first {_whole(up_to)} "{time}" (restricted mean '
                  "survival time, RMST):")
            for name, m, s in zip(names, rmean, se):
                print(f"  {name} spent on average {_num(m)} (standard error {_num(s)}).")
            print("Note: the difference in average time is given for two groups; keep two groups first, for example "
                  "with table.keep_rows_where(...).")
            return {f"average time up to {_whole(up_to)} in {n}": float(m) for n, m in zip(names, rmean)}
        found = rmst_difference(times, events.astype(float), (codes == 1).astype(float), up_to)
        first, second = names
        a0, a1 = found["arm0"], found["arm1"]
        print(f'In the first {_whole(up_to)} "{time}", "{second}" spent on average {_num(a1[0])} without the event '
              f'(95 % CI {_num(a1[2])} to {_num(a1[3])}) and "{first}" {_num(a0[0])} (95 % CI {_num(a0[2])} to '
              f"{_num(a0[3])}) (restricted mean survival time, RMST).")
        est, low, high, pv = found["estimate"], found["low"], found["high"], found["p"]
        print(f'Difference ("{second}" minus "{first}"): {_num(est[0])} "{time}" (95 % CI {_num(low[0])} to '
              f"{_num(high[0])}); ratio {_num(est[1])} (95 % CI {_num(low[1])} to {_num(high[1])}).")
        print(_p_sentence(float(pv[0]), f'the average time without the event in the first {_whole(up_to)} "{time}" '
                                        "were truly the same in both groups", "a difference this big or bigger",
                          "that the averages are the same"))
        print(f'Method: R survRM2::rmst2(time, status, arm, tau = {_whole(up_to)}), arm 1 = "{second}".')
        return {"up to": up_to, f"average time in {first}": float(a0[0]), f"average time in {second}": float(a1[0]),
                "difference in average time": float(est[0]), "difference 95 % CI low": float(low[0]),
                "difference 95 % CI high": float(high[0]), "difference p-value": float(pv[0]),
                "ratio of average times": float(est[1]), "ratio 95 % CI low": float(low[1]),
                "ratio 95 % CI high": float(high[1])}

    def _grays_test(self, step, time, event, value, competing_with, for_each, allowing, example):
        """compare_survival(value=, competing_with=): Gray's test of the chance of the event between groups."""
        from .survival_r import grays_test

        times, kept, _, _ = self._survival_rows(step, time, event, [for_each] + allowing, example)
        states, kinds, others = read_states(kept[event], event, value, competing_with, time, step)
        names, codes = self._group_codes(kept[for_each])
        if len(names) < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each}"; it found only "{names[0]}".')
        if not (states == 1).any():
            raise SimplydataError(f"{step}() found no rows with {kinds[0]}, so there is nothing to compare.")
        strata = None
        if allowing:
            strata, _ = self._strata(kept, allowing)
        tests = grays_test(times, states, [names[c] for c in codes], names, strata)
        counts = _list_words(f"{k} ({int((states == i).sum())} rows)" for i, k in enumerate(kinds, start=1))
        print(f'The events in "{event}": {counts}; {kinds[0]} is the event asked about, '
              f"{_list_words(kinds[1:])} {'competes' if len(kinds) == 2 else 'compete'} with it (can come first).")
        print(others_sentence(others, event))
        stat, p, df = tests.get(1, (math.nan, math.nan, 0))
        rival = _list_words(kinds[1:])
        print(f'Gray\'s test for {kinds[0]} between the "{for_each}" groups (chi-square = {_num(stat)}, df = {df}):')
        within = f" within each {_list_words(repr(c) for c in allowing)} group" if allowing else ""
        print(_p_sentence(p, f"the groups truly had the same chance of {kinds[0]} over time (with {rival} as a "
                             f"competing event){within}", "differences this big or bigger", "that the groups are alike"))
        for i, kind in enumerate(kinds[1:], start=2):
            if i in tests:
                s2, p2, d2 = tests[i]
                print(f"For {kind} (the competing event) the same test gives chi-square = {_num(s2)}, df = {d2}, "
                      f"{_p_shown(p2)}.")
        print(f"Test: Gray's test of the chance of each event over time (cumulative incidence), as R "
              f"cmprsk::cuminc(ftime, fstatus, group{', strata' if allowing else ''}, cencode = 0)$Tests, with fstatus "
              f"1 = {kinds[0]}, " + ", ".join(f"{i} = {k}" for i, k in enumerate(kinds[1:], start=2))
              + ", 0 = every other value.")
        row = {"test": "Gray's test",
               "what it compares": f'the chance of "{event}" = {kinds[0]} over time in each "{for_each}" '
                                   f"({', '.join(names)}), with {rival} competing",
               "statistic name": "chi-square", "statistic": stat, "degrees of freedom": float(df), "p-value": p}
        for j, name in enumerate(names):
            row[f"count in {name}"] = int((codes == j).sum())
            row[f"events in {name}"] = int(((codes == j) & (states == 1)).sum())
        return self._result_table(row)

    # ------------------------------------------------------------------ explain_survival
    def _cox_columns(self, using, kept, n_rows):
        """The model columns: numbers as they are, text and True/False as groups vs the first."""
        columns, names, terms = [], [], []
        for column in using:
            values = kept[column]
            if all(_is_number(v) for v in values):
                values = np.asarray(values, dtype=float)
                if np.ptp(values) == 0:
                    raise SimplydataError(f'"{column}" has the same value in every row, so it cannot explain anything.')
                terms.append([len(columns)])
                columns.append(values)
                names.append((column, None, None))
                continue
            keys = [bool(v) if isinstance(v, (bool, np.bool_)) else str(v) for v in values]
            order = group_order(keys)
            if len(order) < 2:
                raise SimplydataError(f'"{column}" has only one group ("{order[0]}"), so it cannot explain anything.')
            if len(order) > max(20, n_rows // 2):
                raise SimplydataError(f'"{column}" has {len(order)} different values: too many groups to fit. '
                                      "Is it a column of numbers stored as text?")
            cols = []
            for level in order[1:]:
                cols.append(len(columns))
                columns.append(np.array([k == level for k in keys], dtype=float))
                names.append((column, _label(level), _label(order[0])))
            terms.append(cols)
        return np.column_stack(columns), names, terms

    @friendly
    def explain_survival(self, time=None, event=None, using=None, allowing_for=None, followed_from=None, value=None,
                         competing_with=None, method="cox", distribution=None):
        """Which columns go with a higher or lower risk of the event? (Cox model, hazard ratios)

        table.explain_survival(time="days", event="died", using=["treatment", "age"])   (with sdata.get_example("trial"))
        The Cox proportional hazards model, as R coxph(Surv(days, died == "yes") ~ treatment +
        age), with Efron's method for tied times. A hazard ratio above 1 means a higher risk
        of the event at any moment (2 = twice the risk), below 1 a lower risk. Numbers count
        per 1 more; text columns are groups compared with the first group (A to Z). Prints
        each hazard ratio with its 95 % CI and p-value, and the likelihood-ratio test of the
        whole model; a note says if a hazard ratio seems to change over time (the
        proportional-hazards check of R cox.zph()), and, with R, Harrell's C: how often the model ranks
        two rows the right way (measured on the rows it was fitted to, so likely too high for new rows).
        Gives back a table with one row per term.

        More: allowing_for="centre" gives each centre its own baseline risk (a stratified Cox model, R +
        strata(centre)): no hazard ratio for centre; using= would estimate one. A text column only.
        followed_from="entry_day" gives each row the time its follow-up started (R Surv(entry_day, days,
        died)). This is also how to avoid immortal time: a treatment that starts on day 40 becomes two rows,
        0 to 40 untreated and 40 to the end treated, each with followed_from= its start.
        value="relapse", competing_with="death" (the event column has kinds): the cause-specific hazard ratios
        of relapse, with death counted as the end of follow-up (method="cox", the default; "cause-specific"
        works too); method="fine-gray" gives the Fine-Gray model of the chance of relapse by each time
        (subdistribution hazard ratios, R cmprsk::crr). distribution="weibull" ("exponential", "lognormal",
        "log-logistic") fits a parametric model instead (R survival::survreg) and gives time ratios: how many
        times as long the time until the event is.
        """
        step = "explain_survival"
        example = EXAMPLE.format(word=step, more=', using=["treatment", "age"]')
        asked_cause_specific = isinstance(method, str) and method.strip().lower().startswith("cause")
        method = _choice(step, "method", method, MODEL_METHODS, MODEL_SPELLINGS)
        dist = (_choice(step, "distribution", distribution, DISTRIBUTIONS, DISTRIBUTION_SPELLINGS)
                if distribution is not None else None)
        if isinstance(using, str):
            using = [using]
        if not using or not all(isinstance(u, str) for u in using):
            raise SimplydataError(f"{step}() needs using= with one or more column names.\nFor example, {example}")
        using = list(using)
        repeated = [u for i, u in enumerate(using) if u in using[:i]]
        if repeated:
            raise SimplydataError(f'"{repeated[0]}" is in using= twice. Give each column once.')
        if time in using or event in using:
            raise SimplydataError(f"using= cannot hold the time= or event= column.\nFor example, {example}")
        allowing = self._allowing(step, allowing_for, {time, event, *using}, True, example)
        if method == "fine-gray" and competing_with is None:
            raise SimplydataError('method="fine-gray" needs value= and competing_with=: the Fine-Gray model is about '
                                  "the chance of one event when another can come first.\nFor example, "
                                  'table.explain_survival(time="months", event="outcome", value="relapse", '
                                  'competing_with="death", using=["age"], method="fine-gray")')
        if asked_cause_specific and competing_with is None:
            raise SimplydataError('method="cause-specific" needs value= and competing_with=: a cause-specific model '
                                  "is a Cox model of one event with the competing event counted as the end of "
                                  "follow-up.\nFor example, table.explain_survival(time=\"months\", event=\"outcome\", "
                                  'value="relapse", competing_with="death", using=["age"])')
        if dist is not None:
            others = [o for o, v in (("method=\"fine-gray\"", method == "fine-gray"),
                                     ("competing_with=", competing_with is not None), ("allowing_for=", allowing),
                                     ("followed_from=", followed_from is not None)) if v]
            if others:
                raise SimplydataError(f"distribution= chooses a parametric model, which works without "
                                      f"{_list_words(others)}. Leave distribution= out for a Cox model.")
        if method == "fine-gray" and (allowing or followed_from is not None):
            raise SimplydataError('method="fine-gray" (R cmprsk::crr) works without allowing_for= and followed_from=.')
        if competing_with is not None:
            times, kept, entries, _ = self._survival_rows(step, time, event, using + allowing, example, followed_from)
            states, kinds, others = read_states(kept[event], event, value, competing_with, time, step)
            events, yes = states == 1, kinds[0]
        else:
            times, events, kept, yes, entries = self._survival_data(step, time, event, using + allowing, example,
                                                                    value, followed_from)
            states, kinds, others = None, None, None
        if not events.any():
            raise SimplydataError(f'{step}() found no events ("{event}" = {yes}), so there is nothing to explain.')
        x, names, terms = self._cox_columns(using, kept, len(times))
        if x.shape[1] >= len(times):
            raise SimplydataError(f"{step}() needs more rows than terms: {len(times)} rows for {x.shape[1]} terms.")
        if dist is not None:
            return self._explain_parametric(time, event, yes, times, events, x, names, using, dist)
        if method == "fine-gray":
            return self._explain_fine_gray(time, event, times, states, kinds, others, x, names, using)
        return self._explain_cox(time, event, yes, times, events, kept, x, names, terms, using, allowing, entries,
                                 followed_from, kinds, others, states)

    def _explain_cox(self, time, event, yes, times, events, kept, x, names, terms, using, allowing, entries,
                     followed_from, kinds, others, states):
        from scipy import stats

        strata, strata_names = self._strata(kept, allowing) if allowing else (None, [])
        tied = int(np.isin(entries, times[events]).sum()) if entries is not None else 0
        if tied:  # R's (start, stop]: a row is not at risk at an event time equal to its start; statsmodels says it is
            from .survival_r import cox_start_stop

            fit = cox_start_stop(times, events, x, entries, strata)
        else:
            fit = cox_fit(times, events, x, strata=strata, entry=entries)
        beta, se = fit["beta"], np.sqrt(np.diag(fit["var"]))
        z = beta / se
        p = 2 * stats.norm.sf(np.abs(z))
        lr = 2 * (fit["loglik"] - fit["loglik0"])
        df = len(beta)
        lr_p = float(stats.chi2.sf(lr, df))
        from .._r import RMissing

        r_notes = io.StringIO()  # R's notes go with the other notes, after the results
        try:
            with contextlib.redirect_stdout(r_notes):
                checked = cox_zph(times, events, fit, terms, strata=strata, entry=entries)
            zph, concordance, zph_missing = checked["table"], (checked["c"], checked["c_se"]), None
        except RMissing as missing:  # the model stands without R; only the check is left out
            zph, concordance = [(math.nan, len(cols), math.nan) for cols in terms + [[]]], None
            zph_missing = str(missing)
        term_of = {c: i for i, cols in enumerate(terms) for c in cols}
        rival = _list_words(kinds[1:]) if kinds else ""
        if kinds:
            counts = _list_words(f"{k} ({int((states == i).sum())} rows)" for i, k in enumerate(kinds, start=1))
            print(f'The events in "{event}": {counts}; {kinds[0]} is the event asked about and {rival} counts as '
                  "the end of follow-up (it competes: it can come first).")
            print(others_sentence(others, event))
            print(f"Cause-specific hazard ratios from {len(times)} rows with {int(events.sum())} events of {kinds[0]} "
                  f"(the risk of {kinds[0]} at any moment among those still free of both events; above 1: a higher "
                  "risk, below 1: a lower risk):")
        else:
            print(self._event_sentence(event, yes, events, time, followed_from))
            print(f"Hazard ratios from {len(times)} rows with {int(events.sum())} events (above 1: a higher risk of "
                  "the event at any moment; below 1: a lower risk):")
        rows = []
        ratio_name = "cause-specific hazard ratio" if kinds else "hazard ratio"
        for i, (column, level, base) in enumerate(names):
            hr, low, high = _ratio(beta[i]), _ratio(beta[i] - Z95 * se[i]), _ratio(beta[i] + Z95 * se[i])
            what = f'each 1 more "{column}"' if level is None else f'"{column}" {level} vs {base}'
            print(f"  {what}: {ratio_name} {_num(hr)} (95 % CI {_num(low)} to {_num(high)}); {_p_clause(float(p[i]))}.")
            rows.append({"term": column if level is None else f"{column}: {level} vs {base}",
                         "hazard ratio": hr, "95 % CI low": low, "95 % CI high": high,
                         "coefficient": float(beta[i]), "standard error": float(se[i]), "z": float(z[i]),
                         "p-value": float(p[i]), "proportional hazards check p-value": zph[term_of[i]][2]})
        if allowing:
            shown = _list_words(f'"{c}"' for c in allowing)
            print(f"Allowing for {shown}: each of its {len(strata_names)} groups has its own baseline risk, so there "
                  f"is no hazard ratio for {shown}.")
        print(f"The model as a whole (likelihood-ratio test, chi-square = {_num(lr)}, df = {df}): "
              f"{_p_clause(lr_p, 'none of the columns truly mattered')}.")
        if concordance is not None:
            c, c_se = concordance
            print(f"Harrell's C = {_num(c)} (standard error {_num(c_se)}): in {_pct(c)} of the pairs where one row had "
                  "the event first, the model gave that row the higher risk; 0.5 is a coin toss. Measured on the rows "
                  "the model was fitted to, so it is likely too high for new rows.")
        status = f"{event} == {kinds[0]}" if kinds else None
        surv = (f"Surv({followed_from + ', ' if followed_from else ''}{time}, {status})" if kinds
                else _surv(time, event, yes, followed_from))
        rhs = " + ".join(using) + "".join(f" + strata({c})" for c in allowing)
        label = "Cause-specific Cox model" if kinds else "Cox proportional hazards model"
        print(f"Method: {label}, Efron's method for tied times, as R coxph({surv} ~ {rhs}).")
        if kinds:
            print(f'Note: these hazard ratios are about the risk of {kinds[0]} among those still free of both events. '
                  f'For the chance of {kinds[0]} by each time, when {rival} can come first, use method="fine-gray" '
                  "here, and table.find_risk_over_time(...) for the curves.")
        if not fit["converged"]:
            print(f"Note: the model did not settle after {COX_STEPS} steps; a hazard ratio may be heading to 0 or "
                  "infinity (for example a group with no events). Treat the numbers with care.")
        elif np.any(np.abs(beta) * np.std(fit["x"], axis=0) > 10):
            print("Note: a hazard ratio is extremely large or small; perhaps a group has no events or "
                  "all of them. Treat it with care.")
        if allowing:
            self._strata_notes(strata, strata_names, events, allowing)
        if tied:
            print(f"Note: {tied} {'row starts' if tied == 1 else 'rows start'} at an event time, as when one person's "
                  "follow-up is split into rows. R counts such a row as at risk only after its start, statsmodels "
                  "PHReg already at it (the person would count twice), so this model was fitted by R "
                  "survival::coxph(Surv(start, stop, event) ~ ...).")
        if zph_missing:
            print("Note: the proportional-hazards check was left out, and Harrell's C with it. " + zph_missing)
        if r_notes.getvalue():
            print(r_notes.getvalue(), end="")
        for i, cols in enumerate(terms):
            if zph[i][2] < 0.05:
                column = names[cols[0]][0]
                print(f'Note: the hazard ratio of "{column}" may change over time (proportional-hazards check as R '
                      f"cox.zph(), {_p_shown(zph[i][2])}), so it is an average over the follow-up. "
                      "chart.draw_survival_curves(...) shows how the curves run, and average_time_up_to= on "
                      "compare_survival gives a difference that needs no such assumption.")
        if zph[-1][2] < 0.05 and all(t[2] >= 0.05 for t in zph[:-1]):
            print(f"Note: the proportional-hazards check of the whole model has {_p_shown(zph[-1][2])} "
                  "(as R cox.zph()): some hazard ratio may change over time.")
        if concordance is not None:
            for r in rows:
                r["Harrell's C"] = concordance[0]
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _explain_fine_gray(self, time, event, times, states, kinds, others, x, names, using):
        """explain_survival(method="fine-gray"): subdistribution hazard ratios, R cmprsk::crr."""
        from .survival_r import fine_gray

        fit = fine_gray(times, states, x)
        rival = _list_words(kinds[1:])
        counts = _list_words(f"{k} ({int((states == i).sum())} rows)" for i, k in enumerate(kinds, start=1))
        print(f'The events in "{event}": {counts}; {kinds[0]} is the event asked about, {rival} competes with it.')
        print(others_sentence(others, event))
        print(f"Subdistribution hazard ratios for {kinds[0]} (Fine-Gray model) from {int(fit['n'][0])} rows. A "
              f"subdistribution hazard ratio above 1 means a higher chance of {kinds[0]} by each time; its size is not "
              "how many times higher. The risk curves (table.find_risk_over_time) show the size.")
        rows = []
        for i, (column, level, base) in enumerate(names):
            what = f'each 1 more "{column}"' if level is None else f'"{column}" {level} vs {base}'
            print(f"  {what}: subdistribution hazard ratio {_num(fit['ratio'][i])} (95 % CI {_num(fit['low'][i])} to "
                  f"{_num(fit['high'][i])}); {_p_clause(float(fit['p'][i]))}.")
            rows.append({"term": column if level is None else f"{column}: {level} vs {base}",
                         "subdistribution hazard ratio": float(fit["ratio"][i]), "95 % CI low": float(fit["low"][i]),
                         "95 % CI high": float(fit["high"][i]), "coefficient": float(fit["beta"][i]),
                         "standard error": float(fit["se"][i]), "z": float(fit["z"][i]), "p-value": float(fit["p"][i])})
        print(f"Method: Fine-Gray model with robust (sandwich) standard errors, as R cmprsk::crr(ftime, fstatus, "
              f"cov1 = {' + '.join(using)}, failcode = 1, cencode = 0), with fstatus 1 = {kinds[0]}, "
              + ", ".join(f"{i} = {k}" for i, k in enumerate(kinds[1:], start=2)) + ", 0 = every other value.")
        print(f"Note: for the risk of {kinds[0]} at any moment among those still free of both events (the "
              'cause-specific hazard ratios, best for asking what causes it), leave out method="fine-gray".')
        if not fit["converged"]:
            print("Note: cmprsk::crr did not settle; treat the numbers with care.")
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _explain_parametric(self, time, event, yes, times, events, x, names, using, dist):
        """explain_survival(distribution=): an accelerated failure time model, R survival::survreg."""
        from .survival_r import survival_regression

        zero = int((times <= 0).sum())
        if zero:
            raise SimplydataError(f'distribution="{dist}" needs times above 0 (it takes their logarithm), but '
                                  f'"{time}" is 0 in {zero} {"row" if zero == 1 else "rows"}. Check them, or use the '
                                  "Cox model (leave distribution= out).")
        fit = survival_regression(times, events, x, dist)
        print(self._event_sentence(event, yes, events, time))
        print(f"Time ratios ({dist} accelerated failure time model) from {len(times)} rows with {int(events.sum())} "
              "events: above 1, the time until the event is longer; below 1, shorter:")
        rows = []
        for i, (column, level, base) in enumerate(names):
            what = f'each 1 more "{column}"' if level is None else f'"{column}" {level} vs {base}'
            print(f"  {what}: the time until the event is {_num(fit['ratio'][i])} times as long (95 % CI "
                  f"{_num(fit['low'][i])} to {_num(fit['high'][i])}); {_p_clause(float(fit['p'][i]))}.")
            rows.append({"term": column if level is None else f"{column}: {level} vs {base}",
                         "time ratio": float(fit["ratio"][i]), "95 % CI low": float(fit["low"][i]),
                         "95 % CI high": float(fit["high"][i]), "coefficient": float(fit["beta"][i]),
                         "standard error": float(fit["se"][i]), "z": float(fit["z"][i]), "p-value": float(fit["p"][i])})
        if dist == "weibull":
            shape = float(fit["shape"][0])
            trend = "rises" if shape > 1 else "falls" if shape < 1 else "stays the same"
            print(f"Weibull shape {_num(shape)} (1 / survreg's scale): the risk of the event at any moment {trend} "
                  "over time.")
        print(f"AIC = {_num(fit['aic'][0])}: lower is a closer fit; compare it with another distribution= on the same "
              "rows.")
        r_dist = {"log-logistic": "loglogistic"}.get(dist, dist)
        print(f"Method: {dist} accelerated failure time model, as R survreg({_surv(time, event, yes)} ~ "
              f"{' + '.join(using)}, dist = \"{r_dist}\"); time ratios are exp(coefficient).")
        print("Note: a Cox model (leave distribution= out) gives hazard ratios instead, without choosing a "
              "distribution.")
        if not fit["converged"]:
            print("Note: survreg did not settle; treat the numbers with care.")
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)
