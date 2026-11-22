"""ui/progress.py - PDF report, attempts over time, progress file and privacy information."""

from __future__ import annotations

import logging
from datetime import datetime

import streamlit as st

from backend.explainability import explain_prediction
from backend.history import CONSTRUCTS, LABELS, compare_attempts
from backend.interventions import all_progress, intervention_summary
from backend.report import build_report_pdf
from ui import charts
from ui.resources import get_cached_explainer, get_models
from ui.state import goto, iv_values
from ui.theme import chart_card, esc, md_html, notice, section_title, stat

logger = logging.getLogger("cognivue.progress")


def _make_report() -> None:
    result = st.session_state.get("result")
    st.session_state["report_error"] = None
    if not result:
        st.session_state["report_error"] = "Complete the assessment first."
        return
    try:
        if result["shap"] is None:
            models = get_models()
            result["shap"] = explain_prediction(models["random_forest"], result["frame"], get_cached_explainer())
        values = iv_values()
        summary = intervention_summary(result["interventions"], all_progress(values), values,
                                       include_reflections=bool(st.session_state.get("report_reflections")))
        cluster = result["cluster"]
        st.session_state["report_bytes"] = build_report_pdf(
            result, result["shap"] or None, cluster, summary, st.session_state.get("history", []),
            label=st.session_state.get("report_label", ""), include_reflections=bool(st.session_state.get("report_reflections")))
        st.session_state["report_time"] = datetime.now().strftime("%H:%M")
    except Exception:
        logger.exception("Report generation failed")
        st.session_state["report_bytes"] = None
        st.session_state["report_error"] = "The report could not be created. Please try again, or complete the assessment again."


def _clear_history() -> None:
    st.session_state["history"] = []
    st.session_state["progress_msg"] = ("ok", "Saved attempts for this session were cleared.")


def page_progress():
    section_title("My Report & Progress", "Download your assessment report, review earlier attempts, and see how your data is handled.")
    result = st.session_state.get("result")
    history = st.session_state.get("history", [])

    # ---------------- report ----------------
    md_html('<div class="eyebrow">A \u00b7 My assessment report</div>')
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment to create a report.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_progress")
    else:
        md_html('<div class="card"><h4>Download your assessment report (PDF)</h4><p>The report contains your predicted overreliance score, your four learning-dimension scores, '
                'recommendations, the explanation of your result, your activity progress and, if you have two attempts, your change since the last one. '
                'It does not list your answers question by question.</p></div>')
        st.write("")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.text_input("Optional label for the cover (for example your first name or a nickname)", key="report_label", max_chars=40)
        with c2:
            st.checkbox("Include the reflections I wrote in my activities", key="report_reflections")
        st.button("Create PDF report", type="primary", on_click=_make_report, key="make_report")
        if st.session_state.get("report_error"):
            st.error(st.session_state["report_error"])
        if st.session_state.get("report_bytes"):
            st.download_button("Download PDF report", data=st.session_state["report_bytes"], file_name="cognivue_report.pdf",
                               mime="application/pdf", key="download_report")
            st.caption(f"Generated at {st.session_state.get('report_time', '')}. Generate it again after you change an activity or start a new attempt.")

    # ---------------- attempts ----------------
    st.write("")
    md_html('<div class="eyebrow">B \u00b7 My progress</div>')
    section_title("Your attempts over time", "Each assessment you submit is added here so you can compare your predicted score and learning-dimension scores.")
    if not history:
        md_html('<div class="card"><h4>No attempts yet</h4><p>Each time you submit the assessment, your scores are added here so you can repeat it later and compare.</p></div>')
    else:
        def _row(i, a):
            return (f"<tr><td>{i}</td><td>{esc(a['timestamp'].replace('T', ' ')[:16])}</td><td>{a['predicted_score']:.2f}</td>"
                    + "".join(f"<td>{a['construct_scores'][f]:.2f}</td>" for f in CONSTRUCTS) + "</tr>")

        rows = "".join(_row(i, a) for i, a in enumerate(history, 1))
        head = "".join(f"<th>{LABELS[f]}</th>" for f in CONSTRUCTS)
        md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr><th>#</th><th>Time (UTC)</th><th>Predicted score</th>{head}</tr>{rows}</table></div>')
        if len(history) >= 2:
            st.write("")
            with chart_card("How have my scores changed across attempts?"):
                xs = list(range(1, len(history) + 1))
                series = {"Predicted overreliance": [a["predicted_score"] for a in history]}
                colors = {"Predicted overreliance": "#142B55"}
                palette = ["#3478F6", "#8757E8", "#0F8F80", "#E8731F"]
                for f, color in zip(CONSTRUCTS, palette):
                    series[LABELS[f]] = [a["construct_scores"][f] for a in history]
                    colors[LABELS[f]] = color
                charts.show(charts.multi_line(xs, series, colors, "Score (1\u20135)", "Attempt number", yrange=[1, 5]), "prog_lines")
                st.caption("Each point is one attempt. All values are on a 1\u20135 scale.")
            prev, last = history[-2], history[-1]
            delta = compare_attempts(prev, last)
            md_html('<div class="grid g4">'
                    + "".join(stat(f"{delta['construct_scores'][f]:+.2f}", LABELS[f], f"{prev['construct_scores'][f]:.2f} \u2192 {last['construct_scores'][f]:.2f}") for f in CONSTRUCTS)
                    + "</div>")
            st.write("")
            notice(f"Change in the predicted score since the previous attempt: <b>{delta['predicted_score']:+.2f}</b>. "
                   "These are changes in <b>self-reported scores</b>. They do not prove that your actual ability or thinking has changed, and differences can be small "
                   "relative to the model's typical error of about 0.5 points.", "warn")
    st.write("")
    msg = st.session_state.get("progress_msg")
    if msg:
        (st.success if msg[0] == "ok" else st.warning)(msg[1])
    if history:
        st.button("Clear saved attempts", on_click=_clear_history, key="clear_history")

    # ---------------- privacy ----------------
    st.write("")
    md_html('<div class="eyebrow">C \u00b7 Privacy and data usage</div>')
    section_title("How your data is handled", "What the app keeps, when it is cleared, and what the PDF report contains.")
    md_html(
        '<div class="grid g3">'
        '<div class="card"><h4>Kept during this session</h4><p>Your answers, your result, your attempts and the text you write in activities are held in this browser session only. '
        'The app does not ask for your name, email or student ID, and it does not write your answers to a file or database.</p></div>'
        '<div class="card"><h4>When it is cleared</h4><p>Refreshing or closing the page clears the session. Start Over clears your current answers, result and activity text. '
        '\u201cClear saved attempts\u201d removes the attempts listed above.</p></div>'
        '<div class="card"><h4>What the PDF contains</h4><p>The PDF report contains your scores, your chosen AI usage frequency and duration, and suggestions based on your answers. '
        'It does not list your answers question by question. Activity reflections are added to the PDF only if you tick the box, and the optional label appears only on the cover.</p></div>'
        '</div>'
    )
    st.caption("Please avoid typing personal or identifying details into the free-text activity boxes.")
    st.write("")
    c1, _ = st.columns([1.4, 3])
    with c1:
        st.button("Back to results", on_click=goto, args=("Results",), key="prog_back")
