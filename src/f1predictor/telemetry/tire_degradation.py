import fastf1
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

fastf1.Cache.enable_cache("cache")


def tire_deg_analysis(year=2024, gp="Monza", session_type="R", driver="VER"):

    session = fastf1.get_session(year, gp, session_type)
    session.load()

    laps = session.laps.pick_drivers(driver)

    laps = laps[
        laps["LapTime"].notna() &
        laps["TyreLife"].notna()
    ]

    df = pd.DataFrame({
        "LapNumber": laps["LapNumber"],
        "LapTime": laps["LapTime"].dt.total_seconds(),
        "TyreLife": laps["TyreLife"],
        "Compound": laps["Compound"]
    })

    # μόνο valid racing laps
    df = df[df["LapTime"] < df["LapTime"].median() + 5]

    X = df[["TyreLife"]]
    y = df["LapTime"]

    model = LinearRegression()
    model.fit(X, y)

    slope = model.coef_[0]

    predictions = model.predict(X)

    plt.figure(figsize=(10, 6))

    plt.scatter(df["TyreLife"], y, label="Actual Laps")
    plt.plot(df["TyreLife"], predictions, linewidth=3,
             label=f"Deg Rate = {slope:.3f} s/lap")

    plt.title(f"{driver} Tire Degradation - {gp} {year}")
    plt.xlabel("Tire Age (laps)")
    plt.ylabel("Lap Time (s)")
    plt.grid(True)
    plt.legend()

    plt.savefig("assets/tire_degradation.png", dpi=200)

    print("\n==========================")
    print(f"Driver: {driver}")
    print(f"Tire degradation rate: {slope:.3f} sec/lap")
    print("==========================\n")

    plt.show()


if __name__ == "__main__":
    tire_deg_analysis()
