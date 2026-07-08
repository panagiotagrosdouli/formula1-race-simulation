from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel

st.set_page_config(page_title="Fantasy Roster Manager", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Fantasy Roster Manager",
    "Prototype roster and budget workspace: driver market values, constructor selection, 100M budget cap, projected points and contract mechanics scaffold.",
    ["Roster", "Budget", "Contracts", "Market"],
)

drivers = pd.DataFrame(
    [
        ["LEC", "Ferrari", 24.2, 31.4, 1.8, "3 races"],
        ["NOR", "McLaren", 23.6, 29.7, 1.4, "Race-by-race"],
        ["VER", "Red Bull", 28.5, 28.9, -0.2, "6 races"],
        ["PIA", "McLaren", 21.8, 23.8, 0.9, "3 races"],
        ["HAM", "Ferrari", 20.5, 19.2, -0.5, "Race-by-race"],
        ["RUS", "Mercedes", 18.9, 18.4, 0.3, "3 races"],
        ["ALO", "Aston Martin", 13.4, 11.8, 0.1, "Race-by-race"],
        ["SAI", "Williams", 15.0, 13.6, 0.6, "Race-by-race"],
    ],
    columns=["Driver", "Team", "Value", "Projected points", "Trend", "Contract"],
)
constructors = pd.DataFrame(
    [
        ["McLaren", 27.0, 44.0, 0.94],
        ["Ferrari", 25.5, 39.5, 0.91],
        ["Red Bull", 26.8, 36.0, 0.90],
        ["Mercedes", 22.2, 32.4, 0.89],
        ["Aston Martin", 12.5, 15.8, 0.84],
    ],
    columns=["Constructor", "Value", "Projected points", "Reliability"],
)

selected = st.multiselect("Select exactly 5 drivers", drivers["Driver"].tolist(), default=["LEC", "NOR", "PIA", "RUS", "SAI"])
constructor = st.selectbox("Constructor", constructors["Constructor"].tolist())

cost = drivers.loc[drivers["Driver"].isin(selected), "Value"].sum() + float(constructors.loc[constructors["Constructor"] == constructor, "Value"].iloc[0])
points = drivers.loc[drivers["Driver"].isin(selected), "Projected points"].sum() + float(constructors.loc[constructors["Constructor"] == constructor, "Projected points"].iloc[0])
remaining = 100.0 - float(cost)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Roster cost", f"{cost:.1f}M")
c2.metric("Budget left", f"{remaining:.1f}M")
c3.metric("Drivers", f"{len(selected)}/5")
c4.metric("Projected points", f"{points:.1f}")

if len(selected) != 5 or remaining < 0:
    st.error("Roster invalid: select 5 drivers and stay under the 100M cap.")
else:
    st.success("Roster valid under prototype 100M cost cap.")

chart(px.scatter(drivers, x="Value", y="Projected points", color="Team", size="Trend", hover_name="Driver", title="Driver market value versus projected points"))
st.subheader("Driver market")
st.dataframe(drivers, use_container_width=True, hide_index=True)
st.subheader("Constructor market")
st.dataframe(constructors, use_container_width=True, hide_index=True)
panel("Data status", "This is a fantasy-management prototype. Official F1 Fantasy data requires authorized integration and is not included here.")
