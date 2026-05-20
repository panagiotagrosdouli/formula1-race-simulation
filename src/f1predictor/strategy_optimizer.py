import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

TOTAL_LAPS = 53

# tire models
compounds = {
    "SOFT": {
        "base": 88.5,
        "deg": 0.085,
        "max_life": 18
    },
    "MEDIUM": {
        "base": 89.3,
        "deg": 0.055,
        "max_life": 28
    },
    "HARD": {
        "base": 90.2,
        "deg": 0.035,
        "max_life": 40
    }
}

PIT_LOSS = 22.5


def simulate_stint(compound, laps):

    tire = compounds[compound]

    lap_times = []

    for lap in range(laps):

        degradation = tire["deg"] * lap

        # tire cliff
        if lap > tire["max_life"]:
            degradation += 0.25 * (lap - tire["max_life"])

        lap_time = tire["base"] + degradation

        lap_times.append(lap_time)

    return np.array(lap_times)


def simulate_strategy(strategy):

    total_time = 0
    all_laps = []

    for compound, laps in strategy:

        stint = simulate_stint(compound, laps)

        total_time += stint.sum()

        all_laps.extend(stint)

    pitstops = len(strategy) - 1

    total_time += pitstops * PIT_LOSS

    return total_time, np.array(all_laps)


strategies = {
    "S-M": [("SOFT", 16), ("MEDIUM", 37)],
    "M-H": [("MEDIUM", 25), ("HARD", 28)],
    "S-H": [("SOFT", 14), ("HARD", 39)],
    "M-M": [("MEDIUM", 26), ("MEDIUM", 27)],
    "S-M-M": [("SOFT", 12), ("MEDIUM", 20), ("MEDIUM", 21)]
}

results = []

for name, strat in strategies.items():

    total, laps = simulate_strategy(strat)

    results.append({
        "Strategy": name,
        "TotalRaceTime": total
    })

    plt.plot(laps, label=name)

results_df = pd.DataFrame(results)
results_df = results_df.sort_values("TotalRaceTime")

print("\n=== STRATEGY RESULTS ===")
print(results_df)

best = results_df.iloc[0]

print(f"\nBest strategy: {best['Strategy']}")
print(f"Predicted race time: {best['TotalRaceTime']:.2f}s")

plt.figure(figsize=(12, 6))

for name, strat in strategies.items():

    _, laps = simulate_strategy(strat)

    plt.plot(laps, label=name)

plt.title("Race Strategy Simulation")
plt.xlabel("Lap")
plt.ylabel("Lap Time (s)")
plt.legend()
plt.grid(True)

plt.savefig("assets/strategy_simulation.png", dpi=200)

plt.show()
