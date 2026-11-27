"""Numbers: plain-English words over NumPy for lists and grids of numbers.

    numbers = sdata.numbers([3, 5, 2, 8])
    numbers.add(5)            # words change the numbers (numbers.undo() takes it back)
    bigger = numbers * 2      # symbols make new numbers
    numbers.find_average()

sdata.show_lesson(13) teaches them.
"""

from .numbers import NumberGrid, Numbers, make_random_numbers, number_grid, numbers
from .blocks import NumberBlock, number_block
from .numbers_2 import count_ways_to_choose, count_ways_to_order
from .block_files import show_whats_inside

__all__ = ["NumberBlock", "NumberGrid", "Numbers", "make_random_numbers", "make_number_grid", "number_block", "numbers"]
