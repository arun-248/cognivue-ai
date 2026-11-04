# Cognivue AI — audit of the uploaded project (before this update)

Based on reading every Python file in `backend/` and `ui/`, `app.py`, `requirements.txt`, the tests, the Dockerfile, the ignore files and the saved model/metadata files.

## Working features (kept)
- 24-question assessment, strict validation, no default answers, review page, session-only answers.
- Exact nine-feature preprocessing, verified against the Colab metadata and respondent 118; saved Random Forest prediction (1–5).
- SHAP TreeExplainer with an additivity check; rule-based interventions from the notebook; Docker image for Render; 27 automated app-flow tests.

## Bugs and research inconsistencies found
| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | `ui/art.py` gauge illustration showed 1–7 with Low · Moderate · High zones | High (contradicts the 1–5 continuous model) | Replaced by a single-colour 1–5 "continuous model estimate" gauge; a test scans the UI for old scale/risk wording |
| 2 | K-Means label came from the student's own construct average (≥ 3.0), not from the fitted centroids | High (the same cluster could be labelled "Stronger" or "Developing") | Labels derived from the saved centroids; cluster sizes, averages and PCA now come from the saved objects |
| 3 | Q12–Q18 distributions were not shown anywhere | Medium (missing research information) | New Research tab with the seven statements and counts (all sum to 151) |
| 4 | "Actual vs predicted"/residual plots had no genuine data | Medium | Kept honest: plots appear only from a real `evaluation_predictions.csv`; a notebook export cell is provided |
| 5 | Chart styling inconsistent and static | Low | Interactive Plotly charts in one style; Matplotlib removed |
| 6 | Hover/animation effects and a SMIL animation in an illustration | Low | Removed |
| 7 | Low-contrast small labels | Low | Darkened |

## Deployment and repository hygiene
- Theme file was named `Config · TOML` at the project root, so Render never used it → moved to `.streamlit/config.toml`.
- `package-lock.json` (Node) present in a Python project → removed and ignored.
- `__pycache__` folders were present in the upload (they should never be tracked) → ignored; Git clean-up commands are in the README.
- Plotly was pinned but unused → now used for all charts; Matplotlib removed; ReportLab added for PDF reports.
- Dockerfile ran as root without a health check → non-root user and health check added.
- No README or documentation of changes → added `README.md`, `AUDIT.md`, `CHANGES.md`.
- `test_results.json` only held the app-flow suite → every test script now records its results.

## Privacy and security
- No personal data is requested and answers are not stored or logged. No problems found.
- Free-text activity boxes could receive personal details → warning added; they remain session-only.
- Uploaded progress files are size-limited and schema-validated.

## Not verifiable in this review
- Visual appearance on real desktop and mobile browsers (no browser was available); a manual checklist is in `CHANGES.md`.
- The Docker image build and the Render deployment (Docker was not available); the dependencies were verified by a clean install on Python 3.11 and all tests.
