"""Families for 100 %, batches 14-16 (approved by Manish 2026-11-28): SciPy optimize, integrate and interpolate (plan
section 2.6): the new test_method= values of find_where_smallest and solve, fit_curve(always=), find_best_pairing, the
new integrators of find_area_under and find_volume_under, find_path_between_ends, the new joined_by= values of
find_values_at, and curve_through_points with the words on a curve, each next to the SciPy code that does the same
job."""

from . import Entry

TOLD = "simplydata also says the method, whether the search settled and how many times the formula was worked out."
CURVE = """
    import numpy as np
    from scipy import interpolate
    x, y = [0, 5, 10, 20, 30, 40], [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
    spline = interpolate.make_interp_spline(x, y, k=3, bc_type="natural")   # (1)
"""
CURVE_OURS = "curve = sdata.curve_through_points(x=[0, 5, 10, 20, 30, 40], y=[8.1, 7.9, 6.2, 5.0, 4.4, 4.6])\n"
CURVE_CHOICE = ("the curve of curve_through_points: a cubic spline through every point with natural ends (no bend at "
                "the first and last point), as R splinefun(method = \"natural\").",)
SYSTEM = ["x = 0.5*cos(y)", "y = 0.5*sin(x)"]


def _solver(value, scipy_name, sign="+"):
    """The entry of one SciPy root solver as a test_method= value of solve."""
    gap = ("lambda v: np.array([v[0] - 0.5*np.cos(v[1]), v[1] - 0.5*np.sin(v[0])])" if sign == "+" else
           "lambda v: np.array([0.5*np.cos(v[1]) - v[0], 0.5*np.sin(v[0]) - v[1]])")
    side = "left minus right" if sign == "+" else "right minus left"
    return Entry(
        word="sdata.solve",
        option=f'test_method="{value}"',
        ours=f"""
            sdata.solve({SYSTEM!r}, start={{"x": 0, "y": 0}}, test_method="{value}")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import optimize
            # solve({SYSTEM!r}, start={{"x": 0, "y": 0}}, test_method="{value}")
            gaps = {gap}   # (1)
            found = optimize.root(gaps, [0, 0], method="{scipy_name}",
                                  options={{"fatol": 1e-12, "maxiter": 5000}})   # (2)
            {{"x": found.x[0], "y": found.x[1]}}
        """},
        compare="result",
        fields=("x", "y"),
        tolerance=1e-9,
        choices=(f"each equation as {side}" + (" (these methods take the Jacobian to be about minus 1, as for "
                                               "x = g(x))" if sign == "-" else "") + ".",
                 "a tight tolerance (fatol 1e-12) and up to 5000 steps; SciPy's own default stops at about 6e-6."),
        also="simplydata also checks that every equation holds at the answer (left minus right in the table) and "
             "says how many steps and evaluations the search took.",
    )


ENTRIES = [
    Entry(
        word="sdata.find_where_smallest",
        option='test_method="golden section"',
        ours="""
            sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], test_method="golden section")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import optimize
            # find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], test_method="golden section")
            f = lambda x: (x - 2)**2 + np.sin(5*x)
            xs = np.linspace(0, 5, 200)                                        # (1)
            best = int(np.argmin(f(xs)))
            found = optimize.minimize_scalar(f, bracket=(xs[best - 1], xs[best], xs[best + 1]),
                                             method="golden", options={"xtol": 1e-10, "maxiter": 10000})  # (2)
            {"x": found.x, "smallest value": found.fun}
        """},
        compare="result",
        fields=("x", "smallest value"),
        tolerance=1e-8,
        choices=("the lowest of 200 evenly spaced points and its two neighbours make the bracket, so the golden "
                 "sections stay inside between=.",
                 "a tolerance of 1e-10, as Brent's method in find_where_smallest (R optimize(tol = 1e-10))."),
        also=TOLD,
    ),
    Entry(
        word="sdata.find_where_smallest",
        option='test_method="grid search"',
        ours="""
            sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], search="whole range",
                                      test_method="grid search")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import optimize
            # find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], test_method="grid search")
            f = lambda v: (v[0] - 2)**2 + np.sin(5*v[0])
            corner = optimize.brute(f, [(0, 5)], Ns=20000, finish=None)        # (1)
            found = optimize.minimize(f, np.atleast_1d(corner), method="L-BFGS-B", bounds=[(0, 5)],
                                      options={"ftol": 1e-15, "gtol": 1e-10})  # (2)
            {"x": found.x[0], "smallest value": found.fun}
        """},
        compare="result",
        fields=("x", "smallest value"),
        tolerance=1e-9,
        choices=("about 20,000 grid points in all, shared evenly among the names (here one name, so 20,000).",
                 "then a local polish that keeps to between= (L-BFGS-B), as after DIRECT; SciPy brute's own finish "
                 "(fmin) may leave the range."),
        also=TOLD,
    ),
    Entry(
        word="sdata.find_where_smallest",
        option='test_method="newton conjugate gradient"',
        ours="""
            sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1},
                                      test_method="newton conjugate gradient")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import optimize
            # find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start=..., test_method="newton conjugate gradient")
            from scipy import differentiate
            f = lambda v: (1 - v[0])**2 + 100*(v[1] - v[0]**2)**2
            slopes = lambda v: differentiate.jacobian(f, np.asarray(v, dtype=float)).df   # (1)
            found = optimize.minimize(f, [-1.2, 1], method="Newton-CG", jac=slopes, hess="3-point",  # (2)
                                      options={"xtol": 1e-10, "maxiter": 10000})  # (3)
            {"x": found.x[0], "y": found.x[1]}
        """},
        compare="result",
        fields=("x", "y"),
        tolerance=1e-6,
        choices=("the slopes from scipy.differentiate.jacobian; Newton-CG needs slopes as a function and SciPy has "
                 "no default for them.",
                 "the bends by SciPy's central differences of those slopes (hess=\"3-point\"); SciPy's own default "
                 "is too rough to settle on a flat minimum.",
                 "a tight tolerance (xtol 1e-10) and up to 10,000 steps."),
        also=TOLD,
    ),
    Entry(
        word="sdata.find_where_smallest",
        option='test_method="truncated newton"',
        ours="""
            sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1},
                                      test_method="truncated newton")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import optimize
            # find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start=..., test_method="truncated newton")
            f = lambda v: (1 - v[0])**2 + 100*(v[1] - v[0]**2)**2
            found = optimize.minimize(f, [-1.2, 1], method="TNC", jac="3-point", options={   # (1)
                "xtol": 1e-12, "ftol": 1e-15, "gtol": 1e-10, "maxfun": 20000})   # (2)
            {"x": found.x[0], "y": found.x[1]}
        """},
        compare="result",
        fields=("x", "y"),
        tolerance=1e-6,
        choices=("the slopes by SciPy's central differences (jac=\"3-point\"); its default uses forward differences.",
                 "tight tolerances and up to 20,000 evaluations; TNC keeps to between= when it is given."),
        also=TOLD,
    ),
    Entry(
        word="sdata.solve",
        option='test_method="fixed point"',
        ours="""
            sdata.solve("x = cos(x)", start=1, test_method="fixed point")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import optimize
            # solve("x = cos(x)", start=1, test_method="fixed point")
            root = optimize.fixed_point(np.cos, 1.0, xtol=1e-12, maxiter=1000,
                                        method="del2")                          # (1)
            {"x": float(root)}
        """},
        compare="result",
        fields=("x",),
        tolerance=1e-10,
        choices=("Steffensen's acceleration (del2, SciPy's default) to a tolerance of 1e-12, as R uniroot(tol = "
                 "1e-12) in solve.",),
        also="simplydata also checks that the answer meets the equation and says how many times the right side was "
             "worked out.",
    ),
    _solver("broyden second", "broyden2"),
    _solver("diagonal broyden", "diagbroyden"),
    _solver("anderson mixing", "anderson"),
    _solver("newton-krylov", "krylov"),
    _solver("linear mixing", "linearmixing", sign="-"),
    _solver("exciting mixing", "excitingmixing", sign="-"),
    Entry(
        word="table.fit_curve",
        option="always=",
        ours="""
            table = sdata.table({"dose": [1, 2, 3, 4, 5, 6], "response": [1, 3, 2, 4, 3.5, 5]})
            table.fit_curve(x="dose", y="response", always="rising")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import optimize
            df = pd.DataFrame({"dose": [1, 2, 3, 4, 5, 6], "response": [1, 3, 2, 4, 3.5, 5]})
            # fit_curve(x="dose", y="response", always="rising")
            df = df.sort_values("dose", kind="stable")                            # (1)
            df["fitted response"] = optimize.isotonic_regression(df["response"]).x
            df
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the rows in the order of x, ties kept in the order of the rows, as R isoreg().",),
        also="simplydata also says how many levels the curve has and the sum of squared distances.",
    ),
    Entry(
        word="sdata.find_best_pairing",
        ours="""
            pairs = sdata.find_best_pairing(sdata.number_grid([[4, 1, 3], [2, 0, 5], [3, 2, 2]]))
            pairs
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import optimize
            # find_best_pairing([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
            costs = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]], dtype=float)
            rows, columns = optimize.linear_sum_assignment(costs)                  # (1)
            pd.DataFrame({"row": [str(i + 1) for i in rows], "column": [str(j + 1) for j in columns],
                          "cost": costs[rows, columns]})                          # (2)
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the exact answer of the linear assignment problem (shortest augmenting path), as R "
                 "lpSolve::lp.assign().",
                 "rows and columns named 1, 2, 3 ... (or by the table's names), not counted from 0."),
        also="simplydata also prints the pairs and the total, says which rows or columns stay free, and takes empty "
             "cells as pairs that are not allowed.",
    ),
    Entry(
        word="sdata.find_best_pairing",
        option="with_distances=",
        ours="""
            flows = sdata.number_grid([[0, 5, 2], [5, 0, 3], [2, 3, 0]])
            distances = sdata.number_grid([[0, 8, 15], [8, 0, 13], [15, 13, 0]])
            sdata.find_best_pairing(flows, with_distances=distances)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import optimize
            # find_best_pairing(flows, with_distances=distances)
            flows = [[0, 5, 2], [5, 0, 3], [2, 3, 0]]
            distances = [[0, 8, 15], [8, 0, 13], [15, 13, 0]]
            found = optimize.quadratic_assignment(flows, distances, method="faq")  # (1)
            pd.DataFrame({"item": ["1", "2", "3"], "place": [str(p + 1) for p in found.col_ind]})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the Fast Approximate QAP method (Vogelstein et al. 2015), SciPy's default; test_method=\"2-opt\" "
                 "swaps places instead.",),
        also="simplydata also prints the total of flow times distance and says that the answer is a good one, not "
             "one proven to be the best.",
    ),
    Entry(
        word="sdata.find_area_under",
        option='test_method="tanh-sinh"',
        ours="""
            sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="tanh-sinh")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import integrate
            # find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="tanh-sinh")
            integrate.tanhsinh(lambda x: np.exp(-x**2), 0, np.inf).integral
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also prints the error estimate and SciPy's notes.",
    ),
    Entry(
        word="sdata.find_area_under",
        option='test_method="cubature"',
        ours="""
            sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="cubature")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import integrate
            # find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="cubature")
            integrate.cubature(lambda x: np.exp(-x[:, 0]**2), [0], [np.inf]).estimate
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also prints the error estimate, and a note when cubature did not reach its tolerance.",
    ),
    Entry(
        word="sdata.find_area_under",
        option='test_method="quasi monte carlo"',
        ours="""
            sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="quasi monte carlo")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import integrate, stats
            # find_area_under("exp(-x**2)", between=[0, 2], test_method="quasi monte carlo")
            engine = stats.qmc.Halton(1, rng=1)                                   # (1)
            integrate.qmc_quad(lambda x: np.exp(-x[0]**2), [0], [2], qrng=engine).integral
        """},
        compare="value",
        tolerance=1e-12,
        choices=("scrambled Halton points with_seed=1, so the same call gives the same estimate.",),
        also="simplydata also prints the standard error of the estimate.",
    ),
    Entry(
        word="sdata.find_area_under",
        option='test_method="romberg on even steps"',
        ours="""
            sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="romberg on even steps")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import integrate
            # find_area_under("exp(-x**2)", between=[0, 2], test_method="romberg on even steps")
            xs = np.linspace(0, 2, 2**10 + 1)                                     # (1)
            integrate.romb(np.exp(-xs**2), dx=2 / 2**10)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("1025 evenly spaced points (2**10 + 1, as romb needs).",),
        also="simplydata also says that romb gives no error estimate.",
    ),
    Entry(
        word="sdata.find_volume_under",
        option='test_method="cubature"',
        ours="""
            sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]}, test_method="cubature")
        """,
        code={"SciPy": """
            from scipy import integrate
            # find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]}, test_method="cubature")
            integrate.cubature(lambda p: p[:, 0] * p[:, 1], [0, 0], [1, 2]).estimate
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also prints the error estimate.",
    ),
    Entry(
        word="sdata.find_volume_under",
        option='test_method="quasi monte carlo"',
        ours="""
            sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]}, test_method="quasi monte carlo")
        """,
        code={"SciPy": """
            from scipy import integrate, stats
            # find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]}, test_method="quasi monte carlo")
            engine = stats.qmc.Halton(2, rng=1)                                   # (1)
            integrate.qmc_quad(lambda p: p[0] * p[1], [0, 0], [1, 2], qrng=engine).integral
        """},
        compare="value",
        tolerance=1e-12,
        choices=("scrambled Halton points with_seed=1.",),
        also="simplydata also prints the standard error of the estimate.",
    ),
    Entry(
        word="sdata.find_path_between_ends",
        ours="""
            path = sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5])
            path
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import integrate
            # find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5])
            x = np.linspace(0, 1.5, 101)                                          # (1)
            guess = np.vstack([x / 1.5, np.full_like(x, 1 / 1.5)])                # (2)
            found = integrate.solve_bvp(lambda x, y: np.vstack([y[1], -y[0]]), lambda a, b: np.array([a[0], b[0] - 1]),
                                        x, guess, tol=1e-8, max_nodes=100000)    # (3)
            values = found.sol(x)
            pd.DataFrame({"x": x, "y": values[0], "dy/dx": values[1]})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("101 evenly spaced places in the table (step= chooses others).",
                 "the first guess: a straight line between the known ends.",
                 "a tolerance of 1e-8 (SciPy's own default is 1e-3), as R bvpSolve's 1e-6 or tighter."),
        also="simplydata also turns the second-order equation into two first-order ones and says whether the "
             "collocation settled, after how many steps and on how many points.",
    ),
    Entry(
        word="table.find_values_at",
        option='joined_by="polynomial"',
        ours="""
            table = sdata.table({"year": [2000, 2002, 2004, 2006, 2008], "population": [10, 11, 13, 14, 13]})
            table.find_values_at("population", at={"year": [2001, 2003, 2007]}, joined_by="polynomial")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import interpolate
            # find_values_at("population", at={"year": [2001, 2003, 2007]}, joined_by="polynomial")
            curve = interpolate.BarycentricInterpolator([2000, 2002, 2004, 2006, 2008], [10, 11, 13, 14, 13])
            pd.DataFrame({"year": [2001, 2003, 2007], "population": curve([2001, 2003, 2007])})
        """},
        compare="table",
        tolerance=1e-9,
        also="simplydata also averages several values at one place first and leaves places outside the points empty.",
    ),
    Entry(
        word="table.find_values_at",
        option='joined_by="rational curve"',
        ours="""
            table = sdata.table({"year": [2000, 2002, 2004, 2006, 2008], "population": [10, 11, 13, 14, 13]})
            table.find_values_at("population", at={"year": [2001, 2003, 2007]}, joined_by="rational curve")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import interpolate
            # find_values_at("population", at={"year": [2001, 2003, 2007]}, joined_by="rational curve")
            curve = interpolate.FloaterHormannInterpolator([2000, 2002, 2004, 2006, 2008],
                                                           [10, 11, 13, 14, 13], d=3)   # (1)
            pd.DataFrame({"year": [2001, 2003, 2007], "population": curve([2001, 2003, 2007])})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("degree 3 (d=3, SciPy's default), or one less than the number of points when there are fewer.",),
        also="simplydata also averages several values at one place first and leaves places outside the points empty.",
    ),
    Entry(
        word="table.find_values_at",
        option='joined_by="aaa"',
        ours="""
            table = sdata.table({"year": [2000, 2002, 2004, 2006, 2008], "population": [10, 11, 13, 14, 13]})
            table.find_values_at("population", at={"year": [2001, 2003, 2007]}, joined_by="aaa")
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import interpolate
            # find_values_at("population", at={"year": [2001, 2003, 2007]}, joined_by="aaa")
            curve = interpolate.AAA([2000, 2002, 2004, 2006, 2008], [10, 11, 13, 14, 13])
            pd.DataFrame({"year": [2001, 2003, 2007], "population": np.real(curve([2001, 2003, 2007]))})  # (1)
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the real part of the AAA curve (SciPy gives complex numbers).",),
        also="simplydata also averages several values at one place first and leaves places outside the points empty.",
    ),
    Entry(
        word="table.find_values_at",
        option='joined_by="smooth triangles"',
        ours="""
            table = sdata.table({"east": [0, 1, 0, 1, 0.5, 0.2], "north": [0, 0, 1, 1, 0.5, 0.7],
                                 "height": [1, 2, 3, 4, 2.5, 3.1]})
            table.find_values_at("height", at={"east": [0.3, 0.6], "north": [0.4, 0.2]}, joined_by="smooth triangles")
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import interpolate
            # find_values_at("height", at={"east": [0.3, 0.6], "north": [0.4, 0.2]}, joined_by="smooth triangles")
            points = np.array([[0, 0], [1, 0], [0, 1], [1, 1], [0.5, 0.5], [0.2, 0.7]])
            surface = interpolate.CloughTocher2DInterpolator(points, [1, 2, 3, 4, 2.5, 3.1], tol=1e-12,
                                                             maxiter=10000)   # (1)
            pd.DataFrame({"east": [0.3, 0.6], "north": [0.4, 0.2], "height": surface([[0.3, 0.4], [0.6, 0.2]])})
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the slopes at the points, which Clough-Tocher finds step by step, to a tolerance of 1e-12 (SciPy's "
                 "default is 1e-6, at which the order of the points changes the last digits).",),
        also="simplydata also counts the places outside the outline of the points (left empty, or the nearest point's "
             "value with outside=\"nearest end\").",
    ),
    # ------------------------------------------------------------------ batch 16: curve_through_points (G6)
    Entry(
        word="sdata.curve_through_points",
        ours=CURVE_OURS + "curve.find_value_at(12)",
        code={"SciPy": CURVE + """
    # curve_through_points(x=..., y=...), then curve.find_value_at at 12
    float(spline(12))
"""},
        compare="value",
        tolerance=1e-12,
        choices=CURVE_CHOICE,
        also="simplydata also prints how the curve was made and leaves places outside the points empty.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="smoothness=",
        ours=CURVE_OURS.replace(")\n", ", smoothness=0.01)\n") + "curve.find_value_at(12)",
        code={"SciPy": """
            import numpy as np
            from scipy import interpolate
            # curve_through_points(x=..., y=..., smoothness=0.01), then curve.find_value_at at 12
            x, y = np.array([0, 5, 10, 20, 30, 40]), [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
            spline = interpolate.make_smoothing_spline(x / 40, y, lam=0.01)          # (1)
            float(spline(12 / 40))
        """},
        compare="value",
        tolerance=1e-12,
        choices=("x rescaled to run from 0 to 1, so smoothness= is R smooth.spline's lambda, as in find_values_at.",),
        also="simplydata also lets smoothness=\"auto\" ask R for lambda (generalised cross-validation).",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="allowed_error=",
        ours=CURVE_OURS.replace(")\n", ", allowed_error=0.5)\n") + "curve.find_value_at(12)",
        code={"SciPy": """
            from scipy import interpolate
            # curve_through_points(x=..., y=..., allowed_error=0.5), then curve.find_value_at at 12
            x, y = [0, 5, 10, 20, 30, 40], [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
            spline = interpolate.make_splrep(x, y, s=0.5, k=3)
            float(spline(12))
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also prints how many inner knots were needed and the sum of squared distances reached.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="knots=",
        ours=CURVE_OURS.replace(")\n", ", knots=[15])\n") + "curve.find_value_at(12)",
        code={"SciPy": """
            from scipy import interpolate
            # curve_through_points(x=..., y=..., knots=[15]), then curve.find_value_at at 12
            x, y = [0, 5, 10, 20, 30, 40], [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
            t = [0, 0, 0, 0, 15, 40, 40, 40, 40]                                    # (1)
            float(interpolate.make_lsq_spline(x, y, t, k=3)(12))
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the inner knots with the first and last x repeated degree + 1 times at the ends, as "
                 "splines::bs() in R.",),
        also="simplydata also checks that the knots lie between the points and explains a knot that has no points.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="slopes=",
        ours=CURVE_OURS.replace(")\n", ", slopes=[0, 0, -0.2, -0.1, 0, 0])\n") + "curve.find_value_at(12)",
        code={"SciPy": """
            from scipy import interpolate
            # curve_through_points(x=..., y=..., slopes=[0, 0, -0.2, -0.1, 0, 0]), then curve.find_value_at at 12
            x, y = [0, 5, 10, 20, 30, 40], [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
            spline = interpolate.CubicHermiteSpline(x, y, [0, 0, -0.2, -0.1, 0, 0])
            float(spline(12))
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also sorts the points by x (with their slopes) first.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="degree=",
        ours=CURVE_OURS.replace(")\n", ", degree=5)\n") + "curve.find_value_at(12)",
        code={"SciPy": """
            from scipy import interpolate
            # curve_through_points(x=..., y=..., degree=5), then curve.find_value_at at 12
            x, y = [0, 5, 10, 20, 30, 40], [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
            spline = interpolate.make_interp_spline(x, y, k=5)                      # (1)
            float(spline(12))
        """},
        compare="value",
        tolerance=1e-12,
        choices=("SciPy's own ends for degrees other than 3 (not-a-knot for odd degrees); natural, clamped and "
                 "periodic ends are chosen with ends= for cubic splines.",),
        also="simplydata also says which ends were used.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="ends=",
        ours=CURVE_OURS.replace(")\n", ', ends="not-a-knot")\n') + "curve.find_value_at(12)",
        code={"SciPy": """
            from scipy import interpolate
            # curve_through_points(x=..., y=..., ends="not-a-knot"), then curve.find_value_at at 12
            x, y = [0, 5, 10, 20, 30, 40], [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
            float(interpolate.make_interp_spline(x, y, k=3, bc_type="not-a-knot")(12))
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also checks that a periodic curve starts and ends at the same value.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="weights=",
        ours=CURVE_OURS.replace(")\n", ", allowed_error=0.5, weights=[1, 1, 2, 2, 1, 1])\n") +
        "curve.find_value_at(12)",
        code={"SciPy": """
            from scipy import interpolate
            # curve_through_points(x=..., y=..., allowed_error=0.5, weights=[1, 1, 2, 2, 1, 1])
            x, y = [0, 5, 10, 20, 30, 40], [8.1, 7.9, 6.2, 5.0, 4.4, 4.6]
            spline = interpolate.make_splrep(x, y, s=0.5, k=3, w=[1, 1, 2, 2, 1, 1])
            float(spline(12))
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also refuses weights= for a curve through every point, which meets each point exactly.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="in_order=",
        ours="""
            curve = sdata.curve_through_points(x=[0, 1, 2, 1, 0], y=[0, 1, 0, -1, -0.2], in_order=True)
            curve.find_value_at([0, 0.5, 1])
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import interpolate
            # curve_through_points(x=..., y=..., in_order=True), then curve.find_value_at([0, 0.5, 1])
            spline, u = interpolate.make_splprep([[0, 1, 2, 1, 0], [0, 1, 0, -1, -0.2]], s=0, k=3)
            found = spline([0, 0.5, 1])
            pd.DataFrame({"fraction": [0, 0.5, 1], "x": found[0], "y": found[1]})
        """},
        compare="table",
        tolerance=1e-12,
        also="simplydata also checks that each fraction is between 0 and 1.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="z=",
        ours="""
            east = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
            north = [0, 1, 2, 3] * 4
            height = [e**2 + 2 * n for e, n in zip(east, north)]
            surface = sdata.curve_through_points(x=east, y=north, z=height)
            surface.find_value_at(1.5, 2.5)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import interpolate
            # curve_through_points(x=east, y=north, z=height), then surface.find_value_at(1.5, 2.5)
            east, north = np.arange(4.0), np.arange(4.0)
            grid = east[:, None]**2 + 2 * north[None, :]                           # (1)
            surface = interpolate.RectBivariateSpline(east, north, grid, kx=3, ky=3, s=0)
            float(surface.ev(1.5, 2.5))
        """},
        compare="value",
        tolerance=1e-12,
        choices=("points that form a full grid go to RectBivariateSpline (scattered points to "
                 "SmoothBivariateSpline).",),
        also="simplydata also finds out whether the points form a full grid and says which spline it used.",
    ),
    Entry(
        word="sdata.curve_through_points",
        option="on_sphere=",
        ours="""
            latitude = [-30, -30, -30, -30, 0, 0, 0, 0, 30, 30, 30, 30, 60, 60, 60, 60]
            longitude = [0, 90, 180, 270] * 4
            values = [1.0, 1.5, 2.0, 1.5, 2.0, 2.5, 3.0, 2.5, 1.0, 1.5, 2.0, 1.5, 0.5, 1.0, 1.5, 1.0]
            surface = sdata.curve_through_points(x=latitude, y=longitude, z=values, on_sphere=True)
            surface.find_value_at(10, 100)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import interpolate
            # curve_through_points(x=latitude, y=longitude, z=values, on_sphere=True), then find_value_at(10, 100)
            theta = np.radians(90 - np.array([60, 30, 0, -30]))                   # (1)
            phi = np.radians([0, 90, 180, 270]) - np.pi                            # (2)
            grid = np.array([[1.0, 1.5, 2.0, 1.5], [2.0, 2.5, 3.0, 2.5], [1.0, 1.5, 2.0, 1.5], [0.5, 1.0, 1.5, 1.0]])
            surface = interpolate.RectSphereBivariateSpline(theta, phi, grid[::-1], s=0)
            float(surface.ev(np.radians(80), np.radians(100) - np.pi))
        """},
        compare="value",
        tolerance=1e-10,
        choices=("latitude in degrees turned into SciPy's colatitude in radians (90 degrees minus the latitude).",
                 "longitude in degrees turned into radians from -pi to pi, as RectSphereBivariateSpline needs."),
        also="simplydata also chooses the spline for scattered points on a sphere (SmoothSphereBivariateSpline).",
    ),
    Entry(
        word="curve.find_value_at",
        ours=CURVE_OURS + "curve.find_value_at([1, 12, 35])",
        code={"SciPy": CURVE + """
    # curve.find_value_at([1, 12, 35])
    spline([1, 12, 35])
"""},
        compare="value",
        tolerance=1e-12,
        choices=CURVE_CHOICE,
        also="simplydata also leaves places outside the points empty, with a note.",
    ),
    Entry(
        word="curve.find_slope_at",
        ours=CURVE_OURS + "curve.find_slope_at(12)",
        code={"SciPy": CURVE + """
    # curve.find_slope_at at 12
    float(spline.derivative(1)(12))
"""},
        compare="value",
        tolerance=1e-12,
        choices=CURVE_CHOICE,
        also="simplydata also gives every slope at one place with order=\"all\" (as spalde).",
    ),
    Entry(
        word="curve.find_area_between",
        ours=CURVE_OURS + "curve.find_area_between(0, 20)",
        code={"SciPy": CURVE + """
    # curve.find_area_between(0, 20)
    float(spline.integrate(0, 20))
"""},
        compare="value",
        tolerance=1e-12,
        choices=CURVE_CHOICE,
        also="simplydata also refuses an area beyond the points (guesswork).",
    ),
    Entry(
        word="curve.find_zeros",
        ours=CURVE_OURS + "curve.find_zeros(where_value_is=5)",
        code={"SciPy": CURVE + """
    # curve.find_zeros(where_value_is=5)
    interpolate.PPoly.from_spline(spline, extrapolate=False).solve(5, extrapolate=False)
"""},
        compare="value",
        tolerance=1e-10,
        choices=CURVE_CHOICE,
        also="simplydata also keeps each place once and says when the curve never gets there.",
    ),
    Entry(
        word="curve.turn_into_slope_curve",
        ours=CURVE_OURS + "slopes = curve.turn_into_slope_curve()\nslopes.find_value_at(12)",
        code={"SciPy": CURVE + """
    # curve.turn_into_slope_curve(), then find_value_at at 12
    float(spline.derivative()(12))
"""},
        compare="value",
        tolerance=1e-12,
        choices=CURVE_CHOICE,
        also="simplydata also says the degree of the new curve.",
    ),
    Entry(
        word="curve.turn_into_area_curve",
        ours=CURVE_OURS + "areas = curve.turn_into_area_curve()\nareas.find_value_at(20)",
        code={"SciPy": CURVE + """
    # curve.turn_into_area_curve(), then find_value_at at 20
    area = spline.antiderivative()
    float(area(20) - area(0))                                              # (2)
"""},
        compare="value",
        tolerance=1e-12,
        choices=CURVE_CHOICE + ("the area curve starts at 0 at the first point.",),
        also="simplydata also says the degree of the new curve.",
    ),
    Entry(
        word="curve.show_pieces",
        ours=CURVE_OURS + "curve.show_pieces()",
        code={"SciPy": CURVE + """
    import pandas as pd
    # curve.show_pieces()
    pieces = interpolate.PPoly.from_spline(spline)
    keep = np.diff(pieces.x) > 0                                           # (2)
    c = pieces.c[:, keep]
    pd.DataFrame({"from": pieces.x[:-1][keep], "to": pieces.x[1:][keep], "constant": c[3], "(x - from)": c[2],
                  "(x - from)**2": c[1], "(x - from)**3": c[0]})
"""},
        compare="table",
        tolerance=1e-10,
        choices=CURVE_CHOICE + ("pieces of no width (the repeated knots at the ends) are left out.",),
        also="simplydata also gives the pieces in the Bernstein basis (basis=\"bernstein\", SciPy BPoly).",
    ),
    Entry(
        word="curve.show_knots",
        ours=CURVE_OURS + "curve.show_knots()",
        code={"SciPy": CURVE + """
    import pandas as pd
    # curve.show_knots()
    coefficients = list(spline.c) + [np.nan] * (len(spline.t) - len(spline.c))   # (2)
    pd.DataFrame({"knot": spline.t, "coefficient": coefficients})
"""},
        compare="table",
        tolerance=1e-12,
        choices=CURVE_CHOICE + ("one table: the coefficients run out before the knots (there are degree + 1 fewer), "
                                "so the last cells are empty.",),
        also="simplydata also prints the degree and the counts.",
    ),
    Entry(
        word="curve.as_scipy",
        ours=CURVE_OURS + "spline = curve.as_scipy()\nfloat(spline(12))",
        code={"SciPy": CURVE + """
    # curve.as_scipy(), then spline at 12
    float(spline(12))
"""},
        compare="value",
        tolerance=1e-12,
        choices=CURVE_CHOICE,
        also="simplydata hands over the same SciPy object, with places outside the points empty (extrapolate=False).",
    ),
]
