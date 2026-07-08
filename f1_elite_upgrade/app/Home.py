from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[0]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel, status_cards, workflow_steps

st.set_page_config(page_title="F1Sim Pro Command Center", page_icon="F1", layout="wide")
apply_theme()

hero(
    "F1Sim Pro Race Intelligence Platform",
    "A premium Formula 1-style command center for prediction, live timing analysis, tyre strategy, telemetry, driver databases and engineering reports. The platform uses transparent simulation models and clearly labelled public-data scaffolds.",
    ["Race Control", "Predictions", "Telemetry", "Strategy", "Reports"],
)

status_cards(
    [
        ("Race engine", "Lap-by-lap", "Tyres, fuel, race clock, gaps and pit events."),
        ("Prediction", "Monte Carlo", "Seeded uncertainty and risk envelope reporting."),
        ("Data mode", "Transparent", "Synthetic examples are labelled; real integrations require sources."),
        ("Interface", "Multipage Pro", "Designed as a race-weekend engineering cockpit."),
    ]
)

panel(
    "Platform identity",
    "The app is organized as a race-weekend operations system: observe timing, diagnose pace, simulate scenarios, decide strategy, and export reports with assumptions and limitations.",
)

modules = pd.DataFrame(
    [
        ["Race Control", "Timing wall, positions, gaps, lap-time evolution and pit events.", "Implemented"],
        ["Prediction Center", "Expected finishing order, confidence interval and risk profile.", "Implemented / Prototype"],
        ["Strategy Room", "Pit windows, undercut, overcut and tyre-life risk.", "Implemented"],
        ["Telemetry Workstation", "CSV processing and public telemetry scaffolds.", "Prototype"],
        ["Tyre Lab", "Compound degradation and cliff behaviour.", "Implemented"],
        ["Weather Center", "Rain probability, wetness and track evolution.", "Prototype"],
        ["Driver Database", "Pace, qualifying, wet index and tyre management.", "Prototype"],
        ["Team Database", "Reliability, pit crew and strategy profile.", "Prototype"],
        ["Track Database", "Pit loss, degradation, overtaking and SC profile.", "Prototype"],
        ["Report Center", "Markdown and CSV engineering exports.", "Implemented"],
    ],
    columns=["Workspace", "Engineering problem", "Status"],
)

left, right = st.columns([1.12, 0.88])
with left:
    st.subheader("Platform workspaces")
    st.dataframe(modules, use_container_width=True, hide_index=True)
    st.subheader("Race-weekend workflow")
    workflow_steps(
        [
            ("Observe", "Read timing, gaps, tyres, weather and safety-car state."),
            ("Predict", "Estimate finishing order using simulation and Monte Carlo risk."),
            ("Diagnose", "Explain pace using telemetry or uploaded lap-time data."),
            ("Decide", "Evaluate pit windows, undercut, overcut and compound strategy."),
            ("Report", "Export assumptions, metrics and reproducible configuration."),
        ]
    )
with right:
    st.subheader("Example prediction board")
    board = pd.DataFrame(
        {
            "Driver": ["LEC", "NOR", "VER", "PIA", "HAM"],
            "Win probability": [0.31, 0.27, 0.22, 0.13, 0.07],
            "Expected position": [2.3, 2.8, 3.0, 4.4, 5.1],
        }
    )
    chart(px.bar(board, x="Driver", y="Win probability", color="Expected position", title="Synthetic prediction snapshot"))
    st.caption("Synthetic example only. Replace with public-data calibrated outputs in later phases.")

st.info("Use the sidebar pages to open the full platform modules. Real public-data integrations require configured data sources.")
