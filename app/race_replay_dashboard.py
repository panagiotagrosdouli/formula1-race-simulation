import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.race_grid_simulator import (
    plot_position_evolution,
    plot_starting_grid,
    plot_race_animation,
    simulate_lap_by_lap_order,
)
from src.f1predictor.simulation import lap_by_lap_race_simulation


st.set_page_config(page_title="F1 Race Replay Simulator", layout="wide")

st.title("🏁 F1 Race Replay Simulator")
st.write(
    "Lap-by-lap Formula 1 race simulation with starting grid, pit stops, tyre states, "
    "Safety Car/VSC/rain events, position evolution, and replay-style visualisation."
)

with st.sidebar:
    st.header("Race setup")
    race_name = st.selectbox(
        "Race",
        [
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
        ],
        index=11,
    )
    total_laps = st.slider("Race laps", 10, 78, 53)
    replay_laps = st.slider("Visual replay frames", 5, 60, 25)
    pit_loss = st.slider("Pit loss (seconds)", 15.0, 35.0, 22.5, step=0.5)
    rain_probability = st.slider("Rain probability", 0.0, 1.0, 0.20, step=0.05)
    random_state = st.number_input("Random seed", min_value=1, max_value=99999, value=42)

run_replay = st.button("Run race replay simulation", type="primary")

if run_replay:
    with st.spinner("Building forecast and running lap-by-lap race simulation..."):
        history_df = build_demo_dataset()
        forecast_result = forecast_future_race(
            history_df=history_df,
            race_name=race_name,
            year=2026,
            round_no=12,
            n_simulations=3000,
            noise_std=2.0,
            use_2026_grid=True,
        )
        forecast = forecast_result["forecast"]

        replay = lap_by_lap_race_simulation(
            forecast,
            total_laps=int(total_laps),
            pit_loss=float(pit_loss),
            rain_probability=float(rain_probability),
            random_state=int(random_state),
        )

        visual_replay = simulate_lap_by_lap_order(
            forecast,
            total_laps=int(replay_laps),
            random_state=int(random_state),
        )

    timeline = replay["timeline"]
    final_order = replay["final_order"]
    events = replay["events"]
    pitstops = replay["pitstops"]

    st.success("Race replay simulation completed.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Winner", final_order.iloc[0]["Driver"] if not final_order.empty else "N/A")
    c2.metric("Events", len(events))
    c3.metric("Pit stops", len(pitstops))
    c4.metric("DNFs", int(final_order["DNF"].sum()) if "DNF" in final_order else 0)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Starting grid",
            "Race replay",
            "Position evolution",
            "Final order",
            "Pit stops",
            "Event log",
        ]
    )

    with tab1:
        st.subheader("Starting grid")
        st.plotly_chart(plot_starting_grid(visual_replay.starting_grid), use_container_width=True)
        st.dataframe(visual_replay.starting_grid, use_container_width=True)

    with tab2:
        st.subheader("Virtual replay animation")
        st.plotly_chart(plot_race_animation(visual_replay), use_container_width=True)
        st.caption(
            "The replay animation is a visual abstraction of race order. The detailed state model is shown in the timeline, pit-stop, and event tables."
        )

    with tab3:
        st.subheader("Lap-by-lap position evolution")
        st.plotly_chart(plot_position_evolution(visual_replay), use_container_width=True)

        selected_driver = st.selectbox("Inspect driver", sorted(timeline["Driver"].unique()))
        driver_timeline = timeline[timeline["Driver"] == selected_driver]
        st.dataframe(driver_timeline, use_container_width=True)

        st.plotly_chart(
            px.line(
                driver_timeline,
                x="Lap",
                y="GapToLeader",
                color="Compound",
                title=f"{selected_driver} gap to leader and tyre compound",
            ),
            use_container_width=True,
        )

    with tab4:
        st.subheader("Final race order")
        final_cols = [
            "RacePosition",
            "Driver",
            "Team",
            "Compound",
            "TyreAge",
            "PitStops",
            "DNF",
            "GapToLeader",
        ]
        visible_cols = [c for c in final_cols if c in final_order.columns]
        st.dataframe(final_order[visible_cols], use_container_width=True)

        st.plotly_chart(
            px.bar(
                final_order.sort_values("RacePosition"),
                x="Driver",
                y="GapToLeader",
                hover_data=["Team", "Compound", "PitStops", "DNF"],
                title="Final gap to leader",
            ),
            use_container_width=True,
        )

    with tab5:
        st.subheader("Pit stop timeline")
        if pitstops.empty:
            st.info("No pit stops occurred in this simulation run.")
        else:
            st.dataframe(pitstops, use_container_width=True)
            st.plotly_chart(
                px.scatter(
                    pitstops,
                    x="Lap",
                    y="Driver",
                    color="NewCompound",
                    size="PitLoss",
                    hover_data=["OldCompound", "NewCompound", "PitLoss"],
                    title="Pit stop events",
                ),
                use_container_width=True,
            )

    with tab6:
        st.subheader("Race event log")
        if events.empty:
            st.info("No Safety Car, VSC, rain, or DNF events occurred in this simulation run.")
        else:
            st.dataframe(events, use_container_width=True)
            st.plotly_chart(
                px.histogram(events, x="Lap", color="Event", title="Race events by lap"),
                use_container_width=True,
            )

else:
    st.info("Configure the race and press 'Run race replay simulation'.")
