"""
test_app_flow.py - drives the real Streamlit app headlessly (Streamlit AppTest).

Run from the project root:   py test_app_flow.py
Checks the assessment flow end to end: no default answers, validation,
navigation, preserved answers, submission, real prediction and Start Over.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.disable(logging.CRITICAL)  # silence harmless Streamlit bare-mode warnings

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit.testing.v1 import AppTest

from backend.questionnaire import CONSTRUCT_ITEMS, LIKERT_ITEM_IDS, PROFILE_KEYS

PASSED = []


def ok(message):
    PASSED.append(message)
    print(f"  PASSED  {message}")


def new_app() -> AppTest:
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=90)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def click(at, key):
    at.button(key=key).click().run()
    assert not at.exception, [e.value for e in at.exception]


def go_assessment(at):
    click(at, "home_start")
    assert at.session_state["_page"] == "Assessment"


def answer_step(at, step_answers: dict):
    for qid, value in step_answers.items():
        at.radio(key=f"w_{qid}").set_value(value)
    at.run()
    assert not at.exception, [e.value for e in at.exception]


GOLDEN = {
    "age_group": "18–22", "study_year": "First year", "experience": "Beginner",
    "usage_frequency": "Daily", "usage_duration": "31–60 minutes",
}
for _id in CONSTRUCT_ITEMS["independent_learning_score"] + CONSTRUCT_ITEMS["verification_score"] \
        + CONSTRUCT_ITEMS["learning_benefit_score"]:
    GOLDEN[_id] = "Agree"
for _id, _label in zip(CONSTRUCT_ITEMS["metacognition_score"],
                       ["Agree", "Agree", "Agree", "Neutral", "Neutral"]):
    GOLDEN[_id] = _label

STEP_IDS = [PROFILE_KEYS] + [CONSTRUCT_ITEMS[k] for k in (
    "independent_learning_score", "verification_score", "metacognition_score", "learning_benefit_score")]


def fill_all(at):
    for step_index, ids in enumerate(STEP_IDS):
        answer_step(at, {i: GOLDEN[i] for i in ids})
        click(at, f"next_{step_index}")


def main():
    print("=" * 66)
    print("COGNIVUE AI - ASSESSMENT FLOW TEST")
    print("=" * 66)

    at = new_app()
    assert at.session_state["_page"] == "Home"
    ok("Home page renders without errors")

    go_assessment(at)
    radios = list(at.radio)
    assert len(radios) == 5 and all(r.value is None for r in radios)
    ok("Assessment opens with 5 profile questions and NO default answers")

    click(at, "next_0")
    assert at.session_state["step"] == 0 and len(at.error) == 1
    ok("Next is blocked while profile questions are unanswered (clear error shown)")

    answer_step(at, {k: GOLDEN[k] for k in PROFILE_KEYS})
    click(at, "next_0")
    assert at.session_state["step"] == 1 and len(list(at.radio)) == 5
    ok("Profile completed -> Independent learning section (5 Likert questions)")

    answer_step(at, {i: GOLDEN[i] for i in STEP_IDS[1]})
    click(at, "back_1")
    assert at.session_state["step"] == 0
    assert [r.value for r in at.radio] == [GOLDEN[k] for k in PROFILE_KEYS]
    ok("Back keeps previously entered profile answers")
    click(at, "next_0")
    assert [r.value for r in at.radio] == [GOLDEN[i] for i in STEP_IDS[1]]
    assert len(at.warning) == 0
    ok("Returning to a section restores its answers (no Streamlit warnings)")

    for step_index in range(1, 5):
        if step_index > 1:
            answer_step(at, {i: GOLDEN[i] for i in STEP_IDS[step_index]})
        click(at, f"next_{step_index}")
    assert at.session_state["step"] == 5
    ok("All four Likert sections completed -> Review page")

    submit = at.button(key="submit")
    assert not submit.disabled
    ok("Submit enabled when all 24 answers are present")

    click(at, "edit_3")
    assert at.session_state["step"] == 3
    ok("Edit on the review page jumps to that section")
    click(at, "next_3"); click(at, "next_4")
    assert at.session_state["step"] == 5

    click(at, "submit")
    assert at.session_state["_page"] == "Results", at.session_state["submit_error"]
    result = at.session_state["result"]
    assert result is not None
    score = result["prediction"]["score"]
    assert abs(score - 2.8551) < 5e-5, score
    ok(f"Submission produces the real Random Forest score {score:.4f} (matches Colab respondent 118)")
    assert [round(v, 1) for v in result["construct_scores"].values()] == [4.0, 4.0, 3.6, 4.0]
    ok("Construct scores 4.0 / 4.0 / 3.6 / 4.0 calculated from the answers")
    assert any("2.86" in m.value for m in at.markdown)
    ok("Result page displays the score")

    click(at, "results_reset")
    assert at.session_state["answers"] == {} and at.session_state["result"] is None
    assert at.session_state["step"] == 0 and at.session_state["_page"] == "Assessment"
    assert all(r.value is None for r in at.radio)
    ok("Start Over clears answers, result and widget state")

    # One unanswered question -> review blocks submission
    fill_all(at)
    assert at.session_state["step"] == 5
    answers = dict(at.session_state["answers"])
    answers.pop("Q27")
    at.session_state["answers"] = answers
    at.run()
    assert at.button(key="submit").disabled
    assert any("unanswered" in e.value for e in at.error)
    ok("Submit is disabled and an error names the unanswered question")

    click(at, "goto_missing")
    assert at.session_state["step"] == 2
    ok("'Go to first unanswered question' jumps to the right section")

    print("\n" + "=" * 66)
    print(f"ALL {len(PASSED)} CHECKS PASSED")
    print("=" * 66)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print("\nTEST FAILED")
        print(repr(error))
        raise SystemExit(1)