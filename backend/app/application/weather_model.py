"""Deterministic weather and track-evolution model.

The model evolves weather state one lap at a time. It uses explicit trends rather
than uncontrolled randomness so simulation experiments remain reproducible and
reviewable.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from backend.app.domain.models import WeatherState


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass(frozen=True)
class WeatherTrend:
    """Per-lap weather trend assumptions.

    Positive rain_intensity_delta_per_lap represents worsening rain. Negative
    values represent improving conditions. Drying rate only applies when rain is
    very low.
    """

    rain_intensity_delta_per_lap: float = 0.0
    air_temperature_delta_per_lap: float = 0.0
    track_temperature_delta_per_lap: float = 0.0
    wind_speed_delta_per_lap: float = 0.0
    humidity_delta_per_lap: float = 0.0
    drying_rate_per_lap: float = 0.035
    rubbering_rate_per_lap: float = 0.006

    def validate(self) -> None:
        if self.drying_rate_per_lap < 0:
            raise ValueError("drying_rate_per_lap must be >= 0")
        if self.rubbering_rate_per_lap < 0:
            raise ValueError("rubbering_rate_per_lap must be >= 0")


class WeatherEvolutionModel:
    """Advance weather and track state by one lap."""

    def step(self, weather: WeatherState, trend: WeatherTrend) -> WeatherState:
        """Return the next weather state from current state and explicit trend."""

        trend.validate()
        rain = _clamp(weather.rain_intensity + trend.rain_intensity_delta_per_lap, 0.0, 1.0)
        air_temp = weather.air_temperature_c + trend.air_temperature_delta_per_lap
        track_temp = weather.track_temperature_c + trend.track_temperature_delta_per_lap
        humidity = _clamp(weather.humidity + trend.humidity_delta_per_lap, 0.0, 1.0)
        wind_speed = max(0.0, weather.wind_speed_kph + trend.wind_speed_delta_per_lap)

        if rain <= 0.03:
            drying_line = _clamp(weather.drying_line + trend.drying_rate_per_lap, 0.0, 1.0)
        else:
            drying_line = _clamp(weather.drying_line - rain * 0.045, 0.0, 1.0)

        rain_grip_penalty = rain * 0.42
        drying_grip_gain = drying_line * 0.12
        rubbering_gain = trend.rubbering_rate_per_lap if rain < 0.08 else 0.0
        track_grip = _clamp(weather.track_grip - rain_grip_penalty * 0.15 + drying_grip_gain * 0.08 + rubbering_gain, 0.25, 1.0)

        forecast_uncertainty = _clamp(weather.forecast_uncertainty + abs(trend.rain_intensity_delta_per_lap) * 0.2 - 0.01, 0.0, 1.0)

        return replace(
            weather,
            air_temperature_c=round(air_temp, 4),
            track_temperature_c=round(track_temp, 4),
            humidity=round(humidity, 4),
            wind_speed_kph=round(wind_speed, 4),
            rain_intensity=round(rain, 4),
            track_grip=round(track_grip, 4),
            drying_line=round(drying_line, 4),
            forecast_uncertainty=round(forecast_uncertainty, 4),
        )
