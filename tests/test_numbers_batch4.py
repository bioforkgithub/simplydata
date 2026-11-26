"""Numbers phase, batch 4 (approved by Manish 2026-11-26): the SymPy words.

Each answer is compared with SymPy (or SciPy) doing the same, and with the answer worked out by hand where there is
one. The time limit is tested with a SymPy call that really does not finish, and the helper process is checked to be
gone when Python exits, even when Python is stopped without a goodbye.
"""

from __future__ import annotations

import math
import operator
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import numpy as np
import pytest

import simplydata as sdata
from simplydata import _time_limit

pytestmark = pytest.mark.usefixtures("needs_sympy")
SRC = Path(__file__).resolve().parents[1] / "src"


def _sp():
    import sympy as sp

    return sp, sp.Symbol("x")


def _listed(table, column) -> list:
    """A column as a plain list (a column of numbers comes back as sdata.numbers, any other as a list)."""
    found = table.get_column(column)
    return found if isinstance(found, list) else found.as_numpy().tolist()


# ---------------------------------------------------------------- P1: slopes
def test_slope_how_many_times_and_mixed_slopes_are_sympy_diff(capsys):
    sp, x = _sp()
    y = sp.Symbol("y")
    third = sdata.formula("sin(x)").find_slope_formula(how_many_times=3)
    assert third._expr == sp.diff(sp.sin(x), x, 3) == -sp.cos(x)
    assert "3 times over: -cos(x)   (the 3rd derivative; SymPy diff)" in capsys.readouterr().out
    mixed = sdata.formula("x**2 * y**3").find_slope_formula(for_letter=["x", "y"])
    assert mixed._expr == sp.diff(x ** 2 * y ** 3, x, y) == 6 * x * y ** 2
    assert "mixed partial derivative" in capsys.readouterr().out
    twice = sdata.formula("x**2 * y**3").find_slope_formula(for_letter=["y", "y"])
    assert twice._expr == sp.diff(x ** 2 * y ** 3, y, 2)
    assert sdata.formula("x**5").find_slope_formula(how_many_times=2)._expr == 20 * x ** 3


@pytest.mark.parametrize("call, problem", [
    (lambda f: f.find_slope_formula(how_many_times=0), "whole number from 1 to 20"),
    (lambda f: f.find_slope_formula(how_many_times=21), "whole number from 1 to 20"),
    (lambda f: f.find_slope_formula(how_many_times=2.5), "whole number"),
    (lambda f: f.find_slope_formula(how_many_times=True), "whole number"),
    (lambda f: f.find_slope_formula(for_letter=["x", "y"], how_many_times=2), "works with one letter"),
    (lambda f: f.find_slope_formula(for_letter=["x", "z"]), "one of the letters"),
    (lambda f: f.find_slope_formula(for_letter=[]), "list of 1 to 20"),
    (lambda f: f.find_slope_formula(for_letter=["__import__('os')"]), "one of the letters"),
])
def test_slope_options_are_checked(call, problem):
    with pytest.raises(sdata.SimplydataError, match=problem):
        call(sdata.formula("x**2 * y"))


# ---------------------------------------------------------------- P2: one-sided limits
def test_limit_from_one_side_is_sympy_dir(capsys):
    sp, x = _sp()
    f = sdata.formula("1/x")
    assert f.find_limit_as("x", goes_to=0, from_side="above") == math.inf
    assert "from above" in capsys.readouterr().out
    assert f.find_limit_as("x", goes_to=0, from_side="below") == -math.inf
    g = sdata.formula("abs(x) / x")
    for side, sign, value in [("above", "+", 1.0), ("right", "+", 1.0), ("+", "+", 1.0), ("below", "-", -1.0),
                              ("left", "-", -1.0), ("-", "-", -1.0)]:
        assert g.find_limit_as("x", goes_to=0, from_side=side) == float(sp.limit(sp.Abs(x) / x, x, 0, dir=sign)) == value
    with pytest.raises(sdata.SimplydataError, match='from_side="above"'):  # both sides differ: points to from_side=
        g.find_limit_as("x", goes_to=0)


def test_limit_from_side_is_checked():
    f = sdata.formula("1/x")
    with pytest.raises(sdata.SimplydataError, match="does not know from_side"):
        f.find_limit_as("x", goes_to=0, from_side="up")
    with pytest.raises(sdata.SimplydataError, match="only one side"):
        f.find_limit_as("x", goes_to="infinity", from_side="below")


# ---------------------------------------------------------------- P3, P4, P5: decimal, grouping, partial fractions
def test_show_as_decimal_is_sympy_n(capsys):
    sp, _ = _sp()
    text = sdata.formula("sqrt(2)").show_as_decimal(digits=50)
    assert text == str(sp.N(sp.sqrt(2), 50)) == "1.4142135623730950488016887242096980785696718753769"
    assert text in capsys.readouterr().out
    assert sdata.formula("pi").show_as_decimal() == str(sp.N(sp.pi, 15))
    assert sdata.formula("x**2").put_in(x=3).show_as_decimal(digits=3) == "9.00"
    with pytest.raises(sdata.SimplydataError, match="still has letters"):
        sdata.formula("x + 1").show_as_decimal()
    with pytest.raises(sdata.SimplydataError, match="from 1 to 10,000"):
        sdata.formula("sqrt(2)").show_as_decimal(digits=10_001)
    with pytest.raises(sdata.SimplydataError, match="no value among the ordinary numbers"):
        sdata.formula("1/(1 - 1)").show_as_decimal()


def test_group_by_powers_of_is_expand_then_collect(capsys):
    sp, x = _sp()
    a, b = sp.symbols("a b")
    f = sdata.formula("a*x**2 + b*x**2 + a*x - x")
    f.group_by_powers_of("x")
    assert f._expr == sp.collect(sp.expand(a * x ** 2 + b * x ** 2 + a * x - x), x) == x ** 2 * (a + b) + x * (a - 1)
    assert "grouped by powers of x" in capsys.readouterr().out
    f.undo()
    assert f._expr == a * x ** 2 + b * x ** 2 + a * x - x
    g = sdata.formula("(a + x)*(b + x) - x").group_by_powers_of("x")  # brackets are multiplied out first
    assert g._expr == sp.collect(sp.expand((a + x) * (b + x) - x), x)
    with pytest.raises(sdata.SimplydataError, match="one of the letters"):
        sdata.formula("a*x").group_by_powers_of("z")


def test_partial_fractions_is_sympy_apart():
    sp, x = _sp()
    f = sdata.formula("(3*x + 5) / ((x + 1)*(x + 2))").turn_into_partial_fractions()
    assert f._expr == sp.apart((3 * x + 5) / ((x + 1) * (x + 2)), x) == 1 / (x + 2) + 2 / (x + 1)
    f.undo()
    assert f._expr == (3 * x + 5) / ((x + 1) * (x + 2))
    with pytest.raises(sdata.SimplydataError, match="fraction of polynomials"):
        sdata.formula("sin(x) / (x + 1)").turn_into_partial_fractions()
    with pytest.raises(sdata.SimplydataError, match="for_letter="):
        sdata.formula("1 / ((x + a)*(x + 1))").turn_into_partial_fractions()
    a = sp.Symbol("a")
    found = sdata.formula("1 / ((x + a)*(x + 1))").turn_into_partial_fractions(for_letter="x")
    assert found._expr == sp.apart(1 / ((x + a) * (x + 1)), x)


@pytest.mark.parametrize("word", ["turn_into_sum", "group_by_powers_of", "turn_into_partial_fractions"])
def test_a_sum_with_letters_to_a_big_power_is_refused_before_expand(word):
    f = sdata.formula("(x + y + z + 1)**200" if word != "turn_into_partial_fractions" else "1/(x + 1)**101")
    with pytest.raises(sdata.SimplydataError, match="far too many terms"):
        getattr(f, word)(*(["x"] if word == "group_by_powers_of" else []))
    sdata.formula("(x + 1)**100").turn_into_sum()  # up to 100 is fine
    sdata.formula("x**500").turn_into_sum()  # a single letter to a big power is nothing to multiply out


# ---------------------------------------------------------------- P6: letters_are=
def test_letters_are_gives_sympy_assumptions(capsys):
    sp, _ = _sp()
    k, t = sp.symbols("k t", positive=True)
    f = sdata.formula("sqrt(k**2) + log(k*t)", letters_are={"k": "positive", "t": "positive"})
    assert "letters k (positive), t (positive)" in capsys.readouterr().out
    assert f._expr == sp.sqrt(k ** 2) + sp.log(k * t) == k + sp.log(k * t)
    assert f.turn_into_sum()._expr == sp.expand(k + sp.log(k * t)) == k + sp.log(k) + sp.log(t)
    assert "k (positive)" in repr(f)
    plain = sdata.formula("sqrt(k**2)")
    assert plain._expr != sp.Symbol("k")  # without the option SymPy may not drop the root
    n = sdata.formula("cos(pi*n)", letters_are={"n": "whole number"})
    assert n.make_simpler()._expr == (-1) ** sp.Symbol("n", integer=True)
    # the letters keep what they are through the other words
    assert f.find_slope_formula(for_letter="k").find_value_at(k=2) == pytest.approx(1.5)
    assert f.put_in(t=1)._expr == k + sp.log(k)
    assert f.find_value_at(k=2, t=3) == pytest.approx(2 + math.log(6))


@pytest.mark.parametrize("option, problem", [
    ({"q": "positive"}, "not a letter of the formula"), ({"k": "huge"}, "does not know letters_are for k"),
    ("positive", "dict of letter"), ({}, "dict of letter"), ({"k": 1}, "does not know"),
    ({"__import__('os')": "positive"}, "not a letter of the formula"),
])
def test_letters_are_is_checked_against_the_letters_and_a_fixed_list(option, problem):
    with pytest.raises(sdata.SimplydataError, match=problem):
        sdata.formula("sqrt(k**2)", letters_are=option)


def test_letters_are_spellings():
    sp, _ = _sp()
    assert sdata.formula("k", letters_are={"k": "non-negative"})._expr.is_nonnegative
    assert sdata.formula("k", letters_are={"k": "integer"})._expr.is_integer
    assert sdata.formula("k", letters_are={"k": "positive whole number"})._expr.is_positive


# ---------------------------------------------------------------- P7, P8, P9: solve
def test_solve_for_one_letter_keeps_the_others(capsys):
    sp, _ = _sp()
    p, V, n, R, T = sp.symbols("p V n R T")
    found = sdata.solve("p*V = n*R*T", for_letter="T", exactly=True)
    assert _listed(found, "T exactly") == [str(s[T]) for s in sp.solve([sp.Eq(p * V, n * R * T)], [T],
                                                                                    dict=True)] == ["V*p/(R*n)"]
    assert found.get_cell_at(row=1, column="T") is None  # an empty decimal
    out = capsys.readouterr().out
    assert "T = V*p/(R*n)" in out and "stay letters" in out
    with pytest.raises(sdata.SimplydataError, match="not a letter of the equations"):
        sdata.solve("p*V = n*R*T", for_letter="Q", exactly=True)
    with pytest.raises(sdata.SimplydataError, match="for_letter="):  # still more letters than equations
        sdata.solve("p*V = n*R*T", exactly=True)
    two = sdata.solve(["x + y = a", "x - y = b"], for_letter=["x", "y"], exactly=True)
    assert _listed(two, "x exactly") == ["a/2 + b/2"]


def test_solve_for_letter_without_exactly_needs_the_others_known():
    found = sdata.solve("p*V = n*R*T", for_letter="T", known={"p": 101325, "V": 0.0224, "n": 1, "R": 8.314},
                        between=[0, 1000])
    assert found.get_cell_at(row=1, column="T") == pytest.approx(101325 * 0.0224 / 8.314)
    with pytest.raises(sdata.SimplydataError, match="exactly=True"):
        sdata.solve("p*V = n*R*T", for_letter="T", between=[0, 1000])


def test_solve_letters_are(capsys):
    sp, _ = _sp()
    c = sp.Symbol("c", positive=True)
    found = sdata.solve("c**2 = 4", exactly=True, letters_are={"c": "positive"})
    assert _listed(found, "c exactly") == [str(s[c]) for s in sp.solve([sp.Eq(c ** 2, 4)], [c],
                                                                                    dict=True)] == ["2"]
    assert "These are all the solutions" in capsys.readouterr().out
    assert sdata.solve("c**2 = 4", exactly=True).count_rows() == 2
    with pytest.raises(sdata.SimplydataError, match="works with exactly=True"):
        sdata.solve("c**2 = 4", between=[0, 3], letters_are={"c": "positive"})


def test_solve_rules_are_sympy_solveset_over_the_reals(capsys):
    sp, x = _sp()
    found = sdata.solve("x**2 - 4 > 0", exactly=True)
    whole = sp.solveset(x ** 2 - 4 > 0, x, sp.S.Reals)
    assert _listed(found, "to exactly") == [str(piece.end).replace("oo", "infinity") for piece in whole.args] == [
        "-2", "infinity"]
    assert _listed(found, "from") == [-math.inf, 2.0]
    assert _listed(found, "includes to") == [False, False]
    assert "x**2 - 4 > 0 when x < -2 or x > 2   (SymPy solveset over the real numbers)" in capsys.readouterr().out
    closed = sdata.solve("x**2 <= 9", exactly=True)
    assert _listed(closed, "from") == [-3.0] and _listed(closed, "includes from") == [True]
    several = sdata.solve(["x > 1", "x <= 3"], exactly=True)
    reduced = sp.reduce_inequalities([x > 1, x <= 3], x).as_set()
    assert (several.get_cell_at(row=1, column="from"), several.get_cell_at(row=1, column="to")) == (
        float(reduced.start), float(reduced.end)) == (1.0, 3.0)
    assert "1 < x <= 3" in capsys.readouterr().out
    point = sdata.solve("x**2 <= 0", exactly=True)
    assert _listed(point, "from") == [0.0] == _listed(point, "to")
    never = sdata.solve("x**2 < 0", exactly=True)
    assert "is never true" in capsys.readouterr().out and never.get_cell_at(row=1, column="from") is None
    with pytest.raises(sdata.SimplydataError, match="not both at once"):
        sdata.solve(["x = 1", "x > 0"], exactly=True)
    with pytest.raises(sdata.SimplydataError, match="in one letter"):
        sdata.solve("x + y > 0", exactly=True)
    with pytest.raises(sdata.SimplydataError, match="works with = only.*exactly=True"):
        sdata.solve("x**2 - 4 > 0", between=[0, 3])


def test_a_formula_means_formula_equals_zero(capsys):
    sp, x = _sp()
    f = sdata.formula("x**3 - 3*x")
    found = sdata.solve(f.find_slope_formula(), exactly=True)
    assert _listed(found, "x") == [-1.0, 1.0]
    assert "3*x**2 - 3 = 0 when x = -1 or x = 1" in capsys.readouterr().out
    numeric = sdata.solve(f.find_slope_formula(), between=[0, 3])
    assert numeric.get_cell_at(row=1, column="x") == pytest.approx(1.0)
    k = sdata.formula("k**2 - 4", letters_are={"k": "positive"})
    assert _listed(sdata.solve(k, exactly=True), "k") == [2.0]  # the letter keeps what it is
    assert _listed(sdata.solve([sdata.formula("x + y - 3"), "x - y = 1"], exactly=True), "y") == [1.0]


def test_draw_curve_takes_a_formula(tmp_path):
    f = sdata.formula("x**3 - 3*x")
    chart = sdata.chart()
    chart.draw_curve(f, between=[-2, 2])
    chart.save(str(tmp_path / "curve.png"))
    assert (tmp_path / "curve.png").stat().st_size > 0
    line = chart._render().axes[0].get_lines()[0]
    xs, ys = line.get_data()
    assert np.allclose(ys, xs ** 3 - 3 * xs)


# ---------------------------------------------------------------- P10: sums of series
def test_sum_of_series_is_sympy_summation(capsys):
    sp, _ = _sp()
    k, n = sp.Symbol("k", integer=True), sp.Symbol("n", integer=True)
    basel = sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])
    assert basel._expr == sp.summation(1 / k ** 2, (k, 1, sp.oo)) == sp.pi ** 2 / 6
    assert "pi**2/6 (about 1.644934067)   (SymPy summation)" in capsys.readouterr().out
    assert sdata.find_sum_of_series("k", between=[1, "n"])._expr == sp.summation(k, (k, 1, n)) == n ** 2 / 2 + n / 2
    assert sdata.find_sum_of_series("1/2**k", between=[0, "infinity"])._expr == 2
    assert sdata.find_sum_of_series("k**2", between=[1, 10])._expr == 385
    big = sdata.find_sum_of_series("k**2", between=[1, 10**9])  # never added term by term
    assert big._expr == sp.Integer(10**9) * (10**9 + 1) * (2 * 10**9 + 1) / 6


def test_sum_of_series_says_when_it_does_not_settle(capsys):
    sp, _ = _sp()
    assert sdata.find_sum_of_series("1/k", between=[1, "infinity"]) == math.inf
    assert "grows without end" in capsys.readouterr().out
    assert math.isnan(sdata.find_sum_of_series("(-1)**k", between=[0, "infinity"]))
    assert "does not settle" in capsys.readouterr().out
    k = sp.Symbol("k", integer=True)
    settles = sdata.find_sum_of_series("1/(k**3 + k + 1)", between=[1, "infinity"])
    assert settles == pytest.approx(float(sp.Sum(1 / (k ** 3 + k + 1), (k, 1, sp.oo)).evalf()), rel=1e-12)
    assert "no exact formula; it settles at about 0.49472" in capsys.readouterr().out
    geometric = sdata.find_sum_of_series("r**k", between=[0, "infinity"], for_letter="k")
    assert str(geometric) == "Piecewise((1/(1 - r), Abs(r) < 1), (nan, True))"
    assert "when Abs(r) < 1; otherwise it does not settle" in capsys.readouterr().out
    assert sdata.find_sum_of_series("r**k", between=[0, "infinity"], for_letter="k", known={"r": 0.5})._expr == 2


@pytest.mark.parametrize("kwargs, problem", [
    ({"between": [1]}, "first and the last"), ({"between": [1.5, 3]}, "whole numbers"),
    ({"between": [5, 1]}, "smaller end"), ({"between": [1, "__import__('os')"]}, "not a function"),
    ({"between": [1, "n + 1"]}, "whole numbers"), ({"between": [1, "k"]}, "letter that counts"),
    ({"between": [1, 10], "for_letter": "q"}, "one of the letters"),
])
def test_sum_of_series_checks_its_options(kwargs, problem):
    with pytest.raises(sdata.SimplydataError, match=problem):
        sdata.find_sum_of_series("1/k**2", **kwargs)


def test_a_long_finite_sum_without_a_formula_is_refused():
    with pytest.raises(sdata.SimplydataError, match="does not add more than 10,000 terms"):
        sdata.find_sum_of_series("log(k)/k**2", between=[1, 10**9])


# ---------------------------------------------------------------- P11, P12: volumes and paths exactly
def test_volume_exactly_is_sympy_integrate_inner_letter_first(capsys):
    sp, _ = _sp()
    x, y = sp.symbols("x y")
    v = sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]}, exactly=True)
    assert v._expr == sp.integrate(x * y ** 2, (y, 0, 2), (x, 0, 1)) == sp.Rational(4, 3)
    assert "y first (the inner letter)" in capsys.readouterr().out
    triangle = sdata.find_volume_under("x + y + z", between={"x": [0, 1], "y": [0, 1], "z": [0, 1]}, exactly=True)
    assert triangle._expr == sp.Rational(3, 2)
    assert sdata.find_volume_under("exp(-x**2 - y**2)", between={"x": ["-infinity", "infinity"],
                                                                 "y": ["-infinity", "infinity"]},
                                   exactly=True)._expr == sp.pi
    with pytest.raises(sdata.SimplydataError, match="does not settle|infinite"):
        sdata.find_volume_under("1/(x*y)", between={"x": [0, 1], "y": [0, 1]}, exactly=True)


def test_path_general_formula_and_second_order(capsys):
    sp, _ = _sp()
    t, r, C1, C2 = sp.symbols("t r C1 C2")
    N, X = sp.Function("N"), sp.Function("x")
    general = sdata.find_path_over_time("dN/dt = r * N", exactly=True)
    assert general._expr == sp.simplify(sp.dsolve(sp.Eq(N(t).diff(t), r * N(t)), N(t)).rhs) == C1 * sp.exp(r * t)
    assert "C1 is a constant" in capsys.readouterr().out
    spring = sdata.find_path_over_time("d2x/dt2 = -k*x", at_start={"x": 1, "dx/dt": 0}, known={"k": 4},
                                       exactly=True)
    assert spring._expr == sp.cos(2 * t)
    free = sdata.find_path_over_time("d^2x/dt^2 = -k*x", known={"k": 4}, exactly=True)
    assert free._expr == C1 * sp.sin(2 * t) + C2 * sp.cos(2 * t)
    assert "C1 and C2 are constants" in capsys.readouterr().out
    damped = sdata.find_path_over_time("d2x/dt2 = -k*x - c*dx/dt", at_start={"x": 1, "dx/dt": 0},
                                       known={"k": 4, "c": 1}, exactly=True)
    solved = sp.dsolve(sp.Eq(X(t).diff(t, 2), -4 * X(t) - X(t).diff(t)), X(t),
                       ics={X(0): 1, X(t).diff(t).subs(t, 0): 0})
    assert sp.simplify(damped._expr - solved.rhs) == 0


def test_second_order_in_numbers_is_two_first_order_equations():
    from scipy.integrate import solve_ivp

    path = sdata.find_path_over_time("d2x/dt2 = -k*x - c*dx/dt", at_start={"x": 1, "dx/dt": 0}, between=[0, 10],
                                     known={"k": 4, "c": 0.5}, time_step=0.5)
    assert path.get_column_names() == ["time", "x", "dx/dt"]
    s = solve_ivp(lambda t, y: [y[1], -4 * y[0] - 0.5 * y[1]], (0, 10), [1, 0], t_eval=np.linspace(0, 10, 21),
                  rtol=1e-6, atol=1e-6)
    assert np.allclose(path.get_column("x").as_numpy(), s.y[0], rtol=0, atol=1e-12)
    assert np.allclose(path.get_column("dx/dt").as_numpy(), s.y[1], rtol=0, atol=1e-12)
    w = math.sqrt(4 - 0.0625)
    assert path.get_cell_at(row=21, column="x") == pytest.approx(
        math.exp(-2.5) * (math.cos(10 * w) + 0.25 / w * math.sin(10 * w)), abs=1e-4)


@pytest.mark.parametrize("kwargs, problem", [
    ({"equations": ["d2x/dt2 = -x", "dy/dt = y"], "at_start": {"x": 1, "dx/dt": 0, "y": 1}, "between": [0, 1]},
     "works on its own"),
    ({"equations": "d2x/dt2 = -x", "at_start": {"x": 1}, "between": [0, 1]}, "missing: dx/dt"),
    ({"equations": "d2x/dt2 = -dx_dt", "at_start": {"x": 1, "dx/dt": 0}, "between": [0, 1]}, "use another letter"),
    ({"equations": "dN/dt = r * N", "between": [0, 1], "known": {"r": 0.3}}, "general formula"),
])
def test_path_options_are_checked(kwargs, problem):
    with pytest.raises(sdata.SimplydataError, match=problem):
        sdata.find_path_over_time(**kwargs)


# ---------------------------------------------------------------- P13: the matrix words
GRID = [[4, 3, 2], [3, 5, 1], [2, 1, 6]]


def test_determinant_inverse_and_eigenvalues_are_scipy(capsys):
    from scipy import linalg

    g = np.array(GRID, dtype=float)
    assert sdata.number_grid(GRID).find_determinant() == float(linalg.det(g))
    grid = sdata.number_grid(GRID)
    grid.take_inverse()
    assert np.array_equal(grid.as_numpy(), linalg.inv(g))
    grid.undo()
    assert np.array_equal(grid.as_numpy(), g)
    values = sdata.number_grid(GRID).find_eigenvalues()
    assert np.array_equal(values.get_column("eigenvalue").as_numpy(), linalg.eigvalsh(g)[::-1])
    assert "eigvalsh, for a symmetric grid" in capsys.readouterr().out
    turn = sdata.number_grid([[0, -1], [1, 0]]).find_eigenvalues()
    assert _listed(turn, "imaginary part") == [1.0, -1.0]
    assert "linalg.eigvals, ordered by size (modulus) as R eigen()" in capsys.readouterr().out


def test_matrix_words_refuse_what_has_no_answer():
    with pytest.raises(sdata.SimplydataError, match="has no inverse"):
        sdata.number_grid([[1, 2], [2, 4]]).take_inverse()
    with pytest.raises(sdata.SimplydataError, match="exactly 0"):
        sdata.number_grid([[1, 2], [2, 4]]).take_inverse(exactly=True)
    with pytest.raises(sdata.SimplydataError, match="square grid"):
        sdata.number_grid([[1, 2, 3], [4, 5, 6]]).find_determinant()
    with pytest.raises(sdata.SimplydataError, match="up to 6 rows"):
        sdata.number_grid(np.eye(7).tolist()).find_eigenvalues(exactly=True)
    with pytest.raises(sdata.SimplydataError, match="up to 12 rows"):
        sdata.number_grid(np.eye(13).tolist()).find_determinant(exactly=True)
    with pytest.raises(sdata.SimplydataError, match="True or False"):
        sdata.number_grid(GRID).find_determinant(exactly="yes")


def test_matrix_words_exactly_are_sympy_matrix(capsys):
    sp, _ = _sp()
    d = sdata.number_grid([[0.5, 0.25], [0.2, 0.4]]).find_determinant(exactly=True)
    assert d._expr == sp.Matrix([[sp.Rational(1, 2), sp.Rational(1, 4)], [sp.Rational(1, 5), sp.Rational(2, 5)]]).det()
    assert d._expr == sp.Rational(3, 20)
    grid = sdata.number_grid([[2, 1], [1, 2]])
    grid.take_inverse(exactly=True)
    assert "[2/3, -1/3]" in capsys.readouterr().out
    assert np.array_equal(grid.as_numpy(), np.array(sp.Matrix([[2, 1], [1, 2]]).inv().evalf(), dtype=float))
    exact = sdata.number_grid([[2, 1, 0], [0, 2, 0], [0, 0, 3]]).find_eigenvalues(exactly=True)
    assert _listed(exact, "eigenvalue exactly") == ["3", "2"]
    assert _listed(exact, "times") == [1, 2]
    assert sp.Matrix([[2, 1, 0], [0, 2, 0], [0, 0, 3]]).eigenvals() == {3: 1, 2: 2}
    roots = sdata.number_grid([[1, 1], [1, 0]]).find_eigenvalues(exactly=True)
    assert _listed(roots, "eigenvalue exactly") == ["1/2 + sqrt(5)/2", "1/2 - sqrt(5)/2"]
    null = sdata.number_grid([[1, 2], [2, 4]]).find_null_space(exactly=True)
    assert null.as_numpy().tolist() == [[-2.0], [1.0]]
    assert "not of length 1" in capsys.readouterr().out
    none = sdata.number_grid([[1, 0], [0, 1]]).find_null_space(exactly=True)
    assert none.as_numpy().shape == (2, 0)


# ---------------------------------------------------------------- P14: display, the bridge and the time limit
def test_repr_latex_and_as_sympy():
    sp, x = _sp()
    f = sdata.formula("x**3 - 2*x")
    assert f._repr_latex_() == "$\\displaystyle " + sp.latex(x ** 3 - 2 * x) + "$"
    expr = f.as_sympy()
    assert expr == x ** 3 - 2 * x and isinstance(expr, sp.Expr)
    assert "_repr_latex_" not in dir(f) and "as_sympy" in dir(f)


def test_the_new_words_have_other_names():
    with pytest.raises(sdata.MissingWordError if hasattr(sdata, "MissingWordError") else Exception,
                       match="turn_into_partial_fractions"):
        sdata.formula("x").apart()
    with pytest.raises(Exception, match="group_by_powers_of"):
        sdata.formula("x").collect()
    with pytest.raises(Exception, match="find_sum_of_series"):
        sdata.summation
    with pytest.raises(Exception, match="find_determinant"):
        sdata.det
    with pytest.raises(Exception, match="find_eigenvalues"):
        sdata.number_grid([[1, 0], [0, 1]]).eigvals()


def test_heavy_sympy_calls_run_in_one_kept_alive_helper():
    sp, x = _sp()
    sdata.formula("x**2 - 1").turn_into_product()
    first = _time_limit.helper_process_id()
    assert first is not None and first != os.getpid()
    sdata.formula("sin(x)**2 + cos(x)**2").make_simpler()
    sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], exactly=True)
    assert _time_limit.helper_process_id() == first  # the same helper, kept alive
    with pytest.raises(ValueError, match="direction"):  # SymPy's own errors come back as they are
        _time_limit.run_with_time_limit(sp.limit, 1 / x, x, 0, dir="up")


def test_a_call_that_does_not_finish_is_stopped_and_the_helper_restarts(monkeypatch):
    sp, x = _sp()
    monkeypatch.setattr(_time_limit, "TIME_LIMIT", 3.0)
    sdata.formula("x").make_simpler()
    before = _time_limit.helper_process_id()
    started = time.monotonic()
    with pytest.raises(sdata.SimplydataError, match="SymPy integrate did not finish in 3 seconds"):
        sdata.formula("exp(sin(x))*log(x)**3/(1 + x**7)").find_area_formula()  # SymPy works on this for minutes
    assert time.monotonic() - started < 30
    assert not _time_limit.helper_is_running()
    with pytest.raises(sdata.SimplydataError, match="did not finish"):  # a big number SymPy cannot factor quickly
        _time_limit.run_with_time_limit(sp.factorint, 2 ** 512 + 1, what="SymPy factorint")
    assert sdata.formula("x**2 - 1").turn_into_product()._expr == (x - 1) * (x + 1)
    after = _time_limit.helper_process_id()
    assert after is not None and after != before


def _alive(pid: int) -> bool:
    if sys.platform == "win32":
        import ctypes

        kernel = ctypes.windll.kernel32
        handle = kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        kernel.GetExitCodeProcess(handle, ctypes.byref(code))
        kernel.CloseHandle(handle)
        return code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:  # pragma: no cover
        return True
    try:  # a finished child of init that is not yet reaped counts as gone
        with open(f"/proc/{pid}/stat") as stat:
            return stat.read().split()[2] != "Z"
    except OSError:
        return True


def _run_script(tmp_path, body: str, end: str = ""):
    temp = tmp_path / "temp"
    temp.mkdir()
    script = tmp_path / "script.py"
    script.write_text(textwrap.dedent(body) + end, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(SRC), "SIMPLYDATA_NO_CITE_LIST": "1", "TEMP": str(temp), "TMP": str(temp),
           "TMPDIR": str(temp)}
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=tmp_path, env=env,
                            timeout=300)
    assert result.returncode == 0, result.stderr
    return result, temp


SCRIPT = """
    print("top-level line")   # no if __name__ == "__main__": the helper must not run this again
    import simplydata as sdata
    from simplydata import _time_limit
    sdata.formula("(x**2 - 1) / (x - 1)").make_simpler()
    print("HELPER", _time_limit.helper_process_id())
"""


def _helper_gone(pid: int, seconds: float = 20.0) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not _alive(pid):
            return True
        time.sleep(0.2)
    return False


def test_the_helper_is_stopped_when_python_exits_and_leaves_no_file(tmp_path):
    result, temp = _run_script(tmp_path, SCRIPT)
    assert result.stdout.count("top-level line") == 1
    pid = int(result.stdout.split("HELPER")[1].split()[0])
    assert _helper_gone(pid)
    assert list(temp.iterdir()) == []  # no temporary file left behind
    assert sorted(p.name for p in tmp_path.iterdir()) == ["script.py", "temp"]  # and nothing else written


def test_the_helper_stops_when_python_is_killed_without_a_goodbye(tmp_path):
    result, _ = _run_script(tmp_path, SCRIPT, "import os, sys\nsys.stdout.flush()\nos._exit(0)\n")
    pid = int(result.stdout.split("HELPER")[1].split()[0])
    assert _helper_gone(pid)  # the helper sees its pipe close and ends


def test_without_a_helper_sympy_runs_here_and_says_so(monkeypatch, capsys):
    monkeypatch.setattr(_time_limit, "_start", lambda: None)
    monkeypatch.setitem(_time_limit._STATE, "said_no_helper", False)
    sp, x = _sp()
    assert sdata.formula("x**2 - 1").turn_into_product()._expr == (x - 1) * (x + 1)
    assert "without the 60-second time limit" in capsys.readouterr().out


# ================================================================ review of 52e71db (each test fails on that commit)
def _run_code(tmp_path, code: str, seconds: float = 120):
    """Run code in a fresh Python; a hang shows as a failure here instead of hanging the test run."""
    script = tmp_path / "check.py"
    script.write_text(textwrap.dedent(code), encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(SRC), "SIMPLYDATA_NO_CITE_LIST": "1"}
    try:
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=tmp_path, env=env,
                                timeout=seconds)
    except subprocess.TimeoutExpired:
        pytest.fail(f"did not finish in {seconds} seconds:\n{code}")
    return result


# ---- 1: a slowly settling series gets only the digits SymPy is sure of
def test_review_1_a_slowly_settling_series_gives_only_sure_digits(capsys):
    value = sdata.find_sum_of_series("1/(k*log(k)**2)", between=[2, "infinity"])
    out = capsys.readouterr().out
    assert abs(value - 2.10974280124) < 0.01  # R: the sum to 1e7 and the integral of the tail
    assert "only 2 digits are sure" in out and "2.106552124" not in out  # 52e71db printed 10 wrong digits
    third = sdata.find_sum_of_series("1/(k*log(k)**3)", between=[2, "infinity"])
    assert third == pytest.approx(2.06588653888, rel=1e-5)
    assert "about 2.06588;" in capsys.readouterr().out


def test_review_1_a_sum_that_runs_out_of_time_gives_advice_for_sums(monkeypatch):
    monkeypatch.setattr(_time_limit, "TIME_LIMIT", 3.0)
    with pytest.raises(sdata.SimplydataError, match="put the terms in numbers") as info:
        sdata.find_sum_of_series("(-1)**k/log(k)", between=[2, "infinity"])
    assert "make_simpler" not in str(info.value)


# ---- 2: an end that is a letter of the formula is that same letter
def test_review_2_a_sum_up_to_a_letter_of_the_formula_is_that_letter():
    sp, _ = _sp()
    s = sdata.find_sum_of_series("k/n", between=[1, "n"], for_letter="k")
    assert len(s._expr.free_symbols) == 1
    assert s.put_in(n=4)._expr == sp.Rational(5, 2)


# ---- 3: letters_are= and the kinds of formulas reach every equation of solve
def test_review_3_letters_are_reaches_formulas_in_solve():
    found = sdata.solve(sdata.formula("c**2 - 4"), exactly=True, letters_are={"c": "positive"})
    assert _listed(found, "c") == [2.0]
    mixed = sdata.solve([sdata.formula("x - 1", letters_are={"x": "positive"}), "x + y = 3"], exactly=True)
    assert _listed(mixed, "x") == [1.0] and _listed(mixed, "y") == [2.0]
    with pytest.raises(sdata.SimplydataError, match="say one thing for each letter"):
        sdata.solve(sdata.formula("c**2 - 4", letters_are={"c": "negative"}), exactly=True,
                    letters_are={"c": "positive"})


# ---- 4: rules keep to the numbers the letter may be
def test_review_4_rules_keep_to_what_the_letter_is(capsys):
    found = sdata.solve("x**2 < 4", exactly=True, letters_are={"x": "positive"})
    assert _listed(found, "from") == [0.0] and _listed(found, "to") == [2.0]
    assert "0 < x < 2" in capsys.readouterr().out
    several = sdata.solve(["x**2 < 4", "x < 1"], exactly=True, letters_are={"x": "positive"})
    assert _listed(several, "from") == [0.0] and _listed(several, "to") == [1.0]
    with pytest.raises(sdata.SimplydataError, match="one period only"):  # SymPy would give 0 < x < pi only
        sdata.solve("sin(x) > 0", exactly=True)


# ---- 5: no heavy SymPy work outside the time limit
def test_review_5_big_special_values_are_refused_while_reading(tmp_path):
    result = _run_code(tmp_path, """
        import simplydata as sdata
        for text in ["gamma(10**7)", "digamma(10**6)", "lgamma(2*10**4)"]:
            try:
                sdata.formula(text)
            except sdata.SimplydataError as error:
                print("REFUSED", str(error).splitlines()[0])
        print("SMALL", sdata.formula("gamma(10)").as_sympy())
    """, seconds=60)
    assert result.stdout.count("REFUSED") == 3 and "SMALL 362880" in result.stdout, result.stderr


def test_review_5_put_in_and_long_sums_stay_inside_the_time_limit(tmp_path):
    result = _run_code(tmp_path, """
        import simplydata as sdata
        from simplydata import _time_limit
        _time_limit.TIME_LIMIT = 5
        try:
            sdata.formula("gamma(x)").put_in(x=10**7)
        except sdata.SimplydataError as error:
            print("STOPPED", str(error).splitlines()[0])
        print("SUM", sdata.find_sum_of_series("1/k**2", between=[1, 10**6]))
        print("VALUE", sdata.formula("x**(x**x)").put_in(x=8))
    """, seconds=120)
    assert "STOPPED SymPy subs did not finish in 5 seconds" in result.stdout, result.stderr
    total = float(result.stdout.split("SUM")[1].split()[0])
    assert total == pytest.approx(math.pi ** 2 / 6 - 1e-6 + 5e-13, rel=1e-12)
    assert "15,151,336 digits" in result.stdout


# ---- 6: answers with more than 4300 digits are shown, never a raw ValueError
def test_review_6_very_long_numbers_are_shown_with_their_size(capsys):
    long_sum = sdata.find_sum_of_series("k**k", between=[1, 2000])
    out = capsys.readouterr().out
    assert "digits, too long to write out" in out
    assert "digits, too long to write out" in repr(long_sum)
    power = sdata.formula("2**x").put_in(x=20000)
    assert "a whole number of 6,021 digits" in repr(power)
    assert sdata.find_sum_of_series("1/k**2", between=[1, 20000]) == pytest.approx(math.pi ** 2 / 6 - 1 / 20000,
                                                                                   rel=1e-8)


# ---- 7: a busy helper never outlives a Python that is killed
def test_review_7_a_busy_helper_ends_when_python_is_killed(tmp_path):
    pid_file = tmp_path / "helper.txt"
    result = _run_code(tmp_path, f"""
        import os, threading
        import simplydata as sdata
        from simplydata import _time_limit
        sdata.formula("x + 1").make_simpler()
        open({str(pid_file)!r}, "w").write(str(_time_limit.helper_process_id()))
        threading.Timer(4, lambda: os._exit(4)).start()
        sdata.formula("(x + y + 1)**100*(x + y + 2)**100").turn_into_sum()
    """, seconds=90)  # 52e71db: the helper kept the output pipe open, so this never returned
    assert result.returncode == 4
    assert _helper_gone(int(pid_file.read_text()), 20)


# ---- 8: a value or a range that contradicts letters_are= is refused
def test_review_8_values_must_fit_letters_are():
    f = sdata.formula("sqrt(x**2)", letters_are={"x": "positive"})
    with pytest.raises(sdata.SimplydataError, match="x is positive"):
        f.find_value_at(x=-2)
    with pytest.raises(sdata.SimplydataError, match="x is positive"):
        f.find_value_at(x=[1, 2, -3])
    with pytest.raises(sdata.SimplydataError, match="x is positive"):
        f.put_in(x=-2)
    with pytest.raises(sdata.SimplydataError, match="x is positive"):
        sdata.find_area_under(f, between=[-1, 1])
    with pytest.raises(sdata.SimplydataError, match="x is positive"):
        sdata.find_area_under(f, between=[-1, 1], exactly=True)
    with pytest.raises(sdata.SimplydataError, match="x is positive"):
        sdata.find_where_smallest(f, between=[-1, 1])
    with pytest.raises(sdata.SimplydataError, match="x is positive"):
        sdata.chart().draw_curve(f, between=[-1, 1])
    assert f.find_value_at(x=2) == 2.0
    assert sdata.find_area_under(f, between=[0, 1]) == pytest.approx(0.5)


# ---- 9: a letter every number fits is said so
def test_review_9_a_letter_every_number_fits_is_said(capsys):
    found = sdata.solve(["x + y = 3", "2*x + 2*y = 6"], exactly=True)
    out = capsys.readouterr().out
    assert "y can be any number; x = 3 - y" in out
    assert "These are all the solutions" not in out and "y = y" not in out and "\n stay" not in out
    assert _listed(found, "y exactly") == ["any number"]


# ---- 10 and 11: the order of R eigen(), and real exact eigenvalues without a rounding remainder
def test_review_10_eigenvalues_are_in_the_order_of_r(capsys):
    from scipy import linalg

    g = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
    values = sdata.number_grid(g).find_eigenvalues()
    found = linalg.eigvals(np.array(g, dtype=float))
    assert np.allclose(_listed(values, "eigenvalue"), sorted(found.real, key=abs, reverse=True))  # R: by Mod
    almost = np.array([[2.0, 1.0], [1.0 + 1e-16, 2.0]])  # symmetric to within R isSymmetric's tolerance
    sdata.number_grid(almost.tolist()).find_eigenvalues()
    assert "eigvalsh, for a symmetric grid" in capsys.readouterr().out


def test_review_11_real_exact_eigenvalues_have_no_imaginary_part():
    exact = sdata.number_grid([[1, 2, 3], [0, 1, 4], [5, 6, 0]]).find_eigenvalues(exactly=True)
    assert _listed(exact, "imaginary part") == [0.0, 0.0, 0.0]
    assert np.allclose(_listed(exact, "eigenvalue"), [7.25602, -5.22967, -0.0263528], rtol=1e-5)


# ---- 12: exactly=True keeps a number no short fraction gives back
def test_review_12_exact_grids_do_not_round_the_numbers():
    sp, _ = _sp()
    d = sdata.number_grid([[1, 2], [2, 4 + 1e-15]]).find_determinant(exactly=True)
    assert d._expr != 0 and d._expr == sp.Rational(4 + 1e-15) - 4
    assert sdata.number_grid([[0.5, 0.25], [0.2, 0.4]]).find_determinant(exactly=True)._expr == sp.Rational(3, 20)


# ---- 13: a letter SymPy cancels is still integrated over
def test_review_13_volume_with_a_cancelled_letter():
    v = sdata.find_volume_under("x*y/y", between={"x": [0, 1], "y": [0, 2]}, exactly=True)
    assert v._expr == 1


# ---- 14: wording
def test_review_14_wording(capsys):
    sp, _ = _sp()
    assert sdata.formula("1/x").find_limit_as("x", goes_to="infinity") == 0.0
    out = capsys.readouterr().out
    assert "goes to infinity" in out and "oo" not in out
    with pytest.raises(sdata.SimplydataError, match="at infinity there is only one side"):
        sdata.formula("1/x").find_limit_as("x", goes_to="infinity", from_side="below")
    sdata.find_sum_of_series("1/k**2", between=["-infinity", -1])
    assert "from -infinity to -1" in capsys.readouterr().out
    sdata.formula("sqrt(-4)").show_as_decimal()
    assert "complex number" in capsys.readouterr().out
    path = sdata.find_path_over_time("d2x/dt2 = -x", at_start={"x": 1, "dx/dt": 0}, between=[0, 10],
                                     stop_when="dx/dt > 0.5")
    assert path.get_cell_at(row=path.count_rows(), column="dx/dt") == pytest.approx(0.5, abs=1e-6)
    with pytest.raises(Exception, match="show_as_decimal") as info:
        sdata.formula("x").N()
    assert "find_value_at" in str(info.value)
    assert "solve_matrix" not in sdata.NumberGrid._HINTS  # solving is sdata.solve, not an inverse
    geometric = sdata.find_sum_of_series("r**k", between=[0, "infinity"], for_letter="k")
    assert geometric.find_value_at(r=0.5) == 2.0
    with pytest.raises(sdata.SimplydataError, match="no value among the ordinary numbers"):
        geometric.find_value_at(r=2)
    t = sp.Symbol("t")
    typed = sdata.find_path_over_time("dN/dt = 0.3*N", at_start={"N": 10}, exactly=True)
    assert typed._expr == 10 * sp.exp(sp.Rational(3, 10) * t)  # as known={"r": 0.3} gives


# ---- 15: the helper's edge cases
def test_review_15_helper_edge_cases(monkeypatch, capsys):
    sp, x = _sp()
    with pytest.raises(sdata.SimplydataError, match="could not be handed to the helper"):
        _time_limit.run_with_time_limit(lambda: 1, what="a lambda")

    class Gone:
        def send(self, job):
            raise OSError("pipe gone")

    started = iter([(None, Gone(), None), None])
    monkeypatch.setattr(_time_limit, "_start", lambda: next(started))
    monkeypatch.setattr(_time_limit, "_kill", lambda: None)
    monkeypatch.setitem(_time_limit._STATE, "said_no_helper", False)
    assert _time_limit.run_with_time_limit(sp.factor, x ** 2 - 1) == (x - 1) * (x + 1)  # 52e71db: TypeError
    assert "without the 60-second time limit" in capsys.readouterr().out


def test_review_15_the_main_module_is_not_swapped_while_the_helper_starts():
    seen = []

    class Process:
        def start(self):
            from multiprocessing import spawn

            seen.append(sys.modules["__main__"])
            seen.append(spawn.get_preparation_data("x"))

    main = sys.modules["__main__"]
    _time_limit._start_without_main(Process())
    assert seen[0] is main
    assert "init_main_from_path" not in seen[1] and "init_main_from_name" not in seen[1]


# ---- suspected: memory, embedded Pythons, one deadline per word
def test_review_suspected_the_helper_has_a_memory_limit():
    sp, _ = _sp()
    with pytest.raises(sdata.SimplydataError, match="more memory than the helper may use"):
        _time_limit.run_with_time_limit(operator.lshift, 1, 2 ** 37, what="SymPy power")  # 16 GB at once
    with pytest.raises(sdata.SimplydataError, match="too big to add up exactly"):
        sdata.find_sum_of_series("2**(2**k)", between=[1, 36])


def test_review_suspected_an_embedded_python_runs_sympy_here(monkeypatch, capsys):
    from multiprocessing import spawn

    _time_limit._stop()
    monkeypatch.setattr(spawn, "get_executable", lambda: "C:/Program Files/SomeApp/someapp.exe")
    monkeypatch.setitem(_time_limit._STATE, "said_no_helper", False)
    sp, x = _sp()
    assert sdata.formula("x**2 - 1").turn_into_product()._expr == (x - 1) * (x + 1)
    assert "without the 60-second time limit" in capsys.readouterr().out
    assert not _time_limit.helper_is_running()


def test_review_suspected_one_word_has_one_deadline(monkeypatch):
    monkeypatch.setattr(_time_limit, "TIME_LIMIT", 4.0)

    @_time_limit.one_deadline
    def two_calls():
        _time_limit.run_with_time_limit(time.sleep, 3)
        _time_limit.run_with_time_limit(time.sleep, 3)

    started = time.monotonic()
    with pytest.raises(sdata.SimplydataError, match="did not finish"):
        two_calls()
    assert time.monotonic() - started < 5.5
    assert _time_limit._STATE["deadline"] is None
