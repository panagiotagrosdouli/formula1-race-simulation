from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = PROJECT_ROOT / "cache"
MODEL_DIR = PROJECT_ROOT / "models"

DEMO_DATA_PATH = PROCESSED_DIR / "demo_training_data.csv"
TRAINING_DATA_PATH = PROCESSED_DIR / "training_data.csv"
PREDICTIONS_PATH = PROCESSED_DIR / "predictions.csv"
SIMULATION_PATH = PROCESSED_DIR / "simulation_results.csv"
MODEL_PATH = MODEL_DIR / "race_position_model.joblib"

for path in [RAW_DIR, PROCESSED_DIR, CACHE_DIR, MODEL_DIR]:
    path.mkdir(parents=True, exist_ok=True)
