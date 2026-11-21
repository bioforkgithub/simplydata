"""S1 Part B: compare_each_pair follow-up tests and add_adjusted_p_value_column(test_method=) choices.

Reference values: R 4.6.2 on sdata.get_example("marks") (m <- read.csv(".../marks.csv"); m$class <- factor(m$class)).
Pairs in R's order: A vs B, A vs C, B vs C (difference = first group minus second).
"""

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def frame(result):
    return result._frame.to_pandas()


@pytest.fixture
def marks(engine):
    return make(sdata.get_example("marks"), engine)


def test_games_howell(marks, capsys, needs_r):
    got = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", test_method="games-howell"))
    # R: rstatix::games_howell_test(m, marks ~ class) (estimate is group2 - group1; here group 1 - group 2)
    assert got["difference"].tolist() == pytest.approx([7.55555555556, 13.2222222222, 5.66666666667], rel=1e-9)
    assert got["difference 95 % CI low"].tolist() == pytest.approx([-4.13938313571, 1.81661028685, -6.19930464960],
                                                                   rel=1e-9)
    assert got["p-value (adjusted)"].tolist() == pytest.approx([0.2664795597222, 0.0201247160814, 0.4786719163634],
                                                               rel=1e-8)
    assert "rstatix::games_howell_test()" in capsys.readouterr().out


def test_scheffe_and_lsd(marks, capsys, needs_r):
    got = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", test_method="scheffe"))
    # R: DescTools::ScheffeTest(aov(marks ~ class, m)) (B-A, C-A, C-B: signs turned round)
    assert got["difference 95 % CI low"].tolist() == pytest.approx([-4.43752306719, 1.22914359947, -6.32641195608],
                                                                   rel=1e-9)
    assert got["p-value (adjusted)"][1] == pytest.approx(0.0274, abs=5e-5)
    got = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", test_method="lsd"))
    # R: DescTools::PostHocTest(aov(marks ~ class, m), method = "lsd")
    assert got["difference 95 % CI high"].tolist() == pytest.approx([17.1045536186, 22.7712202853, 15.2156647297],
                                                                    rel=1e-9)
    assert got["p-value"][1] == pytest.approx(0.0076, abs=5e-5)
    assert "NOT adjusted" in capsys.readouterr().out


def test_dunn(marks, needs_r):
    got = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", based_on="ranks", test_method="dunn"))
    # R: FSA::dunnTest(marks ~ class, data = m, method = "holm")$res
    assert got["statistic"].tolist() == pytest.approx([1.57426373194, 2.73508446358, 1.16082073163], rel=1e-9)
    assert got["p-value (adjusted)"].tolist() == pytest.approx([0.2308529815114, 0.0187092813904, 0.2457148101991],
                                                               rel=1e-9)


def test_conover(marks, needs_r):
    got = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", test_method="conover"))
    # R: PMCMRplus::kwAllPairsConoverTest(marks ~ class, data = m, p.adjust.method = "holm")$p.value
    assert got["p-value (adjusted)"].tolist() == pytest.approx([0.2031345282618, 0.0166203565546, 0.224530961538],
                                                               rel=1e-9)


def test_dunnett(marks, capsys):
    got = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", against="A"))
    # R: summary(multcomp::glht(aov(marks ~ class, m), linfct = mcp(class = "Dunnett"))): p 0.2046252632603,
    # 0.0144035051254; confint: B - A -18.3764072289 to 3.26529611778, C - A -24.0430738956 to -2.40137054889.
    # Both SciPy and multcomp integrate with random numbers: tolerance 1e-3.
    assert got["group 1"].tolist() == ["B", "C"] and got["group 2"].tolist() == ["A", "A"]
    assert got["difference"].tolist() == pytest.approx([-7.55555555556, -13.2222222222], rel=1e-9)
    assert got["p-value (adjusted)"].tolist() == pytest.approx([0.2046252632603, 0.0144035051254], abs=1e-3)
    assert got["difference 95 % CI low"].tolist() == pytest.approx([-18.3764072289, -24.0430738956], abs=2e-3)
    assert got["difference 95 % CI high"].tolist() == pytest.approx([3.26529611778, -2.40137054889], abs=2e-3)
    again = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", against="A"))
    assert again["p-value (adjusted)"].tolist() == got["p-value (adjusted)"].tolist()  # seed 1: the same every time
    assert "seed 1" in capsys.readouterr().out


def test_pair_errors(marks):
    with pytest.raises(SimplydataError, match="for ranks use"):
        marks.compare_each_pair_of("marks", for_each_group_in="class", based_on="ranks", test_method="games-howell")
    with pytest.raises(SimplydataError, match='does not know against="a"'):
        marks.compare_each_pair_of("marks", for_each_group_in="class", against="a")
    with pytest.raises(SimplydataError, match="leave out test_method="):
        marks.compare_each_pair_of("marks", for_each_group_in="class", test_method="tukey", against="A")


@pytest.mark.parametrize("method, want", [
    # R: p.adjust(c(0.01, 0.04, 0.03, 0.2), "hochberg") and "hommel"
    ("hochberg", [0.04, 0.08, 0.08, 0.20]),
    ("hommel", [0.04, 0.08, 0.06, 0.20]),
])
def test_hochberg_hommel(engine, method, want):
    t = make(pd.DataFrame({"p": [0.01, 0.04, 0.03, 0.2]}), engine)
    t.add_adjusted_p_value_column("q", from_column="p", test_method=method)
    assert t._frame.to_pandas()["q"].tolist() == pytest.approx(want, rel=1e-12)


# ---------------------------------------------------------------------------- show="letters"
def test_letters_marks(marks, capsys, needs_r):
    got = frame(marks.compare_each_pair_of("marks", for_each_group_in="class", show="letters"))
    # R: r <- pairwise.t.test(m$marks, m$class, pool.sd = FALSE, p.adjust.method = "holm");
    #    multcompView::multcompLetters(<symmetric matrix of r$p.value>, threshold = 0.05)$Letters: a ab b
    assert got["letters"].tolist() == ["a", "ab", "b"]
    assert got["average of marks"].tolist() == pytest.approx([71.8333333333, 64.2777777778, 58.6111111111], rel=1e-9)
    assert "Letters: A a, B ab and C b" in capsys.readouterr().out
    # R: TukeyHSD(aov(marks ~ class, m)) p adj 0.2598, 0.0204, 0.4637 -> a ab b
    assert frame(marks.compare_each_pair_of("marks", for_each_group_in="class", test_method="tukey", show="letters"))[
        "letters"].tolist() == ["a", "ab", "b"]


def test_letters_four_groups(engine, needs_r):
    data = pd.DataFrame({"y": [10, 11, 12, 13, 14, 11, 12, 13, 14, 15, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24.5],
                         "g": ["w"] * 5 + ["x"] * 5 + ["y"] * 5 + ["z"] * 5})
    got = frame(make(data, engine).compare_each_pair_of("y", for_each_group_in="g", show="letters"))
    # R: pairwise.t.test(y, g, pool.sd = FALSE, p.adjust.method = "holm"), then
    #    multcompView::multcompLetters(<symmetric p matrix>, threshold = 0.05)$Letters: w a, x a, y b, z c
    assert got["letters"].tolist() == ["a", "a", "b", "c"]
    assert got["count"].tolist() == [5, 5, 5, 5]


def test_letters_errors(marks):
    with pytest.raises(SimplydataError, match='Did you mean show="letters"'):
        marks.compare_each_pair_of("marks", for_each_group_in="class", show="letter")
    with pytest.raises(SimplydataError, match="against="):
        marks.compare_each_pair_of("marks", for_each_group_in="class", against="A", show="letters")
