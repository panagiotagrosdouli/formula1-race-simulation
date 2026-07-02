"""Pydantic schemas for the race engineering API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.app.domain.models import TyreCompound


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "ok"
    service: str = "f1-race-engineering-backend"


class CircuitProfileRequest(BaseModel):
    """Circuit parameters required for a strategy preview."""

    id: str = Field(default="spa")
    name: str = Field(default="Spa-Francorchamps")
    lap_count: int = Field(default=44, ge=1)
    pit_lane_loss_s: float = Field(default=22.0, ge=0)
    pit_lane_speed_limit_kph: int = Field(default=80, ge=1)
    overtaking_difficulty: float = Field(default=0.42, ge=0, le=1)
    safety_car_probability: float = Field(default=0.24, ge=0, le=1)
    virtual_safety_car_probability: float = Field(default=0.18, ge=0, le=1)
    red_flag_probability: float = Field(default=0.04, ge=0, le=1)
    tyre_degradation_multiplier: float = Field(default=1.12, ge=0.1)
    drs_zones: int = Field(default=2, ge=0)


class WeatherStateRequest(BaseModel):
    """Weather parameters required for a strategy preview."""

    air_temperature_c: float = 18.0
    track_temperature_c: float = 28.0
    humidity: float = Field(default=0.65, ge=0, le=1)
    wind_speed_kph: float = Field(default=12.0, ge=0)
    wind_direction_deg: float = Field(default=220.0, ge=0, le=360)
    rain_intensity: float = Field(default=0.20, ge=0, le=1)
    cloud_coverage: float = Field(default=0.55, ge=0, le=1)
    track_grip: float = Field(default=0.82, ge=0, le=1)
    drying_line: float = Field(default=0.20, ge=0, le=1)
    forecast_uncertainty: float = Field(default=0.30, ge=0, le=1)


class StrategyPreviewRequest(BaseModel):
    """Request body for deterministic strategy preview."""

    circuit: CircuitProfileRequest = Field(default_factory=CircuitProfileRequest)
    current_lap: int = Field(default=14, ge=1)
    tyre_compound: TyreCompound = TyreCompound.MEDIUM
    tyre_age_laps: int = Field(default=12, ge=0)
    weather: WeatherStateRequest = Field(default_factory=WeatherStateRequest)


class StrategyPreviewResponse(BaseModel):
    """Response body for deterministic strategy preview."""

    recommended_window_start: int
    recommended_window_end: int
    risk_label: str
    explanation: str
