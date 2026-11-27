"""Colour words of seaborn's palette tools (owner's decision 2026-11-28: cover all of seaborn).

sdata.show_colours (seaborn palplot), sdata.pick_colours_with_sliders (seaborn's choose_*_palette widgets, in
Jupyter with ipywidgets) and sdata.change_colour (seaborn desaturate, saturate and set_hls_values). The names of
xkcd's and Crayola's colours (seaborn xkcd_palette and crayon_palette) work in the colour words through
from_colour_list=, and use_style(colour_letters=) is seaborn set_color_codes. Own code is glue only. Nothing is
downloaded and nothing is installed: seaborn keeps both colour lists inside the package.
"""

from __future__ import annotations

from ._errors import SimplydataError, choice_error, friendly

COLOUR_LISTS = ("xkcd", "crayon")
SLIDER_KINDS = {"brewer": "choose_colorbrewer_palette", "cubehelix": "choose_cubehelix_palette",
                "dark": "choose_dark_palette", "light": "choose_light_palette",
                "diverging": "choose_diverging_palette"}
BREWER_TYPES = ("sequential", "diverging", "qualitative")
LETTER_SETS = ("seaborn", "deep", "muted", "pastel", "dark", "bright", "colorblind")


def colours_from_list(names, from_colour_list: str, step: str) -> list:
    """Colour names of xkcd's survey or of Crayola's crayons as colours matplotlib can use (seaborn xkcd_palette or
    crayon_palette), with a friendly sentence for a name the list does not have."""
    import seaborn as sns
    from matplotlib.colors import to_hex

    if from_colour_list not in COLOUR_LISTS:
        raise choice_error(step, "from_colour_list", from_colour_list, list(COLOUR_LISTS))
    known = sns.colors.xkcd_rgb if from_colour_list == "xkcd" else sns.colors.crayons
    missing = [n for n in names if not isinstance(n, str) or n not in known]
    if missing:
        from ._errors import suggest

        guess = suggest(str(missing[0]), list(known), n=1)
        raise SimplydataError(f'.{step}() does not know the {from_colour_list} colour {missing[0]!r}.'
                              + (f' Did you mean "{guess[0]}"?' if guess else "")
                              + f" The {len(known)} names are in seaborn.colors."
                              + ("xkcd_rgb" if from_colour_list == "xkcd" else "crayons") + ".")
    found = sns.xkcd_palette(list(names)) if from_colour_list == "xkcd" else sns.crayon_palette(list(names))
    return [to_hex(c) for c in found]


def _colours_of(palette, how_many):
    import seaborn as sns
    from matplotlib.colors import is_color_like, to_hex

    if isinstance(palette, (list, tuple)) and palette and all(is_color_like(c) for c in palette):
        return [to_hex(c) for c in palette]
    if isinstance(palette, str):
        try:
            return [to_hex(c) for c in sns.color_palette(palette, how_many)]
        except (ValueError, KeyError):
            pass
    raise SimplydataError('show_colours() needs a named set of colours, such as "deep", "Set2" or "viridis", or a '
                          'list of colours, such as ["navy", "#E69F00"].')


@friendly
def show_colours(colours=None, how_many=None, save_as=None):
    """Draw a row of colour swatches, to see a set of colours before you use it. sdata.show_colours("deep")

    sdata.show_colours("Set2") draws seaborn's palplot of the set and prints each colour as a code (#66c2a5 ...),
    which use_colours() takes. colours= is a named set (seaborn's "deep", "muted", "pastel", "colorblind",
    matplotlib's "tab10", "Set2", a colour scale such as "viridis" with how_many=), or your own list of colours.
    save_as="colours.png" saves the picture; in Jupyter it is shown. Gives back the colour codes, as a list.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    if how_many is not None and (isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 1):
        raise SimplydataError(f"how_many= should be a whole number such as 6, not {how_many!r}.")
    codes = _colours_of(colours, how_many)
    sns.palplot(codes)
    fig = plt.gcf()
    print(f"{len(codes)} colours (seaborn palplot):")
    for code in codes:
        print(code)
    if save_as is not None:
        fig.savefig(save_as, bbox_inches="tight")
        print(f"Saved the swatches to {save_as}.")
    from ._web import in_notebook as in_jupyter

    if in_jupyter():
        plt.show()
    else:
        plt.close(fig)
    return codes


def _jupyter_and_widgets() -> str | None:
    """None when the sliders can run (Jupyter with ipywidgets), else what is missing, in plain words."""
    from ._web import in_notebook as in_jupyter

    if not in_jupyter():
        return ("The sliders need Jupyter (a notebook or JupyterLab): they move inside the notebook. Here, choose a "
                "set by name instead and look at it with sdata.show_colours(\"deep\").")
    try:
        import ipywidgets  # noqa: F401
    except ImportError:
        return ("The sliders need the package ipywidgets, which is not installed. Install it yourself if you want "
                "them (pip install ipywidgets); simplydata never installs anything.")
    return None


@friendly
def pick_colours_with_sliders(kind="brewer", brewer_type="sequential"):
    """Choose a set of colours with sliders in Jupyter. sdata.pick_colours_with_sliders(kind="dark")

    kind= "brewer" (the ColorBrewer sets; brewer_type= "sequential", "diverging" or "qualitative"), "cubehelix",
    "dark", "light" or "diverging": seaborn's choose_colorbrewer_palette, choose_cubehelix_palette,
    choose_dark_palette, choose_light_palette and choose_diverging_palette. Gives back the list of colours, which
    changes as you move the sliders; give it to chart.use_colours(...). Needs Jupyter and ipywidgets; anywhere else
    it says what is needed and gives back nothing. simplydata never installs anything.
    """
    import seaborn.widgets as widgets

    if kind not in SLIDER_KINDS:
        raise choice_error("pick_colours_with_sliders", "kind", kind, list(SLIDER_KINDS))
    if brewer_type not in BREWER_TYPES:
        raise choice_error("pick_colours_with_sliders", "brewer_type", brewer_type, list(BREWER_TYPES))
    missing = _jupyter_and_widgets()
    if missing is not None:
        print(missing)
        return None
    choose = getattr(widgets, SLIDER_KINDS[kind])
    print(f"Move the sliders; the list this gives back follows them (seaborn {SLIDER_KINDS[kind]}).")
    return choose(brewer_type) if kind == "brewer" else choose()


def _share(value, name: str):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise SimplydataError(f"{name}= should be a number from 0 to 1, not {value!r}.")
    return float(value)


@friendly
def change_colour(colour=None, lightness=None, colour_strength=None, colour_strength_times=None, hue=None,
                  full_colour_strength=False):
    """A lighter, darker, greyer or stronger version of a colour, as a colour code. sdata.change_colour("navy", lightness=0.6)

    lightness= sets how light the colour is, from 0 (black) to 1 (white); colour_strength= sets how strong
    (saturated) it is, from 0 (grey) to 1 (full colour); hue= sets the colour round the colour wheel, from 0 to 1
    (0 red, 1/3 green, 2/3 blue). These are seaborn set_hls_values(color, h=hue, l=lightness, s=colour_strength).
    colour_strength_times=0.5 makes the colour half as strong (seaborn desaturate(color, prop)), and
    full_colour_strength=True makes it as strong as it can be (seaborn saturate). Gives back the new colour as a
    code such as "#3a5fcd", which every colour word takes.
    """
    import seaborn as sns
    from matplotlib.colors import is_color_like, to_hex

    if colour is None or isinstance(colour, bool) or not is_color_like(colour):
        raise SimplydataError('change_colour() needs a colour, such as "navy" or "#0072B2".\nFor example:  '
                              'sdata.change_colour("navy", lightness=0.6)')
    if not isinstance(full_colour_strength, bool):
        raise SimplydataError("full_colour_strength= should be True or False.")
    lightness, colour_strength = _share(lightness, "lightness"), _share(colour_strength, "colour_strength")
    hue, times = _share(hue, "hue"), _share(colour_strength_times, "colour_strength_times")
    done = []
    out = colour
    if full_colour_strength:
        out = sns.saturate(out)
        done.append("full colour strength (seaborn saturate)")
    if times is not None:
        out = sns.desaturate(out, times)
        done.append(f"colour strength times {times:g} (seaborn desaturate)")
    if lightness is not None or colour_strength is not None or hue is not None:
        out = sns.set_hls_values(out, h=hue, l=lightness, s=colour_strength)
        done.append("hue, lightness and colour strength set (seaborn set_hls_values)")
    if not done:
        raise SimplydataError("change_colour() needs what to change: lightness=, colour_strength=, hue=, "
                              "colour_strength_times= or full_colour_strength=True.")
    code = to_hex(out)
    print(f"{colour} with {'; '.join(done)}: {code}")
    return code
