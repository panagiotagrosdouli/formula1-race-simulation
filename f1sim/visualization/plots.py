"""Professional engineering visualisation exports."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _ensure_parent(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def plot_lap_times(lap_history: list[dict], path: str | Path) -> Path:
    """Save a lap-time evolution plot."""

    frame = pd.DataFrame(lap_history)
    output = _ensure_parent(path)
    fig, ax = plt.subplots(figsize=(10, 5))
    for driver_id, group in frame.groupby("driver_id"):
        ax.plot(group["lap"], group["lap_time_s"], label=driver_id)
    ax.set_xlabel("Lap")
    ax.set_ylabel("Lap time [s]")
    ax.set_title("Lap-time evolution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def plot_positions(lap_history: list[dict], path: str | Path) -> Path:
    """Save a race position chart."""

    frame = pd.DataFrame(lap_history)
    output = _ensure_parent(path)
    fig, ax = plt.subplots(figsize=(10, 5))
    for driver_id, group in frame.groupby("driver_id"):
        ax.step(group["lap"], group["position"], where="post", label=driver_id)
    ax.invert_yaxis()
    ax.set_xlabel("Lap")
    ax.set_ylabel("Position")
    ax.set_title("Race position chart")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def plot_monte_carlo_distribution(times_s: list[float], path: str | Path) -> Path:
    """Save Monte Carlo finishing-time distribution."""

    output = _ensure_parent(path)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(times_s, bins=30)
    ax.set_xlabel("Race time [s]")
    ax.set_ylabel("Frequency")
    ax.set_title("Monte Carlo race-time distribution")
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output
