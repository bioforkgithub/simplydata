"""Statistical tests in plain words. They never change the table.

You ask the question in words; simplydata picks the standard test, prints one plain answer
that says which test was used and why, and gives back a one-row result table (which can be
saved like any table). test= lets an expert choose another test. Numbers come from SciPy.

Choices (the same defaults as R, so results can be checked there):

* compare_averages_of, 2 groups: Welch's t-test (R t.test() default). It does NOT assume that
  the groups have the same spread, so there is nothing to check about spread. Effect size:
  Hedges' g, the difference in pooled standard deviations (R effectsize::hedges_g).

Every effect size and its two-sided 95 % interval comes from R effectsize through
simplydata[r] (table/effect_sizes.py): hedges_g, omega_squared, rank_biserial,
rank_epsilon_squared (bootstrap interval, set.seed(1)), cohens_d, and the intervals of
cohens_w and cramers_v. Cramer's V (SciPy association), Cohen's w (statsmodels
chisquare_effectsize) and Cohen's h (statsmodels proportion_effectsize = R pwr::ES.h) come
from Python. Without R the test still runs, the R effect size is left empty, and a one-line
note says how to add it.
* compare_averages_of, 3 or more groups: Welch's one-way ANOVA (R oneway.test() default,
  var.equal = FALSE; Welch 1951), from statsmodels anova_oneway. Effect size: omega-squared
  (R effectsize::omega_squared on the ordinary one-way ANOVA); it is less biased upwards than
  eta-squared in small samples (Okada 2013). Which pairs differ: compare_each_pair_of(), pairwise Welch t-tests with Holm's
  correction (R pairwise.t.test(pool.sd = FALSE, p.adjust.method = "holm")); or with
  test="tukey" Tukey's honest significant difference (R TukeyHSD(aov(...)), SciPy
  tukey_hsd, the Tukey-Kramer form for unequal group sizes), with simultaneous 95 %
  intervals. Tukey assumes equal spreads, so a note warns when the biggest standard
  deviation is more than twice the smallest.
* compare_spreads_of: Levene's test centred on the medians (the Brown-Forsythe form; the
  R car::leveneTest() default, SciPy levene(center="median"); the same as a one-way ANOVA
  on the distances from each group's median). test="bartlett" (R bartlett.test()) and
  test="fligner" (R fligner.test(), Fligner-Killeen with median centring).
* based_on="ranks": Mann-Whitney U (2 groups) or Kruskal-Wallis (3 or more), with the
  rank-biserial correlation or rank epsilon-squared as effect size.
* compare_before_and_after: paired t-test (Cohen's d_z) or Wilcoxon signed-rank.
* compare_average_to: one-sample t-test (Cohen's d) or Wilcoxon signed-rank.
  Wilcoxon and Mann-Whitney give an exact p-value when there are fewer than 50 values and
  no ties (and no zero changes), otherwise the normal approximation with continuity and tie
  correction; zero changes are left out. This is R wilcox.test() as it was for many years,
  and R wilcox.test(exact = FALSE) when there are ties. (R 4.6 by default now gives an
  exact p-value even with ties below 50 values, which can differ a little.)
* compare_counts_of: chi-square test of independence, with Yates' continuity correction for
  2 x 2 tables only (R chisq.test() and SciPy default). If an expected count is below 5 a
  note says so and suggests test="fisher" (2 x 2 tables); simplydata never switches by
  itself. Effect size: Cramer's V (SciPy association, without correction), its interval from R
  effectsize::cramers_v.
* compare_counts_to: chi-square goodness-of-fit test against expected shares (R
  chisq.test(x, p = ...); equal shares when none are given). Effect size: Cohen's w.
* compare_percent_to: the exact binomial test of a percent against a chosen percent
  (R binom.test(x, n, p), SciPy binomtest; the two-sided p-value as R), with the exact
  Clopper-Pearson 95 % interval. Effect size: Cohen's h.
* compare_shape_to(..., "normal"): the Shapiro-Wilk test (R shapiro.test(), Royston's
  algorithm), for 3 to 5000 values per group, as R.
* add_adjusted_p_value_column: Holm (default), Bonferroni, Benjamini-Hochberg or
  Benjamini-Yekutieli, exactly as R p.adjust(); empty p-values stay empty and are not
  counted. method="storey" (Storey's q-values) and "local fdr" come from R qvalue
  (table/small_r.py).
* The groups column is for_each_group_in= in every test (between= was its old name and still works
  for one release, with a note).
* fit_line, fit_curve and fit_formula: see fitting.py (R lm() and nls()).

Assumption checks are notes, never silent switches. For tests on averages, each group with
3 to 5000 values is checked with the Shapiro-Wilk test. With fewer than 30 values a
"not bell-shaped" result comes with a safer choice (based_on="ranks"). With 30 or more the
note says the test is usually still fine: the average of many values is close to
bell-shaped even when the values are not (the central limit theorem), and with many values
Shapiro-Wilk flags even tiny, harmless departures.

Every p-value is said in one sentence (the same in every word, summaries._p_sentence):
"If there were truly no difference, a difference this big or bigger would turn up in about 3
of 100 studies like this one (p = 0.031)." Below p = 0.001 it says "fewer than 1 in 1000
studies". From p = 0.05 a second sentence says that this does not show there is no difference.
"""

from __future__ import annotations

import ast
import difflib
import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._stats import _plain_name
from .columns import (CONSTANTS, FORMULA_HELP, FUNCTION_SPELLINGS, FUNCTIONS, SPECIAL_FUNCTIONS, _formula_error,
                      _FormulaReader, _is_number, special_function)
from .summaries import GROUPS_IN_SENTENCE as GROUPS_SHOWN
from .effect_sizes import effect_size, interval_only, interval_text
from .post_hoc import R_PAIR_TESTS, dunnett_pairs, pair_letters, r_pairs
from .small_r import FRIEDMAN_PAIR_TESTS
from .summaries import _key, _order, _p_clause, _p_sentence, _p_shown, _plain, _say_label

BASED_ON = ("averages", "ranks")
AVERAGE_TESTS = ("welch", "student", "welch anova", "anova", "mann-whitney", "kruskal-wallis", "yuen",
                 "brunner-munzel", "alexander-govern", "median", "jonckheere")
# test= choices of compare_averages_of with their own engine (_more_average_test); the first two take 2 groups
MORE_AVERAGE_TESTS = ("yuen", "brunner-munzel", "alexander-govern", "median")
RANK_LIKE = ("mann-whitney", "kruskal-wallis", "brunner-munzel", "median", "jonckheere")  # with based_on="ranks"
RANK_TESTS = ("mann-whitney", "kruskal-wallis")
TWO_GROUP_TESTS = ("welch", "student", "mann-whitney", "yuen", "brunner-munzel")
COUNT_TESTS = ("chi-square", "fisher", "g", "barnard", "boschloo")
FISHER_TABLES = 100_000  # Fisher on a bigger table: the p-value from this many random tables (seeded)
EXACT_METHODS = {"barnard": "z-pooled", "boschloo": "boschloo"}  # R Exact::exact.test(method =)
PAIR_TESTS = ("welch", "mann-whitney", "tukey", "games-howell", "scheffe", "lsd", "dunn", "conover")
PAIR_ALIASES = {"games howell": "games-howell", "gameshowell": "games-howell", "scheffé": "scheffe",
                "fisher": "lsd", "fisher's lsd": "lsd", "dunn's": "dunn", "conover-iman": "conover"}
FRIEDMAN_PAIR_ALIASES = {"nemenyi-wilcoxon-wilcox": "nemenyi", "nemenyi's": "nemenyi", "conover's": "conover",
                         "conover-iman": "conover"}
PERCENT_PAIR_TESTS = ("chi-square", "fisher")  # compare_each_pair_of(based_on="percents", test=)
SPREAD_TESTS = ("levene", "bartlett", "fligner", "ansari", "mood", "f")
TWO_GROUP_SPREAD_TESTS = ("ansari", "mood", "f")
SPREAD_ALIASES = {"brown-forsythe": "levene", "brown forsythe": "levene", "fligner-killeen": "fligner",
                  "fligner killeen": "fligner"}
SPREAD_RATIO = 2  # Tukey note: the biggest standard deviation more than twice the smallest
EXACT_LIMIT = 50  # exact p-values below 50 values without ties, as R wilcox.test()
CLT_SIZE = 30  # from this many values, a "not bell-shaped" note does not suggest switching
SHAPIRO_LIMIT = 5000  # SciPy's Shapiro-Wilk is reliable up to 5000 values
SHAPES = ("normal",)  # compare_shape_to: the shapes it can check
# compare_shape_to(test=): name -> (name in sentences, statistic name, R function, fewest values)
SHAPE_TESTS = {
    "shapiro-wilk": ("Shapiro-Wilk test", "W", "shapiro.test()", 3),
    "lilliefors": ("Lilliefors test", "D", "nortest::lillie.test()", 5),
    "dagostino": ("D'Agostino-Pearson test", "K2", "fBasics::dagoTest()", 8),
    "jarque-bera": ("Jarque-Bera test", "JB", "tseries::jarque.bera.test()", 3),
    "kolmogorov-smirnov": ("one-sample Kolmogorov-Smirnov test", "D", 'ks.test(x, "DIST", ...)', 2),
    "cramer-von-mises": ("Cramer-von Mises test", "omega2", 'goftest::cvm.test(x, "DIST", ...)', 2),
}
NORMAL_TESTS = ("shapiro-wilk", "lilliefors", "dagostino", "jarque-bera")
FIXED_SHAPE_TESTS = ("kolmogorov-smirnov", "cramer-von-mises")
SHAPE_TEST_ALIASES = {"shapiro": "shapiro-wilk", "shapiro wilk": "shapiro-wilk", "d'agostino": "dagostino",
                      "dagostino-pearson": "dagostino", "d'agostino-pearson": "dagostino", "normaltest": "dagostino",
                      "jarque bera": "jarque-bera", "jb": "jarque-bera", "lillie": "lilliefors", "ks": "kolmogorov-smirnov",
                      "kolmogorov smirnov": "kolmogorov-smirnov", "cvm": "cramer-von-mises",
                      "cramer von mises": "cramer-von-mises", "cramer-von mises": "cramer-von-mises"}
# add_adjusted_p_value_column: method -> (name in sentences, R p.adjust name)
ADJUST_METHODS = {
    "holm": ("Holm", "holm"),
    "bonferroni": ("Bonferroni", "bonferroni"),
    "benjamini-hochberg": ("Benjamini-Hochberg", "BH"),
    "benjamini-yekutieli": ("Benjamini-Yekutieli", "BY"),
    "hochberg": ("Hochberg", "hochberg"),
    "hommel": ("Hommel", "hommel"),
}
ADJUST_ALIASES = {"bh": "benjamini-hochberg", "fdr": "benjamini-hochberg", "by": "benjamini-yekutieli",
                  "benjamini hochberg": "benjamini-hochberg", "benjamini yekutieli": "benjamini-yekutieli",
                  "q-values": "storey", "q-value": "storey", "q values": "storey", "q value": "storey",
                  "qvalue": "storey", "qvalues": "storey", "storey-tibshirani": "storey", "storey tibshirani": "storey",
                  "local false discovery rate": "local fdr", "lfdr": "local fdr", "localfdr": "local fdr",
                  "local-fdr": "local fdr"}
# methods that come from R qvalue (Storey & Tibshirani 2003), not from p.adjust()
STOREY_METHODS = {"storey": "Storey q-value", "local fdr": "local false discovery rate"}
ADJUST_MEANING = {
    "holm": "the chance of even one false alarm among all the tests stays at 5 %",
    "bonferroni": "the chance of even one false alarm among all the tests stays at 5 %",
    "benjamini-hochberg": "about 5 % of the findings below 0.05 are expected to be false alarms "
                          "(the false discovery rate)",
    "benjamini-yekutieli": "about 5 % of the findings below 0.05 are expected to be false alarms "
                           "(the false discovery rate), however the tests depend on each other",
    "hochberg": "the chance of even one false alarm among all the tests stays at 5 % (when the tests do not "
                "depend on each other in an unusual way)",
    "hommel": "the chance of even one false alarm among all the tests stays at 5 % (when the tests do not depend "
              "on each other in an unusual way)",
}


# ---------------------------------------------------------------------------- small helpers
def _num(x) -> str:
    """A number with 3 significant digits, written plainly (no 1e+05 unless huge or tiny)."""
    x = float(x)
    if math.isnan(x):
        return "nan"
    if math.isinf(x):
        return "infinite"
    if x == 0:
        return "0"
    size = abs(x)
    if size >= 1e6 or size < 1e-4:
        return f"{x:.3g}"
    digits = max(0, 2 - math.floor(math.log10(size)))
    text = f"{x:.{digits}f}"
    return "0" if float(text) == 0 else text


# _p_sentence(p, *ALIKE): the p-value sentence of a test of 3 or more groups
ALIKE = ("the groups were truly alike", "differences this big or bigger between them", "that the groups are alike")


def _whole(x) -> str:
    """Degrees of freedom and rank sums: 2 not 2.00, 33.8 stays 33.8, 213.5 stays 213.5."""
    x = float(x)
    return str(int(x)) if x.is_integer() else (f"{x:g}" if abs(x) >= 100 else _num(x))


def _percent(share: float) -> str:
    return f"{round(share * 100)} %"


def _label(value) -> str:
    if hasattr(value, "item"):
        value = value.item()
    return str(value)


def _looks_like_direction(name) -> bool:
    from .places import looks_like_direction

    return looks_like_direction(name)


def _list_words(items) -> str:
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _skipped_note(skipped: int, names) -> None:
    if not skipped:
        return
    rows = "row" if skipped == 1 else "rows"
    verb = "was" if skipped == 1 else "were"
    where = " or ".join(f'"{n}"' for n in names)
    print(f"Note: {skipped} {rows} with an empty cell in {where} {verb} skipped.")


# simplydata method name -> statsmodels multipletests method (the same numbers as R p.adjust())
_MULTIPLETESTS = {"holm": "holm", "bonferroni": "bonferroni", "benjamini-hochberg": "fdr_bh",
                  "benjamini-yekutieli": "fdr_by", "hochberg": "simes-hochberg", "hommel": "hommel"}


def _adjust_p(p_values, method: str) -> np.ndarray:
    """Adjusted p-values from statsmodels multipletests, the same as R p.adjust() (no empty values here)."""
    from statsmodels.stats.multitest import multipletests

    p = np.asarray(p_values, dtype=float)
    if len(p) == 0:
        return p
    return np.asarray(multipletests(p, method=_MULTIPLETESTS[method])[1], dtype=float)


def _holm(p_values) -> list[float]:
    """Holm's step-down adjustment (R p.adjust(method = "holm"))."""
    return _adjust_p(p_values, "holm").tolist()


SCIPY_SIDES = ("two-sided", "greater", "less")


def _direction(step, sides, higher, lower, alternative, choices, example, words=None, lower_words=None):
    """sides=2 (default) or sides=1 with higher= or its mirror lower= (chosen before seeing the data).

    choices maps each side's word to the SciPy alternative it means when that side is higher (the
    first group, the after column, the data's average ... minus the other side); a side that is
    not a word users type (the number in compare_average_to) has a key starting with "_".
    words: the words higher= accepts (default: every key without "_"); lower_words: the words
    lower= accepts (default: the same; lower=X means the other side is higher). R's and SciPy's
    alternative="greater" / "less" / "two-sided" is accepted too, with the translation printed.
    Gives back (SciPy alternative, the key of the side that is higher, or None)."""
    words = list(words if words is not None else [k for k in choices if not k.startswith("_")])
    lower_words = list(lower_words if lower_words is not None else words)

    def other(key):
        return next(k for k in choices if k != key)

    if alternative is not None:
        if alternative not in SCIPY_SIDES:
            raise choice_error(step, "alternative", alternative, SCIPY_SIDES)
        if sides != 2 or higher is not None or lower is not None:
            raise SimplydataError(f'{step}() was given alternative= and sides=/higher=/lower=; give only one of them.')
        if alternative == "two-sided":
            return "two-sided", None
        up = next(k for k, v in choices.items() if v == alternative)
        said = f'higher="{up}"' if up in words else f'lower="{other(up)}"'
        print(f'Note: alternative="{alternative}" is sides=1, {said} in simplydata.')
        return alternative, up
    if isinstance(sides, bool) or sides not in (1, 2):
        raise SimplydataError(f"{step}() needs sides=2 (a difference either way, the usual) or sides=1 (only the "
                              "direction you expected before seeing the data, with higher= or lower=).\n"
                              f"For example, {example}")
    if higher is not None and lower is not None:
        raise SimplydataError(f'{step}() was given both higher= and lower=; give one of them (lower="{lower}" is the '
                              f"same as saying the other side is higher).\nFor example, {example}")
    if sides == 2:
        if higher is not None or lower is not None:
            option = "higher=" if higher is not None else "lower="
            raise SimplydataError(f"{option} says which side a one-sided test looks at, so it goes with sides=1.\n"
                                  f"For example, {example}")
        return "two-sided", None
    if higher is None and lower is None:
        raise SimplydataError(f"sides=1 looks in one direction only, so it needs higher= (or lower=) to say what "
                              f"you expected before seeing the data.\nFor example, {example}")
    if higher is not None:
        if higher not in words:
            raise choice_error(step, "higher", higher, words)
        return choices[higher], higher
    if not lower_words:
        raise SimplydataError(f"{step}() takes higher= for a one-sided test, not lower=.\nFor example, {example}")
    if lower not in lower_words:
        raise choice_error(step, "lower", lower, lower_words)
    up = other(lower)
    return choices[up], up


def _non_inferiority(step, same_within, sides, higher, lower, not_lower, not_higher, words, example):
    """not_lower="B" / not_higher="B" with same_within= (a non-inferiority test) as the sides=, higher=, lower=
    that _direction() reads, plus the claim: None (the side named is not lower) or "not_higher".

    not_lower="B" is the one-sided test that B is not lower than the other side by more than the margin
    (the math of sides=1, higher="B"); not_higher="B" that B is not higher by more than the margin (the math
    of sides=1, lower="B"), for outcomes where lower is better, such as pain. The older spelling sides=1,
    higher="B" (or lower=) with same_within= still works, and a note gives the new one."""
    if not_lower is None and not_higher is None:
        if same_within is not None and sides == 1 and (higher is None) != (lower is None):
            old, new = (f'higher="{higher}"', f'not_lower="{higher}"') if higher is not None else \
                (f'lower="{lower}"', f'not_higher="{lower}"')
            print(f"Note: sides=1, {old} with same_within= is a non-inferiority test; it is written {new}.")
            return sides, higher, lower, (None if higher is not None else "not_higher")
        return sides, higher, lower, None
    if not_lower is not None and not_higher is not None:
        raise SimplydataError(f"{step}() was given both not_lower= and not_higher=; give one of them.\n"
                              f"For example, {example}")
    option, side = ("not_lower", not_lower) if not_lower is not None else ("not_higher", not_higher)
    if same_within is None:
        raise SimplydataError(f"{option}= is a non-inferiority test, so it needs same_within= (the margin).\n"
                              f"For example, {example}")
    if higher is not None or lower is not None:
        raise SimplydataError(f"{option}= already gives the direction; leave out higher= and lower=.\n"
                              f"For example, {example}")
    if isinstance(sides, bool) or sides not in (1, 2):
        raise SimplydataError(f"{option}= is one-sided already; leave out sides=.\nFor example, {example}")
    if side not in words:
        raise choice_error(step, option, side, list(words))
    return (1, side, None, None) if option == "not_lower" else (1, None, side, "not_higher")


def _one_sided_sentence(looks_for: str, not_counted: str) -> str:
    return (f"One-sided, as you asked before seeing the data: it only looks for {looks_for}; {not_counted} "
            "would not count.")


def _interval_words(low: float, high: float) -> str:
    """"1.2 to 3.4", or for a one-sided interval "at least 1.2" / "at most 3.4"."""
    if math.isinf(high) and high > 0:
        return f"at least {_num(low)}"
    if math.isinf(low) and low < 0:
        return f"at most {_num(high)}"
    return f"{_num(low)} to {_num(high)}"


def _welch_anova(groups):
    """Welch's one-way ANOVA (Welch 1951), as R oneway.test(var.equal = FALSE).

    statsmodels anova_oneway(use_var="unequal", welch_correction=True). Returns F, df1, df2, p."""
    from statsmodels.stats.oneway import anova_oneway

    result = anova_oneway([np.asarray(g, dtype=float) for g in groups], use_var="unequal",
                          welch_correction=True)
    df1, df2 = result.df
    return float(result.statistic), float(df1), float(df2), float(result.pvalue)


def _has_ties(values) -> bool:
    return len(np.unique(values)) < len(values)


def _mann_whitney(a, b, alternative="two-sided"):
    """Mann-Whitney U like R wilcox.test(): exact below 50 values per group without ties."""
    from scipy import stats

    exact = len(a) < EXACT_LIMIT and len(b) < EXACT_LIMIT and not _has_ties(np.concatenate([a, b]))
    method = "exact" if exact else "asymptotic"
    result = stats.mannwhitneyu(a, b, alternative=alternative, method=method, use_continuity=True)
    u = float(result.statistic)  # U of the first group, the same as R's W
    how = "exact p-value" if exact else "normal approximation with continuity correction"
    return u, float(result.pvalue), how


def _hodges_lehmann(a, b, exact, alternative="two-sided"):
    """The Hodges-Lehmann shift (first minus second) and its interval, from R wilcox.test(conf.int = TRUE) with the
    same exact/approximate choice as the test (Python has no function for this interval)."""
    from .._r import RMissing, r_call

    side = {"two-sided": "two.sided", "greater": "greater", "less": "less"}[alternative]
    try:
        found = r_call("w <- stats::wilcox.test(a, b, conf.int = TRUE, exact = ex, correct = TRUE, alternative = side); "
                       "list(value = unname(w$estimate), ci = as.numeric(w$conf.int))", packages=(),
                       what="the Hodges-Lehmann shift with its interval (R wilcox.test(conf.int = TRUE))",
                       a=np.asarray(a, dtype=float), b=np.asarray(b, dtype=float), ex=bool(exact), side=side)
    except RMissing:
        return {"value": math.nan, "low": math.nan, "high": math.nan,
                "note": ("Note: the Hodges-Lehmann shift with its 95 % CI comes from R (wilcox.test(conf.int = TRUE)), "
                         'which is not ready here; to add it: pip install "simplydata[r]" and install R.')}
    low, high = (float(v) for v in np.asarray(found["ci"], dtype=float))
    return {"value": float(np.asarray(found["value"])[0]), "low": low, "high": high, "note": ""}


def _signed_rank(changes, alternative="two-sided"):
    """Wilcoxon signed-rank like R wilcox.test(): zero changes left out; exact below 50 values
    without ties, otherwise the normal approximation with continuity correction.
    Gives V (the sum of the ranks of the positive changes, as R), p, the matched-pairs
    how p was found, how many zero changes were left out, and whether the changes lean up
    (V above half of the largest possible V; the size of the lean comes from R effectsize)."""
    from scipy import stats

    zeros = int((changes == 0).sum())
    nonzero = changes[changes != 0]
    if len(nonzero) == 0:
        return None
    ranks = stats.rankdata(np.abs(nonzero))
    v = float(ranks[nonzero > 0].sum())
    top = len(nonzero) * (len(nonzero) + 1) / 2
    exact = len(nonzero) < EXACT_LIMIT and not _has_ties(np.abs(nonzero)) and zeros == 0
    method = "exact" if exact else "approx"
    result = stats.wilcoxon(nonzero, zero_method="wilcox", correction=True, method=method, alternative=alternative)
    how = "exact p-value" if exact else "normal approximation with continuity correction"
    return v, float(result.pvalue), how, zeros, ("up" if v > top / 2 else "down" if v < top / 2 else "neither way")


def _shape_notes(named_values, what="the values") -> list[str]:
    """Shapiro-Wilk check of each group; plain notes, never a switch. Each name is a group ('group "a"'),
    giving "the values in group "a" ..."; a name of None checks one set of values on its own, and then
    what= says all of it ("the changes", "the residuals"), giving "the changes don't look ..."."""
    from scipy import stats

    notes = []
    for name, values in named_values:
        n = len(values)
        subject = what if name is None else f"{what} in {name}"
        if n < 3:
            notes.append(f"Note: there are only {n} {what.removeprefix('the ')}: too few to check whether they "
                         "are bell-shaped." if name is None else
                         f"Note: {name} has only {n} values: too few to check whether {what} are bell-shaped.")
            continue
        if n > SHAPIRO_LIMIT or np.ptp(values) == 0:
            continue
        p = float(stats.shapiro(values).pvalue)
        if p >= 0.05:
            continue
        shown = "p < 0.0001" if p < 0.0001 else f"p = {p:.3f}" if p >= 0.001 else f"p = {p:.4f}"
        if n < CLT_SIZE:
            notes.append(
                f"Note: {subject} don't look bell-shaped (Shapiro-Wilk {shown}); "
                'a safer test here: based_on="ranks".'
            )
        else:
            notes.append(
                f"Note: {subject} don't look bell-shaped (Shapiro-Wilk {shown}), but with {n} values "
                "the average is close to bell-shaped anyway (the central limit theorem), so this test is "
                "usually still fine."
            )
    return notes


# ---------------------------------------------------------------------------- fit_formula reader
FIT_FUNCTIONS = {"exp": (1, 1), "log": (1, 2), "sqrt": (1, 1), "abs": (1, 1),
                 **{name: FUNCTIONS[name] for name in ("sin", "cos", *SPECIAL_FUNCTIONS)},
                 "arctan": (1, 1), "arcsin": (1, 1), "arccos": (1, 1), "arctan2": (2, 2)}
# the inverse trigonometric functions are NumPy's own (NIST Roszman1 needs arctan); R's names work too
FIT_NUMPY = {"arctan": np.arctan, "arcsin": np.arcsin, "arccos": np.arccos}
FIT_SPELLINGS = {"atan": "arctan", "asin": "arcsin", "acos": "arccos", "atan2": "arctan2"}
# gamma and beta are also usual names for values to find: written without brackets they are values
FIT_NAMES_FREE = ("gamma", "beta")
FIT_HELP = (
    "A formula to fit has the column to fit on the left of =, and on the right:\n"
    "  column names               hours  (names with spaces go in backticks: `max temp`)\n"
    "  values to find             any other name, such as a, b, k or rate\n"
    "  numbers                    2, 100, 0.5\n"
    "  + - * / **                 add, subtract, multiply, divide, power\n"
    "  ( )                        brackets\n"
    "  exp(x)  log(x)  log(x, 10) e to the power x, natural log, log to base 10\n"
    "  sqrt(x)  abs(x)            square root, size without the minus sign\n"
    "  sin(x)  cos(x)  tan(x)     sine, cosine, tangent (x in radians); pi is 3.14159...\n"
    "  arctan(x)  arcsin(x)       the angle (in radians) whose tangent or sine is x; arccos(x) too\n"
    "  arctan2(y, x)              the angle of the point (x, y), from -pi to pi (as R atan2(y, x))\n"
    "  erf(x)  erfc(x)            error function, and 1 - erf(x)\n"
    "  gamma(x)  lgamma(x)        gamma function, and the log of its size (as R)\n"
    "  digamma(x)  beta(a, b)     digamma function, beta function (as R)\n"
    "  besselJ(x, nu)             Bessel function of the first kind, order nu (as R)\n"
    "  sinc(x)                    sin(pi x) / (pi x), and 1 at x = 0 (as NumPy sinc)\n"
    'Example: table.fit_formula("marks = a * hours + b")   (with sdata.get_example("marks"))'
)


def _fit_error(problem: str) -> SimplydataError:
    return SimplydataError(f"{problem}\n\n{FIT_HELP}")


class _FitReader(_FormulaReader):
    """The safe formula reader of add_column, turned into a NumPy function for fitting.

    The text is still read with ast and never run. Names that are columns are data; any
    other name is a value to find. Each piece becomes a small function f(values, data).
    """

    def __init__(self, text, columns):
        super().__init__(text, columns)
        self.values_to_find: list[str] = []
        self.finished = False
        self._depth = 0

    def _column(self, name):
        if name not in self.used:
            self.used.append(name)
        return lambda p, d: d[name]

    def _node(self, node):
        self._depth += 1
        try:
            out = self._fit_node(node)
        finally:
            self._depth -= 1
        if self._depth == 0:
            self.finished = True
        return out

    def _value_name(self, name):
        if (name in FIT_FUNCTIONS and name not in FIT_NAMES_FREE) or name in ("round",):
            raise _fit_error(f"{name} needs brackets after it, for example {name}(hours).")
        close = difflib.get_close_matches(name, [str(c) for c in self.columns], n=1, cutoff=0.8)
        if close and len(name) > 1:
            raise _fit_error(
                f'"{name}" is not a column, so it would be a value to find. Did you mean the column "{close[0]}"?\n'
                "If you really mean a value to find, give it a name not so like a column, such as k."
            )
        if name not in self.values_to_find:
            self.values_to_find.append(name)
        return lambda p, d: p[name]

    def _fit_node(self, node):
        if isinstance(node, ast.Constant):
            if not _is_number(node.value):
                raise _fit_error(f"{node.value!r} is not allowed in a formula: only numbers and names are.")
            value = float(node.value)
            return lambda p, d: value
        if isinstance(node, ast.Name):
            if node.id in self.placeholders:
                return self._column(self.placeholders[node.id])
            if node.id in self.columns:
                return self._column(node.id)
            if node.id in CONSTANTS:
                value = CONSTANTS[node.id]
                return lambda p, d: value
            return self._value_name(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            inner = self._node(node.operand)
            return (lambda p, d: -inner(p, d)) if isinstance(node.op, ast.USub) else inner
        if isinstance(node, ast.BinOp):
            op = node.op
            if isinstance(op, ast.BitXor):
                raise _fit_error("For a power use ** instead of ^, for example hours ** 2.")
            if not isinstance(op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                raise _fit_error(f'The sign in "{self._snippet(node)}" is not allowed in a formula to fit.')
            left, right = self._node(node.left), self._node(node.right)
            if isinstance(op, ast.Add):
                return lambda p, d: left(p, d) + right(p, d)
            if isinstance(op, ast.Sub):
                return lambda p, d: left(p, d) - right(p, d)
            if isinstance(op, ast.Mult):
                return lambda p, d: left(p, d) * right(p, d)
            if isinstance(op, ast.Div):
                return lambda p, d: left(p, d) / right(p, d)
            return lambda p, d: np.power(left(p, d), right(p, d))
        if isinstance(node, ast.Call):
            return self._fit_call(node)
        if isinstance(node, ast.Attribute):
            raise _fit_error(f'"{self._snippet(node)}" is not allowed: a formula cannot use a dot after a name.')
        raise _fit_error(f'"{self._snippet(node)}" is not allowed in a formula.')

    def _fit_call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in FUNCTION_SPELLINGS:
            node.func.id = FUNCTION_SPELLINGS[node.func.id]
        if isinstance(node.func, ast.Name) and node.func.id in FIT_SPELLINGS:
            node.func.id = FIT_SPELLINGS[node.func.id]
        if not isinstance(node.func, ast.Name) or node.func.id not in FIT_FUNCTIONS:
            name = node.func.id if isinstance(node.func, ast.Name) else self._snippet(node.func)
            guess = difflib.get_close_matches(name, list(FIT_FUNCTIONS), n=1)
            hint = f" Did you mean {guess[0]}()?" if guess else ""
            raise _fit_error(f'"{name}()" is not allowed in a formula to fit.{hint}')
        name = node.func.id
        if node.keywords or any(isinstance(a, ast.Starred) for a in node.args):
            raise _fit_error(f"Write {name}() simply, like {name}(hours).")
        low, high = FIT_FUNCTIONS[name]
        if not low <= len(node.args) <= high:
            given = f"{len(node.args)} thing" + ("" if len(node.args) == 1 else "s")
            raise _fit_error(f"{name}() was given {given} inside the brackets.")
        if name in SPECIAL_FUNCTIONS:
            inside = [self._node(a) for a in node.args]
            return lambda p, d: special_function(name, *(f(p, d) for f in inside))
        if name == "arctan2":
            first, second = (self._node(a) for a in node.args)
            return lambda p, d: np.arctan2(first(p, d), second(p, d))
        inner = self._node(node.args[0])
        if name in FIT_NUMPY:
            numpy_function = FIT_NUMPY[name]
            return lambda p, d: numpy_function(inner(p, d))
        if name == "exp":
            return lambda p, d: np.exp(inner(p, d))
        if name == "sqrt":
            return lambda p, d: np.sqrt(inner(p, d))
        if name == "abs":
            return lambda p, d: np.abs(inner(p, d))
        if name == "sin":
            return lambda p, d: np.sin(inner(p, d))
        if name == "cos":
            return lambda p, d: np.cos(inner(p, d))
        if len(node.args) == 1:
            return lambda p, d: np.log(inner(p, d))
        base = node.args[1]
        if not (isinstance(base, ast.Constant) and _is_number(base.value)) or base.value <= 0 or base.value == 1:
            raise _fit_error("The base of log() must be a positive number other than 1, for example log(x, 10).")
        scale = math.log(float(base.value))
        return lambda p, d: np.log(inner(p, d)) / scale


# ---------------------------------------------------------------------------- the words
# fit_line, fit_curve and fit_formula live in fitting.py (FittingWords, a word group of Table).
class StatTestWords:
    # ------------------------------------------------------------------ helpers
    def _result_table(self, row: dict):
        """A one-row result table, on the same engine as this table."""
        frame = nw.from_dict({k: [v] for k, v in row.items()}, backend=self._frame.implementation)
        return self._new_table(frame)

    @staticmethod
    def _need_name(step: str, option: str, value, example: str):
        if not isinstance(value, str):
            raise SimplydataError(f"{step}() needs {option} as a column name in quotes.\nFor example, {example}")

    def _check_based_on(self, step, based_on):
        self._check_choice(step, "based_on", based_on, BASED_ON)

    @staticmethod
    def _check_bayesian(step, bayesian, prior_width="medium"):
        """bayesian= is True or False; prior_width= goes with bayesian=True (S3d-3)."""
        if bayesian not in (True, False) or not isinstance(bayesian, (bool, np.bool_)):
            raise SimplydataError(f"{step}() takes bayesian=True (the Bayesian answer) or bayesian=False (the usual "
                                  f"one); it got bayesian={bayesian!r}.")
        if not bayesian and prior_width != "medium":
            raise SimplydataError(f"prior_width= sets the prior of the Bayes factor; it goes with bayesian=True, such "
                                  f'as {step}(..., bayesian=True, prior_width="wide").')

    def _number_values(self, step: str, columns: list[str]):
        """The columns as float arrays, rows with an empty cell in any of them skipped (with a note)."""
        frame = self._number_frame(step, columns)
        kept = frame.select(*columns).drop_nulls()
        _skipped_note(len(frame) - len(kept), columns)
        return [kept[c].to_numpy().astype(float) for c in columns]

    def _groups(self, step: str, column, for_each, example: str):
        """[(group name, values)] sorted by group; empty cells skipped with a note."""
        self._need_name(step, "the column", column, example)
        self._need_name(step, "for_each_group_in=", for_each, example)
        self._need_columns(column, for_each)
        if column == for_each:
            raise SimplydataError(f'"{column}" cannot be both the column to compare and the for_each_group_in= column.\n'
                                  f"For example, {example}")
        frame = self._number_frame(step, [column])
        if frame.schema[for_each].is_float():
            frame = frame.with_columns(nw.col(for_each).fill_nan(None))
        kept = frame.select(for_each, column).drop_nulls()
        _skipped_note(len(frame) - len(kept), [column, for_each])
        keys = kept[for_each].to_list()
        values = kept[column].to_numpy().astype(float)
        order = sorted(set(keys), key=lambda k: (str(type(k)), k))
        keys = np.asarray(keys, dtype=object)
        groups = [(_label(k), values[keys == k]) for k in order]
        if len(groups) < 2:
            found = f'only "{groups[0][0]}"' if groups else "none"
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each}"; it found {found}.')
        small = [name for name, v in groups if len(v) < 2]
        if small:
            raise SimplydataError(
                f"{step}() needs at least 2 values in each group; "
                + _list_words(f'"{s}"' for s in small) + f' in "{for_each}" has fewer.\n'
                "Remove that group first, for example with table.remove_rows_where(...)."
            )
        return groups

    # ------------------------------------------------------------------ compare_averages_of
    @friendly(renamed={"between": "for_each_group_in", "for_each": "for_each_group_in", "seed": "with_seed"},
              others={"rscale": "prior_width", "prior_scale": "prior_width"})
    def compare_averages_of(self, column=None, for_each_group_in=None, based_on="averages", test=None, sides=2, higher=None,
                            lower=None, alternative=None, p_value_by="formula", shuffles=9999, with_seed=1,
                            same_within=None, not_lower=None, not_higher=None, in_order=None, matched_by=None,
                            grouped_by=None, bayesian=False, prior_width="medium"):
        """Are the averages of the groups really different?

        table.compare_averages_of("marks", for_each_group_in="class")   (with sdata.get_example("marks"))
        Two groups: Welch's t-test (the R t.test() default). Three or more: Welch's one-way
        ANOVA (the R oneway.test() default). Neither needs the groups to have the same spread.
        based_on="ranks" uses ranks instead (Mann-Whitney U or Kruskal-Wallis): safer when
        groups are small and their values are not bell-shaped. test= chooses another test:
        "welch", "student", "welch anova", "anova", "mann-whitney" or "kruskal-wallis"; and
        "yuen" (Yuen's test of 20 % trimmed averages, R WRS2::yuen, SciPy ttest_ind(trim=0.2)),
        "brunner-munzel" (R brunnermunzel.test, SciPy brunnermunzel), "alexander-govern" (3 or
        more groups with different spreads, R onewaytests::ag.test, SciPy alexandergovern) or
        "median" (Mood's median test, SciPy median_test, as R chisq.test on the counts above and
        not above the overall median).
        Prints the answer in words (with the test used and why) and gives back a one-row
        table of results. The effect size says how big the difference is: Hedges' g (the
        difference in standard deviations) for 2 groups, omega-squared (the share of the
        differences explained by the groups) for 3 or more. Each group is checked for a
        bell shape (Shapiro-Wilk) and a note says if it does not look like one; with 30 or
        more values that matters little (the central limit theorem).
        To see which groups differ, use compare_each_pair_of().
        sides=1, higher="B" (or lower="A") tests in one direction only (2 groups): that B is
        higher, as decided before seeing the data (R t.test(alternative = ...), wilcox.test(
        alternative = ...)); the 95 % interval is then one-sided too. R's and SciPy's
        alternative= is accepted.
        p_value_by="shuffling" (2 groups, averages): the p-value comes from shuffling the group
        labels shuffles=9999 times (with_seed=1) and counting how often the difference in averages is
        as big as the one in the data (SciPy permutation_test, as R perm::permTS()). When there
        are no more arrangements than shuffles, every one is counted and the p-value is exact.
        same_within=5 (2 groups) asks whether the averages are the same within 5 (or within
        [-3, 5]): two one-sided tests (TOST, Welch; statsmodels ttost_ind, as R TOSTER::t_TOST()),
        with the 90 % interval. The answer is one of three: the same within the margin,
        different, or the data cannot tell. same_within=5, not_lower="B" is a non-inferiority
        test: is B lower than A by no more than 5? (one-sided; as R TOSTER::t_TOST(hypothesis =
        "MET")). not_higher="B" asks whether B is higher by no more than 5, for outcomes where
        lower is better, such as pain.
        matched_by="name" is for repeated measures: the same person (or plot, animal ...) in every
        group of for_each_group_in=, for example compare_averages_of("marks", for_each_group_in="subject",
        matched_by="name"). It runs a repeated-measures ANOVA with the Greenhouse-Geisser
        correction, R afex::aov_ez() (needs R). for_each_group_in=["subject", "class"] with one column that
        changes within a person and one that does not gives the mixed ANOVA.
        grouped_by="tank" is for several rows from each tank, each tank in one group (nested): a
        nested ANOVA that tests the groups against the differences between tanks, R aov(length ~
        diet + Error(tank)) (needs R). A list of columns, compare_averages_of(["length", "width"],
        for_each_group_in="species"), compares them all at once: a MANOVA with Pillai's trace
        (statsmodels MANOVA, as R summary(manova())).
        Under a survey design (table.use_survey_design) two groups are compared by the design-based t
        test, R survey::svyttest.
        bayesian=True (two groups) gives the Bayes factor and a 95 % credible interval of the difference
        instead of a p-value: R BayesFactor::ttestBF() with the JZS prior (Rouder et al. 2009), whose width
        prior_width= sets: "medium" (0.707, the default), "wide" (1), "ultrawide" (1.414) or a number. The
        interval comes from 10,000 posterior draws (with_seed=1). Needs R (BayesFactor).
        """
        if self._survey_on():
            self._survey_only("compare_averages_of", locals(), ("column", "for_each_group_in"))
            return self._survey_compare_averages(column, for_each_group_in)
        step = "compare_averages_of"
        if bayesian is not False or prior_width != "medium":
            from . import bayes_r, bayes_words

            self._check_bayesian(step, bayesian, prior_width)
            bayes_words.check_bayes_options(step, [
                ("based_on=", based_on, "averages"), ("test=", test, None), ("sides=", sides, 2),
                ("higher=", higher, None), ("lower=", lower, None), ("alternative=", alternative, None),
                ("p_value_by=", p_value_by, "formula"), ("shuffles=", shuffles, 9999),
                ("same_within=", same_within, None), ("not_lower=", not_lower, None),
                ("not_higher=", not_higher, None), ("in_order=", in_order, None), ("matched_by=", matched_by, None),
                ("grouped_by=", grouped_by, None)])
            if isinstance(column, (list, tuple)):
                raise SimplydataError("bayesian=True compares one column between two groups; give one column.")
            seed = bayes_words.check_seed(with_seed)
            width = bayes_r.width_value(prior_width)
            groups = self._groups(step, column, for_each_group_in,
                                  'with sdata.get_example("marks"): table.compare_averages_of("marks", '
                                  'for_each_group_in="class", bayesian=True)')
            if len(groups) != 2:
                raise SimplydataError(f'bayesian=True compares the averages of 2 groups; "{for_each_group_in}" has '
                                      f"{len(groups)}. Keep two groups first (table.keep_rows_where(...)), or leave "
                                      "out bayesian=True for Welch's ANOVA.")
            return bayes_words.two_groups(self, column, for_each_group_in, groups, width, seed)
        # S3a-3 (checking and comparing): nested ANOVA and MANOVA (table/checking_more.py)
        if grouped_by is not None or isinstance(column, (list, tuple)):
            from .checking_more import manova, nested_averages

            given = [name for name, value, default in (
                ("based_on=", based_on, "averages"), ("test=", test, None), ("sides=", sides, 2),
                ("higher=", higher, None), ("lower=", lower, None), ("alternative=", alternative, None),
                ("p_value_by=", p_value_by, "formula"), ("same_within=", same_within, None),
                ("not_lower=", not_lower, None), ("not_higher=", not_higher, None), ("in_order=", in_order, None),
                ("matched_by=", matched_by, None)) if value != default]
            if given:
                what = "grouped_by= (a nested ANOVA)" if grouped_by is not None else "a list of columns (a MANOVA)"
                raise SimplydataError(f"{_list_words(given)} cannot be used with {what}.")
            if isinstance(column, (list, tuple)):
                if grouped_by is not None:
                    raise SimplydataError("A list of columns (a MANOVA) cannot be used with grouped_by= yet.")
                return manova(self, list(column), for_each_group_in)
            return nested_averages(self, column, for_each_group_in, grouped_by)
        if matched_by is not None:
            if based_on != "averages" or test is not None:
                raise SimplydataError('matched_by= runs a repeated-measures ANOVA on averages; leave out based_on= '
                                      "and test= (for two matched columns side by side, compare_before_and_after() "
                                      "has a rank test).")
            if (sides != 2 or higher is not None or lower is not None or alternative not in (None, "two-sided")
                    or p_value_by != "formula" or same_within is not None or not_lower is not None
                    or not_higher is not None or in_order is not None):
                raise SimplydataError("matched_by= runs a repeated-measures ANOVA, which looks for any difference; "
                                      "leave out sides=, higher=, lower=, p_value_by=, same_within=, not_lower=, "
                                      "not_higher= and in_order=.")
            return self._repeated_averages(column, for_each_group_in, matched_by)
        example = 'with sdata.get_example("marks"): table.compare_averages_of("marks", for_each_group_in="class")'
        self._check_based_on(step, based_on)
        self._check_choice(step, "p_value_by", p_value_by, ("formula", "shuffling"))
        if test is not None:
            self._check_choice(step, "test", test, AVERAGE_TESTS)
            if based_on == "ranks" and test not in RANK_LIKE:
                raise SimplydataError(
                    f'test="{test}" compares averages, but based_on="ranks" asks for ranks. '
                    'Use one of them: test="mann-whitney" or test="kruskal-wallis" are the rank tests.'
                )
        groups = self._groups(step, column, for_each_group_in, example)
        k = len(groups)
        names = [g[0] for g in groups]
        sides, higher, lower, claim = _non_inferiority(
            step, same_within, sides, higher, lower, not_lower, not_higher, names if k == 2 else [],
            f'table.compare_averages_of("{column}", for_each_group_in="{for_each_group_in}", same_within=5, not_lower="{names[-1]}")')
        if test == "jonckheere" or in_order is not None:
            if test != "jonckheere":
                raise SimplydataError('in_order= gives the order of the groups for a trend test: test="jonckheere".')
            return self._jonckheere(step, column, for_each_group_in, groups, in_order)
        if (sides != 2 or higher is not None or lower is not None or alternative not in (None, "two-sided")) \
                and k != 2:
            raise SimplydataError(
                f"A test of {k} groups looks for any difference between them, so it has no one direction; "
                f'sides=1 and higher= work with 2 groups.\nUse the usual two-sided test, or compare two groups at a '
                f'time with table.compare_each_pair_of("{column}", for_each_group_in="{for_each_group_in}").')
        side_example = f'table.compare_averages_of("{column}", for_each_group_in="{for_each_group_in}", sides=1, higher="{names[-1]}")'
        alt, up = _direction(step, sides, higher, lower, alternative, {names[0]: "greater", names[1]: "less"}
                             if k == 2 else {}, side_example)
        side_words = ""
        if_none = "there were truly no difference"
        if up is not None:
            down = names[1] if up == names[0] else names[0]
            side_words = _one_sided_sentence(f"{up} higher than {down}", f"{up} lower")
            if_none = f"{up} were truly not higher than {down}"
        if test is None:
            if based_on == "ranks":
                test = "mann-whitney" if k == 2 else "kruskal-wallis"
            else:
                test = "welch" if k == 2 else "welch anova"
            chosen = False
        else:
            chosen = True
        if test in TWO_GROUP_TESTS and k != 2:
            other = "kruskal-wallis" if test == "mann-whitney" else "welch anova"
            raise SimplydataError(
                f'test="{test}" compares exactly 2 groups, but "{for_each_group_in}" has {k}.\n'
                f'Use test="{other}" for all groups at once, or table.compare_each_pair_of("{column}", for_each_group_in="{for_each_group_in}").'
            )
        if same_within is not None:
            if k != 2 or test not in ("welch",) or p_value_by != "formula":
                raise SimplydataError("same_within= compares the averages of 2 groups (Welch); leave out test=, "
                                      "based_on= and p_value_by=.")
            (n1, a), (n2, b) = groups
            return self._same_within(step, "two groups", (a, b), same_within, up, n1, n2, "Welch",
                                     "TOSTER::t_TOST()", {f"count in {n1}": len(a), f"count in {n2}": len(b),
                                                          f"average in {n1}": float(a.mean()),
                                                          f"average in {n2}": float(b.mean())}, claim)
        if p_value_by == "shuffling" and (k != 2 or test not in ("welch", "student")):
            raise SimplydataError('p_value_by="shuffling" works for the difference between the averages of 2 groups '
                                  "(Welch's or Student's t-test); leave it out here.")
        if test in MORE_AVERAGE_TESTS:
            return self._more_average_test(column, for_each_group_in, groups, test, alt, up, side_words, if_none)
        arrays = [g[1] for g in groups]
        what = f'the average of "{column}" in each "{for_each_group_in}" ({", ".join(names)})'
        row = {"test": None, "what it compares": what}
        means = [float(v.mean()) for v in arrays]
        if test not in RANK_TESTS:
            spread = [float(v.std(ddof=1)) for v in arrays]
            if all(s == 0 for s in spread) or (test in ("welch anova",) and any(s == 0 for s in spread)):
                flat = [n for n, s in zip(names, spread) if s == 0]
                groups = _list_words('"' + str(n) + '"' for n in flat)
                raise SimplydataError(
                    f'Every value is the same within {groups}, so a test on averages '
                    f'cannot measure the spread there. Use based_on="ranks", or check the data.'
                )
        from scipy import stats

        notes = []
        if test in ("welch", "student"):
            a, b = arrays
            result = stats.ttest_ind(a, b, equal_var=(test == "student"), alternative=alt)
            low, high = result.confidence_interval(0.95)
            t, p, df = float(result.statistic), float(result.pvalue), float(result.df)
            es = effect_size("hedges_g", a=a, b=b)
            g = es["value"]
            diff = means[0] - means[1]
            name = "Welch's t-test" if test == "welch" else "Student's t-test"
            why = (
                "the usual test for two averages; it does not assume both groups have the same spread"
                if test == "welch" else "chosen with test=; it assumes both groups have the same spread"
            )
            row.update({"test": name, "statistic name": "t", "statistic": t, "degrees of freedom": df,
                        "p-value": p, "effect size name": "difference in standard deviations (Hedges' g)",
                        "effect size": float(g), "effect size 95 % CI low": es["low"],
                        "effect size 95 % CI high": es["high"], "difference": diff,
                        "difference 95 % CI low": float(low), "difference 95 % CI high": float(high)})
            direction = "higher" if diff > 0 else "lower"
            first = (f'The average "{column}" is {_num(means[0])} in {names[0]} and {_num(means[1])} in {names[1]}: '
                     f"{names[0]} is {_num(abs(diff))} {direction} ({'' if up is None else 'one-sided '}95 % CI of "
                     f"the difference {_interval_words(low, high)}"
                     + ("" if es["note"] else f"; Hedges' g = {_num(g)}{interval_text(es['low'], es['high'])}, a "
                        f"difference of {_num(abs(g))} standard deviations")
                     + ").")
            second = f"Test: {name} (t = {_num(t)}, df = {_whole(df)}), {why}."
            if p_value_by == "shuffling":
                from .resampling import difference_in_averages, resample_p

                found = resample_p((a, b), difference_in_averages, "independent", alt, shuffles, with_seed)
                p = found["p"]
                row.update({"p-value": p, "p-value by": found["method"]})
                second += (f" The p-value comes from shuffling, not from the t distribution: {found['words']} "
                           "(SciPy permutation_test, as R perm::permTS()).")
            p_line = _p_sentence(p, if_none)
            notes = ([es["note"]] if es["note"] else []) + _shape_notes([(f'group "{n}"', v) for n, v in groups])
        elif test in ("welch anova", "anova"):
            if test == "welch anova":
                f, df1, df2, p = _welch_anova(arrays)
                name = "Welch's one-way ANOVA"
                why = ("the usual test for three or more averages; it does not assume the groups have the same spread"
                       if not chosen else "it does not assume the groups have the same spread")
            else:
                result = stats.f_oneway(*arrays)
                f, p = float(result.statistic), float(result.pvalue)
                df1, df2 = k - 1.0, float(sum(len(v) for v in arrays) - k)
                name = "one-way ANOVA"
                why = "chosen with test=; it assumes the groups have the same spread"
            es = effect_size("omega_squared", y=np.concatenate(arrays),
                             g=np.repeat(np.array(names, dtype=object), [len(v) for v in arrays]))
            omega = es["value"]
            row.update({"test": name, "statistic name": "F", "statistic": f, "degrees of freedom 1": df1,
                        "degrees of freedom 2": df2, "p-value": p,
                        "effect size name": "share of the differences explained by the groups (omega-squared)",
                        "effect size": omega, "effect size 95 % CI low": es["low"], "effect size 95 % CI high": es["high"]})
            averages = _list_words(f"{_num(m)} in {n}" for n, m in zip(names, means))
            first = f'The average "{column}" is {averages}.'
            p_line = _p_sentence(p, *ALIKE)
            if not es["note"]:
                share = f"about {_percent(omega)}" if omega > 0 else "about 0 % (R effectsize reads a value below 0 as 0)"
                first += (f" Omega-squared = {_num(omega)}{interval_text(es['low'], es['high'])}: the groups explain "
                          f'{share} of the differences in "{column}".')
            second = f"Test: {name} (F = {_num(f)}, df = {_whole(df1)} and {_whole(df2)}), {why}."
            if k > 2:
                second += f' To see which groups differ: table.compare_each_pair_of("{column}", for_each_group_in="{for_each_group_in}").'
            notes = ([es["note"]] if es["note"] else []) + _shape_notes([(f'group "{n}"', v) for n, v in groups])
        elif test == "mann-whitney":
            a, b = arrays
            u, p, how = _mann_whitney(a, b, alt)
            es = effect_size("rank_biserial", a=a, b=b)
            r = es["value"]
            medians = [float(np.median(v)) for v in arrays]
            row.update({"test": "Mann-Whitney U test", "statistic name": "U", "statistic": u, "p-value": p,
                        "effect size name": "how far one group's values lie above the other's, -1 to 1 "
                                            "(rank-biserial correlation)",
                        "effect size": r, "effect size 95 % CI low": es["low"], "effect size 95 % CI high": es["high"]})
            half = len(a) * len(b) / 2  # U above half of its largest value: the first group tends to be higher
            lean = f"the values in {names[0]} tend to be higher" if u > half else (
                f"the values in {names[0]} tend to be lower" if u < half else "neither group tends to be higher")
            size = "" if es["note"] else f" (rank-biserial correlation = {_num(r)}{interval_text(es['low'], es['high'])})"
            shift = _hodges_lehmann(a, b, how.startswith("exact"), alt)
            row.update({"shift": shift["value"], "shift 95 % CI low": shift["low"],
                        "shift 95 % CI high": shift["high"],
                        "method": "shift: Hodges-Lehmann estimate and interval (R wilcox.test(conf.int = TRUE))"})
            moved = "" if shift["note"] else (
                f'; the typical shift from {names[1]} to {names[0]} (Hodges-Lehmann) is {_num(shift["value"])}, '
                f"values from {_interval_words(shift['low'], shift['high'])} fit the data (95 % CI)")
            first = (f'The median "{column}" is {_num(medians[0])} in {names[0]} and {_num(medians[1])} in {names[1]}: '
                     f"{lean}{size}{moved}.")
            p_line = _p_sentence(p, if_none)
            notes = [n for n in (es["note"], shift["note"]) if n]
            second = (f"Test: Mann-Whitney U test (U = {_whole(u)}, {how}), which compares ranks rather than "
                      "averages, so it does not need bell-shaped values.")
        else:
            result = stats.kruskal(*arrays)
            h, p = float(result.statistic), float(result.pvalue)
            es = effect_size("rank_epsilon_squared", y=np.concatenate(arrays),
                             g=np.repeat(np.array(names, dtype=object), [len(v) for v in arrays]))
            eps = es["value"]
            medians = [float(np.median(v)) for v in arrays]
            row.update({"test": "Kruskal-Wallis test", "statistic name": "H", "statistic": h,
                        "degrees of freedom": float(k - 1), "p-value": p,
                        "effect size name": "share of the rank differences explained by the groups "
                                            "(rank epsilon-squared)",
                        "effect size": eps, "effect size 95 % CI low": es["low"], "effect size 95 % CI high": es["high"]})
            first = f'The median "{column}" is {_list_words(f"{_num(m)} in {n}" for n, m in zip(names, medians))}.'
            p_line = _p_sentence(p, *ALIKE)
            if not es["note"]:
                ci = interval_text(es["low"], es["high"]).replace("95 % CI", "95 % bootstrap CI, R seed 1,")
                first += (f" Epsilon-squared = {_num(eps)}{ci}: the groups explain "
                          f"about {_percent(eps)} of the differences in the ranks.")
            notes = [es["note"]] if es["note"] else []
            second = (f"Test: Kruskal-Wallis test (H = {_num(h)}, df = {k - 1}), which compares ranks rather than "
                      "averages, so it does not need bell-shaped values.")
            if k > 2:
                second += (f' To see which groups differ: table.compare_each_pair_of("{column}", for_each_group_in="{for_each_group_in}", '
                           'based_on="ranks").')
        for name, v in groups:
            row[f"count in {name}"] = len(v)
            row[f"average in {name}"] = float(v.mean())
            if test in RANK_TESTS:
                row[f"median in {name}"] = float(np.median(v))
        if up is not None:
            row["sides"] = f"one-sided: {up} higher"
            second += " " + side_words
        print(first)
        print(p_line)
        print(second)
        for note in notes:
            print(note)
        return self._result_table(row)

    def _jonckheere(self, step, column, for_each, groups, in_order):
        """The Jonckheere-Terpstra test for a trend across ordered groups (statsmodels jonckheere_terpstra, two-sided;
        R clinfun::jonckheere.test agrees to about 1e-4, the two treat ties a little differently)."""
        from statsmodels.stats.nonparametric import jonckheere_terpstra

        by_name = dict(groups)
        if in_order is None or isinstance(in_order, str) or not hasattr(in_order, "__iter__"):
            raise SimplydataError(f'test="jonckheere" needs the "{for_each}" groups in order: in_order=['
                                  + ", ".join(f'"{n}"' for n in by_name) + "] (lowest first).")
        order = [str(g) for g in in_order]
        if sorted(order) != sorted(by_name):
            raise SimplydataError(f'in_order= must list every "{for_each}" group once: '
                                  + _list_words(f'"{n}"' for n in by_name) + ".")
        samples = [by_name[g] for g in order]
        result = jonckheere_terpstra(samples, alternative="two-sided")
        stat, p = float(result.statistic), float(result.pvalue)
        medians = [float(np.median(v)) for v in samples]
        listed = _list_words(f'{_num(m)} in {g}' for g, m in zip(order, medians))
        print(f'The median "{column}" is {listed} (in this order).')
        print(_p_sentence(p, "there were truly no trend across the groups", "a trend this strong or stronger",
                          "that there is no trend"))
        print(f"Test: Jonckheere-Terpstra test for a trend across ordered groups (JT = {_whole(stat)}, normal "
              "approximation), two-sided: it looks for values that rise or fall along the order you gave; "
              "statsmodels jonckheere_terpstra, as R clinfun::jonckheere.test().")
        row = {"test": "Jonckheere-Terpstra test", "what it compares": f'"{column}" across "{for_each}" in the order '
               + ", ".join(order), "statistic name": "JT", "statistic": stat, "p-value": p}
        for g, m, v in zip(order, medians, samples):
            row[f"median in {g}"] = m
            row[f"count in {g}"] = len(v)
        return self._result_table(row)

    def _more_average_test(self, column, for_each, groups, test, alt, up, side_words, if_none):
        """compare_averages(test="yuen" | "brunner-munzel" | "alexander-govern" | "median"): SciPy, as R."""
        from scipy import stats

        names = [g[0] for g in groups]
        arrays = [g[1] for g in groups]
        if up is not None and test in ("alexander-govern", "median"):
            raise SimplydataError(f'test="{test}" looks for any difference, so it has no one direction; leave out '
                                  "sides= and higher=.")
        row = {"test": None, "what it compares": f'"{column}" in each "{for_each}" ({", ".join(names)})'}
        if test == "yuen":
            a, b = arrays
            result = stats.ttest_ind(a, b, trim=0.2, equal_var=False, alternative=alt)
            low, high = result.confidence_interval(0.95)
            t, p, df = float(result.statistic), float(result.pvalue), float(result.df)
            trimmed = [float(stats.trim_mean(v, 0.2)) for v in arrays]
            diff = trimmed[0] - trimmed[1]
            row.update({"test": "Yuen's test (20 % trimmed averages)", "statistic name": "t", "statistic": t,
                        "degrees of freedom": df, "p-value": p, "difference": diff,
                        "difference 95 % CI low": float(low), "difference 95 % CI high": float(high)})
            for n, m in zip(names, trimmed):
                row[f"trimmed average in {n}"] = m
            first = (f'The 20 % trimmed average "{column}" is {_num(trimmed[0])} in {names[0]} and {_num(trimmed[1])} in '
                     f"{names[1]}: {names[0]} is {_num(abs(diff))} {'higher' if diff > 0 else 'lower'} "
                     f"({'' if up is None else 'one-sided '}95 % CI of the difference {_interval_words(low, high)}).")
            p_line = _p_sentence(p, if_none)
            second = (f"Test: Yuen's test (t = {_num(t)}, df = {_whole(df)}), which leaves out the lowest and highest "
                      "20 % of each group, so a few extreme values matter less; as R WRS2::yuen(tr = 0.2).")
        elif test == "brunner-munzel":
            a, b = arrays
            result = stats.brunnermunzel(a, b, alternative=alt)
            w, p = float(result.statistic), float(result.pvalue)
            medians = [float(np.median(v)) for v in arrays]
            row.update({"test": "Brunner-Munzel test", "statistic name": "W", "statistic": w, "p-value": p})
            for n, m in zip(names, medians):
                row[f"median in {n}"] = m
            first = f'The median "{column}" is {_num(medians[0])} in {names[0]} and {_num(medians[1])} in {names[1]}.'
            p_line = _p_sentence(p, if_none, "a difference this big or bigger in how often one group's values beat "
                                 "the other's")
            second = (f"Test: Brunner-Munzel test (W = {_num(w)}), a rank test that, unlike Mann-Whitney, allows the "
                      "groups to differ in spread and shape; as R brunnermunzel::brunnermunzel.test().")
        elif test == "alexander-govern":
            result = stats.alexandergovern(*arrays)
            a_stat, p = float(result.statistic), float(result.pvalue)
            means = [float(v.mean()) for v in arrays]
            row.update({"test": "Alexander-Govern test", "statistic name": "A", "statistic": a_stat,
                        "degrees of freedom": float(len(arrays) - 1), "p-value": p})
            for n, m in zip(names, means):
                row[f"average in {n}"] = m
            first = f'The average "{column}" is {_list_words(f"{_num(m)} in {n}" for n, m in zip(names, means))}.'
            p_line = _p_sentence(p, *ALIKE)
            second = (f"Test: Alexander-Govern test (A = {_num(a_stat)}, df = {len(arrays) - 1}), which, like Welch's "
                      "ANOVA, does not assume the groups have the same spread; as R onewaytests::ag.test().")
        else:
            result = stats.median_test(*arrays)
            chi, p, grand = float(result.statistic), float(result.pvalue), float(result.median)
            above = result.table[0]
            row.update({"test": "Mood's median test", "statistic name": "chi-square", "statistic": chi,
                        "degrees of freedom": float(len(arrays) - 1), "p-value": p, "overall median": grand})
            for n, v, a_count in zip(names, arrays, above):
                row[f"median in {n}"] = float(np.median(v))
                row[f"above the overall median in {n}"] = int(a_count)
            shares = _list_words(f"{int(a)} of {len(v)} in {n}" for n, v, a in zip(names, arrays, above))
            first = f'Values of "{column}" above the overall median ({_num(grand)}): {shares}.'
            p_line = _p_sentence(p, *ALIKE)
            second = (f"Test: Mood's median test (chi-square = {_num(chi)}, df = {len(arrays) - 1}), the chi-square "
                      "test on the counts above and not above the overall median; as R chisq.test(table(group, x > "
                      "median(x))).")
        for n, v in zip(names, arrays):
            row[f"count in {n}"] = len(v)
        if up is not None:
            row["sides"] = f"one-sided: {up} higher"
            second += " " + side_words
        print(first)
        print(p_line)
        print(second)
        return self._result_table(row)

    # ------------------------------------------------------------------ compare_each_pair_of
    @friendly(renamed={"between": "for_each_group_in", "for_each": "for_each_group_in", "seed": "with_seed"})
    def compare_each_pair_of(self, column=None, for_each_group_in=None, based_on="averages", test=None, against=None, with_seed=1,
                             show="pairs", matched_by=None, value=None):
        """Which pairs of groups differ? Every pair is compared, with Holm's correction.

        table.compare_each_pair_of("marks", for_each_group_in="class")   (with sdata.get_example("marks"))
        Each pair gets Welch's t-test (or Mann-Whitney U with based_on="ranks"). Testing many
        pairs makes a false alarm more likely, so the p-values are adjusted with Holm's
        method: the chance of at least one false alarm stays at 5 %. This is the same as R
        pairwise.t.test(pool.sd = FALSE, p.adjust.method = "holm"). Gives back a table with
        one row per pair.
        test="tukey" gives Tukey's honest significant difference instead (R
        TukeyHSD(aov(marks ~ class)), the Tukey-Kramer form when the groups differ in size):
        the textbook follow-up to a one-way ANOVA, with 95 % confidence intervals that hold
        for all pairs at once. It assumes the groups have the same spread; the default does
        not. test="welch" and test="mann-whitney" name the other two choices.
        More follow-up tests, each run in R (simplydata[r]): test="games-howell" (like Tukey, but
        for groups with different spreads; R rstatix::games_howell_test()), "scheffe" (R
        DescTools::ScheffeTest()), "lsd" (Fisher's least significant difference, NOT adjusted for
        the number of pairs; R DescTools::PostHocTest(method = "lsd")), and for ranks "dunn" (R
        FSA::dunnTest(method = "holm")) and "conover" (R PMCMRplus::kwAllPairsConoverTest(
        p.adjust.method = "holm")).
        against="A" compares every group with one control group only: Dunnett's test (SciPy
        stats.dunnett, as R multcomp::glht(mcp(group = "Dunnett"))), with intervals that hold for
        all the comparisons at once. SciPy works it out with random numbers, so with_seed=1 is used
        (printed); the last digit can differ from R's.
        show="letters" gives each group letters instead (a compact letter display, R
        multcompView::multcompLetters()): groups that share a letter have an adjusted p-value of
        0.05 or more between them. It works with every test= above, and gives back one row per
        group.
        matched_by="patient": the same rows (patients) were measured in every group, such as pain
        at week 0, 4 and 8 in long form. Each pair is then compared within the patients: paired
        t-tests, or with based_on="ranks" (after compare_matched_columns's Friedman test) the Wilcoxon
        signed-rank test, with Holm's correction (SciPy, as R pairwise.t.test(paired = TRUE) and
        pairwise.wilcox.test(paired = TRUE)). After Friedman's test, test="nemenyi" gives Nemenyi's
        test (R PMCMRplus::frdAllPairsNemenyiTest(), which allows for all the pairs itself: no further
        adjustment) and test="conover" Conover's test (R PMCMRplus::frdAllPairsConoverTest(
        p.adjust.method = "holm")); both work on the ranks within each matched row.
        based_on="percents" with a column of two values (value="yes" names the one counted)
        compares the percent of each pair of groups: the 2 x 2 chi-square test with Yates'
        correction that compare_counts_of uses (SciPy), or test="fisher" (Fisher's exact test), then
        Holm's correction; each pair also gets its difference in percentage points with Newcombe's
        95 % interval, as compare_risks (statsmodels). The same as R pairwise.prop.test().
        table.compare_each_pair_of("resistant", for_each_group_in="farm", based_on="percents", value="yes")
        """
        step = "compare_each_pair_of"
        self._check_choice(step, "show", show, ("pairs", "letters"))
        if based_on == "percents":
            if matched_by is not None or against is not None or show != "pairs":
                raise SimplydataError('based_on="percents" compares the percent of every pair of groups; leave out '
                                      "matched_by=, against= and show=.")
            return self._percent_pairs(step, column, for_each_group_in, value, test)
        if value is not None:
            raise SimplydataError('value= names the value that is counted, so it goes with based_on="percents".\n'
                                  'For example:  table.compare_each_pair_of("resistant", for_each_group_in="farm", '
                                  'based_on="percents", value="yes")')
        if matched_by is not None:
            if isinstance(test, str):
                test = FRIEDMAN_PAIR_ALIASES.get(test.strip().lower(), test.strip().lower())
            if (test is not None and test not in FRIEDMAN_PAIR_TESTS) or against is not None or show != "pairs":
                raise SimplydataError("matched_by= gives paired tests of each pair (Holm); after Friedman's test "
                                      'test="nemenyi" or test="conover" are the other choices. Otherwise leave out '
                                      "test=, and leave out against= and show=.")
            return self._matched_pairs(step, column, for_each_group_in, matched_by, based_on, test)
        if show == "letters" and against is not None:
            raise SimplydataError("show=\"letters\" compares every pair; against= compares each group with one "
                                  "control only. Leave out one of them.")
        pairs = self._each_pair(step, column, for_each_group_in, based_on, test, against, with_seed)
        if show == "pairs":
            return pairs
        return self._pair_letters(column, for_each_group_in, pairs)

    def _matched_pairs(self, step, column, for_each, matched_by, based_on, test=None):
        """Paired tests of each pair of groups within the matched rows, Holm-adjusted; or Nemenyi's or Conover's test
        after Friedman's (test=)."""
        from scipy import stats

        example = 'table.compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient", based_on="ranks")'
        self._check_based_on(step, based_on)
        if test is not None:
            based_on = "ranks"  # Nemenyi and Conover work on the ranks within each matched row
        for option, value in (("the column", column), ("for_each_group_in=", for_each), ("matched_by=", matched_by)):
            self._need_name(step, option, value, example)
        if len({column, for_each, matched_by}) != 3:
            raise SimplydataError(f"{step}() needs three different columns.\nFor example, {example}")
        frame = self._number_frame(step, [column])
        floats = [c for c in (for_each, matched_by) if frame.schema[c].is_float()]
        if floats:
            frame = frame.with_columns(nw.col(c).fill_nan(None) for c in floats)
        kept = frame.select(matched_by, for_each, column).drop_nulls()
        _skipped_note(len(frame) - len(kept), [column, for_each, matched_by])
        cells = {}
        for who, group, value in zip(kept[matched_by].to_list(), kept[for_each].to_list(),
                                     kept[column].to_numpy().astype(float)):
            if (who, group) in cells:
                raise SimplydataError(f'"{_label(who)}" has more than one row for "{_label(group)}"; matched_by= needs '
                                      f'one value per "{matched_by}" in each "{for_each}" group.')
            cells[(who, group)] = value
        groups = sorted({g for _, g in cells}, key=lambda k: (str(type(k)), k))
        people = sorted({w for w, _ in cells}, key=lambda k: (str(type(k)), k))
        complete = [w for w in people if all((w, g) in cells for g in groups)]
        if len(complete) < len(people):
            print(f'Note: {len(people) - len(complete)} of the {len(people)} "{matched_by}" values were not measured in '
                  f'every "{for_each}" group and were left out.')
        if len(groups) < 2 or len(complete) < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups and 2 "{matched_by}" values measured in each.')
        data = {g: np.array([cells[(w, g)] for w in complete]) for g in groups}
        if test is not None:
            return self._friedman_pairs(column, for_each, matched_by, groups, complete, data, test)
        rows = []
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                g1, g2 = groups[i], groups[j]
                a, b = data[g1], data[g2]
                row = {"group 1": _label(g1), "group 2": _label(g2)}
                if based_on == "averages":
                    result = stats.ttest_rel(a, b)
                    low, high = result.confidence_interval(0.95)
                    row.update({"test": "paired t-test", "difference": float(np.mean(a - b)),
                                "difference 95 % CI low": float(low), "difference 95 % CI high": float(high),
                                "statistic name": "t", "statistic": float(result.statistic),
                                "degrees of freedom": float(result.df), "p-value": float(result.pvalue)})
                else:
                    found = _signed_rank(a - b)
                    if found is None:
                        raise SimplydataError(f'Every "{matched_by}" has the same value in {_label(g1)} and '
                                              f"{_label(g2)}, so there is nothing to test.")
                    v, p, how, _, _ = found
                    row.update({"test": "Wilcoxon signed-rank test", "difference in medians":
                                float(np.median(a) - np.median(b)), "statistic name": "V", "statistic": v,
                                "p-value": p, "p-value by": how})
                row["rows"] = len(complete)
                rows.append(row)
        for row, p in zip(rows, _holm([r["p-value"] for r in rows])):
            row["p-value (Holm)"] = p
        test = "paired t-tests" if based_on == "averages" else "Wilcoxon signed-rank tests"
        r_name = ("pairwise.t.test(paired = TRUE)" if based_on == "averages" else "pairwise.wilcox.test(paired = TRUE)")
        print(f'Each pair of "{for_each}" groups compared on "{column}" within the same {len(complete)} "{matched_by}" '
              f"values with {test}; the p-values are adjusted for {len(rows)} pair{'' if len(rows) == 1 else 's'} with "
              f"Holm's method, so the chance of any false alarm stays at 5 %. As R {r_name}.")
        self._pair_lines(rows, "p-value (Holm)", "Holm-adjusted ")
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _friedman_pairs(self, column, for_each, matched_by, groups, complete, data, test):
        """compare_each_pair_of(matched_by=, test="nemenyi" | "conover"): R PMCMRplus after Friedman's test."""
        from .small_r import FRIEDMAN_PAIR_TESTS as TESTS, friedman_pairs

        if len(groups) < 3:
            raise SimplydataError(f'test="{test}" follows Friedman\'s test of 3 or more groups; "{for_each}" has '
                                  f"{len(groups)}. For two groups leave out test= (the Wilcoxon signed-rank test).")
        title, r_name, meaning = TESTS[test]
        found = friedman_pairs(test, groups, complete, data)
        rows = []
        for one in found:
            g1, g2 = groups[one["i"]], groups[one["j"]]
            row = {"group 1": _label(g1), "group 2": _label(g2), "test": title,
                   "mean rank in group 1": one["rank 1"], "mean rank in group 2": one["rank 2"],
                   "statistic name": one["dist"], "statistic": one["statistic"]}
            if one["dist"] == "t":
                row["degrees of freedom"] = one["df"]
            row.update({"p-value (adjusted)": one["p"], "rows": len(complete)})
            rows.append(row)
        pairs = "pair" if len(rows) == 1 else "pairs"
        print(f'Each pair of "{for_each}" groups compared on "{column}" within the same {len(complete)} '
              f'"{matched_by}" values with {title} (ranks within each "{matched_by}"), run in R as {r_name}: '
              f"{len(rows)} {pairs}; {meaning}.")
        null = f'the two groups had the same typical "{column}" (in ranks)'
        for row in rows:
            r1, r2 = row["mean rank in group 1"], row["mean rank in group 2"]
            where = "higher than" if r1 > r2 else "lower than" if r1 < r2 else "the same as"
            word = "Holm-adjusted " if test == "conover" else "Nemenyi "
            shown = word + _p_shown(row["p-value (adjusted)"])
            print(f"  {row['group 1']} vs {row['group 2']}: {row['group 1']} ranks {where} {row['group 2']} within "
                  f'each "{matched_by}" (mean rank {_num(r1)} against {_num(r2)}); '
                  f"{_p_clause(row['p-value (adjusted)'], null, shown=shown)}.")
        print("Note: tests of mean ranks such as these compare two groups through the ranks of all the groups, so "
              "the answer for one pair can change when another group is added or left out (Benavoli, Corani & "
              "Mangili 2016); the default, Wilcoxon signed-rank tests with Holm's correction, compares each pair "
              "on its own.")
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _percent_pairs(self, step, column, for_each, value, test):
        """compare_each_pair_of(based_on="percents"): each pair's 2 x 2 test (SciPy chi-square with Yates' correction,
        as compare_counts_of, or Fisher's exact test), Holm's adjustment (statsmodels), and the difference with
        Newcombe's interval (statsmodels), as R pairwise.prop.test()."""
        import warnings

        from scipy import stats
        from statsmodels.stats.proportion import confint_proportions_2indep, test_proportions_2indep

        from .risk_words import _event_value, _say_pct

        example = 'table.compare_each_pair_of("resistant", for_each_group_in="farm", based_on="percents", value="yes")'
        for option, given in (("the column", column), ("for_each_group_in=", for_each)):
            self._need_name(step, option, given, example)
        if column == for_each:
            raise SimplydataError(f"{step}() needs two different columns.\nFor example, {example}")
        if isinstance(test, str):
            test = test.strip().lower()
        if test is not None:
            self._check_choice(step, "test", test, PERCENT_PAIR_TESTS)
        kept = self._two_columns_frame(step, [column, for_each], example)
        outcomes = kept[column].to_list()
        event, event_words = _event_value(step, column, outcomes, value, option="value")
        keys = kept[for_each].to_list()
        groups = sorted(set(keys), key=lambda k: (str(type(k)), k))
        if len(groups) < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each}".')
        is_event = np.array([v == event for v in outcomes])
        keys_arr = np.asarray(keys, dtype=object)
        counts = [(g, int(is_event[keys_arr == g].sum()), int((keys_arr == g).sum())) for g in groups]
        fisher = test == "fisher"
        rows, low_expected = [], False
        for i in range(len(counts)):
            for j in range(i + 1, len(counts)):
                (g1, e1, n1), (g2, e2, n2) = counts[i], counts[j]
                tab = np.array([[e1, n1 - e1], [e2, n2 - e2]])
                share1, share2 = stats.binomtest(e1, n1).statistic, stats.binomtest(e2, n2).statistic
                with warnings.catch_warnings():  # statsmodels also works out an odds ratio, 1 / 0 when a share is 1
                    warnings.simplefilter("ignore", RuntimeWarning)
                    diff = float(test_proportions_2indep(e1, n1, e2, n2, compare="diff").diff)
                low, high = (float(v) for v in confint_proportions_2indep(e1, n1, e2, n2, method="newcomb",
                                                                          compare="diff"))
                empty_column = bool((tab.sum(axis=0) == 0).any())
                if fisher:
                    p, statistic, name = float(stats.fisher_exact(tab).pvalue), math.nan, "odds ratio"
                    statistic = float(stats.contingency.odds_ratio(tab, kind="conditional").statistic)
                elif empty_column:
                    p, statistic, name = math.nan, math.nan, "chi-square"  # as R prop.test(): NaN
                else:
                    chi = stats.chi2_contingency(tab, correction=True)
                    p, statistic, name = float(chi.pvalue), float(chi.statistic), "chi-square"
                    low_expected = low_expected or bool((chi.expected_freq < 5).any())
                rows.append({"group 1": _label(g1), "group 2": _label(g2),
                             "test": "Fisher's exact test" if fisher else "chi-square test with Yates' correction",
                             f"share {_label(event)} in group 1": float(share1),
                             f"share {_label(event)} in group 2": float(share2),
                             "difference": diff, "difference 95 % CI low": low, "difference 95 % CI high": high,
                             "statistic name": name, "statistic": statistic, "p-value": p,
                             f"{_label(event)} in group 1": e1, "count in group 1": n1,
                             f"{_label(event)} in group 2": e2, "count in group 2": n2})
        given = [r["p-value"] for r in rows if not math.isnan(r["p-value"])]
        adjusted = iter(_holm(given))
        for row in rows:
            row["p-value (Holm)"] = math.nan if math.isnan(row["p-value"]) else next(adjusted)
        shown = _list_words(f"{e} of {n} ({_say_pct(stats.binomtest(e, n).statistic)}) in {_label(g)}"
                            for g, e, n in counts[:GROUPS_SHOWN])
        print(f'"{column}" = {event_words}: {shown}{" ..." if len(counts) > GROUPS_SHOWN else ""}.')
        how = ("Fisher's exact test (SciPy fisher_exact), as R rstatix::pairwise_fisher_test(p.adjust.method = "
               '"holm")' if fisher else
               "the chi-square test with Yates' continuity correction, the 2 x 2 test of compare_counts_of (SciPy "
               "chi2_contingency), as R pairwise.prop.test(), whose default is the same")
        print(f'Each pair of "{for_each}" groups compared on the percent "{column}" = {_label(event)} with {how}; the '
              f"p-values are adjusted for {len(given)} pair{'' if len(given) == 1 else 's'} with Holm's method "
              "(statsmodels multipletests), so the chance of any false alarm stays at 5 %. Each difference has "
              "Newcombe's 95 % interval (statsmodels confint_proportions_2indep), as compare_risks.")
        null = f'the two groups had the same percent "{_label(event)}"'
        for row in rows:
            diff = row["difference"]
            points = _say_pct(abs(diff)).replace(" %", " percentage points")
            ends = (_say_pct(row["difference 95 % CI low"]).replace(" %", "") + " to "
                    + _say_pct(row["difference 95 % CI high"]).replace(" %", ""))
            where = "higher" if diff > 0 else "lower" if diff < 0 else "the same"
            amount = f"{points} {where}" if diff != 0 else "the same"
            clause = (_p_clause(row["p-value (Holm)"], null, shown="Holm-adjusted " + _p_shown(row["p-value (Holm)"]))
                      if not math.isnan(row["p-value (Holm)"]) else "no p-value: every row in the two groups is the same")
            print(f"  {row['group 1']} vs {row['group 2']}: the percent in {row['group 1']} is {amount} (95 % CI "
                  f"{ends}); {clause}.")
        print("A large p-value for a pair does not show that the two groups have the same percent.")
        if low_expected:
            print('Note: an expected count is below 5 in at least one pair, so the chi-square p-value is rough there; '
                  'test="fisher" gives Fisher\'s exact test for every pair.')
        if any(math.isnan(r["p-value"]) for r in rows):
            print("Note: a pair where every row has the same value has no p-value (as R prop.test(), which gives NaN) "
                  "and is not counted in Holm's adjustment.")
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _pair_letters(self, column, for_each, pairs):
        """compare_each_pair_of(show="letters"): R multcompView::multcompLetters() on the pairs' p-values."""
        rows = pairs._frame.to_pandas().to_dict("records")
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):  # the note on skipped rows was printed already
            groups = self._groups("compare_each_pair_of", column, for_each, "")
        names = [g[0] for g in groups]
        letters, p_name = pair_letters(names, rows)
        medians = "difference in medians" in rows[0]
        word = "median" if medians else "average"
        table = {"group": names, "letters": [letters[n] for n in names],
                 f"{word} of {column}": [float(np.median(v) if medians else v.mean()) for _, v in groups],
                 "count": [len(v) for _, v in groups]}
        shown = _list_words(f"{n} {letters[n]}" for n in names)
        print(f"Letters: {shown}. Groups that share a letter could not be told apart: the {p_name} between them is "
              "0.05 or more. Letters from R multcompView::multcompLetters().")
        return self._new_table(nw.from_dict(table, backend=self._frame.implementation))

    def _each_pair(self, step, column, for_each, based_on, test, against, seed):
        example = 'with sdata.get_example("marks"): table.compare_each_pair_of("marks", for_each_group_in="class")'
        self._check_based_on(step, based_on)
        if isinstance(test, str):
            test = PAIR_ALIASES.get(test.strip().lower(), test.strip().lower())
        if against is not None:
            if test is not None or based_on != "averages":
                raise SimplydataError("against= gives Dunnett's test on averages; leave out test= and based_on=.")
            if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
                raise SimplydataError("with_seed= needs a whole number, such as with_seed=1.")
            groups = self._groups(step, column, for_each, example)
            return self._dunnett(column, for_each, groups, against, int(seed))
        if test in R_PAIR_TESTS:
            wanted = R_PAIR_TESTS[test][1]
            if based_on == "ranks" and wanted == "averages":
                raise SimplydataError(f'test="{test}" compares averages, but based_on="ranks" asks for ranks; for ranks '
                                      'use test="dunn" or test="conover".')
            groups = self._groups(step, column, for_each, example)
            return self._r_pairs(column, for_each, groups, test)
        if test is not None:
            self._check_choice(step, "test", test, PAIR_TESTS)
            if based_on == "ranks" and test != "mann-whitney":
                raise SimplydataError(
                    f'test="{test}" compares averages, but based_on="ranks" asks for ranks. Use one of them: '
                    'test="mann-whitney" is the rank test.'
                )
            if test == "mann-whitney":
                based_on = "ranks"
        groups = self._groups(step, column, for_each, example)
        if test == "tukey":
            return self._tukey_pairs(column, for_each, groups)
        from scipy import stats

        rows, pair_notes = [], set()
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                (n1, a), (n2, b) = groups[i], groups[j]
                row = {"group 1": n1, "group 2": n2}
                if based_on == "averages":
                    if a.std(ddof=1) == 0 and b.std(ddof=1) == 0:
                        raise SimplydataError(
                            f'Every value is the same within "{n1}" and within "{n2}", so a t-test cannot '
                            'measure the spread. Use based_on="ranks", or check the data.'
                        )
                    result = stats.ttest_ind(a, b, equal_var=False)
                    low, high = result.confidence_interval(0.95)
                    row.update({"test": "Welch's t-test", "difference": float(a.mean() - b.mean()),
                                "difference 95 % CI low": float(low), "difference 95 % CI high": float(high),
                                "statistic name": "t", "statistic": float(result.statistic),
                                "degrees of freedom": float(result.df), "p-value": float(result.pvalue)})
                else:
                    u, p, _ = _mann_whitney(a, b)
                    es = effect_size("rank_biserial", a=a, b=b)
                    pair_notes.add(es["note"])
                    row.update({"test": "Mann-Whitney U test",
                                "difference in medians": float(np.median(a) - np.median(b)),
                                "statistic name": "U", "statistic": u, "p-value": p,
                                "rank-biserial correlation": es["value"],
                                "rank-biserial correlation 95 % CI low": es["low"],
                                "rank-biserial correlation 95 % CI high": es["high"]})
                row.update({"count in group 1": len(a), "count in group 2": len(b)})
                rows.append(row)
        adjusted = _holm([r["p-value"] for r in rows])
        for row, p in zip(rows, adjusted):
            row["p-value (Holm)"] = p
        test = "Welch's t-test" if based_on == "averages" else "Mann-Whitney U test"
        pairs = "pair" if len(rows) == 1 else "pairs"
        print(f'Each pair of "{for_each}" groups compared on "{column}" with {test}; the p-values are adjusted for '
              f"{len(rows)} {pairs} with Holm's method, so the chance of any false alarm stays at 5 %.")
        for row in rows:
            if based_on == "averages":
                diff, word = row["difference"], "average"
            else:
                diff, word = row["difference in medians"], "median"
            direction = "higher" if diff > 0 else "lower"
            words = "Holm-adjusted " + _p_shown(row["p-value (Holm)"])
            print(f"  {row['group 1']} vs {row['group 2']}: the {word} of {row['group 1']} is {_num(abs(diff))} "
                  f"{direction}; {words}.")
        for note in sorted(pair_notes - {""}):
            print(note.replace("rank-biserial correlation and its", "the rank-biserial correlation of each pair and its"))
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _pair_lines(self, rows, p_name, adjusted):
        for row in rows:
            if "difference" in row:
                diff, word = row["difference"], "average"
            else:
                diff, word = row["difference in medians"], "median"
            interval = ""
            if "difference 95 % CI low" in row:
                interval = (f" (95 % CI {_num(row['difference 95 % CI low'])} to "
                            f"{_num(row['difference 95 % CI high'])})")
            print(f"  {row['group 1']} vs {row['group 2']}: the {word} of {row['group 1']} is {_num(abs(diff))} "
                  f"{'higher' if diff > 0 else 'lower'}{interval}; {adjusted}{_p_shown(row[p_name])}.")

    def _r_pairs(self, column, for_each, groups, test):
        """compare_each_pair_of(test="games-howell" | "scheffe" | "lsd" | "dunn" | "conover"), run in R."""
        rows = r_pairs(test, groups)
        title, based_on, r_name, meaning = R_PAIR_TESTS[test]
        pairs = "pair" if len(rows) == 1 else "pairs"
        print(f'Each pair of "{for_each}" groups compared on "{column}" with {title}, run in R as {r_name}: '
              f"{len(rows)} {pairs}; {meaning}.")
        p_name = "p-value" if test == "lsd" else "p-value (adjusted)"
        self._pair_lines(rows, p_name, "" if test == "lsd" else
                         ("Holm-adjusted " if test in ("dunn", "conover") else "adjusted "))
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _dunnett(self, column, for_each, groups, against, seed):
        """compare_each_pair_of(against=): Dunnett's test, SciPy stats.dunnett."""
        rows = dunnett_pairs(groups, against, seed)
        others = "group" if len(rows) == 1 else "groups"
        print(f'Each "{for_each}" group compared on "{column}" with the control group "{against}" ({len(rows)} {others}) '
              "with Dunnett's test, as R multcomp::glht(mcp(group = \"Dunnett\")): the p-values and 95 % intervals hold "
              "for all the comparisons at once, so the chance of any false alarm stays at 5 %. SciPy stats.dunnett "
              f"works this out with random numbers (seed {seed}); the last digit can differ from R's.")
        self._pair_lines(rows, "p-value (adjusted)", "adjusted ")
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _tukey_pairs(self, column, for_each, groups):
        """compare_each_pair_of(test="tukey"): Tukey HSD (Tukey-Kramer for unequal sizes), as R TukeyHSD()."""
        from scipy import stats

        names = [g[0] for g in groups]
        arrays = [g[1] for g in groups]
        spreads = [float(v.std(ddof=1)) for v in arrays]
        if all(s == 0 for s in spreads):
            raise SimplydataError(
                "Every value is the same within each group, so Tukey's method cannot measure the spread. "
                'Use based_on="ranks", or check the data.'
            )
        result = stats.tukey_hsd(*arrays)
        interval = result.confidence_interval(0.95)
        rows = []
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                rows.append({"group 1": names[i], "group 2": names[j], "test": "Tukey HSD",
                             "difference": float(result.statistic[i, j]),
                             "difference 95 % CI low": float(interval.low[i, j]),
                             "difference 95 % CI high": float(interval.high[i, j]),
                             "p-value (Tukey)": float(result.pvalue[i, j]),
                             "count in group 1": len(arrays[i]), "count in group 2": len(arrays[j])})
        pairs = "pair" if len(rows) == 1 else "pairs"
        sizes = len({len(v) for v in arrays}) > 1
        kramer = " (the Tukey-Kramer form, as the groups differ in size)" if sizes else ""
        print(f'Each pair of "{for_each}" groups compared on "{column}" with Tukey\'s honest significant difference'
              f"{kramer}, as R TukeyHSD(aov({column} ~ {for_each})): the p-values and 95 % confidence intervals hold "
              f"for all {len(rows)} {pairs} at once, so the chance of any false alarm stays at 5 %. It assumes the "
              "groups have the same spread.")
        for row in rows:
            diff = row["difference"]
            direction = "higher" if diff > 0 else "lower"
            words = "Tukey-adjusted " + _p_shown(row["p-value (Tukey)"])
            print(f"  {row['group 1']} vs {row['group 2']}: the average of {row['group 1']} is {_num(abs(diff))} "
                  f"{direction} (95 % CI {_num(row['difference 95 % CI low'])} to "
                  f"{_num(row['difference 95 % CI high'])}); {words}.")
        smallest = min(spreads)
        ratio = max(spreads) / smallest if smallest > 0 else math.inf
        if ratio > SPREAD_RATIO:
            shown = "many" if math.isinf(ratio) else _num(ratio)
            print(f"Note: the biggest standard deviation is {shown} times the smallest, so the groups may not have "
                  f'the same spread. Check with table.compare_spreads_of("{column}", for_each_group_in="{for_each}"), or leave '
                  "out test= for Welch's t-tests with Holm's correction, which do not assume it.")
        for note in _shape_notes([(f'group "{n}"', v) for n, v in groups]):
            print(note)
        frame = nw.from_dict({key: [r[key] for r in rows] for key in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    # ------------------------------------------------------------------ compare_spreads_of
    @friendly(renamed={"for_each": "for_each_group_in"})
    def compare_spreads_of(self, column=None, for_each_group_in=None, test="levene"):
        """Do the groups really differ in how spread out their values are?

        table.compare_spreads_of("marks", for_each_group_in="class")   (with sdata.get_example("marks"))
        test="levene" (the default): Levene's test centred on each group's median, also
        called the Brown-Forsythe test. It is the default of R car::leveneTest() and SciPy
        levene(center="median"), and copes well with values that are not bell-shaped.
        test="bartlett": Bartlett's test (R bartlett.test()), a little stronger when the
        values are bell-shaped but easily fooled when they are not. test="fligner": the
        Fligner-Killeen test (R fligner.test()), based on ranks, the safest with outliers.
        For 2 groups also: test="ansari" (Ansari-Bradley, R ansari.test(), SciPy ansari),
        test="mood" (Mood's test of scale, R mood.test(), SciPy mood) and test="f" (the F test
        of the ratio of two variances, R var.test(), run in R through simplydata[r]; it assumes
        bell-shaped values).
        Empty cells are skipped. Prints the standard deviation of each group and the answer
        in words; gives back a one-row table of results. compare_averages_of() uses Welch's
        test by default, which does not need equal spreads.
        """
        step = "compare_spreads_of"
        example = 'with sdata.get_example("marks"): table.compare_spreads_of("marks", for_each_group_in="class")'
        chosen = _plain_name(test)
        chosen = SPREAD_ALIASES.get(chosen, chosen)
        if chosen not in SPREAD_TESTS:
            raise choice_error(step, "test", test, list(SPREAD_TESTS))
        groups = self._groups(step, column, for_each_group_in, example)
        names = [g[0] for g in groups]
        arrays = [g[1] for g in groups]
        if chosen in TWO_GROUP_SPREAD_TESTS and len(arrays) != 2:
            raise SimplydataError(f'test="{chosen}" compares exactly 2 groups, but "{for_each_group_in}" has {len(arrays)}. '
                                  'Use test="levene" (the default) for all groups at once.')
        spreads = [float(v.std(ddof=1)) for v in arrays]
        if all(s == 0 for s in spreads):
            raise SimplydataError(f'Every value is the same within each group of "{for_each_group_in}", so there is no '
                                  "spread to compare. Check the data.")
        from scipy import stats

        what = f'the spread of "{column}" in each "{for_each_group_in}" ({", ".join(names)})'
        row = {"test": None, "what it compares": what}
        if chosen == "levene":
            result = stats.levene(*arrays, center="median")
            stat, p = float(result.statistic), float(result.pvalue)
            if not math.isfinite(stat):
                raise SimplydataError(f'Every value lies the same distance from its group\'s median in "{column}", '
                                      'so Levene\'s test cannot work here. Try test="fligner".')
            df1, df2 = float(len(arrays) - 1), float(sum(len(v) for v in arrays) - len(arrays))
            name = "Levene's test (Brown-Forsythe, centred on the medians)"
            row.update({"test": name, "statistic name": "F", "statistic": stat, "degrees of freedom 1": df1,
                        "degrees of freedom 2": df2, "p-value": p})
            second = (f"Test: Levene's test centred on the medians, the Brown-Forsythe form (F = {_num(stat)}, "
                      f"df = {_whole(df1)} and {_whole(df2)}), as R car::leveneTest() "
                      'and SciPy levene(center="median"); it copes well with values that are not bell-shaped.')
        elif chosen == "bartlett":
            flat = [n for n, s in zip(names, spreads) if s == 0]
            if flat:
                raise SimplydataError(
                    f"Every value is the same within {_list_words(repr(n) for n in flat)}, which Bartlett's test "
                    'cannot handle. Use test="levene" (the default) or test="fligner".'
                )
            result = stats.bartlett(*arrays)
            stat, p = float(result.statistic), float(result.pvalue)
            df = float(len(arrays) - 1)
            name = "Bartlett's test"
            row.update({"test": name, "statistic name": "Bartlett's K-squared", "statistic": stat,
                        "degrees of freedom": df, "p-value": p})
            second = (f"Test: {name} (K-squared = {_num(stat)}, df = {_whole(df)}), as R bartlett.test(); "
                      "it assumes bell-shaped values.")
        elif chosen == "ansari":
            result = stats.ansari(*arrays)
            stat, p = float(result.statistic), float(result.pvalue)
            name = "Ansari-Bradley test"
            row.update({"test": name, "statistic name": "AB", "statistic": stat, "p-value": p})
            second = (f"Test: {name} (AB = {_whole(stat)}), as R ansari.test(); it uses ranks, so it does not need "
                      "bell-shaped values, but it assumes the groups have the same middle.")
        elif chosen == "mood":
            result = stats.mood(*arrays)
            stat, p = float(result.statistic), float(result.pvalue)
            name = "Mood's test of scale"
            row.update({"test": name, "statistic name": "z", "statistic": stat, "p-value": p})
            second = (f"Test: {name} (z = {_num(stat)}), as R mood.test(); it uses ranks, so it does not need "
                      "bell-shaped values, but it assumes the groups have the same middle.")
        elif chosen == "f":
            from .._r import r_call

            found = r_call("t <- stats::var.test(a, b); list(f = t$statistic, df = t$parameter, p = t$p.value, "
                           "ci = t$conf.int)", what="The F test of two variances (R var.test())",
                           python_note="SciPy has no F test of two variances; Levene's test (the default) needs no R",
                           a=arrays[0], b=arrays[1])
            stat, p = float(found["f"][0]), float(found["p"][0])
            df1, df2 = (float(v) for v in found["df"])
            low, high = (float(v) for v in found["ci"])
            name = "F test of two variances"
            row.update({"test": name, "statistic name": "F", "statistic": stat, "degrees of freedom 1": df1,
                        "degrees of freedom 2": df2, "p-value": p, "ratio of variances": stat,
                        "ratio 95 % CI low": low, "ratio 95 % CI high": high})
            second = (f"Test: {name} (F = {_num(stat)}, df = {_whole(df1)} and {_whole(df2)}; 95 % CI of the ratio of "
                      f"the variances {_num(low)} to {_num(high)}), as R var.test(), run in R; it assumes bell-shaped "
                      "values and is easily fooled when they are not.")
        else:
            result = stats.fligner(*arrays, center="median")
            stat, p = float(result.statistic), float(result.pvalue)
            df = float(len(arrays) - 1)
            name = "Fligner-Killeen test"
            row.update({"test": name, "statistic name": "chi-square", "statistic": stat, "degrees of freedom": df,
                        "p-value": p})
            second = (f"Test: {name} (chi-square = {_num(stat)}, df = {_whole(df)}), as R fligner.test(); it uses "
                      "ranks, so it does not need bell-shaped values and copes with outliers.")
        for n, v, s in zip(names, arrays, spreads):
            row[f"count in {n}"] = len(v)
            row[f"standard deviation in {n}"] = s
        listed = _list_words(f"{_num(s)} in {n}" for n, s in zip(names, spreads))
        print(f'The standard deviation of "{column}" is {listed}.')
        print(_p_sentence(p, "the groups truly had the same spread", "differences in spread this big or bigger",
                          "that the groups have the same spread"))
        print(second)
        if chosen == "bartlett":
            for n, v in groups:
                if 3 <= len(v) <= SHAPIRO_LIMIT and np.ptp(v) > 0:
                    sw = float(stats.shapiro(v).pvalue)
                    if sw < 0.05:
                        print(f'Note: the values in group "{n}" don\'t look bell-shaped (Shapiro-Wilk {_p_shown(sw)}); '
                              "Bartlett's test is easily fooled by that, whatever the group size. A safer choice: "
                              'test="levene" (the default).')
        if p < 0.05:
            print("Note: compare_averages_of() uses Welch's test by default, which does not need equal spreads; "
                  'test="student", test="anova" and compare_each_pair_of(test="tukey") do need them.')
        return self._result_table(row)

    # ------------------------------------------------------------------ same_within= (equivalence)
    def _same_within(self, step, kind, data, same_within, up, first, second, method, r_call, extra=None,
                     claim=None):
        """Equivalence (TOST) or, with not_lower= / not_higher=, non-inferiority. first and second name the two
        sides of the difference (first minus second); up is the side the test looks toward (or None).
        claim: None (not_lower=up: up is not lower than the other side by more than the margin) or
        "not_higher" (the other side is not higher than up by more than the margin; the same test)."""
        from .equivalence import margin, non_inferior, say, tost

        low, high = margin(step, same_within)
        row = {"what it compares": f"{first} minus {second}, against the margin {low:g} to {high:g}"}
        if up is None:
            result = tost(kind, data, low, high)
            lines, verdict = say(result, low, high, "", f"{first} and {second}", method,
                                 f"the difference were truly outside {low:g} to {high:g}")
            lines[-1] += f" As R {r_call}."
            row.update({"test": f"two one-sided tests (TOST, {method})", "difference": result["difference"],
                        "difference 90 % CI low": result["ci90"][0], "difference 90 % CI high": result["ci90"][1],
                        "p-value against the low margin": result["p_low"],
                        "p-value against the high margin": result["p_high"], "p-value": result["p"],
                        "margin low": low, "margin high": high, "answer": verdict})
        else:
            looks_up = up == first
            edge = low if looks_up else high
            other = second if looks_up else first
            worse = "lower"  # not_lower="B": B is not lower than the other side by more than the margin
            if claim == "not_higher":  # not_higher="A": A is not higher than B by more than the margin
                up, other, worse = other, up, "higher"
            amount = f"{abs(edge):g}"
            result = non_inferior(kind, data, edge, "higher" if looks_up else "lower")
            ci_low, ci_high = result["ci"]
            if looks_up:
                ends, clear = f"at least {_num(ci_low)}", ci_low > edge
            else:
                ends, clear = f"at most {_num(ci_high)}", ci_high < edge
            if result["p"] < 0.05:
                verdict = "not worse than the margin"
                answer = f"so {up} is not {worse} than {other} by more than {amount}"
            else:
                verdict = "the data cannot tell"
                answer = (f"so the data cannot show that {up} is not {worse} than {other} by more than {amount}; "
                          "more data would narrow the interval")
            where = "lies above" if looks_up else "lies below"
            lines = [f"The difference ({first} minus {second}) is {_num(result['difference'])}; the one-sided 95 % "
                     f"interval, {ends}, {where if clear else 'does not lie ' + where.split()[1]} {edge:g}, "
                     f"{answer}.",
                     _p_sentence(result["p"], f"{up} were truly {worse} than {other} by {amount} or more",
                                 "a difference this far from that", f"that {up} is {worse} by more than {amount}"),
                     f"Method: one one-sided test against the margin (non-inferiority, {method}), as R "
                     f'TOSTER::t_TOST(hypothesis = "MET"); one-sided, as you asked before seeing the data.']
            row.update({"test": f"non-inferiority test ({method})", "difference": result["difference"],
                        "difference one-sided 95 % CI low": ci_low, "difference one-sided 95 % CI high": ci_high,
                        "p-value": result["p"], "margin": edge, "answer": verdict,
                        "sides": f"one-sided: {up} not {worse} by more than {amount}"})
        row.update(extra or {})
        for line in lines:
            print(line)
        return self._result_table(row)

    # ------------------------------------------------------------------ paired and one-sample
    def _one_sample(self, step, values, label, against, based_on, what, notes_label, alternative="two-sided"):
        """Shared by compare_before_and_after (changes against 0) and compare_average_to."""
        from scipy import stats

        row = {"test": None, "what it compares": what}
        if based_on == "averages":
            if values.std(ddof=1) == 0:
                raise SimplydataError(
                    f"Every {label} is the same ({_num(values[0])}), so there is no spread to test with. "
                    "Check the data."
                )
            result = stats.ttest_1samp(values, against, alternative=alternative)
            low, high = result.confidence_interval(0.95)
            t, p, df = float(result.statistic), float(result.pvalue), float(result.df)
            es = effect_size("cohens_d_one", x=values, mu=float(against))
            return row, dict(t=t, p=p, df=df, low=float(low), high=float(high), d=es["value"], d_low=es["low"],
                             d_high=es["high"], d_text=interval_text(es["low"], es["high"]), have_d=not es["note"],
                             notes=([es["note"]] if es["note"] else [])
                             + _shape_notes([(None, values)], what=notes_label))
        found = _signed_rank(values - against, alternative)
        if found is None:
            raise SimplydataError(f"Every {label} is exactly {_num(against)}, so there is nothing to test.")
        v, p, how, zeros, lean = found
        es = effect_size("rank_biserial_one", x=values, mu=float(against))
        return row, dict(v=v, p=p, r=es["value"], r_low=es["low"], r_high=es["high"],
                         r_text=interval_text(es["low"], es["high"]), have_r=not es["note"], lean=lean, how=how,
                         zeros=zeros, notes=[es["note"]] if es["note"] else [])

    def _paired_kind(self, before, after):
        """"numbers", "yes/no" (both columns hold the same 2 values, or 0 and 1) or "categories"."""
        schema = self._frame.schema
        numeric = schema[before].is_numeric() and schema[after].is_numeric()
        kept = self._frame.select(before, after)
        floats = [c for c in (before, after) if schema[c].is_float()]
        if floats:
            kept = kept.with_columns(nw.col(c).fill_nan(None) for c in floats)
        kept = kept.drop_nulls()
        values = set(kept[before].to_list()) | set(kept[after].to_list())
        if numeric:
            return ("yes/no" if values and values <= {0, 1} and len(values) == 2 else "numbers"), kept
        return ("yes/no" if len(values) <= 2 else "categories"), kept

    def _paired_counts(self, step, before, after, kind, kept, p_value_by, side_given):
        """compare_before_and_after on yes/no columns (McNemar) or categories (Bowker), as R mcnemar.test()."""
        from statsmodels.stats.contingency_tables import SquareTable, mcnemar

        from .models import YES_NO_PAIRS, _sort_key

        if side_given:
            raise SimplydataError(f"{step}() on {kind} columns looks for a change either way; leave out sides= and "
                                  "higher=/lower=.")
        _skipped_note(len(self._frame) - len(kept), [before, after])
        b_values, a_values = kept[before].to_list(), kept[after].to_list()
        n = len(b_values)
        if n < 2:
            raise SimplydataError(f'{step}() needs at least 2 rows with a value in both "{before}" and "{after}".')
        levels = sorted(set(b_values) | set(a_values), key=_sort_key)
        if kind == "yes/no":
            if len(levels) < 2:
                raise SimplydataError(f'{step}() needs both values of a yes/no column; "{before}" and "{after}" only '
                                      f'hold "{_label(levels[0])}".')
            lowered = {str(v).strip().lower(): v for v in levels}
            yes = next((lowered[w] for w, o in YES_NO_PAIRS if set(lowered) == {w, o}), levels[1])
            levels = [yes] + [v for v in levels if v != yes]
        index = {v: i for i, v in enumerate(levels)}
        tab = np.zeros((len(levels), len(levels)), dtype=np.int64)
        for b_, a_ in zip(b_values, a_values):
            tab[index[b_], index[a_]] += 1
        if kind == "yes/no":
            return self._mcnemar(step, before, after, tab, _label(levels[0]), n, p_value_by == "exact", mcnemar)
        if p_value_by == "exact":
            raise SimplydataError('p_value_by="exact" works for yes/no columns (McNemar); for 3 or more categories '
                                  "leave it out (Bowker's test).")
        empty = [(levels[i], levels[j]) for i in range(len(levels)) for j in range(i + 1, len(levels))
                 if tab[i, j] + tab[j, i] == 0]
        if empty:
            pairs = _list_words(f'"{_label(a)}" and "{_label(b)}"' for a, b in empty)
            raise SimplydataError(f"No row changed between {pairs} (either way), so Bowker's test has nothing to "
                                  "compare there and R mcnemar.test() gives no answer. Merge categories that "
                                  "rarely change into their neighbours first.")
        result = SquareTable(tab, shift_zeros=False).symmetry()
        stat, p, df = float(result.statistic), float(result.pvalue), int(result.df)
        changed = int(tab.sum() - np.trace(tab))
        row = {"test": "Bowker's test of symmetry", "what it compares": f'"{before}" and "{after}", row by row',
               "statistic name": "chi-square", "statistic": stat, "degrees of freedom": float(df), "p-value": p,
               "rows": n, "rows that changed": changed}
        for v in levels:
            row[f"{_say_label(v)} in {before}"] = int(tab[index[v]].sum())
            row[f"{_say_label(v)} in {after}"] = int(tab[:, index[v]].sum())
        counts = _list_words(f'"{_label(v)}" {int(tab[index[v]].sum())} then {int(tab[:, index[v]].sum())}'
                             for v in levels)
        print(f'Counts in "{before}" then "{after}": {counts}. {changed} of {n} rows changed category.')
        print(_p_sentence(p, "the changes truly went both ways equally", "changes this lopsided or more",
                          "that the changes are balanced"))
        print(f"Test: Bowker's test of symmetry (chi-square = {_num(stat)}, df = {df}), because the columns hold "
              f"{len(levels)} categories; as R mcnemar.test() on the {len(levels)} x {len(levels)} table.")
        return self._result_table(row)

    def _mcnemar(self, step, before, after, tab, yes_label, n, exact, mcnemar):
        """McNemar's test (statsmodels mcnemar with R's defaults) and the difference in percents (R exact2x2)."""
        from .._r import RMissing, r_call

        result = mcnemar(tab, exact=exact, correction=True)
        p, stat = float(result.pvalue), float(result.statistic)
        down, up = int(tab[0, 1]), int(tab[1, 0])  # yes -> no, no -> yes
        yes_before, yes_after = int(tab[0].sum()), int(tab[:, 0].sum())
        row = {"test": "McNemar's test" + (" (exact binomial)" if exact else " with continuity correction"),
               "what it compares": f'"{yes_label}" in "{before}" and in "{after}", row by row',
               "statistic name": "the smaller count of changes" if exact else "chi-square", "statistic": stat,
               "p-value": p, "rows": n, f"{yes_label} in {before}": yes_before, f"{yes_label} in {after}": yes_after,
               "changed from yes to no": down, "changed from no to yes": up}
        try:
            found = r_call("r <- exact2x2::mcnemarExactDP(x = x, m = m, n = n); list(d = unname(r$estimate[3]), "
                           "ci = unname(r$conf.int))", packages=("exact2x2",),
                           what="the difference in percents with its 95 % interval (R exact2x2::mcnemarExactDP())",
                           x=up, m=up + down, n=n)
            d = float(np.asarray(found["d"])[0])
            low, high = (float(v) for v in np.asarray(found["ci"]))
            note = ""
        except RMissing:
            d = low = high = math.nan
            note = ("Note: the difference in percents and its 95 % CI come from the R package exact2x2 "
                    '(mcnemarExactDP), which is not ready here; to add them: pip install "simplydata[r]", install R, '
                    'then in R install.packages("exact2x2").')
        row.update({"effect size name": "difference in percent yes, after minus before", "effect size": d * 100,
                    "effect size 95 % CI low": low * 100, "effect size 95 % CI high": high * 100})
        first = (f'"{yes_label}": {yes_before} of {n} in "{before}" and {yes_after} of {n} in "{after}". {down} rows '
                 f'changed from "{yes_label}" to the other value, and {up} the other way.')
        if not note:
            first += (f" The percent changed by {d * 100:+.1f} percentage points (95 % CI {low * 100:.1f} to "
                      f"{high * 100:.1f}).")
        print(first)
        print(_p_sentence(p, "there were truly no change", "a split of the changes this uneven or more",
                          "that there is no change"))
        how = ('the exact binomial test on the rows that changed (p_value_by="exact"), as R '
               "exact2x2::exact2x2(paired = TRUE)" if exact else
               f"with continuity correction (chi-square = {_num(stat)}, df = 1), as R mcnemar.test()")
        print(f"Test: McNemar's test, {how}, because both columns are yes/no; it uses only the rows that changed."
              + ("" if note else " The interval of the difference is R exact2x2::mcnemarExactDP()."))
        if note:
            print(note)
        return self._result_table(row)

    def _sign_test(self, step, before, after, sides, higher, lower, alternative):
        """compare_before_and_after(test="sign"): statsmodels sign_test, as R DescTools::SignTest()."""
        from statsmodels.stats.descriptivestats import sign_test

        if sides != 2 or higher is not None or lower is not None or alternative not in (None, "two-sided"):
            raise SimplydataError('test="sign" looks for a change either way here; leave out sides= and higher=.')
        b, a = self._number_values(step, [before, after])
        changes = a - b
        ups, downs = int((changes > 0).sum()), int((changes < 0).sum())
        if ups + downs == 0:
            raise SimplydataError(f'Every row has the same value in "{before}" and "{after}", so there is no change '
                                  "to test.")
        m, p = sign_test(changes, 0)
        p = float(p)
        zeros = len(changes) - ups - downs
        row = {"test": "sign test", "what it compares": f'the change from "{before}" to "{after}" in each row',
               "statistic name": "rows that went up", "statistic": float(ups), "p-value": p, "rows that went up": ups,
               "rows that went down": downs, "rows with no change": zeros, "median change": float(np.median(changes)),
               "rows": len(changes)}
        print(f'"{after}" is higher than "{before}" in {ups} rows and lower in {downs}'
              + (f" ({zeros} with no change, left out)" if zeros else "")
              + f"; the median change is {_num(np.median(changes))}.")
        print(_p_sentence(p, "ups and downs were truly equally likely", "a split this uneven or more",
                          "that there is no change"))
        print("Test: sign test, chosen with test=; it counts only whether each row went up or down, so it needs no "
              "bell shape and ignores how big the changes are. As R DescTools::SignTest() and statsmodels "
              "sign_test().")
        return self._result_table(row)

    @friendly(renamed={"seed": "with_seed"}, others={"rscale": "prior_width", "prior_scale": "prior_width"})
    def compare_before_and_after(self, before=None, after=None, based_on="averages", sides=2, higher=None, lower=None,
                                 alternative=None, test=None, p_value_by="formula", shuffles=9999, with_seed=1,
                                 same_within=None, not_lower=None, not_higher=None, bayesian=False,
                                 prior_width="medium"):
        """Did the values really change from one column to the other, row by row?

        table.compare_before_and_after("Maths", "Science")   (with sdata.get_example("marks"))
        For two measurements of the same thing, such as each child's mark before and after
        a course. Uses the change in each row (after minus before): a paired t-test, or the
        Wilcoxon signed-rank test with based_on="ranks". Rows with an empty cell in either
        column are skipped. Effect size: Cohen's d_z, the average change in standard
        deviations of the changes. Gives back a one-row table of results.
        sides=1, higher="after" (or "before"; lower= is the mirror: lower="before" is the same as
        higher="after") tests in one direction only, as decided before seeing the data (R
        t.test(after, before, paired = TRUE, alternative = "greater")).
        test="sign": the sign test, which only counts ups and downs (statsmodels sign_test, as R
        DescTools::SignTest()).
        The kind of column decides the test, and the sentence says so:
        yes/no columns (two values, such as "yes"/"no", True/False or 0/1): McNemar's test with
        continuity correction (statsmodels mcnemar, as R mcnemar.test()), with the change in the
        percent and its 95 % interval from R exact2x2::mcnemarExactDP(); p_value_by="exact" gives
        the exact binomial test on the rows that changed (as R exact2x2::exact2x2(paired = TRUE)).
        columns of 3 or more categories (such as mild / moderate / severe): Bowker's test of
        symmetry (statsmodels SquareTable.symmetry(), as R mcnemar.test() on the k x k table).
        p_value_by="shuffling" (numbers, averages): the p-value comes from swapping the two values
        within rows at random shuffles=9999 times (with_seed=1), which flips the sign of each change,
        and counting how often the average change is as big as the one in the data (SciPy
        permutation_test). With few rows every arrangement is counted, and the p-value is exact.
        same_within=5 (numbers) asks whether the average change is within -5 to 5 (or [-3, 5]):
        two one-sided tests on the changes (statsmodels ttost_paired, as R TOSTER::t_TOST(paired =
        TRUE)); same_within=5, not_lower="after" is a non-inferiority test (the after values no more
        than 5 lower), and not_higher="after" its mirror (no more than 5 higher).
        bayesian=True (numbers) gives the Bayes factor and a 95 % credible interval of the average change
        instead of a p-value: R BayesFactor::ttestBF(after, before, paired = TRUE) with the JZS prior,
        prior_width= "medium" (0.707, the default), "wide", "ultrawide" or a number; 10,000 posterior draws
        (with_seed=1). Needs R (BayesFactor).
        """
        step = "compare_before_and_after"
        example = 'table.compare_before_and_after("before", "after")'
        self._need_name(step, "before", before, example)
        self._need_name(step, "after", after, example)
        self._check_based_on(step, based_on)
        if before == after:
            raise SimplydataError(f"{step}() needs two different columns, for example {example}.")
        if bayesian is not False or prior_width != "medium":
            from . import bayes_r, bayes_words

            self._check_bayesian(step, bayesian, prior_width)
            bayes_words.check_bayes_options(step, [
                ("based_on=", based_on, "averages"), ("sides=", sides, 2), ("higher=", higher, None),
                ("lower=", lower, None), ("alternative=", alternative, None), ("test=", test, None),
                ("p_value_by=", p_value_by, "formula"), ("shuffles=", shuffles, 9999),
                ("same_within=", same_within, None), ("not_lower=", not_lower, None),
                ("not_higher=", not_higher, None)])
            seed = bayes_words.check_seed(with_seed)
            width = bayes_r.width_value(prior_width)
            self._need_columns(before, after)
            if self._paired_kind(before, after)[0] != "numbers":
                raise SimplydataError(f'bayesian=True compares two columns of numbers; "{before}" and "{after}" are '
                                      "not both numbers.")
            b, a = self._number_values(step, [before, after])
            if len(a) < 2:
                raise SimplydataError(f'{step}() needs at least 2 rows with a number in both "{before}" and "{after}".')
            return bayes_words.matched(self, before, after, b, a, width, seed)
        sides, higher, lower, claim = _non_inferiority(
            step, same_within, sides, higher, lower, not_lower, not_higher, ["after", "before"],
            f'table.compare_before_and_after("{before}", "{after}", same_within=5, not_lower="after")')
        self._need_columns(before, after)
        self._check_choice(step, "p_value_by", p_value_by, ("formula", "exact", "shuffling"))
        kind, kept = self._paired_kind(before, after)
        if p_value_by == "shuffling" and (kind != "numbers" or based_on != "averages" or test is not None):
            raise SimplydataError('p_value_by="shuffling" works for the average change between two columns of '
                                  "numbers (the paired t-test); leave it out here.")
        if kind != "numbers":
            if test is not None:
                raise SimplydataError(f'test="{test}" is for columns of numbers; "{before}" and "{after}" are {kind} '
                                      "columns, so they choose the test (leave out test=).")
            side_given = sides != 2 or higher is not None or lower is not None or alternative not in (None, "two-sided")
            return self._paired_counts(step, before, after, kind, kept, p_value_by, side_given)
        if p_value_by == "exact":
            raise SimplydataError('p_value_by="exact" is for yes/no columns (McNemar\'s exact test). For numbers, the '
                                  'Wilcoxon test (based_on="ranks") is already exact for small groups.')
        if test is not None:
            self._check_choice(step, "test", test, ("sign",))
            return self._sign_test(step, before, after, sides, higher, lower, alternative)
        b, a = self._number_values(step, [before, after])
        if len(a) < 2:
            raise SimplydataError(f'{step}() needs at least 2 rows with a number in both "{before}" and "{after}".')
        changes = a - b
        what = f'the change from "{before}" to "{after}" in each row'
        side_example = f'table.compare_before_and_after("{before}", "{after}", sides=1, higher="after")'
        alt, up = _direction(step, sides, higher, lower, alternative, {"after": "greater", "before": "less"},
                             side_example)
        if same_within is not None:
            if based_on != "averages" or p_value_by != "formula":
                raise SimplydataError("same_within= works on the average change; leave out based_on= and p_value_by=.")
            names = {"after": f'"{after}"', "before": f'"{before}"'}
            return self._same_within(step, "paired", (a, b), same_within, None if up is None else names[up],
                                     names["after"], names["before"], "paired", "TOSTER::t_TOST(paired = TRUE)",
                                     {"rows": len(changes)}, claim)
        row, r = self._one_sample(step, changes, "change", 0.0, based_on, what, "the changes", alt)
        mean_change = float(changes.mean())
        if based_on == "averages":
            direction = "higher" if mean_change > 0 else "lower"
            row.update({"test": "paired t-test", "statistic name": "t", "statistic": r["t"],
                        "degrees of freedom": r["df"], "p-value": r["p"],
                        "effect size name": "average change in standard deviations of the changes (Cohen's d_z)",
                        "effect size": r["d"], "effect size 95 % CI low": r["d_low"],
                        "effect size 95 % CI high": r["d_high"], "average change": mean_change,
                        "average change 95 % CI low": r["low"], "average change 95 % CI high": r["high"]})
            first = (f'On average "{after}" is {_num(abs(mean_change))} {direction} than "{before}" '
                     f"({'' if up is None else 'one-sided '}95 % CI of the average change "
                     f"{_interval_words(r['low'], r['high'])}"
                     + (f"; Cohen's d_z = {_num(r['d'])}{r['d_text']}" if r["have_d"] else "")
                     + ").")
            second = (f"Test: paired t-test (t = {_num(r['t'])}, df = {_whole(r['df'])}), the usual test when each row "
                      "is measured twice; it looks at the change in each row.")
            if p_value_by == "shuffling":
                from .resampling import average, resample_p

                found = resample_p((changes,), average, "paired", alt, shuffles, with_seed)
                r["p"] = found["p"]
                row.update({"p-value": found["p"], "p-value by": found["method"]})
                second += (f" The p-value comes from shuffling, not from the t distribution: {found['words']} "
                           "(SciPy permutation_test).")
        else:
            median_change = float(np.median(changes))
            row.update({"test": "Wilcoxon signed-rank test", "statistic name": "V", "statistic": r["v"],
                        "p-value": r["p"],
                        "effect size name": "how far the changes lean up rather than down, -1 to 1 "
                                            "(matched-pairs rank-biserial correlation)",
                        "effect size": r["r"], "effect size 95 % CI low": r["r_low"],
                        "effect size 95 % CI high": r["r_high"], "median change": median_change})
            size = f" (rank-biserial correlation = {_num(r['r'])}{r['r_text']})" if r["have_r"] else ""
            first = (f'The median change from "{before}" to "{after}" is {_num(median_change)}; the changes lean '
                     f"{r['lean']}{size}.")
            second = (f"Test: Wilcoxon signed-rank test (V = {_whole(r['v'])}, {r['how']}), which uses the ranks of "
                      "the changes, so it does not need bell-shaped values.")
            if r["zeros"]:
                second += f" {r['zeros']} rows with no change were left out, as R does."
        row.update({"rows": len(changes), f"average of {before}": float(b.mean()), f"average of {after}": float(a.mean())})
        if_none = "there were truly no change"
        if up is not None:
            row["sides"] = f'one-sided: "{after if up == "after" else before}" higher'
            names = {"after": f'"{after}"', "before": f'"{before}"'}
            other = "before" if up == "after" else "after"
            second += " " + _one_sided_sentence(f"{names[up]} higher than {names[other]}", f"a change the other way")
            if_none = f"{names[up]} were truly not higher than {names[other]}"
        print(first)
        print(_p_sentence(r["p"], if_none, "a change this big or bigger", "that there is no change"))
        print(second)
        for note in r["notes"]:
            print(note)
        return self._result_table(row)

    @friendly(renamed={"seed": "with_seed"}, others={"rscale": "prior_width", "prior_scale": "prior_width"})
    def compare_average_to(self, column=None, value=None, based_on="averages", sides=2, higher=None, lower=None,
                           alternative=None, same_within=None, not_lower=None, not_higher=None, test=None,
                           standard_deviation=None, bayesian=False, prior_width="medium", with_seed=1):
        """Is the average of a column really different from a number you choose?

        table.compare_average_to("marks", 60)   (with sdata.get_example("marks"))
        A one-sample t-test, or the Wilcoxon signed-rank test (on the median) with
        based_on="ranks". Empty cells are skipped. Effect size: Cohen's d, the difference
        in standard deviations. Gives back a one-row table of results.
        test="z" with standard_deviation=10: the z-test, for when the spread of the values is
        known beforehand (not worked out from these values), run in R (BSDA::z.test()).
        sides=1, higher="average" (the average is above the number) or lower="average" (below it)
        tests in one direction only, as decided before seeing the data (R t.test(x, mu = 60,
        alternative = "greater")).
        same_within=5 asks whether the average is within 5 of the number: two one-sided tests
        (statsmodels DescrStatsW.ttost_mean, as R TOSTER::t_TOST(x - 60, eqb = 5));
        same_within=5, not_lower="average" is a non-inferiority test (the average no more than 5
        below the number), and not_higher="average" its mirror (no more than 5 above it).
        bayesian=True gives the Bayes factor and a 95 % credible interval of the average minus the number
        instead of a p-value: R BayesFactor::ttestBF() with the JZS prior, prior_width= "medium" (0.707,
        the default), "wide", "ultrawide" or a number; 10,000 posterior draws (with_seed=1). Needs R
        (BayesFactor).
        """
        step = "compare_average_to"
        example = 'with sdata.get_example("marks"): table.compare_average_to("marks", 60)'
        self._need_name(step, "the column", column, example)
        if not _is_number(value) or not math.isfinite(value):
            raise SimplydataError(f"{step}() needs a number to compare with, for example {example}.")
        self._check_based_on(step, based_on)
        if bayesian is not False or prior_width != "medium":
            from . import bayes_r, bayes_words

            self._check_bayesian(step, bayesian, prior_width)
            bayes_words.check_bayes_options(step, [
                ("based_on=", based_on, "averages"), ("sides=", sides, 2), ("higher=", higher, None),
                ("lower=", lower, None), ("alternative=", alternative, None), ("same_within=", same_within, None),
                ("not_lower=", not_lower, None), ("not_higher=", not_higher, None), ("test=", test, None),
                ("standard_deviation=", standard_deviation, None)])
            seed = bayes_words.check_seed(with_seed)
            width = bayes_r.width_value(prior_width)
            (values,) = self._number_values(step, [column])
            if len(values) < 2:
                raise SimplydataError(f'{step}() needs at least 2 numbers in "{column}".')
            return bayes_words.one_column(self, column, float(value), values, width, seed)
        if not isinstance(with_seed, (int, np.integer)) or isinstance(with_seed, bool) or with_seed != 1:
            raise SimplydataError("with_seed= fixes the random draws of bayesian=True; the usual test has none, so "
                                  "leave it out.")
        (values,) = self._number_values(step, [column])
        if len(values) < 2:
            raise SimplydataError(f'{step}() needs at least 2 numbers in "{column}".')
        shown = f"{value:g}"
        what = f'the average of "{column}" against {shown}'
        sides, higher, lower, claim = _non_inferiority(
            step, same_within, sides, higher, lower, not_lower, not_higher, ["average"],
            f'table.compare_average_to("{column}", {shown}, same_within=5, not_lower="average")')
        side_example = f'table.compare_average_to("{column}", {shown}, sides=1, higher="average")'
        alt, up = _direction(step, sides, higher, lower, alternative, {"average": "greater", "_value": "less"},
                             side_example)
        if same_within is not None:
            if based_on != "averages":
                raise SimplydataError("same_within= works on the average; leave out based_on=.")
            words = {"average": f'the average of "{column}"', "_value": shown}
            return self._same_within(step, "one sample", (values - float(value),), same_within,
                                     None if up is None else words[up], words["average"], shown, "one-sample t",
                                     "TOSTER::t_TOST(x - value, eqb = ...)", {"average": float(values.mean()),
                                                                  "count": len(values)}, claim)
        if test is not None or standard_deviation is not None:
            if test is None:
                raise SimplydataError(f'standard_deviation= is the known spread for the z-test, so it goes with '
                                      f'test="z": table.compare_average_to("{column}", {shown}, test="z", '
                                      f"standard_deviation={standard_deviation!r}).")
            self._check_choice(step, "test", test, ("z",))
            return self._z_test(step, column, values, float(value), standard_deviation, based_on, alt, up, shown)
        row, r = self._one_sample(step, values, f'value of "{column}"', float(value), based_on, what,
                                  f'the values of "{column}"', alt)
        mean = float(values.mean())
        if based_on == "averages":
            diff = mean - value
            direction = "higher" if diff > 0 else "lower"
            row.update({"test": "one-sample t-test", "statistic name": "t", "statistic": r["t"],
                        "degrees of freedom": r["df"], "p-value": r["p"],
                        "effect size name": "difference in standard deviations (Cohen's d)",
                        "effect size": r["d"], "effect size 95 % CI low": r["d_low"],
                        "effect size 95 % CI high": r["d_high"], "average": mean,
                        "average 95 % CI low": r["low"], "average 95 % CI high": r["high"]})
            first = (f'The average "{column}" is {_num(mean)}, which is {_num(abs(diff))} {direction} than '
                     f"{shown} ({'' if up is None else 'one-sided '}95 % CI of the average "
                     f"{_interval_words(r['low'], r['high'])}"
                     + (f"; Cohen's d = {_num(r['d'])}{r['d_text']}" if r["have_d"] else "")
                     + ").")
            second = (f"Test: one-sample t-test (t = {_num(r['t'])}, df = {_whole(r['df'])}), the usual test for "
                      "one average against a fixed number.")
        else:
            median = float(np.median(values))
            row.update({"test": "Wilcoxon signed-rank test", "statistic name": "V", "statistic": r["v"],
                        "p-value": r["p"],
                        "effect size name": "how far the values lean above rather than below the number, -1 to 1 "
                                            "(rank-biserial correlation)",
                        "effect size": r["r"], "effect size 95 % CI low": r["r_low"],
                        "effect size 95 % CI high": r["r_high"], "median": median, "average": mean})
            size = f" (rank-biserial correlation = {_num(r['r'])}{r['r_text']})" if r["have_r"] else ""
            first = f'The median "{column}" is {_num(median)}, against {shown}{size}.'
            second = (f"Test: Wilcoxon signed-rank test (V = {_whole(r['v'])}, {r['how']}), which uses ranks, so it "
                      "does not need bell-shaped values.")
            if r["zeros"]:
                second += f" {r['zeros']} values exactly equal to {shown} were left out, as R does."
        row["rows"] = len(values)
        centre = "average" if based_on == "averages" else "median"
        if_none = f"the {centre} were truly {shown}"
        if up is not None:
            row["sides"] = f"one-sided: {'average' if up == 'average' else shown} higher"
            looks = f'an average of "{column}" above {shown}' if up == "average" else f'an average below {shown}'
            other = "an average below it" if up == "average" else "an average above it"
            second += " " + _one_sided_sentence(looks, other)
            if_none = f"the {centre} were truly not {'above' if up == 'average' else 'below'} {shown}"
        print(first)
        print(_p_sentence(r["p"], if_none, "a difference this big or bigger", f"that the {centre} is {shown}"))
        print(second)
        for note in r["notes"]:
            print(note)
        return self._result_table(row)

    def _z_test(self, step, column, values, value, sd, based_on, alt, up, shown):
        """The one-sample z-test with a known standard deviation, from R BSDA::z.test() (statsmodels' ztest
        uses the standard deviation of the values, so it is not this test)."""
        from .._r import r_call

        if based_on != "averages":
            raise SimplydataError('test="z" compares the average; leave out based_on=.')
        if isinstance(sd, bool) or not _is_number(sd) or not sd > 0:
            raise SimplydataError(f'test="z" needs the known standard deviation, such as standard_deviation=10 '
                                  f'(known beforehand, not worked out from "{column}").')
        side = {"two-sided": "two.sided", "greater": "greater", "less": "less"}[alt]
        found = r_call("z <- BSDA::z.test(x, mu = mu, sigma.x = s, alternative = side); "
                       "list(z = unname(z$statistic), p = z$p.value, ci = as.numeric(z$conf.int))", packages=("BSDA",),
                       what="the z-test with a known standard deviation (R BSDA::z.test())",
                       python_note="statsmodels ztest uses the standard deviation of the values, not a known one",
                       x=values, mu=value, s=float(sd), side=side)
        z, p = float(np.asarray(found["z"])[0]), float(np.asarray(found["p"])[0])
        low, high = (float(v) for v in np.asarray(found["ci"], dtype=float))
        mean = float(values.mean())
        diff = mean - value
        print(f'The average "{column}" is {_num(mean)}, which is {_num(abs(diff))} {"higher" if diff > 0 else "lower"} '
              f"than {shown} ({'' if up is None else 'one-sided '}95 % CI of the average {_interval_words(low, high)}).")
        if_none = f"the average were truly {shown}" if up is None else (
            f"the average were truly not {'above' if up == 'average' else 'below'} {shown}")
        print(_p_sentence(p, if_none, "a difference this big or bigger", f"that the average is {shown}"))
        second = (f"Test: z-test with the known standard deviation {sd:g} (z = {_num(z)}), as R BSDA::z.test(); use it "
                  "only when the spread is known beforehand, otherwise the t-test (leave out test=).")
        if up is not None:
            second += " " + _one_sided_sentence(f'an average of "{column}" above {shown}' if up == "average" else
                                                f"an average below {shown}",
                                                "an average below it" if up == "average" else "an average above it")
        print(second)
        return self._result_table({"test": "one-sample z-test", "what it compares": f'the average of "{column}" against '
                                   f"{shown}", "statistic name": "z", "statistic": z, "p-value": p,
                                   "known standard deviation": float(sd), "average": mean,
                                   "average 95 % CI low": low, "average 95 % CI high": high, "rows": len(values)})

    # ------------------------------------------------------------------ compare_counts_of
    @friendly(renamed={"between": "for_each_group_in", "for_each": "for_each_group_in", "seed": "with_seed"})
    def compare_counts_of(self, column=None, for_each_group_in=None, test=None, in_order=None, p_value_by="formula",
                          shuffles=9999, with_seed=1, show=None, bayesian=False):
        """Does how often each value turns up really differ between groups?

        table.add_group_column("result", from_column="marks", cut_at=[60], names=["below 60", "60 or more"])
        table.compare_counts_of("result", for_each_group_in="class")   (with sdata.get_example("marks"))
        (Do the classes differ in how many children score 60 or more?) Counts the rows for
        each pair of values and uses the chi-square test of independence (as R chisq.test():
        Yates' continuity correction for 2 x 2 tables only).
        If an expected count is below 5 a note says so; for a 2 x 2 table test="fisher" then
        gives Fisher's exact test. test="g": the G-test (likelihood ratio, SciPy chi2_contingency(
        lambda_="log-likelihood"), as R DescTools::GTest()). For 2 x 2 tables also
        test="barnard" and test="boschloo": unconditional exact tests, often stronger than
        Fisher's, run in R (Exact::exact.test(method = "z-pooled" / "boschloo"), simplydata[r]).
        test="fisher" on a bigger table gives its p-value from 100,000 random tables with the
        same totals (SciPy, with_seed=1); p_value_by="exact" counts every table instead, in R
        (fisher.test()). p_value_by="shuffling": the chi-square p-value from shuffles=9999 random
        tables (SciPy, with_seed=1, as R chisq.test(simulate.p.value = TRUE)).
        test="trend" with in_order=["low", "middle", "high"] (the for_each groups in order) and a
        yes/no column: the Cochran-Armitage test for a trend in the percent across ordered groups
        (R prop.trend.test()). show="cells" gives back one row per cell with its standardised
        residual (statsmodels, as R chisq.test()$stdres): cells beyond 2 or -2 stand out.
        Empty cells are skipped. Effect size: Cramer's V, the
        strength of the link from 0 (none) to 1 (complete). Gives back a one-row table.
        Under a survey design (table.use_survey_design) it gives the Rao-Scott F test, R
        survey::svychisq.
        bayesian=True gives the Bayes factor and each group's shares with 95 % credible intervals
        instead of a p-value: R BayesFactor::contingencyTableBF(sampleType = "indepMulti", fixedMargin =
        "rows"), each group's total fixed (the for_each_group_in= groups are the rows), with the
        Gunel-Dickey prior (concentration 1); 10,000 posterior draws (with_seed=1). Needs R (BayesFactor).
        """
        if self._survey_on():
            self._survey_only("compare_counts_of", locals(), ("column", "for_each_group_in"))
            return self._survey_compare_counts(column, for_each_group_in)
        step = "compare_counts_of"
        example = 'with sdata.get_example("fruit"): table.compare_counts_of("fruit", for_each_group_in="shop")'
        self._need_name(step, "the column", column, example)
        self._need_name(step, "for_each_group_in=", for_each_group_in, example)
        self._need_columns(column, for_each_group_in)
        if test is not None:
            self._check_choice(step, "test", test, COUNT_TESTS + ("trend",))
        self._check_choice(step, "p_value_by", p_value_by, ("formula", "exact", "shuffling"))
        if show is not None:
            self._check_choice(step, "show", show, ("cells",))
        if isinstance(with_seed, bool) or not isinstance(with_seed, (int, np.integer)):
            raise SimplydataError("with_seed= needs a whole number, such as with_seed=1.")
        if isinstance(shuffles, bool) or not isinstance(shuffles, (int, np.integer)) or shuffles < 99:
            raise SimplydataError("shuffles= needs a whole number of 99 or more, such as shuffles=9999.")
        if column == for_each_group_in:
            raise SimplydataError(f"{step}() needs two different columns, for example {example}.")
        if bayesian is not False:
            self._check_bayesian(step, bayesian)
        frame = self._frame
        floats = [c for c in (column, for_each_group_in) if frame.schema[c].is_float()]
        if floats:
            frame = frame.with_columns(nw.col(c).fill_nan(None) for c in floats)
        kept = frame.select(column, for_each_group_in).drop_nulls()
        _skipped_note(len(frame) - len(kept), [column, for_each_group_in])
        rows_of = kept[column].to_list()
        cols_of = kept[for_each_group_in].to_list()
        order = lambda keys: sorted(set(keys), key=lambda k: (str(type(k)), k))  # noqa: E731
        row_keys, col_keys = order(rows_of), order(cols_of)
        if len(row_keys) < 2 or len(col_keys) < 2:
            few = column if len(row_keys) < 2 else for_each_group_in
            raise SimplydataError(f'{step}() needs at least 2 different values in "{few}".')
        if in_order is not None:
            if isinstance(in_order, str) or not hasattr(in_order, "__iter__"):
                raise SimplydataError(f'in_order= lists the "{for_each_group_in}" groups in order, such as '
                                      'in_order=["low", "middle", "high"].')
            given = list(in_order)
            missing = [k for k in col_keys if k not in given and str(k) not in [str(g) for g in given]]
            if missing or len(given) != len(col_keys):
                raise SimplydataError(f'in_order= must list every "{for_each_group_in}" group once: '
                                      + _list_words(f'"{_label(k)}"' for k in col_keys) + ".")
            col_keys = [next(k for k in col_keys if k == g or str(k) == str(g)) for g in given]
        elif test == "trend":
            raise SimplydataError(f'test="trend" needs the "{for_each_group_in}" groups in order: in_order=[...] (lowest first).')
        observed = np.zeros((len(row_keys), len(col_keys)), dtype=np.int64)
        ri = {k: i for i, k in enumerate(row_keys)}
        ci = {k: i for i, k in enumerate(col_keys)}
        for r_, c_ in zip(rows_of, cols_of):
            observed[ri[r_], ci[c_]] += 1
        if bayesian:
            from . import bayes_words

            bayes_words.check_bayes_options(step, [
                ("test=", test, None), ("in_order=", in_order, None), ("p_value_by=", p_value_by, "formula"),
                ("shuffles=", shuffles, 9999), ("show=", show, None)])
            return bayes_words.counts(self, column, for_each_group_in, [_label(v) for v in rows_of],
                                      [_label(v) for v in cols_of], [_label(k) for k in row_keys],
                                      [_label(k) for k in col_keys], int(with_seed))
        if test == "trend":
            return self._trend_test(step, observed, column, for_each_group_in, row_keys, col_keys)
        result = self._counts_engine(observed, column, for_each_group_in, test, p_value_by=p_value_by, shuffles=int(shuffles),
                                     seed=int(with_seed))
        if show == "cells":
            return self._count_cells(observed, column, for_each_group_in, row_keys, col_keys)
        return result

    def _count_cells(self, observed, column, for_each, row_keys, col_keys):
        """One row per cell: observed and expected counts and the standardised residual (statsmodels Table, as R
        chisq.test()$stdres)."""
        from statsmodels.stats.contingency_tables import Table

        table = Table(observed.astype(float))
        resid, expected = np.asarray(table.standardized_resids), np.asarray(table.fittedvalues)
        rows = []
        for i, rk in enumerate(row_keys):
            for j, ck in enumerate(col_keys):
                rows.append({column: _label(rk), for_each: _label(ck), "count": int(observed[i, j]),
                             "expected count": float(expected[i, j]), "standardised residual": float(resid[i, j])})
        out = [r for r in rows if abs(r["standardised residual"]) > 2]
        if out:
            listed = _list_words(f'"{r[column]}" in "{r[for_each]}" ({r["count"]}, expected {_num(r["expected count"])}, '
                                 f'residual {_num(r["standardised residual"])})' for r in out)
            print(f"Cells that stand out (standardised residual beyond 2 or -2): {listed}.")
        else:
            print("No cell stands out: every standardised residual lies between -2 and 2.")
        print("Method: standardised residuals (statsmodels Table.standardized_resids), as R chisq.test()$stdres.")
        frame = nw.from_dict({k: [r[k] for r in rows] for k in rows[0]}, backend=self._frame.implementation)
        return self._new_table(frame)

    def _trend_test(self, step, observed, column, for_each, row_keys, col_keys):
        """Cochran-Armitage test for a trend in a percent across ordered groups, R prop.trend.test() (statsmodels'
        test_ordinal_association is the linear-by-linear test, a different statistic)."""
        from .._r import r_call
        from .more_tests import _yes_no

        if observed.shape[0] != 2:
            raise SimplydataError(f'test="trend" needs a yes/no column; "{column}" has {observed.shape[0]} values.')
        yes, _, yes_words = _yes_no(column, list(row_keys))
        events = observed[row_keys.index(yes)].astype(float)
        totals = observed.sum(axis=0).astype(float)
        found = r_call("t <- stats::prop.trend.test(x, n); list(chi = unname(t$statistic), p = t$p.value)", packages=(),
                       what="the test for a trend across ordered groups (R prop.trend.test())",
                       python_note="statsmodels test_ordinal_association is the linear-by-linear test, a different "
                                   "statistic", x=events, n=totals)
        chi, p = float(np.asarray(found["chi"])[0]), float(np.asarray(found["p"])[0])
        listed = _list_words(f'{_num(e / t * 100)} % in "{_label(k)}"' for e, t, k in zip(events, totals, col_keys))
        print(f'"{column}" = {yes_words}: {listed} (in this order).')
        print(_p_sentence(p, "the percent truly had no trend across the groups", "a trend this strong or stronger",
                          "that there is no trend"))
        print(f"Test: Cochran-Armitage test for trend (chi-square = {_num(chi)}, df = 1), as R prop.trend.test(), with "
              f'scores 1 to {len(col_keys)} for the "{for_each}" groups in the order given.')
        row = {"test": "Cochran-Armitage test for trend", "what it compares":
               f'the percent "{column}" = {_label(yes)} across "{for_each}" in order', "statistic name": "chi-square",
               "statistic": chi, "degrees of freedom": 1.0, "p-value": p}
        for e, t, k in zip(events, totals, col_keys):
            row[f"percent {_label(yes)} in {_label(k)}"] = e / t * 100
        return self._result_table(row)

    def _counts_engine(self, observed, column, for_each, test, what=None, unit="rows", unrelated=None,
                       p_value_by="formula", shuffles=9999, seed=1):
        """compare_counts on a table of counts (also sdata.compare_counts([[20, 40], [30, 30]]))."""
        from scipy import stats

        empty = [f"row {i + 1}" for i in np.flatnonzero(observed.sum(axis=1) == 0)] + \
                [f"column {j + 1}" for j in np.flatnonzero(observed.sum(axis=0) == 0)]
        if empty:
            raise SimplydataError(f"The table of counts has only zeros in {_list_words(empty)}, so an expected count "
                                  "is 0 and the test cannot be worked out (R chisq.test() gives NaN). Leave that "
                                  "row or column out.")
        chi = stats.chi2_contingency(observed, correction=True)
        expected = chi.expected_freq
        n = int(observed.sum())
        v = float(stats.contingency.association(observed, method="cramer", correction=False))
        v_ci = interval_only("cramers_v", x=observed.astype(float))
        two_by_two = observed.shape == (2, 2)
        what = what or f'how often each "{column}" turns up in each "{for_each}"'
        row = {"test": None, "what it compares": what}
        size = f"{observed.shape[0]} x {observed.shape[1]}"
        if p_value_by != "formula" and test not in (None, "chi-square", "fisher"):
            raise SimplydataError(f'p_value_by= goes with the chi-square test or test="fisher", not test="{test}".')
        if test == "fisher" and not two_by_two:
            if p_value_by == "exact":
                from .._r import r_call

                p = float(np.asarray(r_call("stats::fisher.test(x, workspace = 2e8)$p.value", packages=(),
                                            what=f"Fisher's exact test on a {size} table (R fisher.test())",
                                            python_note=f"SciPy fisher_exact gives the p-value of a {size} table from random tables "
                                                        "(leave out p_value_by= for it, seeded)",
                                            x=observed.astype(float)))[0])
                how = "every table with the same totals counted, in R (fisher.test())"
            else:
                result = stats.fisher_exact(observed, method=stats.MonteCarloMethod(
                    n_resamples=FISHER_TABLES, rng=np.random.default_rng(seed)))
                p = float(result.pvalue)
                how = (f"from {FISHER_TABLES:,} random tables with the same totals (SciPy, with_seed={seed}); "
                       'p_value_by="exact" counts every table, in R')
            row.update({"test": "Fisher's exact test", "p-value": p})
            second = f"Test: Fisher's exact test on the {size} table (chosen with test=), its p-value {how}."
        elif test == "fisher":
            result = stats.fisher_exact(observed)
            p = float(result.pvalue)
            row.update({"test": "Fisher's exact test", "statistic name": "odds ratio (sample)",
                        "statistic": float(result.statistic), "p-value": p})
            second = ("Test: Fisher's exact test (chosen with test=), which gives an exact p-value, so it is safe "
                      "with small counts.")
        elif test == "g":
            g = stats.chi2_contingency(observed, lambda_="log-likelihood", correction=False)
            stat, p, df = float(g.statistic), float(g.pvalue), int(g.dof)
            row.update({"test": "G-test", "statistic name": "G", "statistic": stat, "degrees of freedom": float(df),
                        "p-value": p})
            second = (f"Test: G-test, the likelihood-ratio test of independence (G = {_num(stat)}, df = {df}), chosen "
                      "with test=; as R DescTools::GTest().")
        elif test in EXACT_METHODS:
            if not two_by_two:
                raise SimplydataError(f'test="{test}" works on 2 x 2 tables, but "{column}" and "{for_each}" make a '
                                      f"{size} table.")
            from .._r import r_call

            name = "Barnard's exact test" if test == "barnard" else "Boschloo's exact test"
            found = r_call(f'Exact::exact.test(x, method = "{EXACT_METHODS[test]}", to.plot = FALSE)$p.value',
                           packages=("Exact",), what=f"{name} (R Exact::exact.test())",
                           python_note=f"SciPy {test}_exact uses another two-sided rule, so its p-value differs from "
                                       "R's", x=observed.astype(float))
            p = float(found[0])
            row.update({"test": name, "p-value": p})
            second = (f"Test: {name} (chosen with test=), an unconditional exact test, run in R: Exact::exact.test("
                      f'method = "{EXACT_METHODS[test]}").')
        else:
            stat, p, df = float(chi.statistic), float(chi.pvalue), int(chi.dof)
            name = "chi-square test of independence"
            row.update({"test": name, "statistic name": "chi-square", "statistic": stat,
                        "degrees of freedom": float(df), "p-value": p})
            yates = " with Yates' continuity correction (as R chisq.test() does for 2 x 2 tables)" if two_by_two else ""
            second = f"Test: {name}{yates} (chi-square = {_num(stat)}, df = {df}), the usual test for counts."
            if p_value_by == "exact":
                raise SimplydataError('p_value_by="exact" for counts is Fisher\'s exact test: give test="fisher".')
            if p_value_by == "shuffling":
                plain = stats.chi2_contingency(observed, correction=False)
                shuffled = stats.chi2_contingency(observed, correction=False, method=stats.MonteCarloMethod(
                    n_resamples=shuffles, rng=np.random.default_rng(seed)))
                stat, p = float(plain.statistic), float(shuffled.pvalue)
                row.update({"statistic": stat, "p-value": p, "p-value by": f"{shuffles} random tables, seed {seed}"})
                second = (f"Test: {name} (chi-square = {_num(stat)}, without Yates' correction), its p-value from "
                          f"{shuffles} random tables with the same totals (SciPy, with_seed={seed}), as R "
                          "chisq.test(simulate.p.value = TRUE).")
        row.update({"effect size name": "strength of the link, 0 (none) to 1 (complete) (Cramer's V)",
                    "effect size": v, "effect size 95 % CI low": v_ci["low"], "effect size 95 % CI high": v_ci["high"],
                    "rows": n, "smallest expected count": float(expected.min())})
        first = (f"Comparing {what} ({size} table, {n} {unit}): Cramer's V = {_num(v)} ("
                 + (interval_text(v_ci["low"], v_ci["high"])[2:-1] + "; " if not v_ci["note"] else "")
                 + "0 means no link, 1 a complete link).")
        print(first)
        print(_p_sentence(p, unrelated or f'"{column}" and "{for_each}" were truly unrelated',
                          "differences this big or bigger", "that they are unrelated"))
        print(second)
        if v_ci["note"]:
            print(v_ci["note"])
        low = int((expected < 5).sum())
        if low and test != "fisher" and p_value_by != "shuffling":
            counts = "count is" if low == 1 else "counts are"
            note = (f"Note: {low} of the {expected.size} expected {counts} below 5, so the chi-square p-value "
                    "may be off. ")
            note += ('Fisher\'s exact test is safer here: test="fisher".' if two_by_two
                     else 'test="fisher" (or p_value_by="shuffling") gives a p-value that does not need large counts.')
            print(note)
        return self._result_table(row)

    # ------------------------------------------------------------------ one column of values against chosen shares
    def _filled_values(self, step, column, example):
        """The values of one column (any kind) without empty cells, which are skipped with a note."""
        self._need_name(step, "the column", column, example)
        self._need_columns(column)
        kept = self._frame.filter(~self._empty(column))
        _skipped_note(len(self._frame) - len(kept), [column])
        return [_plain(v) for v in kept[column].to_list()]

    @friendly
    def compare_counts_to(self, column=None, expected=None):
        """Does how often each value turns up really differ from the shares you expect?

        table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})   (with sdata.get_example("school"))
        The chi-square goodness-of-fit test (as R chisq.test(x, p = ...)). expected= gives
        the share of each value, adding up to 1 (or percents adding up to 100); for a ratio
        such as 9:3:3:1 write {"a": 9/16, "b": 3/16, ...}. Without expected= every value is
        expected equally often (as R chisq.test(table(x))). Empty cells are skipped. If an
        expected count is below 5 a note says so. Effect size: Cohen's w, how far the counts
        are from the expected shares (0.1 small, 0.3 medium, 0.5 large). For one value
        against one percent, compare_percent_to() gives an exact test.
        Gives back a one-row table with the count and expected count of each value.
        """
        step = "compare_counts_to"
        example = ('with sdata.get_example("school"): '
                   'table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})')
        values = self._filled_values(step, column, example)
        counts: dict = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1
        order = sorted(counts, key=_order)
        if expected is None:
            if len(order) < 2:
                raise SimplydataError(f'{step}() needs at least 2 different values in "{column}"; it found '
                                      f"{len(order)}.\nFor example, {example}")
            labels, observed = order, [counts[k] for k in order]
            shares = [1.0 / len(order)] * len(order)
            how = "the same share for every value"
        else:
            labels, observed, shares = self._expected_shares(step, column, expected, counts, order, example)
            how = "the shares in expected="
        n = sum(observed)
        if n == 0:
            raise SimplydataError(f'"{column}" has no values to count.')
        from scipy import stats

        expected_counts = np.asarray(shares) * n
        chi = stats.chisquare(np.asarray(observed, dtype=float), expected_counts)
        stat, p = float(chi.statistic), float(chi.pvalue)
        df = len(labels) - 1
        from statsmodels.stats.gof import chisquare_effectsize

        w = float(chisquare_effectsize(np.asarray(shares, dtype=float), np.asarray(observed, dtype=float) / n))
        w_ci = interval_only("cohens_w", x=np.asarray(observed, dtype=float), p=np.asarray(shares, dtype=float))
        what = f'how often each "{column}" turns up, against {how}'
        row = {"test": "chi-square goodness-of-fit test", "what it compares": what, "statistic name": "chi-square",
               "statistic": stat, "degrees of freedom": float(df), "p-value": p,
               "effect size name": "distance of the counts from the expected shares (Cohen's w)", "effect size": w,
               "effect size 95 % CI low": w_ci["low"], "effect size 95 % CI high": w_ci["high"],
               "rows": n, "smallest expected count": float(expected_counts.min())}
        for label, o, e in zip(labels, observed, expected_counts):
            row[f"count of {_say_label(label)}"] = int(o)
            row[f"expected count of {_say_label(label)}"] = float(e)
        items = [f"{_say_label(k)} {o} (expected {_num(e)})" for k, o, e in zip(labels, observed, expected_counts)]
        shown = ", ".join(items[:GROUPS_SHOWN])
        if len(items) > GROUPS_SHOWN:
            shown += f" ... and {len(items) - GROUPS_SHOWN} more (the new table has them all)"
        print(f'Counts of "{column}" ({n} rows): {shown}. Cohen\'s w = {_num(w)}'
              f"{interval_text(w_ci['low'], w_ci['high'])}.")
        print(_p_sentence(p, "the expected shares were true", "differences this big or bigger from the expected counts",
                          "that the expected shares are right"))
        r_call = "chisq.test(table(x))" if expected is None else "chisq.test(x, p = ...)"
        print(f"Test: chi-square goodness-of-fit test (chi-square = {_num(stat)}, df = {df}), as R {r_call}; "
              "the usual test of counts against expected shares.")
        if w_ci["note"]:
            print(w_ci["note"])
        low = int((expected_counts < 5).sum())
        if low:
            counts_word = "count is" if low == 1 else "counts are"
            note = (f"Note: {low} of the {len(labels)} expected {counts_word} below 5, so the chi-square p-value may "
                    "be off. ")
            if len(labels) == 2:
                note += (f'With two values the exact binomial test is safer: table.compare_percent_to("{column}", '
                         f'value={_say_label(labels[0])!r}, percent={round(shares[0] * 100, 6):g}).')
            else:
                note += "Merge small groups, or collect more data."
            print(note)
        return self._result_table(row)

    @staticmethod
    def _expected_shares(step, column, expected, counts, order, example):
        """(labels, observed counts, shares adding up to 1) from expected={value: share}."""
        if not isinstance(expected, dict) or len(expected) < 2:
            raise SimplydataError(f"expected= needs the share of each value, at least two of them.\nFor example, {example}")
        bad = [k for k, v in expected.items() if not _is_number(v) or not math.isfinite(v) or v <= 0]
        if bad:
            raise SimplydataError(
                f"The expected share of {bad[0]!r} should be a number above 0, but it is {expected[bad[0]]!r}. "
                f"(A value that should never turn up cannot be tested; remove those rows first.)\nFor example, {example}"
            )
        total = float(sum(expected.values()))
        if math.isclose(total, 1.0, abs_tol=1e-6):
            scale = 1.0
        elif math.isclose(total, 100.0, abs_tol=1e-4):
            scale = 100.0
        else:
            raise SimplydataError(
                f"The expected shares add up to {_num(total)}; they should add up to 1 (or to 100 for percents). "
                "For a ratio such as 3:1, divide by its total: {\"yes\": 3/4, \"no\": 1/4}."
            )
        found = {}
        by_text = {str(k): k for k in order}
        for key in expected:
            if key in counts:
                found[key] = key
            elif str(key) in by_text:
                found[key] = by_text[str(key)]
            else:
                found[key] = None
        missing = [k for k in order if k not in found.values()]
        if missing:
            unknown = [k for k, v in found.items() if v is None]
            hint = ""
            if unknown:
                guesses = difflib.get_close_matches(str(unknown[0]), [str(k) for k in missing], n=1)
                hint = f' Did you mean "{guesses[0]}" for "{unknown[0]}"?' if guesses else ""
            raise SimplydataError(
                f'"{column}" has {_list_words(repr(_say_label(k)) for k in missing)}, which expected= does not '
                f"give a share for.{hint}\nGive a share for every value; values found: "
                f"{', '.join(repr(_say_label(k)) for k in order)}."
            )
        for key, value in found.items():
            if value is None:
                print(f'Note: {key!r} does not turn up in "{column}"; it counts as 0 rows.')
        labels = list(expected)
        observed = [counts[found[k]] if found[k] is not None else 0 for k in labels]
        shares = [float(expected[k]) / scale for k in labels]
        top = sum(shares)
        return labels, observed, [s / top for s in shares]

    @friendly(renamed={"method": "interval_by"})
    def compare_percent_to(self, column=None, value=None, percent=None, sides=2, higher=None, lower=None,
                           alternative=None, interval_by="exact"):
        """Is the percent of rows with one value really different from a percent you choose?

        table.compare_percent_to("passed", value="yes", percent=50)   (with sdata.get_example("school"))
        The exact binomial test (as R binom.test(x, n, p)), with the exact Clopper-Pearson
        95 % interval of the percent (as find_percent_of_rows_where()). Percents go from 0 to 100. For a
        yes/no column (yes/no, True/False or 1/0) value= may be left out: "yes" (True, 1)
        is counted. Empty cells are skipped. Effect size: Cohen's h, the difference between
        the two shares on the arcsine scale (0.2 small, 0.5 medium, 0.8 large).
        Gives back a one-row table of results.
        sides=1, higher="percent" (the data's percent is above percent=) or lower="percent"
        (below it) tests in one direction only (R binom.test(alternative = "greater")).
        interval_by= chooses the 95 % interval of the percent: "exact" (Clopper-Pearson, the default),
        "wilson" (Wilson score, SciPy) or "agresti-coull" (statsmodels proportion_confint), each as
        R DescTools::BinomCI(); the test stays the exact binomial test.
        """
        step = "compare_percent_to"
        from .summaries import PERCENT_METHODS, _percent_method

        method = _percent_method(step, interval_by)
        example = ('with sdata.get_example("school"): table.compare_percent_to("passed", value="yes", percent=50)')
        if not _is_number(percent) or not math.isfinite(percent):
            raise SimplydataError(f"{step}() needs percent= as a number from 0 to 100.\nFor example, {example}")
        if not 0 < percent < 100:
            raise SimplydataError(f"percent= should be above 0 and below 100 (it is {percent:g}).\nFor example, {example}")
        values = self._filled_values(step, column, example)
        if not values:
            raise SimplydataError(f'"{column}" has no values to count.')
        value, chosen_by = self._value_to_count(step, column, value, values, example)
        hits = sum(1 for v in values if v == value or (isinstance(v, str) and isinstance(value, str)
                                                         and chosen_by and v.strip().lower() == value.lower()))
        n = len(values)
        from scipy import stats

        side_example = (f'table.compare_percent_to("{column}", value={value!r}, percent={percent:g}, sides=1, '
                        'higher="percent")')
        alt, up = _direction(step, sides, higher, lower, alternative, {"percent": "greater", "_given": "less"},
                             side_example)
        result = stats.binomtest(hits, n, percent / 100.0, alternative=alt)
        p = float(result.pvalue)
        if method == "agresti-coull":
            if up is not None:
                raise SimplydataError('interval_by="agresti-coull" gives a two-sided interval only; with sides=1 use '
                                      'interval_by="exact" or interval_by="wilson".')
            from statsmodels.stats.proportion import proportion_confint

            low, high = proportion_confint(hits, n, alpha=0.05, method="agresti_coull")
        else:
            low, high = result.proportion_ci(confidence_level=0.95, method=method)
        share = hits / n
        from statsmodels.stats.proportion import proportion_effectsize

        h = float(proportion_effectsize(share, percent / 100.0))  # Cohen's h, as R pwr::ES.h
        label = _say_label(value)
        what = f'the percent of rows where "{column}" is "{label}", against {percent:g} %'
        row = {"test": "exact binomial test", "what it compares": what,
               "statistic name": f'rows where "{column}" is "{label}"', "statistic": float(hits), "p-value": p,
               "effect size name": "difference between the shares on the arcsine scale (Cohen's h)",
               "effect size": h, "percent": share * 100, "percent 95 % CI low": float(low) * 100,
               "percent 95 % CI high": float(high) * 100, "matching rows": hits, "rows": n}
        print(f'"{column}" is "{label}" in {share * 100:.1f} % of the rows ({hits} of {n}; 95 % CI {low * 100:.1f} % '
              f"to {high * 100:.1f} %), against {percent:g} %. Cohen's h = {_num(h)}.")
        side_words = ""
        if_none = f"the percent were truly {percent:g} %"
        if up is not None:
            if_none = f"the percent were truly not {'above' if up == 'percent' else 'below'} {percent:g} %"
            row["sides"] = f"one-sided: {'the percent' if up == 'percent' else f'{percent:g} %'} higher"
            side_words = " " + _one_sided_sentence(
                f"a percent above {percent:g} %" if up == "percent" else f"a percent below {percent:g} %",
                "a percent on the other side")
        print(_p_sentence(p, if_none, "a difference this big or bigger", f"that the percent is {percent:g} %"))
        print(f"Test: exact binomial test, as R binom.test({hits}, {n}, p = {percent / 100:g}"
              + ("" if up is None else f', alternative = "{alt}"') + "); the 95 % CI is the "
              f"{PERCENT_METHODS[method][0]}.{chosen_by}{side_words}")
        if percent < 1:
            print(f"Note: percent={percent:g} means {percent:g} %. For a half write percent=50.")
        return self._result_table(row)

    @staticmethod
    def _value_to_count(step, column, value, values, example):
        """(the value to count, words for the sentence when it was chosen from a yes/no column)."""
        if value is None:
            kinds = {type(v) for v in values}
            if kinds <= {bool}:
                return True, ' Counted as yes: True.'
            if all(_is_number(v) for v in values) and {float(v) for v in values} <= {0.0, 1.0}:
                return 1, " Counted as yes: 1."
            if kinds <= {str}:
                words = {v.strip().lower() for v in values}
                for yes, no in (("yes", "no"), ("true", "false"), ("y", "n")):
                    if words <= {yes, no}:
                        return yes, f' Counted as yes: "{yes}" (capital letters do not matter here).'
            shown = ", ".join(repr(v) for v in sorted({_say_label(v) for v in values})[:6])
            raise SimplydataError(
                f'{step}() needs value= to say which value of "{column}" to count, for example value={shown.split(", ")[0]}.\n'
                f"Values in \"{column}\": {shown}\nFor example, {example}"
            )
        if any(v == value for v in values):
            return value, ""
        shown = sorted({_say_label(v) for v in values})
        guess = difflib.get_close_matches(str(value), shown, n=1)
        hint = f' Did you mean "{guess[0]}"?' if guess else ""
        raise SimplydataError(
            f'value={value!r} is not in "{column}".{hint}\nValues in "{column}": '
            + ", ".join(repr(v) for v in shown[:8]) + (" ..." if len(shown) > 8 else "")
        )

    # ------------------------------------------------------------------ compare_shape_to
    @staticmethod
    def _shape_test_run(test, v, dist=None):
        """(statistic, p-value) of one shape test on the values v; each from SciPy or R, as R."""
        from scipy import stats

        if test == "shapiro-wilk":
            result = stats.shapiro(v)
        elif test == "dagostino":
            result = stats.normaltest(v)
        elif test == "jarque-bera":
            result = stats.jarque_bera(v)
        elif test == "lilliefors":
            from .._r import r_call

            found = r_call("r <- nortest::lillie.test(x); list(d = unname(r$statistic), p = r$p.value)",
                           packages=("nortest",), what="the Lilliefors test (R nortest::lillie.test())",
                           python_note="statsmodels lilliefors() uses another p-value approximation, which differs "
                                       "from R's (most above p = 0.1); the Shapiro-Wilk test (the default) needs no R",
                           x=v)
            return float(np.asarray(found["d"])[0]), float(np.asarray(found["p"])[0])
        elif test == "kolmogorov-smirnov":
            ties = len(np.unique(v)) < len(v)
            # R ks.test(): exact below 100 values without ties, otherwise the limiting distribution
            result = stats.ks_1samp(v, dist._cdf, method="asymp" if ties or len(v) >= 100 else "exact")
        else:
            result = stats.cramervonmises(v, dist._cdf)
        return float(result.statistic), float(result.pvalue)

    @friendly(renamed={"for_each": "for_each_group_in", "seed": "with_seed"})
    def compare_shape_to(self, column=None, shape="normal", for_each_group_in=None, with_seed=1, samples=9999, test=None,
                         full_turn=None):
        """Do the values look bell-shaped (normal), or are they too far from it?

        table.compare_shape_to("marks", "normal", for_each_group_in="class")   (with sdata.get_example("marks"))
        Uses the Shapiro-Wilk test (as R shapiro.test()), for 3 to 5000 values in each
        group; empty cells are skipped. A small p-value says a shape this far from a bell
        shape would rarely turn up if the values were bell-shaped. A large p-value does not
        prove the values are normal: with few values the test can miss a different shape, and
        with many values (30 or more) it flags even tiny, harmless differences, while tests on
        averages are then usually fine anyway (the central limit theorem). Gives back a table
        with one row per group.
        test= chooses another test of a bell shape: "lilliefors" (Kolmogorov-Smirnov with the
        average and standard deviation taken from the data, run in R: nortest::lillie.test()),
        "dagostino" (D'Agostino-Pearson, from skewness and kurtosis, SciPy normaltest, as R
        fBasics::dagoTest()) or "jarque-bera" (SciPy jarque_bera, as R tseries::jarque.bera.test()).

        A distribution with fixed numbers can be the shape too:
        table.compare_shape_to("marks", sdata.distribution("normal", average=60, standard_deviation=15))
        gives the one-sample Kolmogorov-Smirnov test (SciPy ks_1samp, as R ks.test(x, "pnorm", 60,
        15)); test="cramer-von-mises" the Cramer-von Mises test (SciPy cramervonmises, as R
        goftest::cvm.test()).

        Any other smooth shape works too: table.compare_shape_to("days", "gamma") fits the
        distribution (as table.fit_distribution_to) and runs the Anderson-Darling test, with a
        p-value from samples=9999 simulated samples that are each fitted again (with_seed=1,
        printed; the same seed gives the same p-value). Most shapes take a second or two; t,
        Cauchy and F take minutes, and a note says so before a long run. samples=999 is ten
        times quicker and gives a rougher p-value.

        Directions (or times of day) on a circle: table.compare_shape_to("current_direction",
        shape="even around the circle", full_turn=360) gives the Rayleigh test (test="rayleigh",
        R circular::rayleigh.test(), with the units always given): could the directions be
        spread evenly around the circle, or is there a preferred direction? full_turn= says how
        big a full turn is (360 degrees, 24 hours, "radians"); with it, shape="uniform" means
        even around the circle too.
        """
        from ..distributions import Distribution

        step = "compare_shape_to"
        example = 'with sdata.get_example("marks"): table.compare_shape_to("marks", "normal", for_each_group_in="class")'
        self._need_name(step, "the column", column, example)
        if full_turn is not None and isinstance(shape, Distribution):
            raise SimplydataError("full_turn= says the values are directions on a circle; a distribution of fixed numbers "
                                  "(sdata.distribution) is a shape on a line. Leave out one of them.")
        if self._circle_shape_wanted(shape, test, full_turn) or full_turn is not None:
            if isinstance(shape, str) and shape.strip().lower() == "normal" and test is None:
                print('On a circle (full_turn=) the shape to compare with is "even around the circle": the Rayleigh '
                      "test (review 3.1: the default with full_turn=).")
            return self._compare_circle(step, column, shape, full_turn, for_each_group_in, test)
        if isinstance(shape, str) and shape.strip().lower() in ("uniform", "even") and _looks_like_direction(column):
            print(f'Note: "{column}" looks like directions. On a circle, "uniform" means even around the circle: '
                  "add full_turn=360 (the Rayleigh test). Without it, the test below treats the values as a line, "
                  "and its answer depends on where 0 is.")
        if isinstance(test, str):
            test = SHAPE_TEST_ALIASES.get(test.strip().lower(), test.strip().lower())
        dist = shape if isinstance(shape, Distribution) else None
        if dist is not None:
            if dist.is_discrete:
                raise SimplydataError(f"{step}() compares with smooth (continuous) distributions; "
                                      f"{dist.label} is a distribution of counts.")
            test = test or "kolmogorov-smirnov"
            self._check_choice(step, "test", test, FIXED_SHAPE_TESTS)
        else:
            name = shape.strip().lower() if isinstance(shape, str) else shape
            if not isinstance(name, str) or not name:
                raise SimplydataError(f'{step}() needs a shape in quotes, such as "normal" or "gamma", or a '
                                      f"distribution from sdata.distribution(...).\nFor example, {example}")
            if name not in SHAPES:
                if test is not None:
                    raise SimplydataError(f'test= chooses a test of a bell shape ("normal"); for "{shape}" the test is '
                                          "Anderson-Darling with a fitted distribution (leave out test=).")
                return self._compare_other_shape(step, column, shape, for_each_group_in, with_seed, samples)
            test = test or "shapiro-wilk"
            if test in FIXED_SHAPE_TESTS:
                raise SimplydataError(f'test="{test}" compares with a distribution of fixed numbers, for example '
                                      f'table.compare_shape_to("{column}", sdata.distribution("normal", average=60, '
                                      f'standard_deviation=15), test="{test}").')
            self._check_choice(step, "test", test, NORMAL_TESTS)
        title, stat_name, r_name, smallest = SHAPE_TESTS[test]
        groups = self._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else []
        frame = self._number_frame(step, [column])
        values = frame.select(nw.col(column).cast(nw.Float64))[column].to_numpy()
        keys = [_key(r) for r in frame.select(groups).rows()] if groups else [()] * len(values)
        by_group: dict = {}
        for key, v in zip(keys, values):
            by_group.setdefault(key, [])
            if not math.isnan(v):
                by_group[key].append(v)
        order = sorted(by_group, key=lambda k: tuple(_order(v) for v in k))
        skipped = int(np.isnan(values).sum())
        _skipped_note(skipped, [column])

        rows, lines, any_large_flag = [], [], False
        if dist is None:
            what = f'the shape of "{column}" with a normal (bell-shaped) distribution'
            shape_words, null = "bell-shaped (normal)", "the values truly came from a bell shape"
            far = "a shape this far from normal or further"
            r_call_text = r_name
        else:
            what = f'the shape of "{column}" with the given distribution ({dist.label})'
            shape_words, null = "like the given distribution", "the values truly came from the given distribution"
            far = "a shape this far from it or further"
            r_call_text = r_name.replace("DIST", dist._r("p", "x").split("(", 1)[0]) if dist._r("p", "x") else r_name
        for key in order:
            v = np.asarray(by_group[key], dtype=float)
            n = len(v)
            label = " / ".join(_say_label(x) for x in key)
            problem = None
            if n < smallest:
                problem = f"only {n} value{'' if n == 1 else 's'}: {title.replace(' test', '')} needs at least {smallest}"
            elif test == "shapiro-wilk" and n > SHAPIRO_LIMIT:
                problem = (f"{n} values: Shapiro-Wilk works up to {SHAPIRO_LIMIT} values (as R); look at the shape "
                           f'on a chart instead, for example chart.draw_histogram(x="{column}"), or use test="dagostino"')
            elif np.ptp(v) == 0:
                problem = "every value is the same, so there is no shape to test"
            if problem and not groups:
                raise SimplydataError(f'{step}() cannot test "{column}": {problem}.')
            w = p = math.nan
            if not problem:
                w, p = self._shape_test_run(test, v, dist)
            row = {g: k for g, k in zip(groups, key)}
            row.update({"test": title, "what it compares": what, "statistic name": stat_name,
                        "statistic": w, "p-value": p, "rows": n})
            rows.append(row)
            if problem:
                lines.append(f"  {label}: not tested ({problem}).")
                continue
            if dist is None:
                looks = "do not look bell-shaped" if p < 0.05 else "could well be bell-shaped"
            else:
                looks = (f"do not look like the given distribution ({dist.label})" if p < 0.05 else
                         f"could well come from the given distribution ({dist.label})")
            if not groups:
                short = title.replace(" test", "")
                lines.append(f'The values of "{column}" {looks}{" (normal)" if dist is None else ""} ({short} '
                             f"{stat_name} = {w:.3f}, {n} values).")
                lines.append(_p_sentence(p, null, far, "that they are bell-shaped" if dist is None else
                                         "that they come from it"))
            else:
                lines.append(f"  {label}: {looks} ({stat_name} = {w:.3f}, {_p_shown(p)}, {n} values)")
            any_large_flag = any_large_flag or (p < 0.05 and n >= CLT_SIZE)
        chosen = "" if test in ("shapiro-wilk", "kolmogorov-smirnov") else "; chosen with test="
        if groups:
            names = " and ".join(f'"{g}"' for g in groups)
            print(f'Do the values of "{column}" look {shape_words} in each {names}? '
                  f"{title} (as R {r_call_text}{chosen}); each p-value says how often {far} "
                  f"would turn up if {null}:")
        for line in lines:
            print(line)
        if not groups:
            usual = {"shapiro-wilk": ", the usual check of a bell shape for 3 to 5000 values",
                     "lilliefors": ", run in R; the average and standard deviation come from the data",
                     "kolmogorov-smirnov": "; the distribution's numbers are fixed, not taken from the data"}
            print(f"Test: {title} (as R {r_call_text}){usual.get(test, '')}{chosen}.")
        else:
            print("A large p-value does not prove that the values are "
                  + ("bell-shaped." if dist is None else "like the given distribution."))
        if any_large_flag:
            print(f"Note: with {CLT_SIZE} or more values {title.replace(' test', '')} flags even small, harmless "
                  f"differences from {'a bell shape' if dist is None else 'the given distribution'}; tests on "
                  "averages are usually still fine (the central limit theorem).")
        data = {k: [r[k] for r in rows] for k in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    def _compare_other_shape(self, step, column, shape, for_each, seed, samples):
        """compare_shape_to() for any shape but normal: the engine is distributions.shape_test."""
        from ..distributions import _find_family, _shape_test_start, check_samples, shape_test, time_note

        try:
            _find_family(shape, step)
        except SimplydataError as error:  # the option here is shape=: say so in the did-you-mean
            raise SimplydataError(str(error).replace('Did you mean "', 'Did you mean shape="')) from None
        if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
            raise SimplydataError("with_seed= needs a whole number, such as with_seed=1 (the same seed gives the same p-value).")
        check_samples(samples, step)
        groups = self._group_columns(step, for_each, [column]) if for_each is not None else []
        frame = self._number_frame(step, [column])
        values = frame.select(nw.col(column).cast(nw.Float64))[column].to_numpy()
        keys = [_key(r) for r in frame.select(groups).rows()] if groups else [()] * len(values)
        by_group: dict = {}
        for key, v in zip(keys, values):
            by_group.setdefault(key, [])
            if not math.isnan(v):
                by_group[key].append(v)
        order = sorted(by_group, key=lambda k: tuple(_order(v) for v in k))
        _skipped_note(int(np.isnan(values).sum()), [column])
        started = [_shape_test_start(np.asarray(by_group[key], dtype=float), shape, seed, samples, column)
                   for key in order]
        note = time_note(sum(run[3].pilot() for run in started), samples, groups=len(started))
        if note:
            print(note)
        rows, method = [], None
        for key, ready in zip(order, started):
            label = " / ".join(_say_label(x) for x in key)
            result = shape_test(None, shape, seed=seed, samples=samples, column=column, _started=ready)
            sentence = result["sentence"]
            print(f"  {label}: {sentence}" if groups else sentence)
            method = result["method"]
            row = {g: k for g, k in zip(groups, key)}
            row.update({k: result[k] for k in ("test", "what it compares", "statistic name", "statistic", "p-value",
                                               "rows", "Monte Carlo samples", "seed")})
            rows.append(row)
        print(method)
        data = {k: [r[k] for r in rows] for k in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ many p-values at once
    @friendly
    def add_adjusted_p_value_column(self, name=None, from_column="p-value", method="holm"):
        """Adjust p-values for testing many things at once, in a new column.

        table = sdata.table(sdata.get_example("marks")).find_correlation_between("hours", "marks", "height", show="each pair")
        table.add_adjusted_p_value_column("p_adjusted", method="benjamini-hochberg")
        (table is now one row per pair of columns, with its p-value)
        The more tests you run, the more likely one of them looks real by chance; adjusted
        p-values allow for that. method="holm" (the default, as R p.adjust()): the chance
        of even one false alarm among all the tests stays at 5 %. "bonferroni": the same
        promise, simpler and stricter. "benjamini-hochberg" (also "bh" or "fdr"): about 5 %
        of the findings below 0.05 are expected to be false alarms (the false discovery
        rate); it finds more with many tests. "benjamini-yekutieli" ("by"): a false
        discovery rate that is safe however the tests depend on each other. "hochberg" and
        "hommel": the same promise as Holm, a little stronger, when the tests do not depend on
        each other in an unusual way (statsmodels multipletests, as R p.adjust()).
        method="storey" ("q-values" accepted): Storey's q-values, the false discovery rate with the
        share of true nulls (pi0) estimated from the p-values instead of set to 1 as in
        Benjamini-Hochberg (R qvalue::qvalue(), from Bioconductor; Storey & Tibshirani 2003); for
        hundreds or thousands of tests, such as genes. method="local fdr": each test's own chance of
        being a false discovery (qvalue's $lfdr), in a column called "local false discovery rate"; it
        is not an adjusted p-value. With fewer than 100 p-values pi0 is unstable, and a note says so.
        from_column= is the column of p-values ("p-value" in simplydata result tables).
        Without a name the new column is called, for example, "p-value (Holm)". Empty
        cells stay empty and are not counted, as R p.adjust().
        """
        step = "add_adjusted_p_value_column"
        example = ('results.add_adjusted_p_value_column("p_adjusted", from_column="p-value", method="benjamini-hochberg")\n'
                   '              (results from table.find_correlation_between("hours", "marks", "height", '
                   'show="each pair") with sdata.get_example("marks"))')
        chosen = _plain_name(method)
        chosen = ADJUST_ALIASES.get(chosen, chosen)
        if chosen not in ADJUST_METHODS and chosen not in STOREY_METHODS:
            raise choice_error(step, "method", method, list(ADJUST_METHODS) + list(STOREY_METHODS))
        label, r_name = ADJUST_METHODS.get(chosen, (STOREY_METHODS.get(chosen), None))
        if not isinstance(from_column, str):
            raise SimplydataError(f"{step}() needs from_column= as one column name in quotes.\nFor example:  {example}")
        self._need_columns(from_column)
        if name is None:
            name = "local false discovery rate" if chosen == "local fdr" else f"{from_column} ({label})"
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f"{step}() needs the new column's name in quotes.\nFor example:  {example}")
        frame = self._number_frame(step, [from_column])
        p = frame.select(nw.col(from_column).cast(nw.Float64))[from_column].to_numpy()
        given = ~np.isnan(p)
        bad = p[given & ((p < 0) | (p > 1))]
        if len(bad):
            raise SimplydataError(
                f'"{from_column}" should hold p-values, which go from 0 to 1, but it has {_num(bad[0])}.\n'
                f"For example:  {example}"
            )
        m = int(given.sum())
        if m == 0:
            raise SimplydataError(f'"{from_column}" has no p-values to adjust: every cell is empty.')
        adjusted = np.full(len(p), np.nan)
        before = int((p[given] < 0.05).sum())
        tests = "p-value" if m == 1 else "p-values"
        if chosen in STOREY_METHODS:
            from .risk_words import _say_pct
            from .small_r import storey

            found = storey(p[given], chosen)
            adjusted[given] = found["q"] if chosen == "storey" else found["lfdr"]
            after = int((adjusted[given] < 0.05).sum())
            pi0 = found["pi0"]
            share = _say_pct(pi0)
            if chosen == "storey":
                print(f'Added "{name}": Storey\'s q-values for {m} {tests} from "{from_column}" (R qvalue::qvalue()). '
                      f"About {share} of the tests look like true nulls (pi0 = {_num(pi0)}, estimated from the "
                      "p-values). A q-value of 0.05 means about 5 % of the results at least this small are false "
                      f"discoveries. Below 0.05: {after} of {m} q-values ({before} p-values).")
                print("Storey's q-values estimate pi0 from the data; Benjamini-Hochberg (method=\"benjamini-hochberg\")"
                      " is the same idea with pi0 = 1, so its numbers are never smaller (about 1 / pi0 times as large).")
            else:
                print(f'Added "{name}": for each of {m} {tests} from "{from_column}", the chance that this one test '
                      f"is a false discovery (R qvalue::qvalue()$lfdr, with pi0 = {_num(pi0)}, about {share} of the "
                      f"tests looking like true nulls). Below 0.05: {after} of {m}.")
                print("The local false discovery rate belongs to the one test; it is not an adjusted p-value (a q-value "
                      'is about all the results at least this small: method="storey").')
            if m < 100:
                print(f"Note: with fewer than 100 p-values ({m} here), the estimate of pi0 is unstable, so these "
                      'numbers can move a lot; method="benjamini-hochberg" does not estimate it.')
        else:
            adjusted[given] = _adjust_p(p[given], chosen)
            after = int((adjusted[given] < 0.05).sum())
            print(f'Added "{name}": {m} {tests} from "{from_column}" adjusted with {label}\'s method '
                  f'(as R p.adjust(method = "{r_name}")): {ADJUST_MEANING[chosen]}. '
                  f"Below 0.05: {after} of {m} after adjusting ({before} before).")
        values = [None if math.isnan(v) else float(v) for v in adjusted]
        base = nw.maybe_reset_index(self._frame)
        new = nw.new_series(name, values, nw.Float64, backend=base.implementation)
        if m < len(p):
            print(f"Note: {len(p) - m} empty cell{'' if len(p) - m == 1 else 's'} in \"{from_column}\" "
                  f"{'stays' if len(p) - m == 1 else 'stay'} empty and {'was' if len(p) - m == 1 else 'were'} "
                  "not counted.")
        return self._change(f'add adjusted p-value column "{name}" from {from_column} ({label})',
                            base.with_columns(new))
