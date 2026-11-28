"""The reliability study for the families for 100 % plan, batches 14-16 (approved by Manish 2026-11-28): SciPy optimize,
integrate and interpolate (plan section 2.6), each set up from real data (mtcars, stackloss, Lake Huron) or, for the
words that take a formula and no data (solve, the areas and volumes, find_path_between_ends), from a formula whose
answer is known in closed form or published, and compared with SciPy and, where R does the same in a few lines, with
R (optimize, optim, nleqslv, isoreg, lpSolve::lp.assign, integrate, cubature::hcubature, pracma::bvp,
pracma::barylag, splinefun, splinefunH, smooth.spline, splines::bs).

cases_underneath.py loads this file and adds the cases. The simplydata side reads its results only with simplydata
words (get_cell_at, get_column, get_number_at, find_total).
"""

from __future__ import annotations

import textwrap

MTCARS = dict(dataset="mtcars", kind="real data")
HURON = dict(dataset="Lake Huron", kind="real data")
CLOSED = dict(dataset="closed form (no data)", kind="closed form")
# the normal log-likelihood of mtcars mpg, up to a constant: its smallest value is at the average and at the
# standard deviation with n in the bottom (the maximum likelihood estimates), so every optimiser has a known answer
LIKELIHOOD = """
    n = len(data); m = data["mpg"].mean(); q = ((data["mpg"] - m) ** 2).sum()
    formula = "n*log(s) + (q + n*(m - mu)**2)/(2*s**2)"
    known = {"n": n, "q": q, "m": m}
"""
SYSTEM = ["x = 0.5*y**2 + 0.375", "y = 0.5*x**2 + 0.375"]  # x = y = 1 - sqrt(1/4) = 0.5 (the root nearer 0)
# the Lake Huron levels every 10 years (1875 to 1965): points far enough apart for a curve through them
EVERY_10 = 'data = data[data["year"] % 10 == 5]\n'
CURVE_R = "f <- splinefun(year[year %% 10 == 5], level[year %% 10 == 5], method = 'natural')\n"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts if part and part.strip())


def _curve(extra: str = "") -> str:
    return _code(EVERY_10, f'curve = sdata.curve_through_points(x=data["year"], y=data["level"]{extra})')


def _scipy_curve(make: str) -> str:
    return _code("""
        from scipy import interpolate
        d = data[data["year"] % 10 == 5]
        x, y = d["year"].to_numpy(float), d["level"].to_numpy(float)
    """, make)


def _solver_case(Case, value, scipy_name, sign):
    gaps = ("np.array([v[0] - 0.5*v[1]**2 - 0.375, v[1] - 0.5*v[0]**2 - 0.375])" if sign > 0 else
            "np.array([0.5*v[1]**2 + 0.375 - v[0], 0.5*v[0]**2 + 0.375 - v[1]])")
    return Case("sdata.solve", f"x = 0.5 y**2 + 0.375 and y = 0.5 x**2 + 0.375 by SciPy's {scipy_name} (x = y = 0.5, "
                "worked out by hand)", option=f'test_method="{value}"', **CLOSED,
                ours=f"""
                    r = sdata.solve({SYSTEM!r}, start={{"x": 0, "y": 0}}, test_method="{value}")
                    {{"x": r.get_cell_at(row=1, column="x"), "y": r.get_cell_at(row=1, column="y")}}
                """,
                published={"x": (0.5, 1e-9, "worked out: x = y = 1 - sqrt(1 - 2 * 0.375)"),
                           "y": (0.5, 1e-9, "worked out: x = y = 1 - sqrt(1 - 2 * 0.375)")},
                parent=f"""
                    from scipy import optimize
                    r = optimize.root(lambda v: {gaps}, [0, 0], method="{scipy_name}",
                                      options={{"fatol": 1e-12, "maxiter": 5000}})
                    {{"x": r.x[0], "y": r.x[1]}}
                """, parent_label=f"SciPy optimize.root(method=\"{scipy_name}\")", parent_tolerance=1e-9,
                r="""
                    f <- function(v) c(v[1] - 0.5*v[2]^2 - 0.375, v[2] - 0.5*v[1]^2 - 0.375)
                    s <- nleqslv::nleqslv(c(0, 0), f, method = "Broyden", control = list(ftol = 1e-12, xtol = 1e-12))$x
                    list(x = s[1], y = s[2])
                """, r_packages=("nleqslv",), r_tolerance=1e-9,
                note="Every SciPy root solver goes to the same root; R nleqslv (Broyden's method) checks it.")


def cases(Case):
    return [
        # ---------------------------------------------------------------- batch 14: find_where_smallest
        Case("sdata.find_where_smallest", "mtcars: the standard deviation of mpg that fits best (normal likelihood, "
             "golden-section search)", option='test_method="golden section"', **MTCARS,
             ours=_code("""
                 n = len(data); q = ((data["mpg"] - data["mpg"].mean()) ** 2).sum()
                 r = sdata.find_where_smallest("n*log(s) + q/(2*s**2)", between=[1, 20], known={"n": n, "q": q},
                                               test_method="golden section")
                 {"s": r.get_cell_at(row=1, column="s")}
             """),
             parent="""
                 {"s": data["mpg"].std(ddof=0)}
             """, parent_label="NumPy standard deviation with n in the bottom (the closed-form answer)",
             parent_tolerance=1e-7,
             r="""
                 n <- length(mpg); q <- sum((mpg - mean(mpg))^2)
                 list(s = optimize(function(s) n*log(s) + q/(2*s^2), c(1, 20), tol = 1e-10)$minimum)
             """, r_tolerance=1e-7,
             note="R optimize() is Brent's method (golden sections with parabolic steps); both reach the closed form. "
                  "A smallest value can be placed only to about the square root of the machine precision (about "
                  "1e-8 here), where the curve is flat to the last digit."),
        Case("sdata.find_where_smallest", "mtcars: the average and standard deviation of mpg that fit best, by a "
             "grid search over the whole range", option='test_method="grid search"', **MTCARS,
             ours=_code(LIKELIHOOD, """
                 r = sdata.find_where_smallest(formula, between={"mu": [10, 30], "s": [1, 15]}, known=known,
                                               search="whole range", test_method="grid search")
                 {"mu": r.get_cell_at(row=1, column="mu"), "s": r.get_cell_at(row=1, column="s")}
             """),
             parent="""
                 {"mu": data["mpg"].mean(), "s": data["mpg"].std(ddof=0)}
             """, parent_label="the closed-form maximum likelihood estimates (NumPy)", parent_tolerance=1e-7,
             r="""
                 n <- length(mpg); m <- mean(mpg); q <- sum((mpg - m)^2)
                 f <- function(p) n*log(p[2]) + (q + n*(m - p[1])^2)/(2*p[2]^2)
                 o <- optim(c(20, 5), f, method = "L-BFGS-B", lower = c(10, 1), upper = c(30, 15),
                            control = list(factr = 1, pgtol = 1e-12))
                 list(mu = o$par[1], s = o$par[2])
             """, r_tolerance=1e-6),
        *[Case("sdata.find_where_smallest", f"mtcars: the average and standard deviation of mpg that fit best, by "
               f"{value}", option=f'test_method="{value}"', **MTCARS,
               ours=_code(LIKELIHOOD, f"""
                   r = sdata.find_where_smallest(formula, start={{"mu": 15, "s": 4}}, known=known,
                                                 test_method="{value}")
                   {{"mu": r.get_cell_at(row=1, column="mu"), "s": r.get_cell_at(row=1, column="s")}}
               """),
               parent="""
                   {"mu": data["mpg"].mean(), "s": data["mpg"].std(ddof=0)}
               """, parent_label="the closed-form maximum likelihood estimates (NumPy)", parent_tolerance=1e-6,
               r="""
                   n <- length(mpg); m <- mean(mpg); q <- sum((mpg - m)^2)
                   f <- function(p) n*log(p[2]) + (q + n*(m - p[1])^2)/(2*p[2]^2)
                   o <- optim(c(15, 4), f, method = "BFGS", control = list(reltol = 1e-14))
                   list(mu = o$par[1], s = o$par[2])
               """, r_tolerance=1e-6)
          for value in ("newton conjugate gradient", "truncated newton")],
        # ---------------------------------------------------------------- batch 14: solve
        Case("sdata.solve", "x = cos(x): the Dottie number (OEIS A003957)", option='test_method="fixed point"',
             dataset="closed form (no data)", kind="closed form",
             ours="""
                 r = sdata.solve("x = cos(x)", start=1, test_method="fixed point")
                 {"x": r.get_cell_at(row=1, column="x")}
             """,
             published={"x": (0.7390851332151607, 1e-12, "OEIS A003957 (the Dottie number)")},
             parent="""
                 from scipy import optimize
                 {"x": float(optimize.fixed_point(np.cos, 1.0, xtol=1e-12, method="del2"))}
             """, parent_label="SciPy optimize.fixed_point", parent_tolerance=1e-12,
             r="""
                 list(x = uniroot(function(x) x - cos(x), c(0, 1), tol = 1e-14)$root)
             """, r_tolerance=1e-10),
        *[_solver_case(Case, value, scipy_name, sign) for value, scipy_name, sign in (
            ("broyden second", "broyden2", 1), ("diagonal broyden", "diagbroyden", 1),
            ("anderson mixing", "anderson", 1), ("newton-krylov", "krylov", 1),
            ("linear mixing", "linearmixing", -1), ("exciting mixing", "excitingmixing", -1))],
        # ---------------------------------------------------------------- batch 14: fit_curve(always=), pairing
        Case("table.fit_curve", "mtcars: miles per gallon as a curve that only falls with horsepower (isotonic "
             "regression)", option="always=", **MTCARS,
             ours="""
                 r = sdata.table(data).fit_curve(x="hp", y="mpg", always="falling")
                 fitted = r.get_column("fitted mpg")
                 {"first": fitted.get_number_at(1), "last": fitted.get_number_at(32), "total": fitted.find_total()}
             """,
             parent="""
                 from scipy import optimize
                 d = data.sort_values("hp", kind="stable")
                 f = optimize.isotonic_regression(d["mpg"].to_numpy(float), increasing=False).x
                 {"first": f[0], "last": f[-1], "total": f.sum()}
             """, parent_label="SciPy optimize.isotonic_regression", parent_tolerance=1e-12,
             r="""
                 f <- -isoreg(hp, -mpg)$yf
                 list(first = f[1], last = f[32], total = sum(f))
             """, r_tolerance=1e-12,
             note="R isoreg() fits a curve that rises; minus the fit to minus mpg is the curve that falls."),
        Case("sdata.find_best_pairing", "mtcars: each of 6 cars paired with one of 6 others of the closest weight and "
             "power (the smallest total gap)", **MTCARS,
             ours=_code("""
                 a, b = data.iloc[:6], data.iloc[6:12]
                 costs = [[abs(i.wt - j.wt) + abs(i.hp - j.hp) / 100 for j in b.itertuples()] for i in a.itertuples()]
                 r = sdata.find_best_pairing(costs)
                 {"total": r.get_column("cost").find_total(), "pairs": r.count_rows()}
             """),
             parent="""
                 from scipy import optimize
                 a, b = data.iloc[:6], data.iloc[6:12]
                 c = np.array([[abs(i.wt - j.wt) + abs(i.hp - j.hp) / 100 for j in b.itertuples()]
                               for i in a.itertuples()])
                 rows, cols = optimize.linear_sum_assignment(c)
                 {"total": c[rows, cols].sum(), "pairs": len(rows)}
             """, parent_label="SciPy optimize.linear_sum_assignment", parent_tolerance=1e-12,
             r="""
                 c <- outer(wt[1:6], wt[7:12], function(i, j) abs(i - j)) +
                      outer(hp[1:6], hp[7:12], function(i, j) abs(i - j)) / 100
                 list(total = lpSolve::lp.assign(c)$objval, pairs = 6)
             """, r_packages=("lpSolve",), r_tolerance=1e-9),
        Case("sdata.find_best_pairing", "mtcars: 6 cars placed at 6 places, the flow between cars their horsepower "
             "gap and the distance between places their weight gap (quadratic assignment)",
             option="with_distances=", **MTCARS,
             ours=_code("""
                 hp, wt = data["hp"].to_numpy(float)[:6], data["wt"].to_numpy(float)[6:12]
                 flows = [[abs(i - j) for j in hp] for i in hp]
                 distances = [[abs(i - j) for j in wt] for i in wt]
                 r = sdata.find_best_pairing(flows, with_distances=distances)
                 {"first place": float(r.get_cell_at(row=1, column="place")), "items": r.count_rows()}
             """),
             parent="""
                 from scipy import optimize
                 hp, wt = data["hp"].to_numpy(float)[:6], data["wt"].to_numpy(float)[6:12]
                 r = optimize.quadratic_assignment(np.abs(hp[:, None] - hp), np.abs(wt[:, None] - wt), method="faq")
                 {"first place": r.col_ind[0] + 1.0, "items": 6}
             """, parent_label="SciPy optimize.quadratic_assignment (FAQ)", parent_tolerance=0.0,
             note="The quadratic assignment problem is hard, so there is no exact answer to compare with; R has no "
                  "common equivalent. The check is that simplydata makes SciPy's call."),
        # ---------------------------------------------------------------- batch 15: areas and volumes (no data)
        Case("sdata.find_area_under", "the area under exp(-x**2) from 0 to infinity (half the square root of pi), by "
             "tanh-sinh quadrature", option='test_method="tanh-sinh"', **CLOSED,
             ours="""
                 {"area": sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="tanh-sinh")}
             """,
             published={"area": (0.8862269254527580, 1e-12, "worked out: sqrt(pi) / 2")},
             parent="""
                 from scipy import integrate
                 {"area": integrate.tanhsinh(lambda x: np.exp(-x**2), 0, np.inf).integral}
             """, parent_label="SciPy integrate.tanhsinh", parent_tolerance=1e-14,
             r="""
                 list(area = integrate(function(x) exp(-x^2), 0, Inf, rel.tol = 1e-12)$value)
             """, r_tolerance=1e-10),
        Case("sdata.find_area_under", "the area under exp(-x**2) from 0 to infinity, by cubature",
             option='test_method="cubature"', **CLOSED,
             ours="""
                 {"area": sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="cubature")}
             """,
             published={"area": (0.8862269254527580, 1e-9, "worked out: sqrt(pi) / 2")},
             parent="""
                 from scipy import integrate
                 {"area": integrate.cubature(lambda x: np.exp(-x[:, 0]**2), [0], [np.inf]).estimate}
             """, parent_label="SciPy integrate.cubature", parent_tolerance=1e-14,
             r="""
                 list(area = cubature::hcubature(function(x) exp(-x^2), 0, 50, tol = 1e-12)$integral)
             """, r_packages=("cubature",), r_tolerance=1e-9,
             note="R hcubature takes finite ends: exp(-x**2) is below 1e-1000 beyond 50, so 0 to 50 is the same area."),
        Case("sdata.find_area_under", "the area under exp(-x**2) from 0 to 2 (sqrt(pi) erf(2) / 2), by "
             "quasi-Monte Carlo", option='test_method="quasi monte carlo"', **CLOSED,
             ours="""
                 {"area": sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="quasi monte carlo")}
             """,
             published={"area": (0.8820813907624215, 1e-3, "worked out: sqrt(pi) erf(2) / 2")},
             parent="""
                 from scipy import integrate, stats
                 engine = stats.qmc.Halton(1, rng=1)
                 {"area": integrate.qmc_quad(lambda x: np.exp(-x[0]**2), [0], [2], qrng=engine).integral}
             """, parent_label="SciPy integrate.qmc_quad (Halton, seed 1)", parent_tolerance=1e-14,
             note="A quasi-Monte Carlo estimate: its standard error here is about 2e-4, so the worked answer is met to "
                  "1e-3."),
        Case("sdata.find_area_under", "the area under exp(-x**2) from 0 to 2, by Romberg's method on 1025 points",
             option='test_method="romberg on even steps"', **CLOSED,
             ours="""
                 {"area": sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="romberg on even steps")}
             """,
             published={"area": (0.8820813907624215, 1e-12, "worked out: sqrt(pi) erf(2) / 2")},
             parent="""
                 from scipy import integrate
                 xs = np.linspace(0, 2, 1025)
                 {"area": integrate.romb(np.exp(-xs**2), dx=2 / 1024)}
             """, parent_label="SciPy integrate.romb", parent_tolerance=1e-14,
             r="""
                 list(area = pracma::romberg(function(x) exp(-x^2), 0, 2, tol = 1e-14)$value)
             """, r_packages=("pracma",), r_tolerance=1e-12),
        Case("sdata.find_volume_under", "the volume under x * y**2 over [0, 1] by [0, 2] (4/3), by cubature",
             option='test_method="cubature"', **CLOSED,
             ours="""
                 {"volume": sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]},
                                                    test_method="cubature")}
             """,
             published={"volume": (4 / 3, 1e-12, "worked out: (1/2) (8/3)")},
             parent="""
                 from scipy import integrate
                 {"volume": integrate.cubature(lambda p: p[:, 0] * p[:, 1]**2, [0, 0], [1, 2]).estimate}
             """, parent_label="SciPy integrate.cubature", parent_tolerance=1e-14,
             r="""
                 list(volume = cubature::hcubature(function(p) p[1] * p[2]^2, c(0, 0), c(1, 2), tol = 1e-12)$integral)
             """, r_packages=("cubature",), r_tolerance=1e-10),
        Case("sdata.find_volume_under", "the volume under x * y**2 over [0, 1] by [0, 2] (4/3), by quasi-Monte Carlo",
             option='test_method="quasi monte carlo"', **CLOSED,
             ours="""
                 {"volume": sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]},
                                                    test_method="quasi monte carlo")}
             """,
             published={"volume": (4 / 3, 5e-3, "worked out: (1/2) (8/3)")},
             parent="""
                 from scipy import integrate, stats
                 engine = stats.qmc.Halton(2, rng=1)
                 {"volume": integrate.qmc_quad(lambda p: p[0] * p[1]**2, [0, 0], [1, 2], qrng=engine).integral}
             """, parent_label="SciPy integrate.qmc_quad (Halton, seed 1)", parent_tolerance=1e-14,
             note="A quasi-Monte Carlo estimate, met to its few digits."),
        Case("sdata.find_path_between_ends", "y'' = -y with y(0) = 0 and y(1.5) = 1: y = sin(x) / sin(1.5)",
             **CLOSED,
             ours="""
                 path = sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5])
                 {"y at 0.75": path.get_cell_at(row=51, column="y"),
                  "slope at 0": path.get_cell_at(row=1, column="dy/dx")}
             """,
             published={"y at 0.75": (0.6816387600233341 / 0.9974949866040544, 1e-8,
                                      "worked out: sin(0.75) / sin(1.5)"),
                        "slope at 0": (1 / 0.9974949866040544, 1e-7, "worked out: cos(0) / sin(1.5)")},
             parent="""
                 from scipy import integrate
                 x = np.linspace(0, 1.5, 101)
                 g = integrate.solve_bvp(lambda x, y: np.vstack([y[1], -y[0]]), lambda a, b: np.array([a[0], b[0] - 1]),
                                         x, np.vstack([x / 1.5, np.full_like(x, 1 / 1.5)]), tol=1e-8, max_nodes=100000)
                 {"y at 0.75": g.sol(0.75)[0], "slope at 0": g.sol(0.0)[1]}
             """, parent_label="SciPy integrate.solve_bvp", parent_tolerance=1e-10,
             r="""
                 s <- pracma::bvp(function(x) rep(0, length(x)), function(x) rep(-1, length(x)),
                                  function(x) rep(0, length(x)), c(0, 1.5), c(0, 1), n = 2999)
                 list(`y at 0.75` = s$ys[which.min(abs(s$xs - 0.75))])
             """, r_packages=("pracma",), r_tolerance=1e-6,
             note="R pracma::bvp solves y'' = f y' + g y + h by finite differences on 3001 points, accurate to about "
                  "1e-7 here."),
        # ---------------------------------------------------------------- batch 15: joined_by=
        Case("table.find_values_at", "Lake Huron every 10 years: the level in 1900 and 1950 from the one polynomial "
             "through the 10 points", option='joined_by="polynomial"', **HURON,
             ours=_code(EVERY_10, """
                 r = sdata.table(data).find_values_at("level", at={"year": [1900, 1950]}, joined_by="polynomial")
                 {"1900": r.get_cell_at(row=1, column="level"), "1950": r.get_cell_at(row=2, column="level")}
             """),
             parent=_scipy_curve("""
                 f = interpolate.BarycentricInterpolator(x, y)
                 {"1900": float(f(1900)), "1950": float(f(1950))}
             """), parent_label="SciPy interpolate.BarycentricInterpolator", parent_tolerance=1e-9,
             r="""
                 k <- year %% 10 == 5
                 v <- pracma::barylag(year[k], level[k], c(1900, 1950))
                 list(`1900` = v[1], `1950` = v[2])
             """, r_packages=("pracma",), r_tolerance=1e-8),
        Case("table.find_values_at", "Lake Huron every 10 years: the level in 1900 and 1950 from the Floater-Hormann "
             "rational curve", option='joined_by="rational curve"', **HURON,
             ours=_code(EVERY_10, """
                 r = sdata.table(data).find_values_at("level", at={"year": [1900, 1950]}, joined_by="rational curve")
                 {"1900": r.get_cell_at(row=1, column="level"), "1950": r.get_cell_at(row=2, column="level")}
             """),
             parent=_scipy_curve("""
                 f = interpolate.FloaterHormannInterpolator(x, y, d=3)
                 {"1900": float(f(1900)), "1950": float(f(1950))}
             """), parent_label="SciPy interpolate.FloaterHormannInterpolator", parent_tolerance=1e-10,
             note="R has no Floater-Hormann interpolation in a common package."),
        Case("table.find_values_at", "Lake Huron every 10 years: the level in 1900 and 1950 from the AAA rational "
             "curve", option='joined_by="aaa"', **HURON,
             ours=_code(EVERY_10, """
                 r = sdata.table(data).find_values_at("level", at={"year": [1900, 1950]}, joined_by="aaa")
                 {"1900": r.get_cell_at(row=1, column="level"), "1950": r.get_cell_at(row=2, column="level")}
             """),
             parent=_scipy_curve("""
                 f = interpolate.AAA(x, y)
                 {"1900": float(np.real(f(1900))), "1950": float(np.real(f(1950)))}
             """), parent_label="SciPy interpolate.AAA", parent_tolerance=1e-9,
             note="R has no AAA rational approximation in a common package."),
        Case("table.find_values_at", "stackloss: the stack loss at two settings of air flow and water temperature, "
             "on a smooth surface over the triangles between the 21 runs", option='joined_by="smooth triangles"',
             dataset="stackloss", kind="real data",
             ours="""
                 r = sdata.table(data).find_values_at("stack_loss", at={"air_flow": [60, 70], "water_temp": [20, 22]},
                                                      joined_by="smooth triangles")
                 {"first": r.get_cell_at(row=1, column="stack_loss"),
                  "second": r.get_cell_at(row=2, column="stack_loss")}
             """,
             parent="""
                 from scipy import interpolate
                 g = data.groupby(["air_flow", "water_temp"], as_index=False)["stack_loss"].mean()
                 f = interpolate.CloughTocher2DInterpolator(g[["air_flow", "water_temp"]].to_numpy(float),
                                                            g["stack_loss"].to_numpy(float), tol=1e-12, maxiter=10000)
                 v = f([[60, 20], [70, 22]])
                 {"first": v[0], "second": v[1]}
             """, parent_label="SciPy interpolate.CloughTocher2DInterpolator", parent_tolerance=1e-9,
             note="Runs at the same settings are averaged first, as find_values_at does. R interp::interp(linear = "
                  "FALSE) uses Akima's method on the triangles, so it gives other values."),
        # ---------------------------------------------------------------- batch 16: curve_through_points (G6)
        Case("sdata.curve_through_points", "Lake Huron every 10 years: the natural cubic spline at 1900 and 1950",
             **HURON,
             ours=_code(_curve(), '{"1900": curve.find_value_at(1900), "1950": curve.find_value_at(1950)}'),
             parent=_scipy_curve("""
                 f = interpolate.make_interp_spline(x, y, k=3, bc_type="natural")
                 {"1900": float(f(1900)), "1950": float(f(1950))}
             """), parent_label="SciPy make_interp_spline(bc_type=\"natural\")", parent_tolerance=1e-12,
             r=CURVE_R + "list(`1900` = f(1900), `1950` = f(1950))", r_tolerance=1e-10),
        Case("sdata.curve_through_points", "Lake Huron, all 98 years: the smoothing spline at lambda 0.001",
             option="smoothness=", **HURON,
             ours="""
                 curve = sdata.curve_through_points(x=data["year"], y=data["level"], smoothness=0.001)
                 {"1900": curve.find_value_at(1900), "1950": curve.find_value_at(1950)}
             """,
             parent="""
                 from scipy import interpolate
                 x, y = data["year"].to_numpy(float), data["level"].to_numpy(float)
                 f = interpolate.make_smoothing_spline((x - x[0]) / (x[-1] - x[0]), y, lam=0.001)
                 {"1900": float(f((1900 - x[0]) / (x[-1] - x[0]))), "1950": float(f((1950 - x[0]) / (x[-1] - x[0])))}
             """, parent_label="SciPy make_smoothing_spline on x rescaled to 0 to 1", parent_tolerance=1e-12,
             r="""
                 s <- smooth.spline(year, level, all.knots = TRUE, lambda = 0.001)
                 list(`1900` = predict(s, 1900)$y, `1950` = predict(s, 1950)$y)
             """, r_tolerance=1e-4,
             note="R solves the same penalised sum in a B-spline basis with its own rounding (about 1e-5 apart, as for "
                  "find_values_at(smoothness=))."),
        Case("sdata.curve_through_points", "Lake Huron, all 98 years: the fewest knots that keep the sum of squared "
             "distances at most 30", option="allowed_error=", **HURON,
             ours="""
                 curve = sdata.curve_through_points(x=data["year"], y=data["level"], allowed_error=30)
                 {"1900": curve.find_value_at(1900), "knots": curve.show_knots().count_rows()}
             """,
             parent="""
                 from scipy import interpolate
                 f = interpolate.make_splrep(data["year"].to_numpy(float), data["level"].to_numpy(float), s=30, k=3)
                 {"1900": float(f(1900)), "knots": len(f.t)}
             """, parent_label="SciPy make_splrep (FITPACK s)", parent_tolerance=1e-12,
             note="FITPACK's choice of knots has no R equivalent in base R."),
        Case("sdata.curve_through_points", "Lake Huron, all 98 years: a least-squares cubic spline with knots at "
             "1900, 1925 and 1950", option="knots=", **HURON,
             ours="""
                 curve = sdata.curve_through_points(x=data["year"], y=data["level"], knots=[1900, 1925, 1950])
                 {"1910": curve.find_value_at(1910), "1960": curve.find_value_at(1960)}
             """,
             parent="""
                 from scipy import interpolate
                 x, y = data["year"].to_numpy(float), data["level"].to_numpy(float)
                 t = np.r_[[x[0]] * 4, [1900, 1925, 1950], [x[-1]] * 4]
                 f = interpolate.make_lsq_spline(x, y, t, k=3)
                 {"1910": float(f(1910)), "1960": float(f(1960))}
             """, parent_label="SciPy make_lsq_spline", parent_tolerance=1e-10,
             r="""
                 m <- lm(level ~ splines::bs(year, knots = c(1900, 1925, 1950), degree = 3))
                 p <- predict(m, data.frame(year = c(1910, 1960)))
                 list(`1910` = p[[1]], `1960` = p[[2]])
             """, r_tolerance=1e-8),
        Case("sdata.curve_through_points", "Lake Huron every 10 years: a cubic curve with the slopes of the yearly "
             "changes", option="slopes=", **HURON,
             ours=_code(EVERY_10, """
                 slopes = np.gradient(data["level"].to_numpy(float), data["year"].to_numpy(float))
                 curve = sdata.curve_through_points(x=data["year"], y=data["level"], slopes=slopes)
                 {"1900": curve.find_value_at(1900), "1950": curve.find_value_at(1950)}
             """),
             parent=_scipy_curve("""
                 f = interpolate.CubicHermiteSpline(x, y, np.gradient(y, x))
                 {"1900": float(f(1900)), "1950": float(f(1950))}
             """), parent_label="SciPy CubicHermiteSpline", parent_tolerance=1e-12,
             r="""
                 k <- year %% 10 == 5; x <- year[k]; y <- level[k]
                 m <- c(diff(y[1:2]) / 10, (y[3:10] - y[1:8]) / 20, diff(y[9:10]) / 10)
                 f <- splinefunH(x, y, m)
                 list(`1900` = f(1900), `1950` = f(1950))
             """, r_tolerance=1e-10),
        Case("sdata.curve_through_points", "Lake Huron every 10 years: a spline of degree 5 through the points",
             option="degree=", **HURON,
             ours=_code(_curve(", degree=5"), '{"1900": curve.find_value_at(1900)}'),
             parent=_scipy_curve("""
                 {"1900": float(interpolate.make_interp_spline(x, y, k=5)(1900))}
             """), parent_label="SciPy make_interp_spline(k=5)", parent_tolerance=1e-12),
        Case("sdata.curve_through_points", "Lake Huron every 10 years: the cubic spline with not-a-knot ends",
             option="ends=", **HURON,
             ours=_code(_curve(', ends="not-a-knot"'), '{"1900": curve.find_value_at(1900)}'),
             parent=_scipy_curve("""
                 {"1900": float(interpolate.make_interp_spline(x, y, k=3, bc_type="not-a-knot")(1900))}
             """), parent_label="SciPy make_interp_spline(bc_type=\"not-a-knot\")", parent_tolerance=1e-12,
             note="MATLAB spline() uses not-a-knot ends; R's spline(method = \"fmm\") uses other ends."),
        Case("sdata.curve_through_points", "Lake Huron, all 98 years: the 1930s counted twice in the fit",
             option="weights=", **HURON,
             ours="""
                 weights = np.where((data["year"] >= 1930) & (data["year"] < 1940), 2.0, 1.0)
                 curve = sdata.curve_through_points(x=data["year"], y=data["level"], allowed_error=30, weights=weights)
                 {"1935": curve.find_value_at(1935)}
             """,
             parent="""
                 from scipy import interpolate
                 w = np.where((data["year"] >= 1930) & (data["year"] < 1940), 2.0, 1.0)
                 x, y = data["year"].to_numpy(float), data["level"].to_numpy(float)
                 f = interpolate.make_splrep(x, y, s=30, k=3, w=w)
                 {"1935": float(f(1935))}
             """, parent_label="SciPy make_splrep(w=)", parent_tolerance=1e-12),
        Case("sdata.curve_through_points", "mtcars: a path through the weight and miles per gallon of the first 6 "
             "cars, in their order", option="in_order=", **MTCARS,
             ours="""
                 path = sdata.curve_through_points(x=data["wt"][:6], y=data["mpg"][:6], in_order=True)
                 middle = path.find_value_at(0.5)
                 {"x": middle.get_cell_at(row=1, column="x"), "y": middle.get_cell_at(row=1, column="y")}
             """,
             parent="""
                 from scipy import interpolate
                 spline, u = interpolate.make_splprep([data["wt"][:6].to_numpy(float), data["mpg"][:6].to_numpy(float)],
                                                      s=0, k=3)
                 x, y = spline(0.5)
                 {"x": float(x), "y": float(y)}
             """, parent_label="SciPy make_splprep", parent_tolerance=1e-12),
        Case("sdata.curve_through_points", "stackloss: a surface of stack loss over air flow and water temperature "
             "through the 21 runs, smoothed", option="z=", dataset="stackloss", kind="real data",
             ours="""
                 surface = sdata.curve_through_points(x=data["air_flow"], y=data["water_temp"], z=data["stack_loss"],
                                                      degree=1, allowed_error=100)
                 {"value": surface.find_value_at(62, 21)}
             """,
             parent="""
                 from scipy import interpolate
                 x, y = data["air_flow"].to_numpy(float), data["water_temp"].to_numpy(float)
                 f = interpolate.SmoothBivariateSpline(x, y, data["stack_loss"].to_numpy(float), kx=1, ky=1, s=100)
                 {"value": float(f.ev(62, 21))}
             """, parent_label="SciPy SmoothBivariateSpline", parent_tolerance=1e-12),
        Case("sdata.curve_through_points", "mtcars: miles per gallon placed on a sphere by weight (as latitude) and "
             "power (as longitude), smoothed", option="on_sphere=", **MTCARS,
             ours="""
                 latitude = (data["wt"] - 3.5) * 20; longitude = data["hp"] / 2
                 surface = sdata.curve_through_points(x=latitude, y=longitude, z=data["mpg"], on_sphere=True,
                                                      allowed_error=400)
                 {"value": surface.find_value_at(0, 60)}
             """,
             parent="""
                 from scipy import interpolate
                 theta = np.radians(90 - (data["wt"] - 3.5) * 20); phi = np.radians(np.mod(data["hp"] / 2, 360))
                 f = interpolate.SmoothSphereBivariateSpline(theta, phi, data["mpg"].to_numpy(float), s=400)
                 {"value": float(f.ev(np.radians(90), np.radians(60)))}
             """, parent_label="SciPy SmoothSphereBivariateSpline", parent_tolerance=1e-12),
        Case("curve.find_value_at", "Lake Huron every 10 years: the natural spline at 1888, 1922 and 1958", **HURON,
             ours=_code(_curve(), """
                 values = curve.find_value_at([1888, 1922, 1958])
                 {"1888": values.get_number_at(1), "1922": values.get_number_at(2), "1958": values.get_number_at(3)}
             """),
             r=CURVE_R + "v <- f(c(1888, 1922, 1958)); list(`1888` = v[1], `1922` = v[2], `1958` = v[3])",
             r_tolerance=1e-10),
        Case("curve.find_slope_at", "Lake Huron every 10 years: the slope of the natural spline in 1900 and its bend",
             **HURON,
             ours=_code(_curve(), '{"slope": curve.find_slope_at(1900), "bend": curve.find_slope_at(1900, order=2)}'),
             r=CURVE_R + "list(slope = f(1900, deriv = 1), bend = f(1900, deriv = 2))", r_tolerance=1e-9),
        Case("curve.find_area_between", "Lake Huron every 10 years: the area under the natural spline from 1885 to "
             "1955", **HURON,
             ours=_code(_curve(), '{"area": curve.find_area_between(1885, 1955)}'),
             r=CURVE_R + "list(area = integrate(f, 1885, 1955, rel.tol = 1e-12)$value)", r_tolerance=1e-9),
        Case("curve.find_zeros", "Lake Huron every 10 years: the years the natural spline crosses 579 ft", **HURON,
             ours=_code(_curve(), """
                 years = curve.find_zeros(where_value_is=579)
                 {"first": years.get_number_at(1), "count": years.count()}
             """),
             parent=_scipy_curve("""
                 f = interpolate.make_interp_spline(x, y, k=3, bc_type="natural")
                 r = interpolate.PPoly.from_spline(f, extrapolate=False).solve(579, extrapolate=False)
                 r = np.unique(np.round(r[np.isfinite(r)], 12))
                 {"first": r[0], "count": len(r)}
             """), parent_label="SciPy PPoly.solve", parent_tolerance=1e-10,
             r=CURVE_R + "g <- function(x) f(x) - 579; xs <- seq(1875, 1965, by = 0.5); v <- g(xs); "
               "i <- which(v[-1] * v[-length(v)] < 0)[1]; "
               "list(first = uniroot(g, xs[c(i, i + 1)], tol = 1e-12)$root)",
             r_tolerance=1e-8),
        Case("curve.turn_into_slope_curve", "Lake Huron every 10 years: the slope curve of the natural spline in "
             "1930", **HURON,
             ours=_code(_curve(), '{"slope": curve.turn_into_slope_curve().find_value_at(1930)}'),
             r=CURVE_R + "list(slope = f(1930, deriv = 1))", r_tolerance=1e-9),
        Case("curve.turn_into_area_curve", "Lake Huron every 10 years: the area curve of the natural spline in 1945",
             **HURON,
             ours=_code(_curve(), '{"area": curve.turn_into_area_curve().find_value_at(1945)}'),
             r=CURVE_R + "list(area = integrate(f, 1875, 1945, rel.tol = 1e-12)$value)", r_tolerance=1e-9),
        Case("curve.show_pieces", "Lake Huron every 10 years: the cubic pieces of the natural spline", **HURON,
             ours=_code(_curve(), """
                 pieces = curve.show_pieces()
                 {"pieces": pieces.count_rows(), "first constant": pieces.get_cell_at(row=1, column="constant"),
                  "last cube": pieces.get_cell_at(row=9, column="(x - from)**3")}
             """),
             parent=_scipy_curve("""
                 p = interpolate.PPoly.from_spline(interpolate.make_interp_spline(x, y, k=3, bc_type="natural"))
                 keep = np.diff(p.x) > 0
                 {"pieces": int(keep.sum()), "first constant": p.c[3][keep][0], "last cube": p.c[0][keep][-1]}
             """), parent_label="SciPy PPoly.from_spline", parent_tolerance=1e-9,
             note="R splinefun(method = \"natural\") keeps the same pieces inside (environment(f)$z), in another "
                  "form."),
        Case("curve.show_knots", "Lake Huron every 10 years: the knots and coefficients of the natural spline",
             **HURON,
             ours=_code(_curve(), """
                 knots = curve.show_knots()
                 {"knots": knots.count_rows(), "first coefficient": knots.get_cell_at(row=1, column="coefficient"),
                  "third coefficient": knots.get_cell_at(row=3, column="coefficient")}
             """),
             parent=_scipy_curve("""
                 f = interpolate.make_interp_spline(x, y, k=3, bc_type="natural")
                 {"knots": len(f.t), "first coefficient": f.c[0], "third coefficient": f.c[2]}
             """), parent_label="SciPy BSpline t and c", parent_tolerance=1e-10),
        Case("curve.as_scipy", "Lake Huron every 10 years: the SciPy BSpline handed over, at 1900", **HURON,
             ours=_code(_curve(), '{"1900": float(curve.as_scipy()(1900))}'),
             r=CURVE_R + "list(`1900` = f(1900))", r_tolerance=1e-10),
    ]
