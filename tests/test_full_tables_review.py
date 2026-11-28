"""Families for 100 %, batches 1-2: the fixes of the independent review (2026-11-28). Each test failed before its fix.
No test writes to the computer's real clipboard: pandas' clipboard functions are replaced by a stand-in."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import polars as pl
import pytest

import simplydata as sdata

ENGINES = [False, True]


@pytest.mark.parametrize("fast", ENGINES)
def test_a_dict_of_measures_keeps_the_group_with_an_empty_key(fast):
    table = sdata.table({"g": ["b", None, "b"], "v": [1, 2, 3], "w": [1, 2, 3]}, fast=fast)
    found = table.find_summary_of(show={"v": ["average"], "w": ["total"]}, for_each_group_in="g")
    want = pd.DataFrame({"g": ["b", None, "b"], "w": [1, 2, 3]}).groupby("g", dropna=False)["w"].sum()
    assert found.get_column("w total").as_numpy().tolist() == [want["b"], want[np.nan]] == [4, 2]


@pytest.mark.parametrize("fast", ENGINES)
def test_a_web_page_in_windows_1252_keeps_its_letters(tmp_path, fast):
    page = tmp_path / "page.html"
    page.write_bytes('<html><head><meta charset="windows-1252"></head><body><table><tr><th>place</th></tr>'
                     "<tr><td>Tromsø</td></tr></table></body></html>".encode("cp1252"))
    assert sdata.table(str(page), fast=fast).get_column("place") == ["Tromsø"]
    plain = tmp_path / "plain.html"
    plain.write_bytes("<table><tr><th>place</th></tr><tr><td>Tromsø</td></tr></table>".encode("cp1252"))
    assert sdata.table(str(plain), encoding="cp1252").get_column("place") == ["Tromsø"]


def test_fixed_widths_uses_the_other_reading_options(tmp_path):
    (tmp_path / "w.txt").write_text("# note\nsite  depth n\nN01   30,5  1\nS02   12,0  2\n")
    table = sdata.table(str(tmp_path / "w.txt"), fixed_widths=[6, 6, 1], decimal_mark=",", read_as_text=["site"],
                        skip_lines_starting_with="#")
    want = pd.read_fwf(tmp_path / "w.txt", widths=[6, 6, 1], decimal=",", comment="#", dtype={"site": str})
    assert table.get_column("depth").as_numpy().tolist() == want["depth"].tolist() == [30.5, 12.0]
    assert table.get_column("site") == ["N01", "S02"]
    (tmp_path / "v.txt").write_text("N01   30.5  1\nS02   12.0  2\n")
    named = sdata.table(str(tmp_path / "v.txt"), fixed_widths=[6, 6, 1], column_names=["a", "b", "c"])
    assert named.get_column_names() == ["a", "b", "c"] and named.count_rows() == 2
    with pytest.raises(sdata.SimplydataError, match="give one of them"):
        sdata.table(str(tmp_path / "v.txt"), fixed_widths=[6, 6, 1], separator=";")


@pytest.mark.parametrize("typed", ["sum", "mean", "unique", "first", "df.sum", "pd.concat"])
def test_list_pointers_stay_with_list_and_arr(typed, capsys):
    sdata.help(typed)
    assert "list." not in capsys.readouterr().out
    sdata.help(f"list.{typed.split('.')[-1]}")
    assert "split_into_rows" in capsys.readouterr().out


def test_first_and_last_point_to_the_table_words(capsys):
    for name in ("first", "last"):
        sdata.help(name)
        assert 'sdata.help("find_summary_of")' in capsys.readouterr().out


def test_move_layer_by_moves_the_error_band_too():
    chart = sdata.chart(sdata.get_example("weather"))
    chart.draw_lines(x="month_number", y="temperature", error="standard error")
    still = chart.as_matplotlib().axes[0]
    moved_chart = sdata.chart(sdata.get_example("weather"))
    moved_chart.draw_lines(x="month_number", y="temperature", error="standard error", move_layer_by=0.5)
    moved = moved_chart.as_matplotlib().axes[0]
    before = np.concatenate([p.vertices[:, 0] for p in still.collections[0].get_paths()])
    after = np.concatenate([p.vertices[:, 0] for p in moved.collections[0].get_paths()])
    np.testing.assert_allclose(after, before + 0.5)
    np.testing.assert_allclose(moved.lines[0].get_xdata(), still.lines[0].get_xdata() + 0.5)


def test_draw_dashes_keeps_a_number_axis_as_seaborn_so_dash():
    import matplotlib.pyplot as plt
    import seaborn.objects as so

    weather = sdata.get_example("weather")
    chart = sdata.chart(weather)
    chart.draw_dashes(x="month_number", y="temperature")
    ours = np.asarray(chart.as_matplotlib().axes[0].collections[0].get_segments())
    fig = plt.figure()
    so.Plot(weather.as_pandas(), x="month_number", y="temperature").add(so.Dash()).on(fig).plot()
    theirs = np.asarray(fig.axes[0].collections[0].get_segments())
    plt.close(fig)
    key = np.lexsort
    ours = ours[key((ours[:, 0, 1], ours[:, 0, 0]))]
    theirs = theirs[key((theirs[:, 0, 1], theirs[:, 0, 0]))]
    np.testing.assert_allclose(ours, theirs)


@pytest.mark.parametrize("fast", ENGINES)
def test_time_of_day_between_counts_parts_of_a_second(fast):
    times = [dt.datetime(2026, 1, 1, 17, 0, 0, 500000), dt.datetime(2026, 1, 1, 17, 0), dt.datetime(2026, 1, 1, 8)]
    table = sdata.table({"t": times}, fast=fast).keep_rows_where("t", time_of_day_between=["08:00", "17:00"])
    assert table.count_rows() == len(pd.DataFrame({"t": times}).set_index("t").between_time("08:00", "17:00")) == 2


@pytest.mark.parametrize("fast", ENGINES)
def test_check_if_sorted_by_follows_the_order_of_the_categories(fast):
    table = sdata.table({"s": ["mild", "moderate", "moderate", "severe"]}, fast=fast)
    table.turn_into_categories("s", in_order=["mild", "moderate", "severe"])
    assert table.check_if_sorted_by("s") is True
    table = sdata.table({"s": ["severe", "mild"]}, fast=fast)
    table.turn_into_categories("s", in_order=["severe", "mild"])
    assert table.check_if_sorted_by("s") is True  # severe comes first in this order, though "m" < "s"
    plain = sdata.table({"s": ["b", "a"]}, fast=fast)
    plain.turn_into_categories("s")  # no order given: the groups in the order they turn up, on both engines
    assert plain.check_if_sorted_by("s") is True
    ordered = pd.DataFrame({"s": pd.Categorical(["low", "high", "high"], categories=["low", "high"], ordered=True)})
    assert sdata.table(ordered, fast=fast).check_if_sorted_by("s") is bool(ordered["s"].is_monotonic_increasing)


@pytest.mark.parametrize("fast", ENGINES)
def test_title_case_is_one_rule_on_both_engines(fast):
    words = ["ﬁsh", "ǆungla", "asha ali"]
    table = sdata.table({"w": words}, fast=fast).turn_into_title_case("w")
    assert table.get_column("w") == pd.Series(words, dtype="string").str.title().tolist()


@pytest.mark.parametrize("fast", ENGINES)
def test_every_match_leaves_out_empty_matches(fast):
    table = sdata.table({"n": ["baac", "xyz"]}, fast=fast)
    table.add_column_with_part_of_text("m", from_column="n", matches_pattern="a*", every_match=True)
    assert table.get_column("m") == ["aa", None]


def test_markdown_cells_with_a_bar_a_line_break_or_a_date(tmp_path):
    table = sdata.table({"a": ["x|y", "two\nlines"], "d": [dt.datetime(2026, 1, 1), dt.datetime(2026, 1, 2)]})
    table.save(str(tmp_path / "t.md"))
    lines = (tmp_path / "t.md").read_text().splitlines()
    assert len(lines) == 4 and "x\\|y" in lines[2] and "two lines" in lines[3]
    assert "| 2026-01-01 |" in lines[2] and "00:00" not in "".join(lines)
    joined = table.find_summary_of("d", show=["joined text"]).get_column("joined text")
    assert joined == ["2026-01-01; 2026-01-02"]


def test_significant_figures_say_where_they_differ_from_r():
    from simplydata.table.rows import _significant

    assert _significant(0.639075, 5) == 0.63908  # R signif: 0.63907 (the stored number), said in the docstring
    import inspect

    assert "0.639075" in inspect.getdoc(sdata.Table.round_numbers_in)


def test_move_layer_by_must_be_a_finite_number():
    with pytest.raises(sdata.SimplydataError, match="move_layer_by"):
        sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks", move_layer_by=float("inf"))


def test_join_where_says_plainly_when_a_name_clashes(capsys):
    with pytest.raises(sdata.SimplydataError, match="already has a column with that name"):
        sdata.table({"x": [1], "x_other": [2]}).join_with(sdata.table({"x": [3]}), where="x < x_other")
    readings = sdata.table({"time": [1, None, 9]})
    readings.join_with(sdata.table({"start": [0, 8], "end": [6, 10]}), where="time >= start and time < end")
    assert "pairs of rows have an empty cell" in capsys.readouterr().out


def test_nested_json_and_jsonl_get_their_dates(tmp_path):
    import json

    rows = [{"id": 1, "site": {"name": "N1", "date": "2026-01-02"}},
            {"id": 2, "site": {"name": "S2", "date": "2026-01-03"}}]
    (tmp_path / "n.json").write_text(json.dumps(rows))
    (tmp_path / "n.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    for name in ("n.json", "n.jsonl"):
        table = sdata.table(str(tmp_path / name))
        assert table.get_column_names() == ["id", "site.name", "site.date"]
        assert pd.Timestamp(table.get_column("site.date")[0]) == pd.Timestamp("2026-01-02")


def test_the_clipboard_says_when_a_cell_has_a_line_break(monkeypatch, capsys):
    store = {}
    monkeypatch.setattr(pd.DataFrame, "to_clipboard", lambda self, **kw: store.setdefault("df", self))
    monkeypatch.setattr(pd, "read_clipboard", lambda **kw: pd.DataFrame({"a": ['"two', 'lines"']}))
    sdata.table({"a": ["two\nlines"]}).save("clipboard")
    assert "have a line break" in capsys.readouterr().out
    sdata.table("clipboard")
    assert "may have been split" in capsys.readouterr().out


def test_capitalize_and_factorize_say_what_they_are(capsys):
    sdata.help("str.capitalize")
    out = capsys.readouterr().out
    assert "first letter of the whole text" in out
    sdata.help("pd.factorize")
    assert "in sorted order" in capsys.readouterr().out
