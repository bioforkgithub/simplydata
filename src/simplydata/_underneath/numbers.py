"""Number words: the same job in NumPy (SciPy where it is used)."""

from . import Entry

ENTRIES = [
    Entry(
        word="nums.find_median",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.find_median()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
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
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.find_average()
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
            numbers = sdata.number_list([12, 15, 9, 20, 14])
            numbers.find_percentile(90)
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
            numbers = sdata.number_list([12, 15, None, 9, 20, 14])
            numbers.keep_each_number_that(is_above=12)
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
    # ---------------------------------------------------------------- U3: number and grid words (batch 4)
    # ---- looking
    Entry(
        word="nums.show",
        ours="""
            numbers = sdata.number_list(1, to=1200)
            numbers.show()
        """,
        code={"NumPy": """
            import sys
            import numpy as np
            values = np.arange(1, 1201)
            # show()
            print(np.array2string(values, threshold=sys.maxsize,     # (1)
                                  separator=", "))                   # (2)
        """},
        compare="printed",
        choices=("every number is shown, however many there are (threshold=sys.maxsize); NumPy's own print "
                 "shortens a list of more than 1000 numbers to its ends with \"...\" in the middle.",
                 "the numbers are written with commas between them, like a Python list; NumPy's print leaves out "
                 "the commas.",),
        also="An empty value is shown as nan. Typing numbers on its own line shows how many numbers there are and "
             "every number up to 60; above that only the first 3 and the last 3 (a grid: above 200 numbers).",
    ),
    Entry(
        word="nums.show_first_numbers",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.show_first_numbers(3)
        """,
        code={"NumPy": """
            import sys
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # show_first_numbers(how_many=3)
            print(np.array2string(values[:3], threshold=sys.maxsize, separator=", "))   # (1)
        """},
        compare="printed",
        choices=("the numbers are written with commas between them, like a Python list; NumPy's print leaves out "
                 "the commas. threshold=sys.maxsize keeps a long list whole, as in show().",),
        also="Without a number it shows the first 5. Asking for more than there are shows them all.",
    ),
    Entry(
        word="nums.show_last_numbers",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.show_last_numbers(2)
        """,
        code={"NumPy": """
            import sys
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # show_last_numbers(how_many=2)
            print(np.array2string(values[-2:], threshold=sys.maxsize, separator=", "))   # (1)
        """},
        compare="printed",
        choices=("the numbers are written with commas between them, like a Python list; NumPy's print leaves out "
                 "the commas. threshold=sys.maxsize keeps a long list whole, as in show().",),
        also="Without a number it shows the last 5. show_last_numbers(0) shows none, where NumPy's values[-0:] "
             "would give them all.",
    ),
    Entry(
        word="nums.get_number_at",
        ours="""
            numbers = sdata.number_list([12, 15, 9, 20, 14])
            numbers.get_number_at(2)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, 9, 20, 14])
            # get_number_at(position=2)
            values[2 - 1]                        # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("positions count from 1, the way people count and the way charts number the x axis: 2 is the "
                 "second number. NumPy's [ ] counts from 0, so the same number is values[1].",),
        also="get_number_at(\"last\") is the last number (NumPy values[-1]). A position that is not there stops "
             "with a message that says how many numbers there are. The number comes back as a plain Python number.",
    ),
    Entry(
        word="nums.count",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.count()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # count()
            values.size                          # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("empty values are counted too: count() is how many places there are. The filled ones alone are "
                 "count() minus count_empty_numbers(), as np.count_nonzero(~np.isnan(values)).",),
    ),
    Entry(
        word="nums.count_empty_numbers",
        ours="""
            numbers = sdata.number_list([12, None, 9, None, 14])
            numbers.count_empty_numbers()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, np.nan, 14])
            # count_empty_numbers()
            int(np.isnan(values).sum())
        """},
        compare="value",
        tolerance=0.0,
        also="None in the list you give becomes an empty value (nan). Whole numbers can hold no empty value, so "
             "their count is 0.",
    ),
    # ---- maths that changes the numbers
    Entry(
        word="nums.add",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.add(5)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # add(number=5)
            values + 5
        """},
        compare="value",
        tolerance=0.0,
        also="An empty value stays empty. add() changes these numbers and can be undone; numbers + 5 makes new "
             "numbers instead, with the same sum. A list of the same length adds one number to each.",
    ),
    Entry(
        word="nums.subtract",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.subtract(2)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # subtract(number=2)
            values - 2
        """},
        compare="value",
        tolerance=0.0,
        also="An empty value stays empty. numbers - 2 makes new numbers instead, with the same sum.",
    ),
    Entry(
        word="nums.times",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.times(2)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # times(number=2)
            values * 2
        """},
        compare="value",
        tolerance=0.0,
        also="An empty value stays empty. numbers * 2 makes new numbers instead, with the same sum.",
    ),
    Entry(
        word="nums.divide_by",
        ours="""
            numbers = sdata.number_list([8, None, 6, 4])
            numbers.divide_by([2, 1, 0, 4])
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([8, np.nan, 6, 4])
            divisors = np.array([2, 1, 0, 4])
            # divide_by([2, 1, 0, 4])
            with np.errstate(divide="ignore"):
                result = values / divisors
            np.where(divisors == 0, np.nan, result)    # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("dividing by 0 has no answer, so the number becomes empty (nan) and a note says how many; NumPy "
                 "gives inf (or nan for 0 / 0) with a warning.",),
        also="divide_by(4) divides every number by 4. numbers / 4 makes new numbers instead, with the same rule.",
    ),
    Entry(
        word="nums.raise_to_power",
        ours="""
            numbers = sdata.number_list([2, 0, 4])
            numbers.raise_to_power(-1)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([2, 0, 4])
            # raise_to_power(-1)
            with np.errstate(divide="ignore"):
                result = np.power(values.astype(float), -1)   # (1)
            np.where(values == 0, np.nan, result)             # (2)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("whole numbers to a minus power are worked out as decimals; NumPy's np.power on whole numbers "
                 "stops with an error instead.",
                 "0 to a minus power means dividing by 0, so it becomes empty (nan) with a note; NumPy gives inf. A "
                 "negative number to a power with decimals, such as 0.5, becomes empty too.",),
        also="Whole numbers to a whole power that is not negative stay whole numbers while the answer fits. "
             "numbers ** 2 makes new numbers instead, with the same rules.",
    ),
    Entry(
        word="nums.take_square_root",
        ours="""
            numbers = sdata.number_list([9, 16, None, 2])
            numbers.take_square_root()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([9, 16, np.nan, 2])
            # take_square_root()
            np.sqrt(values)
        """},
        compare="value",
        tolerance=1e-12,
        also="A negative number has no square root among ordinary numbers, so it becomes empty with a note saying "
             "how many; NumPy gives nan too, but with a RuntimeWarning.",
    ),
    Entry(
        word="nums.take_absolute_value",
        ours="""
            numbers = sdata.number_list([-3, 5, None, -2.5])
            numbers.take_absolute_value()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([-3, 5, np.nan, -2.5])
            # take_absolute_value()
            np.abs(values)
        """},
        compare="value",
        tolerance=0.0,
        also="An empty value stays empty.",
    ),
    Entry(
        word="nums.round_to",
        ours="""
            numbers = sdata.number_list([0.5, 1.5, 2.5, -2.5, 2.346])
            numbers.round_to(0)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([0.5, 1.5, 2.5, -2.5, 2.346])
            # round_to(with_decimals=0)
            np.round(values, 0)                  # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("a number exactly halfway goes to the even neighbour (0.5 to 0, 1.5 and 2.5 to 2), as NumPy, "
                 "pandas and R's round() do, so a run of halves does not push a total up. Excel and the way taught "
                 "at school round halves away from 0.",),
        also="round_to(2) keeps 2 decimals; round_to(-1) rounds to tens. A decimal such as 2.675 is stored a "
             "little below its written value, so it can round down.",
    ),
    Entry(
        word="nums.take_log",
        ours="""
            numbers = sdata.number_list([1, 1000, 0, None, 0.01])
            numbers.take_log(base=10)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([1, 1000, 0, np.nan, 0.01])
            # take_log(base=10)
            with np.errstate(divide="ignore", invalid="ignore"):
                result = np.log10(values)
            np.where(values <= 0, np.nan, result)    # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the log only exists for numbers above 0, so 0 and negative numbers become empty (nan) with a "
                 "note; NumPy gives -inf for 0 and nan for a negative number, with a warning.",),
        also="Without base= it is the natural log (np.log); base=2 is np.log2, and any other base is "
             "np.log(values) / np.log(base). take_exp() undoes the natural log.",
    ),
    Entry(
        word="nums.take_exp",
        ours="""
            numbers = sdata.number_list([0, 1, None, -2])
            numbers.take_exp()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([0, 1, np.nan, -2])
            # take_exp()
            np.exp(values)
        """},
        compare="value",
        tolerance=1e-12,
        also="An empty value stays empty. An answer too big to hold (above about 1.8e308) is shown as inf, with a "
             "note saying how many.",
    ),
    Entry(
        word="nums.turn_into_running_total",
        ours="""
            numbers = sdata.number_list([1, None, 2, 3])
            numbers.turn_into_running_total()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([1, np.nan, 2, 3])
            # turn_into_running_total()
            totals = np.nancumsum(values)
            np.where(np.isnan(values), np.nan, totals)    # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("an empty value stays empty and is skipped in the total (1, empty, 3, 6), as pandas cumsum() "
                 "does. NumPy's cumsum would make every total after it empty, and nancumsum would fill the empty "
                 "place with the total so far.",),
    ),
    # ---- keeping and removing
    Entry(
        word="nums.remove_each_number_that",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.remove_each_number_that(is_below=10)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # remove_each_number_that(is_below=10)
            values[~(values < 10)]               # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("is_below= means strictly below (<). An empty value is never below a number, so it stays; only "
                 "is_empty=True removes empty values. values[values >= 10] would drop it.",),
        also="simplydata also says how many numbers it removed and how many are left, and keeps the numbers before "
             "the step (undo).",
    ),
    Entry(
        word="nums.keep_first_numbers",
        ours="""
            numbers = sdata.number_list([12, 15, 9, 20, 14])
            numbers.keep_first_numbers(3)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, 9, 20, 14])
            # keep_first_numbers(how_many=3)
            values[:3]
        """},
        compare="value",
        tolerance=0.0,
        also="Without a number it keeps the first 5. simplydata also says how many it kept.",
    ),
    Entry(
        word="nums.keep_last_numbers",
        ours="""
            numbers = sdata.number_list([12, 15, 9, 20, 14])
            numbers.keep_last_numbers(3)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, 9, 20, 14])
            # keep_last_numbers(how_many=3)
            values[len(values) - 3:]
        """},
        compare="value",
        tolerance=0.0,
        also="Without a number it keeps the last 5. keep_last_numbers(0) keeps none (NumPy's values[-0:] would "
             "keep them all).",
    ),
    Entry(
        word="nums.keep_random_numbers",
        ours="""
            numbers = sdata.number_list([10, 20, 30, 40, 50, 60])
            numbers.keep_random_numbers(3, with_seed=2)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([10, 20, 30, 40, 50, 60])
            # keep_random_numbers(3, with_seed=2)
            rng = np.random.default_rng(2)                           # (1)
            picked = rng.choice(len(values), size=3, replace=False)
            values[np.sort(picked)]                                  # (2)
        """},
        compare="value",
        tolerance=0.0,
        choices=("NumPy's random generator (default_rng) with the seed you give, picking without repeats; the old "
                 "np.random.seed() gives another pick.",
                 "the numbers kept stay in their order in the list; rng.choice alone gives them in the order they "
                 "were drawn.",),
        also="Without with_seed= the pick changes every time. Asking for more numbers than there are keeps them "
             "all, with a note.",
    ),
    Entry(
        word="nums.remove_duplicate_numbers",
        ours="""
            numbers = sdata.number_list([3, None, 5, 3, 8, None, 5])
            numbers.remove_duplicate_numbers()
        """,
        code={"pandas": """
            import numpy as np
            import pandas as pd
            values = np.array([3, np.nan, 5, 3, 8, np.nan, 5])
            # remove_duplicate_numbers()
            repeats = pd.Series(values).duplicated(keep="first")   # (1)
            values[~repeats.to_numpy()]
        """},
        compare="value",
        tolerance=0.0,
        choices=("each number is kept once, in its first place, and the order stays as it was; empty values count "
                 "as one value, so the first empty one stays. NumPy's np.unique would sort the numbers instead.",),
    ),
    Entry(
        word="nums.remove_empty_numbers",
        ours="""
            numbers = sdata.number_list([12, None, 9, None, 14])
            numbers.remove_empty_numbers()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, np.nan, 14])
            # remove_empty_numbers()
            values[~np.isnan(values)]
        """},
        compare="value",
        tolerance=0.0,
        also="simplydata also says how many it removed. The summary words skip empty values without this step.",
    ),
    Entry(
        word="nums.keep_numbers_by_position",
        ours="""
            numbers = sdata.number_list([12, 15, 9, 20, 14])
            numbers.keep_numbers_by_position(2, to=4)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, 9, 20, 14])
            # keep_numbers_by_position(2, to=4)
            values[2 - 1:4]                      # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("positions count from 1 and both ends are kept: positions 2 to 4 are three numbers. NumPy counts "
                 "from 0 and leaves out the end, so the same numbers are values[1:4].",),
        also="to=\"last\" goes to the end, step=2 keeps every 2nd number (values[1::2]) and a list such as [4, 1] "
             "keeps those numbers in that order (values[[3, 0]]).",
    ),
    Entry(
        word="nums.remove_numbers_by_position",
        ours="""
            numbers = sdata.number_list([12, 15, 9, 20, 14])
            numbers.remove_numbers_by_position(2, to=3)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 15, 9, 20, 14])
            # remove_numbers_by_position(2, to=3)
            np.delete(values, np.arange(2 - 1, 3))    # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("positions count from 1 and both ends go: positions 2 and 3 are removed. NumPy counts from 0, so "
                 "they are places 1 and 2.",),
        also="remove_numbers_by_position(\"last\") removes the last number (np.delete(values, -1)). Removing every "
             "number stops with a message.",
    ),
    Entry(
        word="nums.replace_each_number_that",
        ours="""
            numbers = sdata.number_list([120, None, 80, 101])
            numbers.replace_each_number_that(is_above=100, with_value=100)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([120, np.nan, 80, 101])
            # replace_each_number_that(is_above=100, with_value=100)
            np.where(values > 100, 100, values)      # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("is_above= means strictly above (>). An empty value matches no condition, so it stays empty; "
                 "only is_empty=True picks the empty values.",),
        also="replace_each_number_that(-999, with_value=None) turns a code for \"missing\" into empty values "
             "(np.where(values == -999, np.nan, values)). simplydata also says how many it replaced.",
    ),
    Entry(
        word="nums.fill_empty_numbers",
        ours="""
            numbers = sdata.number_list([None, 12, None, 9, None, None, 18, None])
            numbers.fill_empty_numbers(with_the="line between neighbours")
        """,
        code={
            "NumPy": """
                import numpy as np
                values = np.array([np.nan, 12, np.nan, 9, np.nan, np.nan, 18, np.nan])
                # fill_empty_numbers(with_the="line between neighbours")
                places = np.arange(len(values))
                known = ~np.isnan(values)
                line = np.interp(places, places[known], values[known])       # (1)
                inside = (places > places[known][0]) & (places < places[known][-1])
                np.where(inside, line, values)                               # (2)
            """,
            "pandas": """
                import numpy as np
                import pandas as pd
                values = np.array([np.nan, 12, np.nan, 9, np.nan, np.nan, 18, np.nan])
                # fill_empty_numbers(with_the="line between neighbours")
                filled = pd.Series(values).interpolate(limit_area="inside")  # (1) (2)
                filled.to_numpy()
            """,
        },
        compare="value",
        tolerance=1e-12,
        choices=("each gap is filled on the straight line between the values just before and just after it, "
                 "spaced by position (linear interpolation).",
                 "empty values at the start or the end have a neighbour on one side only, so they stay empty, with "
                 "a note; np.interp alone would copy the first and last values outward.",),
        also="with_value=0 fills with a number; with_the=\"average\", \"median\", \"value above\" or \"value "
             "below\" fill with np.nanmean, np.nanmedian, pandas ffill() or bfill().",
    ),
    # ---- order
    Entry(
        word="nums.sort",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.sort(biggest_first=True)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            empty = np.isnan(values)
            # sort(biggest_first=True)
            ordered = np.sort(values[~empty])[::-1]
            np.concatenate([ordered, values[empty]])    # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("empty values go last, smallest first or biggest first; np.sort(values)[::-1] would put them "
                 "first.",),
        also="Without biggest_first=True the smallest comes first (np.sort, which already puts empty values last).",
    ),
    Entry(
        word="nums.reverse",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.reverse()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # reverse()
            values[::-1]
        """},
        compare="value",
        tolerance=0.0,
        also="It turns the order round as it is; for biggest first use sort(biggest_first=True).",
    ),
    # ---- summaries
    Entry(
        word="nums.find_total",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.find_total()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # find_total()
            np.nansum(values)                    # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("empty values are skipped (np.nansum), with a note saying how many; NumPy's np.sum would give "
                 "nan.",),
        also="simplydata also says the total in a sentence, with how many numbers it used. With no numbers at all "
             "the total is 0.",
    ),
    Entry(
        word="nums.find_smallest",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.find_smallest()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # find_smallest()
            np.nanmin(values)                    # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("empty values are skipped (np.nanmin), with a note saying how many; NumPy's np.min would give "
                 "nan.",),
        also="simplydata also says the smallest number in a sentence, with how many numbers it used.",
    ),
    Entry(
        word="nums.find_biggest",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.find_biggest()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # find_biggest()
            np.nanmax(values)                    # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("empty values are skipped (np.nanmax), with a note saying how many; NumPy's np.max would give "
                 "nan.",),
        also="simplydata also says the biggest number in a sentence, with how many numbers it used.",
    ),
    Entry(
        word="nums.find_standard_deviation",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.find_standard_deviation()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # find_standard_deviation()
            np.nanstd(values, ddof=1)            # (1) (2)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the sample standard deviation, dividing by n - 1 (ddof=1), as pandas .std() and R sd(); NumPy's "
                 "own default divides by n.",
                 "empty values are skipped (np.nanstd), with a note saying how many; np.std would give nan.",),
        also="simplydata also says the answer in a sentence. Fewer than 2 numbers give an empty answer, with a "
             "note.",
    ),
    Entry(
        word="nums.count_each",
        ours="""
            numbers = sdata.number_list([3, None, 5, 3, None, 8, 5])
            numbers.count_each()
        """,
        code={"pandas": """
            import numpy as np
            import pandas as pd
            s = pd.Series([3, np.nan, 5, 3, np.nan, 8, 5], name="number")
            # count_each()
            counts = s.value_counts(dropna=False).rename("count").reset_index()   # (1)
            counts["percent"] = (counts["count"] * 100.0 / len(s)).round(1)        # (2)
            counts.sort_values(["count", "number"], ascending=[False, True],
                               na_position="last", kind="stable")                  # (3)
        """},
        compare="table",
        choices=("empty values are counted as a value of their own (dropna=False), so the percents are out of all "
                 "the numbers; pandas' value_counts() leaves them out by default.",
                 "percents are rounded to 1 decimal place.",
                 "the biggest count comes first; equal counts go smallest number first, with the empty values last, "
                 "so the order is the same every time.",),
        also="simplydata also lists the counts in a sentence. The result is a simplydata table (number, count, "
             "percent), so table words work on it.",
    ),
    Entry(
        word="nums.make_number_grid",
        ours="""
            numbers = sdata.number_list([1, 2, 3, 4, 5, 6])
            numbers.make_number_grid(columns=3)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([1, 2, 3, 4, 5, 6])
            # make_number_grid(columns=3)
            values.reshape(-1, 3)                # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("the numbers fill the grid row after row (NumPy's order \"C\"): 1 2 3, then 4 5 6.",),
        also="rows=2 is values.reshape(2, -1). The numbers stay as they are: the grid is new. simplydata stops with "
             "a message when the numbers cannot fill the grid exactly.",
    ),
    # ---- grids: looking
    Entry(
        word="grid.count_rows",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.count_rows()
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # count_rows()
            g.shape[0]
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="grid.count_columns",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.count_columns()
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # count_columns()
            g.shape[1]
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="grid.find_shape",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.find_shape()
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # find_shape()
            g.shape
        """},
        compare="value",
        tolerance=0.0,
        also="The shape is (rows, columns), as plain Python whole numbers.",
    ),
    Entry(
        word="grid.show_first_rows",
        ours="""
            grid = sdata.number_list(1, to=12).make_number_grid(columns=3)
            grid.show_first_rows(2)
        """,
        code={"NumPy": """
            import sys
            import numpy as np
            g = np.arange(1, 13).reshape(-1, 3)
            # show_first_rows(rows=2)
            print(np.array2string(g[:2], threshold=sys.maxsize, separator=", "))   # (1)
        """},
        compare="printed",
        choices=("the numbers are written with commas, like Python lists of rows; NumPy's print leaves out the "
                 "commas. threshold=sys.maxsize keeps a long grid whole, as in show().",),
        also="Without a number it shows the first 5 rows.",
    ),
    Entry(
        word="grid.show_last_rows",
        ours="""
            grid = sdata.number_list(1, to=12).make_number_grid(columns=3)
            grid.show_last_rows(2)
        """,
        code={"NumPy": """
            import sys
            import numpy as np
            g = np.arange(1, 13).reshape(-1, 3)
            # show_last_rows(rows=2)
            print(np.array2string(g[-2:], threshold=sys.maxsize, separator=", "))   # (1)
        """},
        compare="printed",
        choices=("the numbers are written with commas, like Python lists of rows; NumPy's print leaves out the "
                 "commas. threshold=sys.maxsize keeps a long grid whole, as in show().",),
        also="Without a number it shows the last 5 rows.",
    ),
    Entry(
        word="grid.get_number_at",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.get_number_at(row=2, column=3)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # get_number_at(row=2, column=3)
            g[2 - 1, 3 - 1]                      # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("rows and columns count from 1: row 2, column 3 is the bottom right number here. NumPy counts from "
                 "0, so it is g[1, 2].",),
        also="row=\"last\" and column=\"last\" are the last row and column (NumPy g[-1, -1]).",
    ),
    Entry(
        word="grid.get_row",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.get_row(2)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # get_row(position=2)
            g[2 - 1].copy()                      # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("rows count from 1: get_row(2) is the second row from the top, NumPy g[1]. It comes back as new "
                 "numbers (a copy), so changing them leaves the grid as it was.",),
        also="get_row(\"last\") is the bottom row.",
    ),
    Entry(
        word="grid.get_column",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.get_column(2)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # get_column(position=2)
            g[:, 2 - 1].copy()                   # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("columns count from 1 at the left: get_column(2) is NumPy g[:, 1]. It comes back as new numbers "
                 "(a copy), so changing them leaves the grid as it was.",),
        also="get_column(\"last\") is the right-hand column.",
    ),
    Entry(
        word="grid.get_all_numbers",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.get_all_numbers()
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # get_all_numbers()
            g.ravel().copy()                     # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("the numbers are read row by row (NumPy's order \"C\"): 3 5 2, then 8 6 4. Column by column "
                 "would be g.ravel(order=\"F\").",),
        also="The list is new numbers, so number words such as keep_each_number_that work on it.",
    ),
    # ---- grids: rows and columns by position
    Entry(
        word="grid.keep_rows_by_position",
        ours="""
            grid = sdata.number_list(1, to=24).make_number_grid(columns=6)
            grid.keep_rows_by_position(2, to=3)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.arange(1, 25).reshape(-1, 6)
            # keep_rows_by_position(2, to=3)
            g[2 - 1:3]                           # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("rows count from 1 and both ends are kept: rows 2 to 3 are two rows. NumPy counts from 0 and "
                 "leaves out the end, so the same rows are g[1:3].",),
        also="step=2 keeps every 2nd row and a list such as [3, 1] keeps those rows in that order. A grid always "
             "stays a grid, even with one row left (get_row gives it as numbers). simplydata also says the new "
             "size.",
    ),
    Entry(
        word="grid.keep_columns_by_position",
        ours="""
            grid = sdata.number_list(1, to=24).make_number_grid(columns=6)
            grid.keep_columns_by_position(2, to=4)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.arange(1, 25).reshape(-1, 6)
            # keep_columns_by_position(2, to=4)
            g[:, 2 - 1:4]                        # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("columns count from 1 at the left and both ends are kept: columns 2 to 4 are three columns, "
                 "NumPy g[:, 1:4].",),
        also="A block is two steps: keep_rows_by_position(2, to=3) then keep_columns_by_position(2, to=4), as "
             "NumPy g[1:3, 1:4].",
    ),
    Entry(
        word="grid.remove_rows_by_position",
        ours="""
            grid = sdata.number_list(1, to=24).make_number_grid(columns=6)
            grid.remove_rows_by_position(1)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.arange(1, 25).reshape(-1, 6)
            # remove_rows_by_position(positions=1)
            np.delete(g, 1 - 1, axis=0)          # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("rows count from 1: row 1 is the top row, NumPy's row 0.",),
        also="The same positions as keep_rows_by_position (to=, step= or a list). Removing every row stops with a "
             "message.",
    ),
    Entry(
        word="grid.remove_columns_by_position",
        ours="""
            grid = sdata.number_list(1, to=24).make_number_grid(columns=6)
            grid.remove_columns_by_position(1, step=2)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.arange(1, 25).reshape(-1, 6)
            # remove_columns_by_position(1, step=2)
            np.delete(g, np.s_[1 - 1::2], axis=1)    # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("columns count from 1 at the left: from column 1 with step=2 removes columns 1, 3 and 5, NumPy's "
                 "columns 0, 2 and 4.",),
        also="The same positions as keep_columns_by_position (to=, step= or a list).",
    ),
    Entry(
        word="grid.replace_each_number_that",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, None, 4]])
            grid.replace_each_number_that(is_below=4, with_value=0)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, np.nan, 4]])
            # replace_each_number_that(is_below=4, with_value=0)
            np.where(g < 4, 0, g)                # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("the numbers are changed where they are, so the grid keeps its rows and columns (np.where); "
                 "g[g < 4] would give a flat list instead. An empty value matches no condition, so it stays empty.",),
        also="with_value=None makes the numbers empty. The conditions are those of keep_each_number_that, one at a "
             "time.",
    ),
    Entry(
        word="grid.swap_rows_and_columns",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.swap_rows_and_columns()
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # swap_rows_and_columns()
            g.T.copy()
        """},
        compare="value",
        tolerance=0.0,
        also="A grid of 2 rows and 3 columns becomes 3 rows and 2 columns. The step can be undone.",
    ),
    # ---- steps, and passing the numbers on
    Entry(word="nums.undo", ours="""
              numbers = sdata.number_list([12, 15, 9, 20, 14])
              numbers.add(5)
              numbers.undo()
          """, compare="none",
          note="simplydata's own: it keeps the numbers as they were before each step (up to 30 steps) and puts back "
               "the last one. With NumPy you keep a copy yourself before a step (before = values.copy())."),
    Entry(word="nums.show_steps", ours="""
              numbers = sdata.number_list([12, 15, 9, 20, 14])
              numbers.add(5)
              numbers.show_steps()
          """, compare="none",
          note="simplydata's own: it writes down each step as you do it and lists them. A NumPy array keeps no list "
               "of steps; your script is the record."),
    Entry(word="nums.start_again", ours="""
              numbers = sdata.number_list([12, 15, 9, 20, 14])
              numbers.add(5)
              numbers.start_again()
          """, compare="none",
          note="simplydata's own: it keeps the numbers you started with and puts them back, as one more step that "
               "undo() can take back. With NumPy you keep the first array yourself."),
    Entry(
        word="nums.turn_into_table",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.turn_into_table()
        """,
        code={"pandas": """
            import numpy as np
            import pandas as pd
            values = np.array([12, np.nan, 9, 20, 14])
            # turn_into_table()
            pd.DataFrame({"value": values})      # (1)
        """},
        compare="table",
        choices=("the column is called \"value\" unless you give name=, such as turn_into_table(name=\"marks\").",),
        also="The result is a simplydata table, so every table word works on it.",
    ),
    Entry(
        word="nums.start_chart",
        ours="""
            numbers = sdata.number_list([12, 15, 9, 20, 14, 18, 11, 16])
            chart = numbers.start_chart()
            chart.draw_histogram(x="value")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            values = [12, 15, 9, 20, 14, 18, 11, 16]
            # start_chart(): the numbers as a table, the figure and its axes
            df = pd.DataFrame({"value": values})     # (1)
            fig, ax = plt.subplots()
            sns.histplot(df, x="value", bins=10, ax=ax)   # draw_histogram's 10 bins
        """},
        compare="chart",
        check=("bars", "ticks", "limits"),
        choices=("the numbers become a table with one column called \"value\", so chart words name it: "
                 "draw_histogram(x=\"value\").",),
        also="A grid's chart has columns called \"1\", \"2\" ... and rows numbered from 1, ready for "
             "draw_heatmap(). simplydata writes the y label in small letters (count) and gives the chart its paper look; "
             "both are left out here.",
    ),
    Entry(
        word="nums.save",
        ours="""
            import os
            import tempfile
            numbers = sdata.number_list([12, None, 9, 20, 14])
            with tempfile.TemporaryDirectory() as folder:
                numbers.save(os.path.join(folder, "numbers.csv"))
                saved = sdata.table(os.path.join(folder, "numbers.csv"), separator=",")
            saved
        """,
        code={"pandas": """
            import os
            import tempfile
            import numpy as np
            import pandas as pd
            values = np.array([12, np.nan, 9, 20, 14])
            with tempfile.TemporaryDirectory() as folder:
                # save, into the file numbers.csv
                pd.DataFrame({"value": values}).to_csv(os.path.join(folder, "numbers.csv"),
                                                       index=False)              # (1)
                saved = pd.read_csv(os.path.join(folder, "numbers.csv"))
            saved
        """},
        compare="table",
        choices=("the numbers are written as one column called \"value\", without row numbers (index=False), so "
                 "the file reads back as it was.",),
        also="The end of the name decides the type: .xlsx, .tsv, .parquet and .json work as for tables, and .wav "
             "writes a sound file (SciPy io.wavfile, with time_step=). A current limitation of simplydata's own "
             "reader: sdata.table() guesses the separator of a file with only one column wrongly, so such a file "
             "is read back here with separator=\",\" (pandas read_csv reads it as it is).",
    ),
    Entry(
        word="nums.as_numpy",
        ours="""
            numbers = sdata.number_list([12, None, 9, 20, 14])
            numbers.as_numpy()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, np.nan, 9, 20, 14])
            # as_numpy()
            values.copy()                        # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("a copy of the numbers as they are now, so changing the array leaves the simplydata numbers as "
                 "they were.",),
        also="Empty values are nan in the array.",
    ),
]
