"""Charts phase, batch 1 (approved by Manish 2026-11-25): reading a chart back (get_text_drawn, get_scales_drawn,
get_size), a step back (undo), a panel letter (write_letter), the legend inside the chart (put_legend_inside) and
the dot shapes of the groups (use_shapes).
"""

from . import Entry
from .charts import LOOK

ENTRIES = [
    Entry(
        word="get_text_drawn",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks", colour="class")
            text = chart.get_text_drawn()
            text.keep_rows_where("part", is_equal_to="legend entry").keep_columns("text")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", hue="class", ax=ax)
            # get_text_drawn(): the words matplotlib keeps of the legend
            pd.DataFrame({"text": [t.get_text() for t in ax.get_legend().get_texts()]})
        """},
        compare="table",
        also="simplydata reads every piece of text the same way (Axes.get_title, get_xlabel, get_ylabel, "
             "Figure.get_suptitle, the legend's title and entries, Axes.texts, the tick labels shown and the colour "
             "bar's label), names what each one is (part) and where a legend or a note is, and numbers the panels "
             "as get_numbers_drawn() does.",
    ),
    Entry(
        word="get_scales_drawn",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            scales = chart.get_scales_drawn()
            scales.keep_columns("scale", "low", "high")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import pandas as pd
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            ax.scatter(df["hours"], df["marks"])
            # get_scales_drawn(): the ranges matplotlib shows
            (x_low, x_high), (y_low, y_high) = ax.get_xlim(), ax.get_ylim()
            pd.DataFrame({"scale": ["x", "y"], "low": [x_low, y_low], "high": [x_high, y_high]})
        """},
        compare="table",
        also="simplydata also reads each axis's kind (Axes.get_xscale, dates and named groups through the axis's "
             "converter), whether it is flipped (xaxis_inverted), its ticks and tick words, the panels that share "
             "its range, and each colour scale (the colour map's name, norm.vmin, norm.vmax and the middle of a "
             "TwoSlopeNorm).",
    ),
    Entry(
        word="get_size",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.set_size(width=17, height=12, unit="cm")
            chart.get_size(unit="cm")
        """,
        code={"matplotlib": """
            import io
            import matplotlib.pyplot as plt
            from PIL import Image
            fig = plt.figure(figsize=(17 / 2.54, 12 / 2.54))
            # get_size(unit="cm"): the picture savefig writes at 300 dots per inch
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=300)
            width, height = Image.open(buffer).size
            (round(width / 300 * 2.54, 4), round(height / 300 * 2.54, 4))
        """},
        compare="value",
        tolerance=1e-9,
        also="simplydata also gives the size in inches, mm or pixels, and the size of a whole page of charts; "
             "without set_size it is the size of the page trimmed to what is drawn, as chart.save() writes it.",
    ),
    Entry(word="undo", ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.use_log_scale_y()
            chart.undo()
        """, compare="none",
          note="simplydata's own: a chart is a list of steps drawn only when it is shown or saved, so undo takes the "
               "last word's steps and settings back before anything is drawn again. In matplotlib you would draw the "
               "chart again without that line."),
    Entry(
        word="write_letter",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.write_letter("B")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # write_letter("B")
            ax.set_title("B", loc="left", fontweight="bold")
        """},
        compare="chart",
        check=("dots", "labels"),
        also="The letter is written a little bigger than the title, in bold, as with_letters=True writes it on a "
             "page of charts; on a chart of several panels it goes on its own line above them. " + LOOK,
    ),
    Entry(
        word="put_legend_inside",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.put_legend_inside("top left")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
            # put_legend_inside("top left")
            sns.move_legend(ax, "upper left")
        """},
        compare="chart",
        check=("legend_place", "legend"),
        also="simplydata names the places in plain words (\"top left\", \"middle\", \"best\" ...) and also takes "
             "in the entries of a second y-axis. " + LOOK,
    ),
    Entry(
        word="use_shapes",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks", colour="class")
            chart.use_shapes("circle", "square", "triangle")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # use_shapes("circle", "square", "triangle"): one shape for each class
            sns.scatterplot(df, x="hours", y="marks", hue="class", style="class",
                            markers=["o", "s", "^"], ax=ax)
        """},
        compare="chart",
        check=("dots", "dot_colour_groups", "legend"),
        also="simplydata names the shapes in words (\"circle\", \"square\", \"triangle\", \"diamond\" ...) and "
             "repeats them when there are more groups than shapes. " + LOOK,
    ),
]
