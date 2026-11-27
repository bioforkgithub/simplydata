"""seaborn's colour tools (owner's decision 2026-11-28: cover all of seaborn): show_colours, change_colour,
pick_colours_with_sliders, from_colour_list= and use_style(colour_letters=), against seaborn itself."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.colors as mcolors  # noqa: E402
import pytest  # noqa: E402
import seaborn as sns  # noqa: E402

import simplydata as sdata  # noqa: E402
from simplydata import SimplydataError, colours  # noqa: E402
from simplydata._errors import MissingWordError  # noqa: E402


def _bar_colours(chart):
    return [mcolors.to_hex(c) for c in chart.get_numbers_drawn().as_pandas()["colour"]]


# ---------------------------------------------------------------- show_colours
def test_show_colours_gives_and_prints_seabornss_codes(capsys, tmp_path):
    codes = sdata.show_colours("deep")
    assert codes == sns.color_palette("deep").as_hex()
    out = capsys.readouterr().out
    assert "seaborn palplot" in out and all(c in out for c in codes)
    sdata.show_colours(["navy", "#E69F00"], save_as=str(tmp_path / "c.png"))
    assert (tmp_path / "c.png").is_file()
    assert sdata.show_colours("viridis", how_many=4) == sns.color_palette("viridis", 4).as_hex()


def test_show_colours_refuses_what_is_not_a_set_of_colours():
    with pytest.raises(SimplydataError, match="named set of colours"):
        sdata.show_colours("no such set")
    with pytest.raises(SimplydataError, match="how_many="):
        sdata.show_colours("deep", how_many=0)


# ---------------------------------------------------------------- change_colour
@pytest.mark.parametrize("ours, theirs", [
    (dict(lightness=0.6), lambda c: sns.set_hls_values(c, l=0.6)),
    (dict(colour_strength=0.3), lambda c: sns.set_hls_values(c, s=0.3)),
    (dict(hue=0.5), lambda c: sns.set_hls_values(c, h=0.5)),
    (dict(colour_strength_times=0.5), lambda c: sns.desaturate(c, 0.5)),
    (dict(full_colour_strength=True), sns.saturate),
])
def test_change_colour_is_seaborn(ours, theirs):
    for colour in ("navy", "#7a8f99", "darkorange"):
        assert sdata.change_colour(colour, **ours) == mcolors.to_hex(theirs(colour))


def test_change_colour_checks_what_it_is_given():
    with pytest.raises(SimplydataError, match="needs a colour"):
        sdata.change_colour("not a colour", lightness=0.5)
    with pytest.raises(SimplydataError, match="from 0 to 1"):
        sdata.change_colour("navy", lightness=2)
    with pytest.raises(SimplydataError, match="needs what to change"):
        sdata.change_colour("navy")


# ---------------------------------------------------------------- pick_colours_with_sliders
def test_outside_jupyter_the_sliders_say_what_is_needed(capsys):
    assert sdata.pick_colours_with_sliders(kind="dark") is None
    assert "need Jupyter" in capsys.readouterr().out


def test_without_ipywidgets_the_sliders_say_so_and_install_nothing(monkeypatch, capsys):
    import builtins

    import simplydata._web as web

    monkeypatch.setattr(web, "in_notebook", lambda: True)
    real_import = builtins.__import__

    def no_widgets(name, *args, **kwargs):
        if name == "ipywidgets":
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_widgets)
    assert sdata.pick_colours_with_sliders(kind="light") is None
    out = capsys.readouterr().out
    assert "ipywidgets" in out and "never installs" in out


@pytest.mark.parametrize("kind, function", list(colours.SLIDER_KINDS.items()))
def test_each_kind_calls_its_seaborn_widget(kind, function, monkeypatch):
    import seaborn.widgets as widgets

    called = {}
    monkeypatch.setattr(colours, "_jupyter_and_widgets", lambda: None)
    monkeypatch.setattr(widgets, function, lambda *args, **kwargs: called.setdefault("args", args) or ["#000000"])
    sdata.pick_colours_with_sliders(kind=kind, brewer_type="diverging")
    assert called["args"] == (("diverging",) if kind == "brewer" else ())


def test_an_unknown_kind_gets_did_you_mean():
    with pytest.raises(SimplydataError, match='Did you mean kind="dark"'):
        sdata.pick_colours_with_sliders(kind="darkk")


# ---------------------------------------------------------------- from_colour_list= and colour_letters=
def test_use_colours_reads_xkcd_and_crayon_names():
    chart = sdata.chart(sdata.get_example("marks"))
    chart.draw_bars(x="class", y="marks", colour="class")
    chart.use_colours("windows blue", "amber", "faded green", from_colour_list="xkcd")
    assert _bar_colours(chart) == [mcolors.to_hex(c) for c in sns.xkcd_palette(["windows blue", "amber",
                                                                                 "faded green"])]
    chart = sdata.chart(sdata.get_example("marks"))
    chart.draw_bars(x="class", y="marks")
    chart.use_colour("Mahogany", from_colour_list="crayon")
    assert set(_bar_colours(chart)) == {mcolors.to_hex(sns.crayon_palette(["Mahogany"])[0])}


def test_use_colour_scale_reads_xkcd_names():
    chart = sdata.chart(sdata.get_example("weather"))
    chart.draw_heatmap(x="month", y="city", value="rain")
    chart.use_colour_scale("pale yellow", "dark red", from_colour_list="xkcd")
    cmap = chart.as_matplotlib().axes[0].collections[0].cmap
    low, high = sns.xkcd_palette(["pale yellow", "dark red"])
    assert mcolors.to_hex(cmap(0.0)) == mcolors.to_hex(low) and mcolors.to_hex(cmap(1.0)) == mcolors.to_hex(high)


def test_a_name_the_list_lacks_gets_did_you_mean():
    chart = sdata.chart(sdata.get_example("marks"))
    with pytest.raises(SimplydataError, match='Did you mean "windows blue"'):
        chart.use_colours("windows bleu", from_colour_list="xkcd")
    with pytest.raises(SimplydataError, match="from_colour_list"):
        chart.use_colours("red", from_colour_list="pantone")


def test_colour_letters_are_seaborns_on_this_chart_only():
    chart = sdata.chart(sdata.get_example("marks"))
    chart.draw_bars(x="class", y="marks", colour="class")
    chart.use_colours("b", "g", "r")
    chart.use_style("paper", colour_letters="seaborn")
    deep = sns.color_palette("deep6")
    assert _bar_colours(chart) == [mcolors.to_hex(deep[i]) for i in (0, 1, 2)]
    assert mcolors.to_hex("b") == "#0000ff"  # matplotlib's own letters come back for every other chart
    plain = sdata.chart(sdata.get_example("marks"))
    plain.draw_bars(x="class", y="marks", colour="class")
    plain.use_colours("b", "g", "r")
    assert _bar_colours(plain) == ["#0000ff", "#008000", "#ff0000"]
    with pytest.raises(SimplydataError, match="colour_letters"):
        chart.use_style("paper", colour_letters="neon")


# ---------------------------------------------------------------- pointers
@pytest.mark.parametrize("typed, word", [
    ("sns.palplot", "sdata.show_colours("), ("sns.choose_cubehelix_palette", 'kind="cubehelix"'),
    ("sns.xkcd_palette", 'from_colour_list="xkcd"'), ("sns.crayon_palette", 'from_colour_list="crayon"'),
    ("sns.desaturate", "colour_strength_times="), ("sns.saturate", "full_colour_strength=True"),
    ("sns.set_hls_values", "lightness="), ("sns.set_color_codes", 'colour_letters="seaborn"'),
    ("sns.dogplot", "downloads nothing"), ("sns.reset_defaults", "nothing to reset"),
    ("sns.reset_orig", "nothing to reset"), ("sns.get_data_home", "nothing is downloaded"),
    ("sns.set", "use_style"),
    ("so.Dot", "chart.draw_dots("), ("so.Bars", "chart.draw_bars("), ("so.Hist", "chart.draw_histogram("),
    ("so.KDE", "chart.draw_density("), ("so.Stack", "stacked=True"), ("so.PolyFit", "fit_curve(of_degree=2)"),
    ("so.Plot", "sdata.chart(table)"), ("so.Plot.facet", "draw_one_chart_for_each_group_in("),
    ("seaborn.objects.Plot.pair", "sdata.draw_all_pairs("), ("seaborn.objects.Area", "chart.draw_area("),
])
def test_seaborn_names_point_to_their_word(typed, word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert word in out, out


@pytest.mark.parametrize("typed, heading", [("so.Plot.save", "chart.save()"), ("so.Plot.show", "chart.show()")])
def test_a_plot_method_that_is_a_chart_word_explains_it(typed, heading, capsys):
    sdata.help(typed)
    assert capsys.readouterr().out.startswith(heading)


def test_a_seaborn_name_on_a_chart_never_runs():
    with pytest.raises(MissingWordError, match="show_colours"):
        sdata.chart().palplot  # noqa: B018 - a pointer, never a word
