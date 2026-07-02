from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.championship_probability import (
    calculate_constructor_title_probabilities,
    calculate_title_probabilities,
)
from src.f1predictor.config import PREDICTIONS_PATH, SIMULATION_PATH, TRAINING_DATA_PATH
from src.f1predictor.data_loader import build_demo_dataset, build_fastf1_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.model import train_model
from src.f1predictor.race_analyst import generate_race_report
from src.f1predictor.season_simulator import simulate_2026_season
from src.f1predictor.simulation import monte_carlo_race
from src.f1predictor.telemetry.degradation_dashboard import (
    detect_tire_cliff,
    load_tire_degradation,
    plot_degradation,
)
from src.f1predictor.telemetry.streamlit_insights import (
    compare_driver_controls,
    compare_driver_speed_trace,
    load_fastest_lap_telemetry,
)
from src.f1predictor.visualization import plot_predicted_order, plot_probabilities

APP_TITLE = "F1 Race Engineering Intelligence"
FERRARI_RED = "#dc2626"
FERRARI_DARK_RED = "#991b1b"
TEXT = "#f9fafb"
BORDER = "rgba(255,255,255,0.12)"
PLOT_PALETTE = [FERRARI_RED, "#ef4444", "#f97316", "#f59e0b", "#22c55e", "#06b6d4", "#3b82f6"]

RACE_OPTIONS_2026 = [
    "Australian Grand Prix 2026",
    "Chinese Grand Prix 2026",
    "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026",
    "Saudi Arabian Grand Prix 2026",
    "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026",
    "Canadian Grand Prix 2026",
    "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026",
    "British Grand Prix 2026",
    "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026",
    "Italian Grand Prix 2026",
    "Singapore Grand Prix 2026",
    "United States Grand Prix 2026",
    "Mexico City Grand Prix 2026",
    "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026",
    "Qatar Grand Prix 2026",
    "Abu Dhabi Grand Prix 2026",
]

PAGES = [
    "Command Centre",
    "Race Forecast",
    "Model Lab",
    "Season Simulator",
    "FastF1 Training",
    "Telemetry",
    "Tyre Strategy",
    "Diagnostics",
]

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = PLOT_PALETTE

st.set_page_config(page_title=APP_TITLE, page_icon="🏎️", layout="wide", initial_sidebar_state="expanded")


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(135deg, #05070d 0%, #0b0f19 55%, #05070d 100%);
            color: {TEXT};
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #090d16 0%, #05070d 100%);
            border-right: 1px solid {BORDER};
        }}
        [data-testid="stHeader"] {{ background: rgba(5, 7, 13, 0.72); }}
        .block-container {{ max-width: 1500px; padding-top: 1.25rem; padding-bottom: 2rem; }}
        h1, h2, h3 {{ letter-spacing: -0.035em; }}
        .hero {{
            border: 1px solid rgba(220, 38, 38, 0.35);
            border-radius: 26px;
            padding: 28px 32px;
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.24), rgba(17, 24, 39, 0.94));
            box-shadow: 0 26px 80px rgba(0,0,0,0.35);
            margin-bottom: 1rem;
        }}
        .hero h1 {{ margin: 0; font-size: 2.65rem; color: #ffffff; }}
        .hero p {{ color: #d1d5db; line-height: 1.65; max-width: 1080px; }}
        .pill {{
            display: inline-block;
            margin: 0.15rem 0.25rem 0.15rem 0;
            padding: 0.32rem 0.72rem;
            border-radius: 999px;
            background: rgba(220, 38, 38, 0.16);
            border: 1px solid rgba(248, 113, 113, 0.32);
            color: #fef2f2;
            font-size: 0.82rem;
            font-weight: 700;
        }}
        .panel {{
            border: 1px solid {BORDER};
            border-left: 4px solid {FERRARI_RED};
            border-radius: 18px;
            padding: 17px 20px;
            background: rgba(17, 24, 39, 0.78);
            margin: 0.7rem 0 1rem 0;
        }}
        .panel p {{ color: #d1d5db; line-height: 1.55; margin-bottom: 0; }}
        div[data-testid="stMetric"] {{
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 14px 16px;
            background: linear-gradient(180deg, rgba(31, 41, 55, 0.86), rgba(17, 24, 39, 0.82));
        }}
        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(248, 113, 113, 0.45);
            background: linear-gradient(135deg, {FERRARI_RED}, {FERRARI_DARK_RED});
            color: white;
            font-weight: 800;
        }}
        [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 16px; overflow: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>🏎️ F1 Race Engineering Intelligence</h1>
            <p>
                Professional motorsport analytics cockpit for race prediction, Monte Carlo uncertainty,
                weather-aware risk, telemetry comparison, tyre degradation and championship scenarios.
                Designed for clear presentation and engineering-grade interpretation.
            </p>
            <span class="pill">Prediction</span><span class="pill">Uncertainty</span><span class="pill">Telemetry</span>
            <span class="pill">Weather risk</span><span class="pill">Tyre life</span><span class="pill">Championship</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, body: str) -> None:
    st.markdown(f"<div class='panel'><h3>{title}</h3><p>{body}</p></div>", unsafe_allow_html=True)


def apply_plot_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(5, 7, 13, 0)",
        plot_bgcolor="rgba(17, 24, 39, 0.92)",
        font={"color": TEXT, "family": "Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 20, "r": 20, "t": 55, "b": 35},
        colorway=PLOT_PALETTE,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor=BORDER, linecolor="rgba(255,255,255,0.18)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor=BORDER, linecolor="rgba(255,255,255,0.18)")
    return fig


def chart(fig: go.Figure) -> None:
    st.plotly_chart(apply_plot_theme(fig), use_container_width=True)


@st.cache_data(show_spinner=False)
def demo_data() -> pd.DataFrame:
    return build_demo_dataset()


def to_percent(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["WinProbability", "PodiumProbability", "Top10Probability"]:
        if col in out.columns:
            out[col] = (pd.to_numeric(out[col], errors="coerce") * 100).round(2)
    return out


def select_existing(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    selected = [col for col in columns if col in df.columns]
    return df[selected].copy() if selected else df.copy()


def prediction_view(df: pd.DataFrame) -> pd.DataFrame:
    return select_existing(
        df,
        [
            "PredictedRank",
            "Driver",
            "Team",
            "PredictedFinishPosition",
            "GridPosition",
            "QualiGapToPole_s",
            "LongRunPace_s",
            "TeamStrength",
            "DriverRating",
            "RecentForm",
            "RainProbability",
            "SafetyCarProbability",
            "DNFRisk",
            "RiskAdjustment",
        ],
    )


def download_csv(name: str, df: pd.DataFrame) -> None:
    st.download_button(
        f"Download {name.replace('_', ' ')} CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"{name}.csv",
        mime="text/csv",
        key=f"download_{name}",
    )


def probability_cards(sim: pd.DataFrame) -> None:
    required = {"Driver", "WinProbability", "PodiumProbability", "Top10Probability", "ExpectedFinish"}
    if sim.empty or not required.issubset(sim.columns):
        st.warning("No complete probability table is available yet.")
        return
    safe = sim.copy()
    for col in ["WinProbability", "PodiumProbability", "Top10Probability", "ExpectedFinish"]:
        safe[col] = pd.to_numeric(safe[col], errors="coerce")
    safe = safe.dropna(subset=["WinProbability", "PodiumProbability", "Top10Probability", "ExpectedFinish"])
    if safe.empty:
        st.warning("Probability table exists but has no numeric probability values.")
        return

    winner = safe.sort_values("WinProbability", ascending=False).iloc[0]
    podium = safe.sort_values("PodiumProbability", ascending=False).iloc[0]
    expected = safe.sort_values("ExpectedFinish", ascending=True).iloc[0]
    top10 = safe.sort_values("Top10Probability", ascending=False).iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Most likely winner", winner["Driver"], f"{winner['WinProbability'] * 100:.1f}% win")
    col2.metric("Best podium chance", podium["Driver"], f"{podium['PodiumProbability'] * 100:.1f}% podium")
    col3.metric("Best expected finish", expected["Driver"], f"P{expected['ExpectedFinish']:.2f}")
    col4.metric("Most secure Top 10", top10["Driver"], f"{top10['Top10Probability'] * 100:.1f}%")


def model_metrics(metrics: dict | None) -> None:
    if not metrics:
        st.info("Validation metrics appear after a training run.")
        return
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MAE", metrics.get("MAE", "N/A"))
    col2.metric("RMSE", metrics.get("RMSE", "N/A"))
    col3.metric("Rank correlation", metrics.get("SpearmanRankCorrelation", "N/A"))
    col4.metric("Test rows", metrics.get("TestRows", "N/A"))


def run_demo_pipeline(n_simulations: int, noise_std: float) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    df = demo_data()
    TRAINING_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(TRAINING_DATA_PATH, index=False)
    _model, metrics, predictions = train_model(df)
    sim = monte_carlo_race(predictions, n_simulations=n_simulations, noise_std=noise_std)
    return metrics, predictions, sim


def show_prediction_output(predictions: pd.DataFrame, name: str, title: str) -> None:
    st.markdown(f"### {title}")
    st.dataframe(prediction_view(predictions), use_container_width=True)
    download_csv(name, predictions)
    chart(plot_predicted_order(predictions))


def show_probability_output(sim: pd.DataFrame, name: str) -> None:
    st.markdown("### Probability distribution")
    probability_cards(sim)
    st.dataframe(to_percent(sim), use_container_width=True)
    download_csv(name, sim)
    col1, col2, col3 = st.columns(3)
    with col1:
        chart(plot_probabilities(sim, "WinProbability"))
    with col2:
        chart(plot_probabilities(sim, "PodiumProbability"))
    with col3:
        chart(plot_probabilities(sim, "Top10Probability"))


def command_centre() -> None:
    st.subheader("Command Centre")
    panel("Executive overview", "Top-level race-control view for data readiness, latest output and the recommended analysis workflow.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Forecast engine", "ML + priors")
    col2.metric("Uncertainty layer", "Monte Carlo")
    col3.metric("Data layer", "FastF1-ready")
    col4.metric("Output layer", "Dashboard + CSV")

    if PREDICTIONS_PATH.exists() and SIMULATION_PATH.exists():
        predictions = pd.read_csv(PREDICTIONS_PATH)
        sim = pd.read_csv(SIMULATION_PATH)
        st.markdown("### Latest generated output")
        probability_cards(sim)
        st.dataframe(prediction_view(predictions.tail(24)), use_container_width=True)
    else:
        st.info("No saved output found. Run Model Lab or Race Forecast first.")

    st.markdown("### Operating workflow")
    st.markdown(
        """
        1. **Model Lab** trains the baseline and checks metrics.  
        2. **Race Forecast** creates a pre-race engineering brief.  
        3. **Telemetry** and **Tyre Strategy** explain the on-track evidence.  
        4. **Diagnostics** checks data quality and error behaviour.
        """
    )


def model_lab(n_simulations: int, noise_std: float) -> None:
    st.subheader("Model Lab")
    panel("Historical model", "Train the demo pipeline and convert predicted finishing order into uncertainty-aware probabilities.")
    if st.button("Run historical model pipeline", type="primary") or not PREDICTIONS_PATH.exists() or not SIMULATION_PATH.exists():
        metrics, predictions, sim = run_demo_pipeline(n_simulations, noise_std)
        st.success("Historical pipeline completed.")
        model_metrics(metrics)
    else:
        predictions = pd.read_csv(PREDICTIONS_PATH)
        sim = pd.read_csv(SIMULATION_PATH)
        model_metrics(None)

    latest_gp = predictions["GrandPrix"].iloc[-1] if "GrandPrix" in predictions else "Race"
    race_predictions = predictions[predictions["GrandPrix"] == latest_gp] if "GrandPrix" in predictions else predictions
    if "PredictedRank" in race_predictions:
        race_predictions = race_predictions.sort_values("PredictedRank")
    show_prediction_output(race_predictions.reset_index(drop=True), "historical_predictions", f"Predicted order — {latest_gp}")
    show_probability_output(sim, "historical_probabilities")


def race_forecast(n_simulations: int, noise_std: float) -> None:
    st.subheader("Race Forecast")
    panel("Pre-race engineering brief", "Forecast a future race with priors, weather, safety-car risk, DNF risk and Monte Carlo uncertainty.")
    col1, col2, col3 = st.columns([2, 1, 1])
    race_name = col1.selectbox("Future race", RACE_OPTIONS_2026, index=11)
    round_no = col2.number_input("Round", min_value=1, max_value=30, value=12)
    race_date = col3.text_input("Weather date", "", placeholder="YYYY-MM-DD")
    if not st.button("Generate forecast", type="primary"):
        st.info("Choose a race and run the forecast.")
        return

    with st.spinner("Generating forecast..."):
        result = forecast_future_race(
            history_df=demo_data(),
            race_name=race_name,
            year=2026,
            round_no=int(round_no),
            race_date=race_date if race_date else None,
            n_simulations=n_simulations,
            noise_std=noise_std,
            use_2026_grid=True,
        )
    forecast = result["forecast"]
    sim = result["simulation"]
    weather = result["weather"]
    st.success("Forecast completed.")
    model_metrics(result.get("metrics"))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Weather", weather.condition)
    col2.metric("Rain", f"{weather.rain_probability * 100:.1f}%")
    col3.metric("Air temp", f"{weather.air_temperature:.1f} °C")
    col4.metric("Humidity", f"{weather.humidity:.1f}%")
    st.markdown("### Race analyst briefing")
    st.info(generate_race_report(forecast=forecast, simulation=sim, weather=weather))
    risk_cols = ["Driver", "Team", "SafetyCarProbability", "DNFRisk", "RiskAdjustment", "PredictedWeatherAdjustment"]
    visible_risk_cols = [col for col in risk_cols if col in forecast.columns]
    if visible_risk_cols:
        st.markdown("### Risk exposure")
        st.dataframe(forecast[visible_risk_cols], use_container_width=True)
    show_prediction_output(forecast, "future_race_forecast", "Predicted future finishing order")
    show_probability_output(sim, "future_race_probabilities")


def season_simulator(n_simulations: int, noise_std: float) -> None:
    st.subheader("Season Simulator")
    panel("Championship scenarios", "Aggregate race-level probability across the 2026 calendar.")
    season_runs = st.slider("Season simulation runs per race", 500, 10000, min(3000, n_simulations), step=500)
    if not st.button("Run championship simulation", type="primary"):
        st.info("Run the simulator to generate championship tables.")
        return
    with st.spinner("Simulating season..."):
        season = simulate_2026_season(history_df=demo_data(), n_simulations=season_runs, noise_std=noise_std)
        driver_probs = calculate_title_probabilities(season["driver_standings"])
        constructor_probs = calculate_constructor_title_probabilities(season["constructor_standings"])
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Driver title probability")
        st.dataframe(driver_probs, use_container_width=True)
        chart(px.bar(driver_probs.head(10), x="Driver", y="ChampionshipProbability", hover_data=["Team", "ExpectedPoints", "ProjectedPosition"], title="Driver championship probability (%)", color_discrete_sequence=[FERRARI_RED]))
        download_csv("driver_title_probabilities", driver_probs)
    with col2:
        st.markdown("### Constructor title probability")
        st.dataframe(constructor_probs, use_container_width=True)
        chart(px.bar(constructor_probs, x="Team", y="ChampionshipProbability", hover_data=["ConstructorExpectedPoints", "ProjectedPosition"], title="Constructor championship probability (%)", color_discrete_sequence=[FERRARI_RED]))
        download_csv("constructor_title_probabilities", constructor_probs)
    st.markdown("### Race-by-race table")
    st.dataframe(season["driver_race_table"], use_container_width=True)
    download_csv("race_by_race_driver_table", season["driver_race_table"])


def fastf1_training(n_simulations: int, noise_std: float) -> None:
    st.subheader("FastF1 Training")
    panel("Real-data mode", "Build a training table from real FastF1 qualifying and race sessions.")
    col1, col2 = st.columns([1, 3])
    year = col1.number_input("Training year", min_value=2018, max_value=2026, value=2024)
    gp_text = col2.text_input("GP names, comma separated", "Bahrain, Saudi Arabia, Australia, Japan, China, Miami")
    if not st.button("Build FastF1 dataset + train", type="primary"):
        st.info("First run may take longer while FastF1 downloads and caches sessions.")
        return
    gp_names = [item.strip() for item in gp_text.split(",") if item.strip()] or None
    try:
        with st.spinner("Downloading FastF1 sessions and training model..."):
            real_df = build_fastf1_dataset(int(year), grand_prix_names=gp_names)
            real_df.to_csv(TRAINING_DATA_PATH, index=False)
            _model, metrics, predictions = train_model(real_df)
            sim = monte_carlo_race(predictions, n_simulations=n_simulations, noise_std=noise_std)
    except Exception as exc:
        st.error(str(exc))
        st.info("Use official FastF1 event names, or leave the GP field empty to attempt all completed events.")
        return
    st.success("Real-data training completed.")
    model_metrics(metrics)
    st.markdown("### Training dataset")
    st.dataframe(real_df, use_container_width=True)
    download_csv("real_fastf1_training_dataset", real_df)
    show_prediction_output(predictions, "real_data_predictions", "Predictions from real-data model")
    show_probability_output(sim, "real_data_probabilities")


def telemetry() -> None:
    st.subheader("Telemetry")
    panel("Driver evidence layer", "Compare fastest-lap telemetry to explain where drivers gain or lose time.")
    col1, col2, col3, col4 = st.columns(4)
    year = col1.number_input("Telemetry year", min_value=2018, max_value=2026, value=2024)
    gp = col2.text_input("Grand Prix", "Monza")
    session = col3.selectbox("Session", ["Q", "R", "S", "SQ"], index=0)
    channel = col4.selectbox("Extra channel", ["Throttle", "Brake", "nGear", "DRS", "RPM"], index=0)
    col_a, col_b = st.columns(2)
    driver_a = col_a.text_input("Driver A", "VER").upper()
    driver_b = col_b.text_input("Driver B", "LEC").upper()
    if not st.button("Compare telemetry", type="primary"):
        st.info("Use three-letter driver abbreviations, for example VER, LEC, NOR or PIA.")
        return
    try:
        with st.spinner("Loading FastF1 telemetry..."):
            telemetry_a = load_fastest_lap_telemetry(int(year), gp, session, driver_a)
            telemetry_b = load_fastest_lap_telemetry(int(year), gp, session, driver_b)
    except Exception as exc:
        st.error(str(exc))
        st.info("Use official FastF1 event names and completed sessions.")
        return
    col1, col2, col3 = st.columns(3)
    col1.metric(f"{driver_a} fastest lap", f"{telemetry_a.lap_time_seconds:.3f}s" if telemetry_a.lap_time_seconds else "N/A")
    col2.metric(f"{driver_b} fastest lap", f"{telemetry_b.lap_time_seconds:.3f}s" if telemetry_b.lap_time_seconds else "N/A")
    if telemetry_a.lap_time_seconds and telemetry_b.lap_time_seconds:
        col3.metric("Lap delta", f"{telemetry_b.lap_time_seconds - telemetry_a.lap_time_seconds:+.3f}s")
    chart(compare_driver_speed_trace(telemetry_a, telemetry_b))
    chart(compare_driver_controls(telemetry_a, telemetry_b, channel))


def tyre_strategy() -> None:
    st.subheader("Tyre Strategy")
    panel("Stint degradation analysis", "Estimate degradation rate and possible tyre-cliff laps from real FastF1 lap data.")
    col1, col2, col3, col4 = st.columns(4)
    year = col1.number_input("Degradation year", min_value=2018, max_value=2026, value=2024)
    gp = col2.text_input("Degradation Grand Prix", "Monza")
    session = col3.selectbox("Degradation session", ["R", "S"], index=0)
    driver = col4.text_input("Driver", "VER").upper()
    if not st.button("Analyze tyre degradation", type="primary"):
        st.info("Choose a completed race or sprint session with available lap data.")
        return
    try:
        with st.spinner("Loading laps and estimating degradation..."):
            result = load_tire_degradation(int(year), gp, session, driver)
            cliff = detect_tire_cliff(result)
    except Exception as exc:
        st.error(str(exc))
        st.info("Use a completed race/sprint session and a valid driver abbreviation.")
        return
    col1, col2 = st.columns(2)
    col1.metric("Estimated degradation", f"{result.degradation_rate:.3f} s/lap")
    col2.metric("Potential cliff laps", len(cliff))
    chart(plot_degradation(result))
    st.markdown("### Compound summary")
    st.dataframe(result.compound_summary, use_container_width=True)
    st.markdown("### Potential tyre-cliff laps")
    st.dataframe(cliff, use_container_width=True)


def diagnostics() -> None:
    st.subheader("Diagnostics")
    panel("Trust and validation layer", "Inspect data volume, missing values, feature distributions and largest prediction errors.")
    if not PREDICTIONS_PATH.exists():
        st.info("Run Model Lab or FastF1 Training first to generate prediction diagnostics.")
        return
    predictions = pd.read_csv(PREDICTIONS_PATH)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", len(predictions))
    col2.metric("Grand Prix events", predictions["GrandPrix"].nunique() if "GrandPrix" in predictions else "N/A")
    col3.metric("Drivers", predictions["Driver"].nunique() if "Driver" in predictions else "N/A")
    col4.metric("Missing values", f"{float(predictions.isna().mean(numeric_only=False).mean() * 100):.1f}%")
    numeric_cols = predictions.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        selected = st.selectbox("Numeric feature distribution", numeric_cols)
        chart(px.histogram(predictions, x=selected, title=f"Distribution of {selected}", color_discrete_sequence=[FERRARI_RED]))
    if {"PredictedFinishPosition", "FinishPosition"}.issubset(predictions.columns):
        error_df = predictions.dropna(subset=["PredictedFinishPosition", "FinishPosition"]).copy()
        error_df["AbsoluteError"] = (
            pd.to_numeric(error_df["PredictedFinishPosition"], errors="coerce")
            - pd.to_numeric(error_df["FinishPosition"], errors="coerce")
        ).abs()
        st.markdown("### Largest absolute errors")
        st.dataframe(error_df.sort_values("AbsoluteError", ascending=False).head(25), use_container_width=True)
    st.markdown("### Full prediction table")
    st.dataframe(predictions, use_container_width=True)
    download_csv("model_diagnostics_predictions", predictions)


def sidebar() -> tuple[str, int, float]:
    with st.sidebar:
        st.header("Race Control")
        page = st.radio("Navigation", PAGES, index=0)
        st.divider()
        st.caption("Simulation parameters")
        n_simulations = st.slider("Monte Carlo simulations", 1000, 50000, 10000, step=1000)
        noise_std = st.slider("Race uncertainty", 0.5, 5.0, 2.0, step=0.1)
        st.divider()
        st.info("Forecasts are probabilistic. For scientific use, validate with FastF1 data and diagnostics.")
    return page, n_simulations, noise_std


def main() -> None:
    inject_css()
    hero()
    page, n_simulations, noise_std = sidebar()
    routes: dict[str, Callable[[], None]] = {
        "Command Centre": command_centre,
        "Race Forecast": lambda: race_forecast(n_simulations, noise_std),
        "Model Lab": lambda: model_lab(n_simulations, noise_std),
        "Season Simulator": lambda: season_simulator(n_simulations, noise_std),
        "FastF1 Training": lambda: fastf1_training(n_simulations, noise_std),
        "Telemetry": telemetry,
        "Tyre Strategy": tyre_strategy,
        "Diagnostics": diagnostics,
    }
    routes[page]()


if __name__ == "__main__":
    main()
