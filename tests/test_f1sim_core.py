from __future__ import annotations

from pathlib import Path

from f1sim.data.config import load_race_config
from f1sim.models.fuel import FuelModel
from f1sim.models.tyres import TyreModel
from f1sim.safety_car.model import SafetyCarModel
from f1sim.simulation.engine import RaceSimulation
from f1sim.simulation.monte_carlo import MonteCarloSimulation
from f1sim.strategy.generator import generate_candidate_strategies
from f1sim.weather.model import WeatherModel


def test_tyre_degradation_increases_with_age() -> None:
    model = TyreModel()
    assert model.lap_delta_s("medium", 20, 35.0) > model.lap_delta_s("medium", 1, 35.0)


def test_fuel_model_gets_faster_as_fuel_burns() -> None:
    model = FuelModel(start_kg=100.0, burn_kg_per_lap=2.0)
    assert model.lap_delta_s(20) < model.lap_delta_s(1)


def test_weather_transition_is_bounded() -> None:
    weather = WeatherModel(0.8, 20.0, 30.0, seed=1)
    states = [weather.step() for _ in range(10)]
    assert all(0.0 <= state.wetness <= 1.0 for state in states)


def test_safety_car_effect_can_reduce_pit_loss() -> None:
    model = SafetyCarModel(1.0, 0.0, 0.6, seed=1)
    state = model.step()
    assert state.safety_car
    assert state.pit_loss_multiplier < 1.0


def test_strategy_generator_contains_multiple_stop_counts() -> None:
    stops = {strategy.stops for strategy in generate_candidate_strategies(58)}
    assert {1, 2, 3}.issubset(stops)


def test_race_simulation_loop_runs() -> None:
    config = load_race_config(Path("configs/experiments/dry_race.yml"))
    result = RaceSimulation(config).run()
    assert len(result.classification) == len(config.drivers)
    assert len(result.lap_history) == config.laps * len(config.drivers)


def test_monte_carlo_reproducibility() -> None:
    config = load_race_config(Path("configs/experiments/dry_race.yml"))
    a = MonteCarloSimulation(config, runs=5, seed=123).run()
    b = MonteCarloSimulation(config, runs=5, seed=123).run()
    assert a.expected_time_s == b.expected_time_s
