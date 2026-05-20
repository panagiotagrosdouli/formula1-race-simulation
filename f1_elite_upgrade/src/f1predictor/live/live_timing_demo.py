"""Demo live timing stream for dashboards.

Uses synthetic values by default so it works in portfolio demos without requiring
an active race session.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_live_timing_snapshot(lap: int = 18) -> pd.DataFrame:
    drivers = ["NOR", "VER", "LEC", "HAM", "PIA", "RUS", "SAI", "ALO", "PER", "GAS"]
    rng = np.random.default_rng(lap)
    base = np.linspace(0, 28, len(drivers)) + rng.normal(0, 0.8, len(drivers))
    win_prob = np.exp(-base / 12)
    win_prob = win_prob / win_prob.sum()
    return pd.DataFrame({
        "Position": range(1, len(drivers) + 1),
        "Driver": drivers,
        "GapToLeader_s": np.round(np.maximum(base, 0), 2),
        "LastLap_s": np.round(89 + rng.normal(0, 0.7, len(drivers)) + base / 70, 3),
        "WinProbability": np.round(win_prob, 4),
    })
