"""Numbers: plain-English words over NumPy for lists and grids of numbers.

    nums = numbers([3, 5, 2, 8])
    nums.add(5)            # words change the numbers (nums.undo() takes it back)
    bigger = nums * 2      # symbols make new numbers
    nums.find_average()

sdata.show_lesson(13) teaches them.
"""

from .numbers import NumberGrid, Numbers, make_random_numbers, number_grid, numbers
from .blocks import NumberBlock, number_block

__all__ = ["NumberBlock", "NumberGrid", "Numbers", "make_random_numbers", "make_number_grid", "number_block", "numbers"]
