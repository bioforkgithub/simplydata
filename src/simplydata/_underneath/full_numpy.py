"""Families for 100 %, batches 10-12 (approved by Manish 2026-11-28, plan section 2.4): the NumPy and SciPy words for
lists and grids of numbers, and the new options of existing words, each next to the NumPy or SciPy code that does the
same job. Positions in simplydata count from 1, so the library code adds or takes away 1 where NumPy counts from 0."""

from . import Entry

SAID = "simplydata also says in a sentence what it did and which NumPy or SciPy call did it (undo takes a step back)."
FROM_1 = "simplydata also counts positions from 1, as people do; NumPy counts them from 0."

ENTRIES = [
    # ---------------------------------------------------------------- batch 10: lists of numbers
    Entry(
        word="nums.find_product",
        ours="""
            numbers = sdata.number_list([2, 3, 4.5, None])
            numbers.find_product()
        """,
        code={"NumPy": """
            import numpy as np
            x = np.array([2, 3, 4.5, np.nan])
            # find_product()
            np.nanprod(x)
        """},
        compare="value",
        tolerance=1e-12,
        also="Whole numbers give a whole number that never wraps round (NumPy prod of int64 would); empty values "
             "are left out and counted in the sentence.",
    ),
    Entry(
        word="nums.turn_into_running_total", option='show="product"',
        ours="""
            numbers = sdata.number_list([2, 3, None, 4])
            numbers.turn_into_running_total(show="product")
        """,
        code={"NumPy": """
            import numpy as np
            x = np.array([2, 3, np.nan, 4])
            # turn_into_running_total(show="product")
            out = np.nancumprod(x)
            np.where(np.isnan(x), np.nan, out)
        """},
        compare="value",
        tolerance=1e-12,
        also="An empty value stays empty, as in the running total (NumPy nancumprod would show the product so far).",
    ),
    Entry(
        word="nums.turn_into_changes",
        ours="""
            numbers = sdata.number_list([3, 5, 9, 15, 23])
            numbers.turn_into_changes()
        """,
        code={"NumPy": """
            import numpy as np
            # turn_into_changes()
            np.diff([3, 5, 9, 15, 23])
        """},
        compare="value",
        tolerance=1e-12,
        also="rows_back= gives the change from further back (R diff(x, lag =)); " + SAID,
    ),
    Entry(
        word="nums.turn_into_slopes",
        ours="""
            numbers = sdata.number_list([1, 4, 9, 16, 25])
            numbers.turn_into_slopes(time_step=0.5)
        """,
        code={"NumPy": """
            import numpy as np
            # turn_into_slopes(time_step=0.5)
            np.gradient([1, 4, 9, 16, 25], 0.5)
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.count_in_bins",
        ours="""
            numbers = sdata.number_list([3, 12, 15, 22, 9, 31, 48, 17, 50])
            numbers.count_in_bins(edges=[0, 10, 20, 50])
        """,
        code={"NumPy": """
            import numpy as np
            import pandas as pd
            # count_in_bins(edges=[0, 10, 20, 50])
            counts, edges = np.histogram([3, 12, 15, 22, 9, 31, 48, 17, 50], bins=[0, 10, 20, 50])
            pd.DataFrame({"from": edges[:-1], "to": edges[1:], "count": counts})
        """},
        compare="table",
        tolerance=1e-12,
        also="Empty values are left out and counted; edges= also takes a rule (\"sturges\" ...: NumPy "
             "histogram_bin_edges) and together_with= counts pairs (histogram2d).",
    ),
    Entry(
        word="nums.find_bin_of_each",
        ours="""
            numbers = sdata.number_list([3, 12, 15, 22, 9, 31, 48, 17])
            numbers.find_bin_of_each(edges=[0, 10, 20, 50])
        """,
        code={"NumPy": """
            import numpy as np
            # find_bin_of_each(edges=[0, 10, 20, 50])
            np.digitize([3, 12, 15, 22, 9, 31, 48, 17], [0, 10, 20, 50])
        """},
        compare="value",
        tolerance=1e-12,
        also="Numbers outside the edges get an empty bin with a note (NumPy gives 0 or the number of edges).",
    ),
    Entry(
        word="nums.find_positions_where",
        ours="""
            numbers = sdata.number_list([12, 35, 9, 41, 30, 33])
            numbers.find_positions_where(is_above=30)
        """,
        code={"NumPy": """
            import numpy as np
            x = np.array([12, 35, 9, 41, 30, 33])
            # find_positions_where(is_above=30)
            np.flatnonzero(x > 30) + 1
        """},
        compare="value",
        tolerance=1e-12,
        also=FROM_1,
    ),
    Entry(
        word="nums.keep_numbers_also_in",
        ours="""
            numbers = sdata.number_list([3, 5, 8, 5, 2])
            numbers.keep_numbers_also_in([5, 8, 13, 21])
        """,
        code={"NumPy": """
            import numpy as np
            # keep_numbers_also_in([5, 8, 13, 21])
            np.intersect1d([3, 5, 8, 5, 2], [5, 8, 13, 21])
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.remove_numbers_also_in",
        ours="""
            numbers = sdata.number_list([3, 5, 8, 5, 2])
            numbers.remove_numbers_also_in([5, 8, 13, 21])
        """,
        code={"NumPy": """
            import numpy as np
            # remove_numbers_also_in([5, 8, 13, 21])
            np.setdiff1d([3, 5, 8, 5, 2], [5, 8, 13, 21])
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.keep_numbers_in_only_one",
        ours="""
            numbers = sdata.number_list([3, 5, 8, 5, 2])
            numbers.keep_numbers_in_only_one([5, 8, 13, 21])
        """,
        code={"NumPy": """
            import numpy as np
            # keep_numbers_in_only_one([5, 8, 13, 21])
            np.setxor1d([3, 5, 8, 5, 2], [5, 8, 13, 21])
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.join_numbers_with",
        ours="""
            numbers = sdata.number_list([3, 5, 8, 5, 2])
            numbers.join_numbers_with([5, 8, 13, 21])
        """,
        code={"NumPy": """
            import numpy as np
            # join_numbers_with([5, 8, 13, 21])
            np.union1d([3, 5, 8, 5, 2], [5, 8, 13, 21])
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.find_dot_product_with",
        ours="""
            numbers = sdata.number_list([1, 2, 3])
            numbers.find_dot_product_with([4, 5, 6])
        """,
        code={"NumPy": """
            import numpy as np
            # find_dot_product_with([4, 5, 6])
            np.dot([1, 2, 3], [4, 5, 6])
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also checks that both lists have the same length and no empty values.",
    ),
    Entry(
        word="nums.find_cross_product_with",
        ours="""
            numbers = sdata.number_list([1, 2, 3])
            numbers.find_cross_product_with([4, 5, 6])
        """,
        code={"NumPy": """
            import numpy as np
            # find_cross_product_with([4, 5, 6])
            np.cross([1, 2, 3], [4, 5, 6])
        """},
        compare="value",
        tolerance=1e-12,
        also="Two numbers each give the one number of the turn between them (NumPy 2 refuses them in np.cross).",
    ),
    Entry(
        word="nums.find_size",
        ours="""
            numbers = sdata.number_list([3, 4, 12])
            numbers.find_size()
        """,
        code={"NumPy": """
            import numpy as np
            # find_size()
            np.linalg.vector_norm([3, 4, 12])
        """},
        compare="value",
        tolerance=1e-12,
        also="kind= names the other norms in plain words (\"total size\" is ord=1, \"biggest size\" ord=inf).",
    ),
    Entry(
        word="nums.sort", option='show="positions"',
        ours="""
            numbers = sdata.number_list([30, 10, 20, None, 10])
            numbers.sort(show="positions")
        """,
        code={"NumPy": """
            import numpy as np
            x = np.array([30, 10, 20, np.nan, 10])
            # sort(show="positions")
            np.argsort(x, kind="stable") + 1
        """},
        compare="value",
        tolerance=1e-12,
        also=FROM_1 + " Empty values come last, as NumPy puts NaN last.",
    ),
    Entry(
        word="nums.sort", option="then_by=",
        ours="""
            numbers = sdata.number_list([2, 1, 2, 1])
            numbers.sort(then_by=[9, 8, 7, 6])
        """,
        code={"NumPy": """
            import numpy as np
            x, then_by = np.array([2, 1, 2, 1]), np.array([9, 8, 7, 6])
            # sort(then_by=[9, 8, 7, 6])
            x[np.lexsort((then_by, x))]
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.remove_duplicate_numbers", option='show="positions"',
        ours="""
            numbers = sdata.number_list([3, 5, 3, 8, 5, 5])
            numbers.remove_duplicate_numbers(show="positions")
        """,
        code={"NumPy": """
            import numpy as np
            import pandas as pd
            # remove_duplicate_numbers(show="positions")
            found = np.unique_all([3, 5, 3, 8, 5, 5])
            pd.DataFrame({"number": found.values, "first position": found.indices + 1, "count": found.counts})
        """},
        compare="table",
        tolerance=1e-12,
        also=FROM_1,
    ),
    Entry(
        word="nums.remove_duplicate_numbers", option='show="which number"',
        ours="""
            numbers = sdata.number_list([3, 5, 3, 8, 5, 5])
            numbers.remove_duplicate_numbers(show="which number")
        """,
        code={"NumPy": """
            import numpy as np
            # remove_duplicate_numbers(show="which number")
            np.unique_inverse([3, 5, 3, 8, 5, 5]).inverse_indices + 1
        """},
        compare="value",
        tolerance=1e-12,
        also=FROM_1,
    ),
    Entry(
        word="sdata.number_list", option='spacing="log"',
        ours="""
            sdata.number_list(1, to=1000, how_many=4, spacing="log")
        """,
        code={"NumPy": """
            import numpy as np
            # number_list(1, to=1000, how_many=4, spacing="log")
            np.geomspace(1, 1000, 4)
        """},
        compare="value",
        tolerance=1e-12,
        also="NumPy logspace(0, 3, 4) gives the same numbers from the powers of 10.",
    ),
    Entry(
        word="nums.change_angles_to", option="remove_jumps=",
        ours="""
            numbers = sdata.number_list([350, 355, 2, 8, 12])
            numbers.change_angles_to("degrees", remove_jumps=True)
        """,
        code={"NumPy": """
            import numpy as np
            # change_angles_to("degrees", remove_jumps=True)
            np.unwrap([350, 355, 2, 8, 12], period=360)
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.replace_numbers_where", option="at_positions=",
        ours="""
            numbers = sdata.number_list([4, 8, 15, 16, 23])
            numbers.replace_numbers_where(at_positions=[1, 4], with_value=0)
        """,
        code={"NumPy": """
            import numpy as np
            x = np.array([4, 8, 15, 16, 23])
            # replace_numbers_where(at_positions=[1, 4], with_value=0)
            np.put(x, [0, 3], 0)
            x
        """},
        compare="value",
        tolerance=1e-12,
        also=FROM_1,
    ),
    Entry(
        word="nums.replace_numbers_where", option="rules=",
        ours="""
            numbers = sdata.number_list([2, 9, 15, 30, 7])
            cold = numbers.turn_into_yes_or_no(is_below=8)
            warm = numbers.turn_into_yes_or_no(is_above=20)
            numbers.replace_numbers_where(rules=[(cold, -1), (warm, 1)], with_value=0)
        """,
        code={"NumPy": """
            import numpy as np
            x = np.array([2, 9, 15, 30, 7])
            # replace_numbers_where(rules=[(cold, -1), (warm, 1)], with_value=0)
            np.select([x < 8, x > 20], [-1, 1], default=0)
        """},
        compare="value",
        tolerance=1e-12,
        also="Without with_value= the numbers no rule picks keep their own value. " + SAID,
    ),
    Entry(
        word="nums.replace_numbers_where", option="with_value=",
        ours="""
            numbers = sdata.number_list([2, 9, 15, 30, 7])
            cold = numbers.turn_into_yes_or_no(is_below=8)
            numbers.replace_numbers_where(cold, with_value=[10, 20, 30, 40, 50])
        """,
        code={"NumPy": """
            import numpy as np
            x = np.array([2, 9, 15, 30, 7])
            # replace_numbers_where(cold, with_value=[10, 20, 30, 40, 50])
            np.copyto(x, [10, 20, 30, 40, 50], where=x < 8)
            x
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.take_cosine_transform", option='kind="sine"',
        ours="""
            numbers = sdata.number_list([1, 2, 3, 4])
            numbers.take_cosine_transform(kind="sine")
        """,
        code={"SciPy": """
            from scipy import fft
            # take_cosine_transform(kind="sine")
            fft.dst([1, 2, 3, 4], type=2, norm="ortho")
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.take_cosine_transform", option="inverse=",
        ours="""
            numbers = sdata.number_list([5, -2.23, 0, -0.16])
            numbers.take_cosine_transform(inverse=True)
        """,
        code={"SciPy": """
            from scipy import fft
            # take_cosine_transform(inverse=True)
            fft.idct([5, -2.23, 0, -0.16], type=2, norm="ortho")
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="nums.take_cosine_transform", option='kind="hankel"',
        ours="""
            numbers = sdata.number_list([1.0, 0.8, 0.5, 0.2, 0.1])
            numbers.take_cosine_transform(kind="hankel", log_step=0.1, order=0)
        """,
        code={"SciPy": """
            from scipy import fft
            # take_cosine_transform(kind="hankel", log_step=0.1, order=0)
            fft.fht([1.0, 0.8, 0.5, 0.2, 0.1], dln=0.1, mu=0)
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    # ---------------------------------------------------------------- batches 11-12: grids of numbers
    Entry(
        word="grid.find_positions_where",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.find_positions_where(is_above=4)
        """,
        code={"NumPy": """
            import numpy as np
            import pandas as pd
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # find_positions_where(is_above=4)
            found = np.argwhere(g > 4) + 1
            pd.DataFrame({"row": found[:, 0], "column": found[:, 1]})
        """},
        compare="table",
        tolerance=1e-12,
        also=FROM_1,
    ),
    Entry(
        word="grid.add_border",
        ours="""
            grid = sdata.number_grid([[1, 2], [3, 4]])
            grid.add_border(width=2, with_value=0)
        """,
        code={"NumPy": """
            import numpy as np
            # add_border(width=2, with_value=0)
            np.pad([[1, 2], [3, 4]], 2, mode="constant", constant_values=0)
        """},
        compare="value",
        tolerance=1e-12,
        also="with_value= also copies the grid's own numbers in plain words (\"repeat edge\", \"mirror\", \"wrap "
             "around\"). " + SAID,
    ),
    Entry(
        word="grid.get_part",
        ours="""
            grid = sdata.number_grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            grid.get_part("upper triangle")
        """,
        code={"NumPy": """
            import numpy as np
            # get_part("upper triangle")
            np.triu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        """},
        compare="value",
        tolerance=1e-12,
        also="\"diagonal\" is NumPy diagonal, and as_list=True gives the triangle's numbers (triu_indices).",
    ),
    Entry(
        word="grid.replace_part",
        ours="""
            grid = sdata.number_grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            grid.replace_part("diagonal", with_value=0)
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            # replace_part("diagonal", with_value=0)
            np.fill_diagonal(g, 0)
            g
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="grid.multiply_as_matrix_by",
        ours="""
            grid = sdata.number_grid([[1, 2], [3, 4]])
            grid.multiply_as_matrix_by([[0, 1], [1, 0]])
        """,
        code={"NumPy": """
            import numpy as np
            # multiply_as_matrix_by([[0, 1], [1, 0]])
            np.matmul([[1, 2], [3, 4]], [[0, 1], [1, 0]])
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says when the two do not fit (columns of the first, rows of the second).",
    ),
    Entry(
        word="grid.find_rank",
        ours="""
            grid = sdata.number_grid([[1, 2, 3], [2, 4, 6], [1, 0, 1]])
            grid.find_rank()
        """,
        code={"NumPy": """
            import numpy as np
            # find_rank()
            np.linalg.matrix_rank([[1, 2, 3], [2, 4, 6], [1, 0, 1]])
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says whether the grid has full rank.",
    ),
    Entry(
        word="grid.find_size",
        ours="""
            grid = sdata.number_grid([[1, 2], [3, 4]])
            grid.find_size()
        """,
        code={"NumPy": """
            import numpy as np
            # find_size()
            np.linalg.matrix_norm([[1, 2], [3, 4]])
        """},
        compare="value",
        tolerance=1e-12,
        also="kind= names the other sizes in plain words (\"biggest stretch\" is ord=2, \"nuclear\" ord=\"nuc\").",
    ),
    Entry(
        word="grid.find_condition_number",
        ours="""
            grid = sdata.number_grid([[1, 2], [3, 4]])
            grid.find_condition_number()
        """,
        code={"NumPy": """
            import numpy as np
            # find_condition_number()
            np.linalg.cond([[1, 2], [3, 4]])
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also warns when the number is so big that solving with the grid loses most digits.",
    ),
    Entry(
        word="grid.find_column_space",
        ours="""
            grid = sdata.number_grid([[1, 2], [2, 4], [0, 0]])
            grid.find_column_space()
        """,
        code={"SciPy": """
            from scipy import linalg
            # find_column_space()
            linalg.orth([[1, 2], [2, 4], [0, 0]])
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="grid.take_fourier_transform",
        ours="""
            grid = sdata.number_grid([[1, 2, 1], [0, 1, 0]])
            table = grid.take_fourier_transform(show="all")
            table.get_column("size")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import fft
            # take_fourier_transform(show="all")
            np.abs(fft.fft2([[1, 2, 1], [0, 1, 0]])).ravel()
        """},
        compare="value",
        tolerance=1e-12,
        also="The table also has the frequencies, the phases and the real and imaginary parts; "
             "sdata.find_inverse_fourier_transform turns it back into the grid.",
    ),
    Entry(
        word="grid.take_cosine_transform",
        ours="""
            grid = sdata.number_grid([[1, 2, 1], [0, 1, 0]])
            grid.take_cosine_transform()
        """,
        code={"SciPy": """
            from scipy import fft
            # take_cosine_transform()
            fft.dctn([[1, 2, 1], [0, 1, 0]], type=2, norm="ortho")
        """},
        compare="value",
        tolerance=1e-12,
        also=SAID,
    ),
    Entry(
        word="grid.take_inverse", option="closest_possible=",
        ours="""
            grid = sdata.number_grid([[1, 2], [2, 4], [3, 6]])
            grid.take_inverse(closest_possible=True)
        """,
        code={"SciPy": """
            from scipy import linalg
            # take_inverse(closest_possible=True)
            linalg.pinv([[1, 2], [2, 4], [3, 6]])
        """},
        compare="value",
        tolerance=1e-10,
        also="A symmetric grid uses linalg.pinvh. " + SAID,
    ),
    Entry(
        word="grid.find_determinant", option="as_log=",
        ours="""
            grid = sdata.number_grid([[2, 1], [1, 3]])
            grid.find_determinant(as_log=True)
        """,
        code={"NumPy": """
            import numpy as np
            # find_determinant(as_log=True)
            sign, log_size = np.linalg.slogdet([[2, 1], [1, 3]])
            log_size
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says the sign of the determinant in the sentence.",
    ),
    Entry(
        word="sdata.number_grid", option='kind="toeplitz"',
        ours="""
            sdata.number_grid(kind="toeplitz", first_column=[1, 2, 3], first_row=[1, 5, 6])
        """,
        code={"SciPy": """
            from scipy import linalg
            # number_grid(kind="toeplitz", first_column=[1, 2, 3], first_row=[1, 5, 6])
            linalg.toeplitz([1, 2, 3], [1, 5, 6])
        """},
        compare="value",
        tolerance=1e-12,
        also="The other SciPy kinds (hankel, circulant, companion, hadamard, hilbert, pascal, leslie, helmert, "
             "block diagonal ...) work the same way.",
    ),
    Entry(
        word="sdata.number_grid", option='kind="identity"',
        ours="""
            sdata.number_grid(kind="identity", size=3, shifted_by=1)
        """,
        code={"NumPy": """
            import numpy as np
            # number_grid(kind="identity", size=3, shifted_by=1)
            np.eye(3, 3, 1)
        """},
        compare="value",
        tolerance=1e-12,
        also="\"diagonal\", \"ones below diagonal\", \"vandermonde\" and \"blocks\" are NumPy diag, tri, vander and "
             "block.",
    ),
    Entry(
        word="sdata.number_grid", option='kind="rotation"',
        ours="""
            sdata.number_grid(kind="rotation", axis="z", by_degrees=30)
        """,
        code={"SymPy": """
            import numpy as np
            import sympy as sp
            # number_grid(kind="rotation", axis="z", by_degrees=30)
            np.array(sp.rot_ccw_axis3(sp.pi / 6).evalf(), dtype=float)
        """},
        compare="value",
        tolerance=1e-12,
        also="A counterclockwise turn of a point, as MATLAB rotz and SciPy Rotation; SymPy works under simplydata's "
             "time limit for SymPy; by_degrees= is the angle in degrees.",
    ),
    Entry(
        word="sdata.number_grid", option="from_formula=",
        ours="""
            sdata.number_grid(from_formula="row * column + 1", rows=2, columns=3)
        """,
        code={"NumPy": """
            import numpy as np
            # number_grid(from_formula="row * column + 1", rows=2, columns=3)
            np.fromfunction(lambda i, j: (i + 1) * (j + 1) + 1, (2, 3))
        """},
        compare="value",
        tolerance=1e-12,
        also="row and column count from 1 (NumPy fromfunction gives positions from 0, hence the + 1).",
    ),
    Entry(
        word="sdata.make_coordinate_grids",
        ours="""
            x_grid, y_grid = sdata.make_coordinate_grids(x=[0, 1, 2], y=[10, 20])
            [x_grid.as_numpy(), y_grid.as_numpy()]
        """,
        code={"NumPy": """
            import numpy as np
            # make_coordinate_grids(x=[0, 1, 2], y=[10, 20])
            x_grid, y_grid = np.meshgrid([0, 1, 2], [10, 20])
            [x_grid, y_grid]
        """},
        compare="value",
        tolerance=1e-12,
        also="rows= and columns= give the row and column numbers from 1 (NumPy indices, plus 1).",
    ),
]
