"""Families for 100 %, batches 7-9 (plan section 2.3, approved by Manish 2026-11-28): the maths family of NumPy and
scipy.special. numbers.take_function (one name table, _maths_functions.py), numbers.work_on_bits (NumPy's bit
words), turn_into_yes_or_no(is_=) (NumPy's is* words), sdata.find_zeros_of (scipy.special *_zeros) and
sdata.find_area_points (scipy.special roots_*, scipy.integrate newton_cotes and lebedev_rule).
"""

from . import Entry

ENTRIES = [
    Entry(
        word="nums.take_function",
        ours="""
            numbers = sdata.number_list([-1.5, 0.0, 0.5, 2.0])
            numbers.take_function("bessel J", order=1)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import special
            values = np.array([-1.5, 0.0, 0.5, 2.0])
            # take_function("bessel J", order=1)
            special.jv(1, values)                # (1)
        """},
        compare="value",
        tolerance=1e-15,
        choices=("the plain name comes from one name table: \"bessel J\" is special.jv, and \"jv\" works too; the "
                 "numbers go where SciPy's x goes, the other inputs are options with plain names (order=).",),
        also="Where the function has no value the answer is empty and a note says how many (erfinv of 2 is NaN in "
             "SciPy too); a grid or block keeps its shape; undo() takes the step back. The same names work inside "
             "formula text (bessel_j(1, x)).",
    ),
    Entry(
        word="nums.take_function", option="part=",
        ours="""
            numbers = sdata.number_list([0.5, 1.0, 2.0])
            numbers.take_function("hankel H1", order=1, part="imaginary")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import special
            values = np.array([0.5, 1.0, 2.0])
            # take_function("hankel H1", order=1, part="imaginary")
            np.imag(special.hankel1(1, values))   # (1)
        """},
        compare="value",
        tolerance=1e-15,
        choices=("simplydata numbers are real numbers: a complex answer gives its real part unless part= asks for "
                 "\"imaginary\", \"size\" (np.abs) or \"angle\" (np.angle), and the sentence says so.",),
    ),
    Entry(
        word="nums.work_on_bits",
        ours="""
            numbers = sdata.number_list([12, 10, 7, 3])
            numbers.work_on_bits("and", with_numbers=6)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 10, 7, 3])
            # work_on_bits("and", with_numbers=6)
            np.bitwise_and(values, 6)
        """},
        compare="value",
        tolerance=0.0,
        also="Decimals and empty numbers stop with a plain sentence (NumPy refuses them too). \"only one\" is "
             "bitwise_xor, \"flip\" invert, \"count ones\" bitwise_count; \"pack into bytes\" and \"unpack bytes\" "
             "are packbits and unpackbits along the last direction.",
    ),
    Entry(
        word="nums.work_on_bits", option="by=",
        ours="""
            numbers = sdata.number_list([12, 10, 7, 3])
            numbers.work_on_bits("shift left", by=2)
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([12, 10, 7, 3])
            # work_on_bits("shift left", by=2)
            np.left_shift(values, 2)
        """},
        compare="value",
        tolerance=0.0,
    ),
    Entry(
        word="nums.turn_into_yes_or_no", option="is_=",
        ours="""
            numbers = sdata.number_list([1.0, float("inf"), float("-inf"), None, 5.0])
            numbers.turn_into_yes_or_no(is_="finite")
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([1.0, np.inf, -np.inf, np.nan, 5.0])
            # turn_into_yes_or_no(is_="finite")
            np.isfinite(values)
        """},
        compare="value",
        tolerance=0.0,
        also="\"infinite\" is np.isinf, \"minus infinity\" np.isneginf, \"plus infinity\" np.isposinf; \"real\", "
             "\"complex\" and \"not a time\" are always yes, no and no for simplydata numbers, which are real "
             "numbers and hold no dates.",
    ),
    Entry(
        word="sdata.find_zeros_of",
        ours="""
            sdata.find_zeros_of("bessel J", order=0, how_many=5)
        """,
        code={"SciPy": """
            from scipy import special
            # find_zeros_of("bessel J", order=0, how_many=5)
            special.jn_zeros(0, 5)
        """},
        compare="value",
        tolerance=0.0,
        also="The zeros of the error function and the Fresnel integrals are complex numbers: they come back as a "
             "table of real and imaginary parts (special.erf_zeros, fresnels_zeros, fresnelc_zeros).",
    ),
    Entry(
        word="sdata.find_area_points",
        ours="""
            points = sdata.find_area_points("legendre", how_many=5)
            points.get_column("weight")
        """,
        code={"SciPy": """
            from scipy import special
            # find_area_points("legendre", how_many=5)
            points, weights = special.roots_legendre(5)
            weights
        """},
        compare="value",
        tolerance=0.0,
        also="A table with a point and a weight column, so that formula words work on it: "
             "points.add_column(\"value\", \"weight * exp(point)\") then find_total_of(\"value\") is the area.",
    ),
]
