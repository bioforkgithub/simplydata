"""Table words for forecasts and change points: table.forecast(...), table.compare_forecasts(...) and
table.find_change_points(...). Every number comes from R itself (simplydata[r]); see
simplydata._forecast for the R calls and why Python's packages are not used.
"""

from __future__ import annotations

import math

import narwhals as nw
import numpy as np

from .. import _forecast as fc
from .._errors import SimplydataError, choice_error, friendly
from .._time_axis import future_times, need_filled, need_regular, series_of
from .stat_tests import _num, _p_shown

SHOWS = ("forecast", "model")
CALENDAR_WORDS = {"months": "month", "quarters": "quarter", "years": "year"}


def _time_value(value):
    """A sorted_by value as a plain Python value for a new table."""
    import pandas as pd

    if isinstance(value, (np.datetime64, pd.Timestamp)):
        return pd.Timestamp(value).to_pydatetime()
    return value.item() if hasattr(value, "item") else value


def _shown(value) -> str:
    import datetime

    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d") if (value.hour, value.minute, value.second) == (0, 0, 0) else str(value)
    return _num(value) if isinstance(value, float) else str(value)


def _unit(series):
    """'month', 'quarter', 'year', 'day' (one reading a day), or None."""
    unit = CALENDAR_WORDS.get(series.unit)
    if unit is None and series.unit == "days" and series.step == 1:
        unit = "day"
    return unit


def _ahead_words(series, k: int, first: bool) -> str:
    """'Next month' / 'in 12 months', or '1 step ahead' / '12 steps ahead'."""
    unit = _unit(series)
    if unit:
        return f"Next {unit}" if first else f"in {k} {unit}s"
    return f"{k} step{'s' if k != 1 else ''} ahead"


def _next_words(series, k: int) -> str:
    """'the next 12 months' or 'the next 12 steps'."""
    unit = _unit(series) or "step"
    return f"the next {unit}" if k == 1 else f"the next {k} {unit}s"


def _box_words(box, lag) -> str:
    stat, p = box
    if math.isnan(p):
        return ""
    if p < 0.05:
        return (f" The leftover one-step errors still hold a pattern (Ljung-Box up to {lag} rows back, "
                f"{_p_shown(p)}): another method may do better.")
    return f" The leftover one-step errors look like noise (Ljung-Box up to {lag} rows back, {_p_shown(p)})."


def _model_words(method, got) -> str:
    if method == "exponential smoothing":
        alpha, beta, gamma = got["estimates"][:3]
        parts = [f"weight on the newest level {_num(alpha)}"]
        if not math.isnan(beta):
            parts.append(f"on the newest trend {_num(beta)}")
        if not math.isnan(gamma):
            parts.append(f"on the newest season {_num(gamma)}")
        return ": " + ", ".join(parts)
    if method == "arima":
        coefs = [f"{t} {_num(e)}" for t, e in zip(got["terms"], got["estimates"])
                 if t not in ("sigma^2", "log-likelihood", "AIC")]
        return (": estimates " + ", ".join(coefs)) if coefs else ""
    return ""


def _accuracy_words(accuracy, scale_words) -> str:
    mae, rmse, mape, mase = accuracy
    mape_words = f", MAPE {_num(mape)} %" if math.isfinite(mape) else ""
    return (f"off by {_num(mae)} on average (MAE; RMSE {_num(rmse)}{mape_words}, MASE {_num(mase)}: below 1 means "
            f"better than {scale_words})")


class ForecastWords:
    def _forecast_series(self, step_name, column, sorted_by, for_each, method, example):
        """Each series, checked: filled (ARIMA may have empty cells) and evenly spaced."""
        series = series_of(self, column, sorted_by, for_each, step_name, example)
        for one in series:
            if method != "arima":
                need_filled(one, column, step_name, sorted_by)
            if sorted_by is not None:
                need_regular(one, step_name, sorted_by)
        return series

    @friendly
    def forecast(self, column=None, sorted_by=None, steps_ahead=12, method="exponential smoothing",
                 repeats_every=None, trend=True, season="added", order=None, seasonal_order=None, interval=95,
                 check_on_last=None, show="forecast", for_each=None):
        """Forecast the next values of a column, with an interval for each.

        table.forecast("visitors", sorted_by="month", steps_ahead=12, repeats_every="year", for_each="museum")
        (with sdata.example("visitors")). Gives back one row per future step: the sorted_by column carried
        on (months stay months), the forecast and its interval= (95 %) low and high. method=
        "exponential smoothing" (the default: Holt-Winters, a level, a trend unless trend=False, and a
        season with repeats_every=, season "added" or "multiplied"; R HoltWinters), "last value" (R
        forecast::naive), "same season last time" (R snaive), "average" (R meanf), "straight on" (the
        line from the first to the last reading carried on: R rwf(drift = TRUE)) or "arima" (R arima
        with order=(p, d, q): past values, differences, past errors; seasonal_order= the same for the
        season; empty cells allowed). check_on_last=12 fits on all but the last 12 rows, forecasts them
        and says how far off it was (R forecast::accuracy: MAE, RMSE, MAPE, MASE); the table gains the
        actual values and the errors. show="model" gives the fitted weights or estimates instead. All in
        R itself: needs simplydata[r] and R with the forecast package.
        """
        step_name = "forecast"
        example = 'table.forecast("visitors", sorted_by="month", repeats_every="year")'
        self._need_name(step_name, "the column", column, example)
        chosen = fc.read_method(method, step_name)
        if show not in SHOWS:
            raise choice_error(step_name, "show", show, list(SHOWS))
        if show == "model" and chosen not in ("exponential smoothing", "arima"):
            raise SimplydataError('show="model" is for method="exponential smoothing" or "arima" (the other methods '
                                  "have nothing fitted to show).")
        kind = {"additive": "added", "multiplicative": "multiplied"}.get(season, season)
        if kind not in ("added", "multiplied"):
            raise choice_error(step_name, "season", season, ["added", "multiplied"])
        steps = fc.read_whole(steps_ahead, "steps_ahead", step_name)
        level = fc.read_interval(interval, step_name)
        order = fc.read_order(order, "order", step_name)
        seasonal_order = fc.read_order(seasonal_order, "seasonal_order", step_name)
        held = None if check_on_last is None else fc.read_whole(check_on_last, "check_on_last", step_name)
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        from .. import _trend_season as ts

        rows, how = [], None
        for one in self._forecast_series(step_name, column, sorted_by, for_each, chosen, example):
            period = ts.read_repeats_every(repeats_every, one, step_name, needed=False)
            n = len(one.values)
            if held is not None and held > n - 3:
                raise SimplydataError(f"check_on_last={held} leaves too few readings to fit ({n} in all).")
            fit_values = one.values if held is None else one.values[: n - held]
            fc.check_options(chosen, period, len(fit_values), kind, order, seasonal_order, step_name)
            if chosen == "arima" and np.isnan(fit_values).any():
                print(f"Note: {int(np.isnan(fit_values).sum())} empty cells are left as gaps; ARIMA handles them, "
                      "as R arima.")
            ahead = steps if held is None else held
            got = fc.r_forecast(fit_values, period, chosen, ahead, level, bool(trend), kind, order, seasonal_order,
                                test=None if held is None else one.values[n - held:])
            name, words, call = fc.method_words(chosen, period, bool(trend), kind, order, seasonal_order)
            how = (name, words, call)
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            label = {", ".join(groups): one.label} if groups else {}
            if show == "model":
                for term, estimate, error in zip(got["terms"], got["estimates"], got["errors"]):
                    rows.append({**label, "term": term, "estimate": float(estimate), "standard error": float(error)})
                print(f"Fitted {what} by {name} ({words}){_model_words(chosen, got)}.")
                continue
            lag = fc.box_lag(int((~np.isnan(fit_values)).sum()), period)
            mean, low, high = got["mean"], got["low"], got["high"]
            if held is None:
                times = future_times(self, one, sorted_by, ahead) if sorted_by is not None else None
                first, last = _ahead_words(one, 1, True), _ahead_words(one, ahead, False)
                text = (f"Forecast of {what} for {_next_words(one, ahead)} by {name} ({words})"
                        f"{_model_words(chosen, got)}. {first}: {_num(mean[0])} ({level:g} % prediction interval "
                        f"{_num(low[0])} to {_num(high[0])})")
                if ahead > 1:
                    text += f"; {last}: {_num(mean[-1])} ({_num(low[-1])} to {_num(high[-1])})"
                print(text + "." + _box_words(got["box"], lag))
            else:
                raw = self._frame[sorted_by].to_numpy() if sorted_by is not None else None
                times = [_time_value(raw[r]) for r in one.rows[n - held:]] if raw is not None else None
                scale = "the same season last time" if period and period > 1 else "the last value"
                print(f"Checked on the last {held} readings of {what}: {name} ({words}), fitted on the readings "
                      f"before{_model_words(chosen, got)}, was {_accuracy_words(got['accuracy'], scale)}.")
            for j in range(ahead):
                row = dict(label)
                if times is not None:
                    row[sorted_by] = times[j]
                row.update({"steps ahead": j + 1, "forecast": float(mean[j]),
                            f"forecast {level:g} % prediction low": float(low[j]),
                            f"forecast {level:g} % prediction high": float(high[j])})
                if held is not None:
                    actual = float(one.values[n - held + j])
                    row.update({"actual": actual, "error": actual - float(mean[j])})
                row["method"] = chosen
                rows.append(row)
        name, words, call = how
        extra = "; accuracy as R forecast::accuracy(f, held-back readings)" if held is not None else ""
        interval_words = f"; {level:g} % intervals" if show == "forecast" else ""
        print(f"Method: {name} ({words}), as R {call}{interval_words}{extra} (run in R).")
        data = {key: [r[key] for r in rows] for key in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    @friendly
    def compare_forecasts(self, column=None, sorted_by=None, methods=None, check_on_last=12, repeats_every=None,
                          order=None, seasonal_order=None, for_each=None):
        """Which forecast method would have done best on the last rows? (R forecast::accuracy)

        table.compare_forecasts("visitors", sorted_by="month", repeats_every="year", for_each="museum")
        (with sdata.example("visitors")). Each method in methods= is fitted on all but the last
        check_on_last= rows (12) and forecasts them; the methods are ranked by MASE, the average error
        divided by the average error of the simplest forecast inside the fitted rows (the same season
        last time with repeats_every=, otherwise the last value): below 1 is better than that. Also MAE
        (the average size of the errors), RMSE and MAPE (the average error in % of the actual values).
        methods= defaults to "last value", "same season last time" (with repeats_every=; else "average"),
        "straight on" and "exponential smoothing"; "arima" needs order=. Runs in R itself (simplydata[r]).
        Gives back one row per method.
        """
        step_name = "compare_forecasts"
        example = 'table.compare_forecasts("visitors", sorted_by="month", repeats_every="year")'
        self._need_name(step_name, "the column", column, example)
        if methods is None:
            chosen = None
        else:
            if isinstance(methods, str):
                methods = [methods]
            chosen = list(dict.fromkeys(fc.read_method(m, step_name) for m in methods))
            if len(chosen) < 2:
                raise SimplydataError(f"{step_name}() needs at least two methods to compare, such as "
                                      'methods=["last value", "exponential smoothing"].')
        held = fc.read_whole(check_on_last, "check_on_last", step_name)
        order = fc.read_order(order, "order", step_name)
        seasonal_order = fc.read_order(seasonal_order, "seasonal_order", step_name)
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        from .. import _trend_season as ts

        any_arima = chosen is not None and "arima" in chosen
        rows, scale = [], None
        for one in self._forecast_series(step_name, column, sorted_by, for_each, "arima" if any_arima else "", example):
            period = ts.read_repeats_every(repeats_every, one, step_name, needed=False)
            seasonal = bool(period and period > 1)
            these = chosen or ["last value", "same season last time" if seasonal else "average", "straight on",
                               "exponential smoothing"]
            n = len(one.values)
            if held > n - 3:
                raise SimplydataError(f"check_on_last={held} leaves too few readings to fit ({n} in all).")
            train, test = one.values[: n - held], one.values[n - held:]
            if np.isnan(test).any() or (np.isnan(train).any() and these != ["arima"]):
                need_filled(one, column, step_name, sorted_by)
            scale = "the same season last time" if seasonal else "the last value"
            results = []
            for method in these:
                fc.check_options(method, period, len(train), "added", order if method == "arima" else None,
                                 seasonal_order if method == "arima" else None, step_name)
                got = fc.r_forecast(train, period, method, held, 95.0, True, "added",
                                    order if method == "arima" else None,
                                    seasonal_order if method == "arima" else None, test=test)
                results.append((method, got["accuracy"]))
            ranked = sorted(results, key=lambda item: (math.isnan(item[1][3]), item[1][3]))
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            best, *others = ranked
            then = ", ".join(f"{m} ({_num(a[3])})" for m, a in others)
            print(f"Best on the last {held} readings of {what}: {best[0]} (MASE {_num(best[1][3])}), then {then}. "
                  f"Below 1 means better than {scale}.")
            for rank, (method, accuracy) in enumerate(ranked, start=1):
                row = {", ".join(groups): one.label} if groups else {}
                row.update({"method": method, "MAE": float(accuracy[0]), "RMSE": float(accuracy[1]),
                            "MAPE": float(accuracy[2]), "MASE": float(accuracy[3]), "rank": rank})
                rows.append(row)
        print(f"Method: each method fitted on all but the last {held} readings and checked on them, as R "
              "forecast::accuracy(f, held-back readings) (MASE scaled by the in-sample error of "
              f"{'forecast::snaive' if scale.startswith('the same') else 'forecast::naive'}); run in R.")
        data = {key: [r[key] for r in rows] for key in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    @friendly
    def find_change_points(self, column=None, sorted_by=None, change="average", penalty="mbic", for_each=None):
        """Find the points where the average of a column jumps to a new level (R changepoint, PELT).

        table.find_change_points("nitrate", sorted_by="date", for_each="station")   (with sdata.example("river"))
        Splits the readings, in the order of sorted_by=, into pieces with their own average, and gives
        back one row per piece: where it starts and ends, how many readings, its average (and its
        standard deviation). change="average" (R changepoint::cpt.mean, after dividing the readings by
        mad(diff(x)) / sqrt(2): simplydata's choice of noise size, because cpt.mean assumes noise with
        standard deviation 1 and changepoint itself does not scale) or "average and spread"
        (R cpt.meanvar: the spread may jump too). The search is PELT; penalty= "mbic" (the default, as
        R), "bic", "aic" or "hannan-quinn" sets how big a jump must be to count (a smaller penalty, such
        as "aic", finds more points). The readings are taken in order; they need no empty cells. Runs
        in R itself (simplydata[r]).
        """
        step_name = "find_change_points"
        example = 'table.find_change_points("nitrate", sorted_by="date", for_each="station")'
        self._need_name(step_name, "the column", column, example)
        kind = fc.read_change(change, step_name)
        chosen_penalty = fc.read_penalty(penalty, step_name)
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        raw = self._frame[sorted_by].to_numpy() if sorted_by is not None else None
        rows = []
        for one in series_of(self, column, sorted_by, for_each, step_name, example):
            need_filled(one, column, step_name, sorted_by)
            if len(one.values) < 4:
                raise SimplydataError(f"{step_name}() needs at least 4 readings; there are {len(one.values)}.")
            got = fc.r_change_points(one.values, kind, chosen_penalty)
            starts, ends = got["starts"], got["ends"]
            if raw is not None:
                first = [_time_value(raw[one.rows[s - 1]]) for s in starts]
                last = [_time_value(raw[one.rows[e - 1]]) for e in ends]
                before, after = "up to", "from"
            else:
                first, last = [int(s) for s in starts], [int(e) for e in ends]
                before, after = "up to reading", "from reading"
            what = f'"{column}"' + (f" for {one.label}" if one.label else "")
            count = len(starts) - 1
            if count == 0:
                print(f"{what} has no change point: its average stays near {_num(got['average'][0])}.")
            else:
                pieces = [f"{_num(got['average'][0])} {before} {_shown(last[0])}"]
                for j in range(1, count):
                    pieces.append(f"{_num(got['average'][j])} from {_shown(first[j])} to {_shown(last[j])}")
                pieces.append(f"{_num(got['average'][-1])} {after} {_shown(first[-1])} on")
                times = "once" if count == 1 else "twice" if count == 2 else f"{count} times"
                print(f"{what} changes {times}: the average is " + ", then ".join(pieces) + ".")
            for j in range(len(starts)):
                row = {", ".join(groups): one.label} if groups else {}
                row.update({"piece": j + 1, "from": first[j], "to": last[j],
                            "readings": int(ends[j] - starts[j] + 1), "average": float(got["average"][j]),
                            "standard deviation": float(got["spread"][j])})
                rows.append(row)
        call = ('changepoint::cpt.mean(x / s, method = "PELT", penalty = "{p}"), where s = mad(diff(x)) / sqrt(2). '
                "Dividing by s is simplydata's choice, not part of changepoint: cpt.mean assumes noise with "
                "standard deviation 1, and s is the noise size read from the differences between neighbours, "
                "so the jumps themselves do not inflate it" if kind == "average" else
                'changepoint::cpt.meanvar(x, method = "PELT", penalty = "{p}")').format(p=fc.PENALTIES[chosen_penalty])
        print(f"Method: PELT search for changes in the {kind} with the {fc.PENALTIES[chosen_penalty]} penalty, as R "
              f"{call} (run in R).")
        data = {key: [r[key] for r in rows] for key in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))
