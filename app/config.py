"""
config.py
Loads API keys from environment variables or Streamlit secrets,
depending on where the app is running.
"""

import os


def get_api_key(key_name: str) -> str:
    """
    Returns the API key value, checking environment variables first,
    then Streamlit secrets (for cloud deployment).
    """
    value = os.environ.get(key_name)
    if value:
        return value

    try:
        import streamlit as st
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass

    raise ValueError(
        f"{key_name} not found. Set it as an environment variable "
        f"or in Streamlit secrets."
    )
