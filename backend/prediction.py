"""
backend/prediction.py
---------------------
Runs the saved RandomForestRegressor on one preprocessed student row.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

TARGET_MIN = 1.0
TARGET_MAX = 5.0


def predict_overreliance(random_forest, frame: pd.DataFrame, feature_order: list) -> dict:
    """Return the estimated overreliance score for a 1 x 9 feature frame."""
    if list(frame.columns) != list(feature_order):
        raise ValueError(
            "Feature columns do not match the trained feature order.\n"
            f"Got:      {list(frame.columns)}\nExpected: {list(feature_order)}"
        )
    if len(frame) != 1:
        raise ValueError("Exactly one student row is expected.")

    row = frame[feature_order].astype("float64")
    if not np.isfinite(row.to_numpy()).all():
        raise ValueError("The feature row contains missing or non-finite values.")

    raw = float(random_forest.predict(row)[0])
    if not math.isfinite(raw):
        raise ValueError("Model produced a non-finite prediction.")

    # Same 1-5 clipping the Colab prediction function applied.
    score = min(max(raw, TARGET_MIN), TARGET_MAX)
    return {
        "raw_prediction": raw,
        "score": score,
        "was_clipped": score != raw,
        "scale_min": TARGET_MIN,
        "scale_max": TARGET_MAX,
    }
