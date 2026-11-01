"""
ui/state.py
-----------
Session state and navigation helpers. Page changes always happen inside
callbacks (on_click / on_change) so Streamlit allows updating the nav widget.
"""

from __future__ import annotations

import streamlit as st

PAGES = [
    "Home",
    "Assessment",
    "Results",
    "Explainable AI",
    "Behavioural Insights",
    "Interventions",
    "Research",
    "Model Insights",
    "About",
]


def init_state() -> None:
    defaults = {
        "_page": "Home",
        "nav": "Home",
        "answers": {},        # question id -> answer label (only answered ones)
        "step": 0,            # assessment step 0..5
        "result": None,       # derived scores after submission (no raw dataset)
        "submit_error": None,
        "flag_missing_step": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go(page: str) -> None:
    """Callback: switch page and keep the nav control in sync."""
    st.session_state["_page"] = page
    st.session_state["nav"] = page


def nav_changed() -> None:
    """Callback for the nav control; re-selecting the active page is ignored."""
    choice = st.session_state.get("nav")
    if choice is None:
        st.session_state["nav"] = st.session_state["_page"]
    else:
        st.session_state["_page"] = choice