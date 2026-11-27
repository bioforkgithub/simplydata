"""Numbers finishing (P41 and the designed matrix words): grid.solve_for and grid.break_down against SciPy and SymPy."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import linalg, optimize

import simplydata as sdata
from simplydata import SimplydataError

SQUARE = [[4.0, 3.0, 2.0], [3.0, 5.0, 1.0], [2.0, 1.0, 6.0]]
TALL = [[1.0, 1.0], [1.0, 2.0], [1.0, 3.0], [1.0, 4.0]]


# ---------------------------------------------------------------- solve_for
def test_a_square_grid_is_solved_by_scipy_linalg_solve(capsys):
    x = sdata.number_grid(SQUARE).solve_for([1, 2, 3])
    assert np.allclose(x.as_numpy(), linalg.solve(np.array(SQUARE), [1, 2, 3]), rtol=1e-13)
    assert "SciPy linalg.solve" in capsys.readouterr().out
    assert type(x).__name__ == "Numbers"


def test_a_grid_that_is_not_square_gives_least_squares_and_says_so(capsys):
    x = sdata.number_grid(TALL).solve_for([6, 5, 7, 10])
    assert np.allclose(x.as_numpy(), linalg.lstsq(np.array(TALL), [6, 5, 7, 10])[0], rtol=1e-13)
    out = capsys.readouterr().out
    assert "least-squares answer" in out and "more equations than unknowns" in out and "linalg.lstsq" in out


def test_fewer_equations_than_unknowns_gives_the_shortest_answer(capsys):
    x = sdata.number_grid([[1, 1, 1]]).solve_for([3])
    assert np.allclose(x.as_numpy(), [1, 1, 1])
    out = capsys.readouterr().out
    assert "fewer equations than unknowns" in out and "shortest" in out


def test_a_singular_square_grid_is_refused_and_with_best_fit_gives_the_shortest_answer(capsys):
    grid = sdata.number_grid([[1, 2], [2, 4]])
    with pytest.raises(SimplydataError, match="with_best_fit=True"):
        grid.solve_for([1, 2])
    x = grid.solve_for([1, 2], with_best_fit=True)
    assert np.allclose(x.as_numpy(), linalg.lstsq(np.array([[1, 2], [2, 4]], float), [1, 2])[0])
    assert "rank 1 of 2" in capsys.readouterr().out


def test_b_may_be_a_grid_with_one_right_side_in_each_column():
    b = [[1, 4], [2, 5], [3, 6]]
    x = sdata.number_grid(SQUARE).solve_for(sdata.number_grid(b))
    assert type(x).__name__ == "NumberGrid"
    assert np.allclose(x.as_numpy(), linalg.solve(np.array(SQUARE), np.array(b, float)))


def test_between_zero_and_none_is_nnls(capsys):
    a = np.array([[2, 0, 1], [1, 1, 0], [0, 3, 1], [1, 0, 2]], float)
    b = [4, 1, 2, -5]
    x = sdata.number_grid(a.tolist()).solve_for(b, between=[0, None])
    assert np.allclose(x.as_numpy(), optimize.nnls(a, b)[0], atol=1e-12)
    assert (x.as_numpy() >= 0).all()
    out = capsys.readouterr().out
    assert "optimize.nnls" in out and "at a limit" in out


def test_other_limits_are_lsq_linear_bvls(capsys):
    a = np.array(TALL)
    x = sdata.number_grid(TALL).solve_for([6, 5, 7, 10], between=[0, 2])
    assert np.allclose(x.as_numpy(), optimize.lsq_linear(a, [6, 5, 7, 10], bounds=(0, 2), method="bvls").x)
    assert "lsq_linear" in capsys.readouterr().out
    x = sdata.number_grid(TALL).solve_for([6, 5, 7, 10], between=[None, 1])
    assert np.allclose(x.as_numpy(), optimize.lsq_linear(a, [6, 5, 7, 10], bounds=(-np.inf, 1), method="bvls").x)


@pytest.mark.parametrize("between", [[1], [2, 1], [None, None], ["a", 2], 5])
def test_wrong_limits_are_refused(between):
    with pytest.raises(SimplydataError, match="between="):
        sdata.number_grid(TALL).solve_for([6, 5, 7, 10], between=between)


def test_exactly_gives_sympy_fractions(capsys):
    x = sdata.number_grid([[2, 1], [1, 3]]).solve_for([1, 1], exactly=True)
    assert np.allclose(x.as_numpy(), [0.4, 0.2], rtol=1e-15)
    assert "[2/5, 1/5]" in capsys.readouterr().out
    x = sdata.number_grid(TALL).solve_for([6, 5, 7, 10], exactly=True)
    assert np.allclose(x.as_numpy(), [3.5, 1.4], rtol=1e-15)
    assert "7/2, 7/5" in capsys.readouterr().out


def test_exactly_refuses_a_singular_grid_and_limits():
    with pytest.raises(SimplydataError, match="exactly 0"):
        sdata.number_grid([[1, 2], [2, 4]]).solve_for([1, 2], exactly=True)
    with pytest.raises(SimplydataError, match="does not go with between="):
        sdata.number_grid(TALL).solve_for([1, 2, 3, 4], between=[0, None], exactly=True)


def test_solve_for_checks_its_right_side():
    grid = sdata.number_grid(SQUARE)
    with pytest.raises(SimplydataError, match="needs the right side b"):
        grid.solve_for()
    with pytest.raises(SimplydataError, match="one number for each row"):
        grid.solve_for([1, 2])
    with pytest.raises(SimplydataError, match="every place of b"):
        grid.solve_for([1, float("nan"), 2])
    with pytest.raises(SimplydataError, match="True or False"):
        grid.solve_for([1, 2, 3], exactly="yes")


def test_solve_for_leaves_the_grid_as_it_was():
    grid = sdata.number_grid(SQUARE)
    grid.solve_for([1, 2, 3])
    assert np.array_equal(grid.as_numpy(), np.array(SQUARE))


# ---------------------------------------------------------------- break_down
def _parts(method, grid=SQUARE, **options):
    parts = sdata.number_grid(grid).break_down(test_method=method, **options)
    return {k: v.as_numpy() for k, v in parts.items()}


def test_the_default_is_the_short_svd():
    a = np.array(TALL)
    parts = sdata.number_grid(TALL).break_down()
    u, s, vt = linalg.svd(a, full_matrices=False)
    assert list(parts) == ["U", "singular values", "Vt"]
    assert type(parts["singular values"]).__name__ == "Numbers"
    assert np.allclose(parts["U"].as_numpy(), u) and np.allclose(parts["singular values"].as_numpy(), s)
    assert np.allclose(parts["Vt"].as_numpy(), vt)


@pytest.mark.parametrize("method, call, names", [
    ("qr", lambda a: linalg.qr(a, mode="economic"), ["Q", "R"]),
    ("lu", linalg.lu, ["P", "L", "U"]),
    ("cholesky", lambda a: (linalg.cholesky(a),), ["U"]),
    ("schur", lambda a: linalg.schur(a, output="real"), ["T", "Z"]),
    ("polar", linalg.polar, ["U", "P"]),
    ("hessenberg", lambda a: linalg.hessenberg(a, calc_q=True), ["H", "Q"]),
])
def test_each_method_is_scipy_linalg(method, call, names, capsys):
    parts = _parts(method)
    assert list(parts) == names
    for got, want in zip(parts.values(), call(np.array(SQUARE))):
        assert np.allclose(got, want, rtol=1e-13, atol=1e-13)
    out = capsys.readouterr().out
    assert "SciPy linalg." in out and all(f"  {n}:" in out for n in names)


def test_ldl_gives_its_row_order_counted_from_1():
    low, d, order = linalg.ldl(np.array(SQUARE))
    parts = _parts("ldl")
    assert np.allclose(parts["L"], low) and np.allclose(parts["D"], d)
    assert np.array_equal(parts["row order"], order + 1)


def test_qz_needs_the_other_grid():
    b = [[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]]
    parts = _parts("qz", together_with=b)
    for got, want in zip(parts.values(), linalg.qz(np.array(SQUARE), np.array(b), output="real")):
        assert np.allclose(got, want)
    with pytest.raises(SimplydataError, match="together_with="):
        sdata.number_grid(SQUARE).break_down(test_method="qz")
    with pytest.raises(SimplydataError, match="together_with="):
        sdata.number_grid(SQUARE).break_down(test_method="lu", together_with=b)
    with pytest.raises(SimplydataError, match="same size"):
        sdata.number_grid(SQUARE).break_down(test_method="qz", together_with=[[1, 0], [0, 1]])


def test_break_down_refuses_grids_that_do_not_fit():
    with pytest.raises(SimplydataError, match="symmetric"):
        sdata.number_grid([[1, 2], [3, 4]]).break_down(test_method="cholesky")
    with pytest.raises(SimplydataError, match="positive definite"):
        sdata.number_grid([[1, 2], [2, 1]]).break_down(test_method="cholesky")
    with pytest.raises(SimplydataError, match="square grid"):
        sdata.number_grid(TALL).break_down(test_method="schur")
    with pytest.raises(SimplydataError, match='Did you mean test_method="lu"'):
        sdata.number_grid(SQUARE).break_down(test_method="luu")


def test_the_parts_multiply_back_to_the_grid():
    a = np.array(SQUARE)
    p = _parts("svd")
    assert np.allclose(p["U"] @ np.diag(p["singular values"]) @ p["Vt"], a)
    p = _parts("lu")
    assert np.allclose(p["P"] @ p["L"] @ p["U"], a)
    p = _parts("cholesky")
    assert np.allclose(p["U"].T @ p["U"], a)


def test_other_names_point_to_the_new_words():
    from simplydata._errors import MissingWordError

    grid = sdata.number_grid(SQUARE)
    for name, word in [("lstsq", "solve_for"), ("nnls", "solve_for"), ("svd", "break_down"), ("qr", "break_down"),
                       ("cholesky", "break_down"), ("schur", "break_down")]:
        with pytest.raises(MissingWordError, match=word):
            getattr(grid, name)


def test_help_has_an_example_for_both(capsys):
    sdata.help("grid.solve_for")
    sdata.help("grid.break_down")
    out = capsys.readouterr().out
    assert "between=[0, None]" in out and 'test_method="cholesky"' in out
