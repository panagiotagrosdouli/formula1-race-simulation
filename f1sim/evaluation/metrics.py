"""Engineering metrics for race simulation outputs."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from f1sim.simulation.engine import RaceResult


def summarize_result(result: RaceResult) -> dict[str, Any]:
    """Return a dictionary of headline engineering metrics."""

    metrics = asdict(result.metrics)
    metrics["winner"] = result.classification[0].driver_id
    metrics["classification"] = [driver.driver_id for driver in result.classification]
    return metrics


def probability_beating(target_position_samples: list[int], threshold_position: int) -> float:
    """Return probability of finishing ahead of a target position threshold."""

    if not target_position_samples:
        return 0.0
    return sum(position < threshold_position for position in target_position_samples) / len(target_position_samples)
