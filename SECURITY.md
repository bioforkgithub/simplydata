# Security and privacy

simplydata is used on sensitive data, such as patient records and surveillance data. It is built so that this
data never leaves your computer.

## What simplydata promises

- **No data is sent anywhere.** simplydata has no telemetry, no analytics, no update checks and no crash reports.
  It never uploads, sends or logs your data.
- **The only network use is one you ask for.** `sdata.table("https://...")` downloads the table at a web address
  you give. The request carries the address and the program name "simplydata", nothing else. Every other word,
  including the ones that run R, works fully offline.
- **R stays offline too.** The R code simplydata runs never downloads, installs a package or writes a file, and
  `simplydata._r.r_call()` refuses R code that could.
- **Files are written only where you ask:** `table.save(...)`, `chart.save(...)`, `nums.save(...)` and `save_as=`.
  The one exception holds no data: `sdata.start_30_days()` keeps the dates of your learning days in
  `.simplydata/progress.json` in your home folder (the environment variable `SIMPLYDATA_PROGRESS_FILE` chooses
  another file). An SPSS file read from a web address is put in a temporary folder for the moment pyreadstat
  reads it, then deleted.
- **What simplydata prints goes to your own screen.** The list of packages printed at the end of a script, and
  `sdata.show_packages_used()`, name packages, versions and references only, never a value, a column name or a
  group from your tables.

These promises are checked by automatic tests on every change:
[tests/test_privacy.py](tests/test_privacy.py) scans the source for network code and for R code that could reach
the internet or write files, and [tests/conftest.py](tests/conftest.py) runs the whole test suite with outgoing
network connections blocked.

The packages simplydata uses (pandas, Polars, NumPy, SciPy, statsmodels, matplotlib, seaborn, R and its packages)
keep their own caches, such as matplotlib's list of fonts. None of them sends your data anywhere when used through
simplydata.

## Supported versions

Security and privacy fixes go into the latest release. Please update to it:
`pip install --upgrade simplydata` or `conda update -c conda-forge simplydata`.

## Reporting a problem

If you find a way in which simplydata could leak data, or any other security problem, please report it privately:
use the **"Report a vulnerability"** button on the
[Security tab](https://github.com/bioforkgithub/simplydata/security) of the GitHub repository. Please do not open a
public issue for it.

Never include real patient or other sensitive data in a report or an issue: a few made-up rows that show the
problem are enough. You will get an answer as soon as possible, and the fix will be released with a note in
[CHANGELOG.md](CHANGELOG.md).
