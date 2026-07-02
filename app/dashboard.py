import sys
from pathlib import Path

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


FERRARI_RED = "#dc2626"
FERRARI_DARK_RED = "#991b1b"
CARBON = "#05070d"
PANEL = "#111827"
PANEL_SOFT = "#1f2937"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
BORDER = "rgba(255,255,255,0.12)"
PLOT_PALETTE = [
    FERRARI_RED,
    "#ef4444",
    "#f97316",
    "#f59e0b",
    "#eab308",
    "#22c55e",
    "#06b6d4",
    "#3b82f6",
    "#8b5cf6",
    "#ec4899",
]

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = PLOT_PALETTE


st.set_page_config(
    page_title="F1 Race Engineering Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)


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


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --f1-red: {FERRARI_RED};
            --f1-dark-red: {FERRARI_DARK_RED};
            --f1-bg: {CARBON};
            --f1-panel: {PANEL};
            --f1-panel-soft: {PANEL_SOFT};
            --f1-text: {TEXT};
            --f1-muted: {MUTED};
            --f1-border: {BORDER};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at top left, rgba(220, 38, 38, 0.18), transparent 28rem),
                linear-gradient(135deg, #05070d 0%, #0b0f19 48%, #05070d 100%);
            color: var(--f1-text);
        }}

        .main {{
            background: transparent;
        }}

        [data-testid="stHeader"] {{
            background: rgba(5, 7, 13, 0.72);
            backdrop-filter: blur(14px);
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #090d16 0%, #05070d 100%);
            border-right: 1px solid var(--f1-border);
        }}

        .block-container {{
            padding-top: 1.35rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}

        h1, h2, h3 {{
            letter-spacing: -0.035em;
            color: var(--f1-text);
        }}

        p, li, label, span {{
            color: inherit;
        }}

        .hero {{
            border: 1px solid rgba(220, 38, 38, 0.36);
            border-radius: 26px;
            padding: 30px 32px;
            background:
                linear-gradient(135deg, rgba(220, 38, 38, 0.24), rgba(17, 24, 39, 0.92)),
                radial-gradient(circle at 90% 20%, rgba(239, 68, 68, 0.22), transparent 18rem);
            box-shadow: 0 26px 80px rgba(0,0,0,0.38);
            margin-bottom: 1.1rem;
        }}

        .hero h1 {{
            margin: 0;
            font-size: clamp(2rem, 4vw, 2.75rem);
            color: #ffffff;
        }}

        .hero p {{
            margin-top: 0.75rem;
            max-width: 1020px;
            color: #d1d5db;
            font-size: 1.04rem;
            line-height: 1.65;
        }}

        .badge-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }}

        .badge {{
            border-radius: 999px;
            padding: 0.35rem 0.78rem;
            background: rgba(220, 38, 38, 0.16);
            border: 1px solid rgba(248, 113, 113, 0.32);
            color: #fef2f2;
            font-size: 0.82rem;
            font-weight: 600;
        }}

        .panel {{
            border: 1px solid var(--f1-border);
            border-left: 4px solid var(--f1-red);
            border-radius: 18px;
            padding: 18px 20px;
            background: rgba(17, 24, 39, 0.78);
            margin: 0.6rem 0 1rem 0;
            box-shadow: 0 16px 45px rgba(0,0,0,0.18);
        }}

        .panel h3 {{
            margin-top: 0;
            color: #ffffff;
        }}

        .panel p, .panel li {{
            color: #d1d5db;
            line-height: 1.55;
        }}

        div[data-testid="stMetric"] {{
            border: 1px solid var(--f1-border);
            border-radius: 16px;
            padding: 14px 16px;
            background:
                linear-gradient(180deg, rgba(31, 41, 55, 0.86), rgba(17, 24, 39, 0.82));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }}

        div[data-testid="stMetricLabel"] {{
            color: var(--f1-muted);
        }}

        div[data-testid="stMetricValue"] {{
            color: #ffffff;
        }}

        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(248, 113, 113, 0.40);
            background: linear-gradient(135deg, var(--f1-red), var(--f1-dark-red));
            color: #ffffff;
            font-weight: 700;
            box-shadow: 0 12px 30px rgba(220, 38, 38, 0.22);
        }}

        .stButton > button:hover, .stDownloadButton > button:hover {{
            border-color: rgba(252, 165, 165, 0.85);
            filter: brightness(1.08);
        }}

        [data-baseweb="tab-list"] {{
            gap: 0.45rem;
            border-bottom: 1px solid var(--f1-border);
        }}

        [data-baseweb="tab"] {{
            background: rgba(17, 24, 39, 0.86);
            border: 1px solid var(--f1-border);
            border-radius: 999px 999px 0 0;
            padding: 0.55rem 1rem;
        }}

        [aria-selected="true"][data-baseweb="tab"] {{
            background: linear-gradient(135deg, var(--f1-red), var(--f1-dark-red));
            border-color: rgba(248, 113, 113, 0.55);
            color: #ffffff;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid var(--f1-border);
            border-radius: 16px;
            overflow: hidden;
            background: rgba(17, 24, 39, 0.72);
        }}

        div[data-baseweb="select"] > div,
        input,
        textarea {{
            background-color: rgba(17, 24, 39, 0.96) !important;
            color: var(--f1-text) !important;
            border-color: rgba(255,255,255,0.16) !important;
        }}

        .small-note {{
            color: var(--f1-muted);
            font-size: 0.9rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>🏎️ F1 Race Engineering Intelligence Platform</h1>
            <p>
                Machine-learning forecasting, Monte Carlo race uncertainty, weather-aware risk,
                telemetry comparison, tyre degradation and championship simulation in one decision
                dashboard. Designed for students, data scientists, race strategists and motorsport
                engineers who need both the prediction and the reasoning behind it.
            </p>
            <div class="badge-row">
                <span class="badge">Race forecast</span>
                <span class="badge">Monte Carlo uncertainty</span>
                <span class="badge">FastF1 telemetry</span>
                <span class="badge">Weather risk</span>
                <span class="badge">Tyre degradation</span>
                <span class="badge">Championship simulation</span>
                <span class="badge">Engineering decision support</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def engineering_panel(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="panel">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_f1_plot_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(5, 7, 13, 0)",
        plot_bgcolor="rgba(17, 24, 39, 0.92)",
        font={"color": TEXT, "family": "Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 20, "r": 20, "t": 55, "b": 35},
        colorway=PLOT_PALETTE,
        legend={
            "bgcolor": "rgba(17, 24, 39, 0.55)",
            "bordercolor": "rgba(255,255,255,0.12)",
            "borderwidth": 1,
        },
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.18)",
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.18)",
    )
    return fig


def plot_chart(fig: go.Figure) -> None:
    st.plotly_chart(apply_f1_plot_theme(fig), use_container_width=True)


def probability_to_percent(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = (pd.to_numeric(out[col], errors="coerce") * 100).round(2)
    return out


def format_prediction_table(df: pd.DataFrame) -> pd.DataFrame:
    priority_cols = [
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
        "DNFRisk",
        "SafetyCarProbability",
        "RiskAdjustment",
    ]
    cols = [col for col in priority_cols if col in df.columns]
    return df[cols].copy() if cols else df.copy()


def show_probability_cards(sim: pd.DataFrame) -> None:
    required = {"Driver", "WinProbability", "PodiumProbability", "Top10Probability", "ExpectedFinish"}
    if sim.empty or not required.issubset(sim.columns):
        st.warning("No complete simulation output is available yet.")
        return

    safe = sim.copy()
    for col in ["WinProbability", "PodiumProbability", "Top10Probability", "ExpectedFinish"]:
        safe[col] = pd.to_numeric(safe[col], errors="coerce")

    safe = safe.dropna(subset=["WinProbability", "PodiumProbability", "Top10Probability", "ExpectedFinish"])
    if safe.empty:
        st.warning("Simulation output exists but does not contain numeric probability values.")
        return

    leader = safe.sort_values("WinProbability", ascending=False).iloc[0]
    podium = safe.sort_values("PodiumProbability", ascending=False).iloc[0]
    consistency = safe.sort_values("ExpectedFinish", ascending=True).iloc[0]
    top10 = safe.sort_values("Top10Probability", ascending=False).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Most likely winner", leader["Driver"], f"{leader['WinProbability'] * 100:.1f}% win")
    c2.metric("Best podium chance", podium["Driver"], f"{podium['PodiumProbability'] * 100:.1f}% podium")
    c3.metric("Best expected finish", consistency["Driver"], f"P{consistency['ExpectedFinish']:.2f}")
    c4.metric("Most secure Top 10", top10["Driver"], f"{top10['Top10Probability'] * 100:.1f}% top 10")


def show_model_summary(metrics: dict | None) -> None:
    if not metrics:
        st.info("Run a training workflow to generate validation metrics.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MAE", metrics.get("MAE", "N/A"))
    c2.metric("RMSE", metrics.get("RMSE", "N/A"))
    c3.metric("Rank correlation", metrics.get("SpearmanRankCorrelation", "N/A"))
    c4.metric("Test rows", metrics.get("TestRows", "N/A"))

    engineering_panel(
        "How to read these diagnostics",
        "MAE/RMSE measure finishing-position error, while Spearman correlation measures whether "
        "the model preserves the correct ranking order. For race engineering decisions, ranking "
        "quality is often more informative than absolute position error.",
    )


def show_downloads(name: str, df: pd.DataFrame) -> None:
    st.download_button(
        label=f"Download {name.replace('_', ' ')} CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{name.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        key=f"download_{name}",
    )


inject_css()
hero()

with st.sidebar:
    st.header("Race control")

    st.caption("Global simulation parameters")
    n_simulations = st.slider(
        "Monte Carlo simulations",
        1000,
        50000,
        10000,
        step=1000,
        help="Higher values make probability estimates more stable but slower.",
    )

    noise_std = st.slider(
        "Race uncertainty",
        0.5,
        5.0,
        2.0,
        step=0.1,
        help="Controls random variation around the model's central prediction.",
    )

    st.divider()
    st.caption("Interpretation")
    st.info(
        "Use this as a decision-support platform: forecasts are probabilistic, not deterministic. "
        "For scientific work, prefer real FastF1 training and backtesting over demo data."
    )


(
    tab_overview,
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
    tab6,
    tab7,
) = st.tabs(
    [
        "Command centre",
        "Historical model",
        "Future race forecast",
        "Season simulator",
        "Real FastF1 training",
        "Telemetry insights",
        "Tyre degradation",
        "Model diagnostics",
    ]
)


with tab_overview:
    st.subheader("Command centre")

    engineering_panel(
        "From prediction to engineering decision",
        "The platform separates three layers: model forecast, probabilistic race simulation and "
        "engineering interpretation. This makes the dashboard useful both for general viewers and "
        "for technically demanding motorsport analysis.",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Forecast engine", "ML + priors")
    c2.metric("Uncertainty layer", "Monte Carlo")
    c3.metric("Telemetry layer", "FastF1")
    c4.metric("Decision layer", "Risk + strategy")

    st.markdown("### Workflow map")
    st.markdown(
        """
        1. **Train or load data** — synthetic demo for instant use, FastF1 data for scientific analysis.
        2. **Predict race order** — estimate expected finishing position and rank.
        3. **Simulate uncertainty** — convert central forecasts into win, podium and top-10 probabilities.
        4. **Inspect engineering context** — weather, DNF risk, safety-car exposure, tyre degradation and telemetry.
        5. **Export results** — download tables for reports, notebooks or presentations.
        """
    )

    if PREDICTIONS_PATH.exists() and SIMULATION_PATH.exists():
        predictions = pd.read_csv(PREDICTIONS_PATH)
        sim = pd.read_csv(SIMULATION_PATH)
        st.markdown("### Latest available run")
        show_probability_cards(sim)
        st.dataframe(format_prediction_table(predictions.tail(20)), use_container_width=True)
    else:
        st.info("Run the historical pipeline or a future race forecast to populate the command centre.")


with tab1:
    st.subheader("Historical model")

    engineering_panel(
        "Purpose",
        "Train a baseline race-outcome model and convert the prediction into an uncertainty-aware "
        "probability table. This is the fastest way to demonstrate the full pipeline.",
    )

    run_demo = st.button("Build demo data + train + simulate", type="primary")

    if run_demo or not PREDICTIONS_PATH.exists() or not SIMULATION_PATH.exists():
        df = build_demo_dataset()
        TRAINING_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(TRAINING_DATA_PATH, index=False)

        model, metrics, predictions = train_model(df)
        sim = monte_carlo_race(predictions, n_simulations=n_simulations, noise_std=noise_std)

        st.success("Pipeline completed.")
        show_model_summary(metrics)
    else:
        predictions = pd.read_csv(PREDICTIONS_PATH)
        sim = pd.read_csv(SIMULATION_PATH)

    latest_gp = predictions["GrandPrix"].iloc[-1]
    latest_predictions = (
        predictions[predictions["GrandPrix"] == latest_gp]
        .sort_values("PredictedRank")
        .reset_index(drop=True)
    )

    st.markdown(f"### Predicted order — {latest_gp}")
    show_probability_cards(sim)

    st.dataframe(format_prediction_table(latest_predictions), use_container_width=True)
    show_downloads("historical_predictions", latest_predictions)
    plot_chart(plot_predicted_order(latest_predictions))

    st.markdown("### Monte Carlo probabilities")
    sim_display = probability_to_percent(sim, ["WinProbability", "PodiumProbability", "Top10Probability"])
    st.dataframe(sim_display, use_container_width=True)
    show_downloads("monte_carlo_probabilities", sim)

    col1, col2, col3 = st.columns(3)
    with col1:
        plot_chart(plot_probabilities(sim, "WinProbability"))
    with col2:
        plot_chart(plot_probabilities(sim, "PodiumProbability"))
    with col3:
        plot_chart(plot_probabilities(sim, "Top10Probability"))


with tab2:
    st.subheader("Future race forecast")

    engineering_panel(
        "Race-engineering forecast",
        "Forecast a future Formula 1 race using driver/team priors, rolling form, weather uncertainty, "
        "safety-car risk, DNF risk and Monte Carlo simulation. The output is designed like a pre-race "
        "briefing: likely winner, podium threats, risk exposure and downloadable decision tables.",
    )

    c1, c2, c3 = st.columns([2, 1, 1])
    race_name = c1.selectbox("Future race", RACE_OPTIONS_2026, index=11)
    round_no = c2.number_input("Round number", min_value=1, max_value=30, value=12)
    race_date = c3.text_input("Race date for live weather API", "", placeholder="YYYY-MM-DD")

    run_forecast = st.button("Forecast selected race", type="primary")

    if run_forecast:
        df = build_demo_dataset()
        result = forecast_future_race(
            history_df=df,
            race_name=race_name,
            year=2026,
            round_no=int(round_no),
            race_date=race_date if race_date else None,
            n_simulations=n_simulations,
            noise_std=noise_std,
            use_2026_grid=True,
        )

        forecast = result["forecast"]
        sim_future = result["simulation"]
        weather = result["weather"]
        metrics = result.get("metrics")

        st.success("Future race forecast completed.")
        show_model_summary(metrics)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Weather", weather.condition)
        c2.metric("Rain probability", f"{weather.rain_probability * 100:.1f}%")
        c3.metric("Air temperature", f"{weather.air_temperature:.1f} °C")
        c4.metric("Humidity", f"{weather.humidity:.1f}%")

        show_probability_cards(sim_future)

        report = generate_race_report(forecast=forecast, simulation=sim_future, weather=weather)
        st.markdown("### Race analyst briefing")
        st.info(report)

        risk_cols = [
            "Driver",
            "Team",
            "SafetyCarProbability",
            "DNFRisk",
            "RiskAdjustment",
            "PredictedWeatherAdjustment",
        ]
        visible_risk_cols = [col for col in risk_cols if col in forecast.columns]

        st.markdown("### Risk model")
        if visible_risk_cols:
            st.dataframe(forecast[visible_risk_cols], use_container_width=True)
        else:
            st.info("Risk model columns are not available for this forecast.")

        st.markdown("### Predicted future finishing order")
        st.dataframe(format_prediction_table(forecast), use_container_width=True)
        show_downloads("future_race_forecast", forecast)
        plot_chart(plot_predicted_order(forecast))

        st.markdown("### Future race probabilities")
        sim_future_display = probability_to_percent(
            sim_future,
            ["WinProbability", "PodiumProbability", "Top10Probability"],
        )
        st.dataframe(sim_future_display, use_container_width=True)
        show_downloads("future_race_probabilities", sim_future)

        col1, col2, col3 = st.columns(3)
        with col1:
            plot_chart(plot_probabilities(sim_future, "WinProbability"))
        with col2:
            plot_chart(plot_probabilities(sim_future, "PodiumProbability"))
        with col3:
            plot_chart(plot_probabilities(sim_future, "Top10Probability"))


with tab3:
    st.subheader("2026 Championship Simulator")

    engineering_panel(
        "Season-level simulation",
        "Race probabilities are aggregated across the calendar to estimate championship outcomes. "
        "This is useful for strategic scenario analysis, not just single-race prediction.",
    )

    season_runs = st.slider(
        "Season simulation Monte Carlo runs per race",
        500,
        10000,
        3000,
        step=500,
    )

    run_season = st.button("Run 2026 Championship Simulation", type="primary")

    if run_season:
        df = build_demo_dataset()
        season = simulate_2026_season(
            history_df=df,
            n_simulations=season_runs,
            noise_std=noise_std,
        )

        driver_probs = calculate_title_probabilities(season["driver_standings"])
        constructor_probs = calculate_constructor_title_probabilities(season["constructor_standings"])

        st.success("Season simulation completed.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Driver title probabilities")
            st.dataframe(driver_probs, use_container_width=True)
            fig = px.bar(
                driver_probs.head(10),
                x="Driver",
                y="ChampionshipProbability",
                hover_data=["Team", "ExpectedPoints", "ProjectedPosition"],
                title="Driver championship probability (%)",
                color_discrete_sequence=[FERRARI_RED],
            )
            plot_chart(fig)
            show_downloads("driver_title_probabilities", driver_probs)

        with c2:
            st.markdown("### Constructor title probabilities")
            st.dataframe(constructor_probs, use_container_width=True)
            fig = px.bar(
                constructor_probs,
                x="Team",
                y="ChampionshipProbability",
                hover_data=["ConstructorExpectedPoints", "ProjectedPosition"],
                title="Constructor championship probability (%)",
                color_discrete_sequence=[FERRARI_RED],
            )
            plot_chart(fig)
            show_downloads("constructor_title_probabilities", constructor_probs)

        st.markdown("### Race-by-race driver table")
        st.dataframe(season["driver_race_table"], use_container_width=True)
        show_downloads("race_by_race_driver_table", season["driver_race_table"])


with tab4:
    st.subheader("Real FastF1 training")

    engineering_panel(
        "Scientific upgrade path",
        "Use real qualifying and race sessions through FastF1. This is the recommended mode for "
        "academic reports, model validation and motorsport analytics beyond a demo dataset.",
    )

    year = st.number_input("Training year", min_value=2018, max_value=2026, value=2024)
    gp_text = st.text_input(
        "Optional GP names separated by comma",
        "Bahrain, Saudi Arabia, Australia, Japan, China, Miami",
    )

    run_real = st.button("Build real FastF1 dataset + train", type="primary")

    if run_real:
        gp_names = [x.strip() for x in gp_text.split(",") if x.strip()]
        if not gp_names:
            gp_names = None

        try:
            with st.spinner("Downloading FastF1 data and training model..."):
                real_df = build_fastf1_dataset(int(year), grand_prix_names=gp_names)
                real_df.to_csv(TRAINING_DATA_PATH, index=False)

                model, metrics, predictions = train_model(real_df)
                sim = monte_carlo_race(predictions, n_simulations=n_simulations, noise_std=noise_std)

            st.success("Real-data training completed.")
            show_model_summary(metrics)

            st.markdown("### Real FastF1 training dataset")
            st.dataframe(real_df, use_container_width=True)
            show_downloads("real_fastf1_training_dataset", real_df)

            st.markdown("### Predictions from real-data model")
            st.dataframe(format_prediction_table(predictions), use_container_width=True)
            show_downloads("real_data_predictions", predictions)

            st.markdown("### Monte Carlo probabilities")
            st.dataframe(
                probability_to_percent(sim, ["WinProbability", "PodiumProbability", "Top10Probability"]),
                use_container_width=True,
            )
            show_downloads("real_data_probabilities", sim)

        except Exception as exc:
            st.error(str(exc))
            st.info(
                "Try official FastF1 event names, or leave the GP field empty "
                "to let FastF1 attempt available completed events."
            )


with tab5:
    st.subheader("Telemetry insights")

    engineering_panel(
        "Driver telemetry comparison",
        "Compare fastest-lap telemetry between two drivers using speed, throttle, brake, gear, DRS "
        "and RPM channels. This helps connect model output with on-track driving evidence.",
    )

    c1, c2, c3, c4 = st.columns(4)
    tel_year = c1.number_input("Telemetry year", min_value=2018, max_value=2026, value=2024)
    tel_gp = c2.text_input("Grand Prix", "Monza")
    tel_session = c3.selectbox("Session", ["Q", "R", "S", "SQ"], index=0)
    tel_channel = c4.selectbox("Extra channel", ["Throttle", "Brake", "nGear", "DRS", "RPM"], index=0)

    d1, d2 = st.columns(2)
    driver_a = d1.text_input("Driver A", "VER").upper()
    driver_b = d2.text_input("Driver B", "LEC").upper()

    if st.button("Compare driver telemetry", type="primary"):
        try:
            with st.spinner("Loading FastF1 telemetry..."):
                telemetry_a = load_fastest_lap_telemetry(int(tel_year), tel_gp, tel_session, driver_a)
                telemetry_b = load_fastest_lap_telemetry(int(tel_year), tel_gp, tel_session, driver_b)

            m1, m2, m3 = st.columns(3)
            m1.metric(
                f"{driver_a} fastest lap",
                f"{telemetry_a.lap_time_seconds:.3f}s" if telemetry_a.lap_time_seconds else "N/A",
            )
            m2.metric(
                f"{driver_b} fastest lap",
                f"{telemetry_b.lap_time_seconds:.3f}s" if telemetry_b.lap_time_seconds else "N/A",
            )
            if telemetry_a.lap_time_seconds and telemetry_b.lap_time_seconds:
                delta = telemetry_b.lap_time_seconds - telemetry_a.lap_time_seconds
                m3.metric("Lap delta", f"{delta:+.3f}s")

            plot_chart(compare_driver_speed_trace(telemetry_a, telemetry_b))
            plot_chart(compare_driver_controls(telemetry_a, telemetry_b, tel_channel))

        except Exception as exc:
            st.error(str(exc))
            st.info("Use official FastF1 event names and three-letter driver abbreviations, e.g. VER, LEC, NOR, PIA.")


with tab6:
    st.subheader("Tyre degradation")

    engineering_panel(
        "Stint and tyre-life analysis",
        "Estimate tyre degradation from real race laps using tyre age and lap-time evolution. "
        "This section supports strategy discussions such as one-stop vs two-stop trade-offs.",
    )

    c1, c2, c3, c4 = st.columns(4)
    deg_year = c1.number_input("Degradation year", min_value=2018, max_value=2026, value=2024)
    deg_gp = c2.text_input("Degradation Grand Prix", "Monza")
    deg_session = c3.selectbox("Degradation session", ["R", "S"], index=0)
    deg_driver = c4.text_input("Degradation driver", "VER").upper()

    if st.button("Analyze tyre degradation", type="primary"):
        try:
            with st.spinner("Loading lap data and estimating degradation..."):
                result = load_tire_degradation(int(deg_year), deg_gp, deg_session, deg_driver)
                cliff = detect_tire_cliff(result)

            c1, c2 = st.columns(2)
            c1.metric("Estimated degradation rate", f"{result.degradation_rate:.3f} s/lap")
            c2.metric("Potential cliff laps", len(cliff))
            plot_chart(plot_degradation(result))

            st.markdown("### Compound summary")
            st.dataframe(result.compound_summary, use_container_width=True)

            st.markdown("### Potential tyre-cliff laps")
            st.dataframe(cliff, use_container_width=True)

        except Exception as exc:
            st.error(str(exc))
            st.info("Use a completed race/sprint session with available FastF1 lap data.")


with tab7:
    st.subheader("Model diagnostics")

    engineering_panel(
        "Transparency and validation",
        "A serious forecasting dashboard must show feature coverage, data volume and output "
        "distributions. Use this section to detect suspicious inputs before trusting predictions.",
    )

    if PREDICTIONS_PATH.exists():
        predictions = pd.read_csv(PREDICTIONS_PATH)
        st.markdown("### Prediction dataset overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", len(predictions))
        c2.metric("Grand Prix events", predictions["GrandPrix"].nunique() if "GrandPrix" in predictions else "N/A")
        c3.metric("Drivers", predictions["Driver"].nunique() if "Driver" in predictions else "N/A")
        missing_rate = float(predictions.isna().mean(numeric_only=False).mean() * 100)
        c4.metric("Missing values", f"{missing_rate:.1f}%")

        numeric_cols = predictions.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            selected_metric = st.selectbox("Numeric feature distribution", numeric_cols)
            plot_chart(
                px.histogram(
                    predictions,
                    x=selected_metric,
                    title=f"Distribution of {selected_metric}",
                    color_discrete_sequence=[FERRARI_RED],
                )
            )

        if {"PredictedFinishPosition", "FinishPosition"}.issubset(predictions.columns):
            diagnostics = predictions.dropna(subset=["PredictedFinishPosition", "FinishPosition"]).copy()
            diagnostics["AbsoluteError"] = (
                pd.to_numeric(diagnostics["PredictedFinishPosition"], errors="coerce")
                - pd.to_numeric(diagnostics["FinishPosition"], errors="coerce")
            ).abs()
            st.markdown("### Error inspection")
            st.dataframe(
                diagnostics.sort_values("AbsoluteError", ascending=False).head(25),
                use_container_width=True,
            )

        st.markdown("### Full prediction table")
        st.dataframe(predictions, use_container_width=True)
        show_downloads("model_diagnostics_predictions", predictions)
    else:
        st.info("Run the historical pipeline first to generate prediction diagnostics.")
