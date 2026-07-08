"""Configuration loading and validation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DriverConfig(BaseModel):
    """Input configuration for a simulated driver."""

    driver_id: str
    base_pace_s: float
    start_position: int


class StrategyConfig(BaseModel):
    """Planned strategy for one driver."""

    driver_id: str
    compounds: list[str] = Field(default_factory=lambda: ["medium", "hard"])
    pit_laps: list[int] = Field(default_factory=lambda: [28])


class RaceConfig(BaseModel):
    """Top-level deterministic and stochastic race configuration."""

    name: str = "demo_race"
    seed: int = 42
    laps: int = 58
    pit_loss_s: float = 22.0
    safety_car_pit_loss_multiplier: float = 0.62
    fuel_start_kg: float = 100.0
    fuel_burn_kg_per_lap: float = 1.7
    track_temp_c: float = 35.0
    air_temp_c: float = 25.0
    rain_probability: float = 0.0
    safety_car_probability_per_lap: float = 0.02
    vsc_probability_per_lap: float = 0.03
    drivers: list[DriverConfig]
    strategies: list[StrategyConfig]
    output_dir: str = "results"


def load_race_config(path: str | Path) -> RaceConfig:
    """Load a race configuration from YAML.

    Args:
        path: YAML file path.

    Returns:
        Validated race configuration.
    """

    data: dict[str, Any] = yaml.safe_load(Path(path).read_text())
    return RaceConfig.model_validate(data)
