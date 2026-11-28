"""Families for 100 %, batch 13 (G5, approved by Manish 2026-11-28): sdata.polynomial, each name next to the same
polynomial in scipy.special or numpy.polynomial. SymPy makes the polynomial exactly; the comparison is of its values."""

from . import Entry

FORMULA = ("simplydata also gives the polynomial exactly, as a formula, so every formula word works on it "
           "(find_slope_formula, find_area_formula, turn_into_product, show_as_latex ...).")

ENTRIES = [
    Entry(
        word="sdata.polynomial",
        ours="""
            formula = sdata.polynomial("legendre", degree=3)
            formula.find_value_at(x=0.5)
        """,
        code={"SciPy": """
            from scipy import special
            # polynomial("legendre", degree=3), at x = 0.5
            special.eval_legendre(3, 0.5)
        """, "NumPy": """
            import numpy as np
            # polynomial("legendre", degree=3), at x = 0.5
            np.polynomial.Legendre.basis(3)(0.5)
        """},
        compare="value",
        tolerance=1e-12,
        also=FORMULA,
    ),
    Entry(
        word="sdata.polynomial", option='"chebyshev"',
        ours="""
            formula = sdata.polynomial("chebyshev", degree=5)
            formula.find_value_at(x=0.3)
        """,
        code={"SciPy": """
            from scipy import special
            # polynomial("chebyshev", degree=5), at x = 0.3
            special.chebyt(5)(0.3)
        """, "NumPy": """
            import numpy as np
            # polynomial("chebyshev", degree=5), at x = 0.3
            np.polynomial.Chebyshev.basis(5)(0.3)
        """},
        compare="value",
        tolerance=1e-12,
        also=FORMULA,
    ),
    Entry(
        word="sdata.polynomial", option='"probabilists hermite"',
        ours="""
            formula = sdata.polynomial("probabilists hermite", degree=4)
            formula.find_value_at(x=1.5)
        """,
        code={"SciPy": """
            from scipy import special
            # polynomial("probabilists hermite", degree=4), at x = 1.5
            special.eval_hermitenorm(4, 1.5)
        """, "NumPy": """
            import numpy as np
            # polynomial("probabilists hermite", degree=4), at x = 1.5
            np.polynomial.HermiteE.basis(4)(1.5)
        """},
        compare="value",
        tolerance=1e-12,
        also=FORMULA,
    ),
    Entry(
        word="sdata.polynomial", option='"jacobi"',
        ours="""
            formula = sdata.polynomial("jacobi", degree=3, alpha=1, beta=2)
            formula.find_value_at(x=0.4)
        """,
        code={"SciPy": """
            from scipy import special
            # polynomial("jacobi", degree=3, alpha=1, beta=2), at x = 0.4
            special.eval_jacobi(3, 1, 2, 0.4)
        """},
        compare="value",
        tolerance=1e-12,
        also=FORMULA,
    ),
    Entry(
        word="sdata.polynomial", option='"from roots"',
        ours="""
            formula = sdata.polynomial("from roots", roots=[1, 2, 3])
            formula.find_value_at(x=[0, 4])
        """,
        code={"NumPy": """
            import numpy as np
            # polynomial("from roots", roots=[1, 2, 3]), at x = 0 and 4
            np.polyval(np.poly([1, 2, 3]), [0, 4])
        """},
        compare="value",
        tolerance=1e-12,
        also=FORMULA,
    ),
    Entry(
        word="sdata.polynomial", option='"through points"',
        ours="""
            formula = sdata.polynomial("through points", x=[0, 1, 2, 4], y=[1, 3, 7, 2])
            formula.find_value_at(x=3)
        """,
        code={"SciPy": """
            from scipy import interpolate
            # polynomial("through points", x=[0, 1, 2, 4], y=[1, 3, 7, 2]), at x = 3
            interpolate.BarycentricInterpolator([0, 1, 2, 4], [1, 3, 7, 2])(3)
        """},
        compare="value",
        tolerance=1e-10,
        also="SymPy interpolating_poly gives the polynomial with exact fractions. " + FORMULA,
    ),
]
