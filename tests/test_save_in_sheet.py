"""table.save("x.xlsx", in_sheet=...): several tables as sheets of one Excel file, read back with sheet= and
sheet="all". A pure pass-through to pandas ExcelWriter with openpyxl (mode="a", if_sheet_exists="replace").

The simplydata side uses only simplydata words; the openpyxl lines check the file itself.
"""

import openpyxl
import pytest

import simplydata as sdata
from simplydata import SimplydataError


def made_up(fast=False):
    """A small made-up workbook's two tables: marks for 2025 (3 rows) and 2026 (2 rows)."""
    marks_2025 = sdata.table({"name": ["Asha", "Ben", "Chen"], "marks": [60, 70, 80]}, fast=fast)
    marks_2026 = sdata.table({"name": ["Asha", "Ben"], "marks": [65, 85]}, fast=fast)
    return marks_2025, marks_2026


def sheets_in(path):
    book = openpyxl.load_workbook(path, read_only=True)
    try:
        return book.sheetnames
    finally:
        book.close()


@pytest.mark.parametrize("fast", [False, True])
def test_round_trip_in_sheet_then_sheet_all(tmp_path, fast, capsys):
    if fast:
        pytest.importorskip("polars")
    results = tmp_path / "results.xlsx"
    marks_2025, marks_2026 = made_up(fast)
    marks_2025.save(results, in_sheet="2025")       # the file does not exist: it is made with this sheet
    marks_2026.save(results, in_sheet="2026")       # the file exists: the sheet is added, 2025 is kept
    assert sheets_in(results) == ["2025", "2026"]
    assert "Replaced" not in capsys.readouterr().out

    one = sdata.table(results, sheet="2026")
    assert one.count_rows() == 2
    assert one.get_row(2) == {"name": "Ben", "marks": 85}

    # The manual's lines (save and sdata.table docstrings), run as written.
    everything = sdata.table(results, sheet="all")
    assert everything.get_column_names() == ["sheet", "name", "marks"]
    per_sheet = everything.count_rows(for_each_group_in="sheet")
    assert per_sheet.get_row(1)["sheet"] == "2025" and per_sheet.get_row(2)["sheet"] == "2026"
    assert list(per_sheet.get_column(per_sheet.get_column_names()[-1])) == [3, 2]
    averages = everything.find_average_of("marks", for_each_group_in="sheet")
    assert averages.get_row(1)["sheet"] == "2025" and averages.get_row(2)["sheet"] == "2026"
    assert list(averages.get_column(averages.get_column_names()[-1])) == [70, 75]
    everything.keep_rows_where("sheet", is_equal_to="2026")
    assert everything.count_rows() == 2
    assert everything.get_column("name") == ["Asha", "Ben"]
    everything.undo()                               # the other sheet comes back
    assert everything.count_rows() == 5


def test_same_sheet_name_is_replaced_and_said(tmp_path, capsys):
    results = tmp_path / "results.xlsx"
    marks_2025, marks_2026 = made_up()
    marks_2025.save(results, in_sheet="2025")
    marks_2026.save(results, in_sheet="2026")
    capsys.readouterr()
    marks_2026.save(results, in_sheet="2025")       # replace 2025 with the 2026 rows
    assert capsys.readouterr().out.strip() == 'Replaced the sheet "2025" in results.xlsx; the other sheets are kept.'
    assert sheets_in(results) == ["2025", "2026"]   # same place, nothing lost
    assert sdata.table(results, sheet="2025").count_rows() == 2
    assert sdata.table(results, sheet="2026").count_rows() == 2


def test_without_in_sheet_the_whole_file_is_replaced_as_before(tmp_path):
    results = tmp_path / "results.xlsx"
    marks_2025, marks_2026 = made_up()
    marks_2025.save(results, in_sheet="2025")
    marks_2026.save(results, in_sheet="2026")
    marks_2025.save(results)
    assert sheets_in(results) == ["Sheet1"]         # pandas to_excel's own default, unchanged
    assert sdata.table(results).count_rows() == 3


def test_sheets_with_different_columns_are_read_one_by_one(tmp_path):
    results = tmp_path / "results.xlsx"
    marks_2025, _ = made_up()
    marks_2025.save(results, in_sheet="marks")
    sdata.table({"name": ["Asha"], "age": [12]}).save(results, in_sheet="ages")
    with pytest.raises(SimplydataError, match='sheet "ages" has no column "marks"'):
        sdata.table(results, sheet="all")
    assert sdata.table(results, sheet="ages").get_column_names() == ["name", "age"]


@pytest.mark.parametrize("kind", ["csv", "tsv", "parquet", "json"])
def test_in_sheet_needs_an_excel_file(tmp_path, kind):
    marks_2025, _ = made_up()
    with pytest.raises(SimplydataError, match=r"Only \.xlsx files have sheets") as error:
        marks_2025.save(tmp_path / f"results.{kind}", in_sheet="2025")
    assert 'table.save("results.xlsx", in_sheet=\'2025\')' in str(error.value)
    assert not (tmp_path / f"results.{kind}").exists()


@pytest.mark.parametrize("name, message", [
    ("2025/26", r'Excel does not allow "/" in a sheet name'),
    ("a:b", r'Excel does not allow ":"'),
    ("[raw]", r'Excel does not allow "\["'),
    ("why?", r'Excel does not allow "\?"'),
    ("x" * 32, r"at most 31 characters in a sheet name; \"x+\" has 32"),
    ("", r"at least one letter or digit"),
    ("   ", r"at least one letter or digit"),
    (2025, r'in_sheet= is the name of a sheet, in quotes: in_sheet="2025"'),
])
def test_sheet_names_follow_excel_rules(tmp_path, name, message):
    results = tmp_path / "results.xlsx"
    marks_2025, marks_2026 = made_up()
    marks_2025.save(results, in_sheet="2025")
    with pytest.raises(SimplydataError, match=message):
        marks_2026.save(results, in_sheet=name)
    assert sheets_in(results) == ["2025"]           # a refused name leaves the file as it was


def test_thirty_one_characters_is_allowed(tmp_path):
    results = tmp_path / "results.xlsx"
    made_up()[0].save(results, in_sheet="x" * 31)
    assert sheets_in(results) == ["x" * 31]


def test_excel_counts_names_the_same_whatever_the_case(tmp_path):
    results = tmp_path / "results.xlsx"
    marks_2025, marks_2026 = made_up()
    marks_2025.save(results, in_sheet="Cleaned")
    with pytest.raises(SimplydataError, match='already has a sheet "Cleaned", and Excel counts "cleaned"'):
        marks_2026.save(results, in_sheet="cleaned")
    assert sheets_in(results) == ["Cleaned"]


def test_a_file_that_is_not_excel_inside(tmp_path):
    fake = tmp_path / "results.xlsx"
    fake.write_text("name,marks\nAsha,60\n", encoding="utf-8")
    with pytest.raises(SimplydataError, match="cannot open it as an Excel file"):
        made_up()[0].save(fake, in_sheet="2025")


def test_other_tools_names_point_to_in_sheet(tmp_path, capsys):
    results = tmp_path / "results.xlsx"
    made_up()[0].save(results, sheet_name="2025")   # pandas to_excel(sheet_name=)
    assert "sheet_name= is in_sheet= in simplydata" in capsys.readouterr().out
    made_up()[1].save(results, sheetName="2026")    # R openxlsx write.xlsx(sheetName=)
    assert sheets_in(results) == ["2025", "2026"]


def test_sheet_on_save_suggests_in_sheet(tmp_path):
    with pytest.raises(SimplydataError, match="Did you mean in_sheet="):
        made_up()[0].save(tmp_path / "results.xlsx", sheet="2025")


def test_different_sheets_get_a_line_to_copy_for_each(tmp_path):
    study = tmp_path / "study.xlsx"
    sdata.table({"name": ["Asha"], "age": [12]}).save(study, in_sheet="patients")
    sdata.table({"sample": ["S1"], "esbl": ["yes"]}).save(study, in_sheet="samples")
    with pytest.raises(SimplydataError) as error:
        sdata.table(study, sheet="all")
    text = str(error.value)
    assert text.startswith('The sheets in "study.xlsx" do not have the same columns, so they cannot be joined '
                           "into one table:")
    assert 'sheet "samples" has no column "name"' in text       # the list of differing columns is kept
    assert ('Read each sheet on its own:\n'
            '  patients = sdata.table("study.xlsx", sheet="patients")\n'
            '  samples  = sdata.table("study.xlsx", sheet="samples")') in text
    patients = sdata.table(study, sheet="patients")              # the copied line works
    assert patients.get_column_names() == ["name", "age"]


def test_names_to_copy_are_plain_cleaned_sheet_names(tmp_path):
    study = tmp_path / "study.xlsx"
    names = ["Raw data", "2026", "class", "Raw-data", "Ward B (ICU)"] + [f"extra {i}" for i in range(8)]
    for i, name in enumerate(names):
        sdata.table({f"column {i}": [1]}).save(study, in_sheet=name)
    with pytest.raises(SimplydataError) as error:
        sdata.table(study, sheet="all")
    text = str(error.value)
    assert 'raw_data    = sdata.table("study.xlsx", sheet="Raw data")' in text
    assert 'sheet_2026  = sdata.table("study.xlsx", sheet="2026")' in text      # a leading digit
    assert 'sheet_class = sdata.table("study.xlsx", sheet="class")' in text     # a Python keyword
    assert 'raw_data_2  = sdata.table("study.xlsx", sheet="Raw-data")' in text  # the same after cleaning
    assert 'ward_b_icu  = sdata.table("study.xlsx", sheet="Ward B (ICU)")' in text
    assert '  and the same for the sheets "extra 5", "extra 6", "extra 7"' in text  # past ten, names only


def test_files_with_different_columns_keep_their_message(tmp_path):
    sdata.table({"name": ["Asha"], "marks": [60]}).save(tmp_path / "a.csv")
    sdata.table({"name": ["Ben"], "age": [12]}).save(tmp_path / "b.csv")
    with pytest.raises(SimplydataError, match="These files do not all have the same columns"):
        sdata.table(str(tmp_path / "*.csv"))


def test_the_underneath_box_needs_mode_a():
    from simplydata._underneath import UNDERNEATH, Entry
    from simplydata._underneath.check import check_entry

    entry = UNDERNEATH["table.save in_sheet="]
    changed = {"pandas": entry.code["pandas"].replace('mode="a", if_sheet_exists="replace"', 'mode="w"')}
    outcomes = check_entry(Entry(**{**entry.__dict__, "code": changed}))
    assert outcomes and not any(o.passed for o in outcomes)
