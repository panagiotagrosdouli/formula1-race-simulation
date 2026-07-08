"""Fuel mass effect model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FuelModel:
    """Linear fuel mass model for race simulation.

    Parameters are deliberately configurable because real fuel correction values vary by car, circuit and setup.
    """

    start_kg: float = 100.0
    burn_kg_per_lap: float = 1.7
    lap_time_s_per_kg: float = 0.035
    safety_margin_kg: float = 2.0

    def fuel_at_lap_start(self, lap: int) -> float:
        """Return estimated fuel mass at the beginning of a lap."""

        return max(self.safety_margin_kg, self.start_kg - self.burn_kg_per_lap * max(lap - 1, 0))

    def lap_delta_s(self, lap: int) -> float:
        """Return fuel-mass lap-time delta relative to an empty reference."""

        return self.fuel_at_lap_start(lap) * self.lap_time_s_per_kg
