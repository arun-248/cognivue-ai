"""ui/research.py - methodology, constructs, statistics, limitations and SDG 4."""

from __future__ import annotations

import streamlit as st

from backend import research_data as R
from backend.interventions import CONSTRUCT_RULES, NEUTRAL_MIDPOINT
from backend.questionnaire import FEATURE_ORDER, LIKERT_LABELS, PROFILE_QUESTIONS
from ui.home import arch_html
from ui.model_insights import table
from ui.theme import card, esc, md_html, notice, section_title, stat


def tab_architecture():
    md_html(arch_html())
    st.write("")
    notice("The questionnaire study is a single dataset: 151 consented student responses. The supervised pipeline predicts the overreliance score; K-Means, "
           "the Deep Learning model, the noise experiment and the CTGAN experiment are separate research components and are not part of the live prediction.", "info")


def tab_dataset():
    d = R.DATASET
    md_html('<div class="grid g4">'
            + stat(f'{d["original_rows"]} \u00d7 {d["original_columns"]}', "Original dataset", "rows \u00d7 columns")
            + stat(str(d["consented"]), "Consented respondents", "used for modelling", "#109A8A")
            + stat(str(d["not_consented"]), "Not consented", "excluded", "#D97706")
            + stat(str(d["features"]), "Model input features", "9 columns, fixed order") + "</div>")
    st.write("")
    md_html('<div class="grid g2">'
            + card("What was used", "Only the 151 consented responses were used for the main quantitative modelling. They had complete responses. Timestamp and email were excluded. "
                   "Open-ended answers (Q40\u2013Q42) were kept separate from the quantitative modelling. No completely duplicated full records were identified.")
            + card("Questionnaire structure", "Demographic questions, Generative AI usage questions, Likert statements and open-ended questions. Multi-select questions Q6, Q9 and Q11 were "
                   "multi-hot encoded. Contradictory selections (for example a specific tool and \u201cnot used\u201d) were preserved rather than silently corrected.")
            + "</div>")


def tab_preprocessing():
    rows = [(i, l) for i, l in enumerate(LIKERT_LABELS, 1)]
    table(["Code", "Likert response"], rows)
    st.write("")
    for q in PROFILE_QUESTIONS:
        md_html(f'<div class="card" style="margin-bottom:10px"><h4>{esc(q["text"])}</h4><p>'
                + " \u00b7 ".join(f"{esc(label)} = {code}" for label, code in q["options"]) + "</p></div>")
    notice("These ordinal mappings are implemented exactly as used in the Colab preprocessing, and the app's tests compare them with the saved preprocessing metadata. "
           "The form also offered \u201cPrefer not to say\u201d for age, which has no encoding in the trained model, so it is not offered in this app.", "info")


def tab_constructs():
    table(["Construct", "Questionnaire items", "Meaning"], R.CONSTRUCT_TABLE)
    st.write("")
    notice("<b>Leakage prevention.</b> The overreliance target is the mean of Q12\u2013Q18 (range 1\u20135). Those seven items are never collected as predictors. The app collects 24 answers: "
           "5 profile questions plus 19 Likert statements (5 independent learning, 5 verification, 5 metacognition, 4 learning benefits). The two Q22 questions have different wording "
           "and were treated as separate items. Q36 and Q38 were kept separate because their direction and relationship to the positive learning-benefit construct were not suitable for combining.", "info")
    st.write("")
    md_html(card("The nine model features, in order", " \u2192 ".join(esc(f) for f in FEATURE_ORDER)))


def tab_reliability():
    table(["Construct", "Cronbach's alpha"], [(n, f"{a:.4f}") for n, a in R.RELIABILITY])
    st.write("")
    notice("The first five scales show good internal consistency. The six-item positive/negative outcome scale had a very low alpha (0.2269), which is why Q36 and Q38 were kept "
           "separate from the positive learning-benefit construct.", "info")


def tab_correlations():
    table(["Relationship", "Spearman \u03c1", "p-value"], [(a, f"{b:+.4f}", c) for a, b, c in R.SPEARMAN])
    st.write("")
    notice("Higher self-reported overreliance was associated with lower independent learning, verification and metacognition scores in this sample. The association with learning benefits was not statistically "
           "significant, and usage frequency and duration alone were not significant indicators. These are correlations, <b>not causal effects</b>.", "warn")


def tab_model():
    p = R.RF_PARAMETERS
    n = R.NESTED_CV
    md_html('<div class="grid g2">'
            + card("Model", "A tuned RandomForestRegressor, selected after comparing eight regression models. It is loaded from a saved file and never retrained in the app.")
            + card("Parameters", ", ".join(f"{k} = {v}" for k, v in p.items()))
            + card("Validation", f"Nested cross-validation: MAE {n['MAE']:.4f}, RMSE {n['RMSE']:.4f}, R\u00b2 {n['R2']:.4f}. Repeated 5-fold (3\u00d7): the Random Forest beat the mean and median baselines "
                   f"(MAE reduced by about {R.RF_IMPROVEMENT_PERCENT:.2f}%).")
            + card("Honest reading", "Performance is moderate. There is no external validation, and the model should not be used for high-stakes decisions about students.")
            + "</div>")
    st.write("")
    notice("Charts and full tables are on the Model Insights page.", "info")


def tab_xai():
    md_html('<div class="grid g2">'
            + card("Method", "SHAP TreeExplainer on the saved Random Forest. Values are additive: baseline + sum of SHAP values reconstructs the model output (maximum error 0.0 in the Colab experiment; the app re-checks every explanation).")
            + card("Global ranking", "Independent learning (32.7%), metacognition (16.1%), study year (15.1%), verification (14.2%), learning benefits (7.3%), then usage frequency, usage duration, experience and age.")
            + card("Reading SHAP", "A positive value pushes the model's estimate higher and a negative value pushes it lower, relative to the baseline.")
            + card("Not causation", "SHAP identifies influential predictors in the fitted model. Correlated predictors can share attribution, and the results do not show that any factor causes overreliance.")
            + "</div>")


def tab_interventions():
    rows = [(r["name"], f"{r['priority']}", esc(r["below_midpoint"])) for r in CONSTRUCT_RULES.values()]
    table(["Construct", "Focus", "Recommendation when below 3.0"], rows)
    st.write("")
    notice(f"A construct score below the neutral midpoint ({NEUTRAL_MIDPOINT:.1f}) triggers a support recommendation; otherwise a maintenance recommendation is shown. The midpoint is a heuristic design choice. "
           "The app adds an interactive activity (attempt independently, compare with a reference, find errors, reflect). Completing it does not show improved learning.", "warn")


def tab_experiments():
    md_html('<div class="grid g2">'
            + card("Deep Learning comparison", f"{R.DL_ARCHITECTURE}. MAE 0.7327 vs Random Forest 0.4904; R\u00b2 \u22120.4999 vs 0.3681. The Random Forest performed better; the neural network is not deployed.")
            + card("K-Means profiling", "Six features, K = 2 (silhouette 0.3848), clusters of 120 and 31 respondents. Exploratory only.")
            + card("Noise robustness", "Stable at 0\u20135% noise (R\u00b2 0.399 \u2192 0.399), degrading at 30% (R\u00b2 0.223).")
            + card("CTGAN augmentation", "Synthetic data increased MAE by about 7.4% and did not improve the model; the real-data-only Random Forest is final.")
            + "</div>")
    st.write("")
    notice("Details, tables and charts are on the Model Insights page.", "info")


LIMITATIONS = [
    "The data are self-reported questionnaire answers from 151 consented respondents; the app does not analyse real AI prompts, conversations or usage logs.",
    "The score is an estimate, not a diagnosis, and does not show that AI causes cognitive decline.",
    "Predictive performance is moderate (nested CV R\u00b2 about 0.35, MAE about 0.50) and there has been no external validation on an independent student population.",
    "SHAP and correlations describe the fitted model and this sample; they do not establish causation.",
    "The K-Means grouping is exploratory with moderate separation (silhouette 0.38) and is not a validated student typology.",
    "The Deep Learning model underperformed the Random Forest, and CTGAN augmentation did not improve it.",
    "Performance degrades at higher input-noise levels, and Gaussian noise does not represent all real-world errors.",
    "The intervention rules use a heuristic midpoint of 3.0 and their effectiveness has not been experimentally validated.",
    "One questionnaire dataset from one institution was used, so results may not generalise.",
]
FUTURE = [
    "Validate the model on an independent, larger and more diverse student sample.",
    "Run a longitudinal or controlled study to test whether the adaptive activities change verification and independent-reasoning behaviour.",
    "Examine optimal thresholds for the intervention rules instead of the heuristic midpoint.",
    "Add richer, consented behavioural measures alongside self-report, with clear privacy safeguards.",
    "Study fairness and robustness across programmes, years of study and prior AI experience.",
]


def tab_sdg():
    md_html('<div class="grid g2">'
            + card("SDG 4: Quality Education", "Sustainable Development Goal 4 aims for inclusive and equitable quality education and lifelong learning. Generative AI can support learning, "
                   "but uncritical dependence may weaken independent reasoning and verification.")
            + card("Intended contribution", "A prototype that estimates overreliance from self-reported habits, explains the estimate, and suggests activities that encourage verification, critical thinking and independent reasoning.")
            + card("How the prototype aligns", "Responsible AI-assisted learning, personalised support through rule-based interventions, and transparency through SHAP explanations and stated limitations.")
            + card("What is not claimed", "This is an intended contribution, not proven impact. Longitudinal studies are needed to show whether the interventions improve learning or reduce overreliance.")
            + "</div>")


def page_research():
    section_title("Research", "Methodology, statistics, experiments and honest limitations of the framework.")
    names = ["Architecture", "Dataset", "Preprocessing", "Constructs", "Reliability", "Correlations", "Predictive model",
             "Explainable AI", "Interventions", "Experiments", "Limitations", "Future work", "SDG 4"]
    tabs = st.tabs(names)
    fns = [tab_architecture, tab_dataset, tab_preprocessing, tab_constructs, tab_reliability, tab_correlations, tab_model,
           tab_xai, tab_interventions, tab_experiments,
           lambda: md_html('<div class="card"><h4>Limitations</h4><p>' + "<br>".join(f"{i}. {esc(t)}" for i, t in enumerate(LIMITATIONS, 1)) + "</p></div>"),
           lambda: md_html('<div class="card"><h4>Future work</h4><p>' + "<br>".join(f"{i}. {esc(t)}" for i, t in enumerate(FUTURE, 1)) + "</p></div>"),
           tab_sdg]
    for tab, fn in zip(tabs, fns):
        with tab:
            fn()