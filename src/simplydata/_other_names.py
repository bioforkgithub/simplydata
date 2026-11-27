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
     "interpolate interp interp1d approx approxfun spline splinefun CubicSpline pchip PchipInterpolator "
     "make_interp_spline"),
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
    ('table.find_average_of("marks", for_each_group_in="class")', "groupby group_by aggregate agg"),
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
    # Tables finishing PR: pandas Series.unique() is the different values of one column; DataFrame unique is rows
    ('table.keep_columns("class"), then table.remove_duplicate_rows(), for the different values of one column '
     "(pandas and Polars unique of a column); table.remove_duplicate_rows() alone for whole rows (Polars "
     'DataFrame.unique). The manual chapter "From pandas (and Polars) to simplydata" shows both',
     "unique"),
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
    ('table.add_previous_value_column("last_year", from_column="population")', "shift lag"),
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
    ('chart.draw_one_chart_for_each_group_in("class")', "facet_wrap facet_grid FacetGrid subplots"),
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
    ("numbers.find_coherence_with(other, time_step=0.01)", "coherence csd mscohere"),
    ("numbers.take_cosine_transform()", "dct dst"),
    ("numbers.show_as_fraction()", "nsimplify Rational rat as_fraction"),
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
    ('table.keep_rows_where("name", contains="an") to keep the rows; for a yes or no column, count first: '
     "table.add_column(\"an_count\", \"count_text(name, 'an')\"), then table.add_group_column(\"has_an\", "
     'rules={"an_count > 0": "yes"}, otherwise="no")', "contains contains_any"),
    ('table.keep_rows_where("name", starts_with="A")', "startswith starts_with"),
    ('table.keep_rows_where("name", ends_with="n")', "endswith ends_with"),
    ('table.keep_rows_where("sample_id", matches_pattern="^S[0-9]+$")', "match fullmatch"),
    ('table.keep_rows_where("sample_id", matches_pattern="^[0-9]+$") for text made of digits (letters: '
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
     'side; joining the text of many rows into one cell is in the manual chapter "From pandas (and Polars) to '
     'simplydata"', "join cat concat"),
    ('table.turn_into_lowercase("name")', "lower to_lowercase casefold"),
    ('table.turn_into_uppercase("name")', "upper to_uppercase"),
    ('table.as_pandas(), then df["name"].str.title() in pandas, and give the result to sdata.table to come back: '
     "simplydata has no word for Title Case", "title capitalize to_titlecase swapcase"),
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
    ('table.find_summary_of(["marks", "hours"], show=["average", "count"], for_each_group_in="class"); different '
     'measures for different columns are in the manual chapter "From pandas (and Polars) to simplydata"',
     "agg aggregate"),
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
    ('table.add_previous_value_column("last_year", from_column="population", for_each_group_in="country")', "shift"),
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


OTHER_NAMES = {"sdata": _build(_SDATA), "table": _build(_TABLE), "chart": _build(_CHART + _CHART_2 + _CHART_3),
               "numbers": _build(_NUMBERS), "block": _build(_BLOCKS),
               "text": _build(_TEXT), "dates": _build(_DATES), "groups": _build(_GROUPS)}

# The namespaces: how each is typed in pandas and Polars, and how simplydata writes it ("str.replace")
NAMESPACES = {"str": "text", "dt": "dates", "groupby": "groups", "group_by": "groups", "GroupBy": "groups",
              "DataFrameGroupBy": "groups", "SeriesGroupBy": "groups"}
NAMESPACE_SHOWN = {"text": "str", "dates": "dt", "groups": "groupby"}
# A name that a namespace does not list means the same as on a table (groupby().mean() is find_average_of); a
# text or date name never falls back, because there the table meaning is the wrong one (str.count is not count_rows)
NAMESPACE_FALLBACK = {"groups": "table"}
# What can stand in front of a name and changes nothing: pd.read_csv, pl.DataFrame.join, df.merge, Series.replace
QUALIFIERS = {"pd", "pl", "pandas", "polars", "df", "DataFrame", "Series", "Expr", "LazyFrame", "frame", "s", "col",
              "data", "dplyr", "tidyr", "base", "stats"}
# How simplydata's own objects are written: chart.draw_bars is a simplydata word, not a name from another tool
SIMPLYDATA_OBJECTS = {"sdata", "table", "chart", "charts", "page", "numbers", "nums", "grid", "block", "distribution",
                      "dist", "formula", "f", "system"}


def other_name_parts(typed: str) -> tuple[str | None, str] | None:
    """("text", "replace") for str.replace, Series.str.replace or df["name"].str.replace("a", "b"); (None, "merge")
    for pd.merge, DataFrame.merge or marks.merge (qualifiers, or one name of your own, in front); None for a bare
    name, a simplydata word (chart.draw_bars) or anything else.

    What is inside brackets is left out first, so pl.col("name").str.contains("a") is str.contains; a bracket left
    open at the end (df.str.replace( or df.str.replace("a") is dropped. Namespace names are read in any capitals
    (Str.Replace, groupBy.filter)."""
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
    for part in reversed(before):
        if part.lower() in spaces:
            return spaces[part.lower()], name
    if before[0] in SIMPLYDATA_OBJECTS:
        return None
    if all(part in QUALIFIERS for part in before) or len(before) == 1:
        return None, name
    return None
