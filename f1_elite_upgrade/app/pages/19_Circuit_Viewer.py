from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel, section_header, status_cards

st.set_page_config(page_title="Circuit Viewer", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Circuit Viewer",
    "Track-intelligence workspace for circuit profile, tyre stress, pit-loss exposure, overtaking, DRS zones, safety-car risk and weather sensitivity. Current profiles are prototype values ready for public-data calibration.",
    ["Track map", "DRS", "Pit loss", "Tyres", "SC risk"],
)

circuits = pd.DataFrame(
    [
        ["Bahrain", 57, 5.412, 15, 22.1, 86, 64, 0.32, 0.04, "Rear-limited traction"],
        ["Jeddah", 50, 6.174, 27, 20.4, 58, 72, 0.48, 0.03, "High-speed walls"],
        ["Melbourne", 58, 5.278, 14, 22.0, 66, 61, 0.39, 0.12, "Stop-start traction"],
        ["Monaco", 78, 3.337, 19, 19.5, 42, 12, 0.44, 0.18, "Track position critical"],
        ["Silverstone", 52, 5.891, 18, 23.1, 72, 70, 0.31, 0.28, "High lateral load"],
        ["Spa", 44, 7.004, 19, 21.4, 76, 74, 0.36, 0.35, "Weather volatility"],
        ["Monza", 53, 5.793, 11, 24.0, 52, 86, 0.26, 0.10, "Low drag efficiency"],
    ],
    columns=["Circuit", "Laps", "Length km", "Corners", "Pit loss", "Deg index", "Overtake index", "SC probability", "Rain exposure", "Strategy note"],
)

controls, body = st.columns([0.28, 0.72])
with controls:
    section_header("Circuit", "Track selector", "Choose a prototype circuit profile for strategy interpretation.")
    circuit = st.selectbox("Circuit", circuits["Circuit"].tolist(), index=4)
    show_sectors = st.toggle("Show sectors", value=True)
    show_drs = st.toggle("Show DRS zones", value=True)
    show_pit = st.toggle("Show pit entry/exit", value=True)
    panel("Profile source", "Values are prototype circuit indicators, not official FIA or team datasets. Calibrate with public historical data before factual use.")

row = circuits[circuits["Circuit"] == circuit].iloc[0]

# Deterministic stylized track shape per circuit name.
name_seed = sum(ord(ch) for ch in circuit)
points = []
for i in range(260):
    t = 2 * math.pi * i / 260
    radius_x = 1.0 + 0.12 * math.sin(2 * t + name_seed * 0.01) + 0.08 * math.sin(5 * t)
    radius_y = 0.62 + 0.10 * math.cos(3 * t + name_seed * 0.02)
    points.append((radius_x * math.cos(t), radius_y * math.sin(t)))
track = pd.DataFrame(points, columns=["x", "y"])

with body:
    status_cards(
        [
            ("Circuit", str(row["Circuit"]), f"{row['Length km']:.3f} km, {int(row['Corners'])} corners."),
            ("Pit loss", f"{row['Pit loss']:.1f}s", "Baseline green-flag stop loss."),
            ("Tyre stress", str(int(row["Deg index"])), "Prototype degradation pressure index."),
            ("SC risk", f"{row['SC probability']:.0%}", "Historical-style safety-car exposure scaffold."),
        ]
    )

    left, right = st.columns([1.18, 0.82])
    with left:
        section_header("Map", "Circuit intelligence view", "Stylized circuit map with DRS, sectors and pit-lane markers.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=track["x"], y=track["y"], mode="lines", name="Circuit", line={"width": 10, "color": "rgba(255,255,255,0.28)"}, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=track["x"], y=track["y"], mode="lines", name="Racing line", line={"width": 2, "color": "rgba(225,6,0,0.92)"}, hoverinfo="skip"))
        if show_drs:
            for start, stop, label in [(26, 58, "DRS 1"), (152, 188, "DRS 2")]:
                seg = track.iloc[start:stop]
                fig.add_trace(go.Scatter(x=seg["x"], y=seg["y"], mode="lines", name=label, line={"width": 5, "color": "rgba(34,197,94,0.9)"}, hoverinfo="skip"))
        if show_sectors:
            sector_points = track.iloc[[0, 86, 172]].copy()
            sector_points["Label"] = ["S1", "S2", "S3"]
            fig.add_trace(go.Scatter(x=sector_points["x"], y=sector_points["y"], mode="markers+text", text=sector_points["Label"], textposition="top center", marker={"size": 12, "color": "#38bdf8"}, name="Sectors"))
        if show_pit:
            pit = track.iloc[[238, 18]].copy()
            pit["Label"] = ["Pit entry", "Pit exit"]
            fig.add_trace(go.Scatter(x=pit["x"], y=pit["y"], mode="markers+text", text=pit["Label"], textposition="bottom center", marker={"size": 11, "color": "#facc15"}, name="Pit lane"))
        fig.update_yaxes(scaleanchor="x", scaleratio=1, visible=False)
        fig.update_xaxes(visible=False)
        fig.update_layout(height=560, title=f"{circuit} stylized circuit profile")
        chart(fig)
    with right:
        section_header("Strategy", "Circuit implications", "How the circuit profile affects race decisions.")
        st.metric("Overtake index", int(row["Overtake index"]))
        st.metric("Rain exposure", f"{row['Rain exposure']:.0%}")
        st.metric("Strategy note", str(row["Strategy note"]))
        panel("Race engineering readout", "High degradation shifts value toward extra stops; high pit loss protects one-stop strategies; high overtaking index improves recovery after stopping into traffic.")

    tabs = st.tabs(["Circuit table", "Strategy trade-offs", "Calibration plan"])
    with tabs[0]:
        st.dataframe(circuits, use_container_width=True, hide_index=True)
    with tabs[1]:
        chart(px.scatter(circuits, x="Deg index", y="Overtake index", size="SC probability", color="Rain exposure", hover_name="Circuit", title="Circuit strategy trade-off map"))
    with tabs[2]:
        calibration = pd.DataFrame(
            [
                ["Pit loss", "Public timing + pit-in/pit-out deltas", "Prototype"],
                ["Degradation", "Long-run lap-time slope by compound", "Prototype"],
                ["SC probability", "Historical race neutralisations", "Planned"],
                ["Weather exposure", "Public weather history", "Planned"],
                ["DRS/overtaking", "Pass counts and speed-trap deltas", "Planned"],
            ],
            columns=["Feature", "Calibration source", "Status"],
        )
        st.dataframe(calibration, use_container_width=True, hide_index=True)
