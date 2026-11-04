"""
backend/evaluation.py
---------------------
Optional genuine out-of-fold predictions for the 'Actual vs predicted' and
residual views. The app never creates or simulates these values: it only reads
a CSV exported from the notebook, validates it, and computes metrics from it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OOF_FILE = PROJECT_ROOT / "evaluation_predictions.csv"

NOTEBOOK_SNIPPET = '''# Run in the Colab notebook after X (the 9 features) and y (overreliance_score) exist.
# Use the SAME cross-validation split settings as in your experiments.
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_predict

rf = RandomForestRegressor(n_estimators=149, max_depth=5, max_features=1.0, max_samples=0.8,
                           min_samples_leaf=2, min_samples_split=5, random_state=42)
oof = cross_val_predict(rf, X, y, cv=KFold(n_splits=5, shuffle=True, random_state=42))
pd.DataFrame({"Actual": y.to_numpy(), "Predicted": oof}).to_csv("evaluation_predictions.csv", index=False)
# Download evaluation_predictions.csv and place it next to app.py.'''


def load_oof_predictions(path: Path = OOF_FILE):
    """Return (DataFrame or None, message). The frame has columns Actual, Predicted."""
    path = Path(path)
    if not path.exists():
        return None, "No evaluation_predictions.csv was found."
    try:
        df = pd.read_csv(path)
    except Exception:
        return None, "evaluation_predictions.csv could not be read."
    cols = {c.strip().lower(): c for c in df.columns}
    if "actual" not in cols or "predicted" not in cols:
        return None, "evaluation_predictions.csv needs the columns Actual and Predicted."
    out = pd.DataFrame({"Actual": pd.to_numeric(df[cols["actual"]], errors="coerce"),
                        "Predicted": pd.to_numeric(df[cols["predicted"]], errors="coerce")})
    if out.isna().any().any() or not np.isfinite(out.to_numpy()).all():
        return None, "evaluation_predictions.csv contains missing or non-numeric values."
    if len(out) < 20:
        return None, "evaluation_predictions.csv has too few rows to be a meaningful evaluation."
    if (out["Actual"].min() < 1 - 1e-6 or out["Actual"].max() > 5 + 1e-6
            or out["Predicted"].min() < 1 - 1e-6 or out["Predicted"].max() > 5 + 1e-6):
        return None, "evaluation_predictions.csv has values outside the 1-5 target range."
    return out.reset_index(drop=True), "ok"


def oof_metrics(df: pd.DataFrame) -> dict:
    err = df["Actual"] - df["Predicted"]
    ss_res = float((err ** 2).sum())
    ss_tot = float(((df["Actual"] - df["Actual"].mean()) ** 2).sum())
    return {
        "n": int(len(df)),
        "MAE": float(err.abs().mean()),
        "RMSE": float(np.sqrt((err ** 2).mean())),
        "R2": float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan"),
        "mean_residual": float(err.mean()),
    }
