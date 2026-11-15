"""30 days of simplydata: the days (learn_days.py), the words that show them and the printable guide."""

import datetime
import importlib.util
import json
import re
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pytest

import simplydata as sdata
from simplydata import learn, learn_days

ROOT = Path(__file__).resolve().parents[1]
TRACKS = learn_days.TRACK_NAMES
DAYS = range(1, learn_days.DAYS_IN_A_TRACK + 1)
ALL_DAYS = [(t, n) for t in TRACKS for n in DAYS]
START = datetime.date(2026, 11, 2)


def _run(code, folder, monkeypatch):
    monkeypatch.chdir(folder)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        exec(compile(code, "<day code>", "exec"), {"__name__": "__main__"})
    plt.close("all")


# ---------------------------------------------------------------- every piece of code runs
@pytest.mark.parametrize("where, code", learn_days.all_code(), ids=[w for w, _ in learn_days.all_code()])
def test_every_example_and_answer_runs(where, code, tmp_path, monkeypatch, capsys):
    _run(code, tmp_path, monkeypatch)
    for name in re.findall(r'\.save(?:fig)?\("([^"]+)"', code):
        assert (tmp_path / name).stat().st_size > 0, name


@pytest.mark.parametrize("unit, code, shows", [(name, c, s) for name, u in learn_days.UNITS.items()
                                               for c, s, _ in u.get("errors", [])])
def test_errors_made_on_purpose_say_what_the_day_says(unit, code, shows):
    with pytest.raises(BaseException) as found:
        exec(compile("import simplydata as sdata\n" + code, "<error>", "exec"), {})
    assert shows in str(found.value), unit


# ---------------------------------------------------------------- the shape of the 30 days
MANUAL_ONLY = {learn.lesson_number(title) for title in learn_days.MANUAL_ONLY_LESSONS}


@pytest.mark.parametrize("track", TRACKS)
def test_each_track_has_thirty_days_and_every_everyday_lesson(track):
    assert len(learn_days.DAYS[track]) == 30
    taught = {n for n in DAYS for n in learn_days.plan(track, n)["lessons"]}
    assert set(range(1, len(learn.LESSONS) + 1)) - MANUAL_ONLY <= taught, f"{track} misses lessons"
    assert not taught & MANUAL_ONLY, "the manual-only lessons are not days of their own"
    kinds = {n: learn_days.plan(track, n)["kind"] for n in DAYS}
    for review in (7, 14, 21):
        assert kinds[review] == "review", (track, review)
    assert kinds[29] == "final"
    assert sum(k == "project" for k in kinds.values()) >= 2


def test_the_python_track_follows_its_outline():
    lessons = {n: learn_days.plan("python", n)["lessons"] for n in DAYS}
    assert set(lessons[1] + lessons[2]) == {1, 2, 3}
    assert {k for n in (3, 4, 5) for k in lessons[n]} == {4, 5, 6, 7, 8}
    assert {k for n in (6, 8, 9) for k in lessons[n]} == {9, 10, 11, 12, 13}
    assert {k for n in (10, 11, 12, 13) for k in lessons[n]} == {14, 15}
    assert [lessons[n] for n in (15, 16, 17, 18, 19)] == [[16], [21], [17], [18], [19, 20]]
    time_series = {learn.lesson_number(t) for t in (learn.TIME_SERIES_LESSON, learn.CYCLES_LESSON)}
    assert set(lessons[20]) == time_series, "the time series lessons have a day of their own"
    assert [learn_days.plan("python", n)["kind"] for n in range(22, 28)] == ["project"] * 6
    assert learn_days.plan("python", 28)["kind"] == "review"


def test_the_beginner_track_starts_with_python():
    for n in (1, 2, 3):
        p = learn_days.plan("beginner", n)
        assert p["examples"] or p["errors"], n
    assert learn_days.plan("beginner", 1)["lessons"] == []
    assert 1 in learn_days.plan("beginner", 3)["lessons"]


@pytest.mark.parametrize("track, number", ALL_DAYS)
def test_every_day_is_complete(track, number):
    p = learn_days.plan(track, number)
    assert p["goal"].endswith(".") and p["goal"].count(". ") == 0, "the goal is one sentence"
    assert p["do"] and p["task"]
    assert len(p["solutions"]) == len(p["task"]), "one worked answer for each task"
    for code, explain in p["solutions"]:
        assert explain.strip() and "\n" not in explain
        assert "sdata." not in code or code.startswith("import simplydata as sdata\n") or \
            "\nimport simplydata as sdata\n" in code, "a worked answer runs on its own"
    for key in p["words"]:
        assert key in learn._all_keys(), key
        assert learn._lookup(learn_days.help_name(key)) == key, key
    for n in p["lessons"]:
        assert 1 <= n <= len(learn.LESSONS)


@pytest.mark.parametrize("track, number", ALL_DAYS)
def test_warm_ups_ask_about_earlier_days(track, number):
    warm = learn_days.warm_up(track, number)
    kind = learn_days.plan(track, number)["kind"]
    if number == 1:
        assert warm == []
        return
    assert len(warm) >= 3
    assert all(1 <= source < number for _, _, source in warm)
    assert len({q for q, _, _ in warm}) == len(warm), "no question twice on one day"
    if kind in ("review", "final"):
        assert len(warm) >= 6
        assert len({s for _, _, s in warm}) >= 6, "a review mixes many days"
    if kind == "learn" and number >= 9:
        sources = [s for _, _, s in warm]
        assert number - 1 in sources or not learn_days._has_recall(track, number - 1)
        assert min(sources) <= number - 7, "spaced: something from about a week ago"


@pytest.mark.parametrize("track", TRACKS)
def test_core_words_come_back_after_3_and_7_days_and_in_the_final_test(track):
    final = next(n for n in DAYS if learn_days.plan(track, n)["kind"] == "final")
    final_questions = {q for q, _, _ in learn_days.warm_up(track, final)}
    taught = 0
    for n in DAYS:
        for q, _ in learn_days._spaced_of(track, n):
            taught += 1
            for later in (n + 3, n + 7):
                if later <= len(DAYS):
                    assert q in {w for w, _, _ in learn_days.warm_up(track, later)}, (track, n, later, q)
            assert q in final_questions, (track, n, q)
    assert taught >= 6  # z-scores, interval=95, shuffling, compare_matched, time windows, trend


@pytest.mark.parametrize("track", TRACKS)
def test_every_question_comes_up(track):
    """Every recall question of every day is asked at least once later in the track: the final test asks
    the questions that have not come up yet."""
    asked = {q for n in DAYS for q, _, _ in learn_days.warm_up(track, n)}
    final = next(n for n in DAYS if learn_days.plan(track, n)["kind"] == "final")
    for n in range(1, final):
        for q, _ in learn_days._recall_of(track, n):
            assert q in asked, (track, n, q)


@pytest.mark.parametrize("track, number", ALL_DAYS)
def test_no_day_holds_more_than_about_two_lessons(track, number):
    p = learn_days.plan(track, number)
    if p["kind"] == "learn":
        assert len(p["lessons"]) <= 2, (track, number, p["lessons"])
        assert len(p["units"]) <= 3, (track, number, p["units"])


# Words of the parts left to the manual: the 30 days neither teach them nor ask about them.
MANUAL_ONLY_WORDS = ("find_smallest", "find_biggest", "sdata.solve", "values_at", "map_of", "compare_risks",
                     "compare_to_truth", "agreement_between", "forecast", "spectrum", "add_filtered_column",
                     "check_steady", "sdata.system", "step_response", "with_feedback")


def test_recall_and_tasks_leave_out_the_manual_only_parts():
    for name, unit in learn_days.UNITS.items():
        texts = [q + a for q, a in unit.get("recall", []) + unit.get("spaced", [])]
        texts += unit.get("task", []) + [code for code, _ in unit.get("solutions", [])] + unit.get("words", [])
        for text in texts:
            for word in MANUAL_ONLY_WORDS:
                assert word not in text, (name, word)


def test_days_point_to_the_rest_in_the_manual():
    """Each manual-only lesson (and the parts of lessons 19, 20 and 25 left out) is named on a day, in one
    "More in the manual" line."""
    for track in TRACKS:
        more = [line for n in DAYS for line in learn_days.plan(track, n)["do"] if line.startswith("More in the manual")]
        text = " ".join(more)
        for n in sorted(MANUAL_ONLY) + [19, 20, learn.lesson_number(learn.CYCLES_LESSON)]:
            assert f"sdata.lesson({n})" in text, (track, n)
        assert len(more) == 3, track


def test_manual_sections_named_by_the_days_exist():
    tex = (ROOT / "docs" / "manual" / "simplydata_manual.tex").read_text(encoding="utf-8")
    manual = (ROOT / "docs" / "manual" / "ideas.tex").read_text(encoding="utf-8") + tex
    for name, unit in learn_days.UNITS.items():
        for label, title in unit.get("manual", []):
            assert re.search(r"\{" + re.escape(title) + r"\}\{" + re.escape(label) + r"\}", manual), (name, label)


# ---------------------------------------------------------------- the words
@pytest.fixture
def on(monkeypatch):
    """Set the date sdata.today() sees: on(5) is the 5th day after START (day 1 = START)."""
    def set_day(n):
        monkeypatch.setattr(learn_days, "_date_today", lambda: START + datetime.timedelta(days=n - 1))
    set_day(1)
    return set_day


def _saved():
    return json.loads(learn_days.progress_file().read_text(encoding="utf-8"))


def test_progress_file_follows_the_environment_variable(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMPLYDATA_PROGRESS_FILE", str(tmp_path / "x" / "p.json"))
    assert learn_days.progress_file() == tmp_path / "x" / "p.json"
    monkeypatch.delenv("SIMPLYDATA_PROGRESS_FILE")
    assert learn_days.progress_file() == Path.home() / ".simplydata" / "progress.json"


def test_today_before_starting_explains_and_shows_day_1(on, capsys):
    sdata.today()
    out = capsys.readouterr().out
    assert "not started" in out and "sdata.start_30_days()" in out and 'track="beginner"' in out
    assert "Day 1 of 30 (Python track)" in out
    assert not learn_days.progress_file().exists(), "looking is not starting"


def test_start_remembers_the_day_and_shows_day_1(on, capsys):
    sdata.start_30_days(track="beginner")
    out = capsys.readouterr().out
    assert "Beginner track" in out and "Day 1 of 30 (Beginner track)" in out
    assert " ".join(str(learn_days.progress_file()).split()) in " ".join(out.split())
    saved = _saved()
    assert saved["track"] == "beginner" and saved["started"] == START.isoformat()
    assert saved["opened"] == {"1": START.isoformat()}


def test_starting_twice_changes_nothing_and_says_how_to_start_again(on, capsys):
    sdata.start_30_days(track="beginner")
    on(3)
    sdata.today()
    capsys.readouterr()
    sdata.start_30_days()
    out = capsys.readouterr().out
    assert "You started" in out and 'start_30_days(track="beginner", start_again=True)' in out
    assert _saved()["track"] == "beginner" and len(_saved()["opened"]) == 2
    sdata.start_30_days(track="python", start_again=True)
    assert _saved()["track"] == "python" and _saved()["opened"] == {"1": (START + datetime.timedelta(days=2)).isoformat()}


def test_today_goes_on_one_day_at_a_time(on, capsys):
    sdata.start_30_days()
    on(2)
    sdata.today()
    out = capsys.readouterr().out
    assert "Day 2 of 30" in out and "(day 1)" in out and "sdata.answers(2)" in out
    sdata.today()  # the same date again: the same day
    assert "Day 2 of 30" in capsys.readouterr().out
    on(3)
    sdata.today()
    out = capsys.readouterr().out
    assert "Day 3 of 30" in out and "By the calendar" not in out


def test_after_a_break_today_carries_on_and_says_so_kindly(on, capsys):
    sdata.start_30_days()
    on(2)
    sdata.today()
    on(9)
    capsys.readouterr()
    sdata.today()
    out = capsys.readouterr().out
    assert "Day 3 of 30" in out
    assert "By the calendar it is day 9" in out and "nothing is lost" in out
    assert "sdata.today(follow_calendar=True)" in out
    for scolding in ("missed", "late", "behind", "should have"):
        assert scolding not in out.split("Day 3 of 30")[0]


def test_one_day_off_is_not_mentioned(on, capsys):
    sdata.start_30_days()
    on(3)
    capsys.readouterr()
    sdata.today()
    out = capsys.readouterr().out
    assert "Day 2 of 30" in out and "By the calendar" not in out


def test_today_can_follow_the_calendar(on, capsys):
    sdata.start_30_days()
    on(9)
    capsys.readouterr()
    sdata.today(follow_calendar=True)
    out = capsys.readouterr().out
    assert "Day 9 of 30" in out and "Days 2 to 8 were not opened" in out
    on(10)
    sdata.today()
    assert "Day 10 of 30" in capsys.readouterr().out


def test_next_day_goes_on_now(on, capsys):
    sdata.start_30_days()
    sdata.next_day()
    sdata.next_day()
    assert "Day 3 of 30" in capsys.readouterr().out
    assert set(_saved()["opened"]) == {"1", "2", "3"}
    on(2)
    sdata.today()
    assert "Day 4 of 30" in capsys.readouterr().out


def test_after_day_30_well_done(on, capsys):
    sdata.start_30_days()
    for _ in range(29):
        sdata.next_day()
    assert "This is the last day" in capsys.readouterr().out
    sdata.next_day()
    assert "Well done" in capsys.readouterr().out
    on(40)
    sdata.today()
    assert "Well done" in capsys.readouterr().out


def test_day_shows_any_day_without_moving(on, capsys):
    sdata.start_30_days()
    capsys.readouterr()
    sdata.day(12)
    out = capsys.readouterr().out
    assert "Day 12 of 30 (Python track)" in out and "Next: sdata.day(13)" in out
    assert set(_saved()["opened"]) == {"1"}
    sdata.day(5, track="beginner")
    assert "Day 5 of 30 (Beginner track)" in capsys.readouterr().out


def test_day_without_a_number_lists_the_calendar_with_ticks(on, capsys):
    sdata.start_30_days()
    sdata.next_day()
    capsys.readouterr()
    sdata.day()
    out = capsys.readouterr().out
    assert "[x]  1." in out and "[x]  2." in out and "[ ]  3." in out and "[ ] 30." in out
    assert "review" in out and "project" in out


def test_answers_are_not_shown_with_the_questions(on, capsys):
    sdata.day(4)
    out = capsys.readouterr().out
    p = learn_days.plan("python", 4)
    for question, answer, _ in p["warm_up"]:
        assert question in out.replace("\n       ", " ")
    assert p["solutions"][0][0].splitlines()[-1] not in out
    sdata.answers(4)
    out = capsys.readouterr().out
    assert "Answers to day 4" in out
    for line in p["solutions"][0][0].splitlines():
        assert line in out


def test_answers_without_a_number_is_the_last_day_opened(on, capsys):
    sdata.start_30_days()
    sdata.next_day()
    capsys.readouterr()
    sdata.answers()
    assert "Answers to day 2 (Python track)" in capsys.readouterr().out


@pytest.mark.parametrize("bad", [0, 31, "5", 2.0, True])
def test_wrong_day_number_is_explained(bad):
    with pytest.raises(sdata.SimplydataError, match="days 1 to 30"):
        sdata.day(bad)
    with pytest.raises(sdata.SimplydataError, match="days 1 to 30"):
        sdata.answers(bad)


@pytest.mark.parametrize("typed, expected", [("Python", "python"), ("beginners", "beginner"), (" BEGINNER ", "beginner")])
def test_tracks_are_understood(typed, expected):
    assert learn_days._track(typed) == expected


def test_wrong_track_says_did_you_mean():
    with pytest.raises(sdata.SimplydataError, match='Did you mean track="beginner"'):
        sdata.start_30_days(track="begginer")
    with pytest.raises(sdata.SimplydataError, match="There are two"):
        sdata.start_30_days(track=3)


def test_a_broken_progress_file_is_not_an_error(on, capsys):
    learn_days.progress_file().parent.mkdir(parents=True, exist_ok=True)
    learn_days.progress_file().write_text("{not json", encoding="utf-8")
    sdata.today()
    out = capsys.readouterr().out
    assert "could not be read" in out and "Day 1 of 30" in out
    sdata.start_30_days(start_again=True)
    assert _saved()["track"] == "python"


def test_other_names_point_to_the_30_days(capsys):
    with pytest.raises(sdata.SimplydataError, match="start_30_days"):
        sdata.tutorial()
    sdata.help("course")
    assert "start_30_days" in capsys.readouterr().out


def test_lesson_1_and_help_tell_learners_about_the_30_days(capsys):
    sdata.lesson(1)
    assert "sdata.start_30_days()" in capsys.readouterr().out
    sdata.help()
    assert "sdata.start_30_days()" in capsys.readouterr().out


# ---------------------------------------------------------------- the printable guide
GUIDE = ROOT / "docs" / "manual" / "simplydata_30_days.tex"


def _make_guide():
    spec = importlib.util.spec_from_file_location("make_30_days", ROOT / "docs" / "make_30_days.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_guide_is_up_to_date():
    """The guide's LaTeX is made from learn_days.py (with the manual's page numbers written in it)."""
    guide = _make_guide()
    written = GUIDE.read_text(encoding="utf-8")
    from make_dictionary import fingerprint_in, pages_in

    assert written == guide.make(pages_in(written), fingerprint_in(written)), "Run: python docs/make_manual.py --no-run"
    assert (ROOT / "docs" / "manual" / "simplydata_30_days.pdf").is_file()


def test_guide_pages_come_from_this_manual():
    _make_guide()
    from make_dictionary import fingerprint_in, manual_fingerprint

    assert fingerprint_in(GUIDE.read_text(encoding="utf-8")) == manual_fingerprint(), \
        "The manual changed: run python docs/make_manual.py --no-run to rebuild all three"


def test_guide_has_every_day_with_its_answers_and_manual_pages():
    guide = _make_guide()
    from make_dictionary import pages_in

    written = GUIDE.read_text(encoding="utf-8")
    for track, number in ALL_DAYS:
        assert f"{{{guide.day_label(track, number)}}}" in written
        assert re.search(r"\\answerday\{" + str(number) + r"\}\{[^}]*\}\{" + re.escape(guide.answers_label(track, number)), written)
        for n in learn_days.plan(track, number)["lessons"]:
            assert f"\\manualpage{{lesson:{n}}}" in written
    pages = pages_in(written)
    assert pages and all(page.isdigit() and anchor for page, anchor in pages.values())
    assert written.count(r"\daystart{") == 60


@pytest.mark.parametrize("track", TRACKS)
def test_the_model_words_of_lesson_21_come_back_spaced_and_in_the_final_test(track):
    """Each core word of a release gets recall questions about 3 and 7 days after it is taught, and the
    final test asks for it from memory (retrieval practice and spacing)."""
    taught = next(n for n in DAYS if 21 in learn_days.plan(track, n)["lessons"])
    questions = {q for q, _ in learn_days.UNITS["lesson21"]["recall"]}
    asked = sorted(n for n in DAYS for q, _, _ in learn_days.warm_up(track, n) if q in questions)
    assert any(2 <= n - taught <= 4 for n in asked), asked
    assert any(6 <= n - taught <= 8 for n in asked), asked
    final = learn_days.plan(track, 29)
    assert final["kind"] == "final" and any("compare_models" in code for code, _ in final["solutions"])


def test_lesson_tasks_are_asked_on_the_day_they_are_taught():
    # Lessons 19 and 20 are taught in part (examples 1 and 2): only their tasks 1 and 2 are set, as task 3 is
    # about example 3 (manual only). Of lesson 25 only example 3 (peaks and dips) is taught, with its task 3.
    from simplydata import learn_days

    for unit, n in (("fitting", 19), ("distributions", 20)):
        do = learn_days.UNITS[unit]["do"][0]
        assert "examples 1 and 2" in do and "tasks 1 and 2" in do and f"sdata.lesson({n}, solutions=True)" in do
        assert "lesson's tasks" not in do
        assert len(learn.LESSONS[n - 1]["task"]) == 3
    cycles = learn.lesson_number(learn.CYCLES_LESSON)
    do = " ".join(learn_days.UNITS["time_series"]["do"])
    assert f"sdata.lesson({cycles}), example 3 only" in do and "task 3" in do
    assert "find_dips" in learn.LESSONS[cycles - 1]["task"][2] or "dips" in learn.LESSONS[cycles - 1]["task"][2]
