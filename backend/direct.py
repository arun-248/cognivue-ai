"""
backend/direct.py
-----------------
The Direct Overreliance Assessment (seven statements, 1-5).

* The Direct Overreliance Score is the plain average of the seven answers.
  It is a questionnaire-derived measurement, NOT a Random Forest prediction.
* It is completely separate from the nine model features: nothing in this module
  is imported by preprocessing, prediction, SHAP or clustering.
* The same seven statements define the research training target; that is why
  they are kept out of the model inputs (target leakage).
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from backend.questionnaire import DIRECT_ITEM_IDS
from backend.validation import parse_likert

# Supportive reflection suggestions, one per statement (educational, not validated interventions).
REFLECTION_TIPS = {
    "D1": ("Starting tasks yourself",
           "You reported depending on AI to begin tasks you could attempt alone. Try a first attempt on your own, even a rough one, before asking AI."),
    "D2": ("Practising without AI",
           "You reported finding some tasks hard without AI. Choose one or two tasks each week and practise them with AI switched off."),
    "D3": ("Solving first, then comparing",
           "You reported accepting AI answers before building your own. Work out your own solution first, then compare it with the AI answer and note the differences."),
    "D4": ("Trusting your own knowledge",
           "You reported using AI even when you could solve the problem. Before asking, write down what you already know and try applying it."),
    "D5": ("Building independent confidence",
           "You reported feeling less confident without AI. Short, unaided practice sessions on topics you know can rebuild that confidence."),
    "D6": ("Explaining it in your own words",
           "You reported using AI solutions without fully understanding them. Explain the solution aloud or in writing, in your own words, before you use it."),
    "D7": ("Making your own final decision",
           "You reported finding it hard to decide independently after an AI suggestion. List the alternatives, weigh them, and make the final choice yourself."),
}
AGREE_THRESHOLD = 4  # "Agree" or "Strongly Agree" triggers a tip (a supportive heuristic, not a validated cut-off)


def direct_values(responses: Mapping) -> dict:
    """Numeric 1-5 values for D1-D7. Raises ValueError if any is missing or invalid."""
    values = {}
    for item_id in DIRECT_ITEM_IDS:
        value = responses.get(item_id)
        if value is None:
            raise ValueError(f"{item_id} is not answered")
        values[item_id] = parse_likert(value)
    return values


def direct_missing(responses: Mapping) -> list:
    return [i for i in DIRECT_ITEM_IDS if responses.get(i) is None]


def direct_score(responses: Mapping) -> float:
    """Average of the seven direct answers (1-5)."""
    return float(np.mean(list(direct_values(responses).values())))


def reflection_records(responses: Mapping) -> list:
    """Overreliance Reflection suggestions for statements answered Agree / Strongly Agree."""
    values = direct_values(responses)
    return [
        {"Item": item_id, "Title": REFLECTION_TIPS[item_id][0], "Answer": value, "Suggestion": REFLECTION_TIPS[item_id][1]}
        for item_id, value in values.items() if value >= AGREE_THRESHOLD
    ]
