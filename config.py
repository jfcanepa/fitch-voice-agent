"""
config.py — Returns config values from Streamlit Cloud secrets or local .env.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get(key: str, default: str = "") -> str:
    """Get a config value — checks Streamlit secrets first, then os.environ."""
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return str(val)
    except Exception:
        pass
    return os.getenv(key, default)
