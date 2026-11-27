"""seaborn's colour tools (owner's decision 2026-11-28): the cases of the reliability study.

cases_underneath.py loads this file and adds cases(Case) to the study. A set of colours and a changed colour have no
data by nature, so sdata.show_colours is checked against the published Tableau 10 codes of matplotlib's "tab10" and
sdata.change_colour against the colour worked out by hand in hue, lightness and saturation (Python's colorsys, the
standard HLS formulas); both are also compared with seaborn. The colour options of the chart words draw Fisher's iris
data, with the colour of each bar read back and compared with seaborn's own chart.
"""

from __future__ import annotations

import colorsys
import textwrap

# matplotlib's "tab10" (the Tableau 10 colours), as published in matplotlib's colour documentation
TAB10 = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22",
         "#17becf"]
PUBLISHED = "matplotlib documentation, 'tab10' (Tableau 10)"
BY_HAND = "exact: worked by hand in hue, lightness and saturation (Python colorsys)"
BARS = """
    import matplotlib.colors as mcolors
    shown = chart.get_numbers_drawn().as_pandas()
    {f"bar {i + 1}": float(int(mcolors.to_hex(c)[1:], 16)) for i, c in enumerate(shown["colour"])}
"""
SEABORN_BARS = """
    import matplotlib.colors as mcolors
    {f"bar {i + 1}": float(int(mcolors.to_hex(p.get_facecolor())[1:], 16)) for i, p in enumerate(ax.patches)
     if p.get_height() > 0}
"""


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def _hex(rgb) -> float:
    return float(int("".join(f"{round(v * 255):02x}" for v in rgb), 16))


def _hls(colour_rgb, h=None, l=None, s=None):  # noqa: E741 - the HLS letters
    hh, ll, ss = colorsys.rgb_to_hls(*colour_rgb)
    return colorsys.hls_to_rgb(hh if h is None else h, ll if l is None else l, ss if s is None else s)


def cases(Case):
    navy = (0.0, 0.0, 128 / 255)
    grey_blue = (0x7a / 255, 0x8f / 255, 0x99 / 255)
    red_h, red_l, red_s = colorsys.rgb_to_hls(1.0, 0.0, 0.0)
    return [
        Case("sdata.show_colours", "matplotlib's tab10 set: the ten Tableau colours", "closed form (no data)",
             "closed form",
             ours="""
                 codes = sdata.show_colours("tab10")
                 {f"colour {i + 1}": float(int(c[1:], 16)) for i, c in enumerate(codes)}
             """,
             published={f"colour {i + 1}": (float(int(c[1:], 16)), 0.0, PUBLISHED) for i, c in enumerate(TAB10)},
             parent="""
                 import seaborn as sns
                 {f"colour {i + 1}": float(int(c[1:], 16)) for i, c in enumerate(sns.color_palette("tab10").as_hex())}
             """, parent_label="seaborn color_palette", parent_tolerance=0.0),
        Case("sdata.change_colour", "navy made lighter: lightness 0.6", "closed form (no data)", "closed form",
             ours="""
                 {"colour": float(int(sdata.change_colour("navy", lightness=0.6)[1:], 16))}
             """,
             published={"colour": (_hex(_hls(navy, l=0.6)), 0.0, BY_HAND)},
             parent="""
                 import seaborn as sns
                 import matplotlib.colors as mcolors
                 {"colour": float(int(mcolors.to_hex(sns.set_hls_values("navy", l=0.6))[1:], 16))}
             """, parent_label="seaborn set_hls_values", parent_tolerance=0.0),
        Case("sdata.change_colour", "red at half its colour strength", "closed form (no data)", "closed form",
             option="colour_strength_times=",
             ours="""
                 {"colour": float(int(sdata.change_colour("red", colour_strength_times=0.5)[1:], 16))}
             """,
             published={"colour": (_hex(colorsys.hls_to_rgb(red_h, red_l, red_s * 0.5)), 0.0, BY_HAND)},
             parent="""
                 import seaborn as sns
                 import matplotlib.colors as mcolors
                 {"colour": float(int(mcolors.to_hex(sns.desaturate("red", 0.5))[1:], 16))}
             """, parent_label="seaborn desaturate", parent_tolerance=0.0),
        Case("sdata.change_colour", "a grey blue at full colour strength", "closed form (no data)", "closed form",
             option="full_colour_strength=",
             ours="""
                 {"colour": float(int(sdata.change_colour("#7a8f99", full_colour_strength=True)[1:], 16))}
             """,
             published={"colour": (_hex(_hls(grey_blue, s=1.0)), 0.0, BY_HAND)},
             parent="""
                 import seaborn as sns
                 import matplotlib.colors as mcolors
                 {"colour": float(int(mcolors.to_hex(sns.saturate("#7a8f99"))[1:], 16))}
             """, parent_label="seaborn saturate", parent_tolerance=0.0),
        Case("use_colours", "average petal length of Fisher's three iris species, in xkcd colours", "iris",
             "real data", option="from_colour_list=",
             ours=_code("""
                 chart = sdata.chart(sdata.table(data))
                 chart.draw_bars(x="Species", y="Petal.Length", colour="Species")
                 chart.use_colours("windows blue", "amber", "faded green", from_colour_list="xkcd")
             """, BARS),
             parent=_code("""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="Species", y="Petal.Length", hue="Species", errorbar=None, saturation=1,
                             palette=sns.xkcd_palette(["windows blue", "amber", "faded green"]), ax=ax)
             """, SEABORN_BARS), parent_label="seaborn barplot with xkcd_palette", parent_tolerance=0.0),
        Case("use_colour", "average petal length of Fisher's iris species in Crayola's Mahogany", "iris",
             "real data", option="from_colour_list=",
             ours=_code("""
                 chart = sdata.chart(sdata.table(data))
                 chart.draw_bars(x="Species", y="Petal.Length")
                 chart.use_colour("Mahogany", from_colour_list="crayon")
             """, BARS),
             parent=_code("""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="Species", y="Petal.Length", errorbar=None, saturation=1,
                             color=sns.crayon_palette(["Mahogany"])[0], ax=ax)
             """, SEABORN_BARS), parent_label="seaborn barplot with crayon_palette", parent_tolerance=0.0),
        Case("use_style", "Fisher's iris species in the letters b, g and r as seaborn's colours", "iris",
             "real data", option="colour_letters=",
             ours=_code("""
                 chart = sdata.chart(sdata.table(data))
                 chart.draw_bars(x="Species", y="Petal.Length", colour="Species")
                 chart.use_colours("b", "g", "r")
                 chart.use_style("paper", colour_letters="seaborn")
             """, BARS),
             parent=_code("""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 sns.set_color_codes("deep")
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="Species", y="Petal.Length", hue="Species", errorbar=None, saturation=1,
                             palette=["b", "g", "r"], ax=ax)
                 sns.set_color_codes("reset")
             """, SEABORN_BARS), parent_label="seaborn barplot after set_color_codes", parent_tolerance=0.0),
    ]
