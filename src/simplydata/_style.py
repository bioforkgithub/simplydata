"""The looks a chart can have. "paper" is the default."""

from __future__ import annotations

from contextlib import contextmanager

import matplotlib

# Okabe-Ito colours: safe for people with colour blindness and clear in print.
COLOURS = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]

_BASE = {
    "axes.prop_cycle": matplotlib.cycler(color=COLOURS),
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.5,
    "legend.frameon": False,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 13,
    "axes.labelweight": "bold",
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "lines.linewidth": 2.0,
    "lines.markersize": 7,
    "image.cmap": "viridis",
    # Fonts kept as real text in saved files (decision D6, 2026-11-25): TrueType (Type 42) inside .pdf and .eps,
    # which journal checkers accept (they refuse matplotlib's own Type 3), and text that stays text in .svg
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
}

STYLES = {
    "paper": {},
    "school": {
        "font.size": 15,
        "axes.titlesize": 18,
        "axes.labelsize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "legend.fontsize": 14,
        "lines.linewidth": 3.0,
        "lines.markersize": 10,
        "axes.linewidth": 1.5,
    },
    "presentation": {
        "font.size": 16,
        "axes.titlesize": 20,
        "axes.labelsize": 18,
        "xtick.labelsize": 15,
        "ytick.labelsize": 15,
        "legend.fontsize": 15,
        "lines.linewidth": 3.0,
    },
    "dark": {
        "figure.facecolor": "#1e1e1e",
        "axes.facecolor": "#1e1e1e",
        "savefig.facecolor": "#1e1e1e",
        "axes.edgecolor": "#dddddd",
        "axes.labelcolor": "#eeeeee",
        "text.color": "#eeeeee",
        "xtick.color": "#dddddd",
        "ytick.color": "#dddddd",
        "grid.color": "#555555",
        "axes.prop_cycle": matplotlib.cycler(
            color=["#56B4E9", "#E69F00", "#009E73", "#F0E442", "#CC79A7", "#D55E00", "#0072B2", "#FFFFFF"]
        ),
    },
    # For print in black and white (charts phase, batch 1): greys between about 25 % and 75 % lightness, so that
    # no fill is black and no line nearly white, with black edges round fills. The groups also differ in a second
    # way, set while drawing (simplydata.words.second_cues): patterns in black or white (whichever shows) on bars,
    # boxes, violins, areas and pies, dashes on lines and density curves, shapes on dots; colour maps (heat maps,
    # contour maps, surfaces) run in greys
    "black and white": {
        "axes.prop_cycle": matplotlib.cycler(
            color=["#404040", "#bfbfbf", "#808080", "#5a5a5a", "#a6a6a6", "#737373"]
        ),
        "patch.edgecolor": "black",
        "image.cmap": "Greys",
        "hatch.linewidth": 0.8,
    },
}

_FONT_KEYS = ("font.size", "axes.titlesize", "axes.labelsize", "xtick.labelsize", "ytick.labelsize", "legend.fontsize")


def rc_for(settings: dict) -> dict:
    rc = dict(_BASE)
    rc.update(STYLES[settings.get("style", "paper")])
    size = settings.get("font_size")
    if size:
        scale = size / rc["font.size"]
        for key in _FONT_KEYS:
            rc[key] = rc[key] * scale
    if settings.get("title_size"):  # use_font_size(title=) (charts phase, batch 2)
        rc["axes.titlesize"] = settings["title_size"]
    if settings.get("ticks_size"):  # use_font_size(ticks=)
        rc["xtick.labelsize"] = rc["ytick.labelsize"] = settings["ticks_size"]
    if settings.get("font_name"):
        rc["font.family"] = settings["font_name"]
    if settings.get("grid") is False:
        rc["axes.grid"] = False
    elif settings.get("grid") is True:
        rc["axes.grid"] = True
        rc["axes.grid.axis"] = "both"
    return rc


@contextmanager
def context(settings: dict):
    with matplotlib.rc_context(rc_for(settings)), colour_letters(settings.get("colour_letters")):
        yield


@contextmanager
def colour_letters(palette):
    """use_style(colour_letters=): seaborn set_color_codes while this chart is drawn; matplotlib's own letters come
    back afterwards, so other charts keep them (set_color_codes itself changes them for the whole session)."""
    if palette is None:
        yield
        return
    import matplotlib.colors as mcolors
    import seaborn as sns

    kept = {code: mcolors.colorConverter.colors[code] for code in "bgrmyck"}
    try:
        sns.set_color_codes(palette)
        yield
    finally:
        mcolors.colorConverter.colors.update(kept)
        mcolors.colorConverter.cache.clear()


def letters_as_codes(settings: dict) -> dict:
    """The chart's settings with the one-letter colours of use_colour and use_colours written as the colour codes
    seaborn set_color_codes gives them (so a picture saved later keeps them)."""
    import matplotlib.colors as mcolors

    out = dict(settings)
    with colour_letters(settings["colour_letters"]):
        def code(c):
            return mcolors.to_hex(c) if isinstance(c, str) and len(c) == 1 and c in "bgrmyck" else c

        if out.get("colour") is not None:
            out["colour"] = code(out["colour"])
        if out.get("colours"):
            out["colours"] = [code(c) for c in out["colours"]]
    return out


def palette(settings: dict | None = None) -> list:
    """The colour set for the chart's style ("dark" has its own brighter set)."""
    style = STYLES.get((settings or {}).get("style", "paper"), {})
    cycle = style.get("axes.prop_cycle", _BASE["axes.prop_cycle"])
    return list(cycle.by_key()["color"])
