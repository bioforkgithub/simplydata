"""Chart words of the charts phase, batch 3 (approved by Manish on 2026-11-25): the same chart drawn with
matplotlib and seaborn. As in charts.py, the chart's data are compared, not its pixels. The web-page words draw
nothing new: the picture is drawn by matplotlib and copied into plotly (simplydata._web), so their entries say so."""

from . import Entry
from .charts import LOOK

_DOTS = '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
'''

_WEB = ("simplydata's own: the chart is drawn by matplotlib and seaborn, as for a picture, and what they drew (the "
        "numbers of get_numbers_drawn(), the words of get_text_drawn(), the scales of get_scales_drawn()) is copied "
        "into a plotly figure, which nothing works out again. ")


def _dots_ours(step):
    return f'''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.{step}
        '''


ENTRIES = [
    # ------------------------------------------------------------------ web pages (compare="none": a translation)
    Entry(word="show_in_web_page", ours=_dots_ours("show_in_web_page()"), compare="none",
          note=_WEB + "plotly then shows it: plotly.io.to_html(fig, include_plotlyjs=True) writes plotly.js into a file "
               "on this computer, which the browser opens (a notebook shows the same page below the cell); nothing "
               "is loaded from the internet."),
    Entry(word="show_when_pointing", ours=_dots_ours('show_when_pointing("name", "class")'), compare="none",
          note=_WEB + "The columns you name go into each mark's hover text (plotly's text and hovertemplate, the "
               "job of hover_data in plotly express); each dot's row is found by its x and y; all_lines=True is "
               "plotly's hovermode=\"x unified\"."),
    Entry(word="add_range_bar_x", ours='''
            chart = sdata.chart(sdata.get_example("visitors"))
            chart.draw_lines(x="month", y="visitors", colour="museum")
            chart.add_range_bar_x()
        ''', compare="none",
          note=_WEB + "The bar is plotly's range slider: fig.update_xaxes(rangeslider_visible=True)."),
    # ------------------------------------------------------------------ axes, scales, background
    Entry(
        word="break_between_y",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.break_between_y(5, 50)
        ''',
        code={"seaborn": '''
            import pandas as pd, matplotlib.pyplot as plt, seaborn as sns
            df = pd.read_csv("marks.csv")
            # break_between_y(5, 50): two panels sharing x                      (1)
            fig, (top, bottom) = plt.subplots(2, 1, sharex=True)
            for ax in (top, bottom):
                sns.barplot(df, x="class", y="marks", errorbar=None, ax=ax)
            bottom.set_ylim(bottom.get_ylim()[0], 5); top.set_ylim(50, top.get_ylim()[1])
            top.spines["bottom"].set_visible(False); bottom.spines["top"].set_visible(False)
            top.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
            top.set_xlabel(""); top.set_ylabel("")
            mark = dict(marker=[(-1, -0.5), (1, 0.5)], markersize=12, linestyle="none", color="k", clip_on=False)
            top.plot([0, 1], [0, 0], transform=top.transAxes, **mark)
            bottom.plot([0, 1], [1, 1], transform=bottom.transAxes, **mark)
        '''},
        compare="chart",
        check=("every_panel",),
        choices=("the matplotlib gallery's broken axis: the chart drawn twice, on two panels of the same height; "
                 "short slanted lines mark the break.",),
        also="simplydata prints a note to say in the caption what is left out. " + LOOK,
    ),
    Entry(
        word="use_scale_y",
        data="marks",
        ours=_dots_ours('use_scale_y("square root")'),
        code={"matplotlib": (_DOTS + '''
            # use_scale_y("square root")
            low, high = ax.get_ylim()
            ax.set_yscale("function", functions=(lambda v: np.sqrt(np.clip(v, 0, None)), np.square))
            ax.set_ylim(max(low, 0), high)
        ''').replace("import pandas as pd", "import numpy as np, pandas as pd")},
        compare="chart",
        check=("dots", "limits"),
        also="\"logit\" and \"asinh\" are matplotlib's own scales of those names; simplydata refuses values the scale "
             "cannot show (below 0 for a square root). " + LOOK,
    ),
    Entry(
        word="use_scale_x",
        data="marks",
        ours=_dots_ours('use_scale_x("asinh")'),
        code={"matplotlib": _DOTS + '''
            # use_scale_x("asinh")
            ax.set_xscale("asinh")
        '''},
        compare="chart",
        check=("dots", "scales", "limits"),
        also=LOOK,
    ),
    Entry(
        word="use_log_scale_y",
        option="through_zero=",
        data="marks",
        ours=_dots_ours("use_log_scale_y(through_zero=True)"),
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # use_log_scale_y(through_zero=True)
            ax.set_yscale("symlog")
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
        '''},
        compare="chart",
        check=("dots", "scales", "limits"),
        also="The scale is set before drawing, as for use_log_scale_y(). " + LOOK,
    ),
    Entry(
        word="use_background_colour",
        data="marks",
        ours=_dots_ours('use_background_colour("ivory")'),
        code={"matplotlib": _DOTS + '''
            # use_background_colour("ivory")
            ax.set_facecolor("ivory")
        '''},
        compare="chart",
        check=("dots", "background"),
        also=LOOK,
    ),
    # ------------------------------------------------------------------ marks
    Entry(
        word="draw_hexagon_bins",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_hexagon_bins(x="hours", y="height")
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_hexagon_bins(x="hours", y="height")
            hexagons = ax.hexbin(df["hours"], df["height"], gridsize=20, mincnt=1,   # (1)
                                 cmap="viridis", linewidths=0.2, edgecolors="face")
            fig.colorbar(hexagons, ax=ax, label="count")
            ax.set_xlabel("hours"); ax.set_ylabel("height")
        '''},
        compare="chart",
        check=("hexagons", "labels", "colour_bars"),
        choices=("about 20 hexagons across (gridsize=20); hexagons with no rows are not drawn (mincnt=1); viridis, as "
                 "for heat maps.",),
        also=LOOK,
    ),
    Entry(
        word="draw_side_histograms",
        option="drawn_as=",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.draw_side_histograms(drawn_as="density")
        ''',
        code={"seaborn": '''
            import pandas as pd, matplotlib.pyplot as plt, seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
            # draw_side_histograms(drawn_as="density")
            top = ax.inset_axes([0, 1.02, 1, 0.18], sharex=ax)
            right = ax.inset_axes([1.02, 0, 0.18, 1], sharey=ax)
            sns.kdeplot(x=df["hours"], ax=top, fill=True, alpha=0.8, linewidth=0)          # (1)
            sns.kdeplot(y=df["marks"], ax=right, fill=True, alpha=0.8, linewidth=0)
            top.set(xlabel="", ylabel=""); right.set(xlabel="", ylabel="")
        '''},
        compare="chart",
        check=("dots", "insets"),
        choices=("seaborn's density curve (Gaussian kernel, Scott's bandwidth) on each edge, filled; with colour "
                 "groups, one outline per group, each with its own area of 1.",),
        also="The edges have no frame and no numbers, as with the histograms. " + LOOK,
    ),
    Entry(
        word="draw_time_bars",
        ours='''
            chart = sdata.chart()
            chart.draw_time_bars(start=[1, 3, 6], end=[4, 7, 9], y=["plan", "build", "test"])
        ''',
        code={"matplotlib": '''
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            # draw_time_bars(start=[1, 3, 6], end=[4, 7, 9], y=["plan", "build", "test"])
            start, end = [1, 3, 6], [4, 7, 9]
            ax.barh(["plan", "build", "test"], [e - s for s, e in zip(start, end)], left=start,
                    height=0.8, linewidth=0)                                                    # (1)
            ax.invert_yaxis()                                                                   # (2)
        '''},
        compare="chart",
        check=("bars", "ticks"),
        choices=("bars 0.8 of a row high.",
                 "the first row of the table at the top, as in a plan.",),
        also="With colour= a column, each group gets its own colour and a legend (patterns too in black and white); "
             "dates work as numbers do. " + LOOK,
    ),
    Entry(
        word="draw_rectangle",
        data="marks",
        ours=_dots_ours("draw_rectangle(x_between=[4, 6], y_between=[60, 80])"),
        code={"matplotlib": _DOTS + '''
            # draw_rectangle(x_between=[4, 6], y_between=[60, 80])
            from matplotlib.patches import Rectangle
            ax.add_patch(Rectangle((4, 60), 2, 20, facecolor=(0, 0.447, 0.698, 0.25),   # (1)
                                   edgecolor="#0072B2", linewidth=1.5))
        '''},
        compare="chart",
        check=("bars", "dots", "limits"),
        choices=("filled see-through (a quarter of the colour), so the marks under it still show, with a solid "
                 "edge.",),
        also=LOOK,
    ),
    Entry(
        word="draw_circle",
        data="marks",
        ours=_dots_ours("draw_circle(centre=[5, 70], radius=1)"),
        code={"matplotlib": _DOTS + '''
            # draw_circle(centre=[5, 70], radius=1)
            from matplotlib.patches import Circle
            ax.add_patch(Circle((5, 70), 1, facecolor=(0, 0.447, 0.698, 0.25), edgecolor="#0072B2",
                                linewidth=1.5))
        '''},
        compare="chart",
        check=("shapes", "dots", "limits"),
        also="The radius is in the units of the axes, as matplotlib draws it. " + LOOK,
    ),
    Entry(
        word="draw_residual_dots",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_residual_dots(x="hours", y="marks")
        ''',
        code={"seaborn": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_residual_dots(x="hours", y="marks")
            sns.residplot(df, x="hours", y="marks", ax=ax)
            ax.set_ylabel("residual of marks")                                      # (1)
        '''},
        compare="chart",
        check=("dots", "lines", "labels"),
        choices=("the y-axis is named \"residual of\" the column, so it is not read as the column itself.",),
        also="seaborn fits the straight line by least squares and draws the dotted line at 0. " + LOOK,
    ),
    Entry(
        word="draw_event_lines",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_event_lines(x="hours", y="class")
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_event_lines(x="hours", y="class")
            groups = list(pd.unique(df["class"]))
            ax.eventplot([df.loc[df["class"] == g, "hours"] for g in groups],
                         lineoffsets=range(len(groups)), linelengths=0.8, linewidths=1.5)   # (1)
            ax.set_yticks(range(len(groups)), labels=groups)
        '''},
        compare="chart",
        check=("segments", "ticks"),
        choices=("one row of lines for each group, in the order they first appear; lines 0.8 of a row long.",),
        also=LOOK,
    ),
    Entry(
        word="draw_bars_3d",
        data="weather",
        ours='''
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_bars_3d(x="month", y="city", z="rain")
        ''',
        code={"matplotlib": '''
            import numpy as np, pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("weather.csv")
            fig = plt.figure(); ax = fig.add_subplot(projection="3d")
            # draw_bars_3d(x="month", y="city", z="rain")
            months, cities = list(pd.unique(df["month"])), list(pd.unique(df["city"]))  # (1)
            x = df["month"].map(months.index).to_numpy(float)
            y = df["city"].map(cities.index).to_numpy(float)
            ax.bar3d(x - 0.4, y - 0.4, 0, 0.8, 0.8, df["rain"], shade=True)            # (2)
            ax.set_xticks(range(len(months)), labels=months)
            ax.set_yticks(range(len(cities)), labels=cities)
        '''},
        compare="chart",
        check=("faces_3d",),
        choices=("names along an axis sit at 0, 1, 2 ... in the order they first appear.",
                 "each bar 0.8 of the smallest gap between two places wide and deep, standing on 0.",),
        also="simplydata prints a note that a heat map often shows the same numbers more plainly. " + LOOK,
    ),
]
