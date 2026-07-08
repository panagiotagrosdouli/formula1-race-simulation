"""Core race-state objects used by the simulation engine."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DriverState:
    """Mutable state for one simulated driver.

    Attributes:
        driver_id: Stable driver identifier used in outputs.
        base_pace_s: Reference clean-air lap time in seconds.
        position: Current race position, one-indexed.
        total_time_s: Accumulated race time.
        current_lap: Completed lap count.
        compound: Current tyre compound.
        tyre_age_laps: Laps completed on current tyre set.
        fuel_kg: Current fuel mass.
        pit_stops: Number of completed pit stops.
        retired: Whether the car has retired.
        penalty_s: Accumulated penalty time.
    """

    driver_id: str
    base_pace_s: float
    position: int
    total_time_s: float = 0.0
    current_lap: int = 0
    compound: str = "medium"
    tyre_age_laps: int = 0
    fuel_kg: float = 100.0
    pit_stops: int = 0
    retired: bool = False
    penalty_s: float = 0.0
    traffic_loss_s: float = 0.0
    history: list[dict[str, float | int | str | bool]] = field(default_factory=list)


@dataclass(slots=True)
class TrackState:
    """Track-level state shared by all cars."""

    lap: int = 0
    track_temp_c: float = 35.0
    air_temp_c: float = 25.0
    wetness: float = 0.0
    safety_car_active: bool = False
    vsc_active: bool = False
    wind_speed_kph: float = 0.0


@dataclass(frozen=True, slots=True)
class PitStopEvent:
    """A scheduled or executed pit stop."""

    lap: int
    driver_id: str
    old_compound: str
    new_compound: str
    loss_s: float
    under_neutralisation: bool = False


@dataclass(frozen=True, slots=True)
class RaceMetrics:
    """Summary metrics returned after a race simulation."""

    total_race_time_s: float
    expected_finishing_position: float
    pit_stop_count: int
    compound_sequence: tuple[str, ...]
    stint_lengths: tuple[int, ...]
    degradation_rate_s_per_lap: float
    traffic_loss_s: float
    pit_loss_s: float
    undercut_delta_s: float
    overcut_delta_s: float
    risk_percentile: float
