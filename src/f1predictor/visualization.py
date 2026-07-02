import pandas as pd
import plotly.express as px


FERRARI_RED = "#dc2626"
TEXT = "#f9fafb"
GRID = "rgba(255,255,255,0.08)"


def _finish_plot(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(5, 7, 13, 0)",
        plot_bgcolor="rgba(17, 24, 39, 0.92)",
        font={"color": TEXT, "family": "Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 20, "r": 20, "t": 55, "b": 35},
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    return fig


def plot_predicted_order(predictions: pd.DataFrame):
    df = predictions.sort_values("PredictedRank")
    fig = px.bar(
        df,
        x="Driver",
        y="PredictedFinishPosition",
        hover_data=[col for col in ["Team", "GridPosition", "QualiGapToPole_s"] if col in df.columns],
        title="Predicted finishing position",
        color_discrete_sequence=[FERRARI_RED],
    )
    return _finish_plot(fig)


def plot_probabilities(simulation_results: pd.DataFrame, probability_column: str = "PodiumProbability"):
    df = simulation_results.sort_values(probability_column, ascending=False)
    fig = px.bar(
        df,
        x="Driver",
        y=probability_column,
        hover_data=[col for col in ["Team", "ExpectedFinish", "MedianFinish"] if col in df.columns],
        title=probability_column.replace("Probability", " probability"),
        color_discrete_sequence=[FERRARI_RED],
    )
    return _finish_plot(fig)
