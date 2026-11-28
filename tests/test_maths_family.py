"""The maths family (families for 100 %, batches 7-9, plan section 2.3, approved by Manish 2026-11-28).

One name table (_maths_functions.py) serves numbers.take_function and formula text. Every name is checked against its
library (scipy.special or NumPy) called directly on the same numbers, with negative numbers and 0 among them: where
the library has no value the answer is empty, where it is infinite it is inf, and a function whose answers are
complex numbers gives their real part (or part=). Each formula name is checked inside table.add_column and, where
SymPy has the function, inside sdata.formula. find_zeros_of, find_area_points, work_on_bits and
turn_into_yes_or_no(is_=) are checked against SciPy and NumPy. These tests fail on the code before this batch:
take_function, work_on_bits, find_zeros_of, find_area_points, is_= and the formula names did not exist.
"""

import math

import numpy as np
import pytest
from scipy import integrate, special

import simplydata as sdata
from simplydata import _maths_functions as family
from simplydata._special_points import AREA_RULES, ZEROS

TABLE = family.TABLE


def _options(entry):
    """The sample options of an entry; a characteristic value is worked out by SciPy's pro_cv / obl_cv."""
    options = {k: v for k, v in entry.sample.items() if v is not None}
    if "characteristic_value" in entry.inputs:
        kind = "pro" if entry.library_name.startswith("pro") else "obl"
        options["characteristic_value"] = float(getattr(special, f"{kind}_cv")(options["order"], options["degree"],
                                                                                 options["c"]))
    return options


def _element(function, *arrays):
    """function of single numbers, number by number (plain Python loops, independent of the table's own code)."""
    shape = np.broadcast_shapes(*[np.shape(a) for a in arrays])
    flat = [np.broadcast_to(np.asarray(a), shape).ravel() for a in arrays]
    out = []
    for values in zip(*flat):
        try:
            out.append(function(*values))
        except (ValueError, TypeError, IndexError):
            out.append(np.nan)
    return np.asarray(out).reshape(shape)


def _whole_ok(k):
    return k >= 0 and float(k).is_integer()


# The expected answer of the entries the library does not work out with one call on the arrays: worked out here
# from SciPy and NumPy (or mpmath, SymPy's own decimal maths, for the incomplete gammas) in plain loops.
def _mp_gamma(a, x, upper):
    import mpmath

    if x < 0:
        return np.nan
    return float(mpmath.gammainc(a, x, mpmath.inf) if upper else mpmath.gammainc(a, 0, x))


EXPECTED = {
    "mantissa": lambda x, o: np.frexp(x)[0],
    "exponent of two": lambda x, o: np.frexp(x)[1],
    "division rounded down": lambda x, o: np.floor_divide(x, o["divisor"]),
    "double factorial": lambda x, o: _element(lambda n: special.factorial2(int(n), exact=False), x),
    "multifactorial": lambda x, o: _element(lambda n: special.factorialk(int(n), o["k"], exact=False), x),
    "stirling number of the second kind": lambda x, o: _element(lambda n: special.stirling2(int(n), o["k"],
                                                                                            exact=False), x),
    "bernoulli number": lambda x, o: _element(lambda n: special.bernoulli(int(n))[int(n)], x),
    "euler number": lambda x, o: _element(lambda n: special.euler(int(n))[int(n)], x),
    "lower incomplete gamma": lambda x, o: _element(lambda v: _mp_gamma(o["a"], v, False), x),
    "upper incomplete gamma": lambda x, o: _element(lambda v: _mp_gamma(o["a"], v, True), x),
    "log of multivariate gamma": lambda x, o: _element(lambda v: special.multigammaln(v, o["dimension"]), x),
    "riccati bessel first kind": lambda x, o: _element(lambda v: special.riccati_jn(o["order"], v)[0][o["order"]], x),
    "riccati bessel first kind slope": lambda x, o: _element(lambda v: special.riccati_jn(o["order"], v)[1][o["order"]],
                                                             x),
    "riccati bessel second kind": lambda x, o: _element(lambda v: special.riccati_yn(o["order"], v)[0][o["order"]], x),
    "riccati bessel second kind slope": lambda x, o: _element(
        lambda v: special.riccati_yn(o["order"], v)[1][o["order"]], x),
    "jahnke emde lambda": lambda x, o: _element(lambda v: special.lmbda(o["order"], v)[0][-1], x),
    "jahnke emde lambda slope": lambda x, o: _element(lambda v: special.lmbda(o["order"], v)[1][-1], x),
    "legendre Q": lambda x, o: _element(lambda v: special.lqn(o["degree"], v)[0][o["degree"]], x),
    "legendre Q slope": lambda x, o: _element(lambda v: special.lqn(o["degree"], v)[1][o["degree"]], x),
    "associated legendre Q": lambda x, o: _element(
        lambda v: special.lqmn(o["order"], o["degree"], v)[0][o["order"], o["degree"]], x),
    "mathieu even coefficient": lambda x, o: _element(
        lambda q: special.mathieu_even_coef(o["order"], q)[o["which"]], x),
    "mathieu odd coefficient": lambda x, o: _element(lambda q: special.mathieu_odd_coef(o["order"], q)[o["which"]], x),
    "ellipsoidal harmonic E": lambda x, o: _element(lambda s: special.ellip_harm(o["h_squared"], o["k_squared"],
                                                                                 o["degree"], o["order"], s), x),
    "ellipsoidal harmonic F": lambda x, o: _element(lambda s: special.ellip_harm_2(o["h_squared"], o["k_squared"],
                                                                                   o["degree"], o["order"], s), x),
    "ellipsoidal harmonic normalization": lambda x, o: _element(lambda h: special.ellip_normal(h, o["k_squared"],
                                                                                               o["degree"],
                                                                                               o["order"]), x),
    "dirichlet kernel": lambda x, o: _element(lambda v: special.diric(v, o["n"]), x),
    "softplus": lambda x, o: np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0),
    "softmax": lambda x, o: np.exp(x) / np.exp(x).sum(),
    "log of softmax": lambda x, o: x - np.log(np.exp(x).sum()),
    "lambert W": lambda x, o: np.real(special.lambertw(x, 0)),
    "zeta": lambda x, o: special.zeta(x),
    "spence": lambda x, o: special.spence(x),
    "shifted jacobi polynomial": lambda x, o: special.eval_sh_jacobi(o["degree"], o["p"], o["q"], x),
    "associated legendre polynomial": lambda x, o: _element(
        lambda z: np.asarray(special.assoc_legendre_p(o["degree"], o["order"], z)).ravel()[0], x),
    "spherical legendre polynomial": lambda x, o: _element(
        lambda t: np.asarray(special.sph_legendre_p(o["degree"], o["order"], t)).ravel()[0], x),
    "spherical harmonic": lambda x, o: _element(
        lambda t: np.real(np.asarray(special.sph_harm_y(o["degree"], o["order"], t, o["phi"])).ravel()[0]), x),
}
# below 0 Ci and Chi are complex numbers: empty (SciPy itself gives the real part); Li2 is SciPy spence(1 - x) up to 1
EXPECTED["cosine integral"] = lambda x, o: np.where(x < 0, np.nan, special.sici(x)[1])
EXPECTED["hyperbolic cosine integral"] = lambda x, o: np.where(x < 0, np.nan, special.shichi(x)[1])
EXPECTED["polylogarithm"] = lambda x, o: np.where(x > 1, np.nan, special.spence(1 - x))
for _plain, (_name, _slope) in {"spherical bessel j": ("spherical_jn", False),
                                "spherical bessel j slope": ("spherical_jn", True),
                                "spherical bessel y": ("spherical_yn", False),
                                "spherical bessel y slope": ("spherical_yn", True),
                                "modified spherical bessel i": ("spherical_in", False),
                                "modified spherical bessel i slope": ("spherical_in", True),
                                "modified spherical bessel k": ("spherical_kn", False),
                                "modified spherical bessel k slope": ("spherical_kn", True)}.items():
    EXPECTED[_plain] = (lambda name, slope: lambda x, o: getattr(special, name)(o["order"], x, derivative=slope))(
        _name, _slope)


def _library_answer(entry, numbers, options):
    """What the library itself gives for these numbers and options."""
    if entry.plain in EXPECTED:
        return np.asarray(EXPECTED[entry.plain](numbers, options))
    assert entry.compute is None, f"{entry.plain}: worked out by the table's own code, so it needs an EXPECTED"
    module = special if entry.namespace == "special" else np
    args = []
    for key in entry.inputs:
        value = numbers if key == "x" else options.get(key, entry.defaults.get(key))
        if key in entry.whole and value is not None:
            value = np.asarray(value).astype(np.int64)
        args.append(value)
    with np.errstate(all="ignore"):
        out = getattr(module, entry.library_name)(*args)
    if entry.part is not None:
        out = out[entry.part]
    out = np.asarray(out)
    return np.real(out) if out.dtype.kind == "c" else out


def _same(found, expected, plain):
    found, expected = np.asarray(found), np.asarray(expected)
    assert found.shape == expected.shape, plain
    if expected.dtype.kind == "b":
        assert found.dtype.kind == "b" and np.array_equal(found, expected), plain
        return
    np.testing.assert_allclose(found.astype(float), expected.astype(float), rtol=1e-12, atol=1e-300,
                               equal_nan=True, err_msg=plain)


# ---------------------------------------------------------------- one test per name: take_function = the library
@pytest.mark.parametrize("entry", TABLE, ids=[e.plain for e in TABLE])
def test_every_maths_function_gives_what_its_library_gives(entry):
    numbers = np.asarray(entry.numbers, dtype=float)
    options = _options(entry)
    values = sdata.number_list(list(numbers))
    values.take_function(entry.plain, **options)
    _same(values.as_numpy(), _library_answer(entry, numbers, options), entry.plain)


@pytest.mark.parametrize("entry", TABLE, ids=[e.plain for e in TABLE])
def test_every_name_of_a_function_finds_it(entry):
    names = [entry.plain, entry.formula_name, entry.plain.upper(), *entry.names]
    if entry.library_is_name and entry.library_name not in family.SEVERAL_PARTS and \
            entry.library_name not in family.RUNS:
        head = "special." if entry.namespace == "special" else "np."
        names += [entry.library_name, head + entry.library_name]
        if entry.namespace == "special":
            names.append("scipy.special." + entry.library_name)
    for name in names:
        assert family.find(name) is entry, name


@pytest.mark.parametrize("entry", [e for e in TABLE if e.also], ids=[e.plain for e in TABLE if e.also])
def test_the_other_library_with_the_same_name_agrees(entry):
    numbers = np.asarray(entry.numbers, dtype=float)
    for other in entry.also:
        module = special if other.startswith("special.") else np
        _same(getattr(module, other.split(".", 1)[1])(numbers), _library_answer(entry, numbers, {}), other)


def test_the_table_reaches_every_scipy_special_elementwise_function_of_section_2_3():
    """All the ufuncs of scipy.special are reachable (by take_function, or by the existing words that have a
    pointer), except the distribution functions that plan section 2.2 gives to the distribution words."""
    from simplydata._other_names import OTHER_NAMES

    pointed = set(OTHER_NAMES["special"])  # the names an existing word already does (cbrt, expit, logit ...)
    covered = ({n for n in dir(special) if family.find(n) is not None} | set(family.SEVERAL_PARTS)
               | set(family.RUNS) | pointed)
    distribution_functions = {n for n in dir(special) if "dtr" in n} | {
        "kolmogi", "kolmogorov", "smirnov", "smirnovi", "owens_t", "tklmbda", "nrdtrimn", "nrdtrisd"}
    open_names = [n for n in dir(special) if isinstance(getattr(special, n), np.ufunc) and not n.startswith("_")
                  and n not in covered and n not in distribution_functions]
    assert open_names == [], open_names


def test_the_numpy_elementwise_functions_of_section_2_3_are_reachable():
    names = ("acos acosh arccos arccosh arcsin arcsinh arctan arctan2 arctanh asin asinh atan atan2 atanh conj "
             "conjugate copysign cosh exp2 expm1 fmod frexp gcd heaviside hypot lcm ldexp log1p logaddexp logaddexp2 "
             "mod nextafter positive reciprocal remainder sign signbit sinh spacing tanh angle real imag i0 "
             "sinc").split()
    open_names = [n for n in names + ["divmod"] if family.find(n) is None and n not in family.SEVERAL_PARTS]
    assert open_names == [], open_names


# ---------------------------------------------------------------- what happens at the edges
def test_no_value_gives_empty_answers_with_a_note(capsys):
    values = sdata.number_list([-2.0, 0.0, 0.5, 2.0])
    values.take_function("inverse error function")
    shown = capsys.readouterr().out
    assert "2 numbers are now empty" in shown and "from -1 to 1" in shown and "special.erfinv(numbers)" in shown
    assert np.isnan(values.as_numpy()[[0, 3]]).all()
    values.undo()
    assert values.as_numpy().tolist() == [-2.0, 0.0, 0.5, 2.0]


def test_an_infinite_answer_is_inf_with_a_note(capsys):
    values = sdata.number_list([0.0, 1.0])
    values.take_function("bessel Y0")
    shown = capsys.readouterr().out
    assert "1 answer is infinite" in shown
    assert values.as_numpy()[0] == -np.inf


def test_a_complex_answer_gives_its_real_part_or_the_part_asked_for(capsys):
    x = np.array([0.5, 1.0, 2.0])
    for part, expected in (("real", np.real), ("imaginary", np.imag), ("size", np.abs), ("angle", np.angle)):
        values = sdata.number_list(list(x))
        values.take_function("hankel H1", order=1, part=part)
        np.testing.assert_allclose(values.as_numpy(), expected(special.hankel1(1, x)), rtol=1e-14)
    assert "complex numbers" in capsys.readouterr().out
    with pytest.raises(sdata.SimplydataError, match="part= is for functions whose answers are complex"):
        sdata.number_list([1.0]).take_function("bessel J", order=1, part="imaginary")
    values = sdata.number_list([-1.0, 1.0])  # Lambert W below -1/e is complex: its real part, said plainly
    values.take_function("lambert W")
    assert "complex numbers" in capsys.readouterr().out
    np.testing.assert_allclose(values.as_numpy(), np.real(special.lambertw([-1.0, 1.0])))


def test_a_whole_number_input_that_is_not_whole_gives_an_empty_answer():
    values = sdata.number_list([4.0, 4.5, 6.0])
    values.take_function("greatest common divisor", other=6)
    found = values.as_numpy()
    assert found[0] == 2 and np.isnan(found[1]) and found[2] == 6


def test_options_can_be_numbers_of_the_same_shape_and_grids_keep_their_shape():
    values = sdata.number_list([1.0, 2.0, 3.0])
    values.take_function("bessel J", order=sdata.number_list([0, 1, 2]))
    np.testing.assert_allclose(values.as_numpy(), special.jv([0, 1, 2], [1.0, 2.0, 3.0]), rtol=1e-15)
    grid = sdata.number_grid([[0.5, 1.0], [1.5, 2.0]])
    grid.take_function("erfinv")
    assert grid.as_numpy().shape == (2, 2)
    with pytest.raises(sdata.SimplydataError, match="do not line up"):
        sdata.number_list([1.0, 2.0, 3.0]).take_function("bessel J", order=[1, 2])


def test_plain_sentences_for_mistakes():
    values = sdata.number_list([1.0])
    with pytest.raises(sdata.SimplydataError, match='needs order='):
        values.take_function("bessel J")
    with pytest.raises(sdata.SimplydataError, match="does not take degree="):
        values.take_function("bessel J", order=1, degree=2)
    with pytest.raises(sdata.SimplydataError, match='Did you mean "bessel j"'):
        values.take_function("besel j")
    with pytest.raises(sdata.SimplydataError, match='"airy Ai", "airy Ai slope", "airy Bi", "airy Bi slope"'):
        values.take_function("airy")
    with pytest.raises(sdata.SimplydataError, match="in quotes"):
        values.take_function(3)


def test_no_name_lists_every_function_group_by_group(capsys):
    assert sdata.number_list([1.0]).take_function() is None
    shown = capsys.readouterr().out
    for entry in TABLE:
        assert f'"{entry.plain}"' in " ".join(shown.split()), entry.plain
    for group in family.GROUP_ORDER:
        assert group[1:] in shown


@pytest.mark.parametrize("name", sorted(family.SEVERAL_PARTS))
def test_a_library_name_of_several_answers_names_each_part(name):
    for plain in family.SEVERAL_PARTS[name]:
        assert plain in family.BY_PLAIN, plain
    with pytest.raises(sdata.SimplydataError, match="answers at once"):
        sdata.number_list([1.0]).take_function(name)


RUN_CHECKS = {
    "legendre_p": ({"degree": 2}, lambda x: np.asarray(special.legendre_p(2, x))[0]),
    "legendre_p_all": ({"degree": 2}, lambda x: np.asarray(special.legendre_p_all(2, x))[0, 2]),
    "assoc_legendre_p_all": ({"degree": 2, "order": 1},
                             lambda x: _element(lambda z: np.asarray(special.assoc_legendre_p_all(2, 1, z))[0, 2, 1],
                                                x)),
    "sph_legendre_p_all": ({"degree": 2, "order": 1},
                           lambda x: _element(lambda t: np.asarray(special.sph_legendre_p_all(2, 1, t))[0, 2, 1], x)),
    "sph_harm_y_all": ({"degree": 2, "order": 1, "phi": 0.3},
                       lambda x: _element(lambda t: np.real(np.asarray(special.sph_harm_y_all(2, 1, t, 0.3))[2, 1]),
                                          x)),
    "assoc_laguerre": ({"degree": 3, "alpha": 1.5}, lambda x: special.assoc_laguerre(x, 3, 1.5)),
    "lqmn": ({"order": 1, "degree": 2}, lambda x: _element(lambda z: special.lqmn(1, 2, z)[0][1, 2], x)),
    "pbdn_seq": ({"order": 2}, lambda x: _element(lambda z: np.real(special.pbdn_seq(2, z)[0][2]), x)),
    "pbdv_seq": ({"order": 2}, lambda x: _element(lambda z: special.pbdv_seq(2, z)[0][-1], x)),
    "pbvv_seq": ({"order": 2}, lambda x: _element(lambda z: special.pbvv_seq(2, z)[0][-1], x)),
    "pro_cv_seq": ({"order": 0, "degree": 2}, lambda x: _element(lambda c: special.pro_cv_seq(0, 2, c)[-1], x)),
    "obl_cv_seq": ({"order": 0, "degree": 2}, lambda x: _element(lambda c: special.obl_cv_seq(0, 2, c)[-1], x)),
}


@pytest.mark.parametrize("name", sorted({*family.RUNS, "assoc_laguerre"}))
def test_a_library_name_that_gives_a_whole_run_gives_the_one_asked_for(name, capsys):
    if name == "logsumexp":
        values = sdata.number_list([0.5, 2.0])
        values.take_function(name, other=1.0)
        np.testing.assert_allclose(values.as_numpy(), [special.logsumexp([0.5, 1.0]), special.logsumexp([2.0, 1.0])])
        return
    options, expected = RUN_CHECKS[name]
    x = np.array([0.2, 0.5, 0.75]) if "cv" not in name else np.array([0.5, 1.0, 2.0])
    values = sdata.number_list(list(x))
    values.take_function(name, **options)
    assert ("gives" in capsys.readouterr().out) == (name in family.RUNS)  # assoc_laguerre is a name of its own
    np.testing.assert_allclose(values.as_numpy(), expected(x), rtol=1e-10, equal_nan=True)


def test_names_are_unique_and_formula_names_are_identifiers():
    assert len({e.plain for e in TABLE}) == len(TABLE)
    for name, spec in family.FORMULA_NAMES.items():
        assert name.isidentifier() and spec.entry.formula, name


# ---------------------------------------------------------------- the same names inside formula text
FORMULA_ENTRIES = [e for e in TABLE if e.formula]


def _formula_points(entry):
    numbers = np.asarray(entry.numbers, dtype=float)
    options = _options(entry)
    expected = _library_answer(entry, numbers, options)
    keep = np.isfinite(expected)
    if entry.complex_answer:  # formula text keeps to real numbers: only where the library's answer is real
        whole = np.asarray(entry.library_function()(numbers, *[options.get(k, entry.defaults.get(k))
                                                                for k in entry.options]))
        keep &= np.abs(np.imag(whole)) == 0
    return numbers[keep], options, expected[keep]


def _call(name, order, options, letter="x"):
    shown = [letter if k == "x" else repr(float(options[k])) for k in order if k in options or k == "x"]
    return f"{name}({', '.join(shown)})"


@pytest.mark.parametrize("entry", FORMULA_ENTRIES, ids=[e.plain for e in FORMULA_ENTRIES])
def test_every_formula_name_works_in_add_column(entry):
    x, options, expected = _formula_points(entry)
    if entry.yes_no or not x.size:
        pytest.skip("no finite sample")
    table = sdata.table({"x": x.tolist()})
    table.add_column("y", _call(entry.formula_name, entry.inputs, options))
    _same(np.asarray(table.get_column("y").as_numpy(), dtype=float), expected.astype(float), entry.plain)


SYMPY_ENTRIES = [e for e in FORMULA_ENTRIES if e.sympy or e.sympy_expr]


@pytest.mark.parametrize("entry", FORMULA_ENTRIES, ids=[e.plain for e in FORMULA_ENTRIES])
def test_every_formula_name_works_in_sdata_formula(entry):
    """SymPy's own function where SymPy has it (a SymPy expression), else a function SymPy keeps by name and SciPy
    works out; either way the numbers are the library's."""
    pytest.importorskip("sympy")
    x, options, expected = _formula_points(entry)
    x, expected = x[x > 0], expected[x > 0]  # SymPy's branches agree with SciPy's above 0
    if not x.size:
        pytest.skip("no sample above 0")
    formula = sdata.formula(_call(entry.formula_name, entry.inputs, options))
    found = formula.find_value_at(x=x.tolist())
    np.testing.assert_allclose(found.as_numpy(), expected, rtol=1e-9, atol=1e-12, err_msg=entry.plain)


@pytest.mark.parametrize("entry", [e for e in SYMPY_ENTRIES if e.sympy],
                         ids=[e.plain for e in SYMPY_ENTRIES if e.sympy])
def test_sympys_own_name_works_in_formula_text_in_sympys_order(entry):
    pytest.importorskip("sympy")
    from simplydata._formula import formula_text, parse

    head, order = family._sympy_parts(entry.sympy)
    x, options, expected = _formula_points(entry)
    x, expected = x[x > 0], expected[x > 0]
    if not x.size or head in family._TAKEN:
        pytest.skip("no sample above 0, or the name means something else in formula text")
    text = _call(head, [k for k in order if k == "x" or k in options], options)
    found = sdata.formula(text).find_value_at(x=x.tolist())
    np.testing.assert_allclose(found.as_numpy(), expected, rtol=1e-9, err_msg=text)
    table = sdata.table({"x": x.tolist()})  # and in add_column, worked out by SciPy
    table.add_column("y", text)
    np.testing.assert_allclose(np.asarray(table.get_column("y").as_numpy(), dtype=float), expected, rtol=1e-12)
    again = sdata.formula(formula_text(parse(text)))  # written back as formula text, it reads the same
    np.testing.assert_allclose(again.find_value_at(x=x.tolist()).as_numpy(), expected, rtol=1e-9, err_msg=text)


def test_a_formula_keeps_sympys_function_so_slopes_work():
    pytest.importorskip("sympy")
    slope = sdata.formula("besseli(0, x)").find_slope_formula()
    assert abs(slope.find_value_at(x=1.0) - special.iv(1, 1.0)) < 1e-12
    hyper = sdata.formula("hyp1f1(0.5, 1.5, x)")
    assert "hyp1f1" in hyper._formula_text()
    assert abs(hyper.find_value_at(x=0.7) - special.hyp1f1(0.5, 1.5, 0.7)) < 1e-12


def test_a_function_sympy_does_not_have_is_kept_by_name_and_worked_out_by_scipy():
    pytest.importorskip("sympy")
    formula = sdata.formula("struve_h(0, x) * 2")
    assert "struve_h(0, x)" in formula._formula_text()
    assert abs(formula.find_value_at(x=1.5) - 2 * special.struve(0, 1.5)) < 1e-12
    np.testing.assert_allclose(formula.find_value_at(x=[0.5, 1.5]).as_numpy(), 2 * special.struve(0, [0.5, 1.5]))


def test_sympys_spherical_jn_is_written_back_by_its_plain_name():
    pytest.importorskip("sympy")
    from simplydata._formula import formula_text, parse

    assert formula_text(parse("spherical_bessel_j(1, x)")) == "spherical_bessel_j(1, x)"
    assert abs(sdata.formula("jn(1, x)").find_value_at(x=2.0) - special.jv(1, 2.0)) < 1e-12  # SciPy's jn


def test_names_without_brackets_stay_columns_and_values_to_find():
    """y0, k1 and agm were letters, columns and values to find before this batch, and still are."""
    table = sdata.table({"y0": [1.0, 2.0], "k1": [3.0, 4.0]})
    table.add_column("total", "y0 + k1 + bessel_y0(k1)")
    np.testing.assert_allclose(table.get_column("total").as_numpy(), [1 + 3 + special.y0(3.0), 2 + 4 + special.y0(4.0)])
    data = sdata.table({"t": [0.0, 1.0, 2.0, 3.0], "level": [5.0, 7.0, 9.0, 11.0]})
    found = data.fit_formula("level = y0 + agm * t").as_pandas().iloc[0]
    assert abs(found["y0"] - 5) < 1e-6 and abs(found["agm"] - 2) < 1e-6
    pytest.importorskip("sympy")
    assert sdata.formula("y0 * 2").find_value_at(y0=3) == 6


def test_the_maths_reader_finds_the_smallest_value_of_a_family_function():
    result = sdata.find_where_smallest("bessel_j(0, x)", between=[2, 5])
    assert abs(result.as_pandas()["x"].iloc[0] - special.jn_zeros(1, 1)[0]) < 1e-5


# ---------------------------------------------------------------- zeros and area points
ZERO_CASES = [p for p in ZEROS if p != "bessel J and J slope of every order"]


@pytest.mark.parametrize("plain", ZERO_CASES)
def test_find_zeros_of_gives_scipys_zeros(plain):
    function_name, uses_order, which, is_complex = ZEROS[plain]
    function = getattr(special, function_name)
    expected = function(2, 4) if uses_order else function(4)
    if which is not None:
        expected = expected[which]
    found = sdata.find_zeros_of(plain, how_many=4, **({"order": 2} if uses_order else {}))
    if is_complex:
        frame = found.as_pandas()
        np.testing.assert_allclose(frame["real part"] + 1j * frame["imaginary part"], expected, rtol=1e-15)
    else:
        np.testing.assert_allclose(found.as_numpy(), np.real(expected), rtol=1e-15)
    assert sdata.find_zeros_of(function_name if which is None else plain, how_many=4,
                               **({"order": 2} if uses_order else {})) is not None


def test_find_zeros_of_every_order_together_and_the_names_that_give_several():
    frame = sdata.find_zeros_of("jnjnp_zeros", how_many=6).as_pandas()
    zeros, orders, numbers, kinds = special.jnjnp_zeros(6)
    np.testing.assert_allclose(frame["zero"], zeros)
    assert frame["order"].tolist() == list(orders) and frame["number"].tolist() == list(numbers)
    assert frame["function"].tolist() == ["bessel J" if k == 0 else "bessel J slope" for k in kinds]
    j, jp, y, yp = special.jnyn_zeros(1, 3)
    for plain, expected in zip(("bessel J", "bessel J slope", "bessel Y", "bessel Y slope"), (j, jp, y, yp)):
        np.testing.assert_allclose(sdata.find_zeros_of(plain, order=1, how_many=3).as_numpy(), expected, rtol=1e-12)
    np.testing.assert_allclose(sdata.find_zeros_of("jnyn_zeros", how_many=3).as_numpy(), special.jn_zeros(0, 3))
    kelvin = special.kelvin_zeros(3)
    for plain, expected in zip(("kelvin ber", "kelvin bei", "kelvin ker", "kelvin kei", "kelvin ber slope",
                                "kelvin bei slope", "kelvin ker slope", "kelvin kei slope"), kelvin):
        np.testing.assert_allclose(sdata.find_zeros_of(plain, how_many=3).as_numpy(), expected, rtol=1e-12)
    s_zeros, c_zeros = special.fresnel_zeros(2)
    frame = sdata.find_zeros_of("fresnel C", how_many=2).as_pandas()
    np.testing.assert_allclose(frame["real part"] + 1j * frame["imaginary part"], c_zeros, rtol=1e-12)
    with pytest.raises(sdata.SimplydataError, match="has no order"):
        sdata.find_zeros_of("airy Ai", order=1)
    with pytest.raises(sdata.SimplydataError, match="whole number"):
        sdata.find_zeros_of("bessel J", how_many=0)


@pytest.mark.parametrize("plain", [p for p in AREA_RULES if p not in ("newton cotes", "lebedev")])
def test_find_area_points_gives_scipys_points_and_weights(plain):
    function_name, short, needs, _, _ = AREA_RULES[plain]
    sample = {"alpha": 0.5, "beta": 1.5, "p": 2.0, "q": 1.0}
    options = {k: sample[k] for k in needs}
    points, weights = getattr(special, function_name)(5, *options.values())
    for name in (plain, function_name, short):
        frame = sdata.find_area_points(name, how_many=5, **options).as_pandas()
        np.testing.assert_allclose(frame["point"], points, rtol=1e-15)
        np.testing.assert_allclose(frame["weight"], weights, rtol=1e-15)


def test_newton_cotes_and_lebedev_and_an_area_with_formula_words():
    weights, error = integrate.newton_cotes(4, 1)
    frame = sdata.find_area_points("newton cotes", how_many=5).as_pandas()
    np.testing.assert_allclose(frame["weight"], weights)
    points, lebedev = integrate.lebedev_rule(7)
    frame = sdata.find_area_points("lebedev", degree=7).as_pandas()
    np.testing.assert_allclose(frame[["x", "y", "z"]].to_numpy().T, points)
    np.testing.assert_allclose(frame["weight"], lebedev)
    rule = sdata.find_area_points("legendre", how_many=5)
    rule.add_column("value", "weight * exp(point)")
    assert abs(rule.find_total_of("value") - (math.e - 1 / math.e)) < 1e-9  # exact: e - 1/e
    with pytest.raises(sdata.SimplydataError, match="needs alpha= and beta="):
        sdata.find_area_points("jacobi")


# ---------------------------------------------------------------- bits and kinds of numbers
BIT_CASES = [("and", {"with_numbers": 6}, lambda v: np.bitwise_and(v, 6)),
             ("or", {"with_numbers": 6}, lambda v: np.bitwise_or(v, 6)),
             ("only one", {"with_numbers": 6}, lambda v: np.bitwise_xor(v, 6)),
             ("flip", {}, np.invert), ("count ones", {}, np.bitwise_count),
             ("shift left", {"by": 2}, lambda v: np.left_shift(v, 2)),
             ("shift right", {"by": 1}, lambda v: np.right_shift(v, 1))]


@pytest.mark.parametrize("how, options, expected", BIT_CASES, ids=[c[0] for c in BIT_CASES])
def test_work_on_bits_gives_numpys_bits(how, options, expected):
    values = np.array([12, 10, 7, 3, -5])
    numbers = sdata.number_list(values.tolist())
    numbers.work_on_bits(how, **options)
    assert numbers.as_numpy().tolist() == np.asarray(expected(values)).tolist()


def test_work_on_bits_numpys_names_packing_and_mistakes():
    for numpy_name, plain in (("bitwise_and", "and"), ("bitwise_xor", "only one"), ("invert", "flip"),
                              ("bitwise_not", "flip"), ("left_shift", "shift left")):
        a, b = sdata.number_list([12, 10]), sdata.number_list([12, 10])
        extra = {"with_numbers": 6} if plain in ("and", "only one") else {"by": 1} if plain == "shift left" else {}
        a.work_on_bits(numpy_name, **extra)
        b.work_on_bits(plain, **extra)
        assert a.as_numpy().tolist() == b.as_numpy().tolist()
    bits = sdata.number_list([1, 0, 1, 1, 0, 0, 0, 1, 1])
    bits.work_on_bits("pack into bytes")
    assert bits.as_numpy().tolist() == np.packbits(np.array([1, 0, 1, 1, 0, 0, 0, 1, 1], dtype=np.uint8)).tolist()
    bits.work_on_bits("unpack bytes")
    assert bits.as_numpy().tolist() == np.unpackbits(np.packbits(np.array([1, 0, 1, 1, 0, 0, 0, 1, 1],
                                                                           dtype=np.uint8))).tolist()
    grid = sdata.number_grid([[1, 0, 1, 1, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 1, 1]])
    grid.work_on_bits("pack into bytes")
    assert grid.as_numpy().tolist() == [[177], [3]]
    with pytest.raises(sdata.SimplydataError, match="whole numbers"):
        sdata.number_list([1.5, 2.0]).work_on_bits("and", with_numbers=1)
    with pytest.raises(sdata.SimplydataError, match="empty"):
        sdata.number_list([1.0, None]).work_on_bits("flip")
    with pytest.raises(sdata.SimplydataError, match="needs with_numbers="):
        sdata.number_list([1]).work_on_bits("and")
    with pytest.raises(sdata.SimplydataError, match="needs by="):
        sdata.number_list([1]).work_on_bits("shift left")
    with pytest.raises(sdata.SimplydataError, match="does not know"):
        sdata.number_list([1]).work_on_bits("nand")


KINDS = [("finite", np.isfinite), ("infinite", np.isinf), ("minus infinity", np.isneginf),
         ("plus infinity", np.isposinf), ("real", np.isreal), ("complex", np.iscomplex)]


@pytest.mark.parametrize("kind, numpy_word", KINDS, ids=[k for k, _ in KINDS])
def test_turn_into_yes_or_no_is_kind_gives_numpys_answer(kind, numpy_word):
    values = np.array([1.0, np.inf, -np.inf, np.nan, -2.0])
    found = sdata.number_list([1.0, math.inf, -math.inf, None, -2.0]).turn_into_yes_or_no(is_=kind)
    assert found.as_numpy().tolist() == numpy_word(values).tolist()
    again = sdata.number_list([1.0, math.inf, -math.inf, None, -2.0]).turn_into_yes_or_no(is_=numpy_word.__name__)
    assert again.as_numpy().tolist() == numpy_word(values).tolist()


def test_turn_into_yes_or_no_not_a_time_and_mistakes():
    found = sdata.number_list([1.0, 2.0]).turn_into_yes_or_no(is_="not a time")
    assert found.as_numpy().tolist() == [False, False]
    with pytest.raises(sdata.SimplydataError, match="is_= alone"):
        sdata.number_list([1.0]).turn_into_yes_or_no(is_="finite", is_above=0)
    with pytest.raises(sdata.SimplydataError, match="does not know"):
        sdata.number_list([1.0]).turn_into_yes_or_no(is_="prime")


# ---------------------------------------------------------------- independent review fixes (2026-11-28)
# Spot checks written by hand: each SciPy or NumPy call below is written out with its own argument order, so a
# table row with its inputs in the wrong order, or the wrong part of several answers, fails here.
SPOT_CHECKS = [
    ("bessel J", {"order": 2.5}, 1.7, lambda: special.jv(2.5, 1.7)),
    ("bessel Y", {"order": 1.5}, 2.2, lambda: special.yv(1.5, 2.2)),
    ("bessel I", {"order": 0.5}, 1.3, lambda: special.iv(0.5, 1.3)),
    ("bessel K", {"order": 1.5}, 0.8, lambda: special.kv(1.5, 0.8)),
    ("bessel J scaled", {"order": 2.5}, 1.7, lambda: special.jve(2.5, 1.7)),
    ("bessel K whole order", {"order": 2}, 1.1, lambda: special.kn(2, 1.1)),
    ("bessel Y whole order", {"order": 3}, 2.6, lambda: special.yn(3, 2.6)),
    ("bessel J slope", {"order": 1.5, "how_many_times": 2}, 1.2, lambda: special.jvp(1.5, 1.2, 2)),
    ("elliptic integral first kind", {"parameter": 0.3}, 1.1, lambda: special.ellipkinc(1.1, 0.3)),
    ("elliptic integral second kind", {"parameter": 0.3}, 1.1, lambda: special.ellipeinc(1.1, 0.3)),
    ("hypergeometric 2F1", {"a": 0.3, "b": 1.2, "c": 2.5}, 0.4, lambda: special.hyp2f1(0.3, 1.2, 2.5, 0.4)),
    ("confluent hypergeometric 1F1", {"a": 0.7, "b": 1.9}, 1.3, lambda: special.hyp1f1(0.7, 1.9, 1.3)),
    ("hypergeometric 0F1", {"b": 1.5}, 0.8, lambda: special.hyp0f1(1.5, 0.8)),
    ("confluent hypergeometric U", {"a": 0.5, "b": 1.5}, 2.0, lambda: special.hyperu(0.5, 1.5, 2.0)),
    ("regularized incomplete beta", {"a": 2.0, "b": 5.0}, 0.3, lambda: special.betainc(2.0, 5.0, 0.3)),
    ("inverse regularized incomplete beta", {"a": 2.0, "b": 5.0}, 0.3, lambda: special.betaincinv(2.0, 5.0, 0.3)),
    ("regularized lower incomplete gamma", {"a": 3.0}, 1.7, lambda: special.gammainc(3.0, 1.7)),
    ("regularized upper incomplete gamma", {"a": 3.0}, 1.7, lambda: special.gammaincc(3.0, 1.7)),
    ("inverse regularized lower incomplete gamma", {"a": 3.0}, 0.4, lambda: special.gammaincinv(3.0, 0.4)),
    ("associated legendre function", {"order": 1, "degree": 3}, 0.4, lambda: special.lpmv(1, 3, 0.4)),
    ("spherical harmonic", {"degree": 3, "order": 2, "phi": 0.7}, 0.5,
     lambda: np.real(special.sph_harm_y(3, 2, 0.5, 0.7))),
    ("struve H", {"order": 1.5}, 2.3, lambda: special.struve(1.5, 2.3)),
    ("struve L", {"order": 0.5}, 1.2, lambda: special.modstruve(0.5, 1.2)),
    ("exponential integral En", {"order": 3}, 0.9, lambda: special.expn(3, 0.9)),
    ("polygamma", {"order": 2}, 1.4, lambda: special.polygamma(2, 1.4)),
    ("jacobi polynomial", {"degree": 3, "alpha": 0.5, "beta": 1.5}, 0.3,
     lambda: special.eval_jacobi(3, 0.5, 1.5, 0.3)),
    ("gegenbauer polynomial", {"degree": 4, "alpha": 1.5}, 0.3, lambda: special.eval_gegenbauer(4, 1.5, 0.3)),
    ("generalized laguerre polynomial", {"degree": 3, "alpha": 1.5}, 0.7,
     lambda: special.eval_genlaguerre(3, 1.5, 0.7)),
    ("legendre polynomial", {"degree": 4}, 0.3, lambda: special.eval_legendre(4, 0.3)),
    ("chebyshev T", {"degree": 5}, 0.3, lambda: special.eval_chebyt(5, 0.3)),
    ("hermite polynomial", {"degree": 3}, 0.7, lambda: special.eval_hermite(3, 0.7)),
    ("binomial coefficient", {"k": 2.0}, 5.0, lambda: special.binom(5.0, 2.0)),
    ("rising factorial", {"steps": 3.0}, 1.5, lambda: special.poch(1.5, 3.0)),
    ("log of beta size", {"b": 2.5}, 1.5, lambda: special.betaln(1.5, 2.5)),
    ("x times log y", {"y": 3.0}, 2.0, lambda: special.xlogy(2.0, 3.0)),
    ("huber loss", {"delta": 1.0}, 2.5, lambda: special.huber(1.0, 2.5)),
    ("pseudo huber loss", {"delta": 1.0}, 2.5, lambda: special.pseudo_huber(1.0, 2.5)),
    ("angle of point", {"x_values": -1.0}, 2.0, lambda: np.arctan2(2.0, -1.0)),
    ("remainder", {"divisor": 3.0}, -7.0, lambda: np.remainder(-7.0, 3.0)),
    ("times power of two", {"power": 3}, 1.5, lambda: np.ldexp(1.5, 3)),
    ("mathieu ce", {"order": 1, "q": 0.5}, 30.0, lambda: special.mathieu_cem(1, 0.5, 30.0)[0]),
    ("parabolic cylinder D", {"order": 1.5}, 0.7, lambda: special.pbdv(1.5, 0.7)[0]),
    ("airy Bi slope", {}, 0.7, lambda: special.airy(0.7)[3]),
    ("jacobi cn", {"parameter": 0.3}, 1.1, lambda: special.ellipj(1.1, 0.3)[1]),
    ("prolate angular function of the first kind", {"order": 0, "degree": 1, "c": 1.0}, 0.3,
     lambda: special.pro_ang1(0, 1, 1.0, 0.3)[0]),
    ("carlson RJ", {"y": 1.0, "z": 2.0, "p": 3.0}, 0.5, lambda: special.elliprj(0.5, 1.0, 2.0, 3.0)),
    ("bessel polynomial integral", {"power": 1.0, "order": 0.0}, 0.6, lambda: special.besselpoly(0.6, 1.0, 0.0)),
    ("voigt profile", {"sigma": 1.0, "gamma": 0.5}, 0.3, lambda: special.voigt_profile(0.3, 1.0, 0.5)),
    ("wright bessel", {"a": 0.5, "b": 1.0}, 0.8, lambda: special.wright_bessel(0.5, 1.0, 0.8)),
    ("box cox", {"power": 0.5}, 2.0, lambda: special.boxcox(2.0, 0.5)),
    ("lambert W", {"branch": -1}, -0.2, lambda: np.real(special.lambertw(-0.2, -1))),
    ("zeta", {"shift": 2.0}, 3.0, lambda: special.zeta(3.0, 2.0)),
    ("sine integral", {}, 1.3, lambda: special.sici(1.3)[0]),
    ("fresnel C", {}, 0.9, lambda: special.fresnel(0.9)[1]),
]


@pytest.mark.parametrize("plain, options, x, expected", SPOT_CHECKS, ids=[c[0] for c in SPOT_CHECKS])
def test_spot_checks_written_by_hand_with_the_librarys_argument_order(plain, options, x, expected):
    values = sdata.number_list([x])
    values.take_function(plain, **options)
    assert abs(values.as_numpy()[0] - expected()) <= 1e-12 * max(1.0, abs(expected())), plain


FORMULA_SPOT_CHECKS = [  # formula text written by hand, inputs in SciPy's order (or SymPy's, for SymPy's names)
    ("bessel_j(2.5, x)", 1.7, lambda: special.jv(2.5, 1.7)),
    ("kv(1.5, x)", 0.8, lambda: special.kv(1.5, 0.8)),
    ("besseli(0.5, x)", 1.3, lambda: special.iv(0.5, 1.3)),
    ("ellipkinc(x, 0.3)", 1.1, lambda: special.ellipkinc(1.1, 0.3)),
    ("elliptic_f(x, 0.3)", 1.1, lambda: special.ellipkinc(1.1, 0.3)),
    ("elliptic_e(x, 0.3)", 1.1, lambda: special.ellipeinc(1.1, 0.3)),
    ("hyp2f1(0.3, 1.2, 2.5, x)", 0.4, lambda: special.hyp2f1(0.3, 1.2, 2.5, 0.4)),
    ("betainc(2, 5, x)", 0.3, lambda: special.betainc(2.0, 5.0, 0.3)),
    ("gammaincc(3, x)", 1.7, lambda: special.gammaincc(3.0, 1.7)),
    ("lpmv(1, 3, x)", 0.4, lambda: special.lpmv(1, 3, 0.4)),
    ("assoc_legendre(3, 1, x)", 0.4, lambda: special.lpmv(1, 3, 0.4)),
    ("jacobi(3, 0.5, 1.5, x)", 0.3, lambda: special.eval_jacobi(3, 0.5, 1.5, 0.3)),
    ("expint(3, x)", 0.9, lambda: special.expn(3, 0.9)),
    ("struve(1.5, x)", 2.3, lambda: special.struve(1.5, 2.3)),
]


@pytest.mark.parametrize("text, x, expected", FORMULA_SPOT_CHECKS, ids=[c[0] for c in FORMULA_SPOT_CHECKS])
def test_formula_spot_checks_written_by_hand(text, x, expected):
    table = sdata.table({"x": [x]})
    table.add_column("y", text)
    assert abs(table.get_column("y").as_numpy()[0] - expected()) <= 1e-12 * max(1.0, abs(expected()))
    pytest.importorskip("sympy")
    assert abs(sdata.formula(text).find_value_at(x=x) - expected()) <= 1e-9 * max(1.0, abs(expected()))


def test_double_factorial_follows_scipys_rule_on_every_path():
    """SciPy's rule everywhere: 0 for a whole number below 0, empty for a number that is not whole (SymPy's own
    factorial2 gives 1 at -1 and stops at 5.5, so formula text no longer uses it)."""
    expected = special.factorial2(np.array([-3, -1, 0, 5]), exact=False)
    values = sdata.number_list([-3.0, -1.0, 0.0, 5.0, 5.5])
    values.take_function("double factorial")
    np.testing.assert_array_equal(values.as_numpy()[:4], expected)
    assert np.isnan(values.as_numpy()[4])
    table = sdata.table({"x": [-3.0, -1.0, 0.0, 5.0, 5.5]})
    table.add_column("y", "factorial2(x)")
    np.testing.assert_array_equal(table.get_column("y").as_numpy()[:4], expected)
    pytest.importorskip("sympy")
    formula = sdata.formula("double_factorial(x)")
    assert formula.find_value_at(x=-1) == 0.0 and formula.find_value_at(x=-3) == 0.0
    np.testing.assert_array_equal(formula.find_value_at(x=[-3, -1, 0, 5]).as_numpy(), expected)
    with pytest.raises(sdata.SimplydataError, match="no value among the ordinary numbers"):
        formula.find_value_at(x=5.5)


def test_ci_and_chi_below_zero_are_empty_on_every_path(capsys):
    for plain, name in (("cosine integral", "Ci"), ("hyperbolic cosine integral", "Chi")):
        values = sdata.number_list([-1.5, 0.5])
        values.take_function(plain)
        assert np.isnan(values.as_numpy()[0]) and "only for numbers above 0" in capsys.readouterr().out
        table = sdata.table({"x": [-1.5, 0.5]})
        table.add_column("y", f"{name}(x)")
        assert np.isnan(table.get_column("y").as_numpy()[0])
        pytest.importorskip("sympy")
        formula = sdata.formula(f"{name}(x)")
        assert np.isnan(formula.find_value_at(x=[-1.5, 0.5]).as_numpy()[0])
        with pytest.raises(sdata.SimplydataError, match="no value among the ordinary numbers"):
            formula.find_value_at(x=-1.5)


def test_slopes_of_the_tables_own_functions():
    pytest.importorskip("sympy")
    slope = sdata.formula("kelvin_ber(x)").find_slope_formula()
    assert abs(slope.find_value_at(x=1.3) - special.berp(1.3)) < 1e-12
    np.testing.assert_allclose(slope.find_value_at(x=[1.3, 2.0]).as_numpy(), special.berp([1.3, 2.0]))
    slope = sdata.formula("struve_h(0, x)").find_slope_formula()
    assert abs(slope.find_value_at(x=1.2) - (special.struve(-1, 1.2) - special.struve(1, 1.2)) / 2) < 1e-12
    slope = sdata.formula("bessel_j_slope(1, x)").find_slope_formula()
    assert abs(slope.find_value_at(x=1.2) - special.jvp(1, 1.2, 2)) < 1e-12
    slope = sdata.formula("spence(x)").find_slope_formula()  # d/dx Li2(1 - x) = log(x) / (1 - x)
    x = np.array([0.5, 2.0])
    np.testing.assert_allclose(slope.find_value_at(x=x.tolist()).as_numpy(), np.log(x) / (1 - x))
    with pytest.raises(sdata.SimplydataError, match="no slope formula for voigt_profile"):
        sdata.formula("voigt_profile(x, 1, 0.5)").find_slope_formula()
    with pytest.raises(sdata.SimplydataError, match="as its order changes"):
        sdata.formula("struve_h(x, 2)").find_slope_formula()


def test_limits_of_real_functions_are_plain_numbers():
    pytest.importorskip("sympy")
    found = sdata.formula("bessel_j(0, x)").find_limit_as("x", goes_to=1)
    assert isinstance(found, float) and abs(found - special.jv(0, 1.0)) < 1e-12
    found = sdata.formula("struve_h(0, x)").find_limit_as("x", goes_to=1)
    assert isinstance(found, float) and abs(found - special.struve(0, 1.0)) < 1e-12


@pytest.mark.parametrize("plain, name, option", [("exponential integral En", "expint", "order"),
                                                  ("polygamma", "polygamma", "order"),
                                                  ("hermite polynomial", "hermite", "degree")])
def test_an_order_that_must_be_whole_says_so_on_every_path(plain, name, option):
    with pytest.raises(sdata.SimplydataError, match=f"{option}= of the {plain} must be a whole number"):
        sdata.number_list([0.9]).take_function(plain, **{option: 2.5})
    table = sdata.table({"x": [0.9]})
    with pytest.raises(sdata.SimplydataError, match="must be a whole number"):
        table.add_column("y", f"{name}(2.5, x)")
    pytest.importorskip("sympy")
    with pytest.raises(sdata.SimplydataError, match="must be a whole number"):
        sdata.formula(f"{name}(2.5, x)")


def test_numbers_that_must_be_whole_say_so_in_the_note(capsys):
    values = sdata.number_list([4.0, 4.5])
    values.take_function("greatest common divisor", other=6)
    assert "takes whole numbers only" in capsys.readouterr().out


def test_work_on_bits_refuses_numbers_too_big_for_64_bits():
    with pytest.raises(sdata.SimplydataError, match="fit in 64 bits"):
        sdata.number_list([2.0 ** 63, 1.0]).work_on_bits("and", with_numbers=1)
    with pytest.raises(sdata.SimplydataError, match="fit in 64 bits"):
        sdata.number_list([1, 2]).work_on_bits("or", with_numbers=[2.0 ** 64, 1.0])


def test_scipys_jv_points_to_bessel_j_and_sympys_jn_to_spherical_bessel_j(capsys):
    with pytest.raises(sdata.SimplydataError, match=r"called bessel_j\(\)"):
        sdata.table({"x": [1.0]}).add_column("y", "jv(1, x)")
    sdata.help("sp.jn")
    assert "spherical_bessel_j" in capsys.readouterr().out
    sdata.help("special.jv")
    assert 'take_function("bessel J"' in capsys.readouterr().out


SYMPY_FORMULA_ENTRIES = [e for e in FORMULA_ENTRIES if e.sympy or e.sympy_expr]


@pytest.mark.parametrize("entry", SYMPY_FORMULA_ENTRIES, ids=[e.plain for e in SYMPY_FORMULA_ENTRIES])
def test_every_formula_with_sympys_function_is_written_back_as_readable_formula_text(entry):
    """What sdata.formula writes back (formula_text) is formula text again, with the same values (cot, polylog and
    elliptic_e with two values included)."""
    pytest.importorskip("sympy")
    from simplydata._formula import formula_text, parse

    x, options, expected = _formula_points(entry)
    x, expected = x[x > 0], expected[x > 0]
    if not x.size:
        pytest.skip("no sample above 0")
    written = formula_text(parse(_call(entry.formula_name, entry.inputs, options)))
    again = sdata.formula(written)
    np.testing.assert_allclose(again.find_value_at(x=x.tolist()).as_numpy(), expected, rtol=1e-9, atol=1e-12,
                               err_msg=written)


def test_a_whole_degree_goes_to_scipy_as_a_whole_number():
    # SciPy uses its exact recurrence for a whole degree and a general formula for any other degree; on macOS the
    # general formula gave U_3(0) = 2.6e-17 where SciPy's own call with degree 3 gives 0 (PR #81, 2026-11-28)
    from simplydata._maths_functions import BY_PLAIN, prepare

    for plain in ("chebyshev U", "chebyshev S", "shifted chebyshev U", "legendre polynomial"):
        entry = BY_PLAIN[plain]
        values = [3.0 if key == "degree" else np.array([0.0, 0.5]) for key in entry.inputs]
        ready, _ = prepare(entry, values)
        degree = ready[entry.inputs.index("degree")]
        assert np.asarray(degree).dtype.kind == "i", plain
    ready, _ = prepare(BY_PLAIN["chebyshev U"], [2.5, np.array([0.5])])
    assert np.asarray(ready[0]).dtype.kind == "f"  # a degree that is not whole stays a number with decimals
