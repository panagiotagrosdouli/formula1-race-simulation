"""Strongly typed F1 race simulation domain models.

These models are intentionally framework-independent. They should not import
FastAPI, Streamlit, database clients, or plotting libraries.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

DriverId = NewType("DriverId", str)
TeamId = NewType("TeamId", str)
CircuitId = NewType("CircuitId", str)


class TyreCompound(StrEnum):
    """Supported Formula 1 tyre compounds."""

    SOFT = "soft"
    MEDIUM = "medium"
    HARD = "hard"
    INTERMEDIATE = "intermediate"
    WET = "wet"


class RaceEventType(StrEnum):
    """Race events that can change strategy or classification."""

    GREEN_FLAG = "green_flag"
    YELLOW_FLAG = "yellow_flag"
    SAFETY_CAR = "safety_car"
    VIRTUAL_SAFETY_CAR = "virtual_safety_car"
    RED_FLAG = "red_flag"
    MECHANICAL_FAILURE = "mechanical_failure"
    PUNCTURE = "puncture"
    LOCK_UP = "lock_up"
    SPIN = "spin"
    CRASH = "crash"
    PENALTY = "penalty"
    DNF = "dnf"


@dataclass(frozen=True)
class DriverSkillProfile:
    """Driver attributes normalized to the range [0, 1]."""

    race_pace: float
    qualifying_pace: float
    tyre_management: float
    wet_skill: float
    overtaking: float
    defending: float
    consistency: float
    aggression: float
    reaction_time: float
    pressure_handling: float
    mechanical_sympathy: float

    def validate(self) -> None:
        for name, value in self.__dict__.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {value!r}")


@dataclass(frozen=True)
class Driver:
    """A driver participating in a race simulation."""

    id: DriverId
    code: str
    full_name: str
    team_id: TeamId
    skill: DriverSkillProfile


@dataclass(frozen=True)
class CarPerformanceProfile:
    """Car performance and reliability attributes normalized to [0, 1]."""

    power_unit: float
    ers_efficiency: float
    aero_efficiency: float
    downforce: float
    drag_efficiency: float
    top_speed: float
    corner_speed: float
    brake_performance: float
    suspension_compliance: float
    cooling: float
    reliability: float

    def validate(self) -> None:
        for name, value in self.__dict__.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {value!r}")


@dataclass(frozen=True)
class CarWearState:
    """Mutable-like car wear state represented immutably per lap."""

    engine_wear: float = 0.0
    gearbox_wear: float = 0.0
    brake_wear: float = 0.0
    floor_damage: float = 0.0
    front_wing_damage: float = 0.0
    rear_wing_damage: float = 0.0


@dataclass(frozen=True)
class TyreState:
    """Tyre state for a driver at a point in the race."""

    compound: TyreCompound
    age_laps: int
    temperature_c: float
    pressure_psi: float
    wear: float
    graining: float = 0.0
    blistering: float = 0.0
    flat_spot: float = 0.0


@dataclass(frozen=True)
class CircuitProfile:
    """Circuit-level properties that influence race strategy."""

    id: CircuitId
    name: str
    lap_count: int
    pit_lane_loss_s: float
    pit_lane_speed_limit_kph: int
    overtaking_difficulty: float
    safety_car_probability: float
    virtual_safety_car_probability: float
    red_flag_probability: float
    tyre_degradation_multiplier: float
    drs_zones: int


@dataclass(frozen=True)
class WeatherState:
    """Weather and track evolution state."""

    air_temperature_c: float
    track_temperature_c: float
    humidity: float
    wind_speed_kph: float
    wind_direction_deg: float
    rain_intensity: float
    cloud_coverage: float
    track_grip: float
    drying_line: float
    forecast_uncertainty: float


@dataclass(frozen=True)
class RaceEvent:
    """A race event emitted by the simulation engine."""

    lap: int
    event_type: RaceEventType
    description: str
    affected_driver_id: DriverId | None = None
    time_loss_s: float = 0.0


@dataclass(frozen=True)
class DriverRaceState:
    """Per-driver race state at a given lap."""

    driver_id: DriverId
    position: int
    gap_to_leader_s: float
    tyre: TyreState
    car_wear: CarWearState
    fuel_kg: float
    ers_soc: float
    current_lap_time_s: float | None = None
    is_running: bool = True


@dataclass(frozen=True)
class RaceState:
    """Full race state snapshot."""

    circuit: CircuitProfile
    lap: int
    weather: WeatherState
    driver_states: tuple[DriverRaceState, ...]
    events: tuple[RaceEvent, ...]
    random_seed: int
