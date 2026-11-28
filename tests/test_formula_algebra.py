"""Families for 100 %, batches 22-23 (plan section 2.10, approved by Manish 2026-11-28, G14): polynomial algebra on a
formula, the family find_fact, the by= values of make_simpler, turn_into_sum and turn_into_product, and SymPy's own
names and constants inside the text of sdata.formula.

Every answer is compared with SymPy doing the same directly, and with the answer worked out by hand where there is
one. Every SymPy call of the new words goes through simplydata's one time limit (checked by watching
run_with_time_limit), and the counting functions keep the rule that a number inside them is at most 1000.
"""

from __future__ import annotations

import contextlib
import io
import math

import pytest

import simplydata as sdata
from simplydata import _formula_algebra, _formula_names, _time_limit

pytestmark = pytest.mark.usefixtures("needs_sympy")


def _sp():
    import sympy as sp

    return sp, sp.Symbol("x")


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
    """The SymPy functions run under the time limit while the test runs."""
    calls = []
    real = _time_limit.run_with_time_limit

    def watched(call, *values, **named):
        calls.append(getattr(call, "__name__", str(call)))
        return real(call, *values, **named)

    monkeypatch.setattr(_time_limit, "run_with_time_limit", watched)
    return calls


# ------------------------------------------------------------------------------------------------ find_roots
def test_find_roots_gives_each_root_once_with_how_many_times_as_sympy_all_roots():
    sp, x = _sp()
    roots = _quiet(_formula("(x - 1)**2*(x**2 + 1)").find_roots)
    listed = sp.all_roots((x - 1) ** 2 * (x ** 2 + 1))
    assert _column(roots, "root exactly") == [str(r) for r in dict.fromkeys(listed)]
    assert _column(roots, "times") == [listed.count(r) for r in dict.fromkeys(listed)]
    assert _column(roots, "root")[0] == 1.0 and math.isnan(_column(roots, "root")[1])


def test_find_roots_of_a_cubic_by_hand_and_sympy(sympy_calls):
    roots = _quiet(_formula("x**3 - 2*x**2 - x + 2").find_roots)
    assert _column(roots, "root") == [-1.0, 1.0, 2.0]
    assert "all_roots" in sympy_calls


def test_find_roots_real_only_is_sympy_real_roots_with_crootof():
    sp, x = _sp()
    roots = _quiet(_formula("x**5 - x + 1").find_roots, real_only=True)
    expected = sp.real_roots(x ** 5 - x + 1)
    assert _column(roots, "root exactly") == [str(r) for r in expected]
    assert _column(roots, "root") == pytest.approx([float(r) for r in expected], rel=1e-15)
    value = _column(roots, "root")[0]
    assert abs(value ** 5 - value + 1) < 1e-13


def test_find_roots_fractions_only_is_sympy_ground_roots_smallest_first(sympy_calls):
    sp, x = _sp()
    roots = _quiet(_formula("2*x**3 - 3*x**2 - 2*x + 3").find_roots, fractions_only=True)
    expected = sorted(sp.ground_roots(2 * x ** 3 - 3 * x ** 2 - 2 * x + 3), key=float)
    assert _column(roots, "root exactly") == [str(r) for r in expected] == ["-1", "1", "3/2"]
    assert "ground_roots" in sympy_calls
    none = _quiet(_formula("2*x**2 - 1").find_roots, fractions_only=True)
    assert _quiet(none.count_rows) == 0


def test_find_roots_in_decimals_is_sympy_nroots():
    sp, x = _sp()
    roots = _quiet(_formula("x**3 - 2").find_roots, exactly=False)
    assert _column(roots, "root as text") == [str(r) for r in sp.nroots(x ** 3 - 2, n=15)]
    assert _column(roots, "root")[0] == pytest.approx(2 ** (1 / 3), rel=1e-15)
    assert all(math.isnan(v) for v in _column(roots, "root")[1:])


def test_find_roots_count_and_between_are_sympy_count_roots_and_real_roots():
    sp, x = _sp()
    f = x ** 3 - 2 * x ** 2 - x + 2
    formula = _formula("x**3 - 2*x**2 - x + 2")
    assert _quiet(formula.find_roots, show="count") == sp.count_roots(f) == 3
    assert _quiet(formula.find_roots, show="count", between=[0, 3]) == sp.count_roots(f, 0, 3) == 2
    inside = _quiet(formula.find_roots, between=[0, 3])
    assert _column(inside, "root exactly") == [str(r) for r in sp.real_roots(f) if 0 <= r <= 3]


def test_find_roots_intervals_within_is_sympy_intervals_with_eps():
    sp, x = _sp()
    found = _quiet(_formula("x**2 - 2").find_roots, show="intervals", within=0.001)
    expected = sp.intervals(x ** 2 - 2, eps=sp.Rational(1, 1000))
    assert _column(found, "from exactly") == [str(a) for (a, _), _ in expected]
    assert _column(found, "to exactly") == [str(b) for (_, b), _ in expected]
    low, high = _column(found, "from")[1], _column(found, "to")[1]
    assert low <= math.sqrt(2) <= high and high - low <= 0.001


@pytest.mark.parametrize("text, call, said", [
    ("x*y - 1", {}, "one letter"),
    ("sin(x)", {}, "not one"),
    ("1/(x - 1)", {}, "split_into_top_and_bottom"),
    ("x**2 - 2", {"within": 0.1}, 'show="intervals"'),
    ("x**2 - 2", {"show": "middle"}, "does not know"),
    ("x**2 - 2", {"exactly": False, "real_only": True}, "exactly=False"),
    ("sqrt(2)*x**2 - 1", {}, "exactly=False"),
])
def test_find_roots_says_plainly_what_it_cannot_do(text, call, said):
    with pytest.raises(sdata.SimplydataError, match=said):
        _quiet(_formula(text).find_roots, **call)


# ------------------------------------------------------------------------------------------------ find_degree
def test_find_degree_is_sympy_degree_total_degree_and_degree_list(sympy_calls):
    sp, _ = _sp()
    x, y = sp.symbols("x y")
    f = x ** 3 * y + x * y ** 2 + 1
    formula = _formula("x**3*y + x*y**2 + 1")
    assert _quiet(formula.find_degree) == sp.total_degree(f) == 4
    assert _quiet(formula.find_degree, for_letter="x") == sp.degree(f, x) == 3
    assert _quiet(formula.find_degree, for_letter=["x", "y"]) == dict(zip("xy", sp.degree_list(f, x, y)))
    assert _quiet(_formula("x**7 - 1").find_degree) == 7
    assert _quiet(_formula("5").find_degree) == 0
    assert {"total_degree", "degree", "degree_list"} <= set(sympy_calls)


def test_find_degree_refuses_what_is_not_a_polynomial():
    with pytest.raises(sdata.SimplydataError, match="polynomial"):
        _quiet(_formula("1/x + x").find_degree)
    with pytest.raises(sdata.SimplydataError, match="for_letter="):
        _quiet(_formula("x**2").find_degree, for_letter="z")


# ------------------------------------------------------------------------------------------------ divide_by
def test_divide_by_is_sympy_div_and_the_remainder_theorem(sympy_calls):
    sp, x = _sp()
    f = x ** 3 - 2 * x + 5
    quotient, remainder = _quiet(_formula("x**3 - 2*x + 5").divide_by, "x - 1")
    expected = sp.div(f, x - 1, x)
    assert (quotient.as_sympy(), remainder.as_sympy()) == expected
    assert remainder.as_sympy() == f.subs(x, 1) == 4  # the remainder theorem
    assert "div" in sympy_calls


@pytest.mark.parametrize("options, function", [
    ({"show": "quotient"}, "quo"), ({"show": "remainder"}, "rem"),
    ({"show": "quotient", "without_fractions": True}, "pquo"),
    ({"show": "remainder", "without_fractions": True}, "prem"),
])
def test_divide_by_options_are_sympys_division_functions(options, function):
    sp, x = _sp()
    f, g = x ** 3 - 2 * x + 5, 2 * x - 1
    found = _quiet(_quiet(_formula, "x**3 - 2*x + 5").divide_by, "2*x - 1", **options)
    assert _quiet(found.as_sympy) == getattr(sp, function)(f, g, x)


def test_divide_by_without_fractions_and_with_no_remainder():
    sp, x = _sp()
    f = x ** 3 - 2 * x + 5
    quotient, remainder = _quiet(_formula("x**3 - 2*x + 5").divide_by, "2*x - 1", without_fractions=True)
    assert (quotient.as_sympy(), remainder.as_sympy()) == sp.pdiv(f, 2 * x - 1, x)
    assert remainder.as_sympy() == 8 * f.subs(x, sp.Rational(1, 2)) == 33  # 2**3 * f(1/2)
    exact = _quiet(_formula("x**3 - 1").divide_by, "x - 1", with_no_remainder=True)
    assert exact.as_sympy() == sp.exquo(x ** 3 - 1, x - 1, x)
    pseudo = _quiet(_formula("4*x**2 - 1").divide_by, "2*x - 1", with_no_remainder=True, without_fractions=True)
    assert pseudo.as_sympy() == sp.pexquo(4 * x ** 2 - 1, 2 * x - 1, x)
    with pytest.raises(sdata.SimplydataError, match="without a remainder"):
        _quiet(_formula("x**3 - 2*x + 5").divide_by, "x - 1", with_no_remainder=True)
    with pytest.raises(sdata.SimplydataError, match="by 0"):
        _quiet(_formula("x**2").divide_by, "0")
    with pytest.raises(sdata.SimplydataError, match="needs the other formula"):
        _quiet(_formula("x**2").divide_by)


def test_divide_by_takes_a_formula_and_letters():
    sp, _ = _sp()
    x, y = sp.symbols("x y")
    other = _formula("x - y")
    quotient, remainder = _quiet(_formula("x**2 - y**2 + 1").divide_by, other, for_letter="x")
    assert (quotient.as_sympy(), remainder.as_sympy()) == sp.div(x ** 2 - y ** 2 + 1, x - y, x)


# ------------------------------------------------------------------------------------------------ gcd and lcm
def test_find_common_factor_and_multiple_are_sympy_gcd_and_lcm(sympy_calls):
    sp, x = _sp()
    f, g = x ** 2 + 2 * x + 1, x ** 2 - 1
    formula = _formula("x**2 + 2*x + 1")
    assert _quiet(formula.find_common_factor_with, "x**2 - 1").as_sympy() == sp.gcd(f, g) == x + 1
    assert _quiet(formula.find_common_multiple_with, "x**2 - 1").as_sympy() == sp.lcm(f, g)
    many = ["x**2 - 1", "x**3 + 1"]
    assert _quiet(formula.find_common_factor_with, many).as_sympy() == sp.gcd_list([f, g, x ** 3 + 1])
    assert _quiet(formula.find_common_multiple_with, many).as_sympy() == sp.lcm_list([f, g, x ** 3 + 1])
    assert {"gcd", "lcm", "gcd_list", "lcm_list"} <= set(sympy_calls)


def test_find_common_factor_with_show_is_cofactors_gcdex_and_half_gcdex():
    sp, x = _sp()
    f, g = x ** 2 - 1, x ** 2 + 3 * x + 2
    formula = _formula("x**2 - 1")
    parts = _quiet(formula.find_common_factor_with, "x**2 + 3*x + 2", show="common factor and the rest")
    assert tuple(p.as_sympy() for p in parts) == sp.cofactors(f, g)
    s, t, h = _quiet(formula.find_common_factor_with, "x**2 + 3*x + 2", show="combination")
    assert (s.as_sympy(), t.as_sympy(), h.as_sympy()) == sp.gcdex(f, g, x)
    assert sp.expand(s.as_sympy() * f + t.as_sympy() * g - h.as_sympy()) == 0  # Bezout's identity
    s, h = _quiet(formula.find_common_factor_with, "x**2 + 3*x + 2", show="half combination")
    assert (s.as_sympy(), h.as_sympy()) == sp.half_gcdex(f, g, x)
    with pytest.raises(sdata.SimplydataError, match="one other formula"):
        _quiet(formula.find_common_factor_with, ["x + 1", "x - 1"], show="combination")


# ------------------------------------------------------------------------------------------------ fractions and parts
def test_turn_into_one_fraction_is_sympy_together_and_can_be_undone():
    sp, x = _sp()
    formula = _formula("1/x + 1/(x + 1)")
    _quiet(formula.turn_into_one_fraction)
    assert formula.as_sympy() == sp.together(1 / x + 1 / (x + 1))
    _quiet(formula.undo)
    assert formula.as_sympy() == 1 / x + 1 / (x + 1)


def test_split_into_top_and_bottom_is_sympy_fraction():
    sp, x = _sp()
    top, bottom = _quiet(_formula("(x + 1)/(x - 2)").split_into_top_and_bottom)
    assert (top.as_sympy(), bottom.as_sympy()) == sp.fraction((x + 1) / (x - 2))
    top, bottom = _quiet(_formula("x**2").split_into_top_and_bottom)
    assert bottom.as_sympy() == 1


def test_find_repeated_parts_is_sympy_cse_and_never_reuses_a_letter():
    sp, x = _sp()
    parts, shorter = _quiet(_formula("(x + 1)**2 + sin(x + 1)").find_repeated_parts)
    replacements, reduced = sp.cse((x + 1) ** 2 + sp.sin(x + 1))
    assert {k: v.as_sympy() for k, v in parts.items()} == {str(n): p for n, p in replacements}
    assert shorter.as_sympy() == reduced[0]
    parts, _ = _quiet(_formula("(x0 + 1)**2 + sin(x0 + 1)").find_repeated_parts)
    assert "x0" not in parts


# ------------------------------------------------------------------------------------------------ find_fact
FACT_CASES = [  # (formula, name, options, SymPy call)
    ("x**2 - 3*x + 1", "discriminant", {}, lambda sp, x, f: sp.discriminant(f)),
    ("x**3 - x + 1", "discriminant", {}, lambda sp, x, f: sp.discriminant(f)),
    ("x**2 - 3*x + 1", "resultant", {"other": "x - 1"}, lambda sp, x, f: sp.resultant(f, x - 1, x)),
    ("x**2 - 3*x + 1", "leading coefficient", {}, lambda sp, x, f: sp.LC(f)),
    ("3*x**2 - 3*x + 1", "LC", {}, lambda sp, x, f: sp.LC(f)),
    ("6*x**2 + 4", "number factor", {}, lambda sp, x, f: sp.content(f)),
]


@pytest.mark.parametrize("text, name, options, call", FACT_CASES)
def test_find_fact_numbers_are_sympys(text, name, options, call):
    sp, x = _sp()
    f = sp.sympify(text, locals={"x": x})
    assert _quiet(_formula(text).find_fact, name, **options) == float(call(sp, x, f))


FORMULA_FACTS = [  # (formula, name, options, SymPy call)
    ("x**2 - 3*x + 1", "leading term", {}, lambda sp, x, f: sp.LT(f)),
    ("6*x**2 + 4", "without number factor", {}, lambda sp, x, f: sp.primitive(f)[1]),
    ("x**4 - 1", "square-free part", {}, lambda sp, x, f: sp.sqf_part(f)),
    ("2*x**2 + 4", "divided by leading coefficient", {}, lambda sp, x, f: sp.monic(f)),
    ("x**2 - 3*x + 1", "put into", {"other": "x + 1"}, lambda sp, x, f: sp.compose(f, x + 1)),
    ("x", "inverse modulo", {"other": "x**2 + 1"}, lambda sp, x, f: sp.invert(f, x ** 2 + 1)),
    ("5*x + 7", "coefficients modulo", {"other": 3}, lambda sp, x, f: sp.trunc(f, 3)),
    ("x**2 - 3*x + 1", "powers of roots", {"power": 2}, lambda sp, x, f: sp.nth_power_roots_poly(f, 2)),
    ("sqrt(2) + sqrt(3)", "minimal polynomial", {}, lambda sp, x, f: sp.minimal_polynomial(f, x)),
    ("sqrt(2) + sqrt(3)", "minpoly", {"for_letter": "t"},
     lambda sp, x, f: sp.minimal_polynomial(f, sp.Symbol("t"))),
    ("factorial(k)", "term ratio", {}, lambda sp, x, f: sp.hypersimp(f, sp.Symbol("k"))),
    ("x**2 + 1", "remainder by several", {"other": ["x - 1"]}, lambda sp, x, f: sp.reduced(f, [x - 1])[1]),
]


@pytest.mark.parametrize("text, name, options, call", FORMULA_FACTS)
def test_find_fact_formulas_are_sympys(text, name, options, call):
    sp, x = _sp()
    f = _formula(text).as_sympy() if "factorial" not in text else sp.factorial(sp.Symbol("k"))
    found = _quiet(_formula(text).find_fact, name, **options)
    assert sp.simplify(found.as_sympy() - call(sp, x, f)) == 0


def test_find_fact_lists_tables_and_texts_are_sympys(sympy_calls):
    sp, x = _sp()
    f = x ** 2 - 3 * x + 1
    formula = _formula("x**2 - 3*x + 1")
    sturm = _quiet(formula.find_fact, "sturm sequence")
    assert [s.as_sympy() if hasattr(s, "as_sympy") else sp.nsimplify(s) for s in sturm] == sp.sturm(f)
    assert _quiet(formula.find_fact, "viete formulas") == [f"{a} = {b}" for a, b in sp.viete(f)]
    assert _quiet(formula.find_fact, "galois group") == sp.galois_group(f, by_name=True)[0].name
    assert _quiet(formula.find_fact, "coefficients") == [float(c) for c in sp.Poly(f, x).all_coeffs()]
    parts = _quiet(_formula("x**4 + 2*x**2 + 1").find_fact, "parts it is made of")
    assert [p.as_sympy() for p in parts] == sp.decompose(x ** 4 + 2 * x ** 2 + 1)
    subresultants = _quiet(formula.find_fact, "subresultants", other="x - 1")
    expected = sp.subresultants(f, x - 1)
    assert [s.as_sympy() for s in subresultants[:2]] == expected[:2] and subresultants[2] == float(expected[2])
    factors = _quiet(_formula("2*x**2 - 2").find_fact, "factors")
    number, pairs = sp.factor_list(2 * x ** 2 - 2)
    assert _column(factors, "factor") == [str(number)] + [str(p) for p, _ in pairs]
    repeated = _quiet(_formula("(x - 1)**2*(x + 1)").find_fact, "repeated factors")
    assert _column(repeated, "times") == [k for _, k in sp.sqf_list((x - 1) ** 2 * (x + 1))[1]]
    falling = _quiet(_formula("x**3 - x").find_fact, "factorial factors")
    assert _column(falling, "factor") == [f"ff({p}, {k})" for p, k in sp.gff_list(x ** 3 - x)]
    symmetric, rest = _quiet(_formula("x**2 + y**2").find_fact, "symmetric form")
    s1, s2 = sp.symbols("s1 s2")
    assert (symmetric.as_sympy(), rest.as_sympy()) == (s1 ** 2 - 2 * s2, 0)
    basis = _quiet(_formula("x**2*y - 1").find_fact, "groebner basis", other=["x*y - 1"])
    y = sp.Symbol("y")
    assert [b.as_sympy() for b in basis] == list(sp.groebner([x ** 2 * y - 1, x * y - 1], x, y, order="lex").exprs)
    assert {"sturm", "viete", "galois_group", "factor_list", "groebner"} <= set(sympy_calls)


def test_find_fact_asks_for_the_letter_and_the_values_it_needs():
    sp, _ = _sp()
    a, b, c, x = sp.symbols("a b c x")
    found = _quiet(_formula("a*x**2 + b*x + c").find_fact, "discriminant", for_letter="x")
    assert found.as_sympy() == sp.discriminant(a * x ** 2 + b * x + c, x) == b ** 2 - 4 * a * c
    with pytest.raises(sdata.SimplydataError, match="for_letter="):
        _quiet(_formula("a*x**2 + b*x + c").find_fact, "discriminant")
    with pytest.raises(sdata.SimplydataError, match="needs the other formula"):
        _quiet(_formula("x**2").find_fact, "resultant")
    with pytest.raises(sdata.SimplydataError, match="power="):
        _quiet(_formula("x**2 - 1").find_fact, "powers of roots")
    with pytest.raises(sdata.SimplydataError, match="whole number"):
        _quiet(_formula("x**2 - 1").find_fact, "coefficients modulo", other=1.5)
    with pytest.raises(sdata.SimplydataError, match="without letters"):
        _quiet(_formula("x + sqrt(2)").find_fact, "minimal polynomial")
    with pytest.raises(sdata.SimplydataError, match="Did you mean"):
        _quiet(_formula("x**2 - 1").find_fact, "discriminat")
    with pytest.raises(sdata.SimplydataError, match="needs the name"):
        _quiet(_formula("x**2 - 1").find_fact)


def test_every_fact_has_a_sympy_function():
    import sympy as sp

    for name, (function, needs, gives, about) in _formula_algebra.FACTS.items():
        owner = sp.Poly if function.startswith("Poly.") else sp
        assert callable(getattr(owner, function.split(".")[-1])), name
        assert about and gives
    for spelling, name in _formula_algebra.FACT_SPELLINGS.items():
        assert name in _formula_algebra.FACTS, spelling


# ------------------------------------------------------------------------------------------------ by= values
@pytest.mark.parametrize("value", list(_formula_algebra.SIMPLER))
def test_every_make_simpler_value_is_its_sympy_function(value):
    import sympy as sp

    samples = {"trig functions": "sin(x)**2 + cos(x)**2", "exponentials and trig": "exp(x) + exp(-x)",
               "trig rules": "sin(x)**4 - cos(x)**4", "powers": "x**a*x**b", "powers of powers": "(x**a)**b",
               "logs": "log(x) + log(y)", "fractions": "(x**2 - 1)/(x - 1) + 1/x", "common factors":
               "(x**2 - 1)/(x - 1)", "roots in the bottom": "1/(1 + sqrt(2))", "nested roots": "sqrt(5 + 2*sqrt(6))",
               "gamma functions": "gamma(x + 1)/gamma(x)", "factorials": "factorial(n + 1)/factorial(n)",
               "bessel functions": "besselJ(x, 1) + besselJ(x, 3)",
               "hypergeometric functions": "hyper((1, 1), (2,), x)",
               "kronecker deltas": "KroneckerDelta(a, b)*KroneckerDelta(a, b)", "signs": "-(x - 1)",
               "letters apart": "x*y + x", "conditions":
               "Piecewise((x, x > 0), (0, True)) + 1", "decimals as fractions": "0.5*x + 0.25"}
    formula = _formula(samples[value])
    before = formula.as_sympy()
    function = getattr(sp, _formula_algebra.SIMPLER[value][0])
    _quiet(formula.make_simpler, by=value)
    assert formula.as_sympy() == function(before)
    _quiet(formula.undo)
    assert formula.as_sympy() == before


@pytest.mark.parametrize("value", list(_formula_algebra.SUM))
def test_every_turn_into_sum_value_is_its_sympy_function(value):
    import sympy as sp

    samples = {"logs": "log(x*y)", "trig functions": "sin(a + b)", "powers": "x**(a + b)",
               "power of a product": "(x*y)**a", "products": "x*(y + 1)*(x + 1)", "powers of sums": "(x + y)**3",
               "real and imaginary parts": "exp(x)", "special functions": "gamma(x + 1)"}
    formula = _formula(samples[value])
    before = formula.as_sympy()
    _quiet(formula.turn_into_sum, by=value)
    assert formula.as_sympy() == getattr(sp, _formula_algebra.SUM[value][0])(before)


@pytest.mark.parametrize("value", list(_formula_algebra.PRODUCT))
def test_every_turn_into_product_value_is_its_sympy_function(value):
    import sympy as sp

    samples = {"common factors": "2*x + 4*x*y", "common factors over one fraction": "x/2 + x**2/4",
               "common power of letters": "x**3 + x**2", "repeated factors": "x**3 - x**2 - x + 1",
               "nested": "x**3 + 2*x + 1"}
    formula = _formula(samples[value])
    before = formula.as_sympy()
    _quiet(formula.turn_into_product, by=value)
    assert formula.as_sympy() == getattr(sp, _formula_algebra.PRODUCT[value][0])(before)


def test_by_takes_sympys_names_and_says_the_choices():
    sp, x = _sp()
    formula = _formula("x**a*x**b")
    _quiet(formula.make_simpler, by="powsimp")
    a, b = sp.symbols("a b")
    assert formula.as_sympy() == x ** (a + b)
    with pytest.raises(sdata.SimplydataError, match='by="powers"'):
        _quiet(formula.make_simpler, by="power simp")
    with pytest.raises(sdata.SimplydataError, match="You can use"):
        _quiet(formula.turn_into_sum, by="everything")


def test_the_by_steps_run_under_the_time_limit(sympy_calls):
    _quiet(_formula("sin(x)**2 + cos(x)**2").make_simpler, by="trig functions")
    _quiet(_formula("log(x*y)").turn_into_sum, by="logs")
    _quiet(_formula("x**3 + 2*x + 1").turn_into_product, by="nested")
    assert {"trigsimp", "expand_log", "horner"} <= set(sympy_calls)


# ------------------------------------------------------------------------------------------------ formula names
@pytest.mark.parametrize("entry", _formula_names.NAMES, ids=[e.name for e in _formula_names.NAMES])
def test_every_formula_name_is_sympys_own_function(entry):
    import sympy as sp

    text = f"{entry.name}({entry.sample})"
    found = _formula(text).as_sympy()
    letters = {n: sp.Symbol(n) for n in ("x", "y", "theta", "phi")}
    names = {**letters, "I": sp.I, "pi": sp.pi, "sqrt": sp.sqrt, "exp": sp.exp, "True": True,
             entry.name: getattr(sp, entry.sympy)}
    if entry.name == "Ynm_c":
        names["Ynm_c"] = sp.Ynm_c
    if entry.name == "Eijk":
        names["Eijk"] = sp.Eijk
    expected = sp.parse_expr(text.replace("sqrt(-16)", "4*I").replace("sqrt(-1)", "I"), local_dict=names)
    assert found == expected or sp.simplify(found - expected) == 0, (text, found, expected)


def test_formula_names_are_letters_without_brackets_and_constants_are_sympys():
    sp, x = _sp()
    found = _formula("re + ln + sec + bell")
    assert {str(s) for s in found.as_sympy().free_symbols} == {"re", "ln", "sec", "bell"}
    constants = _formula("Catalan + EulerGamma + GoldenRatio + TribonacciConstant").as_sympy()
    assert constants == sp.Catalan + sp.EulerGamma + sp.GoldenRatio + sp.TribonacciConstant
    assert not constants.free_symbols
    assert _quiet(_formula("GoldenRatio").find_value_at) == pytest.approx((1 + math.sqrt(5)) / 2, rel=1e-15)
    # handed to the decimal words, a constant is its decimal, not a letter to find
    assert _formula("x - Catalan")._formula_text() == f"x - {float(sp.Catalan)!r}"


def test_piecewise_hyper_and_meijerg_take_their_lists():
    sp, x = _sp()
    piece = _formula("Piecewise((x, x > 0), (0, True))")
    assert piece.as_sympy() == sp.Piecewise((x, x > 0), (0, True))
    assert _quiet(piece.find_value_at, x=-2) == 0 and _quiet(piece.find_value_at, x=3) == 3
    assert _formula("hyper((1, 1), (2,), x)").as_sympy() == sp.hyper((1, 1), (2,), x)
    assert _formula("meijerg(((1,), ()), ((), (0,)), x)").as_sympy() == sp.meijerg(((1,), ()), ((), (0,)), x)
    for bad, said in [("Piecewise((x, x = 0), (0, True))", "equation"),
                      ("Piecewise((x, 0 < x < 1), (0, True))", "one comparison"),
                      ("Piecewise(x, (0, True))", "pairs"), ("hyper(((1,),), (2,), x)", "deep"),
                      ("(x, 1) + x", "not allowed"), ("x > 0", "equation")]:
        with pytest.raises(sdata.SimplydataError, match=said):
            _formula(bad)


@pytest.mark.parametrize("text", ["factorial(5000)", "fibonacci(1001)", "bell(2000)", "harmonic(10**4)",
                                  "partition(abs(-5000))", "subfactorial(1001)"])
def test_counting_functions_keep_the_number_inside_at_most_1000(text):
    with pytest.raises(sdata.SimplydataError, match="bigger than 1000"):
        _formula(text)


def test_counting_functions_are_worked_out_under_the_time_limit(sympy_calls):
    sp, _ = _sp()
    assert _formula("factorial(1000)").as_sympy() == sp.factorial(1000)
    assert "doit" in sympy_calls or any("doit" in c for c in sympy_calls)


def test_formula_name_table_is_complete_and_has_no_name_twice():
    import sympy as sp

    names = [e.name for e in _formula_names.NAMES]
    assert len(names) == len(set(names))
    for entry in _formula_names.NAMES:
        assert callable(getattr(sp, entry.sympy)), entry.name
        assert entry.about and entry.group in _formula_names.GROUP_ORDER
        assert 1 <= entry.fewest <= entry.most
    from simplydata._formula import FREE_NAMES, FUNCTIONS

    assert set(names) <= set(FUNCTIONS) and set(names) <= set(FREE_NAMES)


# ------------------------------------------------------------------------------------------------ help pointers
@pytest.mark.parametrize("typed, word", [
    ("sympy.real_roots", "find_roots(real_only=True)"), ("sp.nroots", "find_roots(exactly=False)"),
    ("sympy.all_roots", "find_roots()"), ("sympy.count_roots", 'find_roots(show="count")'),
    ("sympy.ground_roots", "fractions_only=True"), ("sympy.degree", "find_degree()"),
    ("sympy.total_degree", "find_degree()"), ("sympy.degree_list", 'for_letter=["x", "y"]'),
    ("sympy.div", 'divide_by("x - 1")'), ("sympy.pquo", "without_fractions=True"), ("sympy.exquo", "with_no_remainder"),
    ("sympy.gcd", "find_common_factor_with"), ("sympy.gcdex", 'show="combination"'),
    ("sympy.lcm_list", "find_common_multiple_with"), ("sympy.together", "turn_into_one_fraction()"),
    ("sympy.fraction", "split_into_top_and_bottom()"), ("sympy.numer", "split_into_top_and_bottom()"),
    ("sympy.cse", "find_repeated_parts()"), ("sympy.discriminant", 'find_fact("discriminant")'),
    ("sympy.groebner", 'find_fact("groebner basis"'), ("sympy.minpoly", 'find_fact("minimal polynomial")'),
    ("sympy.powsimp", 'make_simpler(by="powers")'), ("sympy.trigsimp", 'make_simpler(by="trig functions")'),
    ("sympy.expand_log", 'turn_into_sum(by="logs")'), ("sympy.horner", 'turn_into_product(by="nested")'),
    ("sympy.factor_terms", 'turn_into_product(by="common factors")'), ("sympy.fibonacci", "fibonacci("),
    ("sympy.Piecewise", "Piecewise((x, x > 0), (0, True))"), ("sympy.Catalan", "Catalan"),
    ("sympy.FiniteSet", "as_sympy() hands"), ("sympy.Point", "as_sympy() hands"), ("sympy.And", "as_sympy() hands"),
    ("sympy.tensorproduct", "as_sympy() hands"), ("sympy.Quaternion", "as_sympy() hands"),
    ("sympy.ZZ", "as_sympy() hands"), ("sympy.PolificationFailed", "as_sympy() hands"),
])
def test_sympy_names_point_to_their_word(typed, word, capsys):
    sdata.help(typed)
    printed = capsys.readouterr().out
    assert word in printed, printed


def test_every_sympy_name_of_these_batches_has_a_pointer(capsys):
    from simplydata._other_names import OTHER_NAMES

    names = OTHER_NAMES["sympy"]
    for entry in _formula_names.NAMES:
        if entry.name not in ("ceil",):  # ceil is a spelling of ceiling, not a SymPy name
            assert entry.name in names, entry.name
    for value in (*_formula_algebra.SIMPLER.values(), *_formula_algebra.SUM.values(),
                  *_formula_algebra.PRODUCT.values()):
        assert value[0] in names, value[0]
    for name, (function, *_) in _formula_algebra.FACTS.items():
        assert function.split(".")[-1].replace("all_coeffs", "Poly") in names or function in names, function


def test_many_values_of_a_function_numpy_lacks_are_worked_out_by_sympy_value_by_value(sympy_calls):
    import sympy as sp

    found = _quiet(_formula("fibonacci(n) + lerchphi(1/2, 2, n)").find_value_at, n=[1, 2, 3])
    expected = [float(sp.fibonacci(k) + sp.lerchphi(sp.Rational(1, 2), 2, k)) for k in (1, 2, 3)]
    assert found.as_numpy().tolist() == pytest.approx(expected, rel=1e-14)
    assert sympy_calls.count("evalf") >= 3  # each value by SymPy evalf, under the time limit
    poles = _quiet(_formula("dirichlet_eta(s)").find_value_at, s=[1, 2])
    assert poles.as_numpy()[1] == pytest.approx(float(sp.dirichlet_eta(2)), rel=1e-14)


def test_a_counting_function_that_takes_whole_numbers_only_refuses_a_letter():
    with pytest.raises(sdata.SimplydataError, match="takes whole numbers here, not letters"):
        _formula("motzkin(n)")
    import sympy as sp

    assert _quiet(_formula("motzkin(10)").find_value_at) == float(sp.motzkin(10))


# ------------------------------------------------------------------------------------------------ review fixes
def test_many_values_of_a_whole_number_function_are_its_values_at_whole_numbers():
    import sympy as sp

    for text, values in [("totient(n)", [36, 12, 7]), ("partition(n)", [5, 10]), ("mobius(n)", [30, 4, 7]),
                         ("lucas(n) + subfactorial(n)", [3, 6]), ("legendre_symbol(n, 7)", [2, 3])]:
        found = _quiet(_formula(text).find_value_at, n=values).as_numpy().tolist()
        n = sp.Symbol("n")
        expected = [float(_formula(text).as_sympy().subs(n, v)) for v in values]
        assert found == expected, text


def test_factorial_at_several_values_is_the_same_as_at_one_value():
    found = _quiet(_formula("factorial(x)").find_value_at, x=[-0.5, -1, 2]).as_numpy()
    one = _quiet(_formula("factorial(x)").find_value_at, x=-0.5)
    assert found[0] == pytest.approx(math.gamma(0.5), rel=1e-14) == pytest.approx(one, rel=1e-14)
    assert math.isnan(found[1]) and found[2] == 2.0


def test_put_in_keeps_the_rule_for_counting_functions():
    with pytest.raises(sdata.SimplydataError, match="bigger than 1000"):
        _quiet(_formula("factorial(n)").put_in, n=100000)


def test_a_fact_too_big_for_a_decimal_comes_back_exactly():
    sp, x = _sp()
    found = _quiet(_formula("x**300 - 999**100").find_fact, "discriminant")
    assert hasattr(found, "as_sympy") and found.as_sympy() == sp.discriminant(x ** 300 - sp.Integer(999) ** 100)


def test_piecewise_takes_at_most_and_at_least_conditions():
    sp, x = _sp()
    found = _formula("Piecewise((x, x <= 1), (1, x >= 1))").as_sympy()
    assert found == sp.Piecewise((x, x <= 1), (1, x >= 1))
    with pytest.raises(sdata.SimplydataError, match="equation"):
        _formula("Piecewise((x, x <= 1), (0, True)) = 2")


def test_factorial_factors_keep_the_number_in_front_and_print_falling_factorials():
    sp, x = _sp()
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        found = _formula("2*x**3 - 2*x").find_fact("factorial factors")
    rows = _column(found, "factor")
    assert rows[0] == str(sp.LC(2 * x ** 3 - 2 * x)) == "2"
    assert rows[1:] == [f"ff({g}, {k})" for g, k in sp.gff_list(2 * x ** 3 - 2 * x)]
    product = sp.LC(2 * x ** 3 - 2 * x) * sp.Mul(*[sp.ff(g, k) for g, k in sp.gff_list(2 * x ** 3 - 2 * x)])
    assert sp.expand(product) == 2 * x ** 3 - 2 * x
    assert "ff(" in printed.getvalue() and "**" not in printed.getvalue().split(":")[-1]


@pytest.mark.parametrize("text, by", [("2*x + 4*y", None), ("2*x + 4*y", "common factors")])
def test_a_number_times_a_sum_stays_a_product_after_the_time_limit_helper(text, by):
    sp, _ = _sp()
    x, y = sp.symbols("x y")
    formula = _formula(text)
    _quiet(formula.turn_into_product, **({} if by is None else {"by": by}))
    assert str(formula) == str(sp.factor(2 * x + 4 * y)) == "2*(x + 2*y)"


@pytest.mark.parametrize("call, said", [
    (lambda: _formula("x**7 - x - 1").find_fact("galois group"), "degree 1 to 6"),
    (lambda: _formula("jacobi_symbol(2, n)").find_value_at(n=36), "no value"),
    (lambda: _formula("legendre_symbol(2, 9)"), "no value of legendre_symbol"),
    (lambda: _formula("chebyshevt_root(3, 7)"), "no value of chebyshevt_root"),
])
def test_sympys_value_errors_are_plain_sentences(call, said):
    with pytest.raises(sdata.SimplydataError, match=said):
        _quiet(call)


def test_viete_formulas_use_the_letter_asked_for():
    sp, _ = _sp()
    a, x = sp.symbols("a x")
    found = _quiet(_formula("x**2 - a*x + 1").find_fact, "viete formulas", for_letter="x")
    assert found == [f"{l} = {r}" for l, r in sp.viete(x ** 2 - a * x + 1, None, x)]
    with pytest.raises(sdata.SimplydataError, match="for_letter="):
        _quiet(_formula("x**2 - a*x + 1").find_fact, "viete formulas")


def test_value_by_value_has_one_deadline_and_says_its_method_once(capsys):
    from simplydata import _formula_names

    assert hasattr(_formula_names.value_by_value, "__wrapped__")  # one_deadline
    _formula("fibonacci(n)").find_value_at(n=[1, 2])
    printed = capsys.readouterr().out
    assert "value by value" in printed and "lambdify" not in printed


def test_small_review_fixes():
    sp, x = _sp()
    with pytest.raises(sdata.SimplydataError, match="no simple ratio"):
        _quiet(_formula("2**(k**2)").find_fact, "term ratio")
    with pytest.raises(sdata.SimplydataError, match="smaller value first"):
        _quiet(_formula("x**2 - 1").find_roots, between=[3, -3])
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        _formula("x**2 + a*x").divide_by("x + a")
    assert "in a, x, in that order" in printed.getvalue()
    assert "-p/2 to p/2" in _formula_algebra.FACTS["coefficients modulo"][3]
    with pytest.raises(sdata.SimplydataError, match="no decimal for mathieuc"):
        _quiet(_formula("mathieuc(1, 1, x)").find_value_at, x=[0.5, 1.0])
    sdata.help("sympy.piecewise_exclusive")


# regression of the review fix 7: only the product words keep SymPy's form; every other answer is fully worked out
def test_values_after_the_helper_are_exact_where_they_should_be():
    sp, x = _sp()
    assert _quiet(_formula("x**2 - 4").find_value_at, x=2) == 0.0  # exactly 0 at a root
    assert _quiet(_formula("2 - a/3").find_value_at, a=6) == 0.0
    expanded = _formula("(x + 2)**2 - 4")
    _quiet(expanded.turn_into_sum)
    assert _quiet(expanded.find_value_at, x=-4) == 0.0
    slope = _quiet(_formula("x**3 - 12*x").find_slope_formula)
    assert _quiet(slope.find_value_at, x=2) == 0.0
    assert _quiet(_formula("sin(x) / x").find_limit_as, "x", goes_to=0) == 1.0
    answer = _quiet(sdata.solve, "x**2 = 4", exactly=True)
    assert sorted(_column(answer, "x")) == [-2.0, 2.0]
    product = _formula("2*x + 4*y")
    _quiet(product.turn_into_product)
    assert str(product) == "2*(x + 2*y)" and _quiet(product.find_value_at, x=-4, y=2) == 0.0
