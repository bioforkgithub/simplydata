"""Families for 100 %, batches 7-9 (plan section 2.3): the maths family against published tables.

cases_underneath.py loads this file and adds cases(Case) to the study. The functions of scipy.special have printed
values in the NIST Digital Library of Mathematical Functions (DLMF, https://dlmf.nist.gov) and in Abramowitz and
Stegun's Handbook of Mathematical Functions (1964, National Bureau of Standards Applied Mathematics Series 55; the
tables DLMF replaced). Each case checks numbers.take_function, a formula name, sdata.find_zeros_of or
sdata.find_area_points against those printed values, against SciPy (or NumPy) called directly, and against base R
where R has the function (besselJ, besselY, besselI, besselK, gamma, digamma, beta, choose). The values are quoted
to the digits printed, with the absolute tolerance of the last printed digit.
"""

from __future__ import annotations

import math
import textwrap

DATASET = "published special-function tables (no data)"
DLMF = "NIST DLMF"
AS = "Abramowitz & Stegun (1964)"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def cases(Case):
    def table(word, title, ours, published, parent, label, r="", option="", tolerance=1e-14, r_tolerance=1e-12):
        return Case(word, title, DATASET, "published", ours=_code(ours), published=published, parent=_code(parent),
                    parent_label=label, parent_tolerance=tolerance, r=_code(r), r_tolerance=r_tolerance,
                    option=option)

    def mtcars(word, title, ours, parent, label, r, option=""):
        return Case(word, title, "mtcars", "real data", ours=_code(ours), parent=_code(parent), parent_label=label,
                    parent_tolerance=0.0, r=_code(r), r_tolerance=0.0, option=option)

    return [
        table("nums.take_function", "part=: Hankel H1 of order 0 at 1 is J0(1) + i Y0(1) (A&S Table 9.1)",
              """
                  real = sdata.number_list([1.0]).take_function("hankel H1", order=0).as_numpy()[0]
                  imaginary = sdata.number_list([1.0]).take_function("hankel H1", order=0, part="imaginary")
                  {"real part": real, "imaginary part": imaginary.as_numpy()[0]}
              """,
              {"real part": (0.765197686557967, 1e-15, f"{AS}, Table 9.1 (J0)"),
               "imaginary part": (0.088256964215677, 1e-15, f"{AS}, Table 9.1 (Y0)")},
              """
                  from scipy import special
                  h = special.hankel1(0, 1.0)
                  {"real part": h.real, "imaginary part": h.imag}
              """, "SciPy special.hankel1",
              r="""
                  list(`real part` = besselJ(1, 0), `imaginary part` = besselY(1, 0))
              """, option="part="),
        mtcars("nums.work_on_bits", "the low 4 bits of the horsepower of 32 cars (bitwise and with 15)",
               """
                   hp = sdata.number_list(data["hp"].tolist())
                   hp.work_on_bits("and", with_numbers=15)
                   {"total": float(hp.find_total()), "first": float(hp.get_number_at(1))}
               """,
               """
                   low = np.bitwise_and(data["hp"].to_numpy(), 15)
                   {"total": float(low.sum()), "first": float(low[0])}
               """, "NumPy bitwise_and",
               """
                   low <- bitwAnd(as.integer(hp), 15L)
                   list(total = sum(low), first = low[1])
               """),
        mtcars("nums.work_on_bits", "by=: the horsepower of 32 cars shifted 2 bits left (times 4)",
               """
                   hp = sdata.number_list(data["hp"].tolist())
                   hp.work_on_bits("shift left", by=2)
                   {"total": float(hp.find_total()), "biggest": float(hp.find_biggest())}
               """,
               """
                   moved = np.left_shift(data["hp"].to_numpy(), 2)
                   {"total": float(moved.sum()), "biggest": float(moved.max())}
               """, "NumPy left_shift",
               """
                   moved <- bitwShiftL(as.integer(hp), 2L)
                   list(total = sum(moved), biggest = max(moved))
               """, option="by="),
        mtcars("nums.turn_into_yes_or_no", 'is_="finite": quarter-mile time per manual gear flag (0 for automatic '
                                           "cars, so no finite answer)",
               """
                   q = sdata.number_list(data["qsec"].tolist())
                   q.divide_by(sdata.number_list(data["am"].tolist()))
                   finite = q.turn_into_yes_or_no(is_="finite")
                   {"finite": float(finite.count_numbers_that(is_equal_to=True))}
               """,
               """
                   with np.errstate(divide="ignore"):
                       q = data["qsec"].to_numpy() / data["am"].to_numpy()
                   {"finite": float(np.isfinite(q).sum())}
               """, "NumPy isfinite",
               """
                   list(finite = sum(is.finite(qsec / am)))
               """, option="is_="),
        table("nums.take_function", "Bessel J0 and J1 at 1 and 2 (A&S Table 9.1, DLMF 10.2)",
              """
                  j0 = sdata.number_list([1.0, 2.0]).take_function("bessel J", order=0).as_numpy()
                  j1 = sdata.number_list([1.0, 2.0]).take_function("bessel J1").as_numpy()
                  {"J0(1)": j0[0], "J0(2)": j0[1], "J1(1)": j1[0], "J1(2)": j1[1]}
              """,
              {"J0(1)": (0.765197686557967, 1e-15, f"{AS}, Table 9.1"),
               "J0(2)": (0.223890779141236, 1e-15, f"{AS}, Table 9.1"),
               "J1(1)": (0.440050585744934, 1e-15, f"{AS}, Table 9.1"),
               "J1(2)": (0.576724807756873, 1e-15, f"{AS}, Table 9.1")},
              """
                  from scipy import special
                  {"J0(1)": special.jv(0, 1.0), "J0(2)": special.jv(0, 2.0), "J1(1)": special.j1(1.0),
                   "J1(2)": special.j1(2.0)}
              """, "SciPy special.jv and special.j1",
              r="""
                  list(`J0(1)` = besselJ(1, 0), `J0(2)` = besselJ(2, 0),
                       `J1(1)` = besselJ(1, 1), `J1(2)` = besselJ(2, 1))
              """),
        table("nums.take_function", "Bessel Y0, I0 and K0 at 1 (A&S Tables 9.1 and 9.8)",
              """
                  x = sdata.number_list([1.0])
                  {"Y0(1)": x.take_function("bessel Y0").as_numpy()[0],
                   "I0(1)": sdata.number_list([1.0]).take_function("bessel I", order=0).as_numpy()[0],
                   "K0(1)": sdata.number_list([1.0]).take_function("bessel K0").as_numpy()[0]}
              """,
              {"Y0(1)": (0.088256964215677, 1e-15, f"{AS}, Table 9.1"),
               "I0(1)": (1.266065877752008, 1e-15, f"{AS}, Table 9.8"),
               "K0(1)": (0.421024438240708, 1e-15, f"{AS}, Table 9.8")},
              """
                  from scipy import special
                  {"Y0(1)": special.y0(1.0), "I0(1)": special.iv(0, 1.0), "K0(1)": special.k0(1.0)}
              """, "SciPy special.y0, iv and k0",
              r="""
                  list(`Y0(1)` = besselY(1, 0), `I0(1)` = besselI(1, 0), `K0(1)` = besselK(1, 0))
              """),
        table("nums.take_function", "Airy Ai(0), Ai'(0) and Bi(0) (DLMF 9.2.3 to 9.2.5)",
              """
                  zero = [0.0]
                  {"Ai(0)": sdata.number_list(zero).take_function("airy Ai").as_numpy()[0],
                   "Ai'(0)": sdata.number_list(zero).take_function("airy Ai slope").as_numpy()[0],
                   "Bi(0)": sdata.number_list(zero).take_function("airy Bi").as_numpy()[0]}
              """,
              {"Ai(0)": (1 / (3 ** (2 / 3) * math.gamma(2 / 3)), 1e-15, f"{DLMF} 9.2.3"),
               "Ai'(0)": (-1 / (3 ** (1 / 3) * math.gamma(1 / 3)), 1e-15, f"{DLMF} 9.2.4"),
               "Bi(0)": (1 / (3 ** (1 / 6) * math.gamma(2 / 3)), 1e-15, f"{DLMF} 9.2.5")},
              """
                  from scipy import special
                  ai, aip, bi, bip = special.airy(0.0)
                  {"Ai(0)": ai, "Ai'(0)": aip, "Bi(0)": bi}
              """, "SciPy special.airy"),
        table("nums.take_function", "the error function, its inverse and Dawson's integral (A&S Tables 7.1 and 7.5)",
              """
                  {"erf(0.5)": sdata.number_list([0.5]).take_function("error function").as_numpy()[0],
                   "erfinv(0.5)": sdata.number_list([0.5]).take_function("erfinv").as_numpy()[0],
                   "F(1)": sdata.number_list([1.0]).take_function("dawson integral").as_numpy()[0]}
              """,
              {"erf(0.5)": (0.520499877813047, 1e-15, f"{AS}, Table 7.1"),
               "F(1)": (0.538079506912768, 1e-15, f"{AS}, Table 7.5")},
              """
                  from scipy import special
                  {"erf(0.5)": special.erf(0.5), "erfinv(0.5)": special.erfinv(0.5), "F(1)": special.dawsn(1.0)}
              """, "SciPy special.erf, erfinv and dawsn",
              r="""
                  list(`erf(0.5)` = 2 * pnorm(0.5 * sqrt(2)) - 1, `erfinv(0.5)` = qnorm((0.5 + 1) / 2) / sqrt(2))
              """),
        table("nums.take_function", "the complete elliptic integrals K and E at m = 1/2 (A&S Table 17.1)",
              """
                  {"K(1/2)": sdata.number_list([0.5]).take_function("ellipk").as_numpy()[0],
                   "E(1/2)": sdata.number_list([0.5]).take_function("ellipe").as_numpy()[0]}
              """,
              {"K(1/2)": (1.854074677301372, 1e-15, f"{AS}, Table 17.1 (modular angle 45 degrees)"),
               "E(1/2)": (1.350643881047676, 1e-15, f"{AS}, Table 17.1 (modular angle 45 degrees)")},
              """
                  from scipy import special
                  {"K(1/2)": special.ellipk(0.5), "E(1/2)": special.ellipe(0.5)}
              """, "SciPy special.ellipk and ellipe"),
        table("nums.take_function", "the sine, cosine and exponential integrals at 1 (A&S Table 5.1)",
              """
                  one = [1.0]
                  {"Si(1)": sdata.number_list(one).take_function("sine integral").as_numpy()[0],
                   "Ci(1)": sdata.number_list(one).take_function("cosine integral").as_numpy()[0],
                   "E1(1)": sdata.number_list(one).take_function("exp1").as_numpy()[0]}
              """,
              {"Si(1)": (0.946083070367183, 1e-15, f"{AS}, Table 5.1"),
               "Ci(1)": (0.337403922900968, 1e-15, f"{AS}, Table 5.1"),
               "E1(1)": (0.219383934395520, 1e-15, f"{AS}, Table 5.1")},
              """
                  from scipy import special
                  si, ci = special.sici(1.0)
                  {"Si(1)": si, "Ci(1)": ci, "E1(1)": special.exp1(1.0)}
              """, "SciPy special.sici and exp1"),
        table("nums.take_function", "Apery's constant zeta(3) and the omega constant W(1) (DLMF 25.6, 4.13)",
              """
                  {"zeta(3)": sdata.number_list([3.0]).take_function("zeta").as_numpy()[0],
                   "W(1)": sdata.number_list([1.0]).take_function("lambert W").as_numpy()[0]}
              """,
              {"zeta(3)": (1.202056903159594, 1e-15, f"{DLMF} 25.6 (Apery's constant)"),
               "W(1)": (0.567143290409784, 1e-15, f"{DLMF} 4.13 (the omega constant)")},
              """
                  from scipy import special
                  {"zeta(3)": special.zeta(3.0), "W(1)": special.lambertw(1.0).real}
              """, "SciPy special.zeta and lambertw"),
        table("nums.take_function", "digamma(1) is minus Euler's constant, and Gamma(1/2) is the root of pi (DLMF 5.4)",
              """
                  {"digamma(1)": sdata.number_list([1.0]).take_function("digamma").as_numpy()[0],
                   "gamma(1/2)": sdata.number_list([0.5]).take_function("gamma").as_numpy()[0]}
              """,
              {"digamma(1)": (-0.577215664901533, 1e-15, f"{DLMF} 5.4.12"),
               "gamma(1/2)": (math.sqrt(math.pi), 1e-15, f"{DLMF} 5.4.6")},
              """
                  from scipy import special
                  {"digamma(1)": special.digamma(1.0), "gamma(1/2)": special.gamma(0.5)}
              """, "SciPy special.digamma and gamma",
              r="""
                  list(`digamma(1)` = digamma(1), `gamma(1/2)` = gamma(0.5))
              """),
        table("nums.take_function", "a formula name in add_column: bessel_j(0, x) at the first zero is 0",
              """
                  t = sdata.table({"x": [2.404825557695773, 1.0]})
                  t.add_column("j", "bessel_j(0, x)")
                  {"at the first zero": t.get_column("j").as_numpy()[0], "at 1": t.get_column("j").as_numpy()[1]}
              """,
              {"at the first zero": (0.0, 1e-15, f"{DLMF} Table 10.21.1"),
               "at 1": (0.765197686557967, 1e-15, f"{AS}, Table 9.1")},
              """
                  from scipy import special
                  {"at the first zero": special.jv(0, 2.404825557695773), "at 1": special.jv(0, 1.0)}
              """, "SciPy special.jv"),
        table("sdata.find_zeros_of", "the first zeros of J0 and J1 (DLMF Table 10.21.1, A&S Table 9.5)",
              """
                  j0 = sdata.find_zeros_of("bessel J", order=0, how_many=3).as_numpy()
                  j1 = sdata.find_zeros_of("bessel J", order=1, how_many=1).as_numpy()
                  {"j0,1": j0[0], "j0,2": j0[1], "j0,3": j0[2], "j1,1": j1[0]}
              """,
              {"j0,1": (2.404825557695773, 1e-15, f"{AS}, Table 9.5"),
               "j0,2": (5.520078110286311, 1e-15, f"{AS}, Table 9.5"),
               "j0,3": (8.653727912911012, 1e-15, f"{AS}, Table 9.5"),
               "j1,1": (3.831705970207512, 1e-15, f"{AS}, Table 9.5")},
              """
                  from scipy import special
                  j0 = special.jn_zeros(0, 3)
                  {"j0,1": j0[0], "j0,2": j0[1], "j0,3": j0[2], "j1,1": special.jn_zeros(1, 1)[0]}
              """, "SciPy special.jn_zeros", tolerance=1e-13),
        table("sdata.find_zeros_of", "the first zeros of Airy Ai (DLMF Table 9.9.1)",
              """
                  a = sdata.find_zeros_of("airy Ai", how_many=2).as_numpy()
                  {"a1": a[0], "a2": a[1]}
              """,
              {"a1": (-2.338107410459767, 1e-15, f"{DLMF} Table 9.9.1"),
               "a2": (-4.087949444130970, 1e-15, f"{DLMF} Table 9.9.1")},
              """
                  from scipy import special
                  a = special.ai_zeros(2)[0]
                  {"a1": a[0], "a2": a[1]}
              """, "SciPy special.ai_zeros", tolerance=1e-13),
        table("sdata.find_area_points", "Gauss-Legendre with 3 points: 0 and the root of 3/5, weights 8/9 and 5/9 "
                                        "(A&S Table 25.4)",
              """
                  p = sdata.find_area_points("legendre", how_many=3).as_pandas()
                  {"outer point": float(p["point"].iloc[2]), "middle weight": float(p["weight"].iloc[1]),
                   "outer weight": float(p["weight"].iloc[2]),
                   "area of x**4": float((p["weight"] * p["point"] ** 4).sum())}
              """,
              {"outer point": (math.sqrt(3 / 5), 1e-15, f"{AS}, Table 25.4"),
               "middle weight": (8 / 9, 1e-15, f"{AS}, Table 25.4"),
               "outer weight": (5 / 9, 1e-15, f"{AS}, Table 25.4"),
               "area of x**4": (2 / 5, 1e-15, "exact: the area under x**4 from -1 to 1")},
              """
                  from scipy import special
                  x, w = special.roots_legendre(3)
                  {"outer point": x[2], "middle weight": w[1], "outer weight": w[2], "area of x**4": (w * x**4).sum()}
              """, "SciPy special.roots_legendre"),
    ]
