from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel

st.set_page_config(page_title="Driver Database", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Driver Database",
    "Prototype driver intelligence layer for pace, qualifying, tyre management, wet sensitivity and risk profiling.",
    ["Drivers", "Pace", "Tyres", "Risk"],
)

drivers = pd.DataFrame(
    [
        ["LEC", "Ferrari", 96, 94, 88, 82, "A"],
        ["NOR", "McLaren", 95, 92, 90, 84, "A"],
        ["VER", "Red Bull", 97, 95, 91, 88, "A"],
        ["PIA", "McLaren", 92, 90, 87, 78, "B"],
        ["HAM", "Ferrari", 90, 89, 86, 93, "B"],
        ["RUS", "Mercedes", 89, 91, 84, 82, "B"],
        ["ALO", "Aston Martin", 86, 85, 88, 90, "C"],
    ],
    columns=["Driver", "Team", "Race pace", "Qualifying", "Tyre management", "Wet index", "Risk tier"],
)

selected = st.selectbox("Driver", drivers["Driver"].tolist())
row = drivers[drivers["Driver"] == selected].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Race pace", int(row["Race pace"]))
c2.metric("Qualifying", int(row["Qualifying"]))
c3.metric("Tyre management", int(row["Tyre management"]))
c4.metric("Wet index", int(row["Wet index"]))

chart(px.bar(drivers, x="Driver", y=["Race pace", "Qualifying", "Tyre management", "Wet index"], title="Driver performance indices"))
st.dataframe(drivers, use_container_width=True, hide_index=True)
panel("Data status", "These indices are prototype placeholders for product design. Production use should be calibrated from public historical timing, weather and result data.")
