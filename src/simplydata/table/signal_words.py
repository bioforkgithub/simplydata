"""Table words for signals: table.find_spectrum_of("signal", sorted_by="time")."""

from __future__ import annotations

from .._typing import _Same

import narwhals as nw
import numpy as np

from .. import _signals
from .._errors import friendly
from .._time_axis import need_filled, need_regular, series_of
from ..numbers.signal_words import spectrum_columns

EXAMPLE = 'table.find_spectrum_of("signal", sorted_by="time")'


class SignalTableWords:
    @friendly(renamed={"method": "test_method", "for_each": "for_each_group_in"})
    def find_spectrum_of(self: _Same, column=None, sorted_by=None, test_method="periodogram", window=None, window_shape="hann",
                         show="power", between=None, for_each_group_in=None) -> _Same:
        """Which repeating cycles (frequencies) a column holds over time, and how strong each is.

        table.find_spectrum_of("signal", sorted_by="time")   (with sdata.get_example("sensor"))
        sorted_by= is the time column (numbers or dates); it gives the order and the time between
        readings (dates: per day, or per month, quarter or year for calendar steps). Without it the
        rows are taken in table order and frequencies are in cycles per reading. The readings must be
        evenly spaced and filled in, except with test_method="lomb-scargle", which is made for uneven times
        (empty cells are then left out). test_method= and show= as numbers.find_spectrum: "periodogram" (SciPy;
        2 x R spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)$spec except at the top
        frequency), "welch" (window= readings per piece) or "lomb-scargle" (R lomb::lsp() itself, needs
        simplydata[r] and R). for_each_group_in= gives one spectrum per group. Gives back a table: frequency,
        repeats every (1 / frequency), power. Prints the 3 strongest cycles.
        """
        step_name = "find_spectrum_of"
        self._need_name(step_name, "the column", column, EXAMPLE)
        name = _signals.read_method(test_method, step_name)
        between = _signals.check_frequency_range(between, step_name)
        series = series_of(self, column, sorted_by, for_each_group_in, step_name, EXAMPLE)
        groups = self._group_columns(step_name, for_each_group_in, [column]) if for_each_group_in is not None else []
        parts, method_line = [], None
        for one in series:
            values, times = one.values, one.times
            if name == "lomb-scargle":
                keep = ~np.isnan(values)
                if not keep.all():
                    where = f" for {one.label}" if one.label else ""
                    print(f'Note: {int((~keep).sum())} empty cells in "{column}"{where} were left out (Lomb-Scargle '
                          "needs no even steps).")
                times = (np.arange(len(values), dtype=float) if times is None else times)[keep]
                values = values[keep]
            else:
                need_filled(one, column, step_name, sorted_by)
                need_regular(one, step_name, sorted_by)
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            result = _signals.spectrum(values, one.step, name, window, window_shape, show, times=times,
                                       unit=one.unit, what=what, step_name=step_name)
            print(result["sentence"])
            method_line = result["method"]
            label = (", ".join(groups), one.label) if groups else None
            parts.append(spectrum_columns(result, between, label))
        print(method_line + (f" Readings: {series[0].describe()}." if len(series) == 1 else ""))
        data = {key: [v.item() if hasattr(v, "item") else v for p in parts for v in p[key]] for key in parts[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))
