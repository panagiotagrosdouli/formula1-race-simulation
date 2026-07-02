from backend.app.application.event_engine import EventProbabilityModel
from backend.app.application.fuel_model import FuelModel
from backend.app.application.lap_simulator import LapSimulator
from backend.app.application.pace_model import PaceModel, PaceModelParameters
from backend.app.application.tyre_model import TyrePerformanceModel
from backend.app.domain.models import (
    CarPerformanceProfile,
    CarWearState,
    CircuitId,
    CircuitProfile,
    Driver,
    DriverId,
    DriverRaceState,
    DriverSkillProfile,
    RaceState,
    TeamId,
    TyreCompound,
    TyreState,
    WeatherState,
)


def _skill(race_pace: float = 0.88) -> DriverSkillProfile:
    return DriverSkillProfile(
        race_pace=race_pace,
        qualifying_pace=0.86,
        tyre_management=0.82,
        wet_skill=0.75,
        overtaking=0.76,
        defending=0.74,
        consistency=0.87,
        aggression=0.60,
        reaction_time=0.83,
        pressure_handling=0.84,
        mechanical_sympathy=0.80,
    )


def _car(power: float = 0.85) -> CarPerformanceProfile:
    return CarPerformanceProfile(
        power_unit=power,
        ers_efficiency=0.82,
        aero_efficiency=0.84,
        downforce=0.86,
        drag_efficiency=0.80,
        top_speed=0.83,
        corner_speed=0.85,
        brake_performance=0.84,
        suspension_compliance=0.78,
        cooling=0.79,
        reliability=0.88,
    )


def _circuit() -> CircuitProfile:
    return CircuitProfile(
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


def _weather(track_grip: float = 0.88) -> WeatherState:
    return WeatherState(
        air_temperature_c=19.0,
        track_temperature_c=31.0,
        humidity=0.60,
        wind_speed_kph=10.0,
        wind_direction_deg=180.0,
        rain_intensity=0.05,
        cloud_coverage=0.35,
        track_grip=track_grip,
        drying_line=0.8,
        forecast_uncertainty=0.18,
    )


def _driver(code: str = "LEC") -> Driver:
    return Driver(
        id=DriverId(code),
        code=code,
        full_name=code,
        team_id=TeamId("ferrari"),
        skill=_skill(),
    )


def _state(fuel: float = 80.0, wear: float = 0.20, seed: int = 42) -> RaceState:
    driver_state = DriverRaceState(
        driver_id=DriverId("LEC"),
        position=1,
        gap_to_leader_s=0.0,
        tyre=TyreState(
            compound=TyreCompound.MEDIUM,
            age_laps=10,
            temperature_c=98.0,
            pressure_psi=22.5,
            wear=wear,
        ),
        car_wear=CarWearState(),
        fuel_kg=fuel,
        ers_soc=0.70,
    )
    return RaceState(
        circuit=_circuit(),
        lap=12,
        weather=_weather(),
        driver_states=(driver_state,),
        events=(),
        random_seed=seed,
    )


def test_fuel_model_reduces_fuel_and_penalty_with_lower_mass():
    model = FuelModel()

    heavy = model.step(90.0)
    light = model.step(20.0)

    assert heavy.fuel_after_kg < heavy.fuel_before_kg
    assert heavy.lap_time_penalty_s > light.lap_time_penalty_s


def test_pace_model_lap_time_increases_with_tyre_wear():
    tyre_model = TyrePerformanceModel()
    fuel = FuelModel().step(70.0)
    pace_model = PaceModel(PaceModelParameters(base_lap_time_s=92.0))

    fresh = tyre_model.estimate_delta(_state(wear=0.15).driver_states[0].tyre, _weather(), 1.0)
    worn_state = _state(wear=0.80)
    worn = tyre_model.estimate_delta(worn_state.driver_states[0].tyre, _weather(), 1.0)

    fresh_pace = pace_model.estimate_lap_time(_skill(), _car(), fuel, fresh, _weather())
    worn_pace = pace_model.estimate_lap_time(_skill(), _car(), fuel, worn, _weather())

    assert worn_pace.expected_lap_time_s > fresh_pace.expected_lap_time_s


def test_lap_simulator_is_deterministic_for_same_seed():
    simulator = LapSimulator()
    state = _state(seed=123)
    driver = _driver("LEC")
    probabilities = EventProbabilityModel(
        safety_car=0.0,
        virtual_safety_car=0.0,
        red_flag=0.0,
        mechanical_failure=0.0,
    )

    first = simulator.simulate_one_lap(
        state=state,
        drivers=(driver,),
        cars={"LEC": _car()},
        base_lap_time_s=92.0,
        event_probabilities=probabilities,
    )
    second = simulator.simulate_one_lap(
        state=state,
        drivers=(driver,),
        cars={"LEC": _car()},
        base_lap_time_s=92.0,
        event_probabilities=probabilities,
    )

    assert first == second
    assert first.lap == state.lap + 1
    assert first.driver_states[0].fuel_kg < state.driver_states[0].fuel_kg
    assert first.driver_states[0].tyre.age_laps == state.driver_states[0].tyre.age_laps + 1
    assert first.driver_states[0].current_lap_time_s is not None
