"""Premium Base44-style Streamlit app for the Formula 1 race simulation project.

Run with:
    streamlit run app/f1_analytics_platform.py
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.live_broadcast import (
    build_weather_radar,
    detect_drs_and_overtake_alerts,
    generate_team_radio,
    plot_track_map_animation,
    plot_weather_radar,
)
from src.f1predictor.race_analyst import generate_race_report
from src.f1predictor.simulation import lap_by_lap_race_simulation, monte_carlo_race
from src.f1predictor.visualization import plot_probabilities


PRIMARY = "#e10600"
PRIMARY_DARK = "#8b0000"
BG = "#07080d"
SURFACE = "#111827"
SURFACE_2 = "#151f2e"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
GRID = "rgba(255,255,255,0.08)"
PALETTE = [PRIMARY, "#ff4d4d", "#f97316", "#facc15", "#38bdf8", "#60a5fa", "#a78bfa"]

RACES_2026 = [
    "Australian Grand Prix 2026", "Chinese Grand Prix 2026", "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026", "Saudi Arabian Grand Prix 2026", "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026", "Canadian Grand Prix 2026", "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026", "British Grand Prix 2026", "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026", "Italian Grand Prix 2026", "Singapore Grand Prix 2026",
    "United States Grand Prix 2026", "Mexico City Grand Prix 2026", "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026", "Qatar Grand Prix 2026", "Abu Dhabi Grand Prix 2026",
]

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = PALETTE

st.set_page_config(
    page_title="F1 Base44 Elite",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = f"""
<style>
:root {{
  --b44-bg: {BG};
  --b44-surface: {SURFACE};
  --b44-surface-2: {SURFACE_2};
  --b44-primary: {PRIMARY};
  --b44-primary-dark: {PRIMARY_DARK};
  --b44-text: {TEXT};
  --b44-muted: {MUTED};
  --b44-border: rgba(255,255,255,.10);
}}
.stApp {{
  background: radial-gradient(circle at 50% -10%, rgba(225,6,0,.18), transparent 34%),
              linear-gradient(135deg, #030407 0%, var(--b44-bg) 46%, #0c111b 100%);
  color: var(--b44-text);
}}
[data-testid="stHeader"] {{ background: rgba(7,8,13,.78); backdrop-filter: blur(18px); border-bottom: 1px solid rgba(255,255,255,.06); }}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #07080d 0%, #0f172a 100%); border-right: 1px solid rgba(225,6,0,.28); }}
.block-container {{ max-width: 1540px; padding-top: 1.1rem; padding-bottom: 2.3rem; }}
h1,h2,h3 {{ letter-spacing: -.04em; color: #fff; }}
.base44-hero {{
  border: 1px solid rgba(225,6,0,.34); border-radius: 30px; padding: 30px 34px; margin-bottom: 1.05rem;
  background: linear-gradient(135deg, rgba(225,6,0,.20), rgba(17,24,39,.96)), radial-gradient(circle at 90% 10%, rgba(225,6,0,.16), transparent 20rem);
  box-shadow: 0 28px 90px rgba(0,0,0,.36), inset 0 1px 0 rgba(255,255,255,.05);
}}
.base44-hero h1 {{ margin:0; font-size: clamp(2.35rem, 4vw, 4.1rem); font-weight: 950; line-height: 1; }}
.base44-hero p {{ margin:.8rem 0 0; color:#d1d5db; max-width:1120px; line-height:1.65; font-size:1.05rem; }}
.badge {{ display:inline-block; margin:.9rem .4rem 0 0; padding:.38rem .78rem; border-radius:999px; background:rgba(225,6,0,.15); border:1px solid rgba(255,100,95,.36); color:#fecaca; font-size:.76rem; font-weight:850; letter-spacing:.05em; text-transform:uppercase; }}
.card {{
  background: linear-gradient(180deg, rgba(21,31,46,.96), rgba(16,23,34,.92)); border:1px solid rgba(255,255,255,.10); border-top:2px solid var(--b44-primary);
  border-radius:22px; padding:19px 20px; min-height:124px; box-shadow:0 18px 45px rgba(0,0,0,.26), inset 0 1px 0 rgba(255,255,255,.04);
}}
.card .label {{ color:var(--b44-muted); font-size:.78rem; font-weight:850; letter-spacing:.07em; text-transform:uppercase; }}
.card .value {{ color:#fff; font-size:2rem; font-weight:950; margin-top:.45rem; line-height:1.05; }}
.card .sub {{ color:var(--b44-muted); font-size:.88rem; margin-top:.35rem; }}
.panel {{ border:1px solid rgba(255,255,255,.10); border-left:4px solid var(--b44-primary); border-radius:20px; padding:18px 20px; background:rgba(17,24,39,.78); margin:.75rem 0 1rem; }}
.panel p {{ color:#d1d5db; line-height:1.58; margin-bottom:0; }}
.feed {{ background:rgba(16,23,34,.86); border:1px solid rgba(255,255,255,.10); border-left:3px solid var(--b44-primary); border-radius:16px; padding:11px 13px; margin:8px 0; box-shadow:0 14px 34px rgba(0,0,0,.22); }}
.feed b {{ color:#fecaca; margin-right:.5rem; }}
[data-testid="stDataFrame"] {{ border:1px solid rgba(255,255,255,.10); border-radius:18px; overflow:hidden; background:rgba(16,23,34,.72); }}
.stButton>button,.stDownloadButton>button {{ border-radius:999px; border:1px solid rgba(255,100,95,.50); background:linear-gradient(135deg,var(--b44-primary),var(--b44-primary-dark)); color:#fff; font-weight:900; box-shadow:0 12px 28px rgba(225,6,0,.20); }}
.stButton>button:hover,.stDownloadButton>button:hover {{ border-color:rgba(255,160,155,.90); filter:brightness(1.08); }}
div[data-baseweb="select"]>div,input,textarea {{ background-color:rgba(16,23,34,.96)!important; color:var(--b44-text)!important; border-color:rgba(255,255,255,.14)!important; border-radius:14px!important; }}
section[data-testid="stTabs"] button {{ color:#f8fafc!important; font-weight:850!important; }}
.stAlert {{ border-radius:16px; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def fig_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(7,8,13,0)",
        plot_bgcolor="rgba(16,23,34,.94)",
        font={"color": TEXT, "family": "Inter, Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 18, "r": 18, "t": 52, "b": 34},
        colorway=PALETTE,
        legend={"bgcolor": "rgba(17,24,39,.55)", "bordercolor": "rgba(255,255,255,.10)", "borderwidth": 1},
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,.18)")
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,.18)")
    return fig


def chart(fig: go.Figure) -> None:
    st.plotly_chart(fig_theme(fig), use_container_width=True)


def kpi(label: str, value: str, sub: str = "") -> None:
    st.markdown(f"<div class='card'><div class='label'>{label}</div><div class='value'>{value}</div><div class='sub'>{sub}</div></div>", unsafe_allow_html=True)


def panel(title: str, text: str) -> None:
    st.markdown(f"<div class='panel'><h3>{title}</h3><p>{text}</p></div>", unsafe_allow_html=True)


def feed(label: str, text: str) -> None:
    st.markdown(f"<div class='feed'><b>{label}</b>{text}</div>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def demo_data() -> pd.DataFrame:
    return build_demo_dataset()


@st.cache_data(show_spinner=True)
def build_state(race_name: str, total_laps: int, pit_loss: float, rain_probability: float, seed: int):
    forecast_result = forecast_future_race(
        history_df=demo_data(),
        race_name=race_name,
        year=2026,
        round_no=12,
        n_simulations=2500,
        noise_std=2.0,
        use_2026_grid=True,
    )
    forecast = forecast_result["forecast"]
    sim = forecast_result["simulation"]
    weather = forecast_result["weather"]
    replay = lap_by_lap_race_simulation(
        forecast,
        total_laps=total_laps,
        pit_loss=pit_loss,
        rain_probability=rain_probability,
        random_state=seed,
    )
    timeline = replay["timeline"]
    alerts = detect_drs_and_overtake_alerts(timeline)
    radar = build_weather_radar(timeline, base_rain_probability=rain_probability)
    radio = generate_team_radio(timeline, replay["pitstops"], alerts)
    report = generate_race_report(forecast=forecast, simulation=sim, weather=weather)
    return {"forecast": forecast, "sim": sim, "weather": weather, "timeline": timeline, "alerts": alerts, "radar": radar, "radio": radio, "report": report, **replay}


with st.sidebar:
    st.header("Base44 Controls")
    race_name = st.selectbox("Grand Prix", RACES_2026, index=11)
    total_laps = st.slider("Race distance", 10, 78, 53)
    pit_loss = st.slider("Pit-lane loss", 15.0, 35.0, 22.5, step=0.5)
    rain_probability = st.slider("Rain probability", 0.0, 1.0, 0.20, step=0.05)
    seed = st.number_input("Simulation seed", min_value=1, max_value=99999, value=42)
    rebuild = st.button("Build race simulation", type="primary")

if rebuild or "base44_state" not in st.session_state:
    with st.spinner("Building premium race intelligence workspace..."):
        st.session_state["base44_state"] = build_state(race_name, int(total_laps), float(pit_loss), float(rain_probability), int(seed))
        st.session_state["base44_lap"] = 1

state = st.session_state["base44_state"]
timeline = state["timeline"]
radar = state["radar"]
alerts = state["alerts"]
radio = state["radio"]

st.markdown(
    """
    <div class="base44-hero">
      <h1>F1 Base44 Elite Race Engineering</h1>
      <p>A polished Formula 1 analytics workspace with race simulation, live timing, strategy intelligence, weather radar, team radio and Monte Carlo probabilities in one unified product experience.</p>
      <span class="badge">Base44-style UI</span><span class="badge">Race control</span><span class="badge">Telemetry-ready</span><span class="badge">Strategy AI</span><span class="badge">Live simulation</span>
    </div>
    """,
    unsafe_allow_html=True,
)

lap = st.slider("Race timeline", 1, int(total_laps), int(st.session_state.get("base44_lap", 1)))
st.session_state["base44_lap"] = lap
lap_df = timeline[timeline["Lap"] == lap].sort_values("RacePosition")
lap_radar = radar[radar["Lap"] == lap]
lap_alerts = alerts[alerts["Lap"] == lap] if not alerts.empty else pd.DataFrame()
lap_radio = radio[radio["Lap"] == lap] if not radio.empty else pd.DataFrame()
leader = lap_df.iloc[0]["Driver"] if not lap_df.empty else "N/A"
grip = f"{float(lap_radar.iloc[0]['TrackGrip']) * 100:.0f}%" if not lap_radar.empty else "N/A"

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Grand Prix", race_name.replace(" Grand Prix 2026", ""), "2026 simulation")
with c2: kpi("Current lap", f"{lap}/{total_laps}", "live race state")
with c3: kpi("Race leader", str(leader), "track position P1")
with c4: kpi("Track grip", grip, "weather-adjusted")

panel("Race intelligence brief", state["report"])

tab1, tab2, tab3, tab4 = st.tabs(["Race Control", "Strategy", "Weather & Alerts", "Data Tables"])

with tab1:
    left, right = st.columns([1, 1.25])
    with left:
        st.subheader("Live Classification")
        cols = [c for c in ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "PitStops"] if c in lap_df.columns]
        st.dataframe(lap_df[cols].head(15), use_container_width=True, hide_index=True)
    with right:
        st.subheader("Track Map")
        chart(plot_track_map_animation(timeline))

    st.subheader("Monte Carlo Win Probability")
    sim = state["sim"].head(10)
    if "WinProbability" in sim.columns:
        chart(plot_probabilities(sim, "WinProbability"))

with tab2:
    s1, s2 = st.columns([1, 1])
    with s1:
        st.subheader("Race pace gap")
        chart(px.bar(lap_df.sort_values("RacePosition"), x="Driver", y="GapToLeader", color="Compound", title=f"Gap to leader — lap {lap}", hover_data=["Team", "RacePosition", "PitStops"]))
    with s2:
        st.subheader("Team Radio")
        if lap_radio.empty:
            feed("RADIO", "No team-radio message on this lap.")
        else:
            for _, row in lap_radio.head(8).iterrows():
                feed(str(row.get("Driver", "RADIO")), f"{row.get('Channel', 'Race Engineer')}: {row.get('Message', '')}")

with tab3:
    w1, w2 = st.columns([1.2, 1])
    with w1:
        st.subheader("Weather Radar")
        chart(plot_weather_radar(radar[radar["Lap"] <= lap]))
    with w2:
        st.subheader("DRS / Overtake Alerts")
        if lap_alerts.empty:
            feed("DRS", "No active DRS or overtake alert.")
        else:
            for _, row in lap_alerts.head(10).iterrows():
                feed(str(row.get("Type", "ALERT")), str(row.get("Message", "")))

with tab4:
    d1, d2 = st.columns(2)
    with d1:
        st.subheader("Forecast table")
        forecast_cols = [c for c in ["PredictedRank", "Driver", "Team", "PredictedFinishPosition", "GridPosition", "DNFRisk", "SafetyCarProbability"] if c in state["forecast"].columns]
        st.dataframe(state["forecast"][forecast_cols], use_container_width=True, hide_index=True)
    with d2:
        st.subheader("Final classification")
        st.dataframe(state["final_order"], use_container_width=True, hide_index=True)

st.caption("Base44 Elite Live Build • main/app/f1_analytics_platform.py")
