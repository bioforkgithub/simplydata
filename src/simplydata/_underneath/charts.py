"""Chart words: the same chart drawn with seaborn or matplotlib (and R's numbers for R words).

The test compares the chart's data (bars, dots, lines, labels, limits), not its pixels: simplydata's
paper look (fonts, colours, no top and right lines) is left out of the code on purpose.
"""

from . import Entry

LOOK = ("simplydata also gives the chart its paper look (fonts, colours, no top and right lines); that is left "
        "out here.")

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
            import pandas as pd
            df = pd.read_csv("marks.csv")
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
            import pandas as pd
            df = pd.read_csv("marks.csv")
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
            import pandas as pd
            df = pd.read_csv("marks.csv")
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
            import pandas as pd
            clinic = pd.read_csv("clinic.csv").dropna(subset=["crp", "infected"])
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
