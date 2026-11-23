"""Time series, cycles, waves and systems (phase U3, batch 7): the same work in SciPy signal, statsmodels and R.

Smoothing, trend and season, autocorrelation, the steady check, change points, forecasts, peaks and dips, spectra,
frequency filters, the envelope, the Fourier transform, convolution, resampling, waves and windows, and the linear
systems of sdata.system (SciPy signal.lti and its friends). The words that run R (the steady check, change points
and forecasts) show the R code simplydata runs; the chart words draw the same sticks, dots, lines and cells with
matplotlib.
"""

from . import Entry

SENSOR = 'df = pd.read_csv("sensor.csv").sort_values("time")'
HARBOUR = """
    import pandas as pd
    visitors_table = pd.read_csv("visitors.csv", parse_dates=["month"])
    harbour = visitors_table[visitors_table["museum"] == "Harbour Museum"].sort_values("month")
    x = harbour["visitors"].to_numpy(dtype=float)
"""
SIGNAL = """
    import pandas as pd
    x = pd.read_csv("sensor.csv").sort_values("time")["signal"].to_numpy(dtype=float)
"""
STEP_UP = """
    import numpy as np
    x = np.array([1.02, 0.97, 1.01, 1.04, 0.98, 1.00, 0.96, 1.03, 0.99, 1.01,
                  1.41, 1.38, 1.43, 1.37, 1.40, 1.44, 1.39, 1.42, 1.36, 1.40])
"""
SYSTEM_ALSO = "simplydata also prints the formula, the poles and whether the system is stable."

ENTRIES = [
    # ------------------------------------------------------------------ smoothing and trend
    Entry(
        word="nums.smooth",
        ours="""
            nums = sdata.numbers([3, 5, 4, 30, 6, 7, 5, 8, 6, 9])
            nums.smooth()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import ndimage
            x = np.array([3, 5, 4, 30, 6, 7, 5, 8, 6, 9], dtype=float)
            # smooth()
            out = ndimage.convolve1d(x, np.ones(5) / 5, mode="reflect")   # (1)
            out[:2] = np.nan                                             # (2)
            out[-2:] = np.nan
            out
        """},
        compare="value",
        tolerance=1e-12,
        choices=("a moving average of 5 readings centred on each one (window=5); the weights add up to 1.",
                 "the first and last 2 readings have no full window, so they are left empty, as R stats::filter(x, "
                 "rep(1 / 5, 5), sides = 2) (ends=\"empty\"; \"shorter windows\" and \"mirror\" fill them).",),
        also="test_method= offers a running median (R runmed itself), Savitzky-Golay, exponential, Gaussian, lowess, "
             "loess, spline, Whittaker and Wiener smoothing. simplydata also says which method it used and the R "
             "call that gives the same numbers, and remembers the step for nums.undo().",
    ),
    Entry(
        word="nums.remove_trend",
        ours="""
            nums = sdata.numbers([2, 4, 3, 7, 6, 9, 8, 12])
            nums.remove_trend()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import signal
            x = np.array([2, 4, 3, 7, 6, 9, 8, 12], dtype=float)
            # remove_trend()
            signal.detrend(x, type="linear")     # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the least-squares straight line through the readings, one step apart, is taken away, as R "
                 "residuals(lm(x ~ seq_along(x))); test_method=\"average\" takes away the average only.",),
        also="breaks= fits a separate straight line to each piece (SciPy detrend's bp=). simplydata also says what "
             "it took away.",
    ),
    Entry(
        word="table.add_trend_and_season",
        data="visitors",
        ours="""
            table = sdata.get_example("visitors")
            table.keep_rows_where("museum", is_equal_to="Harbour Museum")
            table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year")
        """,
        code={"statsmodels": """
            import pandas as pd
            from statsmodels.tsa.seasonal import STL
            df = pd.read_csv("visitors.csv", parse_dates=["month"])
            df = df[df["museum"] == "Harbour Museum"].sort_values("month")
            # add_trend_and_season("visitors", sorted_by="month", repeats_every="year")
            stl = STL(df["visitors"].to_numpy(dtype=float), period=12,  # (1)
                      seasonal=7, trend=23, low_pass=13, seasonal_deg=0,
                      seasonal_jump=1, trend_jump=3, low_pass_jump=2)    # (2)
            fit = stl.fit(inner_iter=2, outer_iter=0)                    # (3)
            df.assign(visitors_trend=fit.trend, visitors_season=fit.seasonal,
                      visitors_rest=fit.resid)
        """},
        compare="table",
        tolerance=1e-9,
        choices=("repeats_every=\"year\" with monthly readings is a cycle of 12 readings.",
                 "R stl()'s settings: a season window of 7 cycles (season_window=), a season of degree 0, and R's "
                 "trend span (23), low-pass span (13) and jumps worked out from the cycle; statsmodels' own defaults "
                 "differ and give other numbers.",
                 "2 inner passes and no robustness passes, as R stl(robust = FALSE) (robust=True: 1 and 15).",),
        also="trend + season + rest = the column. test_method=\"moving averages\" (R decompose: statsmodels "
             "seasonal_decompose) and \"straight line\" (R lm) are the other methods; season_window=\"fixed\" runs R "
             "stl(s.window = \"periodic\") itself. simplydata also checks the readings are evenly spaced and says "
             "how far the season moves the column.",
    ),
    # ------------------------------------------------------------------ autocorrelation, steady, change points
    Entry(
        word="nums.find_autocorrelation",
        data="sensor",
        ours="""
            nums = sdata.get_example("sensor").get_column("signal")
            nums.find_autocorrelation()
        """,
        code={"statsmodels": """
            import numpy as np, pandas as pd
            from scipy import stats
            from statsmodels.stats.diagnostic import acorr_ljungbox
            from statsmodels.tsa.stattools import acf
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # find_autocorrelation()
            k = int(np.floor(10 * np.log10(len(x))))               # (1)
            r = acf(x, nlags=k, adjusted=False, fft=False)[1:]     # (2)
            half = stats.norm.ppf(0.975) / np.sqrt(len(x))         # (3)
            box = acorr_ljungbox(x, lags=[k])
            pd.DataFrame({"rows back": np.arange(1, k + 1), "correlation": r, "band low": -half,
                          "band high": half, "outside band": np.where(abs(r) > half, "yes", "no"),
                          "Ljung-Box statistic": box["lb_stat"].iloc[0], "Ljung-Box p-value": box["lb_pvalue"].iloc[0]})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("rows back 1 to 10 x log10(n), as R acf's lag.max (30 for 1,000 readings).",
                 "each correlation divides by n, not by the number of pairs, as R acf (adjusted=False).",
                 "the band is +/- qnorm(0.975) / sqrt(n), the dashed lines of R plot.acf; the Ljung-Box test runs up "
                 "to the last rows back.",),
        also="show=\"partial\" (statsmodels pacf with method=\"ywm\", as R pacf) and band=\"bartlett\" are the other "
             "options. simplydata also says where the column is most like itself and how many correlations lie "
             "outside the band.",
    ),
    Entry(
        word="table.check_steady_over_time",
        data="sensor",
        ours="""
            table = sdata.get_example("sensor")
            table.check_steady_over_time("signal", sorted_by="time")
        """,
        code={
            "R": """
                # check_steady_over_time("signal", sorted_by="time"): the ADF row
                lags <- trunc((length(x) - 1)^(1/3))                                    # (1)
                u <- urca::ur.df(x, type = "drift", lags = lags, selectlags = "Fixed")  # (2)
                stat <- unname(u@teststat[1])
                p <- urca::punitroot(stat, N = length(u@res), trend = "c", statistic = "t")   # (3)
                k <- tseries::kpss.test(x, null = "Level")   # the KPSS row
                list(stat = stat, lags = lags, p = p)
            """,
            "Python": """
                {"statistic": stat, "rows back": lags, "p-value": p}
            """,
        },
        r_inputs=SIGNAL,
        r_packages=("urca", "tseries"),
        compare="result",
        fields=("statistic", "rows back", "p-value"),
        tolerance=1e-9,
        choices=("trunc((n - 1)^(1/3)) rows back in the test regression, the rule of tseries::adf.test.",
                 "around=\"level\" asks about one steady level, so the Dickey-Fuller regression has a constant and no "
                 "trend (urca type = \"drift\"): tseries::adf.test always allows a trend, so a column that rises "
                 "steadily would pass it as steady.",
                 "MacKinnon's p-value (urca::punitroot), with N the number of rows in the test regression.",),
        python_note="statsmodels adfuller and kpss are similar, but their p-values come from other tables, so the tests "
                    "come from R.",
        also="The KPSS test (tseries::kpss.test(null = \"Level\")) gives the second row. around=\"straight line\" runs "
             "tseries::adf.test and kpss.test(null = \"Trend\"). simplydata also reads the two tests together "
             "(steady, wanders or they disagree) and says when a p-value lies past the end of the published table.",
    ),
    Entry(
        word="table.find_change_points_in",
        ours="""
            table = sdata.table({"reading": [1.02, 0.97, 1.01, 1.04, 0.98, 1.00, 0.96, 1.03, 0.99, 1.01,
                                             1.41, 1.38, 1.43, 1.37, 1.40, 1.44, 1.39, 1.42, 1.36, 1.40]})
            table.find_change_points_in("reading")
        """,
        code={
            "R": """
                # find_change_points_in("reading"), the 20 readings in table order
                s <- stats::mad(diff(x)) / sqrt(2)                                     # (1)
                found <- changepoint::cpt.mean(x / s, method = "PELT", penalty = "MBIC")  # (2)
                ends <- c(changepoint::cpts(found), length(x))
                starts <- c(1, ends[-length(ends)] + 1)
                piece <- function(f) sapply(seq_along(starts), function(i) f(x[starts[i]:ends[i]]))
                list(starts = starts, ends = ends, average = piece(mean), spread = piece(stats::sd))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"piece": range(1, len(starts) + 1), "from": starts, "to": ends,
                              "readings": ends - starts + 1, "average": average,
                              "standard deviation": spread})
            """,
        },
        r_inputs=STEP_UP,
        r_packages=("changepoint",),
        compare="table",
        tolerance=1e-9,
        choices=("the readings are divided by the noise size s = mad(diff(x)) / sqrt(2) first: cpt.mean assumes noise "
                 "with a standard deviation of 1, and changepoint itself does not scale. Taking s from the "
                 "differences between neighbours keeps the jumps from inflating it. This is simplydata's own choice.",
                 "the PELT search with R's own MBIC penalty (penalty=\"bic\", \"aic\" or \"hannan-quinn\" instead).",),
        python_note="Python has no package that gives changepoint's PELT search with its penalties, so the search runs "
                    "in R.",
        also="change=\"average and spread\" runs cpt.meanvar. With sorted_by= the pieces start and end at its values. "
             "simplydata also says where the average jumps, in a sentence.",
    ),
]

ENTRIES += [
    # ------------------------------------------------------------------ forecasts (R)
    Entry(
        word="nums.forecast",
        data="visitors",
        ours="""
            nums = sdata.get_example("visitors").keep_rows_by_position(1, to=144).get_column("visitors")
            nums.forecast(steps_ahead=12, repeats_every=12)
        """,
        code={
            "R": """
                # forecast(steps_ahead=12, repeats_every=12)
                fit <- stats::HoltWinters(stats::ts(x, frequency = 12), seasonal = "additive")   # (1)
                f <- forecast::forecast(fit, h = 12, level = 95)                                # (2)
                list(mean = as.numeric(f$mean), low = as.numeric(f$lower), high = as.numeric(f$upper))
            """,
            "Python": """
                import numpy as np, pandas as pd
                pd.DataFrame({"steps ahead": np.arange(1, 13), "forecast": mean,
                              "forecast 95 % prediction low": low, "forecast 95 % prediction high": high,
                              "method": "exponential smoothing"})
            """,
        },
        r_inputs="""
            import pandas as pd
            x = pd.read_csv("visitors.csv", parse_dates=["month"])["visitors"].to_numpy(dtype=float)[:144]
        """,
        r_packages=("forecast",),
        compare="table",
        tolerance=1e-9,
        choices=("test_method=\"exponential smoothing\" is Holt-Winters as R stats::HoltWinters fits it: a level, a "
                 "trend and a season that is added (trend=True, season=\"added\"), the weights chosen by R.",
                 "95 % prediction intervals (interval=95), from forecast::forecast.",),
        python_note="statsmodels ExponentialSmoothing updates the season in another order and gives other numbers, so "
                    "the forecast comes from R.",
        also="The other methods are \"last value\", \"same season last time\", \"average\", \"straight on\" (R "
             "forecast::naive, snaive, meanf, rwf(drift = TRUE)) and \"arima\". simplydata also checks the leftover "
             "errors with the Ljung-Box test and says the first and last forecast in a sentence.",
    ),
    Entry(
        word="table.compare_forecasts_for",
        data="visitors",
        ours="""
            table = sdata.get_example("visitors")
            table.keep_rows_where("museum", is_equal_to="Harbour Museum")
            table.compare_forecasts_for("visitors", sorted_by="month", repeats_every="year")
        """,
        code={
            "R": """
                # compare_forecasts_for("visitors", sorted_by="month", repeats_every="year")
                y <- stats::ts(x[1:(length(x) - 12)], frequency = 12)          # (1)
                test <- x[(length(x) - 11):length(x)]
                fs <- list(forecast::naive(y, h = 12), forecast::snaive(y, h = 12),
                           forecast::rwf(y, h = 12, drift = TRUE),
                           forecast::forecast(stats::HoltWinters(y), h = 12))
                a <- sapply(fs, function(f) forecast::accuracy(f, stats::ts(test, frequency = 12,     # (2)
                    start = stats::tsp(f$mean)[1]))["Test set", c("MAE", "RMSE", "MAPE", "MASE")])
                list(mae = a[1, ], rmse = a[2, ], mape = a[3, ], mase = a[4, ])
            """,
            "Python": """
                import pandas as pd
                r = pd.DataFrame({"method": ["last value", "same season last time", "straight on",
                                             "exponential smoothing"],
                                  "MAE": mae, "RMSE": rmse, "MAPE": mape, "MASE": mase})
                r = r.sort_values("MASE", kind="stable")                      # (3)
                r.assign(rank=range(1, 5))
            """,
        },
        r_inputs=HARBOUR,
        r_packages=("forecast",),
        compare="table",
        tolerance=1e-9,
        choices=("each method is fitted on all but the last 12 readings (check_on_last=12) and forecasts them.",
                 "the held-back readings are given to forecast::accuracy as a series with 12 readings a cycle, so MASE "
                 "divides the average error by that of the same season last time inside the fitted readings (the last "
                 "value without repeats_every=); given as plain numbers, accuracy would scale by the last value.",
                 "the methods are ranked by MASE, best first.",),
        python_note="statsmodels has the methods but not R's intervals and accuracy measures, so every forecast and "
                    "error comes from R forecast.",
        also="test_method= picks the methods (at least two; \"arima\" with order=, or order=\"automatic\" for "
             "auto.arima). simplydata also names the best method in a sentence.",
    ),
    # ------------------------------------------------------------------ peaks and dips
    Entry(
        word="nums.find_each_peak_that",
        ours="""
            nums = sdata.numbers([0, 2, 1, 3, 3, 1, 5, 0, 4, 1])
            nums.find_each_peak_that(is_at_least=2)
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            x = np.array([0, 2, 1, 3, 3, 1, 5, 0, 4, 1], dtype=float)
            # find_each_peak_that(is_at_least=2)
            peaks, _ = signal.find_peaks(x, height=2)
            prom, left, right = signal.peak_prominences(x, peaks)
            width = signal.peak_widths(x, peaks, rel_height=0.5,
                                       prominence_data=(prom, left, right))[0]   # (1)
            pd.DataFrame({"position": peaks + 1, "value": x[peaks], "stands out by": prom,
                          "width": width, "left base": left + 1, "right base": right + 1})   # (2)
        """},
        compare="table",
        tolerance=1e-12,
        choices=("each peak's width is measured halfway down its prominence: SciPy peak_widths(rel_height=0.5), as "
                 "MATLAB findpeaks(\"WidthReference\", \"halfprom\"); in readings (in units of time with time_step=).",
                 "positions and bases count from 1.",),
        also="A flat top (3, 3) counts once, at its middle, as SciPy does. apart=, stands_out_by= and wide_at_least= "
             "are SciPy's distance=, prominence= and width=. simplydata also says how many peaks it found and which "
             "is highest.",
    ),
    Entry(
        word="nums.find_each_dip_that",
        ours="""
            nums = sdata.numbers([5, 2, 4, 1, 6, 3, 3, 7, 0, 4])
            nums.find_each_dip_that(is_at_most=2)
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            x = np.array([5, 2, 4, 1, 6, 3, 3, 7, 0, 4], dtype=float)
            # find_each_dip_that(is_at_most=2)
            dips, _ = signal.find_peaks(-x, height=-2)                    # (1)
            prom, left, right = signal.peak_prominences(-x, dips)
            width = signal.peak_widths(-x, dips, rel_height=0.5, prominence_data=(prom, left, right))[0]
            pd.DataFrame({"position": dips + 1, "value": x[dips], "stands out by": prom,
                          "width": width, "left base": left + 1, "right base": right + 1})   # (2)
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the dips are the peaks of minus the numbers, so is_at_most=2 becomes SciPy's height=-2 (as R "
                 "pracma::findpeaks(-x) for dips without flat bottoms); widths are measured halfway down.",
                 "positions and bases count from 1; the value is the number itself, not minus it.",),
        also="simplydata also says how many dips it found and which is lowest.",
    ),
    Entry(
        word="table.find_each_dip_that",
        data="sensor",
        ours="""
            table = sdata.get_example("sensor")
            table.find_each_dip_that("signal", sorted_by="time", is_at_most=-1, apart=0.035)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            df = pd.read_csv("sensor.csv").sort_values("time")
            # find_each_dip_that("signal", sorted_by="time", is_at_most=-1, apart=0.035)
            y, step = -df["signal"].to_numpy(), 0.005                       # (1)
            dips, _ = signal.find_peaks(y, height=1, distance=round(0.035 / step, 9))   # (2)
            prom, left, right = signal.peak_prominences(y, dips)
            width = signal.peak_widths(y, dips, rel_height=0.5, prominence_data=(prom, left, right))[0]
            pd.DataFrame({"position": dips + 1, "time": df["time"].to_numpy()[dips],
                          "value": -y[dips], "stands out by": prom, "width": width * step,
                          "left base": left + 1, "right base": right + 1})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the dips are the peaks of minus the readings: is_at_most=-1 becomes SciPy's height=1.",
                 "apart= is in units of sorted_by, so it becomes a number of readings (0.035 / 0.005 = 7). simplydata "
                 "rounds it to 9 decimals first: in floating point it is 7.000000000000001, which SciPy rounds up "
                 "to 8 readings, and 3 of the dips here would be lost.",),
        also="Widths are in units of sorted_by and positions count from 1, as in find_each_peak_that. Empty cells are "
             "never dips. simplydata also says how many dips it found and which is lowest.",
    ),
    # ------------------------------------------------------------------ spectra
    Entry(
        word="table.find_spectrum_of",
        data="sensor",
        ours="""
            table = sdata.get_example("sensor")
            table.find_spectrum_of("signal", sorted_by="time")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            df = pd.read_csv("sensor.csv").sort_values("time")
            y = df["signal"].to_numpy()
            # find_spectrum_of("signal", sorted_by="time")
            f, p = signal.periodogram(y, fs=1 / 0.005, detrend="constant",          # (1)
                                      window="boxcar", scaling="density")       # (2)
            with np.errstate(divide="ignore"):
                every = 1 / f
            pd.DataFrame({"frequency": f, "repeats every": every, "power": p})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("sorted_by=\"time\" gives the time between readings (0.005), so the frequencies are per second.",
                 "the periodogram as SciPy makes it: the average taken away, no taper, one-sided and scaled so that "
                 "power x frequency step adds up to the variance; that is 2 x R spec.pgram(x, taper = 0, detrend = "
                 "FALSE, fast = FALSE)$spec at every frequency but the top one.",),
        also="test_method=\"welch\" (SciPy welch, pieces with half overlap) and \"lomb-scargle\" (R lomb::lsp itself, "
             "for uneven times) are the other methods. simplydata also names the 3 strongest cycles.",
    ),
    Entry(
        word="nums.find_spectrum",
        data="sensor",
        ours="""
            nums = sdata.get_example("sensor").get_column("signal")
            nums.find_spectrum()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy()
            # find_spectrum()
            f, p = signal.periodogram(x, fs=1.0, detrend="constant", window="boxcar",   # (1)
                                      scaling="density")                            # (2)
            with np.errstate(divide="ignore"):
                every = 1 / f
            pd.DataFrame({"frequency": f, "repeats every": every, "power": p})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("without time_step= the readings are one step apart, so the frequencies are cycles per reading.",
                 "the one-sided periodogram, scaled so that power x frequency step adds up to the variance (2 x R "
                 "spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)$spec, except at the top frequency).",),
        also="time_step= (or sampling_rate=) gives frequencies per unit of time; show=\"decibels\" or \"amplitude\" "
             "changes the column. simplydata also names the 3 strongest cycles.",
    ),
    # ------------------------------------------------------------------ filters and the envelope
    Entry(
        word="nums.keep_each_frequency_that",
        data="sensor",
        ours="""
            nums = sdata.get_example("sensor").get_column("signal")
            nums.keep_each_frequency_that(is_below=10, time_step=0.005)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # keep_each_frequency_that(is_below=10, time_step=0.005)
            sos = signal.butter(4, 10, btype="lowpass", output="sos", fs=1 / 0.005)   # (1)
            signal.sosfiltfilt(sos, x)                                               # (2)
        """},
        compare="value",
        tolerance=1e-9,
        choices=("a Butterworth filter of steepness 4 (the filter order), made as second-order sections so it stays "
                 "stable; as R signal::butter(4, 10 / 100).",
                 "run forwards and backwards (both_ways=True), so nothing moves in time; the ends follow SciPy (odd "
                 "reflection, steady start, as MATLAB filtfilt), which differs from R signal::filtfilt near the ends.",),
        also="test_method=\"chebyshev\", \"chebyshev 2\", \"elliptic\" and \"bessel\" are the other designs; "
             "both_ways=False runs it forwards only (sosfilt). simplydata also says what it kept.",
    ),
    Entry(
        word="nums.remove_each_frequency_that",
        data="sensor",
        ours="""
            nums = sdata.get_example("sensor").get_column("signal")
            nums.remove_each_frequency_that(is_equal_to=50, time_step=0.005)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # remove_each_frequency_that(is_equal_to=50, time_step=0.005)
            b, a = signal.iirnotch(50, 50 / 1, fs=1 / 0.005)   # (1)
            signal.filtfilt(b, a, x)                           # (2)
        """},
        compare="value",
        tolerance=1e-9,
        choices=("one frequency is removed by a notch filter whose width is 1 (width=1), so its quality factor is "
                 "50 / 1.",
                 "run forwards and backwards (both_ways=True), so nothing moves in time.",),
        also="and_multiples=True also removes 100, 150 ... (SciPy iircomb with pass_zero=False), and that comb also "
             "removes frequency 0, the average of the numbers. is_between= removes a band. simplydata also says what "
             "it removed.",
    ),
    Entry(
        word="table.add_filtered_column",
        data="sensor",
        ours="""
            table = sdata.get_example("sensor")
            table.sort_by("signal")              # the rows out of time order
            table.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            df = pd.read_csv("sensor.csv").sort_values("signal", kind="stable")
            # add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")
            in_time = df.sort_values("time")                                    # (1)
            sos = signal.butter(4, 10, btype="lowpass", output="sos", fs=1 / 0.005)   # (2)
            slow = signal.sosfiltfilt(sos, in_time["signal"].to_numpy(dtype=float))   # (3)
            df.assign(slow=pd.Series(slow, index=in_time.index))   # back to each row
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the readings are filtered in order of sorted_by=\"time\", whatever the order of the rows, and the time "
                 "between them (0.005 seconds) makes keep_below=10 mean 10 cycles per second; each row keeps its "
                 "own filtered value.",
                 "a Butterworth filter of steepness 4, as second-order sections (R signal::butter(4, 10 / 100)).",
                 "run forwards and backwards (both_ways=True), so nothing moves in time.",),
        also="keep_above=, keep_between=, remove_between= and remove_at= are the other conditions; for_each_group_in= "
             "filters each group on its own. simplydata also checks the readings are evenly spaced and filled in.",
    ),
    Entry(
        word="sdata.frequency_filter",
        ours="""
            system = sdata.frequency_filter(keep_below=10, time_step=0.005)
            system.table()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # frequency_filter(keep_below=10, time_step=0.005)
            sos = signal.butter(4, 10, btype="lowpass", output="sos", fs=1 / 0.005)   # (1)
            b, a = signal.sos2tf(sos)                                                # (2)
            pd.DataFrame({"power of z": np.arange(4, -1, -1), "numerator": b, "denominator": a})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the filter of add_filtered_column(keep_below=10): Butterworth, steepness 4, as second-order "
                 "sections.",
                 "its formula in z comes from the sections (sos2tf), highest power first (system.table() shows it).",),
        also="The System runs the sections themselves (sosfilt, sosfreqz), which is more exact than the formula. "
             "simplydata also prints the formula, the poles and the R call that makes the same filter.",
    ),
    Entry(
        word="nums.find_envelope",
        data="sensor",
        ours="""
            nums = sdata.get_example("sensor").get_column("signal")
            nums.find_envelope()
        """,
        code={"SciPy": """
            import pandas as pd
            import numpy as np
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # find_envelope()
            np.abs(signal.hilbert(x))
        """},
        compare="value",
        tolerance=1e-9,
        also="show=\"phase\" (degrees, unwrapped) and \"frequency\" are the other columns of the analytic signal. "
             "SciPy signal.hilbert gives R gsignal::hilbert's numbers; simplydata also says what it worked out.",
    ),
    Entry(
        word="table.add_envelope_column",
        data="sensor",
        ours="""
            table = sdata.get_example("sensor")
            table.sort_by("signal")              # the rows out of time order
            table.add_envelope_column("signal_envelope", from_column="signal", sorted_by="time")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            df = pd.read_csv("sensor.csv").sort_values("signal", kind="stable")
            # add_envelope_column("signal_envelope", from_column="signal", sorted_by="time")
            in_time = df.sort_values("time")
            z = signal.hilbert(in_time["signal"].to_numpy(dtype=float))    # (1)
            df.assign(signal_envelope=pd.Series(np.abs(z), index=in_time.index))
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the envelope is the size of the analytic signal from the Hilbert transform, worked out on the "
                 "readings in order of sorted_by=, whatever the order of the rows; each row keeps its own value.",),
        also="show=\"phase\" and \"frequency\" are the other choices; for_each_group_in= works on each group. "
             "simplydata also checks the readings are evenly spaced and filled in.",
    ),
    # ------------------------------------------------------------------ Fourier, convolution, resampling
    Entry(
        word="nums.take_fourier_transform",
        ours="""
            nums = sdata.numbers([1, 3, 2, 5, 4, 6, 5, 8])
            nums.take_fourier_transform(time_step=0.5)
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import fft
            x = np.array([1, 3, 2, 5, 4, 6, 5, 8], dtype=float)
            # take_fourier_transform(time_step=0.5)
            z, f = fft.rfft(x), fft.rfftfreq(len(x), d=0.5)          # (1)
            pd.DataFrame({"frequency": f, "size": np.abs(z),
                          "phase": np.degrees(np.angle(z)),          # (2)
                          "real part": z.real, "imaginary part": z.imag})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("show=\"half\": the frequencies from 0 up to the highest the readings can show (rfft); show=\"all\" "
                 "gives every frequency, negative ones too (fft).",
                 "the phase is in degrees, as R Arg(fft(x)) * 180 / pi.",),
        also="simplydata also says where the biggest size lies and remembers what sdata.find_inverse_fourier_transform "
             "needs to turn the table back into the numbers.",
    ),
    Entry(
        word="sdata.find_inverse_fourier_transform",
        ours="""
            nums = sdata.numbers([1, 3, 2, 5, 4])
            table = nums.take_fourier_transform()
            sdata.find_inverse_fourier_transform(table)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import fft
            x = np.array([1, 3, 2, 5, 4], dtype=float)
            z = fft.rfft(x)
            # find_inverse_fourier_transform(table)
            fft.irfft(z, n=len(x))      # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the number of readings is remembered from the transform: an odd count (5) cannot be told from the "
                 "half spectrum, and irfft's own default would give 4 numbers.",),
        also="A table of show=\"all\" goes back with ifft. simplydata also says how many numbers came back.",
    ),
    Entry(
        word="nums.convolve_with",
        ours="""
            nums = sdata.numbers([1, 2, 3])
            nums.convolve_with([1, 2, 1])
        """,
        code={"SciPy": """
            from scipy import signal
            # convolve_with([1, 2, 1])
            signal.convolve([1, 2, 3], [1, 2, 1], mode="full")   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("keep=\"all\": every overlap, n + m - 1 numbers, as R convolve(x, rev(y), type = \"open\"); \"same\" "
                 "keeps the middle n, \"overlap\" only full overlaps.",),
        also="simplydata also says how many numbers came out and remembers the step for nums.undo().",
    ),
    Entry(
        word="nums.deconvolve_by",
        ours="""
            nums = sdata.numbers([0, 1, 2.5, 4, 1.5])
            nums.deconvolve_by([1, 2, 3])
        """,
        code={"SciPy": """
            from scipy import signal
            # deconvolve_by([1, 2, 3])
            quotient, remainder = signal.deconvolve([0, 1, 2.5, 4, 1.5], [1, 2, 3])
            quotient
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also prints the size of the remainder, as R pracma::deconv gives it.",
    ),
    Entry(
        word="nums.change_time_step",
        data="sensor",
        ours="""
            nums = sdata.get_example("sensor").get_column("signal")
            nums.change_time_step(to=0.01, time_step=0.005)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # change_time_step(to=0.01, time_step=0.005)
            n_new = round(len(x) * 0.005 / 0.01)     # (1)
            signal.resample(x, n_new)                # (2)
        """},
        compare="value",
        tolerance=1e-9,
        choices=("the new number of readings fills the same time: n x old step / new step (1,000 readings become "
                 "500).",
                 "test_method=\"fourier\": SciPy resample, which treats the recording as repeating; \"polyphase\" "
                 "(resample_poly) and \"filter then keep\" (decimate) are the other methods.",),
        also="simplydata also remembers the new time step and says when it cannot be exact.",
    ),
    Entry(
        word="sdata.make_wave",
        ours="""
            sdata.make_wave("square", frequency=5, time_step=0.01, how_many=100)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import signal
            # make_wave("square", frequency=5, time_step=0.01, how_many=100)
            t = np.arange(100) * 0.01                              # (1)
            signal.square(2 * np.pi * 5 * t, duty=0.5)             # (2)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the times start at 0 and go up by time_step=.",
                 "a square wave is high (1) for half of each cycle (high_share=0.5) and low (-1) for the rest.",),
        also="The other shapes are \"sine\", \"sawtooth\", \"chirp\", \"pulse\" and \"impulse\" (SciPy sawtooth, chirp, "
             "gausspulse, unit_impulse). simplydata also remembers the time step in the numbers.",
    ),
    Entry(
        word="sdata.make_window_shape",
        ours="""
            sdata.make_window_shape("hann", how_many=64)
        """,
        code={"SciPy": """
            from scipy import signal
            # make_window_shape("hann", how_many=64)
            signal.get_window("hann", 64, fftbins=False)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the symmetric window (as R gsignal::hann and NumPy hanning); SciPy get_window's own default is the "
                 "periodic one used inside spectra (periodic=True).",),
        also="Any SciPy window name works, such as \"hamming\", \"blackman\" or (\"kaiser\", 5). simplydata also says "
             "which window it made.",
    ),
    # ------------------------------------------------------------------ systems
    Entry(
        word="sdata.system",
        ours="""
            system = sdata.system("2 / (2*s**2 + 4*s + 10)")
            system.table()
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            # the system "2 / (2*s**2 + 4*s + 10)"
            lti = signal.lti([2], [2, 4, 10])                    # (1)
            pd.DataFrame({"power of s": [2, 1, 0], "numerator": [0, 0, *lti.num],
                          "denominator": lti.den})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the coefficients are divided by the first one of the bottom, so it is 1, as SciPy's TransferFunction "
                 "keeps them (1 / (s**2 + 2*s + 5)).",),
        also="The formula is read with Python's ast (it is never run) and turned into polynomials with NumPy; "
             "numerator=, denominator=, poles=, zeros= and a=, b=, c=, d= are the other ways in. " + SYSTEM_ALSO,
    ),
    Entry(
        word="system.step_response",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            system.step_response(until=10)
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            lti = signal.lti([1], [1, 2, 5])
            # step_response(until=10)
            t, y = signal.step(lti, T=np.linspace(0, 10, 200))   # (1)
            pd.DataFrame({"time": t, "output": y})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("200 times, evenly spaced from 0 to until= (how_many=200).",),
        also="simplydata also prints the final value, peak, overshoot, rise time and settling time (python-control "
             "step_info on these times, with simplydata[systems]).",
    ),
    Entry(
        word="system.impulse_response",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            system.impulse_response(until=10)
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            lti = signal.lti([1], [1, 2, 5])
            # impulse_response(until=10)
            t, y = signal.impulse(lti, T=np.linspace(0, 10, 200))   # (1)
            pd.DataFrame({"time": t, "output": y})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("200 times, evenly spaced from 0 to until= (how_many=200).",),
        also="simplydata also says where the output is biggest and where it ends.",
    ),
    Entry(
        word="system.response_to",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            system.response_to(sdata.make_wave("square", frequency=0.2, time_step=0.05, how_many=400))
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            lti = signal.lti([1], [1, 2, 5])
            t = np.arange(400) * 0.05                     # (1)
            u = signal.square(2 * np.pi * 0.2 * t)
            # response_to(the square wave)
            y = signal.lsim(lti, u, t, interp=False)[1]   # (2)
            pd.DataFrame({"time": t, "input": u, "output": y})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the times come from the time step the input numbers remember (0.05), starting at 0.",
                 "the system starts at rest and each input value holds until the next time (interp=False, a zero "
                 "order hold), as R control::lsim; SciPy's own default joins the inputs by straight lines.",),
        also="simplydata also says where the output ends and its biggest size.",
    ),
    Entry(
        word="system.frequency_response",
        ours="""
            system = sdata.system("1 / (s + 1)**3")
            system.frequency_response(between=[0.1, 100])
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            lti = signal.lti([1], [1, 3, 3, 1])
            # frequency_response(between=[0.1, 100])
            w, h = signal.freqresp(lti, w=np.logspace(-1, 2, 200))     # (1)
            pd.DataFrame({"frequency": w, "gain": np.abs(h), "gain (decibels)": 20 * np.log10(np.abs(h)),
                          "phase (degrees)": np.degrees(np.unwrap(np.angle(h)))})   # (2)
        """},
        compare="table",
        tolerance=1e-9,
        choices=("200 frequencies spaced evenly on a log scale, in radians per second (unit=).",
                 "the phase is unwrapped, so it runs on past -180 degrees (to -270 here) without jumping back to +180.",),
        also="simplydata also prints the gain and phase margins (python-control stability_margins, with "
             "simplydata[systems]).",
    ),
    Entry(
        word="system.poles",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            system.poles()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # poles()
            p = signal.lti([1], [1, 2, 5]).poles
            pd.DataFrame({"real part": p.real, "imaginary part": p.imag, "distance from 0": np.abs(p),
                          "damping ratio": -p.real / np.abs(p),       # (1)
                          "natural frequency": np.abs(p)})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the damping ratio and natural frequency of each pole, as R control::damp (for a system in steps "
                 "worked out from log(pole) / time step).",),
        also="simplydata also lists the poles in a sentence.",
    ),
    Entry(
        word="system.zeros",
        ours="""
            system = sdata.system("(s + 1) / (s**2 + 2*s + 5)")
            system.zeros()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # zeros()
            z = signal.lti([1, 1], [1, 2, 5]).zeros
            pd.DataFrame({"real part": z.real, "imaginary part": z.imag, "distance from 0": np.abs(z),
                          "damping ratio": -z.real / np.abs(z), "natural frequency": np.abs(z)})
        """},
        compare="table",
        tolerance=1e-12,
        also="The table has the columns of poles(). simplydata also lists the zeros in a sentence.",
    ),
    Entry(
        word="system.is_stable",
        ours="""
            system = sdata.system("1 / (s**2 + 4)")
            system.is_stable()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import signal
            # is_stable()
            bool(np.all(signal.lti([1], [1, 0, 4]).poles.real < -1e-12))   # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("stable means every pole has a real part below 0 (inside the unit circle in steps); poles on the edge, "
                 "such as +/- 2i here, are not stable, because the output never settles.",),
        also="simplydata also says why a system is not stable.",
    ),
    Entry(
        word="system.steady_gain",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            system.steady_gain()
        """,
        code={"NumPy": """
            import numpy as np
            # steady_gain()
            np.polyval([1], 0) / np.polyval([1, 2, 5], 0)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the formula at s = 0 (z = 1 in steps), as R control::dcgain.",),
        also="simplydata also says when the output never settles there (a system that is not stable, or a pole at "
             "s = 0).",
    ),
    Entry(
        word="system.in_steps",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            in_steps = system.in_steps(time_step=0.1)
            in_steps.table()
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            # in_steps(time_step=0.1)
            num, den, _ = signal.cont2discrete(([1], [1, 2, 5]), 0.1, method="zoh")   # (1)
            pd.DataFrame({"power of z": [2, 1, 0], "numerator": num.ravel(), "denominator": den})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("test_method=\"zero order hold\": the input stays constant between steps, as R control::c2d(sys, 0.1).",),
        also="\"bilinear\", \"forward difference\" and \"backward difference\" are the other methods. simplydata also "
             "prints the formula in z.",
    ),
    Entry(
        word="system.then",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            joined = system.then(sdata.system("1 / s"))
            joined.table()
        """,
        code={"NumPy": """
            import numpy as np, pandas as pd
            # then(the system 1 / s)
            num = np.polymul([1], [1])                # (1)
            den = np.polymul([1, 2, 5], [1, 0])
            pd.DataFrame({"power of s": [3, 2, 1, 0], "numerator": [0, 0, 0, *num], "denominator": den})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("in series the formulas multiply, top by top and bottom by bottom, as R control::series.",),
        also="simplydata also prints the joined formula.",
    ),
    Entry(
        word="system.add",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            joined = system.add(sdata.system("1 / (s + 3)"))
            joined.table()
        """,
        code={"NumPy": """
            import numpy as np, pandas as pd
            # add(the system 1 / (s + 3))
            num = np.polyadd(np.polymul([1], [1, 3]), np.polymul([1], [1, 2, 5]))   # (1)
            den = np.polymul([1, 2, 5], [1, 3])
            pd.DataFrame({"power of s": [3, 2, 1, 0], "numerator": [0, *num], "denominator": den})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("side by side the outputs add, so the formulas add over a common bottom, as R control::parallel.",),
        also="simplydata also prints the joined formula.",
    ),
    Entry(
        word="system.with_feedback",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            loop = system.with_feedback()
            loop.table()
        """,
        code={"NumPy": """
            import numpy as np, pandas as pd
            # with_feedback()
            g_num, g_den = [1], [1, 2, 5]
            h_num, h_den = [1], [1]                   # the feedback path: the output itself
            num = np.polymul(g_num, h_den)
            den = np.polyadd(np.polymul(g_den, h_den), np.polymul(g_num, h_num))   # (1)
            pd.DataFrame({"power of s": [2, 1, 0], "numerator": [0, 0, *num], "denominator": den})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("negative feedback through 1 (the output itself): G / (1 + G), as R control::feedback(sys, 1); "
                 "sign=\"positive\" gives G / (1 - G).",),
        also="through= puts another system in the feedback path. simplydata also prints the closed-loop formula.",
    ),
    Entry(
        word="system.table",
        ours="""
            system = sdata.system("(s + 1) / (s**2 + 2*s + 5)")
            system.table()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            lti = signal.lti([1, 1], [1, 2, 5])
            # table()
            top = np.concatenate([np.zeros(len(lti.den) - len(lti.num)), lti.num])   # (1)
            pd.DataFrame({"power of s": [2, 1, 0], "numerator": top, "denominator": lti.den})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("form=\"transfer function\": one row per power, highest first, with the top padded with zeros to the "
                 "length of the bottom.",),
        also="form=\"state space\" (SciPy tf2ss, as R control::tf2ss) and \"poles and zeros\" (tf2zpk) are the other "
             "forms.",
    ),
]

ENTRIES += [
    # ------------------------------------------------------------------ chart words
    Entry(
        word="autocorrelation_bars",
        data="visitors",
        ours="""
            table = sdata.get_example("visitors")
            table.keep_rows_where("museum", is_equal_to="Harbour Museum")
            chart = table.start_chart()
            chart.autocorrelation_bars("visitors", sorted_by="month")
        """,
        code={"matplotlib": """
            import pandas as pd
            import numpy as np, matplotlib.pyplot as plt
            from statsmodels.tsa.stattools import acf
            df = pd.read_csv("visitors.csv", parse_dates=["month"])
            y = df[df["museum"] == "Harbour Museum"].sort_values("month")["visitors"]
            # autocorrelation_bars("visitors", sorted_by="month")
            k = int(np.floor(10 * np.log10(len(y))))                       # (1)
            lags, r = np.arange(1, k + 1), acf(y, nlags=k, adjusted=False, fft=False)[1:]
            half = np.full(k, 1.959963984540054 / np.sqrt(len(y)))        # (2)
            fig, ax = plt.subplots()
            ax.vlines(lags, 0, r); ax.plot(lags, r, "o")
            ax.step(lags, -half, where="mid", linestyle="--"); ax.step(lags, half, where="mid", linestyle="--")
            ax.axhline(0); ax.set_xlabel("rows back"); ax.set_ylabel("correlation")
        """},
        compare="chart",
        check=("lines", "labels", "limits"),
        tolerance=1e-9,
        choices=("rows back 1 to 10 x log10(n), as R acf (21 for 144 months); each correlation divides by n.",
                 "the dashed band is +/- qnorm(0.975) / sqrt(n), as the dashed lines of R plot(acf(x)).",),
        also="The heights are the numbers of table.find_autocorrelation_of (show=\"partial\" and band=\"bartlett\" "
             "work here too). " + "simplydata also gives the chart its paper look (fonts, colours, no top and right "
             "lines); that is left out here.",
    ),
    Entry(
        word="cross_correlation_bars",
        data="sensor",
        ours="""
            chart = sdata.chart(sdata.get_example("sensor"))
            chart.cross_correlation_bars("signal", "vibration", sorted_by="time", rows_back=20)
        """,
        code={"matplotlib": """
            import pandas as pd
            import numpy as np, matplotlib.pyplot as plt
            from statsmodels.tsa.stattools import ccf
            df = pd.read_csv("sensor.csv").sort_values("time")
            a, b = df["signal"], df["vibration"]
            # cross_correlation_bars("signal", "vibration", sorted_by="time", rows_back=20)
            later, earlier = ccf(b, a, adjusted=False, fft=False)[:21], ccf(a, b, adjusted=False, fft=False)[:21]
            s, r = np.arange(-20, 21), np.concatenate([earlier[1:][::-1], later])   # (1)
            half = np.full(41, 1.959963984540054 / np.sqrt(len(a)))                # (2)
            fig, ax = plt.subplots()
            ax.vlines(s, 0, r); ax.plot(s, r, "o")
            ax.step(s, -half, where="mid", linestyle="--"); ax.step(s, half, where="mid", linestyle="--")
            ax.axhline(0); ax.set_xlabel("shift"); ax.set_ylabel("correlation")
        """},
        compare="chart",
        check=("lines", "labels", "limits"),
        tolerance=1e-9,
        choices=("a stick at shift s pairs the first column at row t with the second at row t + s (R ccf's lag -s), "
                 "so a high stick at shift 6 means the second follows the first 6 rows later.",
                 "the dashed band is +/- qnorm(0.975) / sqrt(n), as R plot(ccf(a, b)).",),
        also="The heights are the numbers of table.find_correlation_between(rows_back=). simplydata also gives the "
             "chart its paper look; that is left out here.",
    ),
    Entry(
        word="lag_dots",
        data="visitors",
        ours="""
            table = sdata.get_example("visitors")
            table.keep_rows_where("museum", is_equal_to="Harbour Museum")
            chart = table.start_chart()
            chart.lag_dots("visitors", sorted_by="month", rows_back=[1, 12])
        """,
        code={"matplotlib": """
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("visitors.csv", parse_dates=["month"])
            y = df[df["museum"] == "Harbour Museum"].sort_values("month")["visitors"].reset_index(drop=True)
            fig, ax = plt.subplots()
            # lag_dots("visitors", sorted_by="month", rows_back=[1, 12])
            for k, label in ((1, "1 row back"), (12, "12 rows back")):
                ax.scatter(y.shift(k)[k:], y[k:], label=label)          # (1)
            ax.plot([y.min(), y.max()], [y.min(), y.max()], "--")      # (2)
            ax.set_xlabel("visitors, rows back"); ax.set_ylabel("visitors"); ax.legend()
        """},
        compare="chart",
        check=("dots", "dot_colour_groups", "lines", "labels", "legend"),
        tolerance=1e-12,
        choices=("each value against the value k rows earlier, in the order of sorted_by=; the first k rows have no "
                 "partner and are left out. Each rows_back= gets its own colour.",
                 "the dashed 1:1 line runs from the smallest to the biggest value shown, as R lag.plot(diag = TRUE).",),
        also="transparency= makes the dots see-through. simplydata also gives the chart its paper look; that is left "
             "out here.",
    ),
    Entry(
        word="peak_dots",
        data="sensor",
        ours="""
            chart = sdata.chart(sdata.get_example("sensor"))
            chart.draw_lines(x="time", y="signal")
            chart.peak_dots(is_at_least=1, apart=0.035)
        """,
        code={"matplotlib": """
            import pandas as pd
            import matplotlib.pyplot as plt
            from scipy import signal
            df = pd.read_csv("sensor.csv").sort_values("time")
            t, y = df["time"].to_numpy(), df["signal"].to_numpy()
            fig, ax = plt.subplots()
            ax.plot(t, y)
            # peak_dots(is_at_least=1, apart=0.035)
            peaks, _ = signal.find_peaks(y, height=1, distance=round(0.035 / 0.005, 9))   # (1)
            ax.scatter(t[peaks], y[peaks], marker="^")
        """},
        compare="chart",
        check=("dots", "lines"),
        tolerance=1e-12,
        choices=("the peaks of table.find_each_peak_that: apart= is in units of x, so 0.035 / 0.005 = 7 readings, "
                 "rounded to 9 decimals first (in floating point it is 7.000000000000001, which SciPy would round up "
                 "to 8 and lose 3 peaks).",),
        also="dips=True marks the dips instead (is_at_most=). simplydata also gives the chart its paper look; that is "
             "left out here.",
    ),
    Entry(
        word="spectrum",
        data="sensor",
        ours="""
            chart = sdata.chart(sdata.get_example("sensor"))
            chart.spectrum("signal", sorted_by="time")
        """,
        code={"matplotlib": """
            import pandas as pd
            import numpy as np, matplotlib.pyplot as plt
            from scipy import signal
            y = pd.read_csv("sensor.csv").sort_values("time")["signal"].to_numpy()
            # spectrum("signal", sorted_by="time")
            f, p = signal.periodogram(y, fs=1 / 0.005, detrend="constant", window="boxcar", scaling="density")  # (1)
            fig, ax = plt.subplots()
            ax.plot(f[1:], p[1:])                                         # (2)
            for i in np.argsort(-p[1:], kind="stable")[:3] + 1:            # (3)
                ax.annotate(f"repeats every {1 / f[i]:.3g}", (f[i], p[i]))
            ax.set_yscale("log"); ax.set_xlabel("frequency"); ax.set_ylabel("power")
        """},
        compare="chart",
        check=("lines", "scales", "labels", "texts"),
        tolerance=1e-9,
        choices=("the periodogram of table.find_spectrum_of: one-sided, no taper, scaled so the powers add up to the "
                 "variance; the time step (0.005) gives frequencies per second.",
                 "frequency 0 (the average) is left out, and the power is on a log scale (log_scale=True).",
                 "the 3 frequencies with the biggest powers (frequency 0 left out) are labelled with how often they repeat; "
                 "they can be neighbours on one peak.",),
        also="test_method=\"welch\" or \"lomb-scargle\" and show=\"decibels\" or \"amplitude\" work here too. "
             "simplydata also gives the chart its paper look; that is left out here.",
    ),
    Entry(
        word="spectrum_over_time",
        data="sensor",
        ours="""
            chart = sdata.chart(sdata.get_example("sensor"))
            chart.spectrum_over_time("signal", sorted_by="time", window=100)
        """,
        code={"matplotlib": """
            import pandas as pd
            import numpy as np, matplotlib.pyplot as plt
            from scipy import signal
            df = pd.read_csv("sensor.csv").sort_values("time")
            # spectrum_over_time("signal", sorted_by="time", window=100)
            f, t, p = signal.spectrogram(df["signal"].to_numpy(), fs=1 / 0.005, window="hann",   # (1)
                                         nperseg=100, noverlap=50, detrend="constant")      # (2)
            fig, ax = plt.subplots()
            mesh = ax.pcolormesh(t + df["time"].iloc[0], f, 10 * np.log10(p), shading="nearest",
                                 cmap="viridis")                                             # (3)
            fig.colorbar(mesh, ax=ax, label="power (decibels)")
            ax.set_xlabel("time"); ax.set_ylabel("frequency")
        """},
        compare="chart",
        check=("cells", "labels", "limits"),
        tolerance=1e-9,
        choices=("pieces of window=100 readings with a Hann window (window_shape=), each with its own periodogram.",
                 "the pieces overlap by half and each piece's average is taken away first.",
                 "the power is shown in decibels (10 x log10), on viridis colours; each piece sits at its middle "
                 "time.",),
        also="simplydata also checks the readings are evenly spaced and filled in, and gives the chart its paper "
             "look; that is left out here.",
    ),
]

ENTRIES += [
    Entry(
        word="trend_and_season",
        data="visitors",
        ours="""
            table = sdata.get_example("visitors")
            table.keep_rows_where("museum", is_equal_to="Harbour Museum")
            chart = table.start_chart()
            chart.trend_and_season(x="month", y="visitors", repeats_every="year")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt, pandas as pd
            from statsmodels.tsa.seasonal import STL
            df = pd.read_csv("visitors.csv", parse_dates=["month"])
            df = df[df["museum"] == "Harbour Museum"].sort_values("month")
            # trend_and_season(x="month", y="visitors", repeats_every="year")
            fit = STL(df["visitors"].to_numpy(dtype=float), period=12, seasonal=7, trend=23, low_pass=13,
                      seasonal_deg=0, seasonal_jump=1, trend_jump=3, low_pass_jump=2).fit(inner_iter=2, outer_iter=0)  # (1)
            fig, ax = plt.subplots(); ax.set_axis_off()
            panels, parts = [], [fit.observed, fit.trend, fit.seasonal, fit.resid]
            for i, name in enumerate(["visitors", "trend", "season", "rest"]):
                panels.append(ax.inset_axes([0, 0.77 - 0.25 * i, 1, 0.21], sharex=panels[0] if panels else None))
                panels[-1].set_ylabel(name)                                                        # (2)
                if i == 3: panels[-1].vlines(df["month"], 0, parts[i]); panels[-1].axhline(0); panels[-1].set_xlabel("month")
                else: panels[-1].plot(df["month"], parts[i])
        """},
        compare="chart",
        check=("every_panel",),
        tolerance=1e-9,
        choices=("the parts are those of table.add_trend_and_season: STL with R stl()'s settings (season window 7, "
                 "season of degree 0, R's spans and jumps), on a cycle of 12 months.",
                 "four panels sharing x, top to bottom: the column itself, its trend, its season and the rest, the "
                 "rest drawn as sticks from 0, as R plot(stl(...)) (which names the first panel \"data\").",),
        also="The four panels are inset axes (matplotlib inset_axes) inside one chart, so the chart can be placed on a "
             "page like any other; the test reads each panel. test_method=\"moving averages\" or \"straight line\" "
             "works here too. simplydata also gives the chart its paper look (fonts, colours, tick labels only under "
             "the last panel); that is left out here.",
    ),
    Entry(
        word="forecast",
        data="visitors",
        ours="""
            table = sdata.get_example("visitors")
            table.keep_rows_where("museum", is_equal_to="Harbour Museum")
            chart = table.start_chart().draw_lines(x="month", y="visitors")
            chart.forecast(steps_ahead=12, repeats_every="year")
        """,
        code={
            "R": """
                # forecast(steps_ahead=12, repeats_every="year"), after draw_lines(x="month", y="visitors")
                fit <- stats::HoltWinters(stats::ts(x, frequency = 12), seasonal = "additive")   # (1)
                f <- forecast::forecast(fit, h = 12, level = 95)                                # (2)
                list(mean = as.numeric(f$mean), low = as.numeric(f$lower), high = as.numeric(f$upper))
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt, pandas as pd, seaborn as sns
                df = pd.read_csv("visitors.csv", parse_dates=["month"])
                df = df[df["museum"] == "Harbour Museum"].sort_values("month")
                fig, ax = plt.subplots()
                sns.lineplot(df, x="month", y="visitors", ax=ax)
                ahead = pd.date_range(df["month"].max(), periods=13, freq="MS")[1:]   # (3)
                ax.plot(ahead, mean, "--")
                ax.fill_between(ahead, low, high, alpha=0.2)
            """,
        },
        r_inputs=HARBOUR,
        r_packages=("forecast",),
        compare="chart",
        check=("lines", "shapes", "labels"),
        tolerance=1e-9,
        choices=("the numbers of table.forecast: Holt-Winters as R stats::HoltWinters fits it (a level, a trend and an "
                 "added season, repeats_every=\"year\" = 12 months).",
                 "the band is the 95 % prediction interval (interval=95), from forecast::forecast.",
                 "the months carry on after the last one, one month apart.",),
        python_note="statsmodels ExponentialSmoothing updates the season in another order and gives other numbers, so "
                    "the forecast comes from R; matplotlib draws it.",
        also="With colour= on the lines each group is forecast on its own. simplydata also prints the forecast's "
             "sentence and gives the chart its paper look; that is left out here.",
    ),
    Entry(
        word="system.chart",
        ours="""
            system = sdata.system("1 / (s + 1)**3")
            system.chart()
        """,
        code={"matplotlib": """
            import numpy as np, matplotlib.pyplot as plt
            from scipy import signal
            lti = signal.lti([1], [1, 3, 3, 1])
            # chart()
            w, h = signal.freqresp(lti, w=signal.findfreqs([1], [1, 3, 3, 1], 200))   # (1)
            fig, (top, bottom) = plt.subplots(2, 1, sharex=True)                  # (2)
            top.plot(w, 20 * np.log10(np.abs(h))); top.set_ylabel("gain (decibels)")
            bottom.plot(w, np.degrees(np.unwrap(np.angle(h)))); bottom.set_ylabel("phase (degrees)")
            for panel in (top, bottom):
                panel.set_xscale("log"); panel.set_xlabel("frequency (radians per second)")
        """},
        compare="chart",
        check=("every_panel", "scales"),
        tolerance=1e-9,
        choices=("show=\"bode\": 200 frequencies SciPy picks from the poles and zeros (findfreqs), in radians per "
                 "second (unit=).",
                 "two panels sharing a log x-axis: the gain in decibels above, the phase in degrees below, unwrapped so it "
                 "runs on past -180 degrees.",),
        also="show=\"step\", \"impulse\", \"poles and zeros\" and \"nyquist\" are the other charts. simplydata also "
             "gives the charts their paper look; that is left out here.",
    ),
]
