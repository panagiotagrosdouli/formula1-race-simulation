"""Deterministic strategy-preview use case.

This is the first application-layer use case for the enterprise backend. It is
small by design: deterministic, typed, testable, and independent from FastAPI.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.domain.models import CircuitProfile, TyreCompound, WeatherState


@dataclass(frozen=True)
class StrategyPreviewInput:
    """Input data required for an initial pit-window preview."""

    circuit: CircuitProfile
    current_lap: int
    tyre_compound: TyreCompound
    tyre_age_laps: int
    weather: WeatherState


@dataclass(frozen=True)
class StrategyPreview:
    """Human-readable strategic preview for a race state."""

    recommended_window_start: int
    recommended_window_end: int
    risk_label: str
    explanation: str


def preview_pit_window(request: StrategyPreviewInput) -> StrategyPreview:
    """Estimate a deterministic pit window from circuit, tyre and weather state.

    This is not yet the final simulator. It is a transparent baseline that will
    later be replaced by the full tyre/traffic/Monte-Carlo strategy engine.
    """

    if request.current_lap < 1:
        raise ValueError("current_lap must be >= 1")
    if request.tyre_age_laps < 0:
        raise ValueError("tyre_age_laps must be >= 0")

    base_life = {
        TyreCompound.SOFT: 18,
        TyreCompound.MEDIUM: 28,
        TyreCompound.HARD: 38,
        TyreCompound.INTERMEDIATE: 24,
        TyreCompound.WET: 22,
    }[request.tyre_compound]

    degradation_pressure = request.circuit.tyre_degradation_multiplier
    rain_pressure = request.weather.rain_intensity * 0.35
    grip_penalty = max(0.0, 1.0 - request.weather.track_grip) * 0.25
    effective_life = max(6, int(base_life / max(0.65, degradation_pressure + rain_pressure + grip_penalty)))

    laps_remaining_on_tyre = max(1, effective_life - request.tyre_age_laps)
    window_start = min(request.circuit.lap_count, request.current_lap + max(1, laps_remaining_on_tyre - 3))
    window_end = min(request.circuit.lap_count, window_start + 4)

    risk_score = degradation_pressure + rain_pressure + grip_penalty
    if risk_score >= 1.35:
        risk_label = "high"
    elif risk_score >= 1.05:
        risk_label = "medium"
    else:
        risk_label = "low"

    explanation = (
        f"{request.tyre_compound.value.title()} tyre age is {request.tyre_age_laps} laps. "
        f"Circuit degradation multiplier is {request.circuit.tyre_degradation_multiplier:.2f}, "
        f"rain intensity is {request.weather.rain_intensity:.2f}, and track grip is {request.weather.track_grip:.2f}. "
        f"Recommended review window is laps {window_start}-{window_end}."
    )

    return StrategyPreview(
        recommended_window_start=window_start,
        recommended_window_end=window_end,
        risk_label=risk_label,
        explanation=explanation,
    )
