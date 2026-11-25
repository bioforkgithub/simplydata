"""Real-data cases for the NumPy + SciPy phase, batch 1 (approved by Manish 2026-11-25): yes or no values, rounding,
angles, positions, every pair, whole division, the Fourier option with_zero_in_middle=, and blocks of numbers with any
number of directions. cases_underneath.py loads this file and adds cases(Case) to the study.

The data are the study's own: Fisher's iris data (as a block of 3 species x 50 flowers x 4 measurements), the
AirPassengers series (as a block of 12 years x 12 months), the Lake Huron levels and Michelson's speed-of-light
measurements (NIST). Each case is compared with NumPy (pandas or SciPy where they do the work) and with base R.
simplydata's side reads its results with simplydata words (get_all_numbers, find_shape ...); the NumPy side and R
flatten in the same order (the last direction fastest), so every number is compared, not only a summary.

Three words have nothing underneath to compare (block.find_direction_names, sdata.hide_stretching_notes and
sdata.show_stretching_notes: names kept next to the array, and a setting), so they have no case.
"""

from __future__ import annotations

import textwrap

MEASURES = '["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]'

# iris as a block: 3 species x 50 flowers x 4 measurements (the rows are in species order: 50 of each)
IRIS_BLOCK = f"""
    rows = sdata.number_block(data[{MEASURES}].to_numpy().tolist())
    rows.change_shape_to(3, 50, 4)
    block = sdata.number_block(rows, directions_named=["species", "flower", "measurement"])
"""
IRIS_NUMPY = f"""
    import numpy as np
    a = data[{MEASURES}].to_numpy().reshape(3, 50, 4)
"""
R_FLAT = ("flat <- function(x) { v <- if (is.null(dim(x))) as.vector(x) else as.vector(aperm(x)); "
          "setNames(as.list(as.numeric(v)), as.character(seq_along(v) - 1)) }\n")
R_IRIS = (R_FLAT + "m <- cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)\n"
          "a <- aperm(array(m, dim = c(50, 3, 4)), c(2, 1, 3))\n")

# AirPassengers as a block from its table: 12 years x 12 months, with the years and months as labels
AIR_TABLE = """
    t = data.assign(year=data["month"].str[:4].astype(int), month_of_year=data["month"].str[5:7].astype(int))
    block = sdata.number_block(sdata.table(t), directions_named=["year", "month_of_year"], values="passengers")
"""
AIR_NUMPY = """
    import numpy as np
    m = data["passengers"].to_numpy().reshape(12, 12)
    years = np.arange(1949, 1961)
"""
R_AIR = R_FLAT + "m <- matrix(passengers, nrow = 12, byrow = TRUE)\nyears <- 1949:1960\n"

# the month of each AirPassengers row as an angle on the year's circle
MONTH_ANGLES = """
    months = data["month"].str[5:7].astype(int)
"""
R_MONTHS = R_FLAT + "mo <- as.integer(substr(month, 6, 7))\n"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts) + "\n"


def _ours_flat(result: str) -> str:
    """simplydata's side: every number of a block, grid or numbers, read with simplydata words."""
    return f"{{str(i): v for i, v in enumerate({result})}}"


NP_FLAT = "{str(i): float(v) for i, v in enumerate(np.ravel(x))}"


def cases(Case):
    iris = dict(dataset="iris", kind="real data")
    air = dict(dataset="AirPassengers", kind="real data")
    huron = dict(dataset="Lake Huron", kind="real data")

    def block_case(word, title, step, numpy, r, option="", tolerance=0.0, numbers="block.get_all_numbers()"):
        return Case(word, title, **iris, option=option,
                    ours=_code(IRIS_BLOCK, step, _ours_flat(numbers)),
                    parent=_code(IRIS_NUMPY, numpy, NP_FLAT), parent_label="NumPy", parent_tolerance=tolerance,
                    r=R_IRIS + r + "\nflat(x)", r_tolerance=max(tolerance, 1e-12))

    def air_case(word, title, step, numpy, r, numbers="block.get_all_numbers()", tolerance=0.0):
        return Case(word, title, **air,
                    ours=_code(AIR_TABLE, step, _ours_flat(numbers)),
                    parent=_code(AIR_NUMPY, numpy, NP_FLAT), parent_label="NumPy", parent_tolerance=tolerance,
                    r=R_AIR + r + "\nflat(x)", r_tolerance=max(tolerance, 1e-12))

    return [
        # ---------------------------------------------------------------- yes or no values
        Case("nums.turn_into_yes_or_no", "Michelson's measurements above 299.85 (thousand km/s)", "NIST Michelso",
             "real data",
             ours=_code("""
                 fast = sdata.numbers(data["y"].tolist()).turn_into_yes_or_no(is_above=299.85)
             """, _ours_flat("fast")),
             parent=_code("""
                 import numpy as np
                 x = data["y"].to_numpy() > 299.85
             """, NP_FLAT), parent_label="NumPy (a comparison)", parent_tolerance=0.0,
             r=R_FLAT + "flat(as.numeric(y > 299.85))", r_tolerance=0.0),
        Case("nums.keep_numbers_where", "iris: the petal lengths of the flowers with sepals above 6 cm", **iris,
             ours=_code("""
                 long_sepal = sdata.numbers(data["Sepal.Length"].tolist()).turn_into_yes_or_no(is_above=6)
                 petals = sdata.numbers(data["Petal.Length"].tolist()).keep_numbers_where(long_sepal)
             """, _ours_flat("petals")),
             parent=_code("""
                 import numpy as np
                 x = data["Petal.Length"].to_numpy()[data["Sepal.Length"].to_numpy() > 6]
             """, NP_FLAT), parent_label="NumPy boolean indexing", parent_tolerance=0.0,
             r=R_FLAT + "flat(Petal.Length[Sepal.Length > 6])", r_tolerance=0.0),
        Case("nums.remove_numbers_where", "iris: the petal lengths left when sepals above 6 cm are removed", **iris,
             ours=_code("""
                 long_sepal = sdata.numbers(data["Sepal.Length"].tolist()).turn_into_yes_or_no(is_above=6)
                 petals = sdata.numbers(data["Petal.Length"].tolist()).remove_numbers_where(long_sepal)
             """, _ours_flat("petals")),
             parent=_code("""
                 import numpy as np
                 x = data["Petal.Length"].to_numpy()[~(data["Sepal.Length"].to_numpy() > 6)]
             """, NP_FLAT), parent_label="NumPy boolean indexing", parent_tolerance=0.0,
             r=R_FLAT + "flat(Petal.Length[!(Sepal.Length > 6)])", r_tolerance=0.0),
        Case("nums.replace_numbers_where", "iris: petal lengths set to 0 where the sepal is above 6 cm", **iris,
             ours=_code("""
                 long_sepal = sdata.numbers(data["Sepal.Length"].tolist()).turn_into_yes_or_no(is_above=6)
                 petals = sdata.numbers(data["Petal.Length"].tolist()).replace_numbers_where(long_sepal, with_value=0)
             """, _ours_flat("petals")),
             parent=_code("""
                 import numpy as np
                 x = np.where(data["Sepal.Length"].to_numpy() > 6, 0, data["Petal.Length"].to_numpy())
             """, NP_FLAT), parent_label="NumPy where", parent_tolerance=0.0,
             r=R_FLAT + "flat(ifelse(Sepal.Length > 6, 0, Petal.Length))", r_tolerance=0.0),
        Case("nums.count_numbers_that", "how many of Michelson's 100 measurements are above 299.85", "NIST Michelso",
             "real data",
             ours="""
                 {"count": sdata.numbers(data["y"].tolist()).count_numbers_that(is_above=299.85)}
             """,
             parent="""
                 import numpy as np
                 {"count": np.count_nonzero(data["y"].to_numpy() > 299.85)}
             """, parent_label="NumPy count_nonzero", parent_tolerance=0.0,
             r="list(count = sum(y > 299.85))", r_tolerance=0.0),
        Case("nums.check_if_any_number", "iris: is any petal wider than 2.4 cm?", **iris,
             ours="""
                 {"answer": float(sdata.numbers(data["Petal.Width"].tolist()).check_if_any_number(is_above=2.4))}
             """,
             parent="""
                 import numpy as np
                 {"answer": float(np.any(data["Petal.Width"].to_numpy() > 2.4))}
             """, parent_label="NumPy any", parent_tolerance=0.0,
             r="list(answer = as.numeric(any(Petal.Width > 2.4)))", r_tolerance=0.0),
        Case("nums.check_if_all_numbers", "iris: is every sepal at least 2 cm wide?", **iris,
             ours="""
                 {"answer": float(sdata.numbers(data["Sepal.Width"].tolist()).check_if_all_numbers(is_at_least=2))}
             """,
             parent="""
                 import numpy as np
                 {"answer": float(np.all(data["Sepal.Width"].to_numpy() >= 2))}
             """, parent_label="NumPy all", parent_tolerance=0.0,
             r="list(answer = as.numeric(all(Sepal.Width >= 2)))", r_tolerance=0.0),
        Case("nums.check_if_same_as", "Lake Huron: the levels and the levels rounded to 0.1 ft agree within 0.06",
             **huron,
             ours="""
                 levels = sdata.numbers(data["level"].tolist())
                 rounded = sdata.numbers(data["level"].tolist()).round_to(1)
                 {"same": float(levels.check_if_same_as(rounded, within=0.06)),
                  "same within 0.04": float(levels.check_if_same_as(rounded, within=0.04))}
             """,
             parent="""
                 import numpy as np
                 x = data["level"].to_numpy()
                 {"same": float(np.allclose(x, np.round(x, 1), rtol=0, atol=0.06)),
                  "same within 0.04": float(np.allclose(x, np.round(x, 1), rtol=0, atol=0.04))}
             """, parent_label="NumPy allclose(rtol=0, atol=within)", parent_tolerance=0.0,
             r="list(same = as.numeric(all(abs(level - round(level, 1)) <= 0.06)), "
               "`same within 0.04` = as.numeric(all(abs(level - round(level, 1)) <= 0.04)))", r_tolerance=0.0),
        Case("grid.keep_rows_where", "iris: the flowers (rows) whose petal length is above 5 cm", **iris,
             ours=_code(f"""
                 grid = sdata.number_grid(data[{MEASURES}].to_numpy().tolist())
                 grid.keep_rows_where(column=3, is_above=5)
             """, _ours_flat("grid.get_all_numbers()")),
             parent=_code(f"""
                 import numpy as np
                 g = data[{MEASURES}].to_numpy()
                 x = g[g[:, 2] > 5]
             """, NP_FLAT), parent_label="NumPy boolean indexing", parent_tolerance=0.0,
             r=R_IRIS + "flat(m[m[, 3] > 5, ])", r_tolerance=0.0),
        Case("grid.remove_rows_where", "iris: the flowers left when sepals below 5 cm are removed", **iris,
             ours=_code(f"""
                 grid = sdata.number_grid(data[{MEASURES}].to_numpy().tolist())
                 grid.remove_rows_where(column=1, is_below=5)
             """, _ours_flat("grid.get_all_numbers()")),
             parent=_code(f"""
                 import numpy as np
                 g = data[{MEASURES}].to_numpy()
                 x = g[~(g[:, 0] < 5)]
             """, NP_FLAT), parent_label="NumPy boolean indexing", parent_tolerance=0.0,
             r=R_IRIS + "flat(m[!(m[, 1] < 5), ])", r_tolerance=0.0),
        # ---------------------------------------------------------------- rounding, angles and positions
        Case("nums.round_down", "Lake Huron levels rounded down to whole feet", **huron,
             ours=_code('levels = sdata.numbers(data["level"].tolist()).round_down()', _ours_flat("levels")),
             parent=_code("import numpy as np\nx = np.floor(data['level'].to_numpy())", NP_FLAT),
             parent_label="NumPy floor", parent_tolerance=0.0, r=R_FLAT + "flat(floor(level))", r_tolerance=0.0),
        Case("nums.round_up", "Lake Huron levels rounded up to whole feet", **huron,
             ours=_code('levels = sdata.numbers(data["level"].tolist()).round_up()', _ours_flat("levels")),
             parent=_code("import numpy as np\nx = np.ceil(data['level'].to_numpy())", NP_FLAT),
             parent_label="NumPy ceil", parent_tolerance=0.0, r=R_FLAT + "flat(ceiling(level))", r_tolerance=0.0),
        Case("nums.take_whole_part", "Lake Huron: the whole part of each level's distance from 579.5 ft (minus ones "
             "go towards 0)", **huron,
             ours=_code("""
                 levels = sdata.numbers(data["level"].tolist())
                 levels.subtract(579.5)
                 levels.take_whole_part()
             """, _ours_flat("levels")),
             parent=_code("import numpy as np\nx = np.trunc(data['level'].to_numpy() - 579.5)", NP_FLAT),
             parent_label="NumPy trunc", parent_tolerance=0.0, r=R_FLAT + "flat(trunc(level - 579.5))",
             r_tolerance=0.0),
        Case("nums.take_sin", "AirPassengers: the sine of each month's angle on the year (30 degrees a month)", **air,
             ours=_code(MONTH_ANGLES, """
                 angles = sdata.numbers(((months - 1) * 30).tolist()).take_sin(degrees=True)
             """, _ours_flat("angles")),
             parent=_code(MONTH_ANGLES, "import numpy as np\nx = np.sin(np.deg2rad((months.to_numpy() - 1) * 30))",
                          NP_FLAT), parent_label="NumPy sin, deg2rad", parent_tolerance=1e-15,
             r=R_MONTHS + "flat(sin((mo - 1) * 30 * pi / 180))", r_tolerance=1e-12),
        Case("nums.take_cos", "AirPassengers: the cosine of each month's angle on the year", **air,
             ours=_code(MONTH_ANGLES, """
                 angles = sdata.numbers(((months - 1) * 30).tolist()).take_cos(degrees=True)
             """, _ours_flat("angles")),
             parent=_code(MONTH_ANGLES, "import numpy as np\nx = np.cos(np.deg2rad((months.to_numpy() - 1) * 30))",
                          NP_FLAT), parent_label="NumPy cos, deg2rad", parent_tolerance=1e-15,
             r=R_MONTHS + "flat(cos((mo - 1) * 30 * pi / 180))", r_tolerance=1e-12),
        Case("nums.take_tan", "AirPassengers: the tangent of 7.5 degrees a month (0 to 82.5 degrees)", **air,
             ours=_code(MONTH_ANGLES, """
                 angles = sdata.numbers(((months - 1) * 7.5).tolist()).take_tan(degrees=True)
             """, _ours_flat("angles")),
             parent=_code(MONTH_ANGLES, "import numpy as np\nx = np.tan(np.deg2rad((months.to_numpy() - 1) * 7.5))",
                          NP_FLAT), parent_label="NumPy tan, deg2rad", parent_tolerance=1e-15,
             r=R_MONTHS + "flat(tan((mo - 1) * 7.5 * pi / 180))", r_tolerance=1e-12),
        Case("nums.change_angles_to", "AirPassengers: each month's angle on the year, in radians", **air,
             ours=_code(MONTH_ANGLES, """
                 angles = sdata.numbers(((months - 1) * 30).tolist()).change_angles_to("radians")
             """, _ours_flat("angles")),
             parent=_code(MONTH_ANGLES, "import numpy as np\nx = np.deg2rad((months.to_numpy() - 1) * 30)", NP_FLAT),
             parent_label="NumPy deg2rad", parent_tolerance=1e-15,
             r=R_MONTHS + "flat((mo - 1) * 30 * pi / 180)", r_tolerance=1e-12),
        Case("nums.find_where_biggest", "AirPassengers: the month (counting from 1) with the most passengers", **air,
             ours="""
                 {"position": sdata.numbers(data["passengers"].tolist()).find_where_biggest()}
             """,
             parent="""
                 import numpy as np
                 {"position": int(np.argmax(data["passengers"].to_numpy())) + 1}
             """, parent_label="NumPy argmax + 1", parent_tolerance=0.0,
             r="list(position = which.max(passengers))", r_tolerance=0.0),
        Case("nums.find_where_smallest", "Lake Huron: the year (counting from 1) with the lowest level", **huron,
             ours="""
                 {"position": sdata.numbers(data["level"].tolist()).find_where_smallest()}
             """,
             parent="""
                 import numpy as np
                 {"position": int(np.argmin(data["level"].to_numpy())) + 1}
             """, parent_label="NumPy argmin + 1", parent_tolerance=0.0,
             r="list(position = which.min(level))", r_tolerance=0.0),
        air_case("nums.find_where_biggest", "AirPassengers: the busiest month of each year (over the months)", """
                 busiest = block.find_where_biggest(over="month_of_year")
             """, "x = np.argmax(m, axis=1) + 1", "x <- apply(m, 1, which.max)",
                 numbers="busiest.get_all_numbers()"),
        Case("nums.make_pair_table_with", "Lake Huron: every year's level minus every other's (the first 10 years)",
             **huron,
             ours=_code("""
                 first = data["level"].to_numpy()[:10].tolist()
                 pairs = sdata.numbers(first).make_pair_table_with(first, by_subtracting=True)
             """, _ours_flat("pairs.get_all_numbers()")),
             parent=_code("""
                 import numpy as np
                 first = data["level"].to_numpy()[:10]
                 x = np.subtract.outer(first, first)
             """, NP_FLAT), parent_label="NumPy subtract.outer", parent_tolerance=0.0,
             r=R_FLAT + "l <- level[1:10]\nflat(outer(l, l, `-`))", r_tolerance=0.0),
        Case("nums.divide_by", "AirPassengers: whole dozens of passengers (dividing by 12, rounding down)", **air,
             option="rounding_down=",
             ours=_code('dozens = sdata.numbers(data["passengers"].tolist()).divide_by(12, rounding_down=True)',
                        _ours_flat("dozens")),
             parent=_code("import numpy as np\nx = np.floor_divide(data['passengers'].to_numpy(), 12)", NP_FLAT),
             parent_label="NumPy floor_divide", parent_tolerance=0.0, r=R_FLAT + "flat(passengers %/% 12)",
             r_tolerance=0.0),
        Case("nums.take_fourier_transform", "Lake Huron: the sizes of the Fourier transform with frequency 0 in the "
             "middle", **huron, option="with_zero_in_middle=",
             ours=_code("""
                 t = sdata.numbers(data["level"].tolist()).take_fourier_transform(time_step=1, with_zero_in_middle=True)
             """, _ours_flat('t.get_column("size")')),
             parent=_code("""
                 import numpy as np
                 from scipy import fft
                 x = np.abs(fft.fftshift(fft.fft(data["level"].to_numpy())))
             """, NP_FLAT), parent_label="SciPy fft.fft, fft.fftshift", parent_tolerance=1e-12,
             r=R_FLAT + "z <- Mod(fft(level)); n <- length(z); h <- n %/% 2\n"
                        "flat(c(z[(h + 1):n], z[1:h]))", r_tolerance=1e-9,
             note="R's fft has no shift; the R line puts the negative frequencies first, as fftshift does for an "
                  "even count (98 years)."),
        # ---------------------------------------------------------------- blocks: making and looking
        air_case("sdata.number_block", "AirPassengers as a block of 12 years x 12 months, from its long table",
                 "", "x = m", "x <- m"),
        block_case("block.find_shape", "iris as a block: its shape", "shape = block.find_shape()",
                   "x = np.array(a.shape)", "x <- dim(a)", numbers="shape"),
        block_case("block.count_directions", "iris as a block: how many directions",
                   "n = [block.count_directions()]", "x = np.array([a.ndim])", "x <- length(dim(a))", numbers="n"),
        block_case("block.get_number_at", "iris: the petal length of the 10th versicolor flower",
                   "n = [block.get_number_at(species=2, flower=10, measurement=3)]", "x = np.array([a[1, 9, 2]])",
                   "x <- a[2, 10, 3]", numbers="n"),
        block_case("block.find_average", "iris: the average of each measurement in each species (over the flowers)",
                   'means = block.find_average(over="flower")', "x = np.nanmean(a, axis=1)",
                   "x <- apply(a, c(1, 3), mean)", tolerance=1e-12, numbers="means.get_all_numbers()"),
        block_case("block.keep_by_position_in", "iris: the sepal and petal lengths only (measurements 1 and 3)",
                   'block.keep_by_position_in("measurement", [1, 3])', "x = np.take(a, [0, 2], axis=2)",
                   "x <- a[, , c(1, 3)]"),
        block_case("block.remove_by_position_in", "iris: without versicolor (species 2)",
                   'block.remove_by_position_in("species", 2)', "x = np.delete(a, [1], axis=0)", "x <- a[-2, , ]"),
        air_case("block.keep_where", "AirPassengers: the years 1950 to 1955, the range written backwards",
                 'block.keep_where("year", is_between=[1955, 1950])', "x = m[(years >= 1950) & (years <= 1955)]",
                 "x <- m[years >= 1950 & years <= 1955, ]"),
        air_case("block.remove_where", "AirPassengers: without the first and the last year",
                 'block.remove_where("year", is_one_of=[1949, 1960])', "x = m[~np.isin(years, [1949, 1960])]",
                 "x <- m[!(years %in% c(1949, 1960)), ]"),
        # ---------------------------------------------------------------- blocks: shape and directions
        block_case("block.change_shape_to", "iris: one row per species (3 rows of 200 numbers)",
                   'block.change_shape_to(one_row_per="species")', "x = a.reshape(3, -1)",
                   "x <- t(sapply(1:3, function(s) as.vector(t(a[s, , ]))))"),
        block_case("block.add_direction", "iris: a direction of size 1 in front (shape and numbers)",
                   'block.add_direction("plate", at_position=1)\nshape = list(block.find_shape())',
                   "x = np.concatenate([np.expand_dims(a, 0).shape, np.ravel(np.expand_dims(a, 0))])",
                   "x <- c(1, dim(a), as.vector(aperm(a)))",
                   numbers="shape + list(block.get_all_numbers())"),
        block_case("block.remove_directions_of_size_one", "iris: setosa alone, without its direction of size 1",
                   'block.keep_by_position_in("species", 1)\nblock.remove_directions_of_size_one()\n'
                   "shape = list(block.find_shape())",
                   "s = np.squeeze(a[:1])\nx = np.concatenate([s.shape, np.ravel(s)])",
                   "s <- a[1, , ]\nx <- c(dim(s), as.vector(t(s)))",
                   numbers="shape + list(block.get_all_numbers())"),
        block_case("block.swap_directions", "iris: flowers and measurements swapped",
                   'block.swap_directions("flower", "measurement")', "x = np.swapaxes(a, 1, 2)",
                   "x <- aperm(a, c(1, 3, 2))"),
        block_case("block.move_direction", "iris: the measurement direction moved to the front",
                   'block.move_direction("measurement", to_position=1)', "x = np.moveaxis(a, 2, 0)",
                   "x <- aperm(a, c(3, 1, 2))"),
        block_case("block.rotate", "iris: each species' 50 x 4 table turned a quarter turn",
                   "block.rotate(by_quarter_turns=1)", "x = np.rot90(a, k=1, axes=(1, 2))",
                   "x <- array(0, dim = c(3, 4, 50))\nfor (s in 1:3) x[s, , ] <- t(a[s, , ])[4:1, ]"),
        block_case("block.move_round_by", "iris: the flowers moved round by 3 (the last 3 come first)",
                   'block.move_round_by(3, over="flower")', "x = np.roll(a, 3, axis=1)", "x <- a[, c(48:50, 1:47), ]"),
        block_case("block.insert_numbers", "iris: a measurement of 0 put in at position 2",
                   'block.insert_numbers(0, at_position=2, over="measurement")', "x = np.insert(a, 1, 0, axis=2)",
                   "x <- array(0, dim = c(3, 50, 5))\nx[, , c(1, 3, 4, 5)] <- a"),
        block_case("block.repeat_each_number", "iris: each species twice in a row",
                   'block.repeat_each_number(2, over="species")', "x = np.repeat(a, 2, axis=0)",
                   "x <- a[rep(1:3, each = 2), , ]"),
        block_case("block.repeat_whole_block", "iris: the three species twice over",
                   'block.repeat_whole_block(2, over="species")', "x = np.tile(a, (2, 1, 1))",
                   "x <- a[rep(1:3, times = 2), , ]"),
        air_case("block.add_numbers_from", "AirPassengers: the last 6 years added after the first 6",
                 'first = sdata.number_block(block).keep_by_position_in("year", 1, to=6)\n'
                 'last = sdata.number_block(block).keep_by_position_in("year", 7, to=12)\n'
                 'first.add_numbers_from(last, over="year")',
                 "x = np.concatenate([m[:6], m[6:]], axis=0)", "x <- rbind(m[1:6, ], m[7:12, ])",
                 numbers="first.get_all_numbers()"),
        block_case("block.split_into_pieces", "iris: the flowers in 5 pieces; the total of each piece",
                   'pieces = [p.find_total() for p in block.split_into_pieces(5, over="flower")]',
                   "x = np.array([p.sum() for p in np.array_split(a, 5, axis=1)])",
                   "x <- sapply(split(1:50, rep(1:5, each = 10)), function(i) sum(a[, i, ]))", tolerance=1e-12,
                   numbers="pieces"),
        block_case("block.split_into_one_block_per", "iris: one block per species; the total of each",
                   'totals = [b.find_total() for b in block.split_into_one_block_per("species")]',
                   "x = np.array([b.sum() for b in np.unstack(a, axis=0)])", "x <- apply(a, 1, sum)",
                   tolerance=1e-12, numbers="totals"),
        Case("sdata.stack_up", "iris: the four measurements stacked as a new direction (4 x 150)", **iris,
             ours=_code("""
                 columns = [sdata.numbers(data[c].tolist()) for c in ["Sepal.Length", "Sepal.Width", "Petal.Length",
                                                                       "Petal.Width"]]
                 stacked = sdata.stack_up(columns, as_new_direction="measurement")
             """, _ours_flat("stacked.get_all_numbers()")),
             parent=_code(f"""
                 import numpy as np
                 x = np.stack([data[c].to_numpy() for c in {MEASURES}], axis=0)
             """, NP_FLAT), parent_label="NumPy stack", parent_tolerance=0.0,
             r=R_IRIS + "flat(t(m))", r_tolerance=0.0),
        # ---------------------------------------------------------------- stretching
        Case("block.show_how_it_lines_up_with", "iris: the block lined up with its species averages (the shape it "
             "gives)", **iris,
             ours=_code(IRIS_BLOCK, """
                 import contextlib
                 import io
                 import re
                 averages = block.find_average(over="flower")
                 shown = io.StringIO()
                 with contextlib.redirect_stdout(shown):
                     block.show_how_it_lines_up_with(averages)
                 result = next(line for line in shown.getvalue().splitlines() if line.startswith("result:"))
                 {str(i): float(n) for i, n in enumerate(re.findall(r"(\\d+) \\w", result))}
             """),
             parent=_code(IRIS_NUMPY, """
                 x = np.array(np.broadcast_shapes(a.shape, np.expand_dims(a.mean(axis=1), 1).shape))
             """, NP_FLAT), parent_label="NumPy broadcast_shapes", parent_tolerance=0.0,
             r=R_IRIS + "flat(dim(a))", r_tolerance=0.0,
             note="Named directions line up by name: the averages (species x measurement) are used again for each of "
                  "the 50 flowers, as NumPy does with keepdims=True."),
        air_case("block.stretch_to", "AirPassengers: the average of each month (over the years), used again for "
                 "every year", 'means = block.find_average(over="year")\nmeans.stretch_to((12, 12))',
                 "x = np.broadcast_to(m.mean(axis=0), (12, 12))", "x <- matrix(colMeans(m), 12, 12, byrow = TRUE)",
                 numbers="means.get_all_numbers()", tolerance=1e-12),
        Case("sdata.stretch_to_same_shape", "Lake Huron: the first 10 levels as a column and as a row, stretched to "
             "10 x 10", **huron,
             ours=_code("""
                 first = data["level"].to_numpy()[:10]
                 a2, b2 = sdata.stretch_to_same_shape([[v] for v in first.tolist()], first.tolist())
             """, _ours_flat("list(a2.get_all_numbers()) + list(b2.get_all_numbers())")),
             parent=_code("""
                 import numpy as np
                 first = data["level"].to_numpy()[:10]
                 a2, b2 = np.broadcast_arrays(first[:, None], first)
                 x = np.concatenate([np.ravel(a2), np.ravel(b2)])
             """, NP_FLAT), parent_label="NumPy broadcast_arrays", parent_tolerance=0.0,
             r=R_FLAT + "l <- level[1:10]\nflat(c(as.vector(t(matrix(l, 10, 10))), "
                        "as.vector(t(matrix(l, 10, 10, byrow = TRUE)))))", r_tolerance=0.0),
    ]
