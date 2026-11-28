"""Other names: the words people bring from other tools and from everyday maths.

People choose the same name for a thing surprisingly rarely (Furnas et al. 1987, "The vocabulary
problem in human-system communication"), so a system that knows only one name fails most
first tries. simplydata keeps one word for each idea, but it knows the other names too: typing
one of them never runs anything, it gives a friendly pointer, "In simplydata this is ...".

Each list below is (how the simplydata word is written, the other names that point to it).
The tests check that every target is a real word and that no other name is a word itself.

Some names mean one thing on a table and another inside pandas' and Polars' namespaces: str.replace changes part of
a text, but replace changes whole values; dt.round rounds dates, round rounds numbers; groupby().filter keeps
groups, filter keeps rows. Those names have their own lists (_TEXT for .str, _DATES for .dt, _GROUPS for groupby),
and sdata.help("str.replace") or sdata.help("Series.str.contains") looks there first (other_name_parts below).
"""

from __future__ import annotations

import re

# sdata.<name>: top-level words, and words people expect on sdata that live on a table or a chart.
_SDATA = [
    ('sdata.get_example("lung", from_r_package="survival")', "get_rdataset rdata load_dataset"),
    ('sdata.get_example() lists the practice tables, and sdata.get_example("marks") gives one', "get_dataset_names"),
    ('sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22])',
     "ttest_ind_from_stats tsum_test"),
    ('sdata.make_run_of_dates("2026-01-01", to="2026-12-31", every="day")', "date_range seq.Date datetime_range daterange"),
    ('sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=100)', "chirp square sawtooth gausspulse unit_impulse"),
    ('sdata.make_window_shape("hann", how_many=64)', "hann hanning hamming blackman get_window"),
    ("sdata.find_inverse_fourier_transform(table)", "ifft irfft"),
    ('sdata.number_list("call.wav")', "readWave wavread read_wav"),
    ('sdata.system("1 / (s**2 + 2*s + 5)")',
     "lti dlti tf ss zpk TransferFunction StateSpace ZerosPolesGain transfer_function state_space"),
    ("sdata.frequency_filter(keep_below=10, time_step=0.005)", "freqz sosfreqz iirfilter iirdesign"),
    ('sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5])',
     "minimize minimise optimize optimise optim minimize_scalar fmin fminbound argmin nlm "
     "nlminb fminsearch"),
    ('sdata.find_where_biggest("x * (10 - x)", between=[0, 10])', "maximize maximise argmax fmax"),
    ('sdata.find_where_smallest("2*x + 3*y", rules=["x + y >= 4", "x >= 0", "y >= 0"])',
     "linprog lp milp linear_programming"),
    ('sdata.solve("x**3 - 2*x = 5", between=[0, 3])',
     "root roots fsolve brentq brenth bisect newton root_scalar uniroot polyroot nleqslv fzero zeros_of"),
    ('table.fit_formula("population = a * exp(b * (year - 2000))"), on a table',
     "curve_fit nls nlsLM least_squares leastsq"),
    ('table.fit_curve(x="hours", y="marks", of_degree=2), on one subject (one row per child), on a table', "polyfit"),
    ('table.fit_line(x="hours", y="marks"), on one subject (one row per child), on a table', "linregress lm ols"),
    ('table.find_values_at("population", at={"year": [2001, 2003]}), on a table',
     "interpolate interp interp1d approx approxfun splinefun CubicSpline pchip PchipInterpolator "
     "make_interp_spline"),
    # families for 100 %, batch 16 (G6): "spline" is the other name of curve_through_points
    ("sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.find_value_at(12): a smooth "
     'curve to read anywhere; table.find_values_at("population", at={"year": [2001, 2003]}) gives values in a table',
     "spline"),
    ('table.make_map_of("height", across=["east", "north"]), on a table', "griddata interp2d RBFInterpolator"),
    ('sdata.distribution("normal", average=50, standard_deviation=10).find_density_at(60)', "pdf dnorm pmf dbinom"),
    ('sdata.distribution("normal", average=50, standard_deviation=10).find_chance_that_value(is_below=60)',
     "cdf pnorm pbinom sf"),
    ('sdata.distribution("normal", average=50, standard_deviation=10).find_percentile(95), or '
     '.find_cut_off(with_chance_above=0.025) for a critical value', "ppf qnorm isf"),
    ("numbers.find_percentile(90) for numbers, table.find_percentile_of(\"marks\", 90) for a column, or "
     "sdata.distribution(\"normal\").find_percentile(90)", "quantile percentile"),
    ('sdata.make_random_numbers(how_many=100, average=50, standard_deviation=10, with_seed=1), or '
     'sdata.distribution("gamma", shape=2).make_random_numbers(how_many=100)', "rvs rnorm runif rand randn random"),
    ('sdata.distribution("normal", average=50, standard_deviation=10)', "norm rv_continuous"),
    ('table.fit_distribution_to("days", "gamma"), on a table', "fit fitdistr fitdist fit_distribution"),
    ('sdata.table("my_file.csv")', "read_csv read_excel read_table read_parquet read_json DataFrame data_frame "
     "tibble read"),
    ('sdata.table("survey.sav") for SPSS, or sdata.table("survey.dta") for Stata', "read_spss read_stata"),
    # families for 100 %, batches 1-2 (approved by Manish 2026-11-28): readers and makers of plan section 2.1
    ('sdata.table("stations.html", table_number=1), a web page saved on this computer', "read_html"),
    ('sdata.table("station.txt", fixed_widths=[10, 6, 6])', "read_fwf"),
    ('sdata.table("clipboard"), what you copied', "read_clipboard"),
    ('sdata.table("samples.json"): values inside values become columns of their own (site.name)', "json_normalize"),
    ('sdata.make_run_of_dates("2026-12-01", to="2026-12-31", every="working day")', "bdate_range"),
    ('table.turn_into_dates("seconds", from_unix_seconds=True), on a table of seconds since 1970', "from_epoch"),
    ('table.add_column("days", "count_working_days(start, end)"), on a table', "business_day_count"),
    ('sdata.table("big.csv", fast=True): Polars reads it at once (simplydata runs no lazy plans; they are left to '
     "Polars: table.as_polars())",
     "scan_csv scan_parquet scan_ipc scan_ndjson scan_delta scan_iceberg scan_lines scan_lance "
     "scan_pyarrow_dataset scan_arrow_c_stream scan_external_reader collect_all collect_all_async defer "
     "explain_all"),
    ("table.as_polars(), then pl.align_frames(...) in Polars: simplydata tables have no row index to line up",
     "align_frames"),
    ('table.as_pandas(), then df.groupby("class").apply(my_function), and give the result to sdata.table to come '
     "back", "map_groups"),
    # Tables finishing PR (API audit 2026-11-25): a table from data already in Python
    ('sdata.table({"name": ["Asha", "Ben"], "marks": [61, 73]}) for a dict of columns, a list of rows (dicts), '
     "or a pandas or Polars table", "from_dict from_dicts from_records from_arrow from_numpy from_pandas "
                                    "from_dataframe"),
    # Tables phase, batch 3 (approved by Manish 2026-11-25)
    ("sdata.run_sql(\"SELECT station, avg(nitrate) AS nitrate FROM 'river.csv' GROUP BY station\")",
     "sql read_sql read_sql_query sqldf dbGetQuery duckdb query"),
    ('sdata.table("lab.sqlite", table_name="samples")',
     "read_sql_table dbReadTable read_database read_feather read_ipc read_ndjson read_xml read_sas"),
    # Numbers phase, batch 3 (approved by Manish 2026-11-25): exact maths (SymPy), areas and paths over time
    ('sdata.formula("(x + 2)**2 - 4")', "symbols Symbol sympify parse_expr syms sym"),
    ('sdata.formula("(x + 2)**2 - 4"), then formula.make_simpler(), formula.turn_into_sum() or '
     'formula.turn_into_product()',
     "simplify expand factor factorise factorize"),
    ('sdata.formula("x**3 - 2*x"), then formula.find_slope_formula() or formula.find_area_formula()',
     "diff Derivative Integral deriv derivative"),
    ('sdata.formula("x**3 - 2*x"), then formula.find_value_at(x=2) or formula.put_in(x="y + 1")',
     "subs evalf lambdify matlabFunction substitute"),
    ('sdata.formula("x**3 - 2*x"), then formula.show_as_latex()', "latex pprint pretty"),
    ('sdata.formula("sin(x) / x"), then formula.find_limit_as("x", goes_to=0) or formula.find_taylor_series(around=0)',
     "limit series taylor"),
    ('sdata.solve("x**2 = 2", exactly=True)', "solveset linsolve"),
    ('sdata.find_area_under("exp(-x**2)", between=[0, "infinity"])',
     "quad integrate integral quad_vec fixed_quad romberg"),
    ('sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]})', "dblquad tplquad nquad integral2 integral3"),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3})',
     "solve_ivp odeint ode dsolve lsoda ode45 ode15s ode23"),
    # Numbers phase, batch 4 (approved by Manish 2026-11-26): the SymPy words
    ('sdata.formula("(3*x + 5) / ((x + 1)*(x + 2))"), then formula.turn_into_partial_fractions()',
     "apart partial_fractions partfrac"),
    ('sdata.formula("a*x**2 + b*x**2 + a*x - x"), then formula.group_by_powers_of("x")', "collect coeffs"),
    ('sdata.formula("sqrt(2)"), then formula.find_value_at() for a number, or formula.show_as_decimal(digits=50) '
     'for many digits', "N vpa"),
    ('sdata.formula("sqrt(k**2)", letters_are={"k": "positive"})', "assumptions refine assume Q"),
    ('sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])', "summation Sum nsum symsum is_convergent"),
    ('sdata.solve("x**2 - 4 > 0", exactly=True)',
     "reduce_inequalities solve_univariate_inequality solve_poly_inequality"),
    ("sdata.number_grid([[2, 1], [1, 2]]), then grid.find_determinant()", "det"),
    ("sdata.number_grid([[2, 1], [1, 2]]), then grid.take_inverse()", "inv"),
    ("sdata.number_grid([[2, 1], [1, 2]]), then grid.find_eigenvalues()", "eig eigvals eigvalsh eigen eigenvals"),
    ("sdata.number_list(0, to=10, how_many=50)", "linspace arange seq seq_len array"),
    # NumPy + SciPy phase, batch 2 (approved by Manish 2026-11-25)
    ('sdata.number_block("sst.nc", values="sst")',
     "open_dataset open_mfdataset open_dataarray Dataset nc_open ncvar_get rast read_stars ncread"),
    ('sdata.show_whats_inside("sst.nc")', "ncdump ncinfo ncdisp"),
    ('sdata.number_list("readings.txt", empty_values=[-999])', "genfromtxt loadtxt"),
    ("sdata.count_ways_to_choose(3, out_of=10)", "comb binom nchoosek choose"),
    ("sdata.count_ways_to_order(3, out_of=10)", "perm perms"),
    # NumPy + SciPy phase, batch 1 (approved by Manish 2026-11-25)
    ("sdata.number_block(of_shape=(24, 8, 12), filled_with=0)",
     "ndarray tensor zeros_like ones_like full_like empty_like empty DataArray"),
    ('sdata.stack_up([a, b, c], as_new_direction="image")', "stack dstack column_stack"),
    ("sdata.stretch_to_same_shape(a, b)", "broadcast_arrays"),
    ("sdata.number_grid(rows=2, columns=3, filled_with=0)", "zeros ones matrix full"),
    ('sdata.chart(table), then chart.draw_lines(x="year", y="population")', "plot figure subplots ggplot"),
    ('table.compare_averages_of("marks", for_each_group_in="class"), on one subject (one row per child), on a table',
     "ttest ttest_ind t_test anova aov f_oneway"),
    ('table.compare_averages_of("marks", for_each_group_in="class", based_on="ranks"), on one subject (one row per child), on a table',
     "mannwhitneyu wilcox_test kruskal kruskal_test"),
    ('table.compare_counts_of("result", for_each_group_in="class"), on a table', "chi2_contingency chisq_test fisher_exact"),
    ('table.find_correlation_between("hours", "marks"), on one subject (one row per child), on a table', "pearsonr spearmanr kendalltau cor cor_test"),
    ('table.compare_shape_to("marks", "normal"), on one subject (one row per child), on a table', "shapiro shapiro_test normaltest anderson"),
    ("sdata.find_how_many_needed(effect_size=0.5, power=0.8)", "power_t_test solve_power pwr"),
    # S3b-2: planning a study (the field's names for the new options)
    ('sdata.find_how_many_needed(for_test="compare_survival", effect_size=0.7, percents=[30, 40])',
     "nEvents schoenfeld freedman ssizeCT ssizeEpi power_logrank logrank_power survival_power hazard_ratio"),
    ("sdata.find_how_many_needed(effect_size=0.5, in_clusters_of=20, alike_within_clusters=0.05)",
     "design_effect cluster_size cluster_randomised cluster_randomized n4means intracluster_correlation"),
    ('sdata.find_how_many_needed(for_test="explain", effect_size=0.15, using=["temperature", "salinity", "depth"])',
     "pwr_f2_test f2 FTestPowerF2 regression_power"),
    ('sdata.find_how_many_needed(for_test="explain", outcome="yes or no", using=["dose"], percents=[20], effect_size=1.5)',
     "power_z_logistic wp_logistic logistic_power"),
    ("sdata.find_how_many_needed(interval_width=10, percents=[30])", "prec_prop precision_proportion"),
    ("sdata.find_chance_of_finding(by_running=one_study, tries=1000)",
     "simulate_power power_simulation simulated_power monte_carlo_power simr"),
    ('sdata.start_30_days(track="python") once, then sdata.show_today() each day', "course tutorial"),
    ('sdata.show_packages_used(), or sdata.show_packages_used(save_as="references.bib") for BibTeX',
     "cite citation citations references cite_packages sessionInfo session_info bibtex"),
]

# table.<name>
_TABLE = [
    ('table.repeat_each_row_by("count")', "uncount expand_counts repeat_rows"),
    ('table.find_average_of("marks", for_each_group_in="class")', "groupby group_by"),
    # families for 100 %, batches 1-2: different measures for different columns, one row per group
    ('table.find_summary_of(show={"marks": ["average", "count"], "hours": ["total"]}, for_each_group_in="class")',
     "aggregate agg"),
    ('table.join_with(other_table, using="name")', "merge join left_join inner_join"),
    # Tables phase, batch 1 (approved by Manish 2026-11-25)
    ('table.join_with(other_table, using="name", keep="all rows from the other table")', "right_join"),
    ('table.join_with(other_table, using="name", keep="all rows from both")', "full_join outer_join"),
    ('table.keep_rows_found_in(other_table, using="name")', "semi_join intersect"),
    # Tables finishing PR: isin with a list is keep_rows_where(is_one_of=); with another table, keep_rows_found_in
    ('table.keep_rows_where("class", is_one_of=["A", "B"]) for a list of values, or '
     'table.keep_rows_found_in(other_table, using="name") for the values of another table', "isin is_in"),
    ('table.remove_rows_found_in(other_table, using="name")', "anti_join setdiff except"),
    ("table.clean_column_names()", "clean_names make_clean_names snake_case"),
    ("table.remove_rows_that_are_all_empty()", "remove_empty drop_empty_rows"),
    ("table.remove_columns_that_are_all_empty()", "remove_empty_columns drop_empty_columns"),
    ('table.show_duplicate_rows(columns=["name", "subject"])', "duplicated is_duplicated get_dupes find_duplicates"),
    ('table.add_row_summary_column("average", columns=["pain_week_0", "pain_week_4"], show="average")',
     "rowMeans rowSums rowwise c_across mean_horizontal sum_horizontal max_horizontal min_horizontal"),
    ('table.turn_into_categories("nurse_rating", in_order=["mild", "moderate", "severe"])',
     "factor as_factor Categorical CategoricalDtype Enum fct_relevel reorder_categories set_categories"),
    ('table.split_into_rows("genes", separator=";")', "explode separate_rows separate_longer_delim unnest_longer"),
    ('table.add_running_column("sales_so_far", from_column="sales", show="total")',
     "cumsum cum_sum expanding cumall cumany cummean"),
    # Tables finishing PR: the running biggest, smallest, product and count have their own show=
    ('table.add_running_column("best_so_far", from_column="sales", show="biggest")', "cummax cum_max"),
    ('table.add_running_column("lowest_so_far", from_column="sales", show="smallest")', "cummin cum_min"),
    ('table.add_running_column("growth_so_far", from_column="factor", show="product")', "cumprod cum_prod"),
    ('table.add_running_column("filled_so_far", from_column="sales", show="count")', "cum_count"),
    ('table.add_row_number_column("number", for_each_group_in="station")',
     "cumcount row_number with_row_index with_row_count row_index seq_along rowid"),
    ('table.keep_groups_where("average(marks) >= 50", for_each_group_in="school")',
     "filter_groups groupby_filter having"),
    # Tables phase, batch 2 (approved by Manish 2026-11-25)
    ('table.count_rows() for the rows, or table.count_columns() for the columns', "shape"),
    ("table.count_columns()", "width ncol"),
    ('table.rename_columns({"temperature": "temp", "rain": "rain_mm"})', "add_prefix add_suffix rename_with setnames"),
    ('table.add_missing_combinations_of("year", "country"), or table.add_missing_dates("date") for a run of dates',
     "complete"),
    ('table.add_missing_combinations_of("year", "country")', "crossing"),
    ('table.round_dates_in("date", down_to="month")', "floor_date ceiling_date round_date"),
    ('table.change_time_zone_in("time", to="UTC", recorded_in="Europe/Oslo")',
     "tz_convert tz_localize with_tz force_tz convert_time_zone replace_time_zone"),
    ('table.spread_into_yes_no_columns("fruit")', "get_dummies to_dummies one_hot dummy_cols"),
    ('table.fill_empty_cells_from(other_table, using="id")', "combine_first rows_patch"),
    ('table.fill_empty_cells_in("phone", from_column="mobile") from another column, or '
     'table.fill_empty_cells_from(other_table, using="id") from another table', "coalesce"),
    ('table.add_rank_column("place", from_column="marks", when_tied="no gaps")', "dense_rank min_rank"),
    ('table.add_group_column("quarter", from_column="marks", into_equal_groups=4)', "qcut ntile cut_number"),
    ('table.count_rows(for_each_group_in="shop", across="fruit") for a count table, or '
     'table.compare_counts_of("result", for_each_group_in="class") to test it', "crosstab"),
    ('table.count_rows(for_each_group_in="shop", across="fruit", with_totals=True)', "addmargins adorn_totals"),
    ('table.turn_into_text("date", written_like="31.12.2026")', "strftime"),
    ('table.turn_into_dates("when", written_like="03/15/2026")', "strptime"),
    ('table.add_column("check_on", from_column="date", plus="1 month")', "offset_by"),
    ('table.add_column_with_part_of_date("weekend", from_column="date", part="is weekend")',
     "is_weekend days_in_month is_leap_year is_month_end"),
    # Tables phase, batch 3 (approved by Manish 2026-11-25)
    ('table.add_zeros_in_front_of("sample_id", to_length=3)', "zfill str_pad pad_start rjust formatC"),
    ('table.find_summary_of("level", show=["first", "biggest", "smallest", "last"], for_each_group_in="date", '
     'every="month")', "ohlc"),
    ('table.gather_into_rows(starts_with="pain_week_", names_to="week", values_to="pain")', "wide_to_long"),
    ('table.move_columns("marks", to="start")', "relocate reorder_columns move_column"),
    ("table.show_rows_with_empty_cells_in()", "complete.cases incomplete_cases show_missing"),
    ("table.show_differences_from(other_table)", "compare diffdf compare_df"),
    ("table.check_if_same_as(other_table)", "equals identical all_equal all.equal frame_equal assert_frame_equal"),
    ('table.join_with(rain, using="date", match="nearest before", within="2 days")',
     "merge_asof join_asof rolling_join"),
    ('table.join_with(other_table, keep="every combination")', "cross_join"),
    ('table.run_sql("SELECT station, avg(nitrate) AS nitrate FROM data GROUP BY station")',
     "sql sqldf duckdb"),
    ('table.make_one_table_for_each_group_in("station")', "partition_by group_split split"),
    ("table.as_list()", "to_dict to_dicts to_records iterrows itertuples iter_rows"),
    ('table.save("results.sqlite", in_table="river")', "to_sql dbWriteTable write_database"),
    ("table.add_rows_from(other_table)", "concat append rbind vstack bind_rows"),
    ('table.spread_into_columns(names_from="subject", values_from="marks")',
     "pivot pivot_wider pivot_table spread unstack"),
    ('table.gather_into_rows(["temperature", "rain"])', "melt pivot_longer gather stack unpivot"),
    ("table.swap_rows_and_columns()", "transpose T t"),
    ("table.make_copy(), as in backup = table.make_copy()", "copy clone deepcopy duplicate"),
    ("table.show_first_rows()", "head"),
    ("table.show_last_rows()", "tail"),
    ('table.keep_rows_where("marks", is_above=50)', "loc query subset"),
    # Tables finishing PR: pandas DataFrame.filter picks columns by name; Polars, dplyr and R filter keep rows
    ('table.keep_rows_where("marks", is_above=50) to keep rows (Polars and dplyr filter), or '
     'table.keep_columns(contains="week") to keep columns by their names (pandas DataFrame.filter)', "filter"),
    # pandas where() and mask() replace values; SQL WHERE keeps rows
    ('table.replace_values_in("marks", is_above=100, with_value=100) or table.change_column("marks", value=0, '
     'in_rows_where="marks < 0") to replace values (pandas where and mask), or table.keep_rows_where("marks", '
     "is_above=50) to keep rows (SQL WHERE)", "where"),
    ("table.keep_rows_by_position(10, to=20)", "iloc slice take gather_every nth"),
    ("table.remove_rows_by_position([12, 40])", "drop_index"),
    ('table.get_cell_at(row=3, column="marks")', "at iat item get_value"),
    ('table.keep_columns(of_kind="number")', "select_dtypes"),
    ('table.reverse_rows() to turn the table upside down, or table.sort_by("marks", biggest_first=True) for an '
     "order by a column", "reverse flip flipud"),
    ('table.replace_values_in("marks", is_above=100, with_value=100)', "mask clip"),
    ('table.keep_columns("name", "marks")', "select"),
    ('table.remove_columns("height")', "drop"),
    ('table.rename_column("marks", to="score")', "rename"),
    ('table.sort_by("marks")', "sort_values arrange order sort"),
    ("table.remove_rows_with_empty_cells_in()", "dropna drop_nulls na_omit"),
    ('table.fill_empty_cells_in("price", with_the="median")', "fillna fill_null fill_nan replace_na"),
    ('table.find_values_at("population", at={"year": [2001, 2003]}) for values between the known points, or '
     'table.fill_empty_cells_in("price", with_the="line between neighbours") to fill gaps',
     "interpolate interp interp1d approx approxfun spline splinefun CubicSpline pchip"),
    ('table.make_map_of("height", across=["east", "north"])', "griddata interp2d"),
    ("table.remove_duplicate_rows()", "drop_duplicates distinct"),
    # families for 100 %, batches 1-2 (G18): pandas Series.unique() and pd.unique are the different values of one column
    ('table.get_different_values_in("class") for the different values of one column (pandas Series.unique, Polars '
     'unique); table.remove_duplicate_rows() for whole rows', "unique"),
    ("table.describe_columns()", "describe info glimpse dtypes"),
    # R str() describes a table; pandas .str holds the text steps (sdata.help("str.replace") names each one)
    ('table.describe_columns() for R str(); the text steps of pandas and Polars .str are table words that take '
     'the column name (str.replace is replace_text_in), and help on a name such as "str.replace" gives the word',
     "str"),
    ('table.add_column_with_part_of_date("year", from_column="date", part="year"): the date steps of pandas and '
     'Polars .dt are table words that take the column name, and help on a name such as "dt.year" gives the word',
     "dt"),
    ('table.find_summary_of("marks", for_each_group_in="class")', "summary summarise summarize"),
    ('table.find_average_of("marks")', "mean"),
    ('table.find_total_of("marks")', "sum"),
    ('table.find_smallest_of("marks")', "min minimum"),
    ('table.find_biggest_of("marks")', "max maximum"),
    ('table.find_standard_deviation_of("marks")', "std sd"),
    ('table.find_median_of("marks")', "median"),
    ('table.find_percentile_of("marks", 90)', "quantile percentile"),
    ('table.add_z_score_column("marks_z", from_column="marks")', "zscore z_score standardize standardise"),
    ('table.find_interval_of("marks", "median"), on one subject (one row per child)', "bootstrap boot"),
    ('table.count_each("class")', "value_counts table tabulate"),
    ('table.count_different_values_in("name")', "nunique n_distinct n_unique"),
    ('table.find_most_common_of("marks")', "mode"),
    ("table.count_rows()", "len nrow height"),
    # Tables finishing PR: pandas and Polars count() count the filled cells of each column; dplyr count() the rows
    # of each group
    ('table.count_rows() for the rows, table.count_each("class") for the rows of each group (dplyr count), or '
     "table.describe_columns() for the filled and empty cells of each column (pandas and Polars count)", "count"),
    ("table.get_column_names()", "columns names colnames"),
    ('table.turn_into_numbers("price")', "as_numeric to_numeric"),
    ('table.turn_into_numbers("price"), or turn_into_text, turn_into_dates or turn_into_categories for the other '
     "kinds", "astype cast"),
    ('table.turn_into_dates("date")', "to_datetime as_date"),
    ('table.turn_into_lowercase("name")', "lower tolower"),
    ('table.turn_into_uppercase("name")', "upper toupper"),
    ('table.remove_extra_spaces_in("name")', "strip trimws str_trim"),
    ('table.round_numbers_in("price", 1)', "round"),
    ('table.save("results.csv")', "to_csv write_csv to_parquet write_parquet"),
    ('table.save("results.xlsx")', "to_excel write_xlsx"),
    ('table.save("results.xlsx", in_sheet="cleaned"), which keeps the other sheets of the file',
     "ExcelWriter addWorksheet writeData saveWorkbook create_sheet add_sheet write_excel"),
    ("table.start_chart()", "plot ggplot"),
    ('table.add_column("marks_per_hour", "marks / hours")', "assign mutate with_columns transform"),
    ('table.replace_values_in("class", "A", with_value="Alpha")', "replace recode"),
    ('table.add_previous_value_column("last_year", from_column="population"), or rows_ahead=1 for the next value '
     "(shift(-1), lead)", "shift lag lead"),
    ('table.add_change_column("growth", from_column="population")', "diff pct_change"),
    ('table.add_rolling_column("smooth", from_column="temperature")', "rolling rollmean"),
    ('table.add_rank_column("rank", from_column="marks")', "rank"),
    ('table.add_group_column("result", from_column="marks", cut_at=[60], names=["below 60", "60 or more"])', "cut"),
    ('table.add_is_empty_column("no_price", from_column="price")', "isna isnull is_na is_null"),
    ("table.keep_random_rows(5, with_seed=1)", "sample sample_n slice_sample"),
    ('table.keep_biggest_rows(3, by="marks")', "nlargest top_n slice_max"),
    ('table.keep_smallest_rows(3, by="marks")', "nsmallest slice_min"),
    ('table.find_correlation_between("hours", "marks"), on one subject (one row per child)', "corr cor pearsonr spearmanr"),
    ('table.fit_formula("population = a * exp(b * (year - 2000))")', "curve_fit nls nlsLM least_squares"),
    ('table.fit_curve(x="hours", y="marks", of_degree=2), on one subject (one row per child)', "polyfit"),
    ('table.fit_line(x="hours", y="marks") for one column (on one subject: one row per child), or table.explain("marks", using=["hours", '
     '"breakfast"]) for several', "linregress lm ols"),
    ('table.explain("passed", using=["hours"], outcome="yes or no")', "glm logit lmer glmer"),
    ('table.explain("marks", using=["hours", "breakfast"]), which prints R squared (or a pseudo R squared), AIC '
     'and BIC; table.compare_models(...) compares two models', "r2 r_squared rsquared pseudo_r2 r2_nakagawa aic bic"),
    ('table.explain("marks", using=["hours"], grouped_by="school", effects="for the whole population")',
     "gee geeglm"),
    ('table.explain("marks", using=["hours", "breakfast"], curve_for="hours")',
     "gam mgcv GLMGam smooth_terms"),
    ('table.check_model_of("marks", using=["hours", "breakfast"]), which prints the variance inflation factors',
     "vif variance_inflation_factor collinearity multicollinearity"),
    ('table.find_model_averages_of("marks", for_each_group_in="school", using=["hours"])',
     "marginal_means_of adjusted_averages_of emmeans lsmeans marginal_means estimated_marginal_means"),
    ('table.check_model_of("marks", using=["hours", "breakfast"])',
     "diagnostics model_diagnostics residual_plots plot_regress_exog"),
    ('table.show_rows_that_pull_model("marks", using=["hours", "breakfast"])',
     "show_influential_rows influence influence_measures cooks_distance outlier_test"),
    ('table.compare_models("marks", using=["hours"], against=["hours", "breakfast"])',
     "lrtest compare_lr_test compare_f_test anova_lm"),
    ('table.explain("marks", using=["hours", "breakfast"], robust_errors=True)',
     "vcovHC sandwich coeftest robust_standard_errors heteroskedasticity_robust"),
    ('table.explain("price", using=["shop"], weights="count")', "wls weighted_least_squares var_weights"),
    ('table.explain("passed", using=["hours"], outcome="yes or no", show="risk ratios")',
     "modified_poisson log_binomial logbin relative_risk_regression"),
    ('table.explain("passed", using=["hours"], outcome="yes or no"), which prints Nagelkerke\'s and Tjur\'s pseudo R '
     'squared too', "r2_nagelkerke r2_tjur nagelkerke tjur"),
    ('table.explain("case", using=["smoker"], outcome="yes or no", matched_by="pair")',
     "clogit conditional_logit ConditionalLogit"),
    ('table.explain("marks", using=["hours"], giving_outliers_less_weight=True)',
     "rlm RLM huber robust_regression lmrob"),
    ('table.explain("marks", using=["hours", "breakfast"], show="standardised effects")',
     "standardize_parameters standardise_parameters lm_beta standardized_coefficients"),
    ('table.explain("marks", using=["hours", "breakfast"], curve_for="hours", with_knots=3)',
     "ns natural_spline natural_cubic_spline"),
    ('table.explain("passed", using=["hours"], outcome="yes or no", interval_by="profile")',
     "profile_likelihood confint_profile"),
    ('table.explain("passed", using=["hours"], outcome="yes or no", p_value_by="likelihood ratio")',
     "drop1 likelihood_ratio_test"),
    ('table.explain("marks", using=["hours"], grouped_by="school", crossed_with="class")',
     "crossed_random_effects"),
    ('table.explain("germinated", using=["extract"], outcome="yes or no (overdispersed)", out_of="seeds")',
     "quasibinomial quasi_binomial"),
    ('table.explain("thistle", using=["grazed"], outcome="counts with many zeros that vary a lot")',
     "zeroinfl zinb ZeroInflatedNegativeBinomialP"),
    ('table.explain("thistle", using=["grazed"], outcome="counts in two steps")', "hurdle HurdleCountModel"),
    ('table.add_predicted_column("marks", using=["hours"], interval=95, for_new_rows=True)',
     "predict get_prediction prediction_interval confidence_band"),
    ('table.fit_distribution_to("days", "gamma")', "fit fitdistr fitdist"),
    ('table.compare_averages_of("marks", for_each_group_in="class"), on one subject (one row per child)', "ttest ttest_ind t_test anova aov f_oneway"),
    ('table.compare_before_and_after("Maths", "Science")', "ttest_rel paired_t_test wilcoxon mcnemar mcnemar_test "
                                                        "sign_test"),
    ('table.compare_matched_columns("week_0", "week_4", "week_8")', "friedman friedman_test friedmanchisquare cochrans_q "
                                                           "quade_test"),
    ('table.compare_shapes_of("marks", for_each_group_in="class"), on one subject (one row per child)', "ks_2samp anderson_ksamp"),
    ('table.check_if_random_order("marks")', "runs_test runstest_1samp"),
    ('table.find_average_of("marks", weights="people"), or find_standard_deviation_of(..., weights=)',
     "weighted_mean wtd_mean wtd_var DescrStatsW"),
    ('table.fit_distribution_to("marks", "kernel density")', "gaussian_kde KDEUnivariate"),
    ('table.compare_correlations("hours", "marks", for_each_group_in="class"), on one subject (one row per child)', "cocor cocor_indep_groups compare_correlation"),
    ('table.find_correlation_between("hours", "marks", allowing_for="height"), on one subject (one row per child)', "pcor pcor_test partial_corr partial_cor"),
    ('table.find_correlation_between("hours", "marks", test_method="somers") or test_method="gamma", on one subject (one row per child)',
     "somersd SomersDelta GoodmanKruskalGamma goodman_kruskal_gamma"),
    ('table.compare_average_to("marks", 60, test_method="z", standard_deviation=10), on one subject (one row per child)', "z_test ztest"),
    ('table.compare_counts_of("passed", for_each_group_in="age_group", test_method="trend", in_order=[...])',
     "prop_trend_test cochran_armitage"),
    ('table.compare_averages_of("marks", for_each_group_in="class", test_method="jonckheere", in_order=["A", "B", "C"]), on one subject (one row per child)',
     "jonckheere_test jonckheere_terpstra"),
    ('table.compare_matched_columns("week_0", "week_4", "week_8", test_method="page")', "page_trend_test page_test"),
    ('table.compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient", based_on="ranks")',
     "pairwise_wilcox_test pairwise_t_test"),
    ('table.count_each("fruit", interval=95)', "MultinomCI multinomial_proportions_confint"),
    ('table.show_rows_with_outliers("marks", test_method="grubbs"), on one subject (one row per child)', "grubbs_test dixon_test rosnerTest rosner_test"),
    ('table.compare_counts_of("result", for_each_group_in="class")', "chi2_contingency chisq_test fisher_exact"),
    ('table.compare_shape_to("marks", "normal"), on one subject (one row per child)', "shapiro shapiro_test normaltest"),
    ('table.compare_risks("died", for_each_group_in="treatment", against="usual care")',
     "relative_risk riskratio risk_ratio oddsratio odds_ratio epi_2by2 prop_test mantelhaen_test "
     "mantel_haenszel nnt"),
    ('table.compare_rates("infections", time="patient_days", for_each_group_in="ward")',
     "poisson_test rateratio rate_ratio test_poisson_2indep"),
    ('table.rate_of("infections", time="patient_days")', "incidence_rate person_time"),
    ('table.compare_to_truth("rapid_test", truth="infected"), or with a score column the ROC analysis',
     "epi_tests sensitivity specificity ppv npv likelihood_ratio roc roc_auc_score auc youden diagnostic"),
    ('table.compare_accuracy("crp", "procalcitonin", truth="infected")', "roc_test delong"),
    ('table.agreement_between("nurse_rating", "doctor_rating")',
     "cohen_kappa cohens_kappa kappa kappa2 fleiss_kappa kappam_fleiss icc intraclass kripp_alpha krippendorff ccc concordance"),
    ('table.limits_of_agreement("device_a", "device_b")', "bland_altman_stats limits_agreement"),
    ('table.reliability_of(["item_1", "item_2", "item_3"])', "cronbach_alpha cronbach alpha internal_consistency"),
    ('table.add_adjusted_p_value_column("p_adjusted", test_method="benjamini-hochberg")', "p_adjust multipletests fdr"),
    ('table.find_survival_over_time(time="days", event="died")', "survfit kaplan_meier"),
    ('table.compare_survival(time="days", event="died", for_each_group_in="treatment")', "survdiff logrank_test"),
    ('table.explain_survival(time="days", event="died", using=["age"])', "coxph cox"),
    # S3b-3: survival and person-time (the words, and the field's names for the new options)
    ('table.find_risk_over_time(time="time", event="event", value="first_esbl", competing_with="discharged")',
     "cuminc cumulative_incidence competing_risks aalen_johansen cif CumIncidenceRight"),
    ('table.add_time_and_event_columns(from_date="admitted", to_date="discharged", event_date="first_esbl")',
     "stset lexis Lexis person_years follow_up survSplit"),
    ('table.find_survival_over_time(time="days", event="died", average_time_up_to=365)', "rmst rmst2 rmean restricted_mean"),
    ('table.explain_survival(time="days", event="died", using=["age"], allowing_for="treatment") for a stratified '
     'Cox model; table.use_survey_design(weights="weight", strata="school_type") for a survey; '
     'sdata.make_random_assignments(how_many=40, for_each_of=["Bergen", "Oslo"]) for a list for each centre',
     "strata stratified_cox"),
    ('table.explain_survival(time="months", event="outcome", value="relapse", competing_with="death", using=["age"], '
     'test_method="fine-gray")', "fine_gray finegray crr subdistribution"),
    ('table.explain_survival(time="days", event="died", using=["age"]) (with R it prints Harrell\'s C)',
     "c_index harrell harrells_c concordance_index"),
    ('table.explain_survival(time="days", event="died", using=["age"], distribution="weibull")',
     "aft survreg weibull_aft accelerated_failure_time"),
    ('table.find_survival_over_time(time="days", event="died", test_method="life table", at_time_points=[0, 365, 730])',
     "lifetab life_table actuarial"),
    ('table.find_survival_over_time(time="days", event="died", followed_from="entry_day")',
     "delayed_entry left_truncation counting_process"),
    ('table.find_principal_components_of()', "pca prcomp"),
    ('table.add_clusters(how_many=3)', "kmeans hclust"),
    ('table.find_distances_between_rows(measure="bray-curtis")', "pdist vegdist"),
    ('table.add_nmds()', "metaMDS nmds"),
    ('table.compare_profiles_of(for_each_group_in="grazed")', "adonis adonis2 permanova"),
    ('table.find_spectrum_of("signal", sorted_by="time")',
     "periodogram welch psd spec_pgram lombscargle lsp power_spectrum frequencies_of cycles_of"),
    ('table.check_steady_over_time("signal", sorted_by="time")',
     "adfuller adf_test kpss kpss_test unit_root stationarity is_stationary compare_to_steady"),
    ('table.find_autocorrelation_of("signal", sorted_by="time")',
     "acf pacf acovf autocorrelation autocorr partial_autocorrelation ljung_box Box.test"),
    ('table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year")',
     "stl STL decompose seasonal_decompose decomposition split_trend_and_season deseasonalise"),
    ('table.find_trend_of("visitors", sorted_by="month")',
     "mk.test mann_kendall mannkendall sens.slope sen_slope theilslopes smk.test sea.sens.slope"),
    ('table.find_correlation_between("signal", "vibration", rows_back=12, sorted_by="time")',
     "ccf cross_correlation xcorr"),
    ('table.add_missing_dates("date", every="day")', "asfreq upsample fill_missing_dates"),
    ('table.add_smoothed_column("signal_smoothed", from_column="signal", window=11, sorted_by="time")',
     "rolling_smooth savgol smooth_column add_smooth_column"),
    ('table.forecast("visitors", sorted_by="month", repeats_every="year")',
     "predict_future naive snaive meanf rwf HoltWinters holt_winters ExponentialSmoothing exponential_smoothing "
     "arima ARIMA SARIMAX"),
    ('table.compare_forecasts_for("visitors", sorted_by="month", repeats_every="year")',
     "accuracy forecast_accuracy mase backtest"),
    ('table.find_change_points_in("nitrate", sorted_by="date")',
     "cpt.mean cpt.meanvar changepoint change_points changepoints pelt breakpoints detect_changes"),
    # S3a-2: lines and curves
    ('table.fit_dose_response(x="concentration", y="root_length")', "drm drc dose_response ec50 ed50 ld50 lc50"),
    ('table.find_best_power_of("days")', "boxcox box_cox powerTransform yeojohnson yeo_johnson"),
    ('table.fit_line(x="hours", y="marks", test_method="standardised major axis"), on one subject (one row per child)',
     "sma lmodel2 model_ii deming mcreg passing_bablok siegelslopes"),
    ('table.fit_line(x="hours", y="marks", with_bends=1), on one subject (one row per child)', "segmented piecewise_regression davies.test"),
    ('table.explain("marks", using=["hours"], for_percentile=90), on one subject (one row per child)', "quantreg rq quantile_regression QuantReg"),
    ('table.fit_curve(x="hour", y="density", of_kind="logistic growth")',
     "SSlogis SSgompertz SSmicmen SSweibull getInitial selfStart"),
    # S3a-3: checking and comparing
    ('table.find_columns_that_predict("marks", using=["hours", "sleep", "breakfast"])',
     "lasso glmnet cv.glmnet cv_glmnet elastic_net elasticnet LassoCV ElasticNetCV"),
    ('table.find_group_levels_of("marks", using=["hours"], grouped_by="school")', "ranef blup blups random_effects levels group_levels"),
    ('table.explain("marks", using=["hours"], spread_changes_with="school")', "gls varIdent varPower corAR1 corCAR1 GLSAR"),
    ('table.compare_models("marks", using=[["hours"], ["hours", "breakfast"]])', "aictab model.sel AICc aicc akaike_weights"),
    ('table.compare_models("marks", using=["hours"], check_on_left_out_rows=True)',
     "cv.glm cross_validation cross_validate k_fold kfold cross_val_score"),
    ('table.check_model_of("marks", using=["hours", "breakfast"])',
     "bptest het_breuschpagan het_white breusch_pagan hosmer_lemeshow hoslem.test performance_hosmer brier"),
    ('table.find_model_averages_of("marks", for_each_group_in="class", using=["class"], comparing="each with the first")',
     "contrast trt.vs.ctrl joint_tests simple_effects dunnett helmert"),
    ('table.compare_averages_of(["marks", "hours"], for_each_group_in="class")', "manova MANOVA summary.manova"),
    # S3b-1: combining studies
    ('table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"], out_of=["vaccinated", '
     '"unvaccinated"])',
     "meta_analysis metaanalysis meta_analyse meta_analyze rma rma_uni metagen metabin metacont metacor metainc "
     "escalc pool_studies pooled_effect combine_effects heterogeneity random_effects_meta tau2 i2 i_squared "
     "publication_bias small_study small_study_effects egger regtest peters trimfill "
     "trim_and_fill"),
    ('table.combine_studies(..., interval_by="Hartung-Knapp")', "hksj knha hartung_knapp knapp_hartung"),
    ('table.combine_studies(..., test_method="mantel-haenszel")', "rma_mh mantel_haenszel_meta peto rma_peto"),
    # S3c-1: communities and resistomes
    ('table.add_diversity_columns(columns=["blaTEM", "sul1"])',
     "diversity shannon simpson invsimpson chao1 estimateR specnumber alpha_diversity hill hill_numbers renyi "
     "richness species_richness"),
    ('table.add_diversity_columns(columns=[...], at_total_count=1000)',
     "rarefy rrarefy rarefaction_depth subsample rarefied_richness"),
    ('table.add_log_ratio_columns(columns=["blaTEM", "sul1"])',
     "clr ilr alr cmultRepl multiplicative_replacement log_ratio centred_log_ratio centered_log_ratio "
     "compositional"),
    ('table.add_log_ratio_columns(columns=[...], zeros_replaced_by="adding 1")', "pseudocount pseudo_count"),
    ('table.add_principal_coordinates(columns=["blaTEM", "sul1"])',
     "pcoa cmdscale wcmdscale principal_coordinates mds ordination beta_diversity"),
    ('table.explain_profiles_of(["blaTEM", "sul1"], using=["temperature", "salinity"])',
     "rda cca dbrda capscale constrained_ordination redundancy_analysis envfit varpart"),
    ('table.explain_profiles_of(..., measure="hellinger")', "hellinger decostand"),
    ('table.find_correlation_between_profiles(first=["blaTEM", "sul1"], second=["temperature", "salinity"])',
     "mantel protest procrustes mantel_test"),
    ('table.compare_profiles_of(..., test_method="anosim")', "anosim betadisper"),
    ('table.compare_profiles_of(..., show="contributions")', "simper"),
    ('table.add_clusters(how_many="automatic")', "silhouette elbow optimal_clusters"),
    ('table.add_axes_that_separate_groups(columns=["temperature", "salinity"], for_each_group_in="site")',
     "lda discriminant linear_discriminant discriminant_analysis"),
    ('table.add_correspondence_axes(columns=["blaTEM", "sul1"])', "ca mca mjca correspondence_analysis decorana"),
    # S3c-2: hidden factors ("sem" is left out: scipy.stats.sem is the standard error of the mean)
    ('table.find_hidden_factors_behind(["q1", "q2", "q3", "q4", "q5", "q6"])',
     "fa efa factanal factor_analysis factor_analyse factor_analyze exploratory_factor_analysis fa_parallel "
     "parallel_analysis scree scree_plot oblimin varimax promax kmo latent_factors"),
    ('table.check_hidden_factors(measured_by={"visual": ["x1", "x2", "x3"], "speed": ["x7", "x8", "x9"]})',
     "cfa lavaan confirmatory_factor_analysis structural_equation_model structural_equation_modelling sem_model "
     "path_model measurement_model latent_variables fit_measures fitmeasures cfi rmsea srmr modindices "
     "modification_indices"),
    # S3c-3: directions, places and extremes
    ('table.find_average_direction_of("current_direction", full_turn=360)',
     "circmean mean_direction circular_mean mean_circular average_angle find_mean_direction_of circular_average"),
    ('table.compare_shape_to("current_direction", shape="even around the circle", full_turn=360)',
     "rayleigh rayleigh_test circular_uniformity"),
    ('table.find_autocorrelation_of("zinc", x="east", y="north")',
     "moran morans_i moran_i moran_test spatial_autocorrelation"),
    ('table.find_variogram_of("zinc", x="east", y="north")', "variogram semivariogram fit_variogram"),
    ('table.find_return_levels_of("sea_level", once_in=[10, 100])',
     "fevd return_level return_levels return_period gev_fit extremes block_maxima"),
    ('table.find_return_levels_of("rain", once_in=[10, 100], values_above=30, sorted_by="date")',
     "pot peaks_over_threshold gpd_fit"),
    ('table.find_variogram_of("zinc", x="east", y="north")   (kriging is not offered)', "kriging krige"),
    # S3c-4: small additions to known words
    ('table.find_percentile_of("price", 90, weights="count"), or find_median_of("price", weights="count")',
     "weighted_quantile wtd_quantile weighted_percentile weighted_median svyquantile"),
    ('table.find_correlation_between("hours", "marks", "height", show="covariance"), on one subject (one row per child)',
     "cov covariance covariance_matrix"),
    ('table.forecast("visitors", sorted_by="month", test_method="arima", order="automatic", repeats_every="year")',
     "auto_arima autoarima"),
    ('table.add_adjusted_p_value_column(test_method="storey"), or test_method="local fdr"',
     "qvalue q_values qvalues storey lfdr local_fdr"),
    ('table.compare_each_pair_of("time", for_each_group_in="method", matched_by="player", test_method="nemenyi"), or '
     'test_method="conover"', "nemenyi posthoc_nemenyi_friedman frdAllPairsNemenyiTest posthoc_conover_friedman "
                       "frdAllPairsConoverTest"),
    ('table.compare_each_pair_of("infected", for_each_group_in="age_group", based_on="percents", value="yes")',
     "pairwise_prop_test pairwise_fisher_test"),
    # S3d-1: planning an experiment and survey answers
    ('sdata.make_random_assignments(how_many=60, groups=["A", "B"], in_blocks_of=[4, 6], with_seed=1)',
     "blockrand randomization randomisation randomization_list randomisation_list allocation allocation_list "
     "block_randomization block_randomisation permuted_blocks"),
    ('sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, with_seed=1)',
     "expand.grid expand_grid factorial full_factorial design.ab design.crd design.rcbd design.lsd design.split "
     "gen.factorial latin_square split_plot experimental_design design_of_experiments doe"),
    ('table.use_survey_design(weights="weight", strata="school_type", population_sizes="schools_of_type"), then '
     'table.find_average_of("score_2000")',
     "svydesign survey_design survey_weights svymean svytotal svyglm svyciprop svyby svyttest "
     "svychisq complex_survey design_effect"),
    ('table.keep_random_rows(5, for_each_group_in="school_type", with_seed=1)',
     "stratified_sample stratified_sampling sample_frac strata_sample"),
    ('table.count_empty_cells_in(show="patterns")', "md.pattern md_pattern missing_pattern missingness_pattern "
                                                     "missing_data_pattern"),
    ('table.count_each(columns=["teaching", "pace"], in_order=["strongly disagree", "disagree", "neutral", "agree", '
     '"strongly agree"])', "likert likert_scale likert_summary top_two_box"),
    # S3d-2: epidemiology and cause and effect
    ('table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ"])',
     "propensity propensity_score propensity_scores matchit match_it weightit ipw iptw inverse_probability_weighting "
     "ate att cobalt bal_tab balance_table psm"),
    ('table.explain("depress2", using="treat", through="job_seek")',
     "mediation mediate mediation_analysis acme indirect_effect"),
    ('table.compare_risks("infected", for_each_group_in="ward", against="ward A", show="attributable fractions")',
     "attributable_fraction attributable_fractions paf population_attributable_fraction preventable_fraction"),
    ('table.rate_of("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band", '
     'standard_population="whole table")',
     "ageadjust ageadjust_direct age_adjust age_standardise age_standardize direct_standardisation "
     "direct_standardization epi_directadj standardised_rate standardized_rate"),
    ('table.compare_rates("deaths", time="person_years", allowing_for="age_band", standard_rates=national)',
     "smr standardised_mortality_ratio standardized_mortality_ratio sir ageadjust_indirect epi_indirectadj "
     "indirect_standardisation indirect_standardization"),
    ('table.compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="period", '
     "same_within=[0.8, 1.25])", "bioequivalence crossover be_2x2 abe average_bioequivalence"),
    ('table.find_correlation_between("bmi", "chl", empty_cells="multiple imputation")', "micombine_cor"),
    # S3d-3: Bayesian answers (R BayesFactor and rstanarm; brms and PyMC users land on the same option)
    ('table.compare_averages_of("crp", for_each_group_in="ward", test_method="bayesian") (also on compare_before_and_after, '
     'compare_average_to, find_correlation_between and compare_counts_of)',
     "ttestBF ttest_bf bayes_factor bayesfactor bayesian_t_test bf10 jzs correlationBF contingencyTableBF "
     "bayesian_correlation bayes_factor_ttest bayesfactor_ttest credible_interval"),
    ('table.explain("marks", using=["hours", "breakfast"], test_method="bayesian")',
     "stan_glm stan_glmer stan_lmer rstanarm brm brms pymc bambi bayesian_regression bayesian_model "
     "posterior_interval prior_summary bayesian_mixed_model"),
    ('table.check_model_of("marks", using=["hours"], test_method="bayesian") (show="prior check" for the prior)',
     "pp_check ppc posterior_predictive_check prior_predictive_check ppc_dens_overlay rhat r_hat ess "
     "effective_sample_size"),
    # Numbers phase, batch 3 (approved by Manish 2026-11-25): nearest rows, distances to another table, the fence
    # Tables finishing PR (API audit of pandas 3.1.1 and Polars 2.1.0, 2026-11-25): names with a word but no pointer
    ('table.add_column("label", by_running=make_label) runs your own Python function on each row; a function for '
     'each group is left to pandas: table.as_pandas()', "apply map_rows map_elements map_columns map_batches"),
    ('table.fill_empty_cells_in("price", with_the="value above")', "ffill forward_fill pad"),
    ('table.fill_empty_cells_in("price", with_the="value below")', "bfill backward_fill backfill"),
    ('table.fill_empty_cells_in("sales", with_the="line between neighbours", sorted_by="date")', "interpolate_by"),
    ('table.keep_biggest_rows(1, by="marks") for the row with the biggest value (add for_each_group_in="class" '
     "for each group)", "idxmax arg_max max_by"),
    ('table.keep_smallest_rows(1, by="marks") for the row with the smallest value (add for_each_group_in="class" '
     "for each group)", "idxmin arg_min min_by"),
    ('table.keep_biggest_rows(3, by="marks")', "top_k top_k_by"),
    ('table.keep_smallest_rows(3, by="marks")', "bottom_k bottom_k_by"),
    ('table.add_column("bmi", "weight / height ** 2"), then table.move_columns("bmi", after="name")',
     "insert insert_column"),
    ('table.find_summary_of("marks", show=["variance", "standard error", "skewness", "kurtosis"])',
     "var sem skew kurt kurtosis"),
    ('table.replace_values_in("class", {"A": "Class A", "B": "Class B"})', "map replace_strict"),
    ('table.count_empty_cells_in() to count the empty cells, or table.add_is_empty_column("no_price", '
     'from_column="price") for a True or False column (True where the cell is empty)',
     "has_nulls hasnans null_count"),
    ('table.keep_rows_where("price", is_empty=False) to keep the rows with a value, or '
     'table.remove_rows_with_empty_cells_in("price")', "notna notnull is_not_null"),
    ('table.add_missing_combinations_of("year", "country"), or table.add_missing_dates("date") for a run of dates',
     "reindex"),
    ('table.save("results.json"): the end of the file name chooses the type, also .jsonl, .feather, .dta and .html',
     "to_json to_feather to_stata to_html write_json write_ndjson write_ipc"),
    ('table.round_dates_in("date", down_to="month") for dates (Polars dt.truncate), or table.keep_rows_where('
     '"date", is_before="2026-01-01") for the rows up to a point (pandas truncate)', "truncate"),
    ('table.fill_empty_cells_from(other_table, using="id"), which fills only the empty cells (pandas and Polars '
     "update also overwrite filled ones)", "update"),
    ('table.get_column("marks")', "values to_list tolist to_series"),
    ('table.keep_rows_where("marks", is_between=[50, 70])', "between is_between"),
    ('table.add_group_column("result", rules={"marks >= 80": "top", "marks >= 50": "pass"}, otherwise="fail")',
     "case_when when"),
    ('table.find_average_of("sales", for_each_group_in="date", every="month") (every= works in every find_..._of '
     "word)", "group_by_dynamic"),
    ('table.add_smoothed_column("smooth", from_column="signal", test_method="exponential", sorted_by="time")',
     "ewm_mean ewm_mean_by"),
    ('table.add_rolling_column("smooth", from_column="temperature", show="average")',
     "rolling_mean rolling_mean_by"),
    ('table.add_rolling_column("week_total", from_column="sales", window=7, show="total")',
     "rolling_sum rolling_sum_by"),
    ('table.add_rolling_column("median", from_column="temperature", show="median")',
     "rolling_median rolling_median_by"),
    ('table.add_rolling_column("lowest", from_column="temperature", show="smallest")',
     "rolling_min rolling_min_by"),
    ('table.add_rolling_column("highest", from_column="temperature", show="biggest")',
     "rolling_max rolling_max_by"),
    ('table.add_rolling_column("spread", from_column="temperature", show="standard deviation")',
     "rolling_std rolling_std_by"),
    ('table.add_rolling_column("variance", from_column="temperature", show="variance")',
     "rolling_var rolling_var_by"),
    ('table.add_rolling_column("high", from_column="temperature", show="percentile", percent=90)',
     "rolling_quantile rolling_quantile_by"),
    ('table.add_column("name_and_class", by_joining_text=["name", "class"], separator=" ")',
     "concat_str format paste paste0 str_c unite"),
    ('table.add_column("when", by_joining_text=["year", "month", "day"], separator="-"), then '
     'table.turn_into_dates("when")', "date make_date"),
    ('table.find_nearest_rows_to({"east": 4000, "north": 1000}, how_many=3)',
     "KDTree cKDTree query_ball_point NearestNeighbors knnsearch rangesearch nn2 get.knnx nearest_neighbours"),
    ('table.find_distances_to_rows_of(other, using=["east", "north"])', "cdist pdist2"),
    ('table.find_fence_around(x="east", y="north")', "ConvexHull convex_hull chull convhull"),

    # ---------------------------------------------------------------- families for 100 %, batches 1-2 (approved by
    # Manish 2026-11-28): the pandas and Polars names of plan section 2.1, their words, and the hand-over for the rest
    ('table.check_if_all_values_in("marks", is_above=0), or a list of columns: '
     'table.check_if_all_values_in(["hours", "marks"], is_above=0)', "all all_horizontal"),
    ('table.check_if_any_value_in("marks", is_above=90), or a list of columns: '
     'table.check_if_any_value_in(["hours", "marks"], is_above=90)', "any any_horizontal"),
    ('table.check_if_sorted_by("marks"), or table.check_if_sorted_by("marks", biggest_first=True)',
     "is_monotonic_increasing is_monotonic_decreasing is_sorted is_monotonic"),
    ('table.add_run_number_column("run", from_column="class")', "rle_id consecutive_id"),
    ('table.add_run_number_column("run", from_column="class"), then table.count_rows(for_each_group_in="run") for '
     "the length of each run", "rle"),
    ('table.find_summary_of("marks", show=["product"])', "prod product"),
    ('table.find_summary_of("marks", show=["entropy"])', "entropy"),
    ('table.find_summary_of("marks", show=["first", "last"], for_each_group_in="class") for the first and last value '
     "of each group, or table.keep_first_rows(1) and table.keep_last_rows(1) for whole rows", "first last"),
    ('table.find_summary_of("name", show=["joined text"], separator="; ", for_each_group_in="class")', "implode"),
    ('table.save("table_1.md"), a Markdown table', "to_markdown"),
    ('table.save("table_1.tex"), a LaTeX table (also .docx for Word)', "to_latex"),
    ('table.save("clipboard"), to paste into Excel', "to_clipboard write_clipboard"),
    ('table.keep_rows_where("time", time_of_day_between=["08:00", "17:00"]), or ["08:00", "08:00"] for one clock '
     "time", "between_time at_time"),
    ('table.round_numbers_in("marks", significant_figures=2)', "round_sig_figs signif"),
    ('table.add_column("level", "log10(marks)"): log10, log1p, sign, cbrt, floor and ceil work in a formula',
     "log10 log1p sign cbrt ceil ceiling"),
    ('table.add_column("tens", "floor(marks / 10)")', "floor"),
    ('table.add_rolling_column("link", from_column="hours", with_column="marks", show="correlation", window=3)',
     "rolling_corr"),
    ('table.add_rolling_column("joint", from_column="hours", with_column="marks", show="covariance", window=3)',
     "rolling_cov"),
    ('table.find_correlation_between("hours", "marks"), or table.add_rolling_column("link", from_column="hours", '
     'with_column="marks", show="correlation") for a moving one', "corrwith"),
    ('table.join_with(other_table, where="marks >= marks_other")', "join_where"),
    ('table.join_with(other_table, using="name", keep="all rows from both"): every row of both tables, sorted by '
     "using=", "merge_ordered"),
    ('table.add_rows_from(other_table), then table.sort_by("marks")', "merge_sorted"),
    ('table.join_with(other_table, using="date", match="nearest before")', "asof"),
    ('table.add_column("best", "marks + hours"): a formula works on two columns, cell by cell', "combine"),
    ('table.turn_into_categories("class")', "cat"),
    ('table.add_rank_column("group_number", from_column="class", biggest_first=False, when_tied="no gaps"): a number '
     "for each group, in sorted order (pandas factorize numbers them in the order they first turn up, from 0)",
     "factorize"),
    ('table.find_average_of("marks", for_each_group_in="date", every="month"): every= groups dates by "week", '
     '"month", "quarter" or "year"', "to_period period_range"),
    ('table.describe_columns() shows the kind of each column; turn_into_numbers, turn_into_text, turn_into_dates '
     "and turn_into_categories change them (memory and types are left to pandas: " + "table.as_pandas())",
     "convert_dtypes infer_objects"),
    ("table.count_rows() and table.count_columns(); the memory a table takes is left to pandas and Polars: "
     "table.as_pandas() or table.as_polars()", "memory_usage estimated_size shrink_to_fit shrink_dtype"),
    ("table.save(\"table_1.html\") for a web page table; colours and formats of the cells are left to pandas: "
     "table.as_pandas(), then df.style", "style"),
    ("table.get_column(\"marks\") gives numbers (sdata.number_list); a whole table goes to NumPy by table.as_pandas(), "
     "then df.to_numpy()", "to_numpy to_xarray to_jax to_torch"),
    ("table.as_pandas(), then df.dot(other) in pandas, and give the result to sdata.table to come back", "dot"),
    # G12 (approved): simplydata tables have no row index, keep one value in each cell, run no lazy plans and chain
    # words without pipe; these jobs are left to pandas and Polars
    ("table.as_pandas(), then pandas: simplydata tables have no row index (rows are counted from 1: "
     "table.get_row(3), table.keep_rows_by_position(...)); give the result to sdata.table to come back",
     "set_index reset_index sort_index reindex_like rename_axis reorder_levels swaplevel droplevel xs index "
     "first_valid_index last_valid_index align"),
    ('table.split_into_rows("genes", separator=";"): simplydata keeps one value in each cell; list columns are left '
     "to Polars: table.as_polars()", "list arr explode_list"),
    ("table.as_polars(), then Polars: every word already runs at once (fast=True runs Polars underneath), so "
     "simplydata has no lazy plans", "lazy collect"),
    ("table.as_pandas(), then df.pipe(my_function): simplydata words chain one after the other already",
     "pipe pipe_with_dtype"),
]

# chart.<name>
_CHART = [
    ("chart.get_numbers_drawn()", "get_xydata get_offsets layer_data ggplot_build plot_data"),
    # charts phase, batch 1 (approved by Manish 2026-11-25)
    ("chart.get_text_drawn()", "get_title get_xlabel get_ylabel get_legend get_texts get_xticklabels get_labs"),
    ("chart.get_scales_drawn()", "get_xlim get_ylim get_xscale get_yscale get_xticks get_yticks get_clim layer_scales"),
    ('chart.get_size(unit="cm")', "get_size_inches get_figwidth get_figheight"),
    ('chart.write_letter("B")', "tag_levels plot_annotation panel_letter"),
    ('chart.put_legend_inside("top left")', "move_legend legend_loc"),
    ('chart.use_shapes("circle", "square", "triangle")', "scale_shape_manual symbol_sequence markers"),
    ('chart.draw_answer_bars(columns=["teaching", "pace"], in_order=["strongly disagree", "disagree", "neutral", '
     '"agree", "strongly agree"])', "draw_likert_bars plot_likert likert_plot diverging_bars diverging_stacked_bars"),
    ('chart.draw_lines(x="year", y="population")', "plot geom_line line"),
    ('chart.draw_trade_off_curve(score="crp", truth="infected")', "roc_curve roc plot_roc ggroc roc_plot"),
    ('chart.draw_difference_dots(first="device_a", second="device_b")', "bland_altman mean_diff_plot bland_altman_plot"),
    ('chart.draw_forest_plot(x="estimate", y="measure")', "forestplot interval_dots coefplot"),
    ('chart.draw_dots(x="hours", y="marks")', "geom_point scatterplot scatter"),
    ('chart.draw_bars(x="class", y="marks")', "barplot geom_bar geom_col bar"),
    ('chart.draw_bars(x="class", y="marks", sideways=True)', "barh"),
    ('chart.draw_histogram(x="marks")', "hist geom_histogram histplot"),
    ('chart.draw_boxes(x="class", y="marks")', "boxplot geom_boxplot box"),
    ('chart.draw_violins(x="class", y="marks")', "violinplot geom_violin violin"),
    ('chart.draw_density(x="marks")', "kdeplot geom_density kde"),
    ('chart.draw_cumulative_share(x="marks")', "ecdfplot ecdf stat_ecdf"),
    ("chart.fit_line()", "regplot lmplot geom_smooth"),
    ("chart.fit_curve(of_degree=2)", "polyfit"),
    ('chart.fit_formula("marks = a * hours ** b")', "curve_fit nls"),
    ('chart.fit_distribution("normal")', "fitdistr fitdist"),
    ('chart.draw_curve("y = 100 * exp(-0.3 * x)", between=[0, 10])', "stat_function geom_function fplot"),
    ("chart.draw_smooth_line()", "lowess"),
    ('chart.draw_smooth_line(test_method="loess")', "loess loess.smooth"),
    ('chart.draw_qq_dots("marks")', "probplot qqplot qqnorm"),
    ("chart.draw_line_with_slope(1, through=(0, 0))", "abline axline"),
    ("chart.draw_line_at_y(50)", "axhline geom_hline hline"),
    ("chart.draw_line_at_x(2010)", "axvline geom_vline vline"),
    ("chart.shade_between_y(40, 60)", "axhspan"),
    ("chart.shade_between_x(6, 8)", "axvspan"),
    ('chart.draw_band(x="month", between=["lowest", "highest"])', "fill_between geom_ribbon"),
    ('chart.draw_error_bars("standard error")', "errorbar geom_errorbar"),
    ('chart.write_note("Cherria grows fastest", x=2020, y=12)', "text annotate"),
    ('chart.write_title_on_top("Marks in each class")', "title suptitle set_title ggtitle"),
    ('chart.label_x("Hours of study")', "xlabel set_xlabel"),
    ('chart.label_y("Marks")', "ylabel set_ylabel"),
    ("chart.set_range_x(0, 10)", "xlim set_xlim"),
    ("chart.set_range_y(0, 100)", "ylim set_ylim"),
    ("chart.use_log_scale_x()", "semilogx xscale"),
    ("chart.use_log_scale_y()", "semilogy yscale"),
    ("chart.put_ticks_x(1, 4, 7, 10)", "xticks set_xticks"),
    ("chart.put_ticks_y(0, 25, 50, 75)", "yticks set_yticks"),
    ("chart.put_legend_on_right()", "legend"),
    ("chart.show_grid()", "grid"),
    ('chart.save("chart.png")', "savefig ggsave"),
    ('chart.draw_heatmap(x="month", y="city", value="rain")', "imshow pcolormesh geom_tile"),
    ('chart.draw_contour(x="east", y="north", z="height")', "contourf"),
    ('chart.draw_surface(x="east", y="north", z="height")', "plot_surface"),
    ('chart.add_second_y("rain")', "twinx"),
    ('chart.draw_one_chart_for_each_group_in("class")', "facet_wrap facet_grid FacetGrid"),
    # charts finishing PR: plt.subplots(2, 2) also makes a page of different charts
    ('chart.draw_one_chart_for_each_group_in("class") for one chart per group, or '
     "sdata.put_in_rows_and_columns([chart_a, chart_b, chart_c], per_row=2) for different charts on one page",
     "subplots"),
    ("chart.draw_side_histograms()", "jointplot"),
    ('chart.draw_all_dots(x="class", y="marks")', "stripplot swarmplot geom_jitter"),
    ('chart.draw_count_bars(x="fruit")', "countplot"),
    ('chart.use_colour_scale("magma")', "cmap colormap scale_fill_viridis_c"),
    ('chart.set_size(width=17, height=8, unit="cm")', "figsize set_size_inches"),
    ('chart.draw_sticks(x="rows back", y="correlation")', "stem stems stemplot lollipop"),
    ('chart.draw_autocorrelation_bars("visitors", sorted_by="month")', "plot_acf plot_pacf acorr"),
    ('chart.draw_cross_correlation_bars("signal", "vibration", sorted_by="time")', "plot_ccf xcorr"),
    ('chart.draw_lag_dots("visitors", sorted_by="month", rows_back=1)', "lag_plot lagplot"),
    ('chart.draw_trend_and_season(x="month", y="visitors", repeats_every="year")', "plot_stl plot_decompose"),
    ("chart.draw_forecast(steps_ahead=12)", "plot_predict plot_forecast autoplot"),
    ('chart.draw_spectrum("signal", sorted_by="time")', "psd magnitude_spectrum plot_spectrum periodogram"),
    ('chart.draw_spectrum_over_time("signal", sorted_by="time")', "spectrogram specgram stft"),
    ("chart.draw_peak_dots(is_at_least=1)", "mark_peaks plot_peaks"),
    # S3a-3
    ('chart.draw_interaction_lines(x="class", y="marks", colour="breakfast")', "interaction.plot interaction_plot pointplot"),
    # S3b-3
    ('chart.draw_risk_curves(time="time", event="event", value="first_esbl", competing_with="discharged")',
     "ggcuminc cumulative_incidence_plot plot_cuminc"),
    # S3b-1
    ('chart.draw_funnel_plot(x="estimate", y="standard error")', "funnel funnel_plot draw_funnel"),
    # S3c-1
    ('chart.draw_richness_curves(columns=["blaTEM", "sul1"])',
     "rarecurve rarefaction rarefaction_curves draw_rarefaction_curves iNEXT accumulation species_accumulation "
     "draw_species_curves"),
    ('chart.draw_cluster_tree(columns=["blaTEM", "sul1"])', "dendrogram plot_dendrogram draw_dendrogram draw_tree"),
    # S3c-3
    ('chart.draw_variogram("zinc", x="east", y="north")', "plot_variogram variogram_plot"),
    ('chart.draw_threshold_check(x="rain", between=[20, 40])',
     "mrlplot mrl_plot mean_residual_life threshrange threshrange_plot mean_excess_plot"),
    ('chart.draw_polar(angle="current_direction", distance="depth", full_turn=360)', "rose rose_diagram"),
]

# chart.<name>, charts phase batch 2 (approved by Manish 2026-11-25)
_CHART_2 = [
    ('chart.draw_wind_rose(direction="wind_direction", speed="wind_speed")', "windrose wind_rose bar_polar barpolar"),
    ('chart.draw_rug_lines(x="marks")', "rugplot geom_rug rug"),
    ("chart.draw_arrow(start=[2, 40], end=[4, 60])", "arrow FancyArrow geom_segment"),
    ('chart.put_chart_inside(detail, where="top right")', "inset_axes add_axes inset_element annotation_custom"),
    ('chart.add_second_x(formula="x * 9 / 5 + 32")', "twiny secondary_xaxis sec_axis dup_axis"),
    ('chart.add_second_y(formula="y * 9 / 5 + 32")', "secondary_yaxis"),
    ("chart.hide_frame()", "set_axis_off axis_off theme_void"),
    ("chart.show_small_ticks_x()", "minorticks_on minor_ticks AutoMinorLocator"),
    ("chart.use_true_shape()", "set_aspect coord_equal coord_fixed"),
    ("chart.make_square()", "set_box_aspect"),
    ("chart.say_what_it_shows()", "describe alt_text get_alt_text"),
    ('chart.draw_lines_3d(x="east", y="north", z="height")', "plot3D plot3d line_3d"),
    ('chart.label_z("Height (m)")', "zlabel set_zlabel zlab"),
    ("chart.set_range_z(-10, 20)", "zlim set_zlim"),
    ("chart.put_ticks_z(-10, 0, 10, 20)", "zticks set_zticks"),
    ("chart.look_from(height=20, around=45)", "view_init camera persp"),
    ('chart.draw_histogram(x="hours", y="marks")', "hist2d histogram2d geom_bin_2d"),
    ('chart.draw_density(x="hours", y="marks")', "kde2d geom_density_2d"),
    ('chart.draw_pie(labels="fruit", values="count", hole=0.4)', "donut doughnut"),
    ("chart.draw_line_at_y(50, between=[2, 6])", "hlines"),
    ("chart.draw_line_at_x(4, between=[20, 60])", "vlines"),
]

# chart.<name>, charts phase batch 3 (approved by Manish 2026-11-25): web pages and the priority-3 words
_CHART_3 = [
    ('chart.save("marks.html")', "write_html to_html write_json saveWidget"),
    ("chart.show_in_web_page()", "iplot ggplotly mpld3 show_in_browser show_interactive"),
    ('chart.show_when_pointing("name", "marks")',
     "hovertemplate hover_data hover_name hover tooltip tooltips mplcursors on_hover show_on_hover"),
    ("chart.add_range_bar_x()", "rangeslider range_slider add_range_slider_x dyRangeSelector"),
    ("chart.break_between_y(50, 500)", "brokenaxes broken_axis scale_y_break gap_plot break_y"),
    ('chart.use_scale_y("square root")', "set_yscale scale_y_sqrt scale_y_continuous"),
    ('chart.use_scale_x("square root")', "set_xscale scale_x_sqrt scale_x_continuous"),
    ("chart.use_log_scale_y(through_zero=True)", "symlog pseudo_log_trans"),
    ('chart.use_background_colour("ivory")', "set_facecolor plot_bgcolor panel_background"),
    ('chart.draw_hexagon_bins(x="hours", y="height")', "hexbin geom_hex density_heatmap"),
    ('chart.draw_time_bars(start=[1, 3, 6], end=[4, 7, 9], y=["plan", "build", "test"])',
     "broken_barh timeline gantt gantt_chart"),
    ("chart.draw_rectangle(x_between=[4, 6], y_between=[60, 80])", "Rectangle add_patch geom_rect rect"),
    ("chart.draw_circle(centre=[5, 70], radius=1)", "Circle add_circle"),
    ('chart.draw_residual_dots(x="hours", y="marks")', "residplot resid_plot residuals_plot"),
    ('chart.draw_event_lines(x="hours", y="class")', "eventplot event_plot raster_plot"),
    ('chart.draw_bars_3d(x="month", y="city", z="rain")', "bar3d bar_3d"),
]

# chart.<name>, charts finishing PR (API audit of matplotlib 3.11.2 and seaborn 0.13.2, 2026-11-27): names with a
# chart word but no pointer. matplotlib's and seaborn's names typed with plt., ax., fig. or sns. in front look here
# first (NAMESPACES below), so plt.title is the title and not pandas' str.title.
_CHART_4 = [
    ("chart.as_matplotlib(), which gives the chart's matplotlib Figure: fig = chart.as_matplotlib(), then "
     "ax = fig.axes[0] is its Axes, and any matplotlib code works on them",
     "gcf gca get_figure get_axes Figure Axes fig ax axes figure plt pyplot matplotlib mpl"),
    ("chart.as_matplotlib() gives the matplotlib Figure (fig = chart.as_matplotlib()); then fig.axes[0].table(...) "
     "in matplotlib draws the table: simplydata draws no table inside a chart", "table add_table"),
    # not covered: the hand-over, as the manual's chapter "From matplotlib and seaborn to simplydata" shows
    ("chart.as_matplotlib() gives the matplotlib Figure (fig = chart.as_matplotlib()); then the matplotlib or seaborn "
     "code works on fig.axes[0]: simplydata has no word for this job (the manual's chapter \"From matplotlib and "
     'seaborn to simplydata\" shows how)', "quiver quiverkey barbs streamplot fill Polygon fill_betweenx margins "
                                             "boxenplot bxp supxlabel supylabel voxels triplot"),
    ('chart.draw_lines(x="month", y="temperature", colour="city")', "lineplot"),
    ('chart.draw_dots(x="hours", y="marks"), then chart.draw_one_chart_for_each_group_in("class") for one chart per '
     "group (draw_lines for lines)", "relplot"),
    ('chart.draw_histogram(x="marks"), then chart.draw_one_chart_for_each_group_in("class") for one chart per group '
     "(draw_density or draw_cumulative_share for the other kinds)", "displot distplot"),
    ('chart.draw_bars(x="class", y="marks") (or draw_boxes, draw_violins, draw_all_dots, draw_count_bars), then '
     'chart.draw_one_chart_for_each_group_in("subject") for one chart per group', "catplot"),
    ('sdata.draw_all_pairs(sdata.get_example("marks"), colour="class")', "pairplot PairGrid"),
    ('chart.draw_dots(x="hours", y="marks"), then chart.draw_side_histograms()', "JointGrid"),
    ('chart.draw_heatmap(x="month", y="city", value="rain", cluster=True)', "clustermap"),
    ('chart.draw_bars(x="subject", y="marks", colour="class")', "grouped_bar"),
    ('chart.draw_area(x="month", y="rain", colour="city", stacked=True)', "stackplot"),
    ('chart.draw_lines(x="month_number", y="temperature", joined_by="steps")', "step stairs"),
    ('chart.draw_heatmap(x="month", y="city", value="rain")', "matshow pcolor pcolorfast"),
    ('chart.draw_contour(x="east", y="north", z="height"), which joins scattered points up as tricontour does',
     "tricontour tricontourf tripcolor"),
    ('chart.draw_surface(x="east", y="north", z="height")', "plot_trisurf"),
    ('chart.draw_surface(x="east", y="north", z="height", as_wires=True)', "plot_wireframe"),
    ('chart.draw_dots_3d(x="east", y="north", z="height")', "scatter3D"),
    ("chart.look_from(height=90)", "set_top_view"),
    ('chart.write_note("tallest", x=8, y=95)', "text2D text3D Annotation Text"),
    ("chart.draw_arrow(start=[2, 40], end=[4, 60])", "Arrow FancyArrowPatch"),
    ("chart.draw_line_with_slope(1, through=(0, 0))", "AxLine"),
    ('chart.draw_pie(labels="fruit", values="count")', "pie_label"),
    ('chart.draw_bars(x="class", y="marks"), then chart.write_numbers_on_bars()', "bar_label"),
    ("chart.use_log_scale_x(), then chart.use_log_scale_y()", "loglog"),
    ("chart.flip_x()", "invert_xaxis set_xinverted"),
    ("chart.flip_y()", "invert_yaxis set_yinverted"),
    ("chart.set_range_x(0, 10)", "set_xbound set_xlim3d"),
    ("chart.set_range_y(0, 100)", "set_ybound set_ylim3d"),
    ("chart.set_range_z(-10, 20)", "set_zbound set_zlim3d"),
    ('chart.put_ticks_x(1, 4, 7, 10, labels=["one", "four", "seven", "ten"])',
     "set_xticklabels FixedLocator FixedFormatter"),
    ('chart.put_ticks_y(0, 50, 100, labels=["none", "half", "all"])', "set_yticklabels"),
    ('chart.put_ticks_z(-10, 0, 10, 20, labels=["deep", "sea level", "hill", "top"])', "set_zticklabels"),
    ("chart.put_ticks_x(how_many=5)", "locator_params MaxNLocator LinearLocator"),
    ("chart.put_ticks_x(every=5)", "MultipleLocator"),
    ("chart.hide_ticks_x()", "NullLocator NullFormatter"),
    ('chart.write_ticks_y_as("thousands"), or "percent", "scientific" or "plain"',
     "ticklabel_format FormatStrFormatter StrMethodFormatter PercentFormatter"),
    ("chart.rotate_labels_x(45)", "autofmt_xdate"),
    ("chart.rotate_labels_x(45) to turn the tick labels, chart.hide_ticks_x() to hide the ticks, or "
     "chart.use_font_size(ticks=10) for their size", "tick_params"),
    ('chart.hide_frame() for axis("off"), chart.use_true_shape() for axis("equal"), or chart.set_range_x(0, 10) '
     "and chart.set_range_y(0, 100) for the ranges", "axis"),
    ("chart.hide_frame() takes the whole frame away (the paper look already leaves out the top and right lines)",
     "despine set_frame_on"),
    ('chart.label_colour_bar("Rain (mm)"): a colour scale gets its colour bar by itself, and chart.hide_colour_bar() '
     "takes it away", "colorbar"),
    ('chart.use_colour_scale("magma", between=[0, 30])', "clim Normalize"),
    ('chart.use_colour_scale("magma")', "get_cmap set_cmap colormaps Colormap viridis magma inferno plasma jet"),
    ('chart.use_colours("Set2")', "color_palette set_palette set_prop_cycle cycler mpl_palette husl_palette "
                                   "hls_palette"),
    ('chart.use_colour_scale("white", "navy")', "light_palette dark_palette blend_palette cubehelix_palette"),
    ('chart.use_colour_scale("blue to red", middle=0)', "diverging_palette TwoSlopeNorm CenteredNorm"),
    ('chart.use_style("school"), or "paper", "presentation", "dark" or "black and white"',
     "set_theme set_style axes_style use"),
    # sns.set is the old name of set_theme; matplotlib's ax.set(xlabel=..., title=...) sets several things at once
    ('chart.use_style("school") for seaborn\'s set (the old name of set_theme); matplotlib\'s ax.set(xlabel=..., '
     "title=...) is label_x, label_y, write_title_on_top and the other words, one for each", "set"),
    # the spacing between parts needs nothing: simplydata always draws with matplotlib's constrained layout
    ('chart.set_size(width=17, height=12, unit="cm") gives more room; the spacing itself needs nothing, as '
     "simplydata always uses matplotlib's constrained layout, so labels do not overlap (spacing of your own: "
     "chart.as_matplotlib())", "tight_layout subplots_adjust set_tight_layout set_constrained_layout "
                               "set_layout_engine"),
    ("chart.use_style(\"presentation\") for bigger text and lines (seaborn's \"talk\"), or chart.use_font_size(14)",
     "set_context plotting_context"),
    ('chart.use_style("school"), chart.use_font("DejaVu Serif") or chart.use_font_size(14) set the look; any other '
     "matplotlib setting is left to matplotlib: chart.as_matplotlib()", "rc rc_context rcParams rcdefaults"),
    ('chart.write_caption_at_bottom("Data from 2026")', "figtext"),
    ('chart.set_size(width=17, height=8, unit="cm")', "set_figwidth set_figheight figaspect"),
    ('chart.save("chart.png", resolution=300)', "set_dpi get_dpi"),
    ("chart.add_zoom_box(x_between=[2, 4], y_between=[40, 60])", "indicate_inset indicate_inset_zoom"),
    ('chart.draw_one_chart_for_each_group_in("class", same_y=True)', "sharex sharey"),
    ("sdata.put_in_rows_and_columns([chart_a, chart_b, chart_c], per_row=2)",
     "subplot subplot2grid subplot_mosaic subfigures add_subfigure add_subplot add_gridspec GridSpec SubplotSpec"),
    ("sdata.put_side_by_side([chart_a, chart_b], with_one_legend=True)", "figlegend"),
    ("chart.get_text_drawn()", "get_yticklabels get_xmajorticklabels get_ymajorticklabels get_xminorticklabels "
                               "get_yminorticklabels get_suptitle get_supxlabel get_supylabel "
                               "get_legend_handles_labels get_zlabel get_zticklabels get_zmajorticklabels "
                               "get_zminorticklabels"),
    ("chart.get_numbers_drawn()", "get_lines get_images"),
    ("chart.get_scales_drawn()", "get_xbound get_ybound get_xinverted get_yinverted xaxis_inverted yaxis_inverted "
                                 "get_zlim get_zscale get_zticks get_zbound get_zinverted zaxis_inverted get_xlim3d "
                                 "get_ylim3d get_zlim3d"),
]

# nums.<name> (numbers). Older ones (mean, sum, min ...) are in numbers/_base.py HINTS.
_NUMBERS = [
    ('numbers.fit_distribution("gamma")', "fit fitdistr fitdist"),
    ("numbers.find_spectrum(time_step=0.01)", "fft_power spectral_density"),
    ("numbers.find_autocorrelation(rows_back=10)", "acf pacf"),
    ('numbers.smooth(test_method="median", window=5)',
     "runmed medfilt median_filter savgol_filter sgolayfilt ewm ewma gaussian_filter1d whittaker_henderson wiener "
     "moving_average convolve1d"),
    ("numbers.remove_trend()", "detrend"),
    ("numbers.keep_each_frequency_that(is_below=5, time_step=0.01)",
     "butter cheby1 cheby2 ellip bessel lowpass low_pass highpass high_pass bandpass band_pass filtfilt sosfiltfilt "
     "sosfilt lfilter iirpeak"),
    ("numbers.remove_each_frequency_that(is_equal_to=50, time_step=0.005)",
     "notch iirnotch iircomb bandstop band_stop"),
    ("numbers.find_each_peak_that(is_at_least=1)", "findpeaks argrelmax peak_prominences peak_widths"),
    ("numbers.find_each_dip_that(is_at_most=-1)", "argrelmin find_valleys find_troughs"),
    ("numbers.take_fourier_transform()", "fft rfft dft fft2"),
    ("numbers.find_envelope()", "hilbert analytic_signal"),
    ("numbers.convolve_with([1, 2, 1])", "convolve correlate"),
    ("numbers.deconvolve_by([1, 2, 3])", "deconvolve deconv"),
    ("numbers.change_time_step(to=0.01, time_step=0.005)", "resample resample_poly decimate downsample"),
    ("numbers.start_chart()", "plot hist"),
    ("numbers.keep_random_numbers(3, with_seed=1)", "sample"),
    # NumPy + SciPy phase, batch 2: NumPy's choice puts back by default, as make_random_picks does
    ("numbers.make_random_picks(how_many=40, with_seed=1)", "choice choices randsample datasample"),
    ("numbers.take_log_odds()", "logit qlogis"),
    ("numbers.turn_into_chances()", "expit sigmoid plogis logsig logistic"),
    ("numbers.count_each()", "value_counts tabulate"),
    # NumPy + SciPy phase, batch 1 (approved by Manish 2026-11-25): words on numbers, grids and blocks alike
    ("numbers.turn_into_yes_or_no(is_above=20)", "mask logical_and logical_or logical_not greater less logical"),
    ("numbers.keep_numbers_where(yes_no)", "compress extract"),
    ('numbers.replace_numbers_where(yes_no, with_value="empty")', "ifelse"),
    ("numbers.count_numbers_that(is_above=25)", "count_nonzero nnz"),
    ("numbers.check_if_any_number(is_above=30)", "any sometrue"),
    ("numbers.check_if_all_numbers(is_at_least=0)", "all alltrue"),
    ("numbers.check_if_same_as(other, within=0.001)", "isclose allclose array_equal array_equiv is_same_as"),
    ("numbers.find_where_biggest()", "argmax nanargmax"),
    ("numbers.find_where_smallest()", "argmin nanargmin"),
    ("numbers.make_pair_table_with(other, by_subtracting=True)", "outer kron times_table_with bsxfun"),
    ("numbers.round_down()", "floor"),
    ("numbers.round_up()", "ceil ceiling"),
    ("numbers.take_whole_part()", "trunc fix modf"),
    ("numbers.take_sin(degrees=True)", "sin sind"),
    ("numbers.take_cos(degrees=True)", "cos cosd"),
    ("numbers.take_tan(degrees=True)", "tan tand"),
    ('numbers.change_angles_to("degrees")', "deg2rad rad2deg degrees radians"),
    ("numbers.divide_by(7, rounding_down=True)", "floor_divide floordiv"),
    ("numbers.take_fourier_transform(with_zero_in_middle=True)", "fftshift ifftshift"),
    # Numbers phase, batch 3 (approved by Manish 2026-11-25); the grid words' other names are in NumberGrid._HINTS
    ("numbers.turn_into_running_area(time_step=60)", "cumulative_trapezoid cumtrapz cumulative_simpson"),
    ("numbers.take_cube_root()", "cbrt nthroot"),
    ("numbers.find_coherence_with(other, time_step=0.01)", "coherence csd mscohere cohere"),
    ("numbers.take_cosine_transform()", "dct"),
    ('numbers.take_cosine_transform(kind="sine")', "dst"),
    ("numbers.show_as_fraction()", "nsimplify Rational rat as_fraction"),
    # families for 100 %, batches 10-12 (approved by Manish 2026-11-28, plan section 2.4): NumPy and R names
    ("numbers.find_product()", "prod product nanprod"),
    ('numbers.turn_into_running_total(show="product")', "cumprod nancumprod cumulative_prod"),
    ("numbers.turn_into_changes()", "diff ediff1d differences"),
    ("numbers.turn_into_slopes(time_step=1)", "gradient slopes"),
    ("numbers.count_in_bins(edges=[0, 10, 20, 50])", "histogram histogram_bin_edges histc hist_counts"),
    ("numbers.find_bin_of_each(edges=[0, 10, 20, 50])", "digitize findInterval discretize bin_of"),
    ('numbers.sort(show="positions")', "argsort order"),
    ("numbers.sort(then_by=other_numbers)", "lexsort"),
    ("numbers.keep_numbers_also_in(other_numbers)", "intersect intersect1d intersection"),
    ("numbers.remove_numbers_also_in(other_numbers)", "setdiff setdiff1d difference"),
    ("numbers.keep_numbers_in_only_one(other_numbers)", "setxor setxor1d symmetric_difference"),
    ("numbers.join_numbers_with(other_numbers)", "union union1d"),
    ('numbers.remove_duplicate_numbers(show="positions")', "unique_all"),
    ('numbers.remove_duplicate_numbers(show="which number")', "unique_inverse"),
    ("numbers.find_dot_product_with(other_numbers)", "dot vdot inner vecdot dot_product"),
    ("numbers.find_cross_product_with(other_numbers)", "cross cross_product"),
    ("numbers.find_positions_where(is_above=30)", "flatnonzero nonzero argwhere which find"),
    ("numbers.find_size()", "norm vector_norm magnitude"),
    ('numbers.change_angles_to("radians", remove_jumps=True)', "unwrap"),
]

# block.<name> (blocks of numbers, NumPy + SciPy phase batch 1). The words of numbers above work on blocks too.
_BLOCKS = [
    ('block.change_shape_to(8, "rest")', "reshape flatten_to resize"),
    ('block.add_direction("image", at_position=1)', "expand_dims newaxis atleast_1d atleast_2d atleast_3d unsqueeze"),
    ("block.remove_directions_of_size_one()", "squeeze"),
    ('block.swap_directions("row", "column")', "swapaxes permute_dims permute"),
    ('block.move_direction("colour", to_position=1)', "moveaxis movedim rollaxis"),
    ('block.reverse(over="row")', "flip fliplr flipud"),
    ("block.rotate(by_quarter_turns=1)", "rot90"),
    ('block.move_round_by(3, over="hour")', "roll circshift"),
    ('block.insert_numbers(0, at_position=2, over="row")', "insert"),
    ('block.repeat_each_number(3, over="hour")', "repeat repeat_interleave"),
    ('block.repeat_whole_block(24, over="hour")', "tile repmat"),
    ('block.add_numbers_from(other, over="row")', "concatenate hstack vstack append cat"),
    ('block.split_into_pieces(3, over="row")', "array_split split hsplit vsplit dsplit"),
    ('block.split_into_one_block_per("image")', "unstack unbind"),
    ("block.stretch_to((24, 8, 12))", "broadcast_to expand expand_as"),
    ("block.show_how_it_lines_up_with(other)", "broadcast_shapes broadcast"),
    ('block.keep_where("latitude", is_between=[60, 80])', "sel crop"),
    ('block.keep_by_position_in("image", [1, 3])', "isel take take_along"),
    ('block.remove_by_position_in("image", 40)', "delete drop_isel"),
    ("block.count_directions()", "ndim dim"),
    ("block.find_direction_names()", "dims dim_names"),
    ("block.find_shape()", "shape size_of"),
    # NumPy + SciPy phase, batch 2 (approved by Manish 2026-11-25)
    ('block.save("out.nc")', "to_netcdf"),
    ('block.find_average(in_each="month") for all Januaries together, or block.find_average(every="month") for each '
     'calendar month', "groupby resample climatology retime groupsummary"),
    ('block.find_average(in_groups_of={"latitude": 4, "longitude": 4})', "coarsen block_reduce blockproc aggregate"),
    ("block.find_values_at(latitude=60.5, longitude=5.25)",
     "interp interpn map_coordinates RegularGridInterpolator interp2 interp3 extract"),
    ("block.get_numbers_nearest_to(latitude=60.4, longitude=5.3)", "nearest knnsearch"),
    ('block.turn_into_change_from_average(in_each="month")', "anomalies anomaly"),
    ('block.smooth(over=["latitude", "longitude"], test_method="gaussian", width=2)',
     "gaussian_filter uniform_filter median_filter convolve2d rolling focal imgaussfilt medfilt2 conv2"),
    ("block.change_size_to(latitude=90, longitude=180)", "zoom imresize"),
    ("block.rotate(by_degrees=15)", "imrotate"),
    ('block.get_labels_of("time")', "coords indexes"),
    ('block.add_labels_to("time", dates)', "assign_coords set_index"),
]


# Tables finishing PR: names inside pandas' and Polars' namespaces, which mean something else on a table.
# str.<name>: pandas Series.str and Polars Expr.str (the text steps)
_TEXT = [
    ('table.keep_rows_where("name", contains="an") to keep the rows; for a yes or no column, a written condition: '
     "table.add_group_column(\"has_an\", rules={\"name contains 'an'\": \"yes\"}, otherwise=\"no\")",
     "contains contains_any"),
    ('table.keep_rows_where("name", starts_with="A")', "startswith starts_with"),
    ('table.keep_rows_where("name", ends_with="n")', "endswith ends_with"),
    ('table.keep_rows_where("sample_id", matches_pattern="^S[0-9]+$")', "match fullmatch"),
    ('table.turn_into_numbers("sample_id", show_problems=True) shows the cells that are not numbers; '
     'table.keep_rows_where("sample_id", matches_pattern="^[0-9]+$") keeps text made of digits (letters: '
     '"^[A-Za-z]+$")', "isdigit isnumeric isdecimal isalpha isalnum"),
    ("table.add_column(\"semicolons\", \"count_text(genes, ';')\")", "count count_matches"),
    ('table.add_column("name_length", "length(name)")', "len len_chars"),
    ('table.replace_text_in("name", "Mr ", with_value="")', "replace replace_all replace_many"),
    ('table.replace_text_in("name", matches_pattern="^Dr ", with_value="")',
     "removeprefix removesuffix strip_prefix strip_suffix"),
    ('table.add_column_with_part_of_text("code", from_column="sample_id", characters=[2, 4])', "slice get"),
    ('table.add_column_with_part_of_text("initial", from_column="name", first_characters=1)', "head"),
    ('table.add_column_with_part_of_text("last_two", from_column="name", last_characters=2)', "tail"),
    ('table.add_column_with_part_of_text("number", from_column="sample_id", matches_pattern="[0-9]+")',
     "extract extract_groups"),
    ('table.split_column("name", separator=" ", into=["first_name", "last_name"]) for new columns, or '
     'table.split_into_rows("genes", separator=";") for new rows', "split split_exact splitn rsplit"),
    ('table.add_column("name_and_class", by_joining_text=["name", "class"], separator=" ") joins columns side by '
     'side; table.find_summary_of("name", show=["joined text"], for_each_group_in="class") joins the text of many '
     "rows into one cell", "join cat concat"),
    ('table.add_column_with_part_of_text("found", from_column="genes", matches_pattern="[a-z]+[A-Z0-9]", '
     'every_match=True)',
     "extractall findall extract_all extract_many find_many"),
    ('table.add_column_with_part_of_text("where_an", from_column="name", position_of="an")',
     "find index rfind rindex"),
    ('table.turn_into_lowercase("name")', "lower to_lowercase casefold"),
    ('table.turn_into_uppercase("name")', "upper to_uppercase"),
    ('table.turn_into_title_case("name")', "title to_titlecase"),
    ('table.as_pandas(), then df["name"].str.capitalize() in pandas (a capital for the first letter of the whole text '
     "only; table.turn_into_title_case(\"name\") gives every word one), and give the result to sdata.table to come "
     "back", "capitalize"),
    ('table.as_pandas(), then df["name"].str.swapcase() in pandas, and give the result to sdata.table to come back: '
     "simplydata has no word that swaps capital and small letters", "swapcase"),
    ('table.remove_extra_spaces_in("name")', "strip lstrip rstrip strip_chars strip_chars_start strip_chars_end"),
    ('table.add_zeros_in_front_of("sample_id", to_length=3), which pads at the start (padding at the end is left '
     "to pandas: table.as_pandas())", "zfill pad rjust ljust center pad_start pad_end"),
    ('table.spread_into_yes_no_columns("fruit", separator="|")', "get_dummies"),
    ('table.turn_into_dates("when", written_like="03/15/2026")', "to_datetime strptime to_date to_time"),
    ('table.turn_into_numbers("price")', "to_integer to_decimal"),
    ('table.as_pandas(), then df["name"].str.normalize("NFC"), and give the result to sdata.table to come back (the '
     'manual chapter "From pandas (and Polars) to simplydata" says when you need it)', "normalize"),
    ('table.as_polars(), then pl.col("name").str.reverse() in Polars, and give the result to sdata.table to come '
     "back: simplydata has no word for text written backwards", "reverse"),
]

# dt.<name>: pandas Series.dt and Polars Expr.dt (the date steps)
_DATES = [
    ('table.add_column_with_part_of_date("year", from_column="date", part="year")', "year iso_year"),
    ('table.add_column_with_part_of_date("month", from_column="date", part="month")', "month"),
    ('table.add_column_with_part_of_date("day", from_column="date", part="day")', "day"),
    ('table.add_column_with_part_of_date("hour", from_column="time", part="hour")', "hour"),
    ('table.add_column_with_part_of_date("minute", from_column="time", part="minute")', "minute"),
    ('table.add_column_with_part_of_date("second", from_column="time", part="second")', "second"),
    ('table.add_column_with_part_of_date("quarter", from_column="date", part="quarter")', "quarter"),
    ('table.add_column_with_part_of_date("week", from_column="date", part="week")', "week isocalendar"),
    ('table.add_column_with_part_of_date("weekday", from_column="date", part="weekday")',
     "weekday day_of_week dayofweek"),
    ('table.add_column_with_part_of_date("weekday", from_column="date", part="weekday name")', "day_name"),
    ('table.add_column_with_part_of_date("month", from_column="date", part="month name")', "month_name"),
    ('table.add_column_with_part_of_date("day_number", from_column="date", part="day of year")',
     "day_of_year dayofyear ordinal_day"),
    ('table.add_column_with_part_of_date("day", from_column="time", part="date")', "date normalize"),
    ('table.add_column_with_part_of_date("clock", from_column="time", part="time")', "time"),
    ('table.add_column_with_part_of_date("days", from_column="date", part="days in month")',
     "days_in_month daysinmonth"),
    ('table.add_column_with_part_of_date("leap", from_column="date", part="is leap year")', "is_leap_year"),
    ('table.add_column_with_part_of_date("month_end", from_column="date", part="is month end")', "is_month_end"),
    ('table.add_column_with_part_of_date("first_day", from_column="date", part="is month start")', "is_month_start"),
    ('table.add_column_with_part_of_date("quarter_start", from_column="date", part="is quarter start")',
     "is_quarter_start"),
    ('table.add_column_with_part_of_date("quarter_end", from_column="date", part="is quarter end")', "is_quarter_end"),
    ('table.add_column_with_part_of_date("year_start", from_column="date", part="is year start")', "is_year_start"),
    ('table.add_column_with_part_of_date("year_end", from_column="date", part="is year end")', "is_year_end"),
    ('table.add_column_with_part_of_date("last_day", from_column="date", part="month end")', "month_end"),
    ('table.add_column_with_part_of_date("working", from_column="date", part="is working day")',
     "is_business_day is_busday"),
    ('table.add_column("due", "add_working_days(date, 10)")', "add_business_days"),
    ('table.add_column_with_part_of_date("seconds", from_column="date", part="unix time")', "epoch timestamp"),
    ('table.turn_into_text("date", written_like="2026-12-31"), then table.add_column("when", by_joining_text=["date", '
     '"clock"], separator=" "), then table.turn_into_dates("when")', "combine"),
    ('table.find_average_of("sales", for_each_group_in="date", every="month")', "to_period"),
    ('table.round_dates_in("date", down_to="month")', "floor truncate month_start"),
    ('table.round_dates_in("date", up_to="month")', "ceil"),
    ('table.round_dates_in("time", to_the="hour")', "round"),
    ('table.turn_into_text("date", written_like="31.12.2026")', "strftime to_string"),
    ('table.change_time_zone_in("time", to="UTC", recorded_in="Europe/Oslo")',
     "tz_convert tz_localize convert_time_zone replace_time_zone"),
    ('table.add_column("check_on", from_column="date", plus="1 month")', "offset_by"),
    ('table.add_column("days", by_subtracting=["end", "start"], counted_in="days")',
     "days total_days total_hours total_minutes total_seconds"),
    ('table.as_polars(), then pl.col("date").dt.replace(year=2026) in Polars, and give the result to sdata.table to '
     "come back: simplydata has no word that sets one part of a date", "replace"),
]

# groupby.<name>: pandas DataFrame.groupby() and Polars group_by(); the names not here mean the same as on a table
_GROUPS = [
    ('table.keep_groups_where("average(marks) >= 50", for_each_group_in="school")', "filter"),
    ('table.keep_rows_where("class", is_equal_to="A")', "get_group"),
    ('table.keep_first_rows(2, for_each_group_in="class")', "head"),
    ('table.keep_last_rows(2, for_each_group_in="class")', "tail"),
    ('table.count_rows(for_each_group_in="class")', "size len"),
    # pandas groupby().count() counts the filled cells of each column in each group
    ('table.find_summary_of(["marks", "hours"], show=["count"], for_each_group_in="class") counts the filled cells '
     "of each column (table.count_rows(for_each_group_in=\"class\") counts the rows)", "count"),
    ('table.find_summary_of(show={"marks": ["average", "count"], "hours": ["total"]}, for_each_group_in="class"): '
     "different measures for different columns, one row for each group", "agg aggregate"),
    ('table.check_if_all_values_in("marks", is_above=40, for_each_group_in="class")', "all"),
    ('table.check_if_any_value_in("marks", is_above=90, for_each_group_in="class")', "any"),
    ('table.find_summary_of("marks", show=["product"], for_each_group_in="class")', "prod product"),
    ('table.find_summary_of("name", show=["joined text"], for_each_group_in="class")', "implode"),
    ('table.find_correlation_between("hours", "marks") on the rows of one group (table.keep_rows_where first)',
     "corrwith"),
    ('table.add_column("share", "marks / total(marks) * 100", for_each_group_in="class")', "transform"),
    ('table.as_pandas(), then df.groupby("class").apply(my_function), and give the result to sdata.table to come '
     'back (simplydata runs your own function on each row with table.add_column(by_running=))',
     "apply map_groups pipe"),
    ('table.keep_biggest_rows(1, by="marks", for_each_group_in="class")', "idxmax arg_max"),
    ('table.keep_smallest_rows(1, by="marks", for_each_group_in="class")', "idxmin arg_min"),
    ('table.add_row_number_column("number", for_each_group_in="class")', "cumcount"),
    ('table.add_rank_column("group_number", from_column="class", biggest_first=False, when_tied="no gaps")',
     "ngroup"),
    ('table.add_running_column("so_far", from_column="marks", show="total", for_each_group_in="class")',
     "cumsum cum_sum"),
    ('table.add_running_column("best_so_far", from_column="marks", show="biggest", for_each_group_in="class")',
     "cummax cum_max"),
    ('table.add_running_column("lowest_so_far", from_column="marks", show="smallest", for_each_group_in="class")',
     "cummin cum_min"),
    ('table.as_pandas(), then df["price"] = df.groupby("shop")["price"].ffill() in pandas, and give the result to '
     "sdata.table to come back (table.fill_empty_cells_in(\"price\", with_the=\"value above\") fills the whole "
     "column)", "ffill forward_fill"),
    ('table.as_pandas(), then df["price"] = df.groupby("shop")["price"].bfill() in pandas, and give the result to '
     "sdata.table to come back (table.fill_empty_cells_in(\"price\", with_the=\"value below\") fills the whole "
     "column)", "bfill backward_fill"),
    ('table.find_summary_of("marks", show=["variance", "standard error", "skewness", "kurtosis"], '
     'for_each_group_in="class")', "var sem skew kurt kurtosis"),
    ('table.find_summary_of("marks", show=["count", "average", "standard deviation", "smallest", "percentile 25", '
     '"median", "percentile 75", "biggest"], for_each_group_in="class")', "describe"),
    ('table.add_previous_value_column("last_year", from_column="population", for_each_group_in="country"), or '
     "rows_ahead=1 for the next value", "shift"),
    ('table.add_rank_column("place", from_column="marks", for_each_group_in="class")', "rank"),
    ('table.add_rolling_column("smooth", from_column="sales", for_each_group_in="shop")', "rolling"),
]


def _build(groups):
    table = {}
    for written, names in groups:
        for name in names.split():
            assert name not in table, f"other name {name} is listed twice"
            table[name] = written
    return table


# list.<name> and arr.<name>: Polars list (and array) columns. simplydata keeps one value in each cell (G12, approved
# by Manish 2026-11-28), so every list job points to split_into_rows and the hand-over to Polars.
_LIST_POINTER = ('table.split_into_rows("genes", separator=";") gives each value a row of its own, where table words '
                 "work on it; list columns themselves are left to Polars: table.as_polars(), then pl.col(...).list")
_LISTS = [(_LIST_POINTER, "agg all any arg_max arg_min concat contains count_matches diff drop_nulls eval explode "
                          "filter first gather gather_every get head item join last len max mean median min "
                          "n_unique reverse sample set_difference set_intersection set_symmetric_difference "
                          "set_union shift slice sort std sum tail to_array to_map to_struct unique var")]


# Axes3D.<name>: the 3D Axes of mpl_toolkits.mplot3d, where scatter, plot and bar mean the 3D words
_CHART_3D = [
    ('chart.draw_dots_3d(x="east", y="north", z="height")', "scatter scatter3D"),
    ('chart.draw_lines_3d(x="east", y="north", z="height")', "plot plot3D"),
    ('chart.draw_bars_3d(x="month", y="city", z="rain")', "bar bar3d"),
    ('chart.draw_surface(x="east", y="north", z="height")', "plot_surface plot_trisurf"),
    ('chart.draw_surface(x="east", y="north", z="height", as_wires=True)', "plot_wireframe"),
    ('chart.label_z("Height (m)")', "set_zlabel"),
    ("chart.set_range_z(-10, 20)", "set_zlim set_zlim3d"),
    ("chart.put_ticks_z(-10, 0, 10, 20)", "set_zticks"),
    ("chart.look_from(height=20, around=45)", "view_init"),
]


# Numbers finishing PR (API audit of NumPy, SciPy and SymPy, 2026-11-27): names typed with np., numpy., np.linalg.,
# np.random., rng., np.fft., scipy., stats., optimize., integrate., interpolate., signal., ndimage., spatial.,
# special., sp. or sympy. in front. Inside NumPy, mean is the average of numbers (not of a table column), diff is the
# differences of numbers (not a slope formula), zeros makes a grid (not the zeros of a system) and norm is the length
# of a vector (not the normal distribution). A name a list does not hold falls back to the lists in
# NAMESPACE_FALLBACK below. A job left to the library points to the hand-over (numbers.as_numpy(),
# formula.as_sympy()).
_NUMPY_HAND_OVER = ("numbers.as_numpy() hands the numbers to NumPy (a grid too: grid.as_numpy()), where the NumPy "
                    "call works")
# np.<name>: NumPy's top level
_NUMPY = [
    # families for 100 %, batches 1-2: working days (np.busday_count, busday_offset, is_busday, busdaycalendar)
    ('table.add_column("days", "count_working_days(start, end)"), on a table', "busday_count"),
    ('table.add_column("due", "add_working_days(date, 10)"), on a table', "busday_offset"),
    ('table.add_column_with_part_of_date("working", from_column="date", part="is working day"), on a table',
     "is_busday"),
    ('sdata.make_run_of_dates("2026-12-01", to="2026-12-31", every="working day"): Monday to Friday (holidays are '
     "left to NumPy: numbers.as_numpy())", "busdaycalendar"),
    ("numbers.find_average()", "mean average nanmean"),
    ("numbers.find_median()", "median nanmedian"),
    ("numbers.find_total()", "sum nansum"),
    ("numbers.find_smallest()", "min amin nanmin"),
    ("numbers.find_biggest()", "max amax nanmax"),
    ("numbers.find_biggest() - numbers.find_smallest()", "ptp"),
    ("numbers.find_standard_deviation()", "std nanstd"),
    ("numbers.find_standard_deviation() ** 2 for the variance (or sdata.distribution(...).find_variance())",
     "var nanvar"),
    ("numbers.find_percentile(90)", "percentile nanpercentile quantile nanquantile"),
    ("numbers.turn_into_running_total()", "cumsum nancumsum cumulative_sum"),
    ("numbers.take_square_root()", "sqrt"),
    ("numbers.take_absolute_value()", "abs absolute fabs"),
    ("numbers.take_exp()", "exp"),
    ('numbers.take_log() for the natural log, or numbers.take_log(base=10)', "log log10 log2"),
    ("numbers.raise_to_power(2)", "power pow float_power square"),
    ("numbers.times(3)", "multiply"),
    ("numbers.times(-1)", "negative"),
    ("numbers.divide_by(2)", "divide true_divide"),
    ("numbers.round_to(with_decimals=2)", "round around rint"),
    ("numbers.reverse() for numbers, or block.reverse(over=\"row\") for a block", "flip"),
    ("numbers.remove_duplicate_numbers()", "unique unique_values"),
    ("numbers.count_each()", "unique_counts bincount"),
    ("numbers.count()", "size"),
    ("numbers.turn_into_yes_or_no(is_empty=True)", "isnan"),
    ("numbers.fill_empty_numbers(with_value=0)", "nan_to_num"),
    ("numbers.replace_each_number_that(is_above=100, with_value=100)", "clip"),
    ("numbers.replace_each_number_that(is_below=0, with_value=0) to keep every number at 0 or above",
     "maximum fmax"),
    ("numbers.replace_each_number_that(is_above=100, with_value=100) to keep every number at 100 or below",
     "minimum fmin"),
    ('numbers.replace_each_number_that(is_above=100, with_value=100), or numbers.replace_numbers_where(yes_no, '
     'with_value=0) with a yes or no list', "where"),
    ("numbers.turn_into_yes_or_no(is_one_of=[1, 2])", "isin"),
    ("numbers.turn_into_yes_or_no(is_at_least=20)", "greater_equal"),
    ("numbers.turn_into_yes_or_no(is_at_most=20)", "less_equal"),
    ("numbers.turn_into_yes_or_no(is_equal_to=20)", "equal"),
    ("numbers.turn_into_yes_or_no(is_not_equal_to=20)", "not_equal"),
    (_NUMPY_HAND_OVER + ": np.logical_xor(first_yes_no.as_numpy(), second_yes_no.as_numpy())", "logical_xor"),
    ("grid.swap_rows_and_columns()", "transpose matrix_transpose"),
    ("grid.get_all_numbers()", "ravel"),
    ("grid.get_numbers_from_each_row_at(columns=[2, 1, 3])", "take_along_axis"),
    ("numbers.turn_into_running_area(time_step=1), whose last number is the whole area", "trapezoid trapz"),
    ('table.find_correlation_between("hours", "marks", "height", show="covariance") on the columns of a table',
     "cov"),
    ('table.find_correlation_between("hours", "marks") on the columns of a table', "corrcoef"),
    ('numbers.save("numbers.csv")', "save savetxt savez savez_compressed tofile"),
    ('sdata.number_list("readings.txt")', "load fromfile fromregex fromstring"),
    # families for 100 %, batches 10-13 (approved by Manish 2026-11-28, plan section 2.4): lists and grids
    ("numbers.turn_into_changes() (rows_back=12 for a lag, how_many_times=2 for the changes of the changes)",
     "diff ediff1d"),
    ("numbers.turn_into_slopes(time_step=1)", "gradient"),
    ('numbers.count_in_bins(edges=[0, 10, 20, 50]), or numbers.count_in_bins(edges="sturges") for the edges by a rule',
     "histogram histogram_bin_edges"),
    ("numbers.count_in_bins(edges=5, together_with=other_numbers): the pairs counted in a grid of bins (more than two "
     "lists are left to NumPy: numbers.as_numpy())", "histogram2d histogramdd"),
    ("numbers.find_bin_of_each(edges=[0, 10, 20, 50])", "digitize"),
    ('numbers.find_bin_of_each(edges=sorted_numbers, bins_include="right edge"): NumPy searchsorted(a, v) is the bin '
     "of each v among the edges a", "searchsorted"),
    ("numbers.find_product()", "prod nanprod"),
    ('numbers.turn_into_running_total(show="product")', "cumprod nancumprod cumulative_prod"),
    ("numbers.find_dot_product_with(other_numbers)", "dot vdot inner vecdot"),
    ("grid.multiply_as_matrix_by(other_grid) (other numbers: NumPy matvec; from_the_left=True: vecmat; a list of "
     "grids: multi_dot)", "matmul matvec vecmat tensordot"),
    ("numbers.find_cross_product_with(other_numbers)", "cross"),
    (_NUMPY_HAND_OVER + ": np.einsum(\"ij,jk->ik\", grid.as_numpy(), other.as_numpy()) (its own notation, left to "
     "NumPy; grid.multiply_as_matrix_by(other_grid) covers the usual uses)", "einsum einsum_path"),
    ('grid.get_part("diagonal").find_total()', "trace"),
    ('grid.get_part("diagonal")', "diagonal diag"),
    ('sdata.number_grid([1, 2, 3], kind="diagonal")', "diagflat"),
    ('grid.get_part("upper triangle")', "triu"),
    ('grid.get_part("lower triangle")', "tril"),
    ('grid.get_part("upper triangle", as_list=True)', "triu_indices triu_indices_from mask_indices"),
    ('grid.get_part("lower triangle", as_list=True)', "tril_indices tril_indices_from"),
    ('grid.replace_part("diagonal", with_value=1)', "fill_diagonal diag_indices diag_indices_from"),
    ('sdata.number_grid(kind="identity", size=3)', "eye identity"),
    ('sdata.number_grid(kind="ones below diagonal", rows=3)', "tri"),
    ('sdata.number_grid([1, 2, 3], kind="vandermonde")', "vander"),
    ('sdata.number_grid(kind="blocks", of=[[first, second], [third, fourth]])', "block bmat"),
    ('numbers.sort(show="positions")', "argsort"),
    ("numbers.sort(then_by=other_numbers)", "lexsort"),
    ("numbers.sort(): NumPy partition puts only some numbers in their place, a faster part of a sort; "
     'numbers.sort(show="positions") gives the positions', "partition argpartition"),
    ("sdata.make_coordinate_grids(x=[0, 1, 2], y=[10, 20]) gives the x grid and the y grid", "meshgrid mgrid ogrid"),
    ("sdata.make_coordinate_grids(rows=2, columns=3) gives the row and column numbers (from 1)", "indices"),
    ('sdata.polynomial("from numbers", numbers=[1, 0, -2]), then formula.find_value_at(x=numbers)', "polyval poly1d"),
    ('sdata.polynomial("from numbers", numbers=[1, 0, -2]), then formula.find_slope_formula()', "polyder"),
    ('sdata.polynomial("from numbers", numbers=[1, 0, -2]), then formula.find_area_formula()', "polyint"),
    ('sdata.polynomial("from roots", roots=[1, 2, 3])', "poly"),
    ('sdata.formula(f"({first}) + ({second})") for two formulas (minus for polysub, times for polymul)',
     "polyadd polysub polymul"),
    ("formula.as_sympy() hands the formula to SymPy, where sp.div(first, second) divides one polynomial by another",
     "polydiv"),
    ("grid.find_positions_where(is_above=30)", "argwhere nonzero unravel_index"),
    ("numbers.find_positions_where(is_above=30), or grid.find_positions_where(is_above=30, show=\"position in list\")",
     "flatnonzero ravel_multi_index"),
    ("grid.keep_rows_by_position(1, to=2).keep_columns_by_position(2, to=3) for a block of rows and columns, or "
     "grid.get_numbers_at_pairs(rows=[1, 2], columns=[3, 3])", "ix_"),
    ("grid.add_border(width=2, with_value=0)", "pad"),
    ("numbers.replace_numbers_where(at_positions=[1, 3], with_value=0)", "put put_along_axis"),
    ("numbers.replace_numbers_where(yes_no, with_value=other_numbers): each from its own place",
     "copyto putmask place"),
    ("numbers.replace_numbers_where(rules=[(cold, -1), (warm, 1)])", "select piecewise"),
    ("numbers.keep_numbers_also_in(other_numbers)", "intersect1d"),
    ("numbers.remove_numbers_also_in(other_numbers)", "setdiff1d"),
    ("numbers.keep_numbers_in_only_one(other_numbers)", "setxor1d"),
    ("numbers.join_numbers_with(other_numbers)", "union1d"),
    ('numbers.remove_duplicate_numbers(show="positions")', "unique_all"),
    ('numbers.remove_duplicate_numbers(show="which number")', "unique_inverse"),
    ('sdata.number_list(1, to=1000, how_many=4, spacing="log") (NumPy logspace(0, 3, 4) gives the same from the powers '
     "of 10)", "geomspace logspace"),
    ('sdata.number_grid(from_formula="row * column", rows=3, columns=4)', "fromfunction"),
    ('numbers.change_angles_to("radians", remove_jumps=True)', "unwrap"),
    ('sdata.make_window_shape("bartlett", how_many=64)', "bartlett"),
    ('sdata.make_window_shape(("kaiser", 5), how_many=64)', "kaiser"),
    ("sdata.number_list([3, 5, 2]) for a list, sdata.number_grid([[1, 2], [3, 4]]) for a grid (a copy of numbers: "
     "sdata.number_list(numbers))", "asarray asanyarray asarray_chkfinite asmatrix copy fromiter frombuffer"),
    (_NUMPY_HAND_OVER + ": numbers.as_numpy().astype(int) (simplydata keeps whole numbers and decimals itself; to "
     "change the values, numbers.round_to() or numbers.take_whole_part())", "astype"),
    (_NUMPY_HAND_OVER + ": np.trim_zeros(numbers.as_numpy())", "trim_zeros"),
    # numpy.polynomial (np.polynomial.Legendre ...): the same polynomials as sdata.polynomial
    ('sdata.polynomial("legendre", degree=3)', "Legendre legval legfromroots"),
    ('sdata.polynomial("chebyshev", degree=3)', "Chebyshev chebval chebfromroots"),
    ('sdata.polynomial("hermite", degree=3)', "Hermite hermval hermfromroots"),
    ('sdata.polynomial("probabilists hermite", degree=3)', "HermiteE hermeval hermefromroots"),
    ('sdata.polynomial("laguerre", degree=3)', "Laguerre lagval lagfromroots"),
    ('sdata.polynomial("from numbers", numbers=[1, 0, -2])', "Polynomial"),
    ('sdata.polynomial("from roots", roots=[1, 2, 3])', "polyfromroots"),
]  # sign, arcsin ... gcd, lcm: the maths family below (families for 100 %, batches 7-9)

# linalg.<name>: np.linalg and scipy.linalg
_GRID = "sdata.number_grid([[4, 2, 1], [2, 3, 0.5], [1, 0.5, 2]])"
_LINALG = [
    (f"grid.solve_for([1, 2, 3]), on a grid made with {_GRID}",
     "solve solve_triangular solve_banded solveh_banded solve_toeplitz solve_circulant lu_solve cho_solve "
     "tensorsolve mldivide"),
    ("grid.solve_for([6, 5, 7, 10]), on a grid that is not square (least squares)", "lstsq"),
    ('grid.break_down(test_method="svd")', "svd svdvals diagsvd"),
    ('grid.break_down(test_method="qr")', "qr"),
    ('grid.break_down(test_method="lu")', "lu lu_factor"),
    ('grid.break_down(test_method="cholesky")', "cholesky cho_factor"),
    ('grid.break_down(test_method="schur")', "schur rsf2csf"),
    ('grid.break_down(test_method="polar")', "polar"),
    ('grid.break_down(test_method="ldl")', "ldl"),
    ('grid.break_down(test_method="hessenberg")', "hessenberg"),
    (f'grid.break_down(test_method="qz", together_with={_GRID})', "qz ordqz"),
    ("grid.find_determinant()", "det"),
    ("grid.take_inverse()", "inv"),
    ("grid.find_eigenvalues()", "eig eigh eigvals eigvalsh"),
    ("grid.find_null_space()", "null_space"),
    ("grid.take_matrix_exp()", "expm"),
    # families for 100 %, batches 11-12 (approved by Manish 2026-11-28, plan section 2.4)
    ("numbers.find_size() for numbers, grid.find_size() for a grid", "norm"),
    ("numbers.find_size()", "vector_norm"),
    ("grid.find_size()", "matrix_norm"),
    ("grid.find_rank()", "matrix_rank"),
    ("grid.find_condition_number()", "cond"),
    ("grid.take_inverse(closest_possible=True)", "pinv pinvh"),
    ("grid.find_determinant(as_log=True)", "slogdet"),
    ("grid.multiply_as_matrix_by([second_grid, third_grid])", "multi_dot"),
    ("grid.multiply_as_matrix_by(other_grid)", "matmul tensordot"),
    ("numbers.find_dot_product_with(other_numbers)", "vecdot"),
    ("numbers.find_cross_product_with(other_numbers)", "cross"),
    ('grid.get_part("diagonal")', "diagonal"),
    ('grid.get_part("diagonal").find_total()', "trace"),
    ("grid.find_column_space()", "orth"),
    ('sdata.number_grid(kind="toeplitz", first_column=[1, 2, 3])', "toeplitz"),
    ('sdata.number_grid(kind="hankel", first_column=[1, 2, 3], last_row=[3, 4, 5])', "hankel"),
    ('sdata.number_grid(kind="circulant", first_column=[1, 2, 3])', "circulant"),
    ('sdata.number_grid([1, -6, 11, -6], kind="companion")', "companion"),
    ('sdata.number_grid([1, -6, 11, -6], kind="fiedler companion")', "fiedler_companion"),
    ('sdata.number_grid([1, 4, 6], kind="fiedler")', "fiedler"),
    ('sdata.number_grid([1, 2], kind="convolution", size=3)', "convolution_matrix"),
    ('sdata.number_grid(kind="hadamard", size=4)', "hadamard"),
    ('sdata.number_grid(kind="hilbert", size=3)', "hilbert"),
    ('sdata.number_grid(kind="inverse hilbert", size=3)', "invhilbert"),
    ('sdata.number_grid(kind="pascal", size=3) ("lower pascal", "upper pascal" for the triangles)', "pascal"),
    ('sdata.number_grid(kind="inverse pascal", size=3)', "invpascal"),
    ('sdata.number_grid(kind="leslie", first_row=[0.1, 2, 1], survival=[0.2, 0.8])', "leslie"),
    ('sdata.number_grid(kind="helmert", size=4)', "helmert"),
    ('sdata.number_grid(kind="block diagonal", of=[first, second])', "block_diag"),
    ('sdata.number_grid(kind="toeplitz", first_column=[1, 2, 3]).multiply_as_matrix_by(other_numbers)',
     "matmul_toeplitz"),
    ("numbers.take_fourier_transform(show=\"all\"): the Fourier transform without the grid of complex numbers (NumPy "
     "and SciPy dft makes that grid)", "dft"),
    (_NUMPY_HAND_OVER + ": np.linalg.tensorinv(grid.as_numpy(), ind=1)", "tensorinv"),
]

# families for 100 %, batch 19 (approved by Manish 2026-11-28, plan section 2.8, G7): the names of scipy.linalg
_LINALG += [
    ('grid.take_matrix_function("log")', "logm"),
    ('grid.take_matrix_function("square root")', "sqrtm"),
    ('grid.take_matrix_function("cos")', "cosm"),
    ('grid.take_matrix_function("sin")', "sinm"),
    ('grid.take_matrix_function("tan")', "tanm"),
    ('grid.take_matrix_function("cosh")', "coshm"),
    ('grid.take_matrix_function("sinh")', "sinhm"),
    ('grid.take_matrix_function("tanh")', "tanhm"),
    ('grid.take_matrix_function("sign")', "signm"),
    ('grid.take_matrix_function("power", power=0.5) (a whole power uses NumPy matrix_power)',
     "fractional_matrix_power matrix_power"),
    ('grid.take_matrix_function("1 / (1 + x)"): any formula of x', "funm"),
    ('grid.check_if_grid_is("symmetric")', "issymmetric"),
    ('grid.check_if_grid_is("hermitian")', "ishermitian"),
    ('grid.check_if_grid_is("banded"), which prints how many diagonals below and above hold numbers', "bandwidth"),
    ("grid.find_best_rotation_to(other_grid)", "orthogonal_procrustes"),
    ("grid.find_angles_to(other_grid)", "subspace_angles"),
    ('sdata.solve_matrix_equation("lyapunov", a=grid, q=other_grid)', "solve_lyapunov solve_continuous_lyapunov"),
    ('sdata.solve_matrix_equation("discrete lyapunov", a=grid, q=other_grid)', "solve_discrete_lyapunov"),
    ('sdata.solve_matrix_equation("sylvester", a=grid, b=other_grid, q=third_grid)', "solve_sylvester"),
    ('sdata.solve_matrix_equation("riccati", a=grid, b=other_grid, q=third_grid, r=fourth_grid)',
     "solve_continuous_are"),
    ('sdata.solve_matrix_equation("discrete riccati", a=grid, b=other_grid, q=third_grid, r=fourth_grid)',
     "solve_discrete_are"),
    ('grid.solve_for([1, 2, 3], structure="banded"), on a symmetric banded grid (Cholesky on the band)',
     "cho_solve_banded cholesky_banded"),
    ('grid.find_eigenvalues(structure="banded")', "eig_banded eigvals_banded"),
    ('grid.find_eigenvalues(structure="tridiagonal")', "eigh_tridiagonal eigvalsh_tridiagonal"),
    ('grid.break_down(test_method="rq")', "rq"),
    ('grid.break_down(test_method="cs"), on a grid with columns of length 1 at right angles, such as '
     "sdata.number_grid([[0, 1], [1, 0]])", "cossin"),
    ('grid.break_down(test_method="real eigen blocks")', "cdf2rdf"),
    ("grid.make_pair_table_with(other_grid, as_blocks=True, column_by_column=True)", "khatri_rao"),
    # not user jobs (d): steps inside the solvers, updates of a decomposition and a random sketch
    (_NUMPY_HAND_OVER + ": scipy.linalg.expm_frechet(grid.as_numpy(), other.as_numpy()); grid.take_matrix_exp() "
     "gives the matrix exponential itself", "expm_cond expm_frechet"),
    (_NUMPY_HAND_OVER + ': scipy.linalg.qr_update on the parts of grid.break_down(test_method="qr"); a new '
     "break_down gives the same parts", "qr_delete qr_insert qr_update qr_multiply"),
    (_NUMPY_HAND_OVER + ": scipy.linalg.matrix_balance(grid.as_numpy()); SciPy balances the grid inside "
     "find_eigenvalues already", "matrix_balance"),
    (_NUMPY_HAND_OVER + ": scipy.linalg.clarkson_woodruff_transform(grid.as_numpy(), 100), a random sketch of a "
     "tall grid", "clarkson_woodruff_transform"),
]

# random.<name>: np.random, a NumPy Generator (rng = np.random.default_rng()) and Python's random
_RANDOM = [
    ("sdata.make_random_numbers(how_many=100, average=50, standard_deviation=10, with_seed=1)",
     "normal standard_normal randn gauss normalvariate"),
    ("sdata.make_random_numbers(how_many=100, between=[0, 1], with_seed=1)", "uniform random rand random_sample"),
    ("sdata.make_random_numbers(how_many=10, between=[1, 6], whole_numbers=True, with_seed=1)",
     "integers randint random_integers randrange"),
    ("sdata.make_random_numbers(how_many=10, with_seed=1): with_seed= makes the same numbers each time",
     "seed default_rng Generator RandomState SeedSequence"),
    ("numbers.make_random_picks(how_many=40, with_seed=1)", "choice choices"),
    ("numbers.keep_random_numbers(numbers.count(), with_seed=1) puts every number in a random order",
     "permutation shuffle permuted"),
    ("numbers.keep_random_numbers(5, with_seed=1) keeps 5 numbers at random, each once", "sample"),
    ('sdata.distribution("binomial", tries=10, chance=0.3).make_random_numbers(how_many=100)', "binomial"),
    ('sdata.distribution("poisson", average=3).make_random_numbers(how_many=100)', "poisson"),
    ('sdata.distribution("gamma", shape=2).make_random_numbers(how_many=100)',
     "gamma standard_gamma gammavariate"),
    ('sdata.distribution("beta", shape1=2, shape2=5).make_random_numbers(how_many=100)', "beta betavariate"),
    ('sdata.distribution("exponential", rate=2).make_random_numbers(how_many=100)',
     "exponential standard_exponential expovariate"),
    ('sdata.distribution("lognormal", log_average=0, log_standard_deviation=1).make_random_numbers(how_many=100)',
     "lognormal lognormvariate"),
    ('sdata.distribution("chi-square", degrees_of_freedom=3).make_random_numbers(how_many=100)', "chisquare"),
    ('sdata.distribution("F", degrees_of_freedom_1=3, degrees_of_freedom_2=20).make_random_numbers(how_many=100)',
     "f"),
    ('sdata.distribution("t", degrees_of_freedom=5).make_random_numbers(how_many=100)', "standard_t"),
    ('sdata.distribution("weibull", shape=1.5).make_random_numbers(how_many=100)', "weibull weibullvariate"),
    ('sdata.distribution("gumbel", location=0, scale=1).make_random_numbers(how_many=100)', "gumbel"),
    ('sdata.distribution("laplace", location=0, scale=1).make_random_numbers(how_many=100)', "laplace"),
    ('sdata.distribution("logistic", location=0, scale=1).make_random_numbers(how_many=100)', "logistic"),
    ('sdata.distribution("cauchy", location=0, scale=1).make_random_numbers(how_many=100)', "standard_cauchy"),
    ('sdata.distribution("pareto", shape=3).make_random_numbers(how_many=100) (NumPy\'s pareto gives these numbers '
     "minus 1, the Lomax distribution)", "pareto paretovariate"),
    ('sdata.distribution("triangular", lowest=0, highest=10, peak=3).make_random_numbers(how_many=100)',
     "triangular"),
    ('sdata.distribution("von mises", average=0, concentration=2).make_random_numbers(how_many=100)',
     "vonmises vonmisesvariate"),
    ('sdata.distribution("inverse gaussian", average=1, shape=2).make_random_numbers(how_many=100)', "wald"),
    ('sdata.distribution("geometric", chance=0.2).make_random_numbers(how_many=100)', "geometric"),
    ('sdata.distribution("hypergeometric", marked=10, unmarked=40, drawn=5).make_random_numbers(how_many=100)',
     "hypergeometric"),
    # families for 100 %, batches 5-6: the joint distributions of a NumPy Generator (G4)
    ('sdata.distribution("dirichlet", concentrations=[2, 3, 5]).make_random_numbers(how_many=100)', "dirichlet"),
    ('sdata.distribution("multinomial", tries=10, chances=[0.2, 0.3, 0.5]).make_random_numbers(how_many=100)',
     "multinomial"),
    ('sdata.distribution("multivariate normal", averages=[0, 0], covariance=[[1, 0.5], [0.5, 2]])'
     ".make_random_numbers(how_many=100)", "multivariate_normal"),
    ('sdata.distribution("multivariate hypergeometric", counts=[5, 3, 2], drawn=4).make_random_numbers(how_many=100)',
     "multivariate_hypergeometric"),
    ('sdata.distribution("negative binomial", size=3, chance=0.4).make_random_numbers(how_many=100)',
     "negative_binomial"),
]

# fft.<name>: np.fft and scipy.fft
_FFT = [
    ("numbers.take_fourier_transform(time_step=0.01)", "fft rfft dft fftfreq rfftfreq"),
    ("sdata.find_inverse_fourier_transform(table), on the table take_fourier_transform gives", "ifft irfft"),
    ("numbers.take_fourier_transform(with_zero_in_middle=True)", "fftshift ifftshift"),
    ("numbers.take_cosine_transform()", "dct"),
    ('numbers.take_cosine_transform(kind="sine")', "dst"),
    # families for 100 %, batch 11 (approved by Manish 2026-11-28, plan section 2.4)
    ('grid.take_fourier_transform(over="rows and columns") (show="all" for fft2; one direction: over="rows")',
     "fft2 rfft2 fftn rfftn"),
    ("sdata.find_inverse_fourier_transform(table), on the table grid.take_fourier_transform gives",
     "ifft2 irfft2 ifftn irfftn"),
    ("numbers.take_fourier_transform(): NumPy ihfft of real numbers is the conjugate of rfft divided by their count, "
     "and hfft the real spectrum of a signal given by its half spectrum (sdata.find_inverse_fourier_transform turns "
     "a half spectrum back)", "hfft ihfft hfft2 hfftn ihfft2 ihfftn"),
    ('numbers.take_cosine_transform(inverse=True) (kind="sine" for idst)', "idct idst"),
    ("grid.take_cosine_transform() (kind=\"sine\" for dstn, inverse=True for idctn and idstn)",
     "dctn dstn idctn idstn"),
    ('numbers.take_cosine_transform(kind="hankel", log_step=0.1, order=0) (inverse=True for ifht; SciPy fhtoffset '
     "gives a good offset for it)", "fht ifht fhtoffset"),
]

# stats.<name>: scipy.stats (the distributions; its tests fall back to the sdata and table words)
_STATS = [
    ('sdata.distribution("normal", average=50, standard_deviation=10)', "norm"),
    ('sdata.distribution("lognormal", log_average=0, log_standard_deviation=1)', "lognorm"),
    ('sdata.distribution("exponential", rate=2)', "expon"),
    ('sdata.distribution("gamma", shape=2, rate=1)', "gamma"),
    ('sdata.distribution("beta", shape1=2, shape2=5)', "beta"),
    ('sdata.distribution("uniform", lowest=0, highest=1)', "uniform"),
    ('sdata.distribution("t", degrees_of_freedom=5)', "t"),
    ('sdata.distribution("chi-square", degrees_of_freedom=3)', "chi2"),
    ('sdata.distribution("F", degrees_of_freedom_1=3, degrees_of_freedom_2=20)', "f"),
    ('sdata.distribution("weibull", shape=1.5)', "weibull_min"),
    ('sdata.distribution("cauchy", location=0, scale=1)', "cauchy"),
    ('sdata.distribution("logistic", location=0, scale=1)', "logistic"),
    ('sdata.distribution("laplace", location=0, scale=1)', "laplace"),
    ('sdata.distribution("gumbel", location=0, scale=1)', "gumbel_r"),
    ('sdata.distribution("pareto", shape=3)', "pareto"),
    ('sdata.distribution("gev", location=0, scale=1, shape=0.1)', "genextreme"),
    ('sdata.distribution("generalised pareto", scale=1, shape=0.1)', "genpareto"),
    ('sdata.distribution("triangular", lowest=0, highest=10, peak=3)', "triang"),
    ('sdata.distribution("half-normal", standard_deviation=1)', "halfnorm"),
    ('sdata.distribution("inverse gaussian", average=1, shape=2)', "invgauss"),
    ('sdata.distribution("von mises", average=0, concentration=2)', "vonmises"),
    ('sdata.distribution("binomial", tries=10, chance=0.3)', "binom"),
    ('sdata.distribution("bernoulli", chance=0.3)', "bernoulli"),
    ('sdata.distribution("poisson", average=3)', "poisson"),
    ('sdata.distribution("negative binomial", size=3, chance=0.4)', "nbinom"),
    ('sdata.distribution("geometric", chance=0.2)', "geom"),
    ('sdata.distribution("hypergeometric", marked=10, unmarked=40, drawn=5)', "hypergeom"),
    ('sdata.distribution("whole number uniform", lowest=1, highest=6)', "randint"),
    ('sdata.distribution("normal", average=50, standard_deviation=10).find_middle_range(95)', "interval"),
    ('table.compare_survival(time="days", event="died", for_each_group_in="treatment")', "logrank"),
    ('table.add_adjusted_p_value_column("p_adjusted", test_method="benjamini-hochberg")', "false_discovery_control"),
    ('table.add_rank_column("rank", from_column="marks")', "rankdata"),
    ('table.compare_shape_to("marks", "normal"), on one subject (one row per child)', "kstest ks_1samp jarque_bera"),
    ('chart.draw_cumulative_share(x="marks")', "ecdf"),
    # families for 100 %, batches 3-4 (approved by Manish 2026-11-28): the scipy.stats tests and summaries of plan
    # section 2.2, each to the word and the option value that runs it
    ('table.compare_averages_of("marks", for_each_group_in="class", test_method="alexander-govern"), on one subject',
     "alexandergovern"),
    ('table.compare_averages_of("days", for_each_group_in="treatment", test_method="brunner-munzel"), on two groups',
     "brunnermunzel"),
    ('table.compare_averages_of("days", for_each_group_in="treatment", test_method="wilcoxon rank sum")',
     "ranksums"),
    ('table.compare_averages_of("days", for_each_group_in="treatment", test_method="baumgartner-weiss-schindler")',
     "bws_test"),
    ('table.compare_averages_of("marks", for_each_group_in="class", test_method="median") (Mood\'s median test)',
     "median_test"),
    ('table.compare_averages_of("days", for_each_group_in="treatment", test_method="mann-whitney"), which allows '
     "for ties itself", "tiecorrect"),
    ('table.compare_average_to("marks", value=60), on one subject', "ttest_1samp"),
    ('table.compare_each_pair_of("marks", for_each_group_in="class", test_method="tukey")', "tukey_hsd"),
    ('table.compare_spreads_of("marks", for_each_group_in="class", test_method="levene"), on one subject', "levene"),
    ('table.compare_spreads_of("marks", for_each_group_in="class", test_method="bartlett")', "bartlett"),
    ('table.compare_spreads_of("marks", for_each_group_in="class", test_method="fligner")', "fligner"),
    ('table.compare_spreads_of("days", for_each_group_in="treatment", test_method="ansari")', "ansari"),
    ('table.compare_spreads_of("days", for_each_group_in="treatment", test_method="mood")', "mood"),
    ('table.compare_spreads_of("marks", for_each_group_in="class", test_method="o\'brien")', "obrientransform"),
    ('table.compare_shapes_of("days", for_each_group_in="treatment", test_method="cramer-von mises")',
     "cramervonmises_2samp"),
    ('table.compare_shapes_of("days", for_each_group_in="treatment", test_method="epps-singleton")',
     "epps_singleton_2samp"),
    ('table.compare_shape_to("marks", sdata.distribution("normal", average=60, standard_deviation=15), '
     'test_method="cramer-von-mises")', "cramervonmises"),
    ('table.compare_shape_to("days", "gamma"), Anderson-Darling with a fitted distribution', "goodness_of_fit"),
    ('table.compare_shape_to("marks", "normal", test_method="skewness")', "skewtest"),
    ('table.compare_shape_to("marks", "normal", test_method="kurtosis")', "kurtosistest"),
    ('table.compare_counts_of("died", for_each_group_in="treatment", test_method="barnard"), on a 2 x 2 table',
     "barnard_exact"),
    ('table.compare_counts_of("died", for_each_group_in="treatment", test_method="boschloo"), on a 2 x 2 table',
     "boschloo_exact"),
    ('table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})', "chisquare"),
    ('table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4}, test_method="g") (also "freeman-tukey", '
     '"neyman", "modified g", "cressie-read")', "power_divergence"),
    ('table.compare_percent_to("breakfast", value="yes", percent=50)', "binomtest"),
    ('table.find_median_of("marks", interval=95), or table.find_percentile_of("marks", 90, interval=95): the exact '
     "interval from the order of the values", "quantile_test"),
    ('table.compare_rates("infections", time="patient_days", for_each_group_in="ward", test_method="e-test")',
     "poisson_means_test"),
    ('table.compare_averages_of("days", for_each_group_in="treatment", p_value_by="shuffling"), and p_value_by= on '
     "the other tests", "permutation_test monte_carlo_test PermutationMethod MonteCarloMethod"),
    ('table.find_interval_of("marks", "median", test_method="bootstrap")', "BootstrapMethod"),
    ('table.find_interval_of("marks", "average", test_method="bayesian") (also "variance", "standard deviation")',
     "bayes_mvs mvsdist"),
    ('table.find_correlation_between("hours", "marks", test_method="chatterjee xi"), on one subject', "chatterjeexi"),
    ('table.find_correlation_between("hours", "marks", test_method="weighted kendall")', "weightedtau"),
    ('table.find_correlation_between("hours", "marks", test_method="multiscale graph")', "multiscale_graphcorr"),
    ('table.find_correlation_between("hours", "marks", test_method="spearman")', "spearmanrho"),
    ('table.find_correlation_between("hours", "marks"): Pearson\'s r, the point-biserial one with a 0/1 column',
     "pointbiserialr"),
    ('table.combine_studies(names="gene", p_values="p-value", test_method="fisher") (also "stouffer", "pearson", '
     '"tippett", "mudholkar-george")', "combine_pvalues"),
    ('table.find_summary_of("marks", show=["geometric standard deviation"])', "gstd"),
    ('table.find_summary_of("marks", show=["geometric mean"])', "gmean"),
    ('table.find_summary_of("marks", show=["harmonic mean"])', "hmean"),
    ('table.find_summary_of("marks", show=["power mean 3"])', "pmean"),
    ('table.find_summary_of("marks", show=["interquartile range"])', "iqr"),
    ('table.find_summary_of("marks", show=["median absolute deviation"])', "median_abs_deviation"),
    ('table.find_summary_of("marks", show=["coefficient of variation"])', "variation"),
    ('table.find_summary_of("marks", show=["trimmed average 10"]), or table.keep_rows_where(...) to cut the ends',
     "trim_mean trim1 trimboth"),
    ('table.find_summary_of("marks", show=["cumulant 2"]) (1 to 4)', "kstat"),
    ('table.find_summary_of("marks", show=["cumulant variance 2"]) (1 or 2)', "kstatvar"),
    ('table.find_summary_of("marks", show=["l-moment 2"])', "lmoment"),
    ('table.find_summary_of("marks", show=["central moment 3"])', "moment"),
    ('table.find_summary_of("marks", show=["expectile 90"])', "expectile"),
    ('table.find_summary_of("marks", show=["average between 40 and 80"])', "tmean"),
    ('table.find_summary_of("marks", show=["standard deviation between 40 and 80"])', "tstd"),
    ('table.find_summary_of("marks", show=["variance between 40 and 80"])', "tvar"),
    ('table.find_summary_of("marks", show=["standard error between 40 and 80"])', "tsem"),
    ('table.find_summary_of("marks", show=["smallest from 40"])', "tmin"),
    ('table.find_summary_of("marks", show=["biggest up to 80"])', "tmax"),
    ('table.find_summary_of("wind_direction", show=["circular standard deviation in degrees"]), or '
     'table.find_average_direction_of("wind_direction", full_turn=360)', "circstd"),
    ('table.find_summary_of("wind_direction", show=["circular variance in degrees"]), or '
     'table.find_average_direction_of("wind_direction", full_turn=360)', "circvar"),
    ('table.find_average_direction_of("wind_direction", full_turn=360) (the average direction and its spread)',
     "directional_stats"),
    ('table.find_summary_of("marks", show=["differential entropy"])', "differential_entropy"),
    ('table.find_summary_of("count", show=["entropy"])', "entropy"),
    ('table.find_summary_of("marks", show=["percentile rank 70"]) (the inverse of "percentile 90")', "estimated_cdf"),
    ('table.find_summary_of("marks", show=["percent at or below 70"])', "percentileofscore"),
    ('table.find_summary_of("marks", show=["percentile 90"]), or table.find_percentile_of("marks", 90)',
     "scoreatpercentile"),
    ('table.find_summary_of("marks", show=["sigma-clipped average"])', "sigmaclip"),
    ('table.find_summary_of("marks", show=["average"], in_bins_of={"hours": 2}); two columns or more in in_bins_of= '
     "for 2D bins", "binned_statistic binned_statistic_2d binned_statistic_dd"),
    ('table.find_summary_of("hours", show=["running count"], in_bins_of={"hours": 2})', "cumfreq"),
    ('table.find_summary_of("hours", show=["share of values"], in_bins_of={"hours": 2})', "relfreq"),
    ('table.add_z_score_column("marks_z", from_column="marks"), or on the log of the values for the geometric one',
     "zmap gzscore"),
    ('table.find_best_power_of("days", show="best by normal plot") (SciPy boxcox_normmax\'s default, the '
     "straightest normal plot); show=\"power\" gives the power by maximum likelihood", "boxcox_normmax"),
    ('table.find_best_power_of("days", test_method="yeo-johnson")', "yeojohnson_normmax"),
    ('table.find_best_power_of("days", show="log-likelihood")', "boxcox_llf yeojohnson_llf"),
    ('table.find_best_power_of("days", show="normal plot correlation")', "boxcox_normplot yeojohnson_normplot"),
    ('table.find_best_power_of("days", test_method="tukey lambda") (show="normal plot correlation" for the table)',
     "ppcc_max ppcc_plot"),
    ('chart.draw_qq_dots("marks") (the normal probability plot)', "probplot"),
    ('table.compare_distributions_for("marks", for_each_group_in="class", show="wasserstein distance"); a list of '
     "columns for points", "wasserstein_distance wasserstein_distance_nd"),
    ('table.compare_distributions_for("marks", for_each_group_in="class", show="energy distance")', "energy_distance"),
    ('sdata.find_sensitivity_of("a * x**2 + b", ranges={"a": [0, 1], "b": [0, 5], "x": [0, 2]})', "sobol_indices"),
    ('table.add_group_column("still_alive", rules={\'died == "no"\': "yes"}, otherwise="no"), then '
     'table.fit_distribution_to("days", "weibull", censored_by="still_alive")', "CensoredData"),
    ('sdata.find_chance_of_finding(for_test="compare_averages", effect_size=0.5, values_per_group=30) (the power of a '
     "test)", "power"),
]



def _plain_distribution_pointers():
    """Families for 100 %, batches 5-6 (G3): each SciPy distribution without a family of its own points to its plain
    name, made from the one name table (simplydata._distribution_names.PLAIN)."""
    from ._distribution_names import PLAIN

    out = []
    for scipy_name, (plain, _, shapes) in PLAIN.items():
        names = list(shapes.values())
        counts = scipy_name in ("betabinom", "betanbinom", "boltzmann", "dlaplace", "logser", "nchypergeom_fisher",
                                "nchypergeom_wallenius", "nhypergeom", "planck", "poisson_binom", "skellam",
                                "yulesimon", "zipf", "zipfian")
        names += [] if counts else ["location", "scale"]
        given = ", ".join(f"{n}=..." for n in names)
        out.append((f'sdata.distribution("{plain}"' + (f", {given}" if given else "") + ")", scipy_name))
    return out


_STATS += _plain_distribution_pointers() + [
    # families for 100 %, batches 5-6: joint distributions (G4), made distributions and functions of a distribution
    ('sdata.distribution("multivariate normal", averages=[0, 0], covariance=[[1, 0.5], [0.5, 2]])',
     "multivariate_normal"),
    ('sdata.distribution("multivariate t", location=[0, 0], spread=[[1, 0], [0, 1]], degrees_of_freedom=5)',
     "multivariate_t"),
    ('sdata.distribution("dirichlet", concentrations=[2, 3, 5])', "dirichlet"),
    ('sdata.distribution("multinomial", tries=10, chances=[0.2, 0.3, 0.5])', "multinomial"),
    ('sdata.distribution("multivariate hypergeometric", counts=[5, 3, 2], drawn=4)', "multivariate_hypergeom"),
    ('sdata.distribution("dirichlet multinomial", concentrations=[2, 3, 5], tries=10)', "dirichlet_multinomial"),
    ('sdata.distribution("wishart", degrees_of_freedom=5, scale=[[1, 0], [0, 1]])', "wishart"),
    ('sdata.distribution("inverse wishart", degrees_of_freedom=5, scale=[[1, 0], [0, 1]])', "invwishart"),
    ('sdata.distribution("matrix normal", averages=[[0, 0], [0, 0]], row_covariance=..., column_covariance=...)',
     "matrix_normal"),
    ('sdata.distribution("matrix t", averages=[[0, 0], [0, 0]], row_spread=..., column_spread=..., '
     "degrees_of_freedom=5)", "matrix_t"),
    ('sdata.distribution("von mises-fisher", direction=[0, 0, 1], concentration=10)', "vonmises_fisher"),
    ('sdata.distribution("uniform direction", dimensions=3)', "uniform_direction"),
    ('sdata.distribution("random correlation", eigenvalues=[0.5, 1.5, 1.0])', "random_correlation"),
    ('sdata.distribution("random orthogonal", dimensions=3)', "ortho_group"),
    ('sdata.distribution("random rotation", dimensions=3)', "special_ortho_group"),
    ('sdata.distribution("random unitary", dimensions=3)', "unitary_group"),
    ('sdata.distribution("random table", row_totals=[3, 5], column_totals=[4, 4])', "random_table"),
    ('sdata.distribution("normal inverse gamma", average=0, precision=1, shape=2, scale=1)', "normal_inverse_gamma"),
    ('sdata.distribution("mixture", of=[first, second], shares=[0.3, 0.7])', "Mixture"),
    ('sdata.distribution("from values", values=[1, 2, 5], chances=[0.2, 0.5, 0.3])', "rv_discrete"),
    ('sdata.distribution("histogram", counts=[3, 9, 4], bin_edges=[0, 1, 2, 3])', "rv_histogram"),
    ('sdata.distribution("skew normal", shape=4): every SciPy distribution by its plain name or its SciPy name',
     "make_distribution"),
    ('sdata.distribution("normal", average=50, standard_deviation=10)', "Normal"),
    ('sdata.distribution("binomial", tries=10, chance=0.3)', "Binomial"),
    ('sdata.distribution("lognormal", log_average=0).take_function("log") (also "exp", "absolute value")',
     "log exp abs"),
    ('sdata.distribution("normal").take_function("order statistic", rank=2, out_of=5)', "order_statistic"),
]

# special.<name>: scipy.special (the functions; a formula can use gamma, lgamma, digamma, beta, erf, erfc, besselJ)
_SPECIAL = [
    ("sdata.count_ways_to_choose(3, out_of=10)", "comb binom"),
    ("sdata.count_ways_to_order(3, out_of=10)", "perm"),
    ("sdata.count_ways_to_order(5, out_of=5) for 5! (every order of 5 things)", "factorial"),
    ("numbers.take_log_odds()", "logit"),
    ("numbers.turn_into_chances()", "expit"),
    ('sdata.formula("gamma(x)"), then formula.find_value_at(x=4.5): a formula can use gamma, lgamma, digamma, beta, '
     "erf, erfc and besselJ", "gamma gammaln loggamma digamma psi beta erf erfc"),
    ('sdata.distribution("normal").find_chance_that_value(is_below=1.96)', "ndtr log_ndtr"),
    ('sdata.distribution("normal").find_percentile(97.5)', "ndtri"),
    # families for 100 %, batches 5-6 (approved by Manish 2026-11-28): the distribution functions of scipy.special
    ('sdata.distribution("binomial", tries=10, chance=0.3).find_chance_that_value(is_at_most=3) (is_above= for the '
     "upper tail)", "bdtr bdtrc"),
    ('sdata.distribution("chi-square", degrees_of_freedom=3).find_chance_that_value(is_below=7.8)', "chdtr chdtrc"),
    ('sdata.distribution("F", degrees_of_freedom=[3, 20]).find_chance_that_value(is_below=3.1)', "fdtr fdtrc"),
    ('sdata.distribution("gamma", shape=2, rate=1).find_chance_that_value(is_below=3)', "gdtr gdtrc"),
    ('sdata.distribution("negative binomial", size=3, chance=0.4).find_chance_that_value(is_at_most=2)',
     "nbdtr nbdtrc"),
    ('sdata.distribution("poisson", average=3).find_chance_that_value(is_at_most=2)', "pdtr pdtrc"),
    ('sdata.distribution("t", degrees_of_freedom=5).find_chance_that_value(is_below=2.0)', "stdtr"),
    ('sdata.distribution("noncentral chi-square", degrees_of_freedom=3, noncentrality=2).find_chance_that_value('
     "is_below=5)", "chndtr"),
    ('sdata.distribution("noncentral F", degrees_of_freedom_1=3, degrees_of_freedom_2=20, noncentrality=2)'
     ".find_chance_that_value(is_below=3)", "ncfdtr"),
    ('sdata.distribution("noncentral t", degrees_of_freedom=5, noncentrality=1).find_chance_that_value(is_below=2)',
     "nctdtr"),
    ('sdata.distribution("chi-square", degrees_of_freedom=3).find_percentile(95)', "chdtri"),
    ('sdata.distribution("F", degrees_of_freedom=[3, 20]).find_percentile(95)', "fdtri"),
    ('sdata.distribution("gamma", shape=2, rate=1).find_percentile(95)', "gdtrix"),
    ('sdata.distribution("t", degrees_of_freedom=5).find_percentile(97.5)', "stdtrit"),
    ('sdata.distribution("noncentral chi-square", degrees_of_freedom=3, noncentrality=2).find_percentile(95)',
     "chndtrix"),
    ('sdata.distribution("noncentral F", degrees_of_freedom_1=3, degrees_of_freedom_2=20, noncentrality=2)'
     ".find_percentile(95)", "ncfdtri"),
    ('sdata.distribution("noncentral t", degrees_of_freedom=5, noncentrality=1).find_percentile(95)', "nctdtrit"),
    ('sdata.distribution("binomial", tries=10, chance=0.3).find_percentile(50), the whole count (as R qbinom)',
     "bdtrik"),
    ('sdata.distribution("negative binomial", size=3, chance=0.4).find_percentile(50), the whole count',
     "nbdtrik"),
    ('sdata.distribution("poisson", average=3).find_percentile(50), the whole count (as R qpois)', "pdtrik"),
    ('sdata.distribution("normal").find_percentile(97.5), for a chance given as its log: the percentile of '
     "exp(log chance)", "ndtri_exp"),
    ('sdata.distribution("kolmogorov-smirnov limit").find_chance_that_value(is_above=1.36)', "kolmogorov"),
    ('sdata.distribution("kolmogorov-smirnov limit").find_cut_off(with_chance_above=0.05)', "kolmogi"),
    ('sdata.distribution("kolmogorov-smirnov one-sided", sample_size=20).find_chance_that_value(is_above=0.25)',
     "smirnov"),
    ('sdata.distribution("kolmogorov-smirnov one-sided", sample_size=20).find_cut_off(with_chance_above=0.05)',
     "smirnovi"),
    ('sdata.distribution("skew normal", shape=2).find_chance_that_value(is_below=1): its chance below is the normal\'s '
     "minus 2 x Owen's T", "owens_t"),
    ('sdata.distribution("tukey lambda", shape=0.14).find_chance_that_value(is_below=1)', "tklmbda"),
    ('sdata.find_parameter_that_gives("t", chance_below=0.975, at_value=2.1) (the missing parameter of t, '
     "chi-square, F, gamma, beta, binomial, negative binomial, poisson, normal and the noncentral ones)",
     "stdtridf chdtriv fdtridfd gdtria gdtrib btdtria btdtrib bdtri bdtrin nbdtri nbdtrin pdtri nrdtrimn nrdtrisd "
     "chndtridf chndtrinc ncfdtridfd ncfdtridfn ncfdtrinc nctdtridf nctdtrinc"),
    # families for 100 %, batch 13 (G5, approved by Manish 2026-11-28): the polynomials, as formulas
    ('sdata.polynomial("legendre", degree=3)', "legendre"),
    ('sdata.polynomial("shifted legendre", degree=3)', "sh_legendre"),
    ('sdata.polynomial("chebyshev", degree=3)', "chebyt"),
    ('sdata.polynomial("chebyshev second kind", degree=3)', "chebyu"),
    ('sdata.polynomial("shifted chebyshev", degree=3) ("shifted chebyshev second kind" for sh_chebyu)',
     "sh_chebyt sh_chebyu"),
    ('sdata.polynomial("chebyshev c", degree=3) ("chebyshev s" for chebys)', "chebyc chebys"),
    ('sdata.polynomial("hermite", degree=3)', "hermite"),
    ('sdata.polynomial("probabilists hermite", degree=3)', "hermitenorm"),
    ('sdata.polynomial("laguerre", degree=3)', "laguerre"),
    ('sdata.polynomial("generalized laguerre", degree=3, alpha=1)', "genlaguerre"),
    ('sdata.polynomial("jacobi", degree=3, alpha=1, beta=2)', "jacobi"),
    ('sdata.polynomial("gegenbauer", degree=3, alpha=1)', "gegenbauer"),
    ('sdata.polynomial("jacobi", degree=3, alpha=..., beta=...) (SciPy sh_jacobi is a shifted and scaled Jacobi '
     "polynomial; formula.put_in(x=\"2*x - 1\") shifts it)", "sh_jacobi"),
]

# scipy.<name>, optimize., integrate., interpolate., signal., ndimage. and spatial.: names whose word the sdata,
# numbers, table and block lists do not already give
# families for 100 %, batches 17-18: the signal jobs left to SciPy (2-D filters belong to grids as images, plan 2.9;
# the others are SciPy's helpers and checks)
_SIGNAL_HAND_OVER = ("numbers.as_numpy() hands the numbers to NumPy (a grid too: grid.as_numpy()), where the SciPy "
                     "signal call works")
_SCIPY = [
    ("numbers.find_envelope()", "envelope"),
    ('sdata.system("1 / (s**2 + 2*s + 5)"), then system.step_response() (impulse_response, response_to and '
     "frequency_response for the others)", "step impulse lsim bode freqresp dstep dimpulse dlsim dbode"),
    ("grid.solve_for([4, 1, 2, 5], between=[0, None]) for answers of 0 or above, on a grid of 4 rows",
     "nnls lsqnonneg"),
    ("grid.solve_for([4, 1, 2, 5], between=[0, 1]) for answers between limits, on a grid of 4 rows", "lsq_linear"),
    ("numbers.find_each_peak_that(is_at_least=1)", "find_peaks find_peaks_cwt argrelextrema"),
    ("numbers.find_spectrum(time_step=0.01)", "periodogram welch spectrogram"),
    ("numbers.convolve_with([1, 2, 1])", "fftconvolve oaconvolve"),
    ('numbers.turn_into_running_area(time_step=60, test_method="simpson"), whose last number is the whole area',
     "simpson trapezoid"),
    ("grid.find_each_patch_that(is_above=0.5)", "label sum_labels center_of_mass find_objects"),
    ("grid.rotate(by_degrees=15)", "rotate"),
    ("grid.change_size_to(rows=10, columns=10)", "zoom"),
    ('table.find_distances_to_rows_of(other, using=["east", "north"])', "distance_matrix"),
    ("grid.take_matrix_exp()", "expm"),
    ("grid.find_null_space()", "null_space"),
    # families for 100 %, batches 17-18 (plan 2.7, approved by Manish 2026-11-28): scipy.signal's filter design,
    # system forms, spectra over time, FIR filters and the other signal tools
    ('sdata.frequency_filter(keep_below=10, time_step=0.005, find_order_for={"loss_at": 20}): the smallest steepness '
     "for the losses asked (SciPy buttord, cheb1ord, cheb2ord or ellipord, by test_method=; band_stop_obj is their "
     "helper for a band removed)", "buttord cheb1ord cheb2ord ellipord band_stop_obj"),
    ('sdata.frequency_filter(keep_below=10, time_step=0.005, test_method="fir", find_order_for={"loss_at": 20}): the '
     "number of weights and the Kaiser window (SciPy kaiserord, which uses kaiser_beta)", "kaiserord kaiser_beta"),
    ('sdata.frequency_filter(keep_below=10, time_step=0.005, test_method="fir", how_many_weights=31), then '
     "system.frequency_response() shows how much the filter removes at each frequency", "kaiser_atten"),
    ("sdata.frequency_filter(keep_between=[1, 5], analog=True): the analog (continuous) filter, which SciPy makes from "
     "its prototype (buttap, cheb1ap, cheb2ap, ellipap, besselap) moved to the cutoff (lp2lp, lp2hp, lp2bp, lp2bs)",
     "buttap cheb1ap cheb2ap ellipap besselap lp2lp lp2hp lp2bp lp2bs lp2lp_zpk lp2hp_zpk lp2bp_zpk lp2bs_zpk"),
    ('sdata.system("1 / (s + 1)"), then system.in_steps(time_step=0.1, test_method="bilinear") (SciPy cont2discrete '
     "with the bilinear transform)", "bilinear bilinear_zpk"),
    ('sdata.system("1 / (s + 1)"), then system.in_steps(time_step=0.1) (SciPy cont2discrete; zero order hold unless '
     "test_method= says otherwise)", "cont2discrete"),
    ('sdata.system("1 / (s**2 + 2*s + 5)"), then system.table(form="state space") (SciPy tf2ss)', "tf2ss"),
    ("sdata.system(a=[[0, 1], [-5, -2]], b=[[0], [1]], c=[[1, 0]]) (SciPy ss2tf; d= is 0 when left out, and the "
     "matrices are checked to fit)", "ss2tf abcd_normalize"),
    ('sdata.system(a=[[0, 1], [-5, -2]], b=[[0], [1]], c=[[1, 0]]), then system.table(form="poles and zeros")',
     "ss2zpk"),
    ('sdata.system("1 / (s**2 + 2*s + 5)"), then system.table(form="poles and zeros") (SciPy tf2zpk)', "tf2zpk"),
    ("sdata.system(poles=[-1, -2], zeros=[0], gain=2) (SciPy zpk2tf)", "zpk2tf"),
    ('sdata.system(poles=[-1, -2], zeros=[0], gain=2), then system.table(form="state space")', "zpk2ss"),
    ('sdata.frequency_filter(keep_below=10, time_step=0.005), then system.table(form="sections") (for any system: '
     "SciPy tf2sos)", "tf2sos zpk2sos"),
    ("sdata.system(sections=[[1, 2, 1, 1, -0.5, 0.1]], time_step=0.01) (SciPy sos2tf), then "
     'system.table(form="poles and zeros") for the poles and zeros', "sos2tf sos2zpk"),
    ("sdata.system(numerator=[2, 4], denominator=[2, 4, 10]): the formula is written with the first number of the "
     "bottom 1 (SciPy normalize)", "normalize"),
    ('sdata.system("(s + 1) / (s**2 + 3*s + 2)"), then system.table(form="partial fractions") (SciPy residue; '
     "residuez for a system in steps)", "residue residuez"),
    ("sdata.system(residues=[0, 1], poles=[-1, -2]) (SciPy invres; invresz with time_step=)", "invres invresz"),
    ('sdata.system("1 / (s**2 + 2*s + 5)"), then system.move_poles_to([-2, -3]) (SciPy place_poles)', "place_poles"),
    ('sdata.system("1 / (s**2 + 2*s + 5)"), then system.frequency_response() (SciPy freqresp; freqz or sosfreqz in '
     "steps; findfreqs picks the frequencies when between= is left out)",
     "freqs freqs_zpk freqz_zpk freqz_sos dfreqresp findfreqs"),
    ("sdata.frequency_filter(keep_below=10, time_step=0.005), then system.frequency_response(with_delay=True) (SciPy "
     "group_delay)", "group_delay"),
    ("numbers.take_fourier_transform(time_step=0.01, over_time=True) (SciPy ShortTimeFFT.stft; "
     "sdata.find_inverse_fourier_transform(table) gives the numbers back with ShortTimeFFT.istft)",
     "stft ShortTimeFFT"),
    ("sdata.find_inverse_fourier_transform(table) on the table of numbers.take_fourier_transform(time_step=0.01, "
     "over_time=True) (SciPy ShortTimeFFT.istft, which checks the pieces overlap enough to come back: check_NOLA)",
     "istft check_NOLA"),
    ("numbers.take_fourier_transform(time_step=0.01, between=[2, 6], how_many=50) (SciPy zoom_fft: the chirp "
     "z-transform on the unit circle; other spirals are left to SciPy czt after numbers.as_numpy())",
     "zoom_fft ZoomFFT czt CZT czt_points"),
    ('numbers.keep_each_frequency_that(is_below=2, time_step=0.05, test_method="fir", both_ways=False) (SciPy '
     "firwin)", "firwin"),
    ('numbers.keep_each_frequency_that(is_below=2, time_step=0.05, test_method="fir least squares", '
     "transition_width=2, both_ways=False) (SciPy firls)", "firls"),
    ('numbers.keep_each_frequency_that(is_below=2, time_step=0.05, test_method="fir equiripple", '
     "transition_width=2, both_ways=False) (SciPy remez)", "remez"),
    ('numbers.keep_each_frequency_that(is_below=2, time_step=0.05, test_method="fir frequency sampling", '
     "both_ways=False) (SciPy firwin2)", "firwin2"),
    ('numbers.keep_each_frequency_that(is_below=2, time_step=0.05, test_method="fir", both_ways=False, '
     "with_least_delay=True) (SciPy minimum_phase)", "minimum_phase"),
    ('numbers.keep_each_frequency_that(is_equal_to=2, time_step=0.05, test_method="gammatone", both_ways=False) '
     "(SciPy gammatone)", "gammatone"),
    ('numbers.smooth(test_method="savitzky-golay", window=11, of_degree=2) (SciPy savgol_filter, which uses '
     "savgol_coeffs)", "savgol_coeffs"),
    ('numbers.keep_each_frequency_that(is_below=0.2, time_step=1, both_ways=False, start_from="first value") (SciPy '
     "sosfilt_zi; lfilter_zi for FIR filters): the filter starts in its steady state", "lfilter_zi sosfilt_zi"),
    ('numbers.keep_each_frequency_that(is_below=0.2, time_step=1, both_ways=False, start_from="first value") is '
     "related, not the same: it starts the filter in its steady state for the first reading, while SciPy lfiltic "
     "builds the start from earlier inputs and outputs you give (left to SciPy after numbers.as_numpy())", "lfiltic"),
    ('sdata.make_wave("maximum length sequence", time_step=0.01, how_many=127) (SciPy max_len_seq)', "max_len_seq"),
    ('sdata.make_wave("chirp", sweep="polynomial", frequency=[2, 1], time_step=0.01, how_many=500) (SciPy sweep_poly)',
     "sweep_poly"),
    ('numbers.change_time_step(to=0.5, time_step=1, test_method="polyphase") (SciPy resample_poly, which runs '
     "upfirdn)", "upfirdn"),
    ('numbers.change_time_step(to=0.5, time_step=1, test_method="cubic spline") (SciPy cspline1d and '
     'cspline1d_eval; test_method="quadratic spline" for qspline1d)',
     "cspline1d cspline1d_eval qspline1d qspline1d_eval"),
    ("numbers.find_phase_locking_to(period=0.1), the numbers being the times of the events (SciPy vectorstrength)",
     "vectorstrength"),
    ("numbers.convolve_with([1, 2, 1]) (SciPy convolve chooses the fastest way itself: choose_conv_method)",
     "choose_conv_method"),
    ('grid.smooth(test_method="median", window=3) (SciPy ndimage.median_filter; signal.medfilt2d pads the edges with '
     "zeros instead)", "medfilt2d"),
    # cspline2d, qspline2d, spline_filter, sepfir2d, order_filter, hilbert2, correlate2d and firwin_2d: grid words
    # since batches 20-21 (below)
    (_SIGNAL_HAND_OVER, "BadCoefficients check_COLA closest_STFT_dual_window gauss_spline symiirorder1 symiirorder2 "
                        "correlation_lags unique_roots"),
]

# families for 100 %, batches 14-16 (approved by Manish 2026-11-28): the names of scipy.optimize, integrate and
# interpolate (plan section 2.6); newton_cotes and lebedev_rule are sdata.find_area_points (batch 9)
_SCIPY += [
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], search="whole range", test_method="basin '
     'hopping")',
     'basinhopping'),
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], search="whole range", '
     'test_method="differential evolution")',
     'differential_evolution'),
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], search="whole range", '
     'test_method="direct")',
     'direct'),
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], search="whole range", test_method="dual '
     'annealing")',
     'dual_annealing'),
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], search="whole range", test_method="shgo")',
     'shgo'),
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], search="whole range", test_method="grid '
     'search")',
     'brute'),
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], test_method="golden section")',
     'golden'),
    ('sdata.find_where_smallest("(x - 2)**2 + sin(5*x)", between=[0, 5], test_method="brent")',
     'brent'),
    ('sdata.find_where_smallest("(x - 2)**2", start=0): from a start, the search first finds a bracket around the '
     'dip, then searches along it (SciPy bracket, and the line searches inside minimize)',
     'bracket line_search'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, '
     'test_method="nelder-mead")',
     'fmin'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, test_method="bfgs"): '
     "BFGS and SR1 are the updates of the slopes inside SciPy's quasi-Newton and trust-region methods "
     '(test_method="trust region")',
     'fmin_bfgs BFGS SR1 LbfgsInvHessProduct'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, test_method="conjugate '
     'gradient")',
     'fmin_cg'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, test_method="cobyla")',
     'fmin_cobyla'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, '
     'test_method="l-bfgs-b")',
     'fmin_l_bfgs_b'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, test_method="newton '
     'conjugate gradient")',
     'fmin_ncg'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, test_method="powell")',
     'fmin_powell'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, test_method="slsqp")',
     'fmin_slsqp'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}, test_method="truncated '
     'newton")',
     'fmin_tnc'),
    ('sdata.find_where_smallest("x**2 + y**2", start={"x": 1, "y": 1}, between={"x": [0.5, 2], "y": [-1, 1]}): '
     'between= gives the limits of each name (SciPy Bounds)',
     'Bounds'),
    ('sdata.find_where_smallest("2*x + 3*y", rules=["x + y >= 4", "x >= 0", "y >= 0"]): rules= are the constraints, '
     'straight-line or not (SciPy LinearConstraint, NonlinearConstraint)',
     'LinearConstraint NonlinearConstraint'),
    ('sdata.find_where_smallest("(1 - x)**2 + 100*(y - x**2)**2", start={"x": -1.2, "y": 1}): the Rosenbrock test '
     'function written as a formula; formula.find_slope_formula() gives its slopes',
     'rosen rosen_der rosen_hess rosen_hess_prod'),
    ('sdata.formula("x**3 - 2*x"), then formula.find_slope_formula().find_value_at(x=2): the exact slope, which '
     'approx_fprime estimates by differences and check_grad compares with yours',
     'approx_fprime check_grad'),
    ('sdata.solve("x**3 - 2*x = 5", between=[0, 3]): the sentence says whether the search settled (converged) and '
     'how many times the equations were worked out',
     'NoConvergence RootResults'),
    ('sdata.solve("x**3 - 2*x = 5", between=[0, 3], test_method="ridder")',
     'ridder'),
    ('sdata.solve("x**3 - 2*x = 5", between=[0, 3], test_method="toms748")',
     'toms748'),
    ('sdata.solve("x = cos(x)", start=1, test_method="fixed point")',
     'fixed_point'),
    ('sdata.solve(["x = 0.5*cos(y)", "y = 0.5*sin(x)"], start={"x": 0, "y": 0}, test_method="broyden") '
     '(BroydenFirst and InverseJacobian are its parts inside SciPy)',
     'broyden1 BroydenFirst InverseJacobian'),
    ('sdata.solve(["x = 0.5*cos(y)", "y = 0.5*sin(x)"], start={"x": 0, "y": 0}, test_method="broyden second")',
     'broyden2'),
    ('sdata.solve(["x = 0.5*cos(y)", "y = 0.5*sin(x)"], start={"x": 0, "y": 0}, test_method="diagonal broyden")',
     'diagbroyden'),
    ('sdata.solve(["x = 0.5*cos(y)", "y = 0.5*sin(x)"], start={"x": 0, "y": 0}, test_method="linear mixing")',
     'linearmixing'),
    ('sdata.solve(["x = 0.5*cos(y)", "y = 0.5*sin(x)"], start={"x": 0, "y": 0}, test_method="exciting mixing")',
     'excitingmixing'),
    ('sdata.solve(["x = 0.5*cos(y)", "y = 0.5*sin(x)"], start={"x": 0, "y": 0}, test_method="newton-krylov") '
     '(KrylovJacobian is its part inside SciPy)',
     'newton_krylov KrylovJacobian'),
    ('table.fit_curve(x="hours", y="marks", always="rising"), on a table',
     'isotonic_regression'),
    ('sdata.find_best_pairing(sdata.number_grid([[4, 1, 3], [2, 0, 5], [3, 2, 2]]))',
     'linear_sum_assignment'),
    ('sdata.find_best_pairing(flows, with_distances=distances), with two square grids',
     'quadratic_assignment'),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3}, '
     'test_method="RK45")',
     'RK45'),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3}, '
     'test_method="RK23")',
     'RK23'),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3}, '
     'test_method="DOP853")',
     'DOP853'),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3}, '
     'test_method="stiff") (Radau)',
     'Radau'),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3}, '
     'test_method="BDF")',
     'BDF'),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3}, '
     "time_step=0.5): the table holds the path at even times, from the solver's own dense output",
     'DenseOutput OdeSolution OdeSolver'),
    ('sdata.find_path_over_time(["du/dt = -v", "dv/dt = u"], at_start={"u": 1, "v": 0}, between=[0, 5]): the real '
     'and imaginary parts of a complex equation as two equations',
     'complex_ode'),
    ('sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="tanh-sinh")',
     'tanhsinh'),
    ('sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], test_method="cubature"), or '
     'sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]}, test_method="cubature")',
     'cubature'),
    ('sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="quasi monte carlo")',
     'qmc_quad'),
    ('sdata.find_area_under("exp(-x**2)", between=[0, 2], test_method="romberg on even steps")',
     'romb'),
    ('sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5])',
     'solve_bvp'),
    ('table.find_values_at("population", at={"year": [2001, 2003]}, joined_by="aaa"), on a table',
     'AAA'),
    ('table.find_values_at("population", at={"year": [2001, 2003]}, joined_by="akima"), on a table',
     'Akima1DInterpolator'),
    ('table.find_values_at("population", at={"year": [2001, 2003]}, joined_by="polynomial"), on a table',
     'BarycentricInterpolator barycentric_interpolate KroghInterpolator krogh_interpolate lagrange'),
    ('table.find_values_at("population", at={"year": [2001, 2003]}, joined_by="rational curve"), on a table',
     'FloaterHormannInterpolator'),
    ('table.find_values_at("population", at={"year": [2001, 2003]}, joined_by="curve without overshoot"), on a '
     'table',
     'pchip_interpolate'),
    ('table.find_values_at("population", at={"year": [2001, 2003]}, smoothness=0.001), on a table',
     'make_smoothing_spline'),
    ('table.find_values_at("height", at={"east": [1.5, 2.5], "north": [3, 4.5]}, joined_by="smooth triangles"), on '
     'a table',
     'CloughTocher2DInterpolator'),
    ('table.find_values_at("height", at={"east": [1.5, 2.5], "north": [3, 4.5]}), on a table (flat triangles '
     'between scattered points)',
     'LinearNDInterpolator'),
    ('table.find_values_at("height", at={"east": [1.5, 2.5], "north": [3, 4.5]}, joined_by="nearest"), on a table',
     'NearestNDInterpolator'),
    ('table.find_values_at("height", at={"east": [1.5, 2.5], "north": [3, 4.5]}, joined_by="smooth surface"), on a '
     "table (SciPy's newer RBFInterpolator)",
     'Rbf'),
    ('sdata.formula("exp(x)"), then formula.find_taylor_series(around=0, up_to_power=4): the Taylor polynomial, '
     'exact (approximate_taylor_polynomial estimates it; pade turns it into a fraction, with formula.as_sympy())',
     'approximate_taylor_polynomial pade'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), the cubic spline through every point (a '
     'BSpline; curve.as_scipy() hands it over)',
     'BSpline InterpolatedUnivariateSpline'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.show_pieces(): its '
     'polynomial pieces (PPoly), or show_pieces(basis="bernstein") (BPoly)',
     'PPoly BPoly'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.show_knots(): its knots and '
     'coefficients',
     'splrep'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.find_value_at(12)',
     'splev'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.find_slope_at(12) '
     '(order="all" gives every slope at one place)',
     'spalde'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.turn_into_slope_curve()',
     'splder'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.turn_into_area_curve()',
     'splantider'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.find_area_between(0, 20)',
     'splint'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0]), then curve.find_zeros()',
     'sproot'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20, 30], y=[8.1, 7.9, 6.2, 5.0, 4.4], allowed_error=0.5): the fewest '
     'knots that keep the sum of squared distances at most 0.5 (FITPACK s)',
     'UnivariateSpline make_splrep generate_knots'),
    ('sdata.curve_through_points(x=[0, 5, 10, 20, 30], y=[8.1, 7.9, 6.2, 5.0, 4.4], knots=[15]): least squares with '
     'those inner knots',
     'LSQUnivariateSpline make_lsq_spline'),
    ('sdata.curve_through_points(x=[0, 5, 10], y=[8.1, 7.9, 6.2], slopes=[0, -0.2, -0.3])',
     'CubicHermiteSpline'),
    ('sdata.curve_through_points(x=[0, 1, 2, 1], y=[0, 1, 0, -1], in_order=True): a path through the points in '
     'their order',
     'splprep make_splprep'),
    ('sdata.curve_through_points(x=east, y=north, z=height): a surface (RectBivariateSpline on a full grid, '
     'SmoothBivariateSpline for scattered points, LSQBivariateSpline with knots=)',
     'BivariateSpline RectBivariateSpline SmoothBivariateSpline LSQBivariateSpline bisplrep bisplev'),
    ('sdata.curve_through_points(x=latitude, y=longitude, z=values, on_sphere=True): a surface on a sphere',
     'RectSphereBivariateSpline SmoothSphereBivariateSpline LSQSphereBivariateSpline'),
    ('sdata.curve_through_points(x=east, y=north, z=height) for two directions; for three or more, grid.as_numpy() '
     'hands the numbers to SciPy NdBSpline',
     'NdBSpline NdPPoly'),
]

# families for 100 %, batches 20-21 (approved by Manish 2026-11-28, plan section 2.9, G9): the names of
# scipy.ndimage and scipy.spatial, and scipy.signal's 2-D names
_SCIPY += [
    ('grid.smooth(test_method="biggest", window=3) (along one direction with over="row": maximum_filter1d)',
     "maximum_filter maximum_filter1d"),
    ('grid.smooth(test_method="smallest", window=3) (along one direction with over="row": minimum_filter1d)',
     "minimum_filter minimum_filter1d"),
    ('grid.smooth(test_method="percentile", percentile=90, window=3)', "percentile_filter"),
    ('grid.smooth(test_method="rank", rank=2, window=3)', "rank_filter"),
    ('grid.smooth(test_method="rank", rank=2, window=3, ends="zeros"): the cells outside count as 0',
     "order_filter"),
    ('grid.smooth(test_method="summary", summary="range", window=3): any NumPy summary of each window',
     "generic_filter generic_filter1d vectorized_filter"),
    ('grid.smooth(over="row", window=3): the moving average along one direction', "uniform_filter1d"),
    ('grid.smooth(test_method="fourier gaussian", width=2)', "fourier_gaussian"),
    ('grid.smooth(test_method="fourier uniform", window=3)', "fourier_uniform"),
    ('grid.smooth(test_method="fourier ellipsoid", window=3)', "fourier_ellipsoid"),
    ('grid.smooth(test_method="spline", smoothness=5) for signal.spline_filter, on a big grid such as '
     "sdata.number_grid(rows=30, columns=30, filled_with=1); ndimage.spline_filter is the prefilter inside "
     'grid.change_size_to(rows=6, columns=6, test_method="cubic")', "spline_filter spline_filter1d"),
    ('grid.smooth(test_method="spline", smoothness=5), on a big grid such as sdata.number_grid(rows=30, columns=30, '
     "filled_with=1): the cubic spline coefficients (cspline2d; qspline2d for quadratic ones) are worked out inside "
     "it", "cspline2d qspline2d"),
    ("numbers.convolve_with(other.reverse()): a correlation is a convolution with the weights turned round (on a "
     "grid, grid.convolve_with(kernel, flip=False))", "correlate1d"),
    ("grid.convolve_with([[0, 1, 0], [1, 4, 1], [0, 1, 0]])", "convolve2d"),
    ("grid.convolve_with([[1, 2], [0, -1]], flip=False): the weights slide without turning round", "correlate2d"),
    ("grid.convolve_with(row_weights=[1, 2, 1], column_weights=[1, 2, 1])", "sepfir2d"),
    ("grid.convolve_with(other), with the kernel other designed by SciPy signal.firwin_2d and made a grid with "
     "sdata.number_grid", "firwin_2d"),
    ("grid.find_envelope()", "hilbert2"),
    ('grid.move_and_stretch_by(shift=[0.5, 1], test_method="fourier")', "fourier_shift"),
    ('grid.find_edges(test_method="sobel")', "sobel generic_gradient_magnitude"),
    ('grid.find_edges(test_method="prewitt")', "prewitt"),
    ('grid.find_edges(test_method="laplace")', "laplace generic_laplace"),
    ('grid.find_edges(test_method="gaussian laplace")', "gaussian_laplace"),
    ('grid.find_edges(test_method="gaussian gradient")', "gaussian_gradient_magnitude"),
    ('grid.change_patch_shapes("grow", by=1) (patches: binary_dilation; numbers: grey_dilation)',
     "binary_dilation grey_dilation"),
    ('grid.change_patch_shapes("shrink", by=1)', "binary_erosion grey_erosion"),
    ('grid.change_patch_shapes("open", by=1)', "binary_opening grey_opening"),
    ('grid.change_patch_shapes("close", by=1)', "binary_closing grey_closing"),
    ('grid.change_patch_shapes("fill holes", is_above=0)', "binary_fill_holes"),
    ('grid.change_patch_shapes("top hat", by=1)', "white_tophat"),
    ('grid.change_patch_shapes("dark top hat", by=1)', "black_tophat"),
    ('grid.change_patch_shapes("outline", by=1)', "morphological_gradient"),
    ('grid.change_patch_shapes("laplace", by=1)', "morphological_laplace"),
    ('grid.change_patch_shapes("match pattern", is_above=0, pattern=[[1, 1], [1, 0]])', "binary_hit_or_miss"),
    ('grid.change_patch_shapes("keep patches with points", is_above=0, starting_points=[[1, 1]])',
     "binary_propagation"),
    ('grid.change_patch_shapes("grow", by=2): by= grows the neighbourhood (iterate_structure)', "iterate_structure"),
    ('grid.find_each_patch_that(is_above=0.5, touching="corners"): touching= gives the neighbours '
     "(generate_binary_structure)", "generate_binary_structure"),
    ('grid.find_each_patch_that(is_above=0.5, show=["biggest", "smallest", "where biggest", "where smallest"])',
     "extrema"),
    ('grid.find_each_patch_that(is_above=0.5, show="where biggest")', "maximum_position"),
    ('grid.find_each_patch_that(is_above=0.5, show="where smallest")', "minimum_position"),
    ('grid.find_each_patch_that(is_above=0.5, show="variance")', "variance"),
    ('grid.find_each_patch_that(is_above=0.5, show="standard deviation")', "standard_deviation"),
    ('grid.find_each_patch_that(is_above=0.5, show="counts in bins", bins=4)', "histogram"),
    ('grid.find_each_patch_that(is_above=0.5, show="positions")', "value_indices"),
    ('grid.find_each_patch_that(is_above=0.5, show="range"): any summary of each patch',
     "labeled_comprehension"),
    ("grid.find_distance_to_nearest(is_above=0.5)", "distance_transform_edt"),
    ('grid.find_distance_to_nearest(is_above=0.5, test_method="city block") ("chessboard" too)',
     "distance_transform_cdt"),
    ('grid.find_distance_to_nearest(is_above=0.5, test_method="brute force")', "distance_transform_bf"),
    ("grid.split_touching_patches(starting_points=[[1, 1], [2, 2]])", "watershed_ift"),
    ("grid.move_and_stretch_by(matrix=[[1, 0.5], [0, 1]])", "affine_transform"),
    ('grid.move_and_stretch_by(formulas={"row": "row", "column": "column + 0.5*row"})', "geometric_transform"),
    ('table.find_triangles_between_points(x="east", y="north"), on a table', "Delaunay"),
    ('table.find_triangles_between_points(x="east", y="north", containing={"east": [4000], "north": [1000]}), on a '
     "table", "tsearch"),
    ('table.find_regions_around_points(x="east", y="north"), on a table', "Voronoi"),
    ("table.find_regions_around_points(longitude=longitude_column, latitude=latitude_column), on a table of places "
     "spread over the earth", "SphericalVoronoi"),
    ('table.find_distances_between_rows(columns=["east", "north"], measure="minkowski", power=3), on a table '
     "(minkowski_distance_p is the same before the last root)", "minkowski_distance minkowski_distance_p"),
    ('table.find_fence_around(x="east", y="north") gives the corners to draw (matplotlib, as convex_hull_plot_2d)',
     "convex_hull_plot_2d"),
    ('table.find_triangles_between_points(x="east", y="north") gives the triangles to draw (matplotlib, as '
     "delaunay_plot_2d)", "delaunay_plot_2d"),
    ('table.find_regions_around_points(x="east", y="north") gives the regions to draw (matplotlib, as '
     "voronoi_plot_2d)", "voronoi_plot_2d"),
    # not user jobs (d): KDTree's boxes, and a path on a sphere
    ('table.find_nearest_rows_to({"east": 4000, "north": 1000}, how_many=3): the boxes of the tree (Rectangle) '
     "stay inside SciPy", "Rectangle"),
    (_NUMPY_HAND_OVER + ": scipy.spatial.geometric_slerp(start, end, numbers.as_numpy()), the points along a great "
     "circle", "geometric_slerp"),
]

# sp.<name> and sympy.<name>: SymPy's top level (and Matrix methods such as Matrix.det)
_SYMPY = [
    ('grid.break_down(test_method="jordan") (families for 100 %, batch 19)', "jordan_form"),
    ('sdata.solve("x**2 = 2", exactly=True)', "solve solveset linsolve nonlinsolve roots"),
    ('sdata.solve("x**3 - 2*x = 5", between=[0, 3]) (in decimals, as SymPy nsolve)', "nsolve"),
    ('sdata.formula("(x + 2)**2 - 4")', "symbols Symbol sympify parse_expr S Eq Function"),
    ('sdata.formula("sqrt(2) * sin(x) + exp(-x)"): SymPy functions are written inside the formula text '
     "(exp, log, sqrt, abs, sin, cos, tan, arcsin, arccos, arctan, erf, erfc, gamma, beta, besselJ, sinc)",
     "sqrt sin cos tan exp log asin acos atan atan2 erf erfc Abs sinc besselj loggamma pi E oo"),
    ('sdata.formula("x**3 - 2*x"), then formula.find_slope_formula()', "diff Derivative idiff"),
    ('sdata.formula("x**3 - 2*x"), then formula.find_area_formula()', "integrate Integral"),
    ('sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], exactly=True)', "quad"),
    ('sdata.formula("x**3 - 2*x"), then formula.find_value_at(x=2)', "subs evalf N lambdify"),
    ('sdata.formula("(x + 2)**2 - 4"), then formula.make_simpler()', "simplify nsimplify trigsimp radsimp cancel"),
    ('sdata.formula("(x + 2)**2 - 4"), then formula.turn_into_sum()', "expand expand_trig"),
    ('sdata.formula("x**2 - 4"), then formula.turn_into_product()', "factor"),
    ('sdata.formula("(3*x + 5) / ((x + 1)*(x + 2))"), then formula.turn_into_partial_fractions()', "apart"),
    ('sdata.formula("a*x**2 + b*x**2 + a*x - x"), then formula.group_by_powers_of("x")', "collect"),
    ('sdata.formula("sin(x) / x"), then formula.find_limit_as("x", goes_to=0)', "limit Limit"),
    ('sdata.formula("sin(x)"), then formula.find_taylor_series(around=0)', "series taylor"),
    ('sdata.formula("x**3 - 2*x"), then formula.show_as_latex()', "latex pprint pretty"),
    ('sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])', "summation Sum"),
    ('sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 50], known={"r": 0.3}, '
     "exactly=True)", "dsolve"),
    ('sdata.find_where_smallest("x**2 - 4*x + 1", between=[0, 5])', "minimum"),
    ('sdata.find_where_biggest("x * (10 - x)", between=[0, 10])', "maximum"),
    ("sdata.number_grid([[2, 1], [1, 2]])", "Matrix ImmutableMatrix"),
    ("grid.find_determinant(exactly=True)", "det"),
    ("grid.take_inverse(exactly=True)", "inv"),
    ("grid.find_eigenvalues(exactly=True)", "eigenvals"),
    ("grid.find_null_space(exactly=True)", "nullspace"),
    ("grid.solve_for([5, 10], exactly=True), on a grid of 2 rows", "LUsolve solve_least_squares"),
    ("numbers.show_as_fraction()", "Rational"),
    ('sdata.formula("sqrt(k**2)", letters_are={"k": "positive"})', "assumptions refine Q"),
    ("formula.as_sympy() hands the formula to SymPy, where the SymPy call works (factorint finds the prime factors "
     "of a whole number)", "srepr factorint"),
    # families for 100 %, batches 11 and 13 (approved by Manish 2026-11-28, plan section 2.4)
    ('sdata.polynomial("legendre", degree=3)', "legendre_poly legendre"),
    ('sdata.polynomial("chebyshev", degree=3)', "chebyshevt_poly chebyshevt"),
    ('sdata.polynomial("chebyshev second kind", degree=3)', "chebyshevu_poly chebyshevu"),
    ('sdata.polynomial("hermite", degree=3)', "hermite_poly hermite"),
    ('sdata.polynomial("probabilists hermite", degree=3)', "hermite_prob_poly hermite_prob"),
    ('sdata.polynomial("laguerre", degree=3) (alpha= for the generalized one)',
     "laguerre_poly laguerre assoc_laguerre"),
    ('sdata.polynomial("jacobi", degree=3, alpha=1, beta=2)', "jacobi_poly jacobi"),
    ('sdata.polynomial("gegenbauer", degree=3, alpha=1)', "gegenbauer_poly gegenbauer"),
    ('sdata.polynomial("cyclotomic", degree=6)', "cyclotomic_poly"),
    ('sdata.polynomial("swinnerton-dyer", degree=2)', "swinnerton_dyer_poly"),
    ('sdata.polynomial("symmetric", degree=2, letters=["x", "y", "z"])', "symmetric_poly"),
    ('sdata.polynomial("through points", x=[0, 1, 2], y=[1, 3, 7])', "interpolating_poly"),
    ('sdata.polynomial("bernoulli", degree=3)', "bernoulli"),
    ('sdata.polynomial("euler", degree=3)', "euler"),
    ('sdata.polynomial("from numbers", numbers=[1, 0, -2]): a polynomial as a formula', "Poly PurePoly poly"),
    ('sdata.polynomial("from numbers", numbers=sdata.make_random_numbers(how_many=4, between=[-5, 5], '
     "whole_numbers=True, with_seed=1))", "random_poly"),
    ('sdata.number_grid(kind="rotation", axis="x", by_degrees=30) (a counterclockwise turn; axis="y", "z" for '
     "rot_ccw_axis2, rot_ccw_axis3)", "rot_ccw_axis1 rot_ccw_axis2 rot_ccw_axis3"),
    ('sdata.number_grid(kind="rotation", axis="x", by_degrees=-30): SymPy rot_axis1 turns the frame, the other way '
     "round from a point (axis=\"y\", \"z\" for rot_axis2, rot_axis3)", "rot_axis1 rot_axis2 rot_axis3"),
    ('sdata.number_grid(kind="identity", size=3)', "eye"),
    ('sdata.number_grid([1, 2, 3], kind="diagonal")', "diag"),
]


# so.<name> and seaborn.objects.<name>: seaborn's objects interface (so.Plot with marks, stats, moves and scales), the
# audit of seaborn 0.13.2 (2026-11-28). A Plot method or a name that is a chart word itself (save, show) explains the
# chart word.
_SEABORN_OBJECTS = [
    ("sdata.chart(table): a chart of a table; every step comes after it, as the Plot methods do", "Plot"),
    ('chart.draw_dots(x="hours", y="marks")', "Dot Dots"),
    ('chart.draw_dots(x="hours", y="marks"), then chart.fit_line(): each draw word adds one more layer', "add"),
    ('chart.draw_lines(x="month", y="temperature", colour="city")', "Line Lines"),
    ('chart.draw_lines(x="hours", y="marks", in_row_order=True): the points joined in the order of the rows',
     "Path Paths"),
    ('chart.draw_dots(x="class", y="marks", show="average", move_layer_by=0.2)', "Shift"),
    ('chart.draw_dashes(x="class", y="marks")', "Dash"),
    ('chart.draw_bars(x="class", y="marks")', "Bar Bars Agg"),
    ('chart.draw_area(x="month", y="rain", colour="city")', "Area"),
    ('chart.draw_band(x="month", between=["lowest", "highest"])', "Band"),
    ('chart.draw_error_bars(of_kind="standard deviation") after a draw word', "Range"),
    ('chart.draw_bars(x="class", y="marks", error="confidence interval")', "Est"),
    ('chart.draw_count_bars(x="class")', "Count"),
    ('chart.draw_histogram(x="marks")', "Hist"),
    ('chart.draw_histogram(x="marks", show="percent") for shares of the whole', "Norm"),
    ('chart.draw_density(x="marks")', "KDE"),
    ('chart.draw_boxes(x="class", y="marks") shows the quartiles of each group', "Perc"),
    ('chart.draw_dots(x="hours", y="marks"), then chart.fit_curve(of_degree=2)', "PolyFit"),
    ('chart.draw_all_dots(x="class", y="marks") spreads the dots of each group a little sideways', "Jitter"),
    ('chart.draw_bars(x="subject", y="marks", colour="class"): the groups stand side by side by themselves', "Dodge"),
    ('chart.draw_bars(x="subject", y="marks", colour="class", stacked=True)', "Stack"),
    ('chart.write_names_on_dots("name") after chart.draw_dots(...)', "Text"),
    ('chart.use_log_scale_x() or chart.use_scale_x("square root") for a number axis', "Continuous"),
    ('chart.order_x("C", "B", "A") for groups on an axis', "Nominal"),
    ('chart.draw_lines(x="time", y="signal"): a column of dates gets a date axis by itself', "Temporal"),
    ('chart.draw_one_chart_for_each_group_in(by="class")', "facet"),
    ('chart.draw_one_chart_for_each_group_in(by="class", same_y=False)', "share"),
    ('sdata.draw_all_pairs(sdata.get_example("marks"), colour="class")', "pair"),
    ('chart.set_size(width=17, height=12, unit="cm")', "layout"),
    ('chart.label_x("Hours"), chart.label_y("Marks") or chart.write_title_on_top("Marks")', "label"),
    ("chart.set_range_x(0, 10) and chart.set_range_y(0, 100)", "limit"),
    ('chart.use_colours("Set2") for the colours, or chart.use_log_scale_y() for an axis', "scale"),
    ('chart.use_style("school")', "theme config"),
    ("chart.as_matplotlib() gives the chart as a matplotlib Figure, for code that needs one", "on plot"),
]

# seaborn's colour helpers and setup functions (owner's decision 2026-11-28: cover all of seaborn), typed with sns.
_SEABORN_MORE = [
    ('sdata.show_colours("deep")', "palplot"),
    ('sdata.pick_colours_with_sliders(kind="brewer")', "choose_colorbrewer_palette"),
    ('sdata.pick_colours_with_sliders(kind="cubehelix")', "choose_cubehelix_palette"),
    ('sdata.pick_colours_with_sliders(kind="dark")', "choose_dark_palette"),
    ('sdata.pick_colours_with_sliders(kind="light")', "choose_light_palette"),
    ('sdata.pick_colours_with_sliders(kind="diverging")', "choose_diverging_palette"),
    ('chart.use_colours("windows blue", "amber", from_colour_list="xkcd")', "xkcd_palette xkcd_rgb"),
    ('chart.use_colours("Mahogany", "Denim", from_colour_list="crayon")', "crayon_palette crayons"),
    ('sdata.change_colour("red", colour_strength_times=0.5)', "desaturate"),
    ('sdata.change_colour("#7a8f99", full_colour_strength=True)', "saturate"),
    ('sdata.change_colour("navy", lightness=0.6)', "set_hls_values"),
    ('chart.use_style("paper", colour_letters="seaborn")', "set_color_codes"),
    ('chart.use_style("paper"): each chart starts from simplydata\'s own look, so there is nothing to reset',
     "reset_defaults reset_orig"),
    ('sdata.get_example("marks"): the practice tables are inside simplydata, so nothing is downloaded and there is no '
     "data folder", "get_data_home"),
    ("sdata.help(): seaborn's dogplot is a joke that downloads a photo of a dog from the internet; simplydata "
     "downloads nothing, so it has no such word", "dogplot"),
]


# families for 100 %, batches 7-9 (plan section 2.3, approved by Manish 2026-11-28): the pointers of the maths family,
# made from its one name table (_maths_functions.py): numbers.take_function, work_on_bits, turn_into_yes_or_no(is_=),
# sdata.find_zeros_of and sdata.find_area_points. A name a list above already points keeps that pointer.
def _maths_family() -> dict:
    from ._maths_functions import pointer_groups

    # the names a namespace's own list, or the lists it falls back on (NAMESPACE_FALLBACK), already point
    lists = {"special": _SPECIAL + _NUMBERS + _SDATA, "numpy": _NUMPY + _NUMBERS + _BLOCKS + _SDATA,
             "sympy": _SYMPY + _SDATA, "scipy": _SCIPY + _SDATA + _NUMBERS + _BLOCKS}
    return pointer_groups({kind: {n for _, names in found for n in names.split()} for kind, found in lists.items()})


_MATHS = _maths_family()

OTHER_NAMES = {"sdata": _build(_SDATA), "table": _build(_TABLE),
               "chart": _build(_CHART + _CHART_2 + _CHART_3 + _CHART_4 + _SEABORN_MORE), "chart3d": _build(_CHART_3D),
               "numbers": _build(_NUMBERS), "block": _build(_BLOCKS),
               "text": _build(_TEXT), "dates": _build(_DATES), "groups": _build(_GROUPS),
               # numbers finishing PR: NumPy's, SciPy's and SymPy's names
               "numpy": _build(_NUMPY + _MATHS["numpy"]), "linalg": _build(_LINALG), "random": _build(_RANDOM),
               "fft": _build(_FFT),
               "stats": _build(_STATS), "special": _build(_SPECIAL + _MATHS["special"]),
               "scipy": _build(_SCIPY + _MATHS["scipy"]), "sympy": _build(_SYMPY + _MATHS["sympy"]),
               "so": _build(_SEABORN_OBJECTS),
               "lists": _build(_LISTS)}  # families for 100 %, batches 1-2 (G12)

# The namespaces: how each is typed in pandas and Polars, and how simplydata writes it ("str.replace")
NAMESPACES = {"str": "text", "dt": "dates", "groupby": "groups", "group_by": "groups", "GroupBy": "groups",
              "DataFrameGroupBy": "groups", "SeriesGroupBy": "groups",
              # charts finishing PR: matplotlib's and seaborn's names (plt.title, ax.set_xlabel, fig.savefig,
              # sns.lineplot, fig.axes[0].set_title, matplotlib.pyplot.hist) and pandas' df.plot.bar mean the chart
              # word: plt.title is write_title_on_top, not pandas' str.title
              "plt": "chart", "pyplot": "chart", "matplotlib": "chart", "mpl": "chart", "ax": "chart", "axs": "chart",
              "axes": "chart", "fig": "chart", "figure": "chart", "sns": "chart", "seaborn": "chart", "plot": "chart",
              "style": "chart", "Axes3D": "chart3d",
              # numbers finishing PR: NumPy's, SciPy's and SymPy's names (np.mean, np.linalg.solve, rng.normal,
              # scipy.stats.gamma, optimize.nnls, sp.Matrix.det): np.mean is numbers.find_average, not a table word
              "np": "numpy", "numpy": "numpy", "linalg": "linalg", "random": "random", "rng": "random",
              "Generator": "random", "RandomState": "random", "fft": "fft", "stats": "stats", "special": "special",
              "scipy": "scipy", "optimize": "scipy", "integrate": "scipy", "interpolate": "scipy",
              "signal": "scipy", "ndimage": "scipy", "spatial": "scipy", "sp": "sympy", "sympy": "sympy",
              "Matrix": "sympy",
              # seaborn's objects interface: so.Dot, so.Plot.facet, seaborn.objects.Hist
              "so": "so", "objects": "so",
              # Polars list and array columns (G12): pl.col("genes").list.sum, Series.arr.max
              "list": "lists", "arr": "lists"}
NAMESPACE_SHOWN = {"text": "str", "dates": "dt", "groups": "groupby", "chart3d": "Axes3D"}
# list. and arr. names (Polars list columns) are looked up only with list. or arr. in front: a bare sum, first or
# unique means the table's word, so the list namespace is not among the ones a bare name lists
# A name that a namespace does not list means the same as on a table (groupby().mean() is find_average_of); a
# text or date name never falls back, because there the table meaning is the wrong one (str.count is not count_rows).
# A matplotlib or seaborn name a chart does not list may be an sdata word (sns.load_dataset) or a numbers word
# (plt.cohere).
NAMESPACE_FALLBACK = {"groups": ("table",), "chart": ("sdata", "numbers"), "chart3d": ("chart", "sdata", "numbers"),
                      # numbers finishing PR: a NumPy, SciPy or SymPy name its own list does not hold
                      "numpy": ("numbers", "block", "sdata"), "linalg": ("numpy", "numbers", "sdata"),
                      "random": ("numbers", "sdata"), "fft": ("numbers", "sdata"),
                      "stats": ("sdata", "numbers", "table"), "special": ("numbers", "sdata"),
                      "scipy": ("sdata", "numbers", "block", "table"), "sympy": ("sdata",),
                      "so": ("chart", "sdata")}
# The NumPy, SciPy and SymPy namespaces (numbers finishing PR) and seaborn.objects, and how a bare name shows each
NUMBER_SPACES = {"numpy": "np", "linalg": "linalg", "random": "rng", "fft": "fft", "stats": "stats",
                 "special": "special", "scipy": "scipy", "sympy": "sympy",
                 "so": "so"}  # seaborn.objects has its own list too, and a name it lacks is looked up the same way
# What can stand in front of a name and changes nothing: pd.read_csv, pl.DataFrame.join, df.merge, Series.replace
QUALIFIERS = {"pd", "pl", "pandas", "polars", "df", "DataFrame", "Series", "Expr", "LazyFrame", "frame", "s", "col",
              "data", "dplyr", "tidyr", "base"}
# How simplydata's own objects are written: chart.draw_bars is a simplydata word, not a name from another tool
SIMPLYDATA_OBJECTS = {"simplydata", "sd", "sdata", "table", "chart", "charts", "page", "numbers", "nums", "grid",
                      "block", "distribution", "dist", "formula", "f", "system", "curve"}


def other_name_parts(typed: str) -> tuple[str | None, str] | None:
    """("text", "replace") for str.replace, Series.str.replace or df["name"].str.replace("a", "b"); (None, "merge")
    for pd.merge, DataFrame.merge or marks.merge (qualifiers, or one name of your own, in front); None for a bare
    name, a simplydata word (chart.draw_bars) or anything else.

    What is inside brackets is left out first, so pl.col("name").str.contains("a") is str.contains; a bracket left
    open at the end (df.str.replace( or df.str.replace("a") is dropped. Namespace names are read in any capitals
    (Str.Replace, groupBy.filter). ("chart", "set_title") for ax.set_title, plt.title, sns.lineplot or
    fig.axes[0].set_xlabel: matplotlib's and seaborn's names."""
    found = _name_parts(typed)
    return None if found is None else found[1:]


def other_name_space(typed: str) -> str | None:
    """The namespace as typed in front of a name: "ax" for ax.set_title, "plt" for plt.hist, "str" for
    Series.str.replace; None when there is none."""
    found = _name_parts(typed)
    return None if found is None else found[0]


def _name_parts(typed: str) -> tuple[str | None, str | None, str] | None:
    """(namespace as typed, its kind, name), as other_name_parts reads them."""
    text = str(typed).strip()
    while text.count("(") > text.count(")"):  # a bracket left open: drop it and what follows
        text = text[:text.rindex("(")]
    while True:  # drop what is inside ( ) and [ ], innermost first
        shorter = re.sub(r"\([^()]*\)|\[[^\[\]]*\]", "", text)
        if shorter == text:
            break
        text = shorter
    parts = [part for part in text.split(".") if part]
    if len(parts) < 2 or not all(part.isidentifier() for part in parts):
        return None
    name, before = parts[-1], parts[:-1]
    spaces = {key.lower(): kind for key, kind in NAMESPACES.items()}
    for part in before:  # so.Plot.facet: seaborn.objects' Plot, not pandas' df.plot
        if part in ("so", "objects"):
            return part, "so", name
    for part in reversed(before):
        if part.lower() in spaces:
            return part, spaces[part.lower()], name
    if before[0] in SIMPLYDATA_OBJECTS:
        return None
    if all(part in QUALIFIERS for part in before) or len(before) == 1:
        return None, None, name
    return None
