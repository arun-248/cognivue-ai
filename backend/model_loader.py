"""
backend/model_loader.py
-----------------------
Loads the saved Cognivue AI artifacts and verifies their integrity.
Nothing is trained here.

Models folder: <project root>/models   (override with COGNIVUE_MODELS_DIR)
Streamlit caching is applied in the ui layer, not here, so this module can also
be used from tests and scripts.
"""

from __future__ import annotations

import json
import logging
import os
import warnings
from pathlib import Path

import joblib
import numpy as np
import sklearn

logger = logging.getLogger("cognivue.model_loader")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = Path(os.environ.get("COGNIVUE_MODELS_DIR", PROJECT_ROOT / "models"))

FILES = {
    "random_forest": "Cognivue_Final_RandomForest_Model.joblib",
    "kmeans_model": "Cognivue_KMeans_Model.joblib",
    "kmeans_scaler": "Cognivue_KMeans_Scaler.joblib",
    "kmeans_pca": "Cognivue_KMeans_PCA.joblib",
}
FEATURE_ORDER_FILE = "Cognivue_Feature_Order.json"
MODEL_METADATA_FILE = "Cognivue_Model_Metadata.json"
KMEANS_METADATA_FILE = "Cognivue_KMeans_Metadata.json"


class ModelIntegrityError(RuntimeError):
    """Raised when a saved artifact is missing, unreadable or inconsistent with its metadata."""


def load_json(filename: str):
    """Read a JSON metadata file from the models folder."""
    path = MODELS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing metadata file: {path.name} (looked in {MODELS_DIR})")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _trained_sklearn_version(obj):
    try:
        return obj.__getstate__().get("_sklearn_version")
    except Exception:
        return None


def verify_models(models: dict) -> list:
    """
    Cross-check the loaded objects against their metadata files.
    Raises ModelIntegrityError on a real inconsistency and returns a list of
    human-readable confirmations on success.
    """
    checks = []
    rf = models["random_forest"]
    meta = models["model_metadata"]
    order = models["feature_order"]

    if type(rf).__name__ != meta.get("model_type", "RandomForestRegressor"):
        raise ModelIntegrityError(f"Saved model is {type(rf).__name__}, expected {meta.get('model_type')}.")
    checks.append(f"Model type is {type(rf).__name__}")

    if getattr(rf, "n_features_in_", None) != 9:
        raise ModelIntegrityError(f"Random Forest expects {getattr(rf, 'n_features_in_', None)} features, not 9.")
    if list(getattr(rf, "feature_names_in_", [])) != list(order):
        raise ModelIntegrityError("Random Forest feature names/order differ from Cognivue_Feature_Order.json.")
    if list(order) != list(meta.get("feature_order", order)):
        raise ModelIntegrityError("Feature order file differs from Cognivue_Model_Metadata.json.")
    checks.append("Nine features in the trained order")

    for name, expected in meta.get("best_hyperparameters", {}).items():
        actual = rf.get_params().get(name)
        if actual != expected:
            raise ModelIntegrityError(f"Hyperparameter {name} is {actual} in the model but {expected} in the metadata.")
    checks.append("Hyperparameters match the metadata")

    km, scaler, pca = models["kmeans_model"], models["kmeans_scaler"], models["kmeans_pca"]
    kmeta = models["kmeans_metadata"]
    if km.n_clusters != kmeta.get("selected_k", 2):
        raise ModelIntegrityError(f"K-Means has {km.n_clusters} clusters, metadata says {kmeta.get('selected_k')}.")
    if scaler.n_features_in_ != len(kmeta["features"]) or km.cluster_centers_.shape[1] != len(kmeta["features"]):
        raise ModelIntegrityError("K-Means scaler/model feature count differs from the metadata.")
    if getattr(pca, "n_features_in_", None) != len(kmeta["features"]):
        raise ModelIntegrityError("K-Means PCA feature count differs from the metadata.")
    if len(getattr(km, "labels_", [])) != kmeta.get("dataset_size"):
        raise ModelIntegrityError("K-Means training size differs from the metadata.")
    checks.append("K-Means, scaler and PCA are consistent with the metadata")
    return checks


def load_all_models(verify: bool = True) -> dict:
    """Load the Random Forest, K-Means objects, metadata and feature order."""
    models: dict = {}
    caught: list = []

    for key, filename in FILES.items():
        path = MODELS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing model file: {path.name} (looked in {MODELS_DIR})")
        try:
            with warnings.catch_warnings(record=True) as record:
                warnings.simplefilter("always")
                models[key] = joblib.load(path)
        except Exception as exc:
            raise ModelIntegrityError(f"{path.name} could not be loaded ({type(exc).__name__}).") from exc
        caught.extend(str(w.message) for w in record)

    feature_order = load_json(FEATURE_ORDER_FILE)
    if not isinstance(feature_order, list) or len(feature_order) != 9:
        raise ModelIntegrityError("Feature order file must contain a list of 9 feature names.")
    models["feature_order"] = feature_order
    models["model_metadata"] = load_json(MODEL_METADATA_FILE)
    models["kmeans_metadata"] = load_json(KMEANS_METADATA_FILE)
    models["load_warnings"] = caught

    if verify:
        models["integrity_checks"] = verify_models(models)
    if caught:
        logger.warning("Model loading produced %d warning(s): %s", len(caught), caught[0])
    logger.info("Models loaded from %s", MODELS_DIR)
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
        "integrity_checks": models.get("integrity_checks", []),
    }
