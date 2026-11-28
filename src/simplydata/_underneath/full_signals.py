"""Families for 100 %, batches 17-18 (approved by Manish 2026-11-28): the scipy.signal names of plan section 2.7
(filter design, FIR filters, analog filters, system forms, pole placement, group delay, spectra over time, zoomed
transforms, waves, spline resampling and phase locking), each next to the SciPy code that does the same job."""

from . import Entry

SENSOR = '''
            numbers = sdata.get_example("sensor").get_column("signal")
            {call}
        '''
SENSOR_X = '''
            import numpy as np, pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # {comment}
            {body}
        '''
FILTERED = "simplydata also says what it kept and the SciPy calls it ran; numbers.undo() takes the step back."


def _filter(option, call, body, choices=(), also=FILTERED, word="nums.keep_each_frequency_that", tolerance=1e-9):
    """An entry for an option of the filter words on the sensor practice readings (200 a second)."""
    return Entry(word=word, option=option, data="sensor", ours=SENSOR.format(call=f"numbers.{call}"),
                 code={"SciPy": SENSOR_X.format(comment=call, body=body)}, compare="value", tolerance=tolerance,
                 choices=choices, also=also)


ENTRIES = [
    # ---------------------------------------------------------------- FIR filters
    _filter('test_method="fir"', 'keep_each_frequency_that(is_below=10, time_step=0.005, test_method="fir")',
            '''taps = signal.firwin(101, 10, window="hamming", fs=200)   # (1)
            signal.filtfilt(taps, [1.0], x)                         # (2)''',
            choices=("101 weights (how_many_weights=), a Hamming window (window_shape=): SciPy firwin, the window "
                     "method; the weights add up to 1, so the average passes whole.",
                     "run forwards and backwards (both_ways=True): an FIR filter run both ways has no delay at all.")),
    _filter('test_method="fir least squares"',
            'keep_each_frequency_that(is_below=10, time_step=0.005, test_method="fir least squares", '
            'transition_width=4)',
            '''taps = signal.firls(101, [0, 8, 12, 100], [1, 1, 0, 0], fs=200)   # (1)
            signal.filtfilt(taps, [1.0], x)''',
            choices=("the cutoff sits in the middle of the change from kept to removed: the bands end at 10 - 4 / 2 "
                     "and start at 10 + 4 / 2 (as SciPy kaiserord's documentation puts the cutoff); as R "
                     "gsignal::firls(100, c(0, 8, 12, 100) / 100, c(1, 1, 0, 0)).",)),
    _filter('test_method="fir equiripple"',
            'keep_each_frequency_that(is_below=10, time_step=0.005, test_method="fir equiripple", transition_width=4)',
            '''taps = signal.remez(101, [0, 8, 12, 100], [1, 0], fs=200)   # (1)
            signal.filtfilt(taps, [1.0], x)''',
            choices=("the Parks-McClellan (Remez) design with the same band edges as \"fir least squares\", equal "
                     "weight in both bands (SciPy's default), as R signal::remez(100, c(0, 8, 12, 100) / 100, "
                     "c(1, 1, 0, 0)).",)),
    _filter('test_method="fir frequency sampling"',
            'keep_each_frequency_that(is_below=10, time_step=0.005, test_method="fir frequency sampling")',
            '''taps = signal.firwin2(101, [0.0, 10.0, 10.0, 100.0], [1, 1, 0, 0], fs=200)   # (1)
            signal.filtfilt(taps, [1.0], x)''',
            choices=("without transition_width= the gain jumps from 1 to 0 at the cutoff (the cutoff given twice, as "
                     "decimals: SciPy firwin2 nudges a repeated frequency only then); SciPy's own frequency grid (R "
                     "gsignal::fir2 uses 512 points unless told otherwise) and a Hamming window.",)),
    _filter("how_many_weights=",
            'keep_each_frequency_that(is_below=10, time_step=0.005, test_method="fir", how_many_weights=31, '
            'window_shape="blackman")',
            '''taps = signal.firwin(31, 10, window="blackman", fs=200)
            signal.filtfilt(taps, [1.0], x)'''),
    _filter('test_method="gammatone"',
            'keep_each_frequency_that(is_equal_to=5, time_step=0.005, test_method="gammatone")',
            '''b, a = signal.gammatone(5, "iir", fs=200)   # (1)
            signal.filtfilt(b, a, x)''',
            choices=("SciPy's IIR gammatone filter (Slaney's design), whose width is fixed by the frequency, as in "
                     "models of hearing; width= is not used.",)),
    _filter("find_order_for=",
            'keep_each_frequency_that(is_below=10, time_step=0.005, find_order_for={"loss_at": 20})',
            '''n, wn = signal.buttord(10, 20, 0.5, 40, fs=200)          # (1)
            sos = signal.butter(n, wn, output="sos", fs=200)
            signal.sosfiltfilt(sos, x)''',
            choices=("at most ripple=0.5 dB lost up to 10 and at least removed_by=40 dB removed from 20 on: SciPy "
                     "buttord gives the smallest steepness (8) and the cutoff that meets both, as R "
                     "gsignal::buttord(10 / 100, 20 / 100, 0.5, 40).",)),
    _filter('start_from="first value"',
            'keep_each_frequency_that(is_below=10, time_step=0.005, both_ways=False, start_from="first value")',
            '''sos = signal.butter(4, 10, output="sos", fs=200)
            zi = signal.sosfilt_zi(sos) * x[0]                       # (1)
            signal.sosfilt(sos, x, zi=zi)[0]''',
            choices=("the filter starts as if the first reading had always been there (its steady state), so the "
                     "output does not swing up from 0 at the start, as R gsignal::filter_zi.",)),
    _filter("with_least_delay=",
            'keep_each_frequency_that(is_below=10, time_step=0.005, test_method="fir", both_ways=False, '
            'with_least_delay=True)',
            '''taps = signal.firwin(101, 10, fs=200)
            short = signal.minimum_phase(taps, method="homomorphic", half=False)   # (1)
            signal.lfilter(short, [1.0], x)''',
            choices=("half=False keeps the gain of the filter at every frequency (SciPy's default half=True takes its "
                     "square root and halves the length).",)),
    Entry(
        word="table.add_filtered_column", option='test_method="fir equiripple"', data="sensor",
        ours="""
            table = sdata.get_example("sensor")
            table.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time",
                                      test_method="fir equiripple", how_many_weights=41, transition_width=4)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            df = pd.read_csv("sensor.csv")
            # add_filtered_column("slow", ..., test_method="fir equiripple", transition_width=4)
            taps = signal.remez(41, [0, 8, 12, 100], [1, 0], fs=200)
            in_time = df.sort_values("time")
            slow = signal.filtfilt(taps, [1.0], in_time["signal"].to_numpy(dtype=float))
            df.assign(slow=pd.Series(slow, index=in_time.index))
        """},
        compare="table", tolerance=1e-9,
        also="The other FIR designs and options of keep_each_frequency_that work the same way on a column.",
    ),
    # ---------------------------------------------------------------- sdata.frequency_filter
    Entry(
        word="sdata.frequency_filter", option="analog=",
        ours="""
            system = sdata.frequency_filter(keep_between=[1, 5], analog=True)
            system.table()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # frequency_filter(keep_between=[1, 5], analog=True)
            z, p, k = signal.buttap(4)                                        # (1)
            w0, bw = 2 * np.pi * np.sqrt(1 * 5), 2 * np.pi * (5 - 1)
            b, a = signal.zpk2tf(*signal.lp2bp_zpk(z, p, k, wo=w0, bw=bw))   # (2)
            top = np.concatenate([np.zeros(len(a) - len(b)), b])
            pd.DataFrame({"power of s": np.arange(8, -1, -1), "numerator": top, "denominator": a})
        """},
        compare="table", tolerance=1e-8,
        choices=("the analog Butterworth prototype of steepness 4 (poles on the unit circle), as SciPy butter(..., "
                 "analog=True) starts from.",
                 "moved to the band from 1 to 5 cycles per unit of time: centre 2 pi sqrt(1 x 5) and width 2 pi x 4 "
                 "radians per unit of time (SciPy lp2bp_zpk), as R gsignal::butter(4, 2 * pi * c(1, 5), "
                 "\"pass\", \"s\").",),
        also="keep_below= and keep_above= move the prototype with lp2lp and lp2hp, remove_between= with lp2bs; "
             "test_method= picks cheb1ap, cheb2ap, ellipap or besselap. simplydata also prints the formula.",
    ),
    Entry(
        word="sdata.frequency_filter", option="find_order_for=",
        ours="""
            system = sdata.frequency_filter(keep_below=10, time_step=0.005, test_method="elliptic",
                                            find_order_for={"loss_at": 20})
            system.table()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # frequency_filter(..., test_method="elliptic", find_order_for={"loss_at": 20})
            n, wn = signal.ellipord(10, 20, 0.5, 40, fs=200)                       # (1)
            b, a = signal.sos2tf(signal.ellip(n, 0.5, 40, wn, output="sos", fs=200))
            pd.DataFrame({"power of z": np.arange(n, -1, -1), "numerator": b, "denominator": a})
        """},
        compare="table", tolerance=1e-9,
        choices=("SciPy ellipord gives the smallest steepness (4) that keeps the loss up to 10 within ripple=0.5 dB "
                 "and removes removed_by=40 dB from 20 on, as R gsignal::ellipord.",),
        also="test_method=\"fir\" finds the number of weights and the Kaiser window with SciPy kaiserord.",
    ),
    # ---------------------------------------------------------------- systems
    Entry(
        word="system.table", option='form="sections"',
        ours="""
            system = sdata.frequency_filter(keep_below=10, time_step=0.005)
            system.table(form="sections")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            sos = signal.butter(4, 10, output="sos", fs=200)
            # table(form="sections")
            names = ["numerator 1", "numerator 2", "numerator 3", "denominator 1", "denominator 2", "denominator 3"]
            pd.DataFrame({"section": [1, 2], **dict(zip(names, sos.T))})   # (1)
        """},
        compare="table", tolerance=1e-12,
        choices=("a filter of sdata.frequency_filter shows its own sections; any other system gets them from SciPy "
                 "tf2sos (as R gsignal::tf2sos).",),
        also="sdata.system(sections=..., time_step=...) makes a system from such rows (SciPy sos2tf).",
    ),
    Entry(
        word="system.table", option='form="partial fractions"',
        ours="""
            system = sdata.system("(s + 3) / (s**2 + 3*s + 2)")
            system.table(form="partial fractions")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # table(form="partial fractions")
            r, p, k = signal.residue([1, 3], [1, 3, 2])   # (1)
            pd.DataFrame({"kind": ["fraction"] * 2, "residue (real part)": r.real,
                          "residue (imaginary part)": r.imag, "pole (real part)": p.real,
                          "pole (imaginary part)": p.imag, "power": [np.nan] * 2})
        """},
        compare="table", tolerance=1e-12,
        choices=("SciPy residue for a continuous system (residuez for a system in steps), as R gsignal::residue; "
                 "direct terms, when the top is as long as the bottom, come as extra rows.",),
        also="sdata.system(residues=, poles=) adds the fractions up again (SciPy invres).",
    ),
    Entry(
        word="sdata.system", option="sections=",
        ours="""
            system = sdata.system(sections=[[1, 2, 1, 1, -0.5, 0.1], [1, 0, -1, 1, 0.2, 0.3]], time_step=0.01)
            system.table()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # system(sections=[[1, 2, 1, 1, -0.5, 0.1], [1, 0, -1, 1, 0.2, 0.3]], time_step=0.01)
            b, a = signal.sos2tf([[1, 2, 1, 1, -0.5, 0.1], [1, 0, -1, 1, 0.2, 0.3]])
            pd.DataFrame({"power of z": [4, 3, 2, 1, 0], "numerator": b, "denominator": a})
        """},
        compare="table", tolerance=1e-12,
        also="The system runs the sections themselves (SciPy sosfilt, sosfreqz), as a frequency_filter does.",
    ),
    Entry(
        word="sdata.system", option="residues=",
        ours="""
            system = sdata.system(residues=[-1, 2], poles=[-1, -2])
            system.table()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            # system(residues=[-1, 2], poles=[-1, -2])
            b, a = signal.invres([-1, 2], [-1, -2], [])
            pd.DataFrame({"power of s": [2, 1, 0], "numerator": np.concatenate([[0], b]), "denominator": a})
        """},
        compare="table", tolerance=1e-12,
        also="With time_step= it is SciPy invresz; direct_terms= adds the direct terms.",
    ),
    Entry(
        word="system.move_poles_to",
        ours="""
            system = sdata.system("1 / (s**2 + 2*s + 5)")
            faster = system.move_poles_to([-2, -3])
            faster.table()
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            a, b, c, d = signal.tf2ss([1], [1, 2, 5])                     # (1)
            # move_poles_to([-2, -3])
            k = signal.place_poles(a, b, [-2, -3]).gain_matrix            # (2)
            num, den = signal.ss2tf(a - b @ k, b, c - d @ k, d)
            pd.DataFrame({"power of s": [2, 1, 0], "numerator": num.ravel(), "denominator": den})
        """},
        compare="table", tolerance=1e-10,
        choices=("the state space of SciPy tf2ss (controller form); the gains are in the order of its state, as "
                 "system.table(form=\"state space\") shows it.",
                 "SciPy place_poles (Tits and Yang's method) finds the gains K of the feedback u = r - K x; R "
                 "control::place gives other gains here (it warns that its poles are more than 10 % off), so it is "
                 "not compared.",),
        also="simplydata also prints the gains and the poles it reached.",
    ),
    Entry(
        word="system.frequency_response", option="with_delay=",
        ours="""
            system = sdata.frequency_filter(keep_below=10, time_step=0.005)
            result = system.frequency_response(between=[1, 50], how_many=4, with_delay=True)
            result.get_column("delay")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import signal
            b, a = signal.sos2tf(signal.butter(4, 10, output="sos", fs=200))
            f = np.logspace(0, np.log10(50), 4)
            # frequency_response(between=[1, 50], how_many=4, with_delay=True)
            signal.group_delay((b, a), w=f, fs=200)[1] * 0.005   # (1)
        """},
        compare="value", tolerance=1e-8,
        choices=("SciPy gives the delay in steps; times the time step 0.005 it is in seconds (as R "
                 "gsignal::grpdelay, also in steps).",),
        also="The delay is for systems in steps (SciPy group_delay); a continuous system is refused with a pointer to "
             "system.in_steps().",
    ),
    # ---------------------------------------------------------------- spectra
    Entry(
        word="nums.take_fourier_transform", option="over_time=", data="sensor",
        ours="""
            numbers = sdata.get_example("sensor").get_column("signal")
            result = numbers.take_fourier_transform(time_step=0.005, over_time=True, window=64)
            result.get_column("size")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # take_fourier_transform(time_step=0.005, over_time=True, window=64)
            sft = signal.ShortTimeFFT(signal.get_window("hann", 64), hop=32, fs=200)   # (1)
            z = sft.stft(x)                                                            # (2)
            np.abs(z.T.ravel())
        """},
        compare="value", tolerance=1e-10,
        choices=("pieces of window=64 readings, each moved on by half of it, with periodic Hann weights; not scaled "
                 "(scale_to=None): the legacy signal.stft would divide the sizes by the sum of the weights.",
                 "SciPy's padding: the pieces at the ends hang over the readings and are filled with zeros, so "
                 "sdata.find_inverse_fourier_transform can give every reading back (ShortTimeFFT.istft).",),
        also="The table holds time, frequency, size, phase, real part and imaginary part, one row for each piece and "
             "frequency.",
    ),
    Entry(
        word="nums.take_fourier_transform", option="between=", data="sensor",
        ours="""
            numbers = sdata.get_example("sensor").get_column("signal")
            result = numbers.take_fourier_transform(time_step=0.005, between=[45, 55], how_many=21)
            result.get_column("size")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # take_fourier_transform(time_step=0.005, between=[45, 55], how_many=21)
            z = signal.zoom_fft(x, [45, 55], m=21, fs=200, endpoint=True)   # (1)
            np.abs(z)
        """},
        compare="value", tolerance=1e-9,
        choices=("endpoint=True: both ends of between= are among the frequencies (SciPy's default leaves the top one "
                 "out); the zoom FFT is the chirp z-transform on the unit circle (as R gsignal::czt).",),
        also="These are the numbers of the full Fourier transform at those frequencies, worked out only there.",
    ),
    Entry(
        word="nums.find_spectrum", option="over_time=", data="sensor",
        ours="""
            numbers = sdata.get_example("sensor").get_column("signal")
            result = numbers.find_spectrum(time_step=0.005, over_time=True, window=100)
            result.get_column("power")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            x = pd.read_csv("sensor.csv")["signal"].to_numpy(dtype=float)
            # find_spectrum(time_step=0.005, over_time=True, window=100)
            f, t, p = signal.spectrogram(x, fs=200, window="hann", nperseg=100, noverlap=50,   # (1)
                                         detrend="constant", scaling="density", mode="psd")
            p.T.ravel()
        """},
        compare="value", tolerance=1e-12,
        choices=("half overlap and each piece's mean removed, as chart.draw_spectrum_over_time draws it.",),
        also="show=\"decibels\" gives 10 x log10 of the power; between= keeps a frequency range.",
    ),
    # ---------------------------------------------------------------- waves, resampling, phase
    Entry(
        word="sdata.make_wave", option='shape="maximum length sequence"',
        ours="""
            sdata.make_wave("maximum length sequence", time_step=0.01, how_many=127)
        """,
        code={"SciPy": """
            from scipy import signal
            # make_wave("maximum length sequence", time_step=0.01, how_many=127)
            signal.max_len_seq(7, length=127)[0]   # (1)
        """},
        compare="value", tolerance=0,
        choices=("the fewest bits whose run is at least how_many= long (7 bits repeat after 127 readings), SciPy's "
                 "usual taps and start (all ones).",),
        also="simplydata also says after how many readings the run repeats.",
    ),
    Entry(
        word="sdata.make_wave", option='sweep="polynomial"',
        ours="""
            sdata.make_wave("chirp", sweep="polynomial", frequency=[2, 1], time_step=0.01, how_many=300)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import signal
            # make_wave("chirp", sweep="polynomial", frequency=[2, 1], time_step=0.01, how_many=300)
            signal.sweep_poly(np.arange(300) * 0.01, [2, 1])   # (1)
        """},
        compare="value", tolerance=1e-12,
        choices=("frequency= is the polynomial of the frequency in time, highest power first: 2 t + 1 cycles per "
                 "unit of time.",),
        also="The other sweeps (linear, quadratic, logarithmic, hyperbolic) go from frequency=[start, end].",
    ),
    _filter('test_method="cubic spline"', 'change_time_step(to=0.002, time_step=0.005, test_method="cubic spline")',
            '''new_times = np.arange(2498) * 0.002                                     # (1)
            signal.cspline1d_eval(signal.cspline1d(x), new_times, dx=0.005, x0=0)    # (2)''',
            choices=("the new readings start at the first one and go up by to= while they stay within the last "
                     "(999 x 0.005 / 0.002, 2,498 readings).",
                     "a cubic spline through every reading, its ends mirrored (SciPy cspline1d), read at the new "
                     "times; no filter first."),
            also="test_method=\"quadratic spline\" uses qspline1d and qspline1d_eval. simplydata also remembers "
                 "the new time step.", word="nums.change_time_step", tolerance=1e-12),
    Entry(
        word="nums.find_phase_locking_to",
        ours="""
            numbers = sdata.number_list([0.01, 0.11, 0.205, 0.31, 0.4, 0.52, 0.61])
            numbers.find_phase_locking_to(period=0.1)
        """,
        code={"SciPy": """
            from scipy import signal
            events = [0.01, 0.11, 0.205, 0.31, 0.4, 0.52, 0.61]
            # find_phase_locking_to(period=0.1)
            strength, phase = signal.vectorstrength(events, 0.1)
            strength
        """},
        compare="value", tolerance=1e-12,
        also="simplydata also prints the phase where the events gather, in degrees; a list of periods gives a table.",
    ),
]
