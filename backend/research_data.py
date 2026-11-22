"""
backend/research_data.py
------------------------
Verified experiment outputs from the Colab notebook (RM_MAIN_FINAL) and the
metadata JSON files. Nothing here is simulated. Values are displayed as-is.
"""

from __future__ import annotations

DATASET = {
    "original_rows": 274,
    "original_columns": 45,
    "consented": 249,
    "not_consented": 25,
    "features": 9,
}

# Nested cross-validation (headline generalisation estimate)
NESTED_CV = {"MAE": 0.5286, "RMSE": 0.6968, "R2": 0.1952}

# Repeated 5-fold CV x 3 repeats (15 folds): mean and SD
REPEATED_CV = [
    # model, MAE, RMSE, R2, MAE_SD, RMSE_SD, R2_SD
    ('Mean baseline', 0.6331, 0.7860, -0.0250, 0.0478, 0.0544, 0.0359),
    ('Median baseline', 0.6378, 0.7932, -0.0438, 0.0509, 0.0576, 0.0469),
    ('Random Forest', 0.5329, 0.6957, 0.1971, 0.0676, 0.0927, 0.1314),
]
RF_IMPROVEMENT_PERCENT = 15.83
TRAIN_VALIDATION = {"train_mae": 0.3987, "validation_mae": 0.5329, "gap": 0.1342}

# Phase 9 model comparison: repeated 5-fold x 5 repeats (25 folds)
MODEL_COMPARISON = [
    # model, MAE, MAE_SD, RMSE, RMSE_SD, R2, R2_SD
    ('Gradient Boosting', 0.5362, 0.0574, 0.6975, 0.0884, 0.1845, 0.1221),
    ('Random Forest', 0.5368, 0.0597, 0.7020, 0.0868, 0.1734, 0.1240),
    ('Support Vector Regression', 0.5374, 0.0515, 0.6978, 0.0754, 0.1788, 0.1346),
    ('K-Nearest Neighbors', 0.5464, 0.0573, 0.7134, 0.0749, 0.1458, 0.1024),
    ('Lasso Regression', 0.5937, 0.0622, 0.7660, 0.0885, 0.0152, 0.1351),
    ('Ridge Regression', 0.5952, 0.0636, 0.7682, 0.0911, 0.0089, 0.1450),
    ('Linear Regression', 0.5955, 0.0637, 0.7687, 0.0914, 0.0076, 0.1460),
    ('Dummy Regressor', 0.6352, 0.0426, 0.7879, 0.0555, -0.0419, 0.0529),
]

RF_PARAMETERS = {
    "n_estimators": 149, "max_depth": 5, "max_features": 1.0,
    "max_samples": 0.8, "min_samples_leaf": 2, "min_samples_split": 5,
}

# Deep learning vs Random Forest (repeated 5-fold x 3) - RE-RUN on the final 249-response modelling data
# with the notebook's Phase 15 protocol (same RepeatedKFold(5, 3, random_state=42) splits for both models,
# StandardScaler fitted on each training fold, early stopping patience 15, validation_split 0.20, batch 16).
DEEP_LEARNING = [
    # model, MAE, MAE_SD, RMSE, RMSE_SD, R2, R2_SD
    ("Random Forest", 0.5329, 0.0676, 0.6958, 0.0927, 0.1969, 0.1313),
    ("Deep Learning", 0.5763, 0.0572, 0.7421, 0.0914, 0.0780, 0.1842),
]
DL_DATASET_N = 249
DL_ARCHITECTURE = "Dense 32 \u2192 Dropout \u2192 Dense 16 \u2192 Dropout \u2192 Dense 8 \u2192 Dense 1 (993 parameters)"

RELIABILITY = [
    ('Overreliance (Q12–Q18)', 0.8816),
    ('Independent learning', 0.8538),
    ('Verification', 0.8469),
    ('Metacognition', 0.8839),
    ('Positive learning benefits', 0.7640),
    ('Six-item positive/negative outcome scale', 0.2262),
]

SPEARMAN = [
    ('Overreliance vs independent learning', -0.3491, '< 0.001'),
    ('Overreliance vs verification', -0.3340, '< 0.001'),
    ('Overreliance vs metacognition', -0.2634, '< 0.001'),
    ('Overreliance vs learning benefits', -0.0881, '0.1657'),
    ('Usage frequency vs overreliance', 0.1009, '0.1124'),
    ('Usage duration vs overreliance', 0.0839, '0.1869'),
]

# K-Means (K = 2 selected)
KMEANS_SILHOUETTE = {2: 0.3618, 3: 0.2387, 4: 0.2296, 5: 0.2429, 6: 0.2363}
KMEANS_INERTIA = {2: 1008.2842, 3: 813.5382, 4: 701.1810, 5: 611.3443, 6: 545.5146}
KMEANS_DISTRIBUTION = [(0, 195, 78.31), (1, 54, 21.69)]
KMEANS_FEATURE_MEANS = {
    0: {"independent_learning_score": 4.046, "verification_score": 4.008, "metacognition_score": 4.083, "learning_benefit_score": 3.892, "usage_frequency_encoded": 3.549, "usage_time_encoded": 3.477},
    1: {"independent_learning_score": 2.970, "verification_score": 2.878, "metacognition_score": 2.896, "learning_benefit_score": 3.023, "usage_frequency_encoded": 2.611, "usage_time_encoded": 2.685},
}
KMEANS_PROFILE_SUMMARY = [
    # cluster, respondents, mean predicted overreliance, mean support areas
    (0, 195, 2.7184, 0.0410, 'Stronger learning-strategy profile'),
    (1, 54, 2.8938, 0.9074, 'Developing learning-strategy profile'),
]
PCA_EXPLAINED_VARIANCE = 0.7921

# Input noise robustness, Random Forest (Gaussian noise on standardised test predictors)
NOISE = [
    (0, 0.5214, 0.6905, 0.2251),
    (5, 0.5212, 0.6902, 0.2257),
    (10, 0.5271, 0.6972, 0.2100),
    (20, 0.5382, 0.7069, 0.1877),
    (30, 0.5331, 0.7115, 0.1771),
]

# CTGAN augmentation - HISTORICAL RECORD ONLY (earlier 151-response run). Not shown in the final presentation:
# it could not be repeated on 249 responses because the supplied notebook has no CTGAN code.
GAN = {
    "Real-only Random Forest": (0.4798, 0.5866, 0.3989),
    "GAN-augmented Random Forest": (0.5153, 0.6168, 0.3370),
}
GAN_FACTS = {"synthetic_records": 604, "quality_measurements": 50, "mae_increase_percent": 7.4}

# Distribution of the training target (mean of the seven direct overreliance statements, 1-5) for the
# 249 modelled respondents, computed from the published questionnaire file. Aggregates only.
# Bins are [a, b) except the last, which includes 5.0.
TARGET_DISTRIBUTION = {
    "bins": ["1.0\u20131.5", "1.5\u20132.0", "2.0\u20132.5", "2.5\u20133.0", "3.0\u20133.5", "3.5\u20134.0", "4.0\u20134.5", "4.5\u20135.0"],
    "counts": [16, 19, 57, 40, 74, 25, 15, 3],
    "n": 249, "mean": 2.7458, "sd": 0.7860, "min": 1.0, "max": 5.0,
}

# Global SHAP ranking (mean |SHAP| on the training data)
SHAP_GLOBAL = [
    ('Independent learning', 0.245151, 39.98),
    ('Verification', 0.107475, 17.53),
    ('Study year', 0.084628, 13.80),
    ('Metacognition', 0.055710, 9.09),
    ('Usage frequency', 0.051374, 8.38),
    ('Experience', 0.029599, 4.83),
    ('Learning benefits', 0.019838, 3.24),
    ('Usage duration', 0.015879, 2.59),
    ('Age', 0.003541, 0.58),
]

# Dataset-level intervention summary (respondents identified for support, of 249)
INTERVENTION_SUMMARY = [
    ('Independent learning', 14),
    ('Verification', 16),
    ('Metacognition', 12),
    ('Learning benefits', 15),
]

CONSTRUCT_TABLE = [
    ("Overreliance", "Q12\u2013Q18", "Target variable (mean of 7 items)"),
    ("Independent Learning", "Q19, Q20, Q21, Q22, Q23", "Independent reasoning and learning"),
    ("Verification", "Q24\u2013Q28", "Checking and evaluating AI-generated information"),
    ("Metacognition", "Q29\u2013Q33", "Awareness and regulation of one's learning"),
    ("Learning Benefits", "Q34, Q35, Q37, Q39", "Perceived positive learning outcomes"),
    ("Negative Retention Item", "Q36", "Kept separate (not a model input)"),
    ("AI Access Dependence Item", "Q38", "Kept separate (not a model input)"),
]

# Direct indicators of AI overreliance (the seven target items Q12-Q18).
# Response counts among the 249 modelled respondents (published questionnaire dataset).
# These items define the target; they are NEVER collected as predictors in the app.
LIKERT_ORDER = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
DIRECT_INDICATORS = [
    ("Q12", "I depend on generative AI to begin academic tasks that I could attempt independently.", (30, 49, 102, 60, 8)),
    ("Q13", "I find it difficult to complete certain academic tasks when generative AI is unavailable.", (16, 45, 102, 76, 10)),
    ("Q14", "I often accept AI-generated answers without developing my own solution first.", (41, 76, 80, 47, 5)),
    ("Q15", "I rely on generative AI even when I have enough knowledge to solve a problem myself.", (44, 74, 69, 57, 5)),
    ("Q16", "I feel less confident in my ability to solve academic problems independently when I cannot use generative AI.", (38, 80, 72, 53, 6)),
    ("Q17", "I sometimes submit or use AI-generated solutions without fully understanding how they work.", (45, 70, 73, 56, 5)),
    ("Q18", "After receiving a suggestion from Generative AI, I find it difficult to decide on an answer independently.", (23, 70, 93, 58, 5)),
]

# Evidence types used to keep results from different evaluations clearly separate.
EVIDENCE_GUIDE = [
    ("Nested cross-validation", "Headline generalisation estimate for the final Random Forest on the 249 modelled respondents (internal; not external validation)."),
    ("Repeated 5-fold CV \u00d7 3 (15 folds)", "Final tuned Random Forest versus mean/median baselines (249 respondents). The Deep Learning comparison was re-run on the same 249 respondents with the same folds."),
    ("Repeated 5-fold CV \u00d7 5 (25 folds)", "Comparison of eight candidate regression models used to choose the algorithm."),
    ("Training-data (descriptive)", "SHAP rankings and Random Forest feature importance are calculated on the training respondents and describe the fitted model."),
    ("Hold-out noise test", "Gaussian noise added to standardised test predictors while training data stayed clean."),
    ("Out-of-fold predictions (optional)", "Actual vs predicted and residual plots appear only when a genuine evaluation_predictions.csv exported from the notebook is supplied."),
    ("External validation", "Not done. No result on this site is from an independent student population."),
]


# ---------------------------------------------------------------------------
# Evidence provenance. Every result shown in the app comes from the 249-response final modelling dataset.
# Deep Learning was re-run on 249 (see DEEP_LEARNING). The CTGAN experiment (GAN, GAN_FACTS above) exists only for
# an earlier 151-response snapshot; it is kept as a historical record and is NOT displayed as a result.
EARLIER_SNAPSHOT_RESPONDENTS = 151
EARLIER_SNAPSHOT_EXPERIMENTS = ("CTGAN augmentation",)
HISTORICAL_DEEP_LEARNING_151 = [
    ("Random Forest", 0.4904, 0.0597, 0.6076, 0.0629, 0.3681, 0.1107),
    ("Deep Learning", 0.7327, 0.1693, 0.9347, 0.2056, -0.4999, 0.5511),
]
