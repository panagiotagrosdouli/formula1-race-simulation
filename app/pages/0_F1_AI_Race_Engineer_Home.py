import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.components.theme import card, feed_line, hero, inject_theme, metric_card

st.set_page_config(page_title="F1 AI Race Engineer", layout="wide")
inject_theme()

hero(
    eyebrow="AI motorsport engineering platform",
    title="F1 AI Race Engineer",
    body=(
        "A premium Formula 1 forecasting cockpit built with machine learning, Monte Carlo "
        "simulation, weather intelligence, race-risk modeling, telemetry insights, tire "
        "degradation analysis, and engineering-grade uncertainty communication."
    ),
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Forecast engine", "ML + simulation", "Race outcome modelling")
with m2:
    metric_card("Race outputs", "Win / Podium / Top 10", "Probability-first results")
with m3:
    metric_card("Risk layer", "Weather + DNF + SC", "Volatility-aware forecasting")
with m4:
    metric_card("Experience", "Product UX", "Not a generic dashboard")

st.markdown("## What the platform does")

c1, c2, c3 = st.columns(3)
with c1:
    card(
        "🏁 Race Forecasting",
        "Predict finishing order using pace, grid position, driver form, team strength, and race-specific context.",
    )
with c2:
    card(
        "🎲 Probabilistic Simulation",
        "Run stochastic race scenarios to estimate expected finish, win probability, podium probability, and top-10 probability.",
    )
with c3:
    card(
        "🧠 Engineering Interpretation",
        "Turn model outputs into decision-support insight with strategy, risk, uncertainty, and scientific limitations.",
    )

c4, c5, c6 = st.columns(3)
with c4:
    card(
        "🌦️ Weather Intelligence",
        "Account for rain probability, air temperature, humidity, wind, and changing race volatility.",
    )
with c5:
    card(
        "📡 Telemetry Thinking",
        "Compare speed traces, driver controls, tire degradation, and performance signatures from racing data.",
    )
with c6:
    card(
        "🏆 Championship Projection",
        "Extend single-race forecasting into season-level driver and constructor title probability estimates.",
    )

st.markdown("## Engineering workflow")
feed_line("01", "Ingest race context: event, grid, pace, weather, driver/team strength, and historical form.")
feed_line("02", "Predict baseline order with supervised ML and convert scores into race-ranking insight.")
feed_line("03", "Simulate uncertainty with Monte Carlo scenarios, reliability effects, and volatility assumptions.")
feed_line("04", "Interpret results like an engineer: risk, tires, safety cars, strategy, and probability limits.")
feed_line("05", "Present the system as a polished technical product for motorsport, ML, and portfolio review.")

st.divider()

left, right = st.columns([1.2, 0.8])
with left:
    st.subheader("Why it feels like a real AI product")
    st.write(
        "The interface is organized around user outcomes: run forecasts, inspect probabilities, "
        "understand risk, review telemetry, and communicate uncertainty. The model stays honest "
        "by presenting predictions as probabilistic rather than guaranteed."
    )
with right:
    st.info(
        "Next step: apply this same shared theme to the main dashboard and the race-engineering pages."
    )

st.success("Premium Streamlit product experience: unified, modular, and ready for page-by-page upgrades.")
