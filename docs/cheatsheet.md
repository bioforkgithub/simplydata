# simplydata cheat sheet

Every word on one page. Table words are steps on a table, for looking at data, cleaning
it and summing it up; chart words are steps on a chart:

```python
import simplydata as sdata
table = sdata.table(sdata.get_example("marks"))   # or sdata.table("my_file.xlsx")
table.keep_rows_where("marks", is_above=50)
table.find_average_of("marks", for_each_group_in="class")   # says the answer in a sentence
table.save("good_marks.xlsx")
chart = table.start_chart()                   # or sdata.chart(table), sdata.chart("my_file.xlsx")
chart.draw_bars(x="class", y="marks", error="standard error")
chart.write_title_on_top("Good marks")
chart.save("marks.png")
```

Number words are steps on a list (or a grid) of numbers:

```python
nums = sdata.numbers([12, 15, 9, 20, 14])
bigger = nums * 2                       # symbols make new numbers
nums.keep_each_number_that(is_above=10)             # words change the numbers (undo() takes it back)
nums.find_average()
grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
```

In Python, `sdata.help("draw_bars")` explains any word, `sdata.show_all_words()` prints this list and
`sdata.show_lesson(1)` starts the one-day course (lessons 9 to 12 are about tables, lesson 13
about numbers, lesson 14 about statistical tests, lesson 15 puts it all together, and lessons 16 to 25
go further: models, patterns, survival, fitting curves, finding and solving, distributions, checking
a model, time series, forecasts, cycles and systems). System words are steps on a system:
`system = sdata.system("1 / (s**2 + 2*s + 5)")`.

Every example runs as written on the practice table in the *Table* column:
for example `weather = sdata.get_example("weather")` then `chart = sdata.chart(weather)`,
or `table = sdata.table(sdata.get_example("weather"))` for table words.
Number words use `nums = sdata.numbers([12, 15, 9, 20, 14])` and grid words
`grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])`; `sdata.help("word")` shows each example ready to run.
Steps such as `fit_line` or `write_title_on_top` go after a chart step such as `chart.draw_dots(...)`,
and `a`, `b` in `sdata.put_side_by_side(a, b)` are charts you made first.

*This file is made by `docs/make_cheatsheet.py`. Do not edit it by hand.*

## Start, show and save

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.chart` | `sdata.chart(sdata.get_example("marks"))` |  | Start a chart. |
| `sdata.get_example` | `sdata.get_example("marks")` |  | A small made-up table to practise with. |
| `show` | `chart.show()` |  | Show the chart in a window. |
| `save` | `chart.save("marks.png")` |  | Save the chart. |

## Chart types

| Word | Example | Table | What it does |
|---|---|---|---|
| `draw_bars` | `chart.draw_bars(x="name", y="marks")` |  | Bars. |
| `draw_lines` | `chart.draw_lines(x="month", y="temperature", colour="city")` |  | Lines. |
| `draw_dots` | `chart.draw_dots(x="hours", y="marks")` |  | Dots (a scatter chart). |
| `draw_area` | `chart.draw_area(x="year", y="population", colour="country")` |  | A line with the space under it coloured in. |
| `draw_histogram` | `chart.draw_histogram(x="marks", with_bins=10)` |  | Bars that count how many values fall in each range. |
| `draw_boxes` | `chart.draw_boxes(x="class", y="marks")` |  | Boxes that show the middle half of the values and the median. |
| `draw_violins` | `chart.draw_violins(x="class", y="marks")` |  | Shapes that are wide where many values are. |
| `draw_heatmap` | `chart.draw_heatmap(x="month", y="city", value="rain", with_numbers=True)` |  | A grid of coloured squares, one colour for each number. |
| `draw_pie` | `chart.draw_pie(labels="fruit", values="count")` |  | A circle cut into slices, one slice per group. |
| `draw_polar` | `chart.draw_polar(angle="wind_direction", distance="wind_speed", colour="city")` |  | Dots on a round chart: how far round, and how far out. |
| `draw_contour` | `chart.draw_contour(x="east", y="north", z="height")` |  | A map where each colour band joins places with the same height. |
| `draw_surface` | `chart.draw_surface(x="east", y="north", z="height")` |  | A 3D landscape: z= is how high the ground is. |
| `draw_dots_3d` | `chart.draw_dots_3d(x="hours", y="height", z="marks", colour="class")` |  | Dots floating in a 3D box. |
| `draw_band` | `chart.draw_band(x="month", between=["lowest", "highest"])` |  | A shaded band between a low and a high column, along x. |
| `draw_map_of_empty_cells` | `chart.draw_map_of_empty_cells()` |  | A map of the empty cells: one row of the chart for each row of the table, one strip for each column, with empty cells coloured. |
| `sticks` | `chart.sticks(x="month_number", y="rain", colour="city")` |  | A thin line from 0 up (or down) to each value, with a dot on top (a stem chart). |

## Statistics

| Word | Example | Table | What it does |
|---|---|---|---|
| `show=` | `chart.draw_bars(x="class", y="marks", show="median")` |  | What each bar or point on a line stands for, when a group has many rows. |
| `error=` | `chart.draw_bars(x="class", y="marks", error="standard deviation")` |  | Error bars on top of averages: how spread out, or how sure, the values are. |
| `draw_error_bars` | `chart.draw_error_bars("standard error")` |  | Error bars on dots or lines. |
| `fit_line` | `chart.fit_line()` |  | A straight line that fits the dots best (linear regression). |
| `fit_curve` | `chart.fit_curve(of_degree=2)` |  | A curve that fits the dots best. |
| `fit_formula` | `chart.fit_formula("population = a * exp(b * (year - 2000))")` |  | The curve of a formula fitted to the dots. |
| `fit_distribution` | `chart.fit_distribution("normal")` |  | The best-fitting distribution's curve over a histogram or density chart. |
| `draw_curve` | `chart.draw_curve("y = 100 * exp(-0.3 * x)", between=[0, 10])` |  | Draw a formula, or a distribution, as a curve. |
| `draw_smooth_line` | `chart.draw_smooth_line()` |  | A smooth line that follows the dots (LOWESS). |
| `draw_density` | `chart.draw_density(x="marks", colour="class")` |  | A smooth curve that is high where many values are. |
| `draw_count_bars` | `chart.draw_count_bars(x="fruit", colour="shop")` |  | Bars that count how many rows each group has. |
| `draw_all_dots` | `chart.draw_all_dots(x="class", y="marks")` |  | Every value as a dot, spread out so no dot hides another. |
| `draw_side_histograms` | `chart.draw_side_histograms()` |  | Small histograms along the top and right edges of a dots chart. |
| `draw_qq_dots` | `chart.draw_qq_dots("marks")` |  | Dots that lie on a straight line when the values follow a normal (bell) curve. |
| `draw_cumulative_share` | `chart.draw_cumulative_share(x="marks", colour="class")` |  | A line that climbs from 0 to 1: the share of values at or below each x. |
| `forest_plot` | `chart.forest_plot(x="difference", y="group 1")` |  | Many results with their intervals, one line each (a forest plot). |
| `sdata.draw_all_pairs` | `sdata.draw_all_pairs(sdata.get_example("marks"), colour="class")` |  | Every number column against every other. |

## Lines and shading

| Word | Example | Table | What it does |
|---|---|---|---|
| `draw_line_at_x` | `chart.draw_line_at_x(2010, labelled="2010")` |  | A straight up-and-down line at one x value. |
| `draw_line_at_y` | `chart.draw_line_at_y(50, labelled="pass mark")` |  | A straight side-to-side line at one y value. |
| `draw_line_with_slope` | `chart.draw_line_with_slope(1, through=(0, 0))` |  | A straight line with a given slope, right across the chart. |
| `shade_between_x` | `chart.shade_between_x(6, 8)` |  | Shade the band between two x values, behind the data. |
| `shade_between_y` | `chart.shade_between_y(40, 60)` |  | Shade the band between two y values, behind the data. |

## Words on the chart

| Word | Example | Table | What it does |
|---|---|---|---|
| `write_title_on_top` | `chart.write_title_on_top("My class marks")` |  | A title above the chart. |
| `write_caption_at_bottom` | `chart.write_caption_at_bottom("Data from 2026")` |  | A small line of text under the whole chart. |
| `label_x` | `chart.label_x("Student")` |  | The name under the x-axis. |
| `label_y` | `chart.label_y("Marks")` |  | The name beside the y-axis. |
| `write_note` | `chart.write_note("Biggest", x=2024, y=49)` |  | A note on the chart at a place x, y. |
| `write_numbers_on_bars` | `chart.write_numbers_on_bars()` |  | Write the value of each bar on it. |
| `write_names_on_dots` | `chart.write_names_on_dots("name")` |  | Write a name next to each dot. |
| `use_font_size` | `chart.use_font_size(14)` |  | Make all the text bigger or smaller. |
| `use_font` | `chart.use_font("DejaVu Serif")` |  | The font for all the text on the chart. |

## Axes

| Word | Example | Table | What it does |
|---|---|---|---|
| `set_range_x` | `chart.set_range_x(0, 10)` |  | From where to where the x-axis goes. |
| `set_range_y` | `chart.set_range_y(0, 100)` |  | From where to where the y-axis goes. |
| `use_log_scale_x` | `chart.use_log_scale_x()` |  | A log scale on the x-axis: 1, 10, 100, 1000 are evenly spaced. |
| `use_log_scale_y` | `chart.use_log_scale_y()` |  | A log scale on the y-axis: 1, 10, 100, 1000 are evenly spaced. |
| `put_ticks_x` | `chart.put_ticks_x(1, 4, 7, 10)` |  | Where the marks on the x-axis go. |
| `put_ticks_y` | `chart.put_ticks_y(0, 50, 100)` |  | Where the marks on the y-axis go. |
| `rotate_labels_x` | `chart.rotate_labels_x()` |  | Turn the names under the x-axis so long ones do not bump into each other. |
| `rotate_labels_y` | `chart.rotate_labels_y(30)` |  | Turn the names beside the y-axis. |
| `write_ticks_x_as` | `chart.write_ticks_x_as("thousands")` |  | How the numbers or dates under the x-axis are written. |
| `write_ticks_y_as` | `chart.write_ticks_y_as("percent")` |  | How the numbers beside the y-axis are written. |
| `add_second_y` | `chart.add_second_y("rain", drawn_as="bars", labelled="Rain (mm)")` |  | A second y-axis on the right, for a column measured in other units. |
| `flip_x` | `chart.flip_x()` |  | Turn the x-axis around, so numbers grow from right to left. |
| `flip_y` | `chart.flip_y()` |  | Turn the y-axis upside down, for example for depth going down. |

## Colours and look

| Word | Example | Table | What it does |
|---|---|---|---|
| `use_colour` (also `use_color`) | `chart.use_colour("blue")` |  | One colour for the whole chart. |
| `use_colours` (also `use_colors`) | `chart.use_colours("blue", "orange", "green")` |  | Your own colours for the groups, in order. |
| `use_colour_scale` (also `use_color_scale`) | `chart.use_colour_scale("magma")` |  | The colours for numbers on a heatmap, contour map, surface or dots coloured by a number column. |
| `use_style` | `chart.use_style("school")` |  | The overall look. |
| `set_size` | `chart.set_size(width=17, height=12, unit="cm")` |  | The size of the chart. |
| `show_grid` | `chart.show_grid()` |  | Grid lines across the chart in both directions. |
| `hide_grid` | `chart.hide_grid()` |  | No grid lines. |
| `put_legend_at_top` (also `put_legend_on_top`) | `chart.put_legend_at_top()` |  | The legend above the chart, in one row. |
| `put_legend_at_bottom` (also `put_legend_on_bottom`) | `chart.put_legend_at_bottom()` |  | The legend below the chart, in one row under the x-axis name. |
| `put_legend_on_left` (also `put_legend_at_left`) | `chart.put_legend_on_left()` |  | The legend to the left of the chart. |
| `put_legend_on_right` (also `put_legend_at_right`) | `chart.put_legend_on_right()` |  | The legend to the right of the chart, outside the plot. |
| `hide_legend` | `chart.hide_legend()` |  | No legend. |
| `show_legend` | `chart.show_legend()` |  | The legend in its usual place, for example after hide_legend(). |
| `label_legend` | `chart.label_legend("Class")` |  | The name above the legend. |
| `label_colour_bar` (also `label_color_bar`) | `chart.label_colour_bar("Height (m)")` |  | The name beside the colour bar of a heatmap or contour. |

## Order of groups

| Word | Example | Table | What it does |
|---|---|---|---|
| `order_x` | `chart.order_x("C", "B", "A")` |  | Put the groups along the x-axis in your order. |
| `order_y` | `chart.order_y("C", "B", "A")` |  | Put the groups along the y-axis in your order, the first at the top. |
| `order_legend` | `chart.order_legend("Science", "Maths", "English")` |  | Put the colour groups in your order: in the legend, the colours and side by side. |

## Several charts

| Word | Example | Table | What it does |
|---|---|---|---|
| `draw_one_chart_for_each_group_in` | `chart.draw_one_chart_for_each_group_in("class", per_row=3)` |  | One small chart for each group. |
| `sdata.put_side_by_side` | `sdata.put_side_by_side(a, b)` |  | Charts next to each other. |
| `sdata.put_one_above_other` | `sdata.put_one_above_other(a, b)` |  | Charts on top of each other. |
| `sdata.put_in_rows_and_columns` | `sdata.put_in_rows_and_columns(a, b, c, d, per_row=2)` |  | Charts in rows and columns. |
| `add_zoom_box` | `chart.add_zoom_box(x_between=[2, 4], y_between=[40, 60])` |  | A small box showing part of the chart close up. |
| `animate` | `chart.animate(over="year")` |  | A moving chart with one picture for each value of a column. |

## Tables: start and look

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.table` | `sdata.table(sdata.get_example("marks"))` |  | Start a table. |
| `show_first_rows` | `table.show_first_rows(5)` |  | Show the first rows, numbered from 1. |
| `show_last_rows` | `table.show_last_rows(5)` |  | Show the last rows, with their row numbers in the whole table. |
| `show` | `table.show()` |  | Show the table, every row and every column (or only the first rows=). |
| `get_column_names` | `table.get_column_names()` |  | The names of all columns. |
| `describe_columns` | `table.describe_columns()` |  | Describe every column: its kind, empty cells, smallest, biggest and average. |
| `get_column` | `table.get_column("marks")` |  | One column on its own: a column of numbers becomes sdata.numbers, any other a plain list. |
| `get_row` | `table.get_row(3)` |  | One row as a plain dict of column: value, counting from 1. |
| `get_cell_at` | `table.get_cell_at(row=3, column="marks")` |  | The value in one cell: a row counting from 1 and a column by name. |

## Choose columns

| Word | Example | Table | What it does |
|---|---|---|---|
| `keep_columns` | `table.keep_columns("name", "marks")` |  | Keep only these columns: by name (in the order you list them), a run of names, or by kind. |
| `remove_columns` | `table.remove_columns("height")` |  | Remove these columns: by name, a run of names, or by kind. |
| `keep_columns_by_position` | `table.keep_columns_by_position(1, to=3)` |  | Keep columns by their position, counting from 1 at the left; it says which columns they were. |
| `remove_columns_by_position` | `table.remove_columns_by_position(1)` |  | Remove columns by their position, counting from 1 at the left; it says which columns they were. |
| `rename_column` | `table.rename_column("marks", to="score")` |  | Give a column a new name. |

## Choose rows

| Word | Example | Table | What it does |
|---|---|---|---|
| `keep_rows_where` | `table.keep_rows_where("marks", is_above=50)` |  | Keep only the rows that match a condition. |
| `remove_rows_where` | `table.remove_rows_where("subject", is_equal_to="English")` |  | Remove the rows that match a condition (the opposite of keep_rows_where). |
| `keep_first_rows` | `table.keep_first_rows(10)` |  | Keep only the first rows. |
| `keep_last_rows` | `table.keep_last_rows(10)` |  | Keep only the last rows. |
| `keep_rows_by_position` | `table.keep_rows_by_position(10, to=20)` |  | Keep rows by their position, counting from 1: a run, every n-th row, or a list. |
| `remove_rows_by_position` | `table.remove_rows_by_position([12, 40])` |  | Remove rows by their position, counting from 1: a run, every n-th row, or a list. |
| `reverse_rows` | `table.reverse_rows()` |  | Turn the table upside down: the last row comes first. |
| `keep_random_rows` | `table.keep_random_rows(10, with_seed=1)` |  | Keep some rows picked at random; give a seed to get the same rows every time. |
| `remove_duplicate_rows` | `table.remove_duplicate_rows(columns=["name"])` |  | Remove rows that repeat an earlier row, or that repeat it in the columns you name. |
| `keep_biggest_rows` | `table.keep_biggest_rows(3, by="marks", for_each_group_in="subject")` |  | Keep the n rows with the biggest values in a column (also for each group). |
| `keep_smallest_rows` | `table.keep_smallest_rows(3, by="marks", for_each_group_in="subject")` |  | Keep the n rows with the smallest values in a column (also for each group). |
| `show_rows_with_outliers` | `table.show_rows_with_outliers("marks", for_each_group_in="subject")` |  | Show the rows whose value in a column is an outlier, and say why (the table does not change). |
| `remove_rows_with_outliers` | `table.remove_rows_with_outliers("marks", for_each_group_in="subject")` |  | Remove the rows whose value in a column is an outlier, and say how many and why. |

## Empty cells

| Word | Example | Table | What it does |
|---|---|---|---|
| `count_empty_cells_in` | `table.count_empty_cells_in()` |  | Show how many empty cells each column has. |
| `remove_rows_with_empty_cells_in` | `table.remove_rows_with_empty_cells_in("sales")` |  | Remove rows with an empty cell (in any column, or only in the column you name). |
| `fill_empty_cells_in` | `table.fill_empty_cells_in("customers", with_the="median")` |  | Fill the empty cells of a column with a value, or with the average, median, value above or value below. |
| `add_is_empty_column` | `table.add_is_empty_column("sales_was_empty", from_column="sales")` |  | Add a true/false column: True where a cell of from_column is empty. |

## Fix columns

| Word | Example | Table | What it does |
|---|---|---|---|
| `turn_into_numbers` | `table.turn_into_numbers("marks")` |  | Turn a column into numbers; cells that are not numbers become empty. |
| `turn_into_text` | `table.turn_into_text("month_number")` |  | Turn a column into text. |
| `turn_into_dates` | `table.turn_into_dates("year")` |  | Turn a column into dates; cells that are not dates become empty. |
| `turn_into_lowercase` | `table.turn_into_lowercase("name")` |  | Write all the text in a column in small letters. |
| `turn_into_uppercase` | `table.turn_into_uppercase("name")` |  | Write all the text in a column in capital letters. |
| `remove_extra_spaces_in` | `table.remove_extra_spaces_in("name")` |  | Remove spaces at the start and end of the text, and double spaces inside it. |
| `replace_values_in` | `table.replace_values_in("subject", "Maths", with_value="Math")` |  | Replace a value (or a list of values) in a column; with_value=None makes those cells empty. |
| `round_numbers_in` | `table.round_numbers_in("hours", 0)` |  | Round numbers to this many decimal places: in one column, a list of columns, or every number column. |
| `change_column` | `table.change_column("marks", "marks / 10")` |  | Change the values of a column in place, with the same ways as add_column(). |

## Sort and new columns

| Word | Example | Table | What it does |
|---|---|---|---|
| `sort_by` | `table.sort_by("marks", biggest_first=True)` |  | Put the rows in order of one or more columns; empty cells go last. |
| `add_column` | `table.add_column("study_and_marks", by_adding=["hours", "marks"])` |  | Add a new column, worked out from other columns in plain words or with a formula. |
| `add_group_column` | `table.add_group_column("grade", from_column="marks", cut_at=[40, 60, 80], names=["D", "C", "B", "A"])` |  | Add a column that puts each row into a group, like turning marks into grades. |
| `add_rank_column` | `table.add_rank_column("place", from_column="marks")` |  | Add a column with each row's place, where 1 is the best. |
| `add_z_score_column` | `table.add_z_score_column("marks_z", from_column="marks", for_each_group_in="subject")` |  | Add a column with each value's z-score: how many standard deviations it lies above the average. |

## Dates and text

| Word | Example | Table | What it does |
|---|---|---|---|
| `add_column_with_part_of_date` | `table.add_column_with_part_of_date("weekday", from_column="date", part="weekday name")` |  | Add a column with one part of each date, such as its year, month or weekday. |
| `add_column_with_part_of_text` | `table.add_column_with_part_of_text("initial", from_column="name", first_characters=1)` |  | Add a column with one part of each text, such as its first letters or the text before a mark. |
| `split_column` | `table.split_column("shop", separator=" ", into=["shop_kind", "shop_word"])` |  | Split a text column into several columns at a separator, such as a comma or a space. |
| `replace_text_in` | `table.replace_text_in("shop", " shop", with_value="")` |  | Replace a piece of text inside the cells of a text column, wherever it appears. |

## Row after row

| Word | Example | Table | What it does |
|---|---|---|---|
| `add_rolling_column` | `table.add_rolling_column("rain_3_months", from_column="rain", window=3, show="total",
                           for_each_group_in="city", sorted_by="month_number")` |  | Add a rolling (moving) summary: for each row, the average of this row and the rows just before it. |
| `add_previous_value_column` | `table.add_previous_value_column("last_month", from_column="temperature", for_each_group_in="city",
                                  sorted_by="month_number")` |  | Add a column with the value from the row before (or rows_back= rows before). |
| `add_change_column` | `table.add_change_column("growth", from_column="population", in_percent=True,
                          for_each_group_in="country", sorted_by="year")` |  | Add a column with the change from the row before: this value minus the previous one. |

## Summaries

| Word | Example | Table | What it does |
|---|---|---|---|
| `count_rows` | `table.count_rows(for_each_group_in="class")` |  | How many rows the table has, or how many in each group. |
| `count_each` | `table.count_each("fruit")` |  | Each different value in a column, how many times it appears, and its percent. |
| `find_average_of` | `table.find_average_of("marks", for_each_group_in="class")` |  | The average (mean) of a column; empty cells are skipped. |
| `find_median_of` | `table.find_median_of("marks", for_each_group_in="class")` |  | The middle number of a column once it is sorted; empty cells are skipped. |
| `find_total_of` | `table.find_total_of("count", for_each_group_in="shop")` |  | All the numbers in a column added up; empty cells are skipped. |
| `find_smallest_of` | `table.find_smallest_of("temperature", for_each_group_in="city")` |  | The smallest number in a column; empty cells are skipped. |
| `find_biggest_of` | `table.find_biggest_of("temperature", for_each_group_in="city")` |  | The biggest number in a column; empty cells are skipped. |
| `find_standard_deviation_of` | `table.find_standard_deviation_of("marks", for_each_group_in="class")` |  | How spread out the numbers are: the sample standard deviation (divide by n - 1). |
| `find_summary_of` | `table.find_summary_of("marks", for_each_group_in="class", show=["average", "standard deviation", "count"])` |  | Several measures of one or more columns at once, in one tidy table. |
| `find_percent_of_rows_where` | `table.find_percent_of_rows_where("marks", is_above=60, for_each_group_in="class")` |  | What percent of the rows meet a condition, or each group's share. |
| `count_different_values_in` | `table.count_different_values_in("name", for_each_group_in="class")` |  | How many different values a column has, or how many in each group. |
| `find_percentile_of` | `table.find_percentile_of("marks", 90, for_each_group_in="class")` |  | The value below which a given percent of the numbers lie; empty cells are skipped. |
| `find_most_common_of` | `table.find_most_common_of("days_absent", for_each_group_in="school")` |  | The value that turns up most often (the mode), for numbers or text; empty cells are skipped. |
| `find_interval_of` | `table.find_interval_of("marks", "median", for_each_group_in="class")` |  | A confidence interval for any summary, from the bootstrap. |
| `find_correlation_between` | `table.find_correlation_between("hours", "marks")` |  | How strongly columns of numbers go up or down together, from -1 to 1. |

## Statistical tests

| Word | Example | Table | What it does |
|---|---|---|---|
| `compare_averages_of` | `table.compare_averages_of("marks", for_each_group_in="class")` |  | Are the averages of the groups really different? |
| `compare_each_pair_of` | `table.compare_each_pair_of("marks", for_each_group_in="class")` |  | Which pairs of groups differ? Every pair is compared, with Holm's correction. |
| `compare_before_and_after` | `table.compare_before_and_after("Maths", "Science")` |  | Did the values really change from one column to the other, row by row? |
| `compare_average_to` | `table.compare_average_to("marks", 60)` |  | Is the average of a column really different from a number you choose? |
| `compare_counts_of` | `table.compare_counts_of("result", for_each_group_in="class")` |  | Does how often each value turns up really differ between groups? |
| `compare_shape_to` | `table.compare_shape_to("marks", "normal", for_each_group_in="class")` |  | Do the values look bell-shaped (normal), or are they too far from it? |
| `add_adjusted_p_value_column` | `table.add_adjusted_p_value_column("q", method="benjamini-hochberg")` |  | Adjust p-values for testing many things at once, in a new column. |
| `compare_spreads_of` | `table.compare_spreads_of("marks", for_each_group_in="class")` |  | Do the groups really differ in how spread out their values are? |
| `compare_counts_to` | `table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})` |  | Does how often each value turns up really differ from the shares you expect? |
| `compare_percent_to` | `table.compare_percent_to("passed", value="yes", percent=50)` |  | Is the percent of rows with one value really different from a percent you choose? |
| `compare_matched_columns` | `table.compare_matched_columns("Maths", "Science", "English")` |  | Do three or more measurements of the same rows differ, such as pain at week 0, 4 and 8? |
| `compare_shapes_of` | `table.compare_shapes_of("marks", for_each_group_in="class")` |  | Do the groups differ in the whole shape of their values, not only in the average? |
| `check_if_random_order` | `table.check_if_random_order("marks")` |  | Do the values come in a random order, or in clumps or waves? |
| `compare_correlations` | `table.compare_correlations("hours", "marks", for_each_group_in="class")` |  | Is one correlation stronger than another? |
| `sdata.compare_averages` | `sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22])` |  | Are the averages of the groups different? From the summary numbers of each group. |
| `sdata.compare_counts` | `sdata.compare_counts([[20, 40], [30, 30]])` |  | Are the rows and columns of a table of counts linked? From the counts alone. |

## Risks and rates

| Word | Example | Table | What it does |
|---|---|---|---|
| `compare_risks` | `table.compare_risks("died", for_each_group_in="treatment", against="usual care")` |  | How much more (or less) often does something happen in one group than in another? |
| `compare_rates` | `table.compare_rates("infections", time="patient_days", for_each_group_in="ward", against="ward A")` |  | Do events happen more often per unit of time in one group than in another? |
| `rate_of` | `table.rate_of("infections", time="patient_days", for_each_group_in="ward")` |  | How often do events happen per unit of time, such as infections per 1000 patient-days? |
| `sdata.compare_risks` | `sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new", "usual"], against="usual")` |  | How much more (or less) often does something happen in one group than another? From counts. |
| `sdata.compare_rates` | `sdata.compare_rates(events=[15, 30], time=[1200, 1100], names=["ward A", "ward B"])` |  | Do events happen more often per unit of time in one group than another? From counts and times. |

## Diagnostic tests

| Word | Example | Table | What it does |
|---|---|---|---|
| `compare_to_truth` | `table.compare_to_truth("rapid_test", truth="infected")` |  | How well does a test find what is really there (sensitivity, specificity, predictive values)? |
| `compare_accuracy` | `table.compare_accuracy("crp", "procalcitonin", truth="infected")` |  | Which of two scores tells better who has it? DeLong's test of two AUCs on the same rows. |
| `sdata.compare_to_truth` | `sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)` |  | How well does a test find what is really there? From the four counts, or from percents. |
| `trade_off_curve` | `chart.trade_off_curve(score="crp", truth="infected")` |  | How a score trades found cases against false alarms, cut-off by cut-off (the ROC curve). |

## Agreement and reliability

| Word | Example | Table | What it does |
|---|---|---|---|
| `agreement_between` | `table.agreement_between("nurse_rating", "doctor_rating")` |  | How well do two or more raters (or devices) agree on the same rows? |
| `limits_of_agreement` | `table.limits_of_agreement("device_a", "device_b")` |  | How far apart are two ways of measuring the same thing (Bland-Altman limits of agreement)? |
| `reliability_of` | `table.reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])` |  | Do the items of a questionnaire hang together (Cronbach's alpha)? |
| `difference_dots` | `chart.difference_dots(first="device_a", second="device_b")` |  | Do two ways of measuring agree? The difference of each pair against its average (Bland-Altman). |

## Fitting

| Word | Example | Table | What it does |
|---|---|---|---|
| `fit_line` | `table.fit_line(x="hours", y="marks")` |  | Fit the straight line y = slope * x + intercept that best follows the points. |
| `fit_curve` | `table.fit_curve(x="hours", y="marks", of_degree=2)` |  | Fit a curve y = b0 + b1 * x + b2 * x**2 ... that best follows the points. |
| `fit_formula` | `table.fit_formula("population = a * exp(b * (year - 2000))")` |  | Find the values in a formula that make it follow the data best. |

## Finding and solving

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.find_where_smallest` | `sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5])` |  | Find where a formula is smallest, and its value there. |
| `sdata.find_where_biggest` | `sdata.find_where_biggest("3*x + 2*y", rules=["x + y <= 4", "x + 3*y <= 6", "x >= 0", "y >= 0"])` |  | Find where a formula is biggest, and its value there. |
| `sdata.solve` | `sdata.solve("x**3 - 2*x = 5", between=[0, 3])` |  | Find the values that make an equation true. |

## Values between points

| Word | Example | Table | What it does |
|---|---|---|---|
| `values_at` | `table.values_at("population", at={"year": [2001, 2003, 2011]}, for_each_group_in="country")` |  | Estimate a column at places between the known points, by joining the dots. |
| `make_map_of` | `table.make_map_of("height", across=["east", "north"], steps=100)` |  | Estimate a column at evenly spaced places across one or more columns (a map), ready for a contour or heatmap. |

## Distributions

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.distribution` | `sdata.distribution("normal", average=50, standard_deviation=10)` |  | Make a distribution to ask chances, percentiles and random numbers of. |
| `fit_distribution_to` | `table.fit_distribution_to("sales", "lognormal")` |  | Fit a distribution to a column by maximum likelihood; gives back the fitted distribution. |
| `compare_distributions_for` | `table.compare_distributions_for("sales")` |  | Fit several distributions to a column and rank them by AIC (smaller is better). |
| `fit_distribution` | `nums.fit_distribution("gamma")` |  | Fit a distribution to the numbers by maximum likelihood; gives back the fitted distribution. |
| `find_chance_that_value` | `dist.find_chance_that_value(is_above=80)` |  | The chance of a value in a range, as a share from 0 to 1 (printed as a percent). |
| `find_density_at` | `dist.find_density_at(60)` |  | The height of the density curve at a value (continuous distributions). |
| `find_percentile` | `dist.find_percentile(95)` |  | The value that this percent of the distribution is below: percentile(95). |
| `find_cut_off` | `dist.find_cut_off(with_chance_above=0.025)` |  | The value with this chance above it (or below it): critical values. |
| `find_middle_range` | `dist.find_middle_range(95)` |  | The range that holds the middle percent of the distribution, as Numbers [low, high]. |
| `find_average` | `dist.find_average()` |  | The average (mean) of the distribution. |
| `find_median` | `dist.find_median()` |  | The median: half of the distribution is below it. |
| `find_standard_deviation` | `dist.find_standard_deviation()` |  | The standard deviation of the distribution. |
| `find_variance` | `dist.find_variance()` |  | The variance (the standard deviation squared). |
| `show_summary` | `dist.show_summary()` |  | A one-row table: average, median, standard deviation, variance, skewness, excess kurtosis, entropy and the lowest and highest possible values. |
| `make_random_numbers` | `dist.make_random_numbers(how_many=100, with_seed=1)` |  | Numbers drawn at random from the distribution; the same seed gives the same numbers. |
| `draw_chart` | `dist.draw_chart()` |  | A chart of the distribution: its density curve (or bars for counts). |
| `turn_into_table` | `dist.turn_into_table()` |  | A one-row table: the distribution, its parameters and, for a fit, the standard errors, log-likelihood, AIC and BIC. |
| `show_parameters` | `dist.show_parameters()` |  | The parameters as a dictionary of plain names: {"average": 50, "standard_deviation": 10}. |

## Models

| Word | Example | Table | What it does |
|---|---|---|---|
| `explain` | `table.explain("marks", using=["hours", "breakfast"])` |  | Explain one column from several others with a model, and say how big each effect is. |
| `add_predicted_column` | `table.add_predicted_column("marks", using=["hours", "breakfast"])` |  | Add a column with the value the model predicts for each row. |
| `find_model_averages_of` | `table.find_model_averages_of("marks", for_each_group_in="school", using=["hours", "breakfast"])` |  | The average the model gives for each group, once the other columns are allowed for. |
| `check_model_of` | `table.check_model_of("marks", using=["hours", "breakfast"])` |  | Four pictures to check a model from explain(), as R plot(lm(...)). |
| `show_rows_that_pull_model` | `table.show_rows_that_pull_model("marks", using=["hours", "breakfast"])` |  | Show the rows that change a model from explain() the most (the table does not change). |
| `compare_models` | `table.compare_models("marks", using=["hours"], against=["hours", "breakfast"])` |  | Does a bigger model explain the column better than a smaller one? |

## Patterns across columns

| Word | Example | Table | What it does |
|---|---|---|---|
| `add_principal_components` | `table.add_principal_components(how_many=2)` |  | Add principal components: a few new columns that hold most of the spread of many columns. |
| `find_principal_components_of` | `table.find_principal_components_of()` |  | A table of the principal components: how much spread each explains and the weight of each column. |
| `add_clusters` | `table.add_clusters(how_many=3)` |  | Sort the rows into groups of similar rows (clusters), in a new column. |
| `find_distances_between_rows` | `table.find_distances_between_rows(names="plot")` |  | How different each row is from every other row: a square table of distances. |
| `add_nmds` | `table.add_nmds()` |  | Draw the rows as points on a map where close points are similar rows (NMDS), in new columns. |
| `compare_profiles_of` | `table.compare_profiles_of(for_each_group_in="grazed")` |  | Do the groups really differ in their make-up across many columns (PERMANOVA)? |

## Survival

| Word | Example | Table | What it does |
|---|---|---|---|
| `find_survival_over_time` | `table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment")` |  | The share still without the event over time (Kaplan-Meier), with the median time. |
| `compare_survival` | `table.compare_survival(time="days", event="died", for_each_group_in="treatment")` |  | Do the groups really differ in the time until the event? (log-rank test) |
| `explain_survival` | `table.explain_survival(time="days", event="died", using=["treatment", "age"])` |  | Which columns go with a higher or lower risk of the event? (Cox model, hazard ratios) |
| `draw_survival_curves` | `chart.draw_survival_curves(time="days", event="died", colour="treatment")` |  | The share still without the event over time (Kaplan-Meier curves). |

## Dates and time windows

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.make_run_of_dates` | `sdata.make_run_of_dates("2026-01-01", to="2026-12-31", every="day")` |  | A table with one column, "date": regular dates from start, every day (or week, month ...). |
| `add_missing_dates` | `table.add_missing_dates("date", every="day", for_each_group_in="station")` |  | Add a row for every date that is missing from a regular run of dates (other cells empty). |

## Smoothing and trend

| Word | Example | Table | What it does |
|---|---|---|---|
| `add_smoothed_column` | `table.add_smoothed_column("signal_smoothed", from_column="signal", method="savitzky-golay", window=11, sorted_by="time")` |  | Add a smoothed copy of a column: each value becomes a summary of its neighbours in time. |
| `smooth` | `nums.smooth(method="median", window=5)` |  | Smooth the numbers: each one becomes a summary of its neighbours, so noise and spikes shrink. |
| `find_trend_of` | `table.find_trend_of("visitors", sorted_by="month", for_each_group_in="museum")` |  | Does a column keep rising or falling over time, and by how much? (Mann-Kendall test, Sen's slope) |
| `remove_trend` | `nums.remove_trend()` |  | Take away the trend: the best straight line (or only the average) is taken from the numbers. |
| `add_trend_and_season` | `table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year", for_each_group_in="museum")` |  | Split a column into a trend, a season that repeats, and the rest, as three new columns. |
| `find_autocorrelation_of` | `table.find_autocorrelation_of("signal", sorted_by="time", rows_back=40)` |  | How much a column is like itself some rows back (autocorrelation), with a noise band. |
| `find_autocorrelation` | `nums.find_autocorrelation(rows_back=24)` |  | How much the numbers are like themselves some places back (autocorrelation), with a noise band. |
| `check_steady_over_time` | `table.check_steady_over_time("signal", sorted_by="time")` |  | Does a column stay steady over time, or does it wander? (ADF and KPSS tests, as R tseries) |
| `find_change_points_in` | `table.find_change_points_in("nitrate", sorted_by="date", for_each_group_in="station")` |  | Find the points where the average of a column jumps to a new level (R changepoint, PELT). |
| `trend_and_season` | `chart.trend_and_season(x="month", y="visitors", repeats_every="year")` |  | Four panels sharing x: the column itself, its trend, its season and the rest (as R plot(stl(...)), which labels the first panel "data"). |
| `autocorrelation_bars` | `chart.autocorrelation_bars("visitors", sorted_by="month")` |  | Sticks for the correlation of a column with itself 1, 2, ... rows back, with the noise band. |
| `cross_correlation_bars` | `chart.cross_correlation_bars("signal", "vibration", sorted_by="time", rows_back=20)` |  | Sticks for the correlation of two columns when the second is shifted by -k to k rows. |
| `lag_dots` | `chart.lag_dots("visitors", sorted_by="month", rows_back=[1, 12])` |  | Dots of each value against the value some rows back, with the 1:1 line (as R lag.plot). |

## Forecasts

| Word | Example | Table | What it does |
|---|---|---|---|
| `forecast` | `table.forecast("visitors", sorted_by="month", steps_ahead=12, repeats_every="year", for_each_group_in="museum")` |  | Forecast the next values of a column, with an interval for each. |
| `forecast` | `nums.forecast(steps_ahead=12, repeats_every=12)` |  | Forecast the next numbers, with an interval for each (R forecast and stats, run in R). |
| `forecast` | `chart.forecast(steps_ahead=12, repeats_every="year")` |  | The forecast after the data: a dashed line and its interval band, per colour group. |
| `compare_forecasts_for` | `table.compare_forecasts_for("visitors", sorted_by="month", repeats_every="year", for_each_group_in="museum")` |  | Which forecast method would have done best on the last rows? (R forecast::accuracy) |

## Cycles and filters

| Word | Example | Table | What it does |
|---|---|---|---|
| `find_each_peak_that` | `table.find_each_peak_that("signal", sorted_by="time", is_at_least=1, apart=0.05)` |  | Find the peaks of a column: readings higher than both neighbours, with conditions. |
| `find_each_peak_that` | `nums.find_each_peak_that(is_at_least=1, apart=10)` |  | Find the peaks: numbers higher than both neighbours, with conditions. |
| `peak_dots` | `chart.peak_dots(is_at_least=1, apart=0.05)` |  | Dots on the peaks of the line (and on the dips with dips=True). |
| `find_each_dip_that` | `table.find_each_dip_that("signal", sorted_by="time", is_at_most=-1, apart=0.05)` |  | Find the dips of a column: readings lower than both neighbours (find_each_peak_that upside down). |
| `find_each_dip_that` | `nums.find_each_dip_that(is_at_most=-1, apart=10)` |  | Find the dips: numbers lower than both neighbours. |
| `find_spectrum_of` | `table.find_spectrum_of("signal", sorted_by="time")` |  | Which repeating cycles (frequencies) a column holds over time, and how strong each is. |
| `find_spectrum` | `nums.find_spectrum(time_step=0.01)` |  | Which repeating cycles (frequencies) the numbers hold, and how strong each is. |
| `spectrum` | `chart.spectrum("signal", sorted_by="time")` |  | Power against frequency: which cycles a column holds, the 3 strongest labelled with their period. |
| `spectrum_over_time` | `chart.spectrum_over_time("signal", sorted_by="time", window=100)` |  | How the cycles in a column change over time: a heat map of time, frequency and power (decibels). |
| `keep_each_frequency_that` | `nums.keep_each_frequency_that(is_below=5, time_step=0.01)` |  | Keep only some frequencies of the numbers (a low-pass, high-pass, band-pass or peak filter). |
| `remove_each_frequency_that` | `nums.remove_each_frequency_that(is_equal_to=50, time_step=0.005)` |  | Remove some frequencies from the numbers, such as a 50-per-second hum (band-stop or notch filter). |
| `add_filtered_column` | `table.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")` |  | Add a filtered copy of a column: some frequencies kept or removed (low-pass, high-pass, band, notch). |
| `sdata.frequency_filter` | `sdata.frequency_filter(keep_below=10, time_step=0.005)` |  | The filter of add_filtered_column as a system in steps, to look at before using it. |
| `find_envelope` | `nums.find_envelope()` |  | The envelope of the numbers: how big the wave is at each moment (from the Hilbert transform). |
| `add_envelope_column` | `table.add_envelope_column("signal_envelope", from_column="signal", sorted_by="time")` |  | Add the envelope of a column: how big its wave is at each moment (from the Hilbert transform). |
| `take_fourier_transform` | `nums.take_fourier_transform(time_step=0.005)` |  | The numbers as a sum of waves: the size and phase of each frequency (the Fourier transform). |
| `sdata.find_inverse_fourier_transform` | `sdata.find_inverse_fourier_transform(table)` |  | Numbers back from a Fourier transform table (its real and imaginary parts). |

## Planning a study

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.find_how_many_needed` | `sdata.find_how_many_needed(effect_size=0.5)` |  | How many values (in each group) does a study need to find a real difference? |
| `sdata.find_chance_of_finding` | `sdata.find_chance_of_finding(effect_size=0.5, values_per_group=30)` |  | What chance does a study have to find a real difference of a given size (its power)? |

## Combine and reshape

| Word | Example | Table | What it does |
|---|---|---|---|
| `join_with` | `table.join_with({"name": ["Asha", "Ben"], "age": [12, 13]}, using="name")` |  | Bring in the columns of another table, matching rows on a column such as a name. |
| `add_rows_from` | `table.add_rows_from(sdata.get_example("marks"))` |  | Put the rows of another table under this one; columns are matched by their names. |
| `turn_columns_into_rows` | `table.turn_columns_into_rows(["temperature", "rain"])` |  | Turn some columns into rows: each value gets its own row, with its old column name beside it. |
| `turn_rows_into_columns` | `table.turn_rows_into_columns(names_from="city", values_from="temperature")` |  | Turn rows into columns: each different value in names_from= becomes a new column, filled from values_from=. |

## Undo and finish

| Word | Example | Table | What it does |
|---|---|---|---|
| `undo` | `table.undo()` |  | Take the last step back. |
| `show_steps` | `table.show_steps()` |  | List every step you did to this table, in order. |
| `start_again` | `table.start_again()` |  | Go back to the table as it was at the start. |
| `save` | `table.save("clean.xlsx")` |  | Save the table; the end of the file name decides the type. |
| `start_chart` | `table.start_chart()` |  | Start a chart from this table. |
| `as_pandas` | `table.as_pandas()` |  | Give back the table as a plain pandas table, for other Python tools. |
| `as_polars` | `table.as_polars()` |  | Give back the table as a plain Polars table, for other Python tools. |

## Numbers: make and look

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.numbers` | `sdata.numbers([3, 5, 2, 8])` |  | Make a list of numbers. |
| `sdata.make_random_numbers` | `sdata.make_random_numbers(how_many=10, between=[0, 1], with_seed=1)` |  | Make random numbers; give with_seed= to get the same numbers every time. |
| `show` | `nums.show()` |  | Show every number. |
| `show_first_numbers` | `nums.show_first_numbers(5)` |  | Show the first numbers. |
| `show_last_numbers` | `nums.show_last_numbers(5)` |  | Show the last numbers. |
| `get_number_at` | `nums.get_number_at(1)` |  | The number at a position, counting from 1: get_number_at(1) is the first number. |
| `count` | `nums.count()` |  | How many numbers there are (empty ones included). |
| `count_empty_numbers` | `nums.count_empty_numbers()` |  | How many values are empty (missing). |

## Numbers: maths in words

| Word | Example | Table | What it does |
|---|---|---|---|
| `add` | `nums.add(5)` |  | Add a number to every number (or add numbers one by one). |
| `subtract` | `nums.subtract(2)` |  | Take a number away from every number. |
| `times` | `nums.times(2)` |  | Multiply every number by a number. |
| `divide_by` | `nums.divide_by(4)` |  | Divide every number by a number. |
| `raise_to_power` | `nums.raise_to_power(2)` |  | Raise every number to a power: power(2) squares, power(3) cubes. |
| `take_square_root` | `nums.take_square_root()` |  | The square root of every number: 9 becomes 3. |
| `take_absolute_value` | `nums.take_absolute_value()` |  | Every number without its minus sign: -3 becomes 3. |
| `round_to` | `nums.round_to(2)` |  | Round every number to this many decimal places. |
| `take_log` | `nums.take_log()` |  | The logarithm of every number: natural (base e) unless you give base=10 or base=2. |
| `take_exp` | `nums.take_exp()` |  | e (about 2.718) to the power of every number; it undoes log(). |
| `turn_into_running_total` | `nums.turn_into_running_total()` |  | Each number becomes the total so far (the cumulative sum): 1, 2, 3 becomes 1, 3, 6. |

## Numbers: choose, sort and fill

| Word | Example | Table | What it does |
|---|---|---|---|
| `keep_each_number_that` | `nums.keep_each_number_that(is_above=50)` |  | Keep only the numbers that match one condition. |
| `remove_each_number_that` | `nums.remove_each_number_that(is_below=0)` |  | Remove the numbers that match one condition (the opposite of keep_each_number_that). |
| `keep_first_numbers` | `nums.keep_first_numbers(10)` |  | Keep only the first numbers. |
| `keep_last_numbers` | `nums.keep_last_numbers(10)` |  | Keep only the last numbers. |
| `keep_random_numbers` | `nums.keep_random_numbers(10, with_seed=1)` |  | Keep some numbers picked at random (they keep their order); a seed gives the same pick every time. |
| `remove_duplicate_numbers` | `nums.remove_duplicate_numbers()` |  | Remove numbers that repeat an earlier number, so each number is left once, in its first place. |
| `remove_empty_numbers` | `nums.remove_empty_numbers()` |  | Remove the empty (missing) values. |
| `keep_numbers_by_position` | `nums.keep_numbers_by_position(2, to=4)` |  | Keep numbers by their position, counting from 1: a run, every n-th number, or a list. |
| `remove_numbers_by_position` | `nums.remove_numbers_by_position("last")` |  | Remove numbers by their position, counting from 1: a run, every n-th number, or a list. |
| `replace_each_number_that` | `nums.replace_each_number_that(-999, with_value=None)` |  | Replace a number, or every number that meets one condition; with_value=None makes them empty. |
| `fill_empty_numbers` | `nums.fill_empty_numbers(with_value=0)` |  | Fill the empty values with a number, or with the average, median, value above or value below. |
| `sort` | `nums.sort(biggest_first=True)` |  | Put the numbers in order, smallest first; empty values go last. |
| `reverse` | `nums.reverse()` |  | Turn the order round: the last number comes first. |

## Numbers: summaries

| Word | Example | Table | What it does |
|---|---|---|---|
| `find_average` | `nums.find_average()` |  | The average (mean) of the numbers; empty values are skipped. |
| `find_median` | `nums.find_median()` |  | The middle number once the numbers are sorted; empty values are skipped. |
| `find_total` | `nums.find_total()` |  | All the numbers added up; empty values are skipped. |
| `find_smallest` | `nums.find_smallest()` |  | The smallest number; empty values are skipped. |
| `find_biggest` | `nums.find_biggest()` |  | The biggest number; empty values are skipped. |
| `find_standard_deviation` | `nums.find_standard_deviation()` |  | How spread out the numbers are: the sample standard deviation (divide by n - 1). |
| `find_percentile` | `nums.find_percentile(90)` |  | The number that this percent of the numbers are below: percentile(50) is the median. |
| `count_each` | `nums.count_each()` |  | Each different number, how many times it appears, and its percent, as a table. |

## Grids of numbers

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.number_grid` | `sdata.number_grid([[1, 2, 3], [4, 5, 6]])` |  | Make a grid of numbers in rows and columns. |
| `make_number_grid` | `nums.make_number_grid(columns=3)` |  | Make a NEW grid from these numbers, filled row by row. |
| `count_rows` | `grid.count_rows()` |  | How many rows the grid has. |
| `count_columns` | `grid.count_columns()` |  | How many columns the grid has. |
| `find_shape` | `grid.find_shape()` |  | How many rows and columns, as (rows, columns). |
| `show_first_rows` | `grid.show_first_rows(5)` |  | Show the first rows. |
| `show_last_rows` | `grid.show_last_rows(5)` |  | Show the last rows. |
| `get_number_at` | `grid.get_number_at(row=1, column=2)` |  | The number at a row and column, counting from 1. |
| `get_row` | `grid.get_row(1)` |  | One row of the grid as new numbers, counting from 1: row(1) is the top row. |
| `get_column` | `grid.get_column(1)` |  | One column of the grid as new numbers, counting from 1: column(1) is the left one. |
| `get_all_numbers` | `grid.get_all_numbers()` |  | All the numbers of the grid as a list, row by row (flatten). |
| `keep_rows_by_position` | `grid.keep_rows_by_position(1, to=2)` |  | Keep rows of the grid by their position, counting from 1: a run, every n-th row, or a list. |
| `keep_columns_by_position` | `grid.keep_columns_by_position(2, to=3)` |  | Keep columns of the grid by their position, counting from 1 at the left. |
| `remove_rows_by_position` | `grid.remove_rows_by_position(1)` |  | Remove rows of the grid by their position, counting from 1. |
| `remove_columns_by_position` | `grid.remove_columns_by_position(1)` |  | Remove columns of the grid by their position, counting from 1 at the left. |
| `replace_each_number_that` | `grid.replace_each_number_that(is_below=4, with_value=0)` |  | Replace a number, or every number that meets one condition; the grid keeps its rows and columns. |
| `swap_rows_and_columns` | `grid.swap_rows_and_columns()` |  | Turn rows into columns and columns into rows (the transpose in maths). |

## Numbers: undo and finish

| Word | Example | Table | What it does |
|---|---|---|---|
| `undo` | `nums.undo()` |  | Take the last step back. |
| `show_steps` | `nums.show_steps()` |  | List every step you did, in order. |
| `start_again` | `nums.start_again()` |  | Go back to the numbers as they were at the start. |
| `turn_into_table` | `nums.turn_into_table(name="marks")` |  | Turn the numbers into a simplydata table. |
| `start_chart` | `nums.start_chart()` |  | Start a chart from these numbers. |
| `save` | `nums.save("nums.csv")` |  | Save the numbers; the end of the file name decides the type. |
| `as_numpy` | `nums.as_numpy()` |  | Give back the numbers as a plain NumPy array, for other Python tools. |

## Waves and systems

| Word | Example | Table | What it does |
|---|---|---|---|
| `convolve_with` | `nums.convolve_with([1, 2, 1])` |  | Convolve the numbers with other numbers: each result is a sum of products as one list slides along. |
| `deconvolve_by` | `nums.deconvolve_by([1, 2, 3])` |  | Undo a convolution: the numbers divided by other numbers (polynomial division). |
| `change_time_step` | `nums.change_time_step(to=0.01, time_step=0.001)` |  | Change the time between readings (resample): fewer readings (with a filter first) or more. |
| `sdata.make_wave` | `sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=100)` |  | Numbers that make a wave: a sine, square, sawtooth, chirp, pulse or impulse. |
| `sdata.make_window_shape` | `sdata.make_window_shape("hann", how_many=64)` |  | The weights of a window (taper), such as "hann": high in the middle, low at the ends. |
| `sdata.system` | `sdata.system("1 / (s**2 + 2*s + 5)")` |  | A linear system (one input, one output) from its formula, coefficients, poles or matrices. |
| `step_response` | `system.step_response(until=10)` |  | How the output answers an input that jumps from 0 to 1 and stays there. |
| `impulse_response` | `system.impulse_response(until=10)` |  | How the output answers a short kick at time 0 (an impulse of size 1). |
| `response_to` | `system.response_to(sdata.make_wave("square", frequency=0.2, time_step=0.05, how_many=400))` |  | How the output answers any input you give: a simulation. |
| `frequency_response` | `system.frequency_response(between=[0.1, 100])` |  | How much the system passes each frequency (gain) and how much it delays it (phase): the Bode data. |
| `poles` | `system.poles()` |  | The poles: the values of s (or z) where the bottom of the formula is 0. They set how it moves. |
| `zeros` | `system.zeros()` |  | The zeros: the values of s (or z) where the top of the formula is 0 (inputs that do not get through). |
| `is_stable` | `system.is_stable()` |  | True when every response to a bounded input stays bounded (and settles). |
| `steady_gain` | `system.steady_gain()` |  | Where the output settles for a constant input of 1 (the DC gain). |
| `in_steps` | `system.in_steps(time_step=0.1)` |  | The same system in steps of time_step (discrete time), for a computer that reads and acts in steps. |
| `then` | `system.then(sdata.system("1 / s"))` |  | This system, then another one after it (in series): the output of this one feeds the other. |
| `add` | `system.add(sdata.system("1 / (s + 3)"))` |  | This system and another side by side, their outputs added (in parallel): both get the same input. |
| `with_feedback` | `system.with_feedback()` |  | The closed loop: the output is fed back (through a sensor, say) and taken from the input. |
| `table` | `system.table()` |  | The system as numbers: form="transfer function" (the coefficients of the top and the bottom, highest power first: power of s (power of z in steps), numerator, denominator), "state space" (the matrices A, B, C, D in controller form: matrix, row, column, value; SciPy tf2ss, as R control::tf2ss) or "poles and zeros" (kind, real part, imaginary part; the last row is the gain). |
| `chart` | `system.chart()` |  | A chart of the system: show="bode" (gain in decibels and phase against frequency on a log scale, two panels; "gain and phase" is accepted), "step", "impulse", "poles and zeros" (x for poles, o for zeros; the unit circle for a system in steps; "pole-zero" is accepted) or "nyquist" (the frequency response as one curve; a feedback loop is stable when it stays clear of -1). |

## Help

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.show_all_words` | `sdata.show_all_words()` |  | Print every simplydata word with a short example. |
| `sdata.help` | `sdata.help("draw_bars")` |  | Explain one word: what it does, its options and an example you can run. |
| `sdata.show_lesson` | `sdata.show_lesson(1)` |  | A lesson: an example to run, what each line does, and a task. |

## 30 days of simplydata

| Word | Example | Table | What it does |
|---|---|---|---|
| `sdata.start_30_days` | `sdata.start_30_days()` |  | Start 30 days of simplydata: an hour a day of warm-up questions, lessons and tasks. |
| `sdata.show_today` | `sdata.show_today()` |  | Show today's day of the 30 days of simplydata: warm-up questions, what to do and a task. |
| `sdata.show_day` | `sdata.show_day(5)` |  | Show any day of the 30 days, without changing where you are. |
| `sdata.show_answers` | `sdata.show_answers(5)` |  | The answers to a day's warm-up questions, and a worked answer to its task. |
| `sdata.go_to_next_day` | `sdata.go_to_next_day()` |  | Go on to the next day now, without waiting for tomorrow. |
