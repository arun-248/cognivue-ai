"""
ui/assessment.py
----------------
24-question assessment (5 profile + 19 Likert), review page and submission.

* No default answers: every radio starts unselected.
* Answers persist in st.session_state["answers"] while navigating sections.
* Answers live in the session only; nothing is written to disk.
"""

from __future__ import annotations

import streamlit as st

from backend.clustering import assign_cluster
from backend.interventions import evaluate_interventions
from backend.model_loader import get_model_information
from backend.prediction import predict_overreliance
from backend.preprocessing import preprocess_responses
from backend.questionnaire import LIKERT_LABELS, LIKERT_SECTIONS, PROFILE_QUESTIONS, REQUIRED_KEYS
from backend.validation import ValidationError, validate_responses
from ui.resources import get_models
from ui.state import goto, request_scroll_top
from ui.theme import esc, md_html, notice, stat

TOTAL = len(REQUIRED_KEYS)  # 24
REVIEW_STEP = 5

STEP_PROMPTS = {
    0: ("Let's start with your study background",
        "These details give context to your estimate. Choose the option that fits you best.",
        "Choose one option for each question"),
    1: ("How do you work through problems on your own?",
        "Think about your typical academic work over the past 30 days.",
        "Choose how much you agree with each statement"),
    2: ("How do you check what AI tells you?",
        "Think about the past 30 days. Be honest; there are no right or wrong answers.",
        "Choose how much you agree with each statement"),
    3: ("How closely do you monitor your own understanding?",
        "Metacognition means monitoring and evaluating your own understanding and learning.",
        "Choose how much you agree with each statement"),
    4: ("What does Generative AI do for your learning?",
        "Consider the outcomes you have noticed over the past 30 days.",
        "Choose how much you agree with each statement"),
}
SHORT_NAMES = ["Profile", "Independent Learning", "Verification", "Metacognition", "Learning Benefits"]


def _build_steps() -> list:
    steps = [{
        "name": SHORT_NAMES[0],
        "title": "Section A \u00b7 Student profile",
        "kind": "profile",
        "questions": [
            {"id": q["key"], "text": q["text"], "options": [label for label, _ in q["options"]]}
            for q in PROFILE_QUESTIONS
        ],
    }]
    for index, sec in enumerate(LIKERT_SECTIONS, start=1):
        steps.append({
            "name": SHORT_NAMES[index],
            "title": f"Section {sec['section']} \u00b7 {sec['title']}",
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
        st.session_state["result"] = None   # any change makes an old result stale
        st.session_state["submit_error"] = None


def _next_step() -> None:
    step = st.session_state["step"]
    if _missing_in(step):
        st.session_state["flag_missing_step"] = step
        return
    st.session_state["flag_missing_step"] = None
    st.session_state["step"] = min(step + 1, REVIEW_STEP)
    request_scroll_top()


def _prev_step() -> None:
    st.session_state["flag_missing_step"] = None
    st.session_state["step"] = max(st.session_state["step"] - 1, 0)
    request_scroll_top()


def _jump_to(step: int) -> None:
    st.session_state["flag_missing_step"] = None
    st.session_state["step"] = int(step)
    request_scroll_top()


def _jump_to_first_missing() -> None:
    for index in range(len(STEPS)):
        if _missing_in(index):
            st.session_state["step"] = index
            st.session_state["flag_missing_step"] = index
            request_scroll_top()
            return


def reset_intervention() -> None:
    store = st.session_state["_sticky"]
    for key in [k for k in store if k.startswith("iv_")]:
        store.pop(key, None)
        st.session_state.pop(key, None)
    st.session_state["iv_example_n"] = 0


def reset_assessment() -> None:
    """Start Over: clear every answer, widget state and result."""
    for key in [k for k in st.session_state.keys() if k.startswith("w_")]:
        del st.session_state[key]
    st.session_state["answers"] = {}
    st.session_state["step"] = 0
    st.session_state["result"] = None
    st.session_state["submit_error"] = None
    st.session_state["flag_missing_step"] = None
    reset_intervention()
    request_scroll_top()


def _submit() -> None:
    """Validate, preprocess and predict. Runs as a callback so it can change page."""
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
        cluster = assign_cluster(models["kmeans_model"], models["kmeans_scaler"], student.frame)
        interventions = evaluate_interventions(student.construct_scores)
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

    reset_intervention()
    st.session_state["result"] = {
        "features": student.features,
        "construct_scores": student.construct_scores,
        "frame": student.frame,
        "prediction": prediction,
        "cluster": cluster,
        "interventions": interventions,
        "labels": {q["key"]: answers[q["key"]] for q in PROFILE_QUESTIONS},
        "shap": None,
        "model_warning": None if info["sklearn_versions_match"] else (
            f"The saved model was trained with scikit-learn {info['sklearn_trained_with']} but "
            f"{info['sklearn_installed']} is installed. Install scikit-learn==1.6.1."
        ),
    }
    goto("Results")


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------
def _intro() -> None:
    md_html(
        '<div class="eyebrow">Assessment</div>'
        '<div class="section-title" style="margin-top:0">Understand Your Learning Habits</div>'
        '<div class="section-sub">Answer honestly based on your typical academic use of Generative AI over the '
        'past 30 days. There are no right or wrong answers. This assessment uses self-reported responses only.</div>'
    )
    md_html(
        '<div class="grid g4">'
        + stat(str(TOTAL), "Questions in total", "about 5\u20138 minutes")
        + stat(str(len(PROFILE_QUESTIONS)), "Profile questions", "background and AI usage")
        + stat(str(TOTAL - len(PROFILE_QUESTIONS)), "Likert statements", "Strongly Disagree to Strongly Agree")
        + stat("5", "Short sections", "plus a final review")
        + "</div>"
    )
    st.write("")
    notice(
        "<b>Privacy.</b> Your answers are processed in memory for this browser session only. Cognivue AI does not ask for "
        "your name, email or student ID, and does not write your answers to a file or database. Choosing Start Over clears them.",
        "info",
    )
    st.write("")


def _chips(current: int) -> None:
    chips = []
    for i, step in enumerate(STEPS):
        done = not _missing_in(i)
        cls = "chip active" if i == current else ("chip done" if done else "chip")
        tick = "\u2713 " if (done and i != current) else ""
        chips.append(f'<div class="{cls}">{tick}{i + 1}. {step["name"]}</div>')
    chips.append(f'<div class="{"chip active" if current == REVIEW_STEP else "chip"}">Review</div>')
    md_html(f'<div class="stepper">{"".join(chips)}</div>')


def _progress() -> None:
    answered = TOTAL - len(_missing_all())
    st.progress(answered / TOTAL, text=f"{answered} of {TOTAL} questions answered")


def _render_question(q: dict, flagged: bool) -> None:
    qid, key = q["id"], f"w_{q['id']}"
    # Streamlit drops widget state for widgets that are not on screen, so restore it.
    if key not in st.session_state and _is_answered(qid):
        st.session_state[key] = _answers()[qid]
    with st.container(border=True, key=f"qcard_{qid}"):
        md_html(f'<div class="qq-label">Question {q["number"]} of {TOTAL}</div>'
                f'<div class="qq-text">{esc(q["text"])}</div>')
        st.radio(
            label=f'Question {q["number"]}: {q["text"]}',
            options=q["options"],
            index=None,
            key=key,
            horizontal=True,
            label_visibility="collapsed",
            on_change=_save_answer,
            args=(qid,),
        )
        if flagged and not _is_answered(qid):
            md_html('<div class="q-missing">Please select an answer to continue.</div>')


def _render_step(step_index: int) -> None:
    step = STEPS[step_index]
    title, sub, hint = STEP_PROMPTS[step_index]
    md_html(
        f'<div class="q-card"><div class="q-num">{step_index + 1}</div><div>'
        f'<div class="q-kicker">{esc(step["title"])}</div>'
        f'<div class="q-title">{esc(title)}</div><div class="q-sub">{esc(sub)}</div>'
        f'<div class="q-hint">{esc(hint)}</div></div></div>'
    )
    st.write("")
    flagged = st.session_state["flag_missing_step"] == step_index
    for q in step["questions"]:
        _render_question(q, flagged)

    if flagged:
        count = len(_missing_in(step_index))
        st.error(f"{count} question{'s' if count != 1 else ''} in this section still need"
                 f"{'s' if count == 1 else ''} an answer.")

    st.write("")
    back_col, _, next_col = st.columns([1, 3, 1.4])
    with back_col:
        if step_index > 0:
            st.button("Back", icon=":material/arrow_back:", on_click=_prev_step, key="assess_back")
    with next_col:
        st.button("Review answers" if step_index == len(STEPS) - 1 else "Next", type="primary",
                  on_click=_next_step, key="assess_next")


def _render_review() -> None:
    notice("<b>Review your answers.</b> Check each section and choose Edit to change an answer before submitting.", "info")
    st.write("")
    for i, step in enumerate(STEPS):
        missing = _missing_in(i)
        badge = ('<span class="badge" style="color:#15803D;border-color:rgba(34,197,94,.45)">Complete</span>'
                 if not missing else
                 '<span class="badge" style="color:#B45309;border-color:rgba(245,158,11,.55)">Unanswered questions</span>')
        rows = []
        for q in step["questions"]:
            answer = _answers().get(q["id"])
            cell = f'<td class="ans">{esc(answer)}</td>' if answer else '<td class="miss">Not answered</td>'
            rows.append(f'<tr><td>{q["number"]}. {esc(q["text"])}</td>{cell}</tr>')
        md_html(
            f'<div class="card review-wrap" style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;'
            f'align-items:center;margin-bottom:8px"><h4 style="margin:0">{esc(step["title"])}</h4>{badge}</div>'
            f'<table class="rtable"><tr><th>Question</th><th>Your answer</th></tr>{"".join(rows)}</table></div>'
        )
    st.caption("Edit a section:")
    edit_cols = st.columns(len(STEPS))
    for i, col in enumerate(edit_cols):
        with col:
            st.button(f"Edit {i + 1}", on_click=_jump_to, args=(i,), key=f"review_edit_{i}", use_container_width=True)

    missing_all = _missing_all()
    if missing_all:
        numbers = ", ".join(str(q["number"]) for q in missing_all)
        st.error(f"{len(missing_all)} question{'s' if len(missing_all) != 1 else ''} still unanswered "
                 f"(question {numbers}). Complete them to enable submission.")
        st.button("Go to first unanswered question", key="goto_missing", on_click=_jump_to_first_missing)
    if st.session_state["submit_error"]:
        st.error(st.session_state["submit_error"])

    st.write("")
    b1, b2, b3 = st.columns([1, 1, 2])
    with b1:
        st.button("Back", icon=":material/arrow_back:", on_click=_prev_step, key="assess_back")
    with b2:
        st.button("Start over", on_click=reset_assessment, key="assess_reset")
    with b3:
        st.button("Submit Assessment", type="primary", on_click=_submit, key="assess_go", disabled=bool(missing_all))


def page_assess() -> None:
    step = min(st.session_state["step"], REVIEW_STEP)
    if step == 0:
        _intro()
    _chips(step)
    _progress()
    st.write("")
    if step == REVIEW_STEP:
        _render_review()
    else:
        _render_step(step)
        st.write("")
        st.button("Start over", on_click=reset_assessment, key="assess_reset")