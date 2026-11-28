"""Families for 100 %, batches 20-21 (approved by Manish 2026-11-28): grids as pictures (SciPy ndimage) and points
(SciPy spatial), plan section 2.9: the new test_method= values of grid.smooth, find_edges, change_patch_shapes with
each of its ways, find_distance_to_nearest, split_touching_patches, move_and_stretch_by, find_each_patch_that(show=),
find_triangles_between_points, find_regions_around_points and find_distances_between_rows(measure="minkowski"), each
next to the SciPy code that does the same job."""

from . import Entry

PICTURE = "[[0, 0, 0, 0, 0, 0], [0, 7, 8, 1, 0, 0], [0, 9, 6, 0, 0, 3], [0, 0, 0, 0, 5, 4], [2, 0, 0, 0, 0, 0]]"
RAMP = "[[1, 2, 4, 7, 11], [2, 3, 5, 8, 12], [4, 5, 7, 10, 14], [7, 8, 10, 13, 17]]"
RING = "[[0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 1, 0, 1, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]]"
EDGES = "simplydata also keeps the grid's size and says which filter it used; undo() gives the grid back."
SHAPES = "simplydata also counts the yes cells before and after, and undo() gives the grid back."


def _smooth(value: str, extra: str, call: str, choice: str = "", module: str = "ndimage") -> Entry:
    return Entry(
        word="grid.smooth", option=f'test_method="{value}"',
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.smooth(test_method="{value}"{extra})
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import {module}
            g = np.array({RAMP}, dtype=float)
            # smooth(test_method="{value}"{extra})
            {call}{"   # (1)" if choice else ""}
        """},
        compare="value",
        tolerance=1e-12,
        choices=(choice,) if choice else (),
        also="simplydata also says what each cell became and what happens at the edges; undo() gives the grid back.",
    )


def _edges(value: str, call: str, extra: str = "", word_entry: bool = False) -> Entry:
    return Entry(
        word="grid.find_edges", option="" if word_entry else f'test_method="{value}"',
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.find_edges(test_method="{value}"{extra})
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({RAMP}, dtype=float)
            # find_edges(test_method="{value}"{extra})
            {call}
        """},
        compare="value",
        tolerance=1e-12,
        also=EDGES,
    )


def _binary(how: str, call: str, extra: str = "", word_entry: bool = False) -> Entry:
    return Entry(
        word="grid.change_patch_shapes", option="" if word_entry else f'how="{how}"',
        ours=f"""
            grid = sdata.number_grid({RING})
            grid.change_patch_shapes("{how}"{extra})
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            mask = np.array({RING}) == 1
            s = ndimage.generate_binary_structure(2, 1){"   # (1)" if word_entry else ""}
            # change_patch_shapes("{how}"{extra})
            {call}
        """},
        compare="value",
        choices=("the neighbours touch by their sides (touching=\"corners\" lets a shared corner count too), and "
                 "the grid is repeated 2 x by cells out at its edges (as SciPy mode \"reflect\").",)
        if word_entry else (),
        also=SHAPES,
    )


def _grey(how: str, scipy_name: str, first: bool = False) -> Entry:
    return Entry(
        word="grid.change_patch_shapes", option=f'how="{how}" on numbers',
        ours=f"""
            grid = sdata.number_grid({PICTURE})
            grid.change_patch_shapes("{how}", by=1)
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({PICTURE}, dtype=float)
            # change_patch_shapes("{how}", by=1)
            fp = ndimage.iterate_structure(ndimage.generate_binary_structure(2, 1), 1){"   # (1)" if first else ""}
            ndimage.{scipy_name}(g, footprint=fp)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("without a condition, a grid of numbers changes as a grey picture: the neighbours touch by their "
                 "sides, grown to by= cells by iterate_structure.",) if first else (),
        also="simplydata also says it worked on the grey picture; undo() gives the grid back.",
    )


def _distance(value: str, call: str, word_entry: bool = False) -> Entry:
    return Entry(
        word="grid.find_distance_to_nearest", option="" if word_entry else f'test_method="{value}"',
        ours=f"""
            grid = sdata.number_grid({PICTURE})
            grid.find_distance_to_nearest(is_above=4, test_method="{value}")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({PICTURE}, dtype=float)
            # find_distance_to_nearest(is_above=4, test_method="{value}")
            {call}{"   # (1)" if word_entry else ""}
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the distance is measured from every cell that does not meet the condition to the nearest one "
                 "that does (0 at those).",) if word_entry else (),
        also="simplydata also says how many cells meet the condition and how far the farthest cell is.",
    )


ENTRIES = [
    # ---------------------------------------------------------------- grid.smooth: new values (batch 20)
    _smooth("biggest", ", window=3", 'ndimage.maximum_filter(g, size=3, mode="reflect")',
            "a square window of 3 x 3 cells; at the edges the edge number is repeated (SciPy mode \"reflect\")."),
    _smooth("smallest", ", window=3, over=\"row\"", 'ndimage.minimum_filter1d(g, size=3, axis=0, mode="reflect")',
            "along one direction the 1d filter (minimum_filter1d), with the edge number repeated."),
    _smooth("percentile", ", window=3, percentile=90",
            'ndimage.percentile_filter(g, 90, size=3, mode="reflect", axes=(0, 1))'),
    _smooth("rank", ", window=3, rank=2", 'ndimage.rank_filter(g, 1, size=3, mode="reflect", axes=(0, 1))',
            "rank= counts from 1 (SciPy's rank from 0), in a window of 3 x 3 cells."),
    _smooth("summary", ", window=3, summary=\"range\"",
            'ndimage.vectorized_filter(g, np.ptp, size=3, mode="reflect", axes=(0, 1))'),
    _smooth("fourier gaussian", ", width=1", "np.fft.ifft2(ndimage.fourier_gaussian(np.fft.fft2(g), sigma=1)).real",
            "the smoothing is done in the frequencies (NumPy fft2), so the picture wraps round at its edges."),
    _smooth("fourier uniform", ", window=3", "np.fft.ifft2(ndimage.fourier_uniform(np.fft.fft2(g), size=3)).real"),
    _smooth("fourier ellipsoid", ", window=3",
            "np.fft.ifft2(ndimage.fourier_ellipsoid(np.fft.fft2(g), size=3)).real"),
    # ---------------------------------------------------------------- find_edges (batch 20)
    _edges("sobel", "ndimage.generic_gradient_magnitude(g, ndimage.sobel)", word_entry=True),
    _edges("prewitt", "ndimage.generic_gradient_magnitude(g, ndimage.prewitt)"),
    _edges("laplace", "ndimage.laplace(g)"),
    _edges("gaussian laplace", "ndimage.gaussian_laplace(g, sigma=1)"),
    _edges("gaussian gradient", "ndimage.gaussian_gradient_magnitude(g, sigma=2)", extra=", width=2"),
    Entry(
        word="grid.find_edges", option="along=",
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.find_edges(test_method="sobel", along="columns")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({RAMP}, dtype=float)
            # find_edges(test_method="sobel", along="columns")
            ndimage.sobel(g, axis=1)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("along= gives the signed change in one direction; without it, the slope size in both.",),
        also=EDGES,
    ),
    # ---------------------------------------------------------------- change_patch_shapes (batch 20, G9)
    _binary("grow", "ndimage.binary_dilation(np.pad(mask, 2, mode='symmetric'), structure=s)[2:-2, 2:-2]", ", by=1",
            word_entry=True),
    _binary("shrink", "ndimage.binary_erosion(np.pad(mask, 2, mode='symmetric'), structure=s)[2:-2, 2:-2]"),
    _binary("open", "ndimage.binary_opening(np.pad(mask, 2, mode='symmetric'), structure=s)[2:-2, 2:-2]"),
    _binary("close", "ndimage.binary_closing(np.pad(mask, 2, mode='symmetric'), structure=s)[2:-2, 2:-2]"),
    _binary("fill holes", "ndimage.binary_fill_holes(mask, structure=s)"),
    _binary("top hat", "ndimage.white_tophat(mask.astype(np.int16), footprint=s) > 0"),
    _binary("dark top hat", "ndimage.black_tophat(mask.astype(np.int16), footprint=s) > 0"),
    _binary("outline", "ndimage.morphological_gradient(mask.astype(np.int16), footprint=s) > 0"),
    _binary("laplace", "ndimage.morphological_laplace(mask.astype(np.int16), footprint=s)"),
    _binary("match pattern", "ndimage.binary_hit_or_miss(mask, structure1=np.array([[1, 1], [1, 0]]) == 1,\n"
                             "                           structure2=np.array([[1, 1], [1, 0]]) == 0)",
            ", pattern=[[1, 1], [1, 0]]"),
    _binary("keep patches with points", "seeds = np.zeros(mask.shape, dtype=bool)\n"
                                        "            seeds[1, 1] = True\n"
                                        "            ndimage.binary_propagation(seeds, structure=s, mask=mask)",
            ", starting_points=[[2, 2]]"),
    Entry(
        word="grid.change_patch_shapes", option="is_above=",
        ours=f"""
            grid = sdata.number_grid({PICTURE})
            grid.change_patch_shapes("grow", by=2, is_above=5)
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({PICTURE}, dtype=float)
            # change_patch_shapes("grow", by=2, is_above=5)
            s = ndimage.generate_binary_structure(2, 1)
            big = np.pad(g > 5, 4, mode="symmetric")   # (1)
            ndimage.binary_dilation(big, structure=s, iterations=2)[4:-4, 4:-4]
        """},
        compare="value",
        choices=("the patches are the cells that meet the condition; by=2 is two steps (iterations=2), and the "
                 "edge cells are repeated 2 x by cells out (as the grey picture's mode \"reflect\").",),
        also=SHAPES,
    ),
    *[_grey(how, scipy_name, first=how == "grow") for how, scipy_name in (
        ("grow", "grey_dilation"), ("shrink", "grey_erosion"), ("open", "grey_opening"), ("close", "grey_closing"),
        ("top hat", "white_tophat"), ("dark top hat", "black_tophat"), ("outline", "morphological_gradient"),
        ("laplace", "morphological_laplace"))],
    # ---------------------------------------------------------------- find_each_patch_that(show=) (batch 21)
    Entry(
        word="grid.find_each_patch_that", option="show=",
        ours=f"""
            grid = sdata.number_grid({PICTURE})
            p = grid.find_each_patch_that(is_above=2, show=["biggest", "where biggest", "standard deviation",
                                                            "range"])
            p.get_column("row of biggest").as_numpy().tolist() + p.get_column("range").as_numpy().tolist()
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({PICTURE}, dtype=float)
            labels, n = ndimage.label(g > 2)
            # find_each_patch_that(is_above=2, show=["biggest", "where biggest", "standard deviation", "range"])
            low, high, where_low, where_high = ndimage.extrema(g, labels, np.arange(1, n + 1))   # (1)
            spread = ndimage.labeled_comprehension(g, labels, np.arange(1, n + 1), np.ptp, float, np.nan)
            [r + 1 for r, c in where_high] + spread.tolist()
        """},
        compare="value",
        tolerance=1e-12,
        choices=("positions count from 1; the standard deviation has n in the bottom (ndimage.standard_deviation, "
                 "as NumPy).",),
        also="simplydata also adds each value as a column of the patch table, with the patch's cells, total and "
             "centre.",
    ),
    # ---------------------------------------------------------------- distances, watershed, moving (batch 21)
    _distance("straight line", "ndimage.distance_transform_edt(~(g > 4))", word_entry=True),
    _distance("city block", 'ndimage.distance_transform_cdt(~(g > 4), metric="taxicab")'),
    _distance("chessboard", 'ndimage.distance_transform_cdt(~(g > 4), metric="chessboard")'),
    _distance("brute force", 'ndimage.distance_transform_bf(~(g > 4), metric="euclidean")'),
    Entry(
        word="grid.split_touching_patches",
        ours="""
            grid = sdata.number_grid([[1, 2, 9, 2, 1], [1, 3, 9, 3, 1], [1, 2, 9, 2, 1]])
            grid.split_touching_patches(starting_points=[[2, 1], [2, 5]])
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import ndimage
            g = np.array([[1, 2, 9, 2, 1], [1, 3, 9, 3, 1], [1, 2, 9, 2, 1]], dtype=np.uint16)
            markers = np.zeros(g.shape, dtype=np.int32)
            markers[1, 0], markers[1, 4] = 1, 2   # (1)
            # split_touching_patches(starting_points=[[2, 1], [2, 5]])
            ndimage.watershed_ift(g, markers, structure=ndimage.generate_binary_structure(2, 1))
        """},
        compare="value",
        choices=("each starting point (from 1) gets its own patch number, in the order given.",),
        also="simplydata also checks the numbers are whole grey levels and says how many cells each patch has.",
    ),
    Entry(
        word="grid.move_and_stretch_by",
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.move_and_stretch_by(matrix=[[1, 0.5], [0, 1]], shift=[0, 1])
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({RAMP}, dtype=float)
            # move_and_stretch_by(matrix=[[1, 0.5], [0, 1]], shift=[0, 1])
            ndimage.affine_transform(g, [[1, 0.5], [0, 1]], offset=[0, 1], order=1, mode="constant",
                                     cval=np.nan)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("straight lines between neighbouring cells (order 1), and cells from outside the old grid are "
                 "empty.",),
        also="simplydata also counts the cells that came from outside; undo() gives the grid back.",
    ),
    Entry(
        word="grid.move_and_stretch_by", option="rule=",
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.move_and_stretch_by(rule={{"row": "row", "column": "column + 0.5*row"}})
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({RAMP}, dtype=float)
            # move_and_stretch_by(rule={{"row": "row", "column": "column + 0.5*row"}})
            where = lambda p: (p[0], (p[1] + 1) + 0.5 * (p[0] + 1) - 1)   # (1)
            ndimage.geometric_transform(g, where, order=1, mode="constant", cval=np.nan)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the rule's row and column count from 1, so 1 is added before and taken away after.",),
        also="simplydata also reads the formulas safely and counts the cells that came from outside.",
    ),
    Entry(
        word="grid.move_and_stretch_by", option='test_method="fourier"',
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.move_and_stretch_by(shift=[0.5, 1], test_method="fourier")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import ndimage
            g = np.array({RAMP}, dtype=float)
            # move_and_stretch_by(shift=[0.5, 1], test_method="fourier")
            np.fft.ifft2(ndimage.fourier_shift(np.fft.fft2(g), [-0.5, -1])).real   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("shift= says where each new cell takes its number from, as for affine_transform, so SciPy's "
                 "fourier_shift is given minus shift=.",),
        also="simplydata also says the picture wraps round at its edges.",
    ),
    # ---------------------------------------------------------------- points (SciPy spatial, batch 21)
    Entry(
        word="table.find_triangles_between_points",
        data="stations",
        ours="""
            table = sdata.get_example("stations")
            triangles = table.find_triangles_between_points(x="east", y="north")
            triangles.keep_columns("triangle", "corner 1", "corner 2", "corner 3")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy.spatial import Delaunay
            df = pd.read_csv("stations.csv")
            # find_triangles_between_points(x="east", y="north")
            corners = Delaunay(df[["east", "north"]].to_numpy()).simplices + 1   # (1)
            pd.DataFrame({"triangle": range(1, len(corners) + 1), "corner 1": corners[:, 0],
                          "corner 2": corners[:, 1], "corner 3": corners[:, 2]})
        """},
        compare="table",
        choices=("the corners are the table's rows, counted from 1.",),
        also="simplydata also gives the x and y of each corner, and leaves out rows with an empty cell.",
    ),
    Entry(
        word="table.find_triangles_between_points", option="containing=",
        data="stations",
        ours="""
            table = sdata.get_example("stations")
            found = table.find_triangles_between_points(x="east", y="north",
                                                        containing={"east": [4000, 5200], "north": [1000, 2500]})
            found.get_column("triangle")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy.spatial import Delaunay
            df = pd.read_csv("stations.csv")
            # find_triangles_between_points(x="east", y="north", containing=...)
            mesh = Delaunay(df[["east", "north"]].to_numpy())
            mesh.find_simplex(np.array([[4000, 1000], [5200, 2500]])) + 1.0   # (1)
        """},
        compare="value",
        choices=("the triangle numbers count from 1; a point outside every triangle is empty.",),
        also="simplydata also gives the corners of each point's triangle.",
    ),
    Entry(
        word="table.find_regions_around_points",
        data="stations",
        ours="""
            table = sdata.get_example("stations")
            regions = table.find_regions_around_points(x="east", y="north")
            regions.get_column("area")
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy.spatial import ConvexHull, Voronoi
            v = Voronoi(pd.read_csv("stations.csv")[["east", "north"]].to_numpy())
            # find_regions_around_points(x="east", y="north")
            regions = [v.regions[i] for i in v.point_region]
            np.array([np.nan if -1 in r else ConvexHull(v.vertices[r]).volume for r in regions])   # (1)
        """},
        compare="value",
        tolerance=1e-10,
        choices=("a region that reaches out without end (an index -1 in SciPy) is open and has no area; a closed "
                 "region is convex, so ConvexHull gives its area.",),
        also="simplydata also gives each region's corners and says how many are open.",
    ),
    Entry(
        word="table.find_regions_around_points", option="longitude=",
        data="stations",
        ours="""
            table = sdata.table({"lon": [0, 90, 180, -90, 0, 0, 45, -120], "lat": [0, 0, 0, 0, 90, -90, 30, -40]})
            regions = table.find_regions_around_points(longitude="lon", latitude="lat")
            regions.get_column("area")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy.spatial import SphericalVoronoi
            lon, lat = np.radians([0, 90, 180, -90, 0, 0, 45, -120]), np.radians([0, 0, 0, 0, 90, -90, 30, -40])
            # find_regions_around_points(longitude="lon", latitude="lat")
            xyz = np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
            SphericalVoronoi(xyz).calculate_areas() * 6371.0088 ** 2   # (1)
        """},
        compare="value",
        tolerance=1e-10,
        choices=("the areas in square kilometres on a sphere of the earth's mean radius, 6371.0088 km.",),
        also="simplydata also gives each region's corners as longitude and latitude.",
    ),
    Entry(
        word="table.find_distances_between_rows", option='measure="minkowski"',
        data="stations",
        ours="""
            table = sdata.get_example("stations")
            table.keep_first_rows(4)
            table.find_distances_between_rows(columns=["east", "north"], measure="minkowski", power=3)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy.spatial.distance import cdist
            xy = pd.read_csv("stations.csv").head(4)[["east", "north"]].to_numpy()
            # find_distances_between_rows(columns=["east", "north"], measure="minkowski", power=3)
            d = cdist(xy, xy, "minkowski", p=3)   # (1)
            out = pd.DataFrame(d, columns=["1", "2", "3", "4"])
            out.insert(0, "row", ["1", "2", "3", "4"])
            out
        """},
        compare="table",
        tolerance=1e-12,
        choices=("power= is the p of the Minkowski distance: 1 is Manhattan, 2 straight-line.",),
        also="simplydata also labels the rows with names= and says the measure.",
    ),
    # ---------------------------------------------------------------- scipy.signal's 2-D names (batch 21)
    Entry(
        word="grid.smooth", option='test_method="spline"',
        ours="""
            grid = sdata.number_grid([[row + column ** 1.5 for column in range(30)] for row in range(30)])
            grid.smooth(test_method="spline", smoothness=5)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import signal
            g = np.add.outer(np.arange(30), np.arange(30) ** 1.5)
            # smooth(test_method="spline", smoothness=5)
            signal.spline_filter(g, lmbda=5.0)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("a cubic smoothing spline surface; smoothness=5 is SciPy's own default (lmbda=5.0).",),
        also="simplydata also says when the grid is too small for SciPy's edge sums to settle.",
    ),
    Entry(
        word="grid.smooth", option='ends="zeros"',
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.smooth(test_method="rank", rank=2, window=3, ends="zeros")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import signal
            g = np.array({RAMP}, dtype=float)
            # smooth(test_method="rank", rank=2, window=3, ends="zeros")
            signal.order_filter(g, np.ones((3, 3)), 1)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("rank= counts from 1 (SciPy's rank from 0); the cells outside the grid count as 0.",),
        also="simplydata also says what each cell became; undo() gives the grid back.",
    ),
    Entry(
        word="grid.convolve_with",
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.convolve_with([[0, 1, 0], [1, 4, 1], [0, 1, 0]], keep="same")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import signal
            g = np.array({RAMP}, dtype=float)
            # convolve_with([[0, 1, 0], [1, 4, 1], [0, 1, 0]], keep="same")
            signal.convolve2d(g, [[0, 1, 0], [1, 4, 1], [0, 1, 0]], mode="same")   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("cells outside the grid count as 0 (SciPy's boundary \"fill\"), as numbers.convolve_with.",),
        also="simplydata also says the new size; undo() gives the grid back.",
    ),
    Entry(
        word="grid.convolve_with", option="flip=",
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.convolve_with([[1, 2], [0, -1]], flip=False)
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import signal
            g = np.array({RAMP}, dtype=float)
            # convolve_with([[1, 2], [0, -1]], flip=False)
            signal.correlate2d(g, [[1, 2], [0, -1]], mode="full")
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says the kernel was not turned round.",
    ),
    Entry(
        word="grid.convolve_with", option="row_weights=",
        ours=f"""
            grid = sdata.number_grid({RAMP})
            grid.convolve_with(row_weights=[1, 2, 1], column_weights=[1, 0, -1])
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import signal
            g = np.array({RAMP}, dtype=float)
            # convolve_with(row_weights=[1, 2, 1], column_weights=[1, 0, -1])
            signal.sepfir2d(g, [1, 2, 1], [1, 0, -1])   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("at the edges the edge numbers are repeated (as SciPy mode \"reflect\") and the grid keeps its "
                 "size, as SciPy sepfir2d.",),
        also="simplydata also checks each list has an odd number of weights.",
    ),
    Entry(
        word="grid.find_envelope",
        ours="""
            grid = sdata.number_grid([[0, 1, 0, -1], [1, 0, -1, 0], [0, -1, 0, 1]])
            grid.find_envelope()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import signal
            g = np.array([[0, 1, 0, -1], [1, 0, -1, 0], [0, -1, 0, 1]], dtype=float)
            # find_envelope()
            np.abs(signal.hilbert2(g))
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also keeps the grid's size; undo() gives the grid back.",
    ),
]
