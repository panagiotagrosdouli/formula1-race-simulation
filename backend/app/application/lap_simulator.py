"""One-lap deterministic race-state simulator."""

from __future__ import annotations

from dataclasses import replace

from backend.app.application.event_engine import DeterministicEventEngine, EventProbabilityModel
from backend.app.application.fuel_model import FuelModel
from backend.app.application.pace_model import PaceModel, PaceModelParameters
from backend.app.application.tyre_model import TyrePerformanceModel
from backend.app.application.weather_model import WeatherEvolutionModel, WeatherTrend
from backend.app.domain.models import CarPerformanceProfile, Driver, DriverRaceState, RaceState, RaceEventType


class LapSimulator:
    """Advance a RaceState by one lap using deterministic sub-models."""

    def __init__(
        self,
        fuel_model: FuelModel | None = None,
        tyre_model: TyrePerformanceModel | None = None,
        event_engine: DeterministicEventEngine | None = None,
        weather_model: WeatherEvolutionModel | None = None,
    ) -> None:
        self.fuel_model = fuel_model or FuelModel()
        self.tyre_model = tyre_model or TyrePerformanceModel()
        self.event_engine = event_engine or DeterministicEventEngine()
        self.weather_model = weather_model or WeatherEvolutionModel()

    def simulate_one_lap(
        self,
        state: RaceState,
        drivers: tuple[Driver, ...],
        cars: dict[str, CarPerformanceProfile],
        base_lap_time_s: float,
        event_probabilities: EventProbabilityModel,
        weather_trend: WeatherTrend | None = None,
    ) -> RaceState:
        """Return a new RaceState for lap N+1.

        Args:
            state: Current race state.
            drivers: Driver definitions keyed by driver id.
            cars: Car performance profiles keyed by driver id string.
            base_lap_time_s: Baseline lap time for the circuit/conditions.
            event_probabilities: Explicit probability model for this lap.
            weather_trend: Optional deterministic weather trend for the next lap.
        """

        if state.lap >= state.circuit.lap_count:
            return state

        driver_by_id = {str(driver.id): driver for driver in drivers}
        pace_model = PaceModel(PaceModelParameters(base_lap_time_s=base_lap_time_s))
        events = self.event_engine.generate_events(state, event_probabilities)
        safety_car_active = any(event.event_type in {RaceEventType.SAFETY_CAR, RaceEventType.VIRTUAL_SAFETY_CAR} for event in events)

        next_driver_states: list[DriverRaceState] = []
        for driver_state in state.driver_states:
            driver_id = str(driver_state.driver_id)
            driver = driver_by_id[driver_id]
            car = cars[driver_id]
            fuel_delta = self.fuel_model.step(driver_state.fuel_kg, safety_car_active=safety_car_active)
            tyre_delta = self.tyre_model.estimate_delta(
                driver_state.tyre,
                state.weather,
                track_degradation_multiplier=state.circuit.tyre_degradation_multiplier,
            )
            pace = pace_model.estimate_lap_time(
                driver_skill=driver.skill,
                car=car,
                fuel=fuel_delta,
                tyre=tyre_delta,
                weather=state.weather,
                traffic_factor=0.0,
            )
            next_tyre = replace(
                driver_state.tyre,
                age_laps=driver_state.tyre.age_laps + 1,
                wear=min(1.0, round(driver_state.tyre.wear + 1.0 / max(1, state.circuit.lap_count), 4)),
            )
            next_driver_states.append(
                replace(
                    driver_state,
                    tyre=next_tyre,
                    fuel_kg=fuel_delta.fuel_after_kg,
                    current_lap_time_s=pace.expected_lap_time_s,
                )
            )

        ordered = sorted(next_driver_states, key=lambda item: item.current_lap_time_s or 9999.0)
        reclassified = tuple(
            replace(item, position=index + 1, gap_to_leader_s=round((item.current_lap_time_s or 0.0) - (ordered[0].current_lap_time_s or 0.0), 4))
            for index, item in enumerate(ordered)
        )
        next_weather = self.weather_model.step(state.weather, weather_trend or WeatherTrend())

        return RaceState(
            circuit=state.circuit,
            lap=state.lap + 1,
            weather=next_weather,
            driver_states=reclassified,
            events=state.events + events,
            random_seed=state.random_seed,
        )
