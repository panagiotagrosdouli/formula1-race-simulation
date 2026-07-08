"""Result objects for race simulation outputs."""

from __future__ import annotations

from f1sim.core.state import PitStopEvent, RaceMetrics
from f1sim.simulation.engine import RaceResult

__all__ = ["RaceResult", "RaceMetrics", "PitStopEvent"]
