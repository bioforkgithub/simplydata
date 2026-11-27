# Changes

Each release lists what was added, changed or fixed. When a word is renamed, the old word keeps
working for one release and prints a one-line note with its new name.

## Unreleased

### Changed: `sdata.numbers` is now `sdata.number_list` (check your code)

- `sdata.number_list([3, 5, 2, 8])` makes a list of numbers, so the three makers read alike:
  `sdata.number_list`, `sdata.number_grid` and `sdata.number_block`. `sdata.numbers(...)` still works for one
  release and prints a one-line note with the new name; `sdata.help("numbers")` says the same.

### Changed: examples write names in full

- Every example, help text, lesson and message now writes `formula = sdata.formula(...)`,
  `numbers = sdata.number_list(...)` and `distribution = sdata.distribution(...)`, then
  `formula.turn_into_sum()`, `numbers.find_average()` and `distribution.find_percentile(95)`, in place of the
  short names `f`, `nums` and `dist`. Headings, the manual, the dictionary and `sdata.help()` show the words the
  same way. Your own code can use any name; `sdata.help("numbers.find_average")`, `sdata.help("formula.undo")`
  and `sdata.help("distribution.find_median")` work, as the short names still do.

### Added: NumPy, SciPy and SymPy names point to the simplydata word (numbers finishing)

- `sdata.help("np.mean")`, `sdata.help("np.linalg.solve")`, `sdata.help("rng.normal")`,
  `sdata.help("scipy.stats.gamma")`, `sdata.help("optimize.nnls")` and `sdata.help("sp.solve")` name the word for
  that package's meaning: `np.mean` is `numbers.find_average()` (a bare `mean` is still the table word),
  `np.zeros` makes a grid, `np.linalg.norm` hands the numbers to NumPy, `scipy.special.gamma` is the gamma
  function in a formula and `scipy.stats.gamma` the gamma distribution. The names may have `np.`, `numpy.`,
  `np.linalg.`, `np.random.`, `rng.`, `np.fft.`, `scipy.`, `stats.`, `optimize.`, `integrate.`, `interpolate.`,
  `signal.`, `ndimage.`, `spatial.`, `special.`, `sp.` or `sympy.` in front. A test runs every call these
  pointers write.

### Added: manual chapters for readers who know NumPy, SciPy or SymPy (numbers finishing)

- Two new parts after the matplotlib one: "From NumPy and SciPy to simplydata" follows the NumPy absolute
  beginners guide, the NumPy fundamentals and the SciPy user guide; "From SymPy to simplydata" follows the SymPy
  introductory tutorial. For each topic: the job, the simplydata words with a short example, and for the jobs left
  to the library, the hand-over (`numbers.as_numpy()`, `formula.as_sympy()`) and the way back. A test runs every
  example and checks every link.

### Added: `grid.solve_for(b)` and `grid.break_down(test_method=)` (numbers finishing)

- `x = grid.solve_for([5, 10])` solves grid times x = b: SciPy `linalg.solve` for a square grid, least squares
  (`linalg.lstsq`) for a grid that is not square, and the sentence says which. `with_best_fit=True` asks for least
  squares on a square grid too (one whose determinant is 0). `between=[0, None]` keeps every x at 0 or above
  (non-negative least squares, SciPy `optimize.nnls`, as R nnls and MATLAB lsqnonneg), as for unmixing spectra
  or a diet mix; other limits use `optimize.lsq_linear`. `exactly=True` gives SymPy's exact answer. b may be a
  grid, one right side in each column. `sdata.solve` stays the word for equations written as text.
- `parts = grid.break_down(test_method="qr")` gives the parts of a matrix decomposition as a dict of grids and
  prints what each part is and how they multiply back: `"svd"` (the default), `"qr"`, `"lu"`, `"cholesky"`,
  `"schur"`, `"polar"`, `"ldl"`, `"hessenberg"` and `"qz"` (with `together_with=` for the second grid), all from
  SciPy `linalg`. 581 words now.

### Added: `chart.as_matplotlib()`, the door to matplotlib (charts finishing)

- `fig = chart.as_matplotlib()` gives the chart as a plain matplotlib Figure, for a job no simplydata word does,
  as `table.as_pandas()` gives a pandas table. The charts are the Axes in `fig.axes` (`ax = fig.axes[0]`; a
  second y-axis, a colour bar and the other charts of a page come after it), so any matplotlib or seaborn code
  works on them, and `fig.savefig("chart.png")` saves the result. It is a copy: changing `fig` never changes the
  chart, and later words on the chart never change `fig`. It is the matplotlib Figure also for a chart saved as a
  web page, and the last frame of an animation. Pages of charts and pairs charts (`sdata.draw_all_pairs`) have it
  too. 579 words now.

### Added: a manual chapter for readers who know matplotlib or seaborn (charts finishing)

- The manual has a new part, "From matplotlib and seaborn to simplydata", after the pandas one. It follows the
  matplotlib Quick start guide and User guide, then the seaborn tutorial, with a link to each official page: for
  each topic, the job, the simplydata words that do it with a short example on the practice tables, and, for the
  jobs simplydata leaves to matplotlib and seaborn (arrows of your own shape, a tick function, `rcParams`,
  polygons, vector fields, `boxenplot` and more), how to hand the chart over with `chart.as_matplotlib()` and keep
  going. A test runs every example in it.

### Changed: names from matplotlib and seaborn point to the right word (charts finishing)

- About 170 more names from matplotlib and seaborn point to their simplydata word: `lineplot`, `relplot`,
  `displot`, `catplot`, `pairplot`, `clustermap`, `stackplot`, `step`, `bar_label`, `loglog`, `invert_yaxis`,
  `set_xticklabels`, `tick_params`, `colorbar`, `color_palette`, `despine`, `set_theme`, `subplot_mosaic`,
  `gcf` and `gca` (to `as_matplotlib`) and more. The jobs simplydata leaves out (`quiver`, `streamplot`,
  `boxenplot`, `fill` ...) point to the hand-over with `chart.as_matplotlib()`.
- `sdata.help` reads a name with `plt.`, `ax.`, `fig.` or `sns.` in front as matplotlib's or seaborn's name:
  `sdata.help("plt.title")` gives `write_title_on_top` (not pandas' `str.title`), `sdata.help("ax.table")` the
  hand-over, and `fig.axes[0].set_xlabel`, `matplotlib.pyplot.hist` and `df.plot.bar` work too.
- `subplots` also names `sdata.put_in_rows_and_columns`, for a page of different charts.

### Added: a manual chapter for readers who know pandas or Polars (tables finishing)

- The manual has a new part, "From pandas (and Polars) to simplydata". It follows the topics of the pandas
  User Guide and the Polars User Guide, with a link to each official page: for each topic, the job, the
  simplydata words that do it with a short example on the practice tables, and, for the jobs simplydata leaves
  to pandas and Polars (the row index, a function for each group, memory, lazy plans and more), how to hand the
  table over with `table.as_pandas()` or `table.as_polars()` and come back with `sdata.table(...)`. It also
  shows the different values of a column, different measures for different columns, the next value, a yes/no
  column from a text match, text joined for each group, and a table saved as Markdown or LaTeX. A test runs
  every example in it.

### Changed: names from pandas and Polars point to the right word (tables finishing)

- 246 more names from pandas and Polars point to their simplydata word: `ffill`, `idxmax`, `top_k`,
  `rolling_mean`, `ewm_mean`, `case_when`, `insert`, `kurt`, `to_json`, `values`, `from_dict` and more on a
  table or on `sdata`, and the text, date and group steps typed with their namespace: `sdata.help("str.replace")`
  gives `table.replace_text_in`, `sdata.help("dt.round")` gives `table.round_dates_in` and
  `sdata.help("groupby.filter")` gives `table.keep_groups_where`, not the table words with the same short name.
  `Series.str.contains`, `df["name"].str.split(";")` and `pd.read_csv` work too. A short name lists every
  meaning (`sdata.help("replace")` shows `table.replace` and `str.replace`).
- 14 pointers led to the wrong or a half word and are fixed: `cummax`, `cummin` and `cumprod` give
  `show="biggest"`, `"smallest"` and `"product"`; `filter` also gives `keep_columns(contains=)` (pandas
  `DataFrame.filter` keeps columns); `where` gives `replace_values_in` (pandas `where` replaces values); `isin`
  gives `keep_rows_where(is_one_of=)`; `to_excel` saves .xlsx; `count` names the filled cells of each column;
  `astype` names all four `turn_into_` words; and `unique` gives `keep_columns` then `remove_duplicate_rows`, with
  the manual chapter.

### Fixed (tables finishing)

- A .csv file saved with `fast=True` (Polars) wrote times without a time zone as `2024-07-01T23:45:00.000000`,
  which `turn_into_dates` could not read back, while pandas wrote `2024-07-01 23:45:00`. Both engines now write
  pandas' text for times, times of day (`01:02:03`, not `01:02:03.000000000`) and True/False (not true/false).
  Polars could not save durations to .csv at all (a raw error); they are now written as pandas writes them
  (`0 days 01:00:00`). The one difference left: an empty text (`""`) is `""` on Polars and nothing on pandas.
- A one-column table saved as .csv with `fast=True` wrote an empty cell as an empty line, so reading the file back
  lost that row. It is now written as `""`, as pandas does.
- Reading a .csv or .tsv file with `fast=True` (Polars) took a quoted `""` as empty text, so a column of numbers
  with one such cell came back as text. It is now an empty cell, as pandas reads it: both engines read the same
  numbers, True/False values, text and times back.
- `sdata.help("simplydata.table")` and `sdata.help("sd.table")` explain `sdata.table`, and a name of your own in
  front of a word (`sdata.help("weather.draw_bars")`) explains the word.
- A table of one column said "1 columns" (in `describe_columns`, `check_if_same_as`, `show_differences_from`, its
  printout and the cross tables of `across=`); it now says "1 column" and "1 row".
- `spread_into_columns`: its help says to keep only the needed columns first, and with `show=` its sentence names
  the columns in quotes and counts the cells that combine more than one row (it said "for its fruit and day,
  shop, price"). When several columns differ so that no row merges (the weather table without `keep_columns`),
  a note now says why the new columns are mostly empty.

### Changed: line ends in text files (tables finishing)

- Text files (.csv, .tsv, .csv.gz, .tsv.gz) now end their lines the same way on every computer (a line feed, as
  Polars writes them). On Windows pandas wrote a carriage return and a line feed; now the same table gives the same
  file on Windows, macOS and Linux, on both engines.

### Changed: minimum versions

- NumPy 2.1 or newer is needed (was 2.0): `block.split_into_one_block_per` uses NumPy's `np.unstack`, which
  NumPy has from 2.1, and its printout names it.
- The `simplydata[xarray]` extra needs xarray 2024.10 or newer (was 2024.6): pandas 3 refuses older xarray when a
  block is turned into xarray, so `block.keep_where`, `block.remove_where`, `block.split_into_one_block_per` and
  `sdata.number_block` failed with the oldest allowed versions.

### Fixed

- `find_where_smallest(..., start=...)` and `find_where_biggest(..., start=...)` raised a Python `AttributeError`
  whenever SciPy could not find a dip or a peak from the start (for example `find_where_smallest("x", start=0)`).
  They now say the formula keeps getting smaller (or bigger), so it may have no smallest (or biggest) value.
- The dictionary lists the other names of block words (`reshape`, `squeeze`, `rot90`, `flip`, ...), and
  `block.reverse(over=...)` has its own entry (NumPy `flip`).

### Changed: `ends="mirror"` now means SciPy's "mirror" everywhere (numbers phase)

- `nums.smooth(ends="mirror")`, and with it `table.add_smoothed_column(ends="mirror")` and
  `chart.draw_smooth_line(ends="mirror")`, now use SciPy mode "mirror": the readings are mirrored about the end
  reading, which is not repeated (d c b | a b c d). Before this change they used SciPy mode "reflect", which repeats
  the end reading (d c b a | a b c d), so the first and last few smoothed values change. `grid.smooth` and
  `block.smooth` already meant "mirror" this way; now all the smoothing words agree.
- `ends="reflect"` is a separate option on all of them and means SciPy mode "reflect". To get the old numbers of
  `ends="mirror"`, write `ends="reflect"`.
- `test_method="gaussian"` on numbers takes `ends="reflect"` (its default, SciPy's own, so the default numbers do not
  change) or `ends="mirror"`. Before, its only choice was called "mirror" but was SciPy "reflect".
- Tests compare both options with SciPy and R (`stats::filter` on the padded readings), and two new reliability cases
  check them on the Lake Huron levels.

### Added: numbers phase, batch 4 (the SymPy words; approved by Manish 2026-11-26)

- Formulas: `f.find_slope_formula(how_many_times=2)` (up to 20 times) and `for_letter=["x", "y"]` for a mixed
  slope; `f.find_limit_as("x", goes_to=0, from_side="above")` (or `"below"`; `"right"`, `"left"`, `"+"` and `"-"`
  work too); `f.show_as_decimal(digits=50)` (text, up to 10,000 digits); `f.group_by_powers_of("x")` (expand, then
  collect) and `f.turn_into_partial_fractions()` (apart), both undo-able; `f.as_sympy()` gives the SymPy expression
  to carry on in SymPy itself. In Jupyter a formula is shown typeset (`_repr_latex_`).
- `letters_are={"k": "positive"}` on `sdata.formula` and on `sdata.solve(..., exactly=True)`: "positive", "zero or
  more", "negative", "real", "whole number", "positive whole number" (SymPy's assumptions), so `sqrt(k**2)` is `k`,
  `log(k*t)` splits, and `c**2 = 4` gives only `c = 2`.
- `sdata.solve(..., exactly=True)`: `for_letter="T"` rearranges for one letter and keeps the others as letters
  (`p*V = n*R*T` gives `T = V*p/(R*n)`); rules (`<`, `>`, `<=`, `>=`) give the ranges where they hold (SymPy solveset
  over the real numbers, reduce_inequalities for several), as a table of `from`, `to` and whether each end is in; a
  formula made with `sdata.formula` means formula = 0, so `sdata.solve(f.find_slope_formula(), exactly=True)` finds
  the flat points. Without `exactly=True` a rule now points to it.
- `chart.draw_curve(f, between=[0, 10])` draws a formula made with `sdata.formula`.
- `sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])` (SymPy summation): an exact sum, the formula of a
  sum up to a letter (`between=[1, "n"]`), a plain sentence when the sum grows without end or does not settle, and
  the decimal when SymPy finds no exact formula but the series settles.
- `sdata.find_volume_under(..., exactly=True)` (SymPy integrate). `sdata.find_path_over_time(..., exactly=True)`
  without `at_start=` gives the general formula with its free constants (C1, C2); one second-order equation,
  `"d2x/dt2 = -k*x - c*dx/dt"`, is solved exactly (dsolve) or in numbers (solve_ivp with `dx/dt` as a second changing
  value, shown in the table); `at_start=` then needs `x` and `dx/dt`.
- Grids: `find_determinant()` (SciPy linalg.det), `take_inverse()` (linalg.inv, undo-able) and `find_eigenvalues()`
  (linalg.eigvalsh for a symmetric grid, else eigvals; biggest first), each with `exactly=True` (SymPy Matrix with
  the numbers as fractions: det, inv, eigenvals with how many times each comes); `find_null_space(exactly=True)`
  (SymPy nullspace). Exact work takes grids up to 12 x 12 (6 x 6 for eigenvalues).
- Safety: every heavy SymPy call (simplify, factor, expand, integrate, limit, series, solve, solveset, dsolve,
  summation, apart, collect and the exact grid words) runs under one time limit of 60 seconds, in one local helper
  process that is kept alive between calls (multiprocessing, started with "spawn"; it imports SymPy only, and talks
  to Python through a pipe, never the network; it writes nothing and stops when Python exits). A call that runs
  longer is stopped with a plain sentence, and the next call starts a fresh helper. Where no helper process can be
  started, SymPy runs without the limit and simplydata says so once (`SIMPLYDATA_SYMPY_HELPER=0` turns the helper
  off). A sum with letters raised to a whole power above 100 is refused before it is multiplied out (`(x + y + z +
  1)**200` would have about 1.4 million terms).
- Other names from SymPy, MATLAB and R point to the new words (apart, collect, vpa, summation, Sum, symsum,
  reduce_inequalities, refine, det, inv, eig, eigenvals ...).
- After the independent review of the batch: a series with no exact formula prints only the digits SymPy's evalf
  gives the same at 15 and 30 digits of precision (a slowly settling series such as 1/(k log(k)**2) gets 2.1, not
  ten wrong digits), and refuses when not even two agree; a sum up to a letter of the formula uses that same letter;
  a long finite sum is worked out from SymPy's formula of the sum up to n (exactly when it is a polynomial, else as a
  decimal), and a sum whose terms have more than 100,000 digits is refused; `letters_are=` reaches formulas in
  `solve` and the ranges of rules (x positive: 0 < x < 2), and a value or range that contradicts it is refused in
  `find_value_at`, `put_in`, `find_area_under`, `find_volume_under`, `find_where_*` and `draw_curve`; a rule that
  repeats (sin(x) > 0) is refused, since SymPy gives one period only; a letter every number fits is said ("y can be
  any number; x = 3 - y"); `find_eigenvalues` follows R eigen()'s order (by size for a grid that is not symmetric,
  with R isSymmetric's tolerance) and real exact eigenvalues have no imaginary part; exact grids keep a number that
  no short fraction gives back (4 + 1e-15) instead of rounding it; numbers longer than 4300 digits are shown with
  their size; `gamma`, `lgamma`, `digamma`, `beta` and `besselJ` of a number above 1000 are refused while reading;
  `put_in`, `find_value_at` and every decimal of an exact answer run under the time limit; typed decimals and
  `known=` values are the same exact numbers in exact paths; infinity is written as a word.
- The helper process: a watchdog thread ends it as soon as Python is gone (even mid-job), its own output goes to the
  null device, it has a memory limit (half the memory free when it starts, 1 to 4 GB), multiprocessing's preparation data
  leaves your script out instead of swapping `__main__`, an embedded Python whose executable is not Python runs SymPy
  in-process with a note, every SymPy call of one word shares one 60-second deadline, and the stop sentence gives
  advice for that word. On Linux and macOS multiprocessing also starts its own small resource-tracker process.
- After the second review: a series with no exact formula is bounded instead of compared at two precisions (the
  first 1,000 or 10,000 terms added by SymPy evalf, the rest between two integrals of the terms by SymPy: the
  integral test, with the trapezoid and midpoint rules when SymPy shows the terms bend upwards), and only the digits
  both bounds round to are printed (1/(k log(k)**3) now prints 2.065886539, as R); a formula is read unevaluated and
  the numbers inside `gamma`, `lgamma`, `digamma`, `beta` and `besselJ` and of powers are worked out under the time
  limit and checked first (`gamma(abs(-2000))`, `gamma(2000*x/x)` and `(1 + 1/10**4)**(10**4)` are refused, never
  worked out while reading); a repeating rule is answered when it always or never holds, or when the other rules
  keep the letter to a range of finite length (one period of SymPy solveset moved along by whole periods), and
  refused otherwise; the size of a very long number comes from SymPy N and integer_log; `find_eigenvalues(exactly=
  True)` follows R eigen()'s order also among eigenvalues of the same size; `put_in(x="y")` gives y what x was; a
  whole typed decimal is its simplest fraction again (1e23 is 10**23); the sum of r**k has no value (instead of nan)
  where |r| >= 1, so its slope has none there either, and such a formula works in `find_where_*`,
  `find_area_under` (also exactly) and `draw_curve`; each thread keeps its own deadline, and the helper start leaves
  the main script out only for its own thread; the exact grid words share one deadline; a rule always true or false
  for what the letters are, and the ranges of whole-number letters, are said plainly; typed decimals in rules are
  exact (x < 3.5 is x < 7/2).
- After the third review: every power whose base is not a plain letter or number, and every exp of a log, is sized
  before SymPy makes the number (`(abs(999)**100)**100`, `(999*x)**400`, `exp(3000*log(10))` and a typed whole
  number of 400 digits to a power are refused at once); `find_where_smallest`/`find_where_biggest` say when the
  formula has no value anywhere the search looked, instead of an infinite answer; `put_in` refuses an expression in
  place of a letter with a kind unless SymPy shows it has that kind; a repeating rule over too long a finite range
  says how many repeats it covers; a series whose terms rise to 0 gets its decimal too, the bounds leave room for
  the accuracy of SymPy's integrals, and the 1,000-term answer is kept when the 10,000-term round fails.

### Added: numbers phase, batch 3 (formulas, areas and paths, grids, nearest rows; approved by Manish 2026-11-25)

- Exact maths with SymPy (1.14 or newer), the new extra `simplydata[exact]`: `f = sdata.formula("(x + 2)**2 - 4")` with
  `f.make_simpler()`, `f.turn_into_sum()`, `f.turn_into_product()`, `f.find_slope_formula()`, `f.find_area_formula()`,
  `f.find_value_at(x=2)`, `f.put_in(x="y + 1")`, `f.show_as_latex()`, `f.find_limit_as("x", goes_to=0)`,
  `f.find_taylor_series(around=0, up_to_power=4)` and `f.undo()`; `sdata.solve("x**2 = 2", exactly=True)`;
  `nums.show_as_fraction()`. The text is checked with Python's ast before SymPy reads it, and every letter stays a
  letter (E, I, N and beta too). A formula is accepted by `find_where_smallest`, `find_where_biggest` and
  `find_area_under`. Without SymPy these words say how to install it.
- Areas and paths over time (SciPy integrate): `sdata.find_area_under("exp(-x**2)", between=[0, "infinity"])`
  (quad; `test_method="gauss"`; `exactly=True`), `sdata.find_volume_under(...)` (dblquad, tplquad, nquad),
  `sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start=, between=, known=, time_step=, stop_when=)`
  (solve_ivp with R deSolve's tolerances; `exactly=True` with SymPy dsolve) and `nums.turn_into_running_area()`.
- Numbers: `take_cube_root()` (also on grids), `find_coherence_with(other)`, `take_cosine_transform()`.
- Grids: `get_numbers_at_pairs(rows=, columns=)`, `get_numbers_from_each_row_at(columns=)`,
  `find_each_patch_that(is_above=, touching=)`, `change_size_to(rows=, columns=)`, `rotate(by_degrees=)`,
  `take_matrix_exp()` and `find_null_space()`.
- Tables: `find_nearest_rows_to(point, how_many=, within=)`, `find_distances_to_rows_of(other, using=)` and
  `find_fence_around(x=, y=)` (SciPy spatial).
- Other names from SymPy, SciPy, MATLAB and R point to the new words; lessons 13 and 19 have new parts; SymPy is
  cited (Meurer et al. 2017).

### Added: NumPy + SciPy phase, batch 2 (netCDF files, labels, dates and places; approved by Manish 2026-11-25)

- netCDF files (P21, P22): `sdata.number_block("sst.nc", values="sst")` reads one variable as a block with its names,
  labels and units (decision 2: one block per variable); `values=["u", "v"]` stacks variables as a new direction
  "variable"; `"argo_*.nc"` joins several files by their labels; `keep_on_disk=True` leaves the numbers in the file
  until a word needs them (`keep_where`, `keep_by_position_in` and `get_numbers_nearest_to` cut it there);
  `empty_values=[-999]`; `with_labels={"time": dates}`. `block.save("out.nc")` writes netCDF-4, compressed.
  `sdata.show_whats_inside("file")` shows the variables, sizes, units and labels of a .nc file (and the arrays of
  .npz/.npy, the sheets of .xlsx) without reading the numbers. xarray with h5netcdf (and SciPy's engine for classic
  netCDF-3) is the extra `simplydata[xarray]` (decision 3); without it, a plain error with the install line.
- Privacy: simplydata opens only the file you name; it never downloads or sends anything. A file on a network share
  or a mapped drive is read like any file you name (as `sdata.table` does). Web addresses and every `scheme://` path
  (http, https, s3, OPeNDAP, file:// ...) and `::` tool chains are refused before anything is opened, and so are
  variables that come from another file through a hidden link (HDF5 external links, virtual datasets, soft links to
  nothing). xarray gets an absolute path with the engine named; `show_whats_inside` writes nothing. Tests run with
  the network blocked.
- Dates, labels and places on blocks: `find_average(in_each="month")` (all Januaries together; also "season",
  "year", "quarter", "day of year", "hour") and `find_average(every="month")` (each calendar month) on every block
  summary (P26, xarray groupby and resample); `find_average(in_groups_of={"latitude": 4})` for a coarser grid (P46);
  `block.find_values_at(latitude=60.5, longitude=5.25)` (P27, SciPy interpn as xarray interp);
  `block.get_numbers_nearest_to(latitude=60.4, within=0.5)` (P28); `block.turn_into_change_from_average(
  in_each="month", from_years=["1991", "2020"])` (P29; decision 8: the reference-period option was scored at build
  time, `from_years=` 99.3 against `baseline=` 37.2; confirmed by Manish 2026-11-26, and `baseline=` works as its
  other name);
  `block.get_labels_of("time")` and `block.add_labels_to("time", dates)` (P47).
- `smooth(over=[...])` on grids and blocks (P30): moving average, gaussian and median (SciPy ndimage filters with
  axes=); `block.change_size_to(latitude=90)` (SciPy ndimage.zoom; number labels follow) and
  `block.rotate(by_degrees=15)` (SciPy ndimage.rotate) (P32, block versions).
- Numbers: `nums.make_random_picks(how_many=, putting_back=True, with_chances=, with_seed=)` (P10; decision 5:
  chances must add up to 1), `nums.take_log_odds()` and `nums.turn_into_chances()` (P24, SciPy logit and expit),
  `sdata.count_ways_to_choose(3, out_of=10)` and `sdata.count_ways_to_order(3, out_of=10)` (P23, exact),
  `sdata.numbers("readings.txt", empty_values=[-999])` (P38), `sdata.make_random_numbers(of_shape=(24, 8, 12))`
  (P39, a block).
- Wiring: learn groups (3), help examples, a part of lesson 13, other names (numbers, blocks and sdata; NumPy's
  `choice` now points to make_random_picks), underneath entries (`_underneath/numbers_2.py`), method basis, manual
  library lines, h5netcdf and h5py in the extra and in CI, 22 real-data reliability cases
  (`validation/cases_underneath_numbers_2.py`: El Nino, AirPassengers, iris, Michelson, Lake Huron) against xarray,
  SciPy, NumPy and pandas and, where it has the calculation, base R. Tests: `tests/test_numbers_batch2_*.py`.

### Added: NumPy + SciPy phase, batch 1 (blocks of numbers, yes or no values, rounding and angles; approved by Manish 2026-11-25)

- `sdata.number_block(...)`: numbers with any number of directions (NumPy's n-D array), from lists inside lists, a
  NumPy array, `of_shape=(24, 8, 12), filled_with=0`, `like=other`, a long table (`directions_named=["east",
  "north"], values="height"`: the columns' values become each direction's labels) or an xarray DataArray (its names
  and labels come too). Directions have names: `directions_named=[...]`, or row and column for the last two, then
  page and book (decision 1 of the NumPy review), then direction a, b ... A block prints page by page: "page 1 of
  24 (8 rows x 12 columns)", and every shape is said in words.
- Block words: `find_shape`, `count_directions`, `find_direction_names`, `get_number_at(hour=1, row=2, column=3)`,
  `get_all_numbers`, `turn_into_table` (one column per direction), summaries with `over=` (the directions that go)
  and `in_each=` (the ones kept), `turn_into_running_total(over=)`, `keep_by_position_in` and
  `remove_by_position_in`, `keep_where` and `remove_where` on labels (a range in either order, also when the labels
  run downward), `change_shape_to(8, "rest")` and `change_shape_to(one_row_per="image")` (with `fill="repeat"`),
  `add_direction`, `remove_directions_of_size_one`, `swap_directions`, `move_direction`, `reverse(over=)`,
  `rotate(by_quarter_turns=)`, `move_round_by(3, over=)`, `insert_numbers(at_position=, over=)`,
  `repeat_each_number`, `repeat_whole_block`, `add_numbers_from(other, over=)`, `split_into_pieces`,
  `split_into_one_block_per`, and `sdata.stack_up([a, b, c], as_new_direction="image")`. The maths words take
  `over=`: `plate.subtract(blank, over="row")`.
- Stretching (NumPy's broadcasting) in plain words: blocks that name every direction line up by name (xarray when the
  new extra `simplydata[xarray]` is installed, NumPy expand_dims and transpose otherwise, with a test that both
  agree), others from the right as NumPy does; a clash says, in at most five lines, how the shapes line up and what
  to write instead; words say which numbers were used again, symbols only when both sides stretch.
  `block.show_how_it_lines_up_with(other)`, `only_show_new_shape=True` on every shape-changing word and summary,
  `block.stretch_to(shape)`, `sdata.stretch_to_same_shape(a, b)`, `sdata.hide_stretching_notes()` and
  `sdata.show_stretching_notes()`.
- Yes or no values: `nums.turn_into_yes_or_no(is_above=20)` with `&`, `|` and `~`; `keep_numbers_where`,
  `remove_numbers_where`, `replace_numbers_where(yes_no, with_value="empty")`; `count_numbers_that`,
  `check_if_any_number`, `check_if_all_numbers` (with `over=` on grids and blocks); `check_if_same_as(other,
  within=)`; `grid.keep_rows_where(column=3, is_above=0.5)` and `grid.remove_rows_where`.
  `replace_each_number_that(..., with_value="empty")` works too.
- Rounding and angles: `round_down()`, `round_up()`, `take_whole_part()`; `take_sin`, `take_cos`, `take_tan` (radians,
  as NumPy; `degrees=True` for degrees); `change_angles_to("degrees")`; `divide_by(7, rounding_down=True)`.
- `find_where_biggest()` and `find_where_smallest()` on numbers, grids and blocks: the position counted from 1 (with
  the NumPy index in the sentence), `over=` for one position along a direction.
- `make_pair_table_with(other, by_subtracting=True)`: every pair (NumPy outer; `as_blocks=True` for Kronecker).
- `take_fourier_transform(with_zero_in_middle=True)`: frequency 0 in the middle (SciPy fftshift); the inverse
  transform puts the order back.
- Other tools' names point to the new words (reshape, squeeze, expand_dims, flip, roll, tile, broadcast_to,
  broadcast_shapes, outer, floor, argmax, isclose, count_nonzero ...). Underneath entries, method basis, learn groups
  and two new parts of the numbers lesson; 49 new real-data cases in the reliability study
  (validation/cases_underneath_numbers_1.py: iris as a block, AirPassengers, Lake Huron, Michelson), each against
  NumPy and base R.

### Changed: NumPy + SciPy phase, batch 1

- `table.values_at` is now `table.find_values_at` (decision 7: a verb, as `find_value_at`); the old name works for one
  release with a note.
- Lessons, help examples and the 30-day guide call a page of charts `charts` (`charts = sdata.put_side_by_side(a, b)`),
  since "page" is now the name of a block's third direction.

### Added: charts phase, batch 1 (the priority-1 matplotlib and seaborn words; approved by Manish 2026-11-25)

- Reading a chart back: `chart.get_text_drawn()` (a table of every piece of text: title, axis names, legend title and
  entries, notes, captions, panel letters, tick words, numbers on bars, names next to dots, with where each legend or
  note is), `chart.get_scales_drawn()` (a table of every scale: x, y, second y, z and colour, with its name, range,
  kind, whether it is flipped, its ticks and tick words, the panels sharing its range, and a colour scale's map and
  middle) and `chart.get_size(unit="cm")` (the pair of `set_size`). All three read what matplotlib drew, as
  `get_numbers_drawn()` does; pages of charts have them too.
- `get_numbers_drawn()` gives each drawn point its `colour` ("#0072b2") and, when a named colour has exactly that
  code, its `colour name` ("blue").
- `chart.get_size()` gives the size `chart.save()` writes at 300 dots per inch (read from the picture itself): exactly the size `set_size` asked for, or without it the page trimmed to what is drawn.
- `with_one_legend=True` stops with a message naming the chart that differs unless every chart shows the same legend (name, groups in the same order, colours, kind of mark, shapes, dashes and patterns).
- In black and white the greys stay between about 25 % and 75 % with black edges; patterns are drawn in black or white, whichever shows; boxes, violins and density curves get patterns or dashes too, box medians are white with a black rim, heat maps, contour maps and surfaces use greys (a two-sided scale prints a note), and a page in black and white gets the patterns.
- `chart.undo()`: takes the last word back (a layer, a title, the style, the size), as `table.undo()` does.
- `chart.put_legend_inside("top left")` (or "top right", "bottom left", "bottom right", "top", "bottom", "left",
  "right", "middle", "best").
- `sdata.put_in_rows_and_columns([[a, a], [b, c]], widths=[2, 1], heights=[2, 1])`: rows given as lists, a chart
  named in several places spans them, `None` leaves a place empty; `widths=` and `heights=` also work on a plain
  grid. `with_one_legend=True` on `put_side_by_side`, `put_one_above_other` and `put_in_rows_and_columns`: one
  legend for the whole page.
- `chart.write_letter("B")`: a panel letter on a chart that is not on a page.
- `write_note(..., where="top left")` (a fixed place in the plot), `with_box=True` (a frame round the note) and
  `with_curved_arrow=True`.
- Second cues besides colour: `hatched=True` on `draw_bars`, `draw_histogram`, `draw_area` and `draw_pie` (each group
  its own pattern, in the legend too), `hollow=True` on `draw_dots`, `dashed="city"` (each group its own dashes) and
  `dotted=True` on `draw_lines`, and `chart.use_shapes("circle", "square", "triangle")`.
- `use_style("black and white")`: greys, with patterns, dashes and shapes for the groups; "greyscale" and
  "grayscale" mean the same.
- `use_colours("Set2")`, `use_colours("colour-blind safe")` and `use_colours("viridis", how_many=5)`: named colour
  sets (seaborn's `color_palette`).
- `save("logo.png", see_through=True)`: no background. `.eps` files can be saved (see-through marks are saved solid,
  with a note).
- Other names point to the new words: `get_title`, `get_xlim`, `get_size_inches`, `move_legend`, `tag_levels` ...

### Changed: charts phase, batch 1

- matplotlib 3.11 or newer is needed (`matplotlib>=3.11,<4`; it was `>=3.10`): patterns are drawn in white on dark
  fills with matplotlib's `set_hatchcolor`, which 3.10 does not have (there a pattern always takes the edge
  colour, so in black and white, with black edges, it could not be seen on dark greys).
- Text in saved `.pdf`, `.eps` and `.svg` files stays real text: fonts are kept as TrueType (Type 42) in PDF and
  PostScript, which journal checkers accept, and as text in SVG (decision D6). Files get a little bigger.
- Every chart type starts with `draw_` (decision D11): `draw_sticks`, `draw_spectrum`, `draw_spectrum_over_time`,
  `draw_lag_dots`, `draw_peak_dots`, `draw_difference_dots`, `draw_forecast`, `draw_trend_and_season`,
  `draw_autocorrelation_bars`, `draw_cross_correlation_bars`, `draw_trade_off_curve` and `draw_forest_plot`. The old
  names still work for one release, with a note.

### Fixed: charts phase, batch 1

- `get_numbers_drawn()` no longer stops on lines drawn at named x positions (error bars on dots at groups, as on
  iris): the numbers matplotlib turned the names into are read, and given back as the names.
- `get_numbers_drawn()` on a surface gives each drawn grid point once (kind "surface"), with its height in `value`,
  instead of every corner of every piece.
- `get_numbers_drawn()`: 3D dots coloured by a number keep each dot's colour (matplotlib sorts the drawn colours by depth); colours that cannot be matched to the points are left empty, never guessed.
- `get_scales_drawn()` gives the `middle=` asked for on every colour scale, names heat-map axes as groups, and gives log-axis tick words as shown ("10²", with the small ticks 30, 40 ...); `get_text_drawn()` reads a page title once. `.eps` notes every see-through part (seaborn's bands too), not only `transparency=`.
- `get_numbers_drawn()`: what is drawn on a second y-axis belongs to the panel it is on (panel 1 of a single
  chart), its layers after the panel's own, as the docstring always said.

### Added: charts phase, batch 2 (priority-2 matplotlib and seaborn words; approved by Manish 2026-11-25)

- New chart words: `draw_wind_rose(direction=, speed=, every=30)` (NumPy histogram2d counts as bars round a
  compass), `draw_rug_lines(x=)` (seaborn rugplot), `draw_arrow(start=, end=)`, `put_chart_inside(other_chart,
  where=, size=)`, `add_second_x(...)` (a column, or `formula=` for the same places in other units), `hide_frame()`,
  `hide_ticks_x()` / `_y()`, `show_small_ticks_x()` / `_y()`, `use_true_shape()`, `make_square()`,
  `put_colour_bar_at_bottom()` / `_at_top()` / `_at_left()`, `hide_colour_bar()`, `put_ticks_colour_bar(...)`, the
  3D words `draw_lines_3d()`, `label_z()`, `set_range_z()`, `put_ticks_z()`, `look_from(height=, around=)`
  (`view_from` works too), and `say_what_it_shows()`, which prints and gives back what a chart shows: each chart
  type you drew with its columns and groups ("3 lines, one for each city: ..."), error bars, lines on top, and the
  axes, legend and colour bar read from the drawn figure; nothing is counted or worked out (`describe` points to
  it).
- New options: `y=` on `draw_histogram` and `draw_density` (two-way), `in_halves=True` on `draw_violins`,
  `show=` and `error=` on `draw_dots` (one dot per group, seaborn pointplot; number x keeps its spacing),
  `stacked="percent"` on `draw_bars` and `draw_area` (shares of totals, with the axis named "percent of total";
  values below 0 are refused, and empty places and stacks with a total of 0 get a note), `hole=` on `draw_pie`, `as_wires=` and `with_height_lines=` on `draw_surface`, `between=` on
  `draw_line_at_y` and `draw_line_at_x`, `title=` and `ticks=` on `use_font_size`, `per_row=` on
  `put_legend_at_bottom`, `put_legend_at_top` and `put_legend_inside`, and `formula=` on `add_second_y` (the way back by SciPy brentq).
- One option, one meaning: `value=` and `z=` are the same option on `draw_heatmap`, `draw_contour` and
  `draw_surface`; `x=` and `y=` mean `labels=` and `values=` on `draw_pie`.

- Both batches together: `chart.undo()` takes back every batch-2 word and names the word you used
  ("Undone: chart.draw_wind_rose()", not the step inside it); in black and white, wind roses get greys and a pattern
  for each speed band, 3D lines get dashes, average dots (`show=`) get shapes (`use_shapes` works on them too) and
  two-way histograms get greys; `say_what_it_shows()` names a panel letter (not as a title), notes with their text,
  where a legend was put, patterns, hollow dots, dashes, dot shapes and the black-and-white style; pages have
  `page.say_what_it_shows()` (each chart by its letter and place); `hatched=True` and `drawn_as="outline"` on
  `draw_histogram` are refused together, as `hatched=` with `y=`.

### Changed: charts phase, batch 2

- `draw_histogram(steps=True)` is now `draw_histogram(drawn_as="outline")`; `steps=True` works for one release with
  a note.
- The other name `windrose` now points to `draw_wind_rose` (it pointed to `draw_polar`).

### Added: charts phase, batch 3 (web pages and the priority-3 words; approved by Manish 2026-11-25)

- Web pages: `chart.save("marks.html")` and `chart.show_in_web_page()`. The chart is drawn by matplotlib and seaborn
  as for a picture, and what they drew is copied into plotly (decision D3): the same numbers, words and scales as
  the picture, nothing worked out again. Point at marks, zoom, click the legend. Lines, dots, bars, bands, error
  bars, stems, shapes, contour lines, heat maps, hexagons, pies, round charts, 3D lines, dots, surfaces and bars,
  notes, legends, colour bars, pages of charts and animations (a play button and a slider) all go to the web page.
  Needs the new extra `pip install "simplydata[web]"` (plotly); without it the two words say how to install it.
- Privacy: plotly.js is written inside the page, so it opens with no internet and loads nothing (no web address, no
  MathJax, no web fonts, plotly's links and picture button switched off); pictures still come from matplotlib
  (decision D4). `show_in_web_page()` writes the page to a file on this computer and opens it in the browser (no
  server), or shows it below the cell in a notebook. Saving says once that the page holds the numbers drawn.
- `chart.show_when_pointing("name", "class")`: the columns shown when pointing at a dot or a line (only those, never
  the whole row); `all_lines=True` shows every line at that x. `chart.add_range_bar_x()`: a bar under the x-axis to
  choose the range shown. A picture leaves both out, with a note once.
- Refused in web pages with one sentence (decision D5): `chart.break_between_y(50, 500)` (a broken y-axis, drawn on
  two panels as in the matplotlib gallery), `chart.use_scale_y("square root")` / `use_scale_x` (also "logit" and
  "asinh") and `use_log_scale_y(through_zero=True)` / `use_log_scale_x(through_zero=True)` (matplotlib's symlog);
  all three work in pictures.
- `chart.use_background_colour("ivory")`, `chart.draw_hexagon_bins(x=, y=)` (matplotlib hexbin, with a colour bar
  of the counts), `draw_side_histograms(drawn_as="density")` (seaborn kdeplot on the edges),
  `chart.draw_time_bars(start=, end=, y=)` (bars from a start to an end, dates or numbers),
  `chart.draw_rectangle(x_between=, y_between=)`, `chart.draw_circle(centre=, radius=)`,
  `chart.draw_residual_dots(x=, y=)` (seaborn residplot), `chart.draw_event_lines(x=, y=)` (matplotlib eventplot) and
  `chart.draw_bars_3d(x=, y=, z=)` (matplotlib bar3d, with a note that a heat map is often clearer).
- `get_numbers_drawn()` reads hexagons (kind "hexagon": the centre and the count of each), circles and 3D bars;
  `get_scales_drawn()` names a square-root scale "square root". `say_what_it_shows()` describes the new words, a
  broken axis and the other scales.
- `interactive=True` on `sdata.chart()` and `table.start_chart()`, and plotly names (`write_html`, `iplot`,
  `hovertemplate`, `rangeslider`, `hexbin`, `bar3d` ...) point to the simplydata words. `sdata.show_packages_used()`
  lists plotly when a web page was made.

### Fixed: charts phase, batch 3 (after the independent review)

- `show_when_pointing()` shows a row's columns only on marks that are single rows of the table (dots drawn from the
  rows, and lines with one row at each point), decided from the step that drew the mark; averages, bars, error
  bars, bands, fitted lines, histograms, densities and hexagons say what they are ("the average of several rows")
  and are never matched to a row by their value. A note says so. Groups with the same x and y keep their own rows.
- A second scale (`add_second_x` / `add_second_y`, with `formula=` or a column) is drawn on the web page: it
  overlays its panel's axis on the far side, and its marks use the panel's other axis.
- `break_between_y` refuses a break that would hide drawn values (it says how many, and their range) or leave a part
  empty, checked on the drawn data; `get_numbers_drawn()` lists each point once, on the part that shows it (panel 1
  the upper part, panel 2 the lower).
- What a web page cannot draw is said in a note. Pages fit the window (no sideways scrolling; a chart wider than
  1100 pixels is drawn smaller, text with it); legends are held at matplotlib's corner and show patterns;
  contour maps get a banded colour bar; the animation's buttons sit beside the slider; 3D charts keep their tick
  words inside the scene.
- `show_in_web_page()` in a notebook says once that the page holds the numbers; from a script it says where the
  temporary file is and that it holds the data.
- `get_numbers_drawn()` reads a second y-axis's marks on its panel's x-axis (names of groups, not their places), and
  `get_text_drawn()` lists no tick words of an axis that is not drawn.
- Found by the reliability study of the charts phase: `get_numbers_drawn()` read a band drawn sideways
  (`fill_betweenx`: violins, the density curve on the right of `draw_side_histograms`) with x and y swapped, so the
  web page left the violin bodies out. Each row is now its place on y and its ends along x.
- Web pages: a log axis draws grid lines only where the picture does (at its big ticks, not at the small ticks it
  writes words at); a legend that only just misses a mark in the picture goes outside the chart on the right, the
  page made wider for it, so it covers nothing in a narrow window; marks are given to plotly in matplotlib's
  drawing order, so a violin's box shows over its body.

### Added: the reliability study of the charts phase

- `validation/cases_underneath_charts_2.py`: 56 cases on real data (mtcars, iris, warpbreaks, Seatbelts, Lake Huron,
  birthwt, airquality, the Stanford heart transplant data) for the new chart words and options of batches 1 to 3,
  each against the same chart drawn with matplotlib, seaborn or pandas and, where it is plain base R, against R;
  the web-page words are checked on the plotly figure's own data.

### Changed: Polars and pyarrow are now installed with simplydata (decided by Manish 2026-11-25)

- Polars and pyarrow are now installed with simplydata (`polars>=1.43.2,<3`, `pyarrow>=19,<27`), because several
  table words run on Polars for every table so that pandas and Polars tables give one answer (`round_dates_in`,
  `matches_pattern=` on rows, `replace_text_in(capitals_matter=False)`, `join_with(match="nearest before")`).
  `pip install "simplydata[fast]"` still works and adds nothing more. The messages that asked to install
  `simplydata[fast]` are gone. The lowest Polars is now 1.43.2: older ones stop with a panic in
  `turn_into_dates(written_like=)` for written-out month names.

### Fixed

- One set of time zone rules on every computer (decided by Manish 2026-11-26). pandas reads the clock of a column
  with a time zone through the computer's copy of the world time zone data, Polars through its own; the copies can
  differ before 1970 (Debian and Ubuntu keep Norway's summer time of 1959 to 1965, the main IANA data does not), so
  on Linux 1 July 1959 00:00 in Oslo was month 7 on a pandas table and month 6 on a Polars table. Every date step on
  a column with a time zone now reads and writes its clock through Polars on both engines: the parts of a date,
  `turn_into_text`, `add_column(plus=, minus=, by_subtracting=, counted_in=)`, joined text, `every=`, cross-table
  column names, `keep_rows_where` on dates, `change_time_zone_in(recorded_in=)`, `describe_columns`,
  `add_missing_dates`, `round_dates_in` and Excel and Stata files. Local clock times before 1970 follow the main
  world time-zone data (IANA), the same on every computer; the moments themselves never change. For example,
  Norway's summer time of 1959-65 is not included (it is only in IANA's "backzone" file, which Ubuntu and R on Linux
  include). The reliability study compares pandas through Python's zoneinfo read from the tzdata package (IANA's main
  data) on every system, so `tzdata` (2023.3 to 2027) joins the `test` extra. Where R reads a copy with the
  backzone, its Oslo numbers are listed as an explained difference, only when R given IANA's main data gives simplydata's numbers.
- Time zone names with `_`, `-`, `+` or digits (`America/New_York`, `America/Port-au-Prince`, `Etc/GMT+5`,
  `America/Argentina/Buenos_Aires`) on a pandas table. narwhals (2.27 to 2.29) reads the kind of a pandas column from
  its written dtype with a pattern that takes only letters and `/` in the zone, so such a column was `Unknown`: every
  date word on a pandas table (the parts of a date, days between, `plus=`, `round_dates_in`, `change_time_zone_in`,
  `keep_rows_where`, `every=`, `join_with(match="nearest")`, `add_missing_dates` ...) stopped or called the column
  "other values". simplydata now widens that one narwhals pattern when it is loaded, and only while narwhals needs it;
  the date steps still run in pandas' and Polars' own methods. Polars tables were not affected.
- `every="month"` (and `"quarter"`, `"year"`) on a pandas column with a time zone east of UTC: narwhals truncated
  pandas dates on the UTC clock, so 1 July 00:00 in Oslo was counted in June. It is now truncated by Polars
  `dt.truncate` on the column's own clock, as on a Polars table.
- `keep_rows_where` (`is_after=`, `is_before=`, `is_between=`, a written condition such as `"t > '2024-01-01'"`) on a
  column with a time zone stopped on both engines (a time without a zone cannot be compared with one). A date or time
  given there is now read on the column's clock (pandas `Timestamp.tz_localize`); one that never happens or happens
  twice there stops with a message.
- `round_dates_in`: on a pandas table the sentence counted empty cells as changed.
- `table.save()` with a column that has a time zone: a .csv, .tsv, .csv.gz or .tsv.gz file gets the times with
  their UTC offset in one layout on both engines (`2024-07-01 23:45:00-04:00`; Polars wrote
  `2024-07-01T23:45:00.000000-0400`), and `sdata.table()` now reads a column of such times back as the same
  moments on the UTC clock (pandas `to_datetime(format="ISO8601", utc=True)`); a note names the zone that a text
  file cannot keep. Excel (.xlsx, also `in_sheet=`) and Stata (.dta) have no time zones, and pandas stopped with
  its own error: the clock times of the zone are now saved (pandas `dt.tz_localize(None)`), with a note naming
  the zone and how to save UTC times instead.
- `sdata.table(..., fast=True)`: a blank line in a CSV or TSV file is now skipped, as without `fast=True`. Polars
  made it a row of empty cells, the same row as a line of empty fields (`,,`), which both engines keep; Polars
  cannot tell the two apart, so a file with a row of only empty cells is read by pandas (`skip_blank_lines`) and
  then handed to Polars.

### Added: tables phase, batch 2 (ranks 16-30 of the tables proposal; approved by Manish 2026-11-25)

- `sdata.table(..., columns=[...], column_names=[...], skip_lines_starting_with="#")`: read only some columns (in the
  order given), name the columns of a file without a header line, and skip a logger's note lines (pandas `usecols=`,
  `header=None, names=`, `comment=`; Polars `columns=`, `new_columns=`, `comment_prefix=`). `usecols=`, `names=`,
  `comment=` and friends run with a note once; `header=` points to `column_names=`.
- `capitals_matter=False` on `keep_rows_where`, `remove_rows_where`, `replace_values_in`, `replace_text_in`,
  `find_percent_of_rows_where`, `keep_columns` and `remove_columns`; `matches_pattern=` on `keep_rows_where` and
  `remove_rows_where`. `ignore_case=`, `case=` and `regex=` point to them.
- Durations: `add_column("check_on", from_column="date", plus="1 month")` (also "30 days", "2 weeks", "1 year",
  "12 hours", and `minus=`); `add_column(..., by_subtracting=[end, start], counted_in="hours")`.
- `written_like="31.12.2026"` on `turn_into_text` and `turn_into_dates`: an example date instead of % codes.
- `table.add_missing_combinations_of("station", "depth_m")`, `table.count_columns()`,
  `table.rename_columns({...})` / `rename_columns(add_in_front="w_")`, `table.round_dates_in("date",
  down_to="month")` (`up_to=`, `to_the=`), `table.change_time_zone_in("time", to="UTC", recorded_in="Europe/Oslo")`,
  `table.spread_into_yes_no_columns("fruit")` (empty cells get a column "fruit: (empty)" on both engines),
  `table.fill_empty_cells_from(other, using="id")`.
- `with_totals=True` on `count_rows`, `find_total_of` and `find_average_of` cross tables (a "(total)" row and column; rows with an empty key count in them, unlike pandas margins); `fill_empty_cells_in(...,
  from_column=)`; new `part=` values on `add_column_with_part_of_date` ("date", "time", "second", "is weekend", "days
  in month", "is month end", "is leap year", "year and month"); `add_rank_column(..., for_each_group_in=,
  when_tied=)`; `add_group_column(..., into_equal_groups=4)`.
- One rule on both engines where pandas and Polars differ: `capitals_matter=False` compares after pandas `str.casefold()`; `matches_pattern=` on rows, `round_dates_in` and `replace_text_in(capitals_matter=False)` run through Polars; `into_equal_groups=` through pandas `qcut`.
- Other names: `shape` points to count_rows and count_columns, `crosstab` to count_rows(across=) first, `complete`
  to add_missing_combinations_of and add_missing_dates; get_dummies, tz_convert, combine_first, qcut, strftime ...
  point to the new words.

### Added: tables phase, batch 1 (the 15 jobs a messy table needs most; approved by Manish 2026-11-25)

- `sdata.table("lab.csv", read_as_text=["sample_id"])` keeps columns as text, exactly as typed: 007 stays 007 and a
  lab code such as 3-12 stays text (pandas `read_csv(dtype=)`, Polars `schema_overrides=`). pandas' `dtype=` and
  Polars' `schema_overrides=` (and R's `col_types=`, `colClasses=`) run as `read_as_text=` with a note once when
  every type in them is text.
- `join_with`: `using={"name": "student"}` pairs differently named columns; `keep="all rows from the other table"`
  (the right join); `check_that="each row has one match"` (or "each key appears once in both", "each key appears
  once here") runs pandas' and Polars' own `validate=` and names the repeated keys before anything is joined;
  `with_match_column=True` adds a column "found in" ("both", "this table only", "other table only").
  `how="left"` and friends run as `keep=` with a note once; `left_on=`, `right_on=`, `validate=` and `indicator=`
  point to the simplydata way and never run.
- `table.keep_rows_found_in(other, using=)` and `table.remove_rows_found_in(other, using=)`: semi and anti joins.
- `table.clean_column_names()`: "Max Temp (°C)" becomes max_temp_c (the R janitor rule; pH becomes ph).
- `table.remove_rows_that_are_all_empty()` and `table.remove_columns_that_are_all_empty()`.
- `table.show_duplicate_rows(columns=)` shows every copy with its row number; `remove_duplicate_rows(keep="last")`
  and `keep="none"`.
- `table.add_row_summary_column(name, columns=, show=)`: the average (total, median, ...) across the columns of
  each row.
- `spread_into_columns(..., show="total")` combines rows that would fill the same cell; without `show=` the word
  stops and names the repeated pairs. A pair that never appears stays an empty cell.
- `keep_first_rows`, `keep_last_rows` and `keep_rows_by_position` take `for_each_group_in=`.
- `table.turn_into_categories(column, in_order=[...])`: sorting, group summaries and charts follow the order; a
  value not in the list stops the word with its name.
- `change_column(..., in_rows_where="marks >= 50")`, and `in_rows_where=` on `replace_values_in` and
  `fill_empty_cells_in`: only the rows that meet the condition change.
- `table.keep_groups_where("average(marks) >= 50", for_each_group_in=)` and `remove_groups_where`.
- `table.add_running_column(name, from_column=, show="total")` and `table.add_row_number_column(name,
  for_each_group_in=, sorted_by=)`.
- `table.split_into_rows("genes", separator=";")`.
- New practice tables from one made-up fjord cruise, messy on purpose: `fjord_samples`, `fjord_lab`,
  `fjord_stations`, `fjord_logger` (docs/make_fjord_tables.py), and lesson 37, "Tables: a messy file from a fjord
  cruise". Each new word has a "same underneath" entry (pandas and Polars) and its basis in
  docs/how_simplydata_chooses.md; other names from pandas, Polars and R (semi_join, explode, cumsum, rowMeans,
  factor, clean_names ...) point to the new words.

### Added: tables phase, batch 3 (ranks 31-44 of the proposal; approved by Manish 2026-11-25)

- `table.add_zeros_in_front_of("sample_id", to_length=3)`: "7" becomes "007" (pandas and Polars `str.zfill`);
  longer texts are never cut.
- `find_summary_of(show=["first", "last"])`: the first and last filled value in the order of the rows; with
  `every="month"`, `show=["first", "biggest", "smallest", "last"]` gives open, high, low and close.
- `sort_by("class", "marks", biggest_first=[False, True])`: a direction for each column. Polars' `descending=`
  runs as `biggest_first=`; pandas' `ascending=` (the opposite) points and never runs.
- `gather_into_rows(starts_with="pain_week_", ...)`, and `ends_with=`, `matches_pattern=`: the columns chosen by
  their names, as in `keep_columns`.
- `table.move_columns("marks", to="start")` (or `to="end"`, `after="name"`).
- `table.show_rows_with_empty_cells_in(columns=)`: the rows with a hole, with their row numbers.
- `join_with(rain, using="date", match="nearest before", within="2 days")` (pandas `merge_asof`, Polars
  `join_asof`; also "nearest after" and "nearest"), and `join_with(other, keep="every combination")` (a cross
  join).
- `table.show_differences_from(other)` (pandas `compare`) and `table.check_if_same_as(other)` (pandas and Polars
  `equals`, kinds too).
- File types by name: read .csv.gz, .tsv.gz, .zip (one CSV inside), .feather and .arrow, .jsonl and .ndjson, .xml,
  .sas7bdat, and the databases .sqlite, .db and .duckdb (`sdata.table("lab.sqlite", table_name="samples")`); save
  .csv.gz, .tsv.gz, .feather, .jsonl, .dta and .html, and one table of a database file with
  `table.save("results.sqlite", in_table="river")`, which replaces that table and keeps the others (the mirror of
  `in_sheet=`).
- `table.run_sql("SELECT ... FROM data ...")` and `sdata.run_sql("SELECT ... FROM 'river/*.parquet' ...")`: SQL
  through DuckDB, a new optional extra (`pip install "simplydata[sql]"`); without DuckDB both words stop with the
  install line. For sensitive data, DuckDB is opened with no extensions installed or loaded on their own (so it
  cannot read web or cloud addresses), its settings locked and only one SELECT allowed (checked by DuckDB's own
  parser); a query naming any scheme:// address but file:// (https://, s3://, adl:// ...) is refused before DuckDB
  sees it, and a query on a table cannot open files.
- `tables = table.make_one_table_for_each_group_in("station")`: one table for each group, `tables["Station A"]`.
- Formula functions `length(name)` and `count_text(genes, ";")` (pandas `str.len`, `str.count`; Polars
  `len_chars`, `count_matches`); `length()` works in conditions too.
- `table.as_list()`: one dict per row, for plain Python.
- Each new word and option has a "same underneath" entry (pandas and Polars, or DuckDB, sqlite3) and its basis;
  other names (zfill, relocate, compare, equals, merge_asof, cross_join, partition_by, to_dicts, to_sql, sqldf ...)
  point to them.

### Changed: a front door for new users

- New motto: "Learn basic Python, and simplydata takes you from your first table to sound statistics, in plain
  words, with its results checked against the field's standard tools." It replaces the old one in the README,
  pyproject, CITATION.cff, CONTRIBUTING.md, the package docstring and the title pages of the manual, dictionary
  and 30-day guide.
- A tagline under it, in bold italics, in the README's first screen, on the manual's title page and on the
  30-day guide's front page: ***Easy to do, and you know why you're doing it.***
- The second line says "safe for sensitive data" (was "patient data"), and so do the README's question on it and
  the issue form.
- The README now opens with who it is for, install, a quick start with its real output and where to go next,
  then questions new users ask (why not pandas or R, why not ChatGPT, jamovi or JASP, sensitive data, R). The long
  lists (packages, tasks, fields, lessons, examples by area) moved to
  [docs/what_simplydata_handles.md](docs/what_simplydata_handles.md); the tests check them there.
- The README says why the names are long (you read them more than you type them, you can guess them, and the
  editor completes them), shows three tested "same underneath" pairs side by side, and recommends VS Code or
  Jupyter with a few setup steps; so do the manual's "Install and first steps" and day 1 of the 30 days.
- The 30 days have a new order. Both tracks open a real practice table on day 1 or 2 and test a first difference
  by day 4 (Python track) or day 6 (beginner track); charts are woven in on four days. Models are split over two
  days (Python) or three (beginner), survival curves have a day of their own, and fitting and distributions have
  one day each. Patterns across many columns (lesson 17) and planning a study (lesson 18, example 3) are two
  optional extra days, 31 and 32, opened only with `sdata.show_day(31)` and `sdata.show_day(32)`.
- Progress files of the old order are moved to the new one the first time they are read, with a one-time note: a
  new day is ticked when its lessons were all done before, `sdata.show_today()` carries on with the first day not
  done, and a finished course stays finished. New progress files say which order they follow (`"course": 2`), and
  remember the days passed over with `show_today(follow_calendar=True)`.

### New: easier for new users

- A note when rows repeat one person: when a test or model word (compare_averages_of, compare_spreads_of,
  find_correlation_between, explain, fit_line and the like) runs on a table where an ID column repeats, such as
  "name" in the marks table, one line after the result says so and names the ways out (`matched_by=`,
  `grouped_by=`, `compare_matched_columns`, one row per person). It counts different values only, never changes the
  method and never refuses. An ID column is one named like an ID ("name", "subject", "patient_id", "Sample ID" ...)
  with at least 4 different values, or a column of codes ("P01", "S12") with at least 10 values in 2 to 10 rows
  each; columns the call uses, and calls with matched_by= or grouped_by=, get no note.
- `table.make_copy()` gives an independent copy that keeps the steps so far (pandas `df.copy()`, Polars
  `df.clone()`); `copy.copy(table)` and `copy.deepcopy(table)` do the same. `copy`, `clone`, `deepcopy` and
  `duplicate` point to it.
- `table.count_empty_cells_in("OD600")` and `table.count_empty_cells_in(["a", "b"])` count the empty cells of those
  columns; with no column it counts every column as before, and `show="patterns"` takes the columns too.
- Charts whose `colour=` can be a column (draw_bars, draw_dots, draw_boxes, draw_survival_curves and 16 more) take
  `for_each_group_in=` for the same thing, as the table words do, with a note once; seaborn's `hue=` works too.
- Option names from other tools work with a note once: `on=` and `by=` on `join_with` (its `using=`); `by=`,
  `groupby=` and `group_by=` on every word with `for_each_group_in=`; `random_state=` on every word with
  `with_seed=`; `subset=` on `remove_duplicate_rows` (its `columns=`).

### Changed: copies, not shared tables (check your code)

- `table.as_pandas()` and `table.as_polars()` give a copy: changing it no longer changes the simplydata table, and
  later steps on the table no longer change it (as `nums.as_numpy()` already did). `sdata.table(df)` copies `df`, so
  changing `df` afterwards leaves the table as it was. Under pandas 3 the copy costs nothing until one of them
  changes (copy-on-write).

### New: name completion in editors

- simplydata ships a `py.typed` marker, and every step that gives back the same table, chart or numbers says so in
  its type hints, so VS Code (Pylance) and Jupyter (Jedi) complete `t.keep...` after `t = sdata.table(...)`, and
  chained steps such as `t.keep_rows_where(...).sort_by(...)`. `sdata.get_example()`, `start_chart()`,
  `get_column()`, `turn_into_table()` and `sdata.distribution()` say what they give back. Type hints only: nothing
  runs differently. A test checks the completion with Jedi.

### Changed: reshaping words renamed, and one new word (check your code)

- `table.turn_rows_into_columns` is now `table.spread_into_columns(names_from=..., values_from=...)`, and
  `table.turn_columns_into_rows` is now `table.gather_into_rows(columns, names_to=..., values_to=...)`. The options
  are unchanged; the old names keep working for one release and print a one-line note with the new name.
- `spread_into_columns` adds a note when the new columns get empty cells because another column differs between
  rows that would otherwise merge (hours in the marks table), naming that column and saying how to keep only the
  columns you need.
- New: `table.swap_rows_and_columns()` flips the whole table (pandas `set_index(first).T`; a Polars table goes
  through pandas and back). The first column names the new columns when it holds text with no repeat and no empty
  cell; otherwise they are numbered "1", "2" ... and a note says why. `transpose`, `T` and `t` point to it.

### Fixed: lessons that treated repeated rows as independent

- The marks table has each child three times (one row per subject). Lesson 14 compared the classes on all 54 rows
  and the subjects with Kruskal-Wallis, as if the rows were 54 children. The classes are now compared on one average
  per child (`find_average_of(..., for_each_group_in=["class", "name"])`) or on one subject, and the subjects within
  each child (`compare_matched_columns`, the Friedman test). The lesson says why in a plain sentence. Lessons 12,
  15 and 19, the 30-day guide and the examples and docstrings of the test words do the same.
- The school examples (pupils in 12 schools) that fit ordinary models now say that the p-values are a little too
  small without `grouped_by="school"`.

### Fixed: clearer messages

- `table["marks"]` after a step that took the column away names that step and says `table.undo()`; every
  "no column" message lists the columns there are.
- `table.count_empty_cells_in(show="OD600")` says show= takes only "patterns" and how to count that column,
  instead of `does not know show="OD600"` (a column in the first place is now counted, see above).
- When R does not start, the message says whether R was not found, whether R_HOME points to a folder without R, or
  that R is installed but did not start from Python (with what to try), instead of rpy2's own error.
- `compare_to_truth` without R: the Method line says the likelihood ratios were not computed, and their rows say so,
  instead of naming R epiR as if it had run.
- `remove_duplicate_rows()` that removes nothing says so, and names the columns in which rows that are otherwise the
  same differ.
- Holm's, Bonferroni's, Tukey's and Dunnett's adjustments keep the chance of any false alarm "at most 5 %" (it said
  "stays at 5 %").

### New: several tables in one Excel file

- `table.save("results.xlsx", in_sheet="cleaned")` saves the table as one sheet and keeps the other sheets of the
  file (pandas `ExcelWriter(mode="a", if_sheet_exists="replace")` with openpyxl). A sheet of the same name is
  replaced, and simplydata says so; a file that does not exist is made. Sheet names follow Excel's rules (at most 31
  characters, none of `: \ / ? * [ ]`, no apostrophe at the start or end, not `History`, and the same name in other
  capitals counts as the same sheet). Only .xlsx files have sheets. `sheet=` reads a sheet, `in_sheet=` saves one; `sheet_name=` (pandas) and `sheetName=` (R openxlsx)
  point to `in_sheet=`. Without `in_sheet=`, saving replaces the whole file, as before.
- `sdata.table("results.xlsx", sheet="all")`: when the sheets do not have the same columns, the message still lists
  the differing columns and now gives a line to copy for each sheet, such as
  `patients = sdata.table("study.xlsx", sheet="patients")`.

### New: three numbers given back instead of only printed

- `table.add_correspondence_axes(..., show="numbers")` also gives each axis's eigenvalue (`CA1 eigenvalue`) and the
  `total inertia`, as R vegan gives them (`summary(eigenvals())`, `tot.chi`). On vegan's varespec: 0.5249 and
  0.3568 of 2.083, as Oksanen's vegan tutorial prints. For text columns (MCA) the table gains the total adjusted
  inertia (ca::mjca `inertia.t`).
- `table.find_correlation_between("a", "b", allowing_for="c", show="result table")`: the partial correlation as a
  one-row table: r, its statistic (t, or z for Kendall), the p-value and the rows, from R `ppcor::pcor.test()`.
  `show="result table"` no longer refuses `allowing_for=`.
- `chart.trade_off_curve(...)`: `chart.get_numbers_drawn()` now gives the best cut-off (Youden's index, R
  `pROC::coords(roc, "best")`) in the `value` column of the marked dot, whose `y` is the sensitivity there.

### Changed: `sdata.get_example(name)` gives back a simplydata table (check your 0.2.x code)

- `sdata.get_example("marks")` now gives back a simplydata table, as `get_example(name, from_r_package=)` already
  did, so every table word works on it at once: `sdata.get_example("marks").count_rows()`. Up to simplydata 0.2.x it
  gave back a pandas DataFrame. `sdata.table(sdata.get_example("marks"))` and `sdata.chart(sdata.get_example("marks"))`
  still work as before. Code that used pandas on it, such as `sdata.get_example("marks")["marks"]` or
  `.groupby(...)`, needs simplydata words now (`table.get_column("marks")`, `table.find_average_of(...)`), or, for
  another package, `table.as_pandas()`.
- The "same underneath" boxes of the manual read the practice table from its file with the package itself
  (`pd.read_csv("marks.csv")`); `sdata.get_example("marks").save("marks.csv")` writes that file.

### Fixed: eleven differences found while writing the Underneath entries and by the reference notebooks

- `table.join_with` on a Polars table gave the rows in no fixed order (Polars joins without `maintain_order`). The
  rows now come in the order pandas `merge()` gives on a pandas table: this table's rows in order, each followed by
  its matches in the other table's order; with `keep="all rows from both"` sorted by `using=`. "matching rows" on
  c, a, b, a, z came back b, a, a, a, a, c; now c, a, a, b, a, a, as on pandas.
- `describe_columns` wrote 62.001 as "62.0" (it looked for a whole number before rounding to 2 places); now "62".
- `sdata.compare_rates` and `sdata.compare_risks` said they compared against "the first in sorted order, as R", but
  used the first group of `names=`. They keep that order, which is what R does with counts given as lists
  (`poisson.test()`, `prop.test()` take them in the order given), and now say so: "the first given". The table
  words still sort the groups, as R sorts factor levels.
- `dist.find_middle_range` lost digits near 100 %: the top end was worked out as the value with 1 - tail below it.
  It is now SciPy's `isf(tail)` (R `lower.tail = FALSE`). Normal, 99.99999999 %: 6.4669510747 before, 6.4669511822
  now (= SciPy and R).
- `nums.remove_each_frequency_that(is_equal_to=..., and_multiples=True)` also removed the average (SciPy `iircomb`
  puts a notch at frequency 0 too). It is now one SciPy `iirnotch` at the frequency and at each multiple below half
  the readings per unit of time; the average stays. A signal around 5 came back around 0.012 before, 5.0001 now.
  `sdata.frequency_filter(remove_at=..., and_multiples=True)` changed the same way.
- `chart.spectrum` labelled the 3 biggest values, which can sit on one broad peak, while the sentence of
  `find_spectrum_of` named the strongest peaks. The chart now labels the same peaks as the sentence.
- `chart.show()` left one pyplot figure open after each call. It is now closed once `show()` has finished with it
  (in notebooks with a live window, such as `%matplotlib widget`, the window stays open).
- `round_numbers_in` on a Polars table rounded halves away from zero on Polars before 1.29 (2.5 to 3, 0.125 to 0.13),
  but to the even neighbour (2.5 to 2) on pandas and newer Polars. simplydata[fast] now needs `polars>=1.29`, and an
  older Polars gets a message instead of other numbers.
- `sdata.find_inverse_fourier_transform` trusted the number of readings it stored even after rows of the table were
  removed or reordered, and SciPy quietly padded or cut them. It now refuses with a message; setting the real and
  imaginary parts of some frequencies to 0 still works.
- `compare_each_pair_of(test_method="dunn")`: R FSA's own Holm adjustment leaves out Holm's running maximum, so on
  InsectSprays B - F got 0.926028 where R `p.adjust()` and PMCMRplus give 1 (A25). The adjustment now comes from R
  `p.adjust(method = "holm")`.
- `fit_formula(test_method="trust region")` and `"dogbox"` stopped a little short of the minimum after the A21 change,
  so some standard errors lost digits: NIST Thurber (start 2) 5.8 digits, MGH09 b2 and b4 5.8 to 6.0, ENSO b6 5.9
  (A26). SciPy's stopping rules are now 1e-15: Thurber 6.7, MGH09 7.2, ENSO 6.5, and nothing else of the 27 NIST
  problems got worse (Misra1a, Kirby2 and Hahn1 keep their gains).
- `round_numbers_in` with a negative number of places (tens, hundreds) did the rounding itself (divide, round,
  multiply). It is now pandas `round(-1)`; Polars rounds to decimal places only, so on a Polars table the tens come
  from NumPy's round, the one pandas uses: the same numbers on both.
- `find_spectrum_of` and `nums.find_spectrum` no longer give the "share of variance (%)" column or the "holds 68 % of
  the variance" in the sentence: that share was simplydata's own arithmetic. The powers (SciPy) are unchanged; with
  the periodogram, the powers times the frequency step still add up to the variance.
- `dist.find_middle_range(99.99999999)` printed "The middle 100 %"; it now prints the percent as given.
- The method line of a notch or peak filter read "as R SciPy signal.iirnotch"; it now says what SciPy runs.
### Fixed: closer agreement with certified values, and data licences

- `explain` takes the standard errors of a least-squares model as R `summary.lm()` does, from the QR factor
  (inv(R) inv(R)', R's chol2inv, done with NumPy and LAPACK), not statsmodels' inv(R'R): on NIST Longley they now agree with the certified values to 12.6 to
  14.2 digits (before: 7.97 to 9.42).
- `fit_curve` (polynomials) is unchanged. On NIST Wampler1, 3, 4 and 5 it agrees with the certified values to about
  7 to 9 digits, depending on the computer's linear-algebra library (NIST asks 9); no existing least-squares routine tried (LAPACK gelsd, gelsy and gelss through SciPy,
  NumPy's QR, NumPy's Polynomial.fit) does better on all of them without losing digits on Filip. The reliability study
  now lists these numbers as explained differences (a precision limit), with the reason, and adds Wampler1 to 5.
- `compare_risks(show="attributable fractions")` no longer calls its intervals "Wald": they are the ones epiR gives
  for one table (the score interval of the risk ratio; the exact intervals of the two risks), and the printout says so.
- The power for two percents (`find_chance_of_finding(percents=)` and the "power with that many" of
  `find_how_many_needed(percents=)`) is now R `power.prop.test()`'s default (strict = FALSE): 0.7401659 on R's help
  example, where it gave 0.7401672.
- `combine_studies` (REML, Paule-Mandel), `fit_dose_response` and `find_return_levels_of(values_above=)` ask metafor,
  drc and extRemes for a tighter stopping rule, so their fits converge (Paule-Mandel tau-squared of the BCG trials:
  0.3180685, where metafor's default stopped at 0.3180937); the methods are the same.
- Every practice table is now made up. `job_search`, `bcg`, `passive_smoking`, `ability_tests`, `sea_levels`,
  `sampled_schools`, `job_training` and `drug_levels` keep the columns and size of the real studies they copied, but
  their values are drawn with a fixed seed by `docs/make_job_search.py` and `docs/make_practice_tables.py`, with
  effects built in that the lessons recover; the lessons' answers are updated. simplydata was tested on the real data,
  which it no longer ships: the tests and the reliability study read them from the installed R packages (metadat,
  lavaan, ismev, survey, MatchIt, mediation), and the Schütz et al. (2014) reference datasets from a local file named
  by `SIMPLYDATA_SCHUTZ2014_FILE` (DATA_LICENSES.md).
- The reliability study no longer stores copies of data from GPL or LGPL R packages; it reads them from the installed
  R packages (`validation/r_data.py`). New `DATA_LICENSES.md` lists every table with its source, citation and licence.
- Reliability study: Monte Carlo checks against another generator now allow 4 Monte Carlo standard errors worked out
  for each check (before, 2 to 6 % of the value), with a same-seed exact check next to them; references read from
  rounded printouts are taken at full precision; the GEV, generalised Pareto, drc and metafor references are run to
  convergence. New NIST cases: Longley and Wampler1 to Wampler5. The report counts "explained differences" (a stated
  precision limit) apart from passes and failures.

### Fixed: one-column CSV files were split at a letter (check your one-column files)

- `sdata.table("file.csv")` on a CSV or text file with **one column** could split it at a letter: simplydata let
  pandas guess the separator, and it could pick a letter of the column name, so a column `species` came back as
  columns such as `sp` and `cies`, and `difference` as `diff`, `r`, `nc` (simplydata 0.2.x). If you read one-column
  files with simplydata 0.2.x without `separator=`, read them again. Now simplydata guesses only a comma, semicolon,
  tab or bar (never a letter, digit or other sign); a file with none of them is read as one column. When it guesses,
  it prints one line: `Read "file.csv" with "," between the columns (guessed). To be sure, give separator=",".`
  `separator=` stays the safe way in (`","`, `";"`, `"tab"`, `"|"`, `"space"`): give it when you know it, especially
  for a file with one column. Values lined up with spaces are no longer guessed: give `separator="space"`.

### Fixed: four numbers that differed from their reference

- `explain(..., table_of_tests="in order")`: the p-values are now taken on the full model's residual degrees of
  freedom, as R `anova()` does (statsmodels `anova_lm(typ=1)` on one fit). On `carData::Moore`,
  `conformity ~ fcategory * partner.status`: partner.status p 0.0027934 before (41 df), 0.0028742 now (39 df, =
  R). The F values and sums of squares were already right; types 2 and 3 are unchanged.
- `fit_formula(..., test_method="trust region")` and `"dogbox"`: central differences with a step relative to each
  value (SciPy `jac="3-point"`, `diff_step`), so a small value such as 1e-7 is no longer stepped by 1.5e-8. NIST
  Misra1a standard errors agree to 9.9 digits (4.6 before), Kirby2 to 7.8 (3.1), Hahn1 to 8.5 (0.4). The default
  (Levenberg-Marquardt) is unchanged.
- `compare_forecasts_for` and `forecast(check_on_last=)`: MASE is now scaled by the in-sample error of the same
  season last time, as the printout says: the held-back readings go to R `forecast::accuracy()` as a seasonal `ts`.
  co2, exponential smoothing, last 12: 0.278 before, 0.234 now (= R). With `repeats_every=` the MASE numbers
  change; MAE, RMSE and MAPE do not.
- Savitzky-Golay smoothing (`add_smoothed_column`, `nums.smooth`) refused `of_degree=`, the option its help names, so
  the degree could not be set. `of_degree=` works now; `degree=` is an old name with a note.

### New: six words and options, and four more options

- `chart.get_numbers_drawn()`: a table of the numbers a chart drew (each line, group of dots, set of bars, band,
  stems, error bars, heat map cells, pie slices), read back from matplotlib, for every chart word, page and
  `sdata.draw_all_pairs`.
- `table.show_rows_that_pull_model(...)` now also gives back a table of the rows (or groups) it found.
- `table.check_model_of(..., show="numbers")`: the numbers it prints, as a table (with `test_method="bayesian"`,
  R-hat, effective draws and the predictive check).
- `table.repeat_each_row_by("count")`: one row per thing counted.
- `sdata.get_example("lung", from_r_package="survival")`: a dataset that comes with an installed R package, as a
  table (needs simplydata[r]; nothing is downloaded or installed).
- `table.find_correlation_between("a", "b", show="result table")`: r, its interval, the p-value and the rows as a
  one-row table.
- `table.find_survival_over_time(..., show="median")`: the median time of each group with its 95 % CI, as a table
  (the numbers it prints, as R `print(survfit(...))`).
- `table.fit_formula(...)` gives back a `note` column: "converged" or "did not converge", followed by the warnings
  the fit printed.
- `table.add_nmds(..., show="numbers")`: each row's NMDS coordinates and the stress (vegan::metaMDS) as a table,
  without adding columns.
- `table.add_correspondence_axes(..., show="numbers")`: each row's coordinates and the share of the inertia of each
  axis (vegan::cca, ca::mjca) as a table, without adding columns.

### Fixed: ten differences the reference tests found (A8 to A17)

The reference tests (simplydata_tests, notebooks 18 to 24) ran the words on the examples of their parent packages'
manuals and on real data. These differences are now fixed, or explained where simplydata's answer was right:

- `compare_each_pair_of(test_method="dunn")` with more than three groups put p-values on the wrong pairs (A12). FSA
  lists its pairs in another order than simplydata assumed; each result is now matched to its pair by name. On
  InsectSprays (six sprays) C - B now gets its own p = 5.1e-06, not D - C's 0.586. If you used Dunn's test with four
  or more groups, run it again.
- `compare_counts_of(test_method="barnard")` and `"boschloo"` took the outcome, not the `for_each_group_in=` groups,
  as the two samples (A10). These tests are not symmetric; R Exact fixes the row totals, so it now gets the groups as
  rows. Fisher's twins: Barnard p = 0.000348 (was 0.000280), as R. `sdata.compare_counts()` was right (the rows are the
  samples) and now says so.
- `compare_counts_of(show="cells")` added 0.5 to every cell of a table with an empty cell before working out the
  residuals and expected counts (statsmodels' default). It no longer does, so the residuals are R
  `chisq.test()$stdres` (Agresti's job satisfaction: 0.2096, was 0.0802) (A11).
- Mann-Whitney U with tied values (`compare_averages_of(based_on="ranks")`, `compare_each_pair_of(based_on="ranks")`)
  used the normal approximation; R 4.6.0 made `wilcox.test()` exact with ties below 50 values. That exact p-value now
  comes from R `wilcox.test()` itself (SciPy has none); without R the normal approximation stays and the printout says
  so (A13). InsectSprays C - A after Holm: 1.6e-05 (was 5.1e-04). The Wilcoxon signed-rank test keeps the rule of R
  before 4.6.
- Krippendorff's alpha (`agreement_between(test_method="krippendorff")`) came from R irr, which weights the pairs within
  a row wrongly when three or more raters have no empty cells. It now comes from R icr, which gives Krippendorff's
  published examples (0.743 nominal, 0.849 interval). irr's `anxiety`: 0.1701 (was 0.1631) (A14).
- The ICC of the average of raters with absolute agreement, ICC(A,k), had irr's interval, which does not follow McGraw
  and Wong (1996). Every ICC now comes from R psych `ICC()`: (-0.1266, 0.7451) for irr's `anxiety` (was (-0.1373,
  0.7463)); every other form's numbers are unchanged (A15).
- Spearman's p-value (`find_correlation_between(test_method="spearman")`) was SciPy's t approximation. For fewer than
  1290 rows without ties it is now R `cor.test()`'s default, algorithm AS 89, run in R (without R the t approximation,
  with a note). R's own example: p = 0.0968 (was 0.088) (A9).
- `chart.draw_smooth_line()` fitted every point (LOWESS with delta = 0). It now uses R `lowess()`'s default delta of
  1 % of the x range, and the curve on mtcars is R's to 1e-10 (it differed by up to 5e-4) (A16).
- `find_percentile_of(interval=)`: the help said the quartiles' intervals are R DescTools' exact intervals. They are
  SciPy's Thompson (1936) interval, which splits the chance of missing evenly between the two ends; DescTools picks
  another pair of order statistics away from the median. Both are exact; the help and the printout now say which is
  used (A8). The median's interval is DescTools' `MedianCI()`, as before.
- The smoothing spline with a number for `smoothness=` differs from R `smooth.spline(lambda = )` by about 1e-5. This is
  not about repeated x values: it happens without them too, and SciPy's curve makes the penalised sum a little smaller
  than R's, so the difference is R's rounding. The help now says so (A17).
- New R package: icr (CRAN), for Krippendorff's alpha.

### Changed: one name for choosing the method

- One name for choosing the method: `test_method=` replaces `test=`, `method=`, `rule=` and `methods=` on 57 words,
  and `bayesian=True` becomes `test_method="bayesian"` on 7 words (`prior_width=` stays, with
  `test_method="bayesian"`). `test_method=` chooses the method (the test, estimator or rule) the word uses; each word
  keeps its own choices and its own default, and every printout names the method it used. `sdata.help("test_method=")`
  lists the words. The old names still work and print a one-line note; giving an old name and `test_method=`
  together is refused (`bayesian=False` is simply left out, with the note).
- The values follow one rule: lower case, words separated by spaces, two person names joined by a hyphen.
  `combine_studies` values are now lower case (`"reml"`, `"dersimonian-laird"`, `"paule-mandel"`,
  `"mantel-haenszel"`, `"peto"`; the old spellings are accepted); `find_percentile_of` names its rules with spaces
  (`"median unbiased"`; NumPy's `"median_unbiased"` and R's numbers 1 to 9 are accepted);
  `find_hidden_factors_behind` calls `"ml"` `"maximum likelihood"` (`"ml"` is accepted).
- `compare_each_pair_of(test_method="fisher")` no longer means Fisher's LSD: `"fisher"` is Fisher's exact test, with
  `based_on="percents"`. For Fisher's LSD write `"lsd"` (or `"fisher's lsd"`); the old use gets a message that says so.
- Two options renamed so that they do not look like `test_method=`: the planning words' `test=` (the word whose study
  is planned) is now `for_test=` on `find_how_many_needed` and `find_chance_of_finding`, and `explain`'s
  `test_type=` (the ANOVA table) is now `table_of_tests=`. The old names still work, with a note.
- The second method choices that go together with the main one keep their names: `p_value_by=`, `interval_by=`,
  `linkage=`, `window_shape=`, `search=`, `link=`, `penalty=`, `rotation=`, `zeros_replaced_by=`, `weight_kind=`,
  `empty_cells=` and `band=`.

### New: Bayesian answers (S3d-3)

- `bayesian=True` on `compare_averages_of` (two groups), `compare_before_and_after`, `compare_average_to`,
  `find_correlation_between` (two columns) and `compare_counts_of`: a Bayes factor, said as "the data are 17.3 times
  as likely if the values changed as if they did not", and a 95 % credible interval with its meaning, instead of a
  p-value (R BayesFactor: `ttestBF`, `correlationBF`, `contingencyTableBF(sampleType = "indepMulti", fixedMargin =
  "rows")`, then `posterior()` with 10,000 draws after `set.seed(with_seed)`). `prior_width="medium"` (the default),
  `"wide"`, `"ultrawide"` or a number sets the width of the prior, which is always printed. No p-value and no verdict
  words. The one-column test works on the values minus the number, because BayesFactor's `posterior()` leaves `mu =`
  out (its Bayes factor is the same).
- `explain(..., bayesian=True)`: a Bayesian model from R rstanarm (`stan_glm`, or `stan_glmer` with `grouped_by=`;
  outcome `"numbers"`, `"yes or no"` or `"counts"`), 4 chains of 2000 iterations with `seed = with_seed`. It prints
  the prior (rstanarm's `prior_summary()`), each effect as the posterior median with its 95 % credible interval (odds
  or rate ratios for yes/no and counts), and rank-normalised R-hat and bulk and tail effective draws from the
  posterior package. When R-hat is above 1.01, there are fewer than 400 effective draws or any divergent transition,
  a warning with what to do comes before any estimate. The result table has the columns "R-hat", "effective draws
  (middle)" and "effective draws (tails)".
- `check_model_of(..., bayesian=True)`: the posterior predictive check, the data against 50 sets made up by the
  fitted model (densities for numbers, bars for yes/no and counts, as bayesplot's `pp_check`); `show="prior check"`
  draws the sets made up from the prior alone (`prior_PD = TRUE`).
- rstanarm is a large optional R package (about 400 MB with Stan); its models are compiled when it is installed, so
  nothing is compiled or written while simplydata runs, and simplydata runs the chains one after another
  (`cores = 1`: no worker processes, no sockets).
- Lesson 36 "Bayesian answers: how likely, given the data and the prior"; "more" lines in the lessons on tests and
  on working with a model; other names (`ttestBF`, `correlationBF`, `contingencyTableBF`, `stan_glm`, `stan_glmer`,
  `brm`, `brms`, `pymc`, `bambi`, `pp_check`, `rhat`, `ess`, ...); `rscale=` and `prior_scale=` point to
  `prior_width=`; 8 same-underneath entries, 8 "how simplydata chooses" entries (9 new references, each checked in
  Crossref) and 7 reliability cases on Student's sleep data, mtcars and sleepstudy, with the Bayes factors also
  checked against SciPy versions of the published formulas (Rouder et al. 2009; Gunel and Dickey 1974).

### New: epidemiology and cause and effect (S3d-2)

- `table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", "race", ...])`:
  makes two groups alike in other columns, then compares them. The propensity score (R `glm`), the overlap of the
  scores, the balance table (standardised differences before and after, R `cobalt::bal.tab`, the guide 0.1, never
  p-values), the effect with its interval, and the assumptions it rests on, printed every time.
  `method="weighting"` (the default; R `WeightIt::weightit` and `lm_weightit`, standard errors that allow for the
  estimated weights) or `method="matching"` (R `MatchIt::matchit`, 1:1 nearest neighbour, standard errors clustered
  on the pairs); `match_within=0.2` a caliper in standard deviations of the logit of the score; `effect_for=
  "everyone"` (ATE, the default for weighting) or a group's name (ATT, needed for matching); `show="balance"` or
  `show="propensity scores"`. Checked on lalonde: weighting 224.7 (SE 876), matching 894 (SE 705), as WeightIt and
  MatchIt.
- `explain("depress2", using="treat", through="job_seek", allowing_for=[...])`: causal mediation (statsmodels
  `Mediation`, Imai, Keele and Tingley's quasi-Bayesian algorithm, 1000 simulations, as R `mediation::mediate`): the
  indirect effect, the direct and total effects and the share that goes through, with the assumptions printed.
  `against=` names the starting value of the exposure; a yes or no outcome or mediator gets logistic models.
- `compare_risks(..., show="attributable fractions")`: the attributable fraction among the exposed and in the whole
  population (R `epiR::epi.2by2`), labelled crude; for an exposure that goes with fewer events, the preventable
  fraction among the exposed.
- `rate_of(..., allowing_for="age_band", standard_population="whole table")` (or a table of population sizes):
  directly standardised rates with Fay and Feuer's interval (R `epiR::epi.directadj`, the same numbers as
  `epitools::ageadjust.direct`). `compare_rates(..., allowing_for="age_band", standard_rates=national)`: observed /
  expected (SMR) with its exact Poisson interval (R `epiR::epi.indirectadj`; p-value from R `poisson.test`).
- `compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="period",
  same_within=[0.8, 1.25])`: the 2 x 2 crossover (bioequivalence), the EMA model with all effects fixed on the log
  scale (statsmodels OLS), the ratio of geometric means with its 90 % interval and the within-subject CV; no
  carry-over pre-test. `against=` names the reference formulation. Gives the published answers of the three
  reference datasets of Schütz, Labes and Fuglsang (2014).
- `empty_cells="multiple imputation"` on `explain_survival` (R `coxph` on each filled-in table, pooled by R
  `mice::pool`; the filling uses the event and the Nelson-Aalen hazard, White and Royston 2009) and
  `find_correlation_between` (Fisher's z pooled with Rubin's rules, R `miceadds::micombine.cor`), with `with_seed=`.
  Not added to `compare_averages_of` and `compare_risks`: with two columns, filling one from the other gives on
  average the same answer as leaving the rows out, so `explain()` with other columns is the way.
- New practice tables: `job_training` (lalonde, real), `job_search` (JOBS II, real), `drug_levels` (a real crossover,
  Schütz et al. reference dataset A) and `deaths_by_age` (made up).
- New lesson 35, "Cause and effect from observational data" (a "more" lesson); a "more" line in the risks lesson.
- Other names (`propensity`, `matchit`, `weightit`, `ipw`, `mediation`, `smr`, `ageadjust`, `bioequivalence`,
  `attributable_fraction` ...) point to the new words and options.
- Same-underneath entries, "how simplydata chooses" entries and reliability cases for each: lalonde, JOBS II, dry cat
  food and FLUTD (Willeberg 1977), Down syndrome by birth order (Selvin 2004; epitools as a second package), the
  bioequivalence reference datasets (published ratios and intervals), airquality and lung (against R mice).
- CI installs WeightIt, MatchIt, cobalt, miceadds and epitools from CRAN.
### New: planning an experiment and survey answers (S3d-1)

- `sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, with_seed=1)`: the layout of
  an experiment, every combination of the factors in random order, with the plot to work in and the standard order
  (R `expand.grid()` order). `of_kind="randomised blocks"` (every combination once in each block), `"latin square"`
  (one factor, each level once in every row and column) and `"split plot"` with `whole_plots=` (the factor on whole
  plots). R agricolae, with R's own random number generator (`kinds = "Mersenne-Twister"`) instead of agricolae's
  "Super-Duper", so that `with_seed=` gives the layout an R user gets.
- `sdata.make_random_assignments(how_many=60, groups=["A", "B"], in_blocks_of=[4, 6], for_each_of=["Bergen",
  "Oslo"], with_seed=1)`: a randomisation list in permuted blocks of random sizes, one list for each centre
  (R blockrand, CRAN only). Real block sizes (blockrand counts in multiples of the number of groups); sizes that are
  not a multiple of the number of groups are refused; `groups=3` gives A, B and C. The printout says the last block
  is completed and that the list must be kept from the people who recruit (allocation concealment).
- `keep_random_rows(5, for_each_group_in="site", with_seed=1)`: a stratified random sample (pandas
  `groupby().sample()`), rows kept in table order; a group with too few rows is kept whole, with a note.
  `percent=10` keeps that share of each group (or of the table), at least one row per group.
- `count_empty_cells_in(show="patterns")`: one row for each pattern of empty cells, how many rows have it and how
  many cells it leaves empty (as R `mice::md.pattern()`).
- `count_each(columns=["teaching", "pace"], in_order=["strongly disagree", ..., "strongly agree"])`: answers on a
  scale (Likert items), one row per question with the count and percent of each answer, the percent in the top two
  and the median answer; no averages. `chart.draw_answer_bars(columns=, in_order=)` draws them as diverging bars
  centred on the middle answer (Heiberger and Robbins 2014).
- `table.use_survey_design(weights="weight", strata="school_type", population_sizes="schools_of_type")`: a setting
  that makes `find_average_of`, `find_total_of`, `find_median_of`, `find_percentile_of`, `find_percent_of_rows_where`,
  `count_rows`, `explain`, `compare_averages_of` (two groups) and `compare_counts_of` give answers for the population,
  from R survey (`svymean`, `svytotal`, `svyquantile`, `svyciprop`, `svyby`, `svyglm`, `svyttest`, `svychisq`), with
  intervals on the design's degrees of freedom and `clusters=` for cluster samples. Every printout starts "As a
  survey (...)"; other statistics words refuse while the design is on, and so does a survey word after rows were
  removed (analyse a part with `for_each_group_in=`). `use_survey_design()` turns it off; the table's printout shows
  the setting.
- New practice tables: `sampled_schools` (real: the stratified api sample of the R survey package, Lumley 2010) and
  `course_feedback` (made up: 120 students rate a course on five statements).
- Lesson 34 "Planning an experiment and a survey"; other names (`blockrand`, `expand.grid`, `svydesign`, `svymean`,
  `md.pattern`, `likert` ...) point to the new words; `sdata.help("strata")` now names all three places.
- Same-underneath entries, "how simplydata chooses" entries and reliability cases for each: the api samples (the
  stratified mean 662.29 and the cluster mean 644.17 of Lumley 2010), nhanes (van Buuren and Groothuis-Oudshoorn
  2011), the professional challenges survey (Heiberger and Robbins 2014), and the published properties of permuted
  blocks and Yates' standard order. New R packages: agricolae, blockrand and survey.

### New: small additions to known words (S3c-4)

- `find_percentile_of("price", 90, weights="count")` and `find_median_of("price", weights="count")`: weighted
  percentiles. `weight_kind="frequency"` (the default) repeats each row as often as its whole-number weight and keeps
  `method=`, so weights of 1 change nothing (as R `quantile(rep(x, w))` and `Hmisc::wtd.quantile`);
  `weight_kind="analytic"` is NumPy's weighted inverted CDF (as R `survey::svyquantile(qrule = "math")`). Weights that
  are not whole numbers are refused as frequency weights, with the analytic line to copy.
- `find_correlation_between("hours", "marks", "height", show="covariance")`: the covariance table (pandas
  `DataFrame.cov()`, n - 1, each pair on its own complete rows, as R `cov(use = "pairwise.complete.obs")`), also for
  two columns; the printout says covariances are in the units of the columns multiplied.
- `forecast(..., method="arima", order="automatic")` (also on `compare_forecasts_for` and `chart.forecast`): R
  `forecast::auto.arima` chooses the order and the seasonal order by AICc, trying every order (`stepwise = FALSE,
  approximation = FALSE`) for series of up to 1,000 readings. The printout names the orders chosen and says the
  intervals are a little too narrow because the order was chosen from the data; `seasonal_order=` with
  `order="automatic"` is refused.
- `add_adjusted_p_value_column(method="storey")` (`"q-values"` accepted): Storey's q-values, with the share of true
  nulls (pi0) estimated from the p-values by R `qvalue::qvalue()` (Bioconductor); `method="local fdr"`: each test's
  local false discovery rate, in a column called "local false discovery rate". A note below 100 p-values; a refusal
  that names Benjamini-Hochberg when qvalue cannot estimate pi0. The install message names Bioconductor for qvalue.
- `compare_each_pair_of(..., matched_by="player", test="nemenyi")` and `test="conover"`: Nemenyi's test (no further
  adjustment: its studentized range allows for all pairs) and Conover's test with Holm after Friedman's test, R
  PMCMRplus; the printout notes that mean-rank tests depend on the other groups (Benavoli et al. 2016). Wilcoxon-Holm
  stays the default.
- `compare_each_pair_of("infected", for_each_group_in="age_group", based_on="percents", value="yes")`: the percent of
  each pair of groups, by the 2 x 2 chi-square test with Yates' correction that `compare_counts_of` uses (or
  `test="fisher"`), Holm's adjustment and Newcombe's interval of the difference; the same as R
  `pairwise.prop.test()`.
- New practice table `many_tests` (made up): 2000 genes with their p-values, for q-values.
- "More" lines in lessons 12, 14 and 24; other names (`auto_arima`, `qvalue`, `nemenyi`,
  `pairwise_prop_test`, `weighted_quantile`, `cov` ...) point to the new options.
- Same-underneath entries, "how simplydata chooses" entries and reliability cases for each: Quetelet's chest sizes,
  mtcars, the air passengers (the airline model of Box and Jenkins), Hedenfalk's genes (pi0 0.67, Storey and
  Tibshirani 2003), the rounding-first-base times (Hollander and Wolfe 1973) and Fleiss's smokers.
- CI installs qvalue from Bioconductor (BiocManager, `update = FALSE`).

### New: directions, places and extremes (S3c-3)

- `table.find_average_direction_of("current_direction", full_turn=360)`: the average direction of directions,
  angles or times of day, the resultant length ("close together" or not) and the circular standard deviation
  (SciPy circmean, circstd, circvar, directional_stats). `full_turn=` is required (360, 24, 12, 365 or "radians"),
  because radians read as degrees give a wrong answer without a word.
- `compare_shape_to(..., shape="even around the circle", full_turn=360)` (or `test="rayleigh"`): the Rayleigh test,
  R `circular::rayleigh.test` with the units always given. With `full_turn=`, `shape="uniform"` means the circle too;
  without it, a column named like a direction gets a note.
- `find_autocorrelation_of("zinc", x="east", y="north")`: Moran's I for nearby places, R spdep (1 / distance weights
  between all pairs, row-standardised; `nearest=8` for the 8 nearest; `on_globe=True` for longitude and latitude;
  999 permutations after `with_seed=`). The weights are printed; two rows at one place are refused with the line that
  averages them; longitude and latitude without `on_globe=True` get a note. Mixing it with `sorted_by=` or
  `rows_back=` is refused, with both calls shown.
- `table.find_variogram_of("zinc", x="east", y="north")` and `chart.draw_variogram(...)`: the variogram with a
  spherical, exponential, Gaussian or Matern curve (`of_kind=`), R gstat with its own bins and start values; the
  range said in words for each curve.
- `table.find_return_levels_of("sea_level", once_in=[10, 50, 100], sorted_by="year")`: return levels from yearly
  maxima (GEV), or from every value above a threshold with `values_above=30` and dates in `sorted_by=` (generalised
  Pareto), R extRemes with profile-likelihood intervals; the shape in the extRemes and Coles sign (xi); daily readings
  are refused for block maxima; the extremal index, with a note below 0.7 (no silent declustering).
- `chart.draw_threshold_check(x="rain", between=[10, 30])`: the mean excess and the shape against the threshold
  (R extRemes mrlplot and threshrange.plot), to choose `values_above=`.
- `fit_distribution_to(..., distribution="gev")` and `"generalised pareto"` (`"generalized pareto"`, `"gpd"`): two
  new families, fitted with SciPy and kept in the xi sign (SciPy's genextreme uses c = -xi); d/p/q calls name
  `extRemes::devd` and friends.
- `chart.draw_polar(..., full_turn=360)`: the angles' full turn, and a compass layout (0 at the top, clockwise) with
  `full_turn=` or when the angle column is named like a direction; `degrees=` still works for this release.
- `find_average_of` notes when a column looks like directions, and points to `find_average_direction_of`.
- Practice tables `stations` and `rain` (made up) and `sea_levels` (real: Port Pirie, Coles 2001); lesson 33, "A coastal
  station: currents, neighbours and storms"; same-underneath entries and reliability cases on the turtles and
  intensive-care arrivals (circular), meuse (sp), and Coles's Port Pirie and daily rain (ismev).
- New R packages at run time: circular, spdep with sf, gstat and extRemes; ismev, sp and ape for the checks only.
  Moran's I uses R spdep rather than Python esda/libpysal, which would add about 110 MB of new Python dependencies
  (geopandas, pyproj, shapely, scikit-learn, requests).

### New: how simplydata chooses methods, every default with its published basis

- `docs/how_simplydata_chooses.md` answers a reviewer's question: "simplydata picks the method for the user; how
  does it know which is correct?". It states the five principles simplydata follows (published guidelines first,
  then method comparisons and the method that needs fewer assumptions, then the field's standard software, then
  checks of the data, and openness throughout). For each word and option that chooses a method or setting, it
  gives the default, the alternatives and the option that asks for them, why, the references, and what
  simplydata checks in the data.
- Each default says what kind of basis it has: a published guideline or method comparison, the convention of the
  package named, or simplydata's own starting value (said as such, with the option that changes it).
- Every reference was looked up before it was cited: DOIs in Crossref, the rest at their URL.
- The registry is `src/simplydata/_method_basis.py`, and `docs/make_method_basis.py` writes the document. The
  manual has it as a new last part, "How simplydata chooses methods", and each dictionary entry with a choice
  points to it. A test fails when a "simplydata chooses" line has no basis, when an entry names a word or
  option that no longer exists, or when the document is out of date. No word's behaviour changes.

### Privacy: your data never leaves your computer, checked by tests

- An audit of the whole source found no telemetry, analytics, update checks, crash reports or logging. The only
  network use is `sdata.table("https://...")` with a web address you give; everything else, R included, works
  offline, and files are written only where you ask.
- `r_call()`, simplydata's bridge to R, now refuses R code that names a network, install or file-writing function
  (R does its own networking, out of Python's sight), and R draws into nothing instead of an `Rplots.pdf` file.
- `sdata.table("https://...")` follows a web address on only to another https address (or http from http), never
  from https down to http, to ftp or to a file.
- New `tests/test_privacy.py` scans the source for network code and every R code string for downloads, installs
  and file writing; checks that the list of packages used never holds a value or a column name of your tables;
  and that importing simplydata adds no log file and a script writes only the files it asks for. The whole test
  suite now runs with Python's outgoing network connections and name lookups blocked (`tests/conftest.py`); only
  the tests of reading a web address may reach a local server on 127.0.0.1.
- New README section "Privacy: your data stays on your computer", and `SECURITY.md` with how to report a security
  or privacy problem privately.

### New: `sdata.show_packages_used()`, the packages that did the work and how to cite them

- simplydata now remembers, during a session, every package that did work behind a word that finished without
  an error: Python packages (pandas or Polars, whichever holds the table, narwhals, NumPy, SciPy, statsmodels,
  matplotlib, seaborn ...) and R with each R package it called. Asked for by the owner: "this should happen for
  any package the user uses even for pandas or polars or scipy anything".
- At the end of a script a short list is printed: name, version, language, source (PyPI, conda-forge, CRAN,
  Bioconductor) and a one-line reference. Not in Jupyter or an interactive session. Switch it off with
  `sdata.show_packages_used(at_end=False)` or the environment variable `SIMPLYDATA_NO_CITE_LIST=1`.
- `sdata.show_packages_used()` prints the full references, a sentence for your methods, and the packages you
  loaded yourself (cite them if you used them); `save_as="references.bib"` also writes them as BibTeX.
  simplydata itself comes first, with its Zenodo DOI.
- The references are the packages' own: R's `citation()` and `packageVersion()` for R and its packages, and for
  Python packages the citation each package asks for (a package that asks for none is listed with its name,
  version and home page). No reference is made up, and nothing is computed: results and printouts of the
  other words are unchanged.
- `sdata.help("cite")`, and citation, citations, references, cite_packages, sessionInfo, session_info and bibtex,
  point to the new word.

### Fixed: results from R could change after they were returned

- Numbers coming back from R were NumPy views into R's memory that did not keep the R object alive. When R
  later cleaned up and reused that memory, a result could silently fill with other numbers (seen once on CI,
  where a column turned into one repeated value). Every result from R is now a copy that Python owns. This
  affects every word that runs R; results already printed were right at the time, but numbers kept and used
  later could change.

### explain() grows (S3a-1)

New options of `table.explain`, each checked against the package underneath and R, with a box "The same
underneath" in the manual and a case on real, published data in the reliability study:

- `weights="precision"`: precision weights, as R `lm(weights =)` and `glm(weights =)` (statsmodels WLS and
  `GLM(var_weights=)`); rows with weight 0 are left out first, as R does.
- `outcome="yes or no (overdispersed)"` with `out_of=`: quasi-binomial regression (R `glm(family =
  quasibinomial)`). A yes/no model with `out_of=` now notes when the yes counts vary more than the binomial
  allows and points to it.
- `matched_by="set"` with `outcome="yes or no"`: conditional logistic regression for matched sets
  (statsmodels `ConditionalLogit`, as R `survival::clogit()`).
- `show="risk ratios"`: risk ratios by modified Poisson regression (Zou 2004), or `method="log-binomial"`.
  A yes/no model with odds ratios now notes when yes is common (more than 10 % of the rows), where an odds
  ratio is not a risk ratio. `show="standardised effects"` (also "standardized effects"): each effect per
  standard deviation, refitted on z-scores (R `effectsize::standardize_parameters(method = "refit")`), with
  the warning that these depend on the sample's spread.
- `giving_outliers_less_weight=True`: robust regression by Huber's M-estimation (statsmodels RLM, as R
  `MASS::rlm()`); the printout lists the rows given less weight. Not the same as `robust_errors=True`.
- `with_knots=3` with `curve_for=`: a natural cubic spline (patsy `cr()`, the same curves as R
  `splines::ns()`), with a test of the whole curve; also with `grouped_by=` and `weights=`.
- `interval_by="bootstrap"` (with `resamples=` and `with_seed=`): BCa intervals from SciPy, the rows drawn
  again whole; `interval_by="profile"`: profile-likelihood intervals (R `confint()`, needs R);
  `p_value_by="likelihood ratio"`: a likelihood-ratio test for each column (R `drop1(test = "LRT")`).
- `crossed_with="item"` with `grouped_by=`: two crossed groupings, `(1 | subject) + (1 | item)` (R lme4).
- `outcome="counts with many zeros that vary a lot"` (zero-inflated negative binomial) and `outcome="counts in
  two steps"` (a hurdle model, also "hurdle"; "... that vary a lot" for a negative binomial second step), both
  R pscl; `zero_part_using=` gives the zero part its own columns.
- The fit line of a yes/no model also prints Nagelkerke's and Tjur's pseudo R squared (as R `performance`).
- Lesson 16 has a part on risk ratios; a new lesson 27, "Beyond the average line: outliers", teaches
  `giving_outliers_less_weight=` and how it differs from `robust_errors=`.
- The reliability study adds 16 cases on eight real datasets (Galton's sweet peas, Crowder's Orobanche seeds,
  infert, birthwt, stackloss, mtcars, VerbAgg and the NMES 1988 survey, whose published hurdle and
  zero-inflated estimates (Zeileis, Kleiber & Jackman 2008) it reproduces). The registry of "The same
  underneath" now has entries for options too ("table.explain weights="), each with its own box.

### Lines and curves (S3a-2)

- **New word `table.fit_dose_response(x=, y=)`** and its chart twin **`chart.fit_dose_response()`**: a
  4 parameter log-logistic dose-response curve (R drc) with the ED50 (EC50) and its 95 % interval
  (delta method). `doses_for_effect=[10, 50, 90]` gives more EDs; `of_kind=` "3 parameter
  log-logistic", "5 parameter log-logistic" or "weibull" ("LL.4", "LL.3", "LL.5" accepted);
  `outcome="yes or no", out_of=` gives the LD50 from deaths out of exposed (a 2 parameter
  log-logistic curve from 0 to 100 %); `for_each_group_in=` compares the ED50s of groups (relative
  potency, R drc::EDcomp()). Needs R with drc.
- **New word `table.find_best_power_of(column)`**: the Box-Cox power (SciPy, with its 95 % interval) or
  `method="yeo-johnson"`; with `using=` the power for a model's leftovers (R car::powerTransform()),
  with likelihood-ratio tests of log and no change. Box-Cox with zeros points to Yeo-Johnson.
- `fit_line(method=)`: "theil-sen" and "siegel" (SciPy), "standardised major axis" and "major axis"
  (R smatr), "deming" with `y_error_over_x_error=` and "passing-bablok" (R mcr). Each printout says
  which question the line answers. `y_error_over_x_error=` is y over x; R mcr's `error.ratio` is x
  over y, so simplydata passes 1 / value (tested against R deming::deming as well).
- `fit_line(with_bends=1)`: a line that bends where the data say (R segmented), with each bend's
  interval and Davies' test of "no bend at all". `fit_line(changes_at=37)` and
  `explain(..., changes_at={"month": 37})`: a jump and a change of slope at a point you know
  (interrupted time series), with the lag-1 autocorrelation of the leftovers.
- `fit_curve(of_kind=)`: "logistic growth", "4 parameter logistic", "michaelis-menten", "rise to a
  limit", "rise or fall to a limit", "gompertz growth", "weibull growth" and "two exponentials" (R's
  self-starting models; start values from R's getInitial() when R is there, else a search of the
  whole range). "logistic" and "gompertz" are accepted for the growth curves.
- `explain(..., for_percentile=90)`: percentile (quantile) lines by R quantreg, with standard errors
  by "nid" for every number of rows (R's default below 1001 rows, "rank", gives intervals only).
- `method="loess"` in `add_smoothed_column` (with `interval=95` for its confidence band),
  `draw_smooth_line` (with `with_confidence_band=True`) and `nums.smooth`: R stats::loess() itself.
  **Changed:** "loess" used to be another spelling of "lowess"; it is now its own method (local curves
  of degree 2, no robustness steps), and the printout names which one ran.
- Lesson 19 has a part on growth curves and an optional "if you have R" part on dose-response
  curves, with two tasks. New practice tables `toxicity` and `culture` (made up).
- The reliability study adds NIST Rat42, Misra1a and BoxBOD (certified nonlinear fits), Bliss's
  beetles (1935), Box and Cox's poisons (1964), Bates and Watts's Puromycin, ryegrass (Ritz et al.
  2015), the stagnant band, leaflife, creatinine, the British seat-belt law and Engel's food data.
  Each new option has its own "same underneath" box (keyed by word and option, as for explain()).
- New R packages for the R extra: drc, segmented, smatr, mcr and quantreg (deming for the study).

### Checking and comparing models (S3a-3)

- New: `table.find_columns_that_predict` chooses the columns that predict a column with the lasso or the elastic net, with the penalty checked on left-out rows (R glmnet, the "one standard error" penalty). It prints no p-values and says why.
- New: `table.find_group_levels_of` shows each group's own starting level (and own slope) of a mixed model with a 95 % interval (R lme4 `ranef(condVar = TRUE)`), with the note, printed and in a "note" column, that the levels are not data for later tests.
- New: `chart.draw_interaction_lines` draws one line per group through the averages, with 95 % t intervals (an interaction plot).
- `explain(spread_changes_with=, neighbours_alike_in_order_of=)`: generalised least squares, a spread that changes by group or with a number column, and neighbouring rows that are alike (AR(1), or continuous-time AR(1) for uneven gaps), R nlme `gls()`. `neighbors_alike_in_order_of=` works too.
- `compare_models(using=[[...], [...], ...])` compares several models by AICc (or AIC with 40 or more rows per value estimated) with Akaike weights; `check_on_left_out_rows=True` checks each model on rows it did not see (10 parts, R boot `cv.glm`). A flat `using=` without `against=` now shows the list-of-lists form in its message.
- `check_model_of` prints the Breusch-Pagan and White tests of equal spread as notes under the scale-location picture, and for a yes/no model adds a calibration picture with the Hosmer-Lemeshow test (R performance) and the Brier score.
- `find_model_averages_of(comparing=)`: each with the first, each with the next, each with the average of the ones before (Helmert), each with the average, trend, or your own weights, with emmeans' adjustment printed; `in_order=` orders the groups. `within_each_group_in=` gives simple effects after the interaction test; `over_range_of=` gives the model average across a number column, ready to draw.
- `compare_averages_of(grouped_by=)`: a nested ANOVA (R `aov(y ~ group + Error(unit))`); `compare_averages_of([...], for_each_group_in=)`: a MANOVA with Pillai's trace (statsmodels).
- Lesson 21 gains a three-model comparison line, an `over_range_of=` line and a note; new lesson 28 "When one effect depends on another" (picture first, then simple effects and contrasts).
- Reliability study: 15 new cases on real data (swiss, iris, warpbreaks, Lake Huron, the rat liver glycogen of Sokal & Rohlf, and Dialyzer, sleepstudy and birthwt read from R packages); same-underneath entries for the three new words and nine new options.

### Planning a study (S3b-2)

- `find_how_many_needed` and `find_chance_of_finding` plan survival studies: `test="compare_survival"` with a hazard ratio as `effect_size=` gives the events first (Schoenfeld, R gsDesign) and, with `percents=[30, 40]`, the people (R powerSurvEpi); `method="freedman"` uses Freedman's formula.
- Regression: `test="explain", using=[...]` with Cohen's f² (statsmodels FTestPowerF2, as R pwr.f2.test and, for a whole model, G*Power); `test="compare_models", using=, against=` for the columns in one model and not the other (as R pwr.f2.test). Logistic regression with `outcome="yes or no"`, one bell-shaped column, `percents=[20]` and an odds ratio per standard deviation (R pwrss, Demidenko with variance correction: G*Power's 337 in its manual's example).
- Clusters: `in_clusters_of=20, alike_within_clusters=0.05` multiply by the design effect 1 + (m - 1) x ICC, said with its numbers, with whole clusters and a note below 10 clusters per group. This one line of arithmetic is simplydata's own and waits for the owner's approval (the alternative is R epiR at run time).
- `based_on="ranks"` is no longer refused: Mann-Whitney and Wilcoxon power by simulation with the very test simplydata runs (SciPy stats.power, 10000 tries, with_seed=1), the Monte Carlo error printed as a 95 % interval. `drawing_from=[dist_a, dist_b]` simulates from your own distributions (compare_averages, compare_before_after, compare_spreads), with a list of `values_per_group=` for a power curve; `by_running=one_study` runs your own simulation for any test and refuses a function that ignores its seed.
- `interval_width=10, percents=[30]`: the values needed for a percent's interval (R presize::prec_prop, Wilson).
- `effect_size=` names its scale in the first sentence; a hazard ratio or odds ratio of 1, 0 or below is refused, and Cohen's labels are never printed for them. Lesson 18 gains one line (events first); help examples and other names (schoenfeld, design_effect, power_z_logistic, simulate_power ...).
- Reliability study: 17 new cases, with published answers from the G*Power manual, the Stata power manuals, presize's paper and the pwr vignette, checked against R gsDesign, powerSurvEpi, pwrss, pwr, presize and epiR; same-underneath entries for both power words and nine options. New R packages for the R extra: gsDesign, powerSurvEpi and pwrss (CRAN only).

### Survival and person-time (S3b-3)

- New: `table.add_time_and_event_columns` turns dates into a time column and an event column: from `from_date=` to the first of `event_date=`, `to_date=` and `until=`, in days, weeks, months (30.4375 days) or years (365.25 days, as R Epi and Stata), with the person-time printed and prevalent cases left empty. `competing_with=` takes the dates of competing events (in hospital, discharge before an infection); the event column then names the event that came first.
- New: `table.find_risk_over_time` gives the chance of having had an event by each time when another event can come first (`value=`, `competing_with=`; Aalen-Johansen, R survival), prints how every other value was counted and what 1 minus Kaplan-Meier would wrongly give; with one kind of event it is 1 minus Kaplan-Meier (no R). New chart twin `chart.draw_risk_curves`.
- The survival words refuse an event column with three or more kinds of outcome and show the `find_risk_over_time` call; `value=` names the event in a column of two other values.
- `find_survival_over_time`: `at_time_points=` (survival at chosen times; `at_times=` works too), `method="life table"` (actuarial life table, R KMsurv), `average_time_up_to=` (the average time without the event up to a horizon, restricted mean survival time), `allowing_for=` (curves adjusted by direct adjustment, R adjustedCurves) and `followed_from=` (delayed entry). `draw_survival_curves` takes `allowing_for=` and `followed_from=` too.
- `compare_survival`: `allowing_for=` (stratified log-rank), `followed_from=`, `average_time_up_to=` (difference and ratio of restricted mean survival times, R survRM2), and Gray's test with `value=`, `competing_with=` (R cmprsk).
- `explain_survival`: `allowing_for=` (stratified Cox, text columns only), `followed_from=` (start-stop rows; rows that start at an event time are fitted by R coxph, as statsmodels would count them twice), cause-specific hazard ratios with `value=`, `competing_with=`, `method="fine-gray"` (R cmprsk crr), `distribution=` (Weibull, exponential, lognormal, log-logistic time ratios, R survreg), and with R Harrell's C in every Cox printout.
- New practice table "admissions" (made up: hospital admissions with dates of discharge and first ESBL-positive culture); new lesson "More survival: start times, competing events, adjusted curves" and one "more" line in lesson 18.
- Reliability study: 20 new cases on real data (lung, veteran, Stanford heart transplant and mgus2 from R survival; bfeed, Channing House and larynx from R KMsurv; the UDCA trial's dates); same-underneath entries for the three new words and seventeen new options. New R packages for the R extra: cmprsk, adjustedCurves (with riskRegression), KMsurv and survRM2.

### Combining studies (S3b-1)

- New: `table.combine_studies` combines the results of several studies (a meta-analysis) with R metafor. Ways in: counts (`events=`, `out_of=`; risk ratios, odds ratios, risk differences), estimates with their intervals or `standard_errors=` (`estimates=`; ratios combined on the log scale, `estimates_are_ratios=` decides), averages (`averages=`, `standard_deviations=`, `counts=`; Hedges' g, differences or ratios of averages), events and time (rate ratios) and correlations. Random effects with REML and Hartung-Knapp intervals by default (`method=` "DerSimonian-Laird", "Paule-Mandel", "common effect", "Mantel-Haenszel", "Peto"; `interval_by="normal"`). It always prints the prediction interval (from 3 studies) as "the true effect in a new setting", tau (as a factor for ratios) and I-squared in words; from 10 studies, Peters' test (counts) or Egger's test and trim and fill as a what-if, worded as small-study effects. `for_each_group_in=` gives subgroups, each with its own spread, with the test of their difference first; `using=` a meta-regression. p-values are said as "in about X of 100 sets of studies like these".
- New: `chart.draw_funnel_plot` draws each study's effect against its standard error with the combined effect and the pseudo 95 % funnel (`funnel_plot` and `draw_funnel` point to it).
- `forest_plot` draws the result of `combine_studies` with squares sized by `size="weight %"`, diamonds for the combined effects and a line for the prediction interval; other result tables draw as before.
- The word-list group "Combine and reshape" is now "Join and reshape" (join_with, add_rows_from, ...), so "combine" means only combining studies; a new group "Combining studies" holds combine_studies, forest_plot and draw_funnel_plot.
- New practice tables `bcg` (13 BCG vaccine trials, Colditz et al. 1994) and `passive_smoking` (37 studies, Hackshaw et al. 1997): real published data, said in their descriptions.
- New lesson 30 "Combining studies (meta-analysis)": the forest plot first, then how much the studies differ, then subgroups and the funnel plot; the task is a faded call on the estimates route.
- Reliability study: 18 new cases on real data read from R metadat (BCG trials with Viechtbauer's published numbers, passive smoking with Hackshaw's published pooled odds ratio, Normand, Curtis, Hart and McDaniel), checked against R metafor and, for DerSimonian-Laird and Mantel-Haenszel, statsmodels; same-underneath entries for the two new words and seven options.
- New R package for the R extra: metafor (with metadat); meta for the reliability study.

### Communities and resistomes (S3c-1)

- New: `table.add_diversity_columns` adds richness, Shannon (natural log) and Simpson (1 - D) per row, and on request inverse Simpson, Chao1 (bias-corrected, with its standard error) and Hill numbers (R vegan). Each index is also said as a number of equally common kinds. `at_total_count=` adds the expected richness at a chosen total count (rarefaction as the expected value, not a random subsample); rows below that total get empty cells and are named. Chao1 and `at_total_count=` refuse non-whole numbers; richness works on normalised values with a note.
- New: `chart.draw_richness_curves` draws one rarefaction curve per row (R vegan `rarecurve`) with a dotted line at the smallest total.
- New: `table.add_log_ratio_columns` adds clr (default), alr (`against=`) or ilr columns. Zeros are first replaced by estimated small values (R zCompositions `cmultRepl(method = "GBM", z.delete = FALSE)`; `zeros_replaced_by="multiplicative"` accepted), never by deleting columns; non-whole numbers are refused for it, a column with fewer than two values above 0 is refused with the line that merges rare columns, and the zeros are summed up in one line. `zeros_replaced_by="adding 1"` uses a pseudocount (vegan `decostand`) and says the answer depends on it.
- New measures on every distance word (`find_distances_between_rows`, `add_nmds`, `compare_profiles_of`, `add_clusters`, `add_principal_coordinates`, `explain_profiles_of`, `find_correlation_between_profiles`, `draw_cluster_tree`): `"aitchison"` (zeros replaced first, then vegan `vegdist("aitchison")`), `"robust aitchison"` and `"hellinger"`. Bray-Curtis on raw counts whose row totals differ more than two-fold prints a note on sequencing depth; the distance words print which columns they used.
- New: `table.add_principal_coordinates` (PCoA, R `cmdscale`), with `how_many=`: the printout gives the share of the positive eigenvalues, how many eigenvalues are negative, and why vegan and ape report a higher percent.
- New: `table.explain_profiles_of(columns, using=[...])`: distance-based RDA on Bray-Curtis by default (vegan `dbrda`), RDA with `measure="hellinger"` or `"aitchison"`, CCA with `method="canonical correspondence"`, a partial analysis with `allowing_for=`. Adjusted R squared first; each column tested after all the others (`anova(by = "margin")`). Euclidean RDA on raw counts is refused with the Hellinger line. It gives back one row for all the columns together and one per column.
- New: `table.find_correlation_between_profiles(first=, second=)`: Mantel (default) or Procrustes (`method="procrustes"`, vegan `protest`), with Legendre's caveat.
- `compare_profiles_of(method="anosim")` gives ANOSIM with the spread check; `show="contributions"` gives SIMPER (vegan `simper`, no p-values) with Warton's caveat. Permutation p-values at the floor (no shuffle as extreme) are said as "at most about 1 of 1000".
- `add_clusters`: `measure=` for hierarchical clusters, a linkage chosen by the measure (Ward for straight-line distances, average for the others; Ward with Bray-Curtis is refused, `measure=` with k-means is refused), `how_many="automatic"` (largest average silhouette width, 2 to 10 clusters), the average silhouette width with Kaufman and Rousseeuw's guide whenever R is there, and `show="silhouette"`. New: `chart.draw_cluster_tree` draws the tree with the same choices and prints the cophenetic correlation.
- New: `table.add_axes_that_separate_groups` (linear discriminant analysis, R MASS) prints each axis's share, the leave-one-out accuracy next to the chance of always guessing the largest group, and the prior. New: `table.add_correspondence_axes`: CA for counts (vegan `cca`), MCA with Greenacre's adjusted inertia for text columns (R ca `mjca`).
- New practice table `resistome` (made up, labelled): 14 resistance genes in 24 samples from a hospital effluent, a treatment plant, a harbour and a fjord sediment, with temperature, salinity and reads.
- New lessons 31 "Diversity of a community" and 32 "Make-up of communities"; lesson 17 gains a "more" line.
- Reliability study and same-underneath entries for each new word and option (vegan dune, varespec, BCI; MASS crabs; ca wg93).
- New R packages for the R extra: zCompositions, compositions and ca (cluster and MASS come with R).
### Hidden factors (S3c-2)

- New: `table.find_hidden_factors_behind(columns)` finds the hidden factors behind many columns (exploratory factor analysis, R psych). simplydata chooses minres, oblimin (the factors may correlate; through GPArotation) and parallel analysis to choose how many (`how_many="automatic"`, seeded by `with_seed=`); `how_many=3`, `rotation=` "varimax", "promax" or "none", and `method=` "ml" or "principal axis" on request. It prints why it chose that many factors, the loadings (blank below 0.3), each column's shared part (communality), the share of the spread and the factor correlations, with notes on the KMO, few rows per column, few columns per factor, columns that go with no factor or with two, and Heywood cases. It gives back one row per column with its loadings, shared part and own part. The columns are required: every number column would put ids and ages in too.
- New: `table.check_hidden_factors(measured_by={...})` checks a model of hidden factors written down beforehand (confirmatory factor analysis, R lavaan, maximum likelihood). The chi-square test gets the W2 sentence with its caution turned round (a small p-value is expected with many rows even for a useful model); CFI, TLI, RMSEA with its 90 % interval and SRMR are each said in words with the commonly used guides of Hu & Bentler (1999), as guides, not pass marks; then the standardised loadings, the factor correlations and the three largest modification indices above 10, with a warning against changing the model only to fit these data. Rows with empty cells are kept (lavaan's `missing = "ml"`), where lavaan alone would leave them out. `formula=` takes a whole model in lavaan's syntax (`lavaan::sem()`, paths between factors); a fit_formula-style formula is refused with a sentence.
- New practice table `ability_tests`: the nine mental ability tests of 301 pupils (Holzinger & Swineford 1939), real published data, as R lavaan ships them.
- Lesson 21 gains a "more" line on the two words; factor analysis stays in the manual (it is not core for the life-science audience).
- Other names: fa, efa, factanal, factor_analysis, parallel_analysis, scree, oblimin, varimax, promax, kmo point to find_hidden_factors_behind; cfa, lavaan, structural_equation_model, fit_measures, cfi, rmsea, srmr, modindices to check_hidden_factors ("sem" is left out: scipy.stats.sem is the standard error of the mean).
- Reliability study: 7 new cases on the Holzinger and Swineford data read from R lavaan: the published fit of the three-factor model (Rosseel 2012, Journal of Statistical Software 48(2): chi-square 85.306 on 24 degrees of freedom, CFI 0.931, TLI 0.896, RMSEA 0.092 (0.071 to 0.114), SRMR 0.065), a path model and full-information handling of empty cells against R lavaan, and the exploratory routes against R psych, base R factanal (uniquenesses and varimax loadings) and statsmodels Factor; same-underneath entries for the two new words and four options.
- New R packages for the R extra: GPArotation (the rotations of psych, listed already) and lavaan.

## 0.2.0 (2026-11-20)

More statistics (tests and models), signals and time series, the 30-day course, the talking syntax, the same-underneath boxes and the public reliability study. Every printed statistical result is checked against R.

### The same underneath, and a public reliability study

- The manual now shows, after a word's example, a grey box **The same underneath**: the same job
  written in the package simplydata uses (pandas and then Polars for tables, NumPy for numbers,
  seaborn or matplotlib for charts, SciPy or statsmodels for statistics, R where simplydata runs R
  for you). Each setting where simplydata's default differs from the package's own is marked (1),
  (2) ... and explained, such as Welch's t-test where SciPy's `ttest_ind` assumes equal spreads, or 10
  histogram bins where seaborn chooses the number itself. Chart words show one picture: the chart
  simplydata draws, which the code in the box draws too, without simplydata's paper look.
  Beginners can skip the box. This release has it for ten words, one of each kind: `draw_bars`,
  `draw_histogram`, `draw_dots`, `trade_off_curve` (R pROC), `table.keep_rows_where`,
  `table.find_average_of`, `table.compare_averages_of`, `table.fit_line`, `nums.find_median` and
  `dist.find_chance_that_value`; more words follow in the next releases.
- Each box is kept once in `simplydata/_underneath/` and a test runs it next to its word: numbers
  to a stated tolerance, tables on a pandas and on a Polars table, charts by their data (bars, dots,
  lines, labels), never by pixels. If pandas, seaborn or SciPy change, or a word is renamed, a test
  fails before a reader sees wrong code.
- The dictionary has a new line for every word, **Underneath**: the package that does the work,
  read from the tested code for the words that have a box.
- A public reliability study, `validation/`: `python validation/make_report.py` runs words on real,
  published data and compares them with the published answers (NIST Statistical Reference Datasets
  for the straight-line fit and averages, Student's sleep data, Anscombe's quartet), with the package
  underneath and with R, and writes `validation/report.md` with the tolerance of every check and the
  versions it ran with. Made-up data are used only for edge cases and labelled. The README links to it
  under "How we check simplydata".

### Fixed

- The note on bell shape names what it checked once: `table.compare_before_and_after` says "the
  changes don't look bell-shaped" (it said "the changes in the changes"), and `compare_average_to`,
  `fit_line` and `explain` read the same way.
- `table.compare_averages_of(..., matched_by=)` shows the groups by the names in the table ("1, 2"),
  not by the names afex makes for R ("X1, X2"), in its averages and in afex's notes; number names
  are in order of value (1, 2, ..., 10). Groups that are one name for R, such as "a b" and "a.b"
  ("a.b" and "a.b.1"), had their averages printed under each other's names; each now keeps its
  own. The numbers are unchanged.
- `table.compare_averages_of(..., matched_by=)` says "(Greenhouse-Geisser corrected)" only when the
  correction was applied. It claimed one for every term: for two matched groups, for independent
  groups and their interactions with two matched groups, and where afex could not estimate the
  epsilon (for example with fewer people than groups). Each line, and the Method line, now says
  which of these it is.

### Talking syntax: every line reads as an instruction to the program

A line of simplydata now reads like an instruction you say to the program: the object, a verb
saying what it should do, then the details as options. Most words start with a verb (`draw_`,
`write_`, `put_`, `set_`, `use_`, `find_`, `get_`, `take_`, `make_`, `turn_into_`, `show_`) and the
first input is joined by a small word (`_where`, `_in`, `_of`, `_that`). Every old name and old
option keeps working for one release and prints one line, once per session (`Note: "bars" is now
called "draw_bars". ...`); `sdata.help("old_name")` points to the new word, and old names are not
listed in `sdata.show_all_words()`, the dictionary's word list or the lessons. Old names from other tools
point to the new words.

- Charts: `chart.bars` -> `draw_bars`, `chart.lines` -> `draw_lines`, `chart.dots` -> `draw_dots`,
  `chart.area` -> `draw_area`, `chart.histogram` -> `draw_histogram`, `chart.boxes` -> `draw_boxes`,
  `chart.violins` -> `draw_violins`, `chart.heatmap` -> `draw_heatmap`, `chart.pie` -> `draw_pie`,
  `chart.polar` -> `draw_polar`, `chart.contour` -> `draw_contour`, `chart.surface` -> `draw_surface`,
  `chart.dots_3d` -> `draw_dots_3d`, `chart.band` -> `draw_band`, `chart.empty_cells` ->
  `draw_map_of_empty_cells`, `chart.error_bars` -> `draw_error_bars`, `chart.curve` -> `draw_curve`,
  `chart.smooth_line` -> `draw_smooth_line`, `chart.density` -> `draw_density`, `chart.count_bars` ->
  `draw_count_bars`, `chart.all_dots` -> `draw_all_dots`, `chart.side_histograms` ->
  `draw_side_histograms`, `chart.qq_dots` -> `draw_qq_dots`, `chart.cumulative_share` ->
  `draw_cumulative_share`, `chart.title_top` -> `write_title_on_top`, `chart.caption_bottom` ->
  `write_caption_at_bottom`, `chart.note` -> `write_note`, `chart.numbers_on_bars` ->
  `write_numbers_on_bars`, `chart.names_on_dots` -> `write_names_on_dots`, `chart.font_size` ->
  `use_font_size`, `chart.font_name` -> `use_font`, `chart.range_x` -> `set_range_x`, `chart.range_y` ->
  `set_range_y`, `chart.log_scale_x` -> `use_log_scale_x`, `chart.log_scale_y` -> `use_log_scale_y`,
  `chart.ticks_x` -> `put_ticks_x`, `chart.ticks_y` -> `put_ticks_y`, `chart.tick_format_x` ->
  `write_ticks_x_as`, `chart.tick_format_y` -> `write_ticks_y_as`, `chart.second_y` -> `add_second_y`,
  `chart.colour` -> `use_colour`, `chart.colours` -> `use_colours`, `chart.colour_scale` ->
  `use_colour_scale`, `chart.style` -> `use_style`, `chart.size` -> `set_size`, `chart.legend_top` ->
  `put_legend_at_top`, `chart.legend_bottom` -> `put_legend_at_bottom`, `chart.legend_left` ->
  `put_legend_on_left`, `chart.legend_right` -> `put_legend_on_right`, `chart.one_chart_per` ->
  `draw_one_chart_for_each_group_in`, `chart.zoom_box` -> `add_zoom_box`, `chart.survival_curves` ->
  `draw_survival_curves`, `chart.line_at_x` -> `draw_line_at_x`, `chart.line_at_y` -> `draw_line_at_y`,
  `chart.line_with_slope` -> `draw_line_with_slope`.
- Chart spellings: `chart.color` -> `use_color`, `chart.colors` -> `use_colors`, `chart.color_scale` ->
  `use_color_scale`. The American spellings of the new words (`use_color`, `use_colors`,
  `use_color_scale`, `label_color_bar`) stay for good, with no note, as `color=` does for options.
  `chart.scatter`, `chart.bar`, `chart.line`, `chart.box` and `chart.violin` are names from other tools
  now, like `hist` and `boxplot`: they never run, and say "In simplydata this is chart.draw_dots(...)"
  (and so on), for good. The legend words accept the other spelling too (`put_legend_on_top`,
  `put_legend_on_bottom`, `put_legend_at_left`, `put_legend_at_right`). A page of charts has
  `write_title_on_top`, `use_style` and `set_size`.
- Tables: `table.column_names` -> `get_column_names`, `table.column` -> `get_column`, `table.row` ->
  `get_row`, `table.cell_at` -> `get_cell_at`, `table.keep_rows` -> `keep_rows_where`,
  `table.remove_rows` -> `remove_rows_where`, `table.count_empty_cells` -> `count_empty_cells_in`,
  `table.remove_rows_with_empty_cells` -> `remove_rows_with_empty_cells_in`, `table.fill_empty_cells` ->
  `fill_empty_cells_in`, `table.remove_extra_spaces` -> `remove_extra_spaces_in`, `table.replace_values`
  -> `replace_values_in`, `table.add_date_part_column` -> `add_column_with_part_of_date`,
  `table.add_text_part_column` -> `add_column_with_part_of_text`, `table.replace_text` ->
  `replace_text_in`, `table.average_of` -> `find_average_of`, `table.median_of` -> `find_median_of`,
  `table.total_of` -> `find_total_of`, `table.smallest_of` -> `find_smallest_of`, `table.biggest_of` ->
  `find_biggest_of`, `table.standard_deviation_of` -> `find_standard_deviation_of`, `table.summary_of` ->
  `find_summary_of`, `table.percent_of` -> `find_percent_of_rows_where`, `table.count_different_values`
  -> `count_different_values_in`, `table.percentile_of` -> `find_percentile_of`, `table.most_common_of`
  -> `find_most_common_of`, `table.correlation_between` -> `find_correlation_between`,
  `table.interval_of` -> `find_interval_of`, `table.chart` -> `start_chart`, `table.compare_averages` ->
  `compare_averages_of`, `table.compare_each_pair` -> `compare_each_pair_of`,
  `table.compare_before_after` -> `compare_before_and_after`, `table.compare_counts` ->
  `compare_counts_of`, `table.compare_spreads` -> `compare_spreads_of`, `table.compare_shapes` ->
  `compare_shapes_of`, `table.check_random_order` -> `check_if_random_order`, `table.compare_matched` ->
  `compare_matched_columns`, `table.model_averages_of` -> `find_model_averages_of`, `table.check_model`
  -> `check_model_of`, `table.show_rows_that_pull` -> `show_rows_that_pull_model`,
  `table.principal_components_of` -> `find_principal_components_of`, `table.distances_between_rows` ->
  `find_distances_between_rows`, `table.compare_profiles` -> `compare_profiles_of`,
  `table.survival_over_time` -> `find_survival_over_time`, `table.spectrum_of` -> `find_spectrum_of`,
  `table.check_steady` -> `check_steady_over_time`, `table.autocorrelation_of` ->
  `find_autocorrelation_of`, `table.trend_of` -> `find_trend_of`, `table.compare_forecasts` ->
  `compare_forecasts_for`, `table.find_change_points` -> `find_change_points_in`, `table.find_peaks` ->
  `find_each_peak_that`, `table.find_dips` -> `find_each_dip_that`, `table.map_of` -> `make_map_of`,
  `table.fit_distribution` -> `fit_distribution_to`, `table.compare_distributions` ->
  `compare_distributions_for`, `table.make_numbers` -> `turn_into_numbers`, `table.make_text` ->
  `turn_into_text`, `table.make_dates` -> `turn_into_dates`, `table.make_lowercase` ->
  `turn_into_lowercase`, `table.make_uppercase` -> `turn_into_uppercase`, `table.round_to` ->
  `round_numbers_in`, `table.steps` -> `show_steps`.
- Numbers: `nums.number_at` -> `get_number_at`, `nums.power` -> `raise_to_power`, `nums.square_root` ->
  `take_square_root`, `nums.absolute_value` -> `take_absolute_value`, `nums.log` -> `take_log`,
  `nums.exp` -> `take_exp`, `nums.running_total` -> `turn_into_running_total`, `nums.keep_numbers` ->
  `keep_each_number_that`, `nums.remove_numbers` -> `remove_each_number_that`, `nums.replace_numbers` ->
  `replace_each_number_that`, `nums.average` -> `find_average`, `nums.median` -> `find_median`,
  `nums.total` -> `find_total`, `nums.smallest` -> `find_smallest`, `nums.biggest` -> `find_biggest`,
  `nums.standard_deviation` -> `find_standard_deviation`, `nums.percentile` -> `find_percentile`,
  `nums.number_grid` -> `make_number_grid`, `nums.table` -> `turn_into_table`, `nums.chart` ->
  `start_chart`, `nums.spectrum_of` -> `find_spectrum`, `nums.autocorrelation_of` ->
  `find_autocorrelation`, `nums.keep_frequencies` -> `keep_each_frequency_that`,
  `nums.remove_frequencies` -> `remove_each_frequency_that`, `nums.find_peaks` -> `find_each_peak_that`,
  `nums.find_dips` -> `find_each_dip_that`, `nums.fourier_transform` -> `take_fourier_transform`,
  `nums.envelope` -> `find_envelope`, `nums.steps` -> `show_steps`.
- Grids of numbers (with the number words above that they share): `grid.shape` -> `find_shape`,
  `grid.number_at` -> `get_number_at`, `grid.row` -> `get_row`, `grid.column` -> `get_column`,
  `grid.numbers` -> `get_all_numbers`, `grid.replace_numbers` -> `replace_each_number_that`, `grid.steps`
  -> `show_steps`.
- Distributions: `dist.chance` -> `find_chance_that_value`, `dist.density_at` -> `find_density_at`,
  `dist.percentile` -> `find_percentile`, `dist.cut_off` -> `find_cut_off`, `dist.middle_range` ->
  `find_middle_range`, `dist.average` -> `find_average`, `dist.median` -> `find_median`,
  `dist.standard_deviation` -> `find_standard_deviation`, `dist.variance` -> `find_variance`,
  `dist.summary` -> `show_summary`, `dist.random_numbers` -> `make_random_numbers`, `dist.chart` ->
  `draw_chart`, `dist.table` -> `turn_into_table`, `dist.parameters` -> `show_parameters`.
- sdata words: `sdata.example` -> `get_example`, `sdata.pairs` -> `draw_all_pairs`, `sdata.side_by_side`
  -> `put_side_by_side`, `sdata.one_above_other` -> `put_one_above_other`, `sdata.grid` ->
  `put_in_rows_and_columns`, `sdata.random_numbers` -> `make_random_numbers`, `sdata.how_many_needed` ->
  `find_how_many_needed`, `sdata.chance_to_find` -> `find_chance_of_finding`, `sdata.dates` ->
  `make_run_of_dates`, `sdata.inverse_fourier_transform` -> `find_inverse_fourier_transform`,
  `sdata.wave` -> `make_wave`, `sdata.window_shape` -> `make_window_shape`, `sdata.find_smallest` ->
  `find_where_smallest`, `sdata.find_biggest` -> `find_where_biggest`, `sdata.words` -> `show_all_words`,
  `sdata.lesson` -> `show_lesson`, `sdata.today` -> `show_today`, `sdata.day` -> `show_day`,
  `sdata.answers` -> `show_answers`, `sdata.next_day` -> `go_to_next_day`.
- Options: `above=` -> `is_above=`, `below=` -> `is_below=`, `at_least=` -> `is_at_least=`, `at_most=` ->
  `is_at_most=`, `equal_to=` -> `is_equal_to=`, `not_equal_to=` -> `is_not_equal_to=`, `one_of=` ->
  `is_one_of=`, `after=` -> `is_after=`, `before=` -> `is_before=`, `between=` -> `is_between=`,
  `pattern=` -> `matches_pattern=`, `for_each=` -> `for_each_group_in=`, `arrow=` -> `with_arrow=`,
  `at_risk_table=` -> `with_at_risk_table=`, `censor_marks=` -> `with_censor_marks=`, `confidence_band=`
  -> `with_confidence_band=`, `dots=` -> `with_dots=`, `letters=` -> `with_letters=`, `numbers=` ->
  `with_numbers=`, `bins=` -> `with_bins=`, `decimals=` -> `with_decimals=`, `seed=` -> `with_seed=`,
  `degree=` -> `of_degree=`, `kind=` -> `of_kind=`, `label=` -> `labelled=`.
- Where they apply: the `is_` conditions are on `keep_rows_where`, `remove_rows_where`,
  `replace_values_in`, `find_percent_of_rows_where`, the `each_..._that` words of numbers and grids,
  `keep_each_frequency_that`, `remove_each_frequency_that`, `find_each_peak_that`, `find_each_dip_that`,
  `chart.peak_dots` and `dist.find_chance_that_value`. `between=` stays for every span (axes, search
  ranges, random numbers, colour scales); `after=` and `before=` stay on `compare_before_and_after` (two
  columns) and `add_column_with_part_of_text` (the text around a mark); a grid's summaries take
  `in_each="row"` / `"column"` (was `for_each=`) and `agreement_between` takes `checking_for="agreement"` /
  `"consistency"` (was `kind=`), so `for_each_group_in=` and `of_kind=` each keep one meaning; the old
  spellings work for one release with the usual note. `labeled=` is accepted as well as `labelled=`.
- The note for an old name is given once for each new name, so `table.chart` and `dist.chart` (now
  `start_chart` and `draw_chart`), or `above=` in `keep_rows_where` and in `find_cut_off`, each get their own
  note. `sdata.help("dist.chart")` honours the object written in front and names the object on each line
  (`"dist.chart" is now called "dist.draw_chart".`); an old option lists its words on one line.
- Error messages, step descriptions (`turn marks into text`), docstrings and the lessons use the new names
  throughout.
- The one-page cheat sheet is now the first pages of the dictionary, "All the words at a glance" (every
  word, group by group, with its example and what it does). `docs/cheatsheet.md` and
  `docs/make_cheatsheet.py` are gone: the three documents are the manual, the dictionary and the 30-day
  guide, all built by `python docs/make_manual.py`.
- `dist.find_cut_off(with_chance_above=0.05)` / `with_chance_below=` (was `cut_off(above=)` / `below=`):
  the option says it is a chance, so it does not look like the `is_above=` condition.
- `table.round_numbers_in("price", with_decimals=2)` (was `round_to("price", 2)`); `nums.round_to(2)`
  keeps its name. `draw_one_chart_for_each_group_in("class")` keeps `down=`, `across=` and `per_row=`.
- PLAN section 4 has the new patterns and a rule, "Talking to the program".

### 30 days: everyday work only

- The 30-day guide now teaches only the work people do with data most days; the manual stays the
  complete reference. Left to the manual (the lessons are unchanged): lesson 22 (risks, diagnostic
  tests and agreement), lesson 24 (forecasts), lesson 26 (systems), the spectra, filters and
  steady-or-not parts of lesson 25, finding and solving (lesson 19, example 3) and values between
  points (lesson 20, example 3). Their recall questions go with them, and the days that come near
  them end with one line, "More in the manual: sdata.lesson(n) ...".
- The freed time relieves the fullest days. Python track: 15 models, 16 working with a model,
  17 patterns across many columns, 18 survival and planning a study, 19 fitting and distributions,
  20 time series (lesson 23, with peaks and dips from lesson 25). Beginner track: 22 models,
  23 working with a model, 24 patterns, 25 survival, 26 fitting and distributions, 27 time series.
  Reviews, project days and the final test stay where they were.
- The time-series day sets all of lesson 23 (with a question on `sdata.dates`), and
  `add_rolling_column(window="7 days")` and `trend_of` come back 3 and 7 days later (when the track
  has those days) and in the final test. Lessons 19 and 20 set only their tasks 1 and 2 (task 3 is
  about the part left to the manual).
- The final test also asks every question of a day that has not come up yet, so the words of the
  last learning days of the beginner track are asked from memory too.

### More kinds of outcome in explain()

- `outcome="counts that vary a lot"`: negative binomial regression, as R `MASS::glm.nb()` (theta by
  maximum likelihood with statsmodels, then the GLM with theta held, as glm.nb reports it). It sits
  next to `"counts (overdispersed)"` (quasi-Poisson), and the overdispersion note names both.
- `outcome="positive numbers"`: Gamma regression with a log link for positive, skewed numbers such as
  times or amounts (R `glm(family = Gamma(link = "log"))`); each effect multiplies the average.
- `time="years"` with counts: rates, the count per unit of time (R `offset = log(years)`).
- `out_of="tries"` with `outcome="yes or no"`: the column holds the number of yes out of that many
  tries (R `glm(cbind(yes, tries - yes) ~ ..., family = binomial)`).
- `outcome="ordered groups"` with `in_order=["low", "middle", "high"]`: ordered logistic regression
  (statsmodels OrderedModel, as R `MASS::polr()`), odds ratios of a higher group and the cut-points
  in a short block of their own.
- `outcome="groups"`: multinomial logistic regression (statsmodels MNLogit, as R `nnet::multinom()`),
  one block per group compared with the first.
- `outcome="shares"`: beta regression for shares between 0 and 1, R `betareg::betareg()` itself.
- `outcome="counts with many zeros"`: zero-inflated Poisson regression, R `pscl::zeroinfl()` itself;
  the two parts (how many, and extra zeros) are printed in words, one block each.
- `link=` for experts: "probit" or "cloglog" for yes or no, "identity" or "sqrt" for counts,
  "inverse" or "identity" for positive numbers; the effects are then on that scale.
- Every explain() printout ends its numbers with two lines. "How well it fits:" says it in plain
  words: an R squared when there is one, then AIC and BIC ("smaller is better, but only to compare
  models of the same rows"), for example `How well it fits: pseudo R squared 0.233 (0 = no better than
  no columns). AIC 176, BIC 185: ...` (yes or no from "hours" and "sleep" in the school example). A pseudo
  R squared is never read as "explains 23 %": it does not mean that. The Method line under it names
  the calls that give the same numbers: AIC and BIC as R `AIC()`, `BIC()` (for mixed models those of the REML fit, as R gives them for `lmer`), McFadden's
  pseudo R squared for yes or no, counts, ordered groups, groups and counts with many zeros
  (statsmodels, as R `performance::r2_mcfadden()`), betareg's pseudo R squared for shares, and
  Nakagawa's R squared for mixed models (from the columns alone and with the groups too, marginal and
  conditional, R `performance::r2_nakagawa()` itself, so it needs R; without R the AIC and BIC stay and
  one line says the R squared is left out and how to get R). Quasi-Poisson and GEE have no likelihood,
  and the line says so.
- `explain(..., curve_for="hours")`: "hours" may follow a curve instead of a straight line (a
  generalised additive model with a smooth term), R `mgcv::gam(marks ~ s(hours) + ..., method = "REML")`
  itself, for numbers,
  yes or no and counts: the other effects as usual, and for each curve its effective degrees of freedom
  and the test of whether it is flat (R `summary.gam()`). For numbers the fit line gives adjusted R
  squared and the deviance explained; for yes or no and counts it gives only the deviance explained, as a
  pseudo R squared, for example `deviance explained 0.192 (a pseudo R squared; 0 = no better than no
  columns)`, never as a percentage explained. Each curve's row is matched to R's smooth table by
  name, so `curve_for=` may list the columns in any order; a column needs 10 different values in the rows the model uses.
- `outcome="counts that vary a lot"` on counts that vary no more than Poisson allows now says so
  (theta grows without limit, R `glm.nb()` warns "iteration limit reached") instead of failing inside
  statsmodels.
- Renamed before release, after a review of the names (the old names still work, with a one-line note):
  `smooth_for=` is now `curve_for=` ("smooth" means taking the noise out of readings elsewhere, and the
  pair `own_slope_for=` / `curve_for=` reads as one family); `robust=True` on explain is now
  `robust_errors=True` (robust standard errors, HC3; "robust" alone suggests resistant to outliers,
  which these errors are not).

### Working with a model: averages, checks, rows that pull, comparisons

- `table.model_averages_of("marks", for_each="school", using=["hours", "breakfast"])`: the average the
  model gives for each group, with number columns held at their averages and other group columns
  counted equally (adjusted averages, estimated marginal means), and every pair of groups with
  Tukey's adjustment. R `emmeans::emmeans()` and `pairs()` themselves (needs R); chances of yes and
  odds ratios for `outcome="yes or no"`, average counts and rate ratios for `"counts"`; with `grouped_by=`
  the degrees of freedom emmeans itself used (Kenward-Roger up to 3000 rows, asymptotic above, as
  `pbkrtest.limit`), named in the Method line. Pairs keep group names that hold "-", "+", "/" or "*"
  as they are. `marginal_means_of` and `emmeans` point to it. For `outcome="ordered groups"` and
  `"groups"` the column of each group's value is called "model chance" (it holds a chance), for the
  other outcomes "model average".
- `table.check_model("marks", using=[...])` also prints how strongly each column is linked with the others:
  variance inflation factors as R `car::vif()` (statsmodels `variance_inflation_factor` for least squares;
  R `car::vif()` itself for GLMs and the generalised VIF of group columns with 3 or more groups).
- `table.check_model("marks", using=[...])`: the four pictures of R `plot(lm())` (residuals against
  fitted values, normal Q-Q, scale-location, residuals against leverage with Cook's distance lines),
  with a plain sentence on what to look for in each. Numbers from statsmodels `OLSInfluence` /
  `GLMInfluence`; for yes/no and counts the pictures of R 4.6 `plot(glm())`.
- `table.show_rows_that_pull("marks", using=[...])`: the rows with a Cook's distance above 4 / n,
  biggest first, with leverage and studentised residual (statsmodels, as R `cooks.distance()`,
  `hatvalues()`, `rstudent()`), numbered as in the whole table.
- `table.compare_models("marks", using=["hours"], against=["hours", "breakfast"])`: the F test (or
  likelihood-ratio test for yes/no and counts) of the smaller model against the bigger, as R
  `anova(m0, m1)`, and AIC and BIC for both, as R `AIC()` and `BIC()`, on the same rows.
- The four words work with every outcome they can: `model_averages_of` with all outcomes of `explain()`
  (R emmeans on `MASS::glm.nb`, `glm(quasipoisson)`, `glm(Gamma)`, `betareg`, `zeroinfl`; for
  `"ordered groups"` and `"groups"` the chance of each group, `emmeans(mode = "prob")`, compared pair by
  pair within each group); `check_model` and `show_rows_that_pull` with the count outcomes and
  `"positive numbers"` (hat values from the expected information, as R `hatvalues()`); `compare_models`
  with all outcomes (F tests for quasi-Poisson and Gamma as R `anova(test = "F")`, likelihood-ratio tests
  for the others, with the degrees of freedom of every value estimated, as R).
- With `grouped_by=`: `check_model` shows R `plot(lmer)` (residuals against fitted values, Q-Q of the
  scaled residuals, scale-location) and a Q-Q picture of each group's own starting level, as R
  `qqnorm(ranef(m))` (statsmodels MixedLM; R `lme4::glmer` for yes/no and counts);
  `show_rows_that_pull` shows the groups that pull, each left out in turn, R `lme4` `influence()` and
  `cooks.distance()`; `compare_models` refits both mixed models by maximum likelihood (statsmodels), as R
  `anova(m0, m1)` does.

### Intervals for predictions and robust standard errors

- `table.add_predicted_column(..., interval=95)` adds the low and high end of the 95 % confidence interval
  of the predicted average, in the columns "predicted marks 95 % CI low" and "predicted marks 95 % CI
  high" (the house pattern "<thing> 95 % CI low"; another level gives "90 % CI"), as R `predict(interval = "confidence")` (for yes/no and counts worked out on
  the link scale and turned back); `for_new_rows=True` gives the wider prediction interval where one new
  row would fall, as R `predict(interval = "prediction")` (numbers only), in "predicted marks 95 %
  prediction low" and "... high", so the two kinds of interval keep different names. From statsmodels
  `get_prediction()`.
- `table.explain(..., robust_errors=True)` (experts): robust standard errors (sandwich, HC3), as R
  `sandwich::vcovHC(m, type = "HC3")` with `lmtest::coeftest()` and `coefci()`; the whole-column tests and
  the test of the model as a whole become Wald tests with those errors (as `car::Anova(vcov. = )` and
  `lmtest::waldtest()`). statsmodels for numbers; R `sandwich` itself for yes/no, counts and positive
  numbers, since statsmodels' GLM gives HC0 when HC3 is asked for.

### More choices for grouped rows (grouped_by=)

- `own_slope_for="hours"`: each group gets its own slope for hours as well as its own starting level,
  R `lme4::lmer(... + (1 + hours | school))` itself (and `lme4::glmer()` for yes/no and counts). The
  variance of the slopes and their correlation with the starting levels are printed, with a note on a
  singular fit. R is used because statsmodels' `MixedLM(re_formula=)` does not reliably reach lme4's
  answer.
- `p_value_by="satterthwaite"` (also `"few groups"`): t-tests with Satterthwaite degrees of freedom, their
  intervals and the whole-column F tests from R `lmerTest` itself, instead of the Wald z-tests (still
  the default, without R).
- `effects="for the whole population"`: generalised estimating equations (GEE) instead of a mixed model:
  effects averaged over all groups, with robust standard errors. statsmodels `GEE`, as R
  `geepack::geeglm()`, with `within_groups="alike"` (exchangeable, the default) or `"independent"`;
  `within_groups="in time order"` (AR-1, rows in table order) runs R `geepack` itself, since statsmodels'
  AR-1 estimate differs. The default `effects="for the average group"` is the mixed model.

- `grouped_by=["school", "class"]`: groups inside groups (classes inside schools), as R
  `lme4::lmer(... + (1 | school/class))`: statsmodels MixedLM with a variance component for the inner groups
  (the same REML answer as lme4), and R `lme4::glmer()` for yes/no and counts. The variance at each level
  is printed with its share. `model_averages_of`, `check_model` (a fifth picture: the inner groups' own
  levels, R `qqnorm(ranef(m)$"class:school")`), `compare_models` (both models refitted by maximum
  likelihood, as R `anova()`) and `show_rows_that_pull` (whole outer groups) take the same list.
  `sdata.example("school")` has a `class` column (red, blue or green, 5 pupils of each in every school)
  to practise with, and `sdata.help("table.explain")` shows `grouped_by=["school", "class"]` and
  `curve_for="hours"`.
- Mixed models for yes/no and counts take `time=`, `out_of=` and `link=`, also with `own_slope_for=`
  (R `lme4::glmer(... + offset(log(time)))`, `cbind(yes, tries - yes)`, `binomial(link = "probit")`).
  GEE takes them too: `time=` and `link="probit"` / `"cloglog"` for yes or no with statsmodels `GEE` (the
  same answer as `geepack::geeglm()`), `out_of=` through R `geepack` itself (statsmodels' weighted GEE
  gives other numbers). Links for counts other than log are not in geepack, and GEE says so.
- A mixed model needs fewer groups than rows, for `grouped_by=` and for the inner groups of
  `grouped_by=["school", "class"]`, as R lme4 checks; one row per group is now said plainly before fitting
  (statsmodels would report a group variance that cannot be estimated). If R cannot refit the model for
  Nakagawa's R squared, the fit line says there is no R squared instead of stopping after the printout.

### Repeated measures

- `table.compare_averages("marks", for_each="subject", matched_by="name")`: a repeated-measures ANOVA for
  values measured on the same person (plot, animal ...) in every group, R `afex::aov_ez()` itself, with the
  Greenhouse-Geisser correction, Mauchly's test of sphericity and generalised eta-squared printed.
  `for_each=["subject", "class"]` with one column that changes within a person and one that does not gives
  the mixed ANOVA. simplydata works out which column is which. Needs R. The averages printed are of the
  rows afex analysed: a person not measured in every group is left out by afex, and the printout says so.

### Tables of tests (ANOVA tables)

- `table.explain(..., test_type="type 2")` adds one test for each column: `"type 2"` (the usual choice,
  as R `car::Anova(type = 2)`), `"type 3"` (sum-to-zero coding done for you, as `car::Anova(type = 3)`)
  or `"in order"` (as R `anova()`; the order of `using=` matters: each column after the ones before it,
  main effects before interactions as in R's formula, from nested statsmodels fits). For numbers: F tests
  and sums of squares from statsmodels `anova_lm`, and partial eta-squared from R `effectsize`, matched to
  each column by name. For yes/no and counts: likelihood-ratio tests from R `car::Anova` itself. A
  `test_type=` that cannot be used (with `grouped_by=`, or without R for yes/no and counts) is said
  before the model is printed; type 3's sum-to-zero coding is put back in R even when R stops.
- A model with complete separation now prints "infinite" for an odds ratio instead of stopping with an
  error.

### Mixed models for yes/no and counts

- `table.explain(..., outcome="yes or no", grouped_by="school")` and `outcome="counts"` with
  `grouped_by=` fit a generalised linear mixed model with R `lme4::glmer()` itself (random intercept
  per group, Laplace approximation): odds or rate ratios with Wald intervals, the variance between
  groups and AIC, and the singular-fit and few-groups notes. Needs `simplydata[r]` and R.

### Methods come from established packages

simplydata now calls SciPy and statsmodels for its methods instead of writing them out:
p-value adjustment, Welch's ANOVA, the log-rank test, Kaplan-Meier, the Cox model, linear,
logistic and Poisson models, mixed-model errors, polynomial fits, LOWESS, the line band, PCA,
Cramer's V, the summary measures, and the gamma, Gumbel and von Mises fits. The answers are the
same as before, except that logistic and Poisson standard errors now come from the converged
estimates (R uses the step before), so they agree with R to about 3e-5.

- statsmodels is now required (`pip install "simplydata[stats]"` still works).
- Standard errors of fitted distributions come from statsmodels' numerical Hessian
  (`approx_hess3`); they may move by up to a few in a million (about 3e-6) from before.
- A smoothing spline needs at least 5 different x values (SciPy's spline; it was 4).
- Python 3.11 or newer, and SciPy 1.16 or newer (its quantiles are exact).
- `compare_shape_to` calls SciPy `goodness_of_fit` again; most shapes take a few seconds
  with `samples=9999`, Weibull and t longer (a note says so before a long run).

### One sentence for every p-value

Every test now says its p-value in the same sentence, as a count of studies: "If there were truly
no difference, a difference this big or bigger would turn up in about 3 of 100 studies like this
one (p = 0.031)." Below 0.001 it says "fewer than 1 in 1000 studies"; from 0.05 it adds "This does
not show that there is no difference." Each test words its own "nothing there" ("If the groups were
truly alike", "If B were truly not higher than A", "If there were truly no link", "If the values truly
came from a bell shape" ...). This replaces "unlikely to be chance" / "could easily be chance", which
reads as the chance that chance did it, a common misreading of p-values. The words that list many
p-values (model terms, the strongest correlations, Cox hazard ratios) use a short form: "about 3 of
100 studies would show this much if there were truly none (p = 0.031)"; adjusted p-values in
`compare_each_pair` are printed as "Holm-adjusted p = 0.023". The effect and its interval now come
first, the p-value sentence on its own line after it. The count of studies is the p-value rounded;
nothing is computed anew. The model words and the time-series words say their p-values the same way:
the tests of a model as a whole and of each column (ANOVA tables, smooth curves, ratio models),
`compare_models`, `compare_averages(matched_by=)` and its Mauchly check, a single pair of
`model_averages_of` (several pairs print "Tukey-adjusted p = ..."), `trend_of` and the Ljung-Box test
of `autocorrelation_of`.

### One-sided tests and Kendall's tau

- `sides=1, higher=...` (or its mirror `lower=...`) tests in one direction only, chosen before
  seeing the data: `compare_averages(..., sides=1, higher="B")` or `lower="A"` (two groups: Welch,
  Student, Mann-Whitney, Yuen, Brunner-Munzel), `compare_before_after(..., sides=1, higher="after")`
  or `lower="before"`, `compare_average_to(..., sides=1, higher="average")` or `lower="average"`,
  `compare_percent_to(..., sides=1, higher="percent")` or `lower="percent"`, and
  `correlation_between("hours", "marks", sides=1, higher="positive")` (or `"negative"`). Giving both
  `higher=` and `lower=`, or a word the test does not know, is a friendly error. The interval is then
  one-sided too ("at least 1.2"), and the sentence says what the test does and does not look for.
  R's and SciPy's `alternative="greater"` / `"less"` work as well, with the translation printed.
  Each is checked against R `t.test`, `wilcox.test`, `binom.test` and `cor.test` with `alternative =`.
- `correlation_between(..., method="kendall")`: Kendall's tau-b (SciPy `kendalltau`, as R
  `cor.test(method = "kendall")`).

### More tests to choose with test=

- `compare_averages`: `test="yuen"` (20 % trimmed averages, SciPy, as R `WRS2::yuen`),
  `"brunner-munzel"` (SciPy, as R `brunnermunzel.test`), `"alexander-govern"` (SciPy, as R
  `onewaytests::ag.test`) and `"median"` (Mood's median test, SciPy, as R `chisq.test` on the counts
  above the overall median).
- `compare_spreads`: `test="ansari"` and `"mood"` (SciPy, as R `ansari.test`, `mood.test`), and
  `"f"` (R `var.test`, with the interval of the ratio of the variances).
- `compare_counts`: `test="g"` (G-test, SciPy, as R `DescTools::GTest`), and for 2 x 2 tables
  `"barnard"` and `"boschloo"` (R `Exact::exact.test`; SciPy's versions use another two-sided rule
  and give other p-values).
- `compare_before_after`: `test="sign"` (statsmodels `sign_test`, as R `DescTools::SignTest`).
- `compare_shape_to`: `test="lilliefors"` (R `nortest::lillie.test`; statsmodels' p-value
  approximation differs from R's), `"dagostino"` (SciPy `normaltest`, as R `fBasics::dagoTest`) and
  `"jarque-bera"` (SciPy, as R `tseries::jarque.bera.test`). A distribution with fixed numbers can
  be the shape: `compare_shape_to("marks", sdata.distribution("normal", average=60,
  standard_deviation=15))` gives the one-sample Kolmogorov-Smirnov test (SciPy `ks_1samp`, as R
  `ks.test(x, "pnorm", 60, 15)`), and `test="cramer-von-mises"` the Cramer-von Mises test (SciPy, as
  R `goftest::cvm.test`).
- `percent_of(..., interval_by=)` and `compare_percent_to(..., interval_by=)`: the interval of a
  percent can be `"exact"` (Clopper-Pearson, the default), `"wilson"` or `"agresti-coull"`
  (statsmodels `proportion_confint`, as R `DescTools::BinomCI`). `interval_by=` is the same word
  as on `correlation_between`; `method=` still works, with a note.

### Pairs after a test

- `compare_each_pair(..., test=)` gains `"games-howell"` (R `rstatix::games_howell_test`, for groups
  with different spreads, with simultaneous intervals), `"scheffe"` and `"lsd"` (R
  `DescTools::ScheffeTest`, `PostHocTest(method = "lsd")`; LSD is not adjusted and says so), and for
  ranks `"dunn"` (R `FSA::dunnTest(method = "holm")`) and `"conover"` (R
  `PMCMRplus::kwAllPairsConoverTest`, Holm).
- `compare_each_pair(..., against="A")`: Dunnett's test of every group against one control group
  (SciPy `stats.dunnett`, as R `multcomp::glht(mcp(group = "Dunnett"))`; both use random numbers,
  so simplydata seeds SciPy's, `seed=1`, printed).
- `add_adjusted_p_value_column(method=)` gains `"hochberg"` and `"hommel"` (statsmodels
  `multipletests`, as R `p.adjust`).
- `compare_each_pair(..., show="letters")`: a compact letter display, one row per group; groups
  that share a letter have an adjusted p-value of 0.05 or more between them (R
  `multcompView::multcompLetters`). Works with every `test=`.

### Shuffling and the bootstrap

- `p_value_by="shuffling"` on `compare_averages` (2 groups), `compare_before_after` (numbers) and
  `correlation_between` (2 columns): the p-value from shuffling the group labels, swapping the two
  values within rows, or shuffling one column against the other, `shuffles=9999` times with
  `seed=1` (SciPy `permutation_test`, as R `perm::permTS`). When there are no more arrangements
  than shuffles, every one is counted and the p-value is exact; the sentence says which.
- `correlation_between(..., interval_by="bootstrap")`: a 95 % BCa bootstrap interval of r
  (SciPy `bootstrap`, `resamples=9999`, `seed=1`, as R `boot::boot.ci`), with a note below 20
  values that bootstrap intervals are often too narrow.

### Intervals for summaries

- `interval=95` on `average_of` (t interval, as R `t.test`), `median_of` and `percentile_of`
  (exact interval from the order of the values, SciPy `quantile_test`, as R
  `DescTools::MedianCI(method = "exact")`) and `standard_deviation_of` (R `DescTools::VarCI`,
  square-rooted). They then give back a table with the value, the interval and the count.
- `table.interval_of("marks", "median", for_each="class")`: a bootstrap interval for any summary
  (any one-number `summary_of` measure, or a function of your own); `method="bootstrap"` (BCa),
  `"percentile bootstrap"` or `"reverse percentile bootstrap"` (R's `type = "basic"`; the older
  value `"basic bootstrap"` still works, with a note).
- `summary_of(show=[...])` gains `"harmonic mean"` (SciPy `hmean`, as R `psych::harmonic.mean`)
  and `"winsorised average"` (20 % at each end, SciPy `mstats.winsorize`, as R `WRS2::winmean`;
  `"winsorized average"` works too).
- `percentile_of(..., method=)`: R's nine rules, by R's number or NumPy's name (NumPy
  `percentile`, as R `quantile(type =)`).
- `table.add_z_score_column("marks_z", from_column="marks", for_each="subject")`: SciPy
  `zscore(ddof=1)`, as R `scale()`.
- `weights="people"` on `average_of` (statsmodels `DescrStatsW`, as R `weighted.mean`) and
  `standard_deviation_of`: frequency weights by default (as R `Hmisc::wtd.var`) or
  `weight_kind="analytic"` (NumPy `cov(aweights=)`, as R `Hmisc::wtd.var(normwt = TRUE)`).
- `table.fit_distribution("marks", "kernel density")`: a distribution that follows the values
  (SciPy `gaussian_kde` with Silverman's bandwidth from statsmodels `bw_silverman`, the same curve
  as R `density(x)`), with chance, percentile, random_numbers and the rest. R's `bw.nrd0` divides
  the IQR by 1.34 and statsmodels by 1.349, so the bandwidths differ slightly when the IQR is the
  smaller spread; this is printed.

### Equivalence and non-inferiority

- `same_within=5` (or `[-3, 5]`) on `compare_averages` (2 groups, Welch), `compare_before_after`
  and `compare_average_to`: two one-sided tests (statsmodels `ttost_ind`, `ttost_paired`,
  `DescrStatsW.ttost_mean`, as R `TOSTER::t_TOST`), with the 90 % interval. The answer is one of
  three: the same within the margin, different, or the data cannot tell.
- `same_within=5, not_lower="B"` is a non-inferiority test: is B lower than the other side by no
  more than the margin? (statsmodels `CompareMeans`, as R `t.test(mu = ..., alternative = ...)`).
  `not_higher="B"` is its mirror, for outcomes where lower is better (pain). The words say the
  claim that is tested, which `higher="B"` did not; `sides=1, higher="B"` with `same_within=`
  still works and a note gives the new spelling.

### Power

- `how_many_needed` / `chance_to_find(test="compare_counts", percents=[30, 15])`: two percents
  (statsmodels `power_proportions_2indep` for the power; R `power.prop.test` for the number
  needed).
- `same_within=5, spread=10`: power and numbers for two one-sided tests (R
  `TOSTER::power_t_TOST`).
- `how_many_needed(interval_width=4, spread=10)`: the number needed for a 95 % interval of an
  average of that width (R `presize::prec_mean`).
- `based_on="ranks"` says plainly that no package gives rank-test power.

### Lessons and the 30 days

- Lesson 14 starts with the effect and its 95 % interval (`average_of(..., interval=95)`, then the
  first sentence of `compare_averages`), then shows where a p-value comes from by shuffling the
  labels (`p_value_by="shuffling"`) before the formula p-value, and ends with `compare_matched` on
  three measurements of the same patients.
- The lesson "Risks, diagnostic tests and agreement" is the optional life-science lesson. The
  30-day guide finds it by its title, so its number follows the lessons before it (22 once the
  lesson "Working with a model" is in). Its core needs no R: `compare_risks` (a first example
  with a clear effect, then the forest plot as its own example), `compare_to_truth` with a yes/no
  test and `prevalence=`, and `agreement_between` with Cohen's kappa. Scores and trade-off curves,
  devices, questionnaires, Mantel-Haenszel and rates follow as optional "more" examples, each
  worked. The tasks practise what the examples show, the last one as started lines to complete.
  In the beginner track it has a day of its own (day 25; fitting, solving, distributions and values
  between points share day 26), and the small project's second day comes after the final test (day 30),
  together with looking back. In the Python track it shares day 18 with survival and planning a study.
- Lesson 12 ends with a short worked example of `add_z_score_column` (marks of different subjects on one
  scale), and the 30-day guide asks for that word 3 and 7 days later and in the final test.
- A recall question on the idea, not only the word: "Where only 1 % have it, why are most
  positive results of a good test false alarms?" (asked 3 days later and in the final test).
- The core words of this release come back in the 30-day warm-ups exactly 3 and 7 days after the
  day that teaches them, and in the final test from memory (`spaced=` questions in the guide).

### More from Part A: shifts, trends, bigger tables, correlations

- `compare_averages(..., based_on="ranks")` with two groups also prints the Hodges-Lehmann shift
  with its 95 % interval (R `wilcox.test(conf.int = TRUE)`, the same exact/approximate choice as
  the test), in the columns "shift" and "shift 95 % CI low/high" (so `forest_plot(x="shift")`
  draws it), with Hodges-Lehmann named in "method".
- `compare_average_to(..., test="z", standard_deviation=15)`: the z-test with a known standard
  deviation (R `BSDA::z.test()`; statsmodels' ztest uses the sample's own spread).
- `compare_averages(..., test="jonckheere", in_order=[...])`: the Jonckheere-Terpstra trend test
  (statsmodels, as R `clinfun::jonckheere.test()`; tie handling differs slightly).
- `compare_matched(..., test="page")`: Page's trend test along the column order (SciPy, as R
  `crank::page.trend.test()`).
- `compare_counts`: `test="trend", in_order=[...]` (Cochran-Armitage, R `prop.trend.test()`);
  `test="fisher"` on bigger tables (100,000 seeded random tables in SciPy; `p_value_by="exact"`
  counts every table in R `fisher.test()`); `p_value_by="shuffling"` for the chi-square test
  (SciPy, as R `chisq.test(simulate.p.value = TRUE)`); `show="cells"` with the standardised
  residuals (statsmodels, as R `chisq.test()$stdres`). A p-value found by shuffling or by random
  tables says how in the column "p-value by" (the same words as `p_value_by=`).
- `compare_each_pair(..., matched_by="patient")`: each pair compared within the same patients
  (paired t-tests, or Wilcoxon signed-rank with `based_on="ranks"`, Holm-adjusted; as R
  `pairwise.t.test(paired = TRUE)` / `pairwise.wilcox.test(paired = TRUE)`).
- `correlation_between` with two columns now prints every r with its 95 % interval: Pearson from
  SciPy, Spearman from R `DescTools::SpearmanRho()` (Fisher's z) and Kendall's tau-b from
  `DescTools::KendallTauB()` (its asymptotic standard error). New `method="somers"` and
  `method="gamma"` (R `DescTools::SomersDelta()`, `GoodmanKruskalGamma()`, with intervals) and
  `allowing_for="height"` for the partial correlation (R `ppcor::pcor.test()`).
- New `table.compare_correlations("hours", "marks", for_each="class")`: two correlations in two
  groups (Fisher's z) or two correlations that share a column,
  `compare_correlations(["hours", "marks"], ["height", "marks"])` (Steiger's z), with Zou's
  interval (R `cocor`). The columns are given as in `correlation_between`.
- `count_each(..., interval=95)`: simultaneous Sison-Glaz intervals for the percents (statsmodels,
  as R `DescTools::MultinomCI()`).
- `show_rows_with_outliers` / `remove_rows_with_outliers(rule="grubbs" | "dixon" | "rosner")`:
  outlier tests from R `outliers` and `EnvStats`.

### Risks and rates

- `table.compare_risks("died", for_each="treatment", against="usual care")`: the risk in each group
  (exact interval), then the risk difference with Newcombe's score interval and what it means out
  of 100, the number needed for one event fewer (or more), with its interval through infinity
  when the difference's interval includes 0 (the labels do not assume the event is bad; the
  sentence names NNTB/NNTH for a harmful event), the risk ratio and the odds ratio (Wald intervals
  on the log scale, with a note when the outcome is common), and the p-value (chi-square with
  Yates' correction, as R `prop.test()`). The first option is `column=`, as on the other tests,
  and `value="yes"` says which value is the event (as on `compare_percent_to`; `positive=` is
  accepted too). statsmodels `proportion_confint`, `confint_proportions_2indep`,
  `Table2x2`; checked against R `binom.test`, `DescTools::BinomDiffCI`, `epitools::riskratio` /
  `oddsratio`, `epiR::epi.2by2`. `p_value_by="exact"`: Fisher's exact test and the conditional
  odds ratio (SciPy, as R `fisher.test()`).
- `allowing_for="age_group"`: Mantel-Haenszel odds ratio and risk ratio with the Breslow-Day check
  (statsmodels `StratifiedTable`, as R `mantelhaen.test()`, `DescTools::BreslowDayTest()`; the
  interval of the pooled risk ratio from R `epiR::epi.2by2()`).
- `same_within=15` (percentage points): two one-sided tests of two risks (statsmodels
  `tost_proportions_2indep`, as R `TOSTER::twoprop_test()`); `same_within=15, not_lower="B"` (or
  `not_higher=`) is non-inferiority, as on `compare_averages`. The margin is always said in words
  ("same_within=15 on risks means risk differences from -15 to 15 percentage points"), and a
  number below 1 gets a note (percentage points, not a share). `sides=1` alone gives the one-sided
  test (R `prop.test(alternative =)`).
- `table.compare_rates("infections", time="patient_days", for_each="ward")` and
  `table.rate_of(...)`: rates per 1000 with exact intervals, the rate ratio with the exact
  conditional test (statsmodels `confint_poisson`, `test_poisson_2indep`) and R's exact interval
  of the ratio (`poisson.test()`); `same_within=[0.8, 1.25]` (or `1.25`) for a ratio margin
  (statsmodels `tost_poisson_2indep`, as two one-sided R `poisson.test(r =)`), with `not_lower=` /
  `not_higher=` for non-inferiority ("the rate ratio is not below 0.8"). A single ratio margin of 2
  or more gets a note. Each rate is in the columns "rate" and "rate 95 % CI low/high", with a
  column "per" ("1000 patient_days"), so `forest_plot(x="rate")` draws them.
- `sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new", "usual"])` and
  `sdata.compare_rates(events=[15, 30], time=[1200, 1100])` from given counts (`names=`, as on
  `sdata.compare_averages`; `groups=` still works, with a note).
- A 0 in the 2 x 2 table: nothing is added to the empty cells, so the p-value is R's
  (`prop.test(c(5, 0), c(10, 10))`: p = 0.039) and a ratio with a 0 is shown as R
  `epitools::riskratio()` / `oddsratio()` give it: infinite or 0 without an interval, or "cannot be
  worked out" (0 / 0), with a note. No events in either group (or the event in every row) gives no
  p-value, as R gives NaN; `compare_rates` with no events at all says the rate ratio cannot be
  worked out. One-sided risks and rates use the same words as the other tests ("If the risk in B
  were truly not higher than in A, ...").

### Diagnostic tests

- `table.compare_to_truth("rapid_test", truth="infected")`: of 1000 people like these, how many
  the test finds and misses, sensitivity, specificity and the predictive values with exact
  intervals (statsmodels), the likelihood ratios and diagnostic odds ratio from R
  `epiR::epi.tests()`; `prevalence=1` shows the predictive values where 1 % have it.
- With a column of numbers (`"crp"`): the ROC analysis from R pROC: the AUC with DeLong's
  interval, the best cut-off by Youden's index and the answer there; `cut_off=` chooses one.
  Higher scores count as positive (`positive_when="lower"` turns it round; pROC's automatic
  direction is not used, because it hides a test that works the wrong way round).
- `table.compare_accuracy("crp", "procalcitonin", truth="infected")`: DeLong's test of two AUCs
  on the same people (R `pROC::roc.test()`), with the interval of the difference.
- `sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)`, or
  `sdata.compare_to_truth(sensitivity=90, specificity=95, prevalence=1)` for the base-rate question.
  `tp=`, `fn=`, `fp=`, `tn=` and `true_positives=` ... `true_negatives=` work too, with a one-line
  pointer to the simplydata name.
- A test with no positive results says that the share of positives that are real (and the positive
  likelihood ratio) cannot be worked out; a positive likelihood ratio below 1 is worded as "less
  common", a test that works the wrong way round.
- New example table `clinic`: 200 made-up patients with a rapid test, CRP and procalcitonin,
  ratings by a nurse and a doctor, two blood-pressure devices, pain scores and hospital infections
  (`caught_infection`, yes or no), and five questionnaire items `item_1` to `item_5`; the yes/no
  pain columns are `in_pain_before` and `in_pain_after`.
- The counts "of 1000", the number needed and the predictive values at another
  prevalence are display arithmetic on the packages' results (shares written as counts).

### Agreement and reliability

- `table.agreement_between("nurse_rating", "doctor_rating")`: Cohen's kappa with its interval, z
  and p, and the raw agreement beside it (statsmodels `cohens_kappa`, as R `irr::kappa2()` and
  `psych::cohen.kappa()`); `near_misses="linear"` / `"quadratic"` with `in_order=` for ordered
  categories (`weights=`, `weight=` and `wt=` work too). Three or more columns: Fleiss' kappa (statsmodels; z and p from R
  `irr::kappam.fleiss()`). Columns of numbers: the intraclass correlation from R `irr::icc()`,
  two-way, absolute agreement, one rater by default (`raters="a sample"`, `"these only"` or
  `"different per row"` (McGraw and Wong's "random", "fixed", "different" work too), `kind=`,
  `of=` choose the form, which is always named, with Koo and Li's guide words beside the
  interval). The test statistic is in "statistic name" / "statistic" (z for kappa, F for the
  ICC), as on every test; the kappa or ICC is the "estimate". The agreement by chance is shown
  for Cohen's kappa only; weighted kappa shows the exact agreement beside it, and the result
  names the R call exactly as it is made (`type = "consistency"` for the one-way ICC).
  `method="krippendorff"` (R `irr::kripp.alpha()`, the "kind of data" in its own column) and
  `method="lin"` (R `DescTools::CCC()`).
- `table.limits_of_agreement("device_a", "device_b")`: Bland-Altman limits of agreement with the
  intervals of the average difference and of both limits (R `BlandAltmanLeh::bland.altman.stats()`),
  and Lin's concordance correlation.
- `table.reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])`: Cronbach's alpha with Feldt's interval
  and the alpha without each item (R `psych::alpha()`, `psych::alpha.ci()`).
- Every agreement word says that agreement is not correlation.

### Charts of tests

- `chart.trade_off_curve(score="crp", truth="infected")`: the ROC curve from R pROC, with the AUC
  and its DeLong interval in the legend and the best cut-off marked; several scores give one curve
  each.
- `chart.difference_dots(first="device_a", second="device_b")`: the Bland-Altman chart (the same
  names as `limits_of_agreement`; `x=` and `y=` still work, with a note): dots and average
  difference from statsmodels `mean_diff_plot`, the limits and their shaded intervals from R
  `BlandAltmanLeh` (statsmodels' own limits use the standard deviation with n in the divisor, so
  they differ a little from R's).
- `chart.forest_plot(x="estimate", y="measure")`: each row of a result table as a dot with its
  interval, with a line at no effect (0, or 1 on a log scale for ratios); `log_scale=True/False`
  and `line_at=` choose (`ratios=` still works, with a note). When a table holds intervals of two
  levels (95 % and 90 %), it draws the first and names the rows it left out.
- Their field names (`roc_curve`, `bland_altman`, `interval_dots`, `forestplot`) point to these words.

### Test titles

The help titles of the tests no longer ask "or could it be chance?" (which invites reading the
p-value as the chance that chance did it); they ask "really different?", in line with the
p-value sentence.

### Yes/no and category columns before and after

`compare_before_after` now looks at the kind of column, and the sentence says which test that
gives. Two yes/no columns (yes/no, True/False or 0/1): McNemar's test with continuity correction
(statsmodels `mcnemar`, as R `mcnemar.test`), with the change in the percent and its 95 % interval
from R `exact2x2::mcnemarExactDP`; `p_value_by="exact"` gives the exact binomial test on the rows
that changed (as R `exact2x2::exact2x2(paired = TRUE)`). Two columns of three or more categories:
Bowker's test of symmetry (statsmodels `SquareTable.symmetry`, as R `mcnemar.test` on the k x k
table).

### New tests

- `table.compare_matched("week_0", "week_4", "week_8")`: three or more measurements of the same
  rows. Numbers: the Friedman test (SciPy, as R `friedman.test`), with Kendall's W and its
  bootstrap interval from R `effectsize::kendalls_w` (R seed 1); `test="quade"`: the Quade test (R
  `quade.test`). Yes/no columns: Cochran's Q (statsmodels, as R `DescTools::CochranQTest`). With two
  columns it is `compare_before_after`.
- `table.compare_shapes("marks", for_each="class")`: do the groups differ in the whole shape of
  their values? Two groups: the two-sample Kolmogorov-Smirnov test (SciPy `ks_2samp`, exact as R
  `ks.test`; with tied values R's exact p-value, which SciPy does not give, comes from R). Three or
  more: the Anderson-Darling k-sample test (SciPy `anderson_ksamp`, as R `kSamples::ad.test`
  version 2), with a p-value from shuffling the group labels 9999 times (seed 1).
- `table.check_random_order("marks", sorted_by=None)`: the runs test above and below the
  median (statsmodels, as R `randtests::runs.test`, which leaves out values equal to the median; so
  does simplydata, and says so). Next to `check_steady`; the earlier name `compare_to_random_order`
  still works, with a note.
- `sdata.compare_averages(averages=, standard_deviations=, counts=, names=)`: Welch's t-test (SciPy
  `ttest_ind_from_stats`, as R `BSDA::tsum.test`, whose interval of the difference simplydata uses)
  or, for three or more groups, Welch's ANOVA (statsmodels `anova_generic`, the same as R
  `oneway.test` on the rows), from the summary numbers of a paper or report. `names=` names the
  groups (as on `add_group_column`; `groups=` still works, with a note).
- `sdata.compare_counts([[20, 40], [30, 30]])`: `compare_counts` on a table of counts.

### Effect sizes with their intervals, from R effectsize

- Every effect size now comes with its 95 % interval: Hedges' g, Cohen's d and d_z, omega-squared,
  the rank-biserial correlations (also per pair in `compare_each_pair`), rank epsilon-squared
  (bootstrap interval, R seed 1), and the intervals of Cramer's V and Cohen's w. They come from R
  effectsize (`simplydata[r]`); simplydata's own formulas are removed. Cramer's V (SciPy), Cohen's w
  and Cohen's h (statsmodels) still come from Python.
- Without R the test runs as before; the effect size from R is left empty and one line says how to
  add it.
- `how_many_needed` and `chance_to_find` call statsmodels' power classes (`TTestIndPower`,
  `TTestPower`, `FTestAnovaPower`, `GofChisquarePower`, and their `solve_power`) instead of
  simplydata's own formulas, with the same numbers as R `power.t.test()` (strict = FALSE) and pwr;
  correlations call R `pwr::pwr.r.test` (`simplydata[r]`). The exact number needed now agrees with
  R to about 1e-4 (R's own search precision); the rounded-up number is unchanged.

### python-control for systems: `simplydata[systems]`

The rise time, settling time and overshoot of a step response and the gain and phase margins come from
python-control (`step_info`, `stability_margins`), the established Python package for control systems; R
control has neither. Install it with `pip install "simplydata[systems]"`; without it the responses still
come, with a note.

### R itself, for what only R gives: `simplydata[r]`

Where no Python package gives R's answers, simplydata now runs R's own code through rpy2.
Install once: `pip install "simplydata[r]"`, R from https://cran.r-project.org, and in R
`install.packages(c("vegan", "survival", "mice"))`. Without R these words print what to install
(and name the Python alternative, with its different numbers); there is no fallback of our own.

- `add_clusters()` with k-means: R `kmeans(nstart = 25)` after `set.seed(seed)`.
- `add_nmds()`: R `vegan::metaMDS()`, at least `tries=` starts and up to 100 until the best
  map repeats.
- `compare_profiles()`: R `vegan::adonis2()`, `betadisper()` and `permutest()`; the p-values
  are now exactly R's for the same seed.
- `explain_survival()`: the proportional-hazards check is R `survival::cox.zph()`; without R
  the model is still fitted and a note says how to add the check.
- Smoothing splines with `smoothness="auto"`: R `smooth.spline()` chooses the smoothness (a
  number for `smoothness=` needs no R).
- `explain(..., empty_cells="multiple imputation")`: the results are pooled by R
  `mice::pool()` (Barnard-Rubin degrees of freedom).
- R's warnings are passed on as plain notes, such as
  `Note from R (vegan): some squared distances are negative and changed to zero.`
- Lessons 16, 17 and 18 (and day 17 of the 30-day guide) have a "Needs R" box.

### Signals and time series (first words)

- `table.spectrum_of("signal", sorted_by="time")` and `nums.spectrum_of(time_step=0.01)`: which repeating
  cycles a column holds and how strong each is. method="periodogram" (SciPy; 2 x R `spec.pgram` with
  taper 0, so the powers add up to the variance), "welch" (window= readings per piece) or
  "lomb-scargle" for uneven times (R `lomb::lsp` itself, needs `simplydata[r]`). show="power",
  "decibels" or "amplitude"; between= keeps a frequency range; for_each= one spectrum per group.
  `time_step=` is the time between readings (`sampling_rate=` and `fs=` are accepted).
- `table.check_steady("signal", sorted_by="time")`: does a column stay steady over time, or wander?
  The ADF and KPSS tests together, run in R (`tseries::adf.test`, `tseries::kpss.test`), with R's
  table p-values ("below 0.01", "above 0.1" when outside the tables). around="straight line" checks
  steadiness around a trend. Needs `simplydata[r]`.
- `table.autocorrelation_of("signal", sorted_by="time")` and `nums.autocorrelation_of(rows_back=10)`: how much
  a column is like itself some rows back, with the noise band of R `plot.acf` (band="white noise", or
  "bartlett" as R `ci.type = "ma"`), show="correlation" (R `acf`), "partial" (R `pacf`) or "covariance",
  and the Ljung-Box test of all of them together (R `Box.test(type = "Ljung-Box")`). From statsmodels.
- `table.correlation_between("a", "b", rows_back=12, sorted_by="date")`: the cross-correlation for shifts -12 to
  12 (statsmodels `ccf`, as R `ccf` with the sign of the lag reversed), and which column follows the other.
- `table.add_trend_and_season("visitors", sorted_by="month", repeats_every="year")`: adds the trend, the season and
  the rest as three columns. method="loess" (R `stl`: statsmodels STL with R's settings; season_window="fixed" runs
  R `stl(s.window = "periodic")` itself), "moving averages" (R `decompose`, season "added" or "multiplied") or
  "straight line" (one statsmodels least-squares fit of the line and the season effects, as R `lm`).
- `table.trend_of("visitors", sorted_by="month")`: Sen's slope with its 95 % interval (SciPy `theilslopes`, as R
  `trend::sens.slope`) and the Mann-Kendall test (R `trend::mk.test` itself); repeats_every= gives the seasonal test
  and slope (R `trend::smk.test`, `trend::sea.sens.slope`; per cycle, per year for months). Without R the slope
  is still given. Dates one calendar step apart give the slope per month (quarter, year); other dates per day
  from the dates themselves, so weekly readings and gaps count right.
- `table.forecast("visitors", sorted_by="month", steps_ahead=12, repeats_every="year")` and `nums.forecast(...)`:
  the next values with a 95 % prediction interval (interval=; columns "forecast 95 % prediction low" / "high"),
  the time column carried on. method="exponential smoothing"
  (R `HoltWinters`, with trend= and season "added" or "multiplied"), "last value", "same season last time",
  "average", "straight on" ("drift" and "line from first to last" accepted) (R `forecast::naive`, `snaive`, `meanf`, `rwf(drift = TRUE)`) or "arima" with order=
  and seasonal_order= (R `arima(method = "ML")`). check_on_last=12 holds back the last rows and measures the
  error (R `forecast::accuracy`: MAE, RMSE, MAPE, MASE); show="model" gives the fitted weights or estimates. A
  Ljung-Box test says whether the leftover errors look like noise. All in R itself (statsmodels' exponential
  smoothing and SARIMAX give other numbers). Needs `simplydata[r]`.
- `table.compare_forecasts("visitors", sorted_by="month", repeats_every="year")`: each method fitted on all but
  the last rows and ranked by MASE on them (R `forecast::accuracy`). Needs `simplydata[r]`.
- `table.find_change_points("nitrate", sorted_by="date", for_each="station")`: where the average (or, with
  change="average and spread", also the spread) jumps, by R `changepoint::cpt.mean` / `cpt.meanvar` (PELT,
  penalty="mbic" as R); one row per piece with its average. Needs `simplydata[r]`.
- `sdata.dates("2026-01-01", to="2026-12-31", every="day")` (or how_many=; every="month", "15 minutes", "2 weeks"
  ...): a one-column table of regular dates. Month steps count from the first date, so a run from the 31st stays
  on the month's last day (pandas DateOffset; R's seq(by = "month") overflows instead).
- `table.add_missing_dates("date", every="day", for_each="station")`: a row for every missing date (empty cells),
  between= to extend the run; every= found from the most common step when not given. Month-end dates stay month
  ends (2023-04-30, 2023-05-31, ...; also in forecasts), and dates with a time zone step by the clock of that zone
  (between= is read in it), so a summer-time change does not break every="day".
- `table.add_rolling_column` gains window="7 days" (a window of time, pandas rolling("7D")), centre=True (R stats::filter(sides = 2)), and show= "variance",
  "skewness", "kurtosis", "percentile" (percent=), "count", "correlation" and "covariance" (two columns). window="all"
  (from the first row, pandas expanding) is accepted with a note: running values are planned as their own word,
  add_running_column.
- `nums.smooth(method=..., window=...)` and `table.add_smoothed_column(...)`: "moving average" (weights=, ends=
  "empty"/"shorter windows"/"mirror"; R stats::filter), "median" (R runmed itself, Tukey's end rule; needs
  simplydata[r]), "savitzky-golay" (R signal::sgolayfilt), "exponential" (newest_weight=, alpha=, span=,
  half_life=, com=), "gaussian" (width=), "lowess", "spline", "whittaker" (SciPy 1.17 or newer, so Python 3.12 or newer) and "wiener", from SciPy, pandas and
  statsmodels.
- `nums.remove_trend()` (breaks= for a separate line per piece; SciPy detrend, as R residuals(lm(x ~ t))).
- `nums.keep_frequencies(below=10, time_step=0.005)` / `remove_frequencies(...)` and `table.add_filtered_column(...)`:
  low-pass, high-pass, band, band-stop, notch (equal_to=, width=; and_multiples= for a comb) and peak filters.
  method= "butterworth", "chebyshev", "chebyshev 2", "elliptic" or "bessel"; steepness= the order; both_ways=True
  runs forwards and backwards (SciPy sosfiltfilt; MATLAB's ends rule), both_ways=False forwards only (as R
  signal::filter).
- `find_peaks` / `find_dips` on numbers and tables (at_least= / at_most=, apart=, stands_out_by=, wide_at_least=;
  SciPy find_peaks, positions as R pracma::findpeaks).
- `nums.fourier_transform()` and `sdata.inverse_fourier_transform(table)` (SciPy fft, as R fft), `nums.envelope()`
  (SciPy hilbert, as R gsignal::hilbert), `nums.convolve_with` / `deconvolve_by` (as R convolve, pracma::deconv),
  `nums.change_time_step(to=)` (SciPy resample, resample_poly, decimate), `sdata.wave(...)` and
  `sdata.window_shape(...)` (SciPy; as R gsignal).
- `.wav` sound files: `sdata.numbers("call.wav", channel=1)` reads the readings scaled to -1 to 1 (whole-number files divided by 2^(bits - 1), as MATLAB audioread; R tuneR::readWave keeps the whole numbers) and the numbers
  remember their time step; `nums.save("tone.wav", bits=16)` writes one (SciPy io.wavfile).
- `table.add_envelope_column("signal_envelope", from_column="signal", ...)` (show="envelope", "phase" or
  "frequency"; SciPy hilbert, as R gsignal::hilbert; the new column's name is needed, as on every
  add_..._column word), `sinc(x)` in formulas (as NumPy), and `show_filter=True` on the filter words (the
  filter's Bode chart, titled "run forwards once", and the line that saves it:
  `sdata.frequency_filter(keep_below=10, time_step=0.005).chart().save("filter.png")`).
- Linear systems: `sdata.system("1 / (s**2 + 2*s + 5)")` (or numerator= / denominator=, poles= / zeros= / gain=,
  the matrices a=, b=, c=, d=; z and time_step= for a system in steps; R's num= / den= and A= to D= are
  accepted, but not together with the main spelling) with `step_response(until=, how_many=, time_points=)`
  (rise time, settling time, overshoot from python-control `step_info`; time_points= start at 0),
  `impulse_response`, `response_to(inputs, time_points=)` (inputs in other steps than the system are refused),
  `frequency_response(between=, how_many=, unit=)` (columns gain, "gain (decibels)", "phase (degrees)"; the gain
  and phase margins from python-control `stability_margins`; unit="radians per second" or "cycles per second", "hertz" accepted), `poles` (real part,
  imaginary part, distance from 0, damping ratio, natural frequency), `zeros`, `is_stable`, `steady_gain`,
  `in_steps(time_step=, method=)`, `then`, `add` (side by side, outputs added), `with_feedback(through=, sign=)`,
  `table(form=)` ("power of s" or "power of z", numerator, denominator; "real part" and "imaginary part" for
  poles and zeros) and `chart(show="bode" | "step" | "impulse" | "poles and zeros" | "nyquist", between=, until=,
  unit=)` (an option a chart does not use is refused). sdata.system(poles=, gain=) says that gain= is the number
  in front of the formula, not the steady gain. SciPy signal (lti, dlti, step, lsim, freqresp, freqz,
  cont2discrete, tf2ss), checked against R control, signal and by hand.
- `sdata.frequency_filter(keep_below=10, time_step=0.005)`: the filter of add_filtered_column as a system in steps.
- Chart words: `sticks` (a stem chart), `autocorrelation_bars`, `cross_correlation_bars`, `lag_dots`,
  `trend_and_season` (four panels: the column, its trend, season and rest), `forecast` (dashed line and interval
  band after the lines), `spectrum`, `spectrum_over_time` (SciPy spectrogram) and `peak_dots`. They draw the
  numbers of the table words. The five that draw something other than the column against time take the column
  first and `sorted_by=`, as their table words do: `chart.spectrum("signal", sorted_by="time")`,
  `chart.cross_correlation_bars("signal", "vibration", sorted_by="time")`; x= and y= still work, with a note.
- `add_smoothed_column` without a name adds "<column>_smoothed" (as "_filtered"); `nums.spectrum_of(method=
  "lomb-scargle")` takes the times as `time_points=`.
- Lessons on time series (dates, missing days, time windows, smoothing and trend), forecasts checked on held-back
  months, cycles (spectra, filters, peaks and dips; Welch and check_steady as "more" parts) and, optional, linear
  systems (starting from the filter of the cycles lesson; the Bode chart, margins and systems in steps as "more"
  parts). They come after the lessons of S1 and S2, found by title, so they become lessons 23 to 26. The 30-day
  beginner track gives them a day of their own (day 27), and so does the Python track (day 20; values between
  points moves to day 17, with patterns across many columns).
- `chart.smooth_line(method=...)` takes the methods of `nums.smooth` ("moving average", "median",
  "savitzky-golay", "exponential", "gaussian", "whittaker", "wiener") for evenly spaced x.
- New practice table `visitors`: monthly visitors to two made-up museums, 2014 to 2025.
- New practice table `river`: daily water level and nitrate at two made-up stations, 2024 to 2025, with
  missing days and a few empty cells.
- New practice table `sensor`: five seconds of a made-up sensor at 200 readings per second.

### Fitting

- `table.fit_line(x=, y=)` is the main name of the straight-line fit, the same word as
  `chart.fit_line`; `fit_straight_line` still works for one release, with a note.
- `table.fit_curve(x=, y=, degree=2)` fits a polynomial by least squares (R
  `lm(y ~ poly(x, 2, raw = TRUE))`), with an interval for each term; `weights=` and `for_each=`.
- `table.fit_formula` takes `between=` (limits for the values to find, as R
  `nls(algorithm = "port")`), `weights=`, `for_each=`, `search="whole range"` (differential
  evolution, seed 1, then a least-squares polish) and `method=`, and gives standard errors,
  t, p-values, 95 % intervals, the residual standard error and AIC, as R `nls()`.
- `table.add_predicted_column("population = a * exp(b * (year - 2000))")` fits a formula and adds
  its value for every row (or takes the values of a fit with `using=`).
- On charts: `chart.fit_formula(...)` draws the fitted formula for each colour group and
  `chart.curve(...)` draws any formula of x, or a distribution.

### Finding and solving

- `sdata.find_smallest` and `sdata.find_biggest` find where a formula is smallest or biggest:
  on a range (Brent's method, R `optimize()`), from a start (Nelder-Mead, R `optim()`), with limits
  (L-BFGS-B), under rules (SLSQP; linear programming with HiGHS when everything is a straight line,
  with the value of one more of each rule; `whole_numbers=True` for mixed-integer programming), or
  over the whole range (differential evolution). The method is always printed, never switched
  silently.
- `sdata.solve` finds every solution of an equation in a range (R `uniroot()` on each sign change),
  all roots of a polynomial, complex ones too (R `polyroot()`), and solves sets of equations
  (R `nleqslv`), exactly when they are linear.
- `known=` takes the values of a `fit_formula` result, so a fitted curve can be solved or
  searched straight away.

### Values between points

- `table.values_at(column, at={"year": [2001, 2003]})` estimates a column between the known
  points: `joined_by="straight lines"` (R `approx()`), `"smooth curve"` (natural cubic spline),
  `"curve without overshoot"` (PCHIP), `"steps"` or `"nearest"`, or `smoothness="auto"` for a
  smoothing spline (R `smooth.spline()`); in two or more directions (bilinear on a full grid,
  triangles or a thin-plate spline for scattered points). `outside=` says what happens beyond the
  known points.
- `table.map_of(column, across=["east", "north"])` fills an evenly spaced map, ready for a contour
  map or heatmap.
- `fill_empty_cells(with_the="curve between neighbours")` and `"curve without overshoot"`;
  `chart.lines(joined_by=...)` and `chart.smooth_line(method="spline")`.

### Distributions

- `sdata.distribution("normal", average=50, standard_deviation=10)` for 26 named distributions
  (R's parameters with plain names; R's own names work too) and any other SciPy distribution.
  Its words: `chance` (above=, below=, at_most=, at_least=, between=, or exactly a count),
  `density_at`, `percentile`, `cut_off`, `middle_range`, `average`, `median`,
  `standard_deviation`, `variance`, `summary`, `random_numbers`, `chart`, `table` and
  `parameters`. Each sentence prints the R call that gives the same answer.
- `table.fit_distribution` and `nums.fit_distribution` fit by maximum likelihood (as R
  `MASS::fitdistr`) and give back the fitted distribution; `table.compare_distributions` ranks
  several by AIC, with the goodness-of-fit statistics of R `fitdistrplus::gofstat()`.
- `table.compare_shape_to(column, "gamma")` checks any smooth shape: the Anderson-Darling test with
  a Monte Carlo p-value that allows for the fitting (seed 1). `"normal"` keeps Shapiro-Wilk.
  `samples=` (9999 by default) sets how many simulated samples are refitted. They are refitted
  all at once with the exact likelihood equations, so most shapes take a second or two (Weibull
  went from about a minute to under a second, with the same p-value); t, Cauchy and F are still
  refitted one by one, and a short note says so before a run expected to take more than 10 seconds.
- On charts: `chart.fit_distribution("gamma")` over a histogram or density, and
  `chart.qq_dots(column, distribution="gamma")`.

### Names from other tools

- Names that people bring from pandas, NumPy, SciPy, R, matplotlib and ggplot2 (`sdata.minimize`,
  `sdata.curve_fit`, `sdata.pnorm`, `table.groupby`, `table.merge`, `chart.hist`, `chart.axhline`
  and about 400 more) never run: each says "In simplydata this is ..." with the word to use.
  `sdata.help("minimize")` explains them too.

### Dictionary

- `docs/manual/simplydataDictionary.pdf`: every word A to Z (one entry per word, with a part for
  each object that has it, such as `fit_line` on tables and charts), each with its meaning, a short
  example, its main options, the names other tools use for it, related words and the page of the
  manual that explains it (a link that opens the manual there), plus the lesson that teaches it.
  Its last part, "Coming from another tool?", turns every name from other tools and every old name
  into the simplydata word. It is made from the code by `docs/make_dictionary.py`; building the
  manual (`python docs/make_manual.py`) builds the dictionary too, with the manual's page numbers,
  and a test fails if a word has no page or the pages come from an older manual.

### Lesson 21: working with a model

- `sdata.lesson(21)` "Working with a model: check it, compare it, predict with it": worked examples for
  `check_model`, `show_rows_that_pull`, `compare_models` and `add_predicted_column(interval=95,
  for_new_rows=True)`, then a partly worked task (the learner writes the last line), a task, a task to do
  from memory, and `model_averages_of` last, in an example and a task that need R and may be left out.
  The two tasks on these words that lesson 16 had move here, so lesson 16 keeps its own words.
- The 30 days teach it the day after the models day (day 16 of the Python track, day 23 of the beginner
  track); its words come back in the warm-ups about 3 and 7 days later, and the final test asks for
  `check_model` and `compare_models` from memory. In the Python track lessons 17 and 18 move one day on,
  fitting, finding and distributions share day 19, and values between points shares day 20 with the
  time-series lessons of v0.6.

### 30 days of simplydata

- `sdata.start_30_days(track="python")` starts a course of 30 days of about an hour each:
  `track="python"` for people who already write some Python (about two lessons a day, review days
  on days 7, 14, 21 and 28, then an eight-day project of their own), `track="beginner"` for people
  who have never programmed (three days of just enough Python first, then about one lesson a day
  and a small project). Both cover all the lessons and end with a final test from memory.
- `sdata.today()` shows the day to do next: a 5-minute warm-up of questions on earlier days
  (yesterday, about three days ago, about a week ago; review days mix the whole course), what to do
  (the lesson, the manual's sections and the words to look up) and a task to do without looking
  back. A missed day is never lost: `today()` carries on where you stopped, says so kindly if you
  have fallen behind the calendar, and `today(follow_calendar=True)` jumps to the calendar's day.
- `sdata.day(5)` shows any day (`sdata.day()` lists all 30 with ticks), `sdata.answers(5)` gives
  the warm-up answers and a worked answer to the task, and `sdata.next_day()` goes on now.
- The progress (track, start date and the date each day was opened) is kept only in a small file
  on your computer, `~/.simplydata/progress.json` (`SIMPLYDATA_PROGRESS_FILE` chooses another);
  nothing is sent anywhere.
- `docs/manual/simplydata_30_days.pdf`: the same days on paper, with a calendar to tick for each
  track, one page per day (warm-up questions with lines for the answers, the manual's page for each
  lesson, section and word, and the task) and the answers at the back. It is made by
  `docs/make_30_days.py` from the same source as `sdata.today()` (`simplydata/learn_days.py`), and
  building the manual builds it too. Every piece of code in the days runs in the tests.
- Lesson 1, `sdata.lesson()` and `sdata.help()` say that the 30 days exist; `sdata.help("course")`
  and `sdata.help("tutorial")` point to `start_30_days`.

### Not in this release

Robust (outlier-resistant) curve fitting, gradients given by hand, profile-likelihood intervals
for formula fits, mixtures and truncated distributions, distributions of several variables, and
slopes and areas under splines.

### Models

- `table.explain(column, using=[...])` explains one column from several others: a linear model
  by least squares (multiple regression), with `"a * b"` for an interaction and text columns as
  groups. `outcome="yes or no"` is logistic regression, `outcome="counts"` Poisson regression
  (`"counts (overdispersed)"` quasi-Poisson), `grouped_by=` a mixed model with a random intercept
  per group, and `empty_cells="multiple imputation"` fills empty cells 20 times and pools the
  answers with Rubin's rules.
- `table.add_predicted_column` adds what the model expects for each row.

### Patterns across columns

- `add_principal_components` and `principal_components_of` (PCA), `add_clusters` (k-means or
  hierarchical), `distances_between_rows` (Bray-Curtis, Euclidean, Jaccard, Manhattan),
  `add_nmds` (non-metric multidimensional scaling) and `compare_profiles` (PERMANOVA, with a
  check of the spread of each group).

### Survival

- `survival_over_time` (Kaplan-Meier), `compare_survival` (log-rank test), `explain_survival`
  (Cox model, with a proportional-hazards check) and `chart.survival_curves` (with confidence
  bands, censoring ticks and a number-at-risk table).

### Planning a study

- `sdata.how_many_needed` and `sdata.chance_to_find`: power analysis for the averages, counts and
  correlation tests.

### More tests and summaries

- `compare_spreads` (Levene's test centred on medians, Bartlett or Fligner-Killeen),
  `compare_each_pair(..., test="tukey")` (Tukey's honest significant difference),
  `compare_counts_to` (chi-square goodness of fit) and `compare_percent_to` (exact binomial test).
- `percentile_of`, `most_common_of`, and new `summary_of(show=...)` measures: geometric mean,
  skewness, kurtosis, coefficient of variation, median absolute deviation, trimmed average, most
  common value and any percentile.
- Formulas know `exp`, `sin`, `cos`, `tan`, `pi` and special functions: `erf`, `erfc`, `gamma`,
  `lgamma`, `digamma`, `beta` and `besselJ`.

### Charts

- `colour_scale` chooses the colours for numbers (heatmaps, contour maps, dots coloured by a
  number): named colour-blind-safe scales, your own colours, `middle=`, `log=True`, `steps=` and
  `between=`.
- `transparency=` on every chart type (also survival curves) and `thickness=` on lines.
- `tick_format_x` / `tick_format_y` (percent, thousands, decimals, scientific, dates), and
  `ticks_x(every=...)` / `ticks_y(how_many=...)` for tick spacing, also by year, month or week.
- Histogram options: `show="percent"` or `"density"`, `stacked=`, `steps=`, `cumulative=` and
  `bin_width=`.
- `line_with_slope` (for 1:1 lines), `qq_dots` (Q-Q plots), `cumulative_share` (ECDF) and
  `font_name`.

### Choosing parts by position

- Printed tables number their rows from 1 (`show`, `show_first_rows`, `show_last_rows`, `print`,
  notebooks), so the last row of a 54-row table is row 54; `show_rows_with_outliers` shows each row
  with its number in the whole table. Only the display changes: `as_pandas()` keeps pandas' own
  index.
- `table.keep_rows_by_position(10, to=20)` and `remove_rows_by_position`: rows by their place,
  counting from 1 with both ends included (rows 10 to 20 are 11 rows), `to="last"`, `step=` for every
  n-th row and a list such as `[1, 5, 9]` (as pandas `iloc` and Polars `slice`/`gather_every`).
  `keep_columns_by_position` and `remove_columns_by_position` do the same for columns and say which
  columns they were.
- `table.row(3)` gives one row as a dict, `table.cell_at(row=3, column="marks")` one cell, and
  `table.reverse_rows()` turns the table upside down.
- `keep_columns` and `remove_columns` take a run of names (`keep_columns("hours", to="height")`),
  `kind="number"` (or `"text"`, `"date"`, `"true/false"`), `starts_with=`, `ends_with=`, `contains=`
  and `pattern=`.
- `replace_values` takes the `keep_rows` conditions: `replace_values("marks", above=100,
  with_value=100)`.
- Numbers: `nums.keep_numbers_by_position(3, to=8)`, `remove_numbers_by_position`, and
  `nums.replace_numbers(-999, with_value=None)` or `replace_numbers(above=100, with_value=100)`.
- Grids: `keep_rows_by_position`, `keep_columns_by_position`, `remove_rows_by_position`,
  `remove_columns_by_position` (a block is two steps) and `grid.replace_numbers`. `grid.keep_numbers`
  explains why a grid cannot drop single numbers.
- `"last"` is a position everywhere, also in `nums.number_at`, `grid.row`, `grid.column` and
  `grid.number_at`.
- `table[...]`, `table.marks` and loops over a table explain the words to use instead;
  `iloc`, `iat`, `select_dtypes`, `clip`, `np.where` and other names point to the new words.
- Lesson 10 teaches choosing by position, with a task to do from memory.
- Not yet: setting one cell by position, positions of matching numbers (argwhere, argmax), clip as
  one word, random fractions and sampling with replacement, grid diagonals and flips, unions of
  column choices, nested columns.

### Also

- Example tables `school`, `meadow` and `trial`; lessons 16 to 20; the new words are also taught
  in lessons 3, 5, 6, 11, 12 and 14. Lessons 19 and 20 end with a task that asks you to recall
  the words without looking back.
- The optional extra `stats` (statsmodels), needed only for mixed models and multiple
  imputation.
- Panel letters on a page no longer cover the panel titles of a chart made with
  `one_chart_per`.
- `chart.all_dots` drawn over `boxes` or `violins` uses dark grey dots (or, in colour groups, a
  dark rim), so the dots no longer vanish into boxes of the same colour; `colour=` still wins.

## 0.1.0 (2026-11-12)

The first release: charts, tables, numbers and statistical tests in one small vocabulary.

### Charts

- About 70 words over matplotlib and seaborn: `bars`, `lines`, `dots`, `histogram`, `boxes`,
  `violins`, `heatmap`, `pie`, `error_bars`, `fit_line`, `smooth_line`, `density` and more.
- Titles, labels, legends, ranges, log scales, lines and shaded bands, notes with arrows,
  second y-axis, zoom insets, polar and 3D charts, animation.
- Panels: `sdata.grid(a, b, letters=True)` and `one_chart_per(down=, across=, per_row=)`.
- Months and weekdays in calendar order; `label_legend`, `names_on_dots`, `band`.
- Saving for journals: `chart.size(width=17, height=8, unit="cm")` (inches, cm, mm or pixels)
  gives a file of exactly that size, and `chart.save("figure.tif", resolution=600)` sets the dots
  per inch.
- Charts say how many rows with empty cells they left out; `chart.empty_cells()` shows where
  the gaps are.

### Tables

- Tables on pandas or Polars (through narwhals), with `undo()` and `start_again()`.
- Reading CSV, Excel, whole folders and web addresses; decimal commas and codes such as "NA";
  Word, SPSS and Stata files with the `files` extra.
- Choosing rows, including written conditions: `keep_rows("marks > 50 and class == 'A'")`.
  An empty cell never meets a condition.
- Cleaning: `remove_rows_with_empty_cells`, `fill_empty_cells` (also
  `with_the="line between neighbours"`), `add_is_empty_column`, outliers by Tukey's rule.
- Dates (`make_dates(order=)`, parts of dates, days between dates, `after=`/`before=`), text
  (split, join), rolling averages, previous values and changes, shares per group.
- Summaries: `average_of`, `summary_of`, totals per week, month or year (`every=`), cross
  tables and correlation tables.

### Numbers

- `sdata.numbers`, `sdata.number_grid` and `sdata.random_numbers` over NumPy, with plain words
  and `undo()`.

### Statistical tests

- `compare_averages` (Welch's t-test or Welch's ANOVA; rank tests on request),
  `compare_each_pair` (Holm-adjusted), `compare_before_after`, `compare_average_to`,
  `compare_counts` (chi-square, or Fisher's exact test), `compare_shape_to`,
  `fit_straight_line`, `fit_formula`, adjusted p-values.
- Effect sizes: Hedges' g, omega-squared, Cramér's V. Results checked against R 4.6.2.

### Learning

- `sdata.lesson(1)` to `sdata.lesson(15)`, `sdata.words()`, `sdata.help("word")`,
  `sdata.example()` tables (marks, weather, fruit, growth, island, shop), worked solutions.
- A cheat sheet (`docs/cheatsheet.md`) and a manual (`docs/manual/simplydata_manual.pdf`),
  both made from the code.
