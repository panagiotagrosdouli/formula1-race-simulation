import shap
import matplotlib.pyplot as plt

from f1predictor.data_loader import build_demo_dataset
from f1predictor.model import train_model


def run_shap_explainability():
    df = build_demo_dataset()
    model, metrics, predictions = train_model(df)

    exclude_cols = {
        "FinishPosition",
        "PredictedFinishPosition",
        "PredictedRank",
        "RaceId",
    }

    feature_cols = [
        col for col in df.columns
        if col not in exclude_cols
    ]

    X = df[feature_cols]

    # Use a smaller sample so SHAP runs fast
    X_sample = X.sample(min(80, len(X)), random_state=42)

    print("Using features:")
    for col in feature_cols:
        print(f"- {col}")

    explainer = shap.Explainer(model.predict, X_sample)
    shap_values = explainer(X_sample)

    plt.figure()
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.tight_layout()
    plt.savefig("assets/shap_summary.png", dpi=200, bbox_inches="tight")
    plt.close()

    print("\nSHAP plot saved to assets/shap_summary.png")


if __name__ == "__main__":
    run_shap_explainability()
