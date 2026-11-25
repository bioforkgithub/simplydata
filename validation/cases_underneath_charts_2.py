"""Charts phase, batches 1 to 3: the new chart words and options read back as data on real, published datasets.

As in cases_underneath_charts.py, the simplydata side reads what its own chart drew with the simplydata read-back
words (chart.get_numbers_drawn(), chart.get_text_drawn(), chart.get_scales_drawn(), chart.get_size()) and table
words. What no simplydata word reads yet (legend places, colour bars, small ticks, the frame, the shape of the plot
area, 3D views, wire frames, fonts, the marks of a dot) is read with the same chart_facts() and matplotlib getters the
tests use, and the code says so. The library side draws the same chart with matplotlib, seaborn or pandas and reads it
the same way; R gives the numbers the chart should show (averages, counts, ranges, residuals), where it is plain
base R. The web-page words draw nothing of their own (the page is a copy of the picture), so their cases read the
plotly figure's own data and layout and compare them with what matplotlib drew.

The datasets are those of the study (R's datasets and MASS and survival packages, read from R; NIST's Norris data):
mtcars, Fisher's iris, warpbreaks, Seatbelts, Lake Huron, birthwt, airquality and the Stanford heart transplant data.
"""

from __future__ import annotations

import textwrap

FACTS = "from simplydata._underneath.check import chart_facts\n"
LIBRARY = ("import matplotlib.pyplot as plt\nimport numpy as np\nimport seaborn as sns\n"
           "from simplydata._underneath.check import chart_facts\n")
WEB = "from simplydata import _web\n"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def _ours(build: str, read: str, facts: str = "") -> str:
    """simplydata code: build `chart`, then `read` (ending in the dict of numbers). With `facts` (what no simplydata
    word reads yet), the drawn figure is in fig, its first chart in ax and its chart_facts() in f."""
    if not facts:
        return _code(build, read)
    return _code(FACTS, build, f"""
        # no simplydata word reads {facts} yet
        fig = chart._render()
        ax = fig.axes[0]
        f = chart_facts(ax)
    """, read)


def _library(*parts: str) -> str:
    """Library code: the drawing parts (on `ax`, in `fig`), then chart_facts() into f and the last part, `read`."""
    return _code(LIBRARY, *parts[:-1], "f = chart_facts(ax)", parts[-1])


def _case(Case, word, title, dataset, ours, parent, label, tolerance=1e-12, r="", r_tolerance=1e-12, note="",
          option=""):
    return Case(word, title, dataset, "real data", ours=ours, parent=parent, parent_label=label,
                parent_tolerance=tolerance, r=r, r_tolerance=r_tolerance, note=note, option=option)


# ---------------------------------------------------------------- shared pieces
MTCARS_DOTS = 'chart = sdata.chart(data).draw_dots(x="wt", y="mpg")'
MTCARS_SEABORN = """
    fig, ax = plt.subplots()
    sns.scatterplot(data, x="wt", y="mpg", ax=ax)
"""
IRIS_DOTS = 'chart = sdata.chart(data).draw_dots(x="Sepal.Length", y="Sepal.Width")'
IRIS_SEABORN = """
    fig, ax = plt.subplots()
    sns.scatterplot(data, x="Sepal.Length", y="Sepal.Width", ax=ax)
"""
IRIS_3D = 'chart = sdata.chart(data).draw_dots_3d(x="Sepal.Length", y="Sepal.Width", z="Petal.Length")'
IRIS_3D_MATPLOTLIB = """
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(data["Sepal.Length"], data["Sepal.Width"], data["Petal.Length"], depthshade=False)
    ax.set_xlabel("Sepal.Length"); ax.set_ylabel("Sepal.Width"); ax.set_zlabel("Petal.Length")
"""
WOOL_LINES = 'chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool")'
WOOL_SEABORN = """
    fig, ax = plt.subplots(layout="constrained")
    sns.lineplot(data, x="tension", y="breaks", hue="wool", errorbar=None, ax=ax)
"""
# warpbreaks: the average breaks of each wool (rows) and tension (columns) as a heat map
WOOL_HEATMAP = 'chart = sdata.chart(data).draw_heatmap(x="tension", y="wool", value="breaks")'
WOOL_HEATMAP_SEABORN = """
    fig, ax = plt.subplots(layout="constrained")
    wide = data.pivot_table(index="wool", columns="tension", values="breaks", aggfunc="mean", sort=False)
    sns.heatmap(wide, cmap="viridis", cbar=False, ax=ax)
"""
WOOL_AVERAGES_R = """
    m <- tapply(breaks, list(wool, tension), mean)
"""
GRID_MTCARS = """
    from scipy.interpolate import griddata
    gx, gy = np.meshgrid(np.linspace(data["wt"].min(), data["wt"].max(), 100),
                         np.linspace(data["hp"].min(), data["hp"].max(), 100))
    gz = griddata((data["wt"], data["hp"]), data["mpg"], (gx, gy), method="linear")
"""
COLOUR_BAR = """
    bar = [a for a in fig.axes if a.get_label() == "<colorbar>"]
    {"colour bars": len(bar), "scale low": f["colour_bars"][0][1][0], "scale high": f["colour_bars"][0][1][1],
     "named breaks": float(f["colour_bars"][0][0] == "breaks"), "cells": f["cells"][0][0],
     "total of the cells": float(np.nansum(f["cells"][0][1])), "{side}": float({test})}
"""
SIDES = {"bottom": ("below the chart", "bar[0].get_position().y1 <= ax.get_position().y0"),
         "top": ("above the chart", "bar[0].get_position().y0 >= ax.get_position().y1"),
         "left": ("left of the chart", "bar[0].get_position().x1 <= ax.get_position().x0")}


def _colour_bar_case(Case, side):
    name, test = SIDES[side]
    read = COLOUR_BAR.replace("{side}", name).replace("{test}", test)
    return _case(Case, f"put_colour_bar_at_{side}", f"warpbreaks: average breaks of each wool and tension, the colour "
                 f"bar {name}", "warpbreaks", _ours(f"""
        {WOOL_HEATMAP}
        chart.put_colour_bar_at_{side}()
    """, read, "the colour bar or where it is"), _library(WOOL_HEATMAP_SEABORN, f"""
        fig.colorbar(ax.collections[0], ax=ax, location="{side}", label="breaks")
    """, read), f'seaborn heatmap + matplotlib colorbar(location="{side}")', r=WOOL_AVERAGES_R + """
        list(`scale low` = min(m), `scale high` = max(m), cells = length(m), `total of the cells` = sum(m))
    """)


def _cases_batch1(Case):
    """get_text_drawn, get_scales_drawn, get_size, write_letter, put_legend_inside, use_shapes."""
    return [
        _case(Case, "get_text_drawn", "Fisher's iris: the words of a chart of the three species", "iris", _ours(
            'chart = sdata.chart(data).draw_dots(x="Sepal.Length", y="Petal.Length", colour="Species")', """
            text = chart.get_text_drawn()
            entries = text.keep_rows_where("part", is_equal_to="legend entry")
            count, first = entries.count_rows(), entries.get_cell_at(row=1, column="text")
            text.undo()
            title = text.keep_rows_where("part", is_equal_to="legend title").get_cell_at(row=1, column="text")
            text.undo()
            x_label = text.keep_rows_where("part", is_equal_to="x label").get_cell_at(row=1, column="text")
            {"legend entries": count, "first entry setosa": float(first == "setosa"),
             "legend named Species": float(title == "Species"), "x label Sepal.Length": float(x_label == "Sepal.Length")}
        """), _library("""
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Sepal.Length", y="Petal.Length", hue="Species", ax=ax)
        """, """
            {"legend entries": len(f["legend"]) - 1, "first entry setosa": float(f["legend"][1] == "setosa"),
             "legend named Species": float(f["legend"][0] == "Species"),
             "x label Sepal.Length": float(f["labels"][0] == "Sepal.Length")}
        """), "seaborn scatterplot(hue=) legend and Axes.get_xlabel", tolerance=0.0, r="""
            list(`legend entries` = length(unique(Species)))
        """, r_tolerance=0.0),
        _case(Case, "get_scales_drawn", "mtcars: the ranges of the axes of fuel use against weight", "mtcars", _ours(
            MTCARS_DOTS, """
            scales = chart.get_scales_drawn()
            {"x from": scales.get_cell_at(row=1, column="low"), "x to": scales.get_cell_at(row=1, column="high"),
             "y from": scales.get_cell_at(row=2, column="low"), "y to": scales.get_cell_at(row=2, column="high"),
             "x in numbers": float(scales.get_cell_at(row=1, column="kind") == "numbers")}
        """), _library(MTCARS_SEABORN, """
            {"x from": f["limits"][0][0], "x to": f["limits"][0][1], "y from": f["limits"][1][0],
             "y to": f["limits"][1][1], "x in numbers": float(f["scales"][0] == "linear")}
        """), "matplotlib Axes.get_xlim / get_ylim", r="""
            pad <- function(v) c(min(v) - 0.05 * diff(range(v)), max(v) + 0.05 * diff(range(v)))
            list(`x from` = pad(wt)[1], `x to` = pad(wt)[2], `y from` = pad(mpg)[1], `y to` = pad(mpg)[2])
        """, note="matplotlib adds 5 % of the range of the data at each end of an axis."),
        _case(Case, "get_size", "mtcars: a chart 17 x 12 cm, its size read from the saved picture", "mtcars", _ours(
            MTCARS_DOTS, """
            chart.set_size(width=17, height=12, unit="cm")
            width, height = chart.get_size(unit="cm")
            {"width (cm)": width, "height (cm)": height}
        """), _code(LIBRARY, MTCARS_SEABORN.replace("plt.subplots()", "plt.subplots(figsize=(17 / 2.54, 12 / 2.54))"),
                    """
            import io
            from PIL import Image
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=300)
            width, height = Image.open(buffer).size
            {"width (cm)": round(width / 300 * 2.54, 4), "height (cm)": round(height / 300 * 2.54, 4)}
        """), "matplotlib savefig(dpi=300) + Pillow Image.size", tolerance=0.0,
              note="The size of the picture written at 300 dots per inch: 17 cm is 2008 dots (2007.87 rounded)."),
        _case(Case, "write_letter", "Fisher's iris: sepal length against width, as panel B", "iris", _ours(f"""
            {IRIS_DOTS}
            chart.write_letter("B")
        """, """
            text = chart.get_text_drawn()
            letter = text.keep_rows_where("part", is_equal_to="panel letter").get_cell_at(row=1, column="text")
            {"letter B": float(letter == "B"), "dots": chart.get_numbers_drawn().count_rows(),
             "bold": float(ax._left_title.get_fontweight() in ("bold", 700))}
        """, "the weight of the letter"), _library(IRIS_SEABORN, """
            ax.set_title("B", loc="left", fontweight="bold")
        """, """
            {"letter B": float(ax.get_title(loc="left") == "B"), "dots": len(f["dots"]),
             "bold": float(ax._left_title.get_fontweight() in ("bold", 700))}
        """), 'matplotlib set_title(loc="left", fontweight="bold")', tolerance=0.0, r="""
            list(dots = length(Sepal.Length))
        """, r_tolerance=0.0,
              note="matplotlib keeps the left title only in the private _left_title (read for its weight)."),
        _case(Case, "put_legend_inside", "warpbreaks: lines of the two wools, the legend inside at the top left",
              "warpbreaks", _ours(f"""
            {WOOL_LINES}
            chart.put_legend_inside("top left")
        """, """
            text = chart.get_text_drawn()
            where = text.keep_rows_where("part", is_equal_to="legend title").get_cell_at(row=1, column="where")
            {"said inside top left": float(where == "inside top left"), "place code": f["legend_place"][0][1],
             "legends on the chart": sum(p[0] == "chart" for p in f["legend_place"]),
             "entries": len(f["legend_place"][0][4]) - 1}
        """, "matplotlib's place code of a legend"), _library(WOOL_SEABORN, """
            sns.move_legend(ax, "upper left")
        """, """
            {"said inside top left": float(f["legend_place"][0][1] == 2), "place code": f["legend_place"][0][1],
             "legends on the chart": sum(p[0] == "chart" for p in f["legend_place"]),
             "entries": len(f["legend_place"][0][4]) - 1}
        """), 'seaborn move_legend("upper left")', tolerance=0.0, r="""
            list(entries = length(unique(wool)))
        """, r_tolerance=0.0, note='matplotlib\'s code 2 is "upper left".'),
        _case(Case, "use_shapes", "Fisher's iris: a circle, a square and a triangle for the three species", "iris",
              _ours("""
            chart = sdata.chart(data).draw_dots(x="Sepal.Length", y="Sepal.Width", colour="Species")
            chart.use_shapes("circle", "square", "triangle")
        """, """
            drawn = chart.get_numbers_drawn()
            outlines = {tuple(np.round(p.vertices, 6).ravel()) for c in ax.collections for p in c.get_paths()}
            {"dots": drawn.count_rows(), "colours": drawn.count_different_values_in("colour"),
             "shapes": len(outlines), "corners of the square": min(len(p.vertices) for c in ax.collections
                                                                   for p in c.get_paths())}
        """, "the shape (marker) of a dot"), _library("""
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Sepal.Length", y="Sepal.Width", hue="Species", style="Species",
                            markers=["o", "s", "^"], ax=ax)
        """, """
            outlines = {tuple(np.round(p.vertices, 6).ravel()) for c in ax.collections for p in c.get_paths()}
            {"dots": len(f["dots"]), "colours": len(set(f["dot_colour_groups"])), "shapes": len(outlines),
             "corners of the square": min(len(p.vertices) for c in ax.collections for p in c.get_paths())}
        """), "seaborn scatterplot(style=, markers=)", tolerance=0.0, r="""
            list(dots = length(Species), colours = length(unique(Species)), shapes = length(unique(Species)))
        """, r_tolerance=0.0),
    ]


def _cases_new_marks(Case):
    """New chart types and marks: rug lines, wind rose, arrow, chart inside, hexagons, side densities, time bars,
    rectangle, circle, residual dots, event lines, 3D bars and 3D lines."""
    return [
        _case(Case, "draw_rug_lines", "Fisher's iris: a density of petal length with a rug line for each flower",
              "iris", _ours("""
            chart = sdata.chart(data).draw_density(x="Petal.Length").draw_rug_lines(x="Petal.Length")
        """, """
            rug = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="segment")
            {"rug lines": rug.count_rows(), "first line at": rug.get_column("x").find_smallest(),
             "last line at": rug.get_column("x").find_biggest()}
        """), _library("""
            fig, ax = plt.subplots()
            sns.kdeplot(data, x="Petal.Length", ax=ax)
            sns.rugplot(data, x="Petal.Length", ax=ax)
        """, """
            ends = f["segments"][0][0][1]
            {"rug lines": f["segments"][0][0][0] / 2, "first line at": float(ends[:, 0].min()),
             "last line at": float(ends[:, 0].max())}
        """), "seaborn rugplot", r="""
            list(`rug lines` = length(Petal.Length), `first line at` = min(Petal.Length),
                 `last line at` = max(Petal.Length))
        """),
        _case(Case, "draw_wind_rose", "Seatbelts: drivers killed each month, in bands, round the year as a compass "
              "(month 12 at north)", "Seatbelts", _ours("""
            table = sdata.table(data)
            table.add_column("direction", "month_of_year * 30")
            chart = table.start_chart().draw_wind_rose(direction="direction", speed="DriversKilled")
        """, """
            drawn = chart.get_numbers_drawn()
            {"months counted": drawn.get_column("y").find_total(), "bands": drawn.count_different_values_in("series"),
             "longest stack": drawn.get_column("high").find_biggest(), "bars": drawn.count_rows(),
             "zero at": f["polar_start"][0], "direction": f["polar_start"][1]}
        """, "where a round chart starts and which way it turns"), _code(LIBRARY, """
            from matplotlib.ticker import MaxNLocator
            fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
            ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
            turned = np.mod(data["month_of_year"] * 30 + 15, 360)
            speeds = MaxNLocator(nbins=5).tick_values(data["DriversKilled"].min(), data["DriversKilled"].max())
            counts, _, _ = np.histogram2d(turned, data["DriversKilled"], bins=[np.arange(0, 361, 30), speeds])
            counts = counts[:, counts.sum(axis=0) > 0]  # a band with no months is left out
            bottom = np.zeros(12)
            for band in counts.T:
                ax.bar(np.deg2rad(np.arange(0, 360, 30)), band, width=np.deg2rad(30), bottom=bottom)
                bottom = bottom + band
            f = chart_facts(ax)
            {"months counted": sum(b[3] for b in f["bars"]), "bands": counts.shape[1],
             "longest stack": max(b[1] + b[3] for b in f["bars"]), "bars": len(f["bars"]),
             "zero at": f["polar_start"][0], "direction": f["polar_start"][1]}
        """), "NumPy histogram2d + matplotlib polar bars", r="""
            list(`months counted` = length(DriversKilled), `longest stack` = max(table(month_of_year)),
                 `zero at` = pi / 2, direction = -1)
        """, note="Each month of the year is one direction (30 degrees apart), so each bar stacks the 16 years of "
                  "that month; the speed bands are matplotlib's MaxNLocator steps of the number killed."),
        _case(Case, "draw_arrow", "mtcars: an arrow from (2, 30) to (3, 25) over fuel use against weight", "mtcars",
              _ours(f"""
            {MTCARS_DOTS}
            chart.draw_arrow(start=[2, 30], end=[3, 25])
        """, """
            arrow = ax.texts[0]
            {"points at x": arrow.xy[0], "points at y": arrow.xy[1], "starts at x": arrow.get_position()[0],
             "starts at y": arrow.get_position()[1], "dots": chart.get_numbers_drawn().count_rows()}
        """, "an arrow (it has no drawn points)"), _library(MTCARS_SEABORN, """
            ax.annotate("", xy=(3, 25), xytext=(2, 30), ha="center", va="center",
                        arrowprops=dict(arrowstyle="->", linewidth=1.5, shrinkA=0, shrinkB=0))
        """, """
            arrow = ax.texts[0]
            {"points at x": arrow.xy[0], "points at y": arrow.xy[1], "starts at x": arrow.get_position()[0],
             "starts at y": arrow.get_position()[1], "dots": len(f["dots"])}
        """), "matplotlib annotate(arrowprops=)", tolerance=0.0, r="""
            list(dots = length(mpg))
        """, r_tolerance=0.0),
        _case(Case, "put_chart_inside", "warpbreaks: lines of the two wools, with the average of each wool as a small "
              "bar chart inside", "warpbreaks", _ours(f"""
            {WOOL_LINES}
            detail = sdata.chart(data).draw_bars(x="wool", y="breaks")
            chart.put_chart_inside(detail, where="bottom right", size=0.35)
        """, """
            bars = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="bar")
            {"wool A": bars.get_cell_at(row=1, column="y"), "wool B": bars.get_cell_at(row=2, column="y"),
             "left": f["insets"][0][0][0], "bottom": f["insets"][0][0][1], "width": f["insets"][0][0][2]}
        """, "the place of a small chart inside a chart"), _library(WOOL_SEABORN, """
            inset = ax.inset_axes([1 - 0.03 - 0.35, 0.03, 0.35, 0.35])
            sns.barplot(data, x="wool", y="breaks", errorbar=None, ax=inset)
        """, """
            heights = f["insets"][0][1][5][1][:, 3]
            {"wool A": float(heights[0]), "wool B": float(heights[1]), "left": f["insets"][0][0][0],
             "bottom": f["insets"][0][0][1], "width": f["insets"][0][0][2]}
        """), "matplotlib inset_axes + seaborn barplot", r="""
            list(`wool A` = mean(breaks[wool == "A"]), `wool B` = mean(breaks[wool == "B"]))
        """),
        _case(Case, "draw_hexagon_bins", "birthwt: birth weight against the mother's weight, counted in hexagons",
              "birthwt", _ours("""
            chart = sdata.chart(data).draw_hexagon_bins(x="lwt", y="bwt")
        """, """
            drawn = chart.get_numbers_drawn()
            {"babies": drawn.get_column("value").find_total(), "hexagons": drawn.count_rows(),
             "most in one hexagon": drawn.get_column("value").find_biggest()}
        """), _library("""
            fig, ax = plt.subplots()
            hexagons = ax.hexbin(data["lwt"], data["bwt"], gridsize=20, mincnt=1, cmap="viridis", linewidths=0.2,
                                 edgecolors="face")
        """, """
            counts = f["hexagons"][0][1][1]
            {"babies": float(counts.sum()), "hexagons": f["hexagons"][0][0][0], "most in one hexagon": float(counts.max())}
        """), "matplotlib hexbin(gridsize=20, mincnt=1)", tolerance=0.0, r="""
            list(babies = length(bwt))
        """, r_tolerance=0.0),
        _case(Case, "draw_side_histograms", "Fisher's iris: sepal length against width, a density curve on each edge",
              "iris", _ours(f"""
            {IRIS_DOTS}
            chart.draw_side_histograms(drawn_as="density")
        """, """
            drawn = chart.get_numbers_drawn()
            top = drawn.keep_rows_where("panel", is_equal_to=2)
            peak_top = top.get_column("high").find_biggest()
            drawn.undo()
            right = drawn.keep_rows_where("panel", is_equal_to=3)
            {"small charts": 2, "peak of the top curve": peak_top,
             "peak of the right curve": right.get_column("high").find_biggest()}
        """), _library(IRIS_SEABORN, """
            top = ax.inset_axes([0, 1.02, 1, 0.18], sharex=ax)
            right = ax.inset_axes([1.02, 0, 0.18, 1], sharey=ax)
            sns.kdeplot(x=data["Sepal.Length"], ax=top, fill=True, alpha=0.8, linewidth=0)
            sns.kdeplot(y=data["Sepal.Width"], ax=right, fill=True, alpha=0.8, linewidth=0)
        """, """
            {"small charts": len(f["insets"]), "peak of the top curve": float(f["insets"][0][1][7][0][1][:, 1].max()),
             "peak of the right curve": float(f["insets"][1][1][7][0][1][:, 0].max())}
        """), "matplotlib inset_axes + seaborn kdeplot(fill=True)", option="drawn_as=",
              note="Gaussian kernel with Scott's bandwidth (seaborn's); R's density() uses another rule, so R is not "
                   "asked."),
        _case(Case, "draw_time_bars", "Stanford heart transplant: the time each of the first 10 patients spent "
              "waiting and after a transplant", "Stanford heart transplant (survival)", _ours("""
            first = sdata.table(data).keep_first_rows(10)
            chart = first.start_chart().draw_time_bars(start="start", end="stop", y="id")
        """, """
            bars = chart.get_numbers_drawn()
            {"bars": bars.count_rows(), "days drawn": bars.get_column("x").find_total(),
             "last end": bars.get_column("high").find_biggest(), "rows of the chart": len(f["ticks"][1]),
             "first patient at the top": float(f["limits"][1][0] > f["limits"][1][1])}
        """, "the names beside the y-axis and its direction"), _library("""
            first = data.head(10)
            people = list(dict.fromkeys(first["id"]))
            fig, ax = plt.subplots()
            ax.barh([people.index(i) for i in first["id"]], first["stop"] - first["start"], left=first["start"],
                    height=0.8, linewidth=0)
            ax.set_yticks(range(len(people)), labels=[str(i) for i in people])
            ax.invert_yaxis()
        """, """
            {"bars": len(f["bars"]), "days drawn": sum(b[2] for b in f["bars"]),
             "last end": max(b[0] + b[2] for b in f["bars"]), "rows of the chart": len(f["ticks"][1]),
             "first patient at the top": float(f["limits"][1][0] > f["limits"][1][1])}
        """), "matplotlib barh(left=) + invert_yaxis", r="""
            list(bars = 10, `days drawn` = sum(stop[1:10] - start[1:10]), `last end` = max(stop[1:10]),
                 `rows of the chart` = length(unique(id[1:10])))
        """, note="A patient with a transplant has two rows (waiting, then after it): two bars on the same line."),
        _case(Case, "draw_rectangle", "mtcars: the cars of 3000 to 4000 lb and 15 to 20 miles per gallon marked by "
              "a rectangle", "mtcars", _ours(f"""
            {MTCARS_DOTS}
            chart.draw_rectangle(x_between=[3, 4], y_between=[15, 20])
        """, """
            drawn = chart.get_numbers_drawn()
            box = drawn.keep_rows_where("kind", is_equal_to="rectangle")
            low, high = box.get_cell_at(row=1, column="low"), box.get_cell_at(row=1, column="high")
            drawn.undo()
            inside = (drawn.keep_rows_where("kind", is_equal_to="dot").keep_rows_where("x", is_between=[3, 4])
                      .keep_rows_where("y", is_between=[15, 20]))
            {"bottom": low, "top": high, "left": f["bars"][0][0], "width": f["bars"][0][2], "cars inside": inside.count_rows()}
        """, "the left edge and width of a rectangle"), _library(MTCARS_SEABORN, """
            from matplotlib.patches import Rectangle
            ax.add_patch(Rectangle((3, 15), 1, 5, facecolor=(0, 0.447, 0.698, 0.25), edgecolor="#0072B2",
                                   linewidth=1.5))
        """, """
            (x, y, w, h), = f["bars"]
            inside = [d for d in f["dots"] if 3 <= d[0] <= 4 and 15 <= d[1] <= 20]
            {"bottom": y, "top": y + h, "left": x, "width": w, "cars inside": len(inside)}
        """), "matplotlib Rectangle", tolerance=0.0, r="""
            list(`cars inside` = sum(wt >= 3 & wt <= 4 & mpg >= 15 & mpg <= 20))
        """, r_tolerance=0.0),
        _case(Case, "draw_circle", "mtcars: a circle of radius 1 round (3, 20) over fuel use against weight", "mtcars",
              _ours(f"""
            {MTCARS_DOTS}
            chart.draw_circle(centre=[3, 20], radius=1)
        """, """
            ring = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="shape")
            {"leftmost": ring.get_column("x").find_smallest(), "rightmost": ring.get_column("x").find_biggest(),
             "lowest": ring.get_column("y").find_smallest(), "highest": ring.get_column("y").find_biggest()}
        """), _library(MTCARS_SEABORN, """
            from matplotlib.patches import Circle
            ax.add_patch(Circle((3, 20), 1, facecolor=(0, 0.447, 0.698, 0.25), edgecolor="#0072B2", linewidth=1.5))
        """, """
            circle = ax.patches[0]
            corners = circle.get_patch_transform().transform(circle.get_path().vertices)
            {"leftmost": float(corners[:, 0].min()), "rightmost": float(corners[:, 0].max()),
             "lowest": float(corners[:, 1].min()), "highest": float(corners[:, 1].max())}
        """), "matplotlib Circle", tolerance=1e-12, r="""
            list(leftmost = 3 - 1, rightmost = 3 + 1, lowest = 20 - 1, highest = 20 + 1)
        """, r_tolerance=1e-12),
        _case(Case, "draw_residual_dots", "mtcars: what a straight line of fuel use on weight leaves over, car by car",
              "mtcars", _ours("""
            chart = sdata.chart(data).draw_residual_dots(x="wt", y="mpg")
        """, """
            dots = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="dot")
            {"Mazda RX4": dots.get_cell_at(row=1, column="y"), "largest": dots.get_column("y").find_biggest(),
             "smallest": dots.get_column("y").find_smallest(), "cars": dots.count_rows(),
             "y-axis named": float(f["labels"][1] == "residual of mpg")}
        """, "the name of the y-axis"), _library("""
            fig, ax = plt.subplots()
            sns.residplot(data, x="wt", y="mpg", ax=ax)
            ax.set_ylabel("residual of mpg")
        """, """
            ys = [d[1] for d in f["dots"]]
            {"Mazda RX4": ys[0], "largest": max(ys), "smallest": min(ys), "cars": len(ys),
             "y-axis named": float(f["labels"][1] == "residual of mpg")}
        """), "seaborn residplot", tolerance=1e-9, r="""
            e <- residuals(lm(mpg ~ wt))
            list(`Mazda RX4` = e[[1]], largest = max(e), smallest = min(e), cars = length(e))
        """, r_tolerance=1e-9),
        _case(Case, "draw_event_lines", "warpbreaks: a line for the breaks of each loom, one row for each wool",
              "warpbreaks", _ours("""
            chart = sdata.chart(data).draw_event_lines(x="breaks", y="wool")
        """, """
            lines = chart.get_numbers_drawn()
            count, most = lines.count_rows(), lines.get_column("x").find_biggest()
            length = lines.get_cell_at(row=1, column="high") - lines.get_cell_at(row=1, column="low")
            first_row = lines.keep_rows_where("y", is_equal_to=lines.get_column("y").find_smallest())
            {"lines": count, "lines in the first row": first_row.count_rows(), "line length": length,
             "most breaks": most}
        """), _library("""
            fig, ax = plt.subplots()
            groups = list(data["wool"].unique())
            ax.eventplot([data.loc[data["wool"] == g, "breaks"] for g in groups], lineoffsets=range(len(groups)),
                         linelengths=0.8, linewidths=1.5)
            ax.set_yticks(range(len(groups)), labels=groups)
        """, """
            rows = [np.asarray(c.get_segments(), dtype=float) for c in ax.collections]
            {"lines": sum(len(r) for r in rows), "lines in the first row": len(rows[0]),
             "line length": float(abs(rows[0][0][1, 1] - rows[0][0][0, 1])),
             "most breaks": float(max(r[:, :, 0].max() for r in rows))}
        """), "matplotlib eventplot", r="""
            list(lines = length(breaks), `lines in the first row` = sum(wool == wool[1]), `most breaks` = max(breaks))
        """),
        _case(Case, "draw_bars_3d", "warpbreaks: the average breaks of each tension and wool as 3D bars", "warpbreaks",
              _ours("""
            averages = sdata.table(data).find_average_of("breaks", for_each_group_in=["tension", "wool"])
            chart = averages.start_chart().draw_bars_3d(x="tension", y="wool", z="average of breaks")
        """, """
            bars = chart.get_numbers_drawn()
            {"bars": bars.count_rows(), "tallest": bars.get_column("high").find_biggest(),
             "shortest": bars.get_column("high").find_smallest(), "corners": f["faces_3d"][0][0]}
        """, "the corners of 3D bars"), _library("""
            averages = data.groupby(["tension", "wool"], sort=False)["breaks"].mean().reset_index()
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            tensions, wools = list(averages["tension"].unique()), list(averages["wool"].unique())
            x = averages["tension"].map(tensions.index).to_numpy(float)
            y = averages["wool"].map(wools.index).to_numpy(float)
            ax.bar3d(x - 0.4, y - 0.4, 0, 0.8, 0.8, averages["breaks"], shade=True)
        """, """
            corners = f["faces_3d"][0][1]
            {"bars": len(averages), "tallest": float(corners[:, 2].max()),
             "shortest": float(averages["breaks"].min()), "corners": f["faces_3d"][0][0]}
        """), "pandas groupby mean + matplotlib bar3d", r=WOOL_AVERAGES_R + """
            list(bars = length(m), tallest = max(m), shortest = min(m))
        """),
        _case(Case, "draw_lines_3d", "Seatbelts: drivers killed against drivers hurt, month by month, as a line in 3D",
              "Seatbelts", _ours("""
            chart = sdata.chart(data).draw_lines_3d(x="month", y="drivers", z="DriversKilled")
        """, """
            # on a 3D chart the value column holds z
            line = chart.get_numbers_drawn()
            {"months": line.count_rows(), "z of the first month": line.get_cell_at(row=1, column="value"),
             "z of the last month": line.get_cell_at(row=line.count_rows(), column="value"),
             "z named DriversKilled": float(f["in_3d"][0] == "DriversKilled")}
        """, "the name of the z-axis"), _library("""
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            ax.plot(data["month"], data["drivers"], data["DriversKilled"])
            ax.set_xlabel("month"); ax.set_ylabel("drivers"); ax.set_zlabel("DriversKilled")
        """, """
            xs, ys, zs = ax.get_lines()[0].get_data_3d()
            {"months": len(zs), "z of the first month": float(zs[0]), "z of the last month": float(zs[-1]),
             "z named DriversKilled": float(f["in_3d"][0] == "DriversKilled")}
        """), "matplotlib 3D plot", r="""
            list(months = length(DriversKilled), `z of the first month` = DriversKilled[1],
                 `z of the last month` = DriversKilled[length(DriversKilled)])
        """),
    ]


def _cases_axes_and_look(Case):
    """Second scales, frame, ticks, shape of the plot area, scales and background."""
    def dots_case(word, title, step, draw, read, label, facts, dataset="iris", build=IRIS_DOTS,
                  library=IRIS_SEABORN, r="", note="", option="", tolerance=1e-12):
        return _case(Case, word, title, dataset, _ours(f"""
            {build}
            chart.{step}
        """, read, facts), _library(library, draw, read), label, tolerance=tolerance, r=r, note=note,
            option=option)

    small_ticks = """
        low, high = ax.get_{a}lim()
        small = [v for v in ax.{a}axis.get_minorticklocs() if low <= v <= high]
        {{"small ticks": len(small), "first small tick": small[0], "big ticks": len(f["tick_places"][{i}]),
          "dots": len(f["dots"])}}
    """
    hidden_ticks = """
        ticks = ax.{a}axis.get_major_ticks()
        {{"tick words shown": sum(t.label1.get_visible() or t.label2.get_visible() for t in ticks),
          "tick length": max(t.tick1line.get_markersize() for t in ticks), "dots": len(f["dots"])}}
    """
    return [
        _case(Case, "add_second_x", "airquality (New York, 1973): wind against temperature, with the temperature in "
              "degrees C along the top", "airquality (R datasets)", _ours("""
            chart = sdata.chart(data).draw_dots(x="Temp", y="Wind")
            chart.add_second_x(formula="(x - 32) * 5 / 9", labelled="Temperature (C)")
        """, """
            scales = chart.get_scales_drawn().keep_rows_where("scale", is_equal_to="second x")
            {"top from": scales.get_cell_at(row=1, column="low"), "top to": scales.get_cell_at(row=1, column="high"),
             "top named": float(scales.get_cell_at(row=1, column="name") == "Temperature (C)")}
        """), _library("""
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Temp", y="Wind", ax=ax)
            top = ax.secondary_xaxis("top", functions=(lambda f: (f - 32) * 5 / 9, lambda c: c * 9 / 5 + 32))
            top.set_xlabel("Temperature (C)")
        """, """
            {"top from": (f["limits"][0][0] - 32) * 5 / 9, "top to": (f["limits"][0][1] - 32) * 5 / 9,
             "top named": float(top.get_xlabel() == "Temperature (C)")}
        """), "matplotlib secondary_xaxis(functions=)", tolerance=1e-12, r="""
            pad <- 0.05 * diff(range(Temp))
            list(`top from` = (min(Temp) - pad - 32) * 5 / 9, `top to` = (max(Temp) + pad - 32) * 5 / 9)
        """, r_tolerance=1e-12),
        _case(Case, "add_second_y", "airquality (New York, 1973): temperature against wind, with degrees C on the "
              "right", "airquality (R datasets)", _ours("""
            chart = sdata.chart(data).draw_dots(x="Wind", y="Temp")
            chart.add_second_y(formula="(y - 32) * 5 / 9", labelled="Temperature (C)")
        """, """
            scales = chart.get_scales_drawn().keep_rows_where("scale", is_equal_to="second y")
            {"right from": scales.get_cell_at(row=1, column="low"),
             "right to": scales.get_cell_at(row=1, column="high"),
             "right named": float(scales.get_cell_at(row=1, column="name") == "Temperature (C)")}
        """), _library("""
            fig, ax = plt.subplots()
            sns.scatterplot(data, x="Wind", y="Temp", ax=ax)
            right = ax.secondary_yaxis("right", functions=(lambda f: (f - 32) * 5 / 9, lambda c: c * 9 / 5 + 32))
            right.set_ylabel("Temperature (C)")
        """, """
            {"right from": (f["limits"][1][0] - 32) * 5 / 9, "right to": (f["limits"][1][1] - 32) * 5 / 9,
             "right named": float(right.get_ylabel() == "Temperature (C)")}
        """), "matplotlib secondary_yaxis(functions=)", option="formula=", r="""
            pad <- 0.05 * diff(range(Temp))
            list(`right from` = (min(Temp) - pad - 32) * 5 / 9, `right to` = (max(Temp) + pad - 32) * 5 / 9)
        """),
        dots_case("hide_frame", "Fisher's iris: sepal length against width, with no frame or axes", "hide_frame()",
                  "ax.set_axis_off()", """
            {"frame shown": float(ax.axison), "dots": len(f["dots"]), "x from": f["limits"][0][0],
             "x to": f["limits"][0][1]}
        """, "matplotlib set_axis_off", "whether the frame is drawn", tolerance=0.0),
        *[dots_case(f"hide_ticks_{a}", f"Fisher's iris: sepal length against width, no ticks on the {a}-axis",
                    f"hide_ticks_{a}()",
                    f'ax.tick_params(axis="{a}", which="both", length=0, label{side}=False, label{other}=False)',
                    hidden_ticks.format(a=a), "matplotlib tick_params(length=0, labels off)",
                    "the ticks themselves", tolerance=0.0)
          for a, side, other in (("x", "bottom", "top"), ("y", "left", "right"))],
        *[dots_case(f"show_small_ticks_{a}", f"Fisher's iris: sepal length against width, small ticks on the {a}-axis",
                    f"show_small_ticks_{a}()", f"ax.{a}axis.minorticks_on()", small_ticks.format(a=a, i=i),
                    "matplotlib minorticks_on (AutoMinorLocator)", "the small ticks", tolerance=1e-12)
          for i, a in enumerate("xy")],
        dots_case("use_true_shape", "Fisher's iris: sepal length against width, 1 cm as long on both axes",
                  "use_true_shape()", 'ax.set_aspect("equal")', """
            ax.apply_aspect()
            box = ax.get_window_extent()
            (x0, x1), (y0, y1) = f["limits"]
            {"cm per pixel across / up": ((x1 - x0) / box.width) / ((y1 - y0) / box.height), "dots": len(f["dots"])}
        """, 'matplotlib set_aspect("equal")', "the shape of the plot area", tolerance=1e-9,
                  note="With equal units, 1 cm of sepal takes as many pixels across as up: the ratio is 1."),
        dots_case("make_square", "Fisher's iris: sepal length against width in a square plot area", "make_square()",
                  "ax.set_box_aspect(1)", """
            ax.apply_aspect()
            box = ax.get_window_extent()
            {"height / width": box.height / box.width, "dots": len(f["dots"])}
        """, "matplotlib set_box_aspect(1)", "the shape of the plot area", tolerance=1e-9),
        dots_case("use_background_colour", "Fisher's iris: sepal length against width on ivory",
                  'use_background_colour("ivory")', 'ax.set_facecolor("ivory")', """
            {"ivory": float(f["background"] == "#fffff0ff"), "dots": len(f["dots"])}
        """, "matplotlib set_facecolor", "the background colour", tolerance=0.0),
        dots_case("use_scale_x", "mtcars: fuel use against weight on an asinh scale", 'use_scale_x("asinh")',
                  'ax.set_xscale("asinh")', """
            {"asinh": float(f["scales"][0] == "asinh"), "x from": f["limits"][0][0], "x to": f["limits"][0][1],
             "dots": len(f["dots"])}
        """, 'matplotlib set_xscale("asinh")', "the scale or the ends of an axis", dataset="mtcars",
                  build=MTCARS_DOTS, library=MTCARS_SEABORN),
        dots_case("use_scale_y", "mtcars: horsepower on a square-root scale against weight", 'use_scale_y("square root")',
                  """
            low, high = ax.get_ylim()
            ax.set_yscale("function", functions=(lambda v: np.sqrt(np.clip(v, 0, None)), np.square))
            ax.set_ylim(max(low, 0), high)
        """, """
            {"y from": f["limits"][1][0], "y to": f["limits"][1][1], "dots": len(f["dots"]),
             "middle of the axis": float(ax.transData.inverted().transform(ax.transAxes.transform((0.5, 0.5)))[1])}
        """, 'matplotlib set_yscale("function") with a square root', "the scale or the ends of an axis",
                  dataset="mtcars", build='chart = sdata.chart(data).draw_dots(x="wt", y="hp")',
                  library='fig, ax = plt.subplots()\nsns.scatterplot(data, x="wt", y="hp", ax=ax)\n', tolerance=1e-9,
                  note="On a square-root axis the middle is ((sqrt(low) + sqrt(high)) / 2) squared."),
        _case(Case, "use_log_scale_y", "birthwt: doctor visits in the first trimester (most are 0) against the "
              "mother's weight, on a log scale through zero", "birthwt", _ours("""
            chart = sdata.chart(data).draw_dots(x="lwt", y="ftv").use_log_scale_y(through_zero=True)
        """, """
            scales = chart.get_scales_drawn()
            {"through zero": float(scales.get_cell_at(row=2, column="kind") == "log through zero"),
             "y from": scales.get_cell_at(row=2, column="low"), "y to": scales.get_cell_at(row=2, column="high"),
             "dots at 0": chart.get_numbers_drawn().keep_rows_where("y", is_equal_to=0).count_rows()}
        """), _library("""
            fig, ax = plt.subplots()
            ax.set_yscale("symlog")
            sns.scatterplot(data, x="lwt", y="ftv", ax=ax)
        """, """
            {"through zero": float(f["scales"][1] == "symlog"), "y from": f["limits"][1][0], "y to": f["limits"][1][1],
             "dots at 0": sum(d[1] == 0 for d in f["dots"])}
        """), 'matplotlib set_yscale("symlog")', option="through_zero=", r="""
            list(`dots at 0` = sum(ftv == 0))
        """, r_tolerance=0.0),
        _case(Case, "break_between_y", "mtcars: average horsepower of 4, 6 and 8 cylinders, the y-axis broken "
              "between 130 and 200", "mtcars", _ours("""
            chart = sdata.chart(data).draw_bars(x="cyl", y="hp").break_between_y(130, 200)
        """, """
            bars = chart.get_numbers_drawn()
            top = bars.keep_rows_where("panel", is_equal_to=1)
            eight = top.get_cell_at(row=1, column="y")
            bars.undo()
            bottom = bars.keep_rows_where("panel", is_equal_to=2)
            panels = f["every_panel"]
            {"8 cylinders (top part)": eight, "4 cylinders (bottom part)": bottom.get_cell_at(row=1, column="y"),
             "top part from": panels[0][9][0], "bottom part to": panels[1][9][1], "parts": len(panels)}
        """, "the ranges of the two parts"), _library("""
            fig, (top, bottom) = plt.subplots(2, 1, sharex=True)
            for part in (top, bottom):
                sns.barplot(data, x="cyl", y="hp", errorbar=None, ax=part)
            bottom.set_ylim(bottom.get_ylim()[0], 130); top.set_ylim(200, top.get_ylim()[1])
            ax = top
        """, """
            panels = f["every_panel"]
            {"8 cylinders (top part)": float(panels[0][5][1][2, 3]), "4 cylinders (bottom part)": float(panels[1][5][1][0, 3]),
             "top part from": panels[0][9][0], "bottom part to": panels[1][9][1], "parts": len(panels)}
        """), "the matplotlib gallery's broken axis (two panels sharing x)", r="""
            list(`8 cylinders (top part)` = mean(hp[cyl == 8]), `4 cylinders (bottom part)` = mean(hp[cyl == 4]),
                 `top part from` = 200, `bottom part to` = 130, parts = 2)
        """, note="Each part keeps only its own bars in get_numbers_drawn(): the 8-cylinder bar on top, the others "
                  "below."),
        _case(Case, "draw_line_at_y", "mtcars: a line at 20 miles per gallon over the cars of 2000 to 4000 lb",
              "mtcars", _ours(f"""
            {MTCARS_DOTS}
            chart.draw_line_at_y(20, between=[2, 4])
        """, """
            ends = f["segments"][0][0][1]
            line = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="segment")
            {"at y": line.get_cell_at(row=1, column="y"), "from x": float(ends[:, 0].min()),
             "to x": float(ends[:, 0].max()), "dots": len(f["dots"])}
        """, "the ends of a line drawn between two places"), _library(MTCARS_SEABORN, """
            ax.hlines(20, 2, 4, colors="grey", linestyles="--", linewidths=1.5, zorder=2.5)
        """, """
            ends = f["segments"][0][0][1]
            {"at y": float(ends[0, 1]), "from x": float(ends[:, 0].min()), "to x": float(ends[:, 0].max()),
             "dots": len(f["dots"])}
        """), "matplotlib hlines", tolerance=0.0, option="between=", r="""
            list(dots = length(mpg))
        """, r_tolerance=0.0),
        _case(Case, "use_font_size", "Fisher's iris: bars of sepal length with text size 12, the title 20 and the "
              "ticks 8", "iris", _ours("""
            chart = sdata.chart(data).draw_bars(x="Species", y="Sepal.Length").write_title_on_top("Iris")
            chart.use_font_size(12, title=20, ticks=8)
        """, """
            sizes = f["font_sizes"]
            {"title": sizes[0], "x label": sizes[1], "x ticks": sizes[3], "y ticks": sizes[4],
             "setosa": chart.get_numbers_drawn().get_cell_at(row=1, column="y")}
        """, "the font sizes"), _code(LIBRARY, """
            sizes = {"axes.titlesize": 20, "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.labelsize": 13}
            with plt.rc_context(sizes):
                fig, ax = plt.subplots()
                sns.barplot(data, x="Species", y="Sepal.Length", errorbar=None, ax=ax)
                ax.set_title("Iris")
            f = chart_facts(ax)
            sizes = f["font_sizes"]
            {"title": sizes[0], "x label": sizes[1], "x ticks": sizes[3], "y ticks": sizes[4], "setosa": f["bars"][0][3]}
        """), "matplotlib rc_context (axes.titlesize, xtick.labelsize ...)", option="title=", r="""
            list(setosa = mean(Sepal.Length[Species == "setosa"]))
        """, note="The axis names keep the paper look's size at text size 12 (13 points)."),
        _case(Case, "put_legend_at_bottom", "warpbreaks: lines of the two wools, the legend below in rows of 1",
              "warpbreaks", _ours(f"""
            {WOOL_LINES}
            chart.put_legend_at_bottom(per_row=1)
        """, """
            {"legends on the figure": sum(p[0] == "figure" for p in f["legend_place"]),
             "place": f["legend_place"][0][1], "columns": f["legend_place"][0][3],
             "entries": len(f["legend_place"][0][4]) - 1}
        """, "the legend"), _library(WOOL_SEABORN, """
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            fig.legend(handles, labels, title="wool", loc="outside lower center", ncols=1)
        """, """
            {"legends on the figure": sum(p[0] == "figure" for p in f["legend_place"]),
             "place": f["legend_place"][0][1], "columns": f["legend_place"][0][3],
             "entries": len(f["legend_place"][0][4]) - 1}
        """), 'matplotlib fig.legend(loc="outside lower center", ncols=)', tolerance=0.0, option="per_row=", r="""
            list(entries = length(unique(wool)))
        """, r_tolerance=0.0),
    ]


def _cases_colour_bars_and_3d(Case):
    """The colour bar words and the 3D words."""
    view_read = """
        {"z named Petal.Length": float(f["in_3d"][0] == "Petal.Length"), "z from": f["in_3d"][1][0],
         "z to": f["in_3d"][1][1], "dots": len(f["in_3d"][2][0][1]), "seen from height": float(ax.elev),
         "seen from round": float(ax.azim), "z ticks": len([t for t in ax.get_zticks()
                                                           if f["in_3d"][1][0] <= t <= f["in_3d"][1][1]])}
    """

    def view_case(word, title, step, draw, label, ours_read=""):
        return _case(Case, word, title, "iris", _ours(f"""
            {IRIS_3D}
            chart.{step}
        """, ours_read or view_read, "the 3D view or the z-axis's name and ticks"),
            _library(IRIS_3D_MATPLOTLIB, draw, view_read), label, tolerance=1e-12)

    return [
        *[_colour_bar_case(Case, side) for side in ("bottom", "top", "left")],
        _case(Case, "hide_colour_bar", "warpbreaks: average breaks of each wool and tension, no colour bar",
              "warpbreaks", _ours(f"""
            {WOOL_HEATMAP}
            chart.hide_colour_bar()
        """, """
            {"colour bars": len(f["colour_bars"]), "cells": f["cells"][0][0],
             "total of the cells": float(np.nansum(f["cells"][0][1])), "scale high": f["cells"][0][4]}
        """, "the colour bar"), _library(WOOL_HEATMAP_SEABORN, """
            {"colour bars": len(f["colour_bars"]), "cells": f["cells"][0][0],
             "total of the cells": float(np.nansum(f["cells"][0][1])), "scale high": f["cells"][0][4]}
        """), "seaborn heatmap(cbar=False)", r=WOOL_AVERAGES_R + """
            list(cells = length(m), `total of the cells` = sum(m), `scale high` = max(m))
        """),
        _case(Case, "put_ticks_colour_bar", "warpbreaks: average breaks of each wool and tension, the colour bar "
              "ticked at 20, 30 and 40", "warpbreaks", _ours(f"""
            {WOOL_HEATMAP}
            chart.put_ticks_colour_bar(20, 30, 40)
        """, """
            bar = [a for a in fig.axes if a.get_label() == "<colorbar>"][0]
            low, high = f["colour_bars"][0][1]
            ticks = [t for t in bar.get_yticks() if low <= t <= high]
            {"ticks": len(ticks), "first tick": ticks[0], "last tick": ticks[-1], "scale low": low, "scale high": high}
        """, "the ticks of the colour bar"), _library(WOOL_HEATMAP_SEABORN, """
            bar = fig.colorbar(ax.collections[0], ax=ax, label="breaks")
            bar.set_ticks([20, 30, 40])
        """, """
            low, high = f["colour_bars"][0][1]
            ticks = [t for t in bar.ax.get_yticks() if low <= t <= high]
            {"ticks": len(ticks), "first tick": ticks[0], "last tick": ticks[-1], "scale low": low, "scale high": high}
        """), "matplotlib Colorbar.set_ticks", r=WOOL_AVERAGES_R + """
            list(`scale low` = min(m), `scale high` = max(m))
        """),
        _case(Case, "label_z", "Fisher's iris in 3D, the z-axis named \"Petal length (cm)\"", "iris", _ours(f"""
            {IRIS_3D}
            chart.label_z("Petal length (cm)")
        """, """
            text = chart.get_text_drawn()
            name = text.keep_rows_where("part", is_equal_to="z label").get_cell_at(row=1, column="text")
            {"named as asked": float(name == "Petal length (cm)"), "dots": chart.get_numbers_drawn().count_rows()}
        """), _library(IRIS_3D_MATPLOTLIB, """
            ax.set_zlabel("Petal length (cm)")
        """, """
            {"named as asked": float(f["in_3d"][0] == "Petal length (cm)"), "dots": len(f["in_3d"][2][0][1])}
        """), "matplotlib set_zlabel", tolerance=0.0, r="""
            list(dots = length(Petal.Length))
        """, r_tolerance=0.0),
        _case(Case, "set_range_z", "Fisher's iris in 3D, petal length shown from 0 to 8 cm", "iris", _ours(f"""
            {IRIS_3D}
            chart.set_range_z(0, 8)
        """, """
            z = chart.get_scales_drawn().keep_rows_where("scale", is_equal_to="z")
            {"z from": z.get_cell_at(row=1, column="low"), "z to": z.get_cell_at(row=1, column="high")}
        """), _library(IRIS_3D_MATPLOTLIB, """
            ax.set_zlim(0, 8)
        """, """
            {"z from": f["in_3d"][1][0], "z to": f["in_3d"][1][1]}
        """), "matplotlib set_zlim", tolerance=0.0),
        view_case("put_ticks_z", "Fisher's iris in 3D, z ticks at 0, 2, 4 and 6", "put_ticks_z(0, 2, 4, 6)",
                  "ax.set_zticks([0, 2, 4, 6])", "matplotlib set_zticks"),
        view_case("look_from", "Fisher's iris in 3D, seen from 20 degrees up and 45 degrees round",
                  "look_from(height=20, around=45)", "ax.view_init(elev=20, azim=45)", "matplotlib view_init"),
        _case(Case, "draw_surface", "mtcars: fuel use over weight and horsepower as a wire frame", "mtcars", _ours("""
            chart = sdata.chart(data).draw_surface(x="wt", y="hp", z="mpg", as_wires=True)
        """, """
            wires = [c for c in ax.collections if c.__class__.__name__ == "Line3DCollection"]
            points = np.concatenate([np.asarray(s, dtype=float) for s in wires[0]._segments3d if len(s)])
            {"wire frames": len(wires), "highest point": float(np.nanmax(points[:, 2])),
             "lowest point": float(np.nanmin(points[:, 2])), "colour scales": len(f["in_3d"][3])}
        """, "the wires of a 3D wire frame"), _library(GRID_MTCARS, """
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            ax.plot_wireframe(gx, gy, gz, linewidth=0.8)
        """, """
            wires = [c for c in ax.collections if c.__class__.__name__ == "Line3DCollection"]
            points = np.concatenate([np.asarray(s, dtype=float) for s in wires[0]._segments3d if len(s)])
            {"wire frames": len(wires), "highest point": float(np.nanmax(points[:, 2])),
             "lowest point": float(np.nanmin(points[:, 2])), "colour scales": len(f["in_3d"][3])}
        """), "SciPy griddata + matplotlib plot_wireframe", option="as_wires=",
              note="matplotlib keeps the 3D points of wires only in the private _segments3d. It draws at most 50 "
                   "wires each way, so the highest wire is not the highest car: R is not asked."),
        _case(Case, "draw_surface", "mtcars: fuel use over weight and horsepower as a surface with height lines on "
              "the floor", "mtcars", _ours("""
            chart = sdata.chart(data).draw_surface(x="wt", y="hp", z="mpg", with_height_lines=True)
        """, """
            lines = [c for c in ax.collections if hasattr(c, "levels")]
            {"surface pieces": f["in_3d"][3][0][0], "highest piece": float(np.nanmax(f["in_3d"][3][0][1])),
             "height lines": len(lines[0].levels), "lowest height line": float(min(lines[0].levels))}
        """, "the height lines of a 3D surface"), _library(GRID_MTCARS, """
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            kw = dict(cmap="viridis", vmin=np.nanmin(gz), vmax=np.nanmax(gz))
            ax.plot_surface(gx, gy, np.ma.masked_invalid(gz), linewidth=0, **kw)
            ax.contour(gx, gy, gz, zdir="z", offset=np.nanmin(gz), levels=10, **kw)
        """, """
            lines = [c for c in ax.collections if hasattr(c, "levels")]
            {"surface pieces": f["in_3d"][3][0][0], "highest piece": float(np.nanmax(f["in_3d"][3][0][1])),
             "height lines": len(lines[0].levels), "lowest height line": float(min(lines[0].levels))}
        """), "SciPy griddata + matplotlib plot_surface + contour(zdir=\"z\")", option="with_height_lines="),
    ]


def _cases_options(Case):
    """Options of older words: y= of histograms and densities, violins in halves, dots of averages, stacked bars,
    a ring (pie with a hole)."""
    return [
        _case(Case, "draw_histogram", "Fisher's iris: how many flowers have each sepal length and width (10 x 10 "
              "bins)", "iris", _ours("""
            chart = sdata.chart(data).draw_histogram(x="Sepal.Length", y="Sepal.Width")
        """, """
            cells = chart.get_numbers_drawn()
            {"flowers": cells.get_column("value").find_total(), "most in one cell": cells.get_column("value").find_biggest(),
             "cells": cells.count_rows(), "colour bar high": f["colour_bars"][0][1][1]}
        """, "the colour bar"), _library("""
            fig, ax = plt.subplots(layout="constrained")
            sns.histplot(data, x="Sepal.Length", y="Sepal.Width", bins=10, cmap="viridis", ax=ax)
            fig.colorbar(ax.collections[0], ax=ax, label="count")
        """, """
            counts = f["cells"][0][1]
            {"flowers": float(np.nansum(counts)), "most in one cell": float(np.nanmax(counts)),
             "cells": f["cells"][0][0], "colour bar high": f["colour_bars"][0][1][1]}
        """), "seaborn histplot(x=, y=, bins=10)", tolerance=0.0, option="y=", r="""
            bx <- seq(min(Sepal.Length), max(Sepal.Length), length.out = 11)
            by <- seq(min(Sepal.Width), max(Sepal.Width), length.out = 11)
            counts <- table(cut(Sepal.Length, bx, right = FALSE, include.lowest = TRUE),
                            cut(Sepal.Width, by, right = FALSE, include.lowest = TRUE))
            list(flowers = sum(counts), `most in one cell` = max(counts), cells = length(counts))
        """, r_tolerance=0.0, note="Ten equal bins along each axis; the last bin holds its upper end, as in NumPy."),
        _case(Case, "draw_density", "Fisher's iris: the density of sepal length and width together, as height "
              "lines", "iris", _ours("""
            chart = sdata.chart(data).draw_density(x="Sepal.Length", y="Sepal.Width")
        """, """
            lines = chart.get_numbers_drawn()
            {"height lines": lines.count_different_values_in("value"),
             "lowest height": lines.get_column("value").find_smallest(),
             "highest height": lines.get_column("value").find_biggest()}
        """), _library("""
            fig, ax = plt.subplots()
            sns.kdeplot(data, x="Sepal.Length", y="Sepal.Width", ax=ax)
        """, """
            levels = [c for c in ax.collections if hasattr(c, "levels")][0]
            drawn = [v for v, segs in zip(levels.levels, levels.allsegs) if any(len(s) for s in segs)]
            {"height lines": len(drawn), "lowest height": float(min(drawn)), "highest height": float(max(drawn))}
        """), "seaborn kdeplot(x=, y=)", option="y=",
              note="seaborn's own levels (the heights that hold 10 %, 20 % ... of the density) and bandwidth."),
        _case(Case, "draw_violins", "warpbreaks: breaks at each tension, wool A on the left half, wool B on the right",
              "warpbreaks", _ours("""
            chart = sdata.chart(data).draw_violins(x="tension", y="breaks", colour="wool", in_halves=True)
        """, """
            halves = [s for s in f["shapes"] if s[0] > 4]
            {"halves": len(halves), "top of the highest half": max(float(s[1][:, 1].max()) for s in halves),
             "bottom of the lowest half": min(float(s[1][:, 1].min()) for s in halves)}
        """, "the outlines of violins"), _library("""
            fig, ax = plt.subplots()
            sns.violinplot(data, x="tension", y="breaks", hue="wool", split=True, cut=0, gap=0.1, saturation=1, ax=ax)
        """, """
            halves = [s for s in f["shapes"] if s[0] > 4]
            {"halves": len(halves), "top of the highest half": max(float(s[1][:, 1].max()) for s in halves),
             "bottom of the lowest half": min(float(s[1][:, 1].min()) for s in halves)}
        """), "seaborn violinplot(split=True, cut=0)", option="in_halves=", r="""
            list(halves = 6, `top of the highest half` = max(breaks), `bottom of the lowest half` = min(breaks))
        """, note="cut=0: each half stops at its smallest and largest value."),
        _case(Case, "draw_dots", "warpbreaks: the average breaks at each tension with its standard error",
              "warpbreaks", _ours("""
            chart = sdata.chart(data).draw_dots(x="tension", y="breaks", show="average", error="standard error")
        """, """
            averages = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="dot")
            bar = [line for line in f["lines"] if len(line[0]) > 3 and abs(np.nanmean(line[0])) < 0.2][0]
            {"average at L": averages.get_cell_at(row=1, column="y"), "average at H": averages.get_cell_at(row=3, column="y"),
             "standard error at L": float((np.nanmax(bar[1]) - np.nanmin(bar[1])) / 2)}
        """, "error bars over named groups"), _library("""
            fig, ax = plt.subplots()
            sns.pointplot(data, x="tension", y="breaks", estimator="mean", errorbar="se", linestyle="none",
                          capsize=0.1, ax=ax)
        """, """
            dots = [line for line in f["lines"] if len(line[0]) == 3][0]
            bar = [line for line in f["lines"] if len(line[0]) > 3 and abs(np.nanmean(line[0])) < 0.2][0]
            {"average at L": float(dots[1][0]), "average at H": float(dots[1][2]),
             "standard error at L": float((np.nanmax(bar[1]) - np.nanmin(bar[1])) / 2)}
        """), 'seaborn pointplot(errorbar="se")', option="show=", r="""
            l <- breaks[tension == "L"]
            list(`average at L` = mean(l), `average at H` = mean(breaks[tension == "H"]),
                 `standard error at L` = sd(l) / sqrt(length(l)))
        """, tolerance=1e-12, r_tolerance=1e-12),
        _case(Case, "draw_bars", "warpbreaks: each wool's share of the breaks at each tension, stacked to 100 %",
              "warpbreaks", _ours("""
            chart = sdata.chart(data).draw_bars(x="tension", y="breaks", colour="wool", stacked="percent")
        """, """
            bars = chart.get_numbers_drawn()
            a = bars.keep_rows_where("series", is_equal_to="A")
            a_at_l = a.get_cell_at(row=1, column="y")
            bars.undo()
            b = bars.keep_rows_where("series", is_equal_to="B")
            {"wool A at L (%)": a_at_l, "wool B at H (%)": b.get_cell_at(row=3, column="y"),
             "top of each stack": b.get_column("high").find_biggest(),
             "y-axis named": float(f["labels"][1] == "percent of total breaks")}
        """, "the name of the y-axis"), _library("""
            fig, ax = plt.subplots()
            wide = data.groupby(["tension", "wool"])["breaks"].sum().unstack("wool").loc[["L", "M", "H"]]
            shares = wide.div(wide.sum(axis=1), axis=0).mul(100)
            shares.plot(kind="bar", stacked=True, rot=0, width=0.8, ax=ax)
            ax.set_ylabel("percent of total breaks")
        """, """
            # pandas draws all the bars of wool A (L, M, H), then those of wool B on top
            heights = [p.get_height() for p in ax.patches]
            {"wool A at L (%)": heights[0], "wool B at H (%)": heights[5],
             "top of each stack": max(p.get_y() + p.get_height() for p in ax.patches),
             "y-axis named": float(f["labels"][1] == "percent of total breaks")}
        """), "pandas DataFrame.plot(kind=\"bar\", stacked=True)", option="stacked=", r="""
            list(`wool A at L (%)` = 100 * sum(breaks[wool == "A" & tension == "L"]) / sum(breaks[tension == "L"]),
                 `wool B at H (%)` = 100 * sum(breaks[wool == "B" & tension == "H"]) / sum(breaks[tension == "H"]),
                 `top of each stack` = 100)
        """),
        _case(Case, "draw_pie", "mtcars: the share of cars with 4, 6 and 8 cylinders as a ring", "mtcars", _ours("""
            chart = sdata.chart(data).draw_pie(labels="cyl", hole=0.4)
        """, """
            slices = chart.get_numbers_drawn()
            from matplotlib.patches import Wedge
            wedges = [p for p in ax.patches if isinstance(p, Wedge)]
            {"slices": slices.count_rows(), "largest share": slices.get_column("value").find_biggest(),
             "ring width": float(wedges[0].width), "percents": sum(t.endswith("%") for t in f["texts"][1])}
        """, "the width of the ring"), _library("""
            from matplotlib.patches import Wedge
            fig, ax = plt.subplots()
            counts = data["cyl"].value_counts(sort=False)
            ax.pie(counts, labels=counts.index, autopct="%1.0f%%", startangle=90, counterclock=False,
                   wedgeprops=dict(width=1 - 0.4), pctdistance=1 - (1 - 0.4) / 2)
            wedges = [p for p in ax.patches if isinstance(p, Wedge)]
        """, """
            {"slices": len(wedges), "largest share": float(counts.max() / counts.sum()),
             "ring width": float(wedges[0].width), "percents": sum(t.endswith("%") for t in f["texts"][1])}
        """), "matplotlib pie(wedgeprops=dict(width=))", option="hole=", r="""
            list(slices = length(unique(cyl)), `largest share` = max(table(cyl)) / length(cyl))
        """),
    ]


def _cases_web(Case):
    """The web-page words: the plotly figure's own arrays and layout against what matplotlib drew."""
    return [
        Case("show_in_web_page", "mtcars: fuel use against weight as a web page", "mtcars", "real data",
             ours=_code(WEB, """
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg")
                 # show_in_web_page() opens the page in a browser; it shows this plotly figure
                 page = _web.web_figure(chart)
                 dots = [t for t in page.data if t.type == "scatter" and t.mode == "markers" and len(t.x)]
                 xs = np.concatenate([np.asarray(t.x, dtype=float) for t in dots])
                 ys = np.concatenate([np.asarray(t.y, dtype=float) for t in dots])
                 {"dots": len(xs), "sum of x": float(xs.sum()), "sum of y": float(ys.sum()),
                  "x from": float(page.layout.xaxis.range[0]), "x to": float(page.layout.xaxis.range[1])}
             """),
             parent=_library(MTCARS_SEABORN, """
                 xy = np.asarray(f["dots"], dtype=float)
                 {"dots": len(xy), "sum of x": float(xy[:, 0].sum()), "sum of y": float(xy[:, 1].sum()),
                  "x from": f["limits"][0][0], "x to": f["limits"][0][1]}
             """), parent_label="seaborn scatterplot read with chart_facts (the picture)", parent_tolerance=1e-12,
             r="""
                 list(dots = length(mpg), `sum of x` = sum(wt), `sum of y` = sum(mpg))
             """, r_tolerance=1e-12,
             note="The plotly figure's own x, y and axis range (not simplydata's meta in it)."),
        Case("show_when_pointing", "mtcars: each dot names its car when the pointer rests on it", "mtcars",
             "real data",
             ours=_code(WEB, """
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg").show_when_pointing("model")
                 page = _web.web_figure(chart)
                 dots = [t for t in page.data if t.type == "scatter" and t.mode == "markers" and len(t.x)]
                 pairs = [(float(x), float(y), str(text)) for t in dots for x, y, text in zip(t.x, t.y, t.text)]
                 rows = {(float(w), float(m), n) for w, m, n in zip(data["wt"], data["mpg"], data["model"])}
                 {"dots": len(pairs), "dots naming their own car": sum(any((x, y, n) in rows and n in text
                                                                           for n in data["model"])
                                                                       for x, y, text in pairs),
                  "other columns shown": sum("cyl" in text for _, _, text in pairs)}
             """),
             parent="""
                 {"dots": len(data), "dots naming their own car": len(data), "other columns shown": 0}
             """, parent_label="pandas: one row (car) for each dot", parent_tolerance=0.0,
             note="Only the named column is in the hover text; each car is named at its own dot."),
        Case("add_range_bar_x", "Lake Huron: the level each year as a web page with a range bar", "Lake Huron",
             "real data",
             ours=_code(WEB, """
                 chart = sdata.chart(data).draw_lines(x="year", y="level").add_range_bar_x()
                 page = _web.web_figure(chart)
                 line = [t for t in page.data if t.type == "scatter" and len(t.x)][0]
                 {"range bar": float(bool(page.layout.xaxis.rangeslider.visible)), "years": len(line.x),
                  "first level": float(line.y[0]), "last level": float(line.y[-1])}
             """),
             parent=_library("""
                 fig, ax = plt.subplots()
                 sns.lineplot(data, x="year", y="level", errorbar=None, ax=ax)
             """, """
                 {"range bar": 1.0, "years": len(f["lines"][0][0]), "first level": float(f["lines"][0][1][0]),
                  "last level": float(f["lines"][0][1][-1])}
             """), parent_label="seaborn lineplot (the picture) + plotly rangeslider", parent_tolerance=1e-12,
             r="""
                 list(years = length(level), `first level` = level[1], `last level` = level[length(level)])
             """, r_tolerance=1e-12),
    ]


def cases(Case):
    return (_cases_batch1(Case) + _cases_new_marks(Case) + _cases_axes_and_look(Case) + _cases_colour_bars_and_3d(Case)
            + _cases_options(Case) + _cases_web(Case))
