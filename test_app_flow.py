"""
test_app_flow.py - drives the real Streamlit app headlessly (Streamlit AppTest).

Run from the project root:   py test_app_flow.py
Covers the whole student journey (assessment, confirmation, results, SHAP, K-Means insights,
the four activities, progress, PDF report), repeated attempts, every page, refresh behaviour and
model-loading failure. Results are written to test_results.json for the Testing page.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.disable(logging.CRITICAL)  # silence harmless Streamlit bare-mode warnings

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from streamlit.testing.v1 import AppTest

from backend import interventions as I
from backend import model_loader as ML
from backend.questionnaire import CONSTRUCT_ITEMS, LIKERT_ITEM_IDS, PROFILE_KEYS, PROFILE_QUESTIONS
from testlog import TestLog

LOG = TestLog("App flow", "A")
CATEGORY = "General"
ERROR_TEXTS = ("Something went wrong while displaying this page", "This section could not be displayed")


def ok(message: str) -> None:
    LOG.record(CATEGORY, message)
    print(f"  PASSED  {message}")


def new_app() -> AppTest:
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=180)
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
    parts += [str(c.value) for c in at.caption] + [str(s.value) for s in at.success] + [str(i.value) for i in at.info]
    parts += [str(p.text) for p in at.progress] + [str(c.label) for c in at.checkbox] + [str(e.label) for e in at.expander]
    return "\n".join(map(str, parts))


def charts_on_page(at) -> int:
    return len(at.get("plotly_chart"))


def answer_step(at, step_answers: dict):
    for qid, value in step_answers.items():
        at.radio(key=f"w_{qid}").set_value(value)
    run(at)


GOLDEN = {"age_group": "18\u201322", "study_year": "First year", "experience": "Beginner",
          "usage_frequency": "Daily", "usage_duration": "31\u201360 minutes"}
for _id in (CONSTRUCT_ITEMS["independent_learning_score"] + CONSTRUCT_ITEMS["verification_score"]
            + CONSTRUCT_ITEMS["learning_benefit_score"]):
    GOLDEN[_id] = "Agree"
for _id, _label in zip(CONSTRUCT_ITEMS["metacognition_score"], ["Agree", "Agree", "Agree", "Neutral", "Neutral"]):
    GOLDEN[_id] = _label

STEP_IDS = [PROFILE_KEYS] + [CONSTRUCT_ITEMS[k] for k in (
    "independent_learning_score", "verification_score", "metacognition_score", "learning_benefit_score")]

ALL_PAGES = ["Home", "Assess", "Results", "Why This Result?", "Intervention", "Behavioural Insights", "Progress",
             "Model Insights", "Research", "Testing", "About", "Feature"]


def fill_all(at, answers=None):
    answers = answers or GOLDEN
    for step_index, ids in enumerate(STEP_IDS):
        answer_step(at, {i: answers[i] for i in ids})
        click(at, "assess_next")


def submit_via_state(at, answers):
    """Place a complete set of answers in session state, open the review page, confirm and submit."""
    at.session_state["answers"] = dict(answers)
    at.session_state["step"] = 5
    at.session_state["nav"] = "Assess"
    at.session_state["assess_confirm"] = True
    run(at)
    click(at, "assess_go")


def uniform_answers(likert: str, index: int) -> dict:
    answers = {q["key"]: q["options"][index][0] for q in PROFILE_QUESTIONS}
    for item_id in LIKERT_ITEM_IDS:
        answers[item_id] = likert
    return answers


def visit(at, page: str):
    at.session_state["nav"] = page
    run(at)
    text = all_text(at)
    for bad in ERROR_TEXTS:
        assert bad not in text, (page, bad)
    return text


def main():
    global CATEGORY
    print("=" * 66 + "\nCOGNIVUE AI - APP FLOW TEST\n" + "=" * 66)

    # ------------------------------------------------------------------
    CATEGORY = "Assessment"
    at = new_app()
    assert at.session_state["nav"] == "Home"
    ok("Home page renders without errors")

    click(at, "home_start")
    assert at.session_state["nav"] == "Assess"
    text = all_text(at)
    assert "not an examination" in text and "no right or wrong answers" in text and "How is my data used?" in text
    ok("The assessment explains that it is not an examination and describes data use")
    radios = list(at.radio)
    assert len(radios) == 5 and all(r.value is None for r in radios)
    assert "0 of 24 questions answered" in text and "24 remaining" in text
    ok("Assessment opens with 5 profile questions, NO default answers and a progress indicator")

    click(at, "assess_next")
    assert at.session_state["step"] == 0 and len(at.error) == 1
    ok("Next is blocked while profile questions are unanswered (clear error shown)")

    answer_step(at, {k: GOLDEN[k] for k in PROFILE_KEYS})
    assert "5 of 24 questions answered" in all_text(at) and "this section: 5 of 5" in all_text(at)
    click(at, "assess_next")
    assert at.session_state["step"] == 1 and len(list(at.radio)) == 5
    ok("Profile completed -> Independent learning section; progress shows answered, remaining and section counts")

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

    assert at.button(key="assess_go").disabled
    ok("Submit is disabled until the confirmation box is ticked")
    at.checkbox(key="assess_confirm").check()
    run(at)
    assert not at.button(key="assess_go").disabled
    ok("Ticking the confirmation enables Submit")

    click(at, "review_edit_3")
    assert at.session_state["step"] == 3
    ok("Edit on the review page jumps to that section")
    click(at, "assess_next"); click(at, "assess_next")
    assert at.session_state["step"] == 5 and at.session_state["assess_confirm"] is False
    ok("Revisiting the review page requires confirming again")

    # ------------------------------------------------------------------
    CATEGORY = "Prediction"
    at.checkbox(key="assess_confirm").check()
    run(at)
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
    for needle in ("Predicted overreliance score", "Calculated directly from your answers", "Summary of your learning behaviour",
                   "Personalised recommendations", "not a diagnosis", "average output across its training data is 2.71"):
        assert needle in text, needle
    assert charts_on_page(at) == 2
    ok("Results separate the predicted score from the questionnaire scores, with summary, recommendations, baseline 2.71 and charts")
    assert result["cluster"]["cluster_id"] == 0 and result["cluster"]["profile_label"].startswith("Stronger")
    assert len(at.session_state["history"]) == 1
    ok("K-Means cluster 0 reproduced for respondent 118 and the attempt is recorded")

    # ------------------------------------------------------------------
    CATEGORY = "Explainability"
    text = visit(at, "Why This Result?")
    assert "Additivity check passed" in text and "Part 1" in text and "Part 2" in text and "not proof of causation" in text
    assert result["shap"] not in (None, False) and charts_on_page(at) == 3
    ok("SHAP page shows the verified individual explanation, a waterfall, and clearly separate global importance")

    # ------------------------------------------------------------------
    CATEGORY = "Interventions"
    text = visit(at, "Intervention")
    assert at.session_state["iv_open"] == "metacognition_score"
    assert "Suggested next" in text and "Not started" in text
    ok("The activity hub opens on the weakest construct (Metacognition) and shows status for all four activities")
    for step in I.ACTIVITIES["metacognition_score"]["steps"]:
        key = I.value_key("metacognition_score", step["id"])
        if step["kind"] == "text":
            at.text_area(key=key).input("my answer")
        elif step["kind"] == "rating":
            at.radio(key=key).set_value(3)
        run(at)
    assert "In progress" in all_text(at)
    for r in I.ACTIVITIES["metacognition_score"]["reflections"]:
        at.text_area(key=I.value_key("metacognition_score", r["id"])).input("my reflection")
        run(at)
    text = all_text(at)
    assert "Activity completed" in text and "1 of 4" in text and "Next recommended activity" in text
    ok("Completing steps and reflections marks the activity Completed and updates the summary and next recommendation")
    visit(at, "Behavioural Insights")
    visit(at, "Intervention")
    assert at.text_area(key=I.value_key("metacognition_score", "s1")).value == "my answer"
    ok("Activity progress is preserved when navigating away and back")

    # ------------------------------------------------------------------
    CATEGORY = "Behavioural insights"
    text = visit(at, "Behavioural Insights")
    for needle in ("Cluster 0", "Stronger learning-strategy profile", "Silhouette score", "not</b> a diagnosis", "Groups identified", "79.5%"):
        assert needle in text or needle in "".join(m.value for m in at.markdown), needle
    assert charts_on_page(at) == 4
    ok("Behavioural Insights shows group sizes, silhouette, averages, comparison charts and PCA with caveats")

    # ------------------------------------------------------------------
    CATEGORY = "Report and progress"
    text = visit(at, "Progress")
    assert "Privacy and data usage" in text
    click(at, "make_report")
    pdf = at.session_state["report_bytes"]
    assert pdf and pdf[:5] == b"%PDF-" and len(pdf) > 4000
    ok("The PDF report is generated from the Progress page")
    assert "Your attempts over time" in all_text(at)
    ok("The Progress page lists attempts and explains privacy and data usage")

    # ------------------------------------------------------------------
    CATEGORY = "Repeat assessment"
    changed = {**GOLDEN, "Q19": "Neutral", "Q20": "Neutral"}
    click(at, "prog_back") if False else None
    at.session_state["nav"] = "Results"
    run(at)
    click(at, "results_reset")
    assert at.session_state["answers"] == {} and len(at.session_state["history"]) == 1
    ok("Start Over clears answers but keeps earlier attempts for comparison")
    submit_via_state(at, changed)
    assert len(at.session_state["history"]) == 2 and at.session_state["nav"] == "Results"
    text = all_text(at)
    assert "Compared with your previous attempt" in text and "do not prove a change in actual ability" in text
    ok("A second attempt is compared with the first and the change is described as self-reported")
    text = visit(at, "Progress")
    assert "Change in the predicted score" in text and charts_on_page(at) == 1
    ok("The Progress page charts both attempts")

    # ------------------------------------------------------------------
    CATEGORY = "Pages"
    for page in ALL_PAGES:
        visit(at, page)
    ok("All 12 pages render without errors (with a result)")
    text = visit(at, "Research")
    for needle in ("Direct Indicators of AI Overreliance (Q12", "I depend on generative AI to begin academic tasks", "22 (14.6%)", "58 (38.4%)"):
        assert needle in text or needle in "".join(m.value for m in at.markdown), needle
    ok("Research page shows Q12-Q18 with their statements and response counts")
    text = visit(at, "Model Insights")
    assert "not available yet" in "".join(m.value for m in at.markdown) and charts_on_page(at) >= 15
    ok("Model Insights shows interactive charts and honestly reports that out-of-fold plots need a notebook export")

    # ------------------------------------------------------------------
    CATEGORY = "Start over and refresh"
    at.session_state["nav"] = "Results"
    run(at)
    click(at, "results_reset")
    for page in ("Results", "Why This Result?", "Intervention", "Behavioural Insights"):
        text = visit(at, page)
        assert "No assessment yet" in text, page
    ok("Result pages show a friendly guard when there is no submitted assessment")
    for page in ALL_PAGES:
        visit(at, page)
    ok("All 12 pages render without errors (without a result)")
    fresh = new_app()
    assert fresh.session_state["answers"] == {} and fresh.session_state["result"] is None and fresh.session_state["history"] == []
    ok("A page refresh (new session) starts clean: no answers, result or attempts are retained")

    # ------------------------------------------------------------------
    CATEGORY = "Validation"
    at = new_app()
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
    res = at.session_state["result"]
    assert at.session_state["nav"] == "Results" and res is not None
    assert all(r["Status"] == "Support recommended" for r in res["interventions"])
    text = visit(at, "Intervention")
    assert "4 of 4" in text and "Support recommended" in text
    ok("Low construct scores flag all four dimensions for targeted support")
    assert 1.0 <= res["prediction"]["score"] <= 5.0
    ok("A minimum-style questionnaire still yields a valid score in 1-5")

    at = new_app()
    submit_via_state(at, uniform_answers("Strongly Agree", -1))
    assert 1.0 <= at.session_state["result"]["prediction"]["score"] <= 5.0
    assert all(r["Status"] == "Maintain current practice" for r in at.session_state["result"]["interventions"])
    ok("High construct scores give maintenance suggestions and a valid score")

    # ------------------------------------------------------------------
    CATEGORY = "Model loading failure"
    original = ML.MODELS_DIR
    try:
        ML.MODELS_DIR = Path("/nonexistent/models")
        st.cache_resource.clear()
        at = new_app()
        assert "could not be loaded" in "".join(m.value for m in at.markdown)
        ok("If the models cannot be loaded the app shows a clear message instead of crashing")
        submit_via_state(at, GOLDEN)
        assert at.session_state["nav"] == "Assess" and at.session_state["result"] is None
        assert "could not be generated" in at.session_state["submit_error"]
        ok("Submitting without models shows a friendly error and no result")
        for page in ("Model Insights", "Behavioural Insights", "Home"):
            at.session_state["nav"] = page
            run(at)  # no exception; the sections that need models show a friendly notice
        assert "could not be" in all_text(at) or "could not be" in "".join(m.value for m in at.markdown)
        ok("Pages that need the models degrade gracefully (no crash, friendly notice)")
    finally:
        ML.MODELS_DIR = original
        st.cache_resource.clear()

    LOG.save()
    print("\n" + "=" * 66 + f"\nALL {len(LOG.rows)} CHECKS PASSED\n" + "=" * 66)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print("\nTEST FAILED")
        print(repr(error))
        raise SystemExit(1)
