"""Is one correlation stronger than another? compare_correlations, from R cocor (simplydata[r]).

* Two groups: compare_correlations("hours", "marks", for_each_group_in="school") with exactly two groups: Fisher's z
  test (R cocor::cocor.indep.groups(test = "fisher1925")) and Zou's (2007) interval of the difference.
* One group, two correlations that share a column: compare_correlations(["hours", "marks"], ["sleep", "marks"]):
  Steiger's (1980) z test (cocor::cocor.dep.groups.overlap(test = "steiger1980")) and Zou's interval.
The correlations themselves are Pearson's r from SciPy pearsonr; Python has no test of two correlations.
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError, friendly, renamed_note
from .stat_tests import _label, _num, _skipped_note
from .summaries import _p_sentence


def _r(x, y):
    from scipy import stats

    return float(stats.pearsonr(x, y).statistic)


class CorrelationWords:
    @friendly(renamed={"for_each": "for_each_group_in"})
    def compare_correlations(self, *columns, for_each_group_in=None, first=None, second=None):
        """Is one correlation stronger than another?

        table.compare_correlations("hours", "marks", for_each_group_in="class")   (with sdata.get_example("marks"), two classes)
        The columns are given as in find_correlation_between("hours", "marks"). With for_each_group_in= (two
        groups): is the correlation of the two columns different in the two groups? Fisher's z
        test, R cocor::cocor.indep.groups(). With two pairs of columns that share one column, in
        the same rows: table.compare_correlations(["hours", "marks"], ["height", "marks"]) asks
        whether hours or height goes more strongly with marks: Steiger's z test, R
        cocor::cocor.dep.groups.overlap(). Both print the difference with Zou's 95 % interval
        (simplydata[r]). The correlations are Pearson's r (SciPy). Gives back a one-row table.
        """
        from .._r import r_call

        step = "compare_correlations"
        example = 'table.compare_correlations("hours", "marks", for_each_group_in="class")'
        if first is not None or second is not None:  # the earlier spelling first=, second=
            renamed_note("first=, second=", 'compare_correlations("hours", "marks", ...)')
            if columns:
                raise SimplydataError(f"Give the columns once, without first= and second=.\nFor example, {example}")
            columns = tuple(c for c in (first, second) if c is not None)
        if len(columns) != 2:
            raise SimplydataError(f"{step}() needs two columns and for_each_group_in=, or two pairs of columns.\nFor example, "
                                  f'{example}\nor table.compare_correlations(["hours", "marks"], ["height", "marks"])')
        first, second = columns
        if isinstance(first, str) and isinstance(second, str):
            if not isinstance(for_each_group_in, str):
                raise SimplydataError(f"{step}() with two columns needs for_each_group_in= with two groups.\nFor example, "
                                      f"{example}\nor give two pairs of columns: "
                                      'table.compare_correlations(["hours", "marks"], ["height", "marks"])')
            names = [first, second, for_each_group_in]
            if len(set(names)) != 3:
                raise SimplydataError(f"{step}() needs three different columns.\nFor example, {example}")
            frame = self._number_frame(step, [first, second])
            kept = frame.select(*names).drop_nulls()
            _skipped_note(len(frame) - len(kept), names)
            keys = np.asarray(kept[for_each_group_in].to_list(), dtype=object)
            groups = sorted(set(keys.tolist()), key=lambda k: (str(type(k)), k))
            if len(groups) != 2:
                raise SimplydataError(f'{step}() compares two groups; "{for_each_group_in}" has {len(groups)}. Keep two first, '
                                      "for example with table.keep_rows_where(...).")
            x, y = (kept[c].to_numpy().astype(float) for c in (first, second))
            parts = [(x[keys == g], y[keys == g]) for g in groups]
            if min(len(a) for a, _ in parts) < 4:
                raise SimplydataError(f"{step}() needs at least 4 rows in each group.")
            r1, r2 = (_r(a, b) for a, b in parts)
            n1, n2 = (len(a) for a, _ in parts)
            found = r_call("t <- cocor::cocor.indep.groups(r1, r2, n1, n2, test = c('fisher1925', 'zou2007')); "
                           "list(z = t@fisher1925$statistic, p = t@fisher1925$p.value, ci = t@zou2007$conf.int)",
                           packages=("cocor",), what="the test of two correlations (R cocor)",
                           python_note="SciPy and statsmodels have no test of two correlations",
                           r1=r1, r2=r2, n1=float(n1), n2=float(n2))
            z, p = float(np.asarray(found["z"])[0]), float(np.asarray(found["p"])[0])
            low, high = (float(v) for v in np.asarray(found["ci"], dtype=float))
            g1, g2 = (_label(g) for g in groups)
            print(f'The correlation between "{first}" and "{second}" is r = {r1:.2f} in {g1} ({n1} rows) and '
                  f"r = {r2:.2f} in {g2} ({n2} rows): a difference of {_num(r1 - r2)} (values from {_num(low)} to "
                  f"{_num(high)} fit the data, Zou's 95 % CI).")
            print(_p_sentence(p, "the two correlations were truly the same", "a difference this big or bigger",
                              "that the correlations are the same"))
            print(f"Test: Fisher's z test for two correlations in separate groups (z = {_num(z)}), as R "
                  "cocor::cocor.indep.groups(test = \"fisher1925\").")
            return self._result_table({"test": "Fisher's z test of two correlations", "what it compares":
                                       f'r of "{first}" and "{second}" in {g1} and {g2}', f"r in {g1}": r1,
                                       f"r in {g2}": r2, "difference": r1 - r2, "difference 95 % CI low": low,
                                       "difference 95 % CI high": high, "statistic name": "z", "statistic": z,
                                       "p-value": p, f"rows in {g1}": n1, f"rows in {g2}": n2})
        pairs = [list(v) if isinstance(v, (list, tuple)) else None for v in (first, second)]
        if None in pairs or any(len(p) != 2 or not all(isinstance(c, str) for c in p) for p in pairs):
            raise SimplydataError(f"{step}() needs two columns and for_each_group_in=, or two pairs of columns.\nFor example, "
                                  f'{example}\nor table.compare_correlations(["hours", "marks"], ["height", "marks"])')
        if for_each_group_in is not None:
            raise SimplydataError("Two pairs of columns are compared in the same rows; leave out for_each_group_in=.")
        shared = set(pairs[0]) & set(pairs[1])
        if len(shared) != 1 or len(set(pairs[0]) | set(pairs[1])) != 3:
            raise SimplydataError("The two pairs must share exactly one column, such as [\"hours\", \"marks\"] and "
                                  "[\"height\", \"marks\"]. (Pairs with no column in common are not offered.)")
        (j,) = shared
        k, h = (next(c for c in p if c != j) for p in pairs)
        names = [j, k, h]
        frame = self._number_frame(step, names)
        kept = frame.select(*names).drop_nulls()
        _skipped_note(len(frame) - len(kept), names)
        vj, vk, vh = (kept[c].to_numpy().astype(float) for c in names)
        rjk, rjh, rkh = _r(vj, vk), _r(vj, vh), _r(vk, vh)
        n = len(vj)
        found = r_call("t <- cocor::cocor.dep.groups.overlap(rjk, rjh, rkh, n, test = c('steiger1980', 'zou2007')); "
                       "list(z = t@steiger1980$statistic, p = t@steiger1980$p.value, ci = t@zou2007$conf.int)",
                       packages=("cocor",), what="the test of two correlations (R cocor)",
                       python_note="SciPy and statsmodels have no test of two correlations",
                       rjk=rjk, rjh=rjh, rkh=rkh, n=float(n))
        z, p = float(np.asarray(found["z"])[0]), float(np.asarray(found["p"])[0])
        low, high = (float(v) for v in np.asarray(found["ci"], dtype=float))
        print(f'"{j}" correlates r = {rjk:.2f} with "{k}" and r = {rjh:.2f} with "{h}" ({n} rows; "{k}" and "{h}" '
              f"correlate r = {rkh:.2f}): a difference of {_num(rjk - rjh)} (values from {_num(low)} to {_num(high)} "
              "fit the data, Zou's 95 % CI).")
        print(_p_sentence(p, "the two correlations were truly the same", "a difference this big or bigger",
                          "that the correlations are the same"))
        print(f"Test: Steiger's z test for two correlations that share a column, in the same rows (z = {_num(z)}), as "
              "R cocor::cocor.dep.groups.overlap(test = \"steiger1980\").")
        return self._result_table({"test": "Steiger's z test of two overlapping correlations", "what it compares":
                                   f'r of "{j}" with "{k}" and with "{h}"', f"r with {k}": rjk, f"r with {h}": rjh,
                                   f"r of {k} and {h}": rkh, "difference": rjk - rjh, "difference 95 % CI low": low,
                                   "difference 95 % CI high": high, "statistic name": "z", "statistic": z,
                                   "p-value": p, "rows": n})
