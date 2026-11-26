"""sdata.make_run_of_dates, add_missing_dates, add_rolling_column (time windows, "all", centre=, new show= values),
smoothing (nums.smooth, add_smoothed_column) and nums.remove_trend, checked against R.

Reference values: R 4.6.2 with signal 1.8.1 and zoo 1.9.1 (ref_partA.R in the v0.6 scratch folder):
x <- read.csv("sensor.csv")$signal[1:60]; rv <- read.csv("river.csv"); rv$date <- as.Date(rv$date)
a <- rv[rv$station == "Station A", ]; d <- a$date; y <- a$nitrate
"""

import datetime

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table
from conftest import example_frame

ENGINES = ["pandas", "polars"]


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(data, fast=True)
    return make_table(data)


def col(t, name):
    return np.asarray(t._frame[name].to_numpy(), dtype=float)


def signal60():
    return sdata.numbers(example_frame("sensor")["signal"][:60])


def station_a(engine):
    data = example_frame("river")
    return make(data[data.station == "Station A"].reset_index(drop=True), engine)


def as_dates(values):
    return [v.date() if isinstance(v, datetime.datetime) else v for v in values]


# ---------------------------------------------------------------- sdata.make_run_of_dates
def test_dates_by_day_match_r(capsys):
    t = sdata.make_run_of_dates("2026-01-01", to="2026-12-31", every="day")
    # R: length(seq(as.Date("2026-01-01"), as.Date("2026-12-31"), by = "day")) = 365
    assert len(t._frame) == 365
    assert "365 dates from 2026-01-01 to 2026-12-31, one every day." in capsys.readouterr().out


def test_dates_month_ends_and_weeks_match_r():
    t = sdata.make_run_of_dates("2026-01-31", how_many=3, every="month")
    # R: seq(as.Date("2026-02-01"), by = "month", length.out = 3) - 1
    assert as_dates(t._frame["date"].to_list()) == [datetime.date(2026, 1, 31), datetime.date(2026, 2, 28),
                                                    datetime.date(2026, 3, 31)]
    t = sdata.make_run_of_dates("2026-01-01", to="2026-02-01", every="week", fast=True)
    # R: seq(as.Date("2026-01-01"), as.Date("2026-02-01"), by = "week")
    assert as_dates(t._frame["date"].to_list()) == [datetime.date(2026, 1, d) for d in (1, 8, 15, 22, 29)]
    assert t._frame.implementation.is_polars()
    t = sdata.make_run_of_dates("2026-01-01 00:00", how_many=3, every="15 minutes")
    assert [str(v)[11:16] for v in t._frame["date"].to_list()] == ["00:00", "00:15", "00:30"]


def test_dates_errors():
    with pytest.raises(SimplydataError, match="either to="):
        sdata.make_run_of_dates("2026-01-01")
    with pytest.raises(SimplydataError, match="every"):
        sdata.make_run_of_dates("2026-01-01", how_many=3, every="fortnight")
    with pytest.raises(SimplydataError, match="a date such as"):
        sdata.make_run_of_dates("someday", how_many=3)


# ---------------------------------------------------------------- add_missing_dates
def test_add_missing_dates_matches_r(engine, capsys):
    t = make(example_frame("river"), engine)
    t.add_missing_dates("date", every="day", for_each_group_in="station")
    # R: merge(data.frame(date = seq(min(d), max(d), by = "day")), x, all.x = TRUE): 6 days added for
    #    Station A (the first 2024-03-17), 9 for Station B (the first 2024-01-18)
    assert len(t._frame) == 2 * 731
    out = capsys.readouterr().out
    assert 'Added 15 missing days to "date" (6 for Station A, 9 for Station B)' in out
    frame = t._frame.to_pandas() if hasattr(t._frame, "to_pandas") else t._frame
    row = frame[(frame.station == "Station A") & (frame.date == "2024-03-17")]
    assert len(row) == 1 and np.isnan(row["nitrate"].iloc[0])
    t.undo()
    assert len(t._frame) == 1447


def test_add_missing_dates_finds_the_step(engine, capsys):
    t = make(example_frame("river"), engine)
    t.add_missing_dates("date", for_each_group_in="station")
    assert "(every day: the most common step)" in capsys.readouterr().out


def test_add_missing_dates_between(capsys):
    t = station_a("pandas")
    t.add_missing_dates("date", every="day", between=["2023-12-30", "2026-01-02"])
    assert len(t._frame) == 731 + 4


def test_add_missing_dates_errors(engine):
    t = make(example_frame("river"), engine)
    with pytest.raises(SimplydataError, match="does not hold dates"):
        t.add_missing_dates("level")
    with pytest.raises(SimplydataError, match="same date"):
        t.add_missing_dates("date", every="day")  # two stations on each day


# ---------------------------------------------------------------- add_rolling_column
def test_rolling_time_window_matches_r(engine, capsys):
    t = station_a(engine)
    t.add_rolling_column("n7", from_column="nitrate", window="7 days", sorted_by="date")
    # R: sapply(d, function(t) mean(y[d > t - 7 & d <= t]))[c(1, 10, 100)]
    assert col(t, "n7")[[0, 9, 99]] == pytest.approx([3.15, 3.18, 3.22571428571429], rel=1e-12)
    assert "the 7 days up to and including this row's date" in capsys.readouterr().out
    t.add_rolling_column("count7", from_column="nitrate", window="7 days", sorted_by="date", show="count")
    # R: sapply(d, function(t) sum(d > t - 7 & d <= t))[c(1, 10, 100)]
    assert col(t, "count7")[[0, 9, 99]].tolist() == [1, 7, 7]


def test_rolling_all_and_centre_match_r(engine, capsys):
    t = station_a(engine)
    t.add_rolling_column("mean_so_far", from_column="nitrate", window="all", sorted_by="date")
    assert "running values have their own word: add_running_column" in capsys.readouterr().out
    # R: (cumsum(y) / seq_along(y))[c(1, 10, 100)]
    assert col(t, "mean_so_far")[[0, 9, 99]] == pytest.approx([3.15, 3.188, 3.2654], rel=1e-12)
    t.add_rolling_column("max_so_far", from_column="nitrate", window="all", show="biggest", sorted_by="date")
    assert col(t, "max_so_far")[[9, 99]] == pytest.approx([3.67, 4.2])  # R: cummax(y)[c(10, 100)]
    t.add_rolling_column("centred", from_column="nitrate", window=7, centre=True, sorted_by="date")
    # R: stats::filter(y, rep(1/7, 7), sides = 2)[c(4, 100)]
    values = col(t, "centred")
    assert np.isnan(values[:3]).all()
    assert values[[3, 99]] == pytest.approx([3.23714285714286, 3.22285714285714], rel=1e-12)


# test_method="whittaker" is SciPy signal.whittaker_henderson, new in SciPy 1.17 (Python 3.12 or newer)
NEEDS_SCIPY_117 = pytest.mark.skipif(not hasattr(__import__("scipy.signal").signal, "whittaker_henderson"),
                                     reason="SciPy 1.17 or newer (Python 3.12 or newer)")


def test_whittaker_without_scipy_117_says_what_to_do(monkeypatch):
    from scipy import signal

    monkeypatch.delattr(signal, "whittaker_henderson", raising=False)
    with pytest.raises(SimplydataError, match="needs SciPy 1.17 or newer"):
        sdata.numbers([1.0, 2, 3, 2, 1]).smooth(test_method="whittaker")


@pytest.mark.parametrize("show, kwargs, expected", [
    # R (y[91:100]): var(w); skewness and excess kurtosis adjusted for small samples (sk and ku in
    # ref_partA.R: G1 = g1 * sqrt(n (n - 1)) / (n - 2); G2 = ((n + 1) g2 + 6) (n - 1) / ((n - 2) (n - 3)));
    # quantile(w, 0.9, type = 7)
    ("variance", {}, 0.199738888888889),
    ("skewness", {}, 1.01258723382417),
    ("kurtosis", {}, 0.763227686469065),
    ("percentile", {"percent": 90}, 3.777),
])
def test_rolling_new_summaries_match_r(engine, show, kwargs, expected):
    t = station_a(engine)
    t.add_rolling_column("r", from_column="nitrate", window=10, show=show, sorted_by="date", **kwargs)
    assert col(t, "r")[99] == pytest.approx(expected, rel=1e-10)


def test_rolling_correlation_matches_r(engine):
    t = station_a(engine)
    t.fill_empty_cells_in("level", with_the="line between neighbours", sorted_by="date")
    t.add_rolling_column("r", from_column=["nitrate", "level"], window=10, show="correlation", sorted_by="date")
    t.add_rolling_column("c", from_column=["nitrate", "level"], window=10, show="covariance", sorted_by="date")
    # R: cor(y[91:100], a$level[91:100]); cov(...) (no empty level cells in rows 91 to 100)
    assert col(t, "r")[99] == pytest.approx(0.411065379374423, rel=1e-10)
    assert col(t, "c")[99] == pytest.approx(0.0102822222222222, rel=1e-10)


def test_rolling_errors(engine):
    t = station_a(engine)
    with pytest.raises(SimplydataError, match="odd number"):
        t.add_rolling_column("r", from_column="nitrate", window=6, centre=True)
    with pytest.raises(SimplydataError, match="sorted_by= one column of dates"):
        t.add_rolling_column("r", from_column="nitrate", window="7 days")
    with pytest.raises(SimplydataError, match="different lengths"):
        t.add_rolling_column("r", from_column="nitrate", window="1 month", sorted_by="date")
    with pytest.raises(SimplydataError, match="percent="):
        t.add_rolling_column("r", from_column="nitrate", show="percentile")
    with pytest.raises(SimplydataError, match="two column names"):
        t.add_rolling_column("r", from_column="nitrate", show="correlation")


# ---------------------------------------------------------------- smoothing
@pytest.mark.parametrize("kwargs, positions, expected", [
    # R: stats::filter(x, rep(1/5, 5), sides = 2)[3:4]
    ({"test_method": "moving average"}, [2, 3], [0.52376, 0.73574]),
    # R: zoo::rollapply(x, 5, mean, partial = TRUE)[1:3]
    ({"test_method": "moving average", "ends": "shorter windows"}, [0, 1, 2], [0.1826, 0.4006, 0.52376]),
    # R: w <- c(1, 2, 1); stats::filter(x, w / sum(w), sides = 2)[2:3]
    ({"test_method": "moving average", "weights": [1, 2, 1]}, [1, 2], [0.303, 0.49045]),
    # ends="reflect" is SciPy mode "reflect", the end reading repeated (d c b a | a b c d):
    # R: xr <- c(rev(x[1:2]), x, rev(x[59:60])); stats::filter(xr, rep(1/5, 5), sides = 2)[3:5]
    ({"test_method": "moving average", "ends": "reflect"}, [0, 1, 2], [0.19482, 0.2729, 0.52376]),
    # ends="mirror" is SciPy mode "mirror", the end reading not repeated (d c b | a b c d); before 2026-11-26 it was
    # SciPy "reflect" and gave 0.19482, 0.2729 here, so this row fails on the old mapping:
    # R: xm <- c(rev(x[2:3]), x, rev(x[58:59])); stats::filter(xm, rep(1/5, 5), sides = 2)[c(3:5, 61:62)]
    ({"test_method": "moving average", "ends": "mirror"}, [0, 1, 2, 58, 59], [0.2667, 0.45332, 0.52376, 0.19056,
                                                                              0.2093]),
    # R: signal::sgolayfilt(x, 2, 11)[c(1, 2, 30)]
    ({"test_method": "savitzky-golay", "window": 11}, [0, 1, 29], [0.167486713286713, 0.309181958041956,
                                                               -1.12041235431235]),
    # R: stats::filter(0.3 * x, 0.7, method = "recursive", init = x[1])[c(1, 2, 60)]
    ({"test_method": "exponential"}, [0, 1, 59], [-0.2379, 0.03273, 0.286029719752333]),
    # R: a <- 2 / (9 + 1); stats::filter(a * x, 1 - a, method = "recursive", init = x[1])[60]
    ({"test_method": "exponential", "span": 9}, [59], [0.483183478700769]),
    # R: dnorm(-8:8, sd = 2) weights (scaled to add up to 1) on the mirrored readings (ref_partA.R)
    ({"test_method": "gaussian"}, [0, 1, 2], [0.274174367562221, 0.362412269909438, 0.498816058381256]),
    ({"test_method": "gaussian", "ends": "reflect"}, [0, 1, 2], [0.274174367562221, 0.362412269909438,
                                                                0.498816058381256]),
    # ends="mirror" (SciPy mode "mirror"); before 2026-11-26 gaussian's "mirror" was SciPy "reflect" (the row above):
    # R: w <- dnorm(-8:8, sd = 2); xg <- c(rev(x[2:9]), x, rev(x[52:59])); stats::filter(xg, w / sum(w), sides = 2)[9:11]
    ({"test_method": "gaussian", "ends": "mirror"}, [0, 1, 2], [0.424230122096271, 0.460681197967788,
                                                               0.550571122614385]),
    # R: lowess(seq_along(x), x, f = 2/3)$y[1:3]
    ({"test_method": "lowess"}, [0, 1, 2], [0.986347115509803, 0.947468957834992, 0.907301858393227]),
    # R: solve(diag(60) + 100 * crossprod(diff(diag(60), differences = 2)), x)[1:3]
    pytest.param({"test_method": "whittaker"}, [0, 1, 2], [0.261451335511031, 0.370107044628152, 0.473769240390163],
                 marks=NEEDS_SCIPY_117),
    # R: SciPy's Wiener formula written out (local mean and variance with zero padding; ref_partA.R)
    ({"test_method": "wiener"}, [0, 1, 2], [0.10956, 0.419959808355179, 0.368448620722244]),
])
def test_smoothing_matches_r(kwargs, positions, expected):
    nums = signal60()
    nums.smooth(**kwargs)
    assert np.asarray(nums._values, dtype=float)[positions] == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("ends, expected", [
    ("tukey", [0.6642, 0.6642, 0.6642]),  # R: runmed(x, 5, endrule = "median")[1:3]
    ("keep", [-0.2379, 0.6642, 0.6642]),  # R: runmed(x, 5, endrule = "keep")[1:3]
    ("constant", [0.6642, 0.6642, 0.6642]),  # R: runmed(x, 5, endrule = "constant")[1:3]
])
def test_running_median_runs_r_runmed(ends, expected, needs_r):
    nums = signal60()
    nums.smooth(test_method="median", ends=ends)
    assert np.asarray(nums._values, dtype=float)[:3] == pytest.approx(expected, rel=1e-12)


def test_moving_average_empty_ends_and_undo(capsys):
    nums = signal60()
    nums.smooth()
    values = np.asarray(nums._values, dtype=float)
    assert np.isnan(values[:2]).all() and np.isnan(values[-2:]).all()
    assert "as R stats::filter(x, rep(1 / 5, 5), sides = 2)" in capsys.readouterr().out
    nums.undo()
    assert not np.isnan(np.asarray(nums._values, dtype=float)).any()


def test_add_smoothed_column(engine, capsys):
    t = make(example_frame("sensor"), engine)
    t.add_smoothed_column("smooth", from_column="signal", test_method="savitzky-golay", window=11, sorted_by="time")
    # R: signal::sgolayfilt(x, 2, 11)[c(1, 2, 30)] (the first 60 readings give the same first values)
    assert col(t, "smooth")[[0, 1]] == pytest.approx([0.167486713286713, 0.309181958041956], rel=1e-9)
    assert 'Added "smooth"' in capsys.readouterr().out
    t.undo()
    assert "smooth" not in t._frame.columns
    t.add_smoothed_column(from_column="signal", test_method="savitzky-golay", window=11, sorted_by="time")
    assert 'Added "signal_smoothed"' in capsys.readouterr().out  # the past participle, as "_filtered"


def test_smoothing_errors():
    nums = signal60()
    with pytest.raises(SimplydataError, match="odd whole number"):
        nums.smooth(window=4)
    with pytest.raises(SimplydataError, match="ends"):
        nums.smooth(test_method="savitzky-golay", window=7, ends="empty")
    with pytest.raises(SimplydataError, match="does not take"):
        nums.smooth(test_method="median", of_degree=2)
    with pytest.raises(SimplydataError, match="method"):
        nums.smooth(test_method="kalman")
    with pytest.raises(SimplydataError, match="newest_weight="):
        nums.smooth(test_method="exponential", newest_weight=1.5)


# ---------------------------------------------------------------- remove_trend
def test_remove_trend_matches_r(capsys):
    nums = sdata.numbers(example_frame("sensor")["signal"])
    nums.remove_trend()
    # R: t <- seq_along(xx); residuals(lm(xx ~ t))[1:2]
    assert np.asarray(nums._values, dtype=float)[:2] == pytest.approx([-0.306456172827175, 0.595261418309621],
                                                                       rel=1e-9)
    nums = sdata.numbers(example_frame("sensor")["signal"])
    nums.remove_trend(breaks=[200])
    # R: residuals(lm(xx[1:200] ~ t[1:200]))[1]; residuals(lm(xx[201:1000] ~ t[201:1000]))[1]
    values = np.asarray(nums._values, dtype=float)
    assert [values[0], values[200]] == pytest.approx([-0.464384149253732, -0.0102555964419532], rel=1e-9)
    assert "readings 1 to 200, 201 to 1000" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="breaks="):
        nums.remove_trend(breaks=[1])


# ---------------------------------------------------------------- month ends and time zones
def test_add_missing_dates_keeps_month_ends(engine, capsys):
    import pandas as pd

    # R: seq(as.Date("2023-03-01"), by = "month", length.out = 5) - 1:
    #    "2023-02-28" "2023-03-31" "2023-04-30" "2023-05-31" "2023-06-30"
    data = pd.DataFrame({"date": pd.to_datetime(["2023-02-28", "2023-03-31", "2023-05-31", "2023-06-30"]),
                         "x": [1.0, 2, 3, 4]})
    t = make(data, engine).add_missing_dates("date", every="month")
    got = [str(v)[:10] for v in t._frame["date"].to_list()]
    assert got == ["2023-02-28", "2023-03-31", "2023-04-30", "2023-05-31", "2023-06-30"]
    # a full run of month ends from the 30th: nothing missing; one dropped: one added back
    dates = pd.date_range("2023-04-30", periods=12, freq="ME")
    full = pd.DataFrame({"date": dates, "x": np.arange(12.0)})
    assert len(make(full, engine).add_missing_dates("date")._frame) == 12
    assert len(make(full, engine).add_missing_dates("date", every="month")._frame) == 12
    t = make(full.drop(index=4).reset_index(drop=True), engine).add_missing_dates("date", every="month")
    assert [str(v)[:10] for v in t._frame["date"].to_list()][3:6] == ["2023-07-31", "2023-08-31", "2023-09-30"]
    assert "Added 1 missing month" in capsys.readouterr().out


def test_future_months_stay_month_ends():
    import pandas as pd

    from simplydata._time_axis import future_times, series_of

    data = pd.DataFrame({"date": pd.date_range("2023-04-30", periods=11, freq="ME"), "x": np.arange(11.0)})
    t = make_table(data)  # the last date is 2024-02-29
    s = series_of(t, "x", "date")[0]
    # R: seq(as.Date("2024-03-01"), by = "month", length.out = 3) - 1: "2024-02-29" "2024-03-31" "2024-04-30"
    assert s.unit == "months"
    assert [str(v)[:10] for v in future_times(t, s, "date", 3)] == ["2024-03-31", "2024-04-30", "2024-05-31"]


def test_dates_with_a_time_zone_keep_their_clock(engine, capsys):
    import pandas as pd

    from simplydata._time_axis import series_of

    # daily at midnight in Oslo, across the summer-time change of 2023-03-26 (one day of 23 hours)
    # R: seq(as.POSIXct("2023-03-20", tz = "Europe/Oslo"), by = "DSTday", length.out = 15)
    days = pd.date_range("2023-03-20", periods=15, freq="D", tz="Europe/Oslo")
    data = pd.DataFrame({"date": days, "x": np.sin(np.arange(15.0))})
    s = series_of(make(data, engine), "x", "date")[0]
    assert (s.unit, s.step, s.regular, s.gaps) == ("days", 1.0, True, [])
    assert s.shown_times[:2] == ["2023-03-20", "2023-03-21"]
    make(data, engine).find_autocorrelation_of("x", sorted_by="date", rows_back=3)  # evenly spaced: no error
    gappy = data.drop(index=3).reset_index(drop=True)
    t = make(gappy, engine).add_missing_dates("date", every="day")
    assert len(t._frame) == 15
    t = make(gappy, engine).add_missing_dates("date", between=["2023-03-01", "2023-04-10"])
    assert len(t._frame) == 41  # 1 March to 10 April, Oslo time
    shown = [str(v) for v in t._frame["date"].to_list()]
    assert shown[0].startswith("2023-03-01 00:00:00") and shown[-1].startswith("2023-04-10 00:00:00")
    with pytest.raises(SimplydataError, match="evenly spaced"):
        make(gappy, engine).find_autocorrelation_of("x", sorted_by="date", rows_back=3)
