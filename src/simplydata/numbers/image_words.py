"""Families for 100 %, batches 20-21 (approved by Manish 2026-11-28, plan section 2.9, G9): a grid as a picture, with
SciPy ndimage.

grid.smooth gets new test_method= values (maximum_filter, minimum_filter and their 1d forms, percentile_filter,
rank_filter, vectorized_filter for a summary, fourier_gaussian, fourier_uniform, fourier_ellipsoid); grid.find_edges
(sobel and prewitt with generic_gradient_magnitude, laplace, gaussian_laplace, gaussian_gradient_magnitude);
grid.change_patch_shapes, one family word for morphology (binary_dilation, binary_erosion, binary_opening,
binary_closing, binary_fill_holes, binary_hit_or_miss, binary_propagation, grey_dilation, grey_erosion, grey_opening,
grey_closing, white_tophat, black_tophat, morphological_gradient, morphological_laplace, with
generate_binary_structure and iterate_structure); grid.find_distance_to_nearest (distance_transform_edt, _cdt and
_bf); grid.split_touching_patches (watershed_ift); grid.move_and_stretch_by (affine_transform, geometric_transform,
fourier_shift). scipy.signal's 2-D names join them: order_filter and spline_filter (with cspline2d) as values of
grid.smooth, grid.convolve_with (convolve2d, correlate2d, sepfir2d) and grid.find_envelope (hilbert2). Every number
comes from SciPy (and NumPy's FFT for the Fourier filters). Own code is glue only:
checks, sentences, positions counted from 1.
"""

from __future__ import annotations

import math
import numbers as _nb

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._typing import _Same
from ._base import NOT_GIVEN, amount, is_number, say
from .numbers_2 import SmoothOverWords
from .numbers_3 import TOUCHING, ZOOM_ORDERS, _no_empty

# smooth(test_method=) values of a grid that SciPy ndimage adds (families for 100 %, batch 20)
SMOOTH_MORE = ("biggest", "smallest", "percentile", "rank", "summary", "fourier gaussian", "fourier uniform",
               "fourier ellipsoid", "spline")
SMOOTH_MORE_SPELLINGS = {"maximum": "biggest", "max": "biggest", "maximum_filter": "biggest",
                         "minimum": "smallest", "min": "smallest", "minimum_filter": "smallest",
                         "percentile_filter": "percentile", "rank_filter": "rank", "generic_filter": "summary",
                         "vectorized_filter": "summary", "fourier_gaussian": "fourier gaussian",
                         "fourier_uniform": "fourier uniform", "fourier_ellipsoid": "fourier ellipsoid",
                         "spline_filter": "spline", "smoothing spline": "spline", "order_filter": "rank"}
# smooth(test_method="summary", summary=): the NumPy summary of the cells in each window
SUMMARIES = {"average": np.mean, "median": np.median, "total": np.sum, "standard deviation": np.std,
             "range": np.ptp, "biggest": np.max, "smallest": np.min}
SMOOTH_ENDS = {"reflect": "at the edges the edge number is repeated (SciPy mode \"reflect\")",
               "mirror": "at the edges the numbers are mirrored about the edge number (SciPy mode \"mirror\")",
               "nearest": "at the edges the edge number is used for every cell outside (SciPy mode \"nearest\")"}
# find_edges(test_method=)
EDGE_METHODS = {"sobel": "the Sobel filter", "prewitt": "the Prewitt filter", "laplace": "the Laplace filter",
                "gaussian laplace": "the Laplace filter of a bell-curve smoothing",
                "gaussian gradient": "the slope size of a bell-curve smoothing"}
EDGE_SPELLINGS = {"gaussian_laplace": "gaussian laplace", "laplacian of gaussian": "gaussian laplace",
                  "log": "gaussian laplace", "gaussian_gradient_magnitude": "gaussian gradient",
                  "gaussian gradient magnitude": "gaussian gradient", "laplacian": "laplace"}
ALONG = {"rows": 0, "columns": 1}
# change_patch_shapes(how): value -> (SciPy for yes/no cells, SciPy for numbers, what it does)
PATCH_SHAPES = {
    "grow": ("binary_dilation", "grey_dilation", "grown by"),
    "shrink": ("binary_erosion", "grey_erosion", "shrunk by"),
    "open": ("binary_opening", "grey_opening", "opened (shrunk, then grown back) by"),
    "close": ("binary_closing", "grey_closing", "closed (grown, then shrunk back) by"),
    "fill holes": ("binary_fill_holes", None, "with their holes filled"),
    "top hat": ("white_tophat", "white_tophat", "top hat (what opening removes) by"),
    "dark top hat": ("black_tophat", "black_tophat", "dark top hat (what closing adds) by"),
    "outline": ("morphological_gradient", "morphological_gradient", "outlined (grown minus shrunk) by"),
    "laplace": ("morphological_laplace", "morphological_laplace", "morphological Laplace (grown plus shrunk minus "
                                                                  "twice the grid) by"),
    "match pattern": ("binary_hit_or_miss", None, "matched to the pattern"),
    "keep patches with points": ("binary_propagation", None, "kept where a patch holds a starting point"),
}
PATCH_SPELLINGS = {"dilate": "grow", "dilation": "grow", "erode": "shrink", "erosion": "shrink", "opening": "open",
                   "closing": "close", "fill": "fill holes", "fill_holes": "fill holes", "white top hat": "top hat",
                   "tophat": "top hat", "black top hat": "dark top hat", "bottom hat": "dark top hat",
                   "gradient": "outline", "hit or miss": "match pattern", "hit_or_miss": "match pattern",
                   "propagation": "keep patches with points", "reconstruct": "keep patches with points"}
YES_NO_ONLY = ("fill holes", "match pattern", "keep patches with points")
# find_distance_to_nearest(test_method=)
DISTANCE_KINDS = {"straight line": ("distance_transform_edt", None, "straight-line (Euclidean)"),
                  "city block": ("distance_transform_cdt", "taxicab", "city-block (rows plus columns)"),
                  "chessboard": ("distance_transform_cdt", "chessboard", "chessboard (the bigger of rows and "
                                                                          "columns)"),
                  "brute force": ("distance_transform_bf", "euclidean", "straight-line (Euclidean), by checking "
                                                                       "every pair of cells")}
DISTANCE_SPELLINGS = {"euclidean": "straight line", "straight-line": "straight line", "taxicab": "city block",
                      "manhattan": "city block", "cityblock": "city block", "chebyshev": "chessboard",
                      "brute-force": "brute force"}
MOVE_METHODS = dict(ZOOM_ORDERS, fourier=(None, "the Fourier shift theorem (the grid wraps round at its edges)"))


def _conditions(is_above, is_below, is_at_least, is_at_most, is_equal_to, is_not_equal_to, is_between, is_one_of):
    return {"is_above": is_above, "is_below": is_below, "is_at_least": is_at_least, "is_at_most": is_at_most,
            "is_equal_to": is_equal_to, "is_not_equal_to": is_not_equal_to, "is_between": is_between,
            "is_one_of": is_one_of}


def _window_words(k: int, axes, along: str) -> str:
    """The window of smooth(): "a 3 x 3 window (9 cells)" over both directions, "3 neighbours along the rows"
    along one."""
    if len(axes) == 2:
        return f"a {k} x {k} window ({k * k} cells)"
    return f"{k} neighbours along the {along}"


def _window(window, step: str) -> int:
    if not isinstance(window, _nb.Integral) or isinstance(window, bool) or window < 3 or window % 2 == 0:
        raise SimplydataError(f"{step}() needs window= as an odd whole number of places, at least 3, such as "
                              "window=3, so the window is centred on each number.")
    return int(window)


def _steps(by, step: str) -> int:
    if not isinstance(by, _nb.Integral) or isinstance(by, bool) or by < 1:
        raise SimplydataError(f"{step}() needs by= as a whole number of cells, 1 or more, such as by=1.")
    return int(by)


def _points(points, shape, step: str, option: str, example: str) -> list[tuple[int, int]]:
    """[[row, column], ...] counting from 1 -> [(row, column)] from 0."""
    if hasattr(points, "_values"):
        points = np.asarray(points._values).tolist()
    if not isinstance(points, (list, tuple)) or not points:
        raise SimplydataError(f"{step}() needs {option}= as a list of [row, column] positions, counting from 1.\n"
                              f"For example:  {example}")
    found = []
    for point in points:
        if not isinstance(point, (list, tuple)) or len(point) != 2 or not all(
                is_number(v) and float(v) == int(v) for v in point):
            raise SimplydataError(f"{option}= needs [row, column] pairs of whole numbers, counting from 1; it has "
                                  f"{point!r}.\nFor example:  {example}")
        row, column = int(point[0]), int(point[1])
        if not (1 <= row <= shape[0] and 1 <= column <= shape[1]):
            raise SimplydataError(f"{option}= has [{row}, {column}], outside the grid ({shape[0]} rows, {shape[1]} "
                                  "columns; positions count from 1).")
        found.append((row - 1, column - 1))
    return found


class ImageWords:
    # ------------------------------------------------------------------ smooth: new values (batch 20)
    @friendly(renamed={"method": "test_method"})
    def smooth(self: _Same, over=None, test_method="moving average", window=5, width=None, ends=None,
               percentile=None, rank=None, summary=None, smoothness=None) -> _Same:
        """Smooth along some directions: each number becomes a summary of its neighbours, as blurring a picture. grid.smooth(window=3)

        over= names the directions (a grid: both, unless you say). test_method= "moving average" (the average of
        window= neighbours along each direction), "gaussian" (a bell curve with a standard deviation of width=2
        places) or "median" (removes single spikes). SciPy ndimage.uniform_filter, gaussian_filter and median_filter
        with axes=. ends= says what happens at the edges, with SciPy's own names for its modes: "empty" (the moving
        average's default: the edges without a full window are left empty, as numbers.smooth), "reflect" (the
        gaussian's and median's default: the edge number is repeated, d c b a | a b c d) or "mirror" (it is not:
        d c b | a b c d). More ways (families for 100 %, plan 2.9), each over a square window= of cells: "biggest"
        and "smallest" (SciPy ndimage.maximum_filter and minimum_filter; maximum_filter1d and minimum_filter1d
        along one direction), "percentile" with percentile=90 (percentile_filter), "rank" with rank=1 (the cell
        that comes at that place when the window is sorted, from 1; rank_filter), "summary" with summary="range"
        (or "average", "median", "total", "standard deviation" with n in the bottom, "biggest", "smallest": that
        NumPy summary of each
        window; vectorized_filter, as generic_filter), and the Fourier filters "fourier gaussian" (width=),
        "fourier uniform" and "fourier ellipsoid" (window=), which smooth in the frequencies and wrap round at the
        edges (fourier_gaussian, fourier_uniform, fourier_ellipsoid on NumPy's FFT). "rank" with ends="zeros"
        counts the cells outside the grid as 0 (SciPy signal.order_filter). "spline" fits a smoothing cubic spline
        surface, smoothness=5 unless you say (0 goes through every number; SciPy signal.spline_filter, from the
        spline coefficients of cspline2d). Undo with undo().
        """
        method = test_method.strip().lower() if isinstance(test_method, str) else test_method
        method = SMOOTH_MORE_SPELLINGS.get(method, method)
        if method not in SMOOTH_MORE:
            for name, value in (("percentile", percentile), ("rank", rank), ("summary", summary),
                                ("smoothness", smoothness)):
                if value is not None:
                    raise SimplydataError(f'{name}= goes with test_method="{name}"; leave it out for '
                                          f'test_method="{test_method}".')
            if ends in ("nearest", "zeros"):
                raise SimplydataError(f'ends="{ends}" goes with the new ways of smoothing a grid ("biggest", '
                                      '"smallest", "percentile", "rank", "summary"; "zeros" with "rank" only).')
            return SmoothOverWords.smooth(self, over=over, test_method=test_method, window=window, width=width,
                                          ends=ends)
        if smoothness is not None and method != "spline":
            raise SimplydataError(f'smoothness= goes with test_method="spline"; leave it out for '
                                  f'test_method="{method}".')
        if method == "spline":
            return self._smooth_spline(over, window, width, ends, percentile, rank, summary, smoothness)
        return self._smooth_picture(method, over, window, width, ends, percentile, rank, summary)

    def _smooth_spline(self, over, window, width, ends, percentile, rank, summary, smoothness):
        from scipy import signal

        if over is not None or window != 5 or width is not None or ends is not None or any(
                v is not None for v in (percentile, rank, summary)):
            raise SimplydataError('test_method="spline" smooths the whole picture with smoothness= alone; leave out '
                                  "over=, window=, width=, ends= and the other options.")
        smoothness = 5.0 if smoothness is None else smoothness
        if not is_number(smoothness) or not smoothness >= 0:
            raise SimplydataError("smoothness= needs a number of 0 or more (0 goes through every number).")
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, "smooth")
        try:
            out = signal.spline_filter(values, lmbda=float(smoothness))
        except ValueError as problem:  # SciPy's edge sums need enough rows and columns to settle
            raise SimplydataError(f"SciPy signal.spline_filter stopped: {str(problem).splitlines()[0]} The grid is "
                                  f"probably too small ({values.shape[0]} x {values.shape[1]}) for its edges to "
                                  "settle; try a bigger grid or a smaller smoothness=.") from None
        print(f"Smoothed with a cubic smoothing spline surface (smoothness {say(smoothness)}). SciPy "
              f"signal.spline_filter(grid, lmbda={say(smoothness)})")
        return self._change("smooth (spline)", np.asarray(out, dtype=float))

    def _smooth_picture(self, method, over, window, width, ends, percentile, rank, summary):
        from scipy import ndimage

        step = "smooth"
        names = ["row", "column"]
        wanted = names if over is None else (over if isinstance(over, (list, tuple)) else [over])
        for w in wanted:
            if w not in names:
                raise choice_error(step, "over", w, names)
        axes = sorted({names.index(w) for w in wanted})
        values = np.asarray(self._values, dtype=float)
        if np.isnan(values).any():
            raise SimplydataError(f"smooth() needs a value at every place, but {int(np.isnan(values).sum())} are "
                                  "empty. Fill them first.")
        along = " and ".join(names[a] + "s" for a in axes)
        for name, value, goes in (("percentile", percentile, "percentile"), ("rank", rank, "rank"),
                                  ("summary", summary, "summary")):
            if value is not None and method != goes:
                raise SimplydataError(f'{name}= goes with test_method="{goes}"; leave it out for '
                                      f'test_method="{method}".')
        if method.startswith("fourier"):
            return self._smooth_fourier(method, axes, window, width, ends)
        if width is not None:
            raise SimplydataError(f'width= goes with test_method="gaussian" and "fourier gaussian"; '
                                  f'test_method="{method}" takes window=.')
        k = _window(window, step)
        for a in axes:
            if values.shape[a] < k:
                raise SimplydataError(f"The grid has {values.shape[a]} {names[a]}s, fewer than the window ({k}).")
        mode = "reflect" if ends is None else ends
        zeros = mode == "zeros" and method == "rank" and len(axes) == 2
        if mode not in SMOOTH_ENDS and not zeros:
            raise choice_error(step, "ends", ends, list(SMOOTH_ENDS) + (["zeros"] if method == "rank" else []))
        one = len(axes) == 1
        if method in ("biggest", "smallest"):
            scipy_name = ("maximum_filter" if method == "biggest" else "minimum_filter") + ("1d" if one else "")
            if one:
                out = getattr(ndimage, scipy_name)(values, size=k, axis=axes[0], mode=mode)
                call = f"ndimage.{scipy_name}(grid, size={k}, axis={axes[0]}, mode=\"{mode}\")"
            else:
                out = getattr(ndimage, scipy_name)(values, size=k, mode=mode)
                call = f"ndimage.{scipy_name}(grid, size={k}, mode=\"{mode}\")"
            words = f"the {method} of {_window_words(k, axes, along)}"
        elif method == "percentile":
            if not is_number(percentile) or not 0 <= percentile <= 100:
                raise SimplydataError('test_method="percentile" needs percentile= from 0 to 100, such as '
                                      "percentile=90.")
            out = ndimage.percentile_filter(values, float(percentile), size=k, mode=mode, axes=tuple(axes))
            call = f"ndimage.percentile_filter(grid, {say(percentile)}, size={k}, mode=\"{mode}\", axes={tuple(axes)})"
            words = (f"the {say(percentile)} percentile of {_window_words(k, axes, along)} (SciPy takes the cell "
                     "at that place in the sorted window, without averaging between cells, so 90 % of 9 cells is "
                     "the biggest)")
        elif method == "rank":
            cells = k ** len(axes)
            if not isinstance(rank, _nb.Integral) or isinstance(rank, bool) or not 1 <= rank <= cells:
                raise SimplydataError(f'test_method="rank" needs rank= as a whole number from 1 to {cells} (the '
                                      f"place in the sorted window of {cells} cells, counting from 1).")
            if zeros:  # the cells outside count as 0: SciPy signal.order_filter
                from scipy import signal

                out = signal.order_filter(values, np.ones((k, k)), int(rank) - 1)
                call = f"signal.order_filter(grid, np.ones(({k}, {k})), {int(rank) - 1})"
            else:
                out = ndimage.rank_filter(values, int(rank) - 1, size=k, mode=mode, axes=tuple(axes))
                call = f"ndimage.rank_filter(grid, {int(rank) - 1}, size={k}, mode=\"{mode}\", axes={tuple(axes)})"
            words = f"number {int(rank)} of {_window_words(k, axes, along)}, sorted from the smallest"
        else:
            if summary not in SUMMARIES:
                raise choice_error(step, "summary", summary, list(SUMMARIES))
            function = SUMMARIES[summary]
            out = ndimage.vectorized_filter(values, function, size=k, mode=mode, axes=tuple(axes))
            call = (f"ndimage.vectorized_filter(grid, np.{function.__name__}, size={k}, mode=\"{mode}\", "
                    f"axes={tuple(axes)})")
            words = f"the {summary} of {_window_words(k, axes, along)}" + (
                " (with n in the bottom, as NumPy std)" if summary == "standard deviation" else "")
        edge = "the cells outside the grid count as 0" if zeros else SMOOTH_ENDS[mode]
        print(f"Smoothed with {words}; {edge}. SciPy {call}")
        return self._change(f"smooth ({method}) over {along}", np.asarray(out, dtype=float))

    def _smooth_fourier(self, method, axes, window, width, ends):
        from scipy import ndimage

        if len(axes) != 2:
            raise SimplydataError(f'test_method="{method}" smooths over both directions of the grid (in the '
                                  "frequencies of the whole picture); leave out over=.")
        if ends is not None:
            raise SimplydataError(f'test_method="{method}" wraps round at the edges (the picture repeats); it '
                                  "takes no ends=.")
        values = np.asarray(self._values, dtype=float)
        spectrum = np.fft.fft2(values)
        if method == "fourier gaussian":
            if window != 5:
                raise SimplydataError('test_method="fourier gaussian" takes width= (the standard deviation, in '
                                      "places), not window=.")
            width = 2 if width is None else width
            if not is_number(width) or width <= 0:
                raise SimplydataError("width= needs a number of places above 0 (the bell curve's standard deviation).")
            filtered = ndimage.fourier_gaussian(spectrum, sigma=float(width))
            words, call = (f"a bell curve (standard deviation {say(width)} places) in the frequencies",
                           f"ndimage.fourier_gaussian(np.fft.fft2(grid), sigma={say(width)})")
        else:
            if width is not None:
                raise SimplydataError(f'test_method="{method}" takes window=, not width=.')
            k = _window(window, "smooth")
            scipy_name = method.replace(" ", "_")
            filtered = getattr(ndimage, scipy_name)(spectrum, size=k)
            shape = "a square" if method == "fourier uniform" else "a circle"
            words, call = (f"the average over {shape} of {k} places, in the frequencies",
                           f"ndimage.{scipy_name}(np.fft.fft2(grid), size={k})")
        out = np.fft.ifft2(filtered).real
        print(f"Smoothed with {words}; the picture wraps round at its edges. SciPy {call}, then np.fft.ifft2 (the "
              "real part)")
        return self._change(f"smooth ({method})", out)

    # ------------------------------------------------------------------ edges (batch 20)
    @friendly(renamed={"method": "test_method"})
    def find_edges(self: _Same, test_method="sobel", along=None, width=None) -> _Same:
        """Find the edges in a grid as a picture: where the numbers change fast. grid.find_edges(test_method="sobel")

        Each cell becomes the size of the change round it, big at an edge and 0 where the numbers are flat.
        test_method= "sobel" (the default) or "prewitt" (the slope size from SciPy ndimage.sobel or prewitt in both
        directions, by generic_gradient_magnitude; along="rows" or "columns" gives the signed change in one
        direction only), "laplace" (the second difference, ndimage.laplace: 0 on a steady slope), "gaussian
        laplace" or "gaussian gradient" (the same after a bell-curve smoothing of width=1 place;
        gaussian_laplace and gaussian_gradient_magnitude). At the edges of the grid the edge number is repeated
        (SciPy mode "reflect"). As MATLAB edge and imgradient, R imager::imgradient. Undo with grid.undo().
        """
        from scipy import ndimage

        step = "find_edges"
        method = test_method.strip().lower() if isinstance(test_method, str) else test_method
        method = EDGE_SPELLINGS.get(method, method)
        if method not in EDGE_METHODS:
            raise choice_error(step, "test_method", test_method, list(EDGE_METHODS))
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, step)
        if along is not None and (along not in ALONG or method not in ("sobel", "prewitt")):
            if along in ALONG:
                raise SimplydataError(f'along= goes with test_method="sobel" and "prewitt"; "{method}" has no '
                                      "direction.")
            raise choice_error(step, "along", along, list(ALONG))
        if width is not None and not method.startswith("gaussian"):
            raise SimplydataError(f'width= goes with test_method="gaussian laplace" and "gaussian gradient".')
        if method in ("sobel", "prewitt"):
            filter_ = getattr(ndimage, method)
            if along is None:
                out = ndimage.generic_gradient_magnitude(values, filter_)
                call = f"ndimage.generic_gradient_magnitude(grid, ndimage.{method})"
                what = "the slope size in both directions"
            else:
                out = filter_(values, axis=ALONG[along])
                call = f"ndimage.{method}(grid, axis={ALONG[along]})"
                what = f"the change going down the {along}" if along == "rows" else "the change going along the " \
                                                                                    "columns"
        elif method == "laplace":
            out, call, what = ndimage.laplace(values), "ndimage.laplace(grid)", "the second difference"
        else:
            width = 1 if width is None else width
            if not is_number(width) or width <= 0:
                raise SimplydataError("width= needs a number of places above 0 (the bell curve's standard deviation).")
            scipy_name = "gaussian_laplace" if method == "gaussian laplace" else "gaussian_gradient_magnitude"
            out = getattr(ndimage, scipy_name)(values, sigma=float(width))
            call = f"ndimage.{scipy_name}(grid, sigma={say(width)})"
            what = f"{'the second difference' if method == 'gaussian laplace' else 'the slope size'} after a bell " \
                   f"curve of {say(width)} place{'' if width == 1 else 's'}"
        print(f"Edges by {EDGE_METHODS[method]}: {what}. SciPy {call}")
        return self._change(f"edges ({method})", np.asarray(out, dtype=float))

    # ------------------------------------------------------------------ patch shapes (batch 20, G9)
    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "between": "is_between"})
    def change_patch_shapes(self: _Same, how=None, by=1, touching="sides", is_above=NOT_GIVEN, is_below=NOT_GIVEN,
                            is_at_least=NOT_GIVEN, is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN,
                            is_not_equal_to=NOT_GIVEN, is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, pattern=None,
                            starting_points=None) -> _Same:
        """Grow, shrink, open, close or fill the patches of a grid as a picture (morphology). grid.change_patch_shapes("grow", by=1)

        The patches are the cells that meet a condition (is_above=5 ...), or the yes cells of a yes or no grid (or
        a grid of 0 and 1); the grid becomes yes or no. Without a condition, a grid of other numbers changes as a
        grey picture (each cell takes the biggest or smallest number round it). how= "grow" (dilation), "shrink"
        (erosion), "open" (shrink then grow: removes specks), "close" (grow then shrink: closes gaps), "fill
        holes", "top hat" (what opening removes: small bright spots), "dark top hat" (what closing adds),
        "outline" (grown minus shrunk), "laplace" (grown plus shrunk minus twice the grid), "match pattern" with
        pattern= rows of 1 (in the patch) and 0 (outside) (hit or miss), or "keep patches with points" with
        starting_points=[[row, column], ...] from 1. by= cells (1 unless you say); touching="sides" (the default)
        or "corners" for the neighbours. At the edges the edge cells are repeated, for patches and grey pictures
        alike (SciPy mode "reflect"), so closing never removes a cell. SciPy
        ndimage.binary_dilation, binary_erosion, binary_opening,
        binary_closing, binary_fill_holes, binary_hit_or_miss, binary_propagation (iterations=by), and for numbers
        grey_dilation, grey_erosion, grey_opening, grey_closing, white_tophat, black_tophat,
        morphological_gradient and morphological_laplace, with the neighbours from generate_binary_structure grown
        by iterate_structure. As MATLAB imdilate, imerode, imopen, imclose, imfill. Undo with grid.undo().
        """
        from scipy import ndimage

        step = "change_patch_shapes"
        choices = list(PATCH_SHAPES)
        if not isinstance(how, str):
            raise SimplydataError(f"{step}() needs how= the patches change, one of: "
                                  + ", ".join(f'"{c}"' for c in choices) + "."
                                  + self._example('change_patch_shapes("grow", by=1)'))
        chosen = PATCH_SPELLINGS.get(how.strip().lower(), how.strip().lower())
        if chosen not in PATCH_SHAPES:
            raise choice_error(step, "how", how, choices)
        steps = _steps(by, step)
        if touching not in TOUCHING:
            raise choice_error(step, "touching", touching, list(TOUCHING))
        if (pattern is not None) != (chosen == "match pattern"):
            raise SimplydataError('pattern= goes with how="match pattern", which needs it: rows of 1 (in the patch) '
                                  "and 0 (outside), such as pattern=[[0, 1, 0], [1, 1, 1], [0, 1, 0]].")
        if (starting_points is not None) != (chosen == "keep patches with points"):
            raise SimplydataError('starting_points= goes with how="keep patches with points", which needs it: '
                                  "[[row, column], ...] counting from 1.")
        if chosen in ("fill holes", "match pattern", "keep patches with points") and by != 1:
            raise SimplydataError(f'how="{chosen}" takes no by=.')
        given = _conditions(is_above, is_below, is_at_least, is_at_most, is_equal_to, is_not_equal_to, is_between,
                            is_one_of)
        values = np.asarray(self._values)
        if values.dtype.kind == "f":
            _no_empty(values, step)
        structure = ndimage.generate_binary_structure(2, TOUCHING[touching])
        has_condition = any(v is not NOT_GIVEN for v in given.values())
        zero_one = values.dtype.kind in "iuf" and np.isin(values, (0, 1)).all()
        if has_condition or values.dtype.kind == "b" or zero_one:
            if has_condition:
                mask, words = self._condition_from(step, given)
                said = "cells that " + words
            else:
                mask = values.astype(bool)
                said = "yes cells" if values.dtype.kind == "b" else "cells of 1"
            return self._binary_shapes(chosen, mask, structure, steps, touching, said, pattern, starting_points)
        if chosen in YES_NO_ONLY:
            raise SimplydataError(f'how="{chosen}" works on patches: give a condition, such as '
                                  f'change_patch_shapes("{chosen}", is_above=5), or use a yes or no grid.')
        scipy_name = PATCH_SHAPES[chosen][1]
        footprint = ndimage.iterate_structure(structure, steps)
        out = getattr(ndimage, scipy_name)(values.astype(float), footprint=footprint)
        print(f"The grid as a grey picture, {PATCH_SHAPES[chosen][2]} {amount(steps, 'cell')}, the neighbours "
              f"touching by their {touching} (SciPy ndimage.{scipy_name}, footprint from generate_binary_structure(2, "
              f"{TOUCHING[touching]}) grown by iterate_structure(..., {steps})).")
        return self._change(f"patch shapes ({chosen})", np.asarray(out, dtype=float))

    def _binary_shapes(self, chosen, mask, structure, steps, touching, said, pattern, starting_points):
        from scipy import ndimage

        scipy_name = PATCH_SHAPES[chosen][0]
        before = int(mask.sum())
        if chosen in ("grow", "shrink", "open", "close"):
            # the grid is repeated at its edges (NumPy pad "symmetric", SciPy's mode "reflect"), 2 x by cells, so
            # the edges behave as in the grey picture: closing never removes a cell, shrinking keeps a patch that
            # reaches the edge
            pad = 2 * steps
            big = np.pad(mask, pad, mode="symmetric")
            out = getattr(ndimage, scipy_name)(big, structure=structure, iterations=steps)[pad:-pad, pad:-pad]
            call = (f"ndimage.{scipy_name}(np.pad(mask, {pad}, mode=\"symmetric\"), structure, iterations={steps}), "
                    "the padding cut off again")
        elif chosen == "fill holes":
            out = ndimage.binary_fill_holes(mask, structure=structure)
            call = "ndimage.binary_fill_holes(mask, structure)"
        elif chosen == "match pattern":
            shape = np.asarray(pattern, dtype=float) if not hasattr(pattern, "_values") else \
                np.asarray(pattern._values, dtype=float)
            if shape.ndim != 2 or not np.isin(shape, (0, 1)).all():
                raise SimplydataError("pattern= needs rows of 1 (in the patch) and 0 (outside), such as "
                                      "pattern=[[0, 1, 0], [1, 1, 1], [0, 1, 0]].")
            out = ndimage.binary_hit_or_miss(mask, structure1=shape == 1, structure2=shape == 0)
            call = "ndimage.binary_hit_or_miss(mask, structure1=pattern == 1, structure2=pattern == 0)"
        elif chosen == "keep patches with points":
            seeds = np.zeros(mask.shape, dtype=bool)
            for row, column in _points(starting_points, mask.shape, "change_patch_shapes", "starting_points",
                                       'grid.change_patch_shapes("keep patches with points", is_above=5, '
                                       "starting_points=[[1, 2]])"):
                seeds[row, column] = True
            out = ndimage.binary_propagation(seeds, structure=structure, mask=mask)
            call = "ndimage.binary_propagation(starting cells, structure, mask=mask)"
        else:
            footprint = ndimage.iterate_structure(structure, steps)
            out = getattr(ndimage, scipy_name)(mask.astype(np.int16), footprint=footprint)
            call = f"ndimage.{scipy_name}(mask as 0 and 1, footprint=iterate_structure(structure, {steps}))"
        out = np.asarray(out)
        keep_numbers = chosen == "laplace"
        out = out.astype(float) if keep_numbers else out.astype(bool)
        by_words = f" {amount(steps, 'cell')}" if PATCH_SHAPES[chosen][2].endswith(" by") else ""
        after = "" if keep_numbers else f"; {before} yes cells before, {int(out.sum())} after"
        edge = "" if chosen in ("match pattern", "keep patches with points") else (
            "; outside the grid counts as no patch" if chosen == "fill holes" else
            "; at the edges the edge cells are repeated (as SciPy mode \"reflect\")")
        print(f"The patches of {said}, {PATCH_SHAPES[chosen][2]}{by_words}, the neighbours touching by their "
              f"{touching}{after}{edge} (SciPy {call}, structure = generate_binary_structure(2, "
              f"{TOUCHING[touching]})).")
        return self._change(f"patch shapes ({chosen})", out)

    # ------------------------------------------------------------------ distances (batch 21)
    @friendly(renamed={"method": "test_method", "above": "is_above", "below": "is_below",
                       "at_least": "is_at_least", "at_most": "is_at_most", "equal_to": "is_equal_to",
                       "between": "is_between"})
    def find_distance_to_nearest(self, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN,
                                 is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN,
                                 is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, test_method="straight line",
                                 cell_size=None):
        """For each cell, the distance to the nearest cell that meets a condition (a distance map). distances = grid.find_distance_to_nearest(is_above=0)

        Gives back a new grid of the same size: 0 at the cells that meet the condition, and for every other cell
        how many cells away the nearest one is. test_method= "straight line" (the default; SciPy
        ndimage.distance_transform_edt, exact), "city block" (rows plus columns; distance_transform_cdt, metric
        "taxicab"), "chessboard" (the bigger of rows and columns; distance_transform_cdt) or "brute force"
        (straight line, checking every pair of cells; distance_transform_bf, slow but simple). cell_size=[height,
        width] gives the distances in your units when the cells are not squares of size 1 (straight line and
        brute force). A yes or no grid needs no condition: the yes cells are the targets. As MATLAB bwdist, R
        EBImage::distmap. Nothing changes in the grid.
        """
        from scipy import ndimage

        from .numbers import NumberGrid

        step = "find_distance_to_nearest"
        method = test_method.strip().lower() if isinstance(test_method, str) else test_method
        method = DISTANCE_SPELLINGS.get(method, method)
        if method not in DISTANCE_KINDS:
            raise choice_error(step, "test_method", test_method, list(DISTANCE_KINDS))
        given = _conditions(is_above, is_below, is_at_least, is_at_most, is_equal_to, is_not_equal_to, is_between,
                            is_one_of)
        values = np.asarray(self._values)
        if values.dtype.kind != "b" and not any(v is not NOT_GIVEN for v in given.values()):
            raise SimplydataError(f"{step}() needs a condition saying which cells to measure to, such as "
                                  "is_above=0 (or a yes or no grid)." + self._example(f"{step}(is_above=0)"))
        targets, words = self._condition_from(step, given)
        if not targets.any():
            raise SimplydataError(f"{step}(): no cell {words.replace('are ', 'is ')}, so there is nothing to measure "
                                  "to.")
        sampling = None
        if cell_size is not None:
            if method in ("city block", "chessboard"):
                raise SimplydataError(f'cell_size= goes with "straight line" and "brute force"; "{method}" counts '
                                      "cells.")
            if not isinstance(cell_size, (list, tuple)) or len(cell_size) != 2 or not all(
                    is_number(v) and v > 0 for v in cell_size):
                raise SimplydataError("cell_size= needs two numbers above 0: the height and the width of a cell, "
                                      "such as cell_size=[2, 1].")
            sampling = [float(v) for v in cell_size]
        scipy_name, metric, how = DISTANCE_KINDS[method]
        away = ~targets
        if scipy_name == "distance_transform_edt":
            out = ndimage.distance_transform_edt(away, sampling=sampling)
            call = "ndimage.distance_transform_edt(~targets" + (f", sampling={sampling})" if sampling else ")")
        elif scipy_name == "distance_transform_cdt":
            out = ndimage.distance_transform_cdt(away, metric=metric)
            call = f"ndimage.distance_transform_cdt(~targets, metric=\"{metric}\")"
        else:
            out = ndimage.distance_transform_bf(away, metric=metric, sampling=sampling)
            call = f"ndimage.distance_transform_bf(~targets, metric=\"{metric}\"" + (
                f", sampling={sampling})" if sampling else ")")
        out = np.asarray(out, dtype=float)
        print(f"{how[0].upper()}{how[1:]} distance from each cell to the nearest cell that "
              f"{words.replace('are ', 'is ')} "
              f"({int(targets.sum())} of {targets.size} cells); the farthest is {float(out.max()):.6g} away. SciPy "
              f"{call}")
        return NumberGrid(out)

    # ------------------------------------------------------------------ watershed (batch 21)
    @friendly(renamed={"points": "starting_points", "markers": "starting_points"})
    def split_touching_patches(self, starting_points=None, touching="sides"):
        """Split a picture into one patch round each starting point, along the ridges between them (watershed). patches = grid.split_touching_patches(starting_points=[[1, 1], [2, 3]])

        Think of the numbers as heights: water rising from each starting point fills the low ground, and where two
        floods meet is the border between their patches. Gives back a new grid of patch numbers (1 for the first
        starting point, 2 for the second ...), as for splitting touching cells or grains in a picture.
        starting_points=[[row, column], ...] count from 1. The numbers need to be whole numbers from 0 to 65535 (a
        picture's grey levels; round_to first if not). touching="sides" (the default) or "corners". SciPy
        ndimage.watershed_ift (the image foresting transform), as MATLAB watershed with markers. Nothing changes
        in the grid.
        """
        from scipy import ndimage

        from .numbers import NumberGrid

        step = "split_touching_patches"
        example = "grid.split_touching_patches(starting_points=[[1, 1], [2, 3]])"
        if touching not in TOUCHING:
            raise choice_error(step, "touching", touching, list(TOUCHING))
        values = np.asarray(self._values)
        if values.dtype.kind == "f":
            _no_empty(values, step)
        values = values.astype(float)
        if not (values == np.round(values)).all() or values.min() < 0 or values.max() > 65535:
            raise SimplydataError(f"{step}() needs whole numbers from 0 to 65535 (grey levels); this grid has "
                                  f"numbers from {values.min():.6g} to {values.max():.6g}. Round them first, for "
                                  "example grid.round_to(with_decimals=0) after scaling.")
        points = _points(starting_points, values.shape, step, "starting_points", example)
        twice = sorted({p for p in points if points.count(p) > 1})
        if twice:
            raise SimplydataError(f"starting_points= has [{twice[0][0] + 1}, {twice[0][1] + 1}] more than once; each "
                                  "starting point makes its own patch, so give each place once.")
        markers = np.zeros(values.shape, dtype=np.int32)
        for label, (row, column) in enumerate(points, 1):
            markers[row, column] = label
        structure = ndimage.generate_binary_structure(2, TOUCHING[touching])
        out = ndimage.watershed_ift(values.astype(np.uint16), markers, structure=structure)
        sizes = np.bincount(out.ravel(), minlength=len(points) + 1)[1:]
        print(f"{len(points)} patch{'' if len(points) == 1 else 'es'} grown from the starting points along the low "
              "ground, touching by their "
              f"{touching}: " + ", ".join(f"patch {i} has {int(n)} cells" for i, n in enumerate(sizes[:8], 1))
              + (" ..." if len(sizes) > 8 else "") + ". SciPy ndimage.watershed_ift (positions from 1).")
        return NumberGrid(np.asarray(out, dtype=float))

    # ------------------------------------------------------------------ move and stretch (batch 21)
    @friendly(renamed={"method": "test_method", "offset": "shift"})
    def move_and_stretch_by(self: _Same, matrix=None, shift=None, rule=None, test_method="linear") -> _Same:
        """Move, stretch, shear or turn a grid as a picture, cell by cell from where each new cell comes. grid.move_and_stretch_by(matrix=[[1, 0.5], [0, 1]])

        Each new cell takes its number from the old grid at matrix times its position, plus shift= (both in
        cells, measured from the first cell; SciPy ndimage.affine_transform). So shift=[0, 2] takes each number
        from 2 columns further on (the picture moves 2 columns back), matrix=[[2, 0], [0, 2]] takes from twice as
        far (the picture shrinks to half). rule={"row": "row + 0.1*column**2", "column": "column"} gives where each
        new cell comes from as formulas of row and column (positions from 1; SciPy ndimage.geometric_transform).
        test_method= "linear" (the default), "nearest" or "cubic", as change_size_to; "fourier" moves by shift=
        alone, also by part of a cell, with the picture wrapping round (ndimage.fourier_shift on NumPy's FFT).
        Cells that come from outside the old grid are empty. As MATLAB imwarp, R imager::imwarp. Undo with
        grid.undo().
        """
        from scipy import ndimage

        step = "move_and_stretch_by"
        if test_method not in MOVE_METHODS:
            raise choice_error(step, "test_method", test_method, list(MOVE_METHODS))
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, step)
        if rule is not None and (matrix is not None or shift is not None):
            raise SimplydataError("rule= gives where each new cell comes from on its own; leave out matrix= and "
                                  "shift=.")
        if rule is None and matrix is None and shift is None:
            raise SimplydataError(f"{step}() needs matrix=, shift= or rule=."
                                  + self._example("move_and_stretch_by(matrix=[[1, 0.5], [0, 1]])"))
        offset = np.zeros(2)
        if shift is not None:
            if not isinstance(shift, (list, tuple)) or len(shift) != 2 or not all(
                    is_number(v) and math.isfinite(v) for v in shift):
                raise SimplydataError("shift= needs two numbers: rows and columns, such as shift=[0, 2].")
            offset = np.asarray(shift, dtype=float)
        if test_method == "fourier":
            if matrix is not None or rule is not None:
                raise SimplydataError('test_method="fourier" moves by shift= alone; leave out matrix= and rule=.')
            moved = ndimage.fourier_shift(np.fft.fft2(values), -offset)
            out = np.fft.ifft2(moved).real
            print(f"Each new cell takes its number from {say(offset[0])} rows and {say(offset[1])} columns further on, "
                  "with the picture wrapping round at its edges (SciPy ndimage.fourier_shift(np.fft.fft2(grid), "
                  f"{[-float(v) for v in offset]}), then np.fft.ifft2, the real part).")
            return self._change("move (fourier)", out)
        order, how = ZOOM_ORDERS[test_method]
        if rule is not None:
            mapping, said = self._rule_mapping(rule, step)
            out = ndimage.geometric_transform(values, mapping, order=order, mode="constant", cval=np.nan)
            call = f"ndimage.geometric_transform(grid, mapping, order={order}, mode=\"constant\", cval=np.nan)"
            what = f"from where the rule says ({said})"
        else:
            grid = np.eye(2) if matrix is None else (np.asarray(matrix._values, dtype=float) if hasattr(
                matrix, "_values") else np.asarray(matrix, dtype=float))
            if grid.shape != (2, 2) or not np.isfinite(grid).all():
                raise SimplydataError("matrix= needs a 2 x 2 grid of numbers, such as matrix=[[1, 0.5], [0, 1]].")
            out = ndimage.affine_transform(values, grid, offset=offset, order=order, mode="constant", cval=np.nan)
            call = (f"ndimage.affine_transform(grid, {grid.tolist()}, offset={offset.tolist()}, order={order}, "
                    "mode=\"constant\", cval=np.nan)")
            what = f"from matrix {grid.tolist()} times its position plus {offset.tolist()}"
        empty = int(np.isnan(out).sum())
        print(f"Each new cell takes its number {what}, by {how}; {amount(empty, 'cell')} came from outside the old "
              f"grid and {'is' if empty == 1 else 'are'} empty. SciPy {call}")
        return self._change("move and stretch", out)

    def _rule_mapping(self, rule, step: str):
        from .._maths_formula import read_formula

        if not isinstance(rule, dict) or set(rule) != {"row", "column"}:
            raise SimplydataError('rule= needs a formula for "row" and one for "column", such as rule={"row": '
                                  '"row + 0.1*column", "column": "column"}.')
        formulas = {}
        for key in ("row", "column"):
            formula = read_formula(rule[key])
            extra = [n for n in formula.names if n not in ("row", "column")]
            if extra or formula.columns_used:
                raise SimplydataError(f'rule= formulas use the names row and column only; "{rule[key]}" has '
                                      f"{', '.join(extra)}.")
            formulas[key] = formula

        def mapping(position):
            here = {"row": position[0] + 1.0, "column": position[1] + 1.0}
            return tuple(float(formulas[key]({n: here[n] for n in formulas[key].names})) - 1.0
                         for key in ("row", "column"))

        return mapping, f'row from {rule["row"]}, column from {rule["column"]}'

    # ------------------------------------------------------------------ scipy.signal's 2-D words (batch 21)
    @friendly(renamed={"mode": "keep"})
    def convolve_with(self: _Same, other=None, keep="all", flip=True, row_weights=None,
                      column_weights=None) -> _Same:
        """Convolve a grid with a small grid of weights (a kernel), as filtering a picture. grid.convolve_with([[0, 1, 0], [1, 4, 1], [0, 1, 0]])

        Each new cell is the sum of the weights times the cells under them as the kernel slides over the grid.
        keep="all" (every overlap: the grid grows by the kernel's size less 1, as numbers.convolve_with), "same"
        (the grid's own size) or "overlap" (only where the kernel fits fully). SciPy signal.convolve2d, cells
        outside the grid counting as 0. flip=False slides the weights without turning them round (a
        correlation; SciPy signal.correlate2d), as for matching a pattern. row_weights= and column_weights=
        instead give one list of weights along the rows and one down the columns (a separable filter, much
        faster; SciPy signal.sepfir2d, with the edge numbers repeated, d c b a | a b c d as SciPy mode "reflect",
        and its size kept). Undo with
        grid.undo().
        """
        from scipy import signal

        from .fourier_words import KEEPS

        step = "convolve_with"
        if keep not in KEEPS:
            raise choice_error(step, "keep", keep, list(KEEPS))
        if not isinstance(flip, bool):
            raise SimplydataError("flip= should be True or False.")
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, step)
        separable = row_weights is not None or column_weights is not None
        if separable:
            if other is not None or keep != "all" or not flip:
                raise SimplydataError("row_weights= and column_weights= go on their own (the grid keeps its size); "
                                      "leave out the kernel, keep= and flip=.")
            if row_weights is None or column_weights is None:
                raise SimplydataError("A separable filter needs both row_weights= and column_weights=.")
            lists = []
            for name, weights in (("row_weights", row_weights), ("column_weights", column_weights)):
                found = np.asarray(getattr(weights, "_values", weights), dtype=float)
                if found.ndim != 1 or found.size % 2 == 0 or not np.isfinite(found).all():
                    raise SimplydataError(f"{name}= needs a list of an odd number of weights, such as [1, 2, 1].")
                lists.append(found)
            out = signal.sepfir2d(values, lists[0], lists[1])
            print(f"Filtered with {lists[0].size} weights along the rows and {lists[1].size} down the columns (a "
                  "separable filter; at the edges the edge number is repeated, as SciPy mode \"reflect\", and the "
                  "grid keeps its size). SciPy signal.sepfir2d")
            return self._change("separable filter", np.asarray(out, dtype=float))
        if other is None:
            raise SimplydataError(f"{step}() needs a small grid of weights (a kernel)."
                                  + self._example("convolve_with([[0, 1, 0], [1, 4, 1], [0, 1, 0]])"))
        kernel = np.asarray(getattr(other, "_values", other), dtype=float)
        if kernel.ndim == 1:
            kernel = kernel.reshape(1, -1)
        if kernel.ndim != 2 or kernel.size == 0 or not np.isfinite(kernel).all():
            raise SimplydataError(f"{step}() needs the kernel as rows of numbers, such as [[0, 1, 0], [1, 4, 1], "
                                  "[0, 1, 0]].")
        scipy_name = "convolve2d" if flip else "correlate2d"
        if keep == "overlap" and (kernel.shape[0] > values.shape[0] or kernel.shape[1] > values.shape[1]) and (
                kernel.shape[0] < values.shape[0] or kernel.shape[1] < values.shape[1]):
            raise SimplydataError(f'keep="overlap" keeps the places where the kernel fits fully inside the grid; this '
                                  f"{kernel.shape[0]} x {kernel.shape[1]} kernel is bigger than the "
                                  f"{values.shape[0]} x {values.shape[1]} grid in one direction, so it never fits. "
                                  'Use keep="same" or keep="all".')
        out = getattr(signal, scipy_name)(values, kernel, mode=KEEPS[keep])
        print(f"{'Convolved' if flip else 'Correlated'} the {values.shape[0]} x {values.shape[1]} grid with a "
              f"{kernel.shape[0]} x {kernel.shape[1]} kernel{'' if flip else ' (not turned round)'}: a "
              f"{out.shape[0]} x {out.shape[1]} grid (keep=\"{keep}\"; cells outside count as 0). SciPy "
              f"signal.{scipy_name}(grid, kernel, mode=\"{KEEPS[keep]}\")")
        return self._change("convolve" if flip else "correlate", np.asarray(out, dtype=float))

    @friendly
    def find_envelope(self: _Same) -> _Same:
        """The envelope of a grid as a picture: the size of its 2-D analytic signal (Hilbert transform). grid.find_envelope()

        Each cell becomes the size (modulus) of the grid's analytic signal along both directions, which follows
        the outline of waves and ripples in the picture, as numbers.find_envelope does for one list. SciPy
        signal.hilbert2 (from NumPy's FFT, so the picture wraps round at its edges). Undo with grid.undo().
        """
        from scipy import signal

        values = np.asarray(self._values, dtype=float)
        _no_empty(values, "find_envelope")
        out = np.abs(signal.hilbert2(values))
        print(f"The envelope of the {values.shape[0]} x {values.shape[1]} grid: the size of its analytic signal "
              "(SciPy signal.hilbert2, then its absolute value).")
        return self._change("envelope", out)
