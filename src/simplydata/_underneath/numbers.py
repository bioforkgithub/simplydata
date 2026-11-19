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
]
