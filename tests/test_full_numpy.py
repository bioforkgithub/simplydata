"""Families for 100 %, batches 10-12 (approved by Manish 2026-11-28, plan section 2.4): the NumPy and SciPy words for
lists and grids of numbers, checked against NumPy and SciPy called directly. Positions count from 1 in simplydata, so
NumPy's positions (from 0) are shifted by 1 here. Every word here is new, so each test fails on the code before."""

import numpy as np
import pytest
from scipy import fft, linalg

import simplydata as sdata
from simplydata._errors import SimplydataError

EXACT = dict(rel=1e-12, abs=1e-12)


def values(thing):
    return np.asarray(thing.as_numpy() if hasattr(thing, "as_numpy") else thing)


# ---------------------------------------------------------------- batch 10: lists
def test_find_product_matches_numpy_and_skips_empty_values(capsys):
    assert sdata.number_list([2, 3, 4.5]).find_product() == pytest.approx(np.prod([2, 3, 4.5]), **EXACT)
    assert sdata.number_list([2, None, 4.5]).find_product() == pytest.approx(9.0, **EXACT)
    assert "1 empty value left out" in capsys.readouterr().out
    big = sdata.number_list([10 ** 6] * 4).find_product()  # int64 would wrap round past 9.2e18
    assert big == 10 ** 24 and isinstance(big, int)


def test_running_product_matches_nancumprod_and_keeps_empty_values():
    numbers = sdata.number_list([2, 3, None, 4])
    numbers.turn_into_running_total(show="product")
    expected = np.nancumprod([2, 3, np.nan, 4])
    expected[2] = np.nan
    assert np.allclose(values(numbers), expected, equal_nan=True)
    numbers.undo()
    numbers.turn_into_running_total()
    assert np.allclose(values(numbers), [2, 5, np.nan, 9], equal_nan=True)
    with pytest.raises(SimplydataError, match="product"):
        numbers.turn_into_running_total(show="products")


def test_turn_into_changes_matches_diff_and_r_lag():
    x = [3, 5, 9, 15, 23, 31]
    numbers = sdata.number_list(x)
    assert values(numbers.turn_into_changes()).tolist() == np.diff(x).tolist()
    numbers.undo()
    assert values(numbers.turn_into_changes(how_many_times=2)).tolist() == np.diff(x, n=2).tolist()
    numbers.undo()
    # R: diff(c(3, 5, 9, 15, 23, 31), lag = 2) gives 6 10 14 16
    assert values(numbers.turn_into_changes(rows_back=2)).tolist() == [6, 10, 14, 16]
    with pytest.raises(SimplydataError, match="rows_back"):
        numbers.turn_into_changes(rows_back=0)
    with pytest.raises(SimplydataError, match="more than"):
        sdata.number_list([1, 2]).turn_into_changes(rows_back=2)


def test_turn_into_slopes_matches_gradient():
    y = [1, 4, 9, 16, 25]
    assert np.allclose(values(sdata.number_list(y).turn_into_slopes(time_step=0.5)), np.gradient(y, 0.5))
    times = [0, 1, 3, 4, 6]
    assert np.allclose(values(sdata.number_list(y).turn_into_slopes(at_times=times)),
                       np.gradient(np.array(y, float), np.array(times, float)))
    assert np.allclose(values(sdata.number_list(y).turn_into_slopes()), np.gradient(y))
    with pytest.raises(SimplydataError, match="not both"):
        sdata.number_list(y).turn_into_slopes(time_step=1, at_times=times)


def test_count_in_bins_matches_histogram_and_its_rules():
    x = [3, 12, 15, 22, 9, 31, 48, 17, 50]
    counts = sdata.number_list(x).count_in_bins(edges=[0, 10, 20, 50]).as_pandas()
    found, edges = np.histogram(x, bins=[0, 10, 20, 50])
    assert counts["count"].tolist() == found.tolist()
    assert counts["from"].tolist() == edges[:-1].tolist() and counts["to"].tolist() == edges[1:].tolist()
    by_rule = sdata.number_list(x).count_in_bins(edges="sturges").as_pandas()
    rule_edges = np.histogram_bin_edges(x, bins="sturges")
    assert np.allclose(by_rule["from"], rule_edges[:-1]) and by_rule["count"].sum() == len(x)
    ten = sdata.number_list(x).count_in_bins().as_pandas()
    assert ten["count"].tolist() == np.histogram(x)[0].tolist()
    between = sdata.number_list(x).count_in_bins(how_many_bins=5, between=[0, 100]).as_pandas()
    assert between["count"].tolist() == np.histogram(x, bins=5, range=(0, 100))[0].tolist()
    with pytest.raises(SimplydataError, match="edges"):
        sdata.number_list(x).count_in_bins(edges=[0, 10, 5])


def test_count_in_bins_of_pairs_matches_histogram2d():
    x, y = [1, 2, 2, 3, 4, 5], [5, 3, 2, 2, 1, 0]
    grid = sdata.number_list(x).count_in_bins(edges=3, together_with=y, other_edges=2)
    assert values(grid).tolist() == np.histogram2d(x, y, bins=[3, 2])[0].astype(int).tolist()


def test_find_bin_of_each_matches_digitize_and_empties_the_outside():
    x = [3, 12, 15, 22, 9, 31, 48, 17]
    edges = [0, 10, 20, 50]
    assert values(sdata.number_list(x).find_bin_of_each(edges=edges)).tolist() == np.digitize(x, edges).tolist()
    right = sdata.number_list([10, 20, 5]).find_bin_of_each(edges=edges, bins_include="right edge")
    assert values(right).tolist() == np.digitize([10, 20, 5], edges, right=True).tolist()
    outside = values(sdata.number_list([-1, 5, 60]).find_bin_of_each(edges=edges))
    assert np.isnan(outside[0]) and outside[1] == 1 and np.isnan(outside[2])


def test_sort_positions_and_then_by_match_argsort_and_lexsort():
    x = np.array([30, 10, 20, np.nan, 10])
    numbers = sdata.number_list(x.tolist())
    positions = numbers.sort(show="positions")
    assert values(positions).tolist() == (np.argsort(x, kind="stable") + 1).tolist()
    assert np.allclose(values(numbers), x, equal_nan=True)  # show="positions" changes nothing
    biggest = values(sdata.number_list([3, 1, 2]).sort(show="positions", biggest_first=True)).tolist()
    assert biggest == [1, 3, 2]
    a, b = np.array([2, 1, 2, 1]), np.array([9, 8, 7, 6])
    assert values(sdata.number_list(a).sort(then_by=b)).tolist() == a[np.lexsort((b, a))].tolist()
    with pytest.raises(SimplydataError, match="then_by"):
        sdata.number_list([1, 2]).sort(then_by=[1])


def test_remove_duplicate_numbers_show_matches_unique_all_and_unique_inverse():
    x = [3, 5, 3, 8, 5, 5]
    table = sdata.number_list(x).remove_duplicate_numbers(show="positions").as_pandas()
    found = np.unique_all(x)
    assert table["number"].tolist() == found.values.tolist()
    assert table["first position"].tolist() == (found.indices + 1).tolist()
    assert table["count"].tolist() == found.counts.tolist()
    which = sdata.number_list(x).remove_duplicate_numbers(show="which number")
    assert values(which).tolist() == (np.unique_inverse(x).inverse_indices + 1).tolist()
    plain = sdata.number_list(x).remove_duplicate_numbers()
    assert values(plain).tolist() == [3, 5, 8]  # without show=, the first place of each, as before


@pytest.mark.parametrize("word, func", [("keep_numbers_also_in", np.intersect1d),
                                        ("remove_numbers_also_in", np.setdiff1d),
                                        ("keep_numbers_in_only_one", np.setxor1d),
                                        ("join_numbers_with", np.union1d)])
def test_set_words_match_numpy(word, func):
    a, b = [3, 5, 8, 5, 2], [5, 8, 13, 21]
    numbers = sdata.number_list(a)
    getattr(numbers, word)(b)
    assert values(numbers).tolist() == func(a, b).tolist()
    numbers.undo()
    assert values(numbers).tolist() == a


def test_set_words_leave_out_empty_values(capsys):
    numbers = sdata.number_list([1, None, 2])
    numbers.join_numbers_with([2, 3])
    assert values(numbers).tolist() == [1, 2, 3]
    assert "1 empty value was left out" in capsys.readouterr().out


def test_dot_and_cross_products_match_numpy():
    assert sdata.number_list([1, 2, 3]).find_dot_product_with([4, 5, 6]) == np.dot([1, 2, 3], [4, 5, 6])
    assert values(sdata.number_list([1, 2, 3]).find_cross_product_with([4, 5, 6])).tolist() == \
        np.cross([1, 2, 3], [4, 5, 6]).tolist()
    assert sdata.number_list([1, 2]).find_cross_product_with([3, 4]) == 1 * 4 - 2 * 3
    with pytest.raises(SimplydataError, match="same length"):
        sdata.number_list([1, 2, 3]).find_dot_product_with([1, 2])
    with pytest.raises(SimplydataError, match="empty"):
        sdata.number_list([1, None, 3]).find_dot_product_with([1, 2, 3])


def test_find_positions_where_on_numbers_and_grids():
    x = np.array([12, 35, 9, 41, 30, 33])
    assert values(sdata.number_list(x).find_positions_where(is_above=30)).tolist() == \
        (np.flatnonzero(x > 30) + 1).tolist()
    g = np.array([[3, 5, 2], [8, 6, 4]])
    table = sdata.number_grid(g).find_positions_where(is_above=4).as_pandas()
    assert table[["row", "column"]].to_numpy().tolist() == (np.argwhere(g > 4) + 1).tolist()
    flat = sdata.number_grid(g).find_positions_where(is_above=4, show="position in list")
    assert values(flat).tolist() == (np.flatnonzero(g > 4) + 1).tolist()


def test_find_size_matches_numpy_norms():
    x = [3, -4, 12]
    numbers = sdata.number_list(x)
    assert numbers.find_size() == pytest.approx(np.linalg.vector_norm(x), **EXACT)
    assert numbers.find_size(kind="total size") == pytest.approx(np.linalg.norm(x, 1), **EXACT)
    assert numbers.find_size(kind="biggest size") == pytest.approx(12, **EXACT)
    assert numbers.find_size(kind=3) == pytest.approx(np.linalg.norm(x, 3), **EXACT)
    g = np.array([[1.0, 2], [3, 4]])
    grid = sdata.number_grid(g)
    for kind, order in [("frobenius", "fro"), ("biggest column total", 1), ("biggest row total", np.inf),
                        ("biggest stretch", 2), ("nuclear", "nuc"), ("smallest stretch", -2)]:
        assert grid.find_size(kind=kind) == pytest.approx(np.linalg.norm(g, order), **EXACT), kind
    assert grid.find_size(kind="nuclear") == pytest.approx(linalg.norm(g, "nuc"), **EXACT)
    with pytest.raises(SimplydataError, match="frobenius"):
        grid.find_size(kind="length")


def test_number_list_log_spacing_matches_geomspace_and_logspace():
    assert np.allclose(values(sdata.number_list(1, to=1000, how_many=4, spacing="log")), np.geomspace(1, 1000, 4))
    assert np.allclose(values(sdata.number_list(100, to=1000, how_many=5, spacing="log")), np.logspace(2, 3, 5))
    with pytest.raises(SimplydataError, match="same sign"):
        sdata.number_list(-1, to=10, how_many=3, spacing="log")
    with pytest.raises(SimplydataError, match="how_many"):
        sdata.number_list(1, to=10, spacing="log")


def test_change_angles_to_remove_jumps_matches_unwrap():
    degrees = [350, 355, 2, 8, 12, 359, 3]
    numbers = sdata.number_list(degrees)
    numbers.change_angles_to("degrees", remove_jumps=True)
    assert np.allclose(values(numbers), np.unwrap(degrees, period=360))
    radians = [3.0, -3.0, -2.9]
    assert np.allclose(values(sdata.number_list(radians).change_angles_to("radians", remove_jumps=True)),
                       np.unwrap(radians))


def test_replace_numbers_where_at_positions_rules_and_other_numbers():
    x = np.array([4, 8, 15, 16, 23])
    numbers = sdata.number_list(x)
    numbers.replace_numbers_where(at_positions=[1, 4], with_value=0)
    expected = x.copy()
    np.put(expected, [0, 3], 0)
    assert values(numbers).tolist() == expected.tolist()
    numbers.undo()
    numbers.replace_numbers_where(at_positions=[2, 3], with_value=[1.5, 2.5])
    assert values(numbers).tolist() == [4, 1.5, 2.5, 16, 23]
    numbers.undo()
    cold, warm = numbers.turn_into_yes_or_no(is_below=10), numbers.turn_into_yes_or_no(is_above=20)
    numbers.replace_numbers_where(rules=[(cold, -1), (warm, 1)])
    assert values(numbers).tolist() == np.select([x < 10, x > 20], [-1, 1], default=x).tolist()
    numbers.undo()
    numbers.replace_numbers_where(rules=[(cold, -1)], with_value="empty")
    assert np.allclose(values(numbers), [-1, -1, np.nan, np.nan, np.nan], equal_nan=True)
    numbers.undo()
    numbers.replace_numbers_where(cold, with_value=[10, 20, 30, 40, 50])
    copied = x.copy()
    np.copyto(copied, [10, 20, 30, 40, 50], where=x < 10)
    assert values(numbers).tolist() == copied.tolist()
    with pytest.raises(SimplydataError, match="one of them"):
        numbers.replace_numbers_where(cold, at_positions=[1], with_value=0)
    with pytest.raises(SimplydataError, match="from 1 to 5"):
        numbers.replace_numbers_where(at_positions=[0], with_value=0)


def test_grid_replace_numbers_at_the_positions_find_positions_where_gives():
    g = np.array([[3, 5, 2], [8, 6, 4]])
    grid = sdata.number_grid(g)
    grid.replace_numbers_where(at_positions=grid.find_positions_where(is_above=4), with_value=0)
    assert values(grid).tolist() == np.where(g > 4, 0, g).tolist()
    grid.undo()
    grid.replace_numbers_where(at_positions=[(1, 3), (2, 1)], with_value=-1)
    assert values(grid).tolist() == [[3, 5, -1], [-1, 6, 4]]


def test_cosine_transform_kinds_and_inverses_match_scipy():
    x = [1.0, 2.0, 3.0, 4.0, 2.0]
    for kind, inverse, func in [("sine", False, fft.dst), ("cosine", True, fft.idct), ("sine", True, fft.idst)]:
        got = sdata.number_list(x).take_cosine_transform(kind=kind, inverse=inverse)
        assert np.allclose(values(got), func(x, type=2, norm="ortho")), (kind, inverse)
    there_and_back = sdata.number_list(x).take_cosine_transform().take_cosine_transform(inverse=True)
    assert np.allclose(values(there_and_back), x)
    hankel = sdata.number_list(x).take_cosine_transform(kind="hankel", log_step=0.1, order=0.5)
    assert np.allclose(values(hankel), fft.fht(x, dln=0.1, mu=0.5))
    back = sdata.number_list(x).take_cosine_transform(kind="hankel", log_step=0.1, order=0.5, inverse=True)
    assert np.allclose(values(back), fft.ifht(x, dln=0.1, mu=0.5))
    with pytest.raises(SimplydataError, match="log_step"):
        sdata.number_list(x).take_cosine_transform(kind="hankel")


# ---------------------------------------------------------------- batches 11-12: grids
def test_multiply_as_matrix_by_matches_matmul_matvec_vecmat_and_multi_dot():
    a = np.array([[1.0, 2], [3, 4], [5, 6]])
    b = np.array([[0.0, 1, 2], [1, 0, 1]])
    grid = sdata.number_grid(a)
    assert np.allclose(values(grid.multiply_as_matrix_by(b)), a @ b)
    assert np.allclose(values(grid.multiply_as_matrix_by([1, 2])), np.matvec(a, [1, 2]))
    assert np.allclose(values(grid.multiply_as_matrix_by([1, 2, 3], from_the_left=True)), np.vecmat([1, 2, 3], a))
    c = sdata.number_grid([[1.0], [2.0], [0.5]])
    chain = grid.multiply_as_matrix_by([sdata.number_grid(b), c])
    assert np.allclose(values(chain), np.linalg.multi_dot([a, b, values(c)]))
    assert values(grid).tolist() == a.tolist()  # the grid stays as it is
    with pytest.raises(SimplydataError, match="do not fit"):
        grid.multiply_as_matrix_by([1, 2, 3])


@pytest.mark.parametrize("with_value, mode", [("repeat edge", "edge"), ("mirror", "reflect"),
                                              ("mirror with edge", "symmetric"), ("wrap around", "wrap")])
def test_add_border_matches_pad(with_value, mode):
    g = np.array([[1, 2, 3], [4, 5, 6]])
    grid = sdata.number_grid(g)
    grid.add_border(width=2, with_value=with_value)
    assert values(grid).tolist() == np.pad(g, 2, mode=mode).tolist()


def test_add_border_with_numbers_and_empty_values():
    g = np.array([[1, 2], [3, 4]])
    assert values(sdata.number_grid(g).add_border(width=1, with_value=0)).tolist() == np.pad(g, 1).tolist()
    assert values(sdata.number_grid(g).add_border(width=[1, 0], with_value=9)).tolist() == \
        np.pad(g, ((1, 1), (0, 0)), constant_values=9).tolist()
    empty = values(sdata.number_grid(g).add_border(width=1, with_value="empty"))
    assert np.isnan(empty[0, 0]) and empty[1, 1] == 1


def test_get_part_matches_diagonal_triu_tril_and_their_positions():
    g = np.arange(1, 13).reshape(3, 4)
    grid = sdata.number_grid(g)
    for k in (-1, 0, 2):
        assert values(grid.get_part("diagonal", shifted_by=k)).tolist() == np.diagonal(g, k).tolist()
        assert values(grid.get_part("upper triangle", shifted_by=k)).tolist() == np.triu(g, k).tolist()
        assert values(grid.get_part("lower triangle", shifted_by=k)).tolist() == np.tril(g, k).tolist()
        assert values(grid.get_part("upper triangle", shifted_by=k, as_list=True)).tolist() == \
            g[np.triu_indices(3, k, 4)].tolist()
        assert values(grid.get_part("lower triangle", shifted_by=k, as_list=True)).tolist() == \
            g[np.tril_indices(3, k, 4)].tolist()
    assert grid.get_part("diagonal").find_total() == np.trace(g)
    with pytest.raises(SimplydataError, match="diagonal"):
        grid.get_part("middle")


def test_replace_part_matches_fill_diagonal_and_triangle_positions():
    g = np.arange(1, 10).reshape(3, 3)
    grid = sdata.number_grid(g)
    grid.replace_part("diagonal", with_value=0)
    expected = g.copy()
    np.fill_diagonal(expected, 0)
    assert values(grid).tolist() == expected.tolist()
    grid.undo()
    grid.replace_part("diagonal", with_value=[7, 8], shifted_by=1)
    assert values(grid).tolist() == [[1, 7, 3], [4, 5, 8], [7, 8, 9]]
    grid.undo()
    grid.replace_part("lower triangle", with_value=0, shifted_by=-1)
    expected = g.copy()
    expected[np.tril_indices(3, -1)] = 0
    assert values(grid).tolist() == expected.tolist()
    grid.undo()
    grid.replace_part("upper triangle", with_value="empty")
    assert np.isnan(values(grid)[0, 2]) and values(grid)[2, 0] == 7
    with pytest.raises(SimplydataError, match="one for each of the 3 places"):
        grid.replace_part("diagonal", with_value=[1, 2])


@pytest.mark.parametrize("show, over", [("half", "rows and columns"), ("all", "rows and columns"), ("half", "rows"),
                                        ("all", "columns")])
def test_grid_fourier_transform_matches_scipy_and_comes_back(show, over):
    g = np.array([[1.0, 2, 1, 0], [0, 1, 0, 3], [2, 2, 1, 1]])
    table = sdata.number_grid(g).take_fourier_transform(show=show, over=over)
    frame = table.as_pandas()
    expected = {("half", "rows and columns"): fft.rfft2(g), ("all", "rows and columns"): fft.fft2(g),
                ("half", "rows"): fft.rfft(g, axis=0), ("all", "columns"): fft.fft(g, axis=1)}[(show, over)]
    assert np.allclose(frame["real part"], expected.real.ravel())
    assert np.allclose(frame["imaginary part"], expected.imag.ravel())
    assert np.allclose(frame["size"], np.abs(expected).ravel())
    back = sdata.find_inverse_fourier_transform(table)
    assert np.allclose(values(back), g)


def test_grid_fourier_transform_frequencies_and_zero_in_middle():
    g = np.arange(12.0).reshape(3, 4)
    frame = sdata.number_grid(g).take_fourier_transform(show="all", time_step=0.5).as_pandas()
    rows, columns = np.meshgrid(fft.fftfreq(3, 0.5), fft.fftfreq(4, 0.5), indexing="ij")
    assert np.allclose(frame["row frequency"], rows.ravel()) and np.allclose(frame["column frequency"], columns.ravel())
    middle = sdata.number_grid(g).take_fourier_transform(with_zero_in_middle=True)
    assert np.allclose(middle.as_pandas()["real part"], fft.fftshift(fft.fft2(g)).real.ravel())
    assert np.allclose(values(sdata.find_inverse_fourier_transform(middle)), g)


def test_grid_fourier_table_with_changed_rows_is_refused():
    table = sdata.number_grid([[1.0, 2], [3, 4]]).take_fourier_transform()
    table.keep_first_rows(2)
    with pytest.raises(SimplydataError, match="keep every row"):
        sdata.find_inverse_fourier_transform(table)


@pytest.mark.parametrize("kind, inverse, func", [("cosine", False, fft.dctn), ("sine", False, fft.dstn),
                                                 ("cosine", True, fft.idctn), ("sine", True, fft.idstn)])
def test_grid_cosine_transform_matches_scipy(kind, inverse, func):
    g = np.array([[1.0, 2, 1], [0, 1, 0], [4, 2, 1]])
    got = sdata.number_grid(g).take_cosine_transform(kind=kind, inverse=inverse)
    assert np.allclose(values(got), func(g, type=2, norm="ortho"))


def test_rank_condition_number_and_column_space_match_numpy_and_scipy():
    g = np.array([[1.0, 2, 3], [2, 4, 6], [1, 0, 1]])
    grid = sdata.number_grid(g)
    assert grid.find_rank() == np.linalg.matrix_rank(g) == 2
    h = np.array([[1.0, 2], [3, 4]])
    assert sdata.number_grid(h).find_condition_number() == pytest.approx(np.linalg.cond(h), **EXACT)
    assert sdata.number_grid(h).find_condition_number(kind="biggest row total") == \
        pytest.approx(np.linalg.cond(h, np.inf), **EXACT)
    assert np.allclose(values(grid.find_column_space()), linalg.orth(g))
    assert values(grid.find_column_space()).shape == (3, 2)


def test_take_inverse_closest_possible_matches_pinv_and_pinvh():
    a = np.array([[1.0, 2], [2, 4], [3, 6]])
    grid = sdata.number_grid(a)
    grid.take_inverse(closest_possible=True)
    assert np.allclose(values(grid), linalg.pinv(a))
    symmetric = np.array([[2.0, 1], [1, 2]])
    closest = sdata.number_grid(symmetric).take_inverse(closest_possible=True)
    assert np.allclose(values(closest), linalg.pinvh(symmetric))
    with pytest.raises(SimplydataError, match="choose one"):
        sdata.number_grid(symmetric).take_inverse(exactly=True, closest_possible=True)


def test_find_determinant_as_log_matches_slogdet(capsys):
    g = np.array([[1.0, 2], [3, 4]])  # determinant -2
    sign, logged = np.linalg.slogdet(g)
    assert sdata.number_grid(g).find_determinant(as_log=True) == pytest.approx(logged, **EXACT)
    assert "negative" in capsys.readouterr().out and sign == -1
    huge = np.eye(400) * 10  # the determinant 1e400 is too big for a decimal; its log is not
    assert sdata.number_grid(huge).find_determinant(as_log=True) == pytest.approx(400 * np.log(10), rel=1e-12)


SPECIAL = [
    ("toeplitz", dict(first_column=[1, 2, 3], first_row=[1, 5, 6]), linalg.toeplitz([1, 2, 3], [1, 5, 6])),
    ("hankel", dict(first_column=[1, 2, 3], last_row=[3, 4, 5]), linalg.hankel([1, 2, 3], [3, 4, 5])),
    ("circulant", dict(first_column=[1, 2, 3]), linalg.circulant([1, 2, 3])),
    ("companion", dict(values=[1, -6, 11, -6]), linalg.companion([1, -6, 11, -6])),
    ("fiedler companion", dict(values=[1, -6, 11, -6]), linalg.fiedler_companion([1, -6, 11, -6])),
    ("fiedler", dict(values=[1, 4, 6]), linalg.fiedler([1, 4, 6])),
    ("convolution", dict(values=[1, 2], size=3), linalg.convolution_matrix([1, 2], 3)),
    ("hadamard", dict(size=4), linalg.hadamard(4)),
    ("hilbert", dict(size=4), linalg.hilbert(4)),
    ("inverse hilbert", dict(size=4), linalg.invhilbert(4)),
    ("pascal", dict(size=4), linalg.pascal(4)),
    ("lower pascal", dict(size=4), linalg.pascal(4, kind="lower")),
    ("upper pascal", dict(size=4), linalg.pascal(4, kind="upper")),
    ("inverse pascal", dict(size=4), linalg.invpascal(4)),
    ("leslie", dict(first_row=[0.1, 2, 1], survival=[0.2, 0.8]), linalg.leslie([0.1, 2, 1], [0.2, 0.8])),
    ("helmert", dict(size=4), linalg.helmert(4)),
    ("block diagonal", dict(of=[[[1, 2], [3, 4]], [[5]]]), linalg.block_diag([[1, 2], [3, 4]], [[5]])),
    ("identity", dict(size=3, shifted_by=-1), np.eye(3, 3, -1)),
    ("identity", dict(rows=2, columns=4), np.eye(2, 4)),
    ("diagonal", dict(values=[1, 2, 3], shifted_by=1), np.diag([1, 2, 3], 1)),
    ("ones below diagonal", dict(rows=3, columns=4, shifted_by=1), np.tri(3, 4, 1)),
    ("vandermonde", dict(values=[1, 2, 3], columns=4), np.vander([1, 2, 3], 4)),
    ("blocks", dict(of=[[[[1, 2]], [[3]]], [[[4, 5]], [[6]]]]),
     np.block([[np.array([[1, 2]]), np.array([[3]])], [np.array([[4, 5]]), np.array([[6]])]])),
]


@pytest.mark.parametrize("kind, options, expected", SPECIAL, ids=[s[0] for s in SPECIAL])
def test_number_grid_kinds_match_numpy_and_scipy(kind, options, expected):
    assert np.allclose(values(sdata.number_grid(kind=kind, **options)), expected)


@pytest.mark.parametrize("axis, n", [("x", 1), ("y", 2), ("z", 3)])
def test_number_grid_rotation_matches_sympy(axis, n):
    sp = pytest.importorskip("sympy")
    expected = np.array(getattr(sp, f"rot_ccw_axis{n}")(sp.pi * 30 / 180).evalf(), dtype=float)
    assert np.allclose(values(sdata.number_grid(kind="rotation", axis=axis, by_degrees=30)), expected)


def test_number_grid_from_formula_matches_fromfunction():
    pytest.importorskip("sympy")
    got = sdata.number_grid(from_formula="row * column + 1", rows=3, columns=4)
    assert np.allclose(values(got), np.fromfunction(lambda i, j: (i + 1) * (j + 1) + 1, (3, 4)))
    with pytest.raises(SimplydataError, match="row and column only"):
        sdata.number_grid(from_formula="row * k", rows=2, columns=2)


def test_number_grid_kind_errors_name_what_is_needed():
    with pytest.raises(SimplydataError, match="toeplitz"):
        sdata.number_grid(kind="toeplits", first_column=[1, 2])
    with pytest.raises(SimplydataError, match="power of 2"):
        sdata.number_grid(kind="hadamard", size=6)
    with pytest.raises(SimplydataError, match="go with kind="):
        sdata.number_grid([[1, 2]], first_column=[1, 2])
    with pytest.raises(SimplydataError, match="survival"):
        sdata.number_grid(kind="leslie", first_row=[1, 2, 3], survival=[0.5])


def test_make_coordinate_grids_matches_meshgrid_and_indices():
    x_grid, y_grid = sdata.make_coordinate_grids(x=[0, 1, 2], y=[10, 20])
    mx, my = np.meshgrid([0, 1, 2], [10, 20])
    assert values(x_grid).tolist() == mx.tolist() and values(y_grid).tolist() == my.tolist()
    row_grid, column_grid = sdata.make_coordinate_grids(rows=2, columns=3)
    r, c = np.indices((2, 3)) + 1
    assert values(row_grid).tolist() == r.tolist() and values(column_grid).tolist() == c.tolist()
    with pytest.raises(SimplydataError, match="x= and y="):
        sdata.make_coordinate_grids(x=[1, 2])


def test_new_words_have_numpy_pointers(capsys):
    for typed, word in [("np.argsort", 'sort(show="positions")'), ("np.diff", "turn_into_changes"),
                        ("np.histogram", "count_in_bins"), ("np.linalg.matrix_rank", "find_rank"),
                        ("np.fft.fft2", "take_fourier_transform"), ("scipy.linalg.toeplitz", 'kind="toeplitz"'),
                        ("np.meshgrid", "make_coordinate_grids"), ("np.trace", 'get_part("diagonal")'),
                        ("scipy.fft.dctn", "take_cosine_transform"), ("np.linalg.pinv", "closest_possible=True"),
                        ("sp.rot_axis3", 'kind="rotation"')]:
        sdata.help(typed)
        assert word in capsys.readouterr().out, typed


# ---------------------------------------------------------------- independent review fixes (2026-11-28)
def test_running_product_of_whole_numbers_never_wraps_round(capsys):
    numbers = sdata.number_list([10] * 20)  # 10**19 is past int64, which wraps to a negative number
    numbers.turn_into_running_total(show="product")
    got = values(numbers)
    assert got[17] == 10 ** 18 and got[-1] == pytest.approx(1e20, rel=1e-15) and (got > 0).all()
    assert "given as decimals" in capsys.readouterr().out
    small = sdata.number_list([2, 3, 4]).turn_into_running_total(show="product")
    assert values(small).dtype.kind == "i" and values(small).tolist() == [2, 6, 24]


def test_multiply_as_matrix_by_a_list_uses_matmul_not_numpy_2_2_only_calls():
    import inspect

    from simplydata.numbers import numpy_grid_words

    source = inspect.getsource(numpy_grid_words.NumPyGridWords.multiply_as_matrix_by)
    assert "np.matvec" not in source and "np.vecmat" not in source  # NumPy 2.2; the floor is numpy>=2.1
    a = np.array([[1.0, 2], [3, 4]])
    assert np.allclose(values(sdata.number_grid(a).multiply_as_matrix_by([1, 2])), a @ [1, 2])
    assert np.allclose(values(sdata.number_grid(a).multiply_as_matrix_by([1, 2], from_the_left=True)), [1, 2] @ a)


def test_rotation_turns_a_point_counterclockwise(capsys):
    turn = values(sdata.number_grid(kind="rotation", axis="z", by_degrees=90))
    assert np.allclose(turn @ [1, 0, 0], [0, 1, 0])  # x goes to y, as MATLAB rotz(90) and SciPy Rotation
    from scipy.spatial.transform import Rotation

    for axis in "xyz":
        expected = Rotation.from_euler(axis, 30, degrees=True).as_matrix()
        assert np.allclose(values(sdata.number_grid(kind="rotation", axis=axis, by_degrees=30)), expected), axis
    assert "rot_ccw_axis3" in capsys.readouterr().out
    sdata.help("sp.rot_ccw_axis1")
    assert "by_degrees=30" in capsys.readouterr().out


def test_count_in_bins_says_how_many_fell_outside(capsys):
    sdata.number_list([1, 5, 15, 25, 99]).count_in_bins(edges=[0, 10, 20])
    out = capsys.readouterr().out
    assert "3 numbers counted in 2 bins" in out and "2 numbers outside the edges were not counted" in out


def test_find_bin_of_each_closes_the_outer_edge_like_count_in_bins():
    edges = [0, 10, 20, 50]
    bins = values(sdata.number_list([50, 0, 20]).find_bin_of_each(edges=edges))
    assert bins.tolist() == [3, 1, 3]
    counts = sdata.number_list([50]).count_in_bins(edges=edges).as_pandas()["count"].tolist()
    assert counts == [0, 0, 1]  # both put 50 in the last bin
    right = values(sdata.number_list([0, 10, 50]).find_bin_of_each(edges=edges, bins_include="right edge"))
    assert right.tolist() == [1, 1, 3]


def test_sort_positions_sentence_says_which_comes_first(capsys):
    sdata.number_list([30, 10, 20]).sort(show="positions")
    assert "Which number comes first, second" in capsys.readouterr().out


def test_remove_duplicate_numbers_show_counts_empty_values_once():
    table = sdata.number_list([3, None, 3, None]).remove_duplicate_numbers(show="positions").as_pandas()
    assert len(table) == 2 and table["count"].tolist() == [2, 2] and table["first position"].tolist() == [1, 2]
    which = values(sdata.number_list([3, None, 3, None]).remove_duplicate_numbers(show="which number"))
    assert which.tolist() == [1, 2, 1, 2]


def test_changes_from_further_back_and_two_number_cross_product_call_libraries(capsys):
    x = [3, 5, 9, 15, 23, 31]
    got = values(sdata.number_list(x).turn_into_changes(rows_back=2, how_many_times=2))
    assert got.tolist() == [8, 6]  # R: diff(c(3, 5, 9, 15, 23, 31), lag = 2, differences = 2)
    assert "pandas Series.diff(periods=2)" in capsys.readouterr().out
    assert sdata.number_list([1, 2]).find_cross_product_with([3, 4]) == -2
    assert "with 0 as the third number" in capsys.readouterr().out


def test_from_formula_with_a_constant_prints_one_line(capsys):
    pytest.importorskip("sympy")
    grid = sdata.number_grid(from_formula="5", rows=2, columns=2)
    assert values(grid).tolist() == [[5, 5], [5, 5]]
    assert len([line for line in capsys.readouterr().out.splitlines() if line.strip()]) == 1


def test_pointers_after_the_review(capsys):
    for typed, word in [("scipy.fft.dst", 'take_cosine_transform(kind="sine")'), ("np.astype", "astype(int)"),
                        ("np.linalg.logm", "scipy.linalg.logm"), ("scipy.linalg.sqrtm", "scipy.linalg.sqrtm")]:
        sdata.help(typed)
        assert word in capsys.readouterr().out, typed


def test_small_review_fixes():
    with pytest.raises(SimplydataError, match="takes no numbers of its own"):
        sdata.number_grid([1, 2, 3], kind="identity", size=3)
    with pytest.raises(SimplydataError, match="needs a square grid"):
        sdata.number_grid([[1, 2, 3], [4, 5, 6]]).find_condition_number(kind="frobenius")
    grid = sdata.number_list([1, 2, None, 4]).count_in_bins(edges=2, together_with=[1, None, 3, 4])
    assert values(grid).sum() == 2  # the two whole pairs only


def test_polynomial_hermite_e_name():
    pytest.importorskip("sympy")
    import sympy as sp

    assert sdata.polynomial("Hermite_E", degree=3).as_sympy() == sp.hermite_prob_poly(3, sp.Symbol("x"))
