"""Other names: names from other tools (minimize, curve_fit, groupby, hist ...) point to the
simplydata word with "In simplydata this is ...", and never run."""

from __future__ import annotations

import ast
import contextlib
import datetime as _dt
import inspect
import io
import re
from pathlib import Path

import pytest

import simplydata as sdata
from simplydata._errors import MissingWordError, other_name_target
from simplydata._other_names import OTHER_NAMES
from simplydata._formula import Formula
from simplydata.chart import Chart
from simplydata.distributions import Distribution
from simplydata.numbers.blocks import NumberBlock
from simplydata.numbers.numbers import NumberGrid, Numbers
from simplydata.table import Table

OBJECTS = {"table": Table, "chart": Chart, "numbers": Numbers, "block": NumberBlock}
PREFIX = {"table": "table", "chart": "chart", "numbers": "nums", "block": "block"}


def _target_exists(written: str) -> bool:
    word = other_name_target(written)
    for prefix, owner in (("sdata.", sdata), ("table.", Table), ("chart.", Chart), ("numbers.", Numbers),
                          ("block.", NumberBlock), ("grid.", NumberGrid), ("formula.", Formula)):
        if written.startswith(prefix):
            return word in owner.__dict__ or word in dir(owner) and not word.startswith("_")
    return False


@pytest.mark.parametrize("kind", list(OTHER_NAMES))
def test_every_pointer_names_a_real_word(kind):
    for name, written in OTHER_NAMES[kind].items():
        assert _target_exists(written), f"{kind}.{name} points to {written}, which is not a simplydata word"


@pytest.mark.parametrize("kind", list(OBJECTS))
def test_no_other_name_is_a_word_itself(kind):
    cls = OBJECTS[kind]
    words = set(cls._word_names())
    for name in OTHER_NAMES[kind]:
        assert name not in words, f"{kind}.{name} is a real word, so it cannot be an other name"
        assert name not in cls._OLD_WORDS, f"{kind}.{name} is an old name"


def test_no_other_name_is_an_sdata_word():
    for name in OTHER_NAMES["sdata"]:
        assert name not in vars(sdata), f"sdata.{name} exists, so it cannot be an other name"


@pytest.mark.parametrize("name, word", [
    ("minimize", "find_where_smallest"), ("minimise", "find_where_smallest"), ("optimize", "find_where_smallest"),
    ("optimise", "find_where_smallest"), ("argmin", "find_where_smallest"), ("maximize", "find_where_biggest"),
    ("root", "solve"), ("fsolve", "solve"), ("brentq", "solve"), ("uniroot", "solve"),
    ("curve_fit", "fit_formula"), ("nls", "fit_formula"), ("polyfit", "fit_curve"), ("linregress", "fit_line"),
    ("lm", "fit_line"), ("interpolate", "find_values_at"), ("interp", "find_values_at"), ("approx", "find_values_at"),
    ("spline", "find_values_at"), ("griddata", "make_map_of"), ("pdf", "distribution"), ("dnorm", "distribution"),
    ("cdf", "distribution"), ("pnorm", "distribution"), ("ppf", "distribution"), ("qnorm", "distribution"),
    ("quantile", "find_percentile"), ("rvs", "make_random_numbers"), ("rnorm", "make_random_numbers"), ("read_csv", "table"),
])
def test_sdata_other_names_point_to_the_word_and_never_run(name, word):
    with pytest.raises(MissingWordError) as info:
        getattr(sdata, name)
    text = str(info.value)
    assert text.startswith(f"simplydata has no word called sdata.{name}().")
    assert "\nIn simplydata this is " in text and f"{word}(" in text
    assert not hasattr(sdata, name)  # an AttributeError, so Python tools keep working


def test_distribution_pointers_name_the_distribution_words():
    for name, word in (("pdf", ".find_density_at(60)"), ("cdf", ".find_chance_that_value(is_below=60)"), ("ppf", ".find_percentile(95)"),
                       ("qnorm", ".find_cut_off(with_chance_above=0.025)")):
        with pytest.raises(MissingWordError, match=r"sdata\.distribution\(\"normal\".*" + word.replace("(", r"\(")
                           .replace(")", r"\)").replace(".", r"\.")):
            getattr(sdata, name)


@pytest.mark.parametrize("name, word", [
    ("groupby", "find_average_of"), ("merge", "join_with"), ("concat", "add_rows_from"),
    ("pivot", "spread_into_columns"), ("melt", "gather_into_rows"), ("head", "show_first_rows"),
    ("tail", "show_last_rows"), ("iloc", "keep_rows_by_position"), ("filter", "keep_rows_where"), ("dropna", "remove_rows_with_empty_cells_in"),
    ("fillna", "fill_empty_cells_in"), ("sort_values", "sort_by"), ("mean", "find_average_of"), ("plot", "start_chart"),
    ("curve_fit", "fit_formula"), ("polyfit", "fit_curve"), ("linregress", "fit_line"), ("interpolate", "find_values_at"),
    ("griddata", "make_map_of"), ("fitdistr", "fit_distribution_to"), ("to_csv", "save"), ("addWorksheet", "save"), ("ExcelWriter", "save"), ("value_counts", "count_each"),
    ("slice", "keep_rows_by_position"), ("take", "keep_rows_by_position"), ("gather_every", "keep_rows_by_position"),
    ("drop_index", "remove_rows_by_position"), ("at", "get_cell_at"), ("iat", "get_cell_at"), ("item", "get_cell_at"),
    ("select_dtypes", "keep_columns"), ("reverse", "reverse_rows"), ("flip", "reverse_rows"),
    ("mask", "replace_values_in"), ("clip", "replace_values_in"),
])
def test_table_other_names(name, word):
    table = sdata.table(sdata.get_example("marks"))
    with pytest.raises(MissingWordError) as info:
        getattr(table, name)
    text = str(info.value)
    assert text.startswith(f"simplydata has no step called .{name}().")
    assert f"In simplydata this is table.{word}(" in text
    assert f'sdata.help("{word}")' in text


def test_a_table_interpolate_points_to_both_words():
    with pytest.raises(MissingWordError, match="find_values_at.*fill_empty_cells_in"):
        sdata.table(sdata.get_example("growth")).interpolate()


@pytest.mark.parametrize("name, word", [
    ("plot", "draw_lines"), ("hist", "draw_histogram"), ("boxplot", "draw_boxes"), ("kdeplot", "draw_density"), ("ecdf", "draw_cumulative_share"),
    ("axhline", "draw_line_at_y"), ("axvline", "draw_line_at_x"), ("xlabel", "label_x"), ("title", "write_title_on_top"),
    ("xlim", "set_range_x"), ("savefig", "save"), ("curve_fit", "fit_formula"), ("polyfit", "fit_curve"),
    ("probplot", "draw_qq_dots"), ("lowess", "draw_smooth_line"), ("abline", "draw_line_with_slope"), ("legend", "put_legend_on_right"),
    ("grid", "show_grid"), ("facet_wrap", "draw_one_chart_for_each_group_in"), ("stat_function", "draw_curve"),
])
def test_chart_other_names(name, word):
    with pytest.raises(MissingWordError, match=rf"In simplydata this is chart\.{word}\("):
        getattr(sdata.chart(), name)


def test_number_other_names_and_grids():
    with pytest.raises(MissingWordError, match=r"In simplydata this is numbers\.fit_distribution\("):
        sdata.number_list([1, 2, 3]).fit
    with pytest.raises(MissingWordError, match=r"In simplydata this is grid\.start_chart\(\)"):
        sdata.number_grid([[1, 2], [3, 4]]).plot  # the grid's own name
    with pytest.raises(MissingWordError) as info:
        sdata.number_grid([[1, 2], [3, 4]]).fit  # grids cannot fit a distribution: no pointer
    assert "In simplydata" not in str(info.value)
    with pytest.raises(MissingWordError, match=r"Did you mean numbers\.find_average\(\)"):
        sdata.number_list([1, 2]).mean  # the older hints still work


def test_unknown_sdata_names_get_did_you_mean():
    with pytest.raises(MissingWordError, match=r"Did you mean sdata\.find_where_smallest\(\)"):
        sdata.find_smalest  # a typo of the old name still finds the word as it is written now
    with pytest.raises(MissingWordError, match=r"Did you mean sdata\.find_where_smallest\(\)"):
        sdata.find_where_smalest
    with pytest.raises(AttributeError):
        sdata.__not_there__
    assert hasattr(sdata, "__version__") and hasattr(sdata, "__path__")


def test_help_explains_other_names(capsys):
    sdata.help("minimize")
    out = capsys.readouterr().out
    assert out.startswith('simplydata has no word called "minimize": it is a name from other tools.')
    assert 'In simplydata this is sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5]).' in out
    assert 'sdata.help("find_where_smallest")' in out
    sdata.help("plot")  # a name with a pointer on sdata, on tables and on charts
    out = capsys.readouterr().out
    assert "  table.plot: In simplydata this is table.start_chart()." in out
    assert '  chart.plot: In simplydata this is chart.draw_lines(x="year", y="population").' in out
    sdata.help("table.groupby")
    assert "table.find_average_of(" in capsys.readouterr().out


def test_grid_numbers_keep_their_own_words():
    assert isinstance(sdata.number_grid([[1, 2]]), NumberGrid)


# ---------------------------------------------------------------- tables finishing PR: the API audit's pointers
# Every pandas 3.1.1 / Polars 2.1.0 name the audit (2026-11-25) found with a simplydata word but no pointer, or with a
# wrong one: what sdata.help says now. Names inside .str, .dt and groupby() are typed with their namespace.
AUDIT_POINTERS = [
    ("apply", "add_column"), ("arg_max", "keep_biggest_rows"), ("arg_min", "keep_smallest_rows"),
    ("astype", "turn_into_numbers"), ("backward_fill", "fill_empty_cells_in"),
    ("bfill", "fill_empty_cells_in"), ("bottom_k", "keep_smallest_rows"), ("bottom_k_by", "keep_smallest_rows"),
    ("case_when", "add_group_column"), ("cast", "turn_into_numbers"), ("concat_str", "add_column"),
    ("cum_count", "add_running_column"), ("cum_max", "add_running_column"),
    ("cum_min", "add_running_column"), ("cummax", "add_running_column"), ("cummin", "add_running_column"),
    ("cumprod", "add_running_column"), ("date", "add_column"), ("dt.ceil", "round_dates_in"),
    ("dt.date", "add_column_with_part_of_date"), ("dt.day", "add_column_with_part_of_date"),
    ("dt.day_name", "add_column_with_part_of_date"), ("dt.day_of_week", "add_column_with_part_of_date"),
    ("dt.day_of_year", "add_column_with_part_of_date"), ("dt.dayofweek", "add_column_with_part_of_date"),
    ("dt.dayofyear", "add_column_with_part_of_date"), ("dt.daysinmonth", "add_column_with_part_of_date"),
    ("dt.floor", "round_dates_in"), ("dt.hour", "add_column_with_part_of_date"),
    ("dt.minute", "add_column_with_part_of_date"), ("dt.month", "add_column_with_part_of_date"),
    ("dt.month_name", "add_column_with_part_of_date"), ("dt.month_start", "round_dates_in"),
    ("dt.ordinal_day", "add_column_with_part_of_date"), ("dt.quarter", "add_column_with_part_of_date"),
    ("dt.replace", "as_polars"), ("dt.round", "round_dates_in"), ("dt.second", "add_column_with_part_of_date"),
    ("dt.time", "add_column_with_part_of_date"), ("dt.total_days", "add_column"), ("dt.total_hours", "add_column"),
    ("dt.total_minutes", "add_column"), ("dt.total_seconds", "add_column"), ("dt.truncate", "round_dates_in"),
    ("dt.week", "add_column_with_part_of_date"), ("dt.weekday", "add_column_with_part_of_date"),
    ("dt.year", "add_column_with_part_of_date"), ("ewm_mean", "add_smoothed_column"),
    ("ewm_mean_by", "add_smoothed_column"), ("ffill", "fill_empty_cells_in"), ("filter", "keep_rows_where"),
    ("format", "add_column"), ("forward_fill", "fill_empty_cells_in"), ("from_arrow", "table"),
    ("from_dataframe", "table"), ("from_dict", "table"), ("from_dicts", "table"), ("from_numpy", "table"),
    ("from_pandas", "table"), ("from_records", "table"), ("group_by_dynamic", "find_average_of"),
    ("groupby.apply", "as_pandas"), ("groupby.bfill", "as_pandas"),
    ("groupby.cummax", "add_running_column"), ("groupby.cummin", "add_running_column"),
    ("groupby.ffill", "as_pandas"), ("groupby.filter", "keep_groups_where"),
    ("groupby.get_group", "keep_rows_where"), ("groupby.idxmax", "keep_biggest_rows"),
    ("groupby.idxmin", "keep_smallest_rows"), ("groupby.kurt", "find_summary_of"),
    ("groupby.sem", "find_summary_of"), ("groupby.skew", "find_summary_of"), ("groupby.var", "find_summary_of"),
    ("has_nulls", "count_empty_cells_in"), ("hasnans", "count_empty_cells_in"), ("idxmax", "keep_biggest_rows"),
    ("idxmin", "keep_smallest_rows"), ("insert", "add_column"), ("insert_column", "add_column"),
    ("interpolate_by", "fill_empty_cells_in"), ("is_between", "keep_rows_where"), ("is_in", "keep_rows_where"),
    ("is_not_null", "keep_rows_where"), ("isin", "keep_rows_where"), ("kurt", "find_summary_of"),
    ("kurtosis", "find_summary_of"), ("map", "replace_values_in"), ("map_batches", "add_column"),
    ("map_columns", "add_column"), ("map_elements", "add_column"), ("map_rows", "add_column"),
    ("max_by", "keep_biggest_rows"), ("min_by", "keep_smallest_rows"), ("notna", "keep_rows_where"),
    ("notnull", "keep_rows_where"), ("null_count", "count_empty_cells_in"), ("read_spss", "table"),
    ("read_sql_query", "run_sql"), ("read_stata", "table"), ("reindex", "add_missing_combinations_of"),
    ("replace_strict", "replace_values_in"), ("rolling_max", "add_rolling_column"),
    ("rolling_max_by", "add_rolling_column"), ("rolling_mean", "add_rolling_column"),
    ("rolling_mean_by", "add_rolling_column"), ("rolling_median", "add_rolling_column"),
    ("rolling_median_by", "add_rolling_column"), ("rolling_min", "add_rolling_column"),
    ("rolling_min_by", "add_rolling_column"), ("rolling_quantile", "add_rolling_column"),
    ("rolling_quantile_by", "add_rolling_column"), ("rolling_std", "add_rolling_column"),
    ("rolling_std_by", "add_rolling_column"), ("rolling_sum", "add_rolling_column"),
    ("rolling_sum_by", "add_rolling_column"), ("rolling_var", "add_rolling_column"),
    ("rolling_var_by", "add_rolling_column"), ("sem", "find_summary_of"), ("skew", "find_summary_of"),
    ("str.count", "add_column"), ("str.extract", "add_column_with_part_of_text"),
    ("str.extract_groups", "add_column_with_part_of_text"), ("str.head", "add_column_with_part_of_text"),
    ("str.join", "add_column"), ("str.len", "add_column"), ("str.ljust", "add_zeros_in_front_of"),
    ("str.lstrip", "remove_extra_spaces_in"), ("str.pad", "add_zeros_in_front_of"),
    ("str.replace", "replace_text_in"), ("str.replace_all", "replace_text_in"), ("str.reverse", "as_polars"),
    ("str.rstrip", "remove_extra_spaces_in"), ("str.slice", "add_column_with_part_of_text"),
    ("str.split", "split_column"), ("str.strip_chars", "remove_extra_spaces_in"),
    ("str.strip_chars_end", "remove_extra_spaces_in"), ("str.strip_chars_start", "remove_extra_spaces_in"),
    ("str.tail", "add_column_with_part_of_text"), ("str.title", "turn_into_title_case"),
    ("str.to_date", "turn_into_dates"),
    ("str.to_decimal", "turn_into_numbers"), ("str.to_integer", "turn_into_numbers"),
    ("str.to_lowercase", "turn_into_lowercase"), ("str.to_time", "turn_into_dates"),
    ("str.to_uppercase", "turn_into_uppercase"), ("time", "add_column_with_part_of_date"), ("to_excel", "save"),
    ("to_feather", "save"), ("to_html", "save"), ("to_json", "save"), ("to_list", "get_column"),
    ("to_series", "get_column"), ("to_stata", "save"), ("tolist", "get_column"), ("top_k", "keep_biggest_rows"),
    ("top_k_by", "keep_biggest_rows"), ("truncate", "round_dates_in"), ("update", "fill_empty_cells_from"),
    ("values", "get_column"), ("var", "find_summary_of"), ("when", "add_group_column"),
    ("where", "replace_values_in"), ("write_ipc", "save"), ("write_json", "save"), ("write_ndjson", "save"),
]


@pytest.mark.parametrize("typed, word", AUDIT_POINTERS)
def test_every_name_the_audit_found_points_to_its_word(typed, word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert "it is a name from other tools" in out, typed
    assert f'sdata.help("{word}")' in out.splitlines()[-1], (typed, out)


@pytest.mark.parametrize("typed, shown, word, not_word", [
    ("str.replace", "str.replace", "replace_text_in", "replace_values_in"),
    ("Series.str.replace", "str.replace", "replace_text_in", "replace_values_in"),
    ('df["name"].str.replace("Mr ", "")', "str.replace", "replace_text_in", "replace_values_in"),
    ('pl.col("name").str.contains("an")', "str.contains", "keep_rows_where", None),
    ("str.count", "str.count", "count_text", "count_rows"),
    ("str.len", "str.len", "length(name)", "count_rows"),
    ("str.split", "str.split", "split_column", "make_one_table_for_each_group_in"),
    ("str.slice", "str.slice", "add_column_with_part_of_text", "keep_rows_by_position"),
    ("str.head", "str.head", "first_characters=", "show_first_rows"),
    ("str.join", "str.join", "by_joining_text=", "join_with"),
    ("str.title", "str.title", "turn_into_title_case", "write_title_on_top"),
    ("dt.round", "dt.round", "round_dates_in", "round_numbers_in"),
    ("Series.dt.year", "dt.year", 'part="year"', None),
    ('pl.col("date").dt.truncate("1mo")', "dt.truncate", "round_dates_in", None),
    ("dt.replace", "dt.replace", "as_polars", "replace_values_in"),
    ("groupby.filter", "groupby.filter", "keep_groups_where", "keep_rows_where"),
    ('df.groupby("class").filter', "groupby.filter", "keep_groups_where", "keep_rows_where"),
    ("DataFrameGroupBy.head", "groupby.head", "keep_first_rows", "show_first_rows"),
    ('df.group_by("class").mean', "groupby.mean", "find_average_of", None),  # not listed: the table meaning
    ("pd.read_csv", "read_csv", 'sdata.table("my_file.csv")', None),
    ("pl.DataFrame.join", "join", "join_with", None),
    # review of the tables finishing PR
    ("groupby.ffill", "groupby.ffill", '.groupby("shop")["price"].ffill()', "for_each_group_in"),
    ("groupby.ngroup", "groupby.ngroup", 'when_tied="no gaps"', "add_row_number_column"),
    ("groupby.cumcount", "groupby.cumcount", "add_row_number_column", "add_rank_column"),
    ("groupby.count", "groupby.count", 'show=["count"]', None),
    ("groupby.describe", "groupby.describe", '"percentile 25", "median", "percentile 75"', "skewness"),
    ("str.split", "str.split", 'into=["first_name", "last_name"]', None),
    ("notna", "notna", "is_empty=False", "add_is_empty_column"),
    ("Series.Str.Replace", "str.replace", "replace_text_in", None),  # any capitals
    ('df["name"].str.replace(', "str.replace", "replace_text_in", None),  # a bracket left open
    ("marks.merge", "merge", "join_with", None),  # a table of your own in front
    ("df2.groupBy.filter", "groupby.filter", "keep_groups_where", None),
])
def test_names_inside_a_namespace_point_to_their_own_word(typed, shown, word, not_word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert out.startswith(f'simplydata has no word called "{shown}": it is a name from other tools.'), out
    assert word in out
    if not_word:
        assert not_word not in out


def test_a_bare_name_lists_its_namespace_meanings_too(capsys):
    sdata.help("replace")
    out = capsys.readouterr().out
    assert '  table.replace: In simplydata this is table.replace_values_in("class", "A", with_value="Alpha").' in out
    assert '  str.replace: In simplydata this is table.replace_text_in("name", "Mr ", with_value="").' in out
    sdata.help("filter")
    out = capsys.readouterr().out
    assert "  table.filter: " in out and "  groupby.filter: " in out and "keep_groups_where" in out


def test_a_text_or_date_name_never_falls_back_to_the_table_meaning(capsys):
    sdata.help("str.mean")  # not a text step: no pointer, not the table's find_average_of
    assert "find_average_of" not in capsys.readouterr().out


@pytest.mark.parametrize("name, words", [
    ("cummax", ['show="biggest"']), ("cummin", ['show="smallest"']), ("cumprod", ['show="product"']),
    ("cum_count", ['show="count"']),
    ("filter", ["table.keep_rows_where(", 'table.keep_columns(contains="week")']),
    ("isin", ['is_one_of=["A", "B"]', "table.keep_rows_found_in("]),
    ("to_excel", ['table.save("results.xlsx")']),
    ("where", ["table.replace_values_in(", "in_rows_where=", "table.keep_rows_where("]),
    ("unique", ['table.get_different_values_in("class")', "table.remove_duplicate_rows() for whole rows"]),
    ("count", ["table.count_rows()", "table.describe_columns()", 'table.count_each("class")']),
    ("astype", ["turn_into_numbers", "turn_into_text", "turn_into_dates", "turn_into_categories"]),
    ("str", ["table.describe_columns()", "str.replace is replace_text_in"]),
    ("dt", ["table.add_column_with_part_of_date("]),
    ("between", ["is_between=[50, 70]"]),
])
def test_table_pointers_the_audit_found_wrong_or_missing(name, words):
    table = sdata.table(sdata.get_example("marks"))
    with pytest.raises(MissingWordError) as info:
        getattr(table, name)
    for word in words:
        assert word in str(info.value), (name, word)


@pytest.mark.parametrize("name, word", [("from_dict", "table"), ("from_pandas", "table"), ("read_sql_query", "run_sql"),
                                        ("read_spss", "table")])
def test_sdata_pointers_from_the_audit(name, word):
    with pytest.raises(MissingWordError, match=rf"In simplydata this is sdata\.{word}\("):
        getattr(sdata, name)


def test_other_name_parts():
    from simplydata._other_names import other_name_parts

    assert other_name_parts("str.replace") == ("text", "replace")
    assert other_name_parts('df["a b"].str.split(";", n=1)') == ("text", "split")
    assert other_name_parts("pd.Series.dt.year") == ("dates", "year")
    assert other_name_parts('df.groupby(["a", "b"]).filter') == ("groups", "filter")
    assert other_name_parts("pd.merge") == (None, "merge")
    assert other_name_parts("merge") is None
    assert other_name_parts("chart.draw_bars") is None  # not a pandas or Polars name
    assert other_name_parts("df.str.replace(") == ("text", "replace")
    assert other_name_parts('pl.col("a").STR.contains("x"') == ("text", "contains")
    assert other_name_parts("marks.merge") == (None, "merge")
    assert other_name_parts("a.b.merge") is None  # two names of your own: not read as a qualifier
    assert other_name_parts("simplydata.table") is None and other_name_parts("sd.table") is None


@pytest.mark.parametrize("typed, heading", [
    ("simplydata.table", "sdata.table()"), ("sd.table", "sdata.table()"),
    ("weather.draw_bars", "chart.draw_bars()"), ("students.keep_rows_where", "table.keep_rows_where()"),
])
def test_a_name_of_your_own_in_front_of_a_word_finds_the_word(typed, heading, capsys):
    """simplydata.table and sd.table are sdata.table; weather.draw_bars is the word draw_bars, not a name from another
    tool (sdata.help("simplydata.table") said "table" was an other name, pointing to count_each)."""
    sdata.help(typed)
    out = capsys.readouterr().out
    assert out.startswith(heading), out[:200]
    assert "name from other tools" not in out


# ---------------------------------------------------------------- every pointer's call is a call that works
# A pointer that names a word with a wrong option or value is worse than none. Two checks:
# 1. every call written in a pointer (sdata.x(...), table.x(...), chart.x(...), numbers.x(...), block.x(...)) names a
#    real word, and every option it gives is an option of that word;
# 2. every table call runs (the calls of "a, then b" one after the other on one table) on the first practice table
#    it works on, or on _pointer_table(), made for the columns the pointers name. An option value a word does not
#    know ("does not know ...") or an option it lacks fails the test on every table. A word that runs R is skipped
#    where R is missing; the calls in NEEDS_PREP need a step first that the pointer does not write.

OWNERS = {"sdata": sdata, "table": Table, "chart": Chart, "numbers": Numbers, "nums": Numbers, "grid": NumberGrid,
          "block": NumberBlock, "formula": Formula, "distribution": Distribution}
# A call is not run when it writes "..." (a shortened list), or uses a name of yours the pointer does not make
# (your own function make_label, another table called rain or national): KNOWN_NAMES are the ones the test gives.
KNOWN_NAMES = {"table", "sdata", "other_table", "other", "True", "False", "None"}
# Calls that need a step first, which the pointer leaves out to stay short (they are checked by name only):
NEEDS_PREP = {
    'find_correlation_between("bmi", "chl"': 'R mice::nhanes: sdata.get_example("nhanes", from_r_package="mice")',
    'compare_counts_of("result"': 'a "result" column, made with add_group_column first',
    'explain("case", using=["smoker"]': "a matched case-control table (R survival::infert or your own)",
    'explain("germinated"': "seed germination counts (R's orobanche data)",
    'compare_before_and_after("Maths", "Science")': "the marks spread into one column per subject first",
    'compare_matched_columns("week_0"': "a pain score in one column per week",
    'compare_correlations("hours", "marks"': "one subject kept first (one row per child)",
    'compare_each_pair_of("pain"': "a pain score for each patient and week",
    'compare_each_pair_of("time", for_each_group_in="method"': "a time for each player and method",
    'find_risk_over_time(time="time", event="event"': "a hospital stay table with competing events",
    'explain_survival(time="months", event="outcome"': "a relapse table with competing events",
    'followed_from="entry_day"': "a survival table with a day of entry",
    '"visitors", sorted_by="month"': "one museum kept first (the visitors table has two)",
    'find_change_points_in("nitrate"': "one station kept first (the river table has two)",
    'add_correspondence_axes(columns=["blaTEM", "sul1"])': "counts of more genes than the resistome table names",
    'find_hidden_factors_behind(["q1"': "a questionnaire with answers q1 to q6",
    'values_above=30, sorted_by="date"': 'the "date" of the rain table turned into dates first (it is read as text)',
}


def _pointer_calls(written: str):
    """The calls a pointer writes: [(object, word, call text)], in order."""
    found = []
    for m in re.finditer(r"(?<![\w.\"])(sdata|table|chart|numbers|grid|block|formula|distribution)\.(\w+)\(",
                         written):
        depth, i = 1, m.end()
        while i < len(written) and depth:
            depth += {"(": 1, ")": -1}.get(written[i], 0)
            i += 1
        found.append((m.group(1), m.group(2), written[m.start():i]))
    return found


def _all_pointer_calls():
    seen = {}
    for kind, names in OTHER_NAMES.items():
        for name, written in names.items():
            seen.setdefault(written, (kind, name))
    return [(kind, name, written) for written, (kind, name) in seen.items()]


@pytest.mark.parametrize("kind, name, written", [pytest.param(*c, id=f"{c[0]}.{c[1]}") for c in _all_pointer_calls()])
def test_every_pointer_call_names_a_word_and_its_options(kind, name, written):
    for owner_name, word, call in _pointer_calls(written):
        owner = OWNERS[owner_name]
        function = getattr(owner, word, None)
        assert function is not None, f"{kind}.{name}: {call} names no word"
        if call.endswith("=)") or "..." in call:  # a description such as add_column(by_running=), not a call
            continue
        try:
            tree = ast.parse(call.replace("...", "None"), mode="eval").body
        except SyntaxError:
            pytest.fail(f"{kind}.{name}: {call} is not a Python call")
        if not callable(function) or isinstance(function, type):
            continue
        parameters = inspect.signature(function).parameters
        if any(p.kind is p.VAR_KEYWORD for p in parameters.values()):
            continue
        unknown = [k.arg for k in tree.keywords if k.arg not in parameters]
        assert not unknown, f"{kind}.{name}: {call} gives {unknown}, which {word}() does not have"


def _pointer_table():
    """One small table with the columns the data-handling pointers name."""
    day = _dt.datetime
    return sdata.table({
        "name": ["Mr Asha Ali", "Dr Ben Berg", "Chen Li", "Dina An"], "class": ["A", "B", "A", "C"],
        "marks": [61, 73, 81, 55], "hours": [6.3, 6.4, 7.9, 3.0], "height": [144, 152, 151, 149],
        "sample_id": ["S001", "S012", "S7", "S070"], "genes": ["sul1;tetM", "sul1", "tetM;intI1", "sul1"],
        "price": [1.5, None, 2.0, 2.5], "sales": [10.0, None, 12.0, 9.0], "shop": ["N", "N", "S", "S"],
        "time": [day(2026, 5, 12, 8, 47), day(2026, 5, 12, 9, 5), day(2026, 5, 13, 23, 10), day(2026, 5, 14, 0, 30)],
        "date": [day(2026, 1, 1), day(2026, 1, 2), day(2026, 1, 4), day(2026, 1, 5)],
        "start": [day(2026, 1, 1), day(2026, 2, 1), day(2026, 3, 1), day(2026, 4, 1)],
        "end": [day(2026, 1, 9), day(2026, 2, 3), day(2026, 3, 30), day(2026, 4, 2)],
        "phone": ["555 01", None, "555 03", None], "mobile": ["900 01", "900 02", None, "900 04"], "id": [1, 2, 3, 4],
        "when": ["03/15/2026", "04/01/2026", "12/31/2026", "01/02/2026"],
        "year": [2026, 2026, 2027, 2027], "month": [5, 6, 7, 8], "day": [12, 3, 30, 1],
        "weight": [41.0, 45.5, 39.9, 50.2], "factor": [1.1, 1.2, 0.9, 1.0], "population": [12.0, 12.6, 3.1, 3.3],
        "country": ["Applia", "Applia", "Bananda", "Bananda"], "temperature": [8.3, 10.3, 11.0, 9.2],
        "signal": [0.1, 0.4, 0.2, 0.3], "fruit": ["apple", "pear", "apple|pear", "plum"],
        "school": ["X", "X", "Y", "Y"], "week": [1, 1, 2, 2], "people": [3, 1, 2, 5],
        # families for 100 %, batches 1-2: Unix seconds (from_epoch) and clock times (dt.combine)
        "seconds": [1764288000, 1764291600, 1764374400, 1764460800], "clock": ["08:30", "09:05", "23:10", "00:30"],
    })


EXAMPLES = sorted(p.stem for p in (Path(sdata.__file__).parent / "data").glob("*.csv"))
BAD = ("has no option called", "does not know", "SyntaxError", "TypeError", "is not a Python call")


def _runs_here(call: str) -> bool:
    """A call this test can run: a whole call, with no "...", no step left out (NEEDS_PREP) and no name of yours."""
    if call.endswith("=)") or "..." in call or any(prep in call for prep in NEEDS_PREP):
        return False
    names = {node.id for node in ast.walk(ast.parse(call, mode="eval")) if isinstance(node, ast.Name)}
    return names <= KNOWN_NAMES


def _runnable_pointers():
    out = []
    for kind, name, written in _all_pointer_calls():
        calls = [c for o, w, c in _pointer_calls(written) if o == "table"]
        if " then " in written or "count first" in written:  # one call after the other, on one table
            if calls and all(_runs_here(call) for call in calls):
                out.append(pytest.param(calls, id=f"{kind}.{name}"))
        else:  # "a, or b": each call on its own
            out += [pytest.param([call], id=f"{kind}.{name}-{i}") for i, call in enumerate(calls, 1)
                    if _runs_here(call)]
    return out


@pytest.mark.parametrize("calls", _runnable_pointers())
def test_every_table_pointer_call_runs_on_a_practice_table(calls, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # table.save("results.csv") and friends write here
    import pandas as pd  # table.save("clipboard") must never touch this computer's real clipboard in a test

    copied = {}
    monkeypatch.setattr(pd.DataFrame, "to_clipboard", lambda self, **kw: copied.setdefault("table", self))
    monkeypatch.setattr(pd, "read_clipboard", lambda **kw: copied["table"])
    errors = []
    for source in [None, *EXAMPLES]:
        table = _pointer_table() if source is None else sdata.get_example(source)
        scope = {"sdata": sdata, "table": table, "other_table": table.make_copy(), "other": table.make_copy()}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                for call in calls:
                    exec(call, scope)  # the pointer's own text, run as written
            return
        except Exception as problem:  # noqa: BLE001 - a table without these columns is tried next
            text = f"{type(problem).__name__}: {problem}"
            if type(problem).__name__ == "RMissing":  # the word runs R, and R is not here: checked where R is
                pytest.skip(f"{calls} needs R")
            if "needs SciPy" in text and "or newer" in text:  # checked where that SciPy is installed
                pytest.skip(f"{calls}: {text.splitlines()[0]}")
            assert not any(bad in text for bad in BAD), f"{calls} on {source or 'POINTER_TABLE'}: {text}"
            errors.append(f"{source or 'POINTER_TABLE'}: {text.splitlines()[0]}")
    pytest.fail(f"{calls} ran on no practice table:\n" + "\n".join(errors[:5]))


# ---------------------------------------------------------------- charts finishing PR: the chart pointers
# The API audit of matplotlib 3.11.2 and seaborn 0.13.2 (2026-11-27; plt., Axes, Figure, Axes3D and sns. names): what
# sdata.help says now. Names typed with plt., ax., fig. or sns. in front look among the chart pointers first.
CHART_AUDIT_POINTERS = [
    ("plt.gcf", "as_matplotlib"), ("plt.gca", "as_matplotlib"), ("ax.get_figure", "as_matplotlib"),
    ("plt.figure", "as_matplotlib"), ("matplotlib", "as_matplotlib"), ("ax.table", "as_matplotlib"),
    ("sns.lineplot", "draw_lines"), ("sns.relplot", "draw_dots"), ("sns.displot", "draw_histogram"),
    ("sns.catplot", "draw_bars"), ("sns.pairplot", "draw_all_pairs"), ("sns.PairGrid", "draw_all_pairs"),
    ("sns.JointGrid", "draw_dots"), ("sns.clustermap", "draw_heatmap"), ("ax.grouped_bar", "draw_bars"),
    ("plt.stackplot", "draw_area"), ("ax.step", "draw_lines"), ("ax.stairs", "draw_lines"),
    ("plt.matshow", "draw_heatmap"), ("ax.pcolor", "draw_heatmap"), ("ax.tricontourf", "draw_contour"),
    ("ax.plot_trisurf", "draw_surface"), ("ax.plot_wireframe", "draw_surface"), ("ax.scatter3D", "draw_dots_3d"),
    ("ax.set_top_view", "look_from"), ("ax.text3D", "write_note"), ("ax.bar_label", "draw_bars"),
    ("plt.loglog", "use_log_scale_x"), ("ax.invert_xaxis", "flip_x"), ("ax.invert_yaxis", "flip_y"),
    ("ax.set_xbound", "set_range_x"), ("ax.set_zlim3d", "set_range_z"), ("ax.set_xticklabels", "put_ticks_x"),
    ("ax.set_yticklabels", "put_ticks_y"), ("plt.locator_params", "put_ticks_x"),
    ("ax.ticklabel_format", "write_ticks_y_as"), ("fig.autofmt_xdate", "rotate_labels_x"),
    ("ax.tick_params", "rotate_labels_x"), ("plt.axis", "hide_frame"), ("sns.despine", "hide_frame"),
    ("plt.colorbar", "label_colour_bar"), ("plt.clim", "use_colour_scale"), ("plt.get_cmap", "use_colour_scale"),
    ("plt.viridis", "use_colour_scale"), ("sns.color_palette", "use_colours"), ("sns.set_palette", "use_colours"),
    ("ax.set_prop_cycle", "use_colours"), ("sns.diverging_palette", "use_colour_scale"),
    ("sns.set_theme", "use_style"), ("sns.set_style", "use_style"), ("sns.set_context", "use_style"),
    ("plt.rc_context", "use_style"), ("plt.figtext", "write_caption_at_bottom"), ("fig.set_figwidth", "set_size"),
    ("fig.set_dpi", "save"), ("ax.indicate_inset_zoom", "add_zoom_box"),
    ("ax.sharex", "draw_one_chart_for_each_group_in"), ("plt.subplot", "put_in_rows_and_columns"),
    ("plt.subplot_mosaic", "put_in_rows_and_columns"), ("fig.add_subplot", "put_in_rows_and_columns"),
    ("fig.subfigures", "put_in_rows_and_columns"), ("plt.figlegend", "put_side_by_side"),
    ("ax.get_yticklabels", "get_text_drawn"), ("ax.get_legend_handles_labels", "get_text_drawn"),
    ("fig.get_suptitle", "get_text_drawn"), ("ax.get_lines", "get_numbers_drawn"),
    ("ax.get_xbound", "get_scales_drawn"), ("ax.xaxis_inverted", "get_scales_drawn"),
    ("ax.get_zlim", "get_scales_drawn"), ("plt.cohere", "find_coherence_with"),
    ("sns.get_dataset_names", "get_example"), ("ax.quiver", "as_matplotlib"), ("sns.boxenplot", "as_matplotlib"),
    ("plt.streamplot", "as_matplotlib"), ("ax.margins", "as_matplotlib"),
    # review of the charts finishing PR
    ("ax.triplot", "as_matplotlib"), ("sns.set", "use_style"), ("plt.style.use", "use_style"),
    ("plt.tight_layout", "set_size"), ("plt.subplots_adjust", "set_size"), ("fig.set_layout_engine", "set_size"),
    ("Axes3D.scatter", "draw_dots_3d"), ("Axes3D.plot", "draw_lines_3d"), ("Axes3D.bar", "draw_bars_3d"),
    ("Axes3D.plot_surface", "draw_surface"), ("Axes3D.plot_wireframe", "draw_surface"),
    ("Axes3D.set_zlabel", "label_z"), ("Axes3D.view_init", "look_from"),
    ("Axes3D.set_title", "write_title_on_top"),  # not in the 3D list: the chart meaning
]


@pytest.mark.parametrize("typed, word", CHART_AUDIT_POINTERS)
def test_every_chart_name_the_audit_found_points_to_its_word(typed, word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert "it is a name from other tools" in out, (typed, out)
    assert f'sdata.help("{word}")' in out.splitlines()[-1], (typed, out)


@pytest.mark.parametrize("typed, shown, word, not_word", [
    ("plt.title", "plt.title", "write_title_on_top", "str.title"),  # not pandas' Title Case
    ("ax.set_title", "ax.set_title", "write_title_on_top", None),
    ("fig.axes[0].set_xlabel", "axes.set_xlabel", "label_x", None),  # brackets, and two names in front
    ("matplotlib.pyplot.hist", "pyplot.hist", "draw_histogram", None),
    ("df.plot.bar", "plot.bar", "draw_bars", None),  # pandas' plotting namespace
    ("plt.subplots", "plt.subplots", "put_in_rows_and_columns", "population"),  # the chart meaning, not sdata's
    ("ax.table", "ax.table", "as_matplotlib", "count_each"),  # not the table pointer
    ("sns.load_dataset", "sns.load_dataset", "get_example", None),  # not a chart pointer: an sdata one
    ("Figure", "Figure", "as_matplotlib", None),
])
def test_matplotlib_and_seaborn_names_look_among_the_chart_words_first(typed, shown, word, not_word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert out.startswith(f'simplydata has no word called "{shown}": it is a name from other tools.'), out
    assert word in out
    if not_word:
        assert not_word not in out


@pytest.mark.parametrize("typed, heading", [("plt.show", "chart.show()"), ("fig.show", "chart.show()"),
                                            ("ax.as_matplotlib", "chart.as_matplotlib()")])
def test_a_chart_word_with_plt_or_ax_in_front_explains_the_word(typed, heading, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert out.startswith(heading), out[:200]


def test_other_name_parts_reads_matplotlib_and_seaborn_names():
    from simplydata._other_names import other_name_parts, other_name_space

    assert other_name_parts("plt.hist") == ("chart", "hist")
    assert other_name_parts("fig.axes[0].set_title") == ("chart", "set_title")
    assert other_name_parts("sns.lineplot(data=df, x='a')") == ("chart", "lineplot")
    assert other_name_parts("chart.hist") is None  # a simplydata object in front, as before
    assert other_name_space("ax.set_title") == "ax" and other_name_space("Series.str.replace") == "str"
    assert other_name_space("pd.merge") is None


def test_chart_pointers_the_audit_found_wrong_or_missing():
    chart = sdata.chart(sdata.get_example("marks"))
    with pytest.raises(MissingWordError, match=r"sdata\.put_in_rows_and_columns\("):
        chart.subplots  # plt.subplots(2, 2) also makes a page of different charts
    with pytest.raises(MissingWordError, match=r"In simplydata this is chart\.as_matplotlib\(\)"):
        chart.gcf
    with pytest.raises(MissingWordError, match=r'chart\.draw_lines\(x="month", y="temperature", colour="city"\)'):
        chart.lineplot


# Every chart call written in a pointer runs: on a chart of a practice table, at once or after one of the draws below
# (a word that changes what is drawn, such as label_colour_bar, needs something drawn first), and the chart is then
# drawn. An option value a word does not know, or an option it lacks, fails the test at once.
CHART_FIRST = {
    "marks": ['chart.draw_dots(x="hours", y="marks", colour="class")', 'chart.draw_bars(x="class", y="marks")',
              'chart.draw_histogram(x="marks")'],
    "weather": ['chart.draw_heatmap(x="month", y="city", value="rain")',
                'chart.draw_lines(x="month", y="temperature", colour="city")'],
    "island": ['chart.draw_surface(x="east", y="north", z="height")'],
    "sensor": ['chart.draw_lines(x="time", y="signal")'],
}
CHART_EXAMPLES = [*CHART_FIRST, *[e for e in EXAMPLES if e not in CHART_FIRST]]
# The sdata words that make a chart or a page, run like chart calls
CHART_SDATA = ("draw_all_pairs", "put_side_by_side", "put_one_above_other", "put_in_rows_and_columns")
# Calls the test does not run: they open a web browser or a window (they are checked by name and options above)
CHART_NOT_RUN = ("show_in_web_page", "chart.show(")
# Calls that need a step first, which the pointer leaves out to stay short (they are checked by name only)
CHART_NEEDS_PREP = {
    'draw_forest_plot(x="estimate", y="measure")': "a result table with an estimate for each measure",
    'draw_funnel_plot(x="estimate"': "the result table of table.combine_studies",
    'draw_band(x="month", between=["lowest", "highest"])': "a table with a lowest and a highest column",
    'draw_sticks(x="rows back", y="correlation")': "the result table of table.find_autocorrelation_of",
    '"visitors", sorted_by="month"': "one museum kept first (the visitors table has two)",
    'x="month", y="visitors"': "one museum kept first (the visitors table has two)",
    'draw_risk_curves(time="time", event="event"': "a hospital stay table with competing events",
    "break_between_y(50, 500)": "values both below 50 and above 500",
}


def _chart_runs_here(call: str) -> bool:
    if call.endswith("=)") or "..." in call or any(skip in call for skip in (*CHART_NOT_RUN, *CHART_NEEDS_PREP)):
        return False
    names = {node.id for node in ast.walk(ast.parse(call, mode="eval")) if isinstance(node, ast.Name)}
    return names <= KNOWN_NAMES | {"chart"}


def _runnable_chart_pointers():
    out = []
    for kind, name, written in _all_pointer_calls():
        calls = [c for o, w, c in _pointer_calls(written) if o == "chart" or o == "sdata" and w in CHART_SDATA]
        if " then " in written:  # one call after the other, on one chart
            if calls and all(_chart_runs_here(call) for call in calls):
                out.append(pytest.param(calls, id=f"{kind}.{name}"))
        else:  # "a, or b": each call on its own
            out += [pytest.param([call], id=f"{kind}.{name}-{i}") for i, call in enumerate(calls, 1)
                    if _chart_runs_here(call)]
    return out


def test_the_chart_pointer_calls_are_run():
    assert len(_runnable_chart_pointers()) > 150


@pytest.mark.parametrize("calls", _runnable_chart_pointers())
def test_every_chart_pointer_call_runs_on_a_practice_table(calls, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # chart.save("chart.png") and friends write here
    errors = []
    for source in CHART_EXAMPLES:
        for first in [None, *CHART_FIRST.get(source, [])]:
            table = sdata.get_example(source)
            scope = {"sdata": sdata, "table": table, "chart": sdata.chart(table)}
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    if first:
                        exec(first, scope)
                    for call in calls:
                        exec(f"_made = {call}", scope)  # the pointer's own text, run as written
                        if hasattr(scope["_made"], "_render"):  # a chart or a page (sdata.draw_all_pairs)
                            scope["_made"]._render()
                    scope["chart"]._render()
                return
            except Exception as problem:  # noqa: BLE001 - a table without these columns is tried next
                text = f"{type(problem).__name__}: {problem}"
                if "needs plotly" in text:  # the web page words: checked where plotly is installed
                    pytest.skip(f"{calls} needs plotly")
                if type(problem).__name__ == "RMissing":  # the word runs R, and R is not here: checked where R is
                    pytest.skip(f"{calls} needs R")
                assert not any(bad in text for bad in BAD), f"{calls} on {source} after {first}: {text}"
                errors.append(f"{source} after {first}: {text.splitlines()[0]}")
    pytest.fail(f"{calls} ran on no practice table:\n" + "\n".join(errors[:6]))



@pytest.mark.parametrize("typed, old, new", [
    ("plt.pie", "pie", "draw_pie"), ("ax.pie", "pie", "draw_pie"), ("plt.polar", "polar", "draw_polar"),
    ("plt.contour", "contour", "draw_contour"), ("ax.contour", "contour", "draw_contour"),
    ("sns.heatmap", "heatmap", "draw_heatmap"),
])
def test_a_matplotlib_name_that_is_an_old_chart_word_gives_the_word(typed, old, new, capsys):
    """plt.pie, sns.heatmap ... are the old names of chart words (pie, heatmap): help says what they are called now
    (it said "no word called")."""
    sdata.help(typed)
    out = capsys.readouterr().out
    assert f'"chart.{old}" is now called "chart.{new}"' in out, out
    assert "no word called" not in out


@pytest.mark.parametrize("typed, heading", [
    ("fig.keep_rows_where", "table.keep_rows_where()"), ("plot.keep_rows_where", "table.keep_rows_where()"),
    ("axes.find_average_of", "table.find_average_of()"),
])
def test_a_table_word_after_a_matplotlib_name_is_still_found(typed, heading, capsys):
    """A name with no chart word or pointer falls back to every word, as before the namespaces."""
    sdata.help(typed)
    out = capsys.readouterr().out
    assert out.startswith(heading), out[:200]


def test_axes3d_names_have_their_own_list():
    from simplydata._other_names import OTHER_NAMES, other_name_parts

    assert other_name_parts("Axes3D.scatter") == ("chart3d", "scatter")
    assert "draw_dots_3d" in OTHER_NAMES["chart3d"]["scatter"] and "draw_dots(" in OTHER_NAMES["chart"]["scatter"]


def test_triplot_is_left_to_matplotlib_not_a_contour_map():
    from simplydata._other_names import OTHER_NAMES

    assert "as_matplotlib" in OTHER_NAMES["chart"]["triplot"] and "draw_contour" not in OTHER_NAMES["chart"]["triplot"]


# ---------------------------------------------------------------- numbers finishing PR: NumPy, SciPy and SymPy names
# The API audit of NumPy, SciPy and SymPy (2026-11-27; np., np.linalg., np.random., rng., np.fft., scipy.stats.,
# optimize., integrate., interpolate., signal., ndimage., spatial., special., sp. and sympy. names): what sdata.help
# says now. A name typed with its namespace looks in that namespace's list first.
NUMBER_AUDIT_POINTERS = [
    ("np.mean", "numbers.find_average()"), ("numpy.median", "numbers.find_median()"),
    ("np.sum", "numbers.find_total()"), ("np.std", "numbers.find_standard_deviation()"),
    ("np.percentile", "numbers.find_percentile(90)"), ("np.cumsum", "numbers.turn_into_running_total()"),
    ("np.square", "numbers.raise_to_power(2)"), ("np.flip", "numbers.reverse()"),
    ("np.unique", "numbers.remove_duplicate_numbers()"), ("np.clip", "numbers.replace_each_number_that("),
    ("np.transpose", "grid.swap_rows_and_columns()"), ("np.isin", "numbers.turn_into_yes_or_no(is_one_of="),
    ("np.zeros", "sdata.number_grid(rows=2, columns=3, filled_with=0)"), ("np.diff", "numbers.turn_into_changes()"),
    ("np.save", 'numbers.save("numbers.csv")'), ("np.cbrt", "numbers.take_cube_root()"),
    ("np.linalg.solve", "grid.solve_for("), ("scipy.linalg.solve_triangular", "grid.solve_for("),
    ("np.linalg.lstsq", "grid.solve_for("), ("np.linalg.svd", 'grid.break_down(test_method="svd")'),
    ("scipy.linalg.lu", 'grid.break_down(test_method="lu")'), ("scipy.linalg.ldl", 'test_method="ldl"'),
    ("scipy.linalg.qz", 'test_method="qz", together_with='), ("np.linalg.det", "grid.find_determinant()"),
    ("np.linalg.eigh", "grid.find_eigenvalues()"), ("np.linalg.norm", "numbers.find_size()"),
    ("scipy.linalg.expm", "grid.take_matrix_exp()"), ("optimize.nnls", "between=[0, None]"),
    ("scipy.optimize.lsq_linear", "between=[0, 1]"), ("scipy.optimize.minimize", "sdata.find_where_smallest("),
    ("rng.normal", "sdata.make_random_numbers(how_many=100, average=50"),
    ("np.random.poisson", 'sdata.distribution("poisson", average=3)'), ("rng.integers", "whole_numbers=True"),
    ("np.random.pareto", "Lomax"), ("np.random.default_rng", "with_seed="),
    ("rng.choice", "numbers.make_random_picks("), ("np.fft.rfftfreq", "numbers.take_fourier_transform("),
    ("scipy.fft.dct", "numbers.take_cosine_transform()"), ("scipy.stats.gamma", 'sdata.distribution("gamma"'),
    ("scipy.stats.nbinom", 'sdata.distribution("negative binomial"'), ("stats.norm.pdf", "find_density_at"),
    ("scipy.stats.ttest_ind", "compare_averages_of"), ("scipy.special.gamma", 'sdata.formula("gamma(x)")'),
    ("scipy.special.comb", "sdata.count_ways_to_choose("), ("scipy.special.expit", "numbers.turn_into_chances()"),
    ("scipy.signal.find_peaks", "numbers.find_each_peak_that("), ("scipy.signal.welch", "numbers.find_spectrum("),
    ("scipy.integrate.simpson", 'test_method="simpson"'), ("scipy.integrate.quad", "sdata.find_area_under("),
    ("scipy.ndimage.label", "grid.find_each_patch_that("), ("scipy.ndimage.rotate", "grid.rotate(by_degrees=15)"),
    ("sp.solve", 'sdata.solve("x**2 = 2", exactly=True)'), ("sympy.sqrt", "inside the formula text"),
    ("sympy.integrate", "formula.find_area_formula()"), ("sp.diff", "formula.find_slope_formula()"),
    ("sympy.Matrix", "sdata.number_grid("), ("sympy.Matrix.det", "grid.find_determinant(exactly=True)"),
    ("sp.Matrix.LUsolve", "grid.solve_for([5, 10], exactly=True)"), ("sympy.dsolve", "exactly=True"),
    ("sp.srepr", 'formula.show_as_code("sympy tree")'),  # batch 26 gives srepr a word
    # a name in capitals keeps them when a list has it (scipy.interpolate.CubicSpline was not found, as cubicspline)
    ("scipy.interpolate.CubicSpline", "table.find_values_at("), ("scipy.spatial.KDTree", "find_nearest_rows_to"),
    ("scipy.signal.TransferFunction", "sdata.system("), ("scipy.stats.logrank", "compare_survival"),
    ("scipy.stats.kstest", "compare_shape_to"), ("scipy.signal.step", "step_response()"),
    ("scipy.signal.envelope", "numbers.find_envelope()"),
]


@pytest.mark.parametrize("typed, word", NUMBER_AUDIT_POINTERS)
def test_every_number_name_the_audit_found_points_to_its_word(typed, word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert word in out, out


@pytest.mark.parametrize("typed, word, not_word", [
    ("np.mean", "numbers.find_average()", "table.find_average_of"),  # a bare mean is the table word
    ("np.zeros", "sdata.number_grid(", "system.zeros"),  # a bare zeros is the system word
    ("np.save", "numbers.save(", "chart.save"),
    ("np.diff", "numbers.turn_into_changes()", "find_slope_formula"),  # a bare diff is SymPy's slope
    ("np.linalg.norm", "find_size()", 'distribution("normal"'),  # a bare norm is scipy.stats.norm
    ("scipy.special.gamma", 'formula("gamma(x)")', 'distribution("gamma"'),
    ("scipy.stats.gamma", 'distribution("gamma"', 'formula("gamma(x)")'),
    ("np.linalg.solve", "grid.solve_for(", 'sdata.solve("'),
    ("sp.solve", 'sdata.solve("x**2 = 2", exactly=True)', "grid.solve_for("),
    ("scipy.special.binom", "count_ways_to_choose", 'distribution("binomial"'),
    ("np.random.binomial", 'distribution("binomial"', "count_ways_to_choose"),
])
def test_names_inside_numpy_scipy_and_sympy_point_to_their_own_word(typed, word, not_word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert word in out and not_word not in out, out


@pytest.mark.parametrize("typed, heading", [
    ("np.sort", "numbers.sort()"), ("np.add", "numbers.add()"), ("numpy.subtract", "numbers.subtract()"),
])
def test_a_numpy_name_that_is_a_word_of_numbers_explains_the_word(typed, heading, capsys):
    sdata.help(typed)
    assert capsys.readouterr().out.startswith(heading)


def test_names_only_numpy_scipy_or_sympy_use_are_found_without_their_namespace(capsys):
    for typed, word in [("lstsq", "grid.solve_for("), ("svd", "break_down"), ("rfftfreq", "take_fourier_transform"),
                        ("nnls", "between=[0, None]")]:
        sdata.help(typed)
        out = capsys.readouterr().out
        assert word in out, out


def test_stats_in_front_still_finds_the_table_and_sdata_words(capsys):
    sdata.help("stats.lm")  # R's stats package, typed with a dot: the sdata pointer, as before
    assert "table.fit_line(" in capsys.readouterr().out


def test_other_name_parts_reads_numpy_scipy_and_sympy_names():
    from simplydata._other_names import other_name_parts

    assert other_name_parts("np.mean") == ("numpy", "mean")
    assert other_name_parts("np.linalg.solve") == ("linalg", "solve")
    assert other_name_parts("scipy.linalg.lu") == ("linalg", "lu")
    assert other_name_parts("np.random.normal") == ("random", "normal")
    assert other_name_parts("rng.integers(1, 7)") == ("random", "integers")
    assert other_name_parts("scipy.stats.norm.pdf") == ("stats", "pdf")
    assert other_name_parts("scipy.optimize.nnls") == ("scipy", "nnls")
    # second review of numbers-int-2: a SymPy Matrix method has its own list (falling back on SymPy's)
    assert other_name_parts("sp.Matrix([[1, 2]]).det") == ("matrix", "det")
    assert other_name_parts("sympy.stats.Normal") == ("sympystats", "Normal")
    assert other_name_parts("scipy.sparse.linalg.spsolve") == ("sparse", "spsolve")
    assert other_name_parts("np.strings.add") == ("npstrings", "add")


# Every call of numbers, a grid, a formula or a distribution written in a pointer runs (with the sdata words that make
# them and work with them), on the first of the grids below it works on. A constructor in the pointer
# (sdata.number_grid(...), sdata.formula(...)) makes the object the other calls of that pointer use. An option value a
# word does not know, or an option it lacks, fails the test at once.
NUMBER_OWNERS = ("numbers", "grid", "formula", "distribution")
NUMBER_SDATA = ("number_list", "number_grid", "formula", "distribution", "solve", "find_area_under",
                "find_volume_under", "find_path_over_time", "find_sum_of_series", "find_where_smallest",
                "find_where_biggest", "make_random_numbers", "count_ways_to_choose", "count_ways_to_order",
                "make_wave", "make_window_shape", "system", "frequency_filter")
MAKES = {"number_list": "numbers", "number_grid": "grid", "formula": "formula", "distribution": "distribution"}
NUMBER_KNOWN = {"sdata", "numbers", "grid", "formula", "distribution", "other", "yes_no", "True", "False", "None"}
# Calls that read a file of yours (they are checked by name and options above)
READS_A_FILE = ('sdata.number_list("', 'sdata.number_block("')
GRIDS = {"square": [[4, 2, 1], [2, 3, 0.5], [1, 0.5, 2]], "4 rows": [[2, 0, 1], [1, 1, 0], [0, 3, 1], [1, 0, 2]],
         "2 x 2": [[2, 1], [1, 3]], "4 x 2": [[1, 1], [1, 2], [1, 3], [1, 4]]}
SERIES = [3.0, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4]


def _number_runs_here(call: str) -> bool:
    if call.endswith("=)") or "..." in call or call.startswith(READS_A_FILE):
        return False
    names = {node.id for node in ast.walk(ast.parse(call, mode="eval")) if isinstance(node, ast.Name)}
    return names <= NUMBER_KNOWN


def _runnable_number_pointers():
    out = []
    for kind, name, written in _all_pointer_calls():
        calls = [(o, w, c) for o, w, c in _pointer_calls(written)
                 if o in NUMBER_OWNERS or o == "sdata" and w in NUMBER_SDATA]
        if calls and all(_number_runs_here(c) for _, _, c in calls):
            out.append(pytest.param(calls, id=f"{kind}.{name}"))
    return out


def test_the_number_pointer_calls_are_run():
    assert len(_runnable_number_pointers()) > 150


@pytest.mark.parametrize("calls", _runnable_number_pointers())
def test_every_number_pointer_call_runs(calls, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # numbers.save("numbers.csv") writes here
    owners = {o for o, _, _ in calls}
    makers = [(MAKES[w], c) for o, w, c in calls if o == "sdata" and w in MAKES and MAKES[w] in owners]
    errors = []
    for shape, values in GRIDS.items():
        numbers = sdata.number_list(SERIES)
        scope = {"sdata": sdata, "numbers": numbers, "other": sdata.number_list(SERIES[::-1]),
                 "grid": sdata.number_grid(values), "formula": sdata.formula("x**3 - 2*x"),
                 "distribution": sdata.distribution("normal", average=50, standard_deviation=10)}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                scope["yes_no"] = numbers.turn_into_yes_or_no(is_above=4)
                for made, call in makers:  # the object the pointer makes, first
                    scope[made] = eval(call, scope)
                for _, _, call in calls:
                    if call not in [c for _, c in makers]:
                        exec(f"_made = {call}", scope)  # the pointer's own text, run as written
            return
        except Exception as problem:  # noqa: BLE001 - a grid of another shape is tried next
            text = f"{type(problem).__name__}: {problem}"
            if type(problem).__name__ == "RMissing":  # the word runs R, and R is not here: checked where R is
                pytest.skip(f"{calls} needs R")
            if "needs SciPy" in text and "or newer" in text:  # checked where that SciPy is installed
                pytest.skip(f"{calls}: {text.splitlines()[0]}")
            assert not any(bad in text for bad in BAD), f"{[c for _, _, c in calls]} on the {shape} grid: {text}"
            errors.append(f"{shape}: {text.splitlines()[0]}")
    pytest.fail(f"{[c for _, _, c in calls]} ran on no grid:\n" + "\n".join(errors))


# review fixes (2026-11-28): R-style stats.<summary> keeps the table words; each comparison names its own option
@pytest.mark.parametrize("typed, word, not_word", [
    ("stats.median", "table.find_median_of(", "distribution("),
    ("stats.mean", "table.find_average_of(", "distribution("),
    ("stats.var", "table.find_summary_of(", "find_variance"),
    ("np.greater_equal", "is_at_least=20", "is_above"), ("np.less_equal", "is_at_most=20", "is_above"),
    ("np.equal", "is_equal_to=20", "is_above"), ("np.not_equal", "is_not_equal_to=20", "is_above"),
    ("np.logical_xor", "np.logical_xor(", "is_above"),
    ("sympy.factorint", "numbers.find_prime_factors()", "turn_into_product"),  # batch 26 gives it a word
    ("sp.nsolve", "between=[0, 3]", "exactly=True"),
    ("np.random.sample", "keep_random_numbers(5", "numbers.count()"),
])
def test_review_fixes_of_the_number_pointers(typed, word, not_word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert word in out and not_word not in out, out


# review of numbers-int-2 (2026-11-28): each name points to the word that does the same job
@pytest.mark.parametrize("typed, word, not_word", [
    ("np.concat", "add_numbers_from", "join_numbers_with"),  # concat keeps the order and the repeats
    ("np.e", "exp(1)", "(E in a formula)"),  # E is a letter in formula text
    ("pl.Expr.is_finite", "is_between=[-1e300, 1e300]", "is_below=1e300"),  # -inf is not finite
    ("pl.Expr.nan_max", "find_biggest_of", "count_empty_cells_in"),
    ("pl.Expr.nan_min", "find_smallest_of", "count_empty_cells_in"),
    ("pl.Expr.over", "for_each_group_in=", "keep_columns"),
    ("pl.DataFrame.clear", "as_polars()", "make_copy(), as in"),
    ("pl.Expr.bitwise_count_ones", 'work_on_bits("count ones")', '"and"'),
    ("pl.Expr.rolling_rank", "as_polars()", "add_rank_column(\"rank\", from_column"),
    ("pl.Expr.rolling_skew", 'show="skewness"', "left to pandas"),
    ("np.log2", "take_log(base=2)", "base=10"),
    ("np.rint", "with_decimals=0", "with_decimals=2"),
    ("pd.Series.size", "table.count_rows() is how many values", "for_each_group_in"),
    ("sympy.deg", "change_angles_to", "geometry"),
    ("np.c_", "add_numbers_from", "show_all_words"),
    ("np.datetime64", "make_run_of_dates", "show_all_words"),
    ("np.array2string", "numbers.show()", "show_all_words"),
    ("sympy.preorder_traversal", "show_as_tree", "show_all_words"),
])
def test_review_fixes_of_the_final_pointers(typed, word, not_word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert word in out and not_word not in out, out


def test_a_table_name_in_front_narrows_a_shared_word_to_the_table_word(capsys):
    sdata.help("pl.DataFrame.show")
    out = capsys.readouterr().out
    assert out.startswith("table.show()") and "can mean more than one word" not in out, out[:300]


# second review of numbers-int-2: the probed parts of NumPy, SciPy and SymPy (np.strings, np.ma, ndarray, Matrix,
# sympy.stats, cluster.hierarchy, sparse) have their own lists, so a pandas or Polars name never gets their meaning
_FOREIGN = ("Matrix", "np.ma", "np.strings", "ndarray", "sympy.stats", "hierarchy", "scipy.sparse", "sparse storage",
            "as_sympy", "polynomial", "NumPy's memory")


def _table_library_names():
    import pandas as pd
    import polars as pl

    names = set()
    for front, owner in (("pd", pd.DataFrame), ("pd", pd.Series), ("pl", pl.DataFrame), ("pl", pl.Series),
                         ("pl", pl.Expr)):
        names |= {f"{front}.{owner.__name__}.{n}" for n in dir(owner) if not n.startswith("_")}
    names |= {f"{front}.{n}" for front, module in (("pd", pd), ("pl", pl)) for n in dir(module)
              if not n.startswith("_")}
    return sorted(names)


def test_a_pandas_or_polars_name_never_gets_the_meaning_of_another_library():
    bad = []
    for typed in _table_library_names():
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sdata.help(typed)
        text = out.getvalue()
        hits = [mark for mark in _FOREIGN if mark in text]
        if hits:
            bad.append(f"{typed}: {hits}")
    assert not bad, bad[:20]


@pytest.mark.parametrize("typed, word, not_word", [
    ("np.strings.add", "by_joining_text", "numbers.add"),
    ("np.strings.multiply", "as_pandas()", "numbers.times"),
    ("np.strings.less", "as_pandas", "is_below"),
    ("np.less", "is_below=20", "is_above"),
    ("np.ndarray.choose", "choose works", "show_all_words"),
    ("sympy.Matrix.exp", "take_matrix_exp", "take_exp()"),
    ("sympy.Matrix.solve", "grid.solve_for(", 'sdata.solve("'),
    ("sympy.Matrix.ones", "filled_with=1", "show_all_words"),
    ("sympy.stats.median", "find_median()", "find_median_of"),
    ("sympy.stats.Weibull", 'distribution("weibull"', "show_all_words"),
    ("sympy.stats.Wald", "as_sympy()", 'distribution("wald"'),
    ("sympy.stats.covariance", "as_sympy()", "find_correlation_between"),
    ("scipy.cluster.hierarchy.complete", 'linkage="complete"', "show_all_words"),
    ("scipy.cluster.hierarchy.median", "as_numpy()", "find_median"),
    ("scipy.sparse.kron", "kron works", "show_all_words"),
    ("scipy.sparse.linalg.onenormest", 'kind="biggest column total"', "show_all_words"),
    ("df.ewm(span=3).mean", "adjust=False", "show_all_words"),
    ("df.ewm().adjust", "as_pandas()", "show_all_words"),
    ("df.resample().bfill", '"value below"', '"value above"'),
    ("np.ma.masked_where", "with_value=None", "with_value=100"),
    ("np.ma.make_mask", "as_numpy()", "show_all_words"),
    ("np.strings.ljust", "as_pandas()", "add_zeros_in_front_of"),
    ("np.strings.rfind", "as_pandas()", "position_of"),
    ("scipy.spatial.distance.sqeuclidean", "as_numpy()", "find_distances_between_rows"),
    ("sympy.Matrix.left_eigenvects", "as_sympy", "find_eigenvalues"),
    ("scipy.sparse.csgraph.connected_components", "as_numpy()", "find_each_patch_that"),
    ("scipy.constants.c", "as_numpy()", "show_all_words"),
])
def test_second_review_fixes_of_the_probed_parts(typed, word, not_word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert word in out and not_word not in out, out
