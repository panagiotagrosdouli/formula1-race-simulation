import fastf1
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache("cache")


def compare_drivers(year=2024, gp="Monza", session_type="Q", driver1="VER", driver2="LEC"):
    session = fastf1.get_session(year, gp, session_type)
    session.load()

    lap1 = session.laps.pick_drivers(driver1).pick_fastest()
    lap2 = session.laps.pick_drivers(driver2).pick_fastest()

    tel1 = lap1.get_car_data().add_distance()
    tel2 = lap2.get_car_data().add_distance()

    plt.figure(figsize=(12, 6))
    plt.plot(tel1["Distance"], tel1["Speed"], label=driver1)
    plt.plot(tel2["Distance"], tel2["Speed"], label=driver2)

    plt.title(f"{driver1} vs {driver2} Speed Trace - {gp} {year}")
    plt.xlabel("Distance (m)")
    plt.ylabel("Speed (km/h)")
    plt.legend()
    plt.grid(True)

    plt.savefig("assets/telemetry_speed_comparison.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    compare_drivers()
