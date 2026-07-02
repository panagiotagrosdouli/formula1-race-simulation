from backend.app.application.event_engine import DeterministicEventEngine, EventProbabilityModel
from backend.app.application.simulation_context import SimulationContext, SimulationOptions
from backend.app.application.simulation_engine import BaselineSimulationEngine
from backend.app.domain.models import (
    CarWearState,
    CircuitId,
    CircuitProfile,
    Driver,
    DriverId,
    DriverRaceState,
    DriverSkillProfile,
    RaceEventType,
    RaceState,
    TeamId,
    TyreCompound,
    TyreState,
    WeatherState,
)


def _skill() -> DriverSkillProfile:
    return DriverSkillProfile(
        race_pace=0.9,
        qualifying_pace=0.87,
        tyre_management=0.82,
        wet_skill=0.76,
        overtaking=0.78,
        defending=0.75,
        consistency=0.88,
        aggression=0.62,
        reaction_time=0.84,
        pressure_handling=0.85,
        mechanical_sympathy=0.80,
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


def _weather() -> WeatherState:
    return WeatherState(
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


def _state(seed: int = 42) -> RaceState:
    circuit = _circuit()
    driver_state = DriverRaceState(
        driver_id=DriverId("LEC"),
        position=1,
        gap_to_leader_s=0.0,
        tyre=TyreState(
            compound=TyreCompound.MEDIUM,
            age_laps=10,
            temperature_c=92.0,
            pressure_psi=22.5,
            wear=0.28,
        ),
        car_wear=CarWearState(),
        fuel_kg=80.0,
        ers_soc=0.72,
    )
    return RaceState(
        circuit=circuit,
        lap=12,
        weather=_weather(),
        driver_states=(driver_state,),
        events=(),
        random_seed=seed,
    )


def test_simulation_context_validates_and_baseline_engine_is_deterministic():
    driver = Driver(
        id=DriverId("LEC"),
        code="LEC",
        full_name="Charles Leclerc",
        team_id=TeamId("ferrari"),
        skill=_skill(),
    )
    state = _state(seed=7)
    context = SimulationContext(
        circuit=state.circuit,
        weather=state.weather,
        drivers=(driver,),
        initial_state=state,
        random_seed=7,
        options=SimulationOptions(monte_carlo_runs=5),
    )

    result = BaselineSimulationEngine().run(context)

    assert result.initial_state == state
    assert result.final_state == state
    assert result.lap_states == (state,)
    assert result.assumptions


def test_event_engine_is_seeded_and_reproducible():
    state = _state(seed=123)
    model = EventProbabilityModel(
        safety_car=1.0,
        virtual_safety_car=0.0,
        red_flag=0.0,
        mechanical_failure=1.0,
    )
    engine = DeterministicEventEngine()

    first = engine.generate_events(state, model)
    second = engine.generate_events(state, model)

    assert first == second
    assert any(event.event_type == RaceEventType.SAFETY_CAR for event in first)
    assert any(event.event_type == RaceEventType.MECHANICAL_FAILURE for event in first)
