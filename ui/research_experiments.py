"""ui/research_experiments.py - the dedicated Research & Experiments page (10 sections).

One final research modelling dataset (249 responses) is presented. Every experiment shown (Random Forest, eight-model
comparison, Deep Learning, K-Means, SHAP, noise) was run on it. The IEEE DataPort publication (250 rows) is supporting evidence.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from backend import research_data as R
from ui import charts
from ui.model_insights import (_pm, evidence, tab_ctgan, tab_deep_learning, tab_deployed, tab_interventions, tab_kmeans,
                               tab_models, tab_noise, tab_predictions, tab_shap, table)
from ui.research_graphs import tab_graphs
from ui.research import FUTURE, LIMITATIONS, tab_constructs, tab_correlations, tab_dataset, tab_direct, tab_reliability, tab_sdg
from ui.theme import card, esc, md_html, notice, section_title

BASE_DIR = Path(__file__).resolve().parent.parent
ARCH_IMAGE = BASE_DIR / "assets" / "research_architecture.png"
IEEE_URL = "https://ieee-dataport.org/documents/generative-ai-usage-overreliance-and-learning-behaviour-among-students-questionnaire"
IEEE_DOI = "10.21227/sf15-b979"


def dataset_banner() -> None:
    md_html('<div class="card" style="display:flex;gap:22px;align-items:center;flex-wrap:wrap">'
            '<div style="font-size:3rem;font-weight:800;line-height:1;color:#1E4FD8">249</div>'
            '<div style="flex:1;min-width:240px"><div style="font-weight:700;font-size:1.1rem;color:#0F2A5C">Final Research Modelling Dataset</div>'
            '<div>Anonymised, consented and usable student responses used for the final modelling experiments.</div></div></div>')
    st.caption("Dataset published on IEEE DataPort: 250 anonymised responses and 42 questionnaire columns. The final modelling experiments use 249 usable responses.")
    st.link_button("View dataset on IEEE DataPort", IEEE_URL, icon=":material/open_in_new:")
    st.write("")


def sub(title: str) -> None:
    st.write("")
    st.markdown(f"#### {title}")


def four_dimensions() -> None:
    st.markdown("**Four learning dimensions used as model inputs**")
    table(["#", "Dimension", "Role", "Questionnaire items", "Used by the Random Forest?"], [
        (1, "Independent Learning", "Predictor construct", "Q19\u2013Q23", "Yes, as a mean"),
        (2, "Verification", "Predictor construct", "Q24\u2013Q28", "Yes, as a mean"),
        (3, "Metacognition", "Predictor construct", "Q29\u2013Q33", "Yes, as a mean"),
        (4, "Learning Benefits", "Predictor construct", "Q34, Q35, Q37, Q39", "Yes, as a mean"),
    ])
    st.caption("The overreliance target (mean of Q12\u2013Q18) is the quantity the model learns to estimate. It is not one of the model inputs.")


def sec_overview() -> None:
    md_html('<div class="grid g2">'
            + card("Research motivation", "Generative AI tools are now part of everyday study. Used well they support learning; used uncritically they may replace independent reasoning and verification. "
                   "Cognivue AI studies how self-reported usage patterns and learning behaviours relate to a questionnaire-based overreliance score.")
            + card("Research question", "Can a student's reported independent learning, verification, metacognition, learning benefits and basic profile predict a questionnaire-based overreliance score, and can the estimate be explained and turned into supportive learning activities?")
            + "</div>")
    st.write("")
    md_html('<div class="grid g2">'
            + card("Training target", "The <b>Overreliance Target Score</b> is the mean of seven direct overreliance statements (Q12\u2013Q18, scale 1\u20135) answered by the research respondents: <code>overreliance_score = mean(Q12\u2026Q18)</code>.")
            + card("Model inputs", "The Random Forest uses <b>nine features</b>: four construct means (Independent Learning, Verification, Metacognition, Learning Benefits) and five profile variables (usage frequency, usage duration, age group, study year, prior GenAI experience). "
                   "Q12\u2013Q18 are used only to build the target and are excluded from the inputs to prevent target leakage.")
            + card("In the app", "A student answers 31 questions. The profile and learning-habit answers feed the trained model. The seven additional statements at the end are collected as an extra questionnaire section and are not used by the prediction, SHAP or K-Means.")
            + card("Why the target is not an input", "Feeding the target statements to the model would let it read the answer it is meant to estimate (target leakage). Keeping them out means the predicted score is a genuine estimate from learning habits and usage patterns.")
            + "</div>")
    st.write("")
    four_dimensions()
    sub("Relevance to SDG 4: Quality Education")
    tab_sdg()


def sec_dataset() -> None:
    evidence("Final research modelling dataset: 249 responses")
    md_html('<div class="grid g2">'
            + card("Published IEEE DataPort dataset", "<b>Generative AI Usage, Overreliance, and Learning Behaviour Among Students: A Questionnaire-Based Dataset</b><br>"
                   f"250 anonymised responses \u00b7 42 questionnaire columns \u00b7 CSV/XLSX \u00b7 Creative Commons Attribution \u00b7 DOI {IEEE_DOI}")
            + card("Final 249-response modelling sample", "The 249 usable responses are those with consent and a profile that the existing encoders can handle. One response whose age category (\u201cPrefer not to say\u201d) could not be encoded was excluded. "
                   "All modelling in this section uses these 249 responses.")
            + card("Questionnaire structure", "Profile and Generative AI usage questions, Likert statements (1 = Strongly Disagree to 5 = Strongly Agree) and open-ended questions that are kept outside the modelling. "
                   "The Likert statements are grouped into the four predictor constructs and the seven direct overreliance items.")
            + card("How the questions map to the model", "<b>Four predictor constructs</b> (Independent Learning, Verification, Metacognition, Learning Benefits), <b>five profile variables</b> (usage frequency, usage duration, age group, study year, prior GenAI experience) "
                   "make the <b>nine Random Forest features</b>. The <b>seven direct overreliance items</b> (Q12\u2013Q18) form the target and are never inputs.")
            + "</div>")
    st.link_button("View Dataset on IEEE DataPort", IEEE_URL, icon=":material/open_in_new:", type="primary")
    st.write("")
    notice("The survey-platform collection record (274 submissions, 249 consented responses, 45 columns) is a different record from the published IEEE DataPort file (250 rows, 42 columns); the two have not been reconciled row by row, so they should not be described as identical.", "info")
    st.write("")
    four_dimensions()
    st.write("")
    tab_dataset()
    sub("Questionnaire constructs")
    tab_constructs()
    sub("Direct overreliance indicators (training target)")
    tab_direct()
    sub("Reliability (Cronbach’s alpha)")
    tab_reliability()
    sub("Correlations")
    tab_correlations()


def sec_architecture() -> None:
    if ARCH_IMAGE.exists():
        st.image(str(ARCH_IMAGE), caption="Cognivue AI system architecture and research workflow", width="stretch")
    else:
        md_html('<div style="border:2px dashed #94A3B8;border-radius:14px;padding:56px 24px;text-align:center;background:#F8FAFC">'
                '<div style="font-size:1.1rem;font-weight:700;color:#334155">Research architecture diagram</div>'
                '<div style="color:#64748B;margin-top:6px">The architecture diagram is not available in this deployment.</div></div>')
    st.write("")
    st.markdown("**How the pipeline fits together**")
    table(["#", "Stage", "What happens", "Dataset"], [
        (1, "Questionnaire data collection", "Survey responses collected (274 submissions, 249 consented); published as 250 anonymised responses", "249"),
        (2, "Cleaning and preprocessing", "Consent-based inclusion, identifiers removed, Likert 1\u20135 coding, open-ended answers kept outside modelling", "249"),
        (3, "Four construct calculations", "Means of the items for Independent Learning, Verification, Metacognition and Learning Benefits", "249"),
        (4, "Five profile encodings", "Usage frequency, usage duration, age group, study year, prior GenAI experience (existing ordinal mappings)", "249"),
        (5, "Nine-feature engineering", "4 construct scores + 5 profile features in a fixed order. Q12\u2013Q18 excluded from inputs", "249"),
        (6, "Random Forest regression", "Trained on the nine features to predict the Overreliance Target Score = mean(Q12\u2013Q18)", "249"),
        (7, "Predicted overreliance score", "Continuous 1\u20135 estimate for a new student", "249"),
        (8, "SHAP explainability", "Global and per-student feature contributions; not causal", "249"),
        (9, "K-Means behavioural profiling", "Separate exploratory component; not an input to the Random Forest", "249"),
        (10, "Rule-based adaptive recommendations", "3.0 midpoint heuristic on the four construct scores", "249"),
        (11, "Streamlit application", "Assessment, results, SHAP, profile, activities, PDF report", "n/a"),
    ])
    st.write("")
    notice("<b>Training target vs model inputs.</b> The target is the mean of Q12\u2013Q18. The nine model inputs come from the other questions. The Deep Learning comparison is a research experiment and is not part of the deployed prediction pipeline.", "info")


def sec_models() -> None:
    evidence("Final research modelling dataset: 249 responses")
    sub("Eight-model comparison")
    tab_models()
    sub("Consolidated results table")
    rows = [("Eight-model comparison", m, "249", "Repeated 5-fold × 5", _pm(a, sa), _pm(b, sb), _pm(c, sc)) for m, a, sa, b, sb, c, sc in R.MODEL_COMPARISON]
    rows += [("Final tuned model", m, "249", "Repeated 5-fold × 3", _pm(a, sa), _pm(b, sb), _pm(c, sc)) for m, a, b, c, sa, sb, sc in R.REPEATED_CV]
    n = R.NESTED_CV
    rows.append(("Final tuned model", "Random Forest", "249", "Nested CV (5×3 outer)", f"{n['MAE']:.4f}", f"{n['RMSE']:.4f}", f"{n['R2']:.4f}"))
    rows += [("Deep Learning experiment", m if m != "Random Forest" else "Random Forest (DL experiment folds)", "249", "Repeated 5-fold × 3", _pm(a, sa), _pm(b, sb), _pm(c, sc))
             for m, a, sa, b, sb, c, sc in R.DEEP_LEARNING]
    table(["Experiment", "Model", "Dataset", "Evaluation", "MAE", "RMSE", "R²"], rows)
    notice("All rows use the 249-response dataset, but different experiments use different fold designs, so compare models within an experiment rather than across experiments.", "warn")
    sub("Final deployed Random Forest")
    tab_deployed()
    sub("Out-of-fold predictions and residuals")
    tab_predictions()


def sec_findings() -> None:
    n = R.NESTED_CV
    md_html('<div class="grid g2">'
            + card("Predictive performance", f"On 249 respondents the Random Forest reached nested-CV MAE {n['MAE']:.3f} and R² {n['R2']:.3f}: about {R.RF_IMPROVEMENT_PERCENT:.1f}% lower MAE than a mean baseline, with moderate explained variance.")
            + card("Model choice", "Gradient Boosting, Random Forest and SVR were practically tied on MAE. The Random Forest was kept because it suits small tabular data and integrates with SHAP explanations.")
            + card("Drivers of the estimate", "SHAP ranks independent learning (39.98%) and verification (17.53%) highest; study year (13.80%) is third. Correlations agree in direction: independent learning ρ − 0.349, verification ρ − 0.334.")
            + card("Experiments", "On the same 249 responses the Deep Learning network (MAE 0.576, R² 0.078) did not beat the Random Forest (MAE 0.533, R² 0.197). Noise degrades performance gradually at higher levels.")
            + "</div>")
    sub("Intervention coverage")
    tab_interventions()
    sub("Limitations")
    md_html('<div class="card"><p>' + "<br>".join(f"{i}. {esc(t)}" for i, t in enumerate(LIMITATIONS, 1)) + "</p></div>")
    sub("Future work")
    md_html('<div class="card"><p>' + "<br>".join(f"{i}. {esc(t)}" for i, t in enumerate(FUTURE, 1)) + "</p></div>")
    st.write("")
    notice("Cognivue AI is a research prototype built from a class project. Scores are questionnaire-based estimates for reflection, not a diagnosis or a measure of academic ability.", "warn")


def page_research_experiments() -> None:
    section_title("Research & Experiments", "Dataset, methods, model comparison and experiments behind Cognivue AI. All results use the final 249-response modelling dataset.")
    dataset_banner()
    names = ["1 Overview & SDG 4", "2 Dataset", "3 Architecture", "4 Model Comparison", "5 Deep Learning", "6 K-Means", "7 SHAP Explainability",
             "8 Noise Robustness", "9 CTGAN Experiment", "10 Findings & Limitations", "11 Graphs & Visual Results"]
    fns = [sec_overview, sec_dataset, sec_architecture, sec_models, tab_deep_learning, tab_kmeans, tab_shap, tab_noise, tab_ctgan, sec_findings, tab_graphs]
    for tab, fn in zip(st.tabs(names), fns):
        with tab:
            try:
                fn()
            except Exception:
                notice("This section could not be displayed. Check that the models folder is present and the app starts without errors.", "warn")
