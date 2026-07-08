"""Root Streamlit Cloud entrypoint for the elite Formula 1 engineering app."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
ELITE_HOME = ROOT / "f1_elite_upgrade" / "app" / "Home.py"

if not ELITE_HOME.exists():
    st.error("Elite Streamlit app entrypoint was not found.")
    st.stop()

exec(ELITE_HOME.read_text(encoding="utf-8"), {"__file__": str(ELITE_HOME), "__name__": "__main__"})
