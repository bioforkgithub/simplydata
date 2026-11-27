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
from simplydata.chart import Chart
from simplydata.numbers.blocks import NumberBlock
from simplydata.numbers.numbers import NumberGrid, Numbers
from simplydata.table import Table

OBJECTS = {"table": Table, "chart": Chart, "numbers": Numbers, "block": NumberBlock}
PREFIX = {"table": "table", "chart": "chart", "numbers": "nums", "block": "block"}


def _target_exists(written: str) -> bool:
    word = other_name_target(written)
    for prefix, owner in (("sdata.", sdata), ("table.", Table), ("chart.", Chart), ("numbers.", Numbers),
                          ("block.", NumberBlock)):
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
    ("str.tail", "add_column_with_part_of_text"), ("str.title", "as_pandas"), ("str.to_date", "turn_into_dates"),
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
    ("str.title", "str.title", "as_pandas", "write_title_on_top"),
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
    ("unique", ['table.keep_columns("class"), then table.remove_duplicate_rows()',
                '"From pandas (and Polars) to simplydata"']),
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


# ---------------------------------------------------------------- every pointer's call is a call that works
# A pointer that names a word with a wrong option or value is worse than none. Two checks:
# 1. every call written in a pointer (sdata.x(...), table.x(...), chart.x(...), numbers.x(...), block.x(...)) names a
#    real word, and every option it gives is an option of that word;
# 2. every table call runs (the calls of "a, then b" one after the other on one table) on the first practice table
#    it works on, or on _pointer_table(), made for the columns the pointers name. An option value a word does not
#    know ("does not know ...") or an option it lacks fails the test on every table. A word that runs R is skipped
#    where R is missing; the calls in NEEDS_PREP need a step first that the pointer does not write.

OWNERS = {"sdata": sdata, "table": Table, "chart": Chart, "numbers": Numbers, "nums": Numbers, "grid": NumberGrid,
          "block": NumberBlock}
# Pointers whose calls name what no practice table has (your own function, another table you have, a list "..."):
# only the static check applies to them, on purpose.
# "bmi" and "chl" are columns of R's mice::nhanes, loaded with sdata.get_example("nhanes", from_r_package="mice").
NOT_RUN = {"make_label", "my_function", "national", "rain", "other_table, keep=", "...", '"bmi"'}
# Calls that need a step first, which the pointer leaves out to stay short (they are checked by name only):
NEEDS_PREP = {
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
}


def _pointer_calls(written: str):
    """The calls a pointer writes: [(object, word, call text)], in order."""
    found = []
    for m in re.finditer(r"(?<![\w.\"])(sdata|table|chart|numbers|grid|block)\.(\w+)\(", written):
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


@pytest.mark.parametrize("kind, name, written", _all_pointer_calls())
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
        "school": ["X", "X", "Y", "Y"], "week": [1, 1, 2, 2],
    })


EXAMPLES = sorted(p.stem for p in (Path(sdata.__file__).parent / "data").glob("*.csv"))
BAD = ("has no option called", "does not know", "SyntaxError", "TypeError", "is not a Python call")


def _runnable_pointers():
    out = []
    for kind, name, written in _all_pointer_calls():
        calls = [c for o, w, c in _pointer_calls(written) if o == "table"]
        if not calls:
            continue
        if any(prep in call for call in calls for prep in NEEDS_PREP):
            continue
        if any(skip in written for skip in NOT_RUN) or any(c.endswith("=)") for c in calls):
            continue
        if " then " in written or "count first" in written:  # one call after the other, on one table
            out.append(pytest.param(calls, id=f"{kind}.{name}"))
        else:  # "a, or b": each call on its own
            out += [pytest.param([call], id=f"{kind}.{name}-{i}") for i, call in enumerate(calls, 1)]
    return out


@pytest.mark.parametrize("calls", _runnable_pointers())
def test_every_table_pointer_call_runs_on_a_practice_table(calls):
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
            assert not any(bad in text for bad in BAD), f"{calls} on {source or 'POINTER_TABLE'}: {text}"
            errors.append(f"{source or 'POINTER_TABLE'}: {text.splitlines()[0]}")
    pytest.fail(f"{calls} ran on no practice table:\n" + "\n".join(errors[:5]))
