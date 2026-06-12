import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.simulation import lap_by_lap_race_simulation
from src.f1predictor.decision_intelligence import (
    analyst_explanation,
    bayesian_forecast_intervals,
    dynamic_weather_track_evolution,
    plot_bayesian_intervals,
    plot_dynamic_weather,
    plot_season_twin,
    plot_strategy_agent,
    race_engineer_recommendations,
    season_digital_twin,
    strategy_policy_agent,
)
from src.f1predictor.fastf1_real_replay import load_fastf1_session_summary

st.set_page_config(page_title="Decision Intelligence Center", layout="wide")
st.title("🔥 F1 Decision Intelligence Center")
st.caption("Real replay adapter, race engineer recommendations, Bayesian uncertainty, dynamic weather, season digital twin and strategy policy agent.")

RACES_2026 = ["British Grand Prix 2026", "Belgian Grand Prix 2026", "Italian Grand Prix 2026", "Singapore Grand Prix 2026", "Monaco Grand Prix 2026"]

@st.cache_data(show_spinner=True)
def build_state(race_name: str, laps: int, rain: float, seed: int):
    result = forecast_future_race(history_df=build_demo_dataset(), race_name=race_name, year=2026, round_no=12, n_simulations=2500, noise_std=2.0, use_2026_grid=True)
    replay = lap_by_lap_race_simulation(result["forecast"], total_laps=laps, rain_probability=rain, random_state=seed)
    weather = dynamic_weather_track_evolution(laps, rain, seed)
    return result, replay, weather

with st.sidebar:
    st.header("Controls")
    race_name = st.selectbox("Forecast race", RACES_2026)
    laps = st.slider("Race laps", 10, 78, 53)
    rain = st.slider("Rain probability", 0.0, 1.0, 0.25, step=0.05)
    seed = st.number_input("Seed", 1, 99999, 42)

forecast_result, replay, weather_df = build_state(race_name, int(laps), float(rain), int(seed))
forecast = forecast_result["forecast"]
simulation = forecast_result["simulation"]
timeline = replay["timeline"]

fastf1_tab, engineer_tab, bayes_tab, weather_tab, twin_tab, agent_tab = st.tabs([
    "🏎 Real FastF1 Replay",
    "🧠 AI Race Engineer",
    "🎯 Bayesian Forecasting",
    "🌦 Dynamic Weather",
    "🏁 Season Digital Twin",
    "🔥 Strategy Agent",
])

with fastf1_tab:
    st.markdown("## Real FastF1 Session Loader")
    c1, c2, c3 = st.columns(3)
    year = c1.number_input("Year", 2018, 2026, 2024)
    gp = c2.text_input("Grand Prix / round", "Monaco")
    session_name = c3.selectbox("Session", ["R", "Q", "S", "SQ", "FP1", "FP2", "FP3"])
    if st.button("Load real FastF1 session", type="primary"):
        real = load_fastf1_session_summary(int(year), gp, session_name)
        st.info(real["status"])
        if not real["laps"].empty:
            st.dataframe(real["laps"].head(500), use_container_width=True, hide_index=True)
        if not real["results"].empty:
            st.dataframe(real["results"], use_container_width=True)
    st.caption("If FastF1 or network/cache access is unavailable, this panel fails gracefully and the rest of the platform still runs.")

with engineer_tab:
    st.markdown("## AI Race Engineer")
    lap = st.slider("Engineer lap", 1, int(laps), min(20, int(laps)))
    recs = race_engineer_recommendations(timeline, weather_df, lap)
    st.dataframe(recs, use_container_width=True, hide_index=True)
    if not recs.empty:
        top = recs.iloc[0]
        st.success(f"Recommendation: {top['Driver']} — {top['Recommendation']} | Expected gain: {top['ExpectedGain']}s")
        st.write(top["Reason"])

with bayes_tab:
    st.markdown("## Bayesian Forecasting")
    intervals = bayesian_forecast_intervals(simulation)
    st.dataframe(intervals[[c for c in ["Driver", "Team", "ExpectedFinish", "WinProbability", "PodiumProbability", "CredibleInterval", "UncertaintyIndex"] if c in intervals.columns]], use_container_width=True, hide_index=True)
    st.plotly_chart(plot_bayesian_intervals(intervals), use_container_width=True)

with weather_tab:
    st.markdown("## Dynamic Weather Engine")
    st.plotly_chart(plot_dynamic_weather(weather_df), use_container_width=True)
    st.dataframe(weather_df, use_container_width=True, hide_index=True)

with twin_tab:
    st.markdown("## Season Digital Twin")
    races_remaining = st.slider("Races remaining", 1, 24, 12)
    twin = season_digital_twin(simulation, races_remaining=int(races_remaining), seed=int(seed))
    st.dataframe(twin, use_container_width=True, hide_index=True)
    st.plotly_chart(plot_season_twin(twin), use_container_width=True)

with agent_tab:
    st.markdown("## Strategy Policy Agent")
    drivers = sorted(timeline["Driver"].unique())
    driver = st.selectbox("Driver", drivers)
    agent_df = strategy_policy_agent(timeline, weather_df, driver, seed=int(seed))
    st.plotly_chart(plot_strategy_agent(agent_df), use_container_width=True)
    st.dataframe(agent_df, use_container_width=True, hide_index=True)
    st.markdown("## Analyst Explanation")
    st.code(analyst_explanation(forecast, simulation, driver))
