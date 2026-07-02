"""Simulation context for deterministic race-engineering use cases.

The context is the single input object for simulation services. It keeps domain
state, configuration, and random seed together so simulations are reproducible
and easy to inspect in tests or API calls.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.domain.models import CircuitProfile, Driver, RaceState, WeatherState


@dataclass(frozen=True)
class SimulationOptions:
    """Configuration flags for a simulation run."""

    monte_carlo_runs: int = 1
    enable_safety_car: bool = True
    enable_mechanical_failures: bool = True
    enable_weather_evolution: bool = True

    def validate(self) -> None:
        """Validate option bounds."""

        if self.monte_carlo_runs < 1:
            raise ValueError("monte_carlo_runs must be >= 1")


@dataclass(frozen=True)
class SimulationContext:
    """Complete deterministic context for a simulation run."""

    circuit: CircuitProfile
    weather: WeatherState
    drivers: tuple[Driver, ...]
    initial_state: RaceState
    random_seed: int
    options: SimulationOptions = SimulationOptions()

    def validate(self) -> None:
        """Validate the simulation context before execution."""

        if self.random_seed < 0:
            raise ValueError("random_seed must be >= 0")
        if not self.drivers:
            raise ValueError("at least one driver is required")
        if self.initial_state.circuit != self.circuit:
            raise ValueError("initial_state circuit must match context circuit")
        if self.initial_state.random_seed != self.random_seed:
            raise ValueError("initial_state random_seed must match context random_seed")
        self.options.validate()
        for driver in self.drivers:
            driver.skill.validate()
