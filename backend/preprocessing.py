"""
backend/preprocessing.py
------------------------
Reproduces the Colab preprocessing exactly:

* Likert labels -> 1..5
* Construct score = simple mean of its Likert items
* Five categorical answers -> ordinal codes
* One-row DataFrame with the nine model features in the trained order
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from backend.questionnaire import (
    CONSTRUCT_ITEMS,
    FEATURE_ORDER,
    PROFILE_QUESTIONS,
)
from backend.validation import (
    ValidationError,
    parse_category,
    parse_likert,
    validate_responses,
)


@dataclass
class ProcessedStudent:
    likert_values: dict       # {"Q19": 4, ...} numeric 1-5
    construct_scores: dict    # four construct means
    categorical_codes: dict   # five encoded categorical features
    features: dict            # the nine model features (ordered)
    frame: pd.DataFrame       # 1 x 9, columns in FEATURE_ORDER


def preprocess_responses(responses) -> ProcessedStudent:
    """Validate and convert 24 raw answers into the nine model features."""
    result = validate_responses(responses)
    if not result.is_valid:
        raise ValidationError(result)

    likert_values = {}
    for ids in CONSTRUCT_ITEMS.values():
        for item_id in ids:
            likert_values[item_id] = parse_likert(responses[item_id])

    construct_scores = {
        feature: float(np.mean([likert_values[i] for i in ids]))
        for feature, ids in CONSTRUCT_ITEMS.items()
    }

    categorical_codes = {
        q["feature"]: parse_category(q["key"], responses[q["key"]])
        for q in PROFILE_QUESTIONS
    }

    features = {**construct_scores, **categorical_codes}
    features = {name: float(features[name]) for name in FEATURE_ORDER}

    frame = pd.DataFrame([features], columns=FEATURE_ORDER)
    return ProcessedStudent(
        likert_values=likert_values,
        construct_scores=construct_scores,
        categorical_codes=categorical_codes,
        features=features,
        frame=frame,
    )