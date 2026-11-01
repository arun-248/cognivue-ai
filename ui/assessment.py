"""
ui/assessment.py
----------------
Five-section questionnaire (24 questions), review page and submission.

* No default answers: every radio starts unselected.
* Answers persist in st.session_state["answers"] while navigating sections.
* Answers live in the session only; nothing is written to disk.
"""

from __future__ import annotations

import streamlit as st

from backend.model_loader import get_model_information
from backend.prediction import predict_overreliance
from backend.preprocessing import preprocess_responses
from backend.questionnaire import (
    LIKERT_LABELS,
    LIKERT_SECTIONS,
    PROFILE_QUESTIONS,
    REQUIRED_KEYS,
)
from backend.validation import ValidationError, validate_responses
from ui.resources import get_models
from ui.state import go
from ui.theme import html

TOTAL = len(REQUIRED_KEYS)  # 24
REVIEW_STEP = 5


# ----------------------------------------------------------------------
# Step definitions: step 0 = profile, 1-4 = Likert sections, 5 = review
# ----------------------------------------------------------------------
def _build_steps() -> list:
    steps = [{
        "name": "A · Profile",
        "title": "Section A · Student profile",
        "intro": "Tell us a little about your background and typical AI use.",
        "kind": "profile",
        "questions": [
            {"id": q["key"], "text": q["text"], "options": [label for label, _ in q["options"]]}
            for q in PROFILE_QUESTIONS
        ],
    }]
    short = {"B": "B · Independent", "C": "C · Verification", "D": "D · Metacognition", "E": "E · Benefits"}
    for sec in LIKERT_SECTIONS:
        steps.append({
            "name": short[sec["section"]],
            "title": f"Section {sec['section']} · {sec['title']}",
            "intro": sec.get("intro", "Choose how much you agree with each statement."),
            "kind": "likert",
            "questions": [
                {"id": item["id"], "text": item["text"], "options": LIKERT_LABELS}
                for item in sec["items"]
            ],
        })
    return steps


STEPS = _build_steps()

_number = 0
for _step in STEPS:
    for _q in _step["questions"]:
        _number += 1
        _q["number"] = _number
assert _number == TOTAL


def _answers() -> dict:
    return st.session_state["answers"]


def _is_answered(qid: str) -> bool:
    return _answers().get(qid) is not None


def _missing_in(step_index: int) -> list:
    return [q for q in STEPS[step_index]["questions"] if not _is_answered(q["id"])]


def _missing_all() -> list:
    return [q for step in STEPS for q in step["questions"] if not _is_answered(q["id"])]


# ----------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------
def _save_answer(qid: str) -> None:
    new_value = st.session_state.get(f"w_{qid}")
    if new_value is not None and _answers().get(qid) != new_value:
        _answers()[qid] = new_value
        st.session_state["result"] = None  # any change makes an old result stale
        st.session_state["submit_error"] = None


def _next_step() -> None:
    step = st.session_state["step"]
    if _missing_in(step):
        st.session_state["flag_missing_step"] = step
        return
    st.session_state["flag_missing_step"] = None
    st.session_state["step"] = min(step + 1, REVIEW_STEP)


def _prev_step() -> None:
    st.session_state["flag_missing_step"] = None
    st.session_state["step"] = max(st.session_state["step"] - 1, 0)


def _jump_to(step: int) -> None:
    st.session_state["flag_missing_step"] = None
    st.session_state["step"] = step


def _jump_to_first_missing() -> None:
    for index, step in enumerate(STEPS):
        if _missing_in(index):
            st.session_state["step"] = index
            st.session_state["flag_missing_step"] = index
            return


def reset_assessment() -> None:
    """Start Over: clear every answer, widget state and result."""
    for key in [k for k in st.session_state.keys() if k.startswith("w_")]:
        del st.session_state[key]
    st.session_state["answers"] = {}
    st.session_state["step"] = 0
    st.session_state["result"] = None
    st.session_state["submit_error"] = None
    st.session_state["flag_missing_step"] = None


def _submit() -> None:
    """Validate, preprocess, predict. Runs as a callback so it can change page."""
    st.session_state["submit_error"] = None
    answers = {k: v for k, v in _answers().items() if v is not None}
    check = validate_responses(answers)
    if not check.is_valid:
        st.session_state["submit_error"] = (
            "Some answers are missing or invalid. Please complete every question before submitting."
        )
        return
    try:
        student = preprocess_responses(answers)
        models = get_models()
        prediction = predict_overreliance(models["random_forest"], student.frame, models["feature_order"])
        info = get_model_information(models)
    except ValidationError as exc:
        st.session_state["submit_error"] = f"Your answers could not be validated: {exc}"
        return
    except Exception as exc:  # model files missing, version problems, etc.
        st.session_state["submit_error"] = (
            f"The prediction could not be generated ({type(exc).__name__}: {exc}). "
            "Check that the models folder is present and that py test_pipeline.py passes."
        )
        return

    st.session_state["result"] = {
        "features": student.features,
        "construct_scores": student.construct_scores,
        "prediction": prediction,
        "labels": {q["key"]: answers[q["key"]] for q in PROFILE_QUESTIONS},
        "model_warning": None if info["sklearn_versions_match"] else (
            f"Saved model was trained with scikit-learn {info['sklearn_trained_with']} but "
            f"{info['sklearn_installed']} is installed. Install scikit-learn==1.6.1."
        ),
    }
    go("Results")


# ----------------------------------------------------------------------
# Rendering helpers
# ----------------------------------------------------------------------
def _intro() -> None:
    html(
        f"""
        <div class="card">
          <div class="section-title">Understand Your Learning Habits</div>
          <div class="section-sub">Answer honestly based on your typical academic use of Generative AI.
          There are no right or wrong answers. This assessment uses self-reported responses only.</div>
          <div class="stats">
            <div class="stat"><b>{TOTAL}</b><span>questions in total</span></div>
            <div class="stat"><b>{len(PROFILE_QUESTIONS)}</b><span>profile questions</span></div>
            <div class="stat"><b>{TOTAL - len(PROFILE_QUESTIONS)}</b><span>Likert statements</span></div>
            <div class="stat"><b>5–8</b><span>minutes</span></div>
          </div>
          <div class="note" style="margin-top:16px"><b>Privacy:</b> your answers are processed in memory
          for this browser session only. Cognivue AI does not ask for your name, email or student ID and
          does not save your answers to a file or database. Choosing Start Over clears them.</div>
        </div>
        """
    )


def _stepper(current: int) -> None:
    pills = []
    names = [s["name"] for s in STEPS] + ["Review"]
    for index, name in enumerate(names):
        if index == current:
            css = "active"
        elif index < REVIEW_STEP and not _missing_in(index):
            css = "done"
        else:
            css = ""
        pills.append(f'<span class="step-pill {css}">{name}</span>')
    html(f'<div class="stepper">{"".join(pills)}</div>')


def _progress() -> None:
    answered = TOTAL - len(_missing_all())
    st.progress(answered / TOTAL, text=f"{answered} of {TOTAL} questions answered")


def _render_question(q: dict, kind: str, flagged: bool) -> None:
    qid, key = q["id"], f"w_{q['id']}"
    # Streamlit drops widget state for widgets that are not on screen, so restore it.
    if key not in st.session_state and _is_answered(qid):
        st.session_state[key] = _answers()[qid]

    with st.container(border=True, key=f"qcard_{qid}"):
        html(f'<div class="q-num">Question {q["number"]} of {TOTAL}</div>'
             f'<div class="q-text">{q["text"]}</div>')
        st.radio(
            label=f'Question {q["number"]}: {q["text"]}',
            options=q["options"],
            index=None,
            key=key,
            horizontal=(kind == "likert"),
            label_visibility="collapsed",
            on_change=_save_answer,
            args=(qid,),
        )
        if flagged and not _is_answered(qid):
            html('<div class="q-missing">Please select an answer to continue.</div>')


def _render_step(step_index: int) -> None:
    step = STEPS[step_index]
    html(f'<div class="section-title">{step["title"]}</div><div class="section-sub">{step["intro"]}</div>')
    flagged = st.session_state["flag_missing_step"] == step_index
    for q in step["questions"]:
        _render_question(q, step["kind"], flagged)

    if flagged:
        count = len(_missing_in(step_index))
        st.error(f"{count} question{'s' if count != 1 else ''} in this section still need"
                 f"{'s' if count == 1 else ''} an answer.")

    left, _, right = st.columns([1, 3, 1])
    left.button("Back", key=f"back_{step_index}", on_click=_prev_step,
                disabled=(step_index == 0), use_container_width=True)
    right.button("Next" if step_index < len(STEPS) - 1 else "Review answers", key=f"next_{step_index}",
                 type="primary", on_click=_next_step, use_container_width=True)


def _render_review() -> None:
    html('<div class="section-title">Review your answers</div>'
         '<div class="section-sub">Check each section. Choose Edit to change an answer before submitting.</div>')

    for index, step in enumerate(STEPS):
        with st.container(border=True, key=f"revcard_{index}"):
            top, edit = st.columns([5, 1])
            top.markdown(f"**{step['title']}**")
            edit.button("Edit", key=f"edit_{index}", on_click=_jump_to, args=(index,),
                        use_container_width=True)
            rows = []
            for q in step["questions"]:
                answer = _answers().get(q["id"])
                cell = (f'<div class="review-a">{answer}</div>' if answer
                        else '<div class="review-a missing">Not answered</div>')
                rows.append(f'<div class="review-row"><div class="review-q">{q["number"]}. {q["text"]}</div>{cell}</div>')
            html("".join(rows))

    missing = _missing_all()
    if missing:
        numbers = ", ".join(str(q["number"]) for q in missing)
        st.error(f"{len(missing)} question{'s' if len(missing) != 1 else ''} still unanswered "
                 f"(question {numbers}). Complete them to enable submission.")
        st.button("Go to first unanswered question", key="goto_missing",
                  on_click=_jump_to_first_missing)

    if st.session_state["submit_error"]:
        st.error(st.session_state["submit_error"])

    left, _, right = st.columns([1, 3, 1.6])
    left.button("Back", key="back_review", on_click=_prev_step, use_container_width=True)
    right.button("Submit Assessment", key="submit", type="primary", on_click=_submit,
                 disabled=bool(missing), use_container_width=True)


def render_assessment() -> None:
    step = st.session_state["step"]

    if step == 0:
        _intro()
        st.write("")

    head, reset = st.columns([5, 1])
    with head:
        _stepper(step)
    reset.button("Start Over", key="start_over", on_click=reset_assessment, use_container_width=True)
    _progress()
    st.write("")

    if step == REVIEW_STEP:
        _render_review()
    else:
        _render_step(step)