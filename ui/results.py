"""ui/results.py - estimated overreliance score, learning-habit scores, summary and recommendations."""

from __future__ import annotations

import numpy as np
import streamlit as st

from backend.history import CONSTRUCTS, compare_attempts
from backend.interventions import ACTIVITIES, NEUTRAL_MIDPOINT, recommended_focus
from backend.questionnaire import CONSTRUCT_LABELS
from backend.research_data import NESTED_CV
from ui import charts
from ui.assessment import reset_assessment
from ui.state import goto
from ui.theme import chart_card, esc, md_html, notice, section_title, stat

CONSTRUCT_ORDER = list(CONSTRUCT_LABELS.keys())
CONSTRUCT_COLORS = ["#3478F6", "#8757E8", "#0F8F80", "#E8731F"]
SHORT = {"independent_learning_score": "Independent learning", "verification_score": "Verification",
         "metacognition_score": "Metacognition", "learning_benefit_score": "Learning benefits"}


def gauge_svg(score: float) -> str:
    radius = 100
    circumference = 2 * np.pi * radius
    frac = min(max((score - 1) / 4, 0), 1)
    dash = circumference * frac
    return f"""
    <svg width="290" height="290" viewBox="0 0 260 260" style="max-width:100%;height:auto" role="img" aria-label="Estimated overreliance score {score:.2f} out of 5">
    <defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3478F6"/><stop offset="1" stop-color="#8757E8"/></linearGradient></defs>
    <circle cx="130" cy="130" r="{radius}" fill="none" stroke="#D9E6F7" stroke-width="16"/>
    <circle cx="130" cy="130" r="{radius}" fill="none" stroke="url(#gg)" stroke-width="16" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circumference:.1f}" transform="rotate(-90 130 130)"/>
    <text x="130" y="94" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="10" font-weight="700" letter-spacing="1.2" fill="#425B82">ESTIMATED SCORE</text>
    <text x="130" y="150" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="54" font-weight="800" fill="#142B55">{score:.2f}</text>
    <text x="130" y="180" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="16" fill="#425B82">out of 5</text>
    </svg>
    """


def scale_html(score: float, baseline: float | None) -> str:
    pct = min(max((score - 1) / 4 * 100, 0), 100)
    base = ""
    if baseline is not None:
        bpct = min(max((baseline - 1) / 4 * 100, 0), 100)
        base = f'<div class="mid" style="left:{bpct:.2f}%" title="model baseline"></div>'
    return f"""
    <div class="scale">
    <div class="scale-one">{base}<div class="marker" style="left:{pct:.2f}%"><span>{score:.2f}</span></div></div>
    <div class="ticks">
    <span style="left:0%">1</span><span style="left:25%">2</span><span style="left:50%">3</span>
    <span style="left:75%">4</span><span style="left:100%">5</span>
    </div>
    </div>
    """


def behaviour_summary(scores: dict, labels: dict) -> str:
    """Plain-language summary of the four section averages relative to the neutral midpoint."""
    above = [SHORT[f].lower() for f in CONSTRUCT_ORDER if scores[f] >= NEUTRAL_MIDPOINT]
    below = [SHORT[f].lower() for f in CONSTRUCT_ORDER if scores[f] < NEUTRAL_MIDPOINT]
    parts = []
    if above:
        parts.append(f"Your answers show {'a self-reported strength' if len(above) == 1 else 'self-reported strengths'} in {', '.join(above)} "
                     f"(average at or above the neutral midpoint of {NEUTRAL_MIDPOINT:.1f}).")
    if below:
        parts.append(f"Your {', '.join(below)} {'score is' if len(below) == 1 else 'scores are'} below the midpoint, so "
                     f"{'this is' if len(below) == 1 else 'these are'} suggested as {'an area' if len(below) == 1 else 'areas'} to practise.")
    if not below:
        parts.append("None of the four dimensions fell below the midpoint, so the suggestions focus on keeping these habits.")
    parts.append(f"You reported using Generative AI for academic work {labels['usage_frequency'].lower()}, with {labels['usage_duration'].lower()} on a typical study day.")
    return " ".join(parts)


def page_results():
    result = st.session_state.get("result")
    section_title("Your AI Reliance Assessment Results", "A decision-support estimate from your self-reported learning habits.")

    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the short assessment first. '
                'This page will then show your estimated score.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_results")
        return

    if result["model_warning"]:
        st.warning(result["model_warning"])
    pred = result["prediction"]
    if pred["was_clipped"]:
        st.info("The raw model output was outside 1\u20135 and has been limited to the valid range.")

    notice("<b>This is a model estimate, not a diagnosis.</b> It estimates a <i>self-reported questionnaire score</i> on a continuous 1\u20135 scale. "
           "It is not a probability, a psychological assessment or a category, and Low / Moderate / High labels are deliberately not used.", "info")
    st.write("")

    baseline = None
    try:
        from ui.resources import get_cached_explainer
        baseline = float(np.ravel(get_cached_explainer().expected_value)[0])
    except Exception:
        baseline = None

    # ---------------- A. predicted score ----------------
    md_html('<div class="eyebrow">A \u00b7 Model output</div>')
    left, right = st.columns([1, 1.25], gap="large")
    with left:
        md_html(f'<div class="card gauge-wrap">{gauge_svg(pred["score"])}</div>')
    with right:
        base_text = (f" For reference, the model's average output across its training data is {baseline:.2f} "
                     "(the thin line on the scale below)." if baseline is not None else "")
        md_html(
            f"""
            <div class="card">
            <div class="eyebrow">Predicted overreliance score</div>
            <h4 style="font-size:1.2rem">{pred['score']:.2f} out of 5</h4>
            <p style="color:#425B82;font-size:.95rem">Higher values mean the model estimates stronger self-reported reliance on
            Generative AI for answers like yours; lower values mean weaker reliance. The seven direct overreliance questions were
            <b>not</b> asked: the score is <b>predicted</b> by a Random Forest from your learning habits and background.{base_text}</p>
            </div>
            """
        )
    md_html(f'<div class="card" style="margin-top:12px">{scale_html(pred["score"], baseline)}</div>')

    # ---------------- B. questionnaire scores ----------------
    st.write("")
    md_html('<div class="eyebrow">B \u00b7 Calculated directly from your answers</div>')
    section_title("Your learning-habit scores", "These four scores are plain averages of your own answers in each section (1 = Strongly Disagree, 5 = Strongly Agree). "
                  "They are not predictions, and they are different from the predicted score above.")
    scores = result["construct_scores"]
    labels = result["labels"]
    cards = [stat(f"{scores[f]:.2f} / 5", CONSTRUCT_LABELS[f], "section average") for f in CONSTRUCT_ORDER]
    cards.append(stat(labels["usage_frequency"], "AI usage frequency", "as you selected"))
    cards.append(stat(labels["usage_duration"], "AI usage on a study day", "as you selected"))
    md_html(f'<div class="grid g3">{"".join(cards)}</div>')

    st.write("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("How do my four learning-habit scores compare?"):
            charts.show(charts.construct_bars([SHORT[f] for f in CONSTRUCT_ORDER], [scores[f] for f in CONSTRUCT_ORDER],
                                              CONSTRUCT_COLORS), "res_bars")
            st.caption("Bars show your section averages; the dashed line is the neutral midpoint (3.0), a heuristic used by the intervention rules.")
    with c2:
        with chart_card("What does my pattern look like?"):
            charts.show(charts.radar([SHORT[f] for f in CONSTRUCT_ORDER], {"You": [scores[f] for f in CONSTRUCT_ORDER]}, {"You": "#0F8F80"}), "res_radar")
            st.caption("The shaded shape is your four section averages on a 1\u20135 scale.")

    # ---------------- C. summary, focus, recommendations ----------------
    section_title("Summary of your learning behaviour")
    md_html(f'<div class="sumbox">{esc(behaviour_summary(scores, labels))}</div>')

    records = result["interventions"]
    focus = recommended_focus(records)
    flagged = [r for r in records if r["Priority"] == "Focus area"]
    st.write("")
    md_html(
        f'<div class="iv-card"><div class="eyebrow">{"Most important area to look at" if flagged else "Suggested area to keep strong"}</div>'
        f'<h2 style="text-transform:none">{esc(focus["Construct"])} \u00b7 {focus["Observed_Score"]:.2f} / 5</h2>'
        f'<div class="why">{esc(focus["Intervention"])}</div>'
        f'<div style="margin-top:12px"><span class="badge cyan">Suggested activity: {esc(ACTIVITIES[focus["Feature"]]["title"])}</span></div></div>'
    )
    st.write("")
    section_title("Personalised recommendations", "Rule-based suggestions, with areas below the midpoint first.")
    ordered = sorted(records, key=lambda r: (r["Priority"] != "Focus area", r["Observed_Score"]))
    items = "".join(
        f'<div class="factor"><div class="dot" style="background:{"#D97706" if r["Priority"] == "Focus area" else "#0F8F80"}"></div><div>'
        f'<div class="ft">{esc(r["Construct"])} \u00b7 {esc(r["Status"])}</div><div class="fd">{esc(r["Intervention"])}</div></div></div>'
        for r in ordered
    )
    md_html(f'<div class="card">{items}</div>')

    # ---------------- D. comparison ----------------
    history = st.session_state.get("history", [])
    if len(history) >= 2:
        prev, last = history[-2], history[-1]
        delta = compare_attempts(prev, last)
        section_title("Compared with your previous attempt", "Changes in self-reported scores between two attempts in this session.")
        md_html('<div class="grid g3">'
                + stat(f"{delta['predicted_score']:+.2f}", "Predicted overreliance score", f"{prev['predicted_score']:.2f} \u2192 {last['predicted_score']:.2f}")
                + "".join(stat(f"{delta['construct_scores'][f]:+.2f}", SHORT[f], f"{prev['construct_scores'][f]:.2f} \u2192 {last['construct_scores'][f]:.2f}")
                          for f in CONSTRUCTS[:2]) + "</div>")
        st.caption("These are differences in self-reported scores. They do not prove a change in actual ability. See the Progress page for all attempts.")

    section_title("How to read this result")
    md_html(
        '<div class="grid g2">'
        + f'<div class="card"><h4>Prediction accuracy and limitations</h4><p>In nested cross-validation the model\'s average error was about '
          f'{NESTED_CV["MAE"]:.2f} points (RMSE {NESTED_CV["RMSE"]:.2f}, R\u00b2 {NESTED_CV["R2"]:.2f}). That is moderate, so an individual estimate '
          'can be off by more. It was built from 151 respondents and has not been validated on an independent student population.</p></div>'
        + '<div class="card"><h4>What the estimate can and cannot say</h4><p>It uses self-reported answers, not your actual AI prompts, browsing or '
          'usage logs. It does not diagnose you, and it does not show that AI use causes any change in thinking or learning.</p></div>'
        + "</div>"
    )
    st.write("")
    c1, c2, c3, c4 = st.columns([1.1, 1.3, 1.3, 1])
    with c1:
        st.button("Why this result?", type="primary", on_click=goto, args=("Why This Result?",), key="res_why")
    with c2:
        st.button("Start my activities", on_click=goto, args=("Intervention",), key="res_iv")
    with c3:
        st.button("Report & progress", on_click=goto, args=("Progress",), key="res_progress")
    with c4:
        st.button("Start over", key="results_reset", on_click=lambda: (reset_assessment(), goto("Assess")))
