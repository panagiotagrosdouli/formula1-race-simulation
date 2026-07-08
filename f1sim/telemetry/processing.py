"""Telemetry processing helpers."""

from __future__ import annotations

import pandas as pd

from f1sim.telemetry.loaders import estimate_driver_pace, normalize_lap_times


def validate_lap_frame(frame: pd.DataFrame) -> list[str]:
    """Return validation errors for a lap-time frame."""

    required = {"driver_id", "lap", "lap_time_s"}
    missing = sorted(required.difference(frame.columns))
    errors = [f"Missing column: {column}" for column in missing]
    if "lap_time_s" in frame.columns and (frame["lap_time_s"] <= 0).any():
        errors.append("lap_time_s must be positive")
    return errors


__all__ = ["validate_lap_frame", "normalize_lap_times", "estimate_driver_pace"]
