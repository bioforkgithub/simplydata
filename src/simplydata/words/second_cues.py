"""Second cues besides colour: patterns on bars and areas, hollow dots, dashed and dotted lines, dot shapes.

Charts phase, batch 1 (approved by Manish 2026-11-25). A chart printed in black and white, or read by someone who
does not see some colours, still tells its groups apart when each group also has its own pattern, dash or shape.
Everything here is matplotlib's own (Patch.set_hatch, facecolors="none", seaborn's style= with dashes= and
markers=); simplydata only says which group gets which.

    chart.draw_bars(x="class", y="marks", colour="subject", hatched=True)
    chart.draw_dots(x="hours", y="marks", colour="class", hollow=True)
    chart.draw_lines(x="month", y="temperature", colour="city", dashed="city")
    chart.use_shapes("circle", "square", "triangle")
    chart.use_style("black and white")      greys, with patterns, dashes and shapes for the groups
"""

from __future__ import annotations

import matplotlib as mpl

from .._errors import SimplydataError, choice_error, friendly
from .._typing import _Same

# One pattern for each group, in order (matplotlib hatch codes): lines one way, the other way, crossed lines,
# dots, plus signs, small circles, flat lines, upright lines, stars, big circles
HATCHES = ["//", "\\\\", "xx", "..", "++", "oo", "--", "||", "**", "OO"]

# Dot shapes by name, and matplotlib's marker code for each
SHAPES = {"circle": "o", "square": "s", "triangle": "^", "diamond": "D", "triangle down": "v",
          "triangle left": "<", "triangle right": ">", "plus": "P", "cross": "X", "star": "*", "hexagon": "h",
          "pentagon": "p"}

# The style for print in black and white; the other ways people write it mean the same
BLACK_AND_WHITE = "black and white"
BLACK_AND_WHITE_NAMES = {"black and white", "black-and-white", "black & white", "greyscale", "grayscale", "grey",
                         "gray", "grey scale", "gray scale"}


def style_name(name):
    """ "greyscale" and the other ways of writing it are the style "black and white"."""
    if isinstance(name, str) and name.strip().lower() in BLACK_AND_WHITE_NAMES:
        return BLACK_AND_WHITE
    return name


def in_black_and_white(ctx) -> bool:
    return ctx.settings.get("style") == BLACK_AND_WHITE


def check_switch(word, option, value):
    if not isinstance(value, bool):
        raise SimplydataError(f".{word}() needs {option}=True or {option}=False, not {value!r}.")


def _pattern_colour():
    return mpl.rcParams["text.color"]


def hatch(patch, pattern):
    """Fill a bar, a slice or an area with a pattern, drawn in the text colour so it shows on any fill."""
    patch.set_hatch(pattern)
    if hasattr(patch, "set_hatchcolor"):  # matplotlib 3.11 and later; before it the pattern is black anyway
        patch.set_hatchcolor(_pattern_colour())


def _same_colour(a, b) -> bool:
    from matplotlib.colors import to_rgb

    try:
        return all(abs(x - y) < 1e-3 for x, y in zip(to_rgb(a), to_rgb(b)))
    except (TypeError, ValueError):
        return False


def _face(artist):
    import numpy as np

    face = artist.get_facecolor()
    array = np.asarray(face, dtype=float)
    return array[0] if array.ndim == 2 and len(array) else array


def _legend_patterns(ax, groups):
    """Give the legend's boxes the pattern of the group with the same colour. groups: [(colour, pattern)]."""
    legend = ax.get_legend()
    if legend is None:
        return
    for handle in getattr(legend, "legend_handles", []):
        if handle is None or not hasattr(handle, "set_hatch"):
            continue
        for colour, pattern in groups:
            if _same_colour(_face(handle), colour):
                hatch(handle, pattern)
                break


def hatch_bars(ax, before):
    """Each set of bars drawn since `before` (one BarContainer per group) gets its own pattern."""
    from matplotlib.container import BarContainer

    containers = [c for c in ax.containers if isinstance(c, BarContainer) and c not in before]
    groups = []
    for i, container in enumerate(containers):
        pattern = HATCHES[i % len(HATCHES)]
        for patch in container.patches:
            hatch(patch, pattern)
        if container.patches:
            groups.append((_face(container.patches[0]), pattern))
    _legend_patterns(ax, groups)


def hatch_collections(ax, before):
    """Each filled area drawn since `before` gets its own pattern (stackplot, fill_between)."""
    from matplotlib.collections import PolyCollection

    areas = [c for c in ax.collections if isinstance(c, PolyCollection) and c not in before]
    groups = []
    for i, area in enumerate(areas):
        pattern = HATCHES[i % len(HATCHES)]
        hatch(area, pattern)
        groups.append((_face(area), pattern))
    return groups


def area_legend_with_patterns(ax, groups, title):
    """An area chart's legend shows lines; with patterns it shows each area's colour and pattern instead."""
    from matplotlib.patches import Patch

    legend = ax.get_legend()
    if legend is None:
        return
    labels = [t.get_text() for t in legend.get_texts()]
    handles = []
    for (colour, pattern), _label in zip(groups, labels):
        box = Patch(facecolor=colour, edgecolor=colour)
        hatch(box, pattern)
        handles.append(box)
    ax.legend(handles, labels[:len(handles)], title=title)


def hatch_slices(patches):
    """Each slice of a pie gets its own pattern."""
    for i, patch in enumerate(patches):
        hatch(patch, HATCHES[i % len(HATCHES)])


def make_hollow(ax, before):
    """Dots drawn since `before` keep only their outline, in their own colour (facecolors="none")."""
    import numpy as np

    for coll in [c for c in ax.collections if c not in before and c.__class__.__name__ == "PathCollection"]:
        if coll.get_array() is not None:
            coll.update_scalarmappable()
        faces = np.asarray(coll.get_facecolors(), dtype=float)
        if len(faces):
            coll.set_edgecolors(faces)
            coll.set_facecolors("none")
            coll.set_linewidths(1.5)
    legend = ax.get_legend()
    for handle in getattr(legend, "legend_handles", []) if legend is not None else []:
        if handle is None:
            continue
        if hasattr(handle, "set_markerfacecolor"):  # a Line2D marker
            face = handle.get_markerfacecolor()
            if face not in ("none", None):
                handle.set_markeredgecolor(face)
                handle.set_markerfacecolor("none")
        elif hasattr(handle, "get_facecolors"):
            faces = handle.get_facecolors()
            if len(faces):
                handle.set_edgecolors(faces)
                handle.set_facecolors("none")


def shape_codes(names) -> list:
    """matplotlib's marker codes for the shapes chart.use_shapes() named."""
    return [SHAPES[n] for n in names]


def markers_for(settings, how_many):
    """The dot shapes for how_many groups: the ones use_shapes() named (repeated if there are more groups), else
    None (seaborn's own)."""
    names = settings.get("shapes")
    if not names:
        return None
    codes = shape_codes(names)
    return [codes[i % len(codes)] for i in range(how_many)]


class SecondCueWords:
    @friendly
    def use_shapes(self: _Same, *names) -> _Same:
        """Your own shapes for the dots of each group, in order. chart.use_shapes("circle", "square", "triangle")
        (with chart.draw_dots(x="hours", y="marks", colour="class") on sdata.get_example("marks"))

        Each group of dots (colour= or shape= on draw_dots) gets the next shape, so groups differ in two ways:
        colour and shape, which helps readers who do not see some colours and charts printed in black and
        white. Shapes: "circle", "square", "triangle", "diamond", "triangle down", "triangle left",
        "triangle right", "plus", "cross", "star", "hexagon", "pentagon". Without groups all dots get the
        first shape.
        """
        if len(names) == 1 and isinstance(names[0], (list, tuple)):
            names = tuple(names[0])
        if not names:
            raise SimplydataError('.use_shapes() needs at least one shape, for example chart.use_shapes("circle", '
                                  '"square", "triangle").')
        written = []
        for name in names:
            plain = name.strip().lower() if isinstance(name, str) else name
            if plain not in SHAPES:
                raise choice_error("use_shapes", "shape", name, list(SHAPES))
            written.append(plain)
        return self._set(shapes=written)
