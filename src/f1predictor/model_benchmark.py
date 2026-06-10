import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import spearmanr

try:
    from xgboost import XGBRegressor
except Exception:
    XGBRegressor = None


def evaluate_predictions(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    spearman = spearmanr(y_true, y_pred).correlation
    return {
        'MAE': round(mae, 4),
        'RMSE': round(rmse, 4),
        'Spearman': round(float(spearman), 4),
    }


def benchmark_models(X_train, X_test, y_train, y_test):
    results = []

    rf = RandomForestRegressor(n_estimators=300, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)

    rf_metrics = evaluate_predictions(y_test, rf_pred)
    rf_metrics['Model'] = 'RandomForest'
    results.append(rf_metrics)

    if XGBRegressor is not None:
        xgb = XGBRegressor(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )

        xgb.fit(X_train, y_train)
        xgb_pred = xgb.predict(X_test)

        xgb_metrics = evaluate_predictions(y_test, xgb_pred)
        xgb_metrics['Model'] = 'XGBoost'
        results.append(xgb_metrics)

    return pd.DataFrame(results)
