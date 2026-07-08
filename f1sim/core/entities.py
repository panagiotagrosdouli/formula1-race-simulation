"""Core race entities for the F1Sim platform.

This module provides stable public names for the dashboard, tests and future API layers while
reusing the existing state objects implemented in `f1sim.core.state`.
"""

from __future__ import annotations

from f1sim.core.state import DriverState, PitStopEvent, RaceMetrics, TrackState

__all__ = ["DriverState", "TrackState", "PitStopEvent", "RaceMetrics"]
