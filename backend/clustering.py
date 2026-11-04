"""
backend/clustering.py
---------------------
Exploratory K-Means behavioural grouping (Colab Phase 16/20).

Six clustering features (target excluded) -> StandardScaler -> KMeans (K = 2).
Everything shown about the groups is derived from the *saved* fitted objects:
the cluster centroids (inverse-transformed to the original questionnaire units),
the training cluster sizes (labels_) and the saved PCA. Clustering is
exploratory: it is not a diagnosis and not a validated student typology.
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
STRONGER = "Stronger learning-strategy profile"
DEVELOPING = "Developing learning-strategy profile"

FEATURE_NAMES = {
    "independent_learning_score": "Independent learning",
    "verification_score": "Verification",
    "metacognition_score": "Metacognition",
    "learning_benefit_score": "Learning benefits",
    "usage_frequency_encoded": "AI usage frequency (0-5)",
    "usage_time_encoded": "AI usage duration (0-5)",
}


def _prepare(frame: pd.DataFrame, scaler) -> np.ndarray:
    missing = [c for c in CLUSTER_FEATURES if c not in frame.columns]
    if missing:
        raise ValueError(f"Missing clustering features: {missing}")
    X = frame[CLUSTER_FEATURES].astype("float64")
    if not hasattr(scaler, "feature_names_in_"):
        X = X.to_numpy()
    return scaler.transform(X)


def cluster_profiles(kmeans_model, kmeans_scaler) -> list:
    """
    One record per cluster, derived from the fitted model:
    size and share (training labels), centroid in original units, and a label
    derived from the centroids themselves. With K = 2 the cluster whose four
    construct centroids have the higher mean is the 'stronger' group.
    """
    centers = kmeans_scaler.inverse_transform(kmeans_model.cluster_centers_)
    sizes = np.bincount(kmeans_model.labels_, minlength=len(centers))
    total = int(sizes.sum())
    construct_means = centers[:, :4].mean(axis=1)

    profiles = []
    for cid, row in enumerate(centers):
        profiles.append({
            "cluster_id": cid,
            "size": int(sizes[cid]),
            "percent": float(sizes[cid] / total * 100),
            "centroid": {f: float(v) for f, v in zip(CLUSTER_FEATURES, row)},
            "construct_mean": float(construct_means[cid]),
        })

    if len(profiles) == 2:
        higher = int(np.argmax(construct_means))
        for p in profiles:
            p["label"] = STRONGER if p["cluster_id"] == higher else DEVELOPING
    else:  # generic fallback, ranked by centroid construct mean
        ranks = np.argsort(-construct_means)
        for p in profiles:
            p["label"] = f"Group ranked {int(np.where(ranks == p['cluster_id'])[0][0]) + 1} of {len(profiles)} by construct centroid"

    other = {p["cluster_id"]: [q for q in profiles if q is not p][0] if len(profiles) == 2 else None for p in profiles}
    for p in profiles:
        p["description"] = _describe(p, other[p["cluster_id"]])
    return profiles


def _describe(profile: dict, other: dict | None) -> str:
    c = profile["centroid"]
    constructs = ", ".join(f"{FEATURE_NAMES[f].lower()} {c[f]:.2f}" for f in CONSTRUCT_FEATURES)
    text = f"Average construct scores in this group: {constructs} (scale 1-5)."
    if other is not None:
        diffs = [c[f] - other["centroid"][f] for f in CONSTRUCT_FEATURES]
        if all(d > 0 for d in diffs):
            text += " All four are higher than in the other group."
        elif all(d < 0 for d in diffs):
            text += " All four are lower than in the other group."
    return text


def assign_cluster(kmeans_model, kmeans_scaler, frame: pd.DataFrame, profiles: list | None = None) -> dict:
    """Assign one student row to the saved K-Means model."""
    profiles = profiles or cluster_profiles(kmeans_model, kmeans_scaler)
    scaled = _prepare(frame, kmeans_scaler)
    cluster_id = int(kmeans_model.predict(scaled)[0])
    average = float(np.mean([float(frame.iloc[0][c]) for c in CONSTRUCT_FEATURES]))
    profile = profiles[cluster_id]
    return {
        "cluster_id": cluster_id,
        "profile_label": profile["label"],          # derived from the fitted centroids
        "construct_average": round(average, 3),     # the student's own mean of the 4 constructs
        "above_midpoint": average >= NEUTRAL_MIDPOINT,
    }


def pca_projection(kmeans_model, kmeans_scaler, kmeans_pca, frame: pd.DataFrame | None = None) -> dict:
    """Project the cluster centroids (and optionally one student) into the saved 2-D PCA space."""
    centroid_coords = kmeans_pca.transform(kmeans_model.cluster_centers_)
    out = {
        "centroids": [(float(x), float(y)) for x, y in centroid_coords],
        "explained_variance": [float(v) for v in kmeans_pca.explained_variance_ratio_],
        "student": None,
    }
    if frame is not None:
        x, y = kmeans_pca.transform(_prepare(frame, kmeans_scaler))[0]
        out["student"] = (float(x), float(y))
    return out
