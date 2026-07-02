import pytest

from backend.app.application.tyre_model import TyrePerformanceModel
from backend.app.domain.models import TyreCompound, TyreState, WeatherState


def _weather(track_grip: float = 0.9) -> WeatherState:
    return WeatherState(
        air_temperature_c=22.0,
        track_temperature_c=34.0,
        humidity=0.55,
        wind_speed_kph=10.0,
        wind_direction_deg=180.0,
        rain_intensity=0.0,
        cloud_coverage=0.2,
        track_grip=track_grip,
        drying_line=1.0,
        forecast_uncertainty=0.15,
    )


def test_tyre_model_penalty_increases_with_wear():
    model = TyrePerformanceModel()
    fresh = TyreState(
        compound=TyreCompound.MEDIUM,
        age_laps=5,
        temperature_c=98.0,
        pressure_psi=22.5,
        wear=0.10,
    )
    worn = TyreState(
        compound=TyreCompound.MEDIUM,
        age_laps=25,
        temperature_c=103.0,
        pressure_psi=23.0,
        wear=0.70,
    )

    fresh_delta = model.estimate_delta(fresh, _weather(), track_degradation_multiplier=1.0)
    worn_delta = model.estimate_delta(worn, _weather(), track_degradation_multiplier=1.0)

    assert worn_delta.lap_time_delta_s > fresh_delta.lap_time_delta_s
    assert worn_delta.condition_label in {"degraded", "critical"}


def test_tyre_model_penalizes_temperature_outside_window():
    model = TyrePerformanceModel()
    optimal = TyreState(
        compound=TyreCompound.SOFT,
        age_laps=6,
        temperature_c=96.0,
        pressure_psi=22.5,
        wear=0.20,
    )
    overheated = TyreState(
        compound=TyreCompound.SOFT,
        age_laps=6,
        temperature_c=116.0,
        pressure_psi=22.5,
        wear=0.20,
    )

    optimal_delta = model.estimate_delta(optimal, _weather(), track_degradation_multiplier=1.0)
    overheated_delta = model.estimate_delta(overheated, _weather(), track_degradation_multiplier=1.0)

    assert overheated_delta.thermal_penalty_s > optimal_delta.thermal_penalty_s
    assert overheated_delta.lap_time_delta_s > optimal_delta.lap_time_delta_s


def test_tyre_model_rejects_invalid_inputs():
    model = TyrePerformanceModel()
    invalid = TyreState(
        compound=TyreCompound.HARD,
        age_laps=3,
        temperature_c=100.0,
        pressure_psi=22.0,
        wear=1.2,
    )

    with pytest.raises(ValueError):
        model.estimate_delta(invalid, _weather(), track_degradation_multiplier=1.0)

    valid = TyreState(
        compound=TyreCompound.HARD,
        age_laps=3,
        temperature_c=100.0,
        pressure_psi=22.0,
        wear=0.2,
    )
    with pytest.raises(ValueError):
        model.estimate_delta(valid, _weather(), track_degradation_multiplier=0.0)
