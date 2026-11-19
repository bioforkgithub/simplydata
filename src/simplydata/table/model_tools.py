"""Words that work on a model from explain(): find_model_averages_of, check_model_of, show_rows_that_pull_model
and compare_models. They never change the table.

* find_model_averages_of("marks", for_each_group_in="school", using=["hours", "breakfast"]): the average the
  model gives for each group, with the number columns held at their averages and the other group
  columns counted equally, and every pair of groups compared with Tukey's adjustment. R
  emmeans::emmeans() and pairs() themselves (no Python package gives emmeans' reference grid),
  for every outcome of explain() (chances of each group for ordered groups and groups).
* check_model_of("marks", using=[...]): the four pictures of R plot(lm()), from statsmodels
  (OLSInfluence / GLMInfluence) and drawn with the chart words; with grouped_by= the pictures
  of R plot(lmer) and qqnorm(ranef()).
* show_rows_that_pull_model("marks", using=[...]): the rows that change the model most, by Cook's
  distance, with their leverage and studentised residual (statsmodels OLSInfluence /
  GLMInfluence, as R cooks.distance(), hatvalues() and rstudent()); with grouped_by= the
  groups, by R lme4 influence().
* compare_models("marks", using=["hours"], against=["hours", "breakfast"]): an F test (least
  squares, quasi-Poisson, Gamma) or a likelihood-ratio test (the other outcomes, and mixed models
  refitted by maximum likelihood) of the smaller model against the bigger one, as R
  anova(m0, m1), with AIC and BIC for each.
"""

from __future__ import annotations

import itertools
import math
import warnings

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .models import EXAMPLE, _list_words, _quoted, _r_name
from .stat_tests import _label, _num, _skipped_note, _whole
from .summaries import _p_clause, _p_shown

HELP_NONE = "the extra columns truly did not help"  # compare_models: the p-value sentence (W2)

# every outcome of explain(); emmeans follows each of their models
AVERAGE_OUTCOMES = ("numbers", "yes or no", "counts", "counts (overdispersed)", "counts that vary a lot",
                    "positive numbers", "shares", "counts with many zeros", "ordered groups", "groups")
# outcomes whose model the influence measures and pictures of R plot(glm()) cover (statsmodels GLMInfluence)
CHECK_OUTCOMES = ("numbers", "yes or no", "counts", "counts (overdispersed)", "counts that vary a lot",
                  "positive numbers")
MORE_OUTCOMES = ("ordered groups", "groups", "shares", "counts with many zeros")
AVERAGES_EXAMPLE = ('with sdata.get_example("school"): table.find_model_averages_of("marks", for_each_group_in="school", '
                    'using=["hours", "breakfast"])')
AVERAGE_WORDS = {"numbers": "average", "yes or no": "chance of yes", "counts": "average count",
                 "counts (overdispersed)": "average count", "counts that vary a lot": "average count",
                 "positive numbers": "average", "shares": "average share", "counts with many zeros": "average count",
                 "ordered groups": "chance", "groups": "chance"}
RATIO_PAIRS = {"yes or no": "odds ratio", "counts": "rate ratio", "counts (overdispersed)": "rate ratio",
               "counts that vary a lot": "rate ratio", "positive numbers": "ratio of averages"}
# emmeans' names for its degrees-of-freedom methods, as printed
DF_METHODS = {"kenward-roger": "Kenward-Roger", "satterthwaite": "Satterthwaite", "asymptotic": "asymptotic (z)"}


def model_call(model, pieces, grouped_by=None) -> str:
    """The R call of the model, for the method sentences."""
    formula = f"{_r_name(model['column'])} ~ " + " + ".join(pieces)
    family = "binomial" if model["outcome"] == "yes or no" else "poisson"
    g = _r_name(str(grouped_by)) if grouped_by is not None else ""
    inner = (model.get("grouping") or {}).get("inner")
    if inner:
        g = f"{g}/{_r_name(inner)}"
    return {"lm": f"lm({formula})", "binomial": f"glm({formula}, family = binomial)",
            "poisson": f"glm({formula}, family = poisson)",
            "quasipoisson": f"glm({formula}, family = quasipoisson)", "negbin": f"MASS::glm.nb({formula})",
            "gamma": f'glm({formula}, family = Gamma(link = "log"))', "shares": f"betareg::betareg({formula})",
            "zeros": f'pscl::zeroinfl({formula}, dist = "poisson")', "ordered": f"MASS::polr({formula})",
            "multinom": f"nnet::multinom({formula})", "mixed": f"lme4::lmer({formula} + (1 | {g}))",
            "glmm": f"lme4::glmer({formula} + (1 | {g}), family = {family})"}[model["kind"]]


def _correction_words(term, gg, within):
    """What the ANOVA line says about Greenhouse-Geisser: claimed only when afex applied it (epsilon finite
    and below 1). A repeated column with two groups has no epsilon (NaN): nothing to correct."""
    if not any(part in within for part in term.split(" : ")):
        return ""  # only independent groups in this term
    epsilon = gg.get(term, math.nan)
    if math.isfinite(epsilon) and epsilon < 1:
        return " (Greenhouse-Geisser corrected)"
    if math.isnan(epsilon):
        return " (two matched groups, so no correction is needed)"
    return " (Greenhouse-Geisser epsilon 1, so no correction is needed)"


class ModelToolWords:
    # ------------------------------------------------------------------ one checked model
    def _groups_inside(self, step, grouped_by):
        """grouped_by="school" or ["school", "class"] (classes inside schools): gives (outer, inner or None)."""
        return self._read_nested(step, grouped_by, None, "wald", "for the average group", False, None)

    def _one_model(self, step, column, using, outcome, grouped_by=None, in_order=None, inner=None):
        """Check the inputs as explain() does and fit the model (the rows with every cell given); the
        ordered-groups, groups, shares and many-zeros models are only set up (R fits them). inner= is the
        inner group column of grouped_by=[outer, inner]."""
        terms, pieces, variables, raw, missing, kinds = self._model_parts(
            step, column, using, outcome, grouped_by, "leave out")
        names = [column] + variables + ([grouped_by] if grouped_by is not None else [])
        if inner is not None:
            self._model_parts(step, column, using, outcome, inner, "leave out")  # the same checks for the inner column
            raw[inner], missing[inner], kinds[inner] = self._inner_column(inner)
            names.append(inner)
        keep = ~np.any([missing[nm] for nm in names], axis=0)
        _skipped_note(int((~keep).sum()), names)
        if outcome in MORE_OUTCOMES:
            return self._more_model(step, column, outcome, terms, variables, raw, kinds, keep, in_order), pieces
        if in_order is not None:
            raise SimplydataError('in_order= gives the order of the groups for outcome="ordered groups".')
        model = self._fit_model(step, column, outcome, grouped_by, terms, variables, raw, kinds, keep,
                                grouping={"inner": inner} if inner is not None else None)
        return model, pieces

    # ------------------------------------------------------------------ find_model_averages_of
    @friendly(renamed={"for_each": "for_each_group_in"})
    def find_model_averages_of(self, column=None, for_each_group_in=None, using=None, outcome="numbers", grouped_by=None,
                               in_order=None):
        """The average the model gives for each group, once the other columns are allowed for.

        table.find_model_averages_of("marks", for_each_group_in="school", using=["hours", "breakfast"])
        (with sdata.get_example("school"))
        The model is the one explain() fits from using= (for_each_group_in= is added if it is not in
        using=). Number columns are held at their averages and the other group columns are
        counted equally, so the groups are compared on an equal footing (adjusted averages,
        also called estimated marginal means). Then every pair of groups is compared, with
        Tukey's adjustment for making many comparisons. outcome="yes or no" gives the chance
        of yes in each group and odds ratios for the pairs; the count outcomes the average count
        and rate ratios; "positive numbers" the average and ratios; "shares" the average share;
        "ordered groups" and "groups" the chance of each of the outcome's groups (column "model chance"
        instead of "model average"). grouped_by= uses
        the mixed model (grouped_by=["school", "class"] for classes inside schools). Done by R emmeans::emmeans() and pairs() (needs R: pip install
        "simplydata[r]"). Gives back a table with one row per group and one per pair. Other name:
        marginal means (R emmeans).
        """
        step = "find_model_averages_of"
        grouped_by, inner = self._groups_inside(step, grouped_by)
        self._need_name(step, "the column to explain", column, AVERAGES_EXAMPLE)
        self._need_name(step, "for_each_group_in=", for_each_group_in, AVERAGES_EXAMPLE)
        self._need_columns(column, for_each_group_in)
        if outcome not in AVERAGE_OUTCOMES:
            self._check_choice(step, "outcome", outcome, AVERAGE_OUTCOMES)
        if using is None:
            using = [for_each_group_in]
        using = [using] if isinstance(using, str) else list(using) if isinstance(using, (list, tuple)) else using
        if not isinstance(using, list):
            raise SimplydataError(f"{step}() needs using= as a list of column names.\nFor example, {AVERAGES_EXAMPLE}")
        added = not any(for_each_group_in in [p.strip().strip("`") for p in item.replace("*", ":").split(":")]
                        for item in using if isinstance(item, str))
        if added:
            using = using + [for_each_group_in]
        model, pieces = self._one_model(step, column, using, outcome, grouped_by, in_order, inner=inner)
        if model["kinds"][for_each_group_in] != "group":
            raise SimplydataError(f'for_each_group_in="{for_each_group_in}" holds numbers; find_model_averages_of() gives an average for '
                                  "each group of a text (group) column. For a number column, explain() gives its "
                                  "slope.")
        from .models_r import emmeans_table

        out = emmeans_table(model, for_each_group_in)
        column_words = _quoted(column)
        chances = model["kind"] in ("ordered", "multinom")
        what = AVERAGE_WORDS[outcome]
        ratio = bool(np.atleast_1d(out["ratio"])[0])
        pair_what = RATIO_PAIRS.get(outcome, "ratio") if ratio else (
            "difference in chance" if chances else "difference")
        held = [v for v in model["variables"] if v != for_each_group_in and model["kinds"][v] == "number"]
        others = [v for v in model["variables"] if v != for_each_group_in and model["kinds"][v] == "group"]
        how = []
        if held:
            how.append(_list_words(f'"{v}" held at its average ({_num(float(np.mean(model["data"][v])))})'
                                   for v in held))
        if others:
            how.append(f"the groups of {_list_words(_quoted(v) for v in others)} counted equally")
        how_text = f", with {' and '.join(how)}" if how else ""
        # one block per group of the outcome (ordered groups, groups), otherwise a single block
        cls = [str(c) for c in out["cls"]] if chances else [None] * len(out["level"])
        pcls = [str(c) for c in out["pcls"]] if chances else [None] * len(out["contrast"])
        classes = list(dict.fromkeys(cls))
        levels = list(dict.fromkeys(str(v) for v in out["level"]))
        pairs = list(itertools.combinations(levels, 2))
        joiner = " / " if ratio else " - "
        if chances:
            print(f'Model chances of each {column_words} group for each "{for_each_group_in}" ({model["n"]} rows){how_text}:')
        else:
            print(f'Model averages of {column_words} for each "{for_each_group_in}" ({model["n"]} rows){how_text}:')
        for c in classes:
            indent = "  "
            if c is not None:
                print(f"  {column_words} {c}:")
                indent = "    "
            for i in (i for i in range(len(out["level"])) if cls[i] == c):
                print(f"{indent}{out['level'][i]}: {what} {_num(out['average'][i])} (95 % CI {_num(out['low'][i])} to "
                      f"{_num(out['high'][i])})")
        adjust = (f"Tukey's adjustment for {len(pairs)} comparisons" if len(pairs) > 1 else
                  "one pair, so nothing to adjust for")
        within = f" within each {column_words} group" if chances else ""
        if len(pairs) > 1:  # adjusted p-values are said plainly (W2)
            def pair_p(p):
                return "Tukey-adjusted " + _p_shown(p)
        else:
            def pair_p(p):
                return _p_clause(p, "the two groups truly did not differ")
        print(f"Each pair of groups ({pair_what}, {adjust}){within}:")
        word = "against" if ratio else "minus"
        # each pair from the groups themselves, in emmeans pairs() order (1-2, 1-3, ..., 2-3, ...) within each block:
        # emmeans' own labels cannot be split back when a group's name holds " - " or " / "
        contrasts = [pairs[i % len(pairs)] for i in range(len(out["contrast"]))]
        for i, (a, b) in enumerate(contrasts):
            where = f"{pcls[i]}: " if chances else ""
            print(f"  {where}{a} {word} {b}: {pair_what} {_num(out['difference'][i])} (95 % CI {_num(out['plow'][i])} "
                  f"to {_num(out['phigh'][i])}); {pair_p(float(out['p'][i]))}.")
        call = model_call(model, pieces, grouped_by)
        yes = f" ({model['yes_words']})" if model.get("yes_words") else ""
        spec = f"~ {_r_name(for_each_group_in)} | {_r_name(column)}" if chances else f"~ {_r_name(for_each_group_in)}"
        scale = ', mode = "prob"' if chances else "" if outcome == "numbers" else ', type = "response"'
        tukey = ", with Tukey's adjustment for the intervals and p-values of the pairs" if len(pairs) > 1 else ""
        df_words = ""
        if model["kind"] == "mixed":  # the method emmeans itself used, read from its summary
            method = DF_METHODS.get(out["df_method"], out["df_method"] or "unknown")
            df_words = f", {method} degrees of freedom (as emmeans chose them for {model['n']} rows)"
        print(f"Method: the model {call}{yes}, then R emmeans::emmeans(m, {spec}{scale}) and pairs(){tukey}"
              f"{df_words}.")
        if added:
            print(f'Note: "{for_each_group_in}" was not in using=, so it was added to the model.')
        if any(for_each_group_in in term and len(term) > 1 for term in model["terms"]):
            print(f'Note: "{for_each_group_in}" is part of an interaction, so its averages are averaged over the other '
                  "column in it; look at the interaction itself with explain() too.")
        if ratio:
            print(f"The pairs are ratios: 1 means no difference ({pair_what} of the first group to the second).")
        self._closing_words(out["p"])
        rows = []
        for i in range(len(out["level"])):
            row = {"term": str(out["level"][i])}
            if chances:
                row[f"{column} group"] = cls[i]
            row.update({"model chance" if chances else "model average": float(out["average"][i]),
                        "95 % CI low": float(out["low"][i]), "95 % CI high": float(out["high"][i]), "standard error": float(out["se"][i]),
                        "degrees of freedom": float(out["df"][i])})
            rows.append(row)
        for i, (a, b) in enumerate(contrasts):
            row = {"term": f"{a}{joiner}{b}"}
            if chances:
                row[f"{column} group"] = pcls[i]
            row.update({pair_what: float(out["difference"][i]), "95 % CI low": float(out["plow"][i]),
                        "95 % CI high": float(out["phigh"][i]), "standard error": float(out["pse"][i]),
                        "degrees of freedom": float(out["pdf"][i]), "statistic": float(out["stat"][i]),
                        "p-value (Tukey)": float(out["p"][i])})
            rows.append(row)
        return self._rows_table(rows)

    def _rows_table(self, rows):
        keys = list(dict.fromkeys(k for r in rows for k in r))
        data = {key: [r.get(key, math.nan) for r in rows] for key in keys}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    @staticmethod
    def _closing_words(p_values):
        if any(float(p) >= 0.05 for p in p_values):
            print("A large p-value does not show that there is no difference, only that the data cannot tell.")

    # ------------------------------------------------------------------ compare_averages_of(matched_by=)
    def _repeated_averages(self, column, for_each, matched_by):
        """compare_averages(..., matched_by=): a repeated-measures or mixed ANOVA, R afex::aov_ez()."""
        step = "compare_averages_of"
        example = ('with sdata.get_example("marks"): table.compare_averages_of("marks", for_each_group_in="subject", '
                   'matched_by="name")')
        self._need_name(step, "the column", column, example)
        columns = [for_each] if isinstance(for_each, str) else list(for_each) if isinstance(for_each, (list, tuple)) \
            else None
        if not columns or not all(isinstance(c, str) for c in columns):
            raise SimplydataError(f"{step}() needs for_each_group_in= with the group column (or a list of them).\n"
                                  f"For example, {example}")
        self._need_name(step, "matched_by=", matched_by, example)
        self._need_columns(column, matched_by, *columns)
        if len(set([column, matched_by, *columns])) < len(columns) + 2:
            raise SimplydataError("The column, for_each_group_in= and matched_by= must be different columns.")
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

        # each group goes to R as a plain code (L1, L2, ...) and comes back by name: afex makes R names of the
        # groups (make.names: "1" becomes "X1", "a b" becomes "a.b"), which are not the names in the table
        codes = {c: {g: f"L{i + 1}" for i, g in enumerate(sorted(set(groups[c])))} for c in columns}
        named = {c: {code: g for g, code in codes[c].items()} for c in columns}
        coded = {c: [codes[c][g] for g in groups[c]] for c in columns}
        out = repeated_anova(y, ids, {safe[c]: coded[c] for c in within}, {safe[c]: coded[c] for c in between})
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
        left_out = len(set(ids)) - subjects
        if left_out > 0:
            print(f'  ({left_out} "{matched_by}" left out by afex: not measured in every group; the averages below '
                  "are of the rest.)")
        long_y = np.atleast_1d(out["long_y"]).astype(float)
        for c in columns:  # the averages of the rows afex analysed (a$data$long), so people it left out are not in
            averages = {}
            for g, v in zip((named[c][str(x)] for x in np.atleast_1d(out[f"long_{safe[c]}"])), long_y):
                averages.setdefault(g, []).append(v)
            ordered = sorted(averages)
            print(f'  average "{column}" for each "{c}": '
                  + ", ".join(f"{g} {_num(float(np.mean(averages[g])))}" for g in ordered))
        rows = []
        for i, term in enumerate(terms):
            f, df1, df2 = float(out["f"][i]), float(out["numdf"][i]), float(out["dendf"][i])
            p, ges = float(out["p"][i]), float(out["ges"][i])
            interaction = " : " in term
            what = "the interaction " + term if interaction else f'"{term}"'
            null = ("the differences were truly the same in every group" if interaction
                    else "the averages truly did not differ")
            corrected = _correction_words(term, gg, within)
            print(f"  {what}: F = {_num(f)}, df = {_num(df1)} and {_num(df2)}{corrected}, generalised eta-squared "
                  f"{_num(ges)}; {_p_clause(p, null)}.")
            row = {"term": term, "statistic name": "F", "statistic": f, "degrees of freedom 1": df1,
                   "degrees of freedom 2": df2, "p-value": p, "generalised eta-squared": ges,
                   "Greenhouse-Geisser epsilon": gg.get(term, math.nan)}
            if term in sph:
                row.update({"Mauchly W": sph[term][0], "Mauchly p-value": sph[term][1]})
            rows.append(row)
        for term, (w, p) in sph.items():
            print(f"  Sphericity of {term} (Mauchly's test, W = {_num(w)}): {_p_clause(p, 'the spread of the differences was truly the same')}; "
                  "Greenhouse-Geisser epsilon "
                  f"{_num(gg.get(term, math.nan))}.")
        b = f", between = {_list_words(_quoted(c) for c in between)}" if between else ""
        if any(math.isfinite(e) and e < 1 for e in gg.values()):
            how = ("the degrees of freedom of the repeated groups are corrected with Greenhouse-Geisser's epsilon "
                   "(anova(correction = \"GG\")), which allows for repeated values being more alike in some pairs "
                   "of groups than others")
        elif all(len(set(groups[c])) == 2 for c in within):
            how = ("with two matched groups each person has one difference, so there is nothing for "
                   "Greenhouse-Geisser's correction to correct and the degrees of freedom are left as they are")
        else:
            how = ("Greenhouse-Geisser's epsilon is 1 (anova(correction = \"GG\")), so the degrees of freedom need "
                   "no correction")
        print(f'Method: R afex::aov_ez(id = "{matched_by}", dv = "{column}", within = '
              f"{_list_words(_quoted(c) for c in within)}{b}) with type 3 tests; {how}. Generalised "
              "eta-squared: the share of the differences explained.")
        if any(len(set(groups[c])) > 2 for c in within):
            first = within[0]
            print(f'To see which groups differ: table.find_model_averages_of("{column}", for_each_group_in="{first}", '
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
        family = {"binomial": "binomial", "negbin": "negbin", "gamma": "gamma"}.get(model["kind"], "poisson")
        return _glm(model["X"], model["y"], family, scale="X2" if model["kind"] in ("quasipoisson", "gamma") else None,
                    alpha=model["fit"].get("alpha"))

    def _check_kind(self, step, outcome, allowed=CHECK_OUTCOMES):
        if outcome not in allowed:
            self._check_choice(step, "outcome", outcome, allowed)

    @staticmethod
    def _influence(model, result):
        """Fitted values, residuals and influence measures, each as R gives them for plot(lm) and
        influence.measures(): statsmodels OLSInfluence (least squares) or GLMInfluence (GLMs)."""
        # GLMs: the hat values from the expected information (observed=False), as R hatvalues(); the same as
        # the observed one for the usual links of yes/no and counts, not for Gamma and negative binomial
        influence = result.get_influence() if model["kind"] == "lm" else result.get_influence(observed=False)
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

    @staticmethod
    def _qq(values):
        """R qqnorm() and qqline(): the normal quantiles of ppoints(n) ((i - a) / (n + 1 - 2a), a = 3/8 up to
        10 values, else 1/2; statsmodels ProbPlot) and the line through the first and third quartiles
        (quantile type 7, R's default)."""
        import statsmodels.api as sm
        from scipy import stats

        values = np.asarray(values, dtype=float)
        qq = sm.ProbPlot(values, a=3 / 8 if len(values) <= 10 else 0.5)
        q_y = np.percentile(values, [25, 75])
        q_x = stats.norm.ppf([0.25, 0.75])
        slope = float((q_y[1] - q_y[0]) / (q_x[1] - q_x[0]))
        return dict(theoretical=np.asarray(qq.theoretical_quantiles), ordered=np.asarray(qq.sorted_data),
                    slope=slope, intercept=float(q_y[0] - slope * q_x[0]))

    @staticmethod
    def _qq_chart(qq, y_name, title):
        import pandas as pd

        from ..chart import chart as make_chart

        frame = pd.DataFrame({"normal quantile": qq["theoretical"], y_name: qq["ordered"]})
        made = make_chart(frame).draw_dots(x="normal quantile", y=y_name)
        return made.draw_line_with_slope(qq["slope"], intercept=qq["intercept"]).write_title_on_top(title)

    # ------------------------------------------------------------------ check_model_of
    @friendly
    def check_model_of(self, column=None, using=None, outcome="numbers", grouped_by=None):
        """Four pictures to check a model from explain(), as R plot(lm(...)).

        table.check_model_of("marks", using=["hours", "breakfast"])   (with sdata.get_example("school"))
        1. Residuals against fitted values: the dots should lie in an even band around 0 with no
        curve (a curve means a straight line does not fit). 2. Normal Q-Q: the dots should lie
        on the line (the residuals follow a bell curve). 3. Scale-location: the line should be
        flat (the spread of the residuals is the same everywhere). 4. Residuals against leverage:
        rows outside the dashed Cook's distance lines pull the model strongly
        (show_rows_that_pull_model() lists them). The same options as explain(); outcome="yes or no",
        the count outcomes and "positive numbers" show the pictures of R plot(glm(...)). The
        numbers come from statsmodels (OLSInfluence, GLMInfluence), the LOWESS lines from
        statsmodels lowess (as R panel.smooth). With grouped_by= (a mixed model) the fourth
        picture is a normal Q-Q of the groups' own starting levels, as R qqnorm(ranef(m));
        grouped_by=["school", "class"] adds a fifth for the classes inside the schools. Without
        grouped_by= it also prints each column's variance inflation factor (how strongly it is
        linked with the others, as R car::vif()).
        Gives back the page of charts: .show() or .save("checks.png").
        """
        step = "check_model_of"
        self._check_kind(step, outcome)
        grouped_by, inner = self._groups_inside(step, grouped_by)
        model, pieces = self._one_model(step, column, using, outcome, grouped_by, inner=inner)
        if grouped_by is not None:
            return self._check_mixed_pictures(model, pieces, grouped_by)
        numbers = self._influence(model, self._statsmodels_fit(model))
        return self._check_pictures(model, pieces, numbers)

    def _check_pictures(self, model, pieces, numbers):
        import pandas as pd

        from ..chart import chart as make_chart
        from ..words.layout import put_in_rows_and_columns

        n, p = model["n"], model["X"].shape[1]
        # R qqnorm() of the standardised (deviance) residuals, and qqline()
        qq = self._qq(numbers["standardised"])
        x_name = numbers["x_name"]
        resid_name = "residual" if model["kind"] == "lm" else "Pearson residual"
        frame = pd.DataFrame({x_name: numbers["fitted"], resid_name: numbers["residual"],
                              "root of |standardised residual|": np.sqrt(np.abs(numbers["pearson"])),
                              "leverage": numbers["hat"], "standardised residual": numbers["pearson"]})
        a = make_chart(frame).draw_dots(x=x_name, y=resid_name).draw_smooth_line().draw_line_at_y(0)
        a = a.write_title_on_top("Residuals against fitted values")
        b = self._qq_chart(qq, "standardised residual", "Normal Q-Q")
        c = make_chart(frame).draw_dots(x=x_name, y="root of |standardised residual|").draw_smooth_line()
        c = c.write_title_on_top("Scale-location")
        d = make_chart(frame).draw_dots(x="leverage", y="standardised residual").draw_smooth_line().draw_line_at_y(0)
        positive = numbers["hat"][numbers["hat"] > 0]
        if len(positive) and float(positive.max()) > float(positive.min()):
            low, top = float(positive.min()), float(positive.max())
            for level in (0.5, 1):  # R plot.lm: Cook's distance contours at 0.5 and 1
                for sign in ("", "-"):
                    d = d.draw_curve(f"y = {sign}sqrt({level} * {p} * (1 - x) / x)", between=[low, top], dashed=True)
            # as R: the y range follows the residuals, so far-away contour lines are cut off
            spread = numbers["pearson"]
            reach = max(float(np.max(np.abs(spread))), 1.0) * 1.15
            d = d.set_range_y(-reach, reach)
        d = d.write_title_on_top("Residuals against leverage")
        column = model["column"]
        print(f'Checking the model of "{column}" ({n} rows) in four pictures, as R plot({model_call(model, pieces)}):')
        print("  1. residuals against fitted values: an even band around 0, with no curve, means the form fits;")
        print("  2. normal Q-Q: dots on the line mean the residuals follow a bell curve;")
        print("  3. scale-location: a flat line means the spread is the same everywhere;")
        print("  4. residuals against leverage: rows beyond the dashed lines (Cook's distance 0.5 and 1) pull "
              "the model strongly.")
        strong = int(np.sum(numbers["cooks"] > 0.5))
        if strong:
            print(f"Note: {strong} row{'s have' if strong != 1 else ' has'} a Cook's distance above 0.5; "
                  f'table.show_rows_that_pull_model("{column}", using=...) lists them.')
        if model["kind"] in ("binomial", "poisson", "quasipoisson", "negbin"):
            print("For yes/no and counts the first picture always shows bands (one per outcome value); look at the "
                  "smooth line, which should stay near 0.")
        print("Numbers from statsmodels (OLSInfluence or GLMInfluence); the smooth lines are LOWESS, as R "
              "panel.smooth. Pictures help judge a model better than tests of the residuals.")
        vif = self._vif_table(model)
        page = put_in_rows_and_columns(a, b, c, d, per_row=2)
        page._check_numbers = dict(numbers, theoretical=qq["theoretical"], ordered=qq["ordered"], slope=qq["slope"],
                                   intercept=qq["intercept"], vif=vif)
        return page

    @staticmethod
    def _vif_table(model):
        """How strongly each column is linked with the others: variance inflation factors as R car::vif().
        statsmodels variance_inflation_factor for least squares with one model column per column (the same
        numbers); R car::vif() itself for group columns with 3 or more groups (generalised VIF) and for GLMs
        (car uses the model's own covariance there). Gives back {column: (vif, df, vif ** (1 / (2 df)))}."""
        terms = model["terms"]
        if len(terms) < 2:
            return {}
        if any(len(term) > 1 for term in terms):
            print("Variance inflation factors are not given for a model with interactions: an interaction is linked "
                  "with its own columns by design (R car::vif() warns the same).")
            return {}
        one_column = all(len(model["parts_of"][j]) == 1 for j in range(1, model["X"].shape[1])) and             model["X"].shape[1] - 1 == len(terms)
        if model["kind"] == "lm" and one_column:
            from statsmodels.stats.outliers_influence import variance_inflation_factor

            values = {term[0]: (float(variance_inflation_factor(model["X"], j + 1)), 1.0, None)
                      for j, term in enumerate(terms)}
            how = "statsmodels variance_inflation_factor, as R car::vif()"
        else:
            from .._r import RMissing
            from .models_r import vif_r

            try:
                out = vif_r(model)
            except RMissing:
                print("The variance inflation factors of this model come from R car::vif() (needs R: pip install "
                      '"simplydata[r]"); left out here.')
                return {}
            values = {name: (float(v), float(df), float(adj) if df > 1 else None)
                      for name, v, df, adj in zip(out["names"], np.atleast_1d(out["vif"]), np.atleast_1d(out["df"]),
                                                  np.atleast_1d(out["adj"]))}
            how = "R car::vif() itself"
        parts = []
        for name, (v, df, adj) in values.items():
            extra = f" (generalised, {_whole(df)} df; {_num(adj)} on the scale of one column)" if adj is not None else ""
            parts.append(f'"{name}" {_num(v)}{extra}')
        print(f"How strongly each column is linked with the others (variance inflation factor, {how}): "
              f"{_list_words(parts)}. Above 5 a column's effect is hard to tell apart from the others'.")
        return values

    def _check_mixed_pictures(self, model, pieces, grouped_by):
        """The pictures for a mixed model: R plot(m) (residuals against fitted values), qqnorm() of the
        scaled residuals, scale-location, and qqnorm() of each group's own starting level (ranef)."""
        import pandas as pd

        from ..chart import chart as make_chart
        from ..words.layout import put_in_rows_and_columns

        fit, column, glmm = model["fit"], model["column"], model["kind"] == "glmm"
        if glmm:  # R residuals(m, type = "pearson") from lme4::glmer, against fitted(m) (the chance or count)
            residual = scaled = np.asarray(fit["pearson"], dtype=float)
            resid_name, scaled_name = "Pearson residual", "root of |Pearson residual|"
        else:  # R resid(m) and resid(m, scaled = TRUE): divided by the residual standard deviation
            residual = model["y"] - fit["fitted"]
            scaled = residual / math.sqrt(fit["within"])
            resid_name, scaled_name = "residual", "root of |scaled residual|"
        fitted = np.asarray(fit["fitted"], dtype=float)
        frame = pd.DataFrame({"fitted value": fitted, resid_name: residual, scaled_name: np.sqrt(np.abs(scaled))})
        charts = [make_chart(frame).draw_dots(x="fitted value", y=resid_name).draw_smooth_line().draw_line_at_y(0)
                  .write_title_on_top("Residuals against fitted values")]
        numbers = dict(fitted=fitted, residual=residual, scaled=scaled, ranef=np.asarray(fit["ranef"]),
                       ranef_groups=list(fit["ranef_groups"]))
        if not glmm:
            qq = self._qq(scaled)
            charts.append(self._qq_chart(qq, "scaled residual", "Normal Q-Q of the residuals"))
            numbers["residual_qq"] = qq
        charts.append(make_chart(frame).draw_dots(x="fitted value", y=scaled_name).draw_smooth_line().write_title_on_top("Scale-location"))
        levels = self._qq(numbers["ranef"])
        numbers["group_qq"] = levels
        charts.append(self._qq_chart(levels, "group's own level", f'Normal Q-Q of the "{grouped_by}" levels'))
        inner = (model.get("grouping") or {}).get("inner")
        if inner:  # groups inside groups: the inner groups' own levels too, R qqnorm(ranef(m)$`inner:outer`)
            numbers["inner_ranef"] = np.asarray(fit["inner_ranef"], dtype=float)
            numbers["inner_ranef_groups"] = list(fit["inner_ranef_groups"])
            numbers["inner_qq"] = self._qq(numbers["inner_ranef"])
            charts.append(self._qq_chart(numbers["inner_qq"], "group's own level",
                                         f'Normal Q-Q of the "{inner}" levels inside "{grouped_by}"'))
        groups = len(numbers["ranef_groups"])
        print(f'Checking the mixed model of "{column}" ({model["n"]} rows, {groups} groups in "{grouped_by}") in '
              f"{len(charts)} pictures, for m <- {model_call(model, pieces, grouped_by)}:")
        print("  1. residuals against fitted values (R plot(m)): an even band around 0, with no curve, means the form "
              "fits;")
        number = 2
        if not glmm:
            print("  2. normal Q-Q of the residuals (R qqnorm(resid(m, scaled = TRUE))): dots on the line mean the "
                  "residuals follow a bell curve;")
            number = 3
        print(f"  {number}. scale-location: a flat line means the spread is the same everywhere;")
        print(f"  {number + 1}. normal Q-Q of each group's own starting level (R qqnorm(ranef(m)${_r_name(grouped_by)}"
              "[, 1])): dots on the line mean the groups' levels follow a bell curve, as the model assumes" +
              (";" if inner else "."))
        if inner:
            print(f'  {number + 2}. the same for each "{inner}" group inside its "{grouped_by}" (R qqnorm(ranef(m)$'
                  f"`{_r_name(inner)}:{_r_name(grouped_by)}`[, 1])).")
        if glmm:
            print("For yes/no and counts a Q-Q picture of the residuals says little, so it is left out; the first "
                  "picture shows bands (one per outcome value): look at the smooth line, which should stay near 0.")
        how = ("R lme4::glmer() (residuals(m, type = \"pearson\"), fitted(), ranef())" if glmm else
               "statsmodels MixedLM (residuals, fitted values with each group's own level, and the levels "
               "themselves, as R resid(), fitted() and ranef())")
        print(f"Numbers from {how}; the smooth lines are LOWESS, as R panel.smooth. "
              f'table.show_rows_that_pull_model(..., grouped_by="{grouped_by}") shows the groups that pull the model.')
        page = put_in_rows_and_columns(*charts, per_row=2)
        page._check_numbers = numbers
        return page

    # ------------------------------------------------------------------ show_rows_that_pull_model
    @friendly
    def show_rows_that_pull_model(self, column=None, using=None, outcome="numbers", grouped_by=None):
        """Show the rows that change a model from explain() the most (the table does not change).

        table.show_rows_that_pull_model("marks", using=["hours", "breakfast"])   (with sdata.get_example("school"))
        Each row's Cook's distance says how much all the model's effects would move without
        that row; rows above 4 / (number of rows), the usual rule of thumb, are shown, the
        biggest first, with their leverage (how unusual the row's values in using= are) and
        their studentised residual (how far the row is from the model). Numbers from
        statsmodels OLSInfluence (GLMInfluence for outcome="yes or no", the count outcomes and
        "positive numbers"), as R cooks.distance(), hatvalues() and rstudent(). Each row is shown
        with its number in the whole table, so remove_rows_by_position() can follow, but only
        remove a row for a reason (a mistake in the data), and say so in the report.
        With grouped_by= (a mixed model) whole groups are checked instead: each group is left
        out in turn and the model refitted, R lme4 influence(m, groups =) and cooks.distance()
        (needs R).
        """
        step = "show_rows_that_pull_model"
        self._check_kind(step, outcome)
        grouped_by, inner = self._groups_inside(step, grouped_by)
        model, pieces = self._one_model(step, column, using, outcome, grouped_by, inner=inner)
        if grouped_by is not None:
            return self._groups_that_pull(model, pieces, grouped_by)
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

    def _groups_that_pull(self, model, pieces, grouped_by):
        """show_rows_that_pull_model(grouped_by=): Cook's distance of each whole group, R lme4 influence()."""
        from .models_r import group_influence

        out = group_influence(model)
        groups = [str(g) for g in np.atleast_1d(out["group"])]
        cooks = np.atleast_1d(out["cooks"]).astype(float)
        k = len(groups)
        limit = 4 / k
        order = [int(i) for i in np.argsort(-cooks, kind="stable") if cooks[i] > limit]
        sizes = {g: int(np.sum(model["groups"] == g)) for g in groups}
        print(f'Found {len(order)} of {k} groups in "{grouped_by}" with a Cook\'s distance above 4 / {k} = '
              f"{_num(limit)}:")
        for i in order[:10]:
            print(f"  {groups[i]} ({sizes[groups[i]]} rows): Cook's distance {_num(cooks[i])}")
        if len(order) > 10:
            print(f"  ... and {len(order) - 10} more groups above {_num(limit)}.")
        big = int(np.sum(cooks > 1))
        if big:
            print(f"{big} group{'s pull' if big != 1 else ' pulls'} very strongly (Cook's distance above 1): fit the "
                  "model with and without them and report both.")
        elif not order:
            top = int(np.argmax(cooks))
            print(f"No group pulls the model much (the largest: {groups[top]}, {_num(cooks[top])}).")
        print(f"Method: each group left out in turn and the model refitted, R lme4 influence(m, groups = "
              f'"{grouped_by}") and cooks.distance(), for m <- {model_call(model, pieces, grouped_by)}. With '
              "grouped_by= whole groups are checked, since the rows of a group belong together.")
        return None

    def _pull_numbers(self, model):
        return self._influence(model, self._statsmodels_fit(model))

    @staticmethod
    def _cell_words(value):
        if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
            return _num(value)
        return f'"{_label(value)}"'

    # ------------------------------------------------------------------ compare_models
    def _likelihood(self, model, fit_more=None):
        """(log-likelihood, values estimated) as R logLik() gives them, or (None, None) for quasi-Poisson,
        which has no likelihood. Mixed models are refitted by maximum likelihood, as R anova() does."""
        import statsmodels.api as sm

        kind, fit, p = model["kind"], model.get("fit"), model["X"].shape[1]
        if kind == "quasipoisson":
            return None, None
        if kind == "lm":
            return float(self._statsmodels_fit(model).llf), p + 1  # sigma counts, as R logLik()
        if kind == "glmm" and (model.get("grouping") or {}).get("inner"):
            return float(fit["loglik"]), p + 2  # two variances, as R logLik() of glmer((1 | g/h))
        if kind in ("binomial", "poisson", "negbin", "glmm"):
            return float(fit["loglik"]), p + (1 if kind in ("negbin", "glmm") else 0)
        if kind == "gamma":
            # as R logLik() of a Gamma glm: the dispersion taken as deviance / n, plus one value for it
            mu = np.asarray(fit["fitted"], dtype=float)
            llf = sm.families.Gamma(link=sm.families.links.Log()).loglike(model["y"], mu,
                                                                          scale=fit["deviance"] / model["n"])
            return float(llf), p + 1
        if kind == "mixed" and (model.get("grouping") or {}).get("inner"):
            from .models import _nested_mixed

            refit = _nested_mixed(model["X"], model["y"], model["groups"], model["grouping"]["inner_groups"],
                                  reml=False)
            return refit["loglik"], p + 3  # the three variances count, as R logLik()
        if kind == "mixed":
            from statsmodels.regression.mixed_linear_model import MixedLM

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = MixedLM(model["y"], model["X"], groups=model["groups"]).fit(
                    reml=False, method=["powell", "lbfgs"])
            return float(result.llf), p + 2  # the two variances count, as R logLik()
        # ordered groups, groups, shares, many zeros: the package's own log-likelihood and AIC
        return float(fit_more["loglik"]), int(round((fit_more["aic"] + 2 * fit_more["loglik"]) / 2))

    @friendly
    def compare_models(self, column=None, using=None, against=None, outcome="numbers", grouped_by=None,
                       in_order=None):
        """Does a bigger model explain the column better than a smaller one?

        table.compare_models("marks", using=["hours"], against=["hours", "breakfast"])
        (with sdata.get_example("school"))
        Fits both models on the same rows (those with a value in every column of either model).
        When one model holds every column of the other (nested models), it tests whether the
        extra columns help, as R anova(m0, m1): an F test for outcome="numbers" (statsmodels
        compare_f_test), "counts (overdispersed)" and "positive numbers" (R anova(test = "F")),
        and a likelihood-ratio test for the other outcomes. With grouped_by= both mixed models are
        fitted by maximum likelihood for the test, as R anova() refits lme4 models (also with
        grouped_by=["school", "class"], groups inside groups). It also prints
        AIC and BIC for each model (smaller is better; a difference under about 2 means little).
        Gives back a table with one row per model and one for the test.
        """
        from scipy import stats
        import statsmodels.tools.eval_measures as measures

        step = "compare_models"
        example = ('with sdata.get_example("school"): table.compare_models("marks", using=["hours"], '
                   'against=["hours", "breakfast"])')
        self._check_kind(step, outcome, AVERAGE_OUTCOMES)
        if against is None:
            raise SimplydataError(f"{step}() needs against= with the columns of the other model.\nFor example, {example}")
        grouped_by, inner = self._groups_inside(step, grouped_by)
        first = self._model_parts(step, column, using, outcome, grouped_by, "leave out")
        second = self._model_parts(step, column, against, outcome, grouped_by, "leave out")
        names = list(dict.fromkeys([column] + first[2] + second[2] + ([grouped_by] if grouped_by else [])))
        missing, kinds, raw = {**first[4], **second[4]}, {**first[5], **second[5]}, {**first[3], **second[3]}
        if inner is not None:  # groups inside groups: the inner column, checked as explain() does
            self._model_parts(step, column, using, outcome, inner, "leave out")
            raw[inner], missing[inner], kinds[inner] = self._inner_column(inner)
            names.append(inner)
        keep = ~np.any([missing[nm] for nm in names], axis=0)
        _skipped_note(int((~keep).sum()), names)
        if frozenset(frozenset(t) for t in first[0]) == frozenset(frozenset(t) for t in second[0]):
            raise SimplydataError("using= and against= give the same model; give against= the columns of the other "
                                  f"model.\nFor example, {example}")
        if outcome not in MORE_OUTCOMES and in_order is not None:
            raise SimplydataError('in_order= gives the order of the groups for outcome="ordered groups".')
        models = []
        for terms, pieces, variables in ((first[0], first[1], first[2]), (second[0], second[1], second[2])):
            fit_more = None
            if outcome in MORE_OUTCOMES:
                from . import models_more

                model = self._more_model(step, column, outcome, terms, variables, raw, kinds, keep, in_order)
                fit_more = {"ordered": models_more.fit_ordered, "multinom": models_more.fit_groups,
                            "shares": models_more.fit_shares, "zeros": models_more.fit_zeros}[model["kind"]](
                    model["X"], model["y"])
            else:
                model = self._fit_model(step, column, outcome, grouped_by, terms, variables, raw, kinds, keep,
                                        grouping={"inner": inner} if inner is not None else None)
            llf, k = self._likelihood(model, fit_more)
            models.append((model, pieces, llf, k))
        sets = [{frozenset(t) for t in m[0]["terms"]} for m in models]
        nested = sets[0] < sets[1] or sets[1] < sets[0]
        small, big = (models[0], models[1]) if len(sets[0]) <= len(sets[1]) else (models[1], models[0])
        n = small[0]["n"]
        rows = []
        where = f' in "{grouped_by}" groups' if grouped_by is not None else ""
        if inner is not None:
            where = f' in "{inner}" groups inside "{grouped_by}" groups'
        print(f'Comparing two models of "{column}" on the same {n} rows{where}:')
        for label, (model, pieces, llf, k) in (("using=", models[0]), ("against=", models[1])):
            formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
            if llf is None:
                print(f"  {label} {formula}")
                rows.append({"term": f"{label} {formula}"})
                continue
            aic, bic = float(measures.aic(llf, n, k)), float(measures.bic(llf, n, k))
            print(f"  {label} {formula}: AIC = {_num(aic)}, BIC = {_num(bic)} ({k} values estimated)")
            rows.append({"term": f"{label} {formula}", "AIC": aic, "BIC": bic, "values estimated": float(k),
                         "log-likelihood": llf})
        if models[0][2] is not None:
            better = 0 if rows[0]["AIC"] <= rows[1]["AIC"] else 1
            gap = abs(rows[0]["AIC"] - rows[1]["AIC"])
            close = "; a difference under 2 means the two fit about equally well" if gap < 2 else ""
            print(f"Lower AIC: the {('using=', 'against=')[better]} model (by {_num(gap)}{close}).")
            if grouped_by is not None:
                print("AIC and BIC of the mixed models come from maximum-likelihood fits, as R anova() gives them.")
        else:
            print("Quasi-Poisson has no likelihood, so there is no AIC or BIC (as R); the F test below compares the "
                  "models.")
        aic_words = "AIC and BIC as R AIC() and BIC()" if models[0][2] is not None else "no AIC (as R)"
        if not nested:
            print("Note: neither model holds every column of the other, so there is no test between them; compare "
                  "their AIC (smaller is better).")
            print(f"Method: both models fitted as {model_call(models[0][0], models[0][1], grouped_by)} and the other; "
                  f"{aic_words}.")
            return self._rows_table(rows)
        added = [t for t in big[0]["terms"] if frozenset(t) not in {frozenset(s) for s in small[0]["terms"]}]
        extra = ("Does " if len(added) == 1 else "Do ") + _list_words(_quoted(" : ".join(t)) for t in added)
        kind = big[0]["kind"]
        df = float(big[0]["X"].shape[1] - small[0]["X"].shape[1])
        if kind == "lm":
            f, p, df = self._statsmodels_fit(big[0]).compare_f_test(self._statsmodels_fit(small[0]))
            df2 = float(big[0]["fit"]["df"])
            print(f"{extra} help? F test (F = {_num(f)}, df = {_whole(df)} and {_whole(df2)}): "
                  f"{_p_clause(p, HELP_NONE)}.")
            test = {"statistic name": "F", "statistic": float(f), "degrees of freedom": float(df), "p-value": float(p)}
            how = "an F test, as R anova(m0, m1) (statsmodels compare_f_test)"
        elif kind in ("quasipoisson", "gamma"):
            # as R anova(m0, m1, test = "F"): the change in deviance per extra value over the bigger model's
            # (Pearson) dispersion
            change = small[0]["fit"]["deviance"] - big[0]["fit"]["deviance"]
            df2 = float(big[0]["fit"]["df"])
            f = change / df / big[0]["fit"]["dispersion"]
            p = float(stats.f.sf(f, df, df2))
            print(f"{extra} help? F test (F = {_num(f)}, df = {_whole(df)} and {_whole(df2)}): "
                  f"{_p_clause(p, HELP_NONE)}.")
            test = {"statistic name": "F", "statistic": float(f), "degrees of freedom": df, "p-value": p}
            how = 'an F test on the change in deviance, as R anova(m0, m1, test = "F")'
        else:
            if kind in ("binomial", "poisson"):
                chi = float(small[0]["fit"]["deviance"] - big[0]["fit"]["deviance"])
                how = 'a likelihood-ratio test, as R anova(m0, m1, test = "Chisq") (the change in deviance)'
            else:
                chi = float(2 * (big[2] - small[2]))
                df = float(big[3] - small[3])  # the values estimated (two parts or one per group: more than X)
                how = {"negbin": "a likelihood-ratio test, as R anova(m0, m1) for MASS::glm.nb models (theta found "
                                 "again for each)",
                       "mixed": "a likelihood-ratio test of the two models fitted by maximum likelihood (statsmodels "
                                "MixedLM), as R anova(m0, m1) refits lme4 models",
                       "glmm": "a likelihood-ratio test, as R anova(m0, m1) for lme4::glmer models",
                       "ordered": "a likelihood-ratio test, as R anova(m0, m1) for MASS::polr models",
                       "multinom": "a likelihood-ratio test, as R anova(m0, m1) for nnet::multinom models",
                       }.get(kind, "a likelihood-ratio test, as R lmtest::lrtest(m0, m1)")
            p = float(stats.chi2.sf(chi, df))
            print(f"{extra} help? Likelihood-ratio test (chi-square = {_num(chi)}, df = {_whole(df)}): "
                  f"{_p_clause(p, HELP_NONE)}.")
            test = {"statistic name": "chi-square", "statistic": chi, "degrees of freedom": df, "p-value": p}
        rows.append({"term": "test: the bigger model against the smaller", **test})
        print(f"Method: both models fitted as {model_call(big[0], big[1], grouped_by)} and the smaller one, then {how}; "
              f"{aic_words}.")
        if test["p-value"] >= 0.05:
            print("A large p-value does not show that the extra columns do nothing, only that the data cannot tell.")
        return self._rows_table(rows)
