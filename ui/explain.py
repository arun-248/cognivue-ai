"""ui/explain.py - individual SHAP explanation."""

from __future__ import annotations

import numpy as np
import streamlit as st

from backend.explainability import FEATURE_LABELS, explain_prediction
from backend.questionnaire import PROFILE_QUESTIONS
from ui.resources import get_cached_explainer, get_models
from ui.state import goto, logger
from ui.theme import (C_AMBER, C_BLUE, C_CARD, C_CYAN, C_MUTED, C_PURPLE, C_TEXT, chart_card, esc,
                      md_html, notice, section_title, show_fig, stat, themed_fig)
from matplotlib.patches import Patch

CODE_TO_LABEL = {q["feature"]: {code: label for label, code in q["options"]} for q in PROFILE_QUESTIONS}


def value_text(feature: str, value: float) -> str:
    if feature in CODE_TO_LABEL:
        return CODE_TO_LABEL[feature].get(int(round(value)), str(value))
    return f"{value:.2f} out of 5"


def plain_sentence(row) -> str:
    direction = "higher" if row.shap > 0 else "lower"
    return (f"Your answer for \u201c{esc(row.label)}\u201d ({esc(value_text(row.feature, row.value))}) pushed the model's estimate "
            f"{direction} by {abs(row.shap):.2f} relative to its baseline.")


def shap_bar_chart(table) -> None:
    top = table.sort_values("shap")
    fig, ax = themed_fig(8, 0.46 * len(top) + 1.5)
    colors = [C_AMBER if v > 0 else C_CYAN for v in top["shap"]]
    ax.barh(top["label"], top["shap"], color=colors, height=0.62)
    ax.axvline(0, color=C_MUTED, linewidth=1)
    ax.grid(axis="y", visible=False)
    span = max(float(top["shap"].abs().max()), 1e-6)
    for y, v in enumerate(top["shap"]):
        ax.text(v + (0.03 * span if v >= 0 else -0.03 * span), y, f"{v:+.3f}", va="center",
                ha="left" if v >= 0 else "right", color=C_TEXT, fontsize=8.5)
    ax.set_xlim(-span * 1.4, span * 1.4)
    ax.set_xlabel("Contribution to the estimate  (\u2190 lowers | raises \u2192)")
    ax.set_title("Which answers moved your estimate?", fontsize=11, loc="left", fontweight="bold")
    ax.legend(handles=[Patch(color=C_AMBER, label="Pushes estimate higher"), Patch(color=C_CYAN, label="Pushes estimate lower")],
              loc="lower right", facecolor=C_CARD, edgecolor="#C8D9F0", labelcolor=C_TEXT, fontsize=8)
    show_fig(fig)


def page_explain():
    result = st.session_state.get("result")
    section_title("Why did the model produce this result?",
                  "Each bar shows how much one answer moved your estimate away from the model's baseline.")
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment first. This page will then explain your result.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_explain")
        return

    if result["shap"] is None:
        try:
            with st.spinner("Generating explanation\u2026"):
                models = get_models()
                result["shap"] = explain_prediction(models["random_forest"], result["frame"], get_cached_explainer())
        except Exception:
            logger.exception("SHAP explanation failed")
            result["shap"] = False
    exp = result["shap"]
    if exp is False:
        notice("Something went wrong while generating the explanation. Your estimate is still available on the Results page.", "warn")
        st.button("Back to results", on_click=goto, args=("Results",), key="why_back")
        return

    table = exp["contributions"]
    score = result["prediction"]["raw_prediction"]
    md_html(
        '<div class="grid g3">'
        + stat(f"{score:.2f}", "Predicted score", "your estimate", C_CYAN)
        + stat(f"{exp['baseline']:.2f}", "Baseline", "the model's average output", C_BLUE)
        + stat(f"{score - exp['baseline']:+.2f}", "Difference from baseline", "sum of all contributions", C_PURPLE)
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
        md_html(f'<div class="card"><h4 style="color:{C_AMBER}">\u25b2 Answers that raised the estimate</h4>{factor_html(inc, C_AMBER)}</div>')
    with c2:
        md_html(f'<div class="card"><h4 style="color:{C_CYAN}">\u25bc Answers that lowered the estimate</h4>{factor_html(dec, C_CYAN)}</div>')

    st.write("")
    with chart_card("Which of the nine features influenced this estimate most?"):
        shap_bar_chart(table)
        st.caption("Amber bars push the estimate higher; cyan bars push it lower. Values are in score points on the 1\u20135 scale.")

    notice("These are <b>influential predictors inside the model</b>, not causes. A positive contribution means the model's estimate "
           "went up for answers like yours in this sample; it does not mean that factor causes overreliance.", "info")

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
    st.button("Continue to my intervention", type="primary", on_click=goto, args=("Intervention",), key="why_iv")