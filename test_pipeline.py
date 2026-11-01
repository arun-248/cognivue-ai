"""
test_pipeline.py  -  Phase 2 integration test for Cognivue AI.

Run from the project root:
    py test_pipeline.py

Checks (no training happens):
  1. Saved models load and match the installed scikit-learn version
  2. Feature order is identical in code, JSON file and the Random Forest
  3. Encoding maps and construct item groups match the Colab metadata
  4. A verified Colab respondent (index 118) is reproduced end to end
  5. Validation rejects missing / invalid / target-leaking answers
  6. 2,000 random valid questionnaires give finite scores in 1-5
  7. SHAP additivity holds for every tested case
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from backend.explainability import explain_prediction, get_explainer
from backend.model_loader import MODELS_DIR, get_model_information, load_all_models, load_json
from backend.prediction import predict_overreliance
from backend.preprocessing import preprocess_responses
from backend.questionnaire import (
    CONSTRUCT_ITEMS,
    FEATURE_ORDER,
    LIKERT_ITEM_IDS,
    LIKERT_LABELS,
    LIKERT_SECTIONS,
    PROFILE_LOOKUP,
    PROFILE_QUESTIONS,
    REQUIRED_KEYS,
    TARGET_ITEM_IDS,
    normalize_label,
)
from backend.validation import ValidationError, validate_responses

PASSED = []


def ok(message: str) -> None:
    PASSED.append(message)
    print(f"  PASSED  {message}")


def section(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))


def golden_responses() -> dict:
    """
    Colab respondent 118. The Colab outputs fix the four construct scores
    (4.0, 4.0, 3.6, 4.0) and the five categorical codes
    (frequency 4, duration 3, age 2, year 1, experience 1). Individual item
    answers were not saved, so items are chosen to give those exact means.
    """
    answers = {
        "age_group": "18–22",
        "study_year": "First year",
        "experience": "Beginner",
        "usage_frequency": "Daily",
        "usage_duration": "31–60 minutes",
    }
    for item_id in CONSTRUCT_ITEMS["independent_learning_score"]:
        answers[item_id] = "Agree"
    for item_id in CONSTRUCT_ITEMS["verification_score"]:
        answers[item_id] = "Agree"
    for item_id, label in zip(CONSTRUCT_ITEMS["metacognition_score"],
                              ["Agree", "Agree", "Agree", "Neutral", "Neutral"]):
        answers[item_id] = label
    for item_id in CONSTRUCT_ITEMS["learning_benefit_score"]:
        answers[item_id] = "Agree"
    return answers


def random_responses(rng: random.Random) -> dict:
    answers = {q["key"]: rng.choice([label for label, _ in q["options"]]) for q in PROFILE_QUESTIONS}
    for item_id in LIKERT_ITEM_IDS:
        answers[item_id] = rng.choice(LIKERT_LABELS)
    return answers


def main() -> None:
    print("=" * 66)
    print("COGNIVUE AI - PHASE 2 PIPELINE TEST")
    print("=" * 66)

    # ------------------------------------------------------------------
    section("1. Model loading")
    models = load_all_models()
    info = get_model_information(models)
    for key, value in info.items():
        print(f"  {key}: {value}")
    assert models["random_forest"] is not None
    assert info["random_forest_trees"] == 149 and info["random_forest_max_depth"] == 5
    ok("Random Forest loaded with the documented parameters (149 trees, depth 5)")
    assert info["sklearn_versions_match"], (
        f"scikit-learn mismatch: model trained with {info['sklearn_trained_with']}, "
        f"installed {info['sklearn_installed']}. Install scikit-learn==1.6.1."
    )
    assert info["load_warnings"] == 0, models["load_warnings"]
    ok("Installed scikit-learn matches the version used for training; no load warnings")

    rf = models["random_forest"]
    feature_order = models["feature_order"]

    # ------------------------------------------------------------------
    section("2. Feature order")
    assert feature_order == FEATURE_ORDER
    assert list(rf.feature_names_in_) == FEATURE_ORDER
    assert load_json("Cognivue_Model_Metadata.json")["feature_order"] == FEATURE_ORDER
    assert rf.n_features_in_ == 9
    ok("Feature order identical in code, Feature_Order.json, model metadata and the Random Forest")

    # ------------------------------------------------------------------
    section("3. Encodings and construct items match the Colab metadata")
    meta = load_json("Cognivue_Preprocessing_Metadata.json")
    metadata_maps = {
        "age_group": meta["age_encoding"],
        "study_year": meta["study_year_encoding"],
        "experience": meta["experience_encoding"],
        "usage_frequency": meta["usage_frequency_encoding"],
        "usage_duration": meta["usage_duration_encoding"],
    }
    for key, mapping in metadata_maps.items():
        for label, code in mapping.items():
            assert PROFILE_LOOKUP[key][normalize_label(label)] == code, (key, label)
        for label, code in ((l, c) for l, c in
                            next(q for q in PROFILE_QUESTIONS if q["key"] == key)["options"]):
            assert mapping[normalize_label(label)] == code, (key, label)
    ok("All five categorical encodings are identical to the Colab mappings")

    assert [LIKERT_LABELS.index(l) + 1 for l in LIKERT_LABELS] == [1, 2, 3, 4, 5]
    ok("Likert encoding is 1-5 (Strongly Disagree ... Strongly Agree)")

    # likert_item_NN in Colab = the (NN)th Likert column, Q12..Q39 in form order
    colab_position = {
        "Q19": 8, "Q20": 9, "Q22a": 10, "Q22b": 11, "Q23": 12,
        "Q24": 13, "Q25": 14, "Q26": 15, "Q27": 16, "Q28": 17,
        "Q29": 18, "Q30": 19, "Q31": 20, "Q32": 21, "Q33": 22,
        "Q34": 23, "Q35": 24, "Q37": 26, "Q39": 28,
    }
    for feature, ids in CONSTRUCT_ITEMS.items():
        ours = sorted(colab_position[i] for i in ids)
        theirs = sorted(int(n.split("_")[-1]) for n in meta["construct_items"][feature])
        assert ours == theirs, feature
    ok("Construct item groups match Cognivue_Preprocessing_Metadata.json")

    assert len(PROFILE_QUESTIONS) == 5 and len(LIKERT_ITEM_IDS) == 19 and len(REQUIRED_KEYS) == 24
    assert not set(TARGET_ITEM_IDS) & set(REQUIRED_KEYS)
    assert not {"Q36", "Q38"} & set(REQUIRED_KEYS)
    ok("24 predictors collected (5 categorical + 19 Likert); Q12-Q18, Q36, Q38 excluded")

    # ------------------------------------------------------------------
    section("4. Colab respondent 118 reproduced end to end")
    student = preprocess_responses(golden_responses())
    expected_features = [4.0, 4.0, 3.6, 4.0, 4.0, 3.0, 2.0, 1.0, 1.0]
    assert list(student.frame.columns) == FEATURE_ORDER
    assert np.allclose(student.frame.iloc[0].to_numpy(), expected_features)
    ok("Nine model features equal the Colab values, in the trained order")

    sample = load_json("Cognivue_Sample_Student_Intervention.json")
    prediction = predict_overreliance(rf, student.frame, feature_order)
    assert abs(round(prediction["raw_prediction"], 4) - sample["raw_model_prediction"]) < 1e-4
    assert abs(round(prediction["score"], 4) - sample["predicted_overreliance_score"]) < 1e-4
    ok(f"Prediction {prediction['score']:.4f} equals Colab {sample['predicted_overreliance_score']}")

    explanation = explain_prediction(rf, student.frame, get_explainer(rf))
    assert abs(round(explanation["baseline"], 4) - sample["shap_base_value"]) < 1e-4
    top3 = explanation["contributions"].head(3)
    for row, ref in zip(top3.itertuples(), sample["top_contributing_features"]):
        assert row.feature == ref["Feature"], (row.feature, ref["Feature"])
        assert abs(row.shap - ref["SHAP_Contribution"]) < 1e-8
    ok("SHAP baseline and top-3 contributions equal the Colab sample report")
    assert explanation["verified"] and explanation["reconstruction_error"] < 1e-9
    ok(f"SHAP additivity verified (error {explanation['reconstruction_error']:.2e})")

    # ------------------------------------------------------------------
    section("5. Input validation")
    base = golden_responses()

    for key in REQUIRED_KEYS:
        broken = {k: v for k, v in base.items() if k != key}
        result = validate_responses(broken)
        assert not result.is_valid and key in result.missing, key
    ok("Each of the 24 answers is individually required (no default values)")

    for bad in (None, "", "   ", float("nan")):
        assert not validate_responses({**base, "Q19": bad}).is_valid
    ok("None, empty text and NaN are rejected")

    for bad in ("Maybe", 0, 6, 3.5, True, "5.0", ["Agree"]):
        assert not validate_responses({**base, "Q24": bad}).is_valid, bad
    ok("Invalid Likert answers are rejected (unknown label, 0, 6, 3.5, boolean, list)")

    assert validate_responses({**base, "Q24": 4}).is_valid
    assert validate_responses({**base, "Q24": "strongly agree"}).is_valid
    ok("Integer 1-5 and case-insensitive labels are accepted")

    for key, bad in (("age_group", "Prefer not to say"), ("study_year", "Sixth year"),
                     ("experience", "Expert"), ("usage_frequency", "Hourly"),
                     ("usage_duration", "3 hours")):
        assert not validate_responses({**base, key: bad}).is_valid, key
    ok("Unavailable categorical options are rejected")

    for target in TARGET_ITEM_IDS:
        assert not validate_responses({**base, target: "Agree"}).is_valid, target
    ok("Target items Q12-Q18 are rejected as predictors (leakage guard)")

    try:
        preprocess_responses({})
        raise AssertionError("empty input should fail")
    except ValidationError:
        ok("Empty submission raises ValidationError")

    # ------------------------------------------------------------------
    section("6. Randomised and extreme inputs")
    rng = random.Random(2026)
    explainer = get_explainer(rf)
    scores = []
    for _ in range(2000):
        s = preprocess_responses(random_responses(rng))
        p = predict_overreliance(rf, s.frame, feature_order)
        assert np.isfinite(p["raw_prediction"]) and 1.0 <= p["score"] <= 5.0
        scores.append(p["score"])
    ok(f"2,000 random questionnaires: finite scores in 1-5 (range {min(scores):.3f}-{max(scores):.3f})")

    for _ in range(100):
        s = preprocess_responses(random_responses(rng))
        e = explain_prediction(rf, s.frame, explainer)
        assert e["verified"], e["reconstruction_error"]
    ok("SHAP additivity verified on 100 random students")

    lowest = {q["key"]: q["options"][0][0] for q in PROFILE_QUESTIONS}
    highest = {q["key"]: q["options"][-1][0] for q in PROFILE_QUESTIONS}
    for item_id in LIKERT_ITEM_IDS:
        lowest[item_id], highest[item_id] = "Strongly Disagree", "Strongly Agree"
    for answers in (lowest, highest):
        s = preprocess_responses(answers)
        p = predict_overreliance(rf, s.frame, feature_order)
        assert np.isfinite(p["score"]) and 1.0 <= p["score"] <= 5.0
    ok("Extreme all-minimum and all-maximum questionnaires give valid scores")

    again = predict_overreliance(rf, preprocess_responses(golden_responses()).frame, feature_order)
    assert again["raw_prediction"] == prediction["raw_prediction"]
    ok("Predictions are deterministic")

    # ------------------------------------------------------------------
    section("7. Wording check")
    wording = {item["id"]: item["text"] for sec in LIKERT_SECTIONS for item in sec["items"]}
    assert wording["Q22a"].startswith("I can complete familiar")
    assert wording["Q22b"].startswith("I attempt to solve a problem again")
    assert len(wording) == 19 and all(t.endswith(".") for t in wording.values())
    ok("19 Likert statements present; two Q22 items kept separate")

    print("\n" + "=" * 66)
    print(f"ALL {len(PASSED)} CHECKS PASSED")
    print("=" * 66)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print("\nTEST FAILED")
        print("-" * 66)
        print(error)
        raise SystemExit(1)