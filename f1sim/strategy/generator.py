"""Pit-stop strategy generation and ranking utilities."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True, slots=True)
class RaceStrategy:
    """Compound sequence and pit laps for one car."""

    name: str
    compounds: tuple[str, ...]
    pit_laps: tuple[int, ...]

    @property
    def stops(self) -> int:
        """Number of pit stops in this strategy."""

        return len(self.pit_laps)


def generate_candidate_strategies(race_laps: int) -> list[RaceStrategy]:
    """Generate baseline one-, two- and three-stop candidate strategies."""

    return [
        RaceStrategy("one_stop_medium_hard", ("medium", "hard"), (round(race_laps * 0.48),)),
        RaceStrategy("one_stop_soft_hard", ("soft", "hard"), (round(race_laps * 0.35),)),
        RaceStrategy(
            "two_stop_soft_medium_hard",
            ("soft", "medium", "hard"),
            (round(race_laps * 0.30), round(race_laps * 0.66)),
        ),
        RaceStrategy(
            "three_stop_aggressive",
            ("soft", "medium", "medium", "soft"),
            (round(race_laps * 0.22), round(race_laps * 0.50), round(race_laps * 0.76)),
        ),
    ]


def estimate_pit_window(strategy: RaceStrategy, tolerance_laps: int = 3) -> list[tuple[int, int]]:
    """Return pit-window ranges around planned stop laps."""

    return [(max(1, lap - tolerance_laps), lap + tolerance_laps) for lap in strategy.pit_laps]


def undercut_delta_s(old_tyre_age: int, new_tyre_delta_s: float, old_tyre_delta_s: float) -> float:
    """Approximate one-lap undercut gain from new-tyre offset."""

    age_bonus = min(1.5, old_tyre_age * 0.03)
    return old_tyre_delta_s - new_tyre_delta_s + age_bonus


def overcut_delta_s(track_position_gain_s: float, tyre_loss_s: float) -> float:
    """Approximate overcut delta from clear-air extension versus tyre loss."""

    return track_position_gain_s - tyre_loss_s


def rank_strategies(strategies: list[RaceStrategy], objective: str = "race_time") -> list[RaceStrategy]:
    """Rank strategies with a transparent heuristic before full simulation."""

    if objective == "risk":
        return sorted(strategies, key=lambda s: (s.stops, mean(s.pit_laps) if s.pit_laps else 0))
    return sorted(strategies, key=lambda s: (s.stops * 22.0, s.pit_laps))
