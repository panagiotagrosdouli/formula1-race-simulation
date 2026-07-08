"""Monte Carlo race strategy simulation."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, quantiles

from f1sim.data.config import RaceConfig
from f1sim.simulation.engine import RaceSimulation


@dataclass(frozen=True, slots=True)
class MonteCarloSummary:
    """Aggregated Monte Carlo outputs."""

    runs: int
    expected_time_s: float
    confidence_interval_s: tuple[float, float]
    expected_position: float
    strategy_risk_profile: dict[str, float]
    probability_beating_target: float | None = None


class MonteCarloSimulation:
    """Runs repeated seeded race simulations with controlled stochastic variation."""

    def __init__(self, config: RaceConfig, runs: int = 1000, seed: int | None = None) -> None:
        self.config = config.model_copy(update={"seed": seed or config.seed})
        self.runs = runs

    def run(self, target_driver_id: str | None = None) -> MonteCarloSummary:
        """Execute Monte Carlo simulations and return risk metrics."""

        total_times: list[float] = []
        positions: list[float] = []
        target_beaten = 0
        target_comparisons = 0
        for run_index in range(self.runs):
            result = RaceSimulation(self.config, seed_offset=run_index).run()
            leader = result.classification[0]
            total_times.append(leader.total_time_s)
            positions.append(float(leader.position))
            if target_driver_id is not None:
                order = {driver.driver_id: idx for idx, driver in enumerate(result.classification)}
                if leader.driver_id in order and target_driver_id in order:
                    target_comparisons += 1
                    target_beaten += int(order[leader.driver_id] < order[target_driver_id])

        if len(total_times) >= 20:
            q = quantiles(total_times, n=20)
            ci = (q[0], q[-1])
        else:
            ci = (min(total_times), max(total_times))
        profile = {
            "p05_time_s": ci[0],
            "p50_time_s": sorted(total_times)[len(total_times) // 2],
            "p95_time_s": ci[1],
        }
        probability = None
        if target_comparisons:
            probability = target_beaten / target_comparisons
        return MonteCarloSummary(
            runs=self.runs,
            expected_time_s=mean(total_times),
            confidence_interval_s=ci,
            expected_position=mean(positions),
            strategy_risk_profile=profile,
            probability_beating_target=probability,
        )
