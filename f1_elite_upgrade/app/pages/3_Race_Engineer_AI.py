from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import pandas as pd
import plotly.express as px
import streamlit as st
from f1predictor.race_engineer.advisor import RaceContext, advise_pit_stop
from theme import apply_theme, chart, hero, panel, section_header, status_cards, workflow_steps

st.set_page_config(page_title="Race Engineer AI", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Race Engineer AI",
    "Pit-wall decision support for undercut timing, tyre-life risk, traffic exposure, safety-car uncertainty and rain probability. The page explains why, not only what to do.",
    ["Decision support", "Pit wall", "Explainable AI", "Risk"],
)

controls, cockpit = st.columns([0.32, 0.68])
with controls:
    section_header("Inputs", "Race context", "Tune the current race state before asking the virtual engineer.")
    driver = st.text_input("Driver", "LEC").upper()
    current_lap = st.slider("Current lap", 1, 78, 24)
    total_laps = st.slider("Total laps", 30, 78, 53)
    current_compound = st.selectbox("Current compound", ["SOFT", "MEDIUM", "HARD"], index=1)
    target_compound = st.selectbox("Target compound", ["SOFT", "MEDIUM", "HARD"], index=2)
    tire_age = st.slider("Tyre age", 0, 55, 20)
    gap_ahead = st.number_input("Gap ahead [s]", 0.0, 60.0, 2.0, 0.1)
    gap_behind = st.number_input("Gap behind [s]", 0.0, 60.0, 4.0, 0.1)
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

with cockpit:
    decision = str(advice["decision"])
    score = float(advice["score"])
    confidence = max(0.0, min(1.0, score / 100.0))
    risk = "High" if rain_prob > 0.35 or sc_prob > 0.35 else "Medium" if tire_age > 25 else "Low"
    status_cards(
        [
            ("Recommendation", decision, "Model-derived pit-wall instruction."),
            ("Confidence", f"{confidence:.0%}", "Decision score converted to confidence band."),
            ("Undercut gain", f"{float(advice['undercut_gain_s']):.2f}s", "Estimated attack opportunity."),
            ("Risk", risk, "Driven by tyre age, rain and SC exposure."),
        ]
    )

    left, right = st.columns([1.08, 0.92])
    with left:
        section_header("Engineer board", "Decision rationale", "Traceable logic for the recommendation.")
        workflow_steps([(f"Reason {i + 1}", line) for i, line in enumerate(advice["explanation"])])
        panel(
            "Operational limitation",
            "This is decision-support logic over transparent assumptions. It is not a real team radio message and does not use private team strategy data.",
        )
    with right:
        section_header("Risk model", "Context sensitivity", "Which signals are putting pressure on the decision.")
        factors = pd.DataFrame(
            [
                ["Tyre age", tire_age / max(total_laps, 1)],
                ["Gap ahead pressure", max(0.0, min(1.0, 1.0 - gap_ahead / 10.0))],
                ["Gap behind risk", max(0.0, min(1.0, 1.0 - gap_behind / 10.0))],
                ["Safety car probability", sc_prob],
                ["Rain probability", rain_prob],
            ],
            columns=["Factor", "Pressure"],
        )
        chart(px.bar(factors, x="Factor", y="Pressure", title="Decision pressure factors"))
        st.dataframe(factors, use_container_width=True, hide_index=True)
