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
from theme import apply_theme, chart, hero, panel

st.set_page_config(page_title="Telemetry Lab", page_icon="📡", layout="wide")
apply_theme()
hero(
    "📡 F1 Telemetry Lab",
    "Compare two drivers using FastF1 telemetry with an offline demo fallback. Use this page to explain where lap time is gained: speed trace, delta, inputs and track position.",
    ["FastF1", "Driver comparison", "Speed", "Controls"],
)

with st.sidebar:
    st.header("Telemetry controls")
    year = st.number_input("Year", 2018, 2026, 2024)
    grand_prix = st.text_input("Grand Prix", "Monza")
    session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3", "S"], index=0)
    driver_a = st.text_input("Driver A", "VER").upper()
    driver_b = st.text_input("Driver B", "LEC").upper()
    st.caption("Use official three-letter driver abbreviations, for example VER, LEC, NOR, PIA.")

req = TelemetryRequest(year=int(year), grand_prix=grand_prix, session_type=session_type, driver_a=driver_a, driver_b=driver_b)
with st.spinner("Loading telemetry and building comparison traces..."):
    tel_a, tel_b, source = load_fastf1_telemetry(req)

source_label = "Real FastF1 data" if "fastf1" in str(source).lower() else "Offline demo fallback"
col1, col2, col3, col4 = st.columns(4)
col1.metric("Driver A", driver_a)
col2.metric("Driver B", driver_b)
col3.metric("Session", f"{year} {session_type}")
col4.metric("Source", source_label)

panel(
    "How to read this page",
    "Start with the speed trace and delta trace to find lap-time differences, then use throttle/brake and the track map to connect the gap to driving behaviour.",
)

left, right = st.columns(2)
with left:
    st.subheader("Speed trace")
    chart(make_speed_trace(tel_a, tel_b, driver_a, driver_b))
with right:
    st.subheader("Lap-time delta")
    chart(make_delta_trace(tel_a, tel_b, driver_a, driver_b))

bottom_left, bottom_right = st.columns(2)
with bottom_left:
    st.subheader(f"{driver_a} controls")
    chart(make_controls_trace(tel_a, driver_a))
with bottom_right:
    st.subheader(f"{driver_a} track map")
    chart(make_track_map(tel_a, driver_a))
