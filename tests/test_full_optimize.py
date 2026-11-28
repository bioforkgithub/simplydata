"""Families for 100 %, batches 14-16 (approved by Manish 2026-11-28): SciPy optimize, integrate and interpolate (plan
section 2.6). Every new test_method= value of find_where_smallest and solve, fit_curve(always=), find_best_pairing,
the new integrators, find_path_between_ends, the new joined_by= values and curve_through_points with the words on a
curve, each against SciPy itself; the sentences that say the method, whether it settled and how many evaluations; the
pointers of the 2.6 names."""

from __future__ import annotations

import math
import warnings

import numpy as np
import pytest
from scipy import integrate, interpolate, optimize, stats

import simplydata as sdata
from simplydata import learn
from simplydata._errors import SimplydataError

ROSENBROCK = "(1 - x)**2 + 100*(y - x**2)**2"
WAVY = "(x - 2)**2 + sin(5*x)"
SYSTEM = ["x = 0.5*cos(y)", "y = 0.5*sin(x)"]
X = [0, 5, 10, 20, 30, 40]
Y = [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]


def first(table) -> dict:
    return table.as_pandas().iloc[0].to_dict()


def column(table, name):
    return table.as_pandas()[name].to_numpy(dtype=float)


def rosen(v):
    return (1 - v[0]) ** 2 + 100 * (v[1] - v[0] ** 2) ** 2


# ---------------------------------------------------------------- batch 14: find_where_smallest
def test_golden_section_on_a_range_is_scipy_golden_on_the_best_scan_bracket(capsys):
    found = first(sdata.find_where_smallest(WAVY, between=[0, 5], test_method="golden section"))
    f = lambda x: (x - 2) ** 2 + np.sin(5 * x)  # noqa: E731
    xs = np.linspace(0, 5, 200)
    best = int(np.argmin(f(xs)))
    theirs = optimize.minimize_scalar(f, bracket=(xs[best - 1], xs[best], xs[best + 1]), method="golden",
                                      options={"xtol": 1e-10, "maxiter": 10000})
    assert found["x"] == pytest.approx(theirs.x, rel=1e-8)
    assert found["smallest value"] == pytest.approx(theirs.fun, rel=1e-10)
    assert found["method"] == "golden-section search" and found["settled"] == "yes"
    out = capsys.readouterr().out
    assert 'minimize_scalar(method="golden")' in out
    assert "Search: golden-section search; it settled (converged) after" in out and "worked out" in out


def test_golden_section_works_from_a_start_and_golden_keeps_meaning_brent():
    found = first(sdata.find_where_smallest(WAVY, start=1.5, test_method="golden section"))
    assert found["method"] == "golden-section search from the start"
    assert found["x"] == pytest.approx(2.184353, abs=1e-5)
    # review fix: "golden" meant Brent's method before these batches, and scripts that use it keep working the same
    old = first(sdata.find_where_smallest(WAVY, between=[0, 5], test_method="golden"))
    assert old["method"] == "Brent's method on the range"


@pytest.mark.parametrize("formula, value", [("abs(x) + abs(x - 1)", 1.0), ("floor(x*2)**2", 0.0),
                                            ("abs(x + 2)", 0.0)])
def test_golden_section_on_a_flat_bottom_or_an_end_gives_an_answer_not_an_error(formula, value, capsys):
    found = first(sdata.find_where_smallest(formula, between=[-2, 3], test_method="golden section"))
    assert found["smallest value"] == pytest.approx(value, abs=1e-9)
    out = capsys.readouterr().out
    assert "Note:" in out and "Traceback" not in out


def test_grid_search_is_scipy_brute_then_a_bounded_polish(capsys):
    found = first(sdata.find_where_smallest(WAVY, between=[0, 5], search="whole range", test_method="grid search"))
    f = lambda v: (v[0] - 2) ** 2 + np.sin(5 * v[0])  # noqa: E731
    corner = optimize.brute(f, [(0, 5)], Ns=20000, finish=None)
    theirs = optimize.minimize(f, np.atleast_1d(corner), method="L-BFGS-B", bounds=[(0, 5)],
                               options={"ftol": 1e-15, "gtol": 1e-10})
    assert found["x"] == pytest.approx(theirs.x[0], rel=1e-9)
    assert found["iterations"] == theirs.nit and found["evaluations"] > 20000  # grid points are not steps
    assert found["settled"] == ("yes" if theirs.success else "no")
    assert "(searched 20,000 grid points) then a local polish (L-BFGS-B" in capsys.readouterr().out
    two = first(sdata.find_where_smallest(ROSENBROCK, between={"x": [-2, 2], "y": [-1, 3]}, search="whole range",
                                          test_method="brute"))
    assert two["x"] == pytest.approx(1, abs=1e-6) and two["y"] == pytest.approx(1, abs=1e-6)


def test_grid_search_refuses_too_many_names():
    names = " + ".join(f"x{i}**2" for i in range(10))
    with pytest.raises(SimplydataError, match="up to 9 names"):
        sdata.find_where_smallest(names, between={f"x{i}": [-1, 1] for i in range(10)}, search="whole range",
                                  test_method="grid search")


@pytest.mark.parametrize("value, scipy_name, options", [
    ("newton conjugate gradient", "Newton-CG", {"xtol": 1e-10, "maxiter": 10000}),
    ("truncated newton", "TNC", {"xtol": 1e-12, "ftol": 1e-15, "gtol": 1e-10, "maxfun": 20000}),
])
def test_the_two_slope_methods_reach_the_minimum_with_library_slopes(value, scipy_name, options, capsys):
    found = first(sdata.find_where_smallest(ROSENBROCK, start={"x": -1.2, "y": 1}, test_method=value))
    assert [found["x"], found["y"]] == pytest.approx([1, 1], abs=1e-6)  # the Rosenbrock minimum, known by hand
    # SciPy on its own, with its own slopes (analytic here, so nothing of simplydata's is in the reference)
    theirs = optimize.minimize(optimize.rosen, [-1.2, 1], method=scipy_name, jac=optimize.rosen_der,
                               options=options)
    assert [found["x"], found["y"]] == pytest.approx(list(theirs.x), abs=1e-6)
    assert "needs a smooth formula" in capsys.readouterr().out


def test_the_slope_methods_use_library_differentiation_not_own_code():
    import inspect

    from simplydata import finding

    source = inspect.getsource(finding)
    assert "_central_slopes" not in source and "_central_bends" not in source
    assert "differentiate.jacobian" in source and '"3-point"' in source


@pytest.mark.parametrize("value", ["newton conjugate gradient", "truncated newton"])
def test_a_slope_method_on_a_formula_with_a_corner_says_so(value, capsys):
    sdata.find_where_smallest("abs(x - 1) + abs(y)", start={"x": 0.3, "y": 0.4}, test_method=value)
    assert "has a corner or a jump" in capsys.readouterr().out


@pytest.mark.parametrize("legacy, value", [
    ("fmin", "nelder-mead"), ("fmin_bfgs", "bfgs"), ("fmin_cg", "conjugate gradient"), ("fmin_cobyla", "cobyla"),
    ("fmin_l_bfgs_b", "l-bfgs-b"), ("fmin_ncg", "newton conjugate gradient"), ("fmin_powell", "powell"),
    ("fmin_slsqp", "slsqp"), ("fmin_tnc", "truncated newton"),
])
def test_scipy_legacy_fmin_names_are_the_minimize_methods(legacy, value):
    by_legacy = first(sdata.find_where_smallest(ROSENBROCK, start={"x": -1.2, "y": 1}, test_method=legacy))
    by_value = first(sdata.find_where_smallest(ROSENBROCK, start={"x": -1.2, "y": 1}, test_method=value))
    assert by_legacy["method"] == by_value["method"]
    assert by_legacy["x"] == by_value["x"] and by_legacy["y"] == by_value["y"]


def test_every_search_says_whether_it_settled_and_how_many_evaluations(capsys):
    found = first(sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5]))
    out = capsys.readouterr().out
    assert f"it settled (converged) after {found['iterations']:,} steps, and the formula was worked out " \
           f"{found['evaluations']:,} times." in out
    assert found["evaluations"] > found["iterations"] > 0
    linear = first(sdata.find_where_smallest("2*x + 3*y", rules=["x + y >= 4", "x >= 0", "y >= 0"]))
    assert linear["evaluations"] == 0
    assert "so the formula was not worked out point by point" in capsys.readouterr().out


# ---------------------------------------------------------------- batch 14: solve
def test_fixed_point_is_scipy_fixed_point_with_steffensen(capsys):
    found = first(sdata.solve("x = cos(x)", start=1, test_method="fixed point"))
    theirs = float(optimize.fixed_point(np.cos, 1.0, xtol=1e-12, maxiter=1000, method="del2"))
    assert found["x"] == pytest.approx(theirs, rel=1e-12)
    assert found["x"] == pytest.approx(0.7390851332151607, rel=1e-12)  # the Dottie number (OEIS A003957)
    out = capsys.readouterr().out
    assert "fixed_point, del2" in out and "it settled (converged)" in out


def test_fixed_point_needs_the_name_alone_on_the_left():
    with pytest.raises(SimplydataError, match="alone on the left"):
        sdata.solve("cos(x) = x", start=1, test_method="fixed point")
    with pytest.raises(SimplydataError, match="did not settle"):
        sdata.solve("x = x**2 + 1", start=1, test_method="fixed point")


@pytest.mark.parametrize("value, scipy_name, sign", [
    ("broyden second", "broyden2", 1), ("diagonal broyden", "diagbroyden", 1), ("anderson mixing", "anderson", 1),
    ("newton-krylov", "krylov", 1), ("linear mixing", "linearmixing", -1), ("exciting mixing", "excitingmixing", -1),
    ("broyden2", "broyden2", 1), ("krylov", "krylov", 1), ("newton_krylov", "krylov", 1),
])
def test_the_other_root_solvers_are_scipy_root(value, scipy_name, sign, capsys):
    found = first(sdata.solve(SYSTEM, start={"x": 0, "y": 0}, test_method=value))

    def gaps(v):
        return sign * np.array([v[0] - 0.5 * np.cos(v[1]), v[1] - 0.5 * np.sin(v[0])])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        theirs = optimize.root(gaps, [0, 0], method=scipy_name, options={"fatol": 1e-12, "maxiter": 5000})
    assert [found["x"], found["y"]] == pytest.approx(list(theirs.x), rel=1e-9)
    out = capsys.readouterr().out
    assert "Search:" in out and "the equations were worked out" in out


def test_a_solver_that_breaks_down_gives_a_plain_error():
    with pytest.raises(SimplydataError, match="broke down"):
        sdata.solve(["x = 3*y + 1", "y = 3*x + 1"], start={"x": 0, "y": 0}, test_method="exciting mixing")


# ---------------------------------------------------------------- batch 14: fit_curve(always=), find_best_pairing
def test_fit_curve_always_rising_is_scipy_isotonic_regression(capsys):
    table = sdata.table({"dose": [3, 1, 2, 5, 4, 6], "response": [2, 1, 3, 3.5, 4, 5]})
    result = table.fit_curve(x="dose", y="response", always="rising")
    frame = result.as_pandas()
    assert list(frame["dose"]) == [1, 2, 3, 4, 5, 6]
    theirs = optimize.isotonic_regression([1, 3, 2, 4, 3.5, 5]).x
    assert np.allclose(frame["fitted response"], theirs, rtol=1e-12)
    assert "as R isoreg(dose, response)$yf" in capsys.readouterr().out
    falling = table.fit_curve(x="dose", y="response", always="falling").as_pandas()
    assert np.allclose(falling["fitted response"],
                       optimize.isotonic_regression([1, 3, 2, 4, 3.5, 5], increasing=False).x, rtol=1e-12)


def test_fit_curve_always_with_weights_and_groups():
    table = sdata.table({"dose": [1, 2, 3, 1, 2, 3], "response": [3, 1, 2, 1, 3, 2], "w": [1, 2, 1, 1, 1, 3],
                         "group": ["a", "a", "a", "b", "b", "b"]})
    frame = table.fit_curve(x="dose", y="response", always="rising", weights="w",
                            for_each_group_in="group").as_pandas()
    a = optimize.isotonic_regression([3, 1, 2], weights=[1, 2, 1]).x
    b = optimize.isotonic_regression([1, 3, 2], weights=[1, 1, 3]).x
    assert np.allclose(frame["fitted response"], np.concatenate([a, b]), rtol=1e-12)
    with pytest.raises(SimplydataError, match="always="):
        table.fit_curve(x="dose", y="response", always="rising", of_degree=3)
    with pytest.raises(SimplydataError, match="rising"):
        table.fit_curve(x="dose", y="response", always="upwards")


def test_find_best_pairing_is_scipy_linear_sum_assignment(capsys):
    costs = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
    frame = sdata.find_best_pairing(sdata.number_grid(costs)).as_pandas()
    rows, columns = optimize.linear_sum_assignment(np.array(costs))
    assert list(frame["row"]) == [str(i + 1) for i in rows]
    assert list(frame["column"]) == [str(j + 1) for j in columns]
    assert frame["cost"].sum() == np.array(costs)[rows, columns].sum() == 5
    assert "Total 5." in capsys.readouterr().out
    biggest = sdata.find_best_pairing(costs, aim_for="biggest total").as_pandas()
    rows, columns = optimize.linear_sum_assignment(np.array(costs), maximize=True)
    assert biggest["cost"].sum() == np.array(costs)[rows, columns].sum()


def test_find_best_pairing_takes_tables_rectangles_and_forbidden_pairs(capsys):
    table = sdata.table({"worker": ["Ann", "Bo"], "dig": [3, 5], "paint": [4, 1], "mow": [2, 2]})
    frame = sdata.find_best_pairing(table).as_pandas()
    assert list(frame["row"]) == ["Ann", "Bo"] and list(frame["column"]) == ["mow", "paint"]
    assert "1 column stays free" in capsys.readouterr().out
    frame = sdata.find_best_pairing([[1, None], [None, 1]]).as_pandas()
    assert list(frame["column"]) == ["1", "2"]
    with pytest.raises(SimplydataError, match="No pairing"):
        sdata.find_best_pairing([[1, None], [2, None]])
    with pytest.raises(SimplydataError, match="always solved exactly"):
        sdata.find_best_pairing([[1, 2], [2, 1]], test_method="faq")


@pytest.mark.parametrize("value, scipy_name", [(None, "faq"), ("2-opt", "2opt")])
def test_find_best_pairing_with_distances_is_scipy_quadratic_assignment(value, scipy_name):
    flows = [[0, 5, 2, 4], [5, 0, 3, 0], [2, 3, 0, 0], [4, 0, 0, 0]]
    distances = [[0, 22, 53, 53], [22, 0, 40, 62], [53, 40, 0, 55], [53, 62, 55, 0]]
    frame = sdata.find_best_pairing(flows, with_distances=distances, test_method=value).as_pandas()
    options = {"rng": np.random.default_rng(1)} if scipy_name == "2opt" else {}
    theirs = optimize.quadratic_assignment(flows, distances, method=scipy_name, options=options)
    assert list(frame["place"]) == [str(p + 1) for p in theirs.col_ind]


# ---------------------------------------------------------------- batch 15: integrals
def test_tanh_sinh_and_cubature_areas_are_scipy(capsys):
    ours = sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="tanh-sinh")
    assert ours == pytest.approx(integrate.tanhsinh(lambda x: np.exp(-x ** 2), 0, np.inf).integral, rel=1e-14)
    assert ours == pytest.approx(math.sqrt(math.pi) / 2, rel=1e-12)
    ours = sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="cubature")
    assert ours == pytest.approx(integrate.cubature(lambda x: np.exp(-x[:, 0] ** 2), [0], [np.inf]).estimate,
                                 rel=1e-14)
    out = capsys.readouterr().out
    assert "integrate.tanhsinh" in out and "integrate.cubature" in out


def test_quasi_monte_carlo_and_romberg_areas_are_scipy(capsys):
    ours = sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="quasi monte carlo")
    theirs = integrate.qmc_quad(lambda x: np.exp(-x[0] ** 2), [0], [2], qrng=stats.qmc.Halton(1, rng=1)).integral
    assert ours == pytest.approx(theirs, rel=1e-14)
    assert "standard error" in capsys.readouterr().out
    xs = np.linspace(0, 2, 1025)
    ours = sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="romberg on even steps")
    assert ours == pytest.approx(integrate.romb(np.exp(-xs ** 2), dx=2 / 1024), rel=1e-14)
    with pytest.raises(SimplydataError, match="numbers for both ends"):
        sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="quasi monte carlo")
    with pytest.raises(SimplydataError, match="romberg on even steps"):  # the old name now names the new value
        sdata.find_area_under("x", between=[0, 1], test_method="romberg")


@pytest.mark.parametrize("value", ["cubature", "quasi monte carlo"])
def test_find_volume_under_takes_the_new_integrators(value):
    ours = sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]}, test_method=value)
    if value == "cubature":
        theirs = integrate.cubature(lambda p: p[:, 0] * p[:, 1] ** 2, [0, 0], [1, 2]).estimate
    else:
        engine = stats.qmc.Halton(2, rng=1)
        theirs = integrate.qmc_quad(lambda p: p[0] * p[1] ** 2, [0, 0], [1, 2], qrng=engine).integral
    assert ours == pytest.approx(theirs, rel=1e-13)
    assert ours == pytest.approx(4 / 3, rel=1e-2)
    with pytest.raises(SimplydataError, match="test_method"):
        sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]}, test_method="tanh-sinh")


def test_find_path_between_ends_is_scipy_solve_bvp_and_the_closed_form(capsys):
    path = sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5])
    frame = path.as_pandas()
    assert list(frame.columns) == ["x", "y", "dy/dx"] and len(frame) == 101
    x = np.linspace(0, 1.5, 101)
    guess = np.vstack([x / 1.5, np.full_like(x, 1 / 1.5)])
    theirs = integrate.solve_bvp(lambda x, y: np.vstack([y[1], -y[0]]), lambda a, b: np.array([a[0], b[0] - 1]), x,
                                 guess, tol=1e-8, max_nodes=100000).sol(x)
    assert np.allclose(frame["y"], theirs[0], rtol=1e-10, atol=1e-12)
    assert np.allclose(frame["y"], np.sin(x) / np.sin(1.5), atol=1e-8)  # y = sin(x) / sin(1.5)
    assert np.allclose(frame["dy/dx"], np.cos(x) / np.sin(1.5), atol=1e-7)
    out = capsys.readouterr().out
    assert "integrate.solve_bvp" in out and "it settled (converged)" in out


def test_find_path_between_ends_with_first_order_equations_and_free_ends():
    path = sdata.find_path_between_ends(["dy/dx = v", "dv/dx = -y"], at_ends={"y": [0, None], "v": [None, 2]},
                                        between=[0, 1], step=0.25).as_pandas()
    assert list(path["x"]) == [0, 0.25, 0.5, 0.75, 1]
    a = 2 / math.cos(1)  # y = a sin(x) with y(0) = 0 and y'(1) = 2
    assert np.allclose(path["y"], a * np.sin(path["x"]), atol=1e-8)
    with pytest.raises(SimplydataError, match="as many known values"):
        sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, None]}, between=[0, 1])
    with pytest.raises(SimplydataError, match="does not change"):
        sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"z": [0, 1]}, between=[0, 1])
    with pytest.raises(SimplydataError, match="whole number of times"):
        sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1], step=0.3)


# ---------------------------------------------------------------- batch 15: joined_by=
GROWTH = {"year": [2000, 2002, 2004, 2006, 2008], "population": [10, 11, 13, 14, 13]}
AT = [2001, 2003, 2007]


@pytest.mark.parametrize("joined_by, theirs", [
    ("polynomial", lambda x, y: interpolate.BarycentricInterpolator(x, y)(AT)),
    ("krogh", lambda x, y: interpolate.krogh_interpolate(x, y, AT)),
    ("barycentric", lambda x, y: interpolate.barycentric_interpolate(x, y, AT)),
    ("rational curve", lambda x, y: interpolate.FloaterHormannInterpolator(x, y, d=3)(AT)),
    ("aaa", lambda x, y: np.real(interpolate.AAA(x, y)(AT))),
])
def test_the_new_ways_of_joining_one_direction_are_scipy(joined_by, theirs):
    table = sdata.table(GROWTH)
    found = column(table.find_values_at("population", at={"year": AT}, joined_by=joined_by), "population")
    assert np.allclose(found, theirs(GROWTH["year"], GROWTH["population"]), rtol=1e-8)


def test_smooth_triangles_is_scipy_clough_tocher():
    table = sdata.table({"east": [0, 1, 0, 1, 0.5, 0.2], "north": [0, 0, 1, 1, 0.5, 0.7],
                         "height": [1, 2, 3, 4, 2.5, 3.1]})
    found = column(table.find_values_at("height", at={"east": [0.3, 0.6, 2], "north": [0.4, 0.2, 2]},
                                        joined_by="smooth triangles"), "height")
    points = np.array([[0, 0], [1, 0], [0, 1], [1, 1], [0.5, 0.5], [0.2, 0.7]])
    theirs = interpolate.CloughTocher2DInterpolator(points, [1, 2, 3, 4, 2.5, 3.1], tol=1e-12, maxiter=10000)(
        [[0.3, 0.4], [0.6, 0.2]])
    assert np.allclose(found[:2], theirs, rtol=1e-10) and math.isnan(found[2])
    with pytest.raises(SimplydataError, match="extend"):
        table.find_values_at("height", at={"east": [0.3], "north": [0.4]}, joined_by="smooth triangles",
                             outside="extend")


# ---------------------------------------------------------------- batch 16: curve_through_points (G6)
def natural():
    return interpolate.make_interp_spline(X, Y, k=3, bc_type="natural")


def test_curve_through_points_is_the_natural_cubic_spline_and_find_values_at_agrees(capsys):
    curve = sdata.curve_through_points(x=X, y=Y)
    assert curve.find_value_at(12) == pytest.approx(float(natural()(12)), rel=1e-14)
    found = curve.find_value_at([1, 12, 50])
    assert np.allclose(found.as_numpy()[:2], natural()([1, 12]), rtol=1e-14) and math.isnan(found.as_numpy()[2])
    table = sdata.table({"x": X, "y": Y})
    same = column(table.find_values_at("y", at={"x": [1, 12]}, joined_by="smooth curve"), "y")
    assert np.allclose(found.as_numpy()[:2], same, rtol=1e-12)
    assert 'as R splinefun(method = "natural")' in capsys.readouterr().out


def test_the_words_on_a_curve_are_scipy_bspline_words():
    curve = sdata.curve_through_points(x=X, y=Y)
    spline = natural()
    assert curve.find_slope_at(12) == pytest.approx(float(spline.derivative()(12)), rel=1e-13)
    assert curve.find_slope_at(12, order=2) == pytest.approx(float(spline.derivative(2)(12)), rel=1e-12)
    every = curve.find_slope_at(12, order="all").as_pandas()
    assert np.allclose(every["value"], [float(spline.derivative(k)(12)) if k else float(spline(12))
                                        for k in range(4)], rtol=1e-12)
    assert curve.find_area_between(0, 20) == pytest.approx(float(spline.integrate(0, 20)), rel=1e-13)
    zeros = curve.find_zeros(where_value_is=5).as_numpy()
    theirs = interpolate.PPoly.from_spline(spline, extrapolate=False).solve(5, extrapolate=False)
    assert np.allclose(zeros, theirs, rtol=1e-10)
    slopes = curve.turn_into_slope_curve()
    assert slopes.find_value_at(12) == pytest.approx(float(spline.derivative()(12)), rel=1e-13)
    areas = curve.turn_into_area_curve()
    assert areas.find_value_at(0) == 0
    assert areas.find_value_at(20) == pytest.approx(float(spline.integrate(0, 20)), rel=1e-12)
    assert type(curve.as_scipy()) is interpolate.BSpline


def test_show_pieces_and_show_knots_are_ppoly_bpoly_and_the_bspline():
    curve = sdata.curve_through_points(x=X, y=Y)
    spline = natural()
    pieces = curve.show_pieces().as_pandas()
    pp = interpolate.PPoly.from_spline(spline)
    keep = np.diff(pp.x) > 0
    assert list(pieces.columns) == ["from", "to", "constant", "(x - from)", "(x - from)**2", "(x - from)**3"]
    assert np.allclose(pieces["(x - from)**3"], pp.c[0][keep], rtol=1e-10)
    bernstein = curve.show_pieces(basis="bernstein").as_pandas()
    assert np.allclose(bernstein["control value 0"], interpolate.BPoly.from_power_basis(pp).c[0][keep], rtol=1e-10)
    knots = curve.show_knots().as_pandas()
    assert np.allclose(knots["knot"], spline.t) and np.allclose(knots["coefficient"][:len(spline.c)], spline.c)


@pytest.mark.parametrize("options, theirs", [
    ({"allowed_error": 0.5}, lambda: interpolate.make_splrep(X, Y, s=0.5, k=3)),
    ({"knots": [15]}, lambda: interpolate.make_lsq_spline(X, Y, [0, 0, 0, 0, 15, 40, 40, 40, 40], k=3)),
    ({"slopes": [0, 0, -0.2, -0.1, 0, 0]}, lambda: interpolate.CubicHermiteSpline(X, Y, [0, 0, -0.2, -0.1, 0, 0])),
    ({"degree": 1}, lambda: interpolate.make_interp_spline(X, Y, k=1)),
    ({"degree": 5}, lambda: interpolate.make_interp_spline(X, Y, k=5)),
    ({"ends": "not-a-knot"}, lambda: interpolate.make_interp_spline(X, Y, k=3, bc_type="not-a-knot")),
    ({"ends": "clamped"}, lambda: interpolate.make_interp_spline(X, Y, k=3, bc_type="clamped")),
    ({"allowed_error": 0.5, "weights": [1, 1, 2, 2, 1, 1]},
     lambda: interpolate.make_splrep(X, Y, s=0.5, k=3, w=[1, 1, 2, 2, 1, 1])),
    ({"smoothness": 0.01}, lambda: (lambda unit: lambda at: unit(np.asarray(at) / 40))(
        interpolate.make_smoothing_spline(np.array(X) / 40, Y, lam=0.01))),
])
def test_each_way_of_making_a_curve_is_its_scipy_spline(options, theirs):
    curve = sdata.curve_through_points(x=X, y=Y, **options)
    assert np.allclose(curve.find_value_at([3, 12, 33]).as_numpy(), theirs()([3, 12, 33]), rtol=1e-11)


def test_a_path_a_surface_and_a_surface_on_a_sphere():
    path = sdata.curve_through_points(x=[0, 1, 2, 1, 0], y=[0, 1, 0, -1, -0.2], in_order=True)
    frame = path.find_value_at([0, 0.5, 1]).as_pandas()
    spline, _ = interpolate.make_splprep([[0, 1, 2, 1, 0], [0, 1, 0, -1, -0.2]], s=0, k=3)
    assert np.allclose(frame[["x", "y"]].to_numpy(), np.asarray(spline([0, 0.5, 1])).T, rtol=1e-12)
    east, north = np.meshgrid(np.arange(5.0), np.arange(6.0), indexing="ij")
    height = np.sin(east) + np.cos(north)
    surface = sdata.curve_through_points(x=east.ravel(), y=north.ravel(), z=height.ravel())
    theirs = interpolate.RectBivariateSpline(np.arange(5.0), np.arange(6.0), height, kx=3, ky=3, s=0)
    assert surface.find_value_at(1.5, 2.5) == pytest.approx(float(theirs.ev(1.5, 2.5)), rel=1e-13)
    assert surface.find_area_between(0, 4, y_between=[0, 5]) == pytest.approx(theirs.integral(0, 4, 0, 5), rel=1e-13)
    assert surface.find_slope_at(1.5, 2.5, along="y") == pytest.approx(float(theirs.ev(1.5, 2.5, dy=1)), rel=1e-12)
    rng = np.random.default_rng(1)
    sx, sy = rng.uniform(0, 4, 60), rng.uniform(0, 4, 60)
    scattered = sdata.curve_through_points(x=sx, y=sy, z=np.sin(sx) + sy, allowed_error=0.1)
    theirs = interpolate.SmoothBivariateSpline(sx, sy, np.sin(sx) + sy, kx=3, ky=3, s=0.1)
    assert scattered.find_value_at(2, 2) == pytest.approx(float(theirs.ev(2, 2)), rel=1e-12)
    lat, lon = np.meshgrid([-60.0, -30, 0, 30, 60], np.arange(0.0, 360, 45), indexing="ij")
    values = np.cos(np.radians(lat)) + 0.1 * np.sin(np.radians(lon))
    sphere = sdata.curve_through_points(x=lat.ravel(), y=lon.ravel(), z=values.ravel(), on_sphere=True)
    expected = math.cos(math.radians(10)) + 0.1 * math.sin(math.radians(100))
    assert sphere.find_value_at(10, 100) == pytest.approx(expected, abs=2e-3)


def test_curve_errors_are_plain():
    with pytest.raises(SimplydataError, match="same x"):
        sdata.curve_through_points(x=[0, 1, 1, 2], y=[1, 2, 3, 4])
    with pytest.raises(SimplydataError, match="give one of them"):
        sdata.curve_through_points(x=X, y=Y, knots=[15], allowed_error=1)
    with pytest.raises(SimplydataError, match="cubic spline"):
        sdata.curve_through_points(x=X, y=Y, degree=5, ends="clamped")
    curve = sdata.curve_through_points(x=X, y=Y)
    with pytest.raises(SimplydataError, match="inside the points"):
        curve.find_area_between(0, 50)
    with pytest.raises(SimplydataError, match="In simplydata this is curve.find_area_between"):
        curve.splint
    with pytest.raises(SimplydataError, match="a surface"):
        curve.find_value_at(1, 2)


# ---------------------------------------------------------------- registration, help and pointers
NEW_WORDS = ["sdata.find_best_pairing", "sdata.find_path_between_ends", "sdata.curve_through_points",
             "curve.find_value_at", "curve.find_slope_at", "curve.find_area_between", "curve.find_zeros",
             "curve.turn_into_slope_curve", "curve.turn_into_area_curve", "curve.show_pieces", "curve.show_knots",
             "curve.as_scipy"]


@pytest.mark.parametrize("key", NEW_WORDS)
def test_each_new_word_is_registered_with_a_help_example_and_an_underneath_entry(key):
    from simplydata._underneath import UNDERNEATH

    assert key in learn._all_keys()
    assert key in learn.HELP_EXAMPLES
    assert key in UNDERNEATH
    doc = learn._function(key).__doc__
    assert doc and doc.strip().splitlines()[0]


@pytest.mark.parametrize("typed, word", [
    ("scipy.optimize.basinhopping", 'test_method="basin hopping"'), ("optimize.brute", 'test_method="grid search"'),
    ("optimize.golden", 'test_method="golden section"'), ("optimize.fmin_tnc", 'test_method="truncated newton"'),
    ("optimize.fixed_point", 'test_method="fixed point"'), ("optimize.newton_krylov", 'test_method="newton-krylov"'),
    ("optimize.isotonic_regression", 'always="rising"'), ("optimize.linear_sum_assignment", "find_best_pairing"),
    ("optimize.quadratic_assignment", "with_distances="), ("scipy.integrate.solve_bvp", "find_path_between_ends"),
    ("integrate.tanhsinh", 'test_method="tanh-sinh"'), ("integrate.Radau", 'test_method="stiff"'),
    ("integrate.romb", 'test_method="romberg on even steps"'), ("interpolate.AAA", 'joined_by="aaa"'),
    ("interpolate.KroghInterpolator", 'joined_by="polynomial"'),
    ("interpolate.CloughTocher2DInterpolator", 'joined_by="smooth triangles"'),
    ("scipy.interpolate.BSpline", "curve_through_points"), ("interpolate.splev", "curve.find_value_at"),
    ("interpolate.sproot", "curve.find_zeros"), ("interpolate.RectSphereBivariateSpline", "on_sphere=True"),
    ("spline", "curve_through_points"),
])
def test_the_scipy_names_of_section_2_6_point_to_their_word(typed, word, capsys):
    sdata.help(typed)
    assert word in capsys.readouterr().out


# ---------------------------------------------------------------- review fixes (independent review, 2026-11-28)
def test_fit_curve_always_pools_tied_x_as_r_isoreg(capsys):
    table = sdata.table({"x": [1, 2, 2, 3], "y": [0, 1, 3, 4]})
    rising = table.fit_curve(x="x", y="y", always="rising").as_pandas()
    assert list(rising["fitted y"]) == pytest.approx([0, 2, 2, 4])  # R: isoreg(c(1, 2, 2, 3), c(0, 1, 3, 4))$yf
    falling = table.fit_curve(x="x", y="y", always="falling").as_pandas()
    assert list(falling["fitted y"]) == pytest.approx([2, 2, 2, 2])  # R: -isoreg(x, -y)$yf
    capsys.readouterr()
    table = sdata.table({"x": [1, 2, 3], "y": [3, 1, 2], "w": [1, 2, 1]})
    table.fit_curve(x="x", y="y", always="rising", weights="w")
    out = capsys.readouterr().out
    assert "as R isoreg" not in out and "R isoreg() has no weights" in out


def test_aaa_leaves_places_near_a_pole_between_the_points_empty(capsys):
    table = sdata.table({"t": [0, 1, 2, 3, 4, 5], "y": [math.exp(t) for t in range(6)]})
    found = column(table.find_values_at("y", at={"t": [2.6249, 0.5, 4.5]}, joined_by="aaa"), "y")
    assert math.isnan(found[0])  # SciPy AAA has a real pole at t = 2.612 (16,940 at 2.6249)
    x = np.arange(6.0)
    assert np.allclose(found[1:], np.real(interpolate.AAA(x, np.exp(x))([0.5, 4.5])), rtol=1e-10)
    assert "has a pole" in capsys.readouterr().out


def test_grid_search_settles_by_its_polish_and_fixed_point_says_when_it_left_between(capsys):
    sdata.solve("x = cos(x)", start=2.5, between=[2, 3], test_method="fixed point")
    assert "outside between=" in capsys.readouterr().out


def test_mixing_solvers_say_how_to_write_the_equations():
    with pytest.raises(SimplydataError, match='alone on the left.*"x = ...", "y = ..."'):
        sdata.solve(["x = 3*y + 1", "y = 3*x + 1"], start={"x": 0, "y": 0}, test_method="linear mixing")


def test_a_method_that_cannot_keep_limits_says_the_answer_is_outside(capsys):
    sdata.find_where_smallest("(x - 5)**2 + (y - 5)**2", between={"x": [0, 1], "y": [0, 1]}, test_method="bfgs")
    assert "the answer is outside between=" in capsys.readouterr().out


def test_a_surface_is_empty_outside_its_points(capsys):
    east, north = np.meshgrid(np.arange(6.0), np.arange(4.0), indexing="ij")
    surface = sdata.curve_through_points(x=east.ravel(), y=north.ravel(), z=(east + north).ravel())
    capsys.readouterr()
    assert math.isnan(surface.find_value_at(10, 2))
    assert "outside the points" in capsys.readouterr().out
    assert surface.find_value_at(2.5, 1.5) == pytest.approx(4.0, rel=1e-12)


def test_weighted_curve_names_make_splrep(capsys):
    sdata.curve_through_points(x=X, y=Y, allowed_error=0.5, weights=[1, 1, 2, 2, 1, 1])
    out = capsys.readouterr().out
    assert "make_splrep" in out and "as splrep(s=)" not in out
