"""Numbers phase, batch 3: table.find_nearest_rows_to, find_distances_to_rows_of and find_fence_around (SciPy
spatial), on pandas and Polars tables, each against SciPy doing the same."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy.spatial import ConvexHull, KDTree, distance

import simplydata as sdata


def _stations() -> pd.DataFrame:
    return sdata.get_example("stations").as_pandas()


@pytest.mark.parametrize("fast", [False, True])
def test_find_nearest_rows_to_is_kdtree_query(fast):
    df = _stations()
    table = sdata.table(sdata.get_example("stations"), fast=fast)
    found = table.find_nearest_rows_to({"east": 4000, "north": 1000}, how_many=3).as_pandas()
    gaps, rows = KDTree(df[["east", "north"]].to_numpy(dtype=float)).query([4000, 1000], k=3)
    assert found["station"].tolist() == df["station"].iloc[rows].tolist()
    np.testing.assert_allclose(found["distance"], gaps, rtol=1e-15)
    assert len(table.as_pandas()) == len(df)  # the table itself is not changed


def test_find_nearest_rows_to_within_is_query_ball_point():
    df = _stations()
    found = sdata.table(sdata.get_example("stations")).find_nearest_rows_to(
        {"east": 4000, "north": 1000}, within=1000).as_pandas()
    xy = df[["east", "north"]].to_numpy(dtype=float)
    inside = KDTree(xy).query_ball_point([4000, 1000], r=1000)
    assert sorted(found["station"]) == sorted(df["station"].iloc[inside])
    assert found["distance"].is_monotonic_increasing and found["distance"].max() <= 1000
    listed = sdata.table(sdata.get_example("stations")).find_nearest_rows_to([4000, 1000], using=["east", "north"])
    assert len(listed.as_pandas()) == 1


def test_find_nearest_rows_to_leaves_out_empty_rows_and_explains(capsys):
    table = sdata.table(pd.DataFrame({"x": [0.0, 1, None, 3], "y": [0.0, 1, 2, 3], "name": list("abcd")}))
    found = table.find_nearest_rows_to({"x": 2.0, "y": 2.0}, how_many=4).as_pandas()
    assert sorted(found["name"]) == ["a", "b", "d"]
    with pytest.raises(sdata.SimplydataError, match="point="):
        table.find_nearest_rows_to(5)
    with pytest.raises(sdata.SimplydataError, match="how_many="):
        table.find_nearest_rows_to({"x": 1, "y": 1}, how_many=0)


@pytest.mark.parametrize("method, metric", [("euclidean", "euclidean"), ("manhattan", "cityblock"),
                                            ("bray-curtis", "braycurtis"), ("cosine", "cosine")])
def test_find_distances_to_rows_of_is_cdist(method, metric):
    df = _stations()
    a, b = sdata.table(sdata.get_example("stations")), sdata.table(sdata.get_example("stations"), fast=True)
    a.keep_first_rows(4)
    b.keep_last_rows(3)
    found = a.find_distances_to_rows_of(b, using=["east", "north"], test_method=method, names="station").as_pandas()
    d = distance.cdist(df[["east", "north"]].head(4), df[["east", "north"]].tail(3), metric=metric)
    assert found.columns.tolist() == ["station", *df["station"].tail(3)]
    assert found["station"].tolist() == df["station"].head(4).tolist()
    np.testing.assert_allclose(found.iloc[:, 1:].to_numpy(dtype=float), d, rtol=1e-15)


@pytest.mark.parametrize("fast", [False, True])
def test_find_fence_around_is_convex_hull(fast, capsys):
    df = _stations()
    corners = sdata.table(sdata.get_example("stations"), fast=fast).find_fence_around(x="east", y="north").as_pandas()
    hull = ConvexHull(df[["east", "north"]].to_numpy(dtype=float))
    assert corners["station"].tolist() == df["station"].iloc[hull.vertices].tolist()
    out = capsys.readouterr().out
    assert f"{len(hull.vertices)} corners" in out and f"area {hull.volume:.6g}" in out and f"length {hull.area:.6g}" in out
    # a closed form: the fence around the corners of a 2 x 3 rectangle and a point inside
    box = sdata.table(pd.DataFrame({"x": [0, 2, 2, 0, 1], "y": [0, 0, 3, 3, 1]}))
    assert len(box.find_fence_around(x="x", y="y").as_pandas()) == 4
    assert "area 6, length 10" in capsys.readouterr().out
    with pytest.raises(sdata.SimplydataError, match="one straight line"):
        sdata.table(pd.DataFrame({"x": [0, 1, 2], "y": [0, 1, 2]})).find_fence_around(x="x", y="y")


def test_table_other_names_point_to_the_new_words():
    table = sdata.table(sdata.get_example("stations"))
    for name, word in [("KDTree", "find_nearest_rows_to"), ("cdist", "find_distances_to_rows_of"),
                       ("ConvexHull", "find_fence_around"), ("chull", "find_fence_around")]:
        with pytest.raises(AttributeError, match=word):
            getattr(table, name)
