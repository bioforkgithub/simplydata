"""add_trend_and_season, trend_of and correlation_between(rows_back=), checked against R.

Reference values: R 4.6.2 with trend 1.1.6, on example_frame("visitors") (ref_phase3a.R):
v <- read.csv("visitors.csv"); h <- v$visitors[v$museum == "Harbour Museum"];
g <- v$visitors[v$museum == "Hill Gallery"].
"""

import math

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


def visitors(engine, museum=None):
    data = example_frame("visitors")
    if museum:
        data = data[data.museum == museum].reset_index(drop=True)
    return make(data, engine)


def frame(t):
    return t._frame.to_pandas() if hasattr(t._frame, "to_pandas") else t._frame


def col(t, name, museum="Harbour Museum"):
    f = frame(t)
    return f.loc[f.museum == museum, name].to_numpy(float)


# ---------------------------------------------------------------------------- correlation_between(rows_back=)
def test_cross_correlation_matches_r_ccf_with_the_lag_reversed(capsys):
    data = example_frame("visitors")
    wide = data.pivot(index="month", columns="museum", values="visitors").reset_index()
    wide.columns = ["month", "harbour", "hill"]
    got = make_table(wide).find_correlation_between("harbour", "hill", rows_back=3, sorted_by="month")
    f = frame(got)
    # R: ccf(h, g, lag.max = 3)$acf at lags -3..3; simplydata's shift s is R's lag -s
    r_acf = [0.434739164289954, 0.653354037125857, 0.871730623387588, 0.967973221586085, 0.871092745815142,
             0.655695904824905, 0.417135952261636]
    assert f["shift"].tolist() == [-3, -2, -1, 0, 1, 2, 3]
    assert np.allclose(f["correlation"].to_numpy(), r_acf[::-1], atol=1e-12)
    out = capsys.readouterr().out
    assert "go together best in the same row (r = 0.968)" in out and "ccf(harbour, hill, lag.max = 3)" in out


def test_cross_correlation_finds_which_column_follows(capsys):
    t = make_table(sdata.get_example("sensor"))
    got = frame(t.find_correlation_between("signal", "vibration", rows_back=8, sorted_by="time"))
    assert int(got.loc[got["correlation"].abs().idxmax(), "shift"]) == 6  # vibration is the signal 0.03 s later
    assert '"vibration" follows "signal" by 6 rows' in capsys.readouterr().out


def test_cross_correlation_errors():
    t = make_table(sdata.get_example("sensor"))
    with pytest.raises(SimplydataError, match="exactly two columns"):
        t.find_correlation_between("signal", "vibration", "time", rows_back=3)
    with pytest.raises(SimplydataError, match="give rows_back="):
        t.find_correlation_between("signal", "vibration", sorted_by="time")
    with pytest.raises(SimplydataError, match="rows_back="):
        t.find_correlation_between("signal", "vibration", rows_back=0, sorted_by="time")


# ---------------------------------------------------------------------------- add_trend_and_season
def test_loess_matches_r_stl(engine, capsys):
    t = visitors(engine)
    t.add_trend_and_season("visitors", sorted_by="month", repeats_every="year", for_each_group_in="museum")
    # R: s <- stl(ts(h, frequency = 12), s.window = 7)
    assert np.allclose(col(t, "visitors_trend")[:3], [1202.9668398627, 1212.05091158329, 1221.13498330388],
                       rtol=1e-11)
    assert col(t, "visitors_season")[:3] == pytest.approx([-253.174595139275, -159.883487216769,
                                                           -234.842294017948], rel=1e-10)
    assert col(t, "visitors_rest")[143] == pytest.approx(26.9481612210457, rel=1e-9)
    trend, season, rest = (col(t, n) for n in ("visitors_trend", "visitors_season", "visitors_rest"))
    assert np.allclose(trend + season + rest, col(t, "visitors"))
    out = capsys.readouterr().out
    assert "stl(ts(x, frequency = 12), s.window = 7)" in out and "for Hill Gallery" in out
    t.undo()
    assert "visitors_trend" not in t.get_column_names()


def test_robust_loess_matches_r(engine):
    t = visitors(engine, "Harbour Museum")
    t.add_trend_and_season("visitors", sorted_by="month", repeats_every=12, robust=True)
    # R: stl(ts(h, frequency = 12), s.window = 7, robust = TRUE)
    assert col(t, "visitors_trend")[0] == pytest.approx(1192.13066673084, rel=1e-10)
    assert col(t, "visitors_season")[0] == pytest.approx(-203.73227850781, rel=1e-10)


def test_fixed_season_runs_r_stl_periodic(needs_r):
    t = visitors("pandas", "Harbour Museum")
    t.add_trend_and_season("visitors", sorted_by="month", repeats_every="year", season_window="fixed")
    # R: stl(ts(h, frequency = 12), s.window = "periodic")
    assert col(t, "visitors_trend")[0] == pytest.approx(1200.80656372679, rel=1e-12)
    assert col(t, "visitors_season")[:2] == pytest.approx([-213.739681096364, -196.0601930421], rel=1e-12)


def test_moving_averages_match_r_decompose(engine):
    t = visitors(engine, "Harbour Museum")
    t.add_trend_and_season("visitors", sorted_by="month", repeats_every="year", test_method="moving averages")
    # R: d <- decompose(ts(h, frequency = 12))
    trend = col(t, "visitors_trend")
    assert np.isnan(trend[:6]).all() and np.isnan(trend[-6:]).all()  # the first and last half cycle
    assert trend[6:8] == pytest.approx([1255.04166666667, 1260.66666666667], rel=1e-12)
    assert col(t, "visitors_season")[:2] == pytest.approx([-210.465909090909, -198.174242424242], rel=1e-12)
    assert col(t, "visitors_rest")[6] == pytest.approx(16.1590909090908, rel=1e-10)


def test_multiplied_season_matches_r(engine, capsys):
    t = visitors(engine, "Harbour Museum")
    t.add_trend_and_season("visitors", sorted_by="month", repeats_every=12, test_method="classical", season="multiplied")
    # R: decompose(ts(h, frequency = 12), type = "multiplicative")
    assert col(t, "visitors_season")[:2] == pytest.approx([0.870849298029537, 0.884153172499437], rel=1e-12)
    assert col(t, "visitors_rest")[6] == pytest.approx(1.07328577149643, rel=1e-12)
    assert "The season multiplies visitors by" in capsys.readouterr().out


def test_straight_line_matches_r_lm_with_season_effects(engine):
    t = visitors(engine, "Harbour Museum")
    t.add_trend_and_season("visitors", sorted_by="month", repeats_every=12, test_method="straight line")
    # R: tt <- seq_along(h); p <- factor((tt - 1) %% 12)
    #    fit <- lm(h ~ tt + p, contrasts = list(p = "contr.sum")); trend <- coef(fit)[1] + coef(fit)[2] * tt
    #    season <- fitted(fit) - trend; residuals(fit)
    assert col(t, "visitors_trend")[:2] == pytest.approx([1214.21180555556, 1221.1105526418], rel=1e-12)
    assert col(t, "visitors_season")[:3] == pytest.approx([-212.779113247873, -194.177860334112,
                                                           -225.909940753692], rel=1e-10)
    assert col(t, "visitors_rest")[0] == pytest.approx(-29.4326923076835, rel=1e-9)


def test_trend_and_season_errors(engine):
    t = visitors(engine)
    with pytest.raises(SimplydataError, match="repeats_every="):
        t.add_trend_and_season("visitors", sorted_by="month", for_each_group_in="museum")
    with pytest.raises(SimplydataError, match='"year" for months'):
        make_table(sdata.get_example("sensor")).add_trend_and_season("signal", sorted_by="time", repeats_every="year")
    with pytest.raises(SimplydataError, match="take the log first"):
        t.add_trend_and_season("visitors", sorted_by="month", repeats_every=12, season="multiplied",
                               for_each_group_in="museum")
    with pytest.raises(SimplydataError, match="season_window="):
        t.add_trend_and_season("visitors", sorted_by="month", repeats_every=12, season_window=8, for_each_group_in="museum")
    with pytest.raises(SimplydataError, match="method"):
        t.add_trend_and_season("visitors", sorted_by="month", repeats_every=12, test_method="wavelet", for_each_group_in="museum")
    with pytest.raises(SimplydataError, match="already a column"):
        t.add_trend_and_season("visitors", sorted_by="month", repeats_every=12, for_each_group_in="museum",
                               names=["visitors", "b", "c"])


# ---------------------------------------------------------------------------- trend_of
def test_trend_of_matches_r_trend(engine, capsys, needs_r):
    got = frame(visitors(engine).find_trend_of("visitors", sorted_by="month", for_each_group_in="museum"))
    h = got[got.museum == "Harbour Museum"].iloc[0]
    # R: sens.slope(h): 6.95454545454545 (6.27058823529412 to 7.63636363636364);
    # mk.test(h): z 10.2461062428422, p 1.23207287687804e-24, S 5933, tau 0.576439188052974
    assert h["slope"] == pytest.approx(6.95454545454545, rel=1e-12)
    assert (h["95 % CI low"], h["95 % CI high"]) == pytest.approx((6.27058823529412, 7.63636363636364), rel=1e-12)
    assert h["slope per year"] == pytest.approx(12 * 6.95454545454545)
    assert h["z"] == pytest.approx(10.2461062428422, rel=1e-12)
    assert h["p-value"] == pytest.approx(1.23207287687804e-24, rel=1e-9)
    assert (h["S"], h["Kendall's tau"]) == pytest.approx((5933, 0.576439188052974), rel=1e-12)
    g = got[got.museum == "Hill Gallery"].iloc[0]
    assert g["slope"] == pytest.approx(2.53846153846154, rel=1e-12)  # sens.slope(g)
    assert g["z"] == pytest.approx(9.16848748755386, rel=1e-12)  # mk.test(g)
    out = capsys.readouterr().out
    assert '"visitors" for Harbour Museum rises by 6.95 per month (83.5 a year)' in out
    assert "trend::mk.test()" in out


def test_seasonal_trend_matches_r(needs_r, capsys):
    got = frame(visitors("pandas", "Harbour Museum").find_trend_of("visitors", sorted_by="month", repeats_every="year"))
    # R: smk.test(ts(h, frequency = 12)): z 14.8493018022435, p 7.02969721839593e-50; sea.sens.slope: 83.6090909090909
    assert got["z"].iloc[0] == pytest.approx(14.8493018022435, rel=1e-12)
    assert got["p-value"].iloc[0] == pytest.approx(7.02969721839593e-50, rel=1e-9)
    assert got["slope"].iloc[0] == pytest.approx(83.6090909090909, rel=1e-12)
    assert "seasonal Mann-Kendall" in capsys.readouterr().out


def test_trend_of_without_r_still_gives_the_slope(capsys, monkeypatch):
    from simplydata import _r

    monkeypatch.setattr(_r, "_STATE", {"error": "no R", "missing": "rpy2"})
    got = frame(visitors("pandas", "Harbour Museum").find_trend_of("visitors", sorted_by="month"))
    assert got["slope"].iloc[0] == pytest.approx(6.95454545454545, rel=1e-12)
    assert math.isnan(got["p-value"].iloc[0])
    out = capsys.readouterr().out
    assert "Mann-Kendall test was left out" in out and 'pip install "simplydata[r]"' in out


# ---------------------------------------------------------------------------- trend_of on the real times
def test_trend_of_weekly_and_gappy_dates_are_per_day(engine, capsys):
    import pandas as pd

    # weekly readings: Sen's slope per day, from the dates themselves
    x = np.arange(40.0) + np.sin(np.arange(40)) * 0.1
    weekly = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=40, freq="7D"), "x": x})
    got = frame(make(weekly, engine).find_trend_of("x", sorted_by="date"))
    # R: s <- trend::sens.slope(x); s$estimates / 7 (readings 7 days apart): 0.142841912115012;
    #    s$conf.int / 7: 0.142508586766307, 0.143104050105662
    assert got["slope"].iloc[0] == pytest.approx(0.142841912115012, rel=1e-12)
    assert (got["95 % CI low"].iloc[0], got["95 % CI high"].iloc[0]) == pytest.approx(
        (0.142508586766307, 0.143104050105662), rel=1e-12)
    assert got["slope per year"].iloc[0] == pytest.approx(0.142841912115012 * 365.25, rel=1e-12)
    assert '"x" rises by 0.143 per day (52.2 a year)' in capsys.readouterr().out
    # month ends with one month missing: the slope comes from the days between the dates
    monthly = pd.DataFrame({"date": pd.date_range("2020-01-31", periods=40, freq="ME"), "x": np.arange(40.0)})
    monthly = monthly.drop(index=5).reset_index(drop=True)
    got = frame(make(monthly, engine).find_trend_of("x", sorted_by="date"))
    # R (Sen's slope by hand on the dates, as SciPy theilslopes(x, t)):
    #    d <- seq(as.Date("2020-02-01"), by = "month", length.out = 40) - 1; x <- 0:39; d <- d[-6]; x <- x[-6]
    #    t <- as.numeric(d - d[1]); i <- combn(length(x), 2)
    #    median((x[i[2, ]] - x[i[1, ]]) / (t[i[2, ]] - t[i[1, ]])): 0.0328697850821745
    assert got["slope"].iloc[0] == pytest.approx(0.0328697850821745, rel=1e-12)
    assert "per day (12.0 a year)" in capsys.readouterr().out


def test_seasonal_trend_is_per_year_and_needs_even_steps(capsys, needs_r):
    import pandas as pd

    got = frame(visitors("pandas", "Harbour Museum").find_trend_of("visitors", sorted_by="month", repeats_every="year"))
    # R: sea.sens.slope(ts(h, frequency = 12)) = 83.6090909090909, the change from one year to the next
    assert got["slope per year"].iloc[0] == pytest.approx(83.6090909090909, rel=1e-12)
    assert '"visitors" rises by 83.6 per year (seasonal Sen\'s slope)' in capsys.readouterr().out
    gappy = pd.DataFrame({"date": pd.date_range("2020-01-31", periods=40, freq="ME"), "x": np.arange(40.0)})
    gappy = gappy.drop(index=5).reset_index(drop=True)
    with pytest.raises(SimplydataError, match="evenly spaced"):
        make(gappy, "pandas").find_trend_of("x", sorted_by="date", repeats_every=12)
