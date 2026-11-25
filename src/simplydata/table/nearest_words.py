"""Table words of the numbers phase, batch 3 (approved by Manish 2026-11-25): nearest rows, distances to the rows of
another table, and the fence (convex hull) around points.

find_nearest_rows_to: SciPy spatial.KDTree (query for how_many=, query_ball_point for within=; the distances of the
rows found by spatial.distance.cdist). find_distances_to_rows_of: SciPy spatial.distance.cdist, the measure from
test_method=. find_fence_around: SciPy spatial.ConvexHull (its vertices go round anticlockwise; in two dimensions its
"volume" is the area and its "area" the length of the fence). Rows with an empty cell in the columns used are left
out, with a note. Own code is glue only.
"""

from __future__ import annotations

from .._typing import _Same

import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .stat_tests import _list_words, _skipped_note

# test_method= of find_distances_to_rows_of -> SciPy's metric name
DISTANCE_METHODS = {"euclidean": "euclidean", "manhattan": "cityblock", "chebyshev": "chebyshev",
                    "bray-curtis": "braycurtis", "canberra": "canberra", "cosine": "cosine"}
DISTANCE_WORDS = {"euclidean": "straight-line", "manhattan": "Manhattan (the sum of the differences)",
                  "chebyshev": "Chebyshev (the biggest difference)", "bray-curtis": "Bray-Curtis",
                  "canberra": "Canberra", "cosine": "cosine (1 minus the cosine of the angle)"}
DISTANCE_SPELLINGS = {"cityblock": "manhattan", "braycurtis": "bray-curtis", "bray curtis": "bray-curtis",
                      "straight line": "euclidean", "straight-line": "euclidean"}


def _number(value) -> bool:
    return isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool) and \
        math.isfinite(value)


class NearestWords:
    def _points(self, step: str, columns, example: str):
        """(numbers of the rows without empty cells in columns, which rows were kept)."""
        if isinstance(columns, str):
            columns = [columns]
        if not isinstance(columns, (list, tuple)) or not columns or not all(isinstance(c, str) for c in columns):
            raise SimplydataError(f"{step}() needs using= as a list of column names in quotes.\nFor example:  "
                                  f"{example}")
        columns = list(dict.fromkeys(columns))
        frame = self._number_frame(f"{step}()", columns)
        keep = np.ones(len(frame), dtype=bool)
        values = []
        for name in columns:
            column = frame[name].to_numpy().astype(float)
            keep &= ~np.isnan(column)
            values.append(column)
        _skipped_note(int((~keep).sum()), columns)
        return np.column_stack(values)[keep], np.flatnonzero(keep), columns

    def _rows_with(self, positions, extra: dict):
        """A new table of the rows at these positions (from 0), with extra columns at the end."""
        frame = self._frame[[int(p) for p in positions]]
        backend = self._frame.implementation
        for name, values in extra.items():
            frame = frame.with_columns(nw.new_series(name, list(values), nw.Float64, backend=backend))
        return self._new_table(nw.maybe_reset_index(frame))

    @friendly
    def find_nearest_rows_to(self: _Same, point=None, using=None, how_many=None, within=None) -> _Same:
        """The rows nearest to a point, with their distance. table.find_nearest_rows_to({"east": 4000, "north": 1000}, how_many=3)

        (with sdata.get_example("stations"))

        point= gives a value for each column, as {"east": 5.3, "north": 60.4} (using= is then those columns), or as
        a list with using= the columns in the same order. how_many= rows (1 unless within= is given); within=2.0
        gives every row at most that far. The distance is the straight line (Euclidean) in the columns used.
        Gives back those rows, nearest first, with a column "distance". SciPy spatial.KDTree.
        """
        from scipy.spatial import KDTree, distance

        step = "find_nearest_rows_to"
        example = 'table.find_nearest_rows_to({"east": 5.3, "north": 60.4}, how_many=3)'
        if isinstance(point, dict):
            if using is None:
                using = list(point)
            missing = [c for c in using if c not in point]
            if missing or set(point) - set(using):
                raise SimplydataError(f"point= needs a value for each column of using= ({_list_words(using)}) "
                                      f"and no other.\nFor example:  {example}")
            values = [point[c] for c in using]
        elif isinstance(point, (list, tuple)) and using is not None:
            values = list(point)
        else:
            raise SimplydataError(f"{step}() needs point= as {{column: value}} (or a list, with using= the "
                                  f"columns).\nFor example:  {example}")
        if not all(_number(v) for v in values):
            raise SimplydataError(f"point= needs a number for each column; it has {values!r}.")
        points, rows, using = self._points(step, using, example)
        if len(values) != len(using):
            raise SimplydataError(f"point= has {len(values)} values for {len(using)} columns of using=.")
        if not len(points):
            raise SimplydataError(f"{step}() found no row without empty cells in {_list_words(using)}.")
        tree = KDTree(points)
        here = np.asarray(values, dtype=float)
        if within is not None:
            if not _number(within) or within < 0:
                raise SimplydataError("within= needs a distance: a number, 0 or more, such as within=2.0.")
            found = np.asarray(tree.query_ball_point(here, r=float(within), return_sorted=True), dtype=np.int64)
            gaps = distance.cdist(here[None, :], points[found])[0] if len(found) else np.array([])
            order = np.argsort(gaps, kind="stable")
            found, gaps = found[order], gaps[order]
            if how_many is not None:
                count = self._how_many(how_many)
                found, gaps = found[:count], gaps[:count]
            said = f"{len(found)} row{'s' if len(found) != 1 else ''} at most {within:g} from the point"
        else:
            count = 1 if how_many is None else self._how_many(how_many)
            count = min(count, len(points))
            gaps, found = tree.query(here, k=count)
            gaps, found = np.atleast_1d(gaps), np.atleast_1d(found)
            said = f"the {count} row{'s' if count != 1 else ''} nearest to the point"
        place = ", ".join(f"{c} {v:g}" for c, v in zip(using, here))
        shown = ", ".join(str(int(rows[i]) + 1) for i in found[:10]) + (" ..." if len(found) > 10 else "")
        print(f"{said[0].upper()}{said[1:]} ({place}): row{'s' if len(found) != 1 else ''} {shown or 'none'}. "
              f"Straight-line distance in {_list_words(using)} (SciPy spatial.KDTree).")
        name = "distance" if "distance" not in self._columns else "distance to the point"
        return self._rows_with(rows[found], {name: gaps})

    @staticmethod
    def _how_many(how_many) -> int:
        if isinstance(how_many, bool) or not isinstance(how_many, (int, np.integer)) or how_many < 1:
            raise SimplydataError("how_many= needs a whole number of rows, 1 or more, such as how_many=3.")
        return int(how_many)

    @friendly(renamed={"method": "test_method", "measure": "test_method"})
    def find_distances_to_rows_of(self: _Same, other=None, using=None, test_method="euclidean", names=None) -> _Same:
        """How far each row is from each row of another table: a table of distances. table.find_distances_to_rows_of(other, using=["east", "north"])

        (with sdata.get_example("stations"))

        One row for each row of this table, one column for each row of the other. using= the columns both tables
        have; test_method="euclidean" (the default, straight-line), "manhattan", "chebyshev", "bray-curtis",
        "canberra" or "cosine". names= a column whose values label the rows and columns (in both tables, or
        [this table's, the other's]). SciPy spatial.distance.cdist. For the rows of one table against each
        other, use find_distances_between_rows.
        """
        from scipy.spatial import distance

        step = "find_distances_to_rows_of"
        example = 'samples.find_distances_to_rows_of(sites, using=["east", "north"])'
        if not hasattr(other, "_frame"):
            raise SimplydataError(f"{step}() needs the other table first.\nFor example:  {example}")
        key = DISTANCE_SPELLINGS.get(str(test_method).strip().lower(), str(test_method).strip().lower())
        if key not in DISTANCE_METHODS:
            raise choice_error(step, "test_method", test_method, list(DISTANCE_METHODS))
        if using is None:
            raise SimplydataError(f"{step}() needs using=, the columns of numbers both tables have.\nFor example:  "
                                  f"{example}")
        mine, my_rows, using = self._points(step, using, example)
        theirs, their_rows, _ = other._points(step, using, example)
        if not len(mine) or not len(theirs):
            raise SimplydataError(f"{step}() needs rows without empty cells in {_list_words(using)} in both tables.")
        if isinstance(names, (list, tuple)) and len(names) == 2:
            my_name, their_name = names
        else:
            my_name = their_name = names
        mine_labels = _labels(self, my_name, my_rows, step)
        their_labels = _labels(other, their_name, their_rows, step)
        if len(set(their_labels)) != len(their_labels):
            raise SimplydataError("names= needs a different value in each row of the other table, as they become "
                                  "column names.")
        first = my_name if isinstance(my_name, str) else "row"
        if first in their_labels:
            first = f"{first} (this table)"
        gaps = distance.cdist(mine, theirs, metric=DISTANCE_METHODS[key])
        data = {first: mine_labels}
        for j, label in enumerate(their_labels):
            data[label] = [float(v) for v in gaps[:, j]]
        print(f"{DISTANCE_WORDS[key][0].upper()}{DISTANCE_WORDS[key][1:]} distances from {len(mine)} rows to the "
              f"{len(theirs)} rows of the other table, in {_list_words(using)} (SciPy spatial.distance.cdist, "
              f'metric="{DISTANCE_METHODS[key]}").')
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    @friendly
    def find_fence_around(self: _Same, x=None, y=None) -> _Same:
        """The shortest fence around all the points (the convex hull): its corner rows, in order. table.find_fence_around(x="east", y="north")

        (with sdata.get_example("stations"))

        Gives back the rows at the corners, in order going round anticlockwise, and prints how many corners,
        the area inside and the length of the fence, in the units of x and y. SciPy spatial.ConvexHull, as R
        chull().
        """
        from scipy.spatial import ConvexHull, QhullError

        step = "find_fence_around"
        example = 'table.find_fence_around(x="east", y="north")'
        if not isinstance(x, str) or not isinstance(y, str):
            raise SimplydataError(f"{step}() needs x= and y=, two columns of numbers.\nFor example:  {example}")
        points, rows, _ = self._points(step, [x, y], example)
        if len(points) < 3:
            raise SimplydataError(f"{step}() needs at least 3 points; it found {len(points)}.")
        try:
            hull = ConvexHull(points)
        except QhullError:
            raise SimplydataError(f"{step}(): the points lie on one straight line, so no fence encloses an area.") \
                from None
        corners = hull.vertices
        print(f"The shortest fence around all {len(points)} points (convex hull): {len(corners)} corners, area "
              f"{hull.volume:.6g}, length {hull.area:.6g} (in the units of {x} and {y}; SciPy spatial.ConvexHull). "
              "The corner rows go round anticlockwise.")
        return self._rows_with(rows[corners], {})


def _labels(table, name, rows, step: str) -> list[str]:
    if name is None:
        return [str(int(r) + 1) for r in rows]
    if not isinstance(name, str):
        raise SimplydataError(f"{step}() needs names= as a column name in quotes (or a list of two).")
    table._need_columns(name)
    values = table._frame[name].to_list()
    return [str(values[int(r)]) for r in rows]
