"""
backend/validation.py
---------------------
Strict validation of the 24 questionnaire answers.

Rules
* Every one of the 24 predictor answers must be present.
* No default / neutral filling: a missing answer is an error.
* Likert answers: a label ("Agree") or an integer 1-5. Booleans, floats,
  NaN and out-of-range numbers are rejected.
* Categorical answers must be one of the questionnaire options.
* Target items Q12-Q18 are rejected (leakage guard).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping

from backend.questionnaire import (
    LIKERT_ITEM_IDS,
    LIKERT_LOOKUP,
    PROFILE_KEYS,
    PROFILE_LOOKUP,
    TARGET_ITEM_IDS,
    normalize_label,
)


@dataclass
class ValidationResult:
    errors: dict = field(default_factory=dict)   # key -> message
    missing: list = field(default_factory=list)  # keys not answered

    @property
    def is_valid(self) -> bool:
        return not self.errors and not self.missing


class ValidationError(ValueError):
    """Raised when questionnaire answers are incomplete or invalid."""

    def __init__(self, result: ValidationResult):
        self.result = result
        parts = []
        if result.missing:
            parts.append(f"{len(result.missing)} unanswered: {', '.join(result.missing)}")
        if result.errors:
            parts.append("; ".join(f"{k}: {v}" for k, v in result.errors.items()))
        super().__init__(" | ".join(parts) or "Invalid responses")


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def parse_likert(value: Any) -> int:
    """Return 1-5 for a valid Likert answer, else raise ValueError."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a valid Likert answer")
    if isinstance(value, int):
        if 1 <= value <= 5:
            return value
        raise ValueError(f"{value} is outside 1-5")
    if isinstance(value, float):
        if math.isfinite(value) and value.is_integer() and 1 <= value <= 5:
            return int(value)
        raise ValueError(f"{value} is not an integer from 1 to 5")
    if isinstance(value, str):
        code = LIKERT_LOOKUP.get(normalize_label(value))
        if code is not None:
            return code
        raise ValueError(f"'{value}' is not a Likert option")
    raise ValueError(f"unsupported answer type {type(value).__name__}")


def parse_category(key: str, value: Any) -> int:
    """Return the ordinal code for a valid categorical answer."""
    if not isinstance(value, str):
        raise ValueError("answer must be one of the listed options")
    code = PROFILE_LOOKUP[key].get(normalize_label(value))
    if code is None:
        raise ValueError(f"'{value}' is not an available option")
    return code


def validate_responses(responses: Mapping[str, Any]) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(responses, Mapping):
        result.errors["responses"] = "responses must be a mapping of question id to answer"
        return result

    for key in responses:
        if key in TARGET_ITEM_IDS:
            result.errors[key] = "target item must not be supplied as a predictor (leakage)"

    for key in PROFILE_KEYS:
        value = responses.get(key)
        if _is_blank(value):
            result.missing.append(key)
            continue
        try:
            parse_category(key, value)
        except ValueError as exc:
            result.errors[key] = str(exc)

    for key in LIKERT_ITEM_IDS:
        value = responses.get(key)
        if _is_blank(value):
            result.missing.append(key)
            continue
        try:
            parse_likert(value)
        except ValueError as exc:
            result.errors[key] = str(exc)

    return result