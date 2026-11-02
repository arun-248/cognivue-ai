"""ui/testing.py - automated test results (read from test_results.json, never invented)."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from ui.state import logger
from ui.theme import esc, md_html, notice, section_title, stat

BASE_DIR = Path(__file__).resolve().parent.parent


def load_test_results():
    path = BASE_DIR / "test_results.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("test_results.json could not be read")
        return None


def page_testing():
    section_title("Testing", "Automated checks that the app reproduces the Colab pipeline and behaves safely.")
    data = load_test_results()
    if not data:
        notice("No test results file was found. Run <code>py test_pipeline.py</code> and <code>py test_app_flow.py</code> in the project folder. Each run records its "
               "results in <code>test_results.json</code>, which this page then displays. Nothing is shown as passed until the tests have actually run.", "warn")
        return
    tests = data.get("tests", [])
    passed = sum(t["status"] == "Pass" for t in tests)
    failed = sum(t["status"] == "Fail" for t in tests)
    env = data.get("environment", {})
    md_html('<div class="grid g3">'
            + stat(str(len(tests)), "Test cases", "recorded below")
            + stat(str(passed), "Passed", "observed result matched", "#16A34A")
            + stat(str(failed), "Failed", "needs attention", "#EF4444" if failed else None)
            + "</div>")
    st.write("")
    notice(f"Generated {esc(data.get('generated', 'unknown'))} \u00b7 Python {esc(env.get('python', '?'))} \u00b7 Streamlit {esc(env.get('streamlit', '?'))} \u00b7 "
           f"scikit-learn {esc(env.get('scikit-learn', '?'))} \u00b7 SHAP {esc(env.get('shap', '?'))}. Re-run the scripts on your own machine before submission.", "info")
    st.write("")
    suites = []
    for t in tests:
        if t["suite"] not in suites:
            suites.append(t["suite"])
    tabs = st.tabs(suites)
    for tab, suite in zip(tabs, suites):
        with tab:
            rows = "".join(
                f"<tr><td>{esc(t['id'])}</td><td>{esc(t['category'])}</td><td>{esc(t['test'])}</td>"
                f"<td style='font-weight:700;color:{'#15803D' if t['status'] == 'Pass' else '#DC2626'}'>{esc(t['status'])}</td></tr>"
                for t in tests if t["suite"] == suite)
            md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr><th>ID</th><th>Category</th><th>Check</th><th>Status</th></tr>{rows}</table></div>')