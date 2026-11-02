"""ui/profile.py - Behavioural Insights: construct scores and the exploratory K-Means grouping."""

from __future__ import annotations

import numpy as np
import streamlit as st

from backend.clustering import CLUSTER_FEATURES
from backend.questionnaire import CONSTRUCT_LABELS
from backend.research_data import KMEANS_DISTRIBUTION, KMEANS_FEATURE_MEANS, KMEANS_SILHOUETTE
from ui.results import CONSTRUCT_COLORS, CONSTRUCT_ORDER, radar_chart
from ui.state import goto
from ui.theme import (C_CARD, C_MUTED, C_TEXT, chart_card, esc, md_html, notice, section_title,
                      show_fig, stat, themed_fig)

DESCRIPTIONS = {
    "independent_learning_score": "How often you try problems yourself, develop your own ideas, and re-attempt problems after seeing an AI solution.",
    "verification_score": "How often you check AI-generated information against reliable sources and look for errors, bias or unsupported claims.",
    "metacognition_score": "How well you notice what you know and do not know, test yourself without AI, and change strategy when AI is not helping.",
    "learning_benefit_score": "How strongly you feel Generative AI supports your understanding, recall and long-term learning.",
}
SHORT = {"independent_learning_score": "Independent learning", "verification_score": "Verification",
         "metacognition_score": "Metacognition", "learning_benefit_score": "Learning benefits"}
LEVELS = [(4.0, "Strong"), (3.0, "Moderate"), (0.0, "Developing")]


def level_word(score: float) -> str:
    for cut, word in LEVELS:
        if score >= cut:
            return word
    return "Developing"


def grouped_chart(student: dict, cluster_id: int) -> None:
    feats = CONSTRUCT_ORDER
    x = np.arange(len(feats))
    fig, ax = themed_fig(8, 3.6)
    w = 0.26
    ax.bar(x - w, [student[f] for f in feats], width=w, color="#109A8A", label="You")
    ax.bar(x, [KMEANS_FEATURE_MEANS[0][f] for f in feats], width=w, color="#B9C9E6",
           label="Cluster 0 average", edgecolor="#3478F6" if cluster_id == 0 else "none", linewidth=2)
    ax.bar(x + w, [KMEANS_FEATURE_MEANS[1][f] for f in feats], width=w, color="#D9CCFF",
           label="Cluster 1 average", edgecolor="#3478F6" if cluster_id == 1 else "none", linewidth=2)
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[f] for f in feats])
    ax.set_ylim(1, 5)
    ax.set_ylabel("Average score (1\u20135)")
    ax.grid(axis="x", visible=False)
    ax.legend(facecolor=C_CARD, edgecolor="#C8D9F0", labelcolor=C_TEXT, fontsize=8, loc="lower right")
    show_fig(fig)


def page_profile():
    result = st.session_state.get("result")
    section_title("Understand Your Learning Behaviour", "Based only on the answers you entered in this session.")
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment first. This page will then show your behavioural insights.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_profile")
        return

    scores = result["construct_scores"]
    md_html(
        '<div class="grid g4">'
        + "".join(stat(f"{scores[f]:.2f} / 5", CONSTRUCT_LABELS[f], level_word(scores[f])) for f in CONSTRUCT_ORDER)
        + "</div>"
    )
    st.write("")
    c1, c2 = st.columns([1.1, 1], gap="large")
    with c1:
        with chart_card("What does my learning-behaviour pattern look like?"):
            radar_chart(scores)
            st.caption("Self-reported averages on a 1\u20135 scale; the dashed ring is the neutral midpoint (3.0).")
    with c2:
        bars = []
        for f, color in zip(CONSTRUCT_ORDER, CONSTRUCT_COLORS):
            v = scores[f]
            bars.append(
                f'<div class="mb-row"><div class="top"><span><b>{esc(CONSTRUCT_LABELS[f])}</b></span><span>{v:.2f} / 5</span></div>'
                f'<div class="minibar"><div style="width:{(v - 1) / 4 * 100:.0f}%;background:{color}"></div></div>'
                f'<div style="color:#425B82;font-size:.8rem;margin-top:5px">{esc(DESCRIPTIONS[f])}</div></div>'
            )
        md_html(f'<div class="card"><h4>Construct scores</h4><p style="margin-bottom:14px">These describe your own self-reported habits. '
                f'Descriptions such as Strong, Moderate or Developing are only a plain-language reading of the average (4.0 or more, 3.0 to 3.99, below 3.0).</p>{"".join(bars)}</div>')

    cluster = result["cluster"]
    cid = cluster["cluster_id"]
    section_title("Exploratory behavioural grouping (K-Means)",
                  "Kept separate from your supervised score above. It does not change your estimate.")
    n_k, pct = next((n, p) for c, n, p in KMEANS_DISTRIBUTION if c == cid)
    cluster_means = KMEANS_FEATURE_MEANS[cid]
    md_html(
        '<div class="grid g3">'
        + stat(f"Cluster {cid}", "Closest K-Means group", f"{n_k} of 151 respondents ({pct:.1f}%) in the study")
        + stat(f'{cluster["construct_average"]:.2f}', "Your construct average", "mean of your four construct scores")
        + stat(esc(cluster["profile_label"]), "Exploratory profile label", "construct average \u2265 3.0 = Stronger")
        + "</div>"
    )
    st.write("")
    with chart_card("How do my scores compare with the two K-Means groups?"):
        grouped_chart(scores, cid)
        st.caption("Bars outlined in blue belong to your closest group. Group averages come from the 151-respondent study.")

    rows = "".join(
        f"<tr><td>{esc(f.replace('_', ' ').replace(' encoded', '').replace(' score', '').title())}</td>"
        f"<td>{float(result['frame'].iloc[0][f]):.2f}</td><td>{KMEANS_FEATURE_MEANS[0][f]:.2f}</td><td>{KMEANS_FEATURE_MEANS[1][f]:.2f}</td></tr>"
        for f in CLUSTER_FEATURES
    )
    md_html(f'<div class="card" style="overflow-x:auto"><h4>The six clustering features</h4><table class="rtable"><tr><th>Feature</th><th>You</th>'
            f'<th>Cluster 0 average</th><th>Cluster 1 average</th></tr>{rows}</table>'
            '<p style="margin-top:8px;font-size:.82rem">Usage frequency and duration are coded 0\u20135; construct scores are 1\u20135.</p></div>')
    st.write("")
    notice(
        f"<b>Interpret with care.</b> K-Means (K = 2) was chosen because it had the best silhouette score ({KMEANS_SILHOUETTE[2]:.2f}), which indicates only "
        "moderate separation. In the study, Cluster 0 (120 respondents) had higher average construct scores than Cluster 1 (31 respondents). "
        "The grouping is exploratory: it is not a diagnosis, a personality type, or a validated student category, and the overreliance score was "
        "not used to form the groups.", "warn")
    st.write("")
    st.button("Explore model insights", on_click=goto, args=("Model Insights",), key="prof_mi")