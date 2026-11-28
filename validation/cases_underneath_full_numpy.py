"""The reliability study for the families for 100 % plan, batches 10-13 (approved by Manish 2026-11-28, plan section
2.4): the NumPy and SciPy words for lists and grids of numbers and sdata.polynomial, each run on real data and compared
with NumPy, SciPy or SymPy and, where base R (or pracma, installed for the study) does the same in a few lines, with R.

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
IRIS = '["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]'
IRIS_R = "m <- cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)\n"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts if part and part.strip())


def cases(Case):
    return [
        # ---------------------------------------------------------------- batch 10: lists
        Case("nums.find_product", "AirPassengers: the growth over 1949, the product of the 11 month-to-month ratios",
             "AirPassengers", "real data",
             ours=_code(AIR, """
                 ratios = sdata.number_list((np.asarray(data['passengers'][1:12], dtype=float)
                                             / np.asarray(data['passengers'][0:11], dtype=float)).tolist())
                 {"growth": ratios.find_product()}
             """),
             parent=_code(AIR_X, """
                 {"growth": np.prod(x[1:12] / x[0:11])}
             """), parent_label="NumPy prod", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); list(growth = prod(x[2:12] / x[1:11]))
             """, r_tolerance=1e-12),
        Case("nums.turn_into_running_total", "AirPassengers: the growth over 1949 so far, month by month (running "
             "product of the ratios); the last value", "AirPassengers", "real data", option='show="product"',
             ours="""
                 x = np.asarray(data['passengers'], dtype=float)
                 ratios = sdata.number_list((x[1:12] / x[0:11]).tolist())
                 ratios.turn_into_running_total(show="product")
                 {"after 6 months": ratios.get_number_at(6), "after 11 months": ratios.get_number_at(11)}
             """,
             parent=_code(AIR_X, """
                 p = np.cumprod(x[1:12] / x[0:11])
                 {"after 6 months": p[5], "after 11 months": p[10]}
             """), parent_label="NumPy cumprod", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); p <- cumprod(x[2:12] / x[1:11])
                 list(`after 6 months` = p[6], `after 11 months` = p[11])
             """, r_tolerance=1e-12),
        Case("nums.turn_into_changes", "AirPassengers: the change from the same month a year before (lag 12)",
             "AirPassengers", "real data",
             ours=_code(AIR, """
                 numbers.turn_into_changes(rows_back=12)
                 {"count": numbers.count(), "first": numbers.get_number_at(1), "last": numbers.get_number_at("last"),
                  "average": numbers.find_average()}
             """),
             parent=_code(AIR_X, """
                 d = x[12:] - x[:-12]
                 {"count": len(d), "first": d[0], "last": d[-1], "average": d.mean()}
             """), parent_label="NumPy (x[12:] - x[:-12])", parent_tolerance=1e-12,
             r="""
                 d <- diff(as.numeric(passengers), lag = 12)
                 list(count = length(d), first = d[1], last = d[length(d)], average = mean(d))
             """, r_tolerance=1e-12),
        Case("nums.turn_into_changes", "AirPassengers: the changes of the month-to-month changes",
             "AirPassengers", "real data", option="how_many_times=",
             ours=_code(AIR, """
                 numbers.turn_into_changes(how_many_times=2)
                 {"count": numbers.count(), "total": numbers.find_total(), "biggest": numbers.find_biggest()}
             """),
             parent=_code(AIR_X, """
                 d = np.diff(x, n=2)
                 {"count": len(d), "total": d.sum(), "biggest": d.max()}
             """), parent_label="NumPy diff(n=2)", parent_tolerance=1e-12,
             r="""
                 d <- diff(as.numeric(passengers), differences = 2)
                 list(count = length(d), total = sum(d), biggest = max(d))
             """, r_tolerance=1e-12),
        Case("nums.turn_into_slopes", "AirPassengers: the slope (passengers per year) at the first, a middle and the "
             "last month (central differences)", "AirPassengers", "real data",
             ours=_code(AIR, """
                 numbers.turn_into_slopes(time_step=1 / 12)
                 {"first": numbers.get_number_at(1), "month 70": numbers.get_number_at(70),
                  "last": numbers.get_number_at("last")}
             """),
             parent=_code(AIR_X, """
                 s = np.gradient(x, 1 / 12)
                 {"first": s[0], "month 70": s[69], "last": s[-1]}
             """), parent_label="NumPy gradient", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); n <- length(x); h <- 1 / 12
                 list(first = (x[2] - x[1]) / h, `month 70` = (x[71] - x[69]) / (2 * h), last = (x[n] - x[n - 1]) / h)
             """, r_tolerance=1e-12),
        Case("nums.count_in_bins", "mtcars: how many cars in each fuel-use bin (10-15, 15-20, 20-25, 25-35 mpg)",
             "mtcars", "real data",
             ours="""
                 counts = sdata.number_list(data["mpg"].tolist()).count_in_bins(edges=[10, 15, 20, 25, 35])
                 found = counts.get_column("count")
                 {f"bin {i}": found.get_number_at(i) for i in range(1, 5)}
             """,
             parent="""
                 found = np.histogram(data["mpg"], bins=[10, 15, 20, 25, 35])[0]
                 {f"bin {i}": found[i - 1] for i in range(1, 5)}
             """, parent_label="NumPy histogram", parent_tolerance=1e-12,
             r="""
                 h <- hist(mpg, breaks = c(10, 15, 20, 25, 35), right = FALSE, include.lowest = TRUE, plot = FALSE)
                 list(`bin 1` = h$counts[1], `bin 2` = h$counts[2], `bin 3` = h$counts[3], `bin 4` = h$counts[4])
             """, r_tolerance=1e-12),
        Case("nums.find_bin_of_each", "mtcars: the horsepower class of each car (below 100, 100-150, 150-250, 250 and "
             "up to 400)", "mtcars", "real data",
             ours="""
                 bins = sdata.number_list(data["hp"].tolist()).find_bin_of_each(edges=[0, 100, 150, 250, 400])
                 {"total of the bins": bins.find_total(), "car 31 (Maserati Bora)": bins.get_number_at(31),
                  "in bin 1": bins.count_numbers_that(is_equal_to=1)}
             """,
             parent="""
                 b = np.digitize(data["hp"], [0, 100, 150, 250, 400])
                 {"total of the bins": b.sum(), "car 31 (Maserati Bora)": b[30], "in bin 1": (b == 1).sum()}
             """, parent_label="NumPy digitize", parent_tolerance=1e-12,
             r="""
                 b <- findInterval(hp, c(0, 100, 150, 250, 400))
                 list(`total of the bins` = sum(b), `car 31 (Maserati Bora)` = b[31], `in bin 1` = sum(b == 1))
             """, r_tolerance=1e-12),
        Case("nums.find_positions_where", "AirPassengers: the months with more than 500 passengers (their positions "
             "from 1)", "AirPassengers", "real data",
             ours=_code(AIR, """
                 positions = numbers.find_positions_where(is_above=500)
                 {"how many": positions.count(), "first": positions.get_number_at(1),
                  "total of the positions": positions.find_total()}
             """),
             parent=_code(AIR_X, """
                 p = np.flatnonzero(x > 500) + 1
                 {"how many": len(p), "first": p[0], "total of the positions": p.sum()}
             """), parent_label="NumPy flatnonzero", parent_tolerance=1e-12,
             r="""
                 p <- which(passengers > 500)
                 list(`how many` = length(p), first = p[1], `total of the positions` = sum(p))
             """, r_tolerance=1e-12),
        Case("nums.keep_numbers_also_in", "mtcars: the horsepower values found among both the automatic and the "
             "manual cars", "mtcars", "real data",
             ours="""
                 auto = sdata.number_list(data.loc[data["am"] == 0, "hp"].tolist())
                 auto.keep_numbers_also_in(data.loc[data["am"] == 1, "hp"].tolist())
                 {"how many": auto.count(), "total": auto.find_total()}
             """,
             parent="""
                 both = np.intersect1d(data.loc[data["am"] == 0, "hp"], data.loc[data["am"] == 1, "hp"])
                 {"how many": len(both), "total": both.sum()}
             """, parent_label="NumPy intersect1d", parent_tolerance=1e-12,
             r="""
                 both <- intersect(hp[am == 0], hp[am == 1])
                 list(`how many` = length(both), total = sum(both))
             """, r_tolerance=1e-12),
        Case("nums.remove_numbers_also_in", "mtcars: the horsepower values of automatic cars that no manual car has",
             "mtcars", "real data",
             ours="""
                 auto = sdata.number_list(data.loc[data["am"] == 0, "hp"].tolist())
                 auto.remove_numbers_also_in(data.loc[data["am"] == 1, "hp"].tolist())
                 {"how many": auto.count(), "total": auto.find_total()}
             """,
             parent="""
                 only = np.setdiff1d(data.loc[data["am"] == 0, "hp"], data.loc[data["am"] == 1, "hp"])
                 {"how many": len(only), "total": only.sum()}
             """, parent_label="NumPy setdiff1d", parent_tolerance=1e-12,
             r="""
                 only <- setdiff(hp[am == 0], hp[am == 1])
                 list(`how many` = length(only), total = sum(only))
             """, r_tolerance=1e-12),
        Case("nums.keep_numbers_in_only_one", "mtcars: the horsepower values found in only one of the two gearbox "
             "groups", "mtcars", "real data",
             ours="""
                 auto = sdata.number_list(data.loc[data["am"] == 0, "hp"].tolist())
                 auto.keep_numbers_in_only_one(data.loc[data["am"] == 1, "hp"].tolist())
                 {"how many": auto.count(), "total": auto.find_total()}
             """,
             parent="""
                 one = np.setxor1d(data.loc[data["am"] == 0, "hp"], data.loc[data["am"] == 1, "hp"])
                 {"how many": len(one), "total": one.sum()}
             """, parent_label="NumPy setxor1d", parent_tolerance=1e-12,
             r="""
                 a <- unique(hp[am == 0]); b <- unique(hp[am == 1]); one <- c(setdiff(a, b), setdiff(b, a))
                 list(`how many` = length(one), total = sum(one))
             """, r_tolerance=1e-12),
        Case("nums.join_numbers_with", "mtcars: the different horsepower values of the two gearbox groups together",
             "mtcars", "real data",
             ours="""
                 auto = sdata.number_list(data.loc[data["am"] == 0, "hp"].tolist())
                 auto.join_numbers_with(data.loc[data["am"] == 1, "hp"].tolist())
                 {"how many": auto.count(), "total": auto.find_total()}
             """,
             parent="""
                 every = np.union1d(data.loc[data["am"] == 0, "hp"], data.loc[data["am"] == 1, "hp"])
                 {"how many": len(every), "total": every.sum()}
             """, parent_label="NumPy union1d", parent_tolerance=1e-12,
             r="""
                 every <- union(hp[am == 0], hp[am == 1])
                 list(`how many` = length(every), total = sum(every))
             """, r_tolerance=1e-12),
        Case("nums.find_dot_product_with", "iris: the dot product of sepal length and petal length over the 150 "
             "flowers", "iris", "real data",
             ours="""
                 sepal = sdata.number_list(data["Sepal.Length"].tolist())
                 {"dot product": sepal.find_dot_product_with(data["Petal.Length"].tolist())}
             """,
             parent="""
                 {"dot product": np.dot(data["Sepal.Length"], data["Petal.Length"])}
             """, parent_label="NumPy dot", parent_tolerance=1e-12,
             r="""
                 list(`dot product` = sum(Sepal.Length * Petal.Length))
             """, r_tolerance=1e-12),
        Case("nums.find_cross_product_with", "iris: the cross product of the average first three measurements of "
             "setosa and of virginica", "iris", "real data",
             ours="""
                 cols = ["Sepal.Length", "Sepal.Width", "Petal.Length"]
                 a = data.loc[data["Species"] == "setosa", cols].mean().tolist()
                 b = data.loc[data["Species"] == "virginica", cols].mean().tolist()
                 c = sdata.number_list(a).find_cross_product_with(b)
                 {"x": c.get_number_at(1), "y": c.get_number_at(2), "z": c.get_number_at(3)}
             """,
             parent="""
                 cols = ["Sepal.Length", "Sepal.Width", "Petal.Length"]
                 a = data.loc[data["Species"] == "setosa", cols].mean()
                 b = data.loc[data["Species"] == "virginica", cols].mean()
                 c = np.cross(a, b)
                 {"x": c[0], "y": c[1], "z": c[2]}
             """, parent_label="NumPy cross", parent_tolerance=1e-12,
             r="""
                 s <- Species == "setosa"; v <- Species == "virginica"
                 a <- c(mean(Sepal.Length[s]), mean(Sepal.Width[s]), mean(Petal.Length[s]))
                 b <- c(mean(Sepal.Length[v]), mean(Sepal.Width[v]), mean(Petal.Length[v]))
                 list(x = a[2] * b[3] - a[3] * b[2], y = a[3] * b[1] - a[1] * b[3], z = a[1] * b[2] - a[2] * b[1])
             """, r_tolerance=1e-12),
        Case("nums.find_size", "iris: the length (2-norm) and the total size (1-norm) of the 150 petal lengths",
             "iris", "real data",
             ours="""
                 petal = sdata.number_list(data["Petal.Length"].tolist())
                 {"length": petal.find_size(), "total size": petal.find_size(kind="total size")}
             """,
             parent="""
                 x = data["Petal.Length"].to_numpy()
                 {"length": np.linalg.vector_norm(x), "total size": np.linalg.vector_norm(x, ord=1)}
             """, parent_label="NumPy linalg.vector_norm", parent_tolerance=1e-12,
             r="""
                 list(length = norm(Petal.Length, "2"), `total size` = sum(abs(Petal.Length)))
             """, r_tolerance=1e-12),
        Case("nums.sort", "mtcars: the positions of the three most powerful cars (the order of horsepower, biggest "
             "first)", "mtcars", "real data", option='show="positions"',
             ours="""
                 order = sdata.number_list(data["hp"].tolist()).sort(show="positions", biggest_first=True)
                 {"first": order.get_number_at(1), "second": order.get_number_at(2), "third": order.get_number_at(3)}
             """,
             parent="""
                 o = np.argsort(-data["hp"].to_numpy(), kind="stable") + 1
                 {"first": o[0], "second": o[1], "third": o[2]}
             """, parent_label="NumPy argsort", parent_tolerance=1e-12,
             r="""
                 o <- order(hp, decreasing = TRUE)
                 list(first = o[1], second = o[2], third = o[3])
             """, r_tolerance=1e-12),
        Case("nums.sort", "mtcars: cylinders sorted, with ties in the order of fuel use; the fuel use of the cars "
             "after sorting at three places", "mtcars", "real data", option="then_by=",
             ours="""
                 cyl = sdata.number_list(data["cyl"].tolist())
                 cyl.sort(then_by=data["mpg"].tolist())
                 {"first": cyl.get_number_at(1), "middle": cyl.get_number_at(16), "last": cyl.get_number_at(32)}
             """,
             parent="""
                 o = np.lexsort((data["mpg"], data["cyl"]))
                 c = data["cyl"].to_numpy()[o]
                 {"first": c[0], "middle": c[15], "last": c[31]}
             """, parent_label="NumPy lexsort", parent_tolerance=1e-12,
             r="""
                 c <- cyl[order(cyl, mpg)]
                 list(first = c[1], middle = c[16], last = c[32])
             """, r_tolerance=1e-12),
        Case("nums.remove_duplicate_numbers", "mtcars: the different gear counts, where each first comes and how "
             "many cars have each", "mtcars", "real data", option='show="positions"',
             ours="""
                 t = sdata.number_list(data["gear"].tolist()).remove_duplicate_numbers(show="positions")
                 first, count = t.get_column("first position"), t.get_column("count")
                 {"first of 3": first.get_number_at(1), "first of 5": first.get_number_at(3),
                  "count of 4": count.get_number_at(2)}
             """,
             parent="""
                 u = np.unique_all(data["gear"].to_numpy())
                 {"first of 3": u.indices[0] + 1, "first of 5": u.indices[2] + 1, "count of 4": u.counts[1]}
             """, parent_label="NumPy unique_all", parent_tolerance=1e-12,
             r="""
                 list(`first of 3` = match(3, gear), `first of 5` = match(5, gear), `count of 4` = sum(gear == 4))
             """, r_tolerance=1e-12),
        Case("nums.change_angles_to", "AirPassengers: the month of each reading as an angle in degrees, wrapping round "
             "each year, run on smoothly; the last angle", "AirPassengers", "real data", option="remove_jumps=",
             ours="""
                 angles = sdata.number_list([(i % 12) * 30.0 for i in range(len(data))])
                 angles.change_angles_to("degrees", remove_jumps=True)
                 {"last": angles.get_number_at("last"), "total": angles.find_total()}
             """,
             parent="""
                 a = np.unwrap([(i % 12) * 30.0 for i in range(len(data))], period=360)
                 {"last": a[-1], "total": a.sum()}
             """, parent_label="NumPy unwrap", parent_tolerance=1e-12,
             r="""
                 a <- (seq_along(passengers) - 1) * 30
                 list(last = a[length(a)], total = sum(a))
             """, r_tolerance=1e-12,
             note="R has no unwrap in base; the angles run on smoothly by construction, (i - 1) x 30 degrees."),
        # ---------------------------------------------------------------- batches 11-12: grids
        Case("grid.find_positions_where", "AirPassengers as 12 years x 12 months: the year and month of each month "
             "above 500 passengers", "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 where = grid.find_positions_where(is_above=500)
                 {"how many": where.count_rows(), "first year": where.get_column("row").get_number_at(1),
                  "total of the months": where.get_column("column").find_total()}
             """),
             parent=_code(AIR_G, """
                 w = np.argwhere(g > 500) + 1
                 {"how many": len(w), "first year": w[0, 0], "total of the months": w[:, 1].sum()}
             """), parent_label="NumPy argwhere", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 w <- which(g > 500, arr.ind = TRUE); w <- w[order(w[, 1], w[, 2]), , drop = FALSE]
                 list(`how many` = nrow(w), `first year` = w[1, 1], `total of the months` = sum(w[, 2]))
             """), r_tolerance=1e-12),
        Case("grid.multiply_as_matrix_by", "iris: the cross-product grid of the four measurements (X'X); its trace "
             "and one cell", "iris", "real data",
             ours=f"""
                 m = data[{IRIS}].to_numpy()
                 product = sdata.number_grid(m.T.tolist()).multiply_as_matrix_by(m.tolist())
                 {{"sepal length x petal width": product.get_number_at(row=1, column=4),
                  "trace": product.get_part("diagonal").find_total()}}
             """,
             parent=f"""
                 m = data[{IRIS}].to_numpy()
                 p = np.matmul(m.T, m)
                 {{"sepal length x petal width": p[0, 3], "trace": np.trace(p)}}
             """, parent_label="NumPy matmul", parent_tolerance=1e-12,
             r=_code(IRIS_R, """
                 p <- t(m) %*% m
                 list(`sepal length x petal width` = p[1, 4], trace = sum(diag(p)))
             """), r_tolerance=1e-12),
        Case("grid.get_part", "iris: the correlations above the diagonal of the four measurements, as a list; their "
             "total and the biggest", "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 upper = grid.get_part("upper triangle", shifted_by=1, as_list=True)
                 {{"total": upper.find_total(), "biggest": upper.find_biggest(), "how many": upper.count()}}
             """,
             parent=f"""
                 c = data[{IRIS}].corr().to_numpy()
                 u = c[np.triu_indices(4, 1)]
                 {{"total": u.sum(), "biggest": u.max(), "how many": len(u)}}
             """, parent_label="NumPy triu_indices", parent_tolerance=1e-12,
             r=_code(IRIS_R, """
                 c <- cor(m); u <- c[upper.tri(c)]
                 list(total = sum(u), biggest = max(u), `how many` = length(u))
             """), r_tolerance=1e-12),
        Case("grid.replace_part", "iris: the correlation grid with 0 on the diagonal; the biggest correlation left",
             "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 grid.replace_part("diagonal", with_value=0)
                 {{"biggest": grid.get_all_numbers().find_biggest(), "total": grid.get_all_numbers().find_total()}}
             """,
             parent=f"""
                 c = data[{IRIS}].corr().to_numpy().copy()
                 np.fill_diagonal(c, 0)
                 {{"biggest": c.max(), "total": c.sum()}}
             """, parent_label="NumPy fill_diagonal", parent_tolerance=1e-12,
             r=_code(IRIS_R, """
                 c <- cor(m); diag(c) <- 0
                 list(biggest = max(c), total = sum(c))
             """), r_tolerance=1e-12),
        Case("grid.add_border", "AirPassengers as 12 years x 12 months with a border of the nearest month copied; "
             "the total of the bigger grid", "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 grid.add_border(width=1, with_value="repeat edge")
                 {"rows": grid.count_rows(), "total": grid.get_all_numbers().find_total()}
             """),
             parent=_code(AIR_G, """
                 p = np.pad(g, 1, mode="edge")
                 {"rows": p.shape[0], "total": p.sum()}
             """), parent_label="NumPy pad (edge)", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 p <- rbind(g[1, ], g, g[12, ]); p <- cbind(p[, 1], p, p[, 12])
                 list(rows = nrow(p), total = sum(p))
             """), r_tolerance=1e-12),
        Case("grid.find_rank", "iris: the rank of the 150 x 4 measurements and of the 4 x 4 grid with a column made "
             "from two others", "iris", "real data",
             ours=f"""
                 m = data[{IRIS}].to_numpy()
                 made = np.column_stack([m[:, :3], m[:, 0] + m[:, 2]])
                 {{"measurements": sdata.number_grid(m.tolist()).find_rank(),
                  "with a made column": sdata.number_grid(made.tolist()).find_rank()}}
             """,
             parent=f"""
                 m = data[{IRIS}].to_numpy()
                 made = np.column_stack([m[:, :3], m[:, 0] + m[:, 2]])
                 {{"measurements": np.linalg.matrix_rank(m), "with a made column": np.linalg.matrix_rank(made)}}
             """, parent_label="NumPy linalg.matrix_rank", parent_tolerance=1e-12,
             r=_code(IRIS_R, """
                 made <- cbind(m[, 1:3], m[, 1] + m[, 3])
                 list(measurements = qr(m)$rank, `with a made column` = qr(made)$rank)
             """), r_tolerance=1e-12),
        Case("grid.find_size", "iris: the Frobenius size and the biggest stretch (2-norm) of the centred 150 x 4 "
             "measurements", "iris", "real data",
             ours=f"""
                 m = data[{IRIS}].to_numpy(); m = m - m.mean(axis=0)
                 grid = sdata.number_grid(m.tolist())
                 {{"frobenius": grid.find_size(), "biggest stretch": grid.find_size(kind="biggest stretch")}}
             """,
             parent=f"""
                 m = data[{IRIS}].to_numpy(); m = m - m.mean(axis=0)
                 {{"frobenius": np.linalg.matrix_norm(m), "biggest stretch": np.linalg.matrix_norm(m, ord=2)}}
             """, parent_label="NumPy linalg.matrix_norm", parent_tolerance=1e-12,
             r=_code(IRIS_R, """
                 m <- scale(m, scale = FALSE)
                 list(frobenius = norm(m, "F"), `biggest stretch` = norm(m, "2"))
             """), r_tolerance=1e-10),
        Case("grid.find_condition_number", "iris: the condition number of the correlation grid of the four "
             "measurements", "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 {{"condition number": grid.find_condition_number()}}
             """,
             parent=f"""
                 {{"condition number": np.linalg.cond(data[{IRIS}].corr().to_numpy())}}
             """, parent_label="NumPy linalg.cond", parent_tolerance=1e-12,
             r=_code(IRIS_R, """
                 list(`condition number` = kappa(cor(m), exact = TRUE))
             """), r_tolerance=1e-10),
        Case("grid.find_column_space", "iris: the column space of the four measurements; the directions it has and "
             "the size of the first column of the projection", "iris", "real data",
             ours=f"""
                 m = data[{IRIS}].to_numpy()
                 q = sdata.number_grid(m.tolist()).find_column_space()
                 projection = q.multiply_as_matrix_by(q.as_numpy().T.tolist())
                 {{"directions": q.count_columns(), "first value": projection.get_number_at(row=1, column=1)}}
             """,
             parent=f"""
                 from scipy import linalg
                 q = linalg.orth(data[{IRIS}].to_numpy())
                 p = q @ q.T
                 {{"directions": q.shape[1], "first value": p[0, 0]}}
             """, parent_label="SciPy linalg.orth", parent_tolerance=1e-10,
             r=_code(IRIS_R, """
                 q <- qr.Q(qr(m)); p <- q %*% t(q)
                 list(directions = ncol(q), `first value` = p[1, 1])
             """), r_tolerance=1e-10,
             note="The basis itself is fixed only up to a rotation, so the projection q q' is compared."),
        Case("grid.take_fourier_transform", "AirPassengers as 12 years x 12 months: the size of the yearly wave "
             "(frequency 1/12 per month) in the 2D Fourier transform", "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 table = grid.take_fourier_transform(show="all")
                 size = table.get_column("size")
                 {"size at 0, 0": size.get_number_at(1), "size at 0, 1": size.get_number_at(2)}
             """),
             parent=_code(AIR_G, """
                 from scipy import fft
                 z = np.abs(fft.fft2(g))
                 {"size at 0, 0": z[0, 0], "size at 0, 1": z[0, 1]}
             """), parent_label="SciPy fft.fft2", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 z <- Mod(fft(g))
                 list(`size at 0, 0` = z[1, 1], `size at 0, 1` = z[1, 2])
             """), r_tolerance=1e-10),
        Case("grid.take_cosine_transform", "AirPassengers as 12 years x 12 months: the first numbers of the 2D cosine "
             "transform (orthonormal)", "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 grid.take_cosine_transform()
                 {"first": grid.get_number_at(row=1, column=1), "second": grid.get_number_at(row=1, column=2)}
             """),
             parent=_code(AIR_G, """
                 from scipy import fft
                 d = fft.dctn(g, type=2, norm="ortho")
                 {"first": d[0, 0], "second": d[0, 1]}
             """), parent_label="SciPy fft.dctn", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 n <- 12; k <- 0:(n - 1); w <- function(i) ifelse(i == 0, sqrt(1 / n), sqrt(2 / n))
                 C <- outer(k, k, function(i, j) w(i) * cos(pi * (2 * j + 1) * i / (2 * n))); d <- C %*% g %*% t(C)
                 list(first = d[1, 1], second = d[1, 2])
             """), r_tolerance=1e-10),
        Case("grid.take_inverse", "iris: the closest possible inverse of the 150 x 4 measurements, as MASS::ginv",
             "iris", "real data", option="closest_possible=",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].to_numpy().tolist())
                 grid.take_inverse(closest_possible=True)
                 {{"first": grid.get_number_at(row=1, column=1), "total": grid.get_all_numbers().find_total()}}
             """,
             parent=f"""
                 from scipy import linalg
                 p = linalg.pinv(data[{IRIS}].to_numpy())
                 {{"first": p[0, 0], "total": p.sum()}}
             """, parent_label="SciPy linalg.pinv", parent_tolerance=1e-10,
             r=_code(IRIS_R, """
                 p <- MASS::ginv(m)
                 list(first = p[1, 1], total = sum(p))
             """), r_packages=("MASS",), r_tolerance=1e-8),
        Case("grid.find_determinant", "iris: the log of the determinant of the covariance grid of the four "
             "measurements", "iris", "real data", option="as_log=",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].cov().to_numpy().tolist())
                 {{"log determinant": grid.find_determinant(as_log=True)}}
             """,
             parent=f"""
                 sign, log_size = np.linalg.slogdet(data[{IRIS}].cov().to_numpy())
                 {{"log determinant": log_size}}
             """, parent_label="NumPy linalg.slogdet", parent_tolerance=1e-12,
             r=_code(IRIS_R, """
                 list(`log determinant` = as.numeric(determinant(cov(m), logarithm = TRUE)$modulus))
             """), r_tolerance=1e-10),
        Case("sdata.number_grid", "AirPassengers: the Toeplitz grid of the first 12 autocovariances; its "
             "determinant", "AirPassengers", "real data", option='kind="toeplitz"',
             ours="""
                 x = np.asarray(data['passengers'], dtype=float); x = x - x.mean()
                 acov = [float(np.dot(x[:len(x) - k], x[k:]) / len(x)) for k in range(12)]
                 grid = sdata.number_grid(kind="toeplitz", first_column=acov)
                 {"log determinant": grid.find_determinant(as_log=True), "corner": grid.get_number_at(row=12, column=1)}
             """,
             parent=_code(AIR_X, """
                 from scipy import linalg
                 x = x - x.mean(); acov = [np.dot(x[:len(x) - k], x[k:]) / len(x) for k in range(12)]
                 t = linalg.toeplitz(acov)
                 {"log determinant": np.linalg.slogdet(t)[1], "corner": t[11, 0]}
             """), parent_label="SciPy linalg.toeplitz", parent_tolerance=1e-10,
             r="""
                 a <- acf(as.numeric(passengers), lag.max = 11, type = "covariance", plot = FALSE)$acf[, 1, 1]
                 t <- toeplitz(a)
                 list(`log determinant` = as.numeric(determinant(t)$modulus), corner = t[12, 1])
             """, r_tolerance=1e-8),
        Case("sdata.make_coordinate_grids", "mtcars: the grid of every weight and horsepower pair of the first 4 "
             "cars; the totals of the two grids", "mtcars", "real data",
             ours="""
                 x_grid, y_grid = sdata.make_coordinate_grids(x=data["wt"].head(4).tolist(),
                                                              y=data["hp"].head(4).tolist())
                 {"x total": x_grid.get_all_numbers().find_total(), "y total": y_grid.get_all_numbers().find_total(),
                  "corner": y_grid.get_number_at(row=4, column=1)}
             """,
             parent="""
                 x_grid, y_grid = np.meshgrid(data["wt"].head(4), data["hp"].head(4))
                 {"x total": x_grid.sum(), "y total": y_grid.sum(), "corner": y_grid[3, 0]}
             """, parent_label="NumPy meshgrid", parent_tolerance=1e-12,
             r="""
                 g <- expand.grid(x = wt[1:4], y = hp[1:4])
                 list(`x total` = sum(g$x), `y total` = sum(g$y), corner = hp[4])
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- batch 13: polynomials
        Case("sdata.polynomial", "iris: the Legendre polynomial of degree 3 at the 150 sepal lengths scaled to "
             "-1 to 1; the total of its values", "iris", "real data",
             ours="""
                 x = data["Sepal.Length"].to_numpy(); s = 2 * (x - x.min()) / (x.max() - x.min()) - 1
                 values = sdata.polynomial("legendre", degree=3).find_value_at(x=s.tolist())
                 {"total": values.find_total(), "biggest": values.find_biggest()}
             """,
             parent="""
                 from scipy import special
                 x = data["Sepal.Length"].to_numpy(); s = 2 * (x - x.min()) / (x.max() - x.min()) - 1
                 v = special.eval_legendre(3, s)
                 {"total": v.sum(), "biggest": v.max()}
             """, parent_label="SciPy special.eval_legendre", parent_tolerance=1e-12,
             r="""
                 s <- 2 * (Sepal.Length - min(Sepal.Length)) / (max(Sepal.Length) - min(Sepal.Length)) - 1
                 v <- (5 * s^3 - 3 * s) / 2
                 list(total = sum(v), biggest = max(v))
             """, r_tolerance=1e-12),
        Case("sdata.polynomial", "mtcars: the polynomial of lowest degree through the fuel use of 4 cars by weight; "
             "its value at 3 tonnes", "mtcars", "real data", option='"through points"',
             ours="""
                 cars = data.head(4)
                 formula = sdata.polynomial("through points", x=cars["wt"].tolist(), y=cars["mpg"].tolist())
                 {"at 3": formula.find_value_at(x=3)}
             """,
             parent="""
                 from scipy import interpolate
                 cars = data.head(4)
                 {"at 3": interpolate.BarycentricInterpolator(cars["wt"], cars["mpg"])(3.0)}
             """, parent_label="SciPy interpolate.BarycentricInterpolator", parent_tolerance=1e-9,
             r="""
                 x <- wt[1:4]; y <- mpg[1:4]; b <- solve(outer(x, 0:3, "^"), y)
                 list(`at 3` = sum(b * 3^(0:3)))
             """, r_tolerance=1e-9),
    ]
