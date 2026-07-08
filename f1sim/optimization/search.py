"""Strategy optimisation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from f1sim.strategy.generator import RaceStrategy, generate_candidate_strategies


@dataclass(frozen=True, slots=True)
class OptimizationResult:
    """Result from a strategy optimisation run."""

    best_strategy: RaceStrategy
    score: float
    evaluated: list[tuple[RaceStrategy, float]]


def grid_search_strategy(race_laps: int, objective: Callable[[RaceStrategy], float]) -> OptimizationResult:
    """Brute-force/grid-search baseline over generated strategies."""

    evaluated = [(strategy, objective(strategy)) for strategy in generate_candidate_strategies(race_laps)]
    best_strategy, score = min(evaluated, key=lambda item: item[1])
    return OptimizationResult(best_strategy, score, evaluated)


def bayesian_optimization_scaffold() -> str:
    """Document planned Bayesian optimisation integration."""

    return "Planned: Bayesian optimisation over pit laps, compounds, tyre life and risk objectives."


def genetic_algorithm_scaffold() -> str:
    """Document planned GA integration."""

    return "Planned: genetic algorithm for multi-car, multi-objective strategy search."
