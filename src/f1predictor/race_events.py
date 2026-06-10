from dataclasses import dataclass
import numpy as np


@dataclass
class RaceEventModel:
    safety_car_probability: float = 0.25
    vsc_probability: float = 0.18
    rain_probability: float = 0.20


    def sample_events(self, rng):
        return {
            'SafetyCar': rng.random() < self.safety_car_probability,
            'VirtualSafetyCar': rng.random() < self.vsc_probability,
            'RainEvent': rng.random() < self.rain_probability,
        }


    def race_impact(self, events):
        impact = 0.0

        if events['SafetyCar']:
            impact += 1.5

        if events['VirtualSafetyCar']:
            impact += 0.7

        if events['RainEvent']:
            impact += 2.0

        return impact
