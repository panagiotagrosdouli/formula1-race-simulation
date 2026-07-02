"""Deterministic lap pace model.

The pace model decomposes expected lap time into explicit terms so assumptions
are inspectable and calibratable. It is designed for engineering transparency,
not black-box prediction.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.application.fuel_model import FuelDelta
from backend.app.application.tyre_model import TyrePerformanceDelta
from backend.app.domain.models import CarPerformanceProfile, DriverSkillProfile, WeatherState


@dataclass(frozen=True)
class PaceModelParameters:
    """Global pace model coefficients."""

    base_lap_time_s: float
    driver_pace_gain_s: float = 1.2
    car_performance_gain_s: float = 1.4
    wet_skill_gain_s: float = 0.9
    low_grip_penalty_s: float = 2.2
    traffic_penalty_s: float = 0.35

    def validate(self) -> None:
        if self.base_lap_time_s <= 0:
            raise ValueError("base_lap_time_s must be positive")
        for name in ["driver_pace_gain_s", "car_performance_gain_s", "wet_skill_gain_s", "low_grip_penalty_s", "traffic_penalty_s"]:
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be >= 0")


@dataclass(frozen=True)
class PaceBreakdown:
    """Decomposed expected lap time."""

    expected_lap_time_s: float
    base_lap_time_s: float
    driver_delta_s: float
    car_delta_s: float
    fuel_delta_s: float
    tyre_delta_s: float
    weather_delta_s: float
    traffic_delta_s: float


class PaceModel:
    """Compute expected lap time from driver, car, fuel, tyre and weather state."""

    def __init__(self, parameters: PaceModelParameters) -> None:
        parameters.validate()
        self.parameters = parameters

    def estimate_lap_time(
        self,
        driver_skill: DriverSkillProfile,
        car: CarPerformanceProfile,
        fuel: FuelDelta,
        tyre: TyrePerformanceDelta,
        weather: WeatherState,
        traffic_factor: float = 0.0,
    ) -> PaceBreakdown:
        """Estimate one-lap pace from decomposed model inputs."""

        if not 0.0 <= traffic_factor <= 1.0:
            raise ValueError("traffic_factor must be in [0, 1]")
        driver_skill.validate()
        car.validate()

        driver_quality = (driver_skill.race_pace + driver_skill.consistency + driver_skill.pressure_handling) / 3.0
        driver_delta = -(driver_quality - 0.5) * self.parameters.driver_pace_gain_s

        car_quality = (car.power_unit + car.aero_efficiency + car.downforce + car.corner_speed + car.brake_performance) / 5.0
        car_delta = -(car_quality - 0.5) * self.parameters.car_performance_gain_s

        wet_skill_credit = driver_skill.wet_skill * weather.rain_intensity * self.parameters.wet_skill_gain_s
        low_grip_penalty = max(0.0, 1.0 - weather.track_grip) * self.parameters.low_grip_penalty_s
        weather_delta = low_grip_penalty - wet_skill_credit

        traffic_delta = traffic_factor * self.parameters.traffic_penalty_s

        total = (
            self.parameters.base_lap_time_s
            + driver_delta
            + car_delta
            + fuel.lap_time_penalty_s
            + tyre.lap_time_delta_s
            + weather_delta
            + traffic_delta
        )

        return PaceBreakdown(
            expected_lap_time_s=round(total, 4),
            base_lap_time_s=round(self.parameters.base_lap_time_s, 4),
            driver_delta_s=round(driver_delta, 4),
            car_delta_s=round(car_delta, 4),
            fuel_delta_s=round(fuel.lap_time_penalty_s, 4),
            tyre_delta_s=round(tyre.lap_time_delta_s, 4),
            weather_delta_s=round(weather_delta, 4),
            traffic_delta_s=round(traffic_delta, 4),
        )
