import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.append(str(ROOT))

from app.components.theme import card, feed_line, hero, inject_theme, metric_card
from f1predictor.race_engineer.advisor import RaceContext, advise_pit_stop

st.set_page_config(page_title="Race Engineer AI", layout="wide")
inject_theme()

hero(
    eyebrow="Explainable race engineering assistant",
    title="Race Engineer AI",
    body=(
        "A transparent pit-stop advisor for tyre age, undercut windows, safety-car exposure, rain risk, and race phase. "
        "The recommendation is shown with the reasoning, so the user can judge the decision rather than blindly accept it."
    ),
)

st.markdown("## Decision context")
col1, col2, col3 = st.columns(3)
with col1:
    driver = st.text_input("Driver", "LEC").upper()
    current_lap = st.slider("Current lap", 1, 78, 24)
    total_laps = st.slider("Total laps", 30, 78, 53)
with col2:
    current_compound = st.selectbox("Current compound", ["SOFT", "MEDIUM", "HARD"], index=1)
    tire_age = st.slider("Tyre age", 0, 55, 20)
    target_compound = st.selectbox("Target compound", ["SOFT", "MEDIUM", "HARD"], index=2)
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

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Recommendation", advice["decision"], "pit-wall decision signal")
with m2:
    metric_card("Decision score", str(advice["score"]), "higher means stronger call")
with m3:
    metric_card("Undercut gain", f"{advice['undercut_gain_s']}s", "estimated time opportunity")
with m4:
    metric_card("Tyre age", f"{tire_age} laps", f"current {current_compound}")

st.markdown("## Advisor workflow")
w1, w2, w3 = st.columns(3)
with w1:
    card("Race phase", "The model weighs current lap, remaining laps, and tyre life against the value of track position.")
with w2:
    card("Undercut window", "Small gaps ahead increase the value of stopping early to attack with fresh tyres.")
with w3:
    card("Risk overlay", "Safety-car and rain probabilities make the pit call more uncertain and should be reviewed by the engineer.")

st.markdown("## Engineering reasoning")
for idx, line in enumerate(advice["explanation"], start=1):
    feed_line(f"{idx:02d}", line)
