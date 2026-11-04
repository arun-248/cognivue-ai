"""
Cognivue AI - main Streamlit application.

Run locally:   py -m streamlit run app.py
"""

import logging

import streamlit as st

# Application logging: technical events only. Questionnaire answers are never logged.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

st.set_page_config(
    page_title="Cognivue AI | Learning Intelligence",
    page_icon="\U0001f9e0",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui.about import page_about  # noqa: E402
from ui.assessment import page_assess  # noqa: E402
from ui.explain import page_explain  # noqa: E402
from ui.feature import page_feature  # noqa: E402
from ui.home import page_home  # noqa: E402
from ui.interventions import page_intervention  # noqa: E402
from ui.layout import render_left_panel, render_navbar, render_right_panel  # noqa: E402
from ui.model_insights import page_model_insights  # noqa: E402
from ui.profile import page_profile
from ui.progress import page_progress  # noqa: E402
from ui.research import page_research  # noqa: E402
from ui.resources import get_model_info  # noqa: E402
from ui.results import page_results  # noqa: E402
from ui.state import STUDENT_SET, init_state, logger, scroll_to_top  # noqa: E402
from ui.testing import page_testing  # noqa: E402
from ui.theme import footer, inject_css, notice  # noqa: E402

PAGES = {
    "Home": page_home,
    "Assess": page_assess,
    "Results": page_results,
    "Why This Result?": page_explain,
    "Intervention": page_intervention,
    "Behavioural Insights": page_profile,
    "Progress": page_progress,
    "Model Insights": page_model_insights,
    "Research": page_research,
    "Testing": page_testing,
    "Feature": page_feature,
    "About": page_about,
}

inject_css()
init_state()

current = st.session_state.get("nav")
if current not in PAGES:
    current = "Home"

render_navbar(current)

# Model health check (cached): friendly message instead of a crash if files are missing.
try:
    info = get_model_info()
    if not info["sklearn_versions_match"]:
        notice(f"The saved model was trained with scikit-learn {info['sklearn_trained_with']} but {info['sklearn_installed']} is installed. "
               "Install scikit-learn==1.6.1 (py -m pip install -r requirements.txt).", "warn")
except Exception as exc:
    logger.exception("Model loading failed")
    notice(f"The models could not be loaded ({type(exc).__name__}). Check that the <code>models</code> folder is next to <code>app.py</code> "
           "and that <code>py test_model_loader.py</code> passes. Pages that need the model will not work until this is fixed.", "warn")

show_right = current in STUDENT_SET
with st.container(key="shell"):
    shell_cols = st.columns([0.95, 4.2, 1.2] if show_right else [0.95, 5.4], gap="medium")
    with shell_cols[0]:
        render_left_panel(current)
    with shell_cols[1]:
        try:
            PAGES[current]()
        except Exception:
            logger.exception("Page %s failed", current)
            notice("Something went wrong while displaying this page. Please try another section or reload the app.", "warn")
    if show_right:
        with shell_cols[2]:
            render_right_panel(current)

if st.session_state.pop("_scroll_pending", False):
    with st.container(key="scrollhook"):
        scroll_to_top(st.session_state.get("_scroll_n", 0))

footer()