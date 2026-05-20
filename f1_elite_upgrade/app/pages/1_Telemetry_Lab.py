import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st
from f1predictor.telemetry.telemetry_dashboard import (
    TelemetryRequest,
    load_fastf1_telemetry,
    make_controls_trace,
    make_delta_trace,
    make_speed_trace,
    make_track_map,
)

st.set_page_config(page_title="Telemetry Lab", layout="wide")
st.title("F1 Telemetry Lab")
st.caption("FastF1-powered driver comparison with offline fallback for demos.")

with st.sidebar:
    year = st.number_input("Year", 2018, 2026, 2024)
    grand_prix = st.text_input("Grand Prix", "Monza")
    session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3", "S"], index=0)
    driver_a = st.text_input("Driver A", "VER").upper()
    driver_b = st.text_input("Driver B", "LEC").upper()

req = TelemetryRequest(year=int(year), grand_prix=grand_prix, session_type=session_type, driver_a=driver_a, driver_b=driver_b)
tel_a, tel_b, source = load_fastf1_telemetry(req)
st.info(f"Telemetry source: {source}")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(make_speed_trace(tel_a, tel_b, driver_a, driver_b), width="stretch")
with col2:
    st.plotly_chart(make_delta_trace(tel_a, tel_b, driver_a, driver_b), width="stretch")

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(make_controls_trace(tel_a, driver_a), width="stretch")
with col4:
    st.plotly_chart(make_track_map(tel_a, driver_a), width="stretch")
