"""Generate demo GIF/MP4 from a simulated race.

The animation is generated entirely from simulation output. It is not manually edited.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import pandas as pd

from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation


def make_demo(config_path: str = "configs/experiments/dry_race.yml") -> None:
    """Create assets/demo.gif and results/videos/demo.mp4."""

    config = load_race_config(config_path)
    result = RaceSimulation(config).run()
    frame = pd.DataFrame(result.lap_history)
    Path("assets").mkdir(exist_ok=True)
    Path("results/videos").mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    drivers = list(frame["driver_id"].unique())

    def update(lap: int):
        ax.clear()
        lap_frame = frame[frame["lap"] == lap].sort_values("position")
        labels = [f"{row.driver_id} | P{int(row.position)} | {row.compound}" for row in lap_frame.itertuples()]
        ax.barh(labels, lap_frame["gap_to_leader_s"])
        ax.invert_yaxis()
        sc = bool(lap_frame["safety_car"].any()) if not lap_frame.empty else False
        vsc = bool(lap_frame["vsc"].any()) if not lap_frame.empty else False
        wetness = float(lap_frame["wetness"].mean()) if not lap_frame.empty else 0.0
        ax.set_title(f"Lap {lap}/{config.laps} | wetness={wetness:.2f} | SC={sc} | VSC={vsc}")
        ax.set_xlabel("Gap to leader [s]")
        ax.set_xlim(0, max(5.0, frame["gap_to_leader_s"].max() + 2.0))
        ax.text(0.02, 0.02, "Pit stops, tyres, weather and race outcome from f1sim code", transform=ax.transAxes)
        return ax

    anim = animation.FuncAnimation(fig, update, frames=range(1, config.laps + 1), interval=180)
    anim.save("assets/demo.gif", writer="pillow", fps=5)
    try:
        anim.save("results/videos/demo.mp4", writer="ffmpeg", fps=5)
    except Exception:
        Path("results/videos/demo.mp4.placeholder").write_text(
            "MP4 export requires ffmpeg; GIF was generated from code.\n", encoding="utf-8"
        )
    plt.close(fig)


if __name__ == "__main__":
    make_demo()
