"""Ultimate Streamlit command center for the F1Sim platform.

The module is intentionally product-oriented: it presents the simulation engine as a premium
Formula 1 strategy, prediction, telemetry and reporting workspace. It uses transparent synthetic
examples where real public data is not connected.
"""

from __future__ import annotations

from dataclasses import asdict
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

DRIVER_PALETTE = {
    "VER": "#3671c6",
    "NOR": "#ff8700",
    "LEC": "#e10600",
    "HAM": "#00d2be",
    "PIA": "#ff8700",
    "ALO": "#229971",
    "ONE_STOP": "#facc15",
    "TWO_STOP": "#38bdf8",
}


def configure_page() -> None:
    """Configure Streamlit and inject the premium visual system."""

    st.set_page_config(page_title="F1Sim Pro Race Intelligence", page_icon="F1", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --red: #e10600;
            --red-soft: rgba(225, 6, 0, 0.18);
            --carbon: #05070d;
            --carbon-2: #0b1019;
            --carbon-3: #121826;
            --text: #f8fafc;
            --muted: #9ca3af;
            --line: rgba(255,255,255,0.10);
            --green: #22c55e;
            --amber: #f59e0b;
            --blue: #38bdf8;
        }
        .stApp {
            background:
                radial-gradient(circle at 82% -8%, rgba(225,6,0,0.28), transparent 25rem),
                radial-gradient(circle at 5% 15%, rgba(56,189,248,0.10), transparent 27rem),
                linear-gradient(145deg, #020307 0%, #05070d 42%, #090e17 100%);
            color: var(--text);
        }
        [data-testid="stHeader"] { background: rgba(2,3,7,0.72); backdrop-filter: blur(18px); }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070911 0%, #0c111b 100%);
            border-right: 1px solid rgba(225,6,0,0.32);
        }
        .block-container { max-width: 1580px; padding-top: 1rem; padding-bottom: 3rem; }
        h1, h2, h3 { letter-spacing: -0.045em; }
        .topbar {
            display: flex; justify-content: space-between; align-items: center; gap: 1rem;
            padding: .85rem 1rem; border: 1px solid var(--line); border-radius: 22px;
            background: rgba(10,15,25,.72); box-shadow: 0 20px 70px rgba(0,0,0,.28);
            margin-bottom: 1rem;
        }
        .brand { font-weight: 900; letter-spacing: .14em; text-transform: uppercase; }
        .live-dot { width: .55rem; height: .55rem; background: var(--green); border-radius: 999px; display: inline-block; margin-right: .45rem; box-shadow: 0 0 18px rgba(34,197,94,.9); }
        .hero-pro {
            position: relative; overflow: hidden; border: 1px solid rgba(225,6,0,.35);
            border-radius: 34px; padding: 2rem 2.2rem;
            background:
                linear-gradient(135deg, rgba(225,6,0,.23), rgba(15,23,42,.88) 45%, rgba(2,6,23,.95)),
                repeating-linear-gradient(110deg, transparent, transparent 20px, rgba(255,255,255,.025) 21px, rgba(255,255,255,.025) 22px);
            box-shadow: 0 34px 110px rgba(0,0,0,.42), inset 0 1px 0 rgba(255,255,255,.08);
            margin-bottom: 1rem;
        }
        .hero-pro h1 { margin: 0; font-size: clamp(2.5rem, 5vw, 5.4rem); line-height: .94; }
        .hero-pro p { max-width: 980px; color: #d1d5db; font-size: 1.02rem; line-height: 1.7; margin: 1rem 0 0; }
        .badge-row { margin-top: 1.1rem; }
        .badge {
            display: inline-block; padding: .42rem .72rem; margin: 0 .45rem .5rem 0;
            border: 1px solid rgba(255,255,255,.12); border-radius: 999px; background: rgba(255,255,255,.05);
            color: #e5e7eb; font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase;
        }
        .section-card {
            border: 1px solid var(--line); border-radius: 24px; padding: 1.05rem 1.15rem;
            background: linear-gradient(180deg, rgba(17,24,39,.86), rgba(8,13,22,.82));
            box-shadow: 0 18px 60px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.05);
            height: 100%;
        }
        .section-card h3 { margin: 0 0 .45rem 0; }
        .section-card p { color: var(--muted); line-height: 1.56; margin: 0; font-size: .92rem; }
        .status-strip {
            display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .8rem; margin: 1rem 0;
        }
        .status-cell {
            border: 1px solid var(--line); border-radius: 18px; padding: .9rem 1rem;
            background: rgba(17,24,39,.78);
        }
        .status-cell .label { color: var(--muted); font-size: .76rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; }
        .status-cell .value { font-size: 1.7rem; font-weight: 900; margin-top: .2rem; }
        .panel-note { border-left: 4px solid var(--red); background: rgba(225,6,0,.08); padding: .9rem 1rem; border-radius: 16px; color: #fecaca; }
        div[data-testid="stMetric"] {
            border: 1px solid var(--line); border-radius: 20px; padding: 14px 16px;
            background: linear-gradient(180deg, rgba(31,41,55,.95), rgba(17,24,39,.86));
        }
        div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 18px; overflow: hidden; }
        .small-muted { color: var(--muted); font-size: .86rem; }
        @media (max-width: 900px) { .status-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def available_configs() -> list[str]:
    """Return available YAML experiment configs."""

    if not CONFIG_DIR.exists():
        return []
    return [str(path.relative_to(ROOT)) for path in sorted(CONFIG_DIR.glob("*.yml"))]


@st.cache_data(show_spinner=False)
def load_config(config_path: str):
    """Load and cache a race configuration."""

    return load_race_config(ROOT / config_path)


@st.cache_data(show_spinner=True)
def run_simulation(config_path: str, seed: int) -> RaceResult:
    """Run and cache one deterministic race simulation."""

    config = load_config(config_path).model_copy(update={"seed": seed})
    return RaceSimulation(config).run()


def fmt_time(seconds: float) -> str:
    """Format seconds as mm:ss.mmm."""

    minutes = int(seconds // 60)
    return f"{minutes}:{seconds - minutes * 60:06.3f}"


def chart_layout(fig: go.Figure) -> go.Figure:
    """Apply the F1Sim Pro chart style."""

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,15,25,.78)",
        font={"color": "#f8fafc"},
        margin={"l": 18, "r": 18, "t": 54, "b": 34},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.08)", zerolinecolor="rgba(255,255,255,.12)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.08)", zerolinecolor="rgba(255,255,255,.12)")
    return fig


def topbar() -> None:
    """Render product top bar."""

    st.markdown(
        """
        <div class="topbar">
          <div class="brand">F1Sim Pro Intelligence</div>
          <div class="small-muted"><span class="live-dot"></span>Simulation environment online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, badges: list[str]) -> None:
    """Render hero area."""

    badge_html = "".join(f"<span class='badge'>{badge}</span>" for badge in badges)
    st.markdown(
        f"<div class='hero-pro'><h1>{title}</h1><p>{subtitle}</p><div class='badge-row'>{badge_html}</div></div>",
        unsafe_allow_html=True,
    )


def status_strip(cells: list[tuple[str, str]]) -> None:
    """Render compact status cards."""

    body = "".join(f"<div class='status-cell'><div class='label'>{label}</div><div class='value'>{value}</div></div>" for label, value in cells)
    st.markdown(f"<div class='status-strip'>{body}</div>", unsafe_allow_html=True)


def lap_frame(result: RaceResult) -> pd.DataFrame:
    """Return simulation lap history."""

    return pd.DataFrame(result.lap_history)


def classification_frame(result: RaceResult) -> pd.DataFrame:
    """Return formatted final classification."""

    leader_time = result.classification[0].total_time_s
    rows = []
    for driver in result.classification:
        rows.append(
            {
                "Pos": driver.position,
                "Driver": driver.driver_id,
                "Race time": fmt_time(driver.total_time_s),
                "Gap": round(driver.total_time_s - leader_time, 3),
                "Stops": driver.pit_stops,
                "Tyre": driver.compound,
                "Traffic loss": round(driver.traffic_loss_s, 3),
            }
        )
    return pd.DataFrame(rows)


def prediction_model(result: RaceResult) -> pd.DataFrame:
    """Build a transparent synthetic prediction table from simulated classification."""

    rows = []
    base = [0.34, 0.26, 0.18, 0.12, 0.07, 0.03]
    for idx, driver in enumerate(result.classification):
        p = base[min(idx, len(base) - 1)]
        rows.append(
            {
                "Driver": driver.driver_id,
                "Win probability": p,
                "Podium probability": min(0.98, p + 0.34),
                "Expected position": idx + 1 + (0.12 * idx),
                "Risk index": round(100 * (1 - p), 1),
            }
        )
    total = sum(row["Win probability"] for row in rows)
    for row in rows:
        row["Win probability"] = row["Win probability"] / total
    return pd.DataFrame(rows)


def render_home(config_path: str, seed: int) -> RaceResult:
    """Render the command center landing page."""

    result = run_simulation(config_path, seed)
    frame = lap_frame(result)
    leader = result.classification[0]
    predictions = prediction_model(result)

    hero(
        "Ultimate Formula 1 Race Intelligence Platform",
        "A premium command center for race prediction, lap-by-lap simulation, strategy optimization, tyre degradation, weather uncertainty, safety car risk, telemetry ingestion and engineering reporting. Synthetic examples are labelled; no official team data is fabricated.",
        ["Prediction", "Live timing", "Strategy", "Telemetry", "Championship", "Reports"],
    )
    status_strip(
        [
            ("Predicted winner", leader.driver_id),
            ("Race time", fmt_time(leader.total_time_s)),
            ("Current scenario", config_path.split("/")[-1].replace(".yml", "")),
            ("Data policy", "Transparent"),
        ]
    )

    left, right = st.columns([0.58, 0.42])
    with left:
        fig = px.line(frame, x="lap", y="position", color="driver_id", markers=True, title="Race order evolution")
        fig.update_yaxes(autorange="reversed", dtick=1)
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    with right:
        fig = px.bar(predictions, x="Driver", y="Win probability", text=predictions["Win probability"].map(lambda value: f"{value:.0%}"), title="Race win prediction")
        fig.update_traces(marker_color="#e10600", textposition="outside")
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='section-card'><h3>Race Predictor</h3><p>Winner, podium, expected position and risk profile from the selected simulation scenario.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='section-card'><h3>Strategy Room</h3><p>Compare one-stop, two-stop and three-stop plans with pit exposure, degradation and undercut deltas.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='section-card'><h3>Telemetry Workstation</h3><p>Upload lap-time CSV files, normalize pace and estimate driver performance without inventing official data.</p></div>", unsafe_allow_html=True)

    st.subheader("Final classification")
    st.dataframe(classification_frame(result), use_container_width=True, hide_index=True)
    return result


def render_race_center(config_path: str, seed: int) -> RaceResult:
    """Render full race simulation center."""

    result = run_simulation(config_path, seed)
    frame = lap_frame(result)
    st.header("Race Simulation Center")
    st.caption("Lap-by-lap race clock, position, gaps, tyre state, weather state and neutralisation markers.")
    leader = result.classification[0]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Leader", leader.driver_id)
    k2.metric("Total race time", fmt_time(leader.total_time_s))
    k3.metric("Pit stops", leader.pit_stops)
    k4.metric("Traffic loss", f"{leader.traffic_loss_s:.2f}s")

    tabs = st.tabs(["Timeline", "Lap pace", "Position", "Gaps", "Stints", "Pit stops", "Classification"])
    with tabs[0]:
        timeline = frame.groupby("lap", as_index=False).agg(wetness=("wetness", "mean"), safety_car=("safety_car", "max"), vsc=("vsc", "max"))
        fig = px.line(timeline, x="lap", y="wetness", title="Race timeline: wetness with SC/VSC markers")
        for lap in timeline.loc[timeline["safety_car"], "lap"]:
            fig.add_vline(x=lap, line_color="#e10600", line_dash="dash")
        for lap in timeline.loc[timeline["vsc"], "lap"]:
            fig.add_vline(x=lap, line_color="#f59e0b", line_dash="dot")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    with tabs[1]:
        st.plotly_chart(chart_layout(px.line(frame, x="lap", y="lap_time_s", color="driver_id", title="Lap-time evolution")), use_container_width=True)
    with tabs[2]:
        fig = px.line(frame, x="lap", y="position", color="driver_id", markers=True, title="Position chart")
        fig.update_yaxes(autorange="reversed", dtick=1)
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    with tabs[3]:
        st.plotly_chart(chart_layout(px.line(frame, x="lap", y="gap_to_leader_s", color="driver_id", title="Gap to leader")), use_container_width=True)
    with tabs[4]:
        st.plotly_chart(chart_layout(px.scatter(frame, x="lap", y="driver_id", color="compound", size="tyre_age_laps", title="Tyre stint timeline")), use_container_width=True)
    with tabs[5]:
        st.dataframe(pd.DataFrame([asdict(event) for event in result.pit_events]), use_container_width=True, hide_index=True)
    with tabs[6]:
        st.dataframe(classification_frame(result), use_container_width=True, hide_index=True)
    return result


def render_prediction_center(config_path: str, seed: int) -> None:
    """Render race prediction cockpit."""

    result = run_simulation(config_path, seed)
    predictions = prediction_model(result)
    st.header("Prediction Center")
    st.caption("Transparent scenario prediction derived from simulation outputs. It is not official betting, team or FIA data.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Model source", "Simulation scenario")
    c2.metric("Drivers evaluated", len(predictions))
    c3.metric("Top pick", predictions.sort_values("Win probability", ascending=False).iloc[0]["Driver"])
    fig = px.bar(predictions, x="Driver", y=["Win probability", "Podium probability"], title="Win and podium probability")
    st.plotly_chart(chart_layout(fig), use_container_width=True)
    st.dataframe(predictions, use_container_width=True, hide_index=True)


def render_strategy_room() -> None:
    """Render strategy room."""

    st.header("Strategy Room")
    laps = st.slider("Race laps", 30, 78, 58)
    pit_loss = st.slider("Pit loss", 15.0, 35.0, 22.0, 0.5)
    old_age = st.slider("Tyre age for undercut model", 5, 45, 24)
    tyre = TyreModel()
    rows = []
    for strategy in generate_candidate_strategies(laps):
        edges = [0, *strategy.pit_laps, laps]
        stints = [edges[index + 1] - edges[index] for index in range(len(edges) - 1)]
        tyre_loss = sum(tyre.lap_delta_s(strategy.compounds[min(i, len(strategy.compounds) - 1)], stint, 35.0) for i, stint in enumerate(stints))
        risk = round(strategy.stops * pit_loss + tyre_loss + max(stints) * 0.35, 2)
        rows.append({"Strategy": strategy.name, "Stops": strategy.stops, "Compounds": " / ".join(strategy.compounds), "Pit laps": str(strategy.pit_laps), "Stints": str(stints), "Pit exposure": strategy.stops * pit_loss, "Tyre loss": round(tyre_loss, 3), "Risk score": risk})
    df = pd.DataFrame(rows).sort_values("Risk score")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.plotly_chart(chart_layout(px.bar(df, x="Strategy", y=["Pit exposure", "Tyre loss", "Risk score"], title="Strategy comparison")), use_container_width=True)
    old_delta = tyre.lap_delta_s("medium", old_age, 35.0)
    new_delta = tyre.lap_delta_s("hard", 1, 35.0)
    u_delta = undercut_delta_s(old_age, new_delta, old_delta)
    o_delta = overcut_delta_s(1.2, max(0.0, old_delta - new_delta))
    k1, k2 = st.columns(2)
    k1.metric("Undercut delta", f"{u_delta:.3f}s")
    k2.metric("Overcut delta", f"{o_delta:.3f}s")


def render_engineering_labs() -> None:
    """Render tyre, fuel, weather and safety-car engineering labs."""

    st.header("Engineering Labs")
    tab_tyre, tab_fuel, tab_weather, tab_sc = st.tabs(["Tyres", "Fuel", "Weather", "Safety Car"])
    with tab_tyre:
        model = TyreModel()
        track_temp = st.slider("Track temperature", 15.0, 55.0, 35.0, 1.0)
        wetness = st.slider("Wetness", 0.0, 1.0, 0.0, 0.05)
        max_age = st.slider("Tyre age range", 5, 70, 45)
        rows = [{"Compound": name, "Age": age, "Pace loss": model.lap_delta_s(name, age, track_temp, wetness)} for name in COMPOUNDS for age in range(max_age + 1)]
        st.plotly_chart(chart_layout(px.line(pd.DataFrame(rows), x="Age", y="Pace loss", color="Compound", title="Compound degradation curves")), use_container_width=True)
    with tab_fuel:
        fuel = FuelModel(
            start_kg=st.slider("Start fuel kg", 20.0, 115.0, 100.0),
            burn_kg_per_lap=st.slider("Burn kg/lap", 0.5, 4.0, 1.7),
            lap_time_s_per_kg=st.slider("Lap-time effect s/kg", 0.005, 0.08, 0.035),
            safety_margin_kg=st.slider("Safety margin kg", 0.0, 8.0, 2.0),
        )
        laps = st.slider("Fuel timeline laps", 10, 78, 58)
        df = pd.DataFrame([{"Lap": lap, "Fuel kg": fuel.fuel_at_lap_start(lap), "Lap delta": fuel.lap_delta_s(lap)} for lap in range(1, laps + 1)])
        st.plotly_chart(chart_layout(px.line(df, x="Lap", y=["Fuel kg", "Lap delta"], title="Fuel mass effect")), use_container_width=True)
    with tab_weather:
        model = WeatherModel(st.slider("Rain probability", 0.0, 1.0, 0.12), 24.0, 34.0, st.number_input("Weather seed", 1, 999999, 42))
        rows = []
        for lap in range(1, 59):
            state = model.step()
            rows.append({"Lap": lap, "Wetness": state.wetness, "Track temp": state.track_temp_c, "Raining": state.raining})
        st.plotly_chart(chart_layout(px.line(pd.DataFrame(rows), x="Lap", y=["Wetness", "Track temp"], title="Weather timeline")), use_container_width=True)
    with tab_sc:
        model = SafetyCarModel(st.slider("SC probability", 0.0, 0.3, 0.03), st.slider("VSC probability", 0.0, 0.4, 0.04), st.slider("SC pit multiplier", 0.3, 1.0, 0.62), 123)
        rows = []
        for lap in range(1, 59):
            state = model.step()
            rows.append({"Lap": lap, "Safety car": state.safety_car, "VSC": state.vsc, "Lap multiplier": state.lap_time_multiplier, "Pit multiplier": state.pit_loss_multiplier})
        df = pd.DataFrame(rows)
        st.plotly_chart(chart_layout(px.bar(df, x="Lap", y="Lap multiplier", color="Safety car", title="Neutralisation impact")), use_container_width=True)


def render_monte_carlo(config_path: str, seed: int) -> None:
    """Render Monte Carlo cockpit."""

    st.header("Monte Carlo Cockpit")
    runs = st.slider("Runs", 10, 1000, 150, 10)
    target = st.text_input("Target driver", "NOR").upper()
    summary = MonteCarloSimulation(load_config(config_path), runs=runs, seed=seed).run(target_driver_id=target)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expected time", fmt_time(summary.expected_time_s))
    c2.metric("Expected position", f"{summary.expected_position:.2f}")
    c3.metric("Interval", f"{summary.confidence_interval_s[0]:.1f}-{summary.confidence_interval_s[1]:.1f}s")
    c4.metric("Beat target", "N/A" if summary.probability_beating_target is None else f"{summary.probability_beating_target:.1%}")
    df = pd.DataFrame([summary.strategy_risk_profile]).T.reset_index()
    df.columns = ["Metric", "Race time"]
    st.plotly_chart(chart_layout(px.bar(df, x="Metric", y="Race time", title="Risk percentiles")), use_container_width=True)


def render_telemetry_and_reports(last_result: RaceResult | None) -> None:
    """Render telemetry upload and report exports."""

    st.header("Telemetry and Report Center")
    tab_csv, tab_report = st.tabs(["Data ingestion", "Engineering report"])
    with tab_csv:
        st.markdown("<div class='panel-note'>CSV input must include driver_id, lap and lap_time_s. Public telemetry integrations are scaffolds; no private team data is fabricated.</div>", unsafe_allow_html=True)
        upload = st.file_uploader("Upload lap-time CSV", type=["csv"])
        if upload is None:
            example = pd.DataFrame({"driver_id": ["LEC", "LEC", "NOR", "NOR"], "lap": [1, 2, 1, 2], "lap_time_s": [91.2, 91.4, 91.5, 91.3]})
            st.dataframe(example, use_container_width=True, hide_index=True)
        else:
            RESULTS_DIR.mkdir(exist_ok=True)
            path = RESULTS_DIR / "uploaded_laps.csv"
            path.write_bytes(upload.getvalue())
            frame = load_lap_csv(path)
            normalized = normalize_lap_times(frame)
            pace = estimate_driver_pace(frame)
            st.dataframe(pace, use_container_width=True, hide_index=True)
            st.plotly_chart(chart_layout(px.line(normalized, x="lap", y="normalized_lap_time_s", color="driver_id", title="Normalized lap-time trace")), use_container_width=True)
    with tab_report:
        if last_result is None:
            st.info("Run a race scenario from Home or Race Center first.")
        else:
            frame = lap_frame(last_result)
            cls = classification_frame(last_result)
            metrics = last_result.metrics
            report = f"""# F1Sim Pro Engineering Report

## Headline result

- Total race time: {metrics.total_race_time_s:.3f} s
- Pit stop count: {metrics.pit_stop_count}
- Compound sequence: {' / '.join(metrics.compound_sequence)}
- Stint lengths: {metrics.stint_lengths}
- Degradation rate: {metrics.degradation_rate_s_per_lap:.4f} s/lap
- Traffic loss: {metrics.traffic_loss_s:.3f} s
- Pit loss: {metrics.pit_loss_s:.3f} s

## Limitations

Synthetic/example scenarios are transparent modelling assumptions. This report does not contain official team data.
"""
            st.download_button("Download lap history", frame.to_csv(index=False), "lap_history.csv", "text/csv")
            st.download_button("Download classification", cls.to_csv(index=False), "classification.csv", "text/csv")
            st.download_button("Download report", report, "engineering_report.md", "text/markdown")
            st.markdown(report)


def render_platform() -> None:
    """Render the complete ultimate platform."""

    configure_page()
    configs = available_configs()
    if not configs:
        st.error("No experiment YAML files found under configs/experiments.")
        return

    with st.sidebar:
        st.markdown("### F1Sim Pro")
        st.caption("Race intelligence command center")
        config_path = st.selectbox("Scenario", configs, index=0)
        seed = st.number_input("Seed", 1, 999999, 42)
        st.markdown("---")
        section = st.radio(
            "Workspace",
            [
                "Command Center",
                "Race Prediction",
                "Race Simulation",
                "Strategy Room",
                "Engineering Labs",
                "Monte Carlo",
                "Telemetry and Reports",
            ],
        )
        st.markdown("---")
        st.caption("Open research-grade simulation. Synthetic examples are labelled. No official team data is fabricated.")

    topbar()
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if section == "Command Center":
        st.session_state.last_result = render_home(config_path, int(seed))
    elif section == "Race Prediction":
        render_prediction_center(config_path, int(seed))
    elif section == "Race Simulation":
        st.session_state.last_result = render_race_center(config_path, int(seed))
    elif section == "Strategy Room":
        render_strategy_room()
    elif section == "Engineering Labs":
        render_engineering_labs()
    elif section == "Monte Carlo":
        render_monte_carlo(config_path, int(seed))
    else:
        render_telemetry_and_reports(st.session_state.last_result)


if __name__ == "__main__":
    render_platform()
