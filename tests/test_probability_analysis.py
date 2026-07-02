from backend.app.application.monte_carlo import MonteCarloSummary
from backend.app.application.probability_analysis import build_probability_report


def test_probability_report_builds_win_probabilities_and_intervals():
    summary = MonteCarloSummary(
        runs=10,
        winner_counts={"LEC": 7, "HAM": 3},
        average_finish_position={"LEC": 1.3, "HAM": 1.7},
        assumptions=("test assumption",),
    )

    report = build_probability_report(summary)

    assert report.runs == 10
    assert report.drivers[0].driver_id == "LEC"
    assert report.drivers[0].win_probability == 0.7
    assert 0.0 <= report.drivers[0].win_ci_lower <= report.drivers[0].win_ci_upper <= 1.0
    assert report.assumptions
