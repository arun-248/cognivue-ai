"""ui/results.py - estimated overreliance score and supporting scores."""

from __future__ import annotations

import numpy as np
import streamlit as st

from backend.questionnaire import CONSTRUCT_LABELS
from backend.research_data import NESTED_CV
from ui.assessment import reset_assessment
from ui.state import goto
from ui.theme import (C_BLUE, C_CYAN, C_MUTED, C_PURPLE, C_TEXT, chart_card, md_html, notice,
                      section_title, show_fig, stat, themed_fig)

CONSTRUCT_ORDER = list(CONSTRUCT_LABELS.keys())
CONSTRUCT_COLORS = ["#3478F6", "#8757E8", "#109A8A", "#E8731F"]


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


def construct_bar_chart(scores: dict) -> None:
    labels = [CONSTRUCT_LABELS[f] for f in CONSTRUCT_ORDER]
    values = [scores[f] for f in CONSTRUCT_ORDER]
    fig, ax = themed_fig(7, 3.3)
    ax.barh(labels, values, color=CONSTRUCT_COLORS, height=0.55)
    ax.axvline(3.0, color=C_MUTED, linewidth=1.2, linestyle="--")
    ax.text(3.03, -0.62, "neutral midpoint (3.0)", color=C_MUTED, fontsize=8, va="center")
    ax.set_xlim(1, 5)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    for y, v in enumerate(values):
        ax.text(min(v + 0.05, 4.7), y, f"{v:.2f}", va="center", color=C_TEXT, fontsize=9, fontweight="bold")
    ax.set_xlabel("Average of your answers (1 = Strongly Disagree, 5 = Strongly Agree)")
    show_fig(fig)


def radar_chart(scores: dict, extra: dict | None = None) -> None:
    import matplotlib.pyplot as plt
    from ui.theme import C_CARD

    labels = [CONSTRUCT_LABELS[f].replace("Verification and Critical Thinking", "Verification") for f in CONSTRUCT_ORDER]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    fig = plt.figure(figsize=(5.4, 4.8))
    ax = fig.add_subplot(111, polar=True)
    fig.patch.set_facecolor(C_CARD)
    ax.set_facecolor(C_CARD)
    ax.set_ylim(1, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color=C_MUTED, fontsize=8)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, color=C_TEXT, fontsize=9)
    ax.grid(color="#D3E2F5")
    ax.spines["polar"].set_color("#D3E2F5")
    ax.plot(np.linspace(0, 2 * np.pi, 100), [3] * 100, color=C_MUTED, linewidth=1, linestyle="--", alpha=0.6)
    vals = [scores[f] for f in CONSTRUCT_ORDER]
    ax.plot(angles + angles[:1], vals + vals[:1], color=C_CYAN, linewidth=2, label="You")
    ax.fill(angles + angles[:1], vals + vals[:1], color=C_CYAN, alpha=0.18)
    show_fig(fig)


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

    notice("The score is a <b>continuous model estimate</b> on a 1\u20135 scale. It is not a probability, a category or a diagnosis, "
           "and Low / Moderate / High labels are deliberately not used.", "info")
    st.write("")

    baseline = None
    try:
        from ui.resources import get_cached_explainer
        baseline = float(np.ravel(get_cached_explainer().expected_value)[0])
    except Exception:
        baseline = None

    left, right = st.columns([1, 1.25], gap="large")
    with left:
        md_html(f'<div class="card gauge-wrap">{gauge_svg(pred["score"])}</div>')
    with right:
        base_text = (f" For reference, the model's average output across its training data is {baseline:.2f} "
                     "(marked as a thin line on the scale below)." if baseline is not None else "")
        md_html(
            f"""
            <div class="card">
            <div class="eyebrow">Interpretation</div>
            <h4 style="font-size:1.2rem">Estimated Overreliance Score: {pred['score']:.2f} out of 5</h4>
            <p style="color:#425B82;font-size:.95rem">Higher values mean the model estimates stronger self-reported reliance on
            Generative AI for answers like yours; lower values mean weaker reliance. The seven overreliance questions were
            not asked: the estimate is predicted from your learning habits and background.{base_text}</p>
            </div>
            """
        )

    section_title("Where you sit on the scale")
    md_html(f'<div class="card">{scale_html(pred["score"], baseline)}</div>')

    section_title("Your learning-habit scores", "Each score is the average of your answers in that section (1 = Strongly Disagree, 5 = Strongly Agree).")
    scores = result["construct_scores"]
    cards = [stat(f"{scores[f]:.2f} / 5", CONSTRUCT_LABELS[f], "section average") for f in CONSTRUCT_ORDER]
    labels = result["labels"]
    cards.append(stat(labels["usage_frequency"], "AI usage frequency", "as you selected"))
    cards.append(stat(labels["usage_duration"], "AI usage on a study day", "as you selected"))
    md_html(f'<div class="grid g3">{"".join(cards)}</div>')

    st.write("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("How do my four learning-habit scores compare?"):
            construct_bar_chart(scores)
            st.caption("The dashed line is the neutral Likert midpoint (3.0), used by the intervention rules as a heuristic.")
    with c2:
        with chart_card("What does my pattern look like?"):
            radar_chart(scores)
            st.caption("Self-reported averages on a 1\u20135 scale.")

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
    c1, c2, c3, _ = st.columns([1.1, 1.2, 1, 1.5])
    with c1:
        st.button("Why this result?", type="primary", on_click=goto, args=("Why This Result?",), key="res_why")
    with c2:
        st.button("View my intervention", on_click=goto, args=("Intervention",), key="res_iv")
    with c3:
        st.button("Start over", key="results_reset", on_click=lambda: (reset_assessment(), goto("Assess")))