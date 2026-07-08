from __future__ import annotations

from pathlib import Path

import pandas as pd

from f1sim.dashboard import app as dashboard_app
from f1sim.models.pace import DriverPaceModel
from f1sim.telemetry.processing import validate_lap_frame
from f1sim.visualization.plots import plot_lap_times


def test_dashboard_module_imports() -> None:
    assert callable(dashboard_app.render_dashboard)


def test_driver_pace_model_is_seeded() -> None:
    model = DriverPaceModel(base_pace_s=90.0, seed=7)
    assert model.lap_pace_s(3) == model.lap_pace_s(3)


def test_telemetry_validation() -> None:
    frame = pd.DataFrame({"driver_id": ["A"], "lap": [1], "lap_time_s": [91.2]})
    assert validate_lap_frame(frame) == []


def test_visualization_export(tmp_path: Path) -> None:
    history = [
        {"lap": 1, "driver_id": "A", "lap_time_s": 91.2},
        {"lap": 2, "driver_id": "A", "lap_time_s": 91.0},
    ]
    output = plot_lap_times(history, tmp_path / "lap_times.png")
    assert output.exists()


def test_demo_gif_script_exists() -> None:
    assert Path("scripts/make_demo_gif.py").exists()
