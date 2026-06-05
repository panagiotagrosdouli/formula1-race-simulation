from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import requests


@dataclass(frozen=True)
class RaceWeather:
    race_name: str
    latitude: float
    longitude: float
    air_temperature: float
    rain_probability: float
    wind_speed: float
    humidity: float
    condition: str


RACE_LOCATIONS = {
    "Australian Grand Prix 2026": (-37.8497, 144.9680),
    "Chinese Grand Prix 2026": (31.3389, 121.2200),
    "Japanese Grand Prix 2026": (34.8431, 136.5410),
    "Bahrain Grand Prix 2026": (26.0325, 50.5106),
    "Saudi Arabian Grand Prix 2026": (21.6319, 39.1044),
    "Miami Grand Prix 2026": (25.9580, -80.2389),
    "Monaco Grand Prix 2026": (43.7347, 7.4206),
    "Canadian Grand Prix 2026": (45.5000, -73.5228),
    "Spanish Grand Prix 2026": (41.5700, 2.2611),
    "Austrian Grand Prix 2026": (47.2197, 14.7647),
    "British Grand Prix 2026": (52.0786, -1.0169),
    "Belgian Grand Prix 2026": (50.4372, 5.9714),
    "Hungarian Grand Prix 2026": (47.5830, 19.2510),
    "Italian Grand Prix 2026": (45.6156, 9.2811),
    "Singapore Grand Prix 2026": (1.2914, 103.8640),
    "United States Grand Prix 2026": (30.1328, -97.6411),
    "Mexico City Grand Prix 2026": (19.4042, -99.0907),
    "São Paulo Grand Prix 2026": (-23.7036, -46.6997),
    "Las Vegas Grand Prix 2026": (36.1147, -115.1728),
    "Qatar Grand Prix 2026": (25.4900, 51.4542),
    "Abu Dhabi Grand Prix 2026": (24.4672, 54.6031),
}


CLIMATE_FALLBACK = {
    "Dry": {
        "air_temperature": 24.0,
        "rain_probability": 0.10,
        "wind_speed": 10.0,
        "humidity": 50.0,
    },
    "Hot": {
        "air_temperature": 32.0,
        "rain_probability": 0.05,
        "wind_speed": 12.0,
        "humidity": 45.0,
    },
    "WetRisk": {
        "air_temperature": 20.0,
        "rain_probability": 0.45,
        "wind_speed": 14.0,
        "humidity": 75.0,
    },
}


def _fallback_condition(race_name: str) -> str:
    wet_risk = ["Belgian", "British", "São Paulo", "Japanese", "Canadian"]
    hot = ["Bahrain", "Saudi", "Qatar", "Abu Dhabi", "Miami", "Singapore"]

    if any(x in race_name for x in wet_risk):
        return "WetRisk"
    if any(x in race_name for x in hot):
        return "Hot"
    return "Dry"


def get_race_weather(
    race_name: str,
    race_date: str | None = None,
    use_live_api: bool = True,
) -> RaceWeather:
    if race_name not in RACE_LOCATIONS:
        raise ValueError(f"Unknown race location: {race_name}")

    lat, lon = RACE_LOCATIONS[race_name]

    if use_live_api and race_date is not None:
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m",
                "start_date": race_date,
                "end_date": race_date,
                "timezone": "auto",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()["hourly"]

            temps = data.get("temperature_2m", [])
            rain = data.get("precipitation_probability", [])
            wind = data.get("wind_speed_10m", [])
            humidity = data.get("relative_humidity_2m", [])

            air_temp = sum(temps) / len(temps)
            rain_prob = max(rain) / 100.0 if rain else 0.0
            wind_speed = sum(wind) / len(wind)
            hum = sum(humidity) / len(humidity)

            condition = "WetRisk" if rain_prob >= 0.35 else "Dry"

            return RaceWeather(
                race_name=race_name,
                latitude=lat,
                longitude=lon,
                air_temperature=round(float(air_temp), 2),
                rain_probability=round(float(rain_prob), 3),
                wind_speed=round(float(wind_speed), 2),
                humidity=round(float(hum), 2),
                condition=condition,
            )

        except Exception:
            pass

    condition = _fallback_condition(race_name)
    values = CLIMATE_FALLBACK[condition]

    return RaceWeather(
        race_name=race_name,
        latitude=lat,
        longitude=lon,
        air_temperature=values["air_temperature"],
        rain_probability=values["rain_probability"],
        wind_speed=values["wind_speed"],
        humidity=values["humidity"],
        condition=condition,
    )
