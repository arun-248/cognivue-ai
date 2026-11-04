"""ui/about.py - project description, technology stack, team and disclaimer."""

from __future__ import annotations

import streamlit as st

from ui.theme import DISCLAIMER, card, esc, md_html, notice, section_title

TITLE = "AI-Based Framework for Detecting Generative AI Overreliance and Providing Adaptive Interventions"

TEAM = [
    {"role": "Member 1", "name": "", "id": "", "focus": ""},
    {"role": "Member 2", "name": "", "id": "", "focus": ""},
    {"role": "Member 3", "name": "C Arun", "id": "CB.SC.P2AIE26008", "focus": ""},
]

STACK = [
    ("Frontend", "Streamlit with custom CSS"),
    ("Backend", "Python modules for validation, preprocessing, prediction, explainability, clustering and interventions"),
    ("Machine learning", "scikit-learn RandomForestRegressor, K-Means"),
    ("Deep learning (comparison)", "TensorFlow / Keras neural network"),
    ("Explainability", "SHAP TreeExplainer"),
    ("Data, charts and reports", "pandas, NumPy, Plotly (interactive charts), ReportLab (PDF reports)"),
    ("Deployment", "GitHub, Docker, Render"),
]


def page_about():
    section_title("About")
    md_html(
        f"""
        <div class="card"><div class="eyebrow">Research Methodology Project \u00b7 M.Tech Artificial Intelligence</div>
        <h4 style="font-size:1.25rem">Cognivue AI</h4>
        <p style="margin-bottom:8px"><b>{esc(TITLE)}</b></p>
        <p>Amrita School of Computing, Amrita Vishwa Vidyapeetham, Coimbatore. The framework estimates potential Generative AI overreliance from self-reported
        questionnaire responses, explains the estimate with SHAP, and offers rule-based learning interventions that encourage independent reasoning, verification and metacognition.
        The aim is responsible AI-assisted learning, where AI supports the student instead of replacing the student's thinking.</p></div>
        """
    )
    st.write("")
    md_html('<div class="grid g2">'
            + card("Objective", "Estimate overreliance from questionnaire responses, identify influential behavioural factors, profile behaviour exploratively with K-Means, and provide adaptive, rule-based interventions.")
            + card("Methodology", "151 consented questionnaire responses \u2192 construct scores and encodings \u2192 tuned Random Forest \u2192 SHAP explanation \u2192 intervention rules, "
                   "with Deep Learning, noise and CTGAN experiments as comparative research components.")
            + "</div>")
    section_title("Technology stack")
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in STACK)
    md_html(f'<div class="card"><table class="rtable"><tr><th>Component</th><th>Technology</th></tr>{rows}</table></div>')
    section_title("Privacy and data usage")
    md_html('<div class="card"><p>Answers are processed in memory for your browser session only; they are not stored on the server, written to a database or included in logs, and no name, '
            'email or student ID is requested. Downloads (PDF report, progress file) are created only on request and contain scores rather than raw answers. '
            'The hosting provider may keep standard technical server logs, which do not contain your answers. Full details are on the Report &amp; Progress page.</p></div>')
    st.write("")
    section_title("Team contributions")
    rows = "".join(
        f"<tr><td>{esc(m['name'] or 'Name to be added')}</td><td>{esc(m['id'] or 'ID to be added')}</td><td>{esc(m['role'])}</td>"
        f"<td>{esc(m['focus'] or 'Contribution to be added')}</td></tr>" for m in TEAM)
    md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr><th>Name</th><th>ID</th><th>Role</th><th>Contribution</th></tr>{rows}</table></div>')
    st.caption("Names, IDs and contributions are shown only where supplied by the team; the rest are left as placeholders.")
    st.write("")
    notice(f"<b>Research prototype disclaimer.</b> {esc(DISCLAIMER)}", "warn")