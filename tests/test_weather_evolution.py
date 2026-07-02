from backend.app.application.event_engine import EventProbabilityModel
from backend.app.application.lap_simulator import LapSimulator
from backend.app.application.weather_model import WeatherEvolutionModel, WeatherTrend
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


def _weather(rain: float = 0.0, grip: float = 0.82, drying: float = 0.25) -> WeatherState:
    return WeatherState(
        air_temperature_c=20.0,
        track_temperature_c=32.0,
        humidity=0.60,
        wind_speed_kph=10.0,
        wind_direction_deg=180.0,
        rain_intensity=rain,
        cloud_coverage=0.4,
        track_grip=grip,
        drying_line=drying,
        forecast_uncertainty=0.20,
    )


def test_weather_model_dries_track_when_rain_is_low():
    model = WeatherEvolutionModel()
    current = _weather(rain=0.0, grip=0.80, drying=0.30)
    trend = WeatherTrend(drying_rate_per_lap=0.05, rubbering_rate_per_lap=0.01)

    next_weather = model.step(current, trend)

    assert next_weather.drying_line > current.drying_line
    assert next_weather.track_grip >= current.track_grip


def test_weather_model_reduces_grip_when_rain_increases():
    model = WeatherEvolutionModel()
    current = _weather(rain=0.15, grip=0.82, drying=0.40)
    trend = WeatherTrend(rain_intensity_delta_per_lap=0.20)

    next_weather = model.step(current, trend)

    assert next_weather.rain_intensity > current.rain_intensity
    assert next_weather.track_grip < current.track_grip
    assert next_weather.drying_line < current.drying_line


def test_lap_simulator_applies_weather_trend():
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
    driver = Driver(
        id=DriverId("LEC"),
        code="LEC",
        full_name="Charles Leclerc",
        team_id=TeamId("ferrari"),
        skill=DriverSkillProfile(
            race_pace=0.88,
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
        ),
    )
    state = RaceState(
        circuit=circuit,
        lap=12,
        weather=_weather(rain=0.10, grip=0.82, drying=0.40),
        driver_states=(
            DriverRaceState(
                driver_id=DriverId("LEC"),
                position=1,
                gap_to_leader_s=0.0,
                tyre=TyreState(
                    compound=TyreCompound.MEDIUM,
                    age_laps=10,
                    temperature_c=98.0,
                    pressure_psi=22.5,
                    wear=0.20,
                ),
                car_wear=CarWearState(),
                fuel_kg=80.0,
                ers_soc=0.70,
            ),
        ),
        events=(),
        random_seed=42,
    )
    car = CarPerformanceProfile(
        power_unit=0.85,
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

    next_state = LapSimulator().simulate_one_lap(
        state=state,
        drivers=(driver,),
        cars={"LEC": car},
        base_lap_time_s=92.0,
        event_probabilities=EventProbabilityModel(
            safety_car=0.0,
            virtual_safety_car=0.0,
            red_flag=0.0,
            mechanical_failure=0.0,
        ),
        weather_trend=WeatherTrend(rain_intensity_delta_per_lap=0.15),
    )

    assert next_state.lap == state.lap + 1
    assert next_state.weather.rain_intensity > state.weather.rain_intensity
    assert next_state.weather.track_grip < state.weather.track_grip
