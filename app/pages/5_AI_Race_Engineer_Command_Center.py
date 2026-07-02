"""AI Race Engineer Command Center page."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.ui.cards import feed_line, kpi_card, panel
from app.ui.engineer import render_ai_engineer_console
from app.ui.layout import hero, page_caption, section_header
from app.ui.theme import inject_theme

st.set_page_config(page_title="AI Race Engineer", page_icon="🤖", layout="wide")
inject_theme()

hero(
    title="AI Race Engineer Command Center",
    body=(
        "A premium motorsport decision-support console for race pressure, weather risk, traffic, pit-loss assumptions, "
        "team-radio context and transparent strategic recommendations."
    ),
    badges=["Decision Support", "Strategy Risk", "Weather Chaos", "Race Control", "Simulation Only"],
)

with st.sidebar:
    st.header("Engineer Console")
    lap = st.slider("Current lap", 1, 78, 24)
    total_laps = st.slider("Total laps", 30, 78, 53)
    leader = st.text_input("Current leader", "LEC").upper()
    grip = st.slider("Track grip", 50, 100, 86)
    rain_probability = st.slider("Rain probability", 0.0, 1.0, 0.20, 0.05)
    pit_loss = st.slider("Pit-lane loss", 15.0, 35.0, 22.5, 0.5)
    alert_count = st.slider("Active DRS/overtake alerts", 0, 6, 1)
    radio_message = st.text_input("Latest radio message", "Tyres are stable, keep managing phase one.")

lap_alerts = pd.DataFrame(
    [{"Lap": lap, "Type": "DRS", "Message": f"Pressure window active around lap {lap}."} for _ in range(alert_count)]
)
lap_radio = pd.DataFrame(
    [{"Lap": lap, "Driver": leader, "Channel": "Race Engineer", "Message": radio_message}]
    if radio_message.strip()
    else []
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    kpi_card("Lap", f"{lap}/{total_laps}", "current race phase")
with m2:
    kpi_card("Leader", leader, "track position P1")
with m3:
    kpi_card("Track grip", f"{grip}%", "surface confidence")
with m4:
    kpi_card("Rain risk", f"{rain_probability * 100:.0f}%", "weather volatility")

render_ai_engineer_console(
    lap=lap,
    total_laps=total_laps,
    leader=leader,
    grip=f"{grip}%",
    rain_probability=rain_probability,
    pit_loss=pit_loss,
    lap_alerts=lap_alerts,
    lap_radio=lap_radio,
)

section_header("Engineering interpretation")
left, right = st.columns([1, 1])
with left:
    panel(
        "What this console is doing",
        "It converts race progress, weather risk, traffic pressure and pit-loss assumptions into a readable pit-wall style recommendation. It is a decision-support layer, not an oracle.",
    )
with right:
    panel(
        "Scientific honesty",
        "The recommendation is based on simplified simulation signals. Real outcomes can change because of tyre degradation, traffic, reliability, safety cars, stewarding and team execution.",
    )

section_header("Race-control notes")
feed_line("MODEL", "Higher weather and traffic pressure increases strategic uncertainty.")
feed_line("PIT WALL", "Treat the output as a prompt for human review, not an automatic instruction.")
feed_line("NEXT", "Future upgrade: connect this page directly to the live simulation state and tyre degradation model.")

page_caption("AI Race Engineer Command Center • simulation decision support • estimates, not guarantees")
