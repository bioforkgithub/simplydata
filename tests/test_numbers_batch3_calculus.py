"""Numbers phase, batch 3: sdata.find_area_under, find_volume_under, find_path_over_time (SciPy integrate) and
nums.turn_into_running_area. Each answer against SciPy doing the same and against the closed form worked out by hand.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import integrate

import simplydata as sdata


def test_find_area_under_is_scipy_quad_and_the_closed_form(capsys):
    area = sdata.find_area_under("exp(-x**2)", between=[0, "infinity"])
    assert area == integrate.quad(lambda x: np.exp(-x ** 2), 0, np.inf)[0]
    assert area == pytest.approx(math.sqrt(math.pi) / 2, rel=1e-13)
    assert "SciPy integrate.quad" in capsys.readouterr().out
    assert sdata.find_area_under("sin(x)", between=[0, math.pi]) == pytest.approx(2.0, rel=1e-14)
    assert sdata.find_area_under("1 / (1 + x**2)", between=["-infinity", "infinity"]) == pytest.approx(math.pi,
                                                                                                    rel=1e-12)
    assert sdata.find_area_under("a * x", between=[0, 2], known={"a": 3}) == pytest.approx(6.0, rel=1e-14)


def test_find_area_under_gauss_and_exactly():
    gauss = sdata.find_area_under("x**4", between=[0, 2], test_method="gauss")
    assert gauss == integrate.fixed_quad(lambda x: x ** 4, 0, 2, n=5)[0]
    assert gauss == pytest.approx(6.4, rel=1e-14)
    with pytest.raises(sdata.SimplydataError, match="romberg"):
        sdata.find_area_under("x", between=[0, 1], test_method="romberg")
    with pytest.raises(sdata.SimplydataError, match="infinity"):
        sdata.find_area_under("exp(-x)", between=[0, "infinity"], test_method="gauss")


def test_find_area_under_exactly_is_sympy(needs_sympy):
    import sympy as sp

    exact = sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], exactly=True)
    x = sp.Symbol("x")
    assert exact._expr == sp.integrate(sp.exp(-x ** 2), (x, 0, sp.oo)) == sp.sqrt(sp.pi) / 2
    assert exact.find_value_at() == pytest.approx(math.sqrt(math.pi) / 2, rel=1e-15)


@pytest.mark.parametrize("call, problem", [
    (lambda: sdata.find_area_under("x * y", between=[0, 1]), "one letter"),
    (lambda: sdata.find_area_under("x", between=[1, 0]), "lower value to a higher"),
    (lambda: sdata.find_area_under("x"), "between="),
    (lambda: sdata.find_area_under("x = 1", between=[0, 1]), "equation"),
    (lambda: sdata.find_volume_under("x * y", between={"x": [0, 1]}), "missing: y"),
    (lambda: sdata.find_volume_under("x", between={"x": [0, 1]}), "two or more letters"),
])
def test_wrong_input_is_explained(call, problem):
    with pytest.raises(sdata.SimplydataError, match=problem):
        call()


def test_find_volume_under_is_dblquad_tplquad_and_nquad():
    vol = sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]})
    assert vol == integrate.dblquad(lambda y, x: x * y ** 2, 0, 1, 0, 2)[0]
    assert vol == pytest.approx(4 / 3, rel=1e-13)
    # the first letter is the outer one: a range that depends on order would show it; constant ranges agree
    assert sdata.find_volume_under("x * y**2", between={"y": [0, 2], "x": [0, 1]}) == pytest.approx(4 / 3, rel=1e-13)
    three = sdata.find_volume_under("x + y + z", between={"x": [0, 1], "y": [0, 1], "z": [0, 1]})
    assert three == integrate.tplquad(lambda z, y, x: x + y + z, 0, 1, 0, 1, 0, 1)[0]
    assert three == pytest.approx(1.5, rel=1e-13)
    four = sdata.find_volume_under("w * x * y * z", between={"w": [0, 1], "x": [0, 1], "y": [0, 1], "z": [0, 1]})
    assert four == pytest.approx(1 / 16, rel=1e-12)


def _logistic(t, n0=10.0, r=0.3, k=1000.0):
    return k / (1 + (k - n0) / n0 * np.exp(-r * t))


def test_find_path_over_time_is_solve_ivp_and_close_to_the_closed_form(capsys):
    path = sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50],
                                     known={"r": 0.3, "K": 1000}, time_step=0.5)
    frame = path.as_pandas()
    assert list(frame.columns) == ["time", "N"]
    s = integrate.solve_ivp(lambda t, n: 0.3 * n * (1 - n / 1000), (0, 50), [10], t_eval=0.5 * np.arange(101),
                            rtol=1e-6, atol=1e-6)
    np.testing.assert_allclose(frame["time"], s.t, rtol=0, atol=0)
    np.testing.assert_allclose(frame["N"], s.y[0], rtol=1e-13)
    np.testing.assert_allclose(frame["N"], _logistic(frame["time"].to_numpy()), rtol=1e-4)
    assert "solve_ivp" in capsys.readouterr().out


def test_find_path_over_time_stops_and_takes_several_equations(capsys):
    path = sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50],
                                     known={"r": 0.3, "K": 1000}, stop_when="N >= 900")
    assert "Stopped when N >= 900" in capsys.readouterr().out
    stop = math.log(9 * 99) / 0.3  # the closed form: N = 900 when exp(0.3 t) = 9 x 99
    assert path.as_pandas()["time"].iloc[-1] == pytest.approx(stop, abs=1e-3)
    # predator and prey (Lotka-Volterra), with SciPy's own LSODA
    pp = sdata.find_path_over_time(["dx/dt = a*x - b*x*y", "dy/dt = c*x*y - d*y"], at_start={"x": 10, "y": 5},
                                   between=[0, 15], known={"a": 1.1, "b": 0.4, "c": 0.1, "d": 0.4}, time_step=1,
                                   test_method="LSODA").as_pandas()
    s = integrate.solve_ivp(lambda t, v: [1.1 * v[0] - 0.4 * v[0] * v[1], 0.1 * v[0] * v[1] - 0.4 * v[1]], (0, 15),
                            [10, 5], method="LSODA", t_eval=np.arange(16.0), rtol=1e-6, atol=1e-6)
    np.testing.assert_allclose(pp[["x", "y"]].to_numpy(), s.y.T, rtol=1e-12)


def test_find_path_over_time_exactly_is_sympy_dsolve(needs_sympy):
    path = sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 5], known={"r": 0.3},
                                     exactly=True)
    assert path.find_value_at(t=5) == pytest.approx(10 * math.exp(1.5), rel=1e-14)
    with pytest.raises(sdata.SimplydataError, match="only as an equation"):
        sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50],
                                  known={"r": 0.3, "K": 1000}, exactly=True)


@pytest.mark.parametrize("kwargs, problem", [
    (dict(equations="N = r", at_start={"N": 1}, between=[0, 1]), "how fast"),
    (dict(equations="dN/dt = r * N", at_start={"N": 1}, between=[0, 1]), "known="),
    (dict(equations="dN/dt = -N", at_start={"M": 1}, between=[0, 1]), "at_start="),
    (dict(equations="dN/dt = -N", at_start={"N": 1}), "between="),
    (dict(equations="dN/dt = -N", at_start={"N": 1}, between=[0, 1], test_method="euler"), "test_method"),
])
def test_find_path_over_time_explains_wrong_input(kwargs, problem):
    with pytest.raises(sdata.SimplydataError, match=problem):
        sdata.find_path_over_time(**kwargs)


def test_turn_into_running_area_is_cumulative_trapezoid_and_simpson():
    values = [2.0, 4, 4, 3, 1, 0, 2]
    nums = sdata.numbers(values)
    nums.turn_into_running_area(time_step=60)
    np.testing.assert_array_equal(nums.as_numpy(), integrate.cumulative_trapezoid(values, dx=60, initial=0))
    nums.undo()
    np.testing.assert_array_equal(nums.as_numpy(), values)
    nums.turn_into_running_area(time_step=60, test_method="simpson")
    np.testing.assert_array_equal(nums.as_numpy(), integrate.cumulative_simpson(values, dx=60, initial=0))
    # a closed form: the running area of a straight line 0, 1, 2 ... with step 1 is t^2 / 2
    line = sdata.numbers(list(range(11)))
    line.turn_into_running_area()
    np.testing.assert_allclose(line.as_numpy(), np.arange(11.0) ** 2 / 2, rtol=0, atol=1e-12)
    with pytest.raises(sdata.SimplydataError, match="fill the empty"):
        sdata.numbers([1, None, 3]).turn_into_running_area()
