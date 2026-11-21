"""How simplydata chooses methods: every default with its published basis.

simplydata often chooses a method, an option value or a setting for the user: Welch's t-test for two
averages, Holm's method for many p-values, REML and Hartung-Knapp intervals for a meta-analysis. BASIS
holds, for each such choice, what simplydata chooses, what else you can ask for (and the option that
asks for it), why (the principle and the published evidence), the references, and what simplydata checks
in your data before it uses the method.

BASIS is keyed like simplydata._underneath.UNDERNEATH: the word's key in simplydata.learn
("table.compare_averages_of"), or the word and an option ("table.combine_studies test_method="). Every
underneath entry with "simplydata chooses" lines has an entry here, and a test (tests/test_method_basis.py)
fails when one is missing, when a key is not a current word or option, when a reference has neither a
DOI nor a URL, or when docs/how_simplydata_chooses.md (made by docs/make_method_basis.py) is out of date.

Every reference was looked up before it was cited: a DOI in Crossref (api.crossref.org/works/<doi>), where
authors, year, title and journal below come from; a reference without a DOI at its URL. Where no study
fixes a setting, the entry says so: it is then the convention of the package named, or simplydata's own
starting value, and the option to change it is named.
"""

from __future__ import annotations

from dataclasses import dataclass

# The five principles, in the order simplydata applies them
PRINCIPLES = {
    "P1": "Follow published guidelines and consensus statements where they exist (for example the Cochrane "
          "Handbook, the ASA statement on p-values, the SAMPL guidelines, ICH E9 for clinical trials, the GUM "
          "for measurement).",
    "P2": "Where no guideline exists, follow published method comparisons (simulation studies), and prefer the "
          "method that stays valid under fewer assumptions (Welch's t-test over Student's).",
    "P3": "When the evidence is balanced, match the field's standard software default (the package is named), "
          "so results agree with what reviewers expect. Matching the reference package sometimes takes precedence "
          "over a method comparison; each such entry says which method the studies prefer and the option that "
          "gives it.",
    "P4": "Check the data: refuse or warn when the chosen method does not fit, and say what to use instead.",
    "P5": "Be open: the printout names the method; every default can be changed with an option; the manual "
          "shows the code underneath; the reliability study checks the numbers; independent reviewers checked "
          "every default and its references (see 'How the defaults were reviewed').",
}

# The references behind the principles themselves (shown with them at the top of the document)
PRINCIPLE_REFERENCES = {
    "P1": ("wasserstein2016", "lang2015", "ich_e9", "cochrane10", "gum2008", "bland1994"),
    "P2": ("delacre2017", "veroniki2016"),
    "P3": (),
    "P4": ("zuur2010",),
    "P5": (),
}

# What kind of basis a default has
EVIDENCE = {
    "published": "published guideline or method comparison",
    "convention": "the package named does this, so that results agree with it; studies may prefer another "
                  "method, and when they do the entry says so (and names the option, if there is one)",
    "starting value": "simplydata's own starting value: no published rule fixes it; change it with the option named",
}


@dataclass(frozen=True)
class Reference:
    """One published source. short: "Welch 1947"; text: the full reference; doi or url: where to find it."""

    short: str
    text: str
    doi: str = ""
    url: str = ""

    @property
    def link(self) -> str:
        return f"https://doi.org/{self.doi}" if self.doi else self.url


def _ref(short: str, text: str, doi: str = "", url: str = "") -> Reference:
    return Reference(short, text, doi, url)


@dataclass(frozen=True)
class Basis:
    """Why simplydata chooses what it chooses for one word or option.

    default:      what simplydata chooses, in plain words
    alternatives: what else you can ask for, and the option that asks for it
    why:          one to three plain sentences: the principle and the evidence
    references:   keys of REFERENCES
    principle:    the main principle followed, "P1" to "P5" (PRINCIPLES)
    checks:       what simplydata checks in the data, and when it refuses or warns
    evidence:     "published", "convention" or "starting value" (EVIDENCE)
    """

    default: str
    alternatives: str
    why: str
    references: tuple = ()
    principle: str = "P2"
    checks: str = ""
    evidence: str = "published"


# ---------------------------------------------------------------- references (checked in Crossref)
REFERENCES: dict[str, Reference] = {
    "welch1947": _ref("Welch 1947", "Welch BL (1947). The generalization of 'Student's' problem when several different population variances are involved. Biometrika 34:28-35.", doi="10.1093/biomet/34.1-2.28"),
    "delacre2017": _ref("Delacre et al. 2017", "Delacre M, Lakens D, Leys C (2017). Why Psychologists Should by Default Use Welch’s t-test Instead of Student’s t-test. International Review of Social Psychology 30:92-101.", doi="10.5334/irsp.82"),
    "ruxton2006": _ref("Ruxton 2006", "Ruxton GD (2006). The unequal variance t-test is an underused alternative to Student's t-test and the Mann–Whitney U test. Behavioral Ecology 17:688-690.", doi="10.1093/beheco/ark016"),
    "zimmerman2004": _ref("Zimmerman 2004", "Zimmerman DW (2004). A note on preliminary tests of equality of variances. British Journal of Mathematical and Statistical Psychology 57:173-181.", doi="10.1348/000711004849222"),
    "welch1951": _ref("Welch 1951", "Welch BL (1951). On the comparison of several mean values: an alternative approach. Biometrika 38:330-336.", doi="10.1093/biomet/38.3-4.330"),
    "delacre2019": _ref("Delacre et al. 2019", "Delacre M, Leys C, Mora YL et al. (2019). Taking Parametric Assumptions Seriously: Arguments for the Use of Welch’s F-test instead of the Classical F-test in One-Way ANOVA. International Review of Social Psychology 32:13.", doi="10.5334/irsp.198"),
    "benjamini1995": _ref("Benjamini & Hochberg 1995", "Benjamini Y, Hochberg Y (1995). Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. Journal of the Royal Statistical Society Series B: Statistical Methodology 57:289-300.", doi="10.1111/j.2517-6161.1995.tb02031.x"),
    "wilson1927": _ref("Wilson 1927", "Wilson EB (1927). Probable Inference, the Law of Succession, and Statistical Inference. Journal of the American Statistical Association 22:209-212.", doi="10.1080/01621459.1927.10502953"),
    "agresti1998": _ref("Agresti & Coull 1998", "Agresti A, Coull BA (1998). Approximate is Better than “Exact” for Interval Estimation of Binomial Proportions. The American Statistician 52:119-126.", doi="10.1080/00031305.1998.10480550"),
    "brown2001": _ref("Brown et al. 2001", "Brown LD, Cai TT, DasGupta A (2001). Interval Estimation for a Binomial Proportion. Statistical Science 16:101-133.", doi="10.1214/ss/1009213286"),
    "hyndman1996": _ref("Hyndman & Fan 1996", "Hyndman RJ, Fan Y (1996). Sample Quantiles in Statistical Packages. The American Statistician 50:361-365.", doi="10.1080/00031305.1996.10473566"),
    "mcgill1978": _ref("Mcgill et al. 1978", "Mcgill R, Tukey JW, Larsen WA (1978). Variations of Box Plots. The American Statistician 32:12-16.", doi="10.1080/00031305.1978.10479236"),
    "frigge1989": _ref("Frigge et al. 1989", "Frigge M, Hoaglin DC, Iglewicz B (1989). Some Implementations of the Boxplot. The American Statistician 43:50-54.", doi="10.1080/00031305.1989.10475612"),
    "hoaglin1986": _ref("Hoaglin et al. 1986", "Hoaglin DC, Iglewicz B, Tukey JW (1986). Performance of Some Resistant Rules for Outlier Labeling. Journal of the American Statistical Association 81:991-999.", doi="10.1080/01621459.1986.10478363"),
    "cohen1960": _ref("Cohen 1960", "Cohen J (1960). A Coefficient of Agreement for Nominal Scales. Educational and Psychological Measurement 20:37-46.", doi="10.1177/001316446002000104"),
    "cohen1968": _ref("Cohen 1968", "Cohen J (1968). Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit. Psychological Bulletin 70:213-220.", doi="10.1037/h0026256"),
    "delong1988": _ref("DeLong et al. 1988", "DeLong ER, DeLong DM, Clarke-Pearson DL (1988). Comparing the Areas under Two or More Correlated Receiver Operating Characteristic Curves: A Nonparametric Approach. Biometrics 44:837.", doi="10.2307/2531595"),
    "youden1950": _ref("Youden 1950", "Youden WJ (1950). Index for rating diagnostic tests. Cancer 3:32-35.", doi="10.1002/1097-0142(1950)3:1<32::AID-CNCR2820030106>3.0.CO;2-3"),
    "zou2004": _ref("Zou 2004", "Zou G (2004). A Modified Poisson Regression Approach to Prospective Studies with Binary Data. American Journal of Epidemiology 159:702-706.", doi="10.1093/aje/kwh090"),
    "kaplan1958": _ref("Kaplan & Meier 1958", "Kaplan EL, Meier P (1958). Nonparametric Estimation from Incomplete Observations. Journal of the American Statistical Association 53:457-481.", doi="10.1080/01621459.1958.10501452"),
    "cox1972": _ref("Cox 1972", "Cox DR (1972). Regression Models and Life-Tables. Journal of the Royal Statistical Society Series B: Statistical Methodology 34:187-202.", doi="10.1111/j.2517-6161.1972.tb00899.x"),
    "efron1977": _ref("Efron 1977", "Efron B (1977). The Efficiency of Cox's Likelihood Function for Censored Data. Journal of the American Statistical Association 72:557-565.", doi="10.1080/01621459.1977.10480613"),
    "hertzpicciotto1997": _ref("Hertz-Picciotto & Rockhill 1997", "Hertz-Picciotto I, Rockhill B (1997). Validity and Efficiency of Approximation Methods for Tied Survival Times in Cox Regression. Biometrics 53:1151.", doi="10.2307/2533573"),
    "grambsch1994": _ref("Grambsch & Therneau 1994", "Grambsch PM, Therneau TM (1994). Proportional hazards tests and diagnostics based on weighted residuals. Biometrika 81:515-526.", doi="10.1093/biomet/81.3.515"),
    "peto1972": _ref("Peto & Peto 1972", "Peto R, Peto J (1972). Asymptotically Efficient Rank Invariant Test Procedures. Journal of the Royal Statistical Society. Series A (General) 135:185.", doi="10.2307/2344317"),
    "fine1999": _ref("Fine & Gray 1999", "Fine JP, Gray RJ (1999). A Proportional Hazards Model for the Subdistribution of a Competing Risk. Journal of the American Statistical Association 94:496-509.", doi="10.1080/01621459.1999.10474144"),
    "gray1988": _ref("Gray 1988", "Gray RJ (1988). A Class of K-Sample Tests for Comparing the Cumulative Incidence of a Competing Risk. The Annals of Statistics 16:1141-1154.", doi="10.1214/aos/1176350951"),
    "austin2016": _ref("Austin et al. 2016", "Austin PC, Lee DS, Fine JP (2016). Introduction to the Analysis of Survival Data in the Presence of Competing Risks. Circulation 133:601-609.", doi="10.1161/CIRCULATIONAHA.115.017719"),
    "latouche2013": _ref("Latouche et al. 2013", "Latouche A, Allignol A, Beyersmann J et al. (2013). A competing risks analysis should report results on all cause-specific hazards and cumulative incidence functions. Journal of Clinical Epidemiology 66:648-653.", doi="10.1016/j.jclinepi.2012.09.017"),
    "gooley1999": _ref("Gooley et al. 1999", "Gooley TA, Leisenring W, Crowley J et al. (1999). Estimation of failure probabilities in the presence of competing risks: new representations of old estimators. Statistics in Medicine 18:695-706.", doi="10.1002/(SICI)1097-0258(19990330)18:6<695::AID-SIM60>3.0.CO;2-O"),
    "royston2013": _ref("Royston & Parmar 2013", "Royston P, Parmar MK (2013). Restricted mean survival time: an alternative to the hazard ratio for the design and analysis of randomized trials with a time-to-event outcome. BMC Medical Research Methodology 13.", doi="10.1186/1471-2288-13-152"),
    "uno2014": _ref("Uno et al. 2014", "Uno H, Claggett B, Tian L et al. (2014). Moving Beyond the Hazard Ratio in Quantifying the Between-Group Difference in Survival Analysis. Journal of Clinical Oncology 32:2380-2385.", doi="10.1200/JCO.2014.55.2208"),
    "nieto1996": _ref("Nieto & Coresh 1996", "Nieto FJ, Coresh J (1996). Adjusting Survival Curves for Confounders: A Review and a New Method. American Journal of Epidemiology 143:1059-1068.", doi="10.1093/oxfordjournals.aje.a008670"),
    "denz2023": _ref("Denz et al. 2023", "Denz R, Klaaßen-Mielke R, Timmesfeld N (2023). A comparison of different methods to adjust survival curves for confounders. Statistics in Medicine 42:1461-1479.", doi="10.1002/sim.9681"),
    "cole2004": _ref("Cole & Hernán 2004", "Cole SR, Hernán MA (2004). Adjusted survival curves with inverse probability weights. Computer Methods and Programs in Biomedicine 75:45-49.", doi="10.1016/j.cmpb.2003.10.004"),
    "schoenfeld1983": _ref("Schoenfeld 1983", "Schoenfeld DA (1983). Sample-Size Formula for the Proportional-Hazards Regression Model. Biometrics 39:499.", doi="10.2307/2531021"),
    "freedman1982": _ref("Freedman 1982", "Freedman LS (1982). Tables of the number of patients required in clinical trials using the logrank test. Statistics in Medicine 1:121-129.", doi="10.1002/sim.4780010204"),
    "demidenko2007": _ref("Demidenko 2007", "Demidenko E (2007). Sample size determination for logistic regression revisited. Statistics in Medicine 26:3385-3397.", doi="10.1002/sim.2771"),
    "hsieh1998": _ref("Hsieh et al. 1998", "Hsieh FY, Bloch DA, Larsen MD (1998). A simple method of sample size calculation for linear and logistic regression. Statistics in Medicine 17:1623-1634.", doi="10.1002/(SICI)1097-0258(19980730)17:14<1623::AID-SIM871>3.0.CO;2-S"),
    "faul2009": _ref("Faul et al. 2009", "Faul F, Erdfelder E, Buchner A et al. (2009). Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses. Behavior Research Methods 41:1149-1160.", doi="10.3758/BRM.41.4.1149"),
    "donner1981": _ref("Donner et al. 1981", "Donner A, Birkett N, Buck C (1981). Randomization by cluster. American Journal of Epidemiology 114:906-914.", doi="10.1093/oxfordjournals.aje.a113261"),
    "campbell2012": _ref("Campbell et al. 2012", "Campbell MK, Piaggio G, Elbourne DR et al. (2012). Consort 2010 statement: extension to cluster randomised trials. BMJ 345:e5661-e5661.", doi="10.1136/bmj.e5661"),
    "hoenig2001": _ref("Hoenig & Heisey 2001", "Hoenig JM, Heisey DM (2001). The Abuse of Power. The American Statistician 55:19-24.", doi="10.1198/000313001300339897"),
    "arnold2011": _ref("Arnold et al. 2011", "Arnold BF, Hogan DR, Colford JM et al. (2011). Simulation methods to estimate design power: an overview for applied research. BMC Medical Research Methodology 11.", doi="10.1186/1471-2288-11-94"),
    "veroniki2016": _ref("Veroniki et al. 2016", "Veroniki AA, Jackson D, Viechtbauer W et al. (2016). Methods to estimate the between-study variance and its uncertainty in meta-analysis. Research Synthesis Methods 7:55-79.", doi="10.1002/jrsm.1164"),
    "langan2019": _ref("Langan et al. 2019", "Langan D, Higgins JPT, Jackson D et al. (2019). A comparison of heterogeneity variance estimators in simulated random-effects meta-analyses. Research Synthesis Methods 10:83-98.", doi="10.1002/jrsm.1316"),
    "inthout2014": _ref("IntHout et al. 2014", "IntHout J, Ioannidis JP, Borm GF (2014). The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. BMC Medical Research Methodology 14.", doi="10.1186/1471-2288-14-25"),
    "hartung2001": _ref("Hartung & Knapp 2001", "Hartung J, Knapp G (2001). A refined method for the meta-analysis of controlled clinical trials with binary outcome. Statistics in Medicine 20:3875-3889.", doi="10.1002/sim.1009"),
    "knapp2003": _ref("Knapp & Hartung 2003", "Knapp G, Hartung J (2003). Improved tests for a random effects meta-regression with a single covariate. Statistics in Medicine 22:2693-2710.", doi="10.1002/sim.1482"),
    "rover2015": _ref("Röver et al. 2015", "Röver C, Knapp G, Friede T (2015). Hartung-Knapp-Sidik-Jonkman approach and its modification for random-effects meta-analysis with few studies. BMC Medical Research Methodology 15.", doi="10.1186/s12874-015-0091-1"),
    "inthout2016": _ref("IntHout et al. 2016", "IntHout J, Ioannidis JPA, Rovers MM et al. (2016). Plea for routinely presenting prediction intervals in meta-analysis. BMJ Open 6:e010247.", doi="10.1136/bmjopen-2015-010247"),
    "riley2011": _ref("Riley et al. 2011", "Riley RD, Higgins JPT, Deeks JJ (2011). Interpretation of random effects meta-analyses. BMJ 342:d549-d549.", doi="10.1136/bmj.d549"),
    "higgins2009": _ref("Higgins et al. 2009", "Higgins JPT, Thompson SG, Spiegelhalter DJ (2009). A Re-Evaluation of Random-Effects Meta-Analysis. Journal of the Royal Statistical Society Series A: Statistics in Society 172:137-159.", doi="10.1111/j.1467-985X.2008.00552.x"),
    "borenstein2010": _ref("Borenstein et al. 2010", "Borenstein M, Hedges LV, Higgins JPT et al. (2010). A basic introduction to fixed-effect and random-effects models for meta-analysis. Research Synthesis Methods 1:97-111.", doi="10.1002/jrsm.12"),
    "sterne2011": _ref("Sterne et al. 2011", "Sterne JAC, Sutton AJ, Ioannidis JPA et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ 343:d4002-d4002.", doi="10.1136/bmj.d4002"),
    "egger1997": _ref("Egger et al. 1997", "Egger M, Smith GD, Schneider M et al. (1997). Bias in meta-analysis detected by a simple, graphical test. BMJ 315:629-634.", doi="10.1136/bmj.315.7109.629"),
    "peters2006": _ref("Peters et al. 2006", "Peters JL, Sutton AJ, Jones DR et al. (2006). Comparison of Two Methods to Detect Publication Bias in Meta-analysis. JAMA 295:676-680.", doi="10.1001/jama.295.6.676"),
    "duval2000": _ref("Duval & Tweedie 2000", "Duval S, Tweedie R (2000). Trim and Fill: A Simple Funnel-Plot–Based Method of Testing and Adjusting for Publication Bias in Meta-Analysis. Biometrics 56:455-463.", doi="10.1111/j.0006-341X.2000.00455.x"),
    "dersimonian1986": _ref("DerSimonian & Laird 1986", "DerSimonian R, Laird N (1986). Meta-analysis in clinical trials. Controlled Clinical Trials 7:177-188.", doi="10.1016/0197-2456(86)90046-2"),
    "paule1982": _ref("Paule & Mandel 1982", "Paule RC, Mandel J (1982). Consensus Values and Weighting Factors. Journal of Research of the National Bureau of Standards 87:377.", doi="10.6028/jres.087.022"),
    "viechtbauer2010": _ref("Viechtbauer 2010", "Viechtbauer W (2010). Conducting Meta-Analyses in R with the metafor Package. Journal of Statistical Software 36.", doi="10.18637/jss.v036.i03"),
    "mantel1959": _ref("Mantel & Haenszel 1959", "Mantel N, Haenszel W (1959). Statistical Aspects of the Analysis of Data From Retrospective Studies of Disease. Journal of the National Cancer Institute 22:719-748.", doi="10.1093/jnci/22.4.719"),
    "yusuf1985": _ref("Yusuf et al. 1985", "Yusuf S, Peto R, Lewis J et al. (1985). Beta blockade during and after myocardial infarction: An overview of the randomized trials. Progress in Cardiovascular Diseases 27:335-371.", doi="10.1016/S0033-0620(85)80003-7"),
    "bradburn2007": _ref("Bradburn et al. 2007", "Bradburn MJ, Deeks JJ, Berlin JA et al. (2007). Much ado about nothing: a comparison of the performance of meta-analytical methods with rare events. Statistics in Medicine 26:53-77.", doi="10.1002/sim.2528"),
    "sweeting2004": _ref("Sweeting et al. 2004", "Sweeting MJ, Sutton AJ, Lambert PC (2004). What to add to nothing? Use and avoidance of continuity corrections in meta-analysis of sparse data. Statistics in Medicine 23:1351-1375.", doi="10.1002/sim.1761"),
    "hedges1981": _ref("Hedges 1981", "Hedges LV (1981). Distribution Theory for Glass's Estimator of Effect size and Related Estimators. Journal of Educational Statistics 6:107-128.", doi="10.3102/10769986006002107"),
    "hedges1999": _ref("Hedges et al. 1999", "Hedges LV, Gurevitch J, Curtis PS (1999). The meta-analysis of response ratios in experimental ecology. Ecology 80:1150-1156.", doi="10.1890/0012-9658(1999)080[1150:TMAORR]2.0.CO;2"),
    "deeks2002": _ref("Deeks 2002", "Deeks JJ (2002). Issues in the selection of a summary statistic for meta-analysis of clinical trials with binary outcomes. Statistics in Medicine 21:1575-1600.", doi="10.1002/sim.1188"),
    "sun2010": _ref("Sun et al. 2010", "Sun X, Briel M, Walter SD et al. (2010). Is a subgroup effect believable? Updating criteria to evaluate the credibility of subgroup analyses. BMJ 340:c117-c117.", doi="10.1136/bmj.c117"),
    "thompson2002": _ref("Thompson & Higgins 2002", "Thompson SG, Higgins JPT (2002). How should meta-regression analyses be undertaken and interpreted? Statistics in Medicine 21:1559-1573.", doi="10.1002/sim.1187"),
    "burnham2002": _ref("Burnham & Anderson 2002", "Burnham KP, Anderson DR (2002). Model Selection and Multimodel Inference (2nd ed.). Springer.", doi="10.1007/b97636"),
    "hurvich1989": _ref("Hurvich & Tsai 1989", "Hurvich CM, Tsai CL (1989). Regression and time series model selection in small samples. Biometrika 76:297-307.", doi="10.1093/biomet/76.2.297"),
    "efron1987": _ref("Efron 1987", "Efron B (1987). Better Bootstrap Confidence Intervals. Journal of the American Statistical Association 82:171-185.", doi="10.1080/01621459.1987.10478410"),
    "diciccio1996": _ref("DiCiccio & Efron 1996", "DiCiccio TJ, Efron B (1996). Bootstrap confidence intervals. Statistical Science 11:189-228.", doi="10.1214/ss/1032280214"),
    "venzon1988": _ref("Venzon & Moolgavkar 1988", "Venzon DJ, Moolgavkar SH (1988). A Method for Computing Profile-Likelihood-Based Confidence Intervals. Applied Statistics 37:87.", doi="10.2307/2347496"),
    "huber1964": _ref("Huber 1964", "Huber PJ (1964). Robust Estimation of a Location Parameter. The Annals of Mathematical Statistics 35:73-101.", doi="10.1214/aoms/1177703732"),
    "koenker1978": _ref("Koenker & Bassett 1978", "Koenker R, Bassett G (1978). Regression Quantiles. Econometrica 46:33.", doi="10.2307/1913643"),
    "tibshirani1996": _ref("Tibshirani 1996", "Tibshirani R (1996). Regression Shrinkage and Selection Via the Lasso. Journal of the Royal Statistical Society Series B: Statistical Methodology 58:267-288.", doi="10.1111/j.2517-6161.1996.tb02080.x"),
    "friedman2010": _ref("Friedman et al. 2010", "Friedman J, Hastie T, Tibshirani R (2010). Regularization Paths for Generalized Linear Models via Coordinate Descent. Journal of Statistical Software 33.", doi="10.18637/jss.v033.i01"),
    "hastie2009": _ref("Hastie et al. 2009", "Hastie T, Tibshirani R, Friedman J (2009). The Elements of Statistical Learning. Springer Series in Statistics.", doi="10.1007/978-0-387-84858-7"),
    "davies1987": _ref("Davies 1987", "Davies RB (1987). Hypothesis testing when a nuisance parameter is present only under the alternative. Biometrika 74:33-43.", doi="10.1093/biomet/74.1.33"),
    "muggeo2003": _ref("Muggeo 2003", "Muggeo VMR (2003). Estimating regression models with unknown break-points. Statistics in Medicine 22:3055-3071.", doi="10.1002/sim.1545"),
    "warton2006": _ref("Warton et al. 2006", "Warton DI, Wright IJ, Falster DS et al. (2006). Bivariate line-fitting methods for allometry. Biological Reviews 81:259-291.", doi="10.1017/S1464793106007007"),
    "warton2012smatr": _ref("Warton et al. 2012 (smatr)", "Warton DI, Duursma RA, Falster DS et al. (2012). smatr 3– an R package for estimation and inference about allometric lines. Methods in Ecology and Evolution 3:257-259.", doi="10.1111/j.2041-210X.2011.00153.x"),
    "passing1983": _ref("Passing & Bablok 1983", "Passing H, Bablok W (1983). A New Biometrical Procedure for Testing the Equality of Measurements from Two Different Analytical Methods. Application of linear regression procedures for method comparison studies in Clinical Chemistry, Part I. cclm 21:709-720.", doi="10.1515/cclm.1983.21.11.709"),
    "sen1968": _ref("Sen 1968", "Sen PK (1968). Estimates of the Regression Coefficient Based on Kendall's Tau. Journal of the American Statistical Association 63:1379-1389.", doi="10.1080/01621459.1968.10480934"),
    "siegel1982": _ref("Siegel 1982", "Siegel AF (1982). Robust regression using repeated medians. Biometrika 69:242-244.", doi="10.1093/biomet/69.1.242"),
    "ritz2015": _ref("Ritz et al. 2015", "Ritz C, Baty F, Streibig JC et al. (2015). Dose-Response Analysis Using R. PLoS ONE 10:e0146021.", doi="10.1371/journal.pone.0146021"),
    "oecd2006": _ref("OECD 2006", "OECD (2006). Current Approaches in the Statistical Analysis of Ecotoxicity Data. OECD Series on Testing and Assessment.", doi="10.1787/9789264085275-en"),
    "cleveland1979": _ref("Cleveland 1979", "Cleveland WS (1979). Robust Locally Weighted Regression and Smoothing Scatterplots. Journal of the American Statistical Association 74:829-836.", doi="10.1080/01621459.1979.10481038"),
    "cleveland1988": _ref("Cleveland & Devlin 1988", "Cleveland WS, Devlin SJ (1988). Locally Weighted Regression: An Approach to Regression Analysis by Local Fitting. Journal of the American Statistical Association 83:596-610.", doi="10.1080/01621459.1988.10478639"),
    "pinheiro2000": _ref("Pinheiro & Bates 2000", "Pinheiro JC, Bates DM (2000). Mixed-Effects Models in S and S-PLUS. Springer.", doi="10.1007/b98882"),
    "bates2015": _ref("Bates et al. 2015", "Bates D, Mächler M, Bolker B et al. (2015). Fitting Linear Mixed-Effects Models Using lme4. Journal of Statistical Software 67.", doi="10.18637/jss.v067.i01"),
    "baayen2008": _ref("Baayen et al. 2008", "Baayen RH, Davidson DJ, Bates DM (2008). Mixed-effects modeling with crossed random effects for subjects and items. Journal of Memory and Language 59:390-412.", doi="10.1016/j.jml.2007.12.005"),
    "harville1977": _ref("Harville 1977", "Harville DA (1977). Maximum Likelihood Approaches to Variance Component Estimation and to Related Problems. Journal of the American Statistical Association 72:320-338.", doi="10.1080/01621459.1977.10480998"),
    "kenward1997": _ref("Kenward & Roger 1997", "Kenward MG, Roger JH (1997). Small Sample Inference for Fixed Effects from Restricted Maximum Likelihood. Biometrics 53:983.", doi="10.2307/2533558"),
    "dunnett1955": _ref("Dunnett 1955", "Dunnett CW (1955). A Multiple Comparison Procedure for Comparing Several Treatments with a Control. Journal of the American Statistical Association 50:1096-1121.", doi="10.1080/01621459.1955.10501294"),
    "olson1974": _ref("Olson 1974", "Olson CL (1974). Comparative Robustness of Six Tests in Multivariate Analysis of Variance. Journal of the American Statistical Association 69:894-908.", doi="10.1080/01621459.1974.10480224"),
    "olson1976": _ref("Olson 1976", "Olson CL (1976). On choosing a test statistic in multivariate analysis of variance. Psychological Bulletin 83:579-586.", doi="10.1037/0033-2909.83.4.579"),
    "mcnutt2003": _ref("McNutt et al. 2003", "McNutt LA, Wu C, Xue X, Hafner JP (2003). Estimating the Relative Risk in Cohort Studies and Clinical Trials of Common Outcomes. American Journal of Epidemiology 157:940-943.", doi="10.1093/aje/kwg074"),
    "gail1981": _ref("Gail et al. 1981", "Gail MH, Lubin JH, Rubinstein LV (1981). Likelihood calculations for matched case-control studies and survival studies with tied death times. Biometrika 68:703-707.", doi="10.1093/biomet/68.3.703"),
    "mccullagh1989": _ref("McCullagh & Nelder 1989", "McCullagh P, Nelder JA (1989). Generalized Linear Models (2nd ed.). Chapman and Hall.", doi="10.1007/978-1-4899-3242-6"),
    "wedderburn1974": _ref("Wedderburn 1974", "Wedderburn RWM (1974). Quasi-likelihood functions, generalized linear models, and the Gauss—Newton method. Biometrika 61:439-447.", doi="10.1093/biomet/61.3.439"),
    "mullahy1986": _ref("Mullahy 1986", "Mullahy J (1986). Specification and testing of some modified count data models. Journal of Econometrics 33:341-365.", doi="10.1016/0304-4076(86)90002-3"),
    "zeileis2008": _ref("Zeileis et al. 2008", "Zeileis A, Kleiber C, Jackman S (2008). Regression Models for Count Data in R. Journal of Statistical Software 27.", doi="10.18637/jss.v027.i08"),
    "lambert1992": _ref("Lambert 1992", "Lambert D (1992). Zero-Inflated Poisson Regression, with an Application to Defects in Manufacturing. Technometrics 34:1.", doi="10.2307/1269547"),
    "perperoglou2019": _ref("Perperoglou et al. 2019", "Perperoglou A, Sauerbrei W, Abrahamowicz M et al. (2019). A review of spline function procedures in R. BMC Medical Research Methodology 19.", doi="10.1186/s12874-019-0666-3"),
    "harrell2015": _ref("Harrell 2015", "Harrell FE (2015). Regression Modeling Strategies (2nd ed.). Springer.", doi="10.1007/978-3-319-19425-7"),
    "greenland1986": _ref("Greenland et al. 1986", "Greenland S, Schlesselman JJ, Criqui MH (1986). The fallacy of employing standardized regression coefficients and correlations as measures of effect. American Journal of Epidemiology 123:203-208.", doi="10.1093/oxfordjournals.aje.a114229"),
    "gelman2008": _ref("Gelman 2008", "Gelman A (2008). Scaling regression inputs by dividing by two standard deviations. Statistics in Medicine 27:2865-2873.", doi="10.1002/sim.3107"),
    "box1964": _ref("Box & Cox 1964", "Box GEP, Cox DR (1964). An Analysis of Transformations. Journal of the Royal Statistical Society Series B: Statistical Methodology 26:211-243.", doi="10.1111/j.2517-6161.1964.tb00553.x"),
    "bernal2017": _ref("Lopez Bernal et al. 2017", "Lopez Bernal J, Cummins S, Gasparrini A (2017). Interrupted time series regression for the evaluation of public health interventions: a tutorial. International Journal of Epidemiology 46:348-355.", doi="10.1093/ije/dyw098"),
    "white1980": _ref("White 1980", "White H (1980). A Heteroskedasticity-Consistent Covariance Matrix Estimator and a Direct Test for Heteroskedasticity. Econometrica 48:817.", doi="10.2307/1912934"),
    "long2000": _ref("Long & Ervin 2000", "Long JS, Ervin LH (2000). Using Heteroscedasticity Consistent Standard Errors in the Linear Regression Model. The American Statistician 54:217-224.", doi="10.1080/00031305.2000.10474549"),
    "breusch1979": _ref("Breusch & Pagan 1979", "Breusch TS, Pagan AR (1979). A Simple Test for Heteroscedasticity and Random Coefficient Variation. Econometrica 47:1287.", doi="10.2307/1911963"),
    "koenker1981": _ref("Koenker 1981", "Koenker R (1981). A note on studentizing a test for heteroscedasticity. Journal of Econometrics 17:107-112.", doi="10.1016/0304-4076(81)90062-2"),
    "langsrud2003": _ref("Langsrud 2003", "Langsrud Ø (2003). ANOVA for unbalanced data: Use Type II instead of Type III sums of squares. Statistics and Computing 13:163-167.", doi="10.1023/A:1023260610025"),
    "cook1977": _ref("Cook 1977", "Cook RD (1977). Detection of Influential Observation in Linear Regression. Technometrics 19:15-18.", doi="10.2307/1268249"),
    "shapiro1965": _ref("Shapiro & Wilk 1965", "Shapiro SS, Wilk MB (1965). An analysis of variance test for normality (complete samples). Biometrika 52:591-611.", doi="10.1093/biomet/52.3-4.591"),
    "brown1974": _ref("Brown & Forsythe 1974", "Brown MB, Forsythe AB (1974). Robust Tests for the Equality of Variances. Journal of the American Statistical Association 69:364-367.", doi="10.1080/01621459.1974.10482955"),
    "conover1981": _ref("Conover et al. 1981", "Conover WJ, Johnson ME, Johnson MM (1981). A Comparative Study of Tests for Homogeneity of Variances, with Applications to the Outer Continental Shelf Bidding Data. Technometrics 23:351-361.", doi="10.1080/00401706.1981.10487680"),
    "cochran1954": _ref("Cochran 1954", "Cochran WG (1954). Some Methods for Strengthening the Common χ² Tests. Biometrics 10:417.", doi="10.2307/3001616"),
    "campbell2007": _ref("Campbell 2007", "Campbell I (2007). Chi-squared and Fisher–Irwin tests of two-by-two tables with small sample recommendations. Statistics in Medicine 26:3661-3675.", doi="10.1002/sim.2832"),
    "haviland1990": _ref("Haviland 1990", "Haviland MG (1990). Yates's correction for continuity and the analysis of 2 × 2 contingency tables. Statistics in Medicine 9:363-367.", doi="10.1002/sim.4780090403"),
    "mann1947": _ref("Mann & Whitney 1947", "Mann HB, Whitney DR (1947). On a Test of Whether one of Two Random Variables is Stochastically Larger than the Other. The Annals of Mathematical Statistics 18:50-60.", doi="10.1214/aoms/1177730491"),
    "wilcoxon1945": _ref("Wilcoxon 1945", "Wilcoxon F (1945). Individual Comparisons by Ranking Methods. Biometrics Bulletin 1:80.", doi="10.2307/3001968"),
    "kruskal1952": _ref("Kruskal & Wallis 1952", "Kruskal WH, Wallis WA (1952). Use of Ranks in One-Criterion Variance Analysis. Journal of the American Statistical Association 47:583-621.", doi="10.1080/01621459.1952.10483441"),
    "kramer1956": _ref("Kramer 1956", "Kramer CY (1956). Extension of Multiple Range Tests to Group Means with Unequal Numbers of Replications. Biometrics 12:307.", doi="10.2307/3001469"),
    "games1976": _ref("Games & Howell 1976", "Games PA, Howell JF (1976). Pairwise Multiple Comparison Procedures with Unequal N’s and/or Variances: A Monte Carlo Study. Journal of Educational Statistics 1:113-125.", doi="10.3102/10769986001002113"),
    "dunn1964": _ref("Dunn 1964", "Dunn OJ (1964). Multiple Comparisons Using Rank Sums. Technometrics 6:241-252.", doi="10.1080/00401706.1964.10490181"),
    "fisher1915": _ref("Fisher 1915", "Fisher RA (1915). Frequency Distribution of the Values of the Correlation Coefficient in Samples from an Indefinitely Large Population. Biometrika 10:507.", doi="10.2307/2331838"),
    "bonett2000": _ref("Bonett & Wright 2000", "Bonett DG, Wright TA (2000). Sample Size Requirements for Estimating Pearson, Kendall and Spearman Correlations. Psychometrika 65:23-28.", doi="10.1007/BF02294183"),
    "mcnemar1947": _ref("McNemar 1947", "McNemar Q (1947). Note on the Sampling Error of the Difference Between Correlated Proportions or Percentages. Psychometrika 12:153-157.", doi="10.1007/BF02295996"),
    "fagerland2013": _ref("Fagerland et al. 2013", "Fagerland MW, Lydersen S, Laake P (2013). The McNemar test for binary matched-pairs data: mid-p and asymptotic are better than exact conditional. BMC Medical Research Methodology 13.", doi="10.1186/1471-2288-13-91"),
    "clopper1934": _ref("Clopper & Pearson 1934", "Clopper CJ, Pearson ES (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika 26:404-413.", doi="10.1093/biomet/26.4.404"),
    "garwood1936": _ref("Garwood 1936", "Garwood F (1936). (i) Fiducial Limits for the Poisson Distribution. Biometrika 28:437-442.", doi="10.1093/biomet/28.3-4.437"),
    "katz1978": _ref("Katz et al. 1978", "Katz D, Baptista J, Azen SP et al. (1978). Obtaining Confidence Intervals for the Risk Ratio in Cohort Studies. Biometrics 34:469.", doi="10.2307/2530610"),
    "woolf1955": _ref("Woolf 1955", "Woolf B (1955). On estimating the relation between blood group and disease. Annals of Human Genetics 19:251-253.", doi="10.1111/j.1469-1809.1955.tb01348.x"),
    "newcombe1998": _ref("Newcombe 1998", "Newcombe RG (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. Statistics in Medicine 17:873-890.", doi="10.1002/(SICI)1097-0258(19980430)17:8<873::AID-SIM779>3.0.CO;2-I"),
    "wald1940": _ref("Wald & Wolfowitz 1940", "Wald A, Wolfowitz J (1940). On a Test Whether Two Samples are from the Same Population. The Annals of Mathematical Statistics 11:147-162.", doi="10.1214/aoms/1177731909"),
    "mann1945": _ref("Mann 1945", "Mann HB (1945). Nonparametric Tests Against Trend. Econometrica 13:245.", doi="10.2307/1907187"),
    "hamed1998": _ref("Hamed & Ramachandra Rao 1998", "Hamed KH, Ramachandra Rao A (1998). A modified Mann-Kendall trend test for autocorrelated data. Journal of Hydrology 204:182-196.", doi="10.1016/S0022-1694(97)00125-X"),
    "dickey1979": _ref("Dickey & Fuller 1979", "Dickey DA, Fuller WA (1979). Distribution of the Estimators for Autoregressive Time Series with a Unit Root. Journal of the American Statistical Association 74:427-431.", doi="10.1080/01621459.1979.10482531"),
    "mackinnon1996": _ref("MacKinnon 1996", "MacKinnon JG (1996). Numerical distribution functions for unit root and cointegration tests. Journal of Applied Econometrics 11:601-618.", doi="10.1002/(SICI)1099-1255(199611)11:6<601::AID-JAE417>3.0.CO;2-T"),
    "kwiatkowski1992": _ref("Kwiatkowski et al. 1992", "Kwiatkowski D, Phillips PCB, Schmidt P et al. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root. Journal of Econometrics 54:159-178.", doi="10.1016/0304-4076(92)90104-Y"),
    "killick2012": _ref("Killick et al. 2012", "Killick R, Fearnhead P, Eckley IA (2012). Optimal Detection of Changepoints With a Linear Computational Cost. Journal of the American Statistical Association 107:1590-1598.", doi="10.1080/01621459.2012.737745"),
    "welch1967": _ref("Welch 1967", "Welch P (1967). The use of fast Fourier transform for the estimation of power spectra: A method based on time averaging over short, modified periodograms. IEEE Transactions on Audio and Electroacoustics 15:70-73.", doi="10.1109/TAU.1967.1161901"),
    "gustafsson1996": _ref("Gustafsson 1996", "Gustafsson F (1996). Determining the initial states in forward-backward filtering. IEEE Transactions on Signal Processing 44:988-992.", doi="10.1109/78.492552"),
    "savitzky1964": _ref("Savitzky & Golay 1964", "Savitzky A, Golay MJE (1964). Smoothing and Differentiation of Data by Simplified Least Squares Procedures. Analytical Chemistry 36:1627-1639.", doi="10.1021/ac60214a047"),
    "hyndman2006": _ref("Hyndman & Koehler 2006", "Hyndman RJ, Koehler AB (2006). Another look at measures of forecast accuracy. International Journal of Forecasting 22:679-688.", doi="10.1016/j.ijforecast.2006.03.001"),
    "ljung1978": _ref("Ljung & Box 1978", "Ljung GM, Box GEP (1978). On a measure of lack of fit in time series models. Biometrika 65:297-303.", doi="10.1093/biomet/65.2.297"),
    "bartlett1946": _ref("Bartlett 1946", "Bartlett MS (1946). On the Theoretical Specification and Sampling Properties of Autocorrelated Time-Series. Journal of the Royal Statistical Society Series B: Statistical Methodology 8:27-41.", doi="10.2307/2983611"),
    "crameri2020": _ref("Crameri et al. 2020", "Crameri F, Shephard GE, Heron PJ (2020). The misuse of colour in science communication. Nature Communications 11.", doi="10.1038/s41467-020-19160-7"),
    "nunez2018": _ref("Nuñez et al. 2018", "Nuñez JR, Anderton CR, Renslow RS (2018). Optimizing colormaps with consideration for color vision deficiency to enable accurate interpretation of scientific data. PLoS ONE 13:e0199239.", doi="10.1371/journal.pone.0199239"),
    "cumming2007": _ref("Cumming et al. 2007", "Cumming G, Fidler F, Vaux DL (2007). Error bars in experimental biology. The Journal of Cell Biology 177:7-11.", doi="10.1083/jcb.200611141"),
    "scott1979": _ref("Scott 1979", "Scott DW (1979). On optimal and data-based histograms. Biometrika 66:605-610.", doi="10.1093/biomet/66.3.605"),
    "sturges1926": _ref("Sturges 1926", "Sturges HA (1926). The Choice of a Class Interval. Journal of the American Statistical Association 21:65-66.", doi="10.1080/01621459.1926.10502161"),
    "freedman1981": _ref("Freedman & Diaconis 1981", "Freedman D, Diaconis P (1981). On the histogram as a density estimator: L2 theory. Zeitschrift für Wahrscheinlichkeitstheorie und Verwandte Gebiete 57:453-476.", doi="10.1007/BF01025868"),
    "silverman1986": _ref("Silverman 1986", "Silverman BW (1986; reprinted 2018). Density Estimation for Statistics and Data Analysis. Chapman and Hall.", doi="10.1201/9781315140919"),
    "wilk1968": _ref("Wilk & Gnanadesikan 1968", "Wilk MB, Gnanadesikan R (1968). Probability plotting methods for the analysis for the analysis of data. Biometrika 55:1-17.", doi="10.1093/biomet/55.1.1"),
    "jolliffe2016": _ref("Jolliffe & Cadima 2016", "Jolliffe IT, Cadima J (2016). Principal component analysis: a review and recent developments. Philosophical Transactions of the Royal Society A: Mathematical, Physical and Engineering Sciences 374:20150202.", doi="10.1098/rsta.2015.0202"),
    "bray1957": _ref("Bray & Curtis 1957", "Bray JR, Curtis JT (1957). An Ordination of the Upland Forest Communities of Southern Wisconsin. Ecological Monographs 27:325-349.", doi="10.2307/1942268"),
    "anderson2001": _ref("Anderson 2001", "Anderson MJ (2001). A new method for non-parametric multivariate analysis of variance. Austral Ecology 26:32-46.", doi="10.1111/j.1442-9993.2001.01070.pp.x"),
    "kruskal1964": _ref("Kruskal 1964", "Kruskal JB (1964). Multidimensional Scaling by Optimizing Goodness of Fit to a Nonmetric Hypothesis. Psychometrika 29:1-27.", doi="10.1007/BF02289565"),
    "clarke1993": _ref("Clarke 1993", "Clarke KR (1993). Non-parametric multivariate analyses of changes in community structure. Australian Journal of Ecology 18:117-143.", doi="10.1111/j.1442-9993.1993.tb00438.x"),
    "ward1963": _ref("Ward 1963", "Ward JH (1963). Hierarchical Grouping to Optimize an Objective Function. Journal of the American Statistical Association 58:236-244.", doi="10.1080/01621459.1963.10500845"),
    "rousseeuw1987": _ref("Rousseeuw 1987", "Rousseeuw PJ (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics 20:53-65.", doi="10.1016/0377-0427(87)90125-7"),
    "harrell1996": _ref("Harrell et al. 1996", "Harrell FE, Lee KL, Mark DB (1996). Multivariable prognostic models: issues in developing models, evaluating assumptions and adequacy, and measuring and reducing errors. Statistics in Medicine 15:361-387.", doi="10.1002/(SICI)1097-0258(19960229)15:4<361::AID-SIM168>3.0.CO;2-4"),
    "therneau2000": _ref("Therneau & Grambsch 2000", "Therneau TM, Grambsch PM (2000). Modeling Survival Data: Extending the Cox Model. Statistics for Biology and Health.", doi="10.1007/978-1-4757-3294-8"),
    "hosmer1997": _ref("Hosmer et al. 1997", "Hosmer DW, Hosmer T, Le Cessie S et al. (1997). A comparison of goodness-of-fit tests for the logistic regression model. Statistics in Medicine 16:965-980.", doi="10.1002/(SICI)1097-0258(19970515)16:9<965::AID-SIM509>3.0.CO;2-O"),
    "vancalster2019": _ref("Van Calster et al. 2019", "Van Calster B, McLernon DJ, van Smeden M et al. (2019). Calibration: the Achilles heel of predictive analytics. BMC Medicine 17:230.", doi="10.1186/s12916-019-1466-7"),
    "nagelkerke1991": _ref("Nagelkerke 1991", "Nagelkerke NJD (1991). A note on a general definition of the coefficient of determination. Biometrika 78:691-692.", doi="10.1093/biomet/78.3.691"),
    "tjur2009": _ref("Tjur 2009", "Tjur T (2009). Coefficients of Determination in Logistic Regression Models—A New Proposal: The Coefficient of Discrimination. The American Statistician 63:366-372.", doi="10.1198/tast.2009.08210"),
    "zuur2010": _ref("Zuur et al. 2010", "Zuur AF, Ieno EN, Elphick CS (2010). A protocol for data exploration to avoid common statistical problems. Methods in Ecology and Evolution 1:3-14.", doi="10.1111/j.2041-210X.2009.00001.x"),
    "bolker2009": _ref("Bolker et al. 2009", "Bolker BM, Brooks ME, Clark CJ et al. (2009). Generalized linear mixed models: a practical guide for ecology and evolution. Trends in Ecology & Evolution 24:127-135.", doi="10.1016/j.tree.2008.10.008"),
    "ohara2010": _ref("O'Hara & Kotze 2010", "O'Hara RB, Kotze DJ (2010). Do not log-transform count data. Methods in Ecology and Evolution 1:118-122.", doi="10.1111/j.2041-210X.2010.00021.x"),
    "harrison2018": _ref("Harrison et al. 2018", "Harrison XA, Donaldson L, Correa-Cano ME et al. (2018). A brief introduction to mixed effects modelling and multi-model inference in ecology. PeerJ 6:e4794.", doi="10.7717/peerj.4794"),
    "liang1986": _ref("Liang & Zeger 1986", "Liang KY, Zeger SL (1986). Longitudinal data analysis using generalized linear models. Biometrika 73:13-22.", doi="10.1093/biomet/73.1.13"),
    "luke2017": _ref("Luke 2017", "Luke SG (2017). Evaluating significance in linear mixed-effects models in R. Behavior Research Methods 49:1494-1502.", doi="10.3758/s13428-016-0809-y"),
    "wood2011": _ref("Wood 2011", "Wood SN (2011). Fast Stable Restricted Maximum Likelihood and Marginal Likelihood Estimation of Semiparametric Generalized Linear Models. Journal of the Royal Statistical Society Series B: Statistical Methodology 73:3-36.", doi="10.1111/j.1467-9868.2010.00749.x"),
    "bollen1985": _ref("Bollen & Jackman 1985", "Bollen KA, Jackman RW (1985). Regression Diagnostics. Sociological Methods & Research 13:510-542.", doi="10.1177/0049124185013004004"),
    "hartigan1979": _ref("Hartigan & Wong 1979", "Hartigan JA, Wong MA (1979). Algorithm AS 136: A K-Means Clustering Algorithm. Applied Statistics 28:100.", doi="10.2307/2346830"),
    "faith1987": _ref("Faith et al. 1987", "Faith DP, Minchin PR, Belbin L (1987). Compositional dissimilarity as a robust measure of ecological distance. Vegetatio 69:57-68.", doi="10.1007/BF00038687"),
    "anderson2006": _ref("Anderson 2006", "Anderson MJ (2006). Distance-Based Tests for Homogeneity of Multivariate Dispersions. Biometrics 62:245-253.", doi="10.1111/j.1541-0420.2005.00440.x"),
    "warton2012": _ref("Warton, Wright & Wang 2012", "Warton DI, Wright ST, Wang Y (2012). Distance-based multivariate analyses confound location and dispersion effects. Methods in Ecology and Evolution 3:89-101.", doi="10.1111/j.2041-210X.2011.00127.x"),
    "feldt1965": _ref("Feldt 1965", "Feldt LS (1965). The Approximate Sampling Distribution of Kuder-Richardson Reliability Coefficient Twenty. Psychometrika 30:357-370.", doi="10.1007/BF02289499"),
    "cronbach1951": _ref("Cronbach 1951", "Cronbach LJ (1951). Coefficient Alpha and the Internal Structure of Tests. Psychometrika 16:297-334.", doi="10.1007/BF02310555"),
    "fleiss1971": _ref("Fleiss 1971", "Fleiss JL (1971). Measuring nominal scale agreement among many raters. Psychological Bulletin 76:378-382.", doi="10.1037/h0031619"),
    "sison1995": _ref("Sison & Glaz 1995", "Sison CP, Glaz J (1995). Simultaneous Confidence Intervals and Sample Size Determination for Multinomial Proportions. Journal of the American Statistical Association 90:366-369.", doi="10.1080/01621459.1995.10476521"),
    "zou2007": _ref("Zou 2007", "Zou GY (2007). Toward using confidence intervals to compare correlations. Psychological Methods 12:399-413.", doi="10.1037/1082-989X.12.4.399"),
    "steiger1980": _ref("Steiger 1980", "Steiger JH (1980). Tests for comparing elements of a correlation matrix. Psychological Bulletin 87:245-251.", doi="10.1037/0033-2909.87.2.245"),
    "lin1989": _ref("Lin 1989", "Lin LIK (1989). A Concordance Correlation Coefficient to Evaluate Reproducibility. Biometrics 45:255.", doi="10.2307/2532051"),
    "friedman1937": _ref("Friedman 1937", "Friedman M (1937). The Use of Ranks to Avoid the Assumption of Normality Implicit in the Analysis of Variance. Journal of the American Statistical Association 32:675-701.", doi="10.1080/01621459.1937.10503522"),
    "cochran1950": _ref("Cochran 1950", "Cochran WG (1950). The comparison of percentages in matched samples. Biometrika 37:256-266.", doi="10.1093/biomet/37.3-4.256"),
    "bowker1948": _ref("Bowker 1948", "Bowker AH (1948). A Test for Symmetry in Contingency Tables. Journal of the American Statistical Association 43:572-574.", doi="10.1080/01621459.1948.10483284"),
    "scholz1987": _ref("Scholz & Stephens 1987", "Scholz FW, Stephens MA (1987). K-Sample Anderson–Darling Tests. Journal of the American Statistical Association 82:918-924.", doi="10.1080/01621459.1987.10478517"),
    "massey1951": _ref("Massey 1951", "Massey FJ (1951). The Kolmogorov-Smirnov Test for Goodness of Fit. Journal of the American Statistical Association 46:68-78.", doi="10.1080/01621459.1951.10500769"),
    "hodges1963": _ref("Hodges & Lehmann 1963", "Hodges JL, Lehmann EL (1963). Estimates of Location Based on Rank Tests. The Annals of Mathematical Statistics 34:598-611.", doi="10.1214/aoms/1177704172"),
    "fagerland2009": _ref("Fagerland & Sandvik 2009", "Fagerland MW, Sandvik L (2009). The Wilcoxon–Mann–Whitney test under scrutiny. Statistics in Medicine 28:1487-1497.", doi="10.1002/sim.3561"),
    "fay2010": _ref("Fay & Proschan 2010", "Fay MP, Proschan MA (2010). Wilcoxon-Mann-Whitney or t-test? On assumptions for hypothesis tests and multiple interpretations of decision rules. Statistics Surveys 4:1-39.", doi="10.1214/09-SS051"),
    "eldridge2006": _ref("Eldridge et al. 2006", "Eldridge SM, Ashby D, Kerry S (2006). Sample size for cluster randomized trials: effect of coefficient of variation of cluster size and analysis method. International Journal of Epidemiology 35:1292-1300.", doi="10.1093/ije/dyl129"),
    "hsieh2000": _ref("Hsieh & Lavori 2000", "Hsieh FY, Lavori PW (2000). Sample-Size Calculations for the Cox Proportional Hazards Regression Model with Nonbinary Covariates. Controlled Clinical Trials 21:552-560.", doi="10.1016/S0197-2456(00)00104-5"),
    "rubin1987": _ref("Rubin 1987", "Rubin DB (1987). Multiple Imputation for Nonresponse in Surveys. Wiley Series in Probability and Statistics.", doi="10.1002/9780470316696"),
    "barnard1999": _ref("Barnard & Rubin 1999", "Barnard J, Rubin DB (1999). Small-sample degrees of freedom with multiple imputation. Biometrika 86:948-955.", doi="10.1093/biomet/86.4.948"),
    "vanbuuren2011": _ref("van Buuren & Groothuis-Oudshoorn 2011", "van Buuren S, Groothuis-Oudshoorn K (2011). mice: Multivariate Imputation by Chained Equations in R. Journal of Statistical Software 45.", doi="10.18637/jss.v045.i03"),
    "white2011": _ref("White et al. 2011", "White IR, Royston P, Wood AM (2011). Multiple imputation using chained equations: Issues and guidance for practice. Statistics in Medicine 30:377-399.", doi="10.1002/sim.4067"),
    "ferrari2004": _ref("Ferrari & Cribari-Neto 2004", "Ferrari S, Cribari-Neto F (2004). Beta Regression for Modelling Rates and Proportions. Journal of Applied Statistics 31:799-815.", doi="10.1080/0266476042000214501"),
    "mccullagh1980": _ref("McCullagh 1980", "McCullagh P (1980). Regression Models for Ordinal Data. Journal of the Royal Statistical Society Series B: Statistical Methodology 42:109-127.", doi="10.1111/j.2517-6161.1980.tb01109.x"),
    "verhoef2007": _ref("Ver Hoef & Boveng 2007", "Ver Hoef JM, Boveng PL (2007). Quasi-poisson vs. negative binomial regression: how should we model overdispersed count data? Ecology 88:2766-2772.", doi="10.1890/07-0043.1"),
    "satterthwaite1946": _ref("Satterthwaite 1946", "Satterthwaite FE (1946). An Approximate Distribution of Estimates of Variance Components. Biometrics Bulletin 2:110.", doi="10.2307/3002019"),
    "searle1980": _ref("Searle et al. 1980", "Searle SR, Speed FM, Milliken GA (1980). Population Marginal Means in the Linear Model: An Alternative to Least Squares Means. The American Statistician 34:216-221.", doi="10.1080/00031305.1980.10483031"),
    "mancl2001": _ref("Mancl & DeRouen 2001", "Mancl LA, DeRouen TA (2001). A Covariance Estimator for GEE with Improved Small-Sample Properties. Biometrics 57:126-134.", doi="10.1111/j.0006-341X.2001.00126.x"),
    "hubbard2010": _ref("Hubbard et al. 2010", "Hubbard AE, Ahern J, Fleischer NL et al. (2010). To GEE or Not to GEE. Epidemiology 21:467-474.", doi="10.1097/EDE.0b013e3181caeb90"),
    "mackinnon1985": _ref("MacKinnon & White 1985", "MacKinnon JG, White H (1985). Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties. Journal of Econometrics 29:305-325.", doi="10.1016/0304-4076(85)90158-7"),
    "peduzzi1996": _ref("Peduzzi et al. 1996", "Peduzzi P, Concato J, Kemper E et al. (1996). A simulation study of the number of events per variable in logistic regression analysis. Journal of Clinical Epidemiology 49:1373-1379.", doi="10.1016/S0895-4356(96)00236-3"),
    "vittinghoff2007": _ref("Vittinghoff & McCulloch 2007", "Vittinghoff E, McCulloch CE (2007). Relaxing the Rule of Ten Events per Variable in Logistic and Cox Regression. American Journal of Epidemiology 165:710-718.", doi="10.1093/aje/kwk052"),
    "albert1984": _ref("Albert & Anderson 1984", "Albert A, Anderson JA (1984). On the existence of maximum likelihood estimates in logistic regression models. Biometrika 71:1-10.", doi="10.1093/biomet/71.1.1"),
    "obrien2007": _ref("O'Brien 2007", "O'Brien RM (2007). A Caution Regarding Rules of Thumb for Variance Inflation Factors. Quality & Quantity 41:673-690.", doi="10.1007/s11135-006-9018-6"),
    "davison1997": _ref("Davison & Hinkley 1997", "Davison AC, Hinkley DV (1997). Bootstrap Methods and their Application. Cambridge University Press.", doi="10.1017/CBO9780511802843"),
    "breiman1992": _ref("Breiman & Spector 1992", "Breiman L, Spector P (1992). Submodel Selection and Evaluation in Regression. The X-Random Case. International Statistical Review / Revue Internationale de Statistique 60:291.", doi="10.2307/1403680"),
    "winters1960": _ref("Winters 1960", "Winters PR (1960). Forecasting Sales by Exponentially Weighted Moving Averages. Management Science 6:324-342.", doi="10.1287/mnsc.6.3.324"),
    "hyndman2008": _ref("Hyndman et al. 2008", "Hyndman R, Koehler A, Ord K et al. (2008). Forecasting with Exponential Smoothing. Springer Series in Statistics.", doi="10.1007/978-3-540-71918-2"),
    "hirsch1982": _ref("Hirsch et al. 1982", "Hirsch RM, Slack JR, Smith RA (1982). Techniques of trend analysis for monthly water quality data. Water Resources Research 18:107-121.", doi="10.1029/WR018i001p00107"),
    "yue2002": _ref("Yue et al. 2002", "Yue S, Pilon P, Phinney B et al. (2002). The influence of autocorrelation on the ability to detect trend in hydrological series. Hydrological Processes 16:1807-1829.", doi="10.1002/hyp.1095"),
    "zhang2007": _ref("Zhang & Siegmund 2007", "Zhang NR, Siegmund DO (2007). A Modified Bayes Information Criterion with Applications to the Analysis of Comparative Genomic Hybridization Data. Biometrics 63:22-32.", doi="10.1111/j.1541-0420.2006.00662.x"),
    "killick2014": _ref("Killick & Eckley 2014", "Killick R, Eckley IA (2014). changepoint : An R Package for Changepoint Analysis. Journal of Statistical Software 58.", doi="10.18637/jss.v058.i03"),
    "wong2011": _ref("Wong 2011", "Wong B (2011). Points of view: Color blindness. Nature Methods 8:441-441.", doi="10.1038/nmeth.1618"),
    "liu2018": _ref("Liu & Heer 2018", "Liu Y, Heer J (2018). Somewhere Over the Rainbow. Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems:1-12.", doi="10.1145/3173574.3174172"),
    "harrower2003": _ref("Harrower & Brewer 2003", "Harrower M, Brewer CA (2003). ColorBrewer.org: An Online Tool for Selecting Colour Schemes for Maps. The Cartographic Journal 40:27-37.", doi="10.1179/000870403235002042"),
    "scott1992": _ref("Scott 1992", "Scott DW (1992). Multivariate Density Estimation. Wiley Series in Probability and Statistics.", doi="10.1002/9780470316849"),
    "hintze1998": _ref("Hintze & Nelson 1998", "Hintze JL, Nelson RD (1998). Violin Plots: A Box Plot-Density Trace Synergism. The American Statistician 52:181-184.", doi="10.1080/00031305.1998.10480559"),
    "filliben1975": _ref("Filliben 1975", "Filliben JJ (1975). The Probability Plot Correlation Coefficient Test for Normality. Technometrics 17:111-117.", doi="10.1080/00401706.1975.10489279"),
    "newman2012": _ref("Newman & Scholl 2012", "Newman GE, Scholl BJ (2012). Bar graphs depicting averages are perceptually misinterpreted: The within-the-bar bias. Psychonomic Bulletin & Review 19:601-607.", doi="10.3758/s13423-012-0247-5"),
    "lewis2001": _ref("Lewis & Clarke 2001", "Lewis S, Clarke M (2001). Forest plots: trying to see the wood and the trees. BMJ 322:1479-1480.", doi="10.1136/bmj.322.7300.1479"),
    "sterne2001": _ref("Sterne & Egger 2001", "Sterne JAC, Egger M (2001). Funnel plots for detecting bias in meta-analysis. Journal of Clinical Epidemiology 54:1046-1055.", doi="10.1016/S0895-4356(01)00377-8"),
    "klein2003": _ref("Klein & Moeschberger 2003", "Klein JP, Moeschberger ML (2003). Survival Analysis. Statistics for Biology and Health.", doi="10.1007/b97377"),
    "cutler1958": _ref("Cutler & Ederer 1958", "Cutler SJ, Ederer F (1958). Maximum utilization of the life table method in analyzing survival. Journal of Chronic Diseases 8:699-712.", doi="10.1016/0021-9681(58)90126-7"),
    "partlett2017": _ref("Partlett & Riley 2017", "Partlett C, Riley RD (2017). Random effects meta-analysis: Coverage performance of 95 % confidence and prediction intervals following REML estimation. Statistics in Medicine 36:301-317.", doi="10.1002/sim.7140"),
    "borenstein2013": _ref("Borenstein & Higgins 2013", "Borenstein M, Higgins JPT (2013). Meta-Analysis and Subgroups. Prevention Science 14:134-143.", doi="10.1007/s11121-013-0377-7"),
    "cohen1988": _ref("Cohen 1988", "Cohen J (1988; reprinted 2013). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Routledge.", doi="10.4324/9780203771587"),
    "haynes2021": _ref("Haynes et al. 2021", "Haynes A, Lenz A, Stalder O et al. (2021). presize: An R-package for precision-based sample size calculation in clinical research. Journal of Open Source Software 6:3118.", doi="10.21105/joss.03118"),
    "noether1987": _ref("Noether 1987", "Noether GE (1987). Sample Size Determination for Some Common Nonparametric Tests. Journal of the American Statistical Association 82:645-647.", doi="10.1080/01621459.1987.10478478"),
    "aickin1996": _ref("Aickin & Gensler 1996", "Aickin M, Gensler H (1996). Adjusting for multiple testing when reporting research results: the Bonferroni vs Holm methods. American Journal of Public Health 86:726-728.", doi="10.2105/AJPH.86.5.726"),
    "linnet1993": _ref("Linnet 1993", "Linnet K (1993). Evaluation of regression procedures for methods comparison studies. Clinical Chemistry 39:424-432.", doi="10.1093/clinchem/39.3.424"),
    "bates1988": _ref("Bates & Watts 1988", "Bates DM, Watts DG (1988). Nonlinear Regression Analysis and Its Applications. Wiley Series in Probability and Statistics.", doi="10.1002/9780470316757"),
    "koenker2005": _ref("Koenker 2005", "Koenker R (2005). Quantile Regression. Cambridge University Press.", doi="10.1017/CBO9780511754098"),
    "hendricks1992": _ref("Hendricks & Koenker 1992", "Hendricks W, Koenker R (1992). Hierarchical Spline Models for Conditional Quantiles and the Demand for Electricity. Journal of the American Statistical Association 87:58-68.", doi="10.1080/01621459.1992.10475175"),
    "houslay2017": _ref("Houslay & Wilson 2017", "Houslay TM, Wilson AJ (2017). Avoiding the misuse of BLUP in behavioural ecology. Behavioral Ecology 28:948-952.", doi="10.1093/beheco/arx023"),
    "venables2002": _ref("Venables & Ripley 2002", "Venables WN, Ripley BD (2002). Modern Applied Statistics with S. Statistics and Computing.", doi="10.1007/978-0-387-21706-2"),
    "legendre2001": _ref("Legendre & Gallagher 2001", "Legendre P, Gallagher ED (2001). Ecologically meaningful transformations for ordination of species data. Oecologia 129:271-280.", doi="10.1007/s004420100716"),
    "delignette2015": _ref("Delignette-Muller & Dutang 2015", "Delignette-Muller ML, Dutang C (2015). fitdistrplus : An R Package for Fitting Distributions. Journal of Statistical Software 64.", doi="10.18637/jss.v064.i04"),
    "stephens1974": _ref("Stephens 1974", "Stephens MA (1974). EDF Statistics for Goodness of Fit and Some Comparisons. Journal of the American Statistical Association 69:730-737.", doi="10.1080/01621459.1974.10480196"),
    "nelder1965": _ref("Nelder & Mead 1965", "Nelder JA, Mead R (1965). A Simplex Method for Function Minimization. The Computer Journal 7:308-313.", doi="10.1093/comjnl/7.4.308"),
    "hall1990": _ref("Hall et al. 1990", "Hall P, Kay JW, Titterington DM (1990). Asymptotically optimal difference-based estimation of variance in nonparametric regression. Biometrika 77:521-528.", doi="10.1093/biomet/77.3.521"),
    "hyndman2002": _ref("Hyndman et al. 2002", "Hyndman RJ, Koehler AB, Snyder RD et al. (2002). A state space framework for automatic forecasting using exponential smoothing methods. International Journal of Forecasting 18:439-454.", doi="10.1016/S0169-2070(01)00110-8"),
    "perkins2006": _ref("Perkins & Schisterman 2006", "Perkins NJ, Schisterman EF (2006). The Inconsistency of “Optimal” Cutpoints Obtained using Two Criteria based on the Receiver Operating Characteristic Curve. American Journal of Epidemiology 163:670-675.", doi="10.1093/aje/kwj063"),
    "pocock2002": _ref("Pocock et al. 2002", "Pocock SJ, Clayton TC, Altman DG (2002). Survival plots of time-to-event outcomes in clinical trials: good practice and pitfalls. The Lancet 359:1686-1689.", doi="10.1016/S0140-6736(02)08594-X"),
    "morris2019": _ref("Morris et al. 2019", "Morris TP, Jarvis CI, Cragg W et al. (2019). Proposals on Kaplan–Meier plots in medical research and a survey of stakeholder views: KMunicate. BMJ Open 9:e030215.", doi="10.1136/bmjopen-2019-030215"),
    "schober2018": _ref("Schober et al. 2018", "Schober P, Boer C, Schwarte LA (2018). Correlation Coefficients: Appropriate Use and Interpretation. Anesthesia & Analgesia 126:1763-1768.", doi="10.1213/ANE.0000000000002864"),
    "diedenhofen2015": _ref("Diedenhofen & Musch 2015", "Diedenhofen B, Musch J (2015). cocor: A Comprehensive Solution for the Statistical Comparison of Correlations. PLoS ONE 10:e0121945.", doi="10.1371/journal.pone.0121945"),
    "hayes2007": _ref("Hayes & Krippendorff 2007", "Hayes AF, Krippendorff K (2007). Answering the Call for a Standard Reliability Measure for Coding Data. Communication Methods and Measures 1:77-89.", doi="10.1080/19312450709336664"),
    "student1908": _ref("Student 1908", "Student (1908). The Probable Error of a Mean. Biometrika 6:1.", doi="10.1093/biomet/6.1.1"),
    "campbell1988": _ref("Campbell & Gardner 1988", "Campbell MJ, Gardner MJ (1988). Statistics in Medicine: Calculating confidence intervals for some non-parametric analyses. BMJ 296:1454-1456.", doi="10.1136/bmj.296.6634.1454"),
    "joanes1998": _ref("Joanes & Gill 1998", "Joanes DN, Gill CA (1998). Comparing measures of sample skewness and kurtosis. Journal of the Royal Statistical Society: Series D (The Statistician) 47:183-189.", doi="10.1111/1467-9884.00122"),
    "rousseeuw1993": _ref("Rousseeuw & Croux 1993", "Rousseeuw PJ, Croux C (1993). Alternatives to the Median Absolute Deviation. Journal of the American Statistical Association 88:1273-1283.", doi="10.1080/01621459.1993.10476408"),
    "okada2013": _ref("Okada 2013", "Okada K (2013). Is Omega Squared Less Biased? a Comparison of Three Major Effect Size Indices in One-Way Anova. Behaviormetrika 40:129-147.", doi="10.2333/bhmk.40.129"),
    "ernst2004": _ref("Ernst 2004", "Ernst MD (2004). Permutation Methods: A Basis for Exact Inference. Statistical Science 19:676-685.", doi="10.1214/088342304000000396"),
    "greenhouse1959": _ref("Greenhouse & Geisser 1959", "Greenhouse SW, Geisser S (1959). On Methods in the Analysis of Profile Data. Psychometrika 24:95-112.", doi="10.1007/BF02289823"),
    "haverkamp2017": _ref("Haverkamp & Beauducel 2017", "Haverkamp N, Beauducel A (2017). Violation of the Sphericity Assumption and Its Effect on Type-I Error Rates in Repeated Measures ANOVA and Multi-Level Linear Models (MLM). Frontiers in Psychology 8.", doi="10.3389/fpsyg.2017.01841"),
    "hurlbert1984": _ref("Hurlbert 1984", "Hurlbert SH (1984). Pseudoreplication and the Design of Ecological Field Experiments. Ecological Monographs 54:187-211.", doi="10.2307/1942661"),
    "zhang1998": _ref("Zhang & Yu 1998", "Zhang J, Yu KF (1998). What's the Relative Risk? JAMA 280:1690.", doi="10.1001/jama.280.19.1690"),
    "wasserstein2016": _ref("Wasserstein & Lazar 2016", "Wasserstein RL, Lazar NA (2016). The ASA Statement on p -Values: Context, Process, and Purpose. The American Statistician 70:129-133.", doi="10.1080/00031305.2016.1154108"),
    "bland1994": _ref("Bland & Altman 1994", "Bland JM, Altman DG (1994). Statistics Notes: One and two sided tests of significance. BMJ 309:248.", doi="10.1136/bmj.309.6949.248"),
    "lang2015": _ref("Lang & Altman 2015", "Lang TA, Altman DG (2015). Basic statistical reporting for articles published in Biomedical Journals: The “Statistical Analyses and Methods in the Published Literature” or the SAMPL Guidelines. International Journal of Nursing Studies 52:5-9.", doi="10.1016/j.ijnurstu.2014.09.006"),
    "weissgerber2015": _ref("Weissgerber et al. 2015", "Weissgerber TL, Milic NM, Winham SJ et al. (2015). Beyond Bar and Line Graphs: Time for a New Data Presentation Paradigm. PLOS Biology 13:e1002128.", doi="10.1371/journal.pbio.1002128"),
    "belia2005": _ref("Belia et al. 2005", "Belia S, Fidler F, Williams J et al. (2005). Researchers Misunderstand Confidence Intervals and Standard Error Bars. Psychological Methods 10:389-396.", doi="10.1037/1082-989X.10.4.389"),
    "bland1986": _ref("Bland & Altman 1986", "Bland JM, Altman DG (1986). Statistical methods for assessing agreement between two methods of clinical measurement. The Lancet 327:307-310.", doi="10.1016/S0140-6736(86)90837-8"),
    "bland1999": _ref("Bland & Altman 1999", "Bland JM, Altman DG (1999). Measuring agreement in method comparison studies. Statistical Methods in Medical Research 8:135-160.", doi="10.1177/096228029900800204"),
    "koo2016": _ref("Koo & Li 2016", "Koo TK, Li MY (2016). A Guideline of Selecting and Reporting Intraclass Correlation Coefficients for Reliability Research. Journal of Chiropractic Medicine 15:155-163.", doi="10.1016/j.jcm.2016.02.012"),
    "shrout1979": _ref("Shrout & Fleiss 1979", "Shrout PE, Fleiss JL (1979). Intraclass correlations: Uses in assessing rater reliability. Psychological Bulletin 86:420-428.", doi="10.1037/0033-2909.86.2.420"),
    "mcgraw1996": _ref("McGraw & Wong 1996", "McGraw KO, Wong SP (1996). Forming inferences about some intraclass correlation coefficients. Psychological Methods 1:30-46.", doi="10.1037/1082-989X.1.1.30"),
    "sijtsma2009": _ref("Sijtsma 2009", "Sijtsma K (2009). On the Use, the Misuse, and the Very Limited Usefulness of Cronbach’s Alpha. Psychometrika 74:107-120.", doi="10.1007/s11336-008-9101-0"),
    "bender2001": _ref("Bender & Lange 2001", "Bender R, Lange S (2001). Adjusting for multiple testing—when and how? Journal of Clinical Epidemiology 54:343-349.", doi="10.1016/S0895-4356(00)00314-0"),
    "hesterberg2015": _ref("Hesterberg 2015", "Hesterberg TC (2015). What Teachers Should Know About the Bootstrap: Resampling in the Undergraduate Statistics Curriculum. The American Statistician 69:371-386.", doi="10.1080/00031305.2015.1089789"),
    "gelman2006": _ref("Gelman & Stern 2006", "Gelman A, Stern H (2006). The Difference Between “Significant” and “Not Significant” is not Itself Statistically Significant. The American Statistician 60:328-331.", doi="10.1198/000313006X152649"),
    "schuirmann1987": _ref("Schuirmann 1987", "Schuirmann DJ (1987). A comparison of the Two One-Sided Tests Procedure and the Power Approach for assessing the equivalence of average bioavailability. Journal of Pharmacokinetics and Biopharmaceutics 15:657-680.", doi="10.1007/BF01068419"),
    "lakens2017": _ref("Lakens 2017", "Lakens D (2017). Equivalence Tests. Social Psychological and Personality Science 8:355-362.", doi="10.1177/1948550617697177"),
    "altman1998": _ref("Altman 1998", "Altman DG (1998). Confidence intervals for the number needed to treat. BMJ 317:1309-1312.", doi="10.1136/bmj.317.7168.1309"),
    "davies1998": _ref("Davies et al. 1998", "Davies HTO, Crombie IK, Tavakoli M (1998). When can odds ratios mislead? BMJ 316:989-991.", doi="10.1136/bmj.316.7136.989"),
    "lakens2013": _ref("Lakens 2013", "Lakens D (2013). Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Frontiers in Psychology 4.", doi="10.3389/fpsyg.2013.00863"),
    "bossuyt2015": _ref("Bossuyt et al. 2015", "Bossuyt PM, Reitsma JB, Bruns DE et al. (2015). STARD 2015: an updated list of essential items for reporting diagnostic accuracy studies. Bmj:h5527.", doi="10.1136/bmj.h5527"),
    "gigerenzer1995": _ref("Gigerenzer & Hoffrage 1995", "Gigerenzer G, Hoffrage U (1995). How to improve Bayesian reasoning without instruction: Frequency formats. Psychological Review 102:684-704.", doi="10.1037/0033-295X.102.4.684"),
    "holm1979": _ref("Holm 1979", "Holm S (1979). A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics 6:65-70.", url="https://www.jstor.org/stable/4615733"),
    "mantel1966": _ref("Mantel 1966", "Mantel N (1966). Evaluation of survival data and two new rank order statistics arising in its consideration. Cancer Chemotherapy Reports 50:163-170.", url="https://pubmed.ncbi.nlm.nih.gov/5910392/"),
    "cochrane10": _ref("Deeks et al. (Cochrane Handbook, ch. 10)", "Deeks JJ, Higgins JPT, Altman DG et al. Chapter 10: Analysing data and undertaking meta-analyses. In: Cochrane Handbook for Systematic Reviews of Interventions (current version).", url="https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-10"),
    "okabe2008": _ref("Okabe & Ito 2008", "Okabe M, Ito K (2008). Color Universal Design (CUD): how to make figures and presentations that are friendly to colorblind people.", url="https://jfly.uni-koeln.de/color/"),
    "cleveland1990": _ref("Cleveland et al. 1990", "Cleveland RB, Cleveland WS, McRae JE, Terpenning I (1990). STL: a seasonal-trend decomposition procedure based on loess. Journal of Official Statistics 6:3-73.", url="https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/stl-a-seasonal-trend-decomposition-procedure-based-on-loess.pdf"),
    "ich_e9": _ref("ICH E9 1998", "International Council for Harmonisation (1998). E9: Statistical principles for clinical trials.", url="https://database.ich.org/sites/default/files/E9_Guideline.pdf"),
    "gum2008": _ref("JCGM 100:2008 (GUM)", "Joint Committee for Guides in Metrology (2008). JCGM 100:2008. Evaluation of measurement data: guide to the expression of uncertainty in measurement.", url="https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf"),
    "fpp3": _ref("Hyndman & Athanasopoulos 2021", "Hyndman RJ, Athanasopoulos G (2021). Forecasting: Principles and Practice (3rd ed.). OTexts.", url="https://otexts.com/fpp3/"),
    "emmeans": _ref("Lenth (emmeans)", "Lenth RV. emmeans: Estimated Marginal Means, aka Least-Squares Means. R package.", url="https://CRAN.R-project.org/package=emmeans"),
    "humphreys1969": _ref("Humphreys & Ilgen 1969", "Humphreys LG, Ilgen DR (1969). Note On a Criterion for the Number of Common Factors. Educational and Psychological Measurement 29:571-578.", doi="10.1177/001316446902900303"),
    "crawford2010": _ref("Crawford et al. 2010", "Crawford AV, Green SB, Levy R et al. (2010). Evaluation of Parallel Analysis Methods for Determining the Number of Factors. Educational and Psychological Measurement 70:885-901.", doi="10.1177/0013164410379332"),
    "lim2019": _ref("Lim & Jahng 2019", "Lim S, Jahng S (2019). Determining the number of factors using parallel analysis and its recent variants.. Psychological Methods 24:452-467.", doi="10.1037/met0000230"),
    "briggs2003": _ref("Briggs & MacCallum 2003", "Briggs NE, MacCallum RC (2003). Recovery of Weak Common Factors by Maximum Likelihood and Ordinary Least Squares Estimation. Multivariate Behavioral Research 38:25-56.", doi="10.1207/S15327906MBR3801_2"),
    "dewinter2012": _ref("de Winter & Dodou 2012", "de Winter JCF, Dodou D (2012). Factor recovery by principal axis factoring and maximum likelihood factor analysis as a function of factor pattern and sample size. Journal of Applied Statistics 39:695-710.", doi="10.1080/02664763.2011.610445"),
    "sass2010": _ref("Sass & Schmitt 2010", "Sass DA, Schmitt TA (2010). A Comparative Investigation of Rotation Criteria Within Exploratory Factor Analysis. Multivariate Behavioral Research 45:73-103.", doi="10.1080/00273170903504810"),
    "schafer2002": _ref("Schafer & Graham 2002", "Schafer JL, Graham JW (2002). Missing data: Our view of the state of the art.. Psychological Methods 7:147-177.", doi="10.1037/1082-989X.7.2.147"),
    "hu1999": _ref("Hu & Bentler 1999", "Hu L, Bentler PM (1999). Cutoff criteria for fit indexes in covariance structure analysis: Conventional criteria versus new alternatives. Structural Equation Modeling: A Multidisciplinary Journal 6:1-55.", doi="10.1080/10705519909540118"),
    "marsh2004": _ref("Marsh et al. 2004", "Marsh HW, Hau KT, Wen Z (2004). In Search of Golden Rules: Comment on Hypothesis-Testing Approaches to Setting Cutoff Values for Fit Indexes and Dangers in Overgeneralizing Hu and Bentler's (1999) Findings. Structural Equation Modeling: A Multidisciplinary Journal 11:320-341.", doi="10.1207/s15328007sem1103_2"),
    "maccallum1999": _ref("MacCallum et al. 1999", "MacCallum RC, Widaman KF, Zhang S et al. (1999). Sample size in factor analysis.. Psychological Methods 4:84-99.", doi="10.1037/1082-989X.4.1.84"),
    "horn1965": _ref("Horn 1965", "Horn JL (1965). A Rationale and Test for the Number of Factors in Factor Analysis. Psychometrika 30:179-185.", doi="10.1007/BF02289447"),
    "zwick1986": _ref("Zwick & Velicer 1986", "Zwick WR, Velicer WF (1986). Comparison of five rules for determining the number of components to retain.. Psychological Bulletin 99:432-442.", doi="10.1037/0033-2909.99.3.432"),
    "fabrigar1999": _ref("Fabrigar et al. 1999", "Fabrigar LR, Wegener DT, MacCallum RC et al. (1999). Evaluating the use of exploratory factor analysis in psychological research.. Psychological Methods 4:272-299.", doi="10.1037/1082-989X.4.3.272"),
    "rosseel2012": _ref("Rosseel 2012", "Rosseel Y (2012). lavaan: An R Package for Structural Equation Modeling. Journal of Statistical Software 48.", doi="10.18637/jss.v048.i02"),
    "enders2001": _ref("Enders & Bandalos 2001", "Enders C, Bandalos D (2001). The Relative Performance of Full Information Maximum Likelihood Estimation for Missing Data in Structural Equation Models. Structural Equation Modeling: A Multidisciplinary Journal 8:430-457.", doi="10.1207/S15328007SEM0803_5"),
    "harman1966": _ref("Harman & Jones 1966", "Harman HH, Jones WH (1966). Factor Analysis by Minimizing Residuals (Minres). Psychometrika 31:351-368.", doi="10.1007/BF02289468"),
    "bernaards2005": _ref("Bernaards & Jennrich 2005", "Bernaards CA, Jennrich RI (2005). Gradient Projection Algorithms and Software for Arbitrary Rotation Criteria in Factor Analysis. Educational and Psychological Measurement 65:676-696.", doi="10.1177/0013164404272507"),
    "kaiser1958": _ref("Kaiser 1958", "Kaiser HF (1958). The Varimax Criterion for Analytic Rotation in Factor Analysis. Psychometrika 23:187-200.", doi="10.1007/BF02289233"),
    "mcardle2001": _ref("McArdle & Anderson 2001", "McArdle BH, Anderson MJ (2001). Fitting multivariate models to community data: a comment on distance-based redundancy analysis. Ecology 82:290-297.", doi="10.1890/0012-9658(2001)082[0290:FMMTCD]2.0.CO;2"),
    "kaufman1990": _ref("Kaufman & Rousseeuw 1990", "Kaufman L, Rousseeuw PJ (1990). Finding Groups in Data. Wiley Series in Probability and Statistics.", doi="10.1002/9780470316801"),
    "milligan1985": _ref("Milligan & Cooper 1985", "Milligan GW, Cooper MC (1985). An Examination of Procedures for Determining the Number of Clusters in a Data Set. Psychometrika 50:159-179.", doi="10.1007/BF02294245"),
    "borcard2018": _ref("Borcard et al. 2018", "Borcard D, Gillet F, Legendre P (2018). Numerical Ecology with R. Use R!.", doi="10.1007/978-3-319-71404-2"),
    "murtagh2014": _ref("Murtagh & Legendre 2014", "Murtagh F, Legendre P (2014). Ward's Hierarchical Agglomerative Clustering Method: Which Algorithms Implement Ward's Criterion?. Journal of Classification 31:274-295.", doi="10.1007/s00357-014-9161-z"),
    "chao2005": _ref("Chao 2005", "Chao A (2005). Species Estimation and Applications. Encyclopedia of Statistical Sciences.", doi="10.1002/0471667196.ess5051"),
    "lubbe2021": _ref("Lubbe et al. 2021", "Lubbe S, Filzmoser P, Templ M (2021). Comparison of zero replacement strategies for compositional data with large numbers of zeros. Chemometrics and Intelligent Laboratory Systems 210:104248.", doi="10.1016/j.chemolab.2021.104248"),
    "terbraak1985": _ref("ter Braak 1985", "ter Braak CJF (1985). Correspondence Analysis of Incidence and Abundance Data: Properties in Terms of a Unimodal Response Model. Biometrics 41:859.", doi="10.2307/2530959"),
    "hurlbert1971": _ref("Hurlbert 1971", "Hurlbert SH (1971). The Nonconcept of Species Diversity: A Critique and Alternative Parameters. Ecology 52:577-586.", doi="10.2307/1934145"),
    "chao1987": _ref("Chao 1987", "Chao A (1987). Estimating the Population Size for Capture-Recapture Data with Unequal Catchability. Biometrics 43:783.", doi="10.2307/2531532"),
    "jost2006": _ref("Jost 2006", "Jost L (2006). Entropy and diversity. Oikos 113:363-375.", doi="10.1111/j.2006.0030-1299.14714.x"),
    "hill1973": _ref("Hill 1973a", "Hill MO (1973). Diversity and Evenness: A Unifying Notation and Its Consequences. Ecology 54:427-432.", doi="10.2307/1934352"),
    "shannon1948": _ref("Shannon 1948", "Shannon CE (1948). A Mathematical Theory of Communication. Bell System Technical Journal 27:379-423.", doi="10.1002/j.1538-7305.1948.tb01338.x"),
    "simpson1949": _ref("Simpson 1949", "Simpson EH (1949). Measurement of Diversity. Nature 163:688-688.", doi="10.1038/163688a0"),
    "palarea2015": _ref("Palarea-Albaladejo & Martín-Fernández 2015", "Palarea-Albaladejo J, Martín-Fernández JA (2015). zCompositions — R package for multivariate imputation of left-censored data under a compositional approach. Chemometrics and Intelligent Laboratory Systems 143:85-96.", doi="10.1016/j.chemolab.2015.02.019"),
    "martinfernandez2015": _ref("Martín-Fernández et al. 2015", "Martín-Fernández JA, Hron K, Templ M et al. (2015). Bayesian-multiplicative treatment of count zeros in compositional data sets. Statistical Modelling 15:134-158.", doi="10.1177/1471082X14535524"),
    "aitchison1982": _ref("Aitchison 1982", "Aitchison J (1982). The Statistical Analysis of Compositional Data. Journal of the Royal Statistical Society Series B: Statistical Methodology 44:139-160.", doi="10.1111/j.2517-6161.1982.tb01195.x"),
    "egozcue2003": _ref("Egozcue et al. 2003", "Egozcue JJ, Pawlowsky-Glahn V, Mateu-Figueras G et al. (2003). Isometric Logratio Transformations for Compositional Data Analysis. Mathematical Geology 35:279-300.", doi="10.1023/A:1023818214614"),
    "gloor2017": _ref("Gloor et al. 2017", "Gloor GB, Macklaim JM, Pawlowsky-Glahn V et al. (2017). Microbiome Datasets Are Compositional: And This Is Not Optional. Frontiers in Microbiology 8.", doi="10.3389/fmicb.2017.02224"),
    "gower1966": _ref("Gower 1966", "Gower JC (1966). Some distance properties of latent root and vector methods used in multivariate analysis. Biometrika 53:325-338.", doi="10.1093/biomet/53.3-4.325"),
    "legendre1999": _ref("Legendre & Anderson 1999", "Legendre P, Anderson MJ (1999). Distance-based redundancy analysis: testing multispecies responses in multifactorial ecological experiments. Ecological Monographs 69:1-24.", doi="10.1890/0012-9615(1999)069[0001:DBRATM]2.0.CO;2"),
    "peresneto2006": _ref("Peres-Neto et al. 2006", "Peres-Neto PR, Legendre P, Dray S et al. (2006). Variation partitioning of species data matrices: estimation and comparison of fractions. Ecology 87:2614-2625.", doi="10.1890/0012-9658(2006)87[2614:VPOSDM]2.0.CO;2"),
    "terbraak1986": _ref("ter Braak 1986", "ter Braak CJF (1986). Canonical Correspondence Analysis: A New Eigenvector Technique for Multivariate Direct Gradient Analysis. Ecology 67:1167-1179.", doi="10.2307/1938672"),
    "legendre2015": _ref("Legendre et al. 2015", "Legendre P, Fortin M, Borcard D (2015). Should the Mantel test be used in spatial analysis?. Methods in Ecology and Evolution 6:1239-1247.", doi="10.1111/2041-210X.12425"),
    "peresneto2001": _ref("Peres-Neto & Jackson 2001", "Peres-Neto PR, Jackson DA (2001). How well do multivariate data sets match? The advantages of a Procrustean superimposition approach over the Mantel test. Oecologia 129:169-178.", doi="10.1007/s004420100720"),
    "fisher1936": _ref("Fisher 1936", "Fisher RA (1936). The use of multiple measurements in taxonomic problems. Annals of Eugenics 7:179-188.", doi="10.1111/j.1469-1809.1936.tb02137.x"),
    "hill1973b": _ref("Hill 1973b", "Hill MO (1973). Reciprocal Averaging: An Eigenvector Method of Ordination. The Journal of Ecology 61:237.", doi="10.2307/2258931"),
    "chao2012": _ref("Chao & Jost 2012", "Chao A, Jost L (2012). Coverage-based rarefaction and extrapolation: standardizing samples by completeness rather than size. Ecology 93:2533-2547.", doi="10.1890/11-1952.1"),
    "chao2014": _ref("Chao et al. 2014", "Chao A, Gotelli NJ, Hsieh TC et al. (2014). Rarefaction and extrapolation with Hill numbers: a framework for sampling and estimation in species diversity studies. Ecological Monographs 84:45-67.", doi="10.1890/13-0133.1"),
    "mcmurdie2014": _ref("McMurdie & Holmes 2014", "McMurdie PJ, Holmes S (2014). Waste Not, Want Not: Why Rarefying Microbiome Data Is Inadmissible. PLoS Computational Biology 10:e1003531.", doi="10.1371/journal.pcbi.1003531"),
    "anderson2013": _ref("Anderson & Walsh 2013", "Anderson MJ, Walsh DCI (2013). PERMANOVA, ANOSIM, and the Mantel test in the face of heterogeneous dispersions: What null hypothesis are you testing?. Ecological Monographs 83:557-574.", doi="10.1890/12-2010.1"),
    "cain2011": _ref("Cain et al. 2011", "Cain KC, Harlow SD, Little RJ et al. (2011). Bias Due to Left Truncation and Left Censoring in Longitudinal Studies of Developmental and Disease Processes. American Journal of Epidemiology 173:1078-1084.", doi="10.1093/aje/kwq481"),
    "kocherginsky2005": _ref("Kocherginsky et al. 2005", "Kocherginsky M, He X, Mu Y (2005). Practical Confidence Intervals for Regression Quantiles. Journal of Computational and Graphical Statistics 14:41-55.", doi="10.1198/106186005X27563"),
    "gardner1985": _ref("Gardner & McKenzie 1985", "Gardner ES, McKenzie E (1985). Forecasting Trends in Time Series. Management Science 31:1237-1246.", doi="10.1287/mnsc.31.10.1237"),
    "lenth2001": _ref("Lenth 2001", "Lenth RV (2001). Some Practical Guidelines for Effective Sample Size Determination. The American Statistician 55:187-193.", doi="10.1198/000313001317098149"),
    "austin2015": _ref("Austin & Steyerberg 2015", "Austin PC, Steyerberg EW (2015). The number of subjects per variable required in linear regression analyses. Journal of Clinical Epidemiology 68:627-636.", doi="10.1016/j.jclinepi.2014.12.014"),
    "peters2007": _ref("Peters et al. 2007", "Peters JL, Sutton AJ, Jones DR et al. (2007). Performance of the trim and fill method in the presence of publication bias and between-study heterogeneity. Statistics in Medicine 26:4544-4562.", doi="10.1002/sim.2889"),
    "huynh1976": _ref("Huynh & Feldt 1976", "Huynh H, Feldt LS (1976). Estimation of the Box Correction for Degrees of Freedom from Sample Data in Randomized Block and Split-Plot Designs. Journal of Educational Statistics 1:69-82.", doi="10.3102/10769986001001069"),
    "rochon2012": _ref("Rochon et al. 2012", "Rochon J, Gondan M, Kieser M (2012). To test or not to test: Preliminary assessment of normality when comparing two independent samples. BMC Medical Research Methodology 12.", doi="10.1186/1471-2288-12-81"),
    "albers2018": _ref("Albers & Lakens 2018", "Albers C, Lakens D (2018). When power analyses based on pilot data are biased: Inaccurate effect size estimators and follow-up bias. Journal of Experimental Social Psychology 74:187-195.", doi="10.1016/j.jesp.2017.09.004"),
    "leeflang2008": _ref("Leeflang et al. 2008", "Leeflang MMG, Moons KGM, Reitsma JB et al. (2008). Bias in Sensitivity and Specificity Caused by Data-Driven Selection of Optimal Cutoff Values: Mechanisms, Magnitude, and Solutions. Clinical Chemistry 54:729-737.", doi="10.1373/clinchem.2007.096032"),
    "ewald2006": _ref("Ewald 2006", "Ewald B (2006). Post hoc choice of cut points introduced bias to diagnostic research. Journal of Clinical Epidemiology 59:798-801.", doi="10.1016/j.jclinepi.2005.11.025"),
    "hoaglin1987": _ref("Hoaglin & Iglewicz 1987", "Hoaglin DC, Iglewicz B (1987). Fine-Tuning Some Resistant Rules for Outlier Labeling. Journal of the American Statistical Association 82:1147-1149.", doi="10.1080/01621459.1987.10478551"),
    "yap2011": _ref("Yap & Sim 2011", "Yap BW, Sim CH (2011). Comparisons of various types of normality tests. Journal of Statistical Computation and Simulation 81:2141-2155.", doi="10.1080/00949655.2010.520163"),
    "stute1993": _ref("Stute et al. 1993", "Stute W, González Manteiga W, Presedo Quindimil M (1993). Bootstrap based goodness-of-fit-tests. Metrika 40:243-256.", doi="10.1007/BF02613687"),
    "wilcox2003": _ref("Wilcox & Keselman 2003", "Wilcox RR, Keselman HJ (2003). Modern Robust Data Analysis Methods: Measures of Central Tendency.. Psychological Methods 8:254-274.", doi="10.1037/1082-989X.8.3.254"),
    "przyborowski1940": _ref("Przyborowski & Wilenski 1940", "Przyborowski J, Wilenski H (1940). Homogeneity of results in testing samples from poisson series. Biometrika 31:313-323.", doi="10.1093/biomet/31.3-4.313"),
    "fay2010b": _ref("Fay 2010", "Fay M (2010). Two-sided Exact Tests and Matching Confidence Intervals for Discrete Data. The R Journal 2:53.", doi="10.32614/RJ-2010-008"),
    "greenland1985": _ref("Greenland & Robins 1985", "Greenland S, Robins JM (1985). Estimation of a Common Effect Parameter from Sparse Follow-Up Data. Biometrics 41:55.", doi="10.2307/2530643"),
    "tarone1985": _ref("Tarone 1985", "Tarone RE (1985). On heterogeneity tests based on efficient scores. Biometrika 72:91-95.", doi="10.1093/biomet/72.1.91"),
    "mckinnon1998": _ref("McKinnon 1998", "McKinnon KIM (1998). Convergence of the Nelder--Mead Simplex Method to a Nonstationary Point. SIAM Journal on Optimization 9:148-158.", doi="10.1137/S1052623496303482"),
    "carkeet2015": _ref("Carkeet 2015", "Carkeet A (2015). Exact Parametric Confidence Intervals for Bland-Altman Limits of Agreement. Optometry and Vision Science 92.", doi="10.1097/OPX.0000000000000513"),
    "bonett2006": _ref("Bonett 2006", "Bonett DG (2006). Approximate confidence interval for standard deviation of nonnormal distributions. Computational Statistics & Data Analysis 50:775-782.", doi="10.1016/j.csda.2004.10.003"),
    "may2000": _ref("May & Johnson 2000", "May WL, Johnson WD (2000). Constructing Two-Sided Simultaneous Confidence Intervals for Multinomial Proportions for Small Counts in a Large Number of Cells. Journal of Statistical Software 5.", doi="10.18637/jss.v005.i06"),
    "swed1943": _ref("Swed & Eisenhart 1943", "Swed FS, Eisenhart C (1943). Tables for Testing Randomness of Grouping in a Sequence of Alternatives. The Annals of Mathematical Statistics 14:66-87.", doi="10.1214/aoms/1177731494"),
    "mcneish2018": _ref("McNeish 2018", "McNeish D (2018). Thanks coefficient alpha, we’ll take it from here. Psychological Methods 23:412-433.", doi="10.1037/met0000144"),
    "leys2013": _ref("Leys et al. 2013", "Leys C, Ley C, Klein O et al. (2013). Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the median. Journal of Experimental Social Psychology 49:764-766.", doi="10.1016/j.jesp.2013.03.013"),
    "akaike1974": _ref("Akaike 1974", "Akaike H (1974). A new look at the statistical model identification. IEEE Transactions on Automatic Control 19:716-723.", doi="10.1109/TAC.1974.1100705"),
    "hosmer2013": _ref("Hosmer et al. 2013", "Hosmer DW, Lemeshow S, Sturdivant RX (2013). Applied Logistic Regression (3rd ed.). Wiley Series in Probability and Statistics.", doi="10.1002/9781118548387"),
    "kalbfleisch2002": _ref("Kalbfleisch & Prentice 2002", "Kalbfleisch JD, Prentice RL (2002). The Statistical Analysis of Failure Time Data (2nd ed.). Wiley Series in Probability and Statistics.", doi="10.1002/9781118032985"),
    "feinstein1990": _ref("Feinstein & Cicchetti 1990", "Feinstein AR, Cicchetti DV (1990). High agreement but low Kappa: I. the problems of two paradoxes. Journal of Clinical Epidemiology 43:543-549.", doi="10.1016/0895-4356(90)90158-L"),
    "suissa2008": _ref("Suissa 2008", "Suissa S (2008). Immortal Time Bias in Pharmacoepidemiology. American Journal of Epidemiology 167:492-499.", doi="10.1093/aje/kwm324"),
    "berk2013": _ref("Berk et al. 2013", "Berk R, Brown L, Buja A et al. (2013). Valid post-selection inference. The Annals of Statistics 41:802-837.", doi="10.1214/12-AOS1077"),
    "whittingham2006": _ref("Whittingham et al. 2006", "Whittingham MJ, Stephens PA, Bradbury RB et al. (2006). Why do we still use stepwise modelling in ecology and behaviour? Journal of Animal Ecology 75:1182-1189.", doi="10.1111/j.1365-2656.2006.01141.x"),
    # S3c-3: directions, places and extremes (each DOI looked up in Crossref on 2026-11-21)
    "fisher1993": _ref("Fisher 1993", "Fisher NI (1993). Statistical Analysis of Circular Data. Cambridge University Press.", doi="10.1017/CBO9780511564345"),
    "mardia1999": _ref("Mardia & Jupp 1999", "Mardia KV, Jupp PE (1999). Directional Statistics. Wiley Series in Probability and Statistics. Wiley.", doi="10.1002/9780470316979"),
    "moran1950": _ref("Moran 1950", "Moran PAP (1950). Notes on continuous stochastic phenomena. Biometrika 37:17-23.", doi="10.1093/biomet/37.1-2.17"),
    "bivand2018": _ref("Bivand & Wong 2018", "Bivand RS, Wong DWS (2018). Comparing implementations of global and local indicators of spatial association. TEST 27:716-748.", doi="10.1007/s11749-018-0599-x"),
    "cressie1985": _ref("Cressie 1985", "Cressie N (1985). Fitting variogram models by weighted least squares. Journal of the International Association for Mathematical Geology 17:563-586.", doi="10.1007/BF01032109"),
    "pebesma2004": _ref("Pebesma 2004", "Pebesma EJ (2004). Multivariable geostatistics in S: the gstat package. Computers & Geosciences 30:683-691.", doi="10.1016/j.cageo.2004.03.012"),
    "coles2001": _ref("Coles 2001", "Coles S (2001). An Introduction to Statistical Modeling of Extreme Values. Springer Series in Statistics. Springer.", doi="10.1007/978-1-4471-3675-0"),
    "gilleland2016": _ref("Gilleland & Katz 2016", "Gilleland E, Katz RW (2016). extRemes 2.0: An Extreme Value Analysis Package in R. Journal of Statistical Software 72(8).", doi="10.18637/jss.v072.i08"),
    "davison1990": _ref("Davison & Smith 1990", "Davison AC, Smith RL (1990). Models for Exceedances Over High Thresholds. Journal of the Royal Statistical Society Series B 52:393-425.", doi="10.1111/j.2517-6161.1990.tb01796.x"),
    "ferro2003": _ref("Ferro & Segers 2003", "Ferro CAT, Segers J (2003). Inference for Clusters of Extreme Values. Journal of the Royal Statistical Society Series B 65:545-556.", doi="10.1111/1467-9868.00401"),
    # S3d-2: epidemiology and cause and effect (each DOI looked up in Crossref on 2026-11-21; the EMA guideline and
    # van Buuren's book at their URL)
    "rosenbaum1983": _ref("Rosenbaum & Rubin 1983", "Rosenbaum PR, Rubin DB (1983). The central role of the propensity score in observational studies for causal effects. Biometrika 70:41-55.", doi="10.1093/biomet/70.1.41"),
    "austin2009": _ref("Austin 2009", "Austin PC (2009). Balance diagnostics for comparing the distribution of baseline covariates between treatment groups in propensity-score matched samples. Statistics in Medicine 28:3083-3107.", doi="10.1002/sim.3697"),
    "austin2011": _ref("Austin 2011", "Austin PC (2011). Optimal caliper widths for propensity-score matching when estimating differences in means and differences in proportions in observational studies. Pharmaceutical Statistics 10:150-161.", doi="10.1002/pst.433"),
    "austin2015iptw": _ref("Austin & Stuart 2015", "Austin PC, Stuart EA (2015). Moving towards best practice when using inverse probability of treatment weighting (IPTW) using the propensity score to estimate causal treatment effects in observational studies. Statistics in Medicine 34:3661-3679.", doi="10.1002/sim.6607"),
    "lunceford2004": _ref("Lunceford & Davidian 2004", "Lunceford JK, Davidian M (2004). Stratification and weighting via the propensity score in estimation of causal treatment effects: a comparative study. Statistics in Medicine 23:2937-2960.", doi="10.1002/sim.1903"),
    "stuart2010": _ref("Stuart 2010", "Stuart EA (2010). Matching Methods for Causal Inference: A Review and a Look Forward. Statistical Science 25:1-21.", doi="10.1214/09-STS313"),
    "ho2011": _ref("Ho et al. 2011", "Ho DE, Imai K, King G, Stuart EA (2011). MatchIt: Nonparametric Preprocessing for Parametric Causal Inference. Journal of Statistical Software 42(8).", doi="10.18637/jss.v042.i08"),
    "imai2010": _ref("Imai et al. 2010", "Imai K, Keele L, Tingley D (2010). A general approach to causal mediation analysis. Psychological Methods 15:309-334.", doi="10.1037/a0020761"),
    "tingley2014": _ref("Tingley et al. 2014", "Tingley D, Yamamoto T, Hirose K, Keele L, Imai K (2014). mediation: R Package for Causal Mediation Analysis. Journal of Statistical Software 59(5).", doi="10.18637/jss.v059.i05"),
    "rockhill1998": _ref("Rockhill et al. 1998", "Rockhill B, Newman B, Weinberg C (1998). Use and misuse of population attributable fractions. American Journal of Public Health 88:15-19.", doi="10.2105/AJPH.88.1.15"),
    "fay1997": _ref("Fay & Feuer 1997", "Fay MP, Feuer EJ (1997). Confidence intervals for directly standardized rates: a method based on the gamma distribution. Statistics in Medicine 16:791-801.", doi="10.1002/(SICI)1097-0258(19970415)16:7<791::AID-SIM500>3.0.CO;2-#"),
    "ulm1990": _ref("Ulm 1990", "Ulm K (1990). Simple method to calculate the confidence interval of a standardized mortality ratio (SMR). American Journal of Epidemiology 131:373-375.", doi="10.1093/oxfordjournals.aje.a115507"),
    "ema2010": _ref("EMA 2010", "European Medicines Agency, Committee for Medicinal Products for Human Use (2010). Guideline on the Investigation of Bioequivalence. CPMP/EWP/QWP/1401/98 Rev. 1/Corr**.", url="https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-investigation-bioequivalence-rev1_en.pdf"),
    "freeman1989": _ref("Freeman 1989", "Freeman PR (1989). The performance of the two-stage analysis of two-treatment, two-period crossover trials. Statistics in Medicine 8:1421-1432.", doi="10.1002/sim.4780081202"),
    "schutz2014": _ref("Schütz et al. 2014", "Schütz H, Labes D, Fuglsang A (2014). Reference Datasets for 2-Treatment, 2-Sequence, 2-Period Bioequivalence Studies. The AAPS Journal 16:1292-1297.", doi="10.1208/s12248-014-9661-0"),
    "white2009": _ref("White & Royston 2009", "White IR, Royston P (2009). Imputing missing covariate values for the Cox model. Statistics in Medicine 28:1982-1998.", doi="10.1002/sim.3618"),
    "vanbuuren2018": _ref("van Buuren 2018", "van Buuren S (2018). Flexible Imputation of Missing Data, 2nd ed. Chapman & Hall/CRC (section 5.2.3, pooling correlations on Fisher's z).", url="https://stefvanbuuren.name/fimd/"),
    # S3c-4: small additions (each DOI looked up in Crossref on 2026-11-21; the JMLR papers and the OSTI report at their URL)
    "storey2003": _ref("Storey & Tibshirani 2003", "Storey JD, Tibshirani R (2003). Statistical significance for genomewide studies. Proceedings of the National Academy of Sciences 100:9440-9445.", doi="10.1073/pnas.1530509100"),
    "storey2002": _ref("Storey 2002", "Storey JD (2002). A Direct Approach to False Discovery Rates. Journal of the Royal Statistical Society Series B: Statistical Methodology 64:479-498.", doi="10.1111/1467-9868.00346"),
    "efron2001": _ref("Efron et al. 2001", "Efron B, Tibshirani R, Storey JD, Tusher V (2001). Empirical Bayes Analysis of a Microarray Experiment. Journal of the American Statistical Association 96:1151-1160.", doi="10.1198/016214501753382129"),
    "hyndman2008auto": _ref("Hyndman & Khandakar 2008", "Hyndman RJ, Khandakar Y (2008). Automatic Time Series Forecasting: The forecast Package for R. Journal of Statistical Software 27(3).", doi="10.18637/jss.v027.i03"),
    "lumley2004": _ref("Lumley 2004", "Lumley T (2004). Analysis of Complex Survey Samples. Journal of Statistical Software 9(8).", doi="10.18637/jss.v009.i08"),
    "yates1934": _ref("Yates 1934", "Yates F (1934). Contingency Tables Involving Small Numbers and the χ2 Test. Supplement to the Journal of the Royal Statistical Society 1:217-235.", doi="10.2307/2983604"),
    "demsar2006": _ref("Demšar 2006", "Demšar J (2006). Statistical Comparisons of Classifiers over Multiple Data Sets. Journal of Machine Learning Research 7:1-30.", url="https://jmlr.org/papers/v7/demsar06a.html"),
    "benavoli2016": _ref("Benavoli et al. 2016", "Benavoli A, Corani G, Mangili F (2016). Should We Really Use Post-Hoc Tests Based on Mean-Ranks? Journal of Machine Learning Research 17(5):1-10.", url="https://jmlr.org/papers/v17/benavoli16a.html"),
    "conover1979": _ref("Conover & Iman 1979", "Conover WJ, Iman RL (1979). On multiple-comparisons procedures. Technical Report LA-7677-MS, Los Alamos Scientific Laboratory.", url="https://www.osti.gov/biblio/6057803"),
    # S3d-1: planning and surveys (each DOI looked up in Crossref on 2026-11-21)
    "schulz2002gen": _ref("Schulz & Grimes 2002a", "Schulz KF, Grimes DA (2002). Generation of allocation sequences in randomised trials: chance, not choice. The Lancet 359:515-519.", doi="10.1016/S0140-6736(02)07683-3"),
    "schulz2002conceal": _ref("Schulz & Grimes 2002b", "Schulz KF, Grimes DA (2002). Allocation concealment in randomised trials: defending against deciphering. The Lancet 359:614-618.", doi="10.1016/S0140-6736(02)07750-4"),
    "efird2011": _ref("Efird 2011", "Efird J (2011). Blocked Randomization with Randomly Selected Block Sizes. International Journal of Environmental Research and Public Health 8:15-20.", doi="10.3390/ijerph8010015"),
    "casler2015": _ref("Casler 2015", "Casler MD (2015). Fundamentals of Experimental Design: Guidelines for Designing Successful Experiments. Agronomy Journal 107:692-705.", doi="10.2134/agronj2013.0114"),
    "hurlbert1984": _ref("Hurlbert 1984", "Hurlbert SH (1984). Pseudoreplication and the Design of Ecological Field Experiments. Ecological Monographs 54:187-211.", doi="10.2307/1942661"),
    "lumley2010": _ref("Lumley 2010", "Lumley T (2010). Complex Surveys: A Guide to Analysis Using R. Wiley Series in Survey Methodology. Wiley.", doi="10.1002/9780470580066"),
    "korn1999": _ref("Korn & Graubard 1999", "Korn EL, Graubard BI (1999). Analysis of Health Surveys. Wiley Series in Probability and Statistics. Wiley.", doi="10.1002/9781118032619"),
    "woodruff1952": _ref("Woodruff 1952", "Woodruff RS (1952). Confidence Intervals for Medians and Other Position Measures. Journal of the American Statistical Association 47:635-646.", doi="10.1080/01621459.1952.10483443"),
    "rao1984": _ref("Rao & Scott 1984", "Rao JNK, Scott AJ (1984). On Chi-Squared Tests for Multiway Contingency Tables with Cell Proportions Estimated from Survey Data. The Annals of Statistics 12:46-60.", doi="10.1214/aos/1176346391"),
    "jamieson2004": _ref("Jamieson 2004", "Jamieson S (2004). Likert scales: how to (ab)use them. Medical Education 38:1217-1218.", doi="10.1111/j.1365-2929.2004.02012.x"),
    "norman2010": _ref("Norman 2010", "Norman G (2010). Likert scales, levels of measurement and the 'laws' of statistics. Advances in Health Sciences Education 15:625-632.", doi="10.1007/s10459-010-9222-y"),
    "heiberger2014": _ref("Heiberger & Robbins 2014", "Heiberger RM, Robbins NB (2014). Design of Diverging Stacked Bar Charts for Likert Scales and Other Applications. Journal of Statistical Software 57(5).", doi="10.18637/jss.v057.i05"),
    # S3d-3: Bayesian methods (each DOI looked up in Crossref on 2026-11-21)
    "rouder2009": _ref("Rouder et al. 2009", "Rouder JN, Speckman PL, Sun D, Morey RD, Iverson G (2009). Bayesian t tests for accepting and rejecting the null hypothesis. Psychonomic Bulletin & Review 16:225-237.", doi="10.3758/PBR.16.2.225"),
    "wagenmakers2018": _ref("Wagenmakers et al. 2018", "Wagenmakers EJ, Marsman M, Jamil T, Ly A, Verhagen J, Love J, Selker R, Gronau QF, Smira M, Epskamp S, Matzke D, Rouder JN, Morey RD (2018). Bayesian inference for psychology. Part I: Theoretical advantages and practical ramifications. Psychonomic Bulletin & Review 25:35-57.", doi="10.3758/s13423-017-1343-3"),
    "ly2016": _ref("Ly, Verhagen & Wagenmakers 2016", "Ly A, Verhagen J, Wagenmakers EJ (2016). Harold Jeffreys's default Bayes factor hypothesis tests: Explanation, extension, and application in psychology. Journal of Mathematical Psychology 72:19-32.", doi="10.1016/j.jmp.2015.06.004"),
    "gunel1974": _ref("Gunel & Dickey 1974", "Gunel E, Dickey J (1974). Bayes factors for independence in contingency tables. Biometrika 61:545-557.", doi="10.1093/biomet/61.3.545"),
    "jamil2017": _ref("Jamil et al. 2017", "Jamil T, Ly A, Morey RD, Love J, Marsman M, Wagenmakers EJ (2017). Default 'Gunel and Dickey' Bayes factors for contingency tables. Behavior Research Methods 49:638-652.", doi="10.3758/s13428-016-0739-8"),
    "vehtari2021": _ref("Vehtari et al. 2021", "Vehtari A, Gelman A, Simpson D, Carpenter B, Buerkner PC (2021). Rank-Normalization, Folding, and Localization: An Improved R-hat for Assessing Convergence of MCMC (with Discussion). Bayesian Analysis 16:667-718.", doi="10.1214/20-BA1221"),
    "gabry2019": _ref("Gabry et al. 2019", "Gabry J, Simpson D, Vehtari A, Betancourt M, Gelman A (2019). Visualization in Bayesian Workflow. Journal of the Royal Statistical Society Series A 182:389-402.", doi="10.1111/rssa.12378"),
    "gelman2008prior": _ref("Gelman et al. 2008", "Gelman A, Jakulin A, Pittau MG, Su YS (2008). A weakly informative default prior distribution for logistic and other regression models. The Annals of Applied Statistics 2:1360-1383.", doi="10.1214/08-AOAS191"),
    "kruschke2021": _ref("Kruschke 2021", "Kruschke JK (2021). Bayesian Analysis Reporting Guidelines. Nature Human Behaviour 5:1282-1291.", doi="10.1038/s41562-021-01177-7"),
}


# ---------------------------------------------------------------- the defaults, one entry per word or option
def _b(default, alternatives, why, refs=(), principle="P2", checks="", evidence="published") -> Basis:
    return Basis(default, alternatives, why, tuple(refs), principle, checks, evidence)


BASIS: dict[str, Basis] = {}

# ---- Charts
BASIS["draw_bars"] = _b(
    "Bars of the average with no error bars, unless error= asks for them.",
    "error=\"standard deviation\", \"standard error\" or \"confidence interval\"; show= for another summary; "
    "draw_all_dots() to show every value.",
    "A bar of averages hides the spread and is often misread (Weissgerber et al. 2015; Newman & Scholl 2012), and "
    "readers confuse the kinds of error bar (Belia et al. 2005; Cumming et al. 2007). So simplydata draws no "
    "interval it was not asked for (seaborn's own default is a bootstrap interval that changes from run to run), "
    "and names in a printed line the error bars it does draw. Leaving them out until asked is simplydata's own "
    "choice.",
    ("weissgerber2015", "newman2012", "belia2005", "cumming2007"), "P5",
    "error= works only with show=\"average\"; a printed line says which error bars were drawn.", "starting value")
BASIS["show="] = _b(
    "The average of each group (show=\"average\").",
    "show=\"median\", \"total\", \"count\" (bars only), \"smallest\", \"biggest\", \"standard deviation\".",
    "The average is what seaborn and most papers draw; the other summaries are one word away. A bar of averages "
    "alone hides the data (Weissgerber et al. 2015), so the manual pairs it with draw_all_dots().",
    ("weissgerber2015",), "P3",
    "draw_lines refuses show=\"count\"; draw_bars without y= needs show=\"count\".", "convention")
BASIS["error="] = _b(
    "No error bars or band unless you ask; when you ask for the confidence interval, it is the 95 % t interval "
    "of the average (as R t.test()), not seaborn's bootstrap.",
    "error=\"standard deviation\" (the spread of the values), \"standard error\", \"confidence interval\".",
    "Researchers misread error bars when the kind is not said (Belia et al. 2005), and every figure should say "
    "which bars it shows (Cumming et al. 2007). simplydata prints the kind for the caption, and its t interval "
    "does not change from run to run. Having no default kind is simplydata's own choice: you must name one.",
    ("belia2005", "cumming2007"), "P5",
    "Refused with a summary other than the average, on stacked bars, and on lines that are not joined straight.",
    "starting value")
BASIS["draw_histogram"] = _b(
    "10 bins of equal width, counts on the y axis.",
    "with_bins= (a number or the edges), bin_width=, show=\"percent\" or \"density\".",
    "Ten bins is a fixed, predictable starting value, so the same data always give the same picture. The "
    "published rules choose the number of bins from the data instead (Sturges 1926; Scott 1979; Freedman & "
    "Diaconis 1981), as seaborn's own default does.",
    ("sturges1926", "scott1979", "freedman1981"), "P5",
    "with_bins= and bin_width= together are refused; more than 1000 bars are refused.", "starting value")
BASIS["draw_boxes"] = _b(
    "Tukey's box plot (seaborn boxplot): the box from the first to the third quartile, whiskers to the last value "
    "within 1.5 x IQR of the box, dots beyond.",
    "draw_violins() or draw_all_dots(); there is no option for other whiskers.",
    "The 1.5 x IQR whisker is Tukey's own rule (Exploratory Data Analysis, 1977), the one R boxplot(), seaborn and "
    "most software draw; McGill, Tukey & Larsen 1978 and Frigge, Hoaglin & Iglewicz 1989 describe the variants in "
    "use.",
    ("mcgill1978", "frigge1989"), "P3", "", "convention")
BASIS["draw_violins"] = _b(
    "A Gaussian density with Scott's bandwidth (seaborn's default), cut at the smallest and largest value, with a "
    "small box inside.",
    "draw_boxes() or draw_all_dots(); there is no option for the bandwidth.",
    "The violin plot is a box plot with a density trace (Hintze & Nelson 1998); Scott's rule is the default "
    "bandwidth of seaborn and SciPy (Scott 1992). Cutting at the data keeps the violin from showing impossible "
    "values, such as marks below 0.",
    ("hintze1998", "scott1992"), "P3", "", "convention")
BASIS["draw_density"] = _b(
    "A Gaussian kernel density with Scott's bandwidth (seaborn's default); each group's curve has area 1.",
    "draw_histogram(show=\"density\"); there is no option for the bandwidth.",
    "Scott's rule is the default of seaborn and SciPy (Scott 1992); R uses Silverman's. Both are rules of thumb "
    "made for bell-shaped data (Silverman 1986). The curve runs a little past the data (seaborn's cut=3), unlike "
    "draw_violins().",
    ("scott1992", "silverman1986"), "P3", "x must hold numbers.", "convention")
BASIS["draw_all_dots"] = _b(
    "Every value as a dot: a swarm (no overlap) when the biggest group has 100 values or fewer, else dots spread "
    "at random (fixed seed) and half transparent.",
    "Put draw_boxes() or draw_violins() underneath; the dots then turn dark grey.",
    "Showing every value is the recommendation of Weissgerber et al. 2015 for small samples; above 100 values a "
    "swarm no longer fits. The fixed seed keeps the picture the same each time.",
    ("weissgerber2015",), "P2", "")
BASIS["draw_error_bars"] = _b(
    "Bars of the standard deviation (of_kind=\"standard deviation\") around the average at each x, groups moved "
    "a little apart.",
    "of_kind=\"standard error\" or \"confidence interval\" (95 % t interval); column= for your own sizes; "
    "dodge=False.",
    "The standard deviation describes the spread of the values; the kind is always printed, so the caption can "
    "say it (Cumming et al. 2007). error= on draw_bars has no default, while this word draws the standard "
    "deviation unless told otherwise.",
    ("cumming2007", "belia2005"), "P5",
    "Needs dots or lines first, at least 2 values per x (else column=), and no negative sizes.", "starting value")
BASIS["fit_line"] = _b(
    "A least-squares straight line over the range of the data; no band unless with_confidence_band=True (then "
    "the 95 % band of the average y, as R predict(lm, interval = \"confidence\")).",
    "with_confidence_band=True, show_equation=True; table.fit_line(test_method=...) for other lines.",
    "Least squares answers 'predict y from x', the usual question, and the band is the one R draws. Lines that "
    "treat x and y alike (Warton et al. 2006) are in table.fit_line(test_method=).",
    ("warton2006",), "P3", "Only after dots; x and y must be numbers with at least 2 different x.", "convention")
BASIS["fit_curve"] = _b(
    "A polynomial of degree 2 by least squares (as R lm(y ~ poly(x, 2, raw = TRUE))).",
    "of_degree= 1 to 10; fit_formula() for any formula.",
    "Degree 2 is the smallest curve that bends once. No study fixes the degree: it is a starting value, and "
    "table.fit_curve warns from degree 4, where polynomials wiggle at the ends.",
    (), "P5", "Needs at least degree + 1 different x.", "starting value")
BASIS["fit_formula"] = _b(
    "Nonlinear least squares by Levenberg-Marquardt (as minpack.lm::nlsLM(); R nls()'s Gauss-Newton gives the same "
    "estimates when both converge), with Wald t intervals for each value, as summary(nls).",
    "As table.fit_formula: test_method=, search=\"whole range\", between=.",
    "Least squares is what R nls() fits. The Wald intervals rest on a straight-line approximation; for strongly "
    "curved models Bates & Watts 1988 prefer profile-likelihood intervals, which R confint() gives and simplydata "
    "does not yet offer.",
    ("bates1988",), "P3", "The left side must be the y of the dots, and only x may appear on the right.",
    "convention")
BASIS["fit_distribution"] = _b(
    "The normal distribution fitted by maximum likelihood (as R MASS::fitdistr()), scaled to the histogram.",
    "distribution= any name of sdata.distribution.",
    "Maximum likelihood is the standard way to fit a distribution (Venables & Ripley 2002; Delignette-Muller & "
    "Dutang 2015); a note says how the curve was scaled to counts.",
    ("venables2002", "delignette2015"), "P3", "Only after a histogram or density; at least 2 values.",
    "convention")
BASIS["draw_smooth_line"] = _b(
    "LOWESS as R lowess(): the nearest 2/3 of the dots, 3 robustness steps.",
    "test_method=\"loess\" (R loess, with a confidence band), \"spline\" (R smooth.spline), or a moving average and the "
    "other window methods.",
    "LOWESS is Cleveland's robust local regression (Cleveland 1979) and R's lowess() default; its robustness "
    "steps keep a single outlier from pulling the line.",
    ("cleveland1979",), "P3",
    "A number for smoothness= with LOWESS is refused; with_confidence_band= needs test_method=\"loess\"; window methods "
    "need evenly spaced x.", "convention")
BASIS["draw_qq_dots"] = _b(
    "Against the normal distribution (SciPy probplot): dots at Filliben's positions, and the line by least "
    "squares through the dots.",
    "distribution= any name (fitted by maximum likelihood first); for_each_group_in=.",
    "The Q-Q plot is Wilk & Gnanadesikan's way to compare data with a distribution; Filliben's positions are "
    "SciPy's (Filliben 1975). R's qqnorm() uses slightly different positions and qqline() a line through the "
    "quartiles, which the help says.",
    ("wilk1968", "filliben1975"), "P3", "Fewer than 3 values are refused (a group is left out, with a note).",
    "convention")
BASIS["draw_side_histograms"] = _b(
    "Bins from NumPy's 'auto' rule (the larger of Sturges' and Freedman-Diaconis' numbers), at most 50, the same "
    "edges for every group.",
    "There is no option for the bins here.",
    "The 'auto' rule chooses the number of bins from the data (Sturges 1926; Freedman & Diaconis 1981).",
    ("sturges1926", "freedman1981"), "P3", "", "convention")
BASIS["sdata.draw_all_pairs"] = _b(
    "Dots for each pair of columns; on the diagonal a histogram with seaborn's own bins, or with colour= a "
    "density with Scott's bandwidth.",
    "columns= chooses up to 10 columns.",
    "seaborn pairplot's own choices (Scott 1992 for the bandwidth).",
    ("scott1992",), "P3", "Fewer than 2 or more than 10 number columns are refused.", "convention")
BASIS["draw_heatmap"] = _b(
    "viridis colours; when the values lie on both sides of 0, a blue-to-red scale centred at 0. Repeated cells are "
    "averaged; cluster=True uses average linkage on Euclidean distances.",
    "use_colour_scale() for another scale; cluster=True.",
    "viridis shows equal steps in the data as equal steps in lightness and reads in grey and with colour "
    "blindness (Nuñez et al. 2018; Crameri et al. 2020); a diverging scale centred on a meaningful middle is the "
    "ColorBrewer advice (Harrower & Brewer 2003). The clustering is seaborn clustermap's own choice.",
    ("nunez2018", "crameri2020", "harrower2003"), "P2",
    "cluster=True with empty cells, or with fewer than 2 rows or columns, is refused.")
BASIS["use_colours"] = _b(
    "The Okabe-Ito colours for groups (blue, orange, green, vermilion, reddish purple, sky blue, yellow, black).",
    "use_colours(\"a\", \"b\", ...) for your own; use_colour() for one colour.",
    "Readers with colour blindness can tell the Okabe-Ito colours apart, and they stay distinct in print (Okabe & "
    "Ito 2008; Wong 2011).",
    ("okabe2008", "wong2011"), "P1", "With more groups than colours the colours repeat, and a note says so (once).")
BASIS["use_colour_scale"] = _b(
    "viridis for numbers; with middle=, a blue-to-red scale (RdBu) with the same change of colour per unit on "
    "both sides.",
    "Any named scale (cividis, magma, blues ...), your own colours, log=True, steps=, between=.",
    "Rainbow scales distort the data and fail with colour blindness; perceptually uniform scales such as viridis "
    "and cividis do not (Liu & Heer 2018; Nuñez et al. 2018; Crameri et al. 2020). Diverging scales belong to data "
    "with a meaningful middle (Harrower & Brewer 2003).",
    ("liu2018", "nunez2018", "crameri2020", "harrower2003"), "P2",
    "log=True with values at or below 0 is refused; middle= with log= or steps= is refused; an unknown name is "
    "refused with a list of colour-blind-safe scales; a rainbow scale (jet, rainbow, hsv ...) gets a note (once).")
BASIS["draw_interaction_lines"] = _b(
    "The average of each group joined by lines, with 95 % t intervals (as R t.test()), groups moved a little "
    "apart.",
    "table.explain(using=[..., ...]) and table.find_model_averages_of(within_each_group_in=) for the test.",
    "seaborn's own default is a bootstrap interval that changes from run to run; the t interval is the one R and "
    "most textbooks give. The picture is printed with the reminder to test the interaction, not read it by eye.",
    ("gelman2006",), "P3",
    "y must hold numbers; x and colour need 2 to 12 groups each (more: add_group_column or fit_line).", "convention")

# ---- Tables: rows, empty cells, columns
BASIS["table.keep_rows_where"] = _b(
    "is_above= means strictly above (>); rows with an empty cell in the column are left out, as pandas and Polars "
    "do.",
    "is_at_least= for >=; the other conditions (is_below=, is_between= ...).",
    "The words say exactly which comparison is made; leaving out empty cells is what pandas, Polars and R's "
    "subset() do.",
    (), "P3", "", "convention")
BASIS["table.show_rows_with_outliers"] = _b(
    "Tukey's rule: values more than 1.5 x IQR below the first or above the third quartile (quartiles as R "
    "quantile(type = 7)), within each group when asked.",
    "test_method=\"3 IQR\" (any k IQR), \"3 standard deviations\" (any k), or a test: \"grubbs\", \"dixon\", "
    "\"rosner\" (run in R).",
    "Tukey's fences are the box-plot rule and are not pulled by the outliers themselves, unlike a rule of k "
    "standard deviations. They flag about 0.7 % of clean bell-shaped values, so in a sample of 100 one value is "
    "often flagged (Hoaglin, Iglewicz & Tukey 1986); Hoaglin & Iglewicz 1987 suggest k = 2.2 for labelling, and "
    "Leys et al. 2013 the median plus or minus 2.5 MAD. The rule shows rows to look at, not rows to remove.",
    ("hoaglin1986", "hoaglin1987", "leys2013"), "P3",
    "Refused for non-number columns. A k-SD rule that no value could reach with n values is flagged; the tests "
    "warn that they assume bell-shaped data and skip groups with fewer than 3 values.", "convention")
BASIS["table.remove_rows_with_outliers"] = _b(
    "The same rule as show_rows_with_outliers: Tukey's 1.5 x IQR fences.",
    "test_method= as show_rows_with_outliers.",
    "As show_rows_with_outliers. ICH E9 asks that outlier handling be decided in advance and that results be "
    "reported with and without the values; simplydata names every row it removes, so that both analyses can be "
    "run. With 1.5 x IQR, clean values are removed too in larger samples (Hoaglin & Iglewicz 1987).",
    ("hoaglin1986", "hoaglin1987", "ich_e9"), "P3", "As show_rows_with_outliers; the removed rows are printed.",
    "convention")
BASIS["table.add_z_score_column"] = _b(
    "(value - average) / standard deviation with n - 1, as R scale(); within each group when asked.",
    "There is no other kind of standard deviation here.",
    "The n - 1 standard deviation is the sample standard deviation that R, pandas and the GUM use.",
    ("gum2008",), "P3", "A group with fewer than 2 values gets empty z-scores.", "convention")

# ---- Summaries
BASIS["table.find_average_of"] = _b(
    "Groups stay in the order they first appear; empty cells are skipped, as pandas and Polars do. interval= "
    "gives the t interval, as R t.test().",
    "sorted_by= to sort; interval= for the interval; weights= for a weighted average.",
    "Skipping empty cells and saying how many were skipped is what pandas, Polars and R's mean(na.rm = TRUE) do; "
    "NumPy would give nan. The t interval of the average is Student's (Student 1908), the interval of R t.test().",
    ("student1908",), "P3", "A note gives how many empty cells were skipped; one value gives no interval.",
    "convention")
BASIS["table.find_median_of"] = _b(
    "The middle value; interval= gives the exact interval from the order statistics (as R "
    "DescTools::MedianCI(method = \"exact\")).",
    "interval= sets the level.",
    "The order-statistic interval of the median needs no assumption about the shape of the data (Campbell & "
    "Gardner 1988).",
    ("campbell1988",), "P2", "With few values one end of the interval can be empty, which is said.")
BASIS["nums.find_median"] = _b(
    "The middle value, empty values skipped (np.nanmedian); NumPy's np.median would give nan.",
    "remove_empty_numbers() first if you want them gone for later steps too.",
    "Skipping empty values and saying so is what pandas and R's median(na.rm = TRUE) do.",
    (), "P3", "", "convention")
BASIS["table.find_standard_deviation_of"] = _b(
    "The sample standard deviation, dividing by n - 1, as pandas and R sd(); interval= gives the chi-square "
    "interval (R DescTools::VarCI).",
    "weights= with weight_kind=\"frequency\" (default) or \"analytic\".",
    "The n - 1 form is the experimental standard deviation of the GUM and the default of R and pandas; NumPy's "
    "default divides by n. The chi-square interval follows DescTools and holds only for bell-shaped values, which "
    "the help says; Bonett 2006 gives an interval that does not need a bell shape.",
    ("gum2008", "bonett2006"), "P1",
    "Negative weights are refused; a group with total weight of 1 or less gets an empty value.")
BASIS["table.find_percentile_of"] = _b(
    "Linear interpolation between the values (test_method=\"linear\", R quantile(type = 7)), the default of R, NumPy "
    "and pandas; interval= gives the exact order-statistic interval.",
    "test_method= 1 to 9 (Hyndman & Fan's types) or a NumPy method name; weights= with weight_kind=.",
    "Type 7 is the shared default of R, NumPy and pandas, so results match theirs. Hyndman & Fan 1996, who "
    "compared the nine definitions, recommend type 8; SPSS and Minitab use type 6. The help names both.",
    ("hyndman1996",), "P3", "percent= outside 0 to 100 is refused; interval= works with test_method=\"linear\" only.",
    "convention")
BASIS["table.find_summary_of"] = _b(
    "Count, average, standard deviation (n - 1), smallest, median, biggest. When asked: skewness G1 and excess "
    "kurtosis G2 (the adjusted forms of SAS, SPSS and R e1071 type 2), the MAD scaled by 1.4826 (as R mad()), a 10 "
    "% trimmed average, a 20 % winsorised average.",
    "show= chooses the measures (and the trimmed and winsorised shares).",
    "Joanes & Gill 1998 compare the skewness and kurtosis formulas in use; the 1.4826 factor makes the MAD estimate "
    "the standard deviation of bell-shaped data (Rousseeuw & Croux 1993). The 10 % trimmed share is simplydata's "
    "starting value (R's mean() trims nothing unless asked); Wilcox & Keselman 2003 recommend 20 % for both "
    "trimmed and winsorised averages.",
    ("joanes1998", "rousseeuw1993", "wilcox2003"), "P3",
    "Skewness needs 3 values and kurtosis 4; a trimmed share of 50 % or more is refused.", "convention")
BASIS["table.find_percent_of_rows_where"] = _b(
    "The exact (Clopper-Pearson) 95 % interval, as R binom.test(); rows with an empty cell are left out of the "
    "count, with a note.",
    "interval_by=\"wilson\" or \"agresti-coull\".",
    "The exact interval never covers less than 95 % and is the one R binom.test() prints. Method comparisons find "
    "it wider than needed and prefer Wilson's or Agresti-Coull's interval (Agresti & Coull 1998; Brown, Cai & "
    "DasGupta 2001), which interval_by= gives.",
    ("clopper1934", "wilson1927", "agresti1998", "brown2001"), "P3", "Empty cells are counted and left out, with "
    "a note.", "convention")
BASIS["table.count_each"] = _b(
    "With interval=: Sison and Glaz's simultaneous intervals for all the shares at once (as R "
    "DescTools::MultinomCI).",
    "interval= sets the level.",
    "Separate intervals for each share would together cover less than 95 %; Sison & Glaz 1995 give intervals that "
    "cover all the shares together. May & Johnson 2000 found them good with many groups and small counts, and "
    "Goodman's intervals better with few groups and large counts.",
    ("sison1995", "may2000"), "P2", "Fewer than 2 values are refused.")
BASIS["table.find_interval_of"] = _b(
    "A BCa bootstrap interval (bias-corrected and accelerated) from 9999 resamples, seed 1, as R "
    "boot::boot.ci(type = \"bca\").",
    "test_method=\"percentile bootstrap\" or \"reverse percentile bootstrap\"; resamples=, with_seed=.",
    "BCa intervals are second-order accurate and correct for bias and skew, where the simple percentile interval "
    "is not (Efron 1987; DiCiccio & Efron 1996). The seed makes the answer repeat.",
    ("efron1987", "diciccio1996", "hesterberg2015"), "P2",
    "Fewer than 2 values per group, a seed that is not a whole number and fewer than 99 resamples are refused; "
    "below 20 values a note says the interval is often too narrow (Hesterberg 2015); when BCa cannot be worked "
    "out the note names the percentile bootstrap.")
BASIS["table.find_correlation_between"] = _b(
    "Pearson's r with its 95 % interval (Fisher's z, SciPy) and a two-sided p-value; the strength in words "
    "(below 0.2 very weak ... 0.8 and above very strong).",
    "test_method=\"spearman\" (Fisher-z interval, DescTools::SpearmanRho), \"kendall\" (tau-b, asymptotic "
    "interval), \"somers\", \"gamma\"; allowing_for= (partial correlation); p_value_by=\"shuffling\"; "
    "interval_by=\"bootstrap\".",
    "Pearson's r is the usual measure of a straight-line link and its Fisher-z interval the usual interval (Fisher "
    "1915 for the distribution of r). Bonett & Wright 2000 propose a better standard error for Spearman's rho "
    "than the plain Fisher-z one used here. The strength words are a textbook scale chosen by simplydata; scales "
    "differ between fields (Schober et al. 2018), so the number is always printed with the words.",
    ("fisher1915", "bonett2000", "schober2018"), "P3",
    "Fewer than 3 complete rows and constant columns are refused; with 3 or more columns the p-values are not "
    "adjusted, and a note points to add_adjusted_p_value_column.", "convention")

# ---- Statistical tests
BASIS["table.compare_averages_of"] = _b(
    "Two groups: Welch's t-test, which does not assume both groups have the same spread. Three or more: Welch's "
    "one-way ANOVA (as R oneway.test()). Effect sizes: Hedges' g with the pooled standard deviation (as R "
    "effectsize::hedges_g()), or omega squared from the classic ANOVA.",
    "test_method=\"student\", \"anova\", \"yuen\", \"brunner-munzel\", \"alexander-govern\", \"median\", "
    "\"jonckheere\"; based_on=\"ranks\" (Mann-Whitney, Kruskal-Wallis).",
    "Welch's test keeps its error rate when the spreads differ and loses almost nothing when they are equal, so it "
    "is recommended as the default, without a preliminary test of the spreads (Welch 1947; Zimmerman 2004; "
    "Ruxton 2006; Delacre et al. 2017); the same holds for Welch's F against the classic ANOVA (Welch 1951; Delacre "
    "et al. 2019). The pooled-SD Hedges' g is approximate when the spreads differ; omega squared is much less "
    "biased than eta squared (Okada 2013; Albers & Lakens 2018).",
    ("welch1947", "zimmerman2004", "ruxton2006", "delacre2017", "welch1951", "delacre2019", "lakens2013",
     "okada2013", "albers2018", "rochon2012"), "P2",
    "Fewer than 2 values in a group or no spread at all is refused; one-sided tests with 3 or more groups are "
    "refused. A Shapiro-Wilk note per group suggests based_on=\"ranks\" for small, clearly skewed groups; it never "
    "switches the test, because choosing the test from a normality pre-test distorts the error rate (Rochon, "
    "Gondan & Kieser 2012).")
BASIS["table.compare_averages_of based_on="] = _b(
    "Mann-Whitney U for two groups (exact p-value below 50 values per group without ties, else the normal "
    "approximation with continuity correction, as R wilcox.test()), with the Hodges-Lehmann shift; Kruskal-Wallis "
    "for three or more.",
    "based_on=\"averages\" (the default, Welch).",
    "Rank tests need no bell shape, but they compare more than the medians, and are not robust to unequal "
    "spreads (Fagerland & Sandvik 2009; Fay & Proschan 2010): that is why they are an option, not the default.",
    ("mann1947", "kruskal1952", "hodges1963", "fagerland2009", "fay2010"), "P3",
    "test_method= must then be a rank test.", "convention")
BASIS["table.compare_averages_of p_value_by="] = _b(
    "The p-value from 9999 random shuffles of the group labels (seed 1), exact when there are fewer arrangements "
    "than that; two-sided p twice the smaller side, as R perm::permTS().",
    "shuffles=, with_seed=.",
    "A permutation test needs only that the group labels could be swapped under the null hypothesis (Ernst 2004). "
    "9999 shuffles and seed 1 are simplydata's starting values; the seed makes the answer repeat.",
    ("ernst2004",), "P5", "Two groups and the Welch or Student test only; fewer than 99 shuffles are refused.",
    "starting value")
BASIS["table.compare_averages_of same_within="] = _b(
    "Two one-sided tests (TOST) with Welch's t, the larger p-value counting, with the 90 % interval (as R "
    "TOSTER::t_TOST()).",
    "not_lower= or not_higher= for non-inferiority.",
    "'No evidence of a difference' is not evidence of no difference; the TOST procedure tests equivalence directly "
    "(Schuirmann 1987; Lakens 2017), and Welch's form keeps it valid when the spreads differ (statsmodels' own "
    "default pools them).",
    ("schuirmann1987", "lakens2017"), "P2", "The margin must lie on both sides of 0; two groups only.")
BASIS["table.compare_averages_of matched_by="] = _b(
    "Repeated-measures ANOVA with the Greenhouse-Geisser correction and Mauchly's test (R afex::aov_ez(), whose "
    "default this is).",
    "table.explain(grouped_by=) for a mixed model; compare_matched_columns() for a rank test on columns.",
    "Repeated measurements on the same subject are not independent, and a sphericity correction keeps the error "
    "rate (Greenhouse & Geisser 1959). The Greenhouse-Geisser correction is conservative when sphericity is nearly "
    "met; Haverkamp & Beauducel 2017 found the Huynh-Feldt correction (Huynh & Feldt 1976) better, which "
    "simplydata does not yet offer.",
    ("greenhouse1959", "huynh1976", "haverkamp2017"), "P3",
    "Refused with based_on=, test_method=, sides=, p_value_by=, same_within=.", "convention")
BASIS["table.compare_averages_of grouped_by="] = _b(
    "Nested ANOVA: the treatment is tested against the variation between the units (Error(rat)), not between "
    "readings.",
    "table.explain(grouped_by=) for a mixed model.",
    "Readings of one unit are not independent; testing them as if they were is pseudoreplication (Hurlbert 1984).",
    ("hurlbert1984",), "P2",
    "Units that are not nested in one group, units with one row and fewer than 2 units per group are refused; an "
    "unbalanced design gets a note pointing to a mixed model.")
BASIS["table.compare_averages_of for_each_group_in= with a list of columns"] = _b(
    "MANOVA with Pillai's trace first, as R summary(manova()).",
    "The other three statistics stay in the table.",
    "Pillai's trace is the most robust of the four MANOVA statistics when groups differ in size or spread (Olson "
    "1974, 1976).",
    ("olson1974", "olson1976"), "P2", "Groups with no more rows than columns, and rank deficiency, are refused.")
BASIS["table.compare_each_pair_of"] = _b(
    "Each pair by Welch's t-test, the p-values adjusted with Holm's method (as R pairwise.t.test(pool.sd = FALSE, "
    "p.adjust.method = \"holm\")).",
    "test_method=\"tukey\" (Tukey-Kramer), \"games-howell\", \"scheffe\", \"lsd\", \"dunn\", \"conover\"; "
    "based_on=\"ranks\" or \"percents\"; against= (Dunnett); show=\"letters\".",
    "Holm's method keeps the chance of any false alarm at 5 % and is uniformly more powerful than Bonferroni (Holm "
    "1979; Aickin & Gensler 1996); multiplicity should be adjusted for and the method named (Bender & Lange 2001; "
    "ICH E9). Welch's test per pair keeps the error rate when spreads differ; it gives no simultaneous intervals, "
    "which Games & Howell's procedure does (test_method=\"games-howell\"; Games & Howell 1976). Tukey-Kramer (Kramer "
    "1956) and Dunn's test (Dunn 1964) are options.",
    ("holm1979", "aickin1996", "bender2001", "ich_e9", "games1976", "kramer1956", "dunn1964"), "P1",
    "A pair where both groups have no spread is refused; Tukey prints a note when the largest spread is more than "
    "twice the smallest.")
BASIS["table.compare_each_pair_of against="] = _b(
    "Dunnett's test: each group against the one named, with simultaneous intervals (SciPy stats.dunnett, seeded).",
    "Leave out against= for all pairs.",
    "Dunnett's procedure compares several treatments with one control and keeps the family error rate (Dunnett "
    "1955).",
    ("dunnett1955",), "P2", "Refused with test_method=, based_on= or show=\"letters\".")
BASIS["table.compare_before_and_after"] = _b(
    "Numbers: the paired t-test with Cohen's d_z. Yes/no: McNemar's test with continuity correction (as R "
    "mcnemar.test()). Three or more kinds: Bowker's test of symmetry. Chosen from the kind of column.",
    "based_on=\"ranks\" (Wilcoxon signed-rank), test_method=\"sign\", p_value_by=\"exact\" (exact McNemar), "
    "p_value_by=\"shuffling\", same_within=.",
    "The paired t-test uses the changes within each subject. McNemar's test with continuity correction is R's "
    "default; Fagerland, Lydersen & Laake 2013 found the uncorrected asymptotic and mid-p tests better, and the "
    "exact test conservative.",
    ("mcnemar1947", "bowker1948", "fagerland2013", "wilcoxon1945"), "P3",
    "Fewer than 2 rows, the same column twice, or no change at all are refused; a Shapiro-Wilk note on the "
    "changes; one-sided McNemar and Bowker are refused.", "convention")
BASIS["table.compare_average_to"] = _b(
    "The one-sample t-test with Cohen's d.",
    "based_on=\"ranks\" (Wilcoxon signed-rank); test_method=\"z\" with standard_deviation=; same_within=.",
    "The one-sample t-test is the standard test of an average against a value (Student 1908).",
    ("student1908",), "P3", "A value that is not a finite number and fewer than 2 values are refused.", "convention")
BASIS["table.compare_counts_of"] = _b(
    "The chi-square test of independence, with Yates' continuity correction for 2 x 2 tables only (as R "
    "chisq.test()); Cramér's V.",
    "test_method=\"fisher\", \"g\", \"barnard\", \"boschloo\", \"trend\"; p_value_by=\"shuffling\" or "
    "\"exact\"; show=\"cells\".",
    "simplydata matches R chisq.test() so that results agree with R. The evidence on small tables favours other "
    "choices: Campbell 2007 recommends the 'N - 1' chi-square without Yates' correction (and Fisher's test when an "
    "expected count is below 1), and Yates' correction is conservative (Haviland 1990). Cochran 1954's rule is no "
    "expected count below 1 and at most 20 % below 5; simplydata's note is stricter.",
    ("cochran1954", "campbell2007", "haviland1990"), "P3",
    "A row or column of zeros is refused; when an expected count is below 5, a note suggests test_method=\"fisher\" or "
    "p_value_by=\"shuffling\" (never a silent switch).", "convention")
BASIS["sdata.compare_counts"] = _b(
    "The same test as table.compare_counts_of, from a table of counts.",
    "As table.compare_counts_of.",
    "As table.compare_counts_of.",
    ("cochran1954", "campbell2007"), "P3", "As table.compare_counts_of.", "convention")
BASIS["table.compare_counts_to"] = _b(
    "The chi-square goodness-of-fit test, against equal shares unless expected= gives them; Cohen's w.",
    "expected= the shares you expect.",
    "The goodness-of-fit chi-square is the standard test of counts against expected shares. Cochran 1954 asks that "
    "no expected count be below 1 and at most 20 % below 5; simplydata's note, at any expected count below 5, is "
    "stricter.",
    ("cochran1954",), "P3",
    "Shares at or below 0 and totals other than 1 or 100 are refused; expected counts below 5 get a note "
    "(compare_percent_to for two values, or merge small groups).", "convention")
BASIS["table.compare_percent_to"] = _b(
    "The exact binomial test (as R binom.test()), with the exact (Clopper-Pearson) interval and Cohen's h.",
    "interval_by=\"wilson\" or \"agresti-coull\".",
    "The exact test is valid at any size. The exact interval is conservative; Agresti & Coull 1998 and Brown, Cai "
    "& DasGupta 2001 prefer Wilson's or Agresti-Coull's, which interval_by= gives.",
    ("clopper1934", "agresti1998", "brown2001"), "P3",
    "percent= must lie between 0 and 100; below 1 a note asks whether you meant a share.", "convention")
BASIS["table.add_adjusted_p_value_column"] = _b(
    "Holm's method (as R p.adjust(method = \"holm\")).",
    "test_method=\"bonferroni\", \"benjamini-hochberg\", \"benjamini-yekutieli\", \"hochberg\", \"hommel\"; "
    "\"storey\" (q-values) and \"local fdr\" (R qvalue).",
    "Holm's method controls the chance of any false alarm, like Bonferroni, but is uniformly more powerful (Holm "
    "1979; Aickin & Gensler 1996); it is R's default. Benjamini-Hochberg controls the share of false alarms "
    "instead, for screening many tests (Benjamini & Hochberg 1995).",
    ("holm1979", "aickin1996", "benjamini1995", "bender2001"), "P2",
    "p-values outside 0 to 1 are refused; empty p-values stay empty and are not counted.")
BASIS["table.compare_spreads_of"] = _b(
    "Levene's test centred on the median (the Brown-Forsythe form), as R car::leveneTest().",
    "test_method=\"bartlett\", \"fligner\"; for two groups \"ansari\", \"mood\", \"f\".",
    "In Conover, Johnson & Johnson's comparison of 56 tests, the median-centred Levene test was among the few that "
    "kept their error rate without a bell shape (Brown & Forsythe 1974; Conover et al. 1981); Bartlett's test "
    "does not.",
    ("brown1974", "conover1981"), "P2",
    "No spread in every group is refused; Bartlett gets a note when a group is not bell-shaped.")
BASIS["table.compare_shape_to"] = _b(
    "Against the normal distribution: the Shapiro-Wilk test (as R shapiro.test()). Against another named shape: "
    "the Anderson-Darling test with a parametric-bootstrap p-value (9999 samples, seed 1).",
    "test_method=\"lilliefors\", \"dagostino\", \"jarque-bera\"; a distribution object (Kolmogorov-Smirnov or "
    "Cramér-von Mises).",
    "Shapiro-Wilk is among the most powerful normality tests against most alternatives (Shapiro & Wilk 1965; Yap & "
    "Sim 2011). With estimated parameters the Anderson-Darling table p-values do not hold (Stephens 1974), so the "
    "p-value comes from a parametric bootstrap (Stute, González Manteiga & Presedo Quindimil 1993).",
    ("shapiro1965", "yap2011", "stephens1974", "stute1993"), "P2",
    "Each test's smallest size is checked; Shapiro-Wilk above 5000 values is refused; with 30 or more values a "
    "note says the test flags even harmless differences.")
BASIS["table.compare_shapes_of"] = _b(
    "Two groups: the two-sample Kolmogorov-Smirnov test (exact below 10000 pairs, as R ks.test()). Three or "
    "more: the k-sample Anderson-Darling test with a permutation p-value (9999, seed 1).",
    "shuffles=, with_seed=.",
    "Kolmogorov-Smirnov is the standard test of two whole distributions and matches R ks.test() (Massey 1951). "
    "The k-sample Anderson-Darling test (Scholz & Stephens 1987) also works for two groups and is usually more "
    "powerful, especially in the tails; simplydata keeps Kolmogorov-Smirnov for two groups to match R.",
    ("massey1951", "scholz1987"), "P3", "Fewer than 99 shuffles are refused.", "convention")
BASIS["table.check_if_random_order"] = _b(
    "The runs test about the median, without continuity correction (as R randtests::runs.test()); values equal "
    "to the median are dropped and counted.",
    "sorted_by= for the order.",
    "The runs test asks whether values above and below the middle alternate as often as chance would make them "
    "(Wald & Wolfowitz 1940; Swed & Eisenhart 1943 for the one-sample form).",
    ("wald1940", "swed1943"), "P3", "Fewer than 3 values, or no values on one side of the median, are refused.",
    "convention")
BASIS["table.compare_matched_columns"] = _b(
    "Friedman's test with Kendall's W; for yes/no columns Cochran's Q; two columns go to compare_before_and_after.",
    "test_method=\"quade\" or \"page\"; compare_averages_of(matched_by=) for repeated-measures ANOVA on averages.",
    "Friedman's rank test compares several measurements on the same subjects without a bell shape (Friedman "
    "1937); Cochran's Q is its form for yes/no answers (Cochran 1950). For a comparison of averages in long "
    "format, compare_averages_of(matched_by=) gives repeated-measures ANOVA.",
    ("friedman1937", "cochran1950"), "P3", "Text with more than 2 values and fewer than 2 rows are refused.",
    "convention")
BASIS["table.compare_correlations"] = _b(
    "Two groups: Fisher's z test with Zou's interval of the difference. Two correlations sharing a column in one "
    "sample: Steiger's z (R cocor).",
    "There is no other test here.",
    "Steiger 1980 gives the tests for correlations from the same sample; Zou 2007 gives intervals for the "
    "difference; cocor implements both (Diedenhofen & Musch 2015).",
    ("steiger1980", "zou2007", "diedenhofen2015"), "P2",
    "Exactly 2 groups, at least 4 rows per group, and pairs that share exactly one column; otherwise refused.")
BASIS["sdata.compare_averages"] = _b(
    "Welch's t-test (two groups) or Welch's ANOVA (three or more), from averages, standard deviations and counts.",
    "test_method=\"student\" or \"anova\".",
    "As table.compare_averages_of: Welch's tests stay valid when the spreads differ (Delacre et al. 2017, 2019).",
    ("welch1947", "delacre2017", "delacre2019"), "P2",
    "Counts must be whole numbers of at least 2 and standard deviations above 0.")

# ---- Risks and rates
BASIS["table.compare_risks"] = _b(
    "Against the first group in sorted order: the risk in each group with its exact interval, the risk "
    "difference with Newcombe's score interval, the risk ratio and odds ratio with Wald intervals on the log "
    "scale, and the chi-square p-value with Yates' correction (as R prop.test()); the number needed to treat.",
    "against=; p_value_by=\"exact\" (Fisher, with the conditional odds ratio); allowing_for= (Mantel-Haenszel); "
    "same_within=, not_lower=, not_higher=.",
    "Absolute risks and the risk difference are printed with the ratios, as reporting guidance asks (Lang & Altman "
    "2015). Newcombe's score interval for a difference of proportions does far better than the Wald interval "
    "(Newcombe 1998); the log-scale intervals of the ratios are the standard ones (Katz et al. 1978; Woolf 1955); "
    "the NNT interval follows Altman 1998. The Yates-corrected p-value matches R prop.test(); Campbell 2007 prefers "
    "the uncorrected 'N - 1' chi-square.",
    ("newcombe1998", "katz1978", "woolf1955", "altman1998", "lang2015", "campbell2007", "zhang1998", "davies1998"),
    "P2",
    "No 0.5 is added to empty cells (a note says so); when more than 10 % have the outcome, a note says the odds "
    "ratio is not a risk ratio (the 10 % rule of Zhang & Yu 1998; the gap grows with the baseline risk and the size "
    "of the effect, Davies et al. 1998); a group with no events gives an empty p-value, as prop.test().")
BASIS["table.compare_risks allowing_for="] = _b(
    "The Mantel-Haenszel odds ratio and risk ratio over the strata, the Mantel-Haenszel test with continuity "
    "correction (as R mantelhaen.test()), and the Breslow-Day test that the odds ratios agree (without Tarone's "
    "correction).",
    "Leave out allowing_for= for the crude comparison.",
    "Mantel-Haenszel pooling is the classic way to compare two groups within strata (Mantel & Haenszel 1959; "
    "Greenland & Robins 1985 for the risk ratio). Tarone 1985 showed that the Breslow-Day statistic needs a "
    "correction to follow the chi-square distribution; simplydata does not apply it yet.",
    ("mantel1959", "greenland1985", "tarone1985"), "P3",
    "Two groups and two-sided only; strata with one group are left out (with a note); fewer than 2 usable strata "
    "are refused; when Breslow-Day's p is below 0.05 a note asks for each stratum's odds ratio.", "convention")
BASIS["table.compare_risks same_within="] = _b(
    "Two one-sided tests of the risk difference against the margin, with the 90 % Wald interval (as R "
    "TOSTER::twoprop_test()); not_lower= or not_higher= give one-sided Wald tests.",
    "not_lower=, not_higher=.",
    "Equivalence is tested with two one-sided tests (Schuirmann 1987; Lakens 2017). The Wald interval matches "
    "TOSTER; it is too narrow for small samples or risks near 0 or 100 % (Newcombe 1998), where score intervals "
    "do better.",
    ("schuirmann1987", "lakens2017", "newcombe1998"), "P3",
    "Two groups only; a margin between 0 and 1 gets a note asking whether percentage points were meant.",
    "convention")
BASIS["sdata.compare_risks"] = _b(
    "The same measures as table.compare_risks, from counts.",
    "As table.compare_risks.",
    "As table.compare_risks.",
    ("newcombe1998", "katz1978", "altman1998"), "P2", "As table.compare_risks.")
BASIS["table.rate_of"] = _b(
    "Events per 1000 units of time, with the exact Poisson interval (as R poisson.test()).",
    "per= another unit; interval= another level.",
    "The exact (Garwood) interval is valid even with few events (Garwood 1936). Per 1000 is simplydata's "
    "starting value for the unit.",
    ("garwood1936",), "P3", "Events must be whole numbers of at least 0 and time at least 0.", "convention")
BASIS["table.compare_rates"] = _b(
    "The rate ratio against the first group in sorted order, with the exact conditional test and the exact "
    "interval of R poisson.test(); rates per 1000 (a starting value).",
    "against=, per=; same_within=, not_lower=, not_higher=.",
    "Conditioning on the total number of events gives an exact test of two Poisson rates (Przyborowski & Wilenski "
    "1940), R's poisson.test(); exact tests are conservative, and mid-p versions are an alternative (Fay 2010).",
    ("przyborowski1940", "garwood1936", "fay2010b"), "P3",
    "Without R the interval is left out, with a note; no events in either group gives an empty result, with a "
    "note.", "convention")
BASIS["sdata.compare_rates"] = _b(
    "The same test as table.compare_rates, from counts and times.",
    "As table.compare_rates.", "As table.compare_rates (Przyborowski & Wilenski 1940).", ("przyborowski1940",),
    "P3", "As table.compare_rates.", "convention")

# ---- Diagnostic tests
BASIS["table.compare_to_truth"] = _b(
    "A 2 x 2 table: sensitivity, specificity and the predictive values with exact (Clopper-Pearson) intervals, "
    "likelihood ratios (R epiR), and the same results in natural frequencies ('of 1000 people'). A score column "
    "goes to an ROC curve (AUC with DeLong's interval, the best cut-off by Youden's index).",
    "cut_off=, positive_when=\"lower\", prevalence=.",
    "STARD asks for these measures with their intervals (Bossuyt et al. 2015); natural frequencies make them easier "
    "to read (Gigerenzer & Hoffrage 1995). The exact interval matches epiR; method comparisons prefer Wilson's "
    "interval for single proportions (Brown, Cai & DasGupta 2001). A cut-off chosen on the same data makes the test "
    "look better than it is (Ewald 2006; Leeflang et al. 2008).",
    ("bossuyt2015", "gigerenzer1995", "clopper1934", "brown2001", "delong1988", "youden1950", "ewald2006",
     "leeflang2008"), "P1",
    "A truth column with no positives or no negatives is refused; a cut-off chosen on these data gets a note that "
    "it will look worse on new data; an AUC below 0.5 suggests positive_when=.")
BASIS["sdata.compare_to_truth"] = _b(
    "The same measures as table.compare_to_truth, from counts; from sensitivity, specificity and prevalence "
    "alone, the arithmetic only, without intervals.",
    "As table.compare_to_truth.", "As table.compare_to_truth.", ("bossuyt2015", "gigerenzer1995"), "P1",
    "Prevalence must lie between 0 and 100.")
BASIS["table.compare_accuracy"] = _b(
    "DeLong's test of two AUCs on the same people (pROC::roc.test(method = \"delong\", paired = TRUE)).",
    "There is no other test here.",
    "DeLong's method compares correlated ROC curves without assuming a shape (DeLong, DeLong & Clarke-Pearson "
    "1988).",
    ("delong1988",), "P2", "Exactly two number columns.")
BASIS["trade_off_curve"] = _b(
    "Higher scores count as positive; the AUC with DeLong's 95 % interval in the legend; the best cut-off by "
    "Youden's index marked with a dot.",
    "positive_when=\"lower\"; several scores, or colour= groups.",
    "DeLong's interval needs no assumption about the score's distribution (DeLong et al. 1988). Youden's index is "
    "the usual summary of a cut-off (Youden 1950), though other criteria choose other points (Perkins & "
    "Schisterman 2006), and a cut-off chosen on the same data is optimistic (Leeflang et al. 2008). The direction "
    "is fixed, not pROC's 'auto', which can hide a test that works the wrong way round.",
    ("delong1988", "youden1950", "perkins2006", "leeflang2008"), "P2", "Needs R pROC; the score must hold numbers.")

# ---- Agreement and reliability
BASIS["table.agreement_between"] = _b(
    "Number columns: the ICC for single raters, absolute agreement, two-way random (ICC(A,1), Shrout and "
    "Fleiss' ICC(2,1)), from R irr. Categories: Cohen's kappa for two raters, Fleiss' kappa (a generalisation of "
    "Scott's pi) for more.",
    "raters=, checking_for=, of= for the other ICC forms; test_method=\"kappa\", \"krippendorff\", \"lin\"; "
    "near_misses=\"linear\" or \"quadratic\" (weighted kappa).",
    "The ICC form must be chosen and reported; ICC(A,1) is the form Koo & Li's flowchart leads to when the raters "
    "are a sample of possible raters and single ratings will be used (Shrout & Fleiss 1979; McGraw & Wong 1996). "
    "Kappa is printed with the raw agreement, because it can be low when agreement is high (Feinstein & "
    "Cicchetti 1990).",
    ("koo2016", "shrout1979", "mcgraw1996", "cohen1960", "cohen1968", "fleiss1971", "hayes2007", "feinstein1990"),
    "P1",
    "The ICC words (poor to excellent) use both ends of the interval (Koo & Li 2016); fewer than 2 complete rows "
    "are refused.")
BASIS["table.limits_of_agreement"] = _b(
    "Bland-Altman limits: the average difference plus and minus 1.96 standard deviations (n - 1), with "
    "intervals for the average and both limits; Lin's concordance as well.",
    "interval= another level.",
    "Bland & Altman's limits answer 'do the two methods agree?', which a correlation does not (Bland & Altman "
    "1986); the intervals of the limits are their approximate ones (Bland & Altman 1999), which are a little too "
    "narrow in small samples, where exact intervals exist (Carkeet 2015).",
    ("bland1986", "bland1999", "carkeet2015", "lin1989"), "P1", "Needs R; both columns must hold numbers.")
BASIS["difference_dots"] = _b(
    "The Bland-Altman picture: differences against averages, with the limits (n - 1 standard deviation) and their "
    "95 % intervals shaded.",
    "There is no option for the limits.",
    "As table.limits_of_agreement (Bland & Altman 1999). statsmodels' own limits divide by n, so they come "
    "from R.",
    ("bland1986", "bland1999"), "P1", "Needs R; two different number columns.")
BASIS["table.reliability_of"] = _b(
    "Cronbach's alpha (raw), with Feldt's interval and alpha with each item left out (R psych).",
    "interval= another level.",
    "Alpha with an interval is the usual report (Cronbach 1951; Feldt 1965); the printout says that alpha rises "
    "with more items and does not show that the items measure one thing (Sijtsma 2009). Methodologists prefer "
    "omega, which does not assume that every item weighs the same (McNeish 2018); simplydata does not yet offer it.",
    ("cronbach1951", "feldt1965", "sijtsma2009", "mcneish2018"), "P3",
    "Columns must hold numbers; a note names an item whose removal raises alpha.", "convention")

# ---- Fitting
BASIS["table.fit_line"] = _b(
    "Least squares (SciPy linregress); the 95 % interval of the slope from the t distribution with n - 2 "
    "degrees of freedom, as R confint(lm(...)).",
    "test_method=\"theil-sen\", \"siegel\", \"standardised major axis\", \"major axis\", \"deming\", "
    "\"passing-bablok\"; with_bends=; changes_at=.",
    "Least squares predicts y from x. When both columns carry error and the question is how they change together, "
    "another line answers it (Warton et al. 2006), which test_method= offers.",
    ("warton2006",), "P3", "Fewer than 3 rows and a constant x are refused; notes on the shape of the residuals.",
    "convention")
BASIS["table.fit_line test_method=\"theil-sen\""] = _b(
    "Sen's slope (the median of all pairwise slopes) with its 95 % interval; the intercept is median(y) - slope x "
    "median(x) (Conover; SciPy's default).",
    "test_method=\"siegel\" (repeated medians).",
    "The Theil-Sen slope resists outliers (Sen 1968); R mblm takes the median of y - slope x x instead, which the "
    "help says.",
    ("sen1968", "siegel1982"), "P3", "", "convention")
BASIS["table.fit_line test_method=\"standardised major axis\""] = _b(
    "The standardised major axis with smatr's own 95 % intervals (R smatr::sma()).",
    "test_method=\"major axis\".",
    "When neither column is the 'cause', as in allometry, the standardised major axis describes how two measures "
    "change together (Warton et al. 2006, 2012).",
    ("warton2006", "warton2012smatr"), "P2", "A note when the slope's sign is not pinned down (p of 0.05 or more).")
BASIS["table.fit_line test_method=\"deming\", y_error_over_x_error="] = _b(
    "Deming regression with the ratio of error variances you give (1 when not given), with mcr's analytical "
    "intervals.",
    "y_error_over_x_error=.",
    "Deming regression allows for error in both methods of a method comparison (Linnet 1993). The ratio should "
    "come from replicate measurements; 1 when it is not given is simplydata's starting value. The analytical "
    "intervals repeat exactly, where mcr's default bootstrap changes from run to run.",
    ("linnet1993",), "P2", "", "starting value")
BASIS["table.fit_line test_method=\"passing-bablok\""] = _b(
    "Passing and Bablok's rank-based line with its own intervals (mcr's \"analytical\").",
    "test_method=\"deming\".",
    "Passing & Bablok 1983 designed the method for comparing two laboratory methods; it resists outliers and "
    "assumes no distribution.",
    ("passing1983",), "P2", "Fewer than 10 pairs and negative values are refused; below 30 pairs a note.")
BASIS["table.fit_line with_bends="] = _b(
    "A continuous broken line (segmented's model, seed 1), with Davies' test of 'no bend at all'.",
    "with_bends= 1 to 3.",
    "The bend's own p-value is not valid because the data chose where the bend is; Davies' test allows for that "
    "(Davies 1987; Muggeo 2003).",
    ("davies1987", "muggeo2003"), "P2", "Needs 5 rows per piece; when no bend is found the straight line is kept, "
    "with a note.")
BASIS["table.fit_line changes_at="] = _b(
    "Segmented regression of an interrupted time series: a change of level and of slope at the point given, rows "
    "at the point counting as after; the lag-1 autocorrelation of the residuals is printed.",
    "changes_at= the point.",
    "Lopez Bernal, Cummins & Gasparrini 2017 model both changes and ask that autocorrelation be checked and, when "
    "it is large, allowed for (for example with HAC standard errors); simplydata prints it but does not adjust.",
    ("bernal2017",), "P2", "At least 3 rows on each side of the point.")
BASIS["table.fit_curve"] = _b(
    "A polynomial of degree 2 by least squares (raw powers, as R lm(y ~ poly(x, 2, raw = TRUE))), fitted on x "
    "mapped onto [-1, 1] and turned back into the raw powers by statsmodels t_test(), so the standard errors keep "
    "their digits when the powers are nearly in proportion (NIST Filip).",
    "of_degree= 1 to 10; of_kind= a named curve; fit_formula() for any formula.",
    "Degree 2 is a starting value, not a published rule; from degree 4 a note says the curve wiggles and points "
    "to smoothing or a formula.",
    (), "P5", "Degrees outside 1 to 10 and too few distinct x are refused.", "starting value")
BASIS["table.fit_curve of_kind=\"logistic growth\""] = _b(
    "Start values from R's self-starting model (stats::getInitial()), or a search of the whole range without R; "
    "then least squares.",
    "of_kind= another named curve.",
    "Self-starting models find start values from the data, so the fit does not depend on a guess (Pinheiro & "
    "Bates 2000; Bates & Watts 1988); the least-squares answer is the same either way.",
    ("pinheiro2000", "bates1988"), "P3", "Refused with a hint when the fit does not settle.", "convention")
BASIS["table.fit_formula"] = _b(
    "Nonlinear least squares by Levenberg-Marquardt (as minpack.lm::nlsLM(); R nls() uses Gauss-Newton and gives "
    "the same estimates when both converge), start values 1 (or the middle of between=), Wald t intervals as "
    "summary(nls); AIC as R logLik.nls.",
    "test_method=\"trust region\" or \"dogbox\"; search=\"whole range\" (differential evolution first); start=, "
    "between=.",
    "Least squares is what R nls() fits. The Wald intervals rest on a straight-line approximation; Bates & Watts "
    "1988 show they can be poor for strongly curved models and prefer profile-likelihood intervals (R confint()), "
    "which simplydata does not yet offer.",
    ("bates1988",), "P3",
    "Levenberg-Marquardt with limits, impossible start values and a search that does not settle are refused; values "
    "the data do "
    "not pin down get infinite standard errors, a note and converged \"no\" (R nls() stops there); with R squared "
    "near 0 as well, the note says the search may have stopped in a flat region and suggests other start values or "
    "search=\"whole range\"; R squared below 0.01 alone gets the same hint; a value at its limit gets a note.",
    "convention")
BASIS["table.fit_dose_response"] = _b(
    "The 4-parameter log-logistic curve (drc's LL.4), with the ED50 and its delta-method interval.",
    "of_kind=\"3 parameter log-logistic\", \"5 parameter log-logistic\", \"weibull\"; doses_for_effect=.",
    "LL.4 is drc's usual model (Ritz et al. 2015); the OECD guidance lists log-logistic curves among several "
    "models for ecotoxicity data (OECD 2006), so of_kind= offers the others. The ED50 should come from the fitted "
    "curve with its interval, not from the raw averages (Ritz et al. 2015); drc gives no interval unless asked, so "
    "simplydata always asks.",
    ("ritz2015", "oecd2006"), "P3",
    "Negative doses and too few distinct doses are refused; an ED outside the doses tested gets a note.",
    "convention")
BASIS["fit_dose_response"] = _b(
    "The 4-parameter log-logistic curve (drc's LL.4), as table.fit_dose_response, drawn over 300 doses evenly "
    "spaced on a log scale, with the ED50 and its interval in the legend.",
    "of_kind= as table.fit_dose_response.",
    "As table.fit_dose_response (Ritz et al. 2015; OECD 2006).",
    ("ritz2015", "oecd2006"), "P3", "As table.fit_dose_response; needs R drc.", "convention")
BASIS["table.find_best_power_of"] = _b(
    "The Box-Cox power with its 95 % profile-likelihood interval, and the simple power (1, 0.5, 0, -1 ...) inside "
    "the interval nearest to it.",
    "test_method=\"yeo-johnson\" (also for values at or below 0); using= (R car::powerTransform).",
    "Box & Cox 1964 chose the power by likelihood; the interval shows which simple powers fit as well. For counts "
    "and shares a matching model is better than a transformation (O'Hara & Kotze 2010), which a note says.",
    ("box1964", "ohara2010"), "P2", "Fewer than 10 values are refused; Box-Cox refuses values at or below 0.")

# ---- Finding and solving
BASIS["sdata.find_where_smallest"] = _b(
    "One unknown with between=: Brent's method (as R optimize()) after a scan of 200 points. Several unknowns: "
    "Nelder-Mead (R optim()'s default), or L-BFGS-B within limits; linear problems: the HiGHS solver.",
    "test_method=; search=\"whole range\" (differential evolution); rules=; whole_numbers=True.",
    "Nelder-Mead and Brent's method are R's defaults (Nelder & Mead 1965). The 200-point scan, L-BFGS-B for limits "
    "and HiGHS for linear problems are simplydata's choices. Nelder-Mead can stop at a point that is not a "
    "minimum (McKinnon 1998), which is why the scan and search=\"whole range\" exist.",
    ("nelder1965", "mckinnon1998"), "P3",
    "A missing start or range is refused; notes when the search did not settle or the best point is at an edge.",
    "convention")
BASIS["sdata.find_where_biggest"] = _b(
    "The same methods as find_where_smallest, on the negative of the formula.",
    "As find_where_smallest.", "As find_where_smallest.", ("nelder1965",), "P3", "As find_where_smallest.",
    "convention")
BASIS["sdata.solve"] = _b(
    "One unknown in a range: every sign change in a scan of 1000 steps, each solved by Brent's method (as "
    "rootSolve::uniroot.all(), whose own default is 100 steps); a polynomial: all its roots (as polyroot()); "
    "equations together: exact linear algebra (as solve()), or Powell's hybrid method (MINPACK hybrd, SciPy root()'s "
    "default; R nleqslv's default is Broyden with a double-dogleg step).",
    "test_method=\"bisection\", \"ridder\", \"toms748\", \"levenberg-marquardt\", \"broyden\"; start=.",
    "Brent's method and Powell's hybrid method are the standard solvers of SciPy and MINPACK. The 1000-step scan is "
    "simplydata's own starting value; the printout says that roots that only touch zero can be missed by a sign "
    "scan.",
    (), "P5", "A different number of unknowns and equations, and singular linear systems, are refused.",
    "starting value")

# ---- Values between points
BASIS["table.values_at"] = _b(
    "Straight lines between the points (as R approx()); repeated places averaged; places outside the data left "
    "empty.",
    "joined_by=\"smooth curve\", \"curve without overshoot\", \"steps\", \"nearest\" and more; smoothness=; "
    "outside=\"extend\".",
    "Straight lines invent the least; the other ways are one option away. These are R approx()'s defaults "
    "(ties = mean, rule = 1).",
    (), "P3", "Too few points, and collinear points on a map, are refused; extension gets a note.", "convention")
BASIS["table.make_map_of"] = _b(
    "50 steps in each direction, joined as values_at (triangles for scattered points, bilinear on a full grid), "
    "places outside the points left empty.",
    "steps=, joined_by=, outside=.",
    "The same rules as values_at; 50 steps is a starting value for a smooth-looking map.",
    (), "P5", "At most 1 000 000 places.", "starting value")

# ---- Distributions
BASIS["table.fit_distribution_to"] = _b(
    "The normal distribution, fitted by maximum likelihood (as R MASS::fitdistr() or fitdistrplus).",
    "distribution= any name; fixed= to hold values; \"kernel density\".",
    "Maximum likelihood is the standard estimator (Venables & Ripley 2002; Delignette-Muller & Dutang 2015). The "
    "normal's standard deviation by maximum likelihood divides by n, which a note says.",
    ("venables2002", "delignette2015"), "P3",
    "Data outside the distribution's range, no spread, and a negative binomial with variance not above the mean "
    "are refused; a note when the search did not settle.", "convention")
BASIS["nums.fit_distribution"] = _b(
    "The same fit as table.fit_distribution_to.", "As table.fit_distribution_to.", "As table.fit_distribution_to.",
    ("venables2002", "delignette2015"), "P3", "As table.fit_distribution_to.", "convention")
BASIS["table.compare_distributions_for"] = _b(
    "Normal, lognormal, gamma and Weibull, ranked by AIC, with the goodness-of-fit statistics of "
    "fitdistrplus::gofstat (no p-values).",
    "distributions= your own list.",
    "AIC compares models fitted to the same data (Akaike 1974; Burnham & Anderson 2002); a note says a difference "
    "below 2 is too small to choose.",
    ("akaike1974", "burnham2002", "delignette2015"), "P2",
    "Count and continuous families are not mixed; a family that fails is left out, with a note.")
BASIS["dist.find_chance_that_value"] = _b(
    "The chance above a value is the survival function sf(), not 1 - cdf().",
    "is_below=, is_between=.",
    "1 - cdf() loses all its digits far out in the tail; sf() keeps them. This is numerical care, not a "
    "statistical choice.",
    (), "P3", "", "convention")

# ---- Models
BASIS["table.explain"] = _b(
    "A linear model by least squares (as R lm()), with t-based 95 % intervals, R squared and the F test. Group "
    "columns are compared with their first level in sorted order. The outcome family is never switched by "
    "itself.",
    "outcome= (yes or no, counts, positive numbers, ordered groups, shares ...), grouped_by=, effects=, "
    "robust_errors=, table_of_tests=, interval_by=, p_value_by= and the other options below.",
    "simplydata follows R's lm() so that every number matches what reviewers can check. It never chooses a model "
    "family from the data, because that choice belongs to the question asked; instead the printout checks the "
    "model and points to a better family.",
    ("obrien2007", "austin2015"), "P4",
    "Notes: residuals not bell-shaped; fewer than 10 rows per effect (a starting value: Austin & Steyerberg 2015 "
    "found about 2 per column enough for linear models); a variance inflation factor above 5 (a rule of thumb whose "
    "limits O'Brien 2007 discusses); a 0/1 outcome suggests outcome=\"yes or no\". Refused: no more rows than "
    "values to estimate, columns that say the same thing, a group column with one level.", "convention")
BASIS["table.explain outcome=\"yes or no\""] = _b(
    "Logistic regression (as R glm(family = binomial)): odds ratios with Wald 95 % intervals (as R "
    "confint.default()) and z-tests, the model as a whole by a likelihood-ratio test; 'yes' chosen from the usual "
    "pairs (yes/no, true/false, 1/0), else the second value in sorted order, and printed.",
    "interval_by=\"profile\"; p_value_by=\"likelihood ratio\"; show=\"risk ratios\"; link=\"probit\" or "
    "\"cloglog\".",
    "Wald intervals and z-tests are what R's summary() and confint.default() give. Profile-likelihood intervals "
    "and likelihood-ratio tests are more accurate with few rows or large effects (Venzon & Moolgavkar 1988; Hosmer, "
    "Lemeshow & Sturdivant 2013), and R's confint() now gives profile intervals; both are one option away. With "
    "few events per column the model is unreliable (Peduzzi et al. 1996; Vittinghoff & McCulloch 2007), and with "
    "separation the estimates do not exist (Albert & Anderson 1984): both are checked.",
    ("venzon1988", "hosmer2013", "peduzzi1996", "vittinghoff2007", "albert1984", "zhang1998", "nagelkerke1991",
     "tjur2009"), "P3",
    "Notes: fewer than 10 events per effect; separation (R's 'fitted probabilities numerically 0 or 1'), with "
    "the advice to use fewer columns or merge groups; more than 10 % with the outcome, where an odds ratio is not a "
    "risk ratio (Zhang & Yu 1998). The fit is summarised by McFadden's, Nagelkerke's and Tjur's R squared "
    "(Nagelkerke 1991; Tjur 2009).", "convention")
BASIS["table.explain outcome=\"counts\""] = _b(
    "Poisson regression with a log link (as R glm(family = poisson)): rate ratios with Wald intervals (as R "
    "confint.default()); time= adds the log of the time as an offset.",
    "outcome=\"counts that vary a lot\" (negative binomial), \"counts (overdispersed)\" (quasi-Poisson), "
    "\"counts with many zeros\"; link=; interval_by=\"profile\".",
    "Counts are best modelled as counts, not log-transformed (O'Hara & Kotze 2010); overdispersion must be checked "
    "before trusting the intervals (Zuur, Ieno & Elphick 2010). Profile intervals are more accurate than Wald "
    "intervals with few rows (Venzon & Moolgavkar 1988) and are one option away.",
    ("ohara2010", "zuur2010", "verhoef2007", "venzon1988"), "P4",
    "Non-whole or negative counts are refused; when the residual deviance is more than 1.5 times its degrees of "
    "freedom (a starting value; the Pearson statistic is the more usual measure), a note says the intervals are too "
    "narrow and names the other families (never a silent switch).")
BASIS["table.explain outcome=\"counts that vary a lot\""] = _b(
    "Negative binomial regression (NB2, as R MASS::glm.nb()), theta by maximum likelihood.",
    "outcome=\"counts (overdispersed)\" for quasi-Poisson.",
    "Negative binomial and quasi-Poisson weight the counts differently; Ver Hoef & Boveng 2007 show how to choose. "
    "glm.nb is the reference implementation (Venables & Ripley 2002).",
    ("verhoef2007", "venables2002"), "P3",
    "When theta grows without limit (no extra spread), the fit is refused and outcome=\"counts\" suggested.",
    "convention")
BASIS["table.explain outcome=\"counts (overdispersed)\""] = _b(
    "Quasi-Poisson with the Pearson dispersion, t-tests (as R summary(glm(family = quasipoisson))) and Wald "
    "intervals.",
    "outcome=\"counts that vary a lot\".",
    "The quasi-likelihood dispersion is estimated from Pearson's statistic (Wedderburn 1974; McCullagh & Nelder "
    "1989), as R does.",
    ("wedderburn1974", "mccullagh1989", "verhoef2007"), "P3", "There is no AIC (no likelihood), which is said.",
    "convention")
BASIS["table.explain outcome=\"positive numbers\""] = _b(
    "Gamma regression with a log link (as R glm(family = Gamma(link = \"log\"))), Pearson dispersion, t-tests.",
    "link=\"inverse\" (R's own default for Gamma) or \"identity\".",
    "The log link gives ratios, which are easier to read, and keeps predictions positive (McCullagh & Nelder "
    "1989); choosing it over R's inverse link is simplydata's own choice.",
    ("mccullagh1989",), "P5", "Values at or below 0 are refused.", "starting value")
BASIS["table.explain outcome=\"yes or no (overdispersed)\""] = _b(
    "Quasi-binomial, as R glm(family = quasibinomial): the shares, with the tries as weights and the Pearson "
    "dispersion.",
    "outcome=\"yes or no\" with out_of=.",
    "Wedderburn's quasi-likelihood with the Pearson dispersion is R's quasibinomial; a two-column outcome in "
    "statsmodels would give another dispersion.",
    ("wedderburn1974", "mccullagh1989"), "P3", "", "convention")
BASIS["table.explain outcome=\"ordered groups\""] = _b(
    "The proportional-odds model with a logit link (as R MASS::polr()).",
    "outcome=\"groups\" for groups with no order.",
    "McCullagh's proportional-odds model is the standard model for ordered categories (McCullagh 1980).",
    ("mccullagh1980",), "P3", "Fewer than 3 groups are refused; text needs in_order=.", "convention")
BASIS["table.explain outcome=\"groups\""] = _b(
    "Multinomial logistic regression, each group against the first in sorted order (as R nnet::multinom()).",
    "in_order= to choose the first group.",
    "The baseline-category logit model is the usual model for unordered outcomes; R's first level is the baseline.",
    (), "P3", "", "convention")
BASIS["table.explain outcome=\"shares\""] = _b(
    "Beta regression with a logit link and one precision (R betareg).",
    "There is no other family for shares here.",
    "Beta regression models shares between 0 and 1 directly (Ferrari & Cribari-Neto 2004).",
    ("ferrari2004",), "P2", "Values outside (0, 1) are refused, with a hint to divide percents by 100.")
BASIS["table.explain outcome=\"counts with many zeros that vary a lot\""] = _b(
    "Zero-inflated negative binomial with a logistic zero part and the same columns in both parts "
    "(pscl::zeroinfl(dist = \"negbin\")'s defaults).",
    "zero_part_using= other columns for the zero part; outcome=\"counts with many zeros\" (Poisson).",
    "Lambert 1992 introduced zero-inflated models; pscl is their R reference (Zeileis, Kleiber & Jackman 2008).",
    ("lambert1992", "zeileis2008"), "P3", "Counts with no zeros are refused (use the plain count outcomes).",
    "convention")
BASIS["table.explain outcome=\"counts in two steps\""] = _b(
    "A hurdle model: a logistic part for zero or not, and a Poisson part cut off at 1 for the counts above 0 "
    "(pscl::hurdle()).",
    "outcome=\"counts in two steps that vary a lot\" (negative binomial counts); zero_part_using=.",
    "Mullahy 1986's two-part model; pscl's binomial zero part is the textbook form (Zeileis et al. 2008), where "
    "statsmodels' default zero part is Poisson.",
    ("mullahy1986", "zeileis2008"), "P3", "All zeros or no zeros are refused.", "convention")
BASIS["table.explain zero_part_using="] = _b(
    "The zero part gets its own columns (pscl's y ~ x | z); without the option both parts use the columns of "
    "using=.",
    "Leave it out for the same columns in both parts.",
    "Both forms are pscl's (Zeileis, Kleiber & Jackman 2008).",
    ("zeileis2008",), "P3", "", "convention")
BASIS["table.explain weights="] = _b(
    "Precision weights, as R lm(weights =) (statsmodels WLS, or GLM var_weights); rows with weight 0 are left out, "
    "as R does.",
    "There is no frequency-weight option.",
    "Precision weights are what R's weights= means; frequency weights would change the degrees of freedom. The "
    "printout says which kind was used.",
    (), "P3", "Negative weights and text columns are refused.", "convention")
BASIS["table.explain matched_by="] = _b(
    "Conditional logistic regression with the exact conditional likelihood (as R survival::clogit(), method = "
    "\"exact\"), fitted by Newton's method to the end.",
    "There is no other method here.",
    "Matched sets must be compared within themselves; the exact conditional likelihood is clogit's default (Gail, "
    "Lubin & Rubinstein 1981). statsmodels' default optimiser stops a little short, so Newton's method finishes.",
    ("gail1981",), "P3", "Sets without both a yes and a no are dropped (with a note); fewer than 2 such sets are "
    "refused.", "convention")
BASIS["table.explain show=\"risk ratios\""] = _b(
    "Modified Poisson regression (Zou 2004): a Poisson model for the 0/1 column with robust (HC0) standard errors.",
    "test_method=\"log-binomial\".",
    "Odds ratios overstate risk ratios when the outcome is common (Zhang & Yu 1998). Modified Poisson gives the "
    "risk ratio and always converges (Zou 2004); the log-binomial model often fails to (McNutt et al. 2003).",
    ("zou2004", "mcnutt2003", "zhang1998"), "P2", "Only for yes/no outcomes.")
BASIS["table.explain test_method=\"log-binomial\""] = _b(
    "A binomial model with a log link, as R glm(family = binomial(link = \"log\")).",
    "show=\"risk ratios\" alone (modified Poisson).",
    "The log-binomial model gives risk ratios directly but often does not converge (McNutt et al. 2003).",
    ("mcnutt2003", "zou2004"), "P4",
    "When it does not converge or a predicted chance reaches 1, simplydata says so and points to modified Poisson.")
BASIS["table.explain giving_outliers_less_weight="] = _b(
    "Huber M-estimation with k = 1.345, the median absolute deviation as scale, Huber's H1 covariance (R "
    "MASS::rlm()'s defaults).",
    "There is no MM-estimation here.",
    "Huber's estimator gives large residuals less weight (Huber 1964); k = 1.345 is the default of MASS::rlm "
    "and statsmodels (Venables & Ripley 2002). It does not resist rows with extreme x, which the printout says.",
    ("huber1964", "venables2002"), "P3", "Numbers outcomes only; the down-weighted rows are listed.", "convention")
BASIS["table.explain with_knots="] = _b(
    "A natural cubic spline with its inner knots at the quantiles of all the values, as R splines::ns() places "
    "them, without its constant; the whole-curve test asks 'is it flat?'.",
    "with_knots= 1 to 10; curve_for= for a smooth chosen by the data.",
    "Natural splines are the standard way to let a number column bend inside a model (Perperoglou et al. 2019). "
    "simplydata places the knots as R ns() does; Harrell 2015 places restricted cubic spline knots at fixed "
    "quantiles instead (for example 5, 35, 65 and 95 %).",
    ("perperoglou2019", "harrell2015"), "P3", "Too many repeated values for separate knots are refused.",
    "convention")
BASIS["table.explain show=\"standardised effects\""] = _b(
    "The model fitted again on z-scores (standard deviation with n - 1) of the number columns, and of the outcome "
    "when it is a number (as R effectsize::standardize_parameters(method = \"refit\")).",
    "Leave show= out for effects in the columns' own units.",
    "Standardised effects depend on this sample's spread and are not measures of importance (Greenland, "
    "Schlesselman & Criqui 1986), which the printout says; Gelman 2008 discusses scaling by two standard "
    "deviations instead.",
    ("greenland1986", "gelman2008"), "P3", "A column with no spread is refused.", "convention")
BASIS["table.explain interval_by=\"bootstrap\""] = _b(
    "Rows drawn again whole (case resampling), the same model fitted to each, 9999 times (seed 1), BCa intervals "
    "(as R boot::boot.ci(type = \"bca\")).",
    "interval_by=\"profile\"; resamples=, with_seed=.",
    "Case resampling keeps each row's columns together (Davison & Hinkley 1997); BCa intervals correct for bias "
    "and skew (Efron 1987).",
    ("davison1997", "efron1987"), "P2",
    "A resample that loses a rare group is refused (merge it, or use profile intervals); below 20 rows a note.")
BASIS["table.explain interval_by=\"profile\""] = _b(
    "Profile-likelihood intervals, R's confint() of a glm.",
    "interval_by=\"wald\" (the default) or \"bootstrap\".",
    "Profile intervals are safer than Wald intervals with few rows or effects far from 1 (Venzon & Moolgavkar 1988); "
    "since R 4.4 they are what confint() gives for a glm.",
    ("venzon1988",), "P2", "Yes/no and count outcomes only.")
BASIS["table.explain p_value_by=\"likelihood ratio\""] = _b(
    "Each column left out in turn and the deviances compared (chi-square, 1 df), as R drop1(m, test = \"LRT\").",
    "Leave it out for Wald z-tests.",
    "Likelihood-ratio tests behave better than Wald tests in small samples and near the edge of the parameter "
    "space (Hosmer, Lemeshow & Sturdivant 2013 in the logistic case).",
    ("hosmer2013",), "P2", "Yes/no and count outcomes only; not with grouped_by=.")
BASIS["table.explain robust_errors="] = _b(
    "HC3 standard errors (statsmodels for linear models, R sandwich::vcovHC(type = \"HC3\") for the others).",
    "Leave it out for the model's own standard errors; effects=\"for the whole population\" for grouped rows.",
    "HC3 keeps its error rate in small samples better than White's original HC0 (MacKinnon & White 1985; Long & "
    "Ervin 2000, who recommend it below 250 rows).",
    ("white1980", "mackinnon1985", "long2000"), "P2", "Refused with grouped_by= (GEE is suggested).")
BASIS["table.explain table_of_tests="] = _b(
    "No table unless asked; with table_of_tests=\"type 2\" (the usual choice), each column tested after the others but "
    "before its interactions (as R car::Anova(type = 2)).",
    "table_of_tests=\"type 3\" (sum-to-zero coding done for you) or \"in order\" (type 1, as R anova()).",
    "Type II tests respect the principle of marginality and are more powerful than type III for unbalanced data "
    "(Langsrud 2003); type III needs sum-to-zero coding to mean anything, which simplydata sets.",
    ("langsrud2003",), "P2", "Not with grouped_by= and the newer outcome families.")
BASIS["table.explain grouped_by="] = _b(
    "A linear mixed model with a random intercept for each group, fitted by REML (as R lme4::lmer()); Wald "
    "z-tests and Wald intervals. Yes/no and count outcomes go to R lme4::glmer() (Laplace approximation).",
    "p_value_by=\"satterthwaite\" (lmerTest t-tests); own_slope_for= (random slopes); crossed_with=; nested "
    "groups with a list.",
    "REML is the default of lme4 and nlme and corrects the downward bias of maximum likelihood in the variances "
    "(Harville 1977; Bates et al. 2015). lme4 itself prints no p-values: the Wald z-tests are simplydata's choice. "
    "They are anti-conservative with few groups, and Satterthwaite or Kenward-Roger degrees of freedom keep the "
    "error rate near 5 % (Luke 2017), which p_value_by=\"satterthwaite\" gives (lmerTest's own default).",
    ("harville1977", "bates2015", "luke2017", "satterthwaite1946", "kenward1997", "harrison2018", "bolker2009"), "P5",
    "Fewer than 5 groups get a note (poorly estimated; Harrison et al. 2018); groups at least as many as rows, "
    "fewer than 2 groups and other outcomes are refused; a singular fit and a fit that did not settle get notes.",
    "starting value")
BASIS["table.explain crossed_with="] = _b(
    "Two groupings crossed with each other, (1 | school) + (1 | class), fitted by REML as lme4's default.",
    "grouped_by= alone for one grouping.",
    "Leaving out a crossed grouping (subjects and items) inflates false positives (Baayen, Davidson & Bates "
    "2008); lme4 fits crossed groupings directly (Bates et al. 2015).",
    ("baayen2008", "bates2015"), "P2", "Fewer than 5 groups in a grouping get a note.")
BASIS["table.explain effects="] = _b(
    "With effects=\"for the whole population\": GEE with exchangeable correlation and robust (sandwich) standard "
    "errors, as R geepack::geeglm().",
    "within_groups=\"in time order\" (AR-1) or \"independent\"; leave effects= out for a mixed model.",
    "GEE answers questions about the population average, mixed models about a typical group (Liang & Zeger 1986; "
    "Hubbard et al. 2010). The sandwich standard errors are too small with few groups; Mancl & DeRouen 2001 give a "
    "bias-corrected estimator, which simplydata does not yet offer.",
    ("liang1986", "hubbard2010", "mancl2001"), "P2",
    "Fewer than 20 groups (a starting value) get a note that the robust standard errors may be too small.")
BASIS["table.explain empty_cells="] = _b(
    "With empty_cells=\"multiple imputation\": 20 tables filled by chained equations (predictive mean matching "
    "with 5 donors, seed 1), each fitted and pooled by Rubin's rules with Barnard-Rubin degrees of freedom (as R "
    "mice).",
    "with_seed=; leave it out to use complete rows only.",
    "Multiple imputation keeps the uncertainty of the filled cells (Rubin 1987; Barnard & Rubin 1999); predictive "
    "mean matching with 5 donors is mice's default (van Buuren & Groothuis-Oudshoorn 2011). 20 imputations is "
    "simplydata's starting value (mice's own default is 5); White, Royston & Wood 2011 suggest at least as many "
    "as the percentage of incomplete rows, which simplydata does not check.",
    ("rubin1987", "barnard1999", "vanbuuren2011", "white2011"), "P5",
    "Rows with gaps in text columns are left out, with a note; without gaps the ordinary fit is used; refused with "
    "grouped_by=, time=, out_of=.", "starting value")
BASIS["table.explain curve_for="] = _b(
    "A generalised additive model (R mgcv::gam(method = \"REML\")) with a thin-plate regression spline for each "
    "column named.",
    "with_knots= for a natural spline with fixed knots.",
    "REML chooses the smoothness more reliably than GCV, which tends to under-smooth (Wood 2011).",
    ("wood2011",), "P2", "Columns with fewer than 10 different values are refused (mgcv's own limit).")
BASIS["table.explain for_percentile="] = _b(
    "Quantile regression by R quantreg's exact simplex (Barrodale-Roberts), with standard errors by \"nid\" for "
    "every number of rows.",
    "for_percentile= 1 to 99.",
    "Quantile regression (Koenker & Bassett 1978) describes the edges of the data, not only the average. The "
    "\"nid\" sandwich (Hendricks & Koenker 1992) gives standard errors and p-values at any size, which is why "
    "simplydata uses it; quantreg's own default below 1001 rows, rank-inversion intervals, covers better in small "
    "samples (Kocherginsky, He & Mu 2005) but gives no p-values.",
    ("koenker1978", "hendricks1992", "koenker2005", "kocherginsky2005"), "P5",
    "Numbers outcomes only; a note below 20 rows.", "starting value")
BASIS["table.explain changes_at="] = _b(
    "An interrupted time series: a change of level and of slope at the point given (rows at the point count as "
    "after), with the lag-1 autocorrelation of the residuals.",
    "changes_at= the point.",
    "Lopez Bernal, Cummins & Gasparrini 2017 model both changes and ask that autocorrelation be checked and, when "
    "it is large, allowed for; simplydata prints it but does not adjust.",
    ("bernal2017",), "P2", "")
BASIS["table.explain spread_changes_with="] = _b(
    "Generalised least squares fitted by REML (nlme's default): a group column gives each group its own spread "
    "(varIdent); a number column a spread that grows as a power of it (varPower).",
    "Leave it out for one spread.",
    "These are nlme's variance functions (Pinheiro & Bates 2000); the model with and without them is compared.",
    ("pinheiro2000",), "P3", "Zeros with varPower, groups with fewer than 2 rows and other outcomes are refused.",
    "convention")
BASIS["table.explain neighbours_alike_in_order_of="] = _b(
    "Evenly spaced values give AR(1) correlation (corAR1); uneven gaps give continuous-time AR(1) (corCAR1).",
    "Leave it out for independent rows.",
    "corCAR1 allows for the size of each gap (Pinheiro & Bates 2000); which one was used is printed.",
    ("pinheiro2000",), "P3", "Repeated order values are refused; a correlation above 0.99 gets a note.",
    "convention")
BASIS["table.add_predicted_column"] = _b(
    "No interval unless asked; for_new_rows=True gives a 95 % prediction interval; intervals of GLMs are worked "
    "out on the link scale.",
    "interval=, for_new_rows=.",
    "Intervals on the link scale stay inside the possible range when turned back (McCullagh & Nelder 1989).",
    ("mccullagh1989",), "P3", "for_new_rows= is refused for outcomes other than numbers.", "convention")
BASIS["table.find_model_averages_of"] = _b(
    "Model averages from R emmeans on the response scale, other number columns at their average and groups "
    "counted equally; all pairs compared with Tukey's adjustment; for mixed models the degrees of freedom "
    "emmeans chooses (Kenward-Roger), printed.",
    "comparing=, within_each_group_in=, over_range_of=.",
    "Estimated marginal means (Searle, Speed & Milliken 1980) compare groups at the same values of the other "
    "columns; emmeans is the R reference (Lenth). Comparisons do not need a significant overall test first.",
    ("searle1980", "emmeans", "kenward1997", "kramer1956"), "P3",
    "A column inside an interaction gets a note; a number column for for_each_group_in= is refused.", "convention")
BASIS["table.find_model_averages_of comparing=\"each with the first\""] = _b(
    "Each group against the first group (in sorted order, or the first of in_order=), with emmeans' own "
    "adjustment for this method (dunnettx), printed.",
    "comparing=\"each pair\", \"each with the next\", \"each with the average\", \"trend\".",
    "Comparing with one control is Dunnett's problem (Dunnett 1955); emmeans' dunnettx is its approximation.",
    ("dunnett1955", "emmeans"), "P3", "", "convention")
BASIS["table.find_model_averages_of within_each_group_in="] = _b(
    "The interaction test first (emmeans joint_tests()), then the comparisons within each group.",
    "Leave it out for the overall comparisons.",
    "Groups must be compared with the interaction test, not by which simple effects have small p-values: the "
    "difference between significant and not significant is not itself significant (Gelman & Stern 2006).",
    ("gelman2006",), "P2", "")
BASIS["table.find_model_averages_of over_range_of="] = _b(
    "50 evenly spaced values from the smallest to the largest; the other columns as emmeans holds them.",
    "over_range_of= another column.",
    "50 points make a smooth line; a starting value, not a published rule.",
    ("emmeans",), "P5", "", "starting value")
BASIS["table.check_model_of"] = _b(
    "The four pictures of R plot(lm): residuals against fitted values, Q-Q, scale-location, leverage with Cook's "
    "distance contours at 0.5 and 1; Breusch-Pagan (Koenker's studentised form) and White's tests as notes; for "
    "yes/no outcomes calibration in tenths, Hosmer-Lemeshow (10 groups) and the Brier score.",
    "There are no options for the pictures.",
    "Model checks are shown before they are tested: tests flag harmless departures in large samples, and the "
    "Hosmer-Lemeshow test depends on its groups (Hosmer et al. 1997); calibration is best shown (Van Calster et "
    "al. 2019). Koenker's form of the Breusch-Pagan test does not assume bell-shaped errors (Koenker 1981).",
    ("cook1977", "breusch1979", "koenker1981", "white1980", "hosmer1997", "vancalster2019"), "P2",
    "Rows with Cook's distance above 0.5 get a note; a large p-value is said not to prove a good fit.")
BASIS["table.show_rows_that_pull_model"] = _b(
    "Rows with Cook's distance above 4/n, biggest first (at most 10), with leverage and residuals; for mixed models "
    "groups above 4/k.",
    "There is no option for the cut-off.",
    "Cook's distance measures how much a row moves the fit (Cook 1977); 4/n is a rule of thumb (Bollen & Jackman "
    "1985), not a test, and the printout says to remove a row only for a reason.",
    ("cook1977", "bollen1985"), "P5", "Above 1 the row is said to pull very strongly.", "starting value")
BASIS["table.compare_models"] = _b(
    "Nested models tested as R anova(m0, m1): the F test for linear models, quasi-Poisson and Gamma; the "
    "likelihood-ratio test for the others; mixed models refitted by maximum likelihood first; AIC and BIC as R "
    "logLik.",
    "using= a list of models for an AIC table; check_on_left_out_rows=True.",
    "Comparing nested models by F or likelihood-ratio tests is standard; models fitted by REML must be refitted by "
    "maximum likelihood before their fixed effects are compared (Pinheiro & Bates 2000).",
    ("pinheiro2000", "akaike1974"), "P3",
    "Models that are not nested get AIC only (note); an AIC difference below 2 gets a note; identical models are "
    "refused.", "convention")
BASIS["table.compare_models using=[[...], [...]]"] = _b(
    "AICc when there are fewer than 40 rows per value estimated, else AIC, with Akaike weights; every value "
    "estimated counts, the residual spread too, as R logLik().",
    "There is no BIC table.",
    "Burnham & Anderson 2002 recommend AICc, and say it matters when n / K is below about 40 (Hurvich & Tsai "
    "1989); counting the residual spread as R does keeps the numbers equal to R's.",
    ("burnham2002", "hurvich1989"), "P2",
    "Quasi-Poisson models (no likelihood) and duplicate models are refused.")
BASIS["table.compare_models check_on_left_out_rows=True"] = _b(
    "10-fold cross-validation (R boot::cv.glm(K = 10)), seed 1 so the parts repeat, the same parts for every "
    "model.",
    "with_seed=.",
    "Ten parts balance bias and variance better than leaving out one row at a time, which is cv.glm's own default "
    "(Breiman & Spector 1992; Hastie, Tibshirani & Friedman 2009).",
    ("breiman1992", "hastie2009", "davison1997"), "P2",
    "Fewer than 20 rows, grouped_by= and other outcomes are refused.")
BASIS["table.find_columns_that_predict"] = _b(
    "The lasso (R glmnet, alpha = 1), its penalty by 10-fold cross-validation (seed 1), the largest penalty within "
    "one standard error of the best (lambda.1se); columns standardised; no p-values.",
    "test_method=\"elastic net\" (alpha = 0.5); outcome=\"yes or no\" or \"counts\".",
    "The one-standard-error rule, which its authors call a rule of thumb, picks a simpler model that predicts about "
    "as well (Hastie, Tibshirani & Friedman 2009; Friedman, Hastie & Tibshirani 2010). Ordinary p-values are not "
    "valid after selection, so none are printed (Whittingham et al. 2006; Berk et al. 2013).",
    ("tibshirani1996", "friedman2010", "hastie2009", "whittingham2006", "berk2013"), "P3",
    "Ridge (it keeps every column), fewer than 2 columns and fewer than 20 rows are refused.", "convention")
BASIS["table.find_group_levels_of"] = _b(
    "Each group's level from R lme4 ranef(condVar = TRUE), with level plus and minus 1.96 conditional standard "
    "deviations.",
    "There is no other method here.",
    "Without condVar ranef() gives no uncertainty. The printout warns not to use these levels as data in later "
    "tests, which ignores their uncertainty (Houslay & Wilson 2017).",
    ("houslay2017", "bates2015"), "P4", "Needs grouped_by=; nested groups and other outcomes are refused.")

# ---- Lines and curves (options with their own entries)
BASIS["table.add_smoothed_column test_method=\"loess\", interval="] = _b(
    "R loess's own defaults: span 0.75, local curves of degree 2, no robustness steps; the band uses loess's own "
    "degrees of freedom.",
    "smoothness= another span; interval= the level.",
    "These are the defaults of Cleveland's loess as implemented in R (Cleveland & Devlin 1988).",
    ("cleveland1988",), "P3", "At least 5 readings.", "convention")
BASIS["draw_smooth_line test_method=\"loess\", with_confidence_band="] = _b(
    "R loess's own defaults: span 0.75, local curves of degree 2, no robustness steps (not lowess).",
    "smoothness= another span.",
    "As table.add_smoothed_column(test_method=\"loess\") (Cleveland & Devlin 1988).",
    ("cleveland1988",), "P3", "At least 5 different x.", "convention")

# ---- Patterns across columns
BASIS["table.add_principal_components"] = _b(
    "Principal components of the columns on the same scale (the correlation matrix, as R prcomp(scale. = TRUE)), "
    "2 components, each turned so its biggest weight is positive.",
    "same_scale=False (the covariance matrix); how_many=.",
    "When columns are in different units, PCA of the unscaled columns is driven by the column with the biggest "
    "numbers; scaling is the standard advice (Jolliffe & Cadima 2016). Two components (for a picture) is "
    "simplydata's starting value.",
    ("jolliffe2016",), "P2", "A column with no spread is refused when scaling; at least 2 columns and 3 rows.")
BASIS["table.find_principal_components_of"] = _b(
    "The same principal components as add_principal_components (correlation matrix).",
    "same_scale=False.", "As add_principal_components (Jolliffe & Cadima 2016).", ("jolliffe2016",), "P2",
    "As add_principal_components.")
BASIS["table.add_clusters"] = _b(
    "k-means (R stats::kmeans, Hartigan-Wong, 25 random starts, seed 1) with 3 clusters, on columns put on the same "
    "scale.",
    "how_many=; test_method=\"hierarchical\" (Ward's linkage, or average, complete, single); same_scale=False.",
    "Hartigan-Wong is R's default algorithm (Hartigan & Wong 1979); many starts avoid a poor local answer. The "
    "number of clusters is the user's question: 3 is a starting value, and silhouettes (Rousseeuw 1987) help "
    "choose it.",
    ("hartigan1979", "ward1963", "rousseeuw1987"), "P5",
    "Fewer different rows than clusters are refused; tied heights in hierarchical clustering get a note.",
    "starting value")
BASIS["table.find_distances_between_rows"] = _b(
    "Bray-Curtis dissimilarity (vegan::vegdist's default), on the values as given.",
    "measure=\"euclidean\", \"manhattan\", \"jaccard\".",
    "Bray-Curtis ignores shared absences and was among the most robust measures of community difference in Faith, "
    "Minchin & Belbin 1987 (Bray & Curtis 1957); Euclidean distance on raw abundances is not. On raw abundances "
    "Bray-Curtis is dominated by the most abundant taxa, so a transformation first is often advised (Legendre & "
    "Gallagher 2001).",
    ("bray1957", "faith1987", "legendre2001"), "P2",
    "Negative values and rows of zeros are refused for Bray-Curtis and Jaccard (Euclidean is suggested).")
BASIS["table.add_nmds"] = _b(
    "Non-metric multidimensional scaling (vegan::metaMDS) on Bray-Curtis, 2 dimensions, 20 to 100 random starts "
    "(seed 1), and no automatic square-root or Wisconsin transformation (metaMDS's own default is to transform); "
    "the stress read with Clarke's guide.",
    "dimensions=, tries=, measure=.",
    "NMDS keeps only the rank order of the distances (Kruskal 1964); Clarke 1993 gives the guide for reading the "
    "stress (below 0.05 excellent, 0.1 good, 0.2 usable). No hidden transformation and up to 100 starts are "
    "simplydata's own choices.",
    ("kruskal1964", "clarke1993", "faith1987"), "P5",
    "All rows the same are refused; a note when the best answer was not found twice.", "starting value")
BASIS["table.compare_profiles_of"] = _b(
    "PERMANOVA (vegan::adonis2) on Bray-Curtis with 999 permutations (seed 1), followed by a test of the spread "
    "within groups (betadisper).",
    "measure=, permutations=, with_seed=.",
    "PERMANOVA compares groups on any distance (Anderson 2001), but a difference in spread can look like a "
    "difference in place (Warton, Wright & Wang 2012), so the spread is tested too (Anderson 2006).",
    ("anderson2001", "anderson2006", "warton2012"), "P4",
    "Fewer than 2 groups or a group with 1 row are refused; when the spreads differ (p below 0.05), a note "
    "suggests looking at the NMDS.")

# ---- Survival
BASIS["table.find_survival_over_time"] = _b(
    "Kaplan-Meier curves with 95 % intervals on the log scale (Greenwood's standard error), as R survfit(); the "
    "median time with its interval.",
    "at_time_points=, test_method=\"life table\", allowing_for=, followed_from=, average_time_up_to=.",
    "Kaplan & Meier's estimator is the standard (Kaplan & Meier 1958); the log-scale interval is R survival's "
    "default (Therneau & Grambsch 2000). Log-log and arcsine-root intervals cover better in small samples (Klein & "
    "Moeschberger 2003), and SAS and Stata use log-log by default; simplydata does not yet offer them.",
    ("kaplan1958", "therneau2000", "klein2003", "gooley1999"), "P3",
    "An event column with three or more kinds is refused and find_risk_over_time named, because 1 - Kaplan-Meier "
    "overstates the risk when another event can come first (Gooley et al. 1999).", "convention")
BASIS["table.find_survival_over_time at_time_points="] = _b(
    "The curve is flat between event times: the survival at a time is that of the last event time at or before "
    "it (R summary(survfit(), times =)).",
    "at_time_points= the times.",
    "This is the Kaplan-Meier step function itself (Kaplan & Meier 1958). Times after a group's last follow-up "
    "are left empty, not carried on, which is said.",
    ("kaplan1958",), "P3", "Negative and repeated times are refused; unsorted times are sorted, with a note.",
    "convention")
BASIS["table.find_survival_over_time test_method=\"life table\""] = _b(
    "The actuarial life table (R KMsurv::lifetab()): intervals start at the times given, the last is open, rows "
    "lost in an interval count as followed for half of it.",
    "Leave test_method= out for Kaplan-Meier.",
    "The actuarial method of Cutler & Ederer 1958, for follow-up known only in intervals.",
    ("cutler1958", "klein2003"), "P3", "Needs at_time_points= starting at 0.", "convention")
BASIS["table.find_survival_over_time allowing_for="] = _b(
    "Direct adjustment: each row's curve is predicted as if in each group from a Cox model and averaged over all "
    "rows (R adjustedCurves, method = \"direct\"), with intervals; never the curve of an 'average' row.",
    "Leave it out for unadjusted curves.",
    "The curve of an 'average patient' is not the average of the patients' curves (Nieto & Coresh 1996; Cole & "
    "Hernán 2004); Denz, Klaaßen-Mielke & Timmesfeld 2023 compare the adjustment methods.",
    ("nieto1996", "cole2004", "denz2023"), "P2", "Needs for_each_group_in=; refused with followed_from=.")
BASIS["table.find_survival_over_time followed_from="] = _b(
    "Each row is at risk only after its start (left truncation, R Surv(start, stop, event)).",
    "Leave it out when everyone was followed from time 0.",
    "Counting a row as at risk before it entered the study biases the estimates (Cain et al. 2011); delayed entry "
    "is handled as Klein & Moeschberger 2003 describe.",
    ("cain2011", "klein2003"), "P4",
    "Empty start times and starts not before the end are refused; fewer than 10 rows at risk at the first event "
    "get a note that the start of the curve is shaky.")
BASIS["table.find_survival_over_time average_time_up_to="] = _b(
    "The restricted mean survival time up to the horizon you name (R summary(survfit(), rmean =)).",
    "average_time_up_to= the horizon.",
    "The average time without the event up to a horizon is easier to read than a hazard ratio and needs no "
    "proportional hazards (Royston & Parmar 2013; Uno et al. 2014). The horizon must be chosen by you, so none is "
    "set silently.",
    ("royston2013", "uno2014"), "P2", "A horizon beyond the shortest group's follow-up is refused, with the largest "
    "allowed value.")
BASIS["table.compare_survival"] = _b(
    "The log-rank test (equal weight to every event time), as R survdiff().",
    "allowing_for= (stratified), followed_from=, average_time_up_to= (restricted means), competing_with= (Gray's "
    "test).",
    "The log-rank test is the standard comparison of whole survival curves and the most powerful when hazards "
    "are proportional (Mantel 1966; Peto & Peto 1972).",
    ("mantel1966", "peto1972"), "P3",
    "Fewer than 2 groups or no events are refused; groups with no expected events are dropped, as R does, with a "
    "note.", "convention")
BASIS["table.compare_survival allowing_for="] = _b(
    "The stratified log-rank test: groups compared within each stratum and the results added up (R survdiff(... "
    "+ strata())).",
    "Leave it out for the plain log-rank test.",
    "Stratifying keeps a strong factor from hiding or creating a difference (Kalbfleisch & Prentice 2002).",
    ("kalbfleisch2002",), "P3", "Number columns are refused; more than 20 strata get a note.", "convention")
BASIS["table.compare_survival followed_from="] = _b(
    "The log-rank test with delayed entry: each row counts as at risk only after its start (statsmodels "
    "survdiff(entry=)).",
    "Leave it out when everyone was followed from time 0.",
    "R survdiff takes no start times. The log-rank test with delayed entry equals the score test of a Cox model "
    "with exact ties (coxph(Surv(start, stop, event) ~ group, ties = \"exact\")); the printout names that R "
    "call and the reliability study checks against it (Channing House: equal to 1.6e-11).",
    ("klein2003", "therneau2000"), "P5", "Refused with allowing_for=.", "starting value")
BASIS["table.compare_survival average_time_up_to="] = _b(
    "The difference and ratio of restricted mean survival times up to the horizon you name (R survRM2::rmst2()); "
    "arm 1 is the second group in sorted order.",
    "average_time_up_to= the horizon.",
    "Royston & Parmar 2013 and Uno et al. 2014. survRM2's own default horizon is the shortest of the groups' last "
    "times; simplydata always passes yours.",
    ("royston2013", "uno2014"), "P2", "More than 2 groups give per-group values only, with a note.")
BASIS["table.compare_survival competing_with="] = _b(
    "Gray's test of the chance of each event over time (cmprsk::cuminc), not a log-rank test with the competing "
    "event censored.",
    "Leave it out when nothing competes.",
    "Gray 1988 compares cumulative incidence when another event can come first.",
    ("gray1988",), "P2", "value= is required; the same value in both is refused.")
BASIS["table.explain_survival"] = _b(
    "The Cox proportional hazards model with Efron's method for tied times (as R coxph()), Wald intervals; the "
    "proportional-hazards check by R cox.zph() and Harrell's C.",
    "allowing_for= (strata), followed_from=, competing_with=, test_method=\"fine-gray\", distribution= (accelerated "
    "failure time).",
    "Efron's approximation is more accurate than Breslow's when times are tied (Hertz-Picciotto & Rockhill "
    "1997) and is R's default; the Schoenfeld-residual test checks proportional hazards (Grambsch & Therneau 1994); "
    "C is optimistic on the rows the model was fitted to (Harrell, Lee & Mark 1996), which is said.",
    ("cox1972", "efron1977", "hertzpicciotto1997", "grambsch1994", "harrell1996"), "P2",
    "No events, too few rows, constant columns and columns that say the same thing are refused; a column whose "
    "effect may change over time gets a note pointing to average_time_up_to=; a fit that did not settle and "
    "extreme estimates get notes.")
BASIS["table.explain_survival allowing_for="] = _b(
    "A stratified Cox model: each stratum has its own baseline risk (R coxph(... + strata())), so it gets no "
    "hazard ratio.",
    "Put the column in using= for its hazard ratio.",
    "Stratification allows for a factor whose hazards are not proportional (Therneau & Grambsch 2000).",
    ("therneau2000",), "P3", "Number columns are refused.", "convention")
BASIS["table.explain_survival followed_from="] = _b(
    "Each row is at risk only after its start (R coxph(Surv(start, stop, event) ~ ...)); when a row starts at an "
    "event time, the model is fitted by R coxph itself, and the printout says so.",
    "Leave it out when everyone was followed from time 0.",
    "Start-stop rows handle delayed entry and columns that change over time; an exposure that starts during "
    "follow-up must not count from time 0, which would add immortal time (Suissa 2008; Therneau & Grambsch 2000).",
    ("suissa2008", "therneau2000", "klein2003"), "P4", "Empty start times and starts not before the end are refused.")
BASIS["table.explain_survival competing_with="] = _b(
    "Cause-specific Cox model: the event asked about, with the competing event counted as the end of follow-up.",
    "test_method=\"fine-gray\" for the risk itself.",
    "Austin, Lee & Fine 2016 recommend cause-specific hazards for questions about causes and Fine-Gray for "
    "predicting risk; the printout names the other model.",
    ("austin2016", "latouche2013"), "P2", "")
BASIS["table.explain_survival test_method=\"fine-gray\""] = _b(
    "Fine and Gray's subdistribution hazard model (cmprsk::crr) with robust (sandwich) standard errors.",
    "Leave test_method= out for the cause-specific model.",
    "Fine & Gray 1999 model the risk of an event when another can come first; their hazard ratios are not ordinary "
    "hazard ratios, which the printout says (Austin, Lee & Fine 2016; Latouche et al. 2013).",
    ("fine1999", "austin2016", "latouche2013"), "P2", "Needs value= and competing_with=; refused with allowing_for= "
    "or followed_from=.")
BASIS["table.explain_survival distribution="] = _b(
    "The accelerated failure time model of R survreg(): time ratios exp(coefficient), never hazard ratios; for "
    "Weibull the shape in words.",
    "distribution=\"weibull\", \"exponential\", \"lognormal\", \"log-logistic\".",
    "An accelerated failure time model estimates how much longer or shorter the time is (Kalbfleisch & Prentice "
    "2002); AIC is printed so that distributions can be compared.",
    ("kalbfleisch2002",), "P3", "Times of 0 are refused (a Cox model is suggested).", "convention")
BASIS["table.find_risk_over_time"] = _b(
    "Nothing competing: 1 minus Kaplan-Meier. With competing_with=: the Aalen-Johansen estimate (R survfit with "
    "a factor event) with log-scale 95 % intervals; the competing event is a state of its own.",
    "competing_with=, value=, for_each_group_in=.",
    "1 - Kaplan-Meier overstates the risk when another event can come first (Gooley et al. 1999); the "
    "Aalen-Johansen estimate does not. The printout shows what 1 - Kaplan-Meier would have given.",
    ("gooley1999", "klein2003"), "P2", "Three or more kinds of outcome without competing_with= are refused.")
BASIS["table.add_time_and_event_columns"] = _b(
    "Follow-up ends at the first of the end dates (an empty date does not end it); the event counts when its "
    "date came first or on the same day; a year is 365.25 days and a month 30.4375 days.",
    "unit=\"weeks\", \"months\", \"years\"; until=.",
    "This is data preparation, not a statistical method; 365.25-day years are the convention of R Epi (cal.yr) "
    "and of person-year tables in epidemiology, and the printout says it.",
    (), "P3", "End dates before start dates are refused; events before the start (prevalent cases) are left out, "
    "with a note.", "convention")
BASIS["draw_survival_curves"] = _b(
    "Kaplan-Meier curves with censoring marks; no confidence band and no numbers at risk unless asked.",
    "with_confidence_band=True (95 %, log scale), with_at_risk_table=True, allowing_for=, followed_from=.",
    "Kaplan & Meier 1958. Here simplydata departs from reporting advice, which asks for the numbers at risk and "
    "the uncertainty to be shown (Pocock, Clayton & Altman 2002; Morris et al. 2019); both are one option away.",
    ("kaplan1958", "pocock2002", "morris2019"), "P5",
    "An event column with three or more kinds is refused (draw_risk_curves is named).", "starting value")
BASIS["draw_survival_curves followed_from="] = _b(
    "Each row is at risk only after its start (delayed entry).",
    "Leave it out when everyone was followed from time 0.", "As table.find_survival_over_time(followed_from=).",
    ("klein2003",), "P4", "Refused with allowing_for=.")
BASIS["draw_survival_curves allowing_for="] = _b(
    "Direct adjustment: each row's curve predicted in each group, then averaged over all rows.",
    "Leave it out for unadjusted curves.", "As table.find_survival_over_time(allowing_for=) (Nieto & Coresh 1996).",
    ("nieto1996", "denz2023"), "P2", "Needs colour=; refused with the at-risk table or followed_from=.")
BASIS["draw_risk_curves"] = _b(
    "With nothing competing, the chance of having had the event is 1 minus the Kaplan-Meier curve (R "
    "plot(survfit(...), fun = \"event\")).",
    "competing_with=; with_confidence_band=True.",
    "As table.find_risk_over_time (Gooley et al. 1999).", ("gooley1999",), "P2",
    "Three or more kinds of outcome without competing_with= are refused.")
BASIS["draw_risk_curves competing_with="] = _b(
    "The Aalen-Johansen estimate: the competing event is a state of its own, never counted as censored.",
    "Leave it out when nothing competes.", "As table.find_risk_over_time (Gooley et al. 1999).", ("gooley1999",),
    "P2", "Needs R survival.")

# ---- Combining studies
BASIS["table.combine_studies"] = _b(
    "Risk ratios for counts (studies with no events in either group left out), Hedges' g for averages; random "
    "effects with REML; Hartung-Knapp intervals with the ad hoc rule (never narrower than the normal interval); "
    "the prediction interval from 3 studies; from 10 studies, a small-study test (Peters' test for counts, else "
    "Egger's) and trim-and-fill as a what-if.",
    "show=, test_method= (DerSimonian-Laird, Paule-Mandel, common effect, Mantel-Haenszel, Peto), interval_by=, "
    "for_each_group_in=, using=.",
    "The method is chosen before the data, never by the heterogeneity test (Borenstein et al. 2010). REML and "
    "Paule-Mandel estimate the between-study spread better than DerSimonian-Laird; Veroniki et al. 2016 favour "
    "Paule-Mandel for counts and Langan et al. 2019 favour REML, the default of metafor and RevMan (Cochrane "
    "Handbook). Hartung-Knapp intervals keep their coverage (IntHout, Ioannidis & Borm 2014) once made never "
    "narrower than the normal ones (Röver, Knapp & Friede 2015). Prediction intervals say how much true effects "
    "differ (Riley, Higgins & Deeks 2011; IntHout et al. 2016). Funnel tests need 10 studies (Sterne et al. "
    "2011); Peters' test was developed for odds ratios (Peters et al. 2006), and trim-and-fill performs poorly "
    "under heterogeneity (Peters et al. 2007), so it is printed as a what-if only. With rare events, inverse-variance "
    "methods with a 0.5 correction are biased and Mantel-Haenszel or Peto do better (Bradburn et al. 2007), which "
    "test_method= gives.",
    ("cochrane10", "borenstein2010", "veroniki2016", "langan2019", "inthout2014", "rover2015", "riley2011",
     "inthout2016", "higgins2009", "sterne2011", "peters2006", "peters2007", "egger1997", "duval2000", "deeks2002",
     "hedges1981", "viechtbauer2010", "hartung2001", "hedges1999", "sweeting2004", "bradburn2007"), "P1",
    "Fewer than 2 studies, impossible values (events above the count, an estimate outside its interval ...) and "
    "mixed input routes are refused; notes below 5 studies (the spread is hard to estimate), without a prediction "
    "interval below 3, and 'too few studies (under 10)' for small-study effects, which are 'not proof of "
    "publication bias'; empty cells get 1/2 added (metafor's default, which can pull small studies towards no "
    "effect: Sweeting et al. 2004), with a note. There is no note yet for rare events.")
BASIS["table.combine_studies estimates="] = _b(
    "A column with 'ratio' (or OR, HR, RR ...) in its name is combined on the log scale; each estimate and its "
    "interval become a log ratio and its variance (metafor conv.wald()), and the result is shown back as a ratio.",
    "estimates_are_ratios= decides otherwise; standard_errors= instead of intervals.",
    "Ratios are combined on the log scale, where their sampling distribution is close to normal (Cochrane "
    "Handbook, chapter 10).",
    ("cochrane10", "viechtbauer2010"), "P1", "Interval columns that cannot be found are refused, with the names "
    "expected.")
BASIS["table.combine_studies test_method="] = _b(
    "With test_method=\"DerSimonian-Laird\": the moment estimator of the between-study spread (metafor \"DL\"); "
    "\"Paule-Mandel\" is \"PM\"; \"common effect\" is \"EE\".",
    "Leave test_method= out for REML.",
    "DerSimonian-Laird is the classic estimator of older meta-analyses (DerSimonian & Laird 1986) but "
    "underestimates the spread (Veroniki et al. 2016). Paule-Mandel (Paule & Mandel 1982) is recommended for "
    "binary and continuous data by Veroniki et al. 2016; Langan et al. 2019 prefer REML and found Paule-Mandel "
    "biased upward when study sizes differ widely.",
    ("dersimonian1986", "paule1982", "veroniki2016", "langan2019"), "P2",
    "When REML does not converge, the refusal names Paule-Mandel and DerSimonian-Laird.")
BASIS["table.combine_studies test_method=\"Mantel-Haenszel\""] = _b(
    "Mantel-Haenszel weights, a common-effect method: no between-study spread and no prediction interval.",
    "Leave test_method= out for random effects.",
    "Mantel & Haenszel 1959; a common-effect method assumes every study measures the same effect, which the "
    "printout says.",
    ("mantel1959", "cochrane10"), "P3", "Counts or rates only; no meta-regression; no trim-and-fill.", "convention")
BASIS["table.combine_studies test_method=\"Peto\""] = _b(
    "Peto's one-step odds ratio, a common-effect method; it gives odds ratios only.",
    "Leave test_method= out for random effects.",
    "Peto's method is the least biased for rare events with balanced groups (Bradburn et al. 2007; the Cochrane "
    "Handbook), but biased when effects are large (Yusuf et al. 1985 for the method).",
    ("yusuf1985", "bradburn2007", "cochrane10"), "P2", "Counts only; other show= values are refused.")
BASIS["table.combine_studies interval_by="] = _b(
    "With interval_by=\"normal\": the normal (z) interval and p-value of older meta-analyses.",
    "Leave it out for Hartung-Knapp.",
    "The normal interval is too narrow with few studies (IntHout, Ioannidis & Borm 2014; Partlett & Riley 2017), "
    "so it is offered for comparison with older papers only.",
    ("inthout2014", "partlett2017"), "P2", "Hartung-Knapp with a common-effect method is refused.")
BASIS["table.combine_studies for_each_group_in="] = _b(
    "Each subgroup its own random-effects model with its own between-study spread; the test of subgroup "
    "difference compares the subgroup estimates (a common-effect meta-regression), as RevMan and R meta do.",
    "using= for a meta-regression.",
    "Separate spreads per subgroup follow RevMan and R meta (tau.common = FALSE); Borenstein & Higgins 2013 discuss "
    "both and advise one pooled spread when subgroups have few studies. Subgroups must be compared with the test of "
    "difference, not by which subgroup's interval leaves out no effect (Sun et al. 2010).",
    ("borenstein2013", "sun2010", "cochrane10"), "P3",
    "Subgroups with no informative study are dropped (note); fewer than 5 studies in a subgroup get a note.",
    "convention")
BASIS["table.combine_studies using="] = _b(
    "A meta-regression with the default estimator and Hartung-Knapp intervals; R squared says how much of the "
    "between-study spread the columns account for.",
    "interval_by=\"normal\".",
    "Knapp & Hartung 2003 give the test for meta-regression; Thompson & Higgins 2002 warn that few studies make "
    "chance links likely and that the link is between studies, not within them.",
    ("knapp2003", "thompson2002"), "P2", "Number columns only; fewer than 10 studies per column get a note.")
BASIS["forest_plot"] = _b(
    "Ratios on a log scale with the line of no effect at 1, other effects on a plain scale with the line at 0; "
    "on combine_studies results, squares sized by weight, diamonds for the combined effects and a line for the "
    "prediction interval.",
    "log_scale=, line_at=, size=.",
    "A log scale makes a ratio of 2 and of 0.5 the same distance from 1 (Lewis & Clarke 2001; Cochrane Handbook).",
    ("lewis2001", "cochrane10"), "P2", "With several interval levels, the first is drawn and a note names the rest.")
BASIS["draw_funnel_plot"] = _b(
    "Each study against its standard error (0 at the top), the combined effect of combine_studies as the line, "
    "and pseudo 95 % limits; ratios on a log scale.",
    "There are no options for the limits.",
    "Sterne & Egger 2001 recommend the standard error on the vertical axis; the printout says asymmetry is not "
    "proof of publication bias (Sterne et al. 2011).",
    ("sterne2001", "sterne2011"), "P1",
    "Refused for correlations (their standard error is on Fisher's z scale), meta-regressions and fewer than 3 "
    "studies.")

# ---- Planning a study (power)
BASIS["sdata.find_how_many_needed"] = _b(
    "80 % power, significance 0.05, two-sided, two groups of equal size; the two-sample t-test formula (as R "
    "power.t.test(), counting only the right direction for a two-sided test); the answer rounded up. Three or "
    "more groups: one-way ANOVA (Cohen's f); counts: chi-square (Cohen's w), or two percents (R power.prop.test).",
    "power=, significance=, sides=, groups=, test_method=, percents=, same_within=, interval_width=, based_on=, "
    "using=, outcome=, test_method=, in_clusters_of=, drawing_from=.",
    "80 % power at a two-sided 5 % level is the convention of Cohen 1988 and G*Power (Faul et al. 2009); two-sided "
    "tests are the regulatory norm (ICH E9). The effect to plan for is the smallest that matters (Lenth 2001), "
    "never the one a finished study found (Hoenig & Heisey 2001).",
    ("cohen1988", "faul2009", "ich_e9", "lenth2001", "hoenig2001"), "P1",
    "Power not above the significance, effects of 0, and one-sided F and chi-square tests are refused; notes for "
    "the equal-spread formula (Welch in the test) and for no Yates correction.")
BASIS["sdata.find_chance_of_finding"] = _b(
    "Significance 0.05, two-sided, as R power.t.test() (strict = FALSE).",
    "As find_how_many_needed.",
    "As find_how_many_needed (Cohen 1988; ICH E9).", ("cohen1988", "ich_e9"), "P1",
    "values_per_group= is required; a note when the power is below 80 %.")
BASIS["sdata.find_how_many_needed interval_width="] = _b(
    "The Wilson interval, named explicitly (R presize::prec_prop(method = \"wilson\")); for an average "
    "presize::prec_mean.",
    "There is no other interval here.",
    "Wilson's interval keeps its coverage better than the Wald interval (Brown, Cai & DasGupta 2001); presize's "
    "own test_method= is a list of four and warns when none is chosen (Haynes et al. 2021).",
    ("brown2001", "haynes2021"), "P2", "spread= is required for an average.")
BASIS["sdata.find_how_many_needed test_method="] = _b(
    "For test_method=\"compare_survival\": the events needed by Schoenfeld's formula for the log-rank test (R "
    "gsDesign::nEvents()), then the people from the share expected to have the event.",
    "test_method=\"freedman\".",
    "Survival power depends on the number of events, not of people (Schoenfeld 1983; Hsieh & Lavori 2000), so the "
    "events are printed first.",
    ("schoenfeld1983", "hsieh2000"), "P2",
    "A hazard ratio of 1 or below 0 is refused; the printout says it assumes proportional hazards and plans no "
    "recruitment time or drop-out.")
BASIS["sdata.find_how_many_needed test_method="] = _b(
    "With test_method=\"freedman\": Freedman's (1982) formula, two groups of the same size.",
    "Leave test_method= out for Schoenfeld's formula.",
    "Freedman 1982 is the other classic log-rank formula; it gives slightly larger numbers than Schoenfeld's.",
    ("freedman1982",), "P3", "Needs percents=.", "convention")
BASIS["sdata.find_how_many_needed using="] = _b(
    "Regression power on Cohen's f squared, statsmodels FTestPowerF2 (as R pwr::pwr.f2.test()); the rows are "
    "the denominator degrees of freedom plus the columns plus 1.",
    "test_method=\"compare_models\" with against=.",
    "Cohen 1988, chapter 9; the newer statsmodels class names the degrees of freedom the right way round.",
    ("cohen1988", "faul2009"), "P3", "One-sided tests are refused; each name counts as 1 degree of freedom, with "
    "a note.", "convention")
BASIS["sdata.find_how_many_needed outcome="] = _b(
    "For outcome=\"yes or no\": Demidenko's (2007) formula with the variance correction (R pwrss), one bell-shaped "
    "column, the odds ratio per standard deviation.",
    "by_running= on find_chance_of_finding for several columns.",
    "Demidenko 2007 showed that Hsieh's formula (Hsieh, Bloch & Larsen 1998) is inaccurate; the corrected formula "
    "gives G*Power's answer (337 in the G*Power manual's example).",
    ("demidenko2007", "hsieh1998", "faul2009"), "P2", "Several columns are refused.")
BASIS["sdata.find_how_many_needed in_clusters_of="] = _b(
    "The independent number times the design effect 1 + (m - 1) x ICC, rounded up, then whole clusters.",
    "alike_within_clusters= the ICC.",
    "The design effect is the standard allowance for clustering (Donner, Birkett & Buck 1981; CONSORT for cluster "
    "trials, Campbell et al. 2012); unequal cluster sizes need more (Eldridge, Ashby & Kerry 2006), which a note "
    "says.",
    ("donner1981", "campbell2012", "eldridge2006"), "P1",
    "An ICC outside 0 to 1 and clusters below 2 are refused; fewer than 10 clusters get a note.")
BASIS["sdata.find_how_many_needed based_on="] = _b(
    "Power by simulation with the very test compare_averages_of(based_on=\"ranks\") runs (Mann-Whitney), 10000 "
    "tries (seed 1), normal data shifted by the effect; the smallest number that reaches the power.",
    "tries=, with_seed=, drawing_from=.",
    "Simulation is the general answer when no formula fits the test that will be run (Arnold et al. 2011); the "
    "rank-test formulas need P(X < Y), which is rarely known (Noether 1987). SciPy's own significance default is "
    "0.01, so simplydata passes its own.",
    ("arnold2011", "noether1987"), "P2", "Two-sided only; the answer moves a little with the seed, which is said.")
BASIS["sdata.find_how_many_needed same_within="] = _b(
    "Power of the TOST equivalence test (R TOSTER::power_t_TOST()), assuming a true difference of 0 unless "
    "difference= says otherwise.",
    "difference=.",
    "Equivalence must be planned with its own test (Schuirmann 1987; Lakens 2017). A true difference of 0 is the "
    "most hopeful case; plan with difference= if you expect any difference.",
    ("schuirmann1987", "lakens2017"), "P2", "spread= is required; the difference must lie inside the margin.")
BASIS["sdata.find_chance_of_finding drawing_from="] = _b(
    "Seeded simulation (seed 1, 10000 tries, drawn 1000 at a time) with the test compare_averages_of runs: "
    "Welch's t-test (based_on=\"ranks\" gives Mann-Whitney).",
    "tries=, with_seed=.",
    "Simulation answers the power of the test actually run for the distributions you expect (Arnold et al. 2011); "
    "the seed makes the answer repeat and the Monte Carlo interval is printed.",
    ("arnold2011",), "P2", "Distribution objects only; effect options are refused with it.")
BASIS["sdata.find_chance_of_finding by_running="] = _b(
    "Your function, run once per seed (1, 2, ... 500 by default); the p-values below significance= are counted.",
    "tries=, with_seed=.",
    "Simulation of any study design (Arnold et al. 2011); the seeds make the answer repeat.",
    ("arnold2011",), "P2", "A function that gives a different p for the same seed, or p outside 0 to 1, is refused.")

# ---- Smoothing and trend
BASIS["table.add_smoothed_column"] = _b(
    "A centred moving average of 5 readings, the ends left empty (as R stats::filter(x, rep(1/5, 5), sides = 2)).",
    "test_method=\"median\", \"savitzky-golay\", \"exponential\", \"gaussian\", \"lowess\", \"loess\", \"spline\", "
    "\"whittaker\", \"wiener\"; window=, ends=.",
    "The moving average is the simplest smoother and repeats R exactly; the window of 5 is a starting value, not a "
    "published rule. The other methods keep their packages' defaults (Savitzky & Golay 1964; Cleveland 1979).",
    ("savitzky1964", "cleveland1979"), "P5",
    "Even or too large windows are refused; empty cells and uneven spacing are refused for window methods.",
    "starting value")
BASIS["nums.smooth"] = _b(
    "A centred moving average of 5 numbers, the ends left empty.", "As table.add_smoothed_column.",
    "As table.add_smoothed_column.", (), "P5", "As table.add_smoothed_column.", "starting value")
BASIS["nums.remove_trend"] = _b(
    "Removes a least-squares straight line (SciPy detrend, as residuals(lm(x ~ seq_along(x)))).",
    "test_method=\"average\"; breaks= (separate lines per piece, as SciPy).",
    "A straight line is the simplest trend; the help says that MATLAB and R pracma join the pieces, SciPy does not.",
    (), "P3", "Empty values and fewer than 3 numbers are refused.", "convention")
BASIS["table.find_trend_of"] = _b(
    "Sen's slope with its 95 % interval and the Mann-Kendall test with continuity correction (R trend); with "
    "repeats_every=, the seasonal Mann-Kendall test and seasonal Sen slope.",
    "repeats_every=.",
    "Sen's slope and the Mann-Kendall test need no bell shape and resist outliers (Sen 1968; Mann 1945); the "
    "seasonal form compares the same season across years (Hirsch, Slack & Smith 1982). The test assumes "
    "independent readings; autocorrelation inflates its false alarms (Hamed & Rao 1998; Yue et al. 2002). "
    "simplydata checks for it but does not offer the modified test.",
    ("sen1968", "mann1945", "hirsch1982", "hamed1998", "yue2002"), "P2",
    "Fewer than 4 readings are refused; without R only the slope is given, with a note. Without repeats_every= the "
    "readings left after Sen's line are tested for lag-1 autocorrelation (statsmodels acf and Ljung-Box at lag 1, "
    "lag 1 being the reading before); when it is positive with p < 0.05 a note says the p-value is too small and "
    "names the modified test (R modifiedmk). With "
    "repeats_every= the method line says independence is assumed, not checked.")
BASIS["table.add_trend_and_season"] = _b(
    "STL (season and trend by loess) with a season window of 7, as R stl(s.window = 7), not robust.",
    "season_window=\"fixed\" or another odd number; robust=True; test_method=\"moving averages\" (R decompose) or "
    "\"straight line\".",
    "STL handles any season length and resists outliers when robust (Cleveland et al. 1990). R stl() has no "
    "default season window; 7 is simplydata's starting value.",
    ("cleveland1990",), "P5", "Fewer than 2 full cycles and even or small windows are refused.", "starting value")
BASIS["table.find_autocorrelation_of"] = _b(
    "The autocorrelation up to 10 x log10(n) rows back (as R acf()), the white-noise band +-1.96 / sqrt(n), and "
    "the Ljung-Box test.",
    "show=\"partial\" or \"covariance\"; band=\"bartlett\"; rows_back=.",
    "These are R acf()'s defaults; the Bartlett band (Bartlett 1946) widens with the lag for moving-average "
    "processes; the Ljung-Box test checks many lags at once (Ljung & Box 1978).",
    ("bartlett1946", "ljung1978"), "P3", "Fewer than 4 readings, a constant series and uneven spacing are refused.",
    "convention")
BASIS["table.check_steady_over_time"] = _b(
    "Steady around one level: the ADF test with a constant only (R urca::ur.df(type = \"drift\"), MacKinnon's "
    "p-value from urca::punitroot()) and the KPSS test of a steady level (tseries::kpss.test(null = \"Level\")), "
    "read together.",
    "test_method=\"adf\" or \"kpss\"; around=\"straight line\": tseries::adf.test() (constant and trend) and "
    "kpss.test(null = \"Trend\").",
    "The two tests have opposite null hypotheses, so reading them together separates 'steady', 'wanders' and "
    "'cannot tell' (Dickey & Fuller 1979; Kwiatkowski et al. 1992); that only works when both ask the same "
    "question, so the ADF regression follows around= (tseries::adf.test always includes a trend, which would pass a "
    "steadily rising series as steady around a level). tseries has no constant-only ADF test, so that one is "
    "urca's, with MacKinnon's (1996) response-surface p-value.",
    ("dickey1979", "kwiatkowski1992", "mackinnon1996"), "P3",
    "Fewer than 10 readings are refused; needs R; the printout says which question both tests ask.", "convention")
BASIS["table.find_change_points_in"] = _b(
    "Changes in the average by PELT with the MBIC penalty (R changepoint::cpt.mean(method = \"PELT\")), after "
    "dividing by the noise estimated as the median absolute deviation of neighbouring differences / sqrt(2).",
    "change=\"average and spread\"; penalty=\"bic\", \"aic\", \"hannan-quinn\".",
    "PELT finds the best set of changes exactly and fast (Killick, Fearnhead & Eckley 2012); cpt.mean's own default "
    "method finds at most one change. MBIC is changepoint's default penalty (Zhang & Siegmund 2007). cpt.mean "
    "assumes a noise of 1, so simplydata scales by a robust difference-based noise estimate (in the spirit of Hall, "
    "Kay & Titterington 1990), its own step, said in the method line.",
    ("killick2012", "zhang2007", "killick2014", "hall1990"), "P2",
    "Fewer than 4 readings and readings that do not vary are refused.")

# ---- Forecasts
BASIS["table.forecast"] = _b(
    "Holt-Winters exponential smoothing (R HoltWinters()) with an undamped trend, and a season added when "
    "repeats_every= is given; 12 steps ahead with 95 % intervals; a Ljung-Box check of the residuals.",
    "test_method=\"last value\", \"same season last time\", \"average\", \"straight on\", \"arima\" (order= "
    "required); steps_ahead=, interval=, trend=False, season=\"multiplied\".",
    "Holt-Winters is the classic exponential smoothing (Winters 1960). The evidence favours other defaults: modern "
    "practice chooses among exponential smoothing models by AICc (Hyndman et al. 2002; Hyndman & Athanasopoulos "
    "2021), and damped trends usually forecast better than straight ones (Gardner & McKenzie 1985); simplydata "
    "offers neither yet. The residual check uses the lag rule of Hyndman & Athanasopoulos.",
    ("winters1960", "hyndman2002", "hyndman2008", "fpp3", "gardner1985", "ljung1978"), "P3",
    "A season needs 2 full cycles; ARIMA orders are chosen only when asked (order=\"automatic\"), and the order "
    "chosen is printed; residuals that still hold a pattern get a note.", "convention")
BASIS["nums.forecast"] = _b(
    "As table.forecast.", "As table.forecast.", "As table.forecast.", ("winters1960", "fpp3"), "P3",
    "As table.forecast.", "convention")
BASIS["table.compare_forecasts_for"] = _b(
    "The last 12 readings held back; last value, same season last time (or the average), straight on and "
    "exponential smoothing compared by MASE.",
    "test_method=, check_on_last=.",
    "MASE compares forecasts across series and is defined even with zeros (Hyndman & Koehler 2006).",
    ("hyndman2006", "fpp3"), "P2", "At least 2 methods; ARIMA needs order= (three numbers, or \"automatic\").")

# ---- Cycles and filters
BASIS["table.find_spectrum_of"] = _b(
    "The raw periodogram (no taper, mean removed), scaled so the powers add up to the variance (simplydata's "
    "choice of scaling); the 3 strongest peaks named.",
    "test_method=\"welch\" (averaged pieces of 256 readings, Hann window), \"lomb-scargle\" (uneven times); show=.",
    "The periodogram shows every frequency the data allow; its values scatter widely and do not settle with more "
    "data, which Welch's averaged periodogram reduces (Welch 1967), so test_method=\"welch\" is offered.",
    ("welch1967",), "P3", "Fewer than 4 readings, empty cells and uneven spacing are refused (Lomb-Scargle takes "
    "uneven times).", "convention")
BASIS["nums.find_spectrum"] = _b(
    "As table.find_spectrum_of.", "As table.find_spectrum_of.", "As table.find_spectrum_of.", ("welch1967",), "P3",
    "As table.find_spectrum_of.", "convention")
BASIS["table.add_filtered_column"] = _b(
    "A Butterworth filter of order 4, run forwards and backwards (zero phase, SciPy sosfiltfilt), the ends padded "
    "by odd reflection (SciPy's default).",
    "test_method=\"chebyshev\", \"chebyshev 2\", \"elliptic\", \"bessel\"; steepness=; both_ways=False; "
    "remove_at=.",
    "The Butterworth filter has no ripple in the band kept; running it both ways removes the shift in time. The "
    "ends are handled by SciPy's padding (Gustafsson 1996 gives another way to start the filter). Order 4 is a "
    "common engineering starting value, not a published rule.",
    ("gustafsson1996",), "P5", "Frequencies outside (0, Nyquist), steepness outside 1 to 20 and too few readings "
    "for two-way filtering are refused.", "starting value")
BASIS["sdata.frequency_filter"] = _b(
    "A Butterworth filter of order 4 run both ways, as table.add_filtered_column.", "As table.add_filtered_column.",
    "As table.add_filtered_column.", ("gustafsson1996",), "P5", "As table.add_filtered_column.", "starting value")
BASIS["table.find_each_peak_that"] = _b(
    "Every local maximum (SciPy signal.find_peaks() with no thresholds unless you give them); flat tops counted once; the "
    "prominence and the width at half prominence of each.",
    "is_at_least=, apart=, stands_out_by=, wide_at_least=.",
    "No threshold is a neutral start: which peaks matter is your question, and the conditions say it in words. "
    "These are SciPy's defaults.",
    (), "P3", "Empty cells are never peaks; apart= and wide_at_least= need even spacing.", "convention")

# ---- Twins: the same choice on the numbers words and the chart words
BASIS["nums.find_standard_deviation"] = _b(
    "The sample standard deviation, dividing by n - 1, empty values skipped.",
    "There is no other kind here.",
    "As table.find_standard_deviation_of: the n - 1 form of the GUM, R and pandas (NumPy's own default divides by "
    "n).",
    ("gum2008",), "P1", "Fewer than 2 values give an empty answer, with a note.")
BASIS["nums.find_percentile"] = _b(
    "Linear interpolation (R quantile(type = 7)), empty values skipped.",
    "table.find_percentile_of(test_method=) for the other types.",
    "As table.find_percentile_of (Hyndman & Fan 1996).", ("hyndman1996",), "P3", "", "convention")
BASIS["table.add_rank_column"] = _b(
    "Rank 1 for the biggest value; ties share the lowest rank (1, 2, 2, 4), as in sports.",
    "biggest_first=False.",
    "A ranking for reading, not a statistical method; rank tests rank the data themselves (average ranks for "
    "ties).",
    (), "P3", "", "convention")
BASIS["table.add_missing_dates every="] = _b(
    "Without every=, the most common step between the dates (snapped to months, quarters or years when close), "
    "printed.",
    "every= the step.",
    "Data preparation, not a statistical method: the step found is always printed so it can be checked.",
    (), "P5", "Dates with no nameable step are refused.", "convention")
BASIS["nums.find_autocorrelation"] = _b(
    "As table.find_autocorrelation_of: 10 x log10(n) rows back, the white-noise band, Ljung-Box.",
    "show=, band=, rows_back=.", "As table.find_autocorrelation_of.", ("bartlett1946", "ljung1978"), "P3",
    "As table.find_autocorrelation_of.", "convention")
BASIS["autocorrelation_bars"] = _b(
    "As table.find_autocorrelation_of, drawn with the dashed white-noise band of R plot(acf()).",
    "show=, band=\"bartlett\", rows_back=.", "As table.find_autocorrelation_of.", ("bartlett1946",), "P3",
    "As table.find_autocorrelation_of.", "convention")
BASIS["cross_correlation_bars"] = _b(
    "The cross-correlation of two columns (as R ccf(), with the lag sign turned round) for 10 rows back each way, "
    "with the band +-1.96 / sqrt(n).",
    "rows_back=. table.find_correlation_between(rows_back=) uses R's 10 x log10(n) instead.",
    "These are R ccf()'s band and a fixed starting number of lags; the printout says a correlation does not show "
    "that one thing causes the other.",
    (), "P5", "Exactly two columns, filled and evenly spaced.", "starting value")
BASIS["trend_and_season"] = _b(
    "STL as table.add_trend_and_season.", "test_method=, repeats_every=.", "As table.add_trend_and_season (Cleveland "
    "et al. 1990).", ("cleveland1990",), "P5", "As table.add_trend_and_season.", "starting value")
BASIS["forecast"] = _b(
    "Holt-Winters exponential smoothing as table.forecast, 12 steps ahead, the 95 % interval as a band.",
    "As table.forecast.", "As table.forecast.", ("winters1960", "fpp3"), "P3", "As table.forecast.", "convention")
BASIS["spectrum"] = _b(
    "The periodogram as table.find_spectrum_of, on a log scale, the 3 strongest peaks labelled.",
    "test_method=\"welch\", show=, log_scale=False.", "As table.find_spectrum_of (Welch 1967 for the averaged form).",
    ("welch1967",), "P3", "As table.find_spectrum_of.", "convention")
BASIS["spectrum_over_time"] = _b(
    "Pieces of 256 readings with a Hann window and half overlap (SciPy spectrogram), in decibels.",
    "window=, window_shape=.",
    "SciPy's spectrogram with its usual window; 256 is a starting value that trades time against frequency detail.",
    ("welch1967",), "P5", "", "starting value")
BASIS["nums.keep_each_frequency_that"] = _b(
    "A Butterworth filter of order 4, run both ways, as table.add_filtered_column.", "As table.add_filtered_column.",
    "As table.add_filtered_column.", ("gustafsson1996",), "P5", "As table.add_filtered_column.", "starting value")
BASIS["nums.remove_each_frequency_that"] = _b(
    "A Butterworth filter of order 4, run both ways; is_equal_to= removes one frequency with a notch filter.",
    "As table.add_filtered_column; and_multiples=True for a comb filter.",
    "As table.add_filtered_column.", ("gustafsson1996",), "P5", "As table.add_filtered_column.", "starting value")
BASIS["nums.find_each_peak_that"] = _b(
    "Every local maximum, as table.find_each_peak_that.", "As table.find_each_peak_that.",
    "As table.find_each_peak_that.", (), "P3", "", "convention")
BASIS["peak_dots"] = _b(
    "Every local maximum marked, as table.find_each_peak_that.", "is_at_least=, apart=, stands_out_by=, dips=.",
    "As table.find_each_peak_that.", (), "P3", "", "convention")
BASIS["table.compare_each_pair_of matched_by="] = _b(
    "Paired t-tests (or Wilcoxon signed-rank with based_on=\"ranks\") for each pair, Holm's adjustment (as R "
    "pairwise.t.test(paired = TRUE)).",
    "based_on=\"ranks\"; after Friedman's test test_method=\"nemenyi\" or \"conover\".",
    "As table.compare_each_pair_of: Holm's method (Holm 1979).", ("holm1979",), "P2",
    "Subjects not measured in every group are dropped (note); duplicate subject-group rows are refused.")

# ---- Communities and resistomes (S3c-1)
BASIS["table.add_diversity_columns"] = _b(
    "Richness, Shannon with the natural log (as vegan, base e) and Simpson as 1 - the sum of squared shares (the "
    "Gini-Simpson index: the chance that two counts drawn at random are of different kinds).",
    "show=\"inverse simpson\", \"chao1\", \"evenness\", \"hill numbers\"; at_total_count= for rarefaction.",
    "These are vegan's definitions: Shannon's entropy (Shannon 1948) with the natural log, and 1 - the sum of squared "
    "shares, the Gini-Simpson form of Simpson's concentration (Simpson 1949 defined the concentration itself, drawing "
    "without replacement). The printout names the log base because scikit-bio used base 2 before version 0.6.1. "
    "Indices are not diversities: a 10 % drop in Shannon is not a 10 % drop in diversity, so the printout also gives "
    "the number of equally common kinds (Jost 2006).",
    ("shannon1948", "simpson1949", "jost2006"), "P3",
    "Negative values are refused; a row of zeros gets empty cells and a note; when row totals differ more than "
    "two-fold, a note says richness depends on the number of counts and points to at_total_count=.", "convention")
BASIS["table.add_diversity_columns at_total_count="] = _b(
    "Rarefaction as the expected richness in a sample of that many counts (Hurlbert 1971, vegan rarefy()), not a "
    "random subsample, so the answer is the same every time.",
    "Leave it out for observed richness.",
    "The expected value (Hurlbert 1971) gives the same answer every time, where a random subsample would change from "
    "run to run; rarefying of any kind still discards the extra depth of deeper samples (McMurdie & Holmes 2014). "
    "Method comparisons prefer coverage-based standardisation for comparing richness (Chao & Jost 2012), which "
    "simplydata does not yet offer.",
    ("hurlbert1971", "mcmurdie2014", "chao2012"), "P3",
    "Non-whole numbers are refused (rarefaction needs raw counts); a row with fewer counts than asked gets an empty "
    "cell (vegan gives its observed richness), and the printout names it.", "convention")
BASIS["table.add_diversity_columns show=\"chao1\""] = _b(
    "The bias-corrected Chao1 with its standard error, as vegan::estimateR().",
    "show=\"richness\" for observed richness.",
    "Chao1 is a lower bound for the number of kinds, estimated from the kinds seen once or twice (Chao 1987); the "
    "bias-corrected form (Chao 2005) stays finite when no kind is seen twice. It is meaningless when singletons were "
    "removed (as some amplicon pipelines do), which simplydata does not check yet.",
    ("chao1987", "chao2005"), "P3", "Non-whole numbers are refused: Chao1 needs raw counts.", "convention")
BASIS["table.add_diversity_columns show=\"hill numbers\""] = _b(
    "Hill numbers of order 0, 1 and 2 (richness, exp(Shannon), inverse Simpson).",
    "show= the single indices.",
    "Hill numbers are numbers of equally common kinds, so a doubling means doubled diversity (Hill 1973; Jost 2006); "
    "comparing samples still needs the same depth or coverage, especially for orders 0 and 1 (Chao et al. 2014).",
    ("hill1973", "jost2006", "chao2014"), "P2", "")
BASIS["draw_richness_curves"] = _b(
    "vegan's rarefaction curves (rarecurve()) for each row, about 50 points on the shortest curve, with a dotted "
    "line at the smallest row total.",
    "colour= to colour the rows by a group.",
    "Richness can only be compared at the same number of counts (Hurlbert 1971); the dotted line marks the largest "
    "such number. The curves are vegan's; 50 points is a starting value for a smooth curve. Coverage-based curves "
    "(Chao & Jost 2012) are not yet offered.",
    ("hurlbert1971", "chao2012"), "P3", "Non-whole numbers are refused.", "convention")
BASIS["table.add_log_ratio_columns"] = _b(
    "The centred log ratio (clr, R compositions::clr()); zeros, when there are any, replaced first by "
    "zCompositions' Bayesian-multiplicative method (GBM), with no column deleted.",
    "test_method=\"alr\" (against= the reference) or \"ilr\"; zeros_replaced_by=\"adding 1\".",
    "Counts that are shares of a total are compositional, and log ratios are the analysis that respects that "
    "(Aitchison 1982; Gloor et al. 2017). The Bayesian-multiplicative replacement estimates each zero from the data "
    "and keeps the ratios of the other parts (Martín-Fernández et al. 2015; Palarea-Albaladejo & Martín-Fernández "
    "2015). cmultRepl's own default deletes columns that are more than 80 % zeros with only a message; keeping them "
    "is simplydata's choice, and their log ratios then rest mostly on replaced values (Lubbe, Filzmoser & Templ 2021 "
    "compare replacements when zeros are many).",
    ("aitchison1982", "gloor2017", "martinfernandez2015", "palarea2015", "lubbe2021"), "P2",
    "Negative values, a single column and rows of zeros are refused; with the multiplicative replacement, non-whole "
    "numbers are refused; a column with fewer than 2 values above 0 is refused, with the line that merges it with "
    "others.")
BASIS['table.add_log_ratio_columns test_method="alr"'] = _b(
    "Each part over the part named in against= (R compositions::alr(ivar =)).",
    "test_method=\"clr\" (the default) or \"ilr\".",
    "The additive log ratio needs a reference part, which you name (Aitchison 1982).",
    ("aitchison1982",), "P3", "against= is required.", "convention")
BASIS['table.add_log_ratio_columns test_method="ilr"'] = _b(
    "Isometric log ratios with the default basis of R compositions::ilr().",
    "test_method=\"clr\" (the default).",
    "ilr coordinates depend on the basis chosen (Egozcue et al. 2003): another basis (scikit-bio's) gives other "
    "numbers but the same distances between rows, which the printout says.",
    ("egozcue2003",), "P3", "", "convention")
BASIS["table.add_log_ratio_columns zeros_replaced_by=\"adding 1\""] = _b(
    "1 added to every count before the logs (as vegan::decostand(pseudocount = 1)), only when there are zeros.",
    "Leave it out for the Bayesian-multiplicative replacement.",
    "A pseudocount is simple but the answer depends on the number added, which the printout says; model-based "
    "replacement does not have that problem (Martín-Fernández et al. 2015). The 1 is simplydata's value.",
    ("martinfernandez2015",), "P3", "Non-whole numbers are refused; ilr with adding 1 is refused.", "starting value")
BASIS["table.add_principal_coordinates"] = _b(
    "Classical scaling (PCoA) of the Bray-Curtis distances on the counts as given (R stats::cmdscale(eig = TRUE)), 2 "
    "axes, each turned so its value of largest size is positive; the share of the first axis and the running total, "
    "out of the positive eigenvalues.",
    "measure=, how_many=.",
    "Principal coordinates show any distance in a few axes (Gower 1966). Bray-Curtis is the convention for counts "
    "and held up well in simulated gradients (Faith et al. 1987); it is not a straight-line distance, so some "
    "eigenvalues are negative, and the printout says how many and how large. Turning the axes gives the same answer "
    "on every computer.",
    ("gower1966", "faith1987"), "P3", "Fewer than 3 rows are refused.", "convention")
BASIS['table.add_principal_coordinates measure="aitchison"'] = _b(
    "Zeros replaced first (GBM, no column deleted), then the Aitchison distance: the straight-line distance between "
    "the rows' clr log ratios.",
    "measure=\"bray-curtis\" (the default).",
    "The Aitchison distance is the distance of compositional data (Aitchison 1982; Gloor et al. 2017); vegan's "
    "vegdist refuses zeros for it, so simplydata replaces them as add_log_ratio_columns does.",
    ("aitchison1982", "gloor2017", "martinfernandez2015"), "P2", "As add_log_ratio_columns.")
BASIS['table.find_distances_between_rows measure="aitchison"'] = _b(
    "With measure=\"aitchison\": zeros replaced first (GBM, no column deleted), then the straight-line distance "
    "between the rows' clr log ratios.",
    "measure=\"bray-curtis\" (the default), \"euclidean\", \"manhattan\", \"jaccard\".",
    "As add_principal_coordinates(measure=\"aitchison\") (Aitchison 1982; Gloor et al. 2017).",
    ("aitchison1982", "gloor2017", "martinfernandez2015"), "P2", "As add_log_ratio_columns.")
BASIS["table.explain_profiles_of"] = _b(
    "Distance-based RDA on Bray-Curtis distances (vegan dbrda()), the same distance as compare_profiles_of; the "
    "adjusted R squared first; each column tested after all the others (by = \"margin\"); 999 permutations after "
    "set.seed(1).",
    "measure=, test_method=\"canonical correspondence\", allowing_for=, permutations=, with_seed=.",
    "db-RDA tests how columns explain differences in make-up on any distance (Legendre & Anderson 1999; vegan's "
    "dbrda follows McArdle & Anderson 2001, which keeps non-Euclidean distances without correction). The unadjusted "
    "R squared grows with every column, so the adjusted one is printed first (Peres-Neto et al. 2006). Each column "
    "is tested after all the others, so the order of using= does not matter; vegan's own default tests only the "
    "whole model, and by = \"terms\" would test in order. Marginal tests lose power when columns overlap and skip "
    "main effects that also appear in an interaction. Bray-Curtis and marginal tests are simplydata's choices.",
    ("legendre1999", "mcardle2001", "peresneto2006"), "P3",
    "More columns than rows - 2 are refused; collinear columns get a note.", "convention")
BASIS["table.explain_profiles_of measure=\"hellinger\""] = _b(
    "RDA on the Hellinger-transformed counts (square roots of the shares), never on raw counts; each column tested "
    "after all the others.",
    "measure=\"bray-curtis\" (the default).",
    "Raw abundances give Euclidean-based RDA the problems of Euclidean distance; the Hellinger transformation reduces "
    "them, removing the double-zero problem and the dominance of abundant kinds (Legendre & Gallagher 2001).",
    ("legendre2001",), "P2", "")
BASIS['table.explain_profiles_of test_method="canonical correspondence"'] = _b(
    "CCA on the counts themselves (chi-square distances), so no measure=; its adjusted R squared from permutations "
    "(vegan), after set.seed.",
    "Leave test_method= out for db-RDA.",
    "Canonical correspondence analysis (ter Braak 1986) suits long gradients with unimodal responses.",
    ("terbraak1986",), "P3", "Rows that add up to 0 are refused.", "convention")
BASIS["table.explain_profiles_of allowing_for="] = _b(
    "A partial analysis: the column is taken into account first (vegan Condition()) and not tested.",
    "Leave it out for no conditioning.",
    "This is partial RDA, as used in variation partitioning (Peres-Neto et al. 2006); allowing_for= has the same "
    "meaning on the other words.",
    ("peresneto2006",), "P3", "", "convention")
BASIS["table.find_correlation_between_profiles"] = _b(
    "The Pearson Mantel correlation between the two sets of distances, 999 permutations after set.seed(1); second= "
    "with 3 or more columns of whole numbers from 0 is read as counts and gets measure=, other measurements get "
    "straight-line distances after each column is put on the same scale.",
    "test_method=\"procrustes\"; measure=, permutations=, with_seed=.",
    "The Mantel test is the classic comparison of two distance matrices. It answers a question about distances, not "
    "about the columns themselves, which the printout says, and it has low power (Legendre, Fortin & Borcard 2015); "
    "Peres-Neto & Jackson 2001 found Procrustes more powerful, which test_method= gives.",
    ("legendre2015", "peresneto2001"), "P3", "Different rows in the two sets and fewer than 5 rows are refused.",
    "convention")
BASIS["table.find_correlation_between_profiles test_method=\"procrustes\""] = _b(
    "PROTEST on the first two principal coordinates of each set: the Procrustes correlation and its permutation "
    "p-value.",
    "Leave test_method= out for the Mantel test.",
    "Peres-Neto & Jackson 2001 found Procrustes analysis more powerful than the Mantel test for matching two data "
    "sets. Two axes per set is simplydata's starting value.",
    ("peresneto2001",), "P2", "As the Mantel test.")
BASIS["table.compare_profiles_of test_method=\"anosim\""] = _b(
    "Clarke's ANOSIM R from ranked distances, 999 permutations after set.seed(1), with the spread check "
    "(betadisper).",
    "Leave test_method= out for PERMANOVA.",
    "ANOSIM is Clarke's rank-based test (Clarke 1993). Like PERMANOVA it mixes a difference in spread with a "
    "difference in place, and ANOSIM more so (Anderson & Walsh 2013), so the spread check is printed (Anderson 2006).",
    ("clarke1993", "anderson2013", "anderson2006"), "P3", "As compare_profiles_of.", "convention")
BASIS['table.compare_profiles_of show="contributions"'] = _b(
    "SIMPER: each column's average contribution to the Bray-Curtis difference between each pair of groups, without "
    "permutation p-values.",
    "Leave show= out for the test.",
    "SIMPER ranks columns with large and variable counts high even when they do not differ, and its p-values "
    "mislead (Warton, Wright & Wang 2012); the table is a description, which the printout says.",
    ("warton2012",), "P2", "")
BASIS['table.compare_profiles_of measure="aitchison"'] = _b(
    "Zeros replaced (GBM, no column deleted), then the Aitchison distance.",
    "measure=\"bray-curtis\" (the default).",
    "As add_principal_coordinates(measure=\"aitchison\") (Aitchison 1982; Gloor et al. 2017).",
    ("aitchison1982", "gloor2017"), "P2", "As add_log_ratio_columns.")
BASIS["table.add_clusters how_many=\"automatic\""] = _b(
    "Average linkage on the distances, and the number of clusters (2 to 10) with the largest average silhouette "
    "width (R cluster::silhouette); on a tie, the fewer clusters.",
    "how_many= a number.",
    "Choosing the number by the largest average silhouette is a common rule (Rousseeuw 1987; Kaufman & Rousseeuw "
    "1990), not the winner of a method comparison (Milligan & Cooper 1985 found other rules better); 2 to 10 and "
    "'fewer on a tie' are simplydata's starting values. Average linkage is chosen for Bray-Curtis distances, because "
    "Ward's method assumes straight-line distances (Ward 1963).",
    ("rousseeuw1987", "kaufman1990", "milligan1985", "ward1963"), "P5", "Fewer than 4 rows are refused.",
    "starting value")
BASIS["table.add_clusters measure="] = _b(
    "The counts as they are (no rescaling) for Bray-Curtis distances, with average linkage (Ward is refused with "
    "it), the same as draw_cluster_tree.",
    "linkage=\"complete\" or \"single\"; measure=\"euclidean\".",
    "Ward's method minimises squared Euclidean distances (Ward 1963), so it does not fit Bray-Curtis itself; average "
    "linkage (UPGMA) is the common choice for ecological distances and usually keeps the distances best (highest "
    "cophenetic correlation; Borcard, Gillet & Legendre 2018). Ward on the square roots of Bray-Curtis distances is "
    "a valid alternative (Murtagh & Legendre 2014), not offered.",
    ("ward1963", "borcard2018", "murtagh2014"), "P3", "Ward with Bray-Curtis is refused.", "convention")
BASIS["draw_cluster_tree"] = _b(
    "Average linkage for Bray-Curtis distances, the same choice as table.add_clusters, so the tree matches the "
    "clusters; the cophenetic correlation as a note.",
    "measure=, linkage=.",
    "As table.add_clusters(measure=): average linkage is the common choice for ecological distances (Borcard, Gillet "
    "& Legendre 2018), and Ward's method does not fit Bray-Curtis (Ward 1963).",
    ("borcard2018", "ward1963"), "P3", "", "convention")
BASIS["table.add_axes_that_separate_groups"] = _b(
    "Linear discriminant analysis (R MASS::lda()) with MASS's default prior chances, the group shares in the data; "
    "each axis turned so its biggest value is positive; leave-one-out classification.",
    "how_many=.",
    "Fisher's discriminant axes (Fisher 1936) as MASS fits them (Venables & Ripley 2002); the prior is printed, "
    "because equal priors would classify differently. Leave-one-out accuracy is nearly unbiased, unlike in-sample "
    "accuracy, as long as the columns were not chosen on the same data.",
    ("fisher1936", "venables2002"), "P3",
    "Fewer than 2 groups, a group with fewer than 2 rows, and no more rows - groups than columns (the pooled spread "
    "cannot be worked out) are refused; a group with no more rows than columns gets a note; a column constant "
    "within groups is refused with MASS's reason; how_many= is at most the smaller of groups - 1 and the number of "
    "columns.", "convention")
BASIS["table.add_correspondence_axes"] = _b(
    "Correspondence analysis as vegan's cca() with no explaining columns, row scores with scaling = \"sites\" "
    "(vegan's default is \"species\"); each axis turned so its biggest value is positive.",
    "how_many=.",
    "Correspondence analysis (reciprocal averaging; Hill 1973b) fits counts with unimodal responses (ter Braak "
    "1985); it weights rare kinds heavily (Legendre & Gallagher 2001). Site scaling keeps the chi-square distances "
    "between rows, which is why it is chosen for axes added to the rows.",
    ("hill1973b", "terbraak1985", "legendre2001"), "P3",
    "Negative values, empty rows and columns of zeros are refused.", "convention")


# ---- Hidden factors (S3c-2)
BASIS["table.find_hidden_factors_behind"] = _b(
    "Exploratory factor analysis by R psych::fa(): the number of factors by parallel analysis (psych fa.parallel(fa "
    "= \"fa\")), minimum residuals (minres) fitting and an oblimin rotation (through GPArotation), with R's random "
    "numbers seeded (with_seed=1); rows with any empty cell left out.",
    "how_many= a number; test_method=\"ml\" or \"principal axis\"; rotation=\"varimax\", \"promax\", \"none\".",
    "Parallel analysis keeps the factors whose eigenvalues stand out more than in random data of the same size "
    "(Horn 1965; here psych's common-factor variant, Humphreys & Ilgen 1969); the 'eigenvalue above 1' rule keeps "
    "too many (Zwick & Velicer 1986). Simulations disagree on whether the component or the factor variant is more "
    "accurate (Crawford et al. 2010; Lim & Jahng 2019), and no variant is reliable enough to treat the number as "
    "fixed, so try one factor fewer and one more; a different seed can change the number when it is borderline. "
    "Oblique rotations let factors correlate, as they often do, and are usually recommended over varimax (Fabrigar "
    "et al. 1999), though which rotation works best depends on the loading pattern (Sass & Schmitt 2010). Minres "
    "(Harman & Jones 1966), a least-squares fit, recovers weak factors better than maximum likelihood in simulations "
    "(Briggs & MacCallum 2003) and needs no bell shape; Fabrigar et al. 1999 prefer maximum likelihood for data close "
    "to normal, so this is a judgement. Minres and oblimin are psych::fa()'s defaults; choosing the number by "
    "parallel analysis is simplydata's choice (psych's default is one factor), and leaving out rows with empty "
    "cells too (psych would use pairwise correlations). The items are treated as numbers: for items with few "
    "categories, polychoric correlations are not yet offered.",
    ("horn1965", "humphreys1969", "zwick1986", "crawford2010", "lim2019", "fabrigar1999", "sass2010", "harman1966",
     "briggs2003", "bernaards2005", "maccallum1999"), "P2",
    "Needs at least 3 number columns that vary, and at least columns + 2 complete rows; rows with empty cells are "
    "left out, with a note; how_many= is at most the largest number of factors the columns can identify; refused "
    "when parallel analysis finds no factor. Notes for: KMO below 0.6 (a later convention; Kaiser rated only below "
    "0.5 unacceptable); few rows for this many columns (how many are enough depends on how strongly the columns share "
    "factors: MacCallum et al. 1999); a factor with fewer than 3 loadings of 0.3 or more; a column loading on no "
    "factor or on two; Heywood cases (communality of 1 or more).")
BASIS["table.find_hidden_factors_behind how_many="] = _b(
    "A number of factors chosen by you: no parallel analysis (the seed is still set, for the rotation).",
    "how_many=\"automatic\" (the default, parallel analysis).",
    "When theory fixes the number of factors, you name it; Fabrigar et al. 1999 advise also fitting one factor fewer "
    "and one more.",
    ("fabrigar1999",), "P3",
    "how_many= must be a whole number from 1 to the largest number of factors the columns can identify.",
    "convention")
BASIS["table.find_hidden_factors_behind test_method="] = _b(
    "With test_method=\"ml\": maximum likelihood, as base R factanal() fits; \"principal axis\" is psych's fm = \"pa\".",
    "Leave test_method= out for minres.",
    "Maximum likelihood assumes roughly bell-shaped data and is preferred then (Fabrigar et al. 1999); it is more "
    "prone to improper solutions with small samples or weak factors, where least-squares methods (minres, principal "
    "axis) recover factors as well or better (Briggs & MacCallum 2003; de Winter & Dodou 2012).",
    ("fabrigar1999", "briggs2003", "dewinter2012"), "P3", "", "convention")
BASIS["table.find_hidden_factors_behind rotation="] = _b(
    "With rotation=\"varimax\" (as R factanal() uses): uncorrelated factors (Kaiser 1958); \"promax\" lets them "
    "correlate; \"none\" leaves them unrotated.",
    "Leave rotation= out for oblimin.",
    "Varimax (Kaiser 1958) forces the factors to be uncorrelated, which psychological factors often are not "
    "(Fabrigar et al. 1999); it is offered to match older analyses. Unrotated, more than one factor is seldom "
    "interpretable.",
    ("kaiser1958", "fabrigar1999"), "P3", "", "convention")
BASIS["table.check_hidden_factors"] = _b(
    "Confirmatory factor analysis by normal-theory maximum likelihood (R lavaan); with empty cells, missing = \"ml\" "
    "(full information maximum likelihood), which uses every value given.",
    "formula= for a model in lavaan's own syntax.",
    "lavaan's default (\"listwise\") drops every row with an empty cell, reported only in its summary's row count. "
    "Full information maximum likelihood (lavaan's missing = \"ml\"; Rosseel 2012) uses every value given, and is "
    "unbiased and more efficient than listwise deletion when values are missing at random (Enders & Bandalos 2001; "
    "Schafer & Graham 2002); it assumes missing at random and roughly bell-shaped data. Robust standard errors "
    "(estimator MLR) and estimators for ordinal items are not yet offered. Fit guides are printed as guides, not "
    "pass marks (Hu & Bentler 1999; Marsh, Hau & Wen 2004).",
    ("rosseel2012", "enders2001", "schafer2002", "hu1999", "marsh2004"), "P2",
    "Needs measured_by= or formula=, not both; each factor needs at least 2 columns (3 advised); a factor name may "
    "not be a column name; columns must hold numbers and vary; rows with no value at all are left out, with a note; "
    "refused when lavaan does not converge or the model has negative degrees of freedom. Notes for: 0 degrees of "
    "freedom; a column measuring two factors; the 3 largest modification indices above 10, with a warning against "
    "fitting the model to the data.")
BASIS["table.check_hidden_factors formula="] = _b(
    "The model in lavaan's own syntax, run with lavaan::sem(), so hidden factors can explain each other (a structural "
    "equation model); paths shown standardised (lavaan's std.all, delta-method standard errors), as the loadings are.",
    "measured_by= for a plain measurement model.",
    "lavaan's syntax is the most widely used way to write structural equation models in R (Rosseel 2012); sem() and "
    "cfa() have the same defaults, and sem() is used because the model may have paths.",
    ("rosseel2012",), "P3",
    "A formula in fit_formula's style is refused; it needs at least one name =~ columns; every column must exist and "
    "hold numbers.", "convention")

# ---- S3c-3: directions, places and extremes
BASIS["table.find_average_direction_of"] = _b(
    "The circular mean direction from 0 up to the full turn, the mean resultant length and the circular standard "
    "deviation sqrt(-2 ln R) (SciPy circmean, directional_stats, circstd); full_turn= has no default.",
    "full_turn=24 (hours), 12 (months), 365 (days of the year) or \"radians\"; for_each_group_in= for groups.",
    "Directions must be averaged as unit vectors, not as numbers (Fisher 1993; Mardia & Jupp 1999): the plain average "
    "of 350° and 10° is 180°. The circular standard deviation sqrt(-2 ln R) is the standard one in both books and in "
    "R circular. full_turn= is required because R circular reads plain numbers as radians without a word, the trap "
    "the design checked.",
    ("fisher1993", "mardia1999"), "P1",
    "full_turn= must be given; values outside 0 to the full turn are read round the circle, with a note; a resultant "
    "length below 0.1 says there is no clear average direction.")
BASIS['table.compare_shape_to shape="even around the circle"'] = _b(
    "The Rayleigh test (R circular::rayleigh.test), with the units always given; the default test when full_turn= "
    "is given.",
    "test_method=\"rayleigh\" says the same; on a line, the bell-shape tests of compare_shape_to.",
    "The Rayleigh test is the standard test of uniformity against one preferred direction, and the most powerful "
    "against a von Mises alternative (Mardia & Jupp 1999, 6.3; Fisher 1993, 4.3). It cannot see directions gathered at "
    "two opposite sides, so the printout says so when it finds no preferred direction.",
    ("mardia1999", "fisher1993"), "P1",
    "Fewer than 5 directions refused; full_turn= required; a fixed distribution with full_turn= refused.")
BASIS["table.find_autocorrelation_of x="] = _b(
    "Moran's I with every pair of places as neighbours, weights 1 / distance, each row's weights summing to 1, and a "
    "permutation p-value from 999 shuffles after set.seed(1), one-sided (nearby places more alike) (R spdep).",
    "nearest=8 for the 8 nearest places; on_globe=True for longitude and latitude; permutations=, with_seed=.",
    "Moran's I (Moran 1950) depends on the weights, which must be reported (Bivand & Wong 2018). Inverse-distance "
    "weights between all pairs need no distance band chosen by hand; row-standardising and the one-sided permutation "
    "test are spdep's defaults (Bivand & Wong 2018). No study fixes the weights for every field, so this is a "
    "starting value, printed every time.",
    ("moran1950", "bivand2018"), "P5",
    "Two rows at one place refused, with the line that averages them; fewer than 10 places noted; longitude and "
    "latitude without on_globe=True noted; sorted_by= or rows_back= with x= refused.", "starting value")
BASIS["table.find_autocorrelation_of nearest="] = _b(
    "Each place's k nearest places as neighbours, alike, each row's weights summing to 1 (R spdep knearneigh).",
    "Leave nearest= out for 1 / distance weights between all pairs.",
    "k-nearest-neighbour weights give every place the same number of neighbours, useful when places are unevenly "
    "spread (Bivand & Wong 2018). Moran's I changes with the weights (on meuse 0.12 with 1 / distance, 0.49 with the "
    "8 nearest), so the printout names them.",
    ("bivand2018",), "P5", "nearest= must be below the number of places.", "convention")
BASIS["table.find_autocorrelation_of on_globe="] = _b(
    "Longitude and latitude read as places on the earth (crs 4326): great-circle distances in km.",
    "Leave on_globe= out for straight-line distances on x and y.",
    "Straight-line distances on degrees are wrong away from the equator, because a degree east shortens with "
    "latitude; spdep uses great-circle distances for geographic coordinates (Bivand & Wong 2018). simplydata does "
    "not guess: it notes columns that look like longitude and latitude.",
    ("bivand2018",), "P4", "Refused when x= is beyond -180 to 180 or y= beyond -90 to 90.")
BASIS["table.find_variogram_of"] = _b(
    "R gstat's sample variogram (cutoff a third of the diagonal, 15 bins) and a spherical curve fitted by gstat's "
    "weighted least squares (fit.method = 7, weights pairs / distance^2) from gstat's own start values.",
    "of_kind=\"exponential\", \"gaussian\" or \"matern\"; between=[0, cutoff].",
    "Weighted least squares with weights from the number of pairs and the distance follows Cressie (1985); the "
    "cutoff and bins are gstat's defaults (Pebesma 2004). The spherical curve is the usual first choice in gstat's "
    "own examples, not a published rule, so other curves are one option away; the range is said in words, because "
    "for the exponential, Gaussian and Matern curves gstat's range is not where the curve levels off.",
    ("cressie1985", "pebesma2004"), "P3",
    "Refused when gstat does not converge or the fit is singular; fewer than 30 places noted; shared places noted.",
    "convention")
BASIS["draw_variogram"] = _b(
    "The binned semivariances as dots and gstat's fitted curve at 200 distances (gstat::variogramLine).",
    "of_kind= and between= as on find_variogram_of.",
    "The same fit as find_variogram_of (Cressie 1985; Pebesma 2004), so the picture and the numbers agree.",
    ("cressie1985", "pebesma2004"), "P5", "A fit find_variogram_of would refuse is refused here too.", "convention")
BASIS["table.find_return_levels_of"] = _b(
    "A GEV curve fitted by maximum likelihood to block maxima (R extRemes::fevd), return levels with "
    "profile-likelihood 95 % intervals; the shape in the xi sign; no declustering.",
    "values_above= for every value above a threshold (generalised Pareto); once_in= for other return periods.",
    "Coles (2001, 3.3.3) shows that normal-approximation intervals of long return levels are too narrow and too "
    "symmetric, and recommends the profile likelihood; maximum likelihood is extRemes's default (Gilleland & Katz "
    "2016). The interval search range starts at the normal interval, because extRemes needs one.",
    ("coles2001", "gilleland2016"), "P1",
    "Daily (or any sub-yearly) rows refused for block maxima; fewer than 15 blocks noted; once_in= at or below 1 "
    "refused; a fit that does not converge noted.")
BASIS["table.find_return_levels_of values_above="] = _b(
    "Every value above the threshold, fitted with a generalised Pareto curve by maximum likelihood (R extRemes), the "
    "readings per year from the dates, the extremal index with a note below 0.7, and no silent declustering.",
    "Leave values_above= out for yearly maxima; choose the threshold with chart.draw_threshold_check().",
    "The peaks-over-threshold model (Davison & Smith 1990; Coles 2001, ch. 4) uses more of the data than yearly "
    "maxima. Values above a threshold often come in runs; the extremal index (Ferro & Segers 2003) says how much, and "
    "declustering is left to the user, because the run length is a choice.",
    ("davison1990", "coles2001", "ferro2003"), "P1",
    "sorted_by= dates required, evenly spaced (daily, hourly, by the minute or monthly); empty readings refused; fewer "
    "than 10 values above refused and fewer than 30 noted.")
BASIS["draw_threshold_check"] = _b(
    "Two panels: the mean excess with its 95 % interval (extRemes::mrlplot) and the generalised Pareto shape with its "
    "95 % interval at 10 thresholds (extRemes::threshrange.plot).",
    "between= for the thresholds to look at.",
    "Coles (2001, 4.3.1) chooses the threshold where the mean excess becomes linear and the shape stays stable; the "
    "two panels are extRemes's own (Gilleland & Katz 2016).",
    ("coles2001", "gilleland2016"), "P1",
    "Fewer than 10 values above the highest threshold refused; a note when mrlplot's thresholds stop early.")
BASIS['table.fit_distribution_to distribution="gev"'] = _b(
    "The GEV fitted by maximum likelihood with SciPy (genextreme, then a numerical polish), the shape stored as xi.",
    "distribution=\"gumbel\" for xi = 0; \"generalised pareto\" for the amounts above a threshold.",
    "Maximum likelihood is the standard fit of the GEV (Coles 2001, 3.3); the xi sign follows Coles and extRemes, "
    "while SciPy's genextreme takes c = -xi, so simplydata turns it round and says so.",
    ("coles2001",), "P3", "", "convention")
BASIS['table.fit_distribution_to distribution="generalised pareto"'] = _b(
    "The generalised Pareto curve fitted by maximum likelihood with SciPy (genpareto with the threshold at 0), the "
    "shape as xi.",
    "Subtract the threshold first; find_return_levels_of(values_above=) does the whole peaks-over-threshold analysis.",
    "Maximum likelihood is the standard fit of the generalised Pareto curve to the amounts above a threshold "
    "(Davison & Smith 1990; Coles 2001, 4.3); SciPy's genpareto and extRemes share the xi sign.",
    ("davison1990", "coles2001"), "P3", "", "convention")

# ---- Small additions (S3c-4)
BASIS["table.find_percentile_of weights="] = _b(
    "Frequency weights (weight_kind=\"frequency\"): each row counts as often as its whole-number weight, the rows "
    "repeated and the usual linear rule used, as R quantile(rep(x, w)) and Hmisc::wtd.quantile(normwt = FALSE).",
    "weight_kind=\"analytic\" for sampling weights or precisions; test_method= as without weights.",
    "Repeating the rows keeps the one rule of the unweighted word (Hyndman & Fan 1996, type 7), so weights of 1 change "
    "nothing; NumPy's own weights= offers only the inverted CDF, a step, which gives another answer even with all "
    "weights 1. No study fixes how frequency weights enter a sample quantile; this follows the packages named.",
    ("hyndman1996",), "P3",
    "Weights that are not whole numbers are refused (pointing to weight_kind=\"analytic\"), as are negative weights "
    "and more than 10 million repeated rows; rows with an empty cell are skipped with a note.", "convention")
BASIS['table.find_percentile_of weight_kind="analytic"'] = _b(
    "The weighted inverted CDF (NumPy percentile(weights=, method=\"inverted_cdf\")), the rule of R "
    "survey::svyquantile(qrule = \"math\").",
    "weight_kind=\"frequency\" (whole-number weights, any test_method=).",
    "For sampling weights the population quantile is read from the weighted distribution function (Lumley 2004, the "
    "survey package; Hyndman & Fan 1996, definition 1); it is the only rule NumPy offers with weights.",
    ("lumley2004", "hyndman1996"), "P3",
    "test_method= other than the inverted CDF is refused with analytic weights; NumPy older than 2.0 is refused.",
    "convention")
BASIS["table.find_median_of weights="] = _b(
    "As find_percentile_of(weights=) at 50 %: frequency weights repeat the rows.",
    "weight_kind=\"analytic\".",
    "As table.find_percentile_of weights=.", ("hyndman1996",), "P3", "As table.find_percentile_of weights=.",
    "convention")
BASIS['table.find_correlation_between show="covariance"'] = _b(
    "The covariance table from pandas DataFrame.cov(): divide by n - 1, each pair on the rows where both columns "
    "have a number, as R cov(use = \"pairwise.complete.obs\").",
    "show=\"r\" (the correlation, without units).",
    "n - 1 gives the unbiased covariance, the default of pandas and R; pairwise rows follow the correlation table of "
    "the same word. R's own default (use = \"everything\") gives NA with any empty cell. No study is needed for "
    "this convention.", (), "P3",
    "Fewer than 2 rows for a pair is refused; test_method=, sides= and the test options are refused (a covariance has no "
    "test).", "convention")
BASIS['table.forecast order="automatic"'] = _b(
    "R forecast::auto.arima chooses the order and the seasonal order by AICc, trying every order (stepwise = FALSE, "
    "approximation = FALSE) for series of up to 1,000 readings.",
    "order=(p, d, q) and seasonal_order= given by you; methods other than \"arima\".",
    "auto.arima is the published automatic procedure (Hyndman & Khandakar 2008); its quicker stepwise search and the "
    "approximation can pick another order, so simplydata searches fully where that is fast. An order chosen from "
    "the data makes the intervals a little too narrow (Hyndman & Athanasopoulos 2021), which the printout says.",
    ("hyndman2008auto", "fpp3"), "P2",
    "seasonal_order= with order=\"automatic\" is refused; the chosen orders are printed; above 1,000 readings the "
    "quicker search is used and said.")
BASIS['table.add_adjusted_p_value_column test_method="storey"'] = _b(
    "Storey's q-values from R qvalue::qvalue() with its defaults: the share of true nulls (pi0) estimated from the "
    "p-values by the smoother over lambda = 0.05 to 0.95.",
    "test_method=\"benjamini-hochberg\" (pi0 = 1); \"local fdr\".",
    "Estimating pi0 makes the false discovery rate less conservative than Benjamini-Hochberg when many tests are "
    "real (Storey 2002; Storey & Tibshirani 2003); qvalue is the authors' own package. The gain needs many p-values: "
    "with few, pi0 is unstable.",
    ("storey2002", "storey2003", "benjamini1995"), "P2",
    "Fewer than 100 p-values get a note; when qvalue cannot estimate pi0 the word refuses and names "
    "Benjamini-Hochberg; p-values outside 0 to 1 are refused and empty ones skipped.")
BASIS['table.add_adjusted_p_value_column test_method="local fdr"'] = _b(
    "Each test's local false discovery rate from R qvalue::qvalue()$lfdr (pi0 from the smoother), in a column "
    "called \"local false discovery rate\".",
    "test_method=\"storey\" (q-values: about all the results at least this small).",
    "The local false discovery rate is the chance that one test is a false discovery (Efron et al. 2001); qvalue "
    "gives it with the same pi0 as the q-values (Storey & Tibshirani 2003).",
    ("efron2001", "storey2003"), "P2", "As test_method=\"storey\".")
BASIS['table.compare_each_pair_of matched_by=, test_method="nemenyi"'] = _b(
    "Nemenyi's test after Friedman's (R PMCMRplus::frdAllPairsNemenyiTest()), on the ranks within each matched row; "
    "its studentized range allows for all the pairs, so there is no further adjustment.",
    "The default (Wilcoxon signed-rank tests with Holm); test_method=\"conover\".",
    "Nemenyi's test is the usual follow-up to Friedman's in method comparisons (Demšar 2006), but mean-rank tests "
    "make each pair depend on the other groups in the study (Benavoli et al. 2016), so it is offered on request, "
    "with that note, and Wilcoxon-Holm stays the default.",
    ("demsar2006", "benavoli2016"), "P2",
    "Fewer than 3 groups is refused; rows not measured in every group are left out with a note.")
BASIS['table.compare_each_pair_of matched_by=, test_method="conover"'] = _b(
    "Conover's test after Friedman's (R PMCMRplus::frdAllPairsConoverTest()), with Holm's adjustment.",
    "test_method=\"nemenyi\"; the default Wilcoxon-Holm.",
    "Conover's test on the ranks within blocks is more powerful than Nemenyi's (Conover & Iman 1979); Holm keeps the "
    "chance of any false alarm at 5 % (Holm 1979), as for Conover after Kruskal-Wallis. PMCMRplus's default is "
    "single-step and scikit-posthocs adjusts nothing, so the printout says why their numbers differ. The same "
    "mean-rank caveat applies (Benavoli et al. 2016).",
    ("conover1979", "holm1979", "benavoli2016"), "P2", "As test_method=\"nemenyi\".")
BASIS['table.compare_each_pair_of based_on="percents"'] = _b(
    "Each pair by the 2 x 2 chi-square test with Yates' correction that compare_counts_of uses, Holm's adjustment, "
    "and the difference with Newcombe's interval: as R pairwise.prop.test() (whose default is the same).",
    "test_method=\"fisher\" (Fisher's exact test for each pair).",
    "Yates' correction (Yates 1934) makes the chi-square p-value closer to the exact one for small counts, at the cost "
    "of being conservative (Haviland 1990); simplydata keeps it so that each pair agrees with compare_counts_of, "
    "compare_risks and R. Holm controls the chance of any false alarm (Holm 1979); Newcombe's interval for the "
    "difference keeps its coverage (Newcombe 1998).",
    ("yates1934", "haviland1990", "holm1979", "newcombe1998"), "P3",
    "Expected counts below 5 get a note pointing to test_method=\"fisher\"; a pair whose rows all have one value gets no "
    "p-value (as R) and is left out of Holm's adjustment.", "convention")

# ---- Epidemiology and cause and effect (S3d-2)
BASIS["table.compare_balanced_groups_of"] = _b(
    "Weighting by the inverse of the propensity score (R WeightIt, method = \"glm\"), for everyone (ATE); the effect "
    "from WeightIt::lm_weightit() with M-estimation standard errors that allow for the estimated weights; a balance "
    "table of standardised differences before and after (R cobalt, every column, the guide 0.1).",
    "test_method=\"matching\"; effect_for=\"<a group>\" for the effect among that group (ATT); show=\"balance\" or "
    "\"propensity scores\".",
    "The propensity score balances the measured columns between the groups (Rosenbaum & Rubin 1983). Weighting keeps "
    "every row and gives the average effect for everyone; standard errors that ignore the estimated weights are "
    "wrong, which M-estimation corrects (Lunceford & Davidian 2004). Balance is judged by standardised differences, "
    "not by p-values, which depend on the number of rows (Austin 2009; Austin & Stuart 2015).",
    ("rosenbaum1983", "lunceford2004", "austin2009", "austin2015iptw"), "P2",
    "Two groups only; the overlap of the scores is printed with the rows outside it; columns still more than 0.1 "
    "apart after balancing get a note; weights above 20 get a note; the assumptions (no unmeasured column affecting "
    "both, overlap, a right propensity model) are printed every time.")
BASIS['table.compare_balanced_groups_of test_method="matching"'] = _b(
    "1:1 nearest-neighbour matching on the propensity score without replacement (R MatchIt's default), the effect "
    "among the rows of the effect_for= group (ATT) from lm() on the matched rows with standard errors clustered on "
    "the pairs (sandwich::vcovCL), as the MatchIt vignette does.",
    "match_within=0.2 (a caliper of 0.2 standard deviations of the logit of the score); test_method=\"weighting\" for the "
    "effect for everyone.",
    "Nearest-neighbour matching is the most used and best studied matching method (Stuart 2010; Ho et al. 2011). A "
    "caliper of 0.2 standard deviations of the logit of the score removes most of the bias in simulations (Austin "
    "2011); it is offered, not the default, because it changes the group the effect is about (unmatched rows leave).",
    ("stuart2010", "ho2011", "austin2011"), "P3",
    "effect_for= must name a group (matching gives the effect among one group; asked otherwise, it says to use "
    "weighting); rows left without a match are counted and named in a note.", "convention")
BASIS['table.compare_risks show="attributable fractions"'] = _b(
    "The attributable fraction among the exposed and in the whole population from R epiR::epi.2by2(method = "
    "\"cohort.count\"), with Wald intervals from the risk ratio; for an exposure that goes with fewer events, the "
    "preventable fraction among the exposed (epiR's fraction with the roles of the groups swapped).",
    "compare_risks() without show= (the risk difference, the risk and odds ratios, the number needed to treat).",
    "These are the standard definitions (Rockhill et al. 1998). The fractions here are crude: adjusting the "
    "population fraction for confounders needs a model, and a fraction from a crude risk ratio is biased when "
    "confounding is present (Rockhill et al. 1998), so the printout says \"crude\".",
    ("rockhill1998",), "P5",
    "Two groups only; the printout says that the risks must come from a cohort or cross-sectional study and that "
    "the fractions are causal only if the exposure causes the events.", "convention")
BASIS["table.rate_of standard_population="] = _b(
    "Direct standardisation with R epiR::epi.directadj(): the rate each group would have with the standard "
    "population's make-up, with Fay & Feuer's gamma interval (the same numbers as epitools::ageadjust.direct()).",
    "standard_population=\"whole table\" (the pooled person-time) or a table of population sizes; "
    "compare_rates(..., standard_rates=) for indirect standardisation.",
    "Fay & Feuer's interval keeps its coverage when a few bands hold most of the weight, where the normal interval "
    "fails (Fay & Feuer 1997).",
    ("fay1997",), "P2",
    "Bands missing from the standard or the table are refused and named; a group with no person-time in a band is "
    "refused (pointing to indirect standardisation).")
BASIS["table.compare_rates standard_rates="] = _b(
    "Indirect standardisation with R epiR::epi.indirectadj(): the expected events from the standard rates (per per= "
    "units of time), observed / expected (SMR) with its exact Poisson interval, and the p-value of R "
    "poisson.test(observed, expected).",
    "rate_of(..., standard_population=) for directly standardised rates.",
    "The exact Poisson interval of the observed count, divided by the expected, is the standard interval of an SMR "
    "(Ulm 1990). Indirect standardisation needs only the group's total events, so it works where some bands of a "
    "group are small.",
    ("ulm1990",), "P2",
    "Bands without a standard rate are refused and named; groups without person-time are refused; the printout says "
    "that two groups' ratios are each against the standard, not against each other.")
BASIS["table.explain through="] = _b(
    "Causal mediation analysis with statsmodels Mediation (Imai, Keele & Tingley's quasi-Bayesian algorithm, 1000 "
    "simulations, with_seed=1, as R mediation::mediate()): the indirect effect, the direct effect, the total effect "
    "and the share that goes through, averaged over the two exposure levels.",
    "outcome=\"yes or no\" (logistic models); against= the starting value of the exposure; allowing_for= the "
    "columns taken into account in both models.",
    "The counterfactual definition of the indirect effect holds for any model and states its assumption (sequential "
    "ignorability), unlike the Baron-Kenny steps (Imai, Keele & Tingley 2010); the quasi-Bayesian simulation is the "
    "default of the authors' own package (Tingley et al. 2014).",
    ("imai2010", "tingley2014"), "P2",
    "using= must be one column with two values; through= cannot be the exposure or a column of allowing_for=; the "
    "assumptions are printed every time; a share is said to mean little when the total effect is not clear.")
BASIS["table.compare_averages_of period="] = _b(
    "The EMA guideline's 2 x 2 crossover analysis with all effects fixed: statsmodels OLS of log(column) on sequence, "
    "subject, period and formulation; the ratio of the geometric means with its 90 % interval and the within-subject "
    "CV.",
    "same_within=[0.8, 1.25] (or 1.25) for the bioequivalence decision; against= the reference formulation.",
    "The 90 % interval on the log scale inside 80-125 % is the regulatory rule (EMA 2010), the same as two one-sided "
    "tests at 5 % (Schuirmann 1987). No test for carry-over comes first: the two-stage procedure biases the result "
    "(Freeman 1989). The model gives the published answers of the reference datasets (Schütz et al. 2014).",
    ("ema2010", "schuirmann1987", "freeman1989", "schutz2014"), "P1",
    "Two formulations in two periods only; subjects without both periods are left out and named; values of 0 or "
    "less are refused (the log scale); all subjects in one order is refused.")
BASIS['table.find_correlation_between empty_cells="multiple imputation"'] = _b(
    "The empty cells filled in 20 times by chained equations (statsmodels MICEData, predictive mean matching, as "
    "explain()), then Fisher's z of each table pooled with Rubin's rules and taken back to r by R "
    "miceadds::micombine.cor().",
    "empty_cells=\"leave out\" (the default: each pair on the rows where both columns have a number).",
    "Correlations are not normal near -1 and 1, so they are pooled on Fisher's z scale (van Buuren 2018, section "
    "5.2.3), with Rubin's rules (Rubin 1987).",
    ("vanbuuren2018", "rubin1987"), "P2",
    "test_method=\"pearson\" or \"spearman\" only; show=, sides=, p_value_by=, interval_by= and allowing_for= are refused "
    "with it; rows where every column is empty are left out with a note.")
BASIS['table.explain_survival empty_cells="multiple imputation"'] = _b(
    "The empty cells of the number columns of using= filled in 20 times (statsmodels MICEData) from the event, the "
    "Nelson-Aalen cumulative hazard (R mice::nelsonaalen()) and the other columns; R survival::coxph() on each "
    "filled-in table, pooled by R mice::pool() (Barnard-Rubin degrees of freedom).",
    "empty_cells=\"leave out\" (the default: rows with an empty cell are skipped).",
    "To fill in a covariate of a Cox model, the event and the cumulative hazard should be in the imputation model, "
    "not the time (White & Royston 2009); small-sample degrees of freedom follow Barnard & Rubin (1999).",
    ("white2009", "barnard1999", "rubin1987"), "P2",
    "A plain Cox model only (allowing_for=, followed_from=, competing_with=, distribution= and test_method=\"fine-gray\" "
    "are refused); empty cells in text columns, the time or the event leave those rows out.")

# ---- Planning and surveys (S3d-1)
BASIS["sdata.make_random_assignments"] = _b(
    "Permuted blocks from R blockrand::blockrand(): each block holds every group equally often, and without "
    "in_blocks_of= the block sizes are 2 and 3 times the number of groups, chosen at random block by block; R's "
    "generator is named in full (Mersenne-Twister, Inversion, Rejection) so that with_seed= repeats the list.",
    "in_blocks_of= (any multiples of the number of groups, one size or several); for_each_of= (one list per centre); "
    "groups= (names or a number).",
    "Blocks keep the groups about the same size all the way through, and random block sizes stop recruiters from "
    "guessing the last places of a block (Schulz & Grimes 2002a, 2002b; Efird 2011). The sizes 2 and 3 times the "
    "number of groups are simplydata's own starting value: no study fixes them.",
    ("schulz2002gen", "schulz2002conceal", "efird2011"), "P1",
    "Block sizes that are not a multiple of the number of groups are refused; the printout says the last block is "
    "completed and that the list must be kept from the people who recruit.")
BASIS["sdata.make_design_table"] = _b(
    "Every combination of the factors (a full factorial) in one random order (completely random), from R agricolae "
    "with R's own generator (kinds = \"Mersenne-Twister\", not agricolae's \"Super-Duper\"), and the standard order "
    "of R expand.grid().",
    "of_kind=\"randomised blocks\", \"latin square\" or \"split plot\" (with whole_plots=).",
    "Randomising the order of the plots spreads unknown differences evenly over the treatments, and true repeats of "
    "each combination are needed to measure the noise (Hurlbert 1984; Casler 2015). Completely random is the "
    "simplest layout; blocks are better when the plots differ in a known way, which the word cannot know, so it is "
    "offered, not chosen.",
    ("hurlbert1984", "casler2015"), "P2",
    "Factors need at least 2 levels and a name that is not one of the table's own columns; repeats= is required "
    "(at least 2 for blocks).")
BASIS['sdata.make_design_table of_kind="randomised blocks"'] = _b(
    "Each repeat is a block that holds every combination once, in its own random order (agricolae design.rcbd, or "
    "design.ab(design = \"rcbd\") for several factors).",
    "of_kind=\"completely random\" (the default), \"latin square\", \"split plot\".",
    "Blocks take known differences between groups of plots (benches, fields, days) out of the comparison (Casler "
    "2015).", ("casler2015",), "P2", "repeats= is the number of blocks and must be at least 2.")
BASIS['sdata.make_design_table of_kind="latin square"'] = _b(
    "One factor laid out in rows and columns so that each level is once in every row and every column (agricolae "
    "design.lsd).",
    "of_kind=\"randomised blocks\" when only one direction differs.",
    "A latin square removes differences in two directions at once (rows and columns of a field or a greenhouse) "
    "(Casler 2015).", ("casler2015",), "P2",
    "Exactly one factor with at least 3 levels; repeats= and whole_plots= are refused.")
BASIS['sdata.make_design_table of_kind="split plot"'] = _b(
    "Whole plots in randomised blocks get the factor named in whole_plots=, and each whole plot is split into parts "
    "for the other factor (agricolae design.split(design = \"rcbd\")).",
    "of_kind=\"randomised blocks\" when both factors can change plot by plot.",
    "A split plot is the layout for a factor that is hard to change on small plots, such as irrigation; it has two "
    "sizes of error, so it must be analysed as a split plot (Casler 2015).", ("casler2015",), "P2",
    "Exactly two factors, and whole_plots= naming one of them.")
BASIS["table.keep_random_rows for_each_group_in="] = _b(
    "The same number of random rows from each group (pandas groupby().sample(random_state=)), rows kept in table "
    "order; a group with that many rows or fewer is kept whole, with a note.",
    "percent= for the same share of each group; without for_each_group_in= the rows come from the whole table.",
    "A stratified random sample guarantees every group in the sample and is the usual design behind survey weights "
    "(Lumley 2010). Keeping a small group whole instead of stopping is simplydata's own choice, said in a note.",
    ("lumley2010",), "P5", "with_seed= must be a whole number; empty group cells form a group of their own.",
    "starting value")
BASIS["table.keep_random_rows percent="] = _b(
    "That share of each group, rounded by pandas (groupby().sample(frac=)), and at least 1 row of every group.",
    "A number of rows for each group.",
    "Proportional allocation keeps each group's share of the sample equal to its share of the table (Lumley 2010); "
    "at least one row per group keeps every stratum, simplydata's own choice.",
    ("lumley2010",), "P5", "percent= must be above 0 and up to 100; it cannot go with a number of rows.",
    "starting value")
BASIS['table.count_empty_cells_in show="patterns"'] = _b(
    "One row for each pattern of empty cells, with how many rows have it and how many cells it leaves empty (as R "
    "mice::md.pattern()), sorted by the number of empty cells, and the empty cells of each column printed below.",
    "Without show=, the empty cells of each column; chart.draw_map_of_empty_cells() draws every row.",
    "Which cells are empty together is the first step before choosing how to handle them: monotone patterns and "
    "rows with many empty cells call for different methods (van Buuren & Groothuis-Oudshoorn 2011).",
    ("vanbuuren2011",), "P5", "An empty cell is a missing value, NaN or text of only spaces, as everywhere in "
    "simplydata.")
BASIS["table.count_each columns=, in_order="] = _b(
    "For answers on a scale, the count and percent of each answer (of the answers given), the percent in the top "
    "two answers and the median answer (the inverted CDF, R quantile(type = 1)); no averages.",
    "chart.draw_answer_bars() for the same counts as diverging bars.",
    "The steps between answers on a Likert scale need not be equal, so the median and the shares are the safe "
    "summaries (Jamieson 2004); averages of many items can work (Norman 2010), but simplydata leaves that choice to "
    "you and does not average single items.",
    ("jamieson2004", "norman2010"), "P2",
    "in_order= is required (at least 3 answers); answers not in it are refused and named; empty cells are left out "
    "with a note.")
BASIS["draw_answer_bars"] = _b(
    "Diverging stacked bars: the answers below the middle to the left of 0, those above it to the right, and the "
    "middle answer split across 0; two hues with grey in the middle.",
    "table.count_each(columns=, in_order=) for the numbers.",
    "Diverging bars centred on the middle answer make agreement and disagreement comparable across questions "
    "(Heiberger & Robbins 2014).", ("heiberger2014",), "P2",
    "As table.count_each(columns=, in_order=); with an even number of answers the bars meet at 0 between the middle "
    "two.")
BASIS["table.use_survey_design"] = _b(
    "R survey::svydesign() with the columns given; options(survey.lonely.psu = \"adjust\") and nest = TRUE; from "
    "then on the survey words give design-based answers and the other statistics words refuse.",
    "table.use_survey_design() with no options turns it off.",
    "Analysing a complex sample as if it were a simple random sample gives standard errors that are too small "
    "(Lumley 2010; Korn & Graubard 1999). survey stops by default when a stratum has one cluster; \"adjust\" is the "
    "conservative option Lumley describes (Lumley 2010).",
    ("lumley2010", "korn1999", "lumley2004"), "P1",
    "Empty design cells and weights of 0 or less are refused; the printout says how the population sizes were read; "
    "a survey word refuses after rows were removed.")
_SURVEY_DF = ("A t interval on the design's degrees of freedom, not survey's own normal-curve confint(): with few "
              "clusters or strata the normal curve gives intervals that are too narrow (Korn & Graubard 1999).")
BASIS["table.find_average_of after use_survey_design()"] = _b(
    "The population average from R survey::svymean() (svyby() for groups), its standard error from the design, and "
    "a t interval on the design's degrees of freedom (degf).",
    "table.use_survey_design() off for the average of the rows.", _SURVEY_DF + " survey is Lumley's reference "
    "implementation (Lumley 2004).", ("lumley2004", "korn1999"), "P1",
    "Only column= and for_each_group_in= (one column) are taken; empty cells are left out as survey does.")
BASIS["table.find_total_of after use_survey_design()"] = _b(
    "The estimated population total from R survey::svytotal(), with a t interval on the design's degrees of freedom.",
    "table.use_survey_design() off for the total of the rows.", _SURVEY_DF, ("lumley2004", "korn1999"), "P1",
    "As find_average_of under a survey design.")
BASIS["table.find_median_of after use_survey_design()"] = _b(
    "The population median from R survey::svyquantile(qrule = \"math\") with Woodruff's interval on the design's "
    "degrees of freedom.",
    "find_percentile_of for other percents.",
    "Woodruff's method turns the interval of the distribution function into an interval for the quantile, which "
    "keeps the design (Woodruff 1952; Lumley 2010).", ("woodruff1952", "lumley2010"), "P1",
    "As find_average_of under a survey design.")
BASIS["table.find_percentile_of after use_survey_design()"] = _b(
    "As find_median_of under a survey design, at the percent given.", "test_method= and interval= are refused here.",
    "As table.find_median_of after use_survey_design().", ("woodruff1952", "lumley2010"), "P1",
    "As find_average_of under a survey design.")
BASIS["table.find_percent_of_rows_where after use_survey_design()"] = _b(
    "The population percent from R survey::svyciprop(method = \"logit\"), its interval worked out on the log-odds "
    "scale and on the design's degrees of freedom.",
    "table.use_survey_design() off for the exact interval of the rows.",
    "The logit interval stays between 0 and 100 % and keeps its coverage better than the plain Wald interval for "
    "survey proportions near 0 or 100 % (Korn & Graubard 1999; Lumley 2010).", ("korn1999", "lumley2010"), "P2",
    "One condition and for_each_group_in= are taken; shares of a total go to find_total_of.")
BASIS["table.count_rows after use_survey_design()"] = _b(
    "The estimated number in the population: R survey::svytotal() of a column of ones (the sum of the weights); with "
    "in_percent=True each group's share, svymean(~factor(group)).",
    "table.use_survey_design() off for the number of rows.",
    "Population counts and shares come from the weights and their design-based standard errors (Lumley 2010).",
    ("lumley2010",), "P1", "in_percent=True needs for_each_group_in=.")
BASIS["table.explain after use_survey_design()"] = _b(
    "A survey-weighted model from R survey::svyglm(): gaussian for numbers, quasibinomial for yes or no, "
    "quasipoisson for counts, with survey's t tests and intervals on the model's residual degrees of freedom.",
    "outcome= \"numbers\", \"yes or no\" or \"counts\".",
    "Design-based regression weights each row by its sampling weight and takes the standard errors from the design "
    "(Lumley 2010); the quasi families avoid the warnings that non-whole weights give in binomial and Poisson fits.",
    ("lumley2010",), "P1", "Only column=, using= and outcome= are taken; yes or no outcomes need yes/no, 1/0 or "
    "True/False.")
BASIS["table.compare_averages_of after use_survey_design()"] = _b(
    "The design-based t test of R survey::svyttest() for two groups.",
    "table.explain(column, using=[group]) for more than two groups.",
    "The difference and its standard error come from the design, so the test keeps its size under clustering and "
    "weighting (Lumley 2010).", ("lumley2010",), "P1", "Exactly two groups are needed.")
BASIS["table.compare_counts_of after use_survey_design()"] = _b(
    "Pearson's chi-square with the Rao-Scott correction, as an F test (R survey::svychisq(), statistic = \"F\").",
    "table.use_survey_design() off for the chi-square test of the rows.",
    "The plain chi-square test is too liberal on survey data; the Rao-Scott second-order correction keeps it close "
    "to its nominal size (Rao & Scott 1984).", ("rao1984",), "P1", "for_each_group_in= is required.")

# ---- Bayesian methods (S3d-3)
_BF_WHY = ("A Bayes factor says how much more likely the data are under one hypothesis than under the other, so it can "
           "also speak for no difference, which a p-value cannot (Rouder et al. 2009; Wagenmakers et al. 2018). The "
           "default prior widths are BayesFactor's (the field's reference software, also used by JASP for t tests); "
           "the Bayesian reporting guidelines ask for the prior to be stated and for its influence to be checked "
           "(Kruschke 2021), so the width is printed and prior_width= changes it. The interval comes from 10,000 "
           "posterior draws with a fixed seed, so it is the same on every run.")
_BF_CHECKS = ("The other options of the usual test are refused with test_method=\"bayesian\"; prior_width= without test_method=\"bayesian\" "
              "is refused; no p-value and no verdict words are printed.")
BASIS["table.compare_averages_of test_method=\"bayesian\""] = _b(
    "The JZS Bayes factor t-test for two groups from R BayesFactor::ttestBF(), with a Cauchy prior of medium width "
    "(r = 0.707) on the effect size, and the 95 % credible interval of the difference from BayesFactor::posterior().",
    "prior_width=\"wide\" (1), \"ultrawide\" (1.414) or a number; bayesian=False for Welch's t-test.",
    _BF_WHY, ("rouder2009", "wagenmakers2018", "kruschke2021"), "P3", "Exactly two groups; " + _BF_CHECKS,
    "convention")
BASIS["table.compare_before_and_after test_method=\"bayesian\""] = _b(
    "The JZS Bayes factor paired t-test (R BayesFactor::ttestBF(after, before, paired = TRUE)), medium width, and the "
    "95 % credible interval of the average change.",
    "prior_width=\"wide\", \"ultrawide\" or a number; bayesian=False for the paired t-test.",
    _BF_WHY, ("rouder2009", "wagenmakers2018", "kruschke2021"), "P3", "Both columns must hold numbers; " + _BF_CHECKS,
    "convention")
BASIS["table.compare_average_to test_method=\"bayesian\""] = _b(
    "The JZS Bayes factor one-sample t-test (R BayesFactor::ttestBF() on the values minus the number), medium width, "
    "and the 95 % credible interval of the average minus the number.",
    "prior_width=\"wide\", \"ultrawide\" or a number; bayesian=False for the one-sample t-test.",
    _BF_WHY + " BayesFactor's posterior() leaves its mu = argument out, so the number is taken away first; the Bayes "
    "factor is the same either way.", ("rouder2009", "wagenmakers2018", "kruschke2021"), "P3", _BF_CHECKS,
    "convention")
BASIS["table.find_correlation_between test_method=\"bayesian\""] = _b(
    "The Bayes factor for a correlation from R BayesFactor::correlationBF(), with a stretched beta prior of medium "
    "width (1/3), and the 95 % credible interval of the correlation.",
    "prior_width=\"wide\" (0.577), \"ultrawide\" (1) or a number; bayesian=False for Pearson's test.",
    _BF_WHY + " JASP's default width for correlations is 1, so its Bayes factors differ; the printout says so "
    "(Ly, Verhagen & Wagenmakers 2016).", ("ly2016", "wagenmakers2018", "kruschke2021"), "P3",
    "Exactly two columns; " + _BF_CHECKS, "convention")
BASIS["table.compare_counts_of test_method=\"bayesian\""] = _b(
    "The Gunel-Dickey Bayes factor for a table of counts from R BayesFactor::contingencyTableBF(), with independent "
    "multinomial sampling and each group's total fixed (the groups are the rows), prior concentration 1, and each "
    "group's shares with 95 % credible intervals.",
    "bayesian=False for the chi-square test.",
    "A Bayes factor for a table depends on how the data were collected; with groups chosen first (such as wards or "
    "exposure groups) each group's total is fixed, which is independent multinomial sampling (Gunel & Dickey 1974; "
    "Jamil et al. 2017). The printout names the sampling plan. Concentration 1 is BayesFactor's default.",
    ("gunel1974", "jamil2017", "kruschke2021"), "P3", _BF_CHECKS, "convention")
BASIS["table.explain test_method=\"bayesian\""] = _b(
    "A Bayesian regression from R rstanarm::stan_glm() (numbers, yes or no, counts) with rstanarm's default weakly "
    "informative priors scaled to the data, 4 chains of 2000 iterations and seed = with_seed; each effect as the "
    "posterior median with its central 95 % credible interval; rank-normalised R-hat and bulk and tail effective "
    "draws from the posterior package.",
    "grouped_by= for a mixed model (stan_glmer); bayesian=False for the usual model.",
    "Weakly informative priors keep estimates stable without overruling the data (Gelman et al. 2008); the reporting "
    "guidelines ask for the priors, the convergence measures and the interval type to be stated (Kruschke 2021). "
    "The older R-hat misses some problems; the rank-normalised R-hat with the guide 1.01 and at least 400 effective "
    "draws are the current recommendation (Vehtari et al. 2021). 4 chains of 2000 iterations are rstanarm's "
    "defaults.", ("gelman2008prior", "vehtari2021", "kruschke2021"), "P1",
    "Warnings come before any estimate when R-hat is above 1.01, there are fewer than 400 effective draws or any "
    "divergent transition, each with what to do; options other than outcome=, grouped_by= and with_seed= are refused.")
BASIS["table.explain test_method=\"bayesian\", grouped_by="] = _b(
    "A Bayesian mixed model from R rstanarm::stan_glmer() with its own starting level for each group, (1 | group), "
    "and rstanarm's decov prior for the group spread; otherwise as explain(test_method=\"bayesian\").",
    "bayesian=False for lme4.",
    "As explain(test_method=\"bayesian\"); every group's own level is checked for convergence too (Vehtari et al. 2021).",
    ("vehtari2021", "kruschke2021"), "P1", "One grouped_by= column.")
BASIS["table.check_model_of test_method=\"bayesian\""] = _b(
    "The posterior predictive check: the data against 50 sets made up by the fitted model (rstanarm "
    "posterior_predict()), as densities for numbers (R stats::density(), as bayesplot::ppc_dens_overlay) and as "
    "bars with the median and 90 % interval of the made-up counts for yes/no and counts (as bayesplot::ppc_bars).",
    "show=\"prior check\" for the prior predictive check (prior_PD = TRUE).",
    "Pictures of the data against data made up by the model show what a model misses better than one number, and the "
    "prior predictive check shows whether a prior allows impossible values (Gabry et al. 2019). 50 sets is what "
    "bayesplot's pp_check() draws by default.", ("gabry2019",), "P2",
    "The same convergence warnings as explain(test_method=\"bayesian\").")

