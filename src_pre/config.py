from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

try:
    import streamlit as st
except Exception:
    st = None


def get_secret(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value:
        return value

    if st is not None:
        try:
            return st.secrets[name]
        except Exception:
            pass

    return default


OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "")
OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4.1-mini")