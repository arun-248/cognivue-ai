"""
backend/report.py
-----------------
Downloadable PDF assessment report (reportlab, pure Python).

The report contains derived scores and the student's chosen options only: no
name or email is required, and the optional label is used only on the cover.
It states clearly that the score is an estimate from self-reported answers.
"""

from __future__ import annotations

import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.history import LABELS as CONSTRUCT_SHORT
from backend.history import compare_attempts
from backend.interventions import NEUTRAL_MIDPOINT

NAVY, BLUE, MUTED, LIGHT = colors.HexColor("#142B55"), colors.HexColor("#3478F6"), colors.HexColor("#425B82"), colors.HexColor("#E5F1FF")
NESTED_CV_MAE = 0.4963

DISCLAIMER = (
    "This research prototype estimates potential Generative AI overreliance using self-reported questionnaire "
    "responses. It is intended for educational reflection and research decision support. It is not a clinical or "
    "psychological diagnosis, does not measure actual AI prompt behaviour, and should not be used for high-stakes "
    "decisions about students."
)

_REPLACEMENTS = {
    "\u2265": ">=", "\u2264": "<=", "\u2192": "->", "\u2190": "<-", "\u00b7": "-", "\u2713": "v",
    "\u2212": "-", "\u03c1": "rho", "\u00b1": "+/-", "\u2192": "->", "\u2018": "'", "\u2019": "'",
}


def clean(text) -> str:
    """Make text safe for the built-in PDF fonts (Latin-1 / cp1252)."""
    out = str(text)
    for src, dst in _REPLACEMENTS.items():
        out = out.replace(src, dst)
    return out.encode("cp1252", "replace").decode("cp1252")


def _p(text, style) -> Paragraph:
    return Paragraph(escape(clean(text)), style)


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=base["Title"], fontName="Helvetica-Bold", fontSize=20, textColor=NAVY, spaceAfter=2, alignment=0),
        "sub": ParagraphStyle("s", parent=base["Normal"], fontSize=9.5, textColor=MUTED, spaceAfter=10),
        "h": ParagraphStyle("h", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13, textColor=NAVY, spaceBefore=12, spaceAfter=5),
        "body": ParagraphStyle("b", parent=base["Normal"], fontSize=9.5, leading=13.5, textColor=colors.HexColor("#1F2F4D")),
        "small": ParagraphStyle("sm", parent=base["Normal"], fontSize=8.2, leading=11, textColor=MUTED),
        "cell": ParagraphStyle("c", parent=base["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#1F2F4D")),
        "cellb": ParagraphStyle("cb", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=NAVY),
    }


def _score_bar(score: float, width=170 * mm, height=26) -> Drawing:
    d = Drawing(width, height)
    x0, x1, y = 6, width - 6, 9
    d.add(Rect(x0, y, x1 - x0, 7, fillColor=colors.HexColor("#D9E6F7"), strokeColor=None, rx=3.5, ry=3.5))
    frac = (score - 1) / 4
    d.add(Rect(x0, y, (x1 - x0) * frac, 7, fillColor=BLUE, strokeColor=None, rx=3.5, ry=3.5))
    d.add(Circle(x0 + (x1 - x0) * frac, y + 3.5, 6, fillColor=colors.white, strokeColor=BLUE, strokeWidth=2))
    for v in range(1, 6):
        xx = x0 + (x1 - x0) * (v - 1) / 4
        d.add(Line(xx, y - 3, xx, y, strokeColor=MUTED, strokeWidth=0.6))
        d.add(String(xx, y - 11, str(v), fontSize=8, fillColor=MUTED, textAnchor="middle"))
    return d


def _table(rows, col_widths, header=True):
    t = Table(rows, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D9F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT)]
    t.setStyle(TableStyle(style))
    return t


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, clean("Cognivue AI - research prototype. Estimates from self-reported answers; not a diagnosis."))
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_report_pdf(result: dict, explanation: dict | None = None, cluster_profile: dict | None = None,
                     intervention: dict | None = None, history: list | None = None, label: str = "",
                     include_reflections: bool = False, compress: bool = True) -> bytes:
    """Create the PDF and return its bytes."""
    st = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                            title="Cognivue AI Student Learning Report", author="Cognivue AI", pageCompression=1 if compress else 0)
    W = A4[0] - 36 * mm
    story = []

    pred = result["prediction"]
    scores = result["construct_scores"]
    labels = result["labels"]

    story.append(_p("Cognivue AI - Student Learning Report", st["title"]))
    sub = "AI-Based Framework for Detecting Generative AI Overreliance and Providing Adaptive Interventions"
    stamp = datetime.now().strftime("%d %B %Y, %H:%M")
    story.append(_p(f"{sub}  |  Generated {stamp}" + (f"  |  {label.strip()[:60]}" if label.strip() else ""), st["sub"]))

    # 1. Score
    story.append(_p("1. Estimated overreliance score", st["h"]))
    story.append(_p(f"{pred['score']:.2f} out of 5", ParagraphStyle("big", parent=st["title"], fontSize=26, textColor=BLUE, spaceAfter=0)))
    story.append(_score_bar(pred["score"]))
    story.append(_p("This is a continuous estimate from a Random Forest trained on 151 student questionnaires, on a scale from 1 (weaker "
                    "self-reported reliance) to 5 (stronger). It is not a probability, a category or a diagnosis. In nested cross-validation the average error was about "
                    f"{NESTED_CV_MAE:.2f} points, so an individual estimate can be off by more.", st["body"]))

    # 2. Construct scores
    story.append(_p("2. Learning-habit scores (calculated directly from your answers)", st["h"]))
    rows = [[_p("Dimension", st["cellb"]), _p("Score (1-5)", st["cellb"]), _p(f"Compared with the neutral midpoint ({NEUTRAL_MIDPOINT:.1f})", st["cellb"])]]
    for rec in result["interventions"]:
        s = rec["Observed_Score"]
        rows.append([_p(rec["Construct"], st["cell"]), _p(f"{s:.2f}", st["cell"]),
                     _p("Below the midpoint - support suggested" if s < NEUTRAL_MIDPOINT else "At or above the midpoint", st["cell"])])
    story.append(_table(rows, [W * 0.4, W * 0.18, W * 0.42]))
    story.append(Spacer(1, 4))
    story.append(_p(f"AI usage frequency: {labels['usage_frequency']}.  AI usage on a study day: {labels['usage_duration']}.  "
                    "The midpoint of 3.0 is a heuristic, not a validated cut-off.", st["small"]))

    # 3. Focus & recommendations
    story.append(_p("3. Suggested focus and recommendations", st["h"]))
    flagged = [r for r in result["interventions"] if r["Priority"] == "Focus area"]
    focus = min(flagged or result["interventions"], key=lambda r: r["Observed_Score"])
    story.append(_p(f"Most important area to look at: {focus['Construct']} (score {focus['Observed_Score']:.2f}). "
                    + ("Targeted support is suggested." if flagged else "All dimensions are at or above the midpoint, so maintenance suggestions apply."), st["body"]))
    story.append(Spacer(1, 3))
    for rec in sorted(result["interventions"], key=lambda r: (r["Priority"] != "Focus area", r["Observed_Score"])):
        story.append(KeepTogether([_p(f"{rec['Construct']} - {rec['Status']}", st["cellb"]), _p(rec["Intervention"], st["body"]), Spacer(1, 4)]))

    # 4. SHAP
    if explanation:
        story.append(_p("4. What influenced the estimate (SHAP)", st["h"]))
        story.append(_p(f"Model baseline {explanation['baseline']:.2f}; your estimate {explanation['model_output']:.2f}. Positive values pushed the "
                        "estimate higher and negative values pushed it lower, relative to the baseline. These are influential predictors in the model, not causes.", st["body"]))
        table = explanation["contributions"]
        rows = [[_p("Model feature", st["cellb"]), _p("Contribution", st["cellb"]), _p("Effect", st["cellb"])]]
        for r in table.head(6).itertuples():
            rows.append([_p(r.label, st["cell"]), _p(f"{r.shap:+.3f}", st["cell"]), _p(r.direction, st["cell"])])
        story.append(_table(rows, [W * 0.5, W * 0.2, W * 0.3]))

    # 5. K-Means
    if cluster_profile:
        story.append(_p("5. Exploratory K-Means group", st["h"]))
        story.append(_p(f"Your answers are closest to Cluster {cluster_profile['cluster_id']} ({cluster_profile['profile_label']}). This grouping is exploratory "
                        "(silhouette 0.38, moderate separation). It is not a diagnosis or a validated student type.", st["body"]))

    # 6. Interventions
    if intervention:
        story.append(_p("6. Learning activities", st["h"]))
        rows = [[_p("Dimension", st["cellb"]), _p("Activity", st["cellb"]), _p("Status", st["cellb"]), _p("Done", st["cellb"])]]
        for r in intervention["rows"]:
            rows.append([_p(r["construct"], st["cell"]), _p(r["activity"], st["cell"]), _p(r["progress_status"], st["cell"]), _p(f"{r['percent']:.0f}%", st["cell"])])
        story.append(_table(rows, [W * 0.3, W * 0.37, W * 0.18, W * 0.15]))
        story.append(Spacer(1, 3))
        story.append(_p(f"{intervention['completed']} of {intervention['total']} activities completed. "
                        + (f"Suggested next: {intervention['next']['activity']} ({intervention['next']['construct']})." if intervention["next"] else "All activities completed."), st["body"]))
        story.append(_p("Completing an activity only records that the task was done. It has not been shown to improve learning or reduce overreliance.", st["small"]))
        if include_reflections:
            for r in intervention["rows"]:
                for question, answer in r.get("reflections", []):
                    story.append(KeepTogether([_p(f"{r['construct']}: {question}", st["cellb"]), _p(answer, st["body"]), Spacer(1, 3)]))

    # 7. Progress
    if history and len(history) >= 2:
        story.append(_p("7. Change since the previous attempt", st["h"]))
        prev, last = history[-2], history[-1]
        delta = compare_attempts(prev, last)
        rows = [[_p("Measure", st["cellb"]), _p("Previous", st["cellb"]), _p("Latest", st["cellb"]), _p("Change", st["cellb"])]]
        rows.append([_p("Estimated overreliance score", st["cell"]), _p(f"{prev['predicted_score']:.2f}", st["cell"]),
                     _p(f"{last['predicted_score']:.2f}", st["cell"]), _p(f"{delta['predicted_score']:+.2f}", st["cell"])])
        for f, name in CONSTRUCT_SHORT.items():
            rows.append([_p(name, st["cell"]), _p(f"{prev['construct_scores'][f]:.2f}", st["cell"]),
                         _p(f"{last['construct_scores'][f]:.2f}", st["cell"]), _p(f"{delta['construct_scores'][f]:+.2f}", st["cell"])])
        story.append(_table(rows, [W * 0.46, W * 0.18, W * 0.18, W * 0.18]))
        story.append(_p("These are changes in self-reported scores between attempts. They do not prove a change in actual ability.", st["small"]))

    story.append(Spacer(1, 10))
    story.append(KeepTogether([_p("Disclaimer", st["cellb"]), _p(DISCLAIMER, st["small"])]))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
