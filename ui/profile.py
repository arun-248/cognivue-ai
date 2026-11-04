"""ui/profile.py - Behavioural Insights: learning-habit summary and the exploratory K-Means groups."""

from __future__ import annotations

import streamlit as st

from backend.clustering import CLUSTER_FEATURES, FEATURE_NAMES, cluster_profiles, pca_projection
from backend.questionnaire import CONSTRUCT_ITEMS, CONSTRUCT_LABELS
from ui import charts
from ui.resources import get_models
from ui.results import CONSTRUCT_COLORS, CONSTRUCT_ORDER, SHORT, behaviour_summary
from ui.state import goto
from ui.theme import chart_card, esc, md_html, notice, section_title, stat

DESCRIPTIONS = {
    "independent_learning_score": "How often you try problems yourself, develop your own ideas, and re-attempt problems after seeing an AI solution.",
    "verification_score": "How often you check AI-generated information against reliable sources and look for errors, bias or unsupported claims.",
    "metacognition_score": "How well you notice what you know and do not know, test yourself without AI, and change strategy when AI is not helping.",
    "learning_benefit_score": "How strongly you feel Generative AI supports your understanding, recall and long-term learning.",
}
GROUP_COLORS = {"You": "#0F8F80", "Cluster 0": "#8DB4F8", "Cluster 1": "#D9CCFF"}


def _constructs_section(result):
    scores = result["construct_scores"]
    section_title("Your learning profile", "A plain-language reading of your own answers.")
    md_html(f'<div class="sumbox">{esc(behaviour_summary(scores, result["labels"]))}</div>')
    st.write("")
    md_html('<div class="grid g4">' + "".join(
        stat(f"{scores[f]:.2f} / 5", CONSTRUCT_LABELS[f], "at or above the midpoint" if scores[f] >= 3.0 else "below the midpoint (3.0)")
        for f in CONSTRUCT_ORDER) + "</div>")
    st.write("")
    c1, c2 = st.columns([1.1, 1], gap="large")
    with c1:
        with chart_card("What does my learning-behaviour pattern look like?"):
            charts.show(charts.radar([SHORT[f] for f in CONSTRUCT_ORDER], {"You": [scores[f] for f in CONSTRUCT_ORDER]}, {"You": "#0F8F80"}), "ins_radar")
            st.caption("Self-reported averages on a 1\u20135 scale; the dashed ring is the neutral midpoint (3.0), a heuristic.")
    with c2:
        bars = []
        for f, color in zip(CONSTRUCT_ORDER, CONSTRUCT_COLORS):
            v = scores[f]
            bars.append(
                f'<div class="mb-row"><div class="top"><span><b>{esc(CONSTRUCT_LABELS[f])}</b></span><span>{v:.2f} / 5</span></div>'
                f'<div class="minibar"><div style="width:{(v - 1) / 4 * 100:.0f}%;background:{color}"></div></div>'
                f'<div style="color:#425B82;font-size:.8rem;margin-top:5px">{esc(DESCRIPTIONS[f])}</div></div>'
            )
        md_html(f'<div class="card"><h4>The four constructs</h4>{"".join(bars)}</div>')
    with st.expander("What do the four constructs measure?"):
        for f in CONSTRUCT_ORDER:
            st.markdown(f"**{CONSTRUCT_LABELS[f]}** ({len(CONSTRUCT_ITEMS[f])} statements). {DESCRIPTIONS[f]}")
        st.caption("Each score is the simple average of its statements. Q36 and Q38 are kept separate in the study and are not part of these scores.")


def _cluster_section(result):
    models = get_models()
    profiles = cluster_profiles(models["kmeans_model"], models["kmeans_scaler"])
    silhouette = models["kmeans_metadata"]["selected_silhouette"]
    mine = result["cluster"]["cluster_id"] if result else None

    section_title("Exploratory behavioural groups (K-Means)",
                  "Kept separate from your supervised score. The groups come from the saved K-Means model fitted on the 151 study respondents.")
    md_html('<div class="grid g4">'
            + stat(str(len(profiles)), "Groups identified", "K = 2 chosen by silhouette")
            + "".join(stat(f"{p['size']} ({p['percent']:.1f}%)", f"Cluster {p['cluster_id']}", "respondents in the study") for p in profiles)
            + stat(f"{silhouette:.3f}", "Silhouette score", "moderate separation") + "</div>")
    st.write("")

    if result:
        p = profiles[mine]
        md_html(
            f'<div class="iv-card"><div class="eyebrow">Your closest group</div><h2 style="text-transform:none">Cluster {mine} \u00b7 {esc(p["label"])}</h2>'
            f'<div class="why">{esc(p["description"])} Your own four-construct average is {result["cluster"]["construct_average"]:.2f}. '
            f'The group label is derived from the group\'s centroid, so it describes the group, not you personally.</div></div>'
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

    c1, c2 = st.columns(2, gap="large")
    construct_feats = CLUSTER_FEATURES[:4]
    with c1:
        with chart_card("How do the groups compare on the four constructs?"):
            series = {f"Cluster {p['cluster_id']}": [p["centroid"][f] for f in construct_feats] for p in profiles}
            if result:
                series = {"You": [float(result["frame"].iloc[0][f]) for f in construct_feats], **series}
            charts.show(charts.vbar_grouped([SHORT[f] for f in construct_feats], series, GROUP_COLORS, "Average score (1\u20135)", yrange=[1, 5.4]), "ins_group_constructs")
            st.caption("Cluster 0 had higher average scores than Cluster 1 on all four constructs.")
    with c2:
        with chart_card("How do the groups compare on AI usage?"):
            use_feats = CLUSTER_FEATURES[4:]
            series = {f"Cluster {p['cluster_id']}": [p["centroid"][f] for f in use_feats] for p in profiles}
            if result:
                series = {"You": [float(result["frame"].iloc[0][f]) for f in use_feats], **series}
            charts.show(charts.vbar_grouped(["Usage frequency (0\u20135)", "Usage duration (0\u20135)"], series, GROUP_COLORS, "Average code", yrange=[0, 5.6]), "ins_group_usage")
            st.caption("Usage is coded 0\u20135; higher means more frequent or longer use.")

    with chart_card("Where do the groups sit in the two-dimensional PCA view?"):
        proj = pca_projection(models["kmeans_model"], models["kmeans_scaler"], models["kmeans_pca"], result["frame"] if result else None)
        charts.show(charts.pca_scatter(proj["centroids"], [p["label"] for p in profiles], proj["student"], proj["explained_variance"]), "ins_pca")
        st.caption(f"The saved PCA keeps {sum(proj['explained_variance']) * 100:.1f}% of the variance in two components. Only the two group centroids "
                   "and (if you completed the assessment) your own answers are plotted; individual respondents' data is not published.")

    notice(
        f"<b>Interpret with care.</b> K = 2 had the best silhouette score ({silhouette:.2f}), which indicates only moderate separation. The grouping is exploratory: it is "
        "<b>not</b> a diagnosis, a personality type or a validated student classification, and the overreliance score was excluded when forming the groups.", "warn")


def page_profile():
    result = st.session_state.get("result")
    section_title("Understand Your Learning Behaviour", "Based only on the answers you entered in this session, plus the exploratory study groups.")
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
        st.button("Explore model insights", on_click=goto, args=("Model Insights",), key="prof_mi")
