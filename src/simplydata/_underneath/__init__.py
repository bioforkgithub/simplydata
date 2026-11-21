"""The same work in the packages underneath: one tested entry per simplydata word.

Each entry keeps, once, the code that does a word's job in the package simplydata uses: pandas and
Polars for tables, NumPy for numbers, matplotlib or seaborn for charts, SciPy or statsmodels for
statistics, and R where simplydata calls R. tests/test_underneath.py runs every entry next to the
simplydata word and checks that both give the same numbers, the same table, or a chart with the same
bars, dots, lines and labels (data, not pixels). The manual's grey box "The same underneath", the
dictionary's "Underneath:" line and the reliability report in validation/ are all made from here.

UNDERNEATH is keyed by the word's key in simplydata.learn ("draw_bars", "table.find_average_of",
"nums.find_median"). An option that changes what a word calls underneath gets an entry of its own,
keyed by the word and the option ("table.explain weights="): its box follows the word's in the manual.
The library code holds no simplydata names except sdata.get_example(), so a rename only touches the
key and the ours= line; docs/rename_underneath_keys.py rewrites both.

The entries are split by area: charts.py, tables.py, numbers.py, statistics.py, models.py (the options of
explain()), lines.py (the lines-and-curves words and their options), checking.py (the checking-and-comparing
words and their options), survival.py (S3b-3: the survival and person-time words and options),
combining.py (S3b-1: combining studies), planning.py (S3b-2: the power words and their options) and
communities.py (S3c-1: communities and resistomes), hidden_factors.py (S3c-2: the hidden-factor words and
their options), places.py (S3c-3: directions, places and extremes) and small_additions.py (S3c-4: weighted
percentiles, covariance, the automatic ARIMA order, q-values, pair tests after Friedman and pairs of percents) and
planning_surveys.py (S3d-1: the design words, stratified random rows, patterns of empty cells, answers on a scale and
the survey words),
causal.py (S3d-2: balancing groups, attributable fractions, standardised rates, mediation, the 2 x 2 crossover and
multiple imputation for other words) and bayesian.py (S3d-3: bayesian=True on the tests, explain and check_model_of).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

# How the test compares the two results
COMPARE_KINDS = {
    "value": "the number the word gives, against the library's number",
    "table": "the table the word gives, against the library's table (values and column order)",
    "result": "the numbers in simplydata's result table (statistic, degrees of freedom, p-value ...) against the "
              "library's result",
    "chart": "the chart's data (bars, dots, lines, labels, limits ...), not its pixels",
    "none": "nothing to compare: simplydata's own work, explained in one line",
}

# The facts chart_facts() reads from a chart; an entry names the ones its test compares
CHART_FACTS = ("bars", "bar_colour_groups", "dots", "dot_size_shares", "dot_colour_groups", "lines", "labels",
               "ticks", "legend", "limits", "scales", "panels")

R_LABEL = "R (simplydata runs this in R for you, through rpy2)"


@dataclass(frozen=True)
class Entry:
    """One word and the same work in the package underneath.

    word:     the key in simplydata.learn (a current name: a test checks it is not an old one)
    option:   for an entry of one option of the word: the option as written, "weights=" (its box shows the
              same job with that option); empty for the word's own entry
    ours:     the simplydata code the test runs; its last line gives the result
    code:     the library code shown in the manual, {library: code}, in the order shown. Python blocks
              are separate ways to do the same job (pandas, then Polars), each compared with ours.
              When there is an "R" block, the blocks are one program instead: the Python block before R
              is skipped by the run, R gets the values its code names from r_inputs, and the Python
              block after R carries on with what R gives back (a named list becomes variables).
    compare:  how the test compares (COMPARE_KINDS)
    data:     the practice table both versions use (sdata.get_example)
    choices:  "simplydata chooses" lines, one per mark (1), (2) ... written in the code as a comment
    also:     one line on what simplydata also does that the code leaves out
    tolerance: relative tolerance for numbers
    names:    for compare="table": simplydata's column name -> the library's
    fields:   for compare="result": the columns of simplydata's result table that are compared (the
              library code ends with a dict that has the same keys)
    row:      for compare="result": the row of the result table that is compared, by its "term" (the first
              row when empty)
    check:    for compare="chart": which CHART_FACTS are compared
    legend_pattern, legend_numbers: for R chart words, a regular expression that finds numbers in the first
              legend entry of simplydata's chart, and the names of the R results they must equal (to the
              digits printed)
    r_inputs: Python code that makes the values the R block uses (from the practice table)
    r_packages: R packages the R block loads
    ours_r:   R packages simplydata's own side needs (as Case.ours_r) when the R block needs none or others: the
              comparison is skipped without them too (S3a-3: the nested ANOVA's variances come from lme4)
    python_note: for R words, a line on what Python alone gives
    note:     for compare="none": what simplydata does on its own, and how you would do it yourself
    """

    word: str
    ours: str
    code: dict = field(default_factory=dict)
    option: str = ""
    compare: str = "value"
    data: str | None = None
    choices: tuple = ()
    also: str = ""
    tolerance: float = 1e-9
    names: dict = field(default_factory=dict)
    fields: tuple = ()
    row: str = ""
    check: tuple = ()
    legend_pattern: str = ""
    legend_numbers: tuple = ()
    r_inputs: str = ""
    r_packages: tuple = ()
    ours_r: tuple = ()
    python_note: str = ""
    note: str = ""

    @property
    def uses_r(self) -> bool:
        return "R" in self.code

    @property
    def key(self) -> str:
        """The key in UNDERNEATH: the word, or the word and the option ("table.explain weights=")."""
        return f"{self.word} {self.option}" if self.option else self.word

    def blocks(self) -> list[tuple[str, str, str]]:
        """(library, language, code) of each block, in the order shown; code without its outer indent."""
        import textwrap

        return [(lib, "r" if lib == "R" else "python", textwrap.dedent(src).strip("\n"))
                for lib, src in self.code.items()]

    def ours_code(self) -> str:
        import textwrap

        return textwrap.dedent(self.ours).strip("\n")


def _join() -> dict[str, Entry]:
    from . import (bayesian, causal, charts, checking, combining, communities, hidden_factors, lines, models, numbers,
                   places,
                   planning, planning_surveys, small_additions, statistics, survival, tables)

    found: dict[str, Entry] = {}
    for module in (charts, tables, numbers, statistics, models, lines, checking, survival, combining, planning,
                   communities, hidden_factors, places, small_additions, planning_surveys, causal, bayesian):
        for entry in module.ENTRIES:
            if entry.key in found:
                raise ValueError(f"{entry.key} has two underneath entries")
            found[entry.key] = entry
    return found


def option_entries(word: str) -> list[Entry]:
    """The entries of a word's options, in the order they are written."""
    return [e for e in UNDERNEATH.values() if e.word == word and e.option]


UNDERNEATH: dict[str, Entry] = _join()


# ---------------------------------------------------------------- the one-line "Underneath" name
# Calls that only set the stage (the practice table, a figure, imports, the dict of results) are not named
_STAGE = {"get_example", "subplots", "from_pandas", "dict", "list", "len", "print", "float", "int", "array",
          "asarray", "lexsort"}


def _chain(node) -> tuple[str, list]:
    """A call chain as written after its first name: df.groupby(...)["marks"].mean() -> "groupby().mean()",
    with the calls inside the chain (they are part of it, not calls of their own)."""
    parts, inner = [], []
    while True:
        if isinstance(node, ast.Call):
            parts.append("()")
            inner.append(node)
            node = node.func
        elif isinstance(node, ast.Attribute):
            parts.append("." + node.attr)
            node = node.value
        elif isinstance(node, ast.Subscript):
            node = node.value
        else:
            if isinstance(node, ast.Name) and parts and parts[-1] == "()":
                parts.append(node.id)  # a function called by its own name: anova_oneway(...)
            break
    text = "".join(reversed(parts)).lstrip(".")
    return text, inner


def _python_calls(source: str) -> list[str]:
    """The library calls a Python block makes, in the order written: "barplot()", "groupby().mean()".
    A boolean mask, df[df["marks"] > 50], counts as "boolean indexing"."""
    tree = ast.parse(source)
    inner: set = set()
    chains = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and id(node) not in inner:
            text, calls = _chain(node)
            inner.update(id(c) for c in calls)
            chains.append((node.lineno, node.col_offset, text))
        if isinstance(node, ast.Subscript) and isinstance(node.slice, (ast.Compare, ast.BoolOp)):
            chains.append((node.lineno, node.col_offset, "boolean indexing"))
    found = []
    for _, _, text in sorted(chains):
        first = text.split("(")[0].split(".")[0]
        if text and first not in _STAGE and text not in found:
            found.append(text)
    return found


def _r_calls(source: str) -> list[str]:
    import re

    found = []
    for m in re.finditer(r"\b([A-Za-z][\w.]*::[\w.]+)\s*\(", source):
        if m.group(1) + "()" not in found:
            found.append(m.group(1) + "()")
    return found


def library_calls(entry: Entry) -> list[tuple[str, list[str]]]:
    """[(library, [calls])] for each block: what the one-line "Underneath" name is made from."""
    out = []
    for library, language, source in entry.blocks():
        calls = _r_calls(source) if language == "r" else _python_calls(source)
        out.append((library, calls))
    return out


def underneath_line(entry: Entry) -> str:
    """One line for the dictionary and the manual: "seaborn barplot · Polars filter" (read from the code)."""
    if entry.compare == "none":
        return entry.note
    parts = []
    for library, calls in library_calls(entry):
        if calls:
            parts.append(f"{library} " + ", ".join(calls))
    return " · ".join(parts)
