"""Numbers finishing (P41 and the designed matrix words): grid.solve_for and grid.break_down on real data.

cases_underneath.py loads this file and adds cases(Case) to the study. solve_for gives NIST's certified straight line
through the Norris ozone calibration points (least squares, a grid that is not square), the standardised effects of
three iris measurements on petal width (a square grid of correlations), the shortest answer for a grid whose columns
depend on each other, non-negative and bounded least squares on Brownlee's stack loss data (the unmixing shape of
problem) and an exact answer on AirPassengers as 12 years x 12 months. break_down splits the iris measurements and
their correlation grid; parts that a decomposition fixes only up to signs are compared through what does not depend
on the signs (singular values, the size of the diagonal, the grid multiplied back). Each case is compared with SciPy
and, where base R or an installed package does the same, with R (solve, qr.solve, MASS::ginv, pracma::lsqnonneg,
svd, chol, qr, eigen).
"""

from __future__ import annotations

import textwrap

IRIS = '["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]'
IRIS_R = "cor(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width))"
THREE = '["Sepal.Length", "Sepal.Width", "Petal.Length"]'
STACK = '["air_flow", "water_temp", "acid_conc"]'
AIR_GRID = "grid = sdata.number_grid(np.asarray(data['passengers'], dtype=float).reshape(12, 12).tolist())\n"
AIR_NUMPY = "g = np.asarray(data['passengers'], dtype=float).reshape(12, 12)\n"
AIR_R = "g <- matrix(as.numeric(passengers), nrow = 12, byrow = TRUE)\n"
# NIST StRD Norris, certified values (validation/data/nist/Norris.dat)
NORRIS_SLOPE = 1.00211681802045
NORRIS_INTERCEPT = -0.262323073774029


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def cases(Case):
    return [
        # ---------------------------------------------------------------- solve_for
        Case("grid.solve_for", "NIST's certified line through 36 ozone calibration points (least squares)",
             "NIST Norris", "published",
             ours="""
                 grid = sdata.number_grid([[1.0, x] for x in data["x"]])
                 x = grid.solve_for(data["y"].tolist())
                 {"intercept": x.get_number_at(1), "slope": x.get_number_at(2)}
             """,
             published={"intercept": (NORRIS_INTERCEPT, "lre", "NIST certified"),
                        "slope": (NORRIS_SLOPE, "lre", "NIST certified")},
             parent="""
                 from scipy import linalg
                 g = np.column_stack([np.ones(len(data)), data["x"]])
                 x = linalg.lstsq(g, data["y"].to_numpy())[0]
                 {"intercept": x[0], "slope": x[1]}
             """, parent_label="SciPy linalg.lstsq", parent_tolerance=1e-10,
             r="""
                 b <- qr.solve(cbind(1, x), y)
                 list(intercept = b[1], slope = b[2])
             """, r_tolerance=1e-10),
        Case("grid.solve_for", "standardised effects of three iris measurements on petal width (a square grid)",
             "iris", "real data",
             ours=f"""
                 c = data[{IRIS}].corr().to_numpy()
                 x = sdata.number_grid(c[:3, :3].tolist()).solve_for(c[:3, 3].tolist())
                 {{"sepal length": x.get_number_at(1), "sepal width": x.get_number_at(2),
                  "petal length": x.get_number_at(3)}}
             """,
             parent=f"""
                 from scipy import linalg
                 c = data[{IRIS}].corr().to_numpy()
                 x = linalg.solve(c[:3, :3], c[:3, 3])
                 {{"sepal length": x[0], "sepal width": x[1], "petal length": x[2]}}
             """, parent_label="SciPy linalg.solve", parent_tolerance=1e-12,
             r=f"""
                 c <- {IRIS_R}
                 x <- solve(c[1:3, 1:3], c[1:3, 4])
                 list(`sepal length` = x[1], `sepal width` = x[2], `petal length` = x[3])
             """, r_tolerance=1e-10),
        Case("grid.solve_for", "with_best_fit=True: the shortest answer from the first 3 iris flowers (4 x 4, rank 3)",
             "iris", "real data", option="with_best_fit=",
             ours=f"""
                 m = data[{IRIS}].head(3).to_numpy()
                 grid = sdata.number_grid((m.T @ m).tolist())
                 x = grid.solve_for((m.T @ np.array([1.0, 2.0, 3.0])).tolist(), with_best_fit=True)
                 {{"first": x.get_number_at(1), "last": x.get_number_at(4),
                  "length": float(np.linalg.norm(x.as_numpy()))}}
             """,
             parent=f"""
                 from scipy import linalg
                 m = data[{IRIS}].head(3).to_numpy()
                 x = linalg.lstsq(m.T @ m, m.T @ np.array([1.0, 2.0, 3.0]))[0]
                 {{"first": x[0], "last": x[3], "length": float(np.linalg.norm(x))}}
             """, parent_label="SciPy linalg.lstsq", parent_tolerance=1e-6,
             r="""
                 m <- cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)[1:3, ]
                 x <- MASS::ginv(t(m) %*% m) %*% (t(m) %*% c(1, 2, 3))
                 list(first = x[1], last = x[4], length = sqrt(sum(x^2)))
             """, r_packages=("MASS",), r_tolerance=1e-6),
        Case("grid.solve_for", "between=[0, None]: stack loss from air flow, water and acid, no effect below 0",
             "stackloss", "real data", option="between=",
             ours=f"""
                 grid = sdata.number_grid(data[{STACK}].to_numpy(dtype=float).tolist())
                 x = grid.solve_for(data["stack_loss"].tolist(), between=[0, None])
                 {{"air flow": x.get_number_at(1), "water temperature": x.get_number_at(2),
                  "acid concentration": x.get_number_at(3)}}
             """,
             parent=f"""
                 from scipy import optimize
                 x = optimize.nnls(data[{STACK}].to_numpy(dtype=float), data["stack_loss"].to_numpy(dtype=float))[0]
                 {{"air flow": x[0], "water temperature": x[1], "acid concentration": x[2]}}
             """, parent_label="SciPy optimize.nnls", parent_tolerance=1e-9,
             r="""
                 x <- pracma::lsqnonneg(cbind(air_flow, water_temp, acid_conc), stack_loss)$x
                 list(`air flow` = x[1], `water temperature` = x[2], `acid concentration` = x[3])
             """, r_packages=("pracma",), r_tolerance=1e-7),
        Case("grid.solve_for", "between=[0, 1]: stack loss with every effect between 0 and 1 (bounded least squares)",
             "stackloss", "real data", option="between=",
             ours=f"""
                 grid = sdata.number_grid(data[{STACK}].to_numpy(dtype=float).tolist())
                 x = grid.solve_for(data["stack_loss"].tolist(), between=[0, 1])
                 {{"air flow": x.get_number_at(1), "water temperature": x.get_number_at(2),
                  "acid concentration": x.get_number_at(3)}}
             """,
             parent=f"""
                 from scipy import optimize
                 f = optimize.lsq_linear(data[{STACK}].to_numpy(dtype=float), data["stack_loss"].to_numpy(dtype=float),
                                         bounds=(0, 1), method="bvls")
                 {{"air flow": f.x[0], "water temperature": f.x[1], "acid concentration": f.x[2]}}
             """, parent_label="SciPy optimize.lsq_linear (bvls)", parent_tolerance=1e-9),
        Case("grid.solve_for", "exactly=True: AirPassengers as 12 years x 12 months, b the yearly totals, x all 1",
             "AirPassengers", "real data", option="exactly=",
             ours=_code(AIR_GRID, """
                 x = grid.solve_for(grid.as_numpy().sum(axis=1).tolist(), exactly=True)
                 {"total": x.find_total(), "smallest": x.find_smallest(), "biggest": x.find_biggest()}
             """),
             parent=_code(AIR_NUMPY, """
                 import sympy as sp
                 m = sp.Matrix(g.astype(int).tolist())
                 x = m.LUsolve(sp.Matrix(g.astype(int).sum(axis=1).tolist()))
                 v = np.array(x.evalf(), dtype=float).ravel()
                 {"total": v.sum(), "smallest": v.min(), "biggest": v.max()}
             """), parent_label="SymPy Matrix.LUsolve", parent_tolerance=1e-15,
             r=_code(AIR_R, """
                 x <- solve(g, rowSums(g))
                 list(total = sum(x), smallest = min(x), biggest = max(x))
             """), r_tolerance=1e-9),
        # ---------------------------------------------------------------- break_down
        Case("grid.break_down", "the singular values of Fisher's 150 iris flowers x 4 measurements",
             "iris", "real data",
             ours=f"""
                 parts = sdata.number_grid(data[{IRIS}].to_numpy().tolist()).break_down()
                 s = parts["singular values"].as_numpy()
                 u = parts["U"].as_numpy()
                 {{"first": s[0], "second": s[1], "third": s[2], "fourth": s[3],
                  "U columns at right angles": float(np.allclose(u.T @ u, np.eye(4)))}}
             """,
             parent=f"""
                 from scipy import linalg
                 u, s, vt = linalg.svd(data[{IRIS}].to_numpy(), full_matrices=False)
                 {{"first": s[0], "second": s[1], "third": s[2], "fourth": s[3],
                  "U columns at right angles": float(np.allclose(u.T @ u, np.eye(4)))}}
             """, parent_label="SciPy linalg.svd", parent_tolerance=1e-12,
             r="""
                 s <- svd(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width))
                 list(first = s$d[1], second = s$d[2], third = s$d[3], fourth = s$d[4],
                      `U columns at right angles` = as.numeric(isTRUE(all.equal(crossprod(s$u), diag(4)))))
             """, r_tolerance=1e-10),
        Case("grid.break_down", 'test_method="cholesky": the correlations of Fisher\'s iris measurements',
             "iris", "real data", option="test_method=",
             ours=f"""
                 u = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist()).break_down(test_method="cholesky")["U"]
                 u = u.as_numpy()
                 {{"corner": u[0, 3], "last": u[3, 3], "total": u.sum()}}
             """,
             parent=f"""
                 from scipy import linalg
                 u = linalg.cholesky(data[{IRIS}].corr().to_numpy())
                 {{"corner": u[0, 3], "last": u[3, 3], "total": u.sum()}}
             """, parent_label="SciPy linalg.cholesky", parent_tolerance=1e-12,
             r=f"""
                 u <- chol({IRIS_R})
                 list(corner = u[1, 4], last = u[4, 4], total = sum(u))
             """, r_tolerance=1e-10),
        Case("grid.break_down", 'test_method="qr": the iris measurements (150 x 4), sizes of the diagonal of R',
             "iris", "real data", option="test_method=",
             ours=f"""
                 parts = sdata.number_grid(data[{IRIS}].to_numpy().tolist()).break_down(test_method="qr")
                 d = np.abs(np.diag(parts["R"].as_numpy()))
                 {{"first": d[0], "second": d[1], "third": d[2], "fourth": d[3], "Q rows": parts["Q"].count_rows()}}
             """,
             parent=f"""
                 from scipy import linalg
                 q, r = linalg.qr(data[{IRIS}].to_numpy(), mode="economic")
                 d = np.abs(np.diag(r))
                 {{"first": d[0], "second": d[1], "third": d[2], "fourth": d[3], "Q rows": q.shape[0]}}
             """, parent_label="SciPy linalg.qr", parent_tolerance=1e-12,
             r="""
                 d <- abs(diag(qr.R(qr(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)))))
                 list(first = d[1], second = d[2], third = d[3], fourth = d[4], `Q rows` = 150)
             """, r_tolerance=1e-10),
        Case("grid.break_down", 'test_method="schur": AirPassengers as 12 x 12, the eigenvalues on the diagonal of T',
             "AirPassengers", "real data", option="test_method=",
             ours=_code(AIR_GRID, """
                 parts = grid.break_down(test_method="schur")
                 t, z = parts["T"].as_numpy(), parts["Z"].as_numpy()
                 {"trace": np.trace(t), "biggest": np.max(np.diag(t)),
                  "multiplied back": float(np.allclose(z @ t @ z.T, grid.as_numpy()))}
             """),
             parent=_code(AIR_NUMPY, """
                 from scipy import linalg
                 t, z = linalg.schur(g, output="real")
                 {"trace": np.trace(t), "biggest": np.max(np.diag(t)),
                  "multiplied back": float(np.allclose(z @ t @ z.T, g))}
             """), parent_label="SciPy linalg.schur", parent_tolerance=1e-10,
             r=_code(AIR_R, """
                 e <- eigen(g)$values
                 list(trace = sum(diag(g)), biggest = max(Re(e)), `multiplied back` = 1)
             """), r_tolerance=1e-8),
        Case("grid.break_down", 'test_method="lu": AirPassengers as 12 x 12, P times L times U gives the grid back',
             "AirPassengers", "real data", option="test_method=",
             ours=_code(AIR_GRID, """
                 parts = grid.break_down(test_method="lu")
                 p, low, up = (parts[k].as_numpy() for k in ("P", "L", "U"))
                 {"product of U's diagonal": abs(np.prod(np.diag(up))), "first of U": up[0, 0],
                  "multiplied back": float(np.allclose(p @ low @ up, grid.as_numpy()))}
             """),
             parent=_code(AIR_NUMPY, """
                 from scipy import linalg
                 p, low, up = linalg.lu(g)
                 {"product of U's diagonal": abs(np.prod(np.diag(up))), "first of U": up[0, 0],
                  "multiplied back": float(np.allclose(p @ low @ up, g))}
             """), parent_label="SciPy linalg.lu", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 list(`product of U's diagonal` = abs(det(g)), `first of U` = max(abs(g[, 1])), `multiplied back` = 1)
             """), r_tolerance=1e-8),
        Case("grid.break_down", 'test_method="polar": the iris correlations, the turn and the stretch',
             "iris", "real data", option="test_method=",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 parts = grid.break_down(test_method="polar")
                 u, p = parts["U"].as_numpy(), parts["P"].as_numpy()
                 {{"stretch total": p.sum(), "turn total": u.sum(),
                  "multiplied back": float(np.allclose(u @ p, grid.as_numpy()))}}
             """,
             parent=f"""
                 from scipy import linalg
                 u, p = linalg.polar(data[{IRIS}].corr().to_numpy())
                 {{"stretch total": p.sum(), "turn total": u.sum(),
                  "multiplied back": float(np.allclose(u @ p, data[{IRIS}].corr().to_numpy()))}}
             """, parent_label="SciPy linalg.polar", parent_tolerance=1e-10),
        Case("grid.break_down", 'test_method="ldl": the iris correlations, L times D times L turned gives them back',
             "iris", "real data", option="test_method=",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 parts = grid.break_down(test_method="ldl")
                 low, d = parts["L"].as_numpy(), parts["D"].as_numpy()
                 {{"D total": d.sum(), "first in row order": parts["row order"].get_number_at(1),
                  "multiplied back": float(np.allclose(low @ d @ low.T, grid.as_numpy()))}}
             """,
             parent=f"""
                 from scipy import linalg
                 c = data[{IRIS}].corr().to_numpy()
                 low, d, order = linalg.ldl(c)
                 {{"D total": d.sum(), "first in row order": order[0] + 1,
                  "multiplied back": float(np.allclose(low @ d @ low.T, c))}}
             """, parent_label="SciPy linalg.ldl", parent_tolerance=1e-12),
        Case("grid.break_down", 'test_method="hessenberg": AirPassengers as 12 x 12, Q times H times Q turned',
             "AirPassengers", "real data", option="test_method=",
             ours=_code(AIR_GRID, """
                 parts = grid.break_down(test_method="hessenberg")
                 h, q = parts["H"].as_numpy(), parts["Q"].as_numpy()
                 {"trace": np.trace(h), "zeros below": float(np.allclose(np.tril(h, -2), 0)),
                  "multiplied back": float(np.allclose(q @ h @ q.T, grid.as_numpy()))}
             """),
             parent=_code(AIR_NUMPY, """
                 from scipy import linalg
                 h, q = linalg.hessenberg(g, calc_q=True)
                 {"trace": np.trace(h), "zeros below": float(np.allclose(np.tril(h, -2), 0)),
                  "multiplied back": float(np.allclose(q @ h @ q.T, g))}
             """), parent_label="SciPy linalg.hessenberg", parent_tolerance=1e-10,
             r=_code(AIR_R, """
                 list(trace = sum(diag(g)), `zeros below` = 1, `multiplied back` = 1)
             """), r_tolerance=1e-10),
        Case("grid.break_down", "together_with=: QZ of the iris correlations with their covariances",
             "iris", "real data", option="together_with=",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 parts = grid.break_down(test_method="qz", together_with=data[{IRIS}].cov().to_numpy().tolist())
                 ratios = np.sort(np.diag(parts["AA"].as_numpy()) / np.diag(parts["BB"].as_numpy()))
                 {{"smallest ratio": ratios[0], "biggest ratio": ratios[-1], "total of ratios": ratios.sum()}}
             """,
             parent=f"""
                 from scipy import linalg
                 values = np.sort(linalg.eigvals(data[{IRIS}].corr().to_numpy(), data[{IRIS}].cov().to_numpy()).real)
                 {{"smallest ratio": values[0], "biggest ratio": values[-1], "total of ratios": values.sum()}}
             """, parent_label="SciPy linalg.eigvals (the generalised eigenvalues)", parent_tolerance=1e-9,
             r=f"""
                 m <- cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)
                 e <- sort(Re(eigen(solve(cov(m)) %*% cor(m))$values))
                 list(`smallest ratio` = e[1], `biggest ratio` = e[4], `total of ratios` = sum(e))
             """, r_tolerance=1e-8),
    ]
