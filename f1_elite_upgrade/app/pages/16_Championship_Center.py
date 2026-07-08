from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel, status_cards

st.set_page_config(page_title="Championship Center", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Championship Center",
    "Prototype title-probability and championship evolution workspace for driver and constructor scenarios.",
    ["Drivers", "Constructors", "Scenarios", "Probability"],
)

standings = pd.DataFrame(
    [
        ["LEC", "Ferrari", 252, 0.28, 0.72],
        ["NOR", "McLaren", 247, 0.25, 0.69],
        ["VER", "Red Bull", 239, 0.22, 0.65],
        ["PIA", "McLaren", 211, 0.14, 0.48],
        ["HAM", "Ferrari", 188, 0.07, 0.31],
        ["RUS", "Mercedes", 176, 0.04, 0.24],
    ],
    columns=["Driver", "Team", "Points", "Title probability", "Top 3 probability"],
)
constructors = pd.DataFrame(
    [
        ["McLaren", 458, 0.35],
        ["Ferrari", 440, 0.31],
        ["Red Bull", 352, 0.19],
        ["Mercedes", 326, 0.13],
        ["Aston Martin", 124, 0.02],
    ],
    columns=["Constructor", "Points", "Title probability"],
)

leader = standings.sort_values("Title probability", ascending=False).iloc[0]
constructor_leader = constructors.sort_values("Title probability", ascending=False).iloc[0]
status_cards(
    [
        ("Driver title favorite", str(leader["Driver"]), f"{leader['Title probability']:.0%} prototype probability."),
        ("Constructor favorite", str(constructor_leader["Constructor"]), f"{constructor_leader['Title probability']:.0%} prototype probability."),
        ("Remaining scenario mode", "Prototype", "Connect public race calendar and points model in Phase 2."),
        ("Data integrity", "Labelled", "Values are synthetic scenario examples."),
    ]
)

left, right = st.columns(2)
with left:
    chart(px.bar(standings, x="Driver", y="Points", color="Title probability", title="Driver championship board"))
    st.dataframe(standings, use_container_width=True, hide_index=True)
with right:
    chart(px.bar(constructors, x="Constructor", y="Points", color="Title probability", title="Constructor championship board"))
    st.dataframe(constructors, use_container_width=True, hide_index=True)

panel("Scientific limitation", "This page is a championship modelling scaffold. Production use requires real calendar, results, points system, sprint format and calibrated race-outcome distributions.")
