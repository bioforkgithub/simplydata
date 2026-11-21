"""Charts for places and extremes (S3c-3): the variogram and the threshold check.

* draw_variogram("zinc", x="east", y="north"): the semivariance of each distance bin as dots and the fitted curve,
  from R gstat (variogram, fit.variogram, variogramLine), drawn with matplotlib; the same numbers as
  table.find_variogram_of.
* draw_threshold_check(x="rain", between=[20, 40]): two panels against the threshold, to choose values_above= of
  table.find_return_levels_of. Top: the mean excess (the average amount above each threshold) with its 95 %
  interval, from R extRemes::mrlplot; above a good threshold it runs along a straight line. Bottom: the shape (xi) of
  the generalised Pareto curve fitted above each threshold, with its 95 % interval, from R
  extRemes::threshrange.plot; above a good threshold it stays level. Both R functions draw into nothing; their values
  are drawn by matplotlib.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .._errors import SimplydataError, friendly
from ._helpers import check, default_colour
from .charts import _remember

VARIOGRAM_X = "Distance (in the units of x and y)"
VARIOGRAM_Y = "Semivariance (half the average squared difference)"
CURVE_POINTS = 200


def _numbers(word, data, names):
    for name in names:
        check(data, x=name)
        if not pd.api.types.is_numeric_dtype(data[name]):
            raise SimplydataError(f'.{word}() needs numbers; "{name}" holds text.')


# ---------------------------------------------------------------- draw_variogram
def _draw_variogram(ctx, column, x, y, kind, cutoff):
    from ..table import places_r

    frame = ctx.data[[column, x, y]].apply(pd.to_numeric, errors="coerce").dropna()
    found = places_r.variogram(frame[x].to_numpy(dtype=float), frame[y].to_numpy(dtype=float),
                               frame[column].to_numpy(dtype=float), kind, cutoff, line_points=CURVE_POINTS)
    from ..table.places import variogram_problem

    problem = variogram_problem(found, kind, column, x, y)
    if problem:
        raise SimplydataError(problem)
    ax = ctx.ax
    colour = default_colour(ctx.settings)
    ax.scatter(found["dist"], found["gamma"], color=colour, zorder=3)
    if found["line_dist"] is not None:
        ax.plot(found["line_dist"], found["line_gamma"], color=colour, linewidth=1.5, zorder=2)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    if ax.get_xlabel() == "":
        ax.set_xlabel(VARIOGRAM_X)
    if ax.get_ylabel() == "":
        ax.set_ylabel(VARIOGRAM_Y)
    _remember(ctx, "draw_variogram", frame, {"x": None, "y": None, "colour": None})


# ---------------------------------------------------------------- draw_threshold_check
def _draw_threshold_check(ctx, x, low, high):
    from ..table import places_r

    values = pd.to_numeric(ctx.data[x], errors="coerce").dropna().to_numpy(dtype=float)
    found = places_r.threshold_check(values, low, high)
    ax = ctx.ax
    ax.set_axis_off()
    colour = default_colour(ctx.settings)
    top = ax.inset_axes([0, 0.56, 1, 0.42])
    bottom = ax.inset_axes([0, 0, 1, 0.42], sharex=top)
    keep = (found["mean_u"] >= low) & (found["mean_u"] <= high)
    u = found["mean_u"][keep]
    top.plot(u, found["mean"][keep], color=colour, linewidth=1.5)
    top.plot(u, found["mean_low"][keep], color="grey", linestyle="--", linewidth=1)
    top.plot(u, found["mean_high"][keep], color="grey", linestyle="--", linewidth=1)
    top.set_ylabel("Mean excess")
    top.tick_params(labelbottom=False)
    bottom.errorbar(found["shape_u"], found["shape"],
                    yerr=[found["shape"] - found["shape_low"], found["shape_high"] - found["shape"]],
                    color=colour, marker="o", linestyle="-", linewidth=1, capsize=3)
    bottom.axhline(0, color="grey", linewidth=0.8)
    bottom.set_ylabel("Shape (xi)")
    bottom.set_xlabel(f"Threshold ({x})")
    _remember(ctx, "draw_threshold_check", pd.DataFrame({x: values}), {"x": x, "y": None, "colour": None})


class PlaceChartWords:
    @friendly(others={"model": "of_kind", "kind": "of_kind", "cutoff": "between", "z": "column", "value": "column"})
    def draw_variogram(self, column=None, x=None, y=None, of_kind="spherical", between=None):
        """A variogram: how different two values are, on average, at each distance apart, as dots and a curve.

        chart.draw_variogram("zinc", x="east", y="north")   (with sdata.get_example("stations"))
        Each dot is a bin of pairs of places: their distance apart (across) and the semivariance,
        half the average squared difference of their values (up). The curve is fitted through
        the dots (of_kind="spherical", "exponential", "gaussian" or "matern"); where it levels
        off, the values are unrelated. between=[0, 1500] sets the largest distance. The numbers
        are those of table.find_variogram_of, from R gstat. Needs R (gstat).
        """
        from ..table.places import VARIOGRAM_KINDS, VARIOGRAM_SPELLINGS

        word = "draw_variogram"
        data = self._data
        example = 'chart.draw_variogram("zinc", x="east", y="north")'
        if not isinstance(column, str) or not isinstance(x, str) or not isinstance(y, str):
            raise SimplydataError(f".{word}() needs the column of values and x= and y=, the columns that say where each "
                                  f"row is.\nFor example, {example}")
        _numbers(word, data, [column, x, y])
        kind = of_kind.strip().lower() if isinstance(of_kind, str) else of_kind
        kind = VARIOGRAM_SPELLINGS.get(kind, kind)
        if kind not in VARIOGRAM_KINDS:
            raise SimplydataError(f".{word}() does not know of_kind={of_kind!r}. It takes "
                                  f"{', '.join(chr(34) + k + chr(34) for k in VARIOGRAM_KINDS)}.")
        cutoff = None
        if between is not None:
            if not isinstance(between, (list, tuple)) or len(between) != 2 or not all(
                    isinstance(b, (int, float, np.integer, np.floating)) and not isinstance(b, bool) for b in between) \
                    or between[0] != 0 or not between[1] > 0:
                raise SimplydataError(f".{word}() reads between= from 0 to the largest distance, such as "
                                      "between=[0, 1500].")
            cutoff = float(between[1])
        rows = int(data[[column, x, y]].apply(pd.to_numeric, errors="coerce").dropna().shape[0])
        if rows < 5:
            raise SimplydataError(f".{word}() needs at least 5 places with a value; there are {rows}.")
        from .._r import need_r

        need_r(("gstat", "sf"), "The variogram (R gstat)")
        print(f'Variogram of "{column}" ({rows} places): each dot is a bin of pairs of places, their distance apart and '
              f"half the average squared difference of their values (R gstat::variogram); the line is the fitted "
              f"{kind} curve (gstat::fit.variogram). Where the curve levels off, the values are unrelated. "
              f'The numbers: table.find_variogram_of("{column}", x="{x}", y="{y}").')
        self._need_axes(word)
        return self._add("variogram", "draw", _draw_variogram, column=column, x=x, y=y, kind=kind, cutoff=cutoff)

    @friendly(others={"threshold": "between", "thresholds": "between", "column": "x", "r": "between"})
    def draw_threshold_check(self, x=None, between=None):
        """The threshold check: two panels that help choose values_above= for find_return_levels_of.

        chart.draw_threshold_check(x="rain", between=[10, 30])   (with sdata.get_example("rain"))
        Top: the mean excess, the average amount by which the values pass each threshold, with
        its 95 % interval (R extRemes::mrlplot); above a good threshold it runs along a straight
        line. Bottom: the shape (xi) of the generalised Pareto curve fitted above each of 10
        thresholds, with its 95 % interval (R extRemes::threshrange.plot); above a good threshold
        it stays level. Choose the lowest threshold above which both settle, and use it as
        values_above= in table.find_return_levels_of. between= gives the lowest and highest
        thresholds to look at. Needs R (extRemes).
        Other names: mean residual life plot, mrlplot, threshrange.plot.
        """
        word = "draw_threshold_check"
        data = self._data
        example = 'chart.draw_threshold_check(x="rain", between=[10, 30])'
        if not isinstance(x, str):
            raise SimplydataError(f".{word}() needs x=, the column of values.\nFor example, {example}")
        _numbers(word, data, [x])
        if not isinstance(between, (list, tuple)) or len(between) != 2 or not all(
                isinstance(b, (int, float, np.integer, np.floating)) and not isinstance(b, bool) and math.isfinite(b)
                for b in between) or not between[0] < between[1]:
            raise SimplydataError(f".{word}() needs between= as the lowest and the highest threshold to look at, such "
                                  f"as between=[20, 40].\nFor example, {example}")
        values = pd.to_numeric(data[x], errors="coerce").dropna().to_numpy(dtype=float)
        above = int((values > float(between[1])).sum())
        if above < 10:
            raise SimplydataError(f"Only {above} values lie above {between[1]!r}, too few to fit a curve; choose a lower "
                                  "highest threshold.")
        from .._r import need_r

        need_r(("extRemes",), "The threshold check (R extRemes)")
        if values.max() - 1 < float(between[1]):  # extRemes::mrlplot stops its thresholds 1 below the largest value
            print(f"Note: the mean excess (top) stops at {values.max() - 1:g}: R extRemes::mrlplot draws thresholds only "
                  "up to 1 below the largest value, so on values with a small range (such as metres) the top panel is "
                  "short or empty. The shape panel (bottom) covers every threshold asked for.")
        print(f'Threshold check of "{x}" from {between[0]:g} to {between[1]:g}: the mean excess (top, R '
              "extRemes::mrlplot) and the shape of the generalised Pareto curve (bottom, R "
              "extRemes::threshrange.plot), each with its 95 % interval. Choose the lowest threshold above which the "
              "top runs along a straight line and the bottom stays level, then use it as values_above= in "
              "table.find_return_levels_of. A higher threshold leaves fewer values, so the intervals widen.")
        self._need_axes(word)
        return self._add("threshold_check", "draw", _draw_threshold_check, x=x, low=float(between[0]),
                         high=float(between[1]))
