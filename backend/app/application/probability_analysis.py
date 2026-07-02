"""Probability analysis helpers for Monte Carlo race outputs.

The functions in this module convert raw simulation counts into interpretable
engineering summaries. Confidence intervals use a Wilson score interval so small
sample sizes remain visible instead of being over-presented as precise truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from backend.app.application.monte_carlo import MonteCarloSummary


@dataclass(frozen=True)
class DriverProbabilitySummary:
    """Probability summary for one driver."""

    driver_id: str
    win_probability: float
    win_ci_lower: float
    win_ci_upper: float
    expected_finish_position: float


@dataclass(frozen=True)
class RaceProbabilityReport:
    """Probability report for a Monte Carlo experiment."""

    runs: int
    drivers: tuple[DriverProbabilitySummary, ...]
    assumptions: tuple[str, ...]


def _wilson_interval(successes: int, trials: int, z_score: float = 1.96) -> tuple[float, float]:
    """Return Wilson score confidence interval for a binomial proportion."""

    if trials <= 0:
        raise ValueError("trials must be positive")
    if successes < 0 or successes > trials:
        raise ValueError("successes must be in [0, trials]")

    p_hat = successes / trials
    denominator = 1.0 + (z_score * z_score) / trials
    centre = p_hat + (z_score * z_score) / (2.0 * trials)
    margin = z_score * sqrt((p_hat * (1.0 - p_hat) + (z_score * z_score) / (4.0 * trials)) / trials)
    lower = (centre - margin) / denominator
    upper = (centre + margin) / denominator
    return round(max(0.0, lower), 4), round(min(1.0, upper), 4)


def build_probability_report(summary: MonteCarloSummary) -> RaceProbabilityReport:
    """Convert a Monte Carlo summary into probability report rows."""

    if summary.runs < 1:
        raise ValueError("summary.runs must be >= 1")

    driver_ids = sorted(set(summary.winner_counts) | set(summary.average_finish_position))
    rows: list[DriverProbabilitySummary] = []
    for driver_id in driver_ids:
        wins = summary.winner_counts.get(driver_id, 0)
        lower, upper = _wilson_interval(wins, summary.runs)
        rows.append(
            DriverProbabilitySummary(
                driver_id=driver_id,
                win_probability=round(wins / summary.runs, 4),
                win_ci_lower=lower,
                win_ci_upper=upper,
                expected_finish_position=summary.average_finish_position.get(driver_id, 0.0),
            )
        )

    rows.sort(key=lambda item: (-item.win_probability, item.expected_finish_position, item.driver_id))
    return RaceProbabilityReport(
        runs=summary.runs,
        drivers=tuple(rows),
        assumptions=summary.assumptions
        + ("Win confidence intervals use Wilson score intervals and reflect simulation sample uncertainty.",),
    )
