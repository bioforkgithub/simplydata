"""Table words for time series: table.find_autocorrelation_of(...), table.check_steady_over_time(...),
table.add_trend_and_season(...), table.find_trend_of(...) and find_correlation_between(..., rows_back=).

find_autocorrelation_of: statsmodels acf / pacf / acovf and acorr_ljungbox with R's options (see
simplydata._time_series).

check_steady_over_time runs R's own tests through rpy2 (simplydata[r]): the augmented Dickey-Fuller test as R
tseries::adf.test(x) (a constant and a straight-line trend in the test regression, trunc((n - 1)^(1/3))
rows back) and the KPSS test as R tseries::kpss.test(x, null = "Level" or "Trend"), with p-values read
from the published tables exactly as tseries does (outside the tables tseries gives the edge value,
0.01 or 0.1, and says the true p-value is smaller or greater; simplydata prints "below 0.01" or "above
0.1"). statsmodels adfuller gives the same ADF statistic but another p-value (MacKinnon's surface), so
it is not used.
"""

from __future__ import annotations

import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._time_axis import need_filled, need_regular, series_of
from .stat_tests import _p_sentence, _p_shown
from .. import _time_series

EXAMPLE = 'table.check_steady_over_time("signal", sorted_by="time")'
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


def _p_bounded(p, flag) -> str:
    """The p-value of a table-based test: "p below 0.01" when it lies past the end of the table."""
    if flag == "below":
        return f"p below {p:g}"
    if flag == "above":
        return f"p above {p:g}"
    return _p_shown(p)


class TimeSeriesWords:
    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_autocorrelation_of(self, column=None, sorted_by=None, rows_back=None, show="correlation",
                                band="white noise", for_each_group_in=None):
        """How much a column is like itself some rows back (autocorrelation), with a noise band.

        table.find_autocorrelation_of("signal", sorted_by="time", rows_back=40)   (with sdata.get_example("sensor"))
        The correlation of the column with itself 1, 2, ... rows_back= rows back (default as R:
        10 x log10 of the number of readings). A pattern that repeats every 12 rows shows as a high
        correlation 12 rows back. show="correlation" (R acf), "partial" (R pacf: each rows back with
        the shorter ones held fixed) or "covariance". band="white noise" (+/- 1.96 / sqrt(n), the
        dashed lines of R plot.acf) or "bartlett" (wider further back, R ci.type = "ma"). The
        Ljung-Box test asks whether all these correlations together could be chance. The readings
        must be evenly spaced (sorted_by=) and filled in. Numbers come from statsmodels with R's
        options. Gives back one row per rows back.
        """
        step_name = "find_autocorrelation_of"
        example = 'table.find_autocorrelation_of("signal", sorted_by="time")'
        self._need_name(step_name, "the column", column, example)
        series = series_of(self, column, sorted_by, for_each_group_in, step_name, example)
        groups = self._group_columns(step_name, for_each_group_in, [column]) if for_each_group_in is not None else []
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

    @friendly(renamed={"for_each": "for_each_group_in"})
    def check_steady_over_time(self, column=None, sorted_by=None, around="level", method="both", for_each_group_in=None):
        """Does a column stay steady over time, or does it wander? (ADF and KPSS tests, as R tseries)

        table.check_steady_over_time("signal", sorted_by="time")   (with sdata.get_example("sensor"))
        "Steady" (stationary) means the column keeps the same average and spread over time: it goes
        up and down around one level (around="level") or around one straight line (around="straight
        line"). Two tests that start from opposite assumptions run together (method="both"; "adf" or
        "kpss" for one): the augmented Dickey-Fuller test starts from "it wanders", so a small p-value
        says steady; the KPSS test starts from "steady", so a small p-value says it wanders. Both are
        R's own (tseries::adf.test, tseries::kpss.test), run through rpy2: needs simplydata[r] and R.
        The readings must be evenly spaced (sorted_by=) and filled in. Gives back one row per test.
        """
        step_name = "check_steady_over_time"
        self._need_name(step_name, "the column", column, EXAMPLE)
        if around not in AROUND:
            raise choice_error(step_name, "around", around, list(AROUND))
        test = TEST_ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
        if test not in TESTS:
            raise choice_error(step_name, "method", method, list(TESTS))
        series = series_of(self, column, sorted_by, for_each_group_in, step_name, EXAMPLE)
        groups = self._group_columns(step_name, for_each_group_in, [column]) if for_each_group_in is not None else []
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
            adf_text = f"ADF {_p_bounded(got['adf_p'], got['adf_flag'])}"
            kpss_text = f"KPSS {_p_bounded(got['kpss_p'], got['kpss_flag'])}"
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
                          "series close to the edge; look at chart.draw_lines(...) before deciding.")
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

    # ------------------------------------------------------------------ trend and season
    @friendly(renamed={"for_each": "for_each_group_in"})
    def add_trend_and_season(self, column=None, sorted_by=None, repeats_every=None, method="loess", season="added",
                             season_window=7, robust=False, for_each_group_in=None, names=None):
        """Split a column into a trend, a season that repeats, and the rest, as three new columns.

        table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year", for_each_group_in="museum")
        (with sdata.get_example("visitors")). Adds visitors_trend, visitors_season and visitors_rest (names=
        gives three other names); trend + season + rest = the column (season "added"). repeats_every= is
        the number of readings in one cycle (12, or "year" for monthly readings). method="loess" (the
        default, R stl(): statsmodels STL with R's settings; season_window= odd number of cycles, at least
        7, or "fixed" for the same season every cycle, which runs R stl(s.window = "periodic") itself and
        needs simplydata[r]; robust=True keeps outliers from pulling the trend), "moving averages" (R
        decompose(): statsmodels seasonal_decompose; season="multiplied" for a season that grows with the
        level) or "straight line" (R lm(): one statsmodels least-squares fit of a straight line over time and,
        with repeats_every=, an effect for each place in the cycle, the effects adding up to 0). One undo step.
        """
        from .. import _trend_season as ts

        step_name = "add_trend_and_season"
        example = 'table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year")'
        self._need_name(step_name, "the column", column, example)
        chosen = ts.TREND_ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
        if chosen not in ts.TREND_METHODS:
            raise choice_error(step_name, "method", method, list(ts.TREND_METHODS))
        kind = ts.SEASON_ALIASES.get(season, season) if isinstance(season, str) else season
        if kind not in ts.SEASONS:
            raise choice_error(step_name, "season", season, list(ts.SEASONS))
        if names is None:
            names = [f"{column}_trend", f"{column}_season", f"{column}_rest"]
        elif not (isinstance(names, (list, tuple)) and len(names) == 3 and all(isinstance(n, str) for n in names)):
            raise SimplydataError(f"{step_name}() needs names= as a list of three new column names: trend, season, rest.")
        taken = [n for n in names if n in self._columns]
        if taken:
            raise SimplydataError(f'"{taken[0]}" is already a column; give other names with names=[...].')
        series = series_of(self, column, sorted_by, for_each_group_in, step_name, example)
        n_rows = len(self._frame)
        filled = {name: np.full(n_rows, np.nan) for name in names}
        how = call = None
        for one in series:
            need_filled(one, column, step_name, sorted_by)
            if sorted_by is not None:
                need_regular(one, step_name, sorted_by)
            period = ts.read_repeats_every(repeats_every, one, step_name, needed=chosen != "straight line")
            got = ts.trend_and_season(one.values, period, chosen, kind, season_window, bool(robust), step_name)
            for name, part in zip(names, (got["trend"], got["season"], got["rest"])):
                filled[name][one.rows] = part
            how, call = got["how"], got["call"]
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            trend = got["trend"][~np.isnan(got["trend"])]
            cycle = f"a season that repeats every {period} readings, " if period else ""
            season_words = ""
            if period:
                low, high = float(np.nanmin(got["season"])), float(np.nanmax(got["season"]))
                if kind == "multiplied":
                    season_words = f" The season multiplies {column} by {_num(low)} to {_num(high)};"
                else:
                    season_words = f" The season moves {column} from {_num(low)} to +{_num(high)};"
            print(f"Split {what} into a trend, {cycle}and the rest.{season_words} the trend goes from "
                  f"{_num(trend[0])} to {_num(trend[-1])}; the rest has a standard deviation of "
                  f"{_num(float(np.nanstd(got['rest'], ddof=1)))}.")
        print(f"Method: {how}, as R {call}. Added {', '.join(names)}.")
        base = nw.maybe_reset_index(self._frame)
        new = [nw.new_series(name, [None if np.isnan(v) else float(v) for v in filled[name]], nw.Float64,
                             backend=base.implementation) for name in names]
        return self._change(f'add trend and season of "{column}"', base.with_columns(*new))

    # ------------------------------------------------------------------ find_trend_of
    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_trend_of(self, column=None, sorted_by=None, repeats_every=None, for_each_group_in=None):
        """Does a column keep rising or falling over time, and by how much? (Mann-Kendall test, Sen's slope)

        table.find_trend_of("visitors", sorted_by="month", for_each_group_in="museum")   (with sdata.get_example("visitors"))
        Sen's slope is the middle (median) of the slopes between every pair of readings, so a few odd
        readings do not move it, with its 95 % interval (SciPy theilslopes, as R trend::sens.slope): the
        change per reading in table order, per month (quarter, year) for dates one calendar step apart,
        and per day (or second, or unit of sorted_by) otherwise, worked out on the times themselves so
        weekly readings and gaps count right; also per year. The Mann-Kendall test asks
        whether a rise or fall that keeps going one way could be chance; it runs in R itself
        (trend::mk.test, needs simplydata[r]). With repeats_every= (12, or "year") the seasonal test and
        seasonal slope compare each month only with the same month in other years (R trend::smk.test,
        trend::sea.sens.slope, both in R; the slope is per cycle, per year for 12 months; the readings
        must be evenly spaced). Without R the slope (not the seasonal one) is still given and
        a note says how to add the test.
        """
        from scipy import stats

        from .. import _trend_season as ts

        step_name = "find_trend_of"
        example = 'table.find_trend_of("visitors", sorted_by="month")'
        self._need_name(step_name, "the column", column, example)
        series = series_of(self, column, sorted_by, for_each_group_in, step_name, example)
        groups = self._group_columns(step_name, for_each_group_in, [column]) if for_each_group_in is not None else []
        per_year = {"months": 12, "quarters": 4, "days": 365.25}
        rows, missing_note, period = [], None, None
        for one in series:
            need_filled(one, column, step_name, sorted_by)
            if len(one.values) < 4:
                raise SimplydataError(f"{step_name}() needs at least 4 readings; there are {len(one.values)}.")
            period = ts.read_repeats_every(repeats_every, one, step_name, needed=False)
            if period is not None and sorted_by is not None:
                need_regular(one, step_name, sorted_by)  # the seasonal test compares readings a cycle apart
            test, missing = ts.mann_kendall(one.values, period)
            missing_note = missing_note or missing
            calendar = one.unit in ("months", "quarters", "years")  # one reading every calendar step, no gaps
            if one.times is None:
                unit = "reading"
            elif calendar or one.unit in ("days", "seconds"):
                unit = one.unit[:-1]
            else:
                unit = f'1 in "{one.unit}"'
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            if period is None:
                if one.times is None or calendar:  # per reading = per row, or per calendar step
                    slope, low, high = ts.sen_slope(one.values)
                else:  # Sen's slope per unit of time (days, seconds, sorted_by), on the (time, value) pairs
                    fit = stats.theilslopes(one.values, one.times, alpha=0.95)
                    slope, low, high = float(fit.slope), float(fit.low_slope), float(fit.high_slope)
            else:
                slope = test["slope"] if test else math.nan
                low = high = math.nan
            # the change per year: Sen's slope is per unit (per reading for calendar steps); the seasonal slope
            # (R trend::sea.sens.slope) compares readings one cycle apart, so it is per cycle of `period` readings
            step = one.step if one.times is not None and not calendar else 1.0  # time units per reading
            per_unit = slope if period is None else slope / (period * step)
            yearly_value = per_unit * per_year[one.unit] if one.unit in per_year else math.nan
            if period is not None and per_year.get(one.unit) == period:
                cycle_words = "year"  # 12 months or 4 quarters: the cycle is a year
            elif period is not None:
                cycle_words = f"cycle of {period} readings"
            if math.isnan(slope):
                slope_words = "has its seasonal slope only with R"
            else:
                way = "rises" if slope > 0 else "falls" if slope < 0 else "stays level"
                interval = f"; 95 % CI {_num(low)} to {_num(high)}" if not math.isnan(low) else ""
                if period is None:
                    yearly = f" ({_num(abs(yearly_value))} a year)" if not math.isnan(yearly_value) else ""
                    slope_words = f"{way} by {_num(abs(slope))} per {unit}{yearly} (Sen's slope{interval})"
                else:
                    slope_words = f"{way} by {_num(abs(slope))} per {cycle_words} (seasonal Sen's slope{interval})"
            if test:
                test_name = "seasonal Mann-Kendall" if period else "Mann-Kendall"
                print(f"{what} {slope_words}. " + _p_sentence(
                    test["p"], "there were truly no trend", "a trend this steady or steadier",
                    "that there is no trend", shown=f"{test_name}, {_p_shown(test['p'])}"))
            else:
                print(f"{what} {slope_words}.")
            row = {", ".join(groups): one.label} if groups else {}
            row.update({"slope": slope, "95 % CI low": low, "95 % CI high": high})
            if one.unit in per_year:
                row["slope per year"] = yearly_value
            row.update({"z": test["z"] if test else math.nan, "p-value": test["p"] if test else math.nan})
            if period is None:
                row.update({"S": test["S"] if test else math.nan, "Kendall's tau": test["tau"] if test else math.nan})
            row["rows"] = int(len(one.values))
            rows.append(row)
        if missing_note:
            print("Note: the Mann-Kendall test was left out. " + missing_note)
        if period is None:
            print("Method: Sen's slope with its 95 % interval, as R trend::sens.slope() (SciPy theilslopes); "
                  "Mann-Kendall test with continuity correction, as R trend::mk.test() (run in R).")
        else:
            print(f"Method: seasonal Mann-Kendall test and seasonal Sen's slope over cycles of {period} readings, as R "
                  "trend::smk.test() and trend::sea.sens.slope() (run in R).")
        keys = list(dict.fromkeys(k for r in rows for k in r))
        data = {key: [r.get(key, math.nan) for r in rows] for key in keys}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ find_correlation_between(rows_back=)
    def _cross_correlation(self, step, names, rows_back, sorted_by):
        """find_correlation_between(a, b, rows_back=k): the cross-correlation for shifts -k to k."""
        from .. import _trend_season as ts
        from .._time_series import read_rows_back

        if len(names) != 2:
            raise SimplydataError(f"{step}() with rows_back= needs exactly two columns.")
        a_name, b_name = names
        example = f'table.{step}("{a_name}", "{b_name}", rows_back=12, sorted_by="date")'
        first = series_of(self, a_name, sorted_by, None, step, example)[0]
        second = series_of(self, b_name, sorted_by, None, step, example)[0]
        need_filled(first, a_name, step, sorted_by)
        need_filled(second, b_name, step, sorted_by)
        if sorted_by is not None:
            need_regular(first, step, sorted_by)
        k = read_rows_back(rows_back, len(first.values), step)
        shifts, values, half = ts.cross_correlation(first.values, second.values, k)
        best = int(np.argmax(np.abs(values)))
        s, r = int(shifts[best]), float(values[best])
        rows_word = "rows" if abs(s) != 1 else "row"
        if s > 0:
            lead = (f'"{b_name}" follows "{a_name}" by {s} {rows_word}: the strongest correlation (r = {_num(r)}) '
                    f"pairs {a_name} with {b_name} {s} {rows_word} later.")
        elif s < 0:
            lead = (f'"{a_name}" follows "{b_name}" by {-s} {rows_word}: the strongest correlation (r = {_num(r)}) '
                    f"pairs {b_name} with {a_name} {-s} {rows_word} later.")
        else:
            lead = f'"{a_name}" and "{b_name}" go together best in the same row (r = {_num(r)}).'
        outside = int((np.abs(values) > half).sum())
        print(f"{lead} {outside} of the {len(values)} shifts are outside the band expected from random noise "
              f"(+/- {_num(half)}).")
        print(f"Method: cross-correlation for shifts -{k} to {k}, as R ccf({a_name}, {b_name}, lag.max = {k}) with the "
              f"sign of the lag reversed (shift s pairs {a_name} at row t with {b_name} at row t + s); statsmodels "
              "ccf. A correlation does not show that one thing causes the other.")
        data = {"shift": [int(v) for v in shifts], "correlation": [float(v) for v in values],
                "band low": [-half] * len(values), "band high": [half] * len(values),
                "outside band": ["yes" if abs(v) > half else "no" for v in values]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))


def _num(x) -> str:
    from .stat_tests import _num as num

    return num(x)

