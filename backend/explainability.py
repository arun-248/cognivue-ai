"""
backend/explainability.py
-------------------------
Individual SHAP explanation (TreeExplainer) for one student row.

SHAP describes the fitted model, not causes. Positive values push the
model's estimate higher; negative values push it lower.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ADDITIVITY_TOLERANCE = 1e-6

FEATURE_LABELS = {
    "independent_learning_score": "Independent learning",
    "verification_score": "Verification habits",
    "metacognition_score": "Metacognition",
    "learning_benefit_score": "Perceived learning benefits",
    "usage_frequency_encoded": "AI usage frequency",
    "usage_time_encoded": "AI usage duration",
    "age_group_encoded": "Age group",
    "study_year_encoded": "Study year",
    "experience_encoded": "Prior GenAI experience",
}


def get_explainer(random_forest):
    """Create a TreeExplainer (cache this once in the app)."""
    import shap  # imported lazily: heavy import

    return shap.TreeExplainer(random_forest)


def explain_prediction(random_forest, frame: pd.DataFrame, explainer=None) -> dict:
    """SHAP contributions plus the additivity check for one student."""
    explainer = explainer or get_explainer(random_forest)

    values = np.asarray(explainer.shap_values(frame))
    if values.ndim == 3:            # (rows, features, outputs)
        values = values[:, :, 0]
    values = values.reshape(1, -1)[0]
    if values.shape[0] != frame.shape[1]:
        raise ValueError("SHAP output size does not match the number of features.")

    baseline = float(np.ravel(explainer.expected_value)[0])
    model_output = float(random_forest.predict(frame)[0])
    reconstructed = baseline + float(values.sum())
    error = abs(reconstructed - model_output)

    table = pd.DataFrame(
        {
            "feature": list(frame.columns),
            "label": [FEATURE_LABELS.get(c, c) for c in frame.columns],
            "value": frame.iloc[0].to_numpy(dtype=float),
            "shap": values,
        }
    )
    table["abs_shap"] = table["shap"].abs()
    table["direction"] = np.where(table["shap"] >= 0, "raises estimate", "lowers estimate")
    table = table.sort_values("abs_shap", ascending=False).reset_index(drop=True)

    return {
        "baseline": baseline,
        "model_output": model_output,
        "reconstructed": reconstructed,
        "reconstruction_error": float(error),
        "verified": bool(error <= ADDITIVITY_TOLERANCE),
        "contributions": table,
    }