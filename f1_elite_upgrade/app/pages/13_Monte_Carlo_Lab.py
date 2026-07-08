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
from f1sim.simulation.monte_carlo import MonteCarloSimulation

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Monte Carlo Lab", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Monte Carlo Lab",
    "Risk-aware strategy analysis under uncertainty: pace variation, weather exposure, safety-car scenarios, pit-loss exposure and confidence intervals.",
    ["Simulation", "Risk", "Confidence interval", "Strategy profile"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))]
if not configs:
    st.error("No experiment configs found.")
    st.stop()

c1, c2, c3 = st.columns(3)
config_path = c1.selectbox("Scenario", configs)
runs = c2.slider("Runs", 10, 1500, 250, 10)
seed = c3.number_input("Seed", 1, 999999, 2026)
target = st.text_input("Target driver for comparison", "NOR").upper()

config = load_race_config(REPO_ROOT / config_path)
summary = MonteCarloSimulation(config, runs=int(runs), seed=int(seed)).run(target_driver_id=target)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Runs", summary.runs)
k2.metric("Expected position", f"{summary.expected_position:.2f}")
k3.metric("Expected time", f"{summary.expected_time_s:.2f}s")
k4.metric("Beat target", "N/A" if summary.probability_beating_target is None else f"{summary.probability_beating_target:.1%}")

risk = pd.DataFrame(
    {
        "Percentile": ["P05", "P50", "P95"],
        "Race time": [summary.strategy_risk_profile["p05_time_s"], summary.strategy_risk_profile["p50_time_s"], summary.strategy_risk_profile["p95_time_s"]],
    }
)
chart(px.bar(risk, x="Percentile", y="Race time", title="Monte Carlo race-time risk envelope"))
st.dataframe(pd.DataFrame([summary.strategy_risk_profile]), use_container_width=True, hide_index=True)
panel("Interpretation", "The Monte Carlo layer estimates sensitivity around transparent model assumptions. It is not a guarantee of real-world outcomes and should be calibrated against public historical data before publication claims.")
