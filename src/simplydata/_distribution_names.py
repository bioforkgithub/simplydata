"""Plain names for every SciPy distribution (families for 100 %, batches 5-6; approved by Manish 2026-11-28, G3, G4).

sdata.distribution("skew normal", shape=4, location=10, scale=2) is SciPy's skewnorm, and the SciPy name works too
(sdata.distribution("skewnorm", a=4, loc=10, scale=2)). ONE table below holds, for each SciPy distribution that has no
family of its own in simplydata.distributions, its plain name, other plain names, and a plain name for each of its
shape parameters (in SciPy's order); location= and scale= are SciPy's loc and scale (for counts, shift= is loc). The
SciPy parameter names are accepted as other spellings. A parameter is called by what it does where that is clear
(degrees_of_freedom, chance, tries, lowest, highest); otherwise shape, or shape1, shape2 ... in SciPy's order, never a
name that would mislead (the skew normal's shape is not its skewness, so it is not called skewness).
"""

from __future__ import annotations

# scipy name: (plain name, other plain names, {SciPy shape: plain name})
PLAIN = {
    # ---------------------------------------------------------------- smooth (continuous) distributions
    "alpha": ("alpha", ("alpha distribution",), {"a": "shape"}),
    "anglit": ("anglit", (), {}),
    "arcsine": ("arcsine", ("arc sine",), {}),
    "argus": ("argus", ("ARGUS",), {"chi": "curvature"}),
    "betaprime": ("beta prime", ("inverted beta", "beta of the second kind"), {"a": "shape1", "b": "shape2"}),
    "bradford": ("bradford", (), {"c": "shape"}),
    "burr": ("burr type iii", ("burr 3", "burr iii", "dagum"), {"c": "shape1", "d": "shape2"}),
    "burr12": ("burr type xii", ("burr 12", "burr xii", "singh-maddala"), {"c": "shape1", "d": "shape2"}),
    "chi": ("chi", ("chi distribution",), {"df": "degrees_of_freedom"}),
    "cosine": ("cosine", ("raised cosine",), {}),
    "crystalball": ("crystal ball", (), {"beta": "tail_start", "m": "tail_power"}),
    "dgamma": ("double gamma", (), {"a": "shape"}),
    "dpareto_lognorm": ("double pareto lognormal", (), {"u": "log_average", "s": "log_standard_deviation",
                                                         "a": "upper_tail", "b": "lower_tail"}),
    "dweibull": ("double weibull", (), {"c": "shape"}),
    "erlang": ("erlang", (), {"a": "shape"}),
    "exponnorm": ("exponentially modified normal", ("ex-gaussian", "exgaussian", "exponentially modified gaussian"),
                  {"K": "shape"}),
    "exponpow": ("exponential power", (), {"b": "shape"}),
    "exponweib": ("exponentiated weibull", (), {"a": "shape1", "c": "shape2"}),
    "fatiguelife": ("fatigue life", ("birnbaum-saunders", "birnbaum saunders"), {"c": "shape"}),
    "fisk": ("log-logistic", ("fisk", "log logistic"), {"c": "shape"}),
    "foldcauchy": ("folded cauchy", (), {"c": "shape"}),
    "foldnorm": ("folded normal", (), {"c": "shape"}),
    "gausshyper": ("gauss hypergeometric", (), {"a": "shape1", "b": "shape2", "c": "shape3", "z": "shape4"}),
    "genexpon": ("generalised exponential", ("generalized exponential",),
                 {"a": "shape1", "b": "shape2", "c": "shape3"}),
    "gengamma": ("generalised gamma", ("generalized gamma",), {"a": "shape1", "c": "shape2"}),
    "genhalflogistic": ("generalised half-logistic", ("generalized half-logistic",), {"c": "shape"}),
    "genhyperbolic": ("generalised hyperbolic", ("generalized hyperbolic",),
                      {"p": "index", "a": "tail", "b": "asymmetry"}),
    "geninvgauss": ("generalised inverse gaussian", ("generalized inverse gaussian", "gig"),
                    {"p": "index", "b": "shape"}),
    "genlogistic": ("generalised logistic", ("generalized logistic",), {"c": "shape"}),
    "gennorm": ("generalised normal", ("generalized normal", "generalised error", "generalized error", "ged"),
                {"beta": "shape"}),
    "gibrat": ("gibrat", (), {}),
    "gompertz": ("gompertz", (), {"c": "shape"}),
    "gumbel_l": ("left gumbel", ("gumbel left", "gumbel minimum", "gumbel l"), {}),
    "halfcauchy": ("half-cauchy", ("half cauchy",), {}),
    "halfgennorm": ("half generalised normal", ("half generalized normal",), {"beta": "shape"}),
    "halflogistic": ("half-logistic", ("half logistic",), {}),
    "hypsecant": ("hyperbolic secant", (), {}),
    "invgamma": ("inverse gamma", (), {"a": "shape"}),
    "invweibull": ("inverse weibull", ("frechet", "fréchet"), {"c": "shape"}),
    "irwinhall": ("irwin-hall", ("irwin hall", "uniform sum"), {"n": "terms"}),
    "jf_skew_t": ("jones-faddy skew t", ("jones faddy skew t",), {"a": "shape1", "b": "shape2"}),
    "johnsonsb": ("johnson sb", (), {"a": "shape1", "b": "shape2"}),
    "johnsonsu": ("johnson su", (), {"a": "shape1", "b": "shape2"}),
    "kappa3": ("kappa 3", ("three-parameter kappa",), {"a": "shape"}),
    "kappa4": ("kappa 4", ("four-parameter kappa",), {"h": "shape1", "k": "shape2"}),
    "ksone": ("kolmogorov-smirnov one-sided", ("one-sided kolmogorov-smirnov",), {"n": "sample_size"}),
    "kstwo": ("kolmogorov-smirnov two-sided", ("two-sided kolmogorov-smirnov",), {"n": "sample_size"}),
    "kstwobign": ("kolmogorov-smirnov limit", ("kolmogorov", "kolmogorov distribution"), {}),
    "landau": ("landau", (), {}),
    "laplace_asymmetric": ("asymmetric laplace", ("laplace asymmetric",), {"kappa": "asymmetry"}),
    "levy": ("levy", ("lévy",), {}),
    "levy_l": ("left levy", ("levy left", "left lévy"), {}),
    "levy_stable": ("stable", ("levy stable", "alpha stable", "alpha-stable"), {"alpha": "stability", "beta": "skew"}),
    "loggamma": ("log gamma", ("log-gamma",), {"c": "shape"}),
    "loglaplace": ("log-laplace", ("log laplace",), {"c": "shape"}),
    "loguniform": ("log-uniform", ("log uniform",), {"a": "lowest", "b": "highest"}),
    "lomax": ("lomax", ("pareto type ii", "pareto ii"), {"c": "shape"}),
    "maxwell": ("maxwell", ("maxwell-boltzmann",), {}),
    "mielke": ("mielke beta-kappa", ("mielke",), {"k": "shape1", "s": "shape2"}),
    "moyal": ("moyal", (), {}),
    "nakagami": ("nakagami", (), {"nu": "shape"}),
    "ncf": ("noncentral F", ("non-central F",), {"dfn": "degrees_of_freedom_1", "dfd": "degrees_of_freedom_2",
                                                 "nc": "noncentrality"}),
    "nct": ("noncentral t", ("non-central t",), {"df": "degrees_of_freedom", "nc": "noncentrality"}),
    "ncx2": ("noncentral chi-square", ("non-central chi-square", "noncentral chi-squared"),
             {"df": "degrees_of_freedom", "nc": "noncentrality"}),
    "norminvgauss": ("normal inverse gaussian", ("nig",), {"a": "tail", "b": "asymmetry"}),
    "pearson3": ("pearson type iii", ("pearson 3", "pearson iii"), {"skew": "skewness"}),
    "powerlaw": ("power function", ("power law",), {"a": "shape"}),
    "powerlognorm": ("power lognormal", ("power log-normal",), {"c": "shape", "s": "log_standard_deviation"}),
    "powernorm": ("power normal", (), {"c": "shape"}),
    "rayleigh": ("rayleigh", (), {}),
    "rdist": ("r distribution", (), {"c": "shape"}),
    "recipinvgauss": ("reciprocal inverse gaussian", (), {"mu": "shape"}),
    "reciprocal": ("reciprocal", (), {"a": "lowest", "b": "highest"}),
    "rel_breitwigner": ("relativistic breit-wigner", ("relativistic breit wigner",), {"rho": "shape"}),
    "rice": ("rice", ("rician",), {"b": "shape"}),
    "semicircular": ("semicircular", ("wigner semicircle",), {}),
    "skewcauchy": ("skew cauchy", (), {"a": "shape"}),
    "skewnorm": ("skew normal", ("skew-normal", "skew gaussian"), {"a": "shape"}),
    "studentized_range": ("studentized range", (), {"k": "groups", "df": "degrees_of_freedom"}),
    "trapezoid": ("trapezoidal", ("trapezoid",), {"c": "rise_end", "d": "fall_start"}),
    "truncexpon": ("truncated exponential", (), {"b": "upper_end"}),
    "truncnorm": ("truncated normal", (), {"a": "lower_end", "b": "upper_end"}),
    "truncpareto": ("truncated pareto", (), {"b": "shape", "c": "upper_end"}),
    "truncweibull_min": ("truncated weibull", (), {"c": "shape", "a": "lower_end", "b": "upper_end"}),
    "tukeylambda": ("tukey lambda", (), {"lam": "shape"}),
    "vonmises_line": ("von mises line", (), {"kappa": "concentration"}),
    "wald": ("standard wald", ("standard inverse gaussian",), {}),
    "weibull_max": ("reversed weibull", ("weibull maximum", "weibull max"), {"c": "shape"}),
    "wrapcauchy": ("wrapped cauchy", (), {"c": "concentration"}),
    # ---------------------------------------------------------------- counts (discrete distributions)
    "betabinom": ("beta binomial", ("beta-binomial",), {"n": "tries", "a": "shape1", "b": "shape2"}),
    "betanbinom": ("beta negative binomial", ("beta-negative-binomial",), {"n": "size", "a": "shape1",
                                                                            "b": "shape2"}),
    "boltzmann": ("boltzmann", ("truncated discrete exponential",), {"lambda_": "rate", "N": "values"}),
    "dlaplace": ("discrete laplace", (), {"a": "shape"}),
    "logser": ("logarithmic", ("log series", "log-series", "logarithmic series"), {"p": "chance"}),
    "nchypergeom_fisher": ("fisher noncentral hypergeometric", ("fisher's noncentral hypergeometric",),
                           {"M": "total", "n": "marked", "N": "drawn", "odds": "odds"}),
    "nchypergeom_wallenius": ("wallenius noncentral hypergeometric", ("wallenius' noncentral hypergeometric",),
                              {"M": "total", "n": "marked", "N": "drawn", "odds": "odds"}),
    "nhypergeom": ("negative hypergeometric", (), {"M": "total", "n": "marked", "r": "failures"}),
    "planck": ("planck", ("discrete exponential",), {"lambda_": "rate"}),
    "poisson_binom": ("poisson binomial", (), {"p": "chances"}),
    "skellam": ("skellam", (), {"mu1": "average1", "mu2": "average2"}),
    "yulesimon": ("yule-simon", ("yule simon",), {"alpha": "shape"}),
    "zipf": ("zipf", ("zeta",), {"a": "shape"}),
    "zipfian": ("zipfian", ("finite zipf",), {"a": "shape", "n": "highest"}),
}

LOC_SCALE = {"loc": "location", "scale": "scale"}  # smooth distributions
LOC_COUNTS = {"loc": "shift"}  # counts: SciPy's loc moves every count by a whole number


def _key(text: str) -> str:
    import re

    return re.sub(r"[\s_\-']+", " ", text.strip().lower())


LOOKUP = {}
for _scipy, (_plain, _others, _) in PLAIN.items():
    for _name in (_plain, *_others):
        LOOKUP[_key(_name)] = _scipy


class Named(str):
    """A SciPy distribution typed by its plain name: the string is SciPy's name (so every SciPy call works), and it
    knows the plain name and the plain names of its parameters."""

    def __new__(cls, scipy_name):
        made = super().__new__(cls, scipy_name)
        made.plain = PLAIN[scipy_name][0]
        return made

    @property
    def names(self) -> dict:
        """SciPy parameter -> plain name, location and scale included."""
        from scipy import stats

        dist = getattr(stats, str(self))
        extra = LOC_COUNTS if isinstance(dist, stats.rv_discrete) else LOC_SCALE
        return {**PLAIN[str(self)][2], **extra}

    def to_scipy(self, given: dict) -> dict:
        """The parameters as typed (plain or SciPy names) -> SciPy's names; an unknown name is kept, for SciPy's
        own error."""
        back = {plain: scipy for scipy, plain in self.names.items()}
        out = {}
        for key, value in given.items():
            name = back.get(key, key)
            if name in out:
                from ._errors import SimplydataError

                raise SimplydataError(f"{key}= gives {self.names.get(name, name)}= a second time: give it once.")
            out[name] = value
        return out

    def shown(self, scipy_param: str) -> str:
        return self.names.get(scipy_param, scipy_param).replace("_", " ")
