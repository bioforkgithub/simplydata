"""Families for 100 %, batches 24-26 (plan section 2.10, approved by Manish 2026-11-28, G13 and G15): calculus checks,
series, transforms and code on a formula; check_solution, products, ways and the new kinds of sdata.solve(exactly=
True); number theory on numbers; exact grids, the permanent and orthogonal columns.

Every answer is compared with SymPy doing the same directly, and with the answer worked out by hand or a published
value where there is one. Every SymPy call of the new words goes through simplydata's one time limit (checked by
watching run_with_time_limit).
"""

from __future__ import annotations

import contextlib
import io
import math

import pytest

import simplydata as sdata
from simplydata import _formula_calculus, _time_limit
from simplydata.numbers import number_theory_words

pytestmark = pytest.mark.usefixtures("needs_sympy")


def _sp():
    import sympy as sp

    return sp


def _quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return call(*args, **kwargs)


def _formula(text):
    return _quiet(sdata.formula, text)


def _column(table, name) -> list:
    found = _quiet(table.get_column, name)
    return found.as_numpy().tolist() if hasattr(found, "as_numpy") else list(found)


@pytest.fixture
def sympy_calls(monkeypatch):
    calls = []
    real = _time_limit.run_with_time_limit

    def watched(call, *values, **named):
        calls.append(getattr(call, "__name__", str(call)))
        return real(call, *values, **named)

    monkeypatch.setattr(_time_limit, "run_with_time_limit", watched)
    return calls


# ------------------------------------------------------------------------------------------------ transforms
@pytest.mark.parametrize("name, text, letters", [
    ("laplace", "exp(-2*t)", ("t", "s")), ("inverse laplace", "1/(s + 2)", ("s", "t")),
    ("fourier", "exp(-x**2)", ("x", "k")), ("mellin", "exp(-x)", ("x", "s")),
    ("sine", "exp(-x)", ("x", "k")), ("cosine", "exp(-x)", ("x", "k")),
    ("inverse sine", "exp(-k)", ("k", "x")), ("inverse cosine", "exp(-k)", ("k", "x")),
    ("inverse fourier", "exp(-k**2)", ("k", "x")),
])
def test_take_transform_is_sympy_transform(name, text, letters, sympy_calls):
    sp = _sp()
    function = getattr(sp, _formula_calculus.TRANSFORMS[name][0])
    a, b = (sp.Symbol(n) for n in letters)
    expected = function(sp.sympify(text), a, b, noconds=True)
    assert _quiet(_formula(text).take_transform, name).as_sympy() == expected
    assert _formula_calculus.TRANSFORMS[name][0] in sympy_calls


def test_take_transform_by_hand_laplace_table_and_hankel_and_inverse_mellin():
    sp = _sp()
    s, k, x = sp.symbols("s k x")
    assert _quiet(_formula("exp(-2*t)").take_transform, "laplace").as_sympy() == 1 / (s + 2)  # L{e^{-at}} = 1/(s+a)
    assert _quiet(_formula("t**3").take_transform, "laplace_transform").as_sympy() == 6 / s ** 4  # n!/s^(n+1)
    assert _quiet(_formula("exp(-r)").take_transform, "hankel").as_sympy() == (k ** 2 + 1) ** sp.Rational(-3, 2)
    back = _quiet(_formula("gamma(s)").take_transform, "inverse mellin", between=[0, "infinity"])
    assert back.as_sympy() == sp.exp(-x)


def test_take_transform_refuses_plainly():
    with pytest.raises(sdata.SimplydataError, match="needs the name"):
        _quiet(_formula("t").take_transform)
    with pytest.raises(sdata.SimplydataError, match="new letter"):
        _quiet(_formula("exp(-s*t)").take_transform, "laplace", from_letter="t", to_letter="s")
    with pytest.raises(sdata.SimplydataError, match="needs between="):
        _quiet(_formula("gamma(s)").take_transform, "inverse mellin")
    with pytest.raises(sdata.SimplydataError, match="order= goes with"):
        _quiet(_formula("exp(-t)").take_transform, "laplace", order=1)


# ------------------------------------------------------------------------------------------------ along a path
def test_find_area_along_path_is_sympy_line_integrate_and_2_pi_on_the_unit_circle(sympy_calls):
    sp = _sp()
    x, y, t = sp.symbols("x y t")
    found = _quiet(_formula("x**2 + y**2").find_area_along_path, path="x = cos(t), y = sin(t)", between=[0, "2*pi"])
    expected = sp.line_integrate(x ** 2 + y ** 2, sp.Curve([sp.cos(t), sp.sin(t)], (t, 0, 2 * sp.pi)), [x, y])
    assert found == pytest.approx(float(expected)) == pytest.approx(2 * math.pi)  # the circle's length times 1
    assert "line_integrate" in sympy_calls
    same = _quiet(_formula("x**2 + y**2").find_area_along_path, path={"x": "cos(t)", "y": "sin(t)"},
                  between=[0, "2*pi"])
    assert same == found
    with pytest.raises(sdata.SimplydataError, match="needs a formula for each letter"):
        _quiet(_formula("x + y").find_area_along_path, path="x = t", between=[0, 1])


# ------------------------------------------------------------------------------------------------ calculus checks
@pytest.mark.parametrize("kind, text, between", [
    ("rising", "x**3", [-1, 1]), ("falling", "-x**3", [-1, 1]), ("strictly rising", "exp(x)", None),
    ("strictly falling", "exp(-x)", None), ("one way only", "x**3 + x", None), ("bending up", "x**2", None),
    ("rising", "sin(x)", None),
])
def test_check_if_always_is_sympy(kind, text, between, sympy_calls):
    sp = _sp()
    x = sp.Symbol("x")
    function_name = _formula_calculus.ALWAYS[kind][0]
    domain = sp.S.Reals if between is None else sp.Interval(*between)
    expr = sp.sympify(text)
    expected = (sp.is_convex(expr, x, domain=domain) if function_name == "is_convex"
                else getattr(sp, function_name)(expr, domain, x))
    assert _quiet(_formula(text).check_if_always, kind, between=between) == expected
    assert function_name in sympy_calls


def test_check_if_always_by_hand():
    assert _quiet(_formula("x**2").check_if_always, "rising", between=[0, 5]) is True
    assert _quiet(_formula("x**2").check_if_always, "rising", between=[-1, 5]) is False
    assert _quiet(_formula("x**2").check_if_always, "convex") is True  # SymPy's name works too


def test_turning_points_undefined_points_and_period_are_sympy_and_by_hand():
    sp = _sp()
    x = sp.Symbol("x")
    points = _quiet(_formula("x**3 - 3*x").find_turning_points)
    assert _column(points, "at") == [-1.0, 1.0]  # 3x^2 - 3 = 0
    assert _column(points, "value") == [2.0, -2.0]
    assert {sp.sympify(v) for v in _column(points, "at exactly")} == set(sp.stationary_points(x ** 3 - 3 * x, x))
    sine = _quiet(_formula("sin(x)").find_turning_points, between=[0, 7])
    assert _column(sine, "at exactly") == ["pi/2", "3*pi/2"]
    undefined = _quiet(_formula("1/(x**2 - 1)").find_where_undefined)
    assert _column(undefined, "at") == [-1.0, 1.0]
    assert _quiet(_formula("sin(2*x)").find_period) == pytest.approx(math.pi)
    assert _quiet(_formula("x**2").find_period) is None
    with pytest.raises(sdata.SimplydataError, match="endless"):
        _quiet(_formula("sin(x)").find_turning_points)


# ------------------------------------------------------------------------------------------------ series
def test_find_fourier_series_of_x_is_the_known_series_and_sympy(sympy_calls):
    sp = _sp()
    x = sp.Symbol("x")
    found = _quiet(_formula("x").find_fourier_series, between=["-pi", "pi"])
    assert found.as_sympy() == sp.fourier_series(x, (x, -sp.pi, sp.pi)).truncate(3)
    # x = 2 * sum (-1)^(n+1) sin(n x)/n on (-pi, pi)
    assert sp.simplify(found.as_sympy() - (2 * sp.sin(x) - sp.sin(2 * x) + sp.Rational(2, 3) * sp.sin(3 * x))) == 0
    assert "fourier_series" in sympy_calls and "truncate" in sympy_calls


def test_residue_list_terms_product_fps_limit_seq_and_step_slope_are_sympy():
    sp = _sp()
    x, n, h, k = sp.symbols("x n h k")
    assert _quiet(_formula("exp(x)/x**3").find_residue_at, 0) == 0.5  # the coefficient of x**2 in exp(x) is 1/2
    assert _quiet(_formula("1/(x**2 + 1)").find_residue_at, "pi") == 0.0
    terms = _quiet(_formula("n**2").list_terms, between=[1, 5])
    assert _column(terms, "term") == [1.0, 4.0, 9.0, 16.0, 25.0]  # OEIS A000290
    product = _quiet(sdata.find_product_of_series, "k/(k + 1)", between=[1, "n"])
    kk = sp.Symbol("k", integer=True)
    assert product.as_sympy() == sp.product(kk / (kk + 1), (kk, 1, sp.Symbol("n", integer=True)))
    assert sp.simplify(product.as_sympy().subs(sp.Symbol("n", integer=True), 9)) == sp.Rational(1, 10)
    assert _quiet(sdata.find_product_of_series, "k", between=[1, 10]).as_sympy() == 3628800  # 10!
    every = _quiet(_formula("exp(x)").find_taylor_series, all_terms=True)
    assert str(every.as_sympy()) == str(sp.fps(sp.exp(x), x, 0).infinite)  # (a Dummy letter each time)
    assert _quiet(_formula("(-1)**n/n").find_limit_as, "n", goes_to="infinity", whole_numbers_only=True) == 0.0
    assert _quiet(_formula("n/(n + 1)").find_limit_as, "n", goes_to="infinity", whole_numbers_only=True) == 1.0
    step = _quiet(_formula("x**2").find_slope_formula, step="h")
    assert step.as_sympy() == sp.differentiate_finite(x ** 2, x, points=[x, x + h])
    assert sp.expand(step.as_sympy()) == 2 * x + h
    one = _quiet(_formula("n**2").find_slope_formula, step=1)
    assert sp.expand(one.as_sympy()) == sp.expand(sp.difference_delta(n ** 2, n))  # 2n + 1


def test_hessian_wronskian_and_casoratian_are_sympy():
    sp = _sp()
    x, y, n = sp.symbols("x y n")
    grid = _quiet(_formula("x**2*y + y**3").find_hessian)
    assert grid.as_sympy() == sp.hessian(x ** 2 * y + y ** 3, [x, y])
    assert _quiet(_formula("exp(x)").find_wronskian, ["exp(2*x)"]).as_sympy() == sp.exp(3 * x)  # by hand
    found = _quiet(_formula("2**n").find_wronskian, ["3**n"], whole_numbers_only=True)
    assert found.as_sympy() == sp.casoratian([2 ** n, 3 ** n], n)


# ------------------------------------------------------------------------------------------------ code and trees
@pytest.mark.parametrize("language", list(_formula_calculus.LANGUAGES))
def test_show_as_code_is_the_sympy_printer(language):
    sp = _sp()
    x = sp.Symbol("x")
    expr = sp.sin(x) ** 2 + sp.exp(-x)
    printer = getattr(sp, _formula_calculus.LANGUAGES[language][0])
    assert _quiet(_formula("sin(x)**2 + exp(-x)").show_as_code, language) == str(printer(expr))


def test_show_as_code_r_by_hand_and_tree_and_latex_options():
    sp = _sp()
    x = sp.Symbol("x")
    assert _quiet(_formula("sin(x)**2 + exp(-x)").show_as_code, "r") == "sin(x)^2 + exp(-x)"
    from sympy.printing.tree import tree

    assert _quiet(_formula("x**2 + 1").show_as_tree) == tree(x ** 2 + 1, assumptions=False).rstrip("\n")
    assert _quiet(_formula("x + 1").show_as_tree, as_graphviz=True) == sp.dotprint(x + 1)
    assert _quiet(_formula("x**2").show_as_latex, left_side="y") == "y = x^{2}"
    assert _quiet(_formula("x**2 + 1").show_as_latex, over_lines=True) == sp.multiline_latex(sp.Symbol("y"),
                                                                                             x ** 2 + 1)


# ------------------------------------------------------------------------------------------------ solving
def test_check_solution_is_checksol_checkodesol_checkpdesol(sympy_calls):
    assert _quiet(sdata.check_solution, "dy/dx = y", "y = 3*exp(x)") is True
    assert _quiet(sdata.check_solution, "dy/dx = y", "y = 3*exp(2*x)") is False
    assert _quiet(sdata.check_solution, "d2y/dx2 = -y", "y = sin(x)") is True
    assert _quiet(sdata.check_solution, "du/dx + du/dy = 0", "u = (x - y)**2") is True
    assert _quiet(sdata.check_solution, "x**2 = 4", "x = -2") is True
    assert _quiet(sdata.check_solution, "x + y = 3", {"x": 1, "y": 3}) is False
    assert {"checkodesol", "checkpdesol", "checksol"} <= set(sympy_calls)


def test_solve_whole_numbers_sequences_and_partial_equations_are_sympy():
    sp = _sp()
    x, y = sp.symbols("x y")
    table = _quiet(sdata.solve, "x**2 + y**2 = 25", exactly=True, whole_numbers_only=True)
    found = set(zip(_column(table, "x"), _column(table, "y")))
    expected = {(float(a), float(b)) for a, b in sp.diophantine(x ** 2 + y ** 2 - 25, syms=(x, y), permute=True)}
    assert found == expected and len(found) == 12  # r2(25) = 12 (OEIS A004018)
    line = _quiet(sdata.solve, "3*x + 5*y = 1", exactly=True, whole_numbers_only=True)
    assert _column(line, "x exactly") == ["5*t_0 + 2"]
    fibonacci = _quiet(sdata.solve, "a(n + 2) = a(n + 1) + a(n)", exactly=True, at_start={0: 0, 1: 1})
    n = [s for s in fibonacci.as_sympy().free_symbols][0]
    assert [sp.simplify(fibonacci.as_sympy().subs(n, i)) for i in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    same = _quiet(sdata.solve, "a(n + 2) = a(n + 1) + a(n)", exactly=True, at_start={"a(0)": 0, "a(1)": 1})
    assert same.as_sympy() == fibonacci.as_sympy()
    partial = _quiet(sdata.solve, "du/dx + 2*du/dy = 0", exactly=True)
    u, F = sp.Function("u"), sp.Function("F")
    assert partial.as_sympy() == sp.pdsolve(sp.Eq(u(x, y).diff(x) + 2 * u(x, y).diff(y), 0), u(x, y)).rhs
    assert partial.as_sympy() == F(2 * x - y)
    with pytest.raises(sdata.SimplydataError, match="go with exactly=True"):
        _quiet(sdata.solve, "x**2 + y**2 = 25", whole_numbers_only=True)


def test_list_ways_are_sympy_subsets_variations_cartes():
    sp = _sp()
    things = ["A", "B", "C", "D"]
    ways = _quiet(sdata.list_ways_to_choose, 2, out_of=things)
    assert list(zip(_column(ways, "1st"), _column(ways, "2nd"))) == list(sp.subsets(things, 2))
    again = _quiet(sdata.list_ways_to_choose, 2, out_of=3, with_repeats=True)
    assert again.count_rows() == 6  # (3 + 2 - 1) choose 2
    ordered = _quiet(sdata.list_ways_to_order, 2, out_of=["A", "B", "C"])
    assert list(zip(_column(ordered, "1st"), _column(ordered, "2nd"))) == list(sp.variations(["A", "B", "C"], 2))
    each = _quiet(sdata.list_ways_to_choose, one_from_each=[["red", "blue"], ["S", "M", "L"]])
    assert each.count_rows() == 6
    assert list(zip(_column(each, "1st"), _column(each, "2nd"))) == list(sp.cartes(["red", "blue"],
                                                                                    ["S", "M", "L"]))
    with pytest.raises(sdata.SimplydataError, match="lists up to"):
        _quiet(sdata.list_ways_to_choose, 10, out_of=40)


# ------------------------------------------------------------------------------------------------ number theory
def test_check_if_prime_and_prime_factors_are_sympy(sympy_calls):
    sp = _sp()
    values = [0, 1, 2, 9, 11, 561, 7919]
    answer = _quiet(sdata.number_list(values).check_if_prime)
    assert answer.as_numpy().tolist() == [sp.isprime(v) for v in values]
    factors = _quiet(sdata.number_list([12, 35]).find_prime_factors)
    assert _column(factors, "prime") == [2.0, 3.0, 5.0, 7.0]
    assert _column(factors, "times") == [2, 1, 1, 1]
    fraction = _quiet(sdata.number_list([0.75]).find_prime_factors)
    assert dict(zip(_column(fraction, "prime"), _column(fraction, "times"))) == {
        float(p): t for p, t in sp.factorrat(sp.Rational(3, 4)).items()}
    different = _quiet(sdata.number_list([360]).find_prime_factors, show="different primes")
    assert _column(different, "prime") == [float(p) for p in sp.primefactors(360)]
    assert {"isprime", "factorint", "factorrat", "primefactors"} <= set(sympy_calls)
    with pytest.raises(sdata.SimplydataError, match="whole numbers"):
        _quiet(sdata.number_list([2.5]).check_if_prime)
    with pytest.raises(sdata.SimplydataError, match="2\\*\\*53"):
        _quiet(sdata.number_list([2.0 ** 60]).check_if_prime)


EACH = {"divisors": ([12], {}), "number of divisors": ([12, 28], {}), "proper divisors": ([12], {}),
        "number of proper divisors": ([12], {}), "abundance": ([12], {}), "perfect": ([6, 12, 28], {}),
        "abundant": ([12, 13], {}), "deficient": ([12, 13], {}), "amicable with": ([220], {"other": 284}),
        "carmichael": ([561, 560], {}), "mersenne prime": ([31, 63], {}), "perfect power": ([64], {}),
        "next prime": ([12], {}), "previous prime": ([12], {}), "nth prime": ([1, 100], {}),
        "nth composite": ([1, 10], {}), "primes up to": ([30], {}), "number of composites up to": ([30], {}),
        "primorial": ([5], {}), "partitions": ([100], {}), "nth mersenne exponent": ([10], {}),
        "binomial coefficients": ([6], {}), "multinomial coefficients": ([2], {"other": 3}),
        "times divisible by": ([48], {"other": 2}), "primitive root": ([7], {}),
        "primitive root modulo": ([3], {"modulo": 7}), "quadratic residue modulo": ([2], {"modulo": 7}),
        "power residue modulo": ([2], {"modulo": 7, "power": 3}), "order modulo": ([2], {"modulo": 7}),
        "discrete log": ([12], {"modulo": 41, "base": 7}), "square roots modulo": ([10], {"modulo": 13}),
        "nth roots modulo": ([1], {"modulo": 7, "power": 3}), "quadratic residues": ([7], {}),
        "inverse modulo": ([3], {"modulo": 7}), "whole nth root": ([17], {"power": 2}),
        "whole log": ([125], {"base": 5}), "number of digits": ([1000], {}), "trailing zero bits": ([40], {}),
        "continued fraction": ([4.4623655913978495], {}), "continued fraction convergents": ([0.75], {}),
        "egyptian fraction": ([0.75], {})}


def test_every_fact_is_named_and_tested():
    assert set(EACH) | {"greatest common divisor", "least common multiple", "number from continued fraction",
                        "periodic continued fraction", "quadratic congruence"} == set(number_theory_words.FACTS)


def _sympy_answer(sp, name, v, options):
    function = getattr(sp, number_theory_words.FACTS[name][0])
    args = number_theory_words.NumberTheoryWords._arguments(sp, name, v, options)
    if name == "primes up to":
        return list(sp.primerange(2, v + 1))
    if name == "continued fraction convergents":
        return list(sp.continued_fraction_convergents(sp.continued_fraction(*args)))
    named = {"all_roots": True} if name in ("square roots modulo", "nth roots modulo") else {}
    return function(*args, **named)


@pytest.mark.parametrize("name", list(EACH))
def test_find_number_fact_is_sympy(name):
    sp = _sp()
    values, options = EACH[name]
    gives = number_theory_words.FACTS[name][2]
    found = _quiet(sdata.number_list(values).find_number_fact, name, **options)
    for v in values:
        expected = _sympy_answer(sp, name, int(v) if float(v).is_integer() else v, options)
        if gives in ("yes or no",):
            assert found.as_numpy().tolist()[values.index(v)] == bool(expected)
        elif gives == "number":
            got = found.as_numpy().tolist()[values.index(v)] if hasattr(found, "as_numpy") else \
                _column(found, "answer exactly")[values.index(v)]
            assert (got == float(expected)) if hasattr(found, "as_numpy") else got == str(expected)
        elif gives in ("numbers", "fractions"):
            rows = [e for n, e in zip(_column(found, "number"), _column(found, "answer exactly")) if n == float(v)]
            assert rows == [str(sp.Rational(e)) for e in expected]
        elif gives == "pair":
            first = _column(found, "base" if name == "perfect power" else "root" if "root" in name else "log")
            assert first == [float(expected[0])]
        elif gives == "pairs":
            assert _column(found, "coefficient") == [float(c) for _, c in sorted(expected.items(), reverse=True)]


def test_number_facts_by_hand_and_published():
    assert _quiet(sdata.number_list([6, 28, 496, 12]).find_number_fact, "perfect").as_numpy().tolist() == [
        True, True, True, False]  # OEIS A000396
    assert _quiet(sdata.number_list([100]).find_number_fact, "partitions").as_numpy().tolist() == [190569292]  # A000041
    assert _quiet(sdata.number_list([10]).find_number_fact, "nth prime").as_numpy().tolist() == [29]  # A000040
    big = _quiet(sdata.number_list([28]).find_number_fact, "primorial")  # above 2**53: exact text
    assert _column(big, "answer exactly") == ["2566376117594999414479597815340071648394470"]
    assert _quiet(sdata.number_list([12, 18, 30]).find_number_fact, "greatest common divisor") == 6.0
    assert _quiet(sdata.number_list([4, 6]).find_number_fact, "least common multiple") == 12.0
    assert _quiet(sdata.number_list([4, 2, 6, 7]).find_number_fact, "number from continued fraction") == \
        pytest.approx(415 / 93)
    roots = _quiet(sdata.number_list([1, 0, -1]).find_number_fact, "quadratic congruence", modulo=8)
    assert roots.as_numpy().tolist() == [1.0, 3.0, 5.0, 7.0]
    periodic = _quiet(sdata.number_list([0, 1, 2]).find_number_fact, "periodic continued fraction")
    assert _column(periodic, "answer exactly") == ["1", "[2]"]  # sqrt(2) = [1; 2, 2, 2 ...]
    with pytest.raises(sdata.SimplydataError, match="no answer for 3"):
        _quiet(sdata.number_list([3]).find_number_fact, "inverse modulo", modulo=9)
    with pytest.raises(sdata.SimplydataError, match="takes numbers from 0 to"):
        _quiet(sdata.number_list([400]).find_number_fact, "primorial")
    with pytest.raises(sdata.SimplydataError, match="needs modulo="):
        _quiet(sdata.number_list([3]).find_number_fact, "inverse modulo")


# ------------------------------------------------------------------------------------------------ exact grids
def test_exact_grid_words_are_sympy_matrix(sympy_calls):
    sp = _sp()
    a = sp.Symbol("a")
    grid = _quiet(sdata.number_grid, [[1, "1/3"], ["a", 2]], exactly=True)
    matrix = sp.Matrix([[1, sp.Rational(1, 3)], [a, 2]])
    assert grid.as_sympy() == matrix
    assert _quiet(grid.find_determinant).as_sympy() == matrix.det()
    assert _quiet(grid.find_permanent).as_sympy() == matrix.per()
    assert _quiet(grid.find_value_at, a=3).as_numpy().tolist() == [[1.0, 1 / 3], [3.0, 2.0]]
    square = _quiet(sdata.number_grid, [[2, 1], [1, 2]], exactly=True)
    _quiet(square.take_inverse)
    assert square.as_sympy() == sp.Matrix([[2, 1], [1, 2]]).inv()
    _quiet(square.undo)
    assert _column(_quiet(square.find_eigenvalues), "eigenvalue") == [3.0, 1.0]
    assert "det" in sympy_calls and "per" in sympy_calls


def test_permanent_and_orthogonal_columns_on_a_grid_of_numbers():
    sp = _sp()
    assert _quiet(sdata.number_grid([[1, 2], [3, 4]]).find_permanent) == 10.0  # 1*4 + 2*3
    ones = _quiet(sdata.number_grid([[1] * 5] * 5).find_permanent)
    assert ones == 120.0  # the permanent of the n x n grid of 1s is n! (OEIS A000142)
    grid = sdata.number_grid([[1, 1], [1, 0]])
    _quiet(grid.make_columns_orthogonal)
    expected = sp.Matrix.hstack(*sp.GramSchmidt([sp.Matrix([1, 1]), sp.Matrix([1, 0])]))
    assert grid.as_numpy().tolist() == [[float(v) for v in expected.row(i)] for i in range(2)]
    unit = sdata.number_grid([[3, 1], [4, 2]])
    _quiet(unit.make_columns_orthogonal, of_length_1=True)
    values = unit.as_numpy()
    assert (values.T @ values).ravel().tolist() == pytest.approx([1.0, 0.0, 0.0, 1.0])
    with pytest.raises(sdata.SimplydataError, match="depend on each other"):
        _quiet(sdata.number_grid([[1, 2], [2, 4]]).make_columns_orthogonal)
