"""The NumPy + SciPy phase, batch 1 (approved by Manish 2026-11-25): yes or no values, rounding, angles, positions,
every pair, and blocks of numbers with any number of directions. The same job in NumPy (xarray where it lines up
named directions, pandas where a block comes from a table)."""

from . import Entry


def _e(word, ours, numpy, also, tolerance=0.0, choices=(), option="", library="NumPy"):
    return Entry(word=word, ours=ours, code={library: numpy}, compare="value", tolerance=tolerance, also=also,
                 choices=choices, option=option)


_PLATE_OURS = ('block = sdata.number_block([[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], '
               '[[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]]], directions_named=["hour", "row", "column"])')
_PLATE_NUMPY = "import numpy as np\n            a = np.arange(1, 25).reshape(2, 3, 4)"

ENTRIES = [
    # ---- yes or no values
    _e("nums.turn_into_yes_or_no", """
            nums = sdata.numbers([18.0, 21.5, None, 25.0, 19.0])
            nums.turn_into_yes_or_no(is_above=20)
        """, """
            import numpy as np
            values = np.array([18.0, 21.5, np.nan, 25.0, 19.0])
            # turn_into_yes_or_no(is_above=20)
            values > 20                          # (1)
        """, "The numbers themselves do not change; the yes or no values print how many are yes. & | ~ join them "
             "(np.logical_and, np.logical_or, np.logical_not).",
       choices=("an empty value is no (NumPy's nan > 20 is False too); is_empty=True asks for the empty ones.",)),
    _e("nums.keep_numbers_where", """
            deep = sdata.numbers([5, 150, 80, 300, 20]).turn_into_yes_or_no(is_above=100)
            nums = sdata.numbers([1.1, 9.5, 4.2, 12.0, 2.0])
            nums.keep_numbers_where(deep)
        """, """
            import numpy as np
            depth = np.array([5, 150, 80, 300, 20])
            nitrate = np.array([1.1, 9.5, 4.2, 12.0, 2.0])
            # keep_numbers_where(deep)
            nitrate[depth > 100]
        """, "On a grid or a block the shape stays and the other numbers become empty (np.where(deep, values, "
             "np.nan)), as xarray's where. The step can be undone."),
    _e("nums.remove_numbers_where", """
            land = sdata.numbers([0, 0, 1, 0, 1]).turn_into_yes_or_no(is_equal_to=1)
            nums = sdata.numbers([12, 15, 9, 20, 14])
            nums.remove_numbers_where(land)
        """, """
            import numpy as np
            land = np.array([0, 0, 1, 0, 1]) == 1
            values = np.array([12, 15, 9, 20, 14])
            # remove_numbers_where(land)
            values[~land]
        """, "On a grid or a block the shape stays and the removed numbers become empty."),
    _e("nums.replace_numbers_where", """
            land = sdata.numbers([0, 0, 1, 0, 1]).turn_into_yes_or_no(is_equal_to=1)
            nums = sdata.numbers([12.0, 15.0, 9.0, 20.0, 14.0])
            nums.replace_numbers_where(land, with_value="empty")
        """, """
            import numpy as np
            land = np.array([0, 0, 1, 0, 1]) == 1
            values = np.array([12.0, 15.0, 9.0, 20.0, 14.0])
            # replace_numbers_where(land, with_value="empty")
            np.where(land, np.nan, values)
        """, 'with_value="empty" (or None) makes them empty; a number puts that number in. The step can be undone.'),
    _e("nums.count_numbers_that", """
            nums = sdata.numbers([18.0, 21.5, None, 25.0, 19.0])
            nums.count_numbers_that(is_above=20)
        """, """
            import numpy as np
            values = np.array([18.0, 21.5, np.nan, 25.0, 19.0])
            # count_numbers_that(is_above=20)
            np.count_nonzero(values > 20)
        """, "Grids and blocks take over= or in_each= for one count per position of the other directions "
             "(np.count_nonzero(test, axis=)). On yes or no values without a test, it counts the yes."),
    _e("nums.check_if_any_number", """
            nums = sdata.numbers([18.0, 21.5, None, 25.0, 19.0])
            nums.check_if_any_number(is_above=30)
        """, """
            import numpy as np
            values = np.array([18.0, 21.5, np.nan, 25.0, 19.0])
            # check_if_any_number(is_above=30)
            bool(np.any(values > 30))
        """, "It says the answer in a sentence (how many pass) and gives back True or False."),
    _e("nums.check_if_all_numbers", """
            nums = sdata.numbers([18.0, 21.5, None, 25.0, 19.0])
            nums.check_if_all_numbers(is_above=0)
        """, """
            import numpy as np
            values = np.array([18.0, 21.5, np.nan, 25.0, 19.0])
            # check_if_all_numbers(is_above=0)
            bool(np.all(values[~np.isnan(values)] > 0))   # (1)
        """, "It says the answer in a sentence and gives back True or False; over= gives one answer per position.",
       choices=("empty values are skipped: NumPy's np.all(values > 0) would say False because nan > 0 is False.",)),
    _e("nums.check_if_same_as", """
            nums = sdata.numbers([0.1 + 0.2, 1.0])
            nums.check_if_same_as([0.3, 1.0], within=1e-12)
        """, """
            import numpy as np
            a = np.array([0.1 + 0.2, 1.0])
            # check_if_same_as([0.3, 1.0], within=1e-12)
            bool(np.allclose(a, [0.3, 1.0], rtol=0, atol=1e-12))
        """, "Without within= the numbers must be exactly equal (np.array_equal); two empty values count as the "
             "same. A difference names how many differ and where the first is."),
    _e("grid.keep_rows_where", """
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4], [1, 9, 7]])
            grid.keep_rows_where(column=3, is_above=3)
        """, """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4], [1, 9, 7]])
            # keep_rows_where(column=3, is_above=3)
            g[g[:, 2] > 3]
        """, "column= counts from 1, as positions do everywhere in simplydata. The step can be undone."),
    _e("grid.remove_rows_where", """
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4], [1, 9, 7]])
            grid.remove_rows_where(column=1, is_below=2)
        """, """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4], [1, 9, 7]])
            # remove_rows_where(column=1, is_below=2)
            g[~(g[:, 0] < 2)]
        """, "column= counts from 1. The step can be undone."),
    # ---- rounding, angles and positions
    _e("nums.round_down", """
            nums = sdata.numbers([2.7, -2.3, 0.5])
            nums.round_down()
        """, """
            import numpy as np
            values = np.array([2.7, -2.3, 0.5])
            # round_down()
            np.floor(values)
        """, "Minus numbers go down too: -2.3 becomes -3. take_whole_part() goes towards 0 instead."),
    _e("nums.round_up", """
            nums = sdata.numbers([2.1, -2.7, 0.5])
            nums.round_up()
        """, """
            import numpy as np
            values = np.array([2.1, -2.7, 0.5])
            # round_up()
            np.ceil(values)
        """, "Minus numbers go up too: -2.7 becomes -2."),
    _e("nums.take_whole_part", """
            nums = sdata.numbers([2.7, -2.7, 0.5])
            nums.take_whole_part()
        """, """
            import numpy as np
            values = np.array([2.7, -2.7, 0.5])
            # take_whole_part()
            np.trunc(values)
        """, "The decimals go: 2.7 becomes 2 and -2.7 becomes -2 (towards 0)."),
    _e("nums.take_sin", """
            nums = sdata.numbers([0, 30, 90])
            nums.take_sin(degrees=True)
        """, """
            import numpy as np
            values = np.array([0, 30, 90])
            # take_sin(degrees=True)
            np.sin(np.deg2rad(values))           # (1)
        """, "The sentence says which unit the angles were in.", tolerance=1e-15,
       choices=("angles are in radians unless degrees=True, as in NumPy, so the code is the same as NumPy's "
                "(np.sin(values) without degrees=True).",)),
    _e("nums.take_cos", """
            nums = sdata.numbers([0, 60, 90])
            nums.take_cos(degrees=True)
        """, """
            import numpy as np
            values = np.array([0, 60, 90])
            # take_cos(degrees=True)
            np.cos(np.deg2rad(values))
        """, "Angles are in radians unless degrees=True, as in NumPy.", tolerance=1e-15),
    _e("nums.take_tan", """
            nums = sdata.numbers([0, 45, 60])
            nums.take_tan(degrees=True)
        """, """
            import numpy as np
            values = np.array([0, 45, 60])
            # take_tan(degrees=True)
            np.tan(np.deg2rad(values))
        """, "Angles are in radians unless degrees=True. At 90 degrees NumPy gives a very big number.",
       tolerance=1e-15),
    _e("nums.change_angles_to", """
            nums = sdata.numbers([0, 1.5708, 3.14159])
            nums.change_angles_to("degrees")
        """, """
            import numpy as np
            values = np.array([0, 1.5708, 3.14159])
            # change_angles_to("degrees")
            np.rad2deg(values)
        """, 'change_angles_to("radians") goes back (np.deg2rad).', tolerance=1e-15),
    _e("nums.find_where_biggest", """
            nums = sdata.numbers([12, 15, None, 20, 14])
            nums.find_where_biggest()
        """, """
            import numpy as np
            values = np.array([12, 15, np.nan, 20, 14])
            # find_where_biggest()
            int(np.nanargmax(values)) + 1        # (1)
        """, "The sentence gives the NumPy index too (position 4, NumPy index 3). Grids and blocks give a position in "
             "every direction (np.unravel_index); over= gives one per position of the other directions.",
       choices=("positions count from 1 (NumPy's argmax counts from 0); empty values are skipped (np.nanargmax); "
                "on a tie, the first.",)),
    _e("nums.find_where_smallest", """
            nums = sdata.numbers([12, 15, None, 9, 14])
            nums.find_where_smallest()
        """, """
            import numpy as np
            values = np.array([12, 15, np.nan, 9, 14])
            # find_where_smallest()
            int(np.nanargmin(values)) + 1
        """, "Positions count from 1; empty values are skipped; on a tie, the first."),
    _e("nums.make_pair_table_with", """
            nums = sdata.numbers([0, 10, 50])
            nums.make_pair_table_with([0, 10, 50], by_subtracting=True)
        """, """
            import numpy as np
            depths = np.array([0, 10, 50])
            # make_pair_table_with(depths, by_subtracting=True)
            np.subtract.outer(depths, depths)
        """, "Multiplying is the default (np.multiply.outer, the times table); as_blocks=True gives np.kron. "
             "Dividing by 0 gives an empty value with a note."),
    # ---- blocks of numbers
    Entry(word="sdata.number_block", ours="""
            sdata.number_block(sdata.get_example("island"), directions_named=["east", "north"], values="height")
        """, code={"pandas": """
            import numpy as np
            import pandas as pd
            df = pd.read_csv("island.csv")
            # number_block(table, directions_named=["east", "north"], values="height")
            labels = [np.sort(df[n].unique()) for n in ["east", "north"]]
            every = pd.MultiIndex.from_product(labels, names=["east", "north"])
            df.set_index(["east", "north"])["height"].reindex(every).to_numpy().reshape(15, 15)
        """}, compare="value", tolerance=0.0, data="island",
          also="The labels of each direction are kept (for keep_where); a place with no row is empty. From lists or "
               "a NumPy array the block is np.asarray; of_shape= and filled_with= are np.full.",
          choices=()),
    _e("block.find_shape", f"""
            {_PLATE_OURS}
            block.find_shape()
        """, f"""
            {_PLATE_NUMPY}
            # find_shape()
            a.shape
        """, "It also says the shape in words: 2 hours x 3 rows x 4 columns."),
    _e("block.count_directions", f"""
            {_PLATE_OURS}
            block.count_directions()
        """, f"""
            {_PLATE_NUMPY}
            # count_directions()
            a.ndim
        """, "It also names the directions."),
    Entry(word="block.find_direction_names", ours=f"""
            {_PLATE_OURS}
            block.find_direction_names()
        """, compare="none",
          note="simplydata's own: the names of the directions, kept next to the NumPy array (NumPy arrays have no "
               "names; xarray's DataArray.dims holds them)."),
    _e("block.get_number_at", f"""
            {_PLATE_OURS}
            block.get_number_at(hour=2, row=1, column=3)
        """, f"""
            {_PLATE_NUMPY}
            # get_number_at(hour=2, row=1, column=3)
            a[1, 0, 2]
        """, "Positions count from 1 and are given by direction name; \"last\" is the last one."),
    _e("block.find_average", f"""
            {_PLATE_OURS}
            block.find_average(over="hour")
        """, f"""
            {_PLATE_NUMPY}
            # find_average(over="hour")
            np.nanmean(a, axis=0)                # (1)
        """, "in_each= names the directions kept instead. The result keeps the names row and column, so it lines up "
             "with the block by name (no keepdims needed).", tolerance=1e-12,
       choices=("over= names the direction that goes (NumPy's axis= as a name); empty values are skipped "
                "(np.nanmean).",)),
    _e("block.keep_by_position_in", f"""
            {_PLATE_OURS}
            block.keep_by_position_in("column", [1, 3])
        """, f"""
            {_PLATE_NUMPY}
            # keep_by_position_in("column", [1, 3])
            np.take(a, [0, 2], axis=2)
        """, "Positions count from 1, both ends of a run included (1, to=3). The step can be undone."),
    _e("block.remove_by_position_in", f"""
            {_PLATE_OURS}
            block.remove_by_position_in("row", 2)
        """, f"""
            {_PLATE_NUMPY}
            # remove_by_position_in("row", 2)
            np.delete(a, [1], axis=1)
        """, "Positions count from 1. The step can be undone."),
    Entry(word="block.keep_where", ours="""
            block = sdata.number_block(sdata.get_example("island"), directions_named=["east", "north"], values="height")
            block.keep_where("east", is_between=[5, 2])
        """, code={"xarray": """
            import pandas as pd
            df = pd.read_csv("island.csv")
            da = df.set_index(["east", "north"])["height"].to_xarray()
            # keep_where("east", is_between=[5, 2])
            da.sel(east=slice(2, 5)).values      # (1)
        """}, compare="value", tolerance=0.0, data="island",
          choices=("the range is taken in either order, and turned round when the labels run downward (xarray sel "
                   "would give nothing for slice(5, 2)).",),
          also="Without xarray, NumPy finds the positions on the labels (np.flatnonzero) and takes them."),
    Entry(word="block.remove_where", ours="""
            block = sdata.number_block(sdata.get_example("island"), directions_named=["east", "north"], values="height")
            block.remove_where("north", is_one_of=[0, 1])
        """, code={"xarray": """
            import pandas as pd
            df = pd.read_csv("island.csv")
            da = df.set_index(["east", "north"])["height"].to_xarray()
            # remove_where("north", is_one_of=[0, 1])
            da.drop_sel(north=[0, 1]).values
        """}, compare="value", tolerance=0.0, data="island",
          also="The labels left are kept with the numbers."),
    _e("block.change_shape_to", f"""
            {_PLATE_OURS}
            block.change_shape_to(one_row_per="hour")
        """, f"""
            {_PLATE_NUMPY}
            # change_shape_to(one_row_per="hour")
            a.reshape(2, -1)                     # (1)
        """, "It prints the shape before and after; only_show_new_shape=True runs the same reshape on a stand-in "
             "with no numbers (np.broadcast_to(0, shape)) and changes nothing.",
       choices=("the numbers are read row by row (NumPy's C order); one_row_per= must be the first direction, "
                "so a reshape cannot mix up directions (move_direction first otherwise).",)),
    _e("block.add_direction", f"""
            {_PLATE_OURS}
            block.add_direction("plate", at_position=1)
        """, f"""
            {_PLATE_NUMPY}
            # add_direction("plate", at_position=1)
            np.expand_dims(a, 0)
        """, "The new direction has size 1 and a name, so the block lines up by name with others."),
    _e("block.remove_directions_of_size_one", """
            block = sdata.number_block([[[[1, 2, 3]], [[4, 5, 6]]]])
            block.remove_directions_of_size_one()
        """, """
            import numpy as np
            a = np.arange(1, 7).reshape(1, 2, 1, 3)
            # remove_directions_of_size_one()
            np.squeeze(a)
        """, "The names of the other directions stay."),
    _e("block.swap_directions", f"""
            {_PLATE_OURS}
            block.swap_directions("row", "column")
        """, f"""
            {_PLATE_NUMPY}
            # swap_directions("row", "column")
            np.swapaxes(a, 1, 2)
        """, "The names swap with the numbers."),
    _e("block.move_direction", f"""
            {_PLATE_OURS}
            block.move_direction("column", to_position=1)
        """, f"""
            {_PLATE_NUMPY}
            # move_direction("column", to_position=1)
            np.moveaxis(a, 2, 0)
        """, "to_position= counts from 1."),
    _e("block.rotate", f"""
            {_PLATE_OURS}
            block.rotate(by_quarter_turns=1)
        """, f"""
            {_PLATE_NUMPY}
            # rotate(by_quarter_turns=1)
            np.rot90(a, k=1, axes=(1, 2))
        """, "The last two directions turn, as a picture, anticlockwise; over= names two others."),
    _e("block.reverse", f"""
            {_PLATE_OURS}
            block.reverse(over="row")
        """, f"""
            {_PLATE_NUMPY}
            # reverse(over="row")
            np.flip(a, axis=1)
        """, "Without over=, every direction is turned round (np.flip(a)); labels turn round with their direction."),
    _e("block.move_round_by", f"""
            {_PLATE_OURS}
            block.move_round_by(1, over="column")
        """, f"""
            {_PLATE_NUMPY}
            # move_round_by(1, over="column")
            np.roll(a, 1, axis=2)
        """, "The numbers that fall off the end come round to the start."),
    _e("block.insert_numbers", f"""
            {_PLATE_OURS}
            block.insert_numbers(0, at_position=2, over="row")
        """, f"""
            {_PLATE_NUMPY}
            # insert_numbers(0, at_position=2, over="row")
            np.insert(a, 1, 0, axis=1)
        """, "at_position= counts from 1: the new numbers come before that position."),
    _e("block.repeat_each_number", f"""
            {_PLATE_OURS}
            block.repeat_each_number(2, over="column")
        """, f"""
            {_PLATE_NUMPY}
            # repeat_each_number(2, over="column")
            np.repeat(a, 2, axis=2)
        """, "1, 2 becomes 1, 1, 2, 2 along that direction."),
    _e("block.repeat_whole_block", f"""
            {_PLATE_OURS}
            block.repeat_whole_block(2, over="row")
        """, f"""
            {_PLATE_NUMPY}
            # repeat_whole_block(2, over="row")
            np.tile(a, (1, 2, 1))
        """, "over= a name the block lacks adds that direction in front (np.tile with one more 2)."),
    _e("block.add_numbers_from", f"""
            {_PLATE_OURS}
            block.add_numbers_from([[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]], over="hour")
        """, f"""
            {_PLATE_NUMPY}
            # add_numbers_from(other, over="hour")
            np.concatenate([a, np.arange(1, 13).reshape(1, 3, 4)], axis=0)
        """, "Blocks that name every direction are put in the same order first (np.transpose)."),
    _e("block.split_into_pieces", f"""
            {_PLATE_OURS}
            [piece.as_numpy() for piece in block.split_into_pieces(3, over="column")]
        """, f"""
            {_PLATE_NUMPY}
            # split_into_pieces(3, over="column")
            np.array_split(a, 3, axis=2)
        """, "Pieces are as equal as they can be; the block itself does not change."),
    _e("block.split_into_one_block_per", f"""
            {_PLATE_OURS}
            [part.as_numpy() for part in block.split_into_one_block_per("hour")]
        """, f"""
            {_PLATE_NUMPY}
            # split_into_one_block_per("hour")
            list(np.unstack(a, axis=0))
        """, "Each new block keeps the names of the other directions."),
    _e("sdata.stack_up", """
            sdata.stack_up([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], as_new_direction="image")
        """, """
            import numpy as np
            # stack_up([a, b], as_new_direction="image")
            np.stack([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], axis=0)
        """, "The new direction comes first and has the name given."),
    # ---- stretching
    Entry(word="block.show_how_it_lines_up_with", ours="""
            block = sdata.number_block(of_shape=(2, 3, 4), filled_with=1)
            block.show_how_it_lines_up_with(sdata.numbers([1, 2, 3, 4]))
        """, code={"NumPy": """
            import numpy as np
            # show_how_it_lines_up_with(other)
            print("NumPy: np.broadcast_shapes((2, 3, 4), (4,))")
            np.broadcast_shapes((2, 3, 4), (4,))
        """}, compare="printed",
          also="simplydata draws the two shapes lined up from the right and says, for each direction, which side is "
               "used again; nothing is computed on the numbers."),
    _e("block.stretch_to", """
            block = sdata.number_block([[1, 2, 3, 4]])
            block.stretch_to((3, 4))
        """, """
            import numpy as np
            a = np.arange(1, 5).reshape(1, 4)
            # stretch_to((3, 4))
            np.broadcast_to(a, (3, 4)).copy()
        """, "Given another block, the shapes line up by name when both blocks name every direction."),
    _e("sdata.stretch_to_same_shape", """
            [b.as_numpy() for b in sdata.stretch_to_same_shape([[1], [2], [3]], [10, 20])]
        """, """
            import numpy as np
            # stretch_to_same_shape(a, b)
            [np.array(x) for x in np.broadcast_arrays(np.array([[1], [2], [3]]), np.array([10, 20]))]
        """, "Two new blocks; the old ones do not change."),
    Entry(word="sdata.hide_stretching_notes", ours="""
            sdata.hide_stretching_notes()
            sdata.show_stretching_notes()
        """, compare="none",
          note="simplydata's own: a setting that stops the sentences saying which numbers were used again. NumPy "
               "says nothing when it broadcasts."),
    Entry(word="sdata.show_stretching_notes", ours="""
            sdata.show_stretching_notes()
        """, compare="none",
          note="simplydata's own: the sentences that say which numbers were used again are printed (the default)."),
    # ---- options that change the call underneath
    _e("nums.divide_by", """
            nums = sdata.numbers([7, -7, 9])
            nums.divide_by(2, rounding_down=True)
        """, """
            import numpy as np
            values = np.array([7, -7, 9])
            # divide_by(2, rounding_down=True)
            np.floor_divide(values, 2)
        """, "-7 divided by 2 rounded down is -4, as Python's //. Dividing by 0 gives an empty value with a note.",
       option="rounding_down="),
    Entry(word="nums.take_fourier_transform", option="with_zero_in_middle=", ours="""
            nums = sdata.numbers([1.0, 3.0, 2.0, 0.5, 4.0, 2.5])
            nums.take_fourier_transform(time_step=0.5, with_zero_in_middle=True)
        """, code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import fft
            x = np.array([1.0, 3.0, 2.0, 0.5, 4.0, 2.5])
            # take_fourier_transform(time_step=0.5, with_zero_in_middle=True)
            z, f = fft.fftshift(fft.fft(x)), fft.fftshift(fft.fftfreq(6, d=0.5))
            pd.DataFrame({"frequency": f, "size": np.abs(z), "phase": np.degrees(np.angle(z)),
                          "real part": z.real, "imaginary part": z.imag})
        """}, compare="table", tolerance=1e-12,
          also="sdata.find_inverse_fourier_transform puts the order back (fft.ifftshift) before turning the table "
               "into numbers."),
]
