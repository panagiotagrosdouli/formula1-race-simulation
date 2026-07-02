"""F1 Base44 Elite Streamlit entrypoint.

Run with:
    streamlit run app/f1_analytics_platform.py
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.ui.cards import driver_prediction_card, feed_line, kpi_card, panel
from app.ui.charts import plotly_chart
from app.ui.layout import hero, page_caption, section_header
from app.ui.navigation import Workspace, sidebar_workspace_selector
from app.ui.theme import TOKENS, inject_theme
from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.live_broadcast import (
    build_weather_radar,
    detect_drs_and_overtake_alerts,
    generate_team_radio,
    plot_track_map_animation,
    plot_weather_radar,
)
from src.f1predictor.product_intelligence import (
    build_storylines,
    prepare_driver_cards,
    race_brief_markdown,
    shareable_summary,
    uncertainty_table,
)
from src.f1predictor.race_analyst import generate_race_report
from src.f1predictor.simulation import lap_by_lap_race_simulation
from src.f1predictor.visualization import plot_probabilities


RACES_2026 = [
    "Australian Grand Prix 2026", "Chinese Grand Prix 2026", "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026", "Saudi Arabian Grand Prix 2026", "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026", "Canadian Grand Prix 2026", "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026", "British Grand Prix 2026", "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026", "Italian Grand Prix 2026", "Singapore Grand Prix 2026",
    "United States Grand Prix 2026", "Mexico City Grand Prix 2026", "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026", "Qatar Grand Prix 2026", "Abu Dhabi Grand Prix 2026",
]

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = TOKENS.palette

st.set_page_config(
    page_title="F1 Base44 Elite",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()


@st.cache_data(show_spinner=False)
def demo_data() -> pd.DataFrame:
    """Load the demo/historical dataset once for Streamlit."""

    return build_demo_dataset()


@st.cache_data(show_spinner=True)
def build_state(race_name: str, total_laps: int, pit_loss: float, rain_probability: float, seed: int) -> dict:
    """Build the complete race-intelligence state used by the UI."""

    forecast_result = forecast_future_race(
        history_df=demo_data(),
        race_name=race_name,
        year=2026,
        round_no=12,
        n_simulations=2500,
        noise_std=2.0,
        use_2026_grid=True,
    )
    forecast = forecast_result["forecast"]
    simulation = forecast_result["simulation"]
    weather = forecast_result["weather"]
    replay = lap_by_lap_race_simulation(
        forecast,
        total_laps=total_laps,
        pit_loss=pit_loss,
        rain_probability=rain_probability,
        random_state=seed,
    )
    timeline = replay["timeline"]
    alerts = detect_drs_and_overtake_alerts(timeline)
    radar = build_weather_radar(timeline, base_rain_probability=rain_probability)
    radio = generate_team_radio(timeline, replay["pitstops"], alerts)
    report = generate_race_report(forecast=forecast, simulation=simulation, weather=weather)
    cards = prepare_driver_cards(forecast, simulation, limit=8)
    storylines = build_storylines(forecast, simulation, rain_probability=rain_probability)
    share = shareable_summary(race_name, cards, storylines)
    assumptions = {
        "Race distance": f"{total_laps} laps",
        "Pit-lane loss": f"{pit_loss:.1f}s",
        "Rain probability": f"{rain_probability * 100:.1f}%",
        "Simulation seed": seed,
        "Monte Carlo runs": "2500",
    }

    return {
        "forecast": forecast,
        "sim": simulation,
        "weather": weather,
        "timeline": timeline,
        "alerts": alerts,
        "radar": radar,
        "radio": radio,
        "report": report,
        "driver_cards": cards,
        "storylines": storylines,
        "shareable": share,
        "race_brief": race_brief_markdown(race_name, cards, storylines, assumptions),
        "uncertainty": uncertainty_table(simulation),
        **replay,
    }


def render_sidebar() -> tuple[Workspace, str, str, int, float, float, int, bool]:
    """Render controls and return their values."""

    with st.sidebar:
        st.header("F1 Command Center")
        workspace = sidebar_workspace_selector(default_key="overview")
        st.divider()
        mode = st.radio("Experience mode", ["Fan Mode", "Engineer Mode"], horizontal=False)
        selected_race = st.selectbox("Grand Prix", RACES_2026, index=11)
        laps = st.slider("Race distance", 10, 78, 53)
        loss = st.slider("Pit-lane loss", 15.0, 35.0, 22.5, step=0.5)
        rain = st.slider("Rain probability", 0.0, 1.0, 0.20, step=0.05)
        random_seed = st.number_input("Simulation seed", min_value=1, max_value=99999, value=42)
        rebuild_state = st.button("Build race simulation", type="primary")
        st.caption("Fan Mode simplifies the story. Engineer Mode exposes assumptions, tables and uncertainty diagnostics.")
    return workspace, mode, selected_race, int(laps), float(loss), float(rain), int(random_seed), rebuild_state


def render_overview(state: dict, race_name: str, lap: int, total_laps: int, leader: str, grip: str) -> None:
    """Render the executive overview workspace."""

    section_header("Command overview", "A product-style summary of race state, model output and narrative hooks.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Grand Prix", race_name.replace(" Grand Prix 2026", ""), "2026 simulation")
    with c2:
        kpi_card("Current lap", f"{lap}/{total_laps}", "live race state")
    with c3:
        kpi_card("Race leader", str(leader), "track position P1")
    with c4:
        kpi_card("Track grip", grip, "weather-adjusted")

    panel("Race intelligence brief", state["report"])
    section_header("Top storylines")
    for item in state["storylines"][:3]:
        feed_line(item.title, f"{item.driver}: {item.detail}")


def render_fan_hub(state: dict) -> None:
    """Render the fan-facing prediction hub."""

    section_header("Driver prediction cards", "Fan-readable forecasts with probability and a plain-language explanation.")
    cards = state["driver_cards"]
    if cards.empty:
        st.info("No driver-card data available yet.")
    else:
        for row_df in [cards.iloc[i:i + 4] for i in range(0, len(cards), 4)]:
            cols = st.columns(4)
            for col, (_, card_row) in zip(cols, row_df.iterrows()):
                with col:
                    driver_prediction_card(card_row)

    section_header("Race storylines")
    for item in state["storylines"]:
        feed_line(item.title, f"{item.driver}: {item.detail}")

    section_header("Shareable prediction summary")
    st.text_area("Copy this for social posts, reports or messages", state["shareable"], height=110)
    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            "Download short summary",
            data=state["shareable"].encode("utf-8"),
            file_name="f1_prediction_summary.txt",
            mime="text/plain",
        )
    with col_b:
        st.download_button(
            "Download full race brief",
            data=state["race_brief"].encode("utf-8"),
            file_name="f1_base44_race_brief.md",
            mime="text/markdown",
        )


def render_race_control(state: dict, lap_df: pd.DataFrame, timeline: pd.DataFrame) -> None:
    """Render race-control classification and track map."""

    left, right = st.columns([1, 1.25])
    with left:
        section_header("Live Classification")
        cols = [c for c in ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "PitStops"] if c in lap_df.columns]
        st.dataframe(lap_df[cols].head(15), use_container_width=True, hide_index=True)
    with right:
        section_header("Track Map")
        plotly_chart(plot_track_map_animation(timeline))

    section_header("Monte Carlo Win Probability")
    sim = state["sim"].head(10)
    if "WinProbability" in sim.columns:
        plotly_chart(plot_probabilities(sim, "WinProbability"))


def render_strategy(lap_df: pd.DataFrame, lap_radio: pd.DataFrame, lap: int) -> None:
    """Render strategy and radio panels."""

    s1, s2 = st.columns([1, 1])
    with s1:
        section_header("Race pace gap")
        plotly_chart(
            px.bar(
                lap_df.sort_values("RacePosition"),
                x="Driver",
                y="GapToLeader",
                color="Compound",
                title=f"Gap to leader — lap {lap}",
                hover_data=["Team", "RacePosition", "PitStops"],
            )
        )
    with s2:
        section_header("Team Radio")
        if lap_radio.empty:
            feed_line("RADIO", "No team-radio message on this lap.")
        else:
            for _, row in lap_radio.head(8).iterrows():
                feed_line(str(row.get("Driver", "RADIO")), f"{row.get('Channel', 'Race Engineer')}: {row.get('Message', '')}")


def render_weather(radar: pd.DataFrame, lap_alerts: pd.DataFrame, lap: int) -> None:
    """Render weather radar and race alerts."""

    w1, w2 = st.columns([1.2, 1])
    with w1:
        section_header("Weather Radar")
        plotly_chart(plot_weather_radar(radar[radar["Lap"] <= lap]))
    with w2:
        section_header("DRS / Overtake Alerts")
        if lap_alerts.empty:
            feed_line("DRS", "No active DRS or overtake alert.")
        else:
            for _, row in lap_alerts.head(10).iterrows():
                feed_line(str(row.get("Type", "ALERT")), str(row.get("Message", "")))


def render_engineer_mode(state: dict, view_mode: str, rain_probability: float, pit_loss: float) -> None:
    """Render engineer-facing diagnostics and assumptions."""

    if view_mode != "Engineer Mode":
        st.info("Switch the sidebar to Engineer Mode for the deeper diagnostic view. The data is shown here anyway for transparency.")

    e1, e2 = st.columns(2)
    with e1:
        section_header("Forecast table")
        forecast_cols = [
            c
            for c in ["PredictedRank", "Driver", "Team", "PredictedFinishPosition", "GridPosition", "DNFRisk", "SafetyCarProbability", "RiskAdjustment"]
            if c in state["forecast"].columns
        ]
        st.dataframe(state["forecast"][forecast_cols], use_container_width=True, hide_index=True)
    with e2:
        section_header("Uncertainty diagnostics")
        st.dataframe(state["uncertainty"], use_container_width=True, hide_index=True)

    section_header("Simulation assumptions")
    feed_line("Monte Carlo", "Race probabilities come from simulation around a model forecast, not from guaranteed outcomes.")
    feed_line("Weather", f"Rain probability is set to {rain_probability * 100:.1f}% and affects chaos/strategy interpretation.")
    feed_line("Pit loss", f"Pit-lane loss is assumed to be {pit_loss:.1f}s. Strategy conclusions change if this assumption changes.")
    feed_line("Limitations", "FastF1/weather availability, future driver form, upgrades and incidents can all invalidate a clean pre-race forecast.")

    section_header("Final classification")
    st.dataframe(state["final_order"], use_container_width=True, hide_index=True)


def render_workspace(
    workspace: Workspace,
    state: dict,
    race_name: str,
    lap: int,
    total_laps: int,
    leader: str,
    grip: str,
    lap_df: pd.DataFrame,
    timeline: pd.DataFrame,
    radar: pd.DataFrame,
    lap_alerts: pd.DataFrame,
    lap_radio: pd.DataFrame,
    view_mode: str,
    rain_probability: float,
    pit_loss: float,
) -> None:
    """Render the selected product workspace."""

    if workspace.key == "overview":
        render_overview(state, race_name, lap, total_laps, leader, grip)
    elif workspace.key == "fan":
        render_fan_hub(state)
    elif workspace.key == "race":
        render_race_control(state, lap_df, timeline)
    elif workspace.key == "strategy":
        render_strategy(lap_df, lap_radio, lap)
    elif workspace.key == "weather":
        render_weather(radar, lap_alerts, lap)
    elif workspace.key == "engineer":
        render_engineer_mode(state, view_mode, rain_probability, pit_loss)
    else:
        render_overview(state, race_name, lap, total_laps, leader, grip)


def main() -> None:
    """Render the F1 Base44 Elite application."""

    workspace, view_mode, race_name, total_laps, pit_loss, rain_probability, seed, rebuild = render_sidebar()

    if rebuild or "base44_state" not in st.session_state:
        with st.spinner("Building premium race intelligence workspace..."):
            st.session_state["base44_state"] = build_state(race_name, total_laps, pit_loss, rain_probability, seed)
            st.session_state["base44_lap"] = 1

    state = st.session_state["base44_state"]
    timeline = state["timeline"]
    radar = state["radar"]
    alerts = state["alerts"]
    radio = state["radio"]

    hero(
        title="F1 Base44 Elite Race Engineering",
        body=(
            "A polished Formula 1 analytics workspace for beautiful race predictions, race drama, "
            "strategy intelligence, weather chaos, team radio, and engineer-grade uncertainty diagnostics."
        ),
        badges=[workspace.label, "Fan Mode", "Engineer Mode", "Driver Cards", "Shareable Predictions"],
    )

    lap = st.slider("Race timeline", 1, int(total_laps), int(st.session_state.get("base44_lap", 1)))
    st.session_state["base44_lap"] = lap
    lap_df = timeline[timeline["Lap"] == lap].sort_values("RacePosition")
    lap_radar = radar[radar["Lap"] == lap]
    lap_alerts = alerts[alerts["Lap"] == lap] if not alerts.empty else pd.DataFrame()
    lap_radio = radio[radio["Lap"] == lap] if not radio.empty else pd.DataFrame()
    leader = lap_df.iloc[0]["Driver"] if not lap_df.empty else "N/A"
    grip = f"{float(lap_radar.iloc[0]['TrackGrip']) * 100:.0f}%" if not lap_radar.empty else "N/A"

    render_workspace(
        workspace=workspace,
        state=state,
        race_name=race_name,
        lap=lap,
        total_laps=total_laps,
        leader=str(leader),
        grip=grip,
        lap_df=lap_df,
        timeline=timeline,
        radar=radar,
        lap_alerts=lap_alerts,
        lap_radio=lap_radio,
        view_mode=view_mode,
        rain_probability=rain_probability,
        pit_loss=pit_loss,
    )

    page_caption("Base44 Elite Live Build • estimates, not guarantees • main/app/f1_analytics_platform.py")


main()
