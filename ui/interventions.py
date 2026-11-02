"""ui/interventions.py - rule-based support and an interactive learning activity."""

from __future__ import annotations

import streamlit as st

from backend.interventions import ACTIVITIES, NEUTRAL_MIDPOINT, recommended_focus
from ui.state import goto, remember, sticky
from ui.theme import C_AMBER, C_CYAN, esc, md_html, notice, section_title, stat

FEATURE_ORDER_FOR_UI = ["independent_learning_score", "verification_score", "metacognition_score", "learning_benefit_score"]
FIELD_KEYS = ("attempt", "compare", "errors", "reflect")


def _next_task(feature: str) -> None:
    key = f"iv_task_n_{feature}"
    st.session_state["_sticky"][key] = st.session_state["_sticky"].get(key, 0) + 1


def _reset_activity(feature: str) -> None:
    store = st.session_state["_sticky"]
    for key in [k for k in store if k.startswith(f"iv_{feature}_") or k == f"iv_task_n_{feature}"]:
        store.pop(key, None)
        st.session_state.pop(key, None)


def page_intervention():
    result = st.session_state.get("result")
    section_title("Your Personalised Learning Support", "Rule-based suggestions matched to your four learning-habit scores.")
    if not result:
        md_html('<div class="card"><h4>No assessment yet</h4><p>Complete the assessment first. This page will then show your personalised support.</p></div>')
        st.write("")
        st.button("Go to Assessment", type="primary", on_click=goto, args=("Assess",), key="guard_iv")
        return

    records = result["interventions"]
    flagged = [r for r in records if r["Priority"] == "Focus area"]
    focus = recommended_focus(records)

    md_html(
        f"""
        <div class="flowrow">
        <div class="node"><div class="k">Your scores</div><div class="t">Four construct averages</div><div class="d">Independent learning, verification, metacognition, learning benefits</div></div>
        <div class="arrow" style="align-self:center">\u2192</div>
        <div class="node"><div class="k">Rule</div><div class="t">Below {NEUTRAL_MIDPOINT:.1f}?</div><div class="d">Below the neutral midpoint means targeted support</div></div>
        <div class="arrow" style="align-self:center">\u2192</div>
        <div class="node"><div class="k">Suggested focus</div><div class="t">{esc(focus["Construct"])}</div><div class="d">{"Support recommended" if flagged else "Maintain current practice"}</div></div>
        </div>
        """
    )
    st.write("")
    if flagged:
        notice(f"<b>{len(flagged)} of 4</b> learning dimensions are below the neutral midpoint of {NEUTRAL_MIDPOINT:.1f}, so targeted support is suggested for "
               f"{', '.join(esc(r['Construct']) for r in flagged)}. Other dimensions receive maintenance suggestions.", "info")
    else:
        notice(f"All four learning dimensions are at or above the neutral midpoint of {NEUTRAL_MIDPOINT:.1f}, so each receives a maintenance suggestion. "
               "You can still practise any dimension below.", "ok")
    st.write("")

    cards = []
    for r in records:
        is_focus = r["Priority"] == "Focus area"
        color = C_AMBER if is_focus else C_CYAN
        cards.append(
            f'<div class="card"><div class="label-sm" style="color:{color};font-weight:700;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase">'
            f'{esc(r["Status"])}</div><h4 style="margin-top:6px">{esc(r["Construct"])}</h4>'
            f'<div style="font-size:1.4rem;font-weight:800;color:#142B55;margin-bottom:6px">{r["Observed_Score"]:.2f} <span style="font-size:.85rem;color:#425B82;font-weight:600">/ 5</span></div>'
            f'<p>{esc(r["Intervention"])}</p></div>'
        )
    md_html(f'<div class="grid g2">{"".join(cards)}</div>')

    # ---------------- interactive activity ----------------
    section_title("Practise: an interactive activity", "Attempt a task on your own, compare it with a trusted reference, find errors, and reflect.")
    by_feature = {r["Feature"]: r for r in records}
    options = [r["Feature"] for r in records]
    sticky("iv_dimension", focus["Feature"])
    if st.session_state.get("iv_dimension") not in options:
        st.session_state["iv_dimension"] = focus["Feature"]
    st.selectbox(
        "Learning dimension to practise",
        options,
        key="iv_dimension",
        format_func=lambda f: f"{by_feature[f]['Construct']} \u00b7 {by_feature[f]['Status']}" + (" (suggested)" if f == focus["Feature"] else ""),
        on_change=remember, args=("iv_dimension",),
    )
    remember("iv_dimension")
    feature = st.session_state["iv_dimension"]
    record = by_feature[feature]
    activity = ACTIVITIES[feature]
    needs_support = record["Priority"] == "Focus area"

    skills = "".join(f'<span class="badge cyan" style="margin-right:6px">{esc(s)}</span>' for s in activity["skills"])
    md_html(
        f"""
        <div class="iv-card">
        <div class="eyebrow">{"Recommended activity" if needs_support else "Maintenance activity"}</div>
        <h2>{esc(activity["title"])}</h2>
        <div class="why"><b>Why this activity?</b> {esc(activity["why"] if needs_support else activity["why_maintain"])}</div>
        <div style="margin-top:14px">{skills}</div>
        </div>
        """
    )
    st.write("")

    tasks = activity["tasks"]
    n = st.session_state["_sticky"].get(f"iv_task_n_{feature}", 0)
    task = tasks[n % len(tasks)]
    md_html(f'<div class="card"><h4>Step 1 \u00b7 Your task</h4><p style="color:#142B55;font-size:1rem">{esc(task)}</p>'
            f'<p style="margin-top:8px;font-size:.8rem">Task {n % len(tasks) + 1} of {len(tasks)}</p></div>')
    st.button("Show another task", icon=":material/autorenew:", on_click=_next_task, args=(feature,), key="iv_another")
    st.write("")

    keys = {name: f"iv_{feature}_{name}" for name in FIELD_KEYS}
    honest_key = f"iv_{feature}_honest"
    sticky(honest_key, False)
    for k in keys.values():
        sticky(k, "")

    st.markdown("**Step 2 \u00b7 Attempt it independently**")
    st.checkbox("I wrote my attempt before consulting any AI tool.", key=honest_key, on_change=remember, args=(honest_key,))
    remember(honest_key)
    st.text_area("Your independent attempt", key=keys["attempt"], height=130, on_change=remember, args=(keys["attempt"],),
                 placeholder="Write your own answer or reasoning here\u2026")
    remember(keys["attempt"])
    st.markdown("**Step 3 \u00b7 Compare with an AI explanation or a trusted reference**")
    st.caption(activity["compare_hint"])
    st.text_area("What matches, and what differs?", key=keys["compare"], height=110, on_change=remember, args=(keys["compare"],),
                 placeholder="Note similarities and differences\u2026")
    remember(keys["compare"])
    st.markdown("**Step 4 \u00b7 Identify errors or missing steps**")
    st.text_area("Errors or missing steps (in your answer, the AI answer, or the reference)", key=keys["errors"], height=100,
                 on_change=remember, args=(keys["errors"],), placeholder="For example: a skipped step, an unsupported claim, a mistake\u2026")
    remember(keys["errors"])
    st.markdown("**Step 5 \u00b7 Reflect**")
    st.text_area("What did you learn about your own thinking?", key=keys["reflect"], height=100,
                 on_change=remember, args=(keys["reflect"],), placeholder="What will you do differently next time?")
    remember(keys["reflect"])

    done = int(bool(st.session_state.get(honest_key)))
    for name in FIELD_KEYS:
        done += int(bool(str(st.session_state.get(keys[name], "")).strip()))
    total = len(FIELD_KEYS) + 1
    st.progress(done / total, text=f"Activity progress: {done} of {total} parts completed")
    if done == total:
        notice("\u2705 Activity completed. This records only that you finished the task. This prototype does not measure whether the activity "
               "improves learning or reduces overreliance.", "ok")
    st.caption("Your text stays in this browser session only and is cleared when you refresh the page or start over.")
    st.button("Reset this activity", on_click=_reset_activity, args=(feature,), key="iv_reset")

    st.write("")
    notice(f"The midpoint of {NEUTRAL_MIDPOINT:.1f} is a heuristic design choice, not a validated cut-off. The recommendations and activities are "
           "research-informed prototype suggestions; their effectiveness has not been experimentally validated.", "warn")
    st.write("")
    st.button("View my behavioural insights", on_click=goto, args=("Behavioural Insights",), key="iv_profile")