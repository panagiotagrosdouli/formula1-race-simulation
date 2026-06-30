import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.append(str(ROOT))

from app.components.theme import card, hero, inject_theme, metric_card
from f1predictor.telemetry.telemetry_dashboard import (
    TelemetryRequest,
    load_fastf1_telemetry,
    make_controls_trace,
    make_delta_trace,
    make_speed_trace,
    make_track_map,
)

st.set_page_config(page_title="Telemetry Workstation", layout="wide")
inject_theme()

hero(
    eyebrow="FastF1 telemetry comparison",
    title="Telemetry Workstation",
    body=(
        "Compare two drivers through speed, delta, control inputs, and track-position traces. "
        "The workspace keeps the existing FastF1-powered logic while presenting telemetry as an engineering workflow."
    ),
)

with st.sidebar:
    st.header("Telemetry configuration")
    year = st.number_input("Year", 2018, 2026, 2024)
    grand_prix = st.text_input("Grand Prix", "Monza")
    session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3", "S"], index=0)
    driver_a = st.text_input("Driver A", "VER").upper()
    driver_b = st.text_input("Driver B", "LEC").upper()
    execute = st.button("Load telemetry", type="primary")

st.markdown("## Analysis workflow")
w1, w2, w3 = st.columns(3)
with w1:
    card("Driver comparison", "Load two driver laps from a selected event and session for direct telemetry comparison.")
with w2:
    card("Performance traces", "Review speed and delta traces to identify where lap time is gained or lost.")
with w3:
    card("Control behaviour", "Inspect throttle, brake, and track-position views to understand driving style differences.")

if not execute:
    st.info("Configure the session and drivers in the sidebar, then load telemetry.")
    st.stop()

req = TelemetryRequest(
    year=int(year),
    grand_prix=grand_prix,
    session_type=session_type,
    driver_a=driver_a,
    driver_b=driver_b,
)

with st.spinner("Loading telemetry data..."):
    tel_a, tel_b, source = load_fastf1_telemetry(req)

s1, s2, s3, s4 = st.columns(4)
with s1:
    metric_card("Data source", str(source), "FastF1 or offline fallback")
with s2:
    metric_card("Driver A", driver_a, "Primary trace")
with s3:
    metric_card("Driver B", driver_b, "Comparison trace")
with s4:
    metric_card("Session", f"{year} {grand_prix} {session_type}", "Telemetry context")

speed_tab, delta_tab, controls_tab, map_tab, notes_tab = st.tabs(
    ["Speed trace", "Delta trace", "Control inputs", "Track map", "Engineering notes"]
)

with speed_tab:
    st.plotly_chart(make_speed_trace(tel_a, tel_b, driver_a, driver_b), use_container_width=True)

with delta_tab:
    st.plotly_chart(make_delta_trace(tel_a, tel_b, driver_a, driver_b), use_container_width=True)

with controls_tab:
    st.plotly_chart(make_controls_trace(tel_a, driver_a), use_container_width=True)
    st.caption("Control trace currently uses Driver A. Future work can extend this to synchronized dual-driver throttle/brake overlays.")

with map_tab:
    st.plotly_chart(make_track_map(tel_a, driver_a), use_container_width=True)

with notes_tab:
    st.markdown("### Engineering interpretation")
    st.write(
        "Use speed and delta traces together: a driver can show higher peak speed while still losing time through braking, "
        "corner minimum speed, traction, or exit performance. Control traces help identify whether the difference is caused "
        "by earlier braking, throttle application, or a different line through the lap."
    )
    st.markdown("### Data limitation")
    st.write(
        "FastF1 availability depends on event/session support and network/cache state. When live data is unavailable, "
        "the app can use fallback data for demonstration, but real engineering conclusions should only be made from real telemetry."
    )
