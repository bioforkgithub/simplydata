"""Peaks and dips: SciPy signal.find_peaks, peak_prominences and peak_widths (the definitions of MATLAB
findpeaks; R pracma::findpeaks gives the same positions for height and distance). find_each_dip_that runs the
same on minus the values.
"""

from __future__ import annotations

import math

import numpy as np

from ._errors import SimplydataError

SCIPY_NAMES = {"height": "at_least", "distance": "apart", "prominence": "stands_out_by", "width": "wide_at_least"}


def _positive(value, name, step_name):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or not math.isfinite(value):
        raise SimplydataError(f"{step_name}() needs {name}= as a number.")
    return float(value)


def find(values, at_least=None, apart=None, stands_out_by=None, wide_at_least=None, step=1.0, dips=False,
         step_name="find_each_peak_that", experts=None):
    """dict(positions (from 0), heights, stands out by, widths (in readings), left/right bases, sentence bits)."""
    from scipy import signal

    x = np.asarray(values, dtype=float)
    sign = -1.0 if dips else 1.0
    y = sign * x
    empty = np.isnan(y)
    if empty.any():
        y = np.where(empty, -np.inf, y)  # an empty cell is never a peak and splits its neighbours
    options = {}
    at_least = _positive(at_least, "at_least", step_name)
    if at_least is not None:
        options["height"] = sign * at_least if not dips else -at_least
    distance = _positive(apart, "apart", step_name)
    if distance is not None:
        readings = round(distance / step, 9)  # 0.05 / 0.005 is 10.000000000000002 in floating point
        if readings < 1:
            raise SimplydataError(f"apart= is shorter than the time between readings ({step:g}).")
        options["distance"] = readings
    prominence = _positive(stands_out_by, "stands_out_by", step_name)
    if prominence is not None:
        options["prominence"] = prominence
    width = _positive(wide_at_least, "wide_at_least", step_name)
    if width is not None:
        options["width"] = round(width / step, 9)
    options.update(experts or {})
    found, _ = signal.find_peaks(y, **options)
    finite = np.where(np.isfinite(y), y, np.nanmin(np.where(np.isfinite(y), y, np.nan)) if np.isfinite(y).any() else 0)
    prom, left, right = signal.peak_prominences(finite, found)
    widths = signal.peak_widths(finite, found, rel_height=0.5, prominence_data=(prom, left, right))[0]
    return dict(positions=found, heights=x[found], prominences=prom, widths=widths * step, left=left, right=right)
