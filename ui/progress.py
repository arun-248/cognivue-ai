"""ui/progress.py - PDF report, attempts over time, progress file and privacy information."""

from __future__ import annotations

import logging
from datetime import datetime

import streamlit as st

from backend.explainability import explain_prediction
from backend.history import CONSTRUCTS, LABELS, compare_attempts, export_history, import_history, merge_histories
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


def _on_upload() -> None:
    uploaded = st.session_state.get("progress_upload")
    st.session_state["progress_msg"] = None
    if uploaded is None:
        return
    try:
        imported = import_history(uploaded.getvalue())
        before = len(st.session_state["history"])
        st.session_state["history"] = merge_histories(st.session_state["history"], imported)
        added = len(st.session_state["history"]) - before
        st.session_state["progress_msg"] = ("ok", f"Loaded {len(imported)} attempt(s); {added} new attempt(s) added.")
    except ValueError as exc:
        st.session_state["progress_msg"] = ("warn", f"That file could not be loaded: {exc}")


def _clear_history() -> None:
    st.session_state["history"] = []
    st.session_state["progress_msg"] = ("ok", "Saved attempts for this session were cleared.")


def page_progress():
    section_title("My Report & Progress", "Download a report, compare attempts over time, and see exactly how your data is handled.")
    result = st.session_state.get("result")
    history = st.session_state.get("history", [])

    # ---------------- report ----------------
    md_html('<div class="eyebrow">1 \u00b7 PDF report</div>')
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment to create a report.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_progress")
    else:
        md_html('<div class="card"><h4>Student assessment report</h4><p>A short PDF with your estimated score, learning-habit scores, focus area, recommendations, '
                'the SHAP explanation, your activity progress and (if you have two attempts) your change since the last one. It contains scores, not your raw answers.</p></div>')
        st.write("")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.text_input("Optional label for the cover (for example your first name or a nickname)", key="report_label", max_chars=40)
        with c2:
            st.checkbox("Include the reflections I wrote in my activities", key="report_reflections")
        st.button("Generate report", type="primary", on_click=_make_report, key="make_report")
        if st.session_state.get("report_error"):
            st.error(st.session_state["report_error"])
        if st.session_state.get("report_bytes"):
            st.download_button("Download PDF report", data=st.session_state["report_bytes"], file_name="cognivue_report.pdf",
                               mime="application/pdf", key="download_report")
            st.caption(f"Generated at {st.session_state.get('report_time', '')}. Generate it again after you change an activity or start a new attempt.")

    # ---------------- attempts ----------------
    section_title("2 \u00b7 Your attempts over time",
                  "Attempts are kept in this browser session. Download a progress file to compare across visits.")
    if not history:
        md_html('<div class="card"><h4>No attempts yet</h4><p>Each time you submit the assessment, your scores are added here so you can repeat it later and compare.</p></div>')
    else:
        rows = "".join(
            f"<tr><td>{i}</td><td>{esc(a['timestamp'].replace('T', ' ')[:16])}</td><td>{a['predicted_score']:.2f}</td>"
            + "".join(f"<td>{a['construct_scores'][f]:.2f}</td>" for f in CONSTRUCTS) + "</tr>" for i, a in enumerate(history, 1))
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
                st.caption("Each point is one attempt. These are self-reported scores; the predicted score is a model estimate from the same answers.")
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
        st.download_button("Download my progress file (JSON)", data=export_history(history), file_name="cognivue_progress.json",
                           mime="application/json", key="download_progress")
    st.file_uploader("Load a progress file from an earlier visit", type=["json"], key="progress_upload", on_change=_on_upload)
    msg = st.session_state.get("progress_msg")
    if msg:
        (st.success if msg[0] == "ok" else st.warning)(msg[1])
    if history:
        st.button("Clear saved attempts", on_click=_clear_history, key="clear_history")

    # ---------------- privacy ----------------
    section_title("3 \u00b7 Privacy and data usage")
    md_html(
        '<div class="grid g2">'
        '<div class="card"><h4>What the app does with your answers</h4><p>Your answers are converted to four section averages and five encoded values, which are given to a saved model. '
        'They stay in this browser session. The app does not write them to a file, database or application log, and it does not ask for your name, email or student ID.</p></div>'
        '<div class="card"><h4>What you can download</h4><p>The PDF report and the progress file contain derived scores and your chosen options, not your raw answers. '
        'Anything you download is yours to keep or delete. A label on the report is optional and used only on the cover.</p></div>'
        '<div class="card"><h4>What clears your data</h4><p>Refreshing or closing the page clears the session. Start Over clears your current answers and result. '
        'Clear saved attempts removes the attempts shown above.</p></div>'
        '<div class="card"><h4>Hosting note</h4><p>The hosting provider may keep standard technical server logs (for example connection times). These do not contain your answers. '
        'Do not enter personal or identifying details in the free-text activity boxes.</p></div>'
        '</div>'
    )
    st.write("")
    c1, _ = st.columns([1.4, 3])
    with c1:
        st.button("Back to results", on_click=goto, args=("Results",), key="prog_back")
