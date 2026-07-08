from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel
from f1sim.weather.model import WeatherModel

st.set_page_config(page_title="Weather Center", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Weather Center",
    "Race-weekend weather intelligence for rain probability, track wetness, air temperature, track temperature, wind scaffold and dry-wet transition risk.",
    ["Rain risk", "Track evolution", "Wet crossover", "Forecast scaffold"],
)

c1, c2, c3, c4 = st.columns(4)
rain_probability = c1.slider("Rain probability per lap", 0.0, 1.0, 0.14, 0.01)
air_temp = c2.slider("Air temperature C", 5.0, 40.0, 24.0, 1.0)
track_temp = c3.slider("Track temperature C", 5.0, 60.0, 34.0, 1.0)
seed = c4.number_input("Seed", 1, 999999, 42)

laps = st.slider("Timeline laps", 10, 78, 58)
model = WeatherModel(rain_probability, air_temp, track_temp, int(seed))
rows = []
for lap in range(1, laps + 1):
    state = model.step()
    rows.append(
        {
            "Lap": lap,
            "Wetness": state.wetness,
            "Track temp C": state.track_temp_c,
            "Raining": state.raining,
            "Wind kph": state.wind_speed_kph,
        }
    )
frame = pd.DataFrame(rows)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Peak wetness", f"{frame['Wetness'].max():.2f}")
k2.metric("Rain laps", int(frame["Raining"].sum()))
k3.metric("Avg track temp", f"{frame['Track temp C'].mean():.1f} C")
k4.metric("Max wind", f"{frame['Wind kph'].max():.1f} kph")

chart(px.line(frame, x="Lap", y=["Wetness", "Track temp C", "Wind kph"], title="Weather and track-state timeline"))
st.dataframe(frame, use_container_width=True, hide_index=True)
panel("Data status", "This is a stochastic weather model for simulation and strategy research. Real deployment should connect a cited public weather source and preserve deterministic seeds for reproducibility.")
