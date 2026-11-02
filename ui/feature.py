"""ui/feature.py - the four feature cards and their detail pages."""

from __future__ import annotations

import streamlit as st

from backend.research_data import NESTED_CV, SHAP_GLOBAL
from ui.state import goto
from ui.theme import card, esc, md_html

FEATURES = [
    ("AI Reliance Prediction", "Estimate your AI reliance with an explainable machine learning model.", "Assess", "#CFE0FB",
     '<svg viewBox="0 0 24 24"><rect x="3" y="12" width="4" height="9" rx="1.2" fill="#3478F6"/><rect x="10" y="7" width="4" height="14" rx="1.2" fill="#3478F6"/><rect x="17" y="3" width="4" height="18" rx="1.2" fill="#3478F6"/></svg>'),
    ("Explainable AI", "See which of your answers influenced the result, using SHAP.", "Why This Result?", "#E0D2FF",
     '<svg viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z" fill="#8757E8"/><rect x="9" y="19" width="6" height="2.4" rx="1.2" fill="#8757E8"/></svg>'),
    ("Behavioural Insights", "Understand your independent learning, verification and metacognition.", "Behavioural Insights", "#BFEBD8",
     '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.4" fill="#109A8A"/><circle cx="17" cy="9" r="2.6" fill="#109A8A" opacity=".7"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6z" fill="#109A8A"/><path d="M16 14.4c2.8.2 5.5 2 5.5 5.6h-4.2c0-2-.5-3.9-1.3-5.6z" fill="#109A8A" opacity=".7"/></svg>'),
    ("Adaptive Interventions", "Receive rule-based learning activities that build independent reasoning.", "Intervention", "#FFD9BE",
     '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="#E8731F" stroke-width="2.4"/><circle cx="12" cy="12" r="5" fill="none" stroke="#E8731F" stroke-width="2.4"/><circle cx="12" cy="12" r="1.8" fill="#E8731F"/></svg>'),
]
FEATURE_ACCENTS = ["#2457D6", "#6A3FD0", "#0F7A66", "#C2570C"]
FEATURE_TARGETS = [("Assess", "Start the assessment"), ("Why This Result?", "See my explanation"),
                   ("Behavioural Insights", "Open my insights"), ("Intervention", "Open my intervention")]
GRADIENTS = ["linear-gradient(135deg,#EDF5FF,#DCEBFF)", "linear-gradient(135deg,#F5EFFF,#E8DEFF)",
             "linear-gradient(135deg,#E9FAF2,#D5F3E5)", "linear-gradient(135deg,#FFF3E8,#FFE2CC)"]


def feature_details():
    return [
        {
            "tagline": "A Random Forest regression model turns your answers into an estimated overreliance score from 1 to 5.",
            "does": "Estimates how your self-reported habits relate to Generative AI overreliance, based on patterns in 151 student questionnaires.",
            "how": "Your 24 answers (5 profile questions and 19 Likert statements) become 9 model features: four construct averages and five encoded profile answers. The saved model is loaded, never retrained.",
            "careful": f"In nested cross-validation the average error was about {NESTED_CV['MAE']:.2f} points (R² {NESTED_CV['R2']:.2f}). This is a moderate, internal estimate; an individual result can be off by more, and it is not a diagnosis.",
            "see": ["A gauge with your estimated score out of 5", "Your four learning-habit scores with charts", "A plain-language reading of the result and its limits"],
            "extra": "",
        },
        {
            "tagline": "SHAP shows which of your answers moved the estimate up or down.",
            "does": "Splits your prediction into one contribution per model feature, measured against the model's baseline (its average output).",
            "how": "SHAP TreeExplainer values from the saved Random Forest add up so that baseline plus contributions equals your score. The app checks this on every explanation.",
            "careful": "These are influential predictors inside the model, not causes. Across the training data the largest average influence came from independent learning, followed by metacognition and study year.",
            "see": ["Features that raised and lowered your estimate", "A signed bar chart of all nine contributions", "A technical table and the additivity check for researchers"],
            "extra": "",
        },
        {
            "tagline": "A summary of your self-reported learning behaviour across four dimensions.",
            "does": "Shows your independent learning, verification, metacognition and learning-benefit scores side by side.",
            "how": "Each score is the average of your answers in that section on a 1\u20135 scale. An exploratory K-Means grouping (K = 2) shows which group of students your answers resemble most.",
            "careful": "The grouping is exploratory with moderate separation (silhouette 0.38). It is not a diagnosis or a student personality type.",
            "see": ["Four construct scores with a radar chart", "Comparison with the two exploratory K-Means groups", "A note on what the grouping can and cannot say"],
            "extra": "",
        },
        {
            "tagline": "Rule-based learning support matched to your four construct scores.",
            "does": "Flags any construct below the neutral midpoint of 3.0 for targeted support, gives a maintenance suggestion for the others, and guides you through an interactive activity.",
            "how": "The rules come from the research notebook. Each activity asks you to attempt a task independently, compare with an AI or trusted reference, find errors, and reflect.",
            "careful": "The midpoint of 3.0 is a heuristic, not a validated cut-off. Completing an activity does not show that learning improved; effectiveness has not been experimentally validated.",
            "see": ["Your construct status table", "A task to attempt independently", "Spaces for comparison, error-finding and reflection with a progress bar"],
            "extra": "",
        },
    ]


def page_feature():
    idx = int(st.session_state.get("feature_idx", 0)) % len(FEATURES)
    title, _desc, _page, bg, icon = FEATURES[idx]
    d = feature_details()[idx]
    st.button("Back to Home", icon=":material/arrow_back:", on_click=goto, args=("Home",), key="feat_back")
    md_html(
        f'<div class="feat-hero" style="background:{GRADIENTS[idx]}"><div class="feat-ic" style="background:{bg}">{icon}</div>'
        f'<div><div class="eyebrow">Feature {idx + 1} of {len(FEATURES)}</div><h2>{esc(title)}</h2><p>{esc(d["tagline"])}</p></div></div>'
    )
    md_html('<div class="grid g3">' + card("What it does", esc(d["does"])) + card("How it works", esc(d["how"]))
            + card("Keep in mind", esc(d["careful"])) + "</div>")
    st.write("")
    md_html('<div class="card"><h4>What you will see</h4><ul class="feat-list">'
            + "".join(f"<li>{esc(x)}</li>" for x in d["see"]) + "</ul></div>")
    st.write("")
    target, label = FEATURE_TARGETS[idx]
    c1, c2, _ = st.columns([1.2, 1, 2])
    with c1:
        if idx > 0 and st.session_state.get("result") is None:
            st.button("Take the assessment first", icon=":material/assignment:", type="primary",
                      on_click=goto, args=("Assess",), key="feat_try")
        else:
            st.button(label, type="primary", on_click=goto, args=(target,), key="feat_try")
    with c2:
        st.button("Explore model results" if idx == 0 else "Back to Home", on_click=goto,
                  args=("Model Insights" if idx == 0 else "Home",), key="feat_more")