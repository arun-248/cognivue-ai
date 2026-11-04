"""
backend/interventions.py
------------------------
Rule-based adaptive interventions, reproduced from the Colab Phase 20 engine.

Rule: a construct score below the neutral Likert midpoint (3.0) receives a
targeted support recommendation; otherwise a maintenance recommendation.
The midpoint is a heuristic design choice, not a validated cut-off.
"""

from __future__ import annotations

NEUTRAL_MIDPOINT = 3.0

# Recommendation texts are copied from the Colab notebook.
CONSTRUCT_RULES = {
    "independent_learning_score": {
        "name": "Independent Learning",
        "priority": "Independent problem-solving",
        "below_midpoint": (
            "Attempt assignments and problems independently before consulting Generative AI. "
            "Write down an initial solution and compare it with AI suggestions."
        ),
        "maintenance": (
            "Continue attempting problems independently before using AI. "
            "Maintain regular unaided practice."
        ),
    },
    "verification_score": {
        "name": "Verification and Critical Thinking",
        "priority": "AI answer verification",
        "below_midpoint": (
            "Verify AI-generated answers using textbooks, reliable academic sources or independent "
            "calculations. Identify unsupported claims before accepting an answer."
        ),
        "maintenance": (
            "Continue checking AI-generated information against independent sources and testing "
            "important claims."
        ),
    },
    "metacognition_score": {
        "name": "Metacognition",
        "priority": "Self-monitoring and reflection",
        "below_midpoint": (
            "After each study session, record what you understood, what remains unclear and which "
            "concepts require revision. Try a short self-test without AI assistance."
        ),
        "maintenance": (
            "Continue reflecting on your learning progress and testing your understanding without "
            "relying on AI."
        ),
    },
    "learning_benefit_score": {
        "name": "Learning Benefits",
        "priority": "Active learning",
        "below_midpoint": (
            "Use AI as a learning assistant rather than an answer replacement. Apply concepts "
            "through exercises, projects and practical problem-solving."
        ),
        "maintenance": (
            "Continue using AI to clarify concepts and support practical learning while completing "
            "exercises yourself."
        ),
    },
}


def evaluate_interventions(construct_scores: dict) -> list:
    """One record per construct, in the same shape as the Colab sample report."""
    records = []
    for feature, rule in CONSTRUCT_RULES.items():
        score = float(construct_scores[feature])
        if score < NEUTRAL_MIDPOINT:
            status, priority, text = "Support recommended", "Focus area", rule["below_midpoint"]
        else:
            status, priority, text = "Maintain current practice", "Maintenance", rule["maintenance"]
        records.append(
            {
                "Construct": rule["name"],
                "Feature": feature,
                "Observed_Score": round(score, 3),
                "Reference_Midpoint": NEUTRAL_MIDPOINT,
                "Status": status,
                "Priority": priority,
                "Intervention": text,
            }
        )
    return records


def recommended_focus(records: list) -> dict:
    """Lowest-scoring flagged construct; if none is flagged, the lowest-scoring one (maintenance)."""
    flagged = [r for r in records if r["Priority"] == "Focus area"]
    pool = flagged or records
    return min(pool, key=lambda r: r["Observed_Score"])


# ----------------------------------------------------------------------
# Interactive activities (prototype learning tasks; effectiveness NOT validated)
#
# Each activity has ordered steps. A step is one of:
#   "text"   - the student writes something (counts as done when non-empty)
#   "check"  - the student confirms they did something (checkbox)
#   "rating" - the student picks 1-5 on a short self-assessment
# plus reflection questions (free text). An activity is complete when every
# step is done and every reflection is answered.
# ----------------------------------------------------------------------
ACTIVITIES = {
    "independent_learning_score": {
        "title": "Independent Problem-Solving Practice",
        "construct": "Independent Learning",
        "minutes": "15\u201325",
        "skills": ["Independent reasoning", "Persistence", "Self-explanation"],
        "why": (
            "Your Independent Learning score suggests there may be room to attempt problems yourself "
            "before turning to Generative AI. This activity practises forming your own first solution."
        ),
        "why_maintain": (
            "Your Independent Learning score is at or above the midpoint. This activity helps you keep "
            "attempting problems yourself before consulting AI."
        ),
        "instructions": (
            "Choose one task below. Work through the steps in order: your own attempt comes first, AI is used only for "
            "hints, and you finish by solving the problem again without AI."
        ),
        "tasks": [
            "Pick one problem from your current coursework that you would normally give straight to an AI tool.",
            "Choose a concept from this week's classes and prepare to explain it to a friend.",
            "Take a past assignment question and work out a full solution.",
        ],
        "steps": [
            {"id": "s1", "kind": "text", "text": "Attempt the task independently and write down your initial reasoning.",
             "label": "Your initial attempt and reasoning"},
            {"id": "s2", "kind": "check", "text": "I asked an AI tool for hints only (not the full answer) on the part where I got stuck."},
            {"id": "s3", "kind": "text", "text": "Compare the AI explanation with your original attempt.",
             "label": "What matches, and what differs from your attempt?"},
            {"id": "s4", "kind": "text", "text": "Solve the problem again without AI.",
             "label": "Your second solution, written without AI"},
        ],
        "reflections": [
            {"id": "r1", "question": "Which step of your first attempt was hardest, and why?"},
            {"id": "r2", "question": "How did your second solution differ from your first?"},
            {"id": "r3", "question": "What will you try on your own before using AI next time?"},
        ],
    },
    "verification_score": {
        "title": "Verify an AI Answer",
        "construct": "Verification and Critical Thinking",
        "minutes": "15\u201325",
        "skills": ["Verification", "Critical thinking", "Source evaluation"],
        "why": (
            "Your Verification score suggests there may be room to check AI-generated information more "
            "often. This activity practises testing an AI answer against reliable sources."
        ),
        "why_maintain": (
            "Your Verification score is at or above the midpoint. This activity keeps the habit of "
            "checking important AI claims."
        ),
        "instructions": (
            "Ask an AI tool a question on a topic you are studying, then examine its answer critically: look for errors, "
            "check claims against reliable sources, and record what you corrected."
        ),
        "tasks": [
            "Ask an AI tool to explain a concept from your course.",
            "Ask an AI tool to solve a short calculation or code problem.",
            "Ask an AI tool for a short summary of a topic you already know well.",
        ],
        "steps": [
            {"id": "s1", "kind": "text", "text": "Examine the AI-generated answer and note what it claims.",
             "label": "Summarise the AI answer in a few lines"},
            {"id": "s2", "kind": "text", "text": "Identify possible errors, unsupported claims or missing steps.",
             "label": "Possible errors or unsupported claims"},
            {"id": "s3", "kind": "check", "text": "I cross-checked at least two claims against reliable sources (textbook, official documentation or a paper)."},
            {"id": "s4", "kind": "text", "text": "Record the corrections and the source that supports each one.",
             "label": "Corrections and sources"},
        ],
        "reflections": [
            {"id": "r1", "question": "Which claim was hardest to verify, and why?"},
            {"id": "r2", "question": "Did the AI answer contain anything you would have accepted without checking?"},
            {"id": "r3", "question": "What checking habit will you use the next time you rely on an AI answer?"},
        ],
    },
    "metacognition_score": {
        "title": "Reflect and Self-Test",
        "construct": "Metacognition",
        "minutes": "15\u201320",
        "skills": ["Metacognition", "Self-assessment", "Retrieval practice"],
        "why": (
            "Your Metacognition score suggests there may be room to monitor your own understanding more "
            "closely. This activity practises checking what you actually understand without AI."
        ),
        "why_maintain": (
            "Your Metacognition score is at or above the midpoint. This activity keeps the habit of "
            "testing your own understanding."
        ),
        "instructions": (
            "Pick a topic you studied recently. Answer from memory first, explain it in your own words, rate your "
            "confidence, and name what you still do not understand."
        ),
        "tasks": [
            "Choose the last topic you studied with AI help.",
            "Choose a concept from this week's classes that you think you understand.",
            "Choose a topic you expect to be tested on soon.",
        ],
        "steps": [
            {"id": "s1", "kind": "text", "text": "Attempt a question on the topic without AI.",
             "label": "Your answer, written from memory"},
            {"id": "s2", "kind": "text", "text": "Explain the concept in your own words.",
             "label": "Your own-words explanation"},
            {"id": "s3", "kind": "rating", "text": "Short self-assessment: how confident are you that you understand this topic? (1 = not at all, 5 = completely)"},
            {"id": "s4", "kind": "text", "text": "Identify the knowledge gaps that remain.",
             "label": "What you still do not understand, and how you will close the gap"},
        ],
        "reflections": [
            {"id": "r1", "question": "How did your confidence compare with how much you could actually recall?"},
            {"id": "r2", "question": "Which part of your explanation felt weakest?"},
            {"id": "r3", "question": "How will you check your understanding next week without AI?"},
        ],
    },
    "learning_benefit_score": {
        "title": "Use AI as a Learning Assistant",
        "construct": "Learning Benefits",
        "minutes": "15\u201325",
        "skills": ["Active learning", "Applying concepts", "Responsible AI use"],
        "why": (
            "Your Learning Benefits score suggests AI may not yet be supporting your learning as much as "
            "it could. This activity practises using AI to clarify, while you do the applying."
        ),
        "why_maintain": (
            "Your Learning Benefits score is at or above the midpoint. This activity keeps AI in a "
            "supporting role while you do the practice."
        ),
        "instructions": (
            "Use AI to clarify one difficult concept, then close the chat and apply the concept to a new problem and "
            "explain it independently."
        ),
        "tasks": [
            "Choose a concept you find difficult.",
            "Choose a topic where you are stuck on a problem.",
            "Choose a topic you want to be able to explain from memory.",
        ],
        "steps": [
            {"id": "s1", "kind": "check", "text": "I used AI to clarify the concept (asking for explanation or hints, not the final answer)."},
            {"id": "s2", "kind": "text", "text": "Apply the concept to a new problem.",
             "label": "Your attempt at a new problem using the concept"},
            {"id": "s3", "kind": "text", "text": "Explain the concept independently, without looking at the AI chat.",
             "label": "Your independent explanation"},
        ],
        "reflections": [
            {"id": "r1", "question": "What did AI help you understand that you could not work out alone?"},
            {"id": "r2", "question": "What part did you have to do yourself for the understanding to stick?"},
            {"id": "r3", "question": "How will you use AI to clarify rather than replace your thinking next time?"},
        ],
    },
}

SELF_RATING_OPTIONS = [1, 2, 3, 4, 5]


def value_key(feature: str, item_id: str) -> str:
    """Session key for a step or reflection value."""
    return f"iv_{feature}_{item_id}"


def step_done(step: dict, value) -> bool:
    kind = step["kind"]
    if kind == "check":
        return value is True
    if kind == "rating":
        return isinstance(value, int) and not isinstance(value, bool) and value in SELF_RATING_OPTIONS
    return isinstance(value, str) and value.strip() != ""


def activity_progress(feature: str, values: dict) -> dict:
    """
    Progress of one activity. `values` maps value_key(...) -> student input.
    Completion needs every step done and every reflection answered.
    """
    activity = ACTIVITIES[feature]
    steps_done = [s["id"] for s in activity["steps"] if step_done(s, values.get(value_key(feature, s["id"])))]
    refl_done = [r["id"] for r in activity["reflections"]
                 if isinstance(values.get(value_key(feature, r["id"])), str) and values[value_key(feature, r["id"])].strip()]
    total = len(activity["steps"]) + len(activity["reflections"])
    done = len(steps_done) + len(refl_done)
    if done == 0:
        status = "Not started"
    elif done == total:
        status = "Completed"
    else:
        status = "In progress"
    return {
        "feature": feature,
        "title": activity["title"],
        "construct": activity["construct"],
        "steps_done": len(steps_done), "steps_total": len(activity["steps"]),
        "reflections_done": len(refl_done), "reflections_total": len(activity["reflections"]),
        "done": done, "total": total, "percent": done / total * 100,
        "status": status, "completed": status == "Completed",
        "pending_steps": [s["id"] for s in activity["steps"] if s["id"] not in steps_done],
        "pending_reflections": [r["id"] for r in activity["reflections"] if r["id"] not in refl_done],
    }


def all_progress(values: dict) -> dict:
    return {feature: activity_progress(feature, values) for feature in ACTIVITIES}


def next_recommended(records: list, progress: dict):
    """
    The next activity to do: among activities that are not completed, the one for the
    lowest-scoring construct. None when every activity is completed.
    """
    pending = [r for r in records if not progress[r["Feature"]]["completed"]]
    if not pending:
        return None
    return min(pending, key=lambda r: r["Observed_Score"])


def intervention_summary(records: list, progress: dict, values: dict, include_reflections: bool = False) -> dict:
    """Completed / pending overview used by the page and the PDF report."""
    rows = []
    for record in records:
        p = progress[record["Feature"]]
        entry = {
            "construct": record["Construct"], "score": record["Observed_Score"],
            "status": record["Status"], "activity": p["title"],
            "progress_status": p["status"], "percent": p["percent"],
        }
        if include_reflections:
            activity = ACTIVITIES[record["Feature"]]
            entry["reflections"] = [
                (r["question"], str(values.get(value_key(record["Feature"], r["id"]), "")).strip())
                for r in activity["reflections"]
                if str(values.get(value_key(record["Feature"], r["id"]), "")).strip()
            ]
        rows.append(entry)
    completed = [r for r in rows if r["progress_status"] == "Completed"]
    nxt = next_recommended(records, progress)
    return {
        "rows": rows,
        "completed": len(completed),
        "total": len(rows),
        "next": None if nxt is None else {"construct": nxt["Construct"], "activity": ACTIVITIES[nxt["Feature"]]["title"]},
    }
