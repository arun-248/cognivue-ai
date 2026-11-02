"""
testlog.py - tiny helper that records test outcomes in test_results.json so the
Testing page can display genuine results. Each suite replaces only its own rows.
"""

from __future__ import annotations

import json
import platform
from datetime import datetime
from pathlib import Path

PATH = Path(__file__).resolve().parent / "test_results.json"


def _versions() -> dict:
    env = {"python": platform.python_version()}
    for name, module in (("streamlit", "streamlit"), ("scikit-learn", "sklearn"), ("shap", "shap")):
        try:
            env[name] = __import__(module).__version__
        except Exception:
            env[name] = "n/a"
    return env


class TestLog:
    def __init__(self, suite: str, prefix: str):
        self.suite, self.prefix, self.rows = suite, prefix, []

    def record(self, category: str, test: str, status: str = "Pass") -> None:
        self.rows.append({"suite": self.suite, "id": f"{self.prefix}{len(self.rows) + 1:02d}",
                          "category": category, "test": test, "status": status})

    def save(self) -> None:
        data = {"tests": []}
        if PATH.exists():
            try:
                data = json.loads(PATH.read_text(encoding="utf-8"))
            except Exception:
                data = {"tests": []}
        kept = [t for t in data.get("tests", []) if t.get("suite") != self.suite]
        data["tests"] = kept + self.rows
        data["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data["environment"] = _versions()
        PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")