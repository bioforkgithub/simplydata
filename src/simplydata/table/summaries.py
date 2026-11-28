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

from .._typing import _Same

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..numbers import Numbers

import datetime as _dt
import math

import narwhals as nw
import numpy as np

from .. import _zone_clock
from .._errors import SimplydataError, choice_error, friendly
from .._stats import _plain_name
from ._base import counted
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

CORRELATION_METHODS = ("pearson", "spearman", "kendall", "somers", "gamma",
                       # families for 100 %, batches 3-4 (approved by Manish 2026-11-28): SciPy chatterjeexi,
                       # weightedtau and multiscale_graphcorr
                       "chatterjee xi", "weighted kendall", "multiscale graph")
CORRELATION_ALIASES = {"chatterjeexi": "chatterjee xi", "xi": "chatterjee xi", "chatterjee": "chatterjee xi",
                       "weightedtau": "weighted kendall", "weighted tau": "weighted kendall",
                       "multiscale_graphcorr": "multiscale graph", "mgc": "multiscale graph",
                       "spearmanr": "spearman", "spearmanrho": "spearman", "pearsonr": "pearson",
                       "pointbiserialr": "pearson", "point-biserial": "pearson", "point biserial": "pearson",
                       "kendalltau": "kendall", "somersd": "somers"}
LINK_METHODS = ("chatterjee xi", "weighted kendall", "multiscale graph")  # two columns, SciPy's own test
SPEARMAN_EXACT_LIMIT = 1290  # R cor.test(method = "spearman"): AS 89 below 1290 rows without ties
SPEARMAN_NO_R = ("Note: Spearman's p-value is the t approximation (SciPy spearmanr); R cor.test() gives the p-value of "
                 "algorithm AS 89 for fewer than 1290 rows without ties, which needs R here: pip install "
                 '"simplydata[r]" and install R.')
SPEARMAN_AS89 = ("Spearman's p-value from algorithm AS 89 (Best and Roberts 1975), as R cor.test(method = "
                 '"spearman") gives it for fewer than 1290 rows without tied values, run in R.')


def _spearman_p_from_r(a, b, alternative, notes):
    """Spearman's p-value from R cor.test() (AS 89), or None without R (then the note goes into notes)."""
    from .._r import RMissing, r_call

    side = {"two-sided": "two.sided", "greater": "greater", "less": "less"}[alternative]
    try:
        found = r_call("stats::cor.test(x, y, method = 'spearman', alternative = side)$p.value", packages=(),
                       what="Spearman's p-value for fewer than 1290 rows (R cor.test(), algorithm AS 89)",
                       x=np.asarray(a, dtype=float), y=np.asarray(b, dtype=float), side=side)
    except RMissing:
        if notes is not None:
            notes.append(SPEARMAN_NO_R)
        return None
    if notes is not None:
        notes.append(SPEARMAN_AS89)
    return float(np.asarray(found)[0])
ORDINAL_METHODS = ("somers", "gamma") + LINK_METHODS  # two columns: the measure on its own, not a table
METHOD_NAMES = {"pearson": "Pearson", "spearman": "Spearman", "kendall": "Kendall's tau-b", "somers": "Somers' d",
                "gamma": "Goodman and Kruskal's gamma", "chatterjee xi": "Chatterjee's xi",
                "weighted kendall": "the weighted Kendall's tau",
                "multiscale graph": "the multiscale graph correlation"}
CORRELATION_SHOW = ("r", "p-value", "each pair", "covariance", "result table")
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
            "trimmed average", "most common", "percentile", "harmonic mean", "winsorised average",
            "first", "last",  # first, last: tables phase, batch 3
            # families for 100 %, batches 1-2 (approved by Manish 2026-11-28): pandas prod(), Polars entropy() and
            # the text of each group joined into one cell (pandas groupby().agg("; ".join), Polars str.join)
            "product", "entropy", "joined text",
            # families for 100 %, batches 3-4 (approved by Manish 2026-11-28): the scipy.stats summaries (gstd, pmean,
            # kstat, kstatvar, lmoment, moment, expectile, tmean ..., circmean ..., differential_entropy,
            # estimated_cdf, percentileofscore, sigmaclip); the ones with a number are written with it ("power mean 3")
            "geometric standard deviation", "circular average", "circular standard deviation", "circular variance",
            "differential entropy", "power mean", "cumulant", "cumulant variance", "l-moment", "l-skewness",
            "l-kurtosis", "central moment",
            "expectile", "percentile rank", "percent at or below", "sigma-clipped average",
            # with in_bins_of= only: the counts of the bins added up (cumfreq) and each bin's share (relfreq)
            "running count", "share of values")
# families for 100 %, batches 3-4: the measures written with a number, as "percentile 90" ("power mean 3", "cumulant 2",
# "average between 40 and 80" ...), read by _numbered_measure
NUMBERED_MEASURES = ("power mean", "cumulant", "cumulant variance", "l-moment", "central moment", "expectile",
                     "percentile rank", "percent at or below")
BETWEEN_MEASURES = {"average": "tmean", "standard deviation": "tstd", "variance": "tvar", "standard error": "tsem"}
SIGMA_CLIP = 4.0  # "sigma-clipped average": values more than 4 standard deviations out are cut, again and again (SciPy)
BIN_MEASURES = ("running count", "share of values")  # only with in_bins_of=
# "first" and "last": the first and last filled value in the order of the rows (pandas groupby().first() / last(),
# which skip empty cells; Polars drop_nulls().first() / last()); not a NumPy measure, not one of _measure_values
FIRST_LAST = ("first", "last")
MEASURE_ALIASES = {"mean": "average", "sum": "total", "sd": "standard deviation", "se": "standard error",
                   "ci": "confidence interval", "iqr": "interquartile range", "geometric average": "geometric mean",
                   "gmean": "geometric mean", "skew": "skewness", "cv": "coefficient of variation",
                   "mad": "median absolute deviation", "trimmed mean": "trimmed average", "mode": "most common",
                   "quantile": "percentile", "harmonic average": "harmonic mean", "hmean": "harmonic mean",
                   "winsorized average": "winsorised average", "winsorized mean": "winsorised average",
                   "winsorised mean": "winsorised average", "prod": "product", "shannon entropy": "entropy",
                   "implode": "joined text", "joined": "joined text",
                   # families for 100 %, batches 3-4: SciPy's names of the new measures
                   "gstd": "geometric standard deviation", "geometric sd": "geometric standard deviation",
                   "circmean": "circular average", "circular mean": "circular average",
                   "circstd": "circular standard deviation", "circvar": "circular variance",
                   "differential_entropy": "differential entropy", "sigmaclip": "sigma-clipped average",
                   "sigma clipped average": "sigma-clipped average", "cumfreq": "running count",
                   "cumulative count": "running count", "relfreq": "share of values",
                   "relative frequency": "share of values"}
# measures worked out with NumPy / SciPy on each group's numbers (the others come from narwhals)
ARRAY_MEASURES = ("geometric mean", "skewness", "kurtosis", "coefficient of variation", "median absolute deviation",
                  "trimmed average", "most common", "percentile", "harmonic mean", "winsorised average",
                  "product", "entropy",
                  # families for 100 %, batches 3-4
                  "geometric standard deviation", "circular average", "circular standard deviation",
                  "circular variance", "differential entropy", "sigma-clipped average", "l-skewness", "l-kurtosis")
# the beginnings of the measures written with numbers ("power mean 3", "circular average in degrees" ...)
ARRAY_PREFIXES = ("percentile ", "trimmed average ", "winsorised average ", "power mean ", "cumulant ",
                  "l-moment ", "central moment ", "expectile ", "percent at or below ",
                  "average between ", "standard deviation between ", "variance between ", "standard error between ",
                  "smallest from ", "biggest up to ", "circular average ", "circular standard deviation ",
                  "circular variance ", "sigma-clipped average ", "l-skewness", "l-kurtosis")
TEXT_SEPARATOR = "; "  # show="joined text": what goes between the texts of a group, unless separator= says
TRIM_PERCENT = 10  # "trimmed average": 10 % cut from each end, unless another percent is given
WINSOR_PERCENT = 20  # "winsorised average": 20 % pulled in at each end (R WRS2::winmean(tr = 0.2))
MAD_CONSTANT = 1.4826  # R mad(): makes the median absolute deviation match the sd for bell-shaped values
LEAST_VALUES = {"skewness": 3, "kurtosis": 4}  # fewer values than this give an empty cell
DEFAULT_MEASURES = ("count", "average", "standard deviation", "smallest", "median", "biggest")
SUMMARY_LINES = 12  # find_summary_of prints at most this many rows; the table has them all


# lower edge of each band, biggest first
STRENGTH_WORDS = ((0.8, "very strong"), (0.6, "strong"), (0.4, "medium"), (0.2, "weak"), (0.0, "very weak"))


def _truncated(frame, column, code):
    """narwhals dt.truncate(code) of a date column, the start of its hour, day, month, quarter or year.

    A pandas column with a time zone is truncated by Polars dt.truncate and comes back as pandas: narwhals
    truncates pandas months, quarters and years on the UTC clock (through NumPy datetime64), so 1 July 00:00
    in Oslo (30 June 22:00 UTC) fell in June, while Polars uses the column's own clock. A column with a time zone
    is truncated by Polars on both engines (code "1w" too: the Monday of the week), so its local clock follows the
    main world time zone data (IANA), the same on every computer (simplydata._zone_clock).
    """
    dtype = frame.schema[column]
    if not (dtype == nw.Datetime and dtype.time_zone):
        return nw.col(column).dt.truncate(code)
    import polars as pl

    native = frame[column].to_native()
    if frame.implementation.is_polars():
        return nw.from_native(native.dt.truncate(code), series_only=True).alias(column)
    start = pl.from_pandas(native).dt.truncate(code).to_pandas().astype(native.dtype)
    start.index = native.index
    return nw.from_native(start, series_only=True).alias(column)


def _on_one_clock(frame, position, column):
    """frame.rows(), with the cells of column (at position) read on Polars' clock when it has a time zone, so the
    column names of a cross table are the same on both engines (simplydata._zone_clock)."""
    rows = frame.rows()
    if not _zone_clock.on_pandas_with_zone(frame, [column]):
        return rows
    return [(*r[:position], v, *r[position + 1:]) for r, v in zip(rows, _zone_clock.values(frame, column))]


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
# find_interval_of(test_method="bayesian"): families for 100 %, batches 3-4; the summary -> its place in bayes_mvs
BAYES_SUMMARIES = {"average": 0, "variance": 1, "standard deviation": 2}
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
    """find_percentile_of(test_method=): R's type number (1 to 9) or NumPy's name, as the NumPy name."""
    if isinstance(method, (int, np.integer)) and not isinstance(method, bool) and 1 <= method <= 9:
        return PERCENTILE_RULES[int(method) - 1]
    if isinstance(method, str) and method.strip() in [str(n) for n in range(1, 10)]:  # R's type as text, "8"
        return PERCENTILE_RULES[int(method.strip()) - 1]
    if isinstance(method, str) and method.strip().lower().replace(" ", "_") in PERCENTILE_RULES:
        return method.strip().lower().replace(" ", "_")
    raise choice_error(step, "test_method", method, [r.replace("_", " ") for r in PERCENTILE_RULES]
                       + [str(n) for n in range(1, 10)])


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
    found = _numbered_measure(name)
    if found:
        return found
    name = MEASURE_ALIASES.get(name, name)
    if name in NUMBERED_MEASURES:
        raise SimplydataError(f'show="{name}" needs a number after it, for example "{_NUMBER_EXAMPLES[name]}".\n'
                              f'For example:  table.{step}("marks", show=["{_NUMBER_EXAMPLES[name]}"])')
    if name == "percentile":
        raise SimplydataError(f'show="percentile" needs the percent, for example "percentile 90".\nFor example:  {example}')
    if name not in MEASURES:
        raise choice_error(step, "show", item, list(MEASURES))
    return name


_NUMBER = r"(-?\d+(?:\.\d+)?)"
_NUMBER_EXAMPLES = {"power mean": "power mean 3", "cumulant": "cumulant 2", "cumulant variance": "cumulant variance 2",
                    "l-moment": "l-moment 2", "central moment": "central moment 3", "expectile": "expectile 90",
                    "percentile rank": "percentile rank 70", "percent at or below": "percent at or below 70"}
_SCIPY_NUMBERED = {"pmean": "power mean", "kstat": "cumulant", "kstatvar": "cumulant variance",
                   "lmoment": "l-moment", "moment": "central moment", "percentileofscore": "percent at or below",
                   "estimated_cdf": "percentile rank"}


def _numbered_measure(name: str):
    """Families for 100 %, batches 3-4: the scipy.stats measures written with a number: "power mean 3" (pmean),
    "cumulant 2" (kstat), "cumulant variance 2" (kstatvar), "l-moment 2" (lmoment), "central moment 3" (moment),
    "expectile 90" (expectile, in percent), "percentile rank 70" (estimated_cdf), "percent at or below 70"
    (percentileofscore), "average between 40 and 80" (tmean; tstd, tvar, tsem the same), "smallest from 40" (tmin),
    "biggest up to 80" (tmax), "circular average in degrees" (circmean; circstd, circvar) and "sigma-clipped average 3"
    (sigmaclip). None when the name is none of them."""
    import re

    words = name.split()
    if len(words) == 2 and words[0] in _SCIPY_NUMBERED:  # SciPy's own name with the number: "pmean 3", "kstat 2"
        name = f"{_SCIPY_NUMBERED[words[0]]} {words[1]}"
    found = re.fullmatch(r"(power mean|power average|cumulant variance|cumulant|l-moment|l moment|central moment|"
                         r"expectile|percentile rank|percent at or below)\s+" + _NUMBER, name)
    if found:
        kind = {"power average": "power mean", "l moment": "l-moment"}.get(found.group(1), found.group(1))
        number = float(found.group(2))
        if kind in ("cumulant", "cumulant variance", "l-moment", "central moment"):
            top = {"cumulant": 4, "cumulant variance": 2}.get(kind)
            if not number.is_integer() or number < 1 or (top and number > top):
                limit = f"from 1 to {top}" if top else "of 1 or more"
                raise SimplydataError(f'"{kind}" needs a whole number {limit}, not {number:g}.\nFor example:  '
                                      f'table.find_summary_of("marks", show=["{_NUMBER_EXAMPLES[kind]}"])')
        if kind == "expectile" and not 0 < number < 100:
            raise SimplydataError(f"An expectile is written in percent, above 0 and below 100 (not {number:g}).\n"
                                  'For example:  table.find_summary_of("marks", show=["expectile 90"])')
        if kind == "power mean" and number == 0:
            raise SimplydataError('"power mean 0" is the geometric mean: show=["geometric mean"].')
        return f"{kind} {number:g}"
    found = re.fullmatch(r"(average|mean|standard deviation|variance|standard error)\s+between\s+" + _NUMBER
                         + r"\s+and\s+" + _NUMBER, name)
    if found:
        kind = "average" if found.group(1) == "mean" else found.group(1)
        low, high = float(found.group(2)), float(found.group(3))
        if low >= high:
            raise SimplydataError(f'"{name}" needs the lower limit first, then a higher one, like '
                                  f'"{kind} between {min(low, high):g} and {max(low, high) + (low == high):g}".')
        return f"{kind} between {low:g} and {high:g}"
    found = re.fullmatch(r"(smallest from|biggest up to)\s+" + _NUMBER, name)
    if found:
        return f"{found.group(1)} {float(found.group(2)):g}"
    found = re.fullmatch(r"(circular average|circular mean|circular standard deviation|circular variance|circmean|"
                         r"circstd|circvar)\s+in\s+(degrees|radians|hours)", name)
    if found:
        kind = {"circular mean": "circular average", "circmean": "circular average",
                "circstd": "circular standard deviation", "circvar": "circular variance"}.get(found.group(1),
                                                                                           found.group(1))
        return f"{kind} in {found.group(2)}"
    if name in ("circular average", "circular mean", "circular standard deviation", "circular variance",
                "circmean", "circstd", "circvar"):
        plain = {"circular mean": "circular average", "circmean": "circular average",
                 "circstd": "circular standard deviation", "circvar": "circular variance"}.get(name, name)
        raise SimplydataError(f'show="{plain}" needs the unit of the angles, as find_average_direction_of needs '
                              f'full_turn=: "{plain} in degrees" (a full turn is 360), "{plain} in radians" (2 pi) or '
                              f'"{plain} in hours" (24, times of day).\nFor example:  table.find_summary_of('
                              f'"wind_direction", show=["{plain} in degrees"])   (with sdata.get_example("weather"))')
    found = re.fullmatch(r"sigma[- ]clipped (?:average|mean)\s+" + _NUMBER, name)
    if found:
        if float(found.group(1)) <= 0:
            raise SimplydataError(f'"{name}" needs a number of standard deviations above 0, like "sigma-clipped '
                                  'average 3".')
        return f"sigma-clipped average {float(found.group(1)):g}"
    return None


def _is_array_measure(name) -> bool:
    return isinstance(name, str) and (name in ARRAY_MEASURES or name.startswith(ARRAY_PREFIXES)
                                      or name.startswith("percentile rank "))


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
      product                   every value multiplied together (NumPy prod, as pandas prod(),
                                Polars product() and R prod())
      entropy                   Shannon entropy -sum(p * log(p)), with p each value's share of the
                                total and the natural log (SciPy entropy, as Polars entropy())
    """
    from scipy import stats

    n = len(values)
    if n == 0:
        return None, None, None
    if name in ARRAY_MEASURES[12:] or name.startswith(ARRAY_PREFIXES[3:]) or name.startswith("percentile rank "):
        return _scipy_measure(name, values)
    if name == "geometric mean":
        if (values <= 0).any():
            return None, "needs numbers above 0", None
        return float(stats.gmean(values)), None, None
    if name == "harmonic mean":
        if (values <= 0).any():
            return None, "needs numbers above 0", None
        return float(stats.hmean(values)), None, None
    if name == "product":  # NumPy prod, as pandas prod() and Polars product()
        return float(np.prod(values)), None, None
    if name == "entropy":  # SciPy entropy (natural log, the numbers shared out to 1), as Polars entropy()
        if (values < 0).any():
            return None, "needs numbers of 0 or more", None
        if values.sum() == 0:
            return None, "needs numbers that add up to more than 0", None
        return float(stats.entropy(values)), None, None
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


def _scipy_measure(name: str, values):
    """Families for 100 %, batches 3-4: one group's value of a scipy.stats summary (value, why it is empty, None).

      geometric standard deviation  exp(sd(log(x))), sd with n - 1 (SciPy gstd); numbers above 0
      power mean p                   (mean(x ** p)) ** (1 / p) (SciPy pmean); numbers above 0
      cumulant k                     the unbiased estimate of the k-th cumulant, k = 1 to 4 (SciPy kstat)
      cumulant variance k            the unbiased estimate of its variance, k = 1 or 2 (SciPy kstatvar)
      l-moment k                     the k-th sample L-moment lambda_k (SciPy lmoment(standardize=False))
      l-skewness, l-kurtosis         the L-moment ratios tau_3 = lambda_3 / lambda_2 and tau_4 = lambda_4 /
                                     lambda_2 (SciPy lmoment, as R lmom::samlmu gives them)
      central moment k               mean((x - mean(x)) ** k), divided by n (SciPy moment)
      expectile p                    the value t where p % of the squared distances lie below (SciPy expectile,
                                     alpha = p / 100); expectile 50 is the average
      average between a and b        the average of the values from a to b, both included (SciPy tmean); the
                                     standard deviation, variance and standard error the same, with n - 1
                                     (tstd, tvar, tsem)
      smallest from a / biggest up to b   SciPy tmin(lowerlimit=a) / tmax(upperlimit=b)
      circular average ...           angles "in degrees" (a full turn 360), "in radians" (2 pi) or "in hours" (24)
                                     (SciPy circmean, circstd, circvar); the average and standard deviation are in
                                     that unit, the circular variance (1 minus the mean resultant length) has none
      differential entropy           the entropy of the density the values come from, in nats (natural log; SciPy
                                     differential_entropy: van Es's estimate up to 10 values, Ebrahimi's from 11
                                     to 1000, Vasicek's above)
      percentile rank v              the percent p at which the usual percentile rule (R type 7, a straight line
                                     between the sorted values) gives v: the inverse of "percentile p" (SciPy
                                     estimated_cdf, times 100); not the plain share below v ("percent at or below v")
      percent at or below v          the percent of the values at or below v (SciPy percentileofscore(kind="weak"))
      sigma-clipped average k        the average after values more than k standard deviations out are cut, again
                                     until none is (SciPy sigmaclip(low=k, high=k), k = 4 unless written)
    """
    import math

    from scipy import stats

    n = len(values)
    words = name.split()
    number = None
    try:
        number = float(words[-1])
    except ValueError:
        pass
    if name == "geometric standard deviation" or name.startswith("power mean "):
        if (values <= 0).any():
            return None, "needs numbers above 0", None
    if name == "geometric standard deviation":
        if n < 2:
            return None, "needs at least 2 values", None
        return float(stats.gstd(values)), None, None
    if name.startswith("power mean "):
        return float(stats.pmean(values, number)), None, None
    if name.startswith("cumulant variance "):
        if n < 2:
            return None, "needs at least 2 values", None
        return float(stats.kstatvar(values, int(number))), None, None
    if name.startswith("cumulant "):
        if n < int(number):
            return None, f"needs at least {int(number)} values", None
        return float(stats.kstat(values, int(number))), None, None
    if name.startswith("l-moment "):
        if n < int(number):
            return None, f"needs at least {int(number)} values", None
        return float(stats.lmoment(values, order=int(number), standardize=False)), None, None
    if name in ("l-skewness", "l-kurtosis"):
        order = 3 if name == "l-skewness" else 4
        if n < order or np.ptp(values) == 0:
            return None, f"needs at least {order} values that differ", None
        return float(stats.lmoment(values, order=order)), None, None
    if name.startswith("central moment "):
        return float(stats.moment(values, order=int(number))), None, None
    if name.startswith("expectile "):
        return float(stats.expectile(values, alpha=number / 100)), None, None
    if " between " in name:
        kind = name.split(" between ")[0]
        low, high = float(words[-3]), float(words[-1])
        inside = values[(values >= low) & (values <= high)]
        least = 1 if kind == "average" else 2
        if len(inside) < least:
            return None, f"needs at least {least} values between {low:g} and {high:g}", None
        function = getattr(stats, BETWEEN_MEASURES[kind])
        extra = {} if kind == "average" else {"ddof": 1}
        return float(function(values, (low, high), **extra)), None, None
    if name.startswith("smallest from "):
        if not (values >= number).any():
            return None, f"has no value of {number:g} or more", None
        return float(stats.tmin(values, lowerlimit=number)), None, None
    if name.startswith("biggest up to "):
        if not (values <= number).any():
            return None, f"has no value of {number:g} or less", None
        return float(stats.tmax(values, upperlimit=number)), None, None
    if name.startswith("circular "):
        kind, unit = name.split(" in ")
        high = {"degrees": 360.0, "radians": 2 * math.pi, "hours": 24.0}[unit]
        function = {"circular average": stats.circmean, "circular standard deviation": stats.circstd,
                    "circular variance": stats.circvar}[kind]
        return float(function(values, high=high, low=0.0)), None, None
    if name == "differential entropy":
        if n < 2 or np.ptp(values) == 0:
            return None, "needs at least 2 values that differ", None
        import warnings

        with warnings.catch_warnings():  # SciPy warns and gives NaN when the window is too small for the values
            warnings.simplefilter("ignore")
            found = float(stats.differential_entropy(values))
        if math.isnan(found):
            return None, "needs more values (SciPy's estimate needs a window of values)", None
        return found, None, None
    if name.startswith("percentile rank "):
        if not hasattr(stats, "estimated_cdf"):
            import scipy

            raise SimplydataError(f'show="{name}" needs SciPy 1.18 or newer (this computer has SciPy '
                                  f"{scipy.__version__}): pip install --upgrade scipy. SciPy 1.18 needs Python 3.12 or "
                                  'newer. "percent at or below v" works with every SciPy.')
        return float(stats.estimated_cdf(values, number)) * 100, None, None
    if name.startswith("percent at or below "):
        return float(stats.percentileofscore(values, number, kind="weak")), None, None
    if name.startswith("sigma-clipped average"):
        k = number if number is not None else SIGMA_CLIP
        kept = stats.sigmaclip(values, low=k, high=k).clipped
        return float(np.mean(kept)), None, None
    raise SimplydataError(f'find_summary_of() does not know the measure "{name}".')


def _bin_edges(step, name, how, x, example):
    """in_bins_of={"depth": 10}: edges 10 apart from the multiple of 10 at or below the smallest value to the first at
    or above the biggest; {"depth": [0, 10, 50]}: those edges."""
    if isinstance(how, (list, tuple, np.ndarray)):
        edges = np.asarray(how, dtype=float)
        if len(edges) < 2 or not np.all(np.isfinite(edges)) or not np.all(np.diff(edges) > 0):
            raise SimplydataError(f'in_bins_of= for "{name}" needs at least 2 edges, each bigger than the one before, '
                                  f"like [0, 10, 50, 100].\nFor example:  {example}")
        return edges
    if isinstance(how, bool) or not isinstance(how, (int, float, np.integer, np.floating)) or not how > 0 or (
            not math.isfinite(how)):
        raise SimplydataError(f'in_bins_of= for "{name}" needs how wide each bin is (a number above 0) or a list of '
                              f"edges.\nFor example:  {example}")
    filled = x[~np.isnan(x)]
    if len(filled) == 0:
        raise SimplydataError(f'"{name}" has no numbers to cut into bins.')
    from decimal import Decimal

    width = float(how)
    decimals = max(0, -Decimal(repr(width)).normalize().as_tuple().exponent)
    tiny = 1e-9 * width  # a value a hair below a multiple of the width (3.9 / 0.1 = 38.999...) is on it
    start = round(math.floor(filled.min() / width + 1e-9) * width, decimals)
    count = max(1, math.ceil((filled.max() - start) / width - 1e-9))
    if start + count * width < filled.max() - tiny:
        count += 1
    if count > 100_000:
        raise SimplydataError(f'in_bins_of={{"{name}": {how:g}}} makes {count} bins; give wider bins.')
    return np.round(start + width * np.arange(count + 1), decimals)  # edges written with the width's decimals


def _add_bin_measures(result, columns, groups, key, extra, keep_count):
    """show=["running count"] and ["share of values"] with in_bins_of=: the counts of the bins added up in the order of
    the bins (SciPy cumfreq) and each bin's share of the values (relfreq), within each column and group."""
    frame = result._frame
    rows = frame.rows(named=True)
    running, share = [], []
    totals: dict = {}
    for row in rows:
        part = (row["column"], *[row[g] for g in groups])
        totals[part] = totals.get(part, 0) + int(row["count"] or 0)
    seen: dict = {}
    for row in rows:
        part = (row["column"], *[row[g] for g in groups])
        seen[part] = seen.get(part, 0) + int(row["count"] or 0)
        running.append(seen[part])
        share.append(int(row["count"] or 0) / totals[part] if totals[part] else None)
    added = []
    if "running count" in extra:
        added.append(nw.new_series("running count", running, nw.Int64, backend=frame.implementation))
    if "share of values" in extra:
        added.append(nw.new_series("share of values", share, nw.Float64, backend=frame.implementation))
    frame = frame.with_columns(*added)
    if not keep_count:
        frame = frame.drop("count")
    del columns, key
    return result._new_table(frame)


def _method_line(name: str) -> str:
    """The method of a scipy.stats measure of the families for 100 % (one line printed after the summary)."""
    words = name.split()
    lines = [
        ("geometric standard deviation", "exp of the standard deviation of the logs, n - 1 (SciPy gstd)"),
        ("power mean ", "(average of x ** p) ** (1 / p) (SciPy pmean)"),
        ("cumulant variance ", "the unbiased estimate of the variance of the k-statistic (SciPy kstatvar)"),
        ("cumulant ", "the k-statistic, the unbiased estimate of the cumulant (SciPy kstat)"),
        ("l-moment ", "the sample L-moment lambda_k (SciPy lmoment(standardize=False))"),
        ("l-skewness", "the L-moment ratio tau_3 = lambda_3 / lambda_2 (SciPy lmoment, as R lmom::samlmu)"),
        ("l-kurtosis", "the L-moment ratio tau_4 = lambda_4 / lambda_2 (SciPy lmoment, as R lmom::samlmu)"),
        ("central moment ", "the average of (x - average) ** k, divided by n (SciPy moment)"),
        ("expectile ", "the value where the squared distances above and below balance at that percent (SciPy "
                       "expectile)"),
        ("average between ", "only the values between the limits, both included (SciPy tmean; tstd, tvar, tsem with "
                             "n - 1)"),
        ("standard deviation between ", "only the values between the limits, both included, n - 1 (SciPy tstd)"),
        ("variance between ", "only the values between the limits, both included, n - 1 (SciPy tvar)"),
        ("standard error between ", "only the values between the limits, both included, n - 1 (SciPy tsem)"),
        ("smallest from ", "the smallest value at or above the limit (SciPy tmin)"),
        ("biggest up to ", "the biggest value at or below the limit (SciPy tmax)"),
        ("circular variance ", "1 minus the mean resultant length, from 0 to 1, with no unit (SciPy circvar)"),
        ("circular ", "angles on a circle (SciPy circmean, circstd), the answer in "
                      + (words[-1] if len(words) > 1 else "") + ", from 0 to a full turn for the average"),
        ("differential entropy", "in nats (natural log), SciPy differential_entropy (van Es up to 10 values, "
                                 "Ebrahimi from 11 to 1000, Vasicek above)"),
        ("percentile rank ", "the percent at which the usual percentile rule (R type 7) gives the value: the inverse "
                             "of \"percentile p\" (SciPy estimated_cdf)"),
        ("percent at or below ", "the share of the values at or below the value, in percent (SciPy "
                                 "percentileofscore(kind=\"weak\"))"),
        ("sigma-clipped average", "values more than k standard deviations (4 unless written) from the average cut "
                                  "again and again, then the average (SciPy sigmaclip)"),
    ]
    for start, line in lines:
        if name.startswith(start):
            return f'Method of "{name}": {line}.'
    return ""


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


# with_totals=True: the name of the total row and column, in the style of "(empty)"
TOTAL = "(total)"


def _check_with_totals(step, with_totals, across, every, in_percent=False):
    """with_totals= (tables phase, batch 2) goes with across= only: it adds a total row and column to a cross table."""
    if not isinstance(with_totals, bool):
        raise SimplydataError("with_totals= should be True or False.")
    if not with_totals:
        return
    example = (f'table.{step}(for_each_group_in="shop", across="fruit", with_totals=True)' if step == "count_rows" else
               f'table.{step}("count", for_each_group_in="shop", across="fruit", with_totals=True)')
    if across is None:
        raise SimplydataError("with_totals=True adds a total row and a total column to a cross table, so it goes with "
                              f'across=.\nFor example:  {example}   (with sdata.get_example("fruit"))')
    if every is not None or in_percent:
        raise SimplydataError("with_totals=True does not go with every= or in_percent=True; leave one of them out.")


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
            if name == "week" and schema[g] == nw.Datetime and schema[g].time_zone:
                # the Monday on the column's own clock: Polars dt.truncate("1w") on both engines (_zone_clock)
                frame = frame.with_columns(_truncated(frame, g, "1w"))
            elif name == "week":
                values = [None if _missing(v) else _week_start(v) for v in frame[g].to_list()]
                frame = frame.with_columns(
                    nw.new_series(g, values, schema[g], backend=frame.implementation))
            elif schema[g] == nw.Date and name == "hour":
                continue  # a date has no hours: each day stays as it is
            else:
                frame = frame.with_columns(_truncated(frame, g, EVERY[name]))
        return frame, {g: name for g in dates}

    def _cross(self, frame, groups: list[str], across: str, expr, fill=None, periods=None, with_totals=False):
        """A cross table: one row per group, one column per value of across=, expr in each cell.

        with_totals=True adds a "(total)" column (expr over each row's group) and a "(total)" row (expr over each
        across= value, and over every row in its last cell), named in the style of "(empty)". As pandas
        crosstab(margins=True) and pivot_table(margins=True), each total is worked out from the rows themselves
        (group_by().agg()), not from the cells, so the total average is the average of all the rows. Unlike pandas,
        rows with an empty group or across= value stay in the table (as "(empty)") and so count in the totals;
        pandas leaves them out of the table and its margins."""
        long = frame.group_by([*groups, across], drop_null_keys=False).agg(expr.alias("__value"))
        rows = _on_one_clock(long.select(*groups, across, "__value"), len(groups), across)
        row_keys = sorted({_key(r[:-2]) for r in rows}, key=lambda k: tuple(_order(v) for v in k))
        col_keys = sorted({_key(r[-2:-1])[0] for r in rows}, key=_order)
        cells = {(_key(r[:-2]), _key(r[-2:-1])[0]): _plain(r[-1]) for r in rows}
        data = {g: [k[i] for k in row_keys] for i, g in enumerate(groups)}
        for c in col_keys:
            label = _say_label(c, (periods or {}).get(across))
            if label in data:
                label = f"{across} {label}"
            data[label] = [cells.get((k, c), fill) for k in row_keys]
        if with_totals:
            labels = [c for c in data if c not in groups]
            first = data[groups[0]] if groups else []
            if TOTAL in labels or TOTAL in groups or any(str(v) == TOTAL for v in first if v is not None):
                raise SimplydataError(f'with_totals=True adds a row and a column called "{TOTAL}", and the table '
                                      f'already holds the value "{TOTAL}". Rename that value first, for example '
                                      f'table.replace_values_in("{across}", "{TOTAL}", with_value="total (typed)").')
            by_row = {_key(r[:-1]): _plain(r[-1]) for r in frame.group_by(groups, drop_null_keys=False)
                      .agg(expr.alias("__value")).select(*groups, "__value").rows()}
            by_column = {_key(r[:1])[0]: _plain(r[1]) for r in _on_one_clock(
                frame.group_by([across], drop_null_keys=False).agg(expr.alias("__value")).select(across, "__value"),
                0, across)}
            everything = _plain(frame.select(expr.alias("__value")).item())
            data[TOTAL] = [by_row.get(k, fill) for k in row_keys]
            for i, g in enumerate(groups):  # the total row: "(total)" in the first group column, text from here on
                values = data[g]
                if not all(v is None or isinstance(v, str) for v in values):
                    values = [None if v is None else str(_say_label(v, (periods or {}).get(g))) for v in values]
                data[g] = values + ([TOTAL] if i == 0 else [None])
            for c, label in zip(col_keys, labels):
                data[label].append(by_column.get(c, fill))
            data[TOTAL].append(everything)
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

    def _summary(self, step: str, column, for_each, every=None, across=None, measure=None, with_totals=False):
        """measure=(start of the column name, calculation, words for sentences) for words not in _SUMMARIES."""
        start, make = _SUMMARIES[step] if measure is None else measure[:2]
        said = start if measure is None else measure[2]
        columns = _as_list(step, "the column", column)
        _check_with_totals(step, with_totals, across, every)
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
            result, labels = self._cross(frame, groups, across, make(columns[0]), periods=periods,
                                         with_totals=with_totals)
            self._note_empty(frame, columns)
            print(f'The {said} of "{columns[0]}" for each {_each(groups, periods)} (rows) and each "{across}" '
                  f"(columns): a new table with {counted(len(result), 'row')} and {counted(len(labels), 'column')} "
                  "of numbers.")
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
                                                                 "quantile_test, Thompson's interval"
                                                                 + (', as R DescTools::MedianCI(method = "exact"))'
                                                                    if kind == "median" or share == 0.5 else
                                                                    ", which splits the chance of missing evenly "
                                                                    "between the two ends; R DescTools::QuantileCI("
                                                                    "method = \"exact\") "
                                                                    "picks another pair of values, so the ends can "
                                                                    "differ)"))
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

    @friendly(renamed={"method": "test_method", "for_each": "for_each_group_in", "seed": "with_seed"})
    def find_interval_of(self: _Same, column=None, summary="average", for_each_group_in=None, interval=95, test_method="bootstrap",
                         resamples=9999, with_seed=1) -> _Same:
        """A confidence interval for any summary, from the bootstrap.

        table.find_interval_of("marks", "median", for_each_group_in="class")   (with sdata.get_example("marks"), one subject)
        One subject (table.keep_rows_where("subject", is_equal_to="Maths")) gives one row per child: each
        child is in the marks table three times, and a test needs rows that are independent.
        summary= is any one-number measure of find_summary_of() ("average", "median", "standard
        deviation", "trimmed average 20", "percentile 90", "coefficient of variation", ...) or a
        function of your own that gets the numbers (a NumPy array) and gives back one number.
        The bootstrap draws the rows again at random, with replacement, resamples=9999 times
        (with_seed=1, printed; the same seed gives the same interval) and works out the summary each
        time; SciPy stats.bootstrap, as R boot::boot.ci(). test_method="bootstrap" is the
        bias-corrected and accelerated (BCa) interval, the usual choice; "percentile bootstrap"
        and "reverse percentile bootstrap" (R's "basic") are the other two. With fewer than 20
        values a note says the interval is often too narrow. Gives back one row per group: the
        summary, the interval and the count.
        test_method="bayesian" (families for 100 %) gives the Bayesian credible interval of the "average",
        "variance" or "standard deviation" with the usual uninformative prior (SciPy bayes_mvs, Oliphant 2006): no
        resampling, the interval comes from the t (average) or inverse gamma (variance) distribution of the values.
        """
        from .resampling import bootstrap_interval

        step = "find_interval_of"
        example = 'table.find_interval_of("marks", "median", for_each_group_in="class")   (with sdata.get_example("marks"))'
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs one column name in quotes, then the summary.\nFor example:  {example}")
        level = _check_percent(step, interval, "interval", example)
        if not 50 <= level < 100:
            raise SimplydataError(f"interval= is the level in percent, such as interval=95 (it is {level:g}).")
        if test_method == "jackknife":
            raise SimplydataError("A jackknife interval is not offered: no established package gives one (R "
                                  "bootstrap::jackknife() gives only the standard error and the bias). Use "
                                  'test_method="bootstrap".')
        if test_method in OLD_BOOTSTRAP_KINDS:
            from .._errors import renamed_note

            renamed_note(f'test_method="{test_method}"', f'test_method="{OLD_BOOTSTRAP_KINDS[test_method]}"')
            test_method = OLD_BOOTSTRAP_KINDS[test_method]
        if test_method == "bayesian":
            return self._bayesian_interval(step, column, summary, for_each_group_in, level, example)
        self._check_choice(step, "test_method", test_method, tuple(BOOTSTRAP_KINDS) + ("bayesian",))
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
                                                        BOOTSTRAP_KINDS[test_method], resamples, with_seed, vectorized=False)
            notes.add(note)
            if math.isnan(low) or math.isnan(high):
                notes.add(f'Note: the {test_method} interval could not be worked out for '
                          f'{" / ".join(_say_label(v) for v in key) or "the column"} (SciPy says the resampled '
                          'summaries take too few different values); try test_method="percentile bootstrap".')
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

    def _bayesian_interval(self, step, column, summary, for_each_group_in, level, example):
        """find_interval_of(test_method="bayesian"): SciPy bayes_mvs (Jeffreys' prior), for the average, the variance
        or the standard deviation; the middle of the interval is SciPy's estimate (the posterior mean)."""
        from scipy import stats

        label = _measure_name(step, summary) if isinstance(summary, str) else None
        if label not in BAYES_SUMMARIES:
            raise SimplydataError('test_method="bayesian" gives the interval of the "average", the "variance" or the '
                                  f'"standard deviation".\nFor example:  table.{step}("marks", "average", '
                                  'test_method="bayesian")')
        groups = self._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else []
        frame = self._number_frame(step, [column])
        self._note_empty(frame, [column])
        rows = []
        for key, x in self._group_arrays(frame, groups, column).items():
            if len(x) < 2 or np.ptp(x) == 0:
                raise SimplydataError(f"{step}() needs at least 2 different numbers in each group.")
            found = stats.bayes_mvs(x, alpha=level / 100)[BAYES_SUMMARIES[label]]
            rows.append(list(key) + [float(found.statistic), float(found.minmax[0]), float(found.minmax[1]), len(x)])
        names = [f"{label} of {column}", f"{label} of {column} {level:g} % CI low",
                 f"{label} of {column} {level:g} % CI high", "count"]
        data = {name: [r[i] for r in rows] for i, name in enumerate(list(groups) + names)}
        parts = [(" / ".join(_say_label(v) for v in r[:len(groups)]) + ": " if groups else "")
                 + f"{_say_number(r[-4])} ({_say_number(r[-3])} to {_say_number(r[-2])})"
                 for r in rows[:GROUPS_IN_SENTENCE]]
        where = f" for each {_each(groups)}" if groups else ""
        print(f'The {label} of "{column}"{where}, with its {level:g} % Bayesian credible interval: '
              f"{'; '.join(parts)}{' ...' if len(rows) > GROUPS_IN_SENTENCE else ''}.")
        print("Interval: Bayesian, with the uninformative (Jeffreys) prior, so it needs no resampling; the number is "
              "the posterior mean (SciPy bayes_mvs, Oliphant 2006; the same as SciPy mvsdist). The average's interval "
              "is the usual t interval.")
        del example
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ number words
    @friendly(renamed={"for_each": "for_each_group_in"}, others={"margins": "with_totals"})
    def find_average_of(self, column, for_each_group_in=None, every=None, across=None, interval=None, weights=None,
                        with_totals=False):
        """The average (mean) of a column; empty cells are skipped.

        table.find_average_of("marks", for_each_group_in="class")   (with sdata.get_example("marks"))
        across= gives a cross table, one column per subject:
        table.find_average_of("marks", for_each_group_in="class", across="subject")
        every= groups a date column in for_each_group_in= into "hour", "day", "week", "month",
        "quarter" or "year" periods (a date with a time zone on its own clock, read by Polars on both
        engines: local clock times before 1970 follow the main world time-zone data (IANA), the same on
        every computer):
        table.turn_into_dates("year")
        table.find_average_of("population", for_each_group_in="year", every="year")   (with sdata.get_example("growth"))
        interval=95 adds the 95 % confidence interval of each average (the t interval, as R
        t.test()) and gives back a table with the average, the interval and the count.
        weights="people" gives the weighted average: each row counts as much as its number in the
        column of weights (statsmodels DescrStatsW, as R weighted.mean()).
        Under a survey design (table.use_survey_design) it gives the population average with its
        standard error and interval, from R survey::svymean.
        with_totals=True adds a "(total)" row and column to a cross table: the average of all the rows
        of that group (or subject), as pandas pivot_table(aggfunc="mean", margins=True); rows with an
        empty group are kept, as "(empty)", and count in the totals (pandas leaves them out):
        table.find_average_of("marks", for_each_group_in="class", across="subject", with_totals=True)
        """
        from .places import direction_note

        if self._survey_on():
            self._survey_only("find_average_of", locals(), ("column", "for_each_group_in"))
            return self._survey_summary("find_average_of", "mean", column, for_each_group_in, label="average")
        direction_note(column)
        if with_totals is not False and (weights is not None or interval is not None):
            raise SimplydataError("with_totals=True goes with a plain cross table; leave out weights= and interval=.")
        if weights is not None:
            return self._weighted("find_average_of", column, weights, for_each_group_in, every, across, interval)
        if interval is not None:
            return self._summary_interval("find_average_of", column, for_each_group_in, every, across, interval)
        return self._summary("find_average_of", column, for_each_group_in, every, across, with_totals=with_totals)

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
        Under a survey design (use_survey_design) it gives the population median (R survey).
        """
        if self._survey_on():
            self._survey_only("find_median_of", locals(), ("column", "for_each_group_in"))
            return self._survey_summary("find_median_of", "quantile", column, for_each_group_in, percent=50,
                                        label="median")
        if weights is not None:
            return self._weighted_percentile("find_median_of", column, 50.0, weights, weight_kind, for_each_group_in,
                                             every, across, interval, "linear", said="median")
        if weight_kind != "frequency":
            raise SimplydataError("weight_kind= says how to read weights=, so it goes with weights=.\n"
                                  'For example:  table.find_median_of("length", weights="n", weight_kind="analytic")')
        if interval is not None:
            return self._summary_interval("find_median_of", column, for_each_group_in, every, across, interval)
        return self._summary("find_median_of", column, for_each_group_in, every, across)

    @friendly(renamed={"for_each": "for_each_group_in"}, others={"margins": "with_totals"})
    def find_total_of(self, column, for_each_group_in=None, every=None, across=None, with_totals=False):
        """All the numbers in a column added up; empty cells are skipped.

        table.find_total_of("count", for_each_group_in="shop")   (with sdata.get_example("fruit"))
        table.find_total_of("count", for_each_group_in="shop", across="fruit")   a cross table
        every="month" with a date column in for_each_group_in= gives the total of each month.
        Under a survey design (use_survey_design) it gives the estimated population total (R survey).
        with_totals=True adds a "(total)" row and a "(total)" column to the cross table (pandas
        pivot_table(aggfunc="sum", margins=True), except that rows with an empty group are kept, as
        "(empty)", and count in the totals):
        table.find_total_of("count", for_each_group_in="shop", across="fruit", with_totals=True)
        """
        if self._survey_on():
            self._survey_only("find_total_of", locals(), ("column", "for_each_group_in"))
            return self._survey_summary("find_total_of", "total", column, for_each_group_in, label="total")
        return self._summary("find_total_of", column, for_each_group_in, every, across, with_totals=with_totals)

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

    @friendly(renamed={"method": "test_method", "for_each": "for_each_group_in"})
    def find_percentile_of(self, column=None, percent=None, for_each_group_in=None, every=None, across=None, test_method=None,
                           interval=None, weights=None, weight_kind="frequency"):
        """The value below which a given percent of the numbers lie; empty cells are skipped.

        table.find_percentile_of("marks", 90, for_each_group_in="class")   (with sdata.get_example("marks"))
        find_percentile_of("marks", 50) is the median, 25 and 75 the quartiles. Between two
        numbers it uses the usual linear rule (R quantile(type = 7), NumPy and pandas
        default). across= and every= work as in find_average_of.
        test_method= picks one of R's nine rules, by R's number or by name: 1 "inverted cdf",
        2 "averaged inverted cdf", 3 "closest observation", 4 "interpolated inverted cdf",
        5 "hazen", 6 "weibull" (as SPSS and Minitab), 7 "linear" (the default), 8
        "median unbiased" (recommended by Hyndman and Fan), 9 "normal unbiased" (NumPy's names, such as
        "median_unbiased", work too); NumPy percentile(method=), as R quantile(type =).
        interval=95 adds the 95 % confidence interval of each percentile: the exact interval
        from the order of the values (SciPy quantile_test, Thompson 1936: each end leaves at most
        2.5 % chance beyond it). For the median it is R DescTools::MedianCI(method = "exact");
        for other percents R DescTools::QuantileCI(method = "exact") chooses another pair of
        values (the nearby pair whose coverage is closest above 95 %), so the ends can differ.
        Both are exact: each covers the percentile at least 95 % of the time. With few values an
        end can be empty.
        weights="n" gives the weighted percentile. weight_kind="frequency" (the default) reads
        each weight as how many times the row counts, so it needs whole numbers: the rows are
        repeated and the usual test_method= is used (as R quantile(rep(x, w)) and Hmisc::wtd.quantile(x,
        w)); weights of 1 change nothing. weight_kind="analytic" reads any weight of 0 or more,
        such as a sampling weight: NumPy percentile(weights=, method="inverted_cdf"), the only
        weighted rule NumPy has (as R survey::svyquantile(qrule = "math")); it is a step, not a
        line between values, so with all weights 1 it is not the unweighted default.
        Under a survey design (table.use_survey_design) it gives the population percentile with
        Woodruff's interval, from R survey::svyquantile.
        """
        step = "find_percentile_of"
        if column is None:
            raise SimplydataError(f"{step}() needs the column first, then the percent.\n"
                                  f'For example:  table.{step}("marks", 90, for_each_group_in="class")   (with sdata.get_example("marks"))')
        number = _check_percent(step, percent)
        if self._survey_on():
            self._survey_only(step, locals(), ("column", "percent", "for_each_group_in", "number", "step"))
            return self._survey_summary(step, "quantile", column, for_each_group_in, percent=number,
                                        label=f"percentile {number:g}")
        share = number / 100
        rule = _percentile_rule(step, "linear" if test_method is None else test_method)
        if weights is not None:
            return self._weighted_percentile(step, column, number, weights, weight_kind, for_each_group_in, every,
                                             across, interval, rule, method_given=test_method is not None)
        if weight_kind != "frequency":
            raise SimplydataError("weight_kind= says how to read weights=, so it goes with weights=.\n"
                                  f'For example:  table.{step}("length", 90, weights="n", weight_kind="analytic")')
        if interval is not None:
            if rule != "linear":
                raise SimplydataError("interval= gives the interval of the percentile itself, the same for every "
                                      "test_method=; leave out test_method=.")
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
                'method="inverted_cdf")), the only rule NumPy has with weights, so test_method= cannot be changed. Leave '
                'out test_method=, or use weight_kind="frequency" (whole-number weights) to keep test_method=.')
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
        """find_percentile_of(test_method=) other than the linear rule: NumPy percentile(method=), as R quantile(type =)."""
        if every is not None or across is not None or not isinstance(column, str):
            raise SimplydataError("test_method= works with one column and for_each_group_in=; leave out every= and across=.")
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
    @friendly(renamed={"for_each": "for_each_group_in"}, others={"margins": "with_totals"})
    def count_rows(self, for_each_group_in=None, across=None, every=None, in_percent=False, with_totals=False):
        """How many rows the table has, or how many in each group.

        table.count_rows(for_each_group_in="class")   (with sdata.get_example("marks"))
        across= gives a cross table (pandas crosstab), one column per value:
        table.count_rows(for_each_group_in="shop", across="fruit")   (with sdata.get_example("fruit"))
        in_percent=True gives percents (0 to 100) instead: of all rows, or with across= of
        each row of the cross table, so every row adds up to 100 %.
        every="month" with a date column in for_each_group_in= counts the rows of each month.
        Under a survey design (use_survey_design) it gives the estimated number in the population
        (R survey), and with in_percent=True each group's estimated share.
        with_totals=True adds a "(total)" row and a "(total)" column to a cross table, as pandas
        crosstab(margins=True, margins_name="(total)"). Rows with an empty group or across= value are
        kept, as "(empty)", and count in the totals; pandas crosstab leaves them out:
        table.count_rows(for_each_group_in="shop", across="fruit", with_totals=True)
        """
        if self._survey_on():
            self._survey_only("count_rows", locals(), ("for_each_group_in", "in_percent"))
            return self._survey_count("count_rows", for_each_group_in, in_percent)
        step = "count_rows"
        if not isinstance(in_percent, bool):
            raise SimplydataError("in_percent= should be True or False.")
        _check_with_totals(step, with_totals, across, every, in_percent)
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
            result, labels = self._cross(frame, groups, across, nw.len(), fill=0, periods=periods,
                                         with_totals=with_totals)
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
    def count_each(self: _Same, column=None, interval=None, columns=None, in_order=None) -> _Same:
        """Each different value in a column, how many times it appears, and its percent.

        Biggest count first. Empty cells count as a value of their own, so the percents
        are out of all rows. Percents are rounded to 1 decimal place.
        table.count_each("fruit")   (with sdata.get_example("fruit"))
        interval=95 adds a 95 % interval to each percent that holds for all of them at once
        (Sison and Glaz, statsmodels multinomial_proportions_confint, as R
        DescTools::MultinomCI()).
        Answers on a scale (Likert items): columns= names the questions and in_order= the
        answers from the lowest to the highest; one row per question with the count and percent
        of each answer, the percent in the top two answers and the median answer:
        table.count_each(columns=["teaching", "pace"], in_order=["strongly disagree", "disagree",
        "neutral", "agree", "strongly agree"])   (with sdata.get_example("course_feedback"))
        """
        if columns is not None or in_order is not None:
            if interval is not None:
                raise SimplydataError("interval= goes with one column without in_order=; for answers on a scale "
                                      "leave it out.")
            return self._count_answers(columns if columns is not None else column, in_order)
        if column is None:
            raise SimplydataError(
                "count_each() needs one column name in quotes.\n"
                'For example, with sdata.get_example("fruit"): table.count_each("fruit")'
            )
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

    def _count_answers(self, columns, in_order):
        """count_each(columns=, in_order=): answers on a scale, one row per question (table/answers.py)."""
        from .answers import answer_table, check_answers

        data = self._frame.to_pandas()
        columns, levels = check_answers("count_each()", data, columns, in_order)
        found = answer_table(data, columns, levels)
        empty = int(found.pop("empty").sum())
        k = len(levels)
        print(f"Answers to {len(columns)} question{'s' * (len(columns) != 1)} on a scale of {k} ({levels[0]} to "
              f"{levels[-1]}), counted by pandas; each percent is out of the answers given:")
        for _, row in found.head(GROUPS_IN_SENTENCE).iterrows():
            share = row["percent in top two"]
            print(f"  {row['question']}: {_say_number(share)} % in the top two ({levels[-2]} or {levels[-1]}), median "
                  f"answer \"{row['median answer']}\" ({row['answers']} answers)")
        if len(found) > GROUPS_IN_SENTENCE:
            print(f"  ... and {len(found) - GROUPS_IN_SENTENCE} more in the table.")
        print("The median answer is a real answer (R quantile(type = 1)). simplydata gives no averages of answers: the "
              "steps between them need not be equal (Jamieson 2004). chart.draw_answer_bars() draws the same counts.")
        if empty:
            print(f"Note: {empty} empty cell{'s were' if empty != 1 else ' was'} not counted.")
        if k == 3:
            print(f"Note: with 3 answers the top two include the middle one (\"{levels[1]}\"); read the percent of "
                  f"\"{levels[2]}\" alone as well.")
        if self._frame.implementation.is_polars():
            import polars as pl

            found = pl.from_pandas(found)
        return self._new_table(nw.from_native(found, eager_only=True))

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
                                   ends_with=_NOT_GIVEN, is_empty=_NOT_GIVEN, interval_by="exact", capitals_matter=True):
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
        Under a survey design (table.use_survey_design) a condition gives the population percent with
        survey's logit interval (R survey::svyciprop).
        capitals_matter=False makes the text words find "maths", "Maths" and "MATHS" alike:
        table.find_percent_of_rows_where("subject", is_equal_to="maths", capitals_matter=False)
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
            if self._survey_on():
                raise SimplydataError("Under a survey design, each group's share of the population comes from "
                                      f'table.count_rows(for_each_group_in="{for_each_group_in}", in_percent=True).')
            return self._percent_of_rows(step, for_each_group_in, every, method)
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs one column name in quotes.\nFor example:  {example}")
        self._need_columns(column)
        groups = self._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else None
        if not given:
            if self._survey_on():
                raise SimplydataError("Under a survey design, find_percent_of_rows_where needs a condition, like "
                                      f'is_equal_to="yes"; for shares of a total use table.find_total_of("{column}", '
                                      "for_each_group_in=...).")
            return self._percent_of_total(step, column, groups, every)
        if len(given) > 1:
            names = " and ".join(f"{c}=" for c in given)
            raise SimplydataError(
                f"{step}() takes one condition at a time, but you gave {names}. "
                "Use is_between=[low, high] for a range.\n"
                'For example:  table.find_percent_of_rows_where("marks", is_between=[40, 80])   (with sdata.get_example("marks"))'
            )
        cond, words = self._condition(step, column, options, (), capitals_matter)
        counted = nw.lit(True) if "is_empty" in given else ~self._empty(column)
        if self._survey_on():
            if every is not None or interval_by != "exact":
                raise SimplydataError("Under a survey design, find_percent_of_rows_where takes the column, one "
                                      "condition and for_each_group_in= (the interval is survey's logit interval).")
            flags = self._frame.select(cond.fill_null(False).cast(nw.Int64).alias("h"),
                                       counted.cast(nw.Int64).alias("c"))
            return self._survey_percent(step, column, flags["h"].to_numpy(), flags["c"].to_numpy().astype(bool),
                                        words, for_each_group_in)
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
    def _summary_in_bins(self, step, column, show, for_each_group_in, every, separator, in_bins_of):
        """find_summary_of(in_bins_of=): each row gets the bin of each in_bins_of= column (its lower and upper edge,
        as SciPy binned_statistic: a bin holds its lower edge, the last one its upper edge too); then the bins are
        summarised as groups. Bins with no values are left out."""
        import contextlib
        import io

        example = ('table.find_summary_of("marks", show=["average", "count"], in_bins_of={"hours": 2})'
                   '   (with sdata.get_example("marks"))')
        if every is not None or separator is not None or isinstance(show, dict):
            raise SimplydataError("in_bins_of= goes with a column and a list of measures in show=, not with every=, "
                                  f"separator= or a dict in show=.\nFor example:  {example}")
        if not isinstance(in_bins_of, dict) or not in_bins_of:
            raise SimplydataError("in_bins_of= needs a dict: the column to cut into bins, and how wide each bin is "
                                  f"(or a list of the edges).\nFor example:  {example}")
        if column is None:
            raise SimplydataError(f"{step}() needs the column to summarise.\nFor example:  {example}")
        columns = _as_list(step, "the column", column)
        groups = self._group_columns(step, for_each_group_in, columns) if for_each_group_in is not None else []
        binned = list(in_bins_of)
        for name in binned:
            if not isinstance(name, str):
                raise SimplydataError(f"in_bins_of= names a column in quotes, not {name!r}.\nFor example:  {example}")
            if name in groups:
                raise SimplydataError(f'"{name}" is in in_bins_of= and in for_each_group_in=; give it once.')
        frame = self._number_frame(step, binned + [c for c in columns if c not in binned])
        measures = self._measures(step, show)
        extra = [m for m in measures if m in BIN_MEASURES]
        if extra and len(binned) > 1:
            raise SimplydataError(f'show="{extra[0]}" adds up the bins of one column; in_bins_of= has {len(binned)}.')
        inner = [m for m in measures if m not in BIN_MEASURES]
        if extra and "count" not in inner:
            inner.append("count")
        n = len(frame)
        keep = np.ones(n, dtype=bool)
        new_columns, described = [], []
        for name in binned:
            x = frame[name].cast(nw.Float64).to_numpy().astype(float)
            edges = _bin_edges(step, name, in_bins_of[name], x, example)
            index = np.searchsorted(edges, x, side="right") - 1
            index[x == edges[-1]] = len(edges) - 2  # the last bin holds its upper edge too (SciPy binned_statistic)
            inside = (index >= 0) & (index < len(edges) - 1) & ~np.isnan(x)
            keep &= inside
            safe = np.clip(index, 0, len(edges) - 2)
            for label, values in ((f"{name} from", edges[safe]), (f"{name} to", edges[safe + 1])):
                if label in frame.columns:
                    raise SimplydataError(f'in_bins_of= makes a column called "{label}"; the table has one. '
                                          "Rename it first.")
                new_columns.append(nw.new_series(label, values, nw.Float64, backend=frame.implementation))
            outside = int((~inside & ~np.isnan(x)).sum())
            width = in_bins_of[name]
            how = (f"{_say_number(float(width))} wide" if not isinstance(width, (list, tuple, np.ndarray))
                   else "with the edges given")
            described.append(f'"{name}" in {len(edges) - 1} bins {how}, from {_say_number(edges[0])} to '
                             f"{_say_number(edges[-1])}" + (f" ({outside} values outside them left out)" if outside
                                                            else ""))
            empty = int(np.isnan(x).sum())
            if empty:
                described[-1] += f" ({empty} empty cells left out)"
        frame = frame.with_columns(*new_columns).with_columns(
            nw.new_series("__keep", keep, nw.Boolean, backend=frame.implementation))
        frame = frame.filter(nw.col("__keep")).drop("__keep")
        if len(frame) == 0:
            raise SimplydataError(f"No value of {', '.join(binned)} falls in the bins, so there is nothing to "
                                  f"summarise.\nFor example:  {example}")
        keys = groups + [label for name in binned for label in (f"{name} from", f"{name} to")]
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            result = self._new_table(frame).find_summary_of(columns, show=inner, for_each_group_in=keys)
        lines = printed.getvalue().splitlines()
        if extra:
            result = _add_bin_measures(result, columns, groups, f"{binned[0]} from", extra, "count" in measures)
        print(f"Summary of {_names(columns)} in bins of " + "; ".join(described)
              + (f", for each {_names(groups)}" if groups else "") + ":")
        for line in lines[1:]:
            print(line)
        print("Method: each value goes into the bin that holds it, its lower edge included (the last bin holds its "
              "upper edge too), as SciPy binned_statistic" + ("_2d" if len(binned) == 2 else "_dd" if len(binned) > 2
                                                               else "") + "; bins with no values are left out.")
        return result

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

    @friendly(renamed={"for_each": "for_each_group_in"}, others={"sep": "separator", "bins": "in_bins_of"})
    def find_summary_of(self, column=None, show=None, for_each_group_in=None, every=None, separator=None,
                        in_bins_of=None):
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
        WRS2::winmean(tr = 0.2); "winsorised average 10" pulls in 10 %), and "first" and "last"
        (the first and last filled value, in the order of the rows: sort first with sort_by, as
        pandas groupby().first() / last() and Polars first() / last()). With every="month",
        show=["first", "biggest", "smallest", "last"] gives each month's open, high, low and close.
        Without show=: count, average, standard deviation, smallest, median,
        biggest. A measure of your own also works: a function that gets one group's
        numbers (a NumPy array) and gives back one number, show=["average", my_measure].
        The new table has one row for each column (and each group), so it can be saved
        or charted. every= groups a date column in for_each_group_in= by "week", "month", "year" ...
        "product" multiplies the values together (pandas prod(), Polars product()) and "entropy" is the Shannon
        entropy of the values as shares of their total, natural log (SciPy entropy, Polars entropy()).
        show=["joined text"] joins the text of each group into one cell, "; " between them (separator= for
        another), the mirror of split_into_rows (pandas groupby().agg("; ".join), Polars str.join):
          table.find_summary_of("name", show=["joined text"], separator=", ", for_each_group_in="class")
        Different measures for different columns, one row for each group (pandas named aggregation, Polars
        group_by().agg()): show= a dict of column: measures, and leave out the column:
          table.find_summary_of(show={"marks": ["average", "count"], "hours": ["total"]}, for_each_group_in="class")
        The columns of that table are called "marks average", "marks count" and "hours total".
        More scipy.stats measures (families for 100 %): "geometric standard deviation" (gstd), "power mean 3"
        (pmean), "cumulant 2" and "cumulant variance 2" (kstat, kstatvar), "l-moment 2" (lmoment), "l-skewness"
        and "l-kurtosis" (the L-moment ratios, as R lmom::samlmu), "central moment 3"
        (moment, divided by n), "expectile 90" (expectile), "average between 40 and 80" and the same for "standard
        deviation", "variance" and "standard error" (tmean, tstd, tvar, tsem: only the values from 40 to 80),
        "smallest from 40" and "biggest up to 80" (tmin, tmax), "circular average in degrees", "circular standard
        deviation in degrees" and "circular variance in degrees" (or "in radians", "in hours"; circmean, circstd,
        circvar), "differential entropy" (in nats), "percentile rank 70" (the percent at which the usual percentile
        rule gives 70, the inverse of "percentile 90": estimated_cdf), "percent at or below 70" (percentileofscore)
        and "sigma-clipped average" (sigmaclip). Each of these prints one line with its method.
        in_bins_of= cuts a column of numbers into bins and summarises each bin (SciPy binned_statistic):
          table.find_summary_of("marks", show=["average", "count"], in_bins_of={"hours": 2})
        {"hours": 2} makes bins 2 wide, starting at a multiple of 2; {"hours": [0, 5, 10, 20]} gives the edges.
        Each bin holds its lower edge, and the last one its upper edge too. Two columns or more make bins of each
        (binned_statistic_2d, binned_statistic_dd). Bins with no values are left out. With in_bins_of=,
        show=["running count"] adds the counts up bin after bin (cumfreq) and "share of values" gives each bin's
        share of the values (relfreq).
        """
        step = "find_summary_of"
        if in_bins_of is not None:
            return self._summary_in_bins(step, column, show, for_each_group_in, every, separator, in_bins_of)
        bin_only = [m for m in ([show] if isinstance(show, str) else list(show) if isinstance(show, (list, tuple))
                                else []) if isinstance(m, str) and MEASURE_ALIASES.get(m, m) in BIN_MEASURES]
        if bin_only:
            raise SimplydataError(f'show="{bin_only[0]}" adds up the bins of in_bins_of=, so it needs in_bins_of=.\n'
                                  'For example:  table.find_summary_of("marks", show=["count", "running count"], '
                                  'in_bins_of={"hours": 2})   (with sdata.get_example("marks"))')
        if isinstance(show, dict):
            return self._summary_by_column(step, column, show, for_each_group_in, every, separator)
        if separator is not None and (not isinstance(show, (list, tuple, str)) or "joined text" not in (
                [show] if isinstance(show, str) else list(show))):
            raise SimplydataError('separator= goes with show=["joined text"]: it is what goes between the texts.')
        if column is None:
            raise SimplydataError(
                f"{step}() needs the column to summarise.\n"
                f'For example:  table.{step}("marks", for_each_group_in="class", show=["average", "count"])'
                '   (with sdata.get_example("marks"))'
            )
        columns = _as_list(step, "the column", column)
        measures = self._measures(step, show)
        groups = self._group_columns(step, for_each_group_in, columns) if for_each_group_in is not None else []
        if "joined text" in measures:
            return self._joined_text(step, columns, measures, groups, every, separator)
        if "column" in groups:
            raise SimplydataError(
                'find_summary_of() makes a column called "column", so a for_each_group_in= column cannot have that name.\n'
                'Rename it first, for example table.rename_column("column", to="group").'
            )
        frame = self._number_frame(step, columns)
        frame, periods = self._periods(step, frame, groups or None, every)
        frame = frame.with_columns(nw.col(c).is_null().cast(nw.Int64).alias(f"__empty {i}")
                                   for i, c in enumerate(columns))
        names = [m for m in measures if isinstance(m, str) and not _is_array_measure(m) and m not in FIRST_LAST]
        ends = [m for m in measures if m in FIRST_LAST]
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
            if ends:
                array_values = {**array_values, **self._first_and_last(frame, groups, c, ends)}
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
        if ends:  # first and last keep the column's own kind (a whole number above 2**53 stays exact)
            result = self._ends_in_own_kind(result, data, columns, ends)
        result = result.with_columns(nw.col(n).cast(nw.Int64) for n in ("count", "empty cells") if n in out_names)
        table = self._new_table(result)
        self._note_empty(frame, columns)
        self._say_summary(table, columns, groups, out_names, periods)
        for line in dict.fromkeys(_method_line(n) for n in out_names if isinstance(n, str)):
            if line:
                print(line)
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

    def _joined_text(self, step, columns, measures, groups, every, separator):
        """show=["joined text"]: the text of each group in one cell (Polars str.join on both engines, as pandas
        groupby().agg("; ".join)); the rows of each group in table order, empty cells left out."""
        import polars as pl

        if measures != ["joined text"]:
            raise SimplydataError('show=["joined text"] goes on its own (its column holds text, not numbers); '
                                  "find the other measures in a step of their own.")
        if separator is None:
            separator = TEXT_SEPARATOR
        if not isinstance(separator, str):
            raise SimplydataError('separator= is the text that goes between the texts, such as separator="; ".')
        if "column" in groups:
            raise SimplydataError('find_summary_of() makes a column called "column", so a for_each_group_in= column '
                                  'cannot have that name.')
        self._need_columns(*columns)
        frame, periods = self._periods(step, self._frame, groups or None, every)
        from ._base import polars_text

        polars = frame.to_polars()
        polars = polars.with_columns(polars_text(polars[c]).alias(c) for c in columns)  # dates as 2026-03-01
        parts = []
        for c in columns:
            joined = pl.col(c).drop_nulls().str.join(separator).alias("joined text")
            if groups:
                part = polars.group_by(groups, maintain_order=True).agg(joined).sort(groups, nulls_last=True)
            else:
                part = polars.select(joined)
            parts.append(part.with_columns(pl.lit(c).alias("column")).select("column", *groups, "joined text"))
        result = pl.concat(parts)
        if not frame.implementation.is_polars():
            result = result.to_pandas()
        table = self._new_table(nw.from_native(result, eager_only=True))
        rows = table._frame.rows(named=True)
        print(f"The text of {_names(columns)} joined into one cell" + (f" for each {_each(groups, periods)}"
                                                                         if groups else "")
              + f', "{separator}" between the texts (empty cells left out):')
        for row in rows[:SUMMARY_LINES]:
            label = [f'"{row["column"]}"'] if len(columns) > 1 else []
            label += [_say_label(row[g], periods.get(g)) for g in groups]
            text = row["joined text"] if len(row["joined text"]) <= 60 else row["joined text"][:57] + "..."
            print(("  " + " / ".join(label) + ": " if label else "  ") + text)
        if len(rows) > SUMMARY_LINES:
            print(f"  ... and {len(rows) - SUMMARY_LINES} more rows (the new table has them all)")
        _period_note(periods)
        return table

    def _summary_by_column(self, step, column, show, for_each_group_in, every, separator):
        """show={"marks": ["average", "count"], "hours": ["total"]}: different measures for different columns, one
        row for each group, the columns called "marks average" ... (pandas named aggregation, Polars agg)."""
        import contextlib
        import io

        if column is not None:
            raise SimplydataError(
                "With show= a dict of column: measures, the dict names the columns, so leave out the column.\n"
                'For example:  table.find_summary_of(show={"marks": ["average", "count"], "hours": ["total"]}, '
                'for_each_group_in="class")   (with sdata.get_example("marks"))')
        if not show or not all(isinstance(k, str) for k in show):
            raise SimplydataError('show= as a dict gives each column its measures: show={"marks": ["average", '
                                  '"count"], "hours": ["total"]}.')
        groups = _as_list(step, "for_each_group_in=", for_each_group_in) if for_each_group_in is not None else []
        result, periods = None, {}
        for name, measures in show.items():
            with contextlib.redirect_stdout(io.StringIO()):
                part = self.find_summary_of(name, show=measures, for_each_group_in=for_each_group_in, every=every,
                                            separator=separator)._frame
            if every is not None:
                periods = {g: every for g in groups if self._frame.schema[g].is_temporal()}
            renamed = {c: f"{name} {c}" for c in part.columns if c not in groups and c != "column"}
            part = part.drop("column").rename(renamed)
            if result is None:
                result = part
            else:
                # every part has the same groups in the same order (one group_by of the same rows, sorted, empty
                # keys last), so the measures are put side by side; a join would lose the empty-key group, whose
                # key never equals itself
                if groups:
                    part = part.drop(groups)
                result = nw.concat([nw.maybe_reset_index(result), nw.maybe_reset_index(part)], how="horizontal")
        table = self._new_table(nw.maybe_reset_index(result))
        out_names = [c for c in result.columns if c not in groups]
        print("Summary" + (f" for each {_each(groups, periods)}" if groups else "") + ", different measures for "
              "different columns:")
        for row in table._frame.rows(named=True)[:SUMMARY_LINES]:
            label = " / ".join(_say_label(row[g], periods.get(g)) for g in groups)
            items = ", ".join(f"{n} {_say_number(row[n]) if not isinstance(row[n], str) else row[n]}"
                              for n in out_names)
            print(("  " + label + ": " if label else "  ") + items)
        if len(result) > SUMMARY_LINES:
            print(f"  ... and {len(result) - SUMMARY_LINES} more rows (the new table has them all)")
        return table

    def _ends_in_own_kind(self, result, data, columns, ends):
        """The "first" and "last" columns built in the summarised column's own kind: Polars pl.Series(dtype=), pandas
        the same numpy kind, or its nullable twin (Int64 for int64) when a group has no value. Several columns of
        different kinds become decimals."""
        native = self._frame.to_native()
        kinds = {native.schema[c] if self._frame.implementation.is_polars() else native[c].dtype for c in columns}
        values = {end: [None if isinstance(v, float) and math.isnan(v) else v for v in data[end]] for end in ends}
        if len(kinds) != 1:
            return result.with_columns(nw.col(end).cast(nw.Float64) for end in ends)
        kind = next(iter(kinds))
        out = result.to_native()
        if self._frame.implementation.is_polars():
            import polars as pl

            out = out.with_columns(pl.Series(end, values[end], dtype=kind) for end in ends)
        else:
            import pandas as pd

            for end in ends:
                target, name = kind, str(kind)
                if any(v is None for v in values[end]) and name.startswith(("int", "uint")):  # numpy int64 -> Int64
                    target = "UInt" + name[4:] if name.startswith("uint") else "Int" + name[3:]
                out[end] = pd.Series(pd.array(values[end], dtype=target), index=out.index)
        return nw.from_native(out, eager_only=True)

    @staticmethod
    def _first_and_last(frame, groups, column, ends) -> dict:
        """find_summary_of(show=["first", "last"]): the first and last filled value of each group, in row order.

        The empty cells are left out first, as for every other measure, so the first value is the first filled one
        (pandas groupby().first() / last() skip empty cells; Polars first() / last() after drop_nulls()). A group
        whose every cell is empty has no first value, so its cell stays empty."""
        filled = frame.filter(~nw.col(column).is_null())
        exprs = [getattr(nw.col(column), end)().alias(f"__{end}") for end in ends]  # narwhals first() / last()
        if groups:
            found = filled.group_by(groups, drop_null_keys=False).agg(*exprs)
        else:
            found = filled.select(*exprs) if len(filled) else None
        values = {}
        for row in (found.rows(named=True) if found is not None else []):
            key = _key([row[g] for g in groups])
            for end in ends:
                values[(key, end)] = _plain(row[f"__{end}"])
        return values

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
    def get_column(self, name=None) -> Numbers | list:
        """One column on its own: a column of numbers becomes sdata.number_list, any other a plain list.

        marks = table.get_column("marks")   (with sdata.get_example("marks"))
        then marks.find_average(), marks.start_chart() ... like any sdata.number_list. Empty cells become
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
            from ..numbers import number_list

            if series.null_count() or dtype.is_float():
                values = series.cast(nw.Float64).to_numpy()
            else:
                values = series.cast(nw.Int64).to_numpy()
            return number_list(values)
        kind = "text" if dtype == nw.String or dtype == nw.Categorical or dtype == nw.Enum else (
            "True/False values" if dtype == nw.Boolean else "dates" if dtype.is_temporal() else "values")
        print(f'Note: "{name}" holds {kind}, not numbers, so it comes back as a plain Python list.')
        return [None if _missing(v) else _plain(v) for v in series.to_list()]

    # ------------------------------------------------------------------ correlation
    @friendly(renamed={"method": "test_method", "bayesian": ("test_method", {True: "bayesian", False: None}),
                       "seed": "with_seed"},
              others={"rscale": "prior_width", "prior_scale": "prior_width"})
    def find_correlation_between(self, *columns, test_method="pearson", show="r", sides=2, higher=None, lower=None,
                                 alternative=None, p_value_by="formula", interval_by=None, shuffles=9999, resamples=9999,
                                 with_seed=1, allowing_for=None, rows_back=None, sorted_by=None,
                                 empty_cells="leave out", prior_width="medium"):
        """How strongly columns of numbers go up or down together, from -1 to 1.

        table.find_correlation_between("hours", "marks")   (with sdata.get_example("marks"), one subject)
        One subject (table.keep_rows_where("subject", is_equal_to="Maths")) gives one row per child: each
        child is in the marks table three times, and a test needs rows that are independent.
        test_method="pearson" (a straight-line link, the usual one), "spearman" (uses ranks,
        for any link that keeps going one way) or "kendall" (Kendall's tau-b, also ranks: the
        share of pairs of rows that agree in order minus the share that disagree; as R
        cor.test(method = "kendall"), SciPy kendalltau). With two columns also "chatterjee xi" (does
        the second column follow from the first, in any shape? SciPy chatterjeexi), "weighted kendall"
        (Kendall's tau that counts the top of the ranking most, SciPy weightedtau) or "multiscale graph"
        (any kind of link, p-value from 1000 shuffles, SciPy multiscale_graphcorr). Prints the strength in words and the
        p-value from SciPy; Spearman's p-value for fewer than 1290 rows without tied values comes
        from R cor.test() (algorithm AS 89, R's default; SciPy has only the t approximation, used
        without R, with a note). With two columns it gives back the number r; rows with an
        empty cell in either column are skipped.
        With three or more columns it gives back a correlation table (as pandas .corr()),
        and prints the strongest pairs:
        table.find_correlation_between("hours", "marks", "height")
        Each pair uses the rows where both columns have a number. show="p-value" gives the
        table of p-values instead, and show="each pair" one row per pair (r, p-value,
        rows), ready for add_adjusted_p_value_column(): testing many pairs makes a chance
        finding more likely. With two columns, show="result table" gives back a one-row table
        instead of r: r, its 95 % interval, the p-value (from the formula or, with
        p_value_by="shuffling", from shuffling; the interval from interval_by=), which directions
        were tested, the rows used and the strength in words; with three or more it is the same as
        show="each pair".
        allowing_for="height" (two columns and one to allow for) gives the partial correlation: the link left
        after taking out what both columns share with the third, from R ppcor::pcor.test() (Pearson,
        Spearman or Kendall). With show="result table" it is a one-row table of pcor.test()'s numbers: r,
        its statistic (t, or z for Kendall), the p-value and the rows (no interval: ppcor gives none):
        table.find_correlation_between("hours", "marks", allowing_for="height", show="result table")
        show="covariance" gives the covariance table instead (pandas
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
        test_method="bayesian" (two columns) gives the Bayes factor and a 95 % credible interval of the
        correlation instead of a p-value: R BayesFactor::correlationBF() with a stretched beta prior
        whose width prior_width= sets ("medium" 1/3, the default; "wide" 0.577; "ultrawide" 1; or a
        number); 10,000 posterior draws (with_seed=1). Needs R (BayesFactor).
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
        if self._check_bayesian(step, test_method, prior_width):
            return self._bayesian_correlation(step, names, prior_width, with_seed, [
                ("show=", show, "r"), ("sides=", sides, 2), ("higher=", higher, None),
                ("lower=", lower, None), ("alternative=", alternative, None), ("p_value_by=", p_value_by, "formula"),
                ("interval_by=", interval_by, None), ("shuffles=", shuffles, 9999), ("resamples=", resamples, 9999),
                ("allowing_for=", allowing_for, None), ("rows_back=", rows_back, None),
                ("sorted_by=", sorted_by, None), ("empty_cells=", empty_cells, "leave out")])
        if rows_back is not None or sorted_by is not None:
            if rows_back is None:
                raise SimplydataError(f"{step}() uses sorted_by= with rows_back= (the cross-correlation); "
                                      "give rows_back=, such as rows_back=12.")
            if (sides != 2 or higher is not None or lower is not None or alternative not in (None, "two-sided")
                    or p_value_by != "formula" or interval_by is not None or allowing_for is not None):
                raise SimplydataError(f"{step}() with rows_back= gives the cross-correlation; leave out sides=, "
                                      "higher=, lower=, p_value_by=, interval_by= and allowing_for=.")
            if _plain_name(test_method) != "pearson" or _plain_name(show) != "r":
                raise SimplydataError(f"{step}() with rows_back= gives the cross-correlation, which is "
                                      'Pearson\'s r (as R ccf()); leave out test_method= and show=.')
            return self._cross_correlation(step, names, rows_back, sorted_by)
        if isinstance(test_method, str) and test_method.strip().lower() in CORRELATION_ALIASES:
            test_method = CORRELATION_ALIASES[test_method.strip().lower()]
        self._check_choice(step, "test_method", test_method, CORRELATION_METHODS + ("bayesian",))
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

            found = correlation_imputed(self, step, names, _plain_name(test_method), with_seed)
            if found is not None:
                return found
        shown = _plain_name(show)
        if shown not in CORRELATION_SHOW:
            raise choice_error(step, "show", show, list(CORRELATION_SHOW))
        if shown == "covariance":
            if len(set(names)) < len(names):
                twice = next(n for n in names if names.count(n) > 1)
                raise SimplydataError(f'"{twice}" is listed twice. Give each column once.')
            if (_plain_name(test_method) != "pearson" or sides != 2 or higher is not None or lower is not None
                    or alternative not in (None, "two-sided") or p_value_by != "formula" or interval_by is not None
                    or allowing_for is not None):
                raise SimplydataError('show="covariance" gives the covariance table (no test, no ranks); leave out '
                                      "test_method=, sides=, higher=, p_value_by=, interval_by= and allowing_for=.\n"
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
        if len(names) == 2 and shown not in ("r", "result table"):
            raise SimplydataError(
                f'show="{show}" is for a correlation table of three or more columns. With two columns you get r, '
                'and the sentence gives its p-value; show="result table" gives r, its interval, the p-value and the '
                "rows as a one-row table."
            )
        if shown == "result table" and test_method in ORDINAL_METHODS:
            raise SimplydataError('show="result table" goes with test_method="pearson", "spearman" or "kendall"; leave '
                                  "out show= here.")
        if shown == "result table" and len(names) > 2:
            shown = "each pair"  # for three or more columns the result table is one row per pair
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
        if (test_method in ORDINAL_METHODS or allowing_for is not None) and len(names) != 2:
            raise SimplydataError(f'test_method="{test_method}" and allowing_for= work with two columns.' if allowing_for is None
                                  else "allowing_for= works with two columns (and the one to allow for).")
        if test_method in ORDINAL_METHODS and (alt != "two-sided" or p_value_by != "formula" or interval_by is not None
                                          or allowing_for is not None):
            raise SimplydataError(f'test_method="{test_method}" gives the measure of two columns on its own; leave out '
                                  "sides=, p_value_by=, interval_by= and allowing_for=.")
        if allowing_for is not None:
            if not isinstance(allowing_for, str) or allowing_for in names:
                raise SimplydataError('allowing_for= needs a third column name, such as allowing_for="height".')
            if alt != "two-sided" or p_value_by != "formula" or interval_by is not None:
                raise SimplydataError("allowing_for= gives the two-sided partial correlation; leave out sides=, "
                                      "p_value_by= and interval_by=.")
            return self._partial_correlation(step, self._number_frame(step, names + [allowing_for]), names[0],
                                             names[1], allowing_for, test_method,
                                             result_table=shown == "result table")
        frame = self._number_frame(step, names)
        if test_method in LINK_METHODS:
            return self._link_measure(step, frame, names[0], names[1], test_method, with_seed)
        if test_method in ORDINAL_METHODS:
            return self._ordinal_association(step, frame, names[0], names[1], test_method)
        if len(names) == 2:
            return self._one_correlation(step, frame, names[0], names[1], test_method, alt, up,
                                         p_value_by=p_value_by, interval_by=interval_by, shuffles=shuffles,
                                         resamples=resamples, seed=with_seed, result_table=shown == "result table")
        return self._correlation_table(step, frame, names, test_method, shown)

    def _bayesian_correlation(self, step, names, prior_width, with_seed, given):
        """find_correlation_between(a, b, test_method="bayesian"): the Bayes factor and the posterior of the correlation, R
        BayesFactor::correlationBF() (table/bayes_words.py)."""
        from . import bayes_r, bayes_words
        from .stat_tests import _skipped_note

        bayes_words.check_bayes_options(step, given)
        if len(names) != 2 or names[0] == names[1]:
            raise SimplydataError("test_method=\"bayesian\" gives the correlation of two different columns; give two column names, "
                                  'such as table.find_correlation_between("hours", "marks", test_method="bayesian").')
        seed = bayes_words.check_seed(with_seed)
        width = bayes_r.width_value(prior_width)
        frame = self._number_frame(step, names)
        pairs = frame.select(names[0], names[1]).drop_nulls()
        _skipped_note(len(frame) - len(pairs), names)
        if len(pairs) < 3:
            raise SimplydataError(f'{step}() needs at least 3 rows where both "{names[0]}" and "{names[1]}" have a '
                                  f"number; this table has {len(pairs)}.")
        a = pairs[names[0]].to_numpy().astype(float)
        b = pairs[names[1]].to_numpy().astype(float)
        for name, values in ((names[0], a), (names[1], b)):
            if values.min() == values.max():
                raise SimplydataError(f'Every value of "{name}" is the same in the rows used, so it cannot be '
                                      "correlated with anything.")
        return bayes_words.correlation(self, names[0], names[1], a, b, width, seed)

    @staticmethod
    def _correlate(step, frame, column_a, column_b, method, alternative="two-sided", notes=None, need_p=True):
        """r, p and the number of rows used, for one pair (rows with an empty cell skipped).

        Spearman's p-value is R cor.test()'s default: below 1290 rows without ties algorithm AS 89 (Best and
        Roberts 1975), from R itself (SciPy has only the t approximation); otherwise, or without R, SciPy's t
        approximation, and a note for notes= says why. need_p=False: only r is used, so R is not asked."""
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
            no_ties = len(np.unique(a)) == len(a) and len(np.unique(b)) == len(b)
            if need_p and len(a) < SPEARMAN_EXACT_LIMIT and no_ties:
                p = _spearman_p_from_r(a, b, alternative, notes)
                if p is not None:
                    return float(result[0]), p, len(pairs)
        else:
            result = stats.kendalltau(a, b, variant="b", alternative=alternative)
        return float(result[0]), float(result[1]), len(pairs)

    def _one_correlation(self, step, frame, column_a, column_b, method, alternative="two-sided", up=None,
                         p_value_by="formula", interval_by=None, shuffles=9999, resamples=9999, seed=1,
                         result_table=False):
        how_p = []
        r, p, n = self._correlate(step, frame, column_a, column_b, method, alternative, notes=how_p,
                                  need_p=p_value_by != "shuffling")
        skipped = len(frame) - n
        name = METHOD_NAMES[method]
        if skipped:
            rows = "row" if skipped == 1 else "rows"
            verb = "was" if skipped == 1 else "were"
            print(f'Note: {skipped} {rows} with an empty cell in "{column_a}" or "{column_b}" {verb} skipped.')
        extra, interval = [], ""
        low = high = math.nan
        if interval_by is None:
            interval, note, low, high = self._correlation_interval(frame, column_a, column_b, method, alternative)
            if note:
                extra.append(note)
        if p_value_by != "shuffling":
            extra.extend(how_p)
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
        if not result_table:
            return r
        tested = {"two-sided": "both directions", "greater": "positive only", "less": "negative only"}
        data = {"column 1": [column_a], "column 2": [column_b], "method": [name], "r": [float(r)],
                "95 % CI low": [float(low)], "95 % CI high": [float(high)],
                "interval from": ["bootstrap (BCa)" if interval_by == "bootstrap" else
                                  ("formula" if not math.isnan(low) else "none")],
                "p-value": [float(p)], "p-value from": ["shuffling" if p_value_by == "shuffling" else "formula"],
                "tested": [tested.get(alternative, alternative)], "rows": [int(n)], "strength": [_strength(r)]}
        print('Gives back the result as a one-row table (show="result table").')
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

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
            return (f"; values from {_interval_words(ci.low, ci.high)} fit the data ({kind}95 % CI)", "",
                    float(ci.low), float(ci.high))
        if alternative != "two-sided":
            return "", "", math.nan, math.nan
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
                        '"simplydata[r]", install R, then in R install.packages("DescTools").'), math.nan, math.nan
        how = "Fisher's z" if method == "spearman" else "asymptotic standard error"
        return (f"; values from {_num(found[1])} to {_num(found[2])} fit the data (95 % CI, {how}, R DescTools)", "",
                float(found[1]), float(found[2]))

    def _link_measure(self, step, frame, column_a, column_b, method, seed):
        """find_correlation_between(test_method="chatterjee xi" | "weighted kendall" | "multiscale graph"): SciPy
        chatterjeexi (does the second column follow from the first, in any shape?), weightedtau (Kendall's tau that
        weighs the top of the ranking most) and multiscale_graphcorr (any kind of link, with a p-value from
        shuffling). Gives back the measure."""
        from scipy import stats

        from .stat_tests import _num

        pairs = frame.select(column_a, column_b).drop_nulls()
        skipped = len(frame) - len(pairs)
        if skipped:
            print(f"Note: {skipped} row{'' if skipped == 1 else 's'} with an empty cell in \"{column_a}\" or "
                  f"\"{column_b}\" {'was' if skipped == 1 else 'were'} skipped.")
        x, y = (pairs[c].to_numpy().astype(float) for c in (column_a, column_b))
        least = {"multiscale graph": 5}.get(method, 3)
        if len(x) < least:
            raise SimplydataError(f"{METHOD_NAMES[method][0].upper()}{METHOD_NAMES[method][1:]} needs at least "
                                  f"{least} rows with both values; there are {len(x)}.")
        if method == "chatterjee xi":
            result = stats.chatterjeexi(x, y)
            value, p = float(result.statistic), float(result.pvalue)
            meaning = (f'how well "{column_b}" follows from "{column_a}" in any shape, from 0 (not at all) to 1 '
                       "(fully), read from the ranks; it is not symmetric (swap the columns for the other way)")
            how = ("SciPy chatterjeexi (Chatterjee 2021); its p-value is one-sided (is xi bigger than 0, as it "
                   "would be by chance?), from the normal approximation, as R XICOR::xicor(pvalue = TRUE)")
        elif method == "weighted kendall":
            result = stats.weightedtau(x, y)
            value, p = float(result.statistic), math.nan
            meaning = ("Kendall's tau with the pairs near the top of the ranking (the biggest values) counting most, "
                       "from -1 to 1")
            how = "SciPy weightedtau (Vigna 2015, hyperbolic weights, ranked by both columns); it gives no p-value"
        else:
            result = stats.multiscale_graphcorr(x, y, reps=1000, random_state=np.random.default_rng(seed))
            value, p = float(result.statistic), float(result.pvalue)
            meaning = "any kind of link between the columns (straight or not), from about 0 (none) to 1"
            how = ("SciPy multiscale_graphcorr (Vogelstein et al. 2019), its p-value from 1000 shuffles "
                   f"(seed {seed}), as R mgc::mgc.test()")
        p_text = f", {_p_shown(p)}" if not math.isnan(p) else ""
        print(f'{METHOD_NAMES[method][0].upper()}{METHOD_NAMES[method][1:]} between "{column_a}" and "{column_b}" = '
              f"{_num(value)} ({len(x)} rows{p_text}).")
        print(f"It measures {meaning}. Method: {how}; chosen with test_method=.")
        return value

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

    def _partial_correlation(self, step, frame, column_a, column_b, allowing_for, method, result_table=False):
        """The partial correlation of two columns allowing for a third, from R ppcor::pcor.test() (Python has none).
        With result_table=True (show="result table") it gives back pcor.test()'s numbers as a one-row table."""
        from .._r import r_call

        names = [column_a, column_b, allowing_for]
        rows = frame.select(*names).drop_nulls()
        skipped = len(frame) - len(rows)
        if skipped:
            print(f"Note: {skipped} row{'' if skipped == 1 else 's'} with an empty cell in "
                  + " or ".join(f'"{n}"' for n in names) + f" {'was' if skipped == 1 else 'were'} skipped.")
        x, y, z = (rows[c].to_numpy().astype(float) for c in names)
        found = r_call("p <- ppcor::pcor.test(x, y, z, method = m); list(r = p$estimate, p = p$p.value, "
                       "stat = p$statistic, n = p$n)", packages=("ppcor",),
                       what="the partial correlation (R ppcor::pcor.test())",
                       python_note="SciPy and statsmodels have no partial correlation test", x=x, y=y, z=z, m=method)
        r, p = float(np.asarray(found["r"])[0]), float(np.asarray(found["p"])[0])
        # the correlation without allowing for it, on the same rows as the partial correlation
        whole = float(self._correlate(step, rows.select(column_a, column_b), column_a, column_b, method,
                                      need_p=False)[0])
        print(f'The correlation between "{column_a}" and "{column_b}", allowing for "{allowing_for}", is r = {r:.2f} '
              f"({METHOD_NAMES[method]}, {len(x)} rows): {_strength(r)}; without allowing for it, r = {whole:.2f}.")
        print(_p_sentence(p, f'there were truly no link once "{allowing_for}" is allowed for',
                          "a link this strong or stronger", "that there is no link"))
        print(f'Method: partial correlation, as R ppcor::pcor.test(method = "{method}"): the link that is left after '
              f'taking out what both columns share with "{allowing_for}". A correlation does not show that one thing '
              "causes the other.")
        if not result_table:
            return r
        # ppcor's statistic: t on n - 2 - (columns allowed for) degrees of freedom for Pearson and Spearman, z for
        # Kendall (ppcor's own normal approximation); every number is pcor.test()'s
        data = {"column 1": [column_a], "column 2": [column_b], "allowing for": [allowing_for],
                "method": [f"partial {METHOD_NAMES[method]}"], "r": [r],
                "statistic name": ["z" if method == "kendall" else "t"],
                "statistic": [float(np.asarray(found["stat"])[0])], "p-value": [p], "tested": ["both directions"],
                "rows": [int(np.asarray(found["n"])[0])], "strength": [_strength(r)]}
        print('Gives back the result as a one-row table (show="result table").')
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

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
        found, how_p = {}, []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                found[(a, b)] = self._correlate(step, frame, a, b, method, notes=how_p)
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
        if SPEARMAN_NO_R in how_p:
            print(SPEARMAN_NO_R)
        elif SPEARMAN_AS89 in how_p:
            some = "" if how_p.count(SPEARMAN_AS89) == n_pairs else ", and from the t approximation for the others"
            print("Note: Spearman's p-values come from algorithm AS 89 (Best and Roberts 1975), run in R, for the pairs "
                  f"with fewer than 1290 rows and no tied values{some}, as R cor.test(method = \"spearman\") does.")
        print(f"Note: these p-values are not adjusted for testing {n_pairs} pairs. To adjust them: "
              f'results = table.find_correlation_between({listed}, show="each pair"), then '
              'results.add_adjusted_p_value_column(from_column="p-value").')
        return result
