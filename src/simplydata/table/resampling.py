"""Shuffling (permutation tests) and the bootstrap: thin wrappers around SciPy.

simplydata does not resample by itself. Both helpers hand the data and the summary to SciPy:

* resample_p(): SciPy stats.permutation_test. kind="independent" shuffles the group labels,
  kind="paired" flips the sign of each row's change (each row's two values swap places),
  kind="pairings" shuffles which value goes with which (for a correlation). When there are no
  more arrangements than shuffles=, SciPy counts every one, and the p-value is exact. A two-sided
  p-value is twice the smaller one-sided p-value (SciPy, the same as R perm::permTS()).
* bootstrap_interval(): SciPy stats.bootstrap (BCa by default, as R boot::boot.ci(type = "bca")),
  resampling the rows with replacement resamples= times.

Both take seed= so the same seed gives the same answer; the sentences print the number of
shuffles or resamples and the seed (the wording rule: say physically what was done).
"""

from __future__ import annotations

import math

import numpy as np

from .._errors import SimplydataError

SHUFFLES = 9999
RESAMPLES = 9999
FEW_FOR_BOOTSTRAP = 20  # below this many values, a note: bootstrap intervals are often too narrow
KINDS = {"independent": "independent", "paired": "samples", "pairings": "pairings"}
BOOTSTRAP_METHODS = {"bca": "BCa", "percentile": "percentile", "basic": "basic"}


def check_seed_and_count(seed, count, option):
    """seed= a whole number; shuffles= / resamples= a whole number of 99 or more."""
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise SimplydataError("seed= needs a whole number, such as seed=1 (the same seed gives the same answer).")
    if isinstance(count, bool) or not isinstance(count, (int, np.integer)) or count < 99:
        raise SimplydataError(f"{option}= needs a whole number of 99 or more, such as {option}=9999.")


def arrangements(samples, kind) -> int:
    """How many different arrangements a full count would go through (display: whether all were counted)."""
    sizes = [len(s) for s in samples]
    if kind == "independent":
        count = math.factorial(sum(sizes))
        for n in sizes:
            count //= math.factorial(n)
        return count
    if kind == "paired":
        return 2 ** sizes[0]
    return math.factorial(sizes[0])


def resample_p(samples, statistic, kind="independent", alternative="two-sided", shuffles=SHUFFLES, seed=1,
               vectorized=True):
    """p-value from shuffling, SciPy stats.permutation_test. Gives back a dict with the p-value, the
    statistic, the number of arrangements, whether all were counted, and words for the sentence."""
    from scipy import stats

    check_seed_and_count(seed, shuffles, "shuffles")
    total = arrangements(samples, kind)
    exact = total <= shuffles
    data = tuple(np.asarray(s, dtype=float) for s in samples)
    if kind == "pairings":
        # only the order of the second column matters: SciPy then goes through its n! orders, not (n!)^2
        first, two_way = data[0], statistic
        data = data[1:]
        if vectorized:
            def statistic(y, axis=-1):
                return two_way(np.broadcast_to(first, np.shape(y)), y, axis=axis)
        else:
            def statistic(y):
                return two_way(first, y)
    result = stats.permutation_test(data, statistic,
                                    permutation_type=KINDS[kind], vectorized=vectorized,
                                    n_resamples=np.inf if exact else int(shuffles), alternative=alternative,
                                    rng=np.random.default_rng(int(seed)))
    what = {"independent": "the group labels were shuffled", "paired": "the two values in each row were swapped "
            "at random", "pairings": "the values of one column were shuffled against the other"}[kind]
    if exact:
        every = {"independent": "every way of sharing the values out between the groups",
                 "paired": "every way of swapping the two values within the rows",
                 "pairings": "every way of pairing the values of the two columns"}[kind]
        words = f"all {total:,} arrangements ({every}) were counted, so the p-value is exact"
        method = f"shuffling, all {total:,} arrangements counted"
    else:
        words = f"{what} {int(shuffles)} times (seed {int(seed)}); the same seed gives the same p-value"
        method = f"shuffled {int(shuffles)} times, seed {int(seed)}"
    return {"p": float(result.pvalue), "statistic": float(np.asarray(result.statistic)), "arrangements": total,
            "exact": exact, "words": words, "method": method}


def bootstrap_interval(samples, statistic, level=95, method="bca", resamples=RESAMPLES, seed=1, paired=False,
                       vectorized=True):
    """(low, high, words) from SciPy stats.bootstrap. method="bca" (default), "percentile" or "basic" (the
    reverse percentile interval; SciPy and R call it "basic")."""
    from scipy import stats

    check_seed_and_count(seed, resamples, "resamples")
    samples = tuple(np.asarray(s, dtype=float) for s in samples)
    import warnings

    with warnings.catch_warnings():  # a BCa interval SciPy cannot work out comes back empty; the word says so
        warnings.simplefilter("ignore")
        result = stats.bootstrap(samples, statistic, n_resamples=int(resamples), confidence_level=level / 100,
                                 method=BOOTSTRAP_METHODS[method], paired=paired, vectorized=vectorized,
                                 rng=np.random.default_rng(int(seed)))
    low, high = (float(v) for v in (result.confidence_interval.low, result.confidence_interval.high))
    name = {"bca": "bias-corrected and accelerated (BCa)", "percentile": "percentile",
            "basic": "reverse percentile"}[method]
    words = (f"{_level(level)} % bootstrap interval ({name}): the rows were drawn again at random, with "
             f"replacement, {int(resamples)} times (seed {int(seed)}), as R boot::boot.ci(type = "
             f"\"{'bca' if method == 'bca' else 'perc' if method == 'percentile' else 'basic'}\")")
    note = ""
    if min(len(s) for s in samples) < FEW_FOR_BOOTSTRAP:
        note = (f"Note: with fewer than {FEW_FOR_BOOTSTRAP} values the bootstrap interval is often too narrow; "
                "treat it as a rough guide.")
    return low, high, words, note


def _level(level):
    return f"{level:g}"


# The summaries the words shuffle or bootstrap (each a NumPy or SciPy call, for SciPy's vectorised use)
def difference_in_averages(x, y, axis=-1):
    return np.mean(x, axis=axis) - np.mean(y, axis=axis)


def average(x, axis=-1):
    return np.mean(x, axis=axis)


def correlation(method):
    """The correlation of two columns (SciPy pearsonr, spearmanr or kendalltau), for shuffling or the bootstrap."""
    from scipy import stats

    if method == "pearson":
        return lambda x, y, axis=-1: stats.pearsonr(x, y, axis=axis).statistic
    if method == "spearman":
        return lambda x, y: stats.spearmanr(x, y).statistic
    return lambda x, y: stats.kendalltau(x, y, variant="b").statistic
