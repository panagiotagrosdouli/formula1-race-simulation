from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel
from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Race Control", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Race Control",
    "Live-timing style race intelligence: position order, gaps, lap-time evolution, tyre stints, pit events, weather state and safety-car exposure from reproducible simulation scenarios.",
    ["Timing wall", "Gaps", "Pit stops", "Tyres", "Weather"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))]
if not configs:
    st.error("No experiment configs found under configs/experiments.")
    st.stop()

col_a, col_b = st.columns([0.35, 0.65])
with col_a:
    config_path = st.selectbox("Race scenario", configs)
    seed = st.number_input("Deterministic seed", min_value=1, max_value=999999, value=42)
    config = load_race_config(REPO_ROOT / config_path).model_copy(update={"seed": int(seed)})
    st.metric("Race distance", f"{config.laps} laps")
    st.metric("Pit loss", f"{config.pit_loss_s:.1f}s")
    st.metric("Track temp", f"{config.track_temp_c:.1f} C")
    panel("Data status", "Scenario inputs are reproducible YAML configurations. They are not official race-control data.")

result = RaceSimulation(config).run()
frame = pd.DataFrame(result.lap_history)
leader = result.classification[0]

with col_b:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Leader", leader.driver_id)
    k2.metric("Race time", f"{leader.total_time_s:.3f}s")
    k3.metric("Leader pit stops", leader.pit_stops)
    k4.metric("Traffic loss", f"{leader.traffic_loss_s:.2f}s")

    tabs = st.tabs(["Timing wall", "Lap pace", "Position map", "Gap trace", "Tyre stints", "Pit events"])
    with tabs[0]:
        lead_time = result.classification[0].total_time_s
        table = pd.DataFrame([
            {"Pos": d.position, "Driver": d.driver_id, "Gap [s]": round(d.total_time_s - lead_time, 3), "Stops": d.pit_stops, "Tyre": d.compound}
            for d in result.classification
        ])
        st.dataframe(table, use_container_width=True, hide_index=True)
    with tabs[1]:
        chart(px.line(frame, x="lap", y="lap_time_s", color="driver_id", title="Lap-time evolution"))
    with tabs[2]:
        fig = px.line(frame, x="lap", y="position", color="driver_id", markers=True, title="Position tracking")
        fig.update_yaxes(autorange="reversed", dtick=1)
        chart(fig)
    with tabs[3]:
        chart(px.line(frame, x="lap", y="gap_to_leader_s", color="driver_id", title="Gap to leader"))
    with tabs[4]:
        chart(px.scatter(frame, x="lap", y="driver_id", color="compound", size="tyre_age_laps", title="Tyre stint timeline"))
    with tabs[5]:
        pit_rows = [event.__dict__ for event in result.pit_events]
        st.dataframe(pd.DataFrame(pit_rows), use_container_width=True, hide_index=True)
