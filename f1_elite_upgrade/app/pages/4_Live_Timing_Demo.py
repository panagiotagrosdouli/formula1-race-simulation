import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import plotly.express as px
import streamlit as st
from f1predictor.live.live_timing_demo import generate_live_timing_snapshot
from theme import FERRARI_RED, apply_theme, chart, hero, panel

st.set_page_config(page_title="Live Timing Demo", page_icon="⏱️", layout="wide")
apply_theme()
hero(
    "⏱️ Live Timing Probability Demo",
    "Synthetic race-control feed that demonstrates how live timing inputs can update win probability estimates during a race.",
    ["Live timing", "Probability", "Race state", "Demo stream"],
)

with st.sidebar:
    st.header("Timing controls")
    lap = st.slider("Lap", 1, 70, 18)
    st.caption("Move the lap slider to emulate a changing live timing state.")

df = generate_live_timing_snapshot(lap)
leader = df.sort_values("WinProbability", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Current lap", lap)
col2.metric("Probability leader", leader["Driver"])
col3.metric("Win probability", f"{leader['WinProbability'] * 100:.1f}%")

panel(
    "Live probability interpretation",
    "This demo shows how a timing feed can be translated into probabilistic race intelligence. In a production system, this layer would use real sector times, gaps, tyre age, pit windows and safety-car state.",
)

st.subheader("Live timing table")
st.dataframe(df, use_container_width=True, hide_index=True)

fig = px.bar(
    df.sort_values("WinProbability", ascending=False),
    x="Driver",
    y="WinProbability",
    title="Live win probability estimate",
    color_discrete_sequence=[FERRARI_RED],
)
chart(fig)
