import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.components.theme import card, feed_line, hero, inject_theme, metric_card

st.set_page_config(page_title="F1 Base44 Elite", layout="wide")
inject_theme()

hero(
    eyebrow="Base44-style motorsport intelligence platform",
    title="F1 Base44 Elite",
    body=(
        "A premium Formula 1 decision-support workspace for race simulation, strategy thinking, telemetry review, "
        "live timing, and explainable race-engineering recommendations. The app is designed to feel like a real product: "
        "clear hierarchy, strong visual identity, guided workflows, and engineering context instead of disconnected numbers."
    ),
)

status_1, status_2, status_3, status_4 = st.columns(4)
with status_1:
    metric_card("Product layer", "Unified", "one visual language across pages")
with status_2:
    metric_card("Race control", "Live", "simulation and timing workspace")
with status_3:
    metric_card("Engineering AI", "Explainable", "recommendation plus reasoning")
with status_4:
    metric_card("Design system", "Base44", "premium dark Ferrari theme")

st.markdown("## Product experience")
exp_1, exp_2, exp_3 = st.columns(3)
with exp_1:
    card(
        "Race Control Workspace",
        "Run a simulated race state with leaderboard, gaps, tyre compounds, weather evolution, alerts, and a clean classification view.",
    )
with exp_2:
    card(
        "Strategy Intelligence",
        "Compare tyre plans, pit-lane loss assumptions, and pit-window timing through a structured engineering workflow.",
    )
with exp_3:
    card(
        "Telemetry Workstation",
        "Use FastF1-style speed, delta, control, and track-map traces to explain performance rather than only display lap time.",
    )

exp_4, exp_5, exp_6 = st.columns(3)
with exp_4:
    card(
        "Race Engineer AI",
        "Generate pit-stop recommendations with transparent reasoning around undercut, tyre age, rain risk and safety-car probability.",
    )
with exp_5:
    card(
        "Live Timing Prototype",
        "Preview how a lap-by-lap timing feed can update win probabilities and race-state interpretation in real time.",
    )
with exp_6:
    card(
        "Model Validation",
        "Keep the platform credible by separating prediction, uncertainty, diagnostics and engineering interpretation.",
    )

st.markdown("## Guided workflow")
feed_line("01", "Start with Race Control to create the race context and understand current state.")
feed_line("02", "Move to Strategy Lab to compare tyre plans and pit-window sensitivity.")
feed_line("03", "Use Telemetry Workstation to explain where performance differences appear on track.")
feed_line("04", "Ask Race Engineer AI for an explainable recommendation, not just a black-box answer.")
feed_line("05", "Review model and live timing pages to understand probability, uncertainty and data limitations.")

st.markdown("## Open workspaces")
action_1, action_2, action_3, action_4 = st.columns(4)
with action_1:
    st.page_link("app/pages/1_Telemetry_Lab.py", label="Telemetry Workstation", icon="📡")
with action_2:
    st.page_link("app/pages/2_Strategy_Lab.py", label="Strategy Lab", icon="🧠")
with action_3:
    st.page_link("app/pages/3_Race_Engineer_AI.py", label="Race Engineer AI", icon="🎙️")
with action_4:
    st.page_link("app/pages/4_Live_Timing_Demo.py", label="Live Timing Demo", icon="⏱️")

st.divider()

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("Design direction")
    st.write(
        "The interface now follows a single product language: dark premium surfaces, Ferrari-red action color, "
        "rounded cards, consistent spacing, clear page hierarchy, and workflow-led content. The goal is to look "
        "like a polished product built for decision support, not a collection of small Streamlit demos."
    )
with right:
    st.subheader("Engineering standard")
    st.write(
        "Predictions and recommendations should remain probabilistic and transparent. The app should explain what the model sees, "
        "where uncertainty remains, and which race-engineering assumptions matter before a decision is trusted."
    )

st.success("F1 Base44 Elite home is loaded. The broken Quick Actions link has been removed.")
