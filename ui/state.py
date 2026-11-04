"""
ui/state.py
-----------
Session state and navigation helpers. Page changes always happen in callbacks
(on_click / on_change) so Streamlit lets us update widget state safely.
"""

from __future__ import annotations

import logging

import streamlit as st

logger = logging.getLogger("cognivue")

JOURNEY = [
    ("Assess", "assignment", "Answer the 24-question assessment"),
    ("Results", "show_chart", "See your estimated overreliance score"),
    ("Why This Result?", "lightbulb", "Understand what influenced the estimate"),
    ("Intervention", "track_changes", "Complete a personalised learning activity"),
    ("Behavioural Insights", "person", "Review your learning behaviour scores"),
    ("Progress", "timeline", "Report, progress over time and privacy"),
]
RESEARCH_NAV = [
    ("Model Insights", "bar_chart", "Validation, baselines and experiments"),
    ("Research", "science", "Dataset, methods and limitations"),
    ("Testing", "fact_check", "Automated test results"),
    ("About", "info", "Project, team and disclaimer"),
]
STUDENT_SET = {item[0] for item in JOURNEY}


def init_state() -> None:
    defaults = {
        "nav": "Home",
        "answers": {},          # question id -> answer label (answered questions only)
        "step": 0,              # 0 profile, 1-4 Likert sections, 5 review
        "result": None,         # derived scores after submission
        "submit_error": None,
        "flag_missing_step": None,
        "_sticky": {},
        "history": [],          # attempts this session (derived scores only)
        "report_bytes": None,   # generated PDF, kept only in the session
        "assess_confirm": False,
        "iv_task_n": {},
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def iv_values() -> dict:
    """All intervention step/reflection inputs remembered this session (keys iv_<feature>_<id>)."""
    return {k: v for k, v in st.session_state["_sticky"].items() if k.startswith("iv_")}


def sticky(key, default):
    """Keep a widget value across page changes (Streamlit drops unrendered widget state)."""
    store = st.session_state["_sticky"]
    store.setdefault(key, default)
    if key not in st.session_state:
        st.session_state[key] = store[key]


def remember(key):
    st.session_state["_sticky"][key] = st.session_state.get(key)


SCROLL_JS = (
    "<script>(function(){var token=__TOKEN__;function up(){var els=[document.querySelector('[data-testid=\"stMain\"]'),"
    "document.querySelector('section.main'),document.querySelector('[data-testid=\"stAppViewContainer\"]'),"
    "document.scrollingElement,document.documentElement,document.body];"
    "els.forEach(function(e){if(e){try{e.scrollTop=0;if(e.scrollTo){e.scrollTo(0,0);}}catch(_){}}});"
    "try{window.scrollTo(0,0);}catch(_){}}up();var n=0;var t=setInterval(function(){up();n+=1;if(n>8){clearInterval(t);}},100);})();</script>"
)


def scroll_to_top(token):
    """Scroll to the top after navigation. The token inside the script makes each script unique."""
    js = SCROLL_JS.replace("__TOKEN__", str(int(token)))
    try:
        st.html(js, unsafe_allow_javascript=True)
    except TypeError:
        import streamlit.components.v1 as components
        components.html(js.replace("document.", "window.parent.document.").replace("window.scrollTo", "window.parent.scrollTo"), height=0)
    except Exception:
        logger.exception("scroll-to-top helper failed")


def request_scroll_top():
    st.session_state["_scroll_pending"] = True
    st.session_state["_scroll_n"] = st.session_state.get("_scroll_n", 0) + 1


def goto(page):
    st.session_state["nav"] = page
    request_scroll_top()


def open_feature(index):
    st.session_state["feature_idx"] = int(index)
    goto("Feature")