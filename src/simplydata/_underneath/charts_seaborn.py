"""seaborn's colour tools (owner's decision 2026-11-28: cover all of seaborn): sdata.show_colours (palplot),
sdata.change_colour (set_hls_values, desaturate, saturate), sdata.pick_colours_with_sliders (the choose_*_palette
widgets), from_colour_list= on use_colour and use_colours (xkcd_palette, crayon_palette) and use_style(colour_letters=)
(set_color_codes).
"""

from . import Entry

ENTRIES = [
    Entry(
        word="sdata.show_colours",
        ours="""
            sdata.show_colours("tab10")
        """,
        code={"seaborn": """
            import seaborn as sns
            # show_colours("tab10")
            colours = sns.color_palette("tab10").as_hex()
            sns.palplot(colours)
            for code in colours:
                print(code)
        """},
        compare="printed",
        also="simplydata also gives back the codes as a list, saves the swatches with save_as=, and shows them in "
             "Jupyter.",
    ),
    Entry(
        word="sdata.change_colour",
        ours="""
            sdata.change_colour("navy", lightness=0.6)
        """,
        code={"seaborn": """
            import seaborn as sns
            from matplotlib.colors import to_hex
            # change_colour("navy", lightness=0.6)
            to_hex(sns.set_hls_values("navy", l=0.6))
        """},
        compare="value",
        also="simplydata also names each change in its sentence and checks that every share is from 0 to 1.",
    ),
    Entry(
        word="sdata.change_colour", option="colour_strength_times=",
        ours="""
            sdata.change_colour("red", colour_strength_times=0.5)
        """,
        code={"seaborn": """
            import seaborn as sns
            from matplotlib.colors import to_hex
            # change_colour("red", colour_strength_times=0.5)
            to_hex(sns.desaturate("red", 0.5))
        """},
        compare="value",
    ),
    Entry(
        word="sdata.change_colour", option="full_colour_strength=",
        ours="""
            sdata.change_colour("#7a8f99", full_colour_strength=True)
        """,
        code={"seaborn": """
            import seaborn as sns
            from matplotlib.colors import to_hex
            # change_colour("#7a8f99", full_colour_strength=True)
            to_hex(sns.saturate("#7a8f99"))
        """},
        compare="value",
    ),
    Entry(
        word="sdata.pick_colours_with_sliders",
        ours="""
            sdata.pick_colours_with_sliders(kind="dark")
        """,
        compare="none",
        note="The sliders run only in Jupyter with ipywidgets: seaborn choose_dark_palette() (and choose_colorbrewer_"
             "palette, choose_cubehelix_palette, choose_light_palette, choose_diverging_palette for the other kinds). "
             "Anywhere else simplydata says what is needed and gives back nothing; it never installs anything.",
    ),
    Entry(
        word="use_colours", option="from_colour_list=",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="subject", y="marks", colour="class")
            chart.use_colours("windows blue", "amber", "faded green", from_colour_list="xkcd")
        """,
        code={"seaborn": """
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # use_colours("windows blue", "amber", "faded green", from_colour_list="xkcd")
            sns.barplot(df, x="subject", y="marks", hue="class", hue_order=["A", "B", "C"],
                        palette=sns.xkcd_palette(["windows blue", "amber", "faded green"]),
                        errorbar=None, saturation=1, ax=ax)
        """},
        compare="chart",
        check=("colours", "bars"),
        also="from_colour_list=\"crayon\" reads Crayola's names (seaborn crayon_palette); a name the list lacks gets "
             "a \"Did you mean\" line.",
    ),
    Entry(
        word="use_colour", option="from_colour_list=",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="class", y="marks")
            chart.use_colour("Mahogany", from_colour_list="crayon")
        """,
        code={"seaborn": """
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # use_colour("Mahogany", from_colour_list="crayon")
            sns.barplot(df, x="class", y="marks", errorbar=None, color=sns.crayon_palette(["Mahogany"])[0],
                        saturation=1, ax=ax)
        """},
        compare="chart",
        check=("colours", "bars"),
    ),
    Entry(
        word="use_style", option="colour_letters=",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_bars(x="subject", y="marks", colour="class")
            chart.use_colours("b", "g", "r")
            chart.use_style("paper", colour_letters="seaborn")
        """,
        code={"seaborn": """
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # use_style("paper", colour_letters="seaborn")
            sns.set_color_codes("deep")
            sns.barplot(df, x="subject", y="marks", hue="class", hue_order=["A", "B", "C"],
                        palette=["b", "g", "r"], errorbar=None, saturation=1, ax=ax)
            sns.set_color_codes("reset")   # matplotlib's letters again
        """},
        compare="chart",
        check=("colours", "bars"),
        also="simplydata changes the letters for this chart only; seaborn changes them for the whole session.",
    ),
]
