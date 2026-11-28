"""Families for 100 %, batches 5-6 (approved by Manish 2026-11-28): every SciPy distribution by its plain name (one
shared name table, one test per name against SciPy), the joint (multivariate) names, "mixture", "from values",
"histogram", distribution.take_function, sdata.find_parameter_that_gives and the pointers of plan section 2.2."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import special, stats
from scipy.stats._distr_params import distcont, distdiscrete

import simplydata as sdata
from simplydata._distribution_names import PLAIN, Named
from simplydata._errors import SimplydataError
from simplydata.distributions import FAMILIES, distribution

SAMPLE = {name: args for name, args in distcont + distdiscrete}
SAMPLE["poisson_binom"] = ([0.2, 0.5, 0.7],)
SLOW = {"levy_stable", "studentized_range", "kstwo", "ksone", "gausshyper", "genhyperbolic", "jf_skew_t",
        "dpareto_lognorm", "landau", "irwinhall"}  # SciPy integrates these numerically: one point is enough
EXACT = {"rel": 1e-10, "abs": 1e-12}


def test_every_scipy_distribution_is_a_family_or_has_a_plain_name():
    every = {n for n in dir(stats) if isinstance(getattr(stats, n), (stats.rv_continuous, stats.rv_discrete))}
    families = set()
    for family in FAMILIES:
        for name in (family.name, *family.other_names):
            if name in every:
                families.add(name)
    assert every - families - set(PLAIN) <= {"bernoulli", "binom", "nbinom", "geom", "hypergeom", "poisson",
                                            "randint", "lognorm", "expon", "gamma", "beta", "uniform", "t", "chi2",
                                            "f", "weibull_min", "cauchy", "logistic", "laplace", "gumbel_r", "pareto",
                                            "genextreme", "genpareto", "triang", "halfnorm", "invgauss", "vonmises",
                                            "norm"}
    assert len(PLAIN) >= 101 - 4  # the 101 "already work by SciPy name" names, less the 4 joint ones counted there


@pytest.mark.parametrize("scipy_name", sorted(PLAIN))
def test_each_plain_name_gives_the_scipy_distribution(scipy_name, capsys):
    plain, others, shapes = PLAIN[scipy_name]
    args = SAMPLE[scipy_name]
    dist = getattr(stats, scipy_name)
    discrete = isinstance(dist, stats.rv_discrete)
    names = list(shapes.values())
    given = dict(zip(names, args))
    if not discrete:
        given.update(location=0.5, scale=2.0)
        frozen = dist(*args, loc=0.5, scale=2.0)
    else:
        given.update(shift=1)
        frozen = dist(*args, loc=1)
    ours = distribution(plain, **given)
    assert isinstance(ours._family, Named) and ours._family == scipy_name
    point = float(frozen.median())
    if discrete:
        assert ours.find_chance_that_value(is_at_most=point) == pytest.approx(float(frozen.cdf(point)), **EXACT)
        assert ours.find_chance_that_value(point) == pytest.approx(float(frozen.pmf(point)), **EXACT)
    else:
        assert ours.find_chance_that_value(is_below=point) == pytest.approx(float(frozen.cdf(point)), **EXACT)
        if scipy_name not in SLOW:
            assert ours.find_density_at(point) == pytest.approx(float(frozen.pdf(point)), **EXACT)
            assert ours.find_percentile(25) == pytest.approx(float(frozen.ppf(0.25)), rel=1e-8, abs=1e-10)
    out = capsys.readouterr().out
    assert plain in out  # the sentence names the distribution plainly
    for other in others:  # every other plain name gives the same distribution
        assert distribution(other, **given)._family == scipy_name
    # SciPy's own parameter names work as other spellings
    scipy_given = dict(zip([s.strip() for s in (dist.shapes or "").split(",") if s.strip()], args))
    assert distribution(plain, **scipy_given)._family == scipy_name


def test_plain_names_read_well_and_scipy_names_keep_working(capsys):
    dist = distribution("skew normal", shape=4, location=10, scale=2)
    assert repr(dist) == "Skew normal distribution (SciPy skewnorm) with shape 4, location 10, scale 2."
    assert dist.show_parameters() == {"shape": 4.0, "location": 10.0, "scale": 2.0}
    assert distribution("skewnorm", a=4, loc=10, scale=2).find_chance_that_value(is_below=11) == pytest.approx(
        dist.find_chance_that_value(is_below=11), **EXACT)
    assert repr(distribution("burr12", c=2, d=3)) == "SciPy's burr12 with c=2, d=3."
    for name, scipy_name in (("truncated normal", "truncnorm"), ("beta binomial", "betabinom"),
                             ("noncentral t", "nct"), ("log-logistic", "fisk"), ("inverse gamma", "invgamma"),
                             ("zipf", "zipf"), ("generalised normal", "gennorm"), ("generalized normal", "gennorm"),
                             ("Skew-Normal", "skewnorm"), ("frechet", "invweibull"), ("standard wald", "wald")):
        assert _scipy_of(name) == scipy_name
    assert distribution("wald", average=1, shape=2).name == "inverse gaussian"  # "wald" stays simplydata's family


def _scipy_of(plain):
    from simplydata._distribution_names import LOOKUP, _key

    return LOOKUP[_key(plain)]


@pytest.mark.parametrize("typed, says", [
    (dict(shape=4, average=1), "has no parameter called average="),
    (dict(location=1), "needs shape="),
    (dict(shape="x"), "shape= needs a number"),
])
def test_plain_name_errors_use_the_plain_parameters(typed, says):
    with pytest.raises(SimplydataError, match=says):
        distribution("skew normal", **typed)


def test_a_misspelt_plain_name_says_did_you_mean():
    with pytest.raises(SimplydataError, match='Did you mean "skew normal"'):
        distribution("skew normall", shape=2)


def test_fitting_by_plain_name_matches_scipy_fit():
    values = stats.skewnorm(4, 10, 2).rvs(300, random_state=np.random.default_rng(3))
    fit = sdata.number_list(values).fit_distribution("skew normal")
    a, loc, scale = stats.skewnorm.fit(values)
    ll_ours = fit._fit_info["log-likelihood"]
    assert ll_ours >= float(np.sum(stats.skewnorm(a, loc, scale).logpdf(values))) - 1e-6
    assert set(fit.show_parameters()) == {"shape", "location", "scale"}
    held = sdata.number_list(values).fit_distribution("skew normal", fixed={"location": 10})
    assert held.show_parameters()["location"] == 10


def test_poisson_binomial_takes_a_list_of_chances(capsys):
    dist = distribution("poisson binomial", chances=[0.2, 0.5, 0.7])
    assert dist.find_chance_that_value(is_at_most=1) == pytest.approx(stats.poisson_binom([0.2, 0.5, 0.7]).cdf(1))
    with pytest.raises(SimplydataError, match="list of chances"):
        distribution("poisson binomial", chances=0.3)


# ---------------------------------------------------------------- joint distributions
COV = [[1, 0.5], [0.5, 2]]


def test_multivariate_normal_density_chance_draws_average_and_covariance(capsys):
    dist = distribution("multivariate normal", averages=[0, 0], covariance=COV)
    frozen = stats.multivariate_normal([0, 0], COV)
    assert dist.find_density_at([1, 2]) == pytest.approx(frozen.pdf([1, 2]), **EXACT)
    assert dist.find_chance_that_value(is_below=[1, 2]) == pytest.approx(
        frozen.cdf([1, 2], rng=np.random.default_rng(1)), rel=1e-12)
    draws = dist.make_random_numbers(how_many=50, with_seed=4)
    assert draws.as_numpy() == pytest.approx(frozen.rvs(size=50, random_state=np.random.default_rng(4)), **EXACT)
    assert dist.find_average().as_numpy().tolist() == [0, 0]
    assert dist.find_variance().as_numpy() == pytest.approx(np.array(COV))
    with pytest.raises(SimplydataError, match="has no single percentile"):
        dist.find_percentile(50)


@pytest.mark.parametrize("name, params, scipy_name, scipy_params, value", [
    ("multivariate t", dict(location=[0, 0], spread=COV, degrees_of_freedom=5), "multivariate_t",
     dict(loc=[0, 0], shape=COV, df=5), [1, 2]),
    ("dirichlet", dict(concentrations=[2, 3, 5]), "dirichlet", dict(alpha=[2, 3, 5]), [0.2, 0.3, 0.5]),
    ("multinomial", dict(tries=10, chances=[0.2, 0.3, 0.5]), "multinomial", dict(n=10, p=[0.2, 0.3, 0.5]),
     [3, 3, 4]),
    ("multivariate hypergeometric", dict(counts=[5, 3, 2], drawn=4), "multivariate_hypergeom",
     dict(m=[5, 3, 2], n=4), [2, 1, 1]),
    ("dirichlet multinomial", dict(concentrations=[2, 3, 5], tries=10), "dirichlet_multinomial",
     dict(alpha=[2, 3, 5], n=10), [3, 3, 4]),
    ("wishart", dict(degrees_of_freedom=5, scale=[[1, 0], [0, 1]]), "wishart", dict(df=5, scale=[[1, 0], [0, 1]]),
     [[4, 1], [1, 5]]),
    ("inverse wishart", dict(degrees_of_freedom=5, scale=[[1, 0], [0, 1]]), "invwishart",
     dict(df=5, scale=[[1, 0], [0, 1]]), [[0.4, 0.1], [0.1, 0.5]]),
    ("matrix normal", dict(averages=[[0, 0], [0, 0]], row_covariance=[[1, 0], [0, 1]],
                           column_covariance=[[2, 0], [0, 1]]), "matrix_normal",
     dict(mean=[[0, 0], [0, 0]], rowcov=[[1, 0], [0, 1]], colcov=[[2, 0], [0, 1]]), [[1, 0], [0, 1]]),
    ("matrix t", dict(averages=[[0, 0], [0, 0]], row_spread=[[1, 0], [0, 1]], column_spread=[[1, 0], [0, 1]],
                      degrees_of_freedom=5), "matrix_t",
     dict(mean=[[0, 0], [0, 0]], row_spread=[[1, 0], [0, 1]], col_spread=[[1, 0], [0, 1]], df=5), [[1, 0], [0, 1]]),
    ("von mises-fisher", dict(direction=[0, 0, 1], concentration=10), "vonmises_fisher",
     dict(mu=[0, 0, 1], kappa=10), [0, 0.6, 0.8]),
    ("random table", dict(row_totals=[3, 5], column_totals=[4, 4]), "random_table", dict(row=[3, 5], col=[4, 4]),
     [[2, 1], [2, 3]]),
])
def test_each_joint_name_gives_the_scipy_density(name, params, scipy_name, scipy_params, value, capsys):
    dist = distribution(name, **params)
    frozen = getattr(stats, scipy_name)(**scipy_params)
    function = frozen.pmf if dist.is_discrete else frozen.pdf
    assert dist.find_density_at(value) == pytest.approx(float(np.asarray(function(value)).reshape(-1)[0]), **EXACT)
    if not hasattr(frozen, "rvs"):  # SciPy's dirichlet_multinomial draws nothing: simplydata says so
        with pytest.raises(SimplydataError, match="no single way to draw random numbers"):
            dist.make_random_numbers(how_many=3)
        return
    draws = dist.make_random_numbers(how_many=3, with_seed=2)
    expected = np.asarray(frozen.rvs(size=3, random_state=np.random.default_rng(2)), dtype=float)
    assert draws.as_numpy().ravel() == pytest.approx(expected.ravel(), **EXACT)


@pytest.mark.parametrize("name, params, scipy_name, scipy_params", [
    ("uniform direction", dict(dimensions=3), "uniform_direction", dict(dim=3)),
    ("random correlation", dict(eigenvalues=[0.5, 1.5, 1.0]), "random_correlation", dict(eigs=[0.5, 1.5, 1.0])),
    ("random orthogonal", dict(dimensions=3), "ortho_group", dict(dim=3)),
    ("random rotation", dict(dimensions=3), "special_ortho_group", dict(dim=3)),
])
def test_joint_names_without_a_density_draw_as_scipy(name, params, scipy_name, scipy_params, capsys):
    draws = distribution(name, **params).make_random_numbers(how_many=4, with_seed=5)
    frozen, rng = getattr(stats, scipy_name)(**scipy_params), np.random.default_rng(5)
    if scipy_name == "random_correlation":  # one grid at a time in SciPy
        expected = np.stack([frozen.rvs(random_state=rng) for _ in range(4)])
    else:
        expected = frozen.rvs(size=4, random_state=rng)
    assert draws.as_numpy().ravel() == pytest.approx(np.asarray(expected, dtype=float).ravel(), **EXACT)


def test_normal_inverse_gamma_draws_value_and_variance_pairs(capsys):
    draws = distribution("normal inverse gamma", average=0, precision=1, shape=2, scale=1).make_random_numbers(
        how_many=5, with_seed=1)
    x, s2 = stats.normal_inverse_gamma(mu=0, lmbda=1, a=2, b=1).rvs(size=5, random_state=np.random.default_rng(1))
    assert draws.as_numpy() == pytest.approx(np.column_stack([x, s2]), **EXACT)


def test_joint_errors_name_the_plain_parameters():
    with pytest.raises(SimplydataError, match="needs covariance="):
        distribution("multivariate normal", averages=[0, 0])
    with pytest.raises(SimplydataError, match="no parameter called mean_values="):
        distribution("dirichlet", mean_values=[1, 2])
    with pytest.raises(SimplydataError, match="complex numbers"):
        distribution("random unitary", dimensions=2).make_random_numbers(how_many=2)


# ---------------------------------------------------------------- mixture, from values, histogram
def test_mixture_matches_scipy_mixture(capsys):
    mixed = distribution("mixture", of=[distribution("normal"), distribution("normal", average=3)], shares=[0.3, 0.7])
    X = stats.Mixture([stats.Normal(mu=0, sigma=1), stats.Normal(mu=3, sigma=1)], weights=[0.3, 0.7])
    for x in (-1.0, 1.0, 2.5, 4.0):
        assert mixed.find_chance_that_value(is_below=x) == pytest.approx(float(X.cdf(x)), **EXACT)
        assert mixed.find_density_at(x) == pytest.approx(float(X.pdf(x)), **EXACT)
    assert mixed.find_percentile(50) == pytest.approx(float(X.icdf(0.5)), rel=1e-8)
    assert mixed.find_average() == pytest.approx(float(X.mean()), rel=1e-7)
    counts = distribution("mixture", of=[distribution("poisson", average=2), distribution("poisson", average=8)],
                          shares=[0.5, 0.5])
    assert counts.find_chance_that_value(is_at_most=4) == pytest.approx(
        0.5 * stats.poisson(2).cdf(4) + 0.5 * stats.poisson(8).cdf(4), **EXACT)
    with pytest.raises(SimplydataError, match="not both"):
        distribution("mixture", of=[distribution("normal"), distribution("poisson", average=2)])


def test_from_values_and_histogram_match_scipy(capsys):
    values = distribution("from values", values=[5, 1, 2], chances=[0.3, 0.2, 0.5])
    frozen = stats.rv_discrete(values=([1, 2, 5], [0.2, 0.5, 0.3]))
    assert values.find_average() == pytest.approx(frozen.mean())
    assert values.find_chance_that_value(is_at_most=2) == pytest.approx(frozen.cdf(2))
    hist = distribution("histogram", counts=[3, 9, 4], bin_edges=[0, 1, 2, 3])
    made = stats.rv_histogram(([3, 9, 4], [0, 1, 2, 3]), density=False)
    assert hist.find_percentile(80) == pytest.approx(made.ppf(0.8), **EXACT)
    numbers = stats.norm(5, 2).rvs(200, random_state=np.random.default_rng(1))
    from_numbers = distribution("histogram", of=sdata.number_list(numbers), bins=12)
    made = stats.rv_histogram(np.histogram(numbers, bins=12), density=False)
    assert from_numbers.find_chance_that_value(is_below=6) == pytest.approx(made.cdf(6), **EXACT)
    with pytest.raises(SimplydataError, match="add up to 1"):
        distribution("from values", values=[1, 2], chances=[0.5, 0.6])


# ---------------------------------------------------------------- take_function
NORMAL = dict(average=1, standard_deviation=0.5)


@pytest.mark.parametrize("name, made", [
    ("exp", lambda: stats.exp(stats.Normal(mu=1, sigma=0.5))),
    ("absolute value", lambda: stats.abs(stats.Normal(mu=1, sigma=0.5))),
])
def test_take_function_matches_scipy_functions_of_a_random_variable(name, made, capsys):
    ours = distribution("normal", **NORMAL).take_function(name)
    X = made()
    for x in (0.3, 1.0, 2.0):
        assert ours.find_chance_that_value(is_below=x) == pytest.approx(float(X.cdf(x)), **EXACT)
        assert ours.find_density_at(x) == pytest.approx(float(X.pdf(x)), **EXACT)
    assert ours.find_percentile(70) == pytest.approx(float(X.icdf(0.7)), rel=1e-8)


def test_take_function_log_and_order_statistic_match_scipy(capsys):
    lognormal = distribution("lognormal", log_average=0.2, log_standard_deviation=0.4)
    logged = lognormal.take_function("log")
    X = stats.Normal(mu=0.2, sigma=0.4)  # the log of a lognormal is the normal of its log average and spread
    assert logged.find_chance_that_value(is_below=0.5) == pytest.approx(float(X.cdf(0.5)), **EXACT)
    assert logged.find_percentile(10) == pytest.approx(float(X.icdf(0.1)), rel=1e-10)
    second = distribution("normal", **NORMAL).take_function("order statistic", rank=2, out_of=5)
    Y = stats.order_statistic(stats.Normal(mu=1, sigma=0.5), r=2, n=5)
    assert second.find_chance_that_value(is_below=0.9) == pytest.approx(float(Y.cdf(0.9)), **EXACT)
    assert second.find_density_at(0.9) == pytest.approx(float(Y.pdf(0.9)), rel=1e-10)
    assert second.find_percentile(50) == pytest.approx(float(Y.icdf(0.5)), rel=1e-10)


def test_take_function_says_what_is_wrong():
    with pytest.raises(SimplydataError, match="values above 0"):
        distribution("normal").take_function("log")
    with pytest.raises(SimplydataError, match="rank= and out_of="):
        distribution("normal").take_function("order statistic", rank=6, out_of=5)
    with pytest.raises(SimplydataError, match="smooth distribution"):
        distribution("poisson", average=3).take_function("exp")


# ---------------------------------------------------------------- sdata.find_parameter_that_gives
CASES = [
    ("t", dict(chance_below=0.975, at_value=2.1), lambda r: stats.t(r).cdf(2.1), 0.975, "stdtridf"),
    ("chi-square", dict(chance_below=0.9, at_value=7.8), lambda r: stats.chi2(r).cdf(7.8), 0.9, "chdtriv"),
    ("F", dict(chance_below=0.95, at_value=3.1, degrees_of_freedom_1=3), lambda r: stats.f(3, r).cdf(3.1), 0.95,
     "fdtridfd"),
    ("gamma", dict(chance_below=0.8, at_value=3, shape=2), lambda r: stats.gamma(2, scale=1 / r).cdf(3), 0.8, "gdtria"),
    ("gamma", dict(chance_below=0.8, at_value=3, rate=1.5), lambda r: stats.gamma(r, scale=1 / 1.5).cdf(3), 0.8,
     "gdtrib"),
    ("beta", dict(chance_below=0.6, at_value=0.3, shape2=5), lambda r: stats.beta(r, 5).cdf(0.3), 0.6, "btdtria"),
    ("beta", dict(chance_below=0.6, at_value=0.3, shape1=2), lambda r: stats.beta(2, r).cdf(0.3), 0.6, "btdtrib"),
    ("binomial", dict(chance_at_most=0.3, at_value=3, tries=10), lambda r: stats.binom(10, r).cdf(3), 0.3, "bdtri"),
    ("binomial", dict(chance_below=0.3, at_value=4, tries=10), lambda r: stats.binom(10, r).cdf(3), 0.3, "bdtri"),
    ("binomial", dict(chance_above=0.7, at_value=3, tries=10), lambda r: stats.binom(10, r).sf(3), 0.7, "bdtri"),
    ("negative binomial", dict(chance_at_most=0.4, at_value=2, size=3), lambda r: stats.nbinom(3, r).cdf(2), 0.4,
     "nbdtri"),
    ("poisson", dict(chance_at_least=0.2, at_value=5), lambda r: stats.poisson(r).sf(4), 0.2, "pdtri"),
    ("normal", dict(chance_below=0.9, at_value=60, average=50), lambda r: stats.norm(50, r).cdf(60), 0.9, "nrdtrisd"),
    ("normal", dict(chance_above=0.1, at_value=60, standard_deviation=8), lambda r: stats.norm(r, 8).sf(60), 0.1,
     "nrdtrimn"),
    ("noncentral chi-square", dict(chance_below=0.5, at_value=6, noncentrality=2),
     lambda r: stats.ncx2(r, 2).cdf(6), 0.5, "chndtridf"),
    ("noncentral t", dict(chance_below=0.9, at_value=3, degrees_of_freedom=10),
     lambda r: stats.nct(10, r).cdf(3), 0.9, "nctdtrinc"),
    ("noncentral F", dict(chance_below=0.9, at_value=4, degrees_of_freedom_1=3, degrees_of_freedom_2=20),
     lambda r: stats.ncf(3, 20, r).cdf(4), 0.9, "ncfdtrinc"),
]


@pytest.mark.parametrize("name, given, chance_of, target, function", CASES, ids=[c[4] for c in CASES])
def test_find_parameter_that_gives_matches_scipy_special_and_the_chance(name, given, chance_of, target, function,
                                                                         capsys):
    found = sdata.find_parameter_that_gives(name, **given)
    assert float(chance_of(found)) == pytest.approx(target, rel=1e-5)  # cdflib's search, about 6 digits
    assert f"scipy.special {function}" in capsys.readouterr().out


def test_find_parameter_that_gives_equals_stdtridf_exactly():
    assert sdata.find_parameter_that_gives("t", chance_below=0.975, at_value=2.1) == special.stdtridf(0.975, 2.1)


@pytest.mark.parametrize("given, says", [
    (dict(at_value=2), "Give one chance"),
    (dict(chance_below=1.2, at_value=2), "above 0 and below 1"),
    (dict(chance_below=0.9, at_value=2, degrees_of_freedom=3), "Leave out exactly one"),
])
def test_find_parameter_that_gives_says_what_is_wrong(given, says):
    with pytest.raises(SimplydataError, match=says):
        sdata.find_parameter_that_gives("t", **given)


def test_find_parameter_that_gives_knows_its_distributions():
    with pytest.raises(SimplydataError, match="knows the distributions"):
        sdata.find_parameter_that_gives("weibull", chance_below=0.5, at_value=2)


# ---------------------------------------------------------------- pointers
@pytest.mark.parametrize("scipy_name", sorted(PLAIN))
def test_every_scipy_distribution_points_to_its_plain_name(scipy_name, capsys):
    sdata.help(f"scipy.stats.{scipy_name}")
    out = capsys.readouterr().out
    assert "name from other tools" in out.splitlines()[0]
    assert f'sdata.distribution("{PLAIN[scipy_name][0]}"' in out


SPECIAL_POINTERS = {
    "bdtr": "find_chance_that_value", "bdtrc": "find_chance_that_value", "chdtr": "find_chance_that_value",
    "chdtrc": "find_chance_that_value", "fdtr": "find_chance_that_value", "fdtrc": "find_chance_that_value",
    "gdtr": "find_chance_that_value", "gdtrc": "find_chance_that_value", "nbdtr": "find_chance_that_value",
    "nbdtrc": "find_chance_that_value", "pdtr": "find_chance_that_value", "pdtrc": "find_chance_that_value",
    "stdtr": "find_chance_that_value", "btdtr": "find_chance_that_value", "chndtr": "find_chance_that_value",
    "ncfdtr": "find_chance_that_value", "nctdtr": "find_chance_that_value", "chdtri": "find_percentile",
    "fdtri": "find_percentile", "gdtrix": "find_percentile", "stdtrit": "find_percentile", "btdtri": "find_percentile",
    "chndtrix": "find_percentile", "ncfdtri": "find_percentile", "nctdtrit": "find_percentile",
    "bdtrik": "find_percentile", "nbdtrik": "find_percentile", "pdtrik": "find_percentile",
    "ndtri_exp": "find_percentile", "kolmogorov": "kolmogorov-smirnov limit", "kolmogi": "find_cut_off",
    "smirnov": "kolmogorov-smirnov one-sided", "smirnovi": "find_cut_off", "owens_t": "skew normal",
    "tklmbda": "tukey lambda",
    **{name: "find_parameter_that_gives" for name in (
        "stdtridf chdtriv fdtridfd gdtria gdtrib btdtria btdtrib bdtri bdtrin nbdtri nbdtrin pdtri nrdtrimn "
        "nrdtrisd chndtridf chndtrinc ncfdtridfd ncfdtridfn ncfdtrinc nctdtridf nctdtrinc").split()},
}


@pytest.mark.parametrize("name", sorted(SPECIAL_POINTERS))
def test_every_scipy_special_distribution_function_points_to_its_word(name, capsys):
    sdata.help(f"scipy.special.{name}")
    out = capsys.readouterr().out
    assert "name from other tools" in out.splitlines()[0], out
    assert SPECIAL_POINTERS[name] in out, out


@pytest.mark.parametrize("typed, word", [
    ("scipy.stats.multivariate_normal", "multivariate normal"), ("scipy.stats.wishart", "wishart"),
    ("scipy.stats.random_correlation", "random correlation"), ("scipy.stats.normal_inverse_gamma",
                                                               "normal inverse gamma"),
    ("rng.dirichlet", "dirichlet"), ("rng.multinomial", "multinomial"), ("rng.multivariate_normal",
                                                                         "multivariate normal"),
    ("rng.multivariate_hypergeometric", "multivariate hypergeometric"), ("scipy.stats.Mixture", "mixture"),
    ("scipy.stats.rv_discrete", "from values"), ("scipy.stats.rv_histogram", "histogram"),
    ("scipy.stats.log", "take_function"), ("scipy.stats.order_statistic", "order statistic"),
    ("scipy.stats.make_distribution", "plain name"), ("scipy.stats.Normal", "normal"),
    ("scipy.stats.Binomial", "binomial"),
])
def test_joint_and_made_distribution_names_point_to_their_words(typed, word, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    assert "name from other tools" in out.splitlines()[0], out
    assert word in out, out
