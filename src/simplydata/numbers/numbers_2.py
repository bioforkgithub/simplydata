"""The NumPy + SciPy phase, batch 2 (approved by Manish 2026-11-25, with every recommendation of section 8).

* blocks with labels: get_labels_of, add_labels_to (P47), find_values_at (P27), get_numbers_nearest_to (P28),
  turn_into_change_from_average (P29, with from_years= for a reference period: decision 8, the name scored at build
  time), change_size_to (P32, block version), and the summaries' in_each="month" / every="month" (P26) and
  in_groups_of= (P46), worked out in block_summary_by_time_or_groups below
* smooth(over=[...]) on grids and blocks (P30)
* numbers: make_random_picks (P10), take_log_odds and turn_into_chances (P24)
* sdata.count_ways_to_choose and sdata.count_ways_to_order (P23)

Every calculation is one call of the package underneath, named in the sentence each word prints: xarray (groupby,
resample, sel), pandas (Index.get_indexer for the nearest label), SciPy (interpolate.interpn, ndimage filters and
zoom, special.comb, perm, logit, expit) or NumPy (Generator.choice, nanmean, reshape). The rules of the blocks hold
here too: directions are found by NAME; labels move with their numbers; labels are never left out without a note.
"""

from __future__ import annotations

from .._typing import _Same

import numbers as _nb
from typing import TYPE_CHECKING

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from ._base import amount, check_seed, is_number, note_empty, plain, say, to_array
from ._directions import plural, say_shape, say_size

if TYPE_CHECKING:
    from ..table import Table
    from .numbers import Numbers

INSTALL = 'pip install "simplydata[xarray]"'

# in_each= a part of the dates (P26): the name -> xarray's datetime accessor
TIME_PARTS = {"hour": "hour", "day of year": "dayofyear", "month": "month", "quarter": "quarter", "season": "season",
              "year": "year"}
# every= a time step (P26), the same steps as the table words' every=: the name -> pandas frequency (weeks start on
# Monday, as table.find_average_of(every="week"))
EVERY_STEPS = {"hour": "h", "day": "D", "week": "W-MON", "month": "MS", "quarter": "QS", "year": "YS"}
# the xarray reduction of each summary
XARRAY_SUMMARY = {"average": "mean", "median": "median", "total": "sum", "smallest": "min", "biggest": "max",
                  "standard_deviation": "std", "percentile": "quantile"}
# change_size_to / rotate(by_degrees=): test_method= -> the spline order of SciPy ndimage (the grid versions alike)
ZOOM_ORDERS = {"nearest": 0, "linear": 1, "cubic": 3}
SMOOTH_METHODS = ("moving average", "gaussian", "median")


def _xarray(step: str):
    try:
        import xarray
    except ImportError:
        raise SimplydataError(f"{step} works with dates and labels through xarray, the optional extra.\n"
                              f"Install it with:  {INSTALL}") from None
    return xarray


def to_xarray(block, step: str):
    """The block as an xarray DataArray: its names as dims, its labels as coordinates."""
    xr = _xarray(step)
    coords = {n: np.asarray(lab) for n, lab in block._labels.items() if n in block._names}
    return xr.DataArray(block._values, dims=list(block._names), coords=coords)


def from_xarray(da, rename=None):
    """(values, names, labels) of an xarray result, with dims renamed (dayofyear -> day of year)."""
    rename = rename or {}
    names = [rename.get(str(d), str(d)) for d in da.dims]
    labels = {}
    for d, n in zip(da.dims, names):
        if d in da.coords and da.coords[d].ndim == 1:
            labels[n] = np.asarray(da.coords[d].values)
    return np.asarray(da.values), names, labels


def _dates_direction(block, step: str, over=None) -> str:
    """The direction whose labels are dates (P26): over= names it, or the block has exactly one."""
    dated = [n for n in block._names if n in block._labels and np.asarray(block._labels[n]).dtype.kind == "M"]
    if over is not None:
        names = over if isinstance(over, (list, tuple)) else [over]
        if len(names) != 1:
            raise SimplydataError(f'With in_each= a part of the dates, over= names the one direction of dates, such as '
                                  f'over="{dated[0] if dated else "time"}".')
        block._axis(step, names[0])
        if names[0] not in dated:
            raise SimplydataError(f'{names[0]} has no dates as labels, so it cannot be grouped by month or year. Give '
                                  f'it dates first:  {block._name}.add_labels_to("{names[0]}", dates)')
        return names[0]
    if len(dated) == 1:
        return dated[0]
    if not dated:
        raise SimplydataError(
            f"No direction of this block has dates as labels, so it cannot be grouped by month or year. Give one "
            f"dates first, for example:\n    dates = sdata.make_run_of_dates(\"2010-01\", how_many=120, every=\"month\")"
            f"\n    {block._name}.add_labels_to(\"{block._names[0]}\", dates)")
    raise SimplydataError("Several directions have dates (" + ", ".join(dated) + "); over= says which one, such as "
                          f'over="{dated[0]}".')


def is_time_part(block, in_each) -> bool:
    return isinstance(in_each, str) and in_each not in block._names and in_each in TIME_PARTS


def _check_choice(step, option, value, choices):
    if not isinstance(value, str) or value not in choices:
        raise choice_error(step, option, value, list(choices))
    return value


# ====================================================================== summaries by dates and in groups (P26, P46)
def block_summary_by_time_or_groups(block, step: str, func, over, in_each, every, in_groups_of, only_show_new_shape,
                                    **more):
    """find_average(in_each="month"), find_average(every="month") and find_average(in_groups_of={...}) on a block."""
    from .blocks import NumberBlock

    word = f"find_{step}"
    given = [x for x in (every, in_groups_of) if x is not None] + ([in_each] if is_time_part(block, in_each) else [])
    if len(given) > 1:
        raise SimplydataError(f".{word}() takes one of in_each= (a part of the dates), every= and in_groups_of=.")
    what = "percentiles" if step == "percentile" else f"{step.replace('_', ' ')}s".replace("averages", "averages")
    if in_groups_of is not None:
        if over is not None or in_each is not None:
            raise SimplydataError(f".{word}(in_groups_of=...) takes no over= or in_each=: the groups say which "
                                  "directions shrink.")
        return _in_groups(block, step, func, in_groups_of, only_show_new_shape, **more)
    xr = _xarray(f".{word}()")
    if every is not None:
        if in_each is not None:
            raise SimplydataError(f".{word}(every=...) takes no in_each=.")
        _check_choice(word, "every", every, EVERY_STEPS)
        name = _dates_direction(block, word, over)
        freq = EVERY_STEPS[every]
        da = to_xarray(block, word)
        extra = {"label": "left", "closed": "left"} if every == "week" else {}
        grouped = da.resample({name: freq}, **extra)
        options = ', label="left", closed="left"' if extra else ""
        call = f'resample({name}="{freq}"{options})'
        how = f"one for each {every} of the calendar"
    else:
        part = TIME_PARTS[in_each]
        name = _dates_direction(block, word, over)
        da = to_xarray(block, word)
        grouped = da.groupby(f"{name}.{part}")
        call = f'groupby("{name}.{part}")'
        how = f"one for each {in_each} ({'all years together' if in_each != 'year' else 'every date of that year'})"
    if only_show_new_shape:
        sizes = {n: s for n, s in zip(block._names, block._values.shape)}
        sizes[name] = len(grouped.groups)
        renamed = [in_each if (n == name and every is None) else n for n in block._names]
        print(f"{block._shape_words()} -> {say_shape(list(sizes.values()), renamed)} (nothing changed). "
              f"xarray {call}")
        return None
    reduce = XARRAY_SUMMARY[step]
    if step == "percentile":
        result = grouped.quantile(more["q"] / 100, skipna=True).drop_vars("quantile", errors="ignore")
        reduce = f"quantile({more['q'] / 100:g})"
    elif step == "standard_deviation":
        result = grouped.std(ddof=1, skipna=True)
        reduce = "std(ddof=1)"
    else:
        result = getattr(grouped, reduce)(skipna=True)
        reduce = f"{reduce}()"
    rename = {} if every is not None else {TIME_PARTS[in_each]: in_each}
    values, names, labels = from_xarray(result, rename)
    count = values.shape[names.index(in_each if every is None else name)]
    empty = int(block._empty().sum())
    if empty:
        print(f"Note: {amount(empty, 'empty value')} {'was' if empty == 1 else 'were'} skipped.")
    print(f"{count} {what}, {how}: {block._shape_words()} -> {say_shape(values.shape, names)}. "
          f"xarray {call}.{reduce}")
    named = [True if n not in block._names else block._named[block._names.index(n)] for n in names]
    return NumberBlock(values, names, named, labels)


def _in_groups(block, step, func, in_groups_of, only_show_new_shape, **more):
    """in_groups_of={"latitude": 4}: NumPy reshape each named direction into (groups, group size), then the summary over
    the group sizes (as xarray coarsen(..., boundary="exact")); numeric labels are averaged the same way."""
    from .blocks import NumberBlock

    word = f"find_{step}"
    example = f'{block._name}.{word}(in_groups_of={{"{block._names[-1]}": 2}})'
    if not isinstance(in_groups_of, dict) or not in_groups_of:
        raise SimplydataError(f"in_groups_of= needs the size of the groups for each direction, in curly brackets.\n"
                              f"For example:  {example}")
    a = block._values
    shape, sizes = [], {}
    for name, size in in_groups_of.items():
        axis = block._axis(word, name, "in_groups_of")
        if not isinstance(size, _nb.Integral) or isinstance(size, bool) or size < 1:
            raise SimplydataError(f"in_groups_of= needs whole numbers from 1 up as group sizes.\nFor example:  {example}")
        total = a.shape[axis]
        if total % size:
            fits = [d for d in range(1, total + 1) if total % d == 0]
            raise SimplydataError(f"{say_size(total, block._names[axis])} cannot be split into groups of {size} exactly. "
                                  f"Group sizes that fit: {', '.join(map(str, fits))}. Or keep part of it first: "
                                  f'{block._name}.keep_by_position_in("{block._names[axis]}", 1, to={total - total % size})')
        sizes[axis] = int(size)
    for axis, total in enumerate(a.shape):
        k = sizes.get(axis)
        shape += [total // k, k] if k else [total]
    group_axes = []
    position = 0
    for axis in range(a.ndim):
        if axis in sizes:
            group_axes.append(position + 1)
            position += 2
        else:
            position += 1
    new_shape = [a.shape[i] // sizes[i] if i in sizes else a.shape[i] for i in range(a.ndim)]
    call = (f"block.reshape{tuple(shape)}, then np.{func.__name__}(axis={tuple(group_axes) if len(group_axes) > 1 else group_axes[0]}"
            f"{', q=' + format(more['q'], 'g') if 'q' in more else ''}) (as xarray coarsen(boundary=\"exact\"))")
    if only_show_new_shape:
        print(f"{block._shape_words()} -> {say_shape(new_shape, block._names)} (nothing changed). NumPy: {call}")
        return None
    from .summaries import _quiet

    result = np.asarray(_quiet(func, a.reshape(shape), axis=tuple(group_axes), **more))
    labels, left_out = {}, []
    for name, lab in block._labels.items():
        axis = block._names.index(name)
        lab = np.asarray(lab)
        if axis not in sizes:
            labels[name] = lab
        elif lab.dtype.kind in "iuf":
            labels[name] = lab.reshape(-1, sizes[axis]).mean(axis=1)
        else:
            left_out.append(name)
    empty = int(block._empty().sum())
    if empty:
        print(f"Note: {amount(empty, 'empty value')} {'was' if empty == 1 else 'were'} skipped.")
    groups = ", ".join(f"{sizes[i]} {plural(block._names[i]) if sizes[i] != 1 else block._names[i]}" for i in sorted(sizes))
    print(f"The {step.replace('_', ' ')} of each group of {groups}: {block._shape_words()} -> "
          f"{say_shape(result.shape, block._names)}; the labels are the average label of each group. NumPy: {call}"
          + (f" The labels of {', '.join(left_out)} (dates or text) were left out: a group has no single label."
             if left_out else ""))
    return NumberBlock(result, block._names, block._named, labels)


# ====================================================================== blocks with labels
class BlockLabelWords:
    """Words of a block that use the labels of its directions (P27, P28, P29, P47) and change_size_to (P32)."""

    @friendly
    def get_labels_of(self, direction=None) -> Numbers | Table:
        """The labels of one direction (numbers, or a table of dates or text). block.get_labels_of("time")

        Numbers come back as numbers; dates and text as a table with one column named after the direction.
        A direction without labels has only positions (1, 2, 3 ...): add_labels_to gives it some. xarray coords.
        """
        from ..table import Table
        from .numbers import Numbers

        name = self._names[self._axis("get_labels_of", direction, "direction")]
        if name not in self._labels:
            raise SimplydataError(f'{name} has no labels, only positions 1 to {self._values.shape[self._names.index(name)]}.'
                                  f' Give it labels:  {self._name}.add_labels_to("{name}", [...])')
        labels = np.asarray(self._labels[name])
        print(f"The labels of {name}: {labels.size} of them (xarray: block.coords[\"{name}\"]).")
        if labels.dtype.kind in "iuf":
            return Numbers(labels.astype(np.int64 if labels.dtype.kind in "iu" else np.float64).copy())
        import pandas as pd

        return Table(pd.DataFrame({name: labels}))

    @friendly
    def add_labels_to(self: _Same, direction=None, labels=None) -> _Same:
        """Give a direction labels: one for each position, such as dates, depths or plate rows. block.add_labels_to("latitude", [60, 61, 62, 63])

        labels= are numbers, dates (a list of dates, or a table such as sdata.make_run_of_dates(...)), or text.
        They replace any labels the direction had; undo() takes them back. xarray assign_coords.
        """
        axis = self._axis("add_labels_to", direction, "direction")
        name = self._names[axis]
        size = self._values.shape[axis]
        example = f'{self._name}.add_labels_to("{name}", sdata.make_run_of_dates("2010-01", how_many={size}, every="month"))'
        values = _label_values(labels, example)
        if values.ndim != 1 or values.size != size:
            raise SimplydataError(f"{name} has {size} positions, so it needs {size} labels; {values.size} were given."
                                  f"\nFor example:  {example}")
        if values.dtype.kind in "fM" and np.isnan(values.astype(float) if values.dtype.kind == "f" else
                                                  np.isnat(values)).any():
            raise SimplydataError("Every label needs a value; some are empty.")
        if np.unique(values).size != values.size:
            raise SimplydataError(f"Each label of {name} must be different, so that every position can be found by its "
                                  "label.")
        labels_now = dict(self._labels)
        labels_now[name] = values
        named = list(self._named)
        named[axis] = True
        kind = "dates" if values.dtype.kind == "M" else "numbers" if values.dtype.kind in "iuf" else "text"
        print(f"{name} now has {size} labels ({kind}, from {_say_label(values[0])} to {_say_label(values[-1])}). xarray: "
              f"block.assign_coords({name}=labels)")
        return self._change(f"add labels to {name}", self._values, list(self._names), named, labels_now)

    @friendly
    def find_values_at(self, test_method="linear", **at):
        """Values between the labels of a block, by straight lines between neighbours. block.find_values_at(latitude=60.5, longitude=2.5)

        Give a label (or a list of labels) for one or more directions, by name; the others stay as they are.
        test_method= "linear" (straight lines, the default), "nearest" or "cubic". Places outside the labels are
        empty. SciPy interpolate.interpn (the same call xarray interp makes); dates as labels go through xarray
        interp. A single label removes that direction; a list gives it the new labels.
        """
        from .blocks import NumberBlock

        example = f"{self._name}.find_values_at({self._names[0]}=1.5)"
        _check_choice("find_values_at", "test_method", test_method, ZOOM_ORDERS)
        if not at:
            raise SimplydataError(f"find_values_at() needs a label for at least one direction, by name.\nFor example:  "
                                  f"{example}")
        axes, targets = [], []
        for name, value in at.items():
            axis = self._axis("find_values_at", name, "direction")
            if name not in self._labels:
                raise SimplydataError(f'{name} has no labels, so there is nothing to place {value!r} between. Give it '
                                      f'labels first:  {self._name}.add_labels_to("{name}", [...])')
            axes.append(axis)
            targets.append(value)
        dated = [self._names[a] for a in axes if np.asarray(self._labels[self._names[a]]).dtype.kind == "M"]
        if dated:
            da = to_xarray(self, "find_values_at() with dates")
            result = da.interp({n: v for n, v in at.items()}, method=test_method)
            values, names, labels = from_xarray(result)
            print(f"Values at {_say_at(at)} by {test_method} interpolation. xarray interp(method=\"{test_method}\")")
            return _block_or_number(values, names, labels, self)
        from scipy.interpolate import interpn

        points, wanted, singles = [], [], []
        for axis, value in zip(axes, targets):
            labels = np.asarray(self._labels[self._names[axis]])
            if labels.dtype.kind not in "iuf":
                raise SimplydataError(f"{self._names[axis]} has text labels; values between them do not exist. Use "
                                      f'{self._name}.keep_where("{self._names[axis]}", is_one_of=[...]).')
            target = np.atleast_1d(np.asarray(value, dtype=float)) if _numbers_given(value) else None
            if target is None:
                raise SimplydataError(f"{self._names[axis]}= needs a number or a list of numbers.\nFor example:  "
                                      f"{example}")
            points.append(labels.astype(float))
            wanted.append(target)
            singles.append(np.ndim(value) == 0)
        moved = np.moveaxis(self._values.astype(float), axes, list(range(len(axes))))
        mesh = np.stack(np.meshgrid(*wanted, indexing="ij"), axis=-1)
        try:
            out = interpn(points, moved, mesh, method=test_method, bounds_error=False, fill_value=np.nan)
        except ValueError as error:
            raise SimplydataError(f"The labels cannot be used for {test_method} interpolation ({error}). The labels "
                                  "must run steadily up or down, and \"cubic\" needs at least 4 of them.") from None
        out = np.moveaxis(out, list(range(len(axes))), axes)
        names, labels = list(self._names), dict(self._labels)
        for axis, target in zip(axes, wanted):
            labels[names[axis]] = target
        keep = [i for i in range(out.ndim) if not (i in axes and singles[axes.index(i)])]
        out = out.reshape([out.shape[i] for i in keep])
        names = [names[i] for i in keep]
        labels = {n: v for n, v in labels.items() if n in names}
        inside = [int(((t >= lab.min()) & (t <= lab.max())).sum()) for t, lab in zip(wanted, points)]
        asked = int(np.prod([t.size for t in wanted]))
        others = int(np.prod([s for i, s in enumerate(self._values.shape) if i not in axes]))
        outside = (asked - int(np.prod(inside))) * others  # places asked for beyond the first or last label
        print(f"Values at {_say_at(at)} by {test_method} interpolation between the labels"
              + (f"; {outside} places outside the labels are empty" if outside > 0 else "")
              + f". SciPy interpolate.interpn(method=\"{test_method}\") (as xarray interp)")
        return _block_or_number(out, names, labels, self)

    @friendly
    def get_numbers_nearest_to(self, within=None, **at):
        """The numbers at the labels nearest to the ones you give, such as the grid cell nearest a station. block.get_numbers_nearest_to(latitude=60.4, longitude=5.3)

        Give a label for one or more directions, by name; the sentence says which labels were found. within= is
        the largest distance allowed (in the labels' units; for dates a text such as "2 days"). pandas
        Index.get_indexer(method="nearest") on the labels (as xarray sel(method="nearest", tolerance=within)).
        The block itself does not change.
        """
        import pandas as pd

        from .blocks import NumberBlock

        example = f"{self._name}.get_numbers_nearest_to({self._names[0]}=1.5)"
        if not at:
            raise SimplydataError(f"get_numbers_nearest_to() needs a label for at least one direction, by name.\n"
                                  f"For example:  {example}")
        index = [slice(None)] * self._values.ndim
        found = []
        for name, value in at.items():
            axis = self._axis("get_numbers_nearest_to", name, "direction")
            if name not in self._labels:
                raise SimplydataError(f'{name} has no labels, only positions. By position:  '
                                      f'{self._name}.keep_by_position_in("{name}", 1)')
            labels = pd.Index(self._labels[name])
            single = np.ndim(value) == 0
            asked = [value] if single else list(value)
            if labels.dtype.kind == "M":
                asked = pd.to_datetime(asked)
                tolerance = pd.Timedelta(within) if within is not None else None
            else:
                if not _numbers_given(value):
                    raise SimplydataError(f"{name}= needs a number or a list of numbers.\nFor example:  {example}")
                tolerance = within
            if tolerance is not None and not isinstance(tolerance, pd.Timedelta) and not is_number(tolerance):
                raise SimplydataError("within= needs a number in the labels' units (for dates a text such as \"2 days\").")
            if not (labels.is_monotonic_increasing or labels.is_monotonic_decreasing):
                raise SimplydataError(f"The labels of {name} do not run steadily up or down, so the nearest one is not "
                                      "clear. Sort the block along it first.")
            positions = labels.get_indexer(asked, method="nearest", tolerance=tolerance)
            if (positions < 0).any():
                far = [a for a, p in zip(asked, positions) if p < 0]
                raise SimplydataError(f"No label of {name} is within {within} of {far[0]}.")
            index[axis] = int(positions[0]) if single else positions
            found.append(f"{name} {', '.join(_say_label(labels[p]) for p in positions)}")
        values = self._values[tuple(index)] if all(not isinstance(i, np.ndarray) for i in index) else \
            _orthogonal(self._values, index)
        kept = [i for i, x in enumerate(index) if not isinstance(x, int)]
        names = [self._names[i] for i in kept]
        labels = {}
        for i in kept:
            n = self._names[i]
            if n in self._labels:
                labels[n] = np.asarray(self._labels[n])[index[i]] if isinstance(index[i], np.ndarray) else \
                    np.asarray(self._labels[n])
        print(f"Nearest labels: {'; '.join(found)}. pandas Index.get_indexer(method=\"nearest\""
              f"{', tolerance=' + str(within) if within is not None else ''}) (as xarray sel(method=\"nearest\"))")
        return _block_or_number(np.asarray(values).copy(), names, labels, self)

    @friendly(others={"baseline": "from_years"})
    def turn_into_change_from_average(self: _Same, in_each=None, over=None, from_years=None) -> _Same:
        """Take the usual value away from each number, so the numbers become anomalies. block.turn_into_change_from_average(in_each="month")

        in_each="month" subtracts each month's usual value (the average of all Januaries ...) from every value of
        that month (xarray groupby("time.month") minus its mean; also "season", "day of year", "hour", "quarter").
        from_years=["1991", "2020"] takes the usual values from those years only (a reference period, as in climate
        work). over="north" subtracts the average along one direction instead (NumPy nanmean, then stretching).
        Undo with block.undo().
        """
        example = f'{self._name}.turn_into_change_from_average(in_each="month")'
        if in_each is None and over is None:
            raise SimplydataError(f"turn_into_change_from_average() needs in_each= (a part of the dates, such as "
                                  f"\"month\") or over= (a direction).\nFor example:  {example}")
        if in_each is not None:
            _check_choice("turn_into_change_from_average", "in_each", in_each, TIME_PARTS)
            name = _dates_direction(self, "turn_into_change_from_average", over)
            da = to_xarray(self, "turn_into_change_from_average(in_each=...)")
            part = TIME_PARTS[in_each]
            reference, said = da, "all the years"
            if from_years is not None:
                first, last = _two_years(from_years)
                reference = da.sel({name: slice(first, last)})
                if reference.sizes[name] == 0:
                    raise SimplydataError(f"No {name} falls in the years {first} to {last}.")
                said = f"{first} to {last} ({reference.sizes[name]} {plural(name)})"
            usual = reference.groupby(f"{name}.{part}").mean(skipna=True)
            missing = sorted(set(np.unique(getattr(da[name].dt, part).values)) - set(np.asarray(usual[part].values)))
            if missing:
                raise SimplydataError(f"The years {said} have no value for {in_each} {', '.join(map(str, missing))}, so "
                                      "there is nothing to take away there. Choose a longer period.")
            change = (da.groupby(f"{name}.{part}") - usual).drop_vars(part, errors="ignore")
            change = change.transpose(*da.dims)
            print(f"Each number minus the usual value of its {in_each} (the average over {said}): anomalies. "
                  f"xarray: block.groupby(\"{name}.{part}\") - reference.groupby(\"{name}.{part}\").mean()")
            return self._change(f"change from the average of each {in_each}", np.asarray(change.values))
        if from_years is not None:
            raise SimplydataError(f"from_years= goes with in_each= (a part of the dates).\nFor example:  "
                                  f'{self._name}.turn_into_change_from_average(in_each="month", from_years=["1991", "2020"])')
        axes = self._axes("turn_into_change_from_average", over)
        usual = np.nanmean(self._values, axis=tuple(axes), keepdims=True)
        gone = " and ".join(self._names[a] for a in axes)
        print(f"Each number minus the average along {gone}: anomalies. NumPy: block - np.nanmean(block, "
              f"axis={tuple(axes) if len(axes) > 1 else axes[0]}, keepdims=True)")
        return self._change(f"change from the average along {gone}", self._values - usual)

    @friendly(renamed={"method": "test_method"})
    def smooth(self: _Same, over=None, test_method="moving average", window=5, width=None, ends=None) -> _Same:
        """Smooth a block along some directions: each number becomes a summary of its neighbours. block.smooth(over=["latitude", "longitude"], window=3)

        over= names the directions (a block of three or more directions needs it). test_method= "moving average"
        (window= neighbours along each direction; ends="empty", "reflect" or "mirror", SciPy's modes), "gaussian"
        (width=2) or "median", as grid.smooth. SciPy ndimage.uniform_filter, gaussian_filter and median_filter with axes=. Labels stay as they
        are. Undo with block.undo().
        """
        return SmoothOverWords.smooth(self, over=over, test_method=test_method, window=window, width=width, ends=ends)

    @friendly
    def change_size_to(self: _Same, test_method="linear", **sizes) -> _Same:
        """Give directions a new size by filling in between the numbers (as resizing a picture). block.change_size_to(latitude=8, longitude=10)

        Give the new size of each direction to change, by name. test_method= "linear" (straight lines between
        neighbours, the default), "nearest" (copies the nearest number) or "cubic". Numbers as labels are worked
        out the same way, so they stay with their numbers. SciPy ndimage.zoom (NumPy's resize only repeats
        numbers). Undo with block.undo().
        """
        from scipy import ndimage

        example = f'{self._name}.change_size_to({self._names[-1]}=24)'
        _check_choice("change_size_to", "test_method", test_method, ZOOM_ORDERS)
        if not sizes:
            raise SimplydataError(f"change_size_to() needs the new size of a direction, by name.\nFor example:  {example}")
        factors = [1.0] * self._values.ndim
        changed = []
        for name, size in sizes.items():
            if name not in self._names and name.endswith("s") and name[:-1] in self._names:
                name = name[:-1]  # rows=16 for the direction row
            axis = self._axis("change_size_to", name, "direction")
            if not isinstance(size, _nb.Integral) or isinstance(size, bool) or size < 1:
                raise SimplydataError(f"Sizes are whole numbers from 1 up.\nFor example:  {example}")
            factors[axis] = int(size) / self._values.shape[axis]
            changed.append(axis)
        if np.isnan(self._values.astype(float)).any():
            raise SimplydataError("change_size_to() needs a value at every place; fill the empty ones first.")
        order = ZOOM_ORDERS[test_method]
        target = [int(sizes.get(n, sizes.get(plural(n), s))) for n, s in zip(self._names, self._values.shape)]
        out = ndimage.zoom(self._values.astype(float), factors, order=order)
        if list(out.shape) != target:  # zoom rounds the size; it is asked for exactly
            factors = [t / s for t, s in zip(target, self._values.shape)]
            out = ndimage.zoom(self._values.astype(float), factors, order=order)
        labels, left_out = dict(self._labels), []
        for axis in changed:
            n = self._names[axis]
            if n in labels:
                lab = np.asarray(labels[n])
                if lab.dtype.kind in "iuf":
                    labels[n] = ndimage.zoom(lab.astype(float), factors[axis], order=1)
                else:
                    labels.pop(n)
                    left_out.append(n)
        print(f"{self._shape_words()} -> {say_shape(out.shape, self._names)} by {test_method} filling in (SciPy "
              f"ndimage.zoom, order {order})"
              + ("; number labels are filled in by straight lines, so they stay with their numbers" if any(
                  self._names[a] in labels for a in changed) else "")
              + (f". The labels of {', '.join(left_out)} (dates or text) were left out: new places have no label."
                 if left_out else "."))
        return self._change(f"change size to {say_shape(out.shape, self._names)}", out, list(self._names),
                            list(self._named), labels)


def _say_label(value) -> str:
    import pandas as pd

    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return str(pd.Timestamp(value).date()) if pd.Timestamp(value).time() == pd.Timestamp(0).time() else str(value)
    return say(value) if is_number(value) else str(value)


def _say_at(at: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in at.items())


def _numbers_given(value) -> bool:
    if is_number(value):
        return True
    return isinstance(value, (list, tuple, np.ndarray)) and len(value) > 0 and all(is_number(v) for v in value)


def _orthogonal(values, index):
    """values at the positions of each direction (a rectangle, as xarray sel with lists): NumPy ix_ on the lists."""
    lists = [np.arange(values.shape[i]) if isinstance(x, slice) else np.atleast_1d(x) for i, x in enumerate(index)]
    out = values[np.ix_(*lists)]
    singles = tuple(0 if isinstance(x, int) else slice(None) for x in index)
    return out[singles]


def _block_or_number(values, names, labels, block):
    from .blocks import NumberBlock

    values = np.asarray(values)
    if values.ndim == 0:
        return plain(values)
    named = [block._named[block._names.index(n)] if n in block._names else True for n in names]
    return NumberBlock(values, names, named, labels)


def _two_years(value):
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)) or len(value) != 2:
        raise SimplydataError('from_years= needs the first and last year in square brackets, such as '
                              'from_years=["1991", "2020"].')
    return tuple(str(int(v)) if is_number(v) else str(v) for v in value)


def _label_values(labels, example) -> np.ndarray:
    """Labels given as numbers, dates (a list, a pandas or Polars column, a one-column table) or text."""
    import datetime

    import pandas as pd

    if labels is None:
        raise SimplydataError(f"add_labels_to() needs the labels.\nFor example:  {example}")
    if getattr(labels, "_is_simplydata_table", False):
        frame = labels.as_pandas()
        if frame.shape[1] != 1:
            raise SimplydataError("A table of labels needs one column (such as sdata.make_run_of_dates(...)).")
        labels = frame.iloc[:, 0]
    elif getattr(labels, "_is_simplydata_numbers", False) or getattr(labels, "_is_simplydata_block", False):
        labels = labels._values
    if hasattr(labels, "dt") and getattr(labels.dt, "tz", None) is not None:
        labels = pd.DatetimeIndex(labels)
    if isinstance(labels, pd.arrays.DatetimeArray) and labels.tz is not None:
        labels = pd.DatetimeIndex(labels)
    if isinstance(labels, pd.DatetimeIndex) and labels.tz is not None:
        print(f"Note: the dates are in the time zone {labels.tz}; they are kept as the same moments in UTC (blocks hold "
              "dates without a time zone). To keep the local clock, change the time zone in a table first "
              "(table.change_time_zone_in).")
        labels = labels.tz_convert("UTC").tz_localize(None)
    if hasattr(labels, "to_numpy"):
        values = labels.to_numpy()
    else:
        if isinstance(labels, (str, bytes)) or not hasattr(labels, "__len__"):
            raise SimplydataError(f"add_labels_to() needs a list of labels in square brackets.\nFor example:  {example}")
        items = list(labels)
        if items and all(isinstance(v, (datetime.date, np.datetime64, pd.Timestamp)) for v in items):
            return _label_values(pd.DatetimeIndex(pd.to_datetime(items, utc=any(
                getattr(v, "tzinfo", None) is not None for v in items))), example)
        values = np.asarray(items)
    if values.dtype.kind == "O":
        if any(isinstance(v, (datetime.date, np.datetime64, pd.Timestamp)) for v in values):
            if all(isinstance(v, (datetime.date, np.datetime64, pd.Timestamp)) for v in values):
                return _label_values(list(values), example)
            raise SimplydataError("The labels mix dates with other values; give all dates, or all text.")
        values = values.astype(str)
    if values.dtype.kind == "M":
        values = values.astype("datetime64[ns]")
    if values.dtype.kind == "b":
        raise SimplydataError("Labels are numbers, dates or text, not True/False.")
    return values


# ====================================================================== smooth(over=) on grids and blocks (P30)
class SmoothOverWords:
    """smooth(over=[...]) for grids and blocks: SciPy ndimage filters along the directions named."""

    @friendly(renamed={"method": "test_method"})
    def smooth(self: _Same, over=None, test_method="moving average", window=5, width=None, ends=None) -> _Same:
        """Smooth along some directions: each number becomes a summary of its neighbours, as blurring a picture. grid.smooth(window=3)

        over= names the directions (a grid: both, unless you say). test_method= "moving average" (the average of
        window= neighbours along each direction), "gaussian" (a bell curve with a standard deviation of width=2
        places) or "median" (removes single spikes). SciPy ndimage.uniform_filter, gaussian_filter and median_filter
        with axes=. ends= says what happens at the edges, with SciPy's own names for its modes: "empty" (the moving
        average's default: the edges without a full window are left empty, as numbers.smooth), "reflect" (the
        gaussian's and median's default: the edge number is repeated, d c b a | a b c d) or "mirror" (it is not:
        d c b | a b c d). Undo with undo().
        """
        from scipy import ndimage

        from .. import _smoothing

        step = "smooth"
        names = self._direction_names()
        method = _smoothing.read_method(test_method, step) if isinstance(test_method, str) else test_method
        if method not in SMOOTH_METHODS:
            raise SimplydataError(f'On a grid or a block, smooth() takes test_method= "moving average", "gaussian" or '
                                  f'"median" (you gave "{test_method}"). The other ways smooth one list of numbers: '
                                  f'get_all_numbers() or keep one row first.')
        is_block = hasattr(self, "_axes")
        if over is None:
            if is_block and self._values.ndim > 2:
                raise SimplydataError(f"smooth() on a block needs over=, the directions to smooth along.\nFor example:  "
                                      f'{self._name}.smooth(over=["{names[-2]}", "{names[-1]}"], window=3)')
            axes = list(range(self._values.ndim))
        elif is_block:
            axes = sorted(self._axes(step, over))
        else:
            wanted = over if isinstance(over, (list, tuple)) else [over]
            for w in wanted:
                if w not in names:
                    raise choice_error(step, "over", w, names)
            axes = sorted(names.index(w) for w in wanted)
        values = self._values.astype(float)
        if np.isnan(values).any():
            raise SimplydataError(f"smooth() needs a value at every place, but {int(np.isnan(values).sum())} are empty. "
                                  "Fill them first.")
        along = " and ".join(names[a] for a in axes)
        numpy_axes = tuple(axes)
        edge_words = {"reflect": "at the edges the edge number is repeated (SciPy mode \"reflect\")",
                      "mirror": "at the edges the numbers are mirrored about the edge number (SciPy mode \"mirror\")"}
        if method == "gaussian":
            if window != 5:
                raise SimplydataError('test_method="gaussian" takes width= (the standard deviation, in places), not '
                                      'window=.')
            mode = "reflect" if ends is None else ends
            if mode not in edge_words:
                raise choice_error(step, "ends", ends, list(edge_words))
            width = 2 if width is None else width
            if not is_number(width) or width <= 0:
                raise SimplydataError("width= needs a number of places above 0 (the bell curve's standard deviation).")
            out = ndimage.gaussian_filter(values, sigma=float(width), truncate=4.0, mode=mode, axes=numpy_axes)
            words = (f"a bell curve (standard deviation {say(width)} place{'' if width == 1 else 's'}) along {along}; "
                     + edge_words[mode])
            call = f"ndimage.gaussian_filter(block, sigma={say(width)}, mode=\"{mode}\", axes={numpy_axes})"
        else:
            if width is not None:
                raise SimplydataError(f'width= goes with test_method="gaussian"; test_method="{method}" takes window=.')
            if not isinstance(window, _nb.Integral) or isinstance(window, bool) or window < 3 or window % 2 == 0:
                raise SimplydataError("window= needs an odd whole number of places, at least 3, such as window=3, so the "
                                      "window is centred on each number.")
            k = int(window)
            for a in axes:
                if self._values.shape[a] < k:
                    raise SimplydataError(f"{names[a]} has {self._values.shape[a]} places, fewer than the window ({k}).")
            if method == "median":
                mode = "reflect" if ends is None else ends
                if mode not in edge_words:
                    raise choice_error(step, "ends", ends, list(edge_words))
                out = ndimage.median_filter(values, size=k, mode=mode, axes=numpy_axes)
                words = f"the median of {k} neighbours along {along}; {edge_words[mode]}"
                call = f"ndimage.median_filter(block, size={k}, mode=\"{mode}\", axes={numpy_axes})"
            else:
                ends = "empty" if ends is None else ends
                if ends not in ("empty", "reflect", "mirror"):
                    raise choice_error(step, "ends", ends, ["empty", "reflect", "mirror"])
                mode = "reflect" if ends == "empty" else ends  # the edges are left empty anyway
                out = ndimage.uniform_filter(values, size=k, mode=mode, axes=numpy_axes)
                call = f"ndimage.uniform_filter(block, size={k}, mode=\"{mode}\", axes={numpy_axes})"
                half = k // 2
                if ends == "empty":
                    for a in axes:
                        index = [slice(None)] * out.ndim
                        index[a] = np.r_[0:half, out.shape[a] - half:out.shape[a]]
                        out[tuple(index)] = np.nan
                    words = (f"the average of {k} neighbours along {along}; the first and last {half} along each have "
                             "no full window, so they are empty")
                else:
                    words = f"the average of {k} neighbours along {along}; {edge_words[ends]}"
        print(f"Smoothed with {words}. SciPy {call}")
        return self._change(f"smooth ({method}) over {along}", out)


# ====================================================================== chances and random picks (P10, P24)
class ChanceWords:
    """take_log_odds and turn_into_chances: numbers, grids and blocks alike (SciPy special.logit and expit)."""

    @friendly
    def take_log_odds(self: _Same) -> _Same:
        """Turn chances (0 to 1) into log-odds, the logit: 0.8 becomes 1.386. numbers.take_log_odds()

        log-odds = log(p / (1 - p)). Only chances between 0 and 1 have log-odds, so 0, 1 and numbers outside become
        empty. turn_into_chances() takes it back. SciPy special.logit.
        """
        from scipy import special

        v = self._values.astype(float)
        bad = (v <= 0) | (v >= 1)
        with np.errstate(all="ignore"):
            result = np.where(bad, np.nan, special.logit(v))
        print("Chances turned into log-odds (logit). SciPy special.logit")
        note_empty(int((bad & ~np.isnan(v)).sum()), "only chances between 0 and 1 (not 0 or 1 themselves) have log-odds")
        return self._change("log odds", result)

    @friendly
    def turn_into_chances(self: _Same) -> _Same:
        """Turn log-odds back into chances from 0 to 1 (the logistic function): 1.386 becomes 0.8. numbers.turn_into_chances()

        chance = 1 / (1 + e^-x), the inverse logit, as a logistic regression turns its scores into chances. SciPy
        special.expit.
        """
        from scipy import special

        result = special.expit(self._values.astype(float))
        print("Log-odds turned into chances from 0 to 1 (inverse logit, the logistic function). SciPy special.expit")
        return self._change("turn into chances", result)


class RandomPickWords:
    """numbers.make_random_picks (P10): NumPy Generator.choice."""

    @friendly(renamed={"seed": "with_seed"})
    def make_random_picks(self, how_many=None, putting_back=True, with_chances=None, with_seed=None) -> Numbers:
        """Pick numbers at random from these ones; gives back new numbers. numbers.make_random_picks(how_many=40, with_seed=1)

        putting_back=True (the default) puts each pick back, so a number can come up again and you can pick more
        than there are (a bootstrap sample); putting_back=False picks each at most once (as keep_random_numbers).
        with_chances=[0.5, 0.3, 0.2] gives each number its chance of being picked; the chances must add up to 1.
        with_seed=1 gives the same picks every time. NumPy random.default_rng(seed).choice.
        """
        from .numbers import Numbers

        example = "numbers.make_random_picks(how_many=40, putting_back=True, with_seed=1)"
        with_seed = check_seed(with_seed, example)
        if not isinstance(how_many, _nb.Integral) or isinstance(how_many, bool) or how_many < 0:
            raise SimplydataError(f"make_random_picks() needs how_many= as a whole number.\nFor example:  {example}")
        if not isinstance(putting_back, bool):
            raise SimplydataError("putting_back= needs True or False (no quotes).")
        values = self._values.ravel()
        n = values.size
        if n == 0:
            raise SimplydataError("There are no numbers to pick from.")
        if not putting_back and how_many > n:
            raise SimplydataError(f"Without putting back, at most {n} picks can be made (there are {amount(n)}). "
                                  "putting_back=True allows more.")
        chances = None
        if with_chances is not None:
            chances = to_array(with_chances, "with_chances=", "numbers.make_random_picks(how_many=10, with_chances=[0.5, 0.3, 0.2])")
            if chances.ndim != 1 or chances.size != n:
                raise SimplydataError(f"with_chances= needs one chance for each number: {n} chances.")
        rng = np.random.default_rng(with_seed)
        try:
            picks = rng.choice(values, size=int(how_many), replace=putting_back, p=chances)
        except ValueError as error:
            text = str(error)
            if "sum to 1" in text or "probabilities" in text:
                total = float(np.nansum(chances))
                raise SimplydataError(f"with_chances= must add up to 1, as chances do; these add up to {total:g}. "
                                      "Divide each by their total first if they are weights.") from None
            raise SimplydataError(f"The picks could not be made: {text}.") from None
        empty = int(np.isnan(values.astype(float)).sum())
        print(f"{amount(int(how_many), 'pick')} from {amount(n)}, {'putting each back' if putting_back else 'each at most once'}"
              + (", with the chances given" if chances is not None else ", each equally likely")
              + (f" (seed {with_seed})" if with_seed is not None else "; no seed: different each run, add with_seed=1 "
                 "to repeat it")
              + f". NumPy random.default_rng({with_seed if with_seed is not None else ''}).choice(numbers, size={how_many}, "
              f"replace={putting_back}{', p=chances' if chances is not None else ''})")
        if empty:
            print(f"Note: {amount(empty, 'empty value')} can be picked too.")
        return Numbers(np.asarray(picks).copy())


# ====================================================================== sdata.count_ways_to_choose / to_order (P23)
def _two_counts(step, how_many, out_of):
    example = f"sdata.{step}(3, out_of=10)"
    for option, value in (("the first number", how_many), ("out_of=", out_of)):
        if not isinstance(value, _nb.Integral) or isinstance(value, bool) or value < 0:
            raise SimplydataError(f"sdata.{step}() needs {option} as a whole number, 0 or more.\nFor example:  {example}")
    return int(how_many), int(out_of)


@friendly
def count_ways_to_choose(how_many=None, out_of=None) -> int:
    """How many ways there are to choose some things out of more, when the order does not matter. sdata.count_ways_to_choose(3, out_of=10)

    "10 choose 3" = 120: the groups of 3 that can be made from 10. Exact whole numbers, however big. SciPy
    special.comb(10, 3, exact=True); R choose(10, 3).
    """
    k, n = _two_counts("count_ways_to_choose", how_many, out_of)
    from scipy import special

    ways = int(special.comb(n, k, exact=True))
    print(f"{ways:,} way{'' if ways == 1 else 's'} to choose {k} out of {n} (order does not matter). "
          f"SciPy special.comb({n}, {k}, exact=True)")
    return ways


@friendly
def count_ways_to_order(how_many=None, out_of=None) -> int:
    """How many ways there are to pick some things out of more in order (first, second ...). sdata.count_ways_to_order(3, out_of=10)

    10 x 9 x 8 = 720: the orders of 3 that can be made from 10. Exact whole numbers. SciPy special.perm(10, 3,
    exact=True); R factorial(10) / factorial(7).
    """
    k, n = _two_counts("count_ways_to_order", how_many, out_of)
    from scipy import special

    ways = int(special.perm(n, k, exact=True))
    print(f"{ways:,} way{'' if ways == 1 else 's'} to order {k} out of {n} (order matters). "
          f"SciPy special.perm({n}, {k}, exact=True)")
    return ways
