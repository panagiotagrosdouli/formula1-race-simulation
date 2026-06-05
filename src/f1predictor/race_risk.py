import pandas as pd


STREET_TRACK_KEYWORDS = [
    "Monaco",
    "Singapore",
    "Las Vegas",
    "Azerbaijan",
    "Miami",
]


HIGH_INCIDENT_TRACK_KEYWORDS = [
    "Belgian",
    "São Paulo",
    "Canadian",
    "Australian",
    "Japanese",
]


ROOKIES_2026 = {
    "ANT",
    "HAD",
    "COL",
    "LAW",
    "LIN",
    "BEA",
    "BOR",
}


RELIABILITY_RISK_TEAMS = {
    "Cadillac": 0.10,
    "Audi": 0.07,
    "Alpine": 0.06,
    "Haas": 0.05,
    "Racing Bulls": 0.05,
    "Williams": 0.04,
    "Aston Martin": 0.035,
    "Mercedes": 0.025,
    "Ferrari": 0.025,
    "McLaren": 0.02,
    "Red Bull Racing": 0.02,
}


def estimate_safety_car_probability(
    race_name: str,
    rain_probability: float = 0.0,
) -> float:
    base = 0.25

    if any(key in race_name for key in STREET_TRACK_KEYWORDS):
        base += 0.20

    if any(key in race_name for key in HIGH_INCIDENT_TRACK_KEYWORDS):
        base += 0.12

    base += 0.35 * float(rain_probability)

    return round(min(max(base, 0.05), 0.85), 3)


def estimate_driver_dnf_risk(
    row: pd.Series,
    rain_probability: float = 0.0,
    safety_car_probability: float = 0.25,
) -> float:
    driver = row.get("Driver", "")
    team = row.get("Team", "")

    risk = 0.04

    risk += RELIABILITY_RISK_TEAMS.get(team, 0.05)

    if driver in ROOKIES_2026:
        risk += 0.04

    risk += 0.10 * float(rain_probability)
    risk += 0.04 * float(safety_car_probability)

    dnf_rate = row.get("DNFRate", 0.0)
    try:
        risk += 0.10 * float(dnf_rate)
    except Exception:
        pass

    return round(min(max(risk, 0.02), 0.35), 3)


def apply_race_risk_features(
    forecast_df: pd.DataFrame,
    race_name: str,
    rain_probability: float = 0.0,
) -> pd.DataFrame:
    out = forecast_df.copy()

    safety_car_probability = estimate_safety_car_probability(
        race_name=race_name,
        rain_probability=rain_probability,
    )

    out["SafetyCarProbability"] = safety_car_probability

    out["DNFRisk"] = out.apply(
        lambda row: estimate_driver_dnf_risk(
            row,
            rain_probability=rain_probability,
            safety_car_probability=safety_car_probability,
        ),
        axis=1,
    )

    # Higher DNF risk worsens expected finishing position.
    out["RiskAdjustment"] = out["DNFRisk"] * 2.5

    if "PredictedFinishPosition" in out.columns:
        out["PredictedFinishPosition"] = (
            out["PredictedFinishPosition"] + out["RiskAdjustment"]
        )

        out = out.sort_values("PredictedFinishPosition").reset_index(drop=True)
        out["PredictedRank"] = range(1, len(out) + 1)

    return out
