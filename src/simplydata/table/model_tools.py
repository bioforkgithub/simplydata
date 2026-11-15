"""Words that work on a model from explain(): model_averages_of, check_model, show_rows_that_pull
and compare_models. They never change the table.

* model_averages_of("marks", for_each="school", using=["hours", "breakfast"]): the average the
  model gives for each group, with the number columns held at their averages and the other group
  columns counted equally, and every pair of groups compared with Tukey's adjustment. R
  emmeans::emmeans() and pairs() themselves (no Python package gives emmeans' reference grid).
* check_model("marks", using=[...]): the four pictures of R plot(lm()), from statsmodels
  (OLSInfluence / GLMInfluence) and drawn with the chart words.
* show_rows_that_pull("marks", using=[...]): the rows that change the model most, by Cook's
  distance, with their leverage and studentised residual (statsmodels OLSInfluence /
  GLMInfluence, as R cooks.distance(), hatvalues() and rstudent()).
* compare_models("marks", using=["hours"], against=["hours", "breakfast"]): an F test (least
  squares) or a likelihood-ratio test (yes/no, counts) of the smaller model against the bigger
  one, as R anova(m0, m1), with AIC and BIC for each (statsmodels).
"""

from __future__ import annotations

import itertools
import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .models import EXAMPLE, _list_words, _quoted, _r_name
from .stat_tests import _label, _num, _skipped_note, _whole
from .summaries import _p_words

AVERAGE_OUTCOMES = ("numbers", "yes or no", "counts")
AVERAGES_EXAMPLE = ('with sdata.example("school"): table.model_averages_of("marks", for_each="school", '
                    'using=["hours", "breakfast"])')


class ModelToolWords:
    # ------------------------------------------------------------------ one checked model
    def _one_model(self, step, column, using, outcome, grouped_by=None):
        """Check the inputs as explain() does and fit the model (the rows with every cell given)."""
        terms, pieces, variables, raw, missing, kinds = self._model_parts(
            step, column, using, outcome, grouped_by, "leave out")
        names = [column] + variables + ([grouped_by] if grouped_by is not None else [])
        keep = ~np.any([missing[nm] for nm in names], axis=0)
        _skipped_note(int((~keep).sum()), names)
        model = self._fit_model(step, column, outcome, grouped_by, terms, variables, raw, kinds, keep)
        return model, pieces

    # ------------------------------------------------------------------ model_averages_of
    @friendly
    def model_averages_of(self, column=None, for_each=None, using=None, outcome="numbers", grouped_by=None):
        """The average the model gives for each group, once the other columns are allowed for.

        table.model_averages_of("marks", for_each="school", using=["hours", "breakfast"])
        (with sdata.example("school"))
        The model is the one explain() fits from using= (for_each= is added if it is not in
        using=). Number columns are held at their averages and the other group columns are
        counted equally, so the groups are compared on an equal footing (adjusted averages,
        also called estimated marginal means). Then every pair of groups is compared, with
        Tukey's adjustment for making many comparisons. outcome="yes or no" gives the chance
        of yes in each group and odds ratios for the pairs; outcome="counts" the average count
        and rate ratios. grouped_by= uses the mixed model. Done by R emmeans::emmeans() and
        pairs() (needs R: pip install "simplydata[r]"). Gives back a table with one row per
        group and one per pair. Other name: marginal means (R emmeans).
        """
        step = "model_averages_of"
        self._need_name(step, "the column to explain", column, AVERAGES_EXAMPLE)
        self._need_name(step, "for_each=", for_each, AVERAGES_EXAMPLE)
        self._need_columns(column, for_each)
        if outcome not in AVERAGE_OUTCOMES:
            self._check_choice(step, "outcome", outcome, AVERAGE_OUTCOMES)
        if using is None:
            using = [for_each]
        using = [using] if isinstance(using, str) else list(using) if isinstance(using, (list, tuple)) else using
        if not isinstance(using, list):
            raise SimplydataError(f"{step}() needs using= as a list of column names.\nFor example, {AVERAGES_EXAMPLE}")
        added = not any(for_each in [p.strip().strip("`") for p in item.replace("*", ":").split(":")]
                        for item in using if isinstance(item, str))
        if added:
            using = using + [for_each]
        model, pieces = self._one_model(step, column, using, outcome, grouped_by)
        if model["kinds"][for_each] != "group":
            raise SimplydataError(f'for_each="{for_each}" holds numbers; model_averages_of() gives an average for '
                                  "each group of a text (group) column. For a number column, explain() gives its "
                                  "slope.")
        from .models_r import emmeans_table

        out = emmeans_table(model, for_each)
        levels = [str(v) for v in out["level"]]
        kind, column_words = model["kind"], _quoted(column)
        what = {"numbers": "average", "yes or no": "chance of yes", "counts": "average count"}[outcome]
        pair_what = {"numbers": "difference", "yes or no": "odds ratio", "counts": "rate ratio"}[outcome]
        held = [v for v in model["variables"] if v != for_each and model["kinds"][v] == "number"]
        others = [v for v in model["variables"] if v != for_each and model["kinds"][v] == "group"]
        how = []
        if held:
            how.append(_list_words(f'"{v}" held at its average ({_num(float(np.mean(model["data"][v])))})'
                                   for v in held))
        if others:
            how.append(f"the groups of {_list_words(_quoted(v) for v in others)} counted equally")
        how_text = f", with {' and '.join(how)}" if how else ""
        print(f'Model averages of {column_words} for each "{for_each}" ({model["n"]} rows){how_text}:')
        for i, level in enumerate(levels):
            print(f"  {level}: {what} {_num(out['average'][i])} (95 % CI {_num(out['low'][i])} to "
                  f"{_num(out['high'][i])})")
        pairs = list(itertools.combinations(levels, 2))
        joiner = "minus" if outcome == "numbers" else "against"
        adjust = (f"Tukey's adjustment for {len(pairs)} comparisons" if len(pairs) > 1 else
                  "one pair, so nothing to adjust for")
        print(f"Each pair of groups ({pair_what}, {adjust}):")
        for i, (a, b) in enumerate(pairs):
            print(f"  {a} {joiner} {b}: {pair_what} {_num(out['difference'][i])} (95 % CI {_num(out['plow'][i])} to "
                  f"{_num(out['phigh'][i])}); {_p_words(float(out['p'][i]))}.")
        formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
        call = {"lm": f"lm({formula})", "binomial": f"glm({formula}, family = binomial)",
                "poisson": f"glm({formula}, family = poisson)",
                "mixed": f"lme4::lmer({formula} + (1 | {_r_name(str(grouped_by))}))",
                "glmm": f"lme4::glmer({formula} + (1 | {_r_name(str(grouped_by))}), "
                        f"family = {'binomial' if outcome == 'yes or no' else 'poisson'})"}[kind]
        yes = f" ({model['yes_words']})" if model.get("yes_words") else ""
        scale = "" if outcome == "numbers" else ', type = "response"'
        tukey = ", with Tukey's adjustment for the intervals and p-values of the pairs" if len(pairs) > 1 else ""
        df_words = ", Kenward-Roger degrees of freedom" if kind == "mixed" else ""
        print(f"Method: the model {call}{yes}, then R emmeans::emmeans(m, ~ {_r_name(for_each)}{scale}) and "
              f"pairs(){tukey}{df_words}.")
        if added:
            print(f'Note: "{for_each}" was not in using=, so it was added to the model.')
        if any(for_each in term and len(term) > 1 for term in model["terms"]):
            print(f'Note: "{for_each}" is part of an interaction, so its averages are averaged over the other '
                  "column in it; look at the interaction itself with explain() too.")
        if outcome != "numbers":
            print(f"The pairs are ratios: 1 means no difference ({pair_what} of the first group to the second).")
        self._closing_words(out["p"])
        rows = []
        for i, level in enumerate(levels):
            rows.append({"term": level, "model average": float(out["average"][i]), "95 % CI low": float(out["low"][i]),
                         "95 % CI high": float(out["high"][i]), "standard error": float(out["se"][i]),
                         "degrees of freedom": float(out["df"][i])})
        for i, (a, b) in enumerate(pairs):
            rows.append({"term": f"{a} {'-' if outcome == 'numbers' else '/'} {b}", pair_what: float(out["difference"][i]),
                         "95 % CI low": float(out["plow"][i]), "95 % CI high": float(out["phigh"][i]),
                         "standard error": float(out["pse"][i]), "degrees of freedom": float(out["pdf"][i]),
                         "statistic": float(out["stat"][i]), "p-value (Tukey)": float(out["p"][i])})
        return self._rows_table(rows)

    def _rows_table(self, rows):
        keys = list(dict.fromkeys(k for r in rows for k in r))
        data = {key: [r.get(key, math.nan) for r in rows] for key in keys}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    @staticmethod
    def _closing_words(p_values):
        if any(float(p) >= 0.05 for p in p_values):
            print("A large p-value does not show that there is no difference, only that the data cannot tell.")

    # ------------------------------------------------------------------ compare_averages(matched_by=)
    def _repeated_averages(self, column, for_each, matched_by):
        """compare_averages(..., matched_by=): a repeated-measures or mixed ANOVA, R afex::aov_ez()."""
        step = "compare_averages"
        example = ('with sdata.example("marks"): table.compare_averages("marks", for_each="subject", '
                   'matched_by="name")')
        self._need_name(step, "the column", column, example)
        columns = [for_each] if isinstance(for_each, str) else list(for_each) if isinstance(for_each, (list, tuple)) \
            else None
        if not columns or not all(isinstance(c, str) for c in columns):
            raise SimplydataError(f"{step}() needs for_each= with the group column (or a list of them).\n"
                                  f"For example, {example}")
        self._need_name(step, "matched_by=", matched_by, example)
        self._need_columns(column, matched_by, *columns)
        if len(set([column, matched_by, *columns])) < len(columns) + 2:
            raise SimplydataError("The column, for_each= and matched_by= must be different columns.")
        frame = self._frame
        if not frame.schema[column].is_numeric():
            raise SimplydataError(f'compare_averages() needs numbers in "{column}".')
        values = frame[column].cast(nw.Float64).to_numpy().astype(float)
        ids = frame[matched_by].to_list()
        groups = {c: frame[c].to_list() for c in columns}
        empty = np.isnan(values) | np.array([v is None for v in ids])
        for c in columns:
            empty |= np.array([v is None or (isinstance(v, float) and math.isnan(v)) for v in groups[c]])
        _skipped_note(int(empty.sum()), [column, matched_by, *columns])
        keep = ~empty
        y = values[keep]
        ids = [str(v) for v, k in zip(ids, keep) if k]
        groups = {c: [_label(v) for v, k in zip(groups[c], keep) if k] for c in columns}
        within, between = [], []
        for c in columns:
            seen = {}
            for person, g in zip(ids, groups[c]):
                seen.setdefault(person, set()).add(g)
            if len(set(groups[c])) < 2:
                raise SimplydataError(f'"{c}" needs at least 2 groups.')
            (between if all(len(v) == 1 for v in seen.values()) else within).append(c)
        if not within:
            raise SimplydataError(f'Each "{matched_by}" is in only one group of {_list_words(_quoted(c) for c in columns)}, '
                                  "so nothing is matched. Leave out matched_by= to compare independent groups.")
        safe = {c: f"f{i}" for i, c in enumerate(columns)}
        from .models_r import repeated_anova

        out = repeated_anova(y, ids, {safe[c]: groups[c] for c in within}, {safe[c]: groups[c] for c in between})
        back = {v: k for k, v in safe.items()}

        def name(term):
            return " : ".join(back.get(p, p) for p in str(term).split(":"))

        terms = [name(t) for t in np.atleast_1d(out["term"])]
        gg = dict(zip((name(t) for t in np.atleast_1d(out["gg_term"])), np.atleast_1d(out["gg"]).astype(float)))
        sph = {name(t): (float(w), float(p)) for t, w, p in zip(np.atleast_1d(out["sph_term"]),
                                                                  np.atleast_1d(out["sph_w"]),
                                                                  np.atleast_1d(out["sph_p"]))}
        subjects = int(np.atleast_1d(out["subjects"])[0])
        kind = "repeated-measures ANOVA" if not between else "mixed ANOVA (repeated and independent groups)"
        print(f'Comparing the average "{column}" with a {kind}: {subjects} "{matched_by}" each measured in every '
              f"group of {_list_words(_quoted(c) for c in within)}"
              + (f", in groups of {_list_words(_quoted(c) for c in between)}" if between else "") + ".")
        for c in columns:
            averages = {}
            for g, v in zip(groups[c], y):
                averages.setdefault(g, []).append(v)
            ordered = sorted(averages)
            print(f'  average "{column}" for each "{c}": '
                  + ", ".join(f"{g} {_num(float(np.mean(averages[g])))}" for g in ordered))
        rows = []
        for i, term in enumerate(terms):
            f, df1, df2 = float(out["f"][i]), float(out["numdf"][i]), float(out["dendf"][i])
            p, ges = float(out["p"][i]), float(out["ges"][i])
            what = "the interaction " + term if " : " in term else f'"{term}"'
            corrected = " (Greenhouse-Geisser corrected)" if term in gg else ""
            print(f"  {what}: F = {_num(f)}, df = {_num(df1)} and {_num(df2)}{corrected}, generalised eta-squared "
                  f"{_num(ges)}; {_p_words(p)}.")
            row = {"term": term, "statistic name": "F", "statistic": f, "degrees of freedom 1": df1,
                   "degrees of freedom 2": df2, "p-value": p, "generalised eta-squared": ges,
                   "Greenhouse-Geisser epsilon": gg.get(term, math.nan)}
            if term in sph:
                row.update({"Mauchly W": sph[term][0], "Mauchly p-value": sph[term][1]})
            rows.append(row)
        for term, (w, p) in sph.items():
            print(f"  Sphericity of {term} (Mauchly's test, W = {_num(w)}): {_p_words(p)}; Greenhouse-Geisser epsilon "
                  f"{_num(gg.get(term, math.nan))}.")
        b = f", between = {_list_words(_quoted(c) for c in between)}" if between else ""
        print(f'Method: R afex::aov_ez(id = "{matched_by}", dv = "{column}", within = '
              f"{_list_words(_quoted(c) for c in within)}{b}) with type 3 tests; the degrees of freedom of the "
              "repeated groups are corrected with Greenhouse-Geisser's epsilon (anova(correction = \"GG\")), which "
              "allows for repeated values being more alike in some pairs of groups than others. Generalised "
              "eta-squared: the share of the differences explained.")
        if any(len(set(groups[c])) > 2 for c in within):
            first = within[0]
            print(f'To see which groups differ: table.model_averages_of("{column}", for_each="{first}", '
                  f'grouped_by="{matched_by}").')
        self._closing_words([r["p-value"] for r in rows])
        return self._rows_table(rows)

    # ------------------------------------------------------------------ statsmodels results of a model
    @staticmethod
    def _statsmodels_fit(model):
        """The same model as a statsmodels results object (OLS or GLM), for its influence measures."""
        import statsmodels.api as sm

        from .models import _glm

        if model["kind"] == "lm":
            return sm.OLS(model["y"], model["X"]).fit(method="qr")
        return _glm(model["X"], model["y"], model["kind"])

    def _check_kind(self, step, outcome, grouped_by):
        if outcome not in AVERAGE_OUTCOMES:
            self._check_choice(step, "outcome", outcome, AVERAGE_OUTCOMES)
        if grouped_by is not None:
            raise SimplydataError(f"{step}() works on models without grouped_by= for now; for a mixed model, look "
                                  "at the rows within each group with a chart.")

    @staticmethod
    def _influence(model, result):
        """Fitted values, residuals and influence measures, each as R gives them for plot(lm) and
        influence.measures(): statsmodels OLSInfluence (least squares) or GLMInfluence (GLMs)."""
        influence = result.get_influence()
        hat = np.asarray(influence.hat_matrix_diag)
        cooks = np.asarray(influence.cooks_distance[0])
        if model["kind"] == "lm":
            return dict(fitted=np.asarray(result.fittedvalues), residual=np.asarray(result.resid),
                        standardised=np.asarray(influence.resid_studentized_internal),
                        pearson=np.asarray(influence.resid_studentized_internal),
                        studentised=np.asarray(influence.resid_studentized_external), hat=hat, cooks=cooks,
                        x_name="fitted value")
        # GLMs, as R 4.6 plot(glm): Pearson residuals against the linear predictor; standardised deviance
        # residuals (R rstandard(type = "deviance")) for the Q-Q picture; standardised Pearson residuals
        # (R rstandard(type = "pearson"), statsmodels resid_studentized) for scale-location and leverage
        pearson = np.asarray(influence.resid_studentized)
        deviance = np.asarray(result.resid_deviance)
        return dict(fitted=np.asarray(result.predict(which="linear")), residual=np.asarray(result.resid_pearson),
                    standardised=deviance / np.sqrt(float(result.scale) * (1 - hat)),
                    pearson=pearson, studentised=None, hat=hat, cooks=cooks,
                    x_name="predicted value (on the link scale)")

    # ------------------------------------------------------------------ check_model
    @friendly
    def check_model(self, column=None, using=None, outcome="numbers"):
        """Four pictures to check a model from explain(), as R plot(lm(...)).

        table.check_model("marks", using=["hours", "breakfast"])   (with sdata.example("school"))
        1. Residuals against fitted values: the dots should lie in an even band around 0 with no
        curve (a curve means a straight line does not fit). 2. Normal Q-Q: the dots should lie
        on the line (the residuals follow a bell curve). 3. Scale-location: the line should be
        flat (the spread of the residuals is the same everywhere). 4. Residuals against leverage:
        rows outside the dashed Cook's distance lines pull the model strongly
        (show_rows_that_pull() lists them). The same options as explain(); outcome="yes or no"
        and "counts" show the pictures of R plot(glm(...)). The numbers come from statsmodels
        (OLSInfluence, GLMInfluence), the LOWESS lines from statsmodels lowess (as R
        panel.smooth). Gives back the page of four charts: .show() or .save("checks.png").
        """
        step = "check_model"
        self._check_kind(step, outcome, None)
        model, pieces = self._one_model(step, column, using, outcome)
        numbers = self._influence(model, self._statsmodels_fit(model))
        return self._check_pictures(model, pieces, numbers)

    def _check_pictures(self, model, pieces, numbers):
        import pandas as pd
        import statsmodels.api as sm
        from scipy import stats

        from ..chart import chart as make_chart
        from ..words.layout import grid

        n, p = model["n"], model["X"].shape[1]
        # R qqnorm() of the standardised (deviance) residuals: the normal quantiles of ppoints(n), (i - a) / (n + 1 - 2a) with a = 3/8 up to 10 rows, else 1/2
        standardised = numbers["standardised"]
        qq = sm.ProbPlot(standardised, a=3 / 8 if n <= 10 else 0.5)
        theoretical, ordered = np.asarray(qq.theoretical_quantiles), np.asarray(qq.sorted_data)
        # R qqline(): the line through the first and third quartiles (quantile type 7, R's default)
        q_y = np.percentile(standardised, [25, 75])
        q_x = stats.norm.ppf([0.25, 0.75])
        slope = float((q_y[1] - q_y[0]) / (q_x[1] - q_x[0]))
        intercept = float(q_y[0] - slope * q_x[0])
        x_name = numbers["x_name"]
        resid_name = "residual" if model["kind"] == "lm" else "Pearson residual"
        frame = pd.DataFrame({x_name: numbers["fitted"], resid_name: numbers["residual"],
                              "root of |standardised residual|": np.sqrt(np.abs(numbers["pearson"])),
                              "leverage": numbers["hat"], "standardised residual": numbers["pearson"]})
        a = make_chart(frame).dots(x=x_name, y=resid_name).smooth_line().line_at_y(0)
        a = a.title_top("Residuals against fitted values")
        b = make_chart(pd.DataFrame({"normal quantile": theoretical, "standardised residual": ordered}))
        b = b.dots(x="normal quantile", y="standardised residual").line_with_slope(slope, intercept=intercept)
        b = b.title_top("Normal Q-Q")
        c = make_chart(frame).dots(x=x_name, y="root of |standardised residual|").smooth_line()
        c = c.title_top("Scale-location")
        d = make_chart(frame).dots(x="leverage", y="standardised residual").smooth_line().line_at_y(0)
        positive = numbers["hat"][numbers["hat"] > 0]
        if len(positive) and float(positive.max()) > float(positive.min()):
            low, top = float(positive.min()), float(positive.max())
            for level in (0.5, 1):  # R plot.lm: Cook's distance contours at 0.5 and 1
                for sign in ("", "-"):
                    d = d.curve(f"y = {sign}sqrt({level} * {p} * (1 - x) / x)", between=[low, top], dashed=True)
            # as R: the y range follows the residuals, so far-away contour lines are cut off
            spread = numbers["pearson"]
            reach = max(float(np.max(np.abs(spread))), 1.0) * 1.15
            d = d.range_y(-reach, reach)
        d = d.title_top("Residuals against leverage")
        column = model["column"]
        formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
        call = {"lm": f"lm({formula})", "binomial": f"glm({formula}, family = binomial)",
                "poisson": f"glm({formula}, family = poisson)"}[model["kind"]]
        print(f'Checking the model of "{column}" ({n} rows) in four pictures, as R plot({call}):')
        print("  1. residuals against fitted values: an even band around 0, with no curve, means the form fits;")
        print("  2. normal Q-Q: dots on the line mean the residuals follow a bell curve;")
        print("  3. scale-location: a flat line means the spread is the same everywhere;")
        print("  4. residuals against leverage: rows beyond the dashed lines (Cook's distance 0.5 and 1) pull "
              "the model strongly.")
        strong = int(np.sum(numbers["cooks"] > 0.5))
        if strong:
            print(f"Note: {strong} row{'s have' if strong != 1 else ' has'} a Cook's distance above 0.5; "
                  f'table.show_rows_that_pull("{column}", using=...) lists them.')
        if model["kind"] != "lm":
            print("For yes/no and counts the first picture always shows bands (one per outcome value); look at the "
                  "smooth line, which should stay near 0.")
        print("Numbers from statsmodels (OLSInfluence or GLMInfluence); the smooth lines are LOWESS, as R "
              "panel.smooth. Pictures help judge a model better than tests of the residuals.")
        page = grid(a, b, c, d, per_row=2)
        page._check_numbers = dict(numbers, theoretical=theoretical, ordered=ordered, slope=slope,
                                   intercept=intercept)
        return page

    # ------------------------------------------------------------------ show_rows_that_pull
    @friendly
    def show_rows_that_pull(self, column=None, using=None, outcome="numbers"):
        """Show the rows that change a model from explain() the most (the table does not change).

        table.show_rows_that_pull("marks", using=["hours", "breakfast"])   (with sdata.example("school"))
        Each row's Cook's distance says how much all the model's effects would move without
        that row; rows above 4 / (number of rows), the usual rule of thumb, are shown, the
        biggest first, with their leverage (how unusual the row's values in using= are) and
        their studentised residual (how far the row is from the model). Numbers from
        statsmodels OLSInfluence (GLMInfluence for outcome="yes or no" and "counts"), as R
        cooks.distance(), hatvalues() and rstudent(). Each row is shown with its number in the
        whole table, so remove_rows_by_position() can follow, but only remove a row for a reason
        (a mistake in the data), and say so in the report.
        """
        step = "show_rows_that_pull"
        self._check_kind(step, outcome, None)
        model, _ = self._one_model(step, column, using, outcome)
        numbers = self._pull_numbers(model)
        positions = np.flatnonzero(model["keep"])
        n, cooks = model["n"], numbers["cooks"]
        limit = 4 / n
        order = [int(i) for i in np.argsort(-cooks, kind="stable") if cooks[i] > limit]
        lm = numbers["studentised"] is not None
        residual_name = "studentised residual" if lm else "standardised residual"
        residuals = numbers["studentised"] if lm else numbers["pearson"]
        print(f"Found {len(order)} of {n} rows with a Cook's distance above 4 / {n} = {_num(limit)}:")
        shown = order[:10]
        for i in shown:
            values = ", ".join(f"{v} {self._cell_words(model['data'][v][i])}" for v in model["variables"])
            y = self._frame[column][int(positions[i])]
            print(f"  row {positions[i] + 1}: {column} {self._cell_words(y)}, {values}: Cook's distance "
                  f"{_num(cooks[i])}, leverage {_num(numbers['hat'][i])}, {residual_name} {_num(residuals[i])}")
        if len(order) > len(shown):
            print(f"  ... and {len(order) - len(shown)} more rows above {_num(limit)}.")
        big = int(np.sum(cooks > 1))
        if big:
            print(f"{big} row{'s pull' if big != 1 else ' pulls'} very strongly (Cook's distance above 1): fit the "
                  "model with and without them and report both.")
        elif not order:
            print("No row pulls the model much.")
        print(f"Leverage: how unusual a row's values in using= are (the average is {_num(model['X'].shape[1] / n)}). "
              f"{residual_name.capitalize()}: how far the row lies from the model, in standard errors (beyond 2 or "
              "3 is unusual).")
        how = "OLSInfluence" if lm else "GLMInfluence"
        what = "cooks.distance(), hatvalues() and rstudent()" if lm else \
            'cooks.distance(), hatvalues() and rstandard(type = "pearson")'
        print(f"Method: statsmodels {how}, as R {what}. The row numbers count from 1 in the whole table; remove a "
              "row only for a reason (a mistake in the data), and say so.")
        return None

    def _pull_numbers(self, model):
        return self._influence(model, self._statsmodels_fit(model))

    @staticmethod
    def _cell_words(value):
        if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
            return _num(value)
        return f'"{_label(value)}"'

    # ------------------------------------------------------------------ compare_models
    @friendly
    def compare_models(self, column=None, using=None, against=None, outcome="numbers"):
        """Does a bigger model explain the column better than a smaller one, or could it be chance?

        table.compare_models("marks", using=["hours"], against=["hours", "breakfast"])
        (with sdata.example("school"))
        Fits both models on the same rows (those with a value in every column of either model).
        When one model holds every column of the other (nested models), it tests whether the
        extra columns help: an F test for outcome="numbers" (statsmodels compare_f_test) and a
        likelihood-ratio test for outcome="yes or no" and "counts", as R anova(m0, m1). It also
        prints AIC and BIC for each model (smaller is better; a difference under about 2 means
        little). Gives back a table with one row per model and one for the test.
        """
        from scipy import stats
        import statsmodels.tools.eval_measures as measures

        step = "compare_models"
        example = ('with sdata.example("school"): table.compare_models("marks", using=["hours"], '
                   'against=["hours", "breakfast"])')
        self._check_kind(step, outcome, None)
        if against is None:
            raise SimplydataError(f"{step}() needs against= with the columns of the other model.\nFor example, {example}")
        first = self._model_parts(step, column, using, outcome, None, "leave out")
        second = self._model_parts(step, column, against, outcome, None, "leave out")
        names = list(dict.fromkeys([column] + first[2] + second[2]))
        missing, kinds, raw = {**first[4], **second[4]}, {**first[5], **second[5]}, {**first[3], **second[3]}
        keep = ~np.any([missing[nm] for nm in names], axis=0)
        _skipped_note(int((~keep).sum()), names)
        models = []
        for terms, pieces, variables in ((first[0], first[1], first[2]), (second[0], second[1], second[2])):
            model = self._fit_model(step, column, outcome, None, terms, variables, raw, kinds, keep)
            models.append((model, pieces, self._statsmodels_fit(model)))
        sets = [{frozenset(t) for t in m[0]["terms"]} for m in models]
        if sets[0] == sets[1]:
            raise SimplydataError("using= and against= give the same model; give against= the columns of the other "
                                  f"model.\nFor example, {example}")
        nested = sets[0] < sets[1] or sets[1] < sets[0]
        small, big = (models[0], models[1]) if len(sets[0]) <= len(sets[1]) else (models[1], models[0])
        rows = []
        print(f'Comparing two models of "{column}" on the same {small[0]["n"]} rows:')
        for label, (model, pieces, result) in (("using=", models[0]), ("against=", models[1])):
            k = model["X"].shape[1] + (1 if model["kind"] == "lm" else 0)  # as R logLik(): sigma counts for lm
            llf = float(result.llf)
            aic, bic = float(measures.aic(llf, model["n"], k)), float(measures.bic(llf, model["n"], k))
            formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
            print(f"  {label} {formula}: AIC = {_num(aic)}, BIC = {_num(bic)} ({k} values estimated)")
            rows.append({"term": f"{label} {formula}", "AIC": aic, "BIC": bic, "values estimated": float(k),
                         "log-likelihood": llf})
        better = 0 if rows[0]["AIC"] <= rows[1]["AIC"] else 1
        gap = abs(rows[0]["AIC"] - rows[1]["AIC"])
        close = "; a difference under 2 means the two fit about equally well" if gap < 2 else ""
        print(f"Lower AIC: the {('using=', 'against=')[better]} model (by {_num(gap)}{close}).")
        if nested:
            added = [t for t in big[0]["terms"] if frozenset(t) not in {frozenset(s) for s in small[0]["terms"]}]
            extra = ("Does " if len(added) == 1 else "Do ") + _list_words(_quoted(" : ".join(t)) for t in added)
            if big[0]["kind"] == "lm":
                f, p, df = big[2].compare_f_test(small[2])
                df2 = float(big[2].df_resid)
                print(f"{extra} help? F test (F = {_num(f)}, df = {_whole(df)} and {_whole(df2)}): {_p_words(p)}.")
                test = {"statistic name": "F", "statistic": float(f), "degrees of freedom": float(df),
                        "p-value": float(p)}
                how = "an F test, as R anova(m0, m1) (statsmodels compare_f_test)"
            else:
                chi = float(small[2].deviance - big[2].deviance)
                df = float(big[0]["X"].shape[1] - small[0]["X"].shape[1])
                p = float(stats.chi2.sf(chi, df))
                print(f"{extra} help? Likelihood-ratio test (chi-square = {_num(chi)}, df = {_whole(df)}): "
                      f"{_p_words(p)}.")
                test = {"statistic name": "chi-square", "statistic": chi, "degrees of freedom": df, "p-value": p}
                how = 'a likelihood-ratio test, as R anova(m0, m1, test = "Chisq") (the change in deviance)'
            rows.append({"term": "test: the bigger model against the smaller", **test})
            print(f"Method: both models fitted with statsmodels, then {how}; AIC and BIC as R AIC() and BIC().")
            if p >= 0.05:
                print("A large p-value does not show that the extra columns do nothing, only that the data cannot "
                      "tell.")
        else:
            print("Note: neither model holds every column of the other, so there is no test between them; compare "
                  "their AIC (smaller is better).")
            print("Method: both models fitted with statsmodels; AIC and BIC as R AIC() and BIC().")
        return self._rows_table(rows)
