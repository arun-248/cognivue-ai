"""ui/interventions.py - rule-based support and four interactive learning activities."""

from __future__ import annotations

import streamlit as st

from backend.interventions import (ACTIVITIES, NEUTRAL_MIDPOINT, SELF_RATING_OPTIONS, activity_progress, all_progress,
                                   intervention_summary, next_recommended, recommended_focus, value_key)
from ui.state import goto, iv_values, remember, sticky
from ui.theme import esc, md_html, notice, section_title, stat

TAG = {"Completed": "tag-done", "In progress": "tag-prog", "Not started": "tag-todo"}


def _next_task(feature: str) -> None:
    tasks = st.session_state["iv_task_n"]
    tasks[feature] = tasks.get(feature, 0) + 1


def _reset_activity(feature: str) -> None:
    store = st.session_state["_sticky"]
    for key in [k for k in store if k.startswith(f"iv_{feature}_")]:
        store.pop(key, None)
        st.session_state.pop(key, None)
    st.session_state["iv_task_n"].pop(feature, None)
    st.session_state["report_bytes"] = None


def _hub(records, progress, nxt) -> None:
    cards = []
    for r in records:
        p = progress[r["Feature"]]
        flag = "Support recommended" if r["Priority"] == "Focus area" else "Maintenance"
        nxt_tag = ' <span class="step-tag tag-next">Suggested next</span>' if nxt and nxt["Feature"] == r["Feature"] else ""
        cards.append(
            f'<div class="card"><div style="margin-bottom:8px"><span class="step-tag {TAG[p["status"]]}">{p["status"]}</span>{nxt_tag}</div>'
            f'<h4>{esc(p["title"])}</h4><p style="margin-bottom:8px">{esc(r["Construct"])} \u00b7 score {r["Observed_Score"]:.2f} \u00b7 {flag}</p>'
            f'<div class="mini-bar" style="height:8px;background:#E9EEFB;border-radius:99px;overflow:hidden"><div style="width:{p["percent"]:.0f}%;height:100%;'
            f'background:linear-gradient(90deg,#3478F6,#8757E8)"></div></div>'
            f'<p style="margin-top:6px;font-size:.82rem">{p["steps_done"]} of {p["steps_total"]} steps \u00b7 {p["reflections_done"]} of {p["reflections_total"]} reflections</p></div>'
        )
    md_html(f'<div class="grid g2">{"".join(cards)}</div>')


def _render_activity(feature: str, record: dict) -> None:
    activity = ACTIVITIES[feature]
    needs_support = record["Priority"] == "Focus area"
    skills = "".join(f'<span class="badge cyan" style="margin-right:6px">{esc(s)}</span>' for s in activity["skills"])
    md_html(
        f"""
        <div class="iv-card">
        <div class="eyebrow">{"Recommended activity" if needs_support else "Maintenance activity"} \u00b7 about {activity["minutes"]} minutes</div>
        <h2>{esc(activity["title"])}</h2>
        <div class="why"><b>Why this activity?</b> {esc(activity["why"] if needs_support else activity["why_maintain"])}</div>
        <div class="why" style="margin-top:8px"><b>Instructions.</b> {esc(activity["instructions"])}</div>
        <div style="margin-top:14px">{skills}</div>
        </div>
        """
    )
    st.write("")
    tasks = activity["tasks"]
    n = st.session_state["iv_task_n"].get(feature, 0)
    md_html(f'<div class="card"><h4>Your topic</h4><p style="color:#142B55;font-size:1rem">{esc(tasks[n % len(tasks)])}</p>'
            f'<p style="margin-top:8px;font-size:.8rem">Topic {n % len(tasks) + 1} of {len(tasks)}. Use any problem or topic from your own coursework.</p></div>')
    st.button("Show another topic", icon=":material/autorenew:", on_click=_next_task, args=(feature,), key=f"iv_another_{feature}")
    st.write("")

    for number, step in enumerate(activity["steps"], start=1):
        key = value_key(feature, step["id"])
        if step["kind"] == "check":
            sticky(key, False)
            st.checkbox(f"Step {number}. {step['text']}", key=key, on_change=remember, args=(key,))
        elif step["kind"] == "rating":
            sticky(key, None)
            st.markdown(f"**Step {number}. {step['text']}**")
            st.radio("Confidence rating (1 to 5)", SELF_RATING_OPTIONS, index=None, horizontal=True, key=key,
                     on_change=remember, args=(key,), label_visibility="collapsed")
        else:
            sticky(key, "")
            st.markdown(f"**Step {number}. {step['text']}**")
            st.text_area(step["label"], key=key, height=110, on_change=remember, args=(key,))
        remember(key)

    st.markdown("**Reflection questions**")
    for r in activity["reflections"]:
        key = value_key(feature, r["id"])
        sticky(key, "")
        st.text_area(r["question"], key=key, height=80, on_change=remember, args=(key,))
        remember(key)

    p = activity_progress(feature, iv_values())
    st.progress(p["percent"] / 100, text=f"{p['status']} \u00b7 {p['steps_done']} of {p['steps_total']} steps, {p['reflections_done']} of {p['reflections_total']} reflections")
    if p["completed"]:
        notice("\u2705 Activity completed. This records only that you finished the task. This prototype does not measure whether the activity "
               "improves learning or reduces overreliance.", "ok")
    else:
        pending = [f"Step {i}" for i, s in enumerate(activity["steps"], 1) if s["id"] in p["pending_steps"]]
        pending += [f"Reflection {i}" for i, r in enumerate(activity["reflections"], 1) if r["id"] in p["pending_reflections"]]
        st.caption("Still to do: " + ", ".join(pending))
    st.caption("Your text stays in this browser session only and is cleared when you refresh the page or start over.")
    st.button("Reset this activity", on_click=_reset_activity, args=(feature,), key=f"iv_reset_{feature}")


def page_intervention():
    result = st.session_state.get("result")
    section_title("Your Personalised Learning Support", "Rule-based suggestions and four interactive activities, one for each learning dimension.")
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment first. This page will then show your personalised support.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_iv")
        return

    records = result["interventions"]
    by_feature = {r["Feature"]: r for r in records}
    flagged = [r for r in records if r["Priority"] == "Focus area"]
    focus = recommended_focus(records)
    values = iv_values()
    progress = all_progress(values)
    nxt = next_recommended(records, progress)

    md_html(
        f"""
        <div class="flowrow">
        <div class="node"><div class="k">Your scores</div><div class="t">Four construct averages</div><div class="d">Independent learning, verification, metacognition, learning benefits</div></div>
        <div class="arrow" style="align-self:center">\u2192</div>
        <div class="node"><div class="k">Rule</div><div class="t">Below {NEUTRAL_MIDPOINT:.1f}?</div><div class="d">Below the neutral midpoint means targeted support (a heuristic)</div></div>
        <div class="arrow" style="align-self:center">\u2192</div>
        <div class="node"><div class="k">Weakest dimension</div><div class="t">{esc(focus["Construct"])}</div><div class="d">{"Support recommended" if flagged else "Maintain current practice"}</div></div>
        </div>
        """
    )
    st.write("")
    if flagged:
        notice(f"<b>{len(flagged)} of 4</b> learning dimensions are below the neutral midpoint of {NEUTRAL_MIDPOINT:.1f}: "
               f"{', '.join(esc(r['Construct']) for r in flagged)}. Targeted support is suggested there; the other dimensions receive maintenance suggestions. "
               "You can do any of the four activities.", "info")
    else:
        notice(f"All four learning dimensions are at or above the neutral midpoint of {NEUTRAL_MIDPOINT:.1f}, so each receives a maintenance suggestion. "
               "You can still practise any activity.", "ok")
    st.write("")

    section_title("Your four activities", "Status updates as you work. The suggested next activity targets your weakest dimension that is not yet completed.")
    _hub(records, progress, nxt)
    if nxt:
        notice(f"<b>Suggested next:</b> {esc(ACTIVITIES[nxt['Feature']]['title'])} ({esc(nxt['Construct'])}, score {nxt['Observed_Score']:.2f}).", "info")
    else:
        notice("<b>All four activities are completed.</b> See your intervention summary below.", "ok")

    section_title("Work on an activity")
    options = [r["Feature"] for r in records]
    default = nxt["Feature"] if nxt else focus["Feature"]
    sticky("iv_open", default)
    if st.session_state.get("iv_open") not in options:
        st.session_state["iv_open"] = default
    st.selectbox("Choose an activity", options, key="iv_open", on_change=remember, args=("iv_open",),
                 format_func=lambda f: f"{ACTIVITIES[f]['title']} \u00b7 {progress[f]['status']}")
    remember("iv_open")
    feature = st.session_state["iv_open"]
    _render_activity(feature, by_feature[feature])

    # -------- final summary --------
    st.write("")
    section_title("Intervention summary")
    progress = all_progress(iv_values())
    summary = intervention_summary(records, progress, iv_values(), include_reflections=True)
    nxt = next_recommended(records, progress)
    md_html('<div class="grid g3">'
            + stat(f"{summary['completed']} of {summary['total']}", "Activities completed", "this session")
            + stat(str(sum(1 for r in summary["rows"] if r["progress_status"] == "In progress")), "In progress", "started, not finished")
            + stat(str(sum(1 for r in summary["rows"] if r["progress_status"] == "Not started")), "Not started", "still pending") + "</div>")
    st.write("")
    rows = "".join(
        f"<tr><td>{esc(r['construct'])}</td><td>{r['score']:.2f}</td><td>{esc(r['activity'])}</td><td>{esc(r['progress_status'])}</td><td>{r['percent']:.0f}%</td></tr>"
        for r in summary["rows"])
    md_html(f'<div class="card" style="overflow-x:auto"><table class="rtable"><tr><th>Dimension</th><th>Score</th><th>Activity</th><th>Status</th><th>Done</th></tr>{rows}</table></div>')
    st.write("")
    if nxt:
        md_html(f'<div class="sumbox"><b>Next recommended activity:</b> {esc(ACTIVITIES[nxt["Feature"]]["title"])} for {esc(nxt["Construct"])} '
                f'(your lowest score among the activities still to do, {nxt["Observed_Score"]:.2f}).</div>')
    with st.expander("My reflections so far"):
        any_text = False
        for r in summary["rows"]:
            for question, answer in r.get("reflections", []):
                any_text = True
                st.markdown(f"**{r['construct']}** \u2013 {question}")
                st.write(answer)
        if not any_text:
            st.caption("No reflections written yet.")
    st.write("")
    notice(f"The midpoint of {NEUTRAL_MIDPOINT:.1f} is a heuristic design choice, not a validated cut-off. The activities are research-informed prototype suggestions; "
           "their effectiveness has not been experimentally validated, and finishing them does not show improved learning or reduced overreliance.", "warn")
    st.write("")
    c1, c2, _ = st.columns([1.3, 1.4, 2])
    with c1:
        st.button("Report & progress", type="primary", on_click=goto, args=("Progress",), key="iv_to_progress")
    with c2:
        st.button("View behavioural insights", on_click=goto, args=("Behavioural Insights",), key="iv_profile")
