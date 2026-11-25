"""Chart words and options of the charts phase, batch 2 (approved by Manish on 2026-11-25): the same chart drawn
with matplotlib, seaborn and NumPy. As in charts.py, the chart's data are compared, not its pixels."""

from . import Entry
from .charts import LOOK, LOOK_BUT_FONTS

_HEATMAP = '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots(layout="constrained")
            wide = df.pivot_table(index="city", columns="month", values="rain", aggfunc="mean", sort=False)
            sns.heatmap(wide, cmap="viridis", cbar=False, ax=ax)
'''
_DOTS_3D = '''
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("island.csv")
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            ax.scatter(df["east"], df["north"], df["height"], depthshade=False)
            ax.set_xlabel("east"); ax.set_ylabel("north"); ax.set_zlabel("height")
'''
_DOTS = '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
'''


def _heatmap_ours(step):
    return f'''
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_heatmap(x="month", y="city", value="rain")
            chart.{step}
        '''


def _dots_ours(step):
    return f'''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            chart.{step}
        '''


def _dots_3d_ours(step):
    return f'''
            chart = sdata.chart(sdata.get_example("island"))
            chart.draw_dots_3d(x="east", y="north", z="height")
            chart.{step}
        '''


ENTRIES = [
    # ------------------------------------------------------------------ new chart types
    Entry(
        word="draw_rug_lines",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_density(x="marks")
            chart.draw_rug_lines(x="marks")
        ''',
        code={"seaborn": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            sns.kdeplot(df, x="marks", common_norm=False, ax=ax)
            # draw_rug_lines(x="marks")
            sns.rugplot(df, x="marks", ax=ax)
        '''},
        compare="chart",
        check=("segments", "lines"),
        also="seaborn's own rug height (2.5 % of the chart) and line width are kept. " + LOOK,
    ),
    Entry(
        word="draw_wind_rose",
        data="weather",
        ours='''
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_wind_rose(direction="wind_direction", speed="wind_speed")
        ''',
        code={"NumPy and matplotlib": '''
            import numpy as np, pandas as pd, matplotlib.pyplot as plt
            from matplotlib.ticker import MaxNLocator
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
            ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)    # (1)
            # draw_wind_rose(direction="wind_direction", speed="wind_speed")
            turned = np.mod(df["wind_direction"] + 15, 360)                 # (2)
            speeds = MaxNLocator(nbins=5).tick_values(df["wind_speed"].min(), df["wind_speed"].max())  # (3)
            counts, _, _ = np.histogram2d(turned, df["wind_speed"], bins=[np.arange(0, 361, 30), speeds])
            bottom = np.zeros(12)
            for band in counts.T:
                ax.bar(np.deg2rad(np.arange(0, 360, 30)), band, width=np.deg2rad(30), bottom=bottom)
                bottom = bottom + band
        '''},
        compare="chart",
        check=("bars", "polar_start"),
        choices=("a compass: 0 (north) at the top, going round clockwise.",
                 "every=30: twelve bars, each centred on its direction (north from 345 to 15 degrees); NumPy counts "
                 "the rows in each with histogram2d.",
                 "about five speed bands at round numbers (matplotlib's MaxNLocator), stacked from the slowest "
                 "outwards; a band with no rows is left out.",),
        also="simplydata colours the bands from viridis (slow is dark), names them in a legend and writes N, E, S, "
             "W round the edge. " + LOOK,
    ),
    Entry(
        word="draw_arrow",
        data="marks",
        ours=_dots_ours("draw_arrow(start=[2, 40], end=[4, 60])"),
        code={"matplotlib": _DOTS + '''
            # draw_arrow(start=[2, 40], end=[4, 60])
            ax.annotate("", xy=(4, 60), xytext=(2, 40), ha="center", va="center",   # (1)
                        arrowprops=dict(arrowstyle="->", linewidth=1.5, shrinkA=0, shrinkB=0))
        '''},
        compare="chart",
        check=("text_places", "dots"),
        choices=("a plain arrow 1.5 points wide that starts and ends exactly at the two places; words from labelled= "
                 "are centred on the start.",),
        also=LOOK,
    ),
    Entry(
        word="put_chart_inside",
        data="weather",
        ours='''
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month_number", y="temperature", colour="city")
            detail = sdata.chart(sdata.get_example("weather")).draw_bars(x="city", y="rain")
            chart.put_chart_inside(detail, where="bottom right", size=0.35)
        ''',
        code={"seaborn": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots()
            sns.lineplot(df, x="month_number", y="temperature", hue="city", ax=ax)
            # put_chart_inside(detail, where="bottom right", size=0.35)
            inset = ax.inset_axes([1 - 0.03 - 0.35, 0.03, 0.35, 0.35])       # (1)
            sns.barplot(df, x="city", y="rain", errorbar=None, ax=inset)
            inset.tick_params(labelsize="small")
        '''},
        compare="chart",
        check=("insets",),
        choices=("the small chart sits 0.03 of the chart's width in from the corner; its text is written small.",),
        also="The other chart's own steps (title, axis names, ranges) are drawn on the small chart. " + LOOK,
    ),
    Entry(
        word="add_second_x",
        data="weather",
        ours='''
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_dots(x="temperature", y="rain")
            chart.add_second_x(formula="x * 9 / 5 + 32", labelled="Temperature (°F)")
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="temperature", y="rain", ax=ax)
            # add_second_x(formula="x * 9 / 5 + 32", labelled="Temperature (°F)")
            top = ax.secondary_xaxis("top", functions=(lambda c: c * 9 / 5 + 32, lambda f: (f - 32) * 5 / 9))
            top.set_xlabel("Temperature (°F)")
        '''},
        compare="chart",
        check=("dots", "limits", "labels"),
        also="matplotlib needs the way back as well; simplydata finds it with SciPy's brentq on the drawn range, so you "
             "write only the formula (it must go only up, or only down). " + LOOK,
    ),
    # ------------------------------------------------------------------ frame, ticks and shape
    Entry(
        word="hide_frame",
        data="marks",
        ours=_dots_ours("hide_frame()"),
        code={"matplotlib": _DOTS + '''
            # hide_frame()
            ax.set_axis_off()
        '''},
        compare="chart",
        check=("dots", "limits"),
        also=LOOK,
    ),
    Entry(
        word="hide_ticks_x",
        data="marks",
        ours=_dots_ours("hide_ticks_x()"),
        code={"matplotlib": _DOTS + '''
            # hide_ticks_x()
            ax.tick_params(axis="x", which="both", length=0, labelbottom=False, labeltop=False)
        '''},
        compare="chart",
        check=("dots", "tick_places"),
        also=LOOK,
    ),
    Entry(
        word="hide_ticks_y",
        data="marks",
        ours=_dots_ours("hide_ticks_y()"),
        code={"matplotlib": _DOTS + '''
            # hide_ticks_y()
            ax.tick_params(axis="y", which="both", length=0, labelleft=False, labelright=False)
        '''},
        compare="chart",
        check=("dots", "tick_places"),
        also=LOOK,
    ),
    Entry(
        word="show_small_ticks_x",
        data="marks",
        ours=_dots_ours("show_small_ticks_x()"),
        code={"matplotlib": _DOTS + '''
            # show_small_ticks_x()
            ax.xaxis.minorticks_on()
        '''},
        compare="chart",
        check=("dots", "tick_places"),
        also="matplotlib chooses where the small ticks go (AutoMinorLocator; on a log scale, its own). " + LOOK,
    ),
    Entry(
        word="show_small_ticks_y",
        data="marks",
        ours=_dots_ours("show_small_ticks_y()"),
        code={"matplotlib": _DOTS + '''
            # show_small_ticks_y()
            ax.yaxis.minorticks_on()
        '''},
        compare="chart",
        check=("dots", "tick_places"),
        also="matplotlib chooses where the small ticks go. " + LOOK,
    ),
    Entry(
        word="use_true_shape",
        data="marks",
        ours=_dots_ours("use_true_shape()"),
        code={"matplotlib": _DOTS + '''
            # use_true_shape()
            ax.set_aspect("equal")
        '''},
        compare="chart",
        check=("dots", "limits"),
        also="The plot area shrinks to fit, so one unit is as long on both axes. " + LOOK,
    ),
    Entry(
        word="make_square",
        data="marks",
        ours=_dots_ours("make_square()"),
        code={"matplotlib": _DOTS + '''
            # make_square()
            ax.set_box_aspect(1)
        '''},
        compare="chart",
        check=("dots", "limits"),
        also=LOOK,
    ),
    # ------------------------------------------------------------------ colour bar
    Entry(
        word="put_colour_bar_at_bottom",
        data="weather",
        ours=_heatmap_ours("put_colour_bar_at_bottom()"),
        code={"seaborn": _HEATMAP + '''
            # put_colour_bar_at_bottom()
            fig.colorbar(ax.collections[0], ax=ax, location="bottom", label="rain")
        '''},
        compare="chart",
        check=("colour_bars", "cells"),
        also=LOOK,
    ),
    Entry(
        word="put_colour_bar_at_top",
        data="weather",
        ours=_heatmap_ours("put_colour_bar_at_top()"),
        code={"seaborn": _HEATMAP + '''
            # put_colour_bar_at_top()
            fig.colorbar(ax.collections[0], ax=ax, location="top", label="rain")
        '''},
        compare="chart",
        check=("colour_bars", "cells"),
        also=LOOK,
    ),
    Entry(
        word="put_colour_bar_at_left",
        data="weather",
        ours=_heatmap_ours("put_colour_bar_at_left()"),
        code={"seaborn": _HEATMAP + '''
            # put_colour_bar_at_left()
            fig.colorbar(ax.collections[0], ax=ax, location="left", label="rain")
        '''},
        compare="chart",
        check=("colour_bars", "cells"),
        also=LOOK,
    ),
    Entry(
        word="hide_colour_bar",
        data="weather",
        ours=_heatmap_ours("hide_colour_bar()"),
        code={"seaborn": _HEATMAP + '''
            # hide_colour_bar(): no fig.colorbar(...)
        '''},
        compare="chart",
        check=("colour_bars", "cells"),
        also="simplydata draws the bar and then takes it away (Colorbar.remove), so the other colour bar words "
             "still work. " + LOOK,
    ),
    Entry(
        word="put_ticks_colour_bar",
        data="weather",
        ours=_heatmap_ours("put_ticks_colour_bar(0, 10, 20, 30)"),
        code={"seaborn": _HEATMAP + '''
            bar = fig.colorbar(ax.collections[0], ax=ax, label="rain")
            # put_ticks_colour_bar(0, 10, 20, 30)
            bar.set_ticks([0, 10, 20, 30])
        '''},
        compare="chart",
        check=("colour_bars", "cells"),
        also=LOOK,
    ),
    # ------------------------------------------------------------------ 3D
    Entry(
        word="draw_lines_3d",
        data="island",
        ours='''
            chart = sdata.chart(sdata.get_example("island"))
            chart.draw_lines_3d(x="east", y="north", z="height")
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("island.csv")
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            # draw_lines_3d(x="east", y="north", z="height")
            ax.plot(df["east"], df["north"], df["height"])
            ax.set_xlabel("east"); ax.set_ylabel("north"); ax.set_zlabel("height")
        '''},
        compare="chart",
        check=("lines", "in_3d", "labels"),
        also="The line goes through the rows in the order of the table, one line for each group of colour=. " + LOOK,
    ),
    Entry(
        word="label_z",
        data="island",
        ours=_dots_3d_ours('label_z("Height (m)")'),
        code={"matplotlib": _DOTS_3D + '''
            # label_z("Height (m)")
            ax.set_zlabel("Height (m)")
        '''},
        compare="chart",
        check=("in_3d",),
        also=LOOK,
    ),
    Entry(
        word="set_range_z",
        data="island",
        ours=_dots_3d_ours("set_range_z(-10, 20)"),
        code={"matplotlib": _DOTS_3D + '''
            # set_range_z(-10, 20)
            ax.set_zlim(-10, 20)
        '''},
        compare="chart",
        check=("in_3d",),
        also=LOOK,
    ),
    Entry(
        word="put_ticks_z",
        data="island",
        ours=_dots_3d_ours("put_ticks_z(-10, 0, 10, 20)"),
        code={"matplotlib": _DOTS_3D + '''
            # put_ticks_z(-10, 0, 10, 20)
            ax.set_zticks([-10, 0, 10, 20])
        '''},
        compare="chart",
        check=("in_3d",),
        also=LOOK,
    ),
    Entry(
        word="look_from",
        data="island",
        ours=_dots_3d_ours("look_from(height=20, around=45)"),
        code={"matplotlib": _DOTS_3D + '''
            # look_from(height=20, around=45)
            ax.view_init(elev=20, azim=45)
        '''},
        compare="chart",
        check=("in_3d",),
        also="height= is matplotlib's elev (degrees up), around= its azim (degrees round); normal is 30 and -60, "
             "as in matplotlib. " + LOOK,
    ),
    # ------------------------------------------------------------------ describing a chart
    Entry(
        word="say_what_it_shows",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.say_what_it_shows()
        ''',
        compare="none",
        note="simplydata's own words, read back from the drawn matplotlib figure (Axes.get_title, get_xlabel, "
             "get_xlim, the tick names, the legend's texts, the colour bar, and the marks chart.get_numbers_drawn() "
             "reads). Nothing is worked out: write what the chart means in your own words.",
    ),
    # ------------------------------------------------------------------ options of older words
    Entry(
        word="draw_histogram",
        option="y=",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_histogram(x="hours", y="marks")
        ''',
        code={"seaborn": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots(layout="constrained")
            # draw_histogram(x="hours", y="marks")
            sns.histplot(df, x="hours", y="marks", bins=10, cmap="viridis", ax=ax)      # (1)
            fig.colorbar(ax.collections[0], ax=ax, label="count")                         # (2)
        '''},
        compare="chart",
        check=("cells", "colour_bars"),
        choices=("10 bins along each axis, in viridis colours as on heatmaps.",
                 "a colour bar named after what the colour shows (count, percent or density).",),
        also=LOOK,
    ),
    Entry(
        word="draw_density",
        option="y=",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_density(x="hours", y="marks")
        ''',
        code={"seaborn": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_density(x="hours", y="marks")
            sns.kdeplot(df, x="hours", y="marks", common_norm=False, ax=ax)
        '''},
        compare="chart",
        check=("shapes",),
        also="seaborn's own levels and bandwidth are kept. " + LOOK,
    ),
    Entry(
        word="draw_violins",
        option="in_halves=",
        data="school",
        ours='''
            chart = sdata.chart(sdata.get_example("school"))
            chart.draw_violins(x="class", y="marks", colour="breakfast", in_halves=True)
        ''',
        code={"seaborn": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("school.csv")
            fig, ax = plt.subplots()
            # draw_violins(x="class", y="marks", colour="breakfast", in_halves=True)
            sns.violinplot(df, x="class", y="marks", hue="breakfast", split=True,
                           cut=0, gap=0.1, saturation=1, ax=ax)                           # (1)
        '''},
        compare="chart",
        check=("shapes",),
        choices=("each half stops at the smallest and largest value (cut=0), with a small gap between the halves, as "
                 "on every simplydata violin.",),
        also=LOOK,
    ),
    Entry(
        word="draw_dots",
        option="show=",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="class", y="marks", show="average", error="standard error")
        ''',
        code={"seaborn": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_dots(x="class", y="marks", show="average", error="standard error")
            sns.pointplot(df, x="class", y="marks", estimator="mean", errorbar="se",
                          linestyle="none", capsize=0.1, ax=ax)                           # (1)
        '''},
        compare="chart",
        check=("lines",),
        choices=("no line joins the dots (it would suggest a trend between groups), small caps on the error bars, "
                 "and colour groups side by side so their error bars do not cover each other.",),
        also="A line says which error was drawn. " + LOOK,
    ),
    Entry(
        word="draw_bars",
        option="stacked=",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks", colour="subject", stacked="percent")
        ''',
        code={"pandas": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_bars(x="class", y="marks", colour="subject", stacked="percent")
            wide = df.groupby(["class", "subject"])["marks"].sum().unstack("subject")      # (1)
            wide = wide[["Maths", "Science", "English"]]
            shares = wide.div(wide.sum(axis=1), axis=0).mul(100)
            shares.plot(kind="bar", stacked=True, rot=0, width=0.8, ax=ax)
            ax.set_ylabel("percent of total marks")                                     # (2)
        '''},
        compare="chart",
        check=("bars", "labels"),
        choices=("with stacked=\"percent\" each bar is the total of its group (show=\"total\"), so a stack shows shares "
                 "of the whole; show=\"average\" gives shares of averages, with a note.",
                 "the y-axis says whose shares they are: \"percent of total\" the column.",),
        also="The groups keep the order they appear in (order_legend changes it). " + LOOK,
    ),
    Entry(
        word="draw_pie",
        option="hole=",
        data="fruit",
        ours='''
            chart = sdata.chart(sdata.get_example("fruit"))
            chart.draw_pie(labels="fruit", values="count", hole=0.4)
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.read_csv("fruit.csv")
            fig, ax = plt.subplots()
            # draw_pie(labels="fruit", values="count", hole=0.4)
            sizes = df.groupby("fruit", sort=False)["count"].sum()
            ax.pie(sizes, labels=sizes.index, autopct="%1.0f%%", startangle=90, counterclock=False,
                   wedgeprops=dict(width=1 - 0.4), pctdistance=1 - (1 - 0.4) / 2)       # (1)
        '''},
        compare="chart",
        check=("shapes", "text_places"),
        choices=("the percents are written in the middle of the ring.",),
        also=LOOK,
    ),
    Entry(
        word="draw_surface",
        option="as_wires=",
        data="island",
        ours='''
            chart = sdata.chart(sdata.get_example("island"))
            chart.draw_surface(x="east", y="north", z="height", as_wires=True)
        ''',
        code={"matplotlib": '''
            import numpy as np, pandas as pd, matplotlib.pyplot as plt
            df = pd.read_csv("island.csv")
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            # draw_surface(x="east", y="north", z="height", as_wires=True)
            wide = df.pivot(index="north", columns="east", values="height")
            gx, gy = np.meshgrid(wide.columns, wide.index)
            ax.plot_wireframe(gx, gy, wide.to_numpy(), linewidth=0.8)
            ax.set_xlabel("east"); ax.set_ylabel("north"); ax.set_zlabel("height")
        '''},
        compare="chart",
        check=("in_3d", "labels"),
        also="A wire frame has no colours, so no colour bar is drawn. " + LOOK,
    ),
    Entry(
        word="draw_surface",
        option="with_height_lines=",
        data="island",
        ours='''
            chart = sdata.chart(sdata.get_example("island"))
            chart.draw_surface(x="east", y="north", z="height", with_height_lines=True)
        ''',
        code={"matplotlib": '''
            import numpy as np, pandas as pd, matplotlib.pyplot as plt
            df = pd.read_csv("island.csv")
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
            # draw_surface(x="east", y="north", z="height", with_height_lines=True)
            wide = df.pivot(index="north", columns="east", values="height")
            gx, gy = np.meshgrid(wide.columns, wide.index)
            gz = wide.to_numpy(); kw = dict(cmap="viridis", vmin=gz.min(), vmax=gz.max())
            ax.plot_surface(gx, gy, gz, linewidth=0, **kw)
            ax.contour(gx, gy, gz, zdir="z", offset=gz.min(), levels=10, **kw)          # (1)
            ax.set_xlabel("east"); ax.set_ylabel("north"); ax.set_zlabel("height")
        '''},
        compare="chart",
        check=("in_3d", "labels"),
        choices=("ten height lines, on the floor of the box (at the lowest height), in the surface's colours.",),
        also=LOOK,
    ),
    Entry(
        word="draw_line_at_y",
        option="between=",
        data="marks",
        ours=_dots_ours("draw_line_at_y(50, between=[2, 6])"),
        code={"matplotlib": _DOTS + '''
            # draw_line_at_y(50, between=[2, 6])
            ax.hlines(50, 2, 6, colors="grey", linestyles="--", linewidths=1.5, zorder=2.5)   # (1)
        '''},
        compare="chart",
        check=("segments", "dots"),
        choices=("grey, dashed and 1.5 points wide, as the line right across the chart.",),
        also=LOOK,
    ),
    Entry(
        word="use_font_size",
        option="title=",
        data="marks",
        ours='''
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks", colour="subject")
            chart.write_title_on_top("Marks")
            chart.use_font_size(12, title=20, ticks=8)
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            # use_font_size(12, title=20, ticks=8)
            sizes = {"axes.titlesize": 20, "xtick.labelsize": 8, "ytick.labelsize": 8,
                     "axes.labelsize": 13, "legend.fontsize": 11}                       # (1)
            with plt.rc_context(sizes):
                fig, ax = plt.subplots()
                sns.barplot(df, x="class", y="marks", hue="subject", errorbar=None, ax=ax)
                ax.set_title("Marks")
        '''},
        compare="chart",
        check=("font_sizes", "labels"),
        choices=("title= and ticks= replace those two sizes only; the axis names (13) and the legend (11) keep the "
                 "sizes of the paper look at text size 12.",),
        also=LOOK_BUT_FONTS,
    ),
    Entry(
        word="put_legend_at_bottom",
        option="per_row=",
        data="weather",
        ours='''
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="month", y="temperature", colour="city")
            chart.put_legend_at_bottom(per_row=2)
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots(layout="constrained")
            sns.lineplot(df, x="month", y="temperature", hue="city", errorbar=None, ax=ax)
            # put_legend_at_bottom(per_row=2)
            handles, labels = ax.get_legend_handles_labels()
            ax.get_legend().remove()
            fig.legend(handles, labels, title="city", loc="outside lower center", ncols=2)
        '''},
        compare="chart",
        check=("legend_place", "lines"),
        also=LOOK,
    ),
    Entry(
        word="add_second_y",
        option="formula=",
        data="weather",
        ours='''
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_dots(x="rain", y="temperature")
            chart.add_second_y(formula="y * 9 / 5 + 32", labelled="Temperature (°F)")
        ''',
        code={"matplotlib": '''
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="rain", y="temperature", ax=ax)
            # add_second_y(formula="y * 9 / 5 + 32", labelled="Temperature (°F)")
            right = ax.secondary_yaxis("right", functions=(lambda c: c * 9 / 5 + 32, lambda f: (f - 32) * 5 / 9))
            right.set_ylabel("Temperature (°F)")
        '''},
        compare="chart",
        check=("dots", "limits", "labels"),
        also="simplydata finds the way back with SciPy's brentq on the drawn range, so you write only the "
             "formula. " + LOOK,
    ),
]
