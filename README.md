# Cognivue AI

**AI-Based Framework for Detecting Generative AI Overreliance and Providing Adaptive Interventions**
*Detect · Understand · Support · Learn — Think independently. Learn intelligently.*

A research prototype (M.Tech Artificial Intelligence) that estimates potential Generative AI overreliance from
self-reported student learning habits, explains the estimate with SHAP, shows exploratory K-Means behavioural groups and
suggests rule-based learning activities. It is a decision-support tool, **not** a clinical or psychological diagnosis.

Live app: https://cognivue-ai-t2n5.onrender.com/

## Research summary (preserved from the notebook)

| Item | Value |
|---|---|
| Dataset | 170 × 45 original, 151 consented respondents, 19 excluded |
| Student assessment | 24 predictor questions: 5 profile + 5 independent learning + 5 verification + 5 metacognition + 4 learning benefits |
| Target | `overreliance_score` = mean of Q12–Q18 (1–5). Q12–Q18 are **never** asked as inputs (target leakage). Q36 and Q38 stay separate |
| Model | Saved `RandomForestRegressor`, 9 features in fixed order, never retrained by the app |
| Nested CV | MAE 0.4963, RMSE 0.6160, R² 0.3503 (moderate; internal validation only) |
| K-Means | 6 features, K = 2, silhouette 0.3848, clusters of 120 and 31 respondents (exploratory) |
| Interventions | Rule-based; the 3.0 midpoint is a heuristic, not a validated cut-off |

## Project structure

```text
app.py                  Streamlit entry point and page router
backend/                LOGIC (never imports Streamlit)
  questionnaire.py        exact question wording, options and encodings
  validation.py           strict validation of the 24 answers
  preprocessing.py        answers -> 4 construct scores + 5 encodings -> 9 features
  model_loader.py         loads saved models and verifies them against their metadata
  prediction.py           Random Forest prediction (1-5)
  explainability.py       per-student SHAP with additivity check
  clustering.py           K-Means groups derived from the saved model's centroids
  interventions.py        rules + the four interactive activities and progress logic
  history.py              attempts over time (derived scores only), progress file import/export
  report.py               PDF report (ReportLab)
  evaluation.py           optional genuine out-of-fold predictions loader
  research_data.py        verified experiment results (Colab notebook)
ui/                     SCREENS (every file imports Streamlit)
  theme.py art.py layout.py state.py resources.py charts.py
  home.py feature.py assessment.py results.py explain.py interventions.py
  profile.py progress.py model_insights.py research.py testing.py about.py
models/                 saved model + metadata files (unchanged)
.streamlit/config.toml  theme
test_pipeline.py test_features.py test_app_flow.py test_model_loader.py testlog.py
```

`backend/interventions.py` (the rules and activity logic) and `ui/interventions.py` (the page) are different files.

## Run locally (Windows PowerShell, Python 3.11)

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Tests

```powershell
py test_model_loader.py
py test_pipeline.py     # backend: preprocessing, model, SHAP, K-Means, model-loading safety
py test_features.py     # activities, PDF report, attempt history, evaluation loader
py test_app_flow.py     # the full student journey, every page, refresh and model-loading failure
```

The scripts write `test_results.json`, which the **Testing** page displays. Re-run them on your own machine before submission.

## Actual vs predicted and residual plots

These need genuine out-of-fold predictions and are **not** fabricated. Run this in the Colab notebook (use your own cross-validation
settings), download `evaluation_predictions.csv` and place it next to `app.py`:

```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_predict

rf = RandomForestRegressor(n_estimators=149, max_depth=5, max_features=1.0, max_samples=0.8,
                           min_samples_leaf=2, min_samples_split=5, random_state=42)
oof = cross_val_predict(rf, X, y, cv=KFold(n_splits=5, shuffle=True, random_state=42))
pd.DataFrame({"Actual": y.to_numpy(), "Predicted": oof}).to_csv("evaluation_predictions.csv", index=False)
```

The file holds only actual and predicted scores (no identifiers). The app validates it and then shows the plots and metrics.

## Deploy on Render (Docker)

1. Commit and push to GitHub (see the Git clean-up below).
2. In Render, the web service should use **Runtime: Docker** and the repository root. No start command is needed: the `Dockerfile` starts Streamlit on `$PORT`.
3. Set the health check path to `/_stcore/health`. No environment variables are required (`COGNIVUE_MODELS_DIR` can override the models folder).
4. Choose **Manual Deploy → Clear build cache & deploy** after the first push of this version, because the dependencies changed.
5. Open the live URL and complete one assessment end to end. A free instance can take about a minute to wake up.

`render.yaml` is an optional Blueprint if you want to create the service from the repository.

### Git clean-up (run once, PowerShell, project root)

```powershell
git rm -r --cached --ignore-unmatch __pycache__ backend/__pycache__ ui/__pycache__
git rm --cached --ignore-unmatch package-lock.json
git rm --cached --ignore-unmatch -- "Config · TOML"
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
Remove-Item -Force -LiteralPath "Config · TOML" -ErrorAction SilentlyContinue
git add -A
git commit -m "Upgrade Cognivue AI: interactive charts, activities, report, progress, K-Means from centroids"
git push
```

## Privacy

Answers stay in the browser session: they are not stored on the server, written to a database or logged, and no name, email or student ID is requested.
PDF reports and progress files are created only on request and contain derived scores, not raw answers. The hosting provider may keep standard
technical server logs, which do not contain answers.

## Limitations

Self-reported data from 151 respondents at one institution; moderate performance; internal validation only; SHAP and correlations are not causal;
K-Means is exploratory; the intervention threshold is a heuristic and the activities have not been experimentally validated.
