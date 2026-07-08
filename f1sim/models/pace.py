"""Driver pace modelling utilities."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True, slots=True)
class DriverPaceModel:
    """Simple transparent driver pace model.

    Args:
        base_pace_s: Baseline clean-air lap time.
        pace_sigma_s: Standard deviation for stochastic pace perturbations.
        seed: Deterministic seed for reproducible draws.
    """

    base_pace_s: float
    pace_sigma_s: float = 0.15
    seed: int = 42

    def lap_pace_s(self, lap: int, driver_offset_s: float = 0.0) -> float:
        """Return a deterministic pseudo-random pace sample for one lap."""

        rng = random.Random(self.seed + lap)
        return self.base_pace_s + driver_offset_s + rng.gauss(0.0, self.pace_sigma_s)


def normalize_pace(lap_time_s: float, reference_s: float) -> float:
    """Return lap-time delta against a reference pace."""

    return lap_time_s - reference_s
