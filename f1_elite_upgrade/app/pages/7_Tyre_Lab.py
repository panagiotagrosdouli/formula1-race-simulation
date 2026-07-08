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
from f1sim.models.tyres import COMPOUNDS, TyreModel

st.set_page_config(page_title="Tyre Lab", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Tyre Lab",
    "Compound comparison, tyre age, wear degradation, cliff behaviour, track temperature and wetness sensitivity for strategy analysis.",
    ["Tyres", "Degradation", "Strategy"],
)

model = TyreModel()
c1, c2, c3 = st.columns(3)
compound = c1.selectbox("Compound", list(COMPOUNDS), index=1)
track_temp = c2.slider("Track temperature C", 10.0, 60.0, 35.0, 1.0)
wetness = c3.slider("Track wetness", 0.0, 1.0, 0.0, 0.05)

rows = []
for name in COMPOUNDS:
    for age in range(0, 65):
        rows.append({"Compound": name, "Tyre age": age, "Pace loss": model.lap_delta_s(name, age, track_temp, wetness)})
frame = pd.DataFrame(rows)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Selected compound", compound)
k2.metric("Loss at 20 laps", f"{model.lap_delta_s(compound, 20, track_temp, wetness):.3f}s")
k3.metric("Loss at 40 laps", f"{model.lap_delta_s(compound, 40, track_temp, wetness):.3f}s")
k4.metric("Degradation rate", f"{model.degradation_rate(compound, 35):.4f}s/lap")

chart(px.line(frame, x="Tyre age", y="Pace loss", color="Compound", title="Compound degradation curves"))
panel("Engineering use", "Use this page to inspect crossover points between compounds. Values are transparent modelling assumptions and should be calibrated before research claims.")
