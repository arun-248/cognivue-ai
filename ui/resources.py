"""
ui/resources.py
---------------
Load-once cached resources. Models are never retrained.
"""

from __future__ import annotations

import streamlit as st

from backend.explainability import get_explainer
from backend.model_loader import get_model_information, load_all_models


@st.cache_resource(show_spinner=False)
def get_models() -> dict:
    return load_all_models()


@st.cache_resource(show_spinner=False)
def get_cached_explainer():
    return get_explainer(get_models()["random_forest"])


def get_model_info() -> dict:
    return get_model_information(get_models())