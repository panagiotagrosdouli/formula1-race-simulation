import pandas as pd

from .data_loader import build_demo_dataset
from .forecast_features import (
    add_rolling_forecast_features,
    build_future_race_frame,
)
from .model import train_model, predict_next_race
from .simulation import monte_carlo_race


def train_historical_model(history_df: pd.DataFrame):

    history_df = history_df[
        history_df["FinishPosition"].notna()
    ].copy()

    history_df = add_rolling_forecast_features(
        history_df
    )

    model, metrics, predictions = train_model(
        history_df
    )

    return model, metrics, predictions


def forecast_future_race(
    history_df=None,
    race_name="British Grand Prix 2026",
    year=2026,
    round_no=None,
    n_simulations=10000,
    noise_std=2.0,
):

    if history_df is None:
        history_df = build_demo_dataset()

    model, metrics, historical_predictions = (
        train_historical_model(history_df)
    )

    future_df = build_future_race_frame(
        history_df=history_df,
        race_name=race_name,
        year=year,
        round_no=round_no,
    )

    forecast = predict_next_race(
        model,
        future_df,
    )

    simulation = monte_carlo_race(
        forecast,
        n_simulations=n_simulations,
        noise_std=noise_std,
    )

    return {
        "model": model,
        "metrics": metrics,
        "historical_predictions": historical_predictions,
        "forecast": forecast,
        "simulation": simulation,
    }
