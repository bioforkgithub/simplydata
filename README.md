# simplydata

[![PyPI](https://img.shields.io/pypi/v/simplydata)](https://pypi.org/project/simplydata/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24210045.svg)](https://doi.org/10.5281/zenodo.24210045)

**Learn basic Python, and simplydata takes you from your first table to sound statistics, in plain words, with its results checked against the field's standard tools.**

*simplydata is a package that is easy for a beginner, honest with a reviewer, and [safe for sensitive data](#privacy-your-data-stays-on-your-computer), all at once.*

**For researchers and students who want to be fast and correct.**

***Easy to do, and you know why you're doing it.***

## Install

```
pip install simplydata
```

You need Python 3.11 or newer. conda is coming soon, once the conda-forge review is done. Extras and the
methods that need R: [Install in detail](#install-in-detail). Type the code in an editor that completes names
for you: we recommend VS Code or Jupyter ([where to type the code](#where-to-type-the-code)).

## Quick start

Open a practice table, look at it, keep the rows you need, compare two groups, draw a chart and save:

```python
import simplydata as sdata

table = sdata.get_example("marks")              # a practice table; yours: sdata.table("my_file.xlsx")
table.show_first_rows()                                        # look at it
table.keep_rows_where("subject", is_equal_to="Maths")          # one row for each child
table.keep_rows_where("class", is_one_of=["A", "B"])           # the two classes to compare
table.compare_averages_of("marks", for_each_group_in="class")  # a real difference, or chance?

chart = table.start_chart()
chart.draw_boxes(x="class", y="marks")
chart.save("maths_marks.png")
table.save("maths_marks.xlsx")
```

What it prints:

```text
   name class  subject  hours  marks  height
1  Asha     A    Maths    6.3     61     144
2  Asha     A  Science    3.8     66     144
3  Asha     A  English    7.6     77     144
4   Ben     A    Maths    6.4     73     152
5   Ben     A  Science    9.2     98     152
Kept 18 of 54 rows.
Kept 12 of 18 rows.
The average "marks" is 68.3 in A and 65.7 in B: A is 2.67 higher (95 % CI of the difference -19.7 to 25.0).
If there were truly no difference, a difference this big or bigger would turn up in about 79 of 100 studies like this one (p = 0.791). This does not show that there is no difference.
Test: Welch's t-test (t = 0.274, df = 8.20), the usual test for two averages; it does not assume both groups have the same spread.
Note: Hedges' g and its 95 % CI come from the R package effectsize, which is not ready here; to add them: pip install "simplydata[r]", install R, then in R install.packages("effectsize").
```

At the end of the script it also lists the packages that did the work (pandas, SciPy, statsmodels, matplotlib,
seaborn ...), with the references their authors ask you to cite. Each child has three rows in this table, one per
subject, so the example keeps one subject: a test of two groups needs one row for each child.

**Names that say what they do.** `keep_rows_where`, `compare_averages_of`, `find_correlation_between`: you read
code more often than you write it, you can guess a name from what you want to do, and your editor completes it
after three or four letters. Here is the same work in simplydata and in the package underneath, taken from the
manual's "same underneath" boxes, which the tests run and compare. Both give the same numbers; one you can read at
first sight.

<table>
<tr><th>simplydata</th><th>the same in pandas or SciPy</th></tr>
<tr><td>

```python
table = sdata.get_example("marks")
table.keep_rows_where("marks", is_above=50)
```

</td><td>

```python
import pandas as pd
df = pd.read_csv("marks.csv")
df[df["marks"] > 50]
```

</td></tr>
<tr><td>

```python
table = sdata.get_example("trial")
table.compare_averages_of("days", for_each_group_in="treatment")
```

</td><td>

```python
from scipy import stats
import pandas as pd
df = pd.read_csv("trial.csv")
a, b = [rows["days"] for _, rows in df.groupby("treatment", sort=False)]
res = stats.ttest_ind(a, b, equal_var=False)
{"statistic": res.statistic, "degrees of freedom": res.df,
 "p-value": res.pvalue, "difference": a.mean() - b.mean()}
```

</td></tr>
<tr><td>

```python
table = sdata.get_example("weather")
table.keep_columns("month", "city", "temperature")
table.spread_into_columns(names_from="city", values_from="temperature")
```

</td><td>

```python
import pandas as pd
df = pd.read_csv("weather.csv")[["month", "city", "temperature"]]
wide = df.pivot(index="month", columns="city", values="temperature")
wide = wide.loc[df["month"].unique(), df["city"].unique()]
wide.reset_index().rename_axis(columns=None)
```

</td></tr>
</table>

simplydata also prints each answer as a sentence and names the method it used.

## Where to go next

- **Learn it step by step:** [the 30-day guide (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_30_days.pdf), or in Python `sdata.start_30_days(track="beginner")`. Short lessons: `sdata.show_lesson(1)`.
- **Look up a word:** [the manual (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.pdf), [the cheat sheet (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/simplydata_cheat_sheet.pdf), [the dictionary (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydataDictionary.pdf), or `sdata.help("compare_averages_of")`.
- **Can I trust it?** [How much is checked](#can-i-trust-it), the [reliability report](https://github.com/bioforkgithub/simplydata/blob/main/validation/report.md) and the separate [test repository](https://github.com/bioforkgithub/simplydata_tests).
- **Tell us:** a problem, a wrong answer or a word you missed, in a [GitHub issue form](https://github.com/bioforkgithub/simplydata/issues/new/choose); questions and ideas in [Discussions](https://github.com/bioforkgithub/simplydata/discussions).

> Status: early development (alpha). Charts, tables, numbers, statistical tests, fitting and distributions work, and
> their numbers are compared with the packages underneath and with R as described [below](#can-i-trust-it), but not every word is
> compared yet and the word list may still change (an old word keeps working for one release and prints a one-line
> note with its new name). Read each printout, and check an important result before you publish it.

## Questions new users ask

**Why not just learn pandas or R?**
You can, and simplydata is a way in, not a place to stay. It is a ramp, not a cage: every word hands the work to
pandas, Polars, NumPy, SciPy, statsmodels or an R package, the printout names the method it used, and for the words
that have it the manual shows the same job written in that package, in a grey "same underneath" box that the tests
run and check. You start with one small set of words built from a few verbs, instead of thousands of function names
in a dozen packages and two languages, and you can read the code underneath whenever you want to move on.

**Why are the names so long?**
On purpose. You read a line of code many more times than you type it, and `table.keep_rows_where("marks",
is_above=50)` reads as what it does. A name that says what it does can be guessed: if you want to keep rows,
the word starts with `keep_rows`. And you rarely type a whole name: in VS Code or Jupyter, type `table.keep`,
press Tab (or wait a moment in VS Code), and the editor lists `keep_rows_where`, `keep_columns` and the other
`keep_` words to choose from. See [where to type the code](#where-to-type-the-code).

**Why not ChatGPT, jamovi or JASP?**
They are good tools that do a different job. simplydata gives:

- **the same answer twice:** a script of simplydata words gives the same numbers every time you run it on the
  same data (random draws use a fixed seed). A chatbot can write different code, or choose a different method,
  each time you ask, and you must check its code yourself.
- **offline work:** nothing leaves your computer (see [Privacy](#privacy-your-data-stays-on-your-computer)). A
  chatbot on the web receives whatever you paste into it.
- **a script:** the whole analysis, from the raw file to the figure, is a short text file you can rerun on new
  data, send to a co-author and attach to a paper. jamovi and JASP are free point-and-click programs and a fine
  choice if you never want to write code; simplydata is for when you want the analysis written down as code.
- **answers checked against R:** the answers are compared with the package underneath and with R in a public
  reliability study, and many printouts name the R function that gives the same answer.

**Is it safe for sensitive data?**
simplydata itself sends nothing anywhere: no telemetry, no update checks, no crash reports. It reaches the network
only when you give `sdata.table` a web address, writes files only where you ask, and the tests check this on every
change with the network blocked. Details in [Privacy](#privacy-your-data-stays-on-your-computer). It does not
encrypt or anonymise data, so your institution's rules on where sensitive data, such as patient records, may be stored still apply.

**Do I need R?**
Not to start. `pip install simplydata` gives tables, charts, numbers, the common tests (t-tests, ANOVA, rank tests,
chi-square and Fisher), correlations, linear, logistic and Poisson models, distributions and fitting, all in
Python. R is needed only for methods that Python lacks, or that Python does not compute the way R does: for
example effect sizes with intervals (effectsize), meta-analysis (metafor), NMDS and PERMANOVA (vegan), mixed models
for yes/no answers and counts (lme4), and Bayes factors (BayesFactor). The full list is in
[What simplydata handles](docs/what_simplydata_handles.md#packages-underneath). A word that needs R and cannot find
it says what to install, as the note in the quick start does; see [Using the words that need R](#using-the-words-that-need-r).

## What simplydata handles

**431 words (commands) in 48 groups, with 398 different options, on top of 16 Python packages (10 installed always, 6 with an extra; patsy comes with statsmodels) and
87 R packages that it runs (plus R's own `stats`, and 15 more used only to check its answers), checked by 5659 reliability checks.** Every word hands the work to
an established package; simplydata chooses the settings, prints the answer in words and names the
method it used. Words that need an extra say so: `pip install "simplydata[files]"`,
`[systems]`, `[sql]` or `[r]` (the R words also need R itself; see [Using the words that need R](#using-the-words-that-need-r)).

**Simple words for data science in Python.** One small vocabulary: you can start in a day, and the 30-day guide
takes you further. It is built on matplotlib, seaborn, pandas, Polars, NumPy, SciPy and statsmodels (with narwhals linking
pandas and Polars), and on R through rpy2 for the methods only R has, so you don't have to learn
them first.

The full lists are in **[What simplydata handles](docs/what_simplydata_handles.md)**: how much simplydata reduces
the problem, every Python and R package it runs and what for, what you can do task by task and field by field, the
lessons one by one, and short examples by area.

### Can I trust it?

Every number comes from an established package, named in
[What simplydata handles](docs/what_simplydata_handles.md#packages-underneath). How much of that is checked, counted on 2026-11-23: the public
[reliability study](https://github.com/bioforkgithub/simplydata/blob/main/validation/report.md) compares 431 of the
431 words with the package underneath and with R (5659 checks), and the separate test repository
[simplydata_tests](https://github.com/bioforkgithub/simplydata_tests#what-the-comparisons-found) makes 26,718
comparisons on published reference data in 32 notebooks: 26,265 agree, 422 differ for a reason it explains, 29 are
simplydata errors being fixed and 2 were skipped. The other 0 words are not compared in the reliability study yet. The
[manual](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.pdf) has every word, with its
"same underneath" code for the words that have it.

## Learn: lessons, the 30-day guide and the manual

simplydata teaches itself. Open Python and type:

```python
import simplydata as sdata
sdata.show_lesson(1)
```

There are thirty-seven short lessons, from your first chart and table to models, survival, meta-analysis and
Bayesian answers; [the lessons one by one](docs/what_simplydata_handles.md#the-lessons-one-by-one). Each lesson has
an example you can run, says what every line does, explains the idea behind it (average or median, standard
deviation or standard error, p-values) and ends with a small task to try yourself.

- `sdata.show_lesson()` lists the lessons
- `sdata.show_all_words()` lists every word, with an example (also on the first pages of the [dictionary](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydataDictionary.pdf))
- `sdata.help("draw_bars")` explains one word: what it does, its options and an example
  (table and number words too: `sdata.help("keep_rows_where")`, `sdata.help("find_average")`)
- `sdata.get_example()` lists the tables to practise with, all made up (marks, weather, fruit, growth, sensor, visitors, river, shop, school, meadow, trial, clinic, island and more; shop has dates and empty cells); seven copy the columns of real studies (bcg, passive_smoking, ability_tests, sea_levels, sampled_schools, job_training, drug_levels), and simplydata was tested on the real data of those studies ([DATA_LICENSES.md](DATA_LICENSES.md)); `sdata.get_example("marks")` gives one back as a simplydata table, ready for every table word
- `sdata.show_lesson(3, solutions=True)` adds a worked solution to each "Try it yourself" task
- `sdata.show_packages_used()` lists the packages that did the work behind your words (pandas, SciPy, R packages ...), with versions and the references their authors ask for; a short list is also printed at the end of a script

### Or learn it in 30 days

Rather learn an hour a day? simplydata has a 30-day course built in:

```python
import simplydata as sdata
sdata.start_30_days()                  # you already write some Python
sdata.start_30_days(track="beginner")  # you have never programmed: starts with just enough Python
sdata.show_today()                     # every day: the day to do next
```

Each day starts with a 5-minute warm-up of questions on earlier days (answered from memory, which
fixes words better than reading them again), then the lesson to work through, and ends with a task
to do without looking back. You open a real practice table on day 1 or 2 and test a first difference
within the first week, with charts woven in between. Review days mix the whole course, the last week is a
project of your own, and day 29 is a final test from memory. The 30 days teach the everyday work (tables,
charts, summaries, tests, models, fitted curves and everyday time series); two extra days, patterns across
many columns and planning a study, are optional (`sdata.show_day(31)` and `sdata.show_day(32)`). The manual is
the complete reference, and a day points to it for the rest (forecasts, spectra and filters, systems, risks and
diagnostic tests). Missed a day? `sdata.show_today()` carries on where you
stopped. `sdata.show_answers()` gives the answers, `sdata.show_day()` the whole calendar, and `sdata.go_to_next_day()`
goes on now. Your progress is kept only on your computer, in `~/.simplydata/progress.json`.

**[30 days of simplydata (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_30_days.pdf)**
is the same course on paper: a calendar to tick for each track, one page per day with the page of
the manual for each lesson and word, and the answers at the back.

### Manual

**[The simplydata manual (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.pdf)** has everything in one book:
all thirty-seven lessons with the real charts and output they make, every word explained (its options,
an example you can run and the library that does the work underneath), the data science ideas
behind the numbers (average or median, standard deviation or standard error, confidence intervals,
p-values, effect sizes, and which statistical test to use when), and a worked solution for every
task.

**[Cheat sheet (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/simplydata_cheat_sheet.pdf)**: every command on learning cards, one card for each topic, with a short example, what it does and the package it calls. It is made from the code, like the manual.

**[The simplydata dictionary (PDF)](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydataDictionary.pdf)** opens with every word at a glance, group by group, then lists every word A to Z, with its meaning, an example and the page of the manual that explains it, and turns names from other tools (`groupby`, `iloc`, `hist`, `curve_fit` ...) into simplydata words.

The manual is made from the code by `python docs/make_manual.py` (it needs a LaTeX system with
`pdflatex`), so it never goes out of date: a test fails if
[docs/manual/simplydata_manual.tex](https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.tex) no longer matches the code. The same command builds the dictionary and the 30-day guide,
with the page numbers of the manual it has just compiled.

## Install in detail

### Where to type the code

Use an editor that completes names for you, so the long, clear names cost you three or four letters each. We
recommend one of these two:

**VS Code**

1. Install VS Code from https://code.visualstudio.com.
2. In its Extensions view, add the "Python" and "Jupyter" extensions.
3. Open a folder, make a file such as `analysis.py` (or a notebook, `analysis.ipynb`), and choose the Python
   where simplydata is installed (bottom right, or "Select Kernel" in a notebook).
4. Type `table.keep`: the list of words appears as you type. Ctrl+Space brings it up at any time.

**Jupyter (JupyterLab or Notebook)**

1. In the same Python as simplydata: `pip install jupyterlab`.
2. Start it with `jupyter lab`; it opens in your web browser and runs on your own computer.
3. Make a new notebook (Python 3) and type your code in a cell; Shift+Enter runs it.
4. Once the cell that makes `table` has run, type `table.keep` and press Tab to see the words that start
   that way.

Other editors (PyCharm, Spyder) also complete names; IDLE does very little, so it is not recommended.

### pip

**pip** (needs Python 3.11 or newer):

```
pip install simplydata            # with pandas, Polars, NumPy, SciPy, statsmodels, matplotlib and seaborn
pip install "simplydata[files]"   # adds reading Word, SPSS and Stata files
pip install "simplydata[systems]" # adds python-control: rise time, settling time and margins of systems
pip install "simplydata[r]"       # adds rpy2, the bridge from Python to R (install R itself from https://cran.r-project.org)
pip install "simplydata[sql]"     # adds DuckDB: SQL on a table or on files (run_sql), kept on this computer
pip install "simplydata[web]"     # adds plotly: charts as web pages (chart.save("marks.html")), no internet needed
```

With pip, the `[r]` extra also needs R (https://cran.r-project.org) and, in R,
`install.packages(...)` with the R packages listed in [What simplydata handles](docs/what_simplydata_handles.md#packages-underneath). On Windows with
Python 3.13, rpy2 has no ready-made wheel; set `RPY2_CFFI_MODE=ABI` first (in PowerShell:
`$env:RPY2_CFFI_MODE = "ABI"`, in cmd: `set RPY2_CFFI_MODE=ABI`), then run the pip line.

**conda, mamba or micromamba: coming soon**, once the conda-forge review is done (submitted 2026-11-20, still in
review). They will install Python, simplydata and, when you want them, R and its packages in one environment; all
three read the same conda-forge packages. Once the package is there:

```
conda create -n simplydata -c conda-forge simplydata        # a new environment called "simplydata"
conda activate simplydata

mamba create -n simplydata -c conda-forge simplydata        # the same with mamba (faster)
micromamba create -n simplydata -c conda-forge simplydata   # the same with micromamba (small, no base install)
```

Extras, in the same environment (replace `conda` with `mamba` or `micromamba` if you use those):

```
conda install -c conda-forge python-docx pyreadstat   # reading Word, SPSS and Stata files
conda install -c conda-forge control                  # rise time, settling time and margins of systems
conda install -c conda-forge python-duckdb            # SQL on a table or on files (run_sql)
conda install -c conda-forge rpy2 r-base              # R and the bridge to it, for the methods only R has
```

Until then, conda users can make the environment with conda and install simplydata into it with pip:
`conda create -n simplydata -c conda-forge python=3.12 rpy2 r-base`, then `conda activate simplydata` and
`pip install simplydata`. With conda the rpy2 step above is not needed: rpy2 and R come ready-built from
conda-forge, and the R packages too (for example `conda install -c conda-forge r-vegan r-metafor r-lme4`).

## Privacy: your data stays on your computer

simplydata is made for sensitive data too, such as patient records and surveillance data. "Safe for sensitive
data" at the top of this page means the promises below, and automatic tests check each of them on every change.

- **Nothing is sent anywhere.** simplydata has no telemetry, no analytics, no update checks and no crash reports.
  It never uploads, sends or logs your data.
- **The only network use is one you ask for:** `sdata.table("https://...")` downloads the table at a web address
  you give: one request for that file, with none of your data. It follows the address on only to another https
  address. Everything else, R included, runs fully offline.
- **Files are written only where you ask:** `table.save(...)`, `chart.save(...)`, `nums.save(...)` and
  `save_as=`. R draws into nothing, never into an `Rplots.pdf`. `sdata.start_30_days()` keeps the dates of your
  learning days in `.simplydata/progress.json` in your home folder (no data). Temporary files are deleted at once:
  an SPSS file read from a web address, and R's own session folder when Python ends.
- **What simplydata prints goes to your own screen.** The list of packages at the end of a script names packages
  and versions only, never a value or a column name.
- **Checked on every change.** [tests/test_privacy.py](https://github.com/bioforkgithub/simplydata/blob/main/tests/test_privacy.py)
  scans the source for network code and for R code that names a network, install or file-writing function
  (simplydata also refuses to run such R code), and the whole test suite runs with Python's network connections
  blocked.
- **The maintenance automation stays on GitHub.** Dependabot, the weekly version checks and their warning issues
  run only on GitHub's servers, on simplydata's own code and public test data; none of it is in the installed
  package. See [MAINTAINING.md](https://github.com/bioforkgithub/simplydata/blob/main/MAINTAINING.md).

The packages underneath keep their own caches, such as matplotlib's list of fonts; these hold no data. To report a
security or privacy problem, see [SECURITY.md](https://github.com/bioforkgithub/simplydata/blob/main/SECURITY.md).

## How simplydata works

simplydata does not implement statistical methods itself. Every calculation is done by
established, peer-reviewed packages: Python packages (SciPy, statsmodels, pandas, NumPy and
others), and R packages through rpy2 where Python has none. simplydata translates simple words
into those calls, with the right settings, and says in the result which method was used. What we
test is that translation: each answer is checked against the package underneath and against R.

### How we check simplydata

The [reliability report](https://github.com/bioforkgithub/simplydata/blob/main/validation/report.md) runs simplydata words on real, published data (NIST
certified values, Student's sleep data, Anscombe's quartet ...) and compares each answer with the
published one, with the package underneath called directly, and with R. It lists the tolerance of
every check, the package versions it ran with, and every setting where simplydata's default differs
from the package's own. A check passes when the word agrees with the reference to the stated, justified
tolerance: about 1e-9 for calculations without iteration, the certified digits or the same method run to
convergence for iterative fits, and the same seed or 4 Monte Carlo standard errors for simulations. The
report's total also counts the "same underneath" checks, which show that a word makes the call it says it
makes; most of those run on the made-up practice tables, while the study's cases use real or published data
(3 of them are made-up edge cases, and a few simulation checks need no data). Anyone can rerun it with one command: `python validation/make_report.py`
([how it works and the datasets](https://github.com/bioforkgithub/simplydata/blob/main/validation/README.md)). For the words that have it, the manual also
shows the same job written in the package underneath, in a grey box that a test runs and checks.

### How simplydata chooses methods

- Defaults follow published guidelines and method comparisons where they exist; the manual cites them for each
  word.
- Where methods disagree, simplydata prefers the one that is valid under fewer assumptions (Welch's t-test
  rather than Student's, for example).
- Where the evidence is balanced, simplydata matches the field's standard software, and says so; where studies
  prefer another method, the table names it.
- simplydata checks some things in the data and says so in a note; it never switches method by itself. Tests
  check whether each group looks bell-shaped (Shapiro-Wilk) and whether expected counts are below 5, and say how
  many rows with empty cells were left out; models check for residuals that are not bell-shaped, strongly linked
  columns (variance inflation factor above 5), too few rows per effect, complete separation, overdispersion, and an
  odds ratio when yes is common. It refuses what cannot be computed, such as a column with one value only or a
  group with too few rows.
- simplydata does not check whether the rows are independent. If the same person, plot or school appears in
  several rows, say so: `matched_by=`, `grouped_by=`, `compare_matched_columns`, or one row per person.
- Every printout names the method used, and every default can be changed with an option.
- The defaults of each batch were read by an automated review pass when they were designed, and in November 2026
  every entry of the table below, with its references, was read again by automated review passes told to act as
  hostile statistical referees (AI review, not named human reviewers). Their findings were applied.

[How simplydata chooses methods](docs/how_simplydata_chooses.md) gives all 565 defaults: for each, the default,
the alternatives, why it was chosen, what simplydata checks in the data, and its references (each DOI checked in
Crossref). The manual has the same table as its last part.

## Using the words that need R

The packages behind every word, and which need R, are in [What simplydata handles](docs/what_simplydata_handles.md#packages-underneath).
To use the words that need R, install R from https://cran.r-project.org, then
`pip install "simplydata[r]"`, then in R `install.packages(...)` with the R packages listed there.
Every other word works without R. A word that needs R and cannot find it, or a package, stops with
a friendly message that says what to install.

## Why simplydata exists: the learning philosophy

Learning to program is hard for many people, and data science adds a second hurdle: the names. In a study across
several countries, first-year students averaged 22.9 out of 110 on a programming task (McCracken et al. 2001), and
about one in three students still fails a first programming course (Watson & Li 2014). Even experienced data
scientists say they must "know all the function names and class names correctly and have another browser open to
search for help" (Chattopadhyay et al. 2020). For a researcher who wants to analyse data, much of the effort goes into
remembering how each library spells things, not into the science. simplydata was written to remove that effort.

The design follows what the research on learning and on programming languages says:

- **Everyday words are easier than invented ones.** Novices find common English words with a known meaning the most
  intuitive, and languages with English-like keywords are learned more accurately than ones with arbitrary keywords
  (Stefik & Siebert 2013). Full words are understood faster than abbreviations (Lawrie et al. 2007; Hofmeister et al.
  2017). So simplydata uses words such as `keep_rows_where`, `find_average_of` and `draw_bars`.
- **People describe tasks on whole sets of data, as queries** ("the rows where marks are above 50"), not as loops
  (Pane, Ratanamahatana & Myers 2001). simplydata's words follow that way of speaking.
- **No one guesses a name nobody told them.** Two people pick the same name for the same thing less than one time in
  five (Furnas et al. 1987). So every word is built from a short list of verbs and glue words that can be learned once,
  every name is scored for how familiar its words are, and typing a name from another tool (or a near miss) points
  to the right word.
- **Working memory is small** (Miller 1956; Cowan 2001), and effort spent searching for the means competes with
  learning (Sweller 1988). One small, consistent vocabulary with sensible defaults lowers that load; most people keep
  the default they are given (Johnson & Goldstein 2003), so the defaults are the recommended methods.
- **Worked examples teach better than problem solving alone** (Sweller & Cooper 1985). The lessons and the 30-day
  guide start from a worked example, then fade it, then ask for your own call.
- **Readable error messages shorten debugging** (Becker et al. 2019; Denny, Prather & Becker 2020). simplydata's
  messages say what went wrong, how to fix it, and give the corrected call.
- **English-like code can mislead**: AppleScript was easy to read but hard to write, because its English hid fixed
  rules (Cook 2007), and novices tend to believe the computer understands what they mean (Pea 1986). simplydata
  therefore stays plain Python (object, dot, word, options) with a closed set of words, and it is a bridge, not a
  wall: like Hedy, which leads learners step by step to real Python (Hermans 2020), every simplydata word shows the
  pandas, Polars, NumPy, SciPy, statsmodels or R code it runs underneath, so you can move on to those libraries
  whenever you want.
- **Trust comes from checking.** simplydata does not compute statistics itself: every number comes from the
  established package, and a public reliability study compares most words (431 of the 431 so far) with that
  package, with R and with published certified values.

### References

- Becker, B. A., et al. (2019). Compiler error messages considered unhelpful. *ITiCSE Working Group Reports*. https://doi.org/10.1145/3344429.3372508
- Chattopadhyay, S., Prasad, I., Henley, A. Z., Sarma, A., & Barik, T. (2020). What's wrong with computational notebooks? *CHI '20*. https://doi.org/10.1145/3313831.3376729
- Cook, W. R. (2007). AppleScript. *Proceedings of the third ACM SIGPLAN conference on History of Programming Languages (HOPL III)*. https://doi.org/10.1145/1238844.1238845
- Cowan, N. (2001). The magical number 4 in short-term memory. *Behavioral and Brain Sciences*, 24(1), 87-114. https://doi.org/10.1017/S0140525X01003922
- Denny, P., Prather, J., & Becker, B. A. (2020). Error message readability and novice debugging performance. *ITiCSE '20*. https://doi.org/10.1145/3341525.3387384
- Furnas, G. W., Landauer, T. K., Gomez, L. M., & Dumais, S. T. (1987). The vocabulary problem in human-system communication. *Communications of the ACM*, 30(11), 964-971. https://doi.org/10.1145/32206.32212
- Hermans, F. (2020). Hedy: a gradual language for programming education. *ICER '20*, 259-270. https://doi.org/10.1145/3372782.3406262
- Hofmeister, J., Siegmund, J., & Holt, D. V. (2017). Shorter identifier names take longer to comprehend. *SANER 2017*. https://doi.org/10.1109/SANER.2017.7884623
- Johnson, E. J., & Goldstein, D. (2003). Do defaults save lives? *Science*, 302, 1338-1339. https://doi.org/10.1126/science.1091721
- Lawrie, D., Morrell, C., Feild, H., & Binkley, D. (2007). Effective identifier names for comprehension and memory. *Innovations in Systems and Software Engineering*, 3(4), 303-318. https://doi.org/10.1007/s11334-007-0031-2
- McCracken, M., et al. (2001). A multi-national, multi-institutional study of assessment of programming skills of first-year CS students. *ACM SIGCSE Bulletin*, 33(4), 125-180. https://doi.org/10.1145/572139.572181
- Miller, G. A. (1956). The magical number seven, plus or minus two. *Psychological Review*, 63(2), 81-97. https://doi.org/10.1037/h0043158
- Pane, J. F., Ratanamahatana, C. A., & Myers, B. A. (2001). Studying the language and structure in non-programmers' solutions to programming problems. *International Journal of Human-Computer Studies*, 54(2), 237-264. https://doi.org/10.1006/ijhc.2000.0410
- Pea, R. D. (1986). Language-independent conceptual "bugs" in novice programming. *Journal of Educational Computing Research*, 2(1), 25-36. https://doi.org/10.2190/689T-1R2A-X4W4-29J2
- Stefik, A., & Siebert, S. (2013). An empirical investigation into programming language syntax. *ACM Transactions on Computing Education*, 13(4), 19. https://doi.org/10.1145/2534973
- Sweller, J. (1988). Cognitive load during problem solving: effects on learning. *Cognitive Science*, 12(2), 257-285. https://doi.org/10.1207/s15516709cog1202_4
- Sweller, J., & Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving in learning algebra. *Cognition and Instruction*, 2(1), 59-89. https://doi.org/10.1207/s1532690xci0201_3
- Watson, C., & Li, F. W. B. (2014). Failure rates in introductory programming revisited. *ITiCSE '14*, 39-44. https://doi.org/10.1145/2591708.2591749

## Ideas behind it

- **Talk to the program.** Each line reads like an instruction you say to the program: the thing,
  what it should do, then the details: `table.keep_rows_where("marks", is_above=50)`,
  `chart.write_title_on_top(...)`, `chart.draw_line_at_y(50)`.
- **What + where.** A few place words repeat everywhere: `top`, `bottom`, `x`, `y`, `at`, `between`.
- **Old names keep working for one release.** A renamed word still runs and says, once, what it is
  called now.
- **Guess a word from its sibling.** `keep_rows_where` and `keep_first_rows`, `show_first_rows`;
  `find_average_of` and `show="average"`; `label_x` and `label_colour_bar`.
- **The word names the idea.** `error="standard error"`, `fit_line(with_confidence_band=True)`,
  `compare_averages_of` (and the result says "Welch's t-test" for when you write it up).
- **Order doesn't matter.** Write the steps in any order; simplydata draws them correctly.
- **Friendly errors.** Misspell a column and simplydata tells you what you probably meant.
- **Your old words still help.** Names from pandas, NumPy, SciPy, R and matplotlib (`groupby`,
  `curve_fit`, `pnorm`, `hist`) point to the simplydata word, so the first guess is never a dead end.

The full design is in [PLAN.md](https://github.com/bioforkgithub/simplydata/blob/main/PLAN.md).

## Changes and contributing

What changed in each release is in [CHANGELOG.md](https://github.com/bioforkgithub/simplydata/blob/main/CHANGELOG.md). Contributions are welcome:
[CONTRIBUTING.md](https://github.com/bioforkgithub/simplydata/blob/main/CONTRIBUTING.md) explains how to suggest a word, report a problem or add code.

## How to cite

If simplydata helps your work, please cite the archived software:

> bioforkgithub. simplydata: simple words for data science in Python. Zenodo. https://doi.org/10.5281/zenodo.24210045

This DOI always points to the latest version; each release also has its own DOI on Zenodo. GitHub's "Cite this repository" button gives the same citation in other formats.

## Licence

MIT, for the code and the practice tables, which are all made up. The reliability study's NIST files are public
domain and its few stored tables are published facts; every real dataset simplydata was tested on, with its source,
citation and licence, is listed in [DATA_LICENSES.md](DATA_LICENSES.md).
