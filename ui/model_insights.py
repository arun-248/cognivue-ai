"""ui/model_insights.py - research evaluation charts and tables (verified experiment outputs only)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from backend import research_data as R
from ui.theme import (C_AMBER, C_BLUE, C_CARD, C_CYAN, C_MUTED, C_PURPLE, C_TEXT, card, chart_card, esc,
                      md_html, notice, section_title, show_fig, stat, themed_fig)

BASE_DIR = Path(__file__).resolve().parent.parent
GREY = "#B9C9E6"


def table(headers, rows, selected=None) -> None:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join(
        f'<tr class="{"sel" if selected is not None and i == selected else ""}">' + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
        for i, r in enumerate(rows)
    )
    md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr>{head}</tr>{body}</table></div>')


def hbar(labels, values, colors, xlabel, title=None, fmt="{:.3f}", errors=None, xlim=None):
    fig, ax = themed_fig(7.5, 0.5 * len(labels) + 1.3)
    ax.barh(labels, values, color=colors, height=0.6, xerr=errors, ecolor="#425B82", capsize=3)
    ax.grid(axis="y", visible=False)
    ax.invert_yaxis()
    span = max(max(values) - min(0, min(values)), 1e-6)
    for y, v in enumerate(values):
        off = (errors[y] if errors is not None else 0) + 0.015 * span
        ax.text(v + (off if v >= 0 else -off), y, fmt.format(v), va="center", ha="left" if v >= 0 else "right", color=C_TEXT, fontsize=8.5)
    if min(values) < 0:
        ax.axvline(0, color=C_MUTED, linewidth=1)
    if xlim:
        ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title, fontsize=11, loc="left", fontweight="bold")
    show_fig(fig)


def tab_validation():
    n = R.NESTED_CV
    md_html('<div class="grid g3">'
            + stat(f'{n["MAE"]:.4f}', "Nested CV MAE", "headline generalisation estimate", C_BLUE)
            + stat(f'{n["RMSE"]:.4f}', "Nested CV RMSE", "on a 1\u20135 target scale", C_PURPLE)
            + stat(f'{n["R2"]:.4f}', "Nested CV R\u00b2", "internal estimate", C_CYAN) + "</div>")
    st.write("")
    rows = [(m, f"{a:.4f} \u00b1 {sa:.4f}", f"{b:.4f} \u00b1 {sb:.4f}", f"{c:.4f} \u00b1 {sc:.4f}") for m, a, b, c, sa, sb, sc in R.REPEATED_CV]
    table(["Model", "MAE (mean \u00b1 SD)", "RMSE (mean \u00b1 SD)", "R\u00b2 (mean \u00b1 SD)"], rows, selected=2)
    st.caption("Repeated 5-fold cross-validation, 3 repetitions (15 folds).")
    st.write("")
    c1, c2 = st.columns(2, gap="large")
    labels = [r[0] for r in R.REPEATED_CV]
    with c1:
        with chart_card("Does the Random Forest beat simple baselines? (MAE, lower is better)"):
            hbar(labels, [r[1] for r in R.REPEATED_CV], [GREY, GREY, C_BLUE], "MAE", errors=[r[4] for r in R.REPEATED_CV])
    with c2:
        with chart_card("How much variance is explained? (R\u00b2, higher is better)"):
            hbar(labels, [r[3] for r in R.REPEATED_CV], [GREY, GREY, C_CYAN], "R\u00b2", errors=[r[6] for r in R.REPEATED_CV])
    st.write("")
    t = R.TRAIN_VALIDATION
    md_html('<div class="grid g2">'
            + card("Improvement over baselines", f"The Random Forest reduced MAE by about {R.RF_IMPROVEMENT_PERCENT:.2f}% compared with the best baseline (the mean baseline).")
            + card("Training versus validation", f"Mean training MAE {t['train_mae']:.3f} versus validation MAE {t['validation_mae']:.3f} (gap {t['gap']:.3f}), so the model fits its training data somewhat better than new data.")
            + "</div>")
    st.write("")
    notice("<b>Interpretation.</b> Performance is moderate, not perfect. These are internal cross-validation results on the same 151 respondents; "
           "no external validation on an independent student population has been done, and individual predictions can be inaccurate. "
           "The nested CV figures are the stronger headline estimate; the repeated-CV results are not independent validation.", "warn")


def tab_models():
    rows = [(m, f"{a:.4f} \u00b1 {sa:.4f}", f"{b:.4f} \u00b1 {sb:.4f}", f"{c:.4f} \u00b1 {sc:.4f}") for m, a, sa, b, sb, c, sc in R.MODEL_COMPARISON]
    table(["Model", "MAE (mean \u00b1 SD)", "RMSE (mean \u00b1 SD)", "R\u00b2 (mean \u00b1 SD)"], rows, selected=0)
    st.caption("Repeated 5-fold cross-validation, 5 repetitions (25 folds), 151 respondents, 9 features. Sorted by MAE.")
    st.write("")
    names = [r[0] for r in R.MODEL_COMPARISON]
    colors = [C_BLUE if n == "Random Forest" else GREY for n in names]
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("Which model has the lowest error? (MAE)"):
            hbar(names, [r[1] for r in R.MODEL_COMPARISON], colors, "MAE (lower is better)", errors=[r[2] for r in R.MODEL_COMPARISON])
    with c2:
        with chart_card("Which model explains the most variance? (R\u00b2)"):
            hbar(names, [r[5] for r in R.MODEL_COMPARISON], colors, "R\u00b2 (higher is better)", errors=[r[6] for r in R.MODEL_COMPARISON])
    st.write("")
    notice("The Random Forest had the lowest MAE and RMSE and the highest R\u00b2 among the eight candidates. This 25-fold comparison used a different "
           "cross-validation design from the 15-fold validation in the first tab, so figures should not be compared across tables.", "info")
    p = R.RF_PARAMETERS
    md_html(card("Final tuned Random Forest parameters",
                 f"n_estimators = {p['n_estimators']}, max_depth = {p['max_depth']}, max_features = {p['max_features']}, "
                 f"max_samples = {p['max_samples']}, min_samples_leaf = {p['min_samples_leaf']}, min_samples_split = {p['min_samples_split']}."))


def tab_deep_learning():
    rows = [(m, f"{a:.4f} \u00b1 {sa:.4f}", f"{b:.4f} \u00b1 {sb:.4f}", f"{c:.4f} \u00b1 {sc:.4f}") for m, a, sa, b, sb, c, sc in R.DEEP_LEARNING]
    table(["Model", "MAE (mean \u00b1 SD)", "RMSE (mean \u00b1 SD)", "R\u00b2 (mean \u00b1 SD)"], rows, selected=0)
    st.caption(f"Repeated 5-fold cross-validation, 3 repetitions (15 folds). Neural network: {R.DL_ARCHITECTURE}.")
    st.write("")
    names = [r[0] for r in R.DEEP_LEARNING]
    colors = [C_BLUE, C_PURPLE]
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("Which model has the lower error? (MAE)"):
            hbar(names, [r[1] for r in R.DEEP_LEARNING], colors, "MAE (lower is better)", errors=[r[2] for r in R.DEEP_LEARNING])
    with c2:
        with chart_card("Which model explains more variance? (R\u00b2)"):
            hbar(names, [r[5] for r in R.DEEP_LEARNING], colors, "R\u00b2 (higher is better)", errors=[r[6] for r in R.DEEP_LEARNING])
    st.write("")
    notice("The Random Forest performed better. The neural network is a <b>comparative experiment</b>, not the deployed prediction model; on this small "
           "dataset (151 respondents) it had a negative R\u00b2, meaning it did worse than predicting the average. This is an internal repeated cross-validation, "
           "not an independent external test.", "info")


def tab_kmeans():
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("Which number of clusters separates best? (silhouette)"):
            ks = list(R.KMEANS_SILHOUETTE.keys())
            fig, ax = themed_fig(6, 3.4)
            ax.plot(ks, [R.KMEANS_SILHOUETTE[k] for k in ks], marker="o", color=C_BLUE)
            ax.scatter([2], [R.KMEANS_SILHOUETTE[2]], s=140, color=C_AMBER, zorder=5)
            ax.set_xticks(ks)
            ax.set_xlabel("Number of clusters (K)")
            ax.set_ylabel("Silhouette score")
            for k in ks:
                ax.text(k, R.KMEANS_SILHOUETTE[k] + 0.012, f"{R.KMEANS_SILHOUETTE[k]:.3f}", ha="center", fontsize=8, color=C_TEXT)
            show_fig(fig)
    with c2:
        with chart_card("How are the 151 respondents split across clusters?"):
            hbar([f"Cluster {c}" for c, _, _ in R.KMEANS_DISTRIBUTION], [n for _, n, _ in R.KMEANS_DISTRIBUTION],
                 [C_CYAN, C_PURPLE], "Respondents", fmt="{:.0f}")
    st.write("")
    rows = []
    for f in ["independent_learning_score", "verification_score", "metacognition_score", "learning_benefit_score", "usage_frequency_encoded", "usage_time_encoded"]:
        rows.append((f.replace("_", " ").replace(" encoded", "").replace(" score", "").title(),
                     f'{R.KMEANS_FEATURE_MEANS[0][f]:.3f}', f'{R.KMEANS_FEATURE_MEANS[1][f]:.3f}'))
    table(["Clustering feature", "Cluster 0 mean", "Cluster 1 mean"], rows)
    st.write("")
    table(["Cluster", "Respondents", "Mean predicted overreliance", "Mean support areas", "Interpretation"],
          [(c, n, f"{p:.4f}", f"{s:.4f}", lab) for c, n, p, s, lab in R.KMEANS_PROFILE_SUMMARY])
    st.write("")
    notice(f"K = 2 had the best silhouette score ({R.KMEANS_SILHOUETTE[2]:.4f}); six clustering features were used, the target was excluded, and a "
           f"StandardScaler was applied. PCA explained variance was {R.PCA_EXPLAINED_VARIANCE:.4f}. The silhouette indicates moderate/limited separation, "
           "so these are exploratory groupings, <b>not</b> established student personality types or diagnoses.", "warn")


def tab_noise():
    xs = [r[0] for r in R.NOISE]
    fig_cols = st.columns(3, gap="medium")
    series = [("MAE", 1, C_BLUE, "lower is better"), ("RMSE", 2, C_PURPLE, "lower is better"), ("R\u00b2", 3, C_CYAN, "higher is better")]
    for col, (name, idx, color, hint) in zip(fig_cols, series):
        with col:
            with chart_card(f"How does {name} change with noise?"):
                fig, ax = themed_fig(4.2, 3.2)
                ax.plot(xs, [r[idx] for r in R.NOISE], marker="o", color=color)
                ax.set_xticks(xs)
                ax.set_xticklabels([f"{x}%" for x in xs])
                ax.set_xlabel("Noise level")
                ax.set_ylabel(f"{name} ({hint})")
                show_fig(fig)
    st.write("")
    table(["Noise", "MAE", "RMSE", "R\u00b2"], [(f"{n}%", f"{a:.4f}", f"{b:.4f}", f"{c:.4f}") for n, a, b, c in R.NOISE])
    st.write("")
    notice("Gaussian noise was added to the <b>standardised test predictors</b> while training data stayed clean. The Random Forest was relatively stable at low "
           "noise (0\u20135%) and degraded at higher levels (R\u00b2 0.223 at 30%). Synthetic Gaussian noise does not represent all real-world errors, and no noise is "
           "ever added to your own answers in this app.", "info")


def tab_gan():
    rows = [(m, f"{a:.4f}", f"{b:.4f}", f"{c:.4f}") for m, (a, b, c) in R.GAN.items()]
    table(["Model", "MAE", "RMSE", "R\u00b2"], rows, selected=0)
    st.write("")
    with chart_card("Did synthetic CTGAN data improve the model?"):
        names = list(R.GAN.keys())
        fig, ax = themed_fig(7.5, 3.5)
        x = np.arange(3)
        real, gan = R.GAN[names[0]], R.GAN[names[1]]
        ax.bar(x - 0.18, real, width=0.34, color=C_BLUE, label=names[0])
        ax.bar(x + 0.18, gan, width=0.34, color="#8FA6C9", label=names[1])
        for i in range(3):
            ax.text(x[i] - 0.18, real[i] + 0.012, f"{real[i]:.3f}", ha="center", color=C_TEXT, fontsize=8)
            ax.text(x[i] + 0.18, gan[i] + 0.012, f"{gan[i]:.3f}", ha="center", color=C_TEXT, fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(["MAE", "RMSE", "R\u00b2"])
        ax.grid(axis="x", visible=False)
        ax.legend(facecolor=C_CARD, edgecolor="#C8D9F0", labelcolor=C_TEXT, fontsize=8)
        show_fig(fig)
    g = R.GAN_FACTS
    notice(f"CTGAN was trained inside each of five folds, with synthetic training data matching the real training size, and test respondents stayed real. "
           f"{g['synthetic_records']} synthetic records and {g['quality_measurements']} quality measurements were generated. GAN augmentation increased MAE by about "
           f"{g['mae_increase_percent']}% and did <b>not</b> improve the model, so the real-data-only Random Forest remains the final prediction model.", "warn")


def tab_shap():
    with chart_card("Which features influence the model most, on average? (mean |SHAP|)"):
        hbar([n for n, _, _ in R.SHAP_GLOBAL], [v for _, v, _ in R.SHAP_GLOBAL],
             [C_PURPLE] * len(R.SHAP_GLOBAL), "Mean absolute SHAP value", fmt="{:.3f}")
    st.write("")
    table(["Rank", "Feature", "Mean |SHAP|", "Share"], [(i, n, f"{v:.6f}", f"{p:.2f}%") for i, (n, v, p) in enumerate(R.SHAP_GLOBAL, 1)])
    st.write("")
    notice("SHAP TreeExplainer (shap 0.54.1 in the Colab experiment) values were calculated for the 151 training respondents; reconstruction "
           "(baseline + contributions) matched the model output with maximum error 0.0. These global results are descriptive, are based on the training data, and "
           "describe the fitted model rather than causal effects.", "info")


def tab_interventions():
    with chart_card("How many of the 151 respondents were identified for support in each dimension?"):
        hbar([n for n, _ in R.INTERVENTION_SUMMARY], [c for _, c in R.INTERVENTION_SUMMARY], [C_AMBER] * 4,
             "Respondents with a construct score below 3.0", fmt="{:.0f}")
    st.write("")
    table(["Construct", "Respondents identified for support"], [(n, c) for n, c in R.INTERVENTION_SUMMARY])
    st.write("")
    notice("Support is suggested when a construct score is below the neutral midpoint of 3.0, a heuristic design choice rather than a validated cut-off. "
           "Other respondents receive maintenance recommendations. Intervention effectiveness has not been experimentally validated.", "warn")


def tab_predictions():
    path = BASE_DIR / "evaluation_predictions.csv"
    ev = None
    if path.exists():
        try:
            ev = pd.read_csv(path)
        except Exception:
            ev = None
    cols = {c.lower(): c for c in ev.columns} if ev is not None else {}
    if ev is None or "actual" not in cols or "predicted" not in cols:
        notice("<b>Actual vs predicted and residual plots</b><br>These need real held-out predictions, and none are bundled with the app, so nothing is shown "
               "rather than inventing data. Export <code>evaluation_predictions.csv</code> with columns <code>Actual</code> and <code>Predicted</code> from your "
               "notebook into the project folder to enable them.", "info")
        return
    actual = ev[cols["actual"]].astype(float).to_numpy()
    pred = ev[cols["predicted"]].astype(float).to_numpy()
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("How close are predictions to actual scores?"):
            fig, ax = themed_fig(5, 4)
            ax.scatter(actual, pred, s=22, color=C_BLUE, alpha=0.7)
            ax.plot([1, 5], [1, 5], color=C_CYAN, linestyle="--", linewidth=1.2)
            ax.set_xlabel("Actual")
            ax.set_ylabel("Predicted")
            show_fig(fig)
    with c2:
        with chart_card("Are errors balanced across the range?"):
            fig, ax = themed_fig(5, 4)
            ax.scatter(pred, actual - pred, s=22, color=C_PURPLE, alpha=0.7)
            ax.axhline(0, color=C_CYAN, linestyle="--", linewidth=1.2)
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Residual (actual \u2212 predicted)")
            show_fig(fig)


def page_model_insights():
    section_title("Model Insights", "For faculty and researchers: how the deployed model performs and what the supporting experiments show.")
    notice("<b>Key caution.</b> Performance is moderate and based on 151 respondents with internal validation only. The estimate supports reflection and research; "
           "it is not a diagnosis.", "warn")
    st.write("")
    tabs = st.tabs(["Validation & baselines", "Model comparison", "Deep Learning", "K-Means", "Noise robustness",
                    "CTGAN", "SHAP ranking", "Interventions", "Predictions & residuals"])
    for tab, fn in zip(tabs, [tab_validation, tab_models, tab_deep_learning, tab_kmeans, tab_noise,
                              tab_gan, tab_shap, tab_interventions, tab_predictions]):
        with tab:
            fn()