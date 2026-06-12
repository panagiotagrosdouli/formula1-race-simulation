from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd


@dataclass(frozen=True)
class RaceEvent:
    round_no: int
    name: str
    circuit: str
    location: str
    start_utc: datetime

    @property
    def start_local(self) -> datetime:
        return self.start_utc.astimezone(ZoneInfo("Europe/Athens"))


# 2026 race-day schedule. Times are stored in UTC so the countdown is stable on
# Streamlit Cloud and local machines. Update this table if official start times
# are revised during the season.
F1_2026_CALENDAR: list[RaceEvent] = [
    RaceEvent(1, "Australian Grand Prix", "Albert Park Circuit", "Melbourne", datetime(2026, 3, 8, 4, 0, tzinfo=timezone.utc)),
    RaceEvent(2, "Chinese Grand Prix", "Shanghai International Circuit", "Shanghai", datetime(2026, 3, 15, 7, 0, tzinfo=timezone.utc)),
    RaceEvent(3, "Japanese Grand Prix", "Suzuka Circuit", "Suzuka", datetime(2026, 3, 29, 5, 0, tzinfo=timezone.utc)),
    RaceEvent(4, "Miami Grand Prix", "Miami International Autodrome", "Miami", datetime(2026, 5, 3, 17, 0, tzinfo=timezone.utc)),
    RaceEvent(5, "Canadian Grand Prix", "Circuit Gilles-Villeneuve", "Montreal", datetime(2026, 5, 24, 20, 0, tzinfo=timezone.utc)),
    RaceEvent(6, "Monaco Grand Prix", "Circuit de Monaco", "Monte Carlo", datetime(2026, 6, 7, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(7, "Barcelona-Catalunya Grand Prix", "Circuit de Barcelona-Catalunya", "Barcelona", datetime(2026, 6, 14, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(8, "Austrian Grand Prix", "Red Bull Ring", "Spielberg", datetime(2026, 6, 28, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(9, "British Grand Prix", "Silverstone Circuit", "Silverstone", datetime(2026, 7, 5, 14, 0, tzinfo=timezone.utc)),
    RaceEvent(10, "Belgian Grand Prix", "Circuit de Spa-Francorchamps", "Spa-Francorchamps", datetime(2026, 7, 19, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(11, "Hungarian Grand Prix", "Hungaroring", "Mogyorod", datetime(2026, 7, 26, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(12, "Dutch Grand Prix", "Circuit Zandvoort", "Zandvoort", datetime(2026, 8, 23, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(13, "Italian Grand Prix", "Autodromo Nazionale Monza", "Monza", datetime(2026, 9, 6, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(14, "Spanish Grand Prix", "Madring", "Madrid", datetime(2026, 9, 13, 13, 0, tzinfo=timezone.utc)),
    RaceEvent(15, "Azerbaijan Grand Prix", "Baku City Circuit", "Baku", datetime(2026, 9, 26, 11, 0, tzinfo=timezone.utc)),
    RaceEvent(16, "Singapore Grand Prix", "Marina Bay Street Circuit", "Singapore", datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)),
    RaceEvent(17, "United States Grand Prix", "Circuit of the Americas", "Austin", datetime(2026, 10, 25, 20, 0, tzinfo=timezone.utc)),
    RaceEvent(18, "Mexico City Grand Prix", "Autodromo Hermanos Rodriguez", "Mexico City", datetime(2026, 11, 1, 20, 0, tzinfo=timezone.utc)),
]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def get_next_race(reference_time: datetime | None = None) -> RaceEvent | None:
    current = reference_time or now_utc()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    for race in F1_2026_CALENDAR:
        if race.start_utc > current:
            return race
    return None


def get_previous_race(reference_time: datetime | None = None) -> RaceEvent | None:
    current = reference_time or now_utc()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    previous = [race for race in F1_2026_CALENDAR if race.start_utc <= current]
    return previous[-1] if previous else None


def countdown_components(race: RaceEvent, reference_time: datetime | None = None) -> dict[str, int]:
    current = reference_time or now_utc()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    delta = race.start_utc - current.astimezone(timezone.utc)
    total_seconds = max(0, int(delta.total_seconds()))
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds, "total_seconds": total_seconds}


def countdown_label(race: RaceEvent, reference_time: datetime | None = None) -> str:
    c = countdown_components(race, reference_time)
    return f"{c['days']}d {c['hours']}h {c['minutes']}m {c['seconds']}s"


def calendar_dataframe(reference_time: datetime | None = None) -> pd.DataFrame:
    current = reference_time or now_utc()
    rows = []
    for race in F1_2026_CALENDAR:
        status = "Upcoming" if race.start_utc > current.astimezone(timezone.utc) else "Completed"
        rows.append(
            {
                "Round": race.round_no,
                "Grand Prix": race.name,
                "Circuit": race.circuit,
                "Location": race.location,
                "Race Start UTC": race.start_utc.strftime("%Y-%m-%d %H:%M"),
                "Race Start Athens": race.start_local.strftime("%Y-%m-%d %H:%M"),
                "Status": status,
            }
        )
    return pd.DataFrame(rows)
