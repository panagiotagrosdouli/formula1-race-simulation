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

st.set_page_config(page_title="Race Forecast Workspace", layout="wide")
inject_theme()

hero(
    eyebrow="Forecast decision workspace",
    title="Race Forecast Workspace",
    body=(
        "Execute a future-race forecast, review probability outputs, inspect weather and risk factors, "
        "and convert the model result into a structured engineering assessment."
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
    st.header("Forecast configuration")
    race_name = st.selectbox("Race", RACES, index=11)
    round_no = st.number_input("Round", min_value=1, max_value=30, value=12)
    race_date = st.text_input("Weather date (optional, YYYY-MM-DD)", "")
    n_simulations = st.slider("Simulation runs", 1000, 50000, 10000, step=1000)
    noise_std = st.slider("Race uncertainty", 0.5, 5.0, 2.0, step=0.1)
    run_forecast = st.button("Execute forecast", type="primary")

st.markdown("## Workspace structure")
col_a, col_b, col_c = st.columns(3)
with col_a:
    card("Configuration", "Select race context, round, optional weather date, simulation count, and uncertainty level.")
with col_b:
    card("Probability analysis", "Review win, podium, and top-10 probability outputs from Monte Carlo simulation.")
with col_c:
    card("Engineering assessment", "Convert the forecast into an interpretable report with uncertainty and model limitations.")

if not run_forecast:
    st.info("Configure the race in the sidebar and execute the forecast.")
    st.stop()

with st.spinner("Building race context, executing forecast, and running Monte Carlo simulation..."):
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

forecast_order = forecast.sort_values("PredictedRank")
winner = forecast_order.iloc[0]
win_leader = simulation.sort_values("WinProbability", ascending=False).iloc[0]
podium_leader = simulation.sort_values("PodiumProbability", ascending=False).iloc[0]
top10_leader = simulation.sort_values("Top10Probability", ascending=False).iloc[0]

st.markdown("## Executive summary")
s1, s2, s3, s4 = st.columns(4)
with s1:
    metric_card("Forecast winner", str(winner["Driver"]), str(winner.get("Team", "")))
with s2:
    metric_card("Win probability leader", str(win_leader["Driver"]), f"{win_leader['WinProbability'] * 100:.1f}%")
with s3:
    metric_card("Podium probability leader", str(podium_leader["Driver"]), f"{podium_leader['PodiumProbability'] * 100:.1f}%")
with s4:
    metric_card("Top-10 stability leader", str(top10_leader["Driver"]), f"{top10_leader['Top10Probability'] * 100:.1f}%")

w1, w2, w3, w4 = st.columns(4)
with w1:
    metric_card("Weather condition", str(weather.condition), "Forecast context")
with w2:
    metric_card("Rain probability", f"{weather.rain_probability * 100:.1f}%", "Weather risk")
with w3:
    metric_card("Air temperature", f"{weather.air_temperature:.1f} °C", "Thermal context")
with w4:
    metric_card("Humidity", f"{weather.humidity:.1f}%", "Ambient context")

report = generate_race_report(forecast=forecast, simulation=simulation, weather=weather)

results_tab, probabilities_tab, risk_tab, assessment_tab = st.tabs(
    [
        "Forecast results",
        "Probability analysis",
        "Risk assessment",
        "Engineering assessment",
    ]
)

with results_tab:
    st.markdown("### Forecast order")
    visible_cols = [
        column
        for column in ["Driver", "Team", "PredictedRank", "PredictedPosition", "PredictedPoints"]
        if column in forecast_order.columns
    ]
    st.dataframe(forecast_order[visible_cols] if visible_cols else forecast_order, use_container_width=True, hide_index=True)
    st.plotly_chart(plot_predicted_order(forecast), use_container_width=True)

with probabilities_tab:
    st.markdown("### Monte Carlo probability table")
    probability_cols = [
        column
        for column in ["Driver", "Team", "WinProbability", "PodiumProbability", "Top10Probability"]
        if column in simulation.columns
    ]
    st.dataframe(simulation[probability_cols] if probability_cols else simulation, use_container_width=True, hide_index=True)

    p1, p2, p3 = st.columns(3)
    with p1:
        st.plotly_chart(plot_probabilities(simulation, "WinProbability"), use_container_width=True)
    with p2:
        st.plotly_chart(plot_probabilities(simulation, "PodiumProbability"), use_container_width=True)
    with p3:
        st.plotly_chart(plot_probabilities(simulation, "Top10Probability"), use_container_width=True)

with risk_tab:
    st.markdown("### Risk factors")
    risk_cols = [
        column
        for column in [
            "Driver",
            "Team",
            "SafetyCarProbability",
            "DNFRisk",
            "RiskAdjustment",
            "PredictedWeatherAdjustment",
        ]
        if column in forecast.columns
    ]
    if risk_cols:
        st.dataframe(forecast[risk_cols], use_container_width=True, hide_index=True)
    else:
        st.info("Risk columns are not available in this forecast output.")

    card(
        "Risk interpretation",
        "Weather, DNF exposure, safety-car volatility, and model uncertainty should be interpreted together. A forecast leader can still carry high race risk if volatility inputs are elevated.",
    )

with assessment_tab:
    st.markdown("### Engineering assessment")
    st.info(report)
    st.markdown("### Scientific limitations")
    st.write(
        "This forecast is a probabilistic estimate based on the current model inputs and simulation assumptions. "
        "It should not be interpreted as a guaranteed classification. Real race outcomes can change due to tyre behaviour, "
        "strategy calls, reliability, safety cars, weather evolution, driver incidents, and data limitations."
    )

st.caption("Forecasts are probabilistic engineering estimates, not guaranteed race results.")
