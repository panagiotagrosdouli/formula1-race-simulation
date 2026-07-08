"""Safety car and virtual safety car stochastic model."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True, slots=True)
class NeutralisationState:
    """Neutralisation state for a lap."""

    safety_car: bool = False
    vsc: bool = False
    lap_time_multiplier: float = 1.0
    pit_loss_multiplier: float = 1.0


class SafetyCarModel:
    """Models SC/VSC occurrence and their impact on lap time and pit loss."""

    def __init__(
        self,
        safety_car_probability_per_lap: float,
        vsc_probability_per_lap: float,
        pit_loss_multiplier: float,
        seed: int,
    ) -> None:
        self.sc_probability = safety_car_probability_per_lap
        self.vsc_probability = vsc_probability_per_lap
        self.pit_loss_multiplier = pit_loss_multiplier
        self._rng = random.Random(seed)

    def step(self) -> NeutralisationState:
        """Sample neutralisation state for one lap."""

        roll = self._rng.random()
        if roll < self.sc_probability:
            return NeutralisationState(True, False, 1.42, self.pit_loss_multiplier)
        if roll < self.sc_probability + self.vsc_probability:
            return NeutralisationState(False, True, 1.22, 0.78)
        return NeutralisationState()
