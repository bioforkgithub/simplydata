"""The reliability study for the families for 100 % plan, batches 5-6 (approved by Manish 2026-11-28): the SciPy
distributions by their plain names, the joint (multivariate) names, "mixture", "from values", "histogram",
distribution.take_function and sdata.find_parameter_that_gives (plan section 2.2), each set up from real data and
compared with SciPy and, where base R does the same in a few lines, with R.

cases_underneath.py loads this file and adds the cases. The data are the study's mtcars (R datasets): the parameters
of each distribution come from the cars (their groups, counts, averages and spreads), so each case asks a question
about them. The simplydata side reads its results only with simplydata words.
"""

from __future__ import annotations

import textwrap

MPG_BY_GEARBOX = """
    import numpy as np
    auto, manual = data.loc[data["am"] == 0, "mpg"], data.loc[data["am"] == 1, "mpg"]
    m0, s0, m1, s1 = auto.mean(), auto.std(), manual.mean(), manual.std()
    log_mpg = np.log(data["mpg"])
"""


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts if part and part.strip())


def cases(Case):
    return [
        Case("sdata.distribution", "mtcars: Tukey's critical value for comparing the 3 cylinder groups (studentized "
             "range, 3 groups, 29 degrees of freedom)", "mtcars", "real data", option='"studentized range"',
             ours="""
                 k = data["cyl"].nunique(); df = len(data) - k
                 d = sdata.distribution("studentized range", groups=k, degrees_of_freedom=df)
                 {"q 95": d.find_percentile(95)}
             """,
             parent="""
                 from scipy import stats
                 k = data["cyl"].nunique(); df = len(data) - k
                 {"q 95": stats.studentized_range(k, df).ppf(0.95)}
             """, parent_label="SciPy stats.studentized_range", parent_tolerance=1e-9,
             r="""
                 k <- length(unique(cyl)); list(`q 95` = qtukey(0.95, k, length(cyl) - k))
             """, r_tolerance=1e-6,
             note="SciPy and R integrate the studentized range numerically; they agree to about 7 digits."),
        Case("sdata.distribution", "mtcars: the density of a bell-shaped pair (fuel use, weight) at a light, thrifty "
             "car, with the cars' own averages and covariance", "mtcars", "real data", option='"multivariate normal"',
             ours="""
                 pair = data[["mpg", "wt"]]
                 d = sdata.distribution("multivariate normal", averages=pair.mean().tolist(),
                                        covariance=pair.cov().to_numpy().tolist())
                 {"density": d.find_density_at([30, 2])}
             """,
             parent="""
                 from scipy import stats
                 pair = data[["mpg", "wt"]]
                 {"density": stats.multivariate_normal(pair.mean(), pair.cov()).pdf([30, 2])}
             """, parent_label="SciPy stats.multivariate_normal",
             r="""
                 x <- cbind(mpg, wt); S <- cov(x); d <- c(30, 2) - colMeans(x)
                 list(density = exp(-0.5 * sum(d * solve(S, d))) / (2 * pi * sqrt(det(S))))
             """, r_tolerance=1e-10),
        Case("sdata.distribution", "mtcars: the chance of exactly the counts of 3, 4 and 5 gears if each were "
             "equally likely (multinomial)", "mtcars", "real data", option='"multinomial"',
             ours="""
                 counts = data["gear"].value_counts().sort_index().tolist()
                 d = sdata.distribution("multinomial", tries=len(data), chances=[1 / 3] * 3)
                 {"chance": d.find_density_at(counts)}
             """,
             parent="""
                 from scipy import stats
                 counts = data["gear"].value_counts().sort_index().tolist()
                 {"chance": stats.multinomial(len(data), [1 / 3] * 3).pmf(counts)}
             """, parent_label="SciPy stats.multinomial",
             r="""
                 list(chance = dmultinom(as.numeric(table(gear)), prob = rep(1 / 3, 3)))
             """, r_tolerance=1e-12),
        Case("sdata.distribution", "mtcars: the Wishart density of the sum of squares of (fuel use, weight) with "
             "31 degrees of freedom and the cars' own covariance", "mtcars", "real data", option='"wishart"',
             ours="""
                 import math
                 S = data[["mpg", "wt"]].cov().to_numpy()
                 d = sdata.distribution("wishart", degrees_of_freedom=31, scale=S.tolist())
                 {"log density": math.log(d.find_density_at((31 * S).tolist()))}
             """,
             parent="""
                 from scipy import stats
                 S = data[["mpg", "wt"]].cov().to_numpy()
                 {"log density": stats.wishart(df=31, scale=S).logpdf(31 * S)}
             """, parent_label="SciPy stats.wishart", parent_tolerance=1e-10,
             r="""
                 S <- cov(cbind(mpg, wt)); X <- 31 * S; n <- 31; p <- 2
                 lg <- p * (p - 1) / 4 * log(pi) + sum(lgamma((n + 1 - 1:p) / 2))
                 ld <- (n - p - 1) / 2 * log(det(X)) - sum(diag(solve(S, X))) / 2 - n * p / 2 * log(2) -
                       n / 2 * log(det(S)) - lg
                 list(`log density` = ld)
             """, r_tolerance=1e-10),
        Case("sdata.distribution", "mtcars: the chance of a car below 20 mpg from a mixture of the automatic and "
             "manual cars' bell curves", "mtcars", "real data", option='"mixture"',
             ours=_code(MPG_BY_GEARBOX, """
                 first = sdata.distribution("normal", average=m0, standard_deviation=s0)
                 second = sdata.distribution("normal", average=m1, standard_deviation=s1)
                 mixed = sdata.distribution("mixture", of=[first, second],
                                            shares=[len(auto) / len(data), len(manual) / len(data)])
                 {"chance below 20": mixed.find_chance_that_value(is_below=20)}
             """),
             parent=_code(MPG_BY_GEARBOX, """
                 from scipy import stats
                 parts = [stats.Normal(mu=m0, sigma=s0), stats.Normal(mu=m1, sigma=s1)]
                 X = stats.Mixture(parts, weights=[len(auto) / len(data), len(manual) / len(data)])
                 {"chance below 20": X.cdf(20)}
             """), parent_label="SciPy stats.Mixture",
             r="""
                 a <- mpg[am == 0]; m <- mpg[am == 1]
                 list(`chance below 20` = length(a) / 32 * pnorm(20, mean(a), sd(a)) +
                                          length(m) / 32 * pnorm(20, mean(m), sd(m)))
             """, r_tolerance=1e-12),
        Case("sdata.distribution", "mtcars: the average number of gears, from the share of cars with each",
             "mtcars", "real data", option='"from values"',
             ours="""
                 shares = data["gear"].value_counts(normalize=True).sort_index()
                 d = sdata.distribution("from values", values=shares.index.tolist(), chances=shares.tolist())
                 {"average": d.find_average(), "chance of 4 or fewer": d.find_chance_that_value(is_at_most=4)}
             """,
             parent="""
                 from scipy import stats
                 shares = data["gear"].value_counts(normalize=True).sort_index()
                 d = stats.rv_discrete(values=(shares.index.to_numpy(), shares.to_numpy()))
                 {"average": d.mean(), "chance of 4 or fewer": d.cdf(4)}
             """, parent_label="SciPy stats.rv_discrete",
             r="""
                 s <- prop.table(table(gear)); v <- as.numeric(names(s))
                 list(average = sum(v * s), `chance of 4 or fewer` = sum(s[v <= 4]))
             """, r_tolerance=1e-12),
        Case("sdata.distribution", "mtcars: the median fuel use of the histogram of the cars in bins of 5 mpg",
             "mtcars", "real data", option='"histogram"',
             ours="""
                 import numpy as np
                 counts, edges = np.histogram(data["mpg"], bins=np.arange(10, 40, 5))
                 d = sdata.distribution("histogram", counts=counts.tolist(), bin_edges=edges.tolist())
                 {"median": d.find_percentile(50)}
             """,
             parent="""
                 import numpy as np
                 from scipy import stats
                 h = np.histogram(data["mpg"], bins=np.arange(10, 40, 5))
                 {"median": stats.rv_histogram(h, density=False).ppf(0.5)}
             """, parent_label="SciPy stats.rv_histogram",
             r="""
                 h <- hist(mpg, breaks = seq(10, 35, 5), right = FALSE, plot = FALSE)
                 cum <- c(0, cumsum(h$counts)) / sum(h$counts); i <- findInterval(0.5, cum)
                 list(median = h$breaks[i] + (0.5 - cum[i]) / (cum[i + 1] - cum[i]) * 5)
             """, r_tolerance=1e-12,
             note="The median of a histogram is found by straight lines within the bin that holds the middle."),
        Case("dist.take_function", "mtcars: the chance of a car below 20 mpg when the log of fuel use is "
             "bell-shaped (exp of a normal)", "mtcars", "real data",
             ours=_code(MPG_BY_GEARBOX, """
                 logs = sdata.distribution("normal", average=log_mpg.mean(), standard_deviation=log_mpg.std())
                 {"chance below 20": logs.take_function("exp").find_chance_that_value(is_below=20)}
             """),
             parent=_code(MPG_BY_GEARBOX, """
                 from scipy import stats
                 {"chance below 20": stats.exp(stats.Normal(mu=log_mpg.mean(), sigma=log_mpg.std())).cdf(20)}
             """), parent_label="SciPy stats.exp",
             r="""
                 list(`chance below 20` = plnorm(20, mean(log(mpg)), sd(log(mpg))))
             """, r_tolerance=1e-12),
        Case("dist.take_function", "mtcars: the chance that the thirstiest of 32 cars drawn from a bell curve of "
             "the cars' fuel use is below the lowest seen (10.4 mpg)", "mtcars", "real data",
             option='"order statistic"',
             ours="""
                 d = sdata.distribution("normal", average=data["mpg"].mean(), standard_deviation=data["mpg"].std())
                 lowest = d.take_function("order statistic", rank=1, out_of=32)
                 {"chance": lowest.find_chance_that_value(is_below=10.4)}
             """,
             parent="""
                 from scipy import stats
                 X = stats.Normal(mu=data["mpg"].mean(), sigma=data["mpg"].std())
                 {"chance": stats.order_statistic(X, r=1, n=32).cdf(10.4)}
             """, parent_label="SciPy stats.order_statistic",
             r="""
                 list(chance = 1 - (1 - pnorm(10.4, mean(mpg), sd(mpg)))^32)
             """, r_tolerance=1e-10),
        Case("sdata.find_parameter_that_gives", "mtcars: the spread that would put 90 % of cars below 30 mpg, at "
             "the cars' average fuel use", "mtcars", "real data",
             ours="""
                 {"standard deviation": sdata.find_parameter_that_gives("normal", chance_below=0.9, at_value=30,
                                                                        average=data["mpg"].mean())}
             """,
             parent="""
                 from scipy import special
                 {"standard deviation": special.nrdtrisd(data["mpg"].mean(), 0.9, 30)}
             """, parent_label="SciPy special.nrdtrisd",
             r="""
                 list(`standard deviation` = (30 - mean(mpg)) / qnorm(0.9))
             """, r_tolerance=1e-9),
    ]
