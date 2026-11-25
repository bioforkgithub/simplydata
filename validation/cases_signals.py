"""The reliability study for the words that had no check of their own on real data (2026-11-23, branch
reliability-gap): cycles, peaks, filters and the Fourier transform of a series, the time-series chart words, joining
the dots, solving and optimising, and linear systems.

Real data, all in the public domain and read from the installed statsmodels (nothing is stored here):
  * the yearly sunspot numbers 1700-2008 (NOAA National Geophysical Data Center);
  * the monthly sea surface temperature of the Nino 1+2 region 1950-2010 (NOAA ERSST v3b);
  * US inflation and unemployment by quarter 1959-2009 (FRED and the Bureau of Labor Statistics).
The solving and optimising words are checked on published worked examples (Newton's cubic, Rosenbrock's valley, the
Wyndor Glass linear program of Hillier & Lieberman). The system words take formulas, not data: they are checked
against python-control (an implementation of its own, not the SciPy that simplydata calls) and against base R, where
the answers are written out from the poles and residues of the formula; one system answers the sunspot numbers.

Each simplydata side uses simplydata words only. cases.py loads this file at its end and calls add_to().
"""

from __future__ import annotations

import textwrap

import numpy as np
import pandas as pd

SUNSPOTS = "yearly sunspot numbers"
ELNINO = "El Nino sea surface temperatures"
MACRO = "US inflation and unemployment"
NEWTON = "Newton's cubic"
ROSENBROCK = "Rosenbrock's valley"
WYNDOR = "Wyndor Glass linear program"
CHECKS = "checks against R (no published example)"  # defined in cases_planning.py
NO_DATA = (NEWTON, ROSENBROCK, WYNDOR)

STATSMODELS_PD = ("Public domain (a US Government work), as statsmodels states for this dataset. Not stored here: "
                  "read from the installed statsmodels.")


def _datasets(Dataset):
    facts = "No data: a published worked example (facts); only the numbers printed there are quoted, nothing is stored."
    return [
        Dataset(SUNSPOTS, "",
                "309 yearly mean sunspot numbers (Wolf's relative numbers), 1700 to 2008",
                "NOAA National Geophysical Data Center, yearly sunspot numbers (compiled from the Royal Observatory "
                "of Belgium, SIDC). Copy from statsmodels (statsmodels.datasets.sunspots). The solar cycle of about "
                "11 years: Schwabe, H. (1844). Astronomische Nachrichten 21, 233-236; its average length 11.0 years: "
                "Hathaway, D. H. (2015). The solar cycle. Living Reviews in Solar Physics 12, 4.",
                STATSMODELS_PD, "https://www.statsmodels.org/stable/datasets/generated/sunspots.html"),
        Dataset(ELNINO, "",
                "732 monthly averages of the sea surface temperature (degrees Celsius) of the Pacific between 0 and "
                "10 degrees south and 90 and 80 degrees west (Nino 1+2), January 1950 to December 2010",
                "NOAA Climate Prediction Center, ERSST v3b, Nino 1+2 index. Copy from statsmodels "
                "(statsmodels.datasets.elnino).",
                STATSMODELS_PD, "https://www.statsmodels.org/stable/datasets/generated/elnino.html"),
        Dataset(MACRO, "",
                "203 quarters of the US economy, 1959 to 2009: inflation and the unemployment rate (2 of 14 columns)",
                "Federal Reserve Bank of St. Louis (FRED) and the US Bureau of Labor Statistics, compiled by "
                "S. Seabold. Copy from statsmodels (statsmodels.datasets.macrodata).",
                STATSMODELS_PD, "https://www.statsmodels.org/stable/datasets/generated/macrodata.html"),
        Dataset(NEWTON, "",
                "the cubic x^3 - 2x - 5 = 0, Newton's own example for his method; its root 2.09455148",
                "Newton, I. (1669). De analysi per aequationes numero terminorum infinitas, published by Wallis, J. "
                "(1685). A Treatise of Algebra, chapter 94; the root to 8 decimals as in Ypma, T. J. (1995). "
                "Historical development of the Newton-Raphson method. SIAM Review 37(4), 531-551.",
                facts, "https://doi.org/10.1137/1037125"),
        Dataset(ROSENBROCK, "",
                "Rosenbrock's function 100 (y - x^2)^2 + (1 - x)^2 from the start (-1.2, 1); its smallest value 0, "
                "at x = 1, y = 1",
                "Rosenbrock, H. H. (1960). An automatic method for finding the greatest or least value of a "
                "function. The Computer Journal 3(3), 175-184.", facts, "https://doi.org/10.1093/comjnl/3.3.175"),
        Dataset(WYNDOR, "",
                "the Wyndor Glass Co. product mix: largest 3 x1 + 5 x2 with x1 <= 4, 2 x2 <= 12, 3 x1 + 2 x2 <= 18; "
                "the answer x1 = 2, x2 = 6, profit 36, shadow prices 0, 1.5 and 1",
                "Hillier, F. S. & Lieberman, G. J. Introduction to Operations Research (10th ed., 2015), sections "
                "3.1 and 4.7, McGraw-Hill.", facts, "https://www.mheducation.com/"),
    ]


def _load_statsmodels(name: str) -> pd.DataFrame:
    """The three statsmodels datasets as tables with plain column names."""
    if name == SUNSPOTS:
        from statsmodels.datasets import sunspots

        d = sunspots.load_pandas().data
        return pd.DataFrame({"year": d["YEAR"].astype(int).to_numpy(), "sunspots": d["SUNACTIVITY"].to_numpy()})
    if name == ELNINO:
        from statsmodels.datasets import elnino

        d = elnino.load_pandas().data
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        values = d[months].to_numpy(dtype=float).reshape(-1)  # year by year, January to December
        return pd.DataFrame({"month": np.arange(1, len(values) + 1),
                             "year": np.repeat(d["YEAR"].astype(int).to_numpy(), 12), "temperature": values})
    if name == MACRO:
        from statsmodels.datasets import macrodata

        d = macrodata.load_pandas().data
        return pd.DataFrame({"quarter": np.arange(1, len(d) + 1), "infl": d["infl"].to_numpy(),
                             "unemp": d["unemp"].to_numpy()})
    raise KeyError(name)


# ---------------------------------------------------------------- base R written out (no R package needed)
# A system N(s) / D(s) with simple poles p: the residue at p is N(p) / D'(p); the step response is
# N(0) / D(0) + sum(r / p e^(p t)) and the impulse response sum(r e^(p t)). Coefficients highest power first.
R_SYSTEM = """
    pv <- function(cf, s) sapply(s, function(v) sum(cf * v^((length(cf) - 1):0)))
    roots <- function(cf) polyroot(rev(cf))
    deriv <- function(cf) cf[-length(cf)] * ((length(cf) - 1):1)
    conv <- function(a, b) { out <- numeric(length(a) + length(b) - 1)
                             for (i in seq_along(a)) out[i:(i + length(b) - 1)] <- out[i:(i + length(b) - 1)] + a[i] * b
                             out }
    padd <- function(a, b) { n <- max(length(a), length(b)); c(numeric(n - length(a)), a) + c(numeric(n - length(b)), b) }
    step_at <- function(num, den, t) { p <- roots(den); r <- pv(num, p) / pv(deriv(den), p)
                                       sapply(t, function(u) Re(pv(num, 0) / pv(den, 0) + sum(r / p * exp(p * u)))) }
    impulse_at <- function(num, den, t) { p <- roots(den); r <- pv(num, p) / pv(deriv(den), p)
                                          sapply(t, function(u) Re(sum(r * exp(p * u)))) }
"""


def _r(code: str) -> str:
    return R_SYSTEM + code


# the system most cases use: 1 / (s^2 + 2 s + 5), poles -1 +/- 2i, steady gain 0.2
G = '"1 / (s**2 + 2*s + 5)"'


def _with_g(code: str) -> str:
    """python-control code with G = 1 / (s^2 + 2 s + 5) made first."""
    return "import control\nG = control.tf([1], [1, 2, 5])\n" + textwrap.dedent(code).strip("\n")


def _cases(Case):
    sun = 'sdata.table(data)'
    return [
        # ---- cycles: the spectrum (Schwabe's 11-year solar cycle)
        Case("table.find_spectrum_of", "the yearly sunspot numbers: the strongest cycle and the periodogram",
             SUNSPOTS, "published",
             ours=f"""
                 spectrum = {sun}.find_spectrum_of("sunspots", sorted_by="year")
                 strongest = sdata.table(spectrum).keep_biggest_rows(n=1, by="power")
                 {{"strongest cycle (years)": strongest.get_cell_at(row=1, column="repeats every"),
                  "power of the 11-year cycle": spectrum.get_cell_at(row=29, column="power"),
                  "total power": spectrum.get_column("power").find_total()}}
             """,
             published={"strongest cycle (years)": (11.0, 0.5, "Hathaway (2015): 11.0 years on average")},
             parent="""
                 from scipy import signal
                 f, p = signal.periodogram(data["sunspots"].to_numpy(), fs=1.0)
                 {"strongest cycle (years)": 1 / f[1:][p[1:].argmax()], "power of the 11-year cycle": p[28],
                  "total power": p.sum()}
             """, parent_label="SciPy signal.periodogram", parent_tolerance=1e-9,
             r="""
                 p <- spec.pgram(sunspots, taper = 0, detrend = FALSE, fast = FALSE, plot = FALSE)
                 list(`strongest cycle (years)` = 1 / p$freq[which.max(p$spec)],
                      `power of the 11-year cycle` = 2 * p$spec[28], `total power` = 2 * sum(p$spec))
             """, r_tolerance=1e-9,
             note="R spec.pgram gives half the one-sided power and leaves out frequency 0 (whose power is 0 here "
                  "up to rounding); with 309 readings there is no top frequency to treat apart."),
        Case("nums.find_spectrum", "the yearly sunspot numbers as numbers: the periodogram, one reading a year",
             SUNSPOTS, "real data",
             ours=f"""
                 spectrum = {sun}.get_column("sunspots").find_spectrum(time_step=1)
                 {{"frequencies": len(spectrum), "power at 1 / 103 years": spectrum.get_cell_at(row=4, column="power"),
                  "total power": spectrum.get_column("power").find_total()}}
             """,
             parent="""
                 from scipy import signal
                 f, p = signal.periodogram(data["sunspots"].to_numpy(), fs=1.0)
                 {"frequencies": len(f), "power at 1 / 103 years": p[3], "total power": p.sum()}
             """, parent_label="SciPy signal.periodogram", parent_tolerance=1e-9,
             r="""
                 p <- spec.pgram(sunspots, taper = 0, detrend = FALSE, fast = FALSE, plot = FALSE)
                 list(`power at 1 / 103 years` = 2 * p$spec[3], `total power` = 2 * sum(p$spec))
             """, r_tolerance=1e-9),
        Case("draw_spectrum", "the yearly sunspot numbers: the periodogram the chart draws", SUNSPOTS, "real data",
             ours=f"""
                 drawn = {sun}.start_chart().spectrum("sunspots", sorted_by="year").get_numbers_drawn()
                 power = drawn.get_column("y")
                 {{"points": power.count(), "first power": power.get_number_at(1), "total power": power.find_total()}}
             """,
             parent="""
                 from scipy import signal
                 f, p = signal.periodogram(data["sunspots"].to_numpy(), fs=1.0)
                 {"points": len(p) - 1, "first power": p[1], "total power": p[1:].sum()}
             """, parent_label="SciPy signal.periodogram", parent_tolerance=1e-9,
             r="""
                 p <- spec.pgram(sunspots, taper = 0, detrend = FALSE, fast = FALSE, plot = FALSE)
                 list(points = length(p$spec), `first power` = 2 * p$spec[1], `total power` = 2 * sum(p$spec))
             """, r_tolerance=1e-9, note="The chart leaves out frequency 0 (log scale)."),
        Case("draw_spectrum_over_time", "the yearly sunspot numbers in pieces of 64 years: the heat map", SUNSPOTS,
             "real data",
             ours=f"""
                 chart = {sun}.start_chart().spectrum_over_time("sunspots", sorted_by="year", window=64)
                 cells = chart.get_numbers_drawn().get_column("value")
                 {{"cells": cells.count(), "first cell (dB)": cells.get_number_at(1), "total (dB)": cells.find_total()}}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 f, t, s = signal.spectrogram(data["sunspots"].to_numpy(), fs=1.0, window="hann", nperseg=64,
                                              noverlap=32)
                 db = 10 * np.log10(s)
                 {"cells": db.size, "first cell (dB)": db[0, 0], "total (dB)": db.sum()}
             """, parent_label="SciPy signal.spectrogram", parent_tolerance=1e-9),
        # ---- peaks and dips
        Case("nums.find_each_peak_that", "the yearly sunspot numbers: the solar maxima of at least 100", SUNSPOTS,
             "real data",
             ours=f"""
                 peaks = {sun}.get_column("sunspots").find_each_peak_that(is_at_least=100)
                 {{"peaks": len(peaks), "first position": peaks.get_cell_at(row=1, column="position"),
                  "sum of positions": peaks.get_column("position").find_total(),
                  "highest": peaks.get_column("value").find_biggest()}}
             """,
             parent="""
                 from scipy import signal
                 x = data["sunspots"].to_numpy()
                 found, _ = signal.find_peaks(x, height=100)
                 {"peaks": len(found), "first position": found[0] + 1, "sum of positions": (found + 1).sum(),
                  "highest": x[found].max()}
             """, parent_label="SciPy signal.find_peaks", parent_tolerance=0,
             r="""
                 x <- sunspots
                 i <- which(diff(sign(diff(x))) == -2) + 1
                 i <- i[x[i] >= 100]
                 list(peaks = length(i), `first position` = i[1], `sum of positions` = sum(i), highest = max(x[i]))
             """, r_tolerance=0, note="R: the readings higher than both neighbours, written out in base R."),
        Case("nums.find_each_dip_that", "the yearly sunspot numbers: the solar minima of at most 5", SUNSPOTS,
             "real data",
             ours=f"""
                 dips = {sun}.get_column("sunspots").find_each_dip_that(is_at_most=5)
                 {{"dips": len(dips), "first position": dips.get_cell_at(row=1, column="position"),
                  "sum of positions": dips.get_column("position").find_total(),
                  "biggest stands out by": dips.get_column("stands out by").find_biggest()}}
             """,
             parent="""
                 from scipy import signal
                 x = data["sunspots"].to_numpy()
                 found, props = signal.find_peaks(-x, height=-5, prominence=(None, None))
                 {"dips": len(found), "first position": found[0] + 1, "sum of positions": (found + 1).sum(),
                  "biggest stands out by": props["prominences"].max()}
             """, parent_label="SciPy signal.find_peaks on minus the numbers", parent_tolerance=1e-12),
        Case("table.find_each_dip_that", "the yearly sunspot numbers: the years of the solar minima of at most 5",
             SUNSPOTS, "real data",
             ours=f"""
                 dips = {sun}.find_each_dip_that("sunspots", sorted_by="year", is_at_most=5)
                 {{"dips": len(dips), "first year": dips.get_cell_at(row=1, column="year"),
                  "last year": dips.get_cell_at(row=len(dips), column="year")}}
             """,
             parent="""
                 from scipy import signal
                 found, _ = signal.find_peaks(-data["sunspots"].to_numpy(), height=-5)
                 years = data["year"].to_numpy()[found]
                 {"dips": len(found), "first year": years[0], "last year": years[-1]}
             """, parent_label="SciPy signal.find_peaks on minus the numbers", parent_tolerance=0),
        Case("draw_peak_dots", "the yearly sunspot numbers: dots on the maxima of at least 150", SUNSPOTS, "real data",
             ours=f"""
                 chart = {sun}.start_chart().draw_lines(x="year", y="sunspots").peak_dots(is_at_least=150)
                 dots = sdata.table(chart.get_numbers_drawn()).keep_rows_where("kind", is_equal_to="dot")
                 {{"dots": len(dots), "first year": dots.get_cell_at(row=1, column="x"),
                  "sum of years": dots.get_column("x").find_total(), "highest": dots.get_column("y").find_biggest()}}
             """,
             parent="""
                 from scipy import signal
                 x = data["sunspots"].to_numpy()
                 found, _ = signal.find_peaks(x, height=150)
                 years = data["year"].to_numpy()[found]
                 {"dots": len(found), "first year": years[0], "sum of years": years.sum(), "highest": x[found].max()}
             """, parent_label="SciPy signal.find_peaks", parent_tolerance=0,
             r="""
                 i <- which(diff(sign(diff(sunspots))) == -2) + 1
                 i <- i[sunspots[i] >= 150]
                 list(dots = length(i), `first year` = year[i[1]], `sum of years` = sum(year[i]),
                      highest = max(sunspots[i]))
             """, r_tolerance=0),
        # ---- the Fourier transform and the Hilbert envelope
        Case("nums.take_fourier_transform", "the yearly sunspot numbers: size and phase of the 11-year wave",
             SUNSPOTS, "real data",
             ours=f"""
                 waves = {sun}.get_column("sunspots").take_fourier_transform(time_step=1)
                 {{"size at 28 / 309": waves.get_cell_at(row=29, column="size"),
                  "phase at 28 / 309": waves.get_cell_at(row=29, column="phase"),
                  "total of the sizes": waves.get_column("size").find_total()}}
             """,
             parent="""
                 import numpy as np
                 f = np.fft.rfft(data["sunspots"].to_numpy())
                 {"size at 28 / 309": abs(f[28]), "phase at 28 / 309": np.degrees(np.angle(f[28])),
                  "total of the sizes": np.abs(f).sum()}
             """, parent_label="NumPy fft.rfft", parent_tolerance=1e-9,
             r="""
                 f <- fft(sunspots)
                 list(`size at 28 / 309` = Mod(f[29]), `phase at 28 / 309` = Arg(f[29]) * 180 / pi,
                      `total of the sizes` = sum(Mod(f[1:155])))
             """, r_tolerance=1e-9),
        Case("sdata.find_inverse_fourier_transform", "the yearly sunspot numbers there and back", SUNSPOTS,
             "real data",
             ours=f"""
                 back = sdata.find_inverse_fourier_transform({sun}.get_column("sunspots").take_fourier_transform())
                 {{"numbers": back.count(), "1957 (position 258)": back.get_number_at(258), "total": back.find_total()}}
             """,
             parent="""
                 {"numbers": len(data), "1957 (position 258)": data["sunspots"].to_numpy()[257],
                  "total": data["sunspots"].sum()}
             """, parent_label="the numbers themselves", parent_tolerance=1e-12,
             r="""
                 back <- Re(fft(fft(sunspots), inverse = TRUE)) / length(sunspots)
                 list(numbers = length(back), `1957 (position 258)` = back[258], total = sum(back))
             """, r_tolerance=1e-12),
        Case("nums.find_envelope", "the yearly sunspot numbers: the envelope of the solar cycle", SUNSPOTS,
             "real data",
             ours=f"""
                 envelope = {sun}.get_column("sunspots").find_envelope()
                 {{"first": envelope.get_number_at(1), "1957 (position 258)": envelope.get_number_at(258),
                  "total": envelope.find_total()}}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 e = np.abs(signal.hilbert(data["sunspots"].to_numpy()))
                 {"first": e[0], "1957 (position 258)": e[257], "total": e.sum()}
             """, parent_label="SciPy signal.hilbert", parent_tolerance=1e-9,
             r="""
                 n <- length(sunspots); h <- numeric(n); h[1] <- 1; h[2:((n + 1) / 2)] <- 2   # n is odd
                 e <- Mod(fft(fft(sunspots) * h, inverse = TRUE) / n)
                 list(first = e[1], `1957 (position 258)` = e[258], total = sum(e))
             """, r_tolerance=1e-9, note="R: the analytic signal written out with base R fft (as gsignal::hilbert)."),
        Case("table.add_envelope_column", "the yearly sunspot numbers: the envelope as a new column, by year",
             SUNSPOTS, "real data",
             ours=f"""
                 table = {sun}
                 table.add_envelope_column("envelope", from_column="sunspots", sorted_by="year")
                 envelope = table.get_column("envelope")
                 {{"1957 (row 258)": envelope.get_number_at(258), "last": envelope.get_number_at(309),
                  "total": envelope.find_total()}}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 e = np.abs(signal.hilbert(data["sunspots"].to_numpy()))
                 {"1957 (row 258)": e[257], "last": e[-1], "total": e.sum()}
             """, parent_label="SciPy signal.hilbert", parent_tolerance=1e-9,
             r="""
                 n <- length(sunspots); h <- numeric(n); h[1] <- 1; h[2:((n + 1) / 2)] <- 2   # n is odd
                 e <- Mod(fft(fft(sunspots) * h, inverse = TRUE) / n)
                 list(`1957 (row 258)` = e[258], last = e[n], total = sum(e))
             """, r_tolerance=1e-9,
             note="The phase (show=\"phase\") is not compared here: the sunspot phase has a step of exactly half a "
                  "turn, where the last digit of the Fourier transform decides whether unwrapping adds or takes off "
                  "360 degrees."),
        # ---- convolution and resampling
        Case("nums.convolve_with", "the yearly sunspot numbers, weighted with 0.5, 0.3 and 0.2", SUNSPOTS,
             "real data",
             ours=f"""
                 out = {sun}.get_column("sunspots").convolve_with([0.5, 0.3, 0.2])
                 {{"numbers": out.count(), "third": out.get_number_at(3), "total": out.find_total()}}
             """,
             parent="""
                 import numpy as np
                 c = np.convolve(data["sunspots"].to_numpy(), [0.5, 0.3, 0.2])
                 {"numbers": len(c), "third": c[2], "total": c.sum()}
             """, parent_label="NumPy convolve", parent_tolerance=1e-12,
             r="""
                 c <- convolve(sunspots, rev(c(0.5, 0.3, 0.2)), type = "open")
                 list(numbers = length(c), third = c[3], total = sum(c))
             """, r_tolerance=1e-9),
        Case("nums.deconvolve_by", "the yearly sunspot numbers divided by 1 - 0.5 z (polynomial division)",
             SUNSPOTS, "real data",
             ours=f"""
                 out = {sun}.get_column("sunspots").deconvolve_by([1, -0.5])
                 {{"numbers": out.count(), "last": out.get_number_at(out.count()), "total": out.find_total()}}
             """,
             parent="""
                 from scipy import signal
                 q, _ = signal.deconvolve(data["sunspots"].to_numpy(), [1, -0.5])
                 {"numbers": len(q), "last": q[-1], "total": q.sum()}
             """, parent_label="SciPy signal.deconvolve", parent_tolerance=1e-12,
             r="""
                 x <- sunspots; q <- numeric(length(x) - 1); q[1] <- x[1]
                 for (i in 2:length(q)) q[i] <- x[i] + 0.5 * q[i - 1]   # long division by 1 - 0.5 z
                 list(numbers = length(q), last = q[length(q)], total = sum(q))
             """, r_tolerance=1e-9),
        Case("nums.change_time_step", "the yearly sunspot numbers, one reading every 2 years (Fourier)",
             SUNSPOTS, "real data",
             ours=f"""
                 out = {sun}.get_column("sunspots").change_time_step(to=2, time_step=1)
                 {{"numbers": out.count(), "first": out.get_number_at(1), "total": out.find_total()}}
             """,
             parent="""
                 from scipy import signal
                 r = signal.resample(data["sunspots"].to_numpy(), 154)
                 {"numbers": len(r), "first": r[0], "total": r.sum()}
             """, parent_label="SciPy signal.resample", parent_tolerance=1e-9),
        # ---- filters
        Case("nums.keep_each_frequency_that", "the yearly sunspot numbers: the cycles slower than 20 years",
             SUNSPOTS, "real data",
             ours=f"""
                 slow = {sun}.get_column("sunspots").keep_each_frequency_that(is_below=0.05, time_step=1)
                 {{"first": slow.get_number_at(1), "1957 (position 258)": slow.get_number_at(258),
                  "total": slow.find_total()}}
             """,
             parent="""
                 from scipy import signal
                 sos = signal.butter(4, 0.05, btype="lowpass", fs=1.0, output="sos")
                 y = signal.sosfiltfilt(sos, data["sunspots"].to_numpy())
                 {"first": y[0], "1957 (position 258)": y[257], "total": y.sum()}
             """, parent_label="SciPy signal.butter and sosfiltfilt", parent_tolerance=1e-9),
        Case("nums.remove_each_frequency_that", "the yearly sunspot numbers without the 9 to 14-year band",
             SUNSPOTS, "real data",
             ours=f"""
                 rest = {sun}.get_column("sunspots").remove_each_frequency_that(is_between=[0.07, 0.11], time_step=1)
                 {{"first": rest.get_number_at(1), "1957 (position 258)": rest.get_number_at(258),
                  "total": rest.find_total()}}
             """,
             parent="""
                 from scipy import signal
                 sos = signal.butter(4, [0.07, 0.11], btype="bandstop", fs=1.0, output="sos")
                 y = signal.sosfiltfilt(sos, data["sunspots"].to_numpy())
                 {"first": y[0], "1957 (position 258)": y[257], "total": y.sum()}
             """, parent_label="SciPy signal.butter and sosfiltfilt", parent_tolerance=1e-9),
        Case("table.add_filtered_column", "both_ways=False: the yearly sunspot numbers, a forward low-pass filter",
             SUNSPOTS, "real data", option="both_ways=False",
             ours=f"""
                 table = {sun}
                 table.add_filtered_column("slow", from_column="sunspots", keep_below=0.05, sorted_by="year",
                                           both_ways=False)
                 slow = table.get_column("slow")
                 {{"first": slow.get_number_at(1), "1957 (position 258)": slow.get_number_at(258),
                  "total": slow.find_total()}}
             """,
             parent="""
                 from scipy import signal
                 sos = signal.butter(4, 0.05, btype="lowpass", fs=1.0, output="sos")
                 y = signal.sosfilt(sos, data["sunspots"].to_numpy())
                 {"first": y[0], "1957 (position 258)": y[257], "total": y.sum()}
             """, parent_label="SciPy signal.butter and sosfilt", parent_tolerance=1e-9),
        Case("sdata.frequency_filter", "the low-pass filter of the sunspot cases (below 0.05 a year): its poles",
             CHECKS, "real data",
             ours="""
                 poles = sdata.frequency_filter(keep_below=0.05, time_step=1).poles()
                 size = poles.get_column("distance from 0")
                 {"poles": len(poles), "smallest distance": size.find_smallest(), "biggest distance": size.find_biggest(),
                  "steady gain": sdata.frequency_filter(keep_below=0.05, time_step=1).steady_gain()}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 z, p, k = signal.butter(4, 0.05, fs=1.0, output="zpk")
                 {"poles": len(p), "smallest distance": np.abs(p).min(), "biggest distance": np.abs(p).max(),
                  "steady gain": (k * np.prod(1 - z) / np.prod(1 - p)).real}
             """, parent_label="SciPy signal.butter", parent_tolerance=1e-9,
             r="""
                 n <- 4; w <- 4 * tan(pi * 0.1 / 2)                     # prewarped, as the bilinear transform needs
                 s <- w * exp(1i * pi * (2 * (1:n) + n - 1) / (2 * n))  # Butterworth's analog poles
                 z <- (4 + s) / (4 - s)                                 # bilinear transform (fs = 2 for Wn = 0.1)
                 list(poles = n, `smallest distance` = min(Mod(z)), `biggest distance` = max(Mod(z)))
             """, r_tolerance=1e-9, note="R: Butterworth's poles and the bilinear transform written out in base R."),
        # ---- the time-series chart words
        Case("draw_autocorrelation_bars", "the yearly sunspot numbers: the correlation with 1 to 24 years back",
             SUNSPOTS, "real data",
             ours=f"""
                 chart = {sun}.start_chart().autocorrelation_bars("sunspots", sorted_by="year")
                 bars = sdata.table(chart.get_numbers_drawn()).keep_rows_where("kind", is_equal_to="dot")
                 {{"bars": len(bars), "1 year back": bars.get_cell_at(row=1, column="y"),
                  "11 years back": bars.get_cell_at(row=11, column="y"), "24 years back": bars.get_cell_at(row=24, column="y")}}
             """,
             parent="""
                 from statsmodels.tsa.stattools import acf
                 a = acf(data["sunspots"].to_numpy(), nlags=24)
                 {"bars": 24, "1 year back": a[1], "11 years back": a[11], "24 years back": a[24]}
             """, parent_label="statsmodels acf", parent_tolerance=1e-9,
             r="""
                 a <- acf(sunspots, lag.max = 24, plot = FALSE)$acf
                 list(bars = length(a) - 1, `1 year back` = a[2], `11 years back` = a[12], `24 years back` = a[25])
             """, r_tolerance=1e-9),
        Case("draw_cross_correlation_bars", "US inflation and unemployment: shifts of -4 to 4 quarters", MACRO,
             "real data",
             ours="""
                 chart = sdata.table(data).start_chart().cross_correlation_bars("infl", "unemp", sorted_by="quarter",
                                                                                 rows_back=4)
                 bars = sdata.table(chart.get_numbers_drawn()).keep_rows_where("kind", is_equal_to="dot")
                 {"bars": len(bars), "shift -4": bars.get_cell_at(row=1, column="y"),
                  "shift 0": bars.get_cell_at(row=5, column="y"), "shift 4": bars.get_cell_at(row=9, column="y")}
             """,
             r="""
                 a <- ccf(infl, unemp, lag.max = 4, plot = FALSE)$acf   # R lags -4 to 4; shift s is R's lag -s
                 list(bars = length(a), `shift -4` = a[9], `shift 0` = a[5], `shift 4` = a[1])
             """, r_tolerance=1e-9,
             parent="""
                 import numpy as np
                 x, y = data["infl"].to_numpy(), data["unemp"].to_numpy()
                 n = len(x); x, y = x - x.mean(), y - y.mean()
                 c = lambda s: (x[:n - s] * y[s:]).sum() / n / (x.std() * y.std()) if s >= 0 else \\
                     (x[-s:] * y[:n + s]).sum() / n / (x.std() * y.std())
                 {"bars": 9, "shift -4": c(-4), "shift 0": c(0), "shift 4": c(4)}
             """, parent_label="the cross-correlation written out in NumPy (as R ccf)", parent_tolerance=1e-9),
        Case("draw_lag_dots", "the yearly sunspot numbers against the year before", SUNSPOTS, "real data",
             ours=f"""
                 chart = {sun}.start_chart().lag_dots("sunspots", sorted_by="year", rows_back=1)
                 dots = sdata.table(chart.get_numbers_drawn()).keep_rows_where("kind", is_equal_to="dot")
                 {{"dots": len(dots), "sum of the year before": dots.get_column("x").find_total(),
                  "sum of the year itself": dots.get_column("y").find_total()}}
             """,
             parent="""
                 x = data["sunspots"].to_numpy()
                 {"dots": len(x) - 1, "sum of the year before": x[:-1].sum(), "sum of the year itself": x[1:].sum()}
             """, parent_label="NumPy (the pairs themselves)", parent_tolerance=1e-12,
             r="""
                 n <- length(sunspots)
                 list(dots = n - 1, `sum of the year before` = sum(sunspots[-n]), `sum of the year itself` = sum(sunspots[-1]))
             """, r_tolerance=1e-12),
        Case("draw_trend_and_season", "El Nino sea temperatures: the trend panel (season window 7)", ELNINO, "real data",
             ours="""
                 chart = sdata.table(data).start_chart().trend_and_season(x="month", y="temperature", repeats_every=12)
                 trend = sdata.table(chart.get_numbers_drawn()).keep_rows_where("panel", is_equal_to=2)
                 season = sdata.table(chart.get_numbers_drawn()).keep_rows_where("panel", is_equal_to=3)
                 {"trend points": len(trend), "first trend": trend.get_cell_at(row=1, column="y"),
                  "total trend": trend.get_column("y").find_total(), "first season": season.get_cell_at(row=1, column="y")}
             """,
             r="""
                 s <- stl(ts(temperature, frequency = 12), s.window = 7)$time.series
                 list(`trend points` = nrow(s), `first trend` = s[1, "trend"], `total trend` = sum(s[, "trend"]),
                      `first season` = s[1, "seasonal"])
             """, r_tolerance=1e-9),
        Case("draw_forecast", "El Nino sea temperatures: the next 12 months by Holt-Winters, drawn after the line",
             ELNINO, "real data", ours_r=("forecast",),
             ours="""
                 chart = sdata.table(data).start_chart().draw_lines(x="month", y="temperature")
                 chart.draw_forecast(steps_ahead=12, repeats_every=12)
                 drawn = sdata.table(chart.get_numbers_drawn()).keep_rows_where("x", is_above=732)
                 line = sdata.table(drawn).keep_rows_where("kind", is_equal_to="line")
                 {"forecast points": len(line), "first month": line.get_cell_at(row=1, column="y"),
                  "twelfth month": line.get_cell_at(row=12, column="y")}
             """,
             r="""
                 f <- predict(HoltWinters(ts(temperature, frequency = 12)), n.ahead = 12)
                 list(`forecast points` = length(f), `first month` = f[1], `twelfth month` = f[12])
             """, r_tolerance=1e-9,
             note="simplydata runs R HoltWinters through forecast::forecast; the reference is HoltWinters' own "
                  "predict() in base R."),
        # ---- joining the dots
        Case("table.find_values_at", "the yearly sunspot numbers between the years, by straight lines", SUNSPOTS,
             "real data",
             ours=f"""
                 found = {sun}.find_values_at("sunspots", at={{"year": [1700.5, 1850.25, 2007.9]}})
                 {{"1700.5": found.get_cell_at(row=1, column="sunspots"), "1850.25": found.get_cell_at(row=2, column="sunspots"),
                  "2007.9": found.get_cell_at(row=3, column="sunspots")}}
             """,
             parent="""
                 import numpy as np
                 v = np.interp([1700.5, 1850.25, 2007.9], data["year"], data["sunspots"])
                 {"1700.5": v[0], "1850.25": v[1], "2007.9": v[2]}
             """, parent_label="NumPy interp", parent_tolerance=1e-12,
             r="""
                 v <- approx(year, sunspots, xout = c(1700.5, 1850.25, 2007.9))$y
                 list(`1700.5` = v[1], `1850.25` = v[2], `2007.9` = v[3])
             """, r_tolerance=1e-12),
        Case("table.make_map_of", "the yearly sunspot numbers at 5 evenly spaced years", SUNSPOTS, "real data",
             ours=f"""
                 found = {sun}.make_map_of("sunspots", across=["year"], steps=5)
                 {{"places": len(found), "second place": found.get_cell_at(row=2, column="sunspots"),
                  "total": found.get_column("sunspots").find_total()}}
             """,
             parent="""
                 import numpy as np
                 v = np.interp(np.linspace(1700, 2008, 5), data["year"], data["sunspots"])
                 {"places": len(v), "second place": v[1], "total": v.sum()}
             """, parent_label="NumPy interp on linspace", parent_tolerance=1e-12,
             r="""
                 v <- approx(year, sunspots, xout = seq(min(year), max(year), length.out = 5))$y
                 list(places = length(v), `second place` = v[2], total = sum(v))
             """, r_tolerance=1e-12),
        # ---- solving and optimising: published worked examples
        Case("sdata.solve", "Newton's cubic x^3 - 2x = 5 between 0 and 3", NEWTON, "published",
             ours="""
                 found = sdata.solve("x**3 - 2*x = 5", between=[0, 3])
                 {"x": found.get_cell_at(row=1, column="x"), "solutions": len(found)}
             """,
             published={"x": (2.09455148, 5e-9, "Newton (1669), as printed by Ypma (1995)"),
                        "solutions": (1, 0, "exact")},
             parent="""
                 from scipy import optimize
                 {"x": optimize.brentq(lambda x: x ** 3 - 2 * x - 5, 0, 3, xtol=1e-14), "solutions": 1}
             """, parent_label="SciPy optimize.brentq", parent_tolerance=1e-12,
             r="""
                 list(x = uniroot(function(x) x^3 - 2 * x - 5, c(0, 3), tol = 1e-14)$root, solutions = 1)
             """, r_tolerance=1e-12),
        Case("sdata.find_where_smallest", "Rosenbrock's valley from (-1.2, 1) by Nelder-Mead", ROSENBROCK,
             "published",
             ours="""
                 found = sdata.find_where_smallest("100*(y - x**2)**2 + (1 - x)**2", start={"x": -1.2, "y": 1})
                 {"x": found.get_cell_at(row=1, column="x"), "y": found.get_cell_at(row=1, column="y")}
             """,
             published={"x": (1.0, 1e-4, "Rosenbrock (1960)"), "y": (1.0, 1e-4, "Rosenbrock (1960)")},
             parent="""
                 from scipy import optimize
                 f = lambda p: 100 * (p[1] - p[0] ** 2) ** 2 + (1 - p[0]) ** 2
                 r = optimize.minimize(f, [-1.2, 1], method="Nelder-Mead",
                                       options={"xatol": 1e-10, "fatol": 1e-14, "maxiter": 10000})
                 {"x": r.x[0], "y": r.x[1]}
             """, parent_label="SciPy optimize.minimize (Nelder-Mead, run to 1e-10)", parent_tolerance=1e-6,
             r="""
                 o <- optim(c(-1.2, 1), function(p) 100 * (p[2] - p[1]^2)^2 + (1 - p[1])^2,
                            control = list(reltol = 1e-14, maxit = 10000))
                 list(x = o$par[1], y = o$par[2])
             """, r_tolerance=1e-3,
             note="Nelder-Mead stops by its own rule: SciPy run to 1e-10 agrees to 1e-6; R optim's Nelder-Mead "
                  "stops near the valley floor and agrees to 1e-3, the size of the step at which it stops."),
        Case("sdata.find_where_biggest", "the Wyndor Glass product mix (a linear program)", WYNDOR, "published",
             ours="""
                 found = sdata.find_where_biggest("3*x1 + 5*x2", rules=["x1 <= 4", "2*x2 <= 12", "3*x1 + 2*x2 <= 18",
                                                                        "x1 >= 0", "x2 >= 0"])
                 {"x1": found.get_cell_at(row=1, column="x1"), "x2": found.get_cell_at(row=1, column="x2"),
                  "profit": found.get_cell_at(row=1, column="biggest value"),
                  "shadow price of plant 2": found.get_cell_at(row=1, column="value of one more: 2*x2 <= 12"),
                  "shadow price of plant 3": found.get_cell_at(row=1, column="value of one more: 3*x1 + 2*x2 <= 18")}
             """,
             published={"x1": (2, 1e-9, "Hillier & Lieberman (2015)"), "x2": (6, 1e-9, "Hillier & Lieberman (2015)"),
                        "profit": (36, 1e-9, "Hillier & Lieberman (2015)"),
                        "shadow price of plant 2": (1.5, 1e-9, "Hillier & Lieberman (2015)"),
                        "shadow price of plant 3": (1, 1e-9, "Hillier & Lieberman (2015)")},
             parent="""
                 from scipy import optimize
                 r = optimize.linprog([-3, -5], A_ub=[[1, 0], [0, 2], [3, 2]], b_ub=[4, 12, 18], method="highs")
                 {"x1": r.x[0], "x2": r.x[1], "profit": -r.fun, "shadow price of plant 2": -r.ineqlin.marginals[1],
                  "shadow price of plant 3": -r.ineqlin.marginals[2]}
             """, parent_label="SciPy optimize.linprog (HiGHS)", parent_tolerance=1e-9),
        # ---- waves and windows (formulas, no data)
        Case("sdata.make_wave", "a sine wave of 5 cycles per second, 100 readings 0.01 apart", CHECKS, "real data",
             ours="""
                 wave = sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=100)
                 {"readings": wave.count(), "third": wave.get_number_at(3), "biggest": wave.find_biggest(),
                  "total of squares": wave.raise_to_power(2).find_total()}
             """,
             parent="""
                 import numpy as np
                 w = np.sin(2 * np.pi * 5 * np.arange(100) * 0.01)
                 {"readings": len(w), "third": w[2], "biggest": w.max(), "total of squares": (w ** 2).sum()}
             """, parent_label="NumPy sin", parent_tolerance=1e-12,
             r="""
                 w <- sin(2 * pi * 5 * (0:99) * 0.01)
                 list(readings = length(w), third = w[3], biggest = max(w), `total of squares` = sum(w^2))
             """, r_tolerance=1e-12),
        Case("sdata.make_window_shape", "the symmetric Hann window of 64 weights", CHECKS, "real data",
             ours="""
                 w = sdata.make_window_shape("hann", how_many=64)
                 {"weights": w.count(), "second": w.get_number_at(2), "total": w.find_total()}
             """,
             parent="""
                 import numpy as np
                 w = np.hanning(64)
                 {"weights": len(w), "second": w[1], "total": w.sum()}
             """, parent_label="NumPy hanning", parent_tolerance=1e-12,
             r="""
                 w <- 0.5 - 0.5 * cos(2 * pi * (0:63) / 63)
                 list(weights = length(w), second = w[2], total = sum(w))
             """, r_tolerance=1e-12),
        # ---- linear systems: python-control and base R
        Case("sdata.system", "a system from its poles -1 and -2, zero -3 and gain 2", CHECKS, "real data",
             ours="""
                 numbers = sdata.system(poles=[-1, -2], zeros=[-3], gain=2).table()
                 {"numerator, s^0": numbers.get_cell_at(row=3, column="numerator"),
                  "numerator, s^1": numbers.get_cell_at(row=2, column="numerator"),
                  "denominator, s^1": numbers.get_cell_at(row=2, column="denominator"),
                  "denominator, s^0": numbers.get_cell_at(row=3, column="denominator")}
             """,
             parent="""
                 import control
                 g = control.zpk([-3], [-1, -2], 2)
                 num, den = g.num[0][0], g.den[0][0]
                 {"numerator, s^0": num[-1], "numerator, s^1": num[-2], "denominator, s^1": den[-2],
                  "denominator, s^0": den[-1]}
             """, parent_label="python-control zpk", parent_tolerance=1e-12,
             r=_r("""
                 num <- 2 * c(1, 3); den <- conv(c(1, 1), c(1, 2))
                 list(`numerator, s^0` = num[2], `numerator, s^1` = num[1], `denominator, s^1` = den[2],
                      `denominator, s^0` = den[3])
             """), r_tolerance=1e-12),
        Case("system.step_response", "1 / (s^2 + 2 s + 5): the answer to a step, 0 to 5 seconds", CHECKS,
             "real data",
             ours=f"""
                 step = sdata.system({G}).step_response(until=5, how_many=11)
                 {{"at 1.5": step.get_cell_at(row=4, column="output"), "at 5": step.get_cell_at(row=11, column="output"),
                  "total": step.get_column("output").find_total()}}
             """,
             parent=_with_g("""
                 import numpy as np
                 r = control.step_response(G, T=np.linspace(0, 5, 11))
                 y = np.asarray(r.outputs).reshape(-1)
                 {"at 1.5": y[3], "at 5": y[10], "total": y.sum()}
             """), parent_label="python-control step_response", parent_tolerance=1e-8,
             r=_r("""
                 y <- step_at(1, c(1, 2, 5), seq(0, 5, by = 0.5))
                 list(`at 1.5` = y[4], `at 5` = y[11], total = sum(y))
             """), r_tolerance=1e-8,
             note="R: the step response written out from the poles and residues of the formula."),
        Case("system.impulse_response", "1 / (s^2 + 2 s + 5): the answer to a kick, 0 to 5 seconds", CHECKS,
             "real data",
             ours=f"""
                 kick = sdata.system({G}).impulse_response(until=5, how_many=11)
                 {{"at 0.5": kick.get_cell_at(row=2, column="output"), "at 2": kick.get_cell_at(row=5, column="output"),
                  "total": kick.get_column("output").find_total()}}
             """,
             parent=_with_g("""
                 import numpy as np
                 r = control.impulse_response(G, T=np.linspace(0, 5, 11))
                 y = np.asarray(r.outputs).reshape(-1)
                 {"at 0.5": y[1], "at 2": y[4], "total": y.sum()}
             """), parent_label="python-control impulse_response", parent_tolerance=1e-8,
             r=_r("""
                 y <- impulse_at(1, c(1, 2, 5), seq(0, 5, by = 0.5))
                 list(`at 0.5` = y[2], `at 2` = y[5], total = sum(y))
             """), r_tolerance=1e-8),
        Case("system.response_to", "a first-order system (time constant 5 years) answering the sunspot numbers",
             SUNSPOTS, "real data",
             ours=f"""
                 table = {sun}
                 answer = sdata.system("1 / (5*s + 1)").response_to(table.get_column("sunspots"),
                                                                    time_points=table.get_column("year"))
                 {{"1957 (row 258)": answer.get_cell_at(row=258, column="output"),
                  "last": answer.get_cell_at(row=309, column="output"), "total": answer.get_column("output").find_total()}}
             """,
             parent="""
                 import control
                 import numpy as np
                 # each input holds for a year: the system sampled with a zero-order hold, then run year by year
                 d = control.sample_system(control.tf([1], [5, 1]), 1.0, method="zoh")
                 r = control.forced_response(d, T=np.arange(len(data), dtype=float), U=data["sunspots"].to_numpy())
                 y = np.asarray(r.outputs).reshape(-1)
                 {"1957 (row 258)": y[257], "last": y[-1], "total": y.sum()}
             """, parent_label="python-control sample_system (zoh) and forced_response", parent_tolerance=1e-9,
             r="""
                 a <- exp(-1 / 5); y <- numeric(length(sunspots))           # the input holds for each year
                 for (i in 2:length(y)) y[i] <- a * y[i - 1] + (1 - a) * sunspots[i - 1]
                 list(`1957 (row 258)` = y[258], last = y[length(y)], total = sum(y))
             """, r_tolerance=1e-9,
             note="Each input holds until the next year (zero order hold), as simplydata's response_to does; R "
                  "gives the exact answer of that, written out year by year."),
        Case("system.frequency_response", "1 / (s^2 + 2 s + 5): gain and phase from 0.1 to 10 radians a second",
             CHECKS, "real data",
             ours=f"""
                 bode = sdata.system({G}).frequency_response(between=[0.1, 10], how_many=5)
                 {{"gain at 1": bode.get_cell_at(row=3, column="gain"),
                  "phase at 3.16 (degrees)": bode.get_cell_at(row=4, column="phase (degrees)"),
                  "gain at 10 (dB)": bode.get_cell_at(row=5, column="gain (decibels)")}}
             """,
             parent=_with_g("""
                 import numpy as np
                 g = [complex(G(1j * w)) for w in (1.0, 10 ** 0.5, 10.0)]
                 {"gain at 1": abs(g[0]), "phase at 3.16 (degrees)": np.degrees(np.angle(g[1])),
                  "gain at 10 (dB)": 20 * np.log10(abs(g[2]))}
             """), parent_label="python-control (the formula at s = i w)", parent_tolerance=1e-9,
             r=_r("""
                 g <- pv(1, 1i * c(1, sqrt(10), 10)) / pv(c(1, 2, 5), 1i * c(1, sqrt(10), 10))
                 list(`gain at 1` = Mod(g[1]), `phase at 3.16 (degrees)` = Arg(g[2]) * 180 / pi,
                      `gain at 10 (dB)` = 20 * log10(Mod(g[3])))
             """), r_tolerance=1e-9),
        Case("system.poles", "(s^2 + 4 s + 13) / (s^3 + 3 s^2 + 7 s + 5): the poles -1 and -1 +/- 2i", CHECKS,
             "real data",
             ours="""
                 poles = sdata.system("(s**2 + 4*s + 13) / (s**3 + 3*s**2 + 7*s + 5)").poles()
                 {"poles": len(poles), "biggest imaginary part": poles.get_column("imaginary part").find_biggest(),
                  "total of the real parts": poles.get_column("real part").find_total(),
                  "smallest damping ratio": poles.get_column("damping ratio").find_smallest()}
             """,
             parent="""
                 import control
                 import numpy as np
                 p = control.poles(control.tf([1, 4, 13], [1, 3, 7, 5]))
                 {"poles": len(p), "biggest imaginary part": p.imag.max(), "total of the real parts": p.real.sum(),
                  "smallest damping ratio": (-p.real / np.abs(p)).min()}
             """, parent_label="python-control poles", parent_tolerance=1e-9,
             r=_r("""
                 p <- roots(c(1, 3, 7, 5))
                 list(poles = length(p), `biggest imaginary part` = max(Im(p)), `total of the real parts` = sum(Re(p)),
                      `smallest damping ratio` = min(-Re(p) / Mod(p)))
             """), r_tolerance=1e-9),
        Case("system.zeros", "(s^2 + 4 s + 13) / (s^3 + 3 s^2 + 7 s + 5): the zeros -2 +/- 3i", CHECKS,
             "real data",
             ours="""
                 zeros = sdata.system("(s**2 + 4*s + 13) / (s**3 + 3*s**2 + 7*s + 5)").zeros()
                 {"zeros": len(zeros), "biggest imaginary part": zeros.get_column("imaginary part").find_biggest(),
                  "distance from 0": zeros.get_cell_at(row=1, column="distance from 0")}
             """,
             parent="""
                 import control
                 import numpy as np
                 z = control.zeros(control.tf([1, 4, 13], [1, 3, 7, 5]))
                 {"zeros": len(z), "biggest imaginary part": z.imag.max(), "distance from 0": np.abs(z).max()}
             """, parent_label="python-control zeros", parent_tolerance=1e-9,
             r=_r("""
                 z <- roots(c(1, 4, 13))
                 list(zeros = length(z), `biggest imaginary part` = max(Im(z)), `distance from 0` = max(Mod(z)))
             """), r_tolerance=1e-9),
        Case("system.is_stable", "1 / (s^2 + 2 s + 5) is stable; 1 / (s^2 - s + 2) is not", CHECKS, "real data",
             ours=f"""
                 {{"stable one": float(sdata.system({G}).is_stable()),
                  "unstable one": float(sdata.system("1 / (s**2 - s + 2)").is_stable())}}
             """,
             parent="""
                 import control
                 {"stable one": float(all(control.poles(control.tf([1], [1, 2, 5])).real < 0)),
                  "unstable one": float(all(control.poles(control.tf([1], [1, -1, 2])).real < 0))}
             """, parent_label="python-control poles", parent_tolerance=0,
             r=_r("""
                 list(`stable one` = as.numeric(all(Re(roots(c(1, 2, 5))) < 0)),
                      `unstable one` = as.numeric(all(Re(roots(c(1, -1, 2))) < 0)))
             """), r_tolerance=0),
        Case("system.steady_gain", "(s^2 + 4 s + 13) / (s^3 + 3 s^2 + 7 s + 5) settles at 13 / 5", CHECKS,
             "real data",
             ours="""
                 {"steady gain": sdata.system("(s**2 + 4*s + 13) / (s**3 + 3*s**2 + 7*s + 5)").steady_gain()}
             """,
             parent="""
                 import control
                 {"steady gain": float(control.dcgain(control.tf([1, 4, 13], [1, 3, 7, 5])))}
             """, parent_label="python-control dcgain", parent_tolerance=1e-12,
             r=_r("""
                 list(`steady gain` = pv(c(1, 4, 13), 0) / pv(c(1, 3, 7, 5), 0))
             """), r_tolerance=1e-12),
        Case("system.in_steps", "1 / (s^2 + 2 s + 5) in steps of 0.1 (zero order hold)", CHECKS, "real data",
             ours=f"""
                 steps = sdata.system({G}).in_steps(time_step=0.1)
                 poles = steps.poles()
                 {{"distance of the poles from 0": poles.get_cell_at(row=1, column="distance from 0"),
                  "real part of the poles": poles.get_cell_at(row=1, column="real part"),
                  "steady gain": steps.steady_gain()}}
             """,
             parent=_with_g("""
                 import numpy as np
                 d = control.sample_system(G, 0.1, method="zoh")
                 p = control.poles(d)
                 {"distance of the poles from 0": np.abs(p).max(), "real part of the poles": p.real.max(),
                  "steady gain": float(control.dcgain(d))}
             """), parent_label="python-control sample_system (zoh)", parent_tolerance=1e-9,
             r=_r("""
                 z <- exp(roots(c(1, 2, 5)) * 0.1)   # a zero-order hold maps each pole p to exp(p T)
                 list(`distance of the poles from 0` = max(Mod(z)), `real part of the poles` = max(Re(z)),
                      `steady gain` = 1 / 5)
             """), r_tolerance=1e-9),
        Case("system.then", "1 / (s^2 + 2 s + 5), then 1 / (s + 3)", CHECKS, "real data",
             ours=f"""
                 numbers = sdata.system({G}).then(sdata.system("1 / (s + 3)")).table()
                 {{"denominator, s^2": numbers.get_cell_at(row=2, column="denominator"),
                  "denominator, s^1": numbers.get_cell_at(row=3, column="denominator"),
                  "denominator, s^0": numbers.get_cell_at(row=4, column="denominator"),
                  "numerator, s^0": numbers.get_cell_at(row=4, column="numerator")}}
             """,
             parent=_with_g("""
                 s = control.series(G, control.tf([1], [1, 3]))
                 num, den = s.num[0][0], s.den[0][0]
                 {"denominator, s^2": den[1], "denominator, s^1": den[2], "denominator, s^0": den[3],
                  "numerator, s^0": num[-1]}
             """), parent_label="python-control series", parent_tolerance=1e-12,
             r=_r("""
                 den <- conv(c(1, 2, 5), c(1, 3))
                 list(`denominator, s^2` = den[2], `denominator, s^1` = den[3], `denominator, s^0` = den[4],
                      `numerator, s^0` = 1)
             """), r_tolerance=1e-12),
        Case("system.add", "1 / (s^2 + 2 s + 5) and 1 / (s + 3) side by side", CHECKS, "real data",
             ours=f"""
                 numbers = sdata.system({G}).add(sdata.system("1 / (s + 3)")).table()
                 {{"numerator, s^2": numbers.get_cell_at(row=2, column="numerator"),
                  "numerator, s^1": numbers.get_cell_at(row=3, column="numerator"),
                  "numerator, s^0": numbers.get_cell_at(row=4, column="numerator"),
                  "denominator, s^0": numbers.get_cell_at(row=4, column="denominator")}}
             """,
             parent=_with_g("""
                 s = control.parallel(G, control.tf([1], [1, 3]))
                 num, den = s.num[0][0], s.den[0][0]
                 {"numerator, s^2": num[-3], "numerator, s^1": num[-2], "numerator, s^0": num[-1],
                  "denominator, s^0": den[-1]}
             """), parent_label="python-control parallel", parent_tolerance=1e-12,
             r=_r("""
                 num <- padd(conv(1, c(1, 3)), conv(1, c(1, 2, 5)))
                 list(`numerator, s^2` = num[1], `numerator, s^1` = num[2], `numerator, s^0` = num[3],
                      `denominator, s^0` = conv(c(1, 2, 5), c(1, 3))[4])
             """), r_tolerance=1e-12),
        Case("system.with_feedback", "10 / (s + 10) with 1 / (0.1 s + 1) in the feedback path", CHECKS,
             "real data",
             ours="""
                 loop = sdata.system("10 / (s + 10)").with_feedback(through=sdata.system("1 / (0.1*s + 1)"))
                 poles = loop.poles()
                 {"steady gain": loop.steady_gain(), "poles": len(poles),
                  "biggest distance of a pole from 0": poles.get_column("distance from 0").find_biggest()}
             """,
             parent="""
                 import control
                 import numpy as np
                 f = control.feedback(control.tf([10], [1, 10]), control.tf([1], [0.1, 1]))
                 p = control.poles(f)
                 {"steady gain": float(control.dcgain(f)), "poles": len(p),
                  "biggest distance of a pole from 0": np.abs(p).max()}
             """, parent_label="python-control feedback", parent_tolerance=1e-9,
             r=_r("""
                 # G / (1 + G H): top 10 (0.1 s + 1), bottom (s + 10)(0.1 s + 1) + 10
                 num <- conv(10, c(0.1, 1)); den <- padd(conv(c(1, 10), c(0.1, 1)), 10)
                 p <- roots(den)
                 list(`steady gain` = pv(num, 0) / pv(den, 0), poles = length(p),
                      `biggest distance of a pole from 0` = max(Mod(p)))
             """), r_tolerance=1e-9),
        Case("system.table", 'form="state space": 1 / (s^2 + 2 s + 5) in controller form', CHECKS, "real data",
             option='form="state space"',
             ours=f"""
                 m = sdata.system({G}).table(form="state space")
                 a = sdata.table(m).keep_rows_where("matrix", is_equal_to="A")
                 c = sdata.table(m).keep_rows_where("matrix", is_equal_to="C")
                 {{"A row 1, column 1": a.get_cell_at(row=1, column="value"),
                  "A row 1, column 2": a.get_cell_at(row=2, column="value"),
                  "A row 2, column 1": a.get_cell_at(row=3, column="value"),
                  "C column 2": c.get_cell_at(row=2, column="value")}}
             """,
             parent="""
                 from scipy import signal
                 A, B, C, D = signal.tf2ss([1], [1, 2, 5])
                 {"A row 1, column 1": A[0, 0], "A row 1, column 2": A[0, 1], "A row 2, column 1": A[1, 0],
                  "C column 2": C[0, 1]}
             """, parent_label="SciPy signal.tf2ss", parent_tolerance=1e-12,
             r="""
                 den <- c(1, 2, 5)   # controller form: the first row is minus the bottom's coefficients
                 list(`A row 1, column 1` = -den[2], `A row 1, column 2` = -den[3], `A row 2, column 1` = 1,
                      `C column 2` = 1)
             """, r_tolerance=1e-12),
        Case("system.chart", 'show="step": 1 / (s^2 + 2 s + 5), the step response drawn from 0 to 5', CHECKS,
             "real data", option='show="step"',
             ours=f"""
                 drawn = sdata.system({G}).chart(show="step", until=5).get_numbers_drawn()
                 line = sdata.table(drawn).keep_rows_where("layer", is_equal_to=1)
                 {{"points": len(line), "highest point": line.get_column("y").find_biggest(),
                  "last point": line.get_cell_at(row=len(line), column="y")}}
             """,
             parent=_with_g("""
                 import numpy as np
                 y = np.asarray(control.step_response(G, T=np.linspace(0, 5, 200)).outputs).reshape(-1)
                 {"points": len(y), "highest point": y.max(), "last point": y[-1]}
             """), parent_label="python-control step_response", parent_tolerance=1e-8,
             r=_r("""
                 y <- step_at(1, c(1, 2, 5), seq(0, 5, length.out = 200))
                 list(points = length(y), `highest point` = max(y), `last point` = y[200])
             """), r_tolerance=1e-8),
    ]


def add_to(namespace) -> None:
    """Add the datasets and cases to cases.py, and teach its load() the datasets read from statsmodels."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    namespace["CASES"].extend(_cases(Case))
    plain_load = namespace["load"]

    def load(name: str):
        if name in NO_DATA:
            return None
        if name in (SUNSPOTS, ELNINO, MACRO):
            return _load_statsmodels(name)
        return plain_load(name)

    namespace["load"] = load
