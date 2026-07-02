"""Deterministic tyre performance model.

The model is intentionally transparent and parameterized. It is not a claim to
replicate confidential team models; it provides a documented engineering
approximation that can be calibrated with historical race data later.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.domain.models import TyreCompound, TyreState, WeatherState


@dataclass(frozen=True)
class TyreCompoundParameters:
    """Compound-level tyre behaviour parameters."""

    base_life_laps: int
    peak_temp_min_c: float
    peak_temp_max_c: float
    base_degradation_s_per_lap: float
    thermal_sensitivity: float
    mechanical_sensitivity: float
    warmup_laps: int


COMPOUND_PARAMETERS: dict[TyreCompound, TyreCompoundParameters] = {
    TyreCompound.SOFT: TyreCompoundParameters(18, 88.0, 104.0, 0.035, 0.010, 0.018, 2),
    TyreCompound.MEDIUM: TyreCompoundParameters(29, 90.0, 108.0, 0.026, 0.008, 0.014, 3),
    TyreCompound.HARD: TyreCompoundParameters(40, 92.0, 112.0, 0.019, 0.007, 0.011, 4),
    TyreCompound.INTERMEDIATE: TyreCompoundParameters(26, 55.0, 75.0, 0.030, 0.014, 0.015, 2),
    TyreCompound.WET: TyreCompoundParameters(22, 45.0, 65.0, 0.036, 0.018, 0.017, 2),
}


@dataclass(frozen=True)
class TyrePerformanceDelta:
    """Estimated tyre performance contribution for a lap."""

    lap_time_delta_s: float
    thermal_penalty_s: float
    mechanical_penalty_s: float
    wear_penalty_s: float
    warmup_penalty_s: float
    condition_label: str


class TyrePerformanceModel:
    """Estimate tyre-induced lap-time delta from tyre and weather state."""

    def estimate_delta(self, tyre: TyreState, weather: WeatherState, track_degradation_multiplier: float) -> TyrePerformanceDelta:
        """Estimate tyre lap-time penalty in seconds.

        Args:
            tyre: Current tyre state.
            weather: Current weather and track state.
            track_degradation_multiplier: Circuit-specific degradation factor.

        Returns:
            A decomposed tyre performance delta.
        """

        if track_degradation_multiplier <= 0:
            raise ValueError("track_degradation_multiplier must be positive")
        if tyre.age_laps < 0:
            raise ValueError("tyre.age_laps must be >= 0")
        if not 0.0 <= tyre.wear <= 1.0:
            raise ValueError("tyre.wear must be in [0, 1]")

        params = COMPOUND_PARAMETERS[tyre.compound]
        below_window = max(0.0, params.peak_temp_min_c - tyre.temperature_c)
        above_window = max(0.0, tyre.temperature_c - params.peak_temp_max_c)
        thermal_penalty = (below_window + above_window) * params.thermal_sensitivity

        normalized_age = tyre.age_laps / max(params.base_life_laps, 1)
        mechanical_penalty = (
            normalized_age
            * params.base_degradation_s_per_lap
            * tyre.age_laps
            * track_degradation_multiplier
            * params.mechanical_sensitivity
            * 10.0
        )

        wear_penalty = tyre.wear * tyre.wear * 1.4
        surface_penalty = max(0.0, 1.0 - weather.track_grip) * 0.45
        damage_penalty = tyre.graining * 0.35 + tyre.blistering * 0.55 + tyre.flat_spot * 0.75
        warmup_penalty = max(0, params.warmup_laps - tyre.age_laps) * 0.18

        total = thermal_penalty + mechanical_penalty + wear_penalty + surface_penalty + damage_penalty + warmup_penalty

        if tyre.wear >= 0.78 or above_window > 8:
            condition = "critical"
        elif tyre.wear >= 0.55 or thermal_penalty > 0.18:
            condition = "degraded"
        elif warmup_penalty > 0:
            condition = "warming"
        else:
            condition = "optimal"

        return TyrePerformanceDelta(
            lap_time_delta_s=round(total, 4),
            thermal_penalty_s=round(thermal_penalty, 4),
            mechanical_penalty_s=round(mechanical_penalty, 4),
            wear_penalty_s=round(wear_penalty + surface_penalty + damage_penalty, 4),
            warmup_penalty_s=round(warmup_penalty, 4),
            condition_label=condition,
        )
