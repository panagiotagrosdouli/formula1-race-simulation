"""FastAPI routes for the race engineering backend."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.schemas import (
    HealthResponse,
    MonteCarloSimulationRequest,
    MonteCarloSimulationResponse,
    StrategyPreviewRequest,
    StrategyPreviewResponse,
)
from backend.app.application.event_engine import EventProbabilityModel
from backend.app.application.monte_carlo import MonteCarloRaceSimulator
from backend.app.application.strategy_preview import StrategyPreviewInput, preview_pit_window
from backend.app.application.weather_model import WeatherTrend
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
    TyreState,
    WeatherState,
)

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return backend health status."""

    return HealthResponse()


def _circuit_from_request(request: StrategyPreviewRequest | MonteCarloSimulationRequest) -> CircuitProfile:
    return CircuitProfile(
        id=CircuitId(request.circuit.id),
        name=request.circuit.name,
        lap_count=request.circuit.lap_count,
        pit_lane_loss_s=request.circuit.pit_lane_loss_s,
        pit_lane_speed_limit_kph=request.circuit.pit_lane_speed_limit_kph,
        overtaking_difficulty=request.circuit.overtaking_difficulty,
        safety_car_probability=request.circuit.safety_car_probability,
        virtual_safety_car_probability=request.circuit.virtual_safety_car_probability,
        red_flag_probability=request.circuit.red_flag_probability,
        tyre_degradation_multiplier=request.circuit.tyre_degradation_multiplier,
        drs_zones=request.circuit.drs_zones,
    )


@router.post("/strategy/preview", response_model=StrategyPreviewResponse)
def strategy_preview(request: StrategyPreviewRequest) -> StrategyPreviewResponse:
    """Return a deterministic pit-window strategy preview."""

    circuit = _circuit_from_request(request)
    weather = WeatherState(**request.weather.model_dump())
    preview = preview_pit_window(
        StrategyPreviewInput(
            circuit=circuit,
            current_lap=request.current_lap,
            tyre_compound=request.tyre_compound,
            tyre_age_laps=request.tyre_age_laps,
            weather=weather,
        )
    )
    return StrategyPreviewResponse(
        recommended_window_start=preview.recommended_window_start,
        recommended_window_end=preview.recommended_window_end,
        risk_label=preview.risk_label,
        explanation=preview.explanation,
    )


@router.post("/simulations/monte-carlo", response_model=MonteCarloSimulationResponse)
def monte_carlo_simulation(request: MonteCarloSimulationRequest) -> MonteCarloSimulationResponse:
    """Run a controlled Monte Carlo race simulation preview."""

    circuit = _circuit_from_request(request)
    weather = WeatherState(**request.weather.model_dump())
    drivers = tuple(
        Driver(
            id=DriverId(driver.id),
            code=driver.code,
            full_name=driver.full_name,
            team_id=TeamId(driver.team_id),
            skill=DriverSkillProfile(
                race_pace=driver.race_pace,
                qualifying_pace=driver.qualifying_pace,
                tyre_management=driver.tyre_management,
                wet_skill=driver.wet_skill,
                overtaking=driver.overtaking,
                defending=driver.defending,
                consistency=driver.consistency,
                aggression=driver.aggression,
                reaction_time=driver.reaction_time,
                pressure_handling=driver.pressure_handling,
                mechanical_sympathy=driver.mechanical_sympathy,
            ),
        )
        for driver in request.drivers
    )
    cars = {
        car.driver_id: CarPerformanceProfile(
            power_unit=car.power_unit,
            ers_efficiency=car.ers_efficiency,
            aero_efficiency=car.aero_efficiency,
            downforce=car.downforce,
            drag_efficiency=car.drag_efficiency,
            top_speed=car.top_speed,
            corner_speed=car.corner_speed,
            brake_performance=car.brake_performance,
            suspension_compliance=car.suspension_compliance,
            cooling=car.cooling,
            reliability=car.reliability,
        )
        for car in request.cars
    }
    driver_states = tuple(
        DriverRaceState(
            driver_id=DriverId(driver.id),
            position=index + 1,
            gap_to_leader_s=float(index),
            tyre=TyreState(
                compound=request.tyre_compound,
                age_laps=request.tyre_age_laps,
                temperature_c=request.tyre_temperature_c,
                pressure_psi=request.tyre_pressure_psi,
                wear=request.tyre_wear,
            ),
            car_wear=CarWearState(),
            fuel_kg=request.fuel_kg,
            ers_soc=0.70,
        )
        for index, driver in enumerate(request.drivers)
    )
    initial_state = RaceState(
        circuit=circuit,
        lap=request.current_lap,
        weather=weather,
        driver_states=driver_states,
        events=(),
        random_seed=request.random_seed,
    )
    result = MonteCarloRaceSimulator().run(
        initial_state=initial_state,
        drivers=drivers,
        cars=cars,
        base_lap_time_s=request.base_lap_time_s,
        event_probabilities=EventProbabilityModel(
            safety_car=request.safety_car_probability,
            virtual_safety_car=request.virtual_safety_car_probability,
            red_flag=request.red_flag_probability,
            mechanical_failure=request.mechanical_failure_probability,
        ),
        weather_trend=WeatherTrend(rain_intensity_delta_per_lap=request.rain_intensity_delta_per_lap),
        runs=request.runs,
    )
    return MonteCarloSimulationResponse(
        runs=result.summary.runs,
        winner_counts=result.summary.winner_counts,
        average_finish_position=result.summary.average_finish_position,
        assumptions=list(result.summary.assumptions),
    )
