"""
backend/history.py
------------------
Assessment attempts kept for comparison over time.

Attempts live in the browser session. To compare across visits, a student can
download a small JSON progress file and load it again later. The file holds only
derived questionnaire scores and a timestamp: no name, email or raw answers.
Changes reflect self-reported scores, not proven changes in ability.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

SCHEMA_VERSION = 1
MAX_ATTEMPTS = 50
MAX_FILE_BYTES = 200_000
CONSTRUCTS = ["independent_learning_score", "verification_score", "metacognition_score", "learning_benefit_score"]
LABELS = {
    "independent_learning_score": "Independent learning",
    "verification_score": "Verification",
    "metacognition_score": "Metacognition",
    "learning_benefit_score": "Learning benefits",
}


def make_snapshot(result: dict, timestamp: str | None = None) -> dict:
    """A privacy-light record of one attempt (derived scores only)."""
    ts = timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "timestamp": ts,
        "predicted_score": round(float(result["prediction"]["score"]), 4),
        "construct_scores": {f: round(float(result["construct_scores"][f]), 4) for f in CONSTRUCTS},
        "usage_frequency_code": int(result["features"]["usage_frequency_encoded"]),
        "usage_duration_code": int(result["features"]["usage_time_encoded"]),
        "cluster_id": int(result["cluster"]["cluster_id"]),
    }


def export_history(attempts: list) -> str:
    payload = {
        "app": "Cognivue AI",
        "schema_version": SCHEMA_VERSION,
        "note": "Derived self-reported questionnaire scores only. No name, email or raw answers.",
        "attempts": attempts,
    }
    return json.dumps(payload, indent=2)


def _validate_attempt(item) -> dict:
    if not isinstance(item, dict):
        raise ValueError("Each attempt must be an object.")
    try:
        ts = datetime.fromisoformat(str(item["timestamp"]))
    except Exception:
        raise ValueError("An attempt has an invalid timestamp.")
    score = item.get("predicted_score")
    if not isinstance(score, (int, float)) or isinstance(score, bool) or not (1.0 <= float(score) <= 5.0):
        raise ValueError("An attempt has a predicted score outside 1-5.")
    scores = item.get("construct_scores")
    if not isinstance(scores, dict) or set(scores) != set(CONSTRUCTS):
        raise ValueError("An attempt has missing or unexpected construct scores.")
    for key, value in scores.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not (1.0 <= float(value) <= 5.0):
            raise ValueError(f"Construct score {key} is outside 1-5.")
    freq, dur, cid = item.get("usage_frequency_code"), item.get("usage_duration_code"), item.get("cluster_id")
    for name, v, hi in (("usage_frequency_code", freq, 5), ("usage_duration_code", dur, 5), ("cluster_id", cid, 1)):
        if not isinstance(v, int) or isinstance(v, bool) or not (0 <= v <= hi):
            raise ValueError(f"{name} is invalid.")
    return {
        "timestamp": ts.isoformat(),
        "predicted_score": round(float(score), 4),
        "construct_scores": {k: round(float(scores[k]), 4) for k in CONSTRUCTS},
        "usage_frequency_code": freq, "usage_duration_code": dur, "cluster_id": cid,
    }


def import_history(text) -> list:
    """Validate an uploaded progress file. Raises ValueError with a clear message."""
    raw = text.encode("utf-8") if isinstance(text, str) else bytes(text)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("The file is too large to be a Cognivue progress file.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        raise ValueError("The file is not valid JSON.")
    if not isinstance(data, dict) or data.get("app") != "Cognivue AI":
        raise ValueError("This does not look like a Cognivue AI progress file.")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("This progress file was made by an incompatible version.")
    attempts = data.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        raise ValueError("The file contains no attempts.")
    if len(attempts) > MAX_ATTEMPTS:
        raise ValueError(f"The file contains more than {MAX_ATTEMPTS} attempts.")
    return [_validate_attempt(a) for a in attempts]


def merge_histories(current: list, imported: list) -> list:
    """Merge without duplicates (same timestamp + score), oldest first, capped at MAX_ATTEMPTS."""
    seen, merged = set(), []
    for item in list(current) + list(imported):
        key = (str(item["timestamp"]), item["predicted_score"])
        if key not in seen:
            seen.add(key)
            merged.append(item)
    merged.sort(key=lambda a: a["timestamp"])
    return merged[-MAX_ATTEMPTS:]


def compare_attempts(previous: dict, latest: dict) -> dict:
    """Differences latest - previous. Positive = a higher self-reported value."""
    return {
        "predicted_score": round(latest["predicted_score"] - previous["predicted_score"], 4),
        "construct_scores": {
            f: round(latest["construct_scores"][f] - previous["construct_scores"][f], 4) for f in CONSTRUCTS
        },
    }
