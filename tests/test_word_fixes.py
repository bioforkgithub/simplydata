"""get_example gives a simplydata table, and nine fixes found while writing the Underneath entries (PR word-fixes,
2026-11-22), each checked against its parent package or R.

The simplydata side uses simplydata words only; the reference side calls pandas, Polars, SciPy, statsmodels or R
directly. Each test says what simplydata gave before the fix.
"""

import re
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from conftest import example_frame

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.data import EXAMPLES

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- get_example gives a simplydata table
@pytest.mark.parametrize("name", list(EXAMPLES))
def test_get_example_gives_a_simplydata_table_with_the_file_in_it(name):
    # before (0.2.x): a pandas DataFrame. The reference: the same file read by pandas itself
    table = sdata.get_example(name)
    assert type(table).__name__ == "Table"
    reference = example_frame(name)
    assert table.get_column_names() == list(reference.columns)
    assert len(table) == len(reference)
    for column in reference.columns:
        got = table.get_column(column)
        want = reference[column]
        if pd.api.types.is_numeric_dtype(want) and not pd.api.types.is_bool_dtype(want):
            assert np.allclose(got.as_numpy(), want.to_numpy(dtype=float), equal_nan=True), (name, column)
        else:
            assert [None if pd.isna(v) else str(v)[:10] for v in got] == \
                   [None if pd.isna(v) else str(v)[:10] for v in want], (name, column)


def test_get_example_works_with_table_words_and_as_before_inside_sdata_table(capsys):
    marks = sdata.get_example("marks")
    assert marks.count_rows() == 54
    again = sdata.table(sdata.get_example("marks"))  # 0.2.x code keeps working
    assert again.get_column_names() == marks.get_column_names()
    fast = sdata.table(sdata.get_example("marks"), fast=True)
    assert fast.get_cell_at(row=3, column="marks") == marks.get_cell_at(row=3, column="marks")
    capsys.readouterr()


def test_get_example_with_no_name_still_lists_the_tables(capsys):
    assert sdata.get_example() is None
    out = capsys.readouterr().out
    assert 'sdata.get_example("marks")' in out and "table.count_rows()" in out


# ---------------------------------------------------------------- 1. join_with keeps the pandas row order on Polars
LEFT = {"k": ["c", "a", "b", "a", "z"], "x": [1, 2, 3, 4, 5]}
RIGHT = {"k": ["b", "a", "q", "a", "c"], "y": [10, 20, 30, 40, 50]}
KEEPS = {"matching rows": "inner", "all rows from this table": "left", "all rows from both": "outer"}


@pytest.mark.parametrize("keep", list(KEEPS))
def test_join_with_on_polars_gives_the_rows_in_pandas_merge_order(keep, capsys):
    # before: Polars joined without maintain_order: "matching rows" came back b, a, a, a, a, c and "all rows from both"
    # b, a, a, q, a, a, c, z (pandas merge: c, a, a, b, a, a and a, a, a, a, b, c, q, z)
    pytest.importorskip("polars")
    merged = pd.merge(pd.DataFrame(LEFT), pd.DataFrame(RIGHT), on="k", how=KEEPS[keep])
    for fast in (False, True):
        table = sdata.table(LEFT, fast=fast)
        table.join_with(sdata.table(RIGHT, fast=fast), using="k", keep=keep)
        assert table.get_column("k") == merged["k"].tolist(), (keep, fast)
        assert np.allclose(table.get_column("x").as_numpy(), merged["x"].to_numpy(dtype=float), equal_nan=True)
        assert np.allclose(table.get_column("y").as_numpy(), merged["y"].to_numpy(dtype=float), equal_nan=True)
    capsys.readouterr()


def test_join_with_on_polars_matches_polars_with_maintain_order(capsys):
    pl = pytest.importorskip("polars")
    reference = pl.DataFrame(LEFT).join(pl.DataFrame(RIGHT), on="k", how="inner", maintain_order="left_right")
    table = sdata.table(LEFT, fast=True)
    table.join_with(RIGHT, using="k")
    assert table.get_column("k") == reference["k"].to_list()
    assert table.get_column("y").as_numpy().tolist() == reference["y"].cast(pl.Float64).to_list()
    capsys.readouterr()


# ---------------------------------------------------------------- 2. describe_columns rounds before it looks for 62
@pytest.mark.parametrize("value, shown", [(62.001, "62"), (61.996, "62"), (61.5, "61.5"), (1.006, "1.01"),
                                          (-0.001, "0")])
def test_describe_columns_writes_a_rounded_whole_number_without_point_zero(value, shown, capsys):
    # before: 62.001 was written "62.0" (the whole-number check came before the rounding)
    reference = round(value, 2)  # Python's round, which the printout uses for 2 places
    assert (str(int(reference)) if reference.is_integer() else str(reference)) == shown
    table = sdata.table({"v": [value, value]})
    table.describe_columns()
    row = [line for line in capsys.readouterr().out.splitlines() if line.strip().startswith("v ")][0]
    assert row.split()[3:6] == [shown, shown, shown]


# ---------------------------------------------------------------- 3. sdata.compare_rates says which group is first
def test_sdata_compare_rates_says_the_first_given_is_the_reference(capsys):
    # before: 'compared against "ward B" (the first in sorted order, as R)', although "ward A" comes first sorted
    from statsmodels.stats.rates import test_poisson_2indep

    result = sdata.compare_rates(events=[30, 15], time=[1100, 1200], names=["ward B", "ward A"])
    out = capsys.readouterr().out
    assert ('Note: compared against "ward B" (the first given, as R takes counts in the order they are given); '
            "choose another with against=.") in out
    assert "sorted order" not in out
    ratio = sdata.table(result).keep_rows_where("measure", is_equal_to="rate ratio")
    # R poisson.test(c(15, 30), c(1200, 1100)): the group, then the reference (ward B), in the order given
    reference = test_poisson_2indep(15, 1200, 30, 1100, method="exact-cond")
    assert ratio.get_cell_at(row=1, column="estimate") == pytest.approx(float(reference.ratio), rel=1e-12)
    assert ratio.get_cell_at(row=1, column="group") == "ward A"


def test_sdata_compare_risks_says_the_first_given_too(capsys):
    sdata.compare_risks(events=[12, 30], out_of=[100, 100], names=["new", "old"])
    out = capsys.readouterr().out
    assert 'compared against "new" (the first given' in out


def test_table_compare_rates_still_says_sorted_order(capsys):
    table = sdata.table({"ward": ["ward B", "ward A"], "events": [30, 15], "days": [1100, 1200]})
    table.compare_rates("events", time="days", for_each_group_in="ward")
    assert 'compared against "ward A" (the first in sorted order, as R)' in capsys.readouterr().out


def test_sdata_compare_rates_order_matches_r_poisson_test(needs_r, capsys):
    from simplydata._r import r_call

    result = sdata.compare_rates(events=[30, 15], time=[1100, 1200], names=["ward B", "ward A"])
    ratio = sdata.table(result).keep_rows_where("measure", is_equal_to="rate ratio")
    r = r_call("unname(poisson.test(c(15, 30), c(1200, 1100))$estimate)")
    assert ratio.get_cell_at(row=1, column="estimate") == pytest.approx(float(np.asarray(r)[0]), rel=1e-10)
    capsys.readouterr()


# ---------------------------------------------------------------- 4. find_middle_range keeps its digits near 100 %
@pytest.mark.parametrize("percent", [95, 99.99999999, 99.9999999999])
def test_find_middle_range_is_scipy_ppf_and_isf_of_the_tail(percent, capsys):
    # before, at 99.99999999 %: low -6.466951242568076, high 6.466951074732418 (1 - (1 - tail) lost digits);
    # SciPy norm.ppf / norm.isf of the tail: -6.466951182147218 and 6.466951182147218
    from scipy import stats

    tail = (100 - percent) / 200
    middle = sdata.distribution("normal", average=0, standard_deviation=1).find_middle_range(percent)
    assert middle.get_number_at(1) == stats.norm.ppf(tail)
    assert middle.get_number_at(2) == stats.norm.isf(tail)
    out = capsys.readouterr().out
    assert "lower.tail = FALSE" in out


def test_find_middle_range_of_counts_is_scipy_ppf_and_isf(capsys):
    from scipy import stats

    middle = sdata.distribution("binomial", size=20, chance=0.3).find_middle_range(95)
    assert middle.as_numpy().tolist() == [stats.binom.ppf(0.025, 20, 0.3), stats.binom.isf(0.025, 20, 0.3)]
    capsys.readouterr()


def test_find_middle_range_matches_r_near_100_percent(needs_r, capsys):
    from simplydata._r import r_call

    middle = sdata.distribution("normal", average=50, standard_deviation=10).find_middle_range(99.99999999)
    tail = (100 - 99.99999999) / 200
    r = np.asarray(r_call("c(qnorm(p, 50, 10), qnorm(p, 50, 10, lower.tail = FALSE))", p=np.asarray([tail])))
    assert middle.as_numpy() == pytest.approx(r, rel=1e-14)
    capsys.readouterr()


# ---------------------------------------------------------------- 5. and_multiples=True leaves the average alone
def _hum(n=20000, step=0.001):
    t = np.arange(n) * step
    slow = 5 + np.sin(2 * np.pi * 3 * t)
    return slow, slow + 0.8 * np.sin(2 * np.pi * 50 * t) + 0.4 * np.sin(2 * np.pi * 100 * t)


def test_and_multiples_is_scipy_iirnotch_at_each_multiple_and_keeps_the_average(capsys):
    # before: SciPy iircomb (pass_zero=False) also notched frequency 0: the average 5 became 0.0119
    from scipy import signal

    slow, x = _hum()
    nums = sdata.numbers(x)
    nums.remove_each_frequency_that(is_equal_to=50, time_step=0.001, and_multiples=True)
    out = capsys.readouterr().out
    assert "9 notch filters at 50, 100 ... 450 (width 1 each); the average (frequency 0) stays" in out
    assert "the multiple at 500, half the readings per unit of time, cannot have a notch" in out
    sos = np.vstack([np.concatenate(signal.iirnotch(m, m / 1.0, fs=1000)) for m in range(50, 500, 50)])
    reference = signal.sosfiltfilt(sos, x)
    assert np.allclose(nums.as_numpy(), reference, rtol=0, atol=1e-12)
    assert nums.find_average() == pytest.approx(5, abs=1e-3)
    assert np.abs(nums.as_numpy() - slow)[3000:-3000].max() < 1e-3
    capsys.readouterr()


def test_scipy_iircomb_notches_frequency_0_which_is_why_it_is_not_used():
    # SciPy's documentation: pass_zero=False puts the notches at 0, w0, 2 w0 ...; True moves them to w0 / 2, 3 w0 / 2
    from scipy import signal

    b, a = signal.iircomb(50, 50, ftype="notch", fs=1000)
    _, gain = signal.freqz(b, a, worN=[0.0, 25.0], fs=1000)
    assert abs(gain[0]) < 1e-9  # the average is removed
    b, a = signal.iircomb(50, 50, ftype="notch", fs=1000, pass_zero=True)
    _, gain = signal.freqz(b, a, worN=[25.0, 50.0], fs=1000)
    assert abs(gain[0]) < 1e-9 and abs(gain[1]) > 0.99  # notches at 25, not at 50


def test_frequency_filter_with_and_multiples_passes_frequency_0(capsys):
    from scipy import signal

    system = sdata.frequency_filter(remove_at=50, time_step=0.001, and_multiples=True)
    sos = np.vstack([np.concatenate(signal.iirnotch(m, m / 1.0, fs=1000)) for m in range(50, 500, 50)])
    _, reference = signal.sosfreqz(sos, worN=[0.0, 50.0, 100.0], fs=1000)
    assert abs(reference[0]) == pytest.approx(1, abs=1e-12)
    assert "the average (frequency 0) stays" in capsys.readouterr().out
    assert system is not None


# ---------------------------------------------------------------- 6. the spectrum chart labels the sentence's cycles
def _leaky_table():
    t = np.arange(200) * 0.01
    return sdata.table({"time": t, "signal": 3 * np.sin(2 * np.pi * 5.25 * t) + np.sin(2 * np.pi * 20 * t)})


def test_spectrum_chart_labels_the_cycles_the_sentence_names(capsys):
    # before: the chart labelled the 3 biggest bins, "repeats every" 0.2, 0.182 and 0.05 (5 and 5.5 are one broad
    # peak), while the sentence named the local peaks 5 and 20 only; now the chart labels 0.2 and 0.05
    import matplotlib.pyplot as plt
    from scipy import signal

    table = _leaky_table()
    table.find_spectrum_of("signal", sorted_by="time")
    sentence = [line for line in capsys.readouterr().out.splitlines() if "strongest cycle" in line][0]
    chart = sdata.chart(table).spectrum("signal", sorted_by="time")
    drawn = chart.get_numbers_drawn()
    capsys.readouterr()
    labels = [text.get_text() for text in chart._render().axes[0].texts]
    periods = [float(text.split()[-1]) for text in labels]
    # the reference: SciPy periodogram, its local peaks (find_peaks, the ends counting) strongest first
    freq, power = signal.periodogram(table.get_column("signal").as_numpy(), fs=100, detrend="constant",
                                     window="boxcar", scaling="density")
    f, p = freq[freq > 0], power[freq > 0]
    tops = signal.find_peaks(np.concatenate([[-np.inf], p, [-np.inf]]))[0] - 1
    tops = tops[np.argsort(-p[tops], kind="stable")][:3]
    assert periods == pytest.approx([float(f"{1 / f[i]:.3g}") for i in tops])
    assert periods == [0.2, 0.05]
    named = [float(v) for v in re.findall(r"([\d.]+) per unit", sentence)]
    assert [float(f"{1 / v:.3g}") for v in named] == pytest.approx(periods)
    assert len(drawn) > 0
    plt.close("all")


# ---------------------------------------------------------------- 7. chart.show() closes the figure it opened
def test_chart_show_leaves_no_pyplot_figure_open(capsys):
    # before: each chart.show() left one pyplot figure open (3 after 3 calls)
    import matplotlib.pyplot as plt

    plt.close("all")
    chart = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    for _ in range(3):
        chart.show()
    assert plt.get_fignums() == []
    chart.save(str(Path(plt.matplotlib.get_cachedir()) / "word_fixes_show.png"))  # still draws after show()
    capsys.readouterr()


def test_chart_show_keeps_a_window_that_stays_open_in_interactive_mode(monkeypatch, capsys):
    # a notebook with %matplotlib widget, or IPython with a window: the window belongs to the user
    import matplotlib.pyplot as plt

    plt.close("all")
    monkeypatch.setattr(plt, "isinteractive", lambda: True)
    monkeypatch.setattr(plt, "get_backend", lambda: "module://ipympl.backend_nbagg")
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)
    sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks").show()
    assert len(plt.get_fignums()) == 1
    plt.close("all")
    capsys.readouterr()


# ---------------------------------------------------------------- 8. round_numbers_in: halves to even on Polars
def test_pyproject_asks_for_the_polars_that_rounds_halves_to_even():
    # Polars rounds a float halfway to the even neighbour from 1.29 (RoundMode, pola-rs/polars#22248); 1.28.1 gave
    # 2.5 -> 3, 0.125 -> 0.13 and 2.675 -> 2.68. maintain_order= of join (item 1) is there from 1.17
    # Polars is required since the tables phase (2026-11-25): it is in dependencies, and [fast] is kept empty
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    polars = [d for d in project["dependencies"] if d.startswith("polars")]
    # the lower bound is 1.29 or newer (the oldest-versions check sets it); the upper bound is the supported
    # range (MAINTAINING.md)
    assert len(polars) == 1 and polars[0].startswith("polars>=")
    lower = tuple(int(n) for n in polars[0].split(",")[0][len("polars>="):].split(".")[:2])
    assert lower >= (1, 29)
    assert project["optional-dependencies"]["fast"] == []  # pip install "simplydata[fast]" still works
    assert any(d.startswith("pyarrow>=") for d in project["dependencies"])


@pytest.mark.parametrize("places", [0, 1, 2])
def test_round_numbers_in_halves_to_even_on_pandas_and_polars_as_numpy(places, capsys):
    pytest.importorskip("polars")
    values = [0.5, 1.5, 2.5, -0.5, -2.5, 3.5, 0.125, 0.375, 2.675, 1.005, 12345.5]
    reference = np.round(values, places)
    for fast in (False, True):
        table = sdata.table({"v": values}, fast=fast)
        table.round_numbers_in("v", places)
        assert table.get_column("v").as_numpy().tolist() == reference.tolist(), fast
    capsys.readouterr()


def test_round_numbers_in_refuses_a_polars_that_rounds_halves_away_from_zero(monkeypatch, capsys):
    pl = pytest.importorskip("polars")
    monkeypatch.setattr(pl, "__version__", "1.28.1")
    table = sdata.table({"v": [2.5]}, fast=True)
    with pytest.raises(SimplydataError, match=r"needs Polars 1\.29 or newer.*Polars 1\.28\.1"):
        table.round_numbers_in("v", 0)
    sdata.table({"v": [2.5]}).round_numbers_in("v", 0)  # a pandas table needs no Polars
    capsys.readouterr()


# ---------------------------------------------------------------- 9. the inverse Fourier transform checks its rows
def _transform():
    nums = sdata.numbers(np.sin(2 * np.pi * 5 * np.arange(100) * 0.01) + 0.3 * np.sin(2 * np.pi * 30 * np.arange(100)
                                                                                         * 0.01))
    return nums, nums.take_fourier_transform(time_step=0.01)


def test_inverse_fourier_refuses_rows_that_changed(capsys):
    # before: with the row of frequency 50 removed it gave back 100 numbers without a word (SciPy irfft padded the
    # 50 rows with a zero)
    _, table = _transform()
    table.keep_rows_where("frequency", is_below=50)
    with pytest.raises(SimplydataError, match="it had 51 rows and now has 50"):
        sdata.find_inverse_fourier_transform(table)
    table.undo()
    table.sort_by("size", biggest_first=True)
    with pytest.raises(SimplydataError, match="no longer the ones it made"):
        sdata.find_inverse_fourier_transform(table)
    table.undo()
    back = sdata.find_inverse_fourier_transform(table)
    assert back.count() == 100
    capsys.readouterr()


def test_inverse_fourier_with_some_frequencies_set_to_0_is_scipy_irfft(capsys):
    from scipy import fft

    nums, table = _transform()
    for part in ("real part", "imaginary part"):
        table.change_column(part, by_running=lambda row, part=part: 0.0 if row["frequency"] > 20 else row[part])
    back = sdata.find_inverse_fourier_transform(table)
    z = fft.rfft(nums.as_numpy())
    z[fft.rfftfreq(100, d=0.01) > 20] = 0
    assert np.allclose(back.as_numpy(), fft.irfft(z, n=100), rtol=0, atol=1e-12)
    assert np.allclose(back.as_numpy(), np.sin(2 * np.pi * 5 * np.arange(100) * 0.01), atol=1e-9)
    capsys.readouterr()


# ---------------------------------------------------------------- A25: Dunn's test, Holm from R p.adjust
def test_a25_dunn_holm_has_the_running_maximum_as_r(needs_r, capsys):
    # before (FSA::dunnTest(method = "holm")): B - F 0.926028; Holm's steps (R p.adjust, PMCMRplus) give 1
    from simplydata._r import r_call

    sprays = sdata.get_example("InsectSprays", from_r_package="datasets")
    result = sprays.compare_each_pair_of("count", for_each_group_in="spray", test_method="dunn")
    found = r_call('m <- PMCMRplus::kwAllPairsDunnTest(InsectSprays$count, InsectSprays$spray, '
                   'p.adjust.method = "holm")$p.value; list(p = m[lower.tri(m, diag = TRUE)], '
                   'row = rep(rownames(m), ncol(m))[lower.tri(m, diag = TRUE)], '
                   'col = rep(colnames(m), each = nrow(m))[lower.tri(m, diag = TRUE)])',
                   packages=("PMCMRplus",))
    reference = {}
    for p, a, b in zip(np.asarray(found["p"], dtype=float), found["row"], found["col"]):
        reference[(str(a), str(b))] = reference[(str(b), str(a))] = p
    table = sdata.table(result)
    assert len(table) == 15
    for row in range(1, 16):
        pair = (table.get_cell_at(row=row, column="group 1"), table.get_cell_at(row=row, column="group 2"))
        assert table.get_cell_at(row=row, column="p-value (adjusted)") == pytest.approx(reference[pair], rel=1e-9), pair
    bf = sdata.table(result).keep_rows_where("group 1", is_equal_to="B").keep_rows_where("group 2", is_equal_to="F")
    assert bf.get_cell_at(row=1, column="p-value (adjusted)") == 1.0
    capsys.readouterr()


# ---------------------------------------------------------------- A26: trust region and dogbox go on to the minimum
NIST = ROOT / "validation" / "data" / "nist"
NIST_FORMULAS = {
    "Thurber": "y = (b1 + b2*x + b3*x**2 + b4*x**3) / (1 + b5*x + b6*x**2 + b7*x**3)",
    "MGH09": "y = b1*(x**2+x*b2) / (x**2+x*b3+b4)",
    "ENSO": "y = b1 + b2*cos(2*pi*x/12) + b3*sin(2*pi*x/12) + b5*cos(2*pi*x/b4) + b6*sin(2*pi*x/b4)"
            " + b8*cos(2*pi*x/b7) + b9*sin(2*pi*x/b7)",
}


def _nist(name):
    """The data, the starting values and the certified values (estimate, standard error) of a NIST StRD file."""
    lines = (NIST / f"{name}.dat").read_text(encoding="ascii").splitlines()
    starts, certified = {}, {}
    for line in lines:
        m = re.match(r"\s+(b\d+)\s+=\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$", line)
        if m:
            starts[m.group(1)] = float(m.group(3))  # start 2
            certified[m.group(1)] = (float(m.group(4)), float(m.group(5)))
    first = max(i for i, line in enumerate(lines) if line.startswith("Data:")) + 1
    rows = [line.split() for line in lines[first:] if line.strip()]
    data = sdata.table({"y": [float(r[0]) for r in rows], "x": [float(r[1]) for r in rows]})
    return data, starts, certified


def _digits(found, certified):
    return 15.0 if found == certified else -np.log10(abs(found - certified) / abs(certified))


@pytest.mark.parametrize("method", ["trust region", "dogbox"])
@pytest.mark.parametrize("name", list(NIST_FORMULAS))
def test_a26_trust_region_and_dogbox_reach_6_digits_on_thurber_mgh09_and_enso(name, method, capsys):
    # From NIST start 2, with xtol = ftol = gtol = 1e-12 (PR #39): Thurber standard errors 5.77 to 5.85 digits
    # (b2 39.5712219 against the certified 39.5711561), MGH09 b2 and b4 5.79 to 5.99, ENSO b6 5.94. With 1e-15 the
    # lowest are Thurber 6.73, MGH09 7.22 and ENSO 6.50, and Misra1a, Kirby2 and Hahn1 keep PR #39's digits
    data, starts, certified = _nist(name)
    result = data.fit_formula(NIST_FORMULAS[name], start=starts, test_method=method)
    for b, (estimate, error) in certified.items():
        assert _digits(result.get_cell_at(row=1, column=b), estimate) >= 6, b
        assert _digits(result.get_cell_at(row=1, column=f"standard error of {b}"), error) >= 6, b
    capsys.readouterr()


# ---------------------------------------------------------------- item 10, fixed on request
@pytest.mark.parametrize("places", [-1, -2])
def test_round_numbers_in_to_tens_is_pandas_round_on_both_engines(places, capsys):
    # before: simplydata divided, rounded and multiplied itself; now pandas round(-k) (Polars has no negative
    # places: round() refuses them, so a Polars table gets NumPy's round, the one pandas uses)
    pytest.importorskip("polars")
    values = [15.0, 25.0, -35.0, 1234.5, 149.9, 250.0]
    counts = [15, 25, -35, 149, 250, 1250]
    reference = pd.DataFrame({"v": values, "n": counts}).round(places)
    for fast in (False, True):
        table = sdata.table({"v": values, "n": counts}, fast=fast)
        table.round_numbers_in(["v", "n"], places)
        assert table.get_column("v").as_numpy().tolist() == reference["v"].tolist(), fast
        assert table.get_column("n").as_numpy().tolist() == reference["n"].tolist(), fast
    capsys.readouterr()


def test_find_middle_range_prints_the_percent_as_given(capsys):
    # before: "The middle 100 % of the distribution ..." for 99.99999999
    sdata.distribution("normal", average=0, standard_deviation=1).find_middle_range(99.99999999)
    assert "The middle 99.99999999 % of the distribution" in capsys.readouterr().out
    sdata.distribution("normal", average=0, standard_deviation=1).find_middle_range(95)
    assert "The middle 95 % of the distribution" in capsys.readouterr().out


def test_spectrum_gives_no_share_of_variance_and_its_power_is_scipy(capsys):
    # the share (power x step / variance) was simplydata's own arithmetic: dropped; the power is SciPy's
    from scipy import signal

    table = _leaky_table()
    result = table.find_spectrum_of("signal", sorted_by="time")
    out = capsys.readouterr().out
    assert "% of the variance" not in out
    assert "share of variance (%)" not in result.get_column_names()
    freq, power = signal.periodogram(table.get_column("signal").as_numpy(), fs=100, detrend="constant",
                                     window="boxcar", scaling="density")
    assert np.allclose(result.get_column("power").as_numpy(), power, rtol=1e-12, atol=1e-20)  # frequency 0: rounding


def test_notch_method_line_names_what_scipy_runs(capsys):
    # before: "Method: SciPy, as R signal::filtfilt(SciPy signal.iirnotch, x) ..."
    nums = sdata.numbers(_hum(2000)[1])
    nums.remove_each_frequency_that(is_equal_to=50, time_step=0.001)
    out = capsys.readouterr().out
    assert "Method: SciPy signal.iirnotch, run with SciPy signal.filtfilt (forwards and backwards" in out
    assert "as R SciPy" not in out
    nums.remove_each_frequency_that(is_equal_to=50, time_step=0.001, and_multiples=True, both_ways=False)
    out = capsys.readouterr().out
    assert "Method: SciPy signal.iirnotch at each multiple, run with SciPy signal.sosfilt (forwards only" in out
    sdata.frequency_filter(remove_at=50, time_step=0.001)
    assert "Method: SciPy signal.iirnotch." in capsys.readouterr().out
