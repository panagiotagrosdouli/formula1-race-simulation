"""Tyre compound and degradation models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TyreCompound:
    """Parameterisation of a tyre compound."""

    name: str
    base_delta_s: float
    wear_s_per_lap: float
    cliff_lap: int
    cliff_s_per_lap: float
    temp_sensitivity_s_per_c: float
    wet_grip_factor: float = 1.0


COMPOUNDS: dict[str, TyreCompound] = {
    "soft": TyreCompound("soft", -0.45, 0.070, 18, 0.18, 0.012),
    "medium": TyreCompound("medium", 0.0, 0.045, 28, 0.12, 0.008),
    "hard": TyreCompound("hard", 0.35, 0.030, 40, 0.08, 0.006),
    "intermediate": TyreCompound("intermediate", 2.0, 0.050, 30, 0.10, 0.004, wet_grip_factor=0.55),
    "wet": TyreCompound("wet", 4.0, 0.045, 34, 0.08, 0.003, wet_grip_factor=0.35),
}


class TyreModel:
    """Computes tyre-induced lap-time loss.

    The default parameters are illustrative open-model assumptions. They are not official F1 team data.
    """

    def __init__(self, reference_track_temp_c: float = 35.0) -> None:
        self.reference_track_temp_c = reference_track_temp_c

    def lap_delta_s(self, compound: str, age_laps: int, track_temp_c: float, wetness: float = 0.0) -> float:
        """Return lap-time delta in seconds for the tyre state."""

        tyre = COMPOUNDS[compound]
        wear = tyre.wear_s_per_lap * max(age_laps, 0)
        cliff = max(age_laps - tyre.cliff_lap, 0) * tyre.cliff_s_per_lap
        temp = (track_temp_c - self.reference_track_temp_c) * tyre.temp_sensitivity_s_per_c
        wet_penalty = wetness * tyre.wet_grip_factor if compound in {"soft", "medium", "hard"} else wetness * -1.2
        return tyre.base_delta_s + wear + cliff + temp + wet_penalty

    def degradation_rate(self, compound: str, stint_length: int) -> float:
        """Estimate average degradation rate for a stint."""

        if stint_length <= 1:
            return 0.0
        start = self.lap_delta_s(compound, 0, self.reference_track_temp_c)
        end = self.lap_delta_s(compound, stint_length, self.reference_track_temp_c)
        return (end - start) / stint_length
