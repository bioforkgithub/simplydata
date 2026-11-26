# Maintaining simplydata

This note is for the people who keep simplydata working as pandas, NumPy, SciPy, statsmodels,
matplotlib, seaborn and Polars change. [GOVERNANCE.md](GOVERNANCE.md) says who decides what.

## What the maintenance automation does and does not do

Dependabot, the weekly checks (oldest and upcoming versions, the weekly notebook run) and the
warning issues run only on GitHub's servers, against simplydata's own code and its public test
data. They are not part of the installed package: nothing of them is on a user's computer. The
warning issues contain only package versions and test names. The workflows upload nothing but
their own build artifacts (the package, the rebuilt documents, test reports). The package
itself never contacts any server, sends no telemetry and has no update check, and the tests
block the network on every run.

## How a release works

1. All work reaches `main` through a pull request. `main` is protected: the 10 checks of
   `.github/workflows/tests.yml` (Windows, macOS and Linux on Python 3.11 to 3.13 with R, and
   Linux without R) must pass, and the branch must be up to date.
2. Raise the version in `src/simplydata/__init__.py` and add the changes to `CHANGELOG.md` in
   the same pull request. Rebuild the manual, the dictionary and the 30-day guide
   (`python docs/make_manual.py`) so the PDFs match the release.
3. After the merge, publish a release on GitHub with the tag `vX.Y.Z`.
   `.github/workflows/publish.yml` then builds the package and uploads it to PyPI.
4. Release on conda-forge at the same time, with the same version. There is no conda-forge
   feedstock yet: the recipe is still in review (conda-forge/staged-recipes pull request
   #35769). Once the feedstock exists, the conda-forge bot will follow PyPI by itself: after
   each PyPI upload it opens a pull request on the feedstock; check that its requirements match
   the ranges in `pyproject.toml`, then merge it.

## The supported version ranges

Every dependency in `pyproject.toml` has a range such as `pandas>=2.2,<4`.

- The **lower bound** is the oldest release that is tested.
  `.github/workflows/oldest-versions.yml` installs the oldest release each range allows (uv's
  `--resolution lowest-direct`) and runs the tests without R on Python 3.11, for every pull
  request.
- The **upper bound** is the next major release, which nobody has tested yet. It keeps an
  untested release from reaching users by itself.
- `tests/test_dependency_ranges.py` fails if a dependency has no lower or no upper bound.
- Polars and pyarrow are required (since the tables phase, 2026-11-25), because several table
  words run on Polars for every table so that pandas and Polars tables give one answer. The
  `[fast]` extra is kept empty, like `[stats]`, so old install lines still work. A conda-forge
  recipe must list `polars` and `pyarrow` under `run` with the same ranges.
- narwhals: `src/simplydata/_narwhals_mend.py` widens narwhals' pandas datetime pattern
  (`narwhals._pandas_like.utils.PATTERN_PD_DATETIME`) when simplydata is imported, so pandas zone names
  with `_`, `-`, `+` or digits (`America/New_York`) are read as dates; it switches itself off when narwhals
  reads those names itself. `tests/test_time_zone_names.py` fails if narwhals moves that pattern. When a
  fixed narwhals is the lowest supported release, delete the module and its import.

## The warning issues

`.github/workflows/upcoming-versions.yml` runs every Monday (and by hand from the Actions tab).
It installs the newest releases **and pre-releases** of pandas, NumPy, SciPy, statsmodels,
matplotlib, seaborn and Polars, ignoring the upper bounds on purpose, and runs the tests
without R.

- If tests fail, it opens one issue, **"Upcoming package versions break simplydata"**, or
  updates it if it is open already. The issue lists the versions tried and the failing tests,
  with a link to the run.
- When a later run passes, it comments on the issue and closes it.

How to read it: a failure on a **pre-release** (`3.0.0rc1`, `2.0.0b2`) is an early warning;
there is time, and the package may still change its mind. A failure on a **final release**
inside the current ranges reaches users now and comes first. Read the release notes of the
package for the change that broke the test.

The weekly notebook run in [simplydata_tests](https://github.com/bioforkgithub/simplydata_tests)
works the same way: on a failure it opens or updates the issue **"Weekly notebook run found new
differences"** there, with the new FAILs.

## The Dependabot pull requests

`.github/dependabot.yml` opens update pull requests every week, at most 5 open at a time:

- **Grouped minor and patch updates** (Python packages, GitHub Actions): if all checks pass,
  merge.
- **A new major release** comes alone and widens a range (for example `pandas>=2.2,<4` to
  `pandas>=2.2,<5`). Merge it only when all checks pass; if they fail, fix the words first (see
  below), in the same pull request or a new one.

## How to fix a broken word

1. **Find the failing test** in the warning issue or the check log, and run only that test on
   your machine: `python -m pytest -q tests/test_x.py::test_name`.
2. **Find the pass-through call** in `src/simplydata` that the word makes to pandas, SciPy,
   statsmodels or the other package, and read the package's release notes for what changed
   (a renamed argument, a new default, a removed function).
3. **Adjust the call** so the word asks the package for the same thing as before, for example
   with the new argument name, or with a small branch on the package version when both the old
   and the new release are in the range.
4. **Add a test** that would have caught the change, with the reference value from the parent
   package or R written in the test.
5. **Never add simplydata's own computation** to work around the change. simplydata passes the
   work to the parent package; if the package no longer gives the answer, say so to the user in
   plain words and open an issue, and do not compute it ourselves.

## How to widen a version range

1. Change the upper bound in `pyproject.toml` (for example `numpy>=2.1,<3` to
   `numpy>=2.1,<4`), usually in a Dependabot pull request.
2. Let the 10 checks run: they install the newest release. Fix any broken word as above.
3. If a word needs a newer release than the lower bound, raise the lower bound, and check that
   the oldest-versions check passes.
4. Mention the new range in `CHANGELOG.md`, and match it in the conda-forge recipe (the
   feedstock, once it exists) at the next release.
