"""Professional Streamlit dashboard for the F1Sim engineering platform."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from f1sim.data.config import RaceConfig, load_race_config
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
ASSETS_DIR = ROOT / "assets"

STATUS_ROWS = [
    {"Area": "Lap-by-lap race simulation", "Status": "Implemented", "Notes": "Race clock, positions, gaps, pit events and classification."},
    {"Area": "Tyre degradation", "Status": "Implemented", "Notes": "Compound deltas, wear, cliff and temperature sensitivity."},
    {"Area": "Fuel effect", "Status": "Implemented", "Notes": "Fuel mass burn and lap-time improvement as load falls."},
    {"Area": "Weather uncertainty", "Status": "Prototype", "Notes": "Rain probability, wetness and temperature transition."},
    {"Area": "Safety car / VSC", "Status": "Prototype", "Notes": "Neutralisation probability and pit-loss reduction."},
    {"Area": "Traffic, penalties, retirements", "Status": "Prototype", "Notes": "Scaffolds only; not yet calibrated."},
    {"Area": "Monte Carlo risk analysis", "Status": "Implemented", "Notes": "Seeded stochastic runs and confidence intervals."},
    {"Area": "Telemetry integration", "Status": "Prototype", "Notes": "CSV implemented; FastF1/OpenF1 scaffolds only."},
    {"Area": "Optimization", "Status": "Prototype", "Notes": "Grid search baseline; Bayesian/GA planned."},
]

CIRCUITS = {
    "Balanced permanent circuit": {"laps": 58, "base_pace": 91.5, "track_temp": 35.0, "pit_loss": 22.0, "degradation": "medium"},
    "High degradation circuit": {"laps": 56, "base_pace": 94.0, "track_temp": 43.0, "pit_loss": 21.5, "degradation": "high"},
    "Low degradation circuit": {"laps": 52, "base_pace": 88.8, "track_temp": 29.0, "pit_loss": 23.5, "degradation": "low"},
    "Wet transition circuit": {"laps": 44, "base_pace": 104.0, "track_temp": 23.0, "pit_loss": 21.0, "degradation": "wet"},
}


def configure_page() -> None:
    """Configure page and inject professional dark styling."""

    st.set_page_config(page_title="F1Sim Race Engineering Platform", page_icon="F1", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --f1-red: #e10600;
            --bg: #05070d;
            --panel: rgba(17,24,39,0.84);
            --panel-soft: rgba(31,41,55,0.72);
            --border: rgba(255,255,255,0.10);
            --muted: #9ca3af;
        }
        .stApp {
            background: radial-gradient(circle at 80% -10%, rgba(225,6,0,0.16), transparent 32rem),
                        linear-gradient(135deg, #030407 0%, #05070d 55%, #0c111b 100%);
            color: #f9fafb;
        }
        [data-testid="stHeader"] { background: rgba(5,7,13,0.76); backdrop-filter: blur(18px); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #080a10 0%, #0e1420 100%); border-right: 1px solid rgba(225,6,0,0.28); }
        .block-container { max-width: 1540px; padding-top: 1.2rem; }
        h1, h2, h3 { letter-spacing: -0.04em; }
        .hero {
            border: 1px solid rgba(225,6,0,0.32);
            border-radius: 28px;
            padding: 30px 34px;
            background: linear-gradient(135deg, rgba(225,6,0,0.20), rgba(17,24,39,0.88)),
                        radial-gradient(circle at 90% 15%, rgba(255,255,255,0.10), transparent 18rem);
            box-shadow: 0 28px 80px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06);
            margin-bottom: 1rem;
        }
        .hero h1 { margin: 0; font-size: clamp(2.4rem, 4vw, 4.3rem); line-height: 1.02; }
        .hero p { color: #d1d5db; max-width: 1080px; margin: .8rem 0 0 0; line-height: 1.65; }
        .pill { display: inline-block; margin: .9rem .45rem 0 0; padding: .35rem .78rem; border-radius: 999px; border: 1px solid rgba(255,120,115,.35); background: rgba(225,6,0,.13); color: #fecaca; font-size: .75rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; }
        .panel { border: 1px solid var(--border); border-left: 4px solid var(--f1-red); border-radius: 18px; padding: 17px 19px; background: var(--panel); margin: .8rem 0 1rem 0; box-shadow: 0 18px 44px rgba(0,0,0,.20); }
        .panel p { color: #d1d5db; line-height: 1.58; margin-bottom: 0; }
        div[data-testid="stMetric"] { border: 1px solid var(--border); border-radius: 18px; padding: 15px 17px; background: linear-gradient(180deg, rgba(31,41,55,0.92), rgba(17,24,39,0.82)); box-shadow: inset 0 1px 0 rgba(255,255,255,.05); }
        div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 16px; overflow: hidden; }
        .small-muted { color: var(--muted); font-size: .86rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, body: str, pills: list[str] | None = None) -> None:
    """Render a polished hero block."""

    pill_html = "".join(f"<span class='pill'>{pill}</span>" for pill in (pills or []))
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{body}</p>{pill_html}</div>", unsafe_allow_html=True)


def panel(title: str, body: str) -> None:
    """Render a technical information panel."""

    st.markdown(f"<div class='panel'><h3>{title}</h3><p>{body}</p></div>", unsafe_allow_html=True)


def format_time(seconds: float) -> str:
    """Format seconds as minutes and seconds."""

    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes}:{remainder:06.3f}"


def available_configs() -> list[str]:
    """Return available experiment configs."""

    if not CONFIG_DIR.exists():
        return []
    return [str(path.relative_to(ROOT)) for path in sorted(CONFIG_DIR.glob("*.yml"))]


@st.cache_data(show_spinner=False)
def load_config(config_path: str) -> RaceConfig:
    """Load a YAML race configuration."""

    return load_race_config(ROOT / config_path)


@st.cache_data(show_spinner=True)
def simulate(config_path: str, seed: int) -> RaceResult:
    """Run deterministic simulation for dashboard use."""

    config = load_config(config_path).model_copy(update={"seed": seed})
    return RaceSimulation(config).run()


def result_frame(result: RaceResult) -> pd.DataFrame:
    """Return lap history as DataFrame."""

    return pd.DataFrame(result.lap_history)


def final_classification(result: RaceResult) -> pd.DataFrame:
    """Return final classification table."""

    leader_time = result.classification[0].total_time_s
    return pd.DataFrame(
        [
            {
                "Position": driver.position,
                "Driver": driver.driver_id,
                "Race time": format_time(driver.total_time_s),
                "Gap to leader [s]": round(driver.total_time_s - leader_time, 3),
                "Pit stops": driver.pit_stops,
                "Final compound": driver.compound,
                "Traffic loss [s]": round(driver.traffic_loss_s, 3),
            }
            for driver in result.classification
        ]
    )


def plotly_layout(fig: go.Figure) -> go.Figure:
    """Apply consistent engineering chart styling."""

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.82)",
        font={"color": "#f9fafb"},
        margin={"l": 24, "r": 24, "t": 56, "b": 36},
        legend={"bgcolor": "rgba(17,24,39,0.5)", "bordercolor": "rgba(255,255,255,0.12)", "borderwidth": 1},
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.10)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.10)")
    return fig


def render_overview() -> None:
    """Render platform overview section."""

    hero(
        "F1Sim Race Strategy Engineering Platform",
        "An open, reproducible and data-driven Formula 1 simulation platform for strategy analysis under tyre, weather, traffic, safety-car and pace uncertainty.",
        ["Race simulation", "Tyre degradation", "Monte Carlo", "Decision support"],
    )
    panel(
        "Engineering mission",
        "The platform is designed for transparent race strategy analysis. It separates implemented simulation logic, prototype scaffolds and planned research extensions. Default scenarios are synthetic/example configurations and are not official team data.",
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Primary app", "Streamlit")
    c2.metric("Simulation mode", "Lap-by-lap")
    c3.metric("Uncertainty", "Seeded Monte Carlo")
    c4.metric("Data policy", "No fabricated team data")

    st.subheader("System architecture")
    st.code(
        "configs -> f1sim.core -> models(tyre/fuel/pace) -> weather/SC -> strategy -> simulation -> metrics -> Streamlit reports",
        language="text",
    )
    st.subheader("Simulation pipeline")
    st.write("YAML or dashboard configuration defines drivers, strategy, pit loss, weather and neutralisation risk. The engine advances each driver lap by lap, updates race clock, gaps, tyre age, fuel mass, pit events and classification, then exports engineering metrics and figures.")
    st.subheader("Implementation status")
    st.dataframe(pd.DataFrame(STATUS_ROWS), use_container_width=True, hide_index=True)
    panel(
        "Limitations",
        "Traffic, penalties, retirements, restart effects and real-data calibration are intentionally labelled as scaffolds. Public telemetry integrations require external data access and source citation. The app must not be interpreted as an official Formula 1 or team strategy tool.",
    )


def render_race_dashboard() -> RaceResult | None:
    """Render race simulation dashboard."""

    st.header("Race Simulation Dashboard")
    configs = available_configs()
    if not configs:
        st.error("No YAML configs found under configs/experiments.")
        return None

    left, right = st.columns([0.35, 0.65])
    with left:
        config_path = st.selectbox("Experiment configuration", configs, index=0)
        circuit_name = st.selectbox("Circuit profile", list(CIRCUITS), index=0)
        circuit = CIRCUITS[circuit_name]
        seed = st.number_input("Deterministic seed", 1, 999999, 42)
        st.caption("Dashboard controls are paired with YAML experiments. Advanced editing should be done through configs/experiments.")
        config = load_config(config_path).model_copy(update={"seed": int(seed)})
        st.metric("Race distance", f"{config.laps} laps")
        st.metric("Pit loss", f"{config.pit_loss_s:.1f} s")
        st.metric("Track temperature", f"{config.track_temp_c:.1f} C")
        st.write("Drivers")
        st.dataframe(pd.DataFrame([driver.model_dump() for driver in config.drivers]), use_container_width=True, hide_index=True)
        st.write("Strategies")
        st.dataframe(pd.DataFrame([strategy.model_dump() for strategy in config.strategies]), use_container_width=True, hide_index=True)

    with right:
        result = simulate(config_path, int(seed))
        frame = result_frame(result)
        leader = result.classification[0]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Winner", leader.driver_id)
        k2.metric("Total race time", format_time(leader.total_time_s))
        k3.metric("Pit stops", leader.pit_stops)
        k4.metric("Traffic loss", f"{leader.traffic_loss_s:.2f} s")

        tabs = st.tabs(["Timeline", "Lap times", "Positions", "Gaps", "Tyres", "Pit stops", "Classification"])
        with tabs[0]:
            timeline = frame.groupby("lap", as_index=False).agg(wetness=("wetness", "mean"), safety_car=("safety_car", "max"), vsc=("vsc", "max"))
            fig = px.line(timeline, x="lap", y="wetness", title="Race timeline: track wetness and neutralisation markers")
            for lap in timeline.loc[timeline["safety_car"], "lap"]:
                fig.add_vline(x=lap, line_dash="dash", line_color="#e10600")
            for lap in timeline.loc[timeline["vsc"], "lap"]:
                fig.add_vline(x=lap, line_dash="dot", line_color="#f59e0b")
            st.plotly_chart(plotly_layout(fig), use_container_width=True)
        with tabs[1]:
            fig = px.line(frame, x="lap", y="lap_time_s", color="driver_id", title="Lap time evolution")
            st.plotly_chart(plotly_layout(fig), use_container_width=True)
        with tabs[2]:
            fig = px.line(frame, x="lap", y="position", color="driver_id", title="Position chart", markers=True)
            fig.update_yaxes(autorange="reversed", dtick=1)
            st.plotly_chart(plotly_layout(fig), use_container_width=True)
        with tabs[3]:
            fig = px.line(frame, x="lap", y="gap_to_leader_s", color="driver_id", title="Gap to leader evolution")
            st.plotly_chart(plotly_layout(fig), use_container_width=True)
        with tabs[4]:
            fig = px.scatter(frame, x="lap", y="driver_id", color="compound", size="tyre_age_laps", title="Tyre stint timeline")
            st.plotly_chart(plotly_layout(fig), use_container_width=True)
        with tabs[5]:
            pit_rows = [asdict(event) for event in result.pit_events]
            st.dataframe(pd.DataFrame(pit_rows), use_container_width=True, hide_index=True)
        with tabs[6]:
            st.dataframe(final_classification(result), use_container_width=True, hide_index=True)
    return result


def render_tyre_engineering() -> None:
    """Render tyre engineering lab."""

    st.header("Tyre Engineering")
    model = TyreModel()
    col1, col2, col3 = st.columns(3)
    compound = col1.selectbox("Compound", list(COMPOUNDS), index=1)
    track_temp = col2.slider("Track temperature C", 15.0, 55.0, 35.0, 1.0)
    wetness = col3.slider("Track wetness", 0.0, 1.0, 0.0, 0.05)
    max_age = st.slider("Tyre age range", 5, 70, 45)

    rows = []
    for name in COMPOUNDS:
        for age in range(max_age + 1):
            rows.append({"Compound": name, "Tyre age": age, "Pace loss [s]": model.lap_delta_s(name, age, track_temp, wetness)})
    tyre_df = pd.DataFrame(rows)
    fig = px.line(tyre_df, x="Tyre age", y="Pace loss [s]", color="Compound", title="Compound degradation and cliff behaviour")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)
    selected = tyre_df[tyre_df["Compound"] == compound]
    st.metric("Selected compound degradation rate", f"{model.degradation_rate(compound, max_age):.4f} s/lap")
    st.dataframe(selected.tail(12), use_container_width=True, hide_index=True)


def render_fuel_model() -> None:
    """Render fuel model lab."""

    st.header("Fuel Model")
    c1, c2, c3, c4 = st.columns(4)
    start_kg = c1.slider("Start fuel kg", 20.0, 115.0, 100.0, 1.0)
    burn = c2.slider("Burn kg/lap", 0.5, 4.0, 1.7, 0.1)
    effect = c3.slider("Lap-time effect s/kg", 0.005, 0.080, 0.035, 0.005)
    margin = c4.slider("Safety margin kg", 0.0, 8.0, 2.0, 0.5)
    laps = st.slider("Race laps", 10, 78, 58)
    fuel = FuelModel(start_kg=start_kg, burn_kg_per_lap=burn, lap_time_s_per_kg=effect, safety_margin_kg=margin)
    df = pd.DataFrame([{"Lap": lap, "Fuel kg": fuel.fuel_at_lap_start(lap), "Fuel lap-time delta [s]": fuel.lap_delta_s(lap)} for lap in range(1, laps + 1)])
    fig = px.line(df, x="Lap", y=["Fuel kg", "Fuel lap-time delta [s]"], title="Fuel mass and lap-time impact")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)
    panel("Fuel safety margin scaffold", "The model prevents negative fuel and exposes a configurable margin. Race-specific lift-and-coast or fuel-saving logic is planned, not implemented as calibrated physics.")


def render_weather_model() -> None:
    """Render weather uncertainty lab."""

    st.header("Weather Model")
    c1, c2, c3, c4 = st.columns(4)
    rain_probability = c1.slider("Rain probability per lap", 0.0, 1.0, 0.12, 0.01)
    air_temp = c2.slider("Air temperature C", 5.0, 40.0, 24.0, 1.0)
    track_temp = c3.slider("Track temperature C", 5.0, 60.0, 34.0, 1.0)
    seed = c4.number_input("Seed", 1, 999999, 42)
    laps = st.slider("Weather timeline laps", 10, 78, 58)
    weather = WeatherModel(rain_probability, air_temp, track_temp, int(seed))
    rows = []
    for lap in range(1, laps + 1):
        state = weather.step()
        rows.append({"Lap": lap, "Wetness": state.wetness, "Track temp C": state.track_temp_c, "Raining": state.raining, "Wind kph": state.wind_speed_kph})
    df = pd.DataFrame(rows)
    fig = px.line(df, x="Lap", y=["Wetness", "Track temp C"], title="Weather uncertainty timeline")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_safety_car() -> None:
    """Render safety car and VSC lab."""

    st.header("Safety Car and VSC")
    c1, c2, c3, c4 = st.columns(4)
    sc_p = c1.slider("Safety car probability/lap", 0.0, 0.30, 0.03, 0.01)
    vsc_p = c2.slider("VSC probability/lap", 0.0, 0.40, 0.04, 0.01)
    pit_mult = c3.slider("SC pit-loss multiplier", 0.30, 1.00, 0.62, 0.01)
    seed = c4.number_input("SC seed", 1, 999999, 123)
    laps = st.slider("Neutralisation timeline laps", 10, 78, 58)
    model = SafetyCarModel(sc_p, vsc_p, pit_mult, int(seed))
    rows = []
    for lap in range(1, laps + 1):
        state = model.step()
        rows.append({"Lap": lap, "Safety car": state.safety_car, "VSC": state.vsc, "Lap-time multiplier": state.lap_time_multiplier, "Pit-loss multiplier": state.pit_loss_multiplier})
    df = pd.DataFrame(rows)
    fig = px.bar(df, x="Lap", y="Lap-time multiplier", color="Safety car", title="Neutralisation impact by lap")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)
    st.dataframe(df[df["Safety car"] | df["VSC"]], use_container_width=True, hide_index=True)
    panel("Restart effect scaffold", "Restart effects are currently documented as planned. The neutralisation model captures slower laps and reduced pit-loss but does not yet model restart tyre temperature or overtaking risk.")


def render_strategy_lab() -> None:
    """Render strategy lab."""

    st.header("Strategy Lab")
    laps = st.slider("Race laps", 30, 78, 58, key="strategy_laps")
    pit_loss = st.slider("Pit loss seconds", 15.0, 35.0, 22.0, 0.5, key="strategy_pit_loss")
    strategies = generate_candidate_strategies(laps)
    rows = []
    tyre = TyreModel()
    for strategy in strategies:
        stint_lengths = []
        edges = [0, *strategy.pit_laps, laps]
        total_deg = 0.0
        for i in range(len(edges) - 1):
            stint = edges[i + 1] - edges[i]
            stint_lengths.append(stint)
            total_deg += tyre.lap_delta_s(strategy.compounds[min(i, len(strategy.compounds) - 1)], stint, 35.0)
        risk = 100 * (strategy.stops / 3) + max(stint_lengths) * 0.4
        rows.append({"Strategy": strategy.name, "Stops": strategy.stops, "Compounds": "-".join(strategy.compounds), "Pit laps": str(strategy.pit_laps), "Stint lengths": str(stint_lengths), "Tyre loss index": round(total_deg, 3), "Pit exposure [s]": round(strategy.stops * pit_loss, 2), "Risk score": round(risk, 2)})
    df = pd.DataFrame(rows).sort_values(["Risk score", "Tyre loss index"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    fig = px.bar(df, x="Strategy", y=["Tyre loss index", "Pit exposure [s]", "Risk score"], title="Risk-aware strategy comparison")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)
    old_age = st.slider("Old tyre age for undercut analysis", 5, 45, 24)
    old_delta = tyre.lap_delta_s("medium", old_age, 35.0)
    new_delta = tyre.lap_delta_s("hard", 1, 35.0)
    u_delta = undercut_delta_s(old_age, new_delta, old_delta)
    o_delta = overcut_delta_s(track_position_gain_s=1.2, tyre_loss_s=max(0.0, old_delta - new_delta))
    c1, c2 = st.columns(2)
    c1.metric("Undercut delta", f"{u_delta:.3f} s")
    c2.metric("Overcut delta", f"{o_delta:.3f} s")


def render_monte_carlo() -> None:
    """Render Monte Carlo lab."""

    st.header("Monte Carlo Lab")
    configs = available_configs()
    if not configs:
        st.warning("No configs available.")
        return
    config_path = st.selectbox("Monte Carlo config", configs, index=min(2, len(configs) - 1))
    c1, c2, c3 = st.columns(3)
    runs = c1.slider("Runs", 10, 1000, 100, 10)
    seed = c2.number_input("Seed", 1, 999999, 2026)
    target = c3.text_input("Target driver", "NOR").upper()
    config = load_config(config_path)
    summary = MonteCarloSimulation(config, runs=int(runs), seed=int(seed)).run(target_driver_id=target)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Expected race time", format_time(summary.expected_time_s))
    k2.metric("Expected position", f"{summary.expected_position:.2f}")
    k3.metric("Confidence interval", f"{summary.confidence_interval_s[0]:.1f} - {summary.confidence_interval_s[1]:.1f} s")
    k4.metric("Beat target probability", "N/A" if summary.probability_beating_target is None else f"{summary.probability_beating_target:.1%}")
    profile = pd.DataFrame([summary.strategy_risk_profile])
    st.dataframe(profile, use_container_width=True, hide_index=True)
    synthetic = pd.DataFrame({"Race time [s]": [summary.strategy_risk_profile["p05_time_s"], summary.strategy_risk_profile["p50_time_s"], summary.strategy_risk_profile["p95_time_s"]], "Percentile": ["P05", "P50", "P95"]})
    fig = px.bar(synthetic, x="Percentile", y="Race time [s]", title="Monte Carlo risk profile")
    st.plotly_chart(plotly_layout(fig), use_container_width=True)
    panel("Randomization scope", "The current Monte Carlo layer varies seeded stochastic weather, safety car and traffic effects. Pace, degradation and pit-loss randomization are extension points for calibration and are labelled as prototype where not yet explicit.")


def render_telemetry_data() -> None:
    """Render telemetry and data lab."""

    st.header("Telemetry and Data")
    panel("Data honesty", "CSV input is supported for user-provided lap data. FastF1 and OpenF1 integrations are scaffolds and no official team data is fabricated or bundled.")
    upload = st.file_uploader("Upload lap-time CSV with driver_id, lap, lap_time_s", type=["csv"])
    if upload is not None:
        temp_path = RESULTS_DIR / "uploaded_laps.csv"
        RESULTS_DIR.mkdir(exist_ok=True)
        temp_path.write_bytes(upload.getvalue())
        try:
            frame = load_lap_csv(temp_path)
            normalized = normalize_lap_times(frame)
            pace = estimate_driver_pace(frame)
            st.subheader("Validation")
            st.success("CSV schema validated.")
            st.subheader("Normalized lap times")
            st.dataframe(normalized, use_container_width=True, hide_index=True)
            st.subheader("Driver pace estimation")
            st.dataframe(pace, use_container_width=True, hide_index=True)
            fig = px.line(normalized, x="lap", y="normalized_lap_time_s", color="driver_id", title="Lap-time normalization")
            st.plotly_chart(plotly_layout(fig), use_container_width=True)
        except Exception as exc:
            st.error(f"CSV validation failed: {exc}")
    else:
        example = pd.DataFrame({"driver_id": ["DRV1", "DRV1", "DRV2", "DRV2"], "lap": [1, 2, 1, 2], "lap_time_s": [91.2, 91.4, 91.8, 91.7]})
        st.dataframe(example, use_container_width=True, hide_index=True)


def render_engineering_report(last_result: RaceResult | None) -> None:
    """Render report generation section."""

    st.header("Engineering Report")
    if last_result is None:
        st.info("Run a race simulation first to populate the report.")
        return
    frame = result_frame(last_result)
    classification = final_classification(last_result)
    metrics = last_result.metrics
    report = f"""# F1Sim Engineering Report

## Summary

- Total race time: {metrics.total_race_time_s:.3f} s
- Pit stop count: {metrics.pit_stop_count}
- Compound sequence: {' - '.join(metrics.compound_sequence)}
- Stint lengths: {metrics.stint_lengths}
- Degradation rate: {metrics.degradation_rate_s_per_lap:.4f} s/lap
- Traffic loss: {metrics.traffic_loss_s:.3f} s
- Pit loss: {metrics.pit_loss_s:.3f} s
- Undercut delta: {metrics.undercut_delta_s:.3f} s
- Overcut delta: {metrics.overcut_delta_s:.3f} s

## Assumptions and limitations

This report uses transparent open-model assumptions. It does not use or claim official team telemetry. Traffic, penalties, retirements and restart effects are scaffolds unless explicitly calibrated.
"""
    st.download_button("Download lap history CSV", frame.to_csv(index=False), "lap_history.csv", "text/csv")
    st.download_button("Download classification CSV", classification.to_csv(index=False), "classification.csv", "text/csv")
    st.download_button("Download Markdown report", report, "engineering_report.md", "text/markdown")
    st.markdown(report)


def render_about() -> None:
    """Render reproducibility and roadmap section."""

    st.header("About and Reproducibility")
    panel("Deterministic seeds", "Every YAML experiment and dashboard run should specify a seed. This makes race states, weather draws, SC/VSC draws and Monte Carlo summaries reproducible.")
    panel("Data sources", "Public data integrations should cite FastF1, OpenF1 or uploaded CSV provenance. The repository must not include invented official team data.")
    panel("Research roadmap", "Calibration against public historical data, richer traffic modelling, penalty/reliability models, Bayesian optimization and multi-objective Pareto reporting are planned work.")


def render_dashboard() -> None:
    """Render the complete multipage Streamlit platform."""

    configure_page()
    with st.sidebar:
        st.title("F1Sim")
        st.caption("Race strategy engineering platform")
        section = st.radio(
            "Navigation",
            [
                "Platform Overview",
                "Race Simulation Dashboard",
                "Tyre Engineering",
                "Fuel Model",
                "Weather Model",
                "Safety Car / VSC",
                "Strategy Lab",
                "Monte Carlo Lab",
                "Telemetry & Data",
                "Engineering Report",
                "About / Reproducibility",
            ],
        )
        st.markdown("---")
        st.caption("Synthetic configs are clearly labelled. No official team data is fabricated.")

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if section == "Platform Overview":
        render_overview()
    elif section == "Race Simulation Dashboard":
        st.session_state.last_result = render_race_dashboard()
    elif section == "Tyre Engineering":
        render_tyre_engineering()
    elif section == "Fuel Model":
        render_fuel_model()
    elif section == "Weather Model":
        render_weather_model()
    elif section == "Safety Car / VSC":
        render_safety_car()
    elif section == "Strategy Lab":
        render_strategy_lab()
    elif section == "Monte Carlo Lab":
        render_monte_carlo()
    elif section == "Telemetry & Data":
        render_telemetry_data()
    elif section == "Engineering Report":
        render_engineering_report(st.session_state.last_result)
    else:
        render_about()


if __name__ == "__main__":
    render_dashboard()
