"""How each Python package asks to be cited: the reference the package itself gives.

Every entry is copied from the package's own request, never made up (checked 2026-11-20):
  pandas       https://pandas.pydata.org/about/citing.html (McKinney 2010 and the Zenodo record)
  NumPy        CITATION.bib in github.com/numpy/numpy (Harris et al. 2020)
  SciPy        CITATION.bib in github.com/scipy/scipy (Virtanen et al. 2020)
  statsmodels  "Citation" on https://www.statsmodels.org (Seabold and Perktold 2010)
  matplotlib   https://matplotlib.org/stable/project/citing.html (Hunter 2007)
  seaborn      https://seaborn.pydata.org/citing.html (Waskom 2021)
  lifelines    https://lifelines.readthedocs.io, "Citing lifelines" (Davidson-Pilon 2019)
  Polars       the DOI badge of github.com/pola-rs/polars (Zenodo, "DOI Latest Release")
  scikit-learn https://scikit-learn.org/stable/about.html, "Citing scikit-learn" (Pedregosa et al. 2011)
  control      README of github.com/python-control/python-control (Fuller et al. 2021)
A package that is not here (narwhals, rpy2, pyarrow ... ask for no paper) is listed with its name,
version and home page from its installed metadata (importlib.metadata), never with a made-up reference.

Each entry: the import name -> (shown name, distribution name on PyPI, one-line reference, full reference,
BibTeX).
"""

from __future__ import annotations

CITATIONS = {
    "pandas": (
        "pandas", "pandas",
        "McKinney (2010), Proc. 9th Python in Science Conf., 56-61; and The pandas development team, "
        "doi:10.5281/zenodo.3509134",
        "McKinney, W. (2010). Data Structures for Statistical Computing in Python. Proceedings of the 9th Python in "
        "Science Conference, 56-61. doi:10.25080/Majora-92bf1922-00a. "
        "The pandas development team. pandas-dev/pandas: Pandas. Zenodo. doi:10.5281/zenodo.3509134.",
        """@software{reback2020pandas,
  author = {The pandas development team},
  title = {pandas-dev/pandas: Pandas},
  publisher = {Zenodo},
  year = {2020},
  doi = {10.5281/zenodo.3509134},
  url = {https://doi.org/10.5281/zenodo.3509134}
}

@inproceedings{mckinney-proc-scipy-2010,
  author = {Wes McKinney},
  title = {Data Structures for Statistical Computing in Python},
  booktitle = {Proceedings of the 9th Python in Science Conference},
  pages = {56--61},
  year = {2010},
  editor = {St{\\'e}fan van der Walt and Jarrod Millman},
  doi = {10.25080/Majora-92bf1922-00a}
}""",
    ),
    "numpy": (
        "NumPy", "numpy",
        "Harris et al. (2020), Array programming with NumPy, Nature 585, 357-362, doi:10.1038/s41586-020-2649-2",
        "Harris, C. R., Millman, K. J., van der Walt, S. J. et al. (2020). Array programming with NumPy. Nature, "
        "585, 357-362. doi:10.1038/s41586-020-2649-2.",
        """@article{2020NumPy-Array,
  author = {Harris, Charles R. and Millman, K. Jarrod and van der Walt, St{\\'e}fan J. and Gommers, Ralf and
            Virtanen, Pauli and Cournapeau, David and Wieser, Eric and Taylor, Julian and Berg, Sebastian and
            Smith, Nathaniel J. and Kern, Robert and Picus, Matti and Hoyer, Stephan and van Kerkwijk, Marten H. and
            Brett, Matthew and Haldane, Allan and Fern{\\'a}ndez del R{\\'i}o, Jaime and Wiebe, Mark and
            Peterson, Pearu and G{\\'e}rard-Marchant, Pierre and Sheppard, Kevin and Reddy, Tyler and
            Weckesser, Warren and Abbasi, Hameer and Gohlke, Christoph and Oliphant, Travis E.},
  title = {Array programming with {NumPy}},
  journal = {Nature},
  year = {2020},
  volume = {585},
  pages = {357--362},
  doi = {10.1038/s41586-020-2649-2}
}""",
    ),
    "scipy": (
        "SciPy", "scipy",
        "Virtanen et al. (2020), SciPy 1.0, Nature Methods 17, 261-272, doi:10.1038/s41592-019-0686-2",
        "Virtanen, P., Gommers, R., Oliphant, T. E. et al. (2020). SciPy 1.0: Fundamental Algorithms for Scientific "
        "Computing in Python. Nature Methods, 17, 261-272. doi:10.1038/s41592-019-0686-2.",
        """@article{2020SciPy-NMeth,
  author = {Virtanen, Pauli and Gommers, Ralf and Oliphant, Travis E. and Haberland, Matt and Reddy, Tyler and
            Cournapeau, David and Burovski, Evgeni and Peterson, Pearu and Weckesser, Warren and Bright, Jonathan and
            {van der Walt}, St{\\'e}fan J. and Brett, Matthew and Wilson, Joshua and Millman, K. Jarrod and
            Mayorov, Nikolay and Nelson, Andrew R. J. and Jones, Eric and Kern, Robert and Larson, Eric and
            Carey, C J and Polat, {\\.I}lhan and Feng, Yu and Moore, Eric W. and {VanderPlas}, Jake and
            Laxalde, Denis and Perktold, Josef and Cimrman, Robert and Henriksen, Ian and Quintero, E. A. and
            Harris, Charles R. and Archibald, Anne M. and Ribeiro, Ant{\\^o}nio H. and Pedregosa, Fabian and
            {van Mulbregt}, Paul and {SciPy 1.0 Contributors}},
  title = {{SciPy} 1.0: Fundamental Algorithms for Scientific Computing in Python},
  journal = {Nature Methods},
  year = {2020},
  volume = {17},
  pages = {261--272},
  doi = {10.1038/s41592-019-0686-2}
}""",
    ),
    "statsmodels": (
        "statsmodels", "statsmodels",
        "Seabold and Perktold (2010), statsmodels, Proc. 9th Python in Science Conf.",
        "Seabold, S., and Perktold, J. (2010). statsmodels: Econometric and statistical modeling with python. "
        "Proceedings of the 9th Python in Science Conference.",
        """@inproceedings{seabold2010statsmodels,
  title = {statsmodels: Econometric and statistical modeling with python},
  author = {Seabold, Skipper and Perktold, Josef},
  booktitle = {9th Python in Science Conference},
  year = {2010}
}""",
    ),
    "matplotlib": (
        "matplotlib", "matplotlib",
        "Hunter (2007), Matplotlib: A 2D graphics environment, Comput. Sci. Eng. 9(3), 90-95, "
        "doi:10.1109/MCSE.2007.55",
        "Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment. Computing in Science & Engineering, 9(3), "
        "90-95. doi:10.1109/MCSE.2007.55.",
        """@article{Hunter:2007,
  author = {Hunter, J. D.},
  title = {Matplotlib: A 2D graphics environment},
  journal = {Computing in Science \\& Engineering},
  volume = {9},
  number = {3},
  pages = {90--95},
  publisher = {IEEE COMPUTER SOC},
  doi = {10.1109/MCSE.2007.55},
  year = {2007}
}""",
    ),
    "seaborn": (
        "seaborn", "seaborn",
        "Waskom (2021), seaborn: statistical data visualization, JOSS 6(60), 3021, doi:10.21105/joss.03021",
        "Waskom, M. L. (2021). seaborn: statistical data visualization. Journal of Open Source Software, 6(60), "
        "3021. doi:10.21105/joss.03021.",
        """@article{Waskom2021,
  author = {Michael L. Waskom},
  title = {seaborn: statistical data visualization},
  journal = {Journal of Open Source Software},
  year = {2021},
  volume = {6},
  number = {60},
  pages = {3021},
  publisher = {The Open Journal},
  doi = {10.21105/joss.03021},
  url = {https://doi.org/10.21105/joss.03021}
}""",
    ),
    "lifelines": (
        "lifelines", "lifelines",
        "Davidson-Pilon (2019), lifelines: survival analysis in Python, JOSS 4(40), 1317, doi:10.21105/joss.01317",
        "Davidson-Pilon, C. (2019). lifelines: survival analysis in Python. Journal of Open Source Software, 4(40), "
        "1317. doi:10.21105/joss.01317.",
        """@article{Davidson-Pilon2019,
  author = {Cameron Davidson-Pilon},
  title = {lifelines: survival analysis in Python},
  journal = {Journal of Open Source Software},
  year = {2019},
  volume = {4},
  number = {40},
  pages = {1317},
  doi = {10.21105/joss.01317}
}""",
    ),
    "polars": (
        "Polars", "polars",
        "Vink et al., pola-rs/polars, Zenodo, doi:10.5281/zenodo.7697217",
        "Vink, R. et al. pola-rs/polars. Zenodo. doi:10.5281/zenodo.7697217.",
        """@software{polars,
  author = {Ritchie Vink and others},
  title = {pola-rs/polars},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.7697217},
  url = {https://doi.org/10.5281/zenodo.7697217}
}""",
    ),
    "sklearn": (
        "scikit-learn", "scikit-learn",
        "Pedregosa et al. (2011), Scikit-learn: Machine Learning in Python, JMLR 12, 2825-2830",
        "Pedregosa, F., Varoquaux, G., Gramfort, A. et al. (2011). Scikit-learn: Machine Learning in Python. "
        "Journal of Machine Learning Research, 12, 2825-2830.",
        """@article{scikit-learn,
  title = {Scikit-learn: Machine Learning in {P}ython},
  author = {Pedregosa, F. and Varoquaux, G. and Gramfort, A. and Michel, V. and Thirion, B. and Grisel, O. and
            Blondel, M. and Prettenhofer, P. and Weiss, R. and Dubourg, V. and Vanderplas, J. and Passos, A. and
            Cournapeau, D. and Brucher, M. and Perrot, M. and Duchesnay, E.},
  journal = {Journal of Machine Learning Research},
  volume = {12},
  pages = {2825--2830},
  year = {2011}
}""",
    ),
    "control": (
        "python-control", "control",
        "Fuller et al. (2021), The Python Control Systems Library (python-control), 60th IEEE CDC, 4875-4881",
        "Fuller, S., Greiner, B., Moore, J., Murray, R., van Paassen, R., and Yorke, R. (2021). The Python Control "
        "Systems Library (python-control). 60th IEEE Conference on Decision and Control (CDC), 4875-4881.",
        """@inproceedings{python-control2021,
  title = {The Python Control Systems Library (python-control)},
  author = {Sawyer Fuller and Ben Greiner and Jason Moore and Richard Murray and Ren{\\'e} van Paassen and
            Rory Yorke},
  booktitle = {60th IEEE Conference on Decision and Control (CDC)},
  pages = {4875--4881},
  year = {2021},
  organization = {IEEE}
}""",
    ),
}

# Packages that are used but ask for no paper: their import name -> (shown name, distribution name)
NAMES = {"narwhals": ("narwhals", "narwhals"), "rpy2": ("rpy2", "rpy2"), "pyarrow": ("pyarrow", "pyarrow"),
         "openpyxl": ("openpyxl", "openpyxl"), "patsy": ("patsy", "patsy"), "pyreadstat": ("pyreadstat", "pyreadstat"),
         "docx": ("python-docx", "python-docx")}
