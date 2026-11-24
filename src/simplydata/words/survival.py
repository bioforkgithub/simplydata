"""Survival curves on charts: the Kaplan-Meier estimate as steps, and the chance of an event as rising steps.

The numbers are those of table.find_survival_over_time() (simplydata.table.survival.kaplan_meier,
the same as R survfit()): each curve starts at 1 at time 0, drops at each event time and
ends at the last time followed in its group, as R plot(survfit(...)). Censored rows are
small upright ticks on the curve at their time. with_confidence_band=True shades the 95 %
confidence interval (log scale, R's default conf.type = "log"). with_at_risk_table=True writes
the number still at risk (time at or after the tick) under each tick of the x-axis, one row
per group, as in papers. followed_from= gives each row its start time (delayed entry); allowing_for= draws
curves adjusted for other columns by direct adjustment (R adjustedCurves, as find_survival_over_time).

draw_risk_curves draws the numbers of table.find_risk_over_time(): the chance of having had the event by each
time, rising from 0 (Aalen-Johansen with competing_with=, through R; else 1 minus Kaplan-Meier).
"""

from __future__ import annotations

from .._typing import _Same

import numpy as np
import pandas as pd

from .._errors import SimplydataError, friendly
from ..table.survival import (_is_number, _kinds, _key, check_entry, check_time, group_order, is_empty,
                              kaplan_meier, kinds_error, read_event, read_states)
from ._helpers import check, check_thickness, check_transparency, colour_role, default_colour, opacity, palette_for
from .charts import BAND_SHADE, _apply_order, _remember

Y_LABEL = "Survival (share without the event)"
RISK_LINE = 11  # points between the rows of the at-risk table


def _rows_used(data, time, event, group, more=()):
    """The rows with time, event (and group, and the other columns used) filled in, as plain lists."""
    columns = [c for c in (time, event, group, *more) if c]
    empty = data[columns].map(is_empty).any(axis=1)
    return data.loc[~empty]


def _group_names(ctx, table, group):
    """Groups A to Z (as the table words), or in the order of order_legend() / a category column.
    Taken from the whole table, so colours stay the same on every panel."""
    whole = ctx.store.get("whole_table")
    whole = whole if whole is not None and group in whole.columns else table
    asked = (ctx.settings.get("order") or {}).get("colour")
    ordered = _apply_order(ctx, whole[[group]].dropna(), {"colour": group})
    if asked or isinstance(whole[group].dtype, pd.CategoricalDtype):
        return list(pd.unique(ordered[group]))
    return group_order(whole[group].dropna().tolist())


def _parts(ctx, table, group, fixed, n):
    if group:
        names = _group_names(ctx, table, group)
        colours = palette_for(pd.DataFrame({group: names}), group, ctx.settings)
        keys = np.asarray(table[group].tolist(), dtype=object)
        return [(nm, c, keys == nm) for nm, c in zip(names, colours)]
    return [(None, default_colour(ctx.settings, fixed), np.ones(n, dtype=bool))]


def _finish_axes(ctx, x, group, risk, label, kind, table):
    ax = ctx.ax
    ax.set_ylim(0, 1.03)
    ax.set_xlim(left=0)
    if ax.get_xlabel() == "":
        ax.set_xlabel(x)
    if ax.get_ylabel() == "":
        ax.set_ylabel(label)
    if group and risk:
        ax.legend(title=group)
    _remember(ctx, kind, table, {"x": x, "y": None, "colour": group})


def _draw_survival(ctx, x, y, colour, confidence_band, censor_marks, transparency=None, thickness=None, value=None,
                   followed_from=None, allowing=()):
    ax = ctx.ax
    group, fixed = colour_role(ctx.data, colour)
    table = _rows_used(ctx.data, x, y, group, [followed_from, *allowing])
    times = check_time(table[x].tolist(), x) if len(table) else np.array([])
    events = read_event(table[y].tolist(), y, value, x)[0] if len(table) else np.array([], dtype=bool)
    entries = (check_entry(table[followed_from].tolist(), times, followed_from, x, list(range(len(times))))
               if followed_from and len(table) else None)
    parts = _parts(ctx, table, group, fixed, len(times))
    adjusted = None
    if allowing and len(table):
        from ..table.survival_r import adjusted_curves

        names = [p[0] for p in parts]
        keys = np.asarray(table[group].tolist(), dtype=object)
        columns = {c: (table[c].tolist(), not all(_is_number(v) for v in table[c].tolist())) for c in allowing}
        adjusted = adjusted_curves(times, events.astype(float), [str(k) for k in keys], [str(nm) for nm in names],
                                   columns)
    risk = []
    for name, c, rows in parts:
        if not rows.any():
            continue
        if adjusted is not None:
            mine = np.array([g == str(name) for g in adjusted["group"]], dtype=bool)
            xs, ys = adjusted["time"][mine], adjusted["survival"][mine]
            low, high = adjusted["low"][mine], adjusted["high"][mine]
            ax.step(xs, ys, where="post", color=c, label=None if name is None else str(name),
                    alpha=opacity(transparency), linewidth=thickness)
            if confidence_band:
                ax.fill_between(xs, low, high, step="post", color=c, alpha=BAND_SHADE, linewidth=0)
            continue
        km = kaplan_meier(times[rows], events[rows], None if entries is None else entries[rows])
        end = km["end"]
        xs = np.concatenate([[0.0], km["time"], [end]])
        ys = np.concatenate([[1.0], km["survival"], [km["survival"][-1] if len(km["survival"]) else 1.0]])
        ax.step(xs, ys, where="post", color=c, label=None if name is None else str(name),
                alpha=opacity(transparency), linewidth=thickness)
        if confidence_band:
            low = np.concatenate([[1.0], km["low"], [km["low"][-1] if len(km["low"]) else 1.0]])
            high = np.concatenate([[1.0], km["high"], [km["high"][-1] if len(km["high"]) else 1.0]])
            ax.fill_between(xs, low, high, step="post", color=c, alpha=BAND_SHADE, linewidth=0)
        if censor_marks and len(km["censor_time"]):
            ax.plot(km["censor_time"], km["censor_survival"], linestyle="none", marker="|", markersize=8,
                    markeredgewidth=1.2, color=c, alpha=opacity(transparency))
        risk.append((name, c, times[rows], None if entries is None else entries[rows]))
    if adjusted is not None:
        risk = [(p[0], p[1], None, None) for p in parts]
    _finish_axes(ctx, x, group, risk, Y_LABEL, "survival_curves", table)
    if adjusted is None:
        ctx.store.setdefault("at_risk", {})[id(ax)] = risk


def _draw_risk(ctx, x, y, colour, value, competing_with, confidence_band, transparency=None, thickness=None):
    """The chance of having had the event by each time, rising from 0: R survfit's Aalen-Johansen estimate with
    competing_with=, else 1 minus the Kaplan-Meier estimate (the numbers of table.find_risk_over_time)."""
    from ..table.survival_more import one_minus

    ax = ctx.ax
    group, fixed = colour_role(ctx.data, colour)
    table = _rows_used(ctx.data, x, y, group)
    times = check_time(table[x].tolist(), x) if len(table) else np.array([])
    parts = _parts(ctx, table, group, fixed, len(times))
    found = None
    if competing_with is not None and len(table):
        from ..table.survival_r import risk_curves

        states, kinds, _ = read_states(table[y].tolist(), y, value, competing_with, x, "draw_risk_curves")
        names = [str(p[0]) for p in parts] if group else None
        found = risk_curves(times, states, [k.strip('"') for k in kinds],
                            [str(k) for k in table[group].tolist()] if group else None, names)
        events = states == 1
    else:
        events = read_event(table[y].tolist(), y, value, x)[0] if len(table) else np.array([], dtype=bool)
    drawn = []
    for name, c, rows in parts:
        if not rows.any():
            continue
        end = float(times[rows].max())
        if found is not None:
            mine = np.array([(s == str(name)) if group else True for s in
                             (found["strata"] if group else ["1"] * len(found["time"]))], dtype=bool)
            t = found["time"][mine]
            keep = t <= end
            xs = np.concatenate([[0.0], t[keep], [end]])
            r, low, high = found["risk"][mine, 0][keep], found["low"][mine, 0][keep], found["high"][mine, 0][keep]
            ys = np.concatenate([[0.0], r, [r[-1] if len(r) else 0.0]])
            lows = np.concatenate([[0.0], low, [low[-1] if len(low) else 0.0]])
            highs = np.concatenate([[0.0], high, [high[-1] if len(high) else 0.0]])
        else:
            km = kaplan_meier(times[rows], events[rows])
            xs = np.concatenate([[0.0], km["time"], [end]])
            ys = one_minus(np.concatenate([[1.0], km["survival"], [km["survival"][-1] if len(km["survival"]) else 1.0]]))
            lows = one_minus(np.concatenate([[1.0], km["high"], [km["high"][-1] if len(km["high"]) else 1.0]]))
            highs = one_minus(np.concatenate([[1.0], km["low"], [km["low"][-1] if len(km["low"]) else 1.0]]))
        ax.step(xs, ys, where="post", color=c, label=None if name is None else str(name),
                alpha=opacity(transparency), linewidth=thickness)
        if confidence_band:
            ax.fill_between(xs, lows, highs, step="post", color=c, alpha=BAND_SHADE, linewidth=0)
        drawn.append(name)
    label = (f"Risk: chance of having had {value}" if value is not None else "Risk: chance of having had the event")
    _finish_axes(ctx, x, group, drawn, label, "risk_curves", table)


def _draw_at_risk(ctx):
    """Numbers at risk under the x-axis ticks, one row per group (after ranges and ticks are set)."""
    ax = ctx.ax
    risk = ctx.store.get("at_risk", {}).get(id(ax))
    if not risk:
        return
    low, high = ax.get_xlim()
    ticks = [t for t in ax.get_xticks() if low - 1e-9 <= t <= high + 1e-9]
    size = ax.xaxis.get_label().get_fontsize() * 0.85
    gap = ax.xaxis.get_ticklabels()[0].get_fontsize() * 1.6 + 4 if ax.xaxis.get_ticklabels() else 16
    # the names stand left of the first column of numbers (half the widest number, plus a gap)
    digits = max(len(str(len(times))) for _, _, times, _ in risk)
    left = -(digits * size * 0.3 + 6)
    ax.annotate("Number at risk", xy=(0, 0), xycoords="axes fraction", xytext=(left, -gap), textcoords="offset points",
                ha="right", va="top", fontsize=size, fontweight="bold")
    for row, (name, c, times, entries) in enumerate(risk):
        offset = -gap - (row + 1) * RISK_LINE * size / 9
        if name is not None:
            ax.annotate(str(name), xy=(0, 0), xycoords="axes fraction", xytext=(left, offset),
                        textcoords="offset points", ha="right", va="top", fontsize=size, color=c)
        for t in ticks:
            followed = (times >= t) if entries is None else ((times >= t) & (entries < t))
            ax.annotate(str(int(followed.sum())), xy=(t, 0), xycoords=("data", "axes fraction"),
                        xytext=(0, offset), textcoords="offset points", ha="center", va="top", fontsize=size,
                        color=c)
    ax.xaxis.labelpad = (len(risk) + 1) * RISK_LINE * size / 9 + 6


def _event_kinds_check(rows, event, time, value, competing_with, word):
    """The event column read on the user's line: three kinds without competing_with= are refused (S3b-L6)."""
    if competing_with is not None:
        read_states(rows[event].tolist(), event, value, competing_with, time, word)
        return
    kinds = _kinds([_key(v) for v in rows[event].tolist()])
    if len(kinds) >= 3:
        raise kinds_error(event, kinds, time, _key(value) if value is not None else None,
                          word if word == "draw_risk_curves" else None)
    read_event(rows[event].tolist(), event, value, time)


class SurvivalChartWords:
    @friendly(renamed={"confidence_band": "with_confidence_band", "censor_marks": "with_censor_marks",
                       "at_risk_table": "with_at_risk_table"})
    def draw_survival_curves(self: _Same, time=None, event=None, colour=None, with_confidence_band=False, with_censor_marks=True,
                             with_at_risk_table=False, transparency=None, thickness=None, value=None,
                             allowing_for=None, followed_from=None) -> _Same:
        """The share still without the event over time (Kaplan-Meier curves).
        chart.draw_survival_curves(time="days", event="died", colour="treatment") (with sdata.get_example("trial"))

        time= is the time until the event or the end of follow-up; event= says whether the
        event happened (yes/no, True/False or 1/0; value="relapse" names the value that is the event).
        colour="treatment" draws one curve per group (for_each_group_in="treatment" says the same, as on the table
        words), or colour="blue" one colour. Each curve starts at 1 and
        drops at each event; censored rows (followed without the event) are small ticks (with_censor_marks=False
        hides them). with_confidence_band=True shades the 95 % confidence interval. with_at_risk_table=True
        writes the number still at risk under the x-axis. transparency= (0 to 1) makes the curves
        see-through and thickness= sets their width in points. The numbers are those of
        table.find_survival_over_time() (as R survfit()). An event column with three or more kinds is refused:
        chart.draw_risk_curves(...) draws the chance of one event when another can come first.
        More: followed_from="entry_age" gives each row the time its follow-up started (delayed entry).
        allowing_for=["age", "sex"] (with colour= a column) draws curves adjusted for those columns by direct
        adjustment (each row's curve predicted in each group and averaged; R adjustedCurves); adjusted curves
        have no censored rows and no number at risk, so with_at_risk_table= is refused with them.
        """
        example = 'chart.draw_survival_curves(time="days", event="died", colour="treatment")'
        for option, given in (("time", time), ("event", event)):
            if not isinstance(given, str):
                raise SimplydataError(f".draw_survival_curves() needs {option}= as a column name in quotes.\n"
                                      f"For example {example} (with sdata.get_example(\"trial\")).")
        if time == event:
            raise SimplydataError(f'"{time}" cannot be both time= and event=.\nFor example {example}.')
        for option, given in (("confidence_band", with_confidence_band), ("censor_marks", with_censor_marks),
                              ("at_risk_table", with_at_risk_table)):
            if not isinstance(given, bool):
                raise SimplydataError(f"{option}= in .draw_survival_curves() should be True or False, not {given!r}.")
        transparency = check_transparency("draw_survival_curves", transparency)
        thickness = check_thickness("draw_survival_curves", thickness)
        group, _ = colour_role(self._data, colour)
        if group is not None and not isinstance(group, str):
            raise SimplydataError(f'.draw_survival_curves() needs colour= as a column name or a colour.\nFor example {example}.')
        if group in (time, event):
            raise SimplydataError(f'"{group}" cannot be both colour= and time= or event=.')
        allowing = [allowing_for] if isinstance(allowing_for, str) else list(allowing_for or [])
        if allowing_for is not None and (not allowing or not all(isinstance(c, str) for c in allowing)):
            raise SimplydataError("allowing_for= needs a column name or a list of them.")
        if allowing:
            if group is None:
                raise SimplydataError('allowing_for= needs colour= a column: the curves of its groups are adjusted for '
                                      'the other columns.\nFor example chart.draw_survival_curves(time="days", '
                                      'event="died", colour="treatment", allowing_for=["age"]).')
            if with_at_risk_table:
                raise SimplydataError("Adjusted curves have no simple number at risk (each is an average over all "
                                      "rows), so with_at_risk_table=True is not drawn with allowing_for=.")
            if followed_from is not None:
                raise SimplydataError("allowing_for= (adjusted curves) works without followed_from=.")
            for c in allowing:
                if c in (time, event, group):
                    raise SimplydataError(f'"{c}" cannot be in allowing_for= and also be time=, event= or colour=.')
        if followed_from is not None and not isinstance(followed_from, str):
            raise SimplydataError("followed_from= needs a column name in quotes.")
        check(self._data, x=time, y=event, colour=group)
        for c in allowing + ([followed_from] if followed_from else []):
            if c not in self._data.columns:
                check(self._data, x=c)
        rows = _rows_used(self._data, time, event, group, [followed_from, *allowing])
        if not len(rows):
            raise SimplydataError(f'.draw_survival_curves() found no rows with "{time}" and "{event}" filled in.')
        times = check_time(rows[time].tolist(), time)  # say what is wrong on the user's line
        _event_kinds_check(rows, event, time, value, None, "draw_survival_curves")
        if followed_from:
            check_entry(rows[followed_from].tolist(), times, followed_from, time, list(range(len(times))))
        self._need_axes("draw_survival_curves")
        # x= and y= so the chart notes count the rows left out because of empty cells
        self._add("survival_curves", "draw", _draw_survival, x=time, y=event, colour=colour,
                  confidence_band=with_confidence_band, censor_marks=with_censor_marks, transparency=transparency,
                  thickness=thickness, value=value, followed_from=followed_from, allowing=tuple(allowing))
        if with_at_risk_table:
            self._replace("survival_at_risk", "finish", _draw_at_risk)
        return self

    @friendly
    def draw_risk_curves(self: _Same, time=None, event=None, value=None, competing_with=None, colour=None,
                         with_confidence_band=False, transparency=None, thickness=None) -> _Same:
        """The chance of having had the event by each time, rising from 0 (cumulative incidence curves).
        chart.draw_risk_curves(time="time", event="event", value="first_esbl", competing_with="discharged", colour="ward")
        (with sdata.get_example("admissions"), after table.add_time_and_event_columns(from_date="admitted",
        event_date="first_esbl", competing_with="discharged") and chart = table.start_chart())

        The twin of draw_survival_curves: the numbers of table.find_risk_over_time(). event= says which event
        happened; value= is the event you ask about and competing_with= the event (or list) that can come first
        and stop it (the Aalen-Johansen estimate, R survfit; needs R). With a yes/no event column and no
        competing_with= the curve is 1 minus the Kaplan-Meier curve (no R). colour="treatment" draws one curve
        per group; with_confidence_band=True shades the 95 % interval; transparency= and thickness= as on the
        other line words. A column with three or more kinds is refused without competing_with=.
        """
        word = "draw_risk_curves"
        example = 'chart.draw_risk_curves(time="days", event="outcome", value="relapse", competing_with="death")'
        for option, given in (("time", time), ("event", event)):
            if not isinstance(given, str):
                raise SimplydataError(f".draw_risk_curves() needs {option}= as a column name in quotes.\n"
                                      f"For example {example}.")
        if time == event:
            raise SimplydataError(f'"{time}" cannot be both time= and event=.\nFor example {example}.')
        if not isinstance(with_confidence_band, bool):
            raise SimplydataError(f"confidence_band= in .draw_risk_curves() should be True or False, not "
                                  f"{with_confidence_band!r}.")
        transparency = check_transparency(word, transparency)
        thickness = check_thickness(word, thickness)
        group, _ = colour_role(self._data, colour)
        if group is not None and not isinstance(group, str):
            raise SimplydataError(f".draw_risk_curves() needs colour= as a column name or a colour.\nFor example {example}.")
        if group in (time, event):
            raise SimplydataError(f'"{group}" cannot be both colour= and time= or event=.')
        check(self._data, x=time, y=event, colour=group)
        rows = _rows_used(self._data, time, event, group)
        if not len(rows):
            raise SimplydataError(f'.draw_risk_curves() found no rows with "{time}" and "{event}" filled in.')
        check_time(rows[time].tolist(), time)
        _event_kinds_check(rows, event, time, value, competing_with, word)
        if competing_with is not None:
            from .._r import need_r

            need_r(("survival",), "The chance of each kind of event over time (R survival::survfit, Aalen-Johansen)")
        self._need_axes(word)
        self._add("risk_curves", "draw", _draw_risk, x=time, y=event, colour=colour, value=value,
                  competing_with=competing_with, confidence_band=with_confidence_band, transparency=transparency,
                  thickness=thickness)
        return self
