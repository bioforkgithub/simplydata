"""More survival (phase S3b-3): the chance of an event over time when another can come first, and the time and
event columns made from dates.

* find_risk_over_time: the chance of having had the event by each time (the cumulative incidence). With
  competing_with= it is the Aalen-Johansen estimate of R survival::survfit() with a factor event (needs R); with
  one kind of event it is 1 minus the Kaplan-Meier estimate (statsmodels SurvfuncRight, as
  find_survival_over_time), which is what the cumulative incidence is when nothing competes. A column with
  three or more kinds is never read without competing_with=: that is the error the word exists to prevent
  (1 - Kaplan-Meier with the competing event counted as censored is too high; Gooley et al. 1999).
* add_time_and_event_columns: the time from one date to the first of the end dates, and whether the event
  date came first. Date arithmetic (as add_column(by_subtracting=[date, date])), not a statistical method; a
  week is 7 days, a month 30.4375 days and a year 365.25 days (R Epi cal.yr(), Stata stset scale(365.25)).
"""

from __future__ import annotations

import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .stat_tests import _list_words, _num, _whole
from .survival import (_kinds, _key, _pct, _r_vector, _surv, kaplan_meier, kinds_error, others_sentence,
                       read_event, read_states, time_points)

UNITS = {"days": 1.0, "weeks": 7.0, "months": 30.4375, "years": 365.25}
UNIT_SPELLINGS = {"day": "days", "week": "weeks", "month": "months", "year": "years"}
STILL_FOLLOWED = "still followed"
RISK_EXAMPLE = 'table.find_risk_over_time(time="months", event="outcome", value="relapse", competing_with="death")'


def one_minus(values):
    """[D] The chance of having had the event when nothing competes: 1 minus the Kaplan-Meier survival (and its
    interval ends swapped), as R plot(survfit(...), fun = "event")."""
    return 1.0 - np.asarray(values, dtype=float)


class SurvivalMoreWords:
    # ------------------------------------------------------------------ find_risk_over_time
    @friendly(renamed={"for_each": "for_each_group_in"}, others={"at_times": "at_time_points"})
    def find_risk_over_time(self, time=None, event=None, value=None, competing_with=None, for_each_group_in=None,
                            at_time_points=None):
        """The chance of having had the event by each time, when another event can come first (competing risks).

        table.find_risk_over_time(time="time", event="event", value="first_esbl", competing_with="discharged", for_each_group_in="ward")
        (with sdata.get_example("admissions"), after table.add_time_and_event_columns(from_date="admitted",
        event_date="first_esbl", competing_with="discharged")). time= is the time until the first event or the end of follow-up; event= is the column that says which
        event happened; value= is the event you ask about and competing_with= the event (or a list) that can
        come first and stop it from happening. Every other value of event= counts as still followed without
        either event (censored), and the printout says how many rows each such value has. Prints, for each group
        of for_each_group_in=, the chance of having had each event by the last event time (or by each time of
        at_time_points=); gives back one row per group, kind of event and time: at risk, events, risk and its
        95 % CI (Aalen-Johansen, as R survfit(Surv(time, factor(event)) ~ group); needs R).
        This is the chance of having had relapse by a time (a risk by a time), not the risk at any moment of
        explain_survival's hazard ratios. With one kind of event (a yes/no column, or value= in a two-valued
        column) it is 1 minus the Kaplan-Meier survival and needs no R. A column with three or more kinds is
        refused without competing_with=: counting death as the end of follow-up would make the risk of relapse
        too high (the printout shows by how much). Draw it with chart.draw_risk_curves(...).
        """
        step = "find_risk_over_time"
        if for_each_group_in is not None:
            self._check_for_each(step, for_each_group_in, time, event, RISK_EXAMPLE)
        points = time_points(step, at_time_points) if at_time_points is not None else None
        extra = [for_each_group_in] if for_each_group_in else []
        times, kept, _, _ = self._survival_rows(step, time, event, extra, RISK_EXAMPLE)
        if for_each_group_in:
            names, codes = self._group_codes(kept[for_each_group_in])
        else:
            names, codes = [None], np.zeros(len(times), dtype=int)
        if competing_with is None:
            kinds = _kinds([_key(v) for v in kept[event]])
            if len(kinds) >= 3:
                raise kinds_error(event, kinds, time, _key(value) if value is not None else None, step)
            events, yes = read_event(kept[event], event, value, time)
            return self._risk_one_kind(time, event, yes, times, events, names, codes, for_each_group_in, points)
        states, kinds, others = read_states(kept[event], event, value, competing_with, time, step)
        return self._risk_competing(time, event, times, states, kinds, others, names, codes, for_each_group_in,
                                    points)

    def _risk_one_kind(self, time, event, yes, times, events, names, codes, for_each, points):
        """Nothing competes: 1 minus the Kaplan-Meier survival (statsmodels), read at each event time or at the
        times asked."""
        print(self._event_sentence(event, yes, events, time))
        print(f"The chance of having had {yes} by each time (nothing competes with it here, so this is 1 minus "
              "the Kaplan-Meier survival):")
        columns = ["event", "time", "at risk", "events" if points is None else "events by then", "risk",
                   "95 % CI low", "95 % CI high"]
        out = {c: [] for c in ([for_each] if for_each else []) + columns}
        label = yes.strip('"')
        for j, name in enumerate(names):
            rows = codes == j
            t, e = times[rows], events[rows]
            km = kaplan_meier(t, e)
            who = f"{name}, " if for_each else ""
            if points is None:
                read = [(float(x), int(n), int(d), float(s), float(lo), float(hi)) for x, n, d, s, lo, hi in
                        zip(km["time"], km["at_risk"], km["events"], km["survival"], km["low"], km["high"])]
            else:
                read = []
                for point in points:
                    place = int(np.searchsorted(km["all_time"], point, side="right")) - 1
                    n = int((t >= point).sum())
                    d = int((e & (t <= point)).sum())
                    if point > km["end"]:
                        read.append((float(point), n, d, math.nan, math.nan, math.nan))
                    elif place < 0:
                        read.append((float(point), n, d, 1.0, 1.0, 1.0))
                    else:
                        read.append((float(point), n, d, float(km["all_survival"][place]),
                                     float(km["all_low"][place]), float(km["all_high"][place])))
            for x, n, d, s, lo, hi in read:
                if for_each:
                    out[for_each].append(name)
                out["event"].append(label)
                out["time"].append(x)
                out["at risk"].append(n)
                out[columns[3]].append(d)
                risk, low, high = one_minus([s, hi, lo])
                out["risk"].append(float(risk))
                out["95 % CI low"].append(float(low))
                out["95 % CI high"].append(float(high))
            shown = read if points is not None else read[-1:]
            for x, n, d, s, lo, hi in shown:
                if math.isnan(s):
                    print(f'  {who}by "{time}" {_whole(x)}: not followed that long, so it is left empty.')
                else:
                    risk, low, high = one_minus([s, hi, lo])
                    print(f'  {who}by "{time}" {_whole(x)}: {_pct(risk)} had had {yes} (95 % CI {_pct(low)} to '
                          f"{_pct(high)}).")
            if not read:
                print(f"  {who}no events, so the chance stays 0.")
        group = for_each if for_each else "1"
        times_part = f", times = {_r_vector(points)}" if points is not None else ""
        print(f"Method: 1 minus the Kaplan-Meier estimate and its 95 % confidence interval (log scale, Greenwood), as "
              f"R summary(survfit({_surv(time, event, yes)} ~ {group}){times_part}) read as 1 - surv; with one kind "
              "of event this is the cumulative incidence.")
        return self._new_table(nw.from_dict(out, backend=self._frame.implementation))

    def _risk_competing(self, time, event, times, states, kinds, others, names, codes, for_each, points):
        """Competing events: the Aalen-Johansen estimate of R survfit with a factor event, and beside it what
        1 minus Kaplan-Meier would wrongly give."""
        from .survival_r import risk_curves

        labels = [k.strip('"') for k in kinds]
        counts = _list_words(f"{k} ({int((states == i).sum())} rows)" for i, k in enumerate(kinds, start=1))
        print(f'The events in "{event}": {counts}; {kinds[0]} is the event asked about, '
              f"{_list_words(kinds[1:])} {'competes' if len(kinds) == 2 else 'compete'} with it (can come first).")
        print(others_sentence(others, event))
        group_names = [str(n) for n in names] if for_each else None
        found = risk_curves(times, states, labels, [names[c] for c in codes] if for_each else None, group_names,
                            at=points)
        strata = found["strata"] if for_each else ["1"] * len(found["time"])
        columns = ["event", "time", "at risk", "events" if points is None else "events by then", "risk",
                   "95 % CI low", "95 % CI high"]
        out = {c: [] for c in ([for_each] if for_each else []) + columns}
        print(f"The chance of having had each event by each time (Aalen-Johansen), with its 95 % CI:")
        for j, name in enumerate(names):
            where = [i for i, s in enumerate(strata) if (s == str(name) if for_each else True)]
            rows = codes == j
            end = float(times[rows].max())
            who = f"{name}, " if for_each else ""
            for i in where:
                x = float(found["time"][i])
                gone = x > end
                for k, label in enumerate(labels):
                    if for_each:
                        out[for_each].append(name)
                    out["event"].append(label)
                    out["time"].append(x)
                    out["at risk"].append(int(found["at_risk"][i]))
                    if points is None:
                        out["events"].append(int(found["events"][i, k]))
                    else:
                        out["events by then"].append(int(((states == k + 1) & rows & (times <= x)).sum()))
                    for c, key in (("risk", "risk"), ("95 % CI low", "low"), ("95 % CI high", "high")):
                        out[c].append(math.nan if gone else float(found[key][i, k]))
            shown = where if points is not None else where[-1:]
            for i in shown:
                x = float(found["time"][i])
                if x > end:
                    print(f'  {who}by "{time}" {_whole(x)}: not followed that long, so it is left empty.')
                    continue
                rest = _list_words(f"{_pct(found['risk'][i, k])} had had {kinds[k]} first"
                                   for k in range(1, len(kinds)))
                print(f'  {who}by "{time}" {_whole(x)}: {_pct(found["risk"][i, 0])} had had {kinds[0]} (95 % CI '
                      f"{_pct(found['low'][i, 0])} to {_pct(found['high'][i, 0])}), and {rest}.")
            # the error this word prevents, shown rather than told (Gooley et al. 1999)
            km = kaplan_meier(times[rows], states[rows] == 1)
            last = shown[-1] if shown else None
            if last is not None and float(found["time"][last]) <= end:
                x = float(found["time"][last])
                place = int(np.searchsorted(km["all_time"], x, side="right")) - 1
                wrong = one_minus([km["all_survival"][place] if place >= 0 else 1.0])[0]
                print(f'  {who}if {_list_words(kinds[1:])} were wrongly counted as the end of follow-up (1 minus '
                      f'Kaplan-Meier), the chance of {kinds[0]} by "{time}" {_whole(x)} would come out as '
                      f"{_pct(wrong)}: too high, because rows that had {_list_words(kinds[1:])} first are treated as "
                      f"if they could still have {kinds[0]}.")
        group = for_each if for_each else "1"
        times_part = f", times = {_r_vector(points)}, extend = TRUE" if points is not None else ""
        print(f'Method: Aalen-Johansen estimate with 95 % confidence intervals (log scale), as R summary(survfit('
              f'Surv({time}, factor({event})) ~ {group}){times_part}); the risk is the column "pstate" of each event.')
        return self._new_table(nw.from_dict(out, backend=self._frame.implementation))

    # ------------------------------------------------------------------ add_time_and_event_columns
    @friendly
    def add_time_and_event_columns(self, from_date=None, to_date=None, event_date=None, until=None, unit="days",
                                   time="time", event="event", competing_with=None):
        """Add the time followed and whether the event happened, from date columns (person-time).

        table.add_time_and_event_columns(from_date="admitted", to_date="discharged", event_date="first_esbl")   (with sdata.get_example("admissions"))
        Follow-up runs from from_date= to the first of event_date=, to_date= and until= (a date for all rows,
        such as the end of the study). Adds two columns: "time" (from from_date= to that first date, in unit=
        "days", "weeks", "months" or "years") and "event": 1 when event_date= came first (on or before the
        others), else 0. An empty to_date= or event_date= means the row was still followed, up to until=.
        time= and event= name the new columns (here they name columns to be made, not columns that are there);
        give the same names to rate_of, find_survival_over_time and explain_survival next.
        A week is 7 days, a month 30.4375 days and a year 365.25 days (as R Epi cal.yr() and Stata
        stset scale(365.25)). Rows whose event_date= is before from_date= had the event already (prevalent
        cases): their new cells stay empty, and the note names them.
        More: competing_with=["discharged", "died"] takes date columns of events that can come first and stop
        the event from happening (in hospital, discharge before an infection; Wolkewitz et al. 2014). The event
        column then holds the name of the column that came first, or "still followed", ready for
        table.find_risk_over_time(time="time", event="event", value="first_esbl",
        competing_with=["discharged", "died"]).
        """
        step = "add_time_and_event_columns"
        example = ('table.add_time_and_event_columns(from_date="admitted", to_date="discharged", '
                   'event_date="first_esbl", until="2024-12-31")')
        unit = UNIT_SPELLINGS.get(unit.strip().lower(), unit.strip().lower()) if isinstance(unit, str) else unit
        if unit not in UNITS:
            raise choice_error(step, "unit", unit, list(UNITS))
        if not isinstance(from_date, str):
            raise SimplydataError(f"{step}() needs from_date= as a column of dates in quotes.\nFor example, {example}")
        competing = [] if competing_with is None else (
            [competing_with] if isinstance(competing_with, str) else list(competing_with))
        named = {"from_date": from_date, "to_date": to_date, "event_date": event_date}
        for option, column in list(named.items()) + [("competing_with", c) for c in competing]:
            if column is not None and not isinstance(column, str):
                raise SimplydataError(f"{option}= needs a column name in quotes.\nFor example, {example}")
        dates = [c for c in [from_date, to_date, event_date] + competing if c is not None]
        if len(set(dates)) < len(dates):
            raise SimplydataError("Each date column can have one job: from_date=, to_date=, event_date= and "
                                  "competing_with= need different columns.")
        self._need_columns(*dates)
        for c in dates:
            if self._kind(c) != "date":
                raise SimplydataError(f'"{c}" holds {self._kind(c)} values, not dates. Make it dates first: '
                                      f'table.turn_into_dates("{c}").')
        for option, name in (("time", time), ("event", event)):
            if not isinstance(name, str) or not name.strip():
                raise SimplydataError(f"{option}= is the name of the new column, in quotes, such as {option}=\"{option}\".")
        if time == event:
            raise SimplydataError("time= and event= name two new columns, so they need different names.")
        for name in (time, event):
            if name in self._frame.columns:
                raise SimplydataError(f'The table already has a column "{name}". Name the new one otherwise, for '
                                      f'example {"time" if name == time else "event"}="{name}_2", or remove the old one '
                                      f'first with table.remove_columns("{name}").')
        end_day = self._until_day(step, until)
        if to_date is None and event_date is None and end_day is None and not competing:
            raise SimplydataError(f"{step}() needs an end of follow-up: to_date=, event_date= or until= (or "
                                  f"competing_with=).\nFor example, {example}")
        from .between import _days

        try:
            day = {c: _days(self._frame[c].to_numpy()) for c in dates}
        except (TypeError, ValueError):
            raise SimplydataError("These dates could not be read as days (a time zone on one column and not on "
                                  "another?). Make them plain dates first with table.turn_into_dates(...).") from None
        start = day[from_date]
        n = len(start)
        # the ends, in the order that settles a tie: the event first ("on or before" counts as the event), then
        # the competing events in the order given, then the end of follow-up
        ends = []
        if event_date is not None:
            ends.append((event_date, day[event_date]))
        ends += [(c, day[c]) for c in competing]
        if to_date is not None:
            ends.append((to_date, day[to_date]))
        if end_day is not None:
            ends.append((str(until), np.full(n, end_day)))
        self._check_follow_up_dates(start, to_date, day, end_day, until, from_date)
        prevalent = np.zeros(n, dtype=bool) if event_date is None else (day[event_date] < start)
        stacked = np.vstack([e for _, e in ends])
        filled = ~np.isnan(stacked)
        no_end = ~filled.any(axis=0) & ~np.isnan(start)
        if no_end.any():
            rows = np.flatnonzero(no_end)
            shown = ", ".join(str(i + 1) for i in rows[:8]) + (" ..." if len(rows) > 8 else "")
            raise SimplydataError(f"{len(rows)} {'row has' if len(rows) == 1 else 'rows have'} no end of follow-up "
                                  f"(row {shown}, counting from 1): every end date is empty. Give until= (the end of "
                                  "the study, for example until=\"2024-12-31\").")
        first = np.where(filled, stacked, np.inf).argmin(axis=0)  # the end that came first (ties: the first listed)
        end = np.where(filled, stacked, np.inf).min(axis=0)
        usable = ~np.isnan(start) & ~prevalent
        days = np.where(usable, end - start, np.nan)
        span = np.where(usable, days / UNITS[unit], np.nan)
        kinds = [name for name, _ in ends]
        if competing:
            labels = np.array([kinds[f] if kinds[f] in [event_date] + competing else STILL_FOLLOWED for f in first],
                              dtype=object)
            labels[~usable] = None
            event_values = list(labels)
        else:
            had = (first == 0) if event_date is not None else np.zeros(n, dtype=bool)
            event_values = [int(h) if u else None for h, u in zip(had, usable)]
        whole = bool(np.all(np.isnan(span) | (span == np.round(span)))) and unit == "days"
        empty = bool(np.isnan(span).any())  # an empty cell: a column of floats (pandas has no empty whole number)
        if whole and not empty:
            time_series_values, time_type = span.astype("int64"), nw.Int64
        else:
            time_series_values, time_type = span, nw.Float64
        backend = self._frame.implementation
        if competing:
            event_series = nw.new_series(event, event_values, nw.String, backend=backend)
        elif empty:
            event_series = nw.new_series(event, np.array([np.nan if v is None else float(v) for v in event_values]),
                                         nw.Float64, backend=backend)
        else:
            event_series = nw.new_series(event, np.array(event_values, dtype="int64"), nw.Int64, backend=backend)
        frame = self._frame.with_columns(nw.new_series(time, time_series_values, time_type, backend=backend),
                                         event_series)
        self._time_event_sentences(step, time, event, unit, from_date, kinds, event_date, competing, until,
                                   event_values, span, usable, prevalent, start, days)
        what = f"add {time} and {event} from {from_date} to the first of {', '.join(kinds)} ({unit})"
        return self._change(what, frame)

    @staticmethod
    def _until_day(step, until):
        """until=: one date for every row (text such as "2024-12-31", a date or a datetime), as days since 1970."""
        if until is None:
            return None
        import pandas as pd

        from .between import _days

        try:
            stamp = pd.Timestamp(until)
        except (TypeError, ValueError):
            stamp = None
        if stamp is None or stamp is pd.NaT:
            raise SimplydataError(f'until= should be a date, such as until="2024-12-31", not {until!r}.')
        if stamp.tzinfo is not None:
            stamp = stamp.tz_localize(None)
        return float(_days(np.array([stamp.to_datetime64()]))[0])

    @staticmethod
    def _check_follow_up_dates(start, to_date, day, end_day, until, from_date):
        if to_date is not None:
            bad = np.flatnonzero(day[to_date] < start)
            if len(bad):
                shown = ", ".join(str(i + 1) for i in bad[:8]) + (" ..." if len(bad) > 8 else "")
                raise SimplydataError(f'"{to_date}" is before "{from_date}" in {len(bad)} '
                                      f"{'row' if len(bad) == 1 else 'rows'} (row {shown}, counting from 1). Check "
                                      "those dates: follow-up cannot end before it starts.")
        if end_day is not None and np.all(np.isnan(start) | (end_day < start)):
            raise SimplydataError(f'until="{until}" is before every "{from_date}", so no row was followed.')

    @staticmethod
    def _time_event_sentences(step, time, event, unit, from_date, kinds, event_date, competing, until, event_values,
                              span, usable, prevalent, start, days):
        firsts = _list_words(f'"{k}"' if k != str(until) else str(until) for k in kinds)
        print(f'Added "{time}": the {unit} from "{from_date}" to the first of {firsts}.')
        used = int(usable.sum())
        if competing:
            counts = _list_words(f'"{k}" {sum(1 for v in event_values if v == k)}'
                                 for k in [event_date] + competing if k is not None)
            still = sum(1 for v in event_values if v == STILL_FOLLOWED)
            print(f'Added "{event}": the name of the event that came first ({counts} of {used} rows), or '
                  f'"{STILL_FOLLOWED}" ({still} rows). Next: table.find_risk_over_time(time="{time}", event="{event}", '
                  f'value="{event_date}", competing_with=[{", ".join(chr(34) + c + chr(34) for c in competing)}]).')
        elif event_date is not None:
            had = sum(1 for v in event_values if v == 1)
            print(f'Added "{event}": 1 when "{event_date}" came first (on or before the other dates), else 0 '
                  f"({had} of {used} rows).")
        else:
            print(f'Added "{event}": 0 in every row (no event_date= was given), so every row counts as followed '
                  "without the event.")
        total = float(np.nansum(span))
        print(f"Person-time in all: {total:,.6g} {unit} over {used} rows.")
        if unit != "days":
            print(f"Note: one {unit[:-1]} is {_whole(UNITS[unit])} days here (as R Epi cal.yr() and Stata stset "
                  "scale(365.25)); other tools may count calendar months or years.")
        if prevalent.any():
            rows = np.flatnonzero(prevalent)
            shown = ", ".join(str(i + 1) for i in rows[:8]) + (" ..." if len(rows) > 8 else "")
            print(f'Note: {len(rows)} {"row" if len(rows) == 1 else "rows"} had "{event_date}" before "{from_date}" '
                  f"(row {shown}, counting from 1): they had the event already when follow-up began (prevalent "
                  "cases), so their new cells are left empty.")
        missing = int((np.isnan(start)).sum())
        if missing:
            print(f'Note: {missing} {"row has" if missing == 1 else "rows have"} an empty "{from_date}", so '
                  f"{'its' if missing == 1 else 'their'} new cells are left empty.")
        zero = int(np.sum(usable & (days == 0)))
        if zero:
            print(f"Note: {zero} {'row starts and ends' if zero == 1 else 'rows start and end'} on the same day: "
                  f"counted as 0, so {'it adds' if zero == 1 else 'they add'} no person-time (add 1 day if your days "
                  "count both ends).")
