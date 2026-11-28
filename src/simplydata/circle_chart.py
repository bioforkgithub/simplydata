"""Circle charts (circular plots): chord diagrams and circos-style figures, drawn by the R package circlize.

circle_chart = table.start_circle_chart() starts one; words such as circle_chart.draw_links(...) only record what
is asked, as on an ordinary chart. Nothing reaches R until circle_chart.save("x.svg") or circle_chart.show(): then
simplydata writes one R program for the whole picture, in a fixed order (circlize::circos.par, the start of the
circle, the group ring and the names, the links, and what circlize drew read back), and runs it on a picture device
that only simplydata._circlize opens (decision Z1). The data go to R as R variables in memory, never as a file;
circle_chart.show_steps() prints the program with the data as variable names, never values, so a reviewer can rerun
it in R without simplydata.

Batch 1 of the circular plots (approved by Manish 2026-11-27, design "circular plots, best of Circos and circlize"):
start_circle_chart, draw_links (the chord diagram route, circlize::chordDiagram, and the positions route,
circlize::circos.link), the colours (use_colours, use_colour_scale, colour=, split_colours_at=, transparency=),
set_size, rotate, flip_x, save, show, show_steps and get_numbers_drawn. simplydata's colour words make the colours
and hand circlize a plain list (decision B3).
"""

from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd

from ._data import is_listlike, load
from ._errors import SimplydataError, choice_error, column_error, friendly, missing_word_error, other_name_error
from ._typing import _Same

# chordDiagram's own defaults, kept so that a chart drawn by simplydata and by circlize alone look the same
DEFAULT_TRANSPARENCY = 0.5
DEFAULT_SIZE = (7.0, 7.0)  # inches: a circle needs a square page
LINKS_ORDERED_BY = {"fewest crossings": '"default"', "strength": "TRUE", "table order": "FALSE"}
DIRECTION_DRAWN_AS = {"arrows": '"arrows"', "different heights": '"diffHeight"',
                      "both": 'c("diffHeight", "arrows")'}
SELF_LINKS_DRAWN_AS = {"hill": 1, "two ends": 2}
ARROW_SHAPES = {"triangle": "triangle", "circle": "circle", "ellipse": "ellipse", "T": "T", "simple": "simple",
                "curved": "curved", "big arrow": "big.arrow"}
DRAWN_AS = ("ribbons", "lines")
# split_colours_at=: below the split and at or above it (ColorBrewer's RdBu blue and red, safe for colour blindness)
SPLIT_COLOURS = ("#2166AC", "#B2182B")
SAVE_RESOLUTION = 300
SHOW_RESOLUTION = 100


# ---------------------------------------------------------------- small checks
def _is_number(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float, np.integer, np.floating)) \
        and math.isfinite(float(value))


def _share(value, option, word, low=0.0, high=1.0, inclusive_low=False):
    """A share of the circle (or of its radius) between low and high."""
    if not _is_number(value) or not ((low <= value if inclusive_low else low < value) and value <= high):
        raise SimplydataError(f".{word}() needs {option}= to be a number above {low:g} and at most {high:g}, "
                              f"not {value!r}.")
    return float(value)


def _degrees(value, option, word) -> float:
    """gap= as a share of the circle (0.02 is 2 % of the way round) or as "2 degrees"."""
    if isinstance(value, str):
        found = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(?:degrees?|°)\s*", value)
        if not found:
            raise SimplydataError(f'.{word}() needs {option}= as a share of the circle (such as 0.02) or in degrees '
                                  f'(such as "2 degrees"), not {value!r}.')
        return float(found.group(1))
    if not _is_number(value) or not 0 <= value < 0.5:
        raise SimplydataError(f".{word}() needs {option}= as a share of the circle between 0 and 0.5 (such as "
                              f'0.02, which is 2 % of the way round) or in degrees (such as "2 degrees"), '
                              f"not {value!r}.")
    return float(value) * 360.0


def _height(value, option, word) -> str:
    """A height in the circle as R code: a share of the radius (0.1) or in millimetres ("3 mm", circlize::mm_h)."""
    if isinstance(value, str):
        found = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(mm|cm)\s*", value)
        if not found:
            raise SimplydataError(f'.{word}() needs {option}= as a share of the radius (such as 0.1) or in mm or cm '
                                  f'(such as "3 mm"), not {value!r}.')
        size = float(found.group(1)) * (10.0 if found.group(2) == "cm" else 1.0)
        return f"circlize::mm_h({size:g})"
    return f"{_share(value, option, word, high=1.0, inclusive_low=True):g}"


def _cm(value, option, word) -> float:
    """An arrow size in cm, as circlize measures it (a number, or "3 mm" / "0.3 cm")."""
    if isinstance(value, str):
        found = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(mm|cm)\s*", value)
        if found:
            return float(found.group(1)) / (10.0 if found.group(2) == "mm" else 1.0)
    if _is_number(value) and value > 0:
        return float(value)
    raise SimplydataError(f'.{word}() needs {option}= as a size in cm (such as 0.4) or "4 mm", not {value!r}.')


def _switch(value, option, word) -> bool:
    if not isinstance(value, bool):
        raise SimplydataError(f".{word}() needs {option}=True or {option}=False, not {value!r}.")
    return value


def _column(frame: pd.DataFrame, name, option, word):
    if not isinstance(name, str):
        raise SimplydataError(f".{word}() needs {option}= to be the name of a column, not {name!r}.")
    if name not in frame.columns:
        raise column_error(name, frame.columns)
    return name


def _natural_key(text):
    """chr2 before chr10: numbers inside names compared as numbers (circlize's sort.chr idea)."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", str(text))]


def _r_text(value: str) -> str:
    """A fixed word of simplydata (never data) as an R string."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _r_bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"


# ---------------------------------------------------------------- colours
def _hex(colour) -> str:
    from matplotlib import colors as mcolors

    return mcolors.to_hex(colour, keep_alpha=False).upper()


def _base_colours(settings) -> list:
    from ._style import palette

    return list(settings.get("colours") or palette(settings))


def _colours_for(values, settings) -> list:
    """One colour for each of these values (groups, or the words of a text column), in order."""
    base = _base_colours(settings)
    if len(values) > len(dict.fromkeys(base)):
        from .words._helpers import repeat_note

        repeat_note(len(values), len(dict.fromkeys(base)))
    return [_hex(base[i % len(base)]) for i in range(len(values))]


def _scale_colours(numbers, settings, word):
    """Colours for a column of numbers, from circle_chart.use_colour_scale(...) (or viridis), made by matplotlib."""
    from types import SimpleNamespace

    from .words._colour_scale import scale_for

    values = np.asarray(numbers, dtype=float)
    ctx = SimpleNamespace(settings=settings, store={})
    cmap, norm, _, _ = scale_for(ctx, values, word)
    return [_hex(cmap(norm(v))) if np.isfinite(v) else "#BEBEBE" for v in values]


def _split_colours(numbers, at, settings):
    """split_colours_at=: one colour below the split, another at or above it (the two ends of
    circle_chart.use_colour_scale(...) when it is used)."""
    spec = settings.get("colour_scale") or {}
    if spec.get("map") is not None:
        below, above = _hex(spec["map"](0.0)), _hex(spec["map"](1.0))
    else:
        below, above = SPLIT_COLOURS
    values = np.asarray(numbers, dtype=float)
    return [below if v < at else above for v in values]


# ---------------------------------------------------------------- the chart
class CircleChart:
    """A circle chart (circular plot), drawn by R circlize. Start one with circle_chart = table.start_circle_chart()."""

    _is_simplydata_circle_chart = True
    _OLD_WORDS: dict = {}  # no old names yet

    def __init__(self, data, start: dict):
        self._data = load(data) if data is not None else pd.DataFrame()
        self._start = start
        self._links: list[dict] = []
        self._settings = {"style": "paper", "width": DEFAULT_SIZE[0], "height": DEFAULT_SIZE[1],
                          "start_degree": None, "clockwise": True, "each_group_clockwise": True}

    # ------------------------------------------------------------ the words
    @friendly
    def draw_links(self: _Same, from_table=None, links_from=None, links_to=None, strength=None, from_between=None,
                   to_between=None, with_direction=False, direction_drawn_as=None, height_difference=None,
                   drawn_as="ribbons", colour=None, split_colours_at=None, transparency=None, outline_colour=None,
                   outline_thickness=None, thickness=None, dashed=False, links_ordered_by=None, biggest_first=True,
                   biggest_on_top=False, hidden=None, with_in_and_out_overlapping=True, same_both_ways=False,
                   with_self_links=True, self_links_drawn_as=None, with_target_shares=False,
                   target_shares_height=None, arrow_length=None, arrow_width=None, arrow_shape=None,
                   arrow_colour=None, arrow_thickness=None, bend=None, bend_sharpness=None, with_twists=False,
                   hide_groups_smaller_than=None, bundled_when_closer_than=None, with_jitter=False,
                   with_seed=1) -> _Same:
        """Links between groups: a chord diagram, or links between places on the groups.
        circle_chart.draw_links(links_from="site", links_to="gene", strength="copies")

        links_from= and links_to= name the columns with the group at each end of a link; strength= is a column with
        the amount each link carries (its width). Without from_between= and to_between=, the groups and their sizes
        come from the links themselves (a chord diagram: circlize chordDiagram). With them, each link joins two places
        on groups made by start_circle_chart(around=, sizes=): from_between=["qstart", "qend"] and
        to_between=["sstart", "send"] are the columns with the start and end of each end of the link (circlize
        circos.link), for genome comparisons such as BLAST hits. The route used is printed.
        from_table= (or a table as the first thing in the brackets) takes the links from another table.
        with_direction=True draws each link from links_from to links_to; with_direction="both ways" for both;
        direction_drawn_as="arrows", "different heights" or "both", with height_difference= (a share of the radius,
        or "2 mm").
        colour= colours the links: "from" (the colour of the group a link starts at, normal), "to", one colour
        ("grey"), or a column (words: one colour each; numbers: circle_chart.use_colour_scale(...), or two colours
        with split_colours_at=0). transparency= is how see-through the links are (0 solid, normally 0.5).
        links_ordered_by= "fewest crossings" (normal), "strength" (with biggest_first=) or "table order" sets the
        order of the link ends on each group; biggest_on_top=True draws the widest links last.
        drawn_as="lines" draws each link as a line (thickness=); outline_colour=, outline_thickness= and dashed=True
        draw the ribbons' edges. hidden= is a column of True/False: those links take their space but are not drawn.
        with_target_shares=True adds a thin bar on each group with the colours of the groups its links go to
        (target_shares_height=). same_both_ways=True keeps one link for each pair a-b and b-a (a symmetric table);
        with_self_links=False leaves out links from a group to itself, and self_links_drawn_as="hill" or "two ends"
        draws them. hide_groups_smaller_than=0.01 leaves out groups below 1 % of the total.
        arrow_length=, arrow_width= (in cm, or "4 mm"), arrow_shape= ("triangle", "big arrow" ...),
        arrow_colour= and arrow_thickness= shape the arrows; bend= (0 to 1, how high a link rises; or "5 mm"),
        bend_sharpness= and with_twists=True shape the curves.
        On the positions route, bundled_when_closer_than=500 joins links between the same two groups whose ends lie
        closer than 500 into one (the count is kept as the column "links in bundle"), and with_jitter=True varies
        each link's curve a little (with_seed=1, printed), so that links on top of each other can be told apart. A
        bundle coloured by a column of numbers takes the average of its links.
        """
        word = "draw_links"
        source = self._data if from_table is None else load(from_table)
        if not isinstance(source, pd.DataFrame) or source.empty:
            raise SimplydataError(".draw_links() needs a table with the links: start the circle chart from a table "
                                  "(table.start_circle_chart()) or give from_table=.")
        if links_from is None or links_to is None:
            raise SimplydataError('.draw_links() needs links_from= and links_to=, the columns with the group at each '
                                  'end of a link: circle_chart.draw_links(links_from="site", links_to="gene").')
        spec = dict(table=source, links_from=_column(source, links_from, "links_from", word),
                    links_to=_column(source, links_to, "links_to", word))
        if strength is not None:
            _column(source, strength, "strength", word)
            if not pd.api.types.is_numeric_dtype(source[strength]):
                raise SimplydataError(f'.draw_links() needs strength= to be a column of numbers; "{strength}" is not.')
        spec["strength"] = strength
        positions = (from_between is not None, to_between is not None)
        if any(positions) and not all(positions):
            raise SimplydataError(".draw_links() needs both from_between= and to_between= (the places of both ends "
                                  "of each link), or neither (a chord diagram).")
        spec["route"] = "positions" if all(positions) else "chord"
        for option, value in (("from_between", from_between), ("to_between", to_between)):
            if value is None:
                spec[option] = None
                continue
            columns = [value] if isinstance(value, str) else list(value) if is_listlike(value) else None
            if not columns or len(columns) > 2:
                raise SimplydataError(f'.draw_links() needs {option}= as one column (a place) or two columns (the '
                                      f'start and the end), such as {option}=["start", "end"], not {value!r}.')
            for name in columns:
                _column(source, name, option, word)
                if not pd.api.types.is_numeric_dtype(source[name]):
                    raise SimplydataError(f'.draw_links() needs {option}= to name columns of numbers; "{name}" is '
                                          "not.")
            spec[option] = columns
        if with_direction not in (True, False, "both ways"):
            raise SimplydataError('.draw_links() needs with_direction=True, False or "both ways", not '
                                  f"{with_direction!r}.")
        spec["with_direction"] = with_direction
        if direction_drawn_as is not None:
            if direction_drawn_as not in DIRECTION_DRAWN_AS:
                raise choice_error(word, "direction_drawn_as", direction_drawn_as, list(DIRECTION_DRAWN_AS))
            if not with_direction:
                raise SimplydataError(".draw_links() draws a direction only with with_direction=True (or \"both "
                                      'ways"); add it, or leave out direction_drawn_as=.')
        spec["direction_drawn_as"] = direction_drawn_as
        spec["height_difference"] = None if height_difference is None else _height(
            height_difference, "height_difference", word)
        if drawn_as not in DRAWN_AS:
            raise choice_error(word, "drawn_as", drawn_as, list(DRAWN_AS))
        spec["drawn_as"] = drawn_as
        if thickness is not None and drawn_as != "lines":
            raise SimplydataError('.draw_links() uses thickness= for links drawn as lines (drawn_as="lines"); for '
                                  "the edge of a ribbon, use outline_thickness=.")
        for option, value in (("thickness", thickness), ("outline_thickness", outline_thickness),
                              ("arrow_thickness", arrow_thickness)):
            if value is not None and not (_is_number(value) and value >= 0):
                raise SimplydataError(f".draw_links() needs {option}= to be a number of 0 or more, not {value!r}.")
        spec.update(thickness=thickness, outline_thickness=outline_thickness, arrow_thickness=arrow_thickness)
        spec["colour"] = self._check_link_colour(source, colour)
        if split_colours_at is not None:
            if not _is_number(split_colours_at):
                raise SimplydataError(f".draw_links() needs split_colours_at= to be a number, such as 0, not "
                                      f"{split_colours_at!r}.")
            if not (isinstance(colour, str) and colour in source.columns
                    and pd.api.types.is_numeric_dtype(source[colour])):
                raise SimplydataError('.draw_links() splits the colours of a column of numbers: give it as colour= '
                                      '(colour="correlation", split_colours_at=0).')
        spec["split_colours_at"] = split_colours_at
        if transparency is not None:
            from .words._helpers import check_transparency

            check_transparency(word, transparency)
        spec["transparency"] = DEFAULT_TRANSPARENCY if transparency is None else float(transparency)
        from .words.look import check_colour

        spec["outline_colour"] = None if outline_colour is None else _hex(check_colour(outline_colour, word))
        spec["arrow_colour"] = None if arrow_colour is None else _hex(check_colour(arrow_colour, word))
        spec["dashed"] = _switch(dashed, "dashed", word)
        if links_ordered_by is not None and links_ordered_by not in LINKS_ORDERED_BY:
            raise choice_error(word, "links_ordered_by", links_ordered_by, list(LINKS_ORDERED_BY))
        spec["links_ordered_by"] = links_ordered_by
        spec["biggest_first"] = _switch(biggest_first, "biggest_first", word)
        spec["biggest_on_top"] = _switch(biggest_on_top, "biggest_on_top", word)
        if hidden is not None:
            _column(source, hidden, "hidden", word)
            if not pd.api.types.is_bool_dtype(source[hidden]):
                raise SimplydataError(f'.draw_links() needs hidden= to be a column of True and False; "{hidden}" is '
                                      "not.")
        spec["hidden"] = hidden
        spec["with_in_and_out_overlapping"] = _switch(with_in_and_out_overlapping, "with_in_and_out_overlapping",
                                                      word)
        spec["same_both_ways"] = _switch(same_both_ways, "same_both_ways", word)
        spec["with_self_links"] = _switch(with_self_links, "with_self_links", word)
        if self_links_drawn_as is not None and self_links_drawn_as not in SELF_LINKS_DRAWN_AS:
            raise choice_error(word, "self_links_drawn_as", self_links_drawn_as, list(SELF_LINKS_DRAWN_AS))
        spec["self_links_drawn_as"] = self_links_drawn_as
        spec["with_target_shares"] = _switch(with_target_shares, "with_target_shares", word)
        spec["target_shares_height"] = None if target_shares_height is None else _height(
            target_shares_height, "target_shares_height", word)
        spec["arrow_length"] = None if arrow_length is None else _cm(arrow_length, "arrow_length", word)
        spec["arrow_width"] = None if arrow_width is None else _cm(arrow_width, "arrow_width", word)
        if arrow_shape is not None and arrow_shape not in ARROW_SHAPES:
            raise choice_error(word, "arrow_shape", arrow_shape, list(ARROW_SHAPES))
        spec["arrow_shape"] = arrow_shape
        if bend is not None and not isinstance(bend, str):
            _share(bend, "bend", word)
        spec["bend"] = None if bend is None else (_height(bend, "bend", word) if isinstance(bend, str) else float(bend))
        if bend_sharpness is not None and not (_is_number(bend_sharpness) and bend_sharpness > 0):
            raise SimplydataError(f".draw_links() needs bend_sharpness= to be a number above 0 (1 is normal), not "
                                  f"{bend_sharpness!r}.")
        spec["bend_sharpness"] = bend_sharpness
        spec["with_twists"] = _switch(with_twists, "with_twists", word)
        spec["hide_groups_smaller_than"] = None if hide_groups_smaller_than is None else _share(
            hide_groups_smaller_than, "hide_groups_smaller_than", word, high=0.5)
        if bundled_when_closer_than is not None and not (_is_number(bundled_when_closer_than)
                                                         and bundled_when_closer_than >= 0):
            raise SimplydataError(f".draw_links() needs bundled_when_closer_than= to be a distance of 0 or more, "
                                  f"not {bundled_when_closer_than!r}.")
        spec["bundled_when_closer_than"] = bundled_when_closer_than
        spec["with_jitter"] = _switch(with_jitter, "with_jitter", word)
        if isinstance(with_seed, bool) or not isinstance(with_seed, (int, np.integer)):
            raise SimplydataError(f".draw_links() needs with_seed= to be a whole number, not {with_seed!r}.")
        spec["with_seed"] = int(with_seed)
        self._check_route(spec)
        if spec["route"] == "chord" and self._links:
            raise SimplydataError("A chord diagram has one set of links: this circle chart already has them. Put all "
                                  "the links in one table (table.add_rows_from(...)) and draw them once.")
        if self._links and self._links[0]["route"] != spec["route"]:
            raise SimplydataError("Links with places (from_between=, to_between=) and links of a chord diagram "
                                  "cannot share one circle chart.")
        self._links.append(spec)
        return self

    def _check_link_colour(self, source, colour):
        from .words.look import check_colour

        if colour is None or colour in ("from", "to"):
            return colour
        if isinstance(colour, str) and colour in source.columns:
            return ("column", colour)
        if isinstance(colour, str):
            from matplotlib.colors import is_color_like

            if is_color_like(colour):
                return ("one", _hex(check_colour(colour, "draw_links")))
        raise SimplydataError(f'.draw_links() needs colour= to be "from", "to", a colour such as "grey", or a column '
                              f"of the links table; {colour!r} is none of these.\n"
                              "Columns you have: " + ", ".join(map(str, source.columns)))

    def _check_route(self, spec):
        """Options that belong to one route only, said plainly."""
        chord_only = {"links_ordered_by": spec["links_ordered_by"] is not None,
                      "same_both_ways": spec["same_both_ways"], "with_target_shares": spec["with_target_shares"],
                      "self_links_drawn_as": spec["self_links_drawn_as"] is not None,
                      "hide_groups_smaller_than": spec["hide_groups_smaller_than"] is not None,
                      "height_difference": spec["height_difference"] is not None,
                      "hidden": spec["hidden"] is not None}
        positions_only = {"bundled_when_closer_than": spec["bundled_when_closer_than"] is not None,
                          "with_jitter": spec["with_jitter"]}
        if spec["route"] == "positions":
            used = [k for k, v in chord_only.items() if v]
            if spec["direction_drawn_as"] in ("different heights", "both"):
                used.append('direction_drawn_as="different heights"')
            if used:
                raise SimplydataError(f".draw_links() with from_between= and to_between= draws each link between the "
                                      f"places given, so {used[0]}= does not apply (it belongs to a chord diagram, "
                                      "where circlize places the links itself).")
        else:
            used = [k for k, v in positions_only.items() if v]
            if used:
                raise SimplydataError(f".draw_links() uses {used[0]}= on links between places (from_between= and "
                                      "to_between=); in a chord diagram circlize places the links itself.")
        if spec["strength"] is not None and spec["route"] == "positions":
            raise SimplydataError(".draw_links() with from_between= and to_between= takes each link's width from "
                                  "the places given; leave out strength=.")

    @friendly
    def use_colours(self: _Same, *names, how_many=None, from_colour_list=None) -> _Same:
        """Your own colours for the groups, in order. circle_chart.use_colours("teal", "orange", "purple")

        Or a named set: circle_chart.use_colours("Set2"), "tab10", "Dark2", seaborn's "colorblind", or
        "colour-blind safe" (Okabe-Ito, simplydata's own colours, used normally). With a colour scale and how_many=,
        the colours are taken evenly from it: circle_chart.use_colours("viridis", how_many=5). The same colours go to
        a column of words given as colour= in draw_links. simplydata makes the colours and hands circlize the list.
        """
        from .words.look import check_colour, colour_set

        if len(names) == 1 and is_listlike(names[0]):
            names = tuple(names[0])
        if not names:
            raise SimplydataError('.use_colours() needs at least one colour, for example '
                                  'circle_chart.use_colours("teal", "orange").')
        if from_colour_list is not None:
            from .colours import colours_from_list

            if how_many is not None:
                raise SimplydataError("how_many= takes colours from a named set; with from_colour_list=, list the "
                                      "colours themselves.")
            self._settings["colours"] = colours_from_list(names, from_colour_list, "use_colours")
            return self
        if how_many is not None and (isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 1):
            raise SimplydataError(f"how_many= should be a whole number such as 5, not {how_many!r}.")
        from matplotlib import colors as mcolors

        if len(names) == 1 and isinstance(names[0], str) and not mcolors.is_color_like(names[0]):
            self._settings["colours"] = colour_set(names[0], how_many)
            return self
        if how_many is not None:
            raise SimplydataError('how_many= takes colours from a named set or a colour scale, for example '
                                  'circle_chart.use_colours("viridis", how_many=5); with your own colours, list them '
                                  "all.")
        self._settings["colours"] = [check_colour(n, "use_colours") for n in names]
        return self

    use_colors = use_colours  # American spelling, same word

    @friendly
    def use_colour_scale(self: _Same, *names, middle=None, log=False, steps=None, between=None,
                         from_colour_list=None) -> _Same:
        """The colours for a column of numbers (colour= in draw_links). circle_chart.use_colour_scale("white", "navy")

        A name: "viridis" (normal), "cividis", "magma", "blues" ..., "blue to red" or "purple to orange" for numbers
        on both sides of a middle (all safe for colour-blind readers); or two or more colours make your own.
        middle=0 puts the middle colour at 0; log=True spreads the colours on a log scale; steps=5 cuts the scale
        into 5 colours (or steps=[0, 5, 10, 20]); between=[70, 100] fixes the two ends, so several charts share
        them. With split_colours_at= in draw_links, the two ends of the scale are the two colours.
        simplydata (matplotlib) makes the colours and hands circlize the list.
        """
        from .words._colour_scale import check_options, resolve_map

        if from_colour_list is not None:
            from .colours import colours_from_list

            if len(names) < 2:
                raise SimplydataError("from_colour_list= needs two or more colour names, from the low end to the high "
                                      "end.")
            names = tuple(colours_from_list(names, from_colour_list, "use_colour_scale"))
        cmap, shown = resolve_map(names, "use_colour_scale")
        middle, log, steps, between = check_options(middle, log, steps, between, "use_colour_scale")
        self._settings["colour_scale"] = dict(map=cmap, name=shown, middle=middle, log=log, steps=steps,
                                              between=between)
        return self

    use_color_scale = use_colour_scale  # American spelling, same word

    @friendly
    def set_size(self: _Same, width=7, height=7, unit="inches") -> _Same:
        """The size of the picture. circle_chart.set_size(width=17, height=17, unit="cm")

        unit= is "inches" (normal), "cm" or "mm". A saved file is exactly this size; normally 7 by 7 inches.
        """
        from ._units import PER_INCH, check_number, check_unit

        unit = check_unit(unit, "set_size")
        if unit == "pixels":
            raise SimplydataError('.set_size() of a circle chart is in "inches", "cm" or "mm"; for more pixels in a '
                                  ".png, use circle_chart.save(\"x.png\", resolution=600).")
        width = check_number(width, "width", "set_size")
        height = check_number(height, "height", "set_size")
        self._settings.update(width=width / PER_INCH[unit], height=height / PER_INCH[unit])
        return self

    @friendly
    def rotate(self: _Same, by_degrees=90) -> _Same:
        """Turn the circle, so the first group starts somewhere else. circle_chart.rotate(by_degrees=90)

        Degrees go anticlockwise from 3 o'clock, as in circlize (circos.par start.degree): by_degrees=90 starts the
        first group at 12 o'clock.
        """
        if not _is_number(by_degrees):
            raise SimplydataError(f".rotate() needs by_degrees= to be a number, such as 90, not {by_degrees!r}.")
        self._settings["start_degree"] = float(by_degrees)
        return self

    @friendly
    def flip_x(self: _Same, which="the circle") -> _Same:
        """Go round the other way: the groups follow each other anticlockwise. circle_chart.flip_x()

        flip_x("each group") instead turns the places inside every group around (circlize xaxis.clock.wise), so
        they grow anticlockwise; the groups keep their order.
        """
        if which == "the circle":
            self._settings["clockwise"] = False
        elif which == "each group":
            self._settings["each_group_clockwise"] = False
        else:
            raise choice_error("flip_x", "which", which, ["the circle", "each group"])
        return self

    # ------------------------------------------------------------ output
    @friendly
    def save(self: _Same, file_name, quality="normal", resolution=None, dpi=None) -> _Same:
        """Save the circle chart. circle_chart.save("chord_diagram.svg")

        The end of the file name decides the format: .svg and .pdf keep text and lines sharp at any size (for
        journals), .png is a picture of pixels (resolution= dots per inch, normally 300; quality="high" is 600).
        R circlize draws straight into this one file; nothing else is written.
        """
        from pathlib import Path

        from ._units import check_number

        path = Path(file_name)
        kind = path.suffix.lower().lstrip(".")
        if not kind:
            raise SimplydataError(f'Add a file type to the name, for example "{path.name}.svg" or "{path.name}.png".')
        if kind not in ("png", "svg", "pdf"):
            raise choice_error("save", "file type", kind, ["png", "svg", "pdf"])
        if quality not in ("normal", "high"):
            raise choice_error("save", "quality", quality, ["normal", "high"])
        if dpi is not None:
            if resolution is not None:
                raise SimplydataError(".save() needs resolution= or dpi= (they mean the same), not both.")
            resolution = dpi
        if resolution is None:
            resolution = 600 if quality == "high" else SAVE_RESOLUTION
        else:
            resolution = check_number(resolution, "resolution", "save")
        if path.parent and not path.parent.exists():
            raise SimplydataError(f'The folder "{path.parent}" does not exist. Create it first.')
        from . import _circlize

        body, values = self._program()
        _circlize.draw_into_file(body, values, path.resolve(), self._settings["width"], self._settings["height"],
                                 resolution)
        return self

    @friendly
    def show(self: _Same) -> _Same:
        """Show the circle chart. circle_chart.show()

        R circlize draws it as a picture in a private temporary folder, which is deleted as soon as the picture
        is read; in a notebook the picture appears below the cell.
        """
        from . import _circlize

        body, values = self._program()
        data = _circlize.draw_for_showing(body, values, self._settings["width"], self._settings["height"],
                                          SHOW_RESOLUTION)
        _circlize.show_png(data)
        return self

    @friendly
    def show_steps(self: _Same) -> _Same:
        """Print the R code that draws this circle chart. circle_chart.show_steps()

        The code is the one simplydata runs with R circlize, in order. Your data go in as the R variables it names
        (each from a column of your table, listed first), never as numbers in the code, so you can rerun it in R
        with your own data, or show a reviewer exactly what was drawn.
        """
        body, values = self._program()
        print("The R code simplydata runs for this circle chart (R circlize). The data go in as these R variables:")
        for name, about in self._about_values(values).items():
            print(f"  {name}: {about}")
        print("The picture device is opened by circle_chart.save() or circle_chart.show(); in R, draw on any device.")
        print()
        from . import _circlize

        print(_circlize.WRAP.format(body=body))
        return self

    @friendly
    def get_numbers_drawn(self):
        """A table of what circlize drew, read back from R. drawn = circle_chart.get_numbers_drawn()

        One row for each group and each link:
          part          "group" or "link"
          group         the group (for a link: the group it starts at)
          to_group      for a link: the group it goes to
          low, high     where the group or the link's start lies on the group (circlize's own positions)
          to_low, to_high  where the link's end lies on the group it goes to
          strength      the link's amount
          start_degree, end_degree  where the group starts and ends round the circle (in degrees, anticlockwise
                        from 3 o'clock)
          colour        the colour drawn (with its see-through part, as circlize keeps it)
        Nothing is worked out again: circlize places the groups and the links, and these are its numbers.
        """
        from . import _circlize
        from .table.table import table

        body, values = self._program()
        found = _circlize.run(body, values, kind=None, width=self._settings["width"],
                              height=self._settings["height"]) or {}
        frame = drawn_table(found)
        groups = int((frame["part"] == "group").sum())
        links = int((frame["part"] == "link").sum())
        print(f"Drawn: {groups} group{'s' if groups != 1 else ''} and {links} link{'s' if links != 1 else ''}.")
        return table(frame)

    # ------------------------------------------------------------ the R program
    def _about_values(self, values) -> dict:
        return {name: about for name, about in self._value_notes.items() if name in values}

    def _groups(self):
        """The groups in order, and for the positions route their sizes: (names, starts, ends, labels, notes)."""
        start = self._start
        frame = self._data
        links = self._links
        around, sizes = start.get("around"), start.get("sizes")
        if around is not None:
            if around not in frame.columns:
                raise column_error(around, frame.columns)
            names = list(dict.fromkeys(frame[around].dropna().astype(str)))
        else:
            names = []
            for spec in links:
                t = spec["table"]
                for column in (spec["links_from"], spec["links_to"]):
                    names += list(t[column].dropna().astype(str))
            names = list(dict.fromkeys(names))
        order = start.get("in_order")
        if order == "natural":
            names = sorted(names, key=_natural_key)
        elif order is not None:
            unknown = [g for g in order if str(g) not in names]
            if unknown:
                raise SimplydataError(f".start_circle_chart(in_order=...) names a group the chart does not have: "
                                      f"{unknown[0]!r}. The groups are: " + ", ".join(names))
            names = [str(g) for g in order] + [g for g in names if g not in {str(o) for o in order}]
        return names

    def _program(self):
        """The R code of the whole picture and the R variables it uses (the data)."""
        if not self._links and self._start.get("around") is None:
            raise SimplydataError("This circle chart has nothing to draw yet. Add links: "
                                  'circle_chart.draw_links(links_from="site", links_to="gene", strength="copies"), '
                                  "or start it with around= (the column of groups) and sizes=.")
        self._value_notes = {}
        names = self._groups()
        route = self._links[0]["route"] if self._links else "positions"
        lines = []
        values = {}
        settings = self._settings
        start = self._start
        par = []
        if settings["start_degree"] is not None:
            par.append(f"start.degree = {settings['start_degree']:g}")
        if not settings["clockwise"]:
            par.append("clock.wise = FALSE")
        if not settings["each_group_clockwise"]:
            par.append("xaxis.clock.wise = FALSE")
        if start.get("space_around_circle") is not None:
            par.append(f"circle.margin = {start['space_around_circle']:g}")
        if route == "positions":  # the rings hold exactly what is drawn in them (chordDiagram does the same)
            par.append("cell.padding = c(0, 0, 0, 0)")
        gap = start.get("gap")
        if isinstance(gap, dict):
            values["gaps"] = self._gap_vector(names, gap)
            self._value_notes["gaps"] = "the gap after each group, in degrees (from gap=)"
            par.append("gap.after = gaps")
        elif route == "positions" and gap is not None:
            par.append(f"gap.after = {gap:g}")
        if par:
            lines.append("  circlize::circos.par(" + ", ".join(par) + ")")
        group_colours = self._group_colours(names)
        values["group_names"] = names
        values["group_colours"] = group_colours
        self._value_notes["group_names"] = "the groups, in order round the circle"
        self._value_notes["group_colours"] = "the colour of each group"
        labels = self._group_labels(names)
        if labels != names:
            values["group_labels"] = labels
            self._value_notes["group_labels"] = f'the name written for each group (column "{start["names"]}")'
        label_code = "group_labels" if labels != names else "group_names"
        with_names = start.get("with_names", True)
        text_cex = (start.get("text_size") or 12) / 12
        names_height = f"circlize::mm_h({3 * text_cex:.3g})"
        thickness = start.get("thickness") or "circlize::mm_h(2)"
        no_ring = start.get("thickness") == "0"
        name_text = (f"circlize::circos.text(circlize::CELL_META$xcenter, circlize::CELL_META$ylim[1], "
                     f"{label_code}[match(circlize::CELL_META$sector.index, group_names)], facing = \"inside\", "
                     f"niceFacing = TRUE, adj = c(0.5, 0), cex = {text_cex:.3g})")
        if route == "chord":
            lines += self._chord_lines(names, values, with_names, names_height, thickness, no_ring, name_text)
        else:
            lines += self._positions_lines(names, values, with_names, names_height, thickness, no_ring, name_text)
        lines += READ_BACK
        return "\n".join(lines), values

    def _gap_vector(self, names, gap):
        out = []
        for i, group in enumerate(names):
            after = names[(i + 1) % len(names)]
            out.append(gap.get((group, after), gap.get("between others", 1.0)))
        unknown = [pair for pair in gap if pair != "between others" and (
            pair[0] not in names or names[(names.index(pair[0]) + 1) % len(names)] != pair[1])]
        if unknown:
            raise SimplydataError(f".start_circle_chart(gap=...) has a gap between {unknown[0][0]!r} and "
                                  f"{unknown[0][1]!r}, but {unknown[0][1]!r} does not follow {unknown[0][0]!r} round "
                                  "the circle. The groups go: " + ", ".join(names))
        return out

    def _group_colours(self, names):
        colour = self._start.get("colour")
        if colour is None:
            return _colours_for(names, self._settings)
        kind, value = colour
        if kind == "one":
            return [value] * len(names)
        if kind == "dict":
            missing = [g for g in names if g not in value]
            base = dict(zip(missing, _colours_for(missing, self._settings)))
            return [value.get(g) or base[g] for g in names]
        frame = self._data  # a column: the first colour given for each group
        around = self._start["around"]
        firsts = frame.drop_duplicates(subset=[around]).set_index(frame.drop_duplicates(subset=[around])[around]
                                                                  .astype(str))[value]
        from .words.look import check_colour

        return [_hex(check_colour(firsts[g], "start_circle_chart")) for g in names]

    def _group_labels(self, names):
        column = self._start.get("names")
        if column is None:
            return list(names)
        frame = self._data
        around = self._start["around"]
        firsts = frame.drop_duplicates(subset=[around])
        found = dict(zip(firsts[around].astype(str), firsts[column].astype(str)))
        return [found.get(g, g) for g in names]

    def _link_table(self, spec, names):
        """The links as a pandas table: from, to, value (and places), with the rows simplydata leaves out said."""
        t = spec["table"]
        cols = {"from": t[spec["links_from"]].astype(str), "to": t[spec["links_to"]].astype(str)}
        frame = pd.DataFrame(cols)
        frame["value"] = 1.0 if spec["strength"] is None else pd.to_numeric(t[spec["strength"]], errors="coerce")
        for option, keys in (("from_between", ("from_low", "from_high")), ("to_between", ("to_low", "to_high"))):
            if spec[option] is not None:
                first, last = spec[option][0], spec[option][-1]
                low = pd.to_numeric(t[first], errors="coerce")
                high = pd.to_numeric(t[last], errors="coerce")
                frame[keys[0]], frame[keys[1]] = np.minimum(low, high), np.maximum(low, high)
        kind = spec["colour"]
        if isinstance(kind, tuple) and kind[0] == "column":
            frame["colour_value"] = t[kind[1]].to_numpy()
        if spec["hidden"] is not None:
            frame["hidden"] = t[spec["hidden"]].astype(bool).to_numpy()
        empty = frame.drop(columns=[c for c in ("colour_value",) if c in frame]).isna().any(axis=1) | t[
            spec["links_from"]].isna().to_numpy() | t[spec["links_to"]].isna().to_numpy()
        if empty.any():
            n = int(empty.sum())
            print(f"Note: {n} link{'s' if n != 1 else ''} with an empty cell {'were' if n != 1 else 'was'} left out.")
            frame = frame[~empty]
        if spec["strength"] is not None and (frame["value"] < 0).any():
            raise SimplydataError(f'.draw_links() needs strength= to be 0 or more: "{spec["strength"]}" has negative '
                                  "numbers. Give the size as strength= and the sign as colour= (with "
                                  "split_colours_at=0).")
        if not spec["with_self_links"]:
            frame = frame[frame["from"] != frame["to"]]
        if spec["same_both_ways"]:
            pairs = frame.apply(lambda r: tuple(sorted((r["from"], r["to"]))), axis=1)
            frame = frame[~pairs.duplicated()]
        unknown = sorted(set(frame["from"]).union(frame["to"]) - set(names))
        if unknown:
            raise SimplydataError(f'.draw_links() names a group the circle chart does not have: "{unknown[0]}". The '
                                  "groups come from start_circle_chart(around=...): " + ", ".join(names))
        return frame.reset_index(drop=True)

    def _link_colours(self, spec, frame, names, group_colours):
        kind = spec["colour"]
        by_group = dict(zip(names, group_colours))
        if kind in (None, "from"):
            return [by_group[g] for g in frame["from"]]
        if kind == "to":
            return [by_group[g] for g in frame["to"]]
        if kind[0] == "one":
            return [kind[1]] * len(frame)
        column = frame["colour_value"]
        if pd.api.types.is_numeric_dtype(column):
            if spec["split_colours_at"] is not None:
                return _split_colours(column, float(spec["split_colours_at"]), self._settings)
            return _scale_colours(column, self._settings, "draw_links")
        words = list(dict.fromkeys(column.astype(str)))
        lookup = dict(zip(words, _colours_for(words, self._settings)))
        return [lookup[w] for w in column.astype(str)]

    def _link_options(self, spec, chord):
        """The options both routes pass to circlize (chordDiagram passes them on to circos.link)."""
        out = []
        if spec["outline_colour"] is not None:
            out.append(f"{'link.border' if chord else 'border'} = {_r_text(spec['outline_colour'])}")
        lwd = spec["thickness"] if spec["drawn_as"] == "lines" else spec["outline_thickness"]
        if lwd is not None:
            out.append(f"{'link.lwd' if chord else 'lwd'} = {lwd:g}")
        if spec["dashed"]:
            out.append(f"{'link.lty' if chord else 'lty'} = 2")
        if spec["drawn_as"] == "lines":
            out.append("reduce_to_mid_line = TRUE")
        arrow = "link.arr." if chord else "arr."
        for key, r_name in (("arrow_length", "length"), ("arrow_width", "width")):
            if spec[key] is not None:
                out.append(f"{arrow}{r_name} = {spec[key]:g}")
        if spec["arrow_shape"] is not None:
            out.append(f"{arrow}type = {_r_text(ARROW_SHAPES[spec['arrow_shape']])}")
        if spec["arrow_colour"] is not None:
            out.append(f"{arrow}col = {_r_text(spec['arrow_colour'])}")
        if spec["arrow_thickness"] is not None:
            out.append(f"{arrow}lwd = {spec['arrow_thickness']:g}")
        if not spec["with_jitter"]:
            if spec["bend"] is not None:
                bend = spec["bend"]
                out.append(f"h = {bend}" if isinstance(bend, str) else f"h.ratio = {bend:g}")
            if spec["bend_sharpness"] is not None:
                out.append(f"w = {spec['bend_sharpness']:g}")
        if spec["with_twists"]:
            out.append("inverse = TRUE")
        return out

    def _chord_lines(self, names, values, with_names, names_height, thickness, no_ring, name_text):
        spec = self._links[0]
        start = self._start
        frame = self._link_table(spec, names)
        names_used = [g for g in names if g in set(frame["from"]).union(frame["to"])]
        left_out = [g for g in names if g not in names_used]
        if left_out:
            print("Note: " + ", ".join(left_out) + f" ha{'ve' if len(left_out) > 1 else 's'} no links, so "
                  f"{'they are' if len(left_out) > 1 else 'it is'} not on the chord diagram.")
            keep = [i for i, g in enumerate(names) if g in names_used]
            values["group_names"] = [values["group_names"][i] for i in keep]
            values["group_colours"] = [values["group_colours"][i] for i in keep]
            if "group_labels" in values:
                values["group_labels"] = [values["group_labels"][i] for i in keep]
            names = names_used
        group_colours = values["group_colours"]
        self._say_route("Drawn as a chord diagram (circlize chordDiagram): the groups and their sizes come from the "
                        "links.")
        values["links_from"] = list(frame["from"])
        values["links_to"] = list(frame["to"])
        values["strength"] = [float(v) for v in frame["value"]]
        values["link_colours"] = self._link_colours(spec, frame, names, group_colours)
        self._value_notes.update({
            "links_from": f'the group each link starts at (column "{spec["links_from"]}")',
            "links_to": f'the group each link goes to (column "{spec["links_to"]}")',
            "strength": (f'the amount of each link (column "{spec["strength"]}")' if spec["strength"]
                         else "1 for every link (no strength= given)"),
            "link_colours": "the colour of each link" + (
                f' (from column "{spec["colour"][1]}")' if isinstance(spec["colour"], tuple)
                and spec["colour"][0] == "column" else ""),
        })
        args = ["data.frame(from = links_from, to = links_to, value = strength, stringsAsFactors = FALSE)",
                "grid.col = stats::setNames(group_colours, group_names)", "col = link_colours",
                f"transparency = {spec['transparency']:g}"]
        if start.get("in_order") is not None:
            args.append("order = group_names")
        if spec["with_direction"]:
            args.append(f"directional = {2 if spec['with_direction'] == 'both ways' else 1}")
            if spec["direction_drawn_as"] is not None:
                args.append(f"direction.type = {DIRECTION_DRAWN_AS[spec['direction_drawn_as']]}")
            if spec["height_difference"] is not None:
                args.append(f"diffHeight = {spec['height_difference']}")
            if not spec["with_in_and_out_overlapping"] and spec["with_direction"] is True:
                args.append("link.overlap = FALSE")
        if spec["links_ordered_by"] is not None:
            args.append(f"link.sort = {LINKS_ORDERED_BY[spec['links_ordered_by']]}")
        if not spec["biggest_first"]:
            args.append("link.decreasing = FALSE")
        if spec["biggest_on_top"]:
            args.append("link.largest.ontop = TRUE")
        if spec["hidden"] is not None:
            values["link_shown"] = [not h for h in frame["hidden"]]
            self._value_notes["link_shown"] = f'FALSE for the links drawn hidden (column "{spec["hidden"]}")'
            args.append("link.visible = link_shown")
        if spec["self_links_drawn_as"] is not None:
            args.append(f"self.link = {SELF_LINKS_DRAWN_AS[spec['self_links_drawn_as']]}")
        if spec["with_target_shares"]:
            args.append("link.target.prop = TRUE")
            if spec["target_shares_height"] is not None:
                args.append(f"target.prop.height = {spec['target_shares_height']}")
        gap = start.get("gap")
        if gap is not None and not isinstance(gap, dict):
            args.append(f"small.gap = {gap:g}")
        if start.get("big_gap") is not None:
            args.append(f"big.gap = {start['big_gap']:g}")
        if start.get("same_size_groups"):
            args.append("scale = TRUE")
        reduce = spec["hide_groups_smaller_than"] if spec["hide_groups_smaller_than"] is not None else start.get(
            "hide_groups_smaller_than")
        if reduce is not None:
            args.append(f"reduce = {reduce:g}")
        if start.get("in_groups_of") is not None:
            sets = start["in_groups_of"]
            missing = [g for g in names if g not in sets]
            if missing:
                raise SimplydataError(f'.start_circle_chart(in_groups_of=...) gives no set for the group "{missing[0]}"'
                                      ": give every group a set, such as {\"" + missing[0] + "\": \"rows\"}.")
            values["group_sets"] = [str(sets[g]) for g in names]
            self._value_notes["group_sets"] = "the set each group belongs to (from in_groups_of=)"
            args.append("group = stats::setNames(group_sets, group_names)")
        if start.get("sizes") is not None:
            values["group_sizes"] = self._chord_sizes(names)
            self._value_notes["group_sizes"] = f'the size of each group (column "{start["sizes"]}")'
            args.append("xmax = stats::setNames(group_sizes, group_names)")
        track = []
        if not no_ring:
            track.append('"grid"')
        args.append(f"annotationTrack = {('c(' + ', '.join(track) + ')') if track else 'NULL'}")
        if not no_ring:
            args.append(f"annotationTrackHeight = {thickness}")
        if with_names:
            args.append(f"preAllocateTracks = list(track.height = {names_height})")
        args += self._link_options(spec, chord=True)
        out = ["  drawn <- circlize::chordDiagram(" + (",\n    ".join(args)) + ")"]
        if with_names:
            out.append("  circlize::circos.track(track.index = 1, bg.border = NA, panel.fun = function(x, y) {")
            out.append(f"    {name_text}")
            out.append("  })")
        out += ["  link_from_low <- drawn$x1 - abs(drawn$value1)", "  link_from_high <- drawn$x1",
                "  link_to_low <- drawn$x2 - abs(drawn$value2)", "  link_to_high <- drawn$x2",
                "  links_drawn <- list(from = as.character(drawn$rn), to = as.character(drawn$cn), "
                "strength = drawn$value1, colour = as.character(drawn$col))"]
        return out

    def _chord_sizes(self, names):
        frame = self._data
        around, sizes = self._start["around"], self._start["sizes"]
        if isinstance(sizes, list):
            raise SimplydataError(".start_circle_chart(sizes=...) of a chord diagram is one column (the size of each "
                                  "group), not a start and an end.")
        found = dict(zip(frame[around].astype(str), pd.to_numeric(frame[sizes], errors="coerce")))
        return [float(found[g]) for g in names]

    def _positions_sizes(self, names, link_frames):
        """(starts, ends) of the groups: from sizes= on start, else from 0 to the farthest place a link names."""
        start = self._start
        frame = self._data
        sizes = start.get("sizes")
        if sizes is not None:
            around = start["around"]
            firsts = frame.drop_duplicates(subset=[around])
            keyed = firsts.set_index(firsts[around].astype(str))
            if isinstance(sizes, list):
                lows = pd.to_numeric(keyed[sizes[0]], errors="coerce")
                highs = pd.to_numeric(keyed[sizes[-1]], errors="coerce")
            else:
                lows = pd.Series(0.0, index=keyed.index)
                highs = pd.to_numeric(keyed[sizes], errors="coerce")
            return [float(lows[g]) for g in names], [float(highs[g]) for g in names]
        ends = dict.fromkeys(names, 0.0)
        for links in link_frames:
            for side, high in (("from", "from_high"), ("to", "to_high")):
                for g, v in zip(links[side], links[high]):
                    ends[g] = max(ends[g], float(v))
        if self._links:
            print("Note: no sizes= given, so each group goes from 0 to the farthest place its links name.")
        return [0.0] * len(names), [ends[g] if ends[g] > 0 else 1.0 for g in names]

    def _positions_lines(self, names, values, with_names, names_height, thickness, no_ring, name_text):
        start = self._start
        link_frames = [self._bundle(spec, self._link_table(spec, names)) for spec in self._links]
        starts, ends = self._positions_sizes(names, link_frames)
        for links in link_frames:
            self._check_places(links, names, starts, ends)
        values["group_starts"], values["group_ends"] = starts, ends
        self._value_notes["group_starts"] = "where each group starts"
        self._value_notes["group_ends"] = "where each group ends" + (
            f' (column "{start["sizes"][-1] if isinstance(start["sizes"], list) else start["sizes"]}")'
            if start.get("sizes") is not None else "")
        init = ["factor(group_names, levels = group_names)", "xlim = cbind(group_starts, group_ends)"]
        widths = start.get("group_widths")
        if widths is not None:
            values["group_widths"] = self._widths(names, widths)
            self._value_notes["group_widths"] = "the share of the circle each group takes (from group_widths=)"
            init.append("sector.width = group_widths")
        out = ["  circlize::circos.initialize(" + ", ".join(init) + ")"]
        if with_names:
            out.append(f"  circlize::circos.track(ylim = c(0, 1), track.height = {names_height}, bg.border = NA, "
                       "panel.fun = function(x, y) {")
            out.append(f"    {name_text}")
            out.append("  })")
        if not no_ring:
            border = _r_text(start["outline_colour"]) if start.get("outline_colour") else "NA"
            out.append(f"  circlize::circos.track(ylim = c(0, 1), track.height = {thickness}, "
                       f"bg.col = group_colours, bg.border = {border})")
        if not self._links:
            out.append("  links_drawn <- list(from = character(0), to = character(0), strength = numeric(0), "
                       "colour = character(0))")
            out += ["  link_from_low <- numeric(0)", "  link_from_high <- numeric(0)", "  link_to_low <- numeric(0)",
                    "  link_to_high <- numeric(0)"]
            return out
        frames = []
        for spec, links in zip(self._links, link_frames):
            links = links.copy()
            links["colour"] = self._link_colours(spec, links, names, values["group_colours"])
            links["transparency"] = spec["transparency"]
            if spec["biggest_on_top"]:  # the widest links drawn last, on top
                links = links.assign(width=links["from_high"] - links["from_low"]).sort_values(
                    "width", kind="stable").drop(columns="width")
            frames.append(links)
        spec = self._links[0]
        self._say_route("Drawn as links between places (circlize circos.link): each link joins the places given "
                        "by from_between= and to_between=.")
        for name, column in (("links_from", "from"), ("links_to", "to")):
            values[name] = [g for f in frames for g in f[column]]
        for name, column in (("from_low", "from_low"), ("from_high", "from_high"), ("to_low", "to_low"),
                             ("to_high", "to_high")):
            values[name] = [float(v) for f in frames for v in f[column]]
        values["link_colours"] = [c for f in frames for c in f["colour"]]
        values["link_transparency"] = [float(v) for f in frames for v in f["transparency"]]
        self._value_notes.update({
            "links_from": f'the group each link starts at (column "{spec["links_from"]}")',
            "links_to": f'the group each link goes to (column "{spec["links_to"]}")',
            "from_low": f'where each link starts (column "{spec["from_between"][0]}")',
            "from_high": f'where the start of each link ends (column "{spec["from_between"][-1]}")',
            "to_low": f'where each link arrives (column "{spec["to_between"][0]}")',
            "to_high": f'where the end of each link ends (column "{spec["to_between"][-1]}")',
            "link_colours": "the colour of each link",
            "link_transparency": "how see-through each link is (transparency=)",
        })
        options = self._link_options(spec, chord=False)
        if spec["with_direction"]:
            options.append(f"directional = {2 if spec['with_direction'] == 'both ways' else 1}")
        each = ""
        if spec["with_jitter"]:
            rng = np.random.default_rng(spec["with_seed"])
            n = len(values["links_from"])
            base_bend = spec["bend"] if isinstance(spec["bend"], float) else 0.5
            base_sharp = spec["bend_sharpness"] if spec["bend_sharpness"] is not None else 1.0
            values["link_bend"] = [float(min(1.0, base_bend * f)) for f in rng.uniform(0.8, 1.2, n)]
            values["link_sharpness"] = [float(base_sharp * f) for f in rng.uniform(0.8, 1.2, n)]
            self._value_notes["link_bend"] = (f"how high each link rises: {base_bend:g} times a random factor from "
                                              f"0.8 to 1.2 (with_jitter=True, with_seed={spec['with_seed']})")
            self._value_notes["link_sharpness"] = (f"how sharp each link bends: {base_sharp:g} times a random factor "
                                                   f"from 0.8 to 1.2 (with_seed={spec['with_seed']})")
            print(f"Note: each link's curve varies a little (with_jitter=True, with_seed={spec['with_seed']}).")
            each = ", h.ratio = link_bend[i], w = link_sharpness[i]"
        extra = (", " + ", ".join(options)) if options else ""
        out += ["  link_colours <- circlize::add_transparency(link_colours, link_transparency)",
                "  inside <- circlize::get_most_inside_radius()",
                "  for (i in seq_along(links_from)) {",
                "    circlize::circos.link(links_from[i], c(from_low[i], from_high[i]), links_to[i], "
                f"c(to_low[i], to_high[i]), col = link_colours[i], rou = inside{each}{extra})",
                "  }",
                "  link_from_low <- from_low", "  link_from_high <- from_high", "  link_to_low <- to_low",
                "  link_to_high <- to_high",
                "  links_drawn <- list(from = links_from, to = links_to, strength = from_high - from_low, "
                "colour = link_colours)"]
        return out

    def _say_route(self, line):
        """The route used is printed once for each circle chart (decision Z8)."""
        if self.__dict__.get("_route_said") != line:
            print(line)
            self._route_said = line

    def _widths(self, names, widths):
        if isinstance(widths, dict):
            missing = [g for g in names if g not in widths]
            if missing:
                raise SimplydataError(f'.start_circle_chart(group_widths=...) gives no width for "{missing[0]}": '
                                      "give every group a width (shares of the circle, such as 0.25).")
            return [float(widths[g]) for g in names]
        frame = self._data
        around = self._start["around"]
        firsts = frame.drop_duplicates(subset=[around])
        found = dict(zip(firsts[around].astype(str), pd.to_numeric(firsts[widths], errors="coerce")))
        return [float(found[g]) for g in names]

    def _check_places(self, links, names, starts, ends):
        """Places outside their group are refused, with the rows (circlize would only warn)."""
        bounds = {g: (s, e) for g, s, e in zip(names, starts, ends)}
        bad = []
        for i, row in links.iterrows():
            for group, low, high in ((row["from"], row["from_low"], row["from_high"]),
                                     (row["to"], row["to_low"], row["to_high"])):
                s, e = bounds[group]
                if low < s or high > e:
                    bad.append(f"link {i + 1}: {low:g} to {high:g} on {group} (which goes from {s:g} to {e:g})")
        if bad:
            raise SimplydataError(".draw_links() has places outside their group:\n  " + "\n  ".join(bad[:5])
                                  + ("\n  ..." if len(bad) > 5 else "")
                                  + "\nCheck the columns of from_between= and to_between=, and sizes= on "
                                    "start_circle_chart().")

    def _bundle(self, spec, links):
        """bundled_when_closer_than=: links between the same two groups whose starts and ends both lie closer than
        the distance are joined into one, spanning them all (Circos bundlelinks, done in pandas)."""
        distance = spec["bundled_when_closer_than"]
        if distance is None:
            return links
        links = links.sort_values(["from", "to", "from_low", "to_low"], kind="stable").reset_index(drop=True)
        bundles = []
        for row in links.to_dict("records"):
            last = bundles[-1] if bundles else None
            if (last is not None and last["from"] == row["from"] and last["to"] == row["to"]
                    and row["from_low"] - last["from_high"] <= distance
                    and max(row["to_low"] - last["to_high"], last["to_low"] - row["to_high"]) <= distance):
                last["from_high"] = max(last["from_high"], row["from_high"])
                last["to_low"] = min(last["to_low"], row["to_low"])
                last["to_high"] = max(last["to_high"], row["to_high"])
                last["links in bundle"] += 1
                last["colour values"].append(row.get("colour_value"))
                continue
            bundles.append({**row, "links in bundle": 1, "colour values": [row.get("colour_value")]})
        for bundle in bundles:  # a bundle coloured by a column of numbers takes the average of its links
            found = bundle.pop("colour values")
            if "colour_value" in bundle and all(_is_number(v) for v in found):
                bundle["colour_value"] = float(np.mean(found))
        out = pd.DataFrame(bundles)
        print(f"Note: {len(links)} links joined into {len(out)} bundle{'s' if len(out) != 1 else ''} (ends closer "
              f"than {distance:g}, the same two groups); the count is kept as \"links in bundle\".")
        if isinstance(spec["colour"], tuple) and spec["colour"][0] == "column" and \
                spec["colour"][1] == "links in bundle":
            out["colour_value"] = out["links in bundle"]
        return out

    # ------------------------------------------------------------ friendly errors
    @classmethod
    def _word_names(cls) -> list[str]:
        return sorted(n for n in dir(cls) if not n.startswith("_") and callable(getattr(cls, n)))

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        raise other_name_error("chart", name, self._word_names()) or missing_word_error(name, self._word_names())

    def __repr__(self):
        what = ", ".join(f"links ({spec['route']})" for spec in self._links) or "no links yet"
        return f"<simplydata circle chart: {what}>"


# What circlize drew, read back in the same R program (circlize's own numbers: nothing is worked out again)
READ_BACK = [
    "  groups_drawn <- circlize::get.all.sector.index()",
    "  rings <- circlize::get.all.track.index()",
    "  cell <- function(name, k) vapply(groups_drawn, function(g) if (length(rings)) "
    "as.numeric(circlize::get.cell.meta.data(name, sector.index = g, track.index = rings[1]))[k] else NA_real_, 0)",
    "  list(group = groups_drawn, group_low = cell(\"xlim\", 1), group_high = cell(\"xlim\", 2),",
    "       start_degree = cell(\"cell.start.degree\", 1), end_degree = cell(\"cell.end.degree\", 1),",
    "       link_from = links_drawn$from, link_to = links_drawn$to, link_from_low = link_from_low,",
    "       link_from_high = link_from_high, link_to_low = link_to_low, link_to_high = link_to_high,",
    "       link_strength = links_drawn$strength, link_colour = links_drawn$colour)",
]

DRAWN_COLUMNS = ["part", "group", "to_group", "low", "high", "to_low", "to_high", "strength", "start_degree",
                 "end_degree", "colour"]


def drawn_table(found: dict) -> pd.DataFrame:
    """The table of get_numbers_drawn() from what the R program read back (also used by the underneath checks)."""
    def column(name):
        value = found.get(name)
        return [] if value is None else list(np.atleast_1d(value))

    groups = [str(g) for g in column("group")]
    links = [str(g) for g in column("link_from")]
    rows = []
    for i, g in enumerate(groups):
        rows.append(dict(part="group", group=g, to_group=None, low=float(column("group_low")[i]),
                         high=float(column("group_high")[i]), to_low=np.nan, to_high=np.nan, strength=np.nan,
                         start_degree=float(column("start_degree")[i]), end_degree=float(column("end_degree")[i]),
                         colour=None))
    for i, g in enumerate(links):
        rows.append(dict(part="link", group=g, to_group=str(column("link_to")[i]),
                         low=float(column("link_from_low")[i]), high=float(column("link_from_high")[i]),
                         to_low=float(column("link_to_low")[i]), to_high=float(column("link_to_high")[i]),
                         strength=float(column("link_strength")[i]), start_degree=np.nan, end_degree=np.nan,
                         colour=str(column("link_colour")[i])))
    return pd.DataFrame(rows, columns=DRAWN_COLUMNS)


# ---------------------------------------------------------------- the start word (on a table)
def start_circle_chart(table_data, around=None, sizes=None, names=None, in_order=None, gap=None, big_gap=None,
                       colour=None, outline_colour=None, thickness=None, with_names=True, text_size=None,
                       group_widths=None, same_size_groups=False, in_groups_of=None, hide_groups_smaller_than=None,
                       space_around_circle=None) -> CircleChart:
    """Check the options of table.start_circle_chart() and make the circle chart."""
    word = "start_circle_chart"
    frame = load(table_data)
    start: dict = {}
    if around is not None:
        start["around"] = _column(frame, around, "around", word)
    for option, value in (("sizes", sizes), ("names", names)):
        if value is None:
            continue
        if around is None:
            raise SimplydataError(f'.start_circle_chart() needs around= (the column of groups) with {option}=: '
                                  f'table.start_circle_chart(around="contig", {option}="length").')
        if option == "sizes" and is_listlike(value) and not isinstance(value, str):
            value = list(value)
            if len(value) != 2:
                raise SimplydataError('.start_circle_chart() needs sizes= as one column (the size of each group) or '
                                      'two (where each group starts and ends), such as sizes=["start", "end"].')
            for v in value:
                _column(frame, v, "sizes", word)
        else:
            _column(frame, value, option, word)
        start[option] = value
    if in_order is not None:
        if in_order != "natural" and not (is_listlike(in_order) and not isinstance(in_order, str)):
            raise SimplydataError('.start_circle_chart() needs in_order= as a list of the groups in order, or '
                                  f'"natural" (chr2 before chr10), not {in_order!r}.')
        start["in_order"] = in_order if in_order == "natural" else list(in_order)
    if gap is not None:
        if isinstance(gap, dict):
            fixed = {}
            for key, value in gap.items():
                if key != "between others" and not (isinstance(key, tuple) and len(key) == 2):
                    raise SimplydataError('.start_circle_chart() needs gap= as one value, or as a dict of pairs of '
                                          'groups next to each other, such as gap={("A", "B"): "10 degrees", '
                                          '"between others": "1 degree"}.')
                fixed[key if key == "between others" else (str(key[0]), str(key[1]))] = _degrees(value, "gap", word)
            start["gap"] = fixed
            if hide_groups_smaller_than is not None:
                raise SimplydataError(".start_circle_chart() cannot set the gap between named groups together with "
                                      "hide_groups_smaller_than= (the groups round the circle would change).")
        else:
            start["gap"] = _degrees(gap, "gap", word)
    if big_gap is not None:
        start["big_gap"] = _degrees(big_gap, "big_gap", word)
    from .words.look import check_colour

    if colour is not None:
        if isinstance(colour, dict):
            start["colour"] = ("dict", {str(k): _hex(check_colour(v, word)) for k, v in colour.items()})
        elif isinstance(colour, str) and colour in frame.columns:
            if around is None:
                raise SimplydataError(".start_circle_chart() needs around= with a column of colours, so each group "
                                      "takes the colour on its row.")
            start["colour"] = ("column", colour)
        else:
            start["colour"] = ("one", _hex(check_colour(colour, word)))
    if outline_colour is not None:
        start["outline_colour"] = _hex(check_colour(outline_colour, word))
    if thickness is not None:
        if _is_number(thickness) and float(thickness) == 0:
            start["thickness"] = "0"
        else:
            start["thickness"] = _height(thickness, "thickness", word)
    start["with_names"] = _switch(with_names, "with_names", word)
    if text_size is not None:
        if not (_is_number(text_size) and text_size > 0):
            raise SimplydataError(f".start_circle_chart() needs text_size= in points, such as 10, not {text_size!r}.")
        start["text_size"] = float(text_size)
    if group_widths is not None:
        if isinstance(group_widths, str):
            if around is None:
                raise SimplydataError(".start_circle_chart() needs around= with a column of group widths.")
            _column(frame, group_widths, "group_widths", word)
        elif not isinstance(group_widths, dict):
            raise SimplydataError('.start_circle_chart() needs group_widths= as a column or a dict such as '
                                  '{"chr1": 0.3, "chr2": 0.2}.')
        start["group_widths"] = group_widths
    start["same_size_groups"] = _switch(same_size_groups, "same_size_groups", word)
    if in_groups_of is not None:
        if not isinstance(in_groups_of, dict):
            raise SimplydataError('.start_circle_chart() needs in_groups_of= as a dict of each group\'s set, such as '
                                  '{"harbour": "sites", "blaTEM": "genes"}.')
        start["in_groups_of"] = {str(k): v for k, v in in_groups_of.items()}
    if hide_groups_smaller_than is not None:
        start["hide_groups_smaller_than"] = _share(hide_groups_smaller_than, "hide_groups_smaller_than", word,
                                                   high=0.5)
    if space_around_circle is not None:
        if not (_is_number(space_around_circle) and 0 <= space_around_circle <= 1):
            raise SimplydataError(".start_circle_chart() needs space_around_circle= as a share of the radius from 0 "
                                  f"to 1, such as 0.1, not {space_around_circle!r}.")
        start["space_around_circle"] = float(space_around_circle)
    return CircleChart(frame, start)
