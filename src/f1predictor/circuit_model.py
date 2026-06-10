from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CircuitProfile:
    name: str
    overtaking_difficulty: float
    tyre_stress: float
    safety_car_factor: float
    rain_sensitivity: float
    drs_effectiveness: float
    base_lap_modifier: float = 0.0


CIRCUIT_PROFILES = {
    "monaco": CircuitProfile(
        name="Monaco",
        overtaking_difficulty=0.95,
        tyre_stress=0.35,
        safety_car_factor=1.45,
        rain_sensitivity=1.35,
        drs_effectiveness=0.25,
        base_lap_modifier=2.0,
    ),
    "monza": CircuitProfile(
        name="Monza",
        overtaking_difficulty=0.25,
        tyre_stress=0.45,
        safety_car_factor=0.85,
        rain_sensitivity=0.95,
        drs_effectiveness=1.30,
        base_lap_modifier=-1.2,
    ),
    "silverstone": CircuitProfile(
        name="Silverstone",
        overtaking_difficulty=0.45,
        tyre_stress=0.80,
        safety_car_factor=0.95,
        rain_sensitivity=1.25,
        drs_effectiveness=0.90,
        base_lap_modifier=0.2,
    ),
    "spa": CircuitProfile(
        name="Spa-Francorchamps",
        overtaking_difficulty=0.35,
        tyre_stress=0.70,
        safety_car_factor=1.15,
        rain_sensitivity=1.60,
        drs_effectiveness=1.10,
        base_lap_modifier=0.5,
    ),
    "singapore": CircuitProfile(
        name="Singapore",
        overtaking_difficulty=0.80,
        tyre_stress=0.75,
        safety_car_factor=1.55,
        rain_sensitivity=1.20,
        drs_effectiveness=0.45,
        base_lap_modifier=1.6,
    ),
    "bahrain": CircuitProfile(
        name="Bahrain",
        overtaking_difficulty=0.40,
        tyre_stress=0.85,
        safety_car_factor=0.90,
        rain_sensitivity=0.25,
        drs_effectiveness=1.05,
        base_lap_modifier=0.0,
    ),
    "default": CircuitProfile(
        name="Generic Circuit",
        overtaking_difficulty=0.50,
        tyre_stress=0.60,
        safety_car_factor=1.00,
        rain_sensitivity=1.00,
        drs_effectiveness=0.80,
        base_lap_modifier=0.0,
    ),
}


def get_circuit_profile(race_name: str | None) -> CircuitProfile:
    if not race_name:
        return CIRCUIT_PROFILES["default"]

    key = race_name.lower()
    for circuit_key, profile in CIRCUIT_PROFILES.items():
        if circuit_key != "default" and circuit_key in key:
            return profile

    return CIRCUIT_PROFILES["default"]


def circuit_summary(profile: CircuitProfile) -> dict[str, float | str]:
    return {
        "Circuit": profile.name,
        "OvertakingDifficulty": profile.overtaking_difficulty,
        "TyreStress": profile.tyre_stress,
        "SafetyCarFactor": profile.safety_car_factor,
        "RainSensitivity": profile.rain_sensitivity,
        "DRSEffectiveness": profile.drs_effectiveness,
    }
