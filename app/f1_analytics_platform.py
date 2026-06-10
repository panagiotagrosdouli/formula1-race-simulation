import sys
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.championship_probability import (
    calculate_constructor_title_probabilities,
    calculate_title_probabilities,
)
from src.f1predictor.config import PREDICTIONS_PATH, SIMULATION_PATH, TRAINING_DATA_PATH
from src.f1predictor.data_loader import build_demo_dataset, build_fastf1_dataset
from src.f1predictor.driver_animation import (
    driver_event_summary,
    plot_driver_position_animation,
    plot_driver_race_story,
    plot_single_driver_track_animation,
)
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.live_broadcast import (
    build_weather_radar,
    detect_drs_and_overtake_alerts,
    estimate_sector_times,
    generate_team_radio,
    generate_tv_commentary,
    plot_track_map_animation,
    plot_weather_radar,
)
from src.f1predictor.model import train_model
from src.f1predictor.race_analyst import generate_race_report
from src.f1predictor.race_grid_simulator import (
    plot_position_evolution,
    plot_race_animation,
    plot_starting_grid,
    simulate_lap_by_lap_order,
)
from src.f1predictor.season_simulator import simulate_2026_season
from src.f1predictor.simulation import lap_by_lap_race_simulation, monte_carlo_race
from src.f1predictor.telemetry.degradation_dashboard import (
    detect_tire_cliff,
    load_tire_degradation,
    plot_degradation,
)
from src.f1predictor.telemetry.streamlit_insights import (
    compare_driver_controls,
    compare_driver_speed_trace,
    load_fastest_lap_telemetry,
)
from src.f1predictor.visualization import plot_predicted_order, plot_probabilities


st.set_page_config(page_title="F1 AI Analytics Platform", layout="wide")

st.title("🏎️ F1 AI Analytics Platform")
st.write(
    "Unified Formula 1 forecasting, race simulation, telemetry, strategy, championship, "
    "live timing, broadcast, and race-control analytics platform."
)

RACES_2026 = [
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


@st.cache_data(show_spinner=False)
def cached_demo_dataset():
    return build_demo_dataset()


def build_full_race_state(race_name, total_laps, pit_loss, rain_probability, seed):
    history_df = cached_demo_dataset()
    result = forecast_future_race(
        history_df=history_df,
        race_name=race_name,
        year=2026,
        round_no=12,
        n_simulations=3000,
        noise_std=2.0,
        use_2026_grid=True,
    )
    forecast = result["forecast"]
    simulation = result["simulation"]
    weather = result["weather"]

    replay = lap_by_lap_race_simulation(
        forecast,
        total_laps=int(total_laps),
        pit_loss=float(pit_loss),
        rain_probability=float(rain_probability),
        random_state=int(seed),
    )

    timeline = replay["timeline"]
    pitstops = replay["pitstops"]
    sectors = estimate_sector_times(timeline)
    alerts = detect_drs_and_overtake_alerts(timeline)
    weather_radar = build_weather_radar(timeline, base_rain_probability=float(rain_probability))
    radio = generate_team_radio(timeline, pitstops, alerts)
    commentary = generate_tv_commentary(timeline, alerts, pitstops)
    visual_replay = simulate_lap_by_lap_order(forecast, total_laps=min(int(total_laps), 60), random_state=int(seed))

    return {
        "forecast": forecast,
        "simulation": simulation,
        "weather": weather,
        "timeline": timeline,
        "events": replay["events"],
        "pitstops": pitstops,
        "final_order": replay["final_order"],
        "sectors": sectors,
        "alerts": alerts,
        "weather_radar": weather_radar,
        "radio": radio,
        "commentary": commentary,
        "visual_replay": visual_replay,
    }


def render_lap_panel(state, lap_number, total_laps):
    timeline = state["timeline"]
    events = state["events"]
    pitstops = state["pitstops"]
    sectors = state["sectors"]
    alerts = state["alerts"]
    radio = state["radio"]
    commentary = state["commentary"]
    weather_radar = state["weather_radar"]

    lap_df = timeline[timeline["Lap"] == lap_number].sort_values("RacePosition")
    lap_events = events[events["Lap"] == lap_number] if not events.empty and "Lap" in events else pd.DataFrame()
    lap_pits = pitstops[pitstops["Lap"] == lap_number] if not pitstops.empty and "Lap" in pitstops else pd.DataFrame()
    lap_alerts = alerts[alerts["Lap"] == lap_number] if not alerts.empty and "Lap" in alerts else pd.DataFrame()
    lap_radio = radio[radio["Lap"] == lap_number] if not radio.empty and "Lap" in radio else pd.DataFrame()
    lap_commentary = commentary[commentary["Lap"] == lap_number] if not commentary.empty and "Lap" in commentary else pd.DataFrame()
    lap_sectors = sectors[sectors["Lap"] == lap_number].sort_values("RacePosition") if not sectors.empty else pd.DataFrame()
    lap_weather = weather_radar[weather_radar["Lap"] == lap_number] if not weather_radar.empty else pd.DataFrame()

    st.progress(lap_number / max(total_laps, 1), text=f"Lap {lap_number}/{total_laps}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Leader", lap_df.iloc[0]["Driver"] if not lap_df.empty else "N/A")
    c2.metric("Race Control", ", ".join(lap_events["Event"].astype(str).unique()) if not lap_events.empty else "GREEN")
    c3.metric("Pit stops", len(lap_pits))
    c4.metric("DRS/Overtake", len(lap_alerts))
    c5.metric("Track grip", f"{float(lap_weather.iloc[0]['TrackGrip']) * 100:.0f}%" if not lap_weather.empty else "N/A")

    t1, t2, t3, t4 = st.tabs(["Leaderboard", "Sectors / DRS / Weather", "Team Radio", "TV Broadcast"])

    with t1:
        cols = ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "TyreAge", "PitStops", "DNF"]
        cols = [c for c in cols if c in lap_df.columns]
        st.dataframe(lap_df[cols], use_container_width=True, hide_index=True)
        st.plotly_chart(
            px.bar(
                lap_df.sort_values("RacePosition"),
                x="Driver",
                y="GapToLeader",
                color="Compound",
                hover_data=["Team", "RacePosition", "TyreAge", "PitStops", "DNF"],
                title=f"Gap to leader — Lap {lap_number}",
            ),
            use_container_width=True,
        )

    with t2:
        left, right = st.columns(2)
        with left:
            sector_cols = ["RacePosition", "Driver", "S1", "S2", "S3", "EstimatedLapTime", "GapToLeader"]
            sector_cols = [c for c in sector_cols if c in lap_sectors.columns]
            st.dataframe(lap_sectors[sector_cols], use_container_width=True, hide_index=True)
            if not lap_sectors.empty:
                st.plotly_chart(
                    px.bar(lap_sectors.head(10), x="Driver", y=["S1", "S2", "S3"], title="Sector timing estimate"),
                    use_container_width=True,
                )
        with right:
            st.subheader("DRS / Overtake alerts")
            if lap_alerts.empty:
                st.info("No alerts this lap.")
            else:
                st.dataframe(lap_alerts, use_container_width=True, hide_index=True)
            st.plotly_chart(plot_weather_radar(weather_radar[weather_radar["Lap"] <= lap_number]), use_container_width=True)

    with t3:
        if lap_radio.empty:
            st.info("No radio messages this lap.")
        else:
            for _, msg in lap_radio.iterrows():
                st.write(f"**{msg['Driver']} | {msg['Channel']}**: {msg['Message']}")
        radio_so_far = radio[radio["Lap"] <= lap_number] if not radio.empty else pd.DataFrame()
        if not radio_so_far.empty:
            st.dataframe(radio_so_far.tail(25), use_container_width=True, hide_index=True)

    with t4:
        if lap_commentary.empty:
            st.info("No broadcast line this lap.")
        else:
            for _, line in lap_commentary.iterrows():
                st.write(f"📺 {line['Commentary']}")
        commentary_so_far = commentary[commentary["Lap"] <= lap_number] if not commentary.empty else pd.DataFrame()
        if not commentary_so_far.empty:
            st.dataframe(commentary_so_far.tail(30), use_container_width=True, hide_index=True)


with st.sidebar:
    st.header("Global simulation controls")
    race_name = st.selectbox("Race", RACES_2026, index=11)
    total_laps = st.slider("Total laps", 10, 78, 53)
    pit_loss = st.slider("Pit loss (seconds)", 15.0, 35.0, 22.5, step=0.5)
    rain_probability = st.slider("Rain probability", 0.0, 1.0, 0.20, step=0.05)
    seed = st.number_input("Random seed", min_value=1, max_value=99999, value=42)
    n_simulations = st.slider("Monte Carlo simulations", 1000, 50000, 10000, step=1000)
    noise_std = st.slider("Race uncertainty", 0.5, 5.0, 2.0, step=0.1)

    st.divider()
    build_full = st.button("Build unified race state", type="primary")
    reset_full = st.button("Reset unified state")

if reset_full:
    for key in ["unified_state", "unified_lap"]:
        st.session_state.pop(key, None)
    st.rerun()

if build_full:
    with st.spinner("Building forecast, replay, timing, radio, weather radar, and broadcast layer..."):
        st.session_state["unified_state"] = build_full_race_state(race_name, total_laps, pit_loss, rain_probability, seed)
        st.session_state["unified_lap"] = 1
    st.success("Unified race state built.")

(
    overview_tab,
    forecasting_tab,
    championship_tab,
    live_tab,
    replay_tab,
    driver_tab,
    telemetry_tab,
    tyres_tab,
    training_tab,
    diagnostics_tab,
) = st.tabs(
    [
        "Overview",
        "Forecasting",
        "Championship",
        "Live Race Control",
        "Race Replay",
        "Driver Focus",
        "Telemetry",
        "Tyres",
        "FastF1 Training",
        "Diagnostics",
    ]
)

with overview_tab:
    st.subheader("Platform overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Forecasting", "ML + Monte Carlo")
    c2.metric("Live Race", "Lap-by-lap")
    c3.metric("Broadcast", "Radio + TV")
    c4.metric("Telemetry", "FastF1")

    st.write(
        "Use the sidebar to build a unified race state. Once built, the same race feeds all live timing, replay, driver focus, "
        "sector timing, DRS alerts, weather radar, team radio, and TV commentary views."
    )

    if "unified_state" in st.session_state:
        state = st.session_state["unified_state"]
        st.success("Unified race state is available.")
        st.subheader("Forecast snapshot")
        st.dataframe(state["forecast"].head(10), use_container_width=True, hide_index=True)
        st.subheader("Final classification preview")
        final_cols = ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "TyreAge", "PitStops", "DNF"]
        final_cols = [c for c in final_cols if c in state["final_order"].columns]
        st.dataframe(state["final_order"][final_cols], use_container_width=True, hide_index=True)
    else:
        st.info("Build the unified race state from the sidebar.")

with forecasting_tab:
    st.subheader("Race forecasting")
    if st.button("Run standalone future forecast"):
        result = forecast_future_race(
            history_df=cached_demo_dataset(),
            race_name=race_name,
            year=2026,
            round_no=12,
            n_simulations=n_simulations,
            noise_std=noise_std,
            use_2026_grid=True,
        )
        forecast = result["forecast"]
        sim = result["simulation"]
        weather = result["weather"]
        st.metric("Weather", weather.condition)
        st.info(generate_race_report(forecast=forecast, simulation=sim, weather=weather))
        st.dataframe(forecast, use_container_width=True, hide_index=True)
        st.plotly_chart(plot_predicted_order(forecast), use_container_width=True)
        st.dataframe(sim, use_container_width=True, hide_index=True)
        col1, col2, col3 = st.columns(3)
        col1.plotly_chart(plot_probabilities(sim, "WinProbability"), use_container_width=True)
        col2.plotly_chart(plot_probabilities(sim, "PodiumProbability"), use_container_width=True)
        col3.plotly_chart(plot_probabilities(sim, "Top10Probability"), use_container_width=True)
    elif "unified_state" in st.session_state:
        state = st.session_state["unified_state"]
        st.dataframe(state["forecast"], use_container_width=True, hide_index=True)
        st.plotly_chart(plot_predicted_order(state["forecast"]), use_container_width=True)
        st.dataframe(state["simulation"], use_container_width=True, hide_index=True)

with championship_tab:
    st.subheader("2026 championship simulator")
    season_runs = st.slider("Season simulations per race", 500, 10000, 3000, step=500)
    if st.button("Run championship simulation"):
        season = simulate_2026_season(history_df=cached_demo_dataset(), n_simulations=season_runs, noise_std=noise_std)
        driver_probs = calculate_title_probabilities(season["driver_standings"])
        constructor_probs = calculate_constructor_title_probabilities(season["constructor_standings"])
        st.subheader("Driver title probabilities")
        st.dataframe(driver_probs, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(driver_probs.head(10), x="Driver", y="ChampionshipProbability", hover_data=["Team", "ExpectedPoints"]), use_container_width=True)
        st.subheader("Constructor title probabilities")
        st.dataframe(constructor_probs, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(constructor_probs, x="Team", y="ChampionshipProbability", hover_data=["ConstructorExpectedPoints"]), use_container_width=True)
        st.subheader("Race-by-race table")
        st.dataframe(season["driver_race_table"], use_container_width=True, hide_index=True)

with live_tab:
    st.subheader("Live Race Control")
    if "unified_state" not in st.session_state:
        st.info("Build the unified race state from the sidebar first.")
    else:
        state = st.session_state["unified_state"]
        total = int(total_laps)
        controls = st.columns([1, 1, 1, 2])
        with controls[0]:
            if st.button("⏮ Lap 1"):
                st.session_state["unified_lap"] = 1
        with controls[1]:
            if st.button("◀ Previous"):
                st.session_state["unified_lap"] = max(1, int(st.session_state.get("unified_lap", 1)) - 1)
        with controls[2]:
            if st.button("Next ▶"):
                st.session_state["unified_lap"] = min(total, int(st.session_state.get("unified_lap", 1)) + 1)
        with controls[3]:
            st.session_state["unified_lap"] = st.slider("Manual lap selector", 1, total, int(st.session_state.get("unified_lap", 1)))

        autoplay_cols = st.columns([1, 1, 3])
        with autoplay_cols[0]:
            autoplay = st.button("▶ Play race")
        with autoplay_cols[1]:
            finish = st.button("🏁 Finish")
        if finish:
            st.session_state["unified_lap"] = total
        if autoplay:
            slot = st.empty()
            for lap in range(int(st.session_state["unified_lap"]), total + 1):
                st.session_state["unified_lap"] = lap
                with slot.container():
                    render_lap_panel(state, lap, total)
                time.sleep(0.20)
            st.rerun()

        render_lap_panel(state, int(st.session_state.get("unified_lap", 1)), total)

with replay_tab:
    st.subheader("Race replay")
    if "unified_state" not in st.session_state:
        st.info("Build the unified race state from the sidebar first.")
    else:
        state = st.session_state["unified_state"]
        replay = state["visual_replay"]
        t1, t2, t3 = st.tabs(["Starting grid", "Track map", "Position evolution"])
        with t1:
            st.plotly_chart(plot_starting_grid(replay.starting_grid), use_container_width=True)
            st.dataframe(replay.starting_grid, use_container_width=True, hide_index=True)
        with t2:
            st.plotly_chart(plot_track_map_animation(state["timeline"]), use_container_width=True)
            st.plotly_chart(plot_race_animation(replay), use_container_width=True)
        with t3:
            st.plotly_chart(plot_position_evolution(replay), use_container_width=True)
            st.dataframe(state["timeline"], use_container_width=True, hide_index=True)

with driver_tab:
    st.subheader("Driver-focused animation")
    if "unified_state" not in st.session_state:
        st.info("Build the unified race state from the sidebar first.")
    else:
        state = st.session_state["unified_state"]
        drivers = sorted(state["timeline"]["Driver"].unique())
        selected_driver = st.selectbox("Driver", drivers)
        st.plotly_chart(plot_single_driver_track_animation(state["timeline"], selected_driver), use_container_width=True)
        st.plotly_chart(plot_driver_position_animation(state["timeline"], selected_driver), use_container_width=True)
        st.plotly_chart(plot_driver_race_story(state["timeline"], selected_driver), use_container_width=True)
        summary = driver_event_summary(state["timeline"], state["pitstops"], selected_driver)
        st.subheader("Driver event summary")
        st.dataframe(summary, use_container_width=True, hide_index=True)

with telemetry_tab:
    st.subheader("FastF1 telemetry insights")
    c1, c2, c3, c4 = st.columns(4)
    tel_year = c1.number_input("Telemetry year", min_value=2018, max_value=2026, value=2024)
    tel_gp = c2.text_input("Grand Prix", "Monza")
    tel_session = c3.selectbox("Session", ["Q", "R", "S", "SQ"], index=0)
    tel_channel = c4.selectbox("Extra channel", ["Throttle", "Brake", "nGear", "DRS", "RPM"], index=0)
    d1, d2 = st.columns(2)
    driver_a = d1.text_input("Driver A", "VER").upper()
    driver_b = d2.text_input("Driver B", "LEC").upper()
    if st.button("Compare telemetry"):
        try:
            with st.spinner("Loading FastF1 telemetry..."):
                telemetry_a = load_fastest_lap_telemetry(int(tel_year), tel_gp, tel_session, driver_a)
                telemetry_b = load_fastest_lap_telemetry(int(tel_year), tel_gp, tel_session, driver_b)
            st.plotly_chart(compare_driver_speed_trace(telemetry_a, telemetry_b), use_container_width=True)
            st.plotly_chart(compare_driver_controls(telemetry_a, telemetry_b, tel_channel), use_container_width=True)
        except Exception as exc:
            st.error(str(exc))

with tyres_tab:
    st.subheader("Tyre degradation analytics")
    c1, c2, c3, c4 = st.columns(4)
    deg_year = c1.number_input("Degradation year", min_value=2018, max_value=2026, value=2024)
    deg_gp = c2.text_input("Degradation Grand Prix", "Monza")
    deg_session = c3.selectbox("Degradation session", ["R", "S"], index=0)
    deg_driver = c4.text_input("Degradation driver", "VER").upper()
    if st.button("Analyze tyre degradation"):
        try:
            result = load_tire_degradation(int(deg_year), deg_gp, deg_session, deg_driver)
            cliff = detect_tire_cliff(result)
            st.metric("Estimated degradation rate", f"{result.degradation_rate:.3f} s/lap")
            st.plotly_chart(plot_degradation(result), use_container_width=True)
            st.dataframe(result.compound_summary, use_container_width=True, hide_index=True)
            st.dataframe(cliff, use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(str(exc))

with training_tab:
    st.subheader("Real FastF1 training")
    year = st.number_input("Training year", min_value=2018, max_value=2026, value=2024)
    gp_text = st.text_input("Optional GP names separated by comma", "Bahrain, Saudi Arabia, Australia, Japan, China, Miami")
    if st.button("Build real FastF1 dataset + train"):
        gp_names = [x.strip() for x in gp_text.split(",") if x.strip()]
        try:
            with st.spinner("Downloading FastF1 data and training model..."):
                real_df = build_fastf1_dataset(int(year), grand_prix_names=gp_names)
                real_df.to_csv(TRAINING_DATA_PATH, index=False)
                model, metrics, predictions = train_model(real_df)
                sim = monte_carlo_race(predictions, n_simulations=n_simulations, noise_std=noise_std)
            st.json(metrics)
            st.dataframe(real_df, use_container_width=True, hide_index=True)
            st.dataframe(predictions, use_container_width=True, hide_index=True)
            st.dataframe(sim, use_container_width=True, hide_index=True)
        except RuntimeError as exc:
            st.error(str(exc))

with diagnostics_tab:
    st.subheader("Model diagnostics")
    if PREDICTIONS_PATH.exists():
        predictions = pd.read_csv(PREDICTIONS_PATH)
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", len(predictions))
        c2.metric("Grand Prix events", predictions["GrandPrix"].nunique() if "GrandPrix" in predictions else "N/A")
        c3.metric("Drivers", predictions["Driver"].nunique() if "Driver" in predictions else "N/A")
        numeric_cols = predictions.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            selected_metric = st.selectbox("Numeric feature distribution", numeric_cols)
            st.plotly_chart(px.histogram(predictions, x=selected_metric, title=f"Distribution of {selected_metric}"), use_container_width=True)
        st.dataframe(predictions, use_container_width=True, hide_index=True)
    else:
        st.info("Run forecasting or training first to generate prediction diagnostics.")

    if SIMULATION_PATH.exists():
        st.subheader("Latest Monte Carlo output")
        st.dataframe(pd.read_csv(SIMULATION_PATH), use_container_width=True, hide_index=True)
