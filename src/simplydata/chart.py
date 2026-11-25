"""The Chart: one class that brings all the word groups together."""

from __future__ import annotations

from ._core import BaseChart
from ._errors import SimplydataError, friendly
from .words.agreement_charts import AgreementChartWords
from .words.answer_charts import AnswerChartWords
from .words.axes import AxesWords
from .words.charts import ChartWords
from .words.community_charts import CommunityChartWords
from .words.curves import CurveWords
from .words.interaction_charts import InteractionChartWords
from .words.layout import LayoutWords
from .words.letters_and_legends import LetterLegendWords
from .words.look import LookWords
from .words.place_charts import PlaceChartWords
from .words.read_back import ReadBackWords
from .words.second_cues import SecondCueWords
from .words.stats import StatsWords
from .words.survival import SurvivalChartWords
from .words.text import TextWords
from .words.time_charts import TimeChartWords


class Chart(ChartWords, StatsWords, CurveWords, InteractionChartWords, SurvivalChartWords, AgreementChartWords,
            CommunityChartWords, PlaceChartWords, AnswerChartWords, TimeChartWords, TextWords,
            AxesWords, LookWords, LayoutWords, ReadBackWords, SecondCueWords, LetterLegendWords, BaseChart):
    """A chart. Make one with sdata.chart(...), then add steps: chart.draw_bars(...), chart.write_title_on_top(...)."""


@friendly(renamed={"big_data": "fast"})
def chart(data=None, sheet=None, fast: bool = False) -> Chart:
    """Start a chart. sdata.chart(sdata.get_example("marks"))

    sdata.chart(table)                        a pandas or Polars table, like sdata.get_example("marks")
    sdata.chart("my_file.xlsx")               your own file (Excel, CSV, TSV, Parquet, JSON)
    sdata.chart("my_file.xlsx", sheet="2026") one sheet of an Excel file
    sdata.chart()                             no table: give lists to each step instead
    fast=True                              always use the fast engine (Polars) to read the file
    """
    if not isinstance(fast, bool):
        raise SimplydataError("fast= should be True or False.")
    return Chart(data, sheet=sheet, fast=fast)
