"""Tables phase, batch 2: more words for the jobs of a messy table (approved by Manish 2026-11-25).

  count_columns                    how many columns: the pair of count_rows
  rename_columns                   several names at once, or the same start or end added to every name
  add_missing_combinations_of      a row for every year x country pair, so gaps show as empty cells
  round_dates_in                   down to the month, up to the day, or to the nearest hour
  change_time_zone_in              clock times written in Oslo, shown in UTC
  spread_into_yes_no_columns       a yes/no column for each value: "fruit: apple", "fruit: banana" ...
  fill_empty_cells_from            empty cells take the value of the matching row of another table

Every word passes straight through to pandas or Polars (PLAN.md section 7); the comment at each call names it. Each
word works on pandas and Polars tables alike, keeps a step for undo(), and says what it did.
"""

from __future__ import annotations

import narwhals as nw

from .._errors import SimplydataError, friendly, suggest
from .._typing import _Same
from .conditions import _count_in, _kind, _rows
from .more_table_words import _example, _words_list

# round_dates_in(): the units, the narwhals / Polars duration code of one of each, and the pandas frequency
DATE_UNITS = {"second": ("s", "s"), "minute": ("m", "min"), "hour": ("h", "h"), "day": ("d", "D"),
              "week": ("7d", "W"), "month": ("mo", None), "year": ("y", None)}
# the units of a time of day: a table of dates without times has none of these
_TIME_UNITS = ("second", "minute", "hour")
# to_the= (to the nearest): units of a fixed length only; a month or a year has no one length
_NEAREST_UNITS = ("second", "minute", "hour", "day")


def _unit_and_count(option: str, value, example: str):
    """ "hour" -> (1, "hour"); "15 minutes" -> (15, "minute"). The unit is checked against DATE_UNITS."""
    if not isinstance(value, str) or not value.strip():
        raise SimplydataError(f'{option}= takes a unit in quotes, such as {option}="month" or {option}="15 minutes".'
                              + example)
    words = value.strip().lower().split()
    count = 1
    if len(words) == 2 and words[0].isdigit():
        count, words = int(words[0]), words[1:]
    unit = words[0].rstrip("s") if len(words) == 1 else None
    if unit not in DATE_UNITS or count < 1:
        raise SimplydataError(f'{option}="{value}" is not a unit simplydata knows. You can use: '
                              + ", ".join(f'"{u}"' for u in DATE_UNITS) + ', or a number of them, such as "15 minutes".'
                              + example)
    if count > 1 and unit in ("week", "month", "year"):
        raise SimplydataError(f'{option}= takes "{unit}" alone (not "{value}"): steps of several {unit}s have no fixed '
                              "starting point." + example)
    return count, unit


def _check_zone(option: str, zone, example: str) -> str:
    """A time zone name from the IANA list (Python zoneinfo), with a did-you-mean."""
    import zoneinfo

    if not isinstance(zone, str) or not zone.strip():
        raise SimplydataError(f'{option}= takes the name of a time zone in quotes, such as "Europe/Oslo" or "UTC".'
                              + example)
    zone = zone.strip()
    if zone.upper() == "UTC":
        return "UTC"
    try:
        zoneinfo.ZoneInfo(zone)
    except (zoneinfo.ZoneInfoNotFoundError, ValueError):
        names = sorted(zoneinfo.available_timezones())
        guess = suggest(zone, names, n=1)
        hint = f' Did you mean "{guess[0]}"?' if guess else ""
        raise SimplydataError(f'"{zone}" is not a time zone name simplydata knows.{hint} Time zones are written as '
                              'region/city, as in "Europe/Oslo", "America/New_York" or "UTC".' + example) from None
    return zone


def _holds_the_value(values, separator, value) -> bool:
    """value is one of values (or one of their pieces at separator)."""
    return any(value in (str(v).split(separator) if separator else [str(v)]) for v in values)


class MoreTableWords2:
    # ================================================================== columns
    @friendly
    def count_columns(self) -> int:
        """How many columns the table has (count_rows() gives the rows).

        table.count_columns()   (with sdata.get_example("marks"))
        Prints "The table has 6 columns." and gives back the number. As pandas df.shape[1] and Polars
        df.width; get_column_names() lists them.
        """
        n = len(self._columns)
        print(f"The table has {n} column{'' if n == 1 else 's'}.")
        return n

    @friendly(others={"columns": "new_names", "mapper": "new_names", "prefix": "add_in_front",
                      "suffix": "add_at_end"})
    def rename_columns(self: _Same, new_names=None, add_in_front=None, add_at_end=None) -> _Same:
        """Give several columns new names at once, or add the same text in front of (or after) every name.

        table.rename_columns({"temperature": "temp", "rain": "rain_mm"})   (with sdata.get_example("weather"))
        The names go in curly brackets, each old name with its new one. add_in_front= and add_at_end=
        add text to every column name, for example before joining two tables that share names:
          table.rename_columns(add_in_front="w_")
        As pandas df.rename(columns={...}), df.add_prefix("w_") and df.add_suffix("_mm"), and Polars
        df.rename({...}) and df.select(pl.all().name.prefix("w_")). For one column, rename_column("marks",
        to="score") does the same. Undo with table.undo().
        """
        step = "rename_columns"
        example = _example('table.rename_columns({"temperature": "temp", "rain": "rain_mm"})', "weather")
        ways = [w for w, v in (("new names", new_names), ("add_in_front=", add_in_front),
                               ("add_at_end=", add_at_end)) if v is not None]
        if len(ways) != 1:
            raise SimplydataError(
                f".{step}() takes one way at a time: the new names in curly brackets, add_in_front= or add_at_end="
                + (f" (you gave {' and '.join(ways)})." if ways else ".") + example
                + _example('table.rename_columns(add_in_front="w_")', "weather"))
        if new_names is not None:
            if not isinstance(new_names, dict) or not new_names or not all(
                    isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in new_names.items()):
                raise SimplydataError(f".{step}() needs the names in curly brackets, each old name with its new one "
                                      "in quotes." + example)
            self._need_columns(*new_names)
            changes = {old: new for old, new in new_names.items() if old != new}
            said = "the new names"
        else:
            text = add_in_front if add_in_front is not None else add_at_end
            option = ways[0]
            if not isinstance(text, str) or not text:
                raise SimplydataError(f'{option} takes some text in quotes, such as {option}"w_".'
                                      + _example('table.rename_columns(add_in_front="w_")', "weather"))
            changes = {c: (text + c if add_in_front is not None else c + text) for c in self._columns}
            said = f'"{text}" {"in front of" if add_in_front is not None else "at the end of"} every name'
        names = [changes.get(c, c) for c in self._columns]
        twice = sorted({n for n in names if names.count(n) > 1})
        if twice:
            raise SimplydataError(f'After renaming, {_words_list(twice)} would name more than one column. Choose '
                                  "names that differ from each other and from the columns you keep.")
        if not changes:
            print("Every new name is the same as the old one, so nothing changed.")
        else:
            shown = ", ".join(f"{o} -> {n}" for o, n in list(changes.items())[:8])
            more = f" ... ({len(changes)} in all)" if len(changes) > 8 else ""
            print(f"Renamed {len(changes)} column{'s' if len(changes) != 1 else ''}: {shown}{more}.")
        return self._change(f"rename columns ({said})", self._frame.rename(changes))  # pandas rename, Polars rename

    # ================================================================== rows for missing combinations
    @friendly
    def add_missing_combinations_of(self: _Same, *columns) -> _Same:
        """Add a row for every combination of these columns' values that is not in the table yet.

        table.add_missing_combinations_of("station", "depth_m")   (with sdata.get_example("fjord_samples"))
        Every station then has a row for every depth, and a sample that was never taken shows as a
        row with empty cells, instead of being missing without a word. The sentence says how many
        rows were added. The rows come out sorted by these columns; rows with an empty cell in them
        stay, at the end. It is the twin of add_missing_dates() (which fills a run of dates). As
        pandas df.set_index(cols).reindex(pd.MultiIndex.from_product([...])).reset_index() and
        Polars: the unique values of each column, joined how="cross", then joined to the table; as
        R tidyr::complete(). Undo with table.undo().
        """
        step = "add_missing_combinations_of"
        example = _example(f'table.{step}("station", "depth_m")', "fjord_samples")
        cols = []
        for c in columns:
            cols += list(c) if isinstance(c, (list, tuple)) else [c]
        if len(cols) < 2 or not all(isinstance(c, str) for c in cols):
            raise SimplydataError(f".{step}() needs two or more column names in quotes." + example)
        if len(set(cols)) != len(cols):
            raise SimplydataError(f".{step}() got a column twice; give each column once." + example)
        self._need_columns(*cols)
        frame = self._frame
        grid = None
        for c in cols:  # Polars df.select(c).unique(), joined how="cross"
            values = frame.select(c).filter(~nw.col(c).is_null()).unique()
            grid = values if grid is None else grid.join(values, how="cross")
        missing = grid.join(frame.select(cols).unique(), on=cols, how="anti")  # the pairs not in the table
        index = "_simplydata_row_"
        if len(missing) and not frame.implementation.is_polars():
            # pandas would turn whole numbers into decimals for the new empty cells (and lose digits above 2**53):
            # its nullable whole numbers (Int64) keep them whole, as Polars does
            import pandas as pd

            whole = [c for c, d in frame.schema.items() if d.is_integer()]
            native = frame.to_native().astype({c: "Int64" for c in whole})
            extra = missing.to_native().astype({c: "Int64" for c in whole if c in missing.columns})
            extra = extra.assign(**{c: pd.array([pd.NA] * len(extra), dtype="Int64") for c in whole
                                    if c not in extra.columns})
            new = nw.from_native(pd.concat([native, extra], ignore_index=True), eager_only=True)
        else:
            new = nw.concat([frame, missing], how="diagonal") if len(missing) else frame
        new = (new.with_row_index(index).sort([*cols, index], nulls_last=True).drop(index))
        sizes = " x ".join(str(len(frame.select(c).filter(~nw.col(c).is_null()).unique())) for c in cols)
        print(f"Added {_rows(len(missing))} for the missing combinations of {_words_list(cols)} ({sizes} = "
              f"{len(grid)} combinations); their other cells are empty. The rows are sorted by {', '.join(cols)}.")
        return self._change(f"add missing combinations of {', '.join(cols)} ({len(missing)})", new)

    # ================================================================== dates and times
    @friendly(others={"unit": "to_the", "freq": "to_the"})
    def round_dates_in(self: _Same, column=None, to_the=None, down_to=None, up_to=None) -> _Same:
        """Round the dates (or times) of a column: down to the month, up to the day, or to the nearest hour.

        table.round_dates_in("date", down_to="month")   (with sdata.get_example("shop"))
        Every date becomes the first day of its month, ready to count or sum month by month.
          down_to="week"     back to the Monday of the week
          up_to="day"        forward to the next midnight (a time already on the hour stays)
          to_the="hour"      to the nearest hour; a time exactly half way goes up (10:30 becomes 11:00)
          to_the="15 minutes" to the nearest quarter of an hour
        The units are "second", "minute", "hour", "day", "week", "month" and "year", or a number of
        seconds, minutes, hours or days. to_the= takes units of one length only: a month or a year has
        no one length, so they are rounded with down_to= or up_to=. Empty cells stay empty. As pandas
        dt.floor("h") (dt.to_period("M").dt.to_timestamp() for months), dt.ceil("h") and dt.round("h"),
        and Polars dt.truncate("1h") and dt.round("1h"). simplydata runs Polars for every table: pandas
        dt.round sends a time half way to the even hour and stops at the hour that comes twice when
        summer time ends, so Polars' rule (half way goes up; summer-time changes kept in order) is
        used on pandas tables too. Undo with table.undo().
        """
        step = "round_dates_in"
        example = _example(f'table.{step}("date", down_to="month")', "shop")
        if not isinstance(column, str):
            raise SimplydataError(f".{step}() needs the column name in quotes first." + example)
        self._need_columns(column)
        given = [(o, v) for o, v in (("to_the", to_the), ("down_to", down_to), ("up_to", up_to)) if v is not None]
        if len(given) != 1:
            raise SimplydataError(f".{step}() needs one of to_the=, down_to= or up_to=" +
                                  (f" (you gave {' and '.join(o + '=' for o, _ in given)})." if given else ".")
                                  + example)
        option, value = given[0]
        count, unit = _unit_and_count(option, value, example)
        dtype = self._frame.schema[column]
        if _kind(dtype) != "date":
            raise SimplydataError(f'"{column}" holds {_kind(dtype)} values, not dates. If it holds dates written as '
                                  f'text, first write table.turn_into_dates("{column}").' + example)
        if dtype == nw.Date and unit in _TIME_UNITS:
            raise SimplydataError(f'"{column}" holds dates without a time of day, so there is no {unit} to round to.')
        if option == "to_the" and unit not in _NEAREST_UNITS:
            raise SimplydataError(f'to_the="{value}" is not offered: a {unit} has no one length, so "the nearest {unit}" '
                                  f'has no one answer. Use down_to="{unit}" (the start of the {unit}) or up_to="{unit}".')
        code = "1w" if unit == "week" else f"{count}{DATE_UNITS[unit][0]}"
        step_code = "7d" if unit == "week" else code
        # one parent for both engines: Polars dt.round / dt.truncate / dt.offset_by. pandas dt.round sends half way to
        # the even hour and refuses the repeated hour of the autumn change ("Cannot infer dst time"), so a pandas
        # table is rounded by Polars too, and comes back as pandas
        import polars as pl

        native = self._frame[column].to_native()
        polars = self._frame.implementation.is_polars()
        values = native if polars else pl.from_pandas(native)
        d = pl.col(column)
        if option == "to_the":
            expr, how = d.dt.round(code), f"to the nearest {value}"  # Polars dt.round("1h"): half way goes up
        elif option == "down_to":
            expr, how = d.dt.truncate(code), f"down to the {value}"  # Polars dt.truncate("1mo")
        else:  # up: the start of the unit, unless the value is on it already; then one unit on (pandas dt.ceil)
            down = d.dt.truncate(code)
            expr, how = pl.when(d == down).then(d).otherwise(down.dt.offset_by(step_code)), f"up to the {value}"
        rounded = pl.DataFrame({column: values}).select(expr.alias(column))[column]
        if not polars:
            rounded = rounded.to_pandas().astype(native.dtype)
            rounded.index = native.index
        new = self._frame.with_columns(nw.from_native(rounded, series_only=True).alias(column))
        old = "_simplydata_old_"
        both = new.with_columns(self._frame[column].alias(old)).filter(
            (nw.col(column) != nw.col(old)).fill_null(False) & ~nw.col(old).is_null())  # pandas NaT != NaT is True
        changed = len(both)
        shown = f" For example {both[old].item(0)} became {both[column].item(0)}." if changed else ""
        print(f'Rounded the dates in "{column}" {how}: {changed} of {_rows(len(new))} changed.{shown}')
        return self._change(f'round dates in "{column}" {how}', new)

    @friendly(others={"tz": "to", "time_zone": "to", "from_zone": "recorded_in", "tzone": "to"})
    def change_time_zone_in(self: _Same, column=None, to=None, recorded_in=None) -> _Same:
        """Change the clock times of a column to another time zone, such as from Oslo time to UTC.

        table.change_time_zone_in("sampled_local", to="UTC", recorded_in="Europe/Oslo")   (with sdata.get_example("fjord_samples"))
        recorded_in= says where clock times without a time zone were written (08:32 on board in
        Norway); to= gives the same moments on another clock (06:32 UTC in summer). A
        column that already has a time zone needs only to=; recorded_in= alone just writes the zone
        down. Zone names are the standard ones: "UTC", "Europe/Oslo", "America/New_York".
        The sentence shows one time before and after. A clock time that never happens (in the hour
        skipped when summer time starts) or happens twice (when it ends) cannot be placed, so it
        becomes an empty cell, and a note says how many. As pandas dt.tz_localize("Europe/Oslo",
        nonexistent="NaT", ambiguous="NaT").dt.tz_convert("UTC") and Polars
        dt.replace_time_zone("Europe/Oslo", non_existent="null", ambiguous="null").dt.convert_time_zone("UTC").
        """
        step = "change_time_zone_in"
        example = _example(f'table.{step}("sampled_local", to="UTC", recorded_in="Europe/Oslo")', "fjord_samples")
        if not isinstance(column, str):
            raise SimplydataError(f".{step}() needs the column name in quotes first." + example)
        self._need_columns(column)
        dtype = self._frame.schema[column]
        if dtype != nw.Datetime:
            hint = (" It holds dates without a time of day, which have no time zone." if dtype == nw.Date else
                    f' If it holds times written as text, first write table.turn_into_dates("{column}").')
            raise SimplydataError(f'"{column}" holds no clock times.{hint}' + example)
        if to is None and recorded_in is None:
            raise SimplydataError(f".{step}() needs to=, the time zone to change to." + example)
        zone_now = dtype.time_zone
        if recorded_in is not None:
            recorded_in = _check_zone("recorded_in", recorded_in, example)
            if zone_now is not None:
                raise SimplydataError(f'"{column}" already has a time zone ({zone_now}), so leave out recorded_in= and '
                                      f'give only to=: table.{step}("{column}", to="UTC").')
        elif zone_now is None:
            raise SimplydataError(
                f'"{column}" holds clock times without a time zone, so simplydata cannot know which moments they '
                f'are. Say where they were written with recorded_in=.' + example)
        if to is not None:
            to = _check_zone("to", to, example)
        frame, gaps = self._frame, 0
        if recorded_in is not None:
            native = frame.to_native()
            before_empty = native[column].is_null().sum() if frame.implementation.is_polars() else native[column].isna().sum()
            if frame.implementation.is_polars():
                import polars as pl

                native = native.with_columns(pl.col(column).dt.replace_time_zone(
                    recorded_in, ambiguous="null", non_existent="null"))
                after_empty = native[column].is_null().sum()
            else:
                native = native.assign(**{column: native[column].dt.tz_localize(
                    recorded_in, ambiguous="NaT", nonexistent="NaT")})
                after_empty = native[column].isna().sum()
            frame = nw.from_native(native, eager_only=True)
            gaps = int(after_empty - before_empty)
        if to is not None:
            frame = frame.with_columns(nw.col(column).dt.convert_time_zone(to))  # pandas tz_convert, Polars convert
        old = self._frame.filter(~nw.col(column).is_null())
        shown = ""
        if len(old):
            row = self._frame.with_row_index("_simplydata_i_").filter(~nw.col(column).is_null())["_simplydata_i_"].item(0)
            after = frame[column].item(row)
            shown = f" For example {old[column].item(0)}{' ' + zone_now if zone_now else ''} is now {after}."
        where = f"written in {recorded_in}" if recorded_in is not None else f"in {zone_now}"
        if to is not None:
            print(f'The times in "{column}" ({where}) are now on the {to} clock.{shown}')
        else:
            print(f'The times in "{column}" now carry their time zone, {recorded_in}.{shown}')
        if gaps:
            print(f"Note: {gaps} clock time{'s' if gaps != 1 else ''} never happened or happened twice in "
                  f"{recorded_in} (the summer-time change), so {'they are' if gaps != 1 else 'it is'} now empty.")
        what = f'change time zone in "{column}"' + (f" to {to}" if to else "") + (
            f" (recorded in {recorded_in})" if recorded_in else "")
        return self._change(what, frame)

    # ================================================================== yes/no columns
    @friendly(others={"sep": "separator", "prefix_sep": "separator"})
    def spread_into_yes_no_columns(self: _Same, column=None, separator=None) -> _Same:
        """Add a yes/no (True/False) column for each value of a text column: "fruit: apple", "fruit: banana" ...

        table.spread_into_yes_no_columns("fruit")   (with sdata.get_example("fruit"))
        Each new column is True in the rows that hold that value. Models and some charts need this
        form ("dummy" or "one-hot" columns). separator= is for cells that hold several values, such as
        "sul1;tetM": each value gets its own column, True where the cell names it:
          table.spread_into_yes_no_columns("genes", separator=";")
        The new columns come at the end, A to Z; the column itself stays. Empty cells get a column of
        their own, "fruit: (empty)", on pandas and Polars alike (pandas would call it "fruit: nan",
        Polars "fruit: null"); a column that also holds the value "(empty)" is refused, so fill the
        empty cells first. As pandas pd.get_dummies(df["fruit"], prefix="fruit",
        prefix_sep=": ") and df["genes"].str.get_dummies(sep=";"), and Polars
        df["fruit"].to_dummies(separator=": ") and str.split(";").list.contains(...).
        """
        step = "spread_into_yes_no_columns"
        example = _example(f'table.{step}("fruit")', "fruit")
        if not isinstance(column, str):
            raise SimplydataError(f".{step}() needs the column name in quotes first." + example)
        self._need_columns(column)
        if _kind(self._frame.schema[column]) != "text":
            raise SimplydataError(f'.{step}() works on text, but "{column}" holds {_kind(self._frame.schema[column])} '
                                  f'values. To use them as values, first write table.turn_into_text("{column}").'
                                  + example)
        if separator is not None and (not isinstance(separator, str) or not separator):
            raise SimplydataError('separator= is the character between the values in a cell, such as separator=";".')
        empty = self._empty(column)
        n_empty = self._count(empty)
        clean = self._frame.with_columns(nw.when(~empty).then(nw.col(column)).alias(column))
        native = clean.to_native()
        label = f"{column}: (empty)"  # the column of the empty cells: the same name on both engines (approved 2026-11-25)
        if n_empty and _holds_the_value(clean[column].drop_nulls().unique().to_list(), separator, "(empty)"):
            raise SimplydataError(
                f'"{column}" holds the value "(empty)" and also empty cells, so both would make a column called '
                f'"{label}". Fill the empty cells first, for example\n'
                f'table.fill_empty_cells_in("{column}", with_value="not recorded")')
        if self._frame.implementation.is_polars():
            import polars as pl

            if separator is None:  # Polars to_dummies(separator=": "); its column of empty cells is "...: null"
                found = native[column].to_dummies(separator=": ", drop_nulls=not n_empty)
                found = found.rename({f"{column}: null": label} if n_empty else {})
            else:  # Polars str.split(";") and list.contains(value) for each value
                pieces = native[column].str.split(separator)
                values = sorted(v for v in pieces.explode().drop_nulls().unique().to_list() if v != "")
                found = pl.DataFrame({f"{column}: {v}": pieces.list.contains(v).fill_null(False) for v in values})
                if n_empty:
                    found = found.with_columns(native[column].is_null().alias(label))
            found = found.cast(pl.Boolean)
        else:
            import pandas as pd

            if separator is None:  # pandas get_dummies(prefix="fruit", prefix_sep=": ", dummy_na=True)
                found = pd.get_dummies(native[column], prefix=column, prefix_sep=": ", dummy_na=bool(n_empty))
                found = found.rename(columns={f"{column}: nan": label})
            else:  # pandas str.get_dummies(sep=";")
                found = native[column].str.get_dummies(sep=separator)
                found = found[[c for c in found.columns if c != ""]].add_prefix(f"{column}: ")
                if n_empty:
                    found[label] = native[column].isna()
            found = found.astype(bool)
        values = sorted(n for n in found.columns if n != label)
        names = values + ([label] if n_empty else [])
        if not values:
            raise SimplydataError(f'"{column}" has only empty cells, so there are no values to make columns of.')
        clash = [n for n in names if n in self._columns]
        if clash:
            raise SimplydataError(f'The table already has a column "{clash[0]}". Rename it first (rename_column).')
        found = found[names] if not self._frame.implementation.is_polars() else found.select(names)
        frame = nw.concat([self._frame, nw.from_native(found, eager_only=True)], how="horizontal")
        shown = ", ".join(f'"{n}"' for n in names[:6]) + (f" ... ({len(names)} in all)" if len(names) > 6 else "")
        print(f"Added {len(names)} yes/no column{'s' if len(names) != 1 else ''}: {shown}.")
        if n_empty:
            print(f'Note: {_rows(n_empty)} had an empty "{column}"; the column "{label}" is True there, and the '
                  "other new columns are False.")
        if separator is not None and any(n != n.rstrip() or n[len(column) + 2:] != n[len(column) + 2:].lstrip()
                                         for n in names):
            print(f"Note: some values start or end with a space, so they make columns of their own; "
                  f'table.replace_text_in("{column}", "{separator} ", with_value="{separator}") takes the spaces away '
                  "first.")
        return self._change(f'spread "{column}" into yes/no columns ({len(names)})', frame)

    @staticmethod
    def _empty_expr(column, frame):
        """Empty cells of a column of another frame (a missing value or text of only spaces)."""
        from .conditions import _empty_in

        return _empty_in(frame, column)

    # ================================================================== filling from another table
    @friendly(others={"on": "using", "by": "using"})
    def fill_empty_cells_from(self: _Same, other=None, using=None) -> _Same:
        """Fill the empty cells of this table from the matching rows of another table; filled cells never change.

        table.fill_empty_cells_from({"sample_id": [1, 2, 12], "notes": ["calm", "calm", "rain"]}, using="sample_id")   (with sdata.get_example("fjord_samples"))
        Samples 1 and 2 get the note "calm"; sample 12 keeps its own note, because a filled cell never
        changes. For each row, the other table's row with the same key gives the value of every column the
        two tables share, but only where this table's cell is empty: a value typed here is never
        overwritten. Columns only the other table has do not come in (join_with brings them). The
        other table must have each key once, so it is clear which row fills; a repeated key stops
        the word with its name. using= pairs differently named columns as in join_with:
        using={"sample_id": "sample"}. other can be a simplydata table, a pandas or Polars table, a file
        name or a dict. As pandas df.set_index("sample_id").combine_first(
        other.set_index("sample_id")) kept to this table's rows, and Polars join(how="left") then
        pl.coalesce(column, column from the other table); as R dplyr::rows_patch().
        """
        step = "fill_empty_cells_from"
        example = f'table.{step}(backup, using="sample_id")'
        right, keys, said = self._matched_other(other, using, step, example)
        shared = [c for c in self._columns if c in right.columns and c not in keys]
        if not shared:
            raise SimplydataError(f"The two tables share no column apart from {said}, so there is nothing to fill. "
                                  "To bring the other table's columns in, use join_with.")
        # an empty key matches nothing (pandas merge would match two empty keys; Polars does not), so the rows of
        # the other table with an empty key are left out before anything else, and their repeats do not matter
        right = right.filter(~nw.any_horizontal(*[nw.col(k).is_null() for k in keys], ignore_nulls=True))
        repeats = right.filter(right.select(keys).is_duplicated()).select(keys).unique()
        if len(repeats):
            shown = ", ".join(" / ".join(str(v) for v in r) for r in repeats.rows()[:5])
            raise SimplydataError(f"The other table has {said} {shown}{' ...' if len(repeats) > 5 else ''} more than "
                                  "once, so it is not clear which row fills the empty cells. Remove the repeats there "
                                  "first (remove_duplicate_rows).")
        tag = "_simplydata_other_"
        index = "_simplydata_row_"
        # a cell of only spaces in the other table is empty too: it never fills anything
        right = right.with_columns(nw.when(~self._empty_expr(c, right)).then(nw.col(c)).alias(c) for c in shared)
        usable = []
        for c in shared:
            if right[c].null_count() == len(right):  # nothing to fill from (a Polars column of only empty cells
                continue                              # has no kind, so it is left out rather than refused)
            here, there = _kind(self._frame.schema[c]), _kind(right.schema[c])
            if here != there and self._frame[c].null_count() < len(self._frame):
                raise SimplydataError(f'"{c}" holds {here} values in this table but {there} values in the other, so '
                                      "one cannot fill the other. Make them the same kind first (turn_into_numbers, "
                                      "turn_into_text, turn_into_dates).")
            usable.append(c)
        others = right.select(*keys, *[nw.col(c).alias(c + tag) for c in usable])
        joined = (self._frame.with_row_index(index).join(others, on=keys, how="left").sort(index).drop(index))
        counts = {c: 0 for c in shared}
        for c in usable:
            if joined.schema[c] != joined.schema[c + tag] and joined[c].null_count() == len(joined):
                joined = joined.with_columns(nw.col(c).cast(joined.schema[c + tag]))  # a column of only empty cells
            empty, source = self._empty_expr(c, joined), ~nw.col(c + tag).is_null()
            counts[c] = _count_in(joined, empty & source)
            # only an empty cell with a value to take changes; a cell of only spaces with nothing to take stays as it is
            joined = joined.with_columns(nw.when(empty & source).then(nw.col(c + tag)).otherwise(nw.col(c)).alias(c))
        shared = usable
        new = joined.drop([c + tag for c in shared])
        total = sum(counts.values())
        filled = "; ".join(f"{c} {n}" for c, n in counts.items() if n)
        print(f"Filled {total} empty cell{'s' if total != 1 else ''} from the other table, matched on {said}"
              + (f" ({filled})" if filled else "") + ". Filled cells kept their values.")
        still = sum(_count_in(new, self._empty_expr(c, new)) for c in shared)
        if still:
            print(f"{still} empty cell{'s' if still != 1 else ''} stayed empty: the other table has no value there "
                  "either, or no row with that key.")
        return self._change(f"fill empty cells from another table, matched on {said} ({total})", new)

