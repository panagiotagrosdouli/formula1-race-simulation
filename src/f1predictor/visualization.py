import plotly.express as px
import pandas as pd


def plot_predicted_order(predictions: pd.DataFrame):
    df = predictions.sort_values("PredictedRank")
    return px.bar(
        df,
        x="Driver",
        y="PredictedFinishPosition",
        hover_data=["Team", "GridPosition", "QualiGapToPole_s"],
        title="Predicted finishing position",
    )


def plot_probabilities(simulation_results: pd.DataFrame, probability_column: str = "PodiumProbability"):
    df = simulation_results.sort_values(probability_column, ascending=False)
    return px.bar(
        df,
        x="Driver",
        y=probability_column,
        hover_data=["Team", "ExpectedFinish", "MedianFinish"],
        title=probability_column.replace("Probability", " probability"),
    )
