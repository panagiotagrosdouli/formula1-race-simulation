"""Ultimate Formula 1 fantasy and race-management Streamlit command center."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from f1sim.data.config import load_race_config
from f1sim.models.fuel import FuelModel
from f1sim.models.tyres import COMPOUNDS, TyreModel
from f1sim.safety_car.model import SafetyCarModel
from f1sim.simulation.engine import RaceResult, RaceSimulation
from f1sim.simulation.monte_carlo import MonteCarloSimulation
from f1sim.strategy.generator import generate_candidate_strategies, overcut_delta_s, undercut_delta_s
from f1sim.telemetry.loaders import estimate_driver_pace, load_lap_csv, normalize_lap_times
from f1sim.weather.model import WeatherModel

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs" / "experiments"
RESULTS_DIR = ROOT / "results"

DRIVER_MARKET = pd.DataFrame(
    [
        {"Driver": "LEC", "Team": "Ferrari", "Value": 24.2, "Projected": 31.4, "Trend": 1.8, "Contract": "3 races"},
        {"Driver": "NOR", "Team": "McLaren", "Value": 23.6, "Projected": 29.7, "Trend": 1.4, "Contract": "Race-by-race"},
        {"Driver": "VER", "Team": "Red Bull", "Value": 28.5, "Projected": 28.9, "Trend": -0.2, "Contract": "6 races"},
        {"Driver": "PIA", "Team": "McLaren", "Value": 21.8, "Projected": 23.8, "Trend": 0.9, "Contract": "3 races"},
        {"Driver": "HAM", "Team": "Ferrari", "Value": 20.5, "Projected": 19.2, "Trend": -0.5, "Contract": "Race-by-race"},
        {"Driver": "ALO", "Team": "Aston Martin", "Value": 13.4, "Projected": 11.8, "Trend": 0.1, "Contract": "Race-by-race"},
        {"Driver": "RUS", "Team": "Mercedes", "Value": 18.9, "Projected": 18.4, "Trend": 0.3, "Contract": "3 races"},
        {"Driver": "SAI", "Team": "Williams", "Value": 15.0, "Projected": 13.6, "Trend": 0.6, "Contract": "Race-by-race"},
    ]
)

CONSTRUCTOR_MARKET = pd.DataFrame(
    [
        {"Constructor": "McLaren", "Value": 27.0, "Projected": 44.0, "Reliability": 0.94},
        {"Constructor": "Ferrari", "Value": 25.5, "Projected": 39.5, "Reliability": 0.91},
        {"Constructor": "Red Bull", "Value": 26.8, "Projected": 36.0, "Reliability": 0.90},
        {"Constructor": "Mercedes", "Value": 22.2, "Projected": 32.4, "Reliability": 0.89},
        {"Constructor": "Aston Martin", "Value": 12.5, "Projected": 15.8, "Reliability": 0.84},
    ]
)


def configure_page() -> None:
    """Configure Streamlit page and inject premium product styling."""

    st.set_page_config(page_title="F1Sim Ultimate Platform", page_icon="F1", layout="wide")
    st.markdown(
        """
        <style>
        :root { --red:#e10600; --bg:#05070d; --panel:#101827; --muted:#9ca3af; --line:rgba(255,255,255,.11); --green:#22c55e; --amber:#f59e0b; --blue:#38bdf8; }
        .stApp { background: radial-gradient(circle at 85% -8%, rgba(225,6,0,.30), transparent 28rem), radial-gradient(circle at 10% 15%, rgba(56,189,248,.12), transparent 26rem), linear-gradient(145deg,#020307 0%,#05070d 52%,#0b1019 100%); color:#f8fafc; }
        [data-testid="stHeader"] { background: rgba(2,3,7,.72); backdrop-filter: blur(18px); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#070911 0%,#0d1420 100%); border-right:1px solid rgba(225,6,0,.35); }
        .block-container { max-width:1580px; padding-top:1rem; padding-bottom:3rem; }
        h1,h2,h3 { letter-spacing:-.045em; }
        .command-hero { border:1px solid rgba(225,6,0,.38); border-radius:34px; padding:2rem 2.2rem; background: linear-gradient(135deg,rgba(225,6,0,.26),rgba(15,23,42,.90) 46%,rgba(2,6,23,.96)), repeating-linear-gradient(110deg,transparent,transparent 22px,rgba(255,255,255,.025) 23px,rgba(255,255,255,.025) 24px); box-shadow:0 34px 120px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.08); margin-bottom:1rem; }
        .command-hero h1 { margin:0; font-size:clamp(2.5rem,5vw,5.5rem); line-height:.94; }
        .command-hero p { max-width:980px; color:#d1d5db; font-size:1.03rem; line-height:1.7; margin:1rem 0 0; }
        .badge { display:inline-block; padding:.42rem .72rem; margin:1rem .45rem 0 0; border:1px solid rgba(255,255,255,.13); border-radius:999px; background:rgba(255,255,255,.055); font-size:.72rem; font-weight:850; letter-spacing:.08em; text-transform:uppercase; color:#e5e7eb; }
        .grid4 { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.85rem; margin:1rem 0; }
        .card { border:1px solid var(--line); border-radius:22px; padding:1rem 1.1rem; background:linear-gradient(180deg,rgba(17,24,39,.92),rgba(8,13,22,.84)); box-shadow:0 20px 70px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.05); height:100%; }
        .card .label { color:var(--muted); font-size:.74rem; text-transform:uppercase; letter-spacing:.09em; font-weight:850; }
        .card .value { font-size:1.75rem; font-weight:950; margin-top:.25rem; }
        .card p { color:var(--muted); line-height:1.55; margin:.45rem 0 0; font-size:.9rem; }
        .note { border-left:4px solid var(--red); background:rgba(225,6,0,.09); padding:.9rem 1rem; border-radius:16px; color:#fecaca; margin:.75rem 0; }
        div[data-testid="stMetric"] { border:1px solid var(--line); border-radius:20px; padding:14px 16px; background:linear-gradient(180deg,rgba(31,41,55,.95),rgba(17,24,39,.86)); }
        div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:18px; overflow:hidden; }
        @media(max-width:1000px){.grid4{grid-template-columns:repeat(2,minmax(0,1fr));}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def available_configs() -> list[str]:
    """Return experiment configs."""

    return [str(path.relative_to(ROOT)) for path in sorted(CONFIG_DIR.glob("*.yml"))] if CONFIG_DIR.exists() else []


@st.cache_data(show_spinner=False)
def load_config(config_path: str):
    """Load race config."""

    return load_race_config(ROOT / config_path)


@st.cache_data(show_spinner=True)
def run_race(config_path: str, seed: int) -> RaceResult:
    """Run race simulation."""

    config = load_config(config_path).model_copy(update={"seed": seed})
    return RaceSimulation(config).run()


def fmt_time(seconds: float) -> str:
    """Format seconds."""

    minutes = int(seconds // 60)
    return f"{minutes}:{seconds - minutes * 60:06.3f}"


def chart_style(fig: go.Figure) -> go.Figure:
    """Apply dark chart style."""

    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,15,25,.78)", font={"color":"#f8fafc"}, margin={"l":18,"r":18,"t":54,"b":34})
    fig.update_xaxes(gridcolor="rgba(255,255,255,.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.08)")
    return fig


def render_home() -> None:
    """Render command home."""

    st.markdown(
        """
        <div class="command-hero">
          <h1>F1Sim Ultimate Race Intelligence Platform</h1>
          <p>A premium Formula 1 fantasy, management, strategy and telemetry command center. Build a roster, manage contracts, simulate race outcomes, react to live strategy windows and generate engineering-grade reports. Official game data is planned only; current examples are synthetic or public-data scaffolds.</p>
          <span class="badge">Fantasy roster</span><span class="badge">Live strategy</span><span class="badge">Telemetry lab</span><span class="badge">Monte Carlo predictions</span><span class="badge">Engineering reports</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="grid4">
          <div class="card"><div class="label">Race week status</div><div class="value">Simulation live</div><p>Seeded race engine, strategy lab and Monte Carlo cockpit ready.</p></div>
          <div class="card"><div class="label">Budget cap</div><div class="value">100M</div><p>Build 5 drivers and 1 constructor with contract pressure.</p></div>
          <div class="card"><div class="label">Strategy mode</div><div class="value">Interactive</div><p>Pit windows, tyre calls, undercut, overcut and SC/VSC reaction models.</p></div>
          <div class="card"><div class="label">Data policy</div><div class="value">Transparent</div><p>No fabricated official team or F1 Fantasy data.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1.2, .8])
    with c1:
        st.subheader("Product modules")
        modules = pd.DataFrame(
            [
                ["Race Prediction", "Monte Carlo race outcomes and projected fantasy points", "Implemented / Prototype"],
                ["Roster Economy", "100M cap, values, contracts, constructor selection", "Prototype"],
                ["Live Strategy", "Pit-call, tyre-call and SC/VSC reaction scoring", "Prototype"],
                ["Telemetry Lab", "CSV, FastF1/OpenF1 scaffolds, pace estimation", "Prototype"],
                ["Leagues", "Private, global, head-to-head draft", "Planned"],
                ["Community", "Shareable lineup cards and FanHub integrations", "Planned"],
            ],
            columns=["Module", "Capability", "Status"],
        )
        st.dataframe(modules, use_container_width=True, hide_index=True)
    with c2:
        st.subheader("Projected points snapshot")
        fig = px.bar(DRIVER_MARKET, x="Driver", y="Projected", color="Trend", title="Synthetic race-week projection", color_continuous_scale="RdYlGn")
        st.plotly_chart(chart_style(fig), use_container_width=True)
    st.markdown("<div class='note'>Official F1 Fantasy data integration requires licensed/authorized access. Current values and projections are synthetic platform examples.</div>", unsafe_allow_html=True)


def render_roster() -> None:
    """Render roster and economy lab."""

    st.header("Roster and Budget Economics")
    selected_drivers = st.multiselect("Select 5 drivers", DRIVER_MARKET["Driver"].tolist(), default=["LEC", "NOR", "PIA", "RUS", "SAI"])
    constructor = st.selectbox("Select constructor", CONSTRUCTOR_MARKET["Constructor"].tolist(), index=0)
    driver_cost = DRIVER_MARKET.loc[DRIVER_MARKET["Driver"].isin(selected_drivers), "Value"].sum()
    constructor_cost = float(CONSTRUCTOR_MARKET.loc[CONSTRUCTOR_MARKET["Constructor"] == constructor, "Value"].iloc[0])
    total = float(driver_cost + constructor_cost)
    remaining = 100.0 - total
    projected = DRIVER_MARKET.loc[DRIVER_MARKET["Driver"].isin(selected_drivers), "Projected"].sum() + float(CONSTRUCTOR_MARKET.loc[CONSTRUCTOR_MARKET["Constructor"] == constructor, "Projected"].iloc[0])
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Roster cost", f"{total:.1f}M")
    k2.metric("Remaining", f"{remaining:.1f}M")
    k3.metric("Drivers", f"{len(selected_drivers)}/5")
    k4.metric("Projected points", f"{projected:.1f}")
    if remaining < 0 or len(selected_drivers) != 5:
        st.error("Roster is not valid: select exactly 5 drivers and stay under the 100M cap.")
    else:
        st.success("Roster is valid under the 100M cap.")
    st.dataframe(DRIVER_MARKET, use_container_width=True, hide_index=True)
    st.dataframe(CONSTRUCTOR_MARKET, use_container_width=True, hide_index=True)
    st.code("market_value_next = base_value + form + qualifying + practice + upgrade_signal + transfer_demand - risk", language="text")


def render_prediction() -> None:
    """Render prediction cockpit."""

    st.header("Race Prediction and Simulation")
    configs = available_configs()
    if not configs:
        st.warning("No configs found.")
        return
    c1, c2, c3 = st.columns(3)
    config_path = c1.selectbox("Race scenario", configs)
    seed = c2.number_input("Seed", 1, 999999, 42)
    runs = c3.slider("Monte Carlo runs", 10, 600, 100, 10)
    result = run_race(config_path, int(seed))
    frame = pd.DataFrame(result.lap_history)
    leader = result.classification[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Predicted winner", leader.driver_id)
    m2.metric("Race time", fmt_time(leader.total_time_s))
    m3.metric("Pit stops", leader.pit_stops)
    m4.metric("Traffic loss", f"{leader.traffic_loss_s:.2f}s")
    tabs = st.tabs(["Race timeline", "Lap times", "Positions", "Gaps", "Tyres", "Classification", "Monte Carlo"])
    with tabs[0]:
        timeline = frame.groupby("lap", as_index=False).agg(wetness=("wetness", "mean"), safety_car=("safety_car", "max"), vsc=("vsc", "max"))
        st.plotly_chart(chart_style(px.line(timeline, x="lap", y="wetness", title="Race state timeline")), use_container_width=True)
    with tabs[1]:
        st.plotly_chart(chart_style(px.line(frame, x="lap", y="lap_time_s", color="driver_id", title="Lap-time evolution")), use_container_width=True)
    with tabs[2]:
        fig = px.line(frame, x="lap", y="position", color="driver_id", title="Position tracking", markers=True)
        fig.update_yaxes(autorange="reversed", dtick=1)
        st.plotly_chart(chart_style(fig), use_container_width=True)
    with tabs[3]:
        st.plotly_chart(chart_style(px.line(frame, x="lap", y="gap_to_leader_s", color="driver_id", title="Gap evolution")), use_container_width=True)
    with tabs[4]:
        st.plotly_chart(chart_style(px.scatter(frame, x="lap", y="driver_id", color="compound", size="tyre_age_laps", title="Tyre stint timeline")), use_container_width=True)
    with tabs[5]:
        lead_time = result.classification[0].total_time_s
        rows = [{"Position": d.position, "Driver": d.driver_id, "Race time": fmt_time(d.total_time_s), "Gap [s]": round(d.total_time_s - lead_time, 3), "Pit stops": d.pit_stops, "Compound": d.compound} for d in result.classification]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    with tabs[6]:
        summary = MonteCarloSimulation(load_config(config_path), runs=int(runs), seed=int(seed)).run()
        st.dataframe(pd.DataFrame([summary.strategy_risk_profile]), use_container_width=True, hide_index=True)


def render_live_strategy() -> None:
    """Render live strategy game mechanics."""

    st.header("Live Strategy Phase")
    tyre_age = st.slider("Current tyre age", 1, 45, 22)
    gap = st.slider("Gap to target driver [s]", -5.0, 8.0, 1.2, 0.1)
    rain = st.slider("Rain probability", 0.0, 1.0, 0.18, 0.01)
    sc = st.slider("SC/VSC probability", 0.0, 1.0, 0.12, 0.01)
    call = st.selectbox("Race engineer call", ["Hold track position", "Undercut", "Overcut", "Switch to intermediate", "Box under SC/VSC"])
    tyre = TyreModel()
    old_delta = tyre.lap_delta_s("medium", tyre_age, 35.0, rain)
    new_delta = tyre.lap_delta_s("hard", 1, 35.0, rain)
    undercut = undercut_delta_s(tyre_age, new_delta, old_delta) - max(0.0, gap)
    overcut = overcut_delta_s(track_position_gain_s=max(0.0, 1.5 - gap), tyre_loss_s=max(0.0, old_delta - new_delta))
    confidence = max(0, min(100, 50 + 8 * undercut + 5 * overcut + 12 * sc + 10 * rain))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Undercut score", f"{undercut:.2f}")
    c2.metric("Overcut score", f"{overcut:.2f}")
    c3.metric("SC opportunity", f"{sc:.0%}")
    c4.metric("Call confidence", f"{confidence:.0f}%")
    st.markdown(f"<div class='note'>Selected call: {call}. This is a simulated strategy-game mechanic, not real team advice.</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{"Strategy": s.name, "Stops": s.stops, "Compounds": "-".join(s.compounds), "Pit laps": s.pit_laps} for s in generate_candidate_strategies(58)]), use_container_width=True, hide_index=True)


def render_telemetry() -> None:
    """Render telemetry and data tools."""

    st.header("Telemetry and Data Tools")
    st.markdown("<div class='note'>CSV upload is real. FastF1/OpenF1 are scaffolds unless public data access is configured. No official team data is fabricated.</div>", unsafe_allow_html=True)
    upload = st.file_uploader("Upload CSV with driver_id, lap, lap_time_s", type=["csv"])
    if upload:
        RESULTS_DIR.mkdir(exist_ok=True)
        path = RESULTS_DIR / "uploaded_laps.csv"
        path.write_bytes(upload.getvalue())
        frame = load_lap_csv(path)
        normalized = normalize_lap_times(frame)
        st.dataframe(estimate_driver_pace(frame), use_container_width=True, hide_index=True)
        st.plotly_chart(chart_style(px.line(normalized, x="lap", y="normalized_lap_time_s", color="driver_id", title="Normalized lap-time delta")), use_container_width=True)
    else:
        st.dataframe(pd.DataFrame({"driver_id": ["LEC", "LEC", "NOR", "NOR"], "lap": [1, 2, 1, 2], "lap_time_s": [91.2, 91.4, 91.5, 91.3]}), use_container_width=True, hide_index=True)


def render_models() -> None:
    """Render tyre, fuel, weather and SC model labs."""

    st.header("Engineering Models")
    tab1, tab2, tab3, tab4 = st.tabs(["Tyres", "Fuel", "Weather", "Safety Car"])
    with tab1:
        compound = st.selectbox("Compound", list(COMPOUNDS), index=1)
        tyre = TyreModel()
        df = pd.DataFrame([{"Age": age, "Compound": name, "Pace loss": tyre.lap_delta_s(name, age, 35.0, 0.0)} for name in COMPOUNDS for age in range(0, 55)])
        st.plotly_chart(chart_style(px.line(df, x="Age", y="Pace loss", color="Compound", title="Tyre degradation curves")), use_container_width=True)
        st.metric("Selected degradation rate", f"{tyre.degradation_rate(compound, 35):.4f}s/lap")
    with tab2:
        fuel = FuelModel(100.0, 1.7, 0.035, 2.0)
        df = pd.DataFrame([{"Lap": lap, "Fuel": fuel.fuel_at_lap_start(lap), "Delta": fuel.lap_delta_s(lap)} for lap in range(1, 59)])
        st.plotly_chart(chart_style(px.line(df, x="Lap", y=["Fuel", "Delta"], title="Fuel load effect")), use_container_width=True)
    with tab3:
        weather = WeatherModel(0.12, 24.0, 34.0, 42)
        rows = []
        for lap in range(1, 59):
            state = weather.step()
            rows.append({"Lap": lap, "Wetness": state.wetness, "Track temp": state.track_temp_c, "Raining": state.raining})
        st.plotly_chart(chart_style(px.line(pd.DataFrame(rows), x="Lap", y=["Wetness", "Track temp"], title="Weather timeline")), use_container_width=True)
    with tab4:
        model = SafetyCarModel(.03, .04, .62, 12)
        rows = []
        for lap in range(1, 59):
            state = model.step()
            rows.append({"Lap": lap, "Safety car": state.safety_car, "VSC": state.vsc, "Lap multiplier": state.lap_time_multiplier, "Pit multiplier": state.pit_loss_multiplier})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_leagues() -> None:
    """Render planned league and community systems."""

    st.header("Leagues and Community")
    rows = pd.DataFrame(
        [
            ["Global salary-cap league", "Classic cost-cap leaderboard", "Prototype"],
            ["Head-to-head draft", "Each driver owned once per private league", "Planned"],
            ["Constructor championship", "Constructor-only scoring multipliers", "Planned"],
            ["Promotion/relegation tiers", "Season-long competitive ladder", "Planned"],
            ["FanHub integration", "Share lineup cards and strategy calls", "Planned"],
        ],
        columns=["League system", "Mechanic", "Status"],
    )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_report() -> None:
    """Render export/report center."""

    st.header("Engineering Report Center")
    configs = available_configs()
    if not configs:
        st.info("No configs available.")
        return
    config_path = st.selectbox("Report scenario", configs)
    result = run_race(config_path, 42)
    report = f"""# F1Sim Ultimate Report

- Config: {config_path}
- Winner: {result.classification[0].driver_id}
- Race time: {result.metrics.total_race_time_s:.3f}s
- Pit stops: {result.metrics.pit_stop_count}
- Stints: {result.metrics.stint_lengths}
- Compounds: {' - '.join(result.metrics.compound_sequence)}

This report uses synthetic/example configs and open simulation models. It does not include official F1 Fantasy or private team data.
"""
    st.download_button("Download Markdown report", report, "f1sim_report.md", "text/markdown")
    st.markdown(report)


def render_dashboard() -> None:
    """Render the ultimate dashboard."""

    configure_page()
    with st.sidebar:
        st.title("F1Sim Ultimate")
        st.caption("Fantasy, strategy, telemetry and race intelligence")
        section = st.radio("Navigation", ["Command Center", "Roster Economy", "Race Prediction", "Live Strategy", "Telemetry Tools", "Engineering Models", "Leagues", "Report Center"])
        st.markdown("---")
        st.caption("Official game integrations are planned only. Synthetic examples are labelled.")

    if section == "Command Center":
        render_home()
    elif section == "Roster Economy":
        render_roster()
    elif section == "Race Prediction":
        render_prediction()
    elif section == "Live Strategy":
        render_live_strategy()
    elif section == "Telemetry Tools":
        render_telemetry()
    elif section == "Engineering Models":
        render_models()
    elif section == "Leagues":
        render_leagues()
    else:
        render_report()


if __name__ == "__main__":
    render_dashboard()
