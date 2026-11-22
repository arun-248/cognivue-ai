"""ui/research_graphs.py - section 11: Graphs & Visual Results (nine graphs, each with title, caption, dataset version, units).

Every chart is drawn from the saved results in backend/research_data.py. If you later add a screenshot named
assets/graphs/graph_<n>.png it is shown instead of the generated chart for that graph.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from backend import research_data as R
from ui import charts
from ui.theme import chart_card, md_html, notice, section_title

GRAPH_DIR = Path(__file__).resolve().parent.parent / "assets" / "graphs"
V249 = "Final modelling dataset (249 responses)"
BLUE, PURPLE, CYAN, AMBER, GREY, PINK = "#3478F6", "#8757E8", "#0F8F80", "#D97706", "#B9C9E6", "#D6336C"


def _frame(n: int, title: str, version: str, metric: str, caption: str, draw) -> None:
    """One numbered graph: header, chart (or supplied image), version label, metric/units and an interpretation."""
    with chart_card(f"Graph {n}: {title}"):
        image = GRAPH_DIR / f"graph_{n}.png"
        if image.exists():
            st.image(str(image), width="stretch")
        else:
            draw()
        md_html(f'<div style="margin-top:6px"><span class="badge blue">{version}</span> <span class="badge">{metric}</span></div>')
        st.caption(caption)
    st.write("")


def _metric_chart(idx: int, ylabel: str, color_top: str, key: str, fmt="{:.3f}", lower_better=True):
    names = [r[0] for r in R.MODEL_COMPARISON]
    vals = [r[idx] for r in R.MODEL_COMPARISON]
    colors = [PURPLE if n == "Random Forest" else GREY for n in names]
    charts.show(charts.hbar(names, vals, colors, ylabel, fmt=fmt), key)


def tab_graphs() -> None:
    section_title("Graphs & Visual Results", "Nine graphs drawn from the saved experiment results. Each names its dataset, experiment and metric units.")
    notice("All nine graphs use the <b>final 249-response modelling dataset</b>; each one names its experiment below the chart.", "info")
    st.write("")

    cmp = R.MODEL_COMPARISON
    _frame(1, "Eight-Model MAE Comparison", V249, "MAE, rating points on the 1–5 scale; lower is better; repeated 5-fold × 5",
           "Gradient Boosting (0.536), Random Forest (0.537) and SVR (0.537) are practically tied, ahead of KNN and the linear models; the Dummy baseline is worst. "
           "Random Forest is highlighted because it is the deployed model, not because it is the clear best.",
           lambda: _metric_chart(1, "MAE (rating points, 1–5 scale; lower is better)", PURPLE, "g1"))
    _frame(2, "Eight-Model RMSE Comparison", V249, "RMSE, rating points on the 1–5 scale; lower is better; repeated 5-fold × 5",
           "RMSE shows the same grouping: the top three models are within about 0.005 of each other, so the differences are small compared with the fold-to-fold spread (SD about 0.08–0.09).",
           lambda: _metric_chart(3, "RMSE (rating points, 1–5 scale; lower is better)", PURPLE, "g2"))
    _frame(3, "Eight-Model R² Comparison", V249, "R², unitless; higher is better; repeated 5-fold × 5",
           "No model explains much variance: the best R² is about 0.18. The linear models and the Dummy baseline are near zero or below, so the questionnaire predictors carry limited but real signal.",
           lambda: _metric_chart(5, "R² (unitless; higher is better)", PURPLE, "g3"))

    def g4():
        names = [r[0] for r in R.REPEATED_CV]
        charts.show(charts.vbar_grouped(["MAE", "RMSE"], {n: [r[1], r[2]] for n, r in zip(names, R.REPEATED_CV)},
                                        {"Mean baseline": GREY, "Median baseline": "#8DB4F8", "Random Forest": PURPLE}, "Error (rating points, 1–5 scale)", fmt="{:.3f}"), "g4")
    _frame(4, "Random Forest vs Mean and Median Baseline Models", V249, "MAE and RMSE, rating points; lower is better; repeated 5-fold × 3",
           f"Random Forest's MAE (0.533) is about {R.RF_IMPROVEMENT_PERCENT:.1f}% lower than the mean baseline (0.633) and the median baseline (0.638), so the model beats always predicting the average.", g4)

    def g5():
        labels = [n for n, _, _ in R.SHAP_GLOBAL]
        charts.show(charts.hbar(labels, [v for _, v, _ in R.SHAP_GLOBAL], [PURPLE] * len(labels), "Mean |SHAP| (model-output units, rating points)", fmt="{:.3f}"), "g5")
    _frame(5, "SHAP Global Feature Importance", V249, "Mean absolute SHAP value, rating points; nine model input features only",
           "Independent learning (40.0% of total) and verification (17.5%) dominate, followed by study year (13.8%). This describes how the fitted model uses its inputs; it is not causal. "
           "The direct overreliance target is not an input feature, so it does not appear here.", g5)

    def g6():
        ks = sorted(R.KMEANS_SILHOUETTE)
        charts.show(charts.line(ks, [R.KMEANS_SILHOUETTE[k] for k in ks], BLUE, "Silhouette score (unitless, −1 to 1)", "Number of clusters (K)", height=300), "g6")
    _frame(6, "K-Means Silhouette Score Comparison", V249, "Silhouette score, unitless (higher = better separated); K = 2–6",
           "K = 2 has the highest silhouette (0.362); K = 3–6 are about 0.23–0.24. A value of 0.36 means moderate separation, so the groups are exploratory, not validated student types. "
           "K-Means is separate from the Random Forest.", g6)

    def g7():
        xs = [r[0] for r in R.NOISE]
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            charts.show(charts.multi_line(xs, {"MAE": [r[1] for r in R.NOISE], "RMSE": [r[2] for r in R.NOISE]}, {"MAE": BLUE, "RMSE": PURPLE},
                                          "Error (rating points)", "Noise level (% of predictor SD)", height=300), "g7a")
        with c2:
            charts.show(charts.line(xs, [r[3] for r in R.NOISE], CYAN, "R² (unitless)", "Noise level (% of predictor SD)", height=300), "g7b")
    _frame(7, "Random Forest Noise Robustness Analysis", V249, "MAE/RMSE in rating points, R² unitless; Gaussian noise on standardised test predictors",
           "Performance is essentially unchanged at 0–5% noise (MAE 0.521) and degrades at higher levels (R² falls from 0.225 to 0.177 at 30%). Synthetic noise is only one kind of error and is not added to real student answers.", g7)

    def g8():
        names = [r[0] for r in R.DEEP_LEARNING]
        charts.show(charts.vbar_grouped(["MAE", "RMSE", "R²"], {r[0]: [r[1], r[3], r[5]] for r in R.DEEP_LEARNING}, {names[0]: PURPLE, names[1]: GREY}, "Metric value (MAE/RMSE rating points; R² unitless)", fmt="{:.3f}"), "g8")
    _frame(8, "Deep Learning vs Random Forest (Repeated 5-fold × 3)", V249, "MAE/RMSE in rating points (lower is better), R² unitless (higher is better); identical folds for both models",
           "The neural network has higher error (MAE 0.576 vs 0.533) and lower R² (0.078 vs 0.197) than the Random Forest, so the deep model gave no advantage on this small dataset. It is an experiment and is not deployed.", g8)

    t = R.TARGET_DISTRIBUTION

    def g9():
        charts.show(charts.vbar_grouped(t["bins"], {"Respondents": t["counts"]}, {"Respondents": PINK}, "Number of respondents", fmt="{:d}", height=320), "g9")
    _frame(9, "Direct Overreliance Target Distribution", V249, f"Count of respondents per range of the 1–5 target (n = {t['n']}); mean {t['mean']:.2f}, SD {t['sd']:.2f}",
           "The training target (mean of the seven direct statements, called the Overreliance Target Score here) is centred near 2.7 with most respondents between 2.0 and 3.5; few respondents are at the extremes. "
           "Because most targets sit in a narrow band, there is limited variation for the model to explain.", g9)
