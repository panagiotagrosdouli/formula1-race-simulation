import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from theme import FERRARI_RED, apply_theme, chart, hero, panel

st.set_page_config(page_title="F1 Elite Engineering", page_icon="🏎️", layout="wide")
apply_theme()

st.markdown(
    """
    <style>
    .elite-card-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin: 1rem 0 1.2rem 0;
    }
    .elite-card {
        min-height: 190px;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 22px;
        padding: 1.1rem;
        background:
            radial-gradient(circle at 85% 12%, rgba(225,6,0,0.17), transparent 7rem),
            linear-gradient(180deg, rgba(31,41,55,0.92), rgba(12,17,27,0.92));
        box-shadow: 0 22px 60px rgba(0,0,0,0.26), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .elite-card .icon { font-size: 1.8rem; margin-bottom: 0.7rem; }
    .elite-card h3 { margin: 0; font-size: 1.05rem; }
    .elite-card p { color: #cbd5e1; font-size: 0.86rem; line-height: 1.55; margin: 0.55rem 0 0 0; }
    .elite-card .tag { display: inline-block; margin-top: 0.9rem; color: #fecaca; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; }
    .workflow {
        border: 1px solid rgba(225,6,0,0.26);
        border-radius: 24px;
        padding: 1rem 1.1rem;
        background: rgba(7,8,13,0.58);
    }
    .workflow-step {
        border-left: 3px solid rgba(225,6,0,0.85);
        padding: .35rem 0 .35rem .9rem;
        margin: .55rem 0;
        color: #d1d5db;
    }
    @media (max-width: 1100px) { .elite-card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 700px) { .elite-card-grid { grid-template-columns: 1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)

hero(
    "🏎️ F1 Elite Race Engineering Platform",
    "A premium Formula 1 engineering cockpit: telemetry comparison, pit-stop strategy, explainable race-engineer advice, live timing probability and simulation-driven decision support in one Streamlit experience.",
    ["Telemetry", "Strategy", "Race Engineer AI", "Live timing", "Simulation"],
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Telemetry Lab", "Ready", "FastF1 + demo fallback")
col2.metric("Strategy Lab", "Ready", "Pit windows + tyre life")
col3.metric("Race Engineer AI", "Ready", "Explainable advice")
col4.metric("Live Timing", "Ready", "Probability demo")

panel(
    "What this app is",
    "This Streamlit app is the main premium interface. It keeps the elite pages you built and organizes them as a motorsport engineering platform: analysis first, assumptions visible, no fake official team data.",
)

st.markdown(
    """
    <div class="elite-card-grid">
      <div class="elite-card">
        <div class="icon">📡</div>
        <h3>Telemetry Lab</h3>
        <p>Compare two drivers with speed trace, lap-time delta, throttle/brake controls and track map views.</p>
        <span class="tag">FastF1 + fallback</span>
      </div>
      <div class="elite-card">
        <div class="icon">🧠</div>
        <h3>Strategy Lab</h3>
        <p>Simulate candidate tyre plans, pit-loss sensitivity and one-stop pit-window search.</p>
        <span class="tag">Pit windows</span>
      </div>
      <div class="elite-card">
        <div class="icon">🎙️</div>
        <h3>Race Engineer AI</h3>
        <p>Generate transparent pit-stop advice using undercut, tyre age, gaps, SC risk and rain exposure.</p>
        <span class="tag">Explainable AI</span>
      </div>
      <div class="elite-card">
        <div class="icon">⏱️</div>
        <h3>Live Timing Demo</h3>
        <p>Move the lap slider and watch synthetic live probability estimates update like a timing wall.</p>
        <span class="tag">Race control</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("Engineering workflow")
    st.markdown(
        """
        <div class="workflow">
          <div class="workflow-step"><b>1. Observe</b> — read timing, gaps, tyre age, weather and telemetry traces.</div>
          <div class="workflow-step"><b>2. Diagnose</b> — find where lap time is gained or lost using delta, speed and controls.</div>
          <div class="workflow-step"><b>3. Simulate</b> — compare tyre plans, pit loss and strategy windows.</div>
          <div class="workflow-step"><b>4. Decide</b> — use explainable race-engineer advice with risk and assumptions shown.</div>
          <div class="workflow-step"><b>5. Report</b> — communicate a recommendation with limitations instead of hiding uncertainty.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.subheader("Demo race intelligence")
    demo = pd.DataFrame(
        {
            "Driver": ["LEC", "NOR", "VER", "PIA", "HAM"],
            "Win probability": [0.31, 0.27, 0.22, 0.13, 0.07],
        }
    )
    fig = go.Figure(
        go.Bar(
            x=demo["Driver"],
            y=demo["Win probability"],
            marker_color=FERRARI_RED,
            text=[f"{value * 100:.0f}%" for value in demo["Win probability"]],
            textposition="outside",
        )
    )
    fig.update_layout(title="Live probability snapshot", yaxis_title="Probability", xaxis_title="Driver")
    chart(fig)

st.subheader("Open the workspaces")
st.info(
    "Use the Streamlit sidebar to open: Telemetry Lab, Strategy Lab, Race Engineer AI and Live Timing Demo. "
    "For Streamlit Cloud, set the main file to streamlit_app.py or f1_elite_upgrade/app/Home.py."
)

panel(
    "Scientific limitation",
    "The demo outputs are transparent engineering examples. They are not official F1 team data and should be treated as reproducible modelling assumptions until calibrated with public data.",
)
