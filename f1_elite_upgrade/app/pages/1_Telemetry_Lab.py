from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import streamlit as st
from f1predictor.telemetry.telemetry_dashboard import (
    TelemetryRequest,
    load_fastf1_telemetry,
    make_controls_trace,
    make_delta_trace,
    make_speed_trace,
    make_track_map,
)
from theme import apply_theme, chart, hero, panel, section_header, status_cards

st.set_page_config(page_title="Telemetry Lab", page_icon="F1", layout="wide")
apply_theme()

hero(
    "F1 Telemetry Workstation",
    "MoTeC-style driver comparison using FastF1 telemetry when available, with an offline demo fallback. Diagnose where lap time is gained through speed, delta, controls and track position.",
    ["FastF1", "Speed", "Delta", "Throttle", "Brake", "Track map"],
)

controls, workstation = st.columns([0.28, 0.72])
with controls:
    section_header("Session", "Telemetry controls", "Select public-data session metadata and driver pair.")
    year = st.number_input("Year", 2018, 2026, 2024)
    grand_prix = st.text_input("Grand Prix", "Monza")
    session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3", "S"], index=0)
    driver_a = st.text_input("Driver A", "VER").upper()
    driver_b = st.text_input("Driver B", "LEC").upper()
    panel("Driver codes", "Use official three-letter driver abbreviations such as VER, LEC, NOR or PIA. FastF1 is optional; offline fallback remains labelled.")

req = TelemetryRequest(year=int(year), grand_prix=grand_prix, session_type=session_type, driver_a=driver_a, driver_b=driver_b)
with st.spinner("Loading telemetry and building comparison traces..."):
    tel_a, tel_b, source = load_fastf1_telemetry(req)

source_label = "Real FastF1 data" if "fastf1" in str(source).lower() else "Offline demo fallback"

with workstation:
    status_cards(
        [
            ("Driver A", driver_a, "Reference trace."),
            ("Driver B", driver_b, "Comparison trace."),
            ("Session", f"{year} {session_type}", grand_prix),
            ("Source", source_label, "Public telemetry or labelled demo fallback."),
        ]
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Speed and delta", "Controls", "Track position", "Engineering readout"])
    with tab1:
        section_header("Pace", "Speed trace and lap-time delta", "Find the distance ranges where the lap is won or lost.")
        left, right = st.columns(2)
        with left:
            chart(make_speed_trace(tel_a, tel_b, driver_a, driver_b))
        with right:
            chart(make_delta_trace(tel_a, tel_b, driver_a, driver_b))
    with tab2:
        section_header("Inputs", "Driver control traces", "Inspect throttle, brake, gear and input consistency for the reference driver.")
        c1, c2 = st.columns(2)
        with c1:
            chart(make_controls_trace(tel_a, driver_a))
        with c2:
            chart(make_controls_trace(tel_b, driver_b))
    with tab3:
        section_header("Map", "Track-position analysis", "Connect speed and control differences to circuit position.")
        c1, c2 = st.columns(2)
        with c1:
            chart(make_track_map(tel_a, driver_a))
        with c2:
            chart(make_track_map(tel_b, driver_b))
    with tab4:
        panel(
            "How to read this workstation",
            "Start with the delta trace, identify the largest divergence, then inspect speed and controls around that distance. Use the track map to translate the delta into corner or straight-line behaviour.",
        )
        panel(
            "Data limitation",
            "FastF1 provides public timing-derived telemetry where available. This page does not include private team channels such as tyre carcass temperature, live fuel targets or proprietary setup data.",
        )
