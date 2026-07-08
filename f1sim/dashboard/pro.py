"""F1Sim Pro: premium Formula 1 race intelligence Streamlit app."""

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

DRIVER_BOARD = pd.DataFrame(
    [
        ["LEC", "Ferrari", 31.4, 24.2, 1.8, "A"],
        ["NOR", "McLaren", 29.7, 23.6, 1.4, "A"],
        ["VER", "Red Bull", 28.9, 28.5, -0.2, "A"],
        ["PIA", "McLaren", 23.8, 21.8, 0.9, "B"],
        ["HAM", "Ferrari", 19.2, 20.5, -0.5, "B"],
        ["RUS", "Mercedes", 18.4, 18.9, 0.3, "B"],
        ["ALO", "Aston Martin", 11.8, 13.4, 0.1, "C"],
        ["SAI", "Williams", 13.6, 15.0, 0.6, "C"],
    ],
    columns=["Driver", "Team", "Projected points", "Market value", "Form trend", "Risk tier"],
)

CONSTRUCTORS = pd.DataFrame(
    [
        ["McLaren", 44.0, 27.0, 0.94],
        ["Ferrari", 39.5, 25.5, 0.91],
        ["Red Bull", 36.0, 26.8, 0.90],
        ["Mercedes", 32.4, 22.2, 0.89],
        ["Aston Martin", 15.8, 12.5, 0.84],
    ],
    columns=["Constructor", "Projected points", "Market value", "Reliability"],
)


def configure() -> None:
    """Configure page and visual system."""

    st.set_page_config(page_title="F1Sim Pro", page_icon="F1", layout="wide")
    st.markdown(
        """
        <style>
        :root{--red:#e10600;--bg:#05070d;--panel:#101827;--muted:#9ca3af;--line:rgba(255,255,255,.12);--green:#22c55e;--amber:#f59e0b;--blue:#38bdf8;}
        .stApp{background:radial-gradient(circle at 82% -10%,rgba(225,6,0,.32),transparent 28rem),radial-gradient(circle at 8% 18%,rgba(56,189,248,.13),transparent 25rem),linear-gradient(145deg,#020307,#05070d 52%,#0b1019);color:#f8fafc;}
        [data-testid="stHeader"]{background:rgba(2,3,7,.72);backdrop-filter:blur(18px)}
        [data-testid="stSidebar"]{background:linear-gradient(180deg,#070911,#0d1420);border-right:1px solid rgba(225,6,0,.36)}
        .block-container{max-width:1580px;padding-top:1rem;padding-bottom:3rem} h1,h2,h3{letter-spacing:-.045em}
        .hero{border:1px solid rgba(225,6,0,.42);border-radius:34px;padding:2rem 2.2rem;background:linear-gradient(135deg,rgba(225,6,0,.28),rgba(15,23,42,.92) 45%,rgba(2,6,23,.96)),repeating-linear-gradient(110deg,transparent,transparent 22px,rgba(255,255,255,.026) 23px,rgba(255,255,255,.026) 24px);box-shadow:0 34px 120px rgba(0,0,0,.46),inset 0 1px 0 rgba(255,255,255,.08);margin-bottom:1rem}
        .hero h1{margin:0;font-size:clamp(2.6rem,5vw,5.6rem);line-height:.94}.hero p{max-width:1040px;color:#d1d5db;font-size:1.04rem;line-height:1.7;margin:1rem 0 0}
        .badge{display:inline-block;padding:.42rem .74rem;margin:1rem .45rem 0 0;border:1px solid rgba(255,255,255,.13);border-radius:999px;background:rgba(255,255,255,.055);font-size:.72rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:#e5e7eb}
        .grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.85rem;margin:1rem 0}.card{border:1px solid var(--line);border-radius:22px;padding:1rem 1.1rem;background:linear-gradient(180deg,rgba(17,24,39,.94),rgba(8,13,22,.86));box-shadow:0 20px 70px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.05);height:100%}.card .label{color:var(--muted);font-size:.74rem;text-transform:uppercase;letter-spacing:.09em;font-weight:850}.card .value{font-size:1.7rem;font-weight:950;margin-top:.25rem}.card p{color:var(--muted);line-height:1.55;margin:.45rem 0 0;font-size:.9rem}
        .note{border-left:4px solid var(--red);background:rgba(225,6,0,.09);padding:.9rem 1rem;border-radius:16px;color:#fecaca;margin:.75rem 0} div[data-testid="stMetric"]{border:1px solid var(--line);border-radius:20px;padding:14px 16px;background:linear-gradient(180deg,rgba(31,41,55,.95),rgba(17,24,39,.86))} div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:18px;overflow:hidden}
        @media(max-width:1000px){.grid4{grid-template-columns:repeat(2,minmax(0,1fr));}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def configs() -> list[str]:
    """List experiment YAML configs."""

    return [str(path.relative_to(ROOT)) for path in sorted(CONFIG_DIR.glob("*.yml"))] if CONFIG_DIR.exists() else []


@st.cache_data(show_spinner=False)
def load_config(path: str):
    """Load a race config."""

    return load_race_config(ROOT / path)


@st.cache_data(show_spinner=True)
def run_race(path: str, seed: int) -> RaceResult:
    """Run one seeded simulation."""

    return RaceSimulation(load_config(path).model_copy(update={"seed": seed})).run()


def fmt(seconds: float) -> str:
    """Format seconds as race time."""

    minutes = int(seconds // 60)
    return f"{minutes}:{seconds - minutes * 60:06.3f}"


def style(fig: go.Figure) -> go.Figure:
    """Apply Plotly dark style."""

    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,15,25,.78)", font={"color": "#f8fafc"}, margin={"l": 18, "r": 18, "t": 54, "b": 34})
    fig.update_xaxes(gridcolor="rgba(255,255,255,.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.08)")
    return fig


def landing() -> None:
    """Render first screen."""

    st.markdown(
        """
        <div class="hero">
          <h1>F1Sim Pro Race Intelligence</h1>
          <p>An F1-style command platform for race prediction, strategy engineering, driver market intelligence, telemetry analysis and reproducible simulation. It is not official F1 software and does not fabricate team data; synthetic values are clearly labelled.</p>
          <span class="badge">Race prediction</span><span class="badge">Strategy wall</span><span class="badge">Driver market</span><span class="badge">Telemetry lab</span><span class="badge">Engineering reports</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="grid4">
          <div class="card"><div class="label">Platform mode</div><div class="value">Command Center</div><p>Prediction, strategy, telemetry and reporting in one interface.</p></div>
          <div class="card"><div class="label">Race engine</div><div class="value">Lap-by-lap</div><p>Tyres, fuel, weather, gaps, SC/VSC and pit events.</p></div>
          <div class="card"><div class="label">Decision support</div><div class="value">Monte Carlo</div><p>Seeded uncertainty with confidence intervals and risk profile.</p></div>
          <div class="card"><div class="label">Data honesty</div><div class="value">Transparent</div><p>No official game/team data unless licensed and connected.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1.1, .9])
    with c1:
        modules = pd.DataFrame(
            [
                ["Race Control", "Live-style timing, positions, gaps and pit events", "Implemented"],
                ["Driver Predictor", "Projected ranking, market value and risk tier", "Prototype"],
                ["Strategy Room", "Pit windows, undercut, overcut, tyre calls", "Implemented / Prototype"],
                ["Telemetry Workstation", "CSV processing, FastF1/OpenF1 scaffolds", "Prototype"],
                ["Fantasy Manager", "100M roster, contracts and constructor selection", "Prototype"],
                ["Leagues and Community", "Draft, mini-leagues, FanHub-style sharing", "Planned"],
            ],
            columns=["Module", "What it does", "Status"],
        )
        st.dataframe(modules, use_container_width=True, hide_index=True)
    with c2:
        fig = px.bar(DRIVER_BOARD, x="Driver", y="Projected points", color="Form trend", title="Synthetic prediction board", color_continuous_scale="RdYlGn")
        st.plotly_chart(style(fig), use_container_width=True)
    st.markdown("<div class='note'>Official F1 Fantasy-style integration is a planned licensed data integration. Current market values and projections are synthetic examples for product design and simulation testing.</div>", unsafe_allow_html=True)


def race_control() -> None:
    """Race prediction and timing wall."""

    st.header("Race Control and Prediction")
    cfgs = configs()
    if not cfgs:
        st.warning("No configs found under configs/experiments.")
        return
    c1, c2, c3 = st.columns(3)
    config_path = c1.selectbox("Race scenario", cfgs)
    seed = int(c2.number_input("Seed", 1, 999999, 42))
    runs = c3.slider("Monte Carlo runs", 10, 600, 100, 10)
    result = run_race(config_path, seed)
    frame = pd.DataFrame(result.lap_history)
    leader = result.classification[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Predicted winner", leader.driver_id)
    m2.metric("Race time", fmt(leader.total_time_s))
    m3.metric("Pit stops", leader.pit_stops)
    m4.metric("Traffic loss", f"{leader.traffic_loss_s:.2f}s")
    tabs = st.tabs(["Timing wall", "Lap pace", "Position map", "Gap trace", "Tyres", "Monte Carlo"])
    with tabs[0]:
        lead_time = result.classification[0].total_time_s
        table = pd.DataFrame([{"Pos": d.position, "Driver": d.driver_id, "Gap": round(d.total_time_s - lead_time, 3), "Stops": d.pit_stops, "Tyre": d.compound} for d in result.classification])
        st.dataframe(table, use_container_width=True, hide_index=True)
    with tabs[1]:
        st.plotly_chart(style(px.line(frame, x="lap", y="lap_time_s", color="driver_id", title="Lap-time evolution")), use_container_width=True)
    with tabs[2]:
        fig = px.line(frame, x="lap", y="position", color="driver_id", markers=True, title="Position tracking")
        fig.update_yaxes(autorange="reversed", dtick=1)
        st.plotly_chart(style(fig), use_container_width=True)
    with tabs[3]:
        st.plotly_chart(style(px.line(frame, x="lap", y="gap_to_leader_s", color="driver_id", title="Gap to leader")), use_container_width=True)
    with tabs[4]:
        st.plotly_chart(style(px.scatter(frame, x="lap", y="driver_id", color="compound", size="tyre_age_laps", title="Tyre stint timeline")), use_container_width=True)
    with tabs[5]:
        summary = MonteCarloSimulation(load_config(config_path), runs=int(runs), seed=seed).run()
        st.dataframe(pd.DataFrame([summary.strategy_risk_profile]), use_container_width=True, hide_index=True)


def driver_market() -> None:
    """Fantasy-style market and roster."""

    st.header("Driver Market and Roster Builder")
    drivers = st.multiselect("Pick 5 drivers", DRIVER_BOARD["Driver"].tolist(), default=["LEC", "NOR", "PIA", "RUS", "SAI"])
    constructor = st.selectbox("Constructor", CONSTRUCTORS["Constructor"].tolist())
    driver_cost = DRIVER_BOARD.loc[DRIVER_BOARD["Driver"].isin(drivers), "Market value"].sum()
    constructor_cost = float(CONSTRUCTORS.loc[CONSTRUCTORS["Constructor"] == constructor, "Market value"].iloc[0])
    total = float(driver_cost + constructor_cost)
    projected = DRIVER_BOARD.loc[DRIVER_BOARD["Driver"].isin(drivers), "Projected points"].sum() + float(CONSTRUCTORS.loc[CONSTRUCTORS["Constructor"] == constructor, "Projected points"].iloc[0])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Roster value", f"{total:.1f}M")
    c2.metric("Budget left", f"{100-total:.1f}M")
    c3.metric("Drivers", f"{len(drivers)}/5")
    c4.metric("Projected points", f"{projected:.1f}")
    if len(drivers) != 5 or total > 100:
        st.error("Roster invalid: choose exactly 5 drivers and stay under the 100M cap.")
    else:
        st.success("Roster valid under the 100M cap.")
    st.dataframe(DRIVER_BOARD, use_container_width=True, hide_index=True)
    st.dataframe(CONSTRUCTORS, use_container_width=True, hide_index=True)
    st.code("value_next = base + form + qualifying + long_run_pace + demand - risk", language="text")


def strategy_room() -> None:
    """Strategy calls and engineering models."""

    st.header("Strategy Room")
    tyre_age = st.slider("Current tyre age", 1, 45, 22)
    gap = st.slider("Gap to target [s]", -5.0, 8.0, 1.2, .1)
    rain = st.slider("Rain probability", 0.0, 1.0, .18, .01)
    sc = st.slider("SC/VSC probability", 0.0, 1.0, .12, .01)
    tyre = TyreModel()
    old_delta = tyre.lap_delta_s("medium", tyre_age, 35.0, rain)
    new_delta = tyre.lap_delta_s("hard", 1, 35.0, rain)
    undercut = undercut_delta_s(tyre_age, new_delta, old_delta) - max(0.0, gap)
    overcut = overcut_delta_s(max(0.0, 1.5 - gap), max(0.0, old_delta - new_delta))
    confidence = max(0, min(100, 50 + 8 * undercut + 5 * overcut + 12 * sc + 10 * rain))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Undercut delta", f"{undercut:.2f}s")
    c2.metric("Overcut delta", f"{overcut:.2f}s")
    c3.metric("SC opportunity", f"{sc:.0%}")
    c4.metric("Call confidence", f"{confidence:.0f}%")
    st.dataframe(pd.DataFrame([{"Strategy": s.name, "Stops": s.stops, "Compounds": "-".join(s.compounds), "Pit laps": s.pit_laps} for s in generate_candidate_strategies(58)]), use_container_width=True, hide_index=True)


def models_lab() -> None:
    """Tyres, fuel, weather and safety car."""

    st.header("Engineering Models Lab")
    tab1, tab2, tab3, tab4 = st.tabs(["Tyres", "Fuel", "Weather", "Safety Car"])
    with tab1:
        tyre = TyreModel()
        df = pd.DataFrame([{"Age": age, "Compound": name, "Pace loss": tyre.lap_delta_s(name, age, 35.0, 0.0)} for name in COMPOUNDS for age in range(55)])
        st.plotly_chart(style(px.line(df, x="Age", y="Pace loss", color="Compound", title="Tyre degradation and cliff behaviour")), use_container_width=True)
    with tab2:
        fuel = FuelModel(100.0, 1.7, 0.035, 2.0)
        df = pd.DataFrame([{"Lap": lap, "Fuel kg": fuel.fuel_at_lap_start(lap), "Lap delta": fuel.lap_delta_s(lap)} for lap in range(1, 59)])
        st.plotly_chart(style(px.line(df, x="Lap", y=["Fuel kg", "Lap delta"], title="Fuel load effect")), use_container_width=True)
    with tab3:
        weather = WeatherModel(.12, 24.0, 34.0, 42)
        rows = []
        for lap in range(1, 59):
            state = weather.step()
            rows.append({"Lap": lap, "Wetness": state.wetness, "Track temp": state.track_temp_c, "Raining": state.raining})
        st.plotly_chart(style(px.line(pd.DataFrame(rows), x="Lap", y=["Wetness", "Track temp"], title="Weather transition")), use_container_width=True)
    with tab4:
        model = SafetyCarModel(.03, .04, .62, 12)
        rows = []
        for lap in range(1, 59):
            state = model.step()
            rows.append({"Lap": lap, "Safety car": state.safety_car, "VSC": state.vsc, "Lap multiplier": state.lap_time_multiplier, "Pit multiplier": state.pit_loss_multiplier})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def telemetry_lab() -> None:
    """CSV telemetry and pace estimation."""

    st.header("Telemetry Workstation")
    st.markdown("<div class='note'>CSV upload is real. FastF1/OpenF1 remain public-data scaffolds. No official team data is fabricated.</div>", unsafe_allow_html=True)
    upload = st.file_uploader("Upload CSV with driver_id, lap, lap_time_s", type=["csv"])
    if upload:
        RESULTS_DIR.mkdir(exist_ok=True)
        path = RESULTS_DIR / "uploaded_laps.csv"
        path.write_bytes(upload.getvalue())
        frame = load_lap_csv(path)
        normalized = normalize_lap_times(frame)
        st.dataframe(estimate_driver_pace(frame), use_container_width=True, hide_index=True)
        st.plotly_chart(style(px.line(normalized, x="lap", y="normalized_lap_time_s", color="driver_id", title="Normalized pace delta")), use_container_width=True)
    else:
        demo = pd.DataFrame({"driver_id": ["LEC", "LEC", "NOR", "NOR"], "lap": [1, 2, 1, 2], "lap_time_s": [91.2, 91.4, 91.5, 91.3]})
        st.dataframe(demo, use_container_width=True, hide_index=True)


def reports() -> None:
    """Report center."""

    st.header("Engineering Report Center")
    cfgs = configs()
    if not cfgs:
        return
    path = st.selectbox("Scenario", cfgs)
    result = run_race(path, 42)
    report = f"""# F1Sim Pro Report

- Scenario: {path}
- Predicted winner: {result.classification[0].driver_id}
- Race time: {result.metrics.total_race_time_s:.3f}s
- Pit stops: {result.metrics.pit_stop_count}
- Stints: {result.metrics.stint_lengths}
- Compounds: {' - '.join(result.metrics.compound_sequence)}

Synthetic/example configuration. Not official F1 or team data.
"""
    st.download_button("Download Markdown report", report, "f1sim_report.md", "text/markdown")
    st.markdown(report)


def render_dashboard() -> None:
    """Render app."""

    configure()
    with st.sidebar:
        st.title("F1Sim Pro")
        st.caption("Race prediction, strategy, telemetry and management")
        section = st.radio("Navigation", ["Command Center", "Race Control", "Driver Market", "Strategy Room", "Models Lab", "Telemetry", "Reports"])
        st.markdown("---")
        st.caption("Official integrations are planned. Synthetic examples are labelled.")
    if section == "Command Center":
        landing()
    elif section == "Race Control":
        race_control()
    elif section == "Driver Market":
        driver_market()
    elif section == "Strategy Room":
        strategy_room()
    elif section == "Models Lab":
        models_lab()
    elif section == "Telemetry":
        telemetry_lab()
    else:
        reports()


if __name__ == "__main__":
    render_dashboard()
