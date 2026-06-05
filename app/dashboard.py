import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.config import TRAINING_DATA_PATH, PREDICTIONS_PATH, SIMULATION_PATH
from src.f1predictor.data_loader import build_demo_dataset, build_fastf1_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.model import train_model
from src.f1predictor.race_analyst import generate_race_report
from src.f1predictor.season_simulator import simulate_2026_season
from src.f1predictor.simulation import monte_carlo_race
from src.f1predictor.visualization import plot_predicted_order, plot_probabilities


st.set_page_config(page_title="F1 AI Forecasting Platform", layout="wide")

st.title("🏎️ F1 AI Forecasting Platform")
st.write(
    "Race prediction, future forecasting, weather-aware risk modeling, "
    "Monte Carlo simulation, AI race analysis, and 2026 championship projection."
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Historical prediction",
        "Future race forecast",
        "Season simulator",
        "Real FastF1 training",
    ]
)

with st.sidebar:
    st.header("Controls")

    n_simulations = st.slider(
        "Monte Carlo simulations",
        1000,
        50000,
        10000,
        step=1000,
    )

    noise_std = st.slider(
        "Race uncertainty",
        0.5,
        5.0,
        2.0,
        step=0.1,
    )


with tab1:
    st.subheader("Historical prediction pipeline")

    run_demo = st.button("Build demo data + train + simulate")

    if run_demo or not PREDICTIONS_PATH.exists() or not SIMULATION_PATH.exists():
        df = build_demo_dataset()
        TRAINING_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(TRAINING_DATA_PATH, index=False)

        model, metrics, predictions = train_model(df)

        sim = monte_carlo_race(
            predictions,
            n_simulations=n_simulations,
            noise_std=noise_std,
        )

        st.success("Pipeline completed.")
        st.json(metrics)

    else:
        predictions = pd.read_csv(PREDICTIONS_PATH)
        sim = pd.read_csv(SIMULATION_PATH)

    latest_gp = predictions["GrandPrix"].iloc[-1]

    latest_predictions = (
        predictions[predictions["GrandPrix"] == latest_gp]
        .sort_values("PredictedRank")
    )

    st.subheader(f"Predicted order — {latest_gp}")

    st.dataframe(
        latest_predictions,
        use_container_width=True,
    )

    st.plotly_chart(
        plot_predicted_order(latest_predictions),
        use_container_width=True,
    )

    st.subheader("Monte Carlo probabilities")

    st.dataframe(
        sim,
        use_container_width=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(
            plot_probabilities(sim, "WinProbability"),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            plot_probabilities(sim, "PodiumProbability"),
            use_container_width=True,
        )

    with col3:
        st.plotly_chart(
            plot_probabilities(sim, "Top10Probability"),
            use_container_width=True,
        )


with tab2:
    st.subheader("Future race forecast")

    st.write(
        "Forecast a future Formula 1 race using 2026 driver/team priors, "
        "Driver Elo, Team Elo, rolling form, weather data, safety-car risk, "
        "DNF risk and Monte Carlo uncertainty."
    )

    race_name = st.selectbox(
        "Future race",
        [
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
        ],
        index=11,
    )

    round_no = st.number_input(
        "Round number",
        min_value=1,
        max_value=30,
        value=12,
    )

    race_date = st.text_input(
        "Race date for live weather API (optional, YYYY-MM-DD)",
        "",
    )

    run_forecast = st.button("Forecast selected race")

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

        st.success("Future race forecast completed.")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Weather", weather.condition)
        c2.metric("Rain probability", f"{weather.rain_probability * 100:.1f}%")
        c3.metric("Air temperature", f"{weather.air_temperature:.1f} °C")
        c4.metric("Humidity", f"{weather.humidity:.1f}%")

        report = generate_race_report(
            forecast=forecast,
            simulation=sim_future,
            weather=weather,
        )

        st.subheader("AI Race Analyst")
        st.info(report)

        st.subheader("Risk model")

        risk_cols = [
            "Driver",
            "Team",
            "SafetyCarProbability",
            "DNFRisk",
            "RiskAdjustment",
            "PredictedWeatherAdjustment",
        ]

        visible_risk_cols = [c for c in risk_cols if c in forecast.columns]

        st.dataframe(
            forecast[visible_risk_cols],
            use_container_width=True,
        )

        st.subheader("Predicted future finishing order")

        st.dataframe(
            forecast,
            use_container_width=True,
        )

        st.plotly_chart(
            plot_predicted_order(forecast),
            use_container_width=True,
            key="future_predicted_order_chart",
        )

        st.subheader("Future race probabilities")

        st.dataframe(
            sim_future,
            use_container_width=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(
                plot_probabilities(sim_future, "WinProbability"),
                use_container_width=True,
                key="future_win_probability_chart",
            )

        with col2:
            st.plotly_chart(
                plot_probabilities(sim_future, "PodiumProbability"),
                use_container_width=True,
                key="future_podium_probability_chart",
            )

        with col3:
            st.plotly_chart(
                plot_probabilities(sim_future, "Top10Probability"),
                use_container_width=True,
                key="future_top10_probability_chart",
            )


with tab3:
    st.subheader("2026 Championship Simulator")

    st.write(
        "Simulate the full 2026 Formula 1 season using the future-race "
        "forecasting engine and Monte Carlo probabilities."
    )

    season_runs = st.slider(
        "Season simulation Monte Carlo runs per race",
        500,
        10000,
        3000,
        step=500,
    )

    run_season = st.button("Run 2026 Championship Simulation")

    if run_season:
        df = build_demo_dataset()

        season = simulate_2026_season(
            history_df=df,
            n_simulations=season_runs,
            noise_std=noise_std,
        )

        st.success("Season simulation completed.")

        st.subheader("Projected Drivers Championship")

        st.dataframe(
            season["driver_standings"],
            use_container_width=True,
        )

        st.subheader("Projected Constructors Championship")

        st.dataframe(
            season["constructor_standings"],
            use_container_width=True,
        )

        st.subheader("Race-by-race driver table")

        st.dataframe(
            season["driver_race_table"],
            use_container_width=True,
        )


with tab4:
    st.subheader("Real FastF1 training")

    st.write(
        "Download real FastF1 qualifying/race results and train the model on "
        "real historical data. The first run may take time because FastF1 "
        "downloads and caches sessions."
    )

    year = st.number_input(
        "Training year",
        min_value=2018,
        max_value=2026,
        value=2024,
    )

    gp_text = st.text_input(
        "Optional GP names separated by comma",
        "Bahrain, Saudi Arabia, Australia, Japan, China, Miami",
    )

    run_real = st.button("Build real FastF1 dataset + train")

    if run_real:
        gp_names = [x.strip() for x in gp_text.split(",") if x.strip()]

        with st.spinner("Downloading FastF1 data and training model..."):
            real_df = build_fastf1_dataset(
                int(year),
                grand_prix_names=gp_names,
            )

            real_df.to_csv(TRAINING_DATA_PATH, index=False)

            model, metrics, predictions = train_model(real_df)

            sim = monte_carlo_race(
                predictions,
                n_simulations=n_simulations,
                noise_std=noise_std,
            )

        st.success("Real-data training completed.")
        st.json(metrics)

        st.subheader("Real FastF1 training dataset")

        st.dataframe(
            real_df,
            use_container_width=True,
        )

        st.subheader("Predictions from real-data model")

        st.dataframe(
            predictions,
            use_container_width=True,
        )

        st.subheader("Monte Carlo probabilities")

        st.dataframe(
            sim,
            use_container_width=True,
        )
