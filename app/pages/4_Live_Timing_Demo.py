import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.append(str(ROOT))

from app.components.theme import card, chart, hero, inject_theme, metric_card
from f1predictor.live.live_timing_demo import generate_live_timing_snapshot

st.set_page_config(page_title="Live Timing Demo", layout="wide")
inject_theme()

hero(
    eyebrow="Synthetic live timing feed",
    title="Live Timing Probability Demo",
    body=(
        "A clean live-race demo showing how timing snapshots can update win probability estimates lap by lap. "
        "This page is designed as a production-style prototype for a future live timing integration."
    ),
)

with st.sidebar:
    st.header("Timing controls")
    lap = st.slider("Lap", 1, 70, 18)

snapshot = generate_live_timing_snapshot(lap)
leader = snapshot.sort_values("WinProbability", ascending=False).iloc[0]

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Current lap", str(lap), "synthetic race state")
with m2:
    metric_card("Probability leader", str(leader["Driver"]), "highest live win chance")
with m3:
    metric_card("Win probability", f"{leader['WinProbability'] * 100:.1f}%", "current estimate")
with m4:
    metric_card("Field size", str(len(snapshot)), "tracked drivers")

st.markdown("## Live timing workflow")
w1, w2, w3 = st.columns(3)
with w1:
    card("Timing snapshot", "Each lap creates a simplified field state that can be transformed into probability estimates.")
with w2:
    card("Probability update", "The current race order and synthetic performance signals update the win-probability table.")
with w3:
    card("Production path", "A real deployment would replace the synthetic feed with live gaps, tyre age, sector times and race-control status.")

left, right = st.columns([1, 1.25])
with left:
    st.subheader("Live timing table")
    st.dataframe(snapshot, use_container_width=True, hide_index=True)
with right:
    st.subheader("Win probability")
    fig = px.bar(
        snapshot.sort_values("WinProbability", ascending=False),
        x="Driver",
        y="WinProbability",
        title="Live win probability estimate",
    )
    chart(fig)
