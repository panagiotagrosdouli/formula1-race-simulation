import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import plotly.express as px
import streamlit as st
from f1predictor.live.live_timing_demo import generate_live_timing_snapshot

st.set_page_config(page_title="Live Timing Demo", layout="wide")
st.title("Live Timing Probability Demo")
st.caption("Synthetic live timing stream that demonstrates real-time probability recalculation.")

lap = st.slider("Lap", 1, 70, 18)
df = generate_live_timing_snapshot(lap)
st.dataframe(df, width="stretch")
fig = px.bar(df, x="Driver", y="WinProbability", title="Live win probability estimate")
st.plotly_chart(fig, width="stretch")
