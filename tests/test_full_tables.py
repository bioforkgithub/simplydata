"""Families for 100 %, batches 1-2 (approved by Manish 2026-11-28): the pandas and Polars gaps (plan section 2.1) and
the seaborn.objects marks and moves (section 2.5). Each word and option is checked against pandas, Polars or seaborn
itself, on both table engines where it applies."""

from __future__ import annotations

import numpy as np
import pandas as pd
import polars as pl
import pytest

import simplydata as sdata

ENGINES = [False, True]  # pandas, then Polars (fast=True)


def _table(name, fast):
    return sdata.table(sdata.get_example(name), fast=fast)


def _frame(name):
    return sdata.get_example(name).as_pandas()


# ---------------------------------------------------------------- new table words
@pytest.mark.parametrize("fast", ENGINES)
def test_get_different_values_in_matches_pandas_unique_and_polars_unique(fast, capsys):
    df = pd.DataFrame({"site": ["b", "a", None, "b", "c", "a"], "n": [3.0, 1.0, np.nan, 3.0, 2.0, 1.0]})
    table = sdata.table(df, fast=fast)
    values = table.get_different_values_in("site")
    assert values == list(df["site"].dropna().unique())
    assert values == pl.from_pandas(df)["site"].drop_nulls().unique(maintain_order=True).to_list()
    out = capsys.readouterr().out
    assert 'Note: 1 empty cell in "site" was left out.' in out
    assert '"site" has 3 different values, in the order they first turn up: "b", "a", "c".' in out
    numbers = table.get_different_values_in("n")
    assert list(numbers.as_numpy()) == list(df["n"].dropna().unique())  # number_list, as get_column gives
    assert table.count_rows() == 6  # the table does not change


@pytest.mark.parametrize("fast", ENGINES)
def test_check_if_all_and_any_match_pandas_and_polars(fast, capsys):
    df = pd.DataFrame({"depth": [3.0, 5.0, np.nan, 8.0], "dose": [10, 120, 40, 90], "ok": pd.array([True, True, None, True], dtype="boolean"),
                       "site": ["N", "N", "S", "S"]})
    table = sdata.table(df, fast=fast)
    assert table.check_if_all_values_in("depth", is_above=0) is bool((df["depth"].dropna() > 0).all()) is True
    assert table.check_if_all_values_in("depth", is_above=4) is False
    out = capsys.readouterr().out
    assert "Note: 1 empty cell" in out and 'No: 1 of the 3 values in "depth" do not meet "is above 4" (the first in ' \
                                          "row 1)." in out
    assert table.check_if_any_value_in("dose", is_above=100) is bool((df["dose"] > 100).any()) is True
    assert table.check_if_any_value_in("dose", is_above=200) is False
    assert table.check_if_all_values_in("ok") is True  # a True/False column needs no condition; empty left out
    polars = pl.from_pandas(df)
    assert table.check_if_all_values_in(["depth", "dose"], is_above=2) == bool(
        polars.select(pl.all_horizontal(pl.col("depth", "dose").fill_null(99) > 2).all()).item())
    assert table.check_if_any_value_in(["depth", "dose"], is_above=100) == bool(
        polars.select(pl.any_horizontal(pl.col("depth", "dose") > 100).any()).item())
    grouped = table.check_if_all_values_in("dose", is_below=100, for_each_group_in="site")
    expected = df.groupby("site")["dose"].apply(lambda s: bool((s < 100).all()))
    assert grouped.get_column("every value") == list(expected.values)
    assert table.check_if_any_value_in("dose", is_above=100, for_each_group_in="site").get_column("any value") == \
        list(df.groupby("site")["dose"].apply(lambda s: bool((s > 100).any())).values)


def test_check_if_all_values_in_needs_a_condition_unless_true_false():
    table = sdata.table(sdata.get_example("marks"))
    with pytest.raises(sdata.SimplydataError, match="needs a condition"):
        table.check_if_all_values_in("marks")
    with pytest.raises(sdata.SimplydataError, match="one condition at a time"):
        table.check_if_all_values_in("marks", is_above=0, is_below=100)


@pytest.mark.parametrize("fast", ENGINES)
def test_check_if_sorted_by_matches_is_monotonic_and_is_sorted(fast, capsys):
    df = pd.DataFrame({"day": [1, 2, 2, np.nan, 5], "level": [3.0, 2.0, 2.5, 1.0, 0.5], "site": ["a", "b", "b", "c", "c"]})
    table = sdata.table(df, fast=fast)
    assert table.check_if_sorted_by("day") is bool(df["day"].dropna().is_monotonic_increasing) is True
    assert table.check_if_sorted_by("level") is pl.from_pandas(df)["level"].is_sorted() is False
    out = capsys.readouterr().out
    assert 'No: the rows are not in order of "level", smallest first: row 2 (2) comes after 3.' in out
    assert table.check_if_sorted_by("level", biggest_first=True) is bool(df["level"].is_monotonic_decreasing)
    assert table.check_if_sorted_by("site") is True


@pytest.mark.parametrize("fast", ENGINES)
def test_add_run_number_column_matches_polars_rle_id(fast):
    df = pd.DataFrame({"t": [5, 1, 2, 3, 4, 6], "g": ["x", "x", "x", "y", "y", "y"],
                       "wet": ["no", "no", "yes", None, None, "yes"]})
    table = sdata.table(df, fast=fast).add_run_number_column("run", from_column="wet")
    expected = (pl.from_pandas(df).select(pl.col("wet").rle_id() + 1)["wet"]).to_list()
    assert table.get_column("run").as_numpy().tolist() == expected == [1, 1, 2, 3, 3, 4]
    ordered = sdata.table(df, fast=fast).add_run_number_column("run", from_column="wet", for_each_group_in="g",
                                                               sorted_by="t")
    want = pl.from_pandas(df).select((pl.col("wet").rle_id() + 1).over("g", order_by="t"))["wet"].to_list()
    assert ordered.get_column("run").as_numpy().tolist() == want


@pytest.mark.parametrize("fast", ENGINES)
def test_turn_into_title_case_matches_pandas_title_and_polars_to_titlecase(fast, capsys):
    df = pd.DataFrame({"name": ["o'neil mcDONALD", "asha ali", None, "hello-world 2nd"]})
    table = sdata.table(df, fast=fast).turn_into_title_case("name")
    assert table.get_column("name") == [None if pd.isna(v) else v for v in df["name"].str.title()]
    assert table.get_column("name") == pl.from_pandas(df)["name"].str.to_titlecase().to_list()
    assert "Each word in \"name\" now starts with a capital letter: \"o'neil mcDONALD\" became \"O'Neil Mcdonald\"." \
        in capsys.readouterr().out
    table.undo()
    assert table.get_column("name")[0] == "o'neil mcDONALD"


# ---------------------------------------------------------------- new options and values of existing words
@pytest.mark.parametrize("fast", ENGINES)
def test_find_summary_of_product_entropy_joined_text_and_a_dict(fast):
    from scipy import stats

    df = _frame("weather")
    table = sdata.table(df, fast=fast)
    found = table.find_summary_of("rain", show=["product", "entropy"], for_each_group_in="city")
    want = df.astype({"rain": float}).groupby("city")["rain"]  # decimals: an int64 product overflows
    assert found.get_column("product").as_numpy() == pytest.approx(want.prod().to_numpy(), rel=1e-12)
    assert found.get_column("entropy").as_numpy() == pytest.approx(
        pl.from_pandas(df).group_by("city").agg(pl.col("rain").entropy()).sort("city")["rain"].to_numpy(), rel=1e-12)
    assert found.get_column("entropy").as_numpy() == pytest.approx(want.apply(stats.entropy).to_numpy(), rel=1e-12)
    joined = table.find_summary_of("city", show=["joined text"], separator="|", for_each_group_in="month_number")
    assert joined.get_column("joined text")[0] == "|".join(df[df["month_number"] == 1]["city"])
    wide = table.find_summary_of(show={"rain": ["total"], "temperature": ["average", "count"]},
                                 for_each_group_in="city")
    named = df.groupby("city").agg(**{"rain total": ("rain", "sum"), "temperature average": ("temperature", "mean"),
                                      "temperature count": ("temperature", "count")}).reset_index()
    assert wide.get_column_names() == list(named.columns)
    for name in named.columns[1:]:
        assert wide.get_column(name).as_numpy() == pytest.approx(named[name].to_numpy(dtype=float), rel=1e-12)
    with pytest.raises(sdata.SimplydataError, match="separator= goes with"):
        table.find_summary_of("rain", show=["total"], separator=";")


@pytest.mark.parametrize("fast", ENGINES)
def test_rows_ahead_is_shift_minus_one(fast):
    df = _frame("weather")
    table = sdata.table(df, fast=fast).add_previous_value_column("next", from_column="temperature", rows_ahead=1,
                                                                 for_each_group_in="city", sorted_by="month_number")
    ordered = df.sort_values("month_number", kind="stable")
    want = ordered.groupby("city")["temperature"].shift(-1).reindex(df.index)
    np.testing.assert_allclose(table.get_column("next").as_numpy(), want.to_numpy(dtype=float))
    with pytest.raises(sdata.SimplydataError, match="not both"):
        sdata.table(df).add_previous_value_column("x", from_column="rain", rows_back=2, rows_ahead=1)


@pytest.mark.parametrize("fast", ENGINES)
def test_significant_figures_round_halves_to_even_as_r_signif(fast):
    table = sdata.table({"x": [123.456, 0.0012345, None, 3.15, 5.25, -98765.0]}, fast=fast)
    table.round_numbers_in("x", significant_figures=2)
    # R: signif(c(123.456, 0.0012345, NA, 3.15, 5.25, -98765), 2)
    np.testing.assert_allclose(table.get_column("x").as_numpy(), [120, 0.0012, np.nan, 3.2, 5.2, -99000])


@pytest.mark.parametrize("fast", ENGINES)
def test_time_of_day_between_is_between_time(fast):
    df = _frame("fjord_samples")
    df["sampled_local"] = pd.to_datetime(df["sampled_local"])
    table = sdata.table(df, fast=fast).keep_rows_where("sampled_local", time_of_day_between=["09:00", "12:00"])
    assert table.count_rows() == len(df.set_index("sampled_local").between_time("09:00", "12:00"))
    night = sdata.table(df, fast=fast).keep_rows_where("sampled_local", time_of_day_between=["12:00", "09:00"])
    assert night.count_rows() == len(df.set_index("sampled_local").between_time("12:00", "09:00"))


@pytest.mark.parametrize("fast", ENGINES)
def test_contains_in_written_conditions_is_str_contains(fast):
    df = pd.DataFrame({"gene": ["blaTEM", "sul1", None, "blaCTX-M"], "n": [1, 2, 3, 4]})
    table = sdata.table(df, fast=fast)
    table.add_group_column("group", rules={"gene contains 'bla'": "beta-lactamase"}, otherwise="other")
    hits = df["gene"].str.contains("bla", regex=False).fillna(False).astype(bool)
    assert table.get_column("group") == ["beta-lactamase" if h else "other" for h in hits]
    assert table.keep_rows_where("gene contains 'bla' and n > 1").count_rows() == 1


@pytest.mark.parametrize("fast", ENGINES)
def test_show_problems_names_the_cells_and_changes_nothing(fast, capsys):
    table = sdata.table({"dose": ["1.5", "<0.5", "n.d.", None, "2,5"]}, fast=fast)
    table.turn_into_numbers("dose", show_problems=True)
    out = capsys.readouterr().out
    assert 'row 2 "<0.5", row 3 "n.d."' in out and "The table is unchanged" in out
    assert table.get_column("dose")[1] == "<0.5"


@pytest.mark.parametrize("fast", ENGINES)
def test_new_date_parts_match_pandas_and_polars(fast):
    df = _frame("shop")
    df["date"] = pd.to_datetime(df["date"])
    table = sdata.table(df, fast=fast)
    d = df["date"].dt
    for part, want in [("is month start", d.is_month_start), ("is quarter start", d.is_quarter_start),
                       ("is quarter end", d.is_quarter_end), ("is year start", d.is_year_start),
                       ("is year end", d.is_year_end),
                       ("is working day", pd.Series(np.is_busday(df["date"].values.astype("datetime64[D]")))),
                       ("unix time", (df["date"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1))]:
        table.add_column_with_part_of_date("x", from_column="date", part=part)
        got = table.get_column("x")
        got = got.as_numpy().tolist() if part == "unix time" else got
        assert list(got) == list(want), part
    table.add_column_with_part_of_date("x", from_column="date", part="month end")
    want = pl.from_pandas(df)["date"].dt.month_end().to_list()
    assert [pd.Timestamp(v) for v in table.get_column("x")] == [pd.Timestamp(v) for v in want]


@pytest.mark.parametrize("fast", ENGINES)
def test_formula_names_and_working_days(fast):
    df = _frame("shop")
    df["date"] = pd.to_datetime(df["date"])
    table = sdata.table(df, fast=fast)
    for name in ("log10", "log1p", "sign", "cbrt", "floor", "ceil"):
        table.add_column("x", f"{name}(sales / 7)")
        want = getattr(np, name)(df["sales"] / 7)
        np.testing.assert_allclose(table.get_column("x").as_numpy(), want.to_numpy(dtype=float), err_msg=name)
    table.add_column("due", "add_working_days(date, 10)")
    days = df["date"].values.astype("datetime64[D]")
    due = np.busday_offset(days, 10, roll="forward")
    assert [pd.Timestamp(v) for v in table.get_column("due")] == [pd.Timestamp(v) for v in due]
    table.add_column("n", "count_working_days(date, due)")
    assert table.get_column("n").as_numpy().tolist() == np.busday_count(days, due).tolist()


def test_make_run_of_dates_every_working_day_is_bdate_range():
    table = sdata.make_run_of_dates("2026-11-28", to="2026-12-31", every="working day")
    assert [pd.Timestamp(v) for v in table.get_column("date")] == list(pd.bdate_range("2026-11-28", "2026-12-31"))


@pytest.mark.parametrize("fast", ENGINES)
def test_from_unix_seconds_is_from_epoch(fast):
    seconds = [1764288000, 1764291600.5, None, 0]
    table = sdata.table({"t": seconds}, fast=fast).turn_into_dates("t", from_unix_seconds=True)
    want = pd.to_datetime(pd.Series(seconds, dtype=float), unit="s")
    assert [None if v is None else pd.Timestamp(v) for v in table.get_column("t")] == \
        [None if pd.isna(v) else v for v in want]


@pytest.mark.parametrize("fast", ENGINES)
def test_every_match_and_position_of(fast):
    df = pd.DataFrame({"note": ["blaTEM1 and blaCTX", "sul1", None, "blaOXA48"], "name": ["Dana", "Ben", "Ann", None]})
    table = sdata.table(df, fast=fast)
    table.add_column_with_part_of_text("genes", from_column="note", matches_pattern=r"bla[A-Z]+\d*", every_match=True)
    want = [";".join(v) if isinstance(v, list) and v else None for v in df["note"].str.findall(r"bla[A-Z]+\d*")]
    assert table.get_column("genes") == want
    table.add_column_with_part_of_text("at", from_column="name", position_of="an")
    found = df["name"].str.find("an")
    np.testing.assert_allclose(table.get_column("at").as_numpy(),
                               (found + 1).where((found >= 0) & df["name"].notna()).to_numpy(dtype=float))


@pytest.mark.parametrize("fast", ENGINES)
def test_rolling_with_column_and_join_where(fast):
    df = _frame("weather")
    table = sdata.table(df, fast=fast)
    table.add_rolling_column("a", from_column="temperature", with_column="rain", show="correlation", window=4)
    table.add_rolling_column("b", from_column=["temperature", "rain"], show="correlation", window=4)
    np.testing.assert_allclose(table.get_column("a").as_numpy(), table.get_column("b").as_numpy())
    np.testing.assert_allclose(table.get_column("a").as_numpy(),
                               df["temperature"].rolling(4).corr(df["rain"]).to_numpy())
    readings = sdata.table({"time": [1, 5, 9, 12]}, fast=fast)
    periods = pd.DataFrame({"start": [0, 8], "end": [6, 10], "period": ["a", "b"]})
    readings.join_with(periods, where="time >= start and time < end")
    want = pl.DataFrame({"time": [1, 5, 9, 12]}).join_where(pl.from_pandas(periods), pl.col("time") >= pl.col("start"),
                                                            pl.col("time") < pl.col("end")).sort("time")
    assert readings.get_column("period") == want["period"].to_list()


def test_paper_files_clipboard_html_fixed_widths_and_nested_json(tmp_path, monkeypatch):
    import json

    monkeypatch.chdir(tmp_path)
    table = sdata.table({"site": ["N1", "S2"], "depth": [30.5, None], "n": [1, 2]})
    table.save("t.md")
    assert (tmp_path / "t.md").read_text().splitlines()[2] == "| N1   | 30.5  | 1 |"
    table.save("t.tex")
    tex = (tmp_path / "t.tex").read_text()
    assert "N1 & 30.5 & 1" in tex and "begin{tabular}{lrr}" in tex
    table.save("t.docx")
    assert sdata.table("t.docx").get_column("site") == ["N1", "S2"]
    table.save("t.html")
    assert sdata.table("t.html").get_column("site") == list(pd.read_html(str(tmp_path / "t.html"))[0]["site"])
    (tmp_path / "w.txt").write_text("site  depth n\nN1    30.5  1\nS2    12.0  2\n")
    assert sdata.table("w.txt", fixed_widths=[6, 6, 1]).get_column("depth").as_numpy().tolist() == [30.5, 12.0]
    rows = [{"id": 1, "site": {"name": "N1", "depth": 30}}, {"id": 2, "site": {"name": "S2", "depth": 12}}]
    (tmp_path / "n.json").write_text(json.dumps(rows))
    assert sdata.table("n.json").get_column_names() == list(pd.json_normalize(rows).columns)
    copied = {}
    monkeypatch.setattr(pd.DataFrame, "to_clipboard", lambda self, **kw: copied.setdefault("df", self))
    monkeypatch.setattr(pd, "read_clipboard", lambda **kw: copied["df"])
    table.save("clipboard")
    assert sdata.table("clipboard").get_column("site") == ["N1", "S2"]


# ---------------------------------------------------------------- seaborn.objects: Path, Shift, Dash
def test_in_row_order_move_layer_by_and_draw_dashes_match_seaborn():
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.DataFrame({"lon": [5, 6, 5.5, 4], "lat": [60, 61, 62, 60.5]})
    chart = sdata.chart(sdata.table(df))
    chart.draw_lines(x="lon", y="lat", in_row_order=True)
    fig, ax = plt.subplots()
    sns.lineplot(df, x="lon", y="lat", sort=False, estimator=None, ax=ax)
    assert chart.as_matplotlib().axes[0].lines[0].get_xydata().tolist() == ax.lines[0].get_xydata().tolist()
    plt.close(fig)
    marks = sdata.get_example("marks")
    chart = sdata.chart(marks)
    chart.draw_dots(x="hours", y="marks", move_layer_by=0.5)
    offsets = chart.as_matplotlib().axes[0].collections[0].get_offsets()
    np.testing.assert_allclose(offsets[:, 0], marks.as_pandas()["hours"].to_numpy() + 0.5)
    chart = sdata.chart(marks)
    chart.draw_dashes(x="class", y="marks")
    segments = chart.as_matplotlib().axes[0].collections[0].get_segments()
    fig, ax = plt.subplots()
    sns.stripplot(marks.as_pandas(), x="class", y="marks", jitter=False, ax=ax)
    places = np.concatenate([c.get_offsets() for c in ax.collections])
    plt.close(fig)
    middles = np.array([[(s[0][0] + s[1][0]) / 2, s[0][1]] for s in segments])
    np.testing.assert_allclose(middles, places)
    assert all(abs(s[1][0] - s[0][0] - 0.8) < 1e-12 for s in segments)
    with pytest.raises(sdata.SimplydataError, match="in_row_order=True"):
        sdata.chart(marks).draw_lines(x="hours", y="marks", in_row_order=True, error="standard error")


# ---------------------------------------------------------------- the pointers of plan sections 2.1 and 2.5
# every pandas, Polars, NumPy and seaborn.objects name the batches close, and the word sdata.help sends it to
FULL_POINTERS = [
    ("unique", "get_different_values_in"), ("pd.unique", "get_different_values_in"),
    ("Series.unique", "get_different_values_in"), ("all", "check_if_all_values_in"),
    ("pl.all_horizontal", "check_if_all_values_in"), ("any", "check_if_any_value_in"),
    ("pl.any_horizontal", "check_if_any_value_in"), ("groupby.all", "check_if_all_values_in"),
    ("groupby.any", "check_if_any_value_in"), ("is_monotonic_increasing", "check_if_sorted_by"),
    ("is_monotonic_decreasing", "check_if_sorted_by"), ("pl.DataFrame.is_sorted", "check_if_sorted_by"),
    ("rle_id", "add_run_number_column"), ("rle", "add_run_number_column"), ("str.title", "turn_into_title_case"),
    ("str.capitalize", "turn_into_title_case"), ("str.to_titlecase", "turn_into_title_case"),
    ("agg", "find_summary_of"), ("groupby.aggregate", "find_summary_of"), ("prod", "find_summary_of"),
    ("product", "find_summary_of"), ("groupby.prod", "find_summary_of"), ("entropy", "find_summary_of"),
    ("implode", "find_summary_of"), ("pl.implode", "find_summary_of"), ("list.join", "split_into_rows"),
    ("shift", "add_previous_value_column"), ("to_markdown", "save"), ("to_latex", "save"),
    ("to_clipboard", "save"), ("write_clipboard", "save"), ("str.contains", "keep_rows_where"),
    ("str.isnumeric", "turn_into_numbers"), ("str.isalpha", "turn_into_numbers"),
    ("dt.is_month_start", "add_column_with_part_of_date"), ("dt.is_quarter_end", "add_column_with_part_of_date"),
    ("dt.is_quarter_start", "add_column_with_part_of_date"), ("dt.is_year_end", "add_column_with_part_of_date"),
    ("dt.is_year_start", "add_column_with_part_of_date"), ("dt.month_end", "add_column_with_part_of_date"),
    ("dt.is_business_day", "add_column_with_part_of_date"), ("dt.add_business_days", "add_column"),
    ("dt.epoch", "add_column_with_part_of_date"), ("dt.timestamp", "add_column_with_part_of_date"),
    ("dt.combine", "turn_into_text"), ("dt.to_period", "find_average_of"), ("to_period", "find_average_of"),
    ("period_range", "find_average_of"), ("log10", "add_column"), ("log1p", "add_column"), ("cbrt", "add_column"),
    ("sign", "add_column"), ("pl.Expr.ceil", "add_column"), ("pl.Expr.floor", "add_column"),
    ("round_sig_figs", "round_numbers_in"), ("between_time", "keep_rows_where"), ("at_time", "keep_rows_where"),
    ("str.extractall", "add_column_with_part_of_text"), ("str.findall", "add_column_with_part_of_text"),
    ("str.extract_all", "add_column_with_part_of_text"), ("str.extract_many", "add_column_with_part_of_text"),
    ("str.find_many", "add_column_with_part_of_text"), ("str.find", "add_column_with_part_of_text"),
    ("str.index", "add_column_with_part_of_text"), ("str.rfind", "add_column_with_part_of_text"),
    ("str.rindex", "add_column_with_part_of_text"), ("bdate_range", "make_run_of_dates"),
    ("pl.business_day_count", "add_column"), ("np.busday_count", "add_column"), ("np.busday_offset", "add_column"),
    ("np.is_busday", "add_column_with_part_of_date"), ("np.busdaycalendar", "make_run_of_dates"),
    ("from_epoch", "turn_into_dates"), ("corrwith", "find_correlation_between"),
    ("rolling_corr", "add_rolling_column"), ("rolling_cov", "add_rolling_column"), ("join_where", "join_with"),
    ("merge_ordered", "join_with"), ("merge_sorted", "add_rows_from"), ("asof", "join_with"),
    ("read_html", "table"), ("read_fwf", "table"), ("pd.read_clipboard", "table"), ("json_normalize", "table"),
    ("combine", "add_column"), ("Series.cat", "turn_into_categories"), ("factorize", "add_rank_column"),
    ("convert_dtypes", "describe_columns"), ("infer_objects", "describe_columns"), ("memory_usage", "count_rows"),
    ("estimated_size", "count_rows"), ("shrink_to_fit", "count_rows"), ("shrink_dtype", "count_rows"),
    ("to_numpy", "get_column"), ("to_xarray", "get_column"), ("to_jax", "get_column"),
    ("to_torch", "get_column"), ("dot", "as_pandas"),
    # G12 (approved): left to pandas and Polars, with the hand-over
    ("set_index", "as_pandas"), ("reset_index", "as_pandas"), ("sort_index", "as_pandas"), ("xs", "as_pandas"),
    ("swaplevel", "as_pandas"), ("droplevel", "as_pandas"), ("reindex_like", "as_pandas"),
    ("rename_axis", "as_pandas"), ("reorder_levels", "as_pandas"), ("first_valid_index", "as_pandas"),
    ("last_valid_index", "as_pandas"), ("align", "as_pandas"), ("DataFrame.index", "as_pandas"),
    ("pipe", "as_pandas"), ("pl.Expr.pipe_with_dtype", "as_pandas"), ("pl.map_groups", "as_pandas"),
    ("lazy", "as_polars"), ("scan_csv", "table"), ("scan_parquet", "table"), ("collect_all", "table"),
    ("defer", "table"), ("pl.align_frames", "as_polars"), ("pl.list", "split_into_rows"),
    ("Series.arr", "split_into_rows"), ('pl.col("genes").list.sum', "split_into_rows"),
    ("list.eval", "split_into_rows"), ("arr.max", "split_into_rows"),
    # seaborn.objects
    ("so.Path", "draw_lines"), ("so.Paths", "draw_lines"), ("so.Shift", "draw_dots"), ("so.Dash", "draw_dashes"),
]


@pytest.mark.parametrize("typed, word", FULL_POINTERS)
def test_every_name_the_batches_close_points_to_its_word(typed, word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert "it is a name from other tools" in out, (typed, out)
    assert f'sdata.help("{word}")' in out.splitlines()[-1], (typed, out)


def test_a_table_style_points_to_the_html_file_and_the_hand_over():
    """sdata.help("style") explains the old chart word (now use_style); on a table, style is pandas' Styler."""
    from simplydata._errors import MissingWordError

    with pytest.raises(MissingWordError) as info:
        sdata.table(sdata.get_example("marks")).style  # noqa: B018 - the pointer is the point
    assert 'table.save("table_1.html")' in str(info.value) and "df.style" in str(info.value)
