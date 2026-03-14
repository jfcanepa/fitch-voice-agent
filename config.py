"""
config.py — Loads secrets from Streamlit Cloud or local .env, whichever is available.
"""

import os

from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    # Merge Streamlit secrets into os.environ so all modules can use os.getenv()
    for key, value in st.secrets.items():
        if key not in os.environ:
            os.environ[key] = str(value)
except Exception:
    pass  # Not running in Streamlit, .env already loaded above
