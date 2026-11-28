"""The reliability study for the families for 100 % plan, batches 19-21 (approved by Manish 2026-11-28): the matrices
of scipy.linalg (plan section 2.8) and grids as pictures and points (plan section 2.9).

The matrix words run on real data: the correlations of Fisher's iris measurements (a symmetric grid with positive
eigenvalues, so every matrix function is real) and the iris measurements themselves. Base R checks them where it
does the same in a few lines: a matrix function of a symmetric grid is V f(L) V' from eigen(), the Lyapunov and
Sylvester equations are linear equations in vec(X) (kronecker() and solve()), the best rotation and the angles come
from svd(), and a banded system (the Whittaker smoother of the Lake Huron levels) and a tridiagonal grid's eigenvalues
from solve() and eigen(). Base R has no Riccati solver, CS decomposition or RQ decomposition: SciPy is their reference.

The picture words run on AirPassengers as a grid of 12 years by 12 months. R's image packages (EBImage, imager) are
not among the R packages the study installs, so these words are compared with SciPy ndimage and scipy.signal only,
and each case says so. The point words run on the meuse soil samples and the centres of the US states (regions on
the earth, whose areas add up to the sphere's): R sf::st_triangulate (GEOS) checks the number of Delaunay triangles,
and base R dist(method = "minkowski") the Minkowski distances. The simplydata side reads its
results only with simplydata words (get_number_at, find_total, count_rows, get_column).

cases_underneath.py loads this file and adds the cases.
"""

from __future__ import annotations

import textwrap

IRIS = '["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]'
IRIS_R = "c <- cor(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width))\n"
CORR = f"grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())\n"
CORR_NUMPY = f"c = data[{IRIS}].corr().to_numpy()\n"
AIR_GRID = "grid = sdata.number_grid(np.asarray(data['passengers'], dtype=float).reshape(12, 12).tolist())\n"
AIR_NUMPY = "g = np.asarray(data['passengers'], dtype=float).reshape(12, 12)\n"
SCIPY_ONLY = ("R's image packages (EBImage, imager) are not installed for the study, so SciPy itself is the "
              "reference.")
READ = """
    {"first": grid.get_number_at(row=1, column=1), "corner": grid.get_number_at(row=1, column=4),
     "total": grid.find_total()}
"""
READ_PARENT = """
    {"first": f[0, 0], "corner": f[0, 3], "total": f.sum()}
"""
READ_R = "list(first = f[1, 1], corner = f[1, 4], total = sum(f))"
READ_AIR = """
    {"total": grid.find_total(), "row 3 column 5": grid.get_number_at(row=3, column=5),
     "row 12 column 12": grid.get_number_at(row=12, column=12)}
"""
READ_AIR_PARENT = """
    {"total": f.sum(), "row 3 column 5": f[2, 4], "row 12 column 12": f[11, 11]}
"""


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts if part and part.strip())


def _matrix_function(Case, name, scipy_name, r_function):
    return Case("grid.take_matrix_function", f"the matrix {name} of the correlations of Fisher's iris measurements",
                "iris", "real data", option=f'function="{name}"' if name != "square root" else "",
                ours=_code(CORR, f'grid.take_matrix_function("{name}")', READ),
                parent=_code("from scipy import linalg", CORR_NUMPY, f"f = linalg.{scipy_name}(c)", READ_PARENT),
                parent_label=f"SciPy linalg.{scipy_name}", parent_tolerance=1e-10,
                r=_code(IRIS_R, "e <- eigen(c, symmetric = TRUE)",
                        f"f <- e$vectors %*% diag({r_function}) %*% t(e$vectors)", READ_R),
                r_tolerance=1e-9,
                note="For a symmetric grid every matrix function is V f(L) V' with the eigenvalues L and eigenvectors "
                     "V of base R eigen(); the correlations of iris have positive eigenvalues, so all are real.")


def _air(Case, word, title, call, parent_call, option="", tolerance=1e-12):
    return Case(word, f"AirPassengers as a 12 x 12 grid: {title}", "AirPassengers", "real data", option=option,
                ours=_code(AIR_GRID, call, READ_AIR),
                parent=_code("from scipy import ndimage, signal", AIR_NUMPY, f"f = np.asarray({parent_call}, "
                                                                            "dtype=float)", READ_AIR_PARENT),
                parent_label="SciPy (" + parent_call.split("(")[0] + ")", parent_tolerance=tolerance,
                note=SCIPY_ONLY)


def cases(Case):
    return _cases(Case) + more_cases(Case)


def _cases(Case):
    functions = [("square root", "sqrtm", "sqrt(e$values)"), ("log", "logm", "log(e$values)"),
                 ("exp", "expm", "exp(e$values)"), ("cos", "cosm", "cos(e$values)"), ("sin", "sinm", "sin(e$values)"),
                 ("tan", "tanm", "tan(e$values)"), ("cosh", "coshm", "cosh(e$values)"),
                 ("sinh", "sinhm", "sinh(e$values)"), ("tanh", "tanhm", "tanh(e$values)"),
                 ("sign", "signm", "sign(e$values)")]
    return [
        # ---------------------------------------------------------------- batch 19: matrices (scipy.linalg)
        *[_matrix_function(Case, *f) for f in functions],
        Case("grid.take_matrix_function", "iris correlations to the power 0.3 (as a matrix)", "iris", "real data",
             option="power=",
             ours=_code(CORR, 'grid.take_matrix_function("power", power=0.3)', READ),
             parent=_code("from scipy import linalg", CORR_NUMPY, "f = linalg.fractional_matrix_power(c, 0.3)",
                          READ_PARENT),
             parent_label="SciPy linalg.fractional_matrix_power", parent_tolerance=1e-10,
             r=_code(IRIS_R, "e <- eigen(c, symmetric = TRUE)",
                     "f <- e$vectors %*% diag(e$values^0.3) %*% t(e$vectors)", READ_R), r_tolerance=1e-9),
        Case("grid.take_matrix_function", "the matrix function 1 / (1 + x) of the iris correlations", "iris",
             "real data", option='function="a formula of x"',
             ours=_code(CORR, 'grid.take_matrix_function("1 / (1 + x)")', READ),
             parent=_code("from scipy import linalg", CORR_NUMPY,
                          "f = linalg.funm(c, lambda x: 1 / (1 + x), disp=False)[0]", READ_PARENT),
             parent_label="SciPy linalg.funm", parent_tolerance=1e-10,
             r=_code(IRIS_R, "f <- solve(diag(4) + c)", READ_R), r_tolerance=1e-9,
             note="1 / (1 + x) of a grid is the inverse of the identity plus the grid: base R solve()."),
        Case("grid.check_if_grid_is", "the iris correlations are symmetric, and not banded", "iris", "real data",
             ours=_code(CORR, """
                 {"symmetric": float(grid.check_if_grid_is("symmetric", within=1e-12)),
                  "banded": float(grid.check_if_grid_is("banded"))}
             """),
             parent=_code("from scipy import linalg", CORR_NUMPY, """
                 lower, upper = linalg.bandwidth(c)
                 {"symmetric": float(linalg.issymmetric(c, atol=1e-12, rtol=0)), "banded": float(lower < 3)}
             """), parent_label="SciPy linalg.issymmetric and bandwidth", parent_tolerance=0.0,
             r=_code(IRIS_R, "list(symmetric = as.numeric(isSymmetric(c)), banded = as.numeric(any(c == 0)))"),
             r_tolerance=0.0),
        Case("grid.find_best_rotation_to", "the best rotation of iris sepal (length, width) onto petal (length, "
             "width), centred", "iris", "real data",
             ours="""
                 x = data[["Sepal.Length", "Sepal.Width"]].to_numpy()
                 y = data[["Petal.Length", "Petal.Width"]].to_numpy()
                 a, b = sdata.number_grid((x - x.mean(0)).tolist()), sdata.number_grid((y - y.mean(0)).tolist())
                 r = a.find_best_rotation_to(b)
                 {"r11": r.get_number_at(row=1, column=1), "r12": r.get_number_at(row=1, column=2)}
             """,
             parent="""
                 from scipy import linalg
                 x = data[["Sepal.Length", "Sepal.Width"]].to_numpy()
                 y = data[["Petal.Length", "Petal.Width"]].to_numpy()
                 r = linalg.orthogonal_procrustes(x - x.mean(0), y - y.mean(0))[0]
                 {"r11": r[0, 0], "r12": r[0, 1]}
             """, parent_label="SciPy linalg.orthogonal_procrustes", parent_tolerance=1e-10,
             r="""
                 a <- scale(cbind(Sepal.Length, Sepal.Width), scale = FALSE)
                 b <- scale(cbind(Petal.Length, Petal.Width), scale = FALSE)
                 s <- svd(t(a) %*% b); r <- s$u %*% t(s$v)
                 list(r11 = r[1, 1], r12 = r[1, 2])
             """, r_tolerance=1e-9,
             note="The rotation is U V' from the singular value decomposition of a'b (Schonemann 1966)."),
        Case("grid.find_angles_to", "the principal angles between the sepal and the petal measurements of iris",
             "iris", "real data",
             ours="""
                 a = sdata.number_grid(data[["Sepal.Length", "Sepal.Width"]].to_numpy().tolist())
                 b = sdata.number_grid(data[["Petal.Length", "Petal.Width"]].to_numpy().tolist())
                 angles = a.find_angles_to(b)
                 {"biggest": angles.get_number_at(1), "smallest": angles.get_number_at(2)}
             """,
             parent="""
                 from scipy import linalg
                 t = np.degrees(linalg.subspace_angles(data[["Sepal.Length", "Sepal.Width"]].to_numpy(),
                                                       data[["Petal.Length", "Petal.Width"]].to_numpy()))
                 {"biggest": t[0], "smallest": t[1]}
             """, parent_label="SciPy linalg.subspace_angles", parent_tolerance=1e-9,
             r="""
                 qa <- qr.Q(qr(cbind(Sepal.Length, Sepal.Width))); qb <- qr.Q(qr(cbind(Petal.Length, Petal.Width)))
                 d <- pmin(svd(t(qa) %*% qb)$d, 1)
                 t <- sort(acos(d) * 180 / pi, decreasing = TRUE)
                 list(biggest = t[1], smallest = t[2])
             """, r_tolerance=1e-7,
             note="R works the angles out as acos of the singular values of Qa'Qb (Bjorck & Golub 1973); SciPy uses "
                  "the sine for small angles, so the two agree to about 1e-8 relative."),
        Case("sdata.solve_matrix_equation", "the Lyapunov equation a X + X a' = q with a = minus the iris "
             "correlations and q the identity", "iris", "real data",
             ours=_code(CORR_NUMPY, """
                 x = sdata.solve_matrix_equation("lyapunov", a=(-c).tolist(), q=np.eye(4).tolist())
                 {"first": x.get_number_at(row=1, column=1), "corner": x.get_number_at(row=1, column=4),
                  "total": x.find_total()}
             """),
             parent=_code("from scipy import linalg", CORR_NUMPY, "f = linalg.solve_continuous_lyapunov(-c, np.eye(4))",
                          READ_PARENT), parent_label="SciPy linalg.solve_continuous_lyapunov", parent_tolerance=1e-10,
             r=_code(IRIS_R, "a <- -c",
                     "f <- matrix(solve(kronecker(diag(4), a) + kronecker(a, diag(4)), c(diag(4))), 4)", READ_R),
             r_tolerance=1e-9,
             note="vec(a X + X a') = (I x a + a x I) vec(X), a linear equation base R solve() answers."),
        Case("sdata.solve_matrix_equation", "the Sylvester equation a X + X b = q with the iris correlations",
             "iris", "real data", option='kind="sylvester"',
             ours=_code(CORR_NUMPY, """
                 x = sdata.solve_matrix_equation("sylvester", a=c.tolist(), b=(2 * c).tolist(),
                                                 q=np.ones((4, 4)).tolist())
                 {"first": x.get_number_at(row=1, column=1), "corner": x.get_number_at(row=1, column=4),
                  "total": x.find_total()}
             """),
             parent=_code("from scipy import linalg", CORR_NUMPY,
                          "f = linalg.solve_sylvester(c, 2 * c, np.ones((4, 4)))",
                          READ_PARENT), parent_label="SciPy linalg.solve_sylvester", parent_tolerance=1e-10,
             r=_code(IRIS_R,
                     "f <- matrix(solve(kronecker(diag(4), c) + kronecker(t(2 * c), diag(4)), rep(1, 16)), 4)",
                     READ_R), r_tolerance=1e-9),
        Case("grid.break_down", "the RQ decomposition of the iris correlations multiplies back to the grid",
             "iris", "real data", option='test_method="rq"',
             ours=_code(CORR, """
                 parts = grid.break_down(test_method="rq")
                 back = parts["R"].multiply_as_matrix_by(parts["Q"]) if hasattr(parts["R"], "multiply_as_matrix_by") \\
                     else sdata.number_grid((parts["R"].as_numpy() @ parts["Q"].as_numpy()).tolist())
                 {"r11": parts["R"].get_number_at(row=1, column=1), "back total": back.find_total()}
             """),
             parent=_code("from scipy import linalg", CORR_NUMPY, """
                 r, q = linalg.rq(c, mode="economic")
                 {"r11": r[0, 0], "back total": (r @ q).sum()}
             """), parent_label="SciPy linalg.rq", parent_tolerance=1e-10,
             note="R has no RQ decomposition in base R; SciPy itself and the product R Q = grid are the checks."),
        Case("nums.make_pair_table_with", "the Khatri-Rao product of the first 3 and the next 2 iris flowers' "
             "measurements, column by column", "iris", "real data", option="column_by_column=",
             ours=f"""
                 m = data[{IRIS}].to_numpy()
                 k = sdata.number_grid(m[:3].tolist()).make_pair_table_with(sdata.number_grid(m[3:5].tolist()),
                                                                            as_blocks=True, column_by_column=True)
                 {{"rows": k.count_rows(), "total": k.find_total(), "row 6 column 4": k.get_number_at(row=6, column=4)}}
             """,
             parent=f"""
                 from scipy import linalg
                 m = data[{IRIS}].to_numpy()
                 k = linalg.khatri_rao(m[:3], m[3:5])
                 {{"rows": k.shape[0], "total": k.sum(), "row 6 column 4": k[5, 3]}}
             """, parent_label="SciPy linalg.khatri_rao", parent_tolerance=1e-12,
             r="""
                 m <- cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)
                 k <- sapply(1:4, function(j) kronecker(m[1:3, j], m[4:5, j]))
                 list(rows = nrow(k), total = sum(k), `row 6 column 4` = k[6, 4])
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- batch 20: grids as pictures (ndimage)
        _air(Case, "grid.smooth", "the biggest of each 3 x 3 window", 'grid.smooth(test_method="biggest", window=3)',
             'ndimage.maximum_filter(g, size=3, mode="reflect")', option='test_method="biggest"'),
        _air(Case, "grid.smooth", "the smallest of 3 months in each year", 'grid.smooth(test_method="smallest", '
             'window=3, over="column")', 'ndimage.minimum_filter1d(g, 3, axis=1, mode="reflect")',
             option='test_method="smallest"'),
        _air(Case, "grid.smooth", "the 90th percentile of each 3 x 3 window",
             'grid.smooth(test_method="percentile", percentile=90, window=3)',
             'ndimage.percentile_filter(g, 90, size=3, mode="reflect")', option='test_method="percentile"'),
        _air(Case, "grid.smooth", "the second smallest of each window, cells outside 0 (order filter)",
             'grid.smooth(test_method="rank", rank=2, window=3, ends="zeros")',
             "signal.order_filter(g, np.ones((3, 3)), 1)", option='ends="zeros"'),
        _air(Case, "grid.smooth", "the range of each 3 x 3 window", 'grid.smooth(test_method="summary", '
             'summary="range", window=3)', "ndimage.generic_filter(g, np.ptp, size=3)", option='test_method="summary"'),
        _air(Case, "grid.smooth", "a bell curve in the frequencies", 'grid.smooth(test_method="fourier gaussian", '
             "width=1)", "np.fft.ifft2(ndimage.fourier_gaussian(np.fft.fft2(g), 1)).real",
             option='test_method="fourier gaussian"', tolerance=1e-10),
        _air(Case, "grid.find_edges", "the Sobel slope size", 'grid.find_edges(test_method="sobel")',
             "ndimage.generic_gradient_magnitude(g, ndimage.sobel)"),
        _air(Case, "grid.find_edges", "the Laplace filter of a bell curve", 'grid.find_edges(test_method="gaussian '
             'laplace", width=1)', "ndimage.gaussian_laplace(g, 1)", option='test_method="gaussian laplace"'),
        _air(Case, "grid.change_patch_shapes", "the months above 400 thousand grown by one cell",
             'grid.change_patch_shapes("grow", by=1, is_above=400)', "ndimage.binary_dilation(g > 400, iterations=1)",
             option="is_above="),
        _air(Case, "grid.change_patch_shapes", "the grey opening by one cell",
             'grid.change_patch_shapes("open", by=1)',
             "ndimage.grey_opening(g, footprint=ndimage.generate_binary_structure(2, 1))",
             option='how="open" on numbers'),
        _air(Case, "grid.find_distance_to_nearest", "the distance of each month to the nearest above 400 thousand",
             "grid = grid.find_distance_to_nearest(is_above=400)", "ndimage.distance_transform_edt(~(g > 400))"),
        _air(Case, "grid.move_and_stretch_by", "sheared by half a column per row",
             "grid.move_and_stretch_by(matrix=[[1, 0], [0.5, 1]]); "
             "grid.replace_each_number_that(is_empty=True, with_value=0)",
             'np.nan_to_num(ndimage.affine_transform(g, [[1, 0], [0.5, 1]], order=1, cval=np.nan), nan=0.0)'),
        _air(Case, "grid.convolve_with", "smoothed with the kernel [[0, 1, 0], [1, 4, 1], [0, 1, 0]]",
             'grid.convolve_with([[0, 1, 0], [1, 4, 1], [0, 1, 0]], keep="same")',
             'signal.convolve2d(g, [[0, 1, 0], [1, 4, 1], [0, 1, 0]], mode="same")'),
        _air(Case, "grid.find_envelope", "the size of its 2-D analytic signal", "grid.find_envelope()",
             "np.abs(signal.hilbert2(g))", tolerance=1e-10),
        Case("grid.split_touching_patches", "AirPassengers: the months split round the first and the last month "
             "(watershed)", "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 p = grid.split_touching_patches(starting_points=[[1, 1], [12, 12]])
                 {"cells of patch 2": p.count_numbers_that(is_equal_to=2)}
             """),
             parent=_code("from scipy import ndimage", AIR_NUMPY, """
                 m = np.zeros((12, 12), dtype=np.int32); m[0, 0], m[11, 11] = 1, 2
                 p = ndimage.watershed_ift(g.astype(np.uint16), m, structure=ndimage.generate_binary_structure(2, 1))
                 {"cells of patch 2": int((p == 2).sum())}
             """), parent_label="SciPy ndimage.watershed_ift", parent_tolerance=0.0, note=SCIPY_ONLY),
        Case("grid.find_each_patch_that", "AirPassengers: the biggest month and its place in each patch above 400 "
             "thousand", "AirPassengers", "real data", option="show=",
             ours=_code(AIR_GRID, """
                 p = grid.find_each_patch_that(is_above=400, show=["biggest", "where biggest", "standard deviation"])
                 {"biggest": p.get_column("biggest").find_biggest(),
                  "row": p.get_column("row of biggest").find_total(),
                  "spread": p.get_column("standard deviation").find_total()}
             """),
             parent=_code("from scipy import ndimage", AIR_NUMPY, """
                 labels, n = ndimage.label(g > 400)
                 low, high, wl, wh = ndimage.extrema(g, labels, np.arange(1, n + 1))
                 {"biggest": max(high), "row": sum(r + 1 for r, c in wh),
                  "spread": sum(ndimage.standard_deviation(g, labels, np.arange(1, n + 1)))}
             """), parent_label="SciPy ndimage.extrema and standard_deviation", parent_tolerance=1e-12,
             note=SCIPY_ONLY),
        # ---------------------------------------------------------------- batch 21: points (SciPy spatial)
        Case("table.find_triangles_between_points", "meuse: the Delaunay triangles between the 155 soil samples",
             "meuse (sp)", "real data",
             ours="""
                 t = sdata.table(data).find_triangles_between_points(x="x", y="y")
                 {"triangles": t.count_rows()}
             """,
             parent="""
                 from scipy.spatial import Delaunay
                 {"triangles": len(Delaunay(data[["x", "y"]].to_numpy(dtype=float)).simplices)}
             """, parent_label="SciPy spatial.Delaunay", parent_tolerance=0.0,
             r="""
                 p <- sf::st_union(sf::st_as_sf(data.frame(x = x, y = y), coords = c("x", "y")))
                 list(triangles = length(sf::st_collection_extract(sf::st_triangulate(p), "POLYGON")))
             """, r_packages=("sf",), r_tolerance=0.0,
             note="Any Delaunay triangulation of n points with h on the fence has 2n - 2 - h triangles, so GEOS "
                  "(R sf) and Qhull (SciPy) must agree on the count."),
        Case("table.find_regions_around_points", "meuse: the closed Voronoi regions round the 155 soil samples and "
             "their total area", "meuse (sp)", "real data",
             ours="""
                 r = sdata.table(data).find_regions_around_points(x="x", y="y")
                 {"closed": r.count_rows() - r.get_column("area").count_empty_numbers(),
                  "total area": r.get_column("area").find_total()}
             """,
             parent="""
                 from scipy.spatial import ConvexHull, Voronoi
                 v = Voronoi(data[["x", "y"]].to_numpy(dtype=float))
                 closed = [v.regions[i] for i in v.point_region if -1 not in v.regions[i]]
                 {"closed": len(closed), "total area": sum(ConvexHull(v.vertices[r]).volume for r in closed)}
             """, parent_label="SciPy spatial.Voronoi and ConvexHull", parent_tolerance=1e-10,
             note="R deldir is not among the R packages the study installs, so SciPy itself is the reference."),
        Case("table.find_distances_between_rows", "meuse: the Minkowski distances (power 3) between the first 5 "
             "samples", "meuse (sp)", "real data", option='measure="minkowski"',
             ours="""
                 t = sdata.table(data); t.keep_first_rows(5)
                 d = t.find_distances_between_rows(columns=["x", "y"], measure="minkowski", power=3)
                 {"row 1 to 2": d.get_cell_at(row=1, column="2"), "row 4 to 5": d.get_cell_at(row=4, column="5"),
                  "total": sum(d.get_column(c).find_total() for c in ["1", "2", "3", "4", "5"])}
             """,
             parent="""
                 from scipy.spatial import minkowski_distance
                 xy = data[["x", "y"]].to_numpy(dtype=float)[:5]
                 d = minkowski_distance(xy[:, None, :], xy[None, :, :], 3)
                 {"row 1 to 2": d[0, 1], "row 4 to 5": d[3, 4], "total": d.sum()}
             """, parent_label="SciPy spatial.minkowski_distance", parent_tolerance=1e-12,
             r="""
                 d <- as.matrix(dist(cbind(x, y)[1:5, ], method = "minkowski", p = 3))
                 list(`row 1 to 2` = d[1, 2], `row 4 to 5` = d[4, 5], total = sum(d))
             """, r_tolerance=1e-12),
    ]


QR_R = "q <- qr.Q(qr(c))\n"
QR_NUMPY = "q = linalg.qr(c)[0]\n"
HURON_BAND = """
    y = data["level"].to_numpy(dtype=float); n = len(y)
    d = np.diff(np.eye(n), 2, axis=0)
    a = np.eye(n) + 10 * d.T @ d
"""
HURON_BAND_R = """
    n <- length(level); d <- diff(diag(n), differences = 2)
    a <- diag(n) + 10 * t(d) %*% d
"""
HURON_TRI = """
    y = data["level"].to_numpy(dtype=float)[:12]
    a = np.diag(y) + np.diag(np.ones(11), 1) + np.diag(np.ones(11), -1)
"""


def _binary_air(Case, how, call_extra, parent_call):
    return _air(Case, "grid.change_patch_shapes", f'the months above 400 thousand, "{how}"',
                f'grid.change_patch_shapes("{how}", is_above=400{call_extra})', parent_call, option=f'how="{how}"')


def _grey_air(Case, how, scipy_name):
    return _air(Case, "grid.change_patch_shapes", f'"{how}" as a grey picture (one cell)',
                f'grid.change_patch_shapes("{how}", by=1)',
                f"ndimage.{scipy_name}(g, footprint=ndimage.generate_binary_structure(2, 1))",
                option=f'how="{how}" on numbers')


def more_cases(Case):
    m = "(g > 400)"
    u8 = "(g > 400).astype(np.uint8)"
    s = "ndimage.generate_binary_structure(2, 1)"
    return [
        # ---------------------------------------------------------------- batch 19 on real data
        Case("grid.break_down", "the CS decomposition of Q from the QR decomposition of the iris correlations",
             "iris", "real data", option='test_method="cs"',
             ours=_code(CORR_NUMPY, """
                 from scipy import linalg
                 parts = sdata.number_grid(linalg.qr(c)[0].tolist()).break_down(test_method="cs")
                 {"cs total": parts["CS"].find_total(), "cs11": parts["CS"].get_number_at(row=1, column=1)}
             """),
             parent=_code("from scipy import linalg", CORR_NUMPY, QR_NUMPY, """
                 u, cs, vdh = linalg.cossin(q, p=2, q=2)
                 {"cs total": cs.sum(), "cs11": cs[0, 0]}
             """), parent_label="SciPy linalg.cossin", parent_tolerance=1e-10,
             note="Base R has no CS decomposition; SciPy itself is the reference."),
        Case("grid.break_down", "the eigen decomposition of the first 4 iris flowers' measurements in real 2 x 2 "
             "blocks", "iris", "real data", option='test_method="real eigen blocks"',
             ours=f"""
                 m = data[{IRIS}].to_numpy()[:4]
                 parts = sdata.number_grid(m.tolist()).break_down(test_method="real eigen blocks")
                 {{"block total": parts["eigenvalue blocks"].find_total()}}
             """,
             parent=f"""
                 from scipy import linalg
                 m = data[{IRIS}].to_numpy()[:4]
                 {{"block total": linalg.cdf2rdf(*linalg.eig(m))[0].sum()}}
             """, parent_label="SciPy linalg.eig and cdf2rdf", parent_tolerance=1e-10,
             r=f"""
                 m <- cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)[1:4, ]
                 e <- eigen(m)$values
                 list(`block total` = sum(Re(e)) + sum(Re(e)[Im(e) != 0] * 0))
             """, r_tolerance=1e-9,
             note="The blocks [[a, b], [-b, a]] add up to the sum of the real parts of the eigenvalues, which base R "
                  "eigen() gives."),
        Case("grid.break_down", "the Jordan form of AirPassengers' first 2 x 2 months, exactly", "AirPassengers",
             "real data", option='test_method="jordan"',
             ours="""
                 p = np.asarray(data["passengers"], dtype=float)
                 parts = sdata.number_grid([[p[0], p[1]], [p[12], p[13]]]).break_down(test_method="jordan")
                 {"trace": parts["J"].get_number_at(row=1, column=1) + parts["J"].get_number_at(row=2, column=2),
                  "corner": parts["J"].get_number_at(row=1, column=2)}
             """,
             parent="""
                 p = np.asarray(data["passengers"], dtype=float)
                 e = np.linalg.eigvals(np.array([[p[0], p[1]], [p[12], p[13]]]))
                 {"trace": e.sum().real, "corner": 0.0}
             """, parent_label="NumPy linalg.eigvals (two different eigenvalues: J is diagonal)",
             parent_tolerance=1e-10,
             r="""
                 a <- matrix(passengers[c(1, 13, 2, 14)], 2)
                 list(trace = sum(eigen(a)$values), corner = 0)
             """, r_tolerance=1e-10),
        Case("grid.check_if_grid_is", "the iris correlations are hermitian (real and symmetric)", "iris",
             "real data", option='kind="hermitian"',
             ours=_code(CORR, '{"hermitian": float(grid.check_if_grid_is("hermitian", within=1e-12))}'),
             parent=_code("from scipy import linalg", CORR_NUMPY,
                          '{"hermitian": float(linalg.ishermitian(c, atol=1e-12, rtol=0))}'),
             parent_label="SciPy linalg.ishermitian", parent_tolerance=0.0,
             r=_code(IRIS_R, "list(hermitian = as.numeric(isSymmetric(c)))"), r_tolerance=0.0),
        Case("grid.check_if_grid_is", "the iris correlations are symmetric to within 1e-12", "iris", "real data",
             option="within=",
             ours=_code(CORR, '{"symmetric": float(grid.check_if_grid_is("symmetric", within=1e-12))}'),
             parent=_code("from scipy import linalg", CORR_NUMPY,
                          '{"symmetric": float(linalg.issymmetric(c, atol=1e-12, rtol=0))}'),
             parent_label="SciPy linalg.issymmetric", parent_tolerance=0.0,
             r=_code(IRIS_R, "list(symmetric = as.numeric(isSymmetric(c, tol = 1e-12)))"), r_tolerance=0.0),
        *[Case("grid.check_if_grid_is", f"R of the QR decomposition of the iris correlations: {kind}?", "iris",
               "real data", option=f'kind="{kind}"',
               ours=_code(CORR_NUMPY, f"""
                   from scipy import linalg
                   r = sdata.number_grid(np.triu(linalg.qr(c)[1]).tolist())
                   {{"answer": float(r.check_if_grid_is("{kind}"))}}
               """),
               parent=_code("from scipy import linalg", CORR_NUMPY, f"""
                   lower, upper = linalg.bandwidth(np.triu(linalg.qr(c)[1]))
                   {{"answer": float({test})}}
               """), parent_label="SciPy linalg.bandwidth", parent_tolerance=0.0,
               r=_code(IRIS_R, f"r <- qr.R(qr(c))", f"list(answer = as.numeric({r_test}))"), r_tolerance=0.0)
          for kind, test, r_test in (
              ("upper triangle", "lower == 0", "all(r[lower.tri(r)] == 0)"),
              ("lower triangle", "upper == 0", "all(r[upper.tri(r)] == 0)"),
              ("diagonal", "lower == 0 and upper == 0", "all(r[row(r) != col(r)] == 0)"),
              ("banded", "lower < 3 or upper < 3", "all(r[lower.tri(r)] == 0)"))],
        Case("grid.solve_for", "Lake Huron levels smoothed by the Whittaker system (I + 10 D'D) x = y, from its band",
             "Lake Huron", "real data", option="structure=",
             ours=_code(HURON_BAND, """
                 x = sdata.number_grid(a.tolist()).solve_for(y.tolist(), structure="banded")
                 {"first": x.get_number_at(1), "last": x.get_number_at(n), "total": x.find_total()}
             """),
             parent=_code("from scipy import linalg", HURON_BAND, """
                 x = linalg.solve(a, y)
                 {"first": x[0], "last": x[-1], "total": x.sum()}
             """), parent_label="SciPy linalg.solve on the whole grid", parent_tolerance=1e-10,
             r=_code(HURON_BAND_R, "x <- solve(a, level)", "list(first = x[1], last = x[n], total = sum(x))"),
             r_tolerance=1e-10),
        Case("grid.find_eigenvalues", "the eigenvalues of the tridiagonal grid with the first 12 Lake Huron levels "
             "on its diagonal", "Lake Huron", "real data", option="structure=",
             ours=_code(HURON_TRI, """
                 e = sdata.number_grid(a.tolist()).find_eigenvalues(structure="tridiagonal").get_column("eigenvalue")
                 {"biggest": e.get_number_at(1), "smallest": e.get_number_at(12), "total": e.find_total()}
             """),
             parent=_code("from scipy import linalg", HURON_TRI, """
                 e = linalg.eigvalsh(a)
                 {"biggest": e[-1], "smallest": e[0], "total": e.sum()}
             """), parent_label="SciPy linalg.eigvalsh on the whole grid", parent_tolerance=1e-10,
             r="""
                 y <- level[1:12]
                 a <- diag(y); a[abs(row(a) - col(a)) == 1] <- 1
                 e <- eigen(a, symmetric = TRUE)$values
                 list(biggest = e[1], smallest = e[12], total = sum(e))
             """, r_tolerance=1e-10),
        Case("sdata.solve_matrix_equation", "the discrete Lyapunov equation with a = 0.2 times the iris correlations",
             "iris", "real data", option='kind="discrete lyapunov"',
             ours=_code(CORR_NUMPY, """
                 x = sdata.solve_matrix_equation("discrete lyapunov", a=(0.2 * c).tolist(), q=np.eye(4).tolist())
                 {"first": x.get_number_at(row=1, column=1), "corner": x.get_number_at(row=1, column=4),
                  "total": x.find_total()}
             """),
             parent=_code("from scipy import linalg", CORR_NUMPY,
                          "f = linalg.solve_discrete_lyapunov(0.2 * c, np.eye(4))",
                          READ_PARENT), parent_label="SciPy linalg.solve_discrete_lyapunov", parent_tolerance=1e-10,
             r=_code(IRIS_R, "a <- 0.2 * c",
                     "f <- matrix(solve(diag(16) - kronecker(a, a), c(diag(4))), 4)", READ_R), r_tolerance=1e-9,
             note="vec(a X a' - X + q) = 0 is (I - a x a) vec(X) = vec(q), which base R solve() answers."),
        *[Case("sdata.solve_matrix_equation", f"the {kind} equation with a = minus the iris correlations, b = q = r = "
               "the identity", "iris", "real data", option=f'kind="{kind}"',
               ours=_code(CORR_NUMPY, f"""
                   i = np.eye(4).tolist()
                   x = sdata.solve_matrix_equation("{kind}", a=(-c).tolist(), b=i, q=i, r=i)
                   {{"first": x.get_number_at(row=1, column=1), "corner": x.get_number_at(row=1, column=4),
                    "total": x.find_total()}}
               """),
               parent=_code("from scipy import linalg", CORR_NUMPY,
                            f"f = linalg.{scipy_name}(-c, np.eye(4), np.eye(4), np.eye(4))", READ_PARENT),
               parent_label=f"SciPy linalg.{scipy_name}", parent_tolerance=1e-9,
               note="Base R has no Riccati solver; SciPy itself is the reference.")
          for kind, scipy_name in (("riccati", "solve_continuous_are"), ("discrete riccati", "solve_discrete_are"))],
        # ---------------------------------------------------------------- batch 20 on real data (ndimage)
        _air(Case, "grid.change_patch_shapes", "the months above 300 thousand grown by one cell",
             'grid.change_patch_shapes("grow", is_above=300)', "ndimage.binary_dilation(g > 300)"),
        _binary_air(Case, "shrink", "", f"ndimage.binary_erosion({m})"),
        _binary_air(Case, "open", "", f"ndimage.binary_opening({m})"),
        _binary_air(Case, "close", "", f"ndimage.binary_closing({m})"),
        _binary_air(Case, "fill holes", "", f"ndimage.binary_fill_holes({m})"),
        _binary_air(Case, "top hat", "", f"ndimage.white_tophat({u8}, footprint={s}) > 0"),
        _binary_air(Case, "dark top hat", "", f"ndimage.black_tophat({u8}, footprint={s}) > 0"),
        _binary_air(Case, "outline", "", f"ndimage.morphological_gradient({u8}, footprint={s}) > 0"),
        _binary_air(Case, "laplace", "", f"ndimage.morphological_laplace({u8}, footprint={s})"),
        _binary_air(Case, "match pattern", ", pattern=[[1, 1], [1, 0]]",
                    f"ndimage.binary_hit_or_miss({m}, np.array([[1, 1], [1, 0]]) == 1, "
                    "np.array([[1, 1], [1, 0]]) == 0)"),
        _binary_air(Case, "keep patches with points", ", starting_points=[[12, 8]]",
                    f"ndimage.binary_propagation(np.arange(144).reshape(12, 12) == 139, mask={m})"),
        *[_grey_air(Case, how, scipy_name) for how, scipy_name in (
            ("grow", "grey_dilation"), ("shrink", "grey_erosion"), ("close", "grey_closing"),
            ("top hat", "white_tophat"), ("dark top hat", "black_tophat"), ("outline", "morphological_gradient"),
            ("laplace", "morphological_laplace"))],
        _air(Case, "grid.find_edges", "the Prewitt slope size", 'grid.find_edges(test_method="prewitt")',
             "ndimage.generic_gradient_magnitude(g, ndimage.prewitt)", option='test_method="prewitt"'),
        _air(Case, "grid.find_edges", "the Laplace filter", 'grid.find_edges(test_method="laplace")',
             "ndimage.laplace(g)", option='test_method="laplace"'),
        _air(Case, "grid.find_edges", "the slope size of a bell curve", 'grid.find_edges(test_method="gaussian '
             'gradient", width=1)', "ndimage.gaussian_gradient_magnitude(g, 1)",
             option='test_method="gaussian gradient"'),
        _air(Case, "grid.find_edges", "the Sobel change along the months", 'grid.find_edges(test_method="sobel", '
             'along="columns")', "ndimage.sobel(g, axis=1)", option="along="),
        _air(Case, "grid.smooth", "the second smallest of each 3 x 3 window", 'grid.smooth(test_method="rank", rank=2, '
             "window=3)", "ndimage.rank_filter(g, 1, size=3)", option='test_method="rank"'),
        _air(Case, "grid.smooth", "a square average in the frequencies", 'grid.smooth(test_method="fourier uniform", '
             "window=3)", "np.fft.ifft2(ndimage.fourier_uniform(np.fft.fft2(g), 3)).real",
             option='test_method="fourier uniform"', tolerance=1e-10),
        _air(Case, "grid.smooth", "a round average in the frequencies", 'grid.smooth(test_method="fourier ellipsoid", '
             "window=3)", "np.fft.ifft2(ndimage.fourier_ellipsoid(np.fft.fft2(g), 3)).real",
             option='test_method="fourier ellipsoid"', tolerance=1e-10),
        _air(Case, "grid.smooth", "a cubic spline surface through every month (smoothness 0)",
             'grid.smooth(test_method="spline", smoothness=0)', "signal.spline_filter(g, lmbda=0.0)",
             option='test_method="spline"', tolerance=1e-10),
        _air(Case, "grid.convolve_with", "correlated with [[1, 2], [0, -1]] (not turned round)",
             'grid.convolve_with([[1, 2], [0, -1]], flip=False, keep="same")',
             'signal.correlate2d(g, [[1, 2], [0, -1]], mode="same")', option="flip="),
        _air(Case, "grid.convolve_with", "a separable filter [1, 2, 1] by [1, 0, -1]",
             "grid.convolve_with(row_weights=[1, 2, 1], column_weights=[1, 0, -1])",
             "signal.sepfir2d(g, [1, 2, 1], [1, 0, -1])", option="row_weights="),
        # ---------------------------------------------------------------- batch 21 on real data
        *[_air(Case, "grid.find_distance_to_nearest", f"the {method} distance to the nearest month above 400 "
               "thousand", f'grid = grid.find_distance_to_nearest(is_above=400, test_method="{method}")', call,
               option=f'test_method="{method}"')
          for method, call in (("city block", 'ndimage.distance_transform_cdt(~(g > 400), metric="taxicab")'),
                               ("chessboard", 'ndimage.distance_transform_cdt(~(g > 400), metric="chessboard")'),
                               ("brute force", 'ndimage.distance_transform_bf(~(g > 400), metric="euclidean")'))],
        _air(Case, "grid.move_and_stretch_by", "each month taken from half a month on per year (a rule)",
             'grid.move_and_stretch_by(rule={"row": "row", "column": "column + 0.5*row"}); '
             "grid.replace_each_number_that(is_empty=True, with_value=0)",
             "np.nan_to_num(ndimage.geometric_transform(g, lambda p: (p[0], p[1] + 0.5 * (p[0] + 1)), order=1, "
             "cval=np.nan), nan=0.0)", option="rule="),
        _air(Case, "grid.move_and_stretch_by", "moved by half a year and one month, wrapping round (Fourier)",
             'grid.move_and_stretch_by(shift=[0.5, 1], test_method="fourier")',
             "np.fft.ifft2(ndimage.fourier_shift(np.fft.fft2(g), [-0.5, -1])).real", option='test_method="fourier"',
             tolerance=1e-10),
        Case("table.find_triangles_between_points", "meuse: the triangle that holds two points of the flood plain",
             "meuse (sp)", "real data", option="containing=",
             ours="""
                 near = {"x": [179500, 180500], "y": [331500, 332500]}
                 t = sdata.table(data).find_triangles_between_points(x="x", y="y", containing=near)
                 {"first": t.get_cell_at(row=1, column="triangle"), "second": t.get_cell_at(row=2, column="triangle")}
             """,
             parent="""
                 from scipy.spatial import Delaunay, tsearch
                 mesh = Delaunay(data[["x", "y"]].to_numpy(dtype=float))
                 t = tsearch(mesh, np.array([[179500, 331500], [180500, 332500.0]])) + 1
                 {"first": float(t[0]), "second": float(t[1])}
             """, parent_label="SciPy spatial.tsearch", parent_tolerance=0.0,
             note="R deldir is not among the R packages the study installs, so SciPy itself is the reference."),
        Case("table.find_regions_around_points", "state.center: the regions round the centres of the 50 US states on "
             "the earth, in square kilometres", "state.center (R datasets)", "real data", option="longitude=",
             ours="""
                 r = sdata.table(data).find_regions_around_points(longitude="lon", latitude="lat")
                 {"total area": r.get_column("area").find_total(), "biggest": r.get_column("area").find_biggest()}
             """,
             parent="""
                 from scipy.spatial import SphericalVoronoi
                 lo, la = np.radians(data["lon"].to_numpy(float)), np.radians(data["lat"].to_numpy(float))
                 a = SphericalVoronoi(np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
                                      ).calculate_areas() * 6371.0088 ** 2
                 {"total area": a.sum(), "biggest": a.max()}
             """, parent_label="SciPy spatial.SphericalVoronoi", parent_tolerance=1e-10,
             published={"total area": (4 * 3.141592653589793 * 6371.0088 ** 2, 1e-3,
                                       "worked out: the regions cover the whole sphere, 4 pi r**2")},
             note="The regions on a sphere cover all of it, so their areas add up to 4 pi r squared."),
    ]
