"""ui/home.py - landing page."""

from __future__ import annotations

import streamlit as st

from ui.state import go
from ui.theme import html


def render_home() -> None:
    left, right = st.columns([1.15, 1], gap="large")

    with left:
        html('<span class="eyebrow">Responsible AI for Brighter Learning</span>')
        html(
            """
            <div class="hero-title">Think independently.<br>
            <span class="grad">Learn intelligently.</span></div>
            <div class="hero-desc">Discover how your Generative AI usage relates to your independent
            learning, verification habits, and metacognitive strategies. Receive an
            evidence-informed assessment with explainable insights and adaptive learning
            recommendations.</div>
            """
        )
        st.write("")
        c1, c2, c3 = st.columns(3)
        c1.button("Start Your Assessment", type="primary", key="home_start",
                  on_click=go, args=("Assessment",), use_container_width=True)
        c2.button("Explore Research", key="home_research",
                  on_click=go, args=("Research",), use_container_width=True)
        c3.button("Explore Model Insights", key="home_insights",
                  on_click=go, args=("Model Insights",), use_container_width=True)

    with right:
        html(
            """
            <div class="hero-panel">
              <div class="hero-chip"><span class="chip-dot" style="background:#4F7CFF"></span>
                <div>Detect<small>Estimate AI reliance from your own answers</small></div></div>
              <div class="hero-chip"><span class="chip-dot" style="background:#8B7CF6"></span>
                <div>Understand<small>See which behaviours shaped the estimate</small></div></div>
              <div class="hero-chip"><span class="chip-dot" style="background:#2FBF9B"></span>
                <div>Support<small>Adaptive, rule-based learning activities</small></div></div>
              <div class="hero-chip"><span class="chip-dot" style="background:#F59E6B"></span>
                <div>Learn<small>Build independent reasoning habits</small></div></div>
            </div>
            """
        )

    st.write("")
    benefits = [
        ("1", "Understand your AI reliance",
         "See an estimated score from your self-reported learning habits."),
        ("2", "Understand what influences your result",
         "Explainable AI shows which behaviours pushed the estimate up or down."),
        ("3", "Build stronger independent reasoning",
         "Practise verification, self-testing and reflection with guided activities."),
    ]
    cols = st.columns(3, gap="medium")
    for col, (num, title, text) in zip(cols, benefits):
        with col:
            html(f'<div class="card"><div class="num-badge">{num}</div><h4>{title}</h4><p>{text}</p></div>')

    st.write("")
    html('<div class="section-title">What Cognivue AI offers</div>'
         '<div class="section-sub">A structured way to reflect on AI-assisted learning.</div>')
    features = [
        ("📈", "tint-blue", "AI Reliance Prediction",
         "A trained Random Forest estimates an overreliance score from 1 to 5 using your questionnaire answers."),
        ("🔍", "tint-lav", "Explainable AI",
         "SHAP shows how each factor moved the model's estimate, in plain language."),
        ("🧭", "tint-mint", "Behavioural Insights",
         "Understand your independent learning, verification and metacognition scores."),
        ("🎯", "tint-peach", "Adaptive Interventions",
         "Receive rule-based activities that encourage independent thinking and verification."),
    ]
    cols = st.columns(4, gap="medium")
    for col, (icon, tint, title, text) in zip(cols, features):
        with col:
            html(f'<div class="card"><div class="icon-badge {tint}">{icon}</div><h4>{title}</h4><p>{text}</p></div>')

    st.write("")
    html('<div class="section-title">Your journey</div>'
         '<div class="section-sub">Five steps from questionnaire to personalised support.</div>')
    steps = [
        ("STEP 1", "Student Assessment", "24 short questions"),
        ("STEP 2", "Feature Processing", "Construct scores and encodings"),
        ("STEP 3", "Machine Learning Prediction", "Random Forest regression"),
        ("STEP 4", "Explainable Analysis", "SHAP contributions"),
        ("STEP 5", "Adaptive Intervention", "Interactive learning activity"),
    ]
    inner = "".join(
        f'<div class="flow-step"><span class="n">{n}</span>{t}<small>{s}</small></div>'
        for n, t, s in steps
    )
    html(f'<div class="flow">{inner}</div>')

    st.write("")
    html('<div class="section-title">Research architecture</div>'
         '<div class="section-sub">The prediction pipeline built from the questionnaire study.</div>')
    arch = [
        ("Questionnaire dataset", "151 consented responses", True),
        ("Cleaning and preprocessing", "Encoding and validation", False),
        ("Construct score calculation", "Four learning constructs", False),
        ("Feature engineering", "Nine model features", False),
        ("Random Forest regression", "Saved, tuned model", True),
        ("Predicted overreliance score", "Continuous, 1 to 5", False),
        ("SHAP explanation", "Per-student contributions", False),
        ("Adaptive intervention", "Rule-based support", True),
    ]
    inner = "".join(
        f'<div class="flow-step{" accent" if a else ""}">{t}<small>{s}</small></div>'
        for t, s, a in arch
    )
    html(f'<div class="flow arch-main">{inner}</div>')
    st.write("")
    html(
        """
        <div class="label-sm">Separate research components</div>
        <div class="chips">
          <div class="chip">K-Means behavioural profiling<small>Exploratory, K = 2</small></div>
          <div class="chip">Deep Learning comparison<small>Comparative experiment only</small></div>
          <div class="chip">Noise robustness<small>Gaussian input perturbation</small></div>
          <div class="chip">CTGAN augmentation<small>Tested, did not improve the model</small></div>
        </div>
        """
    )