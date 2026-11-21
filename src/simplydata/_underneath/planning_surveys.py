"""Planning an experiment and survey answers (phase S3d-1): the design words (R blockrand and agricolae), stratified
random rows (pandas), patterns of empty cells (pandas), answers on a scale (pandas and matplotlib) and the survey
words (R survey). Practice tables: "marks", "shop", "course_feedback" (made up) and "sampled_schools" (the R survey
package's apistrat, real).
"""

from . import Entry

SURVEY_OURS = """
    table = sdata.table(sdata.get_example("sampled_schools"))
    table.use_survey_design(weights="weight", strata="school_type", population_sizes="schools_of_type")
"""
SCHOOLS = """
    df = sdata.get_example("sampled_schools")
    w = df["weight"].to_numpy(dtype=float)
    s = df["school_type"].to_numpy(dtype=str)
    f = df["schools_of_type"].to_numpy(dtype=float)
"""
DESIGN_R = """d <- survey::svydesign(ids = ~1, strata = ~s, weights = ~w, fpc = ~f,
                       data = data.frame(s, w, f, y))"""
SURVEY_NOTE = ("statsmodels has weights but no strata, clusters or population sizes, so the design-based numbers come "
               "from R survey (Lumley).")
DF_CHOICE = ("the 95 % interval uses t on the design's degrees of freedom (degf(design), here 197), not survey's own "
             "normal-curve confint().")
LEVELS = '["strongly disagree", "disagree", "neutral", "agree", "strongly agree"]'
QUESTIONS = '["teaching", "materials", "pace", "workload", "would_recommend"]'


def _survey(word, option, call, r_code, fields, y_line, choices, also, row="", data_line=""):
    return Entry(
        word=word, option=option, data="sampled_schools",
        ours=SURVEY_OURS + f"    {call}\n",
        code={"R": r_code, "Python": "{" + ", ".join(f'"{k}": {v}' for k, v in fields.items()) + "}\n"},
        r_inputs=SCHOOLS + y_line + data_line, r_packages=("survey",), compare="result", fields=tuple(fields),
        row=row, tolerance=1e-9, choices=choices, python_note=SURVEY_NOTE, also=also)


ENTRIES = [
    # ------------------------------------------------------------------ V03: random assignments
    Entry(
        word="sdata.make_random_assignments",
        ours="""
            sdata.make_random_assignments(how_many=20, groups=["A", "B"], in_blocks_of=[4, 6], with_seed=1)
        """,
        code={
            "R": """
                # make_random_assignments(how_many=20, groups=["A", "B"], in_blocks_of=[4, 6], with_seed=1)
                set.seed(1, kind = "Mersenne-Twister", normal.kind = "Inversion",
                         sample.kind = "Rejection")                                # (1)
                b <- blockrand::blockrand(n = 20, num.levels = 2, levels = groups,
                                          block.sizes = c(4, 6) / 2)                # (2)
                list(number = b$id, block = as.numeric(as.character(b$block.id)),
                     size = b$block.size, group = as.numeric(b$treatment))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"number": number.astype(int), "block": block.astype(int),
                              "block size": size.astype(int),
                              "group": [["A", "B"][int(i) - 1] for i in group]})
            """,
        },
        r_inputs="""
            import numpy as np
            groups = np.array(["A", "B"], dtype=object)
        """,
        r_packages=("blockrand",), compare="table", tolerance=1e-12,
        choices=("R's generator named in full (Mersenne-Twister, Inversion, Rejection): sample() changed in R 3.6.0, "
                 "so the same seed gives another list in older R.",
                 "real block sizes, divided by the number of groups for blockrand (which counts in multiples of it); "
                 "without in_blocks_of= simplydata chooses 2 and 3 times the number of groups, of random sizes."),
        python_note="Python has no package for permuted-block randomisation lists, so the list comes from R blockrand "
                    "(Snow).",
        also="simplydata also refuses block sizes that are not a multiple of the number of groups, makes one list for "
             "each name in for_each_of=, says the last block is completed, and reminds you to keep the list from "
             "the people who recruit.",
    ),
    # ------------------------------------------------------------------ V04 / V06: design tables
    Entry(
        word="sdata.make_design_table",
        ours="""
            sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, with_seed=1)
        """,
        code={
            "R": """
                # make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, with_seed=1)
                d <- agricolae::design.ab(levels_per_factor, r = 3, design = "crd", serie = 0, seed = 1,
                                          kinds = "Mersenne-Twister")             # (1)
                b <- d$book
                g <- expand.grid(1:2, 1:2)
                list(plot = b$plots, rep = as.numeric(as.character(b$r)), A = as.numeric(as.character(b$A)),
                     B = as.numeric(as.character(b$B)),
                     standard = match(paste(b$A, b$B), paste(g[[1]], g[[2]])))     # (2)
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"plot": plot.astype(int), "repeat": rep.astype(int),
                              "temperature": [[10, 20][int(i) - 1] for i in A],
                              "salinity": [[30, 35][int(i) - 1] for i in B],
                              "standard order": standard.astype(int)})
            """,
        },
        r_inputs="""
            import numpy as np
            levels_per_factor = np.array([2.0, 2.0])
        """,
        r_packages=("agricolae",), compare="table", tolerance=1e-12,
        choices=("R's own generator (kinds = \"Mersenne-Twister\"), not agricolae's default \"Super-Duper\", so "
                 "with_seed= gives the layout an R user gets after set.seed().",
                 "the standard order is R expand.grid() order: the first factor changes fastest (Yates' order)."),
        python_note="Python has no package for randomised experimental layouts, so the table comes from R agricolae "
                    "(de Mendiburu).",
        also="simplydata also names the factors and levels you gave (agricolae numbers them), keeps numbers as "
             "numbers, and refuses a factor named like a column the table makes.",
    ),
    Entry(
        word="sdata.make_design_table", option='of_kind="randomised blocks"',
        ours="""
            sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3,
                                    of_kind="randomised blocks", with_seed=1)
        """,
        code={
            "R": """
                # make_design_table(..., repeats=3, of_kind="randomised blocks", with_seed=1)
                d <- agricolae::design.ab(levels_per_factor, r = 3, design = "rcbd", serie = 0, seed = 1,
                                          kinds = "Mersenne-Twister")             # (1)
                b <- d$book
                g <- expand.grid(1:2, 1:2)
                list(plot = b$plots, block = as.numeric(as.character(b$block)), A = as.numeric(as.character(b$A)),
                     B = as.numeric(as.character(b$B)), standard = match(paste(b$A, b$B), paste(g[[1]], g[[2]])))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"plot": plot.astype(int), "block": block.astype(int),
                              "temperature": [[10, 20][int(i) - 1] for i in A],
                              "salinity": [[30, 35][int(i) - 1] for i in B],
                              "standard order": standard.astype(int)})
            """,
        },
        r_inputs="""
            import numpy as np
            levels_per_factor = np.array([2.0, 2.0])
        """,
        r_packages=("agricolae",), compare="table", tolerance=1e-12,
        choices=("each repeat is a block holding every combination once, in its own random order "
                 "(agricolae design.ab(design = \"rcbd\")).",),
        python_note="As make_design_table.",
        also="With one factor simplydata calls agricolae::design.rcbd() instead.",
    ),
    Entry(
        word="sdata.make_design_table", option='of_kind="latin square"',
        ours="""
            sdata.make_design_table({"variety": ["A", "B", "C", "D"]}, of_kind="latin square", with_seed=1)
        """,
        code={
            "R": """
                # make_design_table({"variety": ["A", "B", "C", "D"]}, of_kind="latin square", with_seed=1)
                d <- agricolae::design.lsd(variety, serie = 0, seed = 1,
                                           kinds = "Mersenne-Twister")            # (1)
                b <- d$book
                list(plot = b$plots, row = as.numeric(as.character(b$row)), col = as.numeric(as.character(b$col)),
                     v = match(b[[4]], variety))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"plot": plot.astype(int), "row": row.astype(int), "column": col.astype(int),
                              "variety": [["A", "B", "C", "D"][int(i) - 1] for i in v]})
            """,
        },
        r_inputs="""
            import numpy as np
            variety = np.array(["A", "B", "C", "D"], dtype=object)
        """,
        r_packages=("agricolae",), compare="table", tolerance=1e-12,
        choices=("agricolae design.lsd: each level once in every row and every column, rows and columns in random "
                 "order.",),
        python_note="As make_design_table.",
        also="simplydata also refuses more than one factor, fewer than 3 levels and repeats= (one square).",
    ),
    Entry(
        word="sdata.make_design_table", option='of_kind="split plot"',
        ours="""
            sdata.make_design_table({"irrigation": ["dry", "wet"], "variety": ["A", "B", "C"]}, repeats=2,
                                    of_kind="split plot", whole_plots="irrigation", with_seed=1)
        """,
        code={
            "R": """
                # make_design_table(..., repeats=2, of_kind="split plot", whole_plots="irrigation", with_seed=1)
                d <- agricolae::design.split(irrigation, variety, r = 2, design = "rcbd",
                                             serie = 0, seed = 1, kinds = "Mersenne-Twister")   # (1)
                b <- d$book
                list(whole = b$plots, part = as.numeric(as.character(b$splots)),
                     block = as.numeric(as.character(b$block)), i = match(b[[4]], irrigation),
                     v = match(b[[5]], variety))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"whole plot": whole.astype(int), "part of plot": part.astype(int),
                              "block": block.astype(int),
                              "irrigation": [["dry", "wet"][int(k) - 1] for k in i],
                              "variety": [["A", "B", "C"][int(k) - 1] for k in v]})
            """,
        },
        r_inputs="""
            import numpy as np
            irrigation = np.array(["dry", "wet"], dtype=object)
            variety = np.array(["A", "B", "C"], dtype=object)
        """,
        r_packages=("agricolae",), compare="table", tolerance=1e-12,
        choices=("whole plots in randomised blocks (agricolae design.split(design = \"rcbd\")), the factor named in "
                 "whole_plots= on the whole plots.",),
        python_note="As make_design_table.",
        also="simplydata also refuses a split plot without exactly two factors or without whole_plots=.",
    ),
    # ------------------------------------------------------------------ V02: stratified random rows
    Entry(
        word="table.keep_random_rows", option="for_each_group_in=",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.keep_random_rows(2, for_each_group_in="class", with_seed=1)
        """,
        code={"pandas": """
            df = sdata.get_example("marks")
            # keep_random_rows(2, for_each_group_in="class", with_seed=1)
            df.groupby("class").sample(n=2, random_state=1).sort_index()   # (1)
        """},
        compare="table", tolerance=1e-12,
        choices=("the rows keep their order in the table (sort_index()); a group with n rows or fewer is kept whole, "
                 "with a note (pandas stops with an error).",),
        also="The same pandas call on a Polars table (simplydata takes the rows it picks).",
    ),
    Entry(
        word="table.keep_random_rows", option="percent=",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.keep_random_rows(percent=30, for_each_group_in="class", with_seed=1)
        """,
        code={"pandas": """
            df = sdata.get_example("marks")
            # keep_random_rows(percent=30, for_each_group_in="class", with_seed=1)
            df.groupby("class").sample(frac=0.3, random_state=1).sort_index()   # (1)
        """},
        compare="table", tolerance=1e-12,
        choices=("pandas rounds each group's share; a group whose share rounds to no row still gets one row (a "
                 "stratified sample keeps every stratum).",),
        also="Without for_each_group_in=, percent= keeps that share of the whole table (pandas sample(frac=)).",
    ),
    # ------------------------------------------------------------------ X06: patterns of empty cells
    Entry(
        word="table.count_empty_cells_in", option='show="patterns"',
        data="shop",
        ours="""
            table = sdata.table(sdata.get_example("shop"))
            table.count_empty_cells_in(show="patterns")
        """,
        code={"pandas": """
            df = sdata.get_example("shop")
            # count_empty_cells_in(show="patterns")
            p = df.isna().value_counts().reset_index(name="rows with this pattern")   # (1)
            p["empty cells"] = p[list(df.columns)].sum(axis=1)
            p = p.sort_values(["empty cells", "rows with this pattern"], ascending=[True, False])
            p[list(df.columns)] = p[list(df.columns)].replace({True: "empty", False: "filled"})
            p[["rows with this pattern"] + list(df.columns) + ["empty cells"]]
        """},
        compare="table", tolerance=1e-12,
        choices=("an empty cell is a missing value, NaN or text of only spaces (as count_empty_cells_in); the "
                 "patterns are sorted by how many cells they leave empty, then by how many rows have them (R "
                 "mice::md.pattern() sorts by its own rule and turns the columns round).",),
        also="simplydata also prints the empty cells of each column and how many rows have none.",
    ),
    # ------------------------------------------------------------------ W06: answers on a scale
    Entry(
        word="table.count_each", option="columns=, in_order=",
        data="course_feedback",
        ours=f"""
            table = sdata.table(sdata.get_example("course_feedback"))
            table.count_each(columns={QUESTIONS},
                             in_order={LEVELS})
        """,
        code={"pandas and NumPy": f"""
            import numpy as np
            df = sdata.get_example("course_feedback")
            levels = {LEVELS}
            # count_each(columns=[...], in_order=levels), the first question
            x = df["teaching"].dropna()
            counts = x.value_counts().reindex(levels, fill_value=0)              # (1)
            places = x.map({{v: i for i, v in enumerate(levels)}}).to_numpy()
            {{"agree": counts["agree"], "percent agree": counts["agree"] * 100 / len(x),
             "percent in top two": x.isin(levels[-2:]).mean() * 100,
             "median answer": levels[int(np.quantile(places, 0.5, method="inverted_cdf"))]}}   # (2)
        """},
        compare="result", fields=("agree", "percent agree", "percent in top two", "median answer"), tolerance=1e-12,
        choices=("percents out of the answers given (empty cells left out), and no averages of the answers: the "
                 "steps between them need not be equal.",
                 "the median answer is a real answer, the inverted CDF (R quantile(type = 1)), never a value between "
                 "two."),
        also="simplydata also refuses answers that are not in in_order= (naming them) and fewer than 3 answers.",
    ),
    Entry(
        word="draw_answer_bars",
        data="course_feedback",
        ours=f"""
            chart = sdata.chart(sdata.get_example("course_feedback"))
            chart.draw_answer_bars(columns=["teaching", "pace"],
                                   in_order={LEVELS})
        """,
        code={"matplotlib": f"""
            import matplotlib.pyplot as plt
            import numpy as np
            df = sdata.get_example("course_feedback")
            levels = {LEVELS}
            fig, ax = plt.subplots()
            # draw_answer_bars(columns=["teaching", "pace"], in_order=levels)
            p = np.array([df[q].dropna().value_counts(normalize=True).reindex(levels, fill_value=0) * 100
                          for q in ["teaching", "pace"]])
            start = -(p[:, 0] + p[:, 1] + p[:, 2] / 2)                     # (1)
            left = start[:, None] + np.cumsum(p, axis=1) - p
            for j in range(5):
                ax.barh([1, 0], p[:, j], left=left[:, j], height=0.7)
        """},
        compare="chart", check=("bars",), tolerance=1e-9,
        choices=("diverging bars (Heiberger & Robbins 2014): the answers below the middle to the left of 0, the middle "
                 "answer split half and half across 0, and the first question at the top.",),
        also="simplydata also colours the two halves in two hues with grey in the middle, labels the questions and "
             "the answers, and prints how the bars are centred.",
    ),
    # ------------------------------------------------------------------ W01 / W02: survey designs
    Entry(
        word="table.use_survey_design", data="sampled_schools",
        ours=SURVEY_OURS,
        compare="none",
        note="A setting, not a calculation: it remembers the design columns, checks them (R survey::svydesign() and "
             "degf()), and from then on the survey words build the design in R and the other statistics words "
             "refuse.",
        choices=('options(survey.lonely.psu = "adjust") (survey\'s own default stops when a stratum has only one '
                 "cluster); clusters with the same name in two strata are kept apart (nest = TRUE).",),
        also="simplydata also refuses empty design cells and weights of 0 or less, and says whether the population "
             "sizes were read as numbers or as shares sampled.",
    ),
    _survey("table.find_average_of", "after use_survey_design()", 'table.find_average_of("score_2000")',
            f"""
                # find_average_of("score_2000") under use_survey_design(...)
                {DESIGN_R}
                m <- survey::svymean(~y, d)
                ci <- confint(m, df = survey::degf(d))                         # (1)
                list(est = coef(m), se = survey::SE(m), low = ci[1], high = ci[2])
            """,
            {"average of score_2000": "est", "standard error": "se", "average of score_2000 95 % CI low": "low",
             "average of score_2000 95 % CI high": "high"},
            '    y = df["score_2000"].to_numpy(dtype=float)\n', (DF_CHOICE,),
            "simplydata also prints that the numbers describe the population, and leaves out empty cells as survey "
            "does (na.rm = TRUE) while keeping the design."),
    _survey("table.find_total_of", "after use_survey_design()", 'table.find_total_of("pupils")',
            f"""
                # find_total_of("pupils") under use_survey_design(...)
                {DESIGN_R}
                m <- survey::svytotal(~y, d)
                ci <- confint(m, df = survey::degf(d))                         # (1)
                list(est = coef(m), se = survey::SE(m), low = ci[1], high = ci[2])
            """,
            {"total of pupils": "est", "standard error": "se", "total of pupils 95 % CI low": "low",
             "total of pupils 95 % CI high": "high"},
            '    y = df["pupils"].to_numpy(dtype=float)\n', (DF_CHOICE,), "As find_average_of."),
    _survey("table.find_median_of", "after use_survey_design()", 'table.find_median_of("score_2000")',
            f"""
                # find_median_of("score_2000") under use_survey_design(...)
                {DESIGN_R}
                q <- survey::svyquantile(~y, d, quantiles = 0.5, qrule = "math", ci = TRUE,
                                         df = survey::degf(d))$y                # (1)
                list(est = q[1, 1], se = q[1, 4], low = q[1, 2], high = q[1, 3])
            """,
            {"median of score_2000": "est", "standard error": "se", "median of score_2000 95 % CI low": "low",
             "median of score_2000 95 % CI high": "high"},
            '    y = df["score_2000"].to_numpy(dtype=float)\n',
            ('the population median by the weighted inverted CDF (qrule = "math", as find_percentile_of('
             'weight_kind="analytic")), with Woodruff\'s interval on the design\'s degrees of freedom.',),
            "As find_average_of; find_percentile_of gives any other percent."),
    _survey("table.find_percentile_of", "after use_survey_design()", 'table.find_percentile_of("score_2000", 90)',
            f"""
                # find_percentile_of("score_2000", 90) under use_survey_design(...)
                {DESIGN_R}
                q <- survey::svyquantile(~y, d, quantiles = 0.9, qrule = "math", ci = TRUE,
                                         df = survey::degf(d))$y                # (1)
                list(est = q[1, 1], se = q[1, 4], low = q[1, 2], high = q[1, 3])
            """,
            {"percentile 90 of score_2000": "est", "standard error": "se",
             "percentile 90 of score_2000 95 % CI low": "low", "percentile 90 of score_2000 95 % CI high": "high"},
            '    y = df["score_2000"].to_numpy(dtype=float)\n',
            ('as find_median_of under a survey design: qrule = "math" and Woodruff\'s interval on the design\'s degrees '
             "of freedom.",), "As find_average_of."),
    _survey("table.find_percent_of_rows_where", "after use_survey_design()",
            'table.find_percent_of_rows_where("met_target", is_equal_to="yes")',
            f"""
                # find_percent_of_rows_where("met_target", is_equal_to="yes") under use_survey_design(...)
                {DESIGN_R}
                p <- survey::svyciprop(~y, d, method = "logit")                 # (1)
                ci <- attr(p, "ci")
                list(est = coef(p) * 100, se = survey::SE(p) * 100, low = ci[1] * 100, high = ci[2] * 100)
            """,
            {"percent": "est", "standard error": "se", "percent 95 % CI low": "low", "percent 95 % CI high": "high"},
            '    y = (df["met_target"] == "yes").to_numpy(dtype=float)\n',
            ("survey's logit interval (svyciprop(method = \"logit\")), which stays between 0 and 100 %, on the "
             "design's degrees of freedom; the share is shown in percent.",), "As find_average_of."),
    _survey("table.count_rows", "after use_survey_design()", "table.count_rows(for_each_group_in=\"award\")",
            f"""
                # count_rows(for_each_group_in="award") under use_survey_design(...)
                {DESIGN_R}
                m <- survey::svyby(~y, ~a, d, survey::svytotal)                 # (1)
                ci <- confint(m, df = survey::degf(d))
                list(est = coef(m)[1], se = survey::SE(m)[1], low = ci[1, 1], high = ci[1, 2])
            """,
            {"population count": "est", "standard error": "se", "population count 95 % CI low": "low",
             "population count 95 % CI high": "high"},
            '    import numpy as np\n    y = np.ones(len(df))\n    a = df["award"].to_numpy(dtype=str)\n',
            ("the estimated number in the population is survey's total of a column of ones (the sum of the weights); "
             "in_percent=True gives each group's share, svymean(~factor(group)).",), "As find_average_of.",
            data_line=""),
    _survey("table.explain", "after use_survey_design()",
            'table.explain("score_2000", using=["english_learners", "free_meals"])',
            f"""
                # explain("score_2000", using=["english_learners", "free_meals"]) under use_survey_design(...)
                d <- survey::svydesign(ids = ~1, strata = ~s, weights = ~w, fpc = ~f,
                                       data = data.frame(s, w, f, y, e, m))
                fit <- survey::svyglm(y ~ e + m, design = d)                    # (1)
                s <- summary(fit)$coefficients
                ci <- confint(fit)
                list(est = s[3, 1], se = s[3, 2], p = s[3, 4], low = ci[3, 1], high = ci[3, 2])
            """,
            {"estimate": "est", "standard error": "se", "p-value": "p", "95 % CI low": "low", "95 % CI high": "high"},
            '    y = df["score_2000"].to_numpy(dtype=float)\n    e = df["english_learners"].to_numpy(dtype=float)\n'
            '    m = df["free_meals"].to_numpy(dtype=float)\n',
            ("survey::svyglm with the family of outcome= (gaussian; quasibinomial for yes or no; quasipoisson for "
             "counts) and its own t tests and intervals on the model's residual degrees of freedom.",),
            "simplydata also says the links describe the population, not cause and effect.", row="free_meals"),
    _survey("table.compare_averages_of", "after use_survey_design()",
            'table.compare_averages_of("score_2000", for_each_group_in="award")',
            f"""
                # compare_averages_of("score_2000", for_each_group_in="award") under use_survey_design(...)
                d <- survey::svydesign(ids = ~1, strata = ~s, weights = ~w, fpc = ~f,
                                       data = data.frame(s, w, f, y, a))
                r <- survey::svyttest(y ~ a, d)                                  # (1)
                list(diff = r$estimate, t = r$statistic, df = r$parameter, p = r$p.value)
            """,
            {"difference": "diff", "t": "t", "degrees of freedom": "df", "p-value": "p"},
            '    y = df["score_2000"].to_numpy(dtype=float)\n    a = df["award"].to_numpy(dtype=str)\n',
            ("the design-based t test of survey::svyttest() for two groups; more groups go to explain().",),
            "simplydata also writes the p-value sentence with its null (the same average in the population)."),
    _survey("table.compare_counts_of", "after use_survey_design()",
            'table.compare_counts_of("award", for_each_group_in="school_type")',
            f"""
                # compare_counts_of("award", for_each_group_in="school_type") under use_survey_design(...)
                d <- survey::svydesign(ids = ~1, strata = ~s, weights = ~w, fpc = ~f,
                                       data = data.frame(s, w, f, y, s2 = s))
                r <- survey::svychisq(~y + s2, d)                                # (1)
                list(F = r$statistic, ndf = r$parameter[1], ddf = r$parameter[2], p = r$p.value)
            """,
            {"F": "F", "degrees of freedom": "ndf", "design degrees of freedom": "ddf", "p-value": "p"},
            '    y = df["award"].to_numpy(dtype=str)\n',
            ("the Rao-Scott corrected chi-square as an F test (survey::svychisq()'s default statistic = \"F\").",),
            "As compare_averages_of."),
]
