"""Table words for time series: table.autocorrelation_of(...), table.check_steady(...).

autocorrelation_of: statsmodels acf / pacf / acovf and acorr_ljungbox with R's options (see
simplydata._time_series).

check_steady runs R's own tests through rpy2 (simplydata[r]): the augmented Dickey-Fuller test as R
tseries::adf.test(x) (a constant and a straight-line trend in the test regression, trunc((n - 1)^(1/3))
rows back) and the KPSS test as R tseries::kpss.test(x, null = "Level" or "Trend"), with p-values read
from the published tables exactly as tseries does (outside the tables tseries gives the edge value,
0.01 or 0.1, and says the true p-value is smaller or greater; simplydata prints "below 0.01" or "above
0.1"). statsmodels adfuller gives the same ADF statistic but another p-value (MacKinnon's surface), so
it is not used.
"""

from __future__ import annotations

import narwhals as nw

from .._errors import SimplydataError, choice_error, friendly
from .._time_axis import need_filled, need_regular, series_of
from .stat_tests import _p_shown
from .. import _time_series

EXAMPLE = 'table.check_steady("signal", sorted_by="time")'
AROUND = {"level": "Level", "straight line": "Trend"}
TESTS = ("both", "adf", "kpss")
TEST_ALIASES = {"augmented dickey-fuller": "adf", "dickey-fuller": "adf", "adf.test": "adf", "kpss.test": "kpss"}

_R_CODE = """
caught <- character(0)
catch <- function(expr) withCallingHandlers(expr, warning = function(c) {
  caught <<- c(caught, conditionMessage(c)); invokeRestart("muffleWarning") })
flag <- function(w) if (any(grepl("smaller", w))) "below" else if (any(grepl("greater", w))) "above" else "exact"
a <- catch(tseries::adf.test(x)); wa <- caught; caught <- character(0)
k <- catch(tseries::kpss.test(x, null = NULL_KIND)); wk <- caught
list(adf_stat = unname(a$statistic), adf_lag = unname(a$parameter), adf_p = a$p.value, adf_flag = flag(wa),
     kpss_stat = unname(k$statistic), kpss_lag = unname(k$parameter), kpss_p = k$p.value, kpss_flag = flag(wk))
"""


def _p_words(p, flag) -> str:
    if flag == "below":
        return f"p below {p:g}"
    if flag == "above":
        return f"p above {p:g}"
    return _p_shown(p)


class TimeSeriesWords:
    @friendly
    def autocorrelation_of(self, column=None, sorted_by=None, rows_back=None, show="correlation",
                           band="white noise", for_each=None):
        """How much a column is like itself some rows back (autocorrelation), with a noise band.

        table.autocorrelation_of("signal", sorted_by="time", rows_back=40)   (with sdata.example("sensor"))
        The correlation of the column with itself 1, 2, ... rows_back= rows back (default as R:
        10 x log10 of the number of readings). A pattern that repeats every 12 rows shows as a high
        correlation 12 rows back. show="correlation" (R acf), "partial" (R pacf: each rows back with
        the shorter ones held fixed) or "covariance". band="white noise" (+/- 1.96 / sqrt(n), the
        dashed lines of R plot.acf) or "bartlett" (wider further back, R ci.type = "ma"). The
        Ljung-Box test asks whether all these correlations together could be chance. The readings
        must be evenly spaced (sorted_by=) and filled in. Numbers come from statsmodels with R's
        options. Gives back one row per rows back.
        """
        step_name = "autocorrelation_of"
        example = 'table.autocorrelation_of("signal", sorted_by="time")'
        self._need_name(step_name, "the column", column, example)
        series = series_of(self, column, sorted_by, for_each, step_name, example)
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        rows, method = [], None
        for one in series:
            need_filled(one, column, step_name, sorted_by)
            if sorted_by is not None:
                need_regular(one, step_name, sorted_by)
            got = _time_series.autocorrelation(one.values, rows_back, show, band, step_name)
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            print(_time_series.sentence(got, what, show, band))
            method = _time_series.method_sentence(show, band, got["k"])
            for j in range(got["k"]):
                row = {", ".join(groups): one.label} if groups else {}
                row.update({"rows back": int(got["rows_back"][j]), got["column"]: float(got["values"][j]),
                            "band low": float(got["low"][j]), "band high": float(got["high"][j]),
                            "outside band": "yes" if got["outside"][j] else "no",
                            "Ljung-Box statistic": got["ljung_box"][0], "Ljung-Box p-value": got["ljung_box"][1]})
                rows.append(row)
        print(method)
        data = {key: [r[key] for r in rows] for key in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    @friendly
    def check_steady(self, column=None, sorted_by=None, around="level", method="both", for_each=None):
        """Does a column stay steady over time, or does it wander? (ADF and KPSS tests, as R tseries)

        table.check_steady("signal", sorted_by="time")   (with sdata.example("sensor"))
        "Steady" (stationary) means the column keeps the same average and spread over time: it goes
        up and down around one level (around="level") or around one straight line (around="straight
        line"). Two tests that start from opposite assumptions run together (method="both"; "adf" or
        "kpss" for one): the augmented Dickey-Fuller test starts from "it wanders", so a small p-value
        says steady; the KPSS test starts from "steady", so a small p-value says it wanders. Both are
        R's own (tseries::adf.test, tseries::kpss.test), run through rpy2: needs simplydata[r] and R.
        The readings must be evenly spaced (sorted_by=) and filled in. Gives back one row per test.
        """
        step_name = "check_steady"
        self._need_name(step_name, "the column", column, EXAMPLE)
        if around not in AROUND:
            raise choice_error(step_name, "around", around, list(AROUND))
        test = TEST_ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
        if test not in TESTS:
            raise choice_error(step_name, "method", method, list(TESTS))
        series = series_of(self, column, sorted_by, for_each, step_name, EXAMPLE)
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        from .._r import r_call

        rows = []
        for one in series:
            need_filled(one, column, step_name, sorted_by)
            if sorted_by is not None:
                need_regular(one, step_name, sorted_by)
            if len(one.values) < 10:
                raise SimplydataError(f"{step_name}() needs at least 10 readings; there are {len(one.values)}.")
            out = r_call(_R_CODE.replace("NULL_KIND", f'"{AROUND[around]}"'), packages=("tseries",),
                         what="The steady check (R tseries::adf.test() and kpss.test())",
                         python_note="statsmodels adfuller and kpss are similar, but their p-values come from other "
                                     "tables, so they differ", source="tseries", x=one.values)
            got = {k: (v.tolist()[0] if hasattr(v, "tolist") else v) for k, v in out.items()}
            adf_steady = got["adf_p"] < 0.05
            kpss_wanders = got["kpss_p"] < 0.05
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            shape = "a steady level" if around == "level" else "a steady straight line"
            adf_text = f"ADF {_p_words(got['adf_p'], got['adf_flag'])}"
            kpss_text = f"KPSS {_p_words(got['kpss_p'], got['kpss_flag'])}"
            if test == "both":
                if adf_steady and not kpss_wanders:
                    reading = "steady"
                    print(f"{what} looks steady: it stays around {shape} (both tests agree: {adf_text}, {kpss_text}).")
                elif not adf_steady and kpss_wanders:
                    reading = "wanders"
                    print(f"{what} wanders: it does not stay around {shape} (both tests agree: {adf_text}, "
                          f"{kpss_text}). The changes from one reading to the next are often steady: "
                          "table.add_change_column(...), then check again.")
                else:
                    reading = "the tests disagree"
                    print(f"The two tests disagree about {what} ({adf_text}, {kpss_text}), a common sign of a "
                          "series close to the edge; look at chart.lines(...) before deciding.")
            elif test == "adf":
                reading = "steady" if adf_steady else "could easily wander"
                print(f"{what} {'looks steady' if adf_steady else 'may wander: the ADF test cannot show it is steady'}"
                      f" ({adf_text}).")
            else:
                reading = "wanders" if kpss_wanders else "could well be steady"
                print(f"{what} {'wanders' if kpss_wanders else 'could well be steady'} ({kpss_text}).")
            for kind in (("adf", "kpss") if test == "both" else (test,)):
                row = {}
                if groups:
                    row[", ".join(groups)] = one.label
                row.update({
                    "test": "augmented Dickey-Fuller" if kind == "adf" else "KPSS",
                    "starting assumption": "it wanders (unit root)" if kind == "adf" else f"steady around {around}",
                    "statistic": float(got[f"{kind}_stat"]), "rows back": float(got[f"{kind}_lag"]),
                    "p-value": float(got[f"{kind}_p"]), "p-value is": got[f"{kind}_flag"], "reading": reading})
                rows.append(row)
        null = f'"{AROUND[around]}"'
        print("Method: " + ("augmented Dickey-Fuller test with a constant and a straight-line trend, as R "
                            "tseries::adf.test(x)" if test in ("both", "adf") else "")
              + ("; " if test == "both" else "")
              + (f"KPSS test, as R tseries::kpss.test(x, null = {null})" if test in ("both", "kpss") else "")
              + "; p-values from the published tables, as tseries (run in R).")
        data = {key: [r[key] for r in rows] for key in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))
