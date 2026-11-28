"""The reliability study for the families for 100 % plan, batches 10-13 (plan section 2.4), part 2: the options of the
NumPy and SciPy words for lists and grids, and the named polynomials of sdata.polynomial, that had an underneath
entry but no case on real data yet. Each is run on real data and compared with NumPy, SciPy or SymPy and, where base
R does the same in a few lines, with R.

cases_underneath.py loads this file and adds the cases. The data are the study's AirPassengers (Box and Jenkins'
monthly airline passengers, 1949-1960), Fisher's iris and mtcars (R datasets). The simplydata side reads its results
only with simplydata words; positions count from 1, as in R.
"""

from __future__ import annotations

import textwrap

AIR = "numbers = sdata.number_list(np.asarray(data['passengers'], dtype=float).tolist())\n"
AIR_X = "x = np.asarray(data['passengers'], dtype=float)\n"
AIR_GRID = "grid = sdata.number_grid(np.asarray(data['passengers'], dtype=float).reshape(12, 12).tolist())\n"
AIR_G = "g = np.asarray(data['passengers'], dtype=float).reshape(12, 12)\n"
AIR_R = "g <- matrix(as.numeric(passengers), nrow = 12, byrow = TRUE)\n"
SCALE = "s = 2 * (x - x.min()) / (x.max() - x.min()) - 1\n"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts if part and part.strip())


def cases(Case):
    return [
        # ---------------------------------------------------------------- batch 10: options of the list words
        Case("nums.remove_duplicate_numbers", "mtcars: which of the different gear counts (3, 4 or 5) each car has",
             "mtcars", "real data", option='show="which number"',
             ours="""
                 which = sdata.number_list(data["gear"].tolist()).remove_duplicate_numbers(show="which number")
                 {"first car": which.get_number_at(1), "fourth car": which.get_number_at(4),
                  "total": which.find_total()}
             """,
             parent="""
                 w = np.unique_inverse(data["gear"].to_numpy()).inverse_indices + 1
                 {"first car": w[0], "fourth car": w[3], "total": w.sum()}
             """, parent_label="NumPy unique_inverse", parent_tolerance=1e-12,
             r="""
                 w <- match(gear, sort(unique(gear)))
                 list(`first car` = w[1], `fourth car` = w[4], total = sum(w))
             """, r_tolerance=1e-12),
        Case("nums.replace_numbers_where", "AirPassengers: the January of each of the first three years set to 0",
             "AirPassengers", "real data", option="at_positions=",
             ours=_code(AIR, """
                 numbers.replace_numbers_where(at_positions=[1, 13, 25], with_value=0)
                 {"total": numbers.find_total(), "13th": numbers.get_number_at(13), "2nd": numbers.get_number_at(2)}
             """),
             parent=_code(AIR_X, """
                 np.put(x, [0, 12, 24], 0)
                 {"total": x.sum(), "13th": x[12], "2nd": x[1]}
             """), parent_label="NumPy put", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); x[c(1, 13, 25)] <- 0
                 list(total = sum(x), `13th` = x[13], `2nd` = x[2])
             """, r_tolerance=1e-12),
        Case("nums.replace_numbers_where", "AirPassengers: each month marked -1 below 150 passengers, 1 above 400 and "
             "0 otherwise", "AirPassengers", "real data", option="rules=",
             ours=_code(AIR, """
                 quiet = numbers.turn_into_yes_or_no(is_below=150)
                 busy = numbers.turn_into_yes_or_no(is_above=400)
                 numbers.replace_numbers_where(rules=[(quiet, -1), (busy, 1)], with_value=0)
                 {"total": numbers.find_total(), "first": numbers.get_number_at(1), "last": numbers.get_number_at(144)}
             """),
             parent=_code(AIR_X, """
                 m = np.select([x < 150, x > 400], [-1, 1], default=0)
                 {"total": m.sum(), "first": m[0], "last": m[-1]}
             """), parent_label="NumPy select", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); m <- ifelse(x < 150, -1, ifelse(x > 400, 1, 0))
                 list(total = sum(m), first = m[1], last = m[144])
             """, r_tolerance=1e-12),
        Case("nums.replace_numbers_where", "AirPassengers: each month below 150 passengers replaced by the same month "
             "one year later", "AirPassengers", "real data", option="with_value=",
             ours=_code(AIR, """
                 later = sdata.number_list(np.asarray(data['passengers'], dtype=float)[12:].tolist() + [0.0] * 12)
                 first = sdata.number_list(np.asarray(data['passengers'], dtype=float).tolist())
                 quiet = first.turn_into_yes_or_no(is_below=150)
                 numbers.replace_numbers_where(quiet, with_value=later)
                 {"total": numbers.find_total(), "first": numbers.get_number_at(1), "smallest": numbers.find_smallest()}
             """),
             parent=_code(AIR_X, """
                 later = np.concatenate([x[12:], np.zeros(12)])
                 y = x.copy(); np.copyto(y, later, where=x < 150)
                 {"total": y.sum(), "first": y[0], "smallest": y.min()}
             """), parent_label="NumPy copyto", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); later <- c(x[13:144], rep(0, 12))
                 y <- ifelse(x < 150, later, x)
                 list(total = sum(y), first = y[1], smallest = min(y))
             """, r_tolerance=1e-12),
        Case("nums.take_cosine_transform", "AirPassengers: the inverse cosine transform (orthonormal) of the 144 "
             "monthly counts", "AirPassengers", "real data", option="inverse=",
             ours=_code(AIR, """
                 numbers.take_cosine_transform(inverse=True)
                 {"first": numbers.get_number_at(1), "fifth": numbers.get_number_at(5), "total": numbers.find_total()}
             """),
             parent=_code(AIR_X, """
                 from scipy import fft
                 y = fft.idct(x, type=2, norm="ortho")
                 {"first": y[0], "fifth": y[4], "total": y.sum()}
             """), parent_label="SciPy fft.idct", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); n <- length(x); k <- 0:(n - 1)
                 w <- ifelse(k == 0, sqrt(1 / n), sqrt(2 / n))
                 C <- outer(k, k, function(i, j) cos(pi * (2 * j + 1) * i / (2 * n))) * w
                 y <- as.numeric(t(C) %*% x)
                 list(first = y[1], fifth = y[5], total = sum(y))
             """, r_tolerance=1e-10),
        Case("nums.take_cosine_transform", "AirPassengers: the sine transform (orthonormal) of the 144 monthly counts",
             "AirPassengers", "real data", option='kind="sine"',
             ours=_code(AIR, """
                 numbers.take_cosine_transform(kind="sine")
                 {"first": numbers.get_number_at(1), "second": numbers.get_number_at(2),
                  "last": numbers.get_number_at(144)}
             """),
             parent=_code(AIR_X, """
                 from scipy import fft
                 y = fft.dst(x, type=2, norm="ortho")
                 {"first": y[0], "second": y[1], "last": y[-1]}
             """), parent_label="SciPy fft.dst", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); n <- length(x); k <- 0:(n - 1)
                 w <- ifelse(k == n - 1, sqrt(1 / n), sqrt(2 / n))
                 S <- outer(k, k, function(i, j) sin(pi * (i + 1) * (2 * j + 1) / (2 * n))) * w
                 y <- as.numeric(S %*% x)
                 list(first = y[1], second = y[2], last = y[144])
             """, r_tolerance=1e-10),
        Case("nums.take_cosine_transform", "AirPassengers: the fast Hankel transform of the first year's counts, "
             "taken as spaced 0.1 apart on the natural log scale", "AirPassengers", "real data",
             option='kind="hankel"',
             ours="""
                 numbers = sdata.number_list(np.asarray(data['passengers'][:12], dtype=float).tolist())
                 numbers.take_cosine_transform(kind="hankel", log_step=0.1, order=0)
                 {"first": numbers.get_number_at(1), "sixth": numbers.get_number_at(6), "total": numbers.find_total()}
             """,
             parent="""
                 from scipy import fft
                 y = fft.fht(np.asarray(data['passengers'][:12], dtype=float), dln=0.1, mu=0)
                 {"first": y[0], "sixth": y[5], "total": y.sum()}
             """, parent_label="SciPy fft.fht", parent_tolerance=1e-12,
             note="Base R has no fast Hankel transform (FFTLog), so the check is against SciPy only."),
        # ---------------------------------------------------------------- batch 11: options of the starting words
        Case("sdata.number_list", "AirPassengers: 5 numbers evenly spaced on a log scale from the smallest to the "
             "biggest monthly count", "AirPassengers", "real data", option='spacing="log"',
             ours=_code(AIR, """
                 low, high = numbers.find_smallest(), numbers.find_biggest()
                 spaced = sdata.number_list(low, to=high, how_many=5, spacing="log")
                 {"second": spaced.get_number_at(2), "middle": spaced.get_number_at(3), "total": spaced.find_total()}
             """),
             parent=_code(AIR_X, """
                 s = np.geomspace(x.min(), x.max(), 5)
                 {"second": s[1], "middle": s[2], "total": s.sum()}
             """), parent_label="NumPy geomspace", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); s <- exp(seq(log(min(x)), log(max(x)), length.out = 5))
                 list(second = s[2], middle = s[3], total = sum(s))
             """, r_tolerance=1e-12),
        Case("sdata.number_grid", "AirPassengers as 12 years x 12 months, times the grid row x column: the weighted "
             "totals", "AirPassengers", "real data", option="from_formula=",
             ours=_code(AIR_GRID, """
                 weights = sdata.number_grid(from_formula="row * column", rows=12, columns=12)
                 product = grid.multiply_as_matrix_by(weights)
                 {"corner": product.get_number_at(row=12, column=12), "first": product.get_number_at(row=1, column=1),
                  "total": product.get_all_numbers().find_total()}
             """),
             parent=_code(AIR_G, """
                 w = np.fromfunction(lambda i, j: (i + 1) * (j + 1), (12, 12))
                 p = g @ w
                 {"corner": p[11, 11], "first": p[0, 0], "total": p.sum()}
             """), parent_label="NumPy fromfunction", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 p <- g %*% outer(1:12, 1:12)
                 list(corner = p[12, 12], first = p[1, 1], total = sum(p))
             """), r_tolerance=1e-12),
        Case("sdata.number_grid", "AirPassengers as 12 years x 12 months: the identity grid shifted by one, times the "
             "counts, moves each year up one row", "AirPassengers", "real data", option='kind="identity"',
             ours=_code(AIR_GRID, """
                 shift = sdata.number_grid(kind="identity", size=12, shifted_by=1)
                 moved = shift.multiply_as_matrix_by(grid)
                 {"first": moved.get_number_at(row=1, column=1), "last row": moved.get_number_at(row=12, column=12),
                  "total": moved.get_all_numbers().find_total()}
             """),
             parent=_code(AIR_G, """
                 m = np.eye(12, 12, 1) @ g
                 {"first": m[0, 0], "last row": m[11, 11], "total": m.sum()}
             """), parent_label="NumPy eye", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 e <- matrix(0, 12, 12); e[cbind(1:11, 2:12)] <- 1; m <- e %*% g
                 list(first = m[1, 1], `last row` = m[12, 12], total = sum(m))
             """), r_tolerance=1e-12),
        Case("sdata.number_grid", "iris: the sepal length, sepal width and petal length of the 150 flowers turned "
             "30 degrees about the third axis", "iris", "real data", option='kind="rotation"',
             ours="""
                 points = sdata.number_grid(data[["Sepal.Length", "Sepal.Width", "Petal.Length"]].to_numpy().tolist())
                 turn = sdata.number_grid(kind="rotation", axis="z", by_degrees=30)
                 turned = points.multiply_as_matrix_by(turn.swap_rows_and_columns())
                 {"first": turned.get_number_at(row=1, column=1), "second": turned.get_number_at(row=1, column=2),
                  "total": turned.get_all_numbers().find_total()}
             """,
             parent="""
                 import sympy as sp
                 r = np.array(sp.rot_ccw_axis3(sp.pi / 6).evalf(), dtype=float)
                 t = data[["Sepal.Length", "Sepal.Width", "Petal.Length"]].to_numpy() @ r.T
                 {"first": t[0, 0], "second": t[0, 1], "total": t.sum()}
             """, parent_label="SymPy rot_ccw_axis3", parent_tolerance=1e-12,
             r="""
                 a <- pi / 6; r <- matrix(c(cos(a), -sin(a), 0, sin(a), cos(a), 0, 0, 0, 1), 3, byrow = TRUE)
                 t <- cbind(Sepal.Length, Sepal.Width, Petal.Length) %*% t(r)
                 list(first = t[1, 1], second = t[1, 2], total = sum(t))
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- batch 13: named polynomials
        Case("sdata.polynomial", "iris: the Chebyshev polynomial of degree 5 at the 150 petal lengths scaled to -1 to "
             "1", "iris", "real data", option='"chebyshev"',
             ours=_code("x = data['Petal.Length'].to_numpy()\n", SCALE, """
                 values = sdata.polynomial("chebyshev", degree=5).find_value_at(x=s.tolist())
                 {"total": values.find_total(), "biggest": values.find_biggest(), "first": values.get_number_at(1)}
             """),
             parent=_code("x = data['Petal.Length'].to_numpy()\n", SCALE, """
                 from scipy import special
                 v = special.eval_chebyt(5, s)
                 {"total": v.sum(), "biggest": v.max(), "first": v[0]}
             """), parent_label="SciPy special.eval_chebyt", parent_tolerance=1e-12,
             r="""
                 s <- 2 * (Petal.Length - min(Petal.Length)) / (max(Petal.Length) - min(Petal.Length)) - 1
                 v <- 16 * s^5 - 20 * s^3 + 5 * s
                 list(total = sum(v), biggest = max(v), first = v[1])
             """, r_tolerance=1e-10),
        Case("sdata.polynomial", "mtcars: the probabilists' Hermite polynomial of degree 4 at the 32 fuel uses, "
             "standardised", "mtcars", "real data", option='"probabilists hermite"',
             ours="""
                 x = data["mpg"].to_numpy(); z = (x - x.mean()) / x.std(ddof=1)
                 values = sdata.polynomial("probabilists hermite", degree=4).find_value_at(x=z.tolist())
                 {"total": values.find_total(), "biggest": values.find_biggest(), "first": values.get_number_at(1)}
             """,
             parent="""
                 from scipy import special
                 x = data["mpg"].to_numpy(); z = (x - x.mean()) / x.std(ddof=1)
                 v = special.eval_hermitenorm(4, z)
                 {"total": v.sum(), "biggest": v.max(), "first": v[0]}
             """, parent_label="SciPy special.eval_hermitenorm", parent_tolerance=1e-12,
             r="""
                 z <- (mpg - mean(mpg)) / sd(mpg); v <- z^4 - 6 * z^2 + 3
                 list(total = sum(v), biggest = max(v), first = v[1])
             """, r_tolerance=1e-10),
        Case("sdata.polynomial", "AirPassengers: the Jacobi polynomial of degree 3 (alpha 1, beta 2) at the 144 "
             "monthly counts scaled to -1 to 1", "AirPassengers", "real data", option='"jacobi"',
             ours=_code(AIR_X, SCALE, """
                 values = sdata.polynomial("jacobi", degree=3, alpha=1, beta=2).find_value_at(x=s.tolist())
                 {"total": values.find_total(), "biggest": values.find_biggest(), "first": values.get_number_at(1)}
             """),
             parent=_code(AIR_X, SCALE, """
                 from scipy import special
                 v = special.eval_jacobi(3, 1, 2, s)
                 {"total": v.sum(), "biggest": v.max(), "first": v[0]}
             """), parent_label="SciPy special.eval_jacobi", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); s <- 2 * (x - min(x)) / (max(x) - min(x)) - 1
                 n <- 3; a <- 1; b <- 2
                 v <- Reduce(`+`, lapply(0:n, function(k) choose(n + a, n - k) * choose(n + b, k) *
                                                       ((s - 1) / 2)^k * ((s + 1) / 2)^(n - k)))
                 list(total = sum(v), biggest = max(v), first = v[1])
             """, r_tolerance=1e-10,
             note="R: the explicit sum of the Jacobi polynomial (Abramowitz and Stegun 22.3.2)."),
        Case("sdata.polynomial", "mtcars: the polynomial whose roots are the weights of the first 3 cars, at the "
             "weights of all 32", "mtcars", "real data", option='"from roots"',
             ours="""
                 formula = sdata.polynomial("from roots", roots=data["wt"].head(3).tolist())
                 values = formula.find_value_at(x=data["wt"].tolist())
                 {"total": values.find_total(), "last": values.get_number_at(32), "fifth": values.get_number_at(5)}
             """,
             parent="""
                 v = np.polyval(np.poly(data["wt"].head(3).to_numpy()), data["wt"].to_numpy())
                 {"total": v.sum(), "last": v[-1], "fifth": v[4]}
             """, parent_label="NumPy poly", parent_tolerance=1e-10,
             r="""
                 r <- wt[1:3]; v <- sapply(wt, function(x) prod(x - r))
                 list(total = sum(v), last = v[32], fifth = v[5])
             """, r_tolerance=1e-10),
    ]
