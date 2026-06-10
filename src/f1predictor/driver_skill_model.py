from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DriverSkill:
    driver: str
    qualifying: float
    race_pace: float
    overtaking: float
    defending: float
    tyre_management: float
    wet_weather: float


DEFAULT_DRIVER = DriverSkill(
    driver="GEN",
    qualifying=0.50,
    race_pace=0.50,
    overtaking=0.50,
    defending=0.50,
    tyre_management=0.50,
    wet_weather=0.50,
)

DRIVER_SKILLS = {
    "VER": DriverSkill("VER",0.98,0.99,0.95,0.95,0.92,0.96),
    "NOR": DriverSkill("NOR",0.93,0.95,0.89,0.86,0.88,0.87),
    "LEC": DriverSkill("LEC",0.96,0.92,0.88,0.87,0.84,0.85),
    "PIA": DriverSkill("PIA",0.91,0.93,0.85,0.84,0.87,0.83),
    "RUS": DriverSkill("RUS",0.89,0.88,0.84,0.83,0.82,0.84),
    "HAM": DriverSkill("HAM",0.88,0.90,0.90,0.92,0.93,0.95),
}


def get_driver_skill(driver: str) -> DriverSkill:
    return DRIVER_SKILLS.get(driver.upper(), DEFAULT_DRIVER)


def overtake_probability(attacker: str, defender: str, drs_active: bool, circuit_factor: float = 1.0) -> float:
    atk = get_driver_skill(attacker)
    dfn = get_driver_skill(defender)

    probability = 0.10
    probability += (atk.overtaking - dfn.defending) * 0.35

    if drs_active:
        probability += 0.12

    probability *= circuit_factor
    return max(0.01, min(0.95, probability))


def tyre_preservation_bonus(driver: str) -> float:
    skill = get_driver_skill(driver)
    return (skill.tyre_management - 0.5) * 0.08


def wet_weather_bonus(driver: str) -> float:
    skill = get_driver_skill(driver)
    return (skill.wet_weather - 0.5) * 0.40
