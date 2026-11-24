"""Answers on a scale (Likert items), phase S3d-1: chart.draw_answer_bars(columns=, in_order=).

One bar per question, cut into the answers' percents (the counts of table.count_each(columns=, in_order=), from
pandas), drawn with matplotlib barh as diverging stacked bars (Heiberger & Robbins 2014): the answers below the
middle go left of 0, those above it go right, and the middle answer (an odd number of answers) is split half and
half across 0. With an even number of answers there is no middle answer and the bars meet at 0 between the middle
two. Colours: two hues with a neutral grey in the middle (no colour at the midpoint).
"""

from __future__ import annotations

from .._typing import _Same

import numpy as np

from .._errors import friendly
from .charts import _remember

LOW_COLOURS = ("#b2182b", "#ef8a62", "#fbc4a6")    # strong to mild disagreement (reds)
HIGH_COLOURS = ("#c6dbef", "#67a9cf", "#2166ac")   # mild to strong agreement (blues)
MIDDLE_COLOUR = "#bdbdbd"
EXAMPLE = ('chart.draw_answer_bars(columns=["teaching", "materials", "pace"], in_order=["strongly disagree", '
           '"disagree", "neutral", "agree", "strongly agree"])   (with sdata.get_example("course_feedback"))')


def answer_colours(k):
    """k colours: reds for the low half (darkest at the low end), blues for the high half (darkest at the high end),
    grey for a middle answer; the two halves mirror each other."""
    half = k // 2
    if half > 3:  # long scales: steps of matplotlib's red-blue ramp, so neighbouring answers never share a colour
        import matplotlib
        from matplotlib.colors import to_hex

        ramp = matplotlib.colormaps["RdBu"]
        low = [to_hex(ramp(0.05 + 0.35 * i / (half - 1))) for i in range(half)]
        high = [to_hex(ramp(0.6 + 0.35 * i / (half - 1))) for i in range(half)]
        return low + ([MIDDLE_COLOUR] if k % 2 else []) + high
    pick = {1: [1], 2: [0, 1], 3: [0, 1, 2]}[half]
    low = [LOW_COLOURS[i] for i in pick]
    high = [HIGH_COLOURS[2 - i] for i in reversed(pick)]
    return low + ([MIDDLE_COLOUR] if k % 2 else []) + high


def _draw_answers(ctx, columns, levels):
    from ..table.answers import answer_table

    ax = ctx.ax
    found = answer_table(ctx.data, columns, levels)
    shares = found[[f"percent {lv}" for lv in levels]].to_numpy(dtype=float)
    k = len(levels)
    half = k // 2
    # [D] drawing positions only: each bar starts left of 0 by the low answers' percents and half the middle answer
    middle = shares[:, half] / 2 if k % 2 else np.zeros(len(shares))
    start = -(shares[:, :half].sum(axis=1) + middle)
    lefts = start[:, None] + np.concatenate([np.zeros((len(shares), 1)), np.cumsum(shares, axis=1)[:, :-1]], axis=1)
    rows = np.arange(len(columns))[::-1]  # the first question at the top
    surface = ax.get_facecolor()
    for j, (level, colour) in enumerate(zip(levels, answer_colours(k))):
        ax.barh(rows, shares[:, j], left=lefts[:, j], height=0.7, color=colour, label=str(level),
                edgecolor=surface, linewidth=1)
    ax.axvline(0, color="#525252", linewidth=0.8)
    ax.set_yticks(rows, labels=[str(c) for c in columns])
    reach = float(np.nanmax(np.abs(np.concatenate([lefts[:, :1], lefts[:, -1:] + shares[:, -1:]], axis=1)))) \
        if len(shares) else 50.0
    ax.set_xlim(-reach * 1.05 - 1, reach * 1.05 + 1)
    ticks = ax.get_xticks()
    ax.set_xticks(ticks, labels=[f"{abs(t):g}" for t in ticks])
    ax.set_xlim(-reach * 1.05 - 1, reach * 1.05 + 1)
    if ax.get_xlabel() == "":
        ax.set_xlabel("Percent of answers (left of 0: below the middle; right: above)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=min(k, 5), frameon=False)
    _remember(ctx, "draw_answer_bars", found, {"x": None, "y": None, "colour": None})


class AnswerChartWords:
    @friendly(others={"items": "columns", "questions": "columns", "levels": "in_order", "order": "in_order"})
    def draw_answer_bars(self: _Same, columns=None, in_order=None) -> _Same:
        """Bars of answers on a scale (Likert items): one bar per question, centred on the middle answer.

        chart.draw_answer_bars(columns=["teaching", "materials", "pace"], in_order=["strongly disagree", "disagree", "neutral", "agree", "strongly agree"])   (with sdata.get_example("course_feedback"))
        columns= the questions; in_order= the answers from the lowest to the highest. Each bar shows
        the percent of each answer (of the answers given; empty cells are left out): answers below
        the middle go left of 0, answers above it right, and the middle answer is split across 0
        (diverging stacked bars, Heiberger & Robbins 2014). table.count_each(columns=, in_order=)
        gives the same numbers as a table.
        """
        from ..table.answers import check_answers

        word = "draw_answer_bars"
        data = self._data
        columns, levels = check_answers(f".{word}()", data, columns, in_order, EXAMPLE)
        k = len(levels)
        middle = f'the middle answer, "{levels[k // 2]}", is split half and half across 0' if k % 2 else \
            f'with {k} answers there is no middle one: the bars meet at 0 between "{levels[k // 2 - 1]}" and ' \
            f'"{levels[k // 2]}"'
        print(f"Answer bars for {len(columns)} question{'s' * (len(columns) != 1)}: the percent of each answer (pandas "
              f"counts, as table.count_each(columns=, in_order=)); answers below the middle go left of 0, above it "
              f"right, and {middle}.")
        self._need_axes(word)
        return self._add("answer_bars", "draw", _draw_answers, columns=columns, levels=levels)
