"""Numbers phase, batch 4 (approved by Manish 2026-11-26): the SymPy words.

Each answer is compared with SymPy (or SciPy) doing the same, and with the answer worked out by hand where there is
one. The time limit is tested with a SymPy call that really does not finish, and the helper process is checked to be
gone when Python exits, even when Python is stopped without a goodbye.
"""

from __future__ import annotations

import math
import operator
import os
import pickle
import re
import subprocess
import sys
import textwrap
import threading
import time
from decimal import Decimal
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
    """A column as a plain list (a column of numbers comes back as sdata.number_list, any other as a list)."""
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
    assert str(geometric) == "Piecewise((1/(1 - r), Abs(r) < 1))"  # no value where |r| >= 1 (review 2, I)
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
def _printed_sum(out: str) -> str:
    """The decimal a sum without an exact formula prints ("settles at about 2.065886539")."""
    return out.split("settles at about ")[1].split()[0].rstrip(";")


def _correctly_rounded(reference: float, printed: str) -> bool:
    """Whether printed is reference rounded to as many significant digits as printed has."""
    digits = len(printed.replace("-", "").replace(".", "").lstrip("0"))
    return Decimal(printed) == Decimal(f"{reference:.{digits}g}")


def test_review_1_a_slowly_settling_series_gives_only_sure_digits(capsys):
    # R (r7.R): the terms up to 1e6 or 1e7 and the Euler-Maclaurin tail, good to about 1e-11
    value = sdata.find_sum_of_series("1/(k*log(k)**2)", between=[2, "infinity"])
    out = capsys.readouterr().out
    assert abs(value - 2.10974280124) < 1e-9
    printed = _printed_sum(out)
    assert len(printed.replace(".", "")) >= 8 and _correctly_rounded(2.10974280124, printed)
    assert "2.106552124" not in out  # 52e71db printed 10 wrong digits
    third = sdata.find_sum_of_series("1/(k*log(k)**3)", between=[2, "infinity"])
    assert abs(third - 2.06588653888) < 1e-9
    printed = _printed_sum(capsys.readouterr().out)
    assert _correctly_rounded(2.06588653888, printed)  # 1bab143 printed 2.06588 (R: 2.065887)


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


def test_review_5_put_in_too_big_is_refused_and_long_sums_stay_inside_the_time_limit(tmp_path):
    result = _run_code(tmp_path, """
        import simplydata as sdata
        from simplydata import _time_limit
        _time_limit.TIME_LIMIT = 5
        try:
            sdata.formula("gamma(x)").put_in(x=10**7)
        except sdata.SimplydataError as error:
            print("REFUSED", str(error).splitlines()[0])
        print("SUM", sdata.find_sum_of_series("1/k**2", between=[1, 10**6]))
        try:
            sdata.formula("x**(x**x)").put_in(x=8)
        except sdata.SimplydataError as error:
            print("REFUSED", str(error).splitlines()[0])
    """, seconds=120)
    # since 5417466 both put_in() calls are refused before SymPy starts (gamma of more than 1000, and 8**(8**8) with
    # 15,151,336 digits), instead of being stopped by the time limit
    assert "REFUSED put_in() would give gamma() a number bigger than 1000" in result.stdout, result.stderr
    total = float(result.stdout.split("SUM")[1].split()[0])
    assert total == pytest.approx(math.pi ** 2 / 6 - 1e-6 + 5e-13, rel=1e-12)
    assert "REFUSED put_in() would make a number with more than 1000 digits" in result.stdout


# ---- 6: answers with more than 4300 digits are shown, never a raw ValueError
def test_review_6_very_long_numbers_are_shown_with_their_size(capsys):
    long_sum = sdata.find_sum_of_series("k**k", between=[1, 2000])
    out = capsys.readouterr().out
    assert "digits, too long to write out" in out
    assert "digits, too long to write out" in repr(long_sum)
    from simplydata import _formula

    sp, _ = _sp()
    power = _formula.Formula(sp.Integer(2) ** 20000)  # since 5417466, put_in(x=20000) on 2**x is refused
    assert "a whole number of 6,021 digits" in repr(power)
    n = 20000  # pi**2/6 - psi1(n + 1), with the asymptotic series of psi1 (the next term, 1/(30 n**5), is 1e-23)
    assert sdata.find_sum_of_series("1/k**2", between=[1, n]) == pytest.approx(
        math.pi ** 2 / 6 - 1 / n + 1 / (2 * n ** 2) - 1 / (6 * n ** 3), rel=1e-14)


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
    np.testing.assert_allclose(_listed(values, "eigenvalue"), sorted(found.real, key=abs, reverse=True), rtol=1e-12,
                               atol=0)  # R: by Mod
    almost = np.array([[2.0, 1.0], [1.0 + 1e-14, 2.0]])  # R isSymmetric() gives TRUE (all.equal, 100 * eps)
    assert almost[1, 0] != almost[0, 1]
    capsys.readouterr()
    sdata.number_grid(almost.tolist()).find_eigenvalues()
    assert "eigvalsh, for a symmetric grid" in capsys.readouterr().out


def test_review_11_real_exact_eigenvalues_have_no_imaginary_part():
    exact = sdata.number_grid([[1, 2, 3], [0, 1, 4], [5, 6, 0]]).find_eigenvalues(exactly=True)
    assert _listed(exact, "imaginary part") == [0.0, 0.0, 0.0]
    from scipy import linalg

    found = linalg.eigvals(np.array([[1, 2, 3], [0, 1, 4], [5, 6, 0]], dtype=float))
    np.testing.assert_allclose(_listed(exact, "eigenvalue"), sorted(found.real, key=abs, reverse=True), rtol=1e-12,
                               atol=0)  # R eigen(): 7.25602242, -5.22966960, -0.02635282


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


def test_review_15_main_is_never_swapped_while_a_helper_process_starts(monkeypatch):
    """52e71db swapped sys.modules["__main__"] while the helper started: seen from inside the start itself."""
    from multiprocessing import context

    sp, x = _sp()
    main = sys.modules["__main__"]
    seen = []

    def recording_start(self):  # no process is started: the main module is noted, then the start fails
        seen.append(sys.modules["__main__"])
        raise OSError("test: no process is started")

    _time_limit._stop()
    monkeypatch.setattr(context.SpawnProcess, "start", recording_start)
    monkeypatch.setitem(_time_limit._STATE, "said_no_helper", False)
    try:
        _time_limit.run_with_time_limit(sp.factor, x ** 2 - 1)
    except OSError:
        pass
    assert seen and all(m is main for m in seen)


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


def test_the_helper_reports_its_memory_limit_when_it_is_ready():
    _sp()
    _time_limit.run_with_time_limit(operator.add, 1, 2)  # starts the helper
    limit = _time_limit._STATE["memory_limit"]
    assert isinstance(limit, int) and 2 ** 30 <= limit <= 4 * 2 ** 30


def test_on_macos_the_parent_stops_a_helper_over_its_memory_limit(monkeypatch):
    # macOS ignores RLIMIT_AS, so 1 << 2**37 (16 GB) ran in the helper there and only failed when the answer was
    # sent back ("OverflowError: int too large to pickle", PR #72 macOS 3.12 and 3.13): the parent now watches the
    # helper's memory itself on macOS
    class Waiting:  # an answers pipe with no answer yet
        def poll(self, seconds):
            time.sleep(seconds)
            return False

    class Helper:
        pid = 12345

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setitem(_time_limit._STATE, "memory_limit", 2 ** 30)
    monkeypatch.setattr(_time_limit, "_memory_in_use", lambda pid: 2 ** 31)
    assert _time_limit._wait(Helper(), Waiting(), 5.0) is None
    monkeypatch.setattr(_time_limit, "_memory_in_use", lambda pid: 2 ** 20)
    started = time.monotonic()
    assert _time_limit._wait(Helper(), Waiting(), 0.3) is False  # under the limit: waits for the time limit
    assert time.monotonic() - started >= 0.25


def test_on_macos_a_stand_in_helper_is_waited_for_in_one_go(monkeypatch):
    # the recording stand-in of the deadline tests has no process: on macOS it saw the 0.05 s memory looks instead
    # of the word's whole wait (PR #72 macOS 3.11, test_review2_k_each_thread_keeps_its_own_deadline)
    seen = []

    class Answers:
        def poll(self, seconds):
            seen.append(seconds)
            return True

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setitem(_time_limit._STATE, "memory_limit", 2 ** 30)
    assert _time_limit._wait(None, Answers(), 42.0) is True
    assert seen == [42.0]


def test_a_stopped_helper_forgets_its_memory_limit():
    _sp()
    _time_limit.run_with_time_limit(operator.add, 1, 2)
    assert _time_limit._STATE["memory_limit"]
    _time_limit._stop()
    assert _time_limit._STATE["memory_limit"] is None


@pytest.mark.skipif(sys.platform != "darwin", reason="proc_pid_rusage is part of macOS")
def test_on_macos_the_memory_of_a_process_can_be_read():
    used = _time_limit._memory_in_use(os.getpid())
    assert used is not None and 10 * 2 ** 20 < used < 64 * 2 ** 30


def test_the_helper_starts_when_multiprocessing_keeps_the_executable_as_bytes(monkeypatch):
    # Linux and macOS: multiprocessing.spawn keeps the executable as os.fsencode(sys.executable), so comparing it
    # with text raised TypeError and no SymPy word could start its helper there (PR #72, test-without-r)
    from multiprocessing import spawn

    from simplydata import _time_limit

    monkeypatch.setattr(spawn, "get_executable", lambda: b"/usr/bin/python3.12")
    assert _time_limit._helper_can_start() is True
    monkeypatch.setattr(spawn, "get_executable", lambda: b"/opt/app/embedded-host")
    assert _time_limit._helper_can_start() is False


def test_review_suspected_an_embedded_python_runs_sympy_here(monkeypatch, capsys):
    from multiprocessing import context, spawn

    _time_limit._stop()
    launched = []

    def recording_start(self):  # never run the other program: note the try, then fail as a start would
        launched.append(spawn.get_executable())
        raise OSError("test: not started")

    other = (os.path.join(os.environ.get("SystemRoot", "C:/Windows"), "System32", "notepad.exe")
             if sys.platform == "win32" else "/bin/sh")
    assert os.path.exists(other)  # a real program that is not Python (on 52e71db the start was tried)
    monkeypatch.setattr(context.SpawnProcess, "start", recording_start)
    monkeypatch.setattr(spawn, "get_executable", lambda: other)
    monkeypatch.setitem(_time_limit._STATE, "said_no_helper", False)
    sp, x = _sp()
    assert sdata.formula("x**2 - 1").turn_into_product()._expr == (x - 1) * (x + 1)
    assert "without the 60-second time limit" in capsys.readouterr().out
    assert launched == []
    assert not _time_limit.helper_is_running()


class _RecordingHelper:
    """The two pipes of a helper that runs each job here (pickled both ways, as the real pipes do) and records how
    long run_with_time_limit would wait for each answer."""

    def __init__(self, delay: float = 0.0):
        self.waits, self.jobs, self.delay = [], [], delay
        self._job = None

    def send(self, job):
        self._job = pickle.loads(pickle.dumps(job))
        self.jobs.append(self._job)

    def poll(self, seconds):
        self.waits.append(seconds)
        return True

    def recv(self):
        call, values, named = self._job
        time.sleep(self.delay)
        try:
            return pickle.loads(pickle.dumps(("done", call(*values, **named))))
        except Exception as error:  # noqa: BLE001 - as the helper sends SymPy's error back
            return ("error", error)


def _recording_helper(monkeypatch, delay: float = 0.0) -> _RecordingHelper:
    helper = _RecordingHelper(delay)
    monkeypatch.setattr(_time_limit, "_start", lambda: (None, helper, helper))
    return helper


def test_review_suspected_one_word_has_one_deadline(monkeypatch):
    """The SymPy calls of one word wait less and less: they share the word's deadline (52e71db: each waited the
    whole TIME_LIMIT)."""
    helper = _recording_helper(monkeypatch, delay=0.05)
    sp, _ = _sp()
    assert sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])._expr == sp.pi ** 2 / 6
    assert len(helper.waits) >= 2 and helper.waits[0] <= _time_limit.TIME_LIMIT
    assert helper.waits[-1] < _time_limit.TIME_LIMIT - 0.04


# ================================================================ second review of 1bab143 (each test fails on that commit)
# ---- A: nothing heavy is worked out while a formula is read
@pytest.mark.parametrize("text", ["gamma(abs(-2000))", "gamma(sqrt(4000000))", "gamma(2000 + 0*x)", "gamma(2000*x/x)",
                                  "digamma(abs(-5000))", "gamma(gamma(10))"])
def test_review2_a_numbers_inside_special_functions_are_checked_however_written(text):
    with pytest.raises(sdata.SimplydataError, match="too big to work out exactly"):
        sdata.formula(text)


@pytest.mark.parametrize("text", ["(1 + 1/10**4)**(10**4)", "2**(10**6*x/x)"])
def test_review2_a_powers_with_more_than_1000_digits_are_refused_however_written(text):
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula(text)


def test_review2_a_special_functions_of_numbers_are_worked_out_by_the_helper(monkeypatch):
    helper = _recording_helper(monkeypatch)
    sp, x = _sp()
    assert sdata.formula("gamma(abs(-20)) + x").as_sympy() == sp.factorial(19) + x
    assert helper.jobs  # worked out under the time limit; 1bab143 worked it out while reading the text
    assert sdata.formula("2**3000").as_sympy() == sp.Integer(2) ** 3000  # 903 digits: still allowed
    assert sdata.formula("x**2 - 1").as_sympy() == x ** 2 - 1


# ---- B: a series decimal is bounded, and printed with its sure digits correctly rounded
def test_review2_b_a_series_without_a_formula_is_bounded_and_correctly_rounded(capsys):
    sp, _ = _sp()
    k = sp.Symbol("k", integer=True)
    value = sdata.find_sum_of_series("1/(k**3 + k + 1)", between=[1, "infinity"])
    reference = sp.Sum(1 / (k ** 3 + k + 1), (k, 1, sp.oo)).evalf(30)  # converges fast: SymPy's evalf is good here
    assert value == pytest.approx(float(reference), rel=1e-12)
    out = capsys.readouterr().out
    printed = _printed_sum(out)
    assert _correctly_rounded(float(reference), printed)  # 0.4947249196: rounded, not cut
    assert "integral" in out
    with pytest.raises(sdata.SimplydataError, match="keep falling"):  # 1/(k**2 + sin(k)): SymPy cannot show it
        sdata.find_sum_of_series("1/(k**2 + sin(k))", between=[1, "infinity"])


# ---- C: a repeating rule is answered when it always or never holds, or within a range of finite length
def test_review2_c_repeating_rules_that_have_a_complete_answer(capsys):
    never = sdata.solve("sin(x) > 2", exactly=True)
    assert math.isnan(_listed(never, "from")[0]) and "never true" in capsys.readouterr().out
    never = sdata.solve("cos(x) > 2", exactly=True, letters_are={"x": "positive"})
    assert math.isnan(_listed(never, "from")[0])
    always = sdata.solve("sin(x) >= -1", exactly=True)
    assert _listed(always, "from") == [-math.inf] and _listed(always, "to") == [math.inf]
    short = sdata.solve(["sin(x) > 0", "x > 0", "x < 3"], exactly=True)
    assert _listed(short, "from") == [0.0] and _listed(short, "to") == [3.0]
    longer = sdata.solve(["sin(x) > 0", "x > 0", "x < 10"], exactly=True)  # by hand: 0 < x < pi or 2 pi < x < 3 pi
    assert _listed(longer, "from") == pytest.approx([0.0, 2 * math.pi], rel=1e-15)
    assert _listed(longer, "to") == pytest.approx([math.pi, 3 * math.pi], rel=1e-15)
    with pytest.raises(sdata.SimplydataError, match="one period only"):  # endless and partly true: still refused
        sdata.solve("sin(x) > 0", exactly=True)


# ---- D: the size of a very long number comes from SymPy (N and integer_log)
def test_review2_d_the_digits_of_a_long_number_are_counted_by_sympy():
    from simplydata import _formula

    sp, _ = _sp()
    nines = _formula._too_long(sp, sp.Integer(10) ** 5000 - 1)  # 5000 nines (1bab143: "5,001 digits")
    assert "a whole number of 5,000 digits" in nines and "1.00000E+5000" in nines
    # 2**20000 made by SymPy itself: since 5417466, put_in(x=20000) on 2**x is refused (more than 1000 digits)
    assert "about 3.98028E+6020 (a whole number of 6,021 digits" in repr(_formula.Formula(sp.Integer(2) ** 20000))


# ---- E: exact eigenvalues in R's order, also among eigenvalues of the same size
R_EIGEN = [  # R 4.6.2, eigen(m)$values (printed to 7 digits)
    ([[0, 4], [1, 0]], [2, -2]),
    ([[0, -1], [1, 0]], [1j, -1j]),
    ([[2, 0, 0], [0, -2, 0], [0, 0, 1]], [2, 1, -2]),
    ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], [-0.5 + 0.8660254j, -0.5 - 0.8660254j, 1]),
    ([[1, 2, 0, 0, 1, 1], [0, 0, 1, 2, 0, 0], [0, 1, 0, 0, 1, 3], [0, 1, 0, 1, 0, 0], [0, 1, 0, 0, 0, 0],
      [0, 1, 0, 0, 1, 0]],
     [2.5236326, -0.6751899 + 0.9909579j, -0.6751899 - 0.9909579j, 1, -1, 0.8267473]),
]


@pytest.mark.parametrize("grid, r_order", R_EIGEN)
def test_review2_e_exact_eigenvalues_are_in_r_order(grid, r_order):
    exact = sdata.number_grid(grid).find_eigenvalues(exactly=True)
    found = np.array(_listed(exact, "eigenvalue")) + 1j * np.array(_listed(exact, "imaginary part"))
    decimal = sdata.number_grid(grid).find_eigenvalues()
    in_numbers = np.array(_listed(decimal, "eigenvalue")) + 1j * np.array(_listed(decimal, "imaginary part"))
    np.testing.assert_allclose(found, in_numbers, rtol=1e-12, atol=1e-14)  # SciPy (LAPACK), as R
    np.testing.assert_allclose(found, r_order, atol=5e-8)  # R printed 7 digits; the order is what counts here


# ---- F: put_in(x="y") gives y what x was
def test_review2_f_put_in_a_letter_keeps_what_the_letter_is():
    f = sdata.formula("sqrt(x**2)", letters_are={"x": "positive"})
    g = f.put_in(x="y")
    assert "y (positive)" in repr(g)
    with pytest.raises(sdata.SimplydataError, match="y is positive"):
        g.put_in(y=-2)  # 1bab143: -2, though sqrt((-2)**2) is 2


# ---- G: a whole typed decimal is its simplest fraction (1e23 is 10**23, not its binary value)
def test_review2_g_whole_typed_decimals_are_their_simplest_fraction():
    from simplydata._formula import exact_number

    sp, _ = _sp()
    assert exact_number(sp, 1e23) == 10 ** 23
    assert _listed(sdata.solve("x = 2*N", exactly=True, known={"N": 6.022e23}), "x exactly") == [
        "1204400000000000000000000"]
    assert sdata.find_area_under("1e23*x", between=[0, 1], exactly=True)._expr == 5 * 10 ** 22
    assert exact_number(sp, 4 + 1e-15) == sp.Rational(4 + 1e-15)  # still no rounding (review 1, finding 12)


# ---- H and I: the sum of r**k holds for |r| < 1 only; elsewhere it, and its slope, have no value
def test_review2_h_a_sum_with_a_condition_works_in_the_other_words(tmp_path):
    sp, _ = _sp()
    geometric = sdata.find_sum_of_series("r**k", between=[0, "infinity"], for_letter="k")
    smallest = sdata.find_where_smallest(geometric, between=[-0.5, 0.5])
    assert smallest.get_cell_at(row=1, column="smallest value") == pytest.approx(2 / 3, rel=1e-9)
    assert sdata.find_area_under(geometric, between=[0, 0.5]) == pytest.approx(math.log(2), rel=1e-12)
    assert sdata.find_area_under(geometric, between=[0, 0.5], exactly=True)._expr == sp.log(2)
    chart = sdata.chart()
    chart.draw_curve(geometric, between=[-0.5, 0.5])
    xs, ys = chart._render().axes[0].get_lines()[0].get_data()
    assert np.allclose(ys, 1 / (1 - xs), rtol=1e-12)


def test_review2_i_the_slope_of_a_conditional_sum_has_no_value_where_the_sum_has_none():
    geometric = sdata.find_sum_of_series("r**k", between=[0, "infinity"], for_letter="k")
    slope = geometric.find_slope_formula()
    assert slope.find_value_at(r=0.5) == pytest.approx(4.0, rel=1e-15)
    with pytest.raises(sdata.SimplydataError, match="no value among the ordinary numbers"):
        slope.find_value_at(r=2)  # 1bab143: 0
    many = slope.find_value_at(r=[0.5, 2]).as_numpy()
    assert many[0] == pytest.approx(4.0) and math.isnan(many[1])


# ---- J: while the helper starts, another thread's new process keeps its main script
def test_review2_j_another_thread_keeps_its_main_script_while_the_helper_starts(monkeypatch):
    import types
    from multiprocessing import spawn

    main = types.ModuleType("__main__")
    main.__file__ = os.path.abspath("someone_elses_script.py")
    main.__spec__ = None
    monkeypatch.setitem(sys.modules, "__main__", main)
    expected = spawn.get_preparation_data("other")
    assert "init_main_from_path" in expected
    seen = {}

    class Process:
        def start(self):  # while the helper starts, another thread prepares its own new process
            other = threading.Thread(target=lambda: seen.update(other=spawn.get_preparation_data("other")))
            other.start()
            other.join(10)
            seen["helper"] = spawn.get_preparation_data("helper")

    _time_limit._start_without_main(Process())
    assert seen["other"].get("init_main_from_path") == expected["init_main_from_path"]  # 1bab143: left out
    assert "init_main_from_path" not in seen["helper"]
    assert "init_main_from_path" in spawn.get_preparation_data("after")


# ---- K: each thread has its own deadline; the exact grid words share one
def test_review2_k_each_thread_keeps_its_own_deadline(monkeypatch):
    monkeypatch.setattr(_time_limit, "TIME_LIMIT", 100.0)
    helper = _recording_helper(monkeypatch)
    waits, errors = {}, []
    a_inside, b_inside, a_left = threading.Event(), threading.Event(), threading.Event()

    @_time_limit.one_deadline
    def word_a():
        a_inside.set()
        b_inside.wait(10)

    @_time_limit.one_deadline
    def word_b():
        b_inside.set()
        a_left.wait(10)
        time.sleep(0.3)
        _time_limit.run_with_time_limit(operator.add, 1, 2)
        waits["b"] = helper.waits[-1]

    def run(word):
        try:
            word()
        except Exception as error:  # noqa: BLE001 - reported below
            errors.append(error)

    a = threading.Thread(target=run, args=(word_a,))
    a.start()
    a_inside.wait(10)
    b = threading.Thread(target=run, args=(word_b,))
    b.start()
    a.join(10)
    a_left.set()
    b.join(10)
    assert not errors
    assert waits["b"] < 100.0 - 0.2  # B's own deadline, set 0.3 s before (1bab143: A cleared it, so 100)

    @_time_limit.one_deadline
    def word_c():
        time.sleep(0.5)
        later.wait(10)

    @_time_limit.one_deadline
    def word_d():
        _time_limit.run_with_time_limit(operator.add, 1, 2)
        waits["d"] = helper.waits[-1]

    later = threading.Event()
    c = threading.Thread(target=run, args=(word_c,))
    c.start()
    time.sleep(0.6)
    d = threading.Thread(target=run, args=(word_d,))
    d.start()
    d.join(10)
    later.set()
    c.join(10)
    assert not errors
    assert waits["d"] > 100.0 - 0.3  # D's own deadline (1bab143: C's, 0.6 s older)


@pytest.mark.parametrize("word", ["find_eigenvalues", "find_determinant", "take_inverse"])
def test_review2_k_the_exact_grid_words_share_one_deadline(monkeypatch, word):
    helper = _recording_helper(monkeypatch, delay=0.05)
    getattr(sdata.number_grid([[2, 1], [1, 3]]), word)(exactly=True)
    assert len(helper.waits) >= 2
    assert helper.waits[-1] < _time_limit.TIME_LIMIT - 0.04  # 1bab143: each call waited the whole time limit


# ---- L: wording
def test_review2_l_wording(capsys):
    sdata.solve("x**2 < 10", exactly=True, letters_are={"x": "positive whole number"})
    out = capsys.readouterr().out
    assert "over the positive numbers" in out and "whole number numbers" not in out
    assert "only the positive whole numbers in these ranges count" in out
    with pytest.raises(sdata.SimplydataError, match="false for every value of x when x is zero or more") as info:
        sdata.solve("x < -1", exactly=True, letters_are={"x": "zero or more"})
    assert "no letter left" not in str(info.value)
    with pytest.raises(sdata.SimplydataError, match="false for every value of x when x is positive"):
        sdata.solve("x + a = 0", exactly=True, known={"a": 2}, letters_are={"x": "positive"})
    whole = sdata.formula("x**2 + sin(pi*x)", letters_are={"x": "whole number"})
    with pytest.raises(sdata.SimplydataError, match="x is a whole number") as info:
        sdata.find_area_under(whole, between=[0, 1])
    assert "Keep between=" not in str(info.value)
    rule = sdata.solve("x < 3.5", exactly=True)
    assert _listed(rule, "to exactly") == ["7/2"]  # 1bab143: 3.50000000000000


# ---- M: the helper's memory limit follows the memory free now, at most 4 GB
def test_review2_m_the_helper_memory_limit_follows_free_memory(monkeypatch):
    from simplydata import _sympy_worker

    gigabyte = 1024 ** 3
    assert gigabyte <= _sympy_worker.memory_limit() <= 4 * gigabyte  # 1bab143: half of all memory, up to 8 GB
    monkeypatch.setattr(_sympy_worker, "_memory_free_now", lambda: 3 * gigabyte)
    assert _sympy_worker.memory_limit() == 3 * gigabyte // 2
    monkeypatch.setattr(_sympy_worker, "_memory_free_now", lambda: 64 * gigabyte)
    assert _sympy_worker.memory_limit() == 4 * gigabyte
    monkeypatch.setattr(_sympy_worker, "_memory_free_now", lambda: gigabyte // 2)
    assert _sympy_worker.memory_limit() == gigabyte


# ================================================================ third review of 2ded4aa (each test fails on that commit)
# ---- A: every power that could grow, and every exp of a log, is sized before SymPy makes the number
@pytest.mark.parametrize("text", ["(abs(999)**100)**100", "exp(3000*log(10))", "exp(log(10)*3000)*x",
                                  "exp(3000*log(10) + x)", "exp(1)**(3000*log(10))", "(999*x + 0)**400",
                                  "((999*x)**100)**100", "(x*abs(999)**100)**100", "((1 + 1/abs(10)**4)**100)**100",
                                  "exp(log(1 + 1/10**4)*10**4)", "1" + "0" * 400 + "**100"])
def test_review3_a_nested_powers_and_exp_of_a_log_are_refused(text):
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula(text)  # 2ded4aa: worked out here (29,996 digits for the first), or OverflowError for the last


@pytest.mark.parametrize("text", ["((abs(999)**100)**100)**100", "(((abs(999)**100)**100)**100)**100",
                                  "exp(10**6*log(10))", "exp(10**9*log(10))"])
def test_review3_a_deeper_powers_are_refused_at_once(text):
    started = time.monotonic()
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula(text)  # 2ded4aa: millions of digits (or 10**(10**9)) worked out in this process
    assert time.monotonic() - started < 30


def test_review3_a_ordinary_formulas_are_read_as_before():
    expected = {"2**x": "2**x", "x**2 - 4*x + 1": "x**2 - 4*x + 1", "(x+1)**(1/2)": "sqrt(x + 1)",
                "exp(-x/2)": "exp(-x/2)", "1/(1+exp(-x))": "1/(1 + exp(-x))", "10**(x/10)": "10**(x/10)",
                "x - 1": "x - 1", "2*x/3": "2*x/3", "-x**2": "-x**2", "gamma(x)*2": "2*gamma(x)", "gamma(5)*x": "24*x",
                "x**0.5": "x**0.5", "(x+1)**0.5": "(x + 1)**0.5", "2**-x": "2**(-x)", "beta(2, 3)*x": "x/12",
                "sinc(x)": "sinc(pi*x)", "a*exp(-b*t)": "a*exp(-b*t)", "3.5*x": "3.5*x", "0.1*x + 0.2": "0.1*x + 0.2",
                "(x-1)/(x-1)": "1", "x*y/y": "x", "log(8, 2)*x": "3*x", "sqrt(8)*x": "2*sqrt(2)*x",
                "(2*x)**(3/2)": "2*sqrt(2)*x**(3/2)", "2**(1/2)": "sqrt(2)", "abs(-3)*x": "3*x",
                "4**0.5": "2.00000000000000", "(1/3)**(x)": "(1/3)**x", "exp(3*log(10))*x": "1000*x",
                "exp(log(x)*2)": "x**2", "(2*x)**3": "8*x**3", "(abs(2)**10)**10": str(2 ** 100)}
    for text, shown in expected.items():
        assert str(sdata.formula(text).as_sympy()) == shown, text
    assert sdata.formula("(999*x)**100").as_sympy() == 999 ** 100 * _sp()[1] ** 100  # 300 digits: allowed


# ---- B: series decimals: rising terms, room for the integrals' accuracy, fewer terms kept
def test_review3_b_terms_that_rise_to_zero_are_bounded_as_minus_their_sum():
    from simplydata._calculus import _sum_between

    sp, _ = _sp()
    k = sp.Symbol("k", integer=True)
    low, high, _ = _sum_between(sp, 1 / k ** 2, k, 1, 10, "s")
    minus_low, minus_high, _ = _sum_between(sp, -1 / k ** 2, k, 1, 10, "s")  # 2ded4aa: refused ("keep falling")
    assert (minus_low, minus_high) == (-high, -low)
    assert minus_low <= -sp.pi ** 2 / 6 <= minus_high


def test_review3_b_the_bounds_leave_room_for_the_accuracy_of_the_integrals():
    from simplydata._calculus import _sum_between

    sp, _ = _sp()
    k = sp.Symbol("k", integer=True)
    low, high, bends_up = _sum_between(sp, 1 / k ** 2, k, 1, 10, "s")
    assert bends_up
    first = sum(sp.Rational(1, i ** 2) for i in range(1, 11))
    exact_low = first + sp.Rational(1, 10) - sp.Rational(1, 200)  # trapezoid: integral from 10, less f(10)/2
    exact_high = first + sp.Rational(2, 21)  # midpoint: integral from 10.5
    accuracy = sp.Float(2, 40) ** -99 * (first + sp.Rational(1, 10))  # evalf's integrals are sure to 100 bits
    assert exact_low - low >= accuracy and high - exact_high >= accuracy  # 2ded4aa: room 1e-32 only
    assert low <= sp.pi ** 2 / 6 <= high


def test_review3_b_the_bounds_of_fewer_terms_are_kept_when_more_terms_fail(monkeypatch, capsys):
    from simplydata import _calculus

    sp, _ = _sp()
    k = sp.Symbol("k", integer=True)
    real = _calculus._sum_between

    def fails_with_more(sp_, term, k_, start, count, said):
        if count > 10:
            raise sdata.SimplydataError("SymPy evalf took longer than 60 seconds")
        return real(sp_, term, k_, start, count, said)

    monkeypatch.setattr(_calculus, "TERMS_ONE_BY_ONE", (10, 20))
    monkeypatch.setattr(_calculus, "_sum_between", fails_with_more)
    value = _calculus._settled_decimal(sp, 1 / k ** 2, k, sp.Integer(1), sp.oo, "s")  # 2ded4aa: the error
    assert value == pytest.approx(math.pi ** 2 / 6, rel=1e-4)
    assert "the first 10 terms" in capsys.readouterr().out


def test_review3_b_a_series_of_negative_terms_has_its_decimal(capsys):
    sp, _ = _sp()
    k = sp.Symbol("k", integer=True)
    value = sdata.find_sum_of_series("-1/(k**3 + k + 1)", between=[1, "infinity"])  # 2ded4aa: refused
    reference = -sp.Sum(1 / (k ** 3 + k + 1), (k, 1, sp.oo)).evalf(30)
    assert value == pytest.approx(float(reference), rel=1e-12)
    assert _correctly_rounded(float(reference), _printed_sum(capsys.readouterr().out))


# ---- C: a repeating rule over a long finite range, and after a rule SymPy could not solve
def test_review3_c_a_long_finite_range_says_how_many_repeats():
    with pytest.raises(sdata.SimplydataError, match="covers 15,916 repeats, more than the 1,000") as info:
        sdata.solve(["sin(x) > 0", "x > 0", "x < 100000"], exactly=True)
    assert "finite length" not in str(info.value)  # 2ded4aa: advised a finite range, which it already was


def test_review3_c_a_rule_sympy_could_not_solve_is_said_before_a_repeating_one():
    with pytest.raises(sdata.SimplydataError, match="SymPy could not solve"):
        sdata.solve(["abs(sin(x)) <= 1", "sin(x) > 0"], exactly=True)  # 2ded4aa: NotImplementedError (ConditionSet)


# ---- H: a formula with no value on the whole range has no smallest or biggest value there
def test_review3_h_no_value_on_the_range_is_said(capsys):
    geometric = sdata.find_sum_of_series("r**k", between=[0, "infinity"], for_letter="k")
    with pytest.raises(sdata.SimplydataError, match="found no smallest value"):
        sdata.find_where_smallest(geometric, between=[-3, -2])  # 2ded4aa: "infinite, at r = -2"
    with pytest.raises(sdata.SimplydataError, match="found no biggest value"):
        sdata.find_where_biggest(geometric, between=[1.5, 3])  # 2ded4aa: "minus infinite, at r = 3"
    with pytest.raises(sdata.SimplydataError, match="found no smallest value .*not a number or is infinite"):
        sdata.find_where_smallest("log(x)", between=[-3, -1])
    assert "infinite, at" not in capsys.readouterr().out
    smallest = sdata.find_where_smallest("x - log(x)", between=[-1, 3])  # a value on part of the range: found
    assert smallest.get_cell_at(row=1, column="smallest value") == pytest.approx(1.0, rel=1e-9)


# ---- put_in: a letter with a kind takes a number, or one letter of that kind, never a free expression
def test_review3_put_in_an_expression_for_a_letter_with_a_kind_is_refused():
    sp, _ = _sp()
    f = sdata.formula("sqrt(x**2)", letters_are={"x": "positive"})
    for new in ("y + 1", "2*y"):
        with pytest.raises(sdata.SimplydataError, match=f"cannot put {re.escape(new)} in place of x: the formula "
                                                         "says x is positive"):
            f.put_in(x=new)  # 2ded4aa: y + 1, then put_in(y=-5) gave -4 (sqrt((-5 + 1)**2) is 4)
    assert "y (positive)" in repr(f.put_in(x="y"))
    both = sdata.formula("sqrt(x**2) + y", letters_are={"x": "positive", "y": "positive"})
    y = sp.Symbol("y", positive=True)
    assert both.put_in(x="2*y").as_sympy() == 3 * y  # SymPy shows 2*y is positive
    assert sdata.formula("sqrt(x**2)").put_in(x="y + 1").put_in(y=-5).as_sympy() == 4  # no kind: as before


# ================================================================ fourth review of 5417466 (each test fails on that commit)
# ---- N1 and N6: an exp(c) base, and products and sums of allowed numbers, are sized too
@pytest.mark.parametrize("text", ["exp(2)**(1500*log(10))", "x*exp(2)**(1500*log(10))", "exp(3)**(1000*log(10))",
                                  "sqrt(exp(2))**(3000*log(10))", "999**100*999**100*999**100*999**100",
                                  "exp(900*log(10))*exp(900*log(10))", "exp(log(2)*3000 + log(3)*2000)",
                                  "2**3000*3**2000", "1/999**100 + 1/998**100 + 1/997**100 + 1/996**100"])
def test_review4_a_exp_bases_products_and_sums_are_sized(text):
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula(text)  # 5417466: accepted, with 1,200 to 3,001 digits


def test_review4_a_what_sympy_leaves_as_it_is_is_still_read():
    sp, x = _sp()
    assert sdata.formula("exp(2)**x").as_sympy() == sp.exp(2 * x)
    assert sdata.formula("(x + 999)**400").as_sympy() == (x + 999) ** 400  # never multiplied out
    assert sdata.formula("exp(log(2)*1000)**3").as_sympy() == 2 ** 3000  # 904 digits: allowed
    assert sdata.formula("999**100*999**100*999**100").as_sympy() == 999 ** 300  # 900 digits: allowed
    assert sdata.formula("(2**sqrt(2))**(1000*sqrt(2))").as_sympy() == 2 ** 2000  # 603 digits: allowed


def test_review4_a_a_power_of_a_product_of_roots_counts_every_root():
    # 2**420 * 3**630 * 5**700 * 7**720 has 1,520 digits (by hand: 420*0.301 + 630*0.477 + 700*0.699 + 720*0.845)
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula("(2**(1/2)*3**(3/4)*5**(5/6)*7**(6/7))**840")  # 5417466: sized as 840*log10(7), 710 digits


# ---- N5: put_in() keeps the 1,000-digit rule, sized before SymPy makes the number
def test_review4_n5_put_in_keeps_the_digit_rule():
    for made in (lambda: sdata.formula("2**x").put_in(x=10000), lambda: sdata.formula("exp(log(10)*x)").put_in(x=3000),
                 lambda: sdata.formula("x**100").put_in(x="y**100").put_in(y=999),
                 lambda: sdata.formula("(x + 999)**400").put_in(x=1)):
        with pytest.raises(sdata.SimplydataError,
                           match=re.escape("put_in() would make a number with more than 1000 digits")):
            made()  # 5417466: 3,011, 3,001, 29,996 and 1,201 digits
    with pytest.raises(sdata.SimplydataError, match=re.escape("would give gamma() a number bigger than 1000")):
        sdata.formula("gamma(x)").put_in(x=2000)  # as formula("gamma(2000)") is refused
    sp, x = _sp()
    y = sp.Symbol("y")
    assert sdata.formula("2**x").put_in(x=100).as_sympy() == 2 ** 100
    assert sdata.formula("(x + 999)**400").put_in(x="y").as_sympy() == (y + 999) ** 400
    assert sdata.formula("x + 10*y").put_in(x="y", y=2).as_sympy() == 22  # SymPy subs order, as before


def test_review4_n5_put_in_of_a_huge_power_is_refused_at_once():
    started = time.monotonic()
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula("2**x").put_in(x=10 ** 10)  # 5417466: 2**(10**10) made by the helper (about 1.25 GB)
    assert time.monotonic() - started < 30


# ---- N3: put_in() never makes two letters with one name
def test_review4_n3_put_in_never_makes_two_letters_with_one_name():
    sp, _ = _sp()
    f = sdata.formula("sqrt(x**2) + sqrt(w**2)", letters_are={"x": "positive", "w": "negative"})
    with pytest.raises(sdata.SimplydataError, match="would make two different letters called z, one negative and one "
                                                    "positive"):
        f.put_in(x="z", w="z")  # 5417466: -z + z, which is not 0
    g = sdata.formula("sqrt(x**2) + w", letters_are={"x": "positive"})
    with pytest.raises(sdata.SimplydataError, match="two different letters called z"):
        g.put_in(x="z", w="z + 1")  # a positive z and a plain z
    z = sp.Symbol("z", positive=True)
    same = sdata.formula("sqrt(x**2) + sqrt(w**2)", letters_are={"x": "positive", "w": "positive"})
    assert same.put_in(x="z", w="z").as_sympy() == 2 * z  # one kind: one letter


# ---- the refusal sentences name an example that fits the kind
@pytest.mark.parametrize("kind, example, expression", [
    ("positive", "sqrt(x**2) is x for a positive x (not for a negative one)", "2*y with y positive"),
    ("real", "abs(x)**2 is x**2 for a real x (not for x = sqrt(-1))", "y + 1 with y real"),
    ("whole number", "cos(pi*x)**2 is 1 for a whole x (not for x = 1/2)", "n + 1 with n a whole number")])
def test_review4_put_in_sentence_fits_the_kind(kind, example, expression):
    with pytest.raises(sdata.SimplydataError) as info:
        sdata.formula("x + 1", letters_are={"x": kind}).put_in(x="sqrt(-1)")
    said = str(info.value)
    words = f"{'a ' if 'whole' in kind else ''}{kind}"
    assert f"({example})" in said and f"Put in a number that is {words}," in said  # 5417466: sqrt(x**2), every kind
    assert f"or an expression SymPy can show is {words} ({expression})" in said
    with pytest.raises(sdata.SimplydataError,
                       match=re.escape("(sqrt(x**2) is -x for a negative x (not for a positive one))")):
        sdata.formula("sqrt(x**2)", letters_are={"x": "negative"}).put_in(x=2)


def test_review4_the_kind_examples_are_what_sympy_does():
    sp, _ = _sp()
    assert sp.sqrt(sp.Symbol("x", positive=True) ** 2) == sp.Symbol("x", positive=True)
    assert sp.sqrt(sp.Symbol("x", nonnegative=True) ** 2) == sp.Symbol("x", nonnegative=True)
    assert sp.sqrt(sp.Symbol("x", negative=True) ** 2) == -sp.Symbol("x", negative=True)
    assert abs(sp.Symbol("x", real=True)) ** 2 == sp.Symbol("x", real=True) ** 2
    assert sp.cos(sp.pi * sp.Symbol("x", integer=True)) ** 2 == 1
    assert sp.cos(sp.pi * sp.Symbol("x")) ** 2 != 1 and abs(sp.Symbol("x")) ** 2 != sp.Symbol("x") ** 2


# ---- B and C: SymPy's own errors
def test_review4_b_the_bounds_of_fewer_terms_are_kept_when_sympy_fails_with_more(monkeypatch, capsys):
    from simplydata import _calculus

    sp, _ = _sp()
    k = sp.Symbol("k", integer=True)
    real = _calculus._sum_between

    def fails_with_more(sp_, term, k_, start, count, said):
        if count > 10:
            raise NotImplementedError("SymPy integrate")  # as the helper gives SymPy's own error back
        return real(sp_, term, k_, start, count, said)

    monkeypatch.setattr(_calculus, "TERMS_ONE_BY_ONE", (10, 20))
    monkeypatch.setattr(_calculus, "_sum_between", fails_with_more)
    value = _calculus._settled_decimal(sp, 1 / k ** 2, k, sp.Integer(1), sp.oo, "s")  # 5417466: NotImplementedError
    assert value == pytest.approx(math.pi ** 2 / 6, rel=1e-4)
    assert "the first 10 terms" in capsys.readouterr().out


def test_review4_c_rules_reduce_inequalities_cannot_do_are_said():
    with pytest.raises(sdata.SimplydataError, match=re.escape("SymPy could not solve x**x > 2 and sin(x) > 0")):
        sdata.solve(["x**x > 2", "sin(x) > 0", "x < 10", "x > 0"], exactly=True)  # 5417466: NotImplementedError


# ---------------------------------------------------------------- fifth review of 4c306e1
# ---- NEW-A: a sum or a product with letters has the digits of its biggest number, not of all its numbers together
def test_review5_new_a_numbers_next_to_different_letters_are_not_added_up(capsys):
    sp, x = _sp()
    y, z, w = sp.symbols("y z w")
    big = sp.Integer(999) ** 100  # 300 digits
    ten = sp.Integer(10) ** 300
    cases = {  # each refused on 4c306e1 as "a number with more than 1000 digits"; SymPy keeps every number apart
        "999**100*x + 999**100*y + 999**100*z + 999**100*w": big * (x + y + z + w),
        "(x + 999**100)*(y + 999**100)*(z + 999**100)*(w + 999**100)": (x + big) * (y + big) * (z + big) * (w + big),
        " + ".join(f"exp(300*log(10))*{v}" for v in "xyzw"): ten * x + ten * y + ten * z + ten * w,
        " + ".join(f"12345678901234567890123456*x**{k}" for k in range(40)):
            sp.Add(*[12345678901234567890123456 * x ** k for k in range(40)]),
    }
    for text, sympy_says in cases.items():
        assert sdata.formula(text).as_sympy() == sympy_says, text
    put = sdata.formula("a*x + b*y + c*z + d*w").put_in(a=999 ** 100, b=999 ** 100, c=999 ** 100, d=999 ** 100)
    assert put.as_sympy() == big * (x + y + z + w)  # 4c306e1: refused
    capsys.readouterr()


def test_review5_new_a_long_sums_of_small_terms_are_read(capsys):
    sp, x = _sp()
    harmonic = sdata.formula(" + ".join(f"sin({k}*x)/{k}" for k in range(1, 261)))  # 4c306e1: more than 1000 digits
    assert harmonic.as_sympy() == sp.Add(*[sp.sin(k * x) / k for k in range(1, 261)])
    shifted = sdata.formula(" + ".join(f"sin(x + {k})" for k in range(1, 501)))  # 4c306e1: RecursionError
    assert shifted.as_sympy() == sp.Add(*[sp.sin(x + k) for k in range(1, 501)])
    signs = " - ".join(f"{k}*x**{k % 7}/{k + 1}" for k in range(1, 401))  # read 100 terms at a time, signs kept
    assert sdata.formula(signs).as_sympy() == sp.Rational(1, 2) * x - sp.Add(
        *[sp.Rational(k, k + 1) * x ** (k % 7) for k in range(2, 401)])
    # a long product is read 100 factors at a time, so every Python gives the exact answer (7df315c: refused on
    # Python 3.12 and 3.13, whose reader gives up on 1,200 factors; read on 3.11)
    assert sdata.formula("*".join(["x"] * 1200)).as_sympy() == x ** 1200
    division = "x/" + "/".join(str(k) for k in range(2, 301))  # / stays division: x/300!
    assert sdata.formula(division).as_sympy() == x / sp.factorial(300)
    assert sdata.formula("*".join(["x"] * 150) + "/" + "/".join(["y"] * 150)).as_sympy() == x ** 150 / \
        sp.Symbol("y") ** 150
    assert sdata.formula("y - " + "*".join(["x"] * 250) + " + 3*y").as_sympy() == 4 * sp.Symbol("y") - x ** 250
    assert sdata.formula(" + ".join(["*".join(["x"] * 300)] * 5)).as_sympy() == 5 * x ** 300  # a sum of long products
    assert sdata.formula("*".join(["999"] * 300)).as_sympy() == sp.Integer(999) ** 300  # 900 digits: allowed
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula("*".join(["999"] * 340))  # 1,020 digits: the digit rule holds across the pieces
    # brackets 250 deep: Python's tokenizer stops at 200 nested brackets on every version (3.11, 3.12, 3.13)
    with pytest.raises(sdata.SimplydataError, match="too many steps one inside another to be read"):
        sdata.formula("(" * 250 + "x" + ")" * 250)
    capsys.readouterr()


def test_review6_long_products_and_sums_inside_brackets_are_read_in_pieces(capsys):
    # 25d4c26 read a long product in pieces only outside every bracket: inside brackets (or as a function's value)
    # it was refused as "too many steps one inside another", while the same product without brackets was read
    sp, x = _sp()
    y, z = sp.Symbol("y"), sp.Symbol("z")
    product = "*".join(["x"] * 1200)
    assert sdata.formula("(" + product + ")").as_sympy() == x ** 1200
    assert sdata.formula("sin(" + product + ")").as_sympy() == sp.sin(x ** 1200)
    division = "x/" + "/".join(str(k) for k in range(2, 301))
    assert sdata.formula("exp(-(" + division + "))").as_sympy() == sp.exp(-x / sp.factorial(300))
    division += "/" + "/".join(["y"] * 900)  # / stays division in every piece
    assert sdata.formula("exp(-(" + division + "))").as_sympy() == sp.exp(-x / (sp.factorial(300) * y ** 900))
    long_sum = " + ".join(f"a{k}" for k in range(1, 1201))
    assert sdata.formula("(" + long_sum + ")*y").as_sympy() == y * sp.Add(*sp.symbols("a1:1201"))
    product_in_sum = product + "".join(f" + {k}*y" for k in range(1, 1201))
    assert sdata.formula("z*(" + product_in_sum + ")").as_sympy() == z * (x ** 1200 + 720600 * y)
    assert sdata.formula("atan2(y, " + product + ")").as_sympy() == sp.atan2(y, x ** 1200)  # both values kept
    assert sdata.formula("sin(cos(" + product + ") + 1)").as_sympy() == sp.sin(sp.cos(x ** 1200) + 1)
    assert sdata.formula("sin(" + "*".join(["999"] * 300) + ")").as_sympy() == sp.sin(sp.Integer(999) ** 300)
    with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
        sdata.formula("sin(" + "*".join(["999"] * 340) + ")")  # 1,020 digits: the digit rule holds inside brackets
    with pytest.raises(sdata.SimplydataError, match="too many steps one inside another to be read"):
        sdata.formula("(" * 250 + "x" + ")" * 250)
    with pytest.raises(sdata.SimplydataError, match=r'"\(\.\.\.\)%2"'):  # the sentence shows ... for the long value
        sdata.formula("(" + product + ")%2")
    capsys.readouterr()


def test_review5_new_a_numbers_sympy_puts_together_are_still_refused():
    refused = ["999**100*999**100*999**100*999**100",  # multiplied: 1,200 digits
               "(999**100*x)*(999**100*y)*(999**100*z)*(999**100*w)",  # SymPy multiplies the numbers of a product
               "x/7**300 + x/11**300 + x/13**300 + x/17**300",  # like terms: the bottoms are multiplied
               "999**200*(x + 999**200)",  # a number times a sum goes into each term: 999**400
               "999**150*(x + 999**200)",
               "(999**50*x)**2*(999**50*y)**2*(999**50*z)**2*(999**50*w)**2",
               "abs(999**200*x)*abs(999**200*y)*abs(999**200*z)"]  # abs takes the number out
    for text in refused:
        with pytest.raises(sdata.SimplydataError, match="has a number with more than 1000 digits"):
            sdata.formula(text)
    with pytest.raises(sdata.SimplydataError, match="put_in.. would make a number with more than 1000 digits"):
        sdata.formula("x*(y + 999**200)").put_in(x=999 ** 200)
    with pytest.raises(sdata.SimplydataError, match="put_in.. would make a number with more than 1000 digits"):
        sdata.formula("a*x + b*x + c*x + d*x").put_in(a="1/7**300", b="1/11**300", c="1/13**300", d="1/17**300")


def test_review5_ten_to_the_thousand_has_1001_digits_and_is_refused(capsys):
    assert len(str(10 ** 1000)) == 1001 and len(str(2 ** 3321)) == 1000 and len(str(2 ** 3322)) == 1001
    for text in ["10**1000", "exp(log(10)*1000)"]:  # 4c306e1: accepted, with 1,001 digits
        with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
            sdata.formula(text)
    for name, value in [("10**x", 1000), ("2**x", 3322)]:
        with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
            sdata.formula(name).put_in(x=value)
    assert sdata.formula("2**3321").as_sympy() == 2 ** 3321  # 1,000 digits: allowed
    assert sdata.formula("10**999").as_sympy() == 10 ** 999
    capsys.readouterr()


def test_review5_the_not_for_examples_are_what_sympy_does():
    sp, _ = _sp()
    assert sp.sqrt(sp.Integer(-1) ** 2) != -1 and sp.sqrt(sp.Integer(2) ** 2) != -2  # not for a negative / positive one
    assert abs(sp.sqrt(-1)) ** 2 != sp.sqrt(-1) ** 2 and sp.cos(sp.pi / 2) ** 2 != 1  # not for sqrt(-1), not for 1/2
    assert sp.sqrt(sp.Integer(0) ** 2) == 0  # 0 is fine: "only for a positive x" was not true at 0


def test_review_5_put_in_is_stopped_by_the_time_limit(tmp_path):
    # a long sum with letters only: no number above 1 and no special function, so neither the 1,000-digit rule nor
    # the special-function rule refuses it; SymPy subs on 3,000 terms takes about 1 s, against a limit of 0.05 s
    result = _run_code(tmp_path, """
        import simplydata as sdata
        from simplydata import _time_limit
        f = sdata.formula(" + ".join(f"sin(x + a{k})" for k in range(1, 3001)))
        _time_limit.TIME_LIMIT = 0.05
        try:
            f.put_in(x=1)
        except sdata.SimplydataError as error:
            print("STOPPED", str(error).splitlines()[0])
        _time_limit.TIME_LIMIT = 60
        print("DONE", len(f.put_in(x=1).as_sympy().args))  # the same put_in finishes: the time limit stopped it
    """, seconds=120)
    assert "STOPPED SymPy subs did not finish in 0.05 seconds" in result.stdout, result.stderr
    assert "DONE 3000" in result.stdout
