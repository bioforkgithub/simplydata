"""Chart words: the same chart drawn with seaborn or matplotlib (and R's numbers for R words).

The test compares the chart's data (bars, dots, lines, labels, limits), not its pixels: simplydata's
paper look (fonts, colours, no top and right lines) is left out of the code on purpose.
"""

from . import Entry

LOOK = ("simplydata also gives the chart its paper look (fonts, colours, no top and right lines); that is left "
        "out here.")
LOOK_BUT_FONTS = "The rest of simplydata's paper look (colours, no top and right lines) is left out here."
LOOK_BUT_COLOURS = "The rest of simplydata's paper look (fonts, no top and right lines) is left out here."

ENTRIES = [
    Entry(
        word="draw_bars",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="name", y="marks", colour="class")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_bars(x="name", y="marks", colour="class")
            sns.barplot(df, x="name", y="marks", hue="class",
                        errorbar=None, ax=ax)           # (1)
        """},
        compare="chart",
        check=("bars", "bar_colour_groups", "lines", "labels", "ticks", "legend", "limits"),
        choices=("simplydata draws no error bars unless you ask (error=); seaborn's own default draws a "
                 "bootstrap 95 % interval on each bar.",),
        also="Each bar is the average of its rows, as in seaborn. " + LOOK,
    ),
    Entry(
        word="draw_histogram",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_histogram(x="marks")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_histogram(x="marks")
            sns.histplot(df, x="marks", bins=10, ax=ax)   # (1)
        """},
        compare="chart",
        check=("bars", "ticks", "limits"),
        choices=("simplydata makes 10 bins unless you say with_bins=; seaborn's own default chooses the number "
                 "of bins from the data.",),
        also="simplydata writes the y label in small letters (count). " + LOOK,
    ),
    Entry(
        word="draw_dots",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks", colour="class", size="height")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_dots(x="hours", y="marks", colour="class", size="height")
            sns.scatterplot(df, x="hours", y="marks", hue="class",
                            size="height", ax=ax)
        """},
        compare="chart",
        check=("dots", "dot_size_shares", "dot_colour_groups", "labels", "legend", "limits"),
        also="simplydata's paper look draws every dot a little bigger; the sizes keep the same proportions. "
             + LOOK,
    ),
    Entry(
        word="trade_off_curve",
        data="clinic",
        ours="""
            chart = sdata.chart(sdata.get_example("clinic"))
            chart.trade_off_curve(score="crp", truth="infected")
        """,
        code={
            "R": """
                # trade_off_curve(score="crp", truth="infected")
                # infected (1 = yes, 0 = no) and crp: two columns of sdata.get_example("clinic")
                r <- pROC::roc(infected, crp, levels = c(0, 1),
                               direction = "<", quiet = TRUE)      # (1)
                ci <- pROC::ci.auc(r, method = "delong")           # (2)
                p <- pROC::coords(r, "all", ret = c("specificity", "sensitivity"),
                                  transpose = FALSE)
                b <- pROC::coords(r, "best", best.method = "youden",
                                  ret = c("specificity", "sensitivity"), transpose = FALSE)
                list(x = 1 - p$specificity, y = p$sensitivity,
                     best_x = 1 - b$specificity[1], best_y = b$sensitivity[1],
                     auc = ci[2], auc_low = ci[1], auc_high = ci[3])
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                import numpy as np
                fig, ax = plt.subplots()
                order = np.lexsort((y, x))
                ax.plot(x[order], y[order])                         # the curve
                ax.plot([best_x], [best_y], marker="o")             # (3)
                ax.plot([0, 1], [0, 1], linestyle="--")             # no better than chance
            """,
        },
        r_inputs="""
            clinic = sdata.get_example("clinic").dropna(subset=["crp", "infected"])
            infected = (clinic["infected"] == "yes").to_numpy(dtype=float)
            crp = clinic["crp"].to_numpy(dtype=float)
        """,
        r_packages=("pROC",),
        compare="chart",
        check=("lines",),
        legend_pattern=r"AUC (\S+) \(95 % CI (\S+) to (\S+)\)",
        legend_numbers=("auc", "auc_low", "auc_high"),
        choices=(
            "higher scores count as positive (direction = \"<\"); positive_when=\"lower\" turns it round.",
            "the AUC and its 95 % interval by DeLong's method, written in the legend.",
            "the best cut-off by Youden's index (the most found cases minus false alarms) is marked with a dot.",
        ),
        python_note="Python's stack (SciPy, statsmodels) has no ROC analysis with DeLong's interval, so the "
                    "numbers come from R.",
        also="simplydata also writes the AUC and the cut-off on the chart and labels both axes in words. " + LOOK,
    ),
]


# ---------------------------------------------------------------- U-batch 2: words that change how a chart looks
# The chart words below sit on top of a chart type. Each box draws that chart type the way simplydata does, then makes
# the one call the word adds. Where the chart facts above could not see the change (words on the figure, font sizes,
# the size, the legend's place, the colours themselves, the angle of tick labels), a fact was added for it.

ENTRIES += [
    Entry(
        word="save",
        data="marks",
        ours="""
            import os
            import tempfile
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="name", y="marks")
            chart.save(os.path.join(tempfile.gettempdir(), "marks.png"))
        """,
        code={"matplotlib": """
            import os
            import tempfile
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots(figsize=(8, 6))                       # (1)
            sns.barplot(df, x="name", y="marks", errorbar=None, ax=ax)
            # save("marks.png")
            fig.savefig(os.path.join(tempfile.gettempdir(), "marks_mpl.png"),
                        dpi=300, bbox_inches="tight")                    # (2)
        """},
        compare="chart",
        check=("size", "bars", "ticks"),
        choices=("a chart is 8 x 6 inches unless set_size() says otherwise; matplotlib's own default is 6.4 x 4.8.",
                 "300 dots per inch, with the empty edges trimmed: sharp enough for a journal. quality=\"high\" "
                 "saves at 600, resolution= at any value; a .tif file is packed without loss (LZW).",),
        also="The end of the file name chooses the format (.png, .pdf, .svg, .tif, .jpg), as in matplotlib. "
             "After set_size() the file is exactly that size, edges and all. The test compares the chart that is "
             "saved, not the pixels of the file. " + LOOK,
    ),
    Entry(
        word="write_title_on_top",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.write_title_on_top("Marks in each class")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
            # write_title_on_top("Marks in each class")
            ax.set_title("Marks in each class")                          # (1)
        """},
        compare="chart",
        check=("labels", "bars"),
        choices=("one chart gets the title of its axes; a figure with several panels gets one title over them all "
                 "(fig.suptitle), in bold.",),
        also="simplydata writes titles in bold and a little bigger than the other words. " + LOOK,
    ),
    Entry(
        word="label_x",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.label_x("Hours of study")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # label_x("Hours of study")
            ax.set_xlabel("Hours of study")                              # (1)
        """},
        compare="chart",
        check=("labels", "dots"),
        choices=("on a figure with several panels the panels' own x labels are cleared and one label is written "
                 "under them all (fig.supxlabel).",),
        also=LOOK,
    ),
    Entry(
        word="label_y",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.label_y("Marks (out of 100)")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # label_y("Marks (out of 100)")
            ax.set_ylabel("Marks (out of 100)")                          # (1)
        """},
        compare="chart",
        check=("labels", "dots"),
        choices=("on a figure with several panels the panels' own y labels are cleared and one label is written "
                 "beside them all (fig.supylabel).",),
        also=LOOK,
    ),
    Entry(
        word="rotate_labels_x",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="name", y="marks")
            chart.rotate_labels_x(45)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.barplot(df, x="name", y="marks", errorbar=None, ax=ax)
            # rotate_labels_x: 45 degrees
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_horizontalalignment("right")                   # (1)
                label.set_verticalalignment("top")
                label.set_rotation_mode("anchor")                        # (2)
        """},
        compare="chart",
        check=("tick_angles", "ticks", "bars"),
        choices=("a turned name is lined up by its right end (its left end for a negative angle), so it ends just "
                 "under its own bar; matplotlib's own default centres it, and long names then drift sideways.",
                 "the name turns about that end (rotation mode \"anchor\"), so it stays next to its tick.",),
        also="It runs after put_ticks_x(), so new tick labels are turned too. " + LOOK,
    ),
    Entry(
        word="write_caption_at_bottom",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.write_caption_at_bottom("Made-up data from sdata.get_example")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots(layout="constrained")
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
            # write_caption_at_bottom("Made-up data from sdata.get_example")
            ax.annotate("Made-up data from sdata.get_example", xy=(0.5, 0),
                        xycoords=ax.xaxis.label, xytext=(0, -4),
                        textcoords="offset points", ha="center", va="top",  # (1)
                        fontsize=0.8 * plt.rcParams["font.size"], alpha=0.8)  # (2)
        """},
        compare="chart",
        check=("texts", "bars", "labels"),
        choices=("the caption hangs just under the x-axis label, so it moves down when the labels are turned or "
                 "grow; on a figure with several panels it is the figure's bottom line instead (fig.supxlabel).",
                 "in smaller (0.8 of the font size), slightly faded letters, so it reads as a note, not a label.",),
        also=LOOK,
    ),
    Entry(
        word="use_font_size",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.write_title_on_top("Big text")
            chart.use_font_size(18)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # use_font_size: 18, so every size grows by 18 / 12
            sizes = {"font.size": 18, "axes.titlesize": 21, "axes.labelsize": 19.5,
                     "xtick.labelsize": 16.5, "ytick.labelsize": 16.5,
                     "legend.fontsize": 16.5}                            # (1)
            with plt.rc_context(sizes):
                fig, ax = plt.subplots()
                sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
                ax.set_title("Big text")
        """},
        compare="chart",
        check=("font_sizes", "labels", "bars"),
        choices=("all the words grow together: simplydata's normal sizes are 12 for text, 14 for the title, 13 for "
                 "the axis labels and 11 for tick labels and the legend, and use_font_size(18) multiplies each by "
                 "18 / 12, so the title stays the biggest.",),
        also="matplotlib's own normal size is 10. " + LOOK_BUT_FONTS,
    ),
    Entry(
        word="use_colour",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.use_colour("purple")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # use_colour("purple")
            sns.barplot(df, x="class", y="marks", errorbar=None, color="purple",
                        saturation=1, ax=ax)                             # (1)
        """},
        compare="chart",
        check=("colours", "bars"),
        choices=("the exact colour asked for (saturation=1); seaborn's own default (0.75) makes bar colours a "
                 "little duller than the name says.",),
        also="Any matplotlib colour name or a code such as \"#0072B2\" works. Without groups every chart type uses "
             "it; with groups use_colours() chooses the colours. " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="use_colours",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="subject", y="marks", colour="class")
            chart.use_colours("orange", "teal", "purple")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # use_colours("orange", "teal", "purple")
            sns.barplot(df, x="subject", y="marks", hue="class",
                        hue_order=["A", "B", "C"],                       # (1)
                        palette=["orange", "teal", "purple"],
                        errorbar=None, saturation=1, ax=ax)              # (2)
        """},
        compare="chart",
        check=("colours", "bars", "legend"),
        choices=("the groups get the colours in the order they first appear in the table (order_legend() changes "
                 "it); seaborn sorts the names of some columns first.",
                 "the exact colours asked for (saturation=1), not seaborn's slightly duller ones.",),
        also="With more groups than colours the colours repeat, and a line says so. " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="put_legend_at_bottom",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.put_legend_at_bottom()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots(layout="constrained")
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
            # put_legend_at_bottom()
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            fig.legend(handles, labels, title="city", loc="outside lower center",
                       ncols=3)                                          # (1)
        """},
        compare="chart",
        check=("legend_place", "lines"),
        choices=("one row of entries (up to 6 in a row) under the x-axis label, outside the chart, so it covers no "
                 "data; a label shared by several panels becomes the legend's heading.",),
        also="Entries from every panel and from a second y-axis are gathered into this one legend. " + LOOK,
    ),
    Entry(
        word="order_x",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.order_x("C", "B", "A")
        """,
        code={"pandas": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # order_x("C", "B", "A")
            place = {"C": 0, "B": 1, "A": 2}
            df = df.sort_values("class", key=lambda s: s.map(place),
                                kind="stable")                           # (1)
            fig, ax = plt.subplots()
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("ticks", "bars"),
        choices=("the rows are put in that order with a stable sort, and seaborn draws the groups in the order they "
                 "appear, so every chart type, colour and later step follows it; groups left out come after the "
                 "ones named. seaborn's order= does the same for one call.",),
        also="biggest_first=True orders the groups by what the chart shows (average, median, count ...); month and "
             "weekday names come in calendar order without asking. " + LOOK,
    ),
    Entry(
        word="use_style",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="subject", y="marks", colour="class")
            chart.use_style("school")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # use_style("school")
            school = {"font.size": 15, "axes.titlesize": 18, "axes.labelsize": 16,
                      "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 14,
                      "lines.linewidth": 3.0, "lines.markersize": 10,
                      "axes.linewidth": 1.5}                             # (1)
            with plt.rc_context(school):
                fig, ax = plt.subplots()
                sns.barplot(df, x="subject", y="marks", hue="class", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("font_sizes", "bars", "legend"),
        choices=("\"school\" is bigger words and thicker lines, for a classroom screen; \"presentation\" is bigger "
                 "still, \"dark\" puts light words and brighter colours on a dark background, and \"paper\" is the "
                 "normal look.",),
        also="The style is a set of matplotlib settings used while the chart is drawn and saved, so it never "
             "changes your other charts. " + LOOK_BUT_FONTS,
    ),
    Entry(
        word="hide_legend",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.hide_legend()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
            # hide_legend()
            ax.get_legend().remove()                                     # (1)
        """},
        compare="chart",
        check=("legend_place", "legend", "lines"),
        choices=("the legend of every panel (and of a second y-axis) is removed; show_legend() brings it back.",),
        also="seaborn's legend=False does the same while drawing. " + LOOK,
    ),
    Entry(
        word="put_legend_on_left",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.put_legend_on_left()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots(layout="constrained")
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
            # put_legend_on_left()
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            fig.legend(handles, labels, title="city",
                       loc="outside center left")                        # (1)
        """},
        compare="chart",
        check=("legend_place", "lines"),
        choices=("outside the chart on the left, beside the y-axis label, so it covers no data; on a figure with "
                 "several panels the shared y label goes back to the panels on the left.",),
        also=LOOK,
    ),
]

# ---------------------------------------------------------------- U-batch 2: chart types, options and lines on a chart
ENTRIES += [
    Entry(
        word="draw_lines",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city", with_dots=True)
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            # draw_lines(x="month", y="temperature", colour="city", with_dots=True)
            sns.lineplot(df, x="month", y="temperature", hue="city",
                         estimator="mean", errorbar=None,                # (1)
                         marker="o", ax=ax)
        """},
        compare="chart",
        check=("lines", "labels", "ticks", "legend", "limits"),
        choices=("each point is the average of its rows, with no band around the line unless you ask (error=); "
                 "seaborn's own default shades a bootstrap 95 % interval.",),
        also="Month and weekday names come in calendar order. joined_by= draws smooth curves or steps instead of "
             "straight lines. " + LOOK,
    ),
    Entry(
        word="draw_boxes",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_boxes(x="class", y="marks")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_boxes(x="class", y="marks")
            sns.boxplot(df, x="class", y="marks", saturation=1, ax=ax)  # (1)
        """},
        compare="chart",
        check=("shapes", "lines", "ticks", "labels", "limits"),
        choices=("the exact colours (saturation=1), not seaborn's slightly duller ones.",),
        also="The whiskers reach the furthest value within 1.5 box lengths, as in seaborn and R's boxplot(); with "
             "colour= the boxes of one group stand a little apart. " + LOOK,
    ),
    Entry(
        word="draw_all_dots",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_boxes(x="class", y="marks")
            chart.draw_all_dots(x="class", y="marks")
        """,
        code={"seaborn": """
            import seaborn as sns
            from matplotlib.figure import Figure
            df = sdata.get_example("marks")
            fig = Figure(figsize=(8, 6), layout="constrained")           # (1)
            ax = fig.subplots()
            sns.boxplot(df, x="class", y="marks", color="#0072B2", saturation=1, ax=ax)
            # draw_all_dots(x="class", y="marks")
            sns.swarmplot(df, x="class", y="marks",                     # (2)
                          color="#333333", ax=ax)                        # (3)
            ax
        """},
        compare="chart",
        check=("dots", "colours", "shapes", "lines"),
        choices=("simplydata draws on a matplotlib Figure of its own, not on pyplot's current figure, so a chart "
                 "never lands on another one; seaborn works out the sideways spread of a swarm when the picture is "
                 "drawn (shown or saved).",
                 "up to 100 dots in a group are packed side by side (a swarm); above that they are spread at random "
                 "(seaborn stripplot, with the random numbers fixed so the chart is the same every time).",
                 "over boxes or violins the dots are dark grey, so they stand out; colour= still chooses your own.",),
        also="The test compares where each dot belongs (its group and value) and the colours, before the picture "
             "is drawn. The boxes get simplydata's first colour, so their lines have the same shade. " + LOOK,
    ),
    Entry(
        word="draw_violins",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_violins(x="subject", y="marks")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_violins(x="subject", y="marks")
            sns.violinplot(df, x="subject", y="marks", cut=0,           # (1)
                           saturation=1, ax=ax)                          # (2)
        """},
        compare="chart",
        check=("shapes", "lines", "ticks", "labels"),
        choices=("each violin stops at the smallest and the largest value (cut=0), so it never shows values that "
                 "cannot happen, such as marks below 0; seaborn's own default runs the curve on past them.",
                 "the exact colours (saturation=1), not seaborn's slightly duller ones.",),
        also="The width follows seaborn's kernel density estimate (Scott's rule); the small box inside shows the "
             "middle half of the values. " + LOOK,
    ),
    Entry(
        word="show=",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks", show="median")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_bars(x="class", y="marks", show="median")
            sns.barplot(df, x="class", y="marks", estimator="median",   # (1)
                        errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("bars", "ticks", "limits"),
        choices=("the word becomes seaborn's estimator: \"average\" is \"mean\", \"median\" is \"median\", "
                 "\"total\" is \"sum\", \"smallest\" and \"biggest\" are \"min\" and \"max\"; \"count\" counts the "
                 "rows (seaborn countplot).",),
        also="The same words work in draw_lines(). " + LOOK,
    ),
    Entry(
        word="error=",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks", error="standard deviation")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_bars(x="class", y="marks", error="standard deviation")
            sns.barplot(df, x="class", y="marks", errorbar="sd",        # (1)
                        capsize=0.1, err_kws={"linewidth": 1.3}, ax=ax)  # (2)
        """},
        compare="chart",
        check=("bars", "lines", "limits"),
        choices=("\"standard deviation\" is seaborn's \"sd\" and \"standard error\" its \"se\", both with n - 1; "
                 "\"confidence interval\" is the t interval of the mean (as R t.test()), not seaborn's bootstrap.",
                 "short caps at the ends of each error bar.",),
        also="A line is printed saying which error was drawn, so the figure caption can say it too. On lines "
             "error= shades a band instead. " + LOOK,
    ),
    Entry(
        word="write_numbers_on_bars",
        data="fruit",
        ours="""
            chart = sdata.chart(sdata.get_example("fruit"))
            chart.draw_bars(x="fruit", y="count", show="total")
            chart.write_numbers_on_bars()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("fruit")
            fig, ax = plt.subplots()
            sns.barplot(df, x="fruit", y="count", estimator="sum", errorbar=None, ax=ax)
            # write_numbers_on_bars()
            bars = ax.containers[0]
            ax.bar_label(bars, labels=[f"{v:,.0f}" for v in bars.datavalues],
                         padding=3)                                      # (1)
            ax.margins(y=0.12)                                           # (2)
            ax.autoscale_view()
        """},
        compare="chart",
        check=("texts", "bars", "limits"),
        choices=("each value just above its bar, with a comma for thousands and no decimals unless with_decimals= "
                 "asks; stacked bars get the number in the middle of each piece, and with error bars it sits past "
                 "the end of the error bar.",
                 "a little more room above the bars, so the numbers stay inside the chart.",),
        also=LOOK,
    ),
    Entry(
        word="fit_line",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.fit_line()
        """,
        code={"SciPy": """
            import matplotlib.pyplot as plt
            import numpy as np
            import seaborn as sns
            from scipy import stats
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # fit_line()
            fit = stats.linregress(df["hours"], df["marks"])
            xs = np.linspace(df["hours"].min(), df["hours"].max(), 200)   # (1)
            ax.plot(xs, fit.intercept + fit.slope * xs)
        """},
        compare="chart",
        check=("lines", "dots"),
        choices=("the line is drawn only over the range of x in the data, never past it.",),
        also="Each colour group gets its own line. with_confidence_band=True shades the 95 % band of the line "
             "(statsmodels OLS get_prediction); show_equation=True writes the equation and R squared. " + LOOK,
    ),
    Entry(
        word="draw_qq_dots",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_qq_dots("marks")
        """,
        code={"SciPy": """
            import matplotlib.pyplot as plt
            import numpy as np
            from scipy import stats
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_qq_dots("marks")
            (theory, ordered), (slope, intercept, r) = stats.probplot(
                df["marks"].dropna(), dist="norm")                       # (1)
            ax.scatter(theory, ordered)
            ends = np.array([theory[0], theory[-1]])
            ax.plot(ends, intercept + slope * ends)                      # (2)
            ax.set_xlabel("normal quantiles")
            ax.set_ylabel("marks")
        """},
        compare="chart",
        check=("dots", "lines", "labels"),
        choices=("SciPy places the dots at Filliben's positions; R's qqnorm() uses slightly different ones.",
                 "the straight line is the least-squares line through the dots (as SciPy gives it); R's qqline() "
                 "goes through the quartiles instead.",),
        also="for_each_group_in= draws each group in its own colour with its own line; distribution=\"gamma\" (or "
             "another) fits that distribution first. " + LOOK,
    ),
    Entry(
        word="set_range_y",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.set_range_y(0, 100)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
            # set_range_y(0, 100)
            ax.set_ylim(0, 100)                                          # (1)
        """},
        compare="chart",
        check=("limits", "bars"),
        choices=("None keeps that end where matplotlib put it (set_range_y(None, 100)); a flipped axis stays "
                 "flipped.",),
        also="Dates work as ends too. " + LOOK,
    ),
    Entry(
        word="draw_line_at_y",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="name", y="marks")
            chart.draw_line_at_y(50, labelled="pass mark")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.barplot(df, x="name", y="marks", errorbar=None, ax=ax)
            # draw_line_at_y(50, labelled="pass mark")
            ax.axhline(50, color="grey", linestyle="--", linewidth=1.5)  # (1)
            ax.text(1.01, 50, "pass mark", transform=ax.get_yaxis_transform(),
                    ha="left", va="center", color="grey", clip_on=False)  # (2)
        """},
        compare="chart",
        check=("lines", "texts", "bars"),
        choices=("a grey dashed line, 1.5 points wide, drawn above the bars and below the dots.",
                 "the label sits just outside the right edge, so it never covers a bar or a dot.",),
        also=LOOK,
    ),
    Entry(
        word="shade_between_y",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.shade_between_y(40, 60)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # shade_between_y(40, 60)
            ax.axhspan(40, 60, color="grey", alpha=0.2, linewidth=0,
                       zorder=0)                                         # (1)
        """},
        compare="chart",
        check=("bars", "dots", "limits"),
        choices=("a light band (alpha 0.2), behind everything else on the chart (zorder 0), so the data stay in "
                 "front of it.",),
        also="The band is a rectangle across the whole width: the test reads it among the bars. " + LOOK,
    ),
    Entry(
        word="use_log_scale_y",
        data="growth",
        ours="""
            chart = sdata.chart(sdata.get_example("growth"))
            chart.draw_lines(x="year", y="population", colour="country")
            chart.use_log_scale_y()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            # use_log_scale_y()
            ax.set_yscale("log")                                         # (1)
            sns.lineplot(df, x="year", y="population", hue="country", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("scales", "lines", "limits"),
        choices=("the scale is set before drawing, so the axis ranges are worked out on the log scale and later "
                 "ticks and ranges are not undone by it.",),
        also="simplydata stops with a plain message when a value is 0 or below, which a log scale cannot show. "
             + LOOK,
    ),
    Entry(
        word="draw_line_at_x",
        data="growth",
        ours="""
            chart = sdata.chart(sdata.get_example("growth"))
            chart.draw_lines(x="year", y="population", colour="country")
            chart.draw_line_at_x(2010, labelled="2010")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="year", y="population", hue="country", errorbar=None, ax=ax)
            # draw_line_at_x(2010, labelled="2010")
            ax.axvline(2010, color="grey", linestyle="--", linewidth=1.5)  # (1)
            ax.text(2010, 0.98, " 2010 ", transform=ax.get_xaxis_transform(),
                    rotation=90, ha="right", va="top", color="grey")    # (2)
        """},
        compare="chart",
        check=("lines", "texts", "limits"),
        choices=("a grey dashed line, 1.5 points wide.",
                 "the label stands up along the line, near the top, on its left side.",),
        also=LOOK,
    ),
    Entry(
        word="write_ticks_y_as",
        data="growth",
        ours="""
            chart = sdata.chart(sdata.get_example("growth"))
            chart.draw_lines(x="year", y="forest", colour="country")
            chart.write_ticks_y_as("percent")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            from matplotlib import ticker
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="year", y="forest", hue="country", errorbar=None, ax=ax)
            # write_ticks_y_as("percent")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))  # (1)
        """},
        compare="chart",
        check=("ticks", "lines"),
        choices=("the numbers are already percents (out of 100); out_of=1 is for shares, so 0.25 shows as 25 %.",),
        also="\"thousands\" writes 12,500 (StrMethodFormatter), \"scientific\" and \"plain\" use ScalarFormatter; a "
             "date axis takes how a date should look, such as \"Jan 2026\". " + LOOK,
    ),
    Entry(
        word="set_size",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="rain", colour="city")
            chart.set_size(width=17, height=8, unit="cm")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            # set_size(width=17, height=8, unit="cm")
            fig, ax = plt.subplots(figsize=(17 / 2.54, 8 / 2.54))       # (1)
            sns.lineplot(df, x="month", y="rain", hue="city", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("size", "lines"),
        choices=("matplotlib measures in inches, so centimetres are divided by 2.54 (millimetres by 25.4); in "
                 "pixels the saved picture has exactly that many pixels at any resolution.",),
        also="After set_size() a saved file is exactly that size, without trimming its edges. " + LOOK,
    ),
    Entry(
        word="write_note",
        data="growth",
        ours="""
            chart = sdata.chart(sdata.get_example("growth"))
            chart.draw_lines(x="year", y="population", colour="country")
            chart.write_note("Cherria grows fastest", x=2020, y=12)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="year", y="population", hue="country", errorbar=None, ax=ax)
            # write_note("Cherria grows fastest", x=2020, y=12)
            ax.annotate("Cherria grows fastest", xy=(2020, 12), xytext=(0, 4),
                        textcoords="offset points", ha="center", va="bottom",
                        bbox=dict(boxstyle="round,pad=0.2", fc="white",
                                  ec="none", alpha=0.85))                # (1)
        """},
        compare="chart",
        check=("texts", "lines", "limits"),
        choices=("the note sits just above the place, on a soft background in the chart's own colour, so it stays "
                 "readable over lines and bars.",),
        also="with_arrow=True moves the note 40 points towards the middle of the chart and points an arrow at the "
             "place; on a bar chart x can be the name under a bar. " + LOOK,
    ),
    Entry(
        word="draw_heatmap",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_heatmap(x="month", y="city", value="rain", with_numbers=True)
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            # draw_heatmap(x="month", y="city", value="rain", with_numbers=True)
            wide = df.pivot_table(index="city", columns="month", values="rain",
                                  aggfunc="mean", sort=False)            # (1)
            fig, ax = plt.subplots()
            sns.heatmap(wide, cmap="viridis", cbar=False, annot=True,
                        fmt="g", ax=ax)                                  # (2)
            ax.tick_params(axis="y", rotation=0)
            fig.colorbar(ax.collections[0], ax=ax, label="rain")
        """},
        compare="chart",
        check=("cells", "texts", "ticks", "tick_angles"),
        choices=("each cell is the average of its rows; the rows and columns keep the order they appear in (month "
                 "names in calendar order).",
                 "the viridis colours (safe for colour-blind readers), or blue to red around 0 when the numbers lie "
                 "on both sides of it; the numbers are written plainly, whole numbers without decimals.",),
        also="With no columns named every number column of the table is drawn; cluster=True puts similar rows and "
             "columns together (SciPy linkage, as seaborn clustermap). " + LOOK,
    ),
]

# ---------------------------------------------------------------- U-batch 2: several charts, a second y-axis, animation
ENTRIES += [
    Entry(
        word="draw_one_chart_for_each_group_in",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.draw_one_chart_for_each_group_in("class", per_row=3)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # draw_one_chart_for_each_group_in("class", per_row=3)
            fig = plt.figure(figsize=(13, 4.5), layout="constrained")   # (1)
            axes = fig.subplots(1, 3, sharex=True, sharey=True)          # (2)
            for ax, (name, rows) in zip(axes, df.groupby("class", sort=False)):
                sns.scatterplot(rows, x="hours", y="marks", ax=ax)
                ax.set_title(f"class = {name}")                          # (3)
        """},
        compare="chart",
        check=("every_panel", "panels", "size"),
        choices=("about 4 x 3.3 inches for each small chart (here 3 across, 1 down), unless set_size() says "
                 "otherwise.",
                 "the small charts share their axis ranges, so they can be compared at a glance; same_x=False or "
                 "same_y=False lets each choose its own.",
                 "each small chart is named by its group, in the order the groups appear in the table.",),
        also="down= and across= make a table of charts for two columns (fig.subplots(rows, columns)); seaborn's "
             "FacetGrid and relplot(col=) do the same job. " + LOOK,
    ),
    Entry(
        word="sdata.put_side_by_side",
        data="marks",
        ours="""
            marks = sdata.get_example("marks")
            a = sdata.chart(marks).draw_bars(x="class", y="marks").write_title_on_top("Average")
            b = sdata.chart(marks).draw_boxes(x="class", y="marks").write_title_on_top("Spread")
            sdata.put_side_by_side(a, b, same_y=True)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # put_side_by_side(a, b, same_y=True)
            fig = plt.figure(figsize=(12, 4.5), layout="constrained")   # (1)
            ax1, ax2 = (cell.add_subplot() for cell in fig.subfigures(1, 2))  # (2)
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax1)
            ax1.set_title("Average")
            sns.boxplot(df, x="class", y="marks", saturation=1, ax=ax2)
            ax2.set_title("Spread")
            ends = ax1.get_ylim() + ax2.get_ylim()
            for ax in (ax1, ax2):
                ax.set_ylim(min(ends), max(ends))                        # (3)
        """},
        compare="chart",
        check=("every_panel", "size", "limits"),
        choices=("each chart gets 3/4 of its own size (8 x 6 inches becomes 6 x 4.5), side by side.",
                 "each chart is drawn in a part of the figure of its own (a SubFigure), so its title, labels and "
                 "legend stay with it and never land on its neighbour.",
                 "same_y=True gives every chart the y range that holds all their data.",),
        also="with_letters=True writes A, B, C ... at the top left of each chart, as in papers. " + LOOK,
    ),
    Entry(
        word="sdata.put_one_above_other",
        data="weather",
        ours="""
            weather = sdata.get_example("weather")
            a = sdata.chart(weather).draw_lines(x="month", y="temperature", colour="city")
            b = sdata.chart(weather).draw_bars(x="month", y="rain", colour="city")
            sdata.put_one_above_other(a, b)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            # put_one_above_other(a, b)
            fig = plt.figure(figsize=(6, 9), layout="constrained")      # (1)
            top, bottom = (cell.add_subplot() for cell in fig.subfigures(2, 1))  # (2)
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=top)
            sns.barplot(df, x="month", y="rain", hue="city", errorbar=None, ax=bottom)
        """},
        compare="chart",
        check=("every_panel", "size"),
        choices=("each chart gets 3/4 of its own size (8 x 6 inches becomes 6 x 4.5), one above the other.",
                 "each chart is drawn in a part of the figure of its own (a SubFigure), so its title, labels and "
                 "legend stay with it.",),
        also="same_x=True gives them the same x range, which suits time series. " + LOOK,
    ),
    Entry(
        word="sdata.put_in_rows_and_columns",
        data="marks",
        ours="""
            marks = sdata.get_example("marks")
            a = sdata.chart(marks).draw_bars(x="class", y="marks")
            b = sdata.chart(marks).draw_histogram(x="marks")
            c = sdata.chart(marks).draw_dots(x="hours", y="marks")
            d = sdata.chart(marks).draw_boxes(x="subject", y="marks")
            page = sdata.put_in_rows_and_columns(a, b, c, d, per_row=2)
            page.write_title_on_top("Four ways to look at the marks")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # put_in_rows_and_columns(a, b, c, d, per_row=2), with a title on top
            fig = plt.figure(figsize=(12, 9.5), layout="constrained")   # (1)
            a, b, c, d = (cell.add_subplot() for cell in fig.subfigures(2, 2).flat)
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=a)
            sns.histplot(df, x="marks", bins=10, ax=b)
            b.set_ylabel("count")                                        # (2)
            sns.scatterplot(df, x="hours", y="marks", ax=c)
            sns.boxplot(df, x="subject", y="marks", saturation=1, ax=d)
            fig.suptitle("Four ways to look at the marks", fontweight="bold")  # (3)
        """},
        compare="chart",
        check=("every_panel", "size", "texts"),
        choices=("each chart gets 3/4 of its own size, in rows of per_row= charts, and a title adds half an inch.",
                 "each chart is drawn as it would be on its own: a histogram has 10 bins and its y label in small "
                 "letters (count).",
                 "the page's title goes over every chart, in bold and a little bigger than their own titles.",),
        also="Each chart sits in a SubFigure of its own, as in put_side_by_side(). " + LOOK,
    ),
    Entry(
        word="sdata.draw_all_pairs",
        data="marks",
        ours="""
            sdata.draw_all_pairs(sdata.get_example("marks"), colour="class")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df, cols = sdata.get_example("marks"), ["hours", "marks", "height"]
            # draw_all_pairs(df, colour="class")
            fig, axes = plt.subplots(3, 3, figsize=(8.7, 7.2), sharex="col", sharey="row")  # (1)
            for (i, y), (j, x) in [(a, b) for a in enumerate(cols) for b in enumerate(cols)]:
                if i == j:                                               # (2)
                    twin = axes[i, j].twinx()
                    sns.kdeplot(df, x=x, hue="class", fill=True, common_norm=False, legend=False, ax=twin)
                    twin.set_ylabel("")
                else:
                    sns.scatterplot(df, x=x, y=y, hue="class", s=28, linewidth=0, alpha=0.8,
                                    legend=False, ax=axes[i, j])        # (3)
                axes[i, j].set(xlabel=x if i == 2 else "", ylabel=y if j == 0 else "")
        """},
        compare="chart",
        check=("every_panel", "panels", "size"),
        choices=("every number column (here 3) against every other, about 2.4 inches a column, plus room for the "
                 "legend.",
                 "the diagonal shows each column on its own: a density curve for each group when colour= makes "
                 "groups (common_norm=False: every curve has area 1), a histogram without groups; it sits on a "
                 "second y-axis so the row keeps its own scale.",
                 "smaller, slightly see-through dots without rims, so crowded panels stay readable.",),
        also="One legend for the whole figure goes on the right (fig.legend). seaborn's pairplot() draws a similar "
             "figure with its own grid. " + LOOK,
    ),
    Entry(
        word="add_second_y",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature")
            chart.add_second_y("rain", drawn_as="bars", labelled="Rain (mm)")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="month", y="temperature", errorbar=None, ax=ax)
            # add_second_y("rain", drawn_as="bars", labelled="Rain (mm)")
            rain = df.groupby("month", sort=False)["rain"].mean()        # (1)
            twin = ax.twinx()
            twin.bar(range(len(rain)), rain, width=0.8, alpha=0.6, color="#E69F00")  # (2)
            twin.set_ylabel("Rain (mm)", color="#E69F00")
            ax.set_zorder(twin.get_zorder() + 1)                         # (3)
            ax.patch.set_visible(False)
        """},
        compare="chart",
        check=("every_panel", "panels", "lines"),
        choices=("one value for each name on the x-axis, the average of its rows (as the line under it), placed "
                 "above that name.",
                 "the new layer gets the first colour of the set that the chart does not use yet, and its axis, "
                 "label and tick numbers are written in that colour.",
                 "the first chart is kept in front of the new bars.",),
        also="One legend holds both layers, in the emptiest corner. drawn_as=\"lines\" or \"dots\" draws the second "
             "column as a line or dots instead. " + LOOK,
    ),
    Entry(
        word="animate",
        data="growth",
        ours="""
            chart = sdata.chart(sdata.get_example("growth"))
            chart.draw_bars(x="country", y="population")
            chart.set_range_y(0, 50)
            chart.animate(over="year")
        """,
        code={"matplotlib": """
            import tempfile
            import matplotlib.pyplot as plt
            import seaborn as sns
            from matplotlib.animation import PillowWriter
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            # animate(over="year"), then save("growth.gif"): one picture for each year
            writer = PillowWriter(fps=1 / 0.8)                           # (1)
            with writer.saving(fig, tempfile.gettempdir() + "/growth.gif", dpi=100):
                for year in sorted(df["year"].unique()):                 # (2)
                    ax.clear()
                    sns.barplot(df[df["year"] == year], x="country", y="population", errorbar=None, ax=ax)
                    ax.set(ylim=(0, 50), title=f"year: {year}")          # (3)
                    writer.grab_frame()
        """},
        compare="chart",
        check=("bars", "labels", "limits", "ticks"),
        choices=("0.8 seconds for each picture (seconds_per_frame=), saved as a .gif at 100 dots per inch.",
                 "one picture for each value, smallest first (month names in calendar order); keep=True keeps the "
                 "values before it in each picture.",
                 "every picture keeps the axis ranges of the chart with all the data, so the bars do not jump "
                 "about, and is named by its value.",),
        also="Shown as a still picture (in Jupyter or saved as .png) the chart is its last frame, which the test "
             "compares. " + LOOK,
    ),
    Entry(
        word="fit_formula",
        data="growth",
        ours="""
            chart = sdata.chart(sdata.get_example("growth"))
            chart.draw_dots(x="year", y="population", colour="country")
            chart.fit_formula("population = a * exp(b * (year - 2000))")
        """,
        code={"SciPy": """
            import matplotlib.pyplot as plt
            import numpy as np
            import seaborn as sns
            from scipy import optimize
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="year", y="population", hue="country", ax=ax)
            # fit_formula("population = a * exp(b * (year - 2000))")
            for country, rows in df.groupby("country", sort=False):
                (a, b), cov = optimize.curve_fit(lambda year, a, b: a * np.exp(b * (year - 2000)),
                                                 rows["year"], rows["population"], p0=[1, 1],  # (1)
                                                 method="lm", maxfev=20000, xtol=1e-12, ftol=1e-12)  # (2)
                xs = np.linspace(rows["year"].min(), rows["year"].max(), 200)
                ax.plot(xs, a * np.exp(b * (xs - 2000)))
        """},
        compare="chart",
        check=("lines", "dots"),
        tolerance=1e-7,
        choices=("every value to find starts at 1 unless start= says otherwise.",
                 "Levenberg-Marquardt, as R nls(), with tight stopping rules; between= limits switch to SciPy's "
                 "trust region method.",),
        also="Each colour group gets its own curve, over the range of its own dots, and the values found are "
             "printed once with their 95 % intervals. The curves agree to 7 digits: the search stops at a "
             "tolerance, not at an exact answer. " + LOOK,
    ),
]
