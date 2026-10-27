"""Chronological forecasting model comparison.

Compares persistence, Linear Regression, Random Forest and Gradient Boosting.
Training statistics are calculated only from the training period.
"""
from pathlib import Path
import pickle
import numpy as np

from features import build_features

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

MODEL_DIR = Path(__file__).with_name("models")
MODEL_DIR.mkdir(exist_ok=True)

def evaluate_station(rows):
    f = build_features(rows)
    if len(f) < 20:
        raise ValueError("At least 20 feature rows are required.")

    split = max(1, int(len(f) * 0.8))
    train, test = f[:split], f[split:]
    X_train = np.array([z["x"] for z in train])
    y_train = np.array([z["y"] for z in train])
    X_test = np.array([z["x"] for z in test])
    y_test = np.array([z["y"] for z in test])

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=150, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    }

    results = {}
    persistence = X_test[:, 0]
    results["Persistence"] = {
        "MAE": mean_absolute_error(y_test, persistence),
        "RMSE": mean_squared_error(y_test, persistence) ** 0.5
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        results[name] = {
            "MAE": mean_absolute_error(y_test, pred),
            "RMSE": mean_squared_error(y_test, pred) ** 0.5
        }

    best_name = min(results, key=lambda name: results[name]["MAE"])
    best_model = None
    if best_name != "Persistence":
        best_model = models[best_name]
        with open(MODEL_DIR / "aqi_model.pkl", "wb") as f:
            pickle.dump({"model": best_model, "name": best_name}, f)

    return {
        "best_model": best_name,
        "results": {
            k: {"MAE": round(v["MAE"], 4), "RMSE": round(v["RMSE"], 4)}
            for k, v in results.items()
        }
    }

def predict_next(rows):
    bundle_path = MODEL_DIR / "aqi_model.pkl"
    if not bundle_path.exists():
        raise RuntimeError("Train a forecasting model first.")
    with open(bundle_path, "rb") as f:
        bundle = pickle.load(f)

    f = build_features(rows)
    if not f:
        raise ValueError("Not enough chronological readings.")
    x = np.array(f[-1]["x"]).reshape(1, -1)
    pred = float(bundle["model"].predict(x)[0])
    return max(0, min(500, pred)), bundle["name"]
