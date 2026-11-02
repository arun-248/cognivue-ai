"""
backend/clustering.py
---------------------
Exploratory K-Means behavioural grouping, reproduced from Colab Phase 16/20.

Six clustering features (target excluded) -> StandardScaler -> KMeans (K = 2).
Clustering is exploratory: it is not a diagnosis and not a validated student type.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.interventions import NEUTRAL_MIDPOINT

CLUSTER_FEATURES = [
    "independent_learning_score",
    "verification_score",
    "metacognition_score",
    "learning_benefit_score",
    "usage_frequency_encoded",
    "usage_time_encoded",
]

CONSTRUCT_FEATURES = CLUSTER_FEATURES[:4]


def assign_cluster(kmeans_model, kmeans_scaler, frame: pd.DataFrame) -> dict:
    """Assign one student row to the saved K-Means model."""
    missing = [c for c in CLUSTER_FEATURES if c not in frame.columns]
    if missing:
        raise ValueError(f"Missing clustering features: {missing}")

    X = frame[CLUSTER_FEATURES]
    if not hasattr(kmeans_scaler, "feature_names_in_"):
        X = X.to_numpy()
    scaled = kmeans_scaler.transform(X)
    cluster_id = int(kmeans_model.predict(scaled)[0])

    average = float(np.mean([float(frame.iloc[0][c]) for c in CONSTRUCT_FEATURES]))
    label = (
        "Stronger learning-strategy profile"
        if average >= NEUTRAL_MIDPOINT
        else "Developing learning-strategy profile"
    )
    return {
        "cluster_id": cluster_id,
        "construct_average": round(average, 3),
        "profile_label": label,
    }