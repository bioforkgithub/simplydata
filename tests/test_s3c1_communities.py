"""S3c-1, communities and resistomes: diversity, log ratios, PCoA, constrained ordination, Mantel and Procrustes,
ANOSIM and SIMPER, silhouettes and the cluster tree, discriminant and correspondence axes, the depth note and the
refusals of the independent review (columns= required, GBM on non-whole numbers, rare columns, Ward with
Bray-Curtis, Euclidean RDA on raw counts). The numbers themselves are checked against R in test_underneath (the
same underneath) and in the reliability study (validation/cases_communities.py).
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata._errors import SimplydataError
from conftest import example_frame

GENES = ["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB", "aadA", "mphA",
         "vanA", "mcr1"]


def _table():
    return sdata.table(sdata.get_example("resistome"))


# ---------------------------------------------------------------- the practice table
def test_resistome_is_made_up_and_says_so():
    from simplydata.data import EXAMPLES

    about, columns = EXAMPLES["resistome"]
    assert "MADE-UP" in about and "not from any real study" in about
    frame = example_frame("resistome")
    assert len(frame) == 24 and set(GENES) <= set(frame.columns)
    counts = frame[GENES].to_numpy()
    assert (counts >= 0).all() and (counts == np.round(counts)).all()
    assert ((counts > 0).sum(axis=0) >= 2).all()  # every gene can take estimated small values
    totals = counts.sum(axis=1)
    assert totals.max() > 2 * totals.min()  # depths differ: the lessons show why that matters


# ---------------------------------------------------------------- refusals before R
@pytest.mark.parametrize("call", [
    lambda t: t.add_diversity_columns(),
    lambda t: t.add_log_ratio_columns(),
    lambda t: t.explain_profiles_of(using=["temperature"]),
])
def test_columns_are_required_on_the_community_words(call):
    with pytest.raises(SimplydataError, match="needs columns=") as error:
        call(_table())
    assert '"temperature"' in str(error.value) and '"blaTEM"' in str(error.value)


def test_chart_community_words_need_columns_too():
    chart = _table().start_chart()
    with pytest.raises(SimplydataError, match="needs columns="):
        chart.draw_richness_curves()


def test_chao1_and_rarefaction_refuse_normalised_values_but_richness_does_not():
    frame = example_frame("resistome")
    frame[GENES] = frame[GENES].div(frame[GENES].sum(axis=1), axis=0) * 1000
    table = sdata.table(frame)
    with pytest.raises(SimplydataError, match="raw counts"):
        table.add_diversity_columns(columns=GENES, show="chao1")
    with pytest.raises(SimplydataError, match="raw counts"):
        table.add_diversity_columns(columns=GENES, at_total_count=100)


def test_estimated_small_values_refuse_normalised_values():
    frame = example_frame("resistome")
    frame[GENES] = frame[GENES] / 7.3
    with pytest.raises(SimplydataError, match="needs raw counts"):
        sdata.table(frame).add_log_ratio_columns(columns=GENES)
    with pytest.raises(SimplydataError, match="robust aitchison"):
        sdata.table(frame).find_distances_between_rows(columns=GENES, measure="aitchison")


def test_a_rare_column_is_refused_with_the_merging_line():
    frame = example_frame("resistome")
    frame["mcr1"] = 0
    frame.loc[0, "mcr1"] = 3
    with pytest.raises(SimplydataError) as error:
        sdata.table(frame).add_log_ratio_columns(columns=GENES)
    text = str(error.value)
    assert '"mcr1"' in text and 'table.add_column("other", by_adding=["mcr1"])' in text and "no count is lost" in text


def test_negative_values_and_empty_rows_are_refused():
    frame = example_frame("resistome")
    frame.loc[0, "sul1"] = -1
    with pytest.raises(SimplydataError, match="below 0"):
        sdata.table(frame).add_log_ratio_columns(columns=GENES)
    frame = example_frame("resistome")
    frame.loc[2, GENES] = 0
    with pytest.raises(SimplydataError, match="nothing in it"):
        sdata.table(frame).add_log_ratio_columns(columns=GENES)


def test_alr_needs_against_and_clr_takes_none():
    with pytest.raises(SimplydataError, match="against="):
        _table().add_log_ratio_columns(columns=GENES, test_method="alr")
    with pytest.raises(SimplydataError, match="against="):
        _table().add_log_ratio_columns(columns=GENES, against="sul1")


def test_ward_is_refused_with_bray_curtis_and_kmeans_takes_no_measure():
    with pytest.raises(SimplydataError, match='linkage="ward" assumes straight-line'):
        _table().add_clusters(columns=GENES, test_method="hierarchical", measure="bray-curtis", linkage="ward")
    with pytest.raises(SimplydataError, match="takes no measure="):
        _table().add_clusters(columns=GENES, measure="bray-curtis")
    with pytest.raises(SimplydataError, match='linkage="ward"'):
        _table().start_chart().draw_cluster_tree(columns=GENES, measure="bray-curtis", linkage="ward")


def test_euclidean_rda_on_raw_counts_is_refused_with_hellinger():
    with pytest.raises(SimplydataError, match='measure="hellinger"'):
        _table().explain_profiles_of(GENES, using=["temperature"], measure="euclidean")


def test_canonical_correspondence_takes_no_measure():
    with pytest.raises(SimplydataError, match="no measure="):
        _table().explain_profiles_of(GENES, using=["temperature"], test_method="cca", measure="bray-curtis")


def test_simper_goes_with_permanova_and_bray_curtis_only():
    with pytest.raises(SimplydataError, match="not a test"):
        _table().compare_profiles_of(GENES, for_each_group_in="site", test_method="anosim", show="contributions")
    with pytest.raises(SimplydataError, match="Bray-Curtis"):
        _table().compare_profiles_of(GENES, for_each_group_in="site", measure="jaccard", show="contributions")


def test_using_columns_cannot_be_profile_columns():
    with pytest.raises(SimplydataError, match="cannot be both"):
        _table().explain_profiles_of(GENES, using=["sul1"])


def test_correspondence_axes_refuse_numbers_and_text_together():
    with pytest.raises(SimplydataError, match="not both"):
        _table().add_correspondence_axes(columns=["sul1", "site"])


# ---------------------------------------------------------------- no R needed
def test_depth_note_on_bray_curtis_with_raw_counts(capsys):
    _table().find_distances_between_rows(columns=GENES, names="sample")
    out = capsys.readouterr().out
    assert "very different totals (from 1,285 to 59,389)" in out and 'measure="aitchison"' in out
    assert "14 columns (blaTEM" in out


def test_hierarchical_clusters_with_bray_curtis_choose_average_linkage(capsys):
    from simplydata._r import r_ready

    table = _table().add_clusters(columns=GENES, how_many=3, test_method="hierarchical", measure="bray-curtis")
    out = capsys.readouterr().out
    assert 'simplydata chooses linkage="average" for Bray-Curtis' in out
    assert 'hclust(vegan::vegdist(x, "bray"), method = "average")' in out
    assert set(table.as_pandas()["cluster"]) == {1, 2, 3}
    if not r_ready(("cluster", "vegan")):
        assert "needs R (cluster package)" in out


def test_cluster_tree_matches_scipy_and_prints_the_cophenetic_correlation(capsys):
    from scipy.cluster.hierarchy import cophenet, linkage
    from scipy.spatial.distance import pdist

    chart = _table().start_chart()
    chart.draw_cluster_tree(columns=GENES, measure="bray-curtis", names="sample")
    out = capsys.readouterr().out
    x = example_frame("resistome")[GENES].to_numpy(dtype=float)
    d = pdist(x, "braycurtis")
    r, _ = cophenet(linkage(d, "average"), d)
    assert f"Cophenetic correlation {r:.2f}" in out
    fig = chart._render()
    ax = fig.axes[0]
    assert len(ax.get_lines()) == len(x) - 1  # one link per join
    assert sorted(t.get_text() for t in ax.get_xticklabels()) == sorted(example_frame("resistome")["sample"])


# ---------------------------------------------------------------- with R
def test_diversity_columns_and_the_effective_number(needs_r, capsys):
    table = _table().add_diversity_columns(columns=GENES)
    out = capsys.readouterr().out
    frame = table.as_pandas()
    assert {"richness", "shannon", "simpson"} <= set(frame.columns)
    assert "equally common kinds" in out and "natural log" in out
    assert "at_total_count=1285" in out  # the depth note
    assert frame["richness"].between(1, 14).all()


def test_rarefaction_leaves_rows_below_the_total_empty(needs_r, capsys):
    table = _table().add_diversity_columns(columns=GENES, show="richness", at_total_count=2000, names="sample")
    out = capsys.readouterr().out
    column = table.as_pandas()["expected richness at 2000"]
    assert column.isna().sum() == 2 and "FS3" in out and "FS4" in out


def test_richness_is_allowed_on_normalised_values_with_a_note(needs_r, capsys):
    frame = example_frame("resistome")
    frame[GENES] = frame[GENES].div(frame[GENES].sum(axis=1), axis=0) * 1000
    sdata.table(frame).add_diversity_columns(columns=GENES)
    assert "not whole" in capsys.readouterr().out


def test_log_ratios_keep_every_column_and_print_the_zero_summary(needs_r, capsys):
    table = _table().add_log_ratio_columns(columns=GENES)
    out = capsys.readouterr().out
    frame = table.as_pandas()
    assert [f"clr_{g}" for g in GENES] == [c for c in frame.columns if c.startswith("clr_")]
    assert np.allclose(frame[[f"clr_{g}" for g in GENES]].sum(axis=1), 0, atol=1e-9)  # clr rows sum to 0
    assert "27 of 336 cells are zero" in out and "z.delete = FALSE" in out


def test_adding_one_says_the_answer_depends_on_it(needs_r, capsys):
    _table().add_log_ratio_columns(columns=GENES, zeros_replaced_by="adding 1")
    assert "depends on the 1 you added" in capsys.readouterr().out


def test_pcoa_says_which_percent_and_counts_negative_eigenvalues(needs_r, capsys):
    table = _table().add_principal_coordinates(columns=GENES)
    out = capsys.readouterr().out
    assert "shares of the positive eigenvalues" in out and "eigenvalues are negative" in out and "ape::pcoa" in out
    table.add_principal_coordinates(columns=GENES, measure="aitchison")
    assert "No eigenvalue is negative" in capsys.readouterr().out


def test_explain_profiles_of_tests_each_column_after_the_others(needs_r, capsys):
    result = _table().explain_profiles_of(GENES, using=["temperature", "salinity"]).as_pandas()
    out = capsys.readouterr().out
    assert list(result["term"]) == ["all together", "temperature", "salinity"]
    assert "adjusted R squared" in out and 'by = "margin"' in out and "observational" in out
    assert "simplydata chooses distance-based RDA" in out
    swapped = _table().explain_profiles_of(GENES, using=["salinity", "temperature"]).as_pandas()
    a = result.set_index("term")["p-value"]
    b = swapped.set_index("term")["p-value"]
    assert a["temperature"] == b["temperature"] and a["salinity"] == b["salinity"]


def test_permutation_floor_says_at_most(needs_r, capsys):
    _table().compare_profiles_of(GENES, for_each_group_in="site")
    assert "at most about 1 of 1000" in capsys.readouterr().out


def test_anosim_and_simper(needs_r, capsys):
    row = _table().compare_profiles_of(GENES, for_each_group_in="site", test_method="anosim").as_pandas().iloc[0]
    assert row["test"] == "ANOSIM" and 0 <= row["statistic"] <= 1
    simper = _table().compare_profiles_of(GENES, for_each_group_in="site", show="contributions").as_pandas()
    out = capsys.readouterr().out
    assert "Warton" in out and "p-value" not in simper.columns
    assert set(simper["column"]) == set(GENES) and len(simper) == 6 * len(GENES)


def test_mantel_and_procrustes(needs_r, capsys):
    row = _table().find_correlation_between_profiles(first=GENES, second=["temperature", "salinity"]).as_pandas()
    out = capsys.readouterr().out
    assert row["test"][0] == "Mantel" and "not about the columns themselves" in out
    assert "dist(scale(y))" in out
    row = _table().find_correlation_between_profiles(first=GENES, second=["temperature", "salinity"],
                                                     test_method="procrustes").as_pandas()
    assert 0 <= row["statistic"][0] <= 1


def test_automatic_clusters_print_each_width(needs_r, capsys):
    _table().add_clusters(columns=GENES, how_many="automatic", test_method="hierarchical", measure="bray-curtis")
    out = capsys.readouterr().out
    assert "Average silhouette width for each number of clusters: 2:" in out and "Kaufman & Rousseeuw" in out


def test_show_silhouette_gives_each_rows_width(needs_r):
    widths = _table().add_clusters(columns=GENES, how_many=3, show="silhouette").as_pandas()
    assert list(widths.columns) == ["row", "cluster", "next best cluster", "silhouette width"]
    assert widths["silhouette width"].between(-1, 1).all()


def test_discriminant_axes_print_the_chance_level(needs_r, capsys):
    table = _table().add_axes_that_separate_groups(columns=["temperature", "salinity"], for_each_group_in="site")
    out = capsys.readouterr().out
    assert {"LD1", "LD2"} <= set(table.as_pandas().columns)
    assert "by always guessing the largest group: 25.0 %" in out and "leave-one-out" in out


def test_discriminant_axes_after_rosners_test_in_the_same_session(needs_r, tmp_path):
    """Rosner's outlier test attached R's EnvStats, whose own predict() hides R's; MASS's predict() of the lda fit
    then stopped with "object 'x' not found". Found by pytest-xdist (PR #79), where a worker ran the tests in another
    order. A fresh Python, so R has attached only what these two words attach."""
    import os
    import subprocess
    import sys
    import textwrap

    script = tmp_path / "script.py"
    script.write_text(textwrap.dedent("""
        import pandas as pd
        import simplydata as sdata
        x = [12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 25.6, 3.0, 13.3]
        sdata.table(pd.DataFrame({"v": x})).show_rows_with_outliers("v", test_method="rosner")
        import os
        from simplydata._r import r_call
        print("DIAG search", list(r_call("search()", _cite=False)))
        print("DIAG env", sorted((k, v) for k, v in os.environ.items() if k.startswith(("R_", "PYTHON", "TMP"))))
        print("DIAG sdata", sdata.__file__)
        table = sdata.table(sdata.get_example("resistome")).add_axes_that_separate_groups(
            columns=["temperature", "salinity"], for_each_group_in="site")
        print("AXES", [c for c in table.as_pandas().columns if c.startswith("LD")])
    """), encoding="utf-8")
    src = os.path.dirname(os.path.dirname(os.path.abspath(sdata.__file__)))
    env = {**os.environ, "PYTHONPATH": src + os.pathsep + os.environ.get("PYTHONPATH", "")}
    run = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=tmp_path, env=env,
                         timeout=600)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-3000:]
    assert "AXES ['LD1', 'LD2']" in run.stdout, run.stdout[-2000:]


def test_correspondence_axes_on_counts_and_on_text(needs_r, capsys):
    _table().add_correspondence_axes(columns=GENES)
    assert "Correspondence analysis (CA)" in capsys.readouterr().out
    rng = np.random.default_rng(1)
    answers = pd.DataFrame({q: rng.choice(["agree", "neutral", "disagree"], 60) for q in ("q1", "q2", "q3", "q4")})
    sdata.table(answers).add_correspondence_axes(columns=["q1", "q2", "q3", "q4"])
    assert "Multiple correspondence analysis (MCA)" in capsys.readouterr().out


def test_richness_curves_draw_one_line_per_row(needs_r, capsys):
    chart = _table().start_chart()
    chart.draw_richness_curves(columns=GENES, colour="site")
    fig = chart._render()
    lines = fig.axes[0].get_lines()
    assert len(lines) == 24 + 1  # one curve per sample and the dotted line at the smallest total
    assert fig.axes[0].get_xlabel() == "Total count (reads, individuals)"


# ---------------------------------------------------------------- review fixes
def test_adding_one_is_refused_on_normalised_values():
    frame = example_frame("resistome")
    frame[GENES] = frame[GENES].div(frame[GENES].sum(axis=1), axis=0)
    with pytest.raises(SimplydataError, match="a 1 swamps the values"):
        sdata.table(frame).add_log_ratio_columns(columns=GENES, zeros_replaced_by="adding 1")


def test_a_total_count_above_every_row_is_refused():
    with pytest.raises(SimplydataError, match="above every row's total"):
        _table().add_diversity_columns(columns=GENES, at_total_count=10 ** 7)


def test_pcoa_and_correspondence_axes_need_columns():
    with pytest.raises(SimplydataError, match="needs columns="):
        _table().add_principal_coordinates()
    with pytest.raises(SimplydataError, match="needs columns="):
        _table().add_correspondence_axes()


def test_two_measurement_columns_are_never_read_as_counts(needs_r, capsys):
    frame = example_frame("resistome")
    frame["depth"] = np.arange(len(frame)) % 7 + 1
    frame["year"] = 2020 + np.arange(len(frame)) % 3
    sdata.table(frame).find_correlation_between_profiles(first=GENES, second=["depth", "year"])
    assert "read as measurements" in capsys.readouterr().out


def test_two_groups_give_one_discriminant_axis(needs_r, capsys):
    frame = example_frame("resistome")
    frame = frame[frame["site"].isin(["harbour", "fjord sediment"])]
    sdata.table(frame).add_axes_that_separate_groups(columns=["temperature", "salinity"],
                                                     for_each_group_in="site", how_many=1)
    assert "LD1 is the only axis" in capsys.readouterr().out
