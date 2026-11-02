"""
test_app_flow.py - drives the real Streamlit app headlessly (Streamlit AppTest).

Run from the project root:   py test_app_flow.py
Checks the full student journey: no default answers, validation, navigation,
preserved answers, submission, the real prediction, SHAP, interventions,
behavioural insights, every page rendering, and Start Over.
Results are written to test_results.json for the Testing page.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.disable(logging.CRITICAL)  # silence harmless Streamlit bare-mode warnings

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit.testing.v1 import AppTest

from backend.questionnaire import CONSTRUCT_ITEMS, LIKERT_ITEM_IDS, PROFILE_KEYS, PROFILE_QUESTIONS
from testlog import TestLog

LOG = TestLog("App flow", "A")
CATEGORY = "General"


def ok(message: str) -> None:
    LOG.record(CATEGORY, message)
    print(f"  PASSED  {message}")


def new_app() -> AppTest:
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=120)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def run(at):
    at.run()
    assert not at.exception, [e.value for e in at.exception]


def click(at, key):
    at.button(key=key).click()
    run(at)


def all_text(at) -> str:
    parts = [m.value for m in at.markdown] + [e.value for e in at.error] + [w.value for w in at.warning]
    parts += [str(c.value) for c in at.caption] + [str(s.value) for s in at.success]
    return "\n".join(map(str, parts))


def answer_step(at, step_answers: dict):
    for qid, value in step_answers.items():
        at.radio(key=f"w_{qid}").set_value(value)
    run(at)


GOLDEN = {"age_group": "18–22", "study_year": "First year", "experience": "Beginner",
          "usage_frequency": "Daily", "usage_duration": "31–60 minutes"}
for _id in (CONSTRUCT_ITEMS["independent_learning_score"] + CONSTRUCT_ITEMS["verification_score"]
            + CONSTRUCT_ITEMS["learning_benefit_score"]):
    GOLDEN[_id] = "Agree"
for _id, _label in zip(CONSTRUCT_ITEMS["metacognition_score"], ["Agree", "Agree", "Agree", "Neutral", "Neutral"]):
    GOLDEN[_id] = _label

STEP_IDS = [PROFILE_KEYS] + [CONSTRUCT_ITEMS[k] for k in (
    "independent_learning_score", "verification_score", "metacognition_score", "learning_benefit_score")]

ALL_PAGES = ["Home", "Assess", "Results", "Why This Result?", "Intervention", "Behavioural Insights",
             "Model Insights", "Research", "Testing", "About", "Feature"]


def fill_all(at, answers=None):
    answers = answers or GOLDEN
    for step_index, ids in enumerate(STEP_IDS):
        answer_step(at, {i: answers[i] for i in ids})
        click(at, "assess_next")


def submit_via_state(at, answers):
    """Place a complete set of answers in session state, open the review page and submit."""
    at.session_state["answers"] = dict(answers)
    at.session_state["step"] = 5
    at.session_state["nav"] = "Assess"
    run(at)
    click(at, "assess_go")


def uniform_answers(likert: str, index: int) -> dict:
    answers = {q["key"]: q["options"][index][0] for q in PROFILE_QUESTIONS}
    for item_id in LIKERT_ITEM_IDS:
        answers[item_id] = likert
    return answers


def main():
    global CATEGORY
    print("=" * 66)
    print("COGNIVUE AI - APP FLOW TEST")
    print("=" * 66)

    # ------------------------------------------------------------------
    CATEGORY = "Assessment"
    at = new_app()
    assert at.session_state["nav"] == "Home"
    ok("Home page renders without errors")

    click(at, "home_start")
    assert at.session_state["nav"] == "Assess"
    radios = list(at.radio)
    assert len(radios) == 5 and all(r.value is None for r in radios)
    ok("Assessment opens with 5 profile questions and NO default answers")

    click(at, "assess_next")
    assert at.session_state["step"] == 0 and len(at.error) == 1
    ok("Next is blocked while profile questions are unanswered (clear error shown)")

    answer_step(at, {k: GOLDEN[k] for k in PROFILE_KEYS})
    click(at, "assess_next")
    assert at.session_state["step"] == 1 and len(list(at.radio)) == 5
    ok("Profile completed -> Independent learning section (5 Likert questions)")

    answer_step(at, {i: GOLDEN[i] for i in STEP_IDS[1]})
    click(at, "assess_back")
    assert at.session_state["step"] == 0
    assert [r.value for r in at.radio] == [GOLDEN[k] for k in PROFILE_KEYS]
    ok("Back keeps previously entered profile answers")
    click(at, "assess_next")
    assert [r.value for r in at.radio] == [GOLDEN[i] for i in STEP_IDS[1]]
    assert len(at.warning) == 0
    ok("Returning to a section restores its answers (no Streamlit warnings)")

    for step_index in range(1, 5):
        if step_index > 1:
            answer_step(at, {i: GOLDEN[i] for i in STEP_IDS[step_index]})
        click(at, "assess_next")
    assert at.session_state["step"] == 5
    ok("All four Likert sections completed -> Review page")

    assert not at.button(key="assess_go").disabled
    ok("Submit enabled when all 24 answers are present")

    click(at, "review_edit_3")
    assert at.session_state["step"] == 3
    ok("Edit on the review page jumps to that section")
    click(at, "assess_next"); click(at, "assess_next")
    assert at.session_state["step"] == 5

    # ------------------------------------------------------------------
    CATEGORY = "Prediction"
    click(at, "assess_go")
    assert at.session_state["nav"] == "Results", at.session_state["submit_error"]
    result = at.session_state["result"]
    score = result["prediction"]["score"]
    assert abs(score - 2.8551) < 5e-5, score
    ok(f"Submission produces the real Random Forest score {score:.4f} (matches Colab respondent 118)")
    assert [round(v, 1) for v in result["construct_scores"].values()] == [4.0, 4.0, 3.6, 4.0]
    ok("Construct scores 4.0 / 4.0 / 3.6 / 4.0 calculated from the answers")
    text = all_text(at)
    assert "2.86" in text and "out of 5" in text and "Low Reliance" not in text and "High Reliance" not in text
    ok("Results page shows the continuous score out of 5 with no invented risk labels")
    assert result["cluster"]["cluster_id"] == 0 and result["cluster"]["profile_label"].startswith("Stronger")
    ok("K-Means cluster 0 / Stronger profile reproduced for respondent 118")

    # ------------------------------------------------------------------
    CATEGORY = "Explainability"
    at.session_state["nav"] = "Why This Result?"
    run(at)
    text = all_text(at)
    assert "Additivity check passed" in text
    assert result["shap"] is not False and result["shap"] is not None
    ok("SHAP page renders and the additivity check passes")

    # ------------------------------------------------------------------
    CATEGORY = "Interventions"
    at.session_state["nav"] = "Intervention"
    run(at)
    text = all_text(at)
    assert "Maintain current practice" in text
    feature = at.session_state["iv_dimension"]
    assert feature == "metacognition_score"
    ok("Interventions page opens on the suggested dimension (lowest construct score)")
    assert "0 of 5" in at.progress[-1].text
    at.checkbox(key=f"iv_{feature}_honest").check()
    for name in ("attempt", "compare", "errors", "reflect"):
        at.text_area(key=f"iv_{feature}_{name}").input("my text")
    run(at)
    assert "Activity completed" in all_text(at) and "5 of 5" in at.progress[-1].text
    ok("Interactive activity tracks progress and shows completion (no effectiveness claims)")
    at.session_state["nav"] = "Behavioural Insights"
    run(at)
    at.session_state["nav"] = "Intervention"
    run(at)
    assert at.text_area(key=f"iv_{feature}_attempt").value == "my text"
    ok("Activity text is preserved when navigating away and back")

    # ------------------------------------------------------------------
    CATEGORY = "Behavioural insights"
    at.session_state["nav"] = "Behavioural Insights"
    run(at)
    text = all_text(at)
    assert "Cluster 0" in text and "Stronger learning-strategy profile" in text and "not a diagnosis" in text
    ok("Behavioural Insights shows the exploratory K-Means group with its caveats")

    # ------------------------------------------------------------------
    CATEGORY = "Pages"
    for page in ALL_PAGES:
        at.session_state["nav"] = page
        run(at)
        assert "Something went wrong while displaying this page" not in all_text(at), page
    ok("All 11 pages render without errors (with a result)")

    # ------------------------------------------------------------------
    CATEGORY = "Start over"
    at.session_state["nav"] = "Results"
    run(at)
    click(at, "results_reset")
    assert at.session_state["answers"] == {} and at.session_state["result"] is None
    assert at.session_state["step"] == 0 and at.session_state["nav"] == "Assess"
    assert all(r.value is None for r in at.radio)
    ok("Start Over clears answers, result and widget state")

    for page in ("Results", "Why This Result?", "Intervention", "Behavioural Insights"):
        at.session_state["nav"] = page
        run(at)
        assert "No assessment yet" in all_text(at), page
    ok("Result pages show a friendly guard when no assessment has been submitted")
    for page in ALL_PAGES:
        at.session_state["nav"] = page
        run(at)
        assert "Something went wrong while displaying this page" not in all_text(at), page
    ok("All 11 pages render without errors (without a result)")

    # ------------------------------------------------------------------
    CATEGORY = "Validation"
    at.session_state["nav"] = "Assess"
    run(at)
    fill_all(at)
    assert at.session_state["step"] == 5
    answers = dict(at.session_state["answers"])
    answers.pop("Q27")
    at.session_state["answers"] = answers
    run(at)
    assert at.button(key="assess_go").disabled
    assert any("unanswered" in e.value for e in at.error)
    ok("Submit is disabled and an error names the unanswered question")
    click(at, "goto_missing")
    assert at.session_state["step"] == 2
    ok("'Go to first unanswered question' jumps to the right section")

    # ------------------------------------------------------------------
    CATEGORY = "Interventions"
    at = new_app()
    submit_via_state(at, uniform_answers("Disagree", 0))
    result = at.session_state["result"]
    assert at.session_state["nav"] == "Results" and result is not None
    assert all(r["Status"] == "Support recommended" for r in result["interventions"])
    at.session_state["nav"] = "Intervention"
    run(at)
    assert "4 of 4" in all_text(at) and "Support recommended" in all_text(at)
    ok("Low construct scores flag all four dimensions for targeted support")
    assert 1.0 <= result["prediction"]["score"] <= 5.0
    ok("A minimum-style questionnaire still yields a valid score in 1-5")

    at = new_app()
    submit_via_state(at, uniform_answers("Strongly Agree", -1))
    assert 1.0 <= at.session_state["result"]["prediction"]["score"] <= 5.0
    assert all(r["Status"] == "Maintain current practice" for r in at.session_state["result"]["interventions"])
    ok("High construct scores give maintenance suggestions and a valid score")

    LOG.save()
    print("\n" + "=" * 66)
    print(f"ALL {len(LOG.rows)} CHECKS PASSED")
    print("=" * 66)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print("\nTEST FAILED")
        print(repr(error))
        raise SystemExit(1)