"""Table words: add_filtered_column, add_envelope_column, find_each_peak_that, find_each_dip_that (SciPy; see simplydata._filters and _peaks)."""

from __future__ import annotations

from .._typing import _Same

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._time_axis import need_filled, need_regular, series_of


class SignalMoreTableWords:
    @friendly(renamed={"method": "test_method", "for_each": "for_each_group_in", "numtaps": "how_many_weights"})
    def add_filtered_column(self: _Same, name=None, from_column=None, keep_below=None, keep_above=None, keep_between=None,
                            remove_between=None, remove_at=None, sorted_by=None, for_each_group_in=None, test_method="butterworth",
                            steepness=4, both_ways=True, ripple=0.5, removed_by=40, width=1, show_filter=False,
                            how_many_weights=None, window_shape="hamming", transition_width=None, find_order_for=None,
                            with_least_delay=False, start_from="rest") -> _Same:
        """Add a filtered copy of a column: some frequencies kept or removed (low-pass, high-pass, band, notch).

        table.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")   (with sdata.get_example("sensor"))
        One condition: keep_below=, keep_above=, keep_between=[low, high], remove_between=[low, high] or
        remove_at= one frequency (a notch, width= how wide). Frequencies are cycles per unit of the
        sorted_by column (per second for seconds, per day for dates). The options are those of
        numbers.keep_each_frequency_that (test_method= with the FIR filters, steepness=, find_order_for=, both_ways=,
        start_from=, show_filter=True ...). The readings must be evenly
        spaced and filled in. for_each_group_in= filters each group on its own. Undo with table.undo().
        """
        from ..numbers.filter_words import filter_call, filter_numbers, show_filter_chart

        step_name = "add_filtered_column"
        example = 'table.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")'
        self._need_name(step_name, "the column to filter (from_column=)", from_column, example)
        given = [(k, v) for k, v in (("keep_below", keep_below), ("keep_above", keep_above),
                                     ("keep_between", keep_between), ("remove_between", remove_between),
                                     ("remove_at", remove_at)) if v is not None]
        if len(given) != 1:
            raise SimplydataError(f"{step_name}() needs exactly one of keep_below=, keep_above=, keep_between=, "
                                  f"remove_between= or remove_at=.\nFor example, {example}")
        option, value = given[0]
        keep = option.startswith("keep")
        condition = {"keep_below": "below", "keep_above": "above", "keep_between": "between",
                     "remove_between": "between", "remove_at": "equal_to"}[option]
        if condition == "between" and not (isinstance(value, (list, tuple)) and len(value) == 2 and value[0] < value[1]):
            raise SimplydataError(f"{option}= needs two frequencies, the lower first, such as {option}=[1, 5].")
        if name is None:
            name = f"{from_column}_filtered"
        if name in self._columns:
            raise SimplydataError(f'"{name}" is already a column; give another name.')
        series = series_of(self, from_column, sorted_by, for_each_group_in, step_name, example)
        filled = np.full(len(self._frame), np.nan)
        sentence = method_line = None
        for one in series:
            need_filled(one, from_column, step_name, sorted_by)
            if sorted_by is not None:
                need_regular(one, step_name, sorted_by)
            out, sentence, method_line, made = filter_numbers(one.values, keep, condition, value, one.step, test_method,
                                                        steepness, both_ways, ripple, removed_by, how_many_weights,
                                                        window_shape, width, False, step_name,
                                                        transition_width=transition_width,
                                                        find_order_for=find_order_for,
                                                        with_least_delay=with_least_delay, start_from=start_from)
            filled[one.rows] = out
        print(sentence.replace("in ", f'in "{from_column}": ', 1) if len(series) == 1 else sentence)
        print(method_line + f' Added "{name}".')
        if show_filter:
            step = series[-1].step
            show_filter_chart(made, step, show_filter, filter_call(option, value, step, test_method, steepness, ripple,
                                                                   removed_by, width, False, how_many_weights,
                                                                   window_shape, transition_width, find_order_for,
                                                                   with_least_delay))
        base = nw.maybe_reset_index(self._frame)
        new = nw.new_series(name, [float(v) for v in filled], nw.Float64, backend=base.implementation)
        return self._change(f'add filtered column "{name}"', base.with_columns(new))

    @friendly(renamed={"for_each": "for_each_group_in"})
    def add_envelope_column(self: _Same, name=None, from_column=None, show="envelope", sorted_by=None, for_each_group_in=None) -> _Same:
        """Add the envelope of a column: how big its wave is at each moment (from the Hilbert transform).

        table.add_envelope_column("signal_envelope", from_column="signal", sorted_by="time")   (with sdata.get_example("sensor"))
        show="envelope" (the size of the analytic signal), "phase" (in degrees, unwrapped) or "frequency"
        (how fast the phase turns, in cycles per unit of the sorted_by column; the last value of each
        series is empty). The readings must be evenly spaced and filled in. for_each_group_in= works on each group
        on its own. SciPy signal.hilbert, as R gsignal::hilbert. Undo with table.undo().
        """
        from ..numbers.fourier_words import ENVELOPE_SHOWS, envelope_values

        step_name = "add_envelope_column"
        example = 'table.add_envelope_column("signal_envelope", from_column="signal", sorted_by="time")'
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f"{step_name}() needs a name for the new column first.\nFor example, {example}")
        self._need_name(step_name, "the column (from_column=)", from_column, example)
        if show not in ENVELOPE_SHOWS:
            raise choice_error(step_name, "show", show, list(ENVELOPE_SHOWS))
        if name in self._columns:
            raise SimplydataError(f'"{name}" is already a column; give another name.')
        series = series_of(self, from_column, sorted_by, for_each_group_in, step_name, example)
        filled = np.full(len(self._frame), np.nan)
        for one in series:
            need_filled(one, from_column, step_name, sorted_by)
            if sorted_by is not None:
                need_regular(one, step_name, sorted_by)
            filled[one.rows] = envelope_values(one.values, show, one.step)
        groups = self._group_columns(step_name, for_each_group_in, [from_column]) if for_each_group_in is not None else []
        each = f", for each {', '.join(groups)}" if groups else ""
        order = f' in order of "{sorted_by}"' if sorted_by else ""
        unit = ""
        if show == "frequency":
            u = series[0].unit
            unit = (" (cycles per reading)" if u == "rows" else f" (cycles per {u[:-1]})" if u in (
                "days", "seconds", "months", "quarters", "years") else f' (cycles per unit of "{u}")')
        print(f'The {show} of "{from_column}"{unit}{each}{order}, from the analytic signal. Added "{name}".')
        print("Method: SciPy signal.hilbert, as R gsignal::hilbert(x).")
        base = nw.maybe_reset_index(self._frame)
        new = nw.new_series(name, [None if np.isnan(v) else float(v) for v in filled], nw.Float64,
                            backend=base.implementation)
        return self._change(f'add envelope column "{name}"', base.with_columns(new))

    def _table_peaks(self, dips, column, sorted_by, at_least, at_most, apart, stands_out_by, wide_at_least, for_each,
                     experts):
        from ..numbers.peak_words import _experts, _method_line, peak_columns, peak_sentence

        step_name = "find_each_dip_that" if dips else "find_each_peak_that"
        example = f'table.{step_name}("signal", sorted_by="time", {"is_at_most=-1" if dips else "is_at_least=1"})'
        self._need_name(step_name, "the column", column, example)
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        raw = self._frame[sorted_by].to_numpy() if sorted_by is not None else None
        parts = []
        apart_readings = None
        for one in series_of(self, column, sorted_by, for_each, step_name, example):
            if sorted_by is not None and (apart is not None or wide_at_least is not None):
                need_regular(one, step_name, sorted_by)  # both are turned into a number of readings
            step = one.step if sorted_by is not None else 1.0
            got, columns = peak_columns(one.values, step, dips, at_least, at_most, apart, stands_out_by,
                                        wide_at_least, _experts(experts), step_name)
            apart_readings = None if apart is None else apart / step
            if raw is not None:
                times = [raw[one.rows[p]] for p in got["positions"]]
                columns = {"position": columns["position"], sorted_by: [t.item() if hasattr(t, "item") else t
                                                                        for t in times],
                           **{k: v for k, v in columns.items() if k != "position"}}
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            where = (lambda p: f"{sorted_by} {one.shown_times[p]}") if raw is not None else (lambda p: f"row {p + 1}")
            print(peak_sentence(got, what, dips, at_least, at_most, apart, where))
            if groups:
                columns = {", ".join(groups): [one.label] * len(got["positions"]), **columns}
            parts.append(columns)
        print(_method_line(dips, at_least, at_most, apart_readings))
        data = {key: [v for p in parts for v in p[key]] for key in parts[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    @friendly(renamed={"at_least": "is_at_least", "for_each": "for_each_group_in"})
    def find_each_peak_that(self: _Same, column=None, sorted_by=None, is_at_least=None, apart=None, stands_out_by=None,
                            wide_at_least=None, for_each_group_in=None, **experts) -> _Same:
        """Find the peaks of a column: readings higher than both neighbours, with conditions.

        table.find_each_peak_that("signal", sorted_by="time", is_at_least=1, apart=0.05)   (with sdata.get_example("sensor"))
        apart= and wide_at_least= are in units of the sorted_by column (readings without it). The other
        options and the result are those of numbers.find_each_peak_that, with the sorted_by value of each peak.
        Empty cells are never peaks. SciPy signal.find_peaks, as R pracma::findpeaks.
        """
        return self._table_peaks(False, column, sorted_by, is_at_least, None, apart, stands_out_by, wide_at_least,
                                 for_each_group_in, experts)

    @friendly(renamed={"at_most": "is_at_most", "for_each": "for_each_group_in"})
    def find_each_dip_that(self: _Same, column=None, sorted_by=None, is_at_most=None, apart=None, stands_out_by=None,
                           wide_at_least=None, for_each_group_in=None, **experts) -> _Same:
        """Find the dips of a column: readings lower than both neighbours (find_each_peak_that upside down).

        table.find_each_dip_that("signal", sorted_by="time", is_at_most=-1, apart=0.05)   (with sdata.get_example("sensor"))
        """
        return self._table_peaks(True, column, sorted_by, None, is_at_most, apart, stands_out_by, wide_at_least,
                                 for_each_group_in, experts)
