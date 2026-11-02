"""ui/home.py - landing page (same layout as the earlier project, new content)."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from backend.research_data import DATASET, NESTED_CV
from ui.art import COLLAB_ART, HERO_ART
from ui.feature import FEATURE_ACCENTS, FEATURES
from ui.state import goto, open_feature
from ui.theme import card, md_html, section_title, stat

BASE_DIR = Path(__file__).resolve().parent.parent


def hero_visual() -> str:
    path = BASE_DIR / "assets" / "hero_ai_learning.png"
    if path.exists():
        try:
            encoded = base64.b64encode(path.read_bytes()).decode()
            return f'<img src="data:image/png;base64,{encoded}" alt="Student learning with an AI assistant">'
        except Exception:
            pass
    return HERO_ART


def arch_html() -> str:
    return (
        '<div class="arch-branch"><div class="arch-label">Main pipeline \u00b7 supervised prediction</div>'
        '<div class="flow">'
        '<div class="n">Questionnaire dataset<small>151 consented responses</small></div><i>\u2192</i>'
        '<div class="n">Data cleaning and preprocessing</div><i>\u2192</i>'
        '<div class="n">Construct score calculation<small>4 learning constructs</small></div><i>\u2192</i>'
        '<div class="n">Feature engineering<small>9 model features</small></div><i>\u2192</i>'
        '<div class="n hl">Random Forest regression</div><i>\u2192</i>'
        '<div class="n">Predicted overreliance score<small>continuous, 1\u20135</small></div><i>\u2192</i>'
        '<div class="n">SHAP explanation</div><i>\u2192</i>'
        '<div class="n hl">Adaptive intervention<small>rule-based</small></div></div></div>'
        '<div class="arch-branch"><div class="arch-label">Separate research components</div>'
        '<div class="flow">'
        '<div class="n">K-Means behavioural profiling<small>exploratory, K = 2</small></div>'
        '<div class="n">Deep Learning comparison<small>comparative experiment only</small></div>'
        '<div class="n">Noise robustness<small>Gaussian input perturbation</small></div>'
        '<div class="n">CTGAN augmentation<small>tested; did not improve the model</small></div></div></div>'
    )


def page_home():
    with st.container(key="homehero"):
        h_col, c_col = st.columns([3.1, 1.0], gap="medium")
        with h_col:
            md_html(
                f"""
                <div class="hero2">
                <div>
                <span class="hero-badge">Responsible AI for Brighter Learning</span>
                <h1>Think independently. <span class="hl">Learn intelligently.</span></h1>
                <div class="desc">Discover how your Generative AI usage relates to your independent learning,
                verification habits, and metacognitive strategies. Receive an evidence-informed assessment with
                explainable insights and adaptive learning recommendations.</div>
                <ul class="benefits">
                <li><span class="ck b">\u2713</span>Understand your AI reliance.</li>
                <li><span class="ck p">\u2713</span>Understand what influences your result.</li>
                <li><span class="ck m">\u2713</span>Build stronger independent reasoning habits.</li>
                </ul>
                </div>
                <div><div class="hero-art">{hero_visual()}</div>
                <div class="hero-pills"><span class="pill-b">Detect</span><span class="pill-m">Understand</span><span class="pill-l">Support</span></div></div>
                </div>
                """
            )
        with c_col:
            md_html(
                f"""
                <div class="collab">{COLLAB_ART}
                <div class="cap"><h3>Human\u2013AI Collaboration</h3>
                <p>AI as a learning assistant, with the student still doing the thinking.</p></div></div>
                """
            )
    st.write("")
    with st.container(key="actions"):
        a1, a2, a3 = st.columns(3, gap="medium")
        with a1:
            with st.container(key="act1"):
                st.button("Start Your Assessment", icon=":material/assignment:", on_click=goto, args=("Assess",), key="home_start")
        with a2:
            with st.container(key="act2"):
                st.button("Explore Research", icon=":material/menu_book:", on_click=goto, args=("Research",), key="home_research")
        with a3:
            with st.container(key="act3"):
                st.button("Explore Model Insights", icon=":material/bar_chart:", on_click=goto, args=("Model Insights",), key="home_models")

    section_title("What Cognivue AI offers",
                  "A research-based framework to understand, explain and support responsible AI-assisted learning. "
                  "Insights come from your questionnaire answers, not from analysis of your actual AI prompts or conversations.")
    with st.container(key="features"):
        cols = st.columns(4, gap="medium")
        for i, (col, (title, desc, _page, bg, icon)) in enumerate(zip(cols, FEATURES)):
            with col:
                with st.container(key=f"feat{i}"):
                    md_html(f'<div class="feat-ic" style="background:{bg}">{icon}</div><div class="feat-title">{title}</div>'
                            f'<div class="feat-desc">{desc}</div><div class="feat-more" style="color:{FEATURE_ACCENTS[i]}">Learn more</div>')
                    st.button(f"Learn more about {title}", key=f"feat_btn_{i}", on_click=open_feature, args=(i,))

    section_title("Student experience", "Five steps from self-report to a personalised learning activity.")
    steps = [
        ("Student Assessment", "Answer 24 short questions about your AI use and learning habits."),
        ("Feature Processing", "Answers become four construct scores and five encoded profile features."),
        ("ML Prediction", "A saved Random Forest estimates your overreliance score."),
        ("Explainable Analysis", "SHAP shows which answers moved the estimate."),
        ("Adaptive Intervention", "A rule-based activity encourages independent reasoning."),
    ]
    parts = []
    for i, (title, text) in enumerate(steps, 1):
        parts.append(f'<div class="step"><div class="num">{i}</div><h5>{title}</h5><p>{text}</p></div>')
        if i < len(steps):
            parts.append('<div class="arrow">\u2192</div>')
    md_html(f'<div class="steps">{"".join(parts)}</div>')

    section_title("Research architecture", "The current pipeline built from the questionnaire study.")
    md_html(arch_html())

    section_title("Research evaluation", "Reported from the project's own experiments on the questionnaire dataset.")
    md_html(
        '<div class="grid g4">'
        + stat(str(DATASET["consented"]), "Consented respondents", f'of {DATASET["original_rows"]} responses collected')
        + stat(str(DATASET["features"]), "Model input features", "4 constructs + 5 profile encodings")
        + stat(f'{NESTED_CV["R2"]:.3f}', "Nested CV R\u00b2", "internal estimate, no external validation", "#109A8A")
        + stat(f'{NESTED_CV["MAE"]:.3f}', "Nested CV MAE", "on a 1\u20135 target scale", "#3478F6")
        + "</div>"
    )