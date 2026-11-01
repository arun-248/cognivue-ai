"""
ui/resources.py
---------------
Cached, load-once resources. Models are never retrained.
"""

from __future__ import annotations

import streamlit as st

from backend.model_loader import get_model_information, load_all_models


@st.cache_resource(show_spinner="Loading Cognivue AI models...")
def get_models() -> dict:
    return load_all_models()


def get_model_info() -> dict:
    return get_model_information(get_models())