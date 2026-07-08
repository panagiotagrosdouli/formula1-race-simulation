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

from theme import apply_theme, chart, hero, panel, section_header, status_cards
from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Race Control", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Race Control",
    "Timing-wall race intelligence for position order, gaps, last lap, best lap, tyre state, pit events, weather state and safety-car exposure from reproducible simulation scenarios.",
    ["Timing wall", "Position tower", "Gaps", "Tyres", "Pit wall"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))]
if not configs:
    st.error("No experiment configs found under configs/experiments.")
    st.stop()

control, main = st.columns([0.28, 0.72])
with control:
    section_header("Scenario", "Race weekend control", "Select a reproducible race scenario and deterministic seed.")
    config_path = st.selectbox("Race scenario", configs)
    seed = st.number_input("Deterministic seed", min_value=1, max_value=999999, value=42)
    config = load_race_config(REPO_ROOT / config_path).model_copy(update={"seed": int(seed)})
    panel("Data status", "Scenario inputs are reproducible YAML configurations. They are not official FIA race-control or team data.")

result = RaceSimulation(config).run()
frame = pd.DataFrame(result.lap_history)
leader = result.classification[0]
lead_time = result.classification[0].total_time_s
latest_lap = frame["lap"].max()
latest = frame[frame["lap"] == latest_lap].copy()

last_laps = latest.set_index("driver_id")["lap_time_s"].to_dict()
best_laps = frame.groupby("driver_id")["lap_time_s"].min().to_dict()
tyres = latest.set_index("driver_id")["compound"].to_dict()
tyre_age = latest.set_index("driver_id")["tyre_age_laps"].to_dict()

with main:
    status_cards(
        [
            ("Leader", leader.driver_id, "Current projected race winner."),
            ("Race time", f"{leader.total_time_s:.1f}s", "Leader total simulated time."),
            ("Lap", f"{latest_lap}/{config.laps}", "Completed race distance in simulation."),
            ("Pit events", str(len(result.pit_events)), "Recorded stops across all drivers."),
        ]
    )

    left, right = st.columns([1.15, 0.85])
    with left:
        section_header("Timing", "Position tower", "Live-timing style classification with tyre and pace state.")
        timing = pd.DataFrame(
            [
                {
                    "POS": d.position,
                    "DRIVER": d.driver_id,
                    "TYRE": tyres.get(d.driver_id, d.compound),
                    "AGE": int(tyre_age.get(d.driver_id, 0)),
                    "GAP": "LEADER" if d.position == 1 else f"+{d.total_time_s - lead_time:.3f}",
                    "LAST": f"{last_laps.get(d.driver_id, 0):.3f}",
                    "BEST": f"{best_laps.get(d.driver_id, 0):.3f}",
                    "STOPS": d.pit_stops,
                    "STATUS": "RUNNING",
                }
                for d in result.classification
            ]
        )
        st.dataframe(timing, use_container_width=True, hide_index=True)
    with right:
        section_header("Pit wall", "Engineer alert", "Strategy interpretation from the current race state.")
        max_age = max(tyre_age.values()) if tyre_age else 0
        sc_laps = int(frame.groupby("lap")["safety_car"].max().sum()) if "safety_car" in frame else 0
        recommendation = "PIT WINDOW OPEN" if max_age >= 20 else "MONITOR TYRE LIFE"
        st.metric("Recommendation", recommendation)
        st.metric("Oldest tyre age", f"{max_age} laps")
        st.metric("SC/VSC exposure", f"{sc_laps} laps")
        panel("Race engineer note", "Compare undercut exposure against tyre age and post-stop traffic before committing to a stop. This recommendation is model-derived and not real team advice.")

    tabs = st.tabs(["Lap pace", "Position map", "Gap trace", "Tyre stints", "Race state", "Pit events"])
    with tabs[0]:
        chart(px.line(frame, x="lap", y="lap_time_s", color="driver_id", title="Lap-time evolution"))
    with tabs[1]:
        fig = px.line(frame, x="lap", y="position", color="driver_id", markers=True, title="Position tracking")
        fig.update_yaxes(autorange="reversed", dtick=1)
        chart(fig)
    with tabs[2]:
        chart(px.line(frame, x="lap", y="gap_to_leader_s", color="driver_id", title="Gap to leader"))
    with tabs[3]:
        chart(px.scatter(frame, x="lap", y="driver_id", color="compound", size="tyre_age_laps", title="Tyre stint timeline"))
    with tabs[4]:
        state = frame.groupby("lap", as_index=False).agg(wetness=("wetness", "mean"), safety_car=("safety_car", "max"), vsc=("vsc", "max"))
        chart(px.line(state, x="lap", y=["wetness", "safety_car", "vsc"], title="Race-state timeline"))
    with tabs[5]:
        pit_rows = [event.__dict__ for event in result.pit_events]
        st.dataframe(pd.DataFrame(pit_rows), use_container_width=True, hide_index=True)
