from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel

st.set_page_config(page_title="Track Database", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Track Database",
    "Prototype circuit intelligence layer for degradation, pit loss, fuel effect, DRS relevance, overtaking difficulty, safety-car probability and weather exposure.",
    ["Circuits", "Pit loss", "Tyres", "Weather", "SC risk"],
)

tracks = pd.DataFrame(
    [
        ["Bahrain", 57, 22.1, 86, 64, 0.32, 0.04],
        ["Jeddah", 50, 20.4, 58, 72, 0.48, 0.03],
        ["Melbourne", 58, 22.0, 66, 61, 0.39, 0.12],
        ["Monaco", 78, 19.5, 42, 12, 0.44, 0.18],
        ["Silverstone", 52, 23.1, 72, 70, 0.31, 0.28],
        ["Spa", 44, 21.4, 76, 74, 0.36, 0.35],
        ["Monza", 53, 24.0, 52, 86, 0.26, 0.10],
    ],
    columns=["Circuit", "Laps", "Pit loss", "Deg index", "Overtake index", "SC probability", "Rain exposure"],
)

track = st.selectbox("Circuit", tracks["Circuit"].tolist())
row = tracks[tracks["Circuit"] == track].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Laps", int(row["Laps"]))
c2.metric("Pit loss", f"{row['Pit loss']:.1f}s")
c3.metric("Deg index", int(row["Deg index"]))
c4.metric("SC probability", f"{row['SC probability']:.0%}")

chart(px.scatter(tracks, x="Deg index", y="Overtake index", size="SC probability", color="Rain exposure", hover_name="Circuit", title="Circuit strategy profile"))
st.dataframe(tracks, use_container_width=True, hide_index=True)
panel("Data status", "Track profiles are prototype values for interface and model exploration. Calibrate with public race history before factual claims.")
