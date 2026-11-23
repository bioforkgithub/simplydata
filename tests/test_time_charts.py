"""Chart words for time series and signals, and chart.draw_smooth_line with the smoothing methods.

The chart words draw what the table words give back (those numbers are checked against R in
test_time_series.py, test_forecast.py, test_spectrum and test_filters.py); here the drawn data is compared
with the table words. The spectrogram is checked against R by hand (ref_spectrogram.R, partD scratch):
pieces of 100 readings, periodic Hann weights, each piece's mean removed, |fft|^2 / (fs * sum(w^2)),
doubled except at 0 and the top frequency.
"""

import matplotlib
import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from conftest import example_frame

matplotlib.use("Agg")


def harbour():
    data = example_frame("visitors")
    return data[data["museum"] == "Harbour Museum"].reset_index(drop=True)


def native(table):
    return table._frame.to_pandas()


def test_sticks_draws_a_line_from_zero_to_each_value():
    data = pd.DataFrame({"k": [1, 2, 3, 4], "r": [0.5, -0.2, 0.1, 0.3]})
    ax = sdata.chart(data).sticks(x="k", y="r")._render().axes[0]
    segments = ax.collections[0].get_segments()
    assert [tuple(s[:, 1]) for s in segments] == [(0, 0.5), (0, -0.2), (0, 0.1), (0, 0.3)]
    assert ax.get_lines()[0].get_ydata().tolist() == [0.5, -0.2, 0.1, 0.3]
    with pytest.raises(SimplydataError, match="needs x= and y="):
        sdata.chart(data).sticks(x="k")
    sdata.chart(data).sticks(x="k", y="r").draw_line_at_y(0.2)._render()  # a line on top works


def test_autocorrelation_bars_equal_autocorrelation_of(capsys):
    data = harbour()
    chart = sdata.chart(data).autocorrelation_bars("visitors", sorted_by="month", rows_back=24)
    ax = chart._render().axes[0]
    heights = [s[1, 1] for s in ax.collections[0].get_segments()]
    table = native(sdata.table(data).find_autocorrelation_of("visitors", sorted_by="month", rows_back=24))
    assert heights == pytest.approx(table["correlation"].tolist(), rel=1e-12)
    assert len(heights) == 24
    assert "Ljung-Box" in capsys.readouterr().out
    # the spellings before the name review (x=, y=) still work
    old = sdata.chart(data).autocorrelation_bars(x="month", y="visitors", rows_back=24)._render().axes[0]
    assert [s[1, 1] for s in old.collections[0].get_segments()] == pytest.approx(heights, rel=1e-12)


def test_cross_correlation_bars_equal_correlation_between():
    data = example_frame("sensor")
    ax = sdata.chart(data).cross_correlation_bars("signal", "vibration", sorted_by="time",
                                                  rows_back=10)._render().axes[0]
    heights = [s[1, 1] for s in ax.collections[0].get_segments()]
    table = native(sdata.table(data).find_correlation_between("signal", "vibration", rows_back=10, sorted_by="time"))
    value = [c for c in table.columns if table[c].dtype.kind == "f" and not c.startswith("shift")
             and "band" not in c][0]
    assert heights == pytest.approx(table[value].tolist(), rel=1e-12)
    old = sdata.chart(data).cross_correlation_bars(x="time", y="signal", against="vibration",
                                                   rows_back=10)._render().axes[0]
    assert [s[1, 1] for s in old.collections[0].get_segments()] == pytest.approx(heights, rel=1e-12)
    with pytest.raises(SimplydataError, match="needs two columns"):
        sdata.chart(data).cross_correlation_bars("signal", sorted_by="time")
    with pytest.raises(SimplydataError, match="no option called"):
        sdata.chart(data).cross_correlation_bars("signal", "vibration", shift=3)


def test_lag_dots():
    data = harbour()
    ax = sdata.chart(data).lag_dots("visitors", sorted_by="month", rows_back=[1, 12],
                                    transparency=0.5)._render().axes[0]
    first = ax.collections[0].get_offsets()
    v = data.sort_values("month")["visitors"].to_numpy(dtype=float)
    assert pytest.approx(v[:-1]) == first[:, 0] and pytest.approx(v[1:]) == first[:, 1]
    assert len(ax.collections[1].get_offsets()) == len(v) - 12
    assert ax.collections[0].get_alpha() == pytest.approx(0.5)
    with pytest.raises(SimplydataError, match="whole numbers"):
        sdata.chart(data).lag_dots(y="visitors", rows_back=0)
    with pytest.raises(SimplydataError, match="transparency=1"):
        sdata.chart(data).lag_dots("visitors", transparency=1)


def test_trend_and_season_panels_equal_the_table_word():
    data = harbour()
    fig = sdata.chart(data).trend_and_season(x="month", y="visitors", repeats_every="year")._render()
    panels = fig.axes[0].child_axes
    assert [p.get_ylabel() for p in panels] == ["visitors", "trend", "season", "rest"]
    table = sdata.table(data)
    table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year")
    trend = native(table).sort_values("month")["visitors_trend"].to_numpy()
    assert panels[1].get_lines()[0].get_ydata() == pytest.approx(trend, rel=1e-12)


def test_trend_and_season_says_what_is_underneath(capsys):
    """The printout names the work underneath: statsmodels STL for the parts, matplotlib inset axes for the panels."""
    sdata.chart(harbour()).trend_and_season(x="month", y="visitors", repeats_every="year")
    printed = capsys.readouterr().out
    assert "STL" in printed and "statsmodels" in printed
    assert "Drawn by matplotlib" in printed and "inset axes" in printed


@pytest.mark.usefixtures("needs_r")
def test_chart_forecast_equals_table_forecast():
    data = harbour()
    chart = sdata.chart(data).draw_lines(x="month", y="visitors").forecast(steps_ahead=6, repeats_every="year")
    ax = chart._render().axes[0]
    dashed = [line for line in ax.get_lines() if line.get_linestyle() == "--"][0]
    table = native(sdata.table(data).forecast("visitors", sorted_by="month", steps_ahead=6, repeats_every="year"))
    assert dashed.get_ydata() == pytest.approx(table["forecast"].to_numpy(), rel=1e-12)


def test_spectrum_chart_equals_spectrum_of():
    data = example_frame("sensor")
    ax = sdata.chart(data).spectrum("signal", sorted_by="time")._render().axes[0]
    table = native(sdata.table(data).find_spectrum_of("signal", sorted_by="time"))
    table = table[table["frequency"] > 0]
    assert ax.get_lines()[0].get_ydata() == pytest.approx(table["power"].to_numpy(), rel=1e-12)
    assert ax.get_yscale() == "log"
    labels = [t.get_text() for t in ax.texts]
    assert "repeats every 0.2" in labels and len(labels) == 3


def test_spectrum_over_time_matches_r():
    from simplydata.words.time_charts import spectrum_over_time

    x = example_frame("sensor")["signal"].to_numpy()
    f, t, power = spectrum_over_time(x, 0.005, 100)
    # R by hand (ref_spectrogram.R): piece 1 at frequencies 0, 4 and 100; piece 5 at 4; middle times 0.25, 1.25
    assert power[[0, 2, 50], 0] == pytest.approx([0.00385981167326594, 0.151959085622423, 0.000378566612598927],
                                                rel=1e-10)
    assert power[2, 4] == pytest.approx(0.127424736887222, rel=1e-10)
    assert t[[0, 4]] == pytest.approx([0.25, 1.25]) and f[2] == pytest.approx(4)
    sdata.chart(sdata.get_example("sensor")).spectrum_over_time("signal", sorted_by="time", window=100)._render()
    with pytest.raises(SimplydataError, match="window="):
        sdata.chart(sdata.get_example("sensor")).spectrum_over_time("signal", sorted_by="time", window=2)


def test_peak_dots_equal_find_peaks():
    data = example_frame("sensor")
    ax = sdata.chart(data).draw_lines(x="time", y="signal").peak_dots(is_at_least=1, apart=0.05)._render().axes[0]
    table = native(sdata.table(data).find_each_peak_that("signal", sorted_by="time", is_at_least=1, apart=0.05))
    dots = ax.collections[-1].get_offsets()
    assert len(dots) == 41 and pytest.approx(table["value"].to_numpy()) == dots[:, 1]
    ax = sdata.chart(data).draw_lines(x="time", y="signal").peak_dots(dips=True, is_at_most=-1)._render().axes[0]
    assert len(ax.collections[-1].get_offsets()) > 0


@pytest.mark.parametrize("method, options", [("moving average", {"window": 5}), ("savitzky-golay", {"window": 11}),
                                             ("exponential", {"newest_weight": 0.3}), ("gaussian", {"width": 2}),
                                             pytest.param("whittaker", {"smoothness": 50}, marks=pytest.mark.skipif(
                                                 not hasattr(__import__("scipy.signal").signal, "whittaker_henderson"),
                                                 reason="SciPy 1.17 or newer (Python 3.12 or newer)")),
                                             ("wiener", {"window": 7})])
def test_smooth_line_methods_equal_nums_smooth(method, options):
    data = example_frame("sensor")
    ax = sdata.chart(data).draw_dots(x="time", y="signal").draw_smooth_line(test_method=method, **options)._render().axes[0]
    drawn = ax.get_lines()[-1].get_ydata()
    nums = sdata.numbers(data["signal"])
    nums.smooth(test_method=method, **options)
    assert np.asarray(drawn, dtype=float) == pytest.approx(np.asarray(nums._values, dtype=float), rel=1e-12,
                                                           nan_ok=True)


def test_smooth_line_window_methods_need_even_steps():
    data = pd.DataFrame({"x": [1, 2, 4, 5, 6, 8, 9], "y": [1, 3, 2, 5, 4, 6, 5]})
    chart = sdata.chart(data).draw_dots(x="x", y="y").draw_smooth_line(test_method="moving average", window=3)
    with pytest.raises(SimplydataError, match="evenly spaced"):
        chart._render()
    with pytest.raises(SimplydataError, match="window="):
        sdata.chart(data).draw_dots(x="x", y="y").draw_smooth_line(test_method="moving average", window=4)
    with pytest.raises(SimplydataError, match="go with the window"):
        sdata.chart(data).draw_dots(x="x", y="y").draw_smooth_line(window=3)
    sdata.chart(data).draw_dots(x="x", y="y").draw_smooth_line()._render()  # lowess still takes uneven x
