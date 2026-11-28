"""Families for 100 %, batches 24-26 (plan section 2.10, approved by Manish 2026-11-28, G13 and G15): calculus checks,
series, transforms and code on a formula (take_transform, find_area_along_path, check_if_always, find_turning_points,
find_where_undefined, find_period, find_fourier_series, find_residue_at, list_terms, find_hessian, find_wronskian,
show_as_code, show_as_tree and the new options of find_taylor_series, find_limit_as, find_slope_formula and
show_as_latex); sdata.check_solution, find_product_of_series, list_ways_to_choose, list_ways_to_order and the new
kinds of sdata.solve(exactly=True); number theory on numbers (check_if_prime, find_prime_factors,
find_number_fact); exact grids (sdata.number_grid(exactly=True)), find_permanent and make_columns_orthogonal. Exact
answers are compared as SymPy writes them (text), numbers to a tight tolerance.
"""

from . import Entry

SYMPY = """
            import sympy as sp
            x = sp.Symbol("x")"""

ENTRIES = [
    # ------------------------------------------------------------------ transforms
    Entry(
        word="f.take_transform",
        ours="""
            formula = sdata.formula("exp(-2*t)")
            str(formula.take_transform("laplace"))
        """,
        code={"SymPy": """
            import sympy as sp
            t, s = sp.symbols("t s")
            # formula.take_transform("laplace")
            str(sp.laplace_transform(sp.exp(-2*t), t, s)[0])   # (1)
        """},
        compare="value",
        choices=("the transform, printed with where it holds (Re(s) > -2, SymPy's second answer), from the letter t "
                 "to the letter s (x to k for Fourier, sine, cosine; r to k for Hankel).",),
        also="simplydata also takes SymPy's names (\"laplace_transform\"), refuses a to_letter= already in the "
             "formula, and says so when SymPy gives the transform back unworked.",
    ),
    Entry(
        word="f.take_transform", option="from_letter=",
        ours="""
            formula = sdata.formula("exp(-a*u)")
            str(formula.take_transform("laplace", from_letter="u", to_letter="p"))
        """,
        code={"SymPy": """
            import sympy as sp
            a, u, p = sp.symbols("a u p")
            # formula.take_transform("laplace", from_letter="u", to_letter="p")
            str(sp.laplace_transform(sp.exp(-a*u), u, p)[0])
        """},
        compare="value",
    ),
    Entry(
        word="f.take_transform", option="order=",
        ours="""
            formula = sdata.formula("exp(-r)")
            str(formula.take_transform("hankel", order=1))
        """,
        code={"SymPy": """
            import sympy as sp
            r, k = sp.symbols("r k")
            # formula.take_transform("hankel", order=1)
            str(sp.hankel_transform(sp.exp(-r), r, k, 1, noconds=True))
        """},
        compare="value",
    ),
    Entry(
        word="f.take_transform", option="between=",
        ours="""
            formula = sdata.formula("gamma(s)")
            str(formula.take_transform("inverse mellin", between=[0, "infinity"]))
        """,
        code={"SymPy": """
            import sympy as sp
            s, x = sp.symbols("s x")
            # formula.take_transform("inverse mellin", between=[0, "infinity"])
            str(sp.inverse_mellin_transform(sp.gamma(s), s, x, (0, sp.oo)))
        """},
        compare="value",
    ),
    Entry(
        word="f.find_area_along_path",
        ours="""
            formula = sdata.formula("x**2 + y**2")
            formula.find_area_along_path(path="x = cos(t), y = sin(t)", between=[0, "2*pi"])
        """,
        code={"SymPy": """
            import sympy as sp
            x, y, t = sp.symbols("x y t")
            # formula.find_area_along_path(path="x = cos(t), y = sin(t)", between=[0, "2*pi"])
            circle = sp.Curve([sp.cos(t), sp.sin(t)], (t, 0, 2*sp.pi))
            float(sp.line_integrate(x**2 + y**2, circle, [x, y]))
        """},
        compare="value",
        tolerance=1e-15,
        also="simplydata also reads the path as text or a dict, checks it gives every letter of the formula in "
             "one new letter, and keeps the exact answer in what it prints.",
    ),
    # ------------------------------------------------------------------ calculus checks
    Entry(
        word="f.check_if_always",
        ours="""
            formula = sdata.formula("x**2")
            formula.check_if_always("rising", between=[0, 5])
        """,
        code={"SymPy": SYMPY + """
            # formula.check_if_always("rising", between=[0, 5])
            sp.is_increasing(x**2, sp.Interval(0, 5), x)
        """},
        compare="value",
        also="simplydata also says plainly when SymPy cannot tell (None).",
    ),
    Entry(
        word="f.check_if_always", option="between=",
        ours="""
            formula = sdata.formula("x**2")
            formula.check_if_always("bending up", between=[-1, 1])
        """,
        code={"SymPy": SYMPY + """
            # formula.check_if_always("bending up", between=[-1, 1])
            sp.is_convex(x**2, x, domain=sp.Interval(-1, 1))   # (1)
        """},
        compare="value",
        choices=("without between=, every real number (SymPy's own default domain, S.Reals).",),
    ),
    Entry(
        word="f.find_turning_points",
        ours="""
            formula = sdata.formula("x**3 - 3*x")
            points = formula.find_turning_points()
            points.get_column("at").as_numpy().tolist()
        """,
        code={"SymPy": SYMPY + """
            # formula.find_turning_points()
            sorted(float(p) for p in sp.stationary_points(x**3 - 3*x, x, sp.S.Reals))
        """},
        compare="value",
        also="simplydata also gives the value of the formula at each point, refuses an endless set (sin(x)) with a "
             "pointer to between=, and sorts the points smallest first.",
    ),
    Entry(
        word="f.find_turning_points", option="between=",
        ours="""
            formula = sdata.formula("sin(x)")
            points = formula.find_turning_points(between=[0, 7])
            [str(text) for text in points.get_column("at exactly")]
        """,
        code={"SymPy": SYMPY + """
            # formula.find_turning_points(between=[0, 7])
            [str(p) for p in sorted(sp.stationary_points(sp.sin(x), x, sp.Interval(0, 7)), key=float)]
        """},
        compare="value",
    ),
    Entry(
        word="f.find_where_undefined",
        ours="""
            formula = sdata.formula("1/(x**2 - 1)")
            points = formula.find_where_undefined()
            points.get_column("at").as_numpy().tolist()
        """,
        code={"SymPy": SYMPY + """
            # formula.find_where_undefined()
            sorted(float(p) for p in sp.singularities(1/(x**2 - 1), x, sp.S.Reals))
        """},
        compare="value",
    ),
    Entry(
        word="f.find_period",
        ours="""
            formula = sdata.formula("sin(2*x)")
            formula.find_period()
        """,
        code={"SymPy": SYMPY + """
            # formula.find_period()
            float(sp.periodicity(sp.sin(2*x), x))
        """},
        compare="value",
        tolerance=1e-15,
    ),
    # ------------------------------------------------------------------ series
    Entry(
        word="f.find_fourier_series",
        ours="""
            formula = sdata.formula("x")
            str(formula.find_fourier_series(between=["-pi", "pi"]))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_fourier_series(between=["-pi", "pi"])
            str(sp.fourier_series(x, (x, -sp.pi, sp.pi)).truncate(3))   # (1)
        """},
        compare="value",
        choices=("the first 3 parts that are not 0, each frequency with its cosine and sine one part (SymPy "
                 "truncate's own default), over -pi to pi.",),
    ),
    Entry(
        word="f.find_fourier_series", option="how_many_terms=",
        ours="""
            formula = sdata.formula("x**2")
            str(formula.find_fourier_series(between=["-pi", "pi"], how_many_terms=4))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_fourier_series(between=["-pi", "pi"], how_many_terms=4)
            str(sp.fourier_series(x**2, (x, -sp.pi, sp.pi)).truncate(4))
        """},
        compare="value",
    ),
    Entry(
        word="f.find_residue_at",
        ours="""
            formula = sdata.formula("exp(x)/x**3")
            formula.find_residue_at(at=0)
        """,
        code={"SymPy": SYMPY + """
            # formula.find_residue_at(at=0)
            float(sp.residue(sp.exp(x)/x**3, x, 0))
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="f.list_terms",
        ours="""
            formula = sdata.formula("n**2")
            terms = formula.list_terms(between=[1, 5])
            terms.get_column("term").as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            n = sp.Symbol("n")
            # formula.list_terms(between=[1, 5])
            [float(term) for term in sp.sequence(n**2, (n, 1, 5))]
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="f.find_taylor_series", option="all_terms=",
        ours="""
            formula = sdata.formula("exp(x)")
            str(formula.find_taylor_series(all_terms=True))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_taylor_series(all_terms=True)
            str(sp.fps(sp.exp(x), x, 0).infinite)
        """},
        compare="value",
    ),
    Entry(
        word="f.find_limit_as", option="whole_numbers_only=",
        ours="""
            formula = sdata.formula("(-1)**n/n")
            formula.find_limit_as("n", goes_to="infinity", whole_numbers_only=True)
        """,
        code={"SymPy": """
            import sympy as sp
            n = sp.Symbol("n")
            # formula.find_limit_as("n", goes_to="infinity", whole_numbers_only=True)
            float(sp.limit_seq((-1)**n/n, n))
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="f.find_slope_formula", option="step=",
        ours="""
            formula = sdata.formula("x**2")
            str(formula.find_slope_formula(step="h"))
        """,
        code={"SymPy": """
            import sympy as sp
            x, h = sp.symbols("x h")
            # formula.find_slope_formula(step="h")
            str(sp.differentiate_finite(x**2, x, points=[x, x + h]))   # (1)
        """},
        compare="value",
        choices=("a forward difference, at the points x and x + step (SymPy's own default is the central one, at "
                 "x - 1/2 and x + 1/2); with step=1 it is SymPy difference_delta, the step between neighbouring "
                 "terms of a sequence.",),
    ),
    Entry(
        word="f.find_hessian",
        ours="""
            formula = sdata.formula("x**2*y + y**3")
            grid = formula.find_hessian()
            str(grid.as_sympy())
        """,
        code={"SymPy": """
            import sympy as sp
            x, y = sp.symbols("x y")
            # formula.find_hessian()
            str(sp.hessian(x**2*y + y**3, [x, y]))
        """},
        compare="value",
        also="simplydata also gives the Hessian as an exact grid, on which find_determinant and find_value_at work.",
    ),
    Entry(
        word="f.find_wronskian",
        ours="""
            formula = sdata.formula("exp(x)")
            str(formula.find_wronskian(["exp(2*x)"]))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_wronskian(["exp(2*x)"])
            str(sp.wronskian([sp.exp(x), sp.exp(2*x)], x))
        """},
        compare="value",
    ),
    Entry(
        word="f.find_wronskian", option="whole_numbers_only=",
        ours="""
            formula = sdata.formula("2**n")
            str(formula.find_wronskian(["3**n"], whole_numbers_only=True))
        """,
        code={"SymPy": """
            import sympy as sp
            n = sp.Symbol("n")
            # formula.find_wronskian(["3**n"], whole_numbers_only=True)
            str(sp.casoratian([2**n, 3**n], n, zero=False))   # (1)
        """},
        compare="value",
        choices=("the Casoratian as a formula in the letter (zero=False); SymPy's default puts n = 0 in.",),
    ),
    Entry(
        word="f.find_wronskian", option="for_letter=",
        ours="""
            formula = sdata.formula("exp(a*x)")
            str(formula.find_wronskian(["exp(2*x)"], for_letter="x"))
        """,
        code={"SymPy": """
            import sympy as sp
            a, x = sp.symbols("a x")
            # formula.find_wronskian(["exp(2*x)"], for_letter="x")
            str(sp.wronskian([sp.exp(a*x), sp.exp(2*x)], x))
        """},
        compare="value",
    ),
    # ------------------------------------------------------------------ showing
    Entry(
        word="f.show_as_code",
        ours="""
            formula = sdata.formula("sin(x)**2 + exp(-x)")
            formula.show_as_code("r")
        """,
        code={"SymPy": SYMPY + """
            # formula.show_as_code("r")
            sp.rcode(sp.sin(x)**2 + sp.exp(-x))
        """},
        compare="value",
        also="simplydata also prints the code, and takes SymPy's printer names (\"rcode\", \"julia_code\").",
    ),
    Entry(
        word="f.show_as_tree",
        ours="""
            formula = sdata.formula("x**2 + 1")
            formula.show_as_tree()
        """,
        code={"SymPy": SYMPY + """
            # formula.show_as_tree()
            from sympy.printing.tree import tree
            tree(x**2 + 1, assumptions=False).rstrip()   # (1)
        """},
        compare="value",
        choices=("without the assumptions of each part (print_tree lists them by default), so the tree stays short.",),
    ),
    Entry(
        word="f.show_as_tree", option="as_graphviz=",
        ours="""
            formula = sdata.formula("x + 1")
            formula.show_as_tree(as_graphviz=True)
        """,
        code={"SymPy": SYMPY + """
            # formula.show_as_tree(as_graphviz=True)
            sp.dotprint(x + 1)
        """},
        compare="value",
    ),
    Entry(
        word="f.show_as_latex", option="left_side=",
        ours="""
            formula = sdata.formula("x**2 + 2*x + 1")
            formula.show_as_latex(left_side="y")
        """,
        code={"SymPy": SYMPY + """
            # formula.show_as_latex(left_side="y")
            sp.latex(sp.Symbol("y")) + " = " + sp.latex(x**2 + 2*x + 1)
        """},
        compare="value",
    ),
    Entry(
        word="f.show_as_latex", option="over_lines=",
        ours="""
            formula = sdata.formula("x**2 + 2*x + 1")
            formula.show_as_latex(over_lines=True)
        """,
        code={"SymPy": SYMPY + """
            # formula.show_as_latex(over_lines=True)
            sp.multiline_latex(sp.Symbol("y"), x**2 + 2*x + 1)
        """},
        compare="value",
    ),
    # ------------------------------------------------------------------ solving
    Entry(
        word="sdata.check_solution",
        ours="""
            sdata.check_solution("dy/dx = y", "y = 3*exp(x)")
        """,
        code={"SymPy": SYMPY + """
            # check_solution("dy/dx = y", "y = 3*exp(x)")
            y = sp.Function("y")
            works, rest = sp.checkodesol(sp.Eq(y(x).diff(x), y(x)), sp.Eq(y(x), 3*sp.exp(x)))
            works
        """},
        compare="value",
        also="simplydata also reads the equation as text (dy/dx), and uses checksol for an equation without "
             "slopes and checkpdesol for slopes in two letters.",
    ),
    Entry(
        word="sdata.find_product_of_series",
        ours="""
            str(sdata.find_product_of_series("k/(k + 1)", between=[1, "n"]))
        """,
        code={"SymPy": """
            import sympy as sp
            k, n = sp.symbols("k n", integer=True)
            # find_product_of_series("k/(k + 1)", between=[1, "n"])
            str(sp.product(k/(k + 1), (k, 1, n)))   # (1)
        """},
        compare="value",
        choices=("the letter that counts is a whole number (integer=True), as in find_sum_of_series.",),
    ),
    Entry(
        word="sdata.solve", option="whole_numbers_only=",
        ours="""
            table = sdata.solve("x**2 + y**2 = 25", exactly=True, whole_numbers_only=True)
            table.count_rows()
        """,
        code={"SymPy": """
            import sympy as sp
            x, y = sp.symbols("x y")
            # solve("x**2 + y**2 = 25", exactly=True, whole_numbers_only=True)
            len(sp.diophantine(x**2 + y**2 - 25, syms=(x, y), permute=True))   # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("each change of sign and order of SymPy's solutions (permute=True); SymPy's default gives one of "
                 "each kind only.",),
    ),
    Entry(
        word="sdata.solve", option="at_start=",
        ours="""
            answer = sdata.solve("a(n + 2) = a(n + 1) + a(n)", exactly=True, at_start={0: 0, 1: 1})
            str(answer)
        """,
        code={"SymPy": """
            import sympy as sp
            n = sp.Symbol("n", integer=True)
            a = sp.Function("a")
            # solve("a(n + 2) = a(n + 1) + a(n)", exactly=True, at_start={0: 0, 1: 1})
            str(sp.rsolve(a(n + 2) - a(n + 1) - a(n), a(n), {a(0): 0, a(1): 1}))
        """},
        compare="value",
        also="simplydata also solves an equation with slopes in two letters (\"du/dx + 2*du/dy = 0\") with SymPy "
             "pdsolve.",
    ),
    Entry(
        word="sdata.list_ways_to_choose",
        ours="""
            ways = sdata.list_ways_to_choose(2, out_of=["A", "B", "C", "D"])
            [list(row.values()) for row in ways.as_list()]
        """,
        code={"SymPy": """
            import sympy as sp
            # list_ways_to_choose(2, out_of=["A", "B", "C", "D"])
            [list(way) for way in sp.subsets(["A", "B", "C", "D"], 2)]
        """},
        compare="value",
        also="simplydata also counts the ways first (SymPy binomial) and refuses more than 100,000.",
    ),
    Entry(
        word="sdata.list_ways_to_choose", option="one_from_each=",
        ours="""
            ways = sdata.list_ways_to_choose(one_from_each=[["red", "blue"], ["S", "M"]])
            [list(row.values()) for row in ways.as_list()]
        """,
        code={"SymPy": """
            import sympy as sp
            # list_ways_to_choose(one_from_each=[["red", "blue"], ["S", "M"]])
            [list(way) for way in sp.cartes(["red", "blue"], ["S", "M"])]
        """},
        compare="value",
    ),
    Entry(
        word="sdata.list_ways_to_choose", option="with_repeats=",
        ours="""
            ways = sdata.list_ways_to_choose(2, out_of=["A", "B", "C"], with_repeats=True)
            [list(row.values()) for row in ways.as_list()]
        """,
        code={"SymPy": """
            import sympy as sp
            # list_ways_to_choose(2, out_of=["A", "B", "C"], with_repeats=True)
            [list(way) for way in sp.subsets(["A", "B", "C"], 2, repetition=True)]
        """},
        compare="value",
    ),
    Entry(
        word="sdata.list_ways_to_order",
        ours="""
            ways = sdata.list_ways_to_order(2, out_of=["A", "B", "C"])
            [list(row.values()) for row in ways.as_list()]
        """,
        code={"SymPy": """
            import sympy as sp
            # list_ways_to_order(2, out_of=["A", "B", "C"])
            [list(way) for way in sp.variations(["A", "B", "C"], 2)]
        """},
        compare="value",
    ),
    # ------------------------------------------------------------------ number theory
    Entry(
        word="nums.check_if_prime",
        ours="""
            numbers = sdata.number_list([2, 9, 11, 561])
            numbers.check_if_prime().as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: check_if_prime()
            [sp.isprime(n) for n in [2, 9, 11, 561]]
        """},
        compare="value",
        also="simplydata also refuses empty numbers, numbers with a decimal part and numbers above 2**53.",
    ),
    Entry(
        word="nums.find_prime_factors",
        ours="""
            numbers = sdata.number_list([360])
            factors = numbers.find_prime_factors()
            factors.get_column("times").as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: find_prime_factors()
            [times for prime, times in sorted(sp.factorint(360).items())]
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="nums.find_prime_factors", option="show=",
        ours="""
            numbers = sdata.number_list([360])
            factors = numbers.find_prime_factors(show="different primes")
            factors.get_column("prime").as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: find_prime_factors(show="different primes")
            [float(p) for p in sp.primefactors(360)]
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="nums.find_number_fact",
        ours="""
            numbers = sdata.number_list([28])
            divisors = numbers.find_number_fact("divisors")
            divisors.get_column("answer").as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: find_number_fact("divisors")
            [float(d) for d in sp.divisors(28)]
        """},
        compare="value",
        tolerance=0.0,
        also="simplydata also takes SymPy's names (\"divisor_count\"), gives yes-or-no facts as yes or no values, "
             "and gives an answer above 2**53 exactly as text.",
    ),
    Entry(
        word="nums.find_number_fact", option="other=",
        ours="""
            numbers = sdata.number_list([220])
            numbers.find_number_fact("amicable with", other=284).as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: find_number_fact("amicable with", other=284)
            [sp.is_amicable(220, 284)]
        """},
        compare="value",
    ),
    Entry(
        word="nums.find_number_fact", option="modulo=",
        ours="""
            numbers = sdata.number_list([3])
            numbers.find_number_fact("inverse modulo", modulo=7).as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: find_number_fact("inverse modulo", modulo=7)
            [float(sp.mod_inverse(3, 7))]
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="nums.find_number_fact", option="power=",
        ours="""
            numbers = sdata.number_list([17])
            root = numbers.find_number_fact("whole nth root", power=2)
            root.get_column("root").as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: find_number_fact("whole nth root", power=2)
            [float(sp.integer_nthroot(17, 2)[0])]
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="nums.find_number_fact", option="base=",
        ours="""
            numbers = sdata.number_list([12])
            numbers.find_number_fact("discrete log", modulo=41, base=7).as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # on the numbers: find_number_fact("discrete log", modulo=41, base=7)
            [float(sp.discrete_log(41, 12, 7))]
        """},
        compare="value",
        tolerance=0.0,
    ),
    # ------------------------------------------------------------------ grids
    Entry(
        word="sdata.number_grid", option="exactly=",
        ours="""
            grid = sdata.number_grid([[1, "1/3"], ["a", 2]], exactly=True)
            str(grid.find_determinant())
        """,
        code={"SymPy": """
            import sympy as sp
            a = sp.Symbol("a")
            # number_grid([[1, "1/3"], ["a", 2]], exactly=True), then grid.find_determinant()
            grid = sp.Matrix([[1, sp.Rational(1, 3)], [a, 2]])   # (1)
            str(grid.det())
        """},
        compare="value",
        choices=("a typed decimal is the exact fraction it stands for (0.2 is 1/5), as in the other exact words.",),
        also="simplydata also refuses grids above 12 x 12, and grid.find_value_at(a=2) gives a grid of decimals.",
    ),
    Entry(
        word="grid.find_permanent",
        ours="""
            grid = sdata.number_grid([[1, 2], [3, 4]])
            grid.find_permanent()
        """,
        code={"SymPy": """
            import sympy as sp
            # grid.find_permanent()
            float(sp.Matrix([[1, 2], [3, 4]]).per())   # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("the numbers as exact fractions (SciPy and NumPy have no permanent), so the answer has no rounding "
                 "on the way.",),
    ),
    Entry(
        word="grid.find_permanent", option="exactly=",
        ours="""
            grid = sdata.number_grid([[0.5, 1], [1, 2]])
            str(grid.find_permanent(exactly=True))
        """,
        code={"SymPy": """
            import sympy as sp
            # grid.find_permanent(exactly=True)
            str(sp.Matrix([[sp.Rational(1, 2), 1], [1, 2]]).per())
        """},
        compare="value",
    ),
    Entry(
        word="grid.make_columns_orthogonal",
        ours="""
            grid = sdata.number_grid([[1, 1], [1, 0]])
            grid.make_columns_orthogonal()
            grid.as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # grid.make_columns_orthogonal()
            columns = sp.GramSchmidt([sp.Matrix([1, 1]), sp.Matrix([1, 0])])
            sp.Matrix.hstack(*columns).evalf().tolist()
        """},
        compare="value",
        tolerance=1e-15,
    ),
    Entry(
        word="grid.make_columns_orthogonal", option="of_length_1=",
        ours="""
            grid = sdata.number_grid([[1, 1], [1, 0]])
            grid.make_columns_orthogonal(of_length_1=True)
            grid.as_numpy().tolist()
        """,
        code={"SymPy": """
            import sympy as sp
            # grid.make_columns_orthogonal(of_length_1=True)
            columns = sp.GramSchmidt([sp.Matrix([1, 1]), sp.Matrix([1, 0])], True)
            sp.Matrix.hstack(*columns).evalf().tolist()
        """},
        compare="value",
        tolerance=1e-15,
    ),
]
