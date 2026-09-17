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

# Turnstile Configuration
TURNSTILE_SITE_KEY = get_setting("TURNSTILE_SITE_KEY")
TURNSTILE_SECRET_KEY = get_setting("TURNSTILE_SECRET_KEY")

# Email Configuration
SMTP_SERVER = get_setting("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = get_setting("SMTP_PORT", "587")
SENDER_EMAIL = get_setting("SENDER_EMAIL")
SENDER_PASSWORD = get_setting("SENDER_PASSWORD")