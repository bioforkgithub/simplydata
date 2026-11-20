"""The interaction picture (phase S3a-3): chart.draw_interaction_lines(x=, y=, colour=).

One line per colour group through the group averages of y at each x group, with 95 % t intervals of each
average, the groups moved a little apart so their bars do not hide each other. It is draw_lines(show="average",
with_dots=True) followed by draw_error_bars("confidence interval"): the averages from pandas and the t intervals
from SciPy (_stats.t_interval), drawn with matplotlib and seaborn. The same picture in seaborn is
pointplot(x=, y=, hue=, errorbar=<95 % t interval>, dodge=True); seaborn's own default errorbar is a bootstrap
interval, so the underneath box gives it the t interval.
"""

from __future__ import annotations

import pandas as pd

from .._errors import SimplydataError, column_error, friendly


class InteractionChartWords:
    @friendly(renamed={"color": "colour"})
    def draw_interaction_lines(self, x=None, y=None, colour=None):
        """An interaction picture: one line per colour group through the averages, with 95 % intervals.

        chart.draw_interaction_lines(x="tension", y="breaks", colour="wool")
        (with a table of the number of breaks of yarn of two wools at three tensions)
        Parallel lines: no sign that the effect of x depends on the colour groups. Lines that
        cross or spread apart: the effect of x depends on them, an interaction (test it with
        table.explain("breaks", using=["tension * wool"])). Each dot is a group average with its
        95 % confidence interval (t distribution); the groups are moved a little apart so they
        do not hide each other. Other names: interaction plot (R interaction.plot), pointplot
        (seaborn).
        """
        example = 'chart.draw_interaction_lines(x="diet", y="growth", colour="sex")'
        for role, value in (("x", x), ("y", y), ("colour", colour)):
            if not isinstance(value, str):
                raise SimplydataError(f".draw_interaction_lines() needs {role}= as a column name, for example "
                                      f"{example}.")
        data = self._data
        for value in (x, y, colour):
            if value not in data.columns:
                raise column_error(value, data.columns)
        if len({x, y, colour}) < 3:
            raise SimplydataError(".draw_interaction_lines() needs three different columns: x= (the groups along the "
                                  "bottom), y= (the numbers) and colour= (one line per group).")
        if not pd.api.types.is_numeric_dtype(data[y]) or pd.api.types.is_bool_dtype(data[y]):
            raise SimplydataError(f'.draw_interaction_lines() needs numbers for y=, but "{y}" holds words or other '
                                  "things.")
        for role, value in (("x", x), ("colour", colour)):
            groups = data[value].dropna().nunique()
            if groups < 2:
                raise SimplydataError(f'.draw_interaction_lines() needs at least 2 groups in {role}="{value}".')
            if groups > 12:
                raise SimplydataError(f'"{value}" has {groups} different values; {role}= needs a few groups. For a '
                                      "number column, put it into groups first with table.add_group_column(cut_at=[...]), "
                                      "or use draw_dots() with fit_line().")
        print(f'Interaction picture: parallel lines, no sign that the effect of "{x}" depends on "{colour}"; lines that '
              f'cross or spread apart: it depends on "{colour}" (check with table.explain("{y}", using=["{x} * '
              f'{colour}"])).')
        return self.draw_lines(x=x, y=y, colour=colour, show="average", with_dots=True).draw_error_bars(
            "confidence interval")
