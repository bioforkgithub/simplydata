"""The reliability study for the families for 100 % plan, batches 17-18 (approved by Manish 2026-11-28): the
scipy.signal names of plan section 2.7 (FIR filters, the steepness found for the losses asked, the steady start,
analog filters, system forms, pole placement, group delay, spectra over time, the zoom FFT, waves, spline resampling
and phase locking), each run on real data where it takes data and compared with SciPy and, where R has the same
function, with R (signal, gsignal, base R).

cases_underneath.py loads this file and adds the cases. The series are the study's own: the level of Lake Huron
(1875-1972, one reading a year), the drivers killed or seriously injured in Great Britain (Seatbelts, 1969-1984,
monthly) and the air passengers (Box & Jenkins, 1949-1960). Systems and waves take no data: they are checked
against the answer worked out by hand from their formula (closed form) and against R. The simplydata side reads its
results only with simplydata words.
"""

from __future__ import annotations

LEVEL = 'sdata.number_list(data["level"])'
DRIVERS = 'sdata.number_list(data["drivers"])'


def cases(Case):
    return [
        # ---------------------------------------------------------------- FIR filters on Lake Huron
        Case("nums.keep_each_frequency_that", "the Lake Huron level: cycles slower than 10 years kept by a "
             "least-squares FIR filter of 21 weights", "Lake Huron", "real data",
             option='test_method="fir least squares"',
             ours=f"""
                 s = {LEVEL}.keep_each_frequency_that(is_below=0.1, time_step=1, test_method="fir least squares",
                                                       how_many_weights=21, transition_width=0.1)
                 {{"year 50": s.get_number_at(50), "year 40": s.get_number_at(40)}}
             """,
             parent="""
                 from scipy import signal
                 h = signal.firls(21, [0, 0.05, 0.15, 0.5], [1, 1, 0, 0], fs=1)
                 s = signal.filtfilt(h, [1.0], data["level"].to_numpy(dtype=float))
                 {"year 50": s[49], "year 40": s[39]}
             """, parent_label="SciPy signal.firls and filtfilt", parent_tolerance=1e-12,
             r="""
                 h <- gsignal::firls(20, c(0, 0.05, 0.15, 0.5) / 0.5, c(1, 1, 0, 0))
                 s <- gsignal::filtfilt(h, level)
                 list(`year 50` = s[50], `year 40` = s[40])
             """, r_packages=("gsignal",), r_tolerance=1e-9,
             note="R pads the ends differently (zeros, from rest), so the years compared are 40 and more years from "
                  "either end, where the 21 weights run twice never reach the padding."),
        Case("nums.keep_each_frequency_that", "the Lake Huron level: cycles slower than 10 years kept by an "
             "equiripple (Parks-McClellan) FIR filter of 21 weights", "Lake Huron", "real data",
             option='test_method="fir equiripple"',
             ours=f"""
                 s = {LEVEL}.keep_each_frequency_that(is_below=0.1, time_step=1, test_method="fir equiripple",
                                                       how_many_weights=21, transition_width=0.1)
                 {{"year 50": s.get_number_at(50), "year 45": s.get_number_at(45)}}
             """,
             parent="""
                 from scipy import signal
                 h = signal.remez(21, [0, 0.05, 0.15, 0.5], [1, 0], fs=1)
                 s = signal.filtfilt(h, [1.0], data["level"].to_numpy(dtype=float))
                 {"year 50": s[49], "year 45": s[44]}
             """, parent_label="SciPy signal.remez and filtfilt", parent_tolerance=1e-12,
             r="""
                 h <- signal::remez(20, c(0, 0.05, 0.15, 0.5) / 0.5, c(1, 1, 0, 0))
                 s <- signal::filtfilt(h, level)
                 list(`year 50` = s[50], `year 45` = s[45])
             """, r_packages=("signal",), r_tolerance=1e-9,
             note="As the least-squares case: the years compared are far enough from both ends."),
        Case("nums.keep_each_frequency_that", "the Lake Huron level: cycles slower than 10 years kept by a windowed "
             "FIR filter of 21 weights (SciPy firwin)", "Lake Huron", "real data", option='test_method="fir"',
             ours=f"""
                 s = {LEVEL}.keep_each_frequency_that(is_below=0.1, time_step=1, test_method="fir",
                                                       how_many_weights=21)
                 {{"first year": s.get_number_at(1), "year 50": s.get_number_at(50)}}
             """,
             parent="""
                 from scipy import signal
                 h = signal.firwin(21, 0.1, window="hamming", fs=1)
                 s = signal.filtfilt(h, [1.0], data["level"].to_numpy(dtype=float))
                 {"first year": s[0], "year 50": s[49]}
             """, parent_label="SciPy signal.firwin and filtfilt", parent_tolerance=1e-12,
             r="""
                 k <- -10:10; w <- 0.54 - 0.46 * cos(2 * pi * (0:20) / 20)
                 h <- 0.2 * ifelse(k == 0, 1, sin(pi * 0.2 * k) / (pi * 0.2 * k)) * w; h <- h / sum(h)
                 s <- stats::filter(stats::filter(level, h, sides = 2), h, sides = 2)
                 list(`year 50` = s[50])
             """, r_tolerance=1e-9,
             note="R signal::fir1 designs by frequency sampling (its weights for fir1(100, 0.1) add up to 1.0015), so "
                  "R is given firwin's formula itself: the windowed sinc, scaled to add up to 1, run twice in the "
                  "middle of the series."),
        Case("nums.keep_each_frequency_that", "the drivers killed or seriously injured: the cycles slower than a "
             "year kept by frequency sampling (51 weights)", "Seatbelts", "real data",
             option='test_method="fir frequency sampling"',
             ours=f"""
                 s = {DRIVERS}.keep_each_frequency_that(is_below=1, time_step=1 / 12,
                                                         test_method="fir frequency sampling", how_many_weights=51,
                                                         transition_width=0.24)
                 {{"month 96": s.get_number_at(96), "month 100": s.get_number_at(100)}}
             """,
             parent="""
                 from scipy import signal
                 h = signal.firwin2(51, [0, 0.88, 1.12, 6], [1, 1, 0, 0], fs=12)
                 s = signal.filtfilt(h, [1.0], data["drivers"].to_numpy(dtype=float))
                 {"month 96": s[95], "month 100": s[99]}
             """, parent_label="SciPy signal.firwin2 and filtfilt", parent_tolerance=1e-12,
             r="""
                 h <- gsignal::fir2(50, c(0, 0.88, 1.12, 6) / 6, c(1, 1, 0, 0), 64)
                 s <- gsignal::filtfilt(h, drivers)
                 list(`month 96` = s[96], `month 100` = s[100])
             """, r_packages=("gsignal",), r_tolerance=1e-9,
             note="R gsignal::fir2 is given SciPy's frequency grid (64 steps, 65 points for 51 weights)."),
        Case("nums.keep_each_frequency_that", "the drivers killed or seriously injured: the smallest Butterworth "
             "filter that keeps the cycles slower than a year and removes 40 dB from two a year on", "Seatbelts",
             "real data", option="find_order_for=",
             ours=f"""
                 s = {DRIVERS}.keep_each_frequency_that(is_below=1, time_step=1 / 12, find_order_for={{"loss_at": 2}})
                 f = sdata.frequency_filter(keep_below=1, time_step=1 / 12, find_order_for={{"loss_at": 2}})
                 {{"steepness": f.poles().count_rows(), "month 96": s.get_number_at(96)}}
             """,
             parent="""
                 from scipy import signal
                 n, wn = signal.buttord(1, 2, 0.5, 40, fs=12)
                 sos = signal.butter(n, wn, output="sos", fs=12)
                 s = signal.sosfiltfilt(sos, data["drivers"].to_numpy(dtype=float))
                 {"steepness": n, "month 96": s[95]}
             """, parent_label="SciPy signal.buttord, butter and sosfiltfilt", parent_tolerance=1e-10,
             r="""
                 b <- gsignal::buttord(1 / 6, 2 / 6, 0.5, 40)
                 list(steepness = b$n)
             """, r_packages=("gsignal",), r_tolerance=0,
             note="The steepness is the number of poles of the filter; R gsignal::buttord finds the same order."),
        Case("nums.keep_each_frequency_that", "the Lake Huron level filtered forwards only, starting in the steady "
             "state for 1875", "Lake Huron", "real data", option='start_from="first value"',
             ours=f"""
                 s = {LEVEL}.keep_each_frequency_that(is_below=0.1, time_step=1, both_ways=False,
                                                       start_from="first value")
                 {{"first year": s.get_number_at(1), "year 20": s.get_number_at(20)}}
             """,
             parent="""
                 from scipy import signal
                 x = data["level"].to_numpy(dtype=float)
                 sos = signal.butter(4, 0.1, output="sos", fs=1)
                 s = signal.sosfilt(sos, x, zi=signal.sosfilt_zi(sos) * x[0])[0]
                 {"first year": s[0], "year 20": s[19]}
             """, parent_label="SciPy signal.sosfilt with sosfilt_zi", parent_tolerance=1e-12,
             r="""
                 f <- gsignal::butter(4, 0.2)
                 s <- gsignal::filter(f, level, zi = gsignal::filter_zi(f) * level[1])$y
                 list(`first year` = s[1], `year 20` = s[20])
             """, r_packages=("gsignal",), r_tolerance=1e-8,
             note="R runs the same filter as one numerator and denominator, SciPy as second-order sections: they "
                  "agree to rounding."),
        Case("nums.keep_each_frequency_that", "the Lake Huron level by an FIR filter with the least delay (minimum "
             "phase), forwards only", "Lake Huron", "real data", option="with_least_delay=",
             ours=f"""
                 s = {LEVEL}.keep_each_frequency_that(is_below=0.1, time_step=1, test_method="fir", how_many_weights=21,
                                                       both_ways=False, with_least_delay=True)
                 {{"year 30": s.get_number_at(30), "last year": s.get_number_at(98)}}
             """,
             parent="""
                 from scipy import signal
                 h = signal.minimum_phase(signal.firwin(21, 0.1, fs=1), method="homomorphic", half=False)
                 s = signal.lfilter(h, [1.0], data["level"].to_numpy(dtype=float))
                 {"year 30": s[29], "last year": s[97]}
             """, parent_label="SciPy signal.minimum_phase and lfilter", parent_tolerance=1e-12),
        Case("nums.keep_each_frequency_that", "the drivers killed or seriously injured: the yearly cycle kept by a "
             "gammatone filter", "Seatbelts", "real data", option='test_method="gammatone"',
             ours=f"""
                 s = {DRIVERS}.keep_each_frequency_that(is_equal_to=1, time_step=1 / 12, test_method="gammatone")
                 {{"month 96": s.get_number_at(96)}}
             """,
             parent="""
                 from scipy import signal
                 b, a = signal.gammatone(1, "iir", fs=12)
                 s = signal.filtfilt(b, a, data["drivers"].to_numpy(dtype=float))
                 {"month 96": s[95]}
             """, parent_label="SciPy signal.gammatone and filtfilt", parent_tolerance=1e-10),
        # ---------------------------------------------------------------- filters and systems without data
        Case("sdata.frequency_filter", "the analog Butterworth filter that keeps the frequencies below 3: half the "
             "power at its cutoff", "closed form (no data)", "closed form", option="analog=",
             ours="""
                 f = sdata.frequency_filter(keep_below=3, analog=True)
                 g = f.frequency_response(between=[3, 6], how_many=2, unit="cycles per second")
                 t = f.table()
                 {"gain at 3": g.get_cell_at(row=1, column="gain"), "a1": t.get_cell_at(row=2, column="denominator"),
                  "b4": t.get_cell_at(row=5, column="numerator")}
             """,
             published={"gain at 3": (0.5 ** 0.5, 1e-12, "exact: a Butterworth filter passes 1 / sqrt(2) at its "
                                                          "cutoff")},
             parent="""
                 import numpy as np
                 from scipy import signal
                 z, p, k = signal.lp2lp_zpk(*signal.buttap(4), wo=2 * np.pi * 3)
                 b, a = signal.zpk2tf(z, p, k)
                 {"a1": a[1], "b4": b[-1]}
             """, parent_label="SciPy signal.buttap moved by lp2lp_zpk", parent_tolerance=1e-10,
             r="""
                 f <- gsignal::butter(4, 2 * pi * 3, "low", "s")
                 list(a1 = f$a[2] / f$a[1], b4 = f$b[length(f$b)] / f$a[1])
             """, r_packages=("gsignal",), r_tolerance=1e-9),
        Case("sdata.frequency_filter", "the drivers killed or seriously injured: the smallest elliptic filter that "
             "keeps the cycles slower than a year and removes 40 dB from two a year on, run on the series",
             "Seatbelts", "real data", option="find_order_for=",
             ours=f"""
                 f = sdata.frequency_filter(keep_below=1, time_step=1 / 12, test_method="elliptic",
                                            find_order_for={{"loss_at": 2}})
                 out = f.response_to({DRIVERS})
                 {{"steepness": f.poles().count_rows(), "month 96": out.get_cell_at(row=96, column="output")}}
             """,
             parent="""
                 from scipy import signal
                 n, wn = signal.ellipord(1, 2, 0.5, 40, fs=12)
                 sos = signal.ellip(n, 0.5, 40, wn, output="sos", fs=12)
                 {"steepness": n, "month 96": signal.sosfilt(sos, data["drivers"].to_numpy(dtype=float))[95]}
             """, parent_label="SciPy signal.ellipord, ellip and sosfilt", parent_tolerance=1e-10,
             r="""
                 list(steepness = gsignal::ellipord(1 / 6, 2 / 6, 0.5, 40)$n)
             """, r_packages=("gsignal",), r_tolerance=0),
        Case("nums.keep_each_frequency_that", "the Lake Huron level by a windowed FIR filter of 31 weights with a "
             "Blackman window", "Lake Huron", "real data", option="how_many_weights=",
             ours=f"""
                 s = {LEVEL}.keep_each_frequency_that(is_below=0.1, time_step=1, test_method="fir", how_many_weights=31,
                                                       window_shape="blackman")
                 {{"year 50": s.get_number_at(50)}}
             """,
             parent="""
                 from scipy import signal
                 h = signal.firwin(31, 0.1, window="blackman", fs=1)
                 {"year 50": signal.filtfilt(h, [1.0], data["level"].to_numpy(dtype=float))[49]}
             """, parent_label="SciPy signal.firwin and filtfilt", parent_tolerance=1e-12,
             r="""
                 k <- -15:15; h <- 0.2 * ifelse(k == 0, 1, sin(pi * 0.2 * k) / (pi * 0.2 * k)) * signal::blackman(31)
                 h <- h / sum(h)
                 s <- stats::filter(stats::filter(level, h, sides = 2), h, sides = 2)
                 list(`year 50` = s[50])
             """, r_packages=("signal",), r_tolerance=1e-9,
             note="firwin's formula written out in R with R signal's Blackman window, run twice in the middle."),
        Case("table.add_filtered_column", "the Lake Huron level: a column of the cycles slower than 10 years by an "
             "equiripple FIR filter", "Lake Huron", "real data", option='test_method="fir equiripple"',
             ours="""
                 t = sdata.table(data)
                 t.add_filtered_column("slow", from_column="level", keep_below=0.1, sorted_by="year",
                                       test_method="fir equiripple", how_many_weights=21, transition_width=0.1)
                 {"1924": t.get_cell_at(row=50, column="slow")}
             """,
             parent="""
                 from scipy import signal
                 h = signal.remez(21, [0, 0.05, 0.15, 0.5], [1, 0], fs=1)
                 s = signal.filtfilt(h, [1.0], data.sort_values("year")["level"].to_numpy(dtype=float))
                 {"1924": s[49]}
             """, parent_label="SciPy signal.remez and filtfilt", parent_tolerance=1e-12,
             r="""
                 s <- signal::filtfilt(signal::remez(20, c(0, 0.05, 0.15, 0.5) / 0.5, c(1, 1, 0, 0)), level)
                 list(`1924` = s[50])
             """, r_packages=("signal",), r_tolerance=1e-9),
        Case("system.table", "the drivers killed or seriously injured run through the sections of the filter that "
             "keeps the cycles slower than a year", "Seatbelts", "real data", option='form="sections"',
             ours=f"""
                 rows = sdata.frequency_filter(keep_below=1, time_step=1 / 12).table(form="sections")
                 out = sdata.system(sections=rows, time_step=1 / 12).response_to({DRIVERS})
                 {{"sections": rows.count_rows(), "month 96": out.get_cell_at(row=96, column="output")}}
             """,
             parent="""
                 from scipy import signal
                 sos = signal.butter(4, 1, output="sos", fs=12)
                 {"sections": len(sos), "month 96": signal.sosfilt(sos, data["drivers"].to_numpy(dtype=float))[95]}
             """, parent_label="SciPy signal.butter (sections) and sosfilt", parent_tolerance=1e-12,
             r="""
                 f <- gsignal::butter(4, 1 / 6)
                 list(`month 96` = gsignal::filter(f, drivers)[96])
             """, r_packages=("gsignal",), r_tolerance=1e-8,
             note="R runs the same filter as one numerator and denominator: it agrees to rounding."),
        Case("system.table", "(s + 3) / (s^2 + 3 s + 2) = 2 / (s + 1) - 1 / (s + 2)", "closed form (no data)",
             "closed form", option='form="partial fractions"',
             ours="""
                 t = sdata.system("(s + 3) / (s**2 + 3*s + 2)").table(form="partial fractions")
                 t.sort_by("pole (real part)")
                 {"residue at -2": t.get_cell_at(row=1, column="residue (real part)"),
                  "residue at -1": t.get_cell_at(row=2, column="residue (real part)")}
             """,
             published={"residue at -2": (-1.0, 1e-12, "exact: (s + 3) / (s + 1) at s = -2"),
                        "residue at -1": (2.0, 1e-12, "exact: (s + 3) / (s + 2) at s = -1")},
             r="""
                 r <- gsignal::residue(c(1, 3), c(1, 3, 2))
                 list(`residue at -2` = Re(r$r[Re(r$p) < -1.5]), `residue at -1` = Re(r$r[Re(r$p) > -1.5]))
             """, r_packages=("gsignal",), r_tolerance=1e-10),
        Case("sdata.system", "the fractions -1 / (s + 1) + 2 / (s + 2) added up: s / (s^2 + 3 s + 2)",
             "closed form (no data)", "closed form", option="residues=",
             ours="""
                 t = sdata.system(residues=[-1, 2], poles=[-1, -2]).table()
                 {"s": t.get_cell_at(row=2, column="numerator"), "1": t.get_cell_at(row=3, column="numerator"),
                  "bottom s": t.get_cell_at(row=2, column="denominator")}
             """,
             published={"s": (1.0, 1e-12, "exact"), "1": (0.0, 1e-12, "exact"), "bottom s": (3.0, 1e-12, "exact")},
             r="""
                 b <- gsignal::rresidue(c(-1, 2), c(-1, -2), NULL)
                 list(s = b$b[1], `1` = b$b[2], `bottom s` = b$a[2])
             """, r_packages=("gsignal",), r_tolerance=1e-10),
        Case("sdata.system", "two second-order sections multiplied out", "closed form (no data)", "closed form",
             option="sections=",
             ours="""
                 t = sdata.system(sections=[[1, 2, 1, 1, -0.5, 0.1], [1, 0, -1, 1, 0.2, 0.3]], time_step=0.01).table()
                 {"b1": t.get_cell_at(row=2, column="numerator"), "a2": t.get_cell_at(row=3, column="denominator"),
                  "a4": t.get_cell_at(row=5, column="denominator")}
             """,
             published={"b1": (2.0, 1e-12, "exact: (1 + 2 z + z^2)(1 - z^2), the z^3 term"),
                        "a2": (0.3, 1e-12, "exact: 0.3 + 0.1 - 0.5 x 0.2"),
                        "a4": (0.03, 1e-12, "exact: 0.1 x 0.3")},
             r="""
                 s <- gsignal::sos2tf(matrix(c(1, 2, 1, 1, -0.5, 0.1, 1, 0, -1, 1, 0.2, 0.3), 2, byrow = TRUE))
                 list(b1 = s$b[2], a2 = s$a[3], a4 = s$a[5])
             """, r_packages=("gsignal",), r_tolerance=1e-12),
        Case("system.move_poles_to", "1 / (s^2 + 2 s + 5) with its poles moved to -2 and -3: 1 / (s^2 + 5 s + 6)",
             "closed form (no data)", "closed form",
             ours="""
                 t = sdata.system("1 / (s**2 + 2*s + 5)").move_poles_to([-2, -3]).table()
                 {"s": t.get_cell_at(row=2, column="denominator"), "1": t.get_cell_at(row=3, column="denominator")}
             """,
             published={"s": (5.0, 1e-10, "exact: (s + 2)(s + 3)"), "1": (6.0, 1e-10, "exact: (s + 2)(s + 3)")},
             parent="""
                 from scipy import signal
                 a, b, c, d = signal.tf2ss([1], [1, 2, 5])
                 k = signal.place_poles(a, b, [-2, -3]).gain_matrix
                 den = signal.ss2tf(a - b @ k, b, c, d)[1]
                 {"s": den[1], "1": den[2]}
             """, parent_label="SciPy signal.place_poles", parent_tolerance=1e-10,
             note="R control::place gives other gains for this system (it warns that its poles are more than 10 % "
                  "off), so the closed form is the reference."),
        Case("system.frequency_response", "the delay of z / (z - 0.5), worked out by hand, and of the Butterworth "
             "filter that keeps 10 at 200 readings a second", "closed form (no data)", "closed form",
             option="with_delay=",
             ours="""
                 one = sdata.system("z / (z - 0.5)", time_step=1)
                 d = one.frequency_response(between=[0.125, 0.25], how_many=2, unit="cycles per second",
                                            with_delay=True)
                 f = sdata.frequency_filter(keep_below=10, time_step=0.005)
                 g = f.frequency_response(between=[1.5625, 25], how_many=2, with_delay=True)
                 {"first order at 1/8": d.get_cell_at(row=1, column="delay"),
                  "first order at 1/4": d.get_cell_at(row=2, column="delay"),
                  "delay at 1.5625": g.get_cell_at(row=1, column="delay"),
                  "delay at 25": g.get_cell_at(row=2, column="delay")}
             """,
             published={"first order at 1/8": ((0.5 * 0.5 ** 0.5 - 0.25) / (1.25 - 0.5 ** 0.5), 1e-12,
                                               "exact: (a cos w - a^2) / (1 - 2 a cos w + a^2), a = 0.5, w = pi / 4"),
                        "first order at 1/4": (-0.2, 1e-12, "exact: (0 - 0.25) / (1 + 0.25) at w = pi / 2")},
             parent="""
                 from scipy import signal
                 b, a = signal.sos2tf(signal.butter(4, 10, output="sos", fs=200))
                 d = signal.group_delay((b, a), w=[1.5625, 25], fs=200)[1] * 0.005
                 {"delay at 1.5625": d[0], "delay at 25": d[1]}
             """, parent_label="SciPy signal.group_delay", parent_tolerance=1e-9,
             r="""
                 g <- gsignal::grpdelay(gsignal::butter(4, 0.1), n = 512)
                 h <- gsignal::grpdelay(c(1, 0), c(1, -0.5), n = 512)
                 list(`delay at 1.5625` = g$gd[9] * 0.005, `delay at 25` = g$gd[129] * 0.005,
                      `first order at 1/8` = h$gd[129], `first order at 1/4` = h$gd[257])
             """, r_packages=("gsignal",), r_tolerance=1e-8,
             note="R's grid has 512 frequencies from 0 to half the readings per unit of time: 1.5625 and 25 per "
                  "second are its 9th and 129th, 1/8 and 1/4 per step its 129th and 257th."),
        # ---------------------------------------------------------------- spectra
        Case("nums.take_fourier_transform", "the drivers killed or seriously injured: the short-time Fourier "
             "transform in pieces of 48 months, and back", "Seatbelts", "real data", option="over_time=",
             ours=f"""
                 n = {DRIVERS}
                 t = n.take_fourier_transform(time_step=1 / 12, over_time=True, window=48)
                 back = sdata.find_inverse_fourier_transform(t)
                 {{"rows": t.count_rows(), "size of row 30": t.get_cell_at(row=30, column="size"),
                  "month 100 back": back.get_number_at(100)}}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 sft = signal.ShortTimeFFT(signal.get_window("hann", 48), hop=24, fs=12)
                 z = sft.stft(data["drivers"].to_numpy(dtype=float))
                 {"rows": z.size, "size of row 30": np.abs(z.T.ravel()[29]), "month 100 back": data["drivers"][99]}
             """, parent_label="SciPy signal.ShortTimeFFT.stft", parent_tolerance=1e-10),
        Case("nums.take_fourier_transform", "the Lake Huron level: the zoom FFT at the first 50 frequencies is R's "
             "fft there", "Lake Huron", "real data", option="between=",
             ours=f"""
                 t = {LEVEL}.take_fourier_transform(time_step=1, between=[0, 49 / 98], how_many=50)
                 {{"size at 0": t.get_cell_at(row=1, column="size"),
                  "size at 1/98": t.get_cell_at(row=2, column="size"),
                  "size at 10/98": t.get_cell_at(row=11, column="size")}}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 z = signal.zoom_fft(data["level"].to_numpy(dtype=float), [0, 49 / 98], m=50, fs=1, endpoint=True)
                 {"size at 0": abs(z[0]), "size at 1/98": abs(z[1]), "size at 10/98": abs(z[10])}
             """, parent_label="SciPy signal.zoom_fft", parent_tolerance=1e-10,
             r="""
                 z <- Mod(fft(level))
                 list(`size at 0` = z[1], `size at 1/98` = z[2], `size at 10/98` = z[11])
             """, r_tolerance=1e-9,
             note="98 yearly readings: the plain transform has a frequency every 1/98, so the zoom at those 50 "
                  "frequencies must give R's fft values there."),
        Case("nums.find_spectrum", "the drivers killed or seriously injured: the spectrum of each 48 months",
             "Seatbelts", "real data", option="over_time=",
             ours=f"""
                 t = {DRIVERS}.find_spectrum(time_step=1 / 12, over_time=True, window=48)
                 {{"rows": t.count_rows(), "power of row 26": t.get_cell_at(row=26, column="power")}}
             """,
             parent="""
                 from scipy import signal
                 f, t, p = signal.spectrogram(data["drivers"].to_numpy(dtype=float), fs=12, window="hann", nperseg=48,
                                              noverlap=24, detrend="constant", scaling="density", mode="psd")
                 {"rows": p.size, "power of row 26": p.T.ravel()[25]}
             """, parent_label="SciPy signal.spectrogram", parent_tolerance=1e-10),
        # ---------------------------------------------------------------- waves, resampling, phase locking
        Case("sdata.make_wave", "a maximum length sequence of 7 bits: 64 ones and 63 zeros in its 127 readings",
             "closed form (no data)", "closed form", option='shape="maximum length sequence"',
             ours="""
                 w = sdata.make_wave("maximum length sequence", time_step=0.01, how_many=127)
                 {"ones": w.find_total(), "readings": w.count()}
             """,
             published={"ones": (64.0, 0, "exact: a maximum length sequence of n bits has 2^(n-1) ones"),
                        "readings": (127.0, 0, "exact: 2^7 - 1")},
             parent="""
                 from scipy import signal
                 s = signal.max_len_seq(7)[0]
                 {"ones": s.sum(), "readings": len(s)}
             """, parent_label="SciPy signal.max_len_seq", parent_tolerance=0),
        Case("sdata.make_wave", "a sweep whose frequency is 2 t + 1: cos(2 pi (t^2 + t))", "closed form (no data)",
             "closed form", option='sweep="polynomial"',
             ours="""
                 w = sdata.make_wave("chirp", sweep="polynomial", frequency=[2, 1], time_step=0.01, how_many=300)
                 {"t = 1.37": w.get_number_at(138), "t = 2.99": w.get_number_at(300)}
             """,
             published={"t = 1.37": (0.019476642864966826, 1e-11, "exact: cos(2 pi (1.37^2 + 1.37))"),
                        "t = 2.99": (0.9050943988616084, 1e-11, "exact: cos(2 pi (2.99^2 + 2.99))")},
             r="""
                 t <- c(1.37, 2.99)
                 list(`t = 1.37` = cos(2 * pi * (t[1]^2 + t[1])), `t = 2.99` = cos(2 * pi * (t[2]^2 + t[2])))
             """, r_tolerance=1e-12),
        Case("nums.change_time_step", "the Lake Huron level every half year by a cubic spline through the yearly "
             "readings", "Lake Huron", "real data", option='test_method="cubic spline"',
             ours=f"""
                 s = {LEVEL}.change_time_step(to=0.5, time_step=1, test_method="cubic spline")
                 {{"readings": s.count(), "1876": s.get_number_at(3), "mid 1900": s.get_number_at(52)}}
             """,
             published={"readings": (195.0, 0, "exact: 97 years in steps of half a year, both ends included")},
             parent="""
                 import numpy as np
                 from scipy import signal
                 x = data["level"].to_numpy(dtype=float)
                 s = signal.cspline1d_eval(signal.cspline1d(x), np.arange(195) * 0.5, dx=1, x0=0)
                 {"1876": s[2], "mid 1900": s[51]}
             """, parent_label="SciPy signal.cspline1d and cspline1d_eval", parent_tolerance=1e-12,
             note="SciPy's spline goes through every reading: at 1876 it gives the reading of 1876."),
        Case("nums.find_phase_locking_to", "the air passengers: the month of each year's busiest month keeps time "
             "with the 12-month cycle", "AirPassengers", "real data",
             ours="""
                 import numpy as np
                 years = data["passengers"].to_numpy().reshape(12, 12)
                 busiest = 12 * np.arange(12) + years.argmax(axis=1)
                 {"strength": sdata.number_list(busiest).find_phase_locking_to(period=12)}
             """,
             parent="""
                 import numpy as np
                 from scipy import signal
                 busiest = 12 * np.arange(12) + data["passengers"].to_numpy().reshape(12, 12).argmax(axis=1)
                 {"strength": signal.vectorstrength(busiest, 12)[0]}
             """, parent_label="SciPy signal.vectorstrength", parent_tolerance=1e-12,
             r="""
                 m <- matrix(passengers, nrow = 12); busiest <- 12 * (0:11) + apply(m, 2, which.max) - 1
                 a <- 2 * pi * busiest / 12
                 list(strength = sqrt(mean(cos(a))^2 + mean(sin(a))^2))
             """, r_tolerance=1e-12,
             note="The vector strength is the length of the average point on the circle of phases (Goldberg & "
                  "Brown 1969), written out in base R."),
    ]
