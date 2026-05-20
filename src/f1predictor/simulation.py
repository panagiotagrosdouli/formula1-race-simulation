import numpy as np
import pandas as pd

from .config import SIMULATION_PATH


def monte_carlo_race(
    predictions: pd.DataFrame,
    n_simulations: int = 10000,
    noise_std: float = 2.0,
    reliability_std: float = 1.0,
    random_state: int = 42,
) -> pd.DataFrame:
    """Convert baseline predictions into finishing probability distributions.

    The model gives a central estimate. Simulation adds random variation to model:
    - incidents
    - strategy variance
    - pit-stop variance
    - reliability shocks
    - safety-car timing effects
    """
    rng = np.random.default_rng(random_state)

    df = predictions.copy()
    latest_gp = df["GrandPrix"].iloc[-1] if "GrandPrix" in df.columns else "Race"
    if "GrandPrix" in df.columns and df["GrandPrix"].nunique() > 1:
        df = df[df["GrandPrix"] == latest_gp].copy()

    if "PredictedFinishPosition" not in df.columns:
        raise ValueError("predictions must include PredictedFinishPosition")

    drivers = df["Driver"].to_numpy()
    base = df["PredictedFinishPosition"].to_numpy(dtype=float)
    team_strength = df.get("TeamStrength", pd.Series(0.5, index=df.index)).fillna(0.5).to_numpy(dtype=float)

    finishing_positions = {drv: [] for drv in drivers}

    for _ in range(n_simulations):
        model_noise = rng.normal(0, noise_std, size=len(df))
        reliability_shock = rng.exponential(reliability_std, size=len(df)) * (1 - np.clip(team_strength, 0, 1))
        chaos = rng.normal(0, 0.35, size=len(df))

        simulated_score = base + model_noise + reliability_shock + chaos
        order = np.argsort(simulated_score)

        for pos, idx in enumerate(order, start=1):
            finishing_positions[drivers[idx]].append(pos)

    rows = []
    for drv in drivers:
        positions = np.array(finishing_positions[drv])
        rows.append({
            "Driver": drv,
            "Team": df.loc[df["Driver"] == drv, "Team"].iloc[0] if "Team" in df else "",
            "ExpectedFinish": round(float(positions.mean()), 2),
            "MedianFinish": int(np.median(positions)),
            "WinProbability": round(float(np.mean(positions == 1)), 4),
            "PodiumProbability": round(float(np.mean(positions <= 3)), 4),
            "Top10Probability": round(float(np.mean(positions <= 10)), 4),
        })

    result = pd.DataFrame(rows).sort_values("ExpectedFinish").reset_index(drop=True)
    result.to_csv(SIMULATION_PATH, index=False)
    return result
