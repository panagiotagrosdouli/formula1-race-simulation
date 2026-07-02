"""Deterministic full-race runner built on the one-lap simulator."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.application.event_engine import EventProbabilityModel
from backend.app.application.lap_simulator import LapSimulator
from backend.app.application.weather_model import WeatherTrend
from backend.app.domain.models import CarPerformanceProfile, Driver, RaceState


@dataclass(frozen=True)
class RaceRunResult:
    """Complete deterministic race trajectory."""

    initial_state: RaceState
    final_state: RaceState
    lap_states: tuple[RaceState, ...]
    assumptions: tuple[str, ...]


class DeterministicRaceRunner:
    """Run a deterministic race from an initial state to the chequered flag."""

    def __init__(self, lap_simulator: LapSimulator | None = None) -> None:
        self.lap_simulator = lap_simulator or LapSimulator()

    def run_to_finish(
        self,
        initial_state: RaceState,
        drivers: tuple[Driver, ...],
        cars: dict[str, CarPerformanceProfile],
        base_lap_time_s: float,
        event_probabilities: EventProbabilityModel,
        weather_trend: WeatherTrend | None = None,
        max_laps: int | None = None,
    ) -> RaceRunResult:
        """Run deterministic lap evolution until finish or max_laps.

        Args:
            initial_state: Starting race state.
            drivers: Driver definitions.
            cars: Car profiles keyed by driver id string.
            base_lap_time_s: Baseline lap time used by the pace model.
            event_probabilities: Explicit event probability model.
            weather_trend: Optional per-lap weather trend.
            max_laps: Optional cap for partial simulations and tests.
        """

        if base_lap_time_s <= 0:
            raise ValueError("base_lap_time_s must be positive")
        if max_laps is not None and max_laps < 1:
            raise ValueError("max_laps must be >= 1 when provided")

        states: list[RaceState] = [initial_state]
        current = initial_state
        laps_remaining = current.circuit.lap_count - current.lap
        target_steps = laps_remaining if max_laps is None else min(max_laps, laps_remaining)

        for _ in range(target_steps):
            current = self.lap_simulator.simulate_one_lap(
                state=current,
                drivers=drivers,
                cars=cars,
                base_lap_time_s=base_lap_time_s,
                event_probabilities=event_probabilities,
                weather_trend=weather_trend,
            )
            states.append(current)
            if current.lap >= current.circuit.lap_count:
                break

        return RaceRunResult(
            initial_state=initial_state,
            final_state=current,
            lap_states=tuple(states),
            assumptions=(
                "Deterministic race runner composes one-lap state transitions.",
                "Monte Carlo sampling is not applied in this runner.",
                "All randomness is delegated to seeded sub-models with explicit probability inputs.",
            ),
        )
