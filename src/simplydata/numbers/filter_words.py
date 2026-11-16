"""Numbers words for filters and peaks (to be appended to numbers/signal_words.py as FilterNumberWords)."""

from __future__ import annotations

import numpy as np

from .. import _filters, _peaks
from .._errors import SimplydataError, friendly
from .._time_axis import read_time_step


def _one_condition(below, above, between, equal_to, step_name):
    given = [(n, v) for n, v in (("below", below), ("above", above), ("between", between), ("equal_to", equal_to))
             if v is not None]
    if len(given) != 1:
        raise SimplydataError(f"{step_name}() needs exactly one of is_below=, is_above=, is_between= or is_equal_to=, such as "
                              f"nums.{step_name}(is_below=5, time_step=0.01).")
    name, value = given[0]
    if name == "between":
        if not (isinstance(value, (list, tuple)) and len(value) == 2 and value[0] < value[1]):
            raise SimplydataError("is_between= needs two frequencies, the lower first, such as is_between=[1, 5].")
    return name, value


def filter_numbers(values, keep, condition, value, step, method, steepness, both_ways, ripple, removed_by, window,
                   window_shape, width, and_multiples, step_name):
    """(filtered values, sentence, method sentence)."""
    if condition == "equal_to":
        made = _filters.design_single(keep, value, step, width, and_multiples, step_name)
    else:
        if and_multiples:
            raise SimplydataError("and_multiples= goes with is_equal_to=.")
        kind = {("below", True): "low", ("above", True): "high", ("between", True): "pass",
                ("below", False): "high", ("above", False): "low", ("between", False): "stop"}[(condition, keep)]
        chosen = _filters.read_method(method, step_name)
        made = _filters.design(kind, value, step, chosen, steepness, ripple, removed_by, window, window_shape,
                               step_name)
    out = _filters.apply(values, made, both_ways)
    verb = "Kept" if keep else "Removed"
    what = (f"between {value[0]:g} and {value[1]:g}" if condition == "between" else
            f"at {value:g}" if condition == "equal_to" else f"{condition} {value:g}")
    ways = ("run forwards and backwards so nothing moves in time" + (
        f" (steepness {2 * steepness} in effect)" if "sos" in made and condition != "equal_to" else "")
            if both_ways else "run forwards only, from rest (as a live instrument would)")
    sentence = f"{verb} the frequencies {what} in {len(out)} readings ({step:g} apart): {made['words']}, {ways}."
    call = (f"signal::filtfilt({made['r_call']}, x) in the middle (SciPy's ends: odd reflection and a steady start, as "
            "MATLAB)" if both_ways else f"signal::filter({made['r_call']}, x)")
    return out, sentence, f"Method: SciPy, as R {call}.", made


def filter_call(option, value, step, method="butterworth", steepness=4, ripple=0.5, removed_by=40, width=1,
                and_multiples=False):
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
        parts += [f'method="{method}"'] if method_name != "butterworth" else []
        parts += [f"steepness={steepness}"] if steepness != 4 else []
        parts += [f"ripple={ripple:g}"] if ripple != 0.5 else []
        parts += [f"removed_by={removed_by:g}"] if removed_by != 40 else []
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
                     show_filter=False):
        condition, value = _one_condition(below, above, between, equal_to, step_name)
        step, words = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None), step_name)
        out, sentence, method_line, made = filter_numbers(
            np.asarray(self._values, dtype=float).ravel(), keep, condition, value, step, method, steepness,
            both_ways, ripple, removed_by, window, window_shape, width, and_multiples, step_name)
        print(sentence)
        print(method_line)
        if show_filter:
            option = {("below", True): "keep_below", ("above", True): "keep_above", ("between", True): "keep_between",
                      ("below", False): "keep_above", ("above", False): "keep_below",
                      ("between", False): "remove_between", ("equal_to", False): "remove_at"}.get((condition, keep))
            show_filter_chart(made, step, show_filter, filter_call(option, value, step, method, steepness, ripple,
                                                                   removed_by, width, and_multiples))
        return self._change(f"{'keep' if keep else 'remove'} frequencies {condition}", out)

    @friendly(renamed={"below": "is_below", "above": "is_above", "between": "is_between", "equal_to": "is_equal_to"})
    def keep_each_frequency_that(self, is_below=None, is_above=None, is_between=None, is_equal_to=None, time_step=None,
                                 method="butterworth", steepness=4, both_ways=True, ripple=0.5, removed_by=40, width=1,
                                 show_filter=False, sampling_rate=None, fs=None):
        """Keep only some frequencies of the numbers (a low-pass, high-pass, band-pass or peak filter).

        nums.keep_each_frequency_that(is_below=5, time_step=0.01)
        One condition: is_below=5 keeps the slow cycles (low-pass), is_above=1 the fast ones (high-pass),
        is_between=[1, 5] a band, is_equal_to=10 one frequency (width= how wide). Frequencies are cycles per unit
        of time: time_step= is the time between readings (sampling_rate= or fs= instead). method=
        "butterworth" (flat where it keeps; R signal::butter), "chebyshev" (ripple= dB), "chebyshev 2"
        (removed_by= dB), "elliptic" or "bessel" (keeps the shape of pulses). steepness= is the filter order (4). both_ways=True
        runs the filter forwards and backwards so nothing moves in time (SciPy sosfiltfilt; the ends as
        MATLAB filtfilt, which differs from R signal::filtfilt near the ends); both_ways=False runs it
        forwards only, as R signal::filter. show_filter=True also shows the filter's chart (gain and phase
        against frequency) and prints the line that saves it, sdata.frequency_filter(...).chart().save(...).
        Undo with nums.undo().
        """
        return self._filter_word(True, is_below, is_above, is_between, is_equal_to, time_step, method, steepness, both_ways,
                                 ripple, removed_by, 101, "hamming", width, False, sampling_rate, fs,
                                 "keep_each_frequency_that", show_filter)

    @friendly(renamed={"below": "is_below", "above": "is_above", "between": "is_between", "equal_to": "is_equal_to"})
    def remove_each_frequency_that(self, is_below=None, is_above=None, is_between=None, is_equal_to=None, time_step=None,
                                   method="butterworth", steepness=4, both_ways=True, ripple=0.5, removed_by=40, width=1,
                                   and_multiples=False, show_filter=False, sampling_rate=None, fs=None):
        """Remove some frequencies from the numbers, such as a 50-per-second hum (band-stop or notch filter).

        nums.remove_each_frequency_that(is_equal_to=50, time_step=0.005)
        is_between=[49, 51] removes a band; is_equal_to=50 one frequency (a notch, width= how wide; and_multiples
        =True also removes 100, 150 ...: a comb); is_below= and is_above= remove the slow or the fast cycles.
        The options are those of keep_each_frequency_that (show_filter= too). Undo with nums.undo().
        """
        return self._filter_word(False, is_below, is_above, is_between, is_equal_to, time_step, method, steepness, both_ways,
                                 ripple, removed_by, 101, "hamming", width, and_multiples, sampling_rate, fs,
                                 "remove_each_frequency_that", show_filter)
