from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel

st.set_page_config(page_title="Team Database", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Team Database",
    "Prototype constructor intelligence layer for reliability, pit operations, upgrade signal, tyre usage and strategy aggressiveness.",
    ["Constructors", "Reliability", "Pit crew", "Strategy"],
)

teams = pd.DataFrame(
    [
        ["McLaren", 94, 91, 90, 87, 44.0],
        ["Ferrari", 91, 88, 92, 84, 39.5],
        ["Red Bull", 90, 90, 85, 88, 36.0],
        ["Mercedes", 89, 86, 84, 82, 32.4],
        ["Aston Martin", 84, 82, 78, 76, 15.8],
        ["Williams", 80, 79, 77, 74, 12.6],
    ],
    columns=["Team", "Reliability", "Pit crew", "Upgrade signal", "Strategy index", "Projected points"],
)

team = st.selectbox("Constructor", teams["Team"].tolist())
row = teams[teams["Team"] == team].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Reliability", int(row["Reliability"]))
c2.metric("Pit crew", int(row["Pit crew"]))
c3.metric("Upgrade signal", int(row["Upgrade signal"]))
c4.metric("Projected points", f"{row['Projected points']:.1f}")

chart(px.bar(teams, x="Team", y=["Reliability", "Pit crew", "Upgrade signal", "Strategy index"], title="Constructor operating indices"))
st.dataframe(teams, use_container_width=True, hide_index=True)
panel("Data status", "These constructor scores are prototype indicators for interface design. They must be calibrated from public race data before analytical use.")
