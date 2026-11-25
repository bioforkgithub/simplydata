"""Looking, choosing columns and rows, empty cells, fixing columns.

Every word is written with narwhals expressions, so it works the same on pandas and Polars.
Only turn_into_dates() needs a little native code (text-to-date parsing that forgives bad cells).

What counts as an "empty cell" everywhere in this file:
a missing value (None, NaN, NaT), or text that is only spaces or nothing at all.
Empty cells never match a condition in keep_rows_where()/remove_rows_where(), except is_empty=.

keep_rows_where()/remove_rows_where() also read a written condition, "marks > 50 and class == 'A'".
The condition is read by the shared reader in conditions.py (also used by
add_group_column(rules=)): the text is never run, and a comparison with an empty cell is
never true and never false (as in SQL), so "not" never brings back empty cells either.
"""

from __future__ import annotations

from .._typing import _Same

import datetime as _dt
import math
import numbers
import re

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly, suggest
from ._base import numbered, numbered_at
from ._base import show as _show_native
from .conditions import (
    _NOT_GIVEN, _ConditionReader, _condition_error, _count_in, _empty_in, _is_number, _kind,
    _looks_like_number, _on_clock_of, _rows, _say, empty_cells_note,
)

# Conditions for keep_rows_where() / remove_rows_where(), in the order they are listed in messages.
CONDITIONS = (
    "above", "below", "at_least", "at_most", "equal_to", "not_equal_to",
    "between", "one_of", "contains", "starts_with", "ends_with", "is_empty", "after", "before", "matches_pattern",
)
COMPARE = ("above", "below", "at_least", "at_most")
TEXT_ONLY = ("contains", "starts_with", "ends_with", "matches_pattern")
# capitals_matter=False (tables phase, batch 2): the conditions on text that it changes
CAPITALS_OPTIONS = ("equal_to", "not_equal_to", "one_of", "contains", "starts_with", "ends_with", "matches_pattern")
# option names from other tools for capitals_matter= / matches_pattern=; they never run (ignore_case=True is
# capitals_matter=False, so it cannot be translated one to one)
CAPITALS_POINTERS = {"ignore_case": "capitals_matter=False",
                     "case": "capitals_matter= (case=False is capitals_matter=False)",
                     "regex": "matches_pattern="}
FILL_CHOICES = ("average", "median", "value above", "value below", "line between neighbours",
                "curve between neighbours", "curve without overshoot")
# with_the= choices that join the filled neighbours (they take sorted_by= and for_each_group_in=)
BETWEEN_CHOICES = ("line between neighbours", "curve between neighbours", "curve without overshoot")

# Text-to-date formats, tried in this order. Day comes before month (03/04/2026 is 3 April);
# month-first is only used when day-first cannot work (12/25/2026).
DATE_FORMATS = (
    "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M",
    "%Y/%m/%d", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M",
    "%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
    "%d.%m.%Y", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M",
    "%d-%m-%Y", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M",
    "%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M",
    "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y",
)



def _is(key: str) -> str:
    """The condition option as it is written now: above -> is_above (the old names still work)."""
    return key if key.startswith("is_") or key in ("contains", "starts_with", "ends_with", "matches_pattern") \
        else f"is_{key}"

def _with_times(*days):
    """Each day format, then the same with a time after it."""
    return tuple(f + t for f in days for t in ("", " %H:%M:%S", " %H:%M"))


_ISO = ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M")
# turn_into_dates(order=...): only the formats that read the parts in that order (a year with four
# digits written first is always year-month-day, so those formats are kept for every order).
DATE_ORDERS = {
    "day month year": _ISO + _with_times("%Y/%m/%d", "%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y")
    + ("%d %B %Y", "%d %b %Y"),
    "month day year": _ISO + _with_times("%Y/%m/%d", "%m/%d/%Y", "%m.%d.%Y", "%m-%d-%Y")
    + ("%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y"),
    "year month day": _ISO + _with_times("%Y/%m/%d", "%Y.%m.%d") + ("%Y%m%d", "%Y %B %d", "%Y %b %d"),
}

_NUMBER = r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$"
_THOUSANDS = r"^[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?$"  # 1,200 or 12,345.6
_DECIMAL_COMMA = r"^[+-]?\d*,\d+$"  # 12,5
_NEW = "__simplydata_new__"
SHOW_LIMIT = 1000  # rows that table.show() shows when rows= is not given


def _example(code: str, name: str = "marks") -> str:
    return f'\nFor example:  {code}   (with sdata.get_example("{name}"))'



COUNTS_EXAMPLE = '{"answer": ["yes", "no"], "count": [12, 5]}'  # the table of repeat_each_row_by's examples


def _rows_word(n) -> str:
    return f"{n} row" if n == 1 else f"{n} rows"


POLARS_HALVES_TO_EVEN = (1, 29)  # Polars rounds a float exactly halfway to the even neighbour from 1.29 (RoundMode)


def _need_polars_rounding_halves_to_even():
    """round_numbers_in on a Polars table: Polars before 1.29 rounded halves away from zero (2.5 to 3), so the
    same step would give other numbers than on a pandas table (2.5 to 2). pyproject asks for polars>=1.37; this
    stops an older Polars that is already installed from giving those other numbers without a word."""
    import polars as pl

    found = tuple(int(part) for part in pl.__version__.split(".")[:2] if part.isdigit())
    if found < POLARS_HALVES_TO_EVEN:
        raise SimplydataError(
            f"round_numbers_in() on a Polars table needs Polars 1.29 or newer, which rounds a number exactly halfway to "
            f"the even neighbour (2.5 to 2), as pandas, NumPy and R do. This computer has Polars {pl.__version__}, "
            "which rounds it away from zero (2.5 to 3).\nUpdate it with:  pip install -U \"polars>=1.29\"")


def _nice(value) -> str:
    """A number or date written for people: 61, 61.5, 2026-03-15."""
    if value is None:
        return ""
    if isinstance(value, float):
        if value != value:  # NaN
            return ""
        shown = round(value, 2)  # rounded first, so 62.001 is written 62, not 62.0
        if shown.is_integer() and abs(shown) < 1e15:
            return str(int(shown))
        return str(shown)
    if isinstance(value, (_dt.date, _dt.datetime)) or hasattr(value, "to_pydatetime"):
        return _say(value)
    return str(value)



# keep_columns() / remove_columns(): the kinds describe_columns() prints, and other ways people write them.
COLUMN_KINDS = ("number", "text", "date", "true/false", "mixed")
COLUMN_OPTIONS = ("to", "kind", "starts_with", "ends_with", "contains", "pattern")
_KIND_SPELLINGS = {
    "numbers": "number", "numeric": "number", "numerical": "number", "num": "number",
    "texts": "text", "string": "text", "strings": "text", "str": "text", "character": "text",
    "dates": "date", "datetime": "date", "datetimes": "date", "temporal": "date", "date/time": "date",
    "true or false": "true/false", "bool": "true/false", "boolean": "true/false",
    "booleans": "true/false", "logical": "true/false", "yes/no": "true/false",
}


def _kind_choice(step: str, kind) -> str:
    """kind= in its plain form ("numbers", "numeric" -> "number"), or a friendly error."""
    text = str(kind).strip().lower() if isinstance(kind, str) else ""
    text = _KIND_SPELLINGS.get(text, text)
    if text not in COLUMN_KINDS:
        raise choice_error(step, "kind", kind, COLUMN_KINDS[:4])
    return text


def _past(words: str, n: int) -> str:
    """keep_rows_where condition words in the past: "is above 100" -> "were above 100", "contains" -> "contained"."""
    if words.startswith("is "):
        return ("was " if n == 1 else "were ") + words[3:]
    for now, then in (("contains", "contained"), ("starts with", "started with"), ("ends with", "ended with")):
        if words.startswith(now):
            return then + words[len(now):]
    return words


def _columns_count(n: int) -> str:
    return f"{n} column" if n == 1 else f"{n} columns"


def _list_code(values) -> str:
    """[12, 40] for a list of positions, or just 12 for one."""
    values = list(values)
    return str(values[0]) if len(values) == 1 else "[" + ", ".join(str(v) for v in values) + "]"


def _cells(n: int) -> str:
    return f"{n} cell" if n == 1 else f"{n} cells"


def _as_list(names) -> list:
    """Accept keep_columns("a", "b") as well as keep_columns(["a", "b"])."""
    out = []
    for name in names:
        if isinstance(name, (list, tuple)):
            out.extend(name)
        else:
            out.append(name)
    return out


def _say_key(key) -> str:
    """A group's value (or tuple of values) for a printed sentence."""
    if isinstance(key, tuple):
        return " / ".join(str(k) for k in key)
    return str(key)


def _check_count(step: str, n, example: str) -> int:
    if not isinstance(n, numbers.Integral) or isinstance(n, bool) or n < 0:
        raise SimplydataError(f".{step}() needs a whole number of rows, like 5." + _example(example))
    return int(n)


def _parse_dates(native, formats=DATE_FORMATS):
    """Parse a native text Series (pandas or Polars) into dates, trying the formats in order.

    Native code because narwhals' to_datetime stops at the first bad cell; here bad cells
    simply become empty. The same formats in the same order are used for both engines.
    """
    if type(native).__module__.split(".")[0] == "polars":
        import polars as pl

        return (
            pl.DataFrame({"s": native})
            .select(pl.coalesce([pl.col("s").str.strptime(pl.Datetime("us"), f, strict=False) for f in formats]))
            .to_series()
            .rename(native.name)
        )
    import pandas as pd

    out = pd.Series(pd.NaT, index=native.index, dtype="datetime64[us]", name=native.name)
    for f in formats:
        missing = out.isna()
        if not missing.any():
            break
        found = pd.to_datetime(native.where(missing), format=f, errors="coerce").astype("datetime64[us]")
        out = out.fillna(found)
    return out



# ---------------------------------------------------------------- written_like= (tables phase, batch 2)
# An example date in the layout wanted ("31.12.2026", "March 15, 2026 14:30") is turned into the % codes of
# strftime / strptime by this fixed table of parts; pandas dt.strftime / to_datetime(format=) and Polars
# dt.to_string / str.strptime then do the work.
_MONTH_WORDS = {name.lower(): "%B" for name in ("January", "February", "March", "April", "May", "June", "July",
                                                 "August", "September", "October", "November", "December")}
_MONTH_WORDS.update({name[:3]: "%b" for name in _MONTH_WORDS if name[:3] != name})  # "may" stays %B
_DAY_WORDS = {name.lower(): "%A" for name in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
                                               "Sunday")}
_DAY_WORDS.update({name[:3]: "%a" for name in _DAY_WORDS})
WRITTEN_LIKE_EXAMPLE = 'table.turn_into_text("date", written_like="31.12.2026")'


def format_from_example(example: str) -> str:
    """The strftime / strptime codes of an example date: "31.12.2026" -> "%d.%m.%Y", "03/15/2026 14:30" ->
    "%m/%d/%Y %H:%M". The day must be above 12, so it cannot be taken for the month; text with % in it is taken as
    the codes themselves."""
    how = (f"\nFor example:  {WRITTEN_LIKE_EXAMPLE}  (any date written the way you want; use a day above 12, such "
           "as the 31st, so the day cannot be taken for the month)")
    if not isinstance(example, str) or not example.strip():
        raise SimplydataError("written_like= takes an example date in quotes, written the way you want." + how)
    if "%" in example:
        return example
    pieces = re.findall(r"\d+|[A-Za-z]+|[^\dA-Za-z]+", example)
    codes = [None] * len(pieces)
    numbers = [i for i, p in enumerate(pieces) if p.isdigit()]
    # the time of day: numbers joined by ":" (14:30 or 14:30:05), after the date
    time = [i for i in numbers if (i > 0 and pieces[i - 1] == ":") or (i + 1 < len(pieces) and pieces[i + 1] == ":")]
    twelve = any(p.lower() in ("am", "pm") for p in pieces)
    for i, code in zip(time, ("%I" if twelve else "%H", "%M", "%S")):
        codes[i] = code
    if len(time) > 3:
        raise SimplydataError(f'written_like="{example}": a time of day has at most hours, minutes and seconds.' + how)
    for i, p in enumerate(pieces):
        word = p.lower()
        if not p.isalpha():
            continue
        if word in _MONTH_WORDS:
            codes[i] = _MONTH_WORDS[word]
        elif word in _DAY_WORDS:
            codes[i] = _DAY_WORDS[word]
        elif word in ("am", "pm"):
            codes[i] = "%p"
    month_word = any(c in ("%B", "%b") for c in codes)
    date = [i for i in numbers if i not in time]
    years = [i for i in date if len(pieces[i]) == 4]
    if len(years) != 1:
        raise SimplydataError(f'written_like="{example}" needs the year written with four digits, like 2026 (or give '
                              'the % codes yourself, such as written_like="%d.%m.%y").' + how)
    codes[years[0]] = "%Y"
    rest = [i for i in date if i != years[0]]
    if month_word:
        if len(rest) != 1:
            raise SimplydataError(f'written_like="{example}" is not a date simplydata can read: with the month as a '
                                  "word, it needs one number for the day." + how)
        codes[rest[0]] = "%d"
    else:
        if len(rest) != 2:
            raise SimplydataError(f'written_like="{example}" is not a date simplydata can read: it needs a day, a month '
                                  "and a year." + how)
        above = [i for i in rest if int(pieces[i]) > 12]
        if len(above) != 1 or int(pieces[above[0]]) > 31:
            raise SimplydataError(f'In written_like="{example}" simplydata cannot tell the day from the month. Write '
                                  "the example with a day above 12, such as the 31st." + how)
        codes[above[0]] = "%d"
        codes[next(i for i in rest if i != above[0])] = "%m"
    layout = "".join(c if c is not None else p.replace("%", "%%") for p, c in zip(pieces, codes))
    try:
        _dt.datetime.strptime(example.strip(), layout.strip())
    except ValueError:
        raise SimplydataError(f'written_like="{example}" is not a date that exists (check the day and the month).'
                              + how) from None
    return layout


# ---------------------------------------------------------------- capitals_matter= and matches_pattern= (batch 2)
def _text_values(frame, column) -> list:
    """The different filled values of a text column, as Python text."""
    return [v for v in frame.filter(~nw.col(column).is_null()).select(nw.col(column).cast(nw.String))[column]
            .unique().to_list() if v is not None]


def _found_among(column, values, found) -> "nw.Expr":
    """column is one of the values for which found is True (narwhals is_in: pandas isin, Polars is_in)."""
    matches = [v for v, ok in zip(values, found) if ok]
    return nw.col(column).cast(nw.String).is_in(matches) if matches else nw.lit(False)


def casefold_matches(frame, column, test) -> "nw.Expr":
    """capitals_matter=False: one rule on both engines. pandas and Polars lowercase text differently outside plain
    English (the Greek final sigma, the German ß), so every value is compared after pandas str.casefold(), the
    Unicode case folding, for both engines: ΟΔΟΣ and οδος match, Straße and STRASSE match, Øl and øl match;
    the Turkish İ folds to i with a dot above, so İstanbul does not match istanbul. test() gets the folded
    values (a pandas Series) and gives True or False for each."""
    import pandas as pd

    values = _text_values(frame, column)
    found = test(pd.Series(values, dtype=object).str.casefold()).tolist() if values else []
    return _found_among(column, values, found)


def pattern_matches(frame, column, pattern, any_case, step) -> "nw.Expr":
    """matches_pattern=: Polars str.contains(pattern) for both engines (the Rust regex rules), so a pattern means
    the same on both: no look-ahead or look-behind, and "$" is the very end of the text. (?i) in front: capitals
    do not matter (Unicode simple case folding)."""
    example = _example(f'table.{step}("name", matches_pattern="^A")')
    if not isinstance(pattern, str) or not pattern:
        raise SimplydataError("matches_pattern= needs a regular expression in quotes." + example)
    import polars as pl

    values = _text_values(frame, column)
    try:
        found = pl.Series(values, dtype=pl.String).str.contains(("(?i)" if any_case else "") + pattern).to_list()
    except Exception as error:  # noqa: BLE001 - the parent's refusal, said in words
        raise SimplydataError(
            f'matches_pattern="{pattern}" is not a pattern simplydata can use ({str(error).splitlines()[0][:120]}). '
            "Patterns follow the Rust regex rules on every table: look-ahead (?=...) and look-behind (?<=...) are "
            "not allowed. For plain text use contains=, starts_with= or ends_with=." + example) from None
    return _found_among(column, values, found)


def reading_layouts(layout: str) -> tuple:
    """The layouts turn_into_dates(written_like=) tries: the one from the example, and the same with month and
    weekday names written the other way (full or short), so "31 May 2026" also reads "15 September 2026" and
    "15 Sep 2026" (pandas %b reads only short names, so both are tried, on both engines)."""
    other = layout.translate(str.maketrans({"B": "b", "b": "B", "A": "a", "a": "A"})) if "%" in layout else layout
    swapped = "".join(other[i] if layout[i - 1:i] == "%" else layout[i] for i in range(len(layout)))
    return (layout,) if swapped == layout else (layout, swapped)


TEST_RULES = ("grubbs", "dixon", "rosner")  # outlier tests, run in R (simplydata[r])


def _rule_of(step: str, rule, example: str):
    """Read test_method= for the outlier words: (how many, "IQR" or "standard deviations")."""
    text = str(rule).strip().lower().replace("×", "x") if isinstance(rule, str) else ""
    found = re.match(
        r"^(\d+(?:\.\d+)?)\s*(?:x|\*|times)?\s*(iqrs?|interquartile ranges?|standard deviations?|sds?|std)$", text
    )
    if not found or float(found.group(1)) <= 0:
        raise SimplydataError(
            f'.{step}() does not know test_method={_say(rule)}. You can use:\n'
            '  test_method="1.5 IQR"                 Tukey\'s rule, the usual one (the default)\n'
            '  test_method="3 IQR"                   only values very far out\n'
            '  test_method="3 standard deviations"   further than 3 standard deviations from the average\n'
            '  test_method="grubbs", "dixon" or "rosner"   outlier tests (R outliers, EnvStats)'
            + _example(example)
        )
    how = "IQR" if found.group(2).startswith(("iqr", "inter")) else "standard deviations"
    return float(found.group(1)), how


class RowWords:
    # ================================================================== helpers
    def _kind_of(self, column) -> str:
        return _kind(self._frame.schema[column])

    def _empty(self, column):
        return _empty_in(self._frame, column)

    def _count(self, expr) -> int:
        return _count_in(self._frame, expr)

    def _is_in(self, column, values):
        """column is one of values; whole numbers are checked as decimals in a decimal column (Polars needs it)."""
        if self._frame.schema[column].is_float():
            values = [float(v) if _is_number(v) else v for v in values]
        return nw.col(column).is_in(values)

    def _need_one_column(self, step: str, column, example: str):
        if not isinstance(column, str):
            raise SimplydataError(
                f".{step}() needs a column name in quotes as the first thing." + _example(example)
            )
        self._need_columns(column)

    def _need_text(self, step: str, column, example: str):
        """Friendly error unless the column holds text. Gives the column as text."""
        self._need_one_column(step, column, example)
        kind = self._kind_of(column)
        if kind == "text":
            return nw.col(column).cast(nw.String)
        if kind == "mixed":
            raise SimplydataError(
                f'"{column}" holds a mix of things. Turn it into text first with '
                f'table.turn_into_text("{column}").' + _example(example)
            )
        raise SimplydataError(
            f'.{step}() works on text, but "{column}" is a {kind} column.' + _example(example)
        )

    def _value_for(self, option: str, column: str, value, example: str):
        """Check one value against the column's kind and give it back ready to compare."""
        kind = self._kind_of(column)
        if kind == "number":
            if _is_number(value):
                return value
            if isinstance(value, str) and _looks_like_number(value):
                raise SimplydataError(
                    f'"{column}" is a number column, so write the number without quotes: '
                    f"{_is(option)}={value.strip()}" + _example(example)
                )
            raise SimplydataError(
                f'{_is(option)}= needs a number here, because "{column}" is a number column '
                f"(you gave {_say(value)})." + _example(example)
            )
        if kind == "text":
            if isinstance(value, str):
                return value
            hint = ""
            if _is_number(value):
                hint = (f' If "{column}" holds numbers written as text, first use '
                        f'table.turn_into_numbers("{column}").')
            raise SimplydataError(
                f'"{column}" is a text column, so {_is(option)}= needs text in quotes, like '
                f'{_is(option)}="{value}".{hint}' + _example('table.keep_rows_where("class", is_equal_to="A")')
            )
        if kind == "true/false":
            if isinstance(value, bool):
                return value
            raise SimplydataError(
                f'"{column}" is a true/false column, so {_is(option)}= needs True or False (no quotes).'
            )
        if kind == "date":
            return self._date_value(option, column, value)
        return value

    def _date_value(self, option: str, column: str, value):
        is_datetime = self._frame.schema[column] == nw.Datetime
        if isinstance(value, str):
            try:
                value = _dt.datetime.fromisoformat(value.strip())
            except ValueError:
                raise SimplydataError(
                    f'"{column}" is a date column. Write dates as year-month-day, like '
                    f'{_is(option)}="2026-03-15".'
                ) from None
        if hasattr(value, "to_pydatetime"):  # a pandas Timestamp
            value = value.to_pydatetime()
        if isinstance(value, _dt.datetime):
            return _on_clock_of(value, self._frame.schema[column]) if is_datetime else value.date()
        if isinstance(value, _dt.date):
            return _dt.datetime.combine(value, _dt.time()) if is_datetime else value
        raise SimplydataError(
            f'"{column}" is a date column, so {_is(option)}= needs a date like "2026-03-15" (you gave {_say(value)}).'
        )

    def _condition(self, step: str, column, options: dict, extra: tuple, capitals_matter=True):
        """Build the row condition for keep_rows_where()/remove_rows_where(). Gives (expression, words).

        capitals_matter=False compares text in small letters on both sides (pandas str.lower(), Polars
        str.to_lowercase()); a pattern gets (?i) in front, which pandas (Python re) and Polars (Rust regex) both
        read as "capitals do not matter"."""
        example = f'table.{step}("marks", is_above=50)'
        if extra:
            raise SimplydataError(
                f".{step}() needs the column and then one plain word saying which rows, "
                f'like is_above=50 or is_equal_to="A".' + _example(example)
            )
        if column is None:
            raise SimplydataError(f".{step}() needs a column name first." + _example(example))
        self._need_one_column(step, column, example)
        given = {k: v for k, v in options.items() if v is not _NOT_GIVEN}
        if not given:
            raise SimplydataError(
                f".{step}() needs one condition saying which rows. You can use: "
                + ", ".join(f"{_is(c)}=" for c in CONDITIONS)
                + f"\nor write the whole condition: table.{step}(\"marks > 50 and class == 'A'\")"
                + _example(example)
            )
        if len(given) > 1:
            names = " and ".join(f"{c}=" for c in given)
            raise SimplydataError(
                f".{step}() takes one condition at a time, but you gave {names}. "
                f"Write one step per condition, or use is_between=[low, high]."
                + _example(f'table.{step}("marks", is_at_least=40)   then   table.{step}("marks", is_at_most=80)')
            )
        option, value = next(iter(given.items()))
        kind = self._kind_of(column)
        col = nw.col(column)
        empty = self._empty(column)
        if not isinstance(capitals_matter, bool):
            raise SimplydataError("capitals_matter= should be True or False.")
        any_case = not capitals_matter
        if any_case and (kind != "text" or option not in CAPITALS_OPTIONS):
            what = f'"{column}" is a {kind} column' if kind != "text" else f"{_is(option)}= does not compare text"
            raise SimplydataError(
                "capitals_matter=False is for conditions on text (is_equal_to, is_not_equal_to, is_one_of, contains, "
                f"starts_with, ends_with, matches_pattern), and {what}."
                + _example(f'table.{step}("subject", is_equal_to="maths", capitals_matter=False)')
            )
        any_words = " (capitals do not matter)" if any_case else ""

        if option == "is_empty":
            if not isinstance(value, bool):
                raise SimplydataError(
                    "is_empty= needs True or False (no quotes)." + _example(f'table.{step}("marks", is_empty=True)')
                )
            return (empty if value else ~empty), ("is empty" if value else "is not empty")

        if option in ("after", "before"):
            if kind != "date":
                other = "above" if option == "after" else "below"
                raise SimplydataError(
                    f'{_is(option)}= is for dates, but "{column}" is a {kind} column. '
                    f"For numbers use {other}=." + _example(f'table.{step}("marks", {other}=50)')
                )
            given_time = isinstance(value, _dt.datetime) or hasattr(value, "to_pydatetime") or (
                isinstance(value, str) and any(sign in value for sign in (":", "T", " ")) and len(value.strip()) > 10
            )
            day = self._date_value(option, column, value)
            if self._frame.schema[column] == nw.Datetime and not given_time:
                # a day without a time: "after 1 March" starts on 2 March, "before 1 March" ends on 28 February
                start = day if option == "before" else day + _dt.timedelta(days=1)
                cond = col < start if option == "before" else col >= start
                words = f"is {option} {_say(day)}"
            else:
                cond = col > day if option == "after" else col < day
                words = f"is {option} {_say(day)}"
            return cond.fill_null(False) & ~empty, words

        if (option in COMPARE or option == "between") and kind not in ("number", "date"):
            raise SimplydataError(
                f'{_is(option)}= compares numbers or dates, but "{column}" is a {kind} column. '
                f"For text use is_equal_to=, is_one_of=, contains=, starts_with= or ends_with=."
                + _example(f'table.{step}("class", is_equal_to="A")')
            )

        if option in TEXT_ONLY:
            if kind != "text":
                raise SimplydataError(
                    f'{_is(option)}= looks inside text, but "{column}" is a {kind} column. '
                    f"For numbers use is_above=, is_below=, is_between= or is_equal_to=." + _example(example)
                )
            if not isinstance(value, str):
                raise SimplydataError(
                    f'{_is(option)}= needs text in quotes, like {_is(option)}="{value}".'
                    + _example(f'table.{step}("name", {_is(option)}="A")')
                )
            text = col.cast(nw.String)
            if option == "matches_pattern":
                # Polars str.contains(pattern) for both engines, so a pattern means the same on both
                cond = pattern_matches(self._frame, column, value, any_case, step)
                words = f"matches the pattern {_say(value)}"
            elif any_case:  # pandas str.casefold() for both engines (see casefold_matches)
                folded = value.casefold()
                test = {"contains": lambda f: f.str.contains(folded, regex=False),
                        "starts_with": lambda f: f.str.startswith(folded),
                        "ends_with": lambda f: f.str.endswith(folded)}[option]
                cond = casefold_matches(self._frame, column, test)
            elif option == "contains":
                cond = text.str.contains(value, literal=True)
            elif option == "starts_with":
                cond = text.str.starts_with(value)
            else:
                cond = text.str.ends_with(value)
            words = {"contains": f"contains {_say(value)}", "starts_with": f"starts with {_say(value)}",
                     "ends_with": f"ends with {_say(value)}"}.get(option, words if option == "matches_pattern" else "")
            words += any_words
        elif option in COMPARE:
            value = self._value_for(option, column, value, example)
            cond = {"above": col > value, "below": col < value,
                    "at_least": col >= value, "at_most": col <= value}[option]
            words = f"is {option.replace('_', ' ')} {_say(value)}"
        elif option == "between":
            if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)) or len(value) != 2:
                raise SimplydataError(
                    "is_between= needs two values in square brackets: the lowest and the highest."
                    + _example(f'table.{step}("marks", is_between=[40, 60])')
                )
            low, high = sorted(self._value_for(option, column, v, example) for v in value)
            cond, words = (col >= low) & (col <= high), f"is between {_say(low)} and {_say(high)}"
        elif option == "one_of":
            if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple, set)):
                raise SimplydataError(
                    "is_one_of= needs a list in square brackets. For a single value use is_equal_to=."
                    + _example(f'table.{step}("subject", is_one_of=["Maths", "Science"])')
                )
            values = [self._value_for(option, column, v, example) for v in value]
            if not values:
                raise SimplydataError(
                    "is_one_of= needs at least one value in the list."
                    + _example(f'table.{step}("subject", is_one_of=["Maths", "Science"])')
                )
            if any_case:
                folded = [v.casefold() for v in values]
                cond = casefold_matches(self._frame, column, lambda f: f.isin(folded))
            else:
                cond = self._is_in(column, values)
            words = "is one of " + ", ".join(_say(v) for v in values) + any_words
        else:  # equal_to, not_equal_to
            value = self._value_for(option, column, value, f'table.{step}("class", is_equal_to="A")')
            if any_case:
                same = casefold_matches(self._frame, column, lambda f: f == value.casefold())
                cond = same if option == "equal_to" else ~same
            else:
                cond = col == value if option == "equal_to" else col != value
            words = f"is {'' if option == 'equal_to' else 'not '}{_say(value)}{any_words}"
        return cond.fill_null(False) & ~empty, words

    def _only_in_rows(self, step: str, column: str, condition, run):
        """in_rows_where=: run the step, then keep its new values only in the rows where the condition is surely
        true (pandas df.loc[mask, column] = new, Polars pl.when(mask).then(new).otherwise(column)); every other
        row keeps its value. The condition is read before the step, on the values as they were."""
        import contextlib
        import io

        example = _example(f'table.{step}(..., in_rows_where="marks >= 50")', "school")
        if not isinstance(condition, str) or not condition.strip():
            raise SimplydataError('in_rows_where= takes a written condition in quotes, like in_rows_where="marks >= 50".'
                                  + example)
        reader = _ConditionReader(condition, self._frame, where="in_rows_where=")
        true, false = reader.read()
        try:
            mask = self._frame.select(true.fill_null(False).alias("_simplydata_in_"))["_simplydata_in_"]
        except Exception as error:  # noqa: BLE001 - shown to the user in plain words
            raise _condition_error(f'simplydata could not check the condition "{condition}" '
                                   f"({type(error).__name__}).") from None
        before = self._frame
        with contextlib.redirect_stdout(io.StringIO()):  # the step's own count is of every row; ours follows
            run()
        what, _ = self._history.pop()
        after = self._frame
        object.__setattr__(self, "_frame", before)
        old_kind, new_kind = _kind(before.schema[column]), _kind(after.schema[column])
        if old_kind != new_kind:
            raise SimplydataError(
                f'"{column}" holds {old_kind} values, but the new values are {new_kind}, and with in_rows_where= the '
                f"other rows keep their {old_kind} values: one column cannot hold both. Give a {old_kind} value, or "
                f"change the whole column first (turn_into_text, turn_into_numbers)." + example)
        old, inside = "_simplydata_old_", "_simplydata_in_"
        frame = after.with_columns(before[column].alias(old), mask.alias(inside))
        frame = frame.with_columns(nw.when(nw.col(inside)).then(nw.col(column)).otherwise(nw.col(old)).alias(column))
        a, b = nw.col(column), nw.col(old)
        same = (a == b).fill_null(False) | (a.is_null() & b.is_null())
        changed = _count_in(frame, nw.col(inside) & ~same)
        frame = frame.drop([old, inside])
        n = int(mask.sum())
        print(f'Changed {_cells(changed)} in "{column}", only in the {_rows(n)} where {condition}; the other '
              f"{_rows(len(before) - n)} keep their value.")
        unknown, note = empty_cells_note(before, true, false, reader.used)
        if unknown:
            print(note[:-1] + ", so those rows keep their value.")
        return self._change(f"{what}, only in rows where {condition}", frame)

    def _filter(self, what: str, keep_expr, kept_word: bool = True, note: str = ""):
        before = len(self._frame)
        new = self._frame.filter(keep_expr)
        after = len(new)
        if kept_word:
            print(f"Kept {after} of {_rows(before)}.")
        else:
            print(f"Removed {before - after} of {_rows(before)}. {_rows(after)} left.")
        if note:
            print(note)
        return self._change(what, new)

    def _report_failed(self, column: str, kind_word: str, new_values) -> int:
        """Print how many filled cells could not be changed, with a few of them as examples."""
        marked = self._frame.with_columns(new_values.alias(_NEW))
        failed = marked.filter(~self._empty(column) & nw.col(_NEW).is_null())
        n = len(failed)
        if n:
            samples = failed[column].cast(nw.String).unique(maintain_order=True).head(3).to_list()
            verb = "is" if n == 1 else "are"
            print(f"{_cells(n)} could not become {kind_word} and {verb} now empty, for example: "
                  + ", ".join(f'"{s}"' for s in samples))
        return n

    # ================================================================== looking
    @friendly
    def describe_columns(self):
        """Describe every column: its kind, empty cells, smallest, biggest and average.

        table.describe_columns()   (with sdata.get_example("marks"))
        """
        import pandas as pd

        rows_out = []
        for name in self._columns:
            kind = self._kind_of(name)
            empty = self._empty(name)
            filled = self._frame.filter(~empty)
            row = {"column": name, "kind": kind, "empty cells": self._count(empty),
                   "smallest": "", "biggest": "", "average": "", "different values": ""}
            col = nw.col(name)
            if len(filled) and kind == "number":
                low, high, mean = filled.select(col.min(), col.max().alias("b"), col.mean().alias("c")).row(0)
                row.update(smallest=_nice(low), biggest=_nice(high), average=_nice(float(mean)))
            elif len(filled) and kind == "date":
                low, high = filled.select(col.min(), col.max().alias("b")).row(0)
                row.update(smallest=_nice(low), biggest=_nice(high))
            if kind in ("text", "true/false", "mixed"):
                row["different values"] = str(filled.select(col.n_unique()).item() if len(filled) else 0)
            rows_out.append(row)
        rows, cols = self._frame.shape
        print(f"The table has {_rows(rows)} and {cols} columns.\n")
        print(pd.DataFrame(rows_out).to_string(index=False))
        return None

    @friendly(others={"pattern": "show"})
    def count_empty_cells_in(self, columns=None, show=None):
        """Show how many empty cells each column has, or only the columns you name.

        table.count_empty_cells_in()   (with sdata.get_example("shop"))
        table.count_empty_cells_in("sales") counts only that column, and
        table.count_empty_cells_in(["sales", "customers"]) only those columns.
        show="patterns" gives one row for each pattern of empty cells (which columns are empty
        together), with how many rows have it and how many cells it leaves empty, as R
        mice::md.pattern(): table.count_empty_cells_in(show="patterns")
        """
        if (isinstance(columns, str) and columns not in self._columns and show is None
                and columns.strip().lower() in ("patterns", "pattern")):
            columns, show = None, columns  # count_empty_cells_in("patterns"), the older way to write show=
        if columns is None:
            names = list(self._columns)
        else:
            names = list(dict.fromkeys([columns] if isinstance(columns, str) else _as_list(columns)))
            if not names:
                raise SimplydataError("count_empty_cells_in() got an empty list of columns. Name a column, for "
                                      'example table.count_empty_cells_in("sales"), or write '
                                      "table.count_empty_cells_in() for every column.")
            self._need_columns(*names)
        if show is not None:
            if not isinstance(show, str) or show.strip().lower() not in ("patterns", "pattern"):
                guess = suggest(show, self._columns, n=1) if isinstance(show, str) else []
                if isinstance(show, str) and show in self._columns:
                    raise SimplydataError(
                        f'show= takes only "patterns"; "{show}" is a column. To count its empty cells: '
                        f'table.count_empty_cells_in("{show}").')
                raise SimplydataError(
                    'count_empty_cells_in() takes show="patterns" for the patterns of empty cells (show= takes only '
                    f'"patterns", not {show!r}).\n'
                    "Write table.count_empty_cells_in() for a count in each column, or name the columns: "
                    'table.count_empty_cells_in("sales").'
                    + (f'\nDid you mean the column "{guess[0]}"? Its count: table.count_empty_cells_in("{guess[0]}").'
                       if guess else ""))
            return self._empty_patterns(names)
        counts = {name: self._count(self._empty(name)) for name in names}
        width = max((len(str(n)) for n in counts), default=0)
        print("Empty cells in each column:" if columns is None else
              f"Empty cells in {_rows(len(self._frame))}:")
        for name, n in counts.items():
            print(f"  {str(name).ljust(width)}  {n}")
        total = sum(counts.values())
        print(f"Total: {_cells(total)} empty." if total else "No empty cells.")
        return None

    def _empty_patterns(self, columns=None):
        """count_empty_cells_in(show="patterns"): the rows grouped by which cells are empty (narwhals group_by and
        len, as pandas df.isna().value_counts() and R mice::md.pattern()); columns= limits it to those columns."""
        import pandas as pd

        columns = list(self._columns) if columns is None else list(columns)
        if not columns or not len(self._frame):
            print("The table has no rows, so there are no patterns of empty cells.")
            return None
        marks = [f"__empty_{i}" for i in range(len(columns))]
        flags = self._frame.select(*[self._empty(c).fill_null(True).alias(m) for c, m in zip(columns, marks)])
        found = (flags.group_by(marks).agg(nw.len().alias("__rows")).to_pandas()
                 .reset_index(drop=True))
        found["__cells"] = found[marks].sum(axis=1).astype("int64")
        found = found.sort_values(["__cells", "__rows"], ascending=[True, False], kind="stable").reset_index(drop=True)
        out = pd.DataFrame({"rows with this pattern": found["__rows"].astype("int64")})
        for c, m in zip(columns, marks):
            out[c] = found[m].map({True: "empty", False: "filled"})
        out["empty cells"] = found["__cells"]
        per_column = {c: self._count(self._empty(c)) for c in columns}
        total = sum(per_column.values())
        n = len(out)
        complete = int(out.loc[out["empty cells"] == 0, "rows with this pattern"].sum())
        print(f"{n} pattern{'s' * (n != 1)} of empty cells in {_rows(len(self._frame))} (one row each; \"empty\" marks "
              f"the empty columns). {complete} row{'s have' if complete != 1 else ' has'} no empty cell.")
        print("Empty cells in each column: " + ", ".join(f"{c} {k}" for c, k in per_column.items())
              + f" ({_cells(total)} in all).")
        if n > 1:
            print("Why it matters: if the rows with empty cells differ from the others, leaving them out changes the "
                  "answer; table.explain(..., empty_cells=\"multiple imputation\") keeps them.")
        if self._frame.implementation.is_polars():
            import polars as pl

            out = pl.from_pandas(out)
        return self._new_table(nw.from_native(out, eager_only=True))

    # ================================================================== choosing columns
    def _columns_chosen(self, step: str, names: tuple, to, kind, starts_with, ends_with, contains, pattern,
                        capitals_matter=True):
        """The columns keep_columns()/remove_columns() mean, in table order or the order given.

        Gives (names, words for show_steps(), plain): plain is True for a list of names (the old way).
        """
        verb = step.split("_")[0]
        example = f'table.{step}("height")' if verb == "remove" else f'table.{step}("name", "marks")'
        run_example = f'table.{step}("temperature", to="wind_speed")'
        names = list(dict.fromkeys(_as_list(names)))
        ways = {"names": bool(names), "of_kind=": kind is not None, "starts_with=": starts_with is not None,
                "ends_with=": ends_with is not None, "contains=": contains is not None,
                "matches_pattern=": pattern is not None}
        given = [w for w, on in ways.items() if on]
        if to is not None and not names:
            raise SimplydataError(
                f"to= needs the first column's name before it, like {run_example}." + _example(run_example, "weather")
            )
        if not given:
            raise SimplydataError(
                f".{step}() needs the names of the columns to {verb}, or one of of_kind=, starts_with=, "
                "ends_with=, contains= or matches_pattern=." + _example(example)
                + _example(f'table.{step}(of_kind="number")')
            )
        if len(given) > 1:
            shown = " and ".join("column names" if w == "names" else w for w in given)
            raise SimplydataError(
                f".{step}() chooses columns one way at a time, but you gave {shown}. Write two steps: "
                "the second step works on what the first one left, so you get the columns that meet both."
                + _example(f'table.{step}(of_kind="number")   then   table.{step}(starts_with="wind")', "weather")
            )
        columns = self._columns
        if names:
            if not all(isinstance(n, str) for n in names):
                bad = next(n for n in names if not isinstance(n, str))
                hint = (f" For columns by their place use table.{verb}_columns_by_position({bad!r})."
                        if isinstance(bad, int) and not isinstance(bad, bool) else "")
                raise SimplydataError(f".{step}() needs column names in quotes (you gave {bad!r}).{hint}"
                                      + _example(example))
            if to is None:
                self._need_columns(*names)
                return names, ", ".join(names), True
            if len(names) != 1:
                raise SimplydataError(
                    "to= goes with one column name before it: the first column of the run, like "
                    f"{run_example}." + _example(run_example, "weather")
                )
            if not isinstance(to, str):
                raise SimplydataError(
                    f"to= takes the name of the last column of the run, in quotes (you gave {to!r}). "
                    f"For columns by their place use table.{verb}_columns_by_position(1, to=3)."
                    + _example(run_example, "weather")
                )
            first = names[0]
            self._need_columns(first, to)
            a, b = columns.index(first), columns.index(to)
            if b < a:
                raise SimplydataError(
                    f'"{to}" comes before "{first}" in the table. Write the column on the left first: '
                    f'table.{step}("{to}", to="{first}").\nColumns in order: ' + ", ".join(columns)
                )
            return columns[a:b + 1], f"{first} to {to}", False
        if kind is not None:
            wanted = _kind_choice(step, kind)
            chosen = [c for c in columns if self._kind_of(c) == wanted]
            if not chosen:
                there = {}
                for c in columns:
                    there.setdefault(self._kind_of(c), []).append(c)
                raise SimplydataError(
                    f"This table has no {wanted} columns. The kinds it has: "
                    + "; ".join(f'{k} ({", ".join(v)})' for k, v in there.items())
                    + f'\nFor example:  table.{step}(of_kind="{next(iter(there))}")'
                )
            return chosen, f"of kind {wanted}", False
        option, value = next((o, v) for o, v in (("starts_with", starts_with), ("ends_with", ends_with),
                                                 ("contains", contains), ("pattern", pattern)) if v is not None)
        if not isinstance(value, str) or not value:
            raise SimplydataError(f'{option}= needs some text in quotes, like {option}="wind".'
                                  + _example(f'table.{step}({option}="wind")', "weather"))
        if not isinstance(capitals_matter, bool):
            raise SimplydataError("capitals_matter= should be True or False.")
        # capitals_matter=False: names and text compared in small letters, a pattern with (?i) in front
        fold = (lambda t: str(t)) if capitals_matter else (lambda t: str(t).lower())
        value = value if option == "pattern" else fold(value)
        if option == "pattern":
            try:
                found = re.compile(value, 0 if capitals_matter else re.IGNORECASE)
            except re.error as error:
                raise SimplydataError(
                    f'matches_pattern= is a regular expression, and "{value}" is not one that works ({error}). '
                    "For plain text use contains=, starts_with= or ends_with="
                    + _example(f'table.{step}(matches_pattern="^wind_")', "weather")
                ) from None
            chosen = [c for c in columns if found.search(str(c))]
            words, none = f'whose names match the pattern "{value}"', f'matches the pattern "{value}"'
        elif option == "starts_with":
            chosen = [c for c in columns if fold(c).startswith(value)]
            words, none = f'whose names start with "{value}"', f'starts with "{value}"'
        elif option == "ends_with":
            chosen = [c for c in columns if fold(c).endswith(value)]
            words, none = f'whose names end with "{value}"', f'ends with "{value}"'
        else:
            chosen = [c for c in columns if value in fold(c)]
            words, none = f'whose names contain "{value}"', f'contains "{value}"'
        if not chosen:
            raise SimplydataError(
                f"No column name {none} ({'capital letters matter' if capitals_matter else 'in any capitals'})."
                "\nColumns you have: " + ", ".join(columns)
            )
        return chosen, words + ("" if capitals_matter else " (capitals do not matter)"), False

    @friendly(renamed={"kind": "of_kind", "pattern": "matches_pattern"}, pointers=CAPITALS_POINTERS)
    def keep_columns(self: _Same, *names, to=None, of_kind=None, starts_with=None, ends_with=None, contains=None,
                     matches_pattern=None, capitals_matter=True) -> _Same:
        """Keep only these columns: by name (in the order you list them), a run of names, or by kind.

        table.keep_columns("name", "marks")   (with sdata.get_example("marks"))
        table.keep_columns("hours", to="height") keeps a run of columns, both ends included;
        of_kind="number" (or "text", "date", "true/false", the kinds describe_columns() prints)
        keeps every column of that kind; starts_with=, ends_with=, contains= (plain text, capital
        letters matter) and matches_pattern= (a regular expression) choose by the column names.
        One way at a time; two steps one after the other keep the columns that meet both.
        capitals_matter=False finds the names in any capitals: keep_columns(starts_with="wind",
        capitals_matter=False) also keeps "Wind_speed".
        """
        if capitals_matter is not True and not any(v is not None for v in (starts_with, ends_with, contains,
                                                                           matches_pattern)):
            raise SimplydataError("capitals_matter= goes with starts_with=, ends_with=, contains= or matches_pattern=."
                                  + _example('table.keep_columns(starts_with="wind", capitals_matter=False)', "weather"))
        chosen, words, plain_names = self._columns_chosen("keep_columns", names, to, of_kind, starts_with, ends_with,
                                                          contains, matches_pattern, capitals_matter)
        if not plain_names:
            print(f"Kept {_columns_count(len(chosen))}: {', '.join(chosen)}.")
        return self._change("keep columns " + words, self._frame.select(chosen))

    @friendly(renamed={"kind": "of_kind", "pattern": "matches_pattern"}, pointers=CAPITALS_POINTERS)
    def remove_columns(self: _Same, *names, to=None, of_kind=None, starts_with=None, ends_with=None, contains=None,
                       matches_pattern=None, capitals_matter=True) -> _Same:
        """Remove these columns: by name, a run of names, or by kind.

        table.remove_columns("height")   (with sdata.get_example("marks"))
        The same ways as keep_columns: remove_columns("hours", to="marks"), remove_columns(of_kind="text"),
        remove_columns(starts_with="wind"), remove_columns(matches_pattern="^wind_"), and capitals_matter=False.
        """
        if capitals_matter is not True and not any(v is not None for v in (starts_with, ends_with, contains,
                                                                           matches_pattern)):
            raise SimplydataError("capitals_matter= goes with starts_with=, ends_with=, contains= or matches_pattern=."
                                  + _example('table.remove_columns(starts_with="wind", capitals_matter=False)',
                                             "weather"))
        chosen, words, plain_names = self._columns_chosen("remove_columns", names, to, of_kind, starts_with,
                                                          ends_with, contains, matches_pattern, capitals_matter)
        if len(chosen) == len(self._columns):
            raise SimplydataError(
                "That would remove every column. Keep at least one." + _example('table.remove_columns("height")')
            )
        if not plain_names:
            left = len(self._columns) - len(chosen)
            print(f"Removed {_columns_count(len(chosen))}: {', '.join(chosen)}. {_columns_count(left)} left.")
        return self._change("remove columns " + words, self._frame.drop(chosen))

    @friendly
    def rename_column(self: _Same, old=None, to=None) -> _Same:
        """Give a column a new name.

        table.rename_column("marks", to="score")   (with sdata.get_example("marks"))
        """
        example = 'table.rename_column("marks", to="score")'
        self._need_one_column("rename_column", old, example)
        if not isinstance(to, str) or not to.strip():
            raise SimplydataError(".rename_column() needs the new name in quotes after to=." + _example(example))
        if to == old:
            raise SimplydataError(f'The column is already called "{old}".')
        if to in self._columns:
            raise SimplydataError(
                f'There is already a column called "{to}". Pick another name, or remove that column first.'
                + _example(example)
            )
        return self._change(f'rename column "{old}" to "{to}"', self._frame.rename({old: to}))

    # ================================================================== choosing rows
    def _where(self, step: str, column, options: dict, extra: tuple, capitals_matter=True):
        """(condition, words, note) for keep_rows_where()/remove_rows_where(): a written condition or one plain word."""
        given = any(v is not _NOT_GIVEN for v in options.values())
        if capitals_matter is not True and not given:
            raise SimplydataError(
                "capitals_matter= goes with a plain word on a text column, such as is_equal_to= or contains=."
                + _example(f'table.{step}("subject", is_equal_to="maths", capitals_matter=False)'))
        if isinstance(column, str) and column not in self._frame.columns:
            text = column.strip()
            if text and not text.isidentifier():  # "marks > 50 and class == 'A'"
                if given or extra:
                    raise SimplydataError(
                        f".{step}() takes either a written condition or a column with one plain word, not both."
                        + _example(f'table.{step}("marks > 50")') + _example(f'table.{step}("marks", is_above=50)')
                    )
                true, note = self._read_condition(step, text)
                return true, text, note
        is_yes_no = isinstance(column, str) and column in self._frame.columns and self._kind_of(column) == "true/false"
        if is_yes_no and not given and not extra:  # keep_rows_where("passed")
            true, note = self._read_condition(step, f"`{column}`")
            return true, f"{column} is True", note
        cond, words = self._condition(step, column, options, extra, capitals_matter)
        return cond, f"{column} {words}", ""

    def _read_condition(self, step: str, text: str):
        """(where the condition is surely true, a note about rows it could not check)."""
        reader = _ConditionReader(text, self._frame)
        true, false = reader.read()
        try:
            self._count(true)  # check now that it can be worked out, so errors come at once
        except Exception as error:  # noqa: BLE001 - shown to the user in plain words
            raise _condition_error(
                f'simplydata could not check the condition "{text}" ({type(error).__name__}).'
            ) from None
        n, note = empty_cells_note(self._frame, true, false, reader.used)
        if n:
            gone = "they were left out" if step == "keep_rows_where" else "they were not removed"
            if n == 1:
                gone = "it was left out" if step == "keep_rows_where" else "it was not removed"
            note = note[:-1] + f", so {gone}."
        return true, note

    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                       "one_of": "is_one_of", "after": "is_after", "before": "is_before"}, pointers=CAPITALS_POINTERS)
    def keep_rows_where(self: _Same, column=None, *extra, is_above=_NOT_GIVEN, is_below=_NOT_GIVEN, is_at_least=_NOT_GIVEN,
                        is_at_most=_NOT_GIVEN, is_equal_to=_NOT_GIVEN, is_not_equal_to=_NOT_GIVEN, is_between=_NOT_GIVEN,
                        is_one_of=_NOT_GIVEN, contains=_NOT_GIVEN, starts_with=_NOT_GIVEN, ends_with=_NOT_GIVEN,
                        is_empty=_NOT_GIVEN, is_after=_NOT_GIVEN, is_before=_NOT_GIVEN, matches_pattern=_NOT_GIVEN,
                        capitals_matter=True) -> _Same:
        """Keep only the rows that match a condition.

        table.keep_rows_where("marks", is_above=50)   (with sdata.get_example("marks"))
        table.keep_rows_where("marks > 50 and class == 'A'")   a written condition
        Plain words: is_above, is_below, is_at_least, is_at_most, is_equal_to, is_not_equal_to,
        is_between=[low, high] (both ends included), is_one_of=[...], contains, starts_with,
        ends_with (capital letters matter), is_empty=True, and is_after= / is_before= for dates.
        Written conditions use == != < <= > >=, and, or, not, brackets, in [...], is empty;
        text and dates go in quotes. Empty cells only match is_empty / is empty.
        capitals_matter=False makes "maths", "Maths" and "MATHS" the same in the text words. One rule
        on both engines: pandas str.casefold(), the Unicode case folding (ΟΔΟΣ matches οδος, Straße
        matches STRASSE; the Turkish İ folds to i with a dot, so İstanbul does not match istanbul).
        matches_pattern= takes a regular expression, a pattern language for text, read by Polars
        str.contains on every table (no look-ahead or look-behind; "$" is the very end of the text):
          table.keep_rows_where("subject", is_equal_to="maths", capitals_matter=False)
          table.keep_rows_where("name", matches_pattern=r"^A")   names that start with A
        """
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, contains=contains,
                       starts_with=starts_with, ends_with=ends_with, is_empty=is_empty, after=is_after, before=is_before,
                       matches_pattern=matches_pattern)
        cond, words, note = self._where("keep_rows_where", column, options, extra, capitals_matter)
        return self._filter(f"keep rows where {words}", cond, note=note)

    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                       "one_of": "is_one_of", "after": "is_after", "before": "is_before"}, pointers=CAPITALS_POINTERS)
    def remove_rows_where(self: _Same, column=None, *extra, is_above=_NOT_GIVEN, is_below=_NOT_GIVEN, is_at_least=_NOT_GIVEN,
                          is_at_most=_NOT_GIVEN, is_equal_to=_NOT_GIVEN, is_not_equal_to=_NOT_GIVEN, is_between=_NOT_GIVEN,
                          is_one_of=_NOT_GIVEN, contains=_NOT_GIVEN, starts_with=_NOT_GIVEN, ends_with=_NOT_GIVEN,
                          is_empty=_NOT_GIVEN, is_after=_NOT_GIVEN, is_before=_NOT_GIVEN, matches_pattern=_NOT_GIVEN,
                          capitals_matter=True) -> _Same:
        """Remove the rows that match a condition (the opposite of keep_rows_where).

        table.remove_rows_where("subject", is_equal_to="English")   (with sdata.get_example("marks"))
        table.remove_rows_where("marks < 40 or hours < 2")   a written condition
        Same conditions as keep_rows_where; is_between=[low, high] includes both ends. A row whose
        cell is empty is never removed by a comparison on that cell (use is_empty=True).
        capitals_matter=False and matches_pattern= work as in keep_rows_where:
          table.remove_rows_where("subject", is_equal_to="english", capitals_matter=False)
        """
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, contains=contains,
                       starts_with=starts_with, ends_with=ends_with, is_empty=is_empty, after=is_after, before=is_before,
                       matches_pattern=matches_pattern)
        cond, words, note = self._where("remove_rows_where", column, options, extra, capitals_matter)
        return self._filter(f"remove rows where {words}", ~cond, kept_word=False, note=note)

    def _place_in_group(self, keys, from_end=False):
        """Each row's place inside its group, counting from 0 (from the last row with from_end=True): pandas
        groupby(keys, sort=False, dropna=False).cumcount(), Polars pl.int_range(pl.len()).over(keys). An empty
        cell in a group column is a group of its own, as in both packages."""
        native = self._frame.to_native()
        if self._frame.implementation.is_polars():
            import polars as pl

            place = pl.int_range(pl.len())
            if from_end:
                place = place.reverse()
            values = native.select(place.over(keys).alias("place"))["place"].to_numpy()
        else:
            values = native.groupby(keys, sort=False, dropna=False).cumcount(ascending=not from_end).to_numpy()
        return nw.new_series("_simplydata_place_", values, nw.Int64, backend=self._frame.implementation)

    def _keep_in_each_group(self, step, keys, keep, what):
        """Keep the rows whose place in their group passes keep(place); say how many groups and rows."""
        place = self._place_in_group(keys, from_end=step == "keep_last_rows")
        new = self._frame.with_columns(place).filter(keep(nw.col("_simplydata_place_"))).drop("_simplydata_place_")
        groups = len(self._frame.select(keys).unique())
        label = ", ".join(f'"{k}"' for k in keys)
        print(f"Kept {what} of each group of {label}: {len(new)} of {_rows(len(self._frame))} "
              f"({groups} group{'s' if groups != 1 else ''}).")
        return new

    @friendly(others={"how_many": "n"})
    def keep_first_rows(self: _Same, n=5, for_each_group_in=None) -> _Same:
        """Keep only the first rows, of the whole table or of each group.

        table.keep_first_rows(10)   (with sdata.get_example("marks"))
        for_each_group_in= keeps the first rows of each group, in the order the rows are in now, so
        after sort_by it keeps the best of each group (pandas groupby().head(), Polars group_by().head()):
          table.sort_by("marks", biggest_first=True)
          table.keep_first_rows(2, for_each_group_in="subject")   the two best marks in each subject
        The rows keep their order in the table.
        """
        example = "table.keep_first_rows(10)"
        n = _check_count("keep_first_rows", n, example)
        keys = self._for_each("keep_first_rows", for_each_group_in, None,
                              'table.keep_first_rows(2, for_each_group_in="subject")')
        before = len(self._frame)
        if keys:
            new = self._keep_in_each_group("keep_first_rows", keys, lambda place: place < n, f"the first {_rows(n)}")
            return self._change(f"keep the first {_rows(n)} of each group of {', '.join(keys)}", new)
        new = self._frame.head(n)
        print(f"Kept {len(new)} of {_rows(before)}.")
        return self._change(f"keep the first {_rows(n)}", new)

    @friendly(others={"how_many": "n"})
    def keep_last_rows(self: _Same, n=5, for_each_group_in=None) -> _Same:
        """Keep only the last rows, of the whole table or of each group.

        table.keep_last_rows(10)   (with sdata.get_example("marks"))
        for_each_group_in= keeps the last rows of each group (pandas groupby().tail(), Polars
        group_by().tail()); the rows keep their order in the table:
          table.keep_last_rows(1, for_each_group_in="name")   each child's last row
        """
        example = "table.keep_last_rows(10)"
        n = _check_count("keep_last_rows", n, example)
        keys = self._for_each("keep_last_rows", for_each_group_in, None,
                              'table.keep_last_rows(1, for_each_group_in="name")')
        before = len(self._frame)
        if keys:
            new = self._keep_in_each_group("keep_last_rows", keys, lambda place: place < n, f"the last {_rows(n)}")
            return self._change(f"keep the last {_rows(n)} of each group of {', '.join(keys)}", new)
        new = self._frame.tail(n)
        print(f"Kept {len(new)} of {_rows(before)}.")
        return self._change(f"keep the last {_rows(n)}", new)

    @friendly(renamed={"seed": "with_seed"}, others={"strata": "for_each_group_in", "by": "for_each_group_in",
                                                     "frac": "percent", "fraction": "percent"})
    def keep_random_rows(self: _Same, n=None, for_each_group_in=None, percent=None, with_seed=None) -> _Same:
        """Keep some rows picked at random; give a seed to get the same rows every time.

        table.keep_random_rows(10, with_seed=1)   (with sdata.get_example("marks"))
        for_each_group_in= picks the rows within each group (a stratified random sample):
        table.keep_random_rows(2, for_each_group_in="class", with_seed=1)   2 rows from each class
        percent=10 keeps 10 % of the rows (of each group, with for_each_group_in=), rounded as pandas
        rounds (half to even), and at least 1 row of every group: table.keep_random_rows(percent=50, for_each_group_in="class", with_seed=1)
        Underneath: pandas sample() and groupby().sample(), with random_state=with_seed.
        """
        step = "keep_random_rows"
        example = "table.keep_random_rows(10, with_seed=1)"
        percent_example = 'table.keep_random_rows(percent=10, for_each_group_in="class", with_seed=1)'
        if n is not None and percent is not None:
            raise SimplydataError("Give the number of rows or percent=, not both." + _example(percent_example))
        if percent is not None:
            if isinstance(percent, bool) or not isinstance(percent, numbers.Real) or not 0 < percent <= 100:
                raise SimplydataError("percent= is the share of rows to keep, in percent: a number above 0 and up to "
                                      f"100 (you gave {percent!r})." + _example(percent_example))
        else:
            n = _check_count(step, 5 if n is None else n, example)
        if with_seed is not None and (not isinstance(with_seed, numbers.Integral) or isinstance(with_seed, bool) or with_seed < 0):
            raise SimplydataError(
                "with_seed= needs a whole number, like with_seed=1. The same seed picks the same rows again."
                + _example(example)
            )
        seed = None if with_seed is None else int(with_seed)
        before = len(self._frame)
        said_seed = f" (seed {with_seed})" if with_seed is not None else ""
        if for_each_group_in is None:
            if percent is not None:
                # pandas sample(frac=) picks the rows, the same rule as with for_each_group_in= (rounded half to even)
                picked = self._frame.with_row_index("__i").select("__i").to_pandas().reset_index(drop=True)
                rows = sorted(int(i) for i in picked.sample(frac=percent / 100, random_state=seed).index)
                new = (self._frame.with_row_index("__simplydata_row").filter(nw.col("__simplydata_row").is_in(rows))
                       .drop("__simplydata_row"))
                print(f"Kept {len(new)} of {_rows(before)} ({percent:g} %, rounded by pandas sample(frac=)).")
                return self._change(f"keep {percent:g} % of the rows at random{said_seed}", new)
            if n > before:
                print(f"The table has only {_rows(before)}, so all of them are kept.")
                n = before
            new = self._frame.sample(n=n, seed=seed)
            print(f"Kept {len(new)} of {_rows(before)}.")
            return self._change(f"keep {n} random rows{said_seed}", new)
        if isinstance(for_each_group_in, str):
            groups = [for_each_group_in]
        elif isinstance(for_each_group_in, (list, tuple)):
            groups = list(for_each_group_in)
        else:
            groups = []
        if not groups or not all(isinstance(g, str) for g in groups):
            raise SimplydataError("for_each_group_in= needs a column name in quotes (or a list of them)."
                                  + _example('table.keep_random_rows(2, for_each_group_in="class", with_seed=1)'))
        self._need_columns(*groups)
        import pandas as pd

        df = self._frame.select(*groups).to_pandas().reset_index(drop=True)
        key = groups if len(groups) > 1 else groups[0]
        sizes = df.groupby(key, dropna=False).size()
        none = []
        whole = []
        if percent is not None:
            picked = df.groupby(key, dropna=False).sample(frac=percent / 100, random_state=seed)
            got = picked.groupby(key, dropna=False).size().reindex(sizes.index, fill_value=0)
            none = list(got.index[got == 0])
            if none:  # at least one row of every group: one more pandas draw in each group left empty
                rest = df[df.set_index(key).index.isin(none)]
                picked = pd.concat([picked, rest.groupby(key, dropna=False).sample(n=1, random_state=seed)])
        else:
            small = df.groupby(key, dropna=False)[groups[0]].transform("size") <= n
            picked = df[~small].groupby(key, dropna=False).sample(n=n, random_state=seed) \
                if (~small).any() else df.iloc[0:0]
            picked = pd.concat([picked, df[small]])
            whole = list(sizes.index[sizes <= n])
        rows = sorted(int(i) for i in picked.index)
        new = (self._frame.with_row_index("__simplydata_row").filter(nw.col("__simplydata_row").is_in(rows))
               .drop("__simplydata_row"))
        kept = new.select(*groups).to_pandas().groupby(key, dropna=False).size()
        label = ", ".join(f'"{g}"' for g in groups)
        if percent is None:
            print(f"Kept {n} random row{'s' * (n != 1)} from each group of {label} ({len(new)} of {_rows(before)}; "
                  "pandas groupby().sample()).")
            if whole:
                shown = ", ".join(_say_key(w) for w in whole[:6]) + (" ..." if len(whole) > 6 else "")
                print(f"Note: {len(whole)} group{'s have' if len(whole) != 1 else ' has'} {n} row{'s' * (n != 1)} or "
                      "fewer, so all "
                      f"{'their' if len(whole) != 1 else 'its'} rows are kept: {shown}.")
        else:
            got = kept.reindex(sizes.index, fill_value=0)  # by position: a group named by an empty cell has no label
            parts = ", ".join(f"{_say_key(k)} {int(v)} of {int(n_rows)}"
                              for k, v, n_rows in list(zip(sizes.index, got.to_numpy(), sizes.to_numpy()))[:8])
            print(f"Kept {percent:g} % of each group of {label}, rounded, at least 1 row each ({len(new)} of "
                  f"{_rows(before)}; pandas groupby().sample(frac=)): {parts}{' ...' if len(kept) > 8 else ''}.")
            if none:
                print(f"Note: {len(none)} group{'s were' if len(none) != 1 else ' was'} too small for {percent:g} % to "
                      "give a row, so one row was picked from each.")
        if percent is not None:
            what = f"keep {percent:g} % of each group of {label} at random"
        else:
            what = f"keep {n} random rows from each group of {label}"
        return self._change(what + said_seed, new)

    @friendly(others={"subset": "columns"})  # pandas drop_duplicates(subset=)
    def remove_duplicate_rows(self: _Same, columns=None, keep="first") -> _Same:
        """Remove rows that repeat an earlier row, or that repeat it in the columns you name.

        table.remove_duplicate_rows(columns=["name"])   (with sdata.get_example("marks"))
        keep= says which copy stays: "first" (the normal choice), "last", or "none" (every row that
        repeats goes, the first copy too), as pandas drop_duplicates(keep=) and Polars unique(keep=):
          table.remove_duplicate_rows(columns=["name"], keep="last")
        Look at the repeats first with show_duplicate_rows().
        """
        if keep is False:  # pandas drop_duplicates(keep=False)
            raise SimplydataError("keep=False is how pandas writes keep=\"none\" (every copy goes). "
                                  'Write table.remove_duplicate_rows(keep="none").')
        self._check_choice("remove_duplicate_rows", "keep", keep, ["first", "last", "none"])
        if columns is None:
            subset, what = None, "remove duplicate rows"
        else:
            subset = [columns] if isinstance(columns, str) else _as_list([columns])
            if not subset:
                raise SimplydataError(
                    "columns= needs one or more column names."
                    + _example('table.remove_duplicate_rows(columns=["name"])')
                )
            self._need_columns(*subset)
            what = "remove rows that repeat " + ", ".join(subset)
        before = len(self._frame)
        new = self._frame.unique(subset=subset, keep=keep, maintain_order=True)
        print(f"Removed {before - len(new)} of {_rows(before)}. {_rows(len(new))} left."
              + {"first": "", "last": " The last copy of each stayed.",
                 "none": " Every row that repeats was removed, the first copy too."}[keep])
        if subset is None and len(new) == before:
            self._near_duplicates_note()
        if keep != "first":
            what += f" (keep {keep})"
        return self._change(what, new)

    def _near_duplicates_note(self):
        """remove_duplicate_rows() removed nothing: say so, and name the columns in which rows that are otherwise the
        same differ (each column left out once, with the same unique() call; only counts, on tables of a modest size)."""
        columns = self._columns
        rows = len(self._frame)
        differing = []
        if 2 <= len(columns) <= 50 and rows * len(columns) <= 2_000_000:
            for column in columns:
                others = [c for c in columns if c != column]
                n = rows - len(self._frame.unique(subset=others, keep="first", maintain_order=True))
                if n:
                    differing.append((column, n))
        if not differing:
            print("No row repeats an earlier row exactly, so nothing was removed.")
            return
        listed = ", ".join(f'"{c}" ({_rows(n)})' for c, n in differing)
        column = differing[0][0]
        keep = ", ".join(f'"{c}"' for c in columns if c != column)
        print(f"Note: no row repeats an earlier row exactly, but some rows repeat an earlier row in every column except "
              f"one: {listed}. If those are duplicates for you, name the columns that must match, for example "
              f"table.remove_duplicate_rows(columns=[{keep}]).")

    @friendly
    def repeat_each_row_by(self: _Same, column=None) -> _Same:
        """Repeat each row as many times as the count in a column: one row per thing counted.

        table.repeat_each_row_by("count")   (with sdata.table({"answer": ["yes", "no"], "count": [12, 5]}))
        A table of counts (one row per group, with how many there are) becomes one row per person
        or thing, as many words need. The count column is left out afterwards, since each row now
        stands for one; a row with a count of 0 is left out. The counts must be whole numbers of
        0 or more, with no empty cells. As pandas df.loc[df.index.repeat(df["count"])] and Polars
        df.select(pl.exclude("count").gather(pl.int_range(pl.len()).repeat_by("count").explode().drop_nulls())).
        Undo with table.undo().
        """
        example = 'table.repeat_each_row_by("count")'
        if not isinstance(column, str):
            raise SimplydataError("repeat_each_row_by() needs the name of the column that holds the counts, in quotes."
                                  + f"\nFor example:  {example}   (with sdata.table({COUNTS_EXAMPLE}))")
        self._need_columns(column)
        series = self._frame[column]
        if series.dtype == nw.Boolean:
            raise SimplydataError(f'"{column}" holds True and False, not counts. repeat_each_row_by() needs a column '
                                  "of whole numbers (0 or more), one count per row.")
        if not series.dtype.is_numeric():
            raise SimplydataError(f'"{column}" holds text, not counts. repeat_each_row_by() needs a column of whole '
                                  "numbers (0 or more), one count per row.")
        if series.null_count():
            empty = series.null_count()
            raise SimplydataError(f'"{column}" has {_rows_word(empty).replace("row", "empty cell")}, so simplydata '
                                  "cannot tell how often to repeat those rows. Fill them first (fill_empty_cells_in) or remove them "
                                  f'(remove_rows_with_empty_cells_in("{column}")).')
        counts = series.to_numpy().astype(float)
        if not np.isfinite(counts).all() or (counts != np.round(counts)).any():
            bad = next(v for v in counts if not np.isfinite(v) or v != round(v))
            raise SimplydataError(f'"{column}" holds {_nice(bad)}, not a whole number. A row can only be repeated a '
                                  "whole number of times; check the counts (were they rounded, or are they shares?).")
        if (counts < 0).any():
            raise SimplydataError(f'"{column}" holds {_nice(float(counts.min()))}, below 0. A row cannot be repeated '
                                  "fewer than 0 times; check the counts.")
        before, total = len(self._frame), int(counts.sum())
        # NumPy repeat of the row positions, then the rows taken by position (narwhals, pandas or Polars)
        positions = np.repeat(np.arange(before), counts.astype(np.int64))
        new = self._frame[positions.tolist()].drop(column)
        zero = int(np.sum(counts == 0))
        print(f'Repeated {before:,} row{"s" if before != 1 else ""} into {total:,} row{"s" if total != 1 else ""} by '
              f'"{column}".')
        print(f'The column "{column}" is left out: each row now stands for one.'
              + (f" {zero} row{'s' if zero != 1 else ''} with a count of 0 {'are' if zero != 1 else 'is'} left out."
                 if zero else ""))
        return self._change(f'repeat each row by "{column}"', new)

    # ================================================================== empty cells
    @friendly
    def remove_rows_with_empty_cells_in(self: _Same, column=None) -> _Same:
        """Remove rows with an empty cell (in any column, or only in the column you name).

        table.remove_rows_with_empty_cells_in("sales")   (with sdata.get_example("shop"))
        """
        if column is None:
            names, what = self._columns, "remove rows with an empty cell"
        else:
            names = [column] if isinstance(column, str) else _as_list([column])
            self._need_columns(*names)
            what = f"remove rows where {', '.join(names)} is empty"
        any_empty = nw.any_horizontal(*[self._empty(c) for c in names], ignore_nulls=True)
        return self._filter(what, ~any_empty.fill_null(False), kept_word=False)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def fill_empty_cells_in(self: _Same, column=None, with_value=None, with_the=None, sorted_by=None, for_each_group_in=None,
                            in_rows_where=None, from_column=None) -> _Same:
        """Fill the empty cells of a column with a value, or with the average, median, value above or value below.

        table.fill_empty_cells_in("customers", with_the="median")   (with sdata.get_example("shop"))
        with_the="line between neighbours" fills each gap on the straight line between the
        filled cells just before and just after it (linear interpolation). It follows the rows
        in table order, or sorted_by= a column of numbers or dates (then the line is spaced by
        those values, so a missing day counts as one day); for_each_group_in= fills each group on its
        own. Empty cells at the start or end have only one neighbour, so they stay empty.
          table.fill_empty_cells_in("sales", with_the="line between neighbours", sorted_by="date", for_each_group_in="shop")
        with_the="curve between neighbours" fills them on a smooth curve through the filled
        cells instead (a natural cubic spline, as R zoo::na.spline(method = "natural")), and
        with_the="curve without overshoot" on a smooth curve that never goes above or below
        its neighbours (PCHIP); both take sorted_by= and for_each_group_in= the same way.
        in_rows_where= fills only the empty cells of the rows that meet a written condition (the
        average or median is still that of the whole column):
          table.fill_empty_cells_in("customers", with_value=0, in_rows_where="shop == 'Northgate'")
        from_column= fills each empty cell with the value of another column in the same row, such as
        a phone number from the mobile number; filled cells never change (pandas
        df["phone"].fillna(df["mobile"]), Polars pl.coalesce("phone", "mobile")):
          table.fill_empty_cells_in("phone", from_column="mobile")
        """
        example = 'table.fill_empty_cells_in("marks", with_the="average")'
        self._need_one_column("fill_empty_cells_in", column, example)
        if in_rows_where is not None:
            return self._only_in_rows("fill_empty_cells_in", column, in_rows_where, lambda: self.fill_empty_cells_in(
                column, with_value=with_value, with_the=with_the, sorted_by=sorted_by,
                for_each_group_in=for_each_group_in, from_column=from_column))
        if from_column is not None:
            return self._fill_from_column(column, from_column, with_value, with_the, sorted_by, for_each_group_in)
        if (with_value is None) == (with_the is None):
            raise SimplydataError(
                ".fill_empty_cells_in() needs exactly one of with_value= or with_the=."
                + _example('table.fill_empty_cells_in("marks", with_value=0)')
                + _example(example)
            )
        if with_the is not None:
            choice = str(with_the).strip().lower().replace("_", " ").replace("neighbors", "neighbours")
            if choice in BETWEEN_CHOICES:
                return self._fill_by_line(column, sorted_by, for_each_group_in, choice)
        if sorted_by is not None or for_each_group_in is not None:
            raise SimplydataError(
                'sorted_by= and for_each_group_in= go with with_the="line between neighbours" (or "curve between neighbours").'
                + _example('table.fill_empty_cells_in("sales", with_the="line between neighbours", sorted_by="date")',
                           "shop")
            )
        empty = self._empty(column)
        kind = self._kind_of(column)
        col = nw.col(column)
        if with_value is not None:
            value = self._value_for("with_value", column, with_value, 'table.fill_empty_cells_in("marks", with_value=0)')
            new_col, how = nw.when(empty).then(nw.lit(value)).otherwise(col), _say(value)
        else:
            self._check_choice("fill_empty_cells_in", "with_the", choice, FILL_CHOICES)
            if choice in ("average", "median"):
                if kind != "number":
                    raise SimplydataError(
                        f'with_the="{choice}" needs numbers, but "{column}" is a {kind} column. '
                        f'Try with_the="value above" or with_value= instead.'
                        + _example('table.fill_empty_cells_in("subject", with_the="value above")')
                    )
                filled = self._frame.filter(~empty)
                if len(filled) == 0:
                    raise SimplydataError(f'"{column}" has no numbers at all, so there is no {choice} to fill with.')
                value = filled.select(col.mean() if choice == "average" else col.median()).item()
                new_col, how = nw.when(empty).then(nw.lit(float(value))).otherwise(col), f"the {choice}"
            else:
                strategy = "forward" if choice == "value above" else "backward"
                new_col, how = nw.when(~empty).then(col).fill_null(strategy=strategy), f"the {choice}"
        before = self._count(empty)
        new = self._frame.with_columns(new_col.alias(column))
        after = _count_in(new, _empty_in(new, column))
        print(f"Filled {_cells(before - after)} in {column}."
              + (f" {_cells(after)} stayed empty (nothing to copy from)." if after else ""))
        return self._change(f"fill empty cells in {column} with {how}", new)

    def _fill_from_column(self, column, from_column, with_value, with_the, sorted_by, for_each):
        """fill_empty_cells_in(column, from_column=): pandas fillna(df[other]), Polars pl.coalesce(column, other)."""
        example = _example('table.fill_empty_cells_in("phone", from_column="mobile")')
        if any(v is not None for v in (with_value, with_the, sorted_by, for_each)):
            raise SimplydataError("from_column= is one way to fill, so leave out with_value=, with_the=, sorted_by= "
                                  "and for_each_group_in=." + example)
        self._need_one_column("fill_empty_cells_in", from_column, 'table.fill_empty_cells_in("phone", '
                                                                  'from_column="mobile")')
        if from_column == column:
            raise SimplydataError("from_column= needs another column than the one to fill." + example)
        here, there = self._kind_of(column), self._kind_of(from_column)
        if here != there:
            raise SimplydataError(f'"{column}" holds {here} values but "{from_column}" holds {there} values, so one '
                                  "cannot fill the other. Make them the same kind first (turn_into_numbers, "
                                  "turn_into_text, turn_into_dates)." + example)
        empty, source_empty = self._empty(column), self._empty(from_column)
        new_col = nw.when(empty & ~source_empty).then(nw.col(from_column)).otherwise(nw.col(column))
        before = self._count(empty)
        new = self._frame.with_columns(new_col.alias(column))
        after = _count_in(new, _empty_in(new, column))
        print(f'Filled {_cells(before - after)} in {column} from "{from_column}".'
              + (f" {_cells(after)} stayed empty ({from_column} is empty there too)." if after else ""))
        return self._change(f"fill empty cells in {column} from {from_column}", new)

    def _fill_by_line(self, column, sorted_by, for_each, choice="line between neighbours"):
        """fill_empty_cells_in(with_the="line between neighbours"): see line_between_neighbours().

        with_the="curve between neighbours" / "curve without overshoot": see
        between.curve_between_neighbours() (natural cubic spline / PCHIP through the filled cells).
        """
        from .._stats import line_between_neighbours

        example = f'table.fill_empty_cells_in("sales", with_the="{choice}", sorted_by="date")'
        kind = self._kind_of(column)
        if kind != "number":
            raise SimplydataError(
                f'with_the="{choice}" needs numbers, but "{column}" is a {kind} column. '
                f'Try with_the="value above" or with_value= instead.' + _example(example, "shop")
            )
        keys = [for_each] if isinstance(for_each, str) else list(for_each or [])
        if for_each is not None and (not keys or not all(isinstance(k, str) for k in keys)):
            raise SimplydataError("for_each_group_in= should be a column name or a list of column names." + _example(example, "shop"))
        if sorted_by is not None and not isinstance(sorted_by, str):
            raise SimplydataError("sorted_by= should be one column name, such as a date." + _example(example, "shop"))
        self._need_columns(*keys, *([sorted_by] if sorted_by else []))
        frame = self._frame
        values = frame[column].cast(nw.Float64).to_numpy()
        x = None
        if sorted_by is not None:
            by_kind = self._kind_of(sorted_by)
            if by_kind not in ("number", "date"):
                raise SimplydataError(
                    f'sorted_by= puts the rows in order of numbers or dates, but "{sorted_by}" is a {by_kind} column.'
                    + _example(example, "shop")
                )
            raw = frame[sorted_by].to_numpy()
            if by_kind == "date":
                raw = raw.astype("datetime64[us]")
                missing = raw != raw  # NaT
                x = raw.astype("int64").astype(float) / 86_400_000_000  # in days
                x[missing] = float("nan")
            else:
                x = frame[sorted_by].cast(nw.Float64).to_numpy()
        groups = None
        if keys:
            columns = [frame[k].to_list() for k in keys]
            place = {}
            groups = [place.setdefault(key, len(place)) for key in zip(*columns)]
        if choice == "line between neighbours":
            new_values = line_between_neighbours(values, x, groups)
        else:
            from .between import curve_between_neighbours

            how = "smooth curve" if choice == "curve between neighbours" else "curve without overshoot"
            new_values = curve_between_neighbours(values, x, groups, how)
        before = self._count(self._empty(column))
        new = frame.with_columns(nw.new_series(column, new_values, nw.Float64, backend=frame.implementation))
        after = _count_in(new, _empty_in(new, column))
        order = f" in order of {sorted_by}" if sorted_by else " in table order"
        each = f", for each {', '.join(keys)} on its own" if keys else ""
        said = {"line between neighbours": "on the line between neighbours",
                "curve between neighbours": "on a smooth curve through the filled cells (a natural cubic spline, "
                                            'as R zoo::na.spline(method = "natural"))',
                "curve without overshoot": "on a smooth curve through the filled cells that never overshoots "
                                           "its neighbours (PCHIP)"}[choice]
        print(f"Filled {_cells(before - after)} in {column} {said}{order}{each}.")
        no_place = _count_in(frame, self._empty(column) & self._empty(sorted_by)) if sorted_by else 0
        if after - no_place:
            ends = "the start or end of a group" if keys else "the start or end"
            n = after - no_place
            print(f"Note: {_cells(n)} stayed empty: {'it is' if n == 1 else 'they are'} at {ends}, "
                  "with a filled neighbour on one side only.")
        if no_place:
            print(f"Note: {_cells(no_place)} stayed empty because {sorted_by} is empty in "
                  f"{'that row' if no_place == 1 else 'those rows'}.")
        what = f"fill empty cells in {column} with the {choice}{order}{each}"
        return self._change(what, new)

    # ================================================================== fixing columns
    @friendly
    def turn_into_numbers(self: _Same, column=None) -> _Same:
        """Turn a column into numbers; cells that are not numbers become empty.

        table.turn_into_numbers("marks")   (with sdata.get_example("marks"))
        Understands 12.5, -3, 1e3, 1 200 and 1,200 (thousands) and 12,5 (decimal comma).
        """
        example = 'table.turn_into_numbers("marks")'
        self._need_one_column("turn_into_numbers", column, example)
        kind = self._kind_of(column)
        col = nw.col(column)
        if kind == "number":
            print(f"{column} is already numbers.")
            return self
        if kind == "true/false":
            new = self._frame.with_columns(col.cast(nw.Int64))
            print(f"{column} is now numbers: True is 1 and False is 0.")
            return self._change(f"turn {column} into numbers", new)
        if kind == "date":
            raise SimplydataError(f'"{column}" is a date column, so it cannot become numbers.' + _example(example))
        text = col.cast(nw.String).str.replace_all(r"\s", "", literal=False)
        text = nw.when(text.str.contains(_THOUSANDS).fill_null(False)).then(
            text.str.replace_all(",", "", literal=True)
        ).otherwise(
            nw.when(text.str.contains(_DECIMAL_COMMA).fill_null(False)).then(
                text.str.replace(",", ".", literal=True)
            ).otherwise(text)
        )
        number = nw.when(text.str.contains(_NUMBER).fill_null(False)).then(text).cast(nw.Float64)
        values = self._frame.select(number.alias(column))[column]
        self._report_failed(column, "numbers", values)
        print(f"{column} is now numbers.")
        return self._change(f"turn {column} into numbers", self._frame.with_columns(values))

    @friendly(others={"format": "written_like", "date_format": "written_like"})
    def turn_into_dates(self: _Same, column=None, order=None, written_like=None) -> _Same:
        """Turn a column into dates; cells that are not dates become empty.

        table.turn_into_dates("year")   (with sdata.get_example("growth"))
        Understands 2026-03-15, 15/03/2026, 15.03.2026, 15 March 2026, March 15, 2026, 2026-03 and 2026.
        03/04/2026 is read day first, as 3 April (month first only when day first cannot work).
        order= says how the dates are written, so nothing is guessed: "day month year"
        (15/03/2026), "month day year" (03/15/2026) or "year month day" (2026/03/15).
          table.turn_into_dates("when", order="month day year")
        written_like= gives an example date written the way the column writes them, so any layout
        can be read: written_like="03/15/2026 14:30" (the day must be above 12, so it is not taken for
        the month). Month names are read written out or short ("September" and "Sep") whichever the
        example uses. Cells written another way become empty, and the sentence counts them. % codes
        (written_like="%d.%m.%y") work too. As pandas pd.to_datetime(format="%m/%d/%Y %H:%M") and
        Polars str.strptime(pl.Datetime, "%m/%d/%Y %H:%M"):
          table.turn_into_dates("when", written_like="03/15/2026")
        """
        example = 'table.turn_into_dates("year")'
        self._need_one_column("turn_into_dates", column, example)
        layout = None
        if written_like is not None:
            if order is not None:
                raise SimplydataError("Give order= or written_like=, not both: written_like= already says the order.")
            layout = format_from_example(written_like)
        if order is not None:
            if isinstance(order, str):
                order = " ".join(order.lower().replace(",", " ").replace("-", " ").split())
            self._check_choice("turn_into_dates", "order", order, DATE_ORDERS)
        kind = self._kind_of(column)
        col = nw.col(column)
        if kind == "date":
            print(f"{column} is already dates.")
            return self
        if kind == "true/false":
            raise SimplydataError(f'"{column}" is a true/false column, so it cannot become dates.')
        if kind == "number" and not self._frame.schema[column].is_integer():
            raise SimplydataError(
                f'turn_into_dates() can turn whole years like 2026 into dates, but "{column}" has decimals.'
                + _example(example, "growth")
            )
        text = col.cast(nw.String).str.strip_chars()
        text = nw.when(text.str.contains(r"^\d{4}$").fill_null(False)).then(text + nw.lit("-01-01")).otherwise(
            nw.when(text.str.contains(r"^\d{4}-\d{1,2}$").fill_null(False)).then(text + nw.lit("-01")).otherwise(text)
        )
        cleaned = self._frame.select(text.alias(column))[column]
        formats = reading_layouts(layout) if layout is not None else DATE_FORMATS if order is None else DATE_ORDERS[order]
        values = nw.from_native(_parse_dates(cleaned.to_native(), formats), series_only=True).alias(column)
        self._report_failed(column, "dates", values)
        read_as = "" if order is None else f" (read as {order})"
        if layout is not None:
            read_as = f" (read as {layout})"
        print(f"{column} is now dates{read_as}.")
        what = f"turn {column} into dates" + ("" if order is None else f', order="{order}"') + (
            "" if layout is None else f', written_like="{written_like}"')
        return self._change(what, self._frame.with_columns(values))

    @friendly(others={"format": "written_like", "date_format": "written_like"})
    def turn_into_text(self: _Same, column=None, written_like=None) -> _Same:
        """Turn a column into text.

        table.turn_into_text("month_number")   (with sdata.get_example("weather"))
        Dates become text such as 2026-03-15. written_like= gives an example date written the way
        you want them: written_like="31.12.2026" gives 15.03.2026 for 15 March, and
        written_like="March 31, 2026" gives March 15, 2026 (the day must be above 12, so it is not
        taken for the month; days and months are written with two digits, 03). As pandas
        dt.strftime("%d.%m.%Y") and Polars dt.to_string("%d.%m.%Y"); % codes work too:
          table.turn_into_text("date", written_like="31.12.2026")   (with sdata.get_example("shop"))
        """
        example = 'table.turn_into_text("month_number")'
        self._need_one_column("turn_into_text", column, example)
        kind = self._kind_of(column)
        dtype = self._frame.schema[column]
        col = nw.col(column)
        empty = self._empty(column)
        if written_like is not None:
            if kind != "date":
                raise SimplydataError(f'written_like= is for dates, and "{column}" holds {kind} values.'
                                      + _example('table.turn_into_text("date", written_like="31.12.2026")', "shop"))
            layout = format_from_example(written_like)
            text = col.dt.to_string(layout)  # pandas dt.strftime(layout), Polars dt.to_string(layout)
            new = self._frame.with_columns(nw.when(~empty).then(text).alias(column))
            first = new.filter(~nw.col(column).is_null())
            shown = f', such as "{first[column].item(0)}"' if len(first) else ""
            print(f"{column} is now text, written like {written_like}{shown} ({layout}).")
            return self._change(f'turn {column} into text, written like "{written_like}"', new)
        if dtype == nw.String:
            print(f"{column} is already text.")
            return self
        if kind == "true/false":
            text = nw.when(col).then(nw.lit("True")).otherwise(nw.lit("False"))
        elif kind == "date":
            fmt = "%Y-%m-%d"
            filled = self._frame.filter(~empty)
            if dtype == nw.Datetime and len(filled):
                has_time = filled.select(((col.dt.hour() + col.dt.minute() + col.dt.second()) > 0).any()).item()
                if has_time:
                    fmt = "%Y-%m-%d %H:%M:%S"
            text = col.dt.to_string(fmt)
        else:
            text = col.cast(nw.String)
        new = self._frame.with_columns(nw.when(~empty).then(text).alias(column))
        print(f"{column} is now text.")
        return self._change(f"turn {column} into text", new)

    def _text_step(self, step: str, column, what: str, change):
        text = self._need_text(step, column, f'table.{step}("name")')
        return self._change(what, self._frame.with_columns(change(text).alias(column)))

    @friendly
    def turn_into_lowercase(self: _Same, column=None) -> _Same:
        """Write all the text in a column in small letters.

        table.turn_into_lowercase("name")   (with sdata.get_example("marks"))
        """
        return self._text_step("turn_into_lowercase", column, f"turn {column} into lowercase", lambda t: t.str.to_lowercase())

    @friendly
    def turn_into_uppercase(self: _Same, column=None) -> _Same:
        """Write all the text in a column in capital letters.

        table.turn_into_uppercase("name")   (with sdata.get_example("marks"))
        """
        return self._text_step("turn_into_uppercase", column, f"turn {column} into uppercase", lambda t: t.str.to_uppercase())

    @friendly
    def remove_extra_spaces_in(self: _Same, column=None) -> _Same:
        """Remove spaces at the start and end of the text, and double spaces inside it.

        table.remove_extra_spaces_in("name")   (with sdata.get_example("marks"))
        """
        return self._text_step(
            "remove_extra_spaces_in", column, f"remove extra spaces in {column}",
            lambda t: t.str.replace_all(r"\s+", " ", literal=False).str.strip_chars(),
        )

    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                       "one_of": "is_one_of", "after": "is_after", "before": "is_before"})
    def replace_values_in(self: _Same, column=None, old=_NOT_GIVEN, with_value=_NOT_GIVEN, *, is_above=_NOT_GIVEN,
                          is_below=_NOT_GIVEN, is_at_least=_NOT_GIVEN, is_at_most=_NOT_GIVEN, is_equal_to=_NOT_GIVEN,
                          is_not_equal_to=_NOT_GIVEN, is_between=_NOT_GIVEN, is_one_of=_NOT_GIVEN, contains=_NOT_GIVEN,
                          starts_with=_NOT_GIVEN, ends_with=_NOT_GIVEN, is_after=_NOT_GIVEN, is_before=_NOT_GIVEN,
                          in_rows_where=None, capitals_matter=True) -> _Same:
        """Replace a value (or a list of values) in a column; with_value=None makes those cells empty.

        table.replace_values_in("subject", "Maths", with_value="Math")   (with sdata.get_example("marks"))
        table.replace_values_in("class", {"A": "Class A", "B": "Class B"})   several at once, old: new
        table.replace_values_in("marks", is_above=90, with_value=90)   every value that meets a condition
        With {old: new}, every cell is looked up once in the original column, so
        {"A": "B", "B": "A"} swaps A and B. A new value of None makes those cells empty.
        The conditions are the keep_rows_where ones, one at a time: is_above, is_below, is_at_least,
        is_at_most, is_equal_to, is_not_equal_to, is_between, is_one_of, contains, starts_with, ends_with,
        is_after, is_before.
        Empty cells never match (fill them with fill_empty_cells_in).
        in_rows_where= replaces only in the rows that meet a written condition on other columns:
          table.replace_values_in("subject", "Maths", with_value="Math", in_rows_where="class == 'A'")
        capitals_matter=False finds the old text in any capitals ("maths", "MATHS"), in the old value
        and in the text conditions:
          table.replace_values_in("subject", "maths", with_value="Maths", capitals_matter=False)
        """
        example = 'table.replace_values_in("subject", "Maths", with_value="Math")'
        self._need_one_column("replace_values_in", column, example)
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, contains=contains,
                       starts_with=starts_with, ends_with=ends_with, after=is_after, before=is_before)
        if in_rows_where is not None:
            given = {f"is_{k}" if k not in ("contains", "starts_with", "ends_with") else k: v
                     for k, v in options.items() if v is not _NOT_GIVEN}
            given.update({k: v for k, v in (("old", old), ("with_value", with_value)) if v is not _NOT_GIVEN})
            given["capitals_matter"] = capitals_matter
            return self._only_in_rows("replace_values_in", column, in_rows_where,
                                      lambda: self.replace_values_in(column, **given))
        if any(v is not _NOT_GIVEN for v in options.values()):
            return self._replace_where(column, old, with_value, options, capitals_matter)
        if not isinstance(capitals_matter, bool):
            raise SimplydataError("capitals_matter= should be True or False.")
        if not capitals_matter and self._kind_of(column) != "text":
            raise SimplydataError(f'capitals_matter=False is for text, and "{column}" is a {self._kind_of(column)} '
                                  "column." + _example('table.replace_values_in("subject", "maths", '
                                                       'with_value="Maths", capitals_matter=False)'))
        if isinstance(old, dict):
            if not capitals_matter:
                raise SimplydataError("capitals_matter=False goes with one old value (or a list of them), not with "
                                      "{old: new} pairs." + _example('table.replace_values_in("subject", "maths", '
                                                                     'with_value="Maths", capitals_matter=False)'))
            return self._replace_many(column, old, with_value)
        if old is _NOT_GIVEN or with_value is _NOT_GIVEN:
            raise SimplydataError(
                ".replace_values_in() needs the column, the old value, and with_value= the new value,"
                " or the column and {old: new} pairs." + _example(example)
                + _example('table.replace_values_in("class", {"A": "Class A", "B": "Class B"})')
            )
        olds = list(old) if isinstance(old, (list, tuple, set)) else [old]
        olds = [self._value_for("old value", column, v, example) for v in olds]
        col = nw.col(column)
        if capitals_matter:
            match = self._is_in(column, olds).fill_null(False)
        else:  # pandas str.casefold().isin(...), for both engines
            folded = [v.casefold() for v in olds]
            match = casefold_matches(self._frame, column, lambda f: f.isin(folded)).fill_null(False)
        if with_value is None:
            new_col = nw.when(~match).then(col)
        else:
            new_value = self._value_for("with_value", column, with_value, example)
            new_col = nw.when(match).then(nw.lit(new_value)).otherwise(col)
        n = self._count(match)
        new = self._frame.with_columns(new_col.alias(column))
        print(f"Replaced {_cells(n)} in {column}" + ("" if capitals_matter else " (capitals do not matter)") + ".")
        olds_words = " or ".join(_say(v) for v in olds) + ("" if capitals_matter else " in any capitals")
        return self._change(f"replace {olds_words} in {column} with {_say(with_value)}", new)

    def _replace_where(self, column, old, with_value, options: dict, capitals_matter=True):
        """replace_values_in(column, is_above=100, with_value=100): the cells that meet one keep_rows_where condition."""
        given = [k for k, v in options.items() if v is not _NOT_GIVEN]
        example = f'table.replace_values_in("marks", is_above=90, with_value=90)'
        if old is not _NOT_GIVEN:
            raise SimplydataError(
                f".replace_values_in() takes either the old value or one condition ({_is(given[0])}=), not both."
                + _example('table.replace_values_in("subject", "Maths", with_value="Math")') + _example(example)
            )
        if with_value is _NOT_GIVEN:
            raise SimplydataError(
                ".replace_values_in() needs with_value=, the new value (None makes the cells empty)." + _example(example)
            )
        cond, words = self._condition("replace_values_in", column, options, (), capitals_matter)
        col = nw.col(column)
        if with_value is None:
            new_col, said = nw.when(~cond).then(col), "empty"
        else:
            new_value = self._value_for("with_value", column, with_value, example)
            new_col, said = nw.when(cond).then(nw.lit(new_value)).otherwise(col), _say(new_value)
        n = self._count(cond)
        new = self._frame.with_columns(new_col.alias(column))
        values = "1 value" if n == 1 else f"{n} values"
        if with_value is None:
            print(f'Made {values} in "{column}" empty: the ones that {_past(words, n)}.')
        else:
            print(f'Replaced {values} in "{column}" that {_past(words, n)} with {said}.')
        return self._change(f"replace values in {column} where {column} {words} with {said}", new)

    def _replace_many(self, column, pairs: dict, with_value):
        example = 'table.replace_values_in("class", {"A": "Class A", "B": "Class B"})'
        if with_value is not _NOT_GIVEN:
            raise SimplydataError(
                "With {old: new} pairs the new values are already in the brackets, so leave out with_value=."
                + _example(example)
            )
        if not pairs:
            raise SimplydataError("The {old: new} brackets are empty. Write at least one pair." + _example(example))
        kind = self._kind_of(column)
        checked = []
        for old_value, new_value in pairs.items():
            old_value = self._value_for("old value", column, old_value, example)
            if new_value is not None:
                try:
                    new_value = self._value_for("new value", column, new_value, example)
                except SimplydataError:
                    raise SimplydataError(
                        f'The new values must be the same kind as "{column}", a {kind} column '
                        f"(you gave {_say(new_value)}). To change the kind, replace first and then use "
                        f"turn_into_numbers(), turn_into_text() or turn_into_dates()."
                        + _example('table.replace_values_in("class", {"A": "1", "B": "2"}).turn_into_numbers("class")')
                    ) from None
            checked.append((old_value, new_value))
        col = nw.col(column)
        new_col = col
        for old_value, new_value in reversed(checked):  # every test looks at the original column
            if new_value is not None:
                new_col = nw.when((col == old_value).fill_null(False)).then(nw.lit(new_value)).otherwise(new_col)
        to_empty = [o for o, n in checked if n is None]
        if to_empty:
            new_col = nw.when(~self._is_in(column, to_empty).fill_null(False)).then(new_col)
        counts = [self._count((col == o).fill_null(False)) for o, _ in checked]
        new = self._frame.with_columns(new_col.alias(column))
        said = ", ".join(f"{_say(o)} became {_say(n)} ({_cells(k)})" for (o, n), k in zip(checked, counts) if k)
        print(f"Replaced {_cells(sum(counts))} in {column}" + (f": {said}." if said else "."))
        missing = [_say(o) for (o, _), k in zip(checked, counts) if not k]
        if missing:
            print(f"Note: {', '.join(missing)} {'was' if len(missing) == 1 else 'were'} not found in {column}.")
        what = ", ".join(f"{_say(o)} with {_say(n)}" for o, n in checked)
        return self._change(f"replace {what} in {column}", new)

    @friendly(renamed={"decimals": "with_decimals"})
    def round_numbers_in(self: _Same, column=None, with_decimals=_NOT_GIVEN) -> _Same:
        """Round numbers to this many decimal places: in one column, a list of columns, or every number column.

        table.round_numbers_in("hours", 0)   table.round_numbers_in(["hours", "marks"], 1)   table.round_numbers_in(1)
        (with sdata.get_example("marks"))
        A number exactly halfway goes to the even neighbour (2.5 becomes 2, 3.5 becomes 4),
        like R and NumPy; this stops a run of halves from always pushing totals up.
        round_numbers_in("price", with_decimals=0) gives whole numbers; a negative number of places rounds to tens (-1), hundreds (-2)
        (pandas round(-1); Polars rounds to decimal places only, so on a Polars table tens come from NumPy's round).
        """
        example = 'table.round_numbers_in("hours", 0)'
        if with_decimals is _NOT_GIVEN and isinstance(column, numbers.Integral) and not isinstance(column, bool):
            column, with_decimals = None, column  # table.round_numbers_in(2): every number column
        if with_decimals is _NOT_GIVEN:
            with_decimals = 0
        if not isinstance(with_decimals, numbers.Integral) or isinstance(with_decimals, bool):
            raise SimplydataError(".round_numbers_in() needs a whole number of decimal places, like 2." + _example(example))
        with_decimals = int(with_decimals)
        number_columns = [c for c in self._columns if self._kind_of(c) == "number"]
        if column is None:
            names = number_columns
            if not names:
                raise SimplydataError("This table has no columns of numbers to round.")
        else:
            names = [column] if isinstance(column, str) else _as_list([column])
            if not names or not all(isinstance(n, str) for n in names):
                raise SimplydataError(
                    ".round_numbers_in() needs column names in quotes, then the decimal places." + _example(example)
                )
            self._need_columns(*names)
            for name in names:
                if name not in number_columns:
                    raise SimplydataError(
                        f'.round_numbers_in() rounds numbers, but "{name}" is a {self._kind_of(name)} column.\n'
                        f"Columns with numbers: {', '.join(number_columns) or 'none'}" + _example(example)
                    )
        if self._frame.implementation.is_polars():
            _need_polars_rounding_halves_to_even()
        polars = self._frame.implementation.is_polars()
        if with_decimals < 0 and polars:
            # Polars rounds to decimal places only (round() refuses a negative number of places), so tens and
            # hundreds come from NumPy's round, the one pandas uses for round(-1): the same numbers on both engines
            import numpy as np
            import polars as pl

            native = self._frame.to_native().with_columns(
                [pl.col(name).map_batches(lambda s: pl.Series(s.name, np.round(s.to_numpy(), with_decimals)))
                 for name in names])
            new = nw.from_native(native, eager_only=True)
        changes = []
        for name in names:
            dtype = self._frame.schema[name]
            col = nw.col(name)
            if dtype.is_integer() and with_decimals >= 0:
                continue  # whole numbers stay as they are
            if with_decimals >= 0 or not polars:
                changes.append(col.round(with_decimals).alias(name))  # pandas round(-1) for tens, its own
        if with_decimals >= 0:
            to = f"{with_decimals} decimal place" + ("" if with_decimals == 1 else "s")
        else:
            to = f"the nearest {10 ** -with_decimals}"
        where = ", ".join(names)
        print(f"Rounded {where} to {to}.")
        if not (with_decimals < 0 and polars):
            new = self._frame.with_columns(*changes) if changes else self._frame
        return self._change(f"round {where} to {to}", new)

    @friendly
    def show(self, rows=None):
        """Show the table, every row and every column (or only the first rows=).

        table.show()   table.show(rows=10)   (with sdata.get_example("marks"))
        A table with more than 1,000 rows shows its first 1,000; choose another number with rows=.
        Rows are numbered from 1, the numbers keep_rows_by_position() takes.
        """
        import pandas as pd

        if rows is not None:
            rows = _check_count("show", rows, "table.show(rows=10)")
        total = len(self._frame)
        part = self._frame.head(SHOW_LIMIT if rows is None else rows)
        with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.width", None):
            _show_native(numbered(part))
        if len(part) < total:
            print(f"(the first {_rows(len(part))} of {total}; table.show(rows={total}) shows them all)")
        return None

    # ================================================================== biggest and smallest
    def _for_each(self, step: str, for_each, column, example: str) -> list:
        """The for_each_group_in= columns as a list (empty when not given)."""
        if for_each is None:
            return []
        groups = [for_each] if isinstance(for_each, str) else _as_list([for_each])
        if not groups or not all(isinstance(g, str) for g in groups):
            raise SimplydataError('for_each_group_in= needs a column name in quotes, like for_each_group_in="class".' + _example(example))
        self._need_columns(*groups)
        if column in groups:
            raise SimplydataError(
                f'"{column}" cannot be both the column to look at and the for_each_group_in= column.' + _example(example)
            )
        return groups

    def _keep_extreme(self, step: str, n, by, for_each, biggest: bool):
        word = "biggest" if biggest else "smallest"
        example = f'table.{step}(3, by="marks", for_each_group_in="subject")'
        if n is None:
            raise SimplydataError(f".{step}() needs how many rows to keep, like 3." + _example(example))
        n = _check_count(step, n, example)
        if by is None:
            raise SimplydataError(f'.{step}() needs by= the column to look at, like by="marks".' + _example(example))
        self._need_one_column(step, by, example)
        kind = self._kind_of(by)
        if kind not in ("number", "date"):
            raise SimplydataError(
                f'.{step}() looks for the {word} numbers or dates, but "{by}" is a {kind} column.' + _example(example)
            )
        groups = self._for_each(step, for_each, by, example)
        empty = self._empty(by)
        n_empty = self._count(empty)
        frame = self._frame.filter(~empty)
        place = nw.col(by).rank("ordinal", descending=biggest)
        tied = nw.col(by).rank("min", descending=biggest)
        if groups:
            place, tied = place.over(*groups), tied.over(*groups)
        rank, tie = _NEW, _NEW + "tie"
        frame = frame.with_columns(place.alias(rank), tied.alias(tie))
        cut_ties = _count_in(frame, (nw.col(rank) > n) & (nw.col(tie) <= n))
        kept = frame.filter(nw.col(rank) <= n).sort([*groups, rank], nulls_last=True).drop(rank, tie)
        before = len(self._frame)
        each = f" for each {', '.join(groups)}" if groups else ""
        print(f"Kept the {_rows(n)} with the {word} {by}{each}: {len(kept)} of {_rows(before)}.")
        if cut_ties:
            print(f"Note: {_rows(cut_ties)} had the same {by} as the last row kept and "
                  f"{'was' if cut_ties == 1 else 'were'} left out; rows that tie are kept in table order.")
        if n_empty:
            print(f"Note: {_rows(n_empty)} with an empty {by} cell {'was' if n_empty == 1 else 'were'} left out.")
        return self._change(f"keep the {_rows(n)} with the {word} {by}{each}", kept)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def keep_biggest_rows(self: _Same, n=None, by=None, for_each_group_in=None) -> _Same:
        """Keep the n rows with the biggest values in a column (also for each group).

        table.keep_biggest_rows(3, by="marks", for_each_group_in="subject")   (with sdata.get_example("marks"))
        The rows come biggest first. Exactly n rows are kept: when rows tie at the cut, the
        ones higher up in the table are kept (a note says so). Empty cells are never kept.
        """
        return self._keep_extreme("keep_biggest_rows", n, by, for_each_group_in, biggest=True)

    @friendly(renamed={"for_each": "for_each_group_in"})
    def keep_smallest_rows(self: _Same, n=None, by=None, for_each_group_in=None) -> _Same:
        """Keep the n rows with the smallest values in a column (also for each group).

        table.keep_smallest_rows(3, by="marks", for_each_group_in="subject")   (with sdata.get_example("marks"))
        The rows come smallest first. Exactly n rows are kept: when rows tie at the cut, the
        ones higher up in the table are kept (a note says so). Empty cells are never kept.
        """
        return self._keep_extreme("keep_smallest_rows", n, by, for_each_group_in, biggest=False)

    # ================================================================== outliers
    def _outliers(self, step: str, column, for_each, rule):
        """Print the rule and its limits; give the table with an outlier column (_NEW) and the helper names."""
        example = f'table.{step}("marks", for_each_group_in="subject")'
        self._need_one_column(step, column, example)
        kind = self._kind_of(column)
        if kind != "number":
            raise SimplydataError(
                f'.{step}() looks for outliers among numbers, but "{column}" is a {kind} column.' + _example(example)
            )
        if isinstance(rule, str) and rule.strip().lower() in TEST_RULES:
            return self._test_outliers(step, column, for_each, rule.strip().lower(), example)
        k, how = _rule_of(step, rule, example)
        groups = self._for_each(step, for_each, column, example)
        value, mid, spread, low, high = (_NEW + p for p in ("value", "mid", "spread", "low", "high"))
        frame = self._frame.with_columns(
            nw.when(~self._empty(column)).then(nw.col(column).cast(nw.Float64)).alias(value)
        )
        v = nw.col(value)

        def each(expr):
            return expr.over(*groups) if groups else expr

        if how == "IQR":  # quartiles with linear interpolation, as NumPy, pandas and R's default (type 7)
            frame = frame.with_columns(each(v.quantile(0.25, "linear")).alias(mid),
                                       each(v.quantile(0.75, "linear")).alias(spread))
            iqr = nw.col(spread) - nw.col(mid)
            frame = frame.with_columns((nw.col(mid) - k * iqr).alias(low), (nw.col(spread) + k * iqr).alias(high))
        else:  # average and sample standard deviation (n - 1), as pandas .std() and R sd()
            frame = frame.with_columns(each(v.mean()).alias(mid), each(v.std(ddof=1)).alias(spread))
            frame = frame.with_columns((nw.col(mid) - k * nw.col(spread)).alias(low),
                                       (nw.col(mid) + k * nw.col(spread)).alias(high))
        frame = frame.with_columns(((v < nw.col(low)) | (v > nw.col(high))).fill_null(False).alias(_NEW))
        frame = frame.with_columns(nw.col(_NEW).cast(nw.Int64).alias(_NEW + "count"))

        kk = _nice(k)
        if how == "IQR":
            print(f'Outliers in "{column}" by Tukey\'s rule: values more than {kk} x IQR below the first '
                  f"quartile (Q1) or above the third quartile (Q3).")
            print("IQR, the interquartile range, is Q3 - Q1: the spread of the middle half of the values.")
            names = ("Q1", "Q3")
        else:
            print(f'Outliers in "{column}": values more than {kk} standard deviations below or above the average.')
            names = ("average", "standard deviation")
        summary = [nw.col(low).min().alias("low"), nw.col(high).min().alias("high"),
                   nw.col(mid).min().alias("mid"), nw.col(spread).min().alias("spread"),
                   v.count().alias("n"), nw.col(_NEW + "count").sum().alias("found")]
        if groups:
            limits = frame.group_by(groups, drop_null_keys=False).agg(*summary).sort(groups, nulls_last=True)
        else:
            limits = frame.select(*summary)

        def limit_words(row):
            if row["low"] is None or row["low"] != row["low"]:
                return "too few numbers to judge"
            return (f"below {_nice(float(row['low']))} or above {_nice(float(row['high']))} "
                    f"({names[0]} = {_nice(float(row['mid']))}, {names[1]} = {_nice(float(row['spread']))})")

        rows = limits.rows(named=True)
        if not groups:
            print(f"Here that means {limit_words(rows[0])}.")
        else:
            print(f"For each {', '.join(groups)}:")
            for row in rows[:20]:
                label = ", ".join("(empty)" if row[g] is None else _nice(row[g]) for g in groups)
                print(f"  {label}: {limit_words(row)}; {_rows(int(row['found'] or 0))} found")
            if len(rows) > 20:
                print(f"  ... and {len(rows) - 20} more groups")
        if how != "IQR":
            small = [m for m in (int(r["n"] or 0) for r in rows) if m >= 2 and (m - 1) / math.sqrt(m) <= k]
            if small:
                print(f"Note: with {min(small)} numbers{' in a group' if groups else ''} no value can be more than "
                      f"{kk} standard deviations from the average, because an outlier also makes the standard "
                      f'deviation bigger. For small groups use test_method="1.5 IQR".')
        words = f"{kk} x IQR" if how == "IQR" else f"{kk} standard deviations"
        if groups:
            words += f", for each {', '.join(groups)}"
        return frame, frame.columns[len(self._columns):], words

    def _test_outliers(self, step, column, for_each, rule, example):
        """test_method="grubbs" / "dixon" / "rosner": outlier tests from R (outliers::grubbs.test, outliers::dixon.test,
        EnvStats::rosnerTest), group by group; the value tested is the one R outliers::outlier() names."""
        from .._r import r_call
        from .stat_tests import _num

        groups = self._for_each(step, for_each, column, example)
        place = _NEW + "place"
        frame = self._frame.with_row_index(place)
        values = frame.filter(~_empty_in(frame, column))
        keys = [tuple(r) for r in values.select(*groups).rows()] if groups else [()] * len(values)
        numbers = values[column].to_numpy().astype(float)
        places = np.asarray(values[place].to_list())
        flagged, lines = [], []
        r_name = {"grubbs": "outliers::grubbs.test()", "dixon": "outliers::dixon.test()",
                  "rosner": "EnvStats::rosnerTest(k = 3)"}[rule]
        for key in sorted(set(keys), key=lambda k: tuple((str(type(v)), v) for v in k)):
            rows = np.array([k == key for k in keys])
            x = numbers[rows]
            label = (", ".join(_nice(v) for v in key) + ": ") if groups else ""
            if len(x) < 3 or (rule == "dixon" and len(x) > 30) or np.ptp(x) == 0:
                lines.append(f"{label}not tested ({len(x)} values; {rule.capitalize()}'s test needs "
                             + ("3 to 30" if rule == "dixon" else "at least 3") + " values that differ)")
                continue
            if rule == "rosner":
                found = r_call("r <- EnvStats::rosnerTest(x, k = min(3, length(x) - 2))$all.stats; "
                               "list(at = r$Obs.Num[r$Outlier])", packages=("EnvStats",),
                               what="Rosner's outlier test (R EnvStats::rosnerTest())", source="EnvStats::rosnerTest",
                               python_note="Python's stack has no Rosner test", x=x)
                at = [int(i) - 1 for i in np.atleast_1d(np.asarray(found["at"], dtype=float))] if found["at"] is not None \
                    else []
                lines.append(f"{label}{len(at)} outlier{'' if len(at) == 1 else 's'} found among up to 3 tested")
            else:
                test = "grubbs.test" if rule == "grubbs" else "dixon.test"
                found = r_call(f"t <- outliers::{test}(x); v <- outliers::outlier(x); "
                               "list(p = t$p.value, at = which(x == v))", packages=("outliers",),
                               what=f"{rule.capitalize()}'s outlier test (R outliers::{test}())",
                               python_note=f"Python's stack has no {rule.capitalize()} test", x=x)
                p = float(np.asarray(found["p"], dtype=float)[0])
                at = [int(i) - 1 for i in np.atleast_1d(np.asarray(found["at"], dtype=float))] if p < 0.05 else []
                lines.append(f"{label}the value farthest from the average, {_nice(float(x[int(np.atleast_1d(found['at'])[0]) - 1]))}, "
                             f"{'is an outlier' if at else 'is not shown to be an outlier'} "
                             f"({'p < 0.0001' if p < 1e-4 else 'p = ' + _num(p)})")
            flagged.extend(int(places[rows][i]) for i in at)
        print(f'Outliers in "{column}" by {rule.capitalize()}\'s test (R {r_name}, at the 5 % level), '
              + ("for each " + ", ".join(groups) + ":" if groups else "here:"))
        for line in lines[:20]:
            print(f"  {line}")
        if len(lines) > 20:
            print(f"  ... and {len(lines) - 20} more groups")
        print("Note: these tests assume the other values are roughly bell-shaped; a value that is an outlier is not "
              "automatically wrong, so check it before you remove it.")
        frame = frame.with_columns(nw.col(place).is_in(flagged).alias(_NEW))
        frame = frame.drop(place)
        words = f"{rule.capitalize()}'s test" + (f", for each {', '.join(groups)}" if groups else "")
        return frame, [_NEW], words

    @friendly(renamed={"rule": "test_method", "for_each": "for_each_group_in"})
    def show_rows_with_outliers(self, column=None, for_each_group_in=None, test_method="1.5 IQR"):
        """Show the rows whose value in a column is an outlier, and say why (the table does not change).

        table.show_rows_with_outliers("marks", for_each_group_in="subject")   (with sdata.get_example("marks"))
        test_method="1.5 IQR" (the default) is Tukey's rule, the one box plots use: below Q1 - 1.5 x IQR
        or above Q3 + 1.5 x IQR. Also test_method="3 IQR" or test_method="3 standard deviations", or an
        outlier test run in R (simplydata[r]): test_method="grubbs" (outliers::grubbs.test(), the value
        farthest from the average), "dixon" (outliers::dixon.test(), 3 to 30 values) or "rosner"
        (EnvStats::rosnerTest(), up to 3 outliers), each at the 5 % level, group by group.
        Empty cells are never outliers. Each row is shown with its number in the whole table
        (counting from 1), so remove_rows_by_position() can follow.
        """
        frame, helpers, _ = self._outliers("show_rows_with_outliers", column, for_each_group_in, test_method)
        place = _NEW + "place"
        found = frame.with_row_index(place).filter(nw.col(_NEW))
        positions = found[place].to_list()
        found = found.drop([place, *helpers])
        print(f"Found {_rows(len(found))} with an outlier, of {_rows(len(frame))}.")
        if len(found):
            _show_native(numbered_at(nw.maybe_reset_index(found), positions))
            print("The numbers on the left are the rows' places in the whole table, so "
                  f"table.remove_rows_by_position({_list_code(p + 1 for p in positions)}) would remove them.")
        return None

    @friendly(renamed={"rule": "test_method", "for_each": "for_each_group_in"})
    def remove_rows_with_outliers(self: _Same, column=None, for_each_group_in=None, test_method="1.5 IQR") -> _Same:
        """Remove the rows whose value in a column is an outlier, and say how many and why.

        table.remove_rows_with_outliers("marks", for_each_group_in="subject")   (with sdata.get_example("marks"))
        test_method="1.5 IQR" (the default) is Tukey's rule, the one box plots use: below Q1 - 1.5 x IQR
        or above Q3 + 1.5 x IQR. Also test_method="3 IQR" or test_method="3 standard deviations", or an
        outlier test run in R (simplydata[r]): test_method="grubbs" (outliers::grubbs.test(), the value
        farthest from the average), "dixon" (outliers::dixon.test(), 3 to 30 values) or "rosner"
        (EnvStats::rosnerTest(), up to 3 outliers), each at the 5 % level, group by group.
        Rows with an empty cell stay. Look first with show_rows_with_outliers(), and say in your
        report which rule removed how many rows.
        """
        frame, helpers, words = self._outliers("remove_rows_with_outliers", column, for_each_group_in, test_method)
        new = frame.filter(~nw.col(_NEW)).drop(helpers)
        before = len(frame)
        print(f"Removed {before - len(new)} of {_rows(before)}. {_rows(len(new))} left.")
        return self._change(f"remove rows with outliers in {column} ({words})", new)
