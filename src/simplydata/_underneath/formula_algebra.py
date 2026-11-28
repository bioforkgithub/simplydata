"""Families for 100 %, batches 22-23 (plan section 2.10, approved by Manish 2026-11-28, G14): polynomial algebra on a
formula and SymPy's names in formula text. The words find_roots, find_degree, divide_by, find_common_factor_with,
find_common_multiple_with, turn_into_one_fraction, split_into_top_and_bottom, find_repeated_parts and the family
find_fact, their options, the by= values of make_simpler, turn_into_sum and turn_into_product, and SymPy's own
functions and constants inside the text of sdata.formula. Exact answers are compared as SymPy writes them (text),
numbers to a tight tolerance.
"""

from . import Entry

SYMPY = """
            import sympy as sp
            x = sp.Symbol("x")"""

ENTRIES = [
    # ------------------------------------------------------------------ find_roots
    Entry(
        word="f.find_roots",
        ours="""
            formula = sdata.formula("(x - 1)**2*(x**2 + 1)")
            roots = formula.find_roots()
            roots.get_column("root exactly")
        """,
        code={"SymPy": SYMPY + """
            # formula.find_roots()
            found = sp.all_roots((x - 1)**2*(x**2 + 1))
            [str(r) for r in dict.fromkeys(found)]   # (1)
        """},
        compare="value",
        choices=("a root that repeats has one row, with the number of times in the column times (SymPy all_roots "
                 "lists it once for each time).",),
        also="simplydata also gives each root as a decimal (empty for a complex root), refuses a formula that is "
             "not a polynomial in one letter, and points to sdata.solve for other equations.",
    ),
    Entry(
        word="f.find_roots", option="real_only=",
        ours="""
            formula = sdata.formula("x**5 - x + 1")
            roots = formula.find_roots(real_only=True)
            roots.get_column("root").as_numpy().tolist()
        """,
        code={"SymPy": SYMPY + """
            # formula.find_roots(real_only=True)
            [float(r) for r in sp.real_roots(x**5 - x + 1)]
        """},
        compare="value",
        tolerance=1e-14,
        also="simplydata also keeps SymPy's exact root (CRootOf) in the column root exactly.",
    ),
    Entry(
        word="f.find_roots", option="fractions_only=",
        ours="""
            formula = sdata.formula("2*x**3 - 3*x**2 - 2*x + 3")
            roots = formula.find_roots(fractions_only=True)
            roots.get_column("root exactly")
        """,
        code={"SymPy": SYMPY + """
            # formula.find_roots(fractions_only=True)
            found = sp.ground_roots(2*x**3 - 3*x**2 - 2*x + 3)
            [str(r) for r in sorted(found, key=float)]   # (1)
        """},
        compare="value",
        choices=("the roots come smallest first (SymPy ground_roots gives a dict without an order).",),
    ),
    Entry(
        word="f.find_roots", option="exactly=",
        ours="""
            formula = sdata.formula("x**3 - 2")
            roots = formula.find_roots(exactly=False)
            [str(text) for text in roots.get_column("root as text")]
        """,
        code={"SymPy": SYMPY + """
            # formula.find_roots(exactly=False)
            [str(r) for r in sp.nroots(x**3 - 2, n=15)]   # (1)
        """},
        compare="value",
        choices=("15 significant digits, as many as a float keeps (SymPy nroots' own default).",),
    ),
    Entry(
        word="f.find_roots", option="show=",
        ours="""
            formula = sdata.formula("x**3 - 2*x**2 - x + 2")
            formula.find_roots(show="count")
        """,
        code={"SymPy": SYMPY + """
            # formula.find_roots(show="count")
            sp.count_roots(x**3 - 2*x**2 - x + 2)
        """},
        compare="value",
        also='simplydata also gives show="intervals", an interval around each real root (SymPy intervals).',
    ),
    Entry(
        word="f.find_roots", option="between=",
        ours="""
            formula = sdata.formula("x**3 - 2*x**2 - x + 2")
            roots = formula.find_roots(between=[0, 3])
            roots.get_column("root exactly")
        """,
        code={"SymPy": SYMPY + """
            # formula.find_roots(between=[0, 3])
            found = sp.real_roots(x**3 - 2*x**2 - x + 2)
            [str(r) for r in found if 0 <= r <= 3]
        """},
        compare="value",
    ),
    Entry(
        word="f.find_roots", option="within=",
        ours="""
            formula = sdata.formula("x**2 - 2")
            found = formula.find_roots(show="intervals", within=0.001)
            found.get_column("to").as_numpy().tolist()
        """,
        code={"SymPy": SYMPY + """
            # formula.find_roots(show="intervals", within=0.001)
            found = sp.intervals(x**2 - 2, eps=sp.Rational(1, 1000))
            [float(b) for (a, b), times in found]
        """},
        compare="value",
        tolerance=0.0,
    ),
    # ------------------------------------------------------------------ find_degree
    Entry(
        word="f.find_degree",
        ours="""
            formula = sdata.formula("x**3*y + x*y**2 + 1")
            formula.find_degree()
        """,
        code={"SymPy": """
            import sympy as sp
            x, y = sp.symbols("x y")
            # formula.find_degree()
            sp.total_degree(x**3*y + x*y**2 + 1)   # (1)
        """},
        compare="value",
        choices=("with several letters and no for_letter=, the total degree (the highest sum of powers in one "
                 "term); SymPy degree alone would give the degree in the first letter.",),
    ),
    Entry(
        word="f.find_degree", option="for_letter=",
        ours="""
            formula = sdata.formula("x**3*y + x*y**2 + 1")
            formula.find_degree(for_letter=["x", "y"])
        """,
        code={"SymPy": """
            import sympy as sp
            x, y = sp.symbols("x y")
            # formula.find_degree(for_letter=["x", "y"])
            dict(zip(["x", "y"], sp.degree_list(x**3*y + x*y**2 + 1, x, y)))
        """},
        compare="value",
        also='simplydata also gives the degree in one letter: for_letter="x" (SymPy degree).',
    ),
    # ------------------------------------------------------------------ divide_by
    Entry(
        word="f.divide_by",
        ours="""
            formula = sdata.formula("x**3 - 2*x + 5")
            quotient, remainder = formula.divide_by("x - 1")
            [str(quotient), str(remainder)]
        """,
        code={"SymPy": SYMPY + """
            # formula.divide_by("x - 1")
            quotient, remainder = sp.div(x**3 - 2*x + 5, x - 1, x)
            [str(quotient), str(remainder)]
        """},
        compare="value",
        also="simplydata also refuses a division by 0 and says when a formula is not a polynomial.",
    ),
    Entry(
        word="f.divide_by", option="show=",
        ours="""
            formula = sdata.formula("x**3 - 2*x + 5")
            str(formula.divide_by("x - 1", show="remainder"))
        """,
        code={"SymPy": SYMPY + """
            # formula.divide_by("x - 1", show="remainder")
            str(sp.rem(x**3 - 2*x + 5, x - 1, x))
        """},
        compare="value",
        also='simplydata also gives show="quotient" (SymPy quo).',
    ),
    Entry(
        word="f.divide_by", option="without_fractions=",
        ours="""
            formula = sdata.formula("x**3 - 2*x + 5")
            quotient, remainder = formula.divide_by("2*x - 1", without_fractions=True)
            [str(quotient), str(remainder)]
        """,
        code={"SymPy": SYMPY + """
            # formula.divide_by("2*x - 1", without_fractions=True)
            quotient, remainder = sp.pdiv(x**3 - 2*x + 5, 2*x - 1, x)
            [str(quotient), str(remainder)]
        """},
        compare="value",
    ),
    Entry(
        word="f.divide_by", option="with_no_remainder=",
        ours="""
            formula = sdata.formula("x**3 - 1")
            str(formula.divide_by("x - 1", with_no_remainder=True))
        """,
        code={"SymPy": SYMPY + """
            # formula.divide_by("x - 1", with_no_remainder=True)
            str(sp.exquo(x**3 - 1, x - 1, x))
        """},
        compare="value",
        also="simplydata also says in a sentence when a remainder is left (SymPy raises ExactQuotientFailed).",
    ),
    # ------------------------------------------------------------------ common factor and multiple
    Entry(
        word="f.find_common_factor_with",
        ours="""
            formula = sdata.formula("x**2 + 2*x + 1")
            str(formula.find_common_factor_with("x**2 - 1"))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_common_factor_with("x**2 - 1")
            str(sp.gcd(x**2 + 2*x + 1, x**2 - 1, x))
        """},
        compare="value",
        also="simplydata also takes a list of formulas (SymPy gcd_list).",
    ),
    Entry(
        word="f.find_common_factor_with", option="show=",
        ours="""
            formula = sdata.formula("x**2 - 1")
            s, t, h = formula.find_common_factor_with("x**2 + 3*x + 2", show="combination")
            [str(s), str(t), str(h)]
        """,
        code={"SymPy": SYMPY + """
            # formula.find_common_factor_with("x**2 + 3*x + 2", show="combination")
            [str(part) for part in sp.gcdex(x**2 - 1, x**2 + 3*x + 2, x)]
        """},
        compare="value",
        also='simplydata also gives show="common factor and the rest" (cofactors) and "half combination" '
             "(half_gcdex).",
    ),
    Entry(
        word="f.find_common_multiple_with",
        ours="""
            formula = sdata.formula("x**2 + 2*x + 1")
            str(formula.find_common_multiple_with("x**2 - 1"))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_common_multiple_with("x**2 - 1")
            str(sp.lcm(x**2 + 2*x + 1, x**2 - 1, x))
        """},
        compare="value",
        also="simplydata also takes a list of formulas (SymPy lcm_list).",
    ),
    # ------------------------------------------------------------------ fractions and parts
    Entry(
        word="f.turn_into_one_fraction",
        ours="""
            formula = sdata.formula("1/x + 1/(x + 1)")
            str(formula.turn_into_one_fraction())
        """,
        code={"SymPy": SYMPY + """
            # formula.turn_into_one_fraction()
            str(sp.together(1/x + 1/(x + 1)))
        """},
        compare="value",
        also="simplydata also keeps the step, so formula.undo() takes it back.",
    ),
    Entry(
        word="f.split_into_top_and_bottom",
        ours="""
            formula = sdata.formula("(x + 1)/(x - 2)")
            top, bottom = formula.split_into_top_and_bottom()
            [str(top), str(bottom)]
        """,
        code={"SymPy": SYMPY + """
            # formula.split_into_top_and_bottom()
            top, bottom = sp.fraction((x + 1)/(x - 2))
            [str(top), str(bottom)]
        """},
        compare="value",
    ),
    Entry(
        word="f.find_repeated_parts",
        ours="""
            formula = sdata.formula("(x + 1)**2 + sin(x + 1)")
            parts, shorter = formula.find_repeated_parts()
            [[name, str(part)] for name, part in parts.items()] + [str(shorter)]
        """,
        code={"SymPy": SYMPY + """
            # formula.find_repeated_parts()
            parts, shorter = sp.cse((x + 1)**2 + sp.sin(x + 1))
            [[str(name), str(part)] for name, part in parts] + [str(shorter[0])]
        """},
        compare="value",
    ),
    # ------------------------------------------------------------------ the family find_fact
    Entry(
        word="f.find_fact",
        ours="""
            formula = sdata.formula("a*x**2 + b*x + c")
            str(formula.find_fact("discriminant", for_letter="x"))
        """,
        code={"SymPy": """
            import sympy as sp
            a, b, c, x = sp.symbols("a b c x")
            # formula.find_fact("discriminant", for_letter="x")
            str(sp.discriminant(a*x**2 + b*x + c, x))
        """},
        compare="value",
        also="simplydata also takes SymPy's names (\"LC\", \"groebner\", \"sqf_list\"), and asks for for_letter= "
             "when a fact of one letter meets a formula of several.",
    ),
    Entry(
        word="f.find_fact", option="other=",
        ours="""
            formula = sdata.formula("x**2 - 3*x + 1")
            formula.find_fact("resultant", other="x - 1")
        """,
        code={"SymPy": SYMPY + """
            # formula.find_fact("resultant", other="x - 1")
            float(sp.resultant(x**2 - 3*x + 1, x - 1, x))
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="f.find_fact", option="power=",
        ours="""
            formula = sdata.formula("x**2 - 3*x + 1")
            str(formula.find_fact("powers of roots", power=2))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_fact("powers of roots", power=2)
            str(sp.nth_power_roots_poly(x**2 - 3*x + 1, 2, x))
        """},
        compare="value",
    ),
    # ------------------------------------------------------------------ by= of make_simpler, turn_into_sum, product
    Entry(
        word="f.make_simpler", option="by=",
        ours="""
            formula = sdata.formula("x**a * x**b")
            str(formula.make_simpler(by="powers"))
        """,
        code={"SymPy": """
            import sympy as sp
            a, b, x = sp.symbols("a b x")
            # formula.make_simpler(by="powers")
            str(sp.powsimp(x**a * x**b))
        """},
        compare="value",
        also="simplydata also takes SymPy's names (by=\"powsimp\"), and formula.undo() takes the step back.",
    ),
    Entry(
        word="f.turn_into_sum", option="by=",
        ours="""
            formula = sdata.formula("sin(a + b)")
            str(formula.turn_into_sum(by="trig functions"))
        """,
        code={"SymPy": """
            import sympy as sp
            a, b = sp.symbols("a b")
            # formula.turn_into_sum(by="trig functions")
            str(sp.expand_trig(sp.sin(a + b)))
        """},
        compare="value",
    ),
    Entry(
        word="f.turn_into_product", option="by=",
        ours="""
            formula = sdata.formula("x**3 + 2*x + 1")
            str(formula.turn_into_product(by="nested"))
        """,
        code={"SymPy": SYMPY + """
            # formula.turn_into_product(by="nested")
            str(sp.horner(x**3 + 2*x + 1))
        """},
        compare="value",
    ),
]
