"""
test_features.py - tests for the report, attempt history, intervention activities and evaluation loader.

Run from the project root:   py test_features.py
Results are written to test_results.json for the Testing page.
"""

from __future__ import annotations

import json
import logging
import sys
import tempfile
from pathlib import Path

logging.disable(logging.CRITICAL)
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from backend import history as H
from backend import interventions as I
from backend.clustering import assign_cluster, cluster_profiles
from backend.evaluation import load_oof_predictions, oof_metrics
from backend.explainability import explain_prediction
from backend.model_loader import load_all_models
from backend.prediction import predict_overreliance
from backend.preprocessing import preprocess_responses
from backend.report import build_report_pdf, clean
from test_pipeline import golden_responses
from testlog import TestLog

LOG = TestLog("Features", "F")
CATEGORY = "General"


def ok(message: str) -> None:
    LOG.record(CATEGORY, message)
    print(f"  PASSED  {message}")


def section(title: str) -> None:
    global CATEGORY
    CATEGORY = title
    print("\n" + title + "\n" + "-" * len(title))


def make_result(models, answers=None):
    student = preprocess_responses(answers or golden_responses())
    pred = predict_overreliance(models["random_forest"], student.frame, models["feature_order"])
    profiles = cluster_profiles(models["kmeans_model"], models["kmeans_scaler"])
    cluster = assign_cluster(models["kmeans_model"], models["kmeans_scaler"], student.frame, profiles)
    return {
        "features": student.features, "construct_scores": student.construct_scores, "frame": student.frame,
        "prediction": pred, "cluster": cluster, "interventions": I.evaluate_interventions(student.construct_scores),
        "labels": {"usage_frequency": "Daily", "usage_duration": "31\u201360 minutes"}, "shap": None,
    }


def complete_values(feature, reflections=True):
    values = {}
    for step in I.ACTIVITIES[feature]["steps"]:
        values[I.value_key(feature, step["id"])] = True if step["kind"] == "check" else (3 if step["kind"] == "rating" else "my answer")
    if reflections:
        for r in I.ACTIVITIES[feature]["reflections"]:
            values[I.value_key(feature, r["id"])] = "my reflection"
    return values


def main():
    print("=" * 66 + "\nCOGNIVUE AI - FEATURE TESTS\n" + "=" * 66)
    models = load_all_models()
    result = make_result(models)

    # ------------------------------------------------------------------
    section("Intervention activities")
    assert set(I.ACTIVITIES) == set(I.CONSTRUCT_RULES) and len(I.ACTIVITIES) == 4
    for feature, a in I.ACTIVITIES.items():
        assert a["steps"] and len(a["reflections"]) >= 3 and a["instructions"] and a["tasks"]
        assert len({s["id"] for s in a["steps"]}) == len(a["steps"])
    ok("Four separate activities exist, each with instructions, steps, tasks and reflection questions")

    for feature in I.ACTIVITIES:
        assert I.activity_progress(feature, {})["status"] == "Not started"
        steps_only = complete_values(feature, reflections=False)
        assert I.activity_progress(feature, steps_only)["status"] == "In progress"
        assert I.activity_progress(feature, complete_values(feature))["status"] == "Completed"
    ok("Every activity moves Not started -> In progress -> Completed")

    f = "metacognition_score"
    vals = complete_values(f)
    vals[I.value_key(f, "s3")] = None
    assert not I.activity_progress(f, vals)["completed"]
    vals[I.value_key(f, "s3")] = 9
    assert not I.activity_progress(f, vals)["completed"]
    vals = complete_values("verification_score")
    vals[I.value_key("verification_score", "s3")] = False
    assert not I.activity_progress("verification_score", vals)["completed"]
    vals = complete_values("independent_learning_score")
    vals[I.value_key("independent_learning_score", "s1")] = "   "
    assert not I.activity_progress("independent_learning_score", vals)["completed"]
    ok("Blank text, an unticked check and an invalid rating do not count as done")

    recs = I.evaluate_interventions({"independent_learning_score": 2.0, "verification_score": 2.6, "metacognition_score": 3.4, "learning_benefit_score": 4.0})
    progress = I.all_progress({})
    assert I.next_recommended(recs, progress)["Feature"] == "independent_learning_score"
    progress = I.all_progress(complete_values("independent_learning_score"))
    assert I.next_recommended(recs, progress)["Feature"] == "verification_score"
    done_all = {}
    for feat in I.ACTIVITIES:
        done_all.update(complete_values(feat))
    assert I.next_recommended(recs, I.all_progress(done_all)) is None
    ok("The next recommended activity follows the weakest construct among those not yet completed")

    summary = I.intervention_summary(recs, I.all_progress(complete_values("verification_score")), complete_values("verification_score"), include_reflections=True)
    assert summary["completed"] == 1 and summary["total"] == 4 and summary["next"]["construct"].startswith("Independent")
    assert any(r["reflections"] for r in summary["rows"] if r["progress_status"] == "Completed")
    ok("The intervention summary counts completed activities and includes written reflections")

    # ------------------------------------------------------------------
    section("PDF report")
    explanation = explain_prediction(models["random_forest"], result["frame"])
    values = complete_values("metacognition_score")
    summary = I.intervention_summary(result["interventions"], I.all_progress(values), values, include_reflections=True)
    snap1 = H.make_snapshot(result, "2026-11-01T10:00:00+00:00")
    result2 = make_result(models, {**golden_responses(), "Q19": "Neutral", "Q20": "Neutral"})
    snap2 = H.make_snapshot(result2, "2026-11-02T10:00:00+00:00")
    pdf = build_report_pdf(result, explanation, result["cluster"], summary, [snap1, snap2], label="Test student", include_reflections=True, compress=False)
    assert pdf[:5] == b"%PDF-" and len(pdf) > 4000 and pdf.rstrip().endswith(b"%%EOF")
    ok("A valid multi-section PDF is generated")
    for needle in (b"2.86 out of 5", b"Student Learning Report", b"not a diagnosis", b"Test student", b"Change since the previous attempt",
                   b"my reflection", b"Exploratory K-Means group", b"midpoint"):
        assert needle in pdf, needle
    ok("The PDF contains the score, disclaimer, label, reflections, K-Means note and attempt comparison")
    for bad in (b"1-7", b"Low Reliance", b"High Reliance"):
        assert bad not in pdf
    minimal = build_report_pdf(result)
    assert minimal[:5] == b"%PDF-"
    assert clean("score \u2265 3 \u2192 \u03c1 \u2713") == "score >= 3 -> rho v"
    ok("The report works with minimal inputs and unsupported characters are made PDF-safe")

    # ------------------------------------------------------------------
    section("Attempt history")
    exported = H.export_history([snap1, snap2])
    back = H.import_history(exported)
    assert back[0]["predicted_score"] == snap1["predicted_score"] and len(back) == 2
    payload = json.loads(exported)
    allowed = {"timestamp", "predicted_score", "construct_scores", "usage_frequency_code", "usage_duration_code", "cluster_id"}
    assert all(set(a) == allowed for a in payload["attempts"]) and not any(k in payload for k in ("answers", "email", "name"))
    ok("A progress file round-trips and holds derived scores only (no raw answers or identifiers)")

    for payload, msg in [("not json", "valid JSON"), (json.dumps({"app": "Other"}), "Cognivue"),
                         (json.dumps({"app": "Cognivue AI", "schema_version": 99, "attempts": [snap1]}), "incompatible"),
                         (json.dumps({"app": "Cognivue AI", "schema_version": 1, "attempts": []}), "no attempts"),
                         ("x" * 300000, "too large")]:
        try:
            H.import_history(payload)
            raise AssertionError("should have been rejected: " + msg)
        except ValueError as exc:
            assert msg in str(exc), (msg, str(exc))
    bad = dict(snap1)
    bad["predicted_score"] = 9.0
    try:
        H.import_history(json.dumps({"app": "Cognivue AI", "schema_version": 1, "attempts": [bad]}))
        raise AssertionError("out-of-range score accepted")
    except ValueError:
        pass
    bad = dict(snap1)
    bad["construct_scores"] = {"independent_learning_score": 3}
    try:
        H.import_history(json.dumps({"app": "Cognivue AI", "schema_version": 1, "attempts": [bad]}))
        raise AssertionError("incomplete construct scores accepted")
    except ValueError:
        pass
    ok("Invalid, foreign, oversized or out-of-range progress files are rejected with clear messages")

    merged = H.merge_histories([snap1], [snap1, snap2])
    assert len(merged) == 2 and merged[0]["timestamp"] < merged[1]["timestamp"]
    delta = H.compare_attempts(snap1, snap2)
    assert abs(delta["construct_scores"]["independent_learning_score"] - (snap2["construct_scores"]["independent_learning_score"] - snap1["construct_scores"]["independent_learning_score"])) < 1e-9
    assert delta["construct_scores"]["independent_learning_score"] < 0
    ok("Histories merge without duplicates and attempt differences are computed correctly")

    # ------------------------------------------------------------------
    section("Evaluation file loader")
    tmp = Path(tempfile.mkdtemp())
    df, msg = load_oof_predictions(tmp / "missing.csv")
    assert df is None and "No evaluation" in msg
    pd.DataFrame({"Actual": [1.0] * 25, "Predicted": [9.0] * 25}).to_csv(tmp / "bad.csv", index=False)
    assert load_oof_predictions(tmp / "bad.csv")[0] is None
    pd.DataFrame({"Actual": [1.0, 2.0], "Predicted": [1.5, 2.5]}).to_csv(tmp / "short.csv", index=False)
    assert load_oof_predictions(tmp / "short.csv")[0] is None
    pd.DataFrame({"x": [1] * 30}).to_csv(tmp / "cols.csv", index=False)
    assert load_oof_predictions(tmp / "cols.csv")[0] is None
    rng = np.random.default_rng(0)
    actual = rng.uniform(1.5, 4.5, 60)
    pd.DataFrame({"actual": actual, "PREDICTED": actual * 0.8 + 0.6}).to_csv(tmp / "good.csv", index=False)
    df, msg = load_oof_predictions(tmp / "good.csv")
    assert df is not None and msg == "ok"
    m = oof_metrics(df)
    assert m["n"] == 60 and m["MAE"] > 0 and m["RMSE"] >= m["MAE"] and m["R2"] > 0.5
    ok("Missing, malformed, out-of-range or too-short evaluation files are refused; valid files yield correct metrics")

    LOG.save()
    print("\n" + "=" * 66 + f"\nALL {len(LOG.rows)} CHECKS PASSED\n" + "=" * 66)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print("\nTEST FAILED\n" + repr(error))
        raise SystemExit(1)
