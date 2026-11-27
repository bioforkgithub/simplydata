"""Numbers phase, batch 3: fixes after the independent review. Each test failed before its fix; each compares with
SymPy, SciPy or NumPy directly, or with the answer worked out by hand."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from scipy import integrate, special

import simplydata as sdata


# ---------------------------------------------------------------- 1. limits at infinity keep their sign
@pytest.mark.parametrize("text, goes_to, expected", [
    ("1/x**2", 0, math.inf), ("x", "infinity", math.inf), ("-x", "infinity", -math.inf),
    ("x**3", "-infinity", -math.inf), ("exp(x)", "infinity", math.inf), ("-1/x**2", 0, -math.inf),
])
def test_find_limit_as_keeps_the_sign_of_infinity(needs_sympy, text, goes_to, expected):
    import sympy as sp

    x = sp.Symbol("x")
    target = {0: 0, "infinity": sp.oo, "-infinity": -sp.oo}[goes_to]
    assert sp.limit(sdata.formula(text)._expr, x, target) == (sp.oo if expected > 0 else -sp.oo)
    assert sdata.formula(text).find_limit_as("x", goes_to=goes_to) == expected


def test_find_limit_as_refuses_complex_infinity_plainly(needs_sympy):
    with pytest.raises(sdata.SimplydataError, match="different values from the two sides"):
        sdata.formula("1/x").find_limit_as("x", goes_to=0)


# ---------------------------------------------------------------- 2. the times of time_step= never pass the end
@pytest.mark.parametrize("end, step", [(0.3, 0.1), (0.7, 0.1), (0.6, 0.2), (2.3, 0.1)])
def test_time_step_that_fits_the_span_ends_exactly_at_the_end(end, step):
    path = sdata.find_path_over_time("dN/dt = -N", at_start={"N": 1}, between=[0, end], time_step=step).as_pandas()
    count = round(end / step)
    np.testing.assert_array_equal(path["time"], np.linspace(0, end, count + 1))
    np.testing.assert_allclose(path["N"], np.exp(-path["time"]), rtol=1e-5)  # the closed form exp(-t)


def test_time_step_that_does_not_fit_stops_before_the_end(capsys):
    path = sdata.find_path_over_time("dN/dt = -N", at_start={"N": 1}, between=[0, 1], time_step=0.3).as_pandas()
    np.testing.assert_allclose(path["time"], [0, 0.3, 0.6, 0.9], rtol=1e-15)
    assert "last time in the table is 0.9" in capsys.readouterr().out


# ---------------------------------------------------------------- 3. stop_when= already true at the start
@pytest.mark.parametrize("change, start", [("0.1*N", 950), ("-0.1*N", 1000)])
def test_stop_when_true_at_the_start_stops_at_once(change, start, capsys):
    path = sdata.find_path_over_time(f"dN/dt = {change}", at_start={"N": start}, between=[0, 10],
                                     stop_when="N >= 900", time_step=1).as_pandas()
    assert path["time"].tolist() == [0.0] and path["N"].tolist() == [start]
    out = capsys.readouterr().out
    assert "already true at the start" in out and "never came true" not in out


def test_stop_when_that_comes_true_by_falling():
    path = sdata.find_path_over_time("dN/dt = -0.1*N", at_start={"N": 1000}, between=[0, 10],
                                     stop_when="N <= 900").as_pandas()
    assert path["time"].iloc[-1] == pytest.approx(10 * math.log(10 / 9), abs=1e-4)  # 1000 exp(-0.1 t) = 900


# ---------------------------------------------------------------- 4. areas that do not settle on a number
def test_find_area_under_says_when_the_area_does_not_exist(needs_sympy):
    import sympy as sp

    x = sp.Symbol("x")
    assert sp.integrate(1 / x, (x, -1, 1)) is sp.nan
    with pytest.raises(sdata.SimplydataError, match="does not settle on a number"):
        sdata.find_area_under("1/x", between=[-1, 1], exactly=True)
    assert sp.integrate(1 / x, (x, 0, 1)) == sp.oo
    with pytest.raises(sdata.SimplydataError, match="is infinite"):
        sdata.find_area_under("1/x", between=[0, 1], exactly=True)


def test_find_area_under_numbers_explain_a_division_by_zero_inside_the_range():
    with pytest.raises(ZeroDivisionError):
        integrate.quad(lambda x: 1 / x, -1, 1)  # SciPy itself stops at x = 0
    with pytest.raises(sdata.SimplydataError, match="Split the range"):
        sdata.find_area_under("1/x", between=[-1, 1])


# ---------------------------------------------------------------- 5. lgamma is log|gamma| for one value and many
def test_lgamma_is_scipy_gammaln_for_one_value_and_for_many(needs_sympy):
    f = sdata.formula("lgamma(x)")
    assert f.find_value_at(x=-0.5) == special.gammaln(-0.5)
    np.testing.assert_array_equal(f.find_value_at(x=[-0.5, 3, 200]).as_numpy(), special.gammaln([-0.5, 3, 200]))
    assert f.find_value_at(x=3) == pytest.approx(math.log(2), rel=1e-15)


# ---------------------------------------------------------------- 6. the fraction example says what happens
def test_show_as_fraction_docstring_matches_what_it_shows(needs_sympy, capsys):
    import sympy as sp

    doc = sdata.Numbers.show_as_fraction.__doc__
    assert "0.333333 as 1/3" not in doc and "333333/1000000" in doc
    sdata.number_list([0.333333, 1 / 3, 0.25]).show_as_fraction()
    expected = [str(sp.nsimplify(v, rational=True)) for v in (0.333333, 1 / 3, 0.25)]
    assert capsys.readouterr().out.splitlines()[0] == "[" + ", ".join(expected) + "]" == "[333333/1000000, 1/3, 1/4]"


# ---------------------------------------------------------------- 7. solve(exactly=True) says when there are more
def test_solve_exactly_says_when_sympy_listed_only_some_solutions(needs_sympy, capsys):
    import sympy as sp

    x = sp.Symbol("x")
    assert isinstance(sp.solveset(sp.sin(x), x), sp.Union)  # endless: every n pi
    sdata.solve("sin(x) = 0", exactly=True)
    out = capsys.readouterr().out
    assert "there are more" in out and "repeats without end" in out
    sdata.solve("x**2 = 2", exactly=True)
    assert "These are all the solutions" in capsys.readouterr().out


# ---------------------------------------------------------------- 8. smaller fixes
def test_huge_powers_of_numbers_are_refused_before_sympy_works_them_out(needs_sympy):
    for text in ("9**9**9", "x**(9**9**9)", "10**1001", "2^5000"):
        with pytest.raises(sdata.SimplydataError, match="more than 1000 digits"):
            sdata.formula(text)
    assert sdata.formula("2**3000")._expr == 2 ** 3000  # 904 digits: still fine


@pytest.mark.parametrize("name", ["Integer", "Float", "Rational", "Symbol", "Function", "Lambda"])
def test_letters_named_like_sympys_own_reader_names_are_refused_plainly(needs_sympy, name):
    with pytest.raises(sdata.SimplydataError, match="SymPy uses that name itself"):
        sdata.formula(f"{name} + 1")


def test_letters_named_like_sympy_constants_stay_letters(needs_sympy):
    import sympy as sp

    f = sdata.formula("S + N + E + I + Q + O")
    assert f._expr == sum(sp.Symbol(n) for n in "SNEIQO")


def test_find_fence_around_needs_two_different_columns():
    table = sdata.table(pd.DataFrame({"x": [0, 1, 0], "y": [0, 0, 1]}))
    with pytest.raises(sdata.SimplydataError, match="two different columns"):
        table.find_fence_around(x="x", y="x")


def test_find_value_at_an_empty_value_gives_an_empty_answer(needs_sympy):
    f = sdata.formula("x**2 + 1")
    assert math.isnan(f.find_value_at(x=float("nan")))
    assert np.isnan(f.find_value_at(x=[1, float("nan")]).as_numpy()[1])


def test_coherence_help_says_when_its_segments_differ_from_scipy():
    doc = sdata.Numbers.find_coherence_with.__doc__
    assert "1152 readings" in doc and "no padding" in doc and "only this rule follows MATLAB mscohere" in doc
