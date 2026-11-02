"""ui/layout.py - top navbar, left panel, right art panel (same layout as the earlier project)."""

from __future__ import annotations

import streamlit as st

from ui.art import ART, ART_FOR_PAGE, LOGO_SVG, SIDE_ART
from ui.state import JOURNEY, RESEARCH_NAV, STUDENT_SET, goto
from ui.theme import md_html


def render_navbar(current: str) -> None:
    mode = "Home" if current in ("Home", "Feature") else ("Student" if current in STUDENT_SET else "Research")
    with st.container(key="topnav"):
        cols = st.columns([2.6, 0.9, 1.75, 2.0, 1.4], gap="small")
        with cols[0]:
            md_html(
                f'<div class="nav-brand"><div class="nav-logo">{LOGO_SVG}</div><div>'
                '<div class="nav-name">Cognivue AI</div>'
                '<div class="nav-sub">Detect · Understand · Support · Learn</div></div></div>'
            )
        with cols[1]:
            st.button("Home", icon=":material/home:", key="top_home",
                      type="primary" if mode == "Home" else "secondary", on_click=goto, args=("Home",))
        with cols[2]:
            st.button("Student Experience", icon=":material/school:", key="top_student",
                      type="primary" if mode == "Student" else "secondary", on_click=goto, args=("Assess",))
        with cols[3]:
            st.button("Research & Evaluation", icon=":material/bar_chart:", key="top_research",
                      type="primary" if mode == "Research" else "secondary", on_click=goto, args=("Model Insights",))
        with cols[4]:
            with st.container(key="nav_cta"):
                st.button("Get Started", key="top_cta", on_click=goto, args=("Assess",))


def render_left_panel(current: str) -> None:
    with st.container(key="leftpanel"):
        md_html('<div class="panel-label">Student experience</div>')
        assessed = st.session_state.get("result") is not None
        for i, (page, icon, hint) in enumerate(JOURNEY):
            shown = "check_circle" if (page == "Assess" and assessed) else icon
            st.button(page, icon=f":material/{shown}:", key=f"side_{i}", help=hint,
                      type="primary" if current == page else "secondary", on_click=goto, args=(page,))
        md_html('<div class="panel-divider"></div><div class="panel-label">Research &amp; evaluation</div>')
        for i, (page, icon, hint) in enumerate(RESEARCH_NAV):
            st.button(page, icon=f":material/{icon}:", key=f"rside_{i}", help=hint,
                      type="primary" if current == page else "secondary", on_click=goto, args=(page,))
        md_html(f'<div class="side-art">{SIDE_ART}<p>Think independently. Learn intelligently.</p></div>')


def render_right_panel(current: str) -> None:
    key, title, caption = ART_FOR_PAGE.get(current, ART_FOR_PAGE["Home"])
    with st.container(key="rightpanel"):
        md_html(f'<div class="art-card">{ART[key]}<div class="cap"><b>{title}</b><p>{caption}</p></div></div>')