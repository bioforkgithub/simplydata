"""The reliability study for phase U3, batch 7: time series, cycles, waves and systems.

Each word of src/simplydata/_underneath/signals.py runs on real data and is compared with the package underneath
(SciPy signal, statsmodels) and, where R has the same function, with R (stats, forecast, urca, tseries, changepoint,
signal, gsignal, control). The series are the study's own: the level of Lake Huron (1875-1972), the air passengers
(Box & Jenkins, 1949-1960) and the drivers killed or seriously injured in Great Britain (Seatbelts, 1969-1984).
The systems and the waves have no data: they are checked against their closed-form values (worked out by hand from
the formula) and against R control, signal and gsignal.
"""

from __future__ import annotations

import math

AIR = """
    t = sdata.table(data)
    t.turn_into_dates("month")
"""
CLOSED_FORM = "exact: worked out by hand from the formula"
STEP_FORM = "exact: 0.2 (1 - exp(-t) (cos 2t + sin 2t / 2))"
IMPULSE_FORM = "exact: exp(-t) sin(2t) / 2"
FACTS = "from simplydata._underneath.check import chart_facts\n"


def STEP(t: float) -> float:  # noqa: N802 - the closed form, named as the formula
    return 0.2 * (1 - math.exp(-t) * (math.cos(2 * t) + 0.5 * math.sin(2 * t)))


def IMPULSE(t: float) -> float:  # noqa: N802
    return 0.5 * math.exp(-t) * math.sin(2 * t)


def _join(*parts) -> str:
    import textwrap

    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts)


def _ours_drawn(build: str, read: str, facts: str = "") -> str:
    """simplydata code that builds `chart`, reads what it drew into the table `drawn` with chart.get_numbers_drawn(),
    then the code `read`. `facts` names what no simplydata word reads yet: those are read with chart_facts() into f."""
    import textwrap

    code = textwrap.dedent(build).strip("\n") + "\ndrawn = chart.get_numbers_drawn()\n"
    if facts:
        code = (FACTS + code + f"# no simplydata word reads {facts} yet\n"
                "f = chart_facts(chart._render().axes[0])\n")
    return code + textwrap.dedent(read).strip("\n")


def cases(Case):
    return [
        # ---- smoothing and trend
        Case("nums.smooth", "the level of Lake Huron, 1875-1972: a centred moving average of 5 years", "Lake Huron",
             "real data",
             ours="""
                 s = sdata.numbers(data["level"]).smooth()
                 {"empty at the ends": s.count_empty_numbers(), "third year": s.get_number_at(3),
                  "year 50": s.get_number_at(50)}
             """,
             parent="""
                 m = data["level"].rolling(5, center=True).mean()
                 {"empty at the ends": int(m.isna().sum()), "third year": m.iloc[2], "year 50": m.iloc[49]}
             """, parent_label="pandas rolling(5, center=True).mean()", parent_tolerance=1e-12,
             r="""
                 f <- stats::filter(level, rep(1 / 5, 5), sides = 2)
                 list(`empty at the ends` = sum(is.na(f)), `third year` = f[3], `year 50` = f[50])
             """, r_tolerance=1e-12),
        Case("nums.remove_trend", "the level of Lake Huron without its straight-line fall", "Lake Huron", "real data",
             ours="""
                 d = sdata.numbers(data["level"]).remove_trend()
                 {"first year": d.get_number_at(1), "last year": d.get_number_at(98), "total": d.find_total()}
             """,
             parent="""
                 from scipy import signal
                 d = signal.detrend(data["level"].to_numpy(dtype=float), type="linear")
                 {"first year": d[0], "last year": d[-1], "total": d.sum()}
             """, parent_label="SciPy signal.detrend", parent_tolerance=1e-9,
             r="""
                 d <- stats::residuals(stats::lm(level ~ seq_along(level)))
                 list(`first year` = d[[1]], `last year` = d[[98]])
             """, r_tolerance=1e-9),
        Case("table.add_trend_and_season", "the air passengers: trend, season and rest by STL (season window 7)",
             "AirPassengers", "real data",
             ours=_join(AIR, """
                 t.add_trend_and_season("passengers", sorted_by="month", repeats_every="year")
                 {"trend, January 1949": t.get_cell_at(row=1, column="passengers_trend"),
                  "season, July 1955": t.get_cell_at(row=79, column="passengers_season"),
                  "rest, December 1960": t.get_cell_at(row=144, column="passengers_rest")}
             """),
             parent="""
                 from statsmodels.tsa.seasonal import STL
                 f = STL(data["passengers"].to_numpy(dtype=float), period=12, seasonal=7, trend=23, low_pass=13,
                         seasonal_deg=0, seasonal_jump=1, trend_jump=3, low_pass_jump=2).fit(inner_iter=2,
                                                                                            outer_iter=0)
                 {"trend, January 1949": f.trend[0], "season, July 1955": f.seasonal[78],
                  "rest, December 1960": f.resid[143]}
             """, parent_label="statsmodels STL with R stl()'s settings", parent_tolerance=1e-9,
             r="""
                 s <- stats::stl(stats::ts(passengers, frequency = 12), s.window = 7)$time.series
                 list(`trend, January 1949` = s[1, "trend"], `season, July 1955` = s[79, "seasonal"],
                      `rest, December 1960` = s[144, "remainder"])
             """, r_tolerance=1e-9),
        # ---- autocorrelation, steady, change points
        Case("nums.find_autocorrelation", "the level of Lake Huron: correlation with itself 1 and 2 years back",
             "Lake Huron", "real data",
             ours="""
                 r = sdata.numbers(data["level"]).find_autocorrelation()
                 {"rows back": r.count_rows(), "1 year back": r.get_cell_at(row=1, column="correlation"),
                  "2 years back": r.get_cell_at(row=2, column="correlation"),
                  "Ljung-Box statistic": r.get_cell_at(row=1, column="Ljung-Box statistic")}
             """,
             parent="""
                 from statsmodels.stats.diagnostic import acorr_ljungbox
                 from statsmodels.tsa.stattools import acf
                 x = data["level"].to_numpy(dtype=float)
                 a = acf(x, nlags=19, adjusted=False, fft=False)
                 {"rows back": 19, "1 year back": a[1], "2 years back": a[2],
                  "Ljung-Box statistic": acorr_ljungbox(x, lags=[19])["lb_stat"].iloc[0]}
             """, parent_label="statsmodels acf and acorr_ljungbox", parent_tolerance=1e-12,
             r="""
                 a <- stats::acf(level, plot = FALSE)
                 list(`rows back` = length(a$lag) - 1, `1 year back` = a$acf[2], `2 years back` = a$acf[3],
                      `Ljung-Box statistic` = unname(stats::Box.test(level, lag = 19, type = "Ljung-Box")$statistic))
             """, r_tolerance=1e-12),
        Case("table.check_steady_over_time", "the level of Lake Huron: the ADF and KPSS tests around one level",
             "Lake Huron", "real data", ours_r=("urca", "tseries"),
             ours="""
                 r = sdata.table(data).check_steady_over_time("level", sorted_by="year")
                 {"ADF statistic": r.get_cell_at(row=1, column="statistic"),
                  "ADF p-value": r.get_cell_at(row=1, column="p-value"),
                  "KPSS statistic": r.get_cell_at(row=2, column="statistic")}
             """,
             r="""
                 lags <- trunc((length(level) - 1)^(1/3))
                 u <- urca::ur.df(level, type = "drift", lags = lags, selectlags = "Fixed")
                 p <- urca::punitroot(u@teststat[1], N = length(u@res), trend = "c", statistic = "t")
                 k <- suppressWarnings(tseries::kpss.test(level, null = "Level"))
                 list(`ADF statistic` = unname(u@teststat[1]), `ADF p-value` = p,
                      `KPSS statistic` = unname(k$statistic))
             """, r_packages=("urca", "tseries"), r_tolerance=1e-9),
        Case("table.find_change_points_in", "the level of Lake Huron: where its average jumps (PELT, MBIC)",
             "Lake Huron", "real data", ours_r=("changepoint",),
             ours="""
                 r = sdata.table(data).find_change_points_in("level", sorted_by="year")
                 {"pieces": r.count_rows(), "first piece ends": r.get_cell_at(row=1, column="to"),
                  "average of the first piece": r.get_cell_at(row=1, column="average")}
             """,
             r="""
                 s <- stats::mad(diff(level)) / sqrt(2)
                 e <- changepoint::cpts(changepoint::cpt.mean(level / s, method = "PELT", penalty = "MBIC"))
                 list(pieces = length(e) + 1, `first piece ends` = year[e[1]],
                      `average of the first piece` = mean(level[1:e[1]]))
             """, r_packages=("changepoint",), r_tolerance=1e-12),
        # ---- forecasts
        Case("nums.forecast", "the air passengers: Holt-Winters forecast of 1961 with its 95 % interval",
             "AirPassengers", "real data", ours_r=("forecast",),
             ours="""
                 r = sdata.numbers(data["passengers"]).forecast(steps_ahead=12, repeats_every=12)
                 {"January 1961": r.get_cell_at(row=1, column="forecast"),
                  "January 1961, 95 % low": r.get_cell_at(row=1, column="forecast 95 % prediction low"),
                  "December 1961": r.get_cell_at(row=12, column="forecast")}
             """,
             r="""
                 f <- forecast::forecast(stats::HoltWinters(stats::ts(passengers, frequency = 12)), h = 12, level = 95)
                 list(`January 1961` = f$mean[1], `January 1961, 95 % low` = f$lower[1], `December 1961` = f$mean[12])
             """, r_packages=("forecast",), r_tolerance=1e-9),
        Case("table.compare_forecasts_for", "the air passengers: four methods checked on 1960", "AirPassengers",
             "real data", ours_r=("forecast",),
             ours=_join(AIR, """
                 r = t.compare_forecasts_for("passengers", sorted_by="month", repeats_every="year")
                 {"best MASE": r.get_cell_at(row=1, column="MASE"), "worst MASE": r.get_cell_at(row=4, column="MASE"),
                  "best MAE": r.get_cell_at(row=1, column="MAE")}
             """),
             r="""
                 y <- stats::ts(passengers[1:132], frequency = 12); test <- passengers[133:144]
                 fs <- list(forecast::naive(y, h = 12), forecast::snaive(y, h = 12),
                            forecast::rwf(y, h = 12, drift = TRUE), forecast::forecast(stats::HoltWinters(y), h = 12))
                 a <- sapply(fs, function(f) forecast::accuracy(f, stats::ts(test, frequency = 12, start = stats::tsp(f$mean)[1]))["Test set", c("MAE", "MASE")])
                 list(`best MASE` = min(a[2, ]), `worst MASE` = max(a[2, ]), `best MAE` = a[1, which.min(a[2, ])])
             """, r_packages=("forecast",), r_tolerance=1e-9),
        # ---- peaks and dips
        Case("nums.find_each_peak_that", "the drivers killed or seriously injured: the peaks at least 6 months apart",
             "Seatbelts", "real data",
             ours="""
                 r = sdata.numbers(data["drivers"]).find_each_peak_that(apart=6)
                 {"peaks": r.count_rows(), "first peak": r.get_cell_at(row=1, column="position"),
                  "its width": r.get_cell_at(row=1, column="width")}
             """,
             parent="""
                 from scipy import signal
                 y = data["drivers"].to_numpy(dtype=float)
                 p, _ = signal.find_peaks(y, distance=6)
                 {"peaks": len(p), "first peak": p[0] + 1, "its width": signal.peak_widths(y, p, rel_height=0.5)[0][0]}
             """, parent_label="SciPy find_peaks(distance=6) and peak_widths", parent_tolerance=1e-12,
             r="""
                 p <- pracma::findpeaks(drivers, minpeakdistance = 6, sortstr = FALSE)
                 list(peaks = nrow(p), `first peak` = min(p[, 2]))
             """, r_packages=("pracma",), r_tolerance=0.0,
             note="pracma::findpeaks keeps the higher of two close peaks first, as SciPy's distance= does."),
        Case("nums.find_each_dip_that", "the level of Lake Huron: the lowest years, dips at least 5 years apart",
             "Lake Huron", "real data",
             ours="""
                 r = sdata.numbers(data["level"]).find_each_dip_that(apart=5)
                 {"dips": r.count_rows(), "lowest dip": r.get_column("value").find_smallest(),
                  "first dip": r.get_cell_at(row=1, column="position")}
             """,
             parent="""
                 from scipy import signal
                 y = data["level"].to_numpy(dtype=float)
                 d, _ = signal.find_peaks(-y, distance=5)
                 {"dips": len(d), "lowest dip": y[d].min(), "first dip": d[0] + 1}
             """, parent_label="SciPy find_peaks on minus the level", parent_tolerance=0.0),
        Case("table.find_each_dip_that", "the air passengers: the dips at least 6 months apart", "AirPassengers",
             "real data",
             ours=_join(AIR, """
                 r = t.find_each_dip_that("passengers", apart=6)
                 {"dips": r.count_rows(), "first dip": r.get_cell_at(row=1, column="position"),
                  "lowest dip": r.get_column("value").find_smallest()}
             """),
             parent="""
                 from scipy import signal
                 y = data["passengers"].to_numpy(dtype=float)
                 d, _ = signal.find_peaks(-y, distance=6)
                 {"dips": len(d), "first dip": d[0] + 1, "lowest dip": y[d].min()}
             """, parent_label="SciPy find_peaks on minus the passengers", parent_tolerance=0.0),
        # ---- spectra
        Case("table.find_spectrum_of", "the level of Lake Huron: the periodogram, per year", "Lake Huron", "real data",
             ours="""
                 r = sdata.table(data).find_spectrum_of("level", sorted_by="year")
                 {"frequencies": r.count_rows(), "power at 1 / 98 per year": r.get_cell_at(row=2, column="power"),
                  "power at 10 / 98 per year": r.get_cell_at(row=11, column="power")}
             """,
             parent="""
                 from scipy import signal
                 f, p = signal.periodogram(data["level"].to_numpy(dtype=float), fs=1.0, detrend="constant",
                                           window="boxcar", scaling="density")
                 {"frequencies": len(f), "power at 1 / 98 per year": p[1], "power at 10 / 98 per year": p[10]}
             """, parent_label="SciPy signal.periodogram", parent_tolerance=1e-9,
             r="""
                 s <- stats::spec.pgram(level, taper = 0, detrend = FALSE, fast = FALSE, plot = FALSE)$spec
                 list(`power at 1 / 98 per year` = 2 * s[1], `power at 10 / 98 per year` = 2 * s[10])
             """, r_tolerance=1e-9,
             note="R spec.pgram is two-sided and has no row for frequency 0, so its first value is SciPy's second, "
                  "halved."),
        Case("nums.find_spectrum", "the drivers killed or seriously injured: the yearly cycle in the periodogram",
             "Seatbelts", "real data",
             ours="""
                 r = sdata.numbers(data["drivers"]).find_spectrum()
                 {"power at 1 / 12 per month": r.get_cell_at(row=17, column="power")}
             """,
             parent="""
                 from scipy import signal
                 y = data["drivers"].to_numpy(dtype=float)
                 f, p = signal.periodogram(y, detrend="constant", window="boxcar", scaling="density")
                 {"power at 1 / 12 per month": p[16]}
             """, parent_label="SciPy signal.periodogram", parent_tolerance=1e-9,
             r="""
                 s <- stats::spec.pgram(drivers, taper = 0, detrend = FALSE, fast = FALSE, plot = FALSE)
                 list(`power at 1 / 12 per month` = 2 * s$spec[16])
             """, r_tolerance=1e-9,
             note="192 months: frequency 16 / 192 is once a year."),
        Case("spectrum", "the drawn periodogram of the Lake Huron level is SciPy's", "Lake Huron", "real data",
             ours=_ours_drawn("""
                 chart = sdata.chart(data).spectrum("level", sorted_by="year")
             """, """
                 {"points": drawn.count_rows(), "first power drawn": drawn.get_cell_at(row=1, column="y"),
                  "labels": len(f["texts"][1])}
             """, facts="the labels written on the chart"),
             parent="""
                 from scipy import signal
                 f, p = signal.periodogram(data["level"].to_numpy(dtype=float), detrend="constant", window="boxcar",
                                           scaling="density")
                 {"points": len(f) - 1, "first power drawn": p[1], "labels": 3}
             """, parent_label="SciPy signal.periodogram", parent_tolerance=1e-9),
        Case("spectrum_over_time", "the drivers killed or seriously injured: spectrum over time in pieces of 48 months",
             "Seatbelts", "real data",
             ours=_ours_drawn("""
                 chart = sdata.chart(data).spectrum_over_time("drivers", window=48)
             """, """
                 # row 2: the cells go piece by piece along the lowest frequency first, as SciPy's p.ravel() does
                 {"cells": drawn.count_rows(), "first cell (decibels)": drawn.get_cell_at(row=2, column="value")}
             """),
             parent="""
                 import numpy as np
                 from scipy import signal
                 f, t, p = signal.spectrogram(data["drivers"].to_numpy(dtype=float), window="hann", nperseg=48,
                                              noverlap=24, detrend="constant", scaling="density")
                 {"cells": p.size, "first cell (decibels)": 10 * np.log10(p.ravel()[1])}
             """, parent_label="SciPy signal.spectrogram", parent_tolerance=1e-9),
        # ---- filters and the envelope
        Case("nums.keep_each_frequency_that", "the Lake Huron level: cycles slower than 10 years kept",
             "Lake Huron", "real data",
             ours="""
                 s = sdata.numbers(data["level"]).keep_each_frequency_that(is_below=0.1, time_step=1)
                 {"first year": s.get_number_at(1), "year 50": s.get_number_at(50)}
             """,
             parent="""
                 from scipy import signal
                 sos = signal.butter(4, 0.1, btype="lowpass", output="sos", fs=1.0)
                 s = signal.sosfiltfilt(sos, data["level"].to_numpy(dtype=float))
                 {"first year": s[0], "year 50": s[49]}
             """, parent_label="SciPy butter and sosfiltfilt", parent_tolerance=1e-9),
        Case("nums.remove_each_frequency_that", "the drivers killed or seriously injured: the yearly cycle notched out",
             "Seatbelts", "real data",
             ours="""
                 s = sdata.numbers(data["drivers"]).remove_each_frequency_that(is_equal_to=1, time_step=1 / 12,
                                                                              width=0.1)
                 {"first month": s.get_number_at(1), "month 100": s.get_number_at(100)}
             """,
             parent="""
                 from scipy import signal
                 b, a = signal.iirnotch(1, 1 / 0.1, fs=12)
                 s = signal.filtfilt(b, a, data["drivers"].to_numpy(dtype=float))
                 {"first month": s[0], "month 100": s[99]}
             """, parent_label="SciPy iirnotch and filtfilt", parent_tolerance=1e-9),
        Case("table.add_filtered_column", "the Lake Huron level: a column of the cycles slower than 10 years",
             "Lake Huron", "real data",
             ours="""
                 t = sdata.table(data)
                 t.add_filtered_column("slow", from_column="level", keep_below=0.1, sorted_by="year")
                 {"1875": t.get_cell_at(row=1, column="slow"), "1924": t.get_cell_at(row=50, column="slow")}
             """,
             parent="""
                 from scipy import signal
                 sos = signal.butter(4, 0.1, btype="lowpass", output="sos", fs=1.0)
                 s = signal.sosfiltfilt(sos, data.sort_values("year")["level"].to_numpy(dtype=float))
                 {"1875": s[0], "1924": s[49]}
             """, parent_label="SciPy butter and sosfiltfilt", parent_tolerance=1e-9,
             note="The years are one apart, so keep_below=0.1 keeps the cycles longer than 10 years."),
        Case("sdata.frequency_filter", "the filter of keep_below=10 at 200 readings a second is R signal's",
             "closed form (no data)", "closed form",
             ours="""
                 f = sdata.frequency_filter(keep_below=10, time_step=0.005)
                 t, g = f.table(), f.frequency_response(between=[10, 20], how_many=2)
                 {"b0": t.get_cell_at(row=1, column="numerator"), "a1": t.get_cell_at(row=2, column="denominator"),
                  "a4": t.get_cell_at(row=5, column="denominator"), "gain at 10": g.get_cell_at(row=1, column="gain"),
                  "numerator total / denominator total": t.get_column("numerator").find_total()
                  / t.get_column("denominator").find_total()}
             """,
             published={"gain at 10": (0.5 ** 0.5, 1e-12, "exact: a Butterworth filter passes 1 / sqrt(2) at its "
                                                          "cutoff"),
                        "numerator total / denominator total": (1.0, 1e-12, "exact: a low-pass filter passes "
                                                                             "frequency 0 whole (gain 1 at z = 1)")},
             parent="""
                 from scipy import signal
                 b, a = signal.butter(4, 10, fs=200)
                 {"b0": b[0], "a1": a[1], "a4": a[4]}
             """, parent_label="SciPy signal.butter (as numerator and denominator)", parent_tolerance=1e-9,
             r="""
                 f <- gsignal::butter(4, 10 / 100)
                 list(b0 = f$b[1], a1 = f$a[2], a4 = f$a[5])
             """, r_packages=("gsignal",), r_tolerance=1e-9,
             note="A filter has no data: the Butterworth design of order 4 at a tenth of the top frequency. The "
                  "coefficients are compared with SciPy and R signal; the two gains with their exact values."),
        Case("nums.find_envelope", "the Lake Huron level about its average: the envelope", "Lake Huron", "real data",
             ours="""
                 e = sdata.numbers(data["level"]).remove_trend(test_method="average").find_envelope()
                 {"first year": e.get_number_at(1), "year 50": e.get_number_at(50)}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 x = data["level"].to_numpy(dtype=float)
                 e = np.abs(signal.hilbert(x - x.mean()))
                 {"first year": e[0], "year 50": e[49]}
             """, parent_label="SciPy signal.hilbert", parent_tolerance=1e-9,
             r="""
                 e <- Mod(gsignal::hilbert(level - mean(level)))
                 list(`first year` = e[1], `year 50` = e[50])
             """, r_packages=("gsignal",), r_tolerance=1e-9),
        Case("table.add_envelope_column", "the drivers killed or seriously injured: the envelope column",
             "Seatbelts", "real data",
             ours="""
                 t = sdata.table(data)
                 t.add_envelope_column("envelope", from_column="drivers", sorted_by="month")
                 {"first month": t.get_cell_at(row=1, column="envelope"),
                  "month 100": t.get_cell_at(row=100, column="envelope")}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 e = np.abs(signal.hilbert(data.sort_values("month")["drivers"].to_numpy(dtype=float)))
                 {"first month": e[0], "month 100": e[99]}
             """, parent_label="SciPy signal.hilbert", parent_tolerance=1e-9,
             r="""
                 e <- Mod(gsignal::hilbert(drivers[order(month)]))
                 list(`first month` = e[1], `month 100` = e[100])
             """, r_packages=("gsignal",), r_tolerance=1e-9),
        # ---- Fourier, convolution, resampling
        Case("nums.take_fourier_transform", "the Lake Huron level: the size and phase of the first frequencies",
             "Lake Huron", "real data",
             ours="""
                 r = sdata.numbers(data["level"]).take_fourier_transform()
                 {"frequencies": r.count_rows(), "size at 0": r.get_cell_at(row=1, column="size"),
                  "size at 1 / 98": r.get_cell_at(row=2, column="size"),
                  "phase at 1 / 98": r.get_cell_at(row=2, column="phase")}
             """,
             parent="""
                 import numpy as np
                 from scipy import fft
                 z = fft.rfft(data["level"].to_numpy(dtype=float))
                 {"frequencies": len(z), "size at 0": abs(z[0]), "size at 1 / 98": abs(z[1]),
                  "phase at 1 / 98": np.degrees(np.angle(z[1]))}
             """, parent_label="SciPy fft.rfft", parent_tolerance=1e-12,
             r="""
                 z <- stats::fft(level)
                 list(`size at 0` = Mod(z[1]), `size at 1 / 98` = Mod(z[2]), `phase at 1 / 98` = Arg(z[2]) * 180 / pi)
             """, r_tolerance=1e-10),
        Case("sdata.find_inverse_fourier_transform", "the Lake Huron level there and back", "Lake Huron",
             "real data",
             ours="""
                 back = sdata.find_inverse_fourier_transform(sdata.numbers(data["level"]).take_fourier_transform())
                 {"count": back.count(), "first year": back.get_number_at(1), "last year": back.get_number_at(98)}
             """,
             parent="""
                 {"count": len(data), "first year": data["level"].iloc[0], "last year": data["level"].iloc[-1]}
             """, parent_label="the data themselves", parent_tolerance=1e-12),
        Case("nums.convolve_with", "the air passengers convolved with the weights 1, 2, 1", "AirPassengers",
             "real data",
             ours="""
                 c = sdata.numbers(data["passengers"]).convolve_with([1, 2, 1])
                 {"count": c.count(), "first": c.get_number_at(1), "number 100": c.get_number_at(100)}
             """,
             parent="""
                 import numpy as np
                 c = np.convolve(data["passengers"].to_numpy(dtype=float), [1, 2, 1])
                 {"count": len(c), "first": c[0], "number 100": c[99]}
             """, parent_label="NumPy convolve (full)", parent_tolerance=1e-12,
             r="""
                 c <- stats::convolve(passengers, rev(c(1, 2, 1)), type = "open")
                 list(count = length(c), first = c[1], `number 100` = c[100])
             """, r_tolerance=1e-9),
        Case("nums.deconvolve_by", "the air passengers divided by 1 + 0.5 z^-1", "AirPassengers", "real data",
             ours="""
                 q = sdata.numbers(data["passengers"]).deconvolve_by([1, 0.5])
                 {"count": q.count(), "first": q.get_number_at(1), "number 100": q.get_number_at(100)}
             """,
             parent="""
                 from scipy import signal
                 q, _ = signal.deconvolve(data["passengers"].to_numpy(dtype=float), [1, 0.5])
                 {"count": len(q), "first": q[0], "number 100": q[99]}
             """, parent_label="SciPy signal.deconvolve", parent_tolerance=1e-12,
             r="""
                 q <- stats::filter(passengers, -0.5, method = "recursive")[1:143]
                 list(count = length(q), first = q[1], `number 100` = q[100])
             """, r_tolerance=1e-9,
             note="Dividing by 1 + 0.5 z^-1 is the recursive filter y[t] = x[t] - 0.5 y[t - 1]."),
        Case("nums.change_time_step", "the air passengers every two months (Fourier resampling)", "AirPassengers",
             "real data",
             ours="""
                 r = sdata.numbers(data["passengers"]).change_time_step(to=2, time_step=1)
                 {"count": r.count(), "first": r.get_number_at(1), "number 30": r.get_number_at(30)}
             """,
             parent="""
                 from scipy import signal
                 r = signal.resample(data["passengers"].to_numpy(dtype=float), 72)
                 {"count": len(r), "first": r[0], "number 30": r[29]}
             """, parent_label="SciPy signal.resample", parent_tolerance=1e-9),
        Case("sdata.make_wave", "a square wave of 5 cycles a second, 100 readings 0.01 seconds apart", "closed form (no data)",
             "closed form",
             ours="""
                 w = sdata.make_wave("square", frequency=5, time_step=0.01, how_many=100)
                 {"first": w.get_number_at(1), "number 11": w.get_number_at(11), "total": w.find_total()}
             """,
             published={"first": (1.0, 0.0, CLOSED_FORM), "number 11": (-1.0, 0.0, CLOSED_FORM),
                        "total": (0.0, 0.0, CLOSED_FORM)},
             parent="""
                 import numpy as np
                 from scipy import signal
                 w = signal.square(2 * np.pi * 5 * np.arange(100) * 0.01)
                 {"first": w[0], "number 11": w[10], "total": w.sum()}
             """, parent_label="SciPy signal.square", parent_tolerance=0.0,
             note="Each cycle is 20 readings: 10 high, then 10 low."),
        Case("sdata.make_window_shape", "the symmetric Hann window of 64 weights", "closed form (no data)", "closed form",
             ours="""
                 w = sdata.make_window_shape("hann", how_many=64)
                 {"first": w.get_number_at(1), "number 32": w.get_number_at(32), "total": w.find_total()}
             """,
             published={"first": (0.0, 1e-15, CLOSED_FORM), "total": (31.5, 1e-12, CLOSED_FORM + ": (64 - 1) / 2")},
             parent="""
                 import numpy as np
                 w = np.hanning(64)
                 {"first": w[0], "number 32": w[31], "total": w.sum()}
             """, parent_label="NumPy hanning", parent_tolerance=1e-12,
             r="""
                 w <- gsignal::hann(64)
                 list(`number 32` = w[32], total = sum(w))
             """, r_packages=("gsignal",), r_tolerance=1e-12),
        # ---- systems: no data, closed forms and R control
        Case("sdata.system", "2 / (2 s^2 + 4 s + 10) is written as 1 / (s^2 + 2 s + 5)", "closed form (no data)", "closed form",
             ours="""
                 t = sdata.system("2 / (2*s**2 + 4*s + 10)").table()
                 {"top": t.get_cell_at(row=3, column="numerator"), "s": t.get_cell_at(row=2, column="denominator"),
                  "constant": t.get_cell_at(row=3, column="denominator")}
             """,
             published={"top": (1.0, 1e-15, CLOSED_FORM), "s": (2.0, 1e-15, CLOSED_FORM),
                        "constant": (5.0, 1e-15, CLOSED_FORM)}),
        Case("system.step_response", "1 / (s^2 + 2 s + 5): the step response against its closed form",
             "closed form (no data)", "closed form",
             ours="""
                 r = sdata.system("1 / (s**2 + 2*s + 5)").step_response(until=10)
                 {"at time 10 / 199 x 31": r.get_cell_at(row=32, column="output"),
                  "at time 10": r.get_cell_at(row=200, column="output")}
             """,
             published={"at time 10 / 199 x 31": (STEP(10 / 199 * 31), 1e-7, STEP_FORM),
                        "at time 10": (STEP(10.0), 1e-7, STEP_FORM)},
             parent="""
                 import numpy as np
                 from scipy import signal
                 t, y = signal.step(signal.lti([1], [1, 2, 5]), T=np.linspace(0, 10, 200))
                 {"at time 10 / 199 x 31": y[31], "at time 10": y[199]}
             """, parent_label="SciPy signal.step", parent_tolerance=1e-12,
             note="SciPy's step response solves the system numerically, so it agrees with the formula to about 1e-8."),
        Case("system.impulse_response", "1 / (s^2 + 2 s + 5): the impulse response against its closed form",
             "closed form (no data)", "closed form",
             ours="""
                 r = sdata.system("1 / (s**2 + 2*s + 5)").impulse_response(until=10)
                 {"at time 10 / 199 x 31": r.get_cell_at(row=32, column="output"),
                  "at time 10": r.get_cell_at(row=200, column="output")}
             """,
             published={"at time 10 / 199 x 31": (IMPULSE(10 / 199 * 31), 1e-7, IMPULSE_FORM),
                        "at time 10": (IMPULSE(10.0), 1e-7, IMPULSE_FORM)},
             parent="""
                 import numpy as np
                 from scipy import signal
                 t, y = signal.impulse(signal.lti([1], [1, 2, 5]), T=np.linspace(0, 10, 200))
                 {"at time 10 / 199 x 31": y[31], "at time 10": y[199]}
             """, parent_label="SciPy signal.impulse", parent_tolerance=1e-12),
        Case("system.response_to", "a first-order lag 1 / (5 s + 1) fed the level of Lake Huron, year by year",
             "Lake Huron", "real data",
             ours="""
                 r = sdata.system("1 / (5*s + 1)").response_to(sdata.numbers(data["level"]),
                                                             time_points=sdata.numbers(data["year"]))
                 {"output after 1 year": r.get_cell_at(row=2, column="output"),
                  "output in 1972": r.get_cell_at(row=98, column="output")}
             """,
             parent="""
                 from scipy import signal
                 y = signal.lsim(signal.lti([1], [5, 1]), data["level"].to_numpy(dtype=float),
                                 data["year"].to_numpy(dtype=float), interp=False)[1]
                 {"output after 1 year": y[1], "output in 1972": y[-1]}
             """, parent_label="SciPy signal.lsim(interp=False)", parent_tolerance=1e-9,
             r="""
                 a <- exp(-1 / 5)
                 y <- stats::filter((1 - a) * c(0, level[-length(level)]), a, method = "recursive")
                 list(`output after 1 year` = y[2], `output in 1972` = y[98])
             """, r_tolerance=1e-9,
             note="With each input held for a year, the lag is exactly y[t] = a y[t - 1] + (1 - a) x[t - 1], "
                  "a = exp(-1 / 5)."),
        Case("system.frequency_response", "1 / (s^2 + 2 s + 5) at 1 radian per second", "closed form (no data)", "closed form",
             ours="""
                 r = sdata.system("1 / (s**2 + 2*s + 5)").frequency_response(between=[1, 10], how_many=2)
                 {"gain at 1": r.get_cell_at(row=1, column="gain"),
                  "phase at 1": r.get_cell_at(row=1, column="phase (degrees)")}
             """,
             published={"gain at 1": (20 ** -0.5, 1e-12, CLOSED_FORM + ": 1 / sqrt(16 + 4)"),
                        "phase at 1": (-26.56505117707799, 1e-10, CLOSED_FORM + ": -atan(2 / 4) in degrees")},
             r="""
                 h <- 1 / complex(real = 5 - 1, imaginary = 2)
                 list(`gain at 1` = Mod(h), `phase at 1` = Arg(h) * 180 / pi)
             """, r_tolerance=1e-12),
        Case("system.poles", "1 / (s^2 + 2 s + 5): poles -1 +/- 2i", "closed form (no data)", "closed form",
             ours="""
                 r = sdata.system("1 / (s**2 + 2*s + 5)").poles()
                 {"real part": r.get_cell_at(row=1, column="real part"),
                  "damping ratio": r.get_cell_at(row=1, column="damping ratio"),
                  "natural frequency": r.get_cell_at(row=1, column="natural frequency")}
             """,
             published={"real part": (-1.0, 1e-12, CLOSED_FORM), "damping ratio": (5 ** -0.5, 1e-12, CLOSED_FORM),
                        "natural frequency": (5 ** 0.5, 1e-12, CLOSED_FORM)},
             r="""
                 p <- polyroot(c(5, 2, 1))[1]
                 list(`real part` = Re(p), `damping ratio` = -Re(p) / Mod(p), `natural frequency` = Mod(p))
             """, r_tolerance=1e-12),
        Case("system.zeros", "(s + 1) / (s^2 + 2 s + 5): one zero at -1", "closed form (no data)", "closed form",
             ours="""
                 r = sdata.system("(s + 1) / (s**2 + 2*s + 5)").zeros()
                 {"zeros": r.count_rows(), "real part": r.get_cell_at(row=1, column="real part")}
             """,
             published={"zeros": (1, 0, CLOSED_FORM), "real part": (-1.0, 1e-12, CLOSED_FORM)}),
        Case("system.is_stable", "1 / (s^2 + 4) rings for ever: poles on the axis are not stable", "closed form (no data)",
             "closed form",
             ours="""
                 {"stable (1 = yes)": int(sdata.system("1 / (s**2 + 4)").is_stable()),
                  "1 / (s + 1) stable": int(sdata.system("1 / (s + 1)").is_stable())}
             """,
             published={"stable (1 = yes)": (0, 0, CLOSED_FORM + ": poles +/- 2i"),
                        "1 / (s + 1) stable": (1, 0, CLOSED_FORM + ": pole -1")}),
        Case("system.steady_gain", "1 / (s^2 + 2 s + 5) settles at 0.2", "closed form (no data)", "closed form",
             ours="""
                 {"steady gain": sdata.system("1 / (s**2 + 2*s + 5)").steady_gain()}
             """,
             published={"steady gain": (0.2, 1e-15, CLOSED_FORM + ": 1 / 5")},
             r="""
                 list(`steady gain` = control::dcgain(control::tf(1, c(1, 2, 5))))
             """, r_packages=("control",), r_tolerance=1e-12),
        Case("system.in_steps", "1 / (s + 1) in steps of 0.1 (zero order hold)", "closed form (no data)", "closed form",
             ours="""
                 t = sdata.system("1 / (s + 1)").in_steps(time_step=0.1).table()
                 {"top": t.get_cell_at(row=2, column="numerator"), "pole": -t.get_cell_at(row=2, column="denominator")}
             """,
             published={"top": (0.09516258196404048, 1e-12, CLOSED_FORM + ": 1 - exp(-0.1)"),
                        "pole": (0.9048374180359595, 1e-12, CLOSED_FORM + ": exp(-0.1)")},
             r="""
                 d <- control::c2d(control::tf(1, c(1, 1)), 0.1)
                 list(top = d$num[length(d$num)], pole = -d$den[2])
             """, r_packages=("control",), r_tolerance=1e-9),
        Case("system.then", "1 / (s + 1), then 1 / (s + 2): 1 / (s^2 + 3 s + 2)", "closed form (no data)", "closed form",
             ours="""
                 t = sdata.system("1 / (s + 1)").then(sdata.system("1 / (s + 2)")).table()
                 {"s": t.get_cell_at(row=2, column="denominator"), "constant": t.get_cell_at(row=3, column="denominator")}
             """,
             published={"s": (3.0, 1e-15, CLOSED_FORM), "constant": (2.0, 1e-15, CLOSED_FORM)}),
        Case("system.add", "1 / (s + 1) and 1 / (s + 2) side by side: (2 s + 3) / (s^2 + 3 s + 2)", "closed form (no data)",
             "closed form",
             ours="""
                 t = sdata.system("1 / (s + 1)").add(sdata.system("1 / (s + 2)")).table()
                 {"top s": t.get_cell_at(row=2, column="numerator"),
                  "top constant": t.get_cell_at(row=3, column="numerator")}
             """,
             published={"top s": (2.0, 1e-15, CLOSED_FORM), "top constant": (3.0, 1e-15, CLOSED_FORM)}),
        Case("system.with_feedback", "1 / (s^2 + 2 s + 5) in a loop: 1 / (s^2 + 2 s + 6)", "closed form (no data)", "closed form",
             ours="""
                 t = sdata.system("1 / (s**2 + 2*s + 5)").with_feedback().table()
                 {"constant": t.get_cell_at(row=3, column="denominator")}
             """,
             published={"constant": (6.0, 1e-15, CLOSED_FORM)}),
        Case("system.table", "(s + 1) / (s^2 + 2 s + 5) as numbers, and in state space", "closed form (no data)", "closed form",
             ours="""
                 system = sdata.system("(s + 1) / (s**2 + 2*s + 5)")
                 t = system.table()
                 ss = system.table(form="state space")
                 {"top s^2": t.get_cell_at(row=1, column="numerator"), "rows of A, B, C, D": ss.count_rows()}
             """,
             published={"top s^2": (0.0, 0, CLOSED_FORM), "rows of A, B, C, D": (9, 0, "4 + 2 + 2 + 1 numbers")}),
        Case("system.chart", "the Bode chart of 1 / (s^2 + 2 s + 5): its first gain is SciPy's", "closed form (no data)",
             "closed form",
             ours=_ours_drawn("""
                 import math
                 chart = sdata.system("1 / (s**2 + 2*s + 5)").chart()
             """, """
                 gain = drawn.keep_rows_where("panel", is_equal_to=1)   # panel 1 of a Bode chart is the gain, 2 the phase
                 w = gain.get_cell_at(row=1, column="x")
                 first = gain.get_cell_at(row=1, column="y")
                 exact = -10 * math.log10((5 - w ** 2) ** 2 + (2 * w) ** 2)   # 20 log10 |1 / (5 - w^2 + 2 i w)|
                 {"frequencies": gain.count_rows(), "first gain (decibels)": first,
                  "first gain minus its closed form": first - exact}
             """),
             published={"first gain minus its closed form": (0.0, 1e-9, "exact: 20 log10 |1 / (5 - w^2 + 2iw)| at "
                                                                        "the first frequency drawn")},
             parent="""
                 import numpy as np
                 from scipy import signal
                 w, h = signal.freqresp(signal.lti([1], [1, 2, 5]), w=signal.findfreqs([1], [1, 2, 5], 200))
                 {"frequencies": len(w), "first gain (decibels)": 20 * np.log10(abs(h[0]))}
             """, parent_label="SciPy signal.freqresp", parent_tolerance=1e-12),
        # ---- the other chart words
        Case("autocorrelation_bars", "the drawn sticks for the Lake Huron level are statsmodels' acf", "Lake Huron",
             "real data",
             ours=_ours_drawn("""
                 chart = sdata.chart(data).autocorrelation_bars("level", sorted_by="year")
             """, """
                 sticks = drawn.keep_rows_where("kind", is_equal_to="dot")   # one dot on the top of each stick
                 {"sticks": sticks.count_rows(), "1 year back": sticks.get_cell_at(row=1, column="y")}
             """),
             parent="""
                 from statsmodels.tsa.stattools import acf
                 {"sticks": 19, "1 year back": acf(data["level"], nlags=19, adjusted=False, fft=False)[1]}
             """, parent_label="statsmodels acf", parent_tolerance=1e-12,
             r="""
                 list(`1 year back` = stats::acf(level, plot = FALSE)$acf[2])
             """, r_tolerance=1e-12),
        Case("cross_correlation_bars", "drivers killed or injured and front-seat passengers: the drawn shift 0",
             "Seatbelts", "real data",
             ours=_ours_drawn("""
                 chart = sdata.chart(data).cross_correlation_bars("drivers", "DriversKilled", sorted_by="month",
                                                                  rows_back=12)
             """, """
                 sticks = drawn.keep_rows_where("kind", is_equal_to="dot")   # one dot on the top of each stick
                 count = sticks.count_rows()
                 shift_0 = sticks.keep_rows_where("x", is_equal_to=0).get_cell_at(row=1, column="y")
                 sticks.undo()
                 shift_1 = sticks.keep_rows_where("x", is_equal_to=1).get_cell_at(row=1, column="y")
                 {"sticks": count, "shift 0": shift_0, "shift 1": shift_1}
             """),
             r="""
                 r <- stats::ccf(drivers, DriversKilled, lag.max = 12, plot = FALSE)
                 list(sticks = 25, `shift 0` = r$acf[13], `shift 1` = r$acf[12])
             """, r_tolerance=1e-12,
             note="A stick at shift s pairs the first column at month t with the second at month t + s: R's lag -s."),
        Case("lag_dots", "the Lake Huron level against the year before", "Lake Huron", "real data",
             ours=_ours_drawn("""
                 chart = sdata.chart(data).lag_dots("level", sorted_by="year")
             """, """
                 dots = drawn.keep_rows_where("kind", is_equal_to="dot")
                 {"dots": dots.count_rows(), "first dot x": dots.get_cell_at(row=1, column="x"),
                  "first dot y": dots.get_cell_at(row=1, column="y")}
             """),
             parent="""
                 {"dots": len(data) - 1, "first dot x": data["level"].iloc[0], "first dot y": data["level"].iloc[1]}
             """, parent_label="pandas shift(1)", parent_tolerance=0.0),
        Case("peak_dots", "the drivers killed or seriously injured: a dot on each peak at least 6 months apart",
             "Seatbelts", "real data",
             ours=_ours_drawn("""
                 chart = sdata.chart(data).draw_lines(x="month", y="drivers").peak_dots(apart=6)
             """, """
                 dots = drawn.keep_rows_where("kind", is_equal_to="dot")
                 {"dots": dots.count_rows(), "first dot (month)": dots.get_cell_at(row=1, column="x"),
                  "highest": dots.get_column("y").find_biggest()}
             """),
             parent="""
                 from scipy import signal
                 y = data["drivers"].to_numpy(dtype=float)
                 p, _ = signal.find_peaks(y, distance=6)
                 {"dots": len(p), "first dot (month)": data["month"].iloc[p[0]], "highest": y[p].max()}
             """, parent_label="SciPy find_peaks(distance=6)", parent_tolerance=0.0),
        Case("forecast", "the drawn forecast of the air passengers is R's", "AirPassengers", "real data",
             ours_r=("forecast",),
             ours=_join(AIR, _ours_drawn("""
                 chart = t.start_chart().draw_lines(x="month", y="passengers").forecast(steps_ahead=12,
                                                                                       repeats_every="year")
             """, """
                 # layer 2: the forecast line (layer 1 is the passengers, layer 3 the band); neither line has a name
                 ahead = drawn.keep_rows_where("layer", is_equal_to=2)
                 {"months drawn": ahead.count_rows(), "January 1961": ahead.get_cell_at(row=1, column="y"),
                  "December 1961": ahead.get_cell_at(row="last", column="y")}
             """)),
             r="""
                 f <- forecast::forecast(stats::HoltWinters(stats::ts(passengers, frequency = 12)), h = 12, level = 95)
                 list(`months drawn` = 12, `January 1961` = f$mean[1], `December 1961` = f$mean[12])
             """, r_packages=("forecast",), r_tolerance=1e-9),
            Case("trend_and_season", "the air passengers in four panels: the drawn trend is R stl()'s trend",
             "AirPassengers", "real data",
             ours=_join(AIR, _ours_drawn("""
                 chart = t.start_chart().trend_and_season(x="month", y="passengers", repeats_every="year")
             """, """
                 panels = drawn.get_column("panel").find_biggest()
                 # panel 2: the panels are drawn top to bottom as the column, its trend, its season and the rest
                 trend = drawn.keep_rows_where("panel", is_equal_to=2)
                 {"panels": panels, "trend, January 1949": trend.get_cell_at(row=1, column="y"),
                  "trend, December 1960": trend.get_cell_at(row="last", column="y")}
             """)),
             parent="""
                 from statsmodels.tsa.seasonal import STL
                 f = STL(data["passengers"].to_numpy(dtype=float), period=12, seasonal=7, trend=23, low_pass=13,
                         seasonal_deg=0, seasonal_jump=1, trend_jump=3, low_pass_jump=2).fit(inner_iter=2,
                                                                                            outer_iter=0)
                 {"panels": 4, "trend, January 1949": f.trend[0], "trend, December 1960": f.trend[-1]}
             """, parent_label="statsmodels STL with R stl()'s settings", parent_tolerance=1e-9,
             r="""
                 s <- stats::stl(stats::ts(passengers, frequency = 12), s.window = 7)$time.series
                 list(`trend, January 1949` = s[1, "trend"], `trend, December 1960` = s[144, "trend"])
             """, r_tolerance=1e-9),
]
