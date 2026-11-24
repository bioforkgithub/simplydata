"""Numbers words for smoothing: nums.smooth(...) and nums.remove_trend(...). Engine: simplydata._smoothing."""

from __future__ import annotations

from .._typing import _Same

import numpy as np

from .. import _smoothing
from .._errors import friendly


class SmoothingNumberWords:
    @friendly(renamed={"method": "test_method", "degree": "of_degree"})
    def smooth(self: _Same, test_method="moving average", window=5, ends=None, weights=None, of_degree=None, newest_weight=None,
               width=None, smoothness=None, alpha=None, span=None, half_life=None, com=None) -> _Same:
        """Smooth the numbers: each one becomes a summary of its neighbours, so noise and spikes shrink.

        nums.smooth(test_method="median", window=5)
        The numbers are taken in order, one step apart. test_method= "moving average" (the average of the
        window= readings centred on each; weights=[1, 2, 1] for a weighted average; ends= "empty" (as R
        stats::filter), "shorter windows" or "mirror"), "median" (removes single spikes; R runmed() itself,
        ends= "tukey" (R's default), "keep" or "constant"; needs simplydata[r]), "savitzky-golay" (a
        of_degree=2 curve fitted in each window; keeps peak heights; R signal::sgolayfilt), "exponential"
        (newest_weight=0.3: each value = 0.3 x the reading + 0.7 x the value before; alpha=, span=,
        half_life= or com= instead), "gaussian" (weights from a bell curve with a standard deviation of
        width=2 readings), "lowess" (smoothness= the share of readings in each local fit, 2/3), "spline"
        (smoothness="auto" or R's lambda=), "whittaker" (smoothness=100; bigger is smoother) or "wiener".
        Undo with nums.undo().
        """
        got = _smoothing.smooth(np.asarray(self._values, dtype=float).ravel(), test_method, window, ends,
                                step_name="smooth", weights=weights, of_degree=of_degree, newest_weight=newest_weight,
                                width=width, smoothness=smoothness, alpha=alpha, span=span, half_life=half_life,
                                com=com)
        print(f"Smoothed the numbers with {got.sentence}.")
        print(f"Method: as R {got.r_call}.")
        return self._change(f"smooth ({_smoothing.read_method(test_method, 'smooth')})", got.values)

    @friendly(renamed={"method": "test_method"})
    def remove_trend(self: _Same, test_method="straight line", breaks=None) -> _Same:
        """Take away the trend: the best straight line (or only the average) is taken from the numbers.

        nums.remove_trend()
        test_method="straight line" (least squares, as R residuals(lm(x ~ seq_along(x)))) or "average" (takes
        away the average only). breaks=[200, 500] fits a separate straight line to each piece: a new
        line starts after readings 200 and 500 (counting from 1). The pieces are fitted separately, so
        the lines may jump at a break, as SciPy detrend (MATLAB and R pracma::detrend join them into one
        line). Undo with nums.undo().
        """
        values, words, call = _smoothing.remove_trend(np.asarray(self._values, dtype=float).ravel(), test_method, breaks)
        print(f"From the numbers {words}.")
        print(f"Method: SciPy signal.detrend, as R {call}.")
        return self._change("remove trend", values)
