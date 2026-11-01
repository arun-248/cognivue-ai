"""ui/results.py - prediction result (Phase 4). Charts are added in Phase 5."""

from __future__ import annotations

import streamlit as st

from backend.questionnaire import CONSTRUCT_LABELS
from ui.assessment import reset_assessment
from ui.state import go
from ui.theme import html

# Verified nested cross-validation estimate (Cognivue_Model_Metadata.json)
NESTED_CV_MAE = 0.4963


def _score_card(prediction: dict) -> None:
    score = prediction["score"]
    position = (score - 1.0) / 4.0 * 100
    html(
        f"""
        <div class="score-card">
          <div class="label-sm">Estimated overreliance score</div>
          <div class="score-big">{score:.2f}<span> / 5</span></div>
          <div class="scale"><div class="scale-marker" style="left:{position:.1f}%"></div></div>
          <div class="scale-labels"><span>1 · lower self-reported reliance</span>
          <span>5 · higher self-reported reliance</span></div>
          <p style="margin:18px 0 0 0;color:#4A5775;line-height:1.7">
          This is a continuous estimate produced by a Random Forest trained on questionnaire responses.
          Higher values mean the model estimates stronger self-reported reliance on Generative AI for
          the kind of answers you gave. It is <b>not</b> a probability, a category, or a diagnosis.</p>
        </div>
        """
    )


def _construct_cards(scores: dict) -> None:
    cols = st.columns(4, gap="medium")
    for col, (feature, label) in zip(cols, CONSTRUCT_LABELS.items()):
        value = scores[feature]
        width = (value - 1) / 4 * 100
        with col:
            html(
                f'<div class="card"><div class="label-sm">{label}</div>'
                f'<div class="big-num">{value:.2f}<span> / 5</span></div>'
                f'<div class="mini-bar"><div style="width:{width:.0f}%"></div></div></div>'
            )


def render_results() -> None:
    result = st.session_state.get("result")

    html('<div class="section-title">Your AI Reliance Assessment Results</div>')

    if not result:
        html('<div class="note">No result yet. Complete and submit the assessment to see your '
             'estimated score.</div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=go, args=("Assessment",))
        return

    if result["model_warning"]:
        st.warning(result["model_warning"])
    if result["prediction"]["was_clipped"]:
        st.info("The raw model output was outside 1–5 and has been limited to the valid range.")

    _score_card(result["prediction"])
    st.write("")
    html('<div class="section-title" style="font-size:22px">Your learning-habit scores</div>'
         '<div class="section-sub">Each score is the average of your answers in that section '
         '(1 = Strongly Disagree, 5 = Strongly Agree).</div>')
    _construct_cards(result["construct_scores"])

    st.write("")
    labels = result["labels"]
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        html(f'<div class="card"><div class="label-sm">AI usage frequency</div>'
             f'<div class="big-num" style="font-size:22px">{labels["usage_frequency"]}</div></div>')
    with c2:
        html(f'<div class="card"><div class="label-sm">AI usage duration on a study day</div>'
             f'<div class="big-num" style="font-size:22px">{labels["usage_duration"]}</div></div>')

    st.write("")
    html(
        f"""
        <div class="note"><b>How to read this.</b> In validation, the model's estimates differed from
        the questionnaire-based score by about {NESTED_CV_MAE:.2f} points on average (nested
        cross-validation MAE), so an individual estimate can be off by more than that. The model was
        built from 151 respondents and has not been validated on an independent student population.
        Use the result for reflection, not for decisions about a student.</div>
        """
    )

    st.write("")
    a, b, _ = st.columns([1.4, 1, 3])
    a.button("Edit my answers", on_click=go, args=("Assessment",), use_container_width=True)
    b.button("Start Over", key="results_reset", on_click=lambda: (reset_assessment(), go("Assessment")),
             use_container_width=True)