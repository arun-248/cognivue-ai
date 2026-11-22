"""ui/profile.py - Behavioural Insights: learning-habit summary and the exploratory K-Means groups."""

from __future__ import annotations

import streamlit as st

from backend.clustering import CLUSTER_FEATURES, FEATURE_NAMES, cluster_profiles, pca_projection
from backend.questionnaire import CONSTRUCT_LABELS
from ui import charts
from ui.resources import get_models
from ui.results import CONSTRUCT_COLORS, CONSTRUCT_ORDER, SHORT, behaviour_summary
from ui.state import goto
from ui.theme import chart_card, esc, md_html, notice, section_title, stat

GROUP_COLORS = {"You": "#0F8F80", "Cluster 0": "#8DB4F8", "Cluster 1": "#D9CCFF"}


def _constructs_section(result):
    scores = result["construct_scores"]
    section_title("Your clustering inputs", "Your four learning-habit averages (detailed on your Results page) and your AI usage are what K-Means compares.")
    md_html('<div class="grid g4">' + "".join(
        stat(f"{scores[f]:.2f} / 5", CONSTRUCT_LABELS[f], "at or above the midpoint" if scores[f] >= 3.0 else "below the midpoint (3.0)")
        for f in CONSTRUCT_ORDER) + "</div>")


def _cluster_section(result):
    models = get_models()
    profiles = cluster_profiles(models["kmeans_model"], models["kmeans_scaler"])
    silhouette = models["kmeans_metadata"]["selected_silhouette"]
    mine = result["cluster"]["cluster_id"] if result else None

    section_title("Exploratory behavioural groups (K-Means)",
                  "Groups found by the saved K-Means model, which was fitted on the 249 usable study responses.")
    md_html('<div class="grid g4">'
            + stat(str(len(profiles)), "Groups identified", "K = 2 chosen by silhouette")
            + "".join(stat(f"{p['size']} ({p['percent']:.1f}%)", f"Cluster {p['cluster_id']}", "of the 249 respondents") for p in profiles)
            + stat(f"{silhouette:.3f}", "Silhouette score", "moderate separation") + "</div>")
    st.write("")

    if result:
        p = profiles[mine]
        md_html(
            f'<div class="iv-card"><div class="eyebrow">Your closest exploratory cluster</div><h2 style="text-transform:none">Cluster {mine} \u00b7 {esc(p["label"])}</h2>'
            f'<div class="why">{esc(p["description"])} Your own four-construct average is {result["cluster"]["construct_average"]:.2f}. '
            f'The label describes the cluster\'s centre, not you personally, and is not a diagnosis.</div></div>'
        )
        st.write("")

    # table of group averages (from the model centroids)
    head = "".join(f"<th>{esc(FEATURE_NAMES[f])}</th>" for f in CLUSTER_FEATURES)
    rows = ""
    if result:
        frame = result["frame"].iloc[0]
        rows += '<tr class="sel"><td>You</td><td>\u2013</td>' + "".join(f"<td>{float(frame[f]):.2f}</td>" for f in CLUSTER_FEATURES) + "</tr>"
    for p in profiles:
        rows += (f'<tr class="{"sel" if p["cluster_id"] == mine else ""}"><td>Cluster {p["cluster_id"]}: {esc(p["label"])}</td><td>{p["size"]}</td>'
                 + "".join(f"<td>{p['centroid'][f]:.2f}</td>" for f in CLUSTER_FEATURES) + "</tr>")
    md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr><th>Group</th><th>Respondents</th>{head}</tr>{rows}</table>'
            '<p style="margin-top:8px;font-size:.82rem">Group values are the cluster centroids converted back to questionnaire units. Usage frequency and duration are coded 0\u20135 '
            '(frequency: 0 Never, 3 = 3\u20135 days a week, 4 Daily, 5 Multiple times a day; duration: 0 No use, 3 = 31\u201360 minutes, 4 = 1\u20132 hours, 5 More than 2 hours).</p></div>')
    st.write("")
    hi, lo = sorted(profiles, key=lambda q: sum(q["centroid"][f] for f in CLUSTER_FEATURES[:4]), reverse=True)
    gap = sum(hi["centroid"][f] - lo["centroid"][f] for f in CLUSTER_FEATURES[:4]) / 4
    md_html('<div class="card"><h4>How the two groups differ</h4>'
            f'<p>Cluster {hi["cluster_id"]} ({hi["size"]} respondents) averages {sum(hi["centroid"][f] for f in CLUSTER_FEATURES[:4]) / 4:.2f} across the four learning habits, '
            f'while Cluster {lo["cluster_id"]} ({lo["size"]} respondents) averages {sum(lo["centroid"][f] for f in CLUSTER_FEATURES[:4]) / 4:.2f}, a gap of about {gap:.2f} points. '
            f'Cluster {hi["cluster_id"]} also reports slightly more frequent and longer AI use. The groups are found from these six measures only; the overreliance score played no part in forming them.</p></div>')
    st.write("")

    c1, c2 = st.columns(2, gap="large")
    construct_feats = CLUSTER_FEATURES[:4]
    with c1:
        with chart_card("How do the groups compare on the four constructs?"):
            st.caption("Compares the average learning-habit scores of the two groups (and yours): this is what mainly separates them.")
            series = {f"Cluster {p['cluster_id']}": [p["centroid"][f] for f in construct_feats] for p in profiles}
            if result:
                series = {"You": [float(result["frame"].iloc[0][f]) for f in construct_feats], **series}
            charts.show(charts.vbar_grouped([SHORT[f] for f in construct_feats], series, GROUP_COLORS, "Average score (1\u20135)", yrange=[1, 5.4]), "ins_group_constructs")
    with c2:
        with chart_card("How do the groups compare on AI usage?"):
            st.caption("Compares how often and how long each group uses Generative AI, to show whether usage differs alongside learning habits.")
            use_feats = CLUSTER_FEATURES[4:]
            series = {f"Cluster {p['cluster_id']}": [p["centroid"][f] for f in use_feats] for p in profiles}
            if result:
                series = {"You": [float(result["frame"].iloc[0][f]) for f in use_feats], **series}
            charts.show(charts.vbar_grouped(["Usage frequency (0\u20135)", "Usage duration (0\u20135)"], series, GROUP_COLORS, "Average code", yrange=[0, 5.6]), "ins_group_usage")

    with chart_card("Where do the groups sit in the two-dimensional PCA view?"):
        st.caption("Shows the two groups on a flat map built by PCA, so you can see how far apart they are. Far-apart groups are easier to tell apart.")
        proj = pca_projection(models["kmeans_model"], models["kmeans_scaler"], models["kmeans_pca"], result["frame"] if result else None)
        charts.show(charts.pca_scatter(proj["centroids"], [p["label"] for p in profiles], proj["student"], proj["explained_variance"]), "ins_pca")
        st.caption(f"The two components keep {sum(proj['explained_variance']) * 100:.1f}% of the variance. The map shows the group centres and, if you completed the assessment, your own answers.")

    notice(f"K = 2 had the best silhouette score ({silhouette:.2f}), which indicates moderate separation between the groups.", "info")


def page_profile():
    result = st.session_state.get("result")
    section_title("Understand Your Learning Behaviour", "Exploratory groups of students with similar learning habits, and where your answers fall among them.")
    md_html('<div class="card"><h4>What is Behavioural Insights?</h4>'
            "<p>Behavioural Insights explores similarities in students\u2019 self-reported learning habits. K-Means identifies groups with similar patterns, while PCA provides a two-dimensional visualisation of those patterns. "
            "These analyses complement the supervised overreliance prediction but operate separately from it.</p>"
            '<p style="margin-top:8px"><b>Random Forest</b> regression estimates the questionnaire-based overreliance score. <b>K-Means</b> and <b>PCA</b> are exploratory research components and are not used to generate that prediction. '
            'The groups are described as a <i>Stronger</i> and a <i>Developing</i> learning-strategy profile; these are descriptive labels, not validated risk categories or personality types.</p></div>')
    st.write("")
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment to see your own profile. The study-level K-Means groups are shown below.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_profile")
    else:
        _constructs_section(result)
    st.write("")
    try:
        _cluster_section(result)
    except Exception:
        notice("The K-Means group information could not be loaded. Check that the models folder is present.", "warn")
    st.write("")
    c1, c2 = st.columns([1.2, 3])
    with c1:
        st.button("Explore research & experiments", on_click=goto, args=("Research & Experiments",), key="prof_mi")
