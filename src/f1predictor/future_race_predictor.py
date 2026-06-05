import numpy as np
import pandas as pd

from .data_loader import build_demo_dataset, build_2026_grid_frame
from .forecast_features import add_rolling_forecast_features, build_future_race_frame
from .model import train_model, predict_next_race
from .priors_2026 import DRIVER_2026_PRIORS, TEAM_2026_PRIORS
from .race_risk import apply_race_risk_features
from .simulation import monte_carlo_race
from .weather import get_race_weather


RAIN_SPECIALISTS = {"VER", "HAM", "ALO"}
ROOKIES_2026 = {"ANT", "HAD", "COL", "LAW", "LIN", "BEA", "BOR"}


def train_historical_model(history_df: pd.DataFrame):
    history_df = history_df[history_df["FinishPosition"].notna()].copy()
    history_df = add_rolling_forecast_features(history_df)

    model, metrics, predictions = train_model(history_df)
    return model, metrics, predictions


def _apply_history_to_2026_grid(
    future_df: pd.DataFrame,
    history_df: pd.DataFrame,
) -> pd.DataFrame:
    hist = add_rolling_forecast_features(history_df)

    latest = (
        hist.sort_values(["Round", "Driver"])
        .groupby("Driver")
        .tail(1)
        .set_index("Driver")
    )

    out = future_df.copy()

    columns_to_transfer = [
        "DriverElo",
        "TeamElo",
        "DNFRate",
        "AvgFinishLast5",
        "AvgQualiLast5",
        "PointsLast5",
        "RecentForm",
        "TeamStrength",
        "DriverRating",
    ]

    for col in columns_to_transfer:
        if col in latest.columns:
            out[col] = out["Driver"].map(latest[col])

    neutral_defaults = {
        "DriverElo": 1500.0,
        "TeamElo": 1500.0,
        "DNFRate": 0.0,
        "AvgFinishLast5": 10.5,
        "AvgQualiLast5": 10.5,
        "PointsLast5": 0.0,
        "RecentForm": 10.5,
        "TeamStrength": 0.5,
        "DriverRating": 0.5,
    }

    for col, value in neutral_defaults.items():
        if col not in out.columns:
            out[col] = value
        out[col] = out[col].fillna(value)

    for driver, values in DRIVER_2026_PRIORS.items():
        mask = out["Driver"] == driver

        for col, value in values.items():
            if col not in out.columns:
                out[col] = np.nan

            out.loc[mask, col] = value

    for team, values in TEAM_2026_PRIORS.items():
        mask = out["Team"] == team

        for col, value in values.items():
            if col not in out.columns:
                out[col] = np.nan

            out.loc[mask, col] = value

    out["GridPosition"] = out["AvgQualiLast5"].round().clip(1, len(out))
    out["QualiGapToPole_s"] = (out["GridPosition"].astype(float) - 1.0) * 0.075

    base_quali = pd.to_numeric(history_df["QualiTime_s"], errors="coerce").median()
    base_long_run = pd.to_numeric(history_df["LongRunPace_s"], errors="coerce").median()

    out["QualiTime_s"] = base_quali + out["QualiGapToPole_s"]
    out["LongRunPace_s"] = base_long_run + out["QualiGapToPole_s"] * 0.20

    return out


def _apply_weather_features(
    future_df: pd.DataFrame,
    race_name: str,
    race_date: str | None = None,
) -> tuple[pd.DataFrame, object]:
    weather = get_race_weather(
        race_name=race_name,
        race_date=race_date,
        use_live_api=True,
    )

    out = future_df.copy()

    out["AirTemperature"] = weather.air_temperature
    out["RainProbability"] = weather.rain_probability
    out["WindSpeed"] = weather.wind_speed
    out["Humidity"] = weather.humidity
    out["WeatherCondition"] = weather.condition

    rain = float(weather.rain_probability)

    out["PredictedWeatherAdjustment"] = 0.0

    if rain >= 0.35:
        out.loc[out["Driver"].isin(RAIN_SPECIALISTS), "PredictedWeatherAdjustment"] = -0.35
        out.loc[out["Driver"].isin(ROOKIES_2026), "PredictedWeatherAdjustment"] = 0.45

    return out, weather


def forecast_future_race(
    history_df=None,
    race_name="British Grand Prix 2026",
    year=2026,
    round_no=1,
    race_date=None,
    n_simulations=10000,
    noise_std=2.0,
    use_2026_grid=True,
):
    if history_df is None:
        history_df = build_demo_dataset()

    model, metrics, historical_predictions = train_historical_model(history_df)

    if use_2026_grid and int(year) == 2026:
        future_df = build_2026_grid_frame(
            race_name=race_name,
            year=year,
            round_no=round_no,
        )

        future_df = _apply_history_to_2026_grid(
            future_df=future_df,
            history_df=history_df,
        )

    else:
        future_df = build_future_race_frame(
            history_df=history_df,
            race_name=race_name,
            year=year,
            round_no=round_no,
        )

    future_df, weather = _apply_weather_features(
        future_df=future_df,
        race_name=race_name,
        race_date=race_date,
    )

    forecast = predict_next_race(model, future_df)

    forecast = apply_race_risk_features(
        forecast_df=forecast,
        race_name=race_name,
        rain_probability=weather.rain_probability,
    )

    if "PredictedWeatherAdjustment" in forecast.columns:
        forecast["PredictedFinishPosition"] = (
            forecast["PredictedFinishPosition"]
            + forecast["PredictedWeatherAdjustment"]
        )

        forecast = forecast.sort_values("PredictedFinishPosition").reset_index(drop=True)
        forecast["PredictedRank"] = np.arange(1, len(forecast) + 1)

    weather_noise = noise_std * (1.0 + float(weather.rain_probability))

    simulation = monte_carlo_race(
        forecast,
        n_simulations=n_simulations,
        noise_std=weather_noise,
    )

    return {
        "model": model,
        "metrics": metrics,
        "historical_predictions": historical_predictions,
        "forecast": forecast,
        "simulation": simulation,
        "weather": weather,
    }
