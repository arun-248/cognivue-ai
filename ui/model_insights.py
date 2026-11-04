"""ui/model_insights.py - research evaluation. Evidence types are kept separate and labelled."""

from __future__ import annotations

import streamlit as st

from backend import research_data as R
from backend.clustering import CLUSTER_FEATURES, FEATURE_NAMES, cluster_profiles, pca_projection
from backend.evaluation import NOTEBOOK_SNIPPET, load_oof_predictions, oof_metrics
from backend.explainability import FEATURE_LABELS
from ui import charts
from ui.resources import get_models
from ui.theme import card, chart_card, esc, md_html, notice, section_title, stat

BLUE, PURPLE, CYAN, AMBER, GREY = charts.BLUE, charts.PURPLE, charts.CYAN, charts.AMBER, charts.GREY


def table(headers, rows, selected=None) -> None:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join(
        f'<tr class="{"sel" if selected is not None and i == selected else ""}">' + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
        for i, r in enumerate(rows)
    )
    md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr>{head}</tr>{body}</table></div>')


def evidence(*labels) -> None:
    md_html("".join(f'<span class="evidence">{esc(l)}</span>' for l in labels))


def _pm(m, s):
    return f"{m:.4f} \u00b1 {s:.4f}"


def tab_deployed():
    evidence("Final deployed model", "Nested CV", "Repeated 5-fold \u00d7 3", "Training data (descriptive)")
    n = R.NESTED_CV
    md_html('<div class="grid g3">'
            + stat(f'{n["MAE"]:.4f}', "Nested CV MAE", "headline generalisation estimate", BLUE)
            + stat(f'{n["RMSE"]:.4f}', "Nested CV RMSE", "on a 1\u20135 target scale", PURPLE)
            + stat(f'{n["R2"]:.4f}', "Nested CV R\u00b2", "internal estimate", CYAN) + "</div>")
    st.caption("Nested cross-validation on the 151 respondents. It is an internal estimate and is not external validation.")
    st.write("")
    rows = [(m, _pm(a, sa), _pm(b, sb), _pm(c, sc)) for m, a, b, c, sa, sb, sc in R.REPEATED_CV]
    table(["Model", "MAE (mean \u00b1 SD)", "RMSE (mean \u00b1 SD)", "R\u00b2 (mean \u00b1 SD)"], rows, selected=2)
    st.caption("Repeated 5-fold cross-validation, 3 repetitions (15 folds): tuned Random Forest versus simple baselines.")
    st.write("")
    c1, c2 = st.columns(2, gap="large")
    labels = [r[0] for r in R.REPEATED_CV]
    with c1:
        with chart_card("Does the Random Forest beat simple baselines? (MAE, lower is better)"):
            charts.show(charts.hbar(labels, [r[1] for r in R.REPEATED_CV], [GREY, GREY, BLUE], "MAE", errors=[r[4] for r in R.REPEATED_CV], xrange=[0, 0.85]), "mi_dep_mae")
            st.caption("Bars are fold means; whiskers show \u00b1 one standard deviation across folds.")
    with c2:
        with chart_card("How much variance is explained? (R\u00b2, higher is better)"):
            charts.show(charts.hbar(labels, [r[3] for r in R.REPEATED_CV], [GREY, GREY, CYAN], "R\u00b2", errors=[r[6] for r in R.REPEATED_CV], xrange=[-0.35, 0.6]), "mi_dep_r2")
            st.caption("Both baselines have an R\u00b2 close to zero, as expected.")
    st.write("")
    t, p = R.TRAIN_VALIDATION, R.RF_PARAMETERS
    md_html('<div class="grid g2">'
            + card("Improvement over baselines", f"The Random Forest reduced MAE by about {R.RF_IMPROVEMENT_PERCENT:.2f}% compared with the best baseline (the mean baseline).")
            + card("Training versus validation", f"Mean training MAE {t['train_mae']:.3f} versus validation MAE {t['validation_mae']:.3f} (gap {t['gap']:.3f}).")
            + card("Hyperparameter configuration", ", ".join(f"{k} = {v}" for k, v in p.items()))
            + card("Honest reading", "Performance is moderate, not perfect. There is no external validation, and individual predictions can be inaccurate.")
            + "</div>")
    st.write("")
    evidence("Random Forest impurity importance", "Training data (descriptive)")
    try:
        rf = get_models()["random_forest"]
        pairs = sorted(zip(rf.feature_names_in_, rf.feature_importances_), key=lambda x: -x[1])
        with chart_card("Which features does the saved Random Forest split on most? (feature importance)"):
            charts.show(charts.hbar([FEATURE_LABELS[n] for n, _ in pairs], [float(v) for _, v in pairs], [BLUE] * len(pairs),
                                    "Impurity-based importance (sums to 1)", fmt="{:.3f}"), "mi_importance")
            st.caption("Computed from the loaded model. It describes how the fitted forest uses each feature, can favour features with many split points, and is not causal. "
                       "The SHAP ranking is shown separately in the SHAP tab.")
    except Exception:
        notice("Feature importance could not be computed because the models could not be loaded.", "warn")


def tab_models():
    evidence("Candidate comparison", "Repeated 5-fold \u00d7 5 (25 folds)")
    rows = [(m, _pm(a, sa), _pm(b, sb), _pm(c, sc)) for m, a, sa, b, sb, c, sc in R.MODEL_COMPARISON]
    table(["Model", "MAE (mean \u00b1 SD)", "RMSE (mean \u00b1 SD)", "R\u00b2 (mean \u00b1 SD)"], rows, selected=0)
    st.caption("Eight regression models, 151 respondents, 9 features, sorted by MAE. The Random Forest was selected, then tuned.")
    st.write("")
    names = [r[0] for r in R.MODEL_COMPARISON]
    colors = [BLUE if n == "Random Forest" else GREY for n in names]
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        with chart_card("MAE (lower is better)"):
            charts.show(charts.hbar(names, [r[1] for r in R.MODEL_COMPARISON], colors, "MAE", errors=[r[2] for r in R.MODEL_COMPARISON], xrange=[0, 0.85]), "mi_models_mae")
    with c2:
        with chart_card("RMSE (lower is better)"):
            charts.show(charts.hbar(names, [r[3] for r in R.MODEL_COMPARISON], colors, "RMSE", errors=[r[4] for r in R.MODEL_COMPARISON], xrange=[0, 1.0]), "mi_models_rmse")
    with c3:
        with chart_card("R\u00b2 (higher is better)"):
            charts.show(charts.hbar(names, [r[5] for r in R.MODEL_COMPARISON], colors, "R\u00b2", errors=[r[6] for r in R.MODEL_COMPARISON], xrange=[-0.4, 0.6]), "mi_models_r2")
    st.write("")
    notice("The Random Forest had the lowest MAE and RMSE and the highest R\u00b2 among the eight candidates. This 25-fold comparison used a different cross-validation design from "
           "the 15-fold validation of the final tuned model, so figures must not be compared across tables or mixed with the nested cross-validation result.", "info")


def tab_deep_learning():
    evidence("Experimental model \u2013 not deployed", "Repeated 5-fold \u00d7 3 (15 folds)")
    rows = [(m, _pm(a, sa), _pm(b, sb), _pm(c, sc)) for m, a, sa, b, sb, c, sc in R.DEEP_LEARNING]
    table(["Model", "MAE (mean \u00b1 SD)", "RMSE (mean \u00b1 SD)", "R\u00b2 (mean \u00b1 SD)"], rows, selected=0)
    st.caption(f"Neural network: {R.DL_ARCHITECTURE}.")
    st.write("")
    names = [r[0] for r in R.DEEP_LEARNING]
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("Which model has the lower error? (MAE)"):
            charts.show(charts.hbar(names, [r[1] for r in R.DEEP_LEARNING], [BLUE, PURPLE], "MAE (lower is better)", errors=[r[2] for r in R.DEEP_LEARNING], xrange=[0, 1.1]), "mi_dl_mae")
    with c2:
        with chart_card("Which model explains more variance? (R\u00b2)"):
            charts.show(charts.hbar(names, [r[5] for r in R.DEEP_LEARNING], [BLUE, PURPLE], "R\u00b2 (higher is better)", errors=[r[6] for r in R.DEEP_LEARNING], xrange=[-1.2, 0.7]), "mi_dl_r2")
    st.write("")
    notice("The Random Forest performed better. The neural network is a <b>comparative experiment</b>, not the deployed prediction model; on 151 respondents it had a negative R\u00b2 "
           "(worse than predicting the average). This is internal repeated cross-validation, not an independent external test.", "info")


def tab_shap():
    evidence("Final deployed model", "Training data (descriptive)")
    charts_labels = [n for n, _, _ in R.SHAP_GLOBAL]
    with chart_card("Which features influence the model most, on average? (mean |SHAP|)"):
        charts.show(charts.hbar(charts_labels, [v for _, v, _ in R.SHAP_GLOBAL], [PURPLE] * len(charts_labels), "Mean absolute SHAP value", fmt="{:.3f}"), "mi_shap")
    st.write("")
    table(["Rank", "Feature", "Mean |SHAP|", "Share"], [(i, n, f"{v:.6f}", f"{p:.2f}%") for i, (n, v, p) in enumerate(R.SHAP_GLOBAL, 1)])
    st.write("")
    notice("SHAP TreeExplainer values (shap 0.54.1 in the Colab experiment; the app uses a compatible version) were calculated for the 151 training respondents; the "
           "baseline + contributions reconstruction matched the model output with a maximum error of 0.0. This global ranking is descriptive, is based on the training data, "
           "and describes the fitted model rather than causal effects. Individual explanations are on the Why This Result? page.", "info")


def tab_kmeans():
    evidence("Exploratory clustering", "Derived from the saved K-Means model")
    models = get_models()
    meta = models["kmeans_metadata"]
    profiles = cluster_profiles(models["kmeans_model"], models["kmeans_scaler"])
    sil = {int(k): v for k, v in meta["silhouette_scores"].items()}
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("Which number of clusters separates best? (silhouette)"):
            ks = list(sil.keys())
            charts.show(charts.line(ks, [sil[k] for k in ks], BLUE, "Silhouette score", "Number of clusters (K)"), "mi_km_sil")
            st.caption(f"K = 2 had the best silhouette score ({sil[2]:.4f}). Scores near 0.5 or above would indicate stronger separation.")
    with c2:
        with chart_card("How are the 151 respondents split across clusters?"):
            charts.show(charts.hbar([f"Cluster {p['cluster_id']}" for p in profiles], [p["size"] for p in profiles], [CYAN, PURPLE], "Respondents", fmt="{:.0f}"), "mi_km_dist")
            st.caption(" \u00b7 ".join(f"Cluster {p['cluster_id']}: {p['size']} ({p['percent']:.2f}%)" for p in profiles))
    st.write("")
    head = "".join(f"<th>{esc(FEATURE_NAMES[f])}</th>" for f in CLUSTER_FEATURES)
    rows = [f"<tr><td>Cluster {p['cluster_id']}: {esc(p['label'])}</td><td>{p['size']} ({p['percent']:.1f}%)</td>"
            + "".join(f"<td>{p['centroid'][f]:.2f}</td>" for f in CLUSTER_FEATURES) + "</tr>" for p in profiles]
    md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr><th>Group</th><th>Respondents</th>{head}</tr>{"".join(rows)}</table></div>')
    st.caption("Centroids are converted back to questionnaire units. Group labels are derived from the centroids (the group with the higher construct centroids is the 'stronger' group).")
    st.write("")
    table(["Cluster", "Respondents", "Mean predicted overreliance", "Mean support areas", "Interpretation"],
          [(c, n, f"{p:.4f}", f"{s:.4f}", lab) for c, n, p, s, lab in R.KMEANS_PROFILE_SUMMARY])
    st.caption("Mean predicted overreliance and the mean number of construct areas below 3.0, per cluster (from the Colab analysis).")
    st.write("")
    proj = pca_projection(models["kmeans_model"], models["kmeans_scaler"], models["kmeans_pca"])
    with chart_card("Where are the two group centroids in the saved PCA view?"):
        charts.show(charts.pca_scatter(proj["centroids"], [p["label"] for p in profiles], None, proj["explained_variance"]), "mi_km_pca")
        st.caption(f"Two principal components keep {sum(proj['explained_variance']) * 100:.2f}% of the variance. Respondent-level points are not published.")
    notice(f"Six clustering features were used, the target was excluded and a StandardScaler was applied (random_state {meta['random_state']}). The silhouette indicates moderate/limited "
           "separation, so these are exploratory groupings, <b>not</b> validated student types or diagnoses.", "warn")


def tab_experiments():
    evidence("Noise: hold-out test", "CTGAN: five-fold, real test respondents")
    st.markdown("**Noise robustness (Random Forest)**")
    xs = [r[0] for r in R.NOISE]
    cols = st.columns(3, gap="medium")
    for col, (name, idx, color) in zip(cols, [("MAE (lower is better)", 1, BLUE), ("RMSE (lower is better)", 2, PURPLE), ("R\u00b2 (higher is better)", 3, CYAN)]):
        with col:
            with chart_card(name):
                charts.show(charts.line(xs, [r[idx] for r in R.NOISE], color, name.split(" ")[0], "Noise level", xtick_text=[f"{x}%" for x in xs], height=230), f"mi_noise_{idx}")
    table(["Noise", "MAE", "RMSE", "R\u00b2"], [(f"{n}%", f"{a:.4f}", f"{b:.4f}", f"{c:.4f}") for n, a, b, c in R.NOISE])
    notice("Gaussian noise was added to the <b>standardised test predictors</b> while training data stayed clean. The Random Forest was relatively stable at low noise "
           "(0\u20135%) and degraded at higher levels (R\u00b2 0.223 at 30%). Synthetic noise does not represent all real-world errors, and no noise is added to your own answers in this app.", "info")
    st.write("")
    st.markdown("**CTGAN synthetic-data augmentation**")
    rows = [(m, f"{a:.4f}", f"{b:.4f}", f"{c:.4f}") for m, (a, b, c) in R.GAN.items()]
    table(["Model", "MAE", "RMSE", "R\u00b2"], rows, selected=0)
    names = list(R.GAN.keys())
    with chart_card("Did synthetic CTGAN data improve the model?"):
        real, gan = R.GAN[names[0]], R.GAN[names[1]]
        charts.show(charts.vbar_grouped(["MAE", "RMSE", "R\u00b2"], {names[0]: list(real), names[1]: list(gan)}, {names[0]: BLUE, names[1]: GREY}, "Metric value", fmt="{:.3f}"), "mi_gan")
    g = R.GAN_FACTS
    notice(f"CTGAN was trained inside each of five folds with synthetic training data matching the real training size, and test respondents stayed real. {g['synthetic_records']} synthetic records and "
           f"{g['quality_measurements']} quality measurements were generated. GAN augmentation increased MAE by about {g['mae_increase_percent']}% and did <b>not</b> improve the model, so the "
           "real-data-only Random Forest remains final. Synthetic data is never used in the real evaluation shown elsewhere.", "warn")


def tab_interventions():
    evidence("Dataset-level rule application", "Heuristic threshold")
    with chart_card("How many of the 151 respondents were identified for support in each dimension?"):
        charts.show(charts.hbar([n for n, _ in R.INTERVENTION_SUMMARY], [c for _, c in R.INTERVENTION_SUMMARY], [AMBER] * 4,
                                "Respondents with a construct score below 3.0", fmt="{:.0f}"), "mi_iv")
    table(["Construct", "Respondents identified for support"], [(n, c) for n, c in R.INTERVENTION_SUMMARY])
    notice("Support is suggested when a construct score is below the neutral midpoint of 3.0, a heuristic design choice rather than a validated cut-off. Other respondents receive "
           "maintenance recommendations. Intervention effectiveness has not been experimentally validated.", "warn")


def tab_predictions():
    evidence("Out-of-fold predictions", "Genuine notebook export only")
    df, status = load_oof_predictions()
    if df is None:
        notice("<b>Actual vs predicted and residual plots are not available yet.</b><br>They need genuine out-of-fold predictions from your notebook, and none are bundled with the app, "
               f"so nothing is shown rather than inventing data ({esc(status)}). Run the cell below in your Colab notebook, then place the downloaded "
               "<code>evaluation_predictions.csv</code> next to <code>app.py</code>.", "info")
        st.code(NOTEBOOK_SNIPPET, language="python")
        st.caption("The file contains only the actual and predicted scores (no respondent identifiers). Use the same cross-validation settings as your experiments.")
        return
    m = oof_metrics(df)
    md_html('<div class="grid g4">' + stat(str(m["n"]), "Predictions", "out-of-fold")
            + stat(f'{m["MAE"]:.4f}', "MAE", "from this file", BLUE) + stat(f'{m["RMSE"]:.4f}', "RMSE", "from this file", PURPLE)
            + stat(f'{m["R2"]:.4f}', "R\u00b2", "from this file", CYAN) + "</div>")
    st.write("")
    resid = df["Actual"] - df["Predicted"]
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with chart_card("How close are out-of-fold predictions to the actual scores?"):
            charts.show(charts.scatter_oof(df["Actual"], df["Predicted"]), "mi_oof_scatter")
    with c2:
        with chart_card("Are errors balanced across the predicted range?"):
            charts.show(charts.scatter_residuals(df["Predicted"], resid), "mi_oof_resid")
    with chart_card("How are the residuals distributed?"):
        charts.show(charts.histogram(resid, "Residual (actual \u2212 predicted)"), "mi_oof_hist")
    notice(f"Mean residual {m['mean_residual']:+.3f}. These metrics come from the supplied out-of-fold file only; they are a different evaluation from the nested cross-validation, "
           "repeated cross-validation and noise results, and must not be mixed with them.", "info")


def tab_guide():
    table(["Evidence type", "Used for"], [(esc(a), esc(b)) for a, b in R.EVIDENCE_GUIDE])
    st.write("")
    notice("Results from different evaluations answer different questions and use different splits, so they are never combined or averaged on this site. "
           "Training-data results are descriptive; none of the results is external validation.", "warn")


def page_model_insights():
    section_title("Model Insights", "For faculty and researchers: the final deployed model is shown first, then experimental models, each labelled with its type of evidence.")
    notice("<b>Key caution.</b> Performance is moderate and based on 151 respondents with internal validation only. The estimate supports reflection and research; it is not a diagnosis.", "warn")
    st.write("")
    names = ["Deployed model", "Model comparison", "Deep Learning", "SHAP", "K-Means", "Noise & CTGAN", "Interventions", "Predictions & residuals", "Evidence guide"]
    tabs = st.tabs(names)
    fns = [tab_deployed, tab_models, tab_deep_learning, tab_shap, tab_kmeans, tab_experiments, tab_interventions, tab_predictions, tab_guide]
    for tab, fn in zip(tabs, fns):
        with tab:
            try:
                fn()
            except Exception:
                notice("This section could not be displayed. Check that the models folder is present and the app starts without errors.", "warn")
