import pandas as pd


def generate_race_report(
    forecast: pd.DataFrame,
    simulation: pd.DataFrame,
    weather=None,
) -> str:

    winner = forecast.iloc[0]
    second = forecast.iloc[1]
    third = forecast.iloc[2]

    sim = simulation.set_index("Driver")

    winner_win_prob = 0.0
    winner_podium_prob = 0.0

    if winner["Driver"] in sim.index:
        winner_win_prob = float(
            sim.loc[winner["Driver"], "WinProbability"]
        )

        winner_podium_prob = float(
            sim.loc[winner["Driver"], "PodiumProbability"]
        )

    report = []

    report.append(
        f"{winner['Driver']} is projected to win the race for "
        f"{winner['Team']}."
    )

    report.append(
        f"Estimated win probability: "
        f"{winner_win_prob:.1%}."
    )

    report.append(
        f"Estimated podium probability: "
        f"{winner_podium_prob:.1%}."
    )

    report.append(
        f"The projected podium is "
        f"{winner['Driver']}, "
        f"{second['Driver']}, "
        f"{third['Driver']}."
    )

    if weather is not None:

        report.append(
            f"Weather outlook: {weather.condition}."
        )

        report.append(
            f"Rain probability: "
            f"{weather.rain_probability:.1%}."
        )

        if weather.rain_probability >= 0.35:

            report.append(
                "Wet conditions increase race uncertainty, "
                "safety-car probability and driver error risk."
            )

    return " ".join(report)
