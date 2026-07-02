"""Monte Carlo orchestration for deterministic race simulations.

This module composes the deterministic race runner with seed/probability
perturbations. It keeps sampling policy explicit and reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.application.event_engine import EventProbabilityModel
from backend.app.application.race_runner import DeterministicRaceRunner, RaceRunResult
from backend.app.application.weather_model import WeatherTrend
from backend.app.domain.models import CarPerformanceProfile, Driver, RaceState


@dataclass(frozen=True)
class MonteCarloRun:
    """Single Monte Carlo run output."""

    run_index: int
    seed: int
    result: RaceRunResult


@dataclass(frozen=True)
class MonteCarloSummary:
    """Aggregated Monte Carlo finishing-position summary."""

    runs: int
    winner_counts: dict[str, int]
    average_finish_position: dict[str, float]
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class MonteCarloResult:
    """Full Monte Carlo output."""

    samples: tuple[MonteCarloRun, ...]
    summary: MonteCarloSummary


class MonteCarloRaceSimulator:
    """Run repeated deterministic race simulations with controlled seeds."""

    def __init__(self, runner: DeterministicRaceRunner | None = None) -> None:
        self.runner = runner or DeterministicRaceRunner()

    def run(
        self,
        initial_state: RaceState,
        drivers: tuple[Driver, ...],
        cars: dict[str, CarPerformanceProfile],
        base_lap_time_s: float,
        event_probabilities: EventProbabilityModel,
        weather_trend: WeatherTrend | None,
        runs: int,
    ) -> MonteCarloResult:
        """Run a reproducible Monte Carlo experiment."""

        if runs < 1:
            raise ValueError("runs must be >= 1")

        samples: list[MonteCarloRun] = []
        for index in range(runs):
            seeded_state = RaceState(
                circuit=initial_state.circuit,
                lap=initial_state.lap,
                weather=initial_state.weather,
                driver_states=initial_state.driver_states,
                events=initial_state.events,
                random_seed=initial_state.random_seed + index,
            )
            result = self.runner.run_to_finish(
                initial_state=seeded_state,
                drivers=drivers,
                cars=cars,
                base_lap_time_s=base_lap_time_s,
                event_probabilities=event_probabilities,
                weather_trend=weather_trend,
            )
            samples.append(MonteCarloRun(run_index=index, seed=seeded_state.random_seed, result=result))

        return MonteCarloResult(samples=tuple(samples), summary=self._summarize(samples))

    def _summarize(self, samples: list[MonteCarloRun]) -> MonteCarloSummary:
        winner_counts: dict[str, int] = {}
        position_totals: dict[str, int] = {}
        position_counts: dict[str, int] = {}

        for sample in samples:
            final_order = sorted(sample.result.final_state.driver_states, key=lambda item: item.position)
            if not final_order:
                continue
            winner = str(final_order[0].driver_id)
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
            for driver_state in final_order:
                driver_id = str(driver_state.driver_id)
                position_totals[driver_id] = position_totals.get(driver_id, 0) + driver_state.position
                position_counts[driver_id] = position_counts.get(driver_id, 0) + 1

        average_finish = {
            driver_id: round(position_totals[driver_id] / position_counts[driver_id], 4)
            for driver_id in position_totals
        }

        return MonteCarloSummary(
            runs=len(samples),
            winner_counts=winner_counts,
            average_finish_position=average_finish,
            assumptions=(
                "Monte Carlo samples are produced by deterministic race runs with controlled seed offsets.",
                "Probability inputs are explicit and should be calibrated against historical data.",
            ),
        )
