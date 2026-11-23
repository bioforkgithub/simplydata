"""Statistics and science extras: error bars, fit lines, reference lines, shading.

These words work on the most recent data layer (ctx.last) and are drawn in the "extra"
phase, after every chart type. Methods, written so they can be stated in a paper:

* draw_error_bars: for every x value (and colour group) the mean of y, with
  "standard deviation" (sd) = sample standard deviation (n - 1), "standard error" (se) =
  sd / sqrt(n), "confidence interval" (ci) = 95 % confidence interval of the mean from the
  t distribution (_stats.t_interval).
  Empty cells are skipped. An x value with a single y value gets no bar.
  With colour groups sharing an x value, each group's bars, line and dots are shifted
  sideways together (ggplot2's position_dodge), spread over 15 % of the smallest x gap
  (15 % of 1 for categories); dodge=False keeps the true x.
* fit_line: ordinary least squares, scipy.stats.linregress; R² = rvalue².
  with_confidence_band=True is the 95 % confidence band of the fitted line (of the mean of y at each x),
  from statsmodels OLS get_prediction().conf_int(), as R predict(lm, interval = "confidence").
* fit_curve: least-squares polynomial, the same statsmodels fit as table.fit_curve; R² = 1 - SSE / SST.
* draw_smooth_line: LOWESS (Cleveland 1979), statsmodels lowess(), which follows R's lowess():
  local straight-line fits with tricube weights over the nearest 2/3 of the points, then 3
  robustness iterations with bisquare weights (6 × median absolute residual), and R's
  default delta = 1 % of the x range: points closer than delta to the last fitted point are
  interpolated, not fitted. Where the points are spread out (mtcars) the curve is R
  lowess()'s to about 1e-10; with many close points statsmodels picks the points it fits
  a little differently from R, and the curve agrees with R's to about 1e-4 of the y values.
  (With delta = 0, statsmodels and R lowess(delta = 0) agree to about 1e-9, but R's default
  curve differs from that by up to 1e-3.)
* draw_side_histograms: numpy.histogram_bin_edges(with_bins="auto"), the same bins for all groups.
* sdata.draw_all_pairs: seaborn.histplot on the diagonal, or seaborn.kdeplot (Gaussian kernel,
  Scott's bandwidth) when colour= makes groups; seaborn.scatterplot elsewhere.
"""

from __future__ import annotations

from .._typing import _Same

import datetime as _dt
import math

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import rcParams
from matplotlib.collections import PathCollection
from matplotlib.colors import is_color_like, to_rgba
from matplotlib.figure import Figure
from scipy import stats

from .. import _style
from .._core import PHASES, BaseChart
from .._data import is_listlike
from .._errors import SimplydataError, column_error, friendly
from .._stats import ERROR_LONG, error_code, say_error, t_interval
from ..table.between import MIN_SMOOTHING_POINTS
from ._helpers import check_thickness, colour_role, default_colour, palette_for
from .look import LookWords
from .text import TextWords

try:  # the order seaborn gives to groups, so our colours match the dots
    from seaborn._base import categorical_order as _sns_order
except ImportError:  # pragma: no cover
    _sns_order = None

# Chart types that make a data layer. Used to spot a wrong layer at call time.
_CHART_KINDS = {
    "bars", "lines", "dots", "area", "histogram", "boxes", "violins", "heatmap", "pie",
    "polar", "contour", "surface", "dots_3d", "density", "count_bars", "all_dots",
    "qq_dots", "cumulative_share", "sticks", "autocorrelation_bars", "cross_correlation_bars", "lag_dots",
    "trend_and_season", "spectrum", "spectrum_over_time",
}
_EXAMPLE = {
    "dots": 'chart.draw_dots(x="hours", y="marks")',
    "lines": 'chart.draw_lines(x="month", y="temperature")',
}


# ====================================================================== calculations
def group_errors(table, x, y, group=None, kind="sd") -> pd.DataFrame:
    """Mean and error half-width of y for every x value (and colour group).

    Returns columns x, group (if any), mean, n, half. Empty cells in y are skipped.
    half is NaN for groups with fewer than 2 values.
    """
    keys = [x] + ([group] if group else [])
    df = table[keys + [y]].dropna(subset=[y])
    rows = []
    for key, part in df.groupby(keys, sort=False, dropna=True):
        v = part[y].to_numpy(dtype=float)
        n = len(v)
        mean = v.mean()
        if n < 2:
            half = np.nan
        elif kind == "sd":
            half = v.std(ddof=1)
        elif kind == "se":
            half = v.std(ddof=1) / math.sqrt(n)
        else:  # "ci"
            low, high = t_interval(v)
            half = (high - low) / 2
        key = key if isinstance(key, tuple) else (key,)
        rows.append(dict(zip(keys, key), mean=mean, n=n, half=half))
    return pd.DataFrame(rows, columns=keys + ["mean", "n", "half"])


def linear_fit(x, y) -> dict:
    """Straight line by least squares (scipy.stats.linregress); with 3 or more points also the
    statsmodels OLS fit that the confidence band needs."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    res = stats.linregress(x, y)
    fit = dict(slope=res.slope, intercept=res.intercept, r2=res.rvalue ** 2, n=len(x))
    if len(x) > 2:
        from statsmodels.regression.linear_model import OLS

        fit["ols"] = OLS(y, np.column_stack([np.ones(len(x)), x])).fit()
    return fit


def line_band(fit: dict, xs):
    """95 % confidence band of the fitted line at xs (statsmodels get_prediction): (low, high). Needs n >= 3."""
    xs = np.asarray(xs, dtype=float)
    band = fit["ols"].get_prediction(np.column_stack([np.ones(len(xs)), xs])).conf_int(alpha=0.05)
    return band[:, 0], band[:, 1]


def poly_fit(x, y, degree: int) -> dict:
    """Least-squares polynomial, the same fit as table.fit_curve (statsmodels). coefs are highest power first."""
    from ..table.fitting import fit_curve_core

    fit = fit_curve_core(x, y, degree)
    return dict(coefs=fit["beta"][::-1], r2=fit["r2"], n=fit["n"])


def lowess(x, y, frac: float = 2 / 3, iterations: int = 3, delta: float = 0.0):
    """LOWESS smoother (Cleveland 1979) from statsmodels, the algorithm of R lowess().

    Returns (x_sorted, fitted) with x sorted ascending. frac is the share of points in
    each local fit, iterations the number of robustness steps, delta the distance within
    which points are interpolated instead of fitted (0 = fit every point).
    """
    from statsmodels.nonparametric.smoothers_lowess import lowess as sm_lowess

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    order = np.argsort(x, kind="stable")
    x, y = x[order], y[order]
    if len(x) < 2:
        return x, y.copy()
    fitted = sm_lowess(y, x, frac=frac, it=iterations, delta=delta, is_sorted=True, return_sorted=False)
    return x, np.asarray(fitted, dtype=float)


# ====================================================================== text helpers
_SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_MINUS = "−"


def nice_number(v: float) -> str:
    """About 3 significant figures, without scientific notation for everyday sizes."""
    if v == 0:
        return "0"
    if not np.isfinite(v):
        return str(v)
    a = abs(v)
    if a >= 1e6 or a < 1e-3:
        text = f"{a:.3g}"
    else:
        digits = max(0, 2 - math.floor(math.log10(a)))
        text = f"{a:.{digits}f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
    return (_MINUS if v < 0 else "") + text


def equation_text(coefs, r2) -> str:
    """'y = 2.31x + 0.48, R² = 0.94' from coefficients, highest power first."""
    degree = len(coefs) - 1
    parts = []
    for k, c in enumerate(coefs):
        power = degree - k
        num = nice_number(abs(c))
        if power == 0:
            term = num
        else:
            term = ("" if num == "1" else num) + "x" + (str(power).translate(_SUPERSCRIPT) if power > 1 else "")
        if not parts:
            parts.append((_MINUS if c < 0 else "") + term)
        else:
            parts.append((f" {_MINUS} " if c < 0 else " + ") + term)
    r2_text = f"{r2:.2f}" if np.isfinite(r2) else "?"
    return "y = " + "".join(parts) + f", R² = {r2_text}"


def _write_equation(ctx, text, colour):
    """Equations stack in the top-left corner, one line each."""
    count = ctx.store.get("equations", 0)
    ctx.store["equations"] = count + 1
    size = rcParams["legend.fontsize"]
    ctx.ax.annotate(text, xy=(0.02, 0.98), xycoords="axes fraction",
                    xytext=(0, -count * 1.6 * size), textcoords="offset points",
                    ha="left", va="top", color=colour, fontsize=size, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=rcParams["axes.facecolor"],
                              edgecolor="none", alpha=0.75))


# ====================================================================== layer helpers
def _wrong_layer(word, kinds, found):
    names = " or ".join(sorted(kinds))
    example = _EXAMPLE[sorted(kinds)[0]]
    if found is None:
        return SimplydataError(f".{word}() works on {names}, but your chart has none yet.\n"
                               f"Add one first, for example {example}")
    return SimplydataError(f".{word}() works on {names}, but the last chart type is {found}.\n"
                           f"Use it after {example}")


def _layer(ctx, word, kinds):
    """The data layer this word works on, or a friendly error."""
    last = ctx.last
    if not last or last.get("kind") not in kinds:
        raise _wrong_layer(word, kinds, last.get("kind") if last else None)
    return last


def _groups(ctx, table, group, fixed=None):
    """Yield (name, part of table, colour) for every colour group, matching the dots' colours."""
    if group is None:
        yield None, table, fixed or rcParams["text.color"]
        return
    if _sns_order is not None:
        levels = _sns_order(table[group])
    else:  # pragma: no cover
        levels = list(pd.unique(table[group].dropna()))
    colours = palette_for(table, group, ctx.settings)
    for level, colour in zip(levels, colours):
        yield level, table[table[group] == level], fixed or colour


def _kind_of(series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "dates"
    if pd.api.types.is_bool_dtype(series):
        return "True/False values"
    return "words (text)"


def _is_number_column(series) -> bool:
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def _numeric_xy(word, table, x, y):
    """x and y as float arrays with empty cells skipped; friendly error if not numbers."""
    for role, col in (("x", x), ("y", y)):
        if not _is_number_column(table[col]):
            raise SimplydataError(f'.{word}() needs numbers on {role}, but "{col}" holds {_kind_of(table[col])}.')
    part = table[[x, y]].dropna()
    return part[x].to_numpy(dtype=float), part[y].to_numpy(dtype=float)


def _fixed_colour(word, colour):
    if colour is not None and not (isinstance(colour, str) and is_color_like(colour)):
        raise SimplydataError(
            f'.{word}() does not know the colour "{colour}".\n'
            'Use a colour name such as "red", "blue" or "grey", or a code such as "#0072B2".'
        )


# draw_smooth_line(method=): the plain names first, other spellings accepted
SMOOTH_METHODS = {"lowess": "lowess", "loess": "loess", "local regression": "loess", "spline": "spline",
                  "smoothing spline": "spline", "smooth.spline": "spline"}


# ====================================================================== drawing
def _not_average_error(show):
    return SimplydataError(
        f'.draw_error_bars() shows spread around the average, but your lines show the {show}.\n'
        'Use chart.draw_lines(..., show="average") with error bars.'
    )


def _draw_error_bars(ctx, kind, column, dodge=True):
    last = _layer(ctx, "error_bars", {"dots", "lines"})
    table, x, y, group = last["table"], last["x"], last["y"], last["colour"]
    ax = ctx.ax
    style = dict(capsize=4, elinewidth=1.5, capthick=1.5, zorder=3)
    bars = []  # one entry per colour group: level, colour, x values, centres, half-widths

    if column is not None:
        if is_listlike(column):
            if len(column) != len(table):
                raise SimplydataError(
                    f"draw_error_bars(column=...) got {len(column)} error sizes, but the chart has {len(table)} points."
                )
            values, name = pd.Series(list(column), index=table.index), "your list"
        else:
            if column not in table.columns:
                raise column_error(column, table.columns)
            values, name = table[column], f'"{column}"'
        if not _is_number_column(values):
            raise SimplydataError(f".draw_error_bars() needs numbers in {name} for the size of each error bar.")
        if (values < 0).any():
            raise SimplydataError(f".draw_error_bars(): error sizes cannot be below 0, but {name} has negative values.")
        keys = [x] + ([group] if group else [])
        if last["kind"] == "lines" and table.duplicated(subset=keys).any():
            raise SimplydataError(
                "Your lines join several rows per x value, so one error size per row does not fit.\n"
                'Use chart.draw_error_bars("standard deviation") to work out the spread instead, or use one row '
                "per x value."
            )
        data = table.assign(_err=values.to_numpy())
        for level, part, colour in _groups(ctx, data, group):
            part = part.dropna(subset=[y, "_err"])
            bars.append(dict(level=level, colour=colour, x=part[x].to_list(),
                             mid=part[y].to_numpy(dtype=float), half=part["_err"].to_numpy(dtype=float)))
        fmt = "none"
    else:
        if last.get("show", "average") not in ("average", "mean"):
            raise _not_average_error(last["show"])
        if not _is_number_column(table[y]):
            raise SimplydataError(f'.draw_error_bars() needs numbers on y, but "{y}" holds {_kind_of(table[y])}.')
        summary = group_errors(table, x, y, group, kind)
        if summary["half"].isna().all():
            raise SimplydataError(
                f'.draw_error_bars("{ERROR_LONG[kind]}") needs at least 2 values for an x value, but every x has only one.\n'
                'If your table has its own error sizes, use chart.draw_error_bars(column="your error column").'
            )
        for level, part, colour in _groups(ctx, summary, group):
            part = part.dropna(subset=["half"])
            bars.append(dict(level=level, colour=colour, x=part[x].to_list(),
                             mid=part["mean"].to_numpy(dtype=float), half=part["half"].to_numpy(dtype=float)))
        fmt = "_" if last["kind"] == "dots" else "none"  # on dots, also mark the average

    positions = [list(b["x"]) for b in bars]
    if dodge and group is not None:
        shifted = _dodge(ax, last, bars)
        if shifted is not None:
            positions = shifted
    for b, xs in zip(bars, positions):
        if len(b["mid"]):
            ax.errorbar(xs, b["mid"], yerr=b["half"], fmt=fmt, color=b["colour"], ecolor=b["colour"],
                        markersize=16, markeredgewidth=2, **style)


# ---------------------------------------------------------------- dodging grouped error bars
DODGE_SPREAD = 0.15  # the groups spread over 15 % of the smallest gap between x values


def _to_numbers(ax, values) -> np.ndarray:
    """x values as the numbers matplotlib uses on the axis (categories 0, 1, 2 ...; dates in days)."""
    if len(values) == 0:
        return np.array([], dtype=float)
    return np.asarray(ax.xaxis.convert_units(list(values)), dtype=float)


def dodge_offsets(n_groups: int, gap: float) -> np.ndarray:
    """Sideways shift for each group, in legend order, centred on the true x (ggplot2 position_dodge)."""
    if n_groups < 2:
        return np.zeros(n_groups)
    spread = DODGE_SPREAD * gap
    return (np.arange(n_groups) - (n_groups - 1) / 2) * spread / (n_groups - 1)


def _same_rgb(a, b) -> bool:
    return np.allclose(to_rgba(a)[:3], to_rgba(b)[:3], atol=1e-3)


def _same_x(a, b) -> bool:
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    return len(a) == len(b) and np.allclose(a, b)


def _dodge(ax, last, bars):
    """Shift each group's error bars, line and dots sideways by the same amount.

    Returns the new x positions per group, or None when nothing should move: no x value
    is shared by 2 groups, or a group's own line/dots cannot be found for certain (then the
    bars stay on the true x rather than come loose from their points).
    """
    table, x, y, group = last["table"], last["x"], last["y"], last["colour"]
    numbers = [_to_numbers(ax, b["x"]) for b in bars]
    owners = {}
    for i, xs in enumerate(numbers):
        for v in np.unique(xs):
            owners.setdefault(v, set()).add(i)
    if not any(len(o) > 1 for o in owners.values()):
        return None
    if _is_number_column(table[x]) or pd.api.types.is_datetime64_any_dtype(table[x]):
        distinct = np.unique(np.concatenate(numbers))
        if len(distinct) < 2:
            return None
        gap = float(np.diff(distinct).min())
    else:  # categories sit 1 apart
        gap = 1.0
    offsets = dodge_offsets(len(bars), gap)

    # find every group's own artists first; move nothing unless all are found
    moves = []
    points = table.dropna(subset=[x, y])
    for b in bars:
        part = points[points[group] == b["level"]]
        own_x = _to_numbers(ax, part[x].to_list())
        if last["kind"] == "lines":
            found = [ln for ln in ax.lines
                     if len(ln.get_xdata()) and _same_rgb(ln.get_color(), b["colour"])
                     and _same_x(ln.convert_xunits(ln.get_xdata()), np.unique(own_x))]
            if len(found) != 1:
                return None
            moves.append(("line", found[0]))
        else:
            hits = []
            for coll in ax.collections:
                if not isinstance(coll, PathCollection):
                    continue
                offs = np.asarray(coll.get_offsets())
                faces = coll.get_facecolors()
                if len(offs) == 0 or len(faces) != len(offs):
                    continue
                mask = np.array([_same_rgb(f, b["colour"]) for f in faces])
                if mask.any() and _same_x(offs[mask, 0], own_x):
                    hits.append((coll, mask))
            if len(hits) != 1:
                return None
            moves.append(("dots", hits[0]))
    for (what, target), off in zip(moves, offsets):
        if what == "line":
            target.set_xdata(np.asarray(target.convert_xunits(target.get_xdata()), dtype=float) + off)
        else:
            coll, mask = target
            offs = np.array(coll.get_offsets(), dtype=float)
            offs[mask, 0] += off
            coll.set_offsets(offs)
    return [xs + off for xs, off in zip(numbers, offsets)]


def _draw_fit(ctx, word, how, colour, show_equation, band=False, degree=1, thickness=None, smoothness="auto"):
    last = _layer(ctx, word, {"dots"})
    table, x, y, group = last["table"], last["x"], last["y"], last["colour"]
    _numeric_xy(word, table, x, y)
    ax = ctx.ax
    drawn = 0
    need = {"line": 2, "curve": degree + 1, "smooth": 3, "spline": MIN_SMOOTHING_POINTS}[how]
    for name, part, col in _groups(ctx, table, group, colour):
        xv, yv = _numeric_xy(word, part, x, y)
        if len(np.unique(xv)) < need:
            continue
        xs = np.linspace(xv.min(), xv.max(), 200)  # only over the x range of the data
        if how == "line":
            fit = linear_fit(xv, yv)
            ax.plot(xs, fit["intercept"] + fit["slope"] * xs, color=col, zorder=3, linewidth=thickness)
            if band and "ols" in fit:
                low, high = line_band(fit, xs)
                ax.fill_between(xs, low, high, color=col, alpha=0.2, linewidth=0, zorder=2.5)
            coefs, r2 = [fit["slope"], fit["intercept"]], fit["r2"]
        elif how == "curve":
            fit = poly_fit(xv, yv, degree)
            ax.plot(xs, np.polyval(fit["coefs"], xs), color=col, zorder=3, linewidth=thickness)
            coefs, r2 = fit["coefs"], fit["r2"]
        elif how == "spline":
            from ..table.between import smoothing_spline

            ax.plot(xs, smoothing_spline(xv, yv, smoothness)(xs), color=col, zorder=3, linewidth=thickness)
        else:
            xs, ys = lowess(xv, yv, delta=0.01 * np.ptp(xv))  # R lowess()'s default delta
            ax.plot(xs, ys, color=col, zorder=3, linewidth=thickness)
        drawn += 1
        if show_equation and how not in ("smooth", "spline"):
            text = equation_text(coefs, r2)
            _write_equation(ctx, text if name is None else f"{name}: {text}", col)
    if not drawn:
        raise SimplydataError(
            f".{word}() needs dots at {need} or more different x values"
            + (" in at least one colour group." if group else ".")
        )


def _draw_fit_line(ctx, band, show_equation, colour, thickness=None):
    _draw_fit(ctx, "fit_line", "line", colour, show_equation, band=band, thickness=thickness)


def _draw_fit_curve(ctx, degree, show_equation, colour, thickness=None):
    _draw_fit(ctx, "fit_curve", "curve", colour, show_equation, degree=degree, thickness=thickness)


def _draw_smooth_line(ctx, colour, thickness=None, method="lowess", smoothness="auto", window=5, ends=None,
                      options=None):
    if method in ("lowess", "spline"):
        how = "spline" if method == "spline" else "smooth"
        _draw_fit(ctx, "smooth_line", how, colour, False, thickness=thickness, smoothness=smoothness)
        return
    from .. import _smoothing

    last = _layer(ctx, "smooth_line", {"dots", "lines"})
    table, x, y, group = last["table"], last["x"], last["y"], last["colour"]
    _numeric_xy("draw_smooth_line", table, x, y)
    for _, part, col in _groups(ctx, table, group, colour):
        xv, yv = _numeric_xy("draw_smooth_line", part, x, y)
        order = np.argsort(xv, kind="stable")
        xv, yv = xv[order], yv[order]
        steps = np.diff(xv)
        if len(xv) < 3 or steps[0] <= 0 or not np.allclose(steps, steps[0], rtol=1e-6, atol=0):
            raise SimplydataError(f'chart.draw_smooth_line(test_method="{method}") needs evenly spaced x values, one dot per '
                                  'step (a window counts readings). For uneven x use test_method="lowess" or "spline".')
        got = _smoothing.smooth(yv, method, window, ends, step_name="smooth_line", **(options or {}))
        ctx.ax.plot(xv, got.values, color=col, zorder=3, linewidth=thickness)


def _draw_loess(ctx, colour, thickness=None, span=0.75, band=False):
    """R stats::loess(degree = 2) through each colour group's dots, over 200 points of its x range, with the 95 %
    confidence band of predict(se = TRUE) when band=True."""
    from ..table.lines_r import loess

    last = _layer(ctx, "smooth_line", {"dots"})
    table, x, y, group = last["table"], last["x"], last["y"], last["colour"]
    _numeric_xy("draw_smooth_line", table, x, y)
    drawn = 0
    for _, part, col in _groups(ctx, table, group, colour):
        xv, yv = _numeric_xy("draw_smooth_line", part, x, y)
        if len(np.unique(xv)) < 5:
            continue
        xs = np.linspace(xv.min(), xv.max(), 200)
        got = loess(xv, yv, span, xs)
        ctx.ax.plot(xs, np.asarray(got["fit"], dtype=float), color=col, zorder=3, linewidth=thickness)
        if band:
            ctx.ax.fill_between(xs, np.asarray(got["low"], dtype=float), np.asarray(got["high"], dtype=float),
                                color=col, alpha=0.2, linewidth=0, zorder=2.5)
        drawn += 1
    if not drawn:
        raise SimplydataError('.draw_smooth_line(test_method="loess") needs dots at 5 or more different x values'
                              + (" in at least one colour group." if group else "."))


def _draw_dose_response(ctx, kind, colour, thickness=None):
    """R drc::drm() through each colour group's dots, drawn over 300 doses from the smallest to the largest
    (spaced evenly on a log scale, plus dose 0 when there is one); the ED50 and its interval in the legend."""
    from ..table.lines_r import dose_response_curve
    from ..table.lines_more import DOSE_VALUES, _ci, _num

    last = _layer(ctx, "fit_dose_response", {"dots"})
    table, x, y, group = last["table"], last["x"], last["y"], last["colour"]
    _numeric_xy("fit_dose_response", table, x, y)
    drawn = 0
    for name, part, col in _groups(ctx, table, group, colour):
        xv, yv = _numeric_xy("fit_dose_response", part, x, y)
        if len(np.unique(xv)) < DOSE_VALUES[kind] + 1:
            continue
        if np.any(xv < 0):
            raise SimplydataError(f'.fit_dose_response() needs doses of 0 or more; "{x}" has negative values.')
        positive = xv[xv > 0]
        xs = np.geomspace(positive.min(), xv.max(), 300) if len(positive) else np.linspace(0, xv.max(), 300)
        if np.any(xv == 0):
            xs = np.concatenate([[0.0], xs])
        got = dose_response_curve(xv, yv, kind, xs)
        ed = (float(np.atleast_1d(got[k])[0]) for k in ("ed50", "ed50_low", "ed50_high"))
        est, low, high = ed
        label = f"ED50 {_num(est)} ({_ci(low, high)})"
        ctx.ax.plot(xs, np.asarray(got["fitted"], dtype=float), color=col, zorder=3, linewidth=thickness,
                    label=label if name is None else f"{name}: {label}")
        drawn += 1
    if not drawn:
        raise SimplydataError(f".fit_dose_response() needs dots at {DOSE_VALUES[kind] + 1} or more different doses"
                              + (" in at least one colour group." if group else "."))
    ctx.ax.legend(fontsize="small")


def _draw_side_histograms(ctx):
    last = _layer(ctx, "side_histograms", {"dots"})
    table, x, y, group = last["table"], last["x"], last["y"], last["colour"]
    _numeric_xy("draw_side_histograms", table, x, y)
    ax = ctx.ax
    top = ax.inset_axes([0, 1.02, 1, 0.18], sharex=ax)
    right = ax.inset_axes([1.02, 0, 0.18, 1], sharey=ax)
    edges = {}
    for col in (x, y):
        values = table[col].dropna().to_numpy(dtype=float)
        e = np.histogram_bin_edges(values, bins="auto")
        edges[col] = e if len(e) <= 51 else np.histogram_bin_edges(values, bins=50)
    many = group is not None
    fixed = None if many else default_colour(ctx.settings)
    for _, part, colour in _groups(ctx, table, group, fixed):
        if many:  # outlines, so overlapping groups stay readable
            kw = dict(color=colour, histtype="step", linewidth=1.5)
        else:
            kw = dict(color=colour, alpha=0.8, histtype="stepfilled", linewidth=0)
        top.hist(part[x].dropna().to_numpy(dtype=float), bins=edges[x], **kw)
        right.hist(part[y].dropna().to_numpy(dtype=float), bins=edges[y], orientation="horizontal", **kw)
    for side in (top, right):
        side.grid(False)
        for spine in side.spines.values():
            spine.set_visible(False)
    top.tick_params(labelbottom=False, bottom=False, left=False, labelleft=False)
    right.tick_params(labelleft=False, left=False, bottom=False, labelbottom=False)


def _draw_line_at(ctx, axis, value, dashed, colour, label, thickness=None):
    ax = ctx.ax
    style = dict(color=colour, linestyle="--" if dashed else "-",
                 linewidth=1.5 if thickness is None else thickness, zorder=2.5)
    size = rcParams["legend.fontsize"]
    back = dict(boxstyle="round,pad=0.15", fc=rcParams["axes.facecolor"], ec="none", alpha=0.85)
    if axis == "x":
        ax.axvline(value, **style)
        if label:
            ax.text(value, 0.98, f" {label} ", transform=ax.get_xaxis_transform(), rotation=90,
                    ha="right", va="top", color=colour, fontsize=size, bbox=back)
    else:
        ax.axhline(value, **style)
        if label:
            # just outside the right edge, so it never sits on top of bars or dots
            ax.text(1.01, value, label, transform=ax.get_yaxis_transform(),
                    ha="left", va="center", color=colour, fontsize=size, clip_on=False)


def _draw_line_with_slope(ctx, slope, through, dashed, colour, label, thickness=None):
    ax = ctx.ax
    if ax.get_xscale() != "linear" or ax.get_yscale() != "linear":
        raise SimplydataError(
            ".draw_line_with_slope() draws a straight line, which is only straight on ordinary axes, "
            "not on a log scale.\nLeave out .use_log_scale_x() / .use_log_scale_y(), or draw the line on a chart without them.")
    line = ax.axline(through, slope=slope, color=colour, linestyle="--" if dashed else "-",
                     linewidth=1.5 if thickness is None else thickness, zorder=2.5)
    if label:
        entries = ctx.store.setdefault("slope_lines", [])
        entries.append((line, label))


def _slope_legend(ctx):
    """Put labelled slope lines in the legend (after every chart type, so lines cannot replace it)."""
    entries = ctx.store.pop("slope_lines", [])
    if not entries:
        return
    ax = ctx.ax
    old = ax.get_legend()
    handles, labels, title = [], [], None
    if old is not None:
        handles = list(old.legend_handles)
        labels = [t.get_text() for t in old.get_texts()]
        title = old.get_title().get_text() or None
        old.remove()
    for handle, text in entries:
        handles.append(handle)
        labels.append(text)
    ax.legend(handles, labels, title=title)


def _draw_shade(ctx, axis, low, high, colour):
    span = ctx.ax.axvspan if axis == "x" else ctx.ax.axhspan
    span(low, high, color=colour, alpha=0.2, linewidth=0, zorder=0)


def _check_position(word, option, value, example):
    ok = not isinstance(value, bool) and isinstance(
        value, (int, float, np.integer, np.floating, _dt.date, np.datetime64))
    if ok and isinstance(value, (float, np.floating)) and not np.isfinite(value):
        ok = False
    if not ok:
        raise SimplydataError(f".{word}() needs a number for {option}=, not {value!r}.\nFor example chart.{example}")


# ====================================================================== words
class StatsWords:
    def _check_layer_now(self, word, kinds, numeric=True):
        """Report a wrong layer on the user's own line when it can already be seen.

        If no chart type has been added yet that is fine: steps may come in any order,
        and the check is made again when the chart is drawn.
        """
        draws = [s for s in self._steps if s.phase == PHASES["draw"] and s.name in _CHART_KINDS]
        if not draws:
            return None
        step = draws[-1]
        if step.name not in kinds:
            raise _wrong_layer(word, kinds, step.name)
        if numeric and len(self._data.columns):
            for role in ("x", "y"):
                col = step.kwargs.get(role)
                if isinstance(col, str) and col in self._data.columns and not _is_number_column(self._data[col]):
                    raise SimplydataError(
                        f'.{word}() needs numbers on {role}, but "{col}" holds {_kind_of(self._data[col])}.')
        return step

    @friendly(renamed={"kind": "of_kind"})
    def draw_error_bars(self: _Same, of_kind="standard deviation", column=None, dodge=True) -> _Same:
        """Error bars on dots or lines. chart.draw_error_bars("standard error")

        For every x value the bar shows the average of y and how sure or spread it is:
        "standard deviation" (n - 1): how spread out the values are around the average;
        "standard error": how sure we are about the average itself;
        "confidence interval": the 95 % range the true average is very likely in
        (t distribution). A line says which one was drawn. Empty cells are skipped.
        column="error" uses error sizes from your own column instead.
        With colour groups, bars at the same x move a little apart (with their lines and
        dots) so they do not hide each other; dodge=False keeps them on the true x.
        """
        of_kind = error_code("draw_error_bars", of_kind, option="kind")
        if column is not None and not is_listlike(column):
            if not isinstance(column, str):
                raise SimplydataError('column= should be the name of a column, for example column="error".')
            if len(self._data.columns) and column not in self._data.columns:
                raise column_error(column, self._data.columns)
        step = self._check_layer_now("draw_error_bars", {"dots", "lines"}, numeric=False)
        if step is not None and step.name == "lines" and column is None:
            show = step.kwargs.get("show", "average")
            if show not in ("average", "mean"):
                raise _not_average_error(show)
        if column is None:
            say_error(of_kind)
        return self._add("error_bars", "extra", _draw_error_bars, kind=of_kind, column=column,
                         dodge=bool(dodge))

    @friendly(renamed={"band": "with_confidence_band", "confidence_band": "with_confidence_band"})
    def fit_line(self: _Same, with_confidence_band=False, show_equation=False, colour=None, thickness=None) -> _Same:
        """A straight line that fits the dots best (linear regression). chart.fit_line()

        The line is found by least squares: it makes the squared distances from the dots
        to the line as small as possible.
        with_confidence_band=True shades the 95 % confidence band: where the true line very
        likely is.
        show_equation=True writes the equation and R² on the chart.
        Each colour group gets its own line. colour="red" makes every line red.
        thickness=3 draws a thicker line (normal is 2).
        """
        _fixed_colour("fit_line", colour)
        thickness = check_thickness("fit_line", thickness)
        self._check_layer_now("fit_line", {"dots"})
        return self._add("fit_line", "extra", _draw_fit_line, band=bool(with_confidence_band),
                         show_equation=bool(show_equation), colour=colour, thickness=thickness)

    @friendly(renamed={"degree": "of_degree"})
    def fit_curve(self: _Same, of_degree=2, show_equation=False, colour=None, thickness=None) -> _Same:
        """A curve that fits the dots best. chart.fit_curve(of_degree=2)

        of_degree=2 is a curve with one bend (x²), of_degree=3 can bend twice (x³), and so on.
        show_equation=True writes the equation and R² on the chart.
        thickness=3 draws a thicker curve (normal is 2).
        """
        thickness = check_thickness("fit_curve", thickness)
        if isinstance(of_degree, bool) or not isinstance(of_degree, (int, np.integer)) or not 1 <= of_degree <= 10:
            raise SimplydataError(
                f"of_degree= should be a whole number from 1 to 10, not {of_degree!r}.\n"
                "For example chart.fit_curve(of_degree=2) for a curve with one bend."
            )
        _fixed_colour("fit_curve", colour)
        self._check_layer_now("fit_curve", {"dots"})
        return self._add("fit_curve", "extra", _draw_fit_curve, degree=int(of_degree),
                         show_equation=bool(show_equation), colour=colour, thickness=thickness)

    @friendly
    def fit_dose_response(self: _Same, of_kind=None, colour=None, thickness=None) -> _Same:
        """A dose-response curve through the dots, with its ED50 in the legend. chart.fit_dose_response()

        The same curve as table.fit_dose_response(): a 4 parameter log-logistic curve by R
        drc::drm() (needs R with drc), with the ED50 and its 95 % interval (delta method) in the
        legend. of_kind= "3 parameter log-logistic", "5 parameter log-logistic" or "weibull".
        Each colour group gets its own curve, fitted to that group alone (table.fit_dose_response(...,
        for_each_group_in=) fits all groups in one model, so its intervals can differ a little).
        Add .use_log_scale_x() for a log dose axis (dots at dose 0 then fall off the axis).
        """
        from ..table.lines_more import read_dose_kind

        kind = read_dose_kind(of_kind, "numbers")
        thickness = check_thickness("fit_dose_response", thickness)
        _fixed_colour("fit_dose_response", colour)
        self._check_layer_now("fit_dose_response", {"dots"})
        return self._add("fit_dose_response", "extra", _draw_dose_response, kind=kind, colour=colour,
                         thickness=thickness)

    @friendly(renamed={"method": "test_method", "degree": "of_degree"})
    def draw_smooth_line(self: _Same, colour=None, thickness=None, test_method="lowess", smoothness="auto", window=5, ends=None,
                         weights=None, of_degree=None, newest_weight=None, width=None, with_confidence_band=False) -> _Same:
        """A smooth line that follows the dots (LOWESS). chart.draw_smooth_line()

        Good for seeing a trend that is not straight. Each colour group gets its own line.
        LOWESS as R lowess() with its defaults (the nearest 2/3 of the dots, 3 robustness steps,
        delta = 1 % of the x range), from statsmodels lowess().
        thickness=3 draws a thicker line (normal is 2).
        test_method="spline" draws a smoothing spline instead (as table.values_at(...,
        smoothness=) and R smooth.spline()): smoothness="auto" lets R choose how smooth by
        generalised cross-validation, which needs R (pip install "simplydata[r]"); a number
        is R's lambda= (bigger is smoother) and needs no R.
        The smoothing methods of nums.smooth work too, on dots or lines with evenly spaced x:
        "moving average" (window=, weights=, ends=), "median" (needs R), "savitzky-golay"
        (of_degree=), "exponential" (newest_weight=), "gaussian" (width=), "whittaker" (smoothness=)
        and "wiener". The line goes through the x values of the dots, as table.add_smoothed_column.
        test_method="loess" draws R stats::loess() itself (needs R): local curves of degree 2 through the
        nearest smoothness=0.75 of the dots, without robustness steps (lowess fits local straight
        lines with 3 robustness steps, so the two lines differ); with_confidence_band=True shades
        its 95 % confidence band (R predict(se = TRUE)).
        """
        from .. import _smoothing
        from .._errors import choice_error

        _fixed_colour("smooth_line", colour)
        thickness = check_thickness("draw_smooth_line", thickness)
        if not isinstance(with_confidence_band, bool):
            raise SimplydataError("with_confidence_band= is True or False.")
        key = test_method.strip().lower() if isinstance(test_method, str) else test_method
        if key in SMOOTH_METHODS:
            test_method = SMOOTH_METHODS[key]
        else:
            try:
                test_method = _smoothing.read_method(test_method, "smooth_line")
            except SimplydataError:
                raise choice_error("draw_smooth_line", "test_method", test_method, list(_smoothing.METHODS)) from None
        options = {k: v for k, v in (("weights", weights), ("of_degree", of_degree), ("newest_weight", newest_weight),
                                     ("width", width)) if v is not None}
        if with_confidence_band and test_method != "loess":
            raise SimplydataError(f'with_confidence_band=True goes with test_method="loess" (R loess gives the band), not '
                                  f'"{test_method}".\nFor example chart.draw_smooth_line(test_method="loess", '
                                  "with_confidence_band=True)")
        if test_method == "loess":
            if options or ends is not None or window != 5:
                raise SimplydataError('window=, ends=, weights=, of_degree=, newest_weight= and width= go with the '
                                      'window methods, not with test_method="loess".')
            span = _smoothing.loess_span(smoothness, "draw_smooth_line")
            self._check_layer_now("draw_smooth_line", {"dots"})
            return self._add("smooth_line", "extra", _draw_loess, colour=colour, thickness=thickness, span=span,
                             band=with_confidence_band)
        if test_method not in ("lowess", "spline"):
            if test_method == "whittaker" and smoothness != "auto":
                options["smoothness"] = smoothness
            allowed = _smoothing.OPTIONS.get(test_method, set())
            extra = sorted(k for k in options if k not in allowed)
            if extra:
                raise SimplydataError(f'draw_smooth_line(test_method="{test_method}") does not take {extra[0]}=.')
            if test_method in _smoothing.WINDOW_METHODS and weights is None:
                _smoothing._odd_window(window, "smooth_line", test_method)
            self._check_layer_now("draw_smooth_line", {"dots", "lines"})
            return self._add("smooth_line", "extra", _draw_smooth_line, colour=colour, thickness=thickness,
                             method=test_method, window=window, ends=ends, options=options)
        if options or ends is not None or window != 5:
            raise SimplydataError(f'window=, ends=, weights=, of_degree=, newest_weight= and width= go with the window '
                                  f'methods (such as test_method="moving average"), not with test_method="{test_method}".')
        from ..table.between import smoothness_choice

        smoothness = smoothness_choice("smooth_line", smoothness)
        if test_method == "lowess" and smoothness != "auto":
            raise SimplydataError('smoothness= a number goes with test_method="spline" (a smoothing spline); LOWESS '
                                  'always uses the nearest 2/3 of the dots, as R lowess().\n'
                                  'For example chart.draw_smooth_line(test_method="spline", smoothness=0.001)')
        if smoothness == 0:
            raise SimplydataError('smoothness=0 would pass through every dot; use "auto" or a number above 0, '
                                  'or chart.draw_lines(..., joined_by="smooth curve") to join the dots.')
        self._check_layer_now("draw_smooth_line", {"dots"})
        return self._add("smooth_line", "extra", _draw_smooth_line, colour=colour, thickness=thickness,
                         method=test_method, smoothness=smoothness)

    @friendly
    def draw_side_histograms(self: _Same) -> _Same:
        """Small histograms along the top and right edges of a dots chart. chart.draw_side_histograms()"""
        self._check_layer_now("draw_side_histograms", {"dots"})
        return self._add("side_histograms", "extra", _draw_side_histograms)

    @friendly(renamed={"label": "labelled"})
    def draw_line_at_x(self: _Same, value, dashed=True, colour="grey", labelled=None, thickness=None) -> _Same:
        """A straight up-and-down line at one x value. chart.draw_line_at_x(2010, labelled="2010")

        thickness=3 draws a thicker line (normal is 1.5).
        """
        _check_position("draw_line_at_x", "value", value, "draw_line_at_x(10)")
        _fixed_colour("draw_line_at_x", colour)
        thickness = check_thickness("draw_line_at_x", thickness)
        return self._add("line_at_x", "extra", _draw_line_at, axis="x", value=value, dashed=bool(dashed),
                         colour=colour, label=None if labelled is None else str(labelled), thickness=thickness)

    @friendly(renamed={"label": "labelled"})
    def draw_line_at_y(self: _Same, value, dashed=True, colour="grey", labelled=None, thickness=None) -> _Same:
        """A straight side-to-side line at one y value. chart.draw_line_at_y(50, labelled="pass mark")

        thickness=3 draws a thicker line (normal is 1.5).
        """
        _check_position("draw_line_at_y", "value", value, "draw_line_at_y(50)")
        _fixed_colour("draw_line_at_y", colour)
        thickness = check_thickness("draw_line_at_y", thickness)
        return self._add("line_at_y", "extra", _draw_line_at, axis="y", value=value, dashed=bool(dashed),
                         colour=colour, label=None if labelled is None else str(labelled), thickness=thickness)

    @friendly(renamed={"label": "labelled"})
    def draw_line_with_slope(self: _Same, slope, through=None, intercept=None, dashed=True, colour="grey", labelled=None,
                             thickness=None) -> _Same:
        """A straight line with a given slope, right across the chart. chart.draw_line_with_slope(1, through=(0, 0))

        chart.draw_line_with_slope(1, labelled="1:1") draws the 1:1 line (y = x) on a chart of
        observed against predicted values. through=(2, 10) makes the line pass through
        x = 2, y = 10 (normally through 0, 0); intercept=5 instead sets where it crosses
        x = 0, so y = intercept + slope * x. labelled= names it in the legend.
        thickness=3 draws a thicker line (normal is 1.5). Ordinary (not log) axes only.
        """
        if isinstance(slope, bool) or not isinstance(slope, (int, float, np.integer, np.floating)) \
                or not np.isfinite(slope):
            raise SimplydataError(
                f".draw_line_with_slope() needs a number for the slope, not {slope!r}.\n"
                "For example chart.draw_line_with_slope(1) for the 1:1 line (y = x).")
        if through is not None and intercept is not None:
            raise SimplydataError(
                ".draw_line_with_slope() takes through= or intercept=, not both: both say where the line goes.\n"
                "For example chart.draw_line_with_slope(2, intercept=5) or chart.draw_line_with_slope(2, through=(1, 7)).")
        if intercept is not None:
            _check_position("draw_line_with_slope", "intercept", intercept, "draw_line_with_slope(2, intercept=5)")
            through = (0, intercept)
        elif through is None:
            through = (0.0, 0.0)
        else:
            if isinstance(through, str) or not is_listlike(through) or len(through) != 2:
                raise SimplydataError(
                    f".draw_line_with_slope() needs through= as a point (x, y), such as through=(0, 0), not {through!r}.")
            for v in through:
                _check_position("draw_line_with_slope", "through", v, "draw_line_with_slope(1, through=(0, 0))")
            through = (through[0], through[1])
        _fixed_colour("draw_line_with_slope", colour)
        thickness = check_thickness("draw_line_with_slope", thickness)
        self._add("line_with_slope", "extra", _draw_line_with_slope, slope=slope, through=through,
                  dashed=bool(dashed), colour=colour, label=None if labelled is None else str(labelled),
                  thickness=thickness)
        return self._replace("slope_legend", "extra", _slope_legend)

    def _shade(self, axis, low, high, colour):
        word = f"shade_between_{axis}"
        example = f"{word}(40, 60)"
        _check_position(word, "low", low, example)
        _check_position(word, "high", high, example)
        _fixed_colour(word, colour)
        if low == high:
            raise SimplydataError(f".{word}() needs two different values, for example chart.{example}")
        if high < low:
            low, high = high, low
        return self._add(word, "extra", _draw_shade, axis=axis, low=low, high=high, colour=colour)

    @friendly
    def shade_between_x(self: _Same, low, high, colour="grey") -> _Same:
        """Shade the band between two x values, behind the data. chart.shade_between_x(6, 8)"""
        return self._shade("x", low, high, colour)

    @friendly
    def shade_between_y(self: _Same, low, high, colour="grey") -> _Same:
        """Shade the band between two y values, behind the data. chart.shade_between_y(40, 60)"""
        return self._shade("y", low, high, colour)


# ====================================================================== sdata.draw_all_pairs
class PairsChart(TextWords, LookWords, BaseChart):
    """Every number column against every other. Make one with sdata.draw_all_pairs(table)."""

    def __init__(self, data, colour=None, columns=None):
        super().__init__(data)
        table = self._data
        if not len(table.columns):
            raise SimplydataError('sdata.draw_all_pairs() needs a table, for example sdata.draw_all_pairs(sdata.get_example("marks")).')
        group, fixed = colour_role(table, colour)
        if is_listlike(group):
            raise SimplydataError('In sdata.draw_all_pairs(), colour= should be a column name, for example colour="class".')
        if columns is not None:
            if isinstance(columns, str) or not is_listlike(columns):
                raise SimplydataError('columns= should be a list of column names, for example columns=["hours", "marks"].')
            for c in columns:
                if c not in table.columns:
                    raise column_error(c, table.columns)
            chosen = list(columns)
        else:
            chosen = [c for c in table.columns if c != group]
        numbers = [c for c in chosen if _is_number_column(table[c])]
        if columns is not None and len(numbers) < len(chosen):
            bad = [str(c) for c in chosen if c not in numbers]
            raise SimplydataError("sdata.draw_all_pairs() can only use columns with numbers. Not numbers: " + ", ".join(bad))
        if len(numbers) < 2:
            raise SimplydataError(
                "sdata.draw_all_pairs() needs at least 2 columns with numbers.\n"
                f"Columns with numbers: {', '.join(map(str, numbers)) or 'none'}"
            )
        if len(numbers) > 10:
            raise SimplydataError(
                f"Your table has {len(numbers)} columns with numbers, too many for one pairs chart.\n"
                'Choose up to 10 with columns=, for example sdata.draw_all_pairs(table, columns=["hours", "marks", "height"]).'
            )
        self._columns = numbers
        self._group, self._fixed = group, fixed
        side = float(min(max(2.4 * len(numbers), 5), 12))
        self._settings.update(width=side + (1.5 if group else 0), height=side)

    def label_x(self, *args, **kwargs):
        raise SimplydataError("A pairs chart already names each column under its panels.")

    def label_y(self, *args, **kwargs):
        raise SimplydataError("A pairs chart already names each row beside its panels.")

    def __repr__(self):
        return f"<simplydata pairs chart: {', '.join(map(str, self._columns))}>"

    def _render(self) -> Figure:
        if self._cache is not None:
            return self._cache
        s = self._settings
        table, cols, group = self._data, self._columns, self._group
        k = len(cols)
        with _style.context(s):
            fig = Figure(figsize=(s["width"], s["height"]), layout="constrained")
            axes = fig.subplots(k, k, sharex="col", sharey="row", squeeze=False)
            colour_kw = (dict(hue=group, palette=palette_for(table, group, s)) if group
                         else dict(color=default_colour(s, self._fixed)))
            handles = None
            dot_size = max(8, 40 - 4 * k)
            for i, row_col in enumerate(cols):
                for j, col in enumerate(cols):
                    ax = axes[i][j]
                    if i == j:
                        # the cell keeps the row's y scale (shared); the histogram sits on a twin
                        twin = ax.twinx()
                        if group:
                            sns.kdeplot(data=table, x=col, ax=twin, fill=True, common_norm=False,
                                        warn_singular=False, legend=False, **colour_kw)
                        else:
                            sns.histplot(data=table, x=col, ax=twin, **colour_kw)
                        twin.set_ylim(bottom=0)
                        twin.set_ylabel("")
                        twin.grid(False)
                        twin.tick_params(right=False, labelright=False)
                        twin.spines["right"].set_visible(False)
                    else:
                        want_legend = group is not None and handles is None
                        sns.scatterplot(data=table, x=col, y=row_col, ax=ax, s=dot_size, linewidth=0,
                                        alpha=0.8, legend="auto" if want_legend else False, **colour_kw)
                        if want_legend and ax.get_legend() is not None:
                            handles = ax.get_legend_handles_labels()
                            ax.get_legend().remove()
                    ax.set_xlabel(str(col) if i == k - 1 else "")
                    ax.set_ylabel(str(row_col) if j == 0 else "")
            if handles:
                fig.legend(*handles, title=str(group), loc="outside right upper")
            self._draw_figure_steps(fig, list(axes.flat))
        self._cache = fig
        return fig


@friendly
def draw_all_pairs(data, colour=None, columns=None):
    """Every number column against every other. sdata.draw_all_pairs(sdata.get_example("marks"), colour="class")

    Histograms on the diagonal (density curves when colour= makes groups), dots
    everywhere else. colour="class" colours each group. columns=["hours", "marks"] chooses
    the columns. Empty cells are skipped. Then use it like any chart:
    .write_title_on_top("..."), .save("pairs.png").
    """
    return PairsChart(data, colour=colour, columns=columns)
