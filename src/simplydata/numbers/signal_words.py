"""Numbers words for signals: nums.find_spectrum(time_step=0.01)."""

from __future__ import annotations

import numpy as np

from .. import _signals, _time_series
from .._errors import SimplydataError, friendly
from .._time_axis import read_time_step


class SignalNumberWords:
    @friendly(renamed={"method": "test_method", "times": "time_points"})
    def find_spectrum(self, time_step=None, test_method="periodogram", window=None, window_shape="hann", show="power",
                      between=None, time_points=None, sampling_rate=None, fs=None):
        """Which repeating cycles (frequencies) the numbers hold, and how strong each is.

        nums.find_spectrum(time_step=0.01)   (readings 0.01 seconds apart: frequencies per second)
        time_step= is the time between readings (sampling_rate= or fs=, readings per unit of time, are
        accepted instead); without it the frequencies are in cycles per reading. test_method="periodogram"
        (the default; SciPy periodogram, one-sided, scaled so that the powers times the frequency step
        add up to the variance: 2 x R spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)$spec,
        except at the top frequency, which R does not double), "welch" (the average periodogram of
        pieces of window= readings with half overlap and a window_shape="hann" window; less noisy,
        coarser) or "lomb-scargle" (for readings at uneven time_points=; R lomb::lsp() itself, needs
        simplydata[r] and R). show="power", "decibels" (10 x log10 of the power) or "amplitude" (the
        size of the cycle in the numbers' own units). between=[low, high] keeps that frequency range in
        the table. Gives back a table: frequency, repeats every (1 / frequency), the power and the share
        of the variance (%) at each frequency. Prints the 3 strongest cycles.
        """
        step_name = "find_spectrum"
        name = _signals.read_method(test_method, step_name)
        values = np.asarray(self._values, dtype=float).ravel()
        if name == "lomb-scargle":
            if time_points is None:
                raise SimplydataError('test_method="lomb-scargle" needs time_points= (the time of each reading), as '
                                      "many as the numbers.")
            t = np.asarray(time_points, dtype=float).ravel()
            if len(t) != len(values):
                raise SimplydataError(f"time_points= has {len(t)} values but there are {len(values)} numbers.")
            keep = ~np.isnan(values)
            if not keep.all():
                print(f"Note: {int((~keep).sum())} empty values were left out (Lomb-Scargle needs no even steps).")
            values, t, step, words, unit = values[keep], t[keep], 1.0, "times as given", "time units"
        else:
            if time_points is not None:
                raise SimplydataError('time_points= is for test_method="lomb-scargle"; other methods need evenly '
                                      "spaced readings and take time_step=.")
            if np.isnan(values).any():
                raise SimplydataError(f"find_spectrum() needs a value at every step, but {int(np.isnan(values).sum())} "
                                      "numbers are empty. Fill them first, for example "
                                      'nums.fill_empty_numbers(with_the="line between neighbours").')
            step, words = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None), step_name)
            t = None
            unit = "rows" if (time_step is None and sampling_rate is None and fs is None and
                              getattr(self, "_time_step", None) is None) else "time units"
        result = _signals.spectrum(values, step, name, window, window_shape, show, times=t, unit=unit,
                                   what="the numbers", step_name=step_name)
        print(result["sentence"])
        print(result["method"] + (f" {words[0].upper() + words[1:]}." if name != "lomb-scargle" else ""))
        return _spectrum_table(result, _signals.check_frequency_range(between, step_name))


class TimeSeriesNumberWords:
    @friendly
    def find_autocorrelation(self, rows_back=None, show="correlation", band="white noise"):
        """How much the numbers are like themselves some places back (autocorrelation), with a noise band.

        nums.find_autocorrelation(rows_back=24)
        As table.find_autocorrelation_of: R acf (show="correlation"), pacf ("partial") or the
        covariance, the white-noise or Bartlett band, and the Ljung-Box test, from statsmodels with
        R's options. The numbers are taken in order, evenly spaced, with no empty values.
        """
        import pandas as pd

        from ..table import Table

        step_name = "find_autocorrelation"
        values = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(values).any():
            raise SimplydataError(f"find_autocorrelation() needs a value at every place, but {int(np.isnan(values).sum())} "
                                  'numbers are empty. Fill them first: nums.fill_empty_numbers(with_the="line between '
                                  'neighbours").')
        got = _time_series.autocorrelation(values, rows_back, show, band, step_name)
        print(_time_series.sentence(got, "The numbers", show, band))
        print(_time_series.method_sentence(show, band, got["k"]))
        return Table(pd.DataFrame({"rows back": got["rows_back"], got["column"]: got["values"],
                                   "band low": got["low"], "band high": got["high"],
                                   "outside band": np.where(got["outside"], "yes", "no"),
                                   "Ljung-Box statistic": got["ljung_box"][0],
                                   "Ljung-Box p-value": got["ljung_box"][1]}))


    @friendly(renamed={"method": "test_method"})
    def forecast(self, steps_ahead=12, test_method="exponential smoothing", repeats_every=None, trend=True,
                 season="added", order=None, seasonal_order=None, interval=95, check_on_last=None, show="forecast"):
        """Forecast the next numbers, with an interval for each (R forecast and stats, run in R).

        nums.forecast(steps_ahead=12, repeats_every=12)
        As table.forecast: the numbers are taken in order, one step apart, and called "numbers" in the
        sentences. test_method= "exponential smoothing" (R HoltWinters), "last value", "same season last
        time", "average", "straight on" or "arima" (with order=); repeats_every= is a whole number of
        readings here. Needs simplydata[r] and R with the forecast package. Gives back a table.
        """
        import pandas as pd

        from ..table import Table

        values = np.asarray(self._values, dtype=float).ravel()
        return Table(pd.DataFrame({"numbers": values})).forecast(
            "numbers", steps_ahead=steps_ahead, method=test_method, repeats_every=repeats_every, trend=trend,
            season=season, order=order, seasonal_order=seasonal_order, interval=interval,
            check_on_last=check_on_last, show=show)

def _spectrum_table(result, between, group=None):
    """The spectrum as a pandas Table (Numbers words)."""
    import pandas as pd

    from ..table import Table

    return Table(pd.DataFrame(spectrum_columns(result, between, group)))


def spectrum_columns(result, between, group=None) -> dict:
    """The result columns, optionally only inside between=(low, high), with a group column first."""
    freq = np.asarray(result["frequency"], dtype=float)
    keep = np.ones(len(freq), dtype=bool) if between is None else (freq >= between[0]) & (freq <= between[1])
    columns = {}
    if group is not None:
        columns[group[0]] = [group[1]] * int(keep.sum())
    columns["frequency"] = freq[keep]
    columns["repeats every"] = np.asarray(result["repeats every"], dtype=float)[keep]
    columns[result["column"]] = np.asarray(result[result["column"]], dtype=float)[keep]
    if result["share"] is not None:
        columns["share of variance (%)"] = np.asarray(result["share"], dtype=float)[keep]
    return columns
