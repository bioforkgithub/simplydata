"""Numbers words for filters and peaks (to be appended to numbers/signal_words.py as FilterNumberWords)."""

from __future__ import annotations

from .._typing import _Same

import numpy as np

from .. import _filter_design, _filters, _peaks
from .._errors import SimplydataError, friendly
from .._time_axis import read_time_step


def _one_condition(below, above, between, equal_to, step_name):
    given = [(n, v) for n, v in (("below", below), ("above", above), ("between", between), ("equal_to", equal_to))
             if v is not None]
    if len(given) != 1:
        raise SimplydataError(f"{step_name}() needs exactly one of is_below=, is_above=, is_between= or is_equal_to=, such as "
                              f"numbers.{step_name}(is_below=5, time_step=0.01).")
    name, value = given[0]
    if name == "between":
        if not (isinstance(value, (list, tuple)) and len(value) == 2 and value[0] < value[1]):
            raise SimplydataError("is_between= needs two frequencies, the lower first, such as is_between=[1, 5].")
    return name, value


def filter_numbers(values, keep, condition, value, step, method, steepness, both_ways, ripple, removed_by, window,
                   window_shape, width, and_multiples, step_name, transition_width=None, find_order_for=None,
                   with_least_delay=False, start_from="rest"):
    """(filtered values, sentence, method sentence, made). window: the number of FIR weights (None: 101)."""
    start_from = _filters.read_start(start_from, both_ways, step_name)
    if with_least_delay and both_ways:
        raise SimplydataError("with_least_delay=True goes with both_ways=False: run both ways, a filter has no delay "
                              "at all.")
    if condition == "equal_to":
        chosen = _filters.read_method(method, step_name, single=True)
        if chosen == "gammatone":
            if not keep:
                raise SimplydataError('test_method="gammatone" keeps one frequency: use it with '
                                      "keep_each_frequency_that(is_equal_to=...).")
            b, a = _filter_design.gammatone(value, step)
            made = dict(ba=(b, a), words=f"gammatone filter at {value:g} (SciPy's width for that frequency)",
                        r_call=f'SciPy signal.gammatone({value:g}, "iir", fs={1 / step:g})', scipy_only=True)
        else:
            made = _filters.design_single(keep, value, step, width, and_multiples, step_name)
    else:
        if and_multiples:
            raise SimplydataError("and_multiples= goes with is_equal_to=.")
        kind = {("below", True): "low", ("above", True): "high", ("between", True): "pass",
                ("below", False): "high", ("above", False): "low", ("between", False): "stop"}[(condition, keep)]
        chosen = _filters.read_method(method, step_name)
        made = _filters.design(kind, value, step, chosen, steepness, ripple, removed_by, window, window_shape,
                               step_name, transition_width=transition_width, find_order_for=find_order_for,
                               with_least_delay=with_least_delay)
    out = _filters.apply(values, made, both_ways, start_from)
    verb = "Kept" if keep else "Removed"
    what = (f"between {value[0]:g} and {value[1]:g}" if condition == "between" else
            f"at {value:g}" if condition == "equal_to" else f"{condition} {value:g}")
    forwards = ("run forwards only, from the steady state for the first reading" if start_from == "first value" else
                "run forwards only, from rest (as a live instrument would)")
    ways = ("run forwards and backwards so nothing moves in time" + (
        f" (steepness {2 * made.get('steepness', steepness)} in effect)" if "sos" in made and condition != "equal_to"
        else "")
            if both_ways else forwards)
    if both_ways and made.get("losses"):  # run twice, the losses in decibels add up: say what the order gives
        ripple_found, removed_found = made["losses"]
        ways += (f"; run twice, the losses double: at most {2 * ripple_found:g} dB lost where it keeps and at least "
                 f"{2 * removed_found:g} dB removed (find_order_for= is for one run; both_ways=False keeps them as "
                 "asked)")
    sentence = f"{verb} the frequencies {what} in {len(out)} readings ({step:g} apart): {made['words']}, {ways}."
    if made.get("scipy_only"):  # a SciPy design with no R call to name: say what SciPy runs
        runs = ("sosfiltfilt" if "sos" in made else "filtfilt") if both_ways else ("sosfilt" if "sos" in made else
                                                                                  "lfilter")
        ends = (" (forwards and backwards; the ends as MATLAB filtfilt: odd reflection and a steady start)"
                if both_ways else " (forwards only, from rest)" if start_from == "rest" else
                f" (forwards only, starting from SciPy {'sosfilt_zi' if 'sos' in made else 'lfilter_zi'} times the "
                "first reading)")
        return out, sentence, f"Method: {made['r_call']}, run with SciPy signal.{runs}{ends}.", made
    if both_ways:
        call = (f"signal::filtfilt({made['r_call']}, x) in the middle (SciPy's ends: odd reflection and a steady "
                "start, as MATLAB)")
    elif start_from == "first value":
        call = (f"gsignal::filter({made['r_call']}, x, zi = gsignal::filter_zi(...) * x[1]) (SciPy "
                f"{'sosfilt_zi' if 'sos' in made else 'lfilter_zi'} times the first reading)")
    else:
        call = f"signal::filter({made['r_call']}, x)"
    return out, sentence, f"Method: SciPy, as R {call}.", made


def filter_call(option, value, step, method="butterworth", steepness=4, ripple=0.5, removed_by=40, width=1,
                and_multiples=False, window=None, window_shape="hamming", transition_width=None, find_order_for=None,
                with_least_delay=False):
    """The sdata.frequency_filter(...) call that makes the same filter, as text (None when it has none)."""
    if option is None:
        return None
    shown = f"[{value[0]:g}, {value[1]:g}]" if isinstance(value, (list, tuple)) else f"{value:g}"
    parts = [f"{option}={shown}", f"time_step={step:g}"]
    if option == "remove_at":
        parts += [f"width={width:g}"] if width != 1 else []
        parts += ["and_multiples=True"] if and_multiples else []
    else:
        method_name = str(method).strip().lower()
        parts += [f'test_method="{method}"'] if method_name != "butterworth" else []
        parts += [f"steepness={steepness}"] if steepness != 4 else []
        parts += [f"ripple={ripple:g}"] if ripple != 0.5 else []
        parts += [f"removed_by={removed_by:g}"] if removed_by != 40 else []
        parts += [f"how_many_weights={window}"] if window is not None else []
        parts += [f'window_shape="{window_shape}"'] if window_shape != "hamming" else []
        parts += [f"transition_width={transition_width:g}"] if transition_width is not None else []
        parts += [f"find_order_for={find_order_for!r}"] if find_order_for is not None else []
        parts += ["with_least_delay=True"] if with_least_delay else []
    return "sdata.frequency_filter(" + ", ".join(parts) + ")"


def show_filter_chart(made, step, show_filter, call):
    """show_filter=True shows the filter's Bode chart (gain and phase against frequency) and prints the line that
    saves it (call: the sdata.frequency_filter(...) that makes the same filter)."""
    if show_filter is False or show_filter is None:
        return
    if show_filter is not True:
        how = (f'To save the chart: {call}.chart().save("filter.png")' if call else
               "Save it from the chart window.")
        raise SimplydataError(f"show_filter= is True (show the filter's chart) or False. {how}")
    import contextlib
    import io

    from .. import _filters
    from ..systems import System

    b, a = _filters.coefficients(made)
    with contextlib.redirect_stdout(io.StringIO()):
        chart = System.from_coefficients(b, a, time_step=step, sos=made.get("sos"), label="the filter").chart()
    chart.write_title_on_top("The filter: gain and phase (run forwards once)")
    if call:
        print(f'To save this chart: {call}.chart().save("filter.png")')
    chart.show()


class FilterNumberWords:
    def _filter_word(self, keep, below, above, between, equal_to, time_step, method, steepness, both_ways, ripple,
                     removed_by, window, window_shape, width, and_multiples, sampling_rate, fs, step_name,
                     show_filter=False, transition_width=None, find_order_for=None, with_least_delay=False,
                     start_from="rest"):
        condition, value = _one_condition(below, above, between, equal_to, step_name)
        step, words = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None), step_name)
        out, sentence, method_line, made = filter_numbers(
            np.asarray(self._values, dtype=float).ravel(), keep, condition, value, step, method, steepness,
            both_ways, ripple, removed_by, window, window_shape, width, and_multiples, step_name,
            transition_width=transition_width, find_order_for=find_order_for, with_least_delay=with_least_delay,
            start_from=start_from)
        print(sentence)
        print(method_line)
        if show_filter:
            option = {("below", True): "keep_below", ("above", True): "keep_above", ("between", True): "keep_between",
                      ("below", False): "keep_above", ("above", False): "keep_below",
                      ("between", False): "remove_between", ("equal_to", False): "remove_at"}.get((condition, keep))
            show_filter_chart(made, step, show_filter, filter_call(option, value, step, method, steepness, ripple,
                                                                   removed_by, width, and_multiples, window,
                                                                   window_shape, transition_width, find_order_for,
                                                                   with_least_delay))
        return self._change(f"{'keep' if keep else 'remove'} frequencies {condition}", out)

    @friendly(renamed={"method": "test_method", "below": "is_below", "above": "is_above", "between": "is_between",
                       "equal_to": "is_equal_to", "numtaps": "how_many_weights"})
    def keep_each_frequency_that(self: _Same, is_below=None, is_above=None, is_between=None, is_equal_to=None,
                                 time_step=None, test_method="butterworth", steepness=4, both_ways=True, ripple=0.5,
                                 removed_by=40, width=1, show_filter=False, sampling_rate=None, fs=None,
                                 how_many_weights=None, window_shape="hamming", transition_width=None,
                                 find_order_for=None, with_least_delay=False, start_from="rest") -> _Same:
        """Keep only some frequencies of the numbers (a low-pass, high-pass, band-pass or peak filter).

        numbers.keep_each_frequency_that(is_below=5, time_step=0.01)
        One condition: is_below=5 keeps the slow cycles (low-pass), is_above=1 the fast ones (high-pass),
        is_between=[1, 5] a band, is_equal_to=10 one frequency (width= how wide; test_method="gammatone" for
        SciPy's gammatone filter, as in models of hearing). Frequencies are cycles per unit
        of time: time_step= is the time between readings (sampling_rate= or fs= instead). test_method=
        "butterworth" (flat where it keeps; R signal::butter), "chebyshev" (ripple= dB), "chebyshev 2"
        (removed_by= dB), "elliptic" or "bessel" (keeps the shape of pulses); steepness= is their filter order (4).
        FIR filters (only weights on the readings, no feedback): "fir" (SciPy firwin, the window method with
        window_shape="hamming"), "fir least squares" (firls), "fir equiripple" (remez, Parks-McClellan) and "fir
        frequency sampling" (firwin2); how_many_weights= (odd, 101) is their length, and transition_width= how wide
        the change from kept to removed is (least squares, equiripple; the cutoff in its middle).
        find_order_for={"loss_at": 8} finds the smallest steepness that loses at most ripple= dB where it keeps
        and removes at least removed_by= dB from 8 on (SciPy buttord, cheb1ord, cheb2ord, ellipord; kaiserord
        for "fir"). both_ways=True
        runs the filter forwards and backwards so nothing moves in time (SciPy sosfiltfilt; the ends as
        MATLAB filtfilt, which differs from R signal::filtfilt near the ends); both_ways=False runs it
        forwards only, as R signal::filter, from rest or with start_from="first value" from the steady state
        for the first reading (SciPy sosfilt_zi); with_least_delay=True gives an FIR filter the least delay
        (SciPy minimum_phase). show_filter=True also shows the filter's chart (gain and phase
        against frequency) and prints the line that saves it, sdata.frequency_filter(...).chart().save(...).
        Undo with numbers.undo().
        """
        return self._filter_word(True, is_below, is_above, is_between, is_equal_to, time_step, test_method, steepness,
                                 both_ways, ripple, removed_by, how_many_weights, window_shape, width, False,
                                 sampling_rate, fs, "keep_each_frequency_that", show_filter, transition_width,
                                 find_order_for, with_least_delay, start_from)

    @friendly(renamed={"method": "test_method", "below": "is_below", "above": "is_above", "between": "is_between",
                       "equal_to": "is_equal_to", "numtaps": "how_many_weights"})
    def remove_each_frequency_that(self: _Same, is_below=None, is_above=None, is_between=None, is_equal_to=None,
                                   time_step=None, test_method="butterworth", steepness=4, both_ways=True, ripple=0.5,
                                   removed_by=40, width=1, and_multiples=False, show_filter=False, sampling_rate=None,
                                   fs=None, how_many_weights=None, window_shape="hamming", transition_width=None,
                                   find_order_for=None, with_least_delay=False, start_from="rest") -> _Same:
        """Remove some frequencies from the numbers, such as a 50-per-second hum (band-stop or notch filter).

        numbers.remove_each_frequency_that(is_equal_to=50, time_step=0.005)
        is_between=[49, 51] removes a band; is_equal_to=50 one frequency (a notch, width= how wide; and_multiples
        =True also removes 100, 150 ... below half the readings per unit of time, one SciPy iirnotch each; the
        average stays); is_below= and is_above= remove the slow or the fast cycles.
        The options are those of keep_each_frequency_that (the FIR test_method= values, how_many_weights=,
        transition_width=, find_order_for=, start_from=, show_filter= too). Undo with numbers.undo().
        """
        return self._filter_word(False, is_below, is_above, is_between, is_equal_to, time_step, test_method,
                                 steepness, both_ways, ripple, removed_by, how_many_weights, window_shape, width,
                                 and_multiples, sampling_rate, fs, "remove_each_frequency_that", show_filter,
                                 transition_width, find_order_for, with_least_delay, start_from)
