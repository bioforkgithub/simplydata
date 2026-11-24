"""Learn basic Python, and simplydata takes you from your first table to sound statistics, in plain words, with its results checked against the field's standard tools.

    import simplydata as sdata

    table = sdata.table(sdata.get_example("marks"))   # or sdata.table("results.xlsx")
    table.keep_rows_where("marks", is_above=50)
    chart = table.start_chart()                     # or sdata.chart(table)
    chart.draw_bars(x="class", y="marks")
    chart.write_title_on_top("Good marks")
    chart.save("marks.png")

Numbers too: nums = sdata.numbers([3, 5, 2, 8]), then nums.find_average().

New here? Type sdata.show_lesson(1), or sdata.start_30_days() for an hour a day over 30 days.
Every word: sdata.show_all_words(). One word: sdata.help("draw_bars").
The packages that did the work, and how to cite them: sdata.show_packages_used().
"""

import sys as _sys

# The packages loaded before simplydata (for sdata.show_packages_used(): "You also loaded these yourself")
_BEFORE = {_name.split(".")[0] for _name in list(_sys.modules)}

from ._errors import SimplydataError
from .chart import Chart, chart
from .data import get_example
from .table import Table, table
from .numbers import NumberGrid, Numbers, make_random_numbers, number_grid, numbers
from .words.layout import put_in_rows_and_columns, put_one_above_other, put_side_by_side
from .words.stats import draw_all_pairs
from .power import find_chance_of_finding, find_how_many_needed
from .designs import make_design_table, make_random_assignments
from .finding import find_where_biggest, find_where_smallest, solve
from .distributions import distribution
from ._sdata_tests import compare_averages, compare_counts
from .risks import compare_rates, compare_risks, compare_to_truth
from ._dates import make_run_of_dates
from ._waves import find_inverse_fourier_transform, make_wave, make_window_shape
from .systems import System, frequency_filter, system

# Last, on purpose: the old name sdata.words (defined below) must win over the subpackage simplydata.words
# (sdata.table and sdata.numbers win over their subpackages the same way, by being imported after them).
from .learn import help, show_all_words, show_lesson  # noqa: E402
from .learn_days import go_to_next_day, show_answers, show_day, show_today, start_30_days  # noqa: E402
from ._cite import show_packages_used  # noqa: E402

__version__ = "0.2.0"

# Old names that still work for one release (with a note the first time): old -> new.
# They are never listed in __all__, sdata.show_all_words() or the lessons.
_OLD_WORDS = {
    "example": "get_example", "pairs": "draw_all_pairs", "side_by_side": "put_side_by_side",
    "one_above_other": "put_one_above_other", "grid": "put_in_rows_and_columns",
    "random_numbers": "make_random_numbers", "how_many_needed": "find_how_many_needed",
    "chance_to_find": "find_chance_of_finding", "dates": "make_run_of_dates",
    "inverse_fourier_transform": "find_inverse_fourier_transform", "wave": "make_wave",
    "window_shape": "make_window_shape", "find_smallest": "find_where_smallest", "find_biggest": "find_where_biggest",
    "words": "show_all_words", "lesson": "show_lesson", "today": "show_today", "day": "show_day",
    "answers": "show_answers", "next_day": "go_to_next_day",
}


def words(*args, **kwargs):
    """Old name of sdata.show_all_words() (kept for one release)."""
    from ._errors import renamed_note

    renamed_note("words", "show_all_words")
    return show_all_words(*args, **kwargs)


def __getattr__(name):
    """sdata.<name> that does not exist: an old name works (with a note once); names from other tools
    (sdata.minimize, sdata.curve_fit ...) point to the simplydata word and never run; other names get a
    did-you-mean."""
    if name.startswith("_"):
        raise AttributeError(f"module 'simplydata' has no attribute {name!r}")
    from ._errors import missing_sdata_word, renamed_note

    new = _OLD_WORDS.get(name)
    if new is not None:
        renamed_note(name, new)
        return globals()[new]
    raise missing_sdata_word(name, __all__)


__all__ = [
    "Chart", "NumberGrid", "Numbers", "SimplydataError", "System", "Table", "chart", "compare_averages",
    "compare_counts", "compare_rates", "compare_risks", "compare_to_truth", "distribution", "draw_all_pairs",
    "find_chance_of_finding", "find_how_many_needed", "find_inverse_fourier_transform", "find_where_biggest",
    "find_where_smallest", "frequency_filter", "get_example", "go_to_next_day", "help", "make_design_table",
    "make_random_assignments", "make_random_numbers",
    "make_run_of_dates", "make_wave", "make_window_shape", "number_grid", "numbers", "put_in_rows_and_columns",
    "put_one_above_other", "put_side_by_side", "show_all_words", "show_answers", "show_day", "show_lesson",
    "show_packages_used", "show_today", "solve", "start_30_days", "system", "table", "__version__",
]

# Remember the packages that do the work behind each word (sdata.show_packages_used()), and print the short list
# at the end of a script
from . import _cite  # noqa: E402

_cite.BEFORE_SIMPLYDATA.update(_BEFORE)
_cite.install(globals())
_cite.register_at_exit()
del _BEFORE
