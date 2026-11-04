"""
backend/research_data.py
------------------------
Verified experiment outputs from the Colab notebook (RM_MAIN_FINAL) and the
metadata JSON files. Nothing here is simulated. Values are displayed as-is.
"""

from __future__ import annotations

DATASET = {
    "original_rows": 170,
    "original_columns": 45,
    "consented": 151,
    "not_consented": 19,
    "features": 9,
}

# Nested cross-validation (headline generalisation estimate)
NESTED_CV = {"MAE": 0.4963, "RMSE": 0.6160, "R2": 0.3503}

# Repeated 5-fold CV x 3 repeats (15 folds): mean and SD
REPEATED_CV = [
    # model, MAE, RMSE, R2, MAE_SD, RMSE_SD, R2_SD
    ("Mean baseline", 0.6425, 0.7864, -0.0437, 0.0686, 0.0812, 0.0537),
    ("Median baseline", 0.6458, 0.7940, -0.0648, 0.0705, 0.0835, 0.0792),
    ("Random Forest", 0.4904, 0.6076, 0.3681, 0.0597, 0.0629, 0.1107),
]
RF_IMPROVEMENT_PERCENT = 23.67
TRAIN_VALIDATION = {"train_mae": 0.3390, "validation_mae": 0.4904, "gap": 0.1514}

# Phase 9 model comparison: repeated 5-fold x 5 repeats (25 folds)
MODEL_COMPARISON = [
    # model, MAE, MAE_SD, RMSE, RMSE_SD, R2, R2_SD
    ("Random Forest", 0.5119, 0.0562, 0.6299, 0.0700, 0.3228, 0.0996),
    ("K-Nearest Neighbors", 0.5292, 0.0639, 0.6670, 0.0781, 0.2351, 0.1490),
    ("Gradient Boosting", 0.5311, 0.0575, 0.6549, 0.0761, 0.2676, 0.1140),
    ("Support Vector Regression", 0.5514, 0.0651, 0.6774, 0.0820, 0.2086, 0.1695),
    ("Lasso Regression", 0.6017, 0.0541, 0.7510, 0.0659, 0.0314, 0.1600),
    ("Ridge Regression", 0.6065, 0.0539, 0.7578, 0.0646, 0.0096, 0.1934),
    ("Linear Regression", 0.6075, 0.0539, 0.7591, 0.0644, 0.0051, 0.2018),
    ("Dummy Regressor", 0.6424, 0.0800, 0.7849, 0.0893, -0.0406, 0.0486),
]

RF_PARAMETERS = {
    "n_estimators": 149, "max_depth": 5, "max_features": 1.0,
    "max_samples": 0.8, "min_samples_leaf": 2, "min_samples_split": 5,
}

# Deep learning vs Random Forest (repeated 5-fold x 3)
DEEP_LEARNING = [
    # model, MAE, MAE_SD, RMSE, RMSE_SD, R2, R2_SD
    ("Random Forest", 0.4904, 0.0597, 0.6076, 0.0629, 0.3681, 0.1107),
    ("Deep Learning", 0.7327, 0.1693, 0.9347, 0.2056, -0.4999, 0.5511),
]
DL_ARCHITECTURE = "Dense 32 \u2192 Dropout \u2192 Dense 16 \u2192 Dropout \u2192 Dense 8 \u2192 Dense 1 (993 parameters)"

RELIABILITY = [
    ("Overreliance (Q12\u2013Q18)", 0.872),
    ("Independent learning", 0.8477),
    ("Verification", 0.8512),
    ("Metacognition", 0.8825),
    ("Positive learning benefits", 0.7787),
    ("Six-item positive/negative outcome scale", 0.2269),
]

SPEARMAN = [
    ("Overreliance vs independent learning", -0.4396, "< 0.001"),
    ("Overreliance vs verification", -0.3653, "< 0.001"),
    ("Overreliance vs metacognition", -0.3399, "0.00002"),
    ("Overreliance vs learning benefits", -0.1013, "0.21585"),
    ("Usage frequency vs overreliance", 0.0522, "0.5241"),
    ("Usage duration vs overreliance", 0.084, "0.3054"),
]

# K-Means (K = 2 selected)
KMEANS_SILHOUETTE = {2: 0.3848, 3: 0.2439, 4: 0.2600, 5: 0.2520, 6: 0.2227}
KMEANS_INERTIA = {2: 601.3587, 3: 477.8901, 4: 392.8281, 5: 337.3197, 6: 301.7762}
KMEANS_DISTRIBUTION = [(0, 120, 79.47), (1, 31, 20.53)]
KMEANS_FEATURE_MEANS = {
    0: {"independent_learning_score": 4.042, "verification_score": 4.010, "metacognition_score": 4.072,
        "learning_benefit_score": 3.867, "usage_frequency_encoded": 3.425, "usage_time_encoded": 3.225},
    1: {"independent_learning_score": 2.897, "verification_score": 2.774, "metacognition_score": 2.794,
        "learning_benefit_score": 2.911, "usage_frequency_encoded": 2.548, "usage_time_encoded": 2.419},
}
KMEANS_PROFILE_SUMMARY = [
    # cluster, respondents, mean predicted overreliance, mean support areas
    (0, 120, 2.6852, 0.0417, "Stronger learning-strategy profile"),
    (1, 31, 2.8874, 1.2258, "Developing learning-strategy profile"),
]
PCA_EXPLAINED_VARIANCE = 0.8096

# Input noise robustness, Random Forest (Gaussian noise on standardised test predictors)
NOISE = [
    (0, 0.4798, 0.5866, 0.3989),
    (5, 0.4803, 0.5867, 0.3988),
    (10, 0.4966, 0.6031, 0.3634),
    (20, 0.4936, 0.6117, 0.3507),
    (30, 0.5341, 0.6660, 0.2230),
]

# CTGAN augmentation
GAN = {
    "Real-only Random Forest": (0.4798, 0.5866, 0.3989),
    "GAN-augmented Random Forest": (0.5153, 0.6168, 0.3370),
}
GAN_FACTS = {"synthetic_records": 604, "quality_measurements": 50, "mae_increase_percent": 7.4}

# Global SHAP ranking (mean |SHAP| on the training data)
SHAP_GLOBAL = [
    ("Independent learning", 0.246994, 32.74),
    ("Metacognition", 0.121335, 16.08),
    ("Study year", 0.113543, 15.05),
    ("Verification", 0.106943, 14.18),
    ("Learning benefits", 0.054704, 7.25),
    ("Usage frequency", 0.044211, 5.86),
    ("Usage duration", 0.041937, 5.56),
    ("Experience", 0.014122, 1.87),
    ("Age", 0.010589, 1.40),
]

# Dataset-level intervention summary (respondents identified for support, of 151)
INTERVENTION_SUMMARY = [
    ("Independent learning", 9),
    ("Verification", 12),
    ("Metacognition", 10),
    ("Learning benefits", 12),
]

CONSTRUCT_TABLE = [
    ("Overreliance", "Q12\u2013Q18", "Target variable (mean of 7 items)"),
    ("Independent Learning", "Q19, Q20, Q22a, Q22b, Q23", "Independent reasoning and learning"),
    ("Verification", "Q24\u2013Q28", "Checking and evaluating AI-generated information"),
    ("Metacognition", "Q29\u2013Q33", "Awareness and regulation of one's learning"),
    ("Learning Benefits", "Q34, Q35, Q37, Q39", "Perceived positive learning outcomes"),
    ("Negative Retention Item", "Q36", "Kept separate (not a model input)"),
    ("AI Access Dependence Item", "Q38", "Kept separate (not a model input)"),
]

# Direct indicators of AI overreliance (the seven target items Q12-Q18).
# Response counts among the 151 consented respondents, from the Colab value counts.
# These items define the target; they are NEVER collected as predictors in the app.
LIKERT_ORDER = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
DIRECT_INDICATORS = [
    ("Q12", "I depend on generative AI to begin academic tasks that I could attempt independently.", (22, 27, 60, 38, 4)),
    ("Q13", "I find it difficult to complete certain academic tasks when generative AI is unavailable.", (13, 31, 54, 47, 6)),
    ("Q14", "I often accept AI-generated answers without developing my own solution first.", (28, 45, 47, 28, 3)),
    ("Q15", "I rely on generative AI even when I have enough knowledge to solve a problem myself.", (30, 43, 41, 34, 3)),
    ("Q16", "I feel less confident in my ability to solve academic problems independently when I cannot use generative AI.", (25, 45, 43, 34, 4)),
    ("Q17", "I sometimes submit or use AI-generated solutions without fully understanding how they work.", (33, 42, 44, 32, 0)),
    ("Q18", "After receiving a suggestion from Generative AI, I find it difficult to decide on an answer independently.", (14, 38, 58, 39, 2)),
]

# Evidence types used to keep results from different evaluations clearly separate.
EVIDENCE_GUIDE = [
    ("Nested cross-validation", "Headline generalisation estimate for the final Random Forest on the 151 respondents (internal; not external validation)."),
    ("Repeated 5-fold CV \u00d7 3 (15 folds)", "Final tuned Random Forest versus mean/median baselines, and versus the Deep Learning model."),
    ("Repeated 5-fold CV \u00d7 5 (25 folds)", "Comparison of eight candidate regression models used to choose the algorithm."),
    ("Training-data (descriptive)", "SHAP rankings and Random Forest feature importance are calculated on the training respondents and describe the fitted model."),
    ("Hold-out noise test", "Gaussian noise added to standardised test predictors while training data stayed clean."),
    ("Out-of-fold predictions (optional)", "Actual vs predicted and residual plots appear only when a genuine evaluation_predictions.csv exported from the notebook is supplied."),
    ("External validation", "Not done. No result on this site is from an independent student population."),
]
