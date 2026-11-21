"""Hidden factors (phase S3c-2): table.find_hidden_factors_behind and table.check_hidden_factors.

Many columns (the answers to a questionnaire, the scores of several tests) can go together because a few things
that were not measured lie behind them: hidden (latent) factors. find_hidden_factors_behind explores how many there
are and which columns go with which (exploratory factor analysis, R psych); check_hidden_factors checks a model the
learner writes down beforehand (confirmatory factor analysis, R lavaan). Every number comes from R
(table/factor_r.py); simplydata checks the columns, chooses and prints the defaults, and words the answer
(design_evidence_private/s3c_design.md, items Q11/Y06 and Q12, with the independent review of 2026-11-20).

* simplydata chooses (find_hidden_factors_behind): minres (psych's default), oblimin (the factors may correlate)
  and parallel analysis (Horn 1965) to choose how many, after set.seed(with_seed).
* simplydata chooses (check_hidden_factors): maximum likelihood, and with empty cells lavaan's missing = "ml",
  which uses every value given, where lavaan's own default would leave those rows out silently.
* The fit guides are printed as guides (Hu & Bentler 1999), never as pass marks; the chi-square test gets the W2
  sentence with its caution turned round (a small p-value is expected with many rows even for a useful model).
"""

from __future__ import annotations

import math
import re

import numpy as np

from .._errors import SimplydataError, column_error, friendly
from .checking_more import _new_rows_table
from .stat_tests import _list_words
from .summaries import _p_sentence, _p_shown

EXPLORE_EXAMPLE = ('table.find_hidden_factors_behind(["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"])   '
                   '(with sdata.get_example("ability_tests"))')
CONFIRM_EXAMPLE = ('table.check_hidden_factors(measured_by={"visual": ["x1", "x2", "x3"], "textual": ["x4", "x5", '
                   '"x6"], "speed": ["x7", "x8", "x9"]})   (with sdata.get_example("ability_tests"))')

# method= : (psych fm, in words)
METHODS = {"minres": ("minres", "minimum residual (minres)"),
           "ml": ("ml", "maximum likelihood"),
           "principal axis": ("pa", "principal axis")}
METHOD_SPELLINGS = {"minimum residual": "minres", "min res": "minres", "uls": "minres",
                    "maximum likelihood": "ml", "max likelihood": "ml", "mle": "ml",
                    "pa": "principal axis", "paf": "principal axis", "principal axes": "principal axis",
                    "principal axis factoring": "principal axis", "principal-axis": "principal axis"}
# rotation= : (psych rotate, in words, may the factors correlate?)
ROTATIONS = {"oblimin": ("oblimin", "oblimin rotation (the factors may correlate)", True),
             "varimax": ("varimax", "varimax rotation (the factors kept uncorrelated)", False),
             "promax": ("promax", "promax rotation (the factors may correlate)", True),
             "none": ("none", "no rotation", False)}
ROTATION_SPELLINGS = {"no rotation": "none", "unrotated": "none", "no": "none", "direct oblimin": "oblimin"}
AUTOMATIC_SPELLINGS = {"automatic", "auto", "parallel analysis", "parallel"}
SHOWN_FROM = 0.3       # loadings below 0.3 are left blank in the printout (the full table is given back)
KMO_GUIDE = 0.6        # Kaiser's guide: below 0.6 the columns share little
ROWS_PER_COLUMN = 5    # fewer than 5 rows per column: the factors may not repeat in new data
COLUMNS_PER_FACTOR = 3  # fewer than 3 columns per factor: the factor is weakly pinned down
MODIFICATION_GUIDE = 10  # modification indices above 10 are named (the three largest)
NAME = re.compile(r"[A-Za-z_.][A-Za-z0-9_.]*")


def _choice(value, spellings, choices, option, step):
    if isinstance(value, str):
        key = " ".join(value.strip().lower().replace("_", " ").split())
        if key in choices:
            return key
        if key in spellings:
            return spellings[key]
    listed = ", ".join(f'"{c}"' for c in choices)
    example = EXPLORE_EXAMPLE.replace('"x9"])', f'"x9"], {option}="{choices[0]}")')
    raise SimplydataError(f"{step}() does not know {option}={value!r}. It takes {listed}.\nFor example, {example}")


def _two(x) -> str:
    return "nan" if x is None or math.isnan(x) else f"{x:.2f}"


def _three(x) -> str:
    return "nan" if x is None or math.isnan(x) else f"{x:.3f}"


def _pct(share) -> str:
    return f"{share * 100:.0f} %"


def _floats(x):
    return np.atleast_1d(np.asarray(x, dtype=float))


def _texts(x):
    return [str(v) for v in np.atleast_1d(np.asarray(x, dtype=object))]


class HiddenFactorWords:
    # ------------------------------------------------------------------ exploratory factor analysis
    @friendly(renamed={"method": "test_method"}, others={"nfactors": "how_many", "n_factors": "how_many", "factors": "how_many",
                      "rotate": "rotation", "fm": "method", "seed": "with_seed", "items": "columns"})
    def find_hidden_factors_behind(self, columns=None, how_many="automatic", rotation="oblimin", test_method="minres",
                                   with_seed=1):
        """Find the hidden factors behind many columns: how many there are, and which columns go with which.

        table.find_hidden_factors_behind(["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"])
        (with sdata.get_example("ability_tests"))
        Exploratory factor analysis: when many columns (questions, test scores) go together,
        a few hidden factors may lie behind them. Give the columns, as a list. how_many=
        "automatic" (the default) chooses how many factors by parallel analysis: the factors
        that stand out more than they would in random data of the same size; how_many=3 asks
        for 3. Prints how many factors and why, the loadings (how strongly each column goes
        with each factor, -1 to 1; below 0.3 left blank), each column's shared part (the
        communality), the share of the spread the factors hold and, when they may correlate,
        their correlations. Gives back one row per column: its loading on each factor, its
        shared part and its own part (the uniqueness). Unlike principal components
        (add_principal_components), which only sum the columns up, factor analysis looks for
        what the columns share. More: rotation="oblimin" (default; the factors may correlate),
        "varimax" (kept uncorrelated), "promax" or "none"; test_method="minres" (default), "ml"
        (maximum likelihood, as R factanal) or "principal axis"; with_seed=1 makes the
        parallel analysis and the oblimin rotation repeat. To check a model you wrote down beforehand, use
        check_hidden_factors. Needs R psych and GPArotation (pip install "simplydata[r]").
        Other names: factor analysis, efa, fa, factanal, scree, parallel analysis.
        """
        from .factor_r import explore

        step = "find_hidden_factors_behind"
        if columns is None:
            raise SimplydataError(f"{step}() needs the columns that may share hidden factors, as a list (it does not "
                                  "take every number column, which would put names, ages or totals in too).\n"
                                  f"For example, {EXPLORE_EXAMPLE}")
        if isinstance(columns, str) or not isinstance(columns, (list, tuple)) or not all(
                isinstance(c, str) for c in columns):
            raise SimplydataError(f"{step}() needs columns as a list of column names in quotes.\n"
                                  f"For example, {EXPLORE_EXAMPLE}")
        columns = list(dict.fromkeys(columns))
        if len(columns) < 3:
            raise SimplydataError(f"{step}() needs at least 3 columns to find a factor behind them; it got "
                                  f"{len(columns)}.\nFor example, {EXPLORE_EXAMPLE}")
        p = len(columns)
        # the most factors p columns can pin down: (p - k)^2 >= p + k (a count, not a statistic)
        most = max(k for k in range(1, p) if (p - k) ** 2 >= p + k)
        if isinstance(how_many, str) and how_many.strip().lower() in AUTOMATIC_SPELLINGS:
            automatic, wanted = True, 0
        elif isinstance(how_many, (int, np.integer)) and not isinstance(how_many, bool) and 1 <= how_many <= most:
            automatic, wanted = False, int(how_many)
        else:
            raise SimplydataError(f'{step}() needs how_many= as "automatic" (chosen by parallel analysis) or a whole '
                                  f"number from 1 to {most} ({p} columns can pin down at most {most} "
                                  f"{'factor' if most == 1 else 'factors'}), not {how_many!r}.")
        rotation_name = _choice(rotation, ROTATION_SPELLINGS, tuple(ROTATIONS), "rotation", step)
        method_name = _choice(test_method, METHOD_SPELLINGS, tuple(METHODS), "method", step)
        if isinstance(with_seed, bool) or not isinstance(with_seed, (int, np.integer)) or not 0 <= with_seed < 2 ** 31:
            raise SimplydataError(f"{step}() needs with_seed= as a whole number from 0 (for example with_seed=1), "
                                  f"not {with_seed!r}.")
        self._factor_numbers(step, columns, EXPLORE_EXAMPLE)
        x, _ = self._pattern_matrix(step, columns, least_rows=len(columns) + 2)
        flat = [c for c, same in zip(columns, (x == x[0]).all(axis=0)) if same]
        if flat:
            raise SimplydataError(f"{_list_words(chr(34) + c + chr(34) for c in flat)} has the same value in every "
                                  "row used, so it cannot go with any factor. Leave it out of the columns.")
        fm, fm_words = METHODS[method_name]
        rotate, rotate_words, oblique = ROTATIONS[rotation_name]
        out = explore(x, columns, wanted, fm, rotate, int(with_seed))
        suggested = float(np.atleast_1d(out["suggested"])[0])
        if automatic and (math.isnan(suggested) or suggested < 1):
            raise SimplydataError(f"Parallel analysis finds no hidden factor behind these {len(columns)} columns: none "
                                  "stands out more than it would in random data of the same size. To look anyway, "
                                  "give a number, such as how_many=1.")
        k = int(round(float(np.atleast_1d(out["k"])[0])))
        loadings = np.asarray(out["loadings"], dtype=float).reshape(len(columns), k, order="F") if k > 1 else \
            _floats(out["loadings"]).reshape(len(columns), 1)
        shared, own = _floats(out["communality"]), _floats(out["uniqueness"])
        share, cumulative = _floats(out["share"]), _floats(out["cumulative"])
        kmo = float(_floats(out["kmo"])[0])
        names = [f"factor {i}" for i in range(1, k + 1)]
        rows_used = len(x)
        # what was done
        print(f"Factor analysis of {len(columns)} columns ({rows_used} rows): {k} hidden "
              f"{'factor' if k == 1 else 'factors'}, {fm_words}, {rotate_words if k > 1 else 'no rotation needed'}.")
        if automatic:
            print(f"Parallel analysis suggests {k} {'factor' if k == 1 else 'factors'}: {k} "
                  f"{'stands' if k == 1 else 'stand'} out more than {'it' if k == 1 else 'they'} would in random data "
                  f"of the same size (Horn 1965; with_seed={int(with_seed)}).")
        print("Factor analysis looks for a few hidden factors that the columns share; principal components "
              "(add_principal_components) only sum the columns up.")
        # the loadings
        width = max(len(str(c)) for c in columns)
        print(f"Loadings (how strongly each column goes with each factor, usually -1 to 1; below {SHOWN_FROM} left blank "
              "here, all of them in the table given back), and each column's shared part (communality):")
        print("  " + " " * width + "".join(f"{n:>10}" for n in names) + f"{'shared part':>13}")
        for i, c in enumerate(columns):
            cells = "".join(f"{_two(v):>10}" if abs(v) >= SHOWN_FROM else " " * 10 for v in loadings[i])
            print(f"  {str(c):<{width}}{cells}{_two(shared[i]):>13}")
        held = _list_words(f"{n} {_pct(s)}" for n, s in zip(names, share))
        print(f"Together the factors hold {_pct(cumulative[-1])} of the columns' spread"
              + (f" ({held})." if k > 1 else "."))
        if oblique and k > 1 and "phi" in out and np.asarray(out["phi"]).size == k * k:
            phi = np.asarray(out["phi"], dtype=float).reshape(k, k, order="F")
            pairs = [f"{names[a]} with {names[b]} {_two(phi[a, b])}" for a in range(k) for b in range(a + 1, k)]
            print(f"Correlations between the factors: {_list_words(pairs)}.")
        # the method
        how = (f'set.seed({int(with_seed)}), psych::fa.parallel(x, fm = "{fm}", fa = "fa") chose {k}, then '
               if automatic else f"set.seed({int(with_seed)}), then ")
        rotated = {"oblimin": "GPArotation::oblimin", "varimax": "stats::varimax",
                   "promax": "psych's promax", "none": ""}[rotation_name]
        print(f'Method: R {how}psych::fa(x, nfactors = {k}, fm = "{fm}", rotate = "{rotate}")'
              + (f" (the rotation by {rotated})" if rotated and k > 1 else "") + "; psych::KMO(x) for the KMO.")
        chosen, yours = [], []
        (chosen if method_name == "minres" else yours).append(
            "minres (psych's default; it gives an answer where maximum likelihood can fail)" if method_name == "minres"
            else f"test_method={method_name!r}")
        if k > 1:
            (chosen if rotation_name == "oblimin" else yours).append(
                "oblimin (factors in real data usually correlate)" if rotation_name == "oblimin"
                else f"rotation={rotation_name!r}")
        (chosen if automatic else yours).append(
            "parallel analysis to choose how many (the 'eigenvalue above 1' rule finds too many)" if automatic
            else f"how_many={k}")
        if chosen:
            print(f"simplydata chooses: {_list_words(chosen)}." + (f" You chose {_list_words(yours)}." if yours else ""))
        else:
            print(f"You chose {_list_words(yours)}; simplydata's own choice is minres, oblimin and parallel analysis.")
        print("The signs of a factor are arbitrary: flipping one changes nothing.")
        # notes
        if kmo < KMO_GUIDE:
            print(f"Note: the columns share little (KMO = {_two(kmo)}, below Kaiser's guide of {KMO_GUIDE}), so "
                  "the factors may mean little.")
        if rows_used < ROWS_PER_COLUMN * len(columns):
            print(f"Note: {rows_used} rows for {len(columns)} columns (fewer than {ROWS_PER_COLUMN} rows for each "
                  "column): the factors may not repeat in new data.")
        strong = np.abs(loadings) >= SHOWN_FROM
        main = np.abs(loadings).argmax(axis=1)
        weak = [names[j] for j in range(k) if int((strong[:, j] & (main == j)).sum()) < COLUMNS_PER_FACTOR]
        if weak:
            print(f"Note: {_list_words(weak)} {'has' if len(weak) == 1 else 'have'} fewer than {COLUMNS_PER_FACTOR} "
                  f"columns of {SHOWN_FROM} or more that go mainly with {'it' if len(weak) == 1 else 'them'}: a factor "
                  "with only one or two columns is weakly pinned down.")
        none = [c for c, s in zip(columns, strong) if not s.any()]
        several = [c for c, s in zip(columns, strong) if s.sum() > 1]
        if none:
            print(f"Note: {_list_words(chr(34) + str(c) + chr(34) for c in none)} "
                  f"{'goes' if len(none) == 1 else 'go'} with no factor (every loading below {SHOWN_FROM}).")
        if several:
            print(f"Note: {_list_words(chr(34) + str(c) + chr(34) for c in several)} "
                  f"{'goes' if len(several) == 1 else 'go'} with more than one factor (loadings of {SHOWN_FROM} or "
                  "more on two): such a column does not measure one thing only.")
        heywood = [c for c, h in zip(columns, shared) if h >= 1]
        if heywood:
            print(f"Note: the shared part of {_list_words(chr(34) + str(c) + chr(34) for c in heywood)} is 1 or more "
                  "(a Heywood case), which real data cannot give: the answer is not to be trusted. Try fewer factors "
                  "or leave that column out.")
        rows = []
        for i, c in enumerate(columns):
            row = {"column": str(c)}
            row.update({n: float(loadings[i, j]) for j, n in enumerate(names)})
            row["shared part"] = float(shared[i])
            row["own part"] = float(own[i])
            rows.append(row)
        return _new_rows_table(self, rows)

    # ------------------------------------------------------------------ confirmatory factor analysis
    @friendly(others={"factors": "measured_by", "model": "formula", "syntax": "formula"})
    def check_hidden_factors(self, measured_by=None, formula=None):
        """Check a model of hidden factors you wrote down beforehand: does it match the data?

        table.check_hidden_factors(measured_by={"visual": ["x1", "x2", "x3"], "textual": ["x4",
        "x5", "x6"], "speed": ["x7", "x8", "x9"]})   (with sdata.get_example("ability_tests"))
        Confirmatory factor analysis: measured_by= names each hidden factor and the columns that
        measure it (lavaan's =~, "is measured by"). Prints the chi-square test of the model (a
        small p-value is expected with many rows even for a useful model), then CFI, TLI,
        RMSEA (with its 90 % interval) and SRMR, each with what it means and the commonly used
        guides (Hu & Bentler 1999), which are guides, not pass marks. Then the standardised
        loadings (-1 to 1), the correlations between the factors, and the largest modification
        indices (where the model and the data disagree most). Rows with empty cells are kept:
        lavaan uses every value given (missing = "ml"). Gives back one row per part of the
        model (term, estimate, standard error, 95 % CI, p-value) and the fit (chi-square, CFI,
        TLI, RMSEA, SRMR). More: formula= takes a whole model in lavaan's own syntax, with
        paths between the factors (a structural equation model), for example formula="visual
        =~ x1 + x2 + x3; speed =~ x7 + x8 + x9; speed ~ visual"; it is not the formula of
        fit_formula. To find the factors first, use find_hidden_factors_behind. Needs R lavaan
        (pip install "simplydata[r]"). Other names: cfa, lavaan, confirmatory factor analysis,
        structural equation model.
        """
        from .factor_r import confirm

        step = "check_hidden_factors"
        if (measured_by is None) == (formula is None):
            raise SimplydataError(f"{step}() needs measured_by= (each hidden factor and the columns that measure it) "
                                  "or formula= (a model in lavaan's own syntax), one of them.\n"
                                  f"For example, {CONFIRM_EXAMPLE}")
        if measured_by is not None:
            factors, used, model, shown_model, rename = self._measured_by_model(step, measured_by)
            route = "cfa"
        else:
            factors, used, model, rename = self._formula_model(step, formula)
            shown_model = model
            route = "sem"
        self._factor_numbers(step, used, CONFIRM_EXAMPLE)
        frame = self._number_frame(step, used)
        x = np.column_stack([frame[c].to_pandas().astype("float64").to_numpy() for c in used])
        nothing = np.isnan(x).all(axis=1)
        if nothing.any():
            gone = int(nothing.sum())
            print(f"Note: {gone} {'row has' if gone == 1 else 'rows have'} no value in any of these columns and "
                  f"{'is' if gone == 1 else 'are'} left out.")
            x = x[~nothing]
        same = [c for c, col in zip(used, x.T) if np.unique(col[~np.isnan(col)]).size < 2]
        if same:
            raise SimplydataError(f"{_list_words(chr(34) + c + chr(34) for c in same)} has the same value in every "
                                  "row, so it cannot measure a hidden factor. Leave it out of the model.")
        empty_rows = int(np.isnan(x).any(axis=1).sum())
        missing = "ml" if empty_rows else "listwise"
        out = confirm(x, [rename.get(c, c) for c in used], model, route, missing)
        if not bool(np.atleast_1d(out["converged"])[0]):
            raise SimplydataError("lavaan did not settle on an answer (the fit did not converge). Check the model: "
                                  "each hidden factor needs columns that go together, and a model with more paths "
                                  "than the data can pin down cannot be fitted.")
        back = {v: k for k, v in rename.items()}
        name = (lambda v: back.get(v, v))
        n = int(float(np.atleast_1d(out["n"])[0]))
        chisq, df, p, cfi, tli, rmsea, r_low, r_high, srmr = _floats(out["fit"])
        if df < 0:
            raise SimplydataError(f"The model asks for more values than the data can give ({int(round(-df))} too "
                                  "many), so it is not identified and has no answer. Give each hidden factor at least "
                                  "3 columns (or 2 when it correlates with another factor), or take out a path.")
        # what was done
        if route == "cfa":
            parts = "; ".join(f"{f} by {_list_words(cols)}" for f, cols in factors.items())
            print(f"Confirmatory factor analysis of {len(factors)} hidden "
                  f"{'factor' if len(factors) == 1 else 'factors'} measured by {len(used)} columns ({n} rows): "
                  f"{parts}.")
            twice = [c for c in used if sum(c in cols for cols in factors.values()) > 1]
            for c in twice:
                print(f'Note: "{c}" measures more than one factor '
                      f"({_list_words(f for f, cols in factors.items() if c in cols)}): a cross-loading.")
        else:
            print(f"A model with {len(factors)} hidden {'factor' if len(factors) == 1 else 'factors'} "
                  f"({_list_words(factors)}) in lavaan's syntax, fitted to {n} rows.")
        if empty_rows:
            print(f"Note: {empty_rows} {'row has' if empty_rows == 1 else 'rows have'} empty cells; lavaan uses every "
                  'value given (full-information maximum likelihood, missing = "ml"), so these rows are kept. This '
                  "assumes the cells are empty for reasons the other columns can explain (missing at random).")
        # the test and the fit
        if df < 0.5:
            print("With 0 degrees of freedom the model matches the data exactly by its make-up, so how well it fits "
                  "cannot be judged.")
        else:
            print(_p_sentence(p, if_none="the model were exactly right",
                              this="a gap between the model and the data this big or bigger", not_shown=None,
                              shown=f"chi-square {chisq:.1f} with {int(round(df))} degrees of freedom, {_p_shown(p)}"))
            print("A large p-value does not show the model is right; a small one is expected with many rows (300 or "
                  "more) even for a useful model. Read the guides below.")
            print(f"  CFI {_three(cfi)}: how much better the model matches the data than a model in which the columns "
                  "are unrelated (1 = as well as possible).")
            print(f"  TLI {_three(tli)}: the same idea, with a penalty for each extra value the model estimates.")
            print(f"  RMSEA {_three(rmsea)} (90 % CI {_three(r_low)} to {_three(r_high)}): the misfit for each degree "
                  "of freedom (0 = none).")
            print(f"  SRMR {_three(srmr)}: the average gap between the correlations the model implies and those in "
                  "the data.")
            print("  Commonly used guides: CFI and TLI 0.95 or more, RMSEA 0.06 or less, SRMR 0.08 or less (Hu & "
                  "Bentler 1999); treat them as guides, not pass marks.")
        # the parts of the model
        lhs, op, rhs = _texts(out["lhs"]), _texts(out["op"]), _texts(out["rhs"])
        est, se, pv, low, high = (_floats(out[k]) for k in ("est", "se", "p", "low", "high"))
        latent = set(factors)
        rows = []
        loadings: dict[str, list] = {}
        correlations, paths, leftovers = [], [], []
        for i in range(len(lhs)):
            a, b = name(lhs[i]), name(rhs[i])
            if op[i] == "=~":
                term, kind = f"{a} measured by {b}", "measured by"
                loadings.setdefault(a, []).append(f"{b} {_two(est[i])}")
            elif op[i] == "~~" and a != b:
                term, kind = f"{a} with {b}", "correlation"
                (correlations if a in latent and b in latent else leftovers).append(f"{a} with {b} {_two(est[i])}")
            elif op[i] == "~":
                term, kind = f"{a} explained by {b}", "explained by"
                paths.append(f"{a} explained by {b} {_two(est[i])} (95 % CI {_two(low[i])} to {_two(high[i])})")
            elif op[i] == ":=":
                term, kind = a, "defined"
            else:
                continue  # variances and averages
            rows.append({"term": term, "row kind": kind, "estimate": float(est[i]), "standard error": float(se[i]),
                         "95 % CI low": float(low[i]), "95 % CI high": float(high[i]), "p-value": float(pv[i])})
        if loadings:
            print("Standardised loadings (how strongly each column goes with its hidden factor, usually -1 to 1):")
            for f, items in loadings.items():
                print(f"  {f}: {_list_words(items)}.")
        if correlations:
            print(f"Correlations between the hidden factors: {_list_words(correlations)}.")
        if paths:
            print(f"Paths (standardised): {_list_words(paths)}.")
        if leftovers:
            print(f"Correlated leftovers (what columns share besides their factors): {_list_words(leftovers)}.")
        self._modification_notes(out, name)
        # the method
        call = "lavaan::cfa" if route == "cfa" else "lavaan::sem"
        print(f'Method: R {call}(model, data, estimator = "ML"' + (', missing = "ml"' if empty_rows else "")
              + "), then lavaan::fitMeasures(), lavaan::standardizedSolution() and lavaan::modindices(); the model in "
              f"lavaan's syntax: {shown_model.replace(chr(10), '; ')}.")
        print('simplydata chooses: maximum likelihood, and with empty cells missing = "ml" (lavaan alone would leave '
              "those rows out without a word).")
        fit = [{"term": "chi-square", "row kind": "fit", "estimate": float(chisq), "degrees of freedom": float(df),
                "p-value": float(p)},
               {"term": "CFI", "row kind": "fit", "estimate": float(cfi)},
               {"term": "TLI", "row kind": "fit", "estimate": float(tli)},
               {"term": "RMSEA", "row kind": "fit", "estimate": float(rmsea), "90 % CI low": float(r_low),
                "90 % CI high": float(r_high)},
               {"term": "SRMR", "row kind": "fit", "estimate": float(srmr)}]
        return _new_rows_table(self, rows + fit)

    # ------------------------------------------------------------------ helpers
    def _measured_by_model(self, step, measured_by):
        """lavaan syntax from measured_by=: the factors and columns get plain lavaan names (f1, c1 ...), so any
        column name works; the model as the learner would write it is kept for the printout."""
        if not isinstance(measured_by, dict) or not measured_by:
            raise SimplydataError(f"{step}() needs measured_by= as a dict: each hidden factor's name, then the "
                                  f"columns that measure it.\nFor example, {CONFIRM_EXAMPLE}")
        factors = {}
        for f, cols in measured_by.items():
            if not isinstance(f, str) or not f.strip():
                raise SimplydataError(f"{step}() needs each hidden factor's name in quotes, such as \"visual\".")
            cols = [cols] if isinstance(cols, str) else cols
            if not isinstance(cols, (list, tuple)) or not all(isinstance(c, str) for c in cols):
                raise SimplydataError(f'{step}() needs the columns of "{f}" as a list of column names in quotes.\n'
                                      f"For example, {CONFIRM_EXAMPLE}")
            cols = list(dict.fromkeys(cols))
            if len(cols) < 2:
                raise SimplydataError(f'The hidden factor "{f}" has {len(cols)} column; a hidden factor needs at least '
                                      "2 columns that measure it (3 or more is the usual advice).")
            factors[f] = cols
        used = list(dict.fromkeys(c for cols in factors.values() for c in cols))
        self._need_columns(*used)
        clash = [f for f in factors if f in self._frame.columns]
        if clash:
            raise SimplydataError(f"{_list_words(chr(34) + f + chr(34) for f in clash)} is the name of a column; a "
                                  "hidden factor is not in the table, so give it another name.")
        rename = {c: f"c{i}" for i, c in enumerate(used, 1)}
        latent = {f: f"f{i}" for i, f in enumerate(factors, 1)}
        model = "\n".join(f"{latent[f]} =~ " + " + ".join(rename[c] for c in cols) for f, cols in factors.items())
        shown = "\n".join(f"{f} =~ " + " + ".join(cols) for f, cols in factors.items())
        return factors, used, model, shown, {**rename, **latent}

    def _formula_model(self, step, formula):
        """The columns and hidden factors of a model in lavaan's syntax; a fit_formula-style formula is refused."""
        if not isinstance(formula, str) or not formula.strip():
            raise SimplydataError(f"{step}() needs formula= as text in lavaan's syntax, such as formula=\"visual =~ x1 "
                                  "+ x2 + x3; speed =~ x7 + x8 + x9; speed ~ visual\".")
        uncommented = "\n".join(re.split(r"[#!]", line)[0] for line in formula.splitlines())
        model = "\n".join(part.strip() for part in re.split(r"[;\n]", uncommented) if part.strip())
        if "=~" not in model:
            if re.search(r"(?<![<>=!~:])=(?![~=])", model):
                raise SimplydataError(f"{step}(formula=) takes a model in lavaan's syntax (hidden =~ columns), not a "
                                      'formula like those of fit_formula ("y = a * x + b"). For example, '
                                      'formula="visual =~ x1 + x2 + x3; speed =~ x7 + x8 + x9; speed ~ visual".')
            raise SimplydataError(f"{step}(formula=) needs at least one hidden factor, written name =~ columns (\"is "
                                  "measured by\"). A model of columns only is table.explain(...).")
        factors = list(dict.fromkeys(line.split("=~")[0].strip() for line in model.splitlines() if "=~" in line))
        columns = self._frame.columns
        found, labels = [], set()
        for line in model.splitlines():
            if re.search(r":=|==|<|>", line):
                if ":=" in line:
                    labels.update(m.group() for m in NAME.finditer(line.split(":=")[0]))
                continue  # a defined value or a constraint: it names labels, not columns
            for m in NAME.finditer(line):
                after = line[m.end():].lstrip()
                if after.startswith(("*", "(")) or m.group() == "NA":
                    labels.add(m.group())
                    continue  # a label, a fixed value or a function such as start()
                found.append(m.group())
        used = [c for c in dict.fromkeys(found) if c in columns and c not in factors]
        unknown = [t for t in dict.fromkeys(found) if t not in columns and t not in factors and t not in labels]
        if unknown:
            raise column_error(unknown[0], columns)
        if not used:
            raise SimplydataError(f"{step}(formula=) names no column of the table.")
        return factors, used, model, {}

    def _factor_numbers(self, step, columns, example):
        """The columns exist and hold numbers; the error shows this word's own example."""
        self._need_columns(*columns)
        text = [c for c in columns if not self._frame.schema[c].is_numeric()]
        if text:
            raise SimplydataError(f"{step}() needs columns of numbers (scores, answers on a scale), but "
                                  f"{_list_words(chr(34) + str(c) + chr(34) for c in text)} "
                                  f"{'does' if len(text) == 1 else 'do'} not hold numbers. Leave "
                                  f"{'it' if len(text) == 1 else 'them'} out.\nFor example, {example}")

    @staticmethod
    def _modification_notes(out, name):
        if "mi" not in out:
            return
        mi = _floats(out["mi"])
        lhs, op, rhs = _texts(out["mi_lhs"]), _texts(out["mi_op"]), _texts(out["mi_rhs"])
        big = [i for i in range(len(mi)) if mi[i] > MODIFICATION_GUIDE][:3]
        if not big:
            return
        said = []
        for i in big:
            a, b = name(lhs[i]), name(rhs[i])
            if op[i] == "=~":
                said.append(f"{a} may also be measured by {b} ({mi[i]:.1f})")
            elif op[i] == "~~":
                said.append(f"{a} and {b} may share something the model leaves out ({mi[i]:.1f})")
            elif op[i] == "~":
                said.append(f"{a} may also be explained by {b} ({mi[i]:.1f})")
            else:
                said.append(f"{a} {op[i]} {b} ({mi[i]:.1f})")
        print(f"Note: where the model and the data disagree most (modification indices above {MODIFICATION_GUIDE}, "
              "each about how much the chi-square would drop if that were added): "
              f"{_list_words(said)}. Change the model only for a reason you can defend: a change fitted to these "
              "data makes the fit look better than it will be in new data.")
