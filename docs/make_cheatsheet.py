"""Write docs/cheatsheet.md from the same word list that sdata.show_all_words() prints.

Run it after adding or changing a word:

    python docs/make_cheatsheet.py

A test (tests/test_learn.py) fails if cheatsheet.md is out of date.
"""

from __future__ import annotations

from pathlib import Path

from simplydata import learn

HERE = Path(__file__).resolve().parent
OUT = HERE / "cheatsheet.md"


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def make() -> str:
    aliases = learn._aliases()
    lines = [
        "# simplydata cheat sheet",
        "",
        "Every word on one page. Table words are steps on a table, for looking at data, cleaning",
        "it and summing it up; chart words are steps on a chart:",
        "",
        "```python",
        "import simplydata as sdata",
        'table = sdata.table(sdata.get_example("marks"))   # or sdata.table("my_file.xlsx")',
        'table.keep_rows_where("marks", is_above=50)',
        'table.find_average_of("marks", for_each_group_in="class")   # says the answer in a sentence',
        'table.save("good_marks.xlsx")',
        "chart = table.start_chart()                   # or sdata.chart(table), sdata.chart(\"my_file.xlsx\")",
        'chart.draw_bars(x="class", y="marks", error="standard error")',
        'chart.write_title_on_top("Good marks")',
        'chart.save("marks.png")',
        "```",
        "",
        "Number words are steps on a list (or a grid) of numbers:",
        "",
        "```python",
        "nums = sdata.numbers([12, 15, 9, 20, 14])",
        "bigger = nums * 2                       # symbols make new numbers",
        "nums.keep_each_number_that(is_above=10)             # words change the numbers (undo() takes it back)",
        "nums.find_average()",
        "grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])",
        "```",
        "",
        'In Python, `sdata.help("draw_bars")` explains any word, `sdata.show_all_words()` prints this list and',
        "`sdata.show_lesson(1)` starts the one-day course (lessons 9 to 12 are about tables, lesson 13",
        "about numbers, lesson 14 about statistical tests, lesson 15 puts it all together, and lessons 16 to 25",
        "go further: models, patterns, survival, fitting curves, finding and solving, distributions, checking",
        "a model, time series, forecasts, cycles and systems). System words are steps on a system:",
        "`system = sdata.system(\"1 / (s**2 + 2*s + 5)\")`.",
        "",
        "Every example runs as written on the practice table in the *Table* column:",
        'for example `weather = sdata.get_example("weather")` then `chart = sdata.chart(weather)`,',
        'or `table = sdata.table(sdata.get_example("weather"))` for table words.',
        "Number words use `nums = sdata.numbers([12, 15, 9, 20, 14])` and grid words",
        "`grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])`; `sdata.help(\"word\")` shows each example ready to run.",
        "Steps such as `fit_line` or `write_title_on_top` go after a chart step such as `chart.draw_dots(...)`,",
        "and `a`, `b` in `sdata.put_side_by_side(a, b)` are charts you made first.",
        "",
        "*This file is made by `docs/make_cheatsheet.py`. Do not edit it by hand.*",
    ]
    for group, keys in learn.GROUPS:
        lines += ["", f"## {group}", "", "| Word | Example | Table | What it does |",
                  "|---|---|---|---|"]
        for key in keys:
            word = f"`{learn._display(key)}`"
            if key in aliases:
                word += " (also " + ", ".join(f"`{a}`" for a in aliases[key]) + ")"
            example = f"`{_cell(learn._short_example(key))}`"
            table = learn._example_table(key) or ""
            lines.append(f"| {word} | {example} | {table} | {_cell(learn._summary(key))} |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    OUT.write_text(make(), encoding="utf-8")
    print(f"Wrote {OUT}")
