import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import streamlit as st
from theme import apply_theme, hero, panel

st.set_page_config(page_title="F1 Elite Engineering", page_icon="🏎️", layout="wide")
apply_theme()

hero(
    "🏎️ F1 Elite Engineering Platform",
    "A premium motorsport analytics workspace with telemetry comparison, strategy simulation, explainable race-engineer advice and live timing probability demos.",
    ["Telemetry", "Strategy", "Race Engineer AI", "Live timing"],
)

panel(
    "Where your work is",
    "This is the restored entrypoint for the elite Streamlit upgrade. Use the sidebar pages to open Telemetry Lab, Strategy Lab, Race Engineer AI and Live Timing Demo.",
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Telemetry Lab", "Ready", "FastF1 + demo fallback")
col2.metric("Strategy Lab", "Ready", "Tyre and pit-window model")
col3.metric("Race Engineer AI", "Ready", "Explainable advice")
col4.metric("Live Timing", "Ready", "Synthetic probability feed")

st.subheader("Elite modules")
modules = [
    {
        "title": "📡 Telemetry Lab",
        "body": "Compare two drivers using speed traces, lap-time delta, controls and track map visualizations.",
    },
    {
        "title": "🧠 Strategy Lab",
        "body": "Compare tyre strategies, pit-loss sensitivity and one-stop pit windows with transparent assumptions.",
    },
    {
        "title": "🎙️ Race Engineer AI",
        "body": "Inspect pit-stop decisions with undercut gain, tyre-life risk, safety-car probability and rain exposure.",
    },
    {
        "title": "⏱️ Live Timing Demo",
        "body": "Move the lap slider to emulate live timing and see changing win-probability estimates.",
    },
]

for item in modules:
    panel(item["title"], item["body"])

st.info(
    "Run this app with: streamlit run f1_elite_upgrade/app/Home.py. "
    "For Streamlit Cloud, set the main file path to f1_elite_upgrade/app/Home.py."
)
