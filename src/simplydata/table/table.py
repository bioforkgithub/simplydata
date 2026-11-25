"""The Table: one class that brings all the table word groups together."""

from __future__ import annotations

from .._data import reading_options
from .._errors import SimplydataError, friendly
from ._base import BaseTable
from .accuracy_words import AccuracyWords
from .agreement_words import AgreementWords
from .between import BetweenWords
from .causal_words import CausalWords
from .checking_more import CheckingMoreWords
from .communities import CommunityWords
from .columns import ColumnWords
from .correlation_words import CorrelationWords
from .distribution_words import DistributionTableWords
from .factor_words import HiddenFactorWords
from .fitting import FittingWords
from .forecasts import ForecastWords
from .lines_more import LinesMoreWords
from .meta_words import MetaWords
from .model_tools import ModelToolWords
from .models import ModelWords
from .more_table_words import MoreTableWords
from .more_tests import MoreTestWords
from .patterns import PatternWords
from .places import PlaceWords
from .positions import PositionWords
from .risk_words import RiskWords
from .rows import RowWords
from .signal_more import SignalMoreTableWords
from .signal_words import SignalTableWords
from .stat_tests import StatTestWords
from .summaries import SummaryWords
from .survival import SurvivalWords
from .survival_more import SurvivalMoreWords
from .survey_words import SurveyWords
from .time_series import TimeSeriesWords
from .time_steps import TimeStepWords


class Table(PositionWords, RowWords, ColumnWords, SummaryWords, StatTestWords, MoreTestWords, RiskWords, AccuracyWords,
            AgreementWords, CorrelationWords, FittingWords, LinesMoreWords, ModelWords, ModelToolWords, PatternWords, SurvivalWords, SurvivalMoreWords,
            TimeSeriesWords, TimeStepWords, ForecastWords, SignalTableWords, SignalMoreTableWords, BetweenWords,
            DistributionTableWords, CheckingMoreWords, MetaWords, CommunityWords, HiddenFactorWords, PlaceWords,
            CausalWords, SurveyWords, MoreTableWords, BaseTable):
    """A table. Make one with sdata.table(...), then add steps: table.keep_rows_where(...), table.sort_by(...)."""


# pandas read_csv(dtype=), Polars read_csv(schema_overrides=), R readr col_types= and read.csv colClasses=: each
# runs as read_as_text= when every type in it is text (a note once); other types are refused with the words to use
_READ_AS_TEXT_OTHERS = {"dtype": "read_as_text", "dtypes": "read_as_text", "schema_overrides": "read_as_text",
                        "col_types": "read_as_text", "colClasses": "read_as_text"}


@friendly(renamed={"big_data": "fast"}, others=_READ_AS_TEXT_OTHERS)
def table(data=None, sheet=None, fast: bool = False, separator=None, decimal_mark=None, thousands_mark=None,
          empty_values=None, skip_rows=None, encoding=None, table_number=None, read_as_text=None) -> Table:
    """Start a table.

    sdata.table(sdata.get_example("marks"))         a practice table
    sdata.table("my_file.xlsx")              a file (Excel, CSV, TSV, Parquet, JSON; Word, SPSS, Stata)
    sdata.table("my_file.xlsx", sheet="2026") one sheet of an Excel file; sheet="all" stacks every sheet
    sdata.table("data/*.csv")                several files stacked, with a "file" column (or a folder: "data/")
    sdata.table("https://example.org/data.csv") a file on the web
    fast=True                              use the fast engine (Polars), for big data

    sheet="all" reads every sheet of an Excel file into one table, with a "sheet" column naming the
    sheet each row came from. simplydata words then work sheet by sheet:
    everything = sdata.table("results.xlsx", sheet="all")
    everything.count_rows(for_each_group_in="sheet")                how many rows came from each sheet
    everything.find_average_of("marks", for_each_group_in="sheet")  a summary per sheet
    everything.keep_rows_where("sheet", is_equal_to="2026")         just one sheet's rows
    (keep_rows_where changes everything; everything.undo() brings the other sheets back.)
    sheet="all" stacks the sheets only when they have the same columns. Sheets that hold different
    data are read by name, each on its own: simplydata says which columns differ and prints a line
    to copy for each sheet, such as  patients = sdata.table("study.xlsx", sheet="patients").
    To write such a workbook, save each table with in_sheet= (in_sheet= saves, sheet= reads):
    marks_2025.save("results.xlsx", in_sheet="2025")
    marks_2026.save("results.xlsx", in_sheet="2026")

    separator= is the safe way to read a CSV or text file: give it when you know it, especially for
    a file with one column. Without it simplydata guesses (only a comma, semicolon, tab or bar, never
    a letter or a digit) and prints its guess:
    sdata.table("species.csv", separator=",")

    Reading options, for files whose values are written differently:
    separator=","            the character between values: ",", ";", "|" or "tab" ("space" too)
    decimal_mark=","         3,5 means three and a half
    thousands_mark="."       1.000 means one thousand
    empty_values=["NA", "-"] markers that mean "no value"
    skip_rows=2              skip lines above the column names
    encoding="latin-1"       for text files not saved as UTF-8
    table_number=2           which table in a Word file ("all" stacks them)
    read_as_text=["sample_id"] keep these columns as text, exactly as typed

    read_as_text= stops a reader from changing what was typed: sample IDs such as 007 stay 007
    (not 7), and lab codes such as 3-12 or 2/4 stay text. Without it, a column that looks like
    numbers is read as numbers, and the zeros in front are lost before any later step can save
    them. As pandas read_csv(dtype={"sample_id": str}) and Polars read_csv(schema_overrides=
    {"sample_id": pl.String}); for CSV, TSV, Excel and Word files.
    sdata.table("fjord_lab.csv", read_as_text=["sample_id"])
    """
    if not isinstance(fast, bool):
        raise SimplydataError("fast= should be True or False.")
    if data is None:
        raise SimplydataError('sdata.table() needs some data, for example sdata.table(sdata.get_example("marks")).')
    reading = reading_options(separator=separator, decimal_mark=decimal_mark, thousands_mark=thousands_mark,
                              empty_values=empty_values, skip_rows=skip_rows, encoding=encoding,
                              table_number=table_number, read_as_text=read_as_text)
    return Table(data, sheet=sheet, fast=fast, _reading=reading)
