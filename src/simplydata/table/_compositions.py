"""Checks shared by the community words (S3c-1): counts that are parts of a whole, and their zeros.

A resistome or microbiome table is compositional: the totals are set by how deeply each sample was sequenced, so
the words that read such a table (add_log_ratio_columns, measure="aitchison" on the distance words) first check the
counts and say what happens to the zeros. Nothing here computes a statistic: it counts zeros and compares totals,
and the replacement itself is R zCompositions::cmultRepl (community_r.py).

The rules come from the S3c design and its independent review (design_evidence_private/s3c_design.md 3.1 AC06,
s3c_independent_review_2026-11-20.md 5.1):
- negative values and rows with nothing in them are refused;
- "estimated small values" (multiplicative replacement, zCompositions GBM) needs raw counts: non-whole numbers are
  refused with the reason (GBM runs on them silently and gives other values);
- a column with fewer than two non-zero values is refused (GBM stops on it) with the line that merges such columns,
  so no column is deleted silently (cmultRepl's own default, z.delete = TRUE, would delete them);
- the zeros are summed up in one or two lines, never one line per column.
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError

# The spellings of zeros_replaced_by=: the plain name first, the field names accepted
ESTIMATED = "estimated small values"
ADDING_ONE = "adding 1"
ZERO_WAYS = {ESTIMATED: ESTIMATED, "multiplicative": ESTIMATED, "gbm": ESTIMATED,
             "multiplicative replacement": ESTIMATED, ADDING_ONE: ADDING_ONE, "add 1": ADDING_ONE,
             "pseudocount": ADDING_ONE}
MOSTLY_ZERO = 0.8  # a column that is zero in more than 80 % of rows (cmultRepl's own z.warning)
MERGED = "other"  # the name the merging line suggests


def quoted(names) -> str:
    names = [f'"{n}"' for n in names]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def short_list(names, most: int = 6) -> str:
    """Up to `most` column names, then "and 8 more"."""
    names = [str(n) for n in names]
    if len(names) <= most:
        return ", ".join(names)
    return ", ".join(names[:most]) + f" and {len(names) - most} more"


def whole_numbers(x) -> bool:
    """True when every value is a whole number (raw counts)."""
    finite = x[np.isfinite(x)]
    return bool(np.all(finite == np.round(finite)))


def check_not_negative(step, x, columns, what):
    if (x < 0).any():
        bad = [c for c, has in zip(columns, (x < 0).any(axis=0)) if has]
        raise SimplydataError(
            f"{step}() {what} needs counts or amounts, which cannot be below 0, but {quoted(bad[:5])} "
            f"{'has' if len(bad) == 1 else 'have'} values below 0.")


def check_no_empty_rows(step, x, what, labels=None):
    empty = np.flatnonzero((x > 0).sum(axis=1) == 0)
    if len(empty):
        which = ", ".join(str(labels[i]) if labels is not None else f"row {i + 1}" for i in empty[:5])
        raise SimplydataError(
            f"{step}() {what} cannot use a row with nothing in it (every value 0), and {len(empty)} "
            f"row{'s are' if len(empty) > 1 else ' is'} like that ({which}). Remove "
            f"{'them' if len(empty) > 1 else 'it'} first, for example with table.remove_rows_where(...).")


def merging_line(sparse, columns) -> str:
    """The lines that combine rare columns into one, ready to copy (with the existing column words)."""
    kept = [c for c in columns if c not in sparse] + [MERGED]
    shown = "[" + ", ".join(f'"{c}"' for c in kept) + "]"
    rare = ", ".join(f'"{c}"' for c in sparse)
    return (f'  table.add_column("{MERGED}", by_adding=[{rare}])\n'
            f"  then columns={shown}\n"
            f"This merges {len(sparse)} column{'s' if len(sparse) > 1 else ''} into one, so no count is lost.")


def check_zeros(step, x, columns, how, what, labels=None, measure_hint=True) -> int:
    """Check counts before log ratios; print one summary of the zeros. Gives back the number of zero cells.

    how: ESTIMATED (zCompositions GBM) or ADDING_ONE (vegan's pseudocount). what: the words for the error
    ("add_log_ratio_columns()" or 'measure="aitchison"')."""
    check_not_negative(step, x, columns, what)
    check_no_empty_rows(step, x, what, labels)
    zeros = x == 0
    count = int(zeros.sum())
    if not count:
        return 0
    lead = f"{step}() {what}".strip()
    if how == ADDING_ONE and not whole_numbers(x):
        raise SimplydataError(
            f'{lead} with zeros_replaced_by="adding 1" needs raw counts: on numbers that are not whole (shares, '
            "values per 16S or per million reads) a 1 swamps the values, and every log ratio comes out near 0. Give "
            'the raw counts, or use measure="robust aitchison" on the distance words, which needs no replacement.')
    if how == ESTIMATED:
        if not whole_numbers(x):
            other = ('use measure="robust aitchison", which needs no replacement' if measure_hint else
                     'use measure="robust aitchison" on the distance words, which needs no replacement')
            raise SimplydataError(
                f"{lead} replaces zeros by estimated small values (multiplicative replacement, R "
                "zCompositions GBM), which needs raw counts; these columns hold numbers that are not whole "
                "(normalised values, such as per 16S or per million reads?). GBM would run on them and give other "
                f"values than on the counts. Give the raw counts, or {other}.")
        nonzero = (~zeros).sum(axis=0)
        sparse = [c for c, k in zip(columns, nonzero) if k < 2]
        if sparse:
            raise SimplydataError(
                f"{lead} cannot estimate small values for {quoted(sparse[:8])}"
                f"{' and more' if len(sparse) > 8 else ''}: "
                f"{'it has' if len(sparse) == 1 else 'they have'} fewer than 2 values above 0, and R "
                "zCompositions GBM needs at least 2 in each column. Combine the rare columns into one first "
                "(if the merged column still has fewer than 2, leave the rare columns out):\n"
                + merging_line(sparse, columns))
    rows = x.shape[0]
    mostly = int((zeros.sum(axis=0) > MOSTLY_ZERO * rows).sum())
    replaced = ("replaced by estimated small values first (multiplicative replacement, R zCompositions GBM), so "
                "the logs exist" if how == ESTIMATED else
                "handled by adding 1 to every count first (a pseudocount), so the logs exist; the answer depends on "
                "the 1 you added")
    print(f"{count:,} of {zeros.size:,} cells are zero; they were {replaced}.")
    if mostly:
        print(f"Note: {mostly} of {len(columns)} columns are zero in more than 80 % of rows; their log ratios rest "
              "mostly on replaced values.")
    return count
