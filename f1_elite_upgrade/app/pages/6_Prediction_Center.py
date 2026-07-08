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
from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation
from f1sim.simulation.monte_carlo import MonteCarloSimulation

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Prediction Center", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Prediction Center",
    "Projected finishing order, expected race time, confidence interval and strategy-risk profile from deterministic configs and Monte Carlo simulation.",
    ["Monte Carlo", "Risk", "Expected result", "Confidence interval"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))]
if not configs:
    st.error("No experiment configs found.")
    st.stop()

c1, c2, c3 = st.columns(3)
config_path = c1.selectbox("Prediction scenario", configs)
runs = c2.slider("Monte Carlo runs", 10, 1000, 150, 10)
seed = c3.number_input("Seed", 1, 999999, 2026)

config = load_race_config(REPO_ROOT / config_path).model_copy(update={"seed": int(seed)})
result = RaceSimulation(config).run()
summary = MonteCarloSimulation(config, runs=int(runs), seed=int(seed)).run()

leader = result.classification[0]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Projected winner", leader.driver_id)
k2.metric("Expected position", f"{summary.expected_position:.2f}")
k3.metric("Expected time", f"{summary.expected_time_s:.2f}s")
k4.metric("Risk P95", f"{summary.strategy_risk_profile['p95_time_s']:.2f}s")

left, right = st.columns([1.05, 0.95])
with left:
    lead_time = result.classification[0].total_time_s
    ranking = pd.DataFrame([
        {"Position": d.position, "Driver": d.driver_id, "Race time [s]": round(d.total_time_s, 3), "Gap [s]": round(d.total_time_s - lead_time, 3), "Stops": d.pit_stops}
        for d in result.classification
    ])
    st.subheader("Projected finishing order")
    st.dataframe(ranking, use_container_width=True, hide_index=True)
with right:
    risk = pd.DataFrame({
        "Percentile": ["P05", "P50", "P95"],
        "Race time [s]": [summary.strategy_risk_profile["p05_time_s"], summary.strategy_risk_profile["p50_time_s"], summary.strategy_risk_profile["p95_time_s"]],
    })
    chart(px.bar(risk, x="Percentile", y="Race time [s]", title="Risk envelope"))

panel("Interpretation", "Predictions are simulation outputs from transparent models and example configs. They are not official race predictions, betting advice or team data.")
