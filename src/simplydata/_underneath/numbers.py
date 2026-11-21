"""Number words: the same job in NumPy (SciPy where it is used)."""

from . import Entry

ENTRIES = [
    Entry(
        word="nums.find_median",
        ours="""
            nums = sdata.numbers([12, 15, 9, 20, 14])
            nums.find_median()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, 9, 20, 14])
            # find_median()
            np.nanmedian(values)                 # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("empty values are skipped (np.nanmedian); NumPy's np.median would give nan.",),
        also="simplydata also says the median in a sentence, with how many numbers it used.",
    ),
    Entry(
        word="nums.find_average",
        ours="""
            nums = sdata.numbers([12, None, 9, 20, 14])
            nums.find_average()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # find_average()
            np.nanmean(values)                   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("empty values are skipped (np.nanmean); NumPy's np.mean would give nan.",),
        also="simplydata also says the average in a sentence, with how many numbers it used.",
    ),
    Entry(
        word="nums.find_percentile",
        ours="""
            nums = sdata.numbers([12, 15, 9, 20, 14])
            nums.find_percentile(90)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, 9, 20, 14])
            # find_percentile(percent=90)
            np.nanpercentile(values, 90)         # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("NumPy's usual \"linear\" method, the same as pandas' quantile and R's quantile(type = 7); "
                 "empty values are skipped (nanpercentile).",),
        also="simplydata also says the percentile in a sentence. find_percentile(50) is the median.",
    ),
    Entry(
        word="nums.keep_each_number_that",
        ours="""
            nums = sdata.numbers([12, 15, None, 9, 20, 14])
            nums.keep_each_number_that(is_above=12).as_numpy()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, np.nan, 9, 20, 14])
            # keep_each_number_that(is_above=12)
            values[values > 12]                  # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("is_above= means strictly above (>); is_at_least= is >=. An empty value is never above a "
                 "number, so it goes too (only is_empty=True keeps empty values).",),
        also="simplydata also says how many numbers it kept, and keeps the numbers before the step (undo).",
    ),
]
