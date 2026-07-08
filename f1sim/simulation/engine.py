"""Lap-by-lap Formula 1 race simulation engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import logging
import random

from f1sim.core.state import DriverState, PitStopEvent, RaceMetrics, TrackState
from f1sim.data.config import RaceConfig
from f1sim.models.fuel import FuelModel
from f1sim.models.tyres import TyreModel
from f1sim.safety_car.model import SafetyCarModel
from f1sim.weather.model import WeatherModel

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RaceResult:
    """Full output from a deterministic race simulation."""

    classification: list[DriverState]
    lap_history: list[dict[str, float | int | str | bool]]
    pit_events: list[PitStopEvent]
    metrics: RaceMetrics

    def to_csv(self, path: str | Path) -> None:
        """Export lap history to CSV."""

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if not self.lap_history:
            return
        with Path(path).open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(self.lap_history[0]))
            writer.writeheader()
            writer.writerows(self.lap_history)


class RaceSimulation:
    """Deterministic lap-by-lap simulation with stochastic model hooks.

    The engine tracks race clock, position ordering, gaps, pit events, tyre age, fuel burn,
    weather, SC/VSC impact and simple traffic loss scaffolding. It is intentionally transparent
    rather than overfitted to non-public data.
    """

    def __init__(self, config: RaceConfig, seed_offset: int = 0) -> None:
        self.config = config
        self.seed = config.seed + seed_offset
        self.rng = random.Random(self.seed)
        self.tyres = TyreModel()
        self.fuel = FuelModel(config.fuel_start_kg, config.fuel_burn_kg_per_lap)
        self.weather = WeatherModel(
            config.rain_probability, config.air_temp_c, config.track_temp_c, self.seed + 101
        )
        self.safety_car = SafetyCarModel(
            config.safety_car_probability_per_lap,
            config.vsc_probability_per_lap,
            config.safety_car_pit_loss_multiplier,
            self.seed + 202,
        )
        self.strategy_by_driver = {strategy.driver_id: strategy for strategy in config.strategies}

    def run(self) -> RaceResult:
        """Run the configured race simulation."""

        drivers = [
            DriverState(
                driver.driver_id,
                driver.base_pace_s,
                driver.start_position,
                compound=self.strategy_by_driver[driver.driver_id].compounds[0],
                fuel_kg=self.config.fuel_start_kg,
            )
            for driver in self.config.drivers
        ]
        track = TrackState(track_temp_c=self.config.track_temp_c, air_temp_c=self.config.air_temp_c)
        history: list[dict[str, float | int | str | bool]] = []
        pit_events: list[PitStopEvent] = []
        pit_loss_total = 0.0

        for lap in range(1, self.config.laps + 1):
            track.lap = lap
            weather = self.weather.step()
            neutralisation = self.safety_car.step()
            track.track_temp_c = weather.track_temp_c
            track.air_temp_c = weather.air_temp_c
            track.wetness = weather.wetness
            track.safety_car_active = neutralisation.safety_car
            track.vsc_active = neutralisation.vsc

            for driver in drivers:
                if driver.retired:
                    continue
                strategy = self.strategy_by_driver[driver.driver_id]
                lap_time = driver.base_pace_s
                lap_time += self.tyres.lap_delta_s(driver.compound, driver.tyre_age_laps, track.track_temp_c, track.wetness)
                lap_time += self.fuel.lap_delta_s(lap)
                lap_time *= neutralisation.lap_time_multiplier

                if driver.position > 1 and not neutralisation.safety_car:
                    traffic_loss = max(0.0, 0.04 * (driver.position - 1) + self.rng.uniform(-0.02, 0.08))
                    lap_time += traffic_loss
                    driver.traffic_loss_s += traffic_loss

                if lap in strategy.pit_laps:
                    next_index = min(driver.pit_stops + 1, len(strategy.compounds) - 1)
                    old_compound = driver.compound
                    driver.compound = strategy.compounds[next_index]
                    driver.tyre_age_laps = 0
                    driver.pit_stops += 1
                    pit_loss = self.config.pit_loss_s * neutralisation.pit_loss_multiplier
                    lap_time += pit_loss
                    pit_loss_total += pit_loss
                    pit_events.append(
                        PitStopEvent(
                            lap,
                            driver.driver_id,
                            old_compound,
                            driver.compound,
                            pit_loss,
                            neutralisation.safety_car or neutralisation.vsc,
                        )
                    )
                else:
                    driver.tyre_age_laps += 1

                driver.current_lap = lap
                driver.fuel_kg = self.fuel.fuel_at_lap_start(lap + 1)
                driver.total_time_s += lap_time + driver.penalty_s
                row = {
                    "lap": lap,
                    "driver_id": driver.driver_id,
                    "lap_time_s": round(lap_time, 3),
                    "total_time_s": round(driver.total_time_s, 3),
                    "compound": driver.compound,
                    "tyre_age_laps": driver.tyre_age_laps,
                    "position": driver.position,
                    "gap_to_leader_s": 0.0,
                    "wetness": round(track.wetness, 3),
                    "safety_car": track.safety_car_active,
                    "vsc": track.vsc_active,
                    "pit_stops": driver.pit_stops,
                }
                driver.history.append(row)
                history.append(row)

            drivers.sort(key=lambda d: d.total_time_s)
            leader_time = drivers[0].total_time_s
            for index, driver in enumerate(drivers, start=1):
                driver.position = index
                driver.history[-1]["position"] = index
                driver.history[-1]["gap_to_leader_s"] = round(driver.total_time_s - leader_time, 3)

        classification = sorted(drivers, key=lambda d: d.total_time_s)
        leader = classification[0]
        strategy = self.strategy_by_driver[leader.driver_id]
        stint_lengths = self._stint_lengths(strategy.pit_laps, self.config.laps)
        metrics = RaceMetrics(
            total_race_time_s=leader.total_time_s,
            expected_finishing_position=float(leader.position),
            pit_stop_count=leader.pit_stops,
            compound_sequence=tuple(strategy.compounds),
            stint_lengths=tuple(stint_lengths),
            degradation_rate_s_per_lap=self.tyres.degradation_rate(strategy.compounds[0], stint_lengths[0]),
            traffic_loss_s=leader.traffic_loss_s,
            pit_loss_s=pit_loss_total,
            undercut_delta_s=0.0,
            overcut_delta_s=0.0,
            risk_percentile=50.0,
        )
        LOGGER.info("Completed %s in %.3f s", self.config.name, metrics.total_race_time_s)
        return RaceResult(classification, history, pit_events, metrics)

    @staticmethod
    def _stint_lengths(pit_laps: list[int], race_laps: int) -> list[int]:
        edges = [0, *pit_laps, race_laps]
        return [edges[index + 1] - edges[index] for index in range(len(edges) - 1)]
