import sys
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.data_loader import build_demo_dataset
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
from src.f1predictor.simulation import lap_by_lap_race_simulation


st.set_page_config(page_title="Live F1 Race Simulation", layout="wide")

st.title("🔴 Live F1 Race Simulation")
st.write(
    "Interactive lap-by-lap race simulation with live leaderboard, race-control events, "
    "track-map animation, DRS alerts, sector timing, weather radar, team radio, and TV commentary."
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


def build_replay(race_name, total_laps, pit_loss, rain_probability, seed):
    history_df = build_demo_dataset()
    forecast_result = forecast_future_race(
        history_df=history_df,
        race_name=race_name,
        year=2026,
        round_no=12,
        n_simulations=2000,
        noise_std=2.0,
        use_2026_grid=True,
    )
    forecast = forecast_result["forecast"]
    replay = lap_by_lap_race_simulation(
        forecast,
        total_laps=int(total_laps),
        pit_loss=float(pit_loss),
        rain_probability=float(rain_probability),
        random_state=int(seed),
    )
    return forecast, replay


def render_lap(lap_number, timeline, events, pitstops, total_laps, sectors, alerts, radio, commentary, weather_radar):
    lap_df = timeline[timeline["Lap"] == lap_number].sort_values("RacePosition")
    lap_events = events[events["Lap"] == lap_number] if not events.empty and "Lap" in events else pd.DataFrame()
    lap_pits = pitstops[pitstops["Lap"] == lap_number] if not pitstops.empty and "Lap" in pitstops else pd.DataFrame()
    lap_alerts = alerts[alerts["Lap"] == lap_number] if not alerts.empty and "Lap" in alerts else pd.DataFrame()
    lap_radio = radio[radio["Lap"] == lap_number] if not radio.empty and "Lap" in radio else pd.DataFrame()
    lap_commentary = commentary[commentary["Lap"] == lap_number] if not commentary.empty and "Lap" in commentary else pd.DataFrame()
    lap_sectors = sectors[sectors["Lap"] == lap_number].sort_values("RacePosition") if not sectors.empty else pd.DataFrame()
    lap_weather = weather_radar[weather_radar["Lap"] == lap_number] if not weather_radar.empty else pd.DataFrame()

    progress = lap_number / max(total_laps, 1)
    st.progress(progress, text=f"Lap {lap_number}/{total_laps}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Leader", lap_df.iloc[0]["Driver"] if not lap_df.empty else "N/A")
    c2.metric("Race Control", ", ".join(lap_events["Event"].astype(str).unique()) if not lap_events.empty else "GREEN")
    c3.metric("Pit stops", len(lap_pits))
    c4.metric("DRS/Overtake alerts", len(lap_alerts))
    if not lap_weather.empty:
        c5.metric("Track grip", f"{float(lap_weather.iloc[0]['TrackGrip']) * 100:.0f}%")
    else:
        c5.metric("Track grip", "N/A")

    main_tab, timing_tab, radio_tab, broadcast_tab = st.tabs(
        ["Live timing", "Sectors / DRS / Weather", "Team radio", "TV broadcast"]
    )

    with main_tab:
        left, right = st.columns([1.15, 0.85])
        with left:
            st.subheader("Live leaderboard")
            visible_cols = ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "TyreAge", "PitStops", "DNF"]
            visible_cols = [c for c in visible_cols if c in lap_df.columns]
            st.dataframe(lap_df[visible_cols], use_container_width=True, hide_index=True)

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
        with right:
            st.subheader("Race control")
            if lap_events.empty:
                st.success("GREEN FLAG")
            else:
                for _, event in lap_events.iterrows():
                    driver = f" — {event.get('Driver')}" if "Driver" in event and pd.notna(event.get("Driver")) else ""
                    st.warning(f"Lap {lap_number}: {event['Event']}{driver}")

            st.subheader("Pit wall")
            if lap_pits.empty:
                st.info("No pit stops this lap.")
            else:
                st.dataframe(lap_pits, use_container_width=True, hide_index=True)

            st.subheader("Tyre overview")
            tyre_count = lap_df.groupby("Compound", as_index=False).size().rename(columns={"size": "Cars"})
            st.plotly_chart(px.pie(tyre_count, names="Compound", values="Cars", title="Compounds in use"), use_container_width=True)

    with timing_tab:
        left, right = st.columns(2)
        with left:
            st.subheader("Sector timing")
            sector_cols = ["RacePosition", "Driver", "S1", "S2", "S3", "EstimatedLapTime", "GapToLeader"]
            sector_cols = [c for c in sector_cols if c in lap_sectors.columns]
            st.dataframe(lap_sectors[sector_cols], use_container_width=True, hide_index=True)

            if not lap_sectors.empty:
                st.plotly_chart(
                    px.bar(
                        lap_sectors.head(10),
                        x="Driver",
                        y=["S1", "S2", "S3"],
                        title=f"Top 10 sector split estimate — Lap {lap_number}",
                    ),
                    use_container_width=True,
                )
        with right:
            st.subheader("DRS / Overtake center")
            if lap_alerts.empty:
                st.info("No DRS or overtake alerts this lap.")
            else:
                st.dataframe(lap_alerts, use_container_width=True, hide_index=True)

            st.subheader("Weather radar")
            if not weather_radar.empty:
                st.plotly_chart(plot_weather_radar(weather_radar[weather_radar["Lap"] <= lap_number]), use_container_width=True)

    with radio_tab:
        st.subheader("Team radio feed")
        if lap_radio.empty:
            st.info("No team-radio messages this lap.")
        else:
            for _, msg in lap_radio.iterrows():
                st.write(f"**{msg['Driver']} | {msg['Channel']}**: {msg['Message']}")

        st.subheader("All radio up to current lap")
        radio_so_far = radio[radio["Lap"] <= lap_number] if not radio.empty else pd.DataFrame()
        if radio_so_far.empty:
            st.info("No radio messages yet.")
        else:
            st.dataframe(radio_so_far.tail(25), use_container_width=True, hide_index=True)

    with broadcast_tab:
        st.subheader("Virtual TV broadcast")
        if lap_commentary.empty:
            st.info("No commentary this lap.")
        else:
            for _, line in lap_commentary.iterrows():
                st.write(f"📺 {line['Commentary']}")

        st.subheader("Broadcast feed up to current lap")
        commentary_so_far = commentary[commentary["Lap"] <= lap_number] if not commentary.empty else pd.DataFrame()
        if commentary_so_far.empty:
            st.info("No broadcast lines yet.")
        else:
            st.dataframe(commentary_so_far.tail(30), use_container_width=True, hide_index=True)


with st.sidebar:
    st.header("Simulation controls")
    race_name = st.selectbox("Race", RACES, index=11)
    total_laps = st.slider("Total laps", 10, 78, 53)
    pit_loss = st.slider("Pit loss (seconds)", 15.0, 35.0, 22.5, step=0.5)
    rain_probability = st.slider("Rain probability", 0.0, 1.0, 0.20, step=0.05)
    seed = st.number_input("Random seed", min_value=1, max_value=99999, value=42)
    playback_delay = st.slider("Playback delay per lap (seconds)", 0.0, 2.0, 0.25, step=0.05)

    st.divider()
    build_button = st.button("Build simulation", type="primary")
    reset_button = st.button("Reset session")

if reset_button:
    for key in [
        "live_timeline",
        "live_events",
        "live_pitstops",
        "live_final",
        "live_total_laps",
        "live_lap",
        "live_sectors",
        "live_alerts",
        "live_radio",
        "live_commentary",
        "live_weather_radar",
    ]:
        st.session_state.pop(key, None)
    st.rerun()

if build_button:
    with st.spinner("Generating race forecast, simulation timeline, and broadcast layer..."):
        forecast, replay = build_replay(race_name, total_laps, pit_loss, rain_probability, seed)
        timeline = replay["timeline"]
        events = replay["events"]
        pitstops = replay["pitstops"]
        sectors = estimate_sector_times(timeline)
        alerts = detect_drs_and_overtake_alerts(timeline)
        weather_radar = build_weather_radar(timeline, base_rain_probability=float(rain_probability))
        radio = generate_team_radio(timeline, pitstops, alerts)
        commentary = generate_tv_commentary(timeline, alerts, pitstops)

    st.session_state["live_forecast"] = forecast
    st.session_state["live_timeline"] = timeline
    st.session_state["live_events"] = events
    st.session_state["live_pitstops"] = pitstops
    st.session_state["live_final"] = replay["final_order"]
    st.session_state["live_total_laps"] = int(total_laps)
    st.session_state["live_lap"] = 1
    st.session_state["live_sectors"] = sectors
    st.session_state["live_alerts"] = alerts
    st.session_state["live_weather_radar"] = weather_radar
    st.session_state["live_radio"] = radio
    st.session_state["live_commentary"] = commentary
    st.success("Simulation built. Use the controls below to play the race.")

if "live_timeline" not in st.session_state:
    st.info("Build a simulation from the sidebar to start the live race view.")
else:
    timeline = st.session_state["live_timeline"]
    events = st.session_state["live_events"]
    pitstops = st.session_state["live_pitstops"]
    final_order = st.session_state["live_final"]
    total = int(st.session_state["live_total_laps"])
    sectors = st.session_state["live_sectors"]
    alerts = st.session_state["live_alerts"]
    weather_radar = st.session_state["live_weather_radar"]
    radio = st.session_state["live_radio"]
    commentary = st.session_state["live_commentary"]

    control_cols = st.columns([1, 1, 1, 2])
    with control_cols[0]:
        if st.button("⏮ Lap 1"):
            st.session_state["live_lap"] = 1
    with control_cols[1]:
        if st.button("◀ Previous"):
            st.session_state["live_lap"] = max(1, int(st.session_state["live_lap"]) - 1)
    with control_cols[2]:
        if st.button("Next ▶"):
            st.session_state["live_lap"] = min(total, int(st.session_state["live_lap"]) + 1)
    with control_cols[3]:
        selected_lap = st.slider("Manual lap selector", 1, total, int(st.session_state["live_lap"]))
        st.session_state["live_lap"] = int(selected_lap)

    auto_cols = st.columns([1, 1, 3])
    with auto_cols[0]:
        autoplay = st.button("▶ Play full race")
    with auto_cols[1]:
        finish_now = st.button("🏁 Jump to finish")

    if finish_now:
        st.session_state["live_lap"] = total

    if autoplay:
        live_slot = st.empty()
        start_lap = int(st.session_state["live_lap"])
        for lap in range(start_lap, total + 1):
            st.session_state["live_lap"] = lap
            with live_slot.container():
                render_lap(lap, timeline, events, pitstops, total, sectors, alerts, radio, commentary, weather_radar)
            time.sleep(float(playback_delay))
        st.rerun()

    current_lap = int(st.session_state["live_lap"])
    render_lap(current_lap, timeline, events, pitstops, total, sectors, alerts, radio, commentary, weather_radar)

    st.divider()
    st.subheader("🗺️ Full track map animation")
    st.plotly_chart(plot_track_map_animation(timeline), use_container_width=True)

    st.subheader("Final classification preview")
    final_cols = ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "TyreAge", "PitStops", "DNF"]
    final_cols = [c for c in final_cols if c in final_order.columns]
    st.dataframe(final_order[final_cols], use_container_width=True, hide_index=True)

    log_tab1, log_tab2, log_tab3, log_tab4 = st.tabs(["Event log", "Pit stop log", "DRS/overtake log", "Broadcast datasets"])

    with log_tab1:
        if events.empty:
            st.info("No race-control events were generated in this run.")
        else:
            st.dataframe(events, use_container_width=True, hide_index=True)
    with log_tab2:
        if pitstops.empty:
            st.info("No pit stops were generated in this run.")
        else:
            st.dataframe(pitstops, use_container_width=True, hide_index=True)
    with log_tab3:
        if alerts.empty:
            st.info("No DRS or overtake alerts were generated in this run.")
        else:
            st.dataframe(alerts, use_container_width=True, hide_index=True)
    with log_tab4:
        st.write("Sector timing")
        st.dataframe(sectors, use_container_width=True, hide_index=True)
        st.write("Weather radar")
        st.dataframe(weather_radar, use_container_width=True, hide_index=True)
