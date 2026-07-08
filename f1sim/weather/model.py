"""Weather uncertainty and track wetness model."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(slots=True)
class WeatherState:
    """Weather state for a lap."""

    raining: bool
    wetness: float
    air_temp_c: float
    track_temp_c: float
    wind_speed_kph: float = 0.0


class WeatherModel:
    """Simple Markov-style dry/wet transition model."""

    def __init__(self, rain_probability: float, air_temp_c: float, track_temp_c: float, seed: int) -> None:
        self.rain_probability = rain_probability
        self.air_temp_c = air_temp_c
        self.track_temp_c = track_temp_c
        self._rng = random.Random(seed)
        self._wetness = 0.0
        self._raining = False

    def step(self) -> WeatherState:
        """Advance weather by one lap."""

        if self._rng.random() < self.rain_probability:
            self._raining = True
        elif self._rng.random() < 0.15:
            self._raining = False
        self._wetness += 0.12 if self._raining else -0.08
        self._wetness = min(1.0, max(0.0, self._wetness))
        track_temp = self.track_temp_c - 6.0 * self._wetness
        return WeatherState(self._raining, self._wetness, self.air_temp_c, track_temp)
