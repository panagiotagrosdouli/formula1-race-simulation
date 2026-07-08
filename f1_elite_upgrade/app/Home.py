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

from theme import apply_theme, chart, hero, panel

st.set_page_config(page_title="F1Sim Pro Command Center", page_icon="F1", layout="wide")
apply_theme()

st.markdown(
    """
    <style>
    .f1-grid { display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; margin: 1rem 0 1.25rem; }
    .f1-card { min-height: 175px; border: 1px solid rgba(255,255,255,.10); border-radius: 24px; padding: 1.15rem; background: radial-gradient(circle at 88% 10%, rgba(225,6,0,.18), transparent 7rem), linear-gradient(180deg, rgba(31,41,55,.94), rgba(10,15,25,.94)); box-shadow: 0 24px 70px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.055); }
    .f1-card h3 { margin: 0; font-size: 1.05rem; }
    .f1-card p { color:#cbd5e1; font-size:.86rem; line-height:1.55; margin:.55rem 0 0; }
    .f1-tag { display:inline-block; margin-top:.9rem; color:#fecaca; font-size:.72rem; letter-spacing:.08em; font-weight:850; text-transform:uppercase; }
    .f1-status { border:1px solid rgba(225,6,0,.28); border-radius:22px; padding:1rem 1.1rem; background:rgba(7,8,13,.62); }
    .f1-step { border-left:3px solid rgba(225,6,0,.9); padding:.4rem 0 .4rem .9rem; margin:.55rem 0; color:#d1d5db; }
    @media (max-width: 1100px) { .f1-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 700px) { .f1-grid { grid-template-columns: 1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)

hero(
    "F1Sim Pro Race Intelligence Platform",
    "A premium Formula 1-style command center for race prediction, live timing analysis, tyre strategy, telemetry, driver databases and engineering reports. The platform is built on transparent open simulation models and public-data scaffolds; it never fabricates official team data.",
    ["Race Control", "Predictions", "Telemetry", "Strategy", "Tyres", "Reports"],
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Race engine", "Lap-by-lap", "tyres, fuel, gaps")
m2.metric("Prediction", "Monte Carlo", "seeded uncertainty")
m3.metric("Data mode", "Public/scaffold", "no fake team data")
m4.metric("Interface", "Multipage Pro", "engineering cockpit")

panel(
    "Platform identity",
    "This is the main Streamlit product experience. It is organized like a race-weekend operations system: observe timing, diagnose pace, simulate scenarios, decide strategy, and export an engineering report with assumptions and limitations.",
)

st.markdown(
    """
    <div class="f1-grid">
      <div class="f1-card"><h3>Race Control</h3><p>Timing wall, position order, gaps, lap-time evolution, pit events and race-state timeline.</p><span class="f1-tag">Implemented</span></div>
      <div class="f1-card"><h3>Prediction Center</h3><p>Projected finishing order, expected race time, confidence intervals and target-driver risk.</p><span class="f1-tag">Implemented / Prototype</span></div>
      <div class="f1-card"><h3>Strategy Room</h3><p>One-, two- and three-stop strategies, undercut, overcut, pit windows and tyre-life risk.</p><span class="f1-tag">Implemented</span></div>
      <div class="f1-card"><h3>Telemetry Workstation</h3><p>CSV upload, lap-time normalization, driver pace estimation and FastF1/OpenF1 scaffolds.</p><span class="f1-tag">Prototype</span></div>
      <div class="f1-card"><h3>Tyre Lab</h3><p>Soft, medium, hard, intermediate and wet compounds with degradation and cliff behaviour.</p><span class="f1-tag">Implemented</span></div>
      <div class="f1-card"><h3>Driver Database</h3><p>Driver profiles, pace index, wet sensitivity, qualifying and tyre-management indicators.</p><span class="f1-tag">Prototype</span></div>
      <div class="f1-card"><h3>Team Database</h3><p>Constructor profiles, reliability, pit-crew index, upgrade signal and strategy profile.</p><span class="f1-tag">Prototype</span></div>
      <div class="f1-card"><h3>Track Database</h3><p>Race distance, degradation, pit loss, DRS, fuel effect, SC probability and weather exposure.</p><span class="f1-tag">Prototype</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.08, 0.92])
with left:
    st.subheader("Race-weekend workflow")
    st.markdown(
        """
        <div class="f1-status">
          <div class="f1-step"><b>Observe</b> timing, gaps, tyres, weather and safety-car state.</div>
          <div class="f1-step"><b>Predict</b> finishing order using lap-by-lap simulation and Monte Carlo risk.</div>
          <div class="f1-step"><b>Diagnose</b> driver pace using telemetry or uploaded lap-time data.</div>
          <div class="f1-step"><b>Decide</b> pit windows, undercut, overcut and tyre compound strategy.</div>
          <div class="f1-step"><b>Report</b> assumptions, metrics, limitations and reproducible configuration.</div>
        </div>
        """,
        unsafe_allow_html=True,
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
    fig = px.bar(board, x="Driver", y="Win probability", color="Expected position", title="Synthetic prediction snapshot")
    chart(fig)

st.info("Use the sidebar pages to open the full platform modules. Synthetic demo outputs are clearly labelled; real public-data integrations require configured data sources.")
