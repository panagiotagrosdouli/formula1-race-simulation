"""Deterministic race event engine.

Events are generated from seeded probability draws. This keeps behaviour
reproducible while making the stochastic assumptions explicit and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

from backend.app.domain.models import RaceEvent, RaceEventType, RaceState


@dataclass(frozen=True)
class EventProbabilityModel:
    """Per-lap event probabilities used by the deterministic event engine."""

    safety_car: float
    virtual_safety_car: float
    red_flag: float
    mechanical_failure: float

    def validate(self) -> None:
        for name, value in self.__dict__.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} probability must be in [0, 1], got {value!r}")


class DeterministicEventEngine:
    """Generate race events from explicit seeded probability models."""

    def generate_events(
        self,
        state: RaceState,
        probabilities: EventProbabilityModel,
        seed_offset: int = 0,
    ) -> tuple[RaceEvent, ...]:
        """Generate reproducible events for one race-state snapshot."""

        probabilities.validate()
        rng = Random(state.random_seed + state.lap + seed_offset)
        events: list[RaceEvent] = []

        if rng.random() < probabilities.red_flag:
            events.append(RaceEvent(state.lap, RaceEventType.RED_FLAG, "Red flag probability draw triggered."))
            return tuple(events)

        if rng.random() < probabilities.safety_car:
            events.append(RaceEvent(state.lap, RaceEventType.SAFETY_CAR, "Safety car probability draw triggered."))
        elif rng.random() < probabilities.virtual_safety_car:
            events.append(RaceEvent(state.lap, RaceEventType.VIRTUAL_SAFETY_CAR, "Virtual safety car probability draw triggered."))

        if rng.random() < probabilities.mechanical_failure and state.driver_states:
            target_index = rng.randrange(len(state.driver_states))
            target = state.driver_states[target_index]
            events.append(
                RaceEvent(
                    lap=state.lap,
                    event_type=RaceEventType.MECHANICAL_FAILURE,
                    description="Mechanical failure probability draw triggered.",
                    affected_driver_id=target.driver_id,
                    time_loss_s=30.0,
                )
            )

        return tuple(events)
