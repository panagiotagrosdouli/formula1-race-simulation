from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from theme import apply_theme, chart, hero, panel, section_header, status_cards
from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Race Replay Studio", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Race Replay Studio",
    "Replay-style race visualization with timing wall, driver positions, tyre compounds, pit events, weather state and safety-car markers. This is a platform-native replay cockpit, not a copy of another project.",
    ["Replay", "Track map", "Timing wall", "Tyres", "Safety car"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))]
if not configs:
    st.error("No experiment configs found under configs/experiments.")
    st.stop()

controls, replay = st.columns([0.28, 0.72])
with controls:
    section_header("Replay", "Session controls", "Select a scenario and scrub through simulated race laps.")
    config_path = st.selectbox("Race scenario", configs)
    seed = st.number_input("Seed", min_value=1, max_value=999999, value=42)
    speed = st.select_slider("Playback speed", options=["0.5x", "1x", "2x", "4x"], value="1x")
    show_names = st.toggle("Show driver labels", value=True)
    show_drs = st.toggle("Show DRS zones", value=True)
    panel("Replay data", "The track replay uses simulated lap-progress positions derived from race simulation outputs. Public GPS-style telemetry can be connected in a later phase where data access allows it.")

config = load_race_config(REPO_ROOT / config_path).model_copy(update={"seed": int(seed)})
result = RaceSimulation(config).run()
frame = pd.DataFrame(result.lap_history)
max_lap = int(frame["lap"].max())
selected_lap = st.slider("Replay lap", 1, max_lap, min(12, max_lap))
current = frame[frame["lap"] == selected_lap].copy()

leader_time = current["total_time_s"].min()
current["gap_s"] = current["total_time_s"] - leader_time
current = current.sort_values("total_time_s").reset_index(drop=True)
current["position"] = current.index + 1

# Synthetic circuit path for replay visualization. It is deterministic and clearly labelled.
track_points = []
for i in range(220):
    t = 2 * math.pi * i / 220
    radius_x = 1.0 + 0.18 * math.sin(3 * t)
    radius_y = 0.62 + 0.10 * math.cos(2 * t)
    track_points.append((radius_x * math.cos(t), radius_y * math.sin(t)))
track = pd.DataFrame(track_points, columns=["x", "y"])

car_rows = []
for idx, row in current.iterrows():
    gap_fraction = float(row["gap_s"]) / max(float(current["gap_s"].max()) + 1.0, 1.0)
    progress = (selected_lap - 1 + 0.82 - 0.12 * gap_fraction - idx * 0.012) % 1.0
    point_index = int(progress * (len(track) - 1))
    x, y = track.iloc[point_index][["x", "y"]]
    car_rows.append(
        {
            "Driver": row["driver_id"],
            "Position": int(row["position"]),
            "x": x,
            "y": y,
            "Tyre": row["compound"],
            "Age": int(row["tyre_age_laps"]),
            "Gap": "LEADER" if idx == 0 else f"+{row['gap_s']:.3f}",
            "Last lap": f"{row['lap_time_s']:.3f}",
            "Safety car": bool(row.get("safety_car", False)),
            "VSC": bool(row.get("vsc", False)),
        }
    )
cars = pd.DataFrame(car_rows)

with replay:
    sc_active = bool(current["safety_car"].max()) if "safety_car" in current else False
    vsc_active = bool(current["vsc"].max()) if "vsc" in current else False
    status_cards(
        [
            ("Lap", f"{selected_lap}/{max_lap}", f"Playback speed {speed}."),
            ("Leader", str(cars.iloc[0]["Driver"]), "Current simulated race leader."),
            ("Track status", "SC" if sc_active else "VSC" if vsc_active else "GREEN", "Neutralisation state from model."),
            ("Weather", f"Wetness {current['wetness'].mean():.2f}", "Track wetness from weather model."),
        ]
    )

    left, right = st.columns([1.18, 0.82])
    with left:
        section_header("Replay", "Circuit visualizer", "Cars are positioned by simulated lap progress and gap. This view becomes real-data ready when public positional data is connected.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=track["x"], y=track["y"], mode="lines", name="Track", line={"width": 9, "color": "rgba(255,255,255,0.30)"}, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=track["x"], y=track["y"], mode="lines", name="Racing line", line={"width": 2, "color": "rgba(225,6,0,0.85)"}, hoverinfo="skip"))
        if show_drs:
            drs = track.iloc[22:56]
            fig.add_trace(go.Scatter(x=drs["x"], y=drs["y"], mode="lines", name="DRS zone", line={"width": 5, "color": "rgba(34,197,94,0.85)"}, hoverinfo="skip"))
        fig.add_trace(
            go.Scatter(
                x=cars["x"],
                y=cars["y"],
                mode="markers+text" if show_names else "markers",
                text=cars["Driver"] if show_names else None,
                textposition="top center",
                marker={"size": 15, "color": cars["Position"], "colorscale": "Turbo", "line": {"width": 2, "color": "white"}},
                customdata=cars[["Position", "Driver", "Tyre", "Age", "Gap", "Last lap"]],
                hovertemplate="P%{customdata[0]} %{customdata[1]}<br>Tyre %{customdata[2]} age %{customdata[3]}<br>Gap %{customdata[4]}<br>Last %{customdata[5]}<extra></extra>",
                name="Drivers",
            )
        )
        fig.update_yaxes(scaleanchor="x", scaleratio=1, visible=False)
        fig.update_xaxes(visible=False)
        fig.update_layout(height=560, showlegend=True, title="Replay circuit view")
        chart(fig)
    with right:
        section_header("Timing", "Live leaderboard", "Replay timing wall for current lap.")
        timing = cars[["Position", "Driver", "Tyre", "Age", "Gap", "Last lap"]].copy()
        st.dataframe(timing, use_container_width=True, hide_index=True)
        if sc_active:
            panel("Safety car", "Safety-car state is active in this replay frame. Pit-loss and race pace are neutralised by the simulation model.")
        elif vsc_active:
            panel("Virtual safety car", "VSC state is active in this replay frame. Strategy calls should consider reduced pit-loss exposure.")
        else:
            panel("Green flag", "Race is running under normal simulated conditions. Strategy focus shifts to tyre age, traffic and gap evolution.")

    tabs = st.tabs(["Gap history", "Lap pace", "Tyre state", "Pit events"])
    with tabs[0]:
        chart(go.Figure(data=[go.Scatter(x=frame[frame["driver_id"] == driver]["lap"], y=frame[frame["driver_id"] == driver]["gap_to_leader_s"], mode="lines", name=driver) for driver in frame["driver_id"].unique()]).update_layout(title="Gap history"))
    with tabs[1]:
        chart(go.Figure(data=[go.Scatter(x=frame[frame["driver_id"] == driver]["lap"], y=frame[frame["driver_id"] == driver]["lap_time_s"], mode="lines", name=driver) for driver in frame["driver_id"].unique()]).update_layout(title="Lap pace history"))
    with tabs[2]:
        st.dataframe(current[["driver_id", "compound", "tyre_age_laps", "lap_time_s", "gap_to_leader_s"]], use_container_width=True, hide_index=True)
    with tabs[3]:
        pit_rows = [event.__dict__ for event in result.pit_events]
        st.dataframe(pd.DataFrame(pit_rows), use_container_width=True, hide_index=True)
