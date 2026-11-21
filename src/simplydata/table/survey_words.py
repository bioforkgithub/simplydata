"""Survey designs (phase S3d-1): table.use_survey_design(weights=, strata=, clusters=, population_sizes=).

It is a setting, like chart.use_log_scale_x: from then on these words give answers for the population, from the
survey design (R survey, table/survey_r.py): find_average_of, find_total_of, find_median_of, find_percentile_of,
find_percent_of_rows_where, count_rows, explain, compare_averages_of (two groups) and compare_counts_of. Every
printout starts with "As a survey (...)". Every other statistics word refuses while the setting is on, rather than
give an answer that ignores the design (independent review: mode guards), and so does a survey word after rows
were removed (a part of a survey is analysed with for_each_group_in=, not by deleting rows: deleting them changes
the standard errors). table.use_survey_design() with no options turns the setting off.
"""

from __future__ import annotations

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly

# the words that use the survey design while it is on
SURVEY_WORDS = ("find_average_of", "find_total_of", "find_median_of", "find_percentile_of",
                "find_percent_of_rows_where", "count_rows", "explain", "compare_averages_of", "compare_counts_of")
# words of these classes look at or change the data itself, so they work as usual under a survey design
_DATA_CLASSES = ("BaseTable", "RowWords", "ColumnWords", "PositionWords", "TimeStepWords", "SurveyWords")
_DATA_EXTRA = ("get_column", "count_different_values_in", "find_smallest_of", "find_biggest_of", "start_chart")
_NOT_DATA = ("show_rows_with_outliers", "remove_rows_with_outliers")
# data words that work out numbers from the rows: they still work, with a note that the rows are not weighted
_UNWEIGHTED = ("describe_columns", "add_z_score_column", "add_rank_column", "add_rolling_column",
               "add_smoothed_column", "count_different_values_in", "find_smallest_of", "find_biggest_of")
EXAMPLE = ('table.use_survey_design(weights="weight", strata="school_type", population_sizes="schools_of_type")'
           '   (with sdata.get_example("sampled_schools"))')
INSTEAD = {
    "count_each": 'table.count_rows(for_each_group_in="{column}", in_percent=True) gives each value\'s estimated '
                  "share of the population",
    "find_standard_deviation_of": "find_average_of gives the population average with its standard error",
    "find_summary_of": "find_average_of, find_median_of and find_percentile_of each give one population number",
    "find_correlation_between": 'table.explain("y", using=["x"]) gives the survey-weighted slope',
}


def _say(value) -> str:
    """A survey estimate for a sentence: big totals with thousands marks (3,687,178), others as everywhere."""
    from .summaries import _say_number

    if value == value and abs(value) >= 100_000:
        return f"{value:,.0f}"
    return _say_number(value)


def _data_words(cls) -> set:
    found = set(_DATA_EXTRA)
    for klass in cls.__mro__:
        if klass.__name__ in _DATA_CLASSES:
            found.update(n for n, v in vars(klass).items() if not n.startswith("_") and callable(v))
    return found - set(_NOT_DATA)


class SurveyWords:
    """The survey-design setting and the design-based routes of the survey words."""

    # ------------------------------------------------------------------ the setting
    @friendly(others={"weight": "weights", "pw": "weights", "stratum": "strata", "cluster": "clusters",
                      "ids": "clusters", "id": "clusters", "psu": "clusters", "fpc": "population_sizes"})
    def use_survey_design(self, weights=None, strata=None, clusters=None, population_sizes=None):
        """Treat the table as a survey sample, so that the survey words give answers for the population.

        table.use_survey_design(weights="weight", strata="school_type", population_sizes="schools_of_type")   (with sdata.get_example("sampled_schools"))
        weights=           how many people (schools, households ...) of the population each row stands for
        strata=            the column of the groups the sample was drawn within (strata)
        clusters=          the column of the clusters drawn first (schools, villages), when the rows were
                           drawn within them
        population_sizes=  how many the population has in each stratum (or the share sampled, 0 to 1)
        From then on find_average_of, find_total_of, find_median_of, find_percentile_of,
        find_percent_of_rows_where, count_rows, explain, compare_averages_of (two groups) and
        compare_counts_of give design-based answers (R survey), with intervals on the design's
        degrees of freedom. Other statistics words refuse while the design is on.
        table.use_survey_design() with no options turns it off. Needs R (survey).
        """
        step = "use_survey_design"
        given = {"weights": weights, "strata": strata, "clusters": clusters, "population_sizes": population_sizes}
        if all(v is None for v in given.values()):
            if self.__dict__.get("_survey"):
                object.__setattr__(self, "_survey", None)
                print("The survey design is off: the words describe the rows of this table again.")
            else:
                print("This table has no survey design. To set one: " + EXAMPLE)
            return self
        for option, name in given.items():
            if name is not None and not isinstance(name, str):
                raise SimplydataError(f"{option}= needs one column name in quotes (you gave {name!r}). Designs with "
                                      "more than one stage of clusters are not offered yet.\nFor example:  " + EXAMPLE)
        names = [v for v in given.values() if v is not None]
        self._need_columns(*names)
        if len(set(names)) < len(names):
            raise SimplydataError("Each design option needs its own column; one column is named twice.\nFor example:  "
                                  + EXAMPLE)
        columns = {k: v for k, v in given.items() if v is not None}
        design = self._design_values(columns)
        said = [f'{"population sizes" if option == "population_sizes" else option} "{name}"'
                for option, name in columns.items()]
        if "weights" not in design:
            print("Note: no weights= given, so every row counts the same (survey says: equal chances of being sampled).")
        from . import survey_r

        n = len(self._frame)
        found = survey_r.facts(design, n)
        state = {"columns": columns, "rows": n, "said": ", ".join(said), "df": found["df"]}
        object.__setattr__(self, "_survey", state)
        parts = [f"{int(found['strata'])} strat{'a' if found['strata'] != 1 else 'um'}" if strata else "",
                 f"{int(found['clusters'])} clusters" if clusters else ""]
        shape = ", ".join(p for p in parts if p)
        print(f"This table is now a survey ({state['said']}; {n} rows{', ' + shape if shape else ''}, "
              f"{found['df']:g} degrees of freedom of the design, R survey::svydesign()).")
        print("From now on find_average_of, find_total_of, find_median_of, find_percentile_of, find_percent_of_rows_"
              "where, count_rows, explain, compare_averages_of and compare_counts_of describe the population, from the "
              "survey design; other statistics words refuse. Turn it off with table.use_survey_design().")
        if population_sizes is not None:
            fractions = bool(np.all(design["population_sizes"] <= 1))
            unit = "clusters" if clusters else "rows"
            read = (f"the share of each stratum's {unit} that was sampled (0 to 1)" if fractions else
                    f"the number of {unit} in the population of each stratum")
            print(f'"{population_sizes}" is read as {read}, as survey::svydesign(fpc =) reads it; this makes the '
                  "standard errors smaller when much of a stratum was sampled.")
        if found["lonely"]:
            print(f"Note: {int(found['lonely'])} strat{'a have' if found['lonely'] != 1 else 'um has'} only one cluster; "
                  'simplydata sets options(survey.lonely.psu = "adjust") (survey\'s own default stops with an error), '
                  "which centres it at the overall average: a cautious choice.")
        return self

    # ------------------------------------------------------------------ guards
    def _survey_on(self) -> bool:
        return bool(self.__dict__.get("_survey"))

    def _survey_guard(self, word):
        """Called by every word (the friendly decorator) before it runs: under a survey design, a statistics word
        that does not use the design refuses."""
        if not self.__dict__.get("_survey") or word in SURVEY_WORDS:
            return
        known = type(self).__dict__.get("_SURVEY_DATA_WORDS")
        if known is None:
            known = _data_words(type(self))
            type.__setattr__(type(self), "_SURVEY_DATA_WORDS", known)
        if word in known:
            if word == "start_chart":
                print("Note: this table is a survey; the chart shows its rows as they are, not weighted.")
            elif word in _UNWEIGHTED:
                print(f"Note: this table is a survey; {word} works on its rows as they are, not weighted.")
            return
        hint = INSTEAD.get(word, "").format(column="...")
        raise SimplydataError(
            f"This table is set as a survey ({self._survey['said']}), and {word} does not use survey designs, so its "
            f"answer would describe only these rows, not the population. "
            + (f"Instead: {hint}. " if hint else "")
            + "The survey words are " + ", ".join(SURVEY_WORDS) + ". To use " + word + " on the rows as they are, turn "
            "the design off first:  table.use_survey_design()")

    def _design_values(self, columns):
        """The design columns as R gets them, read from the table as it is now (so sorting or changing rows keeps
        each row's weight with its row), and checked."""
        design = {}
        for option, name in columns.items():
            if name not in self._frame.columns:
                raise SimplydataError(f'The survey design uses "{name}" ({option}=), which is no longer in the table. '
                                      "Take the step back with table.undo(), or set the design again: " + EXAMPLE)
            empty = self._count(self._empty(name))
            if empty:
                raise SimplydataError(
                    f'"{name}" has {empty} empty cell{"s" * (empty != 1)}. Every row of a survey needs its design '
                    f"values ({option}=), or the standard errors are wrong. Fill them in from the survey's records; do "
                    "not remove the rows.")
            values = self._frame[name].to_numpy()
            if option in ("weights", "population_sizes"):
                if not self._frame.schema[name].is_numeric():
                    raise SimplydataError(f'{option}= needs a column of numbers; "{name}" holds text.\nFor example:  '
                                          + EXAMPLE)
                values = values.astype(float)
                if not np.all(np.isfinite(values)) or (values <= 0).any():
                    raise SimplydataError(f'{option}= needs numbers above 0; "{name}" has 0, a negative number or an '
                                          "endless value. Check those rows, then set the design again:  " + EXAMPLE)
            else:
                values = np.array([str(v) for v in values], dtype=object)
            design[option] = values
        return design

    def _survey_design(self, word):
        """The design of this call: the same number of rows as when it was set, its columns read again now."""
        state = self._survey
        if len(self._frame) != state["rows"]:
            raise SimplydataError(
                f"The table had {state['rows']} rows when use_survey_design() was set and has {len(self._frame)} now. "
                "A part of a survey is analysed with for_each_group_in= (or a column made with add_column), not by "
                "removing rows: removing them gives wrong standard errors. Take the step back with table.undo(), or "
                "set the design again on purpose with table.use_survey_design(...).")
        return self._design_values(state["columns"])

    def _survey_only(self, word, given: dict, allowed=()):
        """Refuse options the survey route does not take (anything not at its default)."""
        import inspect

        func = getattr(type(self), word)
        signature = inspect.signature(getattr(func, "__wrapped__", func))
        for name, value in given.items():
            if name in allowed or name == "self" or name not in signature.parameters:
                continue
            default = signature.parameters[name].default
            same = value is default
            if not same:
                try:
                    same = bool(value == default)
                except Exception:  # noqa: BLE001
                    same = False
            if not same:
                raise SimplydataError(
                    f"Under a survey design, {word} takes only " + ", ".join(f"{a}=" for a in allowed)
                    + f" (you gave {name}=). Turn the design off for the other options: table.use_survey_design()")

    def _survey_header(self) -> str:
        return f"As a survey ({self._survey['said']}): numbers describe the population."

    def _survey_values(self, column):
        values = self._frame[column]
        if not self._frame.schema[column].is_numeric():
            raise SimplydataError(f'"{column}" holds text; this word needs numbers under a survey design too. For '
                                  f'yes or no answers use find_percent_of_rows_where.\nFor example:  '
                                  'table.find_percent_of_rows_where("met_target", is_equal_to="yes")')
        empty = self._count(self._empty(column))
        if empty:
            print(f'Note: {empty} empty cell{"s" * (empty != 1)} in "{column}" '
                  f'{"were" if empty != 1 else "was"} left out (survey treats them as not asked; the design is kept).')
        return values.cast(nw.Float64).to_numpy()

    def _survey_group(self, word, for_each_group_in, column=None):
        if for_each_group_in is None:
            return None, None
        if not isinstance(for_each_group_in, str):
            raise SimplydataError(f"Under a survey design, {word}(for_each_group_in=) takes one column name; for two, "
                                  f"make one column of both first (add_column).\nFor example:  "
                                  f'table.{word}("score_2000", for_each_group_in="school_type")')
        self._need_columns(for_each_group_in)
        if for_each_group_in == column:
            raise SimplydataError(f'"{column}" cannot be both the column and the for_each_group_in= column.')
        empty = self._count(self._empty(for_each_group_in))
        if empty:
            print(f'Note: {empty} row{"s" * (empty != 1)} with an empty "{for_each_group_in}" belong to no group.')
        values = self._frame[for_each_group_in].to_numpy()
        return for_each_group_in, np.array([None if v is None or (isinstance(v, float) and np.isnan(v)) else str(v)
                                            for v in values], dtype=object)

    def _survey_table(self, data):
        import pandas as pd

        frame = pd.DataFrame(data)
        if self._frame.implementation.is_polars():
            import polars as pl

            frame = pl.from_pandas(frame)
        return self._new_table(nw.from_native(frame, eager_only=True))

    # ------------------------------------------------------------------ summaries
    def _survey_summary(self, word, what, column, for_each_group_in=None, percent=None, label=None):
        """find_average_of / find_total_of / find_median_of / find_percentile_of under a survey design."""
        from . import survey_r

        design = self._survey_design(word)
        if not isinstance(column, str):
            raise SimplydataError(f"{word}() needs one column name in quotes.\nFor example:  table.{word}(\"score_2000\")")
        self._need_columns(column)
        group, g = self._survey_group(word, for_each_group_in, column)
        y = self._survey_values(column)
        found = survey_r.estimate(design, len(self._frame), what, y=y, g=g,
                                  q=None if percent is None else percent / 100)
        name = f"{label} of {column}"
        data = {} if group is None else {group: found["grp"]}
        data.update({name: found["est"], "standard error": found["se"], f"{name} 95 % CI low": found["low"],
                     f"{name} 95 % CI high": found["high"], "degrees of freedom": [found["df"]] * len(found["est"])})
        r_name = {"mean": "svymean", "total": "svytotal", "quantile": 'svyquantile(qrule = "math")'}[what]
        print(self._survey_header())
        lines = [f"{'' if group is None else found['grp'][i] + ': '}{_say(found['est'][i])} (95 % CI "
                 f"{_say(found['low'][i])} to {_say(found['high'][i])})" for i in range(len(found["est"]))]
        where = "" if group is None else f' for each group of "{group}"'
        print(f'The population {label} of "{column}"{where}: ' + "; ".join(lines[:8])
              + (" ..." if len(lines) > 8 else "") + ".")
        how = ("Woodruff's interval" if what == "quantile" else "t interval")
        print(f"Method: R survey::{r_name}{' with svyby()' if group else ''}; {how} on the design's "
              f"{found['df']:g} degrees of freedom (survey's own confint() uses the normal curve).")
        return self._survey_table(data)

    def _survey_percent(self, word, column, hits, counted, words, for_each_group_in=None):
        """find_percent_of_rows_where(condition) under a survey design: svyciprop(method = "logit")."""
        from . import survey_r
        from .summaries import _say_percent

        design = self._survey_design(word)
        group, g = self._survey_group(word, for_each_group_in, column)
        y = np.where(counted, hits.astype(float), np.nan)
        found = survey_r.estimate(design, len(self._frame), "prop", y=y, g=g)
        # [D] shares (0 to 1) from svyciprop shown as percents
        est, low, high, se = (found[k] * 100 for k in ("est", "low", "high", "se"))
        print(self._survey_header())
        where = "" if group is None else f' in each group of "{group}"'
        lines = [f"{'' if group is None else found['grp'][i] + ': '}{_say_percent(est[i])} (95 % CI "
                 f"{_say_percent(low[i])} to {_say_percent(high[i])})" for i in range(len(est))]
        print(f'"{column}" {words} in this percent of the population{where}: ' + "; ".join(lines[:8])
              + (" ..." if len(lines) > 8 else "") + ".")
        print(f'Method: R survey::svyciprop(method = "logit"){" with svyby()" if group else ""}: the interval is worked '
              f"out on the log-odds scale, so it stays between 0 and 100 %, on the design's {found['df']:g} degrees of "
              "freedom.")
        data = {} if group is None else {group: found["grp"]}
        data.update({"percent": est, "standard error": se, "percent 95 % CI low": low, "percent 95 % CI high": high,
                     "degrees of freedom": [found["df"]] * len(est)})
        return self._survey_table(data)

    def _survey_count(self, word, for_each_group_in=None, in_percent=False):
        """count_rows under a survey design: the estimated number in the population (svytotal of ones), or each
        group's share (svymean(~factor(group)))."""
        from . import survey_r
        from .summaries import _say_percent

        design = self._survey_design(word)
        group, g = self._survey_group(word, for_each_group_in)
        n = len(self._frame)
        print(self._survey_header())
        if in_percent:
            if group is None:
                raise SimplydataError("count_rows(in_percent=True) needs for_each_group_in=: the percent of what?"
                                      f'\nFor example:  table.count_rows(for_each_group_in="award", in_percent=True)')
            found = survey_r.estimate(design, n, "share", g=g)
            est, low, high, se = (found[k] * 100 for k in ("est", "low", "high", "se"))  # [D] shares as percents
            lines = [f"{found['grp'][i]} {_say_percent(est[i])} (95 % CI {_say_percent(low[i])} to "
                     f"{_say_percent(high[i])})" for i in range(len(est))]
            print(f'Each group\'s estimated share of the population, by "{group}": ' + "; ".join(lines[:8]) + ".")
            print(f"Method: R survey::svymean(~factor({group})); t interval on the design's {found['df']:g} degrees "
                  "of freedom.")
            return self._survey_table({group: found["grp"], "percent": est, "standard error": se,
                                       "percent 95 % CI low": low, "percent 95 % CI high": high,
                                       "degrees of freedom": [found["df"]] * len(est)})
        found = survey_r.estimate(design, n, "count", g=g)
        lines = [f"{'' if group is None else found['grp'][i] + ': '}{_say(found['est'][i])} (95 % CI "
                 f"{_say(found['low'][i])} to {_say(found['high'][i])})" for i in range(len(found["est"]))]
        print(f"The estimated number in the population{'' if group is None else ' in each group of ' + chr(34) + group + chr(34)}"
              f" ({n} rows sampled): " + "; ".join(lines[:8]) + ".")
        print(f"Method: R survey::svytotal of a column of ones{' with svyby()' if group else ''} (the sum of the "
              "weights); an interval of width 0 means the design fixes that number (population sizes given).")
        data = {} if group is None else {group: found["grp"]}
        data.update({"population count": found["est"], "standard error": found["se"],
                     "population count 95 % CI low": found["low"], "population count 95 % CI high": found["high"],
                     "degrees of freedom": [found["df"]] * len(found["est"])})
        return self._survey_table(data)

    # ------------------------------------------------------------------ models and tests
    def _survey_explain(self, column, using, outcome):
        from . import survey_r
        from .summaries import _p_clause, _say_number

        word = "explain"
        design = self._survey_design(word)
        if not isinstance(column, str):
            raise SimplydataError('explain() needs the column to explain, like table.explain("score_2000", '
                                  'using=["free_meals"]).')
        using = [using] if isinstance(using, str) else list(using or [])
        if not using or not all(isinstance(u, str) for u in using):
            raise SimplydataError('explain() needs using=, the columns that explain it.'
                                  f'\nFor example:  table.explain("score_2000", using=["free_meals"])')
        self._need_columns(column, *using)
        families = {"numbers": ("gaussian", "linear model"), "yes or no": ("quasibinomial", "logistic model"),
                    "counts": ("quasipoisson", "Poisson model")}
        if outcome not in families:
            raise SimplydataError('Under a survey design, explain() takes outcome="numbers", "yes or no" or "counts".'
                                  f'\nFor example:  table.explain("met_target", using=["free_meals"], outcome="yes or no")')
        family, model = families[outcome]
        raw = self._frame[column].to_numpy()
        if outcome == "yes or no":
            kept = [v for v in raw if v is not None and not (isinstance(v, float) and np.isnan(v))]
            seen = sorted({str(v).strip().lower() for v in kept})
            if set(seen) <= {"yes", "no"}:
                y = np.array([np.nan if v is None or (isinstance(v, float) and np.isnan(v))
                              else float(str(v).strip().lower() == "yes") for v in raw])
            elif set(seen) <= {"0", "1", "0.0", "1.0", "true", "false"}:
                y = np.array([np.nan if v is None or (isinstance(v, float) and np.isnan(v))
                              else float(str(v).strip().lower() in ("1", "1.0", "true")) for v in raw])
            else:
                raise SimplydataError(f'outcome="yes or no" needs "{column}" to hold yes/no, 1/0 or True/False; make such '
                                      f'a column first with add_column.\nFor example:  '
                                      'table.explain("met_target", using=["free_meals"], outcome="yes or no")')
        else:
            y = self._survey_values(column)
        values = []
        for u in using:
            if self._frame.schema[u].is_numeric():
                values.append(self._frame[u].cast(nw.Float64).to_numpy())
            else:
                values.append(np.array([None if v is None else str(v) for v in self._frame[u].to_numpy()],
                                       dtype=object))
        found = survey_r.glm(design, len(self._frame), y, using, values, family)
        print(self._survey_header())
        print(f'A survey-weighted {model} of "{column}" from {", ".join(using)} ({found["n"]} rows; R '
              f"survey::svyglm(family = {family}()), t tests on {found['df']:g} degrees of freedom).")
        effect = {"gaussian": "change in " + column, "quasibinomial": "change in the log odds of yes",
                  "quasipoisson": "change in the log of the count"}[family]
        # text columns: R names each term column + level, against the first level in sorted order (R's factor)
        text = {u: sorted({str(v) for v in vals if v is not None}) for u, vals in zip(using, values)
                if vals.dtype == object}
        for i, term in enumerate(found["term"]):
            if term == "(Intercept)":
                continue
            name = term.strip("`")
            per = "per unit"
            for u, levels in text.items():
                if name.startswith(u) and name[len(u):] in levels[1:]:
                    per = f"for {u} {name[len(u):]} against {levels[0]}"
                    break
            print(f"  {name}: {_say_number(found['est'][i])} {effect} {per} (95 % CI "
                  f"{_say_number(found['low'][i])} to {_say_number(found['high'][i])}); "
                  + _p_clause(found["p"][i], if_none=f"{name} had no link to {column} in the population"))
        print("These are links in the population the survey describes, not proof of cause and effect.")
        return self._survey_table({"term": [t.strip("`") for t in found["term"]], "estimate": found["est"],
                                   "standard error": found["se"], "t": found["stat"],
                                   "degrees of freedom": [found["df"]] * len(found["term"]), "p-value": found["p"],
                                   "95 % CI low": found["low"], "95 % CI high": found["high"]})

    def _survey_compare_averages(self, column, for_each_group_in):
        from . import survey_r
        from .summaries import _p_sentence, _say_number

        word = "compare_averages_of"
        design = self._survey_design(word)
        if not isinstance(column, str):
            raise SimplydataError("compare_averages_of() needs the column first."
                                  f'\nFor example:  table.compare_averages_of("score_2000", for_each_group_in="award")')
        self._need_columns(column)
        group, g = self._survey_group(word, for_each_group_in, column)
        if group is None:
            raise SimplydataError("Under a survey design, compare_averages_of() needs for_each_group_in= with two "
                                  "groups.")
        kinds = sorted({v for v in g if v is not None})
        if len(kinds) != 2:
            raise SimplydataError(f'Under a survey design, compare_averages_of() compares two groups; "{group}" has '
                                  f"{len(kinds)}. For more groups use table.explain(\"{column}\", using=[\"{group}\"]).")
        y = self._survey_values(column)
        found = survey_r.ttest(design, len(self._frame), y, g)
        first, second = found["levels"]
        print(self._survey_header())
        print(f'The population average of "{column}" is {_say_number(found["diff"])} higher for {second} than for '
              f"{first} (95 % CI {_say_number(found['low'])} to {_say_number(found['high'])}; a negative number "
              "means lower).")
        print(_p_sentence(found["p"], if_none=f"{first} and {second} had the same average in the population"))
        print(f"Method: R survey::svyttest(): the design-based t test, t = {_say_number(found['t'])} on "
              f"{found['df']:g} degrees of freedom.")
        return self._survey_table({"group 1": [first], "group 2": [second], "difference": [found["diff"]],
                                   "difference 95 % CI low": [found["low"]], "difference 95 % CI high": [found["high"]],
                                   "t": [found["t"]], "degrees of freedom": [found["df"]], "p-value": [found["p"]]})

    def _survey_compare_counts(self, column, for_each_group_in):
        from . import survey_r
        from .summaries import _p_sentence, _say_number

        word = "compare_counts_of"
        design = self._survey_design(word)
        if not isinstance(column, str):
            raise SimplydataError("compare_counts_of() needs the column first."
                                  f'\nFor example:  table.compare_counts_of("award", for_each_group_in="school_type")')
        self._need_columns(column)
        group, g = self._survey_group(word, for_each_group_in, column)
        if group is None:
            raise SimplydataError("Under a survey design, compare_counts_of() needs for_each_group_in=."
                                  f'\nFor example:  table.compare_counts_of("award", for_each_group_in="school_type")')
        y = np.array([None if v is None or (isinstance(v, float) and np.isnan(v)) else str(v)
                      for v in self._frame[column].to_numpy()], dtype=object)
        found = survey_r.chisq(design, len(self._frame), y, g)
        print(self._survey_header())
        print(f'Do the shares of "{column}" differ between the groups of "{group}" in the population? '
              f"F = {_say_number(found['f'])} on {_say_number(found['ndf'])} and {_say_number(found['ddf'])} degrees "
              "of freedom.")
        print(_p_sentence(found["p"], if_none=f'the shares of "{column}" were the same in every group in the '
                                              "population", this="a difference in shares this big or bigger"))
        print("Method: R survey::svychisq(): Pearson's chi-square with the Rao-Scott correction for the design, as an "
              "F test.")
        return self._survey_table({"F": [found["f"]], "degrees of freedom": [found["ndf"]],
                                   "design degrees of freedom": [found["ddf"]], "p-value": [found["p"]]})
