"""A note when rows repeat: the same person (sample, animal ...) in several rows of a test that takes them as
independent (2026-11-23, new-user study: lesson 14 compared the classes on 54 rows that were 18 children).

Bookkeeping only (PLAN.md section 7): the check counts distinct values in the other columns of the table. It
computes no statistic, never changes the method and never refuses; it prints one plain note after the word.

The rule. A column is taken as an ID when it is not used by the call (not the outcome, the groups, a formula term,
matched_by= or grouped_by=), holds text or whole numbers, and either
  * has an ID name: an ID word alone (name, id, subject, patient, participant, animal, sample, person, child,
    pupil, student, individual, respondent, donor, mouse, case), "id" in the name ("patient_id", "Sample ID"), or
    an ID word followed by name/code/number ("animal number"); not "patient_days" or "person_years". It needs at
    least 4 different values and fewer different values than rows; or
  * holds codes (text values with a letter and a digit, such as "P01" or "S12"; at least 4 in 5 values) with at
    least 10 different values, every value in 2 or more rows and none in more than 10.
The names are singular: "cases", "pupils" or "patients" are usually counts. Without an ID name, plain words such as
"month", "site" or "age_band" are grouping columns crossed with others, which look like an ID by counts alone, so
only codes count.
Among several such columns the note names the one with the most different values. No note when the word is given
matched_by= or grouped_by= (the repeats are then part of the method).
"""

from __future__ import annotations

import re

import narwhals as nw

# words whose rows are taken as independent observations (tests, intervals, models)
WORDS = frozenset({
    "compare_average_to", "compare_averages_of", "compare_spreads_of", "compare_counts_of", "compare_counts_to",
    "compare_percent_to", "compare_each_pair_of", "compare_shape_to", "compare_shapes_of", "compare_distributions_for",
    "compare_profiles_of", "compare_correlations", "compare_rates", "compare_risks", "compare_survival",
    "compare_balanced_groups_of", "compare_models", "find_correlation_between", "find_interval_of", "explain",
    "explain_profiles_of", "explain_survival", "fit_line", "fit_curve",
})

ID_WORDS = frozenset({"name", "id", "subject", "patient", "participant", "animal", "sample", "person", "child",
                      "pupil", "student", "individual", "respondent", "donor", "mouse", "case"})
_CODE = re.compile(r"(?=.*[A-Za-z])(?=.*[0-9])")
NAMED_LEAST = 4  # an ID names at least this many units
PLAIN_LEAST, PLAIN_MOST_REPEATS = 10, 10  # a column without an ID name: many values, each in a few rows


ID_TAILS = frozenset({"id", "ids", "name", "names", "code", "number", "no", "nr", "label"})


def _is_id_name(column) -> bool:
    """"name", "Subject", "patient_id", "Sample ID", "animal number": an ID word alone, "id" in the name, or an
    ID word with name/code/number after it. Not "patient_days" or "person_years" (measurements)."""
    words = re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", str(column)).lower())
    if not words:
        return False
    if len(words) == 1:
        return words[0] in ID_WORDS
    return "id" in words or "ids" in words or (words[-1] in ID_TAILS and any(w in ID_WORDS for w in words[:-1]))


def _codes(series) -> bool:
    """At least 4 in 5 different values hold a letter and a digit ("P01", "S12", "mouse3")."""
    values = [str(v) for v in series.drop_nulls().unique().to_list()]
    return bool(values) and sum(bool(_CODE.match(v)) for v in values) >= 0.8 * len(values)


def _used_columns(columns, values) -> set:
    """The columns a call names: as an option value, in a list, or as a word in a formula ("marks ~ class")."""
    names = {str(c) for c in columns}
    used = set()

    def visit(value):
        if isinstance(value, str):
            if value in names:
                used.add(value)
            else:
                used.update(w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", value) if w in names)
        elif isinstance(value, dict):
            for k, v in value.items():
                visit(k)
                visit(v)
        elif isinstance(value, (list, tuple, set)):
            for v in value:
                visit(v)

    visit(list(values))
    return used


def repeated_rows_note(frame, word: str, params, args, kwargs) -> str:
    """The one-line note, or "" (see the module docstring for the rule)."""
    if word not in WORDS or kwargs.get("matched_by") is not None or kwargs.get("grouped_by") is not None:
        return ""
    rows = len(frame)
    if rows < 3:
        return ""
    used = _used_columns(frame.columns, [*args, *kwargs.values()])
    best = None  # (named, distinct, column, counts)
    for column in frame.columns:
        if column in used:
            continue
        dtype = frame.schema[column]
        text = dtype in (nw.String, nw.Categorical, nw.Enum)
        if not (text or dtype.is_integer()):
            continue
        counts = frame[column].alias("__value").drop_nulls().value_counts(name="__rows")["__rows"].to_list()
        distinct = len(counts)
        if not counts or max(counts) < 2:
            continue
        named = _is_id_name(column)
        if named:
            fits = distinct >= NAMED_LEAST
        else:
            fits = (text and distinct >= PLAIN_LEAST and min(counts) >= 2 and max(counts) <= PLAIN_MOST_REPEATS
                    and _codes(frame[column]))
        if fits and (best is None or (named, distinct) > (best[0], best[1])):
            best = (named, distinct, column, counts)
    if best is None:
        return ""
    _, _, column, counts = best
    times = (f"each value appears {counts[0]} times" if min(counts) == max(counts)
             else f"values appear up to {max(counts)} times")
    ways = [f"{o}=" for o in ("matched_by", "grouped_by") if o in params]
    if word.startswith("compare_"):
        ways.append("compare_matched_columns")
    ways.append("one row per person (see lesson 14)")
    listed = ", ".join(ways[:-1]) + (", or " if len(ways) > 2 else " or ") + ways[-1] if len(ways) > 1 else ways[0]
    return (f'Note: "{column}" repeats ({times}), so these rows may not be independent. If the same person was '
            f"measured more than once, use {listed}.")
