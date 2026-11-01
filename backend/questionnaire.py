"""
backend/questionnaire.py
------------------------
Single source of truth for the Cognivue AI questionnaire.

* Question wording is copied from the original Google Form (not paraphrased).
* Encodings are the exact mappings used in the Colab preprocessing
  (Cognivue_Preprocessing_Metadata.json).
* Q12-Q18 (the seven overreliance items) define the TARGET and are never
  collected here. Q36 and Q38 are not model inputs and are not collected.

Note on numbering: the original form skips Q21 and contains two questions
numbered Q22. They are kept as separate items called "Q22a" and "Q22b".
"""

from __future__ import annotations

import re

# ----------------------------------------------------------------------
# Likert scale
# ----------------------------------------------------------------------
LIKERT_LABELS = [
    "Strongly Disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly Agree",
]
LIKERT_VALUES = {label: value for value, label in enumerate(LIKERT_LABELS, start=1)}

# ----------------------------------------------------------------------
# Section A - student profile (5 categorical questions)
# options = (display label, ordinal code used by the trained model)
# ----------------------------------------------------------------------
PROFILE_QUESTIONS = [
    {
        "key": "age_group",
        "source_id": "Q1",
        "feature": "age_group_encoded",
        "text": "What is your age group?",
        "options": [
            ("16–17", 1),
            ("18–22", 2),
            ("23–26", 3),
            ("Above 26", 4),
        ],
    },
    {
        "key": "study_year",
        "source_id": "Q4",
        "feature": "study_year_encoded",
        "text": "What is your current year of study?",
        "options": [
            ("First year", 1),
            ("Second year", 2),
            ("Third year", 3),
            ("Fourth year", 4),
            ("Fifth year or above", 5),
        ],
    },
    {
        "key": "experience",
        "source_id": "Q5",
        "feature": "experience_encoded",
        "text": "How would you describe your previous experience with generative AI tools?",
        "options": [
            ("No experience", 0),
            ("Beginner", 1),
            ("Intermediate", 2),
            ("Advanced", 3),
        ],
    },
    {
        "key": "usage_frequency",
        "source_id": "Q7",
        "feature": "usage_frequency_encoded",
        "text": "How frequently do you use generative AI for academic work?",
        "options": [
            ("Never", 0),
            ("Less than once a week", 1),
            ("1–2 days a week", 2),
            ("3–5 days a week", 3),
            ("Daily", 4),
            ("Multiple times a day", 5),
        ],
    },
    {
        "key": "usage_duration",
        "source_id": "Q8",
        "feature": "usage_time_encoded",
        "text": (
            "Approximately how much time do you spend using generative AI "
            "for academic work on a typical study day?"
        ),
        "options": [
            ("No use", 0),
            ("Less than 15 minutes", 1),
            ("15–30 minutes", 2),
            ("31–60 minutes", 3),
            ("1–2 hours", 4),
            ("More than 2 hours", 5),
        ],
    },
]

PROFILE_KEYS = [q["key"] for q in PROFILE_QUESTIONS]

# ----------------------------------------------------------------------
# Sections B-E - the 19 Likert predictor items
# ----------------------------------------------------------------------
LIKERT_SECTIONS = [
    {
        "section": "B",
        "title": "Independent learning",
        "feature": "independent_learning_score",
        "construct": "Independent Learning",
        "items": [
            {"id": "Q19", "text": "I try to solve an academic problem independently before asking generative AI for help."},
            {"id": "Q20", "text": "I develop my own ideas before using AI to improve or expand them."},
            {"id": "Q22a", "text": "I can complete familiar academic tasks without depending on generative AI."},
            {"id": "Q22b", "text": "I attempt to solve a problem again independently after learning the solution from AI."},
            {"id": "Q23", "text": "I use AI explanations to understand concepts rather than simply obtain final answers."},
        ],
    },
    {
        "section": "C",
        "title": "Verification and critical thinking",
        "feature": "verification_score",
        "construct": "Verification and Critical Thinking",
        "items": [
            {"id": "Q24", "text": "I verify important AI-generated information using textbooks, research papers, official documentation, or other reliable sources."},
            {"id": "Q25", "text": "I check the steps and reasoning behind AI-generated mathematical or programming solutions."},
            {"id": "Q26", "text": "I look for possible errors, bias, or unsupported claims in AI-generated responses."},
            {"id": "Q27", "text": "When an AI-generated answer conflicts with my existing knowledge, I investigate the disagreement before accepting either answer."},
            {"id": "Q28", "text": "I can identify situations in which an AI-generated response may be incorrect or misleading."},
        ],
    },
    {
        "section": "D",
        "title": "Metacognition and self-assessment",
        "feature": "metacognition_score",
        "construct": "Metacognition",
        "intro": "Metacognition means monitoring and evaluating your own understanding and learning.",
        "items": [
            {"id": "Q29", "text": "Before using AI, I identify what I already know and what I need help understanding."},
            {"id": "Q30", "text": "After using AI, I assess whether I genuinely understand the material."},
            {"id": "Q31", "text": "I test myself without AI to check whether I have learned a concept."},
            {"id": "Q32", "text": "I can identify which topics I do not understand, even after receiving an AI explanation."},
            {"id": "Q33", "text": "I change my learning strategy when I realize that relying on AI is not helping me understand a topic."},
        ],
    },
    {
        "section": "E",
        "title": "Learning outcomes and perceived impact",
        "feature": "learning_benefit_score",
        "construct": "Learning Benefits",
        "items": [
            {"id": "Q34", "text": "Generative AI helps me understand difficult concepts more efficiently."},
            {"id": "Q35", "text": "My ability to solve problems independently has improved through my use of generative AI."},
            {"id": "Q37", "text": "I can recall and explain concepts later without reopening the AI conversation."},
            {"id": "Q39", "text": "Overall, I believe my current use of generative AI supports my long-term learning rather than merely completing tasks."},
        ],
    },
]

LIKERT_ITEM_IDS = [item["id"] for sec in LIKERT_SECTIONS for item in sec["items"]]
CONSTRUCT_ITEMS = {sec["feature"]: [i["id"] for i in sec["items"]] for sec in LIKERT_SECTIONS}
CONSTRUCT_LABELS = {sec["feature"]: sec["construct"] for sec in LIKERT_SECTIONS}

# Target items: must never be collected as predictors (leakage guard).
TARGET_ITEM_IDS = ["Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18"]

# Exact column order the saved Random Forest expects.
FEATURE_ORDER = [
    "independent_learning_score",
    "verification_score",
    "metacognition_score",
    "learning_benefit_score",
    "usage_frequency_encoded",
    "usage_time_encoded",
    "age_group_encoded",
    "study_year_encoded",
    "experience_encoded",
]

REQUIRED_KEYS = PROFILE_KEYS + LIKERT_ITEM_IDS  # 5 + 19 = 24

assert len(PROFILE_KEYS) == 5
assert len(LIKERT_ITEM_IDS) == 19
assert len(REQUIRED_KEYS) == 24
assert len(FEATURE_ORDER) == 9


# ----------------------------------------------------------------------
# Label normalisation (handles hyphen vs en dash, case, spacing)
# ----------------------------------------------------------------------
def normalize_label(value: str) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", text)  # any dash -> "-"
    return re.sub(r"\s+", " ", text)


def _build_lookup(question: dict) -> dict:
    return {normalize_label(label): code for label, code in question["options"]}


PROFILE_LOOKUP = {q["key"]: _build_lookup(q) for q in PROFILE_QUESTIONS}
LIKERT_LOOKUP = {normalize_label(k): v for k, v in LIKERT_VALUES.items()}