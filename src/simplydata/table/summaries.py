"""Summaries: averages, totals, counts, correlation. They never change the table.

Rules (the same as the rest of simplydata, see _stats.py):

* empty cells are skipped, and a short note says how many were skipped
* standard deviation uses the sample formula (divide by n - 1), like pandas and R
* without for_each_group_in= you get one plain number; with for_each_group_in= you get a NEW small table
  with one row per group, sorted by group. Rows with an empty group cell form their own
  group, shown last.
* every summary also prints its answer as one short sentence, so a script needs no print()
* every="month" (or "hour", "day", "week", "quarter", "year") groups a date column in
  for_each_group_in= into periods; each period is shown in the new table by its first day (a week
  starts on Monday, as ISO 8601)
* across="subject" gives a cross table: one row per for_each_group_in= group, one column per value
  of across= (pandas pivot_table / crosstab)
* percents are numbers from 0 to 100 (never fractions, never text); tables keep every
  digit, sentences show one decimal: 41.7 %. Percent intervals are Clopper-Pearson exact
  95 % intervals (R binom.test)
* the interquartile range uses the usual linear rule for quartiles (R type 7, NumPy and
  pandas default)

Correlation strength words (size of r, whichever direction), after Evans (1996):

    below 0.2   very weak
    0.2 - 0.4   weak
    0.4 - 0.6   medium
    0.6 - 0.8   strong
    0.8 - 1     very strong

The p-value sentence (the same in every word, _p_sentence): "If there were truly no link, a
link this strong or stronger would turn up in about 3 of 100 studies like this one (p = 0.031)."
Below p = 0.001 it says "fewer than 1 in 1000 studies".
"""

from __future__ import annotations

import datetime as _dt
import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._stats import _plain_name
from .conditions import _empty_in
from .rows import _NOT_GIVEN

# word -> (start of the result column name, narwhals calculation)
_SUMMARIES = {
    "find_average_of": ("average", lambda c: nw.col(c).mean()),
    "find_median_of": ("median", lambda c: nw.col(c).median()),
    "find_total_of": ("total", lambda c: nw.col(c).sum()),
    "find_smallest_of": ("smallest", lambda c: nw.col(c).min()),
    "find_biggest_of": ("biggest", lambda c: nw.col(c).max()),
    "find_standard_deviation_of": ("standard deviation", lambda c: nw.col(c).std(ddof=1)),
}

CORRELATION_METHODS = ("pearson", "spearman", "kendall", "somers", "gamma")
ORDINAL_METHODS = ("somers", "gamma")  # two columns, the measure with its interval from R DescTools
METHOD_NAMES = {"pearson": "Pearson", "spearman": "Spearman", "kendall": "Kendall's tau-b", "somers": "Somers' d",
                "gamma": "Goodman and Kruskal's gamma"}
CORRELATION_SHOW = ("r", "p-value", "each pair", "covariance")
STRONGEST_PAIRS = 3  # a correlation table prints this many of its strongest pairs

# every= : the time step -> narwhals truncate code (weeks are done by hand: Monday start)
EVERY = {"hour": "1h", "day": "1d", "week": None, "month": "1mo", "quarter": "1q", "year": "1y"}
EVERY_EXAMPLE = ('table.turn_into_dates("year")\n'
                 '              table.find_average_of("population", for_each_group_in="year", every="year")'
                 '   (with sdata.get_example("growth"))')

# find_summary_of(show=[...]): the measure names, the same as the _of words and chart show=/error=
MEASURES = ("count", "average", "median", "total", "smallest", "biggest", "standard deviation", "variance",
            "standard error", "confidence interval", "range", "interquartile range", "empty cells",
            "geometric mean", "skewness", "kurtosis", "coefficient of variation", "median absolute deviation",
            "trimmed average", "most common", "percentile", "harmonic mean", "winsorised average")
MEASURE_ALIASES = {"mean": "average", "sum": "total", "sd": "standard deviation", "se": "standard error",
                   "ci": "confidence interval", "iqr": "interquartile range", "geometric average": "geometric mean",
                   "gmean": "geometric mean", "skew": "skewness", "cv": "coefficient of variation",
                   "mad": "median absolute deviation", "trimmed mean": "trimmed average", "mode": "most common",
                   "quantile": "percentile", "harmonic average": "harmonic mean", "hmean": "harmonic mean",
                   "winsorized average": "winsorised average", "winsorized mean": "winsorised average",
                   "winsorised mean": "winsorised average"}
# measures worked out with NumPy / SciPy on each group's numbers (the others come from narwhals)
ARRAY_MEASURES = ("geometric mean", "skewness", "kurtosis", "coefficient of variation", "median absolute deviation",
                  "trimmed average", "most common", "percentile", "harmonic mean", "winsorised average")
TRIM_PERCENT = 10  # "trimmed average": 10 % cut from each end, unless another percent is given
WINSOR_PERCENT = 20  # "winsorised average": 20 % pulled in at each end (R WRS2::winmean(tr = 0.2))
MAD_CONSTANT = 1.4826  # R mad(): makes the median absolute deviation match the sd for bell-shaped values
LEAST_VALUES = {"skewness": 3, "kurtosis": 4}  # fewer values than this give an empty cell
DEFAULT_MEASURES = ("count", "average", "standard deviation", "smallest", "median", "biggest")
SUMMARY_LINES = 12  # find_summary_of prints at most this many rows; the table has them all


# lower edge of each band, biggest first
STRENGTH_WORDS = ((0.8, "very strong"), (0.6, "strong"), (0.4, "medium"), (0.2, "weak"), (0.0, "very weak"))


def _plain(value):
    """A plain Python number (not a NumPy one); empty becomes nan."""
    if value is None:
        return math.nan
    if hasattr(value, "item"):
        value = value.item()
    return value


def _as_list(step: str, option: str, value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)) and value and all(isinstance(v, str) for v in value):
        return list(value)
    raise SimplydataError(
        f"{step}() needs {option} as a column name in quotes, or a list of names.\n"
        f'For example, with sdata.get_example("marks"): table.{step}("marks", for_each_group_in="class")\n'
        f'or table.{step}(["marks", "hours"], for_each_group_in=["class", "subject"])'
    )


GROUPS_IN_SENTENCE = 8  # a sentence lists at most this many groups; the table has them all


def _say_number(value) -> str:
    """A number for a sentence: 61, 61.24, 0.0042 (never more digits than people need)."""
    value = _plain(value)
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "empty"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    if isinstance(value, int):
        return str(value)
    if abs(value) >= 0.01:
        return f"{round(value, 2):g}" if abs(value) < 1e6 else f"{value:.4g}"
    return f"{value:.2g}"


def _missing(value) -> bool:
    """True for None, NaN and NaT (the empty values a table can give back)."""
    if value is None:
        return True
    try:
        return bool(value != value)
    except (TypeError, ValueError):
        return False


def _as_datetime(value):
    if hasattr(value, "to_pydatetime"):  # pandas Timestamp
        return value.to_pydatetime()
    return value


def _say_label(value, every=None) -> str:
    """A group name for a sentence; dates as 2026-03-15, a period as 2026-03 (every="month")."""
    if _missing(value):
        return "(empty)"
    value = _plain(_as_datetime(value))
    if isinstance(value, _dt.date):
        return _say_period(value, every)
    return str(value)


def _say_period(value, every=None) -> str:
    if every == "year":
        return f"{value.year}"
    if every == "quarter":
        return f"{value.year} Q{(value.month - 1) // 3 + 1}"
    if every == "month":
        return f"{value.year}-{value.month:02d}"
    if every == "week":
        return f"week of {value:%Y-%m-%d}"
    if isinstance(value, _dt.datetime) and (every == "hour" or (every is None and (value.hour or value.minute
                                                                                     or value.second))):
        return f"{value:%Y-%m-%d %H:%M}"
    return f"{value:%Y-%m-%d}"


def _week_start(value):
    """The Monday that starts the week of a date (ISO 8601 weeks), at midnight."""
    value = _as_datetime(value)
    if isinstance(value, _dt.datetime):
        value = value.replace(hour=0, minute=0, second=0, microsecond=0)
    return value - _dt.timedelta(days=value.weekday())


def _say_percent(value) -> str:
    """41.7 % (one decimal, a space before the sign, as everywhere in simplydata)."""
    if _missing(value):
        return "empty"
    return f"{float(value):.1f} %"


def _order(value):
    """Sort key for group names: numbers, then everything else, then empty last."""
    if _missing(value):
        return (2, "", 0)
    value = _plain(_as_datetime(value))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (0, "", value)
    return (1, type(value).__name__, value)


def _key(row) -> tuple:
    """A row of group values as a dictionary key: empty values all become None."""
    return tuple(None if _missing(v) else _plain(_as_datetime(v)) for v in row)


def _say_groups(frame, groups: list[str], column: str, periods=None, say=None) -> str:
    """ "A 62.1, B 58.3, C 65" from a small table: one item per row, the groups then a value."""
    periods = periods or {}
    say = say or _say_number
    rows = frame.select(*groups, column).rows()
    items = [" / ".join(_say_label(v, periods.get(g)) for g, v in zip(groups, row[:-1])) + " " + say(row[-1])
             for row in rows[:GROUPS_IN_SENTENCE]]
    text = ", ".join(items)
    if len(rows) > GROUPS_IN_SENTENCE:
        text += f" ... and {len(rows) - GROUPS_IN_SENTENCE} more (the new table has them all)"
    return text


def _names(names) -> str:
    """ "class" or "class" and "subject" """
    quoted = [f'"{n}"' for n in names]
    return quoted[0] if len(quoted) == 1 else ", ".join(quoted[:-1]) + " and " + quoted[-1]


def _each(groups, periods=None) -> str:
    """ "class" and "subject", or month of "date" (for every="month") """
    periods = periods or {}
    return " and ".join(f'{periods[g]} of "{g}"' if g in periods else f'"{g}"' for g in groups)


def _period_note(periods) -> None:
    for every in dict.fromkeys(periods.values()):
        first = {"week": "its Monday", "hour": "the start of the hour"}.get(every, "its first day")
        print(f"Note: in the new table each {every} is shown by {first}.")


def _strength(r: float) -> str:
    r = round(r, 2)  # the words always match the r that is printed
    size = abs(r)
    word = next(w for edge, w in STRENGTH_WORDS if size >= edge)
    if r > 0:
        return f"{word}, going up"
    if r < 0:
        return f"{word}, going down"
    return "no link at all"


def _p_shown(p: float) -> str:
    """"p = 0.031", "p = 0.0026" or "p < 0.0001"."""
    if p is None or math.isnan(p):
        return "p cannot be worked out"
    if p < 0.0001:
        return "p < 0.0001"
    return f"p = {p:.4f}" if p < 0.001 else f"p = {p:.3f}"


def _studies(p: float) -> str:
    """How often a result this big or bigger turns up when there is truly nothing, as a count of
    studies: "about 3 of 100", "about 3 of 1000", "fewer than 1 in 1000", "almost all of 100".
    Display only [D]: the p-value written as a count (rounded), not a statistic."""
    if p is None or math.isnan(p):
        return "an unknown number of"
    if p < 0.001:
        return "fewer than 1 in 1000"
    per_100 = int(p * 100 + 0.5)
    if per_100 == 0:
        return f"about {int(p * 1000 + 0.5)} of 1000"
    if per_100 >= 100:
        return "almost all of 100"
    return f"about {per_100} of 100"


def _p_sentence(p: float, if_none: str = "there were truly no difference",
                this: str = "a difference this big or bigger", not_shown: str | None = "that there is no difference",
                shown: str | None = None, like: str = "studies like this one") -> str:
    """The one p-value sentence of every word (owner decision O7, wording rule W2):

    "If there were truly no difference, a difference this big or bigger would turn up in about 3
    of 100 studies like this one (p = 0.031)."

    if_none: what "nothing there" means for this test ("the groups were truly alike", "B were
    truly not higher", ...); this: what would turn up. From p = 0.05 a second sentence says that a
    large p-value does not show there is nothing ("This does not show that there is no
    difference."; not_shown=None leaves it out). shown: the p-value as printed, when not "p = ..."
    (e.g. "Holm-adjusted p = 0.010"). like: what the p-value counts, "studies like this one"; combine_studies says
    "sets of studies like these", because its rows are studies."""
    if p is None or math.isnan(p):
        return "The p-value cannot be worked out with these numbers (it is NaN), so this test gives no answer."
    shown = shown or _p_shown(p)
    sentence = f"If {if_none}, {this} would turn up in {_studies(p)} {like} ({shown})."
    if p >= 0.05 and not_shown:
        sentence += f" This does not show {not_shown}."
    return sentence


def _p_clause(p: float, if_none: str = "there were truly none", shown: str | None = None) -> str:
    """The short form of the p-value sentence for one line of a list (model terms, pairs):
    "about 3 of 100 studies would show this much if there were truly none (p = 0.031)"."""
    return f"{_studies(p)} studies would show this much if {if_none} ({shown or _p_shown(p)})"


# interval_by= of find_percent_of_rows_where and compare_percent_to: the 95 % interval of a percent (method= is its old name)
# name -> (name in sentences, statsmodels proportion_confint method); each as R DescTools::BinomCI()
PERCENT_METHODS = {
    "exact": ("exact Clopper-Pearson interval", "beta"),
    "wilson": ("Wilson score interval", "wilson"),
    "agresti-coull": ("Agresti-Coull interval", "agresti_coull"),
}
PERCENT_METHOD_ALIASES = {"clopper-pearson": "exact", "clopper pearson": "exact", "beta": "exact",
                          "agresti coull": "agresti-coull", "agresti_coull": "agresti-coull", "score": "wilson"}


def _percent_method(step: str, method):
    """The interval_by= of a percent interval, checked ("exact", "wilson" or "agresti-coull")."""
    from .._errors import choice_error

    name = PERCENT_METHOD_ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) \
        else method
    if name not in PERCENT_METHODS:
        raise choice_error(step, "interval_by", method, list(PERCENT_METHODS))
    return name


def _interval_words(method: str) -> str:
    """"exact 95 % confidence intervals" (the words used before interval_by= existed) or "95 % Wilson score intervals"."""
    return "exact 95 % confidence intervals" if method == "exact" else f"95 % {PERCENT_METHODS[method][0]}s"


def _share(hits: int, rows: int, method: str = "exact"):
    """Percent and its 95 % interval, all from 0 to 100: Clopper-Pearson exact (R binom.test), or
    Wilson / Agresti-Coull (statsmodels proportion_confint, as R DescTools::BinomCI())."""
    if rows == 0:
        return (None, None, None)
    if method == "exact":
        from scipy import stats

        low, high = stats.binomtest(hits, rows).proportion_ci(confidence_level=0.95, method="exact")
    else:
        from statsmodels.stats.proportion import proportion_confint

        low, high = proportion_confint(hits, rows, alpha=0.05, method=PERCENT_METHODS[method][1])
    return (hits * 100.0 / rows, float(low) * 100.0, float(high) * 100.0)


def _ordinal(number: float) -> str:
    """90 -> "90th", 1 -> "1st", 2.5 -> "2.5th"."""
    text = f"{number:g}"
    if not float(number).is_integer():
        return text + "th"
    whole = int(number)
    if 10 <= whole % 100 <= 20:
        return text + "th"
    return text + {1: "st", 2: "nd", 3: "rd"}.get(whole % 10, "th")


BOOTSTRAP_KINDS = {"bootstrap": "bca", "percentile bootstrap": "percentile", "reverse percentile bootstrap": "basic"}
# old values of find_interval_of(method=), still accepted with a note ("basic" read as "simple, the usual one")
OLD_BOOTSTRAP_KINDS = {"basic bootstrap": "reverse percentile bootstrap", "basic": "reverse percentile bootstrap"}


def _one_number(step, name):
    """find_interval_of(summary=): the find_summary_of measure as a function of one group's numbers (NumPy / SciPy)."""
    from scipy import stats

    plain = {"average": np.mean, "median": np.median, "total": np.sum, "smallest": np.min, "biggest": np.max,
             "standard deviation": lambda x: np.std(x, ddof=1), "variance": lambda x: np.var(x, ddof=1),
             "standard error": stats.sem, "range": np.ptp, "interquartile range": stats.iqr}
    if name in plain:
        return plain[name]
    if _is_array_measure(name) and name != "most common":
        return lambda x: _array_measure(name, np.asarray(x, dtype=float))[0]
    raise SimplydataError(f'find_interval_of() needs a summary that gives one number from the values; "{name}" does not. '
                          'Try "average", "median" or "standard deviation".')


MAX_REPEATED_ROWS = 10_000_000  # frequency weights: the most rows a weighted percentile repeats
PERCENTILE_RULES = ("inverted_cdf", "averaged_inverted_cdf", "closest_observation", "interpolated_inverted_cdf",
                    "hazen", "weibull", "linear", "median_unbiased", "normal_unbiased")  # R quantile types 1-9


def _percentile_rule(step, method):
    """find_percentile_of(method=): R's type number (1 to 9) or NumPy's name, as the NumPy name."""
    if isinstance(method, (int, np.integer)) and not isinstance(method, bool) and 1 <= method <= 9:
        return PERCENTILE_RULES[int(method) - 1]
    if isinstance(method, str) and method.strip().lower().replace(" ", "_") in PERCENTILE_RULES:
        return method.strip().lower().replace(" ", "_")
    raise choice_error(step, "method", method, list(PERCENTILE_RULES) + [str(n) for n in range(1, 10)])


def _check_percent(step: str, percent, option="percent", example=None) -> float:
    example = example or f'table.{step}("marks", 90, for_each_group_in="class")   (with sdata.get_example("marks"))'
    if not isinstance(percent, (int, float)) or isinstance(percent, bool) or not math.isfinite(percent):
        raise SimplydataError(f"{step}() needs the {option} as a number from 0 to 100.\nFor example:  {example}")
    if not 0 <= percent <= 100:
        raise SimplydataError(f"The {option} should be from 0 to 100 (it is {percent:g}).\nFor example:  {example}")
    return float(percent)


def _measure_name(step: str, item):
    """The measure a show= item names: "percentile 90" and "90th percentile" both give
    "percentile 90"; "trimmed average" gives "trimmed average 10 %" (R mean(trim = 0.1))."""
    import re

    name = _plain_name(item)
    if not isinstance(name, str):
        raise choice_error(step, "show", item, list(MEASURES))
    example = f'table.{step}("marks", show=["percentile 90", "trimmed average 20"])   (with sdata.get_example("marks"))'
    found = re.fullmatch(r"(?:(\d+(?:\.\d+)?)\s*(?:st|nd|rd|th)?\s*(?:percentile|quantile)"
                         r"|(?:percentile|quantile)\s*(\d+(?:\.\d+)?))", name)
    if found:
        number = float(found.group(1) or found.group(2))
        if number > 100:
            raise SimplydataError(f"A percentile goes from 0 to 100, but show= asks for {number:g}.\n"
                                  f"For example:  {example}")
        return f"percentile {number:g}"
    found = re.fullmatch(r"trimmed (?:average|mean)\s*(\d+(?:\.\d+)?)?\s*%?", name)
    if found:
        number = float(found.group(1)) if found.group(1) else float(TRIM_PERCENT)
        if number >= 50:
            raise SimplydataError(
                f"A trimmed average leaves out a percent from each end, so it must be below 50 (it is {number:g}).\n"
                f"For example:  {example}"
            )
        return f"trimmed average {number:g} %"
    found = re.fullmatch(r"winsori[sz]ed (?:average|mean)\s*(\d+(?:\.\d+)?)?\s*%?", name)
    if found:
        number = float(found.group(1)) if found.group(1) else float(WINSOR_PERCENT)
        if number >= 50:
            raise SimplydataError(
                f"A winsorised average pulls in a percent at each end, so it must be below 50 (it is {number:g}).\n"
                f"For example:  {example}"
            )
        return f"winsorised average {number:g} %"
    name = MEASURE_ALIASES.get(name, name)
    if name == "percentile":
        raise SimplydataError(f'show="percentile" needs the percent, for example "percentile 90".\nFor example:  {example}')
    if name not in MEASURES:
        raise choice_error(step, "show", item, list(MEASURES))
    return name


def _is_array_measure(name) -> bool:
    return isinstance(name, str) and (name in ARRAY_MEASURES or name.startswith(("percentile ", "trimmed average ", "winsorised average ")))


def _array_measure(name: str, values):
    """One group's value of a NumPy / SciPy measure: (value, why it is empty, values as common).

    Definitions (as R, so results can be checked there):
      geometric mean            exp(mean(log(x))); only for numbers above 0
      skewness                  bias-corrected sample skewness G1 (SciPy skew(bias=False),
                                e1071 skewness(type = 2), SAS, SPSS, Excel SKEW)
      kurtosis                  bias-corrected excess kurtosis G2, 0 for a bell shape (SciPy
                                kurtosis(bias=False), e1071 kurtosis(type = 2), Excel KURT)
      coefficient of variation  sd / average, sd with n - 1 (SciPy variation(ddof=1)); a ratio
      median absolute deviation 1.4826 * median(|x - median(x)|), as R mad()
      trimmed average p %       floor(n * p / 100) values cut from each end, as R mean(trim =)
      most common               the value that turns up most often; the smallest when tied
      percentile p              the usual linear rule (R quantile type 7, NumPy default)
      harmonic mean             n / sum(1 / x); only for numbers above 0 (SciPy hmean, as R
                                psych::harmonic.mean)
      winsorised average p %    floor(n * p / 100) values at each end set to the nearest value
                                kept, then the average (SciPy mstats.winsorize, as R
                                WRS2::winmean(tr = p / 100))
    """
    from scipy import stats

    n = len(values)
    if n == 0:
        return None, None, None
    if name == "geometric mean":
        if (values <= 0).any():
            return None, "needs numbers above 0", None
        return float(stats.gmean(values)), None, None
    if name == "harmonic mean":
        if (values <= 0).any():
            return None, "needs numbers above 0", None
        return float(stats.hmean(values)), None, None
    if name.startswith("winsorised average "):
        share = float(name.split()[-2]) / 100
        return float(np.mean(stats.mstats.winsorize(values, limits=(share, share)))), None, None
    if name in LEAST_VALUES and n < LEAST_VALUES[name]:
        return None, f"needs at least {LEAST_VALUES[name]} values", None
    if name in ("skewness", "kurtosis") and np.ptp(values) == 0:
        return None, "has no spread (every value is the same)", None
    if name == "skewness":
        return float(stats.skew(values, bias=False)), None, None
    if name == "kurtosis":
        return float(stats.kurtosis(values, fisher=True, bias=False)), None, None
    if name == "coefficient of variation":
        if n < 2:
            return None, "needs at least 2 values", None
        mean = float(values.mean())
        if mean == 0:
            return None, "is not defined when the average is 0", None
        return float(stats.variation(values, ddof=1)), None, None
    if name == "median absolute deviation":
        return float(stats.median_abs_deviation(values, scale=1 / MAD_CONSTANT)), None, None
    if name == "most common":
        found, counts = np.unique(values, return_counts=True)  # all tied values, for the note
        return float(stats.mode(values, keepdims=False).mode), None, found[counts == counts.max()]
    number = float(name.split()[-2] if name.endswith("%") else name.split()[-1])
    if name.startswith("percentile"):
        return float(np.percentile(values, number)), None, None
    return float(stats.trim_mean(values, number / 100)), None, None


def _measure_values(names, raw: dict) -> dict:
    """The find_summary_of measures of one group, from its raw pieces (count, mean, sd ...)."""
    n = int(raw["n"] or 0)

    def number(value):
        return None if _missing(value) else float(value)

    sd = number(raw["sd"]) if n >= 2 else None
    out = {}
    for name in names:
        if name == "count":
            out[name] = n
        elif name == "empty cells":
            out[name] = int(raw["empty"] or 0)
        elif n == 0:
            out[name] = None if name not in ("total",) else 0.0
            if name == "confidence interval":
                out["average 95 % CI low"] = out["average 95 % CI high"] = None
        elif name == "average":
            out[name] = number(raw["mean"])
        elif name == "median":
            out[name] = number(raw["median"])
        elif name == "total":
            out[name] = number(raw["sum"])
        elif name == "smallest":
            out[name] = number(raw["min"])
        elif name == "biggest":
            out[name] = number(raw["max"])
        elif name == "standard deviation":
            out[name] = sd
        elif name == "variance":
            out[name] = number(raw["var"]) if n >= 2 else None
        elif name == "standard error":
            out[name] = sd / math.sqrt(n) if sd is not None else None
        elif name == "confidence interval":
            if sd is None:
                out["average 95 % CI low"] = out["average 95 % CI high"] = None
            else:
                from scipy import stats

                half = float(stats.t.ppf(0.975, n - 1)) * sd / math.sqrt(n)
                mean = float(raw["mean"])
                out["average 95 % CI low"], out["average 95 % CI high"] = mean - half, mean + half
        elif name == "range":
            out[name] = number(raw["max"]) - number(raw["min"])
        elif name == "interquartile range":
            out[name] = number(raw["q3"]) - number(raw["q1"])
    return out


class SummaryWords:
    # ------------------------------------------------------------------ helpers
    def _number_frame(self, step: str, columns: list[str]):
        """Check the columns hold numbers; give back the table with NaN made empty."""
        self._need_columns(*columns)
        schema = self._frame.schema
        for name in columns:
            dtype = schema[name]
            if dtype.is_numeric():
                continue
            if dtype == nw.String or dtype == nw.Categorical or dtype == nw.Enum:
                what = "text"
            elif dtype == nw.Boolean:
                what = "True/False values"
            elif dtype.is_temporal():
                what = "dates or times"
            else:
                what = "no numbers"
            numbers = [c for c, d in schema.items() if d.is_numeric()]
            hint = f"Columns with numbers: {', '.join(numbers)}" if numbers else "This table has no columns of numbers."
            raise SimplydataError(
                f'{step} needs a column of numbers; "{name}" has {what}.\n'
                f"{hint}\n"
                f'For example, with sdata.get_example("marks"): table.{step}("marks")'
            )
        floats = [c for c in columns if schema[c].is_float()]
        if floats:
            return self._frame.with_columns(nw.col(c).fill_nan(None) for c in floats)
        return self._frame

    def _group_columns(self, step: str, for_each, columns=()) -> list[str]:
        groups = _as_list(step, "for_each_group_in=", for_each)
        self._need_columns(*groups)
        for name in groups:
            if name in columns:
                raise SimplydataError(
                    f'"{name}" cannot be both the column to summarise and the for_each_group_in= column.\n'
                    f'For example, with sdata.get_example("marks"): table.{step}("marks", for_each_group_in="class")'
                )
        return groups

    @staticmethod
    def _note_empty(frame, columns: list[str]):
        counts = frame.select(nw.col(c).null_count().alias(c) for c in columns).row(0)
        skipped = [(c, int(n)) for c, n in zip(columns, counts) if n]
        if not skipped:
            return
        if len(skipped) == 1:
            name, n = skipped[0]
            cells = "empty cell" if n == 1 else "empty cells"
            verb = "was" if n == 1 else "were"
            print(f'Note: {n} {cells} in "{name}" {verb} skipped.')
        else:
            parts = ", ".join(f'{n} in "{c}"' for c, n in skipped)
            print(f"Note: empty cells were skipped: {parts}.")

    def _grouped(self, frame, groups: list[str], exprs):
        result = frame.group_by(groups, drop_null_keys=False).agg(*exprs).sort(groups, nulls_last=True)
        return self._new_table(nw.maybe_reset_index(result))

    def _periods(self, step: str, frame, groups, every):
        """every="month": the date columns in for_each_group_in= become the first day of their month.

        Gives back (frame, {date column: "month"}). Without every= nothing changes."""
        if every is None:
            return frame, {}
        name = _plain_name(every)
        if name not in EVERY:
            raise choice_error(step, "every", every, list(EVERY))
        if not groups:
            raise SimplydataError(
                f"every= needs the column of dates in for_each_group_in=, to say which dates to group.\n"
                f"For example:  {EVERY_EXAMPLE}"
            )
        schema = frame.schema
        dates = [g for g in groups if schema[g] == nw.Date or schema[g] == nw.Datetime]
        if not dates:
            kinds = ", ".join(f'"{g}"' for g in groups)
            text = [g for g in groups if schema[g] == nw.String]
            hint = (f'If {_names(text)} holds dates written as text, make them dates first: '
                    f'table.turn_into_dates("{text[0]}").\n' if text else "")
            raise SimplydataError(
                f"every= groups dates into periods, but none of the for_each_group_in= columns ({kinds}) holds dates.\n"
                f"{hint}For example:  {EVERY_EXAMPLE}"
            )
        frame = nw.maybe_reset_index(frame)
        for g in dates:
            if name == "week":
                values = [None if _missing(v) else _week_start(v) for v in frame[g].to_list()]
                frame = frame.with_columns(
                    nw.new_series(g, values, schema[g], backend=frame.implementation))
            elif schema[g] == nw.Date and name == "hour":
                continue  # a date has no hours: each day stays as it is
            else:
                frame = frame.with_columns(nw.col(g).dt.truncate(EVERY[name]))
        return frame, {g: name for g in dates}

    def _cross(self, frame, groups: list[str], across: str, expr, fill=None, periods=None):
        """A cross table: one row per group, one column per value of across=, expr in each cell."""
        long = frame.group_by([*groups, across], drop_null_keys=False).agg(expr.alias("__value"))
        rows = long.select(*groups, across, "__value").rows()
        row_keys = sorted({_key(r[:-2]) for r in rows}, key=lambda k: tuple(_order(v) for v in k))
        col_keys = sorted({_key(r[-2:-1])[0] for r in rows}, key=_order)
        cells = {(_key(r[:-2]), _key(r[-2:-1])[0]): _plain(r[-1]) for r in rows}
        data = {g: [k[i] for k in row_keys] for i, g in enumerate(groups)}
        for c in col_keys:
            label = _say_label(c, (periods or {}).get(across))
            if label in data:
                label = f"{across} {label}"
            data[label] = [cells.get((k, c), fill) for k in row_keys]
        result = nw.from_dict(data, backend=frame.implementation)
        return self._new_table(result), [str(c) for c in data if c not in groups]

    @staticmethod
    def _say_cross(table, groups, columns, say=None, periods=None):
        say = say or _say_number
        rows = table._frame.select(*groups, *columns).rows()
        for row in rows[:GROUPS_IN_SENTENCE]:
            name = " / ".join(_say_label(v, (periods or {}).get(g)) for g, v in zip(groups, row))
            cells = ", ".join(f"{c} {say(v)}" for c, v in zip(columns, row[len(groups):]))
            print(f"  {name}: {cells}")
        if len(rows) > GROUPS_IN_SENTENCE:
            print(f"  ... and {len(rows) - GROUPS_IN_SENTENCE} more rows (the new table has them all)")

    def _check_across(self, step: str, across, groups, columns=()):
        example = f'table.{step}("marks", for_each_group_in="class", across="subject")   (with sdata.get_example("marks"))'
        if step == "count_rows":
            example = 'table.count_rows(for_each_group_in="class", across="subject")   (with sdata.get_example("marks"))'
        if not isinstance(across, str):
            raise SimplydataError(f"{step}() needs across= as one column name in quotes.\nFor example:  {example}")
        if groups is None:
            raise SimplydataError(
                f"across= makes a cross table: for_each_group_in= gives its rows and across= its columns.\n"
                f"For example:  {example}"
            )
        self._need_columns(across)
        if across in groups or across in columns:
            raise SimplydataError(
                f'"{across}" cannot be both the across= column and a for_each_group_in= column or the column to summarise.\n'
                f"For example:  {example}"
            )

    def _summary(self, step: str, column, for_each, every=None, across=None, measure=None):
        """measure=(start of the column name, calculation, words for sentences) for words not in _SUMMARIES."""
        start, make = _SUMMARIES[step] if measure is None else measure[:2]
        said = start if measure is None else measure[2]
        columns = _as_list(step, "the column", column)
        groups = self._group_columns(step, for_each, columns) if for_each is not None else None
        if across is not None:
            self._check_across(step, across, groups, columns)
            if len(columns) > 1:
                raise SimplydataError(
                    f"across= makes a cross table of one column. Give one column, or use find_summary_of() for several.\n"
                    f'For example:  table.{step}("marks", for_each_group_in="class", across="subject")'
                    '   (with sdata.get_example("marks"))'
                )
        frame = self._number_frame(step, columns)
        frame, periods = self._periods(step, frame, groups, every)
        exprs = [make(c).alias(f"{start} of {c}") for c in columns]
        if across is not None:
            result, labels = self._cross(frame, groups, across, make(columns[0]), periods=periods)
            self._note_empty(frame, columns)
            print(f'The {said} of "{columns[0]}" for each {_each(groups, periods)} (rows) and each "{across}" '
                  f"(columns): a new table with {len(result)} rows and {len(labels)} columns of numbers.")
            self._say_cross(result, groups, labels, periods=periods)
            _period_note(periods)
            return result
        if groups is None:
            result = frame.select(*exprs)
            self._note_empty(frame, columns)
            counts = frame.select(nw.col(c).count().alias(c) for c in columns).row(0)
            sentence = "; ".join(f'the {said} of "{c}" is {_say_number(v)} ({n} values)'
                                 for c, v, n in zip(columns, result.row(0), counts))
            print(sentence[0].upper() + sentence[1:] + ".")
            if isinstance(column, str):
                return _plain(result.item())
            return self._new_table(result)
        result = self._grouped(frame, groups, exprs)
        self._note_empty(frame, columns)
        each = _each(groups, periods)
        if len(columns) == 1:
            values = _say_groups(result._frame, groups, f"{start} of {columns[0]}", periods)
            print(f'The {said} of "{columns[0]}" for each {each}: {values}.')
        else:
            print(f"The {said} of {_names(columns)} for each {each}: a new table with {len(result)} rows.")
        _period_note(periods)
        return result

    def _weighted(self, step, column, weights, for_each, every, across, interval, kind="frequency"):
        """find_average_of / find_standard_deviation_of with weights=: statsmodels DescrStatsW (frequency weights) or
        NumPy cov(aweights=) (analytic weights), as R weighted.mean() and Hmisc::wtd.var()."""
        import numpy as np
        from statsmodels.stats.weightstats import DescrStatsW

        example = f'table.{step}("marks", for_each_group_in="class", weights="people")'
        if interval is not None:
            raise SimplydataError("weights= and interval= do not go together here yet; leave out one of them.")
        if every is not None or across is not None or not isinstance(column, str):
            raise SimplydataError(f"weights= works with one column and for_each_group_in=; leave out every= and across=.\n"
                                  f"For example:  {example}")
        if not isinstance(weights, str):
            raise SimplydataError(f"weights= is the name of a column of weights, in quotes.\nFor example:  {example}")
        if weights == column:
            raise SimplydataError(f'weights= needs a column other than "{column}".')
        if step == "find_standard_deviation_of":
            self._check_choice(step, "weight_kind", kind, ("frequency", "analytic"))
        groups = self._group_columns(step, for_each, [column, weights]) if for_each is not None else []
        frame = self._number_frame(step, [column, weights])
        both = frame.filter(~nw.col(column).is_null() & ~nw.col(weights).is_null())
        left_out = len(frame) - len(both)
        if left_out:
            print(f'Note: {left_out} row{"" if left_out == 1 else "s"} with an empty cell in "{column}" or '
                  f'"{weights}" {"was" if left_out == 1 else "were"} skipped.')
        values = self._group_arrays(both, groups, column)
        weight_values = self._group_arrays(both, groups, weights)
        found = {}
        for key, x in values.items():
            w = weight_values[key]
            if np.any(w < 0):
                raise SimplydataError(f'weights= cannot be below 0, but "{weights}" has {int(np.sum(w < 0))} '
                                      "negative values.")
            if len(x) == 0 or w.sum() == 0:
                found[key] = math.nan
            elif step == "find_average_of":
                found[key] = float(DescrStatsW(x, weights=w).mean)
            elif kind == "frequency":
                found[key] = float(DescrStatsW(x, weights=w, ddof=1).std) if w.sum() > 1 else math.nan
            else:
                found[key] = float(np.sqrt(np.cov(x, aweights=w, ddof=1))) if np.sum(w > 0) > 1 else math.nan
        if step == "find_average_of":
            said, how = "weighted average", "statsmodels DescrStatsW, as R weighted.mean(x, w)"
        elif kind == "frequency":
            said = "weighted standard deviation"
            how = ("frequency weights: each row counts as often as its weight; statsmodels DescrStatsW(ddof=1), as "
                   "R sqrt(Hmisc::wtd.var(x, w))")
        else:
            said = "weighted standard deviation"
            how = ("analytic weights: how precise each row is; NumPy cov(aweights=), as R sqrt(Hmisc::wtd.var(x, "
                   "w, normwt = TRUE))")
        name = f"{said} of {column}"
        if not groups:
            value = found.get((), math.nan)
            print(f'The {said.replace("weighted ", "")} of "{column}", weighted by "{weights}", is {_say_number(value)} ({how}).')
            return value
        data = {g: [key[i] for key in found] for i, g in enumerate(groups)}
        data[name] = list(found.values())
        table = self._new_table(nw.from_dict(data, backend=self._frame.implementation))
        shown = _say_groups(table._frame, groups, name)
        print(f'The {said.replace("weighted ", "")} of "{column}", weighted by "{weights}", for each {_each(groups)}: {shown} ({how}).')
        return table

    def _summary_interval(self, step, column, for_each, every, across, interval, share=None):
        """find_average_of / find_median_of / find_percentile_of / find_standard_deviation_of with interval=: one row per group with
        the value, its interval and the count. Each interval comes from a package (SciPy, or R DescTools)."""
        from scipy import stats

        level = _check_percent(step, interval, "interval", f'table.{step}("marks", for_each_group_in="class", interval=95)')
        if not 50 <= level < 100:
            raise SimplydataError(f"interval= is the level of the interval in percent, such as interval=95 or 90 "
                                  f"(it is {level:g}).")
        if every is not None or across is not None or not isinstance(column, str):
            raise SimplydataError(f"interval= works with one column and for_each_group_in=; leave out every= and across=.")
        groups = self._group_columns(step, for_each, [column]) if for_each is not None else []
        frame = self._number_frame(step, [column])
        self._note_empty(frame, [column])
        arrays = self._group_arrays(frame, groups, column)
        kind = {"find_average_of": "average", "find_median_of": "median", "find_standard_deviation_of": "standard deviation",
                "find_percentile_of": f"percentile {share * 100:g}" if share is not None else None}[step]
        start = kind
        how = {"average": "t interval, as R t.test()",
               "standard deviation": "chi-square interval, from R DescTools::VarCI() (the interval of the variance, "
                                     "square-rooted)"}.get(kind, "exact interval from the order of the values (SciPy "
                                                                 "quantile_test"
                                                                 + (', as R DescTools::MedianCI(method = "exact"))'
                                                                    if kind == "median" else ")"))
        rows = []
        for key, x in arrays.items():
            n = len(x)
            if kind == "average":
                value = float(x.mean()) if n else math.nan
                low, high = (stats.ttest_1samp(x, 0).confidence_interval(level / 100) if n >= 2
                             else (math.nan, math.nan))
            elif kind == "standard deviation":
                value = float(x.std(ddof=1)) if n >= 2 else math.nan
                low = high = math.nan
                if n >= 2:
                    from .._r import r_call

                    found = r_call("unname(DescTools::VarCI(x, method = 'classic', conf.level = level)[2:3])",
                                   packages=("DescTools",), what="the interval of a standard deviation (R "
                                   "DescTools::VarCI())", python_note="Python has no function for it",
                                   x=x, level=level / 100)
                    low, high = (math.sqrt(float(v)) for v in np.asarray(found))  # display: variance -> sd
            else:
                p = 0.5 if kind == "median" else share
                value = float(np.percentile(x, p * 100)) if n else math.nan
                low = high = math.nan
                if n:
                    found = stats.quantile_test(x, q=value, p=p).confidence_interval(level / 100)
                    low, high = found.low, found.high
            rows.append(list(key) + [value, float(low), float(high), n])
        names = [f"{start} of {column}", f"{start} of {column} {level:g} % CI low",
                 f"{start} of {column} {level:g} % CI high", "count"]
        data = {name: [r[i] for r in rows] for i, name in enumerate(list(groups) + names)}
        table = self._new_table(nw.from_dict(data, backend=self._frame.implementation))
        parts = []
        for r in rows[:GROUPS_IN_SENTENCE]:
            label = " / ".join(_say_label(v) for v in r[:len(groups)])
            low, high = r[-3], r[-2]
            if not (math.isnan(low) or math.isnan(high)):
                ends = f"{_say_number(low)} to {_say_number(high)}"
            elif math.isnan(low) and math.isnan(high):
                ends = "too few values for an interval"
            elif math.isnan(high):
                ends = f"at least {_say_number(low)}; too few values for an upper end"
            else:
                ends = f"at most {_say_number(high)}; too few values for a lower end"
            parts.append((f"{label}: " if groups else "") + f"{_say_number(r[-4])} ({ends})")
        where = f' for each {_each(groups)}' if groups else ""
        said = kind if share is None else f"{_ordinal(share * 100)} percentile"
        print(f'The {said} of "{column}"{where}, with the values that fit the data ({level:g} % confidence '
              f"interval): {'; '.join(parts)}{' ...' if len(rows) > GROUPS_IN_SENTENCE else ''}.")
        print(f"Interval: {how}.")
        if any(math.isnan(r[-3]) or math.isnan(r[-2]) for r in rows):
            print("Note: an end of the interval is empty where there are too few values to reach that level.")
        return table

    @friendly(renamed={"for_each": "for_each_group_in", "seed": "with_seed"})
    def find_interval_of(self, column=None, summary="average", for_each_group_in=None, interval=95, method="bootstrap",
                         resamples=9999, with_seed=1):
        """A confidence interval for any summary, from the bootstrap.

        table.find_interval_of("marks", "median", for_each_group_in="class")   (with sdata.get_example("marks"))
        summary= is any one-number measure of find_summary_of() ("average", "median", "standard
        deviation", "trimmed average 20", "percentile 90", "coefficient of variation", ...) or a
        function of your own that gets the numbers (a NumPy array) and gives back one number.
        The bootstrap draws the rows again at random, with replacement, resamples=9999 times
        (with_seed=1, printed; the same seed gives the same interval) and works out the summary each
        time; SciPy stats.bootstrap, as R boot::boot.ci(). method="bootstrap" is the
        bias-corrected and accelerated (BCa) interval, the usual choice; "percentile bootstrap"
        and "reverse percentile bootstrap" (R's "basic") are the other two. With fewer than 20
        values a note says the interval is often too narrow. Gives back one row per group: the
        summary, the interval and the count.
        """
        from .resampling import bootstrap_interval

        step = "find_interval_of"
        example = 'table.find_interval_of("marks", "median", for_each_group_in="class")   (with sdata.get_example("marks"))'
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs one column name in quotes, then the summary.\nFor example:  {example}")
        level = _check_percent(step, interval, "interval", example)
        if not 50 <= level < 100:
            raise SimplydataError(f"interval= is the level in percent, such as interval=95 (it is {level:g}).")
        if method == "jackknife":
            raise SimplydataError("A jackknife interval is not offered: no established package gives one (R "
                                  "bootstrap::jackknife() gives only the standard error and the bias). Use "
                                  'method="bootstrap".')
        if method in OLD_BOOTSTRAP_KINDS:
            from .._errors import renamed_note

            renamed_note(f'method="{method}"', f'method="{OLD_BOOTSTRAP_KINDS[method]}"')
            method = OLD_BOOTSTRAP_KINDS[method]
        self._check_choice(step, "method", method, tuple(BOOTSTRAP_KINDS))
        if callable(summary):
            label, function = getattr(summary, "__name__", "your summary"), summary
        else:
            label = _measure_name(step, summary)
            function = _one_number(step, label)
        groups = self._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else []
        frame = self._number_frame(step, [column])
        self._note_empty(frame, [column])
        rows, notes, words = [], set(), ""
        for key, x in self._group_arrays(frame, groups, column).items():
            if len(x) < 2:
                raise SimplydataError(f"{step}() needs at least 2 numbers in each group.")
            value = float(function(x))
            low, high, words, note = bootstrap_interval((x,), lambda v: float(function(v)), level,
                                                        BOOTSTRAP_KINDS[method], resamples, with_seed, vectorized=False)
            notes.add(note)
            if math.isnan(low) or math.isnan(high):
                notes.add(f'Note: the {method} interval could not be worked out for '
                          f'{" / ".join(_say_label(v) for v in key) or "the column"} (SciPy says the resampled '
                          'summaries take too few different values); try method="percentile bootstrap".')
            rows.append(list(key) + [value, low, high, len(x)])
        names = [f"{label} of {column}", f"{label} of {column} {level:g} % CI low",
                 f"{label} of {column} {level:g} % CI high", "count"]
        data = {name: [r[i] for r in rows] for i, name in enumerate(list(groups) + names)}
        parts = [(" / ".join(_say_label(v) for v in r[:len(groups)]) + ": " if groups else "")
                 + f"{_say_number(r[-4])} ({_say_number(r[-3])} to {_say_number(r[-2])})".replace("(empty to empty)", "(no interval)")
                 for r in rows[:GROUPS_IN_SENTENCE]]
        where = f" for each {_each(groups)}" if groups else ""
        print(f'The {label} of "{column}"{where}, with the values that fit the data ({level:g} % bootstrap '
              f"interval): {'; '.join(parts)}{' ...' if len(rows) > GROUPS_IN_SENTENCE else ''}.")
        print(f"Interval: {words}; SciPy stats.bootstrap.")
        for note in sorted(notes - {""}):
            print(note)
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ number words
    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_average_of(self, column, for_each_group_in=None, every=None, across=None, interval=None, weights=None):
        """The average (mean) of a column; empty cells are skipped.

        table.find_average_of("marks", for_each_group_in="class")   (with sdata.get_example("marks"))
        across= gives a cross table, one column per subject:
        table.find_average_of("marks", for_each_group_in="class", across="subject")
        every= groups a date column in for_each_group_in= into "hour", "day", "week", "month",
        "quarter" or "year" periods:
        table.turn_into_dates("year")
        table.find_average_of("population", for_each_group_in="year", every="year")   (with sdata.get_example("growth"))
        interval=95 adds the 95 % confidence interval of each average (the t interval, as R
        t.test()) and gives back a table with the average, the interval and the count.
        weights="people" gives the weighted average: each row counts as much as its number in the
        column of weights (statsmodels DescrStatsW, as R weighted.mean()).
        """
        from .places import direction_note

        direction_note(column)
        if weights is not None:
            return self._weighted("find_average_of", column, weights, for_each_group_in, every, across, interval)
        if interval is not None:
            return self._summary_interval("find_average_of", column, for_each_group_in, every, across, interval)
        return self._summary("find_average_of", column, for_each_group_in, every, across)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_median_of(self, column, for_each_group_in=None, every=None, across=None, interval=None, weights=None,
                       weight_kind="frequency"):
        """The middle number of a column once it is sorted; empty cells are skipped.

        table.find_median_of("marks", for_each_group_in="class")   (with sdata.get_example("marks"))
        across= and every= work as in find_average_of.
        interval=95 adds the 95 % confidence interval of each median: the exact interval from
        the order of the values (SciPy quantile_test, as R DescTools::MedianCI(method =
        "exact")); it gives back a table with the median, the interval and the count.
        weights="n" gives the weighted median, with weight_kind= as in find_percentile_of:
        "frequency" (the default; each row counts as often as its whole-number weight) or
        "analytic".
        """
        if weights is not None:
            return self._weighted_percentile("find_median_of", column, 50.0, weights, weight_kind, for_each_group_in,
                                             every, across, interval, "linear", said="median")
        if weight_kind != "frequency":
            raise SimplydataError("weight_kind= says how to read weights=, so it goes with weights=.\n"
                                  'For example:  table.find_median_of("length", weights="n", weight_kind="analytic")')
        if interval is not None:
            return self._summary_interval("find_median_of", column, for_each_group_in, every, across, interval)
        return self._summary("find_median_of", column, for_each_group_in, every, across)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_total_of(self, column, for_each_group_in=None, every=None, across=None):
        """All the numbers in a column added up; empty cells are skipped.

        table.find_total_of("count", for_each_group_in="shop")   (with sdata.get_example("fruit"))
        table.find_total_of("count", for_each_group_in="shop", across="fruit")   a cross table
        every="month" with a date column in for_each_group_in= gives the total of each month.
        """
        return self._summary("find_total_of", column, for_each_group_in, every, across)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_smallest_of(self, column, for_each_group_in=None, every=None, across=None):
        """The smallest number in a column; empty cells are skipped.

        table.find_smallest_of("temperature", for_each_group_in="city")   (with sdata.get_example("weather"))
        across= and every= work as in find_average_of.
        """
        return self._summary("find_smallest_of", column, for_each_group_in, every, across)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_biggest_of(self, column, for_each_group_in=None, every=None, across=None):
        """The biggest number in a column; empty cells are skipped.

        table.find_biggest_of("temperature", for_each_group_in="city")   (with sdata.get_example("weather"))
        across= and every= work as in find_average_of.
        """
        return self._summary("find_biggest_of", column, for_each_group_in, every, across)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_standard_deviation_of(self, column, for_each_group_in=None, every=None, across=None, interval=None, weights=None,
                                   weight_kind="frequency"):
        """How spread out the numbers are: the sample standard deviation (divide by n - 1).

        It is the same as pandas .std() and R sd(). Empty cells are skipped.
        table.find_standard_deviation_of("marks", for_each_group_in="class")   (with sdata.get_example("marks"))
        across= and every= work as in find_average_of.
        interval=95 adds the 95 % confidence interval of each standard deviation (the chi-square
        interval of the variance from R DescTools::VarCI(), square-rooted; needs simplydata[r],
        as Python has no function for it). It assumes bell-shaped values.
        weights="people" gives the weighted standard deviation. weight_kind="frequency" (the
        default) reads each weight as how many times the row counts (statsmodels DescrStatsW,
        divide by the total weight minus 1, as R sqrt(Hmisc::wtd.var(x, w))); "analytic" reads
        it as how precise the row is, such as the number of values behind an average (NumPy
        cov(aweights=), as R sqrt(Hmisc::wtd.var(x, w, normwt = TRUE))).
        """
        if weights is not None:
            return self._weighted("find_standard_deviation_of", column, weights, for_each_group_in, every, across, interval,
                                  weight_kind)
        if weight_kind != "frequency":
            raise SimplydataError("weight_kind= says how to read weights=, so it goes with weights=.\n"
                                  'For example:  table.find_standard_deviation_of("marks", weights="people", '
                                  'weight_kind="analytic")')
        if interval is not None:
            return self._summary_interval("find_standard_deviation_of", column, for_each_group_in, every, across, interval)
        return self._summary("find_standard_deviation_of", column, for_each_group_in, every, across)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_percentile_of(self, column=None, percent=None, for_each_group_in=None, every=None, across=None, method=None,
                           interval=None, weights=None, weight_kind="frequency"):
        """The value below which a given percent of the numbers lie; empty cells are skipped.

        table.find_percentile_of("marks", 90, for_each_group_in="class")   (with sdata.get_example("marks"))
        find_percentile_of("marks", 50) is the median, 25 and 75 the quartiles. Between two
        numbers it uses the usual linear rule (R quantile(type = 7), NumPy and pandas
        default). across= and every= work as in find_average_of.
        method= picks one of R's nine rules, by R's number or NumPy's name: 1 "inverted_cdf",
        2 "averaged_inverted_cdf", 3 "closest_observation", 4 "interpolated_inverted_cdf",
        5 "hazen", 6 "weibull" (as SPSS and Minitab), 7 "linear" (the default), 8
        "median_unbiased" (recommended by Hyndman and Fan), 9 "normal_unbiased"; NumPy
        percentile(method=), as R quantile(type =).
        interval=95 adds the 95 % confidence interval of each percentile: the exact interval
        from the order of the values (SciPy quantile_test; for the median and the quartiles the
        same as R DescTools::QuantileCI(method = "exact"), which picks other values for other
        percents); with few values an end can be empty.
        weights="n" gives the weighted percentile. weight_kind="frequency" (the default) reads
        each weight as how many times the row counts, so it needs whole numbers: the rows are
        repeated and the usual method= is used (as R quantile(rep(x, w)) and Hmisc::wtd.quantile(x,
        w)); weights of 1 change nothing. weight_kind="analytic" reads any weight of 0 or more,
        such as a sampling weight: NumPy percentile(weights=, method="inverted_cdf"), the only
        weighted rule NumPy has (as R survey::svyquantile(qrule = "math")); it is a step, not a
        line between values, so with all weights 1 it is not the unweighted default.
        """
        step = "find_percentile_of"
        if column is None:
            raise SimplydataError(f"{step}() needs the column first, then the percent.\n"
                                  f'For example:  table.{step}("marks", 90, for_each_group_in="class")   (with sdata.get_example("marks"))')
        number = _check_percent(step, percent)
        share = number / 100
        rule = _percentile_rule(step, "linear" if method is None else method)
        if weights is not None:
            return self._weighted_percentile(step, column, number, weights, weight_kind, for_each_group_in, every,
                                             across, interval, rule, method_given=method is not None)
        if weight_kind != "frequency":
            raise SimplydataError("weight_kind= says how to read weights=, so it goes with weights=.\n"
                                  f'For example:  table.{step}("length", 90, weights="n", weight_kind="analytic")')
        if interval is not None:
            if rule != "linear":
                raise SimplydataError("interval= gives the interval of the percentile itself, the same for every "
                                      "method=; leave out method=.")
            return self._summary_interval(step, column, for_each_group_in, every, across, interval, share=share)
        if rule == "linear":
            measure = (f"percentile {number:g}", lambda c: nw.col(c).quantile(share, interpolation="linear"),
                       f"{_ordinal(number)} percentile")
            return self._summary(step, column, for_each_group_in, every, across, measure=measure)
        return self._percentile_by_rule(step, column, number, for_each_group_in, every, across, rule)

    def _weighted_percentile(self, step, column, number, weights, kind, for_each, every, across, interval, rule,
                             method_given=False, said=None):
        """find_percentile_of / find_median_of with weights=. Frequency weights: the rows repeated (NumPy repeat), then
        NumPy percentile(method=) as without weights, as R quantile(rep(x, w)). Analytic weights: NumPy
        percentile(weights=, method="inverted_cdf"), as R survey::svyquantile(qrule = "math")."""
        example = ('table.find_median_of("length", weights="n")' if step == "find_median_of"
                   else f'table.{step}("length", {number:g}, weights="n")')
        self._check_choice(step, "weight_kind", kind, ("frequency", "analytic"))
        if interval is not None:
            raise SimplydataError("weights= and interval= do not go together here yet; leave out one of them.")
        if every is not None or across is not None or not isinstance(column, str):
            raise SimplydataError(f"weights= works with one column and for_each_group_in=; leave out every= and across=.\n"
                                  f"For example:  {example}")
        if not isinstance(weights, str):
            raise SimplydataError(f"weights= is the name of a column of weights, in quotes.\nFor example:  {example}")
        if weights == column:
            raise SimplydataError(f'weights= needs a column other than "{column}".')
        if kind == "analytic" and method_given and rule != "inverted_cdf":
            raise SimplydataError(
                'With weight_kind="analytic" the rule is the weighted inverted CDF (NumPy percentile(weights=, '
                'method="inverted_cdf")), the only rule NumPy has with weights, so method= cannot be changed. Leave '
                'out method=, or use weight_kind="frequency" (whole-number weights) to keep method=.')
        groups = self._group_columns(step, for_each, [column, weights]) if for_each is not None else []
        frame = self._number_frame(step, [column, weights])
        both = frame.filter(~nw.col(column).is_null() & ~nw.col(weights).is_null())
        left_out = len(frame) - len(both)
        if left_out:
            print(f'Note: {left_out} row{"" if left_out == 1 else "s"} with an empty cell in "{column}" or '
                  f'"{weights}" {"was" if left_out == 1 else "were"} skipped.')
        values = self._group_arrays(both, groups, column)
        weight_values = self._group_arrays(both, groups, weights)
        all_weights = np.concatenate([np.asarray(v, dtype=float) for v in weight_values.values()] or [np.array([])])
        if np.any(all_weights < 0):
            raise SimplydataError(f'weights= cannot be below 0, but "{weights}" has {int(np.sum(all_weights < 0))} '
                                  "negative values.")
        if not np.all(np.isfinite(all_weights)):
            raise SimplydataError(f'weights= needs ordinary numbers, but "{weights}" has '
                                  f"{int(np.sum(~np.isfinite(all_weights)))} infinite values. Fix or remove those rows "
                                  "first.")
        if kind == "frequency":
            odd = all_weights[all_weights != np.round(all_weights)]
            if len(odd):
                raise SimplydataError(
                    "Frequency weights say how many times each row counts, so they must be whole numbers, but "
                    f'"{weights}" has {_say_number(float(odd[0]))}. For weights such as sampling weights or '
                    f'precisions use weight_kind="analytic".\nFor example:  {example[:-1]}, weight_kind="analytic")')
            if all_weights.sum() > MAX_REPEATED_ROWS:
                raise SimplydataError(
                    f'The frequency weights in "{weights}" add up to {int(all_weights.sum()):,} rows, more than '
                    f"simplydata repeats ({MAX_REPEATED_ROWS:,}). Use weight_kind=\"analytic\" (the weighted "
                    "inverted CDF), which repeats nothing.")
        elif np.lib.NumpyVersion(np.__version__) < "2.0.0":
            raise SimplydataError('weight_kind="analytic" needs NumPy 2.0 or newer (percentile(weights=)): '
                                  "pip install -U numpy")
        found = {}
        for key, x in values.items():
            w = np.asarray(weight_values[key], dtype=float)
            if len(x) == 0 or not np.any(w > 0):
                found[key] = math.nan
            elif kind == "frequency":
                found[key] = float(np.percentile(np.repeat(x, w.astype(np.int64)), number, method=rule))
            else:
                found[key] = float(np.percentile(x, number, weights=w, method="inverted_cdf"))
        said = said or f"{_ordinal(number)} percentile"
        start = "median" if said == "median" else f"percentile {number:g}"
        if kind == "frequency":
            r_type = PERCENTILE_RULES.index(rule) + 1
            how = (f'frequency weights: each row counts as often as its weight; NumPy percentile(method="{rule}") of '
                   f"the rows repeated, as R quantile(rep(x, w), type = {r_type})"
                   + (" and Hmisc::wtd.quantile(x, w)" if rule == "linear" else ""))
        else:
            how = ('analytic weights: NumPy percentile(weights=, method="inverted_cdf"), the weighted inverted CDF, as '
                   'R survey::svyquantile(qrule = "math")')
        name = f"weighted {start} of {column}"
        if not groups:
            value = found.get((), math.nan)
            print(f'The {said} of "{column}", weighted by "{weights}", is {_say_number(value)} ({how}).')
            return value
        data = {g: [key[i] for key in found] for i, g in enumerate(groups)}
        data[name] = list(found.values())
        table = self._new_table(nw.from_dict(data, backend=self._frame.implementation))
        shown = _say_groups(table._frame, groups, name)
        print(f'The {said} of "{column}", weighted by "{weights}", for each {_each(groups)}: {shown} ({how}).')
        return table

    def _percentile_by_rule(self, step, column, number, for_each, every, across, rule):
        """find_percentile_of(method=) other than the linear rule: NumPy percentile(method=), as R quantile(type =)."""
        if every is not None or across is not None or not isinstance(column, str):
            raise SimplydataError("method= works with one column and for_each_group_in=; leave out every= and across=.")
        groups = self._group_columns(step, for_each, [column]) if for_each is not None else []
        frame = self._number_frame(step, [column])
        self._note_empty(frame, [column])
        arrays = self._group_arrays(frame, groups, column)
        name = f"percentile {number:g}"
        values = {key: (float(np.percentile(x, number, method=rule)) if len(x) else math.nan)
                  for key, x in arrays.items()}
        r_type = PERCENTILE_RULES.index(rule) + 1
        how = f'NumPy percentile(method="{rule}"), as R quantile(type = {r_type})'
        if not groups:
            value = values[()]
            print(f'The {_ordinal(number)} percentile of "{column}" is {_say_number(value)} ({how}).')
            return value
        data = {g: [key[i] for key in values] for i, g in enumerate(groups)}
        data[f"{name} of {column}"] = list(values.values())
        table = self._new_table(nw.from_dict(data, backend=self._frame.implementation))
        shown = _say_groups(table._frame, groups, f"{name} of {column}")
        print(f'The {_ordinal(number)} percentile of "{column}" for each {_each(groups)}: {shown} ({how}).')
        return table

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_most_common_of(self, column=None, for_each_group_in=None, every=None):
        """The value that turns up most often (the mode), for numbers or text; empty cells are skipped.

        table.find_most_common_of("days_absent", for_each_group_in="school")   (with sdata.get_example("school"))
        When values are tied, the smallest (first in order) is given and a note names the
        others. Without for_each_group_in= you get the value; with it a new table with, for each
        group, the most common value, how many rows have it, its percent of the group's
        filled cells, and how many values share the top count.
        """
        step = "find_most_common_of"
        example = 'table.find_most_common_of("days_absent", for_each_group_in="school")   (with sdata.get_example("school"))'
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs one column name in quotes.\nFor example:  {example}")
        self._need_columns(column)
        groups = self._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else []
        frame = self._frame
        empty = self._empty(column)
        n_empty = int(frame.select(empty.cast(nw.Int64).sum()).item())
        frame, periods = self._periods(step, frame, groups or None, every)
        kept = frame.filter(~_empty_in(frame, column)) if n_empty else frame
        if n_empty:
            print(f'Note: {n_empty} empty cell{"" if n_empty == 1 else "s"} in "{column}" '
                  f'{"was" if n_empty == 1 else "were"} skipped.')
        values = [_plain(_as_datetime(v)) for v in kept[column].to_list()]
        keys = [_key(r) for r in kept.select(groups).rows()] if groups else [()] * len(values)
        by_group: dict = {}
        for key, v in zip(keys, values):
            counts = by_group.setdefault(key, {})
            counts[v] = counts.get(v, 0) + 1
        if not by_group:
            raise SimplydataError(f'"{column}" has no values to count: every cell is empty.')
        found = {}
        for key, counts in by_group.items():
            top = max(counts.values())
            tied = sorted((v for v, c in counts.items() if c == top), key=_order)
            found[key] = (tied, top, sum(counts.values()))
        order = sorted(found, key=lambda k: tuple(_order(v) for v in k))
        ties = []
        for key in order:
            tied, top, total = found[key]
            if len(tied) > 1:
                where = " / ".join(_say_label(v, periods.get(g)) for g, v in zip(groups, key)) or f'"{column}"'
                ties.append(f"{where} ({', '.join(_say_label(t) for t in tied[:6])}{' ...' if len(tied) > 6 else ''})")
        if not groups:
            tied, top, total = found[()]
            share = top * 100.0 / total
            if len(tied) > 1:
                listed = ", ".join(f'"{_say_label(t)}"' for t in tied[:6])
                print(f'The most common values of "{column}" are {listed}: each turns up {top} times of {total} '
                      f"({_say_percent(share)}). The first, {_say_label(tied[0])!r}, is given back.")
            else:
                print(f'The most common value of "{column}" is "{_say_label(tied[0])}": {top} of {total} filled cells '
                      f"({_say_percent(share)}).")
            return tied[0]
        name = f"most common {column}"
        data = {g: [k[i] for k in order] for i, g in enumerate(groups)}
        if name in data or any(c in data for c in ("count", "percent", "values with that count")):
            raise SimplydataError(f'A for_each_group_in= column has the name of a result column ("{name}", "count" or '
                                  '"percent"). Rename it first.')
        data[name] = [found[k][0][0] for k in order]
        data["count"] = [found[k][1] for k in order]
        data["percent"] = [found[k][1] * 100.0 / found[k][2] for k in order]
        data["values with that count"] = [len(found[k][0]) for k in order]
        result = self._new_table(nw.from_dict(data, backend=self._frame.implementation))
        result = self._new_table(result._frame.with_columns(nw.col("count").cast(nw.Int64),
                                                             nw.col("values with that count").cast(nw.Int64)))
        shown = _say_groups(result._frame, groups, name, periods, say=_say_label)
        print(f'The most common "{column}" for each {_each(groups, periods)}: {shown}.')
        if ties:
            print(f"Note: more than one value is the most common in {', '.join(ties[:GROUPS_IN_SENTENCE])}"
                  f"{' ...' if len(ties) > GROUPS_IN_SENTENCE else ''}; the table shows the first of them.")
        _period_note(periods)
        return result

    # ------------------------------------------------------------------ counting words
    @friendly(renamed={"for_each": "for_each_group_in"})
    def count_rows(self, for_each_group_in=None, across=None, every=None, in_percent=False):
        """How many rows the table has, or how many in each group.

        table.count_rows(for_each_group_in="class")   (with sdata.get_example("marks"))
        across= gives a cross table (pandas crosstab), one column per value:
        table.count_rows(for_each_group_in="shop", across="fruit")   (with sdata.get_example("fruit"))
        in_percent=True gives percents (0 to 100) instead: of all rows, or with across= of
        each row of the cross table, so every row adds up to 100 %.
        every="month" with a date column in for_each_group_in= counts the rows of each month.
        """
        step = "count_rows"
        if not isinstance(in_percent, bool):
            raise SimplydataError("in_percent= should be True or False.")
        if for_each_group_in is None:
            if across is not None:
                self._check_across(step, across, None)
            if every is not None:
                self._periods(step, self._frame, None, every)
            if in_percent:
                raise SimplydataError(
                    "in_percent=True needs groups to share out the rows.\n"
                    'For example:  table.count_rows(for_each_group_in="class", in_percent=True)   (with sdata.get_example("marks"))'
                )
            n = len(self._frame)
            print(f"The table has {n} row{'' if n == 1 else 's'}.")
            return n
        groups = self._group_columns(step, for_each_group_in)
        if across is not None:
            self._check_across(step, across, groups)
        frame, periods = self._periods(step, self._frame, groups, every)
        each = _each(groups, periods)
        if across is not None:
            result, labels = self._cross(frame, groups, across, nw.len(), fill=0, periods=periods)
            say = _say_number
            if in_percent:
                shares = result._frame.with_columns(nw.sum_horizontal(*labels).alias("__total")).with_columns(
                    *(nw.col(c).cast(nw.Float64) * 100.0 / nw.col("__total") for c in labels)).drop("__total")
                result = self._new_table(shares)
                say = _say_percent
                print(f'Percent of rows in each "{across}" (columns) for each {each} (rows); each row adds up to 100 %:')
            else:
                result = self._new_table(result._frame.with_columns(nw.col(c).cast(nw.Int64) for c in labels))
                print(f'Rows for each {each} (rows) and each "{across}" (columns):')
            self._say_cross(result, groups, labels, say=say, periods=periods)
            _period_note(periods)
            return result
        summary = self._grouped(frame, groups, [nw.len().alias("count")])
        result = self._new_table(summary._frame.with_columns(nw.col("count").cast(nw.Int64)))
        if in_percent:
            total = max(len(self._frame), 1)
            result = self._new_table(result._frame.with_columns((nw.col("count") * 100.0 / total).alias("percent")))
            print(f"Percent of all {len(self._frame)} rows in each {each}: "
                  f"{_say_groups(result._frame, groups, 'percent', periods, _say_percent)}.")
        else:
            print(f"Rows for each {each}: {_say_groups(result._frame, groups, 'count', periods)}.")
        _period_note(periods)
        return result

    @friendly
    def count_each(self, column, interval=None):
        """Each different value in a column, how many times it appears, and its percent.

        Biggest count first. Empty cells count as a value of their own, so the percents
        are out of all rows. Percents are rounded to 1 decimal place.
        table.count_each("fruit")   (with sdata.get_example("fruit"))
        interval=95 adds a 95 % interval to each percent that holds for all of them at once
        (Sison and Glaz, statsmodels multinomial_proportions_confint, as R
        DescTools::MultinomCI()).
        """
        if not isinstance(column, str):
            raise SimplydataError(
                "count_each() needs one column name in quotes.\n"
                'For example, with sdata.get_example("fruit"): table.count_each("fruit")'
            )
        self._need_columns(column)
        if column in ("count", "percent"):
            raise SimplydataError(
                f'count_each() makes columns called "count" and "percent", so it cannot count a column called "{column}".\n'
                f'Rename it first, for example table.rename_column("{column}", to="number").'
            )
        total = len(self._frame)
        result = (
            self._frame.group_by([column], drop_null_keys=False)
            .agg(nw.len().alias("count"))
            .with_columns(nw.col("count").cast(nw.Int64))
            .with_columns((nw.col("count") * 100.0 / max(total, 1)).round(1).alias("percent"))
            .sort(["count", column], descending=[True, False], nulls_last=True)
        )
        kinds = len(result)
        print(f'How many rows have each "{column}" ({kinds} different value{"" if kinds == 1 else "s"}): '
              f"{_say_groups(result, [column], 'count')}.")
        if interval is not None:
            from statsmodels.stats.proportion import multinomial_proportions_confint

            level = _check_percent("count_each", interval, "interval", 'table.count_each("fruit", interval=95)')
            if not 50 <= level < 100 or kinds < 2:
                raise SimplydataError("interval= is the level in percent, such as interval=95, and needs at least two "
                                      "different values.")
            counts = result["count"].to_numpy()
            ci = multinomial_proportions_confint(counts, alpha=1 - level / 100, method="sison-glaz")
            result = result.with_columns(
                nw.new_series(f"percent {level:g} % CI low", ci[:, 0] * 100, nw.Float64, backend=self._frame.implementation),
                nw.new_series(f"percent {level:g} % CI high", ci[:, 1] * 100, nw.Float64,
                              backend=self._frame.implementation))
            print(f"The {level:g} % intervals hold for all {kinds} percents at once (Sison and Glaz; statsmodels "
                  "multinomial_proportions_confint, as R DescTools::MultinomCI()).")
        return self._new_table(nw.maybe_reset_index(result))

    @friendly(renamed={"for_each": "for_each_group_in"})
    def count_different_values_in(self, column=None, for_each_group_in=None, every=None):
        """How many different values a column has, or how many in each group.

        table.count_different_values_in("name", for_each_group_in="class")   (with sdata.get_example("marks"))
        Empty cells are not counted (as pandas nunique()); a note says how many there were.
        Capital letters matter: "Apple" and "apple" are two values.
        """
        step = "count_different_values_in"
        if not isinstance(column, str):
            raise SimplydataError(
                f"{step}() needs one column name in quotes.\n"
                f'For example:  table.{step}("name", for_each_group_in="class")   (with sdata.get_example("marks"))'
            )
        self._need_columns(column)
        groups = self._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else None
        empty = self._empty(column)
        frame = self._frame.with_columns(nw.when(~empty).then(nw.col(column)).alias("__value"),
                                         empty.cast(nw.Int64).alias("__empty"))
        frame, periods = self._periods(step, frame, groups, every)
        n_empty = int(frame.select(nw.col("__empty").sum()).item())
        found = [nw.col("__value").n_unique().alias("__unique"), nw.col("__empty").sum().alias("__empties")]
        if n_empty:
            print(f'Note: {n_empty} empty cell{"" if n_empty == 1 else "s"} in "{column}" '
                  f'{"was" if n_empty == 1 else "were"} not counted.')
        if groups is None:
            unique, empties = frame.select(*found).row(0)
            n = int(unique) - (1 if empties else 0)  # n_unique counts the empty value once
            print(f'"{column}" has {n} different value{"" if n == 1 else "s"}.')
            return n
        summary = self._grouped(frame, groups, found)._frame
        summary = summary.with_columns(
            (nw.col("__unique") - nw.when(nw.col("__empties") > 0).then(1).otherwise(0)).cast(nw.Int64)
            .alias("different values")).select(*groups, "different values")
        result = self._new_table(summary)
        print(f'Different values of "{column}" for each {_each(groups, periods)}: '
              f"{_say_groups(summary, groups, 'different values', periods)}.")
        _period_note(periods)
        return result

    # ------------------------------------------------------------------ percents
    @friendly(renamed={"method": "interval_by", "for_each": "for_each_group_in", "above": "is_above",
                       "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                       "one_of": "is_one_of"})
    def find_percent_of_rows_where(self, column=None, *extra, for_each_group_in=None, every=None, is_above=_NOT_GIVEN, is_below=_NOT_GIVEN,
                                   is_at_least=_NOT_GIVEN, is_at_most=_NOT_GIVEN, is_equal_to=_NOT_GIVEN, is_not_equal_to=_NOT_GIVEN,
                                   is_between=_NOT_GIVEN, is_one_of=_NOT_GIVEN, contains=_NOT_GIVEN, starts_with=_NOT_GIVEN,
                                   ends_with=_NOT_GIVEN, is_empty=_NOT_GIVEN, interval_by="exact"):
        """What percent of the rows meet a condition, or each group's share.

        table.find_percent_of_rows_where("marks", is_above=60, for_each_group_in="class")   (with sdata.get_example("marks"))
        With a condition (the same words as keep_rows_where: is_above, is_below, is_at_least, is_at_most,
        is_equal_to, is_not_equal_to, is_between, is_one_of, contains, starts_with, ends_with, is_empty):
        the percent of rows that meet it, out of the rows with a value in the column, with
        its 95 % confidence interval (Clopper-Pearson exact interval, as R binom.test).
        Without a condition:
        table.find_percent_of_rows_where(for_each_group_in="class")   each group's percent of all rows
        table.find_percent_of_rows_where("count", for_each_group_in="shop")   each group's share of the total of a
        column   (with sdata.get_example("fruit"))
        Percents go from 0 to 100. Without for_each_group_in= you get one number; with it a new table.
        interval_by= chooses the 95 % interval of a percent: "exact" (Clopper-Pearson, the default, as R
        binom.test()), "wilson" (Wilson score) or "agresti-coull"; the last two from statsmodels
        proportion_confint, as R DescTools::BinomCI().
        """
        step = "find_percent_of_rows_where"
        method = _percent_method(step, interval_by)
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, contains=contains,
                       starts_with=starts_with, ends_with=ends_with, is_empty=is_empty)
        given = {k: v for k, v in options.items() if v is not _NOT_GIVEN}
        example = 'table.find_percent_of_rows_where("marks", is_above=60, for_each_group_in="class")   (with sdata.get_example("marks"))'
        if extra:
            raise SimplydataError(
                f"{step}() needs the column and then one plain word saying which rows, like is_above=60 or "
                f'is_equal_to="A".\nFor example:  {example}'
            )
        if column is None:
            if given:
                raise SimplydataError(f"{step}() needs the column name first.\nFor example:  {example}")
            if for_each_group_in is None:
                raise SimplydataError(
                    f"{step}() needs a column with a condition, or groups to share out the rows.\n"
                    f"For example:  {example}\n"
                    'or:           table.find_percent_of_rows_where(for_each_group_in="class")'
                )
            return self._percent_of_rows(step, for_each_group_in, every, method)
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs one column name in quotes.\nFor example:  {example}")
        self._need_columns(column)
        groups = self._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else None
        if not given:
            return self._percent_of_total(step, column, groups, every)
        if len(given) > 1:
            names = " and ".join(f"{c}=" for c in given)
            raise SimplydataError(
                f"{step}() takes one condition at a time, but you gave {names}. "
                "Use is_between=[low, high] for a range.\n"
                'For example:  table.find_percent_of_rows_where("marks", is_between=[40, 80])   (with sdata.get_example("marks"))'
            )
        cond, words = self._condition(step, column, options, ())
        counted = nw.lit(True) if "is_empty" in given else ~self._empty(column)
        frame = self._frame.with_columns(cond.cast(nw.Int64).alias("__hit"), counted.cast(nw.Int64).alias("__counted"))
        frame, periods = self._periods(step, frame, groups, every)
        sums = [nw.col("__hit").sum().alias("matching rows"), nw.col("__counted").sum().alias("rows")]
        left_out = len(frame) - int(frame.select(nw.col("__counted").sum()).item())
        if left_out:
            print(f'Note: {left_out} row{"" if left_out == 1 else "s"} with an empty cell in "{column}" '
                  f'{"was" if left_out == 1 else "were"} left out of the percent.')
        if groups is None:
            hits, rows = (int(v) for v in frame.select(*sums).row(0))
            share, low, high = _share(hits, rows, method)
            print(f'"{column}" {words} in {_say_percent(share)} of the rows ({hits} of {rows}; 95 % CI '
                  f"{_say_percent(low)} to {_say_percent(high)}, {PERCENT_METHODS[method][0]}).")
            return share
        summary = self._grouped(frame, groups, sums)._frame
        result = self._with_shares(summary, "matching rows", "rows", method)
        items = []
        for row in result._frame.select(*groups, "matching rows", "rows", "percent").rows():
            name = " / ".join(_say_label(v, periods.get(g)) for g, v in zip(groups, row))
            items.append(f"{name} {_say_percent(row[-1])} ({row[-3]} of {row[-2]})")
        text = ", ".join(items[:GROUPS_IN_SENTENCE])
        if len(items) > GROUPS_IN_SENTENCE:
            text += f" ... and {len(items) - GROUPS_IN_SENTENCE} more (the new table has them all)"
        print(f'Percent of rows where "{column}" {words}, for each {_each(groups, periods)}: {text}. '
              f"(The new table has {_interval_words(method)}.)")
        _period_note(periods)
        return result

    def _with_shares(self, summary, hits: str, rows: str, method: str = "exact"):
        """Add percent and its 95 % interval (Clopper-Pearson unless interval_by= says otherwise) to a small table of counts."""
        summary = nw.maybe_reset_index(summary.with_columns(nw.col(hits).cast(nw.Int64), nw.col(rows).cast(nw.Int64)))
        found = [_share(int(h), int(n), method) for h, n in summary.select(hits, rows).rows()]
        backend = summary.implementation
        columns = [nw.new_series(name, [f[i] for f in found], nw.Float64, backend=backend)
                   for i, name in enumerate(("percent", "percent 95 % CI low", "percent 95 % CI high"))]
        return self._new_table(summary.with_columns(*columns))

    def _percent_of_rows(self, step, for_each, every, method="exact"):
        groups = self._group_columns(step, for_each)
        frame, periods = self._periods(step, self._frame, groups, every)
        summary = self._grouped(frame, groups, [nw.len().alias("count")])._frame
        summary = summary.with_columns(nw.lit(len(frame)).alias("__all"))
        result = self._with_shares(summary, "count", "__all", method)
        result = self._new_table(result._frame.drop("__all"))
        print(f"Percent of all {len(frame)} rows in each {_each(groups, periods)}: "
              f"{_say_groups(result._frame, groups, 'percent', periods, _say_percent)}. "
              f"(The new table has {_interval_words(method)}.)")
        _period_note(periods)
        return result

    def _percent_of_total(self, step, column, groups, every):
        if groups is None:
            raise SimplydataError(
                f'{step}("{column}") needs for_each_group_in= to share out the total of "{column}", or a condition '
                "such as is_above=60 to count rows.\n"
                'For example:  table.find_percent_of_rows_where("count", for_each_group_in="shop")   (with sdata.get_example("fruit"))'
            )
        frame = self._number_frame(step, [column])
        frame, periods = self._periods(step, frame, groups, every)
        grand = _plain(frame.select(nw.col(column).sum()).item())
        if not grand:
            raise SimplydataError(f'The total of "{column}" is 0, so there is no total to share out.')
        if frame.select((nw.col(column) < 0).any()).item():
            print(f'Note: "{column}" has numbers below 0, so a share can be below 0 % or above 100 %.')
        self._note_empty(frame, [column])
        total = f"total of {column}"
        summary = self._grouped(frame, groups, [nw.col(column).sum().alias(total)])._frame
        result = self._new_table(summary.with_columns((nw.col(total) * 100.0 / grand).alias("percent")))
        print(f'Share of the total of "{column}" ({_say_number(grand)}) for each {_each(groups, periods)}: '
              f"{_say_groups(result._frame, groups, 'percent', periods, _say_percent)}.")
        _period_note(periods)
        return result

    # ------------------------------------------------------------------ several measures at once
    @staticmethod
    def _measures(step, show):
        if show is None:
            return list(DEFAULT_MEASURES)
        items = show if isinstance(show, (list, tuple)) else [show]
        if not items:
            raise SimplydataError(
                f"show= needs at least one measure.\n"
                f'For example:  table.{step}("marks", show=["average", "standard deviation", "count"])'
                '   (with sdata.get_example("marks"))'
            )
        measures = []
        for item in items:
            if callable(item):
                measures.append(item)
                continue
            name = _measure_name(step, item)
            if name not in measures:
                measures.append(name)
        return measures

    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_summary_of(self, column=None, show=None, for_each_group_in=None, every=None):
        """Several measures of one or more columns at once, in one tidy table.

        table.find_summary_of("marks", for_each_group_in="class", show=["average", "standard deviation", "count"])
        (with sdata.get_example("marks")). Several columns: table.find_summary_of(["marks", "hours"]).
        show= takes any of: "count" (numbers, empty cells left out), "average", "median",
        "total", "smallest", "biggest", "standard deviation" (sample, n - 1), "variance"
        (sample, n - 1), "standard error" (of the average), "confidence interval" (95 % t
        interval of the average, as R t.test), "range" (biggest minus smallest),
        "interquartile range" (upper quartile minus lower quartile, R type 7),
        "empty cells", and these, with the definitions R uses:
        "geometric mean" (numbers above 0), "skewness" and "kurtosis" (the bias-corrected
        sample values G1 and G2, as SciPy skew/kurtosis(bias=False), R e1071 type 2 and
        Excel; kurtosis is excess kurtosis, 0 for a bell shape), "coefficient of variation"
        (standard deviation / average, a ratio), "median absolute deviation" (as R mad(),
        times 1.4826), "trimmed average" (10 % cut from each end, as R mean(trim = 0.1);
        "trimmed average 20" cuts 20 %), "most common" (the smallest if tied),
        "percentile 90" (any percent, R quantile type 7), "harmonic mean" (numbers above 0,
        SciPy hmean, as R psych::harmonic.mean) and "winsorised average" (the lowest and
        highest 20 % set to the nearest value kept, then the average; SciPy, as R
        WRS2::winmean(tr = 0.2); "winsorised average 10" pulls in 10 %).
        Without show=: count, average, standard deviation, smallest, median,
        biggest. A measure of your own also works: a function that gets one group's
        numbers (a NumPy array) and gives back one number, show=["average", my_measure].
        The new table has one row for each column (and each group), so it can be saved
        or charted. every= groups a date column in for_each_group_in= by "week", "month", "year" ...
        """
        step = "find_summary_of"
        if column is None:
            raise SimplydataError(
                f"{step}() needs the column to summarise.\n"
                f'For example:  table.{step}("marks", for_each_group_in="class", show=["average", "count"])'
                '   (with sdata.get_example("marks"))'
            )
        columns = _as_list(step, "the column", column)
        measures = self._measures(step, show)
        groups = self._group_columns(step, for_each_group_in, columns) if for_each_group_in is not None else []
        if "column" in groups:
            raise SimplydataError(
                'find_summary_of() makes a column called "column", so a for_each_group_in= column cannot have that name.\n'
                'Rename it first, for example table.rename_column("column", to="group").'
            )
        frame = self._number_frame(step, columns)
        frame, periods = self._periods(step, frame, groups or None, every)
        frame = frame.with_columns(nw.col(c).is_null().cast(nw.Int64).alias(f"__empty {i}")
                                   for i, c in enumerate(columns))
        names = [m for m in measures if isinstance(m, str) and not _is_array_measure(m)]
        arrays = [m for m in measures if _is_array_measure(m)]
        own = [m for m in measures if not isinstance(m, str)]
        problems: dict = {}  # (measure, why) -> [where]
        data = {"column": [], **{g: [] for g in groups}}
        out_names, own_names = [], []
        for m in measures:
            if m == "confidence interval":
                out_names += ["average 95 % CI low", "average 95 % CI high"]
            elif isinstance(m, str):
                out_names.append(m)
            else:
                label = getattr(m, "__name__", "") or ""
                label = "own measure" if not label or label.startswith("<") else label
                while label in out_names or label in data:
                    label += " (own)"
                own_names.append(label)
                out_names.append(label)
        for name in out_names:
            if name in data:
                raise SimplydataError(f'A for_each_group_in= column is called "{name}", like a measure. Rename it first.')
            data[name] = []
        for i, c in enumerate(columns):
            col = nw.col(c)
            raw = {"n": col.count(), "mean": col.mean(), "median": col.median(), "sum": col.sum(), "min": col.min(),
                   "max": col.max(), "sd": col.std(ddof=1), "var": col.var(ddof=1),
                   "q1": col.quantile(0.25, interpolation="linear"), "q3": col.quantile(0.75, interpolation="linear"),
                   "empty": nw.col(f"__empty {i}").sum()}
            exprs = [e.alias(f"__{k}") for k, e in raw.items()]
            if groups:
                agg = frame.group_by(groups, drop_null_keys=False).agg(*exprs).sort(groups, nulls_last=True)
            else:
                agg = frame.select(*exprs)
            own_values = self._own_measures(frame, groups, c, own, own_names) if own else {}
            array_values = self._array_measures(frame, groups, c, arrays, problems, len(columns) > 1) if arrays else {}
            for row in agg.rows(named=True):
                key = _key([row[g] for g in groups])
                data["column"].append(c)
                for g, v in zip(groups, key):
                    data[g].append(v)
                values = _measure_values(names, {k: _plain(row[f"__{k}"]) for k in raw})
                for name in out_names:
                    if name in values:
                        data[name].append(values[name])
                    elif (key, name) in array_values:
                        data[name].append(array_values[(key, name)])
                    else:
                        data[name].append(own_values.get((key, name)))
        result = nw.from_dict(data, backend=self._frame.implementation)
        float_names = [n for n in out_names if _is_array_measure(n)]
        if float_names:
            result = result.with_columns(nw.col(n).cast(nw.Float64) for n in float_names)
        result = result.with_columns(nw.col(n).cast(nw.Int64) for n in ("count", "empty cells") if n in out_names)
        table = self._new_table(result)
        self._note_empty(frame, columns)
        self._say_summary(table, columns, groups, out_names, periods)
        for (name, why), places in problems.items():
            where = ", ".join(places[:GROUPS_IN_SENTENCE]) + (" ..." if len(places) > GROUPS_IN_SENTENCE else "")
            if why.startswith("tied:"):
                print(f"Note: more than one value is the most common in {where}; the table shows the smallest.")
            else:
                print(f"Note: the {name} {why}, so it is empty for {where}.")
        for name in out_names:
            if name.startswith("trimmed average "):
                share = float(name.split()[-2])
                place = " in each group" if groups else ""
                print(f"Note: {name} leaves out the lowest and highest {share:g} % of the values{place}, "
                      f"as R mean(x, trim = {share / 100:g}).")
            if name.startswith("winsorised average "):
                share = float(name.split()[-2])
                place = " in each group" if groups else ""
                print(f"Note: {name} sets the lowest and highest {share:g} % of the values{place} to the nearest value "
                      f"kept, then takes the average, as R WRS2::winmean(x, tr = {share / 100:g}).")
        _period_note(periods)
        return table

    @staticmethod
    def _group_arrays(frame, groups, column) -> dict:
        """{group key: the group's numbers (empty cells left out)}, in the order the groups turn up."""
        values = frame.select(nw.col(column).cast(nw.Float64))[column].to_numpy()
        keys = [_key(r) for r in frame.select(groups).rows()] if groups else [()] * len(values)
        by_group: dict = {}
        for key, v in zip(keys, values):
            by_group.setdefault(key, [])
            if not math.isnan(v):
                by_group[key].append(v)
        return {key: np.asarray(numbers, dtype=float) for key, numbers in by_group.items()}

    def _array_measures(self, frame, groups, column, names, problems, several) -> dict:
        """{(group key, measure): value} for the measures worked out with NumPy / SciPy."""
        out = {}
        for key, array in self._group_arrays(frame, groups, column).items():
            label = [f'"{column}"'] if several or not groups else []
            label += [_say_label(v) for v in key]
            where = " / ".join(label) if groups else f'"{column}"'
            for name in names:
                value, why, tied = _array_measure(name, array)
                out[(key, name)] = value
                if why:
                    problems.setdefault((name, why), []).append(where)
                if tied is not None and len(tied) > 1:
                    problems.setdefault((name, "tied:"), []).append(
                        f"{where} ({', '.join(_say_number(t) for t in tied[:6])})")
        return out

    def _own_measures(self, frame, groups, column, functions, labels):
        """{(group key, label): value} for measures written by the user."""
        out = {}
        for key, array in self._group_arrays(frame, groups, column).items():
            for function, label in zip(functions, labels):
                where = f'"{column}"' + (f" in group {' / '.join(_say_label(v) for v in key)}" if groups else "")
                try:
                    value = function(array)
                    value = None if value is None else float(value)
                except Exception as error:  # the user's own code: say what went wrong in plain words
                    raise SimplydataError(
                        f'Your measure "{label}" did not work on {where}: {error}\n'
                        "A measure of your own gets the numbers of one group (a NumPy array, empty cells left out) "
                        "and gives back one number, for example:\n"
                        "    def spread(values):\n        return values.max() - values.min()\n"
                        '    table.find_summary_of("marks", show=["average", spread])   (with sdata.get_example("marks"))'
                    ) from None
                out[(key, label)] = value
        return out

    @staticmethod
    def _say_summary(table, columns, groups, out_names, periods):
        header = f"Summary of {_names(columns)}"
        if groups:
            header += f" for each {_each(groups, periods)}"
        print(header + ":")
        rows = table._frame.rows(named=True)
        for row in rows[:SUMMARY_LINES]:
            label = [f'"{row["column"]}"'] if len(columns) > 1 else []
            label += [_say_label(row[g], periods.get(g)) for g in groups]
            items = []
            for name in out_names:
                if name == "average 95 % CI high":
                    continue
                if name == "average 95 % CI low":
                    items.append(f"95 % CI {_say_number(row[name])} to {_say_number(row['average 95 % CI high'])}")
                else:
                    items.append(f"{name} {_say_number(row[name])}")
            start = "  " + " / ".join(label) + ": " if label else "  "
            print(start + ", ".join(items))
        if len(rows) > SUMMARY_LINES:
            print(f"  ... and {len(rows) - SUMMARY_LINES} more rows (the new table has them all)")

    # ------------------------------------------------------------------ one column on its own
    @friendly
    def get_column(self, name=None):
        """One column on its own: a column of numbers becomes sdata.numbers, any other a plain list.

        marks = table.get_column("marks")   (with sdata.get_example("marks"))
        then marks.find_average(), marks.start_chart() ... like any sdata.numbers. Empty cells become
        empty numbers. The table does not change.
        """
        if not isinstance(name, str):
            raise SimplydataError(
                "get_column() needs one column name in quotes.\n"
                'For example:  marks = table.get_column("marks")   (with sdata.get_example("marks"))'
            )
        self._need_columns(name)
        dtype = self._frame.schema[name]
        series = self._frame[name]
        if dtype.is_numeric():
            from ..numbers import numbers

            if series.null_count() or dtype.is_float():
                values = series.cast(nw.Float64).to_numpy()
            else:
                values = series.cast(nw.Int64).to_numpy()
            return numbers(values)
        kind = "text" if dtype == nw.String or dtype == nw.Categorical or dtype == nw.Enum else (
            "True/False values" if dtype == nw.Boolean else "dates" if dtype.is_temporal() else "values")
        print(f'Note: "{name}" holds {kind}, not numbers, so it comes back as a plain Python list.')
        return [None if _missing(v) else _plain(v) for v in series.to_list()]

    # ------------------------------------------------------------------ correlation
    @friendly(renamed={"seed": "with_seed"})
    def find_correlation_between(self, *columns, method="pearson", show="r", sides=2, higher=None, lower=None,
                                 alternative=None, p_value_by="formula", interval_by=None, shuffles=9999, resamples=9999,
                                 with_seed=1, allowing_for=None, rows_back=None, sorted_by=None,
                                 empty_cells="leave out"):
        """How strongly columns of numbers go up or down together, from -1 to 1.

        table.find_correlation_between("hours", "marks")   (with sdata.get_example("marks"))
        method="pearson" (a straight-line link, the usual one), "spearman" (uses ranks,
        for any link that keeps going one way) or "kendall" (Kendall's tau-b, also ranks: the
        share of pairs of rows that agree in order minus the share that disagree; as R
        cor.test(method = "kendall"), SciPy kendalltau). Prints the strength in words and the
        p-value from SciPy. With two columns it gives back the number r; rows with an
        empty cell in either column are skipped.
        With three or more columns it gives back a correlation table (as pandas .corr()),
        and prints the strongest pairs:
        table.find_correlation_between("hours", "marks", "height")
        Each pair uses the rows where both columns have a number. show="p-value" gives the
        table of p-values instead, and show="each pair" one row per pair (r, p-value,
        rows), ready for add_adjusted_p_value_column(): testing many pairs makes a chance
        finding more likely. show="covariance" gives the covariance table instead (pandas
        DataFrame.cov(), dividing by n - 1, each pair on the rows where both columns have a number,
        as R cov(use = "pairwise.complete.obs")), also for two columns: covariances are in the units
        of the two columns multiplied; the correlation is the same link without units.
        Strength words for the size of r: below 0.2 very weak, from 0.2 weak, from 0.4
        medium, from 0.6 strong, from 0.8 very strong (after Evans 1996).
        The p-value is said as how often a link this strong or stronger would turn up in studies
        like this one if there were truly no link ("about 3 of 100 studies", p = 0.031).
        sides=1, higher="positive" (or "negative") tests in one direction only, as decided before
        seeing the data (R cor.test(alternative = "greater")); two columns only.
        Two columns only: p_value_by="shuffling" gives the p-value from shuffling one column
        against the other shuffles=9999 times (with_seed=1; SciPy permutation_test), and
        interval_by="bootstrap" adds a 95 % interval of r from drawing the rows again with
        replacement resamples=9999 times (with_seed=1; SciPy bootstrap, BCa, as R boot::boot.ci()).
        With rows_back=12 and two columns (sorted_by= the time column): the correlation for shifts
        -12 to 12 (cross-correlation, as R ccf with the sign of the lag reversed): shift 2 pairs the
        first column with the second 2 rows later. It says which column follows the other.
        empty_cells="multiple imputation" fills in the empty cells 20 times from the other columns named
        (statsmodels MICEData, as explain()) and pools the correlations with Rubin's rules on Fisher's z (R
        miceadds::micombine.cor()); with_seed= fixes the random filling.
        A correlation does not show that one thing causes the other.
        """
        step = "find_correlation_between"
        names = []
        for value in columns:
            names.extend(value if isinstance(value, (list, tuple)) else [value])
        if len(names) < 2 or not all(isinstance(v, str) for v in names):
            raise SimplydataError(
                f"{step}() needs two column names in quotes (or more, for a correlation table).\n"
                f'For example, with sdata.get_example("marks"): table.{step}("hours", "marks")'
            )
        if rows_back is not None or sorted_by is not None:
            if rows_back is None:
                raise SimplydataError(f"{step}() uses sorted_by= with rows_back= (the cross-correlation); "
                                      "give rows_back=, such as rows_back=12.")
            if (sides != 2 or higher is not None or lower is not None or alternative not in (None, "two-sided")
                    or p_value_by != "formula" or interval_by is not None or allowing_for is not None):
                raise SimplydataError(f"{step}() with rows_back= gives the cross-correlation; leave out sides=, "
                                      "higher=, lower=, p_value_by=, interval_by= and allowing_for=.")
            if _plain_name(method) != "pearson" or _plain_name(show) != "r":
                raise SimplydataError(f"{step}() with rows_back= gives the cross-correlation, which is "
                                      'Pearson\'s r (as R ccf()); leave out method= and show=.')
            return self._cross_correlation(step, names, rows_back, sorted_by)
        self._check_choice(step, "method", method, CORRELATION_METHODS)
        from .imputation_more import MULTIPLE, read_empty_cells

        if read_empty_cells(step, empty_cells, f'table.{step}("{names[0]}", "{names[1]}")') == MULTIPLE:
            if (_plain_name(show) != "r" or sides != 2 or higher is not None or lower is not None
                    or alternative not in (None, "two-sided") or p_value_by != "formula" or interval_by is not None
                    or allowing_for is not None):
                raise SimplydataError('empty_cells="multiple imputation" gives the pooled correlations with their '
                                      "intervals; leave out show=, sides=, higher=, p_value_by=, interval_by= and "
                                      "allowing_for=.")
            if len(set(names)) < len(names):
                raise SimplydataError("Give each column once.")
            from .imputation_more import correlation_imputed

            found = correlation_imputed(self, step, names, _plain_name(method), with_seed)
            if found is not None:
                return found
        shown = _plain_name(show)
        if shown not in CORRELATION_SHOW:
            raise choice_error(step, "show", show, list(CORRELATION_SHOW))
        if shown == "covariance":
            if len(set(names)) < len(names):
                twice = next(n for n in names if names.count(n) > 1)
                raise SimplydataError(f'"{twice}" is listed twice. Give each column once.')
            if (_plain_name(method) != "pearson" or sides != 2 or higher is not None or lower is not None
                    or alternative not in (None, "two-sided") or p_value_by != "formula" or interval_by is not None
                    or allowing_for is not None):
                raise SimplydataError('show="covariance" gives the covariance table (no test, no ranks); leave out '
                                      "method=, sides=, higher=, p_value_by=, interval_by= and allowing_for=.\n"
                                      'For example:  table.find_correlation_between("hours", "marks", "height", '
                                      'show="covariance")')
            return self._covariance_table(step, self._number_frame(step, names), names)
        if len(set(names)) < len(names):
            if len(names) == 2:
                raise SimplydataError(
                    f"{step}() needs two different columns.\n"
                    f'For example, with sdata.get_example("marks"): table.{step}("hours", "marks")'
                )
            twice = next(n for n in names if names.count(n) > 1)
            raise SimplydataError(f'"{twice}" is listed twice. Give each column once.')
        if len(names) == 2 and shown != "r":
            raise SimplydataError(
                f'show="{show}" is for a correlation table of three or more columns. With two columns you get r, '
                "and the sentence gives its p-value."
            )
        from .stat_tests import _direction

        example = f'table.find_correlation_between("{names[0]}", "{names[1]}", sides=1, higher="positive")'
        if len(names) > 2 and (sides != 2 or higher is not None or lower is not None
                               or alternative not in (None, "two-sided")):
            raise SimplydataError("sides=1 and higher= work with two columns; a correlation table tests every pair "
                                  "both ways.")
        alt, up = _direction(step, sides, higher, lower, alternative, {"positive": "greater", "negative": "less"},
                             example, lower_words=[])
        self._check_choice(step, "p_value_by", p_value_by, ("formula", "shuffling"))
        if interval_by is not None:
            self._check_choice(step, "interval_by", interval_by, ("bootstrap",))
        if len(names) > 2 and (p_value_by != "formula" or interval_by is not None):
            raise SimplydataError("p_value_by= and interval_by= work with two columns; give two column names.")
        if (method in ORDINAL_METHODS or allowing_for is not None) and len(names) != 2:
            raise SimplydataError(f'method="{method}" and allowing_for= work with two columns.' if allowing_for is None
                                  else "allowing_for= works with two columns (and the one to allow for).")
        if method in ORDINAL_METHODS and (alt != "two-sided" or p_value_by != "formula" or interval_by is not None
                                          or allowing_for is not None):
            raise SimplydataError(f'method="{method}" gives the measure with its 95 % interval; leave out sides=, '
                                  "p_value_by=, interval_by= and allowing_for=.")
        if allowing_for is not None:
            if not isinstance(allowing_for, str) or allowing_for in names:
                raise SimplydataError('allowing_for= needs a third column name, such as allowing_for="height".')
            if alt != "two-sided" or p_value_by != "formula" or interval_by is not None:
                raise SimplydataError("allowing_for= gives the two-sided partial correlation; leave out sides=, "
                                      "p_value_by= and interval_by=.")
            return self._partial_correlation(step, self._number_frame(step, names + [allowing_for]), names[0],
                                             names[1], allowing_for, method)
        frame = self._number_frame(step, names)
        if method in ORDINAL_METHODS:
            return self._ordinal_association(step, frame, names[0], names[1], method)
        if len(names) == 2:
            return self._one_correlation(step, frame, names[0], names[1], method, alt, up,
                                         p_value_by=p_value_by, interval_by=interval_by, shuffles=shuffles,
                                         resamples=resamples, seed=with_seed)
        return self._correlation_table(step, frame, names, method, shown)

    @staticmethod
    def _correlate(step, frame, column_a, column_b, method, alternative="two-sided"):
        """r, p and the number of rows used, for one pair (rows with an empty cell skipped)."""
        pairs = frame.select(column_a, column_b).drop_nulls()
        if len(pairs) < 3:
            raise SimplydataError(
                f'{step}() needs at least 3 rows where both "{column_a}" and "{column_b}" have a number; '
                f"this table has {len(pairs)}."
            )
        a = pairs[column_a].to_numpy().astype(float)
        b = pairs[column_b].to_numpy().astype(float)
        for name, values in ((column_a, a), (column_b, b)):
            if values.min() == values.max():
                where = ""
                if frame[name].drop_nulls().n_unique() > 1:
                    where = f' (in the rows where "{column_a}" and "{column_b}" both have a number)'
                raise SimplydataError(
                    f'{step}() needs numbers that change, but every number in "{name}" is the same{where}, '
                    "so there is no correlation to find."
                )
        from scipy import stats

        if method == "pearson":
            result = stats.pearsonr(a, b, alternative=alternative)
        elif method == "spearman":
            result = stats.spearmanr(a, b, alternative=alternative)
        else:
            result = stats.kendalltau(a, b, variant="b", alternative=alternative)
        return float(result[0]), float(result[1]), len(pairs)

    def _one_correlation(self, step, frame, column_a, column_b, method, alternative="two-sided", up=None,
                         p_value_by="formula", interval_by=None, shuffles=9999, resamples=9999, seed=1):
        r, p, n = self._correlate(step, frame, column_a, column_b, method, alternative)
        skipped = len(frame) - n
        name = METHOD_NAMES[method]
        if skipped:
            rows = "row" if skipped == 1 else "rows"
            verb = "was" if skipped == 1 else "were"
            print(f'Note: {skipped} {rows} with an empty cell in "{column_a}" or "{column_b}" {verb} skipped.')
        extra, interval = [], ""
        if interval_by is None:
            interval, note = self._correlation_interval(frame, column_a, column_b, method, alternative)
            if note:
                extra.append(note)
        if p_value_by == "shuffling" or interval_by is not None:
            from .resampling import bootstrap_interval, correlation, resample_p
            from .stat_tests import _num

            pairs = frame.select(column_a, column_b).drop_nulls()
            x, y = (pairs[c].to_numpy().astype(float) for c in (column_a, column_b))
            statistic = correlation(method)
            vectorized = method == "pearson"
            if p_value_by == "shuffling":
                found = resample_p((x, y), statistic, "pairings", alternative, shuffles, seed, vectorized=vectorized)
                p = found["p"]
                extra.append(f"The p-value comes from shuffling: {found['words']} (SciPy permutation_test).")
            if interval_by == "bootstrap":
                low, high, words, note = bootstrap_interval((x, y), statistic, 95, "bca", resamples, seed,
                                                            paired=True, vectorized=vectorized)
                interval = f"; values from {_num(low)} to {_num(high)} fit the data (95 % bootstrap CI)"
                extra.append(f"The interval is a {words}.")
                if note:
                    extra.append(note)
        print(
            f'The correlation between "{column_a}" and "{column_b}" is r = {r:.2f} ({name}, {n} rows): '
            f"{_strength(r)}{interval}."
        )
        if up is None:
            print(_p_sentence(p, "there were truly no link", "a link this strong or stronger",
                              "that there is no link"))
        else:
            print(_p_sentence(p, f"there were truly no {up} link", f"a {up} link this strong or stronger",
                              f"that there is no {up} link"))
        if up is not None:
            from .stat_tests import _one_sided_sentence

            other = "negative" if up == "positive" else "positive"
            print(_one_sided_sentence(f"a {up} correlation", f"a {other} one")
                  + f' As R cor.test(method = "{method}", alternative = "{alternative}").')
        for line in extra:
            print(line)
        return r

    @staticmethod
    def _correlation_interval(frame, column_a, column_b, method, alternative):
        """("; values from A to B fit the data (95 % CI)", note): Pearson from SciPy pearsonr; Spearman and Kendall
        from R DescTools (SpearmanRho: Fisher's z; KendallTauB: its asymptotic standard error); Somers' d and gamma
        from R DescTools (asymptotic)."""
        from scipy import stats

        from .._r import RMissing, r_call
        from .stat_tests import _interval_words, _num

        pairs = frame.select(column_a, column_b).drop_nulls()
        x, y = (pairs[c].to_numpy().astype(float) for c in (column_a, column_b))
        if method == "pearson":
            ci = stats.pearsonr(x, y, alternative=alternative).confidence_interval(0.95)
            kind = "" if alternative == "two-sided" else "one-sided "
            return f"; values from {_interval_words(ci.low, ci.high)} fit the data ({kind}95 % CI)", ""
        if alternative != "two-sided":
            return "", ""
        code = {"spearman": "DescTools::SpearmanRho(x, y, conf.level = 0.95)",
                "kendall": "DescTools::KendallTauB(x, y, conf.level = 0.95)",
                "somers": 'DescTools::SomersDelta(x, y, direction = "column", conf.level = 0.95)',
                "gamma": "DescTools::GoodmanKruskalGamma(x, y, conf.level = 0.95)"}[method]
        try:
            found = np.asarray(r_call(f"as.numeric({code})", packages=("DescTools",),
                                      what=f"the 95 % interval of {METHOD_NAMES[method]} (R DescTools)", x=x, y=y),
                               dtype=float)
        except RMissing:
            if method in ("somers", "gamma"):
                raise
            return "", (f"Note: the 95 % interval of {METHOD_NAMES[method]} comes from the R package DescTools, which "
                        'is not ready here; interval_by="bootstrap" gives a bootstrap interval in Python, or: pip install '
                        '"simplydata[r]", install R, then in R install.packages("DescTools").')
        how = "Fisher's z" if method == "spearman" else "asymptotic standard error"
        return f"; values from {_num(found[1])} to {_num(found[2])} fit the data (95 % CI, {how}, R DescTools)", ""

    def _ordinal_association(self, step, frame, column_a, column_b, method):
        """Somers' d (of the second column given the first) or Goodman and Kruskal's gamma, with the 95 % interval
        from R DescTools (SciPy somersd gives the same d, but no interval; gamma has no Python function)."""
        pairs = frame.select(column_a, column_b).drop_nulls()
        skipped = len(frame) - len(pairs)
        if skipped:
            print(f"Note: {skipped} row{'' if skipped == 1 else 's'} with an empty cell in \"{column_a}\" or "
                  f"\"{column_b}\" {'was' if skipped == 1 else 'were'} skipped.")
        from .._r import r_call
        from .stat_tests import _num

        x, y = (pairs[c].to_numpy().astype(float) for c in (column_a, column_b))
        code = ('DescTools::SomersDelta(x, y, direction = "column", conf.level = 0.95)' if method == "somers" else
                "DescTools::GoodmanKruskalGamma(x, y, conf.level = 0.95)")
        found = np.asarray(r_call(f"as.numeric({code})", packages=("DescTools",),
                                  what=f"{METHOD_NAMES[method]} with its 95 % interval (R DescTools)",
                                  python_note="SciPy somersd gives Somers' d without an interval; Python has no gamma"
                                  if method == "somers" else "Python has no Goodman-Kruskal gamma", x=x, y=y),
                           dtype=float)
        value, low, high = (float(v) for v in found[:3])
        meaning = (f'of all pairs of rows that differ in "{column_a}", the share where "{column_b}" goes the same way '
                   "minus the share where it goes the other way" if method == "somers" else
                   "of all pairs of rows that differ in both columns, the share in the same order minus the share in "
                   "the opposite order (tied pairs left out)")
        verdict = ("the interval leaves out 0, so the data show a link" if low > 0 or high < 0 else
                   "the interval includes 0, so the data cannot tell whether there is a link")
        print(f'{METHOD_NAMES[method]} between "{column_a}" and "{column_b}" = {_num(value)} ({len(x)} rows; values '
              f"from {_num(low)} to {_num(high)} fit the data, 95 % CI): {verdict}.")
        r_name = 'SomersDelta(direction = "column")' if method == "somers" else "GoodmanKruskalGamma()"
        print(f"It is {meaning}. Method: R DescTools::{r_name}.")
        return value

    def _partial_correlation(self, step, frame, column_a, column_b, allowing_for, method):
        """The partial correlation of two columns allowing for a third, from R ppcor::pcor.test() (Python has none)."""
        from .._r import r_call

        names = [column_a, column_b, allowing_for]
        rows = frame.select(*names).drop_nulls()
        skipped = len(frame) - len(rows)
        if skipped:
            print(f"Note: {skipped} row{'' if skipped == 1 else 's'} with an empty cell in "
                  + " or ".join(f'"{n}"' for n in names) + f" {'was' if skipped == 1 else 'were'} skipped.")
        x, y, z = (rows[c].to_numpy().astype(float) for c in names)
        found = r_call("p <- ppcor::pcor.test(x, y, z, method = m); list(r = p$estimate, p = p$p.value, "
                       "stat = p$statistic)", packages=("ppcor",),
                       what="the partial correlation (R ppcor::pcor.test())",
                       python_note="SciPy and statsmodels have no partial correlation test", x=x, y=y, z=z, m=method)
        r, p = float(np.asarray(found["r"])[0]), float(np.asarray(found["p"])[0])
        # the correlation without allowing for it, on the same rows as the partial correlation
        whole = float(self._correlate(step, rows.select(column_a, column_b), column_a, column_b, method)[0])
        print(f'The correlation between "{column_a}" and "{column_b}", allowing for "{allowing_for}", is r = {r:.2f} '
              f"({METHOD_NAMES[method]}, {len(x)} rows): {_strength(r)}; without allowing for it, r = {whole:.2f}.")
        print(_p_sentence(p, f'there were truly no link once "{allowing_for}" is allowed for',
                          "a link this strong or stronger", "that there is no link"))
        print(f'Method: partial correlation, as R ppcor::pcor.test(method = "{method}"): the link that is left after '
              f'taking out what both columns share with "{allowing_for}". A correlation does not show that one thing '
              "causes the other.")
        return r

    def _covariance_table(self, step, frame, names):
        """find_correlation_between(show="covariance"): pandas DataFrame.cov() (n - 1, pairwise complete rows), as R
        cov(use = "pairwise.complete.obs")."""
        data = frame.select(*names).to_pandas().astype(float)
        cov = data.cov(ddof=1, min_periods=2)  # empty where a pair has fewer than 2 rows with both numbers
        few = [(a, b) for i, a in enumerate(names) for b in names[i:] if cov.isna().loc[a, b]]
        if few:
            a, b = few[0]
            pair = f'"{a}"' if a == b else f'"{a}" and "{b}"'
            raise SimplydataError(f"{step}() needs at least 2 rows where {pair} {'has' if a == b else 'both have'} a "
                                  "number for a covariance.")
        table = {"column": list(names)}
        for b in names:
            table[b] = [float(cov.loc[a, b]) for a in names]
        listed = "; ".join(f'"{a}" and "{b}": {_say_number(float(cov.loc[a, b]))}'
                           for i, a in enumerate(names) for b in names[i + 1:])
        print(f"Covariances between {len(names)} columns (each pair uses the rows where both columns have a number; "
              f"the diagonal is each column's variance): {listed}.")
        print("A covariance is in the units of the two columns multiplied, so its size depends on the units; the "
              "correlation (show=\"r\") is the same link without units, from -1 to 1.")
        print('Method: pandas DataFrame.cov() (divide by n - 1), as R cov(use = "pairwise.complete.obs"); R\'s '
              'default use = "everything" gives NA where a column has an empty cell.')
        gaps = len(frame) - len(frame.select(*names).drop_nulls())
        if gaps:
            print(f"Note: {gaps} row{'' if gaps == 1 else 's'} {'has' if gaps == 1 else 'have'} an empty cell in at "
                  "least one of these columns; each pair skipped only the rows it could not use.")
        return self._new_table(nw.from_dict(table, backend=self._frame.implementation))

    def _correlation_table(self, step, frame, names, method, shown):
        found = {}
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                found[(a, b)] = self._correlate(step, frame, a, b, method)
        method_name = METHOD_NAMES[method]
        if shown == "each pair":
            pairs = list(found.items())
            data = {"column 1": [a for (a, _), _ in pairs], "column 2": [b for (_, b), _ in pairs],
                    "method": [method_name] * len(pairs), "r": [v[0] for _, v in pairs],
                    "p-value": [v[1] for _, v in pairs], "rows": [v[2] for _, v in pairs],
                    "strength": [_strength(v[0]) for _, v in pairs]}
        else:
            index = 0 if shown == "r" else 1
            data = {"column": list(names)}
            for b in names:
                data[b] = [(1.0 if index == 0 else None) if a == b else found.get((a, b), found.get((b, a)))[index]
                           for a in names]
        result = self._new_table(nw.from_dict(data, backend=self._frame.implementation))
        n_pairs = len(found)
        strongest = sorted(found.items(), key=lambda item: -abs(round(item[1][0], 2)))
        print(f"Correlations between {len(names)} columns ({method_name}, {n_pairs} pairs; each pair uses the rows "
              "where both columns have a number). The strongest:")
        for (a, b), (r, p, n) in strongest[:STRONGEST_PAIRS]:
            print(f'  "{a}" and "{b}": r = {r:.2f} ({n} rows), {_strength(r)}; {_p_clause(p, "there were truly no link")}.')
        if n_pairs > STRONGEST_PAIRS:
            print(f"  ... and {n_pairs - STRONGEST_PAIRS} more pairs (the new table has them all).")
        gaps = len(frame) - len(frame.select(*names).drop_nulls())
        if gaps:
            print(f"Note: {gaps} row{'' if gaps == 1 else 's'} {'has' if gaps == 1 else 'have'} an empty cell in at "
                  "least one of these columns; each pair skipped only the rows it could not use.")
        listed = ", ".join(f'"{n}"' for n in names)
        print(f"Note: these p-values are not adjusted for testing {n_pairs} pairs. To adjust them: "
              f'results = table.find_correlation_between({listed}, show="each pair"), then '
              'results.add_adjusted_p_value_column(from_column="p-value").')
        return result
