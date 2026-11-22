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
                        annotation_clip=False, alpha=0.8,
                        fontsize=0.8 * plt.rcParams["font.size"])           # (2)
        """},
        compare="chart",
        check=("texts", "text_places", "bars", "labels"),
        choices=("the caption hangs 4 points under the x-axis label, so it moves down when the labels are turned or "
                 "grow; on a figure with several panels it is the figure's bottom line instead (fig.supxlabel).",
                 "in smaller letters (0.8 of the text size: 9.6 points in simplydata's paper look, where text is 12), "
                 "slightly faded, so it reads as a note, not a label.",),
        also="The size and fading of the letters are not compared. " + LOOK,
    ),
    Entry(
        word="use_font_size",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks", colour="subject")
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
                sns.barplot(df, x="class", y="marks", hue="subject", errorbar=None, ax=ax)
                ax.set_title("Big text")
        """},
        compare="chart",
        check=("font_sizes", "labels", "bars", "legend"),
        choices=("all the words grow together: in the normal paper look the sizes are 12 for text, 14 for the "
                 "title, 13 for the axis labels and 11 for tick labels and the legend, and use_font_size(18) "
                 "multiplies each by 18 / 12, so the title stays the biggest. In another style each grows by 18 over "
                 "that style's text size (18 / 15 in \"school\").",),
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
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.use_style("school")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            # use_style("school")
            school = {"font.size": 15, "axes.titlesize": 18, "axes.labelsize": 16,
                      "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 14,
                      "lines.linewidth": 3.0, "lines.markersize": 10,
                      "axes.linewidth": 1.5}                             # (1)
            with plt.rc_context(school):
                fig, ax = plt.subplots()
                sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("font_sizes", "line_styles", "lines", "legend"),
        choices=("\"school\" is bigger words and thicker lines, for a classroom screen; \"presentation\" is bigger "
                 "still, \"dark\" puts light words and brighter colours on a dark background, and \"paper\" is the "
                 "normal look.",),
        also="The style is a set of matplotlib settings used while the chart is drawn and saved, so it never "
             "changes your other charts. The marker size and the width of the axis lines are not compared. "
             + LOOK_BUT_FONTS,
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
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_lines(x="class", y="marks", colour="subject", with_dots=True)
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_lines(x="class", y="marks", colour="subject", with_dots=True)
            sns.lineplot(df, x="class", y="marks", hue="subject",
                         estimator="mean", errorbar=None,                # (1)
                         marker="o", ax=ax)
        """},
        compare="chart",
        check=("lines", "shapes", "labels", "ticks", "legend", "limits"),
        choices=("each point is the average of its rows (here 6 pupils), with no band around the line unless you "
                 "ask (error=); seaborn's own default shades a bootstrap 95 % interval.",),
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
            sns.boxplot(df, x="class", y="marks", color="#0072B2",      # (1)
                        saturation=1, ax=ax)                             # (2)
        """},
        compare="chart",
        check=("shapes", "shape_colours", "lines", "ticks", "labels", "limits"),
        choices=("without groups the boxes get simplydata's first colour (Okabe-Ito blue, safe for colour-blind "
                 "readers); colour= or use_colour() choose others.",
                 "the exact colour (saturation=1), not seaborn's slightly duller one.",),
        also="The whiskers reach the furthest value within 1.5 box lengths, as in seaborn and R's boxplot(); with "
             "colour= the boxes of one group stand a little apart. " + LOOK_BUT_COLOURS,
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
             "is drawn: the sideways spread of the swarm is not compared. The boxes get simplydata's first "
             "colour, so their lines have the same shade. " + LOOK,
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
                           color="#0072B2", saturation=1, ax=ax)         # (2)
        """},
        compare="chart",
        check=("shapes", "shape_colours", "lines", "ticks", "labels"),
        choices=("each violin stops at the smallest and the largest value (cut=0), so it never shows values that "
                 "cannot happen, such as marks below 0; seaborn's own default runs the curve on past them.",
                 "simplydata's first colour, exactly (saturation=1), not seaborn's slightly duller one.",),
        also="The width follows seaborn's kernel density estimate (Scott's rule); the small box inside shows the "
             "middle half of the values. " + LOOK_BUT_COLOURS,
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
                 "\"total\" is \"sum\", \"smallest\" and \"biggest\" are \"min\" and \"max\", \"standard "
                 "deviation\" is \"std\"; \"count\" counts the rows (seaborn countplot).",),
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
        check=("bars", "lines", "line_styles", "limits"),
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
        check=("texts", "text_places", "bars", "limits"),
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
            ax.axhline(50, color="grey", linestyle="--", linewidth=1.5, zorder=2.5)  # (1)
            ax.text(1.01, 50, "pass mark", transform=ax.get_yaxis_transform(),
                    ha="left", va="center", color="grey", clip_on=False,           # (2)
                    fontsize=plt.rcParams["legend.fontsize"])
        """},
        compare="chart",
        check=("lines", "line_styles", "texts", "text_places", "bars"),
        choices=("a grey dashed line, 1.5 points wide, drawn above the bars and below the dots (zorder 2.5).",
                 "the label sits just outside the right edge, so it never covers a bar or a dot, in the legend's "
                 "size of letters.",),
        also="The colour and the size of the letters are not compared. " + LOOK,
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
            sns.scatterplot(df, x="hours", y="marks", color="#0072B2", ax=ax)
            # shade_between_y(40, 60)
            ax.axhspan(40, 60, color="grey", alpha=0.2, linewidth=0,
                       zorder=0)                                         # (1)
        """},
        compare="chart",
        check=("bars", "colours", "dots", "limits"),
        choices=("a light grey band (alpha 0.2), behind everything else on the chart (zorder 0), so the data stay "
                 "in front of it.",),
        also="The band is a rectangle across the whole width: the test reads it, and its see-through grey, among "
             "the bars. The dots get simplydata's first colour, as draw_dots() gives them. " + LOOK_BUT_COLOURS,
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
            chart.draw_dots(x="year", y="population")
            chart.draw_line_at_x(2010, labelled="2010")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="year", y="population", ax=ax)
            # draw_line_at_x(2010, labelled="2010")
            ax.axvline(2010, color="grey", linestyle="--", linewidth=1.5, zorder=2.5)  # (1)
            ax.text(2010, 0.98, " 2010 ", transform=ax.get_xaxis_transform(), rotation=90,
                    ha="right", va="top", color="grey",                          # (2)
                    fontsize=plt.rcParams["legend.fontsize"],
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
        """},
        compare="chart",
        check=("lines", "line_styles", "texts", "text_places", "dots", "limits"),
        choices=("a grey dashed line, 1.5 points wide, in front of bars and behind dots (zorder 2.5).",
                 "the label stands up along the line, near the top, on its left side, on a soft box in the chart's "
                 "background colour so the line does not cross the words.",),
        also="The colour and the size of the letters are not compared. " + LOOK,
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
        check=("texts", "text_places", "lines", "limits"),
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
            chart.draw_heatmap(x="month", y="city", value="temperature", with_numbers=True)
        """,
        code={"seaborn": """
            import math
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            # draw_heatmap(x="month", y="city", value="temperature", with_numbers=True)
            wide = df.pivot_table(index="city", columns="month", values="temperature",
                                  aggfunc="mean", sort=False)            # (1)
            def plain(v):                                                # (2)
                t = str(int(v)) if v == int(v) else f"{v:.{max(0, min(3, 2 - math.floor(math.log10(abs(v)))))}f}"
                return t.rstrip("0").rstrip(".") if "." in t else t
            fig, ax = plt.subplots()
            sns.heatmap(wide, cmap="RdBu_r", center=0, cbar=False, annot=wide.map(plain).to_numpy(),
                        fmt="", ax=ax)                                   # (3)
            ax.tick_params(axis="y", rotation=0)
        """},
        compare="chart",
        check=("cells", "texts", "text_places", "ticks", "tick_angles"),
        choices=("each cell is the average of its rows; the rows and columns keep the order they appear in (month "
                 "names in calendar order).",
                 "the numbers are written plainly: whole numbers without decimals, others to about 3 significant "
                 "digits, never as 1.2e+02.",
                 "numbers on both sides of 0 get blue below and red above, with white at 0 (the scale goes equally "
                 "far both ways); otherwise the viridis colours, safe for colour-blind readers. use_colour_scale() "
                 "chooses others.",),
        also="A colour bar is added beside the cells (fig.colorbar). With no columns named every number column of the "
             "table is drawn; cluster=True puts similar rows and columns together (SciPy linkage, as seaborn "
             "clustermap). " + LOOK,
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
            sns.boxplot(df, x="class", y="marks", color="#0072B2", saturation=1, ax=ax2)
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
        also="with_letters=True writes A, B, C ... at the top left of each chart, as in papers. The boxes get "
             "simplydata's first colour, as draw_boxes() gives them; colours are not compared here. " + LOOK,
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
            sns.boxplot(df, x="subject", y="marks", color="#0072B2", saturation=1, ax=d)
            fig.suptitle("Four ways to look at the marks", fontweight="bold")  # (3)
        """},
        compare="chart",
        check=("every_panel", "size", "texts"),
        choices=("each chart gets 3/4 of its own size, in rows of per_row= charts, and a title adds half an inch.",
                 "each chart is drawn as it would be on its own: a histogram has 10 bins and its y label in small "
                 "letters (count).",
                 "the page's title goes over every chart, in bold and a little bigger than their own titles.",),
        also="Each chart sits in a SubFigure of its own, as in put_side_by_side(). Colours and the bold letters "
             "of the page's title are not compared. " + LOOK,
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
                    sns.scatterplot(df, x=x, y=y, hue="class", s=28, linewidth=0, alpha=0.8,  # (3)
                                    palette=["#0072B2", "#E69F00", "#009E73"], legend=False, ax=axes[i, j])
                axes[i, j].set(xlabel=x if i == 2 else "", ylabel=y if j == 0 else "")
        """},
        compare="chart",
        check=("every_panel", "panel_styles", "panels", "size"),
        choices=("every number column (here 3) against every other, about 2.4 inches a column, plus room for the "
                 "legend.",
                 "the diagonal shows each column on its own: a density curve for each group when colour= makes "
                 "groups (common_norm=False: every curve has area 1), a histogram without groups; it sits on a "
                 "second y-axis so the row keeps its own scale.",
                 "smaller, slightly see-through dots without rims, so crowded panels stay readable.",),
        also="The groups get simplydata's colours (Okabe-Ito), so the dots' colours can be compared. One legend "
             "for the whole figure goes on the right (fig.legend); it is not compared. seaborn's pairplot() draws a "
             "similar figure with its own grid. " + LOOK_BUT_COLOURS,
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
        check=("every_panel", "panel_styles", "panels", "lines"),
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
            ends = sns.barplot(df, x="country", y="population", errorbar=None, ax=ax).axis()  # (1)
            with (writer := PillowWriter(fps=1 / 0.8)).saving(fig, tempfile.gettempdir() + "/growth.gif", dpi=100):  # (2)
                for year in sorted(df["year"].unique()):                 # (3)
                    ax.clear()
                    sns.barplot(df[df["year"] == year], x="country", y="population", errorbar=None, ax=ax)
                    ax.set(xlim=ends[:2], ylim=ends[2:], title=f"year: {year}")
                    writer.grab_frame()
        """},
        compare="chart",
        check=("bars", "labels", "limits", "ticks"),
        choices=("every picture keeps the axis ranges of the chart with all the data, so the bars do not jump "
                 "about, and is named by its value.",
                 "0.8 seconds for each picture (seconds_per_frame=), saved as a .gif at 100 dots per inch.",
                 "one picture for each value, smallest first (month names in calendar order); keep=True keeps the "
                 "values before it in each picture.",),
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

# ---------------------------------------------------------------- U3 batch 5: more chart types
# The facts added for this batch (grid, fonts, polar_start, in_3d, segments, insets, colour_bars, ax_lines) see what
# the facts above could not: grid lines, fonts, where a round chart starts, 3D points, vlines and error bars, small
# charts inside a chart, colour bars and straight lines drawn right across a chart.
ENTRIES += [
    Entry(
        word="show",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.show()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
            # show()
            plt.show()
            ax
        """},
        compare="chart",
        check=("bars", "ticks", "labels"),
        also="simplydata draws the chart afresh and hands its own Figure to a pyplot window for the showing, so "
             "plt.show() shows this chart and no other. In Jupyter, VS Code and Spyder a chart appears without "
             "show(). The test compares the chart that is shown, not the window. " + LOOK,
    ),
    Entry(
        word="draw_area",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_area(x="month_number", y="temperature")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            # draw_area(x="month_number", y="temperature")
            mean = df.groupby("month_number")["temperature"].mean()     # (1)
            ax.fill_between(mean.index, mean, color="#0072B2", alpha=0.35,
                            linewidth=0)                                 # (2)
            ax.plot(mean.index, mean, color="#0072B2")
            ax.set(xlabel="month_number", ylabel="temperature")
        """},
        compare="chart",
        check=("lines", "shapes", "shape_colours", "labels"),
        choices=("several rows at the same x are averaged, as in draw_lines(): here the 3 cities of each month.",
                 "the space under the line is filled down to 0 in the same colour, see-through (alpha 0.35), so "
                 "areas of several groups show through each other.",),
        also="With colour= each group gets its own area; stacked=True piles them up (matplotlib stackplot, alpha "
             "0.85) so the top edge is the total. " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="draw_pie",
        data="fruit",
        ours="""
            chart = sdata.chart(sdata.get_example("fruit"))
            chart.draw_pie(labels="fruit", values="count")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            df = sdata.get_example("fruit")
            fig, ax = plt.subplots()
            # draw_pie(labels="fruit", values="count")
            sizes = df.groupby("fruit", sort=False)["count"].sum()       # (1)
            ax.pie(sizes, labels=sizes.index, autopct="%1.0f%%",         # (2)
                   colors=["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9"],
                   startangle=90, counterclock=False,                    # (3)
                   wedgeprops=dict(edgecolor="white", linewidth=1.5))
        """},
        compare="chart",
        check=("shapes", "shape_colours", "texts", "text_places"),
        choices=("one slice per label, the total of its values, in the order the labels first appear (without "
                 "values= each slice counts the rows).",
                 "each slice is named and shows its share in whole percents.",
                 "the first slice starts at 12 o'clock and the slices go round clockwise, like a clock; matplotlib's "
                 "own default starts at 3 o'clock and goes anticlockwise.",),
        also="Thin white edges keep the slices apart; the colours are simplydata's set (Okabe-Ito). " + LOOK,
    ),
    Entry(
        word="draw_polar",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_polar(angle="wind_direction", distance="wind_speed", colour="city")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            df = sdata.get_example("weather")
            fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
            # draw_polar(angle="wind_direction", distance="wind_speed", colour="city")
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)                                   # (1)
            colours = ["#0072B2", "#E69F00", "#009E73"]
            for (city, rows), c in zip(df.groupby("city", sort=False), colours):
                ax.scatter(np.deg2rad(rows["wind_direction"]), rows["wind_speed"],  # (2)
                           color=c, label=city, zorder=3)
            ax.legend(title="city", loc="upper left", bbox_to_anchor=(1.05, 1))  # (3)
        """},
        compare="chart",
        check=("polar_start", "dots", "dot_colour_groups", "legend", "legend_place"),
        choices=("a compass: 0 at the top (north) and round clockwise, because the column is named like a direction "
                 "(wind_direction, bearing, heading) or full_turn= is given; other angles start on the right and go "
                 "anticlockwise, the way maths measures them.",
                 "the angles are in degrees and are turned into radians for matplotlib (full_turn=24 reads hours, "
                 "full_turn=12 months).",
                 "the legend sits outside the circle, on its right.",),
        also="Each group gets its own colour, in the order the groups appear. " + LOOK,
    ),
    Entry(
        word="draw_contour",
        data="island",
        ours="""
            chart = sdata.chart(sdata.get_example("island"))
            chart.draw_contour(x="east", y="north", z="height")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            df = sdata.get_example("island")
            fig, ax = plt.subplots()
            # draw_contour(x="east", y="north", z="height")
            wide = df.groupby(["north", "east"])["height"].mean().unstack()   # (1)
            gx, gy = np.meshgrid(wide.columns, wide.index)
            bands = ax.contourf(gx, gy, wide.to_numpy(dtype=float), levels=10,
                                cmap="viridis")                          # (2)
            ax.contour(bands, colors="white", linewidths=0.5, alpha=0.6,
                       linestyles="solid")                               # (3)
            fig.colorbar(bands, ax=ax, label="height")
            ax.set(xlabel="east", ylabel="north")
        """},
        compare="chart",
        check=("shapes", "shape_colours", "labels", "colour_bars"),
        choices=("every east goes with every north here (a full grid), so the heights are drawn as they are; "
                 "scattered points are first joined onto a 100 x 100 grid with straight lines in between (SciPy "
                 "griddata, method=\"linear\").",
                 "about 10 bands, in the viridis colours (safe for colour-blind readers); use_colour_scale() "
                 "chooses others.",
                 "thin white lines between the bands, solid even below 0 (matplotlib dashes one-colour lines there).",),
        also="Several heights at one place are averaged. filled=False draws only the lines, with their heights "
             "written on them (clabel). The dashing of the lines is not compared. " + LOOK,
    ),
    Entry(
        word="draw_surface",
        data="island",
        ours="""
            chart = sdata.chart(sdata.get_example("island"))
            chart.draw_surface(x="east", y="north", z="height")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            df = sdata.get_example("island")
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            # draw_surface(x="east", y="north", z="height")
            wide = df.groupby(["north", "east"])["height"].mean().unstack()   # (1)
            gx, gy = np.meshgrid(wide.columns, wide.index)
            z = wide.to_numpy(dtype=float)
            surface = ax.plot_surface(gx, gy, z, cmap="viridis", vmin=z.min(), vmax=z.max(),
                                      linewidth=0, antialiased=True)
            fig.colorbar(surface, ax=ax, label="height", shrink=0.6, pad=0.1)
            ax.set(xlabel="east", ylabel="north", zlabel="height")
            ax
        """},
        compare="chart",
        check=("in_3d", "labels", "colour_bars"),
        choices=("a full grid (every east with every north) is drawn as it is; scattered points are first joined "
                 "onto a 100 x 100 grid (SciPy griddata, straight lines in between).",),
        also="Several heights at one place are averaged. The colours run through viridis from the lowest to the highest point; use_colour_scale() chooses "
             "others. The test compares the height behind each piece's colour, the z axis and the colour bar. "
             + LOOK,
    ),
    Entry(
        word="draw_dots_3d",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots_3d(x="hours", y="height", z="marks", colour="class")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            df = sdata.get_example("marks")
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            # draw_dots_3d(x="hours", y="height", z="marks", colour="class")
            colours = ["#0072B2", "#E69F00", "#009E73"]
            for (name, rows), c in zip(df.groupby("class", sort=False), colours):  # (1)
                ax.scatter(rows["hours"], rows["height"], rows["marks"], color=c,
                           depthshade=False, label=name)
            ax.legend(title="class")
            ax.set(xlabel="hours", ylabel="height", zlabel="marks")
            ax
        """},
        compare="chart",
        check=("in_3d", "dot_colour_groups", "legend", "labels"),
        choices=("words (or a number column with 8 values or fewer) give each group its own colour, in the order the "
                 "groups appear; a number column with more values gets a colour scale and a colour bar instead.",),
        also="depthshade=False keeps every dot its own colour; matplotlib's own default fades the dots further "
             "back. The fading is not compared. " + LOOK,
    ),
    Entry(
        word="draw_band",
        data="weather",
        ours="""
            table = sdata.table(sdata.get_example("weather"))
            table.add_column("lowest", "temperature - 4")
            table.add_column("highest", "temperature + 4")
            chart = table.start_chart()
            chart.draw_band(x="month", between=["lowest", "highest"], colour="city")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            df = sdata.get_example("weather")
            df["lowest"], df["highest"] = df["temperature"] - 4, df["temperature"] + 4
            fig, ax = plt.subplots()
            # draw_band(x="month", between=["lowest", "highest"], colour="city")
            colours = ["#0072B2", "#E69F00", "#009E73"]
            for (city, rows), c in zip(df.groupby("city", sort=False), colours):  # (1)
                ax.fill_between(rows["month"], rows["lowest"], rows["highest"], color=c,
                                alpha=0.25, linewidth=0, label=city)     # (2)
            ax.legend(title="city")
            ax.set_xlabel("month")
        """},
        compare="chart",
        check=("shapes", "shape_colours", "legend", "labels"),
        choices=("one band per group, in its group's colour and in the order the groups appear, each named in the "
                 "legend.",
                 "light bands (alpha 0.25, transparency=0.75) with no edge line, so lines drawn on top stay clear.",),
        also="An empty cell leaves a gap in the band rather than a made-up edge, and a low edge above the high one "
             "stops with a message. labelled= names a single band in the legend. " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="draw_map_of_empty_cells",
        data="made-up",
        ours="""
            chart = sdata.chart({"sales": [3.0, None, 5.0, 2.0], "shop": ["North", "  ", None, "East"]})
            chart.draw_map_of_empty_cells()
        """,
        code={"pandas": """
            import matplotlib.pyplot as plt
            import pandas as pd
            from matplotlib.colors import ListedColormap
            from matplotlib.patches import Patch
            df = pd.DataFrame({"sales": [3.0, None, 5.0, 2.0], "shop": ["North", "  ", None, "East"]})
            # draw_map_of_empty_cells()
            empty = df.isna() | df.map(lambda v: isinstance(v, str) and not v.strip())  # (1)
            fig, ax = plt.subplots()
            ax.imshow(empty.to_numpy(dtype=float), aspect="auto", interpolation="nearest", vmin=0, vmax=1,
                      cmap=ListedColormap(["#E3E3E3", "#D55E00"]), extent=(-0.5, 1.5, 4.5, 0.5))  # (2)
            ax.set_xticks([0, 1], labels=[f"{c}\\n{n} empty" for c, n in empty.sum().items()])  # (3)
            ax.set_ylabel("row (in table order)")
            ax.legend(handles=[Patch(color="#D55E00", label=f"empty ({empty.sum().sum()} cells)"),
                               Patch(color="#E3E3E3", label="filled")], loc="upper left", bbox_to_anchor=(1.01, 1))
        """},
        compare="chart",
        check=("cells", "limits", "ticks", "legend", "labels"),
        choices=("a cell is empty when it is missing or holds only spaces, as in the table words.",
                 "one strip per column and one line per row, the first row at the top; empty cells in vermilion on "
                 "light grey (Okabe-Ito, safe for colour-blind readers).",
                 "under each column, how many of its cells are empty.",),
        also="columns= shows only some columns; thin gaps in the background colour separate the strips. " + LOOK,
    ),
    Entry(
        word="sticks",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.sticks(x="month_number", y="rain", colour="city")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            # sticks(x="month_number", y="rain", colour="city")
            colours = ["#0072B2", "#E69F00", "#009E73"]
            for (city, rows), c in zip(df.groupby("city", sort=False), colours):
                ax.vlines(rows["month_number"], 0, rows["rain"], color=c, linewidth=1.5, zorder=2)  # (1)
                ax.plot(rows["month_number"], rows["rain"], "o", color=c, markersize=5, zorder=3, label=city)
            ax.axhline(0, color="black", linewidth=0.8, zorder=1)                # (2)
            ax.legend(title="city")
            ax.set(xlabel="month_number", ylabel="rain")
        """},
        compare="chart",
        check=("segments", "lines", "legend", "labels"),
        choices=("each value is a thin stick (1.5 points) from 0, with a small dot on top; thickness= sets the width.",
                 "a thin line marks 0, behind the sticks, so values below 0 hang down from it.",),
        also="matplotlib's stem() draws the same kind of chart. " + LOOK,
    ),
    Entry(
        word="draw_error_bars",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="class", y="marks")
            chart.draw_error_bars()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="class", y="marks", ax=ax)
            # draw_error_bars(): the standard deviation
            summary = df.groupby("class", sort=False)["marks"].agg(["mean", "std"])  # (1)
            ax.errorbar(summary.index, summary["mean"], yerr=summary["std"], fmt="_",  # (2)
                        markersize=16, markeredgewidth=2, capsize=4, elinewidth=1.5,
                        capthick=1.5, zorder=3)
        """},
        compare="chart",
        check=("segments", "lines", "dots"),
        choices=("the standard deviation with n - 1 (pandas std), empty cells skipped; \"standard error\" divides it "
                 "by the square root of n, \"confidence interval\" is the t interval of the mean.",
                 "on dots a short wide dash marks each average, and the bars end in caps.",),
        also="A line is printed saying which error was drawn. With colour groups the bars (with their lines and "
             "dots) move a little apart so they do not hide each other; dodge=False keeps them on the true x. "
             + LOOK,
    ),
    Entry(
        word="fit_curve",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_dots(x="month_number", y="temperature")
            chart.fit_curve()
        """,
        code={"NumPy": """
            import matplotlib.pyplot as plt
            import numpy as np
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="month_number", y="temperature", ax=ax)
            # fit_curve()
            curve = np.polynomial.Polynomial.fit(df["month_number"], df["temperature"],
                                                 deg=2)                  # (1)
            xs = np.linspace(df["month_number"].min(), df["month_number"].max(), 200)  # (2)
            ax.plot(xs, curve(xs))
        """},
        compare="chart",
        check=("lines", "dots"),
        tolerance=1e-8,
        choices=("a curve with one bend (degree 2) unless of_degree= says otherwise, fitted by least squares on the "
                 "powers of x mapped onto -1 to 1 (as NumPy Polynomial.fit and table.fit_curve), which keeps big x "
                 "values accurate.",
                 "the curve is drawn only over the range of x in the data, never past it.",),
        also="Each colour group gets its own curve; show_equation=True writes the equation and R squared. " + LOOK,
    ),
]

# ---------------------------------------------------------------- U3 batch 5: curves, counts and lines on a chart
ENTRIES += [
    Entry(
        word="fit_distribution",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_histogram(x="marks")
            chart.fit_distribution("normal")
        """,
        code={"SciPy": """
            import matplotlib.pyplot as plt
            import numpy as np
            import seaborn as sns
            from scipy import stats
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.histplot(df, x="marks", bins=10, ax=ax)
            # fit_distribution("normal")
            average, spread = stats.norm.fit(df["marks"].dropna())          # (1)
            xs = np.linspace(*ax.dataLim.intervalx, 200)                     # (2)
            width = ax.patches[0].get_width()
            ax.plot(xs, stats.norm.pdf(xs, average, spread) * len(df) * width)  # (3)
        """},
        compare="chart",
        check=("lines", "bars"),
        choices=("the values are found by maximum likelihood, as R MASS::fitdistr(): for the normal distribution "
                 "the standard deviation divides by n, not n - 1. They are printed once.",
                 "the curve runs over the x range of the histogram, at 200 points.",
                 "over a histogram of counts the curve is scaled to the bars: density x number of values x bar width "
                 "(x 100 x bar width for percents; a density histogram needs no scaling).",),
        also="Each colour group gets its own curve; distribution= takes any name of sdata.distribution, such as "
             "\"gamma\" or \"lognormal\". " + LOOK,
    ),
    Entry(
        word="draw_curve",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_histogram(x="marks")
            chart.draw_curve(sdata.distribution("normal", average=60, standard_deviation=15))
        """,
        code={"SciPy": """
            import matplotlib.pyplot as plt
            import numpy as np
            import seaborn as sns
            from scipy import stats
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.histplot(df, x="marks", bins=10, ax=ax)
            # draw_curve(the normal distribution with average 60 and standard deviation 15)
            xs = np.linspace(*ax.dataLim.intervalx, 200)                     # (1)
            width = ax.patches[0].get_width()
            ax.plot(xs, stats.norm.pdf(xs, 60, 15) * df["marks"].count() * width,  # (2)
                    color="black", linewidth=2, zorder=3)
        """},
        compare="chart",
        check=("lines", "line_styles", "bars"),
        choices=("the curve runs over the x range of what is drawn (between= sets it), at 200 points (steps=).",
                 "over a histogram of counts the density is scaled to the bars (x number of values x bar width), and "
                 "a note says so.",),
        also="A formula works too: chart.draw_curve(\"y = 100 * exp(-0.3 * x)\", between=[0, 10]). Whole-number "
             "distributions (binomial, poisson ...) are drawn as the chance of each value; show=\"cumulative\" draws "
             "the chance at or below x. " + LOOK,
    ),
    Entry(
        word="draw_density",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_density(x="marks", colour="class")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_density(x="marks", colour="class")
            sns.kdeplot(df, x="marks", hue="class", common_norm=False,       # (1)
                        palette=["#0072B2", "#E69F00", "#009E73"], ax=ax)
        """},
        compare="chart",
        check=("lines", "colours", "legend"),
        choices=("each group's curve has an area of 1 on its own (common_norm=False), so a small group is not "
                 "squashed flat; seaborn's own default shares one area between all the groups.",),
        also="The curve is seaborn's kernel density estimate (Scott's rule for the width). " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="draw_count_bars",
        data="fruit",
        ours="""
            chart = sdata.chart(sdata.get_example("fruit"))
            chart.draw_count_bars(x="fruit", colour="shop")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("fruit")
            fig, ax = plt.subplots()
            # draw_count_bars(x="fruit", colour="shop")
            sns.countplot(df, x="fruit", hue="shop", palette=["#0072B2", "#E69F00"],
                          saturation=1, ax=ax)                               # (1)
        """},
        compare="chart",
        check=("bars", "colours", "legend", "ticks"),
        choices=("the exact colours (saturation=1), not seaborn's slightly duller ones.",),
        also="Each bar counts the rows of its group; sideways=True lays the bars down. " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="draw_side_histograms",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.draw_side_histograms()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # draw_side_histograms()
            top = ax.inset_axes([0, 1.02, 1, 0.18], sharex=ax)               # (1)
            right = ax.inset_axes([1.02, 0, 0.18, 1], sharey=ax)
            for side, column, way in ((top, "hours", "vertical"), (right, "marks", "horizontal")):
                side.hist(df[column], bins=np.histogram_bin_edges(df[column], bins="auto"),  # (2)
                          orientation=way, histtype="stepfilled", alpha=0.8, linewidth=0)
        """},
        compare="chart",
        check=("insets", "dots"),
        choices=("two thin histograms just outside the chart, along the top (x) and the right (y), sharing the "
                 "chart's axes so each bar lines up with its dots.",
                 "the bins follow NumPy's \"auto\" rule (at most 50); with colour groups each group is an outline, so "
                 "they stay readable where they overlap.",),
        also="seaborn's jointplot draws a similar figure on a grid of its own. The colours are not compared. " + LOOK,
    ),
    Entry(
        word="draw_cumulative_share",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_cumulative_share(x="marks", colour="class")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            # draw_cumulative_share(x="marks", colour="class")
            sns.ecdfplot(df, x="marks", hue="class",
                         palette=["#0072B2", "#E69F00", "#009E73"], ax=ax)
            ax.set_ylabel("share at or below")                               # (1)
        """},
        compare="chart",
        check=("lines", "labels", "legend"),
        choices=("the y-axis is named in words, \"share at or below\", not seaborn's \"Proportion\".",),
        also="Each group's line climbs from 0 to 1 on its own, so groups of any size compare directly. "
             + LOOK,
    ),
    Entry(
        word="draw_line_with_slope",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.draw_line_with_slope(10, labelled="10 marks an hour")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # draw_line_with_slope(10, labelled="10 marks an hour")
            line = ax.axline((0, 0), slope=10, color="grey", linestyle="--",     # (1)
                             linewidth=1.5, zorder=2.5)
            ax.legend([line], ["10 marks an hour"])                          # (2)
        """},
        compare="chart",
        check=("ax_lines", "line_styles", "legend", "dots"),
        choices=("through 0, 0 unless through= or intercept= says otherwise, right across the chart: a grey dashed "
                 "line, 1.5 points wide, above bars and below dots (zorder 2.5).",
                 "labelled= names the line in the legend, after any groups already there.",),
        also="Ordinary axes only: on a log scale a straight line would bend, so simplydata stops with a message. "
             + LOOK,
    ),
    Entry(
        word="shade_between_x",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month_number", y="temperature", colour="city")
            chart.shade_between_x(6, 8)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="month_number", y="temperature", hue="city", errorbar=None,
                         palette=["#0072B2", "#E69F00", "#009E73"], ax=ax)
            # shade_between_x(6, 8)
            ax.axvspan(6, 8, color="grey", alpha=0.2, linewidth=0, zorder=0)    # (1)
        """},
        compare="chart",
        check=("bars", "colours", "lines", "limits"),
        choices=("a light grey band (alpha 0.2) from the bottom of the chart to the top, between the two x values.",),
        also="The band is drawn behind everything else (zorder 0), so the data stay in front of it; the drawing "
             "order is not compared. The two ends may come in either order. The band is a rectangle: the test reads it, and its see-through "
             "grey, among the bars. " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="write_names_on_dots",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.keep_rows_where("class", is_equal_to="A")
            chart = table.start_chart()
            chart.draw_dots(x="hours", y="marks")
            chart.write_names_on_dots("name")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            df = df[(df["subject"] == "Maths") & (df["class"] == "A")]
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # write_names_on_dots("name"): the side of each name is what simplydata's search found
            left = {"Chen", "Dina"}                                          # (1)
            for name, x, y in zip(df["name"], df["hours"], df["marks"]):
                side = -1 if name in left else 1
                ax.annotate(name, xy=(x, y), xytext=(5.5 * side, 0), textcoords="offset points",
                            ha="left" if side > 0 else "right", va="center", zorder=4,
                            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))  # (2)
        """},
        compare="chart",
        check=("text_places", "texts", "dots"),
        choices=("each name goes just right of its dot (2 points past the dot's edge: 5.5 points from its middle in "
                 "the paper look); where it would cover another name or dot, or leave the chart, it tries left, "
                 "above, below and then the corners. Here Chen (at the right edge) and Dina (next to Ben's name) go "
                 "left. A name with no free place is left out, and a line says how many.",
                 "each name sits on a soft background in the chart's own colour, so it stays readable over lines.",),
        also="The search for a free place is simplydata's own; matplotlib only writes each name where it is told. "
             "The size of the letters is not compared. " + LOOK,
    ),
    Entry(
        word="use_font",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.use_font("DejaVu Serif")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # use_font("DejaVu Serif")
            with plt.rc_context({"font.family": "DejaVu Serif"}):            # (1)
                fig, ax = plt.subplots()
                sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("fonts", "labels", "bars"),
        choices=("the font is matplotlib's font.family for every word of the chart, used while it is drawn and saved, "
                 "so your other charts keep theirs.",),
        also="The name is checked against the fonts installed on your computer (any capitals), and a misspelt name "
             "gets a list of close ones; \"serif\", \"sans-serif\" and \"monospace\" work everywhere. " + LOOK,
    ),
    Entry(
        word="set_range_x",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.set_range_x(0, None)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # set_range_x(0, None)
            ax.set_xlim(0, None)                                             # (1)
        """},
        compare="chart",
        check=("limits", "dots"),
        choices=("None keeps that end where matplotlib put it; a flipped axis stays flipped.",),
        also="Dates work as ends too. " + LOOK,
    ),
    Entry(
        word="use_log_scale_x",
        data="growth",
        ours="""
            chart = sdata.chart(sdata.get_example("growth"))
            chart.draw_dots(x="population", y="forest", colour="country")
            chart.use_log_scale_x()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("growth")
            fig, ax = plt.subplots()
            # use_log_scale_x()
            ax.set_xscale("log")
            sns.scatterplot(df, x="population", y="forest", hue="country", ax=ax)
        """},
        compare="chart",
        check=("scales", "dots", "limits"),
        also="The scale is set before drawing, as in use_log_scale_y(), so later ticks and ranges are not undone by "
             "it. simplydata stops with a plain message when a value is 0 or below, which a log scale cannot show. "
             + LOOK,
    ),
    Entry(
        word="put_ticks_x",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.put_ticks_x("A", "C")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
            # put_ticks_x("A", "C")
            ax.set_xticks([0, 2], labels=["A", "C"])                         # (1)
        """},
        compare="chart",
        check=("ticks", "tick_places", "bars", "limits"),
        choices=("a name is looked up among the names under the bars, which seaborn puts at 0, 1, 2 ..., and keeps "
                 "its name; numbers are used as they are.",),
        also="labels= writes your own words; every=5 (or every=\"month\" on dates) and how_many=5 use matplotlib's "
             "MultipleLocator, the date locators and MaxNLocator. " + LOOK,
    ),
    Entry(
        word="put_ticks_y",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.put_ticks_y(0, 25, 50, 75)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
            # put_ticks_y(0, 25, 50, 75)
            ax.set_yticks([0, 25, 50, 75])
        """},
        compare="chart",
        check=("ticks", "tick_places", "bars", "limits"),
        also="labels= writes your own words at the ticks; every=10 and how_many=5 use matplotlib's MultipleLocator "
             "and MaxNLocator (how_many=5 asks for at most 4 gaps), whole_numbers=True MaxNLocator(integer=True). "
             + LOOK,
    ),
]

# ---------------------------------------------------------------- U3 batch 5: axes, grids, legends, order, zoom, forest
ENTRIES += [
    Entry(
        word="rotate_labels_y",
        data="fruit",
        ours="""
            chart = sdata.chart(sdata.get_example("fruit"))
            chart.draw_bars(x="fruit", y="count", sideways=True)
            chart.rotate_labels_y(30)
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("fruit")
            fig, ax = plt.subplots()
            sns.barplot(df, x="count", y="fruit", orient="h", errorbar=None, ax=ax)
            # rotate_labels_y: 30 degrees
            for label in ax.get_yticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment("right")
                label.set_verticalalignment("center")
                label.set_rotation_mode("anchor")                        # (1)
        """},
        compare="chart",
        check=("tick_angles", "ticks", "bars"),
        choices=("each name turns about its right end (rotation mode \"anchor\"), the end next to the axis, so it "
                 "stays beside its own bar; matplotlib's own default turns it about its middle.",),
        also="It runs after put_ticks_y(), so new tick labels are turned too. " + LOOK,
    ),
    Entry(
        word="write_ticks_x_as",
        data="shop",
        ours="""
            chart = sdata.chart(sdata.get_example("shop"))
            chart.draw_dots(x="sales", y="customers")
            chart.write_ticks_x_as("thousands")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            from matplotlib import ticker
            df = sdata.get_example("shop")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="sales", y="customers", ax=ax)
            # write_ticks_x_as("thousands")
            ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))  # (1)
        """},
        compare="chart",
        check=("ticks", "dots"),
        choices=("a comma between the thousands and no decimals unless with_decimals= asks (1,000, not 1000.0).",),
        also="\"percent\" uses PercentFormatter, \"scientific\" and \"plain\" ScalarFormatter; on a date axis you "
             "write how a date should look, such as \"Jan 2026\" (DateFormatter). " + LOOK,
    ),
    Entry(
        word="flip_x",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.flip_x()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # flip_x()
            ax.invert_xaxis()
        """},
        compare="chart",
        check=("limits", "dots"),
        also="The axis is turned round only if it is not turned already, so saying it twice keeps it flipped; "
             "set_range_x() afterwards keeps the flip. " + LOOK,
    ),
    Entry(
        word="flip_y",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.flip_y()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # flip_y()
            ax.invert_yaxis()
        """},
        compare="chart",
        check=("limits", "dots"),
        also="Handy for depth, which grows downwards. The axis is turned round only if it is not turned already; "
             "set_range_y() afterwards keeps the flip. " + LOOK,
    ),
    Entry(
        word="use_colour_scale",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_heatmap(x="month", y="city", value="rain")
            chart.use_colour_scale("magma")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            wide = df.pivot_table(index="city", columns="month", values="rain", aggfunc="mean", sort=False)
            fig, ax = plt.subplots()
            # use_colour_scale("magma")
            sns.heatmap(wide, cmap="magma", vmin=wide.min().min(), vmax=wide.max().max(),  # (1)
                        cbar=False, ax=ax)
            ax.tick_params(axis="y", rotation=0)
        """},
        compare="chart",
        check=("cells", "ticks"),
        choices=("the colours run from the smallest value to the biggest; between=[low, high] fixes the ends (values "
                 "beyond get the end colours), log=True spreads them on a log scale and steps= cuts the scale into "
                 "bands (LogNorm, BoundaryNorm). A two-sided scale such as \"blue to red\" with middle=0 goes "
                 "equally far on both sides.",),
        also="Plain names (\"blue to red\", \"greens\") and any matplotlib or seaborn colour map name work, and two or "
             "more colours make your own (LinearSegmentedColormap). A rainbow map gets a note that it misleads. "
             + LOOK,
    ),
    Entry(
        word="show_grid",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.show_grid()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # show_grid()
            ax.grid(True, axis="both")                                       # (1)
        """},
        compare="chart",
        check=("grid", "dots"),
        choices=("lines in both directions; simplydata's normal paper look draws only the lines across the chart, "
                 "from the y-axis.",),
        also="The grid is a matplotlib setting (axes.grid) used while the chart is drawn and saved. " + LOOK,
    ),
    Entry(
        word="hide_grid",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.hide_grid()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # hide_grid()
            ax.grid(False)
        """},
        compare="chart",
        check=("grid", "dots"),
        also="simplydata's paper look normally draws light lines across the chart from the y-axis; hide_grid() "
             "removes them (matplotlib's own default has none). " + LOOK,
    ),
    Entry(
        word="put_legend_at_top",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.write_title_on_top("Temperature")
            chart.put_legend_at_top()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            from matplotlib.patches import Rectangle
            df = sdata.get_example("weather")
            fig, ax = plt.subplots(layout="constrained")
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
            # put_legend_at_top(), on a chart with the title "Temperature"
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            blank = Rectangle((0, 0), 1, 1, visible=False)
            fig.legend([blank] + handles, ["city:"] + labels, title="Temperature",  # (1)
                       loc="outside upper center", ncols=4)              # (2)
        """},
        compare="chart",
        check=("legend_place", "labels", "lines"),
        choices=("the chart's title becomes the legend's heading, so the two never sit on top of each other, and the "
                 "group name moves to the front of the row.",
                 "one row of entries (up to 6 in a row) above the chart, outside it, so it covers no data.",),
        also="Entries from every panel and from a second y-axis are gathered into this one legend. " + LOOK,
    ),
    Entry(
        word="put_legend_on_right",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.put_legend_on_right()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots(layout="constrained")
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
            # put_legend_on_right()
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            fig.legend(handles, labels, title="city",
                       loc="outside center right")                       # (1)
        """},
        compare="chart",
        check=("legend_place", "lines"),
        choices=("outside the chart on the right, so it covers no data; on a figure with several panels one legend "
                 "holds the entries of them all.",),
        also=LOOK,
    ),
    Entry(
        word="show_legend",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.hide_legend()
            chart.show_legend()
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("weather")
            fig, ax = plt.subplots()
            # hide_legend(), then show_legend(): the legend seaborn draws, in its usual place
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("legend_place", "legend", "lines"),
        also="show_legend() takes back hide_legend() and any put_legend_... word, so the legend is the one drawn "
             "with the chart. A legend appears only when colour= (or shape=) makes groups. " + LOOK,
    ),
    Entry(
        word="label_legend",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks", colour="class")
            chart.label_legend("Class")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", hue="class", ax=ax)
            # label_legend("Class")
            ax.get_legend().set_title("Class")                               # (1)
        """},
        compare="chart",
        check=("legend", "dots"),
        choices=("the legend of every panel (and of a second y-axis) gets the name, and a legend moved outside by "
                 "put_legend_... keeps it; label_legend(\"\") leaves the name out.",),
        also="Without it the legend is named after the colour= column, as seaborn names it. " + LOOK,
    ),
    Entry(
        word="label_colour_bar",
        data="island",
        ours="""
            chart = sdata.chart(sdata.get_example("island"))
            chart.draw_contour(x="east", y="north", z="height")
            chart.label_colour_bar("Height (m)")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            df = sdata.get_example("island")
            wide = df.groupby(["north", "east"])["height"].mean().unstack()
            gx, gy = np.meshgrid(wide.columns, wide.index)
            fig, ax = plt.subplots()
            bands = ax.contourf(gx, gy, wide.to_numpy(dtype=float), levels=10, cmap="viridis")
            bar = fig.colorbar(bands, ax=ax, label="height")
            # label_colour_bar("Height (m)")
            bar.set_label("Height (m)")
        """},
        compare="chart",
        check=("colour_bars",),
        also="Without it the colour bar is named after the z= (or value=) column. It works on heatmaps, contour maps, "
             "surfaces and dots coloured by a number column. " + LOOK,
    ),
    Entry(
        word="order_y",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks", sideways=True)
            chart.order_y("C", "B", "A")
        """,
        code={"pandas": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # order_y("C", "B", "A")
            place = {"C": 0, "B": 1, "A": 2}
            df = df.sort_values("class", key=lambda s: s.map(place),
                                kind="stable")                           # (1)
            fig, ax = plt.subplots()
            sns.barplot(df, x="marks", y="class", orient="h", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("ticks", "tick_places", "bars"),
        choices=("the rows are put in that order with a stable sort, and seaborn draws the groups in the order they "
                 "appear, the first at the top; groups left out come after the ones named.",),
        also="biggest_first=True orders the groups by what the chart shows; it works for sideways bars, sideways "
             "boxes and heatmap rows. " + LOOK,
    ),
    Entry(
        word="order_legend",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks", colour="subject")
            chart.order_legend("Science", "Maths", "English")
        """,
        code={"pandas": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            # order_legend("Science", "Maths", "English")
            place = {"Science": 0, "Maths": 1, "English": 2}
            df = df.sort_values("subject", key=lambda s: s.map(place), kind="stable")  # (1)
            fig, ax = plt.subplots()
            sns.barplot(df, x="class", y="marks", hue="subject", errorbar=None, saturation=1,
                        palette=["#0072B2", "#E69F00", "#009E73"], ax=ax)  # (2)
        """},
        compare="chart",
        check=("legend", "colours", "bars"),
        choices=("the rows are put in that order with a stable sort, so the legend, the colours and the bars side by "
                 "side all follow it; groups left out come after the ones named.",
                 "the first group named gets the first colour.",),
        also="The slices of a pie follow it too. seaborn's hue_order= does the same for one call. " + LOOK_BUT_COLOURS,
    ),
    Entry(
        word="add_zoom_box",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.add_zoom_box(x_between=[2, 4], y_between=[40, 60])
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = sdata.get_example("marks")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # add_zoom_box(x_between=[2, 4], y_between=[40, 60])
            box = ax.inset_axes([0.58, 0.56, 0.39, 0.4])                     # (1)
            sns.scatterplot(df, x="hours", y="marks", ax=box)                # (2)
            box.set(xlim=(2, 4), ylim=(40, 60), xlabel="", ylabel="")
            box.set_zorder(5)
            ax.indicate_inset_zoom(box, edgecolor="black")
        """},
        compare="chart",
        check=("insets", "dots"),
        choices=("the box sits in the top right corner (where= chooses another), 0.39 of the chart wide and 0.4 high.",
                 "the chart's own drawing steps run again inside the box, so it shows exactly what the chart shows, "
                 "without its legend and axis labels.",),
        also="Lines join the box to the part it shows (indicate_inset_zoom); the box sits above the chart's lines "
             "and legend. Its smaller tick labels are not compared. " + LOOK,
    ),
    Entry(
        word="forest_plot",
        data="made-up",
        ours="""
            results = sdata.chart({"study": ["A", "B", "C"], "odds ratio": [0.8, 1.5, 1.1],
                                   "odds ratio 95 % CI low": [0.5, 1.1, 0.7], "odds ratio 95 % CI high": [1.3, 2.0, 1.7]})
            results.forest_plot(x="odds ratio", y="study")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            df = {"study": ["A", "B", "C"], "odds ratio": np.array([0.8, 1.5, 1.1]),
                  "low": np.array([0.5, 1.1, 0.7]), "high": np.array([1.3, 2.0, 1.7])}
            fig, ax = plt.subplots()
            # forest_plot(x="odds ratio", y="study")
            where = np.arange(3)[::-1]                                       # (1)
            est = df["odds ratio"]
            ax.errorbar(est, where, xerr=[est - df["low"], df["high"] - est], fmt="o", capsize=3,
                        elinewidth=1.5, markersize=6)
            ax.axvline(1, color="grey", linestyle="--", linewidth=1)         # (2)
            ax.set_yticks(where, labels=df["study"])
            ax.set_xscale("log")
            ax.set_xlabel("odds ratio, with its 95 % confidence interval (the line: 1, no effect)")  # (3)
        """},
        compare="chart",
        check=("lines", "segments", "ticks", "tick_places", "scales", "labels"),
        choices=("the first row at the top, as in a table.",
                 "a ratio (the column, or every row's name, says \"ratio\") gets a log scale and a dashed line at 1, "
                 "no effect; other results a plain scale with the line at 0. log_scale= and line_at= choose.",
                 "the x label names the interval's level and the line.",),
        also="It reads the columns \"<x> 95 % CI low\" and \"<x> 95 % CI high\" (any level) of a result table, such "
             "as compare_each_pair_of's. On the result of combine_studies the studies are squares sized by weight= "
             "and the combined effects diamonds. " + LOOK,
    ),
]
