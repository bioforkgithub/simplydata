"""Families for 100 %, batch 21 (approved by Manish 2026-11-28, plan section 2.9): points in a plane or on the earth,
with SciPy spatial.

find_triangles_between_points: SciPy spatial.Delaunay (and Delaunay.find_simplex for the triangle that holds a point;
tsearch does the same and is deprecated).
find_regions_around_points: SciPy spatial.Voronoi (each region's area from spatial.ConvexHull of its corners, as a
Voronoi region is convex), or spatial.SphericalVoronoi for longitudes and latitudes (with its own calculate_areas).
Rows with an empty cell in the columns used are left out, with a note. Own code is glue only.
"""

from __future__ import annotations

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .._typing import _Same

EARTH_RADIUS_KM = 6371.0088  # the mean radius of the earth (IUGG), for the areas of regions on the earth


def _two_columns(step: str, x, y, example: str, names=("x", "y")):
    if not isinstance(x, str) or not isinstance(y, str):
        raise SimplydataError(f"{step}() needs {names[0]}= and {names[1]}=, two columns of numbers.\n"
                              f"For example:  {example}")
    if x == y:
        raise SimplydataError(f'{step}() needs two different columns for {names[0]}= and {names[1]}=; both are '
                              f'"{x}".\nFor example:  {example}')


class PointWords:
    @friendly(renamed={"points": "containing"})
    def find_triangles_between_points(self: _Same, x=None, y=None, containing=None) -> _Same:
        """Join the points into triangles with no point inside any of them (Delaunay). triangles = table.find_triangles_between_points(x="east", y="north")

        (with sdata.get_example("stations"))

        Gives back one row for each triangle: its corners as the numbers of the table's rows (from 1), and the x
        and y of each corner. Of all ways to join the points into triangles, this one avoids thin slivers: no
        point lies inside the circle through any triangle's corners. Used for maps of values between stations and
        for meshes. containing={"east": [4000, 5200], "north": [1000, 2500]} instead gives the triangle that holds
        each of those points (empty outside all triangles). SciPy spatial.Delaunay (Qhull) and its find_simplex,
        as R deldir and sf::st_triangulate; chart them with draw_lines.
        """
        from scipy.spatial import Delaunay, QhullError

        step = "find_triangles_between_points"
        example = 'table.find_triangles_between_points(x="east", y="north")'
        _two_columns(step, x, y, example)
        points, rows, _ = self._points(step, [x, y], example)
        if len(points) < 3:
            raise SimplydataError(f"{step}() needs at least 3 points; it found {len(points)}.")
        try:
            mesh = Delaunay(points)
        except QhullError:
            raise SimplydataError(f"{step}(): the points lie on one straight line, so they make no triangles.") \
                from None
        corners = mesh.simplices
        backend = self._frame.implementation
        if containing is not None:
            if not isinstance(containing, dict) or set(containing) != {x, y}:
                raise SimplydataError(f"containing= needs a list of values for {x} and for {y}, such as "
                                      f'containing={{"{x}": [4000, 5200], "{y}": [1000, 2500]}}.')
            xs, ys = (np.atleast_1d(np.asarray(containing[c], dtype=float)) for c in (x, y))
            if xs.shape != ys.shape or xs.ndim != 1 or not np.isfinite(np.r_[xs, ys]).all():
                raise SimplydataError(f"containing= needs as many numbers for {x} as for {y}.")
            found = mesh.find_simplex(np.column_stack([xs, ys]))
            inside = found >= 0
            data = {x: xs.tolist(), y: ys.tolist(),
                    "triangle": [int(t) + 1 if t >= 0 else None for t in found]}
            for k in range(3):
                data[f"corner {k + 1}"] = [int(rows[corners[t, k]]) + 1 if t >= 0 else None for t in found]
            print(f"{int(inside.sum())} of {len(found)} points lie inside a triangle (SciPy Delaunay.find_simplex, "
                  f"the triangulation of {len(points)} points); the corners are the table's rows, from 1.")
            # a point outside every triangle has empty cells, so the numbers are decimals (pandas' whole numbers
            # cannot be empty)
            schema = {name: nw.Float64 for name in data}
            return self._new_table(nw.from_dict(data, schema=schema, backend=backend))
        data = {"triangle": list(range(1, len(corners) + 1))}
        for k in range(3):
            data[f"corner {k + 1}"] = [int(rows[c]) + 1 for c in corners[:, k]]
        for k in range(3):
            data[f"{x} {k + 1}"] = [float(v) for v in points[corners[:, k], 0]]
            data[f"{y} {k + 1}"] = [float(v) for v in points[corners[:, k], 1]]
        print(f"{len(points)} points joined into {len(corners)} triangles with no point inside any triangle's circle "
              "(SciPy spatial.Delaunay); the corners are the table's rows, from 1.")
        return self._new_table(nw.from_dict(data, backend=backend))

    @friendly
    def find_regions_around_points(self: _Same, x=None, y=None, longitude=None, latitude=None) -> _Same:
        """The region round each point that is nearer to it than to any other point (Voronoi). regions = table.find_regions_around_points(x="east", y="north")

        (with sdata.get_example("stations"))

        Gives back one row for each point: its row in the table (from 1), how many corners its region has, its
        area, whether the region is open (it reaches out without end at the edge of the points, so it has no area)
        and its corners as text. As the area each rain gauge or station stands for (Thiessen polygons). SciPy
        spatial.Voronoi (Qhull), the areas from spatial.ConvexHull of each region's corners. longitude= and
        latitude= (in degrees) instead give the regions on the earth (SciPy spatial.SphericalVoronoi), areas in
        square kilometres on a sphere of the earth's mean radius, 6371.0088 km. As R deldir and sf::st_voronoi.
        """
        from scipy.spatial import ConvexHull, QhullError, SphericalVoronoi, Voronoi

        step = "find_regions_around_points"
        example = 'table.find_regions_around_points(x="east", y="north")'
        on_earth = longitude is not None or latitude is not None
        if on_earth:
            if x is not None or y is not None:
                raise SimplydataError(f"{step}() takes x= and y= for points on a plane, or longitude= and latitude= "
                                      "for points on the earth; not both.")
            _two_columns(step, longitude, latitude, 'table.find_regions_around_points(longitude="lon", '
                                                    'latitude="lat")', names=("longitude", "latitude"))
            points, rows, _ = self._points(step, [longitude, latitude], example)
        else:
            _two_columns(step, x, y, example)
            points, rows, _ = self._points(step, [x, y], example)
        least = 4 if on_earth else 3
        if len(points) < least:
            raise SimplydataError(f"{step}() needs at least {least} points; it found {len(points)}.")
        if len(np.unique(points, axis=0)) < len(points):
            raise SimplydataError(f"{step}(): two rows are at the same place, so the region between them has no "
                                  "border. Remove the repeated places first (table.remove_duplicate_rows).")
        corners, areas, opened = [], [], []
        if on_earth:
            if not (np.abs(points[:, 1]) <= 90).all():
                raise SimplydataError("latitude= needs degrees from -90 to 90.")
            lon, lat = np.radians(points[:, 0]), np.radians(points[:, 1])
            unit = np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
            try:
                regions = SphericalVoronoi(unit, radius=1.0)
            except ValueError as problem:
                hint = (" The points lie too close together on the earth for regions on a sphere (SciPy sees them as "
                        "flat); for a small area, give places in metres with x= and y=." if "Rank" in str(problem)
                        else "")
                raise SimplydataError(f"SciPy spatial.SphericalVoronoi: {str(problem).splitlines()[0]}.{hint}")                     from None
            regions.sort_vertices_of_regions()
            found_areas = regions.calculate_areas() * EARTH_RADIUS_KM ** 2
            vertices = np.column_stack([np.degrees(np.arctan2(regions.vertices[:, 1], regions.vertices[:, 0])),
                                        np.degrees(np.arcsin(np.clip(regions.vertices[:, 2], -1, 1)))])
            for i, region in enumerate(regions.regions):
                corners.append(" ".join(f"({vertices[v, 0]:.6g}, {vertices[v, 1]:.6g})" for v in region))
                areas.append(float(found_areas[i]))
                opened.append("no")
            counts = [len(r) for r in regions.regions]
            how = ("SciPy spatial.SphericalVoronoi on the unit sphere, areas by calculate_areas times the earth's "
                   "radius squared; the corners are (longitude, latitude)")
        else:
            try:
                regions = Voronoi(points)
            except QhullError:
                raise SimplydataError(f"{step}(): the points lie on one straight line, so the regions are strips "
                                      "without corners.") from None
            counts = []
            for i in range(len(points)):
                region = regions.regions[regions.point_region[i]]
                is_open = -1 in region or not region
                corners.append(" ".join(f"({regions.vertices[v, 0]:.6g}, {regions.vertices[v, 1]:.6g})"
                                        for v in region if v >= 0))
                counts.append(len([v for v in region if v >= 0]))
                opened.append("yes" if is_open else "no")
                areas.append(None if is_open else float(ConvexHull(regions.vertices[region]).volume))
            how = "SciPy spatial.Voronoi; each closed region's area from spatial.ConvexHull of its corners"
        data = {"row": [int(r) + 1 for r in rows], "corners": counts, "area": areas, "open": opened,
                "corner places": corners}
        closed = opened.count("no")
        print(f"The region round each of {len(points)} points ({how}): {closed} closed, {len(points) - closed} open "
              "(reaching out without end, so without an area)." + (" Areas in square kilometres." if on_earth else
                                                                    ""))
        schema = {"row": nw.Int64, "corners": nw.Int64, "area": nw.Float64, "open": nw.String,
                  "corner places": nw.String}
        return self._new_table(nw.from_dict(data, schema=schema, backend=self._frame.implementation))
