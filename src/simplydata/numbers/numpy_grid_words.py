"""Families for 100 %, batches 11-12 (approved by Manish 2026-11-28, plan section 2.4): NumPy and SciPy words for grids.

multiply_as_matrix_by (NumPy matmul, linalg.multi_dot), add_border (pad), the grid parts get_part and replace_part
(G8: diagonal, triu, tril and their positions), take_fourier_transform on a grid (scipy.fft fft2, rfft2, fft over one
direction), take_cosine_transform on a grid (dctn, dstn, idctn, idstn), and the grid size words find_rank
(linalg.matrix_rank), find_condition_number (linalg.cond) and find_column_space (scipy.linalg.orth). The helpers of
replace_numbers_where(at_positions=, rules=) (NumPy put, select) and of take_inverse(closest_possible=True) (pinv,
pinvh) and find_determinant(as_log=True) (slogdet) are here too. Rows and columns count from 1.
"""

from __future__ import annotations

import numbers as _nb

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._typing import _Same
from ._base import NOT_GIVEN, amount, is_number, say, to_array

PARTS = ("diagonal", "upper triangle", "lower triangle")
BORDERS = {"repeat edge": "edge", "mirror": "reflect", "mirror with edge": "symmetric", "wrap around": "wrap"}
FOURIER_OVER = ("rows and columns", "rows", "columns")
COSINE_KINDS = ("cosine", "sine", "hankel")
CONDITION_KINDS = {"biggest stretch": None, "frobenius": "fro", "biggest column total": 1, "biggest row total": np.inf,
                   "nuclear": "nuc"}


def _shift(shifted_by) -> int:
    if isinstance(shifted_by, bool) or not isinstance(shifted_by, _nb.Integral):
        raise SimplydataError("shifted_by= needs a whole number: 1 is the diagonal just above the main one, -1 the one "
                              "just below, 0 the main one.")
    return int(shifted_by)


def part_positions(shape, name: str, shifted_by: int):
    """The NumPy positions (from 0) of a part of a grid: diag (as np.diag_indices with an offset), triu_indices and
    tril_indices."""
    rows, columns = shape
    if name == "diagonal":
        start_row, start_column = max(-shifted_by, 0), max(shifted_by, 0)
        n = max(min(rows - start_row, columns - start_column), 0)
        return np.arange(n) + start_row, np.arange(n) + start_column
    if name == "upper triangle":
        return np.triu_indices(rows, shifted_by, columns)
    return np.tril_indices(rows, shifted_by, columns)


def _value_or_values(with_value, size: int, step: str, example: str):
    """with_value= of replace_part and replace_numbers_where(at_positions=): a number, "empty", or one number for
    each place."""
    if with_value is NOT_GIVEN:
        raise SimplydataError(f'{step}() needs with_value=, a number, "empty" or one number for each place.'
                              f"\nFor example:  {example}")
    if with_value is None or (isinstance(with_value, str) and with_value == "empty"):
        return np.nan, "empty"
    if is_number(with_value):
        return with_value, say(with_value)
    values = to_array(with_value, "with_value=", example).ravel()
    if values.size != size:
        raise SimplydataError(f"with_value= needs one number, or one for each of the {size} places; it has "
                              f"{values.size}.\nFor example:  {example}")
    return values, "the numbers given"


def _room_for(values, new):
    """The NumPy type that holds both the grid's numbers and the new ones (whole numbers become decimals when an
    empty value or a decimal comes in)."""
    kind = np.result_type(values, np.asarray(new))
    return values.astype(kind, copy=True)


def replace_at_positions(owner, at_positions, with_value):
    """replace_numbers_where(at_positions=): NumPy put at the positions, counting from 1 (on a grid, row and column
    pairs, turned into NumPy's flat positions with ravel_multi_index)."""
    example = (f"{owner._name}.replace_numbers_where(at_positions=[1, 3], with_value=0)" if owner._values.ndim == 1
               else f"{owner._name}.replace_numbers_where(at_positions=positions, with_value=0)")
    values = owner._values
    if values.ndim == 1:
        found = to_array(at_positions, "at_positions=", example).ravel()
        if found.dtype.kind not in "iu" or np.any(found < 1) or np.any(found > values.size):
            raise SimplydataError(f"at_positions= needs whole numbers from 1 to {values.size} (positions count from "
                                  f"1).\nFor example:  {example}")
        flat = found.astype(np.int64) - 1
    elif values.ndim == 2:
        frame = getattr(at_positions, "_frame", None)
        if frame is not None:
            import pandas as pd

            frame = pd.DataFrame(frame) if not hasattr(frame, "to_numpy") else frame
            if not {"row", "column"} <= set(frame.columns):
                raise SimplydataError("at_positions= needs the table find_positions_where gives (columns row and "
                                      f"column), or (row, column) pairs.\nFor example:  {example}")
            pairs = np.column_stack([np.asarray(frame["row"]), np.asarray(frame["column"])])
        else:
            pairs = to_array(at_positions, "at_positions=", example)
            if pairs.ndim != 2 or pairs.shape[1] != 2:
                raise SimplydataError(f"at_positions= on a grid needs (row, column) pairs, such as [(1, 2), (3, 1)].\n"
                                      f"For example:  {example}")
        rows, columns = values.shape
        if (pairs.dtype.kind not in "iu" or np.any(pairs < 1) or np.any(pairs[:, 0] > rows)
                or np.any(pairs[:, 1] > columns)):
            raise SimplydataError(f"at_positions= needs rows from 1 to {rows} and columns from 1 to {columns}.")
        flat = np.ravel_multi_index((pairs[:, 0] - 1, pairs[:, 1] - 1), values.shape)
    else:
        raise SimplydataError("at_positions= works on numbers and grids; on a block, use keep_where or "
                              "replace_numbers_where with yes or no values.")
    value, said = _value_or_values(with_value, flat.size, "replace_numbers_where", example)
    new = _room_for(values, value)
    np.put(new, flat, value)
    print(f"Replaced the numbers at {amount(flat.size, 'position')} with {said}. NumPy: np.put({owner._name}, "
          "positions, value) (positions from 0 in NumPy)")
    return owner._change(f"replace numbers at positions with {said}", new)


def replace_by_rules(owner, rules, with_value):
    """replace_numbers_where(rules=[(yes_no, value), ...]): NumPy select; the first rule that says yes wins."""
    example = f"{owner._name}.replace_numbers_where(rules=[(cold, -1), (warm, 1)])"
    if not isinstance(rules, (list, tuple)) or not rules or not all(
            isinstance(r, (list, tuple)) and len(r) == 2 for r in rules):
        raise SimplydataError(f"rules= needs a list of (yes or no values, value) pairs.\nFor example:  {example}")
    conditions, choices, said = [], [], []
    for yes_no, value in rules:
        conditions.append(owner._mask_from(yes_no, "replace_numbers_where"))
        if value is None or (isinstance(value, str) and value == "empty"):
            choices.append(np.nan)
            said.append("empty")
        elif is_number(value):
            choices.append(value)
            said.append(say(value))
        else:
            raise SimplydataError(f'Each rule gives a number or "empty"; one gives {value!r}.\nFor example:  {example}')
    if with_value is NOT_GIVEN:
        default, other = owner._values, "keep their own number"
    else:
        default, other = _value_or_values(with_value, owner._values.size, "replace_numbers_where", example)
        other = f"get {other}"
    new = np.select(conditions, choices, default=default)
    hits = int(np.count_nonzero(np.logical_or.reduce(conditions)))
    print(f"{amount(len(rules), 'rule')} ({', '.join(said)}) gave {hits} of {amount(owner._values.size)} a new value; "
          f"the others {other}. NumPy: np.select(conditions, values, default)")
    return owner._change("replace numbers by rules", new)


def inverse_grid_fourier(info, frame):
    """sdata.find_inverse_fourier_transform on the table of grid.take_fourier_transform(): SciPy irfft2 / ifft2 (or
    irfft / ifft over one direction), the rows checked as find_inverse_fourier_transform checks them for numbers."""
    from scipy import fft

    from .numbers import NumberGrid

    names = list(info["names"])
    if not {*names, "real part", "imaginary part"} <= set(frame.columns):
        raise SimplydataError("find_inverse_fourier_transform() needs the columns " + ", ".join(names)
                              + ", real part and imaginary part of the table grid.take_fourier_transform() gave back.")
    now = np.asarray(frame[names].to_numpy(), dtype=float)
    if now.shape != info["frequency"].shape or not np.array_equal(now, info["frequency"]):
        raise SimplydataError("find_inverse_fourier_transform() needs the rows of the table as "
                              "grid.take_fourier_transform() made them; keep every row (set the real and imaginary "
                              "parts of a pair to 0 to take it out).")
    z = (np.asarray(frame["real part"], dtype=float) + 1j * np.asarray(frame["imaginary part"], dtype=float))
    z = z.reshape(info["shape"])
    axes = {"rows and columns": (0, 1), "rows": (0,), "columns": (1,)}[info["over"]]
    if info["zero_in_middle"]:
        z = fft.ifftshift(z, axes=axes)
    rows, columns = info["grid"]
    if info["show"] == "half":
        values = (fft.irfft2(z, s=(rows, columns)) if len(axes) == 2 else
                  fft.irfft(z, n=info["grid"][axes[0]], axis=axes[0]))
        name = "irfft2" if len(axes) == 2 else "irfft"
    else:
        values = (fft.ifft2(z) if len(axes) == 2 else fft.ifft(z, axis=axes[0])).real
        name = "ifft2" if len(axes) == 2 else "ifft"
    print(f"The {rows} x {columns} grid back from its Fourier transform (SciPy fft.{name}).")
    return NumberGrid(np.asarray(values, dtype=float))


def closest_inverse(values):
    """take_inverse(closest_possible=True): SciPy linalg.pinvh for a symmetric grid, linalg.pinv otherwise (the
    Moore-Penrose inverse, from the SVD, as R MASS::ginv)."""
    from scipy import linalg

    from .numbers_4 import _is_symmetric

    square = values.shape[0] == values.shape[1]
    if square and _is_symmetric(values):
        return linalg.pinvh(values), "SciPy linalg.pinvh, for a symmetric grid"
    return linalg.pinv(values), "SciPy linalg.pinv"


def log_determinant(values):
    """find_determinant(as_log=True): NumPy linalg.slogdet, the sign and the log of the size of the determinant."""
    sign, logged = np.linalg.slogdet(values)
    return float(sign), float(logged)


class NumPyGridWords:
    """The NumPy and SciPy words of plan section 2.4 on a grid."""

    @friendly
    def multiply_as_matrix_by(self, other=None, from_the_left=False):
        """Multiply the grid by another as matrices: rows times columns. answer = grid.multiply_as_matrix_by(other_grid)

        Each number of the answer is a row of this grid times a column of the other, added up (NumPy matmul, R %*%);
        the grid needs as many columns as the other has rows. other= numbers (one for each column) gives numbers
        (NumPy matvec). from_the_left=True puts the other one first: other times grid (NumPy vecmat for numbers). A
        list of grids multiplies them all in turn, in the fastest order (NumPy linalg.multi_dot). Gives a new grid;
        this one stays as it is.
        """
        example = "grid.multiply_as_matrix_by(other_grid)"
        if not isinstance(from_the_left, bool):
            raise SimplydataError("from_the_left= needs True or False (no quotes).")
        mine = np.asarray(self._values)
        if isinstance(other, (list, tuple)) and other and all(hasattr(g, "_values") for g in other):
            grids = [np.asarray(g._values) for g in other]
            chain = [*grids, mine] if from_the_left else [mine, *grids]
            for a, b in zip(chain, chain[1:]):
                if a.shape[-1] != b.shape[0]:
                    raise SimplydataError(f"The grids do not fit: one has {a.shape[-1]} columns and the next "
                                          f"{b.shape[0]} rows.")
            found = np.linalg.multi_dot(chain)
            print(f"{len(chain)} grids multiplied as matrices in turn (NumPy linalg.multi_dot, in the fastest order).")
            return self._wrap(found)
        if other is None:
            raise SimplydataError(f"multiply_as_matrix_by() needs another grid or numbers.\nFor example:  {example}")
        theirs = to_array(other, "multiply_as_matrix_by()", example)
        first, second = (theirs, mine) if from_the_left else (mine, theirs)
        inner_first = first.shape[-1]
        inner_second = second.shape[0]
        if inner_first != inner_second:
            raise SimplydataError(
                f"The two do not fit as matrices: the first has {amount(inner_first, 'column')} and the second "
                f"{amount(inner_second, 'row')}; they need to be the same. "
                + ("Turn this grid round with grid.swap_rows_and_columns()." if not from_the_left else ""))
        if theirs.ndim == 1:
            found = np.vecmat(first, second) if from_the_left else np.matvec(first, second)
            how = "NumPy vecmat: numbers times grid" if from_the_left else "NumPy matvec: grid times numbers"
        else:
            found = np.matmul(first, second)
            how = "NumPy matmul, R %*%"
        shape = " x ".join(str(n) for n in found.shape)
        print(f"Multiplied as matrices ({'other x grid' if from_the_left else 'grid x other'}): the answer has "
              f"{'%s numbers' % shape if found.ndim == 1 else shape + ' rows x columns'} ({how}).")
        return self._wrap(found)

    @friendly
    def add_border(self: _Same, width=1, with_value=0) -> _Same:
        """Add a border of numbers round the grid. grid.add_border(width=2, with_value=0)

        width= rows and columns on each side (or [rows, columns]). with_value= a number, "empty", or a way to copy
        the grid's own numbers: "repeat edge", "mirror" (without the edge), "mirror with edge" or "wrap around" (the
        other side). NumPy pad (mode constant, edge, reflect, symmetric, wrap). Undo with grid.undo().
        """
        if isinstance(width, (list, tuple)) and len(width) == 2:
            row_width, column_width = width
        else:
            row_width = column_width = width
        for w in (row_width, column_width):
            if isinstance(w, bool) or not isinstance(w, _nb.Integral) or w < 0:
                raise SimplydataError("width= needs a whole number from 0 up, or [rows, columns], such as width=2.")
        pad = ((int(row_width), int(row_width)), (int(column_width), int(column_width)))
        values = np.asarray(self._values)
        if isinstance(with_value, str) and with_value in BORDERS:
            mode = BORDERS[with_value]
            if mode == "reflect" and min(values.shape) < 2 and max(row_width, column_width) > 0:
                raise SimplydataError('with_value="mirror" needs at least 2 rows and 2 columns.')
            out = np.pad(values, pad, mode=mode)
            said, how = f'"{with_value}"', f'mode="{mode}"'
        elif with_value is None or with_value == "empty":
            out = np.pad(values.astype(float), pad, mode="constant", constant_values=np.nan)
            said, how = "empty values", 'mode="constant", constant_values=np.nan'
        elif is_number(with_value):
            out = np.pad(_room_for(values, with_value), pad, mode="constant", constant_values=with_value)
            said, how = say(with_value), f'mode="constant", constant_values={say(with_value)}'
        else:
            raise choice_error("add_border", "with_value", with_value, ["a number", "empty", *BORDERS])
        print(f"A border of {amount(int(row_width), 'row')} and {amount(int(column_width), 'column')} on each side, "
              f"filled with {said}: "
              f"now {out.shape[0]} x {out.shape[1]} (NumPy pad, {how}).")
        return self._change("add border", out)

    # ------------------------------------------------------------------ parts of a grid (G8)
    @friendly
    def get_part(self, name=None, shifted_by=0, as_list=False):
        """A part of the grid: its diagonal, or a triangle of it. upper = grid.get_part("upper triangle")

        "diagonal" gives the numbers from the top left down (NumPy diagonal; R diag); shifted_by=1 the diagonal just
        above it, -1 just below. "upper triangle" gives a grid with the numbers on and above the diagonal and 0
        below (NumPy triu), "lower triangle" the other way (tril); as_list=True gives those numbers as a list instead,
        row by row (NumPy triu_indices, tril_indices). The total of the diagonal (the trace) is
        grid.get_part("diagonal").find_total(). Nothing changes.
        """
        if name not in PARTS:
            raise choice_error("get_part", "name", name, list(PARTS))
        k = _shift(shifted_by)
        if not isinstance(as_list, bool):
            raise SimplydataError("as_list= needs True or False (no quotes).")
        values = np.asarray(self._values)
        where = "the main diagonal" if k == 0 else (f"{k} above the main diagonal" if k > 0 else
                                                     f"{-k} below the main diagonal")
        if name == "diagonal":
            found = np.diagonal(values, offset=k).copy()
            print(f"The diagonal ({where}): {amount(found.size)} (NumPy diagonal, offset={k}).")
            return self._wrap(found)
        func = np.triu if name == "upper triangle" else np.tril
        side = "on and above" if name == "upper triangle" else "on and below"
        if as_list:
            found = values[part_positions(values.shape, name, k)]
            print(f"The {amount(found.size)} {side} the diagonal ({where}), row by row (NumPy "
                  f"{func.__name__}_indices).")
            return self._wrap(found.copy())
        found = func(values, k)
        print(f"The {name}: the numbers {side} the diagonal ({where}), 0 elsewhere (NumPy {func.__name__}, k={k}).")
        return self._wrap(found)

    @friendly
    def replace_part(self: _Same, name=None, with_value=NOT_GIVEN, shifted_by=0) -> _Same:
        """Replace a part of the grid: its diagonal or a triangle. grid.replace_part("diagonal", with_value=1)

        name= "diagonal", "upper triangle" or "lower triangle" (shifted_by= as in get_part). with_value= a number,
        "empty", or one number for each place (row by row). NumPy fill_diagonal for the main diagonal, and assignment
        at diag_indices, triu_indices or tril_indices otherwise. Undo with grid.undo().
        """
        if name not in PARTS:
            raise choice_error("replace_part", "name", name, list(PARTS))
        k = _shift(shifted_by)
        values = np.asarray(self._values)
        where = part_positions(values.shape, name, k)
        example = f'grid.replace_part("{name}", with_value=0)'
        value, said = _value_or_values(with_value, where[0].size, "replace_part", example)
        new = _room_for(values, value)
        if name == "diagonal" and k == 0:
            np.fill_diagonal(new, value)
            how = "NumPy fill_diagonal"
        else:
            new[where] = value
            how = {"diagonal": "NumPy assignment along the diagonal", "upper triangle": "NumPy triu_indices",
                   "lower triangle": "NumPy tril_indices"}[name]
        print(f"The {name} ({amount(where[0].size)}) replaced with {said} ({how}).")
        return self._change(f"replace {name}", new)

    # ------------------------------------------------------------------ transforms of a grid
    @friendly
    def take_fourier_transform(self, time_step=None, show="half", over="rows and columns", with_zero_in_middle=False):
        """The grid as a sum of waves across it. grid.take_fourier_transform(over="rows and columns")

        Gives back a table: row frequency, column frequency, size, phase (degrees), real part, imaginary part, one row
        for each pair. over="rows and columns" transforms both ways (SciPy fft.rfft2 for show="half", fft2 for "all";
        as R fft(z) on a matrix), over="rows" each column down its rows and over="columns" each row along its columns
        (SciPy fft.rfft or fft with axis=). time_step= the step between rows and between columns (1 when not given).
        with_zero_in_middle=True puts frequency 0 in the middle (fftshift). sdata.find_inverse_fourier_transform(table)
        turns the table back into the grid (irfft2, ifft2).
        """
        import pandas as pd
        from scipy import fft

        from ..table import Table
        from .fourier_words import FOURIER_SHOWS

        if show not in FOURIER_SHOWS:
            raise choice_error("take_fourier_transform", "show", show, list(FOURIER_SHOWS))
        if over not in FOURIER_OVER:
            raise choice_error("take_fourier_transform", "over", over, list(FOURIER_OVER))
        if not isinstance(with_zero_in_middle, bool):
            raise SimplydataError("with_zero_in_middle= needs True or False (no quotes).")
        step = 1.0 if time_step is None else time_step
        if not is_number(step) or step <= 0:
            raise SimplydataError("time_step= needs a number above 0, such as time_step=1.")
        if with_zero_in_middle and show == "half":
            show = "all"
        x = np.asarray(self._values, dtype=float)
        if np.isnan(x).any():
            raise SimplydataError("take_fourier_transform() needs a value in every cell; fill the empty ones first.")
        rows, columns = x.shape
        axes = {"rows and columns": (0, 1), "rows": (0,), "columns": (1,)}[over]
        if show == "half":
            z = fft.rfft2(x) if len(axes) == 2 else fft.rfft(x, axis=axes[0])
            name = "rfft2" if len(axes) == 2 else f"rfft(axis={axes[0]})"
        else:
            z = fft.fft2(x) if len(axes) == 2 else fft.fft(x, axis=axes[0])
            name = "fft2" if len(axes) == 2 else f"fft(axis={axes[0]})"
        half_axis = axes[-1] if show == "half" else None
        freqs = []
        for axis in (0, 1):
            n = x.shape[axis]
            if axis not in axes:
                freqs.append(None)
            elif axis == half_axis:
                freqs.append(fft.rfftfreq(n, d=step))
            else:
                freqs.append(fft.fftfreq(n, d=step))
        if with_zero_in_middle:
            z = fft.fftshift(z, axes=axes)
            freqs = [fft.fftshift(f) if f is not None else None for f in freqs]
            name += ", then fft.fftshift"
        out_rows, out_columns = z.shape
        first = freqs[0] if freqs[0] is not None else np.arange(1, out_rows + 1)
        second = freqs[1] if freqs[1] is not None else np.arange(1, out_columns + 1)
        a, b = np.meshgrid(first, second, indexing="ij")
        names = ("row frequency" if freqs[0] is not None else "row",
                 "column frequency" if freqs[1] is not None else "column")
        frame = pd.DataFrame({names[0]: a.ravel(), names[1]: b.ravel(), "size": np.abs(z).ravel(),
                              "phase": np.degrees(np.angle(z)).ravel(), "real part": z.real.ravel(),
                              "imaginary part": z.imag.ravel()})
        print(f"Fourier transform of the {rows} x {columns} grid over {over}: {out_rows} x {out_columns} pairs "
              f"(SciPy fft.{name}).")
        table = Table(frame)
        table._fourier = {"grid": (rows, columns), "over": over, "show": show, "time_step": step,
                          "frequency": frame[list(names)].to_numpy().copy(), "names": names,
                          "zero_in_middle": with_zero_in_middle, "shape": z.shape, "n": rows * columns}
        return table

    @friendly
    def take_cosine_transform(self: _Same, kind="cosine", inverse=False) -> _Same:
        """The grid as a sum of cosine waves both ways (the discrete cosine transform). grid.take_cosine_transform()

        The type-2 transform over rows and columns with orthonormal scaling (SciPy fft.dctn, type 2, norm="ortho");
        kind="sine" the sine transform (dstn); inverse=True turns a transformed grid back (idctn, idstn). Undo with
        grid.undo().
        """
        from scipy import fft

        if kind not in ("cosine", "sine"):
            raise choice_error("take_cosine_transform", "kind", kind, ["cosine", "sine"])
        if not isinstance(inverse, bool):
            raise SimplydataError("inverse= needs True or False (no quotes).")
        x = np.asarray(self._values, dtype=float)
        if np.isnan(x).any():
            raise SimplydataError("take_cosine_transform() needs a value in every cell; fill the empty ones first.")
        func = {("cosine", False): fft.dctn, ("sine", False): fft.dstn, ("cosine", True): fft.idctn,
                ("sine", True): fft.idstn}[(kind, inverse)]
        out = func(x, type=2, norm="ortho")
        print(f"The {'inverse ' if inverse else ''}{kind} transform of the {x.shape[0]} x {x.shape[1]} grid over rows "
              f"and columns (SciPy fft.{func.__name__}, type 2, orthonormal).")
        return self._change(f"{'inverse ' if inverse else ''}{kind} transform", out)

    # ------------------------------------------------------------------ the size of a grid as a matrix
    def _no_empty_cells(self, step: str):
        values = np.asarray(self._values, dtype=float)
        if np.isnan(values).any():
            raise SimplydataError(f"{step}() needs no empty values; fill or remove them first.")
        return values

    @friendly
    def find_rank(self):
        """The rank of the grid: how many of its rows (or columns) are not made from the others. rank = grid.find_rank()

        From the singular values, counting those above a small tolerance (NumPy linalg.matrix_rank, as R
        qr(x)$rank and MATLAB rank). A square grid has an inverse only when its rank is its size. Nothing changes.
        """
        values = self._no_empty_cells("find_rank")
        found = int(np.linalg.matrix_rank(values))
        rows, columns = values.shape
        print(f"The rank of the {rows} x {columns} grid: {found}"
              + (" (full rank)" if found == min(rows, columns) else f" (less than {min(rows, columns)}: some rows or "
                 "columns are made from the others)") + "   (NumPy linalg.matrix_rank, from the SVD)")
        return found

    @friendly
    def find_condition_number(self, kind="biggest stretch"):
        """How much the grid can blow up small errors. condition = grid.find_condition_number()

        The biggest stretch divided by the smallest (the ratio of the singular values; NumPy linalg.cond, as R
        kappa(x, exact = TRUE)). Near 1 is safe; 1e10 or more means answers from solve_for may lose most digits.
        kind="frobenius", "biggest column total", "biggest row total" or "nuclear" use those sizes of the grid and
        its inverse instead. Nothing changes.
        """
        if kind not in CONDITION_KINDS:
            raise choice_error("find_condition_number", "kind", kind, list(CONDITION_KINDS))
        values = self._no_empty_cells("find_condition_number")
        with np.errstate(all="ignore"):
            found = float(np.linalg.cond(values, p=CONDITION_KINDS[kind]))
        print(f"The condition number of the grid ({kind}): {found:.6g}   (NumPy linalg.cond"
              + (f", p={CONDITION_KINDS[kind]!r})" if CONDITION_KINDS[kind] is not None else ")")
              + (". It is very big: solving with this grid can lose most digits." if found > 1e10 else ""))
        return found

    @friendly
    def find_column_space(self):
        """The directions the grid's columns reach, at right angles. directions = grid.find_column_space()

        An orthonormal basis of the column space, from the SVD (SciPy linalg.orth, as R pracma::orth and MATLAB orth);
        it has as many columns as the grid's rank. grid.find_null_space() gives the directions it sends to 0. Gives a
        new grid; this one stays as it is.
        """
        from scipy import linalg

        values = self._no_empty_cells("find_column_space")
        found = linalg.orth(values)
        print(f"The column space of the grid: {amount(found.shape[1], 'direction')} of length 1 at right angles "
              "(SciPy linalg.orth, from the SVD).")
        return self._wrap(found)
