"""More distributions for sdata.distribution (families for 100 %, batches 5-6; approved by Manish 2026-11-28, G4).

* Joint (multivariate) distributions as names of sdata.distribution, no new maker: "multivariate normal",
  "multivariate t", "dirichlet", "multinomial", "multivariate hypergeometric", "dirichlet multinomial", "wishart",
  "inverse wishart", "matrix normal", "matrix t", "von mises-fisher", "uniform direction", "random correlation",
  "random orthogonal", "random rotation", "random unitary", "random table" and "normal inverse gamma" (SciPy's
  multivariate_normal ... normal_inverse_gamma). A value is a list of numbers (or a grid for the matrix ones):
  find_density_at([1, 2]) gives the density there, make_random_numbers(how_many=100) a grid with one row per draw
  (a block for the matrix ones), find_average() the average values.
* "mixture": sdata.distribution("mixture", of=[first, second], shares=[0.3, 0.7]), the values of each distribution
  with those chances (SciPy stats.Mixture does the same sums).
* "from values": sdata.distribution("from values", values=[1, 2, 5], chances=[0.2, 0.5, 0.3]) (SciPy rv_discrete).
* "histogram": sdata.distribution("histogram", counts=[3, 9, 4], bin_edges=[0, 1, 2, 3]), or of=numbers with
  bins=10 (SciPy rv_histogram).
* distribution.take_function("log"): the distribution of the log of the values (also "exp", "absolute value" and
  "order statistic" with rank= and out_of=), as SciPy stats.log, stats.exp, stats.abs and stats.order_statistic.
"""

from __future__ import annotations

import math
import numbers as _nb

import numpy as np

from ._errors import SimplydataError, friendly
from .distributions import SEED, Distribution, _answer, _key, _percent, _say, _st

# ---------------------------------------------------------------- joint distributions: one table
# plain name: (SciPy name, other names, [(plain parameter, SciPy parameter, needed)], kind of value, counts?)
# kind: "vector" (a list of numbers), "matrix" (a grid), "pair" (normal inverse gamma: a value and a variance)
JOINT = {
    "multivariate normal": ("multivariate_normal", ("mvn", "multivariate gaussian", "multinormal"),
                            [("averages", "mean", True), ("covariance", "cov", True)], "vector", False),
    "multivariate t": ("multivariate_t", ("multivariate student t",),
                       [("location", "loc", True), ("spread", "shape", True), ("degrees_of_freedom", "df", True)],
                       "vector", False),
    "dirichlet": ("dirichlet", (), [("concentrations", "alpha", True)], "vector", False),
    "multinomial": ("multinomial", (), [("tries", "n", True), ("chances", "p", True)], "vector", True),
    "multivariate hypergeometric": ("multivariate_hypergeom", ("multivariate hypergeom",),
                                    [("counts", "m", True), ("drawn", "n", True)], "vector", True),
    "dirichlet multinomial": ("dirichlet_multinomial", (), [("concentrations", "alpha", True), ("tries", "n", True)],
                              "vector", True),
    "wishart": ("wishart", (), [("degrees_of_freedom", "df", True), ("scale", "scale", True)], "matrix", False),
    "inverse wishart": ("invwishart", ("invwishart", "inverse-wishart"),
                        [("degrees_of_freedom", "df", True), ("scale", "scale", True)], "matrix", False),
    "matrix normal": ("matrix_normal", (), [("averages", "mean", True), ("row_covariance", "rowcov", True),
                                            ("column_covariance", "colcov", True)], "matrix", False),
    "matrix t": ("matrix_t", (), [("averages", "mean", True), ("row_spread", "row_spread", True),
                                  ("column_spread", "col_spread", True), ("degrees_of_freedom", "df", True)],
                 "matrix", False),
    "von mises-fisher": ("vonmises_fisher", ("von mises fisher", "vonmises fisher"),
                         [("direction", "mu", True), ("concentration", "kappa", True)], "vector", False),
    "uniform direction": ("uniform_direction", ("random direction",), [("dimensions", "dim", True)], "vector", False),
    "random correlation": ("random_correlation", ("random correlation matrix",), [("eigenvalues", "eigs", True)],
                           "matrix", False),
    "random orthogonal": ("ortho_group", ("random orthogonal matrix", "ortho group"), [("dimensions", "dim", True)],
                          "matrix", False),
    "random rotation": ("special_ortho_group", ("random rotation matrix", "special orthogonal"),
                        [("dimensions", "dim", True)], "matrix", False),
    "random unitary": ("unitary_group", ("random unitary matrix", "unitary group"), [("dimensions", "dim", True)],
                       "matrix", False),
    "random table": ("random_table", ("random contingency table",),
                     [("row_totals", "row", True), ("column_totals", "col", True)], "matrix", True),
    "normal inverse gamma": ("normal_inverse_gamma", ("normal-inverse-gamma",),
                             [("average", "mu", False), ("precision", "lmbda", False), ("shape", "a", False),
                              ("scale", "b", False)], "pair", False),
}
JOINT_LOOKUP = {}
for _plain, (_scipy, _others, _, _, _) in JOINT.items():
    for _name in (_plain, _scipy, *_others):
        JOINT_LOOKUP[_key(_name)] = _plain
SPECIAL = {"mixture": "mixture", "mixture distribution": "mixture", "from values": "from values",
           "rv_discrete": "from values", "discrete from values": "from values", "histogram": "histogram",
           "rv_histogram": "histogram", "from histogram": "histogram"}


def kind_of(name) -> str | None:
    """"joint", "mixture", "from values" or "histogram" for a name of this module; None otherwise."""
    if not isinstance(name, str):
        return None
    key = _key(name)
    if key in JOINT_LOOKUP:
        return "joint"
    return SPECIAL.get(key)


def make(name, parameters: dict):
    kind = kind_of(name)
    if kind == "joint":
        return JointDistribution(JOINT_LOOKUP[_key(name)], parameters)
    if kind == "mixture":
        return _mixture(parameters)
    if kind == "from values":
        return _from_values(parameters)
    return _histogram(parameters)


def _as_values(value):
    """A list, a tuple, sdata.number_list or sdata.number_grid -> a NumPy array (other values stay as they are)."""
    if hasattr(value, "as_numpy"):
        value = value.as_numpy()
    if isinstance(value, (list, tuple, np.ndarray)):
        found = np.asarray(value)
        if found.dtype.kind in "iu":
            return found  # whole numbers stay whole: counts, tries and totals
        return found.astype(float)
    return value


class JointDistribution(Distribution):
    """A joint (multivariate) distribution of several values at once, made by sdata.distribution("multivariate
    normal", averages=[0, 0], covariance=grid) and the other joint names: find_density_at([1, 2]),
    make_random_numbers(how_many=100) (one row per draw), find_average(), find_variance() (the covariance grid where
    SciPy gives one) and find_chance_that_value(is_below=[1, 2]) for the multivariate normal and t."""

    def __init__(self, plain, parameters, backend=None):
        stats = _st()
        scipy_name, _, params, kind, counts = JOINT[plain]
        example = _joint_example(plain)
        known = {p for p, _, _ in params} | {s for _, s, _ in params}
        unknown = [k for k in parameters if k not in known]
        if unknown:
            names = ", ".join(f"{p}=" for p, _, _ in params)
            raise SimplydataError(f'The {plain} distribution has no parameter called {unknown[0]}=. Its parameters: '
                                  f"{names} (SciPy's names work too).\nFor example:  {example}")
        given = {}
        for plain_name, scipy_param, needed in params:
            value = parameters.get(plain_name, parameters.get(scipy_param))
            if plain_name in parameters and scipy_param in parameters and plain_name != scipy_param:
                raise SimplydataError(f"Give {plain_name}= once (or SciPy's {scipy_param}=), not both.")
            if value is None:
                if needed:
                    raise SimplydataError(f"The {plain} distribution needs {plain_name}=.\nFor example:  {example}")
                continue
            given[scipy_param] = _as_values(value)
        try:
            frozen = getattr(stats, scipy_name)(**given)
        except Exception as error:  # SciPy says what is wrong with the numbers: say it in plain words
            raise SimplydataError(f"These values do not make a {plain} distribution: {error}\n"
                                  f"For example:  {example}") from None
        object.__setattr__(self, "_family", plain)
        object.__setattr__(self, "_params", {p: given[s] for p, s, _ in params if s in given})
        object.__setattr__(self, "_fit_info", None)
        object.__setattr__(self, "_backend", backend)
        object.__setattr__(self, "_frozen", frozen)
        object.__setattr__(self, "_joint", (scipy_name, kind, counts))

    @property
    def is_discrete(self) -> bool:
        return self._joint[2]

    @property
    def name(self) -> str:
        return self._family

    @property
    def label(self) -> str:
        return self._family

    @property
    def r_call(self) -> str:
        return f"no R function here (SciPy {self._joint[0]})"

    def _describe(self) -> str:
        parts = []
        for k, v in self._params.items():
            parts.append(f"{k.replace('_', ' ')} {_shown_value(v)}")
        return f"{self._family} distribution (SciPy {self._joint[0]}) with " + ", ".join(parts)

    def _r(self, kind, x, upper=False):
        return None

    def __repr__(self):
        text = self._describe()
        return f"{text[0].upper()}{text[1:]}."

    def _param_text(self) -> str:
        return ", ".join(f"{k.replace('_', ' ')} {_shown_value(v)}" for k, v in self._params.items())

    def _shown(self, name):
        return name.replace("_", " ")

    def _none(self, word, why=""):
        raise SimplydataError(f"A joint distribution of several values ({self._family}) has no single {word}"
                              f"{why}. Its words: find_density_at, make_random_numbers, find_average, find_variance"
                              f"{', find_chance_that_value' if self._joint[0] in CDF_JOINT else ''} and "
                              "show_parameters.")

    @friendly
    def find_density_at(self, value=None):
        """The density (or for counts the chance) at one value. distribution.find_density_at([1, 2])"""
        if value is None:
            raise SimplydataError(f"find_density_at() needs a value: a list of numbers.\nFor example:  "
                                  f"distribution.find_density_at({_value_example(self)})")
        point = _as_values(value)
        function = getattr(self._frozen, "pmf" if self.is_discrete else "pdf", None)
        if function is None:
            self._none("density", " in SciPy")
        try:
            found = float(np.asarray(function(point)).reshape(-1)[0])
        except Exception as error:  # noqa: BLE001 - a value of the wrong size: SciPy's words, in plain words
            raise SimplydataError(f"{_shown_value(point)} is not a value of this {self._family} distribution: "
                                  f"{error}") from None
        what = "chance of exactly" if self.is_discrete else "height of the density at"
        print(f"The {what} {_shown_value(point)} is {_answer(found)} ({self._family}, SciPy {self._joint[0]}."
              f"{'pmf' if self.is_discrete else 'pdf'}).")
        return found

    @friendly
    def find_chance_that_value(self, value=None, is_above=None, is_below=None, is_at_most=None, is_at_least=None,
                               is_between=None):
        """The chance that every value is below the given ones (the multivariate normal and t).
        distribution.find_chance_that_value(is_below=[1, 2])"""
        given = is_below if is_below is not None else is_at_most
        if self._joint[0] not in CDF_JOINT or given is None or any(
                v is not None for v in (value, is_above, is_at_least, is_between)) or (
                is_below is not None and is_at_most is not None):
            if self._joint[0] not in CDF_JOINT:
                self._none("chance below a value", " in SciPy")
            raise SimplydataError("find_chance_that_value() on a joint distribution takes is_below= (each value "
                                  "below its own limit), for example distribution.find_chance_that_value(is_below=[1, "
                                  "2]).")
        point = _as_values(given)
        rng = np.random.default_rng(SEED)
        found = float(self._frozen.cdf(point, rng=rng))
        print(f"The chance that each value is below {_shown_value(point)} is {_percent(found)} ({self._family}, SciPy "
              f"{self._joint[0]}.cdf, worked out by quasi-Monte Carlo integration with seed {SEED}).")
        return found

    @friendly(renamed={"seed": "with_seed"})
    def make_random_numbers(self, how_many=None, with_seed=SEED, rows=None, columns=None):
        """Values drawn at random: a grid with one row per draw (a block of grids for the matrix ones).
        distribution.make_random_numbers(how_many=100, with_seed=1)"""
        from .numbers._base import check_seed, check_whole
        from .numbers.blocks import number_block
        from .numbers.numbers import NumberGrid

        example = "distribution.make_random_numbers(how_many=100, with_seed=1)"
        if rows is not None or columns is not None:
            raise SimplydataError(f"A joint distribution gives one row per draw: give how_many=.\nFor example:  "
                                  f"{example}")
        if how_many is None:
            raise SimplydataError(f"make_random_numbers() needs how_many=.\nFor example:  {example}")
        size = check_whole("random_numbers", "how_many=", how_many, example, smallest=1)
        with_seed = check_seed(with_seed, example)
        if not hasattr(self._frozen, "rvs"):
            self._none("way to draw random numbers", " in SciPy")
        rng = np.random.default_rng(with_seed)
        if self._joint[0] == "random_correlation":  # SciPy draws one grid at a time
            values = np.stack([self._frozen.rvs(random_state=rng) for _ in range(size)])
        else:
            values = self._frozen.rvs(size=size, random_state=rng)
        kind = self._joint[1]
        seed_text = f"with_seed={with_seed}" if with_seed is not None else "no seed, so different every time"
        if kind == "pair":
            x, s2 = values
            values = np.column_stack([np.ravel(x), np.ravel(s2)])
            print(f"Drew {size} pairs (a value and its variance) from the {self._family} distribution ({seed_text}); "
                  "column 1 is the value, column 2 the variance.")
            return NumberGrid(values)
        values = np.asarray(values)
        if np.iscomplexobj(values):
            raise SimplydataError("A random unitary matrix holds complex numbers, which simplydata grids do not; "
                                  "draw it in SciPy: scipy.stats.unitary_group(dim=3).rvs().")
        values = values.astype(float)
        if kind == "matrix":
            values = values.reshape((size,) + values.shape[-2:])
            print(f"Drew {size} grids of {values.shape[1]} x {values.shape[2]} from the {self._family} distribution "
                  f"({seed_text}): a block with one page per draw.")
            return number_block(values)
        values = values.reshape(size, -1)
        print(f"Drew {size} values of {values.shape[1]} numbers each from the {self._family} distribution "
              f"({seed_text}): one row per draw.")
        return NumberGrid(values)

    @friendly
    def find_average(self):
        """The average of each value (the means). distribution.find_average()"""
        from .numbers.numbers import NumberGrid, Numbers

        mean = getattr(self._frozen, "mean", None)
        if mean is None:
            self._none("average", " in SciPy")
        found = np.asarray(mean() if callable(mean) else mean, dtype=float)  # an attribute on some, a method on others
        print(f"The average values of the {self._family} distribution: {_shown_value(found)} (SciPy "
              f"{self._joint[0]}.mean).")
        return NumberGrid(found) if found.ndim == 2 else Numbers(found.reshape(-1))

    @friendly
    def find_variance(self):
        """The covariance grid (or each value's variance where SciPy gives only those). distribution.find_variance()"""
        from .numbers.numbers import NumberGrid, Numbers

        cov = getattr(self._frozen, "cov", None)
        if cov is not None and not callable(cov):
            found, what = np.asarray(cov, dtype=float), "covariance grid"
        elif cov is not None:
            found, what = np.asarray(cov(), dtype=float), "covariance grid"
        elif getattr(self._frozen, "var", None) is not None:
            found, what = np.asarray(self._frozen.var(), dtype=float), "variance of each value"
        else:
            self._none("variance", " in SciPy")
        print(f"The {what} of the {self._family} distribution (SciPy {self._joint[0]}).")
        return NumberGrid(found) if found.ndim == 2 else Numbers(found.reshape(-1))

    def find_percentile(self, percent=None):
        """A joint distribution has no single percentile. distribution.find_percentile(95)"""
        self._none("percentile")

    def find_cut_off(self, with_chance_above=None, with_chance_below=None):
        """A joint distribution has no single cut-off. distribution.find_cut_off(with_chance_above=0.025)"""
        self._none("cut-off")

    def find_middle_range(self, percent=95):
        """A joint distribution has no single middle range. distribution.find_middle_range(95)"""
        self._none("middle range")

    def find_median(self):
        """A joint distribution has no single median. distribution.find_median()"""
        self._none("median")

    def find_standard_deviation(self):
        """See find_variance. distribution.find_standard_deviation()"""
        self._none("standard deviation", " (find_variance() gives the covariance grid)")

    def show_summary(self):
        """A joint distribution has no one-row summary. distribution.show_summary()"""
        self._none("summary row")

    def draw_chart(self, show="density", between=None):
        """Chart the random draws instead. distribution.draw_chart()"""
        self._none("density curve", " to draw (draw make_random_numbers(how_many=500) as dots instead)")

    @friendly
    def show_parameters(self):
        """The parameters by their plain names. distribution.show_parameters()"""
        return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in self._params.items()}

    @friendly
    def turn_into_table(self):
        """A one-row table: the distribution and its parameters. distribution.turn_into_table()"""
        row = {"distribution": self._family}
        row.update({k.replace("_", " "): _shown_value(v) for k, v in self._params.items()})
        return self._table(row)


CDF_JOINT = ("multivariate_normal", "multivariate_t")


def _shown_value(value) -> str:
    if isinstance(value, np.ndarray):
        if value.ndim == 0:
            return _say(float(value))
        if value.ndim == 1:
            return "[" + ", ".join(_say(v) for v in value) + "]"
        return "[" + ", ".join(_shown_value(row) for row in value) + "]"
    if isinstance(value, _nb.Real):
        return _say(value)
    return str(value)


def _value_example(dist) -> str:
    return {"multinomial": "[3, 5, 2]", "multivariate_hypergeom": "[2, 1, 1]",
            "dirichlet_multinomial": "[3, 5, 2]", "dirichlet": "[0.2, 0.3, 0.5]"}.get(dist._joint[0], "[1, 2]")


def _joint_example(plain) -> str:
    return {
        "multivariate normal": 'sdata.distribution("multivariate normal", averages=[0, 0], covariance=[[1, 0.5], '
                               "[0.5, 2]])",
        "multivariate t": 'sdata.distribution("multivariate t", location=[0, 0], spread=[[1, 0], [0, 1]], '
                          "degrees_of_freedom=5)",
        "dirichlet": 'sdata.distribution("dirichlet", concentrations=[2, 3, 5])',
        "multinomial": 'sdata.distribution("multinomial", tries=10, chances=[0.2, 0.3, 0.5])',
        "multivariate hypergeometric": 'sdata.distribution("multivariate hypergeometric", counts=[5, 3, 2], drawn=4)',
        "dirichlet multinomial": 'sdata.distribution("dirichlet multinomial", concentrations=[2, 3, 5], tries=10)',
        "wishart": 'sdata.distribution("wishart", degrees_of_freedom=5, scale=[[1, 0], [0, 1]])',
        "inverse wishart": 'sdata.distribution("inverse wishart", degrees_of_freedom=5, scale=[[1, 0], [0, 1]])',
        "matrix normal": 'sdata.distribution("matrix normal", averages=[[0, 0], [0, 0]], row_covariance=[[1, 0], '
                         "[0, 1]], column_covariance=[[1, 0], [0, 1]])",
        "matrix t": 'sdata.distribution("matrix t", averages=[[0, 0], [0, 0]], row_spread=[[1, 0], [0, 1]], '
                    "column_spread=[[1, 0], [0, 1]], degrees_of_freedom=5)",
        "von mises-fisher": 'sdata.distribution("von mises-fisher", direction=[0, 0, 1], concentration=10)',
        "uniform direction": 'sdata.distribution("uniform direction", dimensions=3)',
        "random correlation": 'sdata.distribution("random correlation", eigenvalues=[0.5, 1.5, 1.0])',
        "random orthogonal": 'sdata.distribution("random orthogonal", dimensions=3)',
        "random rotation": 'sdata.distribution("random rotation", dimensions=3)',
        "random unitary": 'sdata.distribution("random unitary", dimensions=3)',
        "random table": 'sdata.distribution("random table", row_totals=[3, 5], column_totals=[4, 4])',
        "normal inverse gamma": 'sdata.distribution("normal inverse gamma", average=0, precision=1, shape=2, '
                                "scale=1)",
    }[plain]


# ---------------------------------------------------------------- distributions made from others or from numbers
class MadeDistribution(Distribution):
    """A distribution simplydata makes from others or from numbers (a mixture, values with chances, a histogram, a
    function of a distribution): every word of a distribution works on it."""

    def __init__(self, name, label, describe, params, frozen, discrete, how, backend=None):
        object.__setattr__(self, "_family", name)
        object.__setattr__(self, "_params", params)
        object.__setattr__(self, "_fit_info", None)
        object.__setattr__(self, "_backend", backend)
        object.__setattr__(self, "_frozen", frozen)
        object.__setattr__(self, "_made", (label, describe, discrete, how))

    @property
    def is_discrete(self) -> bool:
        return self._made[2]

    @property
    def name(self) -> str:
        return self._family

    @property
    def label(self) -> str:
        return self._made[0]

    @property
    def r_call(self) -> str:
        return f"no R function here ({self._made[3]})"

    def _describe(self) -> str:
        return self._made[1]

    def _r(self, kind, x, upper=False):
        return None

    def __repr__(self):
        text = self._describe()
        return f"{text[0].upper()}{text[1:]} ({self._made[3]})."

    def _param_text(self) -> str:
        return ", ".join(f"{k} {_shown_value(v)}" for k, v in self._params.items())

    def _shown(self, name):
        return name

    @friendly
    def show_parameters(self):
        """What the distribution was made from. distribution.show_parameters()"""
        return dict(self._params)

    @friendly
    def turn_into_table(self):
        """A one-row table: the distribution and what it was made from. distribution.turn_into_table()"""
        row = {"distribution": self._family}
        row.update({k: _shown_value(v) if not isinstance(v, str) else v for k, v in self._params.items()})
        return self._table(row)


def _continuous_or_counts(parts, word):
    discrete = {d.is_discrete for d in parts}
    if len(discrete) > 1:
        raise SimplydataError(f"A {word} mixes either smooth distributions or distributions of counts, not both.")
    return discrete.pop()


def _mixture(parameters):
    example = ('sdata.distribution("mixture", of=[sdata.distribution("normal", average=0), '
               'sdata.distribution("normal", average=3)], shares=[0.3, 0.7])')
    unknown = [k for k in parameters if k not in ("of", "shares", "components", "weights")]
    if unknown:
        raise SimplydataError(f"A mixture takes of= (the distributions) and shares= (their chances); not "
                              f"{unknown[0]}=.\nFor example:  {example}")
    parts = parameters.get("of", parameters.get("components"))
    shares = parameters.get("shares", parameters.get("weights"))
    if not isinstance(parts, (list, tuple)) or len(parts) < 2 or not all(isinstance(d, Distribution) for d in parts):
        raise SimplydataError(f"of= needs a list of at least 2 distributions made with sdata.distribution(...).\n"
                              f"For example:  {example}")
    if any(isinstance(d, JointDistribution) for d in parts):
        raise SimplydataError("A mixture here mixes distributions of one value; joint distributions are left out.")
    if shares is None:
        shares = [1 / len(parts)] * len(parts)
    shares = np.asarray(_as_values(shares), dtype=float)
    if shares.shape != (len(parts),) or np.any(shares < 0) or not math.isclose(float(shares.sum()), 1, abs_tol=1e-9):
        raise SimplydataError(f"shares= needs one chance for each distribution, each 0 or more, adding up to 1.\n"
                              f"For example:  {example}")
    discrete = _continuous_or_counts(parts, "mixture")
    frozen = [d._frozen for d in parts]
    stats = _st()
    lows = [float(f.support()[0]) for f in frozen]
    highs = [float(f.support()[1]) for f in frozen]

    def rvs(size, random_state):
        rng = random_state if isinstance(random_state, np.random.Generator) else np.random.default_rng(random_state)
        n = int(np.prod(size)) if size is not None else 1
        which = rng.choice(len(frozen), size=n, p=shares)
        out = np.empty(n)
        for i, f in enumerate(frozen):
            picked = which == i
            if picked.any():
                out[picked] = f.rvs(size=int(picked.sum()), random_state=rng)
        return out.reshape(size if size is not None else ())

    if discrete:
        class _Mix(stats.rv_discrete):
            def _pmf(self, k):
                return sum(w * f.pmf(k) for w, f in zip(shares, frozen))

            def _cdf(self, k):
                return sum(w * f.cdf(k) for w, f in zip(shares, frozen))

            def _rvs(self, size=None, random_state=None):
                return rvs(size, random_state)

        made = _Mix(a=min(lows), b=max(highs), name="mixture")()
    else:
        class _Mix(stats.rv_continuous):
            def _pdf(self, x):
                return sum(w * f.pdf(x) for w, f in zip(shares, frozen))

            def _cdf(self, x):
                return sum(w * f.cdf(x) for w, f in zip(shares, frozen))

            def _sf(self, x):
                return sum(w * f.sf(x) for w, f in zip(shares, frozen))

            def _rvs(self, size=None, random_state=None):
                return rvs(size, random_state)

        made = _Mix(a=min(lows), b=max(highs), name="mixture")()
    labels = [d.label for d in parts]
    words = " and ".join(f"{_say(s * 100)} % {lab}" for s, lab in zip(shares, labels))
    return MadeDistribution("mixture", f"mixture of {words}", f"mixture of {words}",
                            {"of": "; ".join(labels), "shares": shares}, made, discrete,
                            "the shares times each distribution's density and chances, as SciPy stats.Mixture")


def _from_values(parameters):
    example = 'sdata.distribution("from values", values=[1, 2, 5], chances=[0.2, 0.5, 0.3])'
    unknown = [k for k in parameters if k not in ("values", "chances")]
    if unknown or "values" not in parameters:
        raise SimplydataError(f"A distribution from values takes values= and chances= (one chance each, adding up to "
                              f"1).\nFor example:  {example}")
    values = np.asarray(_as_values(parameters["values"]), dtype=float).reshape(-1)
    chances = parameters.get("chances")
    chances = (np.full(len(values), 1 / len(values)) if chances is None else
               np.asarray(_as_values(chances), dtype=float).reshape(-1))
    if len(values) < 1 or len(values) != len(chances) or len(set(values.tolist())) != len(values):
        raise SimplydataError(f"values= needs different numbers and chances= one chance for each.\nFor example:  "
                              f"{example}")
    if np.any(chances < 0) or not math.isclose(float(chances.sum()), 1, abs_tol=1e-9):
        raise SimplydataError(f"chances= needs chances of 0 or more that add up to 1.\nFor example:  {example}")
    order = np.argsort(values)
    values, chances = values[order], chances[order]
    made = _st().rv_discrete(values=(values, chances), name="from values")
    words = ", ".join(f"{_say(v)} ({_percent(c)})" for v, c in list(zip(values, chances))[:6])
    more = " ..." if len(values) > 6 else ""
    return MadeDistribution("from values", f"from values {words}{more}", f"distribution of the values {words}{more}",
                            {"values": values, "chances": chances}, made, True, "SciPy rv_discrete(values=)")


def _histogram(parameters):
    example = 'sdata.distribution("histogram", counts=[3, 9, 4], bin_edges=[0, 1, 2, 3])'
    unknown = [k for k in parameters if k not in ("counts", "bin_edges", "of", "bins")]
    if unknown:
        raise SimplydataError(f"A histogram distribution takes counts= and bin_edges=, or of=numbers and bins=.\n"
                              f"For example:  {example}")
    if "of" in parameters:
        if "counts" in parameters or "bin_edges" in parameters:
            raise SimplydataError("Give of= (the numbers, with bins=), or counts= with bin_edges=, not both.")
        x = np.asarray(_as_values(parameters["of"]), dtype=float).reshape(-1)
        x = x[~np.isnan(x)]
        bins = parameters.get("bins", 10)
        if len(x) < 2:
            raise SimplydataError("of= needs at least 2 numbers.")
        counts, edges = np.histogram(x, bins=bins)
        source = f"{len(x)} numbers in {len(counts)} bins"
    else:
        if "counts" not in parameters or "bin_edges" not in parameters:
            raise SimplydataError(f"A histogram distribution needs counts= and bin_edges= (one more edge than counts)."
                                  f"\nFor example:  {example}")
        counts = np.asarray(_as_values(parameters["counts"]), dtype=float).reshape(-1)
        edges = np.asarray(_as_values(parameters["bin_edges"]), dtype=float).reshape(-1)
        if len(edges) != len(counts) + 1 or not np.all(np.diff(edges) > 0) or np.any(counts < 0) or counts.sum() <= 0:
            raise SimplydataError(f"bin_edges= needs one more edge than counts=, each bigger than the one before, and "
                                  f"the counts 0 or more (not all 0).\nFor example:  {example}")
        source = f"{len(counts)} bins"
    made = _st().rv_histogram((counts, edges), density=False)
    return MadeDistribution("histogram", f"histogram of {source}", f"histogram distribution of {source}, from "
                            f"{_say(edges[0])} to {_say(edges[-1])}", {"counts": counts, "bin_edges": edges}, made,
                            False, "SciPy rv_histogram: even within each bin")


# ---------------------------------------------------------------- distribution.take_function
FUNCTIONS = {"log": "log", "ln": "log", "natural log": "log", "exp": "exp", "exponential": "exp",
             "absolute value": "absolute value", "abs": "absolute value", "absolute": "absolute value",
             "order statistic": "order statistic", "order_statistic": "order statistic"}


def take_function(dist, name=None, rank=None, out_of=None):
    """The distribution of a function of the values: "log", "exp", "absolute value" or "order statistic"."""
    stats = _st()
    example = 'log_distribution = distribution.take_function("log")'
    key = FUNCTIONS.get(str(name).strip().lower()) if isinstance(name, str) else None
    if key is None:
        from ._errors import choice_error

        raise choice_error("take_function", "name", name, ["log", "exp", "absolute value", "order statistic"])
    if isinstance(dist, JointDistribution) or dist.is_discrete:
        raise SimplydataError("take_function() works on a smooth distribution of one value (SciPy's functions of a "
                              "random variable are for continuous ones).")
    if (rank is not None or out_of is not None) and key != "order statistic":
        raise SimplydataError('rank= and out_of= go with take_function("order statistic").')
    f = dist._frozen
    low, high = (float(v) for v in f.support())
    if key == "log" and low < 0:
        raise SimplydataError(f"The log needs values above 0, but {dist.label} goes down to {_say(low)}.")
    if key == "order statistic":
        ok = all(isinstance(v, _nb.Integral) and not isinstance(v, bool) for v in (rank, out_of))
        if not ok or not 1 <= rank <= out_of:
            raise SimplydataError('take_function("order statistic") needs rank= and out_of=, whole numbers with 1 <= '
                                  'rank <= out_of: rank=1 is the smallest of out_of values.\nFor example:  '
                                  'distribution.take_function("order statistic", rank=2, out_of=5)')
    from scipy import special

    class _Function(stats.rv_continuous):
        def _cdf(self, y):
            if key == "log":
                return f.cdf(np.exp(y))
            if key == "exp":
                return f.cdf(np.log(y))
            if key == "absolute value":
                return f.cdf(y) - f.cdf(-y)
            return special.betainc(rank, out_of - rank + 1, f.cdf(y))

        def _sf(self, y):
            if key == "log":
                return f.sf(np.exp(y))
            if key == "exp":
                return f.sf(np.log(y))
            return 1 - self._cdf(y)

        def _pdf(self, y):
            if key == "log":
                return f.pdf(np.exp(y)) * np.exp(y)
            if key == "exp":
                return f.pdf(np.log(y)) / y
            if key == "absolute value":
                return f.pdf(y) + f.pdf(-y)
            u = f.cdf(y)
            return f.pdf(y) * u ** (rank - 1) * (1 - u) ** (out_of - rank) / special.beta(rank, out_of - rank + 1)

        def _ppf(self, p):
            if key == "log":
                return np.log(f.ppf(p))
            if key == "exp":
                return np.exp(f.ppf(p))
            if key == "order statistic":
                return f.ppf(special.betaincinv(rank, out_of - rank + 1, p))
            return super()._ppf(p)

    if key == "log":
        support = (math.log(low) if low > 0 else -math.inf, math.log(high) if math.isfinite(high) else math.inf)
        words = f"the log of {dist.label}"
    elif key == "exp":
        support = (math.exp(low) if math.isfinite(low) else 0.0, math.exp(high) if math.isfinite(high) else math.inf)
        words = f"exp of {dist.label}"
    elif key == "absolute value":
        support = (0.0 if low < 0 else low, max(abs(low), abs(high)))
        words = f"the absolute value of {dist.label}"
    else:
        support = (low, high)
        words = f"the order statistic {rank} of {out_of} (the {_ordinal_word(rank)} smallest of {out_of} values) of " \
                f"{dist.label}"
    made = _Function(a=support[0], b=support[1], name=key)()
    scipy_call = {"log": "stats.log", "exp": "stats.exp", "absolute value": "stats.abs",
                  "order statistic": "stats.order_statistic"}[key]
    params = {"function": key, "of": dist.label}
    if key == "order statistic":
        params.update({"rank": rank, "out of": out_of})
    out = MadeDistribution(f"{key} of a distribution", words, f"distribution of {words}", params, made, False,
                           f"the change of variables, as SciPy {scipy_call}")
    print(f"The distribution of {words}: ask it chances, percentiles and random numbers like any distribution "
          f"(the change of variables, as SciPy {scipy_call}).")
    del example
    return out


def _ordinal_word(n: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, f"{n}th")
