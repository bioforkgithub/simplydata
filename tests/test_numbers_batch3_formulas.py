"""Numbers phase, batch 3: sdata.formula and its words, solve(exactly=True) and show_as_fraction (SymPy).

Each answer is compared with SymPy doing the same, and with the answer worked out by hand where there is one.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import simplydata as sdata
from simplydata import learn

pytestmark = pytest.mark.usefixtures("needs_sympy")


def _sp():
    import sympy as sp

    return sp, sp.Symbol("x")


def test_formula_is_read_by_sympy_with_every_letter_a_symbol(capsys):
    sp, x = _sp()
    f = sdata.formula("(x + 2)**2 - 4")
    assert f._expr == (x + 2) ** 2 - 4
    assert "letter x" in capsys.readouterr().out
    g = sdata.formula("E*I + N + beta^2")  # SymPy alone reads E, I and N as its own things; ^ is a power
    assert sorted(str(s) for s in g._expr.free_symbols) == ["E", "I", "N", "beta"]
    assert g._expr == sp.Symbol("E") * sp.Symbol("I") + sp.Symbol("N") + sp.Symbol("beta") ** 2


@pytest.mark.parametrize("text, problem", [
    ("x = 2", "equation"), ("__import__('os')", "not a function"), ("_x + 1", "cannot be a letter"), ("x.real", "dot"),
    ("open(x)", "not a function"), ("2x", "cannot be read"), ("exp", "brackets"), ("'a'", "only numbers"),
    ("x < 1", "equation"), ("lambda: 1", "not allowed"),
])
def test_formula_text_is_checked_before_sympy_reads_it(text, problem):
    with pytest.raises(sdata.SimplydataError, match=problem):
        sdata.formula(text)


def test_formula_words_match_sympy():
    sp, x = _sp()
    f = sdata.formula("(x + 2)**2 - 4")
    assert f.turn_into_sum()._expr == sp.expand((x + 2) ** 2 - 4) == x ** 2 + 4 * x
    assert f.turn_into_product()._expr == sp.factor(x ** 2 + 4 * x) == x * (x + 4)
    f.undo()
    assert f._expr == x ** 2 + 4 * x
    f.undo()
    assert f._expr == (x + 2) ** 2 - 4
    assert sdata.formula("(x**2 - 1) / (x - 1)").make_simpler()._expr == x + 1
    g = sdata.formula("x**3 - 2*x")
    assert g.find_slope_formula()._expr == sp.diff(x ** 3 - 2 * x, x) == 3 * x ** 2 - 2
    assert g.find_area_formula()._expr == sp.integrate(x ** 3 - 2 * x, x) == x ** 4 / 4 - x ** 2
    assert g.show_as_latex() == sp.latex(x ** 3 - 2 * x) == "x^{3} - 2 x"
    y = sp.Symbol("y")
    assert sdata.formula("x**2").put_in(x="y + 1")._expr == (y + 1) ** 2


def test_find_value_at_one_value_and_many():
    sp, x = _sp()
    g = sdata.formula("x**3 - 2*x")
    assert g.find_value_at(x=2.5) == 10.625 == float((x ** 3 - 2 * x).subs(x, sp.Rational(5, 2)))
    many = g.find_value_at(x=[0, 1, 2, 3]).as_numpy()
    np.testing.assert_allclose(many, sp.lambdify(x, x ** 3 - 2 * x, "numpy")(np.arange(4.0)), rtol=0, atol=0)
    assert np.allclose(many, [0, -1, 4, 21])
    two = sdata.formula("a * x + b")
    assert two.find_value_at(a=2, x=3, b=1) == 7
    with pytest.raises(sdata.SimplydataError, match="needs a value for every letter"):
        two.find_value_at(a=2, x=3)
    with pytest.raises(sdata.SimplydataError, match="not a letter"):
        g.find_value_at(z=1)
    with pytest.raises(sdata.SimplydataError, match="no value among the ordinary numbers"):
        sdata.formula("sqrt(x)").find_value_at(x=-4)


def test_limits_and_taylor_series_match_sympy_and_the_closed_forms():
    sp, x = _sp()
    assert sdata.formula("sin(x) / x").find_limit_as("x", goes_to=0) == 1.0
    assert sdata.formula("(1 + 1/x)**x").find_limit_as("x", goes_to="infinity") == pytest.approx(math.e, rel=1e-15)
    with pytest.raises(sdata.SimplydataError, match="different values from the two sides"):
        sdata.formula("1 / x").find_limit_as("x", goes_to=0)
    series = sdata.formula("exp(x)").find_taylor_series(around=0, up_to_power=4)
    assert series._expr == sp.series(sp.exp(x), x, 0, n=5).removeO()
    assert series.find_value_at(x=1) == pytest.approx(65 / 24, rel=1e-15)


def test_for_letter_is_needed_with_several_letters():
    f = sdata.formula("a * x**2")
    with pytest.raises(sdata.SimplydataError, match="for_letter="):
        f.find_slope_formula()
    sp, x = _sp()
    assert f.find_slope_formula(for_letter="x")._expr == 2 * sp.Symbol("a") * x


def test_solve_exactly_matches_sympy_and_r_polyroot():
    sp, x = _sp()
    found = sdata.solve("x**2 = 2", exactly=True)
    assert found.get_column("x exactly") == [str(s) for s in sp.solve(sp.Eq(x ** 2, 2), x)]
    assert found.get_column("x").as_numpy().tolist() == pytest.approx([-math.sqrt(2), math.sqrt(2)], rel=1e-15)
    system = sdata.solve(["x + y = 3", "x - y = 1"], exactly=True)
    assert system.get_cell_at(row=1, column="x") == 2 and system.get_cell_at(row=1, column="y") == 1
    complex_roots = sdata.solve("x**2 = -1", exactly=True)
    assert complex_roots.get_column("x exactly") == ["-I", "I"]
    assert np.isnan(complex_roots.get_column("x").as_numpy()).all()
    with pytest.raises(sdata.SimplydataError, match="takes no between="):
        sdata.solve("x**2 = 2", exactly=True, between=[0, 2])
    known = sdata.solve("a * x = 3", exactly=True, known={"a": 2})
    assert known.get_column("x exactly") == ["3/2"]


def test_a_formula_is_accepted_by_find_where_smallest_and_find_area_under():
    f = sdata.formula("(x - 1)**2 + abs(x)")
    assert f._formula_text() == "(x - 1)**2 + abs(x)"
    found = sdata.find_where_smallest(f, between=[-3, 3])
    assert found.get_cell_at(row=1, column="x") == pytest.approx(0.5, abs=1e-8)
    assert sdata.find_area_under(sdata.formula("x**2"), between=[0, 3]) == pytest.approx(9.0, rel=1e-14)
    # names written back as the formula reader knows them
    assert sdata.formula("besselJ(x, 2) + lgamma(x) + sinc(x)")._formula_text() == \
        "besselJ(x, 2) + lgamma(x) + sinc((pi*x)/pi)"


def test_show_as_fraction_matches_sympy_nsimplify(capsys):
    sp, _ = _sp()
    values = [0.5, 0.25, 1 / 3, 1.75, 2 / 7]
    sdata.number_list(values).show_as_fraction()
    first = capsys.readouterr().out.splitlines()[0]
    assert first == "[" + ", ".join(str(sp.nsimplify(v, rational=True)) for v in values) + "]"
    assert first == "[1/2, 1/4, 1/3, 7/4, 2/7]"
    grid = sdata.number_grid([[0.5, None], [1.5, 2]])
    grid.show_as_fraction()
    assert capsys.readouterr().out.splitlines()[:2] == ["[1/2, empty]", "[3/2, 2]"]


def test_show_as_latex_writes_no_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sdata.formula("x**2").show_as_latex()
    assert list(tmp_path.iterdir()) == []


def test_formula_names_from_other_tools_point_to_the_words():
    f = sdata.formula("x**2")
    for name, word in [("diff", "find_slope_formula"), ("simplify", "make_simpler"), ("expand", "turn_into_sum"),
                       ("subs", "put_in"), ("latex", "show_as_latex"), ("limit", "find_limit_as"),
                       ("series", "find_taylor_series")]:
        with pytest.raises(AttributeError, match=word):
            getattr(f, name)
    for name, word in [("simplify", "formula"), ("parse_expr", "formula"), ("solveset", "solve"),
                       ("quad", "find_area_under"), ("dblquad", "find_volume_under"),
                       ("solve_ivp", "find_path_over_time"), ("odeint", "find_path_over_time")]:
        with pytest.raises(AttributeError, match=word):
            getattr(sdata, name)


def test_every_formula_word_is_in_a_group_with_an_example():
    keys = learn._all_keys()
    from simplydata._formula import Formula

    assert all(f"f.{w}" in keys for w in Formula._word_names())
    assert learn._lookup("f.make_simpler") == "f.make_simpler"
    for word in Formula._word_names():
        assert f"f.{word}" in learn.HELP_EXAMPLES


def test_without_sympy_the_words_say_how_to_install_it(monkeypatch):
    import builtins

    real = builtins.__import__

    def no_sympy(name, *args, **kwargs):
        if name == "sympy" or name.startswith("sympy."):
            raise ImportError("no sympy")
        return real(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_sympy)
    with pytest.raises(sdata.SimplydataError, match=r'pip install "simplydata\[exact\]"'):
        sdata.formula("x**2")
    with pytest.raises(sdata.SimplydataError, match=r"simplydata\[exact\]"):
        sdata.solve("x**2 = 2", exactly=True)
    with pytest.raises(sdata.SimplydataError, match=r"simplydata\[exact\]"):
        sdata.number_list([0.5]).show_as_fraction()
