"""ui/explain.py - individual SHAP explanation, plus global importance kept clearly separate."""

from __future__ import annotations

import streamlit as st

from backend.explainability import explain_prediction
from backend.questionnaire import PROFILE_QUESTIONS
from backend.research_data import SHAP_GLOBAL
from ui import charts
from ui.resources import get_cached_explainer, get_models
from ui.state import goto, logger
from ui.theme import C_AMBER, C_BLUE, C_CYAN, C_PURPLE, chart_card, esc, md_html, notice, section_title, stat

CODE_TO_LABEL = {q["feature"]: {code: label for label, code in q["options"]} for q in PROFILE_QUESTIONS}


def value_text(feature: str, value: float) -> str:
    if feature in CODE_TO_LABEL:
        return CODE_TO_LABEL[feature].get(int(round(value)), str(value))
    return f"{value:.2f} out of 5"


def plain_sentence(row) -> str:
    direction = "higher" if row.shap > 0 else "lower"
    return (f"Your answer for \u201c{esc(row.label)}\u201d ({esc(value_text(row.feature, row.value))}) pushed the model's estimate "
            f"{direction} by {abs(row.shap):.2f} relative to its baseline.")


def page_explain():
    result = st.session_state.get("result")
    section_title("Why did the model produce this result?",
                  "Part 1 explains your own estimate. Part 2 shows what matters on average across the study respondents. They answer different questions.")
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment first. This page will then explain your result.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_explain")
        _global_section()
        return

    if result["shap"] is None:
        try:
            with st.spinner("Generating your explanation\u2026"):
                models = get_models()
                result["shap"] = explain_prediction(models["random_forest"], result["frame"], get_cached_explainer())
        except Exception:
            logger.exception("SHAP explanation failed")
            result["shap"] = False
    exp = result["shap"]
    if exp is False:
        notice("Something went wrong while generating the explanation. Your estimate is still available on the Results page.", "warn")
        st.button("Back to results", on_click=goto, args=("Results",), key="why_back")
        _global_section()
        return

    table = exp["contributions"]
    score = result["prediction"]["raw_prediction"]

    md_html('<div class="eyebrow">Part 1 \u00b7 Your individual explanation</div>')
    md_html(
        '<div class="grid g3">'
        + stat(f"{score:.2f}", "Predicted score", "your estimate", C_CYAN)
        + stat(f"{exp['baseline']:.2f}", "Baseline", "the model's average output on the training data", C_BLUE)
        + stat(f"{score - exp['baseline']:+.2f}", "Difference from baseline", "sum of all nine contributions", C_PURPLE)
        + "</div>"
    )
    st.write("")
    if exp["verified"]:
        notice(f"<b>Additivity check passed.</b> Baseline {exp['baseline']:.4f} + sum of contributions "
               f"{table['shap'].sum():+.4f} = {exp['reconstructed']:.4f}, which matches the model output {exp['model_output']:.4f} "
               f"(difference {exp['reconstruction_error']:.1e}).", "ok")
    else:
        notice("<b>The explanation could not be verified.</b> Baseline plus the contributions does not reproduce the model output "
               f"within tolerance (difference {exp['reconstruction_error']:.4f}). Do not rely on this explanation.", "warn")

    with st.expander("How to read this in simple words", expanded=False):
        st.markdown(
            "1. The model starts from a **baseline**: its average estimate across the students it learned from.\n"
            "2. Each of your nine inputs then nudges the estimate **up** (amber) or **down** (cyan) from that baseline.\n"
            "3. Adding the baseline and all nudges gives **your estimate**.\n\n"
            "A nudge describes how the *model* used that input for answers like yours. It does **not** mean that input causes anyone to rely on AI."
        )
    st.write("")

    inc = table[table["shap"] > 0].sort_values("shap", ascending=False).head(4)
    dec = table[table["shap"] < 0].sort_values("shap").head(4)

    def factor_html(frame, color):
        if frame.empty:
            return "<p>No answers pushed the estimate in this direction.</p>"
        out = []
        for row in frame.itertuples():
            out.append(
                f'<div class="factor"><div class="dot" style="background:{color}"></div><div>'
                f'<div class="ft">{esc(row.label)} <span style="color:{color}">({row.shap:+.3f})</span></div>'
                f'<div class="fd">{plain_sentence(row)}</div></div></div>'
            )
        return "".join(out)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        md_html(f'<div class="card"><h4 style="color:#B45309">\u25b2 Answers that raised the estimate</h4>{factor_html(inc, C_AMBER)}</div>')
    with c2:
        md_html(f'<div class="card"><h4 style="color:#0B6B5F">\u25bc Answers that lowered the estimate</h4>{factor_html(dec, C_CYAN)}</div>')

    st.write("")
    with chart_card("Step by step: from the baseline to your estimate"):
        ordered = table.sort_values("abs_shap", ascending=False)
        charts.show(charts.waterfall(exp["baseline"], list(zip(ordered["label"], ordered["shap"])), exp["model_output"]), "why_waterfall")
        st.caption("Starting at the baseline, each bar adds or subtracts that feature's contribution (amber raises, cyan lowers) until it reaches your estimate.")
    with chart_card("Which of the nine features influenced this estimate most?"):
        ordered = table.sort_values("abs_shap", ascending=False)
        charts.show(charts.signed_bars(list(ordered["label"]), [float(v) for v in ordered["shap"]]), "why_signed")
        st.caption("Amber bars push the estimate higher; cyan bars push it lower. Values are in score points on the 1\u20135 scale.")

    with st.expander("Technical SHAP explanation (for researchers)"):
        st.markdown(
            "SHAP values come from `shap.TreeExplainer` on the saved `RandomForestRegressor` and are additive: "
            "**baseline + \u03a3 SHAP = model output**. Positive values push the output higher and negative values push it lower "
            "relative to the baseline. Correlated predictors can share attribution, and the explanation describes the fitted model, not causation."
        )
        st.markdown(f"Baseline **{exp['baseline']:.6f}** + \u03a3 SHAP **{table['shap'].sum():+.6f}** = **{exp['reconstructed']:.6f}**; "
                    f"model output **{exp['model_output']:.6f}**; reconstruction error **{exp['reconstruction_error']:.2e}**.")
        rows = "".join(
            f"<tr><td>{esc(r.feature)}</td><td>{esc(value_text(r.feature, r.value))}</td><td>{r.shap:+.5f}</td><td>{esc(r.direction)}</td></tr>"
            for r in table.itertuples()
        )
        md_html(f'<table class="rtable"><tr><th>Model feature</th><th>Your value</th><th>SHAP</th><th>Effect</th></tr>{rows}</table>')

    st.write("")
    _global_section()
    st.write("")
    st.button("Continue to my activities", type="primary", on_click=goto, args=("Intervention",), key="why_iv")


def _global_section():
    st.write("")
    md_html('<div class="eyebrow">Part 2 \u00b7 Global feature importance (all study respondents)</div>')
    md_html('<div class="card"><h4>What matters most on average?</h4><p>This ranking is <b>not about you</b>. It is the average size of each feature\'s '
            'SHAP contribution across the 151 respondents the model was trained on, so it describes the fitted model in general. Your individual explanation above can '
            'differ from this ranking.</p></div>')
    st.write("")
    with chart_card("Which features influence the model most, on average? (mean |SHAP|, training data)"):
        labels = [n for n, _, _ in SHAP_GLOBAL]
        charts.show(charts.hbar(labels, [v for _, v, _ in SHAP_GLOBAL], [C_PURPLE] * len(labels), "Mean absolute SHAP value", fmt="{:.3f}"), "why_global")
        st.caption("Independent learning had the largest average influence (32.7%), followed by metacognition (16.1%), study year (15.1%) and verification (14.2%).")
    notice("Global importance describes the fitted model on its training data. It is descriptive, not independent validation, and it is "
           "<b>not proof of causation</b>: a feature can be influential for prediction without causing the outcome.", "info")
