"""Answers on a scale (Likert items), phase S3d-1: the shared counting behind table.count_each(columns=, in_order=)
and chart.draw_answer_bars(columns=, in_order=).

Counting only: pandas counts each answer of each question (value_counts over the answers in in_order= order), the
percent is the count out of the answers given (as count_each), the "top two" are the two answers at the end of
in_order=, and the median answer is NumPy quantile(method="inverted_cdf") of the answers' places in the order (R
quantile(type = 1)): a real answer, never a value between two. No averages: the steps between answers need not be
equal (Jamieson 2004).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .._errors import SimplydataError

EXAMPLE = ('table.count_each(columns=["teaching", "materials", "pace"], in_order=["strongly disagree", "disagree", '
           '"neutral", "agree", "strongly agree"])   (with sdata.get_example("course_feedback"))')


def check_answers(word, data, columns, in_order, example=EXAMPLE):
    """The question columns and the answers in order, checked: every answer given must be in in_order=."""
    if isinstance(columns, str):
        columns = [columns]
    if not isinstance(columns, (list, tuple)) or not columns or not all(isinstance(c, str) for c in columns):
        raise SimplydataError(f"{word} needs columns=, the questions: a list of column names.\nFor example:  {example}")
    columns = list(dict.fromkeys(columns))
    missing = [c for c in columns if c not in data.columns]
    if missing:
        from .._errors import column_error

        raise column_error(missing[0], list(data.columns))
    if in_order is None or isinstance(in_order, str) or not isinstance(in_order, (list, tuple)):
        raise SimplydataError(f"{word} needs in_order=, the answers from the lowest to the highest, so that it knows "
                              f"which end is which.\nFor example:  {example}")
    levels = list(in_order)
    if len(levels) < 3:
        raise SimplydataError(f"in_order= needs at least 3 answers (you gave {len(levels)}); for yes or no answers use "
                              'table.find_percent_of_rows_where("question", is_equal_to="yes").')
    said = [str(v) for v in levels]
    if len(set(said)) < len(said):
        raise SimplydataError("in_order= names an answer twice; give each answer once.")
    for c in columns:
        given = data[c].dropna()
        given = given[given.astype(str).str.strip() != ""]
        unknown = sorted({str(v) for v in given} - set(said))
        if unknown:
            raise SimplydataError(
                f'"{c}" has answers that are not in in_order=: {", ".join(repr(u) for u in unknown[:5])}'
                f'{" ..." if len(unknown) > 5 else ""}. Add them to in_order= in their place, or fix the spelling '
                f'first: table.replace_values_in("{c}", {unknown[0]!r}, to="...")')
    return columns, said


def answer_table(data, columns, levels) -> pd.DataFrame:
    """One row per question: the answers given, the count and percent of each answer, the percent in the top two
    and the median answer (pandas counts, NumPy quantile(method="inverted_cdf"))."""
    rows = []
    top = set(levels[-2:])
    for c in columns:
        text = data[c].map(lambda v: None if v is None or (isinstance(v, float) and np.isnan(v)) or
                           str(v).strip() == "" else str(v))
        given = text.dropna()
        counts = given.value_counts().reindex(levels, fill_value=0)
        n = int(counts.sum())
        row = {"question": c, "answers": n}
        for level in levels:
            row[level] = int(counts[level])
        for level in levels:
            row[f"percent {level}"] = counts[level] * 100.0 / n if n else np.nan
        row["percent in top two"] = given.isin(top).sum() * 100.0 / n if n else np.nan
        if n:
            places = given.map({v: i for i, v in enumerate(levels)}).to_numpy(dtype=float)
            row["median answer"] = levels[int(np.quantile(places, 0.5, method="inverted_cdf"))]
        else:
            row["median answer"] = None
        row["empty"] = int(len(text) - n)
        rows.append(row)
    return pd.DataFrame(rows)
