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

from theme import apply_theme, chart, hero, panel, section_header, status_cards
from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation
from f1sim.simulation.monte_carlo import MonteCarloSimulation

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Prediction Center", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Prediction Center",
    "Probability-desk view for projected finishing order, confidence intervals, strategy-risk profile and interpretation from deterministic configs and Monte Carlo simulation.",
    ["Probability desk", "Monte Carlo", "Risk", "Interpretability"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))]
if not configs:
    st.error("No experiment configs found.")
    st.stop()

control, body = st.columns([0.30, 0.70])
with control:
    section_header("Inputs", "Forecast controls", "Configure the prediction scenario and uncertainty sample size.")
    config_path = st.selectbox("Prediction scenario", configs)
    runs = st.slider("Monte Carlo runs", 10, 1000, 150, 10)
    seed = st.number_input("Seed", 1, 999999, 2026)
    target = st.text_input("Target driver", "NOR").upper()
    panel("Prediction policy", "Every forecast must be read as a model scenario, not a guaranteed outcome. Synthetic/example configs are clearly labelled.")

config = load_race_config(REPO_ROOT / config_path).model_copy(update={"seed": int(seed)})
result = RaceSimulation(config).run()
summary = MonteCarloSimulation(config, runs=int(runs), seed=int(seed)).run(target_driver_id=target)
leader = result.classification[0]
lead_time = result.classification[0].total_time_s

ranking = pd.DataFrame(
    [
        {
            "Position": d.position,
            "Driver": d.driver_id,
            "Expected finish": d.position,
            "Race time [s]": round(d.total_time_s, 3),
            "Gap [s]": round(d.total_time_s - lead_time, 3),
            "Stops": d.pit_stops,
            "Strategy risk": "Low" if d.pit_stops <= 1 else "Medium",
        }
        for d in result.classification
    ]
)

with body:
    beat_target = "N/A" if summary.probability_beating_target is None else f"{summary.probability_beating_target:.1%}"
    status_cards(
        [
            ("Projected winner", leader.driver_id, "Fastest total simulated race time."),
            ("Expected position", f"{summary.expected_position:.2f}", "Monte Carlo average finishing position."),
            ("Confidence interval", f"{summary.confidence_interval_s[0]:.1f}-{summary.confidence_interval_s[1]:.1f}s", "Race-time uncertainty band."),
            ("Beat target", beat_target, f"Probability versus {target}."),
        ]
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Forecast board", "Risk envelope", "Scenario sensitivity", "Explanation"])
    with tab1:
        section_header("Forecast", "Projected classification", "Driver-level output with gaps, pit count and strategy-risk label.")
        st.dataframe(ranking, use_container_width=True, hide_index=True)
        chart(px.bar(ranking, x="Driver", y="Gap [s]", color="Strategy risk", title="Projected gap to winner"))
    with tab2:
        risk = pd.DataFrame(
            {
                "Percentile": ["P05", "P50", "P95"],
                "Race time [s]": [
                    summary.strategy_risk_profile["p05_time_s"],
                    summary.strategy_risk_profile["p50_time_s"],
                    summary.strategy_risk_profile["p95_time_s"],
                ],
            }
        )
        chart(px.bar(risk, x="Percentile", y="Race time [s]", title="Monte Carlo race-time risk envelope"))
        st.dataframe(pd.DataFrame([summary.strategy_risk_profile]), use_container_width=True, hide_index=True)
    with tab3:
        sensitivity = pd.DataFrame(
            [
                ["Pace uncertainty", "High", "Directly changes finishing spread and confidence interval."],
                ["Safety car", "Medium", "Changes pit-loss exposure and track-position value."],
                ["Weather", "Medium", "Raises tyre crossover and strategy volatility."],
                ["Pit loss", "Medium", "Changes one-stop versus two-stop break-even."],
                ["Traffic", "Prototype", "Currently scaffolded; needs calibration."],
            ],
            columns=["Factor", "Impact", "Interpretation"],
        )
        st.dataframe(sensitivity, use_container_width=True, hide_index=True)
    with tab4:
        panel(
            "Why this prediction?",
            f"{leader.driver_id} leads because the simulated race-time model produces the lowest total time under the selected configuration. The confidence interval describes model uncertainty from seeded Monte Carlo runs, not a real-world certainty statement.",
        )
        panel(
            "What uncertainty remains?",
            "Real weather, safety cars, penalties, retirements, live traffic and team strategy calls can change the result. Production use requires calibration with public historical data and leakage-safe validation.",
        )
