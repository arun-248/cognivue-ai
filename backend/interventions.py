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
# Interactive activities (prototype learning tasks; effectiveness not validated)
# ----------------------------------------------------------------------
ACTIVITIES = {
    "independent_learning_score": {
        "title": "Independent Problem-Solving Practice",
        "skills": ["Independent reasoning", "Persistence", "Self-explanation"],
        "why": (
            "Your Independent Learning score suggests there may be room to attempt problems yourself "
            "before turning to Generative AI. This activity practises forming your own first solution."
        ),
        "why_maintain": (
            "Your Independent Learning score is at or above the midpoint. This activity helps you keep "
            "attempting problems yourself before consulting AI."
        ),
        "tasks": [
            "Pick one problem from your current coursework that you would normally give straight to an AI tool. Solve it on your own for five minutes, writing each step you try.",
            "Choose a concept from this week's classes and explain it in your own words, as if teaching a friend, without looking anything up.",
            "Take a past assignment question and write the first three steps of a solution before opening any AI tool.",
        ],
        "compare_hint": "Now ask an AI tool, or open your textbook or lecture notes, for the same problem and compare it with your attempt.",
    },
    "verification_score": {
        "title": "Verify an AI Answer",
        "skills": ["Verification", "Critical thinking", "Source evaluation"],
        "why": (
            "Your Verification score suggests there may be room to check AI-generated information more "
            "often. This activity practises testing an AI answer against reliable sources."
        ),
        "why_maintain": (
            "Your Verification score is at or above the midpoint. This activity keeps the habit of "
            "checking important AI claims."
        ),
        "tasks": [
            "Ask an AI tool to explain a concept from your course. Pick one factual claim in the answer and find two reliable sources (textbook, official documentation or a paper) that cover it.",
            "Ask an AI tool to solve a short calculation or code problem, then verify each step yourself and mark any step you could not confirm.",
            "Ask an AI tool for a short summary of a topic you know well and list any statement that is unsupported, imprecise or wrong.",
        ],
        "compare_hint": "Compare the AI answer with your trusted reference: what matches, what differs, and which would you rely on?",
    },
    "metacognition_score": {
        "title": "Reflect and Self-Test",
        "skills": ["Metacognition", "Self-assessment", "Retrieval practice"],
        "why": (
            "Your Metacognition score suggests there may be room to monitor your own understanding more "
            "closely. This activity practises checking what you actually understand without AI."
        ),
        "why_maintain": (
            "Your Metacognition score is at or above the midpoint. This activity keeps the habit of "
            "testing your own understanding."
        ),
        "tasks": [
            "Think of the last topic you studied with AI help. Without looking at the conversation, write down what you remember and what is still unclear.",
            "Write three questions about a recent topic and answer them from memory before checking any source.",
            "List which concepts from this week you could explain without AI and which you could not, then pick one to revise.",
        ],
        "compare_hint": "Now check your notes or an AI explanation: which parts did you get right, and which did you miss?",
    },
    "learning_benefit_score": {
        "title": "Use AI as a Learning Assistant",
        "skills": ["Active learning", "Applying concepts", "Responsible AI use"],
        "why": (
            "Your Learning Benefits score suggests AI may not yet be supporting your learning as much as "
            "it could. This activity practises using AI to explain, while you do the applying."
        ),
        "why_maintain": (
            "Your Learning Benefits score is at or above the midpoint. This activity keeps AI in a "
            "supporting role while you do the practice."
        ),
        "tasks": [
            "Choose a concept you find difficult. Ask an AI tool to explain it, then close the chat and solve one exercise on it yourself.",
            "Ask an AI tool for a hint (not the solution) on a problem you are stuck on, then finish the problem on your own.",
            "Use AI to generate a practice question on a topic, answer it unaided, and only then check your answer.",
        ],
        "compare_hint": "Compare what the AI explained with what you managed to apply on your own: where was the gap?",
    },
}