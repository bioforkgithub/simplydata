"""Phase U3, batch 5: the chart words read back as data on real, published datasets.

As in the U-batch 2 chart cases of cases_underneath.py, the simplydata side reads the numbers its own chart drew
(bars, dots, lines, bands, cells, slices, segments) with the simplydata word chart.get_numbers_drawn() and table
words. What no simplydata word reads yet (titles, labels, texts, fonts, legends, colours, grid lines, ticks, axis
ranges and scales, inset places, colour bars, 3D surfaces) is read with the same chart_facts() the tests use, and the
code says so. The library side draws the same chart with seaborn or matplotlib and reads it with chart_facts(); R
gives the numbers the chart should show (averages, counts, standard deviations, fitted curves), where it is plain
base R.
"""

from __future__ import annotations

import textwrap

FACTS = "from simplydata._underneath.check import chart_facts\n"
LIBRARY = ("import matplotlib.pyplot as plt\nimport numpy as np\nimport seaborn as sns\n"
           "from simplydata._underneath.check import chart_facts\n")
OURS_AXES = "chart._render().axes[0]"


def _code(head: str, build: str, axes: str, read: str) -> str:
    return (head + textwrap.dedent(build).strip("\n") + f"\nf = chart_facts({axes})\n"
            + textwrap.dedent(read).strip("\n"))


def _ours_drawn(build: str, read: str, facts: str = "") -> str:
    """simplydata code that builds `chart`, reads what it drew into the table `drawn` with chart.get_numbers_drawn(),
    then the code `read`. `facts` names what no simplydata word reads yet: those are read with chart_facts() into f."""
    code = textwrap.dedent(build).strip("\n") + "\ndrawn = chart.get_numbers_drawn()\n"
    if facts:
        code = FACTS + code + f"# no simplydata word reads {facts} yet\nf = chart_facts({OURS_AXES})\n"
    return code + textwrap.dedent(read).strip("\n")


def _ours_facts(build: str, read: str, facts: str) -> str:
    """simplydata code that builds `chart` and reads it with chart_facts() only: for a case that checks only what no
    simplydata word reads yet (named in `facts`)."""
    return (FACTS + textwrap.dedent(build).strip("\n") + f"\n# no simplydata word reads {facts} yet\n"
            f"f = chart_facts({OURS_AXES})\n" + textwrap.dedent(read).strip("\n"))


def _pair(Case, word, title, dataset, ours, parent, read, label, r="", tolerance=1e-9, r_tolerance=1e-9, note="",
          ours_read="", facts=""):
    """A case whose simplydata side builds `chart` and whose library side draws on `ax` and is read by `read`.

    The simplydata side reads the numbers drawn with `ours_read` (on the table `drawn`, and on f for `facts`); with no
    `ours_read` it reads only what no simplydata word reads yet (`facts`), with chart_facts() and `read`."""
    if not (ours_read or facts):
        raise ValueError(f"the {word} case needs ours_read, or facts naming what no simplydata word reads yet")
    ours_code = _ours_drawn(ours, ours_read, facts) if ours_read else _ours_facts(ours, read, facts)
    return Case(word, title, dataset, "real data", ours=ours_code,
                parent=_code(LIBRARY, parent, "ax", read), parent_label=label, parent_tolerance=tolerance,
                r=r, r_tolerance=r_tolerance, note=note)


OKABE_ITO = '["#0072B2", "#E69F00", "#009E73"]'
GRID_MTCARS = """
    from scipy.interpolate import griddata
    gx, gy = np.meshgrid(np.linspace(data["wt"].min(), data["wt"].max(), 100),
                         np.linspace(data["hp"].min(), data["hp"].max(), 100))
    gz = griddata((data["wt"], data["hp"]), data["mpg"], (gx, gy), method="linear")
"""


CURVE_ENDS = """
    curve = drawn.keep_rows_where("kind", is_equal_to="line")
    {{"{first}": curve.get_cell_at(row=1, column="y"),
     "{last}": curve.get_cell_at(row=curve.count_rows(), column="y")}}
"""


def _on_grid(build: str) -> str:
    """Library code that first joins mtcars' scattered (wt, hp, mpg) onto the 100 x 100 grid simplydata uses."""
    return textwrap.dedent(GRID_MTCARS).strip("\n") + "\n" + textwrap.dedent(build).strip("\n")


def cases(Case):
    lines_wool = 'sns.lineplot(data, x="tension", y="breaks", hue="wool", errorbar=None, ax=ax)'
    legend_read = """
        {"legends on the figure": sum(p[0] == "figure" for p in f["legend_place"]),
         "place": f["legend_place"][0][1], "columns": f["legend_place"][0][3],
         "entries": len(f["legend_place"][0][4]) - 1}
    """
    return [
        _pair(Case, "show", "mtcars: average fuel use for 4, 6 and 8 cylinders, shown", "mtcars", """
            chart = sdata.chart(data).draw_bars(x="cyl", y="mpg")
            chart.show()
        """, """
            fig, ax = plt.subplots()
            sns.barplot(data, x="cyl", y="mpg", errorbar=None, ax=ax)
            plt.show()
        """, """
            {"4 cylinders": f["bars"][0][3], "8 cylinders": f["bars"][2][3]}
        """, "matplotlib plt.show", r="""
            list(`4 cylinders` = mean(mpg[cyl == 4]), `8 cylinders` = mean(mpg[cyl == 8]))
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            {"4 cylinders": drawn.get_cell_at(row=1, column="y"), "8 cylinders": drawn.get_cell_at(row=3, column="y")}
        """),
        _pair(Case, "draw_area", "Seatbelts: UK drivers killed in each month of the year, averaged over 1969-84",
              "Seatbelts", """
            chart = sdata.chart(data).draw_area(x="month_of_year", y="DriversKilled")
        """, """
            fig, ax = plt.subplots()
            mean = data.groupby("month_of_year")["DriversKilled"].mean()
            ax.fill_between(mean.index, mean, alpha=0.35, linewidth=0)
            ax.plot(mean.index, mean)
        """, """
            {"January": f["lines"][0][1][0], "December": f["lines"][0][1][-1], "months": len(f["lines"][0][1])}
        """, "matplotlib fill_between", r="""
            list(January = mean(DriversKilled[month_of_year == 1]), December = mean(DriversKilled[month_of_year == 12]),
                 months = length(unique(month_of_year)))
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            line = drawn.keep_rows_where("kind", is_equal_to="line")
            {"January": line.get_cell_at(row=1, column="y"),
             "December": line.get_cell_at(row=line.count_rows(), column="y"), "months": line.count_rows()}
        """),
        _pair(Case, "draw_pie", "mtcars: the share of cars with 4, 6 and 8 cylinders", "mtcars", """
            chart = sdata.chart(data).draw_pie(labels="cyl")
        """, """
            fig, ax = plt.subplots()
            counts = data["cyl"].value_counts(sort=False)
            ax.pie(counts, labels=counts.index, autopct="%1.0f%%", startangle=90, counterclock=False)
        """, """
            {"slices": len(f["shapes"]),
             "largest share (%)": max(float(t[:-1]) for t in f["texts"][1] if t.endswith("%"))}
        """, "matplotlib pie", r="""
            list(slices = length(unique(cyl)), `largest share (%)` = round(100 * max(table(cyl)) / length(cyl)))
        """, tolerance=0.0, r_tolerance=0.0, ours_read="""
            {"slices": drawn.count_rows(), "largest share (%)": round(100 * drawn.get_column("value").find_biggest())}
        """),
        _pair(Case, "draw_polar", "Seatbelts: drivers killed by month, round the year like a clock", "Seatbelts", """
            chart = sdata.chart(data).draw_polar(angle="month_of_year", distance="DriversKilled", full_turn=12)
        """, """
            fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
            ax.scatter(data["month_of_year"] / 12 * 2 * np.pi, data["DriversKilled"], zorder=3)
        """, """
            {"dots": len(f["dots"]), "angle of the first dot": f["dots"][0][0], "zero at": f["polar_start"][0],
             "direction": f["polar_start"][1]}
        """, "matplotlib polar axes", r="""
            list(dots = length(DriversKilled), `angle of the first dot` = 2 * pi * month_of_year[1] / 12,
                 `zero at` = pi / 2, direction = -1)
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            {"dots": drawn.count_rows(), "angle of the first dot": drawn.get_cell_at(row=1, column="x"),
             "zero at": f["polar_start"][0], "direction": f["polar_start"][1]}
        """, facts="where a round chart starts and which way it turns"),
        _pair(Case, "draw_contour", "mtcars: fuel use over weight and horsepower, a scattered map joined up", "mtcars",
              """
            chart = sdata.chart(data).draw_contour(x="wt", y="hp", z="mpg")
        """, _on_grid("""
            fig, ax = plt.subplots()
            bands = ax.contourf(gx, gy, gz, levels=10, cmap="viridis")
            ax.contour(bands, colors="white", linewidths=0.5, linestyles="solid")
            fig.colorbar(bands, ax=ax, label="mpg")
        """), """
            {"bands": len(f["shapes"]), "scale low": f["colour_bars"][0][1][0], "scale high": f["colour_bars"][0][1][1]}
        """, "SciPy griddata + matplotlib contourf", tolerance=1e-12,
              note="The bands and the lines between them both count among the shapes.",
              facts="the filled bands of a contour map or its colour bar"),
        _pair(Case, "draw_surface", "mtcars: fuel use over weight and horsepower as a 3D surface", "mtcars", """
            chart = sdata.chart(data).draw_surface(x="wt", y="hp", z="mpg")
        """, _on_grid("""
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            ax.plot_surface(gx, gy, np.ma.masked_invalid(gz), cmap="viridis", vmin=np.nanmin(gz), vmax=np.nanmax(gz),
                            linewidth=0)
        """), """
            {"pieces": f["in_3d"][3][0][0], "highest piece": float(np.nanmax(f["in_3d"][3][0][1])),
             "lowest piece": float(np.nanmin(f["in_3d"][3][0][1]))}
        """, "SciPy griddata + matplotlib plot_surface", tolerance=1e-12, facts="the pieces of a 3D surface"),
        _pair(Case, "draw_dots_3d", "Fisher's iris: sepal length, sepal width and petal length in 3D", "iris", """
            chart = sdata.chart(data).draw_dots_3d(x="Sepal.Length", y="Sepal.Width", z="Petal.Length",
                                                   colour="Species")
        """, """
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            for name, rows in data.groupby("Species", sort=False):
                ax.scatter(rows["Sepal.Length"], rows["Sepal.Width"], rows["Petal.Length"], label=name)
        """, """
            {"dots": sum(d[0] for d in f["in_3d"][2]), "groups": len(f["in_3d"][2]),
             "z of the first dot": f["in_3d"][2][0][1][0][2]}
        """, "matplotlib 3D scatter", r="""
            list(dots = length(Petal.Length), groups = length(unique(Species)), `z of the first dot` = Petal.Length[1])
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            # on a 3D chart the value column holds z
            {"dots": drawn.count_rows(), "groups": drawn.count_different_values_in("series"),
             "z of the first dot": drawn.get_cell_at(row=1, column="value")}
        """),
        _pair(Case, "draw_band", "Lake Huron: the level each year, with a band 1 foot either side", "Lake Huron", """
            table = sdata.table(data)
            table.add_column("low", "level - 1")
            table.add_column("high", "level + 1")
            chart = table.start_chart()
            chart.draw_band(x="year", between=["low", "high"])
        """, """
            fig, ax = plt.subplots()
            ax.fill_between(data["year"], data["level"] - 1, data["level"] + 1, alpha=0.25, linewidth=0)
        """, """
            {"lowest edge": float(f["shapes"][0][1][:, 1].min()), "highest edge": float(f["shapes"][0][1][:, 1].max())}
        """, "matplotlib fill_between", r="""
            list(`lowest edge` = min(level) - 1, `highest edge` = max(level) + 1)
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            {"lowest edge": drawn.get_column("low").find_smallest(),
             "highest edge": drawn.get_column("high").find_biggest()}
        """),
        _pair(Case, "draw_map_of_empty_cells", "NHANES (mice): where the 27 empty cells of 25 people are",
              "nhanes (mice)", """
            chart = sdata.chart(data).draw_map_of_empty_cells()
        """, """
            empty = data.isna()
            fig, ax = plt.subplots()
            ax.imshow(empty.to_numpy(dtype=float), aspect="auto", interpolation="nearest", vmin=0, vmax=1)
            ax.set_xticks(range(4), labels=[f"{c}\\n{n} empty" for c, n in empty.sum().items()])
        """, """
            {"empty cells": float(np.nansum(f["cells"][0][1])), "rows": f["cells"][0][0] / 4,
             "bmi empty": float(f["ticks"][0][1].split()[1])}
        """, "pandas isna + matplotlib imshow", r="""
            list(`empty cells` = sum(is.na(cbind(age, bmi, hyp, chl))), rows = length(age), `bmi empty` = sum(is.na(bmi)))
        """, tolerance=0.0, r_tolerance=0.0, ours_read="""
            cells = drawn.keep_rows_where("kind", is_equal_to="cell")
            {"empty cells": cells.get_column("value").find_total(), "rows": cells.count_rows() / 4,
             "bmi empty": float(f["ticks"][0][1].split()[1])}
        """, facts="the names under the x-axis"),
        _pair(Case, "sticks", "Lake Huron: the level of each year as a stick", "Lake Huron", """
            chart = sdata.chart(data).sticks(x="year", y="level")
        """, """
            fig, ax = plt.subplots()
            ax.vlines(data["year"], 0, data["level"], linewidth=1.5)
        """, """
            {"sticks": f["segments"][0][0][0] / 2, "last height": float(f["segments"][0][0][1][-1, 1]),
             "width": f["segments"][0][1][0]}
        """, "matplotlib vlines", r="""
            list(sticks = length(level), `last height` = level[length(level)])
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            sticks = drawn.keep_rows_where("kind", is_equal_to="segment")
            {"sticks": sticks.count_rows(), "last height": sticks.get_cell_at(row=sticks.count_rows(), column="high"),
             "width": f["segments"][0][1][0]}
        """, facts="the width of the sticks"),
        _pair(Case, "draw_error_bars", "Fisher's iris: sepal length of each species with its standard deviation",
              "iris", """
            chart = sdata.chart(data).draw_dots(x="Species", y="Sepal.Length")
            chart.draw_error_bars()
        """, """
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Species", y="Sepal.Length", ax=ax)
            s = data.groupby("Species", sort=False)["Sepal.Length"].agg(["mean", "std"])
            ax.errorbar(s.index, s["mean"], yerr=s["std"], fmt="_", capsize=4)
        """, """
            ends = f["segments"][0][0][1]
            {"setosa standard deviation": float((ends[1, 1] - ends[0, 1]) / 2),
             "virginica standard deviation": float((ends[5, 1] - ends[4, 1]) / 2)}
        """, "pandas std + matplotlib errorbar", r="""
            list(`setosa standard deviation` = sd(Sepal.Length[Species == "setosa"]),
                 `virginica standard deviation` = sd(Sepal.Length[Species == "virginica"]))
        """, tolerance=1e-12, r_tolerance=1e-12,
              facts="error bars over named groups (chart.get_numbers_drawn() stops on their group names)"),
        _pair(Case, "fit_curve", "mtcars: a curve with one bend through fuel use against weight", "mtcars", """
            chart = sdata.chart(data).draw_dots(x="wt", y="mpg")
            chart.fit_curve()
        """, """
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="wt", y="mpg", ax=ax)
            curve = np.polynomial.Polynomial.fit(data["wt"], data["mpg"], deg=2)
            xs = np.linspace(data["wt"].min(), data["wt"].max(), 200)
            ax.plot(xs, curve(xs))
        """, """
            {"at the lightest car": f["lines"][0][1][0], "at the heaviest car": f["lines"][0][1][-1]}
        """, "NumPy Polynomial.fit", r="""
            fit <- lm(mpg ~ poly(wt, 2, raw = TRUE))
            ends <- predict(fit, data.frame(wt = range(wt)))
            list(`at the lightest car` = ends[[1]], `at the heaviest car` = ends[[2]])
        """, tolerance=1e-9, r_tolerance=1e-9, ours_read=CURVE_ENDS.format(first="at the lightest car",
                                                                           last="at the heaviest car")),
        _pair(Case, "fit_distribution", "Michelson's 100 speeds of light: a normal curve fitted over the histogram",
              "NIST Michelso", """
            chart = sdata.chart(data).draw_histogram(x="y")
            chart.fit_distribution("normal")
        """, """
            from scipy import stats
            fig, ax = plt.subplots()
            sns.histplot(data, x="y", bins=10, ax=ax)
            average, spread = stats.norm.fit(data["y"])
            xs = np.linspace(*ax.dataLim.intervalx, 200)
            ax.plot(xs, stats.norm.pdf(xs, average, spread) * len(data) * ax.patches[0].get_width())
        """, """
            {"curve at the smallest value": f["lines"][0][1][0], "curve at the largest value": f["lines"][0][1][-1]}
        """, "SciPy norm.fit (maximum likelihood)", r="""
            s <- sqrt(mean((y - mean(y))^2))
            w <- (max(y) - min(y)) / 10
            list(`curve at the smallest value` = length(y) * w * dnorm(min(y), mean(y), s),
                 `curve at the largest value` = length(y) * w * dnorm(max(y), mean(y), s))
        """, tolerance=1e-9, r_tolerance=1e-9,
              note="Maximum likelihood: the standard deviation divides by n (as R MASS::fitdistr()).",
              ours_read=CURVE_ENDS.format(first="curve at the smallest value", last="curve at the largest value")),
        _pair(Case, "draw_curve", "Fisher's iris: a normal curve (average 5.8, standard deviation 0.8) over the sepal "
                                  "lengths", "iris", """
            chart = sdata.chart(data).draw_histogram(x="Sepal.Length")
            chart.draw_curve(sdata.distribution("normal", average=5.8, standard_deviation=0.8))
        """, """
            from scipy import stats
            fig, ax = plt.subplots()
            sns.histplot(data, x="Sepal.Length", bins=10, ax=ax)
            xs = np.linspace(*ax.dataLim.intervalx, 200)
            ax.plot(xs, stats.norm.pdf(xs, 5.8, 0.8) * len(data) * ax.patches[0].get_width())
        """, """
            {"curve at the smallest value": f["lines"][0][1][0], "curve at the largest value": f["lines"][0][1][-1]}
        """, "SciPy norm.pdf", r="""
            w <- (max(Sepal.Length) - min(Sepal.Length)) / 10
            n <- length(Sepal.Length)
            list(`curve at the smallest value` = n * w * dnorm(min(Sepal.Length), 5.8, 0.8),
                 `curve at the largest value` = n * w * dnorm(max(Sepal.Length), 5.8, 0.8))
        """, tolerance=1e-9, r_tolerance=1e-9,
              ours_read=CURVE_ENDS.format(first="curve at the smallest value", last="curve at the largest value")),
        _pair(Case, "draw_density", "Fisher's iris: a density curve of petal length for each species", "iris", """
            chart = sdata.chart(data).draw_density(x="Petal.Length", colour="Species")
        """, """
            fig, ax = plt.subplots()
            sns.kdeplot(data, x="Petal.Length", hue="Species", common_norm=False, ax=ax)
        """, """
            # seaborn's kdeplot draws the groups last to first: virginica, versicolor, then setosa
            {"curves": len(f["lines"]), "peak of setosa": float(max(f["lines"][2][1])),
             "peak of virginica": float(max(f["lines"][0][1]))}
        """, "seaborn kdeplot(common_norm=False)", tolerance=1e-12,
              note="Each curve has area 1 on its own; R's density() uses another bandwidth rule, so R is not asked.",
              ours_read="""
            curves = drawn.count_different_values_in("series")
            setosa = drawn.keep_rows_where("series", is_equal_to="setosa").get_column("y").find_biggest()
            drawn.undo()
            virginica = drawn.keep_rows_where("series", is_equal_to="virginica").get_column("y").find_biggest()
            {"curves": curves, "peak of setosa": setosa, "peak of virginica": virginica}
        """),
        _pair(Case, "draw_count_bars", "mtcars: how many cars have 3, 4 and 5 gears", "mtcars", """
            chart = sdata.chart(data).draw_count_bars(x="gear")
        """, """
            fig, ax = plt.subplots()
            sns.countplot(data, x="gear", ax=ax)
        """, """
            {"3 gears": f["bars"][0][3], "4 gears": f["bars"][1][3], "5 gears": f["bars"][2][3]}
        """, "seaborn countplot", r="""
            list(`3 gears` = sum(gear == 3), `4 gears` = sum(gear == 4), `5 gears` = sum(gear == 5))
        """, tolerance=0.0, r_tolerance=0.0, ours_read="""
            {"3 gears": drawn.get_cell_at(row=1, column="y"), "4 gears": drawn.get_cell_at(row=2, column="y"),
             "5 gears": drawn.get_cell_at(row=3, column="y")}
        """),
        _pair(Case, "draw_side_histograms", "Fisher's iris: sepal length against width, with a histogram on each side",
              "iris", """
            chart = sdata.chart(data).draw_dots(x="Sepal.Length", y="Sepal.Width")
            chart.draw_side_histograms()
        """, """
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Sepal.Length", y="Sepal.Width", ax=ax)
            top = ax.inset_axes([0, 1.02, 1, 0.18], sharex=ax)
            right = ax.inset_axes([1.02, 0, 0.18, 1], sharey=ax)
            for side, column, way in ((top, "Sepal.Length", "vertical"), (right, "Sepal.Width", "horizontal")):
                side.hist(data[column], bins=np.histogram_bin_edges(data[column], bins="auto"), orientation=way,
                          histtype="stepfilled")
        """, """
            {"small charts": len(f["insets"]), "corners of the top histogram": f["insets"][0][1][7][0][0],
             "height of the top histogram": float(f["insets"][0][1][7][0][1][:, 1].max())}
        """, "matplotlib inset_axes + hist", tolerance=1e-12, ours_read="""
            # panel 1 is the chart of dots, panel 2 the histogram on top, panel 3 the one on the right
            small_charts = drawn.get_column("panel").find_biggest() - 1
            top = drawn.keep_rows_where("panel", is_equal_to=2)
            {"small charts": small_charts, "corners of the top histogram": top.count_rows(),
             "height of the top histogram": top.get_column("y").find_biggest()}
        """),
        _pair(Case, "draw_cumulative_share", "warpbreaks: the share of looms with 30 breaks or fewer, for each wool",
              "warpbreaks", """
            chart = sdata.chart(data).draw_cumulative_share(x="breaks", colour="wool")
        """, """
            fig, ax = plt.subplots()
            sns.ecdfplot(data, x="breaks", hue="wool", ax=ax)
        """, """
            def at(line, value):
                return float(line[1][np.flatnonzero(line[0] <= value)[-1]])
            # seaborn's ecdfplot draws the groups last to first: wool B, then wool A
            {"wool A at 30 or fewer": at(f["lines"][1], 30), "wool B at 30 or fewer": at(f["lines"][0], 30)}
        """, "seaborn ecdfplot", r="""
            list(`wool A at 30 or fewer` = mean(breaks[wool == "A"] <= 30),
                 `wool B at 30 or fewer` = mean(breaks[wool == "B"] <= 30))
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            # each line climbs, so its highest point at 30 or fewer is its share at 30
            wool_a = drawn.keep_rows_where("series", is_equal_to="A").keep_rows_where("x", is_at_most=30)
            a = wool_a.get_column("y").find_biggest()
            drawn.undo()
            drawn.undo()
            b = drawn.keep_rows_where("series", is_equal_to="B").keep_rows_where("x", is_at_most=30).get_column("y")
            {"wool A at 30 or fewer": a, "wool B at 30 or fewer": b.find_biggest()}
        """),
        _pair(Case, "draw_line_with_slope", "mtcars: a line falling 5 miles per gallon for each 1000 lb, through "
                                            "(3, 20)", "mtcars", """
            chart = sdata.chart(data).draw_dots(x="wt", y="mpg")
            chart.draw_line_with_slope(-5, through=(3, 20))
        """, """
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="wt", y="mpg", ax=ax)
            ax.axline((3, 20), slope=-5, linestyle="--")
        """, """
            {"slope": f["ax_lines"][0][2], "through x": f["ax_lines"][0][0][0], "through y": f["ax_lines"][0][0][1],
             "dots": len(f["dots"])}
        """, "matplotlib axline", tolerance=0.0, ours_read="""
            {"slope": f["ax_lines"][0][2], "through x": f["ax_lines"][0][0][0], "through y": f["ax_lines"][0][0][1],
             "dots": drawn.keep_rows_where("kind", is_equal_to="dot").count_rows()}
        """, facts="a line given by a slope and a point (it has no drawn points)"),
        _pair(Case, "shade_between_x", "Lake Huron: the 1930s shaded behind the yearly levels", "Lake Huron", """
            chart = sdata.chart(data).draw_lines(x="year", y="level")
            chart.shade_between_x(1930, 1940)
        """, """
            fig, ax = plt.subplots()
            sns.lineplot(data, x="year", y="level", errorbar=None, ax=ax)
            ax.axvspan(1930, 1940, alpha=0.2)
        """, """
            {"band starts": f["bars"][0][0], "band width": f["bars"][0][2], "years drawn": len(f["lines"][0][0])}
        """, "matplotlib axvspan", r="""
            list(`years drawn` = length(year))
        """, tolerance=0.0, r_tolerance=0.0, ours_read="""
            {"band starts": f["bars"][0][0], "band width": f["bars"][0][2],
             "years drawn": drawn.keep_rows_where("kind", is_equal_to="line").count_rows()}
        """, facts="where a shaded band starts and how wide it is"),
        Case("write_names_on_dots", "mtcars: the names of the seven 6-cylinder cars next to their dots", "mtcars",
             "real data",
             ours=_ours_facts("""
                 table = sdata.table(data)
                 table.keep_rows_where("cyl", is_equal_to=6)
                 chart = table.start_chart().draw_dots(x="wt", y="mpg").write_names_on_dots("model")
             """, """
                 dots = {tuple(d) for d in f["dots"]}
                 {"names at their own dot": sum(p[1] in dots for p in f["text_places"]),
                  "names written": len(f["text_places"])}
             """, "the names written on a chart or where they are"),
             parent="""
                 rows = data[data["cyl"] == 6]
                 {"names at their own dot": len(rows), "names written": len(rows)}
             """, parent_label="pandas: the 6-cylinder cars", parent_tolerance=0.0,
             r="""
                 list(`names written` = sum(cyl == 6))
             """, r_tolerance=0.0,
             note="Where each name goes is simplydata's own search; the case checks every car is named at its dot."),
        _pair(Case, "use_font", "Fisher's iris: bars with every word in DejaVu Serif", "iris", """
            chart = sdata.chart(data).draw_bars(x="Species", y="Sepal.Length").use_font("DejaVu Serif")
        """, """
            with plt.rc_context({"font.family": "DejaVu Serif"}):
                fig, ax = plt.subplots()
                sns.barplot(data, x="Species", y="Sepal.Length", errorbar=None, ax=ax)
        """, """
            {"words in DejaVu Serif": float(sum(name == "DejaVu Serif" for name in f["fonts"])),
             "setosa": f["bars"][0][3]}
        """, "matplotlib rc_context(font.family)", r="""
            list(setosa = mean(Sepal.Length[Species == "setosa"]))
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            {"words in DejaVu Serif": float(sum(name == "DejaVu Serif" for name in f["fonts"])),
             "setosa": drawn.get_cell_at(row=1, column="y")}
        """, facts="the fonts"),
        _pair(Case, "set_range_x", "mtcars: fuel use against weight, the x-axis from 0", "mtcars", """
            chart = sdata.chart(data).draw_dots(x="wt", y="mpg").set_range_x(0, None)
        """, """
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="wt", y="mpg", ax=ax)
            ax.set_xlim(0, None)
        """, """
            {"x from": f["limits"][0][0], "x to": f["limits"][0][1]}
        """, "matplotlib set_xlim", r="""
            list(`x from` = 0, `x to` = max(wt) + 0.05 * diff(range(wt)))
        """, tolerance=1e-12, r_tolerance=1e-12,
              note="The top end stays where matplotlib put it: 5 % of the range past the heaviest car.",
              facts="the ends of an axis"),
        _pair(Case, "use_log_scale_x", "mtcars: fuel use against horsepower on a log scale", "mtcars", """
            chart = sdata.chart(data).draw_dots(x="hp", y="mpg").use_log_scale_x()
        """, """
            fig, ax = plt.subplots()
            ax.set_xscale("log")
            sns.scatterplot(data, x="hp", y="mpg", ax=ax)
        """, """
            {"log x": float(f["scales"][0] == "log"), "x from": f["limits"][0][0], "x to": f["limits"][0][1]}
        """, "matplotlib set_xscale", r="""
            lo <- log10(min(hp)); hi <- log10(max(hp)); pad <- 0.05 * (hi - lo)
            list(`log x` = 1, `x from` = 10^(lo - pad), `x to` = 10^(hi + pad))
        """, tolerance=1e-12, r_tolerance=1e-12,
              note="On a log scale matplotlib adds 5 % of the range of log10(x) at each end.",
              facts="the scale or the ends of an axis"),
        _pair(Case, "put_ticks_x", "Fisher's iris: ticks under setosa and virginica only", "iris", """
            chart = sdata.chart(data).draw_bars(x="Species", y="Petal.Length").put_ticks_x("setosa", "virginica")
        """, """
            fig, ax = plt.subplots()
            sns.barplot(data, x="Species", y="Petal.Length", errorbar=None, ax=ax)
            ax.set_xticks([0, 2], labels=["setosa", "virginica"])
        """, """
            {"first tick": f["tick_places"][0][0], "second tick": f["tick_places"][0][1], "ticks": len(f["ticks"][0]),
             "first name setosa": float(f["ticks"][0][0] == "setosa")}
        """, "matplotlib set_xticks", tolerance=0.0, facts="the places or names of the ticks"),
        _pair(Case, "put_ticks_y", "mtcars: fuel use bars with ticks at 0, 10, 20 and 30", "mtcars", """
            chart = sdata.chart(data).draw_bars(x="cyl", y="mpg").put_ticks_y(0, 10, 20, 30)
        """, """
            fig, ax = plt.subplots()
            sns.barplot(data, x="cyl", y="mpg", errorbar=None, ax=ax)
            ax.set_yticks([0, 10, 20, 30])
        """, """
            {"ticks": len(f["tick_places"][1]), "top tick": f["tick_places"][1][-1], "4 cylinders": f["bars"][0][3]}
        """, "matplotlib set_yticks", r="""
            list(`4 cylinders` = mean(mpg[cyl == 4]))
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            {"ticks": len(f["tick_places"][1]), "top tick": f["tick_places"][1][-1],
             "4 cylinders": drawn.get_cell_at(row=1, column="y")}
        """, facts="the places of the ticks"),
        _pair(Case, "rotate_labels_y", "mtcars: the 32 car names beside sideways bars, turned 30 degrees", "mtcars", """
            chart = sdata.chart(data).draw_bars(x="model", y="mpg", sideways=True).rotate_labels_y(30)
        """, """
            fig, ax = plt.subplots()
            sns.barplot(data, x="mpg", y="model", orient="h", errorbar=None, ax=ax)
            for label in ax.get_yticklabels():
                label.set_rotation(30)
                label.set_rotation_mode("anchor")
        """, """
            {"angle": f["tick_angles"][1][0][0], "names": len(f["ticks"][1]),
             "names turned about their end": sum(a[2] == "anchor" for a in f["tick_angles"][1])}
        """, "matplotlib set_rotation", r="""
            list(names = length(model))
        """, tolerance=0.0, r_tolerance=0.0, facts="the names beside an axis or how they are turned"),
        _pair(Case, "write_ticks_x_as", "birthwt: birth weights (grams) written with a comma for thousands", "birthwt",
              """
            chart = sdata.chart(data).draw_dots(x="bwt", y="lwt").write_ticks_x_as("thousands")
        """, """
            from matplotlib import ticker
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="bwt", y="lwt", ax=ax)
            ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
        """, """
            {"names with a comma": sum("," in t for t in f["ticks"][0]),
             "names with decimals": sum("." in t for t in f["ticks"][0]), "names": len(f["ticks"][0])}
        """, "matplotlib StrMethodFormatter", tolerance=0.0, facts="the names of the ticks"),
        *[_pair(Case, word, f"stackloss: stack loss against air flow, the {axis}-axis turned round", "stackloss", f"""
            chart = sdata.chart(data).draw_dots(x="air_flow", y="stack_loss").{word}()
        """, f"""
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="air_flow", y="stack_loss", ax=ax)
            ax.invert_{axis}axis()
        """, f"""
            {{"left or bottom end": f["limits"][{place}][0], "right or top end": f["limits"][{place}][1]}}
        """, f"matplotlib invert_{axis}axis", tolerance=1e-12, facts="the ends of an axis")
          for word, axis, place in (("flip_x", "x", 0), ("flip_y", "y", 1))],
        _pair(Case, "use_colour_scale", "warpbreaks: average breaks for each wool and tension in magma colours",
              "warpbreaks", """
            chart = sdata.chart(data).draw_heatmap(x="tension", y="wool", value="breaks").use_colour_scale("magma")
        """, """
            wide = data.pivot_table(index="wool", columns="tension", values="breaks", aggfunc="mean", sort=False)
            fig, ax = plt.subplots()
            sns.heatmap(wide, cmap="magma", cbar=False, ax=ax)
        """, """
            {"magma": float(f["cells"][0][2] == "magma"), "scale low": f["cells"][0][3], "scale high": f["cells"][0][4],
             "wool A, tension L": f["cells"][0][1][0]}
        """, "seaborn heatmap(cmap=)", r="""
            m <- tapply(breaks, list(wool, tension), mean)
            list(magma = 1, `scale low` = min(m), `scale high` = max(m), `wool A, tension L` = m["A", "L"])
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            {"magma": float(f["cells"][0][2] == "magma"), "scale low": f["cells"][0][3], "scale high": f["cells"][0][4],
             "wool A, tension L": drawn.get_cell_at(row=1, column="value")}
        """, facts="the colour scale"),
        *[_pair(Case, word, f"Fisher's iris: sepal length against width, {words}", "iris", f"""
            chart = sdata.chart(data).draw_dots(x="Sepal.Length", y="Sepal.Width").{word}()
        """, f"""
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Sepal.Length", y="Sepal.Width", ax=ax)
            ax.grid(True, axis="y")  # simplydata's paper look
            ax.grid({call})
        """, """
            {"lines along x": float(f["grid"][0]), "lines along y": float(f["grid"][1]), "dots": len(f["dots"])}
        """, f"matplotlib grid({call})", r="""
            list(dots = length(Sepal.Length))
        """, tolerance=0.0, r_tolerance=0.0, ours_read="""
            {"lines along x": float(f["grid"][0]), "lines along y": float(f["grid"][1]), "dots": drawn.count_rows()}
        """, facts="the grid lines")
          for word, words, call in (("show_grid", "grid lines both ways", 'True, axis="both"'),
                                    ("hide_grid", "no grid lines", "False"))],
        _pair(Case, "put_legend_at_top", "warpbreaks: lines of the two wools, the legend above", "warpbreaks", """
            chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool").put_legend_at_top()
        """, f"""
            fig, ax = plt.subplots(layout="constrained")
            {lines_wool}
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            fig.legend(handles, labels, title="wool", loc="outside upper center", ncols=2)
        """, legend_read, "matplotlib fig.legend", tolerance=0.0, facts="the legend"),
        _pair(Case, "put_legend_on_right", "warpbreaks: lines of the two wools, the legend on the right", "warpbreaks",
              """
            chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool").put_legend_on_right()
        """, f"""
            fig, ax = plt.subplots(layout="constrained")
            {lines_wool}
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            fig.legend(handles, labels, title="wool", loc="outside center right")
        """, legend_read, "matplotlib fig.legend", tolerance=0.0, facts="the legend"),
        _pair(Case, "show_legend", "warpbreaks: lines of the two wools, the legend hidden and shown again",
              "warpbreaks", """
            chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool")
            chart.hide_legend().show_legend()
        """, f"""
            fig, ax = plt.subplots()
            {lines_wool}
        """, """
            {"legends": len(f["legend_place"]), "entries": len(f["legend"]) - 1}
        """, "seaborn lineplot legend", r="""
            list(entries = length(unique(wool)))
        """, tolerance=0.0, r_tolerance=0.0, facts="the legend"),
        _pair(Case, "label_legend", "Fisher's iris: the legend of the species named \"Iris species\"", "iris", """
            chart = sdata.chart(data).draw_dots(x="Sepal.Length", y="Petal.Length", colour="Species")
            chart.label_legend("Iris species")
        """, """
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Sepal.Length", y="Petal.Length", hue="Species", ax=ax)
            ax.get_legend().set_title("Iris species")
        """, """
            {"named as asked": float(f["legend"][0] == "Iris species"), "entries": len(f["legend"]) - 1}
        """, "matplotlib Legend.set_title", r="""
            list(entries = length(unique(Species)))
        """, tolerance=0.0, r_tolerance=0.0, facts="the legend"),
        _pair(Case, "label_colour_bar", "mtcars: the colour bar of a fuel-use map named \"Miles per gallon\"", "mtcars",
              """
            chart = sdata.chart(data).draw_contour(x="wt", y="hp", z="mpg").label_colour_bar("Miles per gallon")
        """, _on_grid("""
            fig, ax = plt.subplots()
            bar = fig.colorbar(ax.contourf(gx, gy, gz, levels=10), ax=ax)
            bar.set_label("Miles per gallon")
        """), """
            {"named as asked": float(f["colour_bars"][0][0] == "Miles per gallon"), "scale low": f["colour_bars"][0][1][0]}
        """, "matplotlib Colorbar.set_label", tolerance=1e-12, facts="the colour bar"),
        _pair(Case, "order_y", "Fisher's iris: sideways bars, virginica at the top", "iris", """
            chart = sdata.chart(data).draw_bars(x="Species", y="Sepal.Width", sideways=True)
            chart.order_y("virginica", "versicolor", "setosa")
        """, """
            fig, ax = plt.subplots()
            sns.barplot(data, x="Sepal.Width", y="Species", order=["virginica", "versicolor", "setosa"], orient="h",
                        errorbar=None, ax=ax)
        """, """
            {"top name virginica": float(f["ticks"][1][0] == "virginica"),
             "bar at the top": [b[2] for b in f["bars"] if abs(b[1] + 0.4) < 1e-9][0]}
        """, "seaborn barplot(order=)", r="""
            list(`top name virginica` = 1, `bar at the top` = mean(Sepal.Width[Species == "virginica"]))
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            # sideways bars: y is the group, x the length
            {"top name virginica": float(f["ticks"][1][0] == "virginica"),
             "bar at the top": drawn.keep_rows_where("y", is_equal_to="virginica").get_cell_at(row=1, column="x")}
        """, facts="the names beside an axis"),
        _pair(Case, "order_legend", "warpbreaks: bars of the two wools, wool B first", "warpbreaks", """
            chart = sdata.chart(data).draw_bars(x="tension", y="breaks", colour="wool").order_legend("B", "A")
        """, """
            fig, ax = plt.subplots()
            sns.barplot(data, x="tension", y="breaks", hue="wool", hue_order=["B", "A"], errorbar=None, ax=ax)
        """, """
            {"first entry B": float(f["legend"][1] == "B"), "first bar (wool B, tension L)": f["bars"][0][3]}
        """, "seaborn barplot(hue_order=)", r="""
            list(`first entry B` = 1, `first bar (wool B, tension L)` = mean(breaks[wool == "B" & tension == "L"]))
        """, tolerance=1e-12, r_tolerance=1e-12, ours_read="""
            # the bars of each wool run L, M, H, so the first bar of wool B is tension L
            first_of_b = drawn.keep_rows_where("series", is_equal_to="B").get_cell_at(row=1, column="y")
            {"first entry B": float(f["legend"][1] == "B"), "first bar (wool B, tension L)": first_of_b}
        """, facts="the legend"),
        _pair(Case, "add_zoom_box", "mtcars: fuel use against weight, with the cars of 2.5 to 3.5 (1000 lb) close up",
              "mtcars", """
            chart = sdata.chart(data).draw_dots(x="wt", y="mpg")
            chart.add_zoom_box(x_between=[2.5, 3.5], y_between=[15, 25])
        """, """
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="wt", y="mpg", ax=ax)
            box = ax.inset_axes([0.58, 0.56, 0.39, 0.4])
            sns.scatterplot(data, x="wt", y="mpg", ax=box)
            box.set(xlim=(2.5, 3.5), ylim=(15, 25))
        """, """
            inside = [d for d in f["insets"][0][1][4][1] if 2.5 <= d[0] <= 3.5 and 15 <= d[1] <= 25]
            {"box from x": f["insets"][0][1][8][0], "box to x": f["insets"][0][1][8][1], "dots in view": len(inside),
             "box width (share of the chart)": f["insets"][0][0][2]}
        """, "matplotlib inset_axes", r="""
            list(`dots in view` = sum(wt >= 2.5 & wt <= 3.5 & mpg >= 15 & mpg <= 25))
        """, tolerance=1e-12, r_tolerance=0.0, ours_read="""
            # panel 2 is the zoom box
            box = drawn.keep_rows_where("panel", is_equal_to=2)
            inside = box.keep_rows_where("x", is_between=[2.5, 3.5]).keep_rows_where("y", is_between=[15, 25])
            {"box from x": f["insets"][0][1][8][0], "box to x": f["insets"][0][1][8][1],
             "dots in view": inside.count_rows(), "box width (share of the chart)": f["insets"][0][0][2]}
        """, facts="the place or the ends of the axes of a zoom box"),
        Case("forest_plot", "warpbreaks: Tukey's differences between the three tensions, as a forest plot",
             "warpbreaks", "real data",
             ours=_ours_drawn("""
                 pairs = sdata.table(data).compare_each_pair_of("breaks", for_each_group_in="tension",
                                                                test_method="tukey")
                 chart = pairs.start_chart().forest_plot(x="difference", y="group 1")
             """, """
                 dots = drawn.keep_rows_where("kind", is_equal_to="dot")
                 sizes = dots.get_column("x").take_absolute_value()
                 rows = dots.count_rows()
                 drawn.undo()
                 no_effect = drawn.keep_rows_where("kind", is_equal_to="line").get_cell_at(row=1, column="x")
                 {"smallest difference": sizes.find_smallest(), "largest difference": sizes.find_biggest(),
                  "line of no effect at": no_effect, "rows": rows}
             """),
             parent="""
                 from statsmodels.stats.multicomp import pairwise_tukeyhsd
                 sizes = sorted(abs(pairwise_tukeyhsd(data["breaks"], data["tension"]).meandiffs))
                 {"smallest difference": sizes[0], "largest difference": sizes[-1], "line of no effect at": 0.0,
                  "rows": 3}
             """, parent_label="statsmodels pairwise_tukeyhsd", parent_tolerance=1e-9,
             r="""
                 d <- sort(abs(TukeyHSD(aov(breaks ~ tension))$tension[, "diff"]))
                 list(`smallest difference` = d[[1]], `largest difference` = d[[3]], rows = 3)
             """, r_tolerance=1e-9,
             note="The dots of the forest plot are the differences between the averages of each pair of tensions."),
    ]
