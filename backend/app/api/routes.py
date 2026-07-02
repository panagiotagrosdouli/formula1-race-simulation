"""FastAPI routes for the race engineering backend."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.schemas import HealthResponse, StrategyPreviewRequest, StrategyPreviewResponse
from backend.app.application.strategy_preview import StrategyPreviewInput, preview_pit_window
from backend.app.domain.models import CircuitId, CircuitProfile, WeatherState

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return backend health status."""

    return HealthResponse()


@router.post("/strategy/preview", response_model=StrategyPreviewResponse)
def strategy_preview(request: StrategyPreviewRequest) -> StrategyPreviewResponse:
    """Return a deterministic pit-window strategy preview."""

    circuit = CircuitProfile(
        id=CircuitId(request.circuit.id),
        name=request.circuit.name,
        lap_count=request.circuit.lap_count,
        pit_lane_loss_s=request.circuit.pit_lane_loss_s,
        pit_lane_speed_limit_kph=request.circuit.pit_lane_speed_limit_kph,
        overtaking_difficulty=request.circuit.overtaking_difficulty,
        safety_car_probability=request.circuit.safety_car_probability,
        virtual_safety_car_probability=request.circuit.virtual_safety_car_probability,
        red_flag_probability=request.circuit.red_flag_probability,
        tyre_degradation_multiplier=request.circuit.tyre_degradation_multiplier,
        drs_zones=request.circuit.drs_zones,
    )
    weather = WeatherState(**request.weather.model_dump())
    preview = preview_pit_window(
        StrategyPreviewInput(
            circuit=circuit,
            current_lap=request.current_lap,
            tyre_compound=request.tyre_compound,
            tyre_age_laps=request.tyre_age_laps,
            weather=weather,
        )
    )
    return StrategyPreviewResponse(
        recommended_window_start=preview.recommended_window_start,
        recommended_window_end=preview.recommended_window_end,
        risk_label=preview.risk_label,
        explanation=preview.explanation,
    )
