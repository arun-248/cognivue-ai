"""
ui/theme.py
-----------
Global look and feel: pastel premium-SaaS theme, plus small HTML helpers.
"""

from __future__ import annotations

import re

import streamlit as st

# Palette
BLUE = "#4F7CFF"
LAVENDER = "#8B7CF6"
MINT = "#2FBF9B"
PEACH = "#F59E6B"
NAVY = "#1E2A4A"
MUTED = "#5B6784"
BORDER = "#DCE4F5"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, button, input, textarea {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #F3F6FF 0%, #F8F5FF 55%, #F4FBF8 100%);
    color: #1E2A4A;
}
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }
.block-container { max-width: 1180px; padding-top: 1.4rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #1E2A4A; letter-spacing: -0.02em; }

/* ---------- brand bar ---------- */
.brandbar { display:flex; align-items:center; gap:12px; margin-bottom:6px; }
.brand-logo {
    width:40px; height:40px; border-radius:12px; display:flex; align-items:center;
    justify-content:center; font-size:22px;
    background:linear-gradient(135deg,#DCE6FF,#EADFFF);
    box-shadow:0 4px 14px rgba(79,124,255,.18);
}
.brand-name { font-weight:800; font-size:22px; letter-spacing:-0.03em; color:#1E2A4A; }
.brand-name span { color:#4F7CFF; }
.brand-tag { font-size:12px; color:#5B6784; letter-spacing:.08em; text-transform:uppercase; }

/* ---------- hero ---------- */
.eyebrow {
    display:inline-block; padding:6px 14px; border-radius:999px; font-size:12px;
    font-weight:700; letter-spacing:.08em; text-transform:uppercase;
    color:#4F7CFF; background:#E6EDFF;
}
.hero-title {
    font-size:clamp(36px,5.2vw,60px); line-height:1.08; font-weight:800;
    letter-spacing:-0.035em; color:#1E2A4A; margin:18px 0 16px 0;
}
.hero-title .grad {
    background:linear-gradient(90deg,#4F7CFF,#8B7CF6);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.hero-desc { font-size:17px; line-height:1.75; color:#4A5775; max-width:640px; }
.hero-panel {
    border-radius:26px; padding:30px; min-height:300px;
    background:linear-gradient(145deg,#E4ECFF 0%,#EFE6FF 50%,#DDF6EC 100%);
    border:1px solid #DCE4F5; box-shadow:0 18px 40px rgba(79,124,255,.12);
    display:flex; flex-direction:column; justify-content:center; gap:14px;
}
.hero-chip {
    background:rgba(255,255,255,.85); border-radius:16px; padding:15px 18px;
    display:flex; align-items:center; gap:14px; font-weight:700; color:#1E2A4A;
    box-shadow:0 6px 18px rgba(30,42,74,.07);
}
.hero-chip small { display:block; font-weight:500; color:#5B6784; font-size:13px; }
.chip-dot { width:12px; height:12px; border-radius:50%; flex:none; }

/* ---------- generic cards ---------- */
.section-title { font-size:28px; font-weight:800; letter-spacing:-0.03em; color:#1E2A4A; margin:6px 0 4px 0; }
.section-sub { color:#5B6784; line-height:1.7; margin-bottom:14px; }
.card {
    background:#FFFFFF; border:1px solid #DCE4F5; border-radius:20px; padding:22px;
    box-shadow:0 6px 22px rgba(30,42,74,.05); height:100%;
}
.card h4 { margin:0 0 8px 0; font-size:17px; font-weight:700; color:#1E2A4A; }
.card p { margin:0; color:#4A5775; font-size:14.5px; line-height:1.7; }
.icon-badge {
    width:46px; height:46px; border-radius:14px; display:flex; align-items:center;
    justify-content:center; font-size:22px; margin-bottom:14px;
}
.tint-blue { background:#E6EDFF; } .tint-lav { background:#EFE9FF; }
.tint-mint { background:#DDF6EC; } .tint-peach { background:#FFE9DC; }
.num-badge {
    width:34px; height:34px; border-radius:50%; background:#E6EDFF; color:#4F7CFF;
    display:flex; align-items:center; justify-content:center; font-weight:800; margin-bottom:12px;
}

/* ---------- journey + architecture ---------- */
.flow { display:flex; flex-wrap:wrap; gap:10px; align-items:stretch; }
.flow-step {
    flex:1 1 150px; background:#fff; border:1px solid #DCE4F5; border-radius:16px;
    padding:16px 14px; text-align:center; font-weight:600; font-size:14px; color:#1E2A4A;
    box-shadow:0 4px 14px rgba(30,42,74,.04);
}
.flow-step small { display:block; font-weight:500; color:#5B6784; margin-top:4px; font-size:12.5px; }
.flow-step .n { display:block; color:#4F7CFF; font-weight:800; font-size:12px; letter-spacing:.08em; margin-bottom:6px; }
.arch-main .flow-step { flex:1 1 200px; }
.arch-main .flow-step.accent { background:#EEF2FF; border-color:#C9D6FF; }
.chips { display:flex; flex-wrap:wrap; gap:10px; margin-top:6px; }
.chip {
    background:#fff; border:1px dashed #BFCBEA; border-radius:14px; padding:12px 16px;
    font-size:13.5px; color:#1E2A4A; font-weight:600; flex:1 1 220px;
}
.chip small { display:block; color:#5B6784; font-weight:500; margin-top:3px; }

/* ---------- assessment ---------- */
.stats { display:flex; gap:12px; flex-wrap:wrap; margin-top:14px; }
.stat {
    background:#F3F6FF; border:1px solid #DCE4F5; border-radius:14px; padding:12px 18px; min-width:120px;
}
.stat b { display:block; font-size:24px; color:#1E2A4A; letter-spacing:-0.02em; }
.stat span { font-size:12.5px; color:#5B6784; }
.stepper { display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 10px 0; }
.step-pill {
    padding:7px 14px; border-radius:999px; font-size:13px; font-weight:600;
    background:#fff; color:#5B6784; border:1px solid #DCE4F5;
}
.step-pill.active { background:#4F7CFF; color:#fff; border-color:#4F7CFF; }
.step-pill.done { background:#DDF6EC; color:#1E7F67; border-color:#BDE9D8; }
.q-num { font-size:12px; font-weight:700; color:#4F7CFF; letter-spacing:.08em; text-transform:uppercase; }
.q-text { font-size:16.5px; font-weight:600; color:#1E2A4A; line-height:1.5; margin:4px 0 8px 0; }
.q-missing { color:#D6455D; font-size:13px; font-weight:600; margin-top:4px; }
.note {
    background:#EEF2FF; border:1px solid #D3DDFB; border-radius:14px; padding:12px 16px;
    color:#34436B; font-size:14px; line-height:1.65;
}
.note.warn { background:#FFF4E8; border-color:#F8D9B8; color:#7A4A18; }
.review-row { display:flex; gap:12px; padding:9px 0; border-bottom:1px solid #EEF1FA; font-size:14.5px; }
.review-row:last-child { border-bottom:none; }
.review-q { flex:1 1 70%; color:#34436B; }
.review-a { flex:1 1 30%; font-weight:700; color:#1E2A4A; text-align:right; }
.review-a.missing { color:#D6455D; }

/* radio answers as soft pills */
div[data-testid="stRadio"] label {
    background:#FFFFFF; border:1px solid #D9E2F5; border-radius:12px;
    padding:8px 14px; margin-right:2px; transition:all .15s ease;
}
div[data-testid="stRadio"] label:hover { border-color:#4F7CFF; background:#F5F8FF; }
div[data-testid="stRadio"] label:has(input:checked) { background:#EAF0FF; border-color:#4F7CFF; }
div[data-testid="stRadio"] [role="radiogroup"] { gap:8px; flex-wrap:wrap; }

/* bordered containers (question and review cards) -> white cards */
[class*="st-key-qcard_"], [class*="st-key-revcard_"] {
    background:#FFFFFF; border-radius:18px; border-color:#DCE4F5 !important;
    box-shadow:0 4px 16px rgba(30,42,74,.04);
}

/* ---------- results ---------- */
.score-card {
    background:linear-gradient(145deg,#FFFFFF,#F2F5FF); border:1px solid #DCE4F5;
    border-radius:24px; padding:30px; box-shadow:0 12px 34px rgba(79,124,255,.12);
}
.score-big { font-size:68px; font-weight:800; letter-spacing:-0.04em; color:#1E2A4A; line-height:1; }
.score-big span { font-size:26px; color:#5B6784; font-weight:600; }
.scale { position:relative; height:14px; border-radius:999px; margin:26px 0 8px 0;
    background:linear-gradient(90deg,#CFE9FF,#DCD3FF,#FFD9C4); }
.scale-marker {
    position:absolute; top:-6px; width:26px; height:26px; border-radius:50%;
    background:#4F7CFF; border:4px solid #fff; box-shadow:0 4px 12px rgba(79,124,255,.45);
    transform:translateX(-50%);
}
.scale-labels { display:flex; justify-content:space-between; font-size:12.5px; color:#5B6784; }
.mini-bar { height:8px; border-radius:99px; background:#E9EEFB; margin-top:10px; overflow:hidden; }
.mini-bar div { height:100%; border-radius:99px; background:linear-gradient(90deg,#4F7CFF,#8B7CF6); }
.big-num { font-size:30px; font-weight:800; color:#1E2A4A; letter-spacing:-0.02em; }
.big-num span { font-size:15px; color:#5B6784; font-weight:600; }
.label-sm { font-size:12.5px; color:#5B6784; font-weight:600; text-transform:uppercase; letter-spacing:.06em; }

/* ---------- buttons ---------- */
div.stButton > button, div.stDownloadButton > button {
    border-radius:12px; font-weight:700; min-height:46px; padding:8px 22px;
    border:1px solid #CBD7F5; background:#fff; color:#1E2A4A;
}
div.stButton > button:hover { border-color:#4F7CFF; color:#4F7CFF; background:#F5F8FF; }
div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"] {
    background:linear-gradient(90deg,#4F7CFF,#7B6CF6); color:#fff; border:none;
    box-shadow:0 8px 20px rgba(79,124,255,.28);
}
div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    color:#fff; filter:brightness(1.05);
}

/* ---------- footer ---------- */
.footer {
    margin-top:40px; padding:18px 4px 6px 4px; border-top:1px solid #DCE4F5;
    color:#6A7694; font-size:12.5px; line-height:1.7; text-align:center;
}

@media (max-width: 700px) {
    .score-big { font-size:52px; }
    .review-row { flex-direction:column; gap:2px; }
    .review-a { text-align:left; }
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def html(markup: str) -> None:
    """Render HTML safely: collapse newlines/indentation so Markdown never
    mistakes indented lines for a code block."""
    st.markdown(re.sub(r"\s*\n\s*", " ", markup.strip()), unsafe_allow_html=True)


DISCLAIMER = (
    "This research prototype estimates potential Generative AI overreliance using "
    "self-reported questionnaire responses. Results are intended for educational reflection "
    "and research decision support. They are not clinical or psychological diagnoses, do not "
    "measure actual AI prompt behaviour, and should not be used to make high-stakes decisions "
    "about students."
)


def footer() -> None:
    html(
        f"""
        <div class="footer"><b>Cognivue AI</b> · AI-Based Framework for Detecting Generative AI
        Overreliance and Providing Adaptive Interventions<br>{DISCLAIMER}</div>
        """
    )