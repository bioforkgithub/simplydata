"""Circular plots, batch 1 (approved by Manish 2026-11-27): the circle chart words and the options that change what
circlize is asked to do, on the made-up practice table "resistome" (which genes at which sites, as a chord diagram).

How a circle chart is compared. A circle chart is drawn by R circlize, so both sides are R: the simplydata side runs
the word (which writes and runs its own circlize program) and reads back what circlize drew with
circle_chart.get_numbers_drawn(); the library side is circlize code written by hand, which reads back the same
numbers from circlize itself: the groups (get.all.sector.index), where each group lies (get.cell.meta.data "xlim")
and where it starts and ends round the circle (cell.start.degree, cell.end.degree), and for each link the two
groups, its places on them, its strength and the colour drawn (the table chordDiagram gives back). The two tables
are compared value by value (compare="table"): the layout circlize worked out, not pixels. Both draw on R's null
pdf device, so nothing is written.
"""

import textwrap

from . import Entry

NEW_LINE = "\n"
GENES = '["blaTEM", "blaCTXM", "sul1", "tetA"]'
START = """
            table = sdata.get_example("resistome")
            genes_table = table.gather_into_rows(columns={genes}, names_to="gene", values_to="copies")
"""
# The links of the chord diagram, as the R side gets them (the same rows as gather_into_rows, as pandas melt)
LINKS = f"""
    import numpy as np
    import pandas as pd
    df = pd.read_csv("resistome.csv")
    long = df.melt(id_vars=["site", "temperature"], value_vars={GENES}, var_name="gene", value_name="copies")
    links_from = long["site"].to_numpy(dtype=object)
    links_to = long["gene"].to_numpy(dtype=object)
    strength = long["copies"].to_numpy(dtype=float)
    temperature = long["temperature"].to_numpy(dtype=float)
    okabe_ito = np.array(["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"],
                         dtype=object)
"""
# What circlize drew, read back on the R side (as circle_chart.get_numbers_drawn() reads it)
READ_BACK = """
g <- circlize::get.all.sector.index()
m <- function(n, k) sapply(g, function(s) circlize::get.cell.meta.data(n, s, 1)[k])
out <- list(group = g, low = m("xlim", 1), high = m("xlim", 2), start = m("cell.start.degree", 1),
  end = m("cell.end.degree", 1), link_from = d$rn, link_to = d$cn, from_low = d$x1 - abs(d$value1),
  from_high = d$x1, to_low = d$x2 - abs(d$value2), to_high = d$x2, strength = d$value1, colour = d$col)
circlize::circos.clear(); invisible(grDevices::dev.off()); out
"""
# The same table as get_numbers_drawn(), made from what R gave back
TABLE = """
import numpy as np
import pandas as pd
groups = pd.DataFrame({"part": "group", "group": group, "to_group": None, "low": low, "high": high,
                       "to_low": np.nan, "to_high": np.nan, "strength": np.nan, "start_degree": start,
                       "end_degree": end, "colour": None})
links = pd.DataFrame({"part": "link", "group": link_from, "to_group": link_to, "low": from_low,
                      "high": from_high, "to_low": to_low, "to_high": to_high, "strength": strength,
                      "start_degree": np.nan, "end_degree": np.nan, "colour": colour})
pd.concat([groups, links], ignore_index=True)
"""
NOTE = ("Python has no circular-plot package that draws chord diagrams and circos-style tracks as circlize does (and "
        "no other package matches circlize's layout), so simplydata calls R circlize itself.")
ALSO = ("simplydata also writes one R program for the whole picture (circle_chart.show_steps() prints it, with the "
        "data as variable names), opens the picture device itself (the file you name, or none), clears circlize "
        "before and after, and refuses unknown groups with the rows.")


def _ours(body: str, start: str = "genes_table.start_circle_chart()") -> str:
    lines = textwrap.dedent(body).strip(NEW_LINE).splitlines()
    return (START.format(genes=GENES) + f"            circle_chart = {start}" + NEW_LINE
            + "".join("            " + line + NEW_LINE for line in lines)
            + "            circle_chart.get_numbers_drawn()" + NEW_LINE)


def _r(comment: str, *parts: str) -> str:
    """The R block: what it does (a comment naming the word), the null device and circlize cleared, the drawing
    lines, then the read-back."""
    lines = [comment, "pdf(NULL); circlize::circos.clear()"]
    lines += [textwrap.dedent(part).strip(NEW_LINE) for part in parts]
    lines.append(READ_BACK.strip(NEW_LINE))
    return NEW_LINE.join(lines)


def _chord(*extra: str, mark: str = "", colours: str = "okabe_ito[seq_along(groups)]") -> str:
    """The chord diagram on the R side: circlize chordDiagram with the groups' colours, and the arguments given."""
    args = ", ".join((f"grid.col = setNames({colours}, groups)",) + extra)
    return NEW_LINE.join(["groups <- union(links_from, links_to)",
                          "d <- circlize::chordDiagram(data.frame(links_from, links_to, strength),",
                          f"  {args})" + (f"   # {mark}" if mark else "")])


def _entry(word, ours, r_code, option="", choices=(), also=ALSO, r_inputs=LINKS, data="resistome"):
    return Entry(word=word, option=option, data=data, ours=ours, code={"R": r_code, "Python": TABLE},
                 r_inputs=r_inputs, r_packages=("circlize",), compare="table", tolerance=1e-9, choices=choices,
                 python_note=NOTE, also=also)


COLOURS = ("the groups take simplydata's colour-blind-safe Okabe-Ito colours, in order (circlize's own default is "
           "random colours from rand_color, different on every run); each link takes the colour of the group it "
           "starts at, half see-through (transparency 0.5, circlize's default).",)
SITES = """
    import numpy as np
    import pandas as pd
    df = pd.read_csv("resistome.csv")
    sample = df["sample"].to_numpy(dtype=object)
    reads = df["reads"].to_numpy(dtype=float)
    okabe_ito = np.array(["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"],
                         dtype=object)
"""
# links between places on two contigs (made-up numbers, written out on both sides)
PLACES_OURS = """
            contigs_table = sdata.table({"contig": ["chromosome", "plasmid"], "length": [5000, 1200]})
            hits_table = sdata.table({"query": ["chromosome", "chromosome", "plasmid"], "qstart": [100, 3000, 10],
                                      "qend": [400, 3500, 300], "subject": ["plasmid", "plasmid", "chromosome"],
                                      "sstart": [200, 800, 4000], "send": [500, 1100, 4300]})
            circle_chart = contigs_table.start_circle_chart(around="contig", sizes="length")
            circle_chart.draw_links(from_table=hits_table, links_from="query", links_to="subject",
                                    from_between=["qstart", "qend"], to_between=["sstart", "send"])
            circle_chart.get_numbers_drawn()
"""
PLACES = """
    import numpy as np
    contig = np.array(["chromosome", "plasmid"], dtype=object)
    length = np.array([5000.0, 1200.0])
    query = np.array(["chromosome", "chromosome", "plasmid"], dtype=object)
    subject = np.array(["plasmid", "plasmid", "chromosome"], dtype=object)
    qstart, qend = np.array([100.0, 3000.0, 10.0]), np.array([400.0, 3500.0, 300.0])
    sstart, send = np.array([200.0, 800.0, 4000.0]), np.array([500.0, 1100.0, 4300.0])
    okabe_ito = np.array(["#0072B2", "#E69F00"], dtype=object)
"""
NO_LINKS = NEW_LINE.join(["d <- list(rn = character(0), cn = character(0), x1 = numeric(0), x2 = numeric(0),",
                          "          value1 = numeric(0), value2 = numeric(0), col = character(0))"])
SCALE = """
    from matplotlib import colors as mcolors
    scale = mcolors.LinearSegmentedColormap.from_list("white to navy", ["white", "navy"])
    norm = mcolors.Normalize(temperature.min(), temperature.max())
    scale_colours = np.array([mcolors.to_hex(scale(norm(v))) for v in temperature], dtype=object)
"""
LINKS_LINE = 'circle_chart.draw_links(links_from="site", links_to="gene", strength="copies"'
SITES_START = """
              table = sdata.get_example("resistome")
              circle_chart = table.start_circle_chart(around="site")
"""

ENTRIES = [
    _entry("table.start_circle_chart",
           """
               table = sdata.get_example("resistome")
               circle_chart = table.start_circle_chart(around="sample", sizes="reads")
               circle_chart.get_numbers_drawn()
           """,
           _r('# start_circle_chart(around="sample", sizes="reads")',
              "circlize::circos.par(cell.padding = c(0, 0, 0, 0))",
              "circlize::circos.initialize(factor(sample, levels = sample), xlim = cbind(0, reads))   # (1)",
              NEW_LINE.join(["circlize::circos.track(ylim = c(0, 1), track.height = circlize::mm_h(2),",
                             "  bg.col = rep_len(okabe_ito, length(sample)), bg.border = NA)   # (2)"]), NO_LINKS),
           choices=("one group for each value of around=, in the order the table first gives them, each from 0 to "
                    "its size in sizes= (circlize circos.initialize with xlim).",
                    "the group ring takes simplydata's colour-blind-safe Okabe-Ito colours, repeated when there are "
                    "more groups than colours (with a note)."),
           r_inputs=SITES),
    _entry("table.start_circle_chart", _ours(LINKS_LINE + ")", "genes_table.start_circle_chart(gap=0.02)"),
           _r("# start_circle_chart(gap=0.02): a share of the circle, in degrees for circlize",
              _chord("small.gap = 0.02 * 360")),
           option="gap="),
    _entry("circle_chart.draw_links", _ours(LINKS_LINE + ")"),
           _r('# draw_links(links_from="site", links_to="gene", strength="copies")', _chord(mark="(1)")),
           choices=COLOURS),
    _entry("circle_chart.draw_links", PLACES_OURS,
           _r('# draw_links(from_between=["qstart", "qend"], to_between=["sstart", "send"])',
              "circlize::circos.par(cell.padding = c(0, 0, 0, 0))",
              "circlize::circos.initialize(factor(contig, levels = contig), xlim = cbind(0, length))",
              "circlize::circos.track(ylim = c(0, 1), track.height = circlize::mm_h(2), bg.col = okabe_ito)",
              "col <- circlize::add_transparency(okabe_ito[match(query, contig)], 0.5)",
              NEW_LINE.join(["for (i in seq_along(query)) circlize::circos.link(query[i], c(qstart[i], qend[i]),",
                             "  subject[i], c(sstart[i], send[i]), col = col[i], rou = circlize::get_most_inside_radius())"
                             "   # (1)"]),
              NEW_LINE.join(["d <- list(rn = query, cn = subject, x1 = qend, x2 = send, value1 = qend - qstart,",
                             "          value2 = send - sstart, col = col)"])),
           option="from_between=", data=None, r_inputs=PLACES,
           choices=("each link is drawn with circlize circos.link from its start place to its end place, at the "
                    "inside edge of the innermost ring; places outside their group are refused with the rows "
                    "(circlize would only warn).",)),
    _entry("circle_chart.draw_links", _ours(LINKS_LINE + ', with_direction=True, direction_drawn_as="arrows")'),
           _r('# draw_links(..., with_direction=True, direction_drawn_as="arrows")',
              _chord('directional = 1, direction.type = "arrows"')),
           option="with_direction="),
    _entry("circle_chart.draw_links", _ours(LINKS_LINE + ', links_ordered_by="strength")'),
           _r('# draw_links(..., links_ordered_by="strength")', _chord("link.sort = TRUE")),
           option="links_ordered_by="),
    _entry("circle_chart.draw_links", _ours(LINKS_LINE + ', colour="temperature", split_colours_at=12)'),
           _r('# draw_links(..., colour="temperature", split_colours_at=12)',
              _chord('col = ifelse(temperature < 12, "#2166AC", "#B2182B")', mark="(1)")),
           option="split_colours_at=",
           choices=("below the split: ColorBrewer's RdBu blue (#2166AC); at or above it: its red (#B2182B), both "
                    "safe for colour-blind readers; use_colour_scale(...) gives the two ends of another scale.",)),
    _entry("circle_chart.use_colours",
           _ours(LINKS_LINE + ")" + NEW_LINE + 'circle_chart.use_colours("teal", "orange", "purple", "grey")'),
           _r('# use_colours("teal", "orange", "purple", "grey"): the colours repeat round the groups',
              _chord(colours='rep_len(c("#008080", "#FFA500", "#800080", "#808080"), length(groups))')),
           also="simplydata (matplotlib) turns the colour names into codes and hands circlize the list; the same "
                "colours go to a column of words given as colour= in draw_links. " + ALSO),
    _entry("circle_chart.use_colour_scale",
           _ours(LINKS_LINE + ', colour="temperature")' + NEW_LINE + 'circle_chart.use_colour_scale("white", "navy")'),
           _r('# draw_links(..., colour="temperature") with use_colour_scale("white", "navy")',
              _chord("col = scale_colours", mark="(1)")),
           r_inputs=LINKS + SCALE,
           choices=("matplotlib makes the colours (a scale from the lowest to the highest number, as on every "
                    "simplydata chart) and hands circlize the list (decision B3: circlize's colorRamp2 is not "
                    "used).",)),
    Entry(word="circle_chart.set_size",
          ours=SITES_START + '              circle_chart.set_size(width=12, height=12, unit="cm")' + NEW_LINE,
          compare="none",
          note="The size goes to R's picture device in inches (centimetres divided by 2.54), as svg(width=, height=) "
               "in R; circlize fits the circle to the device, so nothing else changes."),
    _entry("circle_chart.rotate", _ours(LINKS_LINE + ")" + NEW_LINE + "circle_chart.rotate(by_degrees=90)"),
           _r("# rotate(by_degrees=90): circlize's start.degree", "circlize::circos.par(start.degree = 90)",
              _chord())),
    _entry("circle_chart.flip_x", _ours(LINKS_LINE + ")" + NEW_LINE + "circle_chart.flip_x()"),
           _r("# flip_x(): the groups go round anticlockwise", "circlize::circos.par(clock.wise = FALSE)", _chord())),
    Entry(word="circle_chart.save",
          ours="""
              import os
              import tempfile
""" + SITES_START + '              circle_chart.save(os.path.join(tempfile.gettempdir(), "simplydata_sites.svg"))'
          + NEW_LINE,
          compare="none",
          note="R circlize draws straight into the file you name: simplydata opens R's svg(), pdf() or png() device "
               "on exactly that file (the one place in simplydata that opens a picture device), runs the circlize "
               "program, and closes the device with dev.off(); nothing else is written."),
    Entry(word="circle_chart.show", ours=SITES_START + "              circle_chart.show()" + NEW_LINE, compare="none",
          note="R circlize draws a PNG into a private temporary folder, simplydata reads it and deletes the folder, "
               "then shows the picture (in a notebook below the cell, elsewhere in a window)."),
    Entry(word="circle_chart.show_steps", ours=SITES_START + "              circle_chart.show_steps()" + NEW_LINE,
          compare="none",
          note="simplydata's own: it prints the circlize program it runs, with your data as R variable names (never "
               "the values), so the picture can be drawn again in R without simplydata."),
    _entry("circle_chart.get_numbers_drawn", _ours(LINKS_LINE + ")"),
           _r("# get_numbers_drawn(): what circlize drew, read back", _chord())),
]
