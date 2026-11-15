"""Table words: add_filtered_column, find_peaks, find_dips (SciPy; see simplydata._filters and _peaks)."""

from __future__ import annotations

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .._time_axis import need_filled, need_regular, series_of


class SignalMoreTableWords:
    @friendly
    def add_filtered_column(self, name=None, from_column=None, keep_below=None, keep_above=None, keep_between=None,
                            remove_between=None, remove_at=None, sorted_by=None, for_each=None, method="butterworth",
                            steepness=4, both_ways=True, ripple=0.5, removed_by=40, width=1):
        """Add a filtered copy of a column: some frequencies kept or removed (low-pass, high-pass, band, notch).

        table.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")   (with sdata.example("sensor"))
        One condition: keep_below=, keep_above=, keep_between=[low, high], remove_between=[low, high] or
        remove_at= one frequency (a notch, width= how wide). Frequencies are cycles per unit of the
        sorted_by column (per second for seconds, per day for dates). The options are those of
        nums.keep_frequencies (method=, steepness=, both_ways= ...). The readings must be evenly spaced
        and filled in. for_each= filters each group on its own. Undo with table.undo().
        """
        from ..numbers.filter_words import filter_numbers

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
        series = series_of(self, from_column, sorted_by, for_each, step_name, example)
        filled = np.full(len(self._frame), np.nan)
        sentence = method_line = None
        for one in series:
            need_filled(one, from_column, step_name, sorted_by)
            if sorted_by is not None:
                need_regular(one, step_name, sorted_by)
            out, sentence, method_line = filter_numbers(one.values, keep, condition, value, one.step, method,
                                                        steepness, both_ways, ripple, removed_by, 101,
                                                        "hamming", width, False, step_name)
            filled[one.rows] = out
        print(sentence.replace("in ", f'in "{from_column}": ', 1) if len(series) == 1 else sentence)
        print(method_line + f' Added "{name}".')
        base = nw.maybe_reset_index(self._frame)
        new = nw.new_series(name, [float(v) for v in filled], nw.Float64, backend=base.implementation)
        return self._change(f'add filtered column "{name}"', base.with_columns(new))

    def _table_peaks(self, dips, column, sorted_by, at_least, at_most, apart, stands_out_by, wide_at_least, for_each,
                     experts):
        from ..numbers.peak_words import _experts, _method_line, peak_columns, peak_sentence

        step_name = "find_dips" if dips else "find_peaks"
        example = f'table.{step_name}("signal", sorted_by="time", {"at_most=-1" if dips else "at_least=1"})'
        self._need_name(step_name, "the column", column, example)
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        raw = self._frame[sorted_by].to_numpy() if sorted_by is not None else None
        parts = []
        apart_readings = None
        for one in series_of(self, column, sorted_by, for_each, step_name, example):
            if sorted_by is not None and apart is not None:
                need_regular(one, step_name, sorted_by)
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

    @friendly
    def find_peaks(self, column=None, sorted_by=None, at_least=None, apart=None, stands_out_by=None,
                   wide_at_least=None, for_each=None, **experts):
        """Find the peaks of a column: readings higher than both neighbours, with conditions.

        table.find_peaks("signal", sorted_by="time", at_least=1, apart=0.05)   (with sdata.example("sensor"))
        apart= and wide_at_least= are in units of the sorted_by column (readings without it). The other
        options and the result are those of nums.find_peaks, with the sorted_by value of each peak.
        Empty cells are never peaks. SciPy signal.find_peaks, as R pracma::findpeaks.
        """
        return self._table_peaks(False, column, sorted_by, at_least, None, apart, stands_out_by, wide_at_least,
                                 for_each, experts)

    @friendly
    def find_dips(self, column=None, sorted_by=None, at_most=None, apart=None, stands_out_by=None,
                  wide_at_least=None, for_each=None, **experts):
        """Find the dips of a column: readings lower than both neighbours (find_peaks upside down).

        table.find_dips("signal", sorted_by="time", at_most=-1, apart=0.05)   (with sdata.example("sensor"))
        """
        return self._table_peaks(True, column, sorted_by, None, at_most, apart, stands_out_by, wide_at_least,
                                 for_each, experts)
