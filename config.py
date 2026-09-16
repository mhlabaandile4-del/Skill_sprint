import os

import streamlit as st


def get_setting(name, default=None):
    value = os.getenv(name)
    if value:
        return value

    try:
        value = st.secrets.get(name)
    except Exception:
        value = None

    return value or default


def require_setting(name):
    value = get_setting(name)
    if not value:
        raise RuntimeError(
            f"Missing required setting: {name}. "
            "Add it to .streamlit/secrets.toml or the environment."
        )
    return value