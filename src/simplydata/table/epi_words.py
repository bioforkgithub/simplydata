"""Epidemiology in plain words (phase S3d-2): attributable fractions on compare_risks, and standardised rates on
rate_of (direct: standard_population=) and compare_rates (indirect, observed / expected: standard_rates=).

simplydata counts the rows in each group and band, checks them, and words the answer; every number comes from R
epiR (table/epi_r.py has the calls).
"""

from __future__ import annotations

import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError
from .stat_tests import _label, _list_words
from .summaries import _p_sentence

AF_SHOW = "attributable fractions"
CRUDE = "Crude: not adjusted for other columns (a confounder can make it too big or too small)."


def _num(x) -> str:
    from .risk_words import _num as num

    return num(x)


def _pct(share) -> str:
    """A share from epiR as a percent, for the sentence: [D] times 100 (display)."""
    return "cannot be worked out" if math.isnan(share) else f"{_num(round(share * 100, 1))} %"


def _pct_range(low, high) -> str:
    if math.isnan(low) or math.isnan(high):
        return "its interval cannot be worked out"
    return f"{_pct(low)} to {_pct(high)}"


def read_show(step, show, example):
    """None or "attributable fractions" (spellings with "attributable fraction", "af", "paf")."""
    if show is None:
        return None
    if isinstance(show, str) and show.strip().lower() in ("attributable fractions", "attributable fraction",
                                                           "attributable", "af", "paf"):
        return AF_SHOW
    raise SimplydataError(f'{step}() takes show="attributable fractions" (the share of the events that goes with the '
                          f"exposure), or no show=.\nFor example, {example.rstrip(')')}, "
                          'show="attributable fractions")')


def attributable_rows(counts, ref, level, what, group_column):
    """compare_risks(show="attributable fractions"): counts = {group: (events, total)} with two groups, ref = the
    unexposed group (against=). Prints the sentences and gives back the result rows."""
    from .epi_r import attributable

    exposed = next(g for g in counts if g != ref)
    ci = f"{level:g} % CI"
    empty = [g for g, (e, _) in counts.items() if e == 0]
    if empty:
        raise SimplydataError(f"There are no events in {_list_words(empty)}, so the risk ratio, and with it the "
                              "attributable fraction, cannot be worked out. The risk difference needs no ratio: "
                              f'table.compare_risks(..., against="{ref}") without show=.')
    listed = _list_words(f"{e} of {t} in {g}" for g, (e, t) in counts.items())
    print(f"{what}: {listed}. Exposed: {exposed}; not exposed: {ref} (against=).")
    found = attributable(counts[exposed], counts[ref], level)
    af, paf, rr = found["af"], found["paf"], found["rr"]
    method = ('R epiR::epi.2by2(method = "cohort.count"); intervals as epiR gives them for one table: among the '
              'exposed from the score interval of the risk ratio, in the population from the exact intervals of the '
              'two risks')
    rows = []
    if not math.isnan(rr[0]) and rr[0] < 1:
        # fewer events among the exposed: the preventable fraction, epiR's attributable fraction with the roles swapped
        swapped = attributable(counts[ref], counts[exposed], level)["af"]
        print(f"The risk is lower in {exposed} (risk ratio {_num(rr[0])}), so the exposure goes with fewer events. "
              f"Among those in {exposed}, {_pct(swapped[0])} of the events that would have happened without it did "
              f"not happen ({ci} {_pct_range(swapped[1], swapped[2])}): the preventable fraction, 1 minus the risk "
              "ratio.")
        print(f"The attributable fractions are negative here (among the exposed {_pct(af[0])}, in the whole "
              f"population {_pct(paf[0])}); they are given in the table. epiR gives no preventable fraction for the "
              "whole population.")
        rows.append({"measure": "preventable fraction among the exposed", "group": _label(exposed),
                     "against": _label(ref), "estimate": swapped[0], f"estimate {ci} low": swapped[1],
                     f"estimate {ci} high": swapped[2],
                     "method": method + " with the two groups' roles swapped (= 1 - risk ratio)"})
    else:
        print(f"Among those in {exposed}, {_pct(af[0])} of the events go with the exposure ({ci} "
              f"{_pct_range(af[1], af[2])}): the attributable fraction among the exposed, (risk ratio - 1) / risk "
              f"ratio, with risk ratio {_num(rr[0])}.")
        print(f"In the whole population of these rows, {_pct(paf[0])} of the events go with the exposure ({ci} "
              f"{_pct_range(paf[1], paf[2])}): the population attributable fraction, which also depends on how many "
              f"are exposed (here {counts[exposed][1]} of {sum(t for _, t in counts.values())}).")
    rows.insert(0, {"measure": "attributable fraction among the exposed", "group": _label(exposed),
                    "against": _label(ref), "estimate": af[0], f"estimate {ci} low": af[1],
                    f"estimate {ci} high": af[2], "method": method})
    rows.insert(1, {"measure": "attributable fraction in the population", "group": _label(exposed),
                    "against": _label(ref), "estimate": paf[0], f"estimate {ci} low": paf[1],
                    f"estimate {ci} high": paf[2], "method": method})
    print(CRUDE)
    print(f"These fractions are about events that would not have happened without the exposure only if "
          f'"{group_column}" causes them; a link alone does not show that.')
    print(f"Method: {method} (Rothman, Greenland & Lash 2008). The risks must come from a cohort or a cross-sectional "
          "study: in a case-control study the risks cannot be estimated from the rows.")
    return rows


# ---------------------------------------------------------------- standardisation
def _standard_values(step, given, band_column, option, what, example):
    """{band label: number} from a dict or a table (sdata table, pandas or Polars) with the band column and one
    column of numbers."""
    if isinstance(given, dict):
        values = {_label(k): v for k, v in given.items()}
    else:
        native = given.as_pandas() if hasattr(given, "as_pandas") else given
        try:
            frame = nw.from_native(native, eager_only=True)
        except TypeError:
            raise SimplydataError(f"{option}= needs a table (or a dict) with one row per {band_column}: {what}.\n"
                                  f"For example, {example}") from None
        if band_column not in frame.columns:
            raise SimplydataError(f'{option}= needs a column "{band_column}" (the column of allowing_for=); it has '
                                  f"{_list_words(chr(34) + c + chr(34) for c in frame.columns)}.\nFor example, {example}")
        numbers = [c for c in frame.columns if c != band_column and frame.schema[c].is_numeric()]
        if len(numbers) != 1:
            raise SimplydataError(f'{option}= needs "{band_column}" and one column of numbers ({what}); it has '
                                  f"{len(numbers)} number columns{': ' + _list_words(numbers) if numbers else ''}. "
                                  "Keep only the one you mean.")
        bands = frame[band_column].to_list()
        values = {_label(b): v for b, v in zip(bands, frame[numbers[0]].to_list())}
        if len(values) != len(bands):
            raise SimplydataError(f'{option}= has a {band_column} more than once; give one row per {band_column}.')
    bad = [b for b, v in values.items() if isinstance(v, bool) or not isinstance(v, (int, float, np.integer,
                                                                                       np.floating))
           or math.isnan(float(v)) or float(v) < 0]
    if bad:
        raise SimplydataError(f"{option}= needs a number of 0 or more for each {band_column} ({what}); "
                              f"{_list_words(bad[:5])} {'has' if len(bad) == 1 else 'have'} none.")
    return {b: float(v) for b, v in values.items()}


def _cells(table, step, events, time, for_each, band_column, example):
    """(groups, bands, events array groups x bands, times array) from the table; rows with an empty cell skipped."""
    names = [events, time, band_column] + ([for_each] if for_each is not None else [])
    roles = ["the events column", "time=", "allowing_for="] + (["for_each_group_in="] if for_each is not None else [])
    for role, name in zip(roles, names):
        table._need_name(step, role, name, example)
    if len(set(names)) != len(names):
        raise SimplydataError(f"{step}() needs different columns for the events, time=, allowing_for= and "
                              f"for_each_group_in=.\nFor example, {example}")
    table._need_columns(*names)
    for c in (events, time):
        if not table._frame.schema[c].is_numeric():
            raise SimplydataError(f'{step}() needs numbers in "{c}".\nFor example, {example}')
    kept = table._two_columns_frame(step, names, example)
    ev = kept[events].to_numpy().astype(float)
    tm = kept[time].to_numpy().astype(float)
    if (ev < 0).any() or (ev != np.round(ev)).any():
        raise SimplydataError(f'"{events}" should hold counts of events: whole numbers of 0 or more.')
    if (tm < 0).any():
        raise SimplydataError(f'"{time}" should hold times of 0 or more (such as person-years).')
    band_of = np.array([_label(b) for b in kept[band_column].to_list()], dtype=object)
    group_of = (np.array([_label(g) for g in kept[for_each].to_list()], dtype=object) if for_each is not None
                else np.array(["all rows"] * len(ev), dtype=object))
    order = sorted(set(kept[band_column].to_list()), key=lambda k: (str(type(k)), k))
    bands = [_label(b) for b in order]
    group_order = (sorted(set(kept[for_each].to_list()), key=lambda k: (str(type(k)), k)) if for_each is not None
                   else ["all rows"])
    groups = [_label(g) for g in group_order]
    e = np.array([[ev[(group_of == g) & (band_of == b)].sum() for b in bands] for g in groups])
    t = np.array([[tm[(group_of == g) & (band_of == b)].sum() for b in bands] for g in groups])
    return groups, bands, e, t


def _match_bands(bands, standard, band_column, option):
    missing = [b for b in bands if b not in standard]
    extra = [b for b in standard if b not in bands]
    if missing:
        raise SimplydataError(f'{option}= has no value for {_list_words(chr(34) + b + chr(34) for b in missing)} '
                              f'(in "{band_column}" of the table). Give one for every {band_column}.')
    if extra:
        raise SimplydataError(f"{option}= has {_list_words(chr(34) + b + chr(34) for b in extra)}, which the table "
                              f'does not have in "{band_column}". Give the same {band_column}s in both.')


def standardised_rates(table, events, time, for_each, band_column, standard_population, per, level):
    """rate_of(allowing_for=, standard_population=): directly standardised rates, epiR::epi.directadj."""
    from .epi_r import direct

    step = "rate_of"
    example = (f'table.rate_of("{events}", time="{time}", for_each_group_in="{for_each or "county"}", '
               f'allowing_for="{band_column}", standard_population="whole table")')
    groups, bands, e, t = _cells(table, step, events, time, for_each, band_column, example)
    if isinstance(standard_population, str):
        if standard_population.strip().lower() not in ("whole table", "the whole table", "pooled"):
            raise SimplydataError('standard_population= takes "whole table" (the person-time of all rows in each '
                                  f"{band_column}), or a table with \"{band_column}\" and one column of population "
                                  f"sizes.\nFor example, {example}")
        standard = dict(zip(bands, t.sum(axis=0)))  # the pooled person-time in each band (counting, not a method)
        said = f"the whole table's \"{time}\" in each {band_column}"
    else:
        standard = _standard_values(step, standard_population, band_column, "standard_population",
                                    "the size of the standard population", example)
        _match_bands(bands, standard, band_column, "standard_population")
        said = "the standard population you gave"
    empty = [(g, b) for i, g in enumerate(groups) for j, b in enumerate(bands) if t[i, j] == 0 and standard[b] > 0]
    if empty:
        listed = _list_words(f"{b} in {g}" for g, b in empty[:5])
        raise SimplydataError(f"Direct standardisation needs a rate in every {band_column} of every group, and "
                              f'there is no "{time}" for {listed}. Merge those bands with their neighbours, or use '
                              f"compare_rates(..., standard_rates=) (indirect standardisation), which needs no rate "
                              f"in each band of each group.")
    found = direct(groups, bands, e, t, [standard[b] for b in bands], per, level)
    ci = f"{level:g} % CI"
    rows = []
    for i, g in enumerate(groups):
        rows.append({"group": g, "events": float(e[i].sum()), "time": float(t[i].sum()),
                     "crude rate": found["crude"][i], f"crude rate {ci} low": found["crude_low"][i],
                     f"crude rate {ci} high": found["crude_high"][i], "adjusted rate": found["adj"][i],
                     f"adjusted rate {ci} low": found["adj_low"][i], f"adjusted rate {ci} high": found["adj_high"][i],
                     "per": f"{per:g} {time}"})
    print(f'"{events}" per {per:g} "{time}", standardised for "{band_column}" ({len(bands)} bands) to {said}:')
    for r in rows:
        print(f"  {r['group']}: adjusted {_num(r['adjusted rate'])} ({ci} {_num(r[f'adjusted rate {ci} low'])} to "
              f"{_num(r[f'adjusted rate {ci} high'])}); crude {_num(r['crude rate'])}.")
    print(f"The adjusted rate is the rate each group would have with the make-up of the standard population in "
          f'"{band_column}", so groups with different make-ups can be compared. Its size depends on the standard '
          "chosen: compare adjusted rates only with others made with the same standard.")
    print("Method: direct standardisation, R epiR::epi.directadj() (the same numbers as R "
          "epitools::ageadjust.direct()): the adjusted rate with Fay & Feuer's (1997) gamma interval; the crude rate "
          "with its exact Poisson interval.")
    return rows


def standardised_ratios(table, events, time, for_each, band_column, standard_rates, per, level):
    """compare_rates(allowing_for=, standard_rates=): observed / expected (SMR), epiR::epi.indirectadj."""
    from .epi_r import indirect

    step = "compare_rates"
    example = (f'table.compare_rates("{events}", time="{time}", allowing_for="{band_column}", '
               f"standard_rates=national_rates)   (national_rates: a table with \"{band_column}\" and \"rate\", per "
               f"{per:g} \"{time}\")")
    groups, bands, e, t = _cells(table, step, events, time, for_each, band_column, example)
    rates = _standard_values(step, standard_rates, band_column, "standard_rates",
                             f"the standard rate per {per:g} units of time (per=)", example)
    missing = [b for b in bands if b not in rates]
    if missing:
        raise SimplydataError(f'standard_rates= has no rate for {_list_words(chr(34) + b + chr(34) for b in missing)} '
                              f'(in "{band_column}" of the table). Give a rate for every {band_column}.')
    if (t.sum(axis=1) == 0).any():
        zero = [g for g, row in zip(groups, t) if row.sum() == 0]
        raise SimplydataError(f'{_list_words(zero)} {"has" if len(zero) == 1 else "have"} no "{time}" (0), so no '
                              "events can be expected there. Leave those rows out first.")
    found = indirect(groups, bands, e.sum(axis=1), t, [rates[b] for b in bands], per, level)
    ci = f"{level:g} % CI"
    rows = []
    for i, g in enumerate(groups):
        rows.append({"group": g, "observed": found["obs"][i], "expected": found["exp"][i],
                     "observed / expected": found["smr"][i], f"observed / expected {ci} low": found["low"][i],
                     f"observed / expected {ci} high": found["high"][i], "p-value": found["p"][i],
                     "method": "R epiR::epi.indirectadj(), exact Poisson interval; p from R poisson.test()"})
    print(f'"{events}" against the standard rates (per {per:g} "{time}", one per "{band_column}"):')
    for r in rows:
        times = r["observed / expected"]
        print(f"  {r['group']}: {_num(r['observed'])} observed, {_num(r['expected'])} expected from the standard "
              f"rates: {_num(times)} times as many ({ci} {_num(r[f'observed / expected {ci} low'])} to "
              f"{_num(r[f'observed / expected {ci} high'])}).")
        print("  " + _p_sentence(r["p-value"], if_none="the standard rates truly held here",
                                 this="a ratio this far from 1", not_shown="that the rates are the standard ones"))
    print("Observed / expected is the standardised ratio (SMR, standardised mortality or incidence ratio): 1 means as "
          f'many events as the standard rates give for the same "{time}" in each {band_column}. Ratios of two groups '
          "are each against the standard, not against each other.")
    print("Method: indirect standardisation, R epiR::epi.indirectadj(): the expected events from the standard rates, "
          "observed / expected with its exact Poisson interval; the p-value from R poisson.test(observed, expected).")
    return rows
