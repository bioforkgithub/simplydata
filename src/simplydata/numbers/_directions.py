"""Directions of a block of numbers: their names, how a shape is said in words, and how two blocks line up.

Bookkeeping only (names, sizes, sentences). Every calculation on the numbers is a NumPy call (or an xarray call,
when the extra simplydata[xarray] is installed and both blocks have named directions); nothing is worked out here.

Default names: the last two directions are "row" and "column", the third from the end "page" and the fourth from
the end "book" (approved by Manish 2026-11-25); further directions are "direction a", "direction b" ...; a block
with one direction has "number". A name the user gives (directions_named=, add_direction, an xarray DataArray) is a
real name: two blocks whose directions all have real names line up by name; otherwise they line up as NumPy does,
from the right.
"""

from __future__ import annotations

import string

import numpy as np

from .._errors import SimplydataError

# sdata.hide_stretching_notes() / show_stretching_notes() (P48): the notes printed when numbers are used again
SETTINGS = {"stretching_notes": True}

TAIL = ["book", "page", "row", "column"]


def _letter(i: int) -> str:
    letters = string.ascii_lowercase
    return letters[i] if i < 26 else letters[i // 26 - 1] + letters[i % 26]


def default_names(ndim: int) -> list[str]:
    """The names a block gets when none are given: [..., "book", "page", "row", "column"]."""
    if ndim == 0:
        return []
    if ndim == 1:
        return ["number"]
    if ndim <= 4:
        return TAIL[-ndim:]
    return [f"direction {_letter(i)}" for i in range(ndim - 4)] + TAIL


def plural(name: str) -> str:
    """row -> rows, species -> species, day -> days, study -> studies."""
    if name.endswith("s"):
        return name
    if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
        return name[:-1] + "ies"
    if name.endswith(("x", "ch", "sh")):
        return name + "es"
    return name + "s"


def say_size(n: int, name: str) -> str:
    """24 pages, 1 row, 5 in direction a, 4 in y (a one-letter name is not made plural)."""
    if name.startswith("direction ") or len(name) == 1:
        return f"{n} in {name}"
    return f"{n} {name if n == 1 else plural(name)}"


def say_shape(shape, names) -> str:
    """24 pages x 8 rows x 12 columns (a block with no directions: one number)."""
    if len(shape) == 0:
        return "one number"
    between = " by " if "x" in names else " x "  # a direction called x would read "1 in x x 4 in y"
    return between.join(say_size(int(n), name) for n, name in zip(shape, names))


def numpy_shape(shape) -> str:
    shape = tuple(int(n) for n in shape)
    return str(shape)


def check_names(names, ndim: int, step: str, example: str) -> list[str]:
    """Names given by the user: one text per direction, all different."""
    if isinstance(names, str) or not isinstance(names, (list, tuple)):
        raise SimplydataError(f"directions_named= needs a list of names in quotes, one for each direction.\n"
                              f"For example:  {example}")
    names = list(names)
    if len(names) != ndim:
        raise SimplydataError(f"directions_named= has {len(names)} names, but the numbers have {ndim} directions. "
                              f"Give one name for each.\nFor example:  {example}")
    for name in names:
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f"Each direction name is a word in quotes, such as \"hour\" (you gave {name!r}).\n"
                                  f"For example:  {example}")
    if len(set(names)) != len(names):
        twice = next(n for n in names if names.count(n) > 1)
        raise SimplydataError(f'The direction name "{twice}" is given twice; each direction needs its own name.\n'
                              f"For example:  {example}")
    return [n.strip() for n in names]


# ---------------------------------------------------------------------- lining up two blocks
def xarray_or_none():
    """xarray when the extra simplydata[xarray] is installed, else None."""
    try:
        import xarray
    except ImportError:
        return None
    return xarray


# A switch for the tests: "auto" uses xarray for named blocks when installed; "numpy" always uses NumPy
UNDERNEATH = {"named": "auto"}


class LinedUp:
    """Two sides of a sum, lined up: a and b broadcast against each other by NumPy in the sum itself."""

    def __init__(self, a, b, names, named, how, numpy_call):
        self.a = a
        self.b = b
        self.names = names  # the names of the result's directions
        self.named = named
        self.how = how  # "by name" or "from the right"
        self.numpy_call = numpy_call  # what NumPy (or xarray) did to line them up, for the sentence
        self.a_kept = list(names)  # by name: the names each side really spans (a direction of size 1 that is
        self.b_kept = list(names)  # used again along the other's size is not one of them)


def clash_message(a_shape, a_names, b_shape, b_names, step, owner="block", by_name=False) -> SimplydataError:
    """NP-L5: at most 5 lines; the first in plain words; both shapes lined up from the right; the fixes do not change
    the other numbers in place."""
    first = f"Cannot combine {say_shape(a_shape, a_names)} with {say_shape(b_shape, b_names)}."
    if by_name:
        sizes = dict(zip(a_names, a_shape))
        bad = next((n for n, s in zip(b_names, b_shape) if n in sizes and sizes[n] != s and 1 not in (s, sizes[n])),
                   None)
        lines = [first, f"Directions line up by name: {bad} is {sizes.get(bad)} in one and "
                        f"{dict(zip(b_names, b_shape)).get(bad)} in the other (each name needs the same size, or 1)."]
        lines.append(f"See how they line up:  {owner}.show_how_it_lines_up_with(other)")
        return SimplydataError("\n".join(lines))
    width = max(len(a_shape), len(b_shape))
    a_cells = [""] * (width - len(a_shape)) + [say_size(int(n), m) for n, m in zip(a_shape, a_names)]
    b_cells = [""] * (width - len(b_shape)) + [say_size(int(n), m) for n, m in zip(b_shape, b_names)]
    col = [max(len(x), len(y)) for x, y in zip(a_cells, b_cells)]
    top = "   ".join(x.rjust(w) for x, w in zip(a_cells, col))
    bottom = "   ".join(y.rjust(w) for y, w in zip(b_cells, col))
    worst = next(i for i in range(width - 1, -1, -1)
                 if a_cells[i] and b_cells[i]
                 and a_shape[i - (width - len(a_shape))] != b_shape[i - (width - len(b_shape))]
                 and 1 not in (a_shape[i - (width - len(a_shape))], b_shape[i - (width - len(b_shape))]))
    need = a_shape[worst - (width - len(a_shape))]
    lines = [first, "Shapes line up from the right:  " + top,
             "                                " + bottom + f"   <- needs {int(need)}, or 1"]
    fix = None
    if len(b_shape) == 1:
        fit = [m for n, m in zip(a_shape, a_names) if n == b_shape[0]]
        if fit:
            fix = f'For one number per {fit[0]}:  {owner}.{step}(other, over="{fit[0]}")'
    lines.append(fix or f"See how they line up:  {owner}.show_how_it_lines_up_with(other)")
    lines.append("NumPy calls lining up broadcasting; the shapes clash, so nothing was worked out.")
    return SimplydataError("\n".join(lines[:5]))


def line_up(a, a_names, a_named, b, b_names, b_named, *, over_axes=None, step="add", owner="block",
            by_name=None) -> LinedUp:
    """Line b up with a: by name when both have real names for every direction, else from the right (NumPy).

    over_axes: the directions of a that b's directions belong to (over="row"): b gets directions of size 1
    elsewhere (np.expand_dims), so that it is used again along them.
    """
    a = np.asarray(a)
    b = np.asarray(b)
    if b.ndim == 0:
        return LinedUp(a, b, list(a_names), list(a_named), "one number", "")
    if over_axes is not None:
        over_axes = list(over_axes)
        if b.ndim != len(over_axes):
            said = ", ".join(a_names[i] for i in over_axes)
            raise SimplydataError(f"over= names {len(over_axes)} direction(s) ({said}), but the other numbers have "
                                  f"{b.ndim} direction(s) ({say_shape(b.shape, b_names)}).")
        for axis, size in zip(over_axes, b.shape):
            if size not in (1, a.shape[axis]):
                raise SimplydataError(
                    f"The other numbers have {size} along {a_names[axis]}, but this {owner} has "
                    f"{say_size(a.shape[axis], a_names[axis])}: one number for each is needed (or 1).")
        order = [int(i) for i in np.argsort(over_axes)]
        moved = np.transpose(b, order) if b.ndim > 1 else b
        others = [i for i in range(a.ndim) if i not in over_axes]
        b2 = np.expand_dims(moved, axis=tuple(others)) if others else moved
        call = f"np.expand_dims(other, axis={tuple(others) if len(others) != 1 else others[0]})"
        return LinedUp(a, b2, list(a_names), list(a_named), f"over {', '.join(a_names[i] for i in over_axes)}", call)
    if by_name is None:
        by_name = all(a_named) and all(b_named) and a.ndim > 0
    if by_name:
        return _line_up_by_name(a, a_names, b, b_names, step, owner)
    try:
        shape = np.broadcast_shapes(a.shape, b.shape)
    except ValueError:
        raise clash_message(a.shape, a_names, b.shape, b_names, step, owner) from None
    extra = len(shape) - a.ndim
    if extra > 0:
        lead = list(b_names[:extra]) if len(b_names) == b.ndim and b.ndim == len(shape) else default_names(len(shape))[:extra]
        lead_named = list(b_named[:extra]) if len(b_named) == b.ndim and b.ndim == len(shape) else [False] * extra
        names, named = lead + list(a_names), lead_named + list(a_named)
    else:
        names, named = list(a_names), list(a_named)
    return LinedUp(a, b, names, named, "from the right",
                   f"np.broadcast_shapes({numpy_shape(a.shape)}, {numpy_shape(b.shape)})")


def _line_up_by_name(a, a_names, b, b_names, step, owner) -> LinedUp:
    """P05: line up by name. Each name must have the same size on both sides, or size 1 on one of them; a name only one
    side has, or has with size 1, is used again along the other's size. The result keeps a's order, with b's other
    names in front (as NumPy puts new directions in front). Both paths (xarray and NumPy) first take away a direction
    of size 1 that meets a bigger one (np.squeeze), so they agree: xarray itself refuses two sizes for one name."""
    sizes_a = dict(zip(a_names, a.shape))
    sizes_b = dict(zip(b_names, b.shape))
    squeeze_a, squeeze_b = [], []
    for name, size in sizes_b.items():
        if name in sizes_a and sizes_a[name] != size:
            if size == 1:
                squeeze_b.append(list(b_names).index(name))
            elif sizes_a[name] == 1:
                squeeze_a.append(list(a_names).index(name))
            else:
                raise clash_message(a.shape, a_names, b.shape, b_names, step, owner, by_name=True)
    order = [n for n in b_names if n not in sizes_a] + list(a_names)
    if squeeze_a:
        a = np.squeeze(a, axis=tuple(squeeze_a))
        a_names = [n for i, n in enumerate(a_names) if i not in squeeze_a]
    if squeeze_b:
        b = np.squeeze(b, axis=tuple(squeeze_b))
        b_names = [n for i, n in enumerate(b_names) if i not in squeeze_b]
    xr = xarray_or_none() if UNDERNEATH["named"] == "auto" else None
    if xr is not None:
        # xarray lines up by name itself (xr.broadcast), then the directions are put in the result's order
        a_full, b_full = xr.broadcast(xr.DataArray(a, dims=list(a_names)), xr.DataArray(b, dims=list(b_names)))
        a2 = a_full.transpose(*order).values
        b2 = b_full.transpose(*order).values
        call = "xarray.broadcast(a, b) on the direction names"
    else:
        a2 = _to_order(a, a_names, order)
        b2 = _to_order(b, b_names, order)
        call = "np.expand_dims and np.transpose, chosen from the direction names"
    lined = LinedUp(a2, b2, order, [True] * len(order), "by name", call)
    lined.a_kept, lined.b_kept = list(a_names), list(b_names)
    return lined


def _to_order(values, names, order):
    """The NumPy calls that put values in the order of names, with size-1 directions for the names it lacks."""
    missing = [i for i, n in enumerate(order) if n not in names]
    present = [n for n in order if n in names]
    moved = np.transpose(values, [list(names).index(n) for n in present]) if values.ndim > 1 else values
    return np.expand_dims(moved, axis=tuple(missing)) if missing else moved


def stretched_along(own_shape, own_names_full, result_shape, result_names) -> list[str]:
    """The directions along which one side was used again: it had size 1 there, or did not have it."""
    out = []
    offset = len(result_shape) - len(own_shape)
    for i, (size, name) in enumerate(zip(result_shape, result_names)):
        j = i - offset
        if size != 1 and (j < 0 or own_shape[j] == 1):
            out.append(say_size(int(size), name))
    return out
