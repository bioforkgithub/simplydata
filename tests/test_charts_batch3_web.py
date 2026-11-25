"""Charts phase, batch 3: charts as web pages (approved by Manish on 2026-11-25; decisions D2 to D5 and D10).

A web page is drawn once by matplotlib and seaborn and then copied into plotly (decision D3). So every chart word
is checked here the same way: the chart of the word's own help example is saved as a web page, the plotly figure
is read back (tests/_plotly_reader.py reads plotly's own data: the x, y, base and z arrays, the axis ranges and
tick words, the titles, notes and legend entries) and the three tables must equal those read from the matplotlib
picture: get_numbers_drawn(), get_text_drawn() and get_scales_drawn().

Then the privacy of the saved page (proposal section 3.4): plotly.js inside the file, nothing loaded from the
web, no network call while saving, a page that is a file opened by the browser and no server; and the words
show_in_web_page, show_when_pointing and add_range_bar_x, the refusals of decision D5, and the message without
plotly.
"""

from __future__ import annotations

import contextlib
import io
import math
import re
import socket
import warnings
from html.parser import HTMLParser

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError, learn
from simplydata.chart import Chart
from simplydata.words.layout import Page
from _plotly_reader import numbers_from_web, scales_from_web, text_from_web
from conftest import example_frame


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


@pytest.fixture(autouse=True)
def _plotly(needs_plotly):
    yield


def _web(chart):
    from simplydata import _web

    with contextlib.redirect_stdout(io.StringIO()):
        return _web.web_figure(chart)


# ---------------------------------------------------------------- the same numbers, words and scales
VALUE_KINDS = {"cell", "contour", "hexagon", "slice"}
COLOUR_KINDS = {"line", "dot", "bar", "slice", "band", "hexagon"}


def _cell(v):
    if isinstance(v, (pd.Timestamp,)) or hasattr(v, "year"):
        return pd.Timestamp(v).isoformat()
    if isinstance(v, str):
        return v
    if v is None:
        return "nan"
    v = float(v)
    if math.isnan(v):
        return "nan"
    return f"{v:.6g}"


def _row_keys(frame, three_d=False):
    keys = []
    for _, r in frame.iterrows():
        key = [r["panel"], r["layer"], r["kind"], _cell(r["x"]), _cell(r["y"]), _cell(r["low"]), _cell(r["high"])]
        if r["kind"] in VALUE_KINDS or three_d:
            key.append(_cell(r["value"]))
        if r["kind"] in COLOUR_KINDS:
            key.append(str(r["colour"]).lower())
        keys.append(tuple(str(k) for k in key))
    return sorted(keys)


def picture_tables(chart):
    from simplydata import _style
    from simplydata._numbers_drawn import numbers_drawn
    from simplydata._read_back import scales_drawn, text_drawn

    from simplydata._read_back import drawn

    fig = chart._render()
    with _style.context(chart._settings):
        drawn(fig)  # what a picture shows: seaborn places swarm dots while drawing
        return numbers_drawn(fig), text_drawn(fig), scales_drawn(fig)


def assert_same_on_web(chart):
    numbers, text, scales = picture_tables(chart)
    web = _web(chart)
    three_d = chart._settings.get("projection") == "3d"
    assert _row_keys(numbers_from_web(web), three_d) == _row_keys(numbers, three_d)
    picture_text = sorted((int(p), part, t) for p, part, t in zip(text["panel"], text["part"], text["text"]))
    web_text = text_from_web(web)
    assert sorted((int(p), part, t) for p, part, t in zip(web_text["panel"], web_text["part"], web_text["text"])) \
        == picture_text
    if not three_d and chart._settings.get("projection") != "polar":
        columns = ["panel", "scale", "name", "kind", "flipped", "tick words"]
        picture = scales[columns].astype(str).sort_values(columns).reset_index(drop=True)
        on_web = scales_from_web(web)[columns].astype(str).sort_values(columns).reset_index(drop=True)
        pd.testing.assert_frame_equal(on_web, picture)
        for a, b in zip(scales_from_web(web).sort_values(["panel", "scale"])[["low", "high"]].to_numpy().ravel(),
                        scales.sort_values(["panel", "scale"])[["low", "high"]].to_numpy().ravel()):
            if isinstance(b, float) and math.isnan(b):
                continue
            if hasattr(b, "year"):
                assert pd.Timestamp(a) == pd.Timestamp(b)
            else:
                assert float(a) == pytest.approx(float(b), rel=1e-9, abs=1e-12)
    return web


def _chart_words():
    words = set(Chart._word_names())
    return [k for k in learn.HELP_EXAMPLES if k in words or k in learn.OPTIONS]


NOT_ON_WEB = {"break_between_y", "use_scale_x", "use_scale_y"}  # refused with a sentence (decision D5)


def _example_chart(key, tmp_path, monkeypatch):
    code = "\n".join(line for line in learn.HELP_EXAMPLES[key].splitlines()
                     if ".save(" not in line and ".show()" not in line and "show_in_web_page" not in line)
    monkeypatch.chdir(tmp_path)
    space = {"__name__": "__main__"}
    try:
        with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            exec(compile(code, f"<{key} example>", "exec"), space)
    except SimplydataError as error:
        if "R " in str(error) or "rpy2" in str(error):
            pytest.skip("this example needs R")
        raise
    for name in ("page", "both", "grid"):
        if isinstance(space.get(name), Page):
            return space[name]
    chart = space.get("chart")
    if isinstance(chart, (Chart, Page)):
        return chart
    found = [v for v in space.values() if isinstance(v, (Chart, Page))]
    if not found:
        pytest.skip("the example draws no chart")
    return found[-1]


@pytest.mark.parametrize("key", _chart_words())
def test_every_chart_word_gives_the_same_numbers_words_and_scales_on_the_web(key, tmp_path, monkeypatch):
    if key == "animate":
        pytest.skip("an animation is one plotly frame per picture: test_an_animation_becomes_plotly_frames_...")
    chart = _example_chart(key, tmp_path, monkeypatch)
    if key in NOT_ON_WEB:
        with pytest.raises(SimplydataError, match="plotly cannot draw"):
            _web(chart)
        return
    assert_same_on_web(chart)


def test_dots_with_groups_dates_and_bars_on_the_web():
    weather = sdata.get_example("weather")
    chart = sdata.chart(weather).draw_bars(x="city", y="rain", colour="month")
    web = assert_same_on_web(chart)
    assert {t.type for t in web.data} >= {"bar"}
    visitors = sdata.get_example("visitors")
    chart = sdata.chart(visitors).draw_lines(x="month", y="visitors", colour="museum")
    web = assert_same_on_web(chart)
    assert web.layout.xaxis.type == "date"


def test_a_log_scale_and_a_flipped_axis_are_kept():
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    chart.use_log_scale_y()
    chart.flip_x()
    web = assert_same_on_web(chart)
    assert web.layout.yaxis.type == "log"
    low, high = web.layout.xaxis.range
    assert low > high  # flipped, as on the picture


def test_a_page_of_charts_on_the_web():
    marks = sdata.get_example("marks")
    a = sdata.chart(marks).draw_dots(x="hours", y="marks").write_title_on_top("Dots")
    b = sdata.chart(marks).draw_bars(x="class", y="marks").write_title_on_top("Bars")
    page = sdata.put_side_by_side(a, b)
    page.write_title_on_top("Two charts")
    web = assert_same_on_web(page)
    domains = [web.layout.xaxis.domain, web.layout.xaxis2.domain]
    assert domains[0][1] <= domains[1][0]  # side by side, as on the picture


def test_an_animation_becomes_plotly_frames_with_a_play_button(tmp_path):
    growth = example_frame("growth")
    chart = sdata.chart(growth).draw_dots(x="population", y="forest", colour="country").animate(over="year")
    web = _web(chart)
    years = [str(v) for v in sorted(growth["year"].unique())]
    assert [f.name for f in web.frames] == years
    assert web.layout.updatemenus[0].buttons[0].label == "Play"
    assert [s.label for s in web.layout.sliders[0].steps] == years


# ---------------------------------------------------------------- privacy (proposal section 3.4)
class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.scripts, self.styles, self._open = [], [], [], None

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in ("script", "style"):
            self._open = (tag, [])

    def handle_endtag(self, tag):
        if self._open and tag == self._open[0]:
            (self.scripts if tag == "script" else self.styles).append("".join(self._open[1]))
            self._open = None

    def handle_data(self, data):
        if self._open:
            self._open[1].append(data)


WEB_ADDRESS = re.compile(r"(?:https?:)?//[a-z0-9.-]+\.[a-z]{2,}", re.IGNORECASE)


def _saved_page(tmp_path, chart=None):
    chart = chart or sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks", colour="class")
    path = tmp_path / "marks.html"
    with contextlib.redirect_stdout(io.StringIO()):
        chart.save(str(path))
    return path.read_text(encoding="utf-8")


def test_the_saved_page_loads_nothing_from_the_web(tmp_path):
    page = _saved_page(tmp_path)
    tags = _Tags()
    tags.feed(page)
    for tag, attrs in tags.tags:
        for name in ("src", "href", "data", "action", "srcset", "poster"):
            assert not (attrs.get(name) and WEB_ADDRESS.match(attrs[name])), f"<{tag} {name}={attrs[name]}>"
        assert tag not in ("link", "iframe", "object", "embed", "img", "base"), f"<{tag}> in the page"
    assert not [a for t, a in tags.tags if t == "script" and a.get("src")], "a script loaded from a file or the web"
    for style in tags.styles:
        assert "@import" not in style and not re.search(r"url\(\s*['\"]?(?:https?:)?//", style)
    library = max(tags.scripts, key=len)
    assert len(library) > 1_000_000, "plotly.js is written inside the page"
    for script in tags.scripts:
        if script is library:
            # plotly.js names web addresses (map tiles, its own site) as text; it loads none of them for these
            # charts. It must not load a script, a style sheet or a font itself:
            assert "@import url(http" not in script
            continue
        assert not WEB_ADDRESS.search(script), "the chart's own code names a web address"
    assert "mathjax" not in page.lower().split("</script>")[-1]
    assert "cdn.plot.ly/plotly" not in page.replace(library, "")
    assert "<title>" in page and "fonts.googleapis" not in page


def test_saving_a_web_page_makes_no_network_call(tmp_path, monkeypatch):
    tried = []

    def refuse(self, address):
        tried.append(address)
        raise OSError("no network in this test")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: tried.append(a) or (_ for _ in ()).throw(OSError()))
    _saved_page(tmp_path)
    assert not tried


def test_the_page_turns_off_plotlys_links_and_picture_button(tmp_path):
    page = _saved_page(tmp_path)
    config = re.search(r'Plotly\.newPlot\([^;]*?(\{"displaylogo".*?\})\s*\)', page, re.S)
    assert config, "the page's settings"
    assert '"displaylogo": false' in config.group(1) and '"toImage"' in config.group(1)


def test_saving_says_once_that_the_page_holds_the_numbers(tmp_path, capsys):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    chart.save(str(tmp_path / "a.html"))
    chart.save(str(tmp_path / "b.html"))
    out = capsys.readouterr().out
    assert out.count("the web page holds the numbers drawn") == 1


def test_show_in_web_page_opens_a_file_on_this_computer_and_starts_no_server(no_browser, tmp_path, monkeypatch):
    import http.server
    import socketserver

    started = []
    monkeypatch.setattr(socketserver.TCPServer, "__init__", lambda *a, **k: started.append(a))
    monkeypatch.setattr(http.server.HTTPServer, "server_bind", lambda *a, **k: started.append(a))
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    with contextlib.redirect_stdout(io.StringIO()) as out:
        assert chart.show_in_web_page() is chart
    assert len(no_browser) == 1 and no_browser[0].startswith("file:")
    assert not started
    files = list(tmp_path.glob("simplydata_chart_*.html"))
    assert len(files) == 1 and "file on this computer" in out.getvalue()


def test_only_file_addresses_are_opened():
    from simplydata._web import open_file_in_browser

    with pytest.raises(SimplydataError, match="files on this computer"):
        open_file_in_browser("https://example.org/chart.html")


def test_in_a_notebook_the_page_is_shown_below_the_cell(monkeypatch):
    from simplydata import _web

    import sys
    import types

    shown = []
    monkeypatch.setattr(_web, "in_notebook", lambda: True)
    display = types.ModuleType("IPython.display")  # a stand-in for IPython's own, which only shows what it gets

    class HTML:
        def __init__(self, data):
            self.data = data

    display.HTML, display.display = HTML, shown.append
    monkeypatch.setitem(sys.modules, "IPython", types.ModuleType("IPython"))
    monkeypatch.setitem(sys.modules, "IPython.display", display)
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    with contextlib.redirect_stdout(io.StringIO()):
        chart.show_in_web_page()
    assert len(shown) == 1 and "<script" in shown[0].data and "<html>" not in shown[0].data


# ---------------------------------------------------------------- pointing, range bar, refusals
def test_show_when_pointing_shows_only_the_named_columns_of_each_dot():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_dots(x="hours", y="marks")
    chart.show_when_pointing("name", "class")
    web = _web(chart)
    texts = [t for trace in web.data if trace.type == "scatter" and trace.text for t in trace.text]
    assert len(texts) == len(marks)
    first = texts[0]
    assert f"name: {marks['name'][0]}" in first and f"class: {marks['class'][0]}" in first
    assert "subject:" not in first and "height:" not in first  # never the whole row
    names = sorted(re.search(r"name: ([^<]+)", t).group(1) for t in texts)
    assert names == sorted(marks["name"].astype(str))


def test_all_lines_shows_one_box_for_every_line_at_that_x():
    chart = sdata.chart(sdata.get_example("weather")).draw_lines(x="month_number", y="temperature", colour="city")
    chart.show_when_pointing(all_lines=True)
    assert _web(chart).layout.hovermode == "x unified"


def test_show_when_pointing_checks_its_columns_and_undo_takes_it_back():
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    with pytest.raises(SimplydataError, match="nme"):
        chart.show_when_pointing("nme")
    with pytest.raises(SimplydataError, match="needs the columns"):
        chart.show_when_pointing()
    chart.show_when_pointing("name")
    with contextlib.redirect_stdout(io.StringIO()) as out:
        chart.undo()
    assert "chart.show_when_pointing()" in out.getvalue()
    assert not chart._settings.get("pointing")


def test_a_picture_notes_once_that_pointing_and_range_bars_are_web_only(tmp_path, capsys):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    chart.show_when_pointing("name").add_range_bar_x()
    chart.save(str(tmp_path / "a.png"))
    chart.save(str(tmp_path / "b.png"))
    assert capsys.readouterr().out.count("only show in web pages") == 1


def test_add_range_bar_x_puts_plotlys_range_slider_under_the_x_axis():
    chart = sdata.chart(sdata.get_example("visitors")).draw_lines(x="month", y="visitors", colour="museum")
    chart.add_range_bar_x()
    web = _web(chart)
    assert web.layout.xaxis.rangeslider.visible is True
    with pytest.raises(SimplydataError, match="flat charts"):
        sdata.chart(sdata.get_example("island")).draw_surface(x="east", y="north", z="height").add_range_bar_x()


@pytest.mark.parametrize("step, words", [
    (lambda c: c.break_between_y(70, 80), "broken axis"),
    (lambda c: c.use_scale_y("square root"), "square-root scale"),
    (lambda c: c.use_scale_x("logit"), "logit scale"),
    (lambda c: c.use_log_scale_y(through_zero=True), "log scale through zero"),
])
def test_what_plotly_cannot_draw_is_refused_with_one_sentence(step, words, tmp_path):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    if "logit" in words:
        chart = sdata.chart(pd.DataFrame({"share": [0.1, 0.5, 0.9], "y": [1, 2, 3]})).draw_dots(x="share", y="y")
    step(chart)
    with pytest.raises(SimplydataError, match=words) as error:
        chart.save(str(tmp_path / "x.html"))
    assert "save a picture (.png, .pdf) instead" in str(error.value)
    assert str(error.value).count(".") <= 6  # one sentence (the dots of the file types and word names aside)
    with contextlib.redirect_stdout(io.StringIO()):
        chart.save(str(tmp_path / "x.png"))  # the picture is fine


def test_resolution_is_refused_for_a_web_page(tmp_path):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    with pytest.raises(SimplydataError, match="no resolution"):
        chart.save(str(tmp_path / "x.html"), resolution=600)


def test_see_through_makes_the_page_background_clear(tmp_path):
    from simplydata import _web as web_module

    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    with contextlib.redirect_stdout(io.StringIO()):
        web = web_module.web_figure(chart, see_through=True)
    assert web.layout.paper_bgcolor == "rgba(0,0,0,0)" and web.layout.plot_bgcolor == "rgba(0,0,0,0)"


def test_interactive_is_another_name_that_points_to_the_web_words():
    marks = sdata.get_example("marks")
    with pytest.raises(SimplydataError, match="show_in_web_page"):
        sdata.chart(marks, interactive=True)
    with pytest.raises(SimplydataError, match="show_in_web_page"):
        sdata.table(marks).start_chart(interactive=True)


@pytest.mark.parametrize("name, word", [("write_html", "save"), ("to_html", "save"), ("iplot", "show_in_web_page"),
                                        ("hovertemplate", "show_when_pointing"), ("rangeslider", "add_range_bar_x")])
def test_plotly_names_point_to_the_simplydata_words(name, word):
    chart = sdata.chart(sdata.get_example("marks"))
    with pytest.raises(SimplydataError, match=word):
        getattr(chart, name)


def test_without_plotly_a_web_page_says_how_to_install_it(monkeypatch, tmp_path):
    import builtins

    real_import = builtins.__import__

    def no_plotly(name, *args, **kwargs):
        if name == "plotly" or name.startswith("plotly."):
            raise ImportError("No module named 'plotly'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_plotly)
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    for call in (lambda: chart.save(str(tmp_path / "x.html")), chart.show_in_web_page):
        with pytest.raises(SimplydataError) as error:
            call()
        assert 'pip install "simplydata[web]"' in str(error.value)
        assert type(error.value) is SimplydataError
    assert not (tmp_path / "x.html").exists()


def test_the_page_names_plotly_among_the_packages_used(tmp_path):
    from simplydata import _cite

    _saved_page(tmp_path)
    assert "plotly" in _cite._USED_PYTHON


def test_the_description_is_in_the_page_for_screen_readers(tmp_path):
    chart = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    chart.write_title_on_top("Marks by class")
    page = _saved_page(tmp_path, chart)
    assert "<title>Marks by class</title>" in page
    assert "draw_bars(x=&quot;class&quot;, y=&quot;marks&quot;)" in page


def test_colours_and_hatches_of_bars_go_to_the_web():
    chart = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks", colour="subject", hatched=True)
    web = assert_same_on_web(chart)
    bars = [t for t in web.data if t.type == "bar"]
    assert all(t.marker.pattern.shape for t in bars)
    assert len({tuple(t.marker.color) for t in bars}) == len(bars)


def test_numbers_are_those_of_the_picture_not_worked_out_again():
    marks = sdata.get_example("marks")
    chart = sdata.chart(marks).draw_violins(x="class", y="marks")
    numbers, _, _ = picture_tables(chart)
    web = numbers_from_web(_web(chart))
    picture_shapes = numbers[numbers["kind"].isin(["band", "shape"])][["x", "y"]].to_numpy(dtype=float)
    web_shapes = web[web["kind"].isin(["band", "shape"])][["x", "y"]].to_numpy(dtype=float)
    assert np.array_equal(np.sort(np.nan_to_num(picture_shapes), axis=0), np.sort(np.nan_to_num(web_shapes), axis=0))
