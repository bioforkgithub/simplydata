"""Run an underneath entry next to its simplydata word and compare the two results.

Used by tests/test_underneath.py and by the reliability report (validation/make_report.py), so the
manual's boxes, the tests and the report check the same thing in the same way.

    check_entry(entry)                  -> [Outcome, ...]   one per library block (and table engine)
    chart_facts(ax)                     -> {fact: value}    what a chart shows, as data
    compare_charts(a, b, check, tol)    -> [difference, ...]
"""

from __future__ import annotations

import ast
import contextlib
import io
import math
import textwrap
from dataclasses import dataclass, field

import numpy as np

from . import CHART_FACTS, Entry

OLD_NAME_NOTE = "is now called"


@dataclass
class Outcome:
    """One comparison: the word against one library block (on one table engine)."""

    word: str
    library: str
    engine: str
    compare: str
    tolerance: float
    passed: bool
    differences: list = field(default_factory=list)
    skipped: str = ""  # why it did not run (R missing), else ""

    @property
    def status(self) -> str:
        return "skipped" if self.skipped else ("pass" if self.passed else "FAIL")


# ---------------------------------------------------------------- running code
def run_python(source: str, namespace: dict | None = None):
    """Run Python code; give back (value of the last line if it is an expression, what it printed, namespace)."""
    import simplydata

    ns = {"sdata": simplydata, "__name__": "__underneath__"} if namespace is None else namespace
    ns.setdefault("sdata", simplydata)
    tree = ast.parse(textwrap.dedent(source))
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    printed = io.StringIO()
    value = None
    with contextlib.redirect_stdout(printed):
        exec(compile(tree, "<underneath>", "exec"), ns)  # noqa: S102 - our own code, from the registry
        if last is not None:
            value = eval(compile(ast.Expression(last.value), "<underneath>", "eval"), ns)  # noqa: S307
    return value, printed.getvalue(), ns


@contextlib.contextmanager
def _practice_tables_as(engine: str):
    """While ours runs, sdata.get_example gives Polars tables (engine="polars") instead of pandas."""
    import simplydata

    if engine == "pandas":
        yield
        return
    import polars as pl

    original = simplydata.get_example

    def as_polars(name=None):
        found = original(name)
        return None if found is None else pl.from_pandas(found)

    simplydata.get_example = as_polars
    try:
        yield
    finally:
        simplydata.get_example = original


def run_ours(entry: Entry, engine: str = "pandas"):
    """Run the simplydata side; give back (result, printed)."""
    with _practice_tables_as(engine):
        value, printed, _ = run_python(entry.ours_code())
    return value, printed


def engines(entry: Entry) -> list[str]:
    """Table words run on a pandas and on a Polars table; other words on pandas."""
    if entry.word.startswith("table."):
        try:
            import polars  # noqa: F401
        except ImportError:  # pragma: no cover - Polars is a dependency
            return ["pandas"]
        return ["pandas", "polars"]
    return ["pandas"]


# ---------------------------------------------------------------- what a chart shows
def _axes_of(value, library_side: bool = False):
    """The Axes a result stands for: a simplydata chart, a Figure or an Axes. Only the library side may
    fall back to the current figure (seaborn and matplotlib draw on it); a simplydata word that gives
    back anything else is an error, so a chart is never compared with itself."""
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    if isinstance(value, Axes):
        return value
    if isinstance(value, Figure):
        return value.axes[0]
    if hasattr(value, "_render"):
        return value._render().axes[0]
    if not library_side:
        raise TypeError(f"the simplydata code gave back {type(value).__name__}, not a chart: end ours= with the "
                        "chart (chart.draw_bars(...) gives it back)")
    if not plt.get_fignums():
        raise TypeError("the library code drew no chart")
    return plt.gcf().axes[0]


def _colour_groups(colours) -> list[int]:
    """Each item's colour as the number of its colour in order of first appearance: [0, 0, 1, 2, 1].
    Which items share a colour is compared, not the colours themselves (simplydata has its own palette)."""
    seen: dict = {}
    out = []
    for c in colours:
        key = tuple(np.round(np.asarray(c, dtype=float), 6))
        out.append(seen.setdefault(key, len(seen)))
    return out


def chart_facts(ax) -> dict:
    """What a chart shows, as data: compare these, not pixels.

    bars              sorted (x, y, width, height) of every bar (Rectangle) on the axes
    bar_colour_groups which bars share a colour, in the sorted order of bars
    dots              every dot's (x, y), group by group as drawn
    dot_size_shares   each dot's size as a share of the biggest (simplydata's look scales all sizes)
    dot_colour_groups which dots share a colour
    lines             (x values, y values) of every line
    labels            (x label, y label, title)
    ticks             the words under the x axis and beside the y axis
    legend            the legend's title and entries
    limits            (x limits, y limits)
    scales            ("linear" or "log", for x and y)
    panels            the number of charts in the figure
    texts             the other words on the figure (titles above several panels, notes, captions, numbers on
                      bars), sorted: (words on the figure, words on the chart)
    font_sizes        the font sizes of the title, the x and y labels, the x and y tick labels and the legend
    size              the figure's width and height in inches
    legend_place      each legend: on the chart or on the figure, matplotlib's place code, the side outside the
                      chart (empty inside it), its number of columns, its title and entries
    colours           the colours themselves (as #rrggbbaa): of the bars (sorted as in bars), the dots and the lines
    tick_angles       the angle and the alignment of each tick label, under the x axis and beside the y axis
    shapes            the corners of every filled shape that is not a bar (violins, boxes, bands)
    cells             the numbers behind each grid of coloured cells (a heatmap)
    every_panel       for each set of axes in the figure (second y-axes too): its labels, title, dots, bars,
                      lines and filled shapes
    """
    from matplotlib.patches import Rectangle

    rects = [p for p in ax.patches if isinstance(p, Rectangle)]
    bars = sorted(((float(r.get_x()), float(r.get_y()), float(r.get_width()), float(r.get_height()), r.get_facecolor())
                   for r in rects), key=lambda b: b[:4])
    dots, sizes, dot_colours = [], [], []
    for coll in ax.collections:
        offsets = np.asarray(coll.get_offsets(), dtype=float)
        if offsets.ndim != 2 or len(offsets) == 0 or coll.__class__.__name__ != "PathCollection":
            continue
        dots.extend(map(tuple, offsets))
        s = np.asarray(coll.get_sizes(), dtype=float)
        if len(s) == len(offsets):
            sizes.extend(s)
        else:  # one size for every dot, or none
            sizes.extend([s[0] if len(s) else np.nan] * len(offsets))
        fc = coll.get_facecolors()
        dot_colours.extend(fc if len(fc) == len(offsets) else [fc[0] if len(fc) else (0, 0, 0, 0)] * len(offsets))
    sizes = np.asarray(sizes, dtype=float)
    biggest = np.nanmax(sizes) if sizes.size and not np.all(np.isnan(sizes)) else 1.0
    legend = ax.get_legend()
    fig = ax.get_figure()
    return {
        "bars": [b[:4] for b in bars],
        "bar_colour_groups": _colour_groups([b[4] for b in bars]),
        "dots": dots,
        "dot_size_shares": list(sizes / biggest) if sizes.size else [],
        "dot_colour_groups": _colour_groups(dot_colours),
        "lines": [(np.asarray(line.get_xdata(), dtype=float), np.asarray(line.get_ydata(), dtype=float))
                  for line in ax.get_lines()],
        "labels": (ax.get_xlabel(), ax.get_ylabel(), ax.get_title()),
        "ticks": ([t.get_text() for t in ax.get_xticklabels()], [t.get_text() for t in ax.get_yticklabels()]),
        "legend": (([legend.get_title().get_text()] + [t.get_text() for t in legend.get_texts()])
                   if legend is not None else []),
        "limits": (tuple(map(float, ax.get_xlim())), tuple(map(float, ax.get_ylim()))),
        "scales": (ax.get_xscale(), ax.get_yscale()),
        "panels": len([a for a in fig.axes if a.get_label() != "<colorbar>"]) if fig is not None else 1,
        "texts": _texts(ax),
        "font_sizes": _font_sizes(ax),
        "size": tuple(map(float, _root(ax).get_size_inches())) if _root(ax) is not None else (),
        "legend_place": _legend_places(ax),
        "colours": ([_hex(b[4]) for b in bars], [_hex(c) for c in dot_colours],
                    [_hex(line.get_color()) for line in ax.get_lines()]),
        "tick_angles": ([(float(t.get_rotation()), t.get_ha()) for t in ax.get_xticklabels()],
                        [(float(t.get_rotation()), t.get_ha()) for t in ax.get_yticklabels()]),
        "shapes": _shapes(ax),
        "cells": _cells(ax),
        "every_panel": ([_panel(a) for a in _root(ax).axes if a.get_label() != "<colorbar>"]
                        if _root(ax) is not None else []),
    }


def _root(ax):
    """The whole figure an Axes is on (not the part of a page it sits in)."""
    try:
        return ax.get_figure(root=True)
    except TypeError:  # pragma: no cover - matplotlib before 3.10
        return ax.get_figure()


def _hex(colour) -> str:
    from matplotlib.colors import to_hex

    return to_hex(colour, keep_alpha=True)


def _shown(text) -> str:
    return text.get_text().strip() if text is not None and text.get_visible() else ""


def _texts(ax) -> tuple:
    """(words on the figure and the parts of a page, words on the chart): each sorted, empty ones left out."""
    from matplotlib.text import Text

    root = _root(ax)
    on_figure = []
    figures = [root] if root is not None else []
    while figures:
        f = figures.pop(0)
        figures.extend(getattr(f, "subfigs", []))
        found = [getattr(f, name, None) for name in ("_suptitle", "_supxlabel", "_supylabel")]
        found += list(f.texts) + [a for a in f.artists if isinstance(a, Text)]
        on_figure += found
    on_figure = [_shown(t) for t in dict.fromkeys(t for t in on_figure if t is not None)]  # a title is in texts too
    on_chart = [_shown(t) for t in ax.texts]
    return sorted(t for t in on_figure if t), sorted(t for t in on_chart if t)


def _font_sizes(ax) -> tuple:
    def first(labels):
        return float(labels[0].get_fontsize()) if labels else math.nan

    root = _root(ax)
    legend = ax.get_legend() or next(iter(root.legends if root is not None else []), None)
    return (float(ax.title.get_fontsize()), float(ax.xaxis.label.get_fontsize()), float(ax.yaxis.label.get_fontsize()),
            first(ax.get_xticklabels()), first(ax.get_yticklabels()),
            first(legend.get_texts()) if legend is not None else math.nan)


def _legend_places(ax) -> list:
    root = _root(ax)
    found = [("chart", ax.get_legend())] + [("figure", leg) for leg in (root.legends if root is not None else [])]
    return [(owner, int(leg._loc), getattr(leg, "_outside_loc", None) or "", int(leg._ncols),
             [leg.get_title().get_text()] + [t.get_text() for t in leg.get_texts()])
            for owner, leg in found if leg is not None and leg.get_visible()]


def _sized(points) -> tuple:
    """(how many, the array): arrays of different lengths are then compared by their length first."""
    points = np.asarray(points, dtype=float)
    return (len(points), points)


def _shapes(ax) -> list:
    from matplotlib.patches import Rectangle

    found = []
    for coll in ax.collections:
        if coll.__class__.__name__ in ("PathCollection", "QuadMesh", "LineCollection") or not hasattr(coll, "get_paths"):
            continue
        found += [_sized(path.vertices) for path in coll.get_paths()]
    found += [_sized(p.get_path().vertices) for p in ax.patches if not isinstance(p, Rectangle)]
    return found


def _cells(ax) -> list:
    grids = [c for c in ax.collections if c.__class__.__name__ == "QuadMesh"] + list(ax.images)
    return [_sized(np.ma.filled(np.ma.asarray(g.get_array(), dtype=float), np.nan).ravel()) for g in grids]


def _panel(ax) -> tuple:
    """What one set of axes shows: labels, title, dots, bars, lines and filled shapes (for figures with several)."""
    from matplotlib.patches import Rectangle

    dots = [tuple(o) for c in ax.collections if c.__class__.__name__ == "PathCollection"
            for o in np.asarray(c.get_offsets(), dtype=float).reshape(-1, 2)]
    bars = sorted((float(r.get_x()), float(r.get_y()), float(r.get_width()), float(r.get_height()))
                  for r in ax.patches if isinstance(r, Rectangle))
    # lines with no points (seaborn adds them for legend entries) show nothing, so they are left out
    lines = [(_sized(line.get_xdata()), _sized(line.get_ydata())) for line in ax.get_lines() if len(line.get_xdata())]
    return (ax.get_xlabel(), ax.get_ylabel(), ax.get_title(), ax.get_title(loc="left"),
            _sized(dots) if dots else (0,), _sized(bars) if bars else (0,), lines, _shapes(ax))


def _same(a, b, tol: float) -> bool:
    """Equal, with numbers compared to a relative tolerance (and 1e-12 absolute, for zeros)."""
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)) or isinstance(a, np.ndarray):
        try:
            if len(a) != len(b):
                return False
        except TypeError:
            return False
        if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
            a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
            return bool(np.allclose(a, b, rtol=tol, atol=1e-12, equal_nan=True))
        return all(_same(x, y, tol) for x, y in zip(a, b))
    if a is None or b is None:
        return a is b
    try:
        x, y = float(a), float(b)
    except (TypeError, ValueError):
        return a == b
    if math.isnan(x) or math.isnan(y):
        return math.isnan(x) and math.isnan(y)
    return math.isclose(x, y, rel_tol=tol, abs_tol=1e-12)


def compare_charts(ours: dict, theirs: dict, check, tol: float) -> list[str]:
    out = []
    for name in check:
        if name not in CHART_FACTS:
            raise ValueError(f"{name} is not a chart fact; use one of {', '.join(CHART_FACTS)}")
        if not _same(ours[name], theirs[name], tol):
            out.append(f"{name}: simplydata {_short(ours[name])} | library {_short(theirs[name])}")
    return out


def _short(value, width: int = 200) -> str:
    text = repr(value)
    return text if len(text) <= width else text[: width - 3] + "..."


# ---------------------------------------------------------------- comparing results
def _as_pandas(value):
    import pandas as pd

    if hasattr(value, "as_pandas"):
        value = value.as_pandas()
    if hasattr(value, "to_pandas") and not isinstance(value, (pd.DataFrame, pd.Series)):
        value = value.to_pandas()
    if isinstance(value, pd.Series):
        value = value.reset_index()
    return value.reset_index(drop=True)


def compare_tables(ours, theirs, names: dict, tol: float) -> list[str]:
    import pandas as pd

    a = _as_pandas(ours).rename(columns=names)
    b = _as_pandas(theirs)
    if list(a.columns) != list(b.columns):
        return [f"columns: simplydata {list(a.columns)} | library {list(b.columns)}"]
    if a.shape != b.shape:
        return [f"shape: simplydata {a.shape} | library {b.shape}"]
    out = []
    for col in a.columns:
        x, y = a[col], b[col]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            if not np.allclose(x.to_numpy(dtype=float), y.to_numpy(dtype=float), rtol=tol, atol=1e-12, equal_nan=True):
                out.append(f"{col}: the numbers differ")
        elif [str(v) for v in x] != [str(v) for v in y]:
            out.append(f"{col}: the values differ")
    return out


def compare_result(ours, theirs: dict, fields, tol: float, row_name: str = "") -> list[str]:
    frame = _as_pandas(ours)
    if row_name:
        found = frame[frame["term"] == row_name]
        if not len(found):
            return [f"no row {row_name!r} in simplydata's result"]
        row = found.iloc[0]
    else:
        row = frame.iloc[0]
    out = []
    for name in fields:
        if name not in theirs:
            out.append(f"{name}: the library code does not give it")
        elif not _same(row[name], theirs[name], tol):
            out.append(f"{name}: simplydata {row[name]!r} | library {theirs[name]!r}")
    return out


def compare_printed(ours: str, theirs: str) -> list[str]:
    """Every line the library code printed appears, in the same order, in what simplydata printed (simplydata may
    print more: a sentence before or after). Spaces at the ends of lines are left out."""
    mine = [line.rstrip() for line in ours.splitlines()]
    wanted = [line.rstrip() for line in theirs.splitlines() if line.strip()]
    if not wanted:
        return ["the library code printed nothing"]
    at = 0
    for line in wanted:
        while at < len(mine) and mine[at] != line:
            at += 1
        if at == len(mine):
            return [f"simplydata did not print the line {line!r} (in this order)"]
        at += 1
    return []


def compare_values(ours, theirs, tol: float) -> list[str]:
    return [] if _same(ours, theirs, tol) else [f"simplydata {ours!r} | library {theirs!r}"]


def compare(entry: Entry, ours, theirs) -> list[str]:
    if entry.compare == "chart":
        return compare_charts(chart_facts(_axes_of(ours)), chart_facts(_axes_of(theirs, library_side=True)),
                              entry.check, entry.tolerance)
    if entry.compare == "table":
        return compare_tables(ours, theirs, entry.names, entry.tolerance)
    if entry.compare == "result":
        return compare_result(ours, theirs, entry.fields, entry.tolerance, entry.row)
    if entry.compare == "value":
        if hasattr(ours, "as_numpy"):  # simplydata numbers or a grid: ours ends with the word itself
            ours = ours.as_numpy()
        return compare_values(ours, theirs, entry.tolerance)
    raise ValueError(f"{entry.word}: compare={entry.compare!r} cannot be run")


# ---------------------------------------------------------------- one entry
def _r_values(entry: Entry) -> dict:
    """The values the R block uses, made by r_inputs from the practice table."""
    _, _, ns = run_python(entry.r_inputs)
    return {k: v for k, v in ns.items() if not k.startswith("__") and k != "sdata" and isinstance(v, np.ndarray)}


def _run_with_r(entry: Entry):
    """Blocks as one program: R gets its values, the Python block after R carries on with R's answer."""
    from .._r import need_r, r_call

    namespace: dict = {}
    value = None
    seen_r = False
    for library, language, source in entry.blocks():
        if language == "r":
            # checked, not attached: the boxes call R packages by name (pROC::roc, drc::drm), and an attached
            # package can hide base R functions from later calls (drc's gaussian(), SparseM's matrix functions)
            need_r(entry.r_packages, f"the underneath code of {entry.word}")
            found = r_call(source, what=f"the underneath code of {entry.word}",
                           **_r_values(entry))
            for k, v in (found or {}).items():
                arr = np.asarray(v, dtype=float)
                namespace[k] = arr if arr.size != 1 else float(arr.reshape(-1)[0])
            seen_r = True
        elif seen_r:
            value, _, namespace = run_python(source, namespace)
    return value, namespace


def compare_legend_numbers(entry: Entry, ours, found: dict) -> list[str]:
    """The numbers simplydata writes in its legend (such as the AUC and its interval) against what R gave,
    to the digits printed (half a unit of the last printed digit)."""
    import re

    if not entry.legend_numbers:
        return []
    texts = chart_facts(_axes_of(ours))["legend"][1:]
    m = next((re.search(entry.legend_pattern, t) for t in texts if re.search(entry.legend_pattern, t)), None)
    if m is None:
        return [f"legend: no text matching {entry.legend_pattern!r} in {texts!r}"]
    out = []
    for name, shown in zip(entry.legend_numbers, m.groups()):
        decimals = len(shown.split(".")[1]) if "." in shown else 0
        if name not in found:
            out.append(f"legend: R gave no {name}")
        elif abs(float(shown) - float(found[name])) > 0.5 * 10 ** -decimals + 1e-12:
            out.append(f"legend {name}: simplydata shows {shown} | R {found[name]!r}")
    return out


def check_entry(entry: Entry) -> list[Outcome]:
    """Run the word and each library block, and compare them. R words that cannot run (no R) are skipped."""
    import matplotlib.pyplot as plt

    outcomes = []
    if entry.compare == "none":
        return [Outcome(entry.key, "-", "-", "none", 0.0, bool(entry.note.strip()),
                        [] if entry.note.strip() else ["a word with nothing underneath needs a note="])]
    for engine in engines(entry):
        try:
            if entry.uses_r:
                from .._r import r_ready

                needed = tuple(dict.fromkeys(entry.r_packages + entry.ours_r))
                if not r_ready(needed):
                    outcomes.append(Outcome(entry.key, "R", engine, entry.compare, entry.tolerance, False,
                                            skipped="R, rpy2 or the R packages " + ", ".join(needed)
                                                    + " are not installed"))
                    continue
                ours, printed = run_ours(entry, engine)
                theirs, found = _run_with_r(entry)
                differences = compare(entry, ours, theirs) + compare_legend_numbers(entry, ours, found)
                if OLD_NAME_NOTE in printed:
                    differences.append("the simplydata code uses an old name: " + printed.strip())
                library = " + ".join(lib for lib, _, _ in entry.blocks())
                outcomes.append(Outcome(entry.key, library, engine, entry.compare, entry.tolerance,
                                        not differences, differences))
                continue
            for library, _, source in entry.blocks():
                ours, printed = run_ours(entry, engine)
                theirs, their_print, _ = run_python(source)
                if entry.compare == "printed":
                    differences = compare_printed(printed, their_print)
                else:
                    differences = compare(entry, ours, theirs)
                if OLD_NAME_NOTE in printed:
                    differences.append("the simplydata code uses an old name: " + printed.strip())
                outcomes.append(Outcome(entry.key, library, engine, entry.compare, entry.tolerance,
                                        not differences, differences))
                plt.close("all")
        finally:
            plt.close("all")
    return outcomes
