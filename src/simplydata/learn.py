"""Learning simplydata: sdata.show_all_words(), sdata.help("draw_bars") and sdata.show_lesson(1) ... sdata.show_lesson(21).

The word list is built from the real words and their docstrings, so it cannot go out of
date. Only the grouping (GROUPS) and the runnable examples (HELP_EXAMPLES, LESSONS) are
written by hand, and the tests check that every word is in a group, has an example,
and that every example runs.
"""

from __future__ import annotations

import builtins
import inspect
import re
import textwrap

from ._errors import ISSUES_URL, SimplydataError, _quoted, suggest

WIDTH = 78

# ---------------------------------------------------------------- the grouping
# "sdata.name" is a function you call on sdata; "name=" is an option used inside chart steps;
# a plain name is a step on a chart (chart.name(...)); "table.name" is a step on a table
# (table.name(...)); "nums.name" is a step on numbers and "grid.name" a step on a grid of
# numbers. Other spellings of a word (bar, scatter, color ...) are found by themselves and
# shown next to it. Old names (kept for one release) are never listed here.
GROUPS = [
    ("Start, show and save", ["sdata.chart", "sdata.get_example", "show", "save", "get_numbers_drawn",
                              # charts phase, batch 1: reading a chart back, and a step back
                              "get_text_drawn", "get_scales_drawn", "get_size", "undo"]),
    ("Chart types", ["draw_bars", "draw_lines", "draw_dots", "draw_area", "draw_histogram", "draw_boxes", "draw_violins",
                     "draw_heatmap", "draw_pie", "draw_polar", "draw_contour", "draw_surface", "draw_dots_3d", "draw_band", "draw_map_of_empty_cells", "draw_sticks"]),
    ("Statistics", ["show=", "error=", "draw_error_bars", "fit_line", "fit_curve", "fit_formula", "fit_distribution",
                    "fit_dose_response", "draw_curve", "draw_smooth_line",
                    # S3a-3 (checking and comparing)
                    "draw_interaction_lines",
                    # S3c-1 (communities and resistomes)
                    "draw_richness_curves", "draw_cluster_tree",
                    # S3c-3 (directions, places and extremes): "more"
                    "draw_variogram", "draw_threshold_check",
                    # S3d-1 (planning and surveys): answers on a scale
                    "draw_answer_bars",
                    "draw_density", "draw_count_bars", "draw_all_dots", "draw_side_histograms", "draw_qq_dots",
                    "draw_cumulative_share", "sdata.draw_all_pairs"]),
    ("Lines and shading", ["draw_line_at_x", "draw_line_at_y", "draw_line_with_slope", "shade_between_x", "shade_between_y"]),
    ("Words on the chart", ["write_title_on_top", "write_caption_at_bottom", "label_x", "label_y", "write_note",
                            "write_numbers_on_bars", "write_names_on_dots", "use_font_size", "use_font",
                            "write_letter"]),
    ("Axes", ["set_range_x", "set_range_y", "use_log_scale_x", "use_log_scale_y", "put_ticks_x", "put_ticks_y",
              "rotate_labels_x", "rotate_labels_y", "write_ticks_x_as", "write_ticks_y_as", "add_second_y",
              "flip_x", "flip_y"]),
    ("Colours and look", ["use_colour", "use_colours", "use_colour_scale", "use_style", "set_size", "show_grid", "hide_grid",
                          "put_legend_at_top", "put_legend_at_bottom", "put_legend_on_left", "put_legend_on_right",
                          "hide_legend", "show_legend", "label_legend", "label_colour_bar",
                          "put_legend_inside", "use_shapes"]),
    ("Order of groups", ["order_x", "order_y", "order_legend"]),
    ("Several charts", ["draw_one_chart_for_each_group_in", "sdata.put_side_by_side", "sdata.put_one_above_other", "sdata.put_in_rows_and_columns",
                        "add_zoom_box", "animate"]),
    # charts phase, batch 2 (approved by Manish 2026-11-25)
    ("More chart types", ["draw_rug_lines", "draw_wind_rose", "draw_arrow", "put_chart_inside", "add_second_x"]),
    ("Frame, ticks and shape", ["hide_frame", "hide_ticks_x", "hide_ticks_y", "show_small_ticks_x",
                                "show_small_ticks_y", "use_true_shape", "make_square"]),
    ("Colour bar", ["put_colour_bar_at_bottom", "put_colour_bar_at_top", "put_colour_bar_at_left", "hide_colour_bar",
                    "put_ticks_colour_bar"]),
    ("3D charts", ["draw_lines_3d", "label_z", "set_range_z", "put_ticks_z", "look_from"]),
    ("Describing a chart", ["say_what_it_shows"]),
    # charts phase, batch 3 (approved by Manish 2026-11-25)
    ("Web pages", ["show_in_web_page", "show_when_pointing", "add_range_bar_x"]),
    ("Breaks and other scales", ["break_between_y", "use_scale_x", "use_scale_y", "use_background_colour"]),
    ("More marks", ["draw_hexagon_bins", "draw_time_bars", "draw_rectangle", "draw_circle", "draw_residual_dots",
                    "draw_event_lines", "draw_bars_3d"]),
    # Table words: "table.name" is a step on a table (table.name(...)).
    ("Tables: start and look", ["sdata.table", "table.show_first_rows", "table.show_last_rows",
                                "table.show", "table.get_column_names", "table.describe_columns", "table.get_column",
                                "table.get_row", "table.get_cell_at",
                                "table.count_columns", "table.show_differences_from",
                                "table.check_if_same_as"]),
    ("Choose columns", ["table.keep_columns", "table.remove_columns", "table.keep_columns_by_position",
                        "table.remove_columns_by_position", "table.rename_column", "table.clean_column_names",
                        "table.rename_columns", "table.move_columns"]),
    ("Choose rows", ["table.keep_rows_where", "table.remove_rows_where", "table.keep_first_rows",
                     "table.keep_last_rows", "table.keep_rows_by_position", "table.remove_rows_by_position",
                     "table.reverse_rows", "table.keep_random_rows", "table.remove_duplicate_rows",
                     "table.repeat_each_row_by", "table.keep_biggest_rows", "table.keep_smallest_rows", "table.show_rows_with_outliers",
                     "table.remove_rows_with_outliers", "table.show_duplicate_rows", "table.keep_groups_where",
                     "table.remove_groups_where"]),
    ("Empty cells", ["table.count_empty_cells_in", "table.remove_rows_with_empty_cells_in",
                     "table.fill_empty_cells_in", "table.add_is_empty_column", "table.remove_rows_that_are_all_empty",
                     "table.remove_columns_that_are_all_empty",
                     "table.fill_empty_cells_from", "table.show_rows_with_empty_cells_in"]),
    ("Fix columns", ["table.turn_into_numbers", "table.turn_into_text", "table.turn_into_dates",
                     "table.turn_into_lowercase", "table.turn_into_uppercase", "table.remove_extra_spaces_in",
                     "table.replace_values_in", "table.round_numbers_in", "table.change_column",
                     "table.turn_into_categories"]),
    ("Sort and new columns", ["table.sort_by", "table.add_column", "table.add_group_column",
                              "table.add_rank_column", "table.add_z_score_column", "table.add_row_summary_column",
                              "table.add_row_number_column"]),
    ("Dates and text", ["table.add_column_with_part_of_date", "table.add_column_with_part_of_text", "table.split_column",
                        "table.replace_text_in", "table.split_into_rows",
                        "table.round_dates_in", "table.change_time_zone_in", "table.add_zeros_in_front_of"]),
    ("Row after row", ["table.add_rolling_column", "table.add_previous_value_column", "table.add_change_column",
                       "table.add_running_column"]),
    ("Summaries", ["table.count_rows", "table.count_each", "table.find_average_of", "table.find_median_of",
                   "table.find_total_of", "table.find_smallest_of", "table.find_biggest_of",
                   "table.find_standard_deviation_of", "table.find_summary_of", "table.find_percent_of_rows_where",
                   "table.count_different_values_in", "table.find_percentile_of", "table.find_most_common_of",
                   "table.find_interval_of", "table.find_correlation_between"]),
    ("Statistical tests", ["table.compare_averages_of", "table.compare_each_pair_of", "table.compare_before_and_after",
                           "table.compare_average_to", "table.compare_counts_of", "table.compare_shape_to",
                           "table.add_adjusted_p_value_column", "table.compare_spreads_of", "table.compare_counts_to",
                           "table.compare_percent_to", "table.compare_matched_columns", "table.compare_shapes_of",
                           "table.check_if_random_order", "table.compare_correlations", "sdata.compare_averages",
                           "sdata.compare_counts"]),
    ("Risks and rates", ["table.compare_risks", "table.compare_rates", "table.rate_of", "sdata.compare_risks",
                         "sdata.compare_rates",
                         # S3d-2 (epidemiology and cause and effect): "more"
                         "table.compare_balanced_groups_of"]),
    ("Diagnostic tests", ["table.compare_to_truth", "table.compare_accuracy", "sdata.compare_to_truth",
                          "draw_trade_off_curve"]),
    ("Agreement and reliability", ["table.agreement_between", "table.limits_of_agreement", "table.reliability_of",
                                   "draw_difference_dots"]),
    ("Fitting", ["table.fit_line", "table.fit_curve", "table.fit_formula",
                # S3a-2 (lines and curves): core, then "more"
                "table.fit_dose_response", "table.find_best_power_of"]),
    ("Finding and solving", ["sdata.find_where_smallest", "sdata.find_where_biggest", "sdata.solve"]),
    # numbers phase, batch 3 (approved by Manish 2026-11-25): "f.name" is a step on a formula,
    # f = sdata.formula("(x + 2)**2 - 4"), then f.turn_into_sum()
    ("Formulas and exact answers", ["sdata.formula", "f.make_simpler", "f.turn_into_sum", "f.turn_into_product",
                                    "f.find_slope_formula", "f.find_area_formula", "f.find_value_at", "f.put_in",
                                    "f.show_as_latex", "f.find_limit_as", "f.find_taylor_series", "f.undo",
                                    # numbers phase, batch 4 (approved by Manish 2026-11-26)
                                    "f.show_as_decimal", "f.group_by_powers_of", "f.turn_into_partial_fractions",
                                    "f.as_sympy"]),
    ("Areas and paths over time", ["sdata.find_area_under", "sdata.find_volume_under", "sdata.find_path_over_time",
                                   "nums.turn_into_running_area",
                                   # numbers phase, batch 4
                                   "sdata.find_sum_of_series"]),
    ("Values between points", ["table.find_values_at", "table.make_map_of"]),
    # "dist.name" is a step on a distribution: dist = sdata.distribution("normal"), then dist.find_chance_that_value(...).
    ("Distributions", ["sdata.distribution", "table.fit_distribution_to", "table.compare_distributions_for",
                       "nums.fit_distribution", "dist.find_chance_that_value", "dist.find_density_at", "dist.find_percentile", "dist.find_cut_off",
                       "dist.find_middle_range", "dist.find_average", "dist.find_median", "dist.find_standard_deviation",
                       "dist.find_variance", "dist.show_summary", "dist.make_random_numbers", "dist.draw_chart", "dist.turn_into_table",
                       "dist.show_parameters"]),
    ("Models", ["table.explain", "table.add_predicted_column", "table.find_model_averages_of", "table.check_model_of",
                "table.show_rows_that_pull_model", "table.compare_models",
                # S3a-3 (checking and comparing): "more"
                "table.find_columns_that_predict", "table.find_group_levels_of"]),
    ("Patterns across columns", ["table.add_principal_components", "table.find_principal_components_of",
                                 "table.add_clusters", "table.find_distances_between_rows",
                                 "table.find_distances_to_rows_of", "table.add_nmds",
                                 "table.compare_profiles_of",
                                 # S3c-1 (communities and resistomes): core, then "more"
                                 "table.add_diversity_columns", "table.add_log_ratio_columns",
                                 "table.add_principal_coordinates", "table.explain_profiles_of",
                                 "table.find_correlation_between_profiles", "table.add_axes_that_separate_groups",
                                 "table.add_correspondence_axes",
                                 # S3c-2 (hidden factors): "more"
                                 "table.find_hidden_factors_behind", "table.check_hidden_factors"]),
    # S3c-3: directions, places and extremes (core, then "more")
    ("Directions, places and extremes", ["table.find_average_direction_of", "table.find_return_levels_of",
                                         "table.find_variogram_of",
                                         # numbers phase, batch 3: nearest rows and the fence around points
                                         "table.find_nearest_rows_to", "table.find_fence_around"]),
    ("Survival", ["table.find_survival_over_time", "table.compare_survival", "table.explain_survival",
                  "draw_survival_curves",
                  # S3b-3 (survival and person-time): core, then the chart twin
                  "table.add_time_and_event_columns", "table.find_risk_over_time", "draw_risk_curves"]),
    # S3b-1: combining studies (meta-analysis); forest_plot draws any result table with intervals, and the combined
    # effect of combine_studies as a diamond
    ("Combining studies", ["table.combine_studies", "draw_forest_plot", "draw_funnel_plot"]),
    # Time series and signals: the core words first in each group, then the "more" words.
    ("Dates and time windows", ["sdata.make_run_of_dates", "table.add_missing_dates"]),
    ("Smoothing and trend", ["table.add_smoothed_column", "nums.smooth", "table.find_trend_of", "nums.remove_trend",
                             "table.add_trend_and_season", "table.find_autocorrelation_of", "nums.find_autocorrelation",
                             "table.check_steady_over_time", "table.find_change_points_in", "draw_trend_and_season",
                             "draw_autocorrelation_bars", "draw_cross_correlation_bars", "draw_lag_dots"]),
    ("Forecasts", ["table.forecast", "nums.forecast", "draw_forecast", "table.compare_forecasts_for"]),
    ("Cycles and filters", ["table.find_each_peak_that", "nums.find_each_peak_that", "draw_peak_dots", "table.find_each_dip_that", "nums.find_each_dip_that",
                            "table.find_spectrum_of", "nums.find_spectrum", "draw_spectrum", "draw_spectrum_over_time",
                            "nums.keep_each_frequency_that", "nums.remove_each_frequency_that", "table.add_filtered_column",
                            "sdata.frequency_filter", "nums.find_envelope", "table.add_envelope_column",
                            "nums.take_fourier_transform", "sdata.find_inverse_fourier_transform",
                            # numbers phase, batch 3
                            "nums.find_coherence_with", "nums.take_cosine_transform"]),
    ("Planning a study", ["sdata.find_how_many_needed", "sdata.find_chance_of_finding"]),
    # S3d-1: planning an experiment and survey answers
    ("Planning and surveys", ["sdata.make_design_table", "sdata.make_random_assignments", "table.use_survey_design"]),
    ("Join and reshape", ["table.join_with", "table.add_rows_from", "table.gather_into_rows",
                             "table.spread_into_columns", "table.swap_rows_and_columns", "table.keep_rows_found_in",
                             "table.remove_rows_found_in",
                             "table.add_missing_combinations_of", "table.spread_into_yes_no_columns",
                             "table.make_one_table_for_each_group_in", "table.run_sql", "sdata.run_sql"]),
    ("Undo and finish", ["table.undo", "table.show_steps", "table.start_again", "table.save",
                         "table.make_copy", "table.start_chart", "table.as_pandas", "table.as_polars",
                         "table.as_list"]),
    # Number words: "nums.name" is a step on numbers, "grid.name" a step on a grid of numbers.
    ("Numbers: make and look", ["sdata.numbers", "sdata.make_random_numbers", "nums.show", "nums.show_first_numbers",
                                "nums.show_last_numbers", "nums.get_number_at", "nums.count",
                                "nums.count_empty_numbers"]),
    ("Numbers: maths in words", ["nums.add", "nums.subtract", "nums.times", "nums.divide_by", "nums.raise_to_power",
                                 "nums.take_square_root", "nums.take_absolute_value", "nums.round_to", "nums.take_log",
                                 "nums.take_exp", "nums.turn_into_running_total",
                                 # numbers phase, batch 3
                                 "nums.take_cube_root", "nums.show_as_fraction"]),
    ("Numbers: choose, sort and fill", ["nums.keep_each_number_that", "nums.remove_each_number_that", "nums.keep_first_numbers",
                                        "nums.keep_last_numbers", "nums.keep_random_numbers",
                                        "nums.remove_duplicate_numbers", "nums.remove_empty_numbers",
                                        "nums.keep_numbers_by_position", "nums.remove_numbers_by_position",
                                        "nums.replace_each_number_that", "nums.fill_empty_numbers", "nums.sort",
                                        "nums.reverse"]),
    ("Numbers: summaries", ["nums.find_average", "nums.find_median", "nums.find_total", "nums.find_smallest", "nums.find_biggest",
                            "nums.find_standard_deviation", "nums.find_percentile", "nums.count_each"]),
    ("Grids of numbers", ["sdata.number_grid", "nums.make_number_grid", "grid.count_rows", "grid.count_columns",
                          "grid.find_shape", "grid.show_first_rows", "grid.show_last_rows", "grid.get_number_at",
                          "grid.get_row", "grid.get_column", "grid.get_all_numbers", "grid.keep_rows_by_position",
                          "grid.keep_columns_by_position", "grid.remove_rows_by_position",
                          "grid.remove_columns_by_position", "grid.replace_each_number_that", "grid.swap_rows_and_columns"]),
    # numbers phase, batch 3 (approved by Manish 2026-11-25)
    ("Grids: pairs, patches and matrices", ["grid.get_numbers_at_pairs", "grid.get_numbers_from_each_row_at",
                                            "grid.find_each_patch_that", "grid.change_size_to", "grid.rotate",
                                            "grid.take_matrix_exp", "grid.find_null_space",
                                            # numbers phase, batch 4 (approved by Manish 2026-11-26)
                                            "grid.find_determinant", "grid.take_inverse", "grid.find_eigenvalues"]),
    ("Numbers: undo and finish", ["nums.undo", "nums.show_steps", "nums.start_again", "nums.turn_into_table", "nums.start_chart",
                                  "nums.save", "nums.as_numpy"]),
    # NumPy + SciPy phase, batch 1 (approved by Manish 2026-11-25): yes or no values, rounding, angles, positions,
    # and blocks of numbers with any number of directions. "block.name" is a step on a block of numbers.
    ("Numbers: yes or no", ["nums.turn_into_yes_or_no", "nums.keep_numbers_where", "nums.remove_numbers_where",
                            "nums.replace_numbers_where", "nums.count_numbers_that", "nums.check_if_any_number",
                            "nums.check_if_all_numbers", "nums.check_if_same_as", "grid.keep_rows_where",
                            "grid.remove_rows_where"]),
    ("Numbers: rounding, angles and positions", ["nums.round_down", "nums.round_up", "nums.take_whole_part",
                                                 "nums.take_sin", "nums.take_cos", "nums.take_tan",
                                                 "nums.change_angles_to", "nums.find_where_biggest",
                                                 "nums.find_where_smallest", "nums.make_pair_table_with"]),
    ("Blocks of numbers", ["sdata.number_block", "block.find_shape", "block.count_directions",
                           "block.find_direction_names", "block.get_number_at", "block.find_average",
                           "block.keep_by_position_in", "block.remove_by_position_in", "block.keep_where",
                           "block.remove_where"]),
    ("Blocks: shape and directions", ["block.change_shape_to", "block.add_direction",
                                      "block.remove_directions_of_size_one", "block.swap_directions",
                                      "block.move_direction", "block.rotate", "block.move_round_by",
                                      "block.insert_numbers", "block.repeat_each_number", "block.repeat_whole_block",
                                      "block.add_numbers_from", "block.split_into_pieces",
                                      "block.split_into_one_block_per", "sdata.stack_up"]),
    ("Blocks: stretching", ["block.show_how_it_lines_up_with", "block.stretch_to", "sdata.stretch_to_same_shape",
                            "sdata.hide_stretching_notes", "sdata.show_stretching_notes"]),
    # NumPy + SciPy phase, batch 2 (approved by Manish 2026-11-25): netCDF files, labels, dates and places on blocks,
    # smoothing grids and blocks, chances and random picks
    ("Blocks: files", ["sdata.show_whats_inside", "block.save"]),
    ("Blocks: labels, dates and places", ["block.get_labels_of", "block.add_labels_to", "block.find_values_at",
                                          "block.get_numbers_nearest_to", "block.turn_into_change_from_average",
                                          "block.smooth", "block.change_size_to", "grid.smooth"]),
    ("Numbers: chances and random picks", ["nums.make_random_picks", "nums.take_log_odds", "nums.turn_into_chances",
                                           "sdata.count_ways_to_choose", "sdata.count_ways_to_order"]),
    # "system.name" is a step on a system: system = sdata.system("1 / (s**2 + 2*s + 5)"), then system.poles().
    ("Waves and systems", ["nums.convolve_with", "nums.deconvolve_by", "nums.change_time_step", "sdata.make_wave",
                           "sdata.make_window_shape", "sdata.system", "system.step_response", "system.impulse_response",
                           "system.response_to",
                           "system.frequency_response", "system.poles", "system.zeros", "system.is_stable",
                           "system.steady_gain", "system.in_steps", "system.then", "system.add",
                           "system.with_feedback", "system.table", "system.chart"]),
    ("Help", ["sdata.show_all_words", "sdata.help", "sdata.show_lesson", "sdata.show_packages_used"]),
    ("30 days of simplydata", ["sdata.start_30_days", "sdata.show_today", "sdata.show_day", "sdata.show_answers",
                               "sdata.go_to_next_day"]),
]

# Options that work inside several chart steps. They are not steps, so they are
# described here.
OPTIONS = {
    "show=": dict(
        about="What each bar or point on a line stands for, when a group has many rows.",
        text=(
            'show="average" (the normal choice) adds up the values and divides by how many '
            'there are. show="median" is the middle value when they are put in order. '
            'show="total" adds them all up. show="count" counts the rows (bars only). '
            'show="smallest", "biggest" and "standard deviation" work too. The names are '
            'the same as the table words: find_average_of, find_median_of, find_total_of, find_smallest_of ...'
        ),
        words=["draw_bars", "draw_lines"],
        example='chart.draw_bars(x="class", y="marks", show="median")',
    ),
    "error=": dict(
        about="Error bars on top of averages: how spread out, or how sure, the values are.",
        text=(
            'error="standard deviation" shows how far the values usually are from the '
            'average: how spread out they are. error="standard error" shows how sure we are '
            'about the average itself; it gets smaller as you collect more values. '
            'error="confidence interval" is the 95 % confidence interval: the range the true '
            'average is very likely to be in. Lines get a shaded band instead of bars. A line '
            'is printed saying which one was drawn, so your figure caption can say it too. '
            'The short forms "sd", "se" and "ci" also work.'
        ),
        words=["draw_bars", "draw_lines"],
        example='chart.draw_bars(x="class", y="marks", error="standard deviation")',
    ),
}

# A few words have something extra worth saying in their help.
EXTRA_NOTES = {
    "use_colour": (
        'Inside a chart step, colour= does more: colour="class" gives each class its own '
        'colour (and a legend), and colour="red" makes that one step red.'
    ),
    "show": (
        'Not the same as the show= option inside draw_bars and draw_lines: for that, type '
        'sdata.help("show=").'
    ),
    "draw_error_bars": (
        'Standard deviation or standard error? The standard deviation describes the values '
        '(how spread out they are). The standard error describes the average (how sure we '
        'are of it). Say in your caption which one you drew.'
    ),
    "save": (
        'File types: .png (a picture), .pdf and .svg (sharp at any size, good for printing), '
        '.eps (for journals that ask for it), .jpg, .tif, and .gif for animations. resolution= is how '
        'sharp a picture is, in dots per inch (dpi): 300 is normal, journals often ask for 300 or 600 (dpi= '
        'means the same). quality="high" is the same as resolution=600. .tif files are compressed without '
        'losing anything. Text in .pdf, .svg and .eps files stays real text (fonts kept as TrueType), as '
        'journals ask. see_through=True leaves out the white background, for a logo or a coloured slide. '
        'To choose the size of the file in cm, mm or pixels, use chart.set_size() first.'
    ),
    "set_size": (
        'unit= is "inches" (the normal choice), "cm", "mm" or "pixels". A saved file is exactly '
        'this size. With "pixels" the picture has exactly that many pixels whatever the '
        'resolution= in chart.save(). Text keeps its size, so a small chart for a paper (about '
        '8 cm wide) usually also needs smaller text: chart.use_font_size(8).'
    ),
}



def needs_r_text(what: str, packages=("vegan", "survival", "mice", "emmeans")) -> str:
    """The "Needs R" box of a lesson or day: what needs R, and how to get it, in plain words."""
    listed = ", ".join(f'"{p}"' for p in packages)
    return (f"{what} run R's own code, the same code R users run. Install it once: "
            'pip install "simplydata[r]", then R from https://cran.r-project.org, then in R: '
            f"install.packages(c({listed})). Without R these words print a message "
            "that says what to install.")


def _ex(table: str, body: str, file: str) -> str:
    """A runnable example: load an example table, start a chart, do the steps, save."""
    lines = ["import simplydata as sdata", f'{table} = sdata.get_example("{table}")',
             f"chart = sdata.chart({table})"]
    lines += textwrap.dedent(body).strip().splitlines()
    lines.append(f'chart.save("{file}.png")')
    return "\n".join(lines)


def _tx(name: str, body: str) -> str:
    """A runnable table example: start a table from a practice table, then the steps."""
    lines = ["import simplydata as sdata", f'table = sdata.table(sdata.get_example("{name}"))']
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _nx(body: str, values: str = "[12, 15, 9, 20, 14]") -> str:
    """A runnable numbers example: make some numbers (or take a column of a practice table), then the steps."""
    made = values if values.startswith("sdata.get_example(") else f"sdata.numbers({values})"
    lines = ["import simplydata as sdata", f"nums = {made}"]
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _dx(body: str) -> str:
    """A runnable distribution example: make a distribution, then the steps."""
    lines = ["import simplydata as sdata", 'dist = sdata.distribution("normal", average=50, standard_deviation=10)']
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _system_x(body: str, formula: str = "1 / (s**2 + 2*s + 5)") -> str:
    """A runnable system example: make a system, then the steps."""
    lines = ["import simplydata as sdata", f'system = sdata.system("{formula}")']
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _gx(body: str) -> str:
    """A runnable grid example: make a grid of numbers, then the steps."""
    lines = ["import simplydata as sdata", "grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])"]
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _bx(body: str) -> str:
    """A runnable example on a bigger grid (4 rows, 6 columns), for choosing parts of it."""
    lines = ["import simplydata as sdata", "grid = sdata.numbers(1, to=24).make_number_grid(columns=6)"]
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _kx(body: str) -> str:
    """A runnable block example: a plate of 24 hours x 8 rows x 12 columns, then the steps (NumPy + SciPy batch 1)."""
    lines = ["import simplydata as sdata",
             'block = sdata.number_block(of_shape=(24, 8, 12), filled_with=0.5, directions_named=["hour", "row", "column"])']
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


_SEA = ('block = sdata.number_block(sdata.make_random_numbers(of_shape=(36, 4, 5), average=12, standard_deviation=2, '
        'with_seed=1), directions_named=["time", "latitude", "longitude"], with_labels={"time": dates, '
        '"latitude": [62, 61, 60, 59], "longitude": [1, 2, 3, 4, 5]})')


def _seax(body: str) -> str:
    """A runnable example on a block with dates: 36 months x 4 latitudes x 5 longitudes of made-up sea temperatures
    (NumPy + SciPy batch 2)."""
    lines = ["import simplydata as sdata", 'dates = sdata.make_run_of_dates("2010-01", how_many=36, every="month")',
             _SEA]
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _lx(body: str) -> str:
    """A runnable example on a labelled block: the island's heights by east and north (labels from the table)."""
    lines = ["import simplydata as sdata",
             'block = sdata.number_block(sdata.get_example("island"), directions_named=["east", "north"], '
             'values="height")']
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


# S3c-1: six genes of the resistome practice table, for the short examples
_SIX_GENES = '["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"]'

HELP_EXAMPLES = {
    # start, show, save
    "sdata.chart": _ex("marks", 'chart.draw_dots(x="hours", y="marks")', "my_chart"),
    "sdata.get_example": textwrap.dedent("""\
        import simplydata as sdata
        sdata.get_example()
        marks = sdata.get_example("marks")
        print(marks)"""),
    "show": _ex("marks", 'chart.draw_bars(x="name", y="marks")\nchart.show()', "marks"),
    "get_numbers_drawn": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.fit_line()\n'
                                      'drawn = chart.get_numbers_drawn()\nprint(drawn)', "numbers_drawn"),
    "save": textwrap.dedent("""\
        import simplydata as sdata
        marks = sdata.get_example("marks")
        chart = sdata.chart(marks)
        chart.draw_bars(x="name", y="marks")
        chart.save("marks.png")
        chart.save("marks.pdf")
        chart.save("marks.tif", resolution=600)
        chart.save("marks_for_a_slide.png", see_through=True)"""),
    # charts phase, batch 1
    "get_text_drawn": _ex("marks", 'chart.draw_dots(x="hours", y="marks", colour="class")\n'
                                   'chart.write_title_on_top("More study, higher marks")\n'
                                   'text = chart.get_text_drawn()\n'
                                   'print(text.keep_rows_where("part", is_equal_to="title"))', "text_drawn"),
    "get_scales_drawn": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.use_log_scale_y()\n'
                                     'scales = chart.get_scales_drawn()\n'
                                     'print(scales.get_cell_at(row=2, column="kind"))', "scales_drawn"),
    "get_size": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.set_size(width=17, height=12, unit="cm")\n'
                             'width, height = chart.get_size(unit="cm")', "get_size"),
    "undo": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.use_log_scale_y()\nchart.undo()', "undo"),
    "write_letter": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.write_letter("B")', "write_letter"),
    "put_legend_inside": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city")\n'
                                        'chart.put_legend_inside("top left")', "put_legend_inside"),
    "use_shapes": _ex("marks", 'chart.draw_dots(x="hours", y="marks", colour="class")\n'
                               'chart.use_shapes("circle", "square", "triangle")', "use_shapes"),
    # chart types
    "draw_bars": _ex("marks", 'chart.draw_bars(x="name", y="marks", colour="class")\nchart.rotate_labels_x()', "draw_bars"),
    "draw_lines": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city", with_dots=True)', "draw_lines"),
    "draw_dots": _ex("marks", 'chart.draw_dots(x="hours", y="marks", colour="class", size="height")', "draw_dots"),
    "draw_area": _ex("growth", 'chart.draw_area(x="year", y="population", colour="country", stacked=True)', "draw_area"),
    "draw_histogram": _ex("marks", 'chart.draw_histogram(x="marks", with_bins=10)', "draw_histogram"),
    "draw_boxes": _ex("marks", 'chart.draw_boxes(x="class", y="marks")', "draw_boxes"),
    "draw_violins": _ex("marks", 'chart.draw_violins(x="subject", y="marks")', "draw_violins"),
    "draw_heatmap": _ex("weather", 'chart.draw_heatmap(x="month", y="city", value="rain", with_numbers=True)', "draw_heatmap"),
    "draw_pie": _ex("fruit", 'chart.draw_pie(labels="fruit", values="count")', "draw_pie"),
    "draw_polar": _ex("weather", 'chart.draw_polar(angle="wind_direction", distance="wind_speed", colour="city")', "draw_polar"),
    "draw_contour": _ex("island", 'chart.draw_contour(x="east", y="north", z="height")', "draw_contour"),
    "draw_surface": _ex("island", 'chart.draw_surface(x="east", y="north", z="height")', "draw_surface"),
    "draw_dots_3d": _ex("marks", 'chart.draw_dots_3d(x="hours", y="height", z="marks", colour="class")', "draw_dots_3d"),
    "draw_band": textwrap.dedent("""\
        import simplydata as sdata
        table = sdata.table(sdata.get_example("weather"))
        table.keep_rows_where("city", is_equal_to="Sunnyvale")
        table.add_column("lowest", "temperature - 4")
        table.add_column("highest", "temperature + 4")
        chart = table.start_chart()
        chart.draw_band(x="month", between=["lowest", "highest"], labelled="4 degrees either side")
        chart.draw_lines(x="month", y="temperature")
        chart.save("band.png")"""),
    "draw_map_of_empty_cells": _ex("shop", 'chart.draw_map_of_empty_cells()\nchart.write_title_on_top("Where the empty cells are")', "draw_map_of_empty_cells"),
    # statistics
    "show=": _ex("marks", 'chart.draw_bars(x="class", y="marks", show="median")', "median"),
    "error=": _ex("marks", 'chart.draw_bars(x="class", y="marks", error="standard deviation")', "error"),
    "draw_error_bars": _ex("marks", 'chart.draw_lines(x="subject", y="marks", colour="class")\n'
                      'chart.draw_error_bars("standard error")', "draw_error_bars"),
    "fit_line": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\n'
                    'chart.fit_line(with_confidence_band=True, show_equation=True)', "fit_line"),
    "fit_curve": _ex("weather", 'chart.draw_dots(x="month_number", y="temperature", colour="city")\nchart.fit_curve(of_degree=2)', "fit_curve"),
    "fit_formula": _ex("growth", 'chart.draw_dots(x="year", y="population", colour="country")\n'
                       'chart.fit_formula("population = a * exp(b * (year - 2000))")', "fit_formula"),
    "fit_distribution": _ex("marks", 'chart.draw_histogram(x="marks", show="density")\nchart.fit_distribution("normal")',
                            "fit_distribution"),
    "draw_curve": _ex("marks", 'chart.draw_histogram(x="marks", show="density")\n'
                 'chart.draw_curve(sdata.distribution("normal", average=60, standard_deviation=15), labelled="a bell curve")',
                 "draw_curve"),
    "draw_smooth_line": _ex("weather", 'chart.draw_dots(x="month_number", y="rain", colour="city")\nchart.draw_smooth_line()', "draw_smooth_line"),
    "draw_density": _ex("marks", 'chart.draw_density(x="marks", colour="class")', "draw_density"),
    "draw_qq_dots": _ex("marks", 'chart.draw_qq_dots("marks")', "draw_qq_dots"),
    "draw_cumulative_share": _ex("marks", 'chart.draw_cumulative_share(x="marks", colour="class")', "draw_cumulative_share"),
    "draw_count_bars": _ex("fruit", 'chart.draw_count_bars(x="fruit", colour="shop")', "draw_count_bars"),
    "draw_all_dots": _ex("marks", 'chart.draw_boxes(x="class", y="marks")\nchart.draw_all_dots(x="class", y="marks")', "draw_all_dots"),
    "draw_side_histograms": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.draw_side_histograms()', "draw_side_histograms"),
    "sdata.draw_all_pairs": textwrap.dedent("""\
        import simplydata as sdata
        marks = sdata.get_example("marks")
        chart = sdata.draw_all_pairs(marks, colour="class")
        chart.write_title_on_top("Every number column against every other")
        chart.save("pairs.png")"""),
    # lines and shading
    "draw_line_at_x": _ex("growth", 'chart.draw_lines(x="year", y="population", colour="country")\nchart.draw_line_at_x(2010, labelled="2010")', "draw_line_at_x"),
    "draw_line_at_y": _ex("marks", 'chart.draw_bars(x="name", y="marks")\nchart.draw_line_at_y(50, labelled="pass mark")\nchart.rotate_labels_x()', "draw_line_at_y"),
    "draw_line_with_slope": _ex("marks", 'chart.draw_dots(x="hours", y="hours")\nchart.draw_line_with_slope(1, through=(0, 0))', "draw_line_with_slope"),
    "shade_between_x": _ex("weather", 'chart.draw_lines(x="month_number", y="temperature", colour="city")\nchart.shade_between_x(6, 8)', "shade_between_x"),
    "shade_between_y": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.shade_between_y(40, 60)', "shade_between_y"),
    # words on the chart
    "write_title_on_top": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.write_title_on_top("Marks in each class")', "write_title_on_top"),
    "write_caption_at_bottom": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.write_caption_at_bottom("Made-up data from sdata.get_example")', "write_caption_at_bottom"),
    "label_x": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.label_x("Hours of study")', "label_x"),
    "label_y": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.label_y("Marks (out of 100)")', "label_y"),
    "write_note": _ex("growth", 'chart.draw_lines(x="year", y="population", colour="country")\nchart.write_note("Cherria grows fastest", x=2020, y=12, with_arrow=True)', "write_note"),
    "write_names_on_dots": textwrap.dedent("""\
        import simplydata as sdata
        table = sdata.table(sdata.get_example("marks"))
        table.keep_rows_where("subject", is_equal_to="Maths")
        chart = table.start_chart()
        chart.draw_dots(x="hours", y="marks")
        chart.write_names_on_dots("name")
        chart.save("names_on_dots.png")"""),
    "write_numbers_on_bars": _ex("fruit", 'chart.draw_bars(x="fruit", y="count", show="total")\nchart.write_numbers_on_bars()', "write_numbers_on_bars"),
    "use_font_size": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.write_title_on_top("Big text")\nchart.use_font_size(18)', "use_font_size"),
    "use_font": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.use_font("DejaVu Serif")', "use_font"),
    # axes
    "set_range_x": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.set_range_x(0, 10)', "set_range_x"),
    "set_range_y": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.set_range_y(0, 100)', "set_range_y"),
    "use_log_scale_x": _ex("growth", 'chart.draw_dots(x="population", y="forest", colour="country")\nchart.use_log_scale_x()', "use_log_scale_x"),
    "use_log_scale_y": _ex("growth", 'chart.draw_lines(x="year", y="population", colour="country")\nchart.use_log_scale_y()', "use_log_scale_y"),
    "write_ticks_x_as": _ex("growth", 'chart.draw_dots(x="population", y="forest")\nchart.write_ticks_x_as("thousands")', "write_ticks_x_as"),
    "write_ticks_y_as": _ex("growth", 'chart.draw_lines(x="year", y="forest", colour="country")\nchart.write_ticks_y_as("percent")', "write_ticks_y_as"),
    "put_ticks_x": _ex("weather", 'chart.draw_lines(x="month_number", y="rain", colour="city")\n'
                   'chart.put_ticks_x(1, 4, 7, 10, labels=["Jan", "Apr", "Jul", "Oct"])', "put_ticks_x"),
    "put_ticks_y": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.put_ticks_y(0, 25, 50, 75)', "put_ticks_y"),
    "rotate_labels_x": _ex("marks", 'chart.draw_bars(x="name", y="marks")\nchart.rotate_labels_x(45)', "rotate_labels_x"),
    "rotate_labels_y": _ex("fruit", 'chart.draw_bars(x="fruit", y="count", sideways=True)\nchart.rotate_labels_y(30)', "rotate_labels_y"),
    "add_second_y": _ex("weather", 'chart.draw_lines(x="month", y="temperature")\nchart.add_second_y("rain", drawn_as="bars", labelled="Rain (mm)")', "add_second_y"),
    "flip_x": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.flip_x()', "flip_x"),
    "flip_y": _ex("island", 'chart.draw_contour(x="east", y="north", z="height")\nchart.flip_y()', "flip_y"),
    # colours and look
    "use_colour": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.use_colour("purple")', "use_colour"),
    "use_colour_scale": _ex("weather", 'chart.draw_heatmap(x="month", y="city", value="rain")\nchart.use_colour_scale("magma")', "use_colour_scale"),
    "use_colours": _ex("marks", 'chart.draw_bars(x="subject", y="marks", colour="class")\nchart.use_colours("orange", "teal", "purple")', "use_colours"),
    "use_style": _ex("marks", 'chart.draw_bars(x="subject", y="marks", colour="class")\nchart.use_style("school")', "use_style"),
    "set_size": _ex("weather", 'chart.draw_lines(x="month", y="rain", colour="city")\nchart.set_size(width=17, height=8, unit="cm")', "set_size"),
    "show_grid": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.show_grid()', "show_grid"),
    "hide_grid": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.hide_grid()', "hide_grid"),
    "put_legend_at_top": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city")\nchart.put_legend_at_top()', "put_legend_at_top"),
    "put_legend_at_bottom": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city")\nchart.put_legend_at_bottom()', "put_legend_at_bottom"),
    "put_legend_on_left": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city")\nchart.put_legend_on_left()', "put_legend_on_left"),
    "put_legend_on_right": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city")\nchart.put_legend_on_right()', "put_legend_on_right"),
    "hide_legend": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city")\nchart.hide_legend()', "hide_legend"),
    "show_legend": _ex("weather", 'chart.draw_lines(x="month", y="temperature", colour="city")\nchart.hide_legend()\n'
                       'chart.show_legend()', "show_legend"),
    "label_legend": _ex("marks", 'chart.draw_dots(x="hours", y="marks", colour="class")\nchart.label_legend("Class")',
                        "label_legend"),
    "order_x": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.order_x("C", "B", "A")', "order_x"),
    "order_y": _ex("marks", 'chart.draw_bars(x="class", y="marks", sideways=True)\nchart.order_y("C", "B", "A")', "order_y"),
    "order_legend": _ex("marks", 'chart.draw_bars(x="class", y="marks", colour="subject")\n'
                        'chart.order_legend("Science", "Maths", "English")', "order_legend"),
    "label_colour_bar": _ex("island", 'chart.draw_contour(x="east", y="north", z="height")\n'
                            'chart.label_colour_bar("Height (m)")', "label_colour_bar"),
    # several charts
    "draw_one_chart_for_each_group_in": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.draw_one_chart_for_each_group_in("class", per_row=3)',
                         "draw_one_chart_for_each_group_in"),
    "sdata.put_side_by_side": textwrap.dedent("""\
        import simplydata as sdata
        marks = sdata.get_example("marks")
        a = sdata.chart(marks).draw_bars(x="class", y="marks").write_title_on_top("Average")
        b = sdata.chart(marks).draw_boxes(x="class", y="marks").write_title_on_top("Spread")
        charts = sdata.put_side_by_side(a, b, same_y=True)
        charts.save("side_by_side.png")"""),
    "sdata.put_one_above_other": textwrap.dedent("""\
        import simplydata as sdata
        weather = sdata.get_example("weather")
        a = sdata.chart(weather).draw_lines(x="month", y="temperature", colour="city")
        b = sdata.chart(weather).draw_bars(x="month", y="rain", colour="city")
        charts = sdata.put_one_above_other(a, b)
        charts.save("one_above_other.png")"""),
    "sdata.put_in_rows_and_columns": textwrap.dedent("""\
        import simplydata as sdata
        marks = sdata.get_example("marks")
        a = sdata.chart(marks).draw_bars(x="class", y="marks")
        b = sdata.chart(marks).draw_histogram(x="marks")
        c = sdata.chart(marks).draw_dots(x="hours", y="marks")
        d = sdata.chart(marks).draw_boxes(x="subject", y="marks")
        charts = sdata.put_in_rows_and_columns(a, b, c, d, per_row=2)
        charts.write_title_on_top("Four ways to look at the marks")
        charts.save("grid.png")"""),
    "add_zoom_box": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\n'
                    'chart.add_zoom_box(x_between=[2, 4], y_between=[40, 60], where="top left")', "add_zoom_box"),
    "animate": textwrap.dedent("""\
        import simplydata as sdata
        growth = sdata.get_example("growth")
        chart = sdata.chart(growth)
        chart.draw_bars(x="country", y="population")
        chart.set_range_y(0, 50)
        chart.animate(over="year")
        chart.save("growth.gif")"""),
    # tables: start and look
    "sdata.table": _tx("marks", "table.show_first_rows()"),
    "table.show_first_rows": _tx("marks", "table.show_first_rows(10)"),
    "table.show_last_rows": _tx("marks", "table.show_last_rows(3)"),
    "table.show": _tx("marks", 'table.keep_rows_where("class", is_equal_to="A")\ntable.show(rows=10)'),
    "table.get_column_names": _tx("marks", "print(table.get_column_names())"),
    "table.get_column": _tx("marks", 'marks = table.get_column("marks")\nmarks.find_average()\nmarks.find_percentile(90)'),
    "table.describe_columns": _tx("marks", "table.describe_columns()"),
    "table.get_row": _tx("marks", 'print(table.get_row(3))\nprint(table.get_row("last"))'),
    "table.get_cell_at": _tx("marks", 'print(table.get_cell_at(row=3, column="marks"))\n'
                                  'print(table.get_cell_at(row="last", column="name"))'),
    # choose columns
    "table.keep_columns": _tx("marks", 'table.keep_columns("name", "marks")\ntable.show_first_rows()\n'
                                       'table.start_again()\ntable.keep_columns("hours", to="height")\n'
                                       'table.start_again()\ntable.keep_columns(of_kind="number")\n'
                                       'table.show_first_rows()'),
    "table.remove_columns": _tx("marks", 'table.remove_columns("height")\nprint(table.get_column_names())\n'
                                         'table.remove_columns(of_kind="text")\nprint(table.get_column_names())'),
    "table.keep_columns_by_position": _tx("marks", "table.keep_columns_by_position(1, to=3)\n"
                                                   "table.show_first_rows()"),
    "table.remove_columns_by_position": _tx("marks", "table.remove_columns_by_position(1)\n"
                                                     "print(table.get_column_names())"),
    "table.rename_column": _tx("marks", 'table.rename_column("marks", to="score")\ntable.show_first_rows()'),
    "table.clean_column_names": _tx("fjord_stations", "table.clean_column_names()\ntable.show_first_rows()"),
    # choose rows
    "table.keep_rows_where": _tx("marks", 'table.keep_rows_where("marks", is_above=50)\n'
                                    'table.keep_rows_where("subject", is_one_of=["Maths", "Science"])\n'
                                    "table.keep_rows_where(\"hours > 5 and class != 'C'\")\ntable.show_first_rows()"),
    "table.remove_rows_where": _tx("marks", 'table.remove_rows_where("subject", is_equal_to="English")\ntable.show_first_rows()'),
    "table.keep_first_rows": _tx("marks", "table.keep_first_rows(10)\nprint(table)\ntable.undo()\n"
                                          'table.sort_by("marks", biggest_first=True)\n'
                                          'table.keep_first_rows(2, for_each_group_in="subject")\ntable.show()'),
    "table.keep_last_rows": _tx("marks", "table.keep_last_rows(10)\nprint(table)"),
    "table.keep_rows_by_position": _tx("marks", "table.show_last_rows(3)\n"
                                                "table.keep_rows_by_position(10, to=20)\n"
                                                "table.keep_rows_by_position(1, step=2)\ntable.show()"),
    "table.remove_rows_by_position": _tx("marks", "table.remove_rows_by_position([12, 40])\n"
                                                  "table.remove_rows_by_position(1, step=2)\ntable.count_rows()"),
    "table.reverse_rows": _tx("marks", "table.reverse_rows()\ntable.show_first_rows(3)"),
    "table.keep_random_rows": _tx("marks", "table.keep_random_rows(10, with_seed=1)\nprint(table)"),
    "table.remove_duplicate_rows": _tx("marks", 'table.remove_duplicate_rows(columns=["name"])\nprint(table)\n'
                                                'table.undo()\n'
                                                'table.remove_duplicate_rows(columns=["name"], keep="last")\nprint(table)'),
    "table.show_duplicate_rows": _tx("fjord_lab", "table.remove_rows_that_are_all_empty()\n"
                                                  "table.show_duplicate_rows()\n"
                                                  'table.show_duplicate_rows(columns=["sample_id", "gene"])\n'
                                                  "table.remove_duplicate_rows()"),
    "table.keep_groups_where": _tx("school", 'table.keep_groups_where("average(marks) >= 50", '
                                             'for_each_group_in="school")\n'
                                             'table.find_average_of("marks", for_each_group_in="school")'),
    "table.remove_groups_where": _tx("school", 'table.remove_groups_where("average(marks) < 50", '
                                               'for_each_group_in="school")\n'
                                               'table.count_rows(for_each_group_in="school")'),
    "table.repeat_each_row_by": "\n".join(['import simplydata as sdata',
                                           'table = sdata.table({"answer": ["yes", "no"], "count": [12, 5]})',
                                           'table.repeat_each_row_by("count")', 'print(table)']),
    "table.keep_biggest_rows": _tx("marks", 'table.keep_biggest_rows(3, by="marks", for_each_group_in="subject")\ntable.show()'),
    "table.keep_smallest_rows": _tx("marks", 'table.keep_smallest_rows(3, by="marks", for_each_group_in="subject")\ntable.show()'),
    "table.show_rows_with_outliers": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                                  'table.show_rows_with_outliers("marks", for_each_group_in="class")'),
    "table.remove_rows_with_outliers": _tx("marks", 'table.remove_rows_with_outliers("marks", for_each_group_in="subject")\n'
                                                    "table.show_steps()"),
    # empty cells (the shop table has some)
    "table.count_empty_cells_in": _tx("shop", "table.count_empty_cells_in()"),
    "table.remove_rows_with_empty_cells_in": _tx("shop", 'table.remove_rows_with_empty_cells_in("sales")\nprint(table)'),
    "table.fill_empty_cells_in": _tx("shop", 'table.fill_empty_cells_in("customers", with_the="median")\n'
                                          'table.fill_empty_cells_in("sales", with_the="line between neighbours", '
                                          'sorted_by="date", for_each_group_in="shop")\ntable.count_empty_cells_in()'),
    "table.remove_rows_that_are_all_empty": _tx("fjord_lab", "table.count_rows()\n"
                                                         "table.remove_rows_that_are_all_empty()\n"
                                                         "table.count_empty_cells_in()"),
    "table.remove_columns_that_are_all_empty": _tx("fjord_lab", "table.remove_columns_that_are_all_empty()\n"
                                                            "print(table.get_column_names())"),
    "table.add_is_empty_column": _tx("shop", 'table.add_is_empty_column("sales_was_empty", from_column="sales")\n'
                                             'table.fill_empty_cells_in("sales", with_the="line between neighbours", '
                                             'sorted_by="date", for_each_group_in="shop")\n'
                                             'table.keep_rows_where("sales_was_empty")\ntable.show()'),
    # fix columns
    "table.turn_into_numbers": _tx("marks", 'table.turn_into_numbers("marks")\ntable.describe_columns()'),
    "table.turn_into_text": _tx("weather", 'table.turn_into_text("month_number")\ntable.describe_columns()'),
    "table.turn_into_dates": _tx("growth", 'table.turn_into_dates("year")\ntable.show_first_rows()'),
    "table.turn_into_lowercase": _tx("marks", 'table.turn_into_lowercase("name")\ntable.show_first_rows()'),
    "table.turn_into_uppercase": _tx("marks", 'table.turn_into_uppercase("name")\ntable.show_first_rows()'),
    "table.remove_extra_spaces_in": _tx("marks", 'table.remove_extra_spaces_in("name")\ntable.show_first_rows()'),
    "table.replace_values_in": _tx("marks", 'table.replace_values_in("subject", "Maths", with_value="Math")\n'
                                         'table.count_each("subject")\n'
                                         'table.replace_values_in("marks", is_above=90, with_value=90)\n'
                                         'table.find_biggest_of("marks")'),
    "table.round_numbers_in": _tx("marks", 'table.round_numbers_in("hours", 0)\ntable.show_first_rows()'),
    "table.change_column": _tx("marks", 'table.change_column("marks", "marks / 10")\ntable.show_first_rows()\n'
                                         'table.change_column("class", value="A or B", in_rows_where="class != \'C\'")\n'
                                         'table.count_each("class")'),
    "table.turn_into_categories": _tx("clinic", 'table.turn_into_categories("nurse_rating", in_order=["mild", '
                                                '"moderate", "severe"])\n'
                                                'table.find_average_of("pain_week_0", for_each_group_in="nurse_rating")'),
    # sort and new columns
    "table.sort_by": _tx("marks", 'table.sort_by("marks", biggest_first=True)\ntable.show_first_rows()'),
    "table.add_column": _tx("marks", 'table.add_column("study_and_marks", by_adding=["hours", "marks"])\n'
                                     'table.add_column("marks_per_hour", "marks / hours")\ntable.show_first_rows()'),
    "table.add_group_column": _tx("marks", 'table.add_group_column("grade", from_column="marks", '
                                           'cut_at=[40, 60, 80], names=["D", "C", "B", "A"])\n'
                                           'table.count_each("grade")'),
    "table.add_row_summary_column": _tx("clinic", 'table.add_row_summary_column("pain_average", '
                                                  'columns=["pain_week_0", "pain_week_4", "pain_week_8"], '
                                                  'show="average")\n'
                                                  'table.keep_columns("patient", "pain_week_0", "pain_week_4", '
                                                  '"pain_week_8", "pain_average")\ntable.show_first_rows()'),
    "table.add_row_number_column": _tx("river", 'table.add_row_number_column("day_number", for_each_group_in="station", '
                                                'sorted_by="date")\ntable.show_last_rows(3)'),
    "table.add_z_score_column": _tx("marks", 'table.add_z_score_column("marks_z", from_column="marks", '
                                             'for_each_group_in="subject")\ntable.show_first_rows()'),
    "table.find_interval_of": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                           'table.find_interval_of("marks", "median", for_each_group_in="class")'),
    "table.add_rank_column": _tx("marks", 'table.add_rank_column("place", from_column="marks")\n'
                                          'table.sort_by("place")\ntable.show_first_rows()'),
    # dates and text
    "table.add_column_with_part_of_date": _tx("shop", 'table.add_column_with_part_of_date("weekday", from_column="date", '
                                              'part="weekday name")\n'
                                              'table.find_average_of("sales", for_each_group_in="weekday")'),
    "table.add_column_with_part_of_text": _tx("marks", 'table.add_column_with_part_of_text("initial", from_column="name", '
                                               'first_characters=1)\ntable.show_first_rows()'),
    "table.split_column": _tx("fruit", 'table.split_column("shop", separator=" ", into=["shop_kind", "shop_word"])\n'
                                       "table.show_first_rows()"),
    "table.split_into_rows": _tx("fjord_samples", 'table.split_into_rows("crew", separator=";")\n'
                                                  'table.count_each("crew")'),
    "table.replace_text_in": _tx("fruit", 'table.replace_text_in("shop", " shop", with_value="")\ntable.count_each("shop")'),
    # row after row
    "table.add_rolling_column": _tx("weather", 'table.add_rolling_column("rain_3_months", from_column="rain", window=3, '
                                               'show="total", for_each_group_in="city", sorted_by="month_number")\n'
                                               "table.show_first_rows()"),
    "table.add_running_column": _tx("shop", 'table.add_running_column("sales_so_far", from_column="sales", '
                                            'show="total", for_each_group_in="shop", sorted_by="date")\n'
                                            "table.show_first_rows()"),
    "table.add_previous_value_column": _tx("weather", 'table.add_previous_value_column("last_month", '
                                                      'from_column="temperature", for_each_group_in="city", '
                                                      'sorted_by="month_number")\ntable.show_first_rows()'),
    "table.add_change_column": _tx("growth", 'table.add_change_column("growth", from_column="population", '
                                             'in_percent=True, for_each_group_in="country", sorted_by="year")\n'
                                             "table.show_first_rows()"),
    # summaries
    "table.count_rows": _tx("marks", 'table.count_rows()\ntable.count_rows(for_each_group_in="class")'),
    "table.count_each": _tx("fruit", 'table.count_each("fruit")'),
    "table.find_average_of": _tx("marks", 'table.find_average_of("marks")\n'
                                     'by_class = table.find_average_of("marks", for_each_group_in="class")\nprint(by_class)'),
    "table.find_median_of": _tx("marks", 'table.find_median_of("marks", for_each_group_in="class")'),
    "table.find_total_of": _tx("fruit", 'table.find_total_of("count", for_each_group_in="shop")'),
    "table.find_smallest_of": _tx("weather", 'table.find_smallest_of("temperature", for_each_group_in="city")'),
    "table.find_biggest_of": _tx("weather", 'table.find_biggest_of("temperature", for_each_group_in="city")'),
    "table.find_standard_deviation_of": _tx("marks", 'table.find_standard_deviation_of("marks", for_each_group_in="class")'),
    "table.find_summary_of": _tx("marks", 'table.find_summary_of("marks", for_each_group_in="class", '
                                     'show=["average", "standard deviation", "count"])'),
    "table.find_percent_of_rows_where": _tx("marks", 'table.find_percent_of_rows_where("marks", is_above=60, for_each_group_in="class")'),
    "table.count_different_values_in": _tx("marks", 'table.count_different_values_in("name", for_each_group_in="class")'),
    "table.find_percentile_of": _tx("marks", 'table.find_percentile_of("marks", 90, for_each_group_in="class")'),
    "table.find_most_common_of": _tx("school", 'table.find_most_common_of("days_absent", for_each_group_in="school")'),
    "table.find_correlation_between": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                                   'table.find_correlation_between("hours", "marks")'),
    # statistical tests
    "table.compare_averages_of": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                           'result = table.compare_averages_of("marks", for_each_group_in="class")\n'
                                           'table.compare_averages_of("marks", for_each_group_in="class", based_on="ranks")\n'
                                           'table.undo()\n'
                                           'table.compare_averages_of("marks", for_each_group_in="subject", matched_by="name")\n'
                                           'result.save("marks_test.csv")'),
    "table.compare_each_pair_of": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                               'table.compare_each_pair_of("marks", for_each_group_in="class")'),
    "table.compare_before_and_after": _tx("marks", 'table.keep_columns("name", "subject", "marks")\n'
                                               'table.spread_into_columns(names_from="subject", values_from="marks")\n'
                                               'table.compare_before_and_after("Maths", "Science")'),
    "table.compare_average_to": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                             'table.compare_average_to("marks", 60)'),
    "table.compare_counts_of": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                            'table.add_group_column("result", from_column="marks", cut_at=[60], '
                                         'names=["below 60", "60 or more"])\n'
                                         'table.compare_counts_of("result", for_each_group_in="class")'),
    # fitting
    "table.fit_line": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                   'table.fit_line(x="hours", y="marks")'),
    "table.fit_curve": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                    'table.fit_curve(x="hours", y="marks", of_degree=2)'),
    "table.fit_formula": _tx("growth", 'table.fit_formula("population = a * exp(b * (year - 2000))", '
                                       'for_each_group_in="country")\n'
                                       'table.keep_rows_where("country", is_equal_to="Applia")\n'
                                       'table.fit_formula("population = a * exp(b * (year - 2000))")'),
    # finding and solving
    "sdata.find_where_smallest": textwrap.dedent("""\
        import simplydata as sdata
        sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5])
        sdata.find_where_smallest("(x - 1)**2 + (y - 2)**2", start={"x": 0, "y": 0})"""),
    "sdata.find_where_biggest": textwrap.dedent("""\
        import simplydata as sdata
        sdata.find_where_biggest("x * (10 - x)", between=[0, 10])
        sdata.find_where_biggest("3*x + 2*y", rules=["x + y <= 4", "x + 3*y <= 6", "x >= 0", "y >= 0"])"""),
    "sdata.solve": textwrap.dedent("""\
        import simplydata as sdata
        sdata.solve("x**3 - 2*x = 5", between=[0, 3])
        sdata.solve("x**2 - 2*x + 5 = 0")
        sdata.solve(["x + y = 3", "x * y = 2"], start={"x": 0, "y": 1})"""),
    # values between points
    "table.find_values_at": _tx("growth", 'estimates = table.find_values_at("population", at={"year": [2001, 2003, 2011]}, '
                                     'for_each_group_in="country")\nestimates.show()\n'
                                     'table.find_values_at("population", at={"year": [2001, 2003, 2011]}, '
                                     'joined_by="smooth curve", for_each_group_in="country")'),
    "table.make_map_of": _tx("island", 'heights = table.make_map_of("height", across=["east", "north"], steps=60, '
                                  'joined_by="smooth surface")\nchart = heights.start_chart()\n'
                                  'chart.draw_contour(x="east", y="north", z="height")\nchart.save("map_of.png")'),
    # distributions
    "sdata.distribution": textwrap.dedent("""\
        import simplydata as sdata
        dist = sdata.distribution("normal", average=50, standard_deviation=10)
        print(dist)
        dist.find_chance_that_value(is_above=80)
        coins = sdata.distribution("binomial", tries=10, chance=0.5)
        coins.find_chance_that_value(is_at_most=3)"""),
    "table.fit_distribution_to": _tx("shop", 'fit = table.fit_distribution_to("sales", "lognormal")\n'
                                          "fit.find_chance_that_value(is_above=600)\nfit.turn_into_table()"),
    "table.compare_distributions_for": _tx("shop", 'table.compare_distributions_for("sales")'),
    "nums.fit_distribution": _nx('fit = nums.fit_distribution("gamma")\nfit.find_chance_that_value(is_above=18)'),
    "dist.find_chance_that_value": _dx("dist.find_chance_that_value(is_above=80)\ndist.find_chance_that_value(is_between=[40, 60])\n"
                       'dice = sdata.distribution("whole number uniform", between=[1, 6])\ndice.find_chance_that_value(6)'),
    "dist.find_density_at": _dx("dist.find_density_at(60)"),
    "dist.find_percentile": _dx("dist.find_percentile(95)\ndist.find_percentile([5, 50, 95])"),
    "dist.find_cut_off": _dx("dist.find_cut_off(with_chance_above=0.025)\ndist.find_cut_off(with_chance_below=0.05)"),
    "dist.find_middle_range": _dx("dist.find_middle_range(95)"),
    "dist.find_average": _dx("dist.find_average()"),
    "dist.find_median": _dx("dist.find_median()"),
    "dist.find_standard_deviation": _dx("dist.find_standard_deviation()"),
    "dist.find_variance": _dx("dist.find_variance()"),
    "dist.show_summary": _dx("dist.show_summary()"),
    "dist.make_random_numbers": _dx("nums = dist.make_random_numbers(how_many=100, with_seed=1)\nnums.find_average()"),
    "dist.draw_chart": _dx('chart = dist.draw_chart()\nchart.write_title_on_top("Normal, average 50, standard deviation 10")\n'
                      'chart.save("distribution.png")'),
    "dist.turn_into_table": _dx("result = dist.turn_into_table()\nresult.show()"),
    "dist.show_parameters": _dx("print(dist.show_parameters())"),
    "table.compare_spreads_of": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                             'table.compare_spreads_of("marks", for_each_group_in="class")'),
    "table.compare_counts_to": _tx("school", 'table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})'),
    "table.compare_percent_to": _tx("school", 'table.compare_percent_to("passed", value="yes", percent=50)'),
    "table.compare_shape_to": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                           'table.compare_shape_to("marks", "normal", for_each_group_in="class")\n'
                                           'table.compare_shape_to("marks", "normal", test_method="jarque-bera")'),
    "table.compare_matched_columns": _tx("marks", 'table.keep_columns("name", "subject", "marks")\n'
                                          'table.spread_into_columns(names_from="subject", values_from="marks")\n'
                                          'table.compare_matched_columns("Maths", "Science", "English")'),
    "table.compare_shapes_of": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                            'table.compare_shapes_of("marks", for_each_group_in="class")'),
    "table.check_if_random_order": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                                'table.check_if_random_order("marks")'),
    "sdata.compare_averages": textwrap.dedent("""\
        import simplydata as sdata
        sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22])"""),
    "sdata.compare_counts": textwrap.dedent("""\
        import simplydata as sdata
        sdata.compare_counts([[20, 40], [30, 30]])"""),
    "table.compare_correlations": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                               'table.keep_rows_where("class", is_one_of=["A", "B"])\n'
                                               'table.compare_correlations("hours", "marks", for_each_group_in="class")'),
    "table.compare_risks": _tx("trial", 'table.compare_risks("died", for_each_group_in="treatment", against="usual care")'),
    "table.compare_rates": _tx("clinic", 'table.compare_rates("infections", time="patient_days", for_each_group_in="ward", '
                                         'against="ward A")'),
    "table.rate_of": _tx("clinic", 'table.rate_of("infections", time="patient_days", for_each_group_in="ward")'),
    "table.compare_balanced_groups_of": _tx("job_training", 'table.compare_balanced_groups_of("re78", '
                                                            'for_each_group_in="treat", allowing_for=["age", "educ", '
                                                            '"race", "married", "nodegree", "re74", "re75"])'),
    "sdata.compare_risks": textwrap.dedent("""\
        import simplydata as sdata
        sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new", "usual"], against="usual")"""),
    "sdata.compare_rates": textwrap.dedent("""\
        import simplydata as sdata
        sdata.compare_rates(events=[15, 30], time=[1200, 1100], names=["ward A", "ward B"])"""),
    "table.compare_to_truth": _tx("clinic", 'table.compare_to_truth("rapid_test", truth="infected")\n'
                                            'table.compare_to_truth("crp", truth="infected")'),
    "table.agreement_between": _tx("clinic", 'table.agreement_between("nurse_rating", "doctor_rating")\n'
                                             'table.agreement_between("device_a", "device_b")'),
    "table.limits_of_agreement": _tx("clinic", 'table.limits_of_agreement("device_a", "device_b")'),
    "table.reliability_of": _tx("clinic", 'table.reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])'),
    "table.compare_accuracy": _tx("clinic", 'table.compare_accuracy("crp", "procalcitonin", truth="infected")'),
    "sdata.compare_to_truth": textwrap.dedent("""\
        import simplydata as sdata
        sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)
        sdata.compare_to_truth(sensitivity=90, specificity=95, prevalence=1)"""),
    "table.add_adjusted_p_value_column": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                                      'table = table.find_correlation_between("hours", "marks", "height", '
                                                      'show="each pair")\n'
                                                      'table.add_adjusted_p_value_column("q", test_method="benjamini-hochberg")\n'
                                                      "table.show()"),
    # combine and reshape
    "table.join_with": _tx("marks", 'ages = {"name": ["Asha", "Ben"], "age": [12, 13]}\n'
                                    'table.join_with(ages, using="name", keep="all rows from this table")\n'
                                    "table.show_first_rows()\ntable.undo()\n"
                                    'students = {"student": ["Asha", "Zoe"], "age": [12, 11]}\n'
                                    'table.join_with(students, using={"name": "student"}, keep="all rows from both", '
                                    'check_that="each row has one match", with_match_column=True)\n'
                                    'table.count_each("found in")'),
    # tables phase, batch 3 (approved by Manish 2026-11-25)
    "table.add_zeros_in_front_of": _tx("fjord_samples", 'table.turn_into_text("sample_id")\n'
                                                        'table.add_zeros_in_front_of("sample_id", to_length=3)\n'
                                                        "table.show_first_rows(3)"),
    "table.move_columns": _tx("marks", 'table.move_columns("marks", to="start")\n'
                                       'table.move_columns("height", after="name")\n'
                                       "table.show_first_rows(3)"),
    "table.show_rows_with_empty_cells_in": _tx("shop", "table.show_rows_with_empty_cells_in()\n"
                                                       'table.show_rows_with_empty_cells_in(columns=["sales"])'),
    "table.show_differences_from": _tx("marks", 'table.show_differences_from(sdata.get_example("marks"))\n'
                                                'table.replace_values_in("marks", is_above=90, with_value=90)\n'
                                                'table.show_differences_from(sdata.get_example("marks"))'),
    "table.check_if_same_as": _tx("marks", 'table.check_if_same_as(sdata.get_example("marks"))\n'
                                           'table.round_numbers_in("hours", 0)\n'
                                           'table.check_if_same_as(sdata.get_example("marks"))'),
    "table.run_sql": _tx("river", 'table.run_sql("SELECT station, avg(nitrate) AS nitrate FROM data GROUP BY station")\n'
                                  'table.run_sql("SELECT * FROM data WHERE nitrate > 4.5 ORDER BY nitrate DESC LIMIT 5")'),
    "sdata.run_sql": "\n".join([
        "import simplydata as sdata",
        'sdata.get_example("river").save("river.csv")',
        "sdata.run_sql(\"SELECT station, avg(nitrate) AS nitrate FROM 'river.csv' GROUP BY station\")",
        "sdata.run_sql(\"SELECT * FROM 'river.csv' WHERE level > 3 ORDER BY level DESC LIMIT 5\")",
    ]),
    "table.make_one_table_for_each_group_in": _tx("river", 'tables = table.make_one_table_for_each_group_in("station")\n'
                                                           'tables["Station A"].find_average_of("nitrate")\n'
                                                           'tables["Station B"].find_average_of("nitrate")'),
    "table.as_list": _tx("marks", "rows = table.as_list()\nprint(rows[0])\nprint(rows[0][\"marks\"])"),
    "table.keep_rows_found_in": _tx("marks", 'table.keep_rows_found_in({"name": ["Asha", "Ben"]}, using="name")\n'
                                             'table.count_each("name")'),
    "table.remove_rows_found_in": _tx("marks", 'table.remove_rows_found_in({"name": ["Asha", "Ben"]}, using="name")\n'
                                               "table.count_rows()"),
    "table.add_rows_from": _tx("marks", 'table.add_rows_from(sdata.get_example("marks"))\nprint(table)'),
    "table.gather_into_rows": _tx("weather", 'table.keep_columns("month", "city", "temperature", "rain")\n'
                                                   'table.gather_into_rows(["temperature", "rain"])\n'
                                                   "table.show_first_rows()"),
    "table.spread_into_columns": _tx("weather", 'table.keep_columns("month", "city", "temperature")\n'
                                                'table.spread_into_columns(names_from="city", '
                                                'values_from="temperature")\ntable.show_first_rows()\n'
                                                'fruit = sdata.get_example("fruit")\n'
                                                'fruit.keep_columns("day", "fruit", "count")\n'
                                                'fruit.spread_into_columns(names_from="fruit", values_from="count", '
                                                'show="total")\nfruit.show()'),
    "table.swap_rows_and_columns": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\n'
                                                'table.keep_columns("name", "hours", "marks")\n'
                                                "table.swap_rows_and_columns()\nprint(table)"),
    # undo and finish
    "table.undo": _tx("marks", 'table.keep_rows_where("marks", is_above=50)\ntable.undo()\nprint(table)'),
    "table.show_steps": _tx("marks", 'table.keep_rows_where("marks", is_above=50)\ntable.sort_by("marks")\ntable.show_steps()'),
    "table.start_again": _tx("marks", 'table.keep_rows_where("marks", is_above=50)\ntable.remove_columns("height")\n'
                                      "table.start_again()\nprint(table)"),
    "table.save": _tx("marks", 'table.keep_rows_where("marks", is_above=50)\ntable.save("good_marks.xlsx")\n'
                               'table.save("good_marks.csv")'),
    "table.start_chart": _tx("marks", 'table.keep_rows_where("subject", is_equal_to="Maths")\nchart = table.start_chart()\n'
                                'chart.draw_bars(x="name", y="marks")\nchart.rotate_labels_x()\n'
                                'chart.save("maths_marks.png")'),
    "table.make_copy": _tx("marks", 'backup = table.make_copy()\ntable.keep_rows_where("class", is_equal_to="A")\n'
                                    "backup.count_rows()\ntable.count_rows()"),
    "table.as_pandas": _tx("marks", 'table.keep_rows_where("marks", is_above=50)\ndf = table.as_pandas()\nprint(type(df))'),
    "table.as_polars": _tx("marks", 'table.keep_rows_where("marks", is_above=50)\ndf = table.as_polars()\nprint(type(df))'),
    # models
    "table.explain": _tx("school", """\
        table.explain("marks", using=["hours", "sleep", "breakfast"])
        table.explain("passed", using=["hours", "breakfast"], outcome="yes or no")
        table.explain("marks", using=["hours", "breakfast"], grouped_by="school")
        table.explain("marks", using=["hours", "breakfast"], grouped_by=["school", "class"])
        table.explain("marks", using=["hours", "breakfast"], grouped_by="school", effects="for the whole population")
        table.explain("marks", using=["hours", "breakfast"], curve_for="hours")
        table.explain("marks", using=["hours", "breakfast"], robust_errors=True)
        table.explain("passed", using=["hours", "breakfast"], outcome="yes or no", show="risk ratios")
        table.explain("marks", using=["hours", "breakfast"], giving_outliers_less_weight=True)
        table.explain("marks", using=["hours", "breakfast"], curve_for="hours", with_knots=3)
        table.explain("marks", using=["hours", "breakfast"], show="standardised effects")"""),
    "table.add_predicted_column": _tx("school", """\
        table.add_predicted_column("marks", using=["hours", "breakfast"], interval=95)
        table.show_first_rows(5)"""),
    "table.find_model_averages_of": _tx("school", """\
        table.find_model_averages_of("marks", for_each_group_in="breakfast", using=["hours", "school"])
        table.find_model_averages_of("passed", for_each_group_in="breakfast", using=["hours"], outcome="yes or no")"""),
    "table.check_model_of": _tx("school", """\
        charts = table.check_model_of("marks", using=["hours", "breakfast"])
        charts.save("model_checks.png")
        table.check_model_of("marks", using=["hours", "breakfast"], grouped_by="school")"""),
    "table.show_rows_that_pull_model": _tx("school", """\
        table.show_rows_that_pull_model("marks", using=["hours", "breakfast"])"""),
    "table.compare_models": _tx("school", """\
        table.compare_models("marks", using=["hours"], against=["hours", "breakfast"])
        table.compare_models("passed", using=["hours"], against=["hours", "breakfast"], outcome="yes or no")
        table.compare_models("marks", using=["hours"], against=["hours", "breakfast"], grouped_by="school")"""),
    # patterns across columns
    "table.add_principal_components": _tx("meadow", """\
        table.add_principal_components(how_many=2)
        chart = table.start_chart()
        chart.draw_dots(x="PC1", y="PC2", colour="grazed")
        chart.save("meadow_pca.png")"""),
    "table.find_principal_components_of": _tx("meadow", """\
        components = table.find_principal_components_of()
        components.show()"""),
    "table.add_clusters": _tx("meadow", """\
        table.add_clusters(how_many=2)
        table.count_rows(for_each_group_in="cluster", across="grazed")"""),
    "table.find_distances_between_rows": _tx("meadow", """\
        distances = table.find_distances_between_rows(measure="bray-curtis", names="plot")
        distances.show_first_rows(3)"""),
    "table.add_nmds": _tx("meadow", """\
        table.add_nmds(measure="bray-curtis")
        chart = table.start_chart()
        chart.draw_dots(x="NMDS1", y="NMDS2", colour="grazed")
        chart.save("meadow_nmds.png")"""),
    "table.compare_profiles_of": _tx("meadow", 'table.compare_profiles_of(for_each_group_in="grazed")'),
    # S3c-1: communities and resistomes (sdata.get_example("resistome"), made up)
    "table.add_diversity_columns": _tx("resistome", f"""\
        table.add_diversity_columns(columns={_SIX_GENES})
        table.compare_averages_of("shannon", for_each_group_in="site")"""),
    "table.add_log_ratio_columns": _tx("resistome", f'table.add_log_ratio_columns(columns={_SIX_GENES})'),
    "table.add_principal_coordinates": _tx("resistome", f"""\
        table.add_principal_coordinates(columns={_SIX_GENES})
        chart = table.start_chart()
        chart.draw_dots(x="PCo1", y="PCo2", colour="site")
        chart.save("resistome_pcoa.png")"""),
    "table.explain_profiles_of": _tx("resistome", f'table.explain_profiles_of({_SIX_GENES}, using=["temperature", '
                                                  '"salinity"])'),
    "table.find_correlation_between_profiles": _tx("resistome", f'table.find_correlation_between_profiles(first={_SIX_GENES}, '
                                                                'second=["temperature", "salinity"])'),
    "table.add_axes_that_separate_groups": _tx("resistome", 'table.add_axes_that_separate_groups(columns=["temperature", '
                                                            '"salinity"], for_each_group_in="site")'),
    "table.add_correspondence_axes": _tx("resistome", f'table.add_correspondence_axes(columns={_SIX_GENES})'),
    "draw_richness_curves": _ex("resistome", f'chart.draw_richness_curves(columns={_SIX_GENES}, colour="site")',
                                "resistome_richness"),
    "draw_cluster_tree": _ex("resistome", f'chart.draw_cluster_tree(columns={_SIX_GENES}, measure="bray-curtis", '
                                          'names="sample")', "resistome_tree"),
    # S3c-2: hidden factors
    "table.find_hidden_factors_behind": _tx("ability_tests", """        table.find_hidden_factors_behind(["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"])"""),
    "table.check_hidden_factors": _tx("ability_tests", 'table.check_hidden_factors(measured_by={"visual": ["x1", "x2", '
                                                       '"x3"], "textual": ["x4", "x5", "x6"], "speed": ["x7", "x8", "x9"]})'),
    # S3c-3: directions, places and extremes
    "table.find_average_direction_of": _tx("stations", 'table.find_average_direction_of("current_direction", '
                                                       'full_turn=360)'),
    "table.find_return_levels_of": _tx("sea_levels", 'table.find_return_levels_of("sea_level", once_in=[10, 100], '
                                                   'sorted_by="year")'),
    "table.find_variogram_of": _tx("stations", 'table.find_variogram_of("zinc", x="east", y="north")'),
    "draw_variogram": _ex("stations", 'chart.draw_variogram("zinc", x="east", y="north")', "stations_variogram"),
    "draw_threshold_check": _ex("rain", 'chart.draw_threshold_check(x="rain", between=[10, 30])', "rain_threshold"),
    # signals and time series
    "table.find_spectrum_of": _tx("sensor", 'table.find_spectrum_of("signal", sorted_by="time")'),
    "nums.find_spectrum": _nx("nums.find_spectrum(time_step=0.005)", values='sdata.get_example("sensor").get_column("signal")'),
    "table.check_steady_over_time": _tx("sensor", 'table.check_steady_over_time("signal", sorted_by="time")'),
    "table.find_autocorrelation_of": _tx("sensor", 'table.find_autocorrelation_of("signal", sorted_by="time", rows_back=10)'),
    "table.add_trend_and_season": _tx("visitors", """\
        table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year", for_each_group_in="museum")
        table.show_first_rows(3)"""),
    "table.find_trend_of": _tx("visitors", 'table.find_trend_of("visitors", sorted_by="month", for_each_group_in="museum")'),
    "sdata.make_run_of_dates": 'import simplydata as sdata\ntable = sdata.make_run_of_dates("2026-01-01", to="2026-12-31", every="day")',
    "table.add_missing_dates": _tx("river", """\
        table.add_missing_dates("date", every="day", for_each_group_in="station")
        table.fill_empty_cells_in("nitrate", with_the="line between neighbours", sorted_by="date", for_each_group_in="station")"""),
    "table.add_smoothed_column": _tx("sensor", 'table.add_smoothed_column("signal_smoothed", from_column="signal", '
                                               'test_method="savitzky-golay", window=11, sorted_by="time")'),
    "nums.smooth": _nx('nums.smooth(test_method="median", window=5)', values='sdata.get_example("sensor").get_column("signal")'),
    "nums.remove_trend": _nx("nums.remove_trend()", values='sdata.get_example("sensor").get_column("signal")'),
    "nums.keep_each_frequency_that": _nx("nums.keep_each_frequency_that(is_below=10, time_step=0.005)",
                                 values='sdata.get_example("sensor").get_column("signal")'),
    "nums.remove_each_frequency_that": _nx("nums.remove_each_frequency_that(is_equal_to=50, time_step=0.005)",
                                   values='sdata.get_example("sensor").get_column("signal")'),
    "table.add_filtered_column": _tx("sensor", 'table.add_filtered_column("slow", from_column="signal", keep_below=10, '
                                               'sorted_by="time")'),
    "nums.find_each_peak_that": _nx("nums.find_each_peak_that(is_at_least=1, apart=10)", values='sdata.get_example("sensor").get_column("signal")'),
    "nums.find_each_dip_that": _nx("nums.find_each_dip_that(is_at_most=-1, apart=10)", values='sdata.get_example("sensor").get_column("signal")'),
    "table.find_each_peak_that": _tx("sensor", 'table.find_each_peak_that("signal", sorted_by="time", is_at_least=1, apart=0.05)'),
    "table.find_each_dip_that": _tx("sensor", 'table.find_each_dip_that("signal", sorted_by="time", is_at_most=-1, apart=0.05)'),
    "nums.take_fourier_transform": _nx("nums.take_fourier_transform(time_step=0.005)", values='sdata.get_example("sensor").get_column("signal")'),
    "sdata.find_inverse_fourier_transform": _nx("""        table = nums.take_fourier_transform()
        back = sdata.find_inverse_fourier_transform(table)""", values="[1, 2, 3, 4]"),
    "nums.find_envelope": _nx("nums.find_envelope()", values='sdata.get_example("sensor").get_column("signal")'),
    "nums.convolve_with": _nx("nums.convolve_with([1, 2, 1])", values="[1, 2, 3]"),
    "nums.deconvolve_by": _nx("nums.deconvolve_by([1, 2, 3])", values="[0, 1, 2.5, 4, 1.5]"),
    "nums.change_time_step": _nx("nums.change_time_step(to=0.01, time_step=0.005)",
                                 values='sdata.get_example("sensor").get_column("signal")'),
    "sdata.make_wave": "\n".join(["import simplydata as sdata",
                              'nums = sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=100)']),
    "sdata.make_window_shape": "\n".join(["import simplydata as sdata", 'nums = sdata.make_window_shape("hann", how_many=64)']),
    "table.add_envelope_column": _tx("sensor", 'table.add_envelope_column("signal_envelope", from_column="signal", sorted_by="time")'),
    "sdata.frequency_filter": "\n".join(['import simplydata as sdata', 'system = sdata.frequency_filter(keep_below=10, time_step=0.005)', 'system.frequency_response(between=[1, 90])']),
    "draw_sticks": _ex("weather", 'chart.draw_sticks(x="month_number", y="rain", colour="city")', "draw_sticks"),
    "draw_autocorrelation_bars": "\n".join(['import simplydata as sdata', 'table = sdata.table(sdata.get_example("visitors"))', 'table.keep_rows_where("museum", is_equal_to="Harbour Museum")', 'chart = table.start_chart()', 'chart.draw_autocorrelation_bars("visitors", sorted_by="month")', 'chart.save("autocorrelation_bars.png")']),
    "draw_cross_correlation_bars": _ex("sensor", 'chart.draw_cross_correlation_bars("signal", "vibration", sorted_by="time", rows_back=20)', "draw_cross_correlation_bars"),
    "draw_lag_dots": "\n".join(['import simplydata as sdata', 'table = sdata.table(sdata.get_example("visitors"))', 'table.keep_rows_where("museum", is_equal_to="Harbour Museum")', 'chart = table.start_chart()', 'chart.draw_lag_dots("visitors", sorted_by="month", rows_back=[1, 12])', 'chart.save("lag_dots.png")']),
    "draw_trend_and_season": "\n".join(['import simplydata as sdata', 'table = sdata.table(sdata.get_example("visitors"))', 'table.keep_rows_where("museum", is_equal_to="Harbour Museum")', 'chart = table.start_chart()', 'chart.draw_trend_and_season(x="month", y="visitors", repeats_every="year")', 'chart.save("trend_and_season.png")']),
    "draw_forecast": _ex("visitors", 'chart.draw_lines(x="month", y="visitors", colour="museum")\nchart.draw_forecast(steps_ahead=12, repeats_every="year")', "forecast"),
    "draw_spectrum": _ex("sensor", 'chart.draw_spectrum("signal", sorted_by="time")', "spectrum"),
    "draw_spectrum_over_time": _ex("sensor", 'chart.draw_spectrum_over_time("signal", sorted_by="time", window=100)', "draw_spectrum_over_time"),
    "draw_peak_dots": _ex("sensor", 'chart.draw_lines(x="time", y="signal")\nchart.draw_peak_dots(is_at_least=1, apart=0.05)', "draw_peak_dots"),
    "sdata.system": "\n".join(['import simplydata as sdata', 'system = sdata.system("1 / (s**2 + 2*s + 5)")']),
    "system.step_response": _system_x("system.step_response(until=10)"),
    "system.impulse_response": _system_x("system.impulse_response(until=10)"),
    "system.response_to": _system_x('system.response_to(sdata.make_wave("square", frequency=0.2, time_step=0.05, how_many=400))'),
    "system.frequency_response": _system_x("system.frequency_response(between=[0.1, 100])"),
    "system.poles": _system_x("system.poles()"),
    "system.zeros": _system_x("system.zeros()", formula="(s + 1) / (s**2 + 2*s + 5)"),
    "system.is_stable": _system_x("system.is_stable()"),
    "system.steady_gain": _system_x("system.steady_gain()"),
    "system.in_steps": _system_x("system.in_steps(time_step=0.1)"),
    "system.then": _system_x('system.then(sdata.system("1 / s"))'),
    "system.add": _system_x('system.add(sdata.system("1 / (s + 3)"))'),
    "system.with_feedback": _system_x("system.with_feedback()"),
    "system.table": _system_x('system.table()\nsystem.table(form="state space")'),
    "system.chart": _system_x('chart = system.chart()\nchart.save("bode.png")'),
    "table.forecast": _tx("visitors", 'table.forecast("visitors", sorted_by="month", steps_ahead=12, '
                                      'repeats_every="year", for_each_group_in="museum")'),
    "nums.forecast": _nx("nums.forecast(steps_ahead=12, repeats_every=12)",
                         values='sdata.get_example("visitors").get_column("visitors").keep_first_numbers(144)'),
    "table.compare_forecasts_for": _tx("visitors", 'table.compare_forecasts_for("visitors", sorted_by="month", '
                                               'repeats_every="year", for_each_group_in="museum")'),
    "table.find_change_points_in": _tx("river", 'table.find_change_points_in("nitrate", sorted_by="date", '
                                             'for_each_group_in="station")'),
    "nums.find_autocorrelation": _nx("nums.find_autocorrelation(rows_back=10)",
                                   values='sdata.get_example("sensor").get_column("signal")'),
    # survival
    "table.find_survival_over_time": _tx("trial", 'table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment")'),
    "table.compare_survival": _tx("trial", 'table.compare_survival(time="days", event="died", for_each_group_in="treatment")'),
    "table.explain_survival": _tx("trial", 'table.explain_survival(time="days", event="died", '
                                           'using=["treatment", "age"])'),
    "draw_survival_curves": _ex("trial", 'chart.draw_survival_curves(time="days", event="died", colour="treatment", '
                                    'with_confidence_band=True)', "draw_survival_curves"),
    # S3b-3 (survival and person-time)
    "table.add_time_and_event_columns": _tx("admissions", 'table.add_time_and_event_columns(from_date="admitted", '
                                                      'to_date="discharged", event_date="first_esbl")\n'
                                                      'table.rate_of("event", time="time", for_each_group_in="ward")'),
    "table.find_risk_over_time": _tx("admissions", 'table.add_time_and_event_columns(from_date="admitted", '
                                                 'event_date="first_esbl", competing_with="discharged")\n'
                                                 'table.find_risk_over_time(time="time", event="event", '
                                                 'value="first_esbl", competing_with="discharged", '
                                                 'for_each_group_in="ward")'),
    "draw_risk_curves": "\n".join([
        "import simplydata as sdata", 'table = sdata.table(sdata.get_example("admissions"))',
        'table.add_time_and_event_columns(from_date="admitted", event_date="first_esbl", competing_with="discharged")',
        "chart = table.start_chart()",
        'chart.draw_risk_curves(time="time", event="event", value="first_esbl", competing_with="discharged", '
        'colour="ward")',
        'chart.save("draw_risk_curves.png")']),
    "draw_trade_off_curve": _ex("clinic", 'chart.draw_trade_off_curve(score=["crp", "procalcitonin"], truth="infected")',
                           "draw_trade_off_curve"),
    "draw_difference_dots": _ex("clinic", 'chart.draw_difference_dots(first="device_a", second="device_b")', "draw_difference_dots"),
    "draw_forest_plot": textwrap.dedent("""\
        import simplydata as sdata
        table = sdata.table(sdata.get_example("marks"))
        pairs = table.compare_each_pair_of("marks", for_each_group_in="class", test_method="tukey")
        chart = pairs.start_chart()
        chart.draw_forest_plot(x="difference", y="group 1")
        chart.save("forest_plot.png")"""),
    # combining studies (S3b-1)
    "table.combine_studies": _tx("bcg", 'table.combine_studies(names="trial", events=["tb_vaccinated", '
                                        '"tb_unvaccinated"], out_of=["vaccinated", "unvaccinated"])'),
    "draw_funnel_plot": textwrap.dedent("""\
        import simplydata as sdata
        table = sdata.table(sdata.get_example("bcg"))
        result = table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"],
                                       out_of=["vaccinated", "unvaccinated"])
        chart = result.start_chart()
        chart.draw_funnel_plot(x="estimate", y="standard error")
        chart.save("draw_funnel_plot.png")"""),
    # S3d-1: planning an experiment and survey answers
    "sdata.make_design_table": textwrap.dedent("""\
        import simplydata as sdata
        sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, with_seed=1)
        sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, of_kind="randomised blocks", with_seed=2)
        sdata.make_design_table({"variety": ["A", "B", "C", "D"]}, of_kind="latin square", with_seed=1)"""),
    "sdata.make_random_assignments": textwrap.dedent("""\
        import simplydata as sdata
        sdata.make_random_assignments(how_many=60, groups=["A", "B"], in_blocks_of=[4, 6], with_seed=1)
        sdata.make_random_assignments(how_many=40, groups=2, for_each_of=["Bergen", "Oslo"], with_seed=1)"""),
    "table.use_survey_design": _tx("sampled_schools", """\
        table.use_survey_design(weights="weight", strata="school_type", population_sizes="schools_of_type")
        table.find_average_of("score_2000")
        table.find_percent_of_rows_where("met_target", is_equal_to="yes")"""),
    "draw_answer_bars": _ex("course_feedback", 'chart.draw_answer_bars(columns=["teaching", "materials", "pace"], '
                                               'in_order=["strongly disagree", "disagree", "neutral", "agree", '
                                               '"strongly agree"])', "answer_bars"),
    # planning a study
    "sdata.find_how_many_needed": textwrap.dedent("""\
        import simplydata as sdata
        sdata.find_how_many_needed(effect_size=0.5, power=0.8)
        sdata.find_how_many_needed(for_test="compare_averages", difference=5, spread=10)
        sdata.find_how_many_needed(for_test="compare_averages", effect_size=0.25, groups=3)
        sdata.find_how_many_needed(effect_size=0.5, in_clusters_of=20, alike_within_clusters=0.05)
        sdata.find_how_many_needed(for_test="explain", effect_size=0.15, using=["temperature", "salinity", "depth"])"""),
    "sdata.find_chance_of_finding": textwrap.dedent("""\
        import simplydata as sdata
        sdata.find_chance_of_finding(effect_size=0.5, values_per_group=20)
        sdata.find_chance_of_finding(effect_size=0.5, values_per_group=[20, 40], based_on="ranks")"""),
    # numbers: make and look
    "sdata.numbers": textwrap.dedent("""\
        import simplydata as sdata
        nums = sdata.numbers([3, 5, 2, 8])
        print(nums)
        print(sdata.numbers(1, to=10))
        print(sdata.numbers(0, to=1, how_many=5))"""),
    "sdata.make_random_numbers": textwrap.dedent("""\
        import simplydata as sdata
        dice = sdata.make_random_numbers(how_many=10, between=[1, 6], whole_numbers=True, with_seed=1)
        dice.show()
        heights = sdata.make_random_numbers(how_many=100, average=150, standard_deviation=8, with_seed=1)
        heights.find_average()"""),
    "nums.show": _nx("nums.show()"),
    "nums.show_first_numbers": _nx("nums.show_first_numbers(3)"),
    "nums.show_last_numbers": _nx("nums.show_last_numbers(2)"),
    "nums.get_number_at": _nx('print(nums.get_number_at(1))\nprint(nums.get_number_at("last"))'),
    "nums.count": _nx("print(nums.count())"),
    "nums.count_empty_numbers": _nx("print(nums.count_empty_numbers())", "[12, None, 9, None, 14]"),
    # numbers: maths in words
    "nums.add": _nx("nums.add(5)\nnums.show()"),
    "nums.subtract": _nx("nums.subtract(2)\nnums.show()"),
    "nums.times": _nx("nums.times(2)\nnums.show()"),
    "nums.divide_by": _nx("nums.divide_by(4)\nnums.show()"),
    "nums.raise_to_power": _nx("nums.raise_to_power(2)\nnums.show()"),
    "nums.take_square_root": _nx("nums.take_square_root()\nnums.show()", "[9, 16, 25]"),
    "nums.take_absolute_value": _nx("nums.take_absolute_value()\nnums.show()", "[-3, 5, -2]"),
    "nums.round_to": _nx("nums.round_to(1)\nnums.show()", "[2.345, 3.14159, 7.07]"),
    "nums.take_log": _nx("nums.take_log(base=10)\nnums.show()", "[1, 10, 100, 1000]"),
    "nums.take_exp": _nx("nums.take_exp()\nnums.show()", "[0, 1, 2]"),
    "nums.turn_into_running_total": _nx("nums.turn_into_running_total()\nnums.show()", "[1, 2, 3, 4]"),
    # numbers: choose, sort and fill
    "nums.keep_each_number_that": _nx("nums.keep_each_number_that(is_above=10)\nnums.show()"),
    "nums.remove_each_number_that": _nx("nums.remove_each_number_that(is_below=10)\nnums.show()"),
    "nums.keep_first_numbers": _nx("nums.keep_first_numbers(3)\nnums.show()"),
    "nums.keep_last_numbers": _nx("nums.keep_last_numbers(3)\nnums.show()"),
    "nums.keep_random_numbers": _nx("nums.keep_random_numbers(3, with_seed=1)\nnums.show()"),
    "nums.remove_duplicate_numbers": _nx("nums.remove_duplicate_numbers()\nnums.show()", "[3, 5, 3, 8, 5]"),
    "nums.remove_empty_numbers": _nx("nums.remove_empty_numbers()\nnums.show()", "[12, None, 9, 14]"),
    "nums.fill_empty_numbers": _nx('nums.fill_empty_numbers(with_the="line between neighbours")\nnums.show()',
                                   "[12, None, 9, None, 14]"),
    "nums.sort": _nx("nums.sort(biggest_first=True)\nnums.show()"),
    "nums.reverse": _nx("nums.reverse()\nnums.show()"),
    "nums.keep_numbers_by_position": _nx("nums.keep_numbers_by_position(2, to=4)\nnums.show()"),
    "nums.remove_numbers_by_position": _nx('nums.remove_numbers_by_position("last")\nnums.show()'),
    "nums.replace_each_number_that": _nx("nums.replace_each_number_that(-999, with_value=None)\n"
                                "nums.replace_each_number_that(is_above=14, with_value=14)\nnums.show()",
                                "[12, -999, 9, 20, 14]"),
    # numbers: summaries
    "nums.find_average": _nx("nums.find_average()"),
    "nums.find_median": _nx("nums.find_median()"),
    "nums.find_total": _nx("nums.find_total()"),
    "nums.find_smallest": _nx("nums.find_smallest()"),
    "nums.find_biggest": _nx("nums.find_biggest()"),
    "nums.find_standard_deviation": _nx("nums.find_standard_deviation()"),
    "nums.find_percentile": _nx("nums.find_percentile(90)"),
    "nums.count_each": _nx("nums.count_each()", "[3, 5, 3, 8, 5, 3]"),
    # grids of numbers
    "sdata.number_grid": textwrap.dedent("""\
        import simplydata as sdata
        grid = sdata.number_grid([[1, 2, 3], [4, 5, 6]])
        print(grid)
        print(sdata.number_grid(rows=2, columns=3, filled_with=0))"""),
    "nums.make_number_grid": _nx("grid = nums.make_number_grid(columns=3)\nprint(grid)", "[1, 2, 3, 4, 5, 6]"),
    "grid.count_rows": _gx("print(grid.count_rows())"),
    "grid.count_columns": _gx("print(grid.count_columns())"),
    "grid.find_shape": _gx("print(grid.find_shape())"),
    "grid.show_first_rows": _gx("grid.show_first_rows(1)"),
    "grid.show_last_rows": _gx("grid.show_last_rows(1)"),
    "grid.get_number_at": _gx("print(grid.get_number_at(row=1, column=2))"),
    "grid.get_row": _gx("top = grid.get_row(1)\ntop.show()"),
    "grid.get_column": _gx("left = grid.get_column(1)\nleft.show()"),
    "grid.get_all_numbers": _gx("nums = grid.get_all_numbers()\nnums.show()"),
    "grid.swap_rows_and_columns": _gx("grid.swap_rows_and_columns()\nprint(grid)"),
    # NumPy + SciPy phase, batch 1: yes or no
    "nums.turn_into_yes_or_no": _nx("warm = nums.turn_into_yes_or_no(is_above=13)\nprint(warm)\nprint(~warm)"),
    "nums.keep_numbers_where": _nx("deep = sdata.numbers([5, 150, 80, 300, 20]).turn_into_yes_or_no(is_above=100)\n"
                                   "nums.keep_numbers_where(deep)\nnums.show()"),
    "nums.remove_numbers_where": _nx("land = sdata.numbers([0, 0, 1, 0, 1]).turn_into_yes_or_no(is_equal_to=1)\n"
                                     "nums.remove_numbers_where(land)\nnums.show()"),
    "nums.replace_numbers_where": _nx("land = sdata.numbers([0, 0, 1, 0, 1]).turn_into_yes_or_no(is_equal_to=1)\n"
                                      'nums.replace_numbers_where(land, with_value="empty")\nnums.show()'),
    "nums.count_numbers_that": _nx("print(nums.count_numbers_that(is_above=13))"),
    "nums.check_if_any_number": _nx("print(nums.check_if_any_number(is_above=30))"),
    "nums.check_if_all_numbers": _nx("print(nums.check_if_all_numbers(is_at_least=0))"),
    "nums.check_if_same_as": _nx("other = sdata.numbers([12, 15, 9, 20, 14.0001])\n"
                                 "print(nums.check_if_same_as(other, within=0.001))"),
    "grid.keep_rows_where": _gx("grid.keep_rows_where(column=3, is_above=0.5)\ngrid.keep_rows_where(column=1, is_above=5)\n"
                                "print(grid)"),
    "grid.remove_rows_where": _gx("grid.remove_rows_where(column=1, is_empty=True)\n"
                                  "grid.remove_rows_where(column=2, is_below=6)\nprint(grid)"),
    # rounding, angles and positions
    "nums.round_down": _nx("nums.round_down()\nnums.show()", "[2.7, -2.3, 0.5]"),
    "nums.round_up": _nx("nums.round_up()\nnums.show()", "[2.1, -2.7, 0.5]"),
    "nums.take_whole_part": _nx("nums.take_whole_part()\nnums.show()", "[2.7, -2.7, 0.5]"),
    "nums.take_sin": _nx("nums.take_sin(degrees=True)\nnums.show()", "[0, 30, 90]"),
    "nums.take_cos": _nx("nums.take_cos(degrees=True)\nnums.show()", "[0, 60, 90]"),
    "nums.take_tan": _nx("nums.take_tan(degrees=True)\nnums.show()", "[0, 45, 60]"),
    "nums.change_angles_to": _nx('nums.change_angles_to("degrees")\nnums.show()', "[0, 1.5708, 3.14159]"),
    "nums.find_where_biggest": _nx("print(nums.find_where_biggest())"),
    "nums.find_where_smallest": _nx("print(nums.find_where_smallest())"),
    "nums.make_pair_table_with": _nx("depths = sdata.numbers([0, 10, 50])\n"
                                     "table = nums.make_pair_table_with(depths, by_subtracting=True)\nprint(table)",
                                     "[0, 10, 50]"),
    # blocks of numbers
    "sdata.number_block": textwrap.dedent("""\
        import simplydata as sdata
        plate = sdata.number_block(of_shape=(24, 8, 12), filled_with=0, directions_named=["hour", "row", "column"])
        print(plate.find_shape())
        cube = sdata.number_block([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        print(cube)"""),
    "block.find_shape": _kx("print(block.find_shape())"),
    "block.count_directions": _kx("print(block.count_directions())"),
    "block.find_direction_names": _kx("print(block.find_direction_names())"),
    "block.get_number_at": _kx("print(block.get_number_at(hour=1, row=2, column=3))"),
    "block.find_average": _kx('wells = block.find_average(over="hour")\nprint(wells.find_shape())\n'
                              'print(block.find_average(in_each="row"))'),
    "block.keep_by_position_in": _kx('block.keep_by_position_in("hour", [1, 3])\nprint(block.find_shape())'),
    "block.remove_by_position_in": _kx('block.remove_by_position_in("hour", 24)\nprint(block.find_shape())'),
    "block.keep_where": _lx('block.keep_where("east", is_between=[2, 5])\nprint(block.find_shape())'),
    "block.remove_where": _lx('block.remove_where("north", is_one_of=[0, 1])\nprint(block.find_shape())'),
    "block.change_shape_to": _kx('block.change_shape_to(one_row_per="hour")\nprint(block.find_shape())'),
    "block.add_direction": _kx('block.add_direction("plate", at_position=1)\nprint(block.find_shape())'),
    "block.remove_directions_of_size_one": _kx('block.add_direction("plate", at_position=1)\n'
                                               "block.remove_directions_of_size_one()"),
    "block.swap_directions": _kx('block.swap_directions("row", "column")\nprint(block.find_direction_names())'),
    "block.move_direction": _kx('block.move_direction("column", to_position=1)\nprint(block.find_direction_names())'),
    "block.rotate": _kx("block.rotate(by_quarter_turns=1)\nprint(block.find_shape())"),
    "block.move_round_by": _kx('block.move_round_by(3, over="hour")'),
    "block.insert_numbers": _kx('block.insert_numbers(0, at_position=2, over="row")\nprint(block.find_shape())'),
    "block.repeat_each_number": _kx('block.repeat_each_number(3, over="hour")\nprint(block.find_shape())'),
    "block.repeat_whole_block": _kx('block.repeat_whole_block(2, over="hour")\nprint(block.find_shape())'),
    "block.add_numbers_from": _kx('other = sdata.number_block(of_shape=(6, 8, 12), filled_with=1, '
                                  'directions_named=["hour", "row", "column"])\n'
                                  'block.add_numbers_from(other, over="hour")\nprint(block.find_shape())'),
    "block.split_into_pieces": _kx('pieces = block.split_into_pieces(3, over="hour")\nprint(len(pieces))'),
    "block.split_into_one_block_per": _kx('hours = block.split_into_one_block_per("hour")\nprint(len(hours))'),
    "sdata.stack_up": textwrap.dedent("""\
        import simplydata as sdata
        a = sdata.number_grid([[1, 2], [3, 4]])
        b = sdata.number_grid([[5, 6], [7, 8]])
        c = sdata.number_grid([[9, 10], [11, 12]])
        images = sdata.stack_up([a, b, c], as_new_direction="image")
        print(images.find_shape())"""),
    # stretching
    "block.show_how_it_lines_up_with": _kx('other = sdata.number_block(of_shape=(8, 12), filled_with=0.05)\n'
                                           "block.show_how_it_lines_up_with(other)"),
    "block.stretch_to": _kx("block.stretch_to((2, 24, 8, 12))"),
    "sdata.stretch_to_same_shape": textwrap.dedent("""\
        import simplydata as sdata
        a = sdata.number_block([[1], [2], [3]])
        b = sdata.numbers([10, 20])
        a2, b2 = sdata.stretch_to_same_shape(a, b)
        print(a2)
        print(b2)"""),
    # NumPy + SciPy phase, batch 2: files
    "sdata.show_whats_inside": _seax('block.save("sst_monthly.nc")\nsdata.show_whats_inside("sst_monthly.nc")'),
    "block.save": _seax('block.save("sst.nc")\nsst = sdata.number_block("sst.nc", values="values")\n'
                      'print(sst.find_shape())'),
    # labels, dates and places
    "block.get_labels_of": _seax('times = block.get_labels_of("time")\ntimes.show()'),
    "block.add_labels_to": _seax('block.add_labels_to("latitude", [60, 61, 62, 63])\n'
                               'print(block.get_labels_of("latitude"))'),
    "block.find_values_at": _seax("between = block.find_values_at(latitude=60.5, longitude=2.5)\n"
                                "print(between.find_shape())"),
    "block.get_numbers_nearest_to": _seax("station = block.get_numbers_nearest_to(latitude=60.4, longitude=5.3)\n"
                                        "print(station.find_shape())"),
    "block.turn_into_change_from_average": _seax('block.turn_into_change_from_average(in_each="month")\n'
                                               'block.undo()\n'
                                               'block.turn_into_change_from_average(in_each="month", '
                                               'from_years=["2010", "2011"])'),
    "block.smooth": _seax('block.smooth(over=["latitude", "longitude"], window=3)\nblock.undo()\n'
                        'block.smooth(over="time", test_method="gaussian", width=2)'),
    "block.change_size_to": _seax("block.change_size_to(latitude=8, longitude=10)\nprint(block.find_shape())"),
    "grid.smooth": textwrap.dedent("""\
        import simplydata as sdata
        grid = sdata.make_random_numbers(rows=6, columns=8, average=20, standard_deviation=3, with_seed=1)
        grid.smooth(window=3)
        print(grid)"""),
    # chances and random picks
    "nums.make_random_picks": _nx("again = nums.make_random_picks(how_many=40, with_seed=1)\n"
                                  "print(again.find_average())\n"
                                  "dice = sdata.numbers([1, 2, 3]).make_random_picks(how_many=10, "
                                  "with_chances=[0.5, 0.3, 0.2], with_seed=1)"),
    "nums.take_log_odds": _nx("nums.take_log_odds()\nnums.show()", "[0.1, 0.5, 0.8]"),
    "nums.turn_into_chances": _nx("nums.turn_into_chances()\nnums.show()", "[-2.2, 0, 1.386]"),
    "sdata.count_ways_to_choose": textwrap.dedent("""\
        import simplydata as sdata
        print(sdata.count_ways_to_choose(3, out_of=10))"""),
    "sdata.count_ways_to_order": textwrap.dedent("""\
        import simplydata as sdata
        print(sdata.count_ways_to_order(3, out_of=10))"""),
    "sdata.hide_stretching_notes": textwrap.dedent("""\
        import simplydata as sdata
        sdata.hide_stretching_notes()
        sdata.show_stretching_notes()"""),
    "sdata.show_stretching_notes": textwrap.dedent("""\
        import simplydata as sdata
        sdata.show_stretching_notes()"""),
    "grid.keep_rows_by_position": _bx("grid.keep_rows_by_position(2, to=3)\nprint(grid)"),
    "grid.keep_columns_by_position": _bx("grid.keep_rows_by_position(2, to=3)\n"
                                         "grid.keep_columns_by_position(1, to=3)\nprint(grid)"),
    "grid.remove_rows_by_position": _bx("grid.remove_rows_by_position(1)\nprint(grid)"),
    "grid.remove_columns_by_position": _bx("grid.remove_columns_by_position(1, step=2)\nprint(grid)"),
    "grid.replace_each_number_that": _gx("grid.replace_each_number_that(is_below=4, with_value=0)\nprint(grid)"),
    # numbers: undo and finish
    "nums.undo": _nx("nums.add(5)\nnums.undo()\nnums.show()"),
    "nums.show_steps": _nx("nums.add(5)\nnums.keep_each_number_that(is_above=15)\nnums.show_steps()"),
    "nums.start_again": _nx("nums.add(5)\nnums.times(2)\nnums.start_again()\nnums.show()"),
    "nums.turn_into_table": _nx('table = nums.turn_into_table(name="marks")\nprint(table)'),
    "nums.start_chart": _nx('chart = nums.start_chart()\nchart.draw_histogram(x="value", with_bins=4)\nchart.save("nums.png")'),
    "nums.save": _nx('nums.save("nums.csv")'),
    "nums.as_numpy": _nx("array = nums.as_numpy()\nprint(type(array))"),
    # help
    "sdata.show_all_words": "import simplydata as sdata\nsdata.show_all_words()",
    "sdata.help": 'import simplydata as sdata\nsdata.help("draw_bars")\nsdata.help("show=")\nsdata.help("keep_rows_where")\nsdata.help("find_average")',
    "sdata.show_lesson": "import simplydata as sdata\nsdata.show_lesson()\nsdata.show_lesson(1)",
    "sdata.show_packages_used": _tx("marks", 'table.find_average_of("marks", for_each_group_in="class")\n'
                                             'sdata.show_packages_used()\n'
                                             'sdata.show_packages_used(save_as="references.bib")'),
    # 30 days of simplydata
    "sdata.start_30_days": 'import simplydata as sdata\nsdata.start_30_days(track="python")',
    "sdata.show_today": "import simplydata as sdata\nsdata.show_today()",
    "sdata.show_day": 'import simplydata as sdata\nsdata.show_day()\nsdata.show_day(5)\nsdata.show_day(1, track="beginner")',
    "sdata.show_answers": "import simplydata as sdata\nsdata.show_answers(5)",
    "sdata.go_to_next_day": "import simplydata as sdata\nsdata.start_30_days()\nsdata.go_to_next_day()",
    # S3a-2: lines and curves (fit_dose_response needs R with drc)
    "table.fit_dose_response": _tx("toxicity", 'table.fit_dose_response(x="concentration", y="root_length", '
                                               'for_each_group_in="chemical")\n'
                                               'table.fit_dose_response(x="concentration", y="dead", outcome="yes or no", '
                                               'out_of="seedlings", doses_for_effect=[10, 50])'),
    "table.find_best_power_of": _tx("trial", 'table.find_best_power_of("days")\n'
                                             'table.find_best_power_of("days", test_method="yeo-johnson")'),
    "fit_dose_response": _ex("toxicity", 'chart.draw_dots(x="concentration", y="root_length", colour="chemical")\n'
                                         'chart.fit_dose_response()', "fit_dose_response"),
    # S3a-3: checking and comparing (the two table words need R)
    "table.find_columns_that_predict": _tx("school", """\
        table.find_columns_that_predict("marks", using=["hours", "sleep", "breakfast", "class"])
        table.find_columns_that_predict("passed", using=["hours", "sleep", "breakfast", "class"], outcome="yes or no")"""),
    "table.find_group_levels_of": _tx("school", """\
        levels = table.find_group_levels_of("marks", using=["hours"], grouped_by="school")
        levels.show()"""),
    "draw_interaction_lines": _ex("school", 'chart.draw_interaction_lines(x="class", y="marks", colour="breakfast")',
                                  "draw_interaction_lines"),
    # tables phase, batch 2 (approved by Manish 2026-11-25)
    "table.count_columns": _tx("marks", "table.count_columns()\ntable.count_rows()"),
    "table.rename_columns": _tx("weather", 'table.rename_columns({"temperature": "temp", "rain": "rain_mm"})\n'
                                           'table.rename_columns(add_in_front="w_")\n'
                                           "print(table.get_column_names())"),
    "table.fill_empty_cells_from": _tx("fjord_samples", 'table.fill_empty_cells_from({"sample_id": [1, 2, 12], '
                                                        '"notes": ["calm", "calm", "rain"]}, using="sample_id")\n'
                                                        'table.keep_columns("sample_id", "notes")\n'
                                                        "table.show_first_rows(3)"),
    "table.round_dates_in": _tx("shop", 'table.round_dates_in("date", down_to="month")\n'
                                        'table.find_total_of("sales", for_each_group_in=["shop", "date"])'),
    "table.change_time_zone_in": _tx("fjord_samples", 'table.change_time_zone_in("sampled_local", to="UTC", '
                                                      'recorded_in="Europe/Oslo")\n'
                                                      'table.round_dates_in("sampled_local", to_the="hour")\n'
                                                      'table.show_first_rows(3)'),
    "table.add_missing_combinations_of": _tx("fjord_samples", 'table.add_missing_combinations_of("station", "depth_m")\n'
                                                              'table.keep_rows_where("sample_id", is_empty=True)\n'
                                                              'table.show()'),
    "table.spread_into_yes_no_columns": _tx("fruit", 'table.spread_into_yes_no_columns("fruit")\n'
                                                     'table.show_first_rows(3)\n'
                                                     'table.undo()\n'
                                                     'table.spread_into_yes_no_columns("shop")\n'
                                                     'print(table.get_column_names())'),
}

# charts phase, batch 2 (approved by Manish 2026-11-25)
HELP_EXAMPLES.update({
    "draw_rug_lines": _ex("marks", 'chart.draw_density(x="marks")\nchart.draw_rug_lines(x="marks")', "draw_rug_lines"),
    "draw_wind_rose": _ex("weather", 'chart.draw_wind_rose(direction="wind_direction", speed="wind_speed")',
                          "draw_wind_rose"),
    "draw_arrow": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\n'
                      'chart.draw_arrow(start=[2, 40], end=[4, 60], labelled="more hours")', "draw_arrow"),
    "put_chart_inside": _ex("weather", 'chart.draw_lines(x="month_number", y="temperature", colour="city")\n'
                            'detail = sdata.chart(weather).draw_bars(x="city", y="rain")\n'
                            'detail.write_title_on_top("Rain")\n'
                            'chart.put_chart_inside(detail, where="bottom right", size=0.35)', "put_chart_inside"),
    "add_second_x": _ex("weather", 'chart.draw_dots(x="temperature", y="rain")\n'
                        'chart.add_second_x(formula="x * 9 / 5 + 32", labelled="Temperature (°F)")', "add_second_x"),
    "hide_frame": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.hide_frame()', "hide_frame"),
    "hide_ticks_x": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.hide_ticks_x()', "hide_ticks_x"),
    "hide_ticks_y": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.hide_ticks_y()', "hide_ticks_y"),
    "show_small_ticks_x": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.show_small_ticks_x()',
                              "show_small_ticks_x"),
    "show_small_ticks_y": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.show_small_ticks_y()',
                              "show_small_ticks_y"),
    "use_true_shape": _ex("island", 'chart.draw_contour(x="east", y="north", z="height")\nchart.use_true_shape()',
                          "use_true_shape"),
    "make_square": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.make_square()', "make_square"),
    "put_colour_bar_at_bottom": _ex("weather", 'chart.draw_heatmap(x="month", y="city", value="rain")\n'
                                    'chart.put_colour_bar_at_bottom()', "put_colour_bar_at_bottom"),
    "put_colour_bar_at_top": _ex("weather", 'chart.draw_heatmap(x="month", y="city", value="rain")\n'
                                 'chart.put_colour_bar_at_top()', "put_colour_bar_at_top"),
    "put_colour_bar_at_left": _ex("weather", 'chart.draw_heatmap(x="month", y="city", value="rain")\n'
                                  'chart.put_colour_bar_at_left()', "put_colour_bar_at_left"),
    "hide_colour_bar": _ex("weather", 'chart.draw_heatmap(x="month", y="city", value="rain", with_numbers=True)\n'
                           'chart.hide_colour_bar()', "hide_colour_bar"),
    "put_ticks_colour_bar": _ex("weather", 'chart.draw_heatmap(x="month", y="city", value="rain")\n'
                                'chart.put_ticks_colour_bar(0, 10, 20, 30)', "put_ticks_colour_bar"),
    "draw_lines_3d": _ex("island", 'chart.draw_lines_3d(x="east", y="north", z="height")', "draw_lines_3d"),
    "label_z": _ex("island", 'chart.draw_surface(x="east", y="north", z="height")\nchart.label_z("Height (m)")',
                   "label_z"),
    "set_range_z": _ex("island", 'chart.draw_surface(x="east", y="north", z="height")\nchart.set_range_z(-10, 20)',
                       "set_range_z"),
    "put_ticks_z": _ex("island", 'chart.draw_surface(x="east", y="north", z="height")\n'
                       'chart.put_ticks_z(-10, 0, 10, 20)', "put_ticks_z"),
    "look_from": _ex("island", 'chart.draw_surface(x="east", y="north", z="height")\n'
                     'chart.look_from(height=20, around=45)', "look_from"),
    "say_what_it_shows": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.say_what_it_shows()',
                             "say_what_it_shows"),
})


def _web_ex(table: str, body: str, file: str) -> str:
    """A runnable example that ends with a web page: chart.save("....html") (needs simplydata[web])."""
    return _ex(table, body, file).rsplit("\n", 1)[0] + f'\nchart.save("{file}.html")'


# charts phase, batch 3 (approved by Manish 2026-11-25)
HELP_EXAMPLES.update({
    "show_in_web_page": "\n".join(["import simplydata as sdata", 'marks = sdata.get_example("marks")',
                                   "chart = sdata.chart(marks)", 'chart.draw_dots(x="hours", y="marks")',
                                   "chart.show_in_web_page()"]),
    "show_when_pointing": _web_ex("marks", 'chart.draw_dots(x="hours", y="marks")\n'
                                  'chart.show_when_pointing("name", "class")', "marks_pointing"),
    "add_range_bar_x": _web_ex("visitors", 'chart.draw_lines(x="month", y="visitors", colour="museum")\n'
                               "chart.add_range_bar_x()", "visitors_range_bar"),
    "break_between_y": _ex("marks", 'chart.draw_bars(x="class", y="marks")\nchart.break_between_y(5, 50)',
                           "break_between_y"),
    "use_scale_x": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.use_scale_x("square root")',
                       "use_scale_x"),
    "use_scale_y": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\nchart.use_scale_y("square root")',
                       "use_scale_y"),
    "use_background_colour": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\n'
                                 'chart.use_background_colour("ivory")', "use_background_colour"),
    "draw_hexagon_bins": _ex("marks", 'chart.draw_hexagon_bins(x="hours", y="height")', "draw_hexagon_bins"),
    "draw_time_bars": "\n".join(["import simplydata as sdata", "chart = sdata.chart()",
                                 'chart.draw_time_bars(start=[1, 3, 6], end=[4, 7, 9], y=["plan", "build", "test"])',
                                 'chart.label_x("Week")', 'chart.save("draw_time_bars.png")']),
    "draw_rectangle": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\n'
                          "chart.draw_rectangle(x_between=[4, 6], y_between=[60, 80])", "draw_rectangle"),
    "draw_circle": _ex("marks", 'chart.draw_dots(x="hours", y="marks")\n'
                       "chart.draw_circle(centre=[5, 70], radius=1)", "draw_circle"),
    "draw_residual_dots": _ex("marks", 'chart.draw_residual_dots(x="hours", y="marks")', "draw_residual_dots"),
    "draw_event_lines": _ex("marks", 'chart.draw_event_lines(x="hours", y="class")', "draw_event_lines"),
    "draw_bars_3d": _ex("weather", 'chart.draw_bars_3d(x="month", y="city", z="rain")', "draw_bars_3d"),
})


def _fx(body: str, formula: str = "(x + 2)**2 - 4") -> str:
    """A runnable formula example: make a formula (needs simplydata[exact], SymPy), then the steps."""
    lines = ["import simplydata as sdata", f'f = sdata.formula("{formula}")']
    lines += textwrap.dedent(body).strip().splitlines()
    return "\n".join(lines)


def _lines(*lines: str) -> str:
    return "\n".join(["import simplydata as sdata", *lines])


# numbers phase, batch 3 (approved by Manish 2026-11-25)
HELP_EXAMPLES.update({
    "sdata.formula": _lines('f = sdata.formula("(x + 2)**2 - 4")', "print(f)"),
    "f.make_simpler": _fx("f.make_simpler()", "(x**2 - 1) / (x - 1)"),
    "f.turn_into_sum": _fx("f.turn_into_sum()"),
    "f.turn_into_product": _fx("f.turn_into_product()", "x**2 + 4*x"),
    "f.find_slope_formula": _fx("slope = f.find_slope_formula()\nslope.find_value_at(x=1)", "x**3 - 2*x"),
    "f.find_area_formula": _fx("area = f.find_area_formula()", "x**3 - 2*x"),
    "f.find_value_at": _fx("f.find_value_at(x=2)\nf.find_value_at(x=[0, 1, 2, 3])", "x**3 - 2*x"),
    "f.put_in": _fx('f.put_in(x="y + 1")', "x**2"),
    "f.show_as_latex": _fx("f.show_as_latex()", "x**3 - 2*x"),
    "f.find_limit_as": _fx('f.find_limit_as("x", goes_to=0)', "sin(x) / x"),
    "f.find_taylor_series": _fx("f.find_taylor_series(around=0, up_to_power=4)", "exp(x)"),
    "f.undo": _fx("f.turn_into_sum()\nf.undo()"),
    "sdata.find_area_under": _lines('sdata.find_area_under("x**2", between=[0, 3])',
                                    'sdata.find_area_under("exp(-x**2)", between=[0, "infinity"])'),
    "sdata.find_volume_under": _lines('sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]})'),
    "sdata.find_path_over_time": _lines(
        'growth = sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50], '
        'known={"r": 0.3, "K": 1000}, time_step=0.5)', "growth.show_last_rows(3)"),
    "nums.turn_into_running_area": _nx("nums.turn_into_running_area(time_step=60)\nnums.show()", "[2, 4, 4, 3, 1]"),
    "nums.take_cube_root": _nx("nums.take_cube_root()\nnums.show()", "[27, -8, 1000]"),
    "nums.show_as_fraction": _nx("nums.show_as_fraction()", "[0.5, 0.25, 0.3333333333333333, 1.75]"),
    "nums.find_coherence_with": _lines('nums = sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=500)',
                                       'other = sdata.make_wave("square", frequency=5, time_step=0.01, how_many=500)',
                                       "together = nums.find_coherence_with(other, time_step=0.01)",
                                       "together.show_first_rows(5)"),
    "nums.take_cosine_transform": _nx("nums.take_cosine_transform()\nnums.show()", "[1, 2, 3, 4]"),
    "grid.get_numbers_at_pairs": _gx("grid.get_numbers_at_pairs(rows=[1, 2], columns=[3, 3])"),
    "grid.get_numbers_from_each_row_at": _gx("grid.get_numbers_from_each_row_at(columns=[2, 1])"),
    "grid.find_each_patch_that": _gx("patches = grid.find_each_patch_that(is_above=5)\nprint(patches)"),
    "grid.change_size_to": _gx("grid.change_size_to(rows=4, columns=6)\nprint(grid)"),
    "grid.rotate": _gx("grid.rotate(by_degrees=15)\nprint(grid)"),
    "grid.take_matrix_exp": _lines("grid = sdata.number_grid([[0, 1], [-1, 0]])", "grid.take_matrix_exp()",
                                   "print(grid)"),
    "grid.find_null_space": _lines("grid = sdata.number_grid([[1, 2], [2, 4]])",
                                   "directions = grid.find_null_space()", "print(directions)"),
    "table.find_nearest_rows_to": _tx("stations", 'nearest = table.find_nearest_rows_to({"east": 4000, "north": 1000}, '
                                                  "how_many=3)\nprint(nearest)"),
    "table.find_distances_to_rows_of": _tx("stations", 'other = sdata.table(sdata.get_example("stations"))\n'
                                                       "table.keep_first_rows(3)\nother.keep_last_rows(2)\n"
                                                       'table.find_distances_to_rows_of(other, using=["east", "north"], '
                                                       'names="station")'),
    "table.find_fence_around": _tx("stations", 'corners = table.find_fence_around(x="east", y="north")\n'
                                               "print(corners)"),
})

# numbers phase, batch 4 (approved by Manish 2026-11-26): the SymPy words
HELP_EXAMPLES.update({
    "f.show_as_decimal": _fx("f.show_as_decimal(digits=50)", "sqrt(2)"),
    "f.group_by_powers_of": _fx('f.group_by_powers_of("x")\nf.undo()', "a*x**2 + b*x**2 + a*x - x"),
    "f.turn_into_partial_fractions": _fx("f.turn_into_partial_fractions()", "(3*x + 5) / ((x + 1)*(x + 2))"),
    "f.as_sympy": _fx("expr = f.as_sympy()\nprint(type(expr))"),
    "sdata.find_sum_of_series": _lines('sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])',
                                       'sdata.find_sum_of_series("k", between=[1, "n"])',
                                       'sdata.find_sum_of_series("1/k", between=[1, "infinity"])'),
    "grid.find_determinant": _lines("grid = sdata.number_grid([[2, 1], [1, 2]])", "grid.find_determinant()",
                                    "grid.find_determinant(exactly=True)"),
    "grid.take_inverse": _lines("grid = sdata.number_grid([[2, 1], [1, 2]])", "grid.take_inverse()", "print(grid)",
                                "grid.undo()", "grid.take_inverse(exactly=True)"),
    "grid.find_eigenvalues": _lines("grid = sdata.number_grid([[2, 1], [1, 2]])", "values = grid.find_eigenvalues()",
                                    "print(values)", "grid.find_eigenvalues(exactly=True)"),
})


# ---------------------------------------------------------------- finding words
def _ps():
    import simplydata  # late import: simplydata imports this file

    return simplydata


def _chart_class():
    from .chart import Chart

    return Chart


def _table_class():
    from .table import Table

    return Table


def _numbers_class():
    from .numbers.numbers import Numbers

    return Numbers


def _grid_class():
    from .numbers.numbers import NumberGrid

    return NumberGrid


# The objects that have steps, and the name they go by in examples ("chart" has no prefix
# in GROUPS: a plain name is a chart word).
_PREFIX = {"table": "table", "numbers": "nums", "grid": "grid", "block": "block", "dist": "dist", "system": "system", "formula": "f"}


def _block_class():
    from .numbers.blocks import NumberBlock

    return NumberBlock


def _distribution_class():
    from .distributions import Distribution

    return Distribution


def _system_class():
    from .systems import System

    return System


def _formula_class():
    from ._formula import Formula

    return Formula


def _classes():
    """(class, kind) for every object with steps."""
    return [(_chart_class(), "chart"), (_table_class(), "table"), (_numbers_class(), "numbers"),
            (_grid_class(), "grid"), (_block_class(), "block"), (_distribution_class(), "dist"),
            (_system_class(), "system"),
            (_formula_class(), "formula")]


def _kind(key: str) -> str:
    """What a key in GROUPS is: "option", "sdata", "table", "numbers", "grid" or "chart"."""
    if key.endswith("="):
        return "option"
    if key.startswith("sdata."):
        return "sdata"
    for kind, prefix in _PREFIX.items():
        if key.startswith(prefix + "."):
            return kind
    return "chart"


def _word(key: str) -> str:
    """The word itself, without "sdata.", "table." or "nums." in front: "sdata.chart" -> "chart"."""
    kind = _kind(key)
    if kind == "sdata":
        return key[len("sdata."):]
    if kind in _PREFIX:
        return key[len(_PREFIX[kind]) + 1:]
    return key


def _display(key: str) -> str:
    """How a key is shown in sdata.show_all_words() and the dictionary: table and number words without
    "table." or "nums." (their group says what they belong to)."""
    return _word(key) if _kind(key) in _PREFIX else key


def _function(key: str):
    """The real function behind a word in GROUPS (None for options such as "show=")."""
    kind = _kind(key)
    if kind == "option":
        return None
    if kind == "sdata":
        return getattr(_ps(), _word(key))
    for cls, cls_kind in _classes():
        if cls_kind == kind:
            return getattr(cls, _word(key))
    return None  # pragma: no cover


def _all_keys() -> list[str]:
    return [k for _, keys in GROUPS for k in keys]


def _group_of(key: str) -> str:
    return next(g for g, keys in GROUPS if key in keys)


def _aliases() -> dict[str, list[str]]:
    """Other names for the same step: {"bars": ["bar"], "dots": ["scatter"], ...}"""
    found: dict[str, list[str]] = {}
    for cls, kind in _classes():
        keys = [k for k in _all_keys() if _kind(k) == kind]
        words = {_word(k) for k in keys}
        for name in cls._word_names():
            if name in words:
                continue
            func = getattr(cls, name)
            for key in keys:
                if getattr(cls, _word(key)) is func:
                    found.setdefault(key, []).append(name)
    return found


def _call_form(key: str) -> str:
    kind = _kind(key)
    if kind == "option":
        return key
    if kind == "chart":
        return f"chart.{key}()"
    return f"{key}()"


def _prefixes(key: str) -> str:
    """What may come before the word in an example: table.keep_rows_where(...), chart.draw_bars(...)."""
    return _PREFIX.get(_kind(key), "chart|charts|sdata|page")


def _find_call(text: str, prefix_word: str,
               prefixes: str = "chart|charts|sdata|page|table|nums|grid|block|dist|system|f") -> str | None:
    """Find the first call like chart.draw_bars(...) in text, brackets and quotes included."""
    # "f" (a formula) only as a whole name: not the f at the end of "pdf." or "self."
    prefixes = "|".join(r"(?<![\w.])f" if p == "f" else p for p in prefixes.split("|"))
    m = re.search(rf"(?:{prefixes})\.{re.escape(prefix_word)}\(", text)
    if not m:
        return None
    depth, quote = 0, None
    for i in range(m.end() - 1, len(text)):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[m.start(): i + 1]
    return None


def _short_example(key: str) -> str:
    """One short example for the word list: from the docstring, else from the help example."""
    if key in OPTIONS:
        return OPTIONS[key]["example"]
    word, prefixes = _word(key), _prefixes(key)
    doc = inspect.getdoc(_function(key)) or ""
    call = _find_call(doc, word, prefixes) or _find_call(HELP_EXAMPLES.get(key, ""), word, prefixes)
    return call or _call_form(key)


_TABLE = re.compile(r'sdata\.example\("(\w+)"\)')


def _example_table(key: str) -> str | None:
    """The example table a word's examples use: named in the docstring, else in the help example.

    A docstring names its table like this: chart.draw_lines(...) (with sdata.get_example("weather")).
    """
    doc = "" if key in OPTIONS else inspect.getdoc(_function(key)) or ""
    found = _TABLE.search(doc) or _TABLE.search(HELP_EXAMPLES.get(key, ""))
    return found.group(1) if found else None


def _summary(key: str) -> str:
    """The first sentence of the word's docstring (without its example)."""
    if key in OPTIONS:
        return OPTIONS[key]["about"]
    doc = inspect.getdoc(_function(key)) or ""
    first = doc.split("\n\n")[0].replace("\n", " ")
    call = _find_call(first, _word(key), _prefixes(key))
    if call:
        first = first.split(call)[0]
        first = re.sub(r"\s*\w+\s*=\s*$", "", first)  # "... chart = table.start_chart()": drop "chart ="
    first = first.strip().rstrip(":").strip()
    if first and first[-1] not in ".!?)":
        first += "."
    return first


# ---------------------------------------------------------------- sdata.show_all_words()
def show_all_words() -> None:
    """Print every simplydata word with a short example. sdata.show_all_words()

    For more about one word, type sdata.help("draw_bars").
    """
    aliases = _aliases()
    pad = max(len(_display(k)) for k in _all_keys()) + 2
    print("simplydata words. Type sdata.help(\"draw_bars\") to learn more about any of them.")
    print("Chart words are steps on a chart: chart = sdata.chart(table), then chart.draw_bars(...).")
    print("Table words are steps on a table: table = sdata.table(...), then table.keep_rows_where(...).")
    print("Number words are steps on numbers: nums = sdata.numbers([3, 5, 2]), then nums.find_average();")
    print("grid words are steps on a grid of numbers: grid = sdata.number_grid([[1, 2], [3, 4]]).")
    print('Distribution words are steps on a distribution: dist = sdata.distribution("normal"), then '
          "dist.find_chance_that_value(is_above=2).")
    print('System words are steps on a system: system = sdata.system("1 / (s**2 + 2*s + 5)"), then '
          "system.step_response().")
    print('Formula words are steps on a formula: f = sdata.formula("(x + 2)**2 - 4"), then f.turn_into_sum().')
    print('The examples use the practice tables; sdata.help("word") shows which one, ready to run.')
    for group, keys in GROUPS:
        print()
        print(group)
        print("-" * len(group))
        for key in keys:
            line = f"  {_display(key):<{pad}}{_short_example(key)}"
            if key in aliases:
                line += "   (also: " + ", ".join(aliases[key]) + ")"
            print(line)
    print()
    print(f"Missing a word? Ask for it at {ISSUES_URL}")


# ---------------------------------------------------------------- sdata.help()
def _normalise(word: str) -> str:
    w = str(word).strip()
    for start in ("sdata.", "chart.", "charts.", "table.", "page.", "nums.", "grid.", "block.", "dist.", "system.", "f.", "."):
        if w.startswith(start):
            w = w[len(start):]
    if w.endswith("()"):
        w = w[:-2]
    return w.strip()


def _chart_or_ps_key(w: str) -> str | None:
    """A chart word, sdata word or option called w (already normalised), or None."""
    keys = _all_keys()
    if w in keys:
        return w
    if f"sdata.{w}" in keys:
        return f"sdata.{w}"
    if f"{w}=" in keys:
        return f"{w}="
    if w.endswith("=") and w[:-1] in keys:
        return w[:-1]
    for key, names in _aliases().items():
        if _kind(key) in ("chart", "sdata") and w in names:
            return key
    if w == "Chart":
        return "sdata.chart"
    if w == "Table":
        return "sdata.table"
    return None


def _object_key(w: str, kind: str = "table") -> str | None:
    """A table, numbers or grid word called w (already normalised), or None."""
    if f"{_PREFIX[kind]}.{w}" in _all_keys():
        return f"{_PREFIX[kind]}.{w}"
    for key, names in _aliases().items():
        if _kind(key) == kind and w in names:
            return key
    return None


def _table_key(w: str) -> str | None:
    """A table word called w (already normalised), or None."""
    return _object_key(w, "table")


def _lookup_all(word) -> list[str]:
    """Every key of GROUPS that what the user typed can mean.

    "save" is a word for charts, tables and numbers, so it gives all of them; "chart.save"
    and "table.save" give one each.
    """
    typed = str(word).strip()
    w = _normalise(typed)
    for kind, prefix in _PREFIX.items():
        if typed.startswith(prefix + "."):
            found = [_object_key(w, kind)]
            break
    else:
        if typed.startswith(("chart.", "page.", "sdata.")):
            found = [_chart_or_ps_key(w)]
        else:
            found = [_chart_or_ps_key(w)] + [_object_key(w, kind) for kind in _PREFIX]
    return [k for k in dict.fromkeys(found) if k is not None]


# How an object is written before a word, and the kind of object it is: "dist.chart" names the
# chart word of a distribution only. "sdata." is written in front of anything (sdata.help("sdata.bars")),
# so it narrows nothing.
_TYPED_KINDS = {"chart": {"chart"}, "page": {"chart"}, "charts": {"chart"}, "table": {"table"}, "nums": {"numbers"},
                "grid": {"grid", "numbers"}, "block": {"block", "grid", "numbers"}, "dist": {"dist"},
                "system": {"system"}, "f": {"formula"}}


def _old_names(word) -> list[tuple[str, str, str]]:
    """What an old name is called now: [(old, new, key of the new word), ...].

    Old words come from each object's _OLD_WORDS, old options from the renamed= of
    @friendly. Both still work for one release, but sdata.show_all_words() never lists them.
    A prefix is honoured: "dist.chart" gives only dist.draw_chart, and no options.
    """
    raw = str(word).strip()
    head = raw.split(".", 1)[0] if "." in raw.rstrip("()") else None
    kinds = _TYPED_KINDS.get(head)
    w = _normalise(raw)
    found = []
    for cls, kind in _classes():
        if kinds is not None and kind not in kinds:
            continue
        new = cls._OLD_WORDS.get(w)
        if new is None:
            continue
        new = new[0] if isinstance(new, tuple) else new
        key = new if kind == "chart" else f"{_PREFIX[kind]}.{new}"
        if key in _all_keys():
            found.append((w, new, key))
    new = _ps()._OLD_WORDS.get(w)
    if new and f"sdata.{new}" in _all_keys() and kinds is None:
        found.append((w, new, f"sdata.{new}"))
    if kinds is None:
        option = w.split("=", 1)[0].strip()
        for key, func in _words_with_options():
            for old, new in _renamed_options_of(func):
                if old.split("=", 1)[0] == option:
                    found.append((old, new, key))
    return list(dict.fromkeys(found))


def _renamed_options_of(func) -> list[tuple[str, str]]:
    """The old options of a word and what they are called now, each as written: ("method=", "test_method="); an
    old switch that is now one value of a new option gives ("bayesian=True", 'test_method="bayesian"')."""
    pairs = []
    for old, new in (getattr(func, "_renamed_options", None) or {}).items():
        if isinstance(new, tuple):  # @friendly(renamed={"bayesian": ("test_method", {True: "bayesian", ...})})
            name, values = new
            pairs.extend((f"{old}={value!r}", f'{name}="{now}"' if isinstance(now, str) else f"{name}={now!r}")
                         for value, now in values.items() if now is not None)
        else:
            pairs.append((f"{old}=", f"{new}="))
    return pairs


def _words_with_options():
    """(key, function) of every word, and of the grid summaries (grid.find_total ...), which share
    their entry with the number words but have options of their own (in_each=)."""
    pairs = [(key, _function(key)) for key in _all_keys()]
    grid = _grid_class()
    for name in grid._word_names():
        key = f"grid.{name}"
        if key not in _all_keys() and f"nums.{name}" in _all_keys():
            func = getattr(grid, name)
            if getattr(func, "_renamed_options", None):
                pairs.append((key, func))
    return pairs


def _old_name_lines(old, typed: str | None = None) -> tuple[list[str], list[str]]:
    """The lines sdata.help() prints for old names, each naming its object, and the keys to explain.

    One line per old word ("table.chart" is now called "table.start_chart"); an old option gets one
    line per new name, with the words it is in, and its new option is explained when it has an entry.
    typed is the object the user wrote ("grid" in "grid.average"), named in place of the one of the key.
    """
    lines, keys, options = [], [], {}
    for name, new, key in old:
        if "=" in name:
            options.setdefault((name, new), []).append(key)
            continue
        where = typed or (key.rsplit(".", 1)[0] if "." in key else "chart")
        line = f'"{where}.{name}" is now called "{where}.{new}".'
        if line not in lines:
            lines.append(line)
            keys.append(key)
    for (name, new), in_keys in options.items():
        calls = list(dict.fromkeys(_call_form(k) for k in in_keys))
        shown = ", ".join(calls[:4]) + (f" and {len(calls) - 4} more" if len(calls) > 4 else "")
        lines.append(f"{_quoted(name)} is now called {_quoted(new)} in {shown}.")
        if new in _all_keys():
            keys.append(new)
        elif len(calls) <= 3:
            keys.extend(k for k in in_keys if k in _all_keys())
    lines.append("The old names still work for now, but will stop working in a later version.")
    return lines, list(dict.fromkeys(keys))


def _lookup(word) -> str | None:
    """Turn what the user typed into a key of GROUPS (the first, if it has two), or None."""
    found = _lookup_all(word)
    return found[0] if found else None


# Options that many words share, each with one help line said the same way everywhere
SHARED_OPTIONS = {
    "test_method": "test_method= chooses the method (the test, estimator or rule) the word uses",
}


def _print_shared_option(word) -> bool:
    """sdata.help("test_method="): the shared help line and the words that have the option. True when printed."""
    name = _normalise(str(word)).split("=", 1)[0].strip()
    if name not in SHARED_OPTIONS:
        return False
    keys = [key for key, func in _words_with_options()
            if func is not None and name in inspect.signature(func).parameters]
    calls = list(dict.fromkeys(_call_form(k) for k in keys))
    print(f"{SHARED_OPTIONS[name]}. Each word has its own choices and its own default, and its printout names "
          "the method it used.")
    print(f"It is in {len(calls)} words: " + ", ".join(calls) + ".")
    print(f'To see the choices of one word, type sdata.help("{_call_form(keys[0])[:-2]}").')
    return True


def _options_text(key: str) -> list[str]:
    func = _function(key)
    if func is None:
        return []
    params = [p for p in inspect.signature(func).parameters.values()
              if p.name != "self" and not (p.kind is p.VAR_POSITIONAL and p.name == "extra")]
    if not params:
        return ["  (nothing: just write the empty brackets)"]
    width = max(len(p.name) for p in params) + 4
    lines = []
    for p in params:
        if p.kind is p.VAR_POSITIONAL:
            lines.append(f"  {p.name + '...':<{width}}as many as you like, separated by commas")
        elif p.kind is p.VAR_KEYWORD:
            continue
        elif p.default is p.empty:
            lines.append(f"  {p.name:<{width}}needed")
        elif p.default is None or type(p.default).__name__ == "_NotGiven":
            lines.append(f"  {p.name}=")
        else:
            normal = f'"{p.default}"' if isinstance(p.default, str) else repr(p.default)
            lines.append(f"  {p.name + '=':<{width}}normally {normal}")
        if p.name in SHARED_OPTIONS:
            lines[-1] = f"{lines[-1]:<{width + 2 + 24}}({SHARED_OPTIONS[p.name].split('= ', 1)[1]})"
    return lines


def _print_help_overview() -> None:
    print(textwrap.dedent("""\
        How to get help in simplydata

          sdata.help("draw_bars")        explains one word: what it does, its options and an example
          sdata.help("keep_rows_where")  works for table words too, and sdata.help("find_average")
                                         for numbers
          sdata.help("show=")            explains an option you use inside a step
          sdata.show_all_words()         lists every word, with a short example of each
          sdata.show_lesson()            lists the lessons: start in a day
          sdata.start_30_days()          or learn it in 30 days, an hour a day: then sdata.show_today()
          sdata.get_example()            lists the made-up tables you can practise with

        You can type the word with or without "chart." or "table." in front and with or
        without brackets: sdata.help("draw_bars"), sdata.help("chart.draw_bars") and
        sdata.help("draw_bars()") all work. A word that charts and tables both have, such as save,
        explains both, and sdata.help("table.save") explains only the table one. An old name, such
        as sdata.help("bars"), says what the word is called now.
        """))


def _print_one(key: str) -> None:
    title = _call_form(key)
    print(title)
    print("=" * len(title))
    print(f"Group: {_group_of(key)}")
    aliases = _aliases().get(key)
    if aliases:
        start = _PREFIX.get(_kind(key), "chart")
        print("Same word, other spelling: " + ", ".join(f"{start}.{a}()" for a in aliases))
    print()
    if key in OPTIONS:
        opt = OPTIONS[key]
        print(opt["about"])
        print()
        print(textwrap.fill(opt["text"], WIDTH))
        print()
        print("Works in: " + ", ".join(f"chart.{w}()" for w in opt["words"]))
    else:
        print(inspect.getdoc(_function(key)) or "")
        print()
        print("What you can put in the brackets (the text above says what each one does):")
        print("\n".join(_options_text(key)))
    if key in EXTRA_NOTES:
        print()
        print(textwrap.fill(EXTRA_NOTES[key], WIDTH))
    print()
    print("Example you can run:")
    print(textwrap.indent(HELP_EXAMPLES[key], "    "))


def _print_other_names(word) -> bool:
    """sdata.help("minimize"): a name from another tool points to the simplydata word (it never runs).

    Gives back True when something was printed."""
    from ._errors import other_name_pointer, other_name_target

    w = _normalise(str(word))
    found = [(kind, other_name_pointer(kind, w)) for kind in ("sdata", "table", "chart", "numbers")]
    found = [(kind, pointer) for kind, pointer in found if pointer is not None]
    if not found:
        return False
    print(f'simplydata has no word called "{w}": it is a name from other tools.')
    if len(found) == 1:
        print(found[0][1])
    else:
        for kind, pointer in found:
            print(f"  {_PREFIX.get(kind, kind)}.{w}: {pointer}")
    targets = list(dict.fromkeys(other_name_target(pointer) for _, pointer in found))
    print("To learn more, type " + " or ".join(f'sdata.help("{t}")' for t in targets) + ".")
    return True


def help(word=None) -> None:  # noqa: A001 - meant to be sdata.help
    """Explain one word: what it does, its options and an example you can run. sdata.help("draw_bars")

    sdata.help() on its own explains how to get help. Table words work too: sdata.help("keep_rows_where").
    """
    if word is None:
        _print_help_overview()
        return None
    if isinstance(word, str):
        keys = _lookup_all(word)
    else:
        keys = [k for k in _all_keys() if k not in OPTIONS and _function(k) is word][:1]
        name = getattr(word, "__name__", None)
        if not keys and name is not None:
            keys = _lookup_all(name)
        if not keys:
            return builtins.help(word)  # not a simplydata word: Python's own help
        word = name
    old = _old_names(word)
    # "band=" is an old option (now with_confidence_band= in fit_line), although band is also a word
    if old and (not keys or str(word).strip().endswith("=")):
        typed = str(word).strip().split(".", 1)[0] if "." in str(word).strip().rstrip("()") else None
        lines, keys = _old_name_lines(old, typed if typed in _TYPED_KINDS and typed != "page" else None)
        if not keys:  # an old option of many words: say where to read more, not every word
            lines.append(f'To learn more, type sdata.help("{_call_form(old[0][2])[:-2]}").')
        print("\n".join(lines))
        if not keys:
            return None
        print()
    if not keys and _print_other_names(word):
        return None
    if not keys and _print_shared_option(word):
        return None
    if not keys:
        known = sorted({_normalise(k) for k in _all_keys()} | {a for v in _aliases().values() for a in v})
        lines = [f'simplydata has no word called "{word}".']
        guesses = suggest(_normalise(word), known)
        if guesses:
            lines.append("Did you mean " + " or ".join(f'sdata.help("{g}")' for g in guesses) + "?")
        lines.append("Type sdata.show_all_words() to see every word.")
        lines.append(f"Missing something? Ask for it at {ISSUES_URL}")
        print("\n".join(lines))
        return None

    for i, key in enumerate(keys):
        if i:
            print()
            print("-" * WIDTH)
            print()
        _print_one(key)
    if len(keys) > 1:
        forms = " or ".join(f'sdata.help("{_call_form(k)[:-2]}")' for k in keys)
        print()
        print(_wrap(f'"{_normalise(word)}" can mean more than one word, so each one is explained '
                    f"above. For only one, type {forms}."))
    return None


# ---------------------------------------------------------------- sdata.show_lesson()
def _sx(code: str) -> str:
    """A worked solution's code, written indented in LESSONS and given back without the indent."""
    return textwrap.dedent(code).strip()


# Each lesson: title, what you will learn, one or more parts, and a task.
# Each part: a sentence to start, then (line of code, what it does) pairs.
# The code of each part runs on its own (the tests run every part).
# solutions: one (code, one-line explanation) for each task, in the same order. Each runs on
# its own (the tests run every one), and sdata.show_lesson(3, solutions=True) prints them.
# The lessons of v0.6, found by title (learn_days.py and the tests use lesson_number), so their numbers can
# change when lessons are added before them. Agreed order across branches: S2's "Working with a model" is
# lesson 21, S1's "Risks, diagnostic tests and agreement" 22, these four 23 to 26, S3a's lesson 27.
TIME_SERIES_LESSON = "Time series: dates, missing days, time windows and trend"
FORECASTS_LESSON = "Forecasts: the next months, checked first"
CYCLES_LESSON = "Cycles: spectra, filters, peaks, and steady or not"
SYSTEMS_LESSON = "Systems: a spring and damper, its response and a feedback loop"
# S3a: outliers (S3a-1) and percentile lines (S3a-2), the title of the name review of 2026-11-20
OUTLIERS_LESSON = "Beyond the average line: percentiles and outliers"
# S3a-3: the interaction lesson (lesson 28; found by title)
INTERACTIONS_LESSON = "When one effect depends on another"
MORE_SURVIVAL_LESSON = "More survival: start times, competing events, adjusted curves"  # S3b-3
# S3b-1: combining studies (lesson 30; found by title)
COMBINING_LESSON = "Combining studies (meta-analysis)"
DIVERSITY_LESSON = "Diversity of a community"  # S3c-1
MAKEUP_LESSON = "Make-up of communities"  # S3c-1
COAST_LESSON = "A coastal station: currents, neighbours and storms"  # S3c-3
PLANNING_LESSON = "Planning an experiment and a survey"  # S3d-1
CAUSE_LESSON = "Cause and effect from observational data"  # S3d-2
BAYES_LESSON = "Bayesian answers: how likely, given the data and the prior"  # S3d-3
FJORD_LESSON = "Tables: a messy file from a fjord cruise"  # tables phase, batch 1
GENES_LINE = ('genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB", "aadA", "mphA", "vanA", "mcr1"]')
COMBINE_CALL = ('table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"], '
                'out_of=["vaccinated", "unvaccinated"])')

LESSONS = [
    dict(
        title="Your first chart",
        learn=[
            "how to get a table to practise with",
            "how to start a chart and draw bars",
            "how to save your chart as a picture",
        ],
        parts=[
            ("A simplydata program is made of small steps, one step on each line, and each step "
             "says what it does.", [
                ("import simplydata as sdata", 'Load simplydata. From now on we call it by its short name, "sdata".'),
                ("sdata.get_example()", "List the made-up tables you can practise with, and their columns."),
                ('marks = sdata.get_example("marks")', "Get the marks table: test marks of made-up children. "
                                                "We call it marks."),
                ("print(marks)", "Look at the table. Each row is one child in one test. The names at "
                                 "the top (name, class, subject ...) are the columns."),
                ("chart = sdata.chart(marks)", "Start a new, empty chart that uses the marks table. We "
                                            "call it chart, and every next line starts with that name."),
                ('chart.draw_bars(x="name", y="marks")', "Draw bars: one bar for each name (along x, the "
                                                    "bottom), as tall as the marks (up y, the side). "
                                                    "Each child did three tests, so the bar shows the "
                                                    "average: add the three marks up and divide by 3."),
                ('chart.save("lesson1.png")', "Save the chart as a picture called lesson1.png, in the "
                                              "folder you are working in. Open it to see your chart!"),
            ]),
        ],
        notes=[
            "Each line is an instruction to the chart: chart.draw_bars, chart.draw_lines, chart.draw_dots ... The "
            "chart is the thing, and draw_bars says what it should do.",
            'For your own data, write chart = sdata.chart("my_marks.xlsx"). Excel, CSV, TSV, Parquet '
            "and JSON files all work.",
            'chart.save("lesson1.pdf") saves a PDF instead: the end of the name decides the type.',
            "In Jupyter, VS Code or Spyder, write chart on the last line of a cell and the chart "
            "appears by itself. In a script, chart.show() opens it in a window.",
            "Are the names under the bars bumping into each other? Lesson 2 shows how to turn them.",
            "chart.get_numbers_drawn() gives back a table of the numbers the chart drew (the height of each "
            "bar, the points of each line), to check a chart or to quote its numbers.",
            "Learning on your own? sdata.start_30_days() turns the everyday lessons into 30 days of about an hour: "
            "each day starts with a few questions on earlier days and ends with a task. Then type "
            'sdata.show_today() each day (or sdata.start_30_days(track="beginner") if you have never programmed).',
        ],
        task=[
            'Change x="name" to x="subject". What does each bar show now?',
            'Save the chart as "my_first_chart.png" and also as "my_first_chart.pdf".',
            'Make a chart of the "fruit" table: bars with x="fruit" and y="count".',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="subject", y="marks")
                chart.save("lesson1_subjects.png")"""),
             "Each bar is now one subject, as tall as the average mark of all 18 children in that "
             "subject."),
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="name", y="marks")
                chart.save("my_first_chart.png")
                chart.save("my_first_chart.pdf")"""),
             "One chart can be saved many times; the end of the file name (.png or .pdf) decides "
             "the type."),
            (_sx("""\
                import simplydata as sdata
                fruit = sdata.get_example("fruit")
                chart = sdata.chart(fruit)
                chart.draw_bars(x="fruit", y="count")
                chart.save("fruit.png")"""),
             "One bar per fruit. Each fruit was sold several times, so a bar is the average count "
             'of one sale; show="total" would show how many were sold in the whole week.'),
        ],
        words=["sdata.get_example", "sdata.chart", "draw_bars", "save", "show", "sdata.start_30_days", "sdata.show_today"],
    ),
    dict(
        title="Titles and labels",
        learn=[
            "how to put a title on top",
            "how to name the x-axis and the y-axis",
            "how to add a small caption and change the size of the text",
        ],
        parts=[
            ("A chart is easier to read when it says what it shows. First draw, then add the words.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_bars(x="name", y="marks")', "Draw one bar for each child."),
                ('chart.write_title_on_top("Our class marks")', "Write a title on top of the chart."),
                ('chart.label_x("Student")', "Write a name under the x-axis (the bottom)."),
                ('chart.label_y("Average mark")', "Write a name beside the y-axis (the side)."),
                ("chart.rotate_labels_x(45)", "Turn the names under the bars by 45 degrees, so "
                                              "long names do not bump into each other."),
                ('chart.write_caption_at_bottom("Made-up data from sdata.get_example")', "Write a small line under "
                                                                         "the whole chart."),
                ("chart.use_font_size(14)", "Make all the text a bit bigger (normal is 12)."),
                ('chart.save("lesson2.png")', "Save it."),
            ]),
            ("Words can also go next to the dots: a name for each dot, where it covers nothing.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('kids = {"name": ["Asha", "Ben", "Chen", "Dina", "Eli"], "hours": [2.0, 5.5, 3.1, 7.2, 4.4], '
                 '"marks": [48, 71, 55, 88, 62]}', "A small table typed by hand: each column name, then its "
                                                   "values in a list."),
                ("chart = sdata.chart(kids)", "Start a chart of it."),
                ('chart.draw_dots(x="hours", y="marks")', "One dot for each child."),
                ('chart.write_names_on_dots("name")', "Write each name next to its dot, where it covers no other "
                                                "name or dot. A name with no free place is left out, and "
                                                "a line says so."),
                ('chart.label_x("Hours of study")', "Name the x-axis."),
                ('chart.save("lesson2_names.png")', "Save it."),
            ]),
        ],
        notes=[
            "After the chart type, the order of words such as write_title_on_top and label_y does not matter: "
            "the chart is drawn when you save or show it.",
            "Words that belong to one axis end in _x or _y: label_x, label_y, rotate_labels_x.",
        ],
        task=[
            'Give the chart your own title, and label the y-axis "Marks out of 100".',
            "Try chart.use_font_size(20). Then try 9. Which is easier to read?",
            "Take away the line chart.rotate_labels_x(45). What happens to the names?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="name", y="marks")
                chart.write_title_on_top("How well did each child do?")
                chart.label_y("Marks out of 100")
                chart.rotate_labels_x(45)
                chart.save("lesson2_my_title.png")"""),
             "write_title_on_top writes any title you like, and label_y names the y-axis."),
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="name", y="marks")
                chart.write_title_on_top("Our class marks")
                chart.rotate_labels_x(45)
                chart.use_font_size(20)
                chart.save("lesson2_big_text.png")
                chart.use_font_size(9)
                chart.save("lesson2_small_text.png")"""),
             "The last use_font_size wins, so one chart gives both pictures. Size 20 is easy to read on "
             "a slide but crowds the names; 9 fits everything but is small. 12 to 14 suits most charts."),
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="name", y="marks")
                chart.write_title_on_top("Our class marks")
                chart.save("lesson2_no_rotate.png")"""),
             "Without rotate_labels_x the 18 names lie flat under the bars and run into each other."),
        ],
        words=["write_title_on_top", "label_x", "label_y", "rotate_labels_x", "write_caption_at_bottom", "use_font_size",
               "write_names_on_dots"],
    ),
    dict(
        title="Colours, groups and legends",
        learn=[
            "how to give each group its own colour",
            "how to choose your own colours",
            "how to move the legend (the box that says which colour is which)",
            "how to change the whole look with a style",
        ],
        parts=[
            ("colour= inside a chart type splits the data into groups.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_bars(x="subject", y="marks", colour="class")', "For each subject, draw one "
                                                                       "bar per class, each class "
                                                                       "in its own colour."),
                ('chart.use_colours("orange", "teal", "purple")', "Choose the colours yourself, in order: "
                                                              "class A orange, B teal, C purple."),
                ("chart.put_legend_at_bottom()", "Put the legend under the chart."),
                ('chart.write_title_on_top("Marks in each subject")', "Add a title."),
                ('chart.save("lesson3_groups.png")', "Save it."),
            ]),
            ("Without groups, one colour is used for everything. You can choose it.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.get_example("weather")', "Get the weather table: three made-up cities."),
                ("chart = sdata.chart(weather)", "Start a chart."),
                ('chart.draw_lines(x="month", y="rain")', "Draw a line of rain through the months. With "
                                                     "three cities in each month, the line shows "
                                                     "their average."),
                ('chart.use_colour("blue")', "Make the line blue."),
                ('chart.use_style("school")', 'Change the whole look. Try "paper", "school", '
                                          '"presentation" and "dark".'),
                ('chart.save("lesson3_look.png")', "Save it."),
            ]),
            ("Groups come in the order they first appear in the table. You can choose another order, "
             "and give the legend a name.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_bars(x="class", y="marks", colour="subject")', "For each class, one bar per subject."),
                ('chart.order_x("C", "B", "A")', "Put the classes along the x-axis in this order."),
                ('chart.order_legend("Science", "Maths", "English")', "Put the subjects in this order: in the "
                                                                      "legend and side by side in each class."),
                ('chart.label_legend("Subject")', "The name above the legend (normally the column name)."),
                ('chart.save("lesson3_order.png")', "Save it."),
            ]),
            ("Numbers can have colours too: a colour scale. And dots that overlap are easier to see when "
             "they let the others show through.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.get_example("weather")', "Get the weather table."),
                ("chart = sdata.chart(weather)", "Start a chart."),
                ('chart.draw_heatmap(x="month", y="city", value="temperature")', "One square per city and month, "
                                                                           "coloured by temperature."),
                ('chart.use_colour_scale("blue to red", middle=10)', "Blue below 10 °C, red above, white at 10. "
                                                                "middle= makes a scale that goes two ways."),
                ('chart.save("lesson3_colour_scale.png")', "Save it."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("dots = sdata.chart(marks)", "A second chart."),
                ('dots.draw_dots(x="hours", y="marks", colour="class", transparency=0.5)',
                 "transparency=0.5 makes each dot half see-through, so dots on top of each other show."),
                ('dots.save("lesson3_transparency.png")', "Save it."),
            ]),
        ],
        notes=[
            'colour="class" (a column) gives each group a colour. colour="red" (a colour) makes '
            "that step red. color works too.",
            "The legend can go on any side: put_legend_at_top, put_legend_at_bottom, put_legend_on_left, put_legend_on_right. "
            "hide_legend takes it away and show_legend brings it back.",
            'Month and weekday names ("Jan", "Monday") come in calendar order by themselves, also in '
            "the small charts of draw_one_chart_for_each_group_in and the frames of animate. order_x(biggest_first=True) "
            "puts the biggest bar first, and order_y orders the groups up the y-axis.",
        ],
        task=[
            'In the weather chart, add colour="city" to chart.draw_lines(...). How many lines do you get?',
            "Move the legend to the top with chart.put_legend_at_top().",
            'Try chart.use_style("dark") and choose three colours that look good on it.',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                weather = sdata.get_example("weather")
                chart = sdata.chart(weather)
                chart.draw_lines(x="month", y="rain", colour="city")
                chart.save("lesson3_cities.png")"""),
             "Three lines, one for each city, and a legend that says which colour is which city."),
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="subject", y="marks", colour="class")
                chart.use_colours("orange", "teal", "purple")
                chart.put_legend_at_top()
                chart.save("lesson3_legend_top.png")"""),
             "put_legend_at_top puts the legend above the chart, in place of put_legend_at_bottom."),
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="subject", y="marks", colour="class")
                chart.use_style("dark")
                chart.use_colours("gold", "turquoise", "hotpink")
                chart.save("lesson3_dark.png")"""),
             "Light, bright colours stand out on a dark background; dark colours such as navy "
             "would almost disappear."),
        ],
        words=["use_colours", "use_colour", "use_colour_scale", "put_legend_at_bottom", "put_legend_at_top", "hide_legend", "use_style", "draw_lines",
               "order_x", "order_legend", "label_legend"],
    ),
    dict(
        title="Different chart types",
        learn=[
            "lines, dots, histograms, boxes and pies",
            "which chart suits which question",
            "how to put two chart types on top of each other",
        ],
        parts=[
            ("Lines show how something changes, for example over time.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.get_example("weather")', "Get the weather table."),
                ("chart = sdata.chart(weather)", "Start a chart."),
                ('chart.draw_lines(x="month", y="temperature", colour="city", with_dots=True)',
                 "One line per city. with_dots=True also marks each month with a dot."),
                ('chart.save("lesson4_lines.png")', "Save it."),
            ]),
            ("Dots show if two things go together. This is also called a scatter chart.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_dots(x="hours", y="marks", colour="class")', "One dot for each test: how "
                                                                    "long the child studied, "
                                                                    "and the mark they got."),
                ('chart.save("lesson4_dots.png")', "Save it. Do more hours give more marks?"),
            ]),
            ("A histogram counts how many values fall in each range, like 40 to 50, 50 to 60 ... "
             "Its shape is called the distribution of the values.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_histogram(x="marks", with_bins=8)', "Cut the marks into 8 ranges (bins) and "
                                                       "draw a bar for how many marks are in each."),
                ('chart.save("lesson4_histogram.png")', "Save it."),
            ]),
            ("Boxes show how spread out the values are. Two chart types on one chart are drawn "
             "one on top of the other.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_boxes(x="class", y="marks")', "One box per class. The line in the box is "
                                                      "the median: the middle mark when they are "
                                                      "put in order. The box holds the middle half "
                                                      "of the marks (the interquartile range)."),
                ('chart.draw_all_dots(x="class", y="marks")', "Also show every single mark as a dot, "
                                                         "on top of the boxes."),
                ('chart.save("lesson4_boxes.png")', "Save it."),
            ]),
            ("A pie shows how a whole is shared out.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('fruit = sdata.get_example("fruit")', "Get the fruit table: what two shops sold in a week."),
                ("chart = sdata.chart(fruit)", "Start a chart."),
                ('chart.draw_pie(labels="fruit", values="count")', "One slice per fruit, as big as the "
                                                              "number sold."),
                ('chart.save("lesson4_pie.png")', "Save it."),
            ]),
        ],
        notes=[
            "Chart types on the same chart are layers of one chart. Lesson 7 shows how to make "
            "several charts and put them on one page.",
            "There are more chart types: draw_area, draw_violins, draw_heatmap, draw_polar, draw_contour, draw_surface and "
            "draw_dots_3d. Type sdata.show_all_words() to see them all and sdata.help(\"draw_violins\") to learn one.",
        ],
        task=[
            'Draw chart.draw_violins(x="class", y="marks") instead of boxes. What is different?',
            'Draw a histogram of the weather "temperature" column with with_bins=6.',
            'Make a chart of sdata.get_example("growth") and draw chart.draw_area(x="year", y="population", '
            'colour="country").',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_violins(x="class", y="marks")
                chart.draw_all_dots(x="class", y="marks")
                chart.save("lesson4_violins.png")"""),
             "A violin shows the whole shape of the marks: it is wide where many marks are and "
             "thin where few are. A box shows only the middle half and the median."),
            (_sx("""\
                import simplydata as sdata
                weather = sdata.get_example("weather")
                chart = sdata.chart(weather)
                chart.draw_histogram(x="temperature", with_bins=6)
                chart.save("lesson4_temperature.png")"""),
             "Six ranges of temperature, each bar as high as the number of months (of all three "
             "cities) that fall in it."),
            (_sx("""\
                import simplydata as sdata
                growth = sdata.get_example("growth")
                chart = sdata.chart(growth)
                chart.draw_area(x="year", y="population", colour="country")
                chart.save("lesson4_area.png")"""),
             "An area chart is a line chart with the space under each line filled in."),
        ],
        words=["draw_lines", "draw_dots", "draw_histogram", "draw_boxes", "draw_all_dots", "draw_pie", "draw_violins", "draw_area"],
    ),
    dict(
        title="Statistics: averages, error bars and fit lines",
        learn=[
            "what a bar shows when a group has many values: the average or the median",
            "how to add error bars, and the difference between standard deviation and standard error",
            "how to draw the straight line that fits some dots best",
        ],
        parts=[
            ("The average (also called the mean) is all the values added up, divided by how many "
             "there are. Error bars show how far the values spread around it.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_bars(x="class", y="marks", show="average", error="standard deviation")',
                 "One bar per class, as tall as the average mark. The error bars show the standard "
                 "deviation: how far marks usually are from the average. A line is printed that "
                 "says which error bars were drawn."),
                ("chart.write_numbers_on_bars()", "Write the average on each bar."),
                ('chart.save("lesson5_average.png")', "Save it."),
            ]),
            ("A fit line is the straight line that goes as close as possible to all the dots.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_dots(x="hours", y="marks")', "One dot per test: hours of study and the mark."),
                ("chart.fit_line(with_confidence_band=True, show_equation=True)", "Add the best straight "
                 "line (also called linear regression). with_confidence_band=True shades where the true "
                 "line very likely is (the 95 % confidence interval). show_equation=True writes its "
                 "equation and R² (1 means the dots sit right on the line, 0 means no pattern at all)."),
                ('chart.save("lesson5_fit.png")', "Save it."),
            ]),
            ("A density curve is a smooth histogram: high where many values are.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_density(x="marks", colour="class")', "One smooth curve for each class "
                                                             "(a kernel density estimate)."),
                ('chart.save("lesson5_density.png")', "Save it."),
            ]),
            ("Two more ways to see the shape of values: are they bell-shaped, and what share lies below "
             "each value?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_qq_dots("marks")', "A Q-Q plot: if the marks follow a bell curve (normal), the dots "
                                          "lie close to the straight line."),
                ('chart.save("lesson5_qq.png")', "Save it."),
                ("shares = sdata.chart(marks)", "A second chart."),
                ('shares.draw_cumulative_share(x="marks", colour="class")',
                 "For each mark, the share of children with that mark or less (an ECDF). The class whose "
                 "line is further right did better."),
                ('shares.save("lesson5_cumulative.png")', "Save it."),
            ]),
        ],
        notes=[
            "Average or median? The median is the middle value when the values are put in order. "
            "One very big or very small value pulls the average towards it, but hardly moves the "
            "median, so the median is safer when a few values are far from the rest (outliers).",
            'show= can be "average", "median", "total" (all added up), "count" (how many rows), '
            '"smallest", "biggest" or "standard deviation": the same names as the table words '
            "find_average_of, find_median_of and so on.",
            "Standard deviation or standard error? The standard deviation describes the values: how "
            "spread out they are. The standard error describes the average: how sure we are of it. "
            "It gets smaller as you collect more values, even when the values spread just as much.",
            'error="confidence interval" draws the 95 % confidence interval: the range the true '
            'average is very likely to be in. The short forms "sd", "se" and "ci" work too. Always '
            "say in your caption which error bars you drew.",
            "fit_curve(of_degree=2) fits a curve with one bend; draw_smooth_line() follows the dots freely.",
        ],
        task=[
            'Change show="average" to show="median". Do the bars change much?',
            'Change error="standard deviation" to error="standard error". Are the error bars '
            "bigger or smaller? Why?",
            'Make a chart of the weather table, draw dots with x="month_number", y="temperature" '
            "and add chart.fit_curve(of_degree=2).",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="class", y="marks", show="median")
                chart.write_numbers_on_bars()
                chart.save("lesson5_median.png")"""),
             "Error bars go with averages, so error= comes out. The medians (A 74, B 68.5, C 57) "
             "are close to the averages (A 71.8, B 64.3, C 58.6): no single mark pulls them far."),
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="class", y="marks", show="average", error="standard error")
                chart.save("lesson5_standard_error.png")"""),
             "Smaller: the standard error is the standard deviation divided by the square root of "
             "the number of values (here 18), so it is about a quarter of the standard deviation."),
            (_sx("""\
                import simplydata as sdata
                weather = sdata.get_example("weather")
                chart = sdata.chart(weather)
                chart.draw_dots(x="month_number", y="temperature", colour="city")
                chart.fit_curve(of_degree=2)
                chart.save("lesson5_fit_curve.png")"""),
             "Each city gets a curve with one bend: warm in the middle of the year, cold at both ends."),
        ],
        words=["show=", "error=", "write_numbers_on_bars", "fit_line", "draw_density", "fit_curve", "draw_smooth_line",
               "draw_qq_dots", "draw_cumulative_share"],
    ),
    dict(
        title="Axes and reference lines",
        learn=[
            "how to choose where an axis starts and stops",
            "how to draw a line at a value, like a pass mark, and shade a band",
            "how to choose the tick marks, and what a log scale is",
        ],
        parts=[
            ("The axes are the two edges with numbers: x along the bottom, y up the side.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_bars(x="name", y="marks")', "One bar for each child."),
                ("chart.set_range_y(0, 100)", "Make the y-axis go from 0 to 100, the lowest and highest "
                                          "mark you can get."),
                ("chart.put_ticks_y(0, 25, 50, 75, 100)", "Put the numbers on the y-axis at these places."),
                ('chart.draw_line_at_y(50, labelled="pass mark")', "Draw a dashed line across at 50, with a name."),
                ("chart.shade_between_y(40, 60)", "Shade the band between 40 and 60."),
                ("chart.rotate_labels_x()", "Turn the names so they fit."),
                ('chart.save("lesson6_marks.png")', "Save it."),
            ]),
            ("On a log scale 1, 10, 100 and 1000 are the same distance apart. It helps when some "
             "numbers are much bigger than others.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('growth = sdata.get_example("growth")', "Get the growth table: people in four made-up "
                                                  "countries."),
                ("chart = sdata.chart(growth)", "Start a chart."),
                ('chart.draw_lines(x="year", y="population", colour="country")', "One line per country."),
                ("chart.use_log_scale_y()", "Use a log scale on the y-axis. A country that grows by the "
                                        "same share each year now gets a straight line."),
                ('chart.draw_line_at_x(2010, labelled="2010")', "Draw an up-and-down line at the year 2010."),
                ('chart.label_y("People (millions)")', "Name the y-axis."),
                ('chart.save("lesson6_log.png")', "Save it."),
            ]),
            ("A band shades the space between a low and a high value at each x: a range, or the "
             "uncertainty around a line.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('days = {"day": [1, 2, 3, 4, 5], "lowest": [3, 5, 4, 6, 8], "average": [6, 8, 7, 9, 11], '
                 '"highest": [9, 11, 10, 12, 14]}', "A small table: the lowest, average and highest "
                                                    "temperature on five days."),
                ("chart = sdata.chart(days)", "Start a chart of it."),
                ('chart.draw_band(x="day", between=["lowest", "highest"], labelled="lowest to highest")',
                 "Shade from the lowest to the highest value of each day. labelled= names it in the legend."),
                ('chart.draw_lines(x="day", y="average")', "The average as a line through the band."),
                ('chart.label_y("Temperature (°C)")', "Name the y-axis."),
                ('chart.save("lesson6_band.png")', "Save it."),
            ]),
            ("Axes can say what their numbers mean, and a 1:1 line shows where two columns agree.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('growth = sdata.get_example("growth")', "Get the growth table."),
                ("chart = sdata.chart(growth)", "Start a chart."),
                ('chart.draw_lines(x="year", y="forest", colour="country")', "The forest of each country, in %."),
                ('chart.write_ticks_y_as("percent")', 'Write the y numbers as 40 %, 50 % ... ("thousands", '
                                                   '"scientific" and dates such as "Jan 2026" work too).'),
                ('chart.save("lesson6_percent.png")', "Save it."),
                ('guesses = {"measured": [12, 18, 25, 31, 40], "predicted": [14, 17, 27, 29, 43]}',
                 "Five measured values and what a model predicted for them."),
                ("check = sdata.chart(guesses)", "A second chart."),
                ('check.draw_dots(x="measured", y="predicted")', "One dot per value."),
                ('check.draw_line_with_slope(1, through=(0, 0), labelled="1:1")',
                 "The 1:1 line: dots on it were predicted exactly; above it, too high."),
                ('check.save("lesson6_one_to_one.png")', "Save it."),
            ]),
        ],
        notes=[
            "Every axis word ends in _x or _y: set_range_x, put_ticks_x, use_log_scale_x, draw_line_at_x, "
            "shade_between_x, flip_x ...",
            "set_range_y(0, None) fixes only the bottom and lets the top choose itself.",
            "Bars should start at 0: a bar is read by its length, so a y-axis that starts at 40 "
            "makes small differences look big.",
        ],
        task=[
            "Move the pass mark to 60 and shade between 0 and 40 instead.",
            "Take away chart.use_log_scale_y(). Which countries look different?",
            "Try chart.flip_y() on any chart. What happens?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="name", y="marks")
                chart.set_range_y(0, 100)
                chart.draw_line_at_y(60, labelled="pass mark")
                chart.shade_between_y(0, 40)
                chart.rotate_labels_x()
                chart.save("lesson6_pass_60.png")"""),
             "draw_line_at_y(60) moves the line; shade_between_y(0, 40) shades the band from 0 to 40."),
            (_sx("""\
                import simplydata as sdata
                growth = sdata.get_example("growth")
                chart = sdata.chart(growth)
                chart.draw_lines(x="year", y="population", colour="country")
                chart.draw_line_at_x(2010, labelled="2010")
                chart.label_y("People (millions)")
                chart.save("lesson6_no_log.png")"""),
             "The lines now bend upwards instead of running straight, and the small countries "
             "(Cherria and Applia) sit low and look flat, although Cherria nearly triples."),
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_bars(x="class", y="marks")
                chart.flip_y()
                chart.save("lesson6_flip.png")"""),
             "The y-axis turns upside down: 0 is at the top and the bars hang down. Useful for "
             "depths, where bigger numbers are further down."),
        ],
        words=["set_range_y", "put_ticks_y", "draw_line_at_y", "shade_between_y", "use_log_scale_y", "draw_line_at_x", "flip_y",
               "draw_band", "write_ticks_y_as", "draw_line_with_slope"],
    ),
    dict(
        title="Several charts together",
        learn=[
            "how to make one small chart for each group",
            "how to put different charts on one page: side by side, one above the other, or in a grid",
            "how to write A, B, C on the charts, as figures in papers have",
            "how to compare every number column with every other",
        ],
        parts=[
            ("draw_one_chart_for_each_group_in draws the same chart once for each group.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_dots(x="hours", y="marks")', "Dots of hours and marks."),
                ("chart.fit_line()", "Add a fit line."),
                ('chart.draw_one_chart_for_each_group_in("class")', "Make one small chart for each class, with the same "
                                                 "axes so they are easy to compare."),
                ('chart.save("lesson7_one_chart_per.png")', "Save it."),
            ]),
            ("Each chart is an object of its own, so different charts can share one page.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.get_example("weather")', "Get the weather table."),
                ('a = sdata.chart(weather).draw_lines(x="month", y="temperature", colour="city")',
                 "Make a first chart, called a. Steps can also be joined with dots on one line."),
                ('b = sdata.chart(weather).draw_bars(x="month", y="rain", colour="city")',
                 "Make a second chart, called b."),
                ("charts = sdata.put_one_above_other(a, b)", "Put a above b on one page."),
                ('charts.write_title_on_top("A year of weather")', "Give the whole page a title."),
                ('charts.save("lesson7_page.png")', "Save the page."),
            ]),
            ("A grid holds many charts in rows and columns. with_letters=True writes A, B, C and D on "
             "them, as figures in papers have.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ('a = sdata.chart(marks).draw_bars(x="class", y="marks").write_title_on_top("Average")', "Chart a."),
                ('b = sdata.chart(marks).draw_histogram(x="marks").write_title_on_top("All marks")', "Chart b."),
                ('c = sdata.chart(marks).draw_dots(x="height", y="marks").write_title_on_top("Height")', "Chart c."),
                ('d = sdata.chart(marks).draw_boxes(x="subject", y="marks").write_title_on_top("Subjects")', "Chart d."),
                ("charts = sdata.put_in_rows_and_columns(a, b, c, d, per_row=2, with_letters=True)", "All four in a grid, 2 charts "
                                                                        "per row, with a letter on each."),
                ('charts.save("lesson7_grid.png")', "Save it."),
            ]),
            ("Charts from different tables can share a page too.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('rain = sdata.chart(sdata.get_example("weather")).draw_lines(x="month", y="rain", colour="city")',
                 "A chart of the weather table, called rain."),
                ('forest = sdata.chart(sdata.get_example("growth")).draw_lines(x="year", y="forest", colour="country")',
                 "A chart of the growth table, called forest."),
                ("charts = sdata.put_side_by_side(rain, forest, with_letters=True)", "Put the two charts next to "
                                                                       "each other, with A and B."),
                ('charts.save("lesson7_two_tables.png")', "Save the page."),
            ]),
            ("sdata.draw_all_pairs draws every number column against every other, in one go.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('pairs = sdata.draw_all_pairs(sdata.get_example("marks"), colour="class")', "Hours, marks and height, "
                                                                          "each against each other. "
                                                                          "The middle line shows how "
                                                                          "each column is spread out."),
                ('pairs.save("lesson7_pairs.png")', "Save it. Which two columns go together?"),
            ]),
        ],
        notes=[
            "same_y=True gives all the charts on a page the same y-axis, so heights can be "
            "compared fairly: sdata.put_side_by_side(a, b, same_y=True).",
            "sdata.put_side_by_side, sdata.put_one_above_other and sdata.put_in_rows_and_columns all take with_letters=True.",
            'chart.draw_one_chart_for_each_group_in(down="class", across="subject") makes a table of small charts: '
            "the classes go down, the subjects go across. per_row=3 puts 3 small charts in a row.",
        ],
        task=[
            'Change chart.draw_one_chart_for_each_group_in("class") to chart.draw_one_chart_for_each_group_in("subject").',
            "Use sdata.put_side_by_side(a, b) instead of sdata.put_one_above_other(a, b) for the weather charts.",
            'Make sdata.draw_all_pairs of sdata.get_example("weather") with colour="city".',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                marks = sdata.get_example("marks")
                chart = sdata.chart(marks)
                chart.draw_dots(x="hours", y="marks")
                chart.fit_line()
                chart.draw_one_chart_for_each_group_in("subject")
                chart.save("lesson7_per_subject.png")"""),
             "One small chart for each subject (Maths, Science and English), each with its own fit line."),
            (_sx("""\
                import simplydata as sdata
                weather = sdata.get_example("weather")
                a = sdata.chart(weather).draw_lines(x="month", y="temperature", colour="city")
                b = sdata.chart(weather).draw_bars(x="month", y="rain", colour="city")
                charts = sdata.put_side_by_side(a, b)
                charts.write_title_on_top("A year of weather")
                charts.save("lesson7_side_by_side.png")"""),
             "The same two charts, now next to each other instead of one above the other."),
            (_sx("""\
                import simplydata as sdata
                pairs = sdata.draw_all_pairs(sdata.get_example("weather"), colour="city")
                pairs.save("lesson7_weather_pairs.png")"""),
             "Every number column of the weather table against every other, one colour per city."),
        ],
        words=["draw_one_chart_for_each_group_in", "sdata.put_one_above_other", "sdata.put_in_rows_and_columns", "sdata.put_side_by_side", "sdata.draw_all_pairs",
               "fit_line", "draw_histogram"],
    ),
    dict(
        title="Hard tricks, and your own program",
        learn=[
            "a second y-axis, a zoom box and a moving chart",
            "a heatmap that sorts itself",
            "a wind rose, a map in its true shape, a 3D view, and words that say what a chart shows",
            "a web page you can point at, and dots counted in hexagons",
            "how to write your own program from start to end",
        ],
        parts=[
            ("A second y-axis shows a column measured in other units on the same chart.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.get_example("weather")', "Get the weather table."),
                ("chart = sdata.chart(weather)", "Start a chart."),
                ('chart.draw_lines(x="month", y="temperature")', "A line of temperature (average of "
                                                            "the three cities)."),
                ('chart.add_second_y("rain", drawn_as="bars", labelled="Rain (mm)")', "Add rain, drawn as "
                                                                               "bars, with its own "
                                                                               "y-axis on the right."),
                ('chart.label_y("Temperature (°C)")', "Name the left y-axis."),
                ('chart.save("lesson8_second_y.png")', "Save it."),
            ]),
            ("A zoom box shows a small part of the chart close up.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_dots(x="hours", y="marks")', "Dots of hours and marks."),
                ("chart.add_zoom_box(x_between=[2, 4], y_between=[40, 60], where=\"top left\")",
                 "Show the part between 2 and 4 hours and between 40 and 60 marks, bigger, in a "
                 "box at the top left."),
                ('chart.save("lesson8_zoom.png")', "Save it."),
            ]),
            ("A heatmap colours a grid of numbers. cluster=True puts rows that are alike next to "
             "each other.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.get_example("weather")', "Get the weather table."),
                ("chart = sdata.chart(weather)", "Start a chart."),
                ('chart.draw_heatmap(x="month", y="city", value="rain", with_numbers=True, cluster=True)',
                 "One square per city and month, coloured by rain, with the number written in. "
                 "cluster=True sorts the rows and columns and draws a tree of how alike they are "
                 "(hierarchical clustering)."),
                ('chart.label_colour_bar("Rain (mm)")', "Name the colour bar."),
                ("chart.set_size(width=12, height=4)", "Make the chart wide and low."),
                ('chart.save("lesson8_heatmap.png")', "Save it."),
            ]),
            ("A wind rose shows how often the wind blows from each direction, and how hard: one bar "
             "for every 30 degrees of the compass, split into bands of wind speed.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.get_example("weather")', "Get the weather table."),
                ("chart = sdata.chart(weather)", "Start a chart."),
                ('chart.draw_wind_rose(direction="wind_direction", speed="wind_speed")',
                 "Count the months for each direction (north at the top) and stack them by wind speed, "
                 "the calmest in the middle."),
                ('chart.save("lesson8_wind_rose.png")', "Save it."),
            ]),
            ("A map should keep its true shape, and a chart can say in words what it shows, for a "
             "caption or for a reader who cannot see it.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('island = sdata.get_example("island")', "Get the island table."),
                ("chart = sdata.chart(island)", "Start a chart."),
                ('chart.draw_contour(x="east", y="north", z="height")', "A map of the heights."),
                ("chart.use_true_shape()", "One km east is as long as one km north, so the island is not "
                                          "stretched."),
                ("chart.put_colour_bar_at_bottom()", "Lay the colour bar under the map."),
                ("chart.say_what_it_shows()", "Print what the chart shows: what is drawn, the axes and the "
                                             "colour bar, read from the chart itself."),
                ('chart.save("lesson8_true_shape.png")', "Save it."),
            ]),
            ("A chart can also be a web page: point at a dot to read its row, zoom with the mouse, click the "
             "legend to hide a group. The numbers are the picture's own: matplotlib draws the chart, and the web "
             "page shows what it drew.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_dots(x="hours", y="marks", colour="class")', "One dot per student, coloured by class."),
                ('chart.show_when_pointing("name", "subject")', "Pointing at a dot shows the student's name and "
                                                                "subject, and nothing else of the row."),
                ('chart.save("lesson8_marks.html")', "The end .html makes a web page; it works with no internet. "
                                                     "Open it in your browser."),
            ]),
            ("When many dots cover each other, count them in hexagons; a rectangle marks the part you write "
             "about.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.get_example("marks")', "Get the marks table."),
                ("chart = sdata.chart(marks)", "Start a chart."),
                ('chart.draw_hexagon_bins(x="hours", y="height", with_bins=8)',
                 "About 8 hexagons across; the darker, the more students."),
                ("chart.draw_rectangle(x_between=[5, 7], y_between=[145, 155], hollow=True)",
                 "An outline round the busiest part."),
                ('chart.use_background_colour("ivory")', "A soft colour behind the hexagons."),
                ('chart.save("lesson8_hexagons.png")', "Save it."),
            ]),
            ("A 3D chart can be turned to look at it from any side.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('island = sdata.get_example("island")', "Get the island table."),
                ("chart = sdata.chart(island)", "Start a chart."),
                ('chart.draw_surface(x="east", y="north", z="height", with_height_lines=True)',
                 "The island as a landscape, with lines of equal height on the floor of the box."),
                ("chart.look_from(height=20, around=45)", "Look from 20 degrees above the ground, after "
                                                         "walking 45 degrees round it."),
                ('chart.save("lesson8_3d.png")', "Save it."),
            ]),
            ("An animation is a chart that moves: one picture for each value of a column.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('growth = sdata.get_example("growth")', "Get the growth table."),
                ("chart = sdata.chart(growth)", "Start a chart."),
                ('chart.draw_bars(x="country", y="population")', "One bar per country."),
                ("chart.set_range_y(0, 50)", "Keep the y-axis still, from 0 to 50."),
                ('chart.animate(over="year")', "Make one picture for each year."),
                ('chart.save("lesson8_growth.gif")', "Save it as a .gif, a moving picture. Open "
                                                     "it in a web browser to watch."),
            ]),
            ("Your own program. Every chart follows the same plan: get the data, look, start, draw, "
             "words, look, save.", [
                ("import simplydata as sdata", "1. Load simplydata."),
                ('island = sdata.get_example("island")', "2. Get the data. For your own file, skip this line "
                                                  'and write chart = sdata.chart("my_file.xlsx") below.'),
                ("print(island)", "3. Look at the data before you draw it."),
                ("chart = sdata.chart(island)", "4. Start a chart."),
                ('chart.draw_contour(x="east", y="north", z="height")', "5. Draw: a map where each "
                                                                   "colour band is one height."),
                ('chart.write_title_on_top("Treasure Island")', "6. Words: a title ..."),
                ('chart.label_x("East (km)")', "... and the axis names ..."),
                ('chart.label_y("North (km)")', ""),
                ('chart.label_colour_bar("Height (m)")', "... and the name of the colour bar."),
                ('chart.write_note("X marks the spot", x=10, y=4, with_arrow=True)', "A note with an arrow."),
                ('chart.use_style("presentation")', "7. Look: big and clear for showing to others."),
                ('chart.save("lesson8_my_program.png")', "8. Save."),
            ]),
        ],
        notes=[
            "Those are all the charts! sdata.show_all_words() lists every word and sdata.help(\"word\") "
            "explains any of them. Lessons 9 to 12 teach tables: how to look at your data, clean "
            "it and sum it up before you draw it.",
            'Your own data: save it from Excel as .xlsx or .csv, then chart = sdata.chart("my_file.xlsx"). '
            "If a column name is spelt wrong, simplydata tells you the right one.",
        ],
        task=[
            "Write your own program, from an empty file, for a question you care about.",
            "Use any example table, or your own. Give it a title, axis names and a note.",
            "Make a second chart of the same table, put the two charts side by side and save the "
            "page as a PDF.",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                fruit = sdata.get_example("fruit")
                print(fruit)
                chart = sdata.chart(fruit)
                chart.draw_bars(x="fruit", y="count", show="total")
                chart.write_numbers_on_bars()
                chart.write_title_on_top("Which fruit sells best?")
                chart.label_x("Fruit")
                chart.label_y("Sold in one week")
                chart.save("lesson8_fruit.png")"""),
             "One possible question: which fruit sells best? Same plan as always: get the data, "
             "look, start, draw, words, save."),
            (_sx("""\
                import simplydata as sdata
                growth = sdata.get_example("growth")
                chart = sdata.chart(growth)
                chart.draw_lines(x="year", y="forest", colour="country")
                chart.write_title_on_top("Forest in four countries")
                chart.label_x("Year")
                chart.label_y("Forest (% of the land)")
                chart.write_note("Applia loses the most", x=2016, y=50, with_arrow=True)
                chart.save("lesson8_forest.png")"""),
             "Another table, with a title, both axis names and a note with an arrow."),
            (_sx("""\
                import simplydata as sdata
                growth = sdata.get_example("growth")
                people = sdata.chart(growth).draw_lines(x="year", y="population", colour="country")
                people.label_y("People (millions)")
                forest = sdata.chart(growth).draw_lines(x="year", y="forest", colour="country")
                forest.label_y("Forest (% of the land)")
                charts = sdata.put_side_by_side(people, forest, with_letters=True)
                charts.save("lesson8_page.pdf")"""),
             "Two charts of one table on one page, saved as a PDF because the name ends in .pdf."),
        ],
        words=["add_second_y", "add_zoom_box", "draw_heatmap", "label_colour_bar", "set_size", "animate",
               "draw_contour", "write_note", "use_style", "sdata.show_all_words", "sdata.help",
               # charts phase, batch 2
               "draw_wind_rose", "use_true_shape", "put_colour_bar_at_bottom", "say_what_it_shows", "draw_surface",
               "look_from",
               # charts phase, batch 3
               "show_when_pointing", "draw_hexagon_bins", "draw_rectangle", "use_background_colour"],
    ),
    dict(
        title="Tables: open one and look at it",
        learn=[
            "how to turn data into a simplydata table",
            "how to look at the first and last rows, and the names of the columns",
            "how to describe every column and count what is in it",
        ],
        parts=[
            ("Before you draw, look at your data. sdata.table gives you plain words for that.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table from the practice marks. For "
                                                          'your own file, write sdata.table("my_file.xlsx").'),
                ("print(table)", "Print the table. The first line says how many rows and columns it "
                                 "has. Then come the first 10 rows."),
                ("table.show_first_rows(5)", "Show only the first 5 rows."),
                ("table.show_last_rows(3)", "Show the last 3 rows."),
                ("print(table.get_column_names())", "Print the names of the columns."),
                ("table.describe_columns()", "Describe every column: is it numbers or text, how many "
                                             "cells are empty, and the smallest, biggest and average "
                                             "number."),
                ("table.count_rows()", "Count the rows, and say the answer in a sentence. One row is "
                                       "one child in one test."),
            ]),
            ("count_each counts how often each different value comes up.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("fruit"))', "Make a table of fruit sold by two shops."),
                ("table.show_first_rows()", "Show the first rows. With nothing in the brackets you "
                                            "get 5."),
                ('table.count_each("fruit")', "For each fruit: in how many rows it comes up. It says "
                                              "the answer in a sentence, and gives back a small table "
                                              "that also has the percent of all the rows."),
                ('table.count_each("shop")', "The same for each shop."),
            ]),
            ("sdata.table can read many files at once. Here we first save two small files, then "
             "read them back together.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.table(sdata.get_example("weather"))', "Make a table of the weather."),
                ("weather.keep_first_rows(12)", "Keep the first 12 rows: one city, a whole year."),
                ('weather.save("lesson9_part1.csv")', "Save them as a CSV file."),
                ("weather.start_again()", "Back to the whole table."),
                ("weather.keep_last_rows(12)", "Keep the last 12 rows: another city."),
                ('weather.save("lesson9_part2.csv")', "Save them as a second file."),
                ('both = sdata.table("lesson9_part*.csv")', "Read every file whose name fits the pattern "
                                                            "(* stands for any text) and stack them. A new "
                                                            'column, "file", says where each row came from.'),
                ('both.count_each("file")', "12 rows from each file."),
                ("both.show(rows=3)", "Show the first 3 rows with every column. both.show() shows the "
                                      "whole table."),
            ]),
        ],
        notes=[
            "Looking never changes the table. Only steps that say what they change (keep_rows_where, "
            "sort_by ...) do, and lesson 10 shows them.",
            "In Jupyter, VS Code or Spyder, write table on the last line of a cell to see it as a "
            "nice table.",
            "sdata.table reads the same files as sdata.chart: .xlsx, .csv, .tsv, .parquet and .json. "
            'For one sheet of an Excel file: sdata.table("results.xlsx", sheet="2026").',
            'Every sheet at once: everything = sdata.table("results.xlsx", sheet="all") gives one table with a '
            '"sheet" column naming the sheet each row came from. Then everything.count_rows(for_each_group_in="sheet") '
            'counts the rows of each sheet, everything.find_average_of("marks", for_each_group_in="sheet") gives a '
            'summary per sheet, and everything.keep_rows_where("sheet", is_equal_to="2026") keeps the rows of one sheet (everything.undo() brings the others back). '
            'sheet="all" works only when the sheets have the same columns; sheets with different data are read by '
            'name, one at a time, and simplydata prints a line to copy for each.',
            'To write such a file, save each table as a sheet: marks_2025.save("results.xlsx", in_sheet="2025"), then '
            'marks_2026.save("results.xlsx", in_sheet="2026") keeps the first sheet and adds the second. sheet= reads '
            'a sheet; in_sheet= saves one.',
            "The row numbers on the left start at 1, the way people count: the last row of a table of 54 "
            "rows is row 54. Lesson 10 uses these numbers to choose rows by their place.",
            'A folder works too: sdata.table("data/") reads every table file in it. A web address '
            'works like a file name: sdata.table("https://example.org/data.csv").',
            'Files written in another way: separator=";", decimal_mark="," (3,5 is three and a half), '
            'thousands_mark=".", empty_values=["NA", "-"], skip_rows=2 and encoding="latin-1".',
            'Give separator= when you know it, especially for a file with one column: '
            'sdata.table("species.csv", separator=","). Without it simplydata guesses (only a comma, semicolon, '
            "tab or bar) and prints its guess, so you can check it.",
        ],
        task=[
            'Make a table of sdata.get_example("weather"). How many rows does it have?',
            "Describe its columns. Which column has the biggest numbers?",
            'Count each "city". Does every city have the same number of rows?',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                table.count_rows()"""),
             "36 rows: 12 months for each of 3 cities."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                table.describe_columns()"""),
             "wind_direction has the biggest numbers (up to 354): it is an angle in degrees, from 0 "
             "to 360."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                table.count_each("city")"""),
             "Yes: Frostby, Rainbridge and Sunnyvale have 12 rows each, one for every month."),
        ],
        words=["sdata.table", "table.show_first_rows", "table.show_last_rows", "table.get_column_names",
               "table.describe_columns", "table.count_rows", "table.count_each", "table.show"],
    ),
    dict(
        title="Tables: choose rows and columns, and undo",
        learn=[
            "how to keep only the columns and rows you want",
            "how to sort the rows",
            "how to take a step back, and start again",
            "how to save your table",
        ],
        parts=[
            ("A table is changed in small steps, like a chart. Each step says what it did.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.keep_columns("name", "subject", "marks")', "Keep only these three columns, "
                                                                   "in this order."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")', "Keep only the rows where the subject "
                                                                 "is Maths. simplydata says how many "
                                                                 "rows it kept."),
                ('table.keep_rows_where("marks", is_above=60)', "Of those, keep only marks above 60."),
                ('table.sort_by("marks", biggest_first=True)', "Put the rows in order, the biggest "
                                                               "mark first."),
                ("table.show_first_rows(10)", "Show the first 10 rows: the best Maths marks."),
                ("table.show_steps()", "List every step you did, in order."),
                ("table.undo()", "Take back the last step (the sorting)."),
                ("table.start_again()", "Go back to the whole table, as it was at the start."),
                ("print(table)", "All 54 rows and 6 columns are back."),
            ]),
            ("keep_rows_where and remove_rows_where know many conditions. Then save what you made.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("weather"))', "Make a table of the weather."),
                ('table.keep_rows_where("month_number", is_between=[6, 8])', "Keep the summer months: 6, 7 and "
                                                                     "8. is_between= keeps both ends."),
                ('table.remove_rows_where("city", is_equal_to="Frostby")', "Remove the rows of the city "
                                                                  "Frostby."),
                ('table.remove_columns("wind_direction", "wind_speed")', "Remove two columns we do "
                                                                         "not need."),
                ('table.rename_column("temperature", to="temp")', 'Give the column "temperature" '
                                                                  'the shorter name "temp".'),
                ("print(table)", "Look at what is left: 6 rows and 5 columns."),
                ('table.save("lesson10_summer.xlsx")', "Save the table as an Excel file. A name "
                                                       "ending in .csv saves a CSV file. in_sheet=\"summer\" "
                                                       "would save it as one sheet and keep the file's other "
                                                       "sheets."),
            ]),
            ("A condition can also be written out, with and, or, not and brackets. And keep_biggest_rows "
             "keeps the top rows of each group.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ("table.keep_rows_where(\"marks > 60 and subject == 'Maths'\")",
                 "Keep the rows where both are true: a mark above 60, in Maths. Text goes in quotes, "
                 "and == means \"is equal to\"."),
                ("table.undo()", "Back to all the rows."),
                ("table.remove_rows_where(\"hours < 3 or class in ['B', 'C']\")",
                 "Remove the rows where at least one is true: under 3 hours of study, or class B or C."),
                ("table.start_again()", "Back to the whole table."),
                ('table.keep_biggest_rows(2, by="marks", for_each_group_in="subject")', "Keep the 2 best marks in "
                                                                              "each subject: 6 rows."),
                ("table.show()", "Show the whole (small) table."),
            ]),
            ("Rows and columns can also be chosen by their place in the table. Positions count from 1, "
             "the numbers table.show() prints, and both ends are included.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ("table.show_last_rows(3)", "The last three rows are numbered 52, 53 and 54: rows count "
                                            "from 1."),
                ("table.keep_rows_by_position(10, to=20)", "Keep rows 10 to 20. Both ends are included, so "
                                                           "that is 11 rows."),
                ("table.keep_rows_by_position(1, step=2)", "Of those, keep every 2nd row: the 1st, 3rd, 5th "
                                                           "... 6 rows."),
                ("table.keep_columns_by_position(1, to=3)", "Keep the first three columns. It says which "
                                                            "columns they were."),
                ("table.show()", "6 rows and 3 columns, numbered again from 1."),
                ("table.start_again()", "Back to the whole table."),
                ('print(table.get_cell_at(row=3, column="marks"))', "One cell: the mark in row 3. get_cell_at only "
                                                                "looks; the table does not change."),
                ("table.reverse_rows()", "Turn the table upside down: the last row comes first."),
                ("table.show_first_rows(3)", "Rosa's marks are on top now."),
            ]),
        ],
        notes=[
            "Conditions for keep_rows_where and remove_rows_where: is_above, is_below, is_at_least, is_at_most, "
            "is_equal_to, is_not_equal_to, is_between, is_one_of, contains, starts_with, ends_with and is_empty.",
            'is_one_of= takes a list: table.keep_rows_where("subject", is_one_of=["Maths", "Science"]).',
            "undo() takes back one step at a time. start_again() is a step too, so undo() can take "
            "it back.",
            "Your file is never changed: only table.save(...) writes a file.",
            "Written conditions use == != < <= > >=, and, or, not, brackets, in [...] and is empty. "
            "An empty cell never meets a condition, and not does not change that: \"not (marks > 50)\" "
            "leaves out empty marks too. To find them, write \"marks is empty\". A note says how many "
            "rows had an empty cell.",
            'Dates go in quotes as year-month-day: table.keep_rows_where("date > \'2026-03-01\'"), or '
            'table.keep_rows_where("date", is_after="2026-03-01").',
            "keep_rows_where chooses rows by their values, keep_rows_by_position by their place. Positions count "
            "from 1 and both ends are included, so rows 10 to 20 are 11 rows. to=\"last\" goes to the end, "
            "and a list such as [1, 5, 9] keeps those rows in that order.",
            "Coming from pandas or NumPy, which count from 0 and leave out the end: df.iloc[9:20] is "
            "table.keep_rows_by_position(10, to=20), df.iloc[::2] is keep_rows_by_position(1, step=2), "
            "df.iloc[[0, 4]] is keep_rows_by_position([1, 5]), df.iloc[:, 0:3] is "
            "keep_columns_by_position(1, to=3), df.loc[:, \"hours\":\"height\"] is "
            "keep_columns(\"hours\", to=\"height\"), df.select_dtypes(\"number\") is "
            "keep_columns(of_kind=\"number\"), df.at[2, \"marks\"] is get_cell_at(row=3, column=\"marks\") and "
            "df.iloc[::-1] is reverse_rows(). For numbers, a[2:8] is nums.keep_numbers_by_position(3, to=8), "
            "and for a grid, g[1:5, 0:3] is grid.keep_rows_by_position(2, to=5).keep_columns_by_position(1, to=3).",
        ],
        task=[
            'In the marks table, keep only class "B" and sort by "hours". Who studied the longest?',
            "Undo the sorting, then sort by name instead.",
            'Keep 5 random rows with table.keep_random_rows(5, with_seed=1) and save them as "five.csv".',
            "With one written condition, keep the rows with marks below 50 or hours above 8. How many "
            "rows are there?",
            "From memory, without looking back: start again, keep rows 5 to 9, then remove the last row. "
            "How many rows are left, and whose name is in row 1 now?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_rows_where("class", is_equal_to="B")
                table.sort_by("hours", biggest_first=True)
                table.show_first_rows(3)"""),
             "Jade studied the longest: 9.4 hours, for Maths. biggest_first=True puts the longest on top."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_rows_where("class", is_equal_to="B")
                table.sort_by("hours", biggest_first=True)
                table.undo()
                table.sort_by("name")
                table.show_first_rows()"""),
             "undo() takes back only the sorting; class B stays. Text is sorted from A to Z."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_random_rows(5, with_seed=1)
                print(table)
                table.save("five.csv")"""),
             "with_seed=1 picks the same 5 rows every time, so someone else can repeat it."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_rows_where("marks < 50 or hours > 8")
                table.count_rows()"""),
             "19 rows: or keeps a row when at least one of the two is true."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_rows_by_position(5, to=9)
                table.remove_rows_by_position("last")
                table.count_rows()
                print(table.get_cell_at(row=1, column="name"))"""),
             "4 rows: rows 5 to 9 are 5 rows (both ends count), and one is removed. Row 1 is now Ben's "
             "Science mark, which was row 5 before: positions are always of the table as it is now."),
        ],
        words=["table.keep_columns", "table.keep_rows_where", "table.sort_by", "table.show_steps", "table.undo",
               "table.start_again", "table.remove_rows_where", "table.remove_columns", "table.rename_column",
               "table.save", "table.keep_random_rows", "table.keep_biggest_rows",
               "table.keep_rows_by_position", "table.remove_rows_by_position", "table.keep_columns_by_position",
               "table.get_cell_at", "table.reverse_rows"],
    ),
    dict(
        title="Tables: clean the data and add new columns",
        learn=[
            "how to find and fill empty cells",
            "how to fix columns: numbers written as text, extra spaces, wrong values",
            "how to add new columns, in plain words or like a sum in maths",
            "what long and wide tables are",
        ],
        parts=[
            ("Real data often has empty cells. The practice tables have none, so we make some first.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.replace_values_in("marks", [61, 73], with_value=None)', "Make every mark of 61 "
                                                                             "or 73 empty. "
                                                                             "with_value=None means "
                                                                             "an empty cell."),
                ("table.count_empty_cells_in()", "Show how many empty cells each column has."),
                ('table.fill_empty_cells_in("marks", with_the="average")', "Fill the empty marks with the "
                                                                        "average of the other marks."),
                ("table.undo()", "Changed your mind? Take it back: the cells are empty again."),
                ('table.remove_rows_with_empty_cells_in("marks")', "This time remove the rows with an "
                                                                "empty cell in marks."),
                ("print(table)", "Some rows fewer than at the start."),
            ]),
            ("Data typed by people is often untidy. These words fix whole columns at once.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table({"name": ["  Asha", "ben ", "Chen"], "height": ["144", "152", "unknown"]})',
                 "Make a small table by hand: each column name, then its values in a list."),
                ('table.remove_extra_spaces_in("name")', "Take away the spaces before and after the names."),
                ('table.replace_values_in("name", "ben", with_value="Ben")', 'Write "ben" with a capital '
                                                                          "letter."),
                ('table.turn_into_numbers("height")', "Turn the heights from text into numbers. "
                                                 '"unknown" is not a number, so that cell becomes '
                                                 "empty, and simplydata tells you."),
                ("table.describe_columns()", "Now height is a column of numbers."),
            ]),
            ("A new column can be worked out from other columns, in plain words.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.add_column("marks_per_hour", by_dividing=["marks", "hours"])',
                 'A new column called "marks_per_hour": the marks divided by the hours.'),
                ('table.add_group_column("grade", from_column="marks", cut_at=[40, 60, 80], '
                 'names=["D", "C", "B", "A"])',
                 "A grade for each mark: below 40 is D, 40 to 59 is C, 60 to 79 is B, 80 and more is A."),
                ("table.show_first_rows()", "Look at the two new columns on the right."),
                ('table.count_each("grade")', "How many of each grade?"),
            ]),
            ("Or write the new column like a sum in maths. Here each subject first gets its own "
             "column: the table goes from long to wide.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.keep_columns("name", "class", "subject", "marks")', "Keep the columns we need."),
                ('table.spread_into_columns(names_from="subject", values_from="marks")',
                 "Make one column for each subject: Maths, Science and English. Each child now has "
                 "one row."),
                ('table.add_column("total", "Maths + Science + English")', 'A new column "total": '
                                                                           "the three marks added up."),
                ('table.add_column("average", "total / 3")', "The average of the three marks."),
                ('table.add_rank_column("place", from_column="total")', "Each child's place: 1 for "
                                                                        "the biggest total."),
                ('table.sort_by("place")', "Put the rows in order of place."),
                ("table.show_first_rows()", "Who came first?"),
            ]),
            ("The shop table has real dates and some empty cells: days when the till broke. Look "
             "where they are, then fill them.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("shop"))', "Daily sales of two shops, January to "
                                                             "March 2026."),
                ("table.count_empty_cells_in()", "10 empty sales and 5 empty customer counts."),
                ("look = table.start_chart()", "A chart of the table, to see where the empty cells are."),
                ("look.draw_map_of_empty_cells()", "One strip per column and one line per row: empty cells are "
                                       "coloured, and each column says how many it has."),
                ('look.save("lesson11_empty_cells.png")', "Save it."),
                ('table.add_is_empty_column("sales_was_empty", from_column="sales")',
                 "Before filling: a True/False column that remembers which sales were empty."),
                ('table.fill_empty_cells_in("sales", with_the="line between neighbours", sorted_by="date", '
                 'for_each_group_in="shop")',
                 "Fill each gap on the straight line between the day before and the day after, in date "
                 "order, for each shop on its own. A gap at the very start or end has a neighbour on one "
                 "side only, so it stays empty, and a note says so."),
                ('table.add_column_with_part_of_date("weekday", from_column="date", part="weekday name")',
                 "A new column with the weekday of each date."),
                ('table.add_rolling_column("sales_7_days", from_column="sales", window=7, for_each_group_in="shop", '
                 'sorted_by="date")',
                 "The average of each day and the 6 days before it: a 7-day moving average, which "
                 "smooths out the busy weekends."),
                ("table.show(rows=8)", "Look at the first 8 rows."),
            ]),
            ("Names and dates typed in by people often need taking apart.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table({"name": ["Asha Rao", "Ben Lee", "Chen Wu"], '
                 '"born": ["04/30/2014", "12/25/2013", "07/03/2014"], "height": [144.37, 152.81, 139.5]})',
                 "A small table typed by hand. The birthdays are written month first, as in the USA."),
                ('table.split_column("name", separator=" ", into=["first_name", "family_name"])',
                 "Split each name at the space into two new columns."),
                ('table.add_column_with_part_of_text("initial", from_column="first_name", first_characters=1)',
                 "The first letter of each first name."),
                ('table.replace_text_in("family_name", "Lee", with_value="Li")', "Replace a piece of text "
                                                                              "inside the cells."),
                ('table.turn_into_dates("born", order="month day year")',
                 "Turn the birthdays into dates. order= says how they are written, so 07/03/2014 is read "
                 "as 3 July and not as 7 March."),
                ('table.add_column_with_part_of_date("month_born", from_column="born", part="month name")',
                 "The month of each birthday, as a word."),
                ('table.change_column("height", "height / 100")', "Change the heights from centimetres "
                                                                  "to metres, in the same column."),
                ('table.round_numbers_in("height", 2)', "Round them to 2 decimal places."),
                ("table.show()", "Look at the whole table."),
            ]),
        ],
        notes=[
            "Formulas know more maths than + - * /: sqrt, log, exp, sin, cos, tan, pi, and special "
            'functions such as erf, gamma, lgamma, beta and besselJ: table.add_column("z", '
            'formula="erf(marks / 100)").',
            "Long or wide? A long table has one row for each measurement: the marks table has a row "
            "for each child in each subject. A wide table puts the measurements of one child side "
            "by side, one column per subject. Charts and tests like long tables (also called tidy "
            "data); sums across columns, like the total above, need wide ones.",
            "Filling empty cells is called imputation. Filling with the average makes the values "
            "look less spread out than they really are, so say in your report how you filled them. "
            'with_the="median", "value above" or "value below" and with_value=0 work too.',
            "remove_rows_with_empty_cells_in() with nothing in the brackets removes every row that has "
            "an empty cell in any column.",
            "More fixing words: turn_into_text, turn_into_dates, turn_into_lowercase and turn_into_uppercase.",
            "Plain words for new columns: by_adding=, by_subtracting=, by_multiplying= and "
            "by_dividing=, or from_column= with plus=, minus=, times= or divide_by=.",
            'In a maths-style column, a column name with spaces goes in backticks: "`max temp` - 2".',
            'with_the="line between neighbours" is linear interpolation. It suits values that change '
            "smoothly, like sales from day to day; it cannot know about a sudden jump. Keep a True/False "
            "column of what you filled, and say in your report how you filled it.",
            "Charts say it too: when a chart leaves out rows because of empty cells, one line tells you "
            "how many.",
            "Row after row: add_previous_value_column gives the value of the row before, and "
            "add_change_column the change since then (in_percent=True for a percent).",
        ],
        task=[
            "In the first example, fill the empty marks with the median instead of the average.",
            'Add a column "height_m" with the height in metres: from_column="height", divide_by=100.',
            'In the last example, add a column "best_two" with the formula "total - English".',
            'In the shop example, add a column "change" with the change in sales from the day before, '
            'for_each_group_in="shop" and sorted_by="date" (add_change_column).',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.replace_values_in("marks", [61, 73], with_value=None)
                table.count_empty_cells_in()
                table.fill_empty_cells_in("marks", with_the="median")
                table.count_empty_cells_in()"""),
             'with_the="median" fills each empty mark with the middle mark of the others; afterwards '
             "no cell is empty."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.add_column("height_m", from_column="height", divide_by=100)
                table.show_first_rows()"""),
             "The height in centimetres divided by 100: 144 becomes 1.44."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_columns("name", "class", "subject", "marks")
                table.spread_into_columns(names_from="subject", values_from="marks")
                table.add_column("total", "Maths + Science + English")
                table.add_column("best_two", "total - English")
                table.show_first_rows()"""),
             "The formula can use a column made earlier (total); best_two is Maths + Science."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("shop"))
                table.fill_empty_cells_in("sales", with_the="line between neighbours", sorted_by="date", for_each_group_in="shop")
                table.add_change_column("change", from_column="sales", for_each_group_in="shop", sorted_by="date")
                table.show(rows=5)"""),
             "Each change is today's sales minus yesterday's, in the same shop; the first day of each "
             "shop has nothing before it, so its change is empty."),
        ],
        words=["table.replace_values_in", "table.count_empty_cells_in", "table.fill_empty_cells_in",
               "table.remove_rows_with_empty_cells_in",
               "table.remove_extra_spaces_in", "table.turn_into_numbers", "table.add_column",
               "table.add_group_column", "table.add_rank_column", "table.spread_into_columns",
               "table.add_is_empty_column", "draw_map_of_empty_cells", "table.add_column_with_part_of_date",
               "table.add_rolling_column", "table.split_column", "table.add_column_with_part_of_text",
               "table.replace_text_in", "table.turn_into_dates", "table.change_column", "table.round_numbers_in",
               "table.add_change_column"],
    ),
    dict(
        title="Tables: summaries, and from a table to a chart",
        learn=[
            "how to work out averages, totals and counts, for each group",
            "how to tell if two columns go together, and why that is not the same as a cause",
            "how to draw a table, and which rows a chart uses",
            "how to join two tables and turn columns into rows",
        ],
        parts=[
            ("A summary turns many rows into a few numbers. It never changes your table, and it "
             "says its answer in a sentence.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.find_average_of("marks")', "The average of all the marks: just one number."),
                ('table.find_average_of("marks", for_each_group_in="class")', "One average for each class. for_each_group_in= "
                                                                "also gives back a new, small table."),
                ('table.find_biggest_of("marks", for_each_group_in="subject")', "The best mark in each subject."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")',
                 "Keep the maths marks: one row per child. Each child is in the table three times, and a "
                 "correlation over all 54 rows would count each child three times."),
                ('table.find_correlation_between("hours", "marks")', "Do more hours go with more marks? "
                                                                "The answer is a number r from -1 "
                                                                "to 1 (Pearson's correlation), "
                                                                "explained in words."),
            ]),
            ("A summary for each group is a table too, so you can sort it and draw it.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("fruit"))', "Make a table of fruit sales."),
                ('totals = table.find_total_of("count", for_each_group_in="fruit")', "A new table called totals: one "
                                                                       "row per fruit, with a column "
                                                                       '"total of count". table itself '
                                                                       "does not change."),
                ('totals.sort_by("total of count", biggest_first=True)', "Best seller first."),
                ("chart = totals.start_chart()", "Start a chart from the summary table."),
                ('chart.draw_bars(x="fruit", y="total of count")', "One bar per fruit."),
                ("chart.write_numbers_on_bars()", "Write the total on each bar."),
                ('chart.save("lesson12_fruit.png")', "Save the chart."),
            ]),
            ("A chart uses the table as it was when you made the chart. Table steps after it are "
             "for the next chart.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.keep_rows_where("class", is_equal_to="A")', "Keep class A."),
                ("all_tests = table.start_chart()", "A chart of the table as it is now: every test of "
                                              "class A. sdata.chart(table) does the same."),
                ('all_tests.draw_dots(x="hours", y="marks")', "Draw hours against marks."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")', "A table step after the chart. The "
                                                                 "chart all_tests does not change."),
                ("maths = table.start_chart()", "A second chart, of the table as it is now: only the Maths "
                                          "tests of class A."),
                ('maths.draw_dots(x="hours", y="marks")', "Draw the same thing again."),
                ("charts = sdata.put_side_by_side(all_tests, maths, same_y=True)", "Both charts on one page, "
                                                                          "with the same y-axis, so "
                                                                          "you can compare them."),
                ('charts.save("lesson12_maths.png")', "Save the page."),
            ]),
            ("Two tables can be joined: their rows are matched on a column they share.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('ages = {"name": ["Asha", "Ben", "Chen"], "age": [12, 13, 12]}', "A small table of "
                                                                                  "ages, typed by hand: "
                                                                                  "each column name, "
                                                                                  "then its values."),
                ('table.join_with(ages, using="name")', "Bring in the age, matching the rows on the "
                                                        "name. Only children found in both tables stay."),
                ("table.show_first_rows()", "Look: there is a new column, age."),
                ('table.find_average_of("marks", for_each_group_in="age")', "The average mark at each age."),
            ]),
            ("Turning columns into rows makes a wide table long: the shape most charts like.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table({"name": ["Asha", "Ben", "Chen"], "test_1": [61, 73, 81], '
                 '"test_2": [70, 68, 90]})', "A small, wide table: two tests, one column for each."),
                ('table.gather_into_rows(["test_1", "test_2"], names_to="test", values_to="mark")',
                 'Put the two tests under each other. The new column "test" says which test, and '
                 '"mark" holds the mark. Each child now has two rows.'),
                ("table.show_first_rows(6)", "Look at the new, long shape."),
                ("chart = table.start_chart()", "Start a chart from it."),
                ('chart.draw_bars(x="name", y="mark", colour="test")', "Both tests side by side for each "
                                                                  "child."),
                ('chart.save("lesson12_tests.png")', "Save it."),
            ]),
            ("find_summary_of gives several measures at once, and every= sums up dates by week, month or "
             "year.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("shop"))', "Daily sales of two shops."),
                ('table.find_summary_of("sales", for_each_group_in="shop", show=["average", "median", "standard deviation", '
                 '"count", "empty cells"])',
                 "Five measures of each shop's sales in one tidy table. count counts the days with a "
                 "number; empty cells counts the others."),
                ('table.find_total_of("sales", for_each_group_in="date", every="month")', "The total sales of each "
                                                                            "month: every= puts the days "
                                                                            "of one month together."),
                ('table.find_percent_of_rows_where("sales", is_above=500, for_each_group_in="shop")',
                 "On what percent of the days did each shop take more than 500? Each percent comes with "
                 "its 95 % confidence interval."),
            ]),
            ("A cross table puts one group down the side and another across the top. A correlation "
             "table compares many columns at once.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('fruit = sdata.table(sdata.get_example("fruit"))', "A table of fruit sales."),
                ('fruit.count_rows(for_each_group_in="shop", across="fruit")', "How many sales of each fruit in "
                                                                      "each shop: one row per shop, one "
                                                                      "column per fruit."),
                ('fruit.count_different_values_in("fruit", for_each_group_in="shop")', "How many different fruits "
                                                                           "each shop sold."),
                ('marks = sdata.table(sdata.get_example("marks"))', "A table of the marks."),
                ('marks.find_average_of("marks", for_each_group_in="class", across="subject")', "The average mark of "
                                                                                  "each class in each "
                                                                                  "subject."),
                ('marks.keep_rows_where("subject", is_equal_to="Maths")',
                 "One row per child (a child's height is the same in all three of its rows)."),
                ('marks.find_correlation_between("hours", "marks", "height")', "Every pair of the three "
                                                                         "columns at once: a "
                                                                         "correlation table, with the "
                                                                         "strongest pairs in words."),
            ]),
            ("More ways to sum up: percentiles, the most common value, and measures of shape.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('marks = sdata.table(sdata.get_example("marks"))', "A table of the marks."),
                ('marks.find_percentile_of("marks", 90, for_each_group_in="class")', "The 90th percentile: 90 % of the "
                                                                      "marks are below it (86.3 in class A)."),
                ('marks.find_summary_of("marks", show=["median", "skewness", "coefficient of variation"], '
                 'for_each_group_in="class")',
                 "Skewness says if the values lean to one side (below 0: a longer tail of low marks); "
                 "the coefficient of variation is the standard deviation divided by the average."),
                ('school = sdata.table(sdata.get_example("school"))', "A table of pupils."),
                ('school.find_most_common_of("days_absent")', "The most common number of days absent (the mode): 2."),
            ]),
            ("A z-score puts marks from different subjects on one scale: how many standard deviations a "
             "value lies above or below the average of its group.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "A table of the marks."),
                ('table.add_z_score_column("marks_z", from_column="marks", for_each_group_in="subject")',
                 'A new column "marks_z": 0 is the average of that subject, 1 one standard deviation above it '
                 "(SciPy zscore, as R scale())."),
                ("table.show_first_rows(3)", "Asha's 77 in English is 1.09 standard deviations above the "
                                             "English average; her 66 in Science is a little below the "
                                             "Science average (-0.25)."),
            ]),
        ],
        notes=[
            "Correlation is not cause. Children who study more might also sleep more, or like the "
            "subject more; r only says that two columns go up and down together, not which one "
            "makes the other change.",
            'find_correlation_between("hours", "marks", show="result table") gives back r, its 95 % interval, '
            "the p-value and the rows as a one-row table, ready to save for a report.",
            'A table of counts (one row per group, with a column "count")? table.repeat_each_row_by("count") '
            "makes it one row per thing counted, as most words need.",
            "More summaries: find_median_of, find_total_of, find_smallest_of, find_biggest_of, find_standard_deviation_of "
            "and count_rows. Each one can take for_each_group_in=.",
            "A chart never changes its table, and a table step never changes a chart you already "
            "made. So one cleaned table can feed many charts.",
            "table.add_rows_from(other) puts the rows of another table under this one. "
            "spread_into_columns does the opposite of gather_into_rows.",
            "Lesson 13 teaches numbers, and lesson 14 the statistical tests: is a difference "
            "real, and how big is it?",
            "Every summary skips empty cells and says how many it skipped. find_summary_of can also show "
            '"variance", "standard error", "confidence interval", "range" and "interquartile range".',
            'More: find_percentile_of("price", 90, weights="count") and find_median_of(..., weights="count") count '
            'each row as often as its weight (weight_kind="analytic" for sampling weights); '
            'find_correlation_between("hours", "marks", "height", show="covariance") gives the covariances, the '
            "correlations with units.",
        ],
        task=[
            'Make the fruit totals for_each_group_in="shop" instead. Which shop sold more?',
            'Work out the average temperature for_each_group_in="city" in the weather table and draw it as bars.',
            "Is there a link between height and marks? Use find_correlation_between to find out.",
            'Make a cross table of the average mark for_each_group_in="subject" across="class". Which class is '
            "best in Science?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("fruit"))
                totals = table.find_total_of("count", for_each_group_in="shop")
                print(totals)"""),
             "The Market stall sold more: 457 pieces of fruit, against 354 at the Corner shop."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                averages = table.find_average_of("temperature", for_each_group_in="city")
                chart = averages.start_chart()
                chart.draw_bars(x="city", y="average of temperature")
                chart.write_numbers_on_bars(with_decimals=1)
                chart.save("lesson12_temperature.png")"""),
             "Frostby 1.0, Rainbridge 10.1 and Sunnyvale 17.0 degrees. The summary table's column is "
             'called "average of temperature".'),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.find_correlation_between("height", "marks")"""),
             "No: r = 0.03, very close to 0. Even with truly no link, a link this strong would turn up in "
             "about 83 of 100 studies (p = 0.83)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.find_average_of("marks", for_each_group_in="subject", across="class")"""),
             "Class A, with an average of 79.2 in Science, against 67.5 for B and 62.3 for C."),
        ],
        words=["table.find_average_of", "table.find_biggest_of", "table.find_correlation_between", "table.find_total_of",
               "table.start_chart", "sdata.put_side_by_side", "table.join_with", "table.gather_into_rows",
               "table.add_rows_from", "table.find_summary_of", "table.find_percent_of_rows_where", "table.count_rows",
               "table.count_different_values_in", "table.find_percentile_of", "table.find_most_common_of"],
    ),
    dict(
        title="Numbers: lists and grids of numbers",
        learn=[
            "how to make a list of numbers, and a grid of them",
            "two ways to do maths: symbols make new numbers, words change the numbers you have",
            "how to keep some numbers, sum them up, and draw them",
        ],
        parts=[
            ("Numbers are for when you have just numbers, not a table with named columns.", [
                ("import simplydata as sdata", "Load simplydata."),
                ("nums = sdata.numbers([12, 15, 9, 20, 14])", "Make a list of five numbers and call it nums."),
                ("print(nums)", "Look at them. The first line says how many there are."),
                ("bigger = nums * 2", "Maths with symbols makes NEW numbers: every number times 2. "
                                      "nums itself does not change."),
                ("print(bigger)", "24, 30, 18, 40 and 28."),
                ("nums.add(1)", "Maths with words CHANGES the numbers you have: add 1 to each one."),
                ("nums.undo()", "Like a table, numbers can take back every word."),
                ("nums.keep_each_number_that(is_above=10)", "Keep only the numbers above 10. The same conditions "
                                                "as keep_rows_where: is_above, is_below, is_between ..."),
                ("nums.find_average()", "The average of what is left, said in a sentence."),
                ("nums.find_standard_deviation()", "How spread out they are (divide by n - 1, as in pandas "
                                              "and R)."),
                ("nums.show_steps()", "List the steps you did."),
            ]),
            ("Counting, random numbers and a chart.", [
                ("import simplydata as sdata", "Load simplydata."),
                ("months = sdata.numbers(1, to=12)", "Count from 1 to 12. The end is included."),
                ("temps = sdata.numbers([4, 6, 9, 13, 17, 20, 22, 21, 17, 12, 8, 5])", "A temperature for "
                                                                                    "each month."),
                ("chart = sdata.chart()", "Start an empty chart: the numbers go straight into the chart "
                                       "type."),
                ("chart.draw_lines(x=months, y=temps, with_dots=True)", "Draw the temperatures as a line, month by "
                                                              "month."),
                ('chart.save("lesson13_line.png")', "Save it."),
                ("heights = sdata.make_random_numbers(how_many=200, average=150, standard_deviation=8, with_seed=1)",
                 "200 made-up heights that bunch around 150 in a bell shape (a normal distribution). "
                 "with_seed=1 gives the same numbers every time, so others can repeat your work."),
                ("heights.find_median()", "The middle height."),
                ("heights.find_percentile(90)", "The height that 90 % of them are below."),
                ("chart = heights.start_chart()", "Start a chart from the numbers. Their column is called "
                                            "value."),
                ('chart.draw_histogram(x="value", with_bins=12)', "Count how many heights fall in each range."),
                ('chart.save("lesson13_heights.png")', "Save it. Can you see the bell shape?"),
            ]),
            ("A grid holds numbers in rows and columns. Positions count from 1.", [
                ("import simplydata as sdata", "Load simplydata."),
                ("grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])", "A grid with 2 rows and 3 columns: one "
                                                                  "list for each row."),
                ("print(grid.get_number_at(row=1, column=2))", "The number in row 1, column 2: 5."),
                ('grid.find_total(in_each="row")', "The total of each row: 10 and 18."),
                ('grid.find_average(in_each="column")', "The average of each column."),
                ("grid.swap_rows_and_columns()", "Rows become columns (in maths: the transpose)."),
                ("print(grid)", "Now 3 rows and 2 columns."),
                ("chart = grid.start_chart()", "Start a chart from the grid."),
                ("chart.draw_heatmap(with_numbers=True)", "One coloured square for each number, with the number "
                                                "written in."),
                ('chart.save("lesson13_grid.png")', "Save it."),
            ]),
            ("Yes or no values, rounding and where the biggest is.", [
                ("import simplydata as sdata", "Load simplydata."),
                ("temps = sdata.numbers([4.6, 6.2, 9.8, 13.1, 17.5, 20.4])", "Six temperatures."),
                ("warm = temps.turn_into_yes_or_no(is_above=10)", "A yes or no value for each one: yes where it is "
                                                                   "above 10. temps does not change."),
                ("print(warm)", "No, no, no, yes, yes, yes."),
                ("temps.count_numbers_that(is_above=10)", "How many are above 10: 3."),
                ("temps.check_if_all_numbers(is_above=0)", "Yes: all six are above 0. It also gives back True."),
                ("print(temps.find_where_biggest())", "The biggest is at position 6, counting from 1 (NumPy, "
                                                      "which counts from 0, says index 5)."),
                ("temps.round_down()", "Every temperature rounded down to a whole number: 4, 6, 9 ..."),
            ]),
            ("A block has more than two directions: a plate read every hour for a day.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('plate = sdata.number_block(of_shape=(24, 8, 12), filled_with=0.5, directions_named=["hour", "row", '
                 '"column"])', "24 hours x 8 rows x 12 columns, all 0.5 for now. Each direction has a name."),
                ("plate.find_shape()", "The shape in words and as NumPy says it: (24, 8, 12)."),
                ('blank = sdata.number_block(of_shape=(8, 12), filled_with=0.05, directions_named=["row", "column"])',
                 "A blank reading for each well: 8 rows x 12 columns."),
                ("plate.show_how_it_lines_up_with(blank)", "See how they line up before combining them: the blank "
                                                           "is used again for each of the 24 hours."),
                ("plate.subtract(blank)", "Take the blank away from every hour (NumPy calls this broadcasting)."),
                ('wells = plate.find_average(over="hour")', "One average per well: the hours go, 8 rows x 12 "
                                                             "columns remain."),
                ('plate.change_shape_to(one_row_per="hour")', "One row per hour, 96 numbers in each: the shape "
                                                               "scikit-learn wants."),
                ("table = wells.turn_into_table()", "A block as a long table: one column per direction and a "
                                                     "column value."),
                ("chart = wells.start_chart()", "Two directions make a grid, so it can be drawn."),
                ('chart.draw_heatmap()', "One square for each well."),
                ('chart.save("lesson13_wells.png")', "Save it."),
            ]),
            ("Sea temperatures by month: a block with dates, saved and read as a netCDF file.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('dates = sdata.make_run_of_dates("2010-01", how_many=36, every="month")', "36 months, one date each."),
                ("temps = sdata.make_random_numbers(of_shape=(36, 4, 5), average=12, standard_deviation=2, "
                 "with_seed=1)", "Made-up sea temperatures: 36 months x 4 latitudes x 5 longitudes."),
                ('sst = sdata.number_block(temps, directions_named=["time", "latitude", "longitude"], '
                 'with_labels={"time": dates, "latitude": [62, 61, 60, 59], "longitude": [1, 2, 3, 4, 5]})',
                 "Name the directions and give them labels: dates, and degrees north and east."),
                ('sst.save("lesson13_sst.nc")', "Save it as a netCDF file, the usual file of ocean and climate "
                                               "grids."),
                ('sdata.show_whats_inside("lesson13_sst.nc")', "See what the file holds, without reading the numbers."),
                ('sst = sdata.number_block("lesson13_sst.nc", values="values")', "Read it back: one block for one "
                                                                                 "variable of the file."),
                ('usual = sst.find_average(in_each="month")', "12 maps: the usual temperature of each month, all "
                                                              "years together."),
                ("station = sst.get_numbers_nearest_to(latitude=60.4, longitude=2.2)", "The 36 months at the grid "
                                                                                      "cell nearest a station."),
                ('sst.turn_into_change_from_average(in_each="month")', "Each value minus the usual value of its "
                                                                       "month: the anomalies."),
                ("again = station.get_all_numbers().make_random_picks(how_many=36, with_seed=1)",
                 "36 random picks from the station's months, each put back: a bootstrap sample."),
            ]),
            ("More with a grid: numbers at pairs of places, patches of high values, and a finer grid.", [
                ("import simplydata as sdata", "Load simplydata."),
                ("grid = sdata.number_grid([[1, 8, 9, 2], [0, 7, 1, 1], [6, 0, 0, 9]])",
                 "A grid of 3 rows and 4 columns, like readings on a small map."),
                ("grid.get_numbers_at_pairs(rows=[1, 2, 3], columns=[2, 2, 4])",
                 "Three numbers, one at each pair of a row and a column: (1, 2), (2, 2) and (3, 4) give 8, 7 and "
                 "9. Not the rectangle of those rows and columns: the sentence says which words give that."),
                ("grid.find_each_patch_that(is_above=5)",
                 "The cells above 5 that touch by a side form patches: 3 patches here. The table gives the cells, "
                 "total, average and centre of each (SciPy ndimage.label underneath)."),
                ("grid.change_size_to(rows=6, columns=8)",
                 "Twice as many rows and columns, filled in with straight lines between neighbouring cells "
                 "(SciPy ndimage.zoom)."),
            ]),
        ],
        notes=[
            "The words follow the table words, with numbers in place of rows: keep_first_numbers, "
            "remove_empty_numbers, fill_empty_numbers, show_first_numbers.",
            "Summaries have no _of, because there is no column to name: nums.find_average(), not "
            'table.find_average_of("marks").',
            "A sum with no answer, such as dividing by 0 or the square root of a negative number, "
            "gives an empty value and a note, never a crash.",
            "nums.turn_into_table() turns numbers into a table, and nums.as_numpy() gives a plain NumPy array "
            "if another Python tool needs one.",
        ],
        task=[
            "Make the numbers 1 to 10, then square them in two ways: with ** 2 and with raise_to_power(2).",
            "Make 6 dice throws with sdata.make_random_numbers(how_many=6, between=[1, 6], whole_numbers=True, "
            "with_seed=1). What is their total?",
            "Make a grid of 3 rows and 4 columns filled with 0: sdata.number_grid(rows=3, columns=4, "
            "filled_with=0).",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                nums = sdata.numbers(1, to=10)
                squares = nums ** 2
                print(squares)
                nums.raise_to_power(2)
                nums.show()"""),
             "Both give 1, 4, 9 ... 100. ** 2 makes new numbers and leaves nums alone; raise_to_power(2) "
             "changes nums itself (and undo() can take it back)."),
            (_sx("""\
                import simplydata as sdata
                dice = sdata.make_random_numbers(how_many=6, between=[1, 6], whole_numbers=True, with_seed=1)
                dice.show()
                dice.find_total()"""),
             "With with_seed=1 the throws are 3, 4, 5, 6, 1 and 1, which add up to 20."),
            (_sx("""\
                import simplydata as sdata
                grid = sdata.number_grid(rows=3, columns=4, filled_with=0)
                print(grid)"""),
             "Three rows of four zeros: a grid to fill in later."),
        ],
        words=["sdata.numbers", "sdata.make_random_numbers", "sdata.number_grid", "nums.add", "nums.undo",
               "nums.keep_each_number_that", "nums.find_average", "nums.find_standard_deviation", "nums.find_median",
               "nums.find_percentile", "nums.start_chart", "grid.get_number_at", "grid.swap_rows_and_columns", "nums.show_steps", "nums.turn_into_yes_or_no", "nums.count_numbers_that", "nums.round_down", "sdata.number_block", "block.change_shape_to", "block.show_how_it_lines_up_with", "sdata.show_whats_inside", "block.save", "block.get_numbers_nearest_to", "block.turn_into_change_from_average", "nums.make_random_picks",
               "grid.get_numbers_at_pairs", "grid.find_each_patch_that", "grid.change_size_to"],
    ),
    dict(
        title="Statistical tests: real difference, or chance?",
        learn=[
            "how big a difference is, and how sure the data are: the effect and its interval first",
            "what a p-value means: first by shuffling the labels, then from the usual formula",
            "how to compare the averages of groups, and which groups differ",
            "how to compare counts and measurements of the same people, and how to fit a line or a formula",
        ],
        parts=[
            ("Start with the question \"how big?\": the difference between two groups, and how sure the "
             "data are about it.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('school = sdata.table(sdata.get_example("school"))', "A table of pupils."),
                ('school.find_average_of("sleep", for_each_group_in="passed", interval=95)',
                 "The average hours of sleep of the pupils who passed and of those who did not, each with its "
                 "95 % confidence interval: the range the true average is very likely in."),
                ('school.compare_averages_of("sleep", for_each_group_in="passed")',
                 "Read the first sentence first: the pupils who did not pass slept about half an hour less "
                 "(0.485 hours), and the 95 % interval of the difference goes from 0.196 to 0.774 hours. That "
                 "is the effect, and how sure the data are about it. The p-value comes after it."),
            ]),
            ("Where does a p-value come from? Shuffle the labels, and count.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('school = sdata.table(sdata.get_example("school"))', "A table of pupils."),
                ('school.compare_averages_of("sleep", for_each_group_in="passed", p_value_by="shuffling")',
                 "Imagine that passing had nothing to do with sleep. Then the labels \"yes\" and \"no\" "
                 "could be shuffled among the pupils and nothing would change. simplydata shuffles them 9999 "
                 "times and counts how often the shuffled difference is as big as the real one: about 1 time "
                 "in 1000 (p = 0.001). That count is the p-value. The p-value in the part before came from a "
                 "formula (the t distribution), a shortcut for the same count: here it is the same, "
                 "p = 0.001."),
            ]),
            ("Groups almost never have exactly the same average. A test asks: is the difference "
             "bigger than chance alone would often give?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('children = table.find_average_of("marks", for_each_group_in=["class", "name"])',
                 "Each child appears three times, once for each subject, so the 54 rows are not 54 independent "
                 "children: the three marks of one child are alike. A test that counts them as 54 children is "
                 "too sure of itself. So first make one value per child: the average of the child's three "
                 "marks, in a new table of 18 rows with the column \"average of marks\"."),
                ('children.compare_averages_of("average of marks", for_each_group_in="class")',
                 "Do the three classes really differ in their average mark? The answer comes in "
                 "words. The p-value says how often differences this big or bigger would turn up in "
                 "studies like this one if the classes were truly the same: here in about 8 of 100 "
                 "(p = 0.081), so these 18 children cannot tell. It is not the chance that the classes are "
                 "the same. (The 54 rows counted as 54 children would have given p = 0.028: too sure.) With "
                 "three or more groups this test is also called Welch's ANOVA; with two groups, a t-test."),
                ('children.compare_each_pair_of("average of marks", for_each_group_in="class")',
                 "Which classes differ? Each pair gets its own t-test (Welch's). Testing many pairs makes a "
                 "false alarm more likely, so the p-values are adjusted (Holm's method). Here no pair is "
                 "clearly different (A and C: adjusted p = 0.092)."),
                ('children.compare_averages_of("average of marks", for_each_group_in="class", based_on="ranks")',
                 "based_on=\"ranks\" puts the values in order and compares the places instead "
                 "(a Kruskal-Wallis test, or Mann-Whitney for two groups). It is safer when groups "
                 "are small and the values are not bell-shaped. Like the test above, it needs "
                 "independent rows: one row per child."),
            ]),
            ("Counts can be compared too: does how often something happens differ between groups?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")',
                 "Keep the maths marks only: one row per child, so each child is counted once."),
                ('table.add_group_column("result", from_column="marks", cut_at=[60], '
                 'names=["below 60", "60 or more"])', "A new column that says if each mark is below "
                                                      "60 or not."),
                ('table.compare_counts_of("result", for_each_group_in="class")',
                 "Do the classes differ in how many maths marks are 60 or more? This counts the children for "
                 "each class and result and uses the chi-square test. Cramer's V says how strong "
                 "the link is, from 0 (none) to 1. With only 18 children every expected count is below 5, "
                 "and a note says the p-value may be off."),
                ('table.compare_counts_of("result", for_each_group_in="class", p_value_by="shuffling")',
                 "So take the p-value by shuffling, as the note suggests: it does not need large counts. "
                 "p = 0.35 (the formula said 0.195): the data cannot tell."),
            ]),
            ("A fit finds the line or formula that follows the data best, and says how sure it is.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")',
                 "Keep the maths marks: one row per child, so every row is a different child."),
                ('table.fit_line(x="hours", y="marks")',
                 "How much do the maths marks go up for each extra hour of study? This is linear regression "
                 "by least squares. R squared says how much of the differences in marks the line "
                 "explains."),
                ('growth = sdata.table(sdata.get_example("growth"))', "A second table, with the growth data."),
                ('growth.keep_rows_where("country", is_equal_to="Applia")', "Keep one country."),
                ('growth.fit_formula("population = a * exp(b * (year - 2000))")',
                 "Fit a formula you write yourself. Names that are columns (population, year) are "
                 "data; the others (a and b) are found by simplydata. Here b is the growth rate "
                 "each year. This is nonlinear least squares."),
            ]),
            ("Before a test, look at the shape of the values and at values far from the rest. After "
             "many tests, adjust the p-values.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")',
                 "Keep the maths marks: one row per child."),
                ('table.compare_shape_to("marks", "normal", for_each_group_in="class")',
                 "Do the marks of each class look bell-shaped (normal)? The Shapiro-Wilk test answers for "
                 "each class. Tests on averages work best with bell-shaped values, or with many values."),
                ('table.show_rows_with_outliers("marks", for_each_group_in="class")',
                 "The rows whose mark is far from the rest of its class, by Tukey's rule (the one box "
                 "plots use): here one maths mark of 47 in class A. The table does not change."),
                ('pairs = table.find_correlation_between("hours", "marks", "height", show="each pair")',
                 "Test three pairs of columns at once: a table with one row per pair and its p-value."),
                ('pairs.add_adjusted_p_value_column(test_method="holm")',
                 "With many tests, one of them looks real by chance more often. Holm's adjustment keeps "
                 "the chance of even one false alarm to at most 5 %."),
                ("pairs.show()", "The p-values and the adjusted ones, side by side."),
            ]),
            ("Some questions are about spread, or about counts compared with what you expect.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Make a table of the marks."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")',
                 "Keep the maths marks: one row per child."),
                ('table.compare_spreads_of("marks", for_each_group_in="class")',
                 "Are the maths marks of one class more spread out? The data cannot tell: differences in "
                 "spread this big would turn up in about 61 of 100 studies even if the spreads were the "
                 "same (p = 0.61)."),
                ('table.compare_each_pair_of("marks", for_each_group_in="class", test_method="tukey")',
                 "Tukey's test compares every pair at once: no pair is clearly different (A and C: "
                 "p = 0.31)."),
                ('school = sdata.table(sdata.get_example("school"))', "A table of pupils."),
                ('school.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})',
                 "Did 60 % eat breakfast, as a survey said? 115 of 180 is close enough (p = 0.29)."),
                ('school.compare_percent_to("passed", value="yes", percent=50)',
                 "Did half the pupils pass? 43.3 % did; if truly half passed, a difference this big would "
                 "turn up in about 9 of 100 studies (p = 0.086), so the data cannot tell."),
            ]),
            ("When the same people are measured three times, compare the measurements within each person.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('clinic = sdata.table(sdata.get_example("clinic"))', "A table of patients."),
                ('clinic.compare_matched_columns("pain_week_0", "pain_week_4", "pain_week_8")',
                 "Each patient scored the pain at week 0, 4 and 8, one column each. compare_matched_columns compares "
                 "the three columns within each patient (the Friedman test, on ranks): the median pain falls "
                 "from 6 to 5 to 4, far more than chance would give (p < 0.0001). For two columns, "
                 "compare_before_and_after does the same."),
                ('marks = sdata.table(sdata.get_example("marks"))',
                 "The marks table is the same kind of data: each child has a mark in all three subjects."),
                ('marks.keep_columns("name", "subject", "marks")', "Keep only who, which subject and the mark."),
                ('marks.spread_into_columns(names_from="subject", values_from="marks")',
                 "One row per child, one column per subject."),
                ('marks.compare_matched_columns("Maths", "Science", "English")',
                 "Do the subjects differ? Each child is compared with itself (Friedman): the median mark is "
                 "64.5, 70 and 62, and differences this big would turn up in about 6 of 100 studies "
                 "(p = 0.056), so the data cannot tell. A Kruskal-Wallis test of the subjects would treat "
                 "the three marks of one child as marks of three different children."),
            ]),
        ],
        notes=[
            "Tests count each row as a separate, independent piece of evidence. In the marks table each child "
            "appears three times, so the rows are not independent: compare the classes on one value per child "
            "(find_average_of(..., for_each_group_in=[\"class\", \"name\"]), or one subject), and compare the "
            "subjects within each child (compare_matched_columns, or matched_by=). The same goes for pupils in "
            "the same school (lesson 16: grouped_by=) and for repeated measurements of one patient, plant or "
            "site. simplydata cannot see this in the data: you have to say it. The school examples of this lesson "
            "treat the 180 pupils as independent to keep them short; lesson 16 shows how to allow for their "
            "12 schools.",
            "The idea behind every test: imagine there is no real difference (this is called the "
            "null hypothesis). The p-value says how often a difference this big or bigger would turn "
            "up then, in studies like yours: p = 0.03 is \"about 3 of 100 studies\". It is not the "
            "chance that there is no difference, and every test says it in that one sentence.",
            "A p-value does not say how big or important the difference is: the effect size does "
            "that (omega-squared, Cohen's d, Cramer's V ...). And a large p-value does not show that "
            "there is no difference. It only means these data cannot tell.",
            "A 95 % confidence interval is the range the true value is very likely in. A narrow one "
            "means the data pin the value down well; a wide one means you need more data.",
            "Each test gives back a one-row table with all its numbers, so you can save it: "
            'result = table.compare_averages_of(...), then result.save("test.csv").',
            "Also: compare_before_and_after for two measurements of the same thing (a paired t-test), "
            "and compare_average_to for one average against a number you choose.",
            "remove_rows_with_outliers removes such rows. Say in your report which rule removed how many "
            "rows, and never remove a value only because it spoils the result.",
            'test_method="benjamini-hochberg" adjusts for many tests more gently: it controls the share of '
            "false alarms among your findings (the false discovery rate).",
            'More: with hundreds of tests, such as genes, test_method="storey" gives q-values (sdata.get_example('
            '"many_tests")); compare_each_pair_of(..., based_on="percents", value="yes") compares the percent of '
            "each pair of groups; after Friedman's test, compare_each_pair_of(..., matched_by=, test_method=\"nemenyi\") or "
            'test_method="conover".',
            "More: test_method=\"bayesian\" on compare_averages_of (two groups), compare_before_and_after, compare_average_to, "
            "find_correlation_between and compare_counts_of gives a Bayes factor (how many times as likely the data "
            "are if there is a difference as if there is none) and a credible interval instead of a p-value (R "
            "BayesFactor; the lesson \"Bayesian answers\" in sdata.show_lesson()).",
        ],
        task=[
            'Compare the classes on the science marks only (keep_rows_where("subject", is_equal_to="Science")). '
            "Could the differences be chance?",
            'Is the average temperature different between the cities of sdata.get_example("weather")?',
            'Fit a straight line of "forest" against "year" in sdata.get_example("growth") for one country.',
            'Make the table of one average mark per child (children, as in part 3), remove the rows with outliers '
            'in "average of marks" for_each_group_in="class", then compare the classes again. Did the answer '
            "change?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_rows_where("subject", is_equal_to="Science")
                table.compare_averages_of("marks", for_each_group_in="class")"""),
             "Yes, they could: p = 0.20 is well above 0.05. That does not prove the classes are "
             "the same; these 18 children simply cannot tell. A note says class B does not look "
             "bell-shaped, so based_on=\"ranks\" is the safer test here."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                table.compare_averages_of("temperature", for_each_group_in="city")
                table.compare_each_pair_of("temperature", for_each_group_in="city")"""),
             "Yes: if the cities truly had the same average, differences this big would turn up in "
             "fewer than 1 in 1000 studies (p = 0.0002). compare_each_pair_of then shows which "
             "cities differ from each other."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("growth"))
                table.keep_rows_where("country", is_equal_to="Applia")
                table.fit_line(x="year", y="forest")"""),
             "In Applia the forest shrinks by about 0.57 percentage points a year (95 % CI 0.48 to "
             "0.67), and the line explains 94 % of the differences."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                children = table.find_average_of("marks", for_each_group_in=["class", "name"])
                children.remove_rows_with_outliers("average of marks", for_each_group_in="class")
                children.compare_averages_of("average of marks", for_each_group_in="class")"""),
             "One child (Hana, 79.7 in class B) is removed. Class B goes down from 64.3 to 61.2, and p goes "
             "from 0.081 to 0.042: with 18 children, one child can change the answer. Report both, say "
             "which rule removed whom, and never remove a value only because it changes the result."),
        ],
        words=["table.compare_averages_of", "table.compare_each_pair_of", "table.compare_counts_of",
               "table.fit_line", "table.fit_formula", "table.add_group_column",
               "table.compare_shape_to", "table.show_rows_with_outliers", "table.add_adjusted_p_value_column",
               "table.remove_rows_with_outliers", "table.compare_spreads_of", "table.compare_counts_to",
               "table.compare_percent_to", "table.compare_matched_columns"],
    ),
    dict(
        title="A whole analysis: from a question to a figure",
        learn=[
            "how to put all the lessons together: open, look, clean, sum up, test, draw and save",
            "how to make a figure with panels A and B, ready for a report or a paper",
            "how show_steps() writes down what you did, in plain words",
            "how to hand your table to pandas or Polars, and back",
        ],
        parts=[
            ("A whole analysis with one question: do children who study longer get better marks, "
             "and do the classes differ? One table feeds two charts, and the two charts become "
             "one figure.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "Open the data. For your own file: "
                                                          'sdata.table("results.xlsx").'),
                ("table.describe_columns()", "Look: what is in each column, and are any cells empty?"),
                ("table.remove_rows_with_empty_cells_in()", "Clean: remove the rows with an empty cell. The "
                                                         "practice table has none, so nothing is removed."),
                ('table.find_average_of("marks", for_each_group_in="class")', "Sum up: the average mark of each class."),
                ('children = table.find_average_of("marks", for_each_group_in=["class", "name"])',
                 "Each child is in the table three times, once for each subject, so the rows are not "
                 "independent. For the test, one value per child: the average of the child's three marks."),
                ('children.compare_averages_of("average of marks", for_each_group_in="class")',
                 "Test: could the differences between the classes be chance? With one value per child, "
                 "they could (p = 0.081)."),
                ("a = table.start_chart()", "Chart A, from the cleaned table."),
                ('a.draw_boxes(x="class", y="marks")', "The marks of each class as boxes."),
                ('a.draw_all_dots(x="class", y="marks")', "Every mark as a dot, on top of the boxes."),
                ('a.label_y("Mark (out of 100)")', "Name its y-axis."),
                ("b = table.start_chart()", "Chart B, from the same table."),
                ('b.draw_dots(x="hours", y="marks", colour="class")', "Hours of study against marks, "
                                                                 "one colour per class."),
                ("b.fit_line(with_confidence_band=True)", "A straight line for each class, with its 95 % "
                                                     "confidence band."),
                ('b.label_x("Hours of study")', "Name its x-axis."),
                ("figure = sdata.put_in_rows_and_columns(a, b, per_row=2, with_letters=True)", "Both charts on one page, with A "
                                                                    "and B at the top left."),
                ('figure.write_title_on_top("Marks, classes and hours of study")', "A title for the whole page."),
                ('figure.use_style("paper")', "A quiet look that suits a paper."),
                ('figure.set_size(width=17, height=8, unit="cm")', "The size a journal asks for: 17 cm wide "
                                                               "(a full page width) and 8 cm high."),
                ('figure.save("lesson15_figure.pdf")', "Save the figure as a PDF: sharp at any size."),
                ('figure.save("lesson15_figure.tif", resolution=600)', "And as a .tif picture with 600 "
                                                                       "dots per inch, as many journals ask."),
                ('table.save("lesson15_clean.xlsx")', "Save the cleaned table that the figure was "
                                                      "drawn from."),
                ("table.show_steps()", "Every table step in plain words, in order: a good start for the "
                                  "methods part of your report."),
            ]),
            ("Two questions about two tables give two charts. sdata.put_in_rows_and_columns puts them on one page.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('weather = sdata.table(sdata.get_example("weather"))', "Table 1: the weather."),
                ('weather.keep_rows_where("city", is_equal_to="Rainbridge")', "Keep one city."),
                ("rain = weather.start_chart()", "A chart of it, called rain."),
                ('rain.draw_bars(x="month", y="rain")', "Its rain through the year."),
                ('rain.draw_line_at_y(100, labelled="100 mm")', "A line at 100 mm."),
                ('growth = sdata.table(sdata.get_example("growth"))', "Table 2: four countries."),
                ("forest = growth.start_chart()", "A chart of it, called forest."),
                ('forest.draw_lines(x="year", y="forest", colour="country")', "Their forest over the years."),
                ('forest.label_y("Forest (% of the land)")', "Name the y-axis."),
                ("charts = sdata.put_in_rows_and_columns(rain, forest, per_row=2, with_letters=True)", "Both charts on one page, "
                                                                          "with letters."),
                ('charts.save("lesson15_two_tables.png")', "Save the page."),
            ]),
            ("A table goes to pandas or Polars and back whenever another Python tool needs it.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("weather"))', "A table of the weather."),
                ('table.keep_rows_where("city", is_equal_to="Rainbridge")', "Keep one city."),
                ("df = table.as_pandas()", "A plain pandas DataFrame (table.as_polars() gives a "
                                           "Polars one)."),
                ('print(df["rain"].max())', "Any pandas code works on it."),
                ("again = sdata.table(df)", "And back: sdata.table takes a pandas or Polars table you "
                                         "already have."),
                ("chart = sdata.chart(df)", "sdata.chart takes one too."),
                ('chart.draw_bars(x="month", y="rain")', "Draw it."),
                ('chart.save("lesson15_rain.png")', "Save the chart."),
            ]),
        ],
        notes=[
            "Every analysis follows the same plan: open, look, clean, sum up, test, draw, words, "
            "save. Lessons 1 to 14 taught each part; this lesson puts them together.",
            "The table and the charts are separate objects, as in pandas and matplotlib: one cleaned "
            "table can feed many charts, and each chart keeps the rows the table had when the chart "
            "was made.",
            "table.save saves the table, and chart.save or charts.save the picture. Save both, so "
            "anyone can check the figure against its data.",
            "table.show_steps() lists the table steps. Together with the chart lines of your program, it "
            "says everything you did.",
            "simplydata words never need as_pandas(); it is only for other tools.",
        ],
        task=[
            'Do a whole analysis of sdata.get_example("weather"): look at it, compare the average rain '
            'for_each_group_in="city", draw the rain of each city as boxes, and save the chart and the table.',
            "Make a second chart of the temperature, then put the two charts together with "
            "sdata.put_side_by_side(..., with_letters=True).",
            "Read the show_steps() of your table out loud. Would someone else understand what you did?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                table.describe_columns()
                table.remove_columns("wind_direction", "wind_speed")
                table.find_average_of("rain", for_each_group_in="city")
                table.compare_averages_of("rain", for_each_group_in="city")
                chart = table.start_chart()
                chart.draw_boxes(x="city", y="rain")
                chart.draw_all_dots(x="city", y="rain")
                chart.label_y("Rain (mm)")
                chart.save("lesson15_rain_boxes.png")
                table.save("lesson15_weather.xlsx")"""),
             "Rainbridge is much wetter (109 mm a month on average) than Frostby (42) and Sunnyvale "
             "(26); if the cities truly had the same rain, differences this big would turn up in fewer "
             "than 1 in 1000 studies (p < 0.0001)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                rain = table.start_chart()
                rain.draw_boxes(x="city", y="rain")
                rain.label_y("Rain (mm)")
                warmth = table.start_chart()
                warmth.draw_lines(x="month", y="temperature", colour="city")
                warmth.label_y("Temperature (°C)")
                charts = sdata.put_side_by_side(rain, warmth, with_letters=True)
                charts.save("lesson15_weather_page.png")"""),
             "Two charts of one table, side by side, with A and B so a report can point to each."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                table.remove_columns("wind_direction", "wind_speed")
                table.keep_rows_where("month_number", is_between=[6, 8])
                table.sort_by("rain", biggest_first=True)
                table.show_steps()"""),
             "show_steps() lists each change in plain words, in order; those lines are a first draft of "
             "the methods part of a report."),
        ],
        words=["sdata.table", "table.describe_columns", "table.remove_rows_with_empty_cells_in",
               "table.compare_averages_of", "table.start_chart", "draw_boxes", "draw_all_dots", "draw_dots", "fit_line",
               "sdata.put_in_rows_and_columns", "use_style", "table.save", "table.show_steps", "table.as_pandas", "sdata.chart"],
    ),
    dict(
        title="Models: explain one column from several others",
        needs_r=needs_r_text('Only explain(..., empty_cells="multiple imputation") needs R: it pools its results with '
                             "R (mice). The rest of the lesson needs no R. That option and the other R words"),
        learn=[
            "how to explain one column from several others at once (multiple regression)",
            "how to explain a yes/no column (logistic regression) and a column of counts (Poisson regression)",
            "how to allow for groups such as schools (a mixed model)",
            "how to use rows with empty cells without guessing once (multiple imputation)",
            "how to say how much a column changes the chance of yes (a risk ratio, not only an odds ratio)",
        ],
        parts=[
            ("Marks depend on more than one thing. explain() looks at several columns together, so each "
             "effect is the effect with the other columns held fixed.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "Pupils in 12 schools: study, sleep, "
                                                                 "breakfast and marks."),
                ('table.explain("marks", using=["hours", "sleep", "breakfast"])',
                 "Explain the marks from hours of study, hours of sleep and breakfast. Each extra hour of "
                 "study goes with about 2.7 more marks, each extra hour of sleep with 2.3 more, and "
                 "breakfast with 3.2 more, each with its 95 % confidence interval and p-value. This is "
                 "a linear model (multiple regression) by least squares. It counts the 180 pupils as "
                 "independent, but they come from 12 schools, and pupils of one school are alike: part 3 "
                 "allows for that with grouped_by=\"school\". Until then, read these p-values as a little too "
                 "small."),
                ('table.explain("marks", using=["hours * breakfast"])',
                 "hours * breakfast also asks: does the effect of study depend on breakfast? That is an "
                 "interaction. Here the data cannot tell: about 31 of 100 studies would show this much "
                 "if there were truly none (p = 0.31)."),
            ]),
            ("Not every column is a number to explain. A yes/no column needs the chance of yes, and a "
             "count needs a model for counts.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.explain("passed", using=["hours", "breakfast"], outcome="yes or no")',
                 'Did the pupil pass? outcome="yes or no" is logistic regression. Each extra hour of '
                 "study multiplies the odds of passing by 1.66 (an odds ratio)."),
                ('table.explain("days_absent", using=["hours", "sleep"], outcome="counts")',
                 'Days absent are counts (0, 1, 2 ...). outcome="counts" is Poisson regression; each '
                 "extra hour of study multiplies the expected days absent by 0.88 (a rate ratio)."),
                ('table.add_predicted_column("marks", using=["hours", "breakfast"])',
                 'Add a column "predicted marks": what the model expects for each pupil.'),
                ("table.show_first_rows(5)", "Look at the marks next to the predicted marks."),
            ]),
            ("Pupils in the same school are alike in ways the columns do not show. A mixed model allows "
             "for that, and multiple imputation uses the rows with empty cells.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.explain("marks", using=["hours", "breakfast"], grouped_by="school")',
                 "A mixed model: each school gets its own starting level (a random intercept). About 39 % "
                 "of the differences the columns do not explain lie between schools (the ICC)."),
                ('table.explain("marks", using=["hours", "sleep", "breakfast"], '
                 'empty_cells="multiple imputation")',
                 "19 pupils did not say how long they slept. Instead of leaving them out, multiple "
                 "imputation fills the empty cells 20 times, fits the model to each filled-in table and "
                 "pools the 20 answers (Rubin's rules), so the extra uncertainty is counted."),
            ]),
            ("An odds ratio is not a risk ratio. When yes is common, the odds ratio is further from 1 than the "
             "change in the chance itself, and readers often take it for the chance.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.explain("passed", using=["hours", "breakfast"], outcome="yes or no")',
                 "Odds ratios, as in part 2. 43 % of the pupils passed, so the printout ends with a note: an "
                 "odds ratio is not a risk ratio here, and show=\"risk ratios\" gives risk ratios."),
                ('table.explain("passed", using=["hours", "breakfast"], outcome="yes or no", show="risk ratios")',
                 'show="risk ratios" gives risk ratios (modified Poisson regression): each extra hour of study '
                 "multiplies the chance of passing by 1.21, where the odds ratio was 1.66. Say in words what "
                 "1.21 means: with one more hour of study, the chance of passing is about a fifth higher."),
            ]),
        ],
        notes=[
            "Each effect in explain() holds the other columns fixed: the effect of sleep is the effect "
            "for pupils who study the same number of hours and have the same breakfast.",
            "A text column such as breakfast is compared with its first group in A to Z order (here "
            '"no"); the answer says which group is the baseline.',
            "An odds ratio above 1 means higher odds of yes; a rate ratio above 1 means more counts. "
            "1 means no difference.",
            "If counts vary much more than a Poisson model expects (overdispersion), simplydata says so "
            'and suggests outcome="counts (overdispersed)"; it never switches by itself.',
            "grouped_by= is for rows that come in groups: pupils in schools, measurements on the same "
            "animal, samples from the same site. Without it, the p-values are too small.",
            "Multiple imputation needs the empty cells to be explainable by the other columns (missing "
            "at random). Say in your report how many cells were empty and how they were handled.",
            "grouped_by= works out of the box (statsmodels comes with simplydata). Multiple "
            "imputation pools its results in R, so it needs R (see the box at the start).",
            "A risk ratio of 1.21 means the chance of yes is 21 % higher. Report risk ratios when yes is common "
            "(more than about 1 in 10 rows); simplydata says when that is the case.",
            "More outcomes for later, all in the manual and the dictionary: \"yes or no (overdispersed)\" (yes "
            "counts out of tries that vary a lot), \"counts with many zeros that vary a lot\" and \"counts in two "
            "steps\" (first zero or not, then how many).",
        ],
        task=[
            'Explain "marks" using "hours" and "school" (school as a column of groups). Which schools '
            "differ from School A, and is school as a whole important?",
            'Explain "passed" using "hours" and "sleep" with outcome="yes or no".',
            'Explain "days_absent" using "hours" and "breakfast" with outcome="counts". Does breakfast '
            "matter?",
            'In the clinic table, explain "caught_infection" using "ward" and "patient_days" with '
            'outcome="yes or no", first as odds ratios and then with show="risk ratios". Which is further '
            "from 1?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.explain("marks", using=["hours", "school"])"""),
             "School as a whole matters a lot (F = 10.4, p < 0.0001); School D scores about 15 marks "
             "more than School A for the same hours of study. grouped_by= would instead treat the "
             "schools as a sample of many possible schools."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.explain("passed", using=["hours", "sleep"], outcome="yes or no")"""),
             "Each extra hour of study multiplies the odds of passing by 1.69 and each extra hour of "
             "sleep by 1.98; with truly no effect, fewer than 1 in 1000 studies (hours) and about 2 "
             "of 1000 (sleep) would show this much."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.explain("days_absent", using=["hours", "breakfast"], outcome="counts")"""),
             "For breakfast the data cannot tell (rate ratio 0.94, p = 0.45: about 45 of 100 studies "
             "would show this much with truly no effect); study hours matter (rate "
             "ratio 0.86 for each hour)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("clinic"))
                table.explain("caught_infection", using=["ward", "patient_days"], outcome="yes or no")
                table.explain("caught_infection", using=["ward", "patient_days"], outcome="yes or no",
                              show="risk ratios")"""),
             "Ward B: odds ratio 5.80, risk ratio 4.63. The odds ratio is further from 1, even with only 1 patient "
             "in 10 infected; the rarer the outcome, the closer the two."),
        ],
        words=["table.explain", "table.add_predicted_column", "table.show_first_rows"],
    ),
    dict(
        title="Patterns across many columns",
        needs_r=needs_r_text('add_nmds(), compare_profiles_of() and add_clusters() with k-means (the default)'),
        learn=[
            "how to sum up many columns in two new ones (principal components)",
            "how to measure how different rows are (Bray-Curtis and other distances)",
            "how to draw a map of the rows (NMDS) and test groups on all columns at once (PERMANOVA)",
            "how to find groups of similar rows (clustering)",
        ],
        parts=[
            ("Ten plant counts per plot are too many to look at one by one. Principal components "
             "make a few new columns that hold most of the spread.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("meadow"))', "Plants counted in 30 plots, half of them "
                                                                 "grazed by sheep."),
                ("table.add_principal_components(how_many=2)",
                 "Principal component analysis (PCA): adds PC1 and PC2. PC1 holds 30 % of the spread, "
                 "PC2 15 %. The printout says which plants weigh most in each."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_dots(x="PC1", y="PC2", colour="grazed")', "Each plot is a dot; grazed and ungrazed "
                                                                 "plots sit apart."),
                ('chart.save("lesson17_pca.png")', "Save it."),
            ]),
            ("Ecologists compare plots by how different their make-up is. Bray-Curtis is the usual "
             "distance for counts, and NMDS draws a map that keeps the order of the distances.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("meadow"))', "The meadow table."),
                ('distances = table.find_distances_between_rows(measure="bray-curtis", names="plot")',
                 "A table of the Bray-Curtis distance between every pair of plots: 0 means the same "
                 "plants in the same numbers, 1 means nothing in common."),
                ("distances.show_first_rows(3)", "Look at the first rows."),
                ('table.add_nmds(measure="bray-curtis")',
                 "Non-metric multidimensional scaling (NMDS): adds NMDS1 and NMDS2. The stress (0.195) "
                 "says how well the map keeps the distances: usable."),
                ('table.compare_profiles_of(for_each_group_in="grazed")',
                 "Do grazed and ungrazed plots differ in make-up? PERMANOVA tests all ten plants at "
                 "once: grazing explains 25 % of the differences (p = 0.001)."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_dots(x="NMDS1", y="NMDS2", colour="grazed")', "The NMDS map."),
                ('chart.save("lesson17_nmds.png")', "Save it."),
            ]),
            ("Clustering finds groups of similar rows without being told the groups.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("meadow"))', "The meadow table."),
                ("table.add_clusters(how_many=2)", 'k-means clustering: adds a column "cluster" with 1 or 2.'),
                ('table.count_rows(for_each_group_in="cluster", across="grazed")',
                 "Did the clusters find the grazing? Cluster 1 is 14 grazed plots, cluster 2 is the 15 "
                 "ungrazed plots and one grazed one."),
            ]),
        ],
        notes=[
            "same_scale=True (the normal choice for PCA and clusters) puts every column on the same "
            "scale first, so a column with big numbers does not drown the others.",
            "The signs and the rotation of PC and NMDS axes are arbitrary; only the distances between "
            "the dots mean something.",
            "Clarke's rule for NMDS stress: below 0.05 excellent, below 0.1 good, below 0.2 usable, "
            "above 0.2 hard to trust. Try dimensions=3 if the stress is high.",
            "PERMANOVA can mistake a difference in spread for a difference in make-up, so "
            "compare_profiles_of also checks the spread of each group and says if it differs.",
            'More: table.add_principal_coordinates() is the twin of add_nmds (a map from the distances, PCo1 and '
            'PCo2); add_clusters(how_many="automatic") chooses the number of clusters by the silhouette width; '
            "chart.draw_cluster_tree() draws the tree of hierarchical clusters. Lessons 31 and 32 use them on a "
            "resistome.",
            "Clusters always appear, even in data without groups: check them against what you know.",
            'test_method="hierarchical" clusters step by step (Ward linkage) instead of k-means.',
        ],
        task=[
            'Add principal components of "hours", "sleep", "marks" and "days_absent" in '
            'sdata.get_example("school"). Which columns weigh most in PC1?',
            "Make an NMDS map of the meadow in 3 dimensions. Is the stress lower than in 2?",
            'Do the three fields differ in make-up? Use compare_profiles_of with for_each_group_in="field".',
            'Cluster the meadow plots with test_method="hierarchical". Do the clusters match the grazing?',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.add_principal_components(columns=["hours", "sleep", "marks", "days_absent"])"""),
             "PC1 (50 % of the spread) is mostly hours, marks and, the other way, days absent: pupils "
             "who study more get better marks and miss fewer days. PC2 is mostly sleep."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("meadow"))
                table.add_nmds(measure="bray-curtis", dimensions=3)"""),
             "Yes: the stress drops from 0.195 to 0.127. That is still in the usable band (good is below "
             "0.1), but the map keeps the distances clearly better."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("meadow"))
                table.compare_profiles_of(for_each_group_in="field")"""),
             "The fields explain 12 % of the differences, much less than grazing (25 %); a difference "
             "this big would turn up in about 5 of 100 studies even if the fields had the same make-up "
             "(p = 0.053). The spread check finds no sign of a difference in spread (p = 0.53)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("meadow"))
                table.add_clusters(how_many=2, test_method="hierarchical")
                table.count_rows(for_each_group_in="cluster", across="grazed")"""),
             "Exactly: cluster 1 is the 15 grazed plots and cluster 2 the 15 ungrazed ones."),
        ],
        words=["table.add_principal_components", "table.find_principal_components_of", "table.add_clusters",
               "table.find_distances_between_rows", "table.add_nmds", "table.compare_profiles_of", "draw_dots"],
    ),
    dict(
        title="Survival, and planning a study",
        needs_r=needs_r_text('The proportional-hazards check inside explain_survival() (R survival::cox.zph()); the rest of the lesson needs no R. Without R that one check is left out with a note. The check and the other R words'),
        learn=[
            "how to draw survival curves (Kaplan-Meier) and compare them (log-rank test)",
            "how to explain the risk of an event from several columns (a Cox model)",
            "how many values a study needs, before you collect them (power analysis)",
        ],
        parts=[
            ("In a trial, some patients are still alive when the follow-up ends. Survival words use "
             "their time too: they count as followed without the event (censored).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("trial"))', "120 patients, a new medicine or usual "
                                                                "care, followed for up to 3 years."),
                ('table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment")',
                 "The Kaplan-Meier estimate: the share still alive at each time, and the median time "
                 "(706 days with the new medicine, 545 with usual care)."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_survival_curves(time="days", event="died", colour="treatment", '
                 'with_confidence_band=True, with_at_risk_table=True)',
                 "Survival curves with their 95 % bands, ticks where patients were censored, and the "
                 "number still followed under the x-axis."),
                ('chart.save("lesson18_survival.png")', "Save it."),
            ]),
            ("Is the difference real? And what else changes the risk?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("trial"))', "The trial table."),
                ('table.compare_survival(time="days", event="died", for_each_group_in="treatment")',
                 "The log-rank test compares the whole curves: here the data cannot tell (p = 0.22; "
                 "differences this big would turn up in about 22 of 100 studies with truly alike groups)."),
                ('table.explain_survival(time="days", event="died", using=["treatment", "age"])',
                 "A Cox model: each year of age raises the risk of dying at any moment by about 5 % "
                 "(hazard ratio 1.05), with the treatment held fixed."),
            ]),
            ("Was the trial big enough? Power analysis tells you how many values you need before you "
             "collect them.", [
                ("import simplydata as sdata", "Load simplydata."),
                ("sdata.find_how_many_needed(effect_size=0.5, power=0.8)",
                 "To find a medium difference between two averages (half a standard deviation) with an "
                 "80 % chance, you need 64 values in each group."),
                ("sdata.find_chance_of_finding(effect_size=0.5, values_per_group=20)",
                 "With only 20 values in each group, the chance to find it is just 34 %."),
                # S3b-2: one line, events first
                ('sdata.find_how_many_needed(for_test="compare_survival", effect_size=0.7, percents=[30, 40])',
                 "Survival is planned in events first: to find a hazard ratio of 0.7 you need 247 events; if 30 % "
                 "and 40 % have the event during the study, that is 706 people (needs R)."),
            ]),
        ],
        notes=[
            "Never leave out the censored rows or count them as survivors: the survival words use the "
            "time they were followed, which is what makes these methods right.",
            "A hazard ratio above 1 means a higher risk of the event at any moment; 1 means no "
            "difference. The Cox model assumes the ratio stays the same over time, and simplydata "
            "checks this and says so if it does not.",
            "A study that is too small often finds nothing even when there is something to find. Plan "
            "the size before collecting data, not after.",
            "effect_size= is Cohen's d for averages, f for 3 or more groups, w for counts and r for a "
            "correlation. You can also give difference= and spread= in your own units.",
            # S3b-3: one "more" line
            "More survival in the lesson \"More survival\": at_time_points=[365, 730] reads the curves at chosen times, and "
            "allowing_for= takes a column into account without estimating its effect.",
        ],
        task=[
            'Explain the risk of dying from "age" alone with explain_survival.',
            "How many pairs does a before/after study need to find a small change (effect_size=0.3)?",
            "What is the chance to find a medium difference (effect_size=0.25) between 3 groups with "
            "30 values in each?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("trial"))
                table.explain_survival(time="days", event="died", using="age")"""),
             "Each year of age multiplies the risk by 1.05 (95 % CI 1.03 to 1.08), p < 0.0001."),
            (_sx("""\
                import simplydata as sdata
                sdata.find_how_many_needed(for_test="compare_before_and_after", effect_size=0.3)"""),
             "90 pairs, each with a before and an after value."),
            (_sx("""\
                import simplydata as sdata
                sdata.find_chance_of_finding(for_test="compare_averages", effect_size=0.25, groups=3, values_per_group=30)"""),
             "Only 54 %: too small. find_how_many_needed with groups=3 tells you how many to aim for."),
        ],
        words=["table.find_survival_over_time", "draw_survival_curves", "table.compare_survival",
               "table.explain_survival", "sdata.find_how_many_needed", "sdata.find_chance_of_finding"],
    ),
    dict(
        title="Fitting curves, finding the best value and solving",
        learn=[
            "how to fit a straight line, a curve or any formula to your data, on a table and on a chart",
            "how to find where a formula is smallest or biggest",
            "how to solve an equation, also one made from a fitted formula",
        ],
        parts=[
            ("Start with something you know: a straight line through the dots. fit_line, fit_curve and "
             "fit_formula are the same words on a table (the numbers) and on a chart (the picture).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("marks"))', "The marks table: hours of study and marks."),
                ('table.keep_rows_where("subject", is_equal_to="Maths")',
                 "Keep the maths marks: one row per child, so each child counts once."),
                ('table.fit_line(x="hours", y="marks")',
                 "The straight line: about 6.2 marks more for each hour of study, and R squared 0.78."),
                ('table.fit_curve(x="hours", y="marks", of_degree=2)',
                 "A curve with one bend (hours and hours**2). R squared only goes from 0.78 to 0.80, so the "
                 "bend adds little: the straight line is enough here."),
                ("chart = table.start_chart()", "Start a chart of the same table."),
                ('chart.draw_dots(x="hours", y="marks")', "The dots."),
                ("chart.fit_line()", "The same straight line, drawn."),
                ("chart.fit_curve(of_degree=2)", "And the curve, to see how close they are."),
                ('chart.save("lesson19_line_and_curve.png")', "Save it."),
            ]),
            ("A research question: how fast does each country grow? Growth by a fixed share each year "
             "is the formula population = a * exp(b * (year - 2000)). Names that are columns (population, "
             "year) are data; the other names (a, b) are the values to find.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("growth"))', "Four countries, every two years."),
                ('table.fit_formula("population = a * exp(b * (year - 2000))", for_each_group_in="country")',
                 "One fit for each country, by nonlinear least squares (as R nls()). a is the population in "
                 "2000 and b the growth rate: Cherria grows fastest, b = 0.0443, about 4.5 % a year."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_dots(x="year", y="population", colour="country")', "The data, one colour per country."),
                ('chart.fit_formula("population = a * exp(b * (year - 2000))")',
                 "The fitted curve of each country, with the same values as the table word."),
                ('chart.save("lesson19_growth.png")', "Save it."),
            ]),
            ("Finding and solving: sdata.find_where_smallest, sdata.find_where_biggest and sdata.solve work on a "
             "formula. The names in it are what to find; between= says where to look.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5])',
                 "The smallest value is -3, at x = 2. The method and its R name are printed (R optimize())."),
                ('sdata.find_where_biggest("3*x + 2*y", rules=["x + y <= 4", "x + 3*y <= 6", "x >= 0", "y >= 0"])',
                 "The biggest value under rules: 12, at x = 4 and y = 0. Everything is a straight line, so "
                 "simplydata uses linear programming and says which rules are reached exactly."),
                ('sdata.solve("x**3 - 2*x = 5", between=[0, 3])',
                 "The value of x that makes both sides equal: 2.09455. Every solution in the range is found."),
                ('table = sdata.table(sdata.get_example("growth"))', "Back to the growth table."),
                ('table.keep_rows_where("country", is_equal_to="Applia")', "Keep one country."),
                ('fit = table.fit_formula("population = a * exp(b * (year - 2000))")',
                 "Fit the growth formula and keep the result, a one-row table with a and b."),
                ('sdata.solve("a * exp(b * (year - 2000)) = 20", between=[2000, 2050], known=fit)',
                 "known=fit puts the fitted a and b into the equation: Applia reaches 20 million in about "
                 "2017 (year = 2017.24). A fitted curve answers questions, not only draws a line."),
            ]),
            ("Growth curves: bacteria in a flask grow fast, then level off. Instead of writing that formula "
             "yourself, name the curve with of_kind=: fit_curve then writes the formula and finds start values "
             "for you (R's own self-starting models when R is there).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("culture"))', "Three flasks, measured every hour."),
                ('table.keep_rows_where("flask", is_equal_to="A")', "Keep flask A."),
                ('table.fit_curve(x="hour", y="density", of_kind="logistic growth")',
                 "Asym = 1.15 is where the culture levels off, xmid = 9.59 the hour it is half way up, and scal = "
                 "2.02 how fast it rises. Say in words what xmid means for this flask."),
                ('table.fit_curve(x="hour", y="density", of_kind="gompertz growth")',
                 "The same data with another growth curve (one change in the call). Compare the levels the two "
                 "curves give."),
            ]),
            ("Exact answers with a formula (needs the extra simplydata[exact], SymPy: "
             "pip install \"simplydata[exact]\"). The letters stay letters, so the answers are formulas.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('f = sdata.formula("(x + 2)**2 - 4")', "A formula with the letter x."),
                ("f.turn_into_sum()", "Multiply out the brackets: x**2 + 4*x."),
                ("f.turn_into_product()", "Write it as a product: x*(x + 4). f.undo() would take it back."),
                ("slope = f.find_slope_formula()", "The formula of its slope (the derivative): 2*x + 4."),
                ("f.find_value_at(x=3)", "Its value at x = 3: 21."),
                ('sdata.solve("x**2 = 2", exactly=True)',
                 "The exact solutions, -sqrt(2) and sqrt(2), with their decimals in the table."),
            ]),
            ("Areas and paths over time: the area under a curve, and the values over time from how fast they "
             "change.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('sdata.find_area_under("exp(-x**2)", between=[0, "infinity"])',
                 "The area under the bell curve from 0 to infinity: 0.886227, half the square root of pi "
                 "(SciPy integrate.quad, as R integrate())."),
                ('growth = sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, '
                 'between=[0, 50], known={"r": 0.3, "K": 1000}, time_step=0.5, stop_when="N >= 900")',
                 "Logistic growth from 10 cells, at rate 0.3 towards 1000: the table holds N every half hour. "
                 "stop_when= stops when N reaches 900, at t = 22.64 (SciPy integrate.solve_ivp)."),
                ("growth.show_last_rows(3)", "The last times before it stopped."),
            ]),
            ("If you have R: a dose-response curve. A toxicity test grows seedlings at eight concentrations. "
             "fit_dose_response finds the dose that halves the effect (the ED50, or EC50) with its 95 % "
             "interval, from the fitted curve, not from the raw averages.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("toxicity"))', "Two chemicals, three dishes per dose."),
                ('table.keep_rows_where("chemical", is_equal_to="A")', "Keep chemical A."),
                ('table.fit_dose_response(x="concentration", y="root_length")',
                 "A 4 parameter log-logistic curve (R drc): the ED50 is 3.92 mg per litre (95 % CI 3.11 to 4.73). "
                 "Say in words what the ED50 means for the roots."),
                ('table.fit_dose_response(x="concentration", y="dead", outcome="yes or no", out_of="seedlings")',
                 "Deaths out of 20 seedlings: the LD50, the dose that kills half, is 4.94 mg per litre."),
                ('chart = sdata.chart(sdata.get_example("toxicity"))', "A chart of both chemicals."),
                ('chart.draw_dots(x="concentration", y="root_length", colour="chemical")', "The dishes."),
                ("chart.fit_dose_response()", "One curve per chemical, with its ED50 in the legend."),
                ('chart.save("lesson19_dose_response.png")', "Save it."),
            ]),
        ],
        notes=[
            "Fitting is the same idea every time: a line, a curve or a formula is moved until it is as "
            "close to the points as it can be (least squares). The printed sentence says how sure each "
            "value is (its 95 % confidence interval).",
            "A curve with a high of_degree= can wiggle through every point and still say nothing true. Choose "
            "the simplest line or formula that follows the data, and a formula whose values mean something "
            "(here b is a growth rate).",
            'If a formula fit fails, give start values near the answer: start={"a": 10, "b": 0.03}.',
            "sdata.find_where_smallest with between= finds one lowest point; when the curve has several dips it says "
            'so, and search="whole range" looks everywhere. solve with between= finds every crossing.',
            "Names from other tools point to these words: minimize, optimise and argmin to find_where_smallest, "
            "fsolve, brentq and uniroot to solve, curve_fit and nls to fit_formula, polyfit to fit_curve.",
            'More: fit_line(test_method=) draws other lines ("theil-sen", "standardised major axis", "deming"), '
            "fit_line(with_bends=1) lets the line bend, and find_best_power_of finds the Box-Cox power of a "
            "column. The manual and the dictionary have the rest.",
        ],
        task=[
            'Fit a curve of degree 3 to the maths "marks" against "hours". Does R squared go up much from the straight '
            "line?",
            'With the weather table, keep the city Sunnyvale and fit "temperature = a + b * cos(2 * pi * '
            '(month_number - c) / 12)" with start={"a": 15, "b": 8, "c": 7}. In which month is it warmest (c)?',
            "Try to remember without looking back: which word finds where a formula is biggest, and which "
            'word finds where the two sides of an equation are equal? Use them on "x * (10 - x)" between 0 '
            'and 10, and on "x**2 = 2" between 0 and 2.',
            'Fill in the call for chemical B of the toxicity table: table.fit_dose_response(x="...", y="...", '
            "doses_for_effect=[10, 50]). Which dose gives 10 % of the effect? (Needs R.)",
            "Without looking back: which word gives the EC50 of a toxicity test, and which of_kind= fits a growth "
            "curve that levels off? Use the second on flask C of the culture table.",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_rows_where("subject", is_equal_to="Maths")
                table.fit_curve(x="hours", y="marks", of_degree=3)"""),
             "R squared is 0.80, against 0.78 for the straight line: the extra bends add very little."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                table.keep_rows_where("city", is_equal_to="Sunnyvale")
                table.fit_formula("temperature = a + b * cos(2 * pi * (month_number - c) / 12)",
                                  start={"a": 15, "b": 8, "c": 7})"""),
             "c = 7.19: the warmest time is in July; a = 17.0 is the average and b = 8.18 how far it swings."),
            (_sx("""\
                import simplydata as sdata
                sdata.find_where_biggest("x * (10 - x)", between=[0, 10])
                sdata.solve("x**2 = 2", between=[0, 2])"""),
             "find_biggest gives 25 at x = 5, and solve gives x = 1.41421, the square root of 2."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("toxicity"))
                table.keep_rows_where("chemical", is_equal_to="B")
                table.fit_dose_response(x="concentration", y="root_length", doses_for_effect=[10, 50])"""),
             "ED10 is 3.32 and ED50 9.35 mg per litre: chemical B needs more than twice the dose of A."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("culture"))
                table.keep_rows_where("flask", is_equal_to="C")
                table.fit_curve(x="hour", y="density", of_kind="logistic growth")"""),
             'fit_dose_response gives the EC50; of_kind="logistic growth" levels off. Flask C levels off at '
             "about 1.25, half way up at about hour 10.5."),
        ],
        words=["table.fit_line", "table.fit_curve", "table.fit_formula", "fit_line", "fit_curve", "fit_formula",
               "sdata.find_where_smallest", "sdata.find_where_biggest", "sdata.solve",
               "sdata.formula", "f.turn_into_sum", "f.turn_into_product", "f.find_slope_formula", "f.find_value_at",
               "sdata.find_area_under", "sdata.find_path_over_time",
               "table.fit_dose_response", "fit_dose_response"],
        needs_r=needs_r_text("Only the last example part and the fourth task (fit_dose_response, R drc)",
                             packages=("drc",)),
    ),
    dict(
        title="Distributions, chances and values between points",
        learn=[
            "how to ask a distribution for chances, percentiles and cut-offs",
            "how to find which distribution fits your data, and check it",
            "how to estimate values between the points you measured",
        ],
        parts=[
            ("A distribution says how likely each value is. Start with the bell curve (normal): marks "
             "with an average of 50 and a standard deviation of 10.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('dist = sdata.distribution("normal", average=50, standard_deviation=10)',
                 "Make the distribution. R's names (mean=, sd=) work too."),
                ("dist.find_chance_that_value(is_above=80)", "The chance of a mark above 80: 0.135 %. The R code that gives "
                                          "the same answer is printed too: pnorm(80, ...)."),
                ("dist.find_chance_that_value(is_between=[40, 60])", "68.3 %: about two in three are within one standard "
                                                  "deviation of the average."),
                ("dist.find_percentile(95)", "95 % of marks are below 66.4."),
                ("dist.find_cut_off(with_chance_above=0.025)", "The cut-off with a 2.5 % chance above it: 69.6. Tests use "
                                              "such cut-offs (critical values)."),
                ("chart = dist.draw_chart()", "A chart of the bell curve."),
                ('chart.save("lesson20_normal.png")', "Save it."),
            ]),
            ("A research question: pupils' days absent are counts (0, 1, 2 ...). Do they vary as a "
             "Poisson distribution expects, or more? The words that fit are fit_distribution_to and "
             "compare_distributions_for.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "180 pupils and their days absent."),
                ('table.compare_distributions_for("days_absent", distributions=("poisson", "negative binomial"))',
                 "Both are fitted by maximum likelihood and ranked by AIC: the negative binomial wins by 7, "
                 "so the counts vary more than Poisson allows."),
                ('fit = table.fit_distribution_to("days_absent", "negative binomial")',
                 "Fit it and keep the fitted distribution."),
                ("fit.find_chance_that_value(is_at_least=10)", "The chance a pupil misses 10 days or more: 0.66 %."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_histogram(x="days_absent", show="density")', "The counts, as shares."),
                ('chart.fit_distribution("negative binomial")', "The fitted chance of each count, on top."),
                ('chart.save("lesson20_absent.png")', "Save it."),
            ]),
            ("Values between points: you measured every two years, but you need 2001. find_values_at joins "
             "the dots (straight lines, or a smooth curve) and reads off the value; make_map_of does it across "
             "a whole map.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("growth"))', "Population every two years."),
                ('estimates = table.find_values_at("population", at={"year": [2001, 2011]}, for_each_group_in="country")',
                 "Straight lines between the known points (linear interpolation, as R approx()), for "
                 "each country."),
                ("estimates.show()", "A new table with the estimates."),
                ('island = sdata.table(sdata.get_example("island"))', "Heights measured on a 15 x 15 grid."),
                ('heights = island.make_map_of("height", across=["east", "north"], steps=60, '
                 'joined_by="smooth surface")', "A finer 60 x 60 map, with a smooth surface through every "
                                                "point (a thin-plate spline)."),
                ("chart = heights.start_chart()", "A chart of the new map."),
                ('chart.draw_contour(x="east", y="north", z="height")', "Its contour map."),
                ('chart.save("lesson20_map.png")', "Save it."),
            ]),
        ],
        notes=[
            "find_chance_that_value() gives back a share from 0 to 1 and prints it as a percent. is_above= and is_below= leave "
            "the value itself out, is_at_least= and is_at_most= keep it in, as in keep_rows_where. For counts that "
            "matters: is_at_most=3 means 3 or fewer.",
            "find_density_at() is the height of the curve, not a chance: a chance is an area under the curve, "
            "so ask find_chance_that_value(is_between=[...]).",
            "A fitted distribution is only as good as its fit. Compare a few with compare_distributions_for, "
            'and test the shape with table.compare_shape_to("column", "gamma").',
            "Values between points are estimates. Straight lines are the safe choice; a smooth curve can "
            'swing above or below the points (joined_by="curve without overshoot" never does). Outside '
            "the measured range the cells stay empty unless you ask for outside=.",
            "Names from other tools point to these words: pnorm and cdf to chance, qnorm and ppf to "
            "percentile, dnorm and pdf to find_density_at, interpolate and approx to find_values_at.",
        ],
        task=[
            'Ten coins are thrown. With sdata.distribution("binomial", tries=10, chance=0.5), what is the '
            "chance of 8 heads or more?",
            'Which fits the daily "sales" of the shop table best: normal, lognormal, gamma or weibull? Then '
            'check the best one with compare_shape_to.',
            "Try to remember without looking back: which word estimates a value between the points you "
            'measured? Use it to estimate the temperature of each city at month_number 6.5, joined by a '
            "smooth curve.",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                coins = sdata.distribution("binomial", tries=10, chance=0.5)
                coins.find_chance_that_value(is_at_least=8)"""),
             "5.47 %: 8, 9 or 10 heads happen about once in 18 tries."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("shop"))
                table.compare_distributions_for("sales")
                table.compare_shape_to("sales", "lognormal")"""),
             "Lognormal has the smallest AIC, and its shape could well fit (p = 0.65)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("weather"))
                estimates = table.find_values_at("temperature", at={"month_number": [6.5]},
                                            joined_by="smooth curve", for_each_group_in="city")
                estimates.show()"""),
             "find_values_at joins the months with a smooth curve and reads off each city at 6.5."),
        ],
        words=["sdata.distribution", "dist.find_chance_that_value", "dist.find_percentile", "dist.find_cut_off", "dist.draw_chart",
               "table.compare_distributions_for", "table.fit_distribution_to", "fit_distribution", "table.find_values_at",
               "table.make_map_of", "draw_curve"],
    ),
    dict(
        title="Working with a model: check it, compare it, predict with it",
        needs_r=needs_r_text("Only example 5, which you may leave out, needs R: find_model_averages_of() (R emmeans). The "
                             "rest of the lesson needs no R. find_model_averages_of() and the other R words"),
        learn=[
            "how to check a model from explain() with four pictures (check_model_of)",
            "how to find the rows that pull a model the most (show_rows_that_pull_model)",
            "how to ask whether a column helps a model (compare_models)",
            "how sure a prediction is, for the average and for one new row (add_predicted_column with interval=95)",
            "if you have R: the average of each group once the other columns are allowed for (find_model_averages_of)",
        ],
        parts=[
            ("explain() gives the effects, but they can only be trusted if the model suits the data. "
             "check_model_of draws the four pictures R users look at first.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The pupils of lesson 16."),
                ('table.explain("marks", using=["hours", "breakfast"])',
                 "The model to check: 2.82 more marks for each hour of study and 3.21 more with breakfast. "
                 "The line under the effects says how well it fits: AIC 1292 and BIC 1305, numbers that only "
                 "mean something when you compare two models."),
                ('charts = table.check_model_of("marks", using=["hours", "breakfast"])',
                 "Four pictures of the same model. Here the residuals lie in an even band around 0, the dots "
                 "follow the Q-Q line, the scale-location line is flat, and the dashed Cook's distance lines lie "
                 "outside the leverage picture: no row comes near them. The variance inflation factors are "
                 "1.00: hours and breakfast are not linked."),
                ('charts.save("lesson21_checks.png")', "Save the page of pictures."),
            ]),
            ("Some rows pull a model more than others. show_rows_that_pull_model lists them, the strongest "
             "first, so you can look at them before you trust the model.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.show_rows_that_pull_model("marks", using=["hours", "breakfast"])',
                 "12 of the 180 rows have a Cook's distance above the rule of thumb 4 / 180 = 0.0222. The "
                 "biggest, row 48 (0.0459), is far below 0.5, where the pictures draw the first dashed line: no "
                 "row pulls strongly. The table itself does not change."),
            ]),
            ("Does a column help? compare_models fits the model with and without it, on the same rows, "
             "and tests the difference.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.compare_models("marks", using=["hours"], against=["hours", "breakfast"])',
                 "Does breakfast help a model that already has hours? The F test: about 2 of 100 studies would "
                 "show this much if breakfast truly did not help (p = 0.018), and the AIC is 3.72 lower "
                 "with breakfast: keep it."),
                ('table.compare_models("marks", using=[["hours"], ["hours", "breakfast"], ["hours * breakfast"]])',
                 "Three models at once, as a list of lists (each inner list is one model): sorted by AICc, with "
                 "Akaike weights. Breakfast without the interaction comes first (weight 0.57); the interaction "
                 "is 1.07 higher, under 2, so about as good."),
            ]),
            ("A prediction is never exact. interval=95 says how sure the model is about the average; "
             "for_new_rows=True says where one new pupil would fall, which is much wider.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.add_predicted_column("marks", using=["hours", "breakfast"], name="average", interval=95)',
                 'Adds "average", the predicted marks, and the ends of its 95 % confidence interval, "average '
                 '95 % CI low" and "average 95 % CI high". name= gives the new columns short names.'),
                ('table.add_predicted_column("marks", using=["hours", "breakfast"], name="new pupil", '
                 "interval=95, for_new_rows=True)",
                 'The 95 % prediction interval, in "new pupil 95 % prediction low" and "... high".'),
                ('table.keep_columns(contains="95 %")', "Keep only the four ends of the two intervals."),
                ("table.show(rows=3)",
                 "For pupils like pupil 1 the model expects between 42.3 and 46.6 marks on average (44.5 in "
                 "the middle), but one new pupil like pupil 1 could score anything from 27.2 to 61.7."),
            ]),
            ("If you have R (you may leave this example out): find_model_averages_of gives the average of each "
             "group with the other columns held fixed, and compares every pair.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.find_model_averages_of("marks", for_each_group_in="breakfast", using=["hours", "school"])',
                 "With hours held at their average (5.00) and the 12 schools counted equally, pupils without "
                 "breakfast average 46.6 marks and pupils with breakfast 49.5. If the two groups truly did not "
                 "differ, a difference of -2.95 or bigger would turn up in about 1 of 100 studies like this one "
                 "(p = 0.008). This is R emmeans."),
                ('table.find_model_averages_of("marks", over_range_of="hours", using=["hours", "breakfast"])',
                 "One change: over_range_of= gives the model average at 50 values of hours, a table ready to draw "
                 "(the printout shows the two chart lines)."),
            ]),
        ],
        notes=[
            "The pupils of the school table come from 12 schools, and pupils of one school are alike, so the "
            "rows are not fully independent. These examples leave the schools out to stay short, so their "
            "p-values are a little too small; in a report, allow for the schools with grouped_by=\"school\" "
            "(lesson 16).",
            "Check before you trust: look at check_model_of's pictures before you read the p-values of explain().",
            'check_model_of(..., show="numbers") gives back the numbers it prints (variance inflation factors, the '
            "tests of equal spread) as a table; show_rows_that_pull_model gives back a table of the rows it found.",
            "For a yes/no or count model the first picture always shows bands of dots, one for each value; look "
            "at the smooth line, which should stay near 0.",
            "AIC and BIC compare models of the same rows only. sleep has 19 empty cells, so a model with sleep "
            "uses fewer rows; compare_models fits both models on the rows they share.",
            "A pseudo R squared (yes/no, counts) is not a share explained: 0 means no better than no columns.",
            "check_model_of also prints two tests of equal spread under picture 3 (notes only: judge by the "
            "picture), and for a yes/no model it adds a fifth picture, calibration, with the Hosmer-Lemeshow test "
            "and the Brier score.",
            "Remove a row that pulls only for a reason, such as a typing mistake, and say so in your report.",
            "The confidence interval (interval=95) is about the average of many pupils like this one; the "
            "prediction interval (for_new_rows=True) is about one pupil. The second is always wider.",
            # S3c-2: one "more" line (factor analysis stays in the manual, design 7.4)
            "More, with R: when many columns (the answers to a questionnaire, the scores of several tests) may "
            "measure a few hidden things, table.find_hidden_factors_behind([...]) finds how many and which columns "
            "go with which, and table.check_hidden_factors(measured_by={...}) checks a model you wrote down "
            "beforehand; read its fit guides as guides, not pass marks. Try them on sdata.get_example(\"ability_tests\").",
            # S3d-3: one "more" line (the Bayesian lesson teaches it)
            "More, with R: explain(..., test_method=\"bayesian\") fits the model the Bayesian way (R rstanarm): each effect with "
            "its credible interval, the prior printed, and R-hat to check the chains; check_model_of(..., "
            "test_method=\"bayesian\") draws the posterior predictive check.",
        ],
        task=[
            'Partly done for you: after import simplydata as sdata, the next two lines are '
            'table = sdata.table(sdata.get_example("school")) and table.check_model_of("marks", using=["hours", '
            '"breakfast"]). Write the last line yourself: does '
            '"sleep" help the model of "marks" that already has "hours" and "breakfast"?',
            'Check the model of "marks" using "hours" and "school" with check_model_of and show_rows_that_pull_model, '
            'then use compare_models to ask whether adding "breakfast" to it helps.',
            "Try to remember without looking back: which word adds a prediction with its interval, and which "
            'option gives the interval for one new row? Use them to predict "marks" from "hours" and "sleep", '
            "and look at the first 3 rows.",
            'If you have R: find the model averages of "marks" for each "school", allowing for "hours". Which '
            "school has the highest average and which the lowest, and how many pairs of schools differ?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.check_model_of("marks", using=["hours", "breakfast"])
                table.compare_models("marks", using=["hours", "breakfast"], against=["hours", "breakfast", "sleep"])"""),
             "Yes: on the 161 rows with every value, sleep helps (F = 10.2, p = 0.002) and the AIC drops by "
             "8.17."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                charts = table.check_model_of("marks", using=["hours", "school"])
                charts.save("model_checks.png")
                table.show_rows_that_pull_model("marks", using=["hours", "school"])
                table.compare_models("marks", using=["hours", "school"], against=["hours", "school", "breakfast"])"""),
             "The pictures look fine, and no row comes near the Cook's distance lines (the largest is 0.0457, "
             "row 97). Adding breakfast helps: F = 7.13, p = 0.008, and the AIC drops by 5.57."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.add_predicted_column("marks", using=["hours", "sleep"], interval=95, for_new_rows=True)
                table.keep_columns(contains="predicted")
                table.show(rows=3)"""),
             "add_predicted_column with interval=95 and for_new_rows=True; keep_columns(contains=\"predicted\") "
             "keeps the three new columns, and show(rows=3) shows the first 3 rows with every column. Pupil 1 is predicted 46.9, but one pupil "
             "like this could score from 29.8 to 64.0. Pupil 2 has no sleep value, so its cells stay empty."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.find_model_averages_of("marks", for_each_group_in="school", using=["hours"])"""),
             "With hours held at their average (5.00), School D has the highest average mark (57.7) and School C "
             "the lowest (36.5). 22 of the 66 pairs of schools differ after Tukey's adjustment (p < 0.05). "
             "This needs R (emmeans)."),
        ],
        words=["table.check_model_of", "table.show_rows_that_pull_model", "table.compare_models",
               "table.add_predicted_column", "table.find_model_averages_of", "table.explain"],
    ),
    dict(
        title="Risks, diagnostic tests and agreement",
        needs_r=needs_r_text("Examples 1 to 4 and the tasks need no R. The optional examples 5 to 8 (a score and "
                             "its trade-off curve, two devices, a questionnaire, risks allowing for age)",
                             packages=("pROC", "BlandAltmanLeh", "DescTools", "psych", "epiR")),
        learn=[
            "how to compare risks: in absolute terms first (out of 100), then as ratios, and how to draw them",
            "how good a test is, in counts of 1000 people: what it finds, what it misses, and its false alarms",
            "why the share of positive results that are real depends on how common the condition is",
            "how to measure agreement between two raters, which is not the same as correlation",
            "optional, for later: scores and their trade-off curves, devices, questionnaires and rates",
        ],
        parts=[
            ("Did patients catch an infection in hospital more often in one ward? Absolute risks come first, then "
             "the ratios.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "200 made-up patients in two hospital wards."),
                ('table.compare_risks("caught_infection", for_each_group_in="ward", against="ward A")',
                 "4 of 100 caught an infection in ward A and 16 of 100 in ward B: out of 100, about 12 more in "
                 "ward B, and the interval of the difference (3.70 to 20.8 points) leaves out 0. For every 9 "
                 "patients in ward B instead of ward A, one infection more. Then the risk ratio (4.00) and the "
                 "odds ratio (4.57), and p = 0.010."),
            ]),
            ("The answer is also a table, one row per measure, so the ratios can be drawn: each as a dot with its "
             "interval (a forest plot).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "The clinic table."),
                ('risks = table.compare_risks("caught_infection", for_each_group_in="ward", against="ward A")',
                 "The same comparison as in example 1, kept as a table named risks."),
                ('risks.keep_rows_where("measure", is_one_of=["risk ratio", "odds ratio"])', "Keep the two ratios."),
                ("chart = risks.start_chart()", "Start a chart of the result table."),
                ('chart.draw_forest_plot(x="estimate", y="measure")',
                 "Each ratio as a dot with its 95 % interval, on a log scale, with a line at 1 (no effect). Both "
                 "intervals lie above the line."),
                ('chart.save("risk_ratios.png")', "Save it."),
            ]),
            ("How good is a quick test, against the truth from a slow lab test?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "50 of the 200 patients have the infection."),
                ('table.compare_to_truth("rapid_test", truth="infected")',
                 "Of 1000 people like these, 250 have it: the test finds 195 (sensitivity 78 %) and misses 55. "
                 "Of the 750 without it, 50 test positive by mistake (specificity 93.3 %)."),
                ('table.compare_to_truth("rapid_test", truth="infected", prevalence=1)',
                 "Where only 1 % have it, the same test gives 74 positives in 1000 people, and only 8 of them "
                 "really have it: most positives are false alarms."),
            ]),
            ("Do a nurse and a doctor agree on how ill each patient looks?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "The clinic table."),
                ('table.agreement_between("nurse_rating", "doctor_rating")',
                 "They agree on 136 of 200 patients (68 %); by chance alone they would agree on about 34 %. "
                 "Cohen's kappa = 0.516: they agree about half of the way from chance to perfect."),
            ]),
            ("More, optional (needs R): a score such as CRP has no single cut-off; each cut-off trades found "
             "cases against false alarms.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "The clinic table."),
                ('table.compare_to_truth("crp", truth="infected")',
                 "AUC 0.893: a person who has it scores higher than one who does not in 89 of 100 such pairs. "
                 "The best cut-off by Youden's index is 2.15."),
                ('table.compare_accuracy("crp", "procalcitonin", truth="infected")',
                 "AUC 0.893 against 0.715, a difference of 0.177 (0.085 to 0.270), on the same patients: CRP "
                 "tells better who has it (DeLong's test, p = 0.0002)."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_trade_off_curve(score=["crp", "procalcitonin"], truth="infected")',
                 "Both trade-off (ROC) curves: CRP climbs faster to the top left than procalcitonin."),
                ('chart.save("trade_off.png")', "Save it."),
            ]),
            ("More, optional (needs R): do two blood-pressure devices agree?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "The clinic table."),
                ('table.limits_of_agreement("device_a", "device_b")',
                 "Device A reads on average 2.18 lower, and 95 % of the differences lie between -11.7 and 7.33."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_difference_dots(first="device_a", second="device_b")',
                 "The Bland-Altman chart: each difference (first minus second) against the average of the two, "
                 "with the limits of agreement."),
                ('chart.save("devices.png")', "Save it."),
            ]),
            ("More, optional (needs R): do five questions on satisfaction with care (item_1 to item_5) hang "
             "together?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "The clinic table."),
                ('table.reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])',
                 "Cronbach's alpha = 0.865 (0.833 to 0.893); leaving out any one item lowers it."),
            ]),
            ("More, optional: risks allowing for a third column, and rates per patient-day.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "The clinic table."),
                ('table.compare_risks("infected", for_each_group_in="ward", allowing_for="age_group")',
                 "Mantel-Haenszel odds ratio 1.76 (0.911 to 3.40), about the same as 1.71 without allowing for "
                 "age (the interval of its risk ratio needs R epiR)."),
                ('table.rate_of("infections", time="patient_days", for_each_group_in="ward")',
                 "2.22 infections per 1000 patient-days in ward A and 10.0 in ward B, each with its exact "
                 "interval; compare_rates compares them."),
            ]),
        ],
        notes=[
            "This lesson is optional, for the life sciences (medicine, biology, ecology); no other lesson "
            "needs it. Examples 1 to 4 are the core; examples 5 to 8 are more, for when you need them.",
            "Give absolute risks first. A risk ratio of 0.5 can mean 2 in 100 instead of 4, or 20 instead of "
            "40: the same ratio, a very different number of people helped.",
            "When the interval of the difference includes 0, the number needed for one event fewer (or more) "
            "has an interval that runs through infinity: the data fit fewer events, no change and more. Task 1 "
            "shows one.",
            "Odds are not risks. When the outcome is common (over 10 %), the odds ratio lies further from 1 than "
            "the risk ratio, so say which one you report.",
            "Sensitivity and specificity belong to the test; the share of positives that are real also depends "
            "on how common the condition is. Counts of 1000 people make this easy to see.",
            "Agreement is not correlation: two raters (or devices) can rise and fall together and still differ "
            "every time.",
            'More: compare_risks(..., show="attributable fractions") gives the share of the events that goes with the '
            'exposure; rate_of(..., allowing_for="age_band", standard_population="whole table") gives age-standardised '
            'rates and compare_rates(..., allowing_for="age_band", standard_rates=...) observed / expected (SMR), '
            'with sdata.get_example("deaths_by_age"); compare_averages_of(..., matched_by="subject", period="period", '
            'same_within=[0.8, 1.25]) is the bioequivalence crossover (sdata.get_example("drug_levels")).',
        ],
        task=[
            'Compare the risk of "infected" between the wards, against "ward A". Does the interval of the '
            "difference leave out 0?",
            "How good is the rapid test where only 2 % have the infection? Of the positive results, how many "
            "really have it?",
            'Complete the started lines to draw the two ratios of task 1: risks = table.compare_risks("infected", '
            'for_each_group_in="ward", against="ward A"), then risks.keep_rows_where("measure", is_one_of=[...]), then '
            "chart = risks.start_chart() and chart.draw_forest_plot(...).",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("clinic"))
                table.compare_risks("infected", for_each_group_in="ward", against="ward A")"""),
             "About 10 more in 100 in ward B, but the interval of the difference, -2.02 to 21.7 points, includes "
             "0, so the data cannot tell (p = 0.142); the number needed runs through infinity."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("clinic"))
                table.compare_to_truth("rapid_test", truth="infected", prevalence=2)"""),
             "Of 1000 people, 20 have it; the test finds 16 but 65 test positive by mistake, so only 16 of the 81 "
             "positives (about 1 in 5) are real."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("clinic"))
                risks = table.compare_risks("infected", for_each_group_in="ward", against="ward A")
                risks.keep_rows_where("measure", is_one_of=["risk ratio", "odds ratio"])
                chart = risks.start_chart()
                chart.draw_forest_plot(x="estimate", y="measure")
                chart.save("infected_ratios.png")"""),
             "Both intervals cross the line at 1, as the interval of the difference includes 0."),
        ],
        words=["table.compare_risks", "draw_forest_plot", "table.compare_to_truth", "table.agreement_between",
               "draw_trade_off_curve", "table.compare_accuracy", "table.limits_of_agreement", "draw_difference_dots",
               "table.reliability_of", "table.rate_of"],
    ),
    dict(
        title=TIME_SERIES_LESSON,
        learn=[
            "how to make a run of dates, and add the days that are missing from a daily table",
            "how to average over a window of time, such as the last 7 days",
            "how to smooth a noisy series, and test whether it has a trend",
        ],
        needs_r=needs_r_text("find_trend_of() and its test", packages=("trend",)),
        parts=[
            ("Time series are readings in time order: one a day, a month or a second. A run of dates is the "
             "backbone of such a table.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('days = sdata.make_run_of_dates("2026-01-01", to="2026-12-31", every="month")',
                 "12 dates, the first of each month of 2026, in a table with one column, date."),
                ("days.show()", "Show them."),
            ]),
            ("Two river stations measured the water level and nitrate every day for two years, but some days "
             "are missing: their rows are simply not there. Words that need even steps stop with a message, so "
             "add the missing days first and fill them in.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("river"))', "Daily date, station, level and nitrate."),
                ('table.add_missing_dates("date", every="day", for_each_group_in="station")',
                 "15 days were missing (6 at Station A, 9 at Station B); their rows are added with empty cells."),
                ('table.fill_empty_cells_in("nitrate", with_the="line between neighbours", sorted_by="date", '
                 'for_each_group_in="station")',
                 "The 15 empty nitrate cells get the value on the straight line between their neighbours."),
                ('table.fill_empty_cells_in("level", with_the="line between neighbours", sorted_by="date", '
                 'for_each_group_in="station")',
                 "The same for the level: 23 cells (a few were empty already)."),
            ]),
            ("Daily readings are noisy. A time window averages the readings of the last 7 days; a smoother "
             "averages the readings on both sides of each day.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("river"))', "The river table."),
                ('table.add_missing_dates("date", every="day", for_each_group_in="station")', "Add the missing days."),
                ('table.fill_empty_cells_in("nitrate", with_the="line between neighbours", sorted_by="date", '
                 'for_each_group_in="station")', "Fill them in."),
                ('table.add_rolling_column("week_average", from_column="nitrate", window="7 days", '
                 'sorted_by="date", for_each_group_in="station")',
                 "Each week_average is the average nitrate of the 7 days up to that day, for each station."),
                ('table.add_smoothed_column("nitrate_smoothed", from_column="nitrate", test_method="moving average", '
                 'window=31, sorted_by="date", for_each_group_in="station")',
                 "A moving average over 31 days centred on each day; the first and last 15 days have no full "
                 "window, so they are empty (as R stats::filter(x, rep(1 / 31, 31), sides = 2))."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_lines(x="date", y="nitrate_smoothed", colour="station")',
                 "The smoothed nitrate, one line per station: Station A creeps up, Station B goes down."),
                ('chart.save("nitrate.png")', "Save it."),
            ]),
            ("Is there a steady trend? find_trend_of gives the slope (Sen's slope, the middle of the "
             "slopes between all pairs of days) and the Mann-Kendall test.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("river"))', "The river table."),
                ('table.find_trend_of("nitrate", sorted_by="date", for_each_group_in="station")',
                 "Station A rises by 0.0708 a year (p = 0.003); Station B falls by 0.927 a year (p < 0.0001). "
                 "R's trend::sens.slope() and trend::mk.test() give the same numbers."),
            ]),
        ],
        notes=[
            "sorted_by= is the time column: it gives the order and the time between readings. for_each_group_in= gives "
            "one series per group, here one per station.",
            "window=7 is 7 rows; window=\"7 days\" is 7 days of time, whatever the number of rows.",
            "find_trend_of needs no even steps and no filling: empty cells are left out.",
        ],
        task=[
            "Make a run of dates for every day of March 2026.",
            "Add a column with the average level of the last 30 days at each station.",
            "Smooth the level of each station with a moving average over 61 days instead of 31, and draw it. "
            "What does the wider window do?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                days = sdata.make_run_of_dates("2026-03-01", to="2026-03-31", every="day")
                days.show()"""),
             "31 dates, one a day."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("river"))
                table.add_rolling_column("month_level", from_column="level", window="30 days", sorted_by="date", for_each_group_in="station")
                table.show_first_rows()"""),
             "A time window works even with missing days: it counts days, not rows."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("river"))
                table.add_missing_dates("date", every="day", for_each_group_in="station")
                table.fill_empty_cells_in("level", with_the="line between neighbours", sorted_by="date", for_each_group_in="station")
                table.add_smoothed_column("level_smoothed", from_column="level", window=61, sorted_by="date", for_each_group_in="station")
                chart = table.start_chart()
                chart.draw_lines(x="date", y="level_smoothed", colour="station")
                chart.save("level_smoothed.png")"""),
             "The wider window gives a calmer line that hides the shorter ups and downs, and now the first and "
             "last 30 days of each station are empty."),
        ],
        words=["sdata.make_run_of_dates", "table.add_missing_dates", "table.fill_empty_cells_in", "table.add_rolling_column",
               "table.add_smoothed_column", "table.find_trend_of", "draw_lines"],
    ),
    dict(
        title=FORECASTS_LESSON,
        learn=[
            "how to draw a series over time, and each year on top of the others (a seasonal chart)",
            "how to forecast the next months, starting from the simplest forecast",
            "how to check a forecast on months it has not seen before trusting it",
        ],
        needs_r=needs_r_text("forecast() and compare_forecasts_for()", packages=("forecast",)),
        parts=[
            ("Two museums counted their visitors every month for twelve years. A chart over time comes first: "
             "it shows the trend and the season at a glance.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("visitors"))', "Monthly visitors to two made-up museums, "
                                                                   "2014 to 2025: month, museum, visitors."),
                ("chart = table.start_chart()", "Start a chart of the table."),
                ('chart.draw_lines(x="month", y="visitors", colour="museum")',
                 "One line per museum: both rise year after year, with a peak every summer."),
                ('chart.save("visitor_lines.png")', "Save it."),
            ]),
            ("A seasonal chart puts each year on top of the others, January to December. It needs no new word: "
             "take the month and the year out of the date, then draw one line per year.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("visitors"))', "The visitors table."),
                ('table.keep_rows_where("museum", is_equal_to="Harbour Museum")', "Keep one museum: 144 of 288 rows."),
                ('table.add_column_with_part_of_date("month_name", from_column="month", part="month")',
                 "The month of each date."),
                ('table.add_column_with_part_of_date("year", from_column="month", part="year")', "The year of each date."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_lines(x="month_name", y="visitors", colour="year")',
                 "Twelve lines, one per year, all with the same summer peak; later years lie higher."),
                ('chart.save("visitor_seasons.png")', "Save it."),
            ]),
            ("Start with the simplest forecast: every future month is the last value. Any better method must "
             "beat it.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("visitors"))', "The visitors table."),
                ('table.forecast("visitors", sorted_by="month", steps_ahead=12, test_method="last value", '
                 'for_each_group_in="museum")',
                 "Harbour Museum: 2072 every month (95 % prediction interval 1746 to 2398 next month, 944 to 3200 in a "
                 "year). The printout warns that the errors still hold a pattern: the season is missed."),
            ]),
            ("Exponential smoothing (Holt-Winters) follows the level, the trend and the season. Before "
             "trusting it, hold back the last year, forecast it from the years before, and see how far off it "
             "is.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("visitors"))', "The visitors table."),
                ('table.forecast("visitors", sorted_by="month", steps_ahead=12, repeats_every="year", '
                 'check_on_last=12, for_each_group_in="museum")',
                 "Fitted on all but the last 12 months, it was off by 64.7 visitors a month on average at the "
                 "Harbour Museum (2.93 %) and 21.5 at the Hill Gallery (2.20 %)."),
                ('table.compare_forecasts_for("visitors", sorted_by="month", repeats_every="year", for_each_group_in="museum")',
                 "Four methods on the same held-back year: exponential smoothing is best for both museums (MASE "
                 "0.469 and 0.348; below 1 is better than repeating last year's month)."),
            ]),
            ("Now forecast the next year from all the data, and draw it after the lines.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("visitors"))', "The visitors table."),
                ('table.forecast("visitors", sorted_by="month", steps_ahead=12, repeats_every="year", '
                 'for_each_group_in="museum")',
                 "Harbour Museum next month: 2016 visitors (95 % prediction interval 1887 to 2146); Hill "
                 "Gallery: 947 (887 to 1008). R's HoltWinters() and forecast() give the same numbers."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_lines(x="month", y="visitors", colour="museum")', "The data, one line per museum."),
                ('chart.draw_forecast(steps_ahead=12, repeats_every="year")',
                 "The forecast as a dashed line after the data, with its interval band."),
                ('chart.save("visitor_forecast.png")', "Save it."),
            ]),
        ],
        notes=[
            "repeats_every=\"year\" turns into 12 rows for monthly data (7 for \"week\" with daily data).",
            "A prediction interval says where the next values will probably fall. It widens the further ahead "
            "you look.",
            "check_on_last=12 holds back the last 12 readings: a forecast is only as good as its check on data "
            "it has not seen.",
            'More: test_method="arima", order="automatic" lets R auto.arima choose the ARIMA order; the printout '
            "names the order, and the intervals are a little too narrow because the order was chosen from the "
            "same data.",
        ],
        task=[
            "Forecast the Harbour Museum with test_method=\"same season last time\". How does it compare with "
            "exponential smoothing?",
            "Check the \"straight on\" method (the line from the first reading to the last) on the last 12 months "
            "of the Hill Gallery.",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("visitors"))
                table.keep_rows_where("museum", is_equal_to="Harbour Museum")
                table.forecast("visitors", sorted_by="month", steps_ahead=12, repeats_every="year", test_method="same season last time")"""),
             "It repeats last year's months, so it misses the rise; compare_forecasts_for showed it is about twice "
             "as far off as exponential smoothing (MASE 1.38 against 0.693)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("visitors"))
                table.keep_rows_where("museum", is_equal_to="Hill Gallery")
                table.forecast("visitors", sorted_by="month", steps_ahead=12, test_method="straight on", check_on_last=12)"""),
             "It follows the rise but not the season: far worse than exponential smoothing (MASE 3.08 against "
             "0.515 in compare_forecasts_for, which scales by the error of the same season last time)."),
        ],
        words=["draw_lines", "table.add_column_with_part_of_date", "table.forecast", "table.compare_forecasts_for", "draw_forecast"],
    ),
    dict(
        title=CYCLES_LESSON,
        learn=[
            "how to find the repeating cycles in a recording, and how strong each is (the spectrum)",
            "how to take out a hum, or keep only the slow cycles (filters)",
            "how to find the peaks and the dips of a signal",
            "more, if you want it: a smoother spectrum (Welch), and whether a series stays steady",
        ],
        needs_r=needs_r_text("Only the last part, check_steady_over_time() and its two tests,", packages=("tseries", "urca")),
        parts=[
            ("A sensor gives 200 readings a second for 5 seconds. Which cycles does its signal hold? The "
             "spectrum splits a recording into its frequencies, like a prism splits light into colours.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("sensor"))', "Five seconds of a made-up sensor: time in "
                                                                 "seconds, signal and vibration."),
                ('table.find_spectrum_of("signal", sorted_by="time")',
                 "The strongest cycle has frequency 5 per second (it repeats every 0.2 seconds); next come 20 "
                 "per second and a 50-per-second hum."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_spectrum("signal", sorted_by="time")',
                 "The same numbers as a chart: power against frequency on a log scale, the three strongest "
                 "cycles labelled with how often they repeat."),
                ('chart.save("spectrum.png")', "Save it."),
            ]),
            ("A filter keeps some frequencies and removes others. remove_at=50 takes out the hum; keep_below=10 "
             "keeps only the slow cycles.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("sensor"))', "The sensor table."),
                ('table.add_filtered_column("no_hum", from_column="signal", remove_at=50, sorted_by="time")',
                 "A notch filter at 50 per second, run forwards and backwards so nothing moves in time."),
                ('table.find_spectrum_of("no_hum", sorted_by="time")',
                 "The hum is gone: now only 5 per second and 20 per second are named."),
                ('table.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")',
                 "A Butterworth low-pass filter (steepness 4), as R signal::filtfilt(signal::butter(4, 0.1), x)."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_lines(x="time", y="signal")', "The raw signal."),
                ('chart.draw_lines(x="time", y="slow")', "The slow part only: a clean 5-per-second wave."),
                ("chart.set_range_x(0, 1)", "Show the first second."),
                ('chart.save("filter.png")', "Save it."),
            ]),
            ("Peaks are readings higher than both neighbours; dips are readings lower than both. Conditions "
             "keep only the ones that matter.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("sensor"))', "The sensor table."),
                ('table.find_each_peak_that("signal", sorted_by="time", is_at_least=2.5)',
                 "One peak is at least 2.5 high: 3.48 at time 3.885, a spike. R's pracma::findpeaks() finds the "
                 "same."),
                ('table.find_each_dip_that("signal", sorted_by="time", is_at_most=-2)',
                 "find_each_dip_that is find_each_peak_that upside down: one dip goes down to -2 or lower, -2.36 at time 0.94."),
                ("chart = table.start_chart()", "Start a chart."),
                ('chart.draw_lines(x="time", y="signal")', "The signal."),
                ("chart.draw_peak_dots(is_at_least=2.5)", "A mark on the peak."),
                ('chart.save("peaks.png")', "Save it."),
            ]),
            ("More (if you want it): Welch's method averages the spectra of overlapping pieces of the "
             "recording. The spectrum is smoother but coarser.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("sensor"))', "The sensor table."),
                ('table.find_spectrum_of("signal", sorted_by="time", test_method="welch", window=200)',
                 "Pieces of 200 readings with half overlap: the same three cycles stand out (5, 20 and 50 per "
                 "second)."),
            ]),
            ("More (if you want it; needs R): some forecasts (ARIMA) assume the series is steady: the same "
             "average and spread all the way through. check_steady_over_time runs two tests that start from opposite "
             "assumptions and gives one answer: steady, wanders, or close to the edge.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("sensor"))', "The sensor table."),
                ('table.check_steady_over_time("signal", sorted_by="time")',
                 "The signal looks steady: it stays around a steady level (both tests agree: ADF p < 0.0001, "
                 "KPSS p = 0.095); both ask whether it stays around one level, as R urca::ur.df(type = \"drift\") "
                 "and tseries::kpss.test()."),
            ]),
        ],
        notes=[
            "Frequencies are counted per unit of the sorted_by column: per second here. For a list of numbers "
            "give time_step= (nums.find_spectrum(time_step=0.005)).",
            "The powers times the frequency step add up to the variance (SciPy's density scaling). R's "
            "spec.pgram() gives half these powers (it spreads them over negative frequencies too).",
            "A recording can only show frequencies up to half its readings per second: 100 per second here.",
            "Filters run both ways by default, so nothing moves in time. both_ways=False runs forwards only, "
            "as a live instrument would. sdata.frequency_filter(keep_below=10, time_step=0.005) gives the filter "
            "itself, to look at with .chart().",
            "ADF starts from \"it wanders\" (a small p-value says steady); KPSS starts from \"steady\" (a "
            "small p-value says it wanders). The first line of the printout gives the answer in words.",
        ],
        task=[
            'Which cycle is strongest in the "vibration" column? Is it the same as in "signal"?',
            "Keep only the frequencies between 15 and 25 in the signal. Which cycle is left?",
            "Find the dips of the signal that go down to -1.5 or lower. Is the lowest one still the same?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("sensor"))
                table.find_spectrum_of("vibration", sorted_by="time")"""),
             "The same: 5 per second, then 20 per second and the 50-per-second hum. "
             "The vibration follows the signal, a little later."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("sensor"))
                table.add_filtered_column("middle", from_column="signal", keep_between=[15, 25], sorted_by="time")
                table.find_spectrum_of("middle", sorted_by="time")"""),
             "Only the 20-per-second cycle is left: it is the strongest cycle of the new column."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("sensor"))
                table.find_each_dip_that("signal", sorted_by="time", is_at_most=-1.5)"""),
             "Many more dips now, each with its time and value; the lowest is still -2.36 at time 0.94."),
        ],
        words=["table.find_spectrum_of", "draw_spectrum", "table.add_filtered_column", "table.find_each_peak_that", "table.find_each_dip_that",
               "draw_peak_dots", "table.check_steady_over_time"],
    ),
    dict(
        title=SYSTEMS_LESSON,
        learn=[
            "that a filter is a system, and how to write down a system of your own (a spring and damper)",
            "whether a system is stable, from its poles, and how it answers a step (overshoot, settling time)",
            "how a feedback loop with a controller changes the answer",
            "more, if you want it: the Bode chart and the margins, and a system in steps for a computer",
        ],
        parts=[
            ("This lesson is optional, for engineering. It starts from the filter of the cycles lesson: a "
             "filter is a system, something that turns an input (the raw signal) into an output.", [
                ("import simplydata as sdata", "Load simplydata."),
                ("low_pass = sdata.frequency_filter(keep_below=10, time_step=0.005)",
                 "The filter of add_filtered_column(keep_below=10) as a system: it prints its formula and its "
                 "poles. All poles lie inside the unit circle, so it is stable: its output settles."),
                ("low_pass.frequency_response(between=[1, 50])",
                 "How much of each frequency gets through: all of 1 per second (gain 1), almost nothing of 50 "
                 "per second (gain 0.0006)."),
                ("chart = low_pass.chart()", "The gain and the phase against frequency (a Bode chart)."),
                ('chart.save("low_pass.png")', "Save it."),
            ]),
            ("A weight on a spring with a damper: push it with a force and it moves. Its output (the position) "
             "over its input (the force) is 1 / (s**2 + 0.8*s + 4). s stands for \"how fast it changes\": s "
             "times the position is its speed.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('spring = sdata.system("1 / (s**2 + 0.8*s + 4)")',
                 "Poles -0.4 +/- 1.96i: stable, because every pole has a negative real part. A constant force "
                 "of 1 settles at 0.25. R: control::tf(1, c(1, 0.8, 4))."),
                ("spring.poles()", "The table of poles: damping ratio 0.2 (lightly damped), natural frequency 2."),
                ('chart = spring.chart(show="poles and zeros")',
                 "The poles as x on the plane of real and imaginary parts: both lie left of the line, so the "
                 "spring is stable."),
                ('chart.save("spring_poles.png")', "Save it."),
                ("spring.step_response(until=15)",
                 "It overshoots by 52.6 % (peak 0.3815 at time 1.58), rises in 0.60 and settles within 2 % "
                 "after 9.9. R's control::step() gives the same response."),
                ('chart = spring.chart(show="step", until=15)', "The step response as a chart."),
                ('chart.save("spring_step.png")', "Save it."),
            ]),
            ("A controller measures the position, compares it with the target and pushes. This one pushes by 2 "
             "x the error plus 2 x the error added up over time: 2 * (s + 1) / s.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('spring = sdata.system("1 / (s**2 + 0.8*s + 4)")', "The spring."),
                ('controller = sdata.system("2 * (s + 1) / s")', "The controller."),
                ("loop = controller.then(spring).with_feedback()",
                 "The controller, then the spring, with the position fed back: (2*s + 2) / (s**3 + 0.8*s**2 + "
                 "6*s + 2), as R control::feedback()."),
                ("loop.step_response(until=30)",
                 "Now the position settles at the target, 1 (without the controller it settled at 0.25), with "
                 "only 1.5 % overshoot."),
            ]),
            ("More (if you want it): the frequency response says how much of each frequency gets through (the "
             "gain) and how late (the phase). The frequencies of systems are in radians per second, as R "
             "control and SciPy: 2 radians per second is 0.32 cycles per second.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('spring = sdata.system("1 / (s**2 + 0.8*s + 4)")', "The spring."),
                ("spring.frequency_response(between=[0.1, 10])",
                 "-12.02 decibels at 0.1 radians per second, -39.68 at 10; R's control::bode() gives the same."),
                ("chart = spring.chart(between=[0.1, 10])",
                 "The Bode chart: a peak near 2 radians per second, where the spring rings."),
                ('chart.save("spring_bode.png")', "Save it."),
                ('controller = sdata.system("2 * (s + 1) / s")', "The controller."),
                ("controller.then(spring).frequency_response()",
                 "Before closing the loop: gain margin 18.06 decibels and phase margin 32.98 degrees. The loop "
                 "could take about 8 times the gain, or 33 degrees more delay, before it stopped settling."),
            ]),
            ("More (if you want it): a computer reads and acts in steps. in_steps turns the system into one "
             "that works every 0.1 seconds.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('spring = sdata.system("1 / (s**2 + 0.8*s + 4)")', "The spring."),
                ("digital = spring.in_steps(time_step=0.1)",
                 "(0.00485317*z + 0.0047253) / (z**2 - 1.8848*z + 0.923116), as R control::c2d(sys, 0.1)."),
                ("response = digital.step_response(until=15)",
                 "Almost the same answer as before: overshoot 52.7 %, settling time 9.9."),
                ("chart = response.start_chart()", "The response is a table, so it can be drawn like any other."),
                ('chart.draw_lines(x="time", y="output", joined_by="steps")',
                 "Each value holds until the next step, as the computer sees it."),
                ('chart.save("spring_in_steps.png")', "Save it."),
            ]),
        ],
        notes=[
            "This lesson is optional: no other lesson needs it.",
            "A system can be written as a formula, as numerator= and denominator= (highest power first), as "
            "poles= and zeros=, or as matrices a=, b=, c=, d=.",
            "Frequencies of systems are in radians per second, as R control and SciPy; unit=\"cycles per "
            "second\" gives cycles per second. A filter from sdata.frequency_filter is in cycles per second.",
            "R's control package has no stepinfo() or margin(): the rise time, settling time, overshoot and "
            "margins come from python-control (step_info, stability_margins), the Python package for control "
            'systems. Install it with pip install "simplydata[systems]"; without it the responses still come.',
        ],
        task=[
            "Make the damper stronger: 1 / (s**2 + 2*s + 4). What happens to the overshoot?",
            "Use a controller that only pushes in proportion to the error, sdata.system(\"10\"). Where does the "
            "position settle?",
            "Draw the poles and zeros of the closed loop of part 3.",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                spring = sdata.system("1 / (s**2 + 2*s + 4)")
                spring.step_response(until=15)"""),
             "Damping ratio 0.5 instead of 0.2: the overshoot drops to about 16 %."),
            (_sx("""\
                import simplydata as sdata
                spring = sdata.system("1 / (s**2 + 0.8*s + 4)")
                loop = sdata.system("10").then(spring).with_feedback()
                loop.step_response(until=30)"""),
             "It settles at 0.714, not at 1: a push in proportion to the error always leaves some error. The "
             "part that adds up the error over time removes it."),
            (_sx("""\
                import simplydata as sdata
                spring = sdata.system("1 / (s**2 + 0.8*s + 4)")
                loop = sdata.system("2 * (s + 1) / s").then(spring).with_feedback()
                chart = loop.chart(show="poles and zeros")
                chart.save("loop_poles.png")"""),
             "Three poles, all left of the imaginary axis (stable), and one zero at -1."),
        ],
        words=["sdata.frequency_filter", "sdata.system", "system.poles", "system.chart", "system.step_response",
               "system.then", "system.with_feedback", "system.frequency_response", "system.in_steps"],
    ),
    dict(
        title=OUTLIERS_LESSON,
        needs_r=needs_r_text("Only the second part and the third task (for_percentile=, R quantreg)",
                             packages=("quantreg",)),
        learn=[
            "how a few rows far from the rest pull an ordinary model towards them",
            "how to give those rows less weight (robust regression, Huber's method)",
            "how giving_outliers_less_weight= differs from robust_errors=",
            "how to fit the line under which 90 % (or 10 %) of the values fall: a percentile line",
        ],
        parts=[
            ("A least-squares line counts every row the same, so a few rows far from the rest pull it towards "
             "them. Robust regression gives those rows less weight, so they pull less.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "Pupils in 12 schools (lesson 16)."),
                ('table.explain("marks", using=["hours", "breakfast"])',
                 "The ordinary model (least squares, as in lesson 16): each extra hour of study goes with about "
                 "2.8 more marks."),
                ('table.explain("marks", using=["hours", "breakfast"], giving_outliers_less_weight=True)',
                 "The same model with Huber's weights: rows far from the line count less. The effect of study "
                 "hardly moves (2.87), and the printout lists the rows given less weight, by their row number. "
                 "Say in words what that means: no few pupils decide the answer here."),
                ('table.explain("marks", using=["hours", "breakfast"], robust_errors=True)',
                 "Not the same thing: robust_errors=True keeps the effects of the ordinary model (2.82) and only "
                 "changes their standard errors, so the intervals stay right when the spread is not the same "
                 "everywhere. Outliers still pull."),
            ]),
            ("If you have R: the average line says nothing about the edges. A percentile line is the line under "
             "which a share of the values fall: the 90th percentile line has 90 % of the marks below it, at each "
             "number of hours. In ecology the edges are often the question (the most a habitat can hold).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table again."),
                ('table.explain("marks", using=["hours"], for_percentile=90)',
                 "The 90th percentile line (R quantreg): each extra hour goes with 3.03 more marks at the top of "
                 "the class. Say in words what that 3.03 means."),
                ('table.explain("marks", using=["hours"], for_percentile=[10, 50, 90])',
                 "One block per percentile: 2.78 at the bottom, 2.84 in the middle (the median line) and 3.03 at "
                 "the top. Lines that are about parallel mean study helps the weak and the strong alike."),
            ]),
        ],
        notes=[
            "The pupils of the school table come from 12 schools, and pupils of one school are alike, so the "
            "rows are not fully independent. These examples leave the schools out to stay short, so their "
            "p-values are a little too small; in a report, allow for the schools with grouped_by=\"school\" "
            "(lesson 16).",
            "giving_outliers_less_weight=True changes the effects (rows far from the model count less); "
            "robust_errors=True keeps the effects and changes only their standard errors. Choose by the problem: "
            "outliers, or a spread that is not the same everywhere.",
            "Huber's method resists outliers in the column you explain, not unusual values in the using= columns "
            "(far-out hours, for example). table.show_rows_that_pull_model() finds those.",
            "A row given less weight is not wrong: look at it before you decide anything. Say in your report that "
            "you used robust regression (Huber's M-estimation, as R MASS::rlm()).",
            "for_percentile= is the same idea as percent= in find_percentile_of, for a line instead of one number. "
            "A percentile line is not the line through a group of rows: it uses every row.",
        ],
        task=[
            'In the marks table, explain "marks" from "hours" with giving_outliers_less_weight=True. Which rows '
            "get less weight?",
            "Without looking back: which option changes the effects themselves, giving_outliers_less_weight= or "
            "robust_errors=? Run both on the school table to check.",
            'In the marks table, fit the 90th percentile line of "marks" against "hours". How many more marks '
            "does one more hour bring at the top? (Needs R.)",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.explain("marks", using=["hours"], giving_outliers_less_weight=True)"""),
             "Four rows get less weight: row 22 (weight 0.59), then rows 45, 11 and 42. The printout lists them "
             "with the lowest weight first."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.explain("marks", using=["hours"], giving_outliers_less_weight=True)
                table.explain("marks", using=["hours"], robust_errors=True)"""),
             "giving_outliers_less_weight= changes the effects (rows far from the model count less); "
             "robust_errors= gives the same effects as the ordinary model, with other standard errors."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.explain("marks", using=["hours"], for_percentile=90)"""),
             "5.00 more marks per hour at the 90th percentile (95 % CI 2.98 to 7.02)."),
        ],
        words=["table.explain", "table.show_rows_that_pull_model"],
    ),
    # S3a-3 (checking and comparing): lesson 28 after S3a's lesson 27, found by title
    dict(
        title=INTERACTIONS_LESSON,
        needs_r=needs_r_text("Example 1 needs no R. Examples 2 and 3 compare model averages with R emmeans: "
                             "find_model_averages_of() with within_each_group_in= and comparing=", packages=("emmeans",)),
        learn=[
            "how to draw an interaction picture: one line per group through the averages (draw_interaction_lines)",
            "how to test whether one effect depends on another column (an interaction in explain)",
            "if you have R: how to compare groups within each group of another column, after the interaction test "
            "(within_each_group_in=)",
            "if you have R: how to compare each group with a control, or in another planned way (comparing=)",
        ],
        parts=[
            ("Picture first. Do pupils who eat breakfast do better in every class, or only in some? "
             "draw_interaction_lines draws one line per breakfast group through the average marks of each class.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('chart = sdata.chart(sdata.get_example("school"))', "The pupils of lesson 16."),
                ('chart.draw_interaction_lines(x="class", y="marks", colour="breakfast")',
                 "Each dot is an average with its 95 % confidence interval. Parallel lines would mean breakfast "
                 "adds the same in every class; here the lines cross at the red class."),
                ('chart.save("lesson28_interaction.png")', "Save the picture."),
                ('table = sdata.table(sdata.get_example("school"))', "The same pupils as a table."),
                ('table.explain("marks", using=["class * breakfast"])',
                 'The test of the crossing (lesson 16): "class * breakfast" adds both columns and their '
                 "interaction. Read the line \"class : breakfast, all groups together\": p = 0.230, so the data "
                 "cannot tell whether the lines truly cross. Say in words what the picture shows and what the test "
                 "adds."),
            ]),
            ("If you have R: within each breakfast group, do the classes differ? within_each_group_in= "
             "compares the groups of for_each_group_in= inside each group of another column (simple effects). "
             "It always prints the interaction test first.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.find_model_averages_of("marks", for_each_group_in="class", using=["class * breakfast"], '
                 'within_each_group_in="breakfast")',
                 "for_each_group_in= names the groups that are compared (the classes); within_each_group_in= the "
                 "groups inside which they are compared (breakfast no, breakfast yes). First the interaction test "
                 "(p = 0.230), then the classes within each breakfast group and every pair there. Say in words why "
                 "the two p-values within the groups do not tell you that the breakfast groups differ."),
            ]),
            ("If you have R: planned comparisons. Often one group is a control and the question is how each "
             "other group differs from it. comparing= chooses the comparisons; emmeans' own adjustment for "
             "making several of them is printed.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "The school table."),
                ('table.find_model_averages_of("marks", for_each_group_in="class", using=["hours", "class"], '
                 'comparing="each with the first")',
                 "Each class against blue, the first in sorted order, with Dunnett's adjustment: green is 3.58 "
                 "marks higher (adjusted p = 0.048), red 1.36 (p = 0.597)."),
                ('table.find_model_averages_of("marks", for_each_group_in="class", using=["hours", "class"], '
                 'comparing="each with the first", in_order=["red", "blue", "green"])',
                 "One change: in_order= puts red first, so each class is compared with red."),
            ]),
        ],
        notes=[
            "The pupils of the school table come from 12 schools, and pupils of one school are alike, so the "
            "rows are not fully independent. These examples leave the schools out to stay short, so their "
            "p-values are a little too small; in a report, allow for the schools with grouped_by=\"school\" "
            "(lesson 16).",
            "Picture first, then the test: the interaction picture shows what the interaction test is about.",
            "Compare the groups with the interaction test, not by which simple effects have small p-values: "
            '"significant in one group but not the other" is not a difference between the groups (Gelman & Stern '
            "2006).",
            "for_each_group_in= names the groups that are compared; within_each_group_in= the groups inside which "
            "they are compared. Swap them and you ask another question.",
            'comparing= takes "each pair" (the default), "each with the first", "each with the next", "each with the '
            'average of the ones before", "each with the average", "trend" (groups in order) or your own weights; '
            "the dictionary has them all.",
        ],
        task=[
            'Draw the interaction picture the other way round: breakfast along the bottom (x="breakfast") and one '
            "line per class. Is the question it shows the same?",
            'If you have R: change only for_each_group_in=: compare the breakfast groups within each class '
            '(for_each_group_in="breakfast", within_each_group_in="class", using=["class * breakfast"]). What does '
            "it compare now?",
            'If you have R: keep for_each_group_in="class" and change only within_each_group_in= to "school", with '
            'using=["class * school"]. How many groups are the classes compared in now?',
            "Try to remember without looking back: which option compares each group with a control group, and "
            'which option puts the control first? Use them to compare each class with "green", allowing for "hours".',
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                chart = sdata.chart(sdata.get_example("school"))
                chart.draw_interaction_lines(x="breakfast", y="marks", colour="class")
                chart.save("interaction_other_way.png")"""),
             "The same averages, drawn the other way: lines that are not parallel here show the same interaction, "
             "seen from breakfast's side."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.find_model_averages_of("marks", for_each_group_in="breakfast", using=["class * breakfast"],
                                             within_each_group_in="class")"""),
             "Now breakfast yes and no are compared within each class: the same interaction test first, then one "
             "comparison per class."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.find_model_averages_of("marks", for_each_group_in="class", using=["class * school"],
                                             within_each_group_in="school")"""),
             "The classes are compared within each of the 12 schools, after the interaction test of class and "
             "school."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.find_model_averages_of("marks", for_each_group_in="class", using=["hours", "class"],
                                             comparing="each with the first", in_order=["green", "blue", "red"])"""),
             'comparing="each with the first" compares each group with the first; in_order= puts green first.'),
        ],
        words=["draw_interaction_lines", "table.explain", "table.find_model_averages_of"],
    ),
    # S3b-3 (survival and person-time): lesson 30 after S3b-1's lesson 29, found by title
    dict(
        title=MORE_SURVIVAL_LESSON,
        needs_r=needs_r_text("Examples 1 and 2 need no R (without R, explain_survival leaves out its proportional-"
                             "hazards check and Harrell's C, with a note). Example 3 finds the chance of an event when "
                             "another can come first with R's survival package: find_risk_over_time() with "
                             "competing_with=", packages=("survival", "cmprsk")),
        learn=[
            "how to turn dates into a time column and an event column (add_time_and_event_columns), and find the "
            "rate per patient-day",
            "how to read survival at chosen times (at_time_points=) and take a column into account without "
            "estimating its effect (allowing_for=)",
            "if you have R: the chance of an event when another event can come first (competing risks), and why 1 "
            "minus the survival curve is then too high",
        ],
        parts=[
            ("Hospital records come as dates. add_time_and_event_columns turns them into the two columns the "
             "survival and rate words need: the time followed, and whether the event happened.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("admissions"))',
                 "300 made-up hospital admissions in 2024, with the date each patient came, left, and first grew "
                 "ESBL-producing bacteria in a culture."),
                ('table.add_time_and_event_columns(from_date="admitted", to_date="discharged", '
                 'event_date="first_esbl")',
                 'Adds "time" (days from admission to the first of first_esbl and discharged) and "event" (1 when '
                 "first_esbl came first): 22 of 300 patients, 2,338 patient-days in all."),
                ('table.rate_of("event", time="time", for_each_group_in="ward")',
                 "New ESBL carriage per 1000 patient-days: 12.7 in intensive care and 6.46 in surgery. Say in words "
                 "what 12.7 per 1000 patient-days means for a ward with 20 patients for 50 days."),
            ]),
            ("At chosen times, and allowing for a column. Back to the trial of lesson 18, where nothing competes "
             "with death.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("trial"))', "The trial table of lesson 18."),
                ('table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment", '
                 "at_time_points=[365, 730])",
                 "Survival read at one and two years: 76.0 % of the new-medicine group and 64.3 % with usual care "
                 "were still alive after 365 days, each with its 95 % interval and the number still followed."),
                ('table.explain_survival(time="days", event="died", using=["age"], allowing_for="treatment")',
                 "Each treatment group gets its own baseline risk, so there is no hazard ratio for treatment; each "
                 "year of age still multiplies the risk at any moment by 1.05. With using= instead, treatment would "
                 "get a hazard ratio of its own."),
            ]),
            ("If you have R: in hospital, leaving hospital stops a patient from acquiring ESBL there. It competes with "
             "the event, so it must not be counted as the end of follow-up.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("admissions"))', "The admissions again."),
                ('table.add_time_and_event_columns(from_date="admitted", event_date="first_esbl", '
                 'competing_with="discharged")',
                 'competing_with= takes the date of the competing event: "event" now holds "first_esbl" or '
                 '"discharged", whichever came first.'),
                ('table.find_risk_over_time(time="time", event="event", value="first_esbl", '
                 'competing_with="discharged", for_each_group_in="ward", at_time_points=[30])',
                 "By day 30, 13.1 % of intensive-care patients had acquired ESBL (and 82.2 % had left first). 1 "
                 "minus Kaplan-Meier would say 35.8 %: the printout shows it, beside the right answer. Say in words "
                 "why 1 minus Kaplan-Meier is too high here."),
            ]),
        ],
        notes=[
            "time= and event= of add_time_and_event_columns name the columns it makes; give the same names to "
            "rate_of and the survival words next.",
            "A year here is 365.25 days and a month 30.4375 days (as R Epi and Stata); unit= chooses days, weeks, "
            "months or years.",
            "When another event can come first and stop the event (leaving hospital, death before relapse), use "
            "find_risk_over_time with competing_with=. The survival words refuse an event column with three kinds "
            "and show the call.",
            "find_risk_over_time gives the chance of having had the event by a time; explain_survival's hazard ratio "
            "is about the risk at any moment.",
            'More: followed_from= (rows that join late), average_time_up_to= (the average time without the event, '
            'easier to read than a hazard ratio), distribution= (time ratios), test_method="fine-gray", and allowing_for= '
            "on the curve words (curves adjusted for other columns). The dictionary has them all.",
        ],
        task=[
            'Add the time in weeks instead (unit="weeks") and give the ESBL rate per 100 patient-weeks for each ward '
            "(per=100).",
            "In the trial table, what share of each treatment group was still alive after 180 days?",
            "If you have R: draw the curves of example 3: chart.draw_risk_curves(...) with one curve per ward.",
            "Try to remember without looking back: which option says which event can come first? Use it with "
            "compare_survival to test whether the wards differ in the chance of ESBL (Gray's test).",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("admissions"))
                table.add_time_and_event_columns(from_date="admitted", to_date="discharged", event_date="first_esbl",
                                                 unit="weeks")
                table.rate_of("event", time="time", for_each_group_in="ward", per=100)"""),
             "8.91 per 100 patient-weeks in intensive care and 4.52 in surgery: the same rates as per 1000 "
             "patient-days, in other units."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("trial"))
                table.find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                              at_time_points=180)"""),
             "90.0 % of the new-medicine group and 81.7 % with usual care."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("admissions"))
                table.add_time_and_event_columns(from_date="admitted", event_date="first_esbl",
                                                 competing_with="discharged")
                chart = table.start_chart()
                chart.draw_risk_curves(time="time", event="event", value="first_esbl", competing_with="discharged",
                                       colour="ward")
                chart.save("esbl_risk.png")"""),
             "Two rising curves: the chance of having acquired ESBL by each day, higher in intensive care."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("admissions"))
                table.add_time_and_event_columns(from_date="admitted", event_date="first_esbl",
                                                 competing_with="discharged")
                table.compare_survival(time="time", event="event", value="first_esbl", competing_with="discharged",
                                       for_each_group_in="ward")"""),
             "competing_with=. Gray's test: chi-square 8.10, p = 0.004; differences this big would turn up in about "
             "4 of 1000 studies if the wards truly had the same chance of ESBL."),
        ],
        words=["table.add_time_and_event_columns", "table.rate_of", "table.find_survival_over_time",
               "table.explain_survival", "table.find_risk_over_time", "draw_risk_curves", "table.compare_survival"],
    ),
    # S3b-1 (combining studies): lesson 30, found by title
    dict(
        title=COMBINING_LESSON,
        needs_r=needs_r_text("Every example of this lesson combines studies with R metafor: combine_studies()",
                             packages=("metafor",)),
        learn=[
            "how to combine the results of several studies into one (a meta-analysis), and draw them as a forest plot",
            "how to read how much the studies differ: the prediction interval, tau and I-squared",
            "more: subgroups, and the funnel plot for small-study effects",
        ],
        parts=[
            ("Picture first. 13 made-up trials test a vaccine against tuberculosis (modelled on the BCG trials of "
             "Colditz et al. 1994). "
             "combine_studies puts their results together, and forest_plot draws each trial and the combined effect.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("bcg"))', "One row per trial: the vaccinated and unvaccinated "
                                                                 "people, and how many of each got tuberculosis."),
                ("result = " + COMBINE_CALL,
                 "events= and out_of= each name two columns: the first group (vaccinated), then the group it is "
                 "compared with. Read the first lines: the combined risk ratio is 0.47 (95 % CI 0.36 to 0.62): on "
                 "average the vaccine about halves the risk."),
                ("chart = result.start_chart()", "A chart of the result table."),
                ('chart.draw_forest_plot(x="estimate", y="study", size="weight %")',
                 "One square per trial, as big as its weight, with its 95 % interval; the diamond is the combined "
                 "effect. The line at 1 is no effect."),
                ('chart.save("lesson30_forest.png")', "Save the picture."),
            ]),
            ("How much do the studies differ? The combined effect is an average; the trials themselves found anything "
             "from a big benefit to none. Run the same call and read the lines after the p-value.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("bcg"))', "The same trials."),
                (COMBINE_CALL,
                 "The prediction interval, 0.19 to 1.19, is where the true risk ratio of a new setting like these "
                 "would lie: from a big benefit to none at all. Tau says the true risk ratios differ from the average "
                 "by a factor of about 1.50 up or down. I-squared, 89 %, is the share of the spread that is beyond "
                 "chance, not how big it is. Say in words why the prediction interval is wider than the confidence "
                 "interval."),
            ]),
            ("More: do groups of studies differ, and are small studies different? for_each_group_in= gives each group "
             "its own combined effect, with the test of their difference first; the funnel plot shows each study's "
             "effect against its standard error.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("bcg"))', "The same trials."),
                ('result = table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"], '
                 'out_of=["vaccinated", "unvaccinated"], for_each_group_in="allocation")',
                 'One change: for_each_group_in="allocation" (how people were put into the groups). The test of the '
                 "difference comes first (p = 0.52): the data cannot tell the three kinds of trial apart."),
                ("chart = result.start_chart()", "A chart of the result."),
                ('chart.draw_funnel_plot(x="estimate", y="standard error")',
                 "Each dot is a trial, small trials at the bottom. Dots missing from one lower corner would suggest "
                 "small-study effects, which are not proof of publication bias."),
                ('chart.save("lesson30_funnel.png")', "Save the picture."),
            ]),
        ],
        notes=[
            "Random or common effect is chosen before looking at the data, never by the Q test. simplydata uses random "
            "effects (REML) with Hartung-Knapp intervals; test_method= and interval_by= change them.",
            "The prediction interval is printed from 3 studies: it shows what a new setting could find, which the "
            "confidence interval of the average does not.",
            "Compare subgroups with the test of their difference, not by which subgroup's interval leaves out 1.",
            "Small-study effects (Peters' or Egger's test, trim and fill) are judged only from 10 studies.",
            "Other ways in: estimates= with their intervals (or standard_errors=), averages= with "
            "standard_deviations= and counts=, events= with time=, correlations=.",
        ],
        task=[
            "37 studies of passive smoking and lung cancer give an odds ratio with its 95 % interval (made up, "
            'modelled on Hackshaw et al. 1997). Fill in the blank: table = sdata.table(sdata.get_example("passive_smoking")), '
            'then table.combine_studies(names="study", estimates=____). What is the combined odds ratio?',
            'In the BCG trials, change only show=: combine odds ratios (show="odds ratios") instead of risk ratios. '
            "Is the answer close?",
            "Say in words why the prediction interval of the BCG trials is wider than the confidence interval.",
            "Try to remember without looking back: which number tells you where the true effect of a new setting "
            "could lie? Find it in the printout of the passive smoking studies.",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("passive_smoking"))
                table.combine_studies(names="study", estimates="odds ratio")"""),
             'estimates="odds ratio": simplydata finds the columns "odds ratio 95 % CI low" and "... high" next to it '
             "and combines the odds ratios on the log scale: about 1.33 (95 % CI 1.23 to 1.43)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("bcg"))
                table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"],
                                      out_of=["vaccinated", "unvaccinated"], show="odds ratios")"""),
             "The combined odds ratio is close to the risk ratio, because tuberculosis was rare in every trial."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("bcg"))
                table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"],
                                      out_of=["vaccinated", "unvaccinated"])"""),
             "The confidence interval is about the average effect; the prediction interval is about the true effect "
             "in one new setting, so it also holds the between-study spread (tau)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("passive_smoking"))
                table.combine_studies(names="study", estimates="odds ratio")"""),
             "The prediction interval: in a new setting like these studies, the true odds ratio would lie between "
             "about 1.22 and 1.45."),
        ],
        words=["table.combine_studies", "draw_forest_plot", "draw_funnel_plot"],
    ),
    # S3c-1 (communities and resistomes): lessons 31 and 32, found by title
    dict(
        title=DIVERSITY_LESSON,
        needs_r=needs_r_text("Every example of this lesson counts kinds with R vegan: add_diversity_columns() and "
                             "draw_richness_curves()", packages=("vegan",)),
        learn=[
            "how to read a community table: one row per sample, one column per kind (species, genes)",
            "richness, Shannon and Simpson, and what \"as diverse as 7 equally common kinds\" means",
            "why richness must be compared at the same total count (rarefaction)",
        ],
        parts=[
            ("Picture first. The resistome table holds the reads that matched 14 antibiotic resistance genes in 24 "
             "made-up samples from a hospital effluent, a treatment plant, a harbour and a fjord sediment. Each "
             "curve shows how many genes a sample would show at each number of reads.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("resistome"))', "One row per sample: its site, temperature, "
                                                                        "salinity, reads, and one column per gene."),
                (GENES_LINE, "The columns that hold counts of a kind. simplydata never guesses them: temperature or "
                             "reads would otherwise be counted as genes."),
                ("chart = table.start_chart()", "A chart of the table."),
                ('chart.draw_richness_curves(columns=genes, colour="site")',
                 "One curve per sample, coloured by site. The curves climb fast and then flatten: more reads find few "
                 "new genes. The dotted line marks the smallest total, 1,285 reads."),
                ('chart.save("lesson31_richness.png")', "Save the picture."),
            ]),
            ("How diverse is each sample? add_diversity_columns adds richness (the genes present), Shannon and "
             "Simpson, one value per sample, and says each as a number of equally common genes.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("resistome"))', "The same samples."),
                (GENES_LINE, "The gene columns."),
                ("table.add_diversity_columns(columns=genes)",
                 "Shannon averages 1.99: as diverse as a sample of 7.4 equally common genes. That is the number to "
                 "say in words; a 10 % drop in Shannon is not a 10 % drop in diversity."),
                ('table.compare_averages_of("shannon", for_each_group_in="site")',
                 "The new column is an ordinary column: Shannon is highest in the hospital effluent (2.15) and lowest "
                 "in the fjord sediment (1.85)."),
            ]),
            ("Compare richness at the same total count. A sample with 59,389 reads shows more genes than one with "
             "1,285, just because it was read more deeply. at_total_count= gives the richness expected in a sample "
             "of that many reads (rarefaction, the expected value, not a random subsample).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("resistome"))', "The same samples."),
                (GENES_LINE, "The gene columns."),
                ("table.add_diversity_columns(columns=genes, show=\"richness\", at_total_count=1285)",
                 "One change: at_total_count=1285, the smallest total. A new column holds the expected richness in "
                 "1,285 reads: 12.9 genes in the hospital effluent, 11.1 in the fjord sediment."),
                ('table.compare_averages_of("expected richness at 1285", for_each_group_in="site")',
                 "Now the sites are compared on the same footing."),
            ]),
        ],
        notes=[
            "Shannon uses the natural log here (scikit-bio's default changed from bits to the natural log in 0.6.1), "
            "and Simpson is 1 - D, the chance that two reads are of different genes; papers differ, so say which.",
            "Chao1 (show=\"chao1\") estimates how many genes would be found if sequencing went on; like "
            "at_total_count= it needs raw counts. Richness, Shannon and Simpson also work on normalised values "
            "(per 16S, per million reads), but richness then still depends on depth.",
            "show=\"hill numbers\" gives all three as numbers of equally common kinds (q = 0, 1, 2), which can be "
            "compared directly.",
        ],
        task=[
            "Fill in the blank: table.add_diversity_columns(columns=genes, show=____) to add Chao1. How close is it "
            "to the richness seen?",
            "Change only show=: add show=\"hill numbers\" and say in words what \"hill number 1\" means.",
            "Say in words: why must richness be compared at the same total count?",
            "Try to remember without looking back: which option gives the richness expected in a sample of 2,000 "
            "reads?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB",
                         "aadA", "mphA", "vanA", "mcr1"]
                table.add_diversity_columns(columns=genes, show="chao1")"""),
             "show=\"chao1\": it averages 12.9, the same as the genes seen: with so many reads per gene, no gene is "
             "seen only once or twice, so Chao1 expects nothing more to find."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB",
                         "aadA", "mphA", "vanA", "mcr1"]
                table.add_diversity_columns(columns=genes, show="hill numbers")"""),
             "Hill number 1 is the number of equally common genes that would give the same Shannon diversity: about "
             "7.4 on average, against 12.9 genes present, because a few genes hold most of the reads."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB",
                         "aadA", "mphA", "vanA", "mcr1"]
                table.add_diversity_columns(columns=genes, show="richness", at_total_count=1285)"""),
             "More reads find more of the rare genes, so a deeply sequenced sample looks richer even when it is not; "
             "at the same total count the depth no longer decides."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB",
                         "aadA", "mphA", "vanA", "mcr1"]
                table.add_diversity_columns(columns=genes, show="richness", at_total_count=2000)"""),
             "at_total_count=2000; the two samples with fewer than 2,000 reads get empty cells, and the printout "
             "names them."),
        ],
        words=["table.add_diversity_columns", "draw_richness_curves", "table.compare_averages_of"],
    ),
    dict(
        title=MAKEUP_LESSON,
        needs_r=needs_r_text("Every example of this lesson runs R: add_log_ratio_columns() (zCompositions, "
                             "compositions), add_principal_coordinates() and explain_profiles_of() (vegan)",
                             packages=("vegan", "zCompositions", "compositions")),
        learn=[
            "why counts of genes or species are compositional: the totals are set by the sequencing depth",
            "how log ratios (clr) and the Aitchison distance read the same table without the depth",
            "how much of the make-up temperature and salinity explain (RDA)",
        ],
        parts=[
            ("Counts are parts of a whole. Two genes can go up together only because a sample got more reads. "
             "Compare the counts of blaTEM and sul1 with their log ratios.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("resistome"))', "The resistome samples."),
                (GENES_LINE, "The gene columns."),
                ('table.find_correlation_between("blaTEM", "sul1")',
                 "r = 0.51 on the counts. But blaTEM also goes with the number of reads (r = 0.52): deeper samples "
                 "have more of everything."),
                ("table.add_log_ratio_columns(columns=genes)",
                 "clr_ columns: the log of each gene over the sample's geometric mean. 27 zeros are first replaced by "
                 "estimated small values, and the printout says so."),
                ('table.find_correlation_between("clr_blaTEM", "clr_sul1")',
                 "On log ratios the positive link is gone (r = -0.35, p = 0.095): it came from the depth."),
            ]),
            ("The same table read two ways. PCoA draws the samples from their distances: Bray-Curtis on the counts, "
             "then Aitchison (the distance between the log ratios).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("resistome"))', "The same samples."),
                (GENES_LINE, "The gene columns."),
                ("table.add_principal_coordinates(columns=genes, measure=\"aitchison\")",
                 "PCo1 shows 43.6 % of the differences between samples, and no eigenvalue is negative. With "
                 "measure=\"bray-curtis\" (the default) PCo1 shows 52.8 %, 5 eigenvalues are negative, and a note "
                 "warns that Bray-Curtis on raw counts mixes in the depth."),
                ("chart = table.start_chart()", "A chart of the table with PCo1 and PCo2."),
                ('chart.draw_dots(x="PCo1", y="PCo2", colour="site")',
                 "The hospital effluent samples sit apart along PCo1; the treatment plant, harbour and fjord sediment "
                 "follow each other along PCo2, from the sewage to the sea."),
                ('chart.save("lesson32_pcoa.png")', "Save the picture."),
            ]),
            ("What explains the make-up? explain_profiles_of tests columns such as temperature and salinity against "
             "the whole profile of genes: redundancy analysis (RDA).", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("resistome"))', "The same samples."),
                (GENES_LINE, "The gene columns."),
                ('table.explain_profiles_of(genes, using=["temperature", "salinity"], measure="aitchison")',
                 "Temperature and salinity together explain 38.6 % of the differences in make-up (adjusted R "
                 "squared); each is tested after the other, so their order does not matter."),
            ]),
        ],
        notes=[
            "Zeros: logs need values above 0. simplydata replaces zeros by estimated small values (R zCompositions "
            "GBM) and never deletes a gene; zeros_replaced_by=\"adding 1\" adds 1 instead, and the answer then "
            "depends on the 1.",
            "PCoA percentages: simplydata gives the share of the positive eigenvalues; vegan and ape divide by the "
            "sum of all of them, so their numbers are a little higher. The printout says both.",
            "explain_profiles_of uses Bray-Curtis by default (distance-based RDA, as compare_profiles_of). With "
            "Bray-Curtis the read depth itself explains part of the make-up: try using=[\"salinity\", \"reads\"].",
            "More: compare_profiles_of(..., test_method=\"anosim\") gives ANOSIM; show=\"contributions\" (SIMPER) shows "
            "which genes add most to the difference between two sites, with Warton's caveat; "
            "find_correlation_between_profiles compares two sets of columns (Mantel, Procrustes); "
            "chart.draw_cluster_tree draws the tree of clusters.",
        ],
        task=[
            "Fill in the blank: table.add_principal_coordinates(columns=genes, measure=____) for the distance "
            "between log ratios.",
            "Change only measure=: run explain_profiles_of(genes, using=[\"temperature\", \"salinity\"]) with the "
            "default Bray-Curtis. How much do they explain now?",
            "Say in words why a correlation between two genes' counts can be false.",
            "Try to remember without looking back: which word adds clr columns?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB",
                         "aadA", "mphA", "vanA", "mcr1"]
                table.add_principal_coordinates(columns=genes, measure="aitchison")"""),
             "measure=\"aitchison\": the straight-line distance between the samples' log ratios."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB",
                         "aadA", "mphA", "vanA", "mcr1"]
                table.explain_profiles_of(genes, using=["temperature", "salinity"])"""),
             "With Bray-Curtis on the counts they explain 35.9 %, and the note warns that the totals differ a lot; "
             "the log ratios (38.6 %) take the depth out."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                table.find_correlation_between("blaTEM", "reads")"""),
             "Each count grows with the sequencing depth of its sample, so two genes rise and fall together even "
             "when their shares do not change (Pearson's spurious correlation)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("resistome"))
                genes = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB",
                         "aadA", "mphA", "vanA", "mcr1"]
                table.add_log_ratio_columns(columns=genes)"""),
             "table.add_log_ratio_columns: test_method=\"clr\" is the default."),
        ],
        words=["table.add_log_ratio_columns", "table.add_principal_coordinates", "table.explain_profiles_of",
               "table.find_correlation_between", "draw_dots"],
    ),
    # S3c-3 (directions, places and extremes): one coastal-station story (independent review 7.3), found by title
    dict(
        title=COAST_LESSON,
        needs_r=needs_r_text("The Rayleigh test (R circular), Moran's I (R spdep) and the return levels (R extRemes) "
                             "in this lesson", packages=("circular", "spdep", "extRemes")),
        learn=[
            "why directions cannot be averaged as plain numbers, and how to average them",
            "how to ask whether nearby places have alike values (Moran's I), and why the weights matter",
            "what a 100-year sea level is, and how sure we can be of it",
        ],
        parts=[
            ("Currents. 60 made-up stations in a fjord each have the direction their current mostly flows to, in "
             "degrees (0 = north). First the mistake: the plain average.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("stations"))', "One row per station: where it is, its depth, "
                                                                       "its current and the zinc in its sediment."),
                ('table.find_average_of("current_direction")',
                 "222: south-west, yet almost every current flows to the north. The plain average of 350° and 10° is "
                 "180°, the opposite way; a note says so."),
                ('table.find_average_direction_of("current_direction", full_turn=360)',
                 "354°, a little west of north. The resultant length 0.93 says the directions are close together "
                 "(1 = all the same, 0 = no average direction). full_turn=360 says the values are degrees."),
                ('table.compare_shape_to("current_direction", shape="even around the circle", full_turn=360)',
                 "The Rayleigh test: if the currents flowed every way evenly, directions this close together would "
                 "turn up in fewer than 1 in 1000 studies like this one."),
            ]),
            ("Neighbours. Is the zinc in the sediment alike at nearby stations? Moran's I is near 0 when the values "
             "are scattered at random and above 0 when nearby places are alike.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("stations"))', "The same stations."),
                ('table.find_autocorrelation_of("zinc", x="east", y="north")',
                 "Moran's I = 0.174 (no pattern gives about 0): nearby stations have more alike zinc. Every pair "
                 "counts, nearer pairs more (weights 1 / distance); 999 shuffles give p = 0.001, the smallest they "
                 "can."),
                ('table.find_autocorrelation_of("zinc", x="east", y="north", nearest=6)',
                 "With only each station's 6 nearest neighbours Moran's I is 0.445: the weights change the answer, "
                 "so say which you used."),
            ]),
            ("Storms. The highest sea level of each year at a coastal town, 1923 to 1987 (made up, modelled on Port "
             "Pirie in Coles 2001). How high is the sea once in 100 years?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("sea_levels"))', "One row per year: its highest sea level in m."),
                ("chart = table.start_chart()", "Picture first."),
                ('chart.draw_dots(x="year", y="sea_level")', "Each year's highest level: no year stands far apart."),
                ('chart.save("lesson33_sea_levels.png")', "Save the picture."),
                ('table.find_return_levels_of("sea_level", once_in=[10, 100], sorted_by="year")',
                 "A level of 4.53 m is reached on average once in 100 years (a 1-in-100 chance in any one year); its "
                 "95 % interval runs from 4.41 to 4.84, longer above than below. sorted_by=\"year\" lets the word "
                 "check that each row is one year."),
            ]),
        ],
        notes=[
            "full_turn= has no default: a column in radians read as degrees gives a wrong answer without a word. "
            "Use full_turn=24 for hours of the day, 12 for months, \"radians\" for radians.",
            "On longitude and latitude, add on_globe=True to find_autocorrelation_of: straight-line distances on "
            "degrees are wrong away from the equator. A station sampled many times needs its values averaged first.",
            "Return levels come with profile-likelihood intervals: for long return periods the usual symmetric "
            "interval is too narrow. Each row must be the largest value of one year; daily readings are refused.",
            "More: table.find_variogram_of(\"zinc\", x=\"east\", y=\"north\") and chart.draw_variogram(...) show "
            "how different two stations are at each distance apart; on daily readings, values_above=20 with "
            "sorted_by=\"date\" uses every reading above 20 (try sdata.get_example(\"rain\")), and "
            "chart.draw_threshold_check(x=\"rain\", between=[10, 30]) helps choose the 20; "
            "chart.draw_polar(..., full_turn=360) draws directions as a compass.",
        ],
        task=[
            "Fill in the blank: table.find_average_direction_of(\"current_direction\", full_turn=____) for degrees.",
            "Change only once_in=: find the 50-year sea level.",
            "Say in words what a 100-year level means. Is it certain to happen in the next 100 years?",
            "Try to remember without looking back: which word tells whether nearby places have alike values?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("stations"))
                table.find_average_direction_of("current_direction", full_turn=360)"""),
             "full_turn=360: a full turn is 360 degrees."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("sea_levels"))
                table.find_return_levels_of("sea_level", once_in=[50], sorted_by="year")"""),
             "About 4.45 m once in 50 years (95 % CI 4.34 to 4.69)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("sea_levels"))
                table.find_return_levels_of("sea_level", once_in=[100], sorted_by="year")"""),
             "A level with a 1-in-100 chance of being reached in any one year. It is not certain in the next 100 "
             "years: it can come twice in a decade, or not at all in 200 years (the chance of at least once in 100 "
             "years is about 63 %)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("stations"))
                table.find_autocorrelation_of("zinc", x="east", y="north")"""),
             "table.find_autocorrelation_of with x= and y=: Moran's I."),
        ],
        words=["table.find_average_direction_of", "table.compare_shape_to", "table.find_autocorrelation_of",
               "table.find_return_levels_of", "table.find_average_of", "draw_dots"],
    ),
    # S3d-1 (planning and surveys): plan the experiment first, then the random list, then a fair sample; found by title
    dict(
        title=PLANNING_LESSON,
        needs_r=needs_r_text("The design table (R agricolae) and the random assignments (R blockrand) in this lesson",
                             packages=("agricolae", "blockrand")),
        learn=[
            "how to lay out an experiment so that unknown differences spread evenly over the treatments",
            "how to make a list that says which group each new participant joins, in random blocks",
            "how to pick a fair sample from every group (a stratified random sample)",
        ],
        parts=[
            ("An experiment in a greenhouse: 2 temperatures and 2 salinities, every combination 3 times. The benches "
             "differ (light, draught), so each bench gets every combination once: randomised blocks.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('design = sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, '
                 'of_kind="randomised blocks", with_seed=2)',
                 "12 plots: the 2 x 2 = 4 combinations, once in each of 3 blocks (benches), each block in its own "
                 "random order. \"plot\" is the order to work in; \"standard order\" numbers the combinations."),
                ("design.show()", "The table to print and take to the greenhouse."),
            ]),
            ("A trial: each new patient gets the new dressing or the usual one. A list made in advance, in random "
             "blocks, keeps the groups about the same size all the way through.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('assignments = sdata.make_random_assignments(how_many=40, groups=["new", "usual"], '
                 'in_blocks_of=[4, 6], for_each_of=["Bergen", "Oslo"], with_seed=1)',
                 "One list for each hospital. Each block of 4 or 6 holds both groups equally often; the block sizes "
                 "change at random, so nobody can guess the end of a block. The last block is completed, so a list "
                 "can be a little longer than 40."),
                ('assignments.count_rows(for_each_group_in="group")', "How many places each group has."),
            ]),
            ("A survey: 200 schools were sampled within each school type. To try a smaller sample by hand, pick the "
             "same number from every type: a stratified random sample.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("sampled_schools"))',
                 "200 made-up schools (modelled on a California survey sample)."),
                ('table.keep_random_rows(5, for_each_group_in="school_type", with_seed=1)',
                 "5 schools of each type, 15 in all, picked at random within each type."),
                ('table.count_rows(for_each_group_in="school_type")', "5 elementary, 5 high and 5 middle schools."),
            ]),
        ],
        notes=[
            "with_seed= makes the same table or list again. A randomisation list must be made once, kept, and kept "
            "away from the people who recruit (allocation concealment): if they can guess the next group, they can "
            "choose who joins when.",
            "Block sizes are multiples of the number of groups: with 2 groups, 4 and 6; with 3 groups, 3 and 6.",
            "of_kind=\"latin square\" (one factor in rows and columns) and of_kind=\"split plot\" with whole_plots= "
            "(a factor that is hard to change plot by plot, such as irrigation) are the other layouts.",
            "More: a survey sample is analysed with its weights: table.use_survey_design(weights=\"weight\", "
            "strata=\"school_type\", population_sizes=\"schools_of_type\"), then find_average_of, "
            "find_percent_of_rows_where and explain describe the population (R survey). Answers on a scale: "
            "table.count_each(columns=[...], in_order=[...]) and chart.draw_answer_bars(...) (try "
            "sdata.get_example(\"course_feedback\")). Empty cells: table.count_empty_cells_in(show=\"patterns\").",
        ],
        task=[
            "Fill in the blank: sdata.make_design_table({\"temperature\": [10, 20], \"salinity\": [30, 35]}, "
            "repeats=3, of_kind=____, with_seed=1) when every plot can go anywhere.",
            "Change only for_each_of=: make the dressing list for three hospitals, Bergen, Oslo and Trondheim.",
            "Say in words why the block sizes should change at random.",
            "Try to remember without looking back: which option of keep_random_rows picks rows within each group?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3,
                                        of_kind="completely random", with_seed=1)"""),
             "of_kind=\"completely random\" (the default): every plot in one random order, with no blocks."),
            (_sx("""\
                import simplydata as sdata
                sdata.make_random_assignments(how_many=40, groups=["new", "usual"], in_blocks_of=[4, 6],
                                              for_each_of=["Bergen", "Oslo", "Trondheim"], with_seed=1)"""),
             "Three lists, one for each hospital, each in random blocks of 4 and 6."),
            (_sx("""\
                import simplydata as sdata
                sdata.make_random_assignments(how_many=20, groups=["new", "usual"], in_blocks_of=[4], with_seed=1)"""),
             "With one block size, a recruiter who knows it can work out the last group of every block (here the "
             "4th place). Random sizes hide where a block ends (Schulz & Grimes 2002)."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("marks"))
                table.keep_random_rows(2, for_each_group_in="class", with_seed=1)"""),
             "for_each_group_in=: the same word as in the summaries, here meaning \"within each group\"."),
        ],
        words=["sdata.make_design_table", "sdata.make_random_assignments", "table.keep_random_rows",
               "table.count_rows", "table.show"],
    ),
    # S3d-2 (epidemiology and cause and effect): a "more" lesson, found by title
    dict(
        title=CAUSE_LESSON,
        needs_r=needs_r_text("Parts 1 and 2 run R WeightIt, MatchIt and cobalt (compare_balanced_groups_of); part 3 "
                             "needs no R", packages=("WeightIt", "MatchIt", "cobalt", "sandwich", "lmtest")),
        learn=[
            "why a plain comparison of groups that chose themselves can mislead",
            "how to make two groups alike in other columns (weighting and matching) and check that they are alike",
            "how to split an effect into the part that goes through another column and the rest (mediation)",
        ],
        parts=[
            ("A job-training study. The 185 trained men earned less in 1978 than 429 men from a survey. Did the "
             "training lower earnings? First the plain comparison.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("job_training"))',
                 "Made-up data, modelled on LaLonde (1986): treat = 1 for the trained men, their age, schooling, "
                 "race, marriage, "
                 "degree and earnings in 1974, 1975 and 1978."),
                ('table.compare_averages_of("re78", for_each_group_in="treat")',
                 "The trained men earned 2733 dollars less. But they differ before the training too: younger, more "
                 "often black and unmarried, and with much lower earnings in 1974."),
                ('table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", '
                 '"race", "married", "nodegree", "re74", "re75"])',
                 "Read the balance table first: before weighting, race (black) differs by 0.74 standard deviations; "
                 "after, by 0.11. Some columns are still above 0.1, and a note says so. The effect for everyone: "
                 "1347 dollars more (95 % CI -937 to 3631)."),
            ]),
            ("The same question, with matching: each trained man gets the man from the survey with the nearest "
             "propensity score. Matching gives the effect among the trained men, so effect_for= names them.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("job_training"))', "The same men."),
                ('table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", '
                 '"race", "married", "nodegree", "re74", "re75"], test_method="matching", effect_for=1, '
                 "match_within=0.2)",
                 "Pairs further apart than 0.2 standard deviations of the logit of the score are left out (51 "
                 "trained men had no match). Race is now balanced; the effect among the matched trained men: 1010 "
                 "dollars more (95 % CI 10.7 to 2008). The table was made with an effect of 1800 dollars."),
            ]),
            ("Mediation. In a made-up version of the JOBS II study a job-search workshop was randomised. Did it "
             "lower depression by raising the workers' confidence in searching for a job?", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("job_search"))',
                 "Made-up data with the columns of the JOBS II study (Vinokur et al. 1995): treat = 1 for the "
                 "workshop, job_seek = confidence in searching, depress2 = depression six months later."),
                ('table.explain("depress2", using="treat", through="job_seek", allowing_for=["econ_hard", "sex", '
                 '"age"])',
                 "The indirect effect (through job_seek) is -0.094 (95 % interval -0.131 to -0.060) and the total "
                 "effect -0.116: the table was made with an indirect effect of about -0.09, and the analysis finds "
                 "it. The printout says what these rest on: nothing unmeasured that affects both job_seek and "
                 "depression."),
            ]),
        ],
        notes=[
            "Balancing can only make groups alike in the columns you give it. A column that was not measured, such "
            "as motivation, can still differ, which is why the printout always names the assumptions.",
            "Judge balance by the standardised differences (within about 0.1), never by p-values: with many rows "
            "a tiny difference has a small p-value, with few rows a big one does not.",
            "effect_for=\"everyone\" (weighting) asks what would happen if everyone were trained rather than "
            "no one; effect_for=1 asks what the training did for those who took it. They are different questions "
            "and can have different answers.",
            "More: compare_balanced_groups_of(..., show=\"balance\") gives the balance table and "
            "show=\"propensity scores\" each row's score; explain(..., through=) also works with a yes or no "
            "outcome (outcome=\"yes or no\").",
        ],
        task=[
            "Fill in the blank: table.compare_balanced_groups_of(\"re78\", for_each_group_in=\"treat\", "
            "allowing_for=[...], test_method=\"matching\", effect_for=____) for the effect among the trained men.",
            "Change only one option of part 1: give the effect among the trained men with weighting "
            "(effect_for=1). How does it compare with matching?",
            "Say in words why the plain comparison of part 1 gave the wrong sign.",
            "Try to remember without looking back: which option of explain() names the column the effect goes "
            "through?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("job_training"))
                table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", "race",
                                                 "married", "nodegree", "re74", "re75"], test_method="matching", effect_for=1)"""),
             "effect_for=1: the group of the trained men (treat = 1). Without match_within= every trained man is "
             "matched; race stays unbalanced (0.52), and a note says so."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("job_training"))
                table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", "race",
                                                 "married", "nodegree", "re74", "re75"], effect_for=1)"""),
             "1321 dollars more among the trained men (95 % CI 555 to 2088): the same question as matching, a "
             "little larger, and now race is balanced."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("job_training"))
                table.compare_averages_of("re74", for_each_group_in="treat")"""),
             "The trained men earned much less already in 1974, before any training: the plain comparison mixes "
             "the training with who took it."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("job_search"))
                table.explain("depress2", using="treat", through="job_seek")"""),
             "through=: the column the effect goes through (the mediator)."),
        ],
        words=["table.compare_balanced_groups_of", "table.compare_averages_of", "table.explain"],
    ),
    # S3d-3 (Bayesian methods): a Bayes factor first, then a credible interval, then a Bayesian model and its check
    dict(
        title=BAYES_LESSON,
        needs_r=needs_r_text("The Bayes factors (R BayesFactor) and the Bayesian model (R rstanarm, a large package) "
                             "in this lesson", packages=("BayesFactor", "rstanarm", "posterior")),
        learn=[
            "how to say how many times as likely the data are if two groups differ as if they do not (a Bayes factor)",
            "what a credible interval says, and how it differs from a confidence interval",
            "how to fit a model the Bayesian way, read its prior, and check that its chains agree",
        ],
        parts=[
            ("Does the CRP blood test differ between the two wards? A Bayes factor compares two answers, a difference "
             "and none, and can speak for either.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "200 made-up patients in two wards."),
                ('table.compare_averages_of("crp", for_each_group_in="ward", test_method="bayesian")',
                 "The Bayes factor: how many times as likely the data are if the wards differ as if they do not. "
                 "Below 1 the data favour no difference. The prior (a Cauchy curve of width 0.707) is printed."),
                ('table.compare_averages_of("crp", for_each_group_in="ward", test_method="bayesian", prior_width="wide")',
                 "The same with a wider prior: the Bayes factor changes, so always say which prior you used."),
            ]),
            ("Did the pain go down after 4 weeks? The credible interval says where the average change probably "
             "lies, given the data and the prior.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("clinic"))', "The same patients, pain at the start and later."),
                ('table.compare_before_and_after("pain_week_0", "pain_week_4", test_method="bayesian", with_seed=1)',
                 "A 95 % credible interval: given the data and the prior, a 95 % chance that the average change lies "
                 "in it. with_seed= makes the same random draws again."),
            ]),
            ("Marks explained by hours of study and breakfast, the Bayesian way: each effect with its credible "
             "interval, the prior, and a check that the 4 chains agree.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('table = sdata.table(sdata.get_example("school"))', "Made-up pupils in 12 schools."),
                ('table.explain("marks", using=["hours", "breakfast"], test_method="bayesian")',
                 "R rstanarm draws 4000 values of each effect. Read the prior first, then each effect and its "
                 "interval, then the convergence line: R-hat at most 1.01 and at least 400 effective draws."),
                ('check = table.check_model_of("marks", using=["hours", "breakfast"], test_method="bayesian")',
                 "The posterior predictive check: the data (dark) against 50 sets made up by the model (light)."),
                ('check.save("predictive_check.png")', "Save the picture."),
            ]),
        ],
        notes=[
            "A Bayes factor is not the chance that a hypothesis is true: it says how much the data shift the odds "
            "between the two. A Bayes factor of 3 means the data are 3 times as likely if the groups differ; the "
            "words \"moderate\" or \"strong\" that some tables add are not used here.",
            "A confidence interval is about the method (95 % of such intervals hold the true value); a credible "
            "interval is about this value, given the data and the prior. With weak priors they are often close.",
            "If a warning says the chains do not agree (R-hat above 1.01) or there are too few effective draws, do "
            "not report the numbers: simplify the model or put the columns on similar scales first.",
            "More: find_correlation_between(\"crp\", \"procalcitonin\", test_method=\"bayesian\") and compare_counts_of(..., "
            "test_method=\"bayesian\") give Bayes factors for a correlation and a table of counts; explain(..., grouped_by=, "
            "test_method=\"bayesian\") fits a Bayesian mixed model; check_model_of(..., test_method=\"bayesian\", show=\"prior check\") "
            "shows what the prior allows before seeing the data.",
        ],
        task=[
            "Fill in the blank: table.compare_averages_of(\"procalcitonin\", for_each_group_in=\"ward\", ____=True).",
            "Change only prior_width=: run part 1 with prior_width=\"ultrawide\". Does the Bayes factor go up or down?",
            "Say in words what the credible interval of part 2 means, without the word \"confidence\".",
            "Try to remember without looking back: which option of check_model_of shows what the prior allows?",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("clinic"))
                table.compare_averages_of("procalcitonin", for_each_group_in="ward", test_method="bayesian")"""),
             "test_method=\"bayesian\": the Bayes factor and the credible interval instead of a p-value."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("clinic"))
                table.compare_averages_of("crp", for_each_group_in="ward", test_method="bayesian", prior_width="ultrawide")"""),
             "A wider prior expects bigger differences, so a small difference counts more for \"no difference\": "
             "the Bayes factor for a difference goes down."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("clinic"))
                table.compare_before_and_after("pain_week_0", "pain_week_4", test_method="bayesian")"""),
             "Given these patients and the prior, there is a 95 % chance that the average change lies between the "
             "two numbers printed."),
            (_sx("""\
                import simplydata as sdata
                table = sdata.table(sdata.get_example("school"))
                table.check_model_of("marks", using=["hours"], test_method="bayesian", show="prior check")"""),
             "show=\"prior check\": 50 sets of values made up from the prior alone."),
        ],
        words=["table.compare_averages_of", "table.compare_before_and_after", "table.explain",
               "table.check_model_of", "table.find_correlation_between", "table.compare_counts_of"],
    ),
    dict(
        title=FJORD_LESSON,
        learn=[
            "how to read sample IDs such as 007 exactly as they were typed",
            "how to tidy a lab file: column names, empty rows and columns, rows pasted twice",
            "how to find the rows that are, or are not, in another table, and how to join two tables safely",
            "how to work group by group: the first rows, row numbers, running totals and whole groups",
        ],
        parts=[
            ("A lab sends its qPCR results as a file. Read it so that the sample IDs stay as they were typed.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('sdata.get_example("fjord_lab").save("fjord_lab.csv")',
                 "Save the practice lab table as a file, as the lab would send it."),
                ('lab = sdata.table("fjord_lab.csv")', "Read the file."),
                ("lab.show_first_rows(3)", 'The IDs "001", "002" ... were read as numbers: 1, 2, 3. The zeros are '
                                           "gone, and no later step can bring them back."),
                ('lab = sdata.table("fjord_lab.csv", read_as_text=["sample_id", "lab_code"])',
                 "Read it again, keeping sample_id and lab_code as text, exactly as typed."),
                ("lab.show_first_rows(3)", 'Now "001" stays "001", and a lab code such as 3-12 stays text.'),
            ]),
            ("Spreadsheets leave empty rows, empty columns and rows pasted twice. Look first, then tidy.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('lab = sdata.table(sdata.get_example("fjord_lab"))', "The lab's results again, as a practice table."),
                ("lab.remove_rows_that_are_all_empty()", "Remove the rows in which every cell is empty. A row with "
                                                         "one empty cell stays."),
                ("lab.remove_columns_that_are_all_empty()", "Remove the column nobody filled in."),
                ("lab.show_duplicate_rows()", "Look at the rows that repeat, each with its row number: every copy "
                                              "is shown, the first one too."),
                ("lab.remove_duplicate_rows()", "Remove the repeats: the first copy of each stays."),
                ("lab.show_steps()", "Every step is listed, and undo() takes the last one back."),
            ]),
            ("The stations table has column names as a spreadsheet writes them: capitals, spaces and signs.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('stations = sdata.table(sdata.get_example("fjord_stations"))', "The eight stations of the cruise."),
                ("stations.clean_column_names()", 'Plain names: "Distance to outfall (km)" becomes '
                                                  "distance_to_outfall_km. One line per change is printed."),
                ("stations.show()", "The same table with names you can type without quotes in a formula."),
            ]),
            ("Which samples have a lab result? The lab writes 007, the samples table 7: make them the same kind "
             "first.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('samples = sdata.table(sdata.get_example("fjord_samples"))', "The 60 water samples."),
                ('lab = sdata.table(sdata.get_example("fjord_lab"))', "The lab's results."),
                ('lab.turn_into_numbers("sample_id")', '"007" becomes 7, as in the samples table.'),
                ('samples.remove_rows_found_in(lab, using="sample_id")', "Remove every sample that the lab table "
                                                                         "has: what is left has no lab result."),
                ("samples.show()", "Sample 23 was lost in transport, as its note says."),
                ("samples.undo()", "Back to all 60 samples."),
                ('lab.remove_rows_found_in(samples, using="sample_id")', "The other way round: remove the lab rows "
                                                                         "whose sample is in the samples table."),
                ("lab.show()", "Left: the 2 empty rows, and 141, which is sample 41 typed with one 1 too many."),
                ("lab.undo()", "Back to every lab row."),
                ('samples.keep_rows_found_in(lab, using="sample_id")', "The opposite: only the samples with a lab "
                                                                       "result. No column comes in, and no row "
                                                                       "is repeated."),
            ]),
            ("Join the samples with their station: where each station is and how far from the outfall. "
             "with_match_column=True shows which rows found no partner.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('samples = sdata.table(sdata.get_example("fjord_samples"))', "The 60 water samples."),
                ('stations = sdata.table(sdata.get_example("fjord_stations"))', "The stations."),
                ("stations.clean_column_names()", "Station becomes station, as in the samples table."),
                ('samples.join_with(stations, using="station", keep="all rows from this table", '
                 'check_that="each row has one match", with_match_column=True)',
                 'Bring in the station columns, keeping every sample. check_that= stops the join if a station '
                 'appeared twice in the stations table; the new column "found in" says where each row was found.'),
                ('samples.count_each("found in")', 'Some samples found no station: their names were typed with a '
                                                   'space at the end ("St.3 ") or in other capitals ("st.3").'),
                ('samples.keep_rows_where("found in", is_equal_to="this table only")', "Look at them."),
                ("samples.show()", "Fix the names (remove_extra_spaces_in, replace_values_in), then join again."),
            ]),
            ("Work group by group: number the samples of each station, keep the first of each, and keep only the "
             "genes the lab found often.", [
                ("import simplydata as sdata", "Load simplydata."),
                ('samples = sdata.table(sdata.get_example("fjord_samples"))', "The 60 water samples."),
                ('samples.add_row_number_column("number_at_station", for_each_group_in="station", '
                 'sorted_by="sampled_local")', "1, 2, 3 ... for the samples of each station, in the order they "
                                               "were taken."),
                ('samples.add_running_column("samples_so_far", from_column="sample_id", show="count", '
                 'sorted_by="sampled_local")', "A running count: how many samples had been taken by then."),
                ('samples.keep_first_rows(1, for_each_group_in="depth_m")', "The first sample at each depth."),
                ("samples.show()", "One row for each depth: 1, 10 and 30 m."),
                ('lab = sdata.table(sdata.get_example("fjord_lab"))', "The lab's results."),
                ("lab.remove_rows_that_are_all_empty()", "Tidy first: no empty rows ..."),
                ("lab.remove_duplicate_rows()", "... and no rows pasted twice."),
                ('lab.turn_into_numbers("copies_per_ml")', '"<LOD" and "n.d." are not numbers, so those cells '
                                                           "become empty, and simplydata says how many."),
                ('lab.keep_groups_where("count(copies_per_ml) >= 40", for_each_group_in="gene")',
                 "Keep the genes measured above the limit in at least 40 samples: whole groups go or stay. "
                 "blaOXA-48, found in only a few samples, goes."),
                ('lab.find_median_of("copies_per_ml", for_each_group_in="gene")', "The median copies per ml of "
                                                                                  "each gene that is left."),
            ]),
        ],
        notes=[
            'read_as_text= matters because the loss is silent: once "007" is read as 7, no step can know it had '
            "zeros. Spreadsheets do worse: they turn gene names such as SEPT2 and MARCH1 into dates, and a study of "
            "published supplementary files found it in about one in five papers with gene lists (Ziemann, Eren "
            "and El-Osta 2016, Genome Biology 17, 177). Read IDs and codes as text, and save as CSV, not Excel.",
            "remove_rows_that_are_all_empty() removes a row only when every cell is empty; "
            "remove_rows_with_empty_cells_in() removes a row for a single empty cell. They are different jobs.",
            'show_duplicate_rows(columns=["sample_id", "gene"]) looks for rows that repeat in those columns only; '
            'remove_duplicate_rows(keep="last") keeps the last copy instead of the first, keep="none" removes them all.',
            "keep_rows_found_in and remove_rows_found_in never add a column and never repeat a row (semi and anti "
            "joins). join_with brings the columns in, and repeats a row when its key appears more than once in "
            "the other table: check_that= stops that before it happens.",
            'using={"sample_id": "sample"} pairs two columns with different names (this table\'s first). '
            'keep="all rows from the other table" keeps every row of the other table.',
            "When several rows would fill one cell, spread_into_columns stops and asks; show=\"total\" (or "
            "\"average\", \"count\" ...) says how to combine them.",
            'change_column(..., in_rows_where="depth_m == 30") changes only the rows that meet the condition; the '
            "other rows keep their value. replace_values_in and fill_empty_cells_in take in_rows_where= too.",
            "Across the columns of one row: add_row_summary_column(\"pain_average\", columns=[...], show=\"average\"). "
            "In order: turn_into_categories(\"nurse_rating\", in_order=[\"mild\", \"moderate\", \"severe\"]). "
            "Lists in a cell: split_into_rows(\"crew\", separator=\";\").",
        ],
        task=[
            'In the tidied lab table, look for rows that repeat in sample_id and gene only '
            '(show_duplicate_rows(columns=[...])).',
            'Fix the station names of the samples (remove_extra_spaces_in, then replace_values_in("station", '
            '"st.3", with_value="St.3")) and join the stations again: how many rows find no station now?',
            "Split the crew of each sample into rows, one person each, and count how many samples each person "
            "took.",
        ],
        solutions=[
            (_sx("""\
                import simplydata as sdata
                lab = sdata.table(sdata.get_example("fjord_lab"))
                lab.remove_rows_that_are_all_empty()
                lab.remove_duplicate_rows()
                lab.show_duplicate_rows(columns=["sample_id", "gene"])"""),
             "After the exact repeats are gone, each sample and gene appears once, so no row repeats."),
            (_sx("""\
                import simplydata as sdata
                samples = sdata.table(sdata.get_example("fjord_samples"))
                stations = sdata.table(sdata.get_example("fjord_stations"))
                stations.clean_column_names()
                samples.remove_extra_spaces_in("station")
                samples.replace_values_in("station", "st.3", with_value="St.3")
                samples.join_with(stations, using="station", keep="all rows from this table", with_match_column=True)
                samples.count_each("found in")"""),
             "One sample still finds no station: its name looks like Råvika but is typed with other characters "
             "(an a and a ring), which no space or capital explains."),
            (_sx("""\
                import simplydata as sdata
                samples = sdata.table(sdata.get_example("fjord_samples"))
                samples.split_into_rows("crew", separator=";")
                samples.count_each("crew")"""),
             "Each sample now has one row per person who took it, so count_each counts the samples of each person."),
        ],
        words=["sdata.table", "table.remove_rows_that_are_all_empty", "table.remove_columns_that_are_all_empty",
               "table.show_duplicate_rows", "table.remove_duplicate_rows", "table.clean_column_names",
               "table.turn_into_numbers", "table.remove_rows_found_in", "table.keep_rows_found_in", "table.join_with",
               "table.count_each", "table.add_row_number_column", "table.add_running_column", "table.keep_first_rows",
               "table.keep_groups_where", "table.find_median_of", "table.split_into_rows",
               "table.add_row_summary_column", "table.turn_into_categories", "table.spread_into_columns",
               "table.change_column"],
    ),
]


def _wrap(text: str, indent: str = "", width: int = WIDTH) -> str:
    return textwrap.fill(text, width, initial_indent=indent, subsequent_indent=indent)


def lesson_number(title: str) -> int:
    """The number of the lesson with this title (sdata.show_lesson(n)). The 30-day guide and the tests find a
    lesson by its title, so its number can change when lessons are added before it."""
    for number, les in enumerate(LESSONS, start=1):
        if les["title"] == title:
            return number
    raise KeyError(title)


# The optional life-science lesson. Agreed order across branches: S2's "Working with a model" is lesson 21,
# this one 22, v0.6's lessons 23 to 26.
RISKS_LESSON = "Risks, diagnostic tests and agreement"


def lesson_code(number: int) -> list[str]:
    """The code of each part of a lesson, ready to run (used by the tests)."""
    return ["\n".join(code for code, _ in steps) for _, steps in LESSONS[number - 1]["parts"]]


def _list_lessons() -> None:
    print(f"Learn simplydata in one day: {len(LESSONS)} lessons of about 30 minutes.")
    print("Lessons 1 to 8 teach charts, lessons 9 to 12 teach tables, lesson 13 teaches numbers,")
    print("lesson 14 teaches statistical tests and lesson 15 puts it all together, from a question")
    print(f"to a figure. Lessons 16 to {len(LESSONS)} go further: models, patterns across many columns,")
    print("survival and planning a study, fitting curves and finding answers, distributions, working")
    print("with a model, risks, diagnostic tests and agreement, time series, forecasts, cycles,")
    print("(optional) systems, percentiles and outliers, effects that depend on each other, more survival,")
    print("combining studies (meta-analysis), the diversity and make-up of communities, and directions,")
    print("places and extremes at a coastal station.\n")
    for i, les in enumerate(LESSONS, start=1):
        print(f"  sdata.show_lesson({i}){' ' * (5 - len(str(i)))}{les['title']}")
    print("\nStart with sdata.show_lesson(1). Each lesson ends with a small task to try yourself.")
    print("Rather learn an hour a day? sdata.start_30_days() spreads the everyday lessons over 30 days, with")
    print("warm-up questions and a project of your own; then type sdata.show_today() each day.")


def lesson_solutions(number: int) -> list[tuple[str, str]]:
    """The worked solution of each task of a lesson: [(code, explanation), ...]."""
    return list(LESSONS[number - 1]["solutions"])


def show_lesson(number=None, solutions=False) -> None:
    """A lesson: an example to run, what each line does, and a task. sdata.show_lesson(1)

    sdata.show_lesson() on its own lists all the lessons. solutions=True also shows a worked
    solution for each task: sdata.show_lesson(3, solutions=True).
    """
    if number is None:
        _list_lessons()
        return None
    if isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= len(LESSONS):
        raise SimplydataError(
            f"There are lessons 1 to {len(LESSONS)}, so sdata.show_lesson({number!r}) does not exist.\n"
            "Start with sdata.show_lesson(1), or type sdata.show_lesson() to see them all."
        )
    les = LESSONS[number - 1]
    title = f"Lesson {number} of {len(LESSONS)}: {les['title']}"
    print(title)
    print("=" * len(title))
    print("\nIn this lesson you will learn")
    for item in les["learn"]:
        print(f"  - {item}")
    if les.get("needs_r"):
        print("\nNeeds R")
        print(textwrap.fill(les["needs_r"], WIDTH, initial_indent="  ", subsequent_indent="  "))
    for i, (intro, steps) in enumerate(les["parts"], start=1):
        print()
        heading = "Example" if len(les["parts"]) == 1 else f"Example {i}"
        print(heading)
        print("-" * len(heading))
        print(_wrap(intro))
        print()
        for code, _ in steps:
            print(f"    {code}")
        print("\nWhat each line does")
        for code, explain in steps:
            if not explain:
                continue
            print(f"    {code}")
            print(_wrap(explain, "        "))
    if les.get("notes"):
        print("\nGood to know")
        for note in les["notes"]:
            print(textwrap.fill(note, WIDTH, initial_indent="  - ", subsequent_indent="    "))
    print("\nTry it yourself")
    for i, task in enumerate(les["task"], start=1):
        print(textwrap.fill(task, WIDTH, initial_indent=f"  {i}. ", subsequent_indent="     "))
    if solutions:
        print("\nSolutions")
        for i, (code, explain) in enumerate(les["solutions"], start=1):
            print()
            print(textwrap.fill(explain, WIDTH, initial_indent=f"  {i}. ", subsequent_indent="     "))
            print(textwrap.indent(code, "        "))
    else:
        print(f"\nStuck? sdata.show_lesson({number}, solutions=True) shows a worked solution for each task.")
    print()
    if number < len(LESSONS):
        print(f"Next: sdata.show_lesson({number + 1})  {LESSONS[number]['title']}")
    else:
        print("You have finished all the lessons. Well done!")
    return None
