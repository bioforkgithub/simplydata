"""Real-data cases for the number and grid words of phase U3, batch 4 (looking, maths, keeping, order, summaries,
grids and passing the numbers on). cases_underneath.py loads this file and adds cases(Case) to the study.

The data are the study's own: Michelson's 100 speed-of-light measurements (NIST), the AirPassengers series, the
NHANES sample of R's mice package (with empty cells), mtcars and Fisher's iris data. Each case is compared with
NumPy or pandas and, where it is plain base R, with R. Words that print (show, show_first_numbers ...) are
checked on what they print: the printed numbers are read back.
"""

from __future__ import annotations

import textwrap

PRINTED = """
    import contextlib
    import io
    shown = io.StringIO()
    with contextlib.redirect_stdout(shown):
        {call}
    lines = [line for line in shown.getvalue().splitlines() if line.strip()]
    printed = [float(x) for x in " ".join(lines).replace("[", " ").replace("]", " ").replace(",", " ").split()]
"""

IRIS = '["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]'
GRID = f"grid = sdata.number_grid(data[{IRIS}].to_numpy().tolist())\n"
R_GRID = "g <- cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)\n"


def _printed(call: str, then: str) -> str:
    """Code that runs a word that prints, keeping the numbers it printed in `printed`, then the code `then`."""
    return textwrap.dedent(PRINTED).format(call=call) + textwrap.dedent(then)


def _grid(then: str) -> str:
    """Code that makes a grid of the four iris measurements (150 rows, 4 columns), then the code `then`."""
    return GRID + textwrap.dedent(then)


def cases(Case):
    return [
        # ---- looking
        Case("nums.show", "all 100 of Michelson's measurements shown", "NIST Michelso", "real data",
             ours=_printed('sdata.numbers(data["y"].tolist()).show()', """
                 {"numbers shown": len(printed), "total shown": sum(printed)}
             """),
             parent="""
                 {"numbers shown": len(data), "total shown": data["y"].sum()}
             """, parent_label="pandas (every value)", parent_tolerance=1e-12,
             r="""
                 list(`numbers shown` = length(y), `total shown` = sum(y))
             """, r_tolerance=1e-12),
        Case("nums.show_first_numbers", "the first 5 months of AirPassengers shown", "AirPassengers", "real data",
             ours=_printed('sdata.numbers(data["passengers"].tolist()).show_first_numbers(5)', """
                 {"numbers shown": len(printed), "total shown": sum(printed)}
             """),
             parent="""
                 {"numbers shown": 5, "total shown": data["passengers"].head(5).sum()}
             """, parent_label="pandas head", parent_tolerance=0.0,
             r="""
                 list(`total shown` = sum(head(passengers, 5)))
             """, r_tolerance=0.0),
        Case("nums.show_last_numbers", "the 12 months of 1960 in AirPassengers shown", "AirPassengers", "real data",
             ours=_printed('sdata.numbers(data["passengers"].tolist()).show_last_numbers(12)', """
                 {"numbers shown": len(printed), "total shown": sum(printed)}
             """),
             parent="""
                 {"numbers shown": 12, "total shown": data["passengers"].tail(12).sum()}
             """, parent_label="pandas tail", parent_tolerance=0.0,
             r="""
                 list(`total shown` = sum(tail(passengers, 12)))
             """, r_tolerance=0.0),
        Case("nums.get_number_at", "the first and the last month of AirPassengers, counting from 1", "AirPassengers",
             "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 {"month 1": nums.get_number_at(1), "month 144": nums.get_number_at(144),
                  "last": nums.get_number_at("last")}
             """,
             parent="""
                 p = data["passengers"].to_numpy()
                 {"month 1": p[0], "month 144": p[143], "last": p[-1]}
             """, parent_label="NumPy [ ] (from 0)", parent_tolerance=0.0,
             r="""
                 list(`month 1` = passengers[1], `month 144` = passengers[144])
             """, r_tolerance=0.0),
        Case("nums.count", "NHANES body mass index: 25 places, empty ones included", "nhanes (mice)", "real data",
             ours="""
                 {"count": sdata.numbers(data["bmi"].tolist()).count()}
             """,
             parent="""
                 {"count": data["bmi"].to_numpy().size}
             """, parent_label="NumPy size", parent_tolerance=0.0,
             r="""
                 list(count = length(bmi))
             """, r_tolerance=0.0),
        Case("nums.count_empty_numbers", "the empty cells of NHANES body mass index", "nhanes (mice)", "real data",
             ours="""
                 {"empty": sdata.numbers(data["bmi"].tolist()).count_empty_numbers()}
             """,
             parent="""
                 {"empty": int(np.isnan(data["bmi"].to_numpy()).sum())}
             """, parent_label="NumPy isnan", parent_tolerance=0.0,
             r="""
                 list(empty = sum(is.na(bmi)))
             """, r_tolerance=0.0),
        # ---- maths
        Case("nums.add", "1 added to NHANES body mass index: the empty cells stay empty", "nhanes (mice)",
             "real data",
             ours="""
                 nums = sdata.numbers(data["bmi"].tolist())
                 nums.add(1)
                 {"total": nums.find_total(), "empty": nums.count_empty_numbers()}
             """,
             parent="""
                 b = data["bmi"].to_numpy() + 1
                 {"total": np.nansum(b), "empty": int(np.isnan(b).sum())}
             """, parent_label="NumPy +", parent_tolerance=1e-12,
             r="""
                 b <- bmi + 1
                 list(total = sum(b, na.rm = TRUE), empty = sum(is.na(b)))
             """, r_tolerance=1e-12),
        Case("nums.subtract", "Michelson's measurements less 299 (thousand km/s)", "NIST Michelso", "real data",
             ours="""
                 nums = sdata.numbers(data["y"].tolist())
                 nums.subtract(299)
                 {"total": nums.find_total(), "first": nums.get_number_at(1)}
             """,
             parent="""
                 d = data["y"].to_numpy() - 299
                 {"total": d.sum(), "first": d[0]}
             """, parent_label="NumPy -", parent_tolerance=1e-12,
             r="""
                 d <- y - 299
                 list(total = sum(d), first = d[1])
             """, r_tolerance=1e-12),
        Case("nums.times", "mtcars weights from thousands of pounds to pounds", "mtcars", "real data",
             ours="""
                 nums = sdata.numbers(data["wt"].tolist())
                 nums.times(1000)
                 {"total pounds": nums.find_total(), "heaviest": nums.find_biggest()}
             """,
             parent="""
                 w = data["wt"].to_numpy() * 1000
                 {"total pounds": w.sum(), "heaviest": w.max()}
             """, parent_label="NumPy *", parent_tolerance=1e-12,
             r="""
                 list(`total pounds` = sum(wt * 1000), heaviest = max(wt * 1000))
             """, r_tolerance=1e-12),
        Case("nums.divide_by", "mtcars horsepower per thousand pounds, car by car", "mtcars", "real data",
             ours="""
                 nums = sdata.numbers(data["hp"].tolist())
                 nums.divide_by(data["wt"].tolist())
                 {"total": nums.find_total(), "biggest": nums.find_biggest(), "empty": nums.count_empty_numbers()}
             """,
             parent="""
                 r = data["hp"].to_numpy() / data["wt"].to_numpy()
                 {"total": r.sum(), "biggest": r.max(), "empty": 0}
             """, parent_label="NumPy /", parent_tolerance=1e-12,
             r="""
                 list(total = sum(hp / wt), biggest = max(hp / wt))
             """, r_tolerance=1e-12),
        Case("nums.raise_to_power", "iris sepal lengths squared", "iris", "real data",
             ours="""
                 nums = sdata.numbers(data["Sepal.Length"].tolist())
                 nums.raise_to_power(2)
                 {"total": nums.find_total()}
             """,
             parent="""
                 {"total": np.power(data["Sepal.Length"].to_numpy(), 2).sum()}
             """, parent_label="NumPy power", parent_tolerance=1e-12,
             r="""
                 list(total = sum(Sepal.Length^2))
             """, r_tolerance=1e-12),
        Case("nums.take_square_root", "square roots of mtcars engine sizes", "mtcars", "real data",
             ours="""
                 nums = sdata.numbers(data["disp"].tolist())
                 nums.take_square_root()
                 {"total": nums.find_total(), "first": nums.get_number_at(1)}
             """,
             parent="""
                 s = np.sqrt(data["disp"].to_numpy())
                 {"total": s.sum(), "first": s[0]}
             """, parent_label="NumPy sqrt", parent_tolerance=1e-12,
             r="""
                 list(total = sum(sqrt(disp)), first = sqrt(disp[1]))
             """, r_tolerance=1e-12),
        Case("nums.take_absolute_value", "how far each of Michelson's measurements lies from their average",
             "NIST Michelso", "real data",
             ours="""
                 nums = sdata.numbers(data["y"].tolist())
                 nums.subtract(299.8524)
                 nums.take_absolute_value()
                 {"total distance": nums.find_total(), "biggest": nums.find_biggest()}
             """,
             parent="""
                 d = np.abs(data["y"].to_numpy() - 299.8524)
                 {"total distance": d.sum(), "biggest": d.max()}
             """, parent_label="NumPy abs", parent_tolerance=1e-12,
             r="""
                 d <- abs(y - 299.8524)
                 list(`total distance` = sum(d), biggest = max(d))
             """, r_tolerance=1e-12),
        Case("nums.round_to", "mtcars miles per gallon to whole numbers: 21.5 and 15.5 go to the even neighbour",
             "mtcars", "real data",
             ours="""
                 nums = sdata.numbers(data["mpg"].tolist())
                 nums.round_to(0)
                 {"total": nums.find_total(), "Toyota Corona (21.5)": nums.get_number_at(21)}
             """,
             parent="""
                 r = np.round(data["mpg"].to_numpy(), 0)
                 {"total": r.sum(), "Toyota Corona (21.5)": r[20]}
             """, parent_label="NumPy round (halves to even)", parent_tolerance=0.0,
             r="""
                 list(total = sum(round(mpg)), `Toyota Corona (21.5)` = round(mpg[21]))
             """, r_tolerance=0.0),
        Case("nums.take_log", "natural logs of the 144 AirPassengers months", "AirPassengers", "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 nums.take_log()
                 {"total": nums.find_total(), "first": nums.get_number_at(1)}
             """,
             parent="""
                 l = np.log(data["passengers"].to_numpy())
                 {"total": l.sum(), "first": l[0]}
             """, parent_label="NumPy log", parent_tolerance=1e-12,
             r="""
                 list(total = sum(log(passengers)), first = log(passengers[1]))
             """, r_tolerance=1e-12),
        Case("nums.take_exp", "e to the power of each iris petal width", "iris", "real data",
             ours="""
                 nums = sdata.numbers(data["Petal.Width"].tolist())
                 nums.take_exp()
                 {"total": nums.find_total()}
             """,
             parent="""
                 {"total": np.exp(data["Petal.Width"].to_numpy()).sum()}
             """, parent_label="NumPy exp", parent_tolerance=1e-12,
             r="""
                 list(total = sum(exp(Petal.Width)))
             """, r_tolerance=1e-12),
        Case("nums.turn_into_running_total", "AirPassengers added up month by month", "AirPassengers", "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 nums.turn_into_running_total()
                 {"after 12 months": nums.get_number_at(12), "after 144 months": nums.get_number_at("last")}
             """,
             parent="""
                 c = data["passengers"].cumsum()
                 {"after 12 months": c.iloc[11], "after 144 months": c.iloc[-1]}
             """, parent_label="pandas cumsum", parent_tolerance=0.0,
             r="""
                 list(`after 12 months` = cumsum(passengers)[12], `after 144 months` = cumsum(passengers)[144])
             """, r_tolerance=0.0),
        # ---- keeping and removing
        Case("nums.remove_each_number_that", "NHANES body mass index below 25 removed: the empty cells stay",
             "nhanes (mice)", "real data",
             ours="""
                 nums = sdata.numbers(data["bmi"].tolist())
                 nums.remove_each_number_that(is_below=25)
                 {"left": nums.count(), "empty left": nums.count_empty_numbers(), "total": nums.find_total()}
             """,
             parent="""
                 b = data["bmi"].to_numpy()
                 kept = b[~(b < 25)]
                 {"left": kept.size, "empty left": int(np.isnan(kept).sum()), "total": np.nansum(kept)}
             """, parent_label="NumPy boolean indexing", parent_tolerance=1e-12,
             r="""
                 kept <- bmi[is.na(bmi) | !(bmi < 25)]
                 list(left = length(kept), `empty left` = sum(is.na(kept)), total = sum(kept, na.rm = TRUE))
             """, r_tolerance=1e-12),
        Case("nums.keep_first_numbers", "the 12 months of 1949 in AirPassengers", "AirPassengers", "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 nums.keep_first_numbers(12)
                 {"kept": nums.count(), "total": nums.find_total()}
             """,
             parent="""
                 {"kept": 12, "total": data["passengers"].to_numpy()[:12].sum()}
             """, parent_label="NumPy [:12]", parent_tolerance=0.0,
             r="""
                 list(total = sum(head(passengers, 12)))
             """, r_tolerance=0.0),
        Case("nums.keep_last_numbers", "the 12 months of 1960 in AirPassengers", "AirPassengers", "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 nums.keep_last_numbers(12)
                 {"kept": nums.count(), "total": nums.find_total()}
             """,
             parent="""
                 {"kept": 12, "total": data["passengers"].to_numpy()[-12:].sum()}
             """, parent_label="NumPy [-12:]", parent_tolerance=0.0,
             r="""
                 list(total = sum(tail(passengers, 12)))
             """, r_tolerance=0.0),
        Case("nums.keep_random_numbers", "10 of Michelson's measurements picked at random (seed 1)", "NIST Michelso",
             "real data",
             ours="""
                 nums = sdata.numbers(data["y"].tolist())
                 nums.keep_random_numbers(10, with_seed=1)
                 {"kept": nums.count(), "total": nums.find_total(), "first kept": nums.get_number_at(1)}
             """,
             parent="""
                 y = data["y"].to_numpy()
                 picked = np.sort(np.random.default_rng(1).choice(y.size, size=10, replace=False))
                 {"kept": 10, "total": y[picked].sum(), "first kept": y[picked][0]}
             """, parent_label="NumPy default_rng choice, kept in order", parent_tolerance=1e-12),
        Case("nums.remove_duplicate_numbers", "the different values among Michelson's measurements, in first-seen "
             "order", "NIST Michelso", "real data",
             ours="""
                 nums = sdata.numbers(data["y"].tolist())
                 nums.remove_duplicate_numbers()
                 {"different": nums.count(), "total": nums.find_total(), "third": nums.get_number_at(3)}
             """,
             parent="""
                 u = data["y"].drop_duplicates(keep="first").to_numpy()
                 {"different": u.size, "total": u.sum(), "third": u[2]}
             """, parent_label="pandas drop_duplicates", parent_tolerance=1e-12,
             r="""
                 u <- unique(y)
                 list(different = length(u), total = sum(u), third = u[3])
             """, r_tolerance=1e-12),
        Case("nums.remove_empty_numbers", "NHANES cholesterol without its empty cells", "nhanes (mice)", "real data",
             ours="""
                 nums = sdata.numbers(data["chl"].tolist())
                 nums.remove_empty_numbers()
                 {"left": nums.count(), "total": nums.find_total()}
             """,
             parent="""
                 c = data["chl"].to_numpy()
                 kept = c[~np.isnan(c)]
                 {"left": kept.size, "total": kept.sum()}
             """, parent_label="NumPy isnan", parent_tolerance=1e-12,
             r="""
                 kept <- chl[!is.na(chl)]
                 list(left = length(kept), total = sum(kept))
             """, r_tolerance=1e-12),
        Case("nums.keep_numbers_by_position", "months 13 to 24 (1950) of AirPassengers", "AirPassengers", "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 nums.keep_numbers_by_position(13, to=24)
                 {"kept": nums.count(), "total": nums.find_total()}
             """,
             parent="""
                 kept = data["passengers"].to_numpy()[12:24]
                 {"kept": kept.size, "total": kept.sum()}
             """, parent_label="NumPy [12:24]", parent_tolerance=0.0,
             r="""
                 list(kept = length(passengers[13:24]), total = sum(passengers[13:24]))
             """, r_tolerance=0.0),
        Case("nums.remove_numbers_by_position", "AirPassengers without its first year", "AirPassengers", "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 nums.remove_numbers_by_position(1, to=12)
                 {"left": nums.count(), "total": nums.find_total()}
             """,
             parent="""
                 left = np.delete(data["passengers"].to_numpy(), np.arange(0, 12))
                 {"left": left.size, "total": left.sum()}
             """, parent_label="NumPy delete", parent_tolerance=0.0,
             r="""
                 left <- passengers[-(1:12)]
                 list(left = length(left), total = sum(left))
             """, r_tolerance=0.0),
        Case("nums.replace_each_number_that", "NHANES body mass index above 30 set to 30: the empty cells stay empty",
             "nhanes (mice)", "real data",
             ours="""
                 nums = sdata.numbers(data["bmi"].tolist())
                 nums.replace_each_number_that(is_above=30, with_value=30)
                 {"total": nums.find_total(), "empty": nums.count_empty_numbers(), "biggest": nums.find_biggest()}
             """,
             parent="""
                 b = data["bmi"].to_numpy()
                 r = np.where(b > 30, 30, b)
                 {"total": np.nansum(r), "empty": int(np.isnan(r).sum()), "biggest": np.nanmax(r)}
             """, parent_label="NumPy where", parent_tolerance=1e-12,
             r="""
                 b <- bmi
                 b[!is.na(b) & b > 30] <- 30
                 list(total = sum(b, na.rm = TRUE), empty = sum(is.na(b)), biggest = max(b, na.rm = TRUE))
             """, r_tolerance=1e-12),
        Case("nums.fill_empty_numbers", "NHANES body mass index: gaps filled on the line between neighbours",
             "nhanes (mice)", "real data",
             ours="""
                 nums = sdata.numbers(data["bmi"].tolist())
                 nums.fill_empty_numbers(with_the="line between neighbours")
                 {"total": nums.find_total(), "empty left": nums.count_empty_numbers()}
             """,
             parent="""
                 f = data["bmi"].interpolate(limit_area="inside")
                 {"total": f.sum(), "empty left": int(f.isna().sum())}
             """, parent_label="pandas interpolate (inside)", parent_tolerance=1e-12,
             r="""
                 f <- approx(seq_along(bmi), bmi, xout = seq_along(bmi), rule = 1)$y
                 list(total = sum(f, na.rm = TRUE), `empty left` = sum(is.na(f)))
             """, r_tolerance=1e-12),
        # ---- order
        Case("nums.sort", "NHANES body mass index biggest first, the empty cells last", "nhanes (mice)", "real data",
             ours="""
                 nums = sdata.numbers(data["bmi"].tolist())
                 nums.sort(biggest_first=True)
                 {"first": nums.get_number_at(1), "16th": nums.get_number_at(16),
                  "empty at the end": nums.count_empty_numbers()}
             """,
             parent="""
                 s = data["bmi"].sort_values(ascending=False, na_position="last").to_numpy()
                 {"first": s[0], "16th": s[15], "empty at the end": int(np.isnan(s[16:]).sum())}
             """, parent_label="pandas sort_values (empty last)", parent_tolerance=0.0,
             r="""
                 s <- sort(bmi, decreasing = TRUE, na.last = TRUE)
                 list(first = s[1], `16th` = s[16], `empty at the end` = sum(is.na(s[17:25])))
             """, r_tolerance=0.0),
        Case("nums.reverse", "AirPassengers from the last month back", "AirPassengers", "real data",
             ours="""
                 nums = sdata.numbers(data["passengers"].tolist())
                 nums.reverse()
                 {"first": nums.get_number_at(1), "last": nums.get_number_at("last")}
             """,
             parent="""
                 r = data["passengers"].to_numpy()[::-1]
                 {"first": r[0], "last": r[-1]}
             """, parent_label="NumPy [::-1]", parent_tolerance=0.0,
             r="""
                 r <- rev(passengers)
                 list(first = r[1], last = r[144])
             """, r_tolerance=0.0),
        # ---- summaries
        Case("nums.find_total", "the total of NHANES body mass index, empty cells skipped", "nhanes (mice)",
             "real data",
             ours="""
                 {"total": sdata.numbers(data["bmi"].tolist()).find_total()}
             """,
             parent="""
                 {"total": np.nansum(data["bmi"].to_numpy())}
             """, parent_label="NumPy nansum", parent_tolerance=1e-12,
             r="""
                 list(total = sum(bmi, na.rm = TRUE))
             """, r_tolerance=1e-12),
        Case("nums.find_smallest", "the smallest NHANES body mass index, empty cells skipped", "nhanes (mice)",
             "real data",
             ours="""
                 {"smallest": sdata.numbers(data["bmi"].tolist()).find_smallest()}
             """,
             parent="""
                 {"smallest": np.nanmin(data["bmi"].to_numpy())}
             """, parent_label="NumPy nanmin", parent_tolerance=0.0,
             r="""
                 list(smallest = min(bmi, na.rm = TRUE))
             """, r_tolerance=0.0),
        Case("nums.find_biggest", "the biggest NHANES body mass index, empty cells skipped", "nhanes (mice)",
             "real data",
             ours="""
                 {"biggest": sdata.numbers(data["bmi"].tolist()).find_biggest()}
             """,
             parent="""
                 {"biggest": np.nanmax(data["bmi"].to_numpy())}
             """, parent_label="NumPy nanmax", parent_tolerance=0.0,
             r="""
                 list(biggest = max(bmi, na.rm = TRUE))
             """, r_tolerance=0.0),
        Case("nums.find_standard_deviation", "the standard deviation of NHANES cholesterol, empty cells skipped",
             "nhanes (mice)", "real data",
             ours="""
                 {"standard deviation": sdata.numbers(data["chl"].tolist()).find_standard_deviation()}
             """,
             parent="""
                 {"standard deviation": np.nanstd(data["chl"].to_numpy(), ddof=1)}
             """, parent_label="NumPy nanstd (ddof=1)", parent_tolerance=1e-12,
             r="""
                 list(`standard deviation` = sd(chl, na.rm = TRUE))
             """, r_tolerance=1e-12),
        Case("nums.count_each", "how many mtcars cars have 4, 6 and 8 cylinders", "mtcars", "real data",
             ours="""
                 counts = sdata.numbers(data["cyl"].tolist()).count_each()
                 {"first number": counts.get_cell_at(row=1, column="number"),
                  "its count": counts.get_cell_at(row=1, column="count"),
                  "its percent": counts.get_cell_at(row=1, column="percent"),
                  "count of 6": counts.get_cell_at(row=3, column="count")}
             """,
             parent="""
                 c = data["cyl"].value_counts()
                 {"first number": c.index[0], "its count": c.iloc[0], "its percent": round(c.iloc[0] * 100 / 32, 1),
                  "count of 6": c[6]}
             """, parent_label="pandas value_counts", parent_tolerance=0.0,
             r="""
                 t <- table(cyl)
                 list(`its count` = max(t), `count of 6` = t[["6"]])
             """, r_tolerance=0.0),
        Case("nums.make_number_grid", "AirPassengers as a grid of 12 years by 12 months", "AirPassengers",
             "real data",
             ours="""
                 grid = sdata.numbers(data["passengers"].tolist()).make_number_grid(columns=12)
                 {"rows": grid.count_rows(), "all Julys": grid.get_column(7).find_total(),
                  "1955": grid.get_row(7).find_total()}
             """,
             parent="""
                 g = data["passengers"].to_numpy().reshape(-1, 12)
                 {"rows": g.shape[0], "all Julys": g[:, 6].sum(), "1955": g[6].sum()}
             """, parent_label="NumPy reshape (row after row)", parent_tolerance=0.0,
             r="""
                 m <- matrix(passengers, ncol = 12, byrow = TRUE)
                 list(rows = nrow(m), `all Julys` = sum(m[, 7]), `1955` = sum(m[7, ]))
             """, r_tolerance=0.0),
        # ---- grids
        Case("grid.count_rows", "the 150 iris flowers as rows of a grid", "iris", "real data",
             ours=_grid("""
                 {"rows": grid.count_rows()}
             """),
             parent=f"""
                 {{"rows": data[{IRIS}].to_numpy().shape[0]}}
             """, parent_label="NumPy shape", parent_tolerance=0.0,
             r=R_GRID + """
                 list(rows = nrow(g))
             """, r_tolerance=0.0),
        Case("grid.count_columns", "the 4 iris measurements as columns of a grid", "iris", "real data",
             ours=_grid("""
                 {"columns": grid.count_columns()}
             """),
             parent=f"""
                 {{"columns": data[{IRIS}].to_numpy().shape[1]}}
             """, parent_label="NumPy shape", parent_tolerance=0.0,
             r=R_GRID + """
                 list(columns = ncol(g))
             """, r_tolerance=0.0),
        Case("grid.find_shape", "the shape of the iris measurements as a grid", "iris", "real data",
             ours=_grid("""
                 rows, columns = grid.find_shape()
                 {"rows": rows, "columns": columns}
             """),
             parent=f"""
                 rows, columns = data[{IRIS}].to_numpy().shape
                 {{"rows": rows, "columns": columns}}
             """, parent_label="NumPy shape", parent_tolerance=0.0,
             r=R_GRID + """
                 list(rows = dim(g)[1], columns = dim(g)[2])
             """, r_tolerance=0.0),
        Case("grid.show_first_rows", "the first 3 iris flowers of the grid shown", "iris", "real data",
             ours=GRID + _printed("grid.show_first_rows(3)", """
                 {"numbers shown": len(printed), "total shown": sum(printed)}
             """),
             parent=f"""
                 first = data[{IRIS}].to_numpy()[:3]
                 {{"numbers shown": first.size, "total shown": first.sum()}}
             """, parent_label="NumPy [:3]", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(`total shown` = sum(g[1:3, ]))
             """, r_tolerance=1e-12),
        Case("grid.show_last_rows", "the last 3 iris flowers of the grid shown", "iris", "real data",
             ours=GRID + _printed("grid.show_last_rows(3)", """
                 {"numbers shown": len(printed), "total shown": sum(printed)}
             """),
             parent=f"""
                 last = data[{IRIS}].to_numpy()[-3:]
                 {{"numbers shown": last.size, "total shown": last.sum()}}
             """, parent_label="NumPy [-3:]", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(`total shown` = sum(g[148:150, ]))
             """, r_tolerance=1e-12),
        Case("grid.get_number_at", "the petal length of the last iris flower, counting from 1", "iris", "real data",
             ours=_grid("""
                 {"row 150, column 3": grid.get_number_at(row=150, column=3),
                  "row 1, column 1": grid.get_number_at(row=1, column=1)}
             """),
             parent=f"""
                 g = data[{IRIS}].to_numpy()
                 {{"row 150, column 3": g[149, 2], "row 1, column 1": g[0, 0]}}
             """, parent_label="NumPy [ ] (from 0)", parent_tolerance=0.0,
             r=R_GRID + """
                 list(`row 150, column 3` = g[150, 3], `row 1, column 1` = g[1, 1])
             """, r_tolerance=0.0),
        Case("grid.get_row", "the four measurements of the first iris flower", "iris", "real data",
             ours=_grid("""
                 row = grid.get_row(1)
                 {"numbers": row.count(), "total": row.find_total()}
             """),
             parent=f"""
                 row = data[{IRIS}].to_numpy()[0]
                 {{"numbers": row.size, "total": row.sum()}}
             """, parent_label="NumPy [0]", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(numbers = length(g[1, ]), total = sum(g[1, ]))
             """, r_tolerance=1e-12),
        Case("grid.get_column", "the 150 iris petal lengths, column 3 of the grid", "iris", "real data",
             ours=_grid("""
                 column = grid.get_column(3)
                 {"numbers": column.count(), "total": column.find_total()}
             """),
             parent=f"""
                 column = data[{IRIS}].to_numpy()[:, 2]
                 {{"numbers": column.size, "total": column.sum()}}
             """, parent_label="NumPy [:, 2]", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(numbers = length(g[, 3]), total = sum(g[, 3]))
             """, r_tolerance=1e-12),
        Case("grid.get_all_numbers", "all 600 iris measurements as one list, row by row", "iris", "real data",
             ours=_grid("""
                 nums = grid.get_all_numbers()
                 {"numbers": nums.count(), "total": nums.find_total(), "fifth": nums.get_number_at(5)}
             """),
             parent=f"""
                 flat = data[{IRIS}].to_numpy().ravel()
                 {{"numbers": flat.size, "total": flat.sum(), "fifth": flat[4]}}
             """, parent_label="NumPy ravel (row by row)", parent_tolerance=1e-12,
             r=R_GRID + """
                 flat <- as.vector(t(g))
                 list(numbers = length(flat), total = sum(flat), fifth = flat[5])
             """, r_tolerance=1e-12),
        Case("grid.keep_rows_by_position", "rows 51 to 100 of the iris grid: the versicolor flowers", "iris",
             "real data",
             ours=_grid("""
                 grid.keep_rows_by_position(51, to=100)
                 {"rows": grid.count_rows(), "total sepal length": grid.get_column(1).find_total()}
             """),
             parent=f"""
                 kept = data[{IRIS}].to_numpy()[50:100]
                 {{"rows": kept.shape[0], "total sepal length": kept[:, 0].sum()}}
             """, parent_label="NumPy [50:100]", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(rows = nrow(g[51:100, ]), `total sepal length` = sum(g[51:100, 1]))
             """, r_tolerance=1e-12),
        Case("grid.keep_columns_by_position", "columns 3 to 4 of the iris grid: the petals", "iris", "real data",
             ours=_grid("""
                 grid.keep_columns_by_position(3, to=4)
                 {"columns": grid.count_columns(), "total": grid.find_total()}
             """),
             parent=f"""
                 kept = data[{IRIS}].to_numpy()[:, 2:4]
                 {{"columns": kept.shape[1], "total": kept.sum()}}
             """, parent_label="NumPy [:, 2:4]", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(columns = ncol(g[, 3:4]), total = sum(g[, 3:4]))
             """, r_tolerance=1e-12),
        Case("grid.remove_rows_by_position", "the iris grid without its first 50 rows (setosa)", "iris",
             "real data",
             ours=_grid("""
                 grid.remove_rows_by_position(1, to=50)
                 {"rows": grid.count_rows(), "total petal length": grid.get_column(3).find_total()}
             """),
             parent=f"""
                 left = np.delete(data[{IRIS}].to_numpy(), np.arange(0, 50), axis=0)
                 {{"rows": left.shape[0], "total petal length": left[:, 2].sum()}}
             """, parent_label="NumPy delete", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(rows = nrow(g[-(1:50), ]), `total petal length` = sum(g[-(1:50), 3]))
             """, r_tolerance=1e-12),
        Case("grid.remove_columns_by_position", "columns 1 and 3 (the lengths) removed from the iris grid", "iris",
             "real data",
             ours=_grid("""
                 grid.remove_columns_by_position(1, step=2)
                 {"columns": grid.count_columns(), "total of the widths": grid.find_total()}
             """),
             parent=f"""
                 left = np.delete(data[{IRIS}].to_numpy(), np.s_[0::2], axis=1)
                 {{"columns": left.shape[1], "total of the widths": left.sum()}}
             """, parent_label="NumPy delete", parent_tolerance=1e-12,
             r=R_GRID + """
                 list(columns = ncol(g[, c(2, 4)]), `total of the widths` = sum(g[, c(2, 4)]))
             """, r_tolerance=1e-12),
        Case("grid.replace_each_number_that", "iris measurements below 1 cm set to 0 where they are", "iris",
             "real data",
             ours=_grid("""
                 grid.replace_each_number_that(is_below=1, with_value=0)
                 rows, columns = grid.find_shape()
                 {"rows": rows, "total": grid.find_total(), "petal width total": grid.get_column(4).find_total()}
             """),
             parent=f"""
                 g = data[{IRIS}].to_numpy()
                 r = np.where(g < 1, 0, g)
                 {{"rows": r.shape[0], "total": r.sum(), "petal width total": r[:, 3].sum()}}
             """, parent_label="NumPy where", parent_tolerance=1e-12,
             r=R_GRID + """
                 g[g < 1] <- 0
                 list(rows = nrow(g), total = sum(g), `petal width total` = sum(g[, 4]))
             """, r_tolerance=1e-12),
        Case("grid.swap_rows_and_columns", "the iris grid turned round: 4 rows of 150 flowers", "iris", "real data",
             ours=_grid("""
                 grid.swap_rows_and_columns()
                 rows, columns = grid.find_shape()
                 {"rows": rows, "columns": columns, "row 3, column 150": grid.get_number_at(row=3, column=150)}
             """),
             parent=f"""
                 t = data[{IRIS}].to_numpy().T
                 {{"rows": t.shape[0], "columns": t.shape[1], "row 3, column 150": t[2, 149]}}
             """, parent_label="NumPy .T", parent_tolerance=0.0,
             r=R_GRID + """
                 tg <- t(g)
                 list(rows = nrow(tg), columns = ncol(tg), `row 3, column 150` = tg[3, 150])
             """, r_tolerance=0.0),
        # ---- passing the numbers on
        Case("nums.turn_into_table", "Michelson's measurements as a table of one column", "NIST Michelso",
             "real data",
             ours="""
                 table = sdata.numbers(data["y"].tolist()).turn_into_table()
                 {"columns": len(table.get_column_names()), "total": table.get_column("value").find_total()}
             """,
             parent="""
                 df = pd.DataFrame({"value": data["y"].to_numpy()})
                 {"columns": df.shape[1], "total": df["value"].sum()}
             """, parent_label="pandas DataFrame", parent_tolerance=1e-12),
        Case("nums.start_chart", "a histogram of Michelson's measurements, started from the numbers",
             "NIST Michelso", "real data",
             ours="""
                 from simplydata._underneath.check import chart_facts
                 chart = sdata.numbers(data["y"].tolist()).start_chart()
                 bars = chart_facts(chart.draw_histogram(x="value")._render().axes[0])["bars"]
                 {"bars": len(bars), "numbers counted": sum(b[3] for b in bars), "tallest": max(b[3] for b in bars)}
             """,
             parent="""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 from simplydata._underneath.check import chart_facts
                 fig, ax = plt.subplots()
                 sns.histplot(pd.DataFrame({"value": data["y"]}), x="value", bins=10, ax=ax)
                 bars = chart_facts(ax)["bars"]
                 {"bars": len(bars), "numbers counted": sum(b[3] for b in bars), "tallest": max(b[3] for b in bars)}
             """, parent_label="seaborn histplot (10 bins)", parent_tolerance=0.0,
             r="""
                 counts <- hist(y, breaks = seq(min(y), max(y), length.out = 11), plot = FALSE)$counts
                 list(bars = length(counts), `numbers counted` = sum(counts))
             """, r_tolerance=0.0),
        Case("nums.save", "Michelson's measurements saved as CSV and read back", "NIST Michelso", "real data",
             ours="""
                 import os
                 import tempfile
                 with tempfile.TemporaryDirectory() as folder:
                     sdata.numbers(data["y"].tolist()).save(os.path.join(folder, "michelson.csv"))
                     back = sdata.table(os.path.join(folder, "michelson.csv"), separator=",")
                 values = back.get_column("value")
                 {"rows": values.count(), "total": values.find_total(), "columns": len(back.get_column_names())}
             """,
             parent="""
                 import os
                 import tempfile
                 with tempfile.TemporaryDirectory() as folder:
                     pd.DataFrame({"value": data["y"]}).to_csv(os.path.join(folder, "michelson.csv"), index=False)
                     back = pd.read_csv(os.path.join(folder, "michelson.csv"))
                 {"rows": len(back), "total": back["value"].sum(), "columns": back.shape[1]}
             """, parent_label="pandas to_csv and read_csv", parent_tolerance=1e-12),
        Case("nums.as_numpy", "Michelson's measurements handed on as a NumPy array", "NIST Michelso", "real data",
             ours="""
                 array = sdata.numbers(data["y"].tolist()).as_numpy()
                 {"numbers": array.size, "total": array.sum()}
             """,
             parent="""
                 array = data["y"].to_numpy().copy()
                 {"numbers": array.size, "total": array.sum()}
             """, parent_label="NumPy array", parent_tolerance=0.0,
             r="""
                 list(numbers = length(y), total = sum(y))
             """, r_tolerance=1e-12),
    ]
