"""Numbers and table words for peaks: find_each_peak_that and find_each_dip_that (SciPy signal.find_peaks)."""

from __future__ import annotations

import narwhals as nw
import numpy as np

from .. import _peaks
from .._errors import SimplydataError, friendly
from .._time_axis import read_time_step


def peak_columns(values, step, dips, at_least, at_most, apart, stands_out_by, wide_at_least, experts, step_name):
    """(got, columns dict) for one series; positions count from 1."""
    if dips and at_least is not None:
        raise SimplydataError("find_dips() takes is_at_most= (how low a dip must reach), not is_at_least=.")
    if not dips and at_most is not None:
        raise SimplydataError("find_peaks() takes is_at_least= (how high a peak must reach), not is_at_most=.")
    got = _peaks.find(values, at_least if not dips else at_most, apart, stands_out_by, wide_at_least, step, dips,
                      step_name, experts)
    columns = {"position": [int(p) + 1 for p in got["positions"]], "value": got["heights"].astype(float),
               "stands out by": got["prominences"].astype(float), "width": got["widths"].astype(float),
               "left base": [int(p) + 1 for p in got["left"]], "right base": [int(p) + 1 for p in got["right"]]}
    return got, columns


def peak_sentence(got, what, dips, at_least, at_most, apart, where):
    n = len(got["positions"])
    word = "dip" if dips else "peak"
    conditions = []
    if at_least is not None:
        conditions.append(f"at least {at_least:g} high")
    if at_most is not None:
        conditions.append(f"at most {at_most:g}")
    if apart is not None:
        conditions.append(f"at least {apart:g} apart")
    cond = (" " + " and ".join(conditions)) if conditions else ""
    if n == 0:
        return f"Found no {word}s in {what}{cond}."
    best = int(np.argmin(got["heights"]) if dips else np.argmax(got["heights"]))
    side = "lowest" if dips else "highest"
    return (f"Found {n} {word}{'s' if n != 1 else ''} in {what}{cond}; the {side} is {got['heights'][best]:.3g} at "
            f"{where(int(got['positions'][best]))}.")


def _method_line(dips, at_least, at_most, apart_readings):
    bits = []
    height = at_most if dips else at_least
    if height is not None:
        bits.append(f"minpeakheight = {-height if dips else height:g}")
    if apart_readings is not None:
        bits.append(f"minpeakdistance = {apart_readings:g}")
    x = "-x" if dips else "x"
    return (f"Method: local {'bottoms' if dips else 'tops'} (SciPy signal.find_peaks, with peak_prominences and "
            f"peak_widths), as R pracma::findpeaks({', '.join([x] + bits)}).")


def _experts(kwargs):
    allowed = {"height", "distance", "prominence", "width", "threshold", "plateau_size", "wlen", "rel_height"}
    extra = set(kwargs) - allowed
    if extra:
        raise SimplydataError(f"find_each_peak_that() does not know {sorted(extra)[0]}=.")
    return kwargs


class PeakNumberWords:
    def _peaks_word(self, dips, at_least, at_most, apart, stands_out_by, wide_at_least, time_step, experts):
        import pandas as pd

        from ..table import Table

        step_name = "find_each_dip_that" if dips else "find_each_peak_that"
        step, _ = read_time_step(time_step, None, None, getattr(self, "_time_step", None), step_name)
        got, columns = peak_columns(np.asarray(self._values, dtype=float).ravel(), step, dips, at_least, at_most,
                                    apart, stands_out_by, wide_at_least, _experts(experts), step_name)
        print(peak_sentence(got, "the numbers", dips, at_least, at_most, apart, lambda p: f"position {p + 1}"))
        print(_method_line(dips, at_least, at_most, None if apart is None else apart / step))
        return Table(pd.DataFrame(columns))

    @friendly(renamed={"at_least": "is_at_least"})
    def find_each_peak_that(self, is_at_least=None, apart=None, stands_out_by=None, wide_at_least=None, time_step=None, **experts):
        """Find the peaks: numbers higher than both neighbours, with conditions. nums.find_each_peak_that(is_at_least=1, apart=10)

        is_at_least= the lowest height that counts; apart= the smallest distance between peaks (in readings,
        or in units of time with time_step=); stands_out_by= how far a peak rises above the higher of the
        two lowest points that part it from higher ground (prominence); wide_at_least= its width at half
        that height. Gives back one row per peak: position (from 1), value, stands out by, width, left
        and right base. SciPy signal.find_peaks (SciPy's height=, distance=, prominence= ... work too);
        the positions are those of R pracma::findpeaks. A flat top counts once, at its middle.
        """
        return self._peaks_word(False, is_at_least, None, apart, stands_out_by, wide_at_least, time_step, experts)

    @friendly(renamed={"at_most": "is_at_most"})
    def find_each_dip_that(self, is_at_most=None, apart=None, stands_out_by=None, wide_at_least=None, time_step=None, **experts):
        """Find the dips: numbers lower than both neighbours. nums.find_each_dip_that(is_at_most=-1, apart=10)

        As find_each_peak_that, turned upside down: is_at_most= the highest value a dip may have. SciPy
        signal.find_peaks on minus the numbers, as R pracma::findpeaks(-x).
        """
        return self._peaks_word(True, None, is_at_most, apart, stands_out_by, wide_at_least, time_step, experts)
