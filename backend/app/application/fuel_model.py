"""Deterministic fuel model for lap-by-lap race simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FuelModelParameters:
    """Fuel model parameters.

    Attributes:
        burn_kg_per_lap: Nominal fuel consumption per racing lap.
        safety_car_saving_factor: Fraction of burn saved under SC/VSC-like running.
        lap_time_penalty_s_per_kg: Approximate lap-time cost per kilogram of fuel.
    """

    burn_kg_per_lap: float = 1.65
    safety_car_saving_factor: float = 0.42
    lap_time_penalty_s_per_kg: float = 0.032

    def validate(self) -> None:
        if self.burn_kg_per_lap <= 0:
            raise ValueError("burn_kg_per_lap must be positive")
        if not 0.0 <= self.safety_car_saving_factor <= 1.0:
            raise ValueError("safety_car_saving_factor must be in [0, 1]")
        if self.lap_time_penalty_s_per_kg < 0:
            raise ValueError("lap_time_penalty_s_per_kg must be >= 0")


@dataclass(frozen=True)
class FuelDelta:
    """Fuel state transition for one lap."""

    fuel_before_kg: float
    fuel_after_kg: float
    fuel_burn_kg: float
    lap_time_penalty_s: float


class FuelModel:
    """Estimate one-lap fuel burn and fuel-mass lap-time penalty."""

    def __init__(self, parameters: FuelModelParameters | None = None) -> None:
        self.parameters = parameters or FuelModelParameters()
        self.parameters.validate()

    def step(self, fuel_kg: float, safety_car_active: bool = False) -> FuelDelta:
        """Advance fuel state by one lap.

        Args:
            fuel_kg: Fuel mass before the lap.
            safety_car_active: Whether the lap is run under reduced fuel burn.
        """

        if fuel_kg < 0:
            raise ValueError("fuel_kg must be >= 0")

        burn = self.parameters.burn_kg_per_lap
        if safety_car_active:
            burn *= 1.0 - self.parameters.safety_car_saving_factor

        actual_burn = min(fuel_kg, burn)
        after = max(0.0, fuel_kg - actual_burn)
        penalty = fuel_kg * self.parameters.lap_time_penalty_s_per_kg

        return FuelDelta(
            fuel_before_kg=round(fuel_kg, 4),
            fuel_after_kg=round(after, 4),
            fuel_burn_kg=round(actual_burn, 4),
            lap_time_penalty_s=round(penalty, 4),
        )
