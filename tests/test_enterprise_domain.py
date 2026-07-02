import pytest

from backend.app.application.strategy_preview import StrategyPreviewInput, preview_pit_window
from backend.app.domain.models import CircuitId, CircuitProfile, DriverSkillProfile, TyreCompound, WeatherState


def test_driver_skill_profile_validates_normalized_values():
    profile = DriverSkillProfile(
        race_pace=0.9,
        qualifying_pace=0.85,
        tyre_management=0.8,
        wet_skill=0.75,
        overtaking=0.7,
        defending=0.72,
        consistency=0.88,
        aggression=0.64,
        reaction_time=0.82,
        pressure_handling=0.86,
        mechanical_sympathy=0.79,
    )

    profile.validate()


def test_driver_skill_profile_rejects_invalid_values():
    profile = DriverSkillProfile(
        race_pace=1.2,
        qualifying_pace=0.85,
        tyre_management=0.8,
        wet_skill=0.75,
        overtaking=0.7,
        defending=0.72,
        consistency=0.88,
        aggression=0.64,
        reaction_time=0.82,
        pressure_handling=0.86,
        mechanical_sympathy=0.79,
    )

    with pytest.raises(ValueError):
        profile.validate()


def test_strategy_preview_is_deterministic_and_bounded():
    circuit = CircuitProfile(
        id=CircuitId("spa"),
        name="Spa-Francorchamps",
        lap_count=44,
        pit_lane_loss_s=22.0,
        pit_lane_speed_limit_kph=80,
        overtaking_difficulty=0.42,
        safety_car_probability=0.24,
        virtual_safety_car_probability=0.18,
        red_flag_probability=0.04,
        tyre_degradation_multiplier=1.12,
        drs_zones=2,
    )
    weather = WeatherState(
        air_temperature_c=18.0,
        track_temperature_c=28.0,
        humidity=0.65,
        wind_speed_kph=12.0,
        wind_direction_deg=220.0,
        rain_intensity=0.20,
        cloud_coverage=0.55,
        track_grip=0.82,
        drying_line=0.20,
        forecast_uncertainty=0.30,
    )

    request = StrategyPreviewInput(
        circuit=circuit,
        current_lap=14,
        tyre_compound=TyreCompound.MEDIUM,
        tyre_age_laps=12,
        weather=weather,
    )

    first = preview_pit_window(request)
    second = preview_pit_window(request)

    assert first == second
    assert 14 <= first.recommended_window_start <= circuit.lap_count
    assert first.recommended_window_start <= first.recommended_window_end <= circuit.lap_count
    assert first.risk_label in {"low", "medium", "high"}
