"""Charts for diagnostic tests, agreement and intervals: trade_off_curve, difference_dots, forest_plot.

* trade_off_curve(score="crp", truth="infected"): the ROC curve. Each cut-off of the score finds a share
  of those who have it (sensitivity, up) at the price of false alarms among those who do not (1 minus
  specificity, along). The points come from R pROC::coords(roc, "all") (simplydata[r]), the same ROC
  analysis as table.compare_to_truth; the legend gives the AUC with its DeLong interval and the best
  cut-off by Youden's index is marked. The diagonal is "no better than chance".
* difference_dots(first="device_a", second="device_b"): the Bland-Altman chart: dots and average from statsmodels
  graphics.agreement.mean_diff_plot, the limits and their intervals from R BlandAltmanLeh (statsmodels uses
  the n-divisor standard deviation for its limits, so they differ a little from R's).
* forest_plot(x="estimate", y="measure"): a dot per row with its interval as a line, from any result
  table that has "<x> 95 % CI low" and "<x> 95 % CI high" columns (risks, rates, pairs, effect sizes). A
  line marks no effect: 0, or 1 for ratios, which are drawn on a log scale (log_scale= chooses). When the
  table holds intervals of more than one level, the first level is drawn and a note says which rows were
  left out. Drawing only, no statistics.
"""

from __future__ import annotations

from .._typing import _Same

import re
import warnings

import numpy as np
import pandas as pd

from .._errors import SimplydataError, friendly
from ._helpers import check, check_thickness, check_transparency, colour_role, default_colour, opacity, palette_for
from .charts import _remember

CHANCE_LINE = "no better than chance"
WHEN = ("higher", "lower")


# ---------------------------------------------------------------- trade_off_curve
def _roc_points(truth01, score, direction, level=0.95):
    """R pROC: every (1 - specificity, sensitivity) point, the AUC with its DeLong interval and the Youden point."""
    from .._r import r_call

    found = r_call(
        "r <- pROC::roc(truth, score, levels = c(0, 1), direction = dir, quiet = TRUE); "
        "a <- pROC::ci.auc(r, method = 'delong', conf.level = level); "
        "p <- pROC::coords(r, 'all', ret = c('specificity', 'sensitivity'), transpose = FALSE); "
        "b <- pROC::coords(r, 'best', best.method = 'youden', ret = c('threshold', 'specificity', 'sensitivity'), "
        "transpose = FALSE); "
        "list(sp = p$specificity, se = p$sensitivity, auc = as.numeric(a[2]), low = as.numeric(a[1]), "
        "high = as.numeric(a[3]), cut = b$threshold[1], best_sp = b$specificity[1], best_se = b$sensitivity[1])",
        packages=("pROC",), what="the trade-off (ROC) curve (R pROC)",
        python_note="Python's stack (SciPy, statsmodels) has no ROC analysis with DeLong's interval",
        truth=truth01, score=score, dir=direction, level=level)
    out = {k: np.asarray(found[k], dtype=float) for k in ("sp", "se")}
    out.update({k: float(np.asarray(found[k], dtype=float)[0]) for k in ("auc", "low", "high", "cut", "best_sp",
                                                                         "best_se")})
    return out


def _truth01(values, truth, positive):
    from ..table.risk_words import _event_value

    has, _ = _event_value("trade_off_curve", truth, list(values), positive, what="has it")
    return np.array([v == has for v in values], dtype=float)


def _draw_trade_off(ctx, scores, truth, group, fixed, positive, positive_when, transparency=None, thickness=None):
    from ..table.stat_tests import _num

    ax = ctx.ax
    data = ctx.data
    direction = "<" if positive_when == "higher" else ">"
    curves = []
    columns = [truth] + list(scores) + ([group] if group else [])
    rows = data[columns].dropna()
    if group:
        names = list(pd.unique(rows[group]))
        colours = palette_for(rows, group, ctx.settings)
        parts = [(scores[0], str(n), c, rows[rows[group] == n]) for n, c in zip(names, colours)]
    elif len(scores) > 1:
        colours = palette_for(pd.DataFrame({"score": list(scores)}), "score", ctx.settings)
        parts = [(s, s, c, rows) for s, c in zip(scores, colours)]
    else:
        parts = [(scores[0], scores[0], default_colour(ctx.settings, fixed), rows)]
    for score, name, c, part in parts:
        points = _roc_points(_truth01(part[truth].tolist(), truth, positive),
                             pd.to_numeric(part[score]).to_numpy(dtype=float), direction)
        x, y = 1 - points["sp"], points["se"]
        order = np.lexsort((y, x))
        label = f"{name}: AUC {_num(points['auc'])} (95 % CI {_num(points['low'])} to {_num(points['high'])})"
        ax.plot(x[order], y[order], color=c, label=label, alpha=opacity(transparency), linewidth=thickness,
                drawstyle="default")
        best, = ax.plot([1 - points["best_sp"]], [points["best_se"]], marker="o", color=c, markersize=7,
                        linestyle="none")
        best.simplydata_value = points["cut"]  # chart.get_numbers_drawn() gives R's cut-off in the value column
        ax.annotate(f"cut-off {_num(points['cut'])}", (1 - points["best_sp"], points["best_se"]), xytext=(8, -12),
                    textcoords="offset points", fontsize="small", color=c)
        curves.append({"name": name, "x": x[order], "y": y[order], **{k: points[k] for k in ("auc", "low", "high",
                                                                                              "cut")}})
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", linewidth=1, label=CHANCE_LINE)
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.01)
    ax.set_aspect("equal", adjustable="box")
    if ax.get_xlabel() == "":
        ax.set_xlabel("False alarms (1 - specificity): share without it that test positive")
    if ax.get_ylabel() == "":
        ax.set_ylabel("Found (sensitivity): share with it that test positive")
    ax.legend(loc="lower right", fontsize="small")
    ctx.store.setdefault("trade_off", {})[id(ax)] = curves
    _remember(ctx, "trade_off_curve", rows, {"x": None, "y": None, "colour": group})


# ---------------------------------------------------------------- difference_dots
def _draw_difference_dots(ctx, first, second, transparency=None):
    from statsmodels.graphics.agreement import mean_diff_plot

    from .._r import r_call
    from ..table.stat_tests import _num

    x, y = first, second
    rows = ctx.data[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
    a, b = rows[x].to_numpy(dtype=float), rows[y].to_numpy(dtype=float)
    kwds = {} if transparency is None else {"alpha": opacity(transparency)}
    # the dots and the average difference from statsmodels; its limits use the standard deviation with n in the
    # divisor, so sd_limit=0 leaves them out and the limits (n - 1, as R) and their intervals come from R
    with warnings.catch_warnings():  # mean_diff_plot calls tight_layout itself; simplydata lays out the page later
        warnings.simplefilter("ignore", UserWarning)
        mean_diff_plot(a, b, ax=ctx.ax, sd_limit=0, scatter_kwds=kwds)
    found = r_call("s <- BlandAltmanLeh::bland.altman.stats(a, b); list(lower = s$lower.limit, upper = s$upper.limit, "
                   "ci = unname(s$CI.lines))", packages=("BlandAltmanLeh",),
                   what="the limits of agreement (R BlandAltmanLeh::bland.altman.stats())",
                   python_note="statsmodels mean_diff_plot draws limits from the standard deviation with n in the "
                               "divisor, which differ a little from R's", a=a, b=b)
    ci = np.asarray(found["ci"], dtype=float)
    for name, key, (low, high) in (("lower limit", "lower", ci[0:2]), ("upper limit", "upper", ci[4:6])):
        value = float(np.asarray(found[key], dtype=float)[0])
        ctx.ax.axhline(value, color="grey", linestyle="--", linewidth=1)
        ctx.ax.axhspan(low, high, color="grey", alpha=0.12, linewidth=0)
        ctx.ax.annotate(f"{name} {_num(value)}", xy=(1, value), xycoords=("axes fraction", "data"), xytext=(-4, 3),
                        textcoords="offset points", ha="right", fontsize="small")
    ctx.ax.set_xlabel(f"Average of {x} and {y}")
    ctx.ax.set_ylabel(f"{x} minus {y}")
    ctx.ax.set_title("")
    _remember(ctx, "difference_dots", rows, {"x": x, "y": y, "colour": None})


# ---------------------------------------------------------------- forest_plot
def _all_interval_columns(columns, x):
    """Every ("<x> 95 % CI low", "<x> 95 % CI high", "95 %") in the table, for any level, in column order."""
    pattern = re.compile(rf"^{re.escape(x)} (\d+(?:\.\d+)?) % CI low$")
    found = []
    for c in columns:
        m = pattern.match(str(c))
        if m and f"{x} {m.group(1)} % CI high" in columns:
            found.append((c, f"{x} {m.group(1)} % CI high", f"{m.group(1)} %"))
    return found


def _interval_columns(columns, x):
    """("<x> 95 % CI low", "<x> 95 % CI high", "95 %"): the first level found, or None."""
    found = _all_interval_columns(columns, x)
    return found[0] if found else None


def _other_level_rows(data, low, high, others):
    """True for each row whose interval is of another level (empty in low/high, given in another pair)."""
    empty = pd.to_numeric(data[low], errors="coerce").isna() & pd.to_numeric(data[high], errors="coerce").isna()
    given = pd.Series(False, index=data.index)
    for o_low, o_high, _ in others:
        given |= pd.to_numeric(data[o_low], errors="coerce").notna() | pd.to_numeric(data[o_high], errors="coerce").notna()
    return empty & given


NL = chr(10)
ON = "combined on"  # combine_studies' result: "log scale (ratios)", "plain scale" or "Fisher's z scale"
LOG_SCALE = "log scale (ratios)"
KIND = "row kind"  # combine_studies' result: "study", "combined", "combined in subgroup", "prediction interval", ...
COMBINED = ("combined", "combined in subgroup")


def _draw_forest(ctx, x, y, low, high, level, line_at, ratios, colour=None, thickness=None, others=(),
                 line_given=False, size=None):
    ax = ctx.ax
    kinds = KIND in ctx.data.columns
    extra = [c for c in ([KIND] if kinds else []) + ([size] if size else []) if c not in (y, x, low, high)]
    rows = ctx.data[[y, x, low, high] + extra + [c for o in others for c in o[:2]]].copy()
    if others:
        rows = rows[~_other_level_rows(rows, low, high, others)]
    rows = rows[[y, x, low, high] + extra]
    if kinds:
        rows = rows[rows[KIND].isin(("study",) + COMBINED + ("prediction interval",))]
    rows = rows[pd.to_numeric(rows[x], errors="coerce").notna()]
    est = pd.to_numeric(rows[x]).to_numpy(dtype=float)
    lo = pd.to_numeric(rows[low], errors="coerce").to_numpy(dtype=float)
    hi = pd.to_numeric(rows[high], errors="coerce").to_numpy(dtype=float)
    where = np.arange(len(rows))[::-1]  # the first row at the top, as in a table
    c = default_colour(ctx.settings, colour)
    if not kinds and size is None:
        ax.errorbar(est, where, xerr=[est - np.where(np.isnan(lo), est, lo), np.where(np.isnan(hi), est, hi) - est],
                    fmt="o", color=c, ecolor=c, capsize=3, elinewidth=thickness or 1.5, markersize=6)
    else:
        kind = rows[KIND].to_numpy(dtype=object) if kinds else np.array(["study"] * len(rows), dtype=object)
        study = kind == "study"
        both = ~np.isnan(lo) & ~np.isnan(hi)
        ax.hlines(where[study & both], lo[study & both], hi[study & both], color=c, linewidth=thickness or 1.5)
        if size is not None:
            weight = pd.to_numeric(rows[size], errors="coerce").to_numpy(dtype=float)
            biggest = np.nanmax(weight[study]) if np.any(study & ~np.isnan(weight)) else 1.0
            area = np.where(np.isnan(weight), 20.0, 20.0 + 180.0 * weight / biggest)  # [D] marker size only
        else:
            area = np.full(len(rows), 40.0)
        ax.scatter(est[study], where[study], s=area[study], marker="s" if kinds else "o", color=c, zorder=3)
        for i in np.flatnonzero(np.isin(kind, COMBINED) & both):
            ax.fill([lo[i], est[i], hi[i], est[i]], [where[i], where[i] + 0.3, where[i], where[i] - 0.3], color=c,
                    zorder=3)
        for i in np.flatnonzero((kind == "prediction interval") & both):
            ax.plot([lo[i], hi[i]], [where[i], where[i]], color=c, linewidth=1, linestyle="-", marker="|",
                    markersize=8)
    ax.axvline(line_at, color="grey", linestyle="--", linewidth=1)
    ax.set_yticks(where)
    ax.set_yticklabels([str(v) for v in rows[y]])
    if ratios and (kinds or size is not None):
        _plain_log_axis(ax)
    elif ratios:
        ax.set_xscale("log")
    if ax.get_xlabel() == "":
        meaning = "" if line_given else ", no effect"
        ax.set_xlabel(f"{x}, with its {level} confidence interval (the line: {line_at:g}{meaning})")
    _remember(ctx, "forest_plot", rows, {"x": x, "y": y, "colour": None})


def _plain_log_axis(ax):
    """A log x-axis whose ticks read 0.2, 0.5, 1, 2 (not 2 x 10^-1)."""
    from matplotlib import ticker

    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%g"))
    ax.xaxis.set_minor_formatter(ticker.FormatStrFormatter("%g"))


def _draw_funnel(ctx, x, y, centre, on_log, ratios, colour=None):
    from scipy import stats

    ax = ctx.ax
    rows = ctx.data[ctx.data[KIND] == "study"][[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
    est = rows[x].to_numpy(dtype=float)
    se = rows[y].to_numpy(dtype=float)
    c = default_colour(ctx.settings, colour)
    ax.scatter(est, se, color=c, s=30, zorder=3)
    top = float(np.max(se))
    # the pseudo 95 % limits: SciPy's 95 % interval around the combined effect (lognorm when the effects were combined
    # on the log scale); drawn on the axis of the same scale they are straight lines, so the ends are enough
    steps = np.array([top]) if on_log == ratios else np.linspace(top / 50, top, 50)
    if on_log:
        left, right = stats.lognorm.interval(0.95, s=steps, scale=centre)
    else:
        left, right = stats.norm.interval(0.95, loc=centre, scale=steps)
    ax.plot(np.concatenate([left[::-1], [centre], right]), np.concatenate([steps[::-1], [0.0], steps]), color="grey",
            linestyle="--", linewidth=1)
    ax.axvline(centre, color="grey", linewidth=1)
    ax.set_ylim(top * 1.05, 0.0)
    if ratios:
        _plain_log_axis(ax)
    if ax.get_xlabel() == "":
        ax.set_xlabel(x)
    if ax.get_ylabel() == "":
        ax.set_ylabel(f"{y}" + (" (of the log ratio)" if on_log else "") + ", small studies at the bottom")
    _remember(ctx, "draw_funnel_plot", rows, {"x": x, "y": y, "colour": None})


class AgreementChartWords:
    @friendly
    def trade_off_curve(self: _Same, score=None, truth=None, positive=None, colour=None, positive_when="higher",
                        transparency=None, thickness=None) -> _Same:
        """How a score trades found cases against false alarms, cut-off by cut-off (the ROC curve).
        chart.trade_off_curve(score="crp", truth="infected") (with sdata.get_example("clinic"))

        Each possible cut-off of the score gives a point: along, the share of those without it
        who test positive anyway (false alarms, 1 - specificity); up, the share of those with it
        that the test finds (sensitivity). A good score climbs steeply to the top left; the
        diagonal is no better than chance. The legend gives the AUC with its DeLong 95 %
        interval, and a dot marks the best cut-off by Youden's index. score=["crp",
        "procalcitonin"] draws one curve per score; colour="ward" one curve per group. Higher
        scores count as positive; positive_when="lower" turns it round. The numbers come from R
        pROC (simplydata[r]), the same as table.compare_to_truth.
        chart.get_numbers_drawn() gives the best cut-off as a number: in the row of the marked dot
        (kind "dot", series the curve's name) the value column holds the cut-off, y the sensitivity
        there and x the false alarms (1 - specificity), all from R pROC::coords(roc, "best",
        best.method = "youden"). The specificity is not in that table: table.compare_to_truth
        gives pROC's specificity at the same cut-off, with its sensitivity, as a result table.
        """
        from .._r import need_r

        example = 'chart.trade_off_curve(score="crp", truth="infected")'
        scores = [score] if isinstance(score, str) else list(score) if isinstance(score, (list, tuple)) else []
        if not scores or not all(isinstance(s, str) for s in scores):
            raise SimplydataError(f".trade_off_curve() needs score= as a column of numbers in quotes (or a list of "
                                  f"them).\nFor example {example} (with sdata.get_example(\"clinic\")).")
        if not isinstance(truth, str):
            raise SimplydataError(f".trade_off_curve() needs truth= as the column with the real answer.\n"
                                  f"For example {example}.")
        if positive_when not in WHEN:
            raise SimplydataError('positive_when= is "higher" (higher scores count as positive) or "lower".')
        group, fixed = colour_role(self._data, colour)
        if group is not None and len(scores) > 1:
            raise SimplydataError("Give several scores or colour= for groups, not both.")
        transparency = check_transparency("trade_off_curve", transparency)
        thickness = check_thickness("trade_off_curve", thickness)
        for s in scores:
            check(self._data, x=s, y=truth, colour=group)
            if not pd.api.types.is_numeric_dtype(self._data[s]):
                raise SimplydataError(f'.trade_off_curve() needs score= as a column of numbers; "{s}" is not.')
        _truth01(self._data[truth].dropna().tolist(), truth, positive)  # say what is wrong on the user's line
        need_r(("pROC",), "The trade-off (ROC) curve (R pROC)",
               "Python's stack (SciPy, statsmodels) has no ROC analysis with DeLong's interval")
        self._need_axes("trade_off_curve")
        return self._add("trade_off_curve", "draw", _draw_trade_off, scores=scores, truth=truth, group=group,
                         fixed=fixed, positive=positive, positive_when=positive_when, transparency=transparency,
                         thickness=thickness)

    @friendly(renamed={"x": "first", "y": "second"})
    def difference_dots(self: _Same, first=None, second=None, transparency=None) -> _Same:
        """Do two ways of measuring agree? The difference of each pair against its average (Bland-Altman).
        chart.difference_dots(first="device_a", second="device_b") (with sdata.get_example("clinic"))

        One dot per row: along, the average of the two measurements; up, first minus second. The
        names are those of table.limits_of_agreement(first, second). The solid
        line is the average difference (does one read higher?), the dashed lines the limits of
        agreement, within which 95 % of the differences lie (average plus and minus 1.96
        standard deviations), each with its 95 % interval shaded. The dots and the average come
        from statsmodels mean_diff_plot, the limits and their intervals from R
        BlandAltmanLeh::bland.altman.stats() (simplydata[r]), the same as
        table.limits_of_agreement(...).
        """
        from .._r import need_r

        example = 'chart.difference_dots(first="device_a", second="device_b")'
        x, y = first, second
        for option, value in (("first", x), ("second", y)):
            if not isinstance(value, str):
                raise SimplydataError(f".difference_dots() needs {option}= as a column of numbers in quotes.\n"
                                      f"For example {example} (with sdata.get_example(\"clinic\")).")
        if x == y:
            raise SimplydataError(f".difference_dots() needs two different columns.\nFor example {example}.")
        check(self._data, x=x, y=y)
        for c in (x, y):
            if not pd.api.types.is_numeric_dtype(self._data[c]):
                raise SimplydataError(f'.difference_dots() needs columns of numbers; "{c}" is not.')
        transparency = check_transparency("difference_dots", transparency)
        need_r(("BlandAltmanLeh",), "The limits of agreement (R BlandAltmanLeh)",
               "statsmodels mean_diff_plot draws limits from the standard deviation with n in the divisor, which "
               "differ a little from R's")
        self._need_axes("difference_dots")
        return self._add("difference_dots", "draw", _draw_difference_dots, first=x, second=y,
                         transparency=transparency)

    @friendly(renamed={"ratios": "log_scale"})
    def forest_plot(self: _Same, x="estimate", y=None, line_at=None, log_scale=None, colour=None, thickness=None, size=None) -> _Same:
        """Many results with their intervals, one line each (a forest plot).
        chart.forest_plot(x="difference", y="group 1")   (on a result table, such as compare_each_pair_of's)

        Draws each row's x as a dot and its interval as a line, from a result table with the
        columns "<x> 95 % CI low" and "<x> 95 % CI high" (any level). y names the rows. Ratios
        (x or every row label says "ratio") are drawn on a log scale with a dashed line at 1 (no
        effect), other results on a plain scale with the line at 0; log_scale=True or False and
        line_at= choose. When the table holds intervals of more than one level (such as 95 % and
        90 %), the first is drawn and a note names the rows left out. The first row is at the top.
        On the result of table.combine_studies (it has a "row kind" column) the studies are squares, the
        combined effects diamonds and the prediction interval a thin line: chart.forest_plot(x="estimate",
        y="study", size="weight %") sizes each square by the study's weight (size= as on draw_dots).
        """
        example = 'chart.forest_plot(x="estimate", y="measure")'
        if not isinstance(x, str) or not isinstance(y, str):
            raise SimplydataError(f".forest_plot() needs x= (the estimate column) and y= (the column naming the rows)."
                                  f"\nFor example {example} (on a result table).")
        check(self._data, x=x, y=y)
        found = _interval_columns(list(self._data.columns), x)
        if found is None:
            raise SimplydataError(f'.forest_plot() needs the columns "{x} 95 % CI low" and "{x} 95 % CI high" (any '
                                  "level) next to the estimate, as in the result tables of compare_risks, "
                                  "compare_each_pair and others.")
        low, high, level = found
        others = _all_interval_columns(list(self._data.columns), x)[1:]
        if others:
            left = _other_level_rows(self._data, low, high, others)
            shown = [str(v) for v in self._data.loc[left, y]]
            levels = ", ".join(o[2] for o in others)
            print(f"Note: the table holds {level} and {levels} intervals; forest_plot draws the {level} intervals"
                  + (f", and left out {len(shown)} row{'s' if len(shown) != 1 else ''} with another level: "
                     + "; ".join(f'"{s}"' for s in shown) + "." if shown else "."))
        line_given = line_at is not None
        if size is not None:
            check(self._data, size=size)
            if not pd.api.types.is_numeric_dtype(self._data[size]):
                raise SimplydataError(f'.forest_plot() needs numbers for size= (such as size="weight %"); "{size}" '
                                      "holds words or other things.")
        ratios = log_scale
        if ratios is None:
            labels = [str(v).lower() for v in self._data[y].dropna()]
            measures = []
            if ON in self._data.columns and KIND in self._data.columns:
                scales = self._data[self._data[KIND] == "study"][ON].dropna().astype(str).tolist()
                measures = ["ratio" if s == LOG_SCALE else "plain" for s in scales]
            elif "measure" in self._data.columns and KIND in self._data.columns:
                studies = self._data[self._data[KIND] == "study"]["measure"].dropna()
                measures = [str(v).lower() for v in studies]
            if measures and ON in self._data.columns:
                ratios = all(m == "ratio" for m in measures)
            else:
                ratios = ("ratio" in x.lower() or (bool(labels) and all("ratio" in v for v in labels))
                          or (bool(measures) and all("ratio" in m for m in measures)))
        if not isinstance(ratios, bool):
            raise SimplydataError("log_scale= should be True or False.")
        if line_at is None:
            line_at = 1.0 if ratios else 0.0
        if isinstance(line_at, bool) or not isinstance(line_at, (int, float)):
            raise SimplydataError("line_at= needs a number, such as line_at=0 or line_at=1.")
        thickness = check_thickness("forest_plot", thickness)
        self._need_axes("forest_plot")
        return self._add("forest_plot", "draw", _draw_forest, x=x, y=y, low=low, high=high, level=level,
                         line_at=float(line_at), ratios=ratios, colour=colour, thickness=thickness,
                         others=others, line_given=line_given, size=size)

    @friendly(renamed={"color": "colour"})
    def draw_funnel_plot(self: _Same, x="estimate", y="standard error", log_scale=None, colour=None) -> _Same:
        """A funnel plot: each study's effect against its standard error, to look for small-study effects.

        chart.draw_funnel_plot(x="estimate", y="standard error")   (on the result of table.combine_studies)
        Each dot is a study; small studies (big standard errors) are at the bottom. The solid line is
        the combined effect and the dashed funnel its pseudo 95 % limits (where 95 % of the studies
        would lie if they all measured that one effect). Dots missing from one lower corner suggest
        small-study effects: publication bias is one cause, real differences between small and large
        studies and chance are others. Ratios are drawn on a log scale (log_scale= chooses). The
        tests are in combine_studies' printout (Peters' or Egger's test, and trim and fill), from
        10 studies. Other names: funnel, funnel_plot, draw_funnel (R metafor funnel()).
        """
        example = 'chart.draw_funnel_plot(x="estimate", y="standard error")'
        data = self._data
        if KIND in data.columns and (data[KIND] == "meta-regression").any():
            raise SimplydataError(".draw_funnel_plot() needs one combined effect; a meta-regression (using=) has none. "
                                  "Combine the studies without using= first, then draw the funnel.")
        if KIND not in data.columns or not (data[KIND] == "combined").any():
            raise SimplydataError(".draw_funnel_plot() draws the result of table.combine_studies: it needs its \"row kind\" "
                                  "column and the combined row. For example:" + NL + '  result = table.combine_studies(names="trial", '
                                  "events=[...], out_of=[...])" + NL + "  chart = result.start_chart()" + NL + "  " + example)
        if not isinstance(x, str) or not isinstance(y, str):
            raise SimplydataError(f".draw_funnel_plot() needs x= (the estimate column) and y= (the standard errors)." + NL
                                  + f"For example {example}")
        check(data, x=x, y=y)
        studies_on = data[data[KIND] == "study"].get(ON, pd.Series(dtype=object)).dropna().astype(str).tolist()
        if studies_on and all(s == "Fisher's z scale" for s in studies_on):
            raise SimplydataError(".draw_funnel_plot() cannot draw correlations: their standard errors are on Fisher's z "
                                  "scale, not the scale of the correlations shown.")
        if studies_on:
            on_log = all(s == LOG_SCALE for s in studies_on)
        else:
            measures = [str(v).lower() for v in data[data[KIND] == "study"].get("measure", pd.Series(dtype=object)).dropna()]
            on_log = bool(measures) and all("ratio" in m for m in measures)
        ratios = on_log if log_scale is None else log_scale
        if not isinstance(ratios, bool):
            raise SimplydataError("log_scale= should be True or False.")
        centre = float(pd.to_numeric(data[data[KIND] == "combined"][x], errors="coerce").iloc[0])
        studies = data[data[KIND] == "study"][[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(studies) < 3:
            raise SimplydataError(".draw_funnel_plot() needs at least 3 studies with an estimate and a standard error.")
        print("Funnel plot: each dot is a study, small studies at the bottom; the line is the combined effect and the "
              "dashed funnel where 95 % of the studies would lie if they all measured it. Dots missing from one lower "
              "corner suggest small-study effects, which are not proof of publication bias.")
        self._need_axes("draw_funnel_plot")
        return self._add("draw_funnel_plot", "draw", _draw_funnel, x=x, y=y, centre=centre, on_log=on_log, ratios=ratios,
                         colour=colour)
