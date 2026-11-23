# How we check simplydata

simplydata does no statistics of its own: every word calls an established package (pandas, Polars,
NumPy, SciPy, statsmodels, matplotlib, seaborn, or R through rpy2). So the question is whether each word
calls it the right way, with the right settings. This folder answers that question in public, so anyone
can rerun it.

**The report:** [report.md](report.md), with every check, what it was compared with, the tolerance, and
whether it passed, plus the system, Python, package and R versions it was run with.

## Rerun it

From a copy of the repository (`pip install -e ".[test]"` first; add `".[test,r]"` and R for the R parts):

```
python validation/make_report.py                       # writes validation/report.md
python validation/make_report.py --check               # checks only: exit code 1 if any check fails
                                                       # (the report goes to the temporary folder, or --out)
python validation/make_report.py --check --require-r   # and a skipped R part counts as a failure
```

Where R, rpy2 or an R package is missing, the R parts are skipped and the report says so. CI runs the
report on every setup with `SIMPLYDATA_REQUIRE_R=1`, so there a missing R fails instead. The test suite
runs the same checks (`tests/test_underneath.py`, `tests/test_validation.py`) on Windows, macOS and Linux
with Python 3.11 to 3.13 for every change.

## What is checked

1. **Real data with published answers** (`cases.py`). Each word runs on real data, and what it gives is
   compared with
   - the **published answer**: certified values from the NIST Statistical Reference Datasets, or the
     numbers printed in the paper (allowing for their printed rounding);
   - the **parent package** called directly, at a tight tolerance;
   - **R**, as an independent second calculation, where R is installed.

   NIST certified values are compared by the log relative error (LRE): the number of significant digits
   that agree. A word must match at least 9 digits; for the nonlinear (curve) problems, at least 6, the
   level at which statistical software is judged on them (McCullough 1999).
   In these cases, made-up data are used only for edge cases that no real dataset tests (empty cells, no
   rows left, an exact line): 3 of the 374 cases, each labelled *made-up* in the report.

   Each check states its tolerance and why: about 1e-9 (relative) for a calculation with no iteration and
   no random numbers; the NIST digits above, or the same method run to convergence, for an iterative fit;
   and for Monte Carlo answers either the same seed (then they must agree exactly) or, against another
   random number generator or an exact limit, 4 Monte Carlo standard errors, worked out for that check
   (the tolerance "4 mcse"). A number that falls a little short of its tolerance for a stated reason that is
   a limit of precision (for example the NIST Wampler polynomials, below) is listed as an *explained
   difference*, with its reason, and counted apart from the passes and the failures.

2. **The same underneath** (`src/simplydata/_underneath/`). For 218 of simplydata's 400 words (326
   entries, counting the options that change what a word calls), the manual shows the same job written in
   the package underneath. Each of those boxes is run next to the word and compared: numbers to a stated
   tolerance, tables by values and column order (on a pandas and on a Polars table), and charts by their
   data (bars, dots, lines, labels, limits), never by pixels. These checks show that a word makes the call
   it says it makes; they are not checks against an independent answer, and 272 of the 326 run on made-up
   practice tables (all practice tables are made up; 54 need no table). The report counts them together with the cases of
   part 1, so its total number of checks mixes both kinds.

3. **Choices simplydata makes.** Where simplydata's default differs from the package underneath (for
   example Welch's t-test where SciPy's `ttest_ind` assumes equal spreads, or 10 histogram bins), the report lists it, so a difference is never hidden.

The study now has 374 cases on 94 datasets (82 with a published or certified answer, 289 compared with the
parent package and R, 3 made-up edge cases). The "datasets" include published sources that hold no data (power
manuals, design tables): 6 of the 289 are simulation and formula checks against R that use no data at all; the
other 283 run on real data. A word passes when it agrees with the reference to the stated, justified tolerance. They cover 207 words, or 332 words and options;
the other words of simplydata's 398 are not checked on real data here (some have a same-underneath box,
part 2, and all have their own tests). Words are added with each release; a word counts as done only when
its checks pass.

An option that changes what a word calls underneath is checked on its own, with its own box and case:
`table.explain` with `weights=`, `outcome="yes or no (overdispersed)"`, `matched_by=`, `show="risk ratios"`,
`method="log-binomial"`, `giving_outliers_less_weight=`, `with_knots=`, `show="standardised effects"`,
`interval_by="bootstrap"`, `interval_by="profile"`, `p_value_by="likelihood ratio"`, `crossed_with=`,
`outcome="counts with many zeros that vary a lot"`, `outcome="counts in two steps"` and `zero_part_using=`
(S3a-1), and its Nagelkerke and Tjur pseudo R squared. The hurdle and zero-inflated models reproduce the
published estimates of Zeileis, Kleiber & Jackman (2008) on the NMES 1988 data.

## Datasets

`data/` holds only the NIST files (public domain) and small tables of published facts typed from a paper or
copied from a help-page example (Bliss's beetles, rat liver glycogen, Quetelet's chest sizes, rounding first base,
smokers, dry cat food and FLUTD, Down syndrome by birth order) and the Orobanche seeds (from the MIT-licensed R package
agridat). The bioequivalence reference datasets of Schütz et al. (2014) are not stored either: simplydata was tested on
them, and the cases read a local copy named by `SIMPLYDATA_SCHUTZ2014_FILE` (DATA_LICENSES.md). Tables that come from GPL or LGPL R packages are not stored: `r_data.py` reads them from the
installed R package (nothing is downloaded), so those cases need R and are skipped without it. Which licence covers
which table is in [DATA_LICENSES.md](../DATA_LICENSES.md).

| dataset | file | source | licence |
|---|---|---|---|
| NIST StRD Norris (straight line, 36 points) | `data/nist/Norris.dat` | Norris, J., NIST. Calibration of Ozone Monitors. NIST Statistical Reference Datasets, Linear Regression. https://www.itl.nist.gov/div898/strd/lls/data/Norris.shtml | Public domain in the US (US Government work, 17 U.S.C. 105); stored with its numbers unchanged |
| NIST StRD Michelso (Michelson's speed of light, 100 values) | `data/nist/Michelso.dat` | Dorsey, E. N. (1944). The Velocity of Light. Transactions of the American Philosophical Society 34(1), 1-110, Table 22. NIST StRD, Univariate Summary Statistics. https://www.itl.nist.gov/div898/strd/univ/michelso.html | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Mavro (filter transmittance, 50 values) | `data/nist/Mavro.dat` | Mavrodineanu, R., NIST. NIST StRD, Univariate Summary Statistics. https://www.itl.nist.gov/div898/strd/univ/mavro.html | Public domain in the US; stored with its numbers unchanged |
| NIST StRD NumAcc4 (1001 constructed values) | `data/nist/NumAcc4.dat` | Simon, S. D. & Lesage, J. P. (1989). Assessing the accuracy of ANOVA calculations in statistical software. Computational Statistics & Data Analysis 8, 325-332. NIST StRD. https://www.itl.nist.gov/div898/strd/univ/numacc4.html | Public domain in the US; stored with its numbers unchanged |
| Student's sleep data | not stored | Cushny, A. R. & Peebles, A. R. (1905). The action of optical isomers. II. Hyoscines. Journal of Physiology 32, 501-510; analysed by Student (1908). The probable error of a mean. Biometrika 6(1), 1-25. Copy from R's `datasets::sleep` | Public domain (published 1905 and 1908); R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| Anscombe's quartet | not stored | Anscombe, F. J. (1973). Graphs in statistical analysis. The American Statistician 27(1), 17-21. Copy from R's `datasets::anscombe` | The published numbers, as in R's datasets package (GPL-2 \| GPL-3); read from the installed package (`r_data.py`), so it needs R |
| Galton's sweet peas | not stored | Galton, F. (1877). Typical laws of heredity. Nature 15, 492-495, 512-514, 532-533; weighted least squares in Weisberg, S. (2014). Applied Linear Regression, 4th ed., section 7.1. Copy from the R package alr4 (`galtonpeas`) | Published 1877 (public domain); the alr4 copy is GPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| Orobanche seeds | `data/crowder_seeds.csv` | Crowder, M. J. (1978). Beta-binomial anova for proportions. Applied Statistics 27(1), 34-37. Copy from the R package agridat (`crowder.seeds`), through Rdatasets | The published counts (facts from a 1978 paper); the agridat copy is MIT licensed |
| infert | not stored | Trichopoulos, D. et al. (1976). Induced abortion and secondary infertility. British Journal of Obstetrics and Gynaecology 83, 645-650. Copy from R's `datasets::infert` | Published 1976; R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| birthwt | not stored | Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Copy from the R package MASS (`birthwt`) | The MASS copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| stackloss | not stored | Brownlee, K. A. (1965). Statistical Theory and Methodology in Science and Engineering, 2nd ed. Wiley. Copy from R's `datasets::stackloss` | Published 1960/1965; R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| mtcars | not stored | Henderson, H. V. & Velleman, P. F. (1981). Building multiple regression models interactively. Biometrics 37, 391-411 (data from Motor Trend, 1974). Copy from R's `datasets::mtcars` | Published 1974 and 1981; R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| VerbAgg | not stored | De Boeck, P. & Wilson, M. (2004). Explanatory Item Response Models. Springer. Copy from the R package lme4 (`VerbAgg`) | The lme4 copy is GPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| NMES 1988 (7 of 19 columns) | not stored | Deb, P. & Trivedi, P. K. (1997). Journal of Applied Econometrics 12, 313-336; analysed in Zeileis, A., Kleiber, C. & Jackman, S. (2008). Regression models for count data in R. Journal of Statistical Software 27(8). Copy from the R package AER (`NMES1988`), through Rdatasets | A US Government survey (public domain); the AER copy is GPL-2 \| GPL-3; the JSS article is CC BY; read from the installed package (`r_data.py`), so it needs R |
| swiss (S3a-3) | not stored | Mosteller, F. & Tukey, J. W. (1977). Data Analysis and Regression. Addison-Wesley. Copy from R's `datasets::swiss` | Official 1888 statistics (public domain); R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| iris (S3a-3) | not stored | Anderson, E. (1935). Bulletin of the American Iris Society 59, 2-5; Fisher, R. A. (1936). Annals of Eugenics 7, 179-188. Copy from R's `datasets::iris` | Public domain (1935); R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| warpbreaks (S3a-3) | not stored | Tippett, L. H. C. (1950). Technological Applications of Statistics. Wiley. Copy from R's `datasets::warpbreaks` | Published facts (1950); R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| Lake Huron (S3a-3) | not stored | Brockwell, P. J. & Davis, R. A. (1991). Time Series and Forecasting Methods, 2nd ed. Springer. Copy from R's `datasets::LakeHuron` | US Government measurements (public domain); R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| rat liver glycogen (S3a-3) | `data/rat_glycogen.csv` | Sokal, R. R. & Rohlf, F. J. (1981). Biometry, 2nd ed. Freeman, Box 10.1 (also Crawley, M. J. (2007). The R Book, chapter 11) | 36 published numbers typed from the book (facts, not covered by copyright) |
| Dialyzer, sleepstudy, birthwt (S3a-3) | not stored | Vonesh & Carter (1992), Pinheiro & Bates (2000), shipped with R nlme; Belenky et al. (2003), Bates et al. (2015) JSS 67(1), shipped with R lme4; Hosmer & Lemeshow (1989), shipped with R MASS | GPL (the R packages); read from the installed packages, so they need R |
| lung (S3b-3) | not stored | Loprinzi, C. L. et al. (1994). Journal of Clinical Oncology 12, 601-607 (NCCTG lung cancer). Copy from R's survival package (`lung`) | Published trial data; the survival copy is LGPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| veteran (S3b-3) | not stored | Kalbfleisch, J. D. & Prentice, R. L. (2002). The Statistical Analysis of Failure Time Data, 2nd ed. Wiley. Copy from R's survival package (`veteran`) | Published trial data; LGPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| Stanford heart transplant (S3b-3) | not stored | Crowley, J. & Hu, M. (1977). JASA 72, 27-36; Therneau & Grambsch (2000), Modeling Survival Data, section 3.7. Copy from R's survival package (`heart`) | Published data; LGPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| mgus2 (S3b-3) | not stored | Kyle, R. A. et al. (2002). NEJM 346, 564-569; Therneau, "Multi-state models and competing risks" (survival vignette). Copy from R's survival package (`mgus2`), first event of each patient | Published data; LGPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| bfeed, Channing House, larynx; udca (S3b-3) | not stored | Klein & Moeschberger (2003), Survival Analysis, 2nd ed. (KMsurv); Hyde (1980); Kardaun (1983); Lindor, K. D. et al. (1994), Gastroenterology 106, 1284-1290 (survival's `udca`) | GPL-3 (KMsurv), LGPL (survival); read from the installed packages, so they need R |
| BCG trials, passive smoking, Normand 1999, Curtis 1998, Hart 1999, McDaniel 1994 (S3b-1) | not stored | Colditz, G. A. et al. (1994). JAMA 271, 698-702, analysed in Viechtbauer, W. (2010). Journal of Statistical Software 36(3) (CC BY); Hackshaw, A. K., Law, M. R. & Wald, N. J. (1997). BMJ 315, 980-988; Normand, S.-L. T. (1999). Statistics in Medicine 18, 321-359; Curtis, P. S. & Wang, X. (1998). Oecologia 113, 299-313; Hart, R. G. et al. (1999). Annals of Internal Medicine 131, 492-501; McDaniel, M. A. et al. (1994). Journal of Applied Psychology 79, 599-616. All shipped with the R package metadat | GPL (>= 2) (metadat); read from the installed package, so they need R |
| Holzinger & Swineford 1939, nine ability tests (S3c-2) | not in `data/`; the same scores ship as the practice table `ability_tests` | Holzinger, K. J. & Swineford, F. (1939). A study in factor analysis: the stability of a bi-factor solution. Supplementary Educational Monographs 48, University of Chicago; the three-factor model and its fit in Rosseel, Y. (2012). Journal of Statistical Software 48(2) (CC BY). Shipped with the R package lavaan (HolzingerSwineford1939) | Published test scores (1939, facts), stored with their citation as a practice table; the cases read lavaan's copy (GPL (>= 2)), so they need R |
| Worked examples for planning a study (S3b-2) | no data | Faul, F. et al. G*Power 3.1 manual, sections 13.3.1 and 29.4 (Cohen 1988, example 9.1); StataCorp, [PSS-2] power logrank (examples 1, 2, 5) and power twomeans, cluster (example 1, from Ahn, Heo & Zhang 2015); Haynes, A. G. et al. (2021). Journal of Open Source Software 6(60), 3118 (presize); the pwr vignette (Kutner et al., exercise 8.43); Bland, J. M., Sample size in guidelines trials (University of York) | Published numbers (facts); only the printed answers are quoted |
| dune, varespec and varechem, BCI, mite (S3c-1) | not stored | Jongman, R. H., ter Braak, C. J. F. & van Tongeren, O. F. R. (1995). Data Analysis in Community and Landscape Ecology. Cambridge University Press; Väre, H., Ohtonen, R. & Oksanen, J. (1995). Journal of Vegetation Science 6, 523-530; Condit, R. et al. (2002). Science 295, 666-669; Borcard, D. & Legendre, P. (1994). Environmental and Ecological Statistics 1, 37-61. All shipped with the R package vegan | GPL-2 (vegan); read from the installed package, so they need R |
| crabs (S3c-1) | not stored | Campbell, N. A. & Mahon, R. J. (1974). Australian Journal of Zoology 22, 417-425; Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed., section 12.1. Shipped with the R package MASS | GPL-2 \| GPL-3 (MASS, which comes with R); read from the installed package, so it needs R |
| wg93 (S3c-1) | not stored | Greenacre, M. (2007). Correspondence Analysis in Practice, 2nd ed. Chapman & Hall/CRC; Nenadić, O. & Greenacre, M. (2007). Journal of Statistical Software 20(3) (CC BY). Shipped with the R package ca | GPL (>= 2) (ca); read from the installed package, so it needs R |
| turtles, ICU arrivals (S3c-3) | not stored | Luschi, P. et al. (2001). Behavioral Ecology and Sociobiology 50, 528-534; Cox, D. R. & Lewis, P. A. W. (1966). The Statistical Analysis of Series of Events, pp. 254-255, as data set B.1 of Fisher, N. I. (1993). Statistical Analysis of Circular Data. Both shipped with the R package circular | GPL-2 (circular); read from the installed package, so they need R |
| meuse (S3c-3) | not stored | Rikken, M. G. J. & Van Rijn, R. P. G. (1993). Soil pollution with heavy metals (Utrecht University); the gstat vignette (Pebesma, E. J. (2004). Computers & Geosciences 30, 683-691). Shipped with the R package sp | GPL-2 \| GPL-3 (sp); read from the installed package, so it needs R |
| Port Pirie, daily rain (S3c-3) | not stored | Coles, S. (2001). An Introduction to Statistical Modeling of Extreme Values. Springer, sections 3.4.1 and 4.4.1. Shipped with the R package ismev (the Port Pirie numbers are also the practice table `sea_levels`) | GPL (>= 2) (ismev); read from the installed package, so they need R |
| Hedenfalk's genes (S3c-4) | not stored | Hedenfalk, I. et al. (2001). New England Journal of Medicine 344, 539-548; the p-values of Storey, J. D. & Tibshirani, R. (2003). PNAS 100, 9440-9445. Shipped with the R package qvalue (Bioconductor) | LGPL (qvalue); read from the installed package, so it needs R |
| Quetelet's chest sizes (S3c-4) | `data/chest_sizes.csv` | Quetelet, A. (1846). Lettres sur la theorie des probabilites. Hayez, Brussels; Stigler, S. M. (1986). The History of Statistics. The same counts as R HistData's ChestSizes | Published 1846 (facts); stored with its numbers unchanged |
| AirPassengers (S3c-4) | not stored | Box, G. E. P. & Jenkins, G. M. (1976). Time Series Analysis: Forecasting and Control, series G. Copy from R's `datasets::AirPassengers` | Published 1976 (facts); R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| rounding first base (S3c-4) | `data/rounding_first_base.csv` | Hollander, M. & Wolfe, D. A. (1973). Nonparametric Statistical Methods. Wiley, p. 140; the example of R's `friedman.test` help | Published 1973 (facts); stored with its numbers unchanged |
| smokers (S3c-4) | `data/smokers.csv` | Fleiss, J. L. (1981). Statistical Methods for Rates and Proportions, 2nd ed., p. 139; the example of R's `prop.test` help | Published 1981 (facts); stored with its numbers unchanged |
| lalonde (S3d-2) | not stored | LaLonde, R. J. (1986). American Economic Review 76, 604-620; Dehejia, R. H. & Wahba, S. (1999). Journal of the American Statistical Association 94, 1053-1062. The copy in the R package MatchIt (lalonde) | Public study data (US Department of Labor NSW); MatchIt's copy is GPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| JOBS II (S3d-2) | not stored | Vinokur, A. D., Price, R. H. & Schul, Y. (1995). American Journal of Community Psychology 23, 39-74; Tingley, D. et al. (2014). Journal of Statistical Software 59(5). The copy in the R package mediation (jobs), 6 of its columns | Human-subject records distributed by ICPSR (study 2739), whose terms do not allow passing them on; GPL (>= 2) in mediation. Read from the installed mediation package, so it needs R. The practice table `job_search` is made up, with the same columns |
| dry cat food and FLUTD (S3d-2) | `data/flutd.csv` | Willeberg, P. (1977). Acta Veterinaria Scandinavica 18 (Suppl. 64); the first example of R `epiR::epi.2by2` | Published counts (facts); stored unchanged |
| Down syndrome by birth order (S3d-2) | `data/down_syndrome.csv` | Selvin, S. (2004). Statistical Analysis of Epidemiologic Data, 3rd ed.; the example of R `epitools::ageadjust.direct` | Published counts (facts); stored unchanged |
| bioequivalence reference datasets A, B, C (S3d-2) | not stored | Schütz, H., Labes, D. & Fuglsang, A. (2014). The AAPS Journal 16, 1292-1297, supplementary data sets A (Sauter et al. 1992), B (Clayton & Leslie 1981) and C (PMC4389751) | (c) AAPS 2014, no open licence, so not shipped. simplydata was tested on them on 2026-11-21: the three ratios and 90 % intervals equal Table II at its 2 printed decimals of percent, and R lm() to 1e-9. The cases read a local copy named by `SIMPLYDATA_SCHUTZ2014_FILE` and are skipped without it (DATA_LICENSES.md) |
| airquality, lung (S3d-2) | not stored | Chambers, J. M. et al. (1983). Graphical Methods for Data Analysis (R datasets airquality); Loprinzi, C. L. et al. (1994). Journal of Clinical Oncology 12, 601-607 (R survival lung) | GPL-2 \| GPL-3 (R datasets), LGPL (survival); read from R, so they need R |
| api stratified sample (S3d-1) | not stored | California Department of Education, Academic Performance Index 2000; the stratified sample of R's survey package (apistrat; Lumley, T. (2010). Complex Surveys. Wiley) | Public data; the survey copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| api cluster sample (S3d-1) | not stored | The one-stage cluster sample of R's survey package (apiclus1; Lumley 2010) | Public data; the survey copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| nhanes (S3d-1) | not stored | Schafer, J. L. (1997). Analysis of Incomplete Multivariate Data, p. 237; R mice (nhanes); van Buuren, S. & Groothuis-Oudshoorn, K. (2011). Journal of Statistical Software 45(3) | US Government survey (public domain); the mice copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| professional challenges (S3d-1) | not stored | Heiberger, R. M. & Robbins, N. B. (2014). Journal of Statistical Software 57(5); R HH (ProfChal) | JSS article CC BY; the HH copy is GPL (>= 2); read from the installed package (`r_data.py`), so it needs R |
| aSAH | not stored | Turck, N. et al. (2010). Intensive Care Medicine 36, 107-115; shipped with the R package pROC (Robin, X. et al. (2011). BMC Bioinformatics 12, 77) | GPL-3 or later (pROC); read from the installed pROC package, so it needs R |
| NIST StRD Rat42 (logistic growth, 9 points) | `data/nist/Rat42.dat` | Ratkowsky, D. A. (1983). Nonlinear Regression Modeling. NIST StRD, Nonlinear Regression. https://www.itl.nist.gov/div898/strd/nls/data/ratkowsky2.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Misra1a (rise to a limit, 14 points) | `data/nist/Misra1a.dat` | Misra, D., NIST (1978). Dental research monomolecular adsorption study. NIST StRD, Nonlinear Regression. https://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD BoxBOD (rise to a limit, 6 points) | `data/nist/BoxBOD.dat` | Box, G. P., Hunter, W. G. & Hunter, J. S. (1978). Statistics for Experimenters, pp. 483-487. NIST StRD, Nonlinear Regression. https://www.itl.nist.gov/div898/strd/nls/data/boxbod.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Filip (polynomial of degree 10, 82 points) | `data/nist/Filip.dat` | Filippelli, A., NIST. NIST StRD, Linear Regression (higher difficulty). https://www.itl.nist.gov/div898/strd/lls/data/Filip.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Longley (16 years, 6 predictors) | `data/nist/Longley.dat` | Longley, J. W. (1967). An appraisal of least squares programs for the electronic computer from the viewpoint of the user. JASA 62, 819-841. NIST StRD, Linear Regression (higher difficulty). https://www.itl.nist.gov/div898/strd/lls/data/Longley.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Wampler1 to Wampler5 (polynomials of degree 5, 21 points) | `data/nist/Wampler1.dat`, `data/nist/Wampler2.dat`, `data/nist/Wampler3.dat`, `data/nist/Wampler4.dat`, `data/nist/Wampler5.dat` | Wampler, R. H. (1970). A report on the accuracy of some widely used least squares computer programs. JASA 65, 549-565. NIST StRD, Linear Regression (higher difficulty). https://www.itl.nist.gov/div898/strd/lls/data/Wampler1.shtml | Public domain in the US; stored with their numbers unchanged. Where fit_curve falls short of 9 digits (about 8.9 on Wampler1, 3 and 4 and 8.0 on Wampler5, whose noise is far larger than its curve, on Windows; the digits vary with the computer's linear-algebra library, down to 8.4 on Wampler1 and 7.1 on Wampler5 on GitHub's runners) the report lists the number as an explained difference: turning the fit on x mapped to [-1, 1] back into raw powers adds rounding of about 1e-9, a limit of double precision; no existing least-squares routine tested (LAPACK gelsd, gelsy, gelss; NumPy QR; NumPy Polynomial.fit) does better on all of them without losing Filip |
| NIST StRD Roszman1 (formula with arctan, 25 points) | `data/nist/Roszman1.dat` | Roszman, L., NIST. Quantum Defects for Sulfur I Atom. NIST StRD, Nonlinear Regression (average difficulty). https://www.itl.nist.gov/div898/strd/nls/data/roszman1.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD Thurber (rational function, 37 points) | `data/nist/Thurber.dat` | Thurber, R., NIST. Semiconductor electron mobility modeling. NIST StRD, Nonlinear Regression (higher difficulty). https://www.itl.nist.gov/div898/strd/nls/data/thurber.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD MGH09 (rational function, 11 points) | `data/nist/MGH09.dat` | Kowalik, J. S. & Osborne, M. R. (1978). Methods for Unconstrained Optimization Problems; More, J. J., Garbow, B. S. & Hillstrom, K. E. (1981). ACM Transactions on Mathematical Software 7(1), 17-41. NIST StRD, Nonlinear Regression (higher difficulty). https://www.itl.nist.gov/div898/strd/nls/data/mgh09.shtml | Public domain in the US; stored with its numbers unchanged |
| NIST StRD ENSO (monthly pressure differences, 168 points) | `data/nist/ENSO.dat` | Kahaner, D., Moler, C. & Nash, S. (1989). Numerical Methods and Software. NIST StRD, Nonlinear Regression (average difficulty). https://www.itl.nist.gov/div898/strd/nls/data/enso.shtml | Public domain in the US; stored with its numbers unchanged |
| Bliss's beetles (8 doses) | `data/bliss.csv` | Bliss, C. I. (1935). The calculation of the dosage-mortality curve. Annals of Applied Biology 22, 134-167; fit printed in Dobson & Barnett (2008), An Introduction to Generalized Linear Models, 3rd ed. | Facts published in 1935, typed from the paper |
| Puromycin, treated (12 rows) | not stored | Treloar, M. A. (1974), M.Sc. thesis, University of Toronto; fit printed in Bates, D. M. & Watts, D. G. (1988). Nonlinear Regression Analysis and Its Applications. Copy from R's `datasets::Puromycin` | Published facts; R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| Seatbelts (UK drivers killed or seriously injured, monthly 1969-1984) | not stored | Harvey, A. C. & Durbin, J. (1986). Journal of the Royal Statistical Society A 149, 187-227. Copy from R's `datasets::Seatbelts` | Official counts published in the paper; R's copy is GPL-2 \| GPL-3; read from the installed package (`r_data.py`), so it needs R |
| ryegrass | not stored | Inderjit et al. (2002), Physiologia Plantarum 114, 422-428; Ritz, C. et al. (2015). Dose-response analysis using R. PLoS ONE 10, e0146021; shipped with R's drc | Article CC BY 4.0; data GPL-2 (drc); read from drc, so it needs R |
| poisons | not stored | Box, G. E. P. & Cox, D. R. (1964). An analysis of transformations. JRSS B 26, 211-252; shipped with R's boot | Published facts; read from boot, so it needs R |
| stagnant | not stored | Bacon, D. W. & Watts, D. G. (1971). Biometrika 58, 525-534; shipped with R's segmented | Published facts; read from segmented (GPL), so it needs R |
| leaflife | not stored | Wright, I. J., Westoby, M. & Reich, P. B. (2002). Journal of Ecology 90, 534-543; shipped with R's smatr | GPL-2 (smatr); read from smatr, so it needs R |
| creatinine | not stored | The method-comparison example of R's mcr (Roche Diagnostics) | GPL-3 (mcr); read from mcr, so it needs R |
| Engel food expenditure | not stored | Engel, E. (1857); Koenker, R. & Bassett, G. (1982). Econometrica 50, 43-61; copy in statsmodels | Public domain (1857); read from statsmodels |
| Standard normal table | not stored | NIST/SEMATECH e-Handbook of Statistical Methods, 1.3.6.7.1. https://www.itl.nist.gov/div898/handbook/eda/section3/eda3671.htm | Public domain in the US; one number quoted |

The same list, with what each dataset holds, is at the end of the report.

## Files

- `make_report.py`: builds the report (one command, above).
- `cases.py`: the cases on real data, the datasets with their licences and citations, and the edge cases.
- `cases_lines.py`: the same for the lines and curves of phase S3a-2 (loaded by `cases.py`).
- `r_data.py`: the tables read from installed R packages instead of stored copies.
- `data/`: the stored datasets (public domain or published facts; see DATA_LICENSES.md).
- `report.md`: the last report made and committed.
