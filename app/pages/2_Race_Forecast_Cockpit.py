import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.components.theme import card, hero, inject_theme, metric_card
from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.race_analyst import generate_race_report
from src.f1predictor.visualization import plot_predicted_order, plot_probabilities

st.set_page_config(page_title="Race Forecast Cockpit", layout="wide")
inject_theme()

hero(
    eyebrow="Race engineering workstation",
    title="Race Forecast Cockpit",
    body=(
        "Run a future-race forecast with weather-aware risk, Monte Carlo probabilities, "
        "driver/team priors, DNF exposure, and an engineering-style race analyst summary."
    ),
)

RACES = [
    "Australian Grand Prix 2026",
    "Chinese Grand Prix 2026",
    "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026",
    "Saudi Arabian Grand Prix 2026",
    "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026",
    "Canadian Grand Prix 2026",
    "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026",
    "British Grand Prix 2026",
    "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026",
    "Italian Grand Prix 2026",
    "Singapore Grand Prix 2026",
    "United States Grand Prix 2026",
    "Mexico City Grand Prix 2026",
    "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026",
    "Qatar Grand Prix 2026",
    "Abu Dhabi Grand Prix 2026",
]

with st.sidebar:
    st.header("Forecast controls")
    race_name = st.selectbox("Race", RACES, index=11)
    round_no = st.number_input("Round", min_value=1, max_value=30, value=12)
    race_date = st.text_input("Weather date (optional, YYYY-MM-DD)", "")
    n_simulations = st.slider("Monte Carlo simulations", 1000, 50000, 10000, step=1000)
    noise_std = st.slider("Race uncertainty", 0.5, 5.0, 2.0, step=0.1)
    run_forecast = st.button("Run forecast", type="primary")

st.markdown("## Cockpit modules")
info1, info2, info3 = st.columns(3)
with info1:
    card("Forecast model", "Combines driver/team priors, recent form, grid/race context, and modelled race risk.")
with info2:
    card("Monte Carlo", "Converts one predicted order into probability distributions for win, podium, and top-10 outcomes.")
with info3:
    card("Race analyst", "Summarizes the forecast in engineering language while keeping uncertainty visible.")

if not run_forecast:
    st.info("Choose a race in the sidebar and run the forecast to populate the cockpit.")
    st.stop()

with st.spinner("Building demo history, forecasting race, and running Monte Carlo simulation..."):
    history_df = build_demo_dataset()
    result = forecast_future_race(
        history_df=history_df,
        race_name=race_name,
        year=2026,
        round_no=int(round_no),
        race_date=race_date if race_date else None,
        n_simulations=int(n_simulations),
        noise_std=float(noise_std),
        use_2026_grid=True,
    )

forecast = result["forecast"]
simulation = result["simulation"]
weather = result["weather"]

winner = forecast.sort_values("PredictedRank").iloc[0]
win_leader = simulation.sort_values("WinProbability", ascending=False).iloc[0]
podium_leader = simulation.sort_values("PodiumProbability", ascending=False).iloc[0]
top10_leader = simulation.sort_values("Top10Probability", ascending=False).iloc[0]

k1, k2, k3, k4 = st.columns(4)
with k1:
    metric_card("Predicted winner", str(winner["Driver"]), str(winner.get("Team", "")))
with k2:
    metric_card("Win probability leader", str(win_leader["Driver"]), f"{win_leader['WinProbability'] * 100:.1f}%")
with k3:
    metric_card("Podium probability leader", str(podium_leader["Driver"]), f"{podium_leader['PodiumProbability'] * 100:.1f}%")
with k4:
    metric_card("Top-10 stability", str(top10_leader["Driver"]), f"{top10_leader['Top10Probability'] * 100:.1f}%")

w1, w2, w3, w4 = st.columns(4)
with w1:
    metric_card("Weather", str(weather.condition), "Forecast condition")
with w2:
    metric_card("Rain probability", f"{weather.rain_probability * 100:.1f}%", "Weather risk input")
with w3:
    metric_card("Air temperature", f"{weather.air_temperature:.1f} °C", "Thermal context")
with w4:
    metric_card("Humidity", f"{weather.humidity:.1f}%", "Ambient context")

report = generate_race_report(forecast=forecast, simulation=simulation, weather=weather)
st.subheader("Engineering race analyst")
st.info(report)

risk_cols = [
    "Driver",
    "Team",
    "SafetyCarProbability",
    "DNFRisk",
    "RiskAdjustment",
    "PredictedWeatherAdjustment",
]
visible_risk_cols = [column for column in risk_cols if column in forecast.columns]

order_tab, probability_tab, risk_tab = st.tabs([
    "Predicted order",
    "Probability view",
    "Risk model",
])

with order_tab:
    st.dataframe(forecast.sort_values("PredictedRank"), use_container_width=True, hide_index=True)
    st.plotly_chart(plot_predicted_order(forecast), use_container_width=True)

with probability_tab:
    st.dataframe(simulation, use_container_width=True, hide_index=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        st.plotly_chart(plot_probabilities(simulation, "WinProbability"), use_container_width=True)
    with p2:
        st.plotly_chart(plot_probabilities(simulation, "PodiumProbability"), use_container_width=True)
    with p3:
        st.plotly_chart(plot_probabilities(simulation, "Top10Probability"), use_container_width=True)

with risk_tab:
    if visible_risk_cols:
        st.dataframe(forecast[visible_risk_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No risk columns are available for this forecast output.")

st.caption(
    "Predictions are probabilistic engineering estimates. They are not guarantees and should be interpreted with uncertainty in mind."
)
