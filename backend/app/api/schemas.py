"""Pydantic schemas for the race engineering API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.app.domain.models import TyreCompound


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "ok"
    service: str = "f1-race-engineering-backend"


class CircuitProfileRequest(BaseModel):
    """Circuit parameters required for strategy and simulation endpoints."""

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
    """Weather parameters required for strategy and simulation endpoints."""

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


class DriverSimulationRequest(BaseModel):
    """Minimal driver input for a simulation preview."""

    id: str = Field(default="LEC")
    code: str = Field(default="LEC")
    full_name: str = Field(default="Charles Leclerc")
    team_id: str = Field(default="ferrari")
    race_pace: float = Field(default=0.88, ge=0, le=1)
    qualifying_pace: float = Field(default=0.86, ge=0, le=1)
    tyre_management: float = Field(default=0.82, ge=0, le=1)
    wet_skill: float = Field(default=0.75, ge=0, le=1)
    overtaking: float = Field(default=0.76, ge=0, le=1)
    defending: float = Field(default=0.74, ge=0, le=1)
    consistency: float = Field(default=0.87, ge=0, le=1)
    aggression: float = Field(default=0.60, ge=0, le=1)
    reaction_time: float = Field(default=0.83, ge=0, le=1)
    pressure_handling: float = Field(default=0.84, ge=0, le=1)
    mechanical_sympathy: float = Field(default=0.80, ge=0, le=1)


class CarSimulationRequest(BaseModel):
    """Minimal car input for a simulation preview."""

    driver_id: str = Field(default="LEC")
    power_unit: float = Field(default=0.85, ge=0, le=1)
    ers_efficiency: float = Field(default=0.82, ge=0, le=1)
    aero_efficiency: float = Field(default=0.84, ge=0, le=1)
    downforce: float = Field(default=0.86, ge=0, le=1)
    drag_efficiency: float = Field(default=0.80, ge=0, le=1)
    top_speed: float = Field(default=0.83, ge=0, le=1)
    corner_speed: float = Field(default=0.85, ge=0, le=1)
    brake_performance: float = Field(default=0.84, ge=0, le=1)
    suspension_compliance: float = Field(default=0.78, ge=0, le=1)
    cooling: float = Field(default=0.79, ge=0, le=1)
    reliability: float = Field(default=0.88, ge=0, le=1)


class MonteCarloSimulationRequest(BaseModel):
    """Request body for a controlled Monte Carlo race simulation."""

    circuit: CircuitProfileRequest = Field(default_factory=CircuitProfileRequest)
    weather: WeatherStateRequest = Field(default_factory=WeatherStateRequest)
    drivers: list[DriverSimulationRequest] = Field(default_factory=lambda: [DriverSimulationRequest()])
    cars: list[CarSimulationRequest] = Field(default_factory=lambda: [CarSimulationRequest()])
    current_lap: int = Field(default=12, ge=1)
    base_lap_time_s: float = Field(default=92.0, gt=0)
    fuel_kg: float = Field(default=30.0, ge=0)
    tyre_compound: TyreCompound = TyreCompound.MEDIUM
    tyre_age_laps: int = Field(default=10, ge=0)
    tyre_temperature_c: float = 98.0
    tyre_pressure_psi: float = 22.5
    tyre_wear: float = Field(default=0.20, ge=0, le=1)
    runs: int = Field(default=10, ge=1, le=250)
    random_seed: int = Field(default=42, ge=0)
    safety_car_probability: float = Field(default=0.02, ge=0, le=1)
    virtual_safety_car_probability: float = Field(default=0.01, ge=0, le=1)
    red_flag_probability: float = Field(default=0.0, ge=0, le=1)
    mechanical_failure_probability: float = Field(default=0.005, ge=0, le=1)
    rain_intensity_delta_per_lap: float = Field(default=0.0, ge=-1, le=1)


class DriverProbabilityResponse(BaseModel):
    """Probability-analysis row for one driver."""

    driver_id: str
    win_probability: float
    win_ci_lower: float
    win_ci_upper: float
    expected_finish_position: float


class MonteCarloSimulationResponse(BaseModel):
    """Response body for a controlled Monte Carlo race simulation."""

    runs: int
    winner_counts: dict[str, int]
    average_finish_position: dict[str, float]
    probabilities: list[DriverProbabilityResponse]
    assumptions: list[str]
