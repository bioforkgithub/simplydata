"""Families for 100 %, batches 5-6 (approved by Manish 2026-11-28): the SciPy distributions by their plain names, the
joint (multivariate) names, "mixture", "from values" and "histogram", distribution.take_function and
sdata.find_parameter_that_gives (plan section 2.2), each next to the SciPy code that does the same job."""

from . import Entry

TOLD = "simplydata also says the answer in a sentence, with the distribution in plain words."

ENTRIES = [
    Entry(
        word="sdata.distribution",
        option='"studentized range"',
        ours="""
            distribution = sdata.distribution("studentized range", groups=3, degrees_of_freedom=20)
            distribution.find_percentile(95)
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("studentized range", groups=3, degrees_of_freedom=20)
            stats.studentized_range(3, 20).ppf(0.95)              # (1)
        """},
        compare="value",
        tolerance=1e-9,
        choices=("every SciPy distribution by a plain name, with a plain name for each parameter (here k is groups= "
                 "and df degrees_of_freedom=); SciPy's names work too.",),
        also="One name table holds all of them (\"skew normal\", \"truncated normal\", \"beta binomial\" ...), so "
             "help, errors and sentences use the plain names. " + TOLD,
    ),
    Entry(
        word="sdata.distribution",
        option='"multivariate normal"',
        ours="""
            pair = sdata.distribution("multivariate normal", averages=[0, 0], covariance=[[1, 0.5], [0.5, 2]])
            pair.find_density_at([1, 2])
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("multivariate normal", averages=[0, 0], covariance=[[1, 0.5], [0.5, 2]])
            pair = stats.multivariate_normal(mean=[0, 0], cov=[[1, 0.5], [0.5, 2]])   # (1)
            pair.pdf([1, 2])
        """},
        compare="value",
        tolerance=1e-12,
        choices=("joint distributions are names of sdata.distribution too (averages= is SciPy's mean, covariance= "
                 "its cov); make_random_numbers gives one row per draw.",),
        also=TOLD,
    ),
    Entry(
        word="sdata.distribution",
        option='"multinomial"',
        ours="""
            gears = sdata.distribution("multinomial", tries=32, chances=[1 / 3, 1 / 3, 1 / 3])
            gears.find_density_at([15, 12, 5])
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("multinomial", tries=32, chances=[1 / 3, 1 / 3, 1 / 3])
            stats.multinomial(n=32, p=[1 / 3, 1 / 3, 1 / 3]).pmf([15, 12, 5])   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("for counts find_density_at gives the chance of exactly those counts (SciPy pmf).",),
        also=TOLD,
    ),
    Entry(
        word="sdata.distribution",
        option='"wishart"',
        ours="""
            spread = sdata.distribution("wishart", degrees_of_freedom=5, scale=[[1, 0], [0, 1]])
            spread.find_density_at([[4, 1], [1, 5]])
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("wishart", degrees_of_freedom=5, scale=[[1, 0], [0, 1]])
            stats.wishart(df=5, scale=[[1, 0], [0, 1]]).pdf([[4, 1], [1, 5]])   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("a value of a matrix distribution is a grid; random draws come as a block, one page per draw.",),
        also=TOLD,
    ),
    Entry(
        word="sdata.distribution",
        option='"mixture"',
        ours="""
            first = sdata.distribution("normal", average=0, standard_deviation=1)
            second = sdata.distribution("normal", average=3, standard_deviation=1)
            mixed = sdata.distribution("mixture", of=[first, second], shares=[0.3, 0.7])
            mixed.find_chance_that_value(is_below=1)
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("mixture", of=[first, second], shares=[0.3, 0.7])
            parts = [stats.Normal(mu=0, sigma=1), stats.Normal(mu=3, sigma=1)]
            stats.Mixture(parts, weights=[0.3, 0.7]).cdf(1)       # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the shares times each distribution's chances, added up; percentiles by root finding, random "
                 "numbers by picking a distribution with its share first.",),
        also="Any distributions of one value mix, the plain-named SciPy ones too. " + TOLD,
    ),
    Entry(
        word="sdata.distribution",
        option='"from values"',
        ours="""
            gears = sdata.distribution("from values", values=[3, 4, 5], chances=[0.5, 0.3, 0.2])
            gears.find_average()
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("from values", values=[3, 4, 5], chances=[0.5, 0.3, 0.2])
            stats.rv_discrete(values=([3, 4, 5], [0.5, 0.3, 0.2])).mean()   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the values sorted, each with its chance; the chances must add up to 1.",),
        also=TOLD,
    ),
    Entry(
        word="sdata.distribution",
        option='"histogram"',
        ours="""
            bins = sdata.distribution("histogram", counts=[3, 9, 4], bin_edges=[0, 1, 2, 3])
            bins.find_percentile(50)
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("histogram", counts=[3, 9, 4], bin_edges=[0, 1, 2, 3])
            stats.rv_histogram(([3, 9, 4], [0, 1, 2, 3]), density=False).ppf(0.5)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the values spread evenly within each bin; of=numbers with bins= counts the numbers first "
                 "(NumPy histogram).",),
        also=TOLD,
    ),
    Entry(
        word="dist.take_function",
        ours="""
            distribution = sdata.distribution("normal", average=1, standard_deviation=0.5)
            grown = distribution.take_function("exp")
            grown.find_chance_that_value(is_below=2)
        """,
        code={"SciPy": """
            from scipy import stats
            # take_function("exp")
            grown = stats.exp(stats.Normal(mu=1, sigma=0.5))         # (1)
            grown.cdf(2)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the change of variables (here exp of a normal is a lognormal); \"log\", \"absolute value\" and "
                 "\"order statistic\" are the others.",),
        also="The new distribution answers every distribution word. " + TOLD,
    ),
    Entry(
        word="dist.take_function",
        option='"order statistic"',
        ours="""
            distribution = sdata.distribution("normal", average=1, standard_deviation=0.5)
            second = distribution.take_function("order statistic", rank=2, out_of=5)
            second.find_chance_that_value(is_below=1)
        """,
        code={"SciPy": """
            from scipy import stats
            # take_function("order statistic", rank=2, out_of=5)
            second = stats.order_statistic(stats.Normal(mu=1, sigma=0.5), r=2, n=5)   # (1)
            second.cdf(1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("rank=1 is the smallest of out_of= values drawn (SciPy r= and n=).",),
        also=TOLD,
    ),
    Entry(
        word="sdata.find_parameter_that_gives",
        ours="""
            sdata.find_parameter_that_gives("t", chance_below=0.975, at_value=2.1)
        """,
        code={"SciPy": """
            from scipy import special
            # find_parameter_that_gives("t", chance_below=0.975, at_value=2.1)
            special.stdtridf(0.975, 2.1)                          # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the one parameter left out is found with scipy.special's inverse function for it (stdtridf, "
                 "bdtri, nrdtrisd ...); for counts chance_below= means fewer than at_value.",),
        also=TOLD,
    ),
]
