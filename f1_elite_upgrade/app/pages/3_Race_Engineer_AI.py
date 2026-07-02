import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import streamlit as st
from f1predictor.race_engineer.advisor import RaceContext, advise_pit_stop
from theme import apply_theme, hero, panel

st.set_page_config(page_title="Race Engineer AI", page_icon="🎙️", layout="wide")
apply_theme()
hero(
    "🎙️ Race Engineer AI",
    "Transparent pit-stop advisor for undercut timing, tyre-life risk, safety-car uncertainty and rain exposure. Built as a decision-support tool, not a black-box answer.",
    ["Pit advice", "Undercut", "Risk", "Explainable AI"],
)

panel(
    "Decision model",
    "Adjust the race context and inspect both the recommendation and the explanation. A strong engineering interface should show why the decision was made, not only the final instruction.",
)

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Race state")
    driver = st.text_input("Driver", "LEC").upper()
    current_lap = st.slider("Current lap", 1, 78, 24)
    total_laps = st.slider("Total laps", 30, 78, 53)
with col2:
    st.subheader("Tyre plan")
    current_compound = st.selectbox("Current compound", ["SOFT", "MEDIUM", "HARD"], index=1)
    target_compound = st.selectbox("Target compound", ["SOFT", "MEDIUM", "HARD"], index=2)
    tire_age = st.slider("Tyre age", 0, 55, 20)
with col3:
    st.subheader("Risk context")
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

k1, k2, k3, k4 = st.columns(4)
k1.metric("Decision", advice["decision"])
k2.metric("Decision score", advice["score"])
k3.metric("Undercut gain", f"{advice['undercut_gain_s']} s")
k4.metric("Tyre age", f"{tire_age} laps")

st.subheader("Engineering reasoning")
for line in advice["explanation"]:
    st.markdown(f"- {line}")
