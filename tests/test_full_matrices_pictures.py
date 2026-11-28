"""Families for 100 %, batches 19-21 (approved by Manish 2026-11-28): the matrices of scipy.linalg (plan section 2.8)
and grids as pictures and points (plan section 2.9, with scipy.signal's 2-D names). Every new word, option and value
against SciPy (or NumPy, SymPy) itself, the refusals with their reasons, and the pointers of the 2.8 and 2.9 names."""

from __future__ import annotations

import numpy as np
import pytest
import sympy as sp
from scipy import linalg, ndimage, signal
from scipy.spatial import ConvexHull, Delaunay, SphericalVoronoi, Voronoi
from scipy.spatial.distance import cdist

import simplydata as sdata
from simplydata._errors import SimplydataError

SPD = [[4, 2, 1], [2, 3, 0.5], [1, 0.5, 2]]
TRI = [[4, 1, 0, 0], [1, 4, 1, 0], [0, 1, 4, 1], [0, 0, 1, 4]]
RAMP = [[1, 2, 4, 7, 11], [2, 3, 5, 8, 12], [4, 5, 7, 10, 14], [7, 8, 10, 13, 17]]
PICTURE = [[0, 0, 0, 0, 0, 0], [0, 7, 8, 1, 0, 0], [0, 9, 6, 0, 0, 3], [0, 0, 0, 0, 5, 4], [2, 0, 0, 0, 0, 0]]
RING = [[0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 1, 0, 1, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]]
SIDES = ndimage.generate_binary_structure(2, 1)


def grid(values):
    return sdata.number_grid([list(map(float, row)) for row in values])


def column(table, name):
    return table.as_pandas()[name].to_numpy(dtype=float)


# ---------------------------------------------------------------- batch 19: take_matrix_function (G7)
@pytest.mark.parametrize("name, scipy_name", [
    ("log", "logm"), ("square root", "sqrtm"), ("exp", "expm"), ("cos", "cosm"), ("sin", "sinm"), ("tan", "tanm"),
    ("cosh", "coshm"), ("sinh", "sinhm"), ("tanh", "tanhm"), ("sign", "signm"), ("logm", "logm"), ("sqrtm", "sqrtm")])
def test_each_matrix_function_is_scipy_linalg_itself(name, scipy_name, capsys):
    g = grid(SPD)
    g.take_matrix_function(name)
    assert np.allclose(g.as_numpy(), getattr(linalg, scipy_name)(np.array(SPD)), rtol=1e-12, atol=1e-14)
    out = capsys.readouterr().out
    assert f"SciPy linalg.{scipy_name}" in out and "not the" in out


def test_the_square_root_times_itself_gives_the_grid_back_and_undo_works():
    g = grid(SPD)
    g.take_matrix_function("square root")
    assert np.allclose(g.as_numpy() @ g.as_numpy(), SPD, atol=1e-12)
    g.undo()
    assert np.allclose(g.as_numpy(), SPD)


def test_a_power_is_numpy_matrix_power_when_whole_and_scipy_fractional_otherwise():
    g = grid(SPD)
    g.take_matrix_function("power", power=3)
    assert np.allclose(g.as_numpy(), np.linalg.matrix_power(np.array(SPD), 3), rtol=1e-14)
    g = grid(SPD)
    g.take_matrix_function("power", power=0.25)
    assert np.allclose(g.as_numpy(), linalg.fractional_matrix_power(np.array(SPD), 0.25), rtol=1e-12)


def test_a_formula_of_x_goes_to_funm():
    g = grid(SPD)
    g.take_matrix_function("1 / (1 + x)")
    theirs = linalg.funm(np.array(SPD), lambda x: 1 / (1 + x), disp=False)[0]
    assert np.allclose(g.as_numpy(), theirs, rtol=1e-12)
    assert np.allclose(g.as_numpy(), np.linalg.inv(np.eye(3) + np.array(SPD)), rtol=1e-10)


def test_matrix_function_refusals():
    with pytest.raises(SimplydataError, match="complex numbers"):
        grid([[-1, 0], [0, 2]]).take_matrix_function("log")
    with pytest.raises(SimplydataError, match="square grid"):
        grid([[1, 2, 3], [4, 5, 6]]).take_matrix_function("log")
    with pytest.raises(SimplydataError, match='power= goes with "power"'):
        grid(SPD).take_matrix_function("log", power=2)
    with pytest.raises(SimplydataError, match="power= as a number"):
        grid(SPD).take_matrix_function("power")
    with pytest.raises(SimplydataError, match="Did you mean"):
        grid(SPD).take_matrix_function("squareroot")


# ---------------------------------------------------------------- check_if_grid_is, rotation, angles
@pytest.mark.parametrize("values, kind, expected", [
    (TRI, "symmetric", True), ([[1, 2], [3, 1]], "symmetric", False), (TRI, "hermitian", True),
    (TRI, "banded", True), (SPD, "banded", False), ([[1, 0], [0, 2]], "diagonal", True), (TRI, "diagonal", False),
    ([[1, 2], [0, 3]], "upper triangle", True), ([[1, 2], [0, 3]], "lower triangle", False),
    ([[1, 0], [5, 3]], "lower triangle", True), ([[1, 2, 3]], "symmetric", False)])
def test_check_if_grid_is_follows_scipy_issymmetric_and_bandwidth(values, kind, expected):
    assert grid(values).check_if_grid_is(kind) is expected


def test_check_if_grid_is_within_is_scipy_atol(capsys):
    nearly = grid([[1, 2], [2.0000000001, 1]])
    assert nearly.check_if_grid_is("symmetric") is False
    assert nearly.check_if_grid_is("symmetric", within=1e-6) is True
    assert "SciPy linalg.bandwidth" in (grid(TRI).check_if_grid_is("banded") and capsys.readouterr().out)
    with pytest.raises(SimplydataError, match="within= goes with"):
        grid(TRI).check_if_grid_is("banded", within=0.1)


def test_best_rotation_and_angles_are_scipy():
    a, b = np.array([[1, 0], [0, 1], [1, 1.0]]), np.array([[0, 1], [-1, 0], [-1, 1.0]])
    rotation = grid(a).find_best_rotation_to(grid(b)).as_numpy()
    assert np.allclose(rotation, linalg.orthogonal_procrustes(a, b)[0], atol=1e-12)
    c = np.array([[1, 0], [0, 1], [0, 1.0]])
    angles = grid(a[:, :1].tolist()).find_angles_to(grid(c)).as_numpy()
    assert np.allclose(angles, np.degrees(linalg.subspace_angles(a[:, :1], c)))
    radians = grid(a).find_angles_to(grid(c), in_radians=True).as_numpy()
    assert np.allclose(radians, linalg.subspace_angles(a, c))
    with pytest.raises(SimplydataError, match="same size"):
        grid(a).find_best_rotation_to(grid(c[:2]))


# ---------------------------------------------------------------- solve_matrix_equation
@pytest.mark.parametrize("kind, given, scipy_name", [
    ("lyapunov", dict(a=[[-1, 0.5], [0, -2]], q=[[1, 0], [0, 1]]), "solve_continuous_lyapunov"),
    ("solve_lyapunov", dict(a=[[-1, 0.5], [0, -2]], q=[[1, 0], [0, 1]]), "solve_continuous_lyapunov"),
    ("discrete lyapunov", dict(a=[[0.5, 0.1], [0, 0.3]], q=[[1, 0], [0, 1]]), "solve_discrete_lyapunov"),
    ("sylvester", dict(a=[[-1, 0.5], [0, -2]], b=[[-3]], q=[[1], [2]]), "solve_sylvester"),
    ("riccati", dict(a=[[0, 1], [0, 0]], b=[[0], [1]], q=[[1, 0], [0, 1]], r=[[1]]), "solve_continuous_are"),
    ("discrete riccati", dict(a=[[0, 1], [0, 0]], b=[[0], [1]], q=[[1, 0], [0, 1]], r=[[1]]), "solve_discrete_are")])
def test_each_matrix_equation_is_scipy(kind, given, scipy_name, capsys):
    found = sdata.solve_matrix_equation(kind, **{k: grid(v) for k, v in given.items()}).as_numpy()
    order = {"solve_sylvester": "abq", "solve_continuous_are": "abqr",
             "solve_discrete_are": "abqr"}.get(scipy_name, "aq")
    theirs = getattr(linalg, scipy_name)(*(np.array(given[k], dtype=float) for k in order))
    assert np.allclose(found, theirs, rtol=1e-12)
    assert f"SciPy linalg.{scipy_name}" in capsys.readouterr().out


def test_matrix_equation_refusals():
    with pytest.raises(SimplydataError, match="r= are missing|b=, r= are missing"):
        sdata.solve_matrix_equation("riccati", a=[[0, 1], [0, 0]], q=[[1, 0], [0, 1]])
    with pytest.raises(SimplydataError, match="leave out b="):
        sdata.solve_matrix_equation("lyapunov", a=[[1]], q=[[1]], b=[[1]])
    with pytest.raises(SimplydataError, match="Did you mean"):
        sdata.solve_matrix_equation("lyapunof", a=[[1]], q=[[1]])


# ---------------------------------------------------------------- break_down, solve_for, find_eigenvalues
def test_break_down_rq_cs_real_eigen_blocks_and_jordan_are_scipy_and_sympy():
    parts = grid(SPD).break_down(test_method="rq")
    r, q = linalg.rq(np.array(SPD), mode="economic")
    assert np.allclose(parts["R"].as_numpy(), r) and np.allclose(parts["Q"].as_numpy(), q)
    orthogonal = [[0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 0]]
    parts = grid(orthogonal).break_down(test_method="cossin")
    for found, theirs in zip(parts.values(), linalg.cossin(np.array(orthogonal, dtype=float), p=2, q=2)):
        assert np.allclose(found.as_numpy(), theirs)
    turning = np.array([[0, -2, 0], [1, 0, 0], [0, 0, 3.0]])
    parts = grid(turning).break_down(test_method="real eigen blocks")
    for found, theirs in zip(parts.values(), linalg.cdf2rdf(*linalg.eig(turning))):
        assert np.allclose(found.as_numpy(), theirs)
    parts = grid([[2, 1, 0], [0, 2, 0], [0, 0, 3]]).break_down(test_method="jordan")
    p, j = sp.Matrix([[2, 1, 0], [0, 2, 0], [0, 0, 3]]).jordan_form()
    assert np.allclose(parts["J"].as_numpy(), np.array(j, dtype=float))
    assert np.allclose(parts["P"].as_numpy(), np.array(p, dtype=float))


def test_break_down_refusals():
    with pytest.raises(SimplydataError, match="columns have length 1"):
        grid(SPD).break_down(test_method="cs")
    with pytest.raises(SimplydataError, match="split_at= goes with"):
        grid(SPD).break_down(test_method="qr", split_at=[1, 1])
    with pytest.raises(SimplydataError, match="every eigenvalue is real"):
        grid([[0, -1], [1, 0]]).break_down(test_method="jordan")


def test_solve_for_banded_uses_cholesky_on_the_band_or_solve_banded(capsys):
    x = grid(TRI).solve_for([1, 2, 3, 4], structure="banded").as_numpy()
    assert np.allclose(x, linalg.solve(np.array(TRI, dtype=float), [1, 2, 3, 4]), rtol=1e-12)
    assert "cholesky_banded and cho_solve_banded" in capsys.readouterr().out
    lopsided = [[4, 2, 0, 0], [1, 5, 2, 0], [0, 1, 6, 2], [0, 0, 1, 7]]
    x = grid(lopsided).solve_for([1, 2, 3, 4], structure="banded").as_numpy()
    assert np.allclose(x, linalg.solve(np.array(lopsided, dtype=float), [1, 2, 3, 4]), rtol=1e-12)
    assert "SciPy linalg.solve_banded" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="does not go"):
        grid(TRI).solve_for([1, 2, 3, 4], structure="banded", exactly=True)


def test_find_eigenvalues_from_the_band():
    banded = column(grid(TRI).find_eigenvalues(structure="banded"), "eigenvalue")
    tridiagonal = column(grid(TRI).find_eigenvalues(structure="tridiagonal"), "eigenvalue")
    theirs = linalg.eigvalsh_tridiagonal([4, 4, 4, 4], [1, 1, 1])[::-1]
    assert np.allclose(banded, theirs) and np.allclose(tridiagonal, theirs)
    with pytest.raises(SimplydataError, match="symmetric"):
        grid([[1, 2], [3, 1]]).find_eigenvalues(structure="banded")
    with pytest.raises(SimplydataError, match="one diagonal each"):
        grid(SPD).find_eigenvalues(structure="tridiagonal")


def test_khatri_rao_column_by_column():
    a, b = [[1, 2], [3, 4]], [[5, 6], [7, 8], [9, 10]]
    found = grid(a).make_pair_table_with(grid(b), as_blocks=True, column_by_column=True).as_numpy()
    assert np.allclose(found, linalg.khatri_rao(np.array(a), np.array(b)))
    with pytest.raises(SimplydataError, match="goes with as_blocks=True"):
        grid(a).make_pair_table_with(grid(b), column_by_column=True)


# ---------------------------------------------------------------- batch 20: grid.smooth new values
G = np.array(RAMP, dtype=float)


@pytest.mark.parametrize("options, theirs", [
    (dict(test_method="biggest", window=3), lambda: ndimage.maximum_filter(G, size=3, mode="reflect")),
    (dict(test_method="biggest", window=3, over="column"), lambda: ndimage.maximum_filter1d(G, 3, axis=1)),
    (dict(test_method="smallest", window=3), lambda: ndimage.minimum_filter(G, size=3, mode="reflect")),
    (dict(test_method="smallest", window=3, over="row"), lambda: ndimage.minimum_filter1d(G, 3, axis=0)),
    (dict(test_method="smallest", window=3, ends="nearest"), lambda: ndimage.minimum_filter(G, 3, mode="nearest")),
    (dict(test_method="percentile", window=3, percentile=90), lambda: ndimage.percentile_filter(G, 90, size=3)),
    (dict(test_method="rank", window=3, rank=2), lambda: ndimage.rank_filter(G, 1, size=3)),
    (dict(test_method="rank", window=3, rank=2, ends="zeros"), lambda: signal.order_filter(G, np.ones((3, 3)), 1)),
    (dict(test_method="summary", window=3, summary="range"), lambda: ndimage.generic_filter(G, np.ptp, size=3)),
    (dict(test_method="summary", window=3, summary="standard deviation"),
     lambda: ndimage.generic_filter(G, np.std, size=3)),
    (dict(test_method="fourier gaussian", width=1),
     lambda: np.fft.ifft2(ndimage.fourier_gaussian(np.fft.fft2(G), 1)).real),
    (dict(test_method="fourier uniform", window=3),
     lambda: np.fft.ifft2(ndimage.fourier_uniform(np.fft.fft2(G), 3)).real),
    (dict(test_method="fourier ellipsoid", window=3),
     lambda: np.fft.ifft2(ndimage.fourier_ellipsoid(np.fft.fft2(G), 3)).real)])
def test_each_new_smooth_value_is_scipy(options, theirs):
    g = grid(RAMP)
    g.smooth(**options)
    assert np.allclose(g.as_numpy(), theirs(), rtol=1e-12, atol=1e-12)


def test_smooth_spline_is_signal_spline_filter_and_small_grids_are_explained():
    values = [[r + c ** 1.5 for c in range(30)] for r in range(30)]
    g = grid(values)
    g.smooth(test_method="spline", smoothness=5)
    assert np.allclose(g.as_numpy(), signal.spline_filter(np.array(values), lmbda=5.0), rtol=1e-12)
    with pytest.raises(SimplydataError, match="too small"):
        grid(RAMP).smooth(test_method="spline")


def test_smooth_old_values_still_work_and_new_options_are_checked():
    g = grid(RAMP)
    g.smooth(test_method="median", window=3)
    assert np.allclose(g.as_numpy(), ndimage.median_filter(G, size=3, mode="reflect"))
    with pytest.raises(SimplydataError, match='percentile= goes with test_method="percentile"'):
        grid(RAMP).smooth(window=3, percentile=90)
    with pytest.raises(SimplydataError, match='ends="zeros"'):
        grid(RAMP).smooth(window=3, ends="zeros")
    with pytest.raises(SimplydataError, match="rank= as a whole number from 1 to 9"):
        grid(RAMP).smooth(test_method="rank", window=3, rank=10)


# ---------------------------------------------------------------- find_edges
@pytest.mark.parametrize("options, theirs", [
    (dict(), lambda: ndimage.generic_gradient_magnitude(G, ndimage.sobel)),
    (dict(test_method="prewitt"), lambda: ndimage.generic_gradient_magnitude(G, ndimage.prewitt)),
    (dict(test_method="sobel", along="rows"), lambda: ndimage.sobel(G, axis=0)),
    (dict(test_method="prewitt", along="columns"), lambda: ndimage.prewitt(G, axis=1)),
    (dict(test_method="laplace"), lambda: ndimage.laplace(G)),
    (dict(test_method="gaussian laplace", width=2), lambda: ndimage.gaussian_laplace(G, 2)),
    (dict(test_method="gaussian gradient"), lambda: ndimage.gaussian_gradient_magnitude(G, 1))])
def test_find_edges_is_scipy(options, theirs):
    g = grid(RAMP)
    g.find_edges(**options)
    assert np.allclose(g.as_numpy(), theirs(), rtol=1e-12, atol=1e-12)


def test_find_edges_refusals():
    with pytest.raises(SimplydataError, match="along= goes with"):
        grid(RAMP).find_edges(test_method="laplace", along="rows")
    with pytest.raises(SimplydataError, match="width= goes with"):
        grid(RAMP).find_edges(width=2)


# ---------------------------------------------------------------- change_patch_shapes (G9)
M = np.array(RING) == 1


@pytest.mark.parametrize("how, extra, theirs", [
    ("grow", {}, lambda: ndimage.binary_dilation(np.pad(M, 2, mode='symmetric'), SIDES)[2:-2, 2:-2]),
    ("grow", {"by": 2, "touching": "corners"},
     lambda: ndimage.binary_dilation(np.pad(M, 4, mode="symmetric"), ndimage.generate_binary_structure(2, 2),
                                     iterations=2)[4:-4, 4:-4]),
    ("shrink", {}, lambda: ndimage.binary_erosion(np.pad(M, 2, mode='symmetric'), SIDES)[2:-2, 2:-2]),
    ("open", {}, lambda: ndimage.binary_opening(np.pad(M, 2, mode='symmetric'), SIDES)[2:-2, 2:-2]),
    ("close", {}, lambda: ndimage.binary_closing(np.pad(M, 2, mode='symmetric'), SIDES)[2:-2, 2:-2]),
    ("fill holes", {}, lambda: ndimage.binary_fill_holes(M, SIDES)),
    ("top hat", {}, lambda: ndimage.white_tophat(M.astype(np.int16), footprint=SIDES) > 0),
    ("dark top hat", {}, lambda: ndimage.black_tophat(M.astype(np.int16), footprint=SIDES) > 0),
    ("outline", {}, lambda: ndimage.morphological_gradient(M.astype(np.int16), footprint=SIDES) > 0),
    ("laplace", {}, lambda: ndimage.morphological_laplace(M.astype(np.int16), footprint=SIDES)),
    ("match pattern", {"pattern": [[1, 1], [1, 0]]},
     lambda: ndimage.binary_hit_or_miss(M, np.array([[1, 1], [1, 0]]) == 1, np.array([[1, 1], [1, 0]]) == 0)),
    ("keep patches with points", {"starting_points": [[2, 2]]},
     lambda: ndimage.binary_propagation(np.eye(5, dtype=bool) & (np.arange(5) == 1), SIDES, mask=M))])
def test_patch_shapes_on_patches_are_scipy_binary_morphology(how, extra, theirs):
    g = grid(RING)
    g.change_patch_shapes(how, **extra)
    assert np.array_equal(g.as_numpy().astype(float), np.asarray(theirs()).astype(float))


@pytest.mark.parametrize("how, scipy_name", [
    ("grow", "grey_dilation"), ("shrink", "grey_erosion"), ("open", "grey_opening"), ("close", "grey_closing"),
    ("top hat", "white_tophat"), ("dark top hat", "black_tophat"), ("outline", "morphological_gradient"),
    ("laplace", "morphological_laplace")])
def test_patch_shapes_on_numbers_are_scipy_grey_morphology(how, scipy_name):
    g = grid(PICTURE)
    g.change_patch_shapes(how, by=2)
    footprint = ndimage.iterate_structure(SIDES, 2)
    assert np.allclose(g.as_numpy(), getattr(ndimage, scipy_name)(np.array(PICTURE, dtype=float),
                                                                  footprint=footprint))


def test_patch_shapes_with_a_condition_and_refusals(capsys):
    g = grid(PICTURE)
    g.change_patch_shapes("grow", is_above=5)
    assert np.array_equal(g.as_numpy(), ndimage.binary_dilation(np.pad(np.array(PICTURE) > 5, 2, mode="symmetric"),
                                                                SIDES)[2:-2, 2:-2])
    assert "4 yes cells before" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="works on patches"):
        grid(PICTURE).change_patch_shapes("fill holes")
    with pytest.raises(SimplydataError, match="pattern= goes with"):
        grid(RING).change_patch_shapes("grow", pattern=[[1]])
    with pytest.raises(SimplydataError, match="Did you mean"):
        grid(RING).change_patch_shapes("grwo")


# ---------------------------------------------------------------- find_each_patch_that(show=)
def test_patch_show_values_are_scipy_ndimage():
    values = np.array(PICTURE, dtype=float)
    labels, n = ndimage.label(values > 2)
    index = np.arange(1, n + 1)
    table = grid(PICTURE).find_each_patch_that(is_above=2, show=[
        "biggest", "smallest", "where biggest", "where smallest", "median", "standard deviation", "variance", "range",
        "positions", "counts in bins"], bins=3)
    low, high, where_low, where_high = ndimage.extrema(values, labels, index)
    assert np.allclose(column(table, "biggest"), high) and np.allclose(column(table, "smallest"), low)
    assert np.allclose(column(table, "row of biggest"), [r + 1 for r, _ in where_high])
    assert np.allclose(column(table, "column of smallest"), [c + 1 for _, c in where_low])
    assert np.allclose(column(table, "median"), ndimage.median(values, labels, index))
    assert np.allclose(column(table, "standard deviation"), ndimage.standard_deviation(values, labels, index))
    assert np.allclose(column(table, "variance"), ndimage.variance(values, labels, index))
    assert np.allclose(column(table, "range"), ndimage.labeled_comprehension(values, labels, index, np.ptp, float, 0))
    inside = values[labels > 0]  # the bins run over the cells of the patches
    counts = ndimage.histogram(values, inside.min(), inside.max(), 3, labels, index)
    assert np.allclose(column(table, "bin 3"), [c[2] for c in counts])
    assert table.as_pandas()["positions"].iloc[0] == "(2, 2) (2, 3) (3, 2) (3, 3)"
    with pytest.raises(SimplydataError, match="needs bins="):
        grid(PICTURE).find_each_patch_that(is_above=2, show="counts in bins")


# ---------------------------------------------------------------- distances, watershed, moving
@pytest.mark.parametrize("method, theirs", [
    ("straight line", lambda m: ndimage.distance_transform_edt(~m)),
    ("city block", lambda m: ndimage.distance_transform_cdt(~m, metric="taxicab")),
    ("chessboard", lambda m: ndimage.distance_transform_cdt(~m, metric="chessboard")),
    ("brute force", lambda m: ndimage.distance_transform_bf(~m, metric="euclidean"))])
def test_find_distance_to_nearest_is_scipy(method, theirs):
    found = grid(PICTURE).find_distance_to_nearest(is_above=4, test_method=method).as_numpy()
    assert np.allclose(found, theirs(np.array(PICTURE) > 4))


def test_distance_cell_size_and_refusals():
    found = grid(PICTURE).find_distance_to_nearest(is_above=4, cell_size=[2, 1]).as_numpy()
    assert np.allclose(found, ndimage.distance_transform_edt(~(np.array(PICTURE) > 4), sampling=[2, 1]))
    with pytest.raises(SimplydataError, match="nothing to measure"):
        grid(PICTURE).find_distance_to_nearest(is_above=100)
    with pytest.raises(SimplydataError, match="needs a condition"):
        grid(PICTURE).find_distance_to_nearest()


def test_split_touching_patches_is_watershed_ift():
    values = [[1, 2, 9, 2, 1], [1, 3, 9, 3, 1], [1, 2, 9, 2, 1]]
    found = grid(values).split_touching_patches(starting_points=[[2, 1], [2, 5]]).as_numpy()
    markers = np.zeros((3, 5), dtype=np.int32)
    markers[1, 0], markers[1, 4] = 1, 2
    assert np.array_equal(found, ndimage.watershed_ift(np.array(values, dtype=np.uint16), markers, structure=SIDES))
    with pytest.raises(SimplydataError, match="whole numbers from 0 to 65535"):
        grid([[0.5, 1], [2, 3]]).split_touching_patches(starting_points=[[1, 1]])


def test_move_and_stretch_by_is_affine_geometric_or_fourier():
    g = grid(RAMP)
    g.move_and_stretch_by(matrix=[[1, 0.5], [0, 1]], shift=[0, 1])
    theirs = ndimage.affine_transform(G, [[1, 0.5], [0, 1]], offset=[0, 1], order=1, cval=np.nan)
    assert np.allclose(g.as_numpy(), theirs, equal_nan=True)
    g = grid(RAMP)
    g.move_and_stretch_by(rule={"row": "row", "column": "column + 0.5*row"}, test_method="cubic")
    theirs = ndimage.geometric_transform(G, lambda p: (p[0], p[1] + 0.5 * (p[0] + 1)), order=3, cval=np.nan)
    assert np.allclose(g.as_numpy(), theirs, equal_nan=True)
    g = grid(RAMP)
    g.move_and_stretch_by(shift=[0.5, 1], test_method="fourier")
    assert np.allclose(g.as_numpy(), np.fft.ifft2(ndimage.fourier_shift(np.fft.fft2(G), [-0.5, -1])).real)
    with pytest.raises(SimplydataError, match="rule= gives"):
        grid(RAMP).move_and_stretch_by(rule={"row": "row", "column": "column"}, shift=[1, 1])


# ---------------------------------------------------------------- scipy.signal's 2-D names
def test_convolve_with_and_find_envelope_are_scipy_signal():
    g = grid(RAMP)
    g.convolve_with([[0, 1, 0], [1, 4, 1], [0, 1, 0]], keep="same")
    assert np.allclose(g.as_numpy(), signal.convolve2d(G, [[0, 1, 0], [1, 4, 1], [0, 1, 0]], mode="same"))
    g = grid(RAMP)
    g.convolve_with([[1, 2], [0, -1]], flip=False)
    assert np.allclose(g.as_numpy(), signal.correlate2d(G, [[1, 2], [0, -1]]))
    g = grid(RAMP)
    g.convolve_with(row_weights=[1, 2, 1], column_weights=[1, 0, -1])
    assert np.allclose(g.as_numpy(), signal.sepfir2d(G, [1, 2, 1], [1, 0, -1]))
    g = grid(RAMP)
    g.find_envelope()
    assert np.allclose(g.as_numpy(), np.abs(signal.hilbert2(G)))
    with pytest.raises(SimplydataError, match="odd number of weights"):
        grid(RAMP).convolve_with(row_weights=[1, 1], column_weights=[1, 2, 1])


# ---------------------------------------------------------------- batch 21: points (SciPy spatial)
def test_triangles_and_regions_are_scipy_spatial():
    table = sdata.get_example("stations")
    frame = table.as_pandas()
    xy = frame[["east", "north"]].to_numpy(dtype=float)
    triangles = table.find_triangles_between_points(x="east", y="north")
    mesh = Delaunay(xy)
    assert np.array_equal(column(triangles, "corner 1"), mesh.simplices[:, 0] + 1)
    assert np.allclose(column(triangles, "north 3"), xy[mesh.simplices[:, 2], 1])
    found = table.find_triangles_between_points(x="east", y="north",
                                                containing={"east": [4000, 99999], "north": [1000, 0]})
    theirs = mesh.find_simplex(np.array([[4000, 1000], [99999, 0]]))
    assert column(found, "triangle")[0] == theirs[0] + 1 and np.isnan(column(found, "triangle")[1])
    regions = table.find_regions_around_points(x="east", y="north")
    v = Voronoi(xy)
    areas = [np.nan if -1 in v.regions[i] else ConvexHull(v.vertices[v.regions[i]]).volume for i in v.point_region]
    assert np.allclose(column(regions, "area"), areas, equal_nan=True)


def test_regions_on_the_earth_are_spherical_voronoi():
    lon, lat = [0, 90, 180, -90, 0, 0, 45, -120], [0, 0, 0, 0, 90, -90, 30, -40]
    regions = sdata.table({"lon": lon, "lat": lat}).find_regions_around_points(longitude="lon", latitude="lat")
    lo, la = np.radians(lon), np.radians(lat)
    xyz = np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    assert np.allclose(column(regions, "area"), SphericalVoronoi(xyz).calculate_areas() * 6371.0088 ** 2)
    with pytest.raises(SimplydataError, match="too close together"):
        sdata.get_example("stations").find_regions_around_points(longitude="lon", latitude="lat")


def test_minkowski_distances_between_rows():
    table = sdata.get_example("stations")
    table.keep_first_rows(4)
    found = table.find_distances_between_rows(columns=["east", "north"], measure="minkowski", power=3)
    xy = table.as_pandas()[["east", "north"]].to_numpy(dtype=float)
    theirs = cdist(xy, xy, "minkowski", p=3)
    assert np.allclose(found.as_pandas().drop(columns="row").to_numpy(dtype=float), theirs)
    with pytest.raises(SimplydataError, match='power= goes with measure="minkowski"'):
        table.find_distances_between_rows(columns=["east", "north"], power=3)


# ---------------------------------------------------------------- pointers of the 2.8 and 2.9 names
@pytest.mark.parametrize("typed, word", [
    ("scipy.linalg.logm", 'take_matrix_function("log")'), ("linalg.sqrtm", 'take_matrix_function("square root")'),
    ("scipy.linalg.funm", "take_matrix_function("), ("np.linalg.matrix_power", 'take_matrix_function("power"'),
    ("scipy.linalg.fractional_matrix_power", 'take_matrix_function("power"'),
    ("scipy.linalg.issymmetric", "check_if_grid_is"), ("scipy.linalg.bandwidth", 'check_if_grid_is("banded")'),
    ("scipy.linalg.orthogonal_procrustes", "find_best_rotation_to"), ("linalg.subspace_angles", "find_angles_to"),
    ("scipy.linalg.solve_continuous_are", 'solve_matrix_equation("riccati"'),
    ("scipy.linalg.solve_sylvester", 'solve_matrix_equation("sylvester"'),
    ("scipy.linalg.cholesky_banded", 'structure="banded"'),
    ("scipy.linalg.eigh_tridiagonal", 'structure="tridiagonal"'),
    ("scipy.linalg.rq", 'test_method="rq"'), ("scipy.linalg.cossin", 'test_method="cs"'),
    ("scipy.linalg.cdf2rdf", "real eigen blocks"), ("sympy.jordan_form", 'test_method="jordan"'),
    ("scipy.linalg.khatri_rao", "column_by_column=True"), ("scipy.linalg.expm_frechet", "as_numpy()"),
    ("scipy.ndimage.maximum_filter", 'test_method="biggest"'), ("ndimage.rank_filter", 'test_method="rank"'),
    ("ndimage.generic_filter", 'test_method="summary"'), ("ndimage.fourier_gaussian", "fourier gaussian"),
    ("ndimage.sobel", 'find_edges(test_method="sobel")'), ("ndimage.gaussian_laplace", "gaussian laplace"),
    ("ndimage.binary_dilation", 'change_patch_shapes("grow"'), ("ndimage.grey_opening", 'change_patch_shapes("open"'),
    ("ndimage.binary_fill_holes", "fill holes"), ("ndimage.white_tophat", "top hat"),
    ("ndimage.binary_hit_or_miss", "match pattern"), ("ndimage.extrema", "find_each_patch_that"),
    ("ndimage.value_indices", 'show="positions"'), ("ndimage.histogram", "counts in bins"),
    ("ndimage.distance_transform_edt", "find_distance_to_nearest"), ("ndimage.watershed_ift", "split_touching"),
    ("ndimage.affine_transform", "move_and_stretch_by"), ("ndimage.geometric_transform", "rule="),
    ("ndimage.fourier_shift", 'test_method="fourier"'), ("scipy.spatial.Delaunay", "find_triangles_between_points"),
    ("spatial.tsearch", "containing="), ("scipy.spatial.Voronoi", "find_regions_around_points"),
    ("spatial.SphericalVoronoi", "longitude="), ("spatial.minkowski_distance", 'measure="minkowski"'),
    ("spatial.voronoi_plot_2d", "find_regions_around_points"), ("signal.order_filter", 'ends="zeros"'),
    ("signal.hilbert2", "find_envelope"), ("scipy.signal.correlate2d", "flip=False"),
    ("signal.sepfir2d", "row_weights="), ("signal.spline_filter", 'test_method="spline"'),
    ("signal.cspline2d", 'test_method="spline"'), ("signal.firwin_2d", "convolve_with"),
])
def test_every_2_8_and_2_9_name_points_to_its_word(typed, word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert word in out, out


# ---------------------------------------------------------------- review fixes (independent review of full-7)
def test_funm_refuses_a_jordan_block_instead_of_a_wrong_answer():
    with pytest.raises(SimplydataError, match="error estimate"):
        grid([[1, 1], [0, 1]]).take_matrix_function("exp(x)")
    with pytest.raises(SimplydataError, match="Jordan block"):
        grid([[1, 1], [0, 1]]).take_matrix_function("x**2")
    g = grid([[1, 1], [0, 1]])
    g.take_matrix_function("exp")  # SciPy expm itself works on a Jordan block
    assert np.allclose(g.as_numpy(), linalg.expm(np.array([[1.0, 1], [0, 1]])))


def test_matrix_functions_of_singular_grids_are_refused_plainly():
    with pytest.raises(SimplydataError, match="singular"):
        grid([[1, 2], [2, 4]]).take_matrix_function("log")
    with pytest.raises(SimplydataError, match="does not exist"):
        grid([[0, 1], [0, 0]]).take_matrix_function("square root")
    with pytest.raises(SimplydataError, match="singular"):
        grid([[1, 2], [2, 4]]).take_matrix_function("power", power=-1)
    with pytest.raises(SimplydataError, match="does not exist|singular"):
        grid([[0, 1], [0, 0]]).take_matrix_function("power", power=0.5)


def test_binary_laplace_keeps_negative_numbers():
    g = grid(RING)
    g.change_patch_shapes("laplace")
    theirs = ndimage.morphological_laplace(M.astype(np.int16), footprint=SIDES)
    assert np.array_equal(g.as_numpy(), theirs.astype(float)) and g.as_numpy().min() < 0


def test_closing_never_removes_cells_and_shrink_matches_the_grey_picture(capsys):
    full = grid([[1] * 5] * 5)
    full.change_patch_shapes("close")
    assert full.as_numpy().all()
    assert "edge cells are repeated" in capsys.readouterr().out
    edge = np.array(PICTURE) > 5
    for how, grey in (("shrink", "grey_erosion"), ("grow", "grey_dilation"), ("open", "grey_opening"),
                      ("close", "grey_closing")):
        g = grid(PICTURE)
        g.change_patch_shapes(how, is_above=5, by=2)
        theirs = getattr(ndimage, grey)(edge.astype(np.uint8), footprint=ndimage.iterate_structure(SIDES, 2)) > 0
        assert np.array_equal(g.as_numpy(), theirs), how


def test_counts_in_bins_run_over_the_patch_cells_and_ignore_empty_cells(capsys):
    values = [[float("nan"), 1, 2], [0, 8, 9], [0, 0, 0]]
    table = grid(values).find_each_patch_that(is_above=0.5, show="counts in bins", bins=2)
    assert column(table, "bin 1").tolist() == [2] and column(table, "bin 2").tolist() == [2]
    assert "from 1 to 9" in capsys.readouterr().out
    flat = grid([[5, 5], [0, 0]]).find_each_patch_that(is_above=1, show="counts in bins", bins=1)
    assert column(flat, "bin 1").tolist() == [2]
    with pytest.raises(SimplydataError, match="only one bin"):
        grid([[5, 5], [0, 0]]).find_each_patch_that(is_above=1, show="counts in bins", bins=3)


def test_real_eigen_blocks_refuse_a_defective_grid_and_jordan_names_its_own_limit():
    with pytest.raises(SimplydataError, match='test_method="jordan"'):
        grid([[1, 1], [0, 1]]).break_down(test_method="real eigen blocks")
    with pytest.raises(SimplydataError, match="up to") as caught:
        grid(np.eye(9).tolist()).break_down(test_method="jordan")
    assert "exactly=" not in str(caught.value)


def test_best_rotation_says_when_it_is_a_reflection(capsys):
    a = np.array([[1.0, 0], [0, 1], [1, 2]])
    b = a * np.array([1, -1])  # a mirror image
    rotation = grid(a).find_best_rotation_to(grid(b)).as_numpy()
    assert np.linalg.det(rotation) < 0
    out = capsys.readouterr().out
    assert "reflection" in out and "scale" not in out


def test_window_wording_percentile_rounding_and_sepfir_edges(capsys):
    grid(RAMP).smooth(test_method="biggest", window=3)
    assert "a 3 x 3 window (9 cells)" in capsys.readouterr().out
    grid(RAMP).smooth(test_method="percentile", percentile=90, window=3)
    assert "without averaging between cells" in capsys.readouterr().out
    grid(RAMP).smooth(test_method="summary", summary="standard deviation", window=3)
    assert "n in the bottom" in capsys.readouterr().out
    grid(RAMP).convolve_with(row_weights=[1, 2, 1], column_weights=[1, 2, 1])
    out = capsys.readouterr().out
    assert "reflect" in out and "mirrored" not in out


def test_convolve_overlap_with_a_kernel_too_big_and_a_repeated_starting_point():
    with pytest.raises(SimplydataError, match="never fits"):
        grid(RAMP).convolve_with(np.ones((2, 6)).tolist(), keep="overlap")
    with pytest.raises(SimplydataError, match="more than once"):
        grid([[1, 2, 9], [1, 2, 9]]).split_touching_patches(starting_points=[[1, 1], [1, 1]])


def test_triangles_and_minkowski_use_the_current_scipy_calls():
    import inspect

    from simplydata.table import patterns, point_words

    assert "tsearch(" not in inspect.getsource(point_words) and "find_simplex" in inspect.getsource(point_words)
    assert "minkowski_distance(" not in inspect.getsource(patterns)


def test_correlate1d_points_to_a_correlation(capsys):
    sdata.help("scipy.ndimage.correlate1d")
    out = capsys.readouterr().out
    assert "reverse()" in out and "flip=False" in out
