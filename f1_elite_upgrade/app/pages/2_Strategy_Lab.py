from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import pandas as pd
import plotly.express as px
import streamlit as st
from f1predictor.strategy.advanced_strategy import make_pit_window_figure, make_strategy_figure, simulate_strategy
from theme import apply_theme, chart, hero, panel, section_header, status_cards

st.set_page_config(page_title="Strategy Lab", page_icon="F1", layout="wide")
apply_theme()

hero(
    "F1 Strategy Room",
    "Pit-wall strategy workspace for comparing one-stop, two-stop and aggressive tyre plans using total race time, pit-loss exposure, tyre-life risk and pit-window sensitivity.",
    ["Pit windows", "Tyre strategy", "Undercut", "Risk"],
)

controls, workspace = st.columns([0.28, 0.72])
with controls:
    section_header("Controls", "Strategy scenario", "Tune the race assumptions and compare candidate tyre plans.")
    total_laps = st.slider("Race laps", 30, 78, 53)
    pit_loss = st.slider("Pit loss [s]", 15.0, 35.0, 22.5, 0.5)
    sc_probability = st.slider("SC/VSC probability", 0.0, 1.0, 0.12, 0.01)
    degradation_mode = st.selectbox("Degradation mode", ["Low", "Medium", "High"], index=1)
    panel("Decision rule", "The fastest strategy is only a baseline. Track position, safety-car exposure, tyre cliff and traffic risk must be interpreted before the final call.")

strategies = {
    "S-M": [("SOFT", 16), ("MEDIUM", total_laps - 16)],
    "M-H": [("MEDIUM", 25), ("HARD", total_laps - 25)],
    "S-H": [("SOFT", 14), ("HARD", total_laps - 14)],
    "S-M-M": [("SOFT", 12), ("MEDIUM", 20), ("MEDIUM", total_laps - 32)],
}

deg_multiplier = {"Low": 0.85, "Medium": 1.0, "High": 1.18}[degradation_mode]
rows = []
for name, strat in strategies.items():
    total, _ = simulate_strategy(strat, pit_loss=pit_loss)
    stops = len(strat) - 1
    longest_stint = max(length for _, length in strat)
    tyre_risk = longest_stint * deg_multiplier / total_laps
    sc_exposure = max(0.0, stops * pit_loss * (1 - 0.35 * sc_probability))
    rows.append(
        {
            "Strategy": name,
            "Stops": stops,
            "Total race time [s]": round(total * deg_multiplier, 3),
            "Longest stint": longest_stint,
            "Tyre risk": round(tyre_risk, 3),
            "Pit exposure [s]": round(sc_exposure, 2),
            "Risk band": "High" if tyre_risk > 0.55 else "Medium" if stops > 1 else "Low",
        }
    )

strategy_df = pd.DataFrame(rows).sort_values("Total race time [s]").reset_index(drop=True)
best = strategy_df.iloc[0]

with workspace:
    status_cards(
        [
            ("Recommended", str(best["Strategy"]), "Lowest modelled race time under current assumptions."),
            ("Race time", f"{best['Total race time [s]']:.1f}s", "Projected total strategy time."),
            ("Stops", str(int(best["Stops"])), "Pit-stop count for recommended plan."),
            ("Risk band", str(best["Risk band"]), "Tyre-life and pit-exposure interpretation."),
        ]
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Strategy board", "Stint structure", "Pit windows", "Risk analysis"])
    with tab1:
        section_header("Comparison", "Candidate strategy board", "Rank strategies by race time, stops, tyre risk and pit exposure.")
        st.dataframe(strategy_df, use_container_width=True, hide_index=True)
        chart(px.bar(strategy_df, x="Strategy", y="Total race time [s]", color="Risk band", title="Strategy race-time comparison"))
    with tab2:
        section_header("Structure", "Stint timeline", "Visualize compound sequence and stint lengths.")
        chart(make_strategy_figure(strategies))
    with tab3:
        section_header("Search", "One-stop pit window", "Find pit-lap sensitivity for baseline one-stop plans.")
        results, fig = make_pit_window_figure(total_laps)
        chart(fig)
        st.dataframe(results.head(10), use_container_width=True, hide_index=True)
    with tab4:
        section_header("Risk", "Strategy trade-off map", "Compare race time against pit exposure and tyre-life risk.")
        chart(px.scatter(strategy_df, x="Pit exposure [s]", y="Tyre risk", size="Total race time [s]", color="Strategy", title="Pit exposure versus tyre-life risk"))
        panel("Engineering limitation", "The model is a transparent strategy baseline. It does not yet include calibrated traffic, restart tyre temperature, live weather radar or real team degradation models.")
