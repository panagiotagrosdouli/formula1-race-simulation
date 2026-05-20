import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st
from f1predictor.race_engineer.advisor import RaceContext, advise_pit_stop

st.set_page_config(page_title="Race Engineer AI", layout="wide")
st.title("AI Race Engineer")
st.caption("Transparent strategy advisor for pit timing, undercut windows and uncertainty risk.")

col1, col2, col3 = st.columns(3)
with col1:
    driver = st.text_input("Driver", "LEC").upper()
    current_lap = st.slider("Current lap", 1, 78, 24)
    total_laps = st.slider("Total laps", 30, 78, 53)
with col2:
    current_compound = st.selectbox("Current compound", ["SOFT", "MEDIUM", "HARD"], index=1)
    target_compound = st.selectbox("Target compound", ["SOFT", "MEDIUM", "HARD"], index=2)
    tire_age = st.slider("Tire age", 0, 55, 20)
with col3:
    gap_ahead = st.number_input("Gap ahead (s)", 0.0, 60.0, 2.0, 0.1)
    gap_behind = st.number_input("Gap behind (s)", 0.0, 60.0, 4.0, 0.1)
    sc_prob = st.slider("Safety car probability", 0.0, 1.0, 0.10, 0.01)
    rain_prob = st.slider("Rain probability", 0.0, 1.0, 0.05, 0.01)

ctx = RaceContext(
    driver=driver,
    current_lap=current_lap,
    total_laps=total_laps,
    current_compound=current_compound,
    tire_age=tire_age,
    gap_ahead_s=gap_ahead,
    gap_behind_s=gap_behind,
    target_compound=target_compound,
    safety_car_probability=sc_prob,
    rain_probability=rain_prob,
)

advice = advise_pit_stop(ctx)

st.metric("Decision", advice["decision"])
st.metric("Decision score", advice["score"])
st.metric("Estimated undercut gain", f"{advice['undercut_gain_s']} s")

st.subheader("Reasoning")
for line in advice["explanation"]:
    st.write(f"- {line}")
