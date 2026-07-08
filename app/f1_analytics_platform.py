"""Streamlit entrypoint for the Formula 1 Race Simulation Engineering Platform.

Run locally with:
    streamlit run app/f1_analytics_platform.py

This app is intentionally lightweight at startup so Streamlit Cloud can boot reliably.
It uses the repository's `f1sim` simulation package and avoids training heavy ML models during
initial page load.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from f1sim.data.config import RaceConfig, load_race_config
from f1sim.simulation.engine import RaceResult, RaceSimulation
from f1sim.simulation.monte_carlo import MonteCarloSimulation, MonteCarloSummary

CONFIG_DIR = ROOT / "configs" / "experiments"
DEFAULT_CONFIG = CONFIG_DIR / "dry_race.yml"


st.set_page_config(
    page_title="F1 Race Simulation Engineering",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def available_configs() -> list[str]:
    """Return available YAML experiment config paths."""

    if not CONFIG_DIR.exists():
        return []
    return [str(path.relative_to(ROOT)) for path in sorted(CONFIG_DIR.glob("*.yml"))]


@st.cache_data(show_spinner=False)
def load_config(config_path: str) -> RaceConfig:
    """Load a race config with Streamlit caching."""

    return load_race_config(ROOT / config_path)


@st.cache_data(show_spinner=True)
def run_race(config_path: str) -> RaceResult:
    """Run one deterministic race simulation."""

    return RaceSimulation(load_config(config_path)).run()


@st.cache_data(show_spinner=True)
def run_monte_carlo(config_path: str, runs: int, seed: int) -> MonteCarloSummary:
    """Run Monte Carlo simulation for the selected config."""

    config = load_config(config_path).model_copy(update={"seed": int(seed)})
    return MonteCarloSimulation(config, runs=int(runs), seed=int(seed)).run()


def format_time(seconds: float) -> str:
    """Format race time in mm:ss.sss."""

    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes}:{remainder:06.3f}"


def build_lap_frame(result: RaceResult) -> pd.DataFrame:
    """Create a normalized lap-history dataframe for visualization."""

    frame = pd.DataFrame(result.lap_history)
    if frame.empty:
        return frame
    return frame.rename(
        columns={
            "driver_id": "Driver",
            "lap": "Lap",
            "lap_time_s": "LapTimeSeconds",
            "total_time_s": "TotalTimeSeconds",
            "compound": "Compound",
            "tyre_age_laps": "TyreAge",
            "position": "Position",
            "gap_to_leader_s": "GapToLeaderSeconds",
            "wetness": "Wetness",
            "safety_car": "SafetyCar",
            "vsc": "VSC",
            "pit_stops": "PitStops",
        }
    )


def render_header() -> None:
    """Render the page header."""

    st.title("🏁 Formula 1 Race Simulation Engineering Platform")
    st.caption(
        "Open, reproducible race strategy simulation for tyre degradation, fuel effect, "
        "weather uncertainty, safety-car scenarios and Monte Carlo strategy risk."
    )
    st.info(
        "This platform uses transparent open-model assumptions. It does not claim access to "
        "private team data and should not be interpreted as official Formula 1 telemetry."
    )


def render_sidebar() -> tuple[str, int, int]:
    """Render sidebar controls."""

    configs = available_configs()
    if not configs:
        st.sidebar.error("No experiment configs found under configs/experiments/.")
        st.stop()

    default = str(DEFAULT_CONFIG.relative_to(ROOT)) if DEFAULT_CONFIG.exists() else configs[0]
    selected_config = st.sidebar.selectbox(
        "Experiment config",
        configs,
        index=configs.index(default) if default in configs else 0,
    )
    monte_carlo_runs = st.sidebar.slider("Monte Carlo runs", 10, 1000, 100, step=10)
    seed = st.sidebar.number_input("Random seed", min_value=1, max_value=999999, value=42)
    st.sidebar.markdown("---")
    st.sidebar.caption("Change the YAML config to compare dry, wet and strategy-risk scenarios.")
    return selected_config, int(monte_carlo_runs), int(seed)


def render_metrics(result: RaceResult, config: RaceConfig) -> None:
    """Render engineering KPIs."""

    leader = result.classification[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Winner", leader.driver_id)
    c2.metric("Race time", format_time(leader.total_time_s))
    c3.metric("Pit stops", leader.pit_stops)
    c4.metric("Race laps", config.laps)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Traffic loss", f"{result.metrics.traffic_loss_s:.2f}s")
    m2.metric("Pit-loss exposure", f"{result.metrics.pit_loss_s:.2f}s")
    m3.metric("Degradation rate", f"{result.metrics.degradation_rate_s_per_lap:.3f}s/lap")
    m4.metric("Risk percentile", f"{result.metrics.risk_percentile:.0f}")


def render_classification(result: RaceResult) -> None:
    """Render final classification table."""

    rows: list[dict[str, Any]] = []
    leader_time = result.classification[0].total_time_s
    for driver in result.classification:
        rows.append(
            {
                "Position": driver.position,
                "Driver": driver.driver_id,
                "TotalTime": format_time(driver.total_time_s),
                "GapToLeaderSeconds": round(driver.total_time_s - leader_time, 3),
                "PitStops": driver.pit_stops,
                "FinalCompound": driver.compound,
                "TrafficLossSeconds": round(driver.traffic_loss_s, 3),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_charts(frame: pd.DataFrame) -> None:
    """Render simulation charts."""

    if frame.empty:
        st.warning("No lap history was produced by the simulation.")
        return

    tab_laps, tab_positions, tab_weather, tab_stints = st.tabs(
        ["Lap time", "Position", "Weather / neutralisation", "Tyres"]
    )

    with tab_laps:
        fig = px.line(
            frame,
            x="Lap",
            y="LapTimeSeconds",
            color="Driver",
            title="Lap-time evolution",
            markers=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_positions:
        fig = px.line(
            frame,
            x="Lap",
            y="Position",
            color="Driver",
            title="Race position evolution",
            markers=True,
        )
        fig.update_yaxes(autorange="reversed", dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    with tab_weather:
        weather = frame.groupby("Lap", as_index=False).agg(
            Wetness=("Wetness", "mean"),
            SafetyCar=("SafetyCar", "max"),
            VSC=("VSC", "max"),
        )
        fig = px.line(weather, x="Lap", y="Wetness", title="Track wetness")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(weather[weather["SafetyCar"] | weather["VSC"]], use_container_width=True, hide_index=True)

    with tab_stints:
        stint_frame = frame[["Lap", "Driver", "Compound", "TyreAge", "PitStops"]].copy()
        fig = px.scatter(
            stint_frame,
            x="Lap",
            y="Driver",
            color="Compound",
            size="TyreAge",
            title="Tyre compound and stint age",
        )
        st.plotly_chart(fig, use_container_width=True)


def render_monte_carlo(config_path: str, runs: int, seed: int) -> None:
    """Render Monte Carlo summary."""

    with st.spinner("Running Monte Carlo simulations..."):
        summary = run_monte_carlo(config_path, runs, seed)
    st.subheader("Monte Carlo strategy risk")
    c1, c2, c3 = st.columns(3)
    c1.metric("Runs", summary.runs)
    c2.metric("Expected race time", format_time(summary.expected_time_s))
    c3.metric(
        "90% interval",
        f"{summary.confidence_interval_s[0]:.1f}s – {summary.confidence_interval_s[1]:.1f}s",
    )
    st.json(summary.strategy_risk_profile)


def main() -> None:
    """Render the Streamlit app."""

    render_header()
    config_path, mc_runs, seed = render_sidebar()

    try:
        config = load_config(config_path).model_copy(update={"seed": seed})
        result = RaceSimulation(config).run()
    except Exception as exc:
        st.error("The selected simulation config could not be executed.")
        st.exception(exc)
        st.stop()

    st.subheader(config.name.replace("_", " ").title())
    render_metrics(result, config)

    st.markdown("---")
    st.subheader("Final classification")
    render_classification(result)

    st.markdown("---")
    render_charts(build_lap_frame(result))

    st.markdown("---")
    if st.button("Run Monte Carlo risk analysis", type="primary"):
        render_monte_carlo(config_path, mc_runs, seed)

    st.caption(
        "F1Sim platform • reproducible YAML experiments • transparent assumptions • estimates, not guarantees."
    )


if __name__ == "__main__":
    main()
