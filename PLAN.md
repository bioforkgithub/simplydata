# simplydata — design plan

*Status: version 0.1.0 released; fitting, distributions and choosing parts by position are on main.*

## 1. The idea

simplydata is **a dictionary, not a new engine**. One small, plain-English vocabulary
that translates into the right calls in **matplotlib, seaborn, plotnine, pandas and NumPy**
(plus SciPy for statistics). Learn simplydata, and you never have to learn the five
libraries underneath.

Like a phrasebook that lets you speak Spanish, Italian and French without learning each
grammar.

- The libraries underneath do all drawing and calculation. **simplydata does not implement
  statistical methods itself**: every calculation is done by established, peer-reviewed
  packages (Python packages; R packages through rpy2 where Python has none), and simplydata
  translates simple words into those calls.
- simplydata's job is the **translation**: each word must map to the right call with the
  right settings. That is what we test.
- Users never need the libraries underneath; the manual shows the same work in them for anyone
  who wants to learn them ("The same underneath", tested against each word). There is still
  **no bridge** in the code (no `show_code()`, no `.matplotlib()`).

## 2. Goals

1. **Simple words, full power.** Every word is simple enough for a child to read, yet together
   they unlock the full power of the libraries underneath, for beginners and researchers alike.
2. **Learn everything in one day**, write programs the next day.
3. **The hardest plots are as easy as the simplest** (multi-panel figures, second
   y-axis, zoom inset, notes with arrows, small multiples, animation, polar, 3D).
4. **Better than seaborn and plotnine** for learners, while covering what they do.
5. Later: replace everyday use of pandas and NumPy as well (tables first, then arrays).

## 3. Basics

| Topic | Decision |
|---|---|
| Name | `simplydata`, used as `import simplydata as sdata` (name free on PyPI on 2026-11-12) |
| Licence | MIT, open on GitHub, contributions welcome |
| Python | 3.10 and newer |
| Audience | Everyone: beginners, students, teachers and researchers. "Simple enough for a school child to read" is the test for every word, not a limit on what it can do |
| Data | Plain lists, Excel/CSV files, pandas tables, Polars tables; results stay plain pandas/NumPy (or Polars, if Polars went in) |
| Speed | Automatic: Polars tables stay Polars, files over 100 MB use Polars, everything else pandas. Override in plain words: `fast=True`. A one-line message says when fast mode is used. |
| Style | One step per line on a chart; chaining also allowed |
| Look | Clean paper style by default (white, large text, colour-blind-safe colours) |
| Showing | Charts appear automatically in Jupyter/VS Code/Spyder; `chart.show()` in scripts |
| Saving | `chart.save("x.png")` or `chart.save("x.pdf")`, format from the file name |
| Spelling | Both `colour` and `color`, `grey` and `gray` |
| Errors | Friendly message, "did you mean …?", list of columns, link to request a missing word on GitHub |
| Learning | Built-in lessons `sdata.show_lesson(1)` … `sdata.show_lesson(20)`, `sdata.help("draw_bars")`, `sdata.show_all_words()` |
| Renaming | A renamed word or option keeps working for one release and prints one line, once per session: `Note: "remove_rows_with_empty_cells" is now called "remove_rows_with_empty_cells_in".` Old names are never listed in `sdata.show_all_words()`, the dictionary's word list or the lessons; `sdata.help("old_name")` points to the new one |

## 4. Grammar rules

A line of simplydata reads like an instruction said to the program: the object, then a verb
saying what it should do, then the details as options (`chart.draw_bars(x="name", y="marks")`,
`table.keep_rows_where("marks", is_above=50)`).

1. **Verb + what + where**: `write_title_on_top`, `write_caption_at_bottom`, `put_legend_at_bottom`,
   `draw_line_at_y`.
2. **Axes are `x` and `y`** (the words children learn in school maths).
3. Anything that belongs to one axis **ends in `_x` or `_y`**: `label_y`, `set_range_y`,
   `use_log_scale_y`, `put_ticks_x`.
4. **Mathematical terms keep their names**: log, histogram, density, polar (`take_log`,
   `draw_histogram`, `draw_density`, `draw_polar`).
5. Other jargon becomes plain words: `draw_dots` (scatter), `sideways=True` (horizontal bars).
6. Drawing two chart types on the same chart puts them on top of each other.

### Six patterns for the whole vocabulary

A user who knows one word of a pattern should be able to guess the others.

| # | Pattern | Examples |
|---|---|---|
| 1 | **verb + thing** changes a table or numbers: `keep_`, `remove_`, `add_`, `fill_`, `turn_`, `rename_`, `sort_` + rows / columns / cells / numbers, with a **glue word at the end** for the first input (`_where`, `_in`, `_that`); **`get_`** takes one piece out; **`take_`** does maths on every number; **`make_`** only makes something new; **`turn_into_`** gives the same data as another kind | `keep_rows_where`, `remove_columns`, `fill_empty_cells_in`, `remove_rows_with_empty_cells_in`, `fill_empty_numbers`, `keep_each_number_that`, `get_column`, `take_log`, `make_random_numbers`, `turn_into_numbers`, `turn_into_table` |
| 2 | **`draw_` + chart type**: `chart.draw_bars(...)` | `draw_bars`, `draw_histogram`, `draw_dots`, `draw_all_dots` |
| 3 | **verb + thing + where** places or sets something on a chart (`write_`, `put_`, `set_`, `use_`, `add_`); where = `top`/`bottom`/`left`/`right`/`x`/`y`/`at`/`between` | `write_title_on_top`, `label_y`, `label_colour_bar`, `draw_line_at_y`, `put_legend_at_bottom`, `set_range_y`, `use_colour("blue")`, `add_zoom_box(where="top right")` |
| 4 | **`find_` + measure + `_of`**(column, `for_each_group_in=`) for one column; **`find_` + relation + `_between`**(a, b) for two; **`compare_` + measure + `_of`** for tests between groups, **`compare_` + measure + `_to`** against one value | `find_median_of`, `find_correlation_between`, `compare_averages_of`, `compare_average_to` |
| 5 | **`show_` / `hide_` + thing** to look at something without changing it; the help words join it | `show_first_rows`, `show_grid`/`hide_grid`, `show_legend`/`hide_legend`, `show_steps`, `show_lesson`, `show_today` |
| 6 | **`as_` + library** hands the data to another Python tool; **`save`** writes a file, its type from the file name | `as_pandas`, `as_polars`, `as_numpy`; `table.save("clean.xlsx")`, `chart.save("marks.png")` |

**One option name, one meaning, everywhere:** `for_each_group_in=` (groups of a table), `in_each="row"` /
`"column"` (a grid's rows or columns), `colour=` (one colour,
or a colour per group), conditions start with `is_` (`is_above=`, `is_below=`, `is_at_least=`,
`is_at_most=`, `is_equal_to=`, `is_not_equal_to=`, `is_one_of=`, `is_between=[low, high]`,
`is_after=`, `is_before=`), `between=[low, high]` and `x_between=`/`y_between=` (every span),
switches start with `with_` (`with_dots=True`, `with_arrow=True`, `with_seed=1`), `of_kind=` (the kind of
data in a column), `checking_for=` (what agreement means: `"agreement"` or `"consistency"`),
`of_degree=`, `from_column=`, `with_value=`, `biggest_first=`, `per_row=` (charts in a row),
`columns=` (table columns only), `labelled=` (text on a line or band; `labeled=` works too),
`fast=`, `drawn_as=`. Measure names are the same wherever they appear: `"average"`, `"median"`,
`"total"`, `"count"`, `"smallest"`, `"biggest"`, `"standard deviation"`, `"standard error"`,
`"confidence interval"` (in `show=`, `error=`, `draw_error_bars` and the `find_..._of` words).
Summary words print their answer as one sentence, so a program needs no `print()`.

**The word names the idea.** The word says the question in plain words; help and the printed
result name the technical term ("Welch's t-test", "linear regression"), so a learner can follow
a paper's Methods section.

**Checklist for a new word:** can a user who has never seen it guess it from one sibling? If
not, rename it before it is released.

**Talking to the program.** A line of simplydata should read like an instruction you say to the program. A longer name is fine when it makes the line clearer read aloud. It is still Python code: the object, then what it should do, then the details as options. Old names keep working as other names for one release.

```python
import simplydata as sdata

chart = sdata.chart("marks.xlsx")
chart.draw_bars(x="name", y="marks")
chart.write_title_on_top("My class marks")
chart.label_x("Student")
chart.label_y("Marks")
chart.draw_line_at_y(50, labelled="pass mark")
chart.shade_between_y(40, 60)
chart.put_legend_at_bottom()
chart.save("marks.png")
```

## 5. Word list (draft v0.1)

### 5.1 Start, show, save
| Word | Example |
|---|---|
| `sdata.chart` | `chart = sdata.chart("marks.xlsx")` · `sdata.chart(table)` · `sdata.chart()` for lists |
| `show` | `chart.show()` |
| `save` | `chart.save("marks.png")` · `chart.save("marks.pdf")` |

### 5.2 Chart types
| Word | Example |
|---|---|
| `draw_bars` | `chart.draw_bars(x="name", y="marks")` · `stacked=True` · `sideways=True` |
| `draw_lines` | `chart.draw_lines(x="day", y="temp", colour="city")` |
| `draw_dots` | `chart.draw_dots(x="height", y="weight", size="age", shape="type")` |
| `draw_area` | `chart.draw_area(x="year", y="sales")` |
| `draw_histogram` | `chart.draw_histogram(x="marks", with_bins=10)` |
| `draw_boxes` | `chart.draw_boxes(x="class", y="marks")` |
| `draw_violins` | `chart.draw_violins(x="class", y="marks")` |
| `draw_heatmap` | `chart.draw_heatmap(with_numbers=True)` · `cluster=True` |
| `draw_pie` | `chart.draw_pie(labels="fruit", values="count")` |
| `draw_polar` | `chart.draw_polar(angle="direction", distance="speed")` |
| `draw_contour` | `chart.draw_contour(x="lon", y="lat", z="depth")` |
| `draw_surface` | `chart.draw_surface(x="lon", y="lat", z="depth")` |
| `draw_dots_3d` | `chart.draw_dots_3d(x="a", y="b", z="c")` |

### 5.3 Statistics
| Word | Example |
|---|---|
| `show=` | `chart.draw_bars(x="class", y="marks", show="average")` · `"median"` · `"total"` · `"count"` · `"smallest"` · `"biggest"` · `"standard deviation"` |
| `error=` | `error="standard deviation"` · `"standard error"` · `"confidence interval"` (`"sd"`, `"se"`, `"ci"` also work) |
| `draw_error_bars` | `chart.draw_error_bars("standard error")` · `chart.draw_error_bars(column="error")` |
| `fit_line` | `chart.fit_line()` · `with_confidence_band=True` · `show_equation=True` |
| `fit_curve` | `chart.fit_curve(of_degree=2)` |
| `draw_smooth_line` | `chart.draw_smooth_line()` |
| `draw_density` | `chart.draw_density(x="marks", colour="class")` |
| `draw_count_bars` | `chart.draw_count_bars(x="fruit")` |
| `draw_all_dots` | `chart.draw_all_dots(x="class", y="marks")` |
| `draw_side_histograms` | `chart.draw_side_histograms()` |
| `sdata.draw_all_pairs` | `sdata.draw_all_pairs(table)` |

### 5.4 Lines, shading, words
| Word | Example |
|---|---|
| `draw_line_at_x` / `draw_line_at_y` | `chart.draw_line_at_y(50, labelled="pass mark")` |
| `shade_between_x` / `shade_between_y` | `chart.shade_between_y(40, 60)` |
| `write_title_on_top` | `chart.write_title_on_top("My class marks")` |
| `write_caption_at_bottom` | `chart.write_caption_at_bottom("Data from 2026")` |
| `label_x` / `label_y` | `chart.label_y("Marks")` |
| `write_note` | `chart.write_note("Highest!", x=5, y=98, with_arrow=True)` |
| `write_numbers_on_bars` | `chart.write_numbers_on_bars()` |
| `use_font_size` | `chart.use_font_size(14)` |

### 5.5 Axes
| Word | Example |
|---|---|
| `set_range_x` / `set_range_y` | `chart.set_range_y(0, 100)` |
| `use_log_scale_x` / `use_log_scale_y` | `chart.use_log_scale_y()` |
| `put_ticks_x` / `put_ticks_y` | `chart.put_ticks_x(0, 10, 20, 30)` |
| `rotate_labels_x` | `chart.rotate_labels_x(45)` |
| `add_second_y` | `chart.add_second_y("rain", drawn_as="bars", labelled="Rain (mm)")` |
| `flip_y` | `chart.flip_y()` |

### 5.6 Colours and look
| Word | Example |
|---|---|
| `use_colour` / `use_color` | `chart.use_colour("blue")` · inside a chart: `colour="site"` |
| `use_colours` | `chart.use_colours("blue", "orange", "green")` |
| `use_style` | `chart.use_style("paper")` · `"school"` · `"dark"` · `"presentation"` |
| `set_size` | `chart.set_size(width=8, height=6)` |
| `show_grid` / `hide_grid` | `chart.hide_grid()` |
| `put_legend_at_top` / `_at_bottom` / `_on_left` / `_on_right` | `chart.put_legend_at_bottom()` |
| `hide_legend` / `show_legend` | `chart.hide_legend()` |
| `label_colour_bar` | `chart.label_colour_bar("Depth (m)")` |

### 5.7 Several charts and hard tricks
| Word | Example |
|---|---|
| `sdata.put_side_by_side` | `sdata.put_side_by_side(a, b).save("both.png")` |
| `sdata.put_one_above_other` | `sdata.put_one_above_other(a, b)` |
| `sdata.put_in_rows_and_columns` | `sdata.put_in_rows_and_columns(a, b, c, d, per_row=2, same_y=True, with_letters=True)` (`with_letters=True` writes A, B, C … on the panels; all three page words take it) |
| `draw_one_chart_for_each_group_in` | `chart.draw_one_chart_for_each_group_in("site", per_row=3)` · `draw_one_chart_for_each_group_in(down="site", across="year")` |
| `add_zoom_box` | `chart.add_zoom_box(x_between=[2, 4], y_between=[10, 20], where="top right")` |
| `animate` | `chart.animate(over="year")` then `chart.save("growth.gif")` |

### 5.8 Help and learning
| Word | Example |
|---|---|
| `sdata.show_lesson` | `sdata.show_lesson(1)` … `sdata.show_lesson(20)` |
| `sdata.help` | `sdata.help("draw_bars")` |
| `sdata.show_all_words` | `sdata.show_all_words()` prints the whole list |

## 6. Libraries underneath

| Library | Used for |
|---|---|
| matplotlib | Drawing, axes, layout, saving, animation |
| seaborn | Statistical charts (averages with error bars, density, violins, pairs, clustered heatmap) |
| plotnine | Grammar-style layered charts and two-way panels where it is the best fit |
| pandas | Reading files, tables, grouping (default for normal-sized data) |
| Polars | Fast engine for large data and Polars input; charts convert it to pandas before drawing |
| narwhals | Candidate helper so the same table code runs on both pandas and Polars |
| NumPy | Arrays and arithmetic |
| SciPy | t-based confidence intervals, curve fitting, KDE, clustering |

Design rule: each simplydata word translates to **one** library. seaborn draws on matplotlib
charts, so those two mix freely; plotnine builds its own charts, so words that use it must
not be mixed with matplotlib/seaborn words on the same chart. Which library each word uses
is decided per word.

## 7. Our responsibility

The libraries do the calculations. **We are responsible for correct translation**: choosing
the right function and settings for each word. Known traps:

- Standard deviation: NumPy defaults to population SD (n), pandas to sample SD (n−1).
  simplydata default: sample SD (n−1).
- Missing values: NumPy returns `nan`, pandas skips them. simplydata must choose and say so.
- Confidence intervals: seaborn bootstraps, a t-interval differs slightly. Default to be
  decided; the method is always stated.

Testing: every word gets a test that its output matches the library underneath, and
statistics are checked against SciPy, seaborn and R on reference data.

## 8. Releases

| Version | Content |
|---|---|
| v0.1 | Charts (sections 5.1–5.8), lessons 1–8, friendly errors |
| v0.1 (also) | Accept Polars tables as chart input |
| v0.2 | Tables: plain-word layer over pandas and Polars (read, clean, keep, group, summarise), with automatic engine choice and `fast=True` |
| v0.3 | Arrays: plain-word layer over NumPy; statistical tests in plain words (comparing averages, comparing counts, fitting formulas) over SciPy |
| v0.4 | More statistics: regression with several predictors, mixed models, survival curves, multiple-testing correction, power analysis, PCA and ordination |
| v0.4.x | Charts and statistics polish: colour scales, transparency, line thickness, tick formats, histogram options, 1:1 lines, Q-Q plots, cumulative share (ECDF), comparing spreads, Tukey pairs, goodness of fit, more summary measures, special maths functions (erf, gamma ...) inside formulas |
| v0.5 | Curve fitting and optimisation: fit any formula, find minima and maxima, solve equations; interpolation; probability distributions (`sdata.distribution`) (done) |
| v0.5.x | Choosing parts by position: rows, columns and cells by their place (counting from 1, both ends included), every n-th row, columns by kind or name pattern, replacing values by a condition; a printable dictionary of every word; the course "30 days of simplydata" (done) |
| Statistics I | Tests: effect sizes with intervals, 2x2 tables, agreement between raters, diagnostic accuracy, bootstrap and permutation tests, equivalence tests, one-sided tests |
| v0.6 | Signals, time series and control systems: smoothing, filtering, peaks, Fourier transforms, rolling averages, resampling dates; transfer functions and step responses |
| Statistics II | The full model family: ANOVA tables, extensions of generalised linear models, mixed models for yes/no answers and counts, GEE, model diagnostics |
| v0.7 | Multivariate statistics II, and Bayesian statistics (as an optional extra) |
| Statistics III | Survival II, meta-analysis, power analysis II, design of experiments, survey weights |
| v0.8 | Maths: areas under curves (integration), differential equations (ODEs), matrices and linear algebra, with SymPy |
| v0.9 | Tables and data handling: the remaining pandas and Polars tasks (row summaries, ordered categories, date arithmetic, choosing columns by a rule ...); SQL queries on tables (DuckDB); labelled arrays (xarray) |
| v0.10 | Numbers and arrays: the remaining NumPy tasks |
| v0.11 | Charts II: page layouts, insets, polar and 3D in full, arrows, colour maps and norms, chart.undo; interactive charts (Plotly) and maps (GeoPandas, Cartopy) |
| v0.12 | Images and networks: image processing with scikit-image (filters, labelling, measuring shapes) and graphs with NetworkX (shortest paths, connected parts) |

Goal: every task in pandas, Polars, NumPy, SciPy, matplotlib and seaborn has a simple simplydata word. Cells hold
one value each (lists inside cells are split into rows instead). Machine learning, deep learning and language models
belong to a separate future package.

