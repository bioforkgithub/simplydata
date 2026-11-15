"""forecast, compare_forecasts and find_change_points, checked against R.

Every number runs in R itself (simplydata[r]); these tests check that simplydata asks R the right
question and reads the answer back correctly. Reference values: R 4.6.2 with forecast 9.0.2 and
changepoint 2.3, on sdata.example("visitors") and sdata.example("river") (scripts ref_phase3b.R and
ref_phase3b_more.R in the v0.6 scratch folder):
library(forecast); library(changepoint); v <- read.csv("visitors.csv")
h <- v$visitors[v$museum == "Harbour Museum"]; x <- ts(h, frequency = 12)
"""

import datetime

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

ENGINES = ["pandas", "polars"]


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def harbour(engine):
    data = sdata.example("visitors")
    return make(data[data.museum == "Harbour Museum"].reset_index(drop=True), engine)


def col(result, name):
    frame = result._frame
    return np.asarray(frame[name].to_numpy(), dtype=float)


SIMPLE = {
    # R: f <- naive(x, h = 3, level = 95); f$mean; f$lower; f$upper  (and snaive, meanf, rwf(drift = TRUE))
    "last value": ([2072, 2072, 2072], [1746.2729917054, 1611.35244723856, 1507.82427223634],
                   [2397.7270082946, 2532.64755276144, 2636.17572776366]),
    "same season last time": ([1871, 1925, 1930], [1641.66682809997, 1695.66682809997, 1700.66682809997],
                              [2100.33317190003, 2154.33317190003, 2159.33317190003]),
    "average": ([1707.47222222222] * 3, [950.106747750013] * 3, [2464.83769669443] * 3),
    "straight on": ([2079.69230769231, 2087.38461538462, 2095.07692307692],
                    [1752.0310246503, 1622.39539987816, 1523.62337081066],
                    [2407.35359073431, 2552.37383089107, 2666.53047534318]),
}


@pytest.mark.parametrize("method", list(SIMPLE))
def test_simple_methods_match_r_forecast(engine, method, needs_r, capsys):
    result = harbour(engine).forecast("visitors", sorted_by="month", steps_ahead=3, method=method, repeats_every=12)
    mean, low, high = SIMPLE[method]
    assert col(result, "forecast") == pytest.approx(mean, rel=1e-12)
    assert col(result, "forecast 95 % prediction low") == pytest.approx(low, rel=1e-12)
    assert col(result, "forecast 95 % prediction high") == pytest.approx(high, rel=1e-12)
    assert col(result, "steps ahead").tolist() == [1, 2, 3]
    out = capsys.readouterr().out
    assert "for the next 3 months" in out and "95 % prediction interval" in out


def test_holt_winters_matches_r(engine, needs_r, capsys):
    result = harbour(engine).forecast("visitors", sorted_by="month", steps_ahead=3, repeats_every="year")
    # R: hw <- HoltWinters(x); predict(hw, 3, prediction.interval = TRUE, level = 0.95)
    assert col(result, "forecast") == pytest.approx([2016.40937479054, 2012.63214414585, 2024.03137321536], rel=1e-9)
    assert col(result, "forecast 95 % prediction low") == pytest.approx([1886.85026764329, 1882.84434188055, 1894.00328815581], rel=1e-9)
    assert col(result, "forecast 95 % prediction high") == pytest.approx([2145.96848193778, 2142.41994641114, 2154.0594582749], rel=1e-9)
    out = capsys.readouterr().out
    # hw$alpha, hw$beta, hw$gamma = 0.0579006360951824, 0.0266388719662365, 0.285394236048636
    assert "weight on the newest level 0.0579, on the newest trend 0.0266, on the newest season 0.285" in out
    # Box.test(residuals(hw), lag = 24, type = "Ljung-Box"): 27.5022088230553, p 0.281593672667988
    assert "look like noise (Ljung-Box up to 24 rows back, p = 0.282)" in out
    assert "Next month: 2016 (95 % prediction interval 1887 to 2146); in 3 months: 2024" in out
    assert "as R HoltWinters(x)" in out
    dates = result._frame["month"].to_list()
    assert [d.date() if isinstance(d, datetime.datetime) else d for d in dates] == [
        datetime.date(2026, 1, 1), datetime.date(2026, 2, 1), datetime.date(2026, 3, 1)]


def test_holt_winters_model_table_matches_r(engine, needs_r):
    result = harbour(engine).forecast("visitors", sorted_by="month", repeats_every=12, show="model")
    assert result._frame["term"].to_list() == ["alpha", "beta", "gamma", "sum of squared errors"]
    # R: hw$alpha, hw$beta, hw$gamma, hw$SSE
    assert col(result, "estimate") == pytest.approx([0.0579006360951824, 0.0266388719662365, 0.285394236048636,
                                                     574940.572420543], rel=1e-7)


# HoltWinters finds its weights with optim(method = "L-BFGS-B") at its default factr = 1e7: it stops when the sum of
# squared errors falls by less than factr * .Machine$double.eps = 2.2e-9 of itself in one step. The weights, and
# so the forecasts, are fixed only to about that: R on macOS (another BLAS and maths library) lands 1.0e-9 from
# the reference made with R on Windows. rel=1e-8 is that stopping rule with a margin; it is R against R.
HW_OPTIM = 1e-8


def test_holt_winters_options_match_r(needs_r):
    h = harbour("pandas")
    # R: forecast(HoltWinters(x, seasonal = "multiplicative"), h = 2, level = 95)$mean and $lower
    result = h.forecast("visitors", sorted_by="month", steps_ahead=2, repeats_every=12, season="multiplied")
    assert col(result, "forecast") == pytest.approx([1980.58674771702, 1973.67989975173], rel=HW_OPTIM)
    assert col(result, "forecast 95 % prediction low") == pytest.approx([1910.78276783023, 1903.86262108701],
                                                                        rel=HW_OPTIM)
    # R: hn <- HoltWinters(x, gamma = FALSE); predict(hn, 1)
    result = h.forecast("visitors", sorted_by="month", steps_ahead=1)
    assert col(result, "forecast") == pytest.approx([2075.28978383523], rel=HW_OPTIM)
    # R: hb <- HoltWinters(x, beta = FALSE); predict(hb, 1)
    result = h.forecast("visitors", sorted_by="month", steps_ahead=1, repeats_every=12, trend=False)
    assert col(result, "forecast") == pytest.approx([2024.30931513405], rel=HW_OPTIM)


def test_arima_matches_r(engine, needs_r, capsys):
    result = harbour(engine).forecast("visitors", sorted_by="month", steps_ahead=3, method="arima", order=(0, 1, 1),
                                      seasonal_order=(0, 1, 1), repeats_every=12)
    # R: a <- arima(x, order = c(0, 1, 1), seasonal = list(order = c(0, 1, 1), period = 12), method = "ML")
    #    f <- forecast(a, h = 3, level = 95); f$mean; f$lower; f$upper
    assert col(result, "forecast") == pytest.approx([1995.58049209294, 2018.97410069196, 1995.9609580597], rel=1e-7)
    assert col(result, "forecast 95 % prediction low") == pytest.approx([1880.48193325173, 1903.87554185072, 1880.86239921841], rel=1e-7)
    assert col(result, "forecast 95 % prediction high") == pytest.approx([2110.67905093415, 2134.07265953319, 2111.05951690099], rel=1e-7)
    out = capsys.readouterr().out
    assert ("ARIMA(0,1,1)(0,1,1)[12] (1 difference and 1 past error; for the season, 1 difference 12 rows back and "
            "1 past error 12 rows back)") in out
    # Box.test(residuals(f), lag = 24, type = "Ljung-Box", fitdf = 2): p 0.0541912249565278
    assert "p = 0.054" in out


def test_arima_model_table_matches_r(needs_r):
    result = harbour("pandas").forecast("visitors", sorted_by="month", method="arima", order=(0, 1, 1),
                                        seasonal_order=(0, 1, 1), repeats_every=12, show="model")
    assert result._frame["term"].to_list() == ["ma1", "sma1", "sigma^2", "log-likelihood", "AIC"]
    # R: coef(a); sqrt(diag(a$var.coef)); a$sigma2; a$loglik; a$aic
    assert col(result, "estimate") == pytest.approx([-0.999999169571446, -0.954838722143905, 3233.27660856894,
                                                     -731.096265324144, 1468.19253064829], rel=1e-6)
    assert col(result, "standard error")[:2] == pytest.approx([0.0458872691187982, 0.313425797468898], rel=1e-4)


def test_arima_with_an_average_matches_r(needs_r, capsys):
    result = harbour("pandas").forecast("visitors", steps_ahead=2, method="arima", order=(1, 0, 0), interval=80)
    # R: a1 <- arima(x, order = c(1, 0, 0), method = "ML"); f1 <- forecast(a1, h = 2, level = 80)
    assert col(result, "forecast") == pytest.approx([2037.767447691, 2006.55675905573], rel=1e-7)
    assert col(result, "forecast 80 % prediction low") == pytest.approx([1829.12155420741, 1724.20996420578], rel=1e-7)
    assert "with an average" in capsys.readouterr().out


ACCURACY = {
    # R: train <- ts(h[1:132], frequency = 12); test <- h[133:144]
    #    accuracy(naive(train, 12), test)["Test set", c("MAE", "RMSE", "MAPE", "MASE")] (and snaive, rwf drift,
    #    forecast(HoltWinters(train), 12))
    "last value": [348.25, 440.520620024383, 14.682027966278, 2.52243447970806],
    "same season last time": [128.416666666667, 150.282234478996, 5.81359734665399, 0.930143941907184],
    "straight on": [305.181297709924, 404.577946108775, 12.7170580114721, 2.21048048214088],
    "exponential smoothing": [64.6941203640645, 73.9732672243653, 2.93143419760529, 0.468590609736396],
}


def test_check_on_last_matches_r_accuracy(engine, needs_r, capsys):
    result = harbour(engine).forecast("visitors", sorted_by="month", repeats_every=12, check_on_last=12)
    assert len(result._frame) == 12
    assert col(result, "actual")[0] == 1871  # R: h[133]
    assert col(result, "error") == pytest.approx(col(result, "actual") - col(result, "forecast"))
    out = capsys.readouterr().out
    assert "off by 64.7 on average (MAE; RMSE 74.0, MAPE 2.93 %, MASE 0.469" in out


def test_compare_forecasts_matches_r_accuracy(engine, needs_r, capsys):
    result = harbour(engine).compare_forecasts("visitors", sorted_by="month", repeats_every="year")
    frame = result._frame
    assert frame["method"].to_list() == ["exponential smoothing", "same season last time", "straight on",
                                         "last value"]
    assert frame["rank"].to_list() == [1, 2, 3, 4]
    for i, method in enumerate(frame["method"].to_list()):
        got = [col(result, c)[i] for c in ("MAE", "RMSE", "MAPE", "MASE")]
        assert got == pytest.approx(ACCURACY[method], rel=1e-7), method
    out = capsys.readouterr().out
    assert "Best on the last 12 readings of \"visitors\": exponential smoothing (MASE 0.469)" in out
    assert "Below 1 means better than the same season last time." in out


def test_compare_forecasts_without_a_season_matches_r(needs_r, capsys):
    result = harbour("pandas").compare_forecasts("visitors", methods=["average", "last value"])
    # R: y1 <- ts(h[1:132]); accuracy(meanf(y1, 12), h[133:144])["Test set", c("MAE", "RMSE", "MAPE", "MASE")]
    frame = result._frame.to_pandas()
    row = frame[frame["method"] == "average"].iloc[0]
    assert [row["MAE"], row["RMSE"], row["MAPE"], row["MASE"]] == pytest.approx(
        [524.484848484848, 589.80056837616, 22.8537670284506, 3.79893371400615], rel=1e-9)
    assert "better than the last value" in capsys.readouterr().out


def test_forecast_for_each_group(engine, needs_r):
    result = make(sdata.example("visitors"), engine).forecast("visitors", sorted_by="month", steps_ahead=2,
                                                              method="last value", for_each="museum")
    assert result._frame["museum"].to_list() == ["Harbour Museum"] * 2 + ["Hill Gallery"] * 2
    assert col(result, "forecast")[:2] == pytest.approx([2072, 2072])


def test_nums_forecast_matches_r(needs_r, capsys):
    nums = sdata.numbers(sdata.example("visitors")["visitors"][:144])
    result = nums.forecast(steps_ahead=3, method="same season last time", repeats_every=12)
    assert col(result, "forecast") == pytest.approx([1871, 1925, 1930])  # R snaive(x, h = 3)$mean
    assert "for the next 3 steps" in capsys.readouterr().out


def test_forecast_errors(engine):
    h = harbour(engine)
    with pytest.raises(SimplydataError, match="needs order="):
        h.forecast("visitors", sorted_by="month", method="arima")
    with pytest.raises(SimplydataError, match='for method="arima"'):
        h.forecast("visitors", sorted_by="month", order=(0, 1, 1))
    with pytest.raises(SimplydataError, match="needs repeats_every="):
        h.forecast("visitors", sorted_by="month", method="same season last time")
    with pytest.raises(SimplydataError, match='season="multiplied" is for'):
        h.forecast("visitors", sorted_by="month", method="naive", season="multiplied")
    with pytest.raises(SimplydataError, match="steps_ahead="):
        h.forecast("visitors", sorted_by="month", steps_ahead=0)
    with pytest.raises(SimplydataError, match="interval="):
        h.forecast("visitors", sorted_by="month", interval=0.95)
    with pytest.raises(SimplydataError, match='show="model"'):
        h.forecast("visitors", sorted_by="month", method="naive", show="model")
    with pytest.raises(SimplydataError, match="three whole numbers"):
        h.forecast("visitors", sorted_by="month", method="arima", order=(0, 1))
    with pytest.raises(SimplydataError, match="method"):
        h.forecast("visitors", sorted_by="month", method="crystal ball")
    with pytest.raises(SimplydataError, match="too few readings"):
        h.forecast("visitors", sorted_by="month", check_on_last=142)
    with pytest.raises(SimplydataError, match="at least two methods"):
        h.compare_forecasts("visitors", sorted_by="month", methods=["naive"])
    river = make(sdata.example("river"), engine)
    with pytest.raises(SimplydataError, match="evenly spaced"):
        river.forecast("nitrate", sorted_by="date", for_each="station")


# ---------------------------------------------------------------- change points
def test_change_points_match_r(needs_r, capsys):
    y = np.concatenate([np.full(40, 10.0), np.full(40, 14.0), np.full(40, 9.0)]) + np.sin(np.arange(1, 121)) * 1.5
    result = make_table({"y": y}).find_change_points("y")
    # R: cm <- cpt.mean(y / (mad(diff(y)) / sqrt(2)), method = "PELT", penalty = "MBIC"); cpts(cm) = 40, 80
    assert result._frame["from"].to_list() == [1, 41, 81]
    assert result._frame["to"].to_list() == [40, 80, 120]
    # R: mean(y[1:40]), mean(y[41:80]), mean(y[81:120])
    assert col(result, "average") == pytest.approx([10.0711829277848, 13.9482919765078, 8.99778917013476], rel=1e-12)
    out = capsys.readouterr().out
    assert '"y" changes twice: the average is 10.1 up to reading 40, then 13.9 from 41 to 80, then 9.00 from ' \
           "reading 81 on." in out
    # R: cpts(cpt.meanvar(y, method = "PELT", penalty = "MBIC")) = 40, 80
    result = make_table({"y": y}).find_change_points("y", change="average and spread")
    assert result._frame["to"].to_list() == [40, 80, 120]
    # R: cpts(cpt.mean(y / s, method = "PELT", penalty = "AIC")) = 40, 80
    assert make_table({"y": y}).find_change_points("y", penalty="aic")._frame["to"].to_list() == [40, 80, 120]


def test_change_points_on_river_match_r(engine, needs_r, capsys):
    result = make(sdata.example("river"), engine).find_change_points("nitrate", sorted_by="date", for_each="station")
    frame = result._frame
    assert frame["station"].to_list() == ["Station A", "Station B", "Station B"]
    # R: xb <- r$nitrate[r$station == "Station B"]; cpts(cpt.mean(xb / (mad(diff(xb)) / sqrt(2)), ...)) = 453
    assert frame["readings"].to_list() == [725, 453, 269]
    # R: mean(xa); mean(xb[1:453]); mean(xb[454:722]); sd(xb[1:453])
    assert col(result, "average") == pytest.approx([3.28507586206897, 4.13068432671082, 2.67237918215613], rel=1e-12)
    assert col(result, "standard deviation")[1] == pytest.approx(0.338655226623319, rel=1e-12)
    out = capsys.readouterr().out
    assert '"nitrate" for Station A has no change point' in out
    assert '"nitrate" for Station B changes once: the average is 4.13 up to 2025-03-31, then 2.67 from 2025-04-01 on.' \
           in out


def test_change_point_errors(engine):
    river = make(sdata.example("river"), engine)
    with pytest.raises(SimplydataError, match="change"):
        river.find_change_points("nitrate", change="slope")
    with pytest.raises(SimplydataError, match="penalty"):
        river.find_change_points("nitrate", penalty="big")
    with pytest.raises(SimplydataError, match="empty cell"):
        river.find_change_points("level", sorted_by="date", for_each="station")


def test_straight_on_other_spellings(needs_r):
    from simplydata import _forecast

    assert _forecast.read_method("drift", "forecast") == "straight on"
    assert _forecast.read_method("line from first to last", "forecast") == "straight on"
