"""Simulation engine interfaces and baseline implementation.

This module introduces a clean boundary around race simulation. The first engine
implementation is intentionally conservative: it validates context and returns
the initial state. Future commits can replace internals without changing API or
UI callers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.app.application.simulation_context import SimulationContext
from backend.app.domain.models import RaceState


@dataclass(frozen=True)
class SimulationResult:
    """Result produced by a simulation engine."""

    initial_state: RaceState
    final_state: RaceState
    lap_states: tuple[RaceState, ...]
    assumptions: tuple[str, ...]


class SimulationEngine(ABC):
    """Interface for deterministic race simulation engines."""

    @abstractmethod
    def run(self, context: SimulationContext) -> SimulationResult:
        """Run a simulation for the supplied context."""


class BaselineSimulationEngine(SimulationEngine):
    """Minimal deterministic engine used as the first production boundary.

    The purpose of this class is architectural: isolate simulation execution
    behind an interface while existing race logic is migrated incrementally.
    """

    def run(self, context: SimulationContext) -> SimulationResult:
        context.validate()
        return SimulationResult(
            initial_state=context.initial_state,
            final_state=context.initial_state,
            lap_states=(context.initial_state,),
            assumptions=(
                "Baseline engine validates deterministic input and returns the initial state.",
                "No race evolution is applied in this first migration step.",
            ),
        )
