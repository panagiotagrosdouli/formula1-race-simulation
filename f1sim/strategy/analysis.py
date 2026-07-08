"""Strategy analysis helpers for undercut, overcut and pit-window interpretation."""

from __future__ import annotations

from dataclasses import dataclass

from f1sim.strategy.generator import RaceStrategy, estimate_pit_window, overcut_delta_s, undercut_delta_s


@dataclass(frozen=True, slots=True)
class StrategyAnalysis:
    """Compact strategy analysis result."""

    strategy: str
    pit_windows: list[tuple[int, int]]
    undercut_delta_s: float
    overcut_delta_s: float
    risk_score: float


def analyse_strategy(
    strategy: RaceStrategy,
    old_tyre_age: int,
    new_tyre_delta_s: float,
    old_tyre_delta_s: float,
    track_position_gain_s: float = 1.0,
) -> StrategyAnalysis:
    """Return transparent strategy analysis metrics."""

    undercut = undercut_delta_s(old_tyre_age, new_tyre_delta_s, old_tyre_delta_s)
    overcut = overcut_delta_s(track_position_gain_s, max(0.0, old_tyre_delta_s - new_tyre_delta_s))
    risk = strategy.stops * 20.0 + len(strategy.pit_laps) * 5.0 + max(strategy.pit_laps or [0]) * 0.05
    return StrategyAnalysis(strategy.name, estimate_pit_window(strategy), undercut, overcut, risk)
