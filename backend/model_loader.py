"""
backend/model_loader.py
-----------------------
Loads the saved Cognivue AI artifacts. Nothing is trained here.

Models folder: <project root>/models   (override with COGNIVUE_MODELS_DIR)
Streamlit caching is applied in app.py, not here, so this module can also be
used from tests and scripts.
"""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import joblib
import sklearn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = Path(os.environ.get("COGNIVUE_MODELS_DIR", PROJECT_ROOT / "models"))

FILES = {
    "random_forest": "Cognivue_Final_RandomForest_Model.joblib",
    "kmeans_model": "Cognivue_KMeans_Model.joblib",
    "kmeans_scaler": "Cognivue_KMeans_Scaler.joblib",
    "kmeans_pca": "Cognivue_KMeans_PCA.joblib",
}
FEATURE_ORDER_FILE = "Cognivue_Feature_Order.json"


def load_json(filename: str):
    """Read a JSON metadata file from the models folder."""
    path = MODELS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing metadata file: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _trained_sklearn_version(obj):
    try:
        return obj.__getstate__().get("_sklearn_version")
    except Exception:
        return None


def load_all_models() -> dict:
    """Load the Random Forest, K-Means objects and feature order."""
    models: dict = {}
    caught: list = []

    for key, filename in FILES.items():
        path = MODELS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing model file: {path}")
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            models[key] = joblib.load(path)
        caught.extend(str(w.message) for w in record)

    feature_order = load_json(FEATURE_ORDER_FILE)
    if not isinstance(feature_order, list) or len(feature_order) != 9:
        raise ValueError("Feature order file must contain a list of 9 feature names.")
    models["feature_order"] = feature_order
    models["load_warnings"] = caught
    return models


def get_model_information(models: dict) -> dict:
    """Summary used by tests and the About / Model pages."""
    rf = models["random_forest"]
    trained_with = _trained_sklearn_version(rf)
    return {
        "models_directory": str(MODELS_DIR),
        "random_forest_type": type(rf).__name__,
        "random_forest_trees": getattr(rf, "n_estimators", None),
        "random_forest_max_depth": getattr(rf, "max_depth", None),
        "random_forest_features": getattr(rf, "n_features_in_", None),
        "kmeans_clusters": getattr(models["kmeans_model"], "n_clusters", None),
        "feature_order": models["feature_order"],
        "sklearn_trained_with": trained_with,
        "sklearn_installed": sklearn.__version__,
        "sklearn_versions_match": trained_with == sklearn.__version__,
        "load_warnings": len(models.get("load_warnings", [])),
    }