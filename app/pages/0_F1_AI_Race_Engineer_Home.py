import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.components.theme import card, feed_line, hero, inject_theme, metric_card

st.set_page_config(page_title="F1 Decision Support Platform", layout="wide")
inject_theme()

hero(
    eyebrow="Motorsport decision-support platform",
    title="Mission Control",
    body=(
        "A professional Formula 1 forecasting environment for race analysis, probabilistic simulation, "
        "telemetry review, tyre degradation, weather risk, and model validation. The platform is designed "
        "to help users understand uncertainty and evaluate race scenarios with engineering discipline."
    ),
)

status_1, status_2, status_3, status_4 = st.columns(4)
with status_1:
    metric_card("Forecast engine", "Operational", "Machine learning workflow available")
with status_2:
    metric_card("Monte Carlo", "Ready", "Probability simulation layer")
with status_3:
    metric_card("Telemetry", "Available", "FastF1 analysis modules")
with status_4:
    metric_card("Weather model", "Connected", "Risk-aware forecast inputs")

st.markdown("## Current platform capabilities")

cap_1, cap_2, cap_3 = st.columns(3)
with cap_1:
    card(
        "Race Forecast Workspace",
        "Forecast finishing order, expected position, win probability, podium probability, top-10 probability, and race risk using the existing predictive model and simulation stack.",
    )
with cap_2:
    card(
        "Simulation and Uncertainty",
        "Use Monte Carlo simulation to move beyond a single deterministic result and communicate probability distributions across race outcomes.",
    )
with cap_3:
    card(
        "Telemetry Workstation",
        "Compare speed traces, driver controls, tyre behaviour, and performance signatures using FastF1-backed telemetry workflows.",
    )

cap_4, cap_5, cap_6 = st.columns(3)
with cap_4:
    card(
        "Weather Intelligence",
        "Represent rain probability, temperature, humidity, and volatility as uncertainty inputs rather than pretending conditions are certain.",
    )
with cap_5:
    card(
        "Championship Projection",
        "Extend race-level forecasts into season-level driver and constructor probability estimates with clear scenario interpretation.",
    )
with cap_6:
    card(
        "Model Validation",
        "Surface validation metrics, feature behaviour, and diagnostic views so the system remains scientifically credible and transparent.",
    )

st.markdown("## Engineering workflow")
feed_line("01", "Select a race context: season, event, weather assumptions, and simulation settings.")
feed_line("02", "Execute a forecast using the existing model and race context features.")
feed_line("03", "Run Monte Carlo simulation to estimate uncertainty and probability distributions.")
feed_line("04", "Review risk factors including weather, DNF exposure, safety-car volatility, and tyre behaviour.")
feed_line("05", "Interpret the output through an engineering assessment rather than a single headline result.")

st.markdown("## Quick actions")
action_1, action_2, action_3, action_4 = st.columns(4)
with action_1:
    st.page_link("app/dashboard.py", label="Open main forecast dashboard")
with action_2:
    st.page_link("app/pages/1_Telemetry_Lab.py", label="Open telemetry workspace")
with action_3:
    st.page_link("app/pages/2_Strategy_Lab.py", label="Open strategy workspace")
with action_4:
    st.page_link("app/pages/7_Model_Evaluation.py", label="Open model validation")

st.divider()

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("Product standard")
    st.write(
        "This application should feel like a professional decision-support platform: calm, readable, "
        "workflow-driven, and scientifically honest. Forecasts are probabilistic estimates, not guarantees. "
        "The interface should help users understand what the model says, why uncertainty remains, and what "
        "engineering factors deserve attention."
    )
with right:
    st.subheader("Implementation direction")
    st.write(
        "Next development work should upgrade one workflow at a time: Race Forecast, Simulation, Telemetry, "
        "Tyre Analysis, Weather Intelligence, Championship, and Model Performance. Backend logic should remain "
        "stable unless a specific correctness or architecture issue is identified."
    )

st.success("Mission Control is now the professional entry point for the Formula 1 decision-support platform.")
