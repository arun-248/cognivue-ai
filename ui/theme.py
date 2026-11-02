"""
ui/theme.py
-----------
Pastel dashboard theme (same visual language as the earlier project) plus
small HTML helpers used by every page.
"""

from __future__ import annotations

import html as htmllib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import streamlit as st  # noqa: E402

C_CARD = "#FFFFFF"
C_BORDER = "#C8D9F0"
C_BLUE = "#3478F6"
C_PURPLE = "#8757E8"
C_NAVY = "#142B55"
C_TEXT = "#142B55"
C_MUTED = "#425B82"
C_CYAN = "#109A8A"
C_GREEN = "#16A34A"
C_AMBER = "#D97706"
C_RED = "#EF4444"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp, button, input, textarea, select {
  font-family: 'Inter','Segoe UI',system-ui,-apple-system,Roboto,sans-serif;
}
.stApp { background: radial-gradient(900px 460px at 8% -10%, rgba(52,120,246,.10), transparent 60%), #DCEBFA; color: #142B55; }
header[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display: none; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 100% !important; padding: 1rem 1.6rem 2rem 1.6rem !important; }
h1, h2, h3, h4, h5 { font-weight: 700; letter-spacing: -0.01em; color: #142B55; }
p, li, label, span { color: inherit; }

/* ---------- brand bar ---------- */
.brandbar { display:flex; align-items:center; justify-content:space-between; gap:12px; margin: 4px 0 14px 0; flex-wrap:wrap; }
.brand { display:flex; align-items:center; gap:12px; }
.logo { width:38px; height:38px; border-radius:11px; background:#3478F6; display:flex; align-items:center; justify-content:center; font-size:20px;  }
.brand-name { font-weight:800; font-size:1.05rem; letter-spacing:-.01em; }
.brand-sub { color:#425B82; font-size:.74rem; margin-top:-2px; }
.badge { display:inline-block; padding:4px 11px; border-radius:999px; font-size:.72rem; font-weight:600; border:1px solid #C8D9F0; background:#EEF4FD; color:#425B82; }
.badge.blue { background:rgba(52,120,246,.14); border-color:rgba(52,120,246,.45); color:#2B63D6; }
.badge.purple { background:rgba(52,120,246,.14); border-color:rgba(52,120,246,.45); color:#2B63D6; }
.badge.cyan { background:rgba(52,120,246,.12); border-color:rgba(52,120,246,.4); color:#109A8A; }

/* ---------- top navbar ---------- */
.st-key-topnav { background:#EEF4FD; border:1px solid #C8D9F0; border-radius:16px; padding:10px 18px; margin-bottom:22px; }
.st-key-topnav [data-testid="stHorizontalBlock"] { align-items:center; gap:.4rem; }
.nav-brand { display:flex; align-items:center; gap:12px; }
.nav-logo { width:38px; height:38px; border-radius:10px; background:#3478F6; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:.9rem; color:#fff; }
.nav-name { font-weight:700; font-size:1.02rem; color:#142B55; letter-spacing:-.01em; }
.st-key-topnav [data-testid="stButton"] { width:100%; }
.st-key-topnav button { width:100%; min-height:42px; border-radius:10px; font-weight:600; }
.st-key-topnav button p { color:inherit; font-weight:600; font-size:.9rem; }
.st-key-topnav button[kind="secondary"], .st-key-topnav button[data-testid="stBaseButton-secondary"] { background:transparent; border:none; color:#425B82; }
.st-key-topnav button[kind="secondary"]:hover, .st-key-topnav button[data-testid="stBaseButton-secondary"]:hover { background:#E3EDFB; color:#142B55; border:none; }
.st-key-topnav button[kind="primary"], .st-key-topnav button[data-testid="stBaseButton-primary"] { background:rgba(52,120,246,.16); color:#2B63D6; border:1px solid rgba(52,120,246,.35); }
.st-key-topnav button[kind="primary"]:hover, .st-key-topnav button[data-testid="stBaseButton-primary"]:hover { background:rgba(52,120,246,.16); color:#2B63D6; filter:none; }
.st-key-nav_cta button { background:#3478F6 !important; color:#fff !important; border:none !important; border-radius:10px !important; min-height:42px; }
.st-key-nav_cta button:hover { background:#5B93F8 !important; }

/* ---------- left panel ---------- */
.panel-label { color:#5A7096; font-size:.7rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; margin:2px 4px 10px 4px; }
.st-key-leftpanel [data-testid="stButton"] { width:100%; }
.st-key-leftpanel button { width:100%; min-height:48px; padding:.4rem .9rem; border-radius:12px; background:#EEF4FD; border:1px solid #D9E6F7; color:#425B82; }
.st-key-leftpanel button > div { justify-content:flex-start; width:100%; text-align:left; }
.st-key-leftpanel button p { font-weight:600; font-size:.9rem; color:inherit; }
.st-key-leftpanel button:hover { border-color:#B9CDEA; background:#FFFFFF; color:#142B55; }
.st-key-leftpanel button[kind="primary"], .st-key-leftpanel button[data-testid="stBaseButton-primary"] { background:rgba(52,120,246,.14); border:1px solid rgba(52,120,246,.45); color:#142B55; }

/* ---------- right panel ---------- */
.art-card { background:#EEF4FD; border:1px solid #D9E6F7; border-radius:16px; overflow:hidden; }
.art-card svg { width:100%; height:auto; display:block; }
.art-card .cap { padding:14px 16px 16px 16px; }
.art-card .cap b { font-size:.92rem; }
.art-card .cap p { color:#425B82; font-size:.8rem; line-height:1.5; margin:4px 0 0 0; }

/* ---------- cards ---------- */
.card { background:#FFFFFF; border:1px solid #C8D9F0; border-radius:16px; padding:20px 22px;  }
.card.tight { padding:14px 16px; }
.card h4 { margin:0 0 6px 0; font-size:1.02rem; }
.card p { color:#425B82; font-size:.9rem; line-height:1.55; margin:0; }
.card .icon { font-size:1.5rem; margin-bottom:8px; }
.eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.7rem; font-weight:700; color:#109A8A; margin-bottom:6px; }
.section-title { font-size:1.35rem; font-weight:800; margin: 26px 0 4px 0; }
.section-sub { color:#425B82; font-size:.92rem; margin-bottom:14px; }
.grid { display:grid; gap:16px; }
.g2 { grid-template-columns:repeat(2,1fr); }
.g3 { grid-template-columns:repeat(3,1fr); }
.g4 { grid-template-columns:repeat(4,1fr); }
.g5 { grid-template-columns:repeat(5,1fr); }
@media (max-width: 980px) { .g4, .g5 { grid-template-columns:repeat(2,1fr); } .g3 { grid-template-columns:repeat(2,1fr); } }
@media (max-width: 640px) { .g2, .g3, .g4, .g5 { grid-template-columns:1fr; } }

/* ---------- hero ---------- */
.hero { display:grid; grid-template-columns:1.1fr .9fr; gap:28px; align-items:center; padding:36px; border-radius:20px; background:#EEF4FD; border:1px solid #C8D9F0; }
@media (max-width: 900px) { .hero { grid-template-columns:1fr; padding:24px; } }
.hero h1 { font-size:2rem; line-height:1.2; margin:12px 0 12px 0; font-weight:800; color:#142B55; }
.hero .sub { color:#425B82; font-size:1.02rem; line-height:1.6; }
.hero .tagline { margin-top:16px; color:#425B82; font-size:.95rem; line-height:1.7; }
.hero-art { width:100%; }
.hero-art svg, .hero-art img { width:100%; height:auto; border-radius:18px; display:block; }

/* ---------- steps / flow ---------- */
.steps { display:flex; align-items:stretch; gap:8px; flex-wrap:wrap; }
.step { flex:1 1 150px; background:#FFFFFF; border:1px solid #C8D9F0; border-radius:14px; padding:16px; text-align:left; min-width:140px; }
.step .num { width:28px; height:28px; border-radius:50%; background:#3478F6; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:.82rem; margin-bottom:10px; color:#fff; }
.step h5 { margin:0 0 4px 0; font-size:.95rem; }
.step p { margin:0; color:#425B82; font-size:.8rem; line-height:1.45; }
.arrow { align-self:center; color:#3478F6; font-size:1.3rem; font-weight:700; }
.stat { background:#FFFFFF; border:1px solid #C8D9F0; border-radius:16px; padding:18px 20px; }
.stat .v { font-size:1.75rem; font-weight:800; letter-spacing:-.02em; }
.stat .l { color:#425B82; font-size:.8rem; margin-top:2px; }
.stat .s { color:#5A7096; font-size:.74rem; margin-top:6px; }

/* ---------- assess ---------- */
.stepper { display:flex; gap:8px; flex-wrap:wrap; margin: 6px 0 10px 0; }
.chip { padding:6px 13px; border-radius:999px; font-size:.78rem; font-weight:600; border:1px solid #C8D9F0; background:#EEF4FD; color:#425B82; }
.chip.active { background:#3478F6; color:#fff; border-color:transparent; }
.chip.done { background:rgba(34,197,94,.12); color:#15803D; border-color:rgba(34,197,94,.35); }
div[data-testid="stProgress"] > div > div > div > div { background: #3478F6; }

/* ---------- prediction ---------- */
.gauge-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; }
.risk-pill { display:inline-block; padding:6px 16px; border-radius:999px; font-weight:700; font-size:.82rem; letter-spacing:.06em; text-transform:uppercase; margin-top:6px; }
.scale { padding: 34px 14px 38px 14px; }
.scale-track { position:relative; display:flex; height:14px; border-radius:999px; }
.scale-track .seg:first-child { border-radius:999px 0 0 999px; }
.scale-track .seg:nth-child(3) { border-radius:0 999px 999px 0; }
.marker { position:absolute; top:-9px; transform:translateX(-50%); width:32px; height:32px; border-radius:50%; background:#142B55; border:4px solid #3478F6;  }
.marker span { position:absolute; top:-26px; left:50%; transform:translateX(-50%); font-size:.78rem; font-weight:700; color:#142B55; white-space:nowrap; }
.ticks { position:relative; height:18px; margin-top:16px; }
.ticks span { position:absolute; transform:translateX(-50%); color:#425B82; font-size:.78rem; }
.zones { display:flex; margin-top:2px; }
.zones span { text-align:center; color:#5A7096; font-size:.74rem; text-transform:uppercase; letter-spacing:.1em; }

/* ---------- XAI ---------- */
.factor { display:flex; gap:10px; align-items:flex-start; padding:10px 0; border-bottom:1px solid #D9E6F7; }
.factor:last-child { border-bottom:none; }
.factor .dot { width:10px; height:10px; border-radius:50%; margin-top:6px; flex:0 0 10px; }
.factor .ft { font-weight:600; font-size:.9rem; }
.factor .fd { color:#425B82; font-size:.82rem; line-height:1.45; }

/* ---------- intervention ---------- */
.flowrow { display:flex; align-items:stretch; gap:10px; flex-wrap:wrap; }
.flowrow .node { flex:1 1 180px; background:#FFFFFF; border:1px solid #C8D9F0; border-radius:14px; padding:14px 16px; }
.flowrow .node .k { color:#109A8A; font-size:.68rem; text-transform:uppercase; letter-spacing:.12em; font-weight:700; }
.flowrow .node .t { font-weight:700; margin-top:4px; font-size:.95rem; }
.flowrow .node .d { color:#425B82; font-size:.8rem; margin-top:3px; }
.iv-card { background: linear-gradient(135deg, rgba(52,120,246,.16), rgba(52,120,246,.14)), #FFFFFF; border:1px solid rgba(52,120,246,.45); border-radius:20px; padding:26px 28px;  }
.iv-card h2 { margin:6px 0 8px 0; font-size:1.55rem; text-transform:uppercase; letter-spacing:.02em; }
.iv-card .why { color:#425B82; font-size:.95rem; line-height:1.6; }
.stages { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.stage { padding:10px 16px; border-radius:12px; background:#EEF4FD; border:1px solid #C8D9F0; color:#5A7096; font-weight:600; font-size:.86rem; }
.stage.active { background:#3478F6; color:#fff; border-color:transparent;  }
.stage-arrow { color:#3478F6; font-weight:700; }
.quote { border-left:3px solid #109A8A; padding:12px 18px; background:rgba(52,120,246,.06); border-radius:0 12px 12px 0; color:#1F3A68; font-size:1rem; line-height:1.6; }

/* ---------- tables / bars ---------- */
.rtable { width:100%; border-collapse:separate; border-spacing:0; font-size:.9rem; }
.rtable th { text-align:left; color:#425B82; font-weight:600; font-size:.76rem; text-transform:uppercase; letter-spacing:.08em; padding:10px 14px; border-bottom:1px solid #C8D9F0; }
.rtable td { padding:12px 14px; border-bottom:1px solid #D9E6F7; color:#1F3A68; }
.rtable tr.sel td { background:rgba(52,120,246,.12); font-weight:700; }
.rtable tr.sel td:first-child { border-left:3px solid #3478F6; }
.minibar { height:8px; background:#D9E6F7; border-radius:99px; overflow:hidden; margin-top:6px; }
.minibar > div { height:100%; border-radius:99px; background:linear-gradient(90deg,#3478F6,#109A8A); }
.mb-row { margin-bottom:14px; }
.mb-row .top { display:flex; justify-content:space-between; font-size:.85rem; }
.mb-row .top span:last-child { color:#425B82; font-weight:600; }

/* ---------- architecture ---------- */
.arch-branch { background:#EEF4FD; border:1px solid #C8D9F0; border-radius:16px; padding:16px 18px; margin-bottom:12px; }
.arch-label { color:#109A8A; font-size:.7rem; text-transform:uppercase; letter-spacing:.12em; font-weight:700; margin-bottom:10px; }
.flow { display:flex; align-items:center; flex-wrap:wrap; gap:8px; }
.flow .n { background:#FFFFFF; border:1px solid #C8D9F0; border-radius:12px; padding:10px 14px; font-size:.84rem; font-weight:600; }
.flow .n small { display:block; color:#425B82; font-weight:400; font-size:.72rem; margin-top:2px; }
.flow .n.hl { border-color:rgba(52,120,246,.6); background:rgba(52,120,246,.1); }
.flow i { color:#3478F6; font-style:normal; font-weight:700; }
.arch-merge { text-align:center; background:linear-gradient(135deg, rgba(52,120,246,.14), rgba(52,120,246,.14)); border:1px dashed rgba(52,120,246,.6); border-radius:16px; padding:16px; }
.arch-merge b { font-size:1rem; }
.arch-merge div { color:#425B82; font-size:.8rem; margin-top:4px; }

/* ---------- misc ---------- */
.notice { border-radius:14px; padding:14px 18px; font-size:.88rem; line-height:1.55; border:1px solid #C8D9F0; background:#EEF4FD; color:#425B82; }
.notice.info { border-color:rgba(52,120,246,.4); background:rgba(52,120,246,.08); }
.notice.warn { border-color:rgba(245,158,11,.4); background:rgba(245,158,11,.07); }
.notice.ok { border-color:rgba(34,197,94,.4); background:rgba(34,197,94,.07); }
.footer { margin-top:34px; padding:22px 20px; text-align:center; border-top:1px solid #D9E6F7; }
.footer .fb { font-weight:700; font-size:.95rem; color:#1F3A68; }
.footer .ft { color:#425B82; font-size:.84rem; margin:4px 0 8px 0; }
.footer .fs { color:#5A7096; font-size:.76rem; }
.big-quote { font-size:1.15rem; font-weight:600; line-height:1.55; text-align:center; padding:22px; border-radius:18px;
  background:linear-gradient(135deg, rgba(52,120,246,.08), rgba(52,120,246,.10)); border:1px solid #C8D9F0; color:#1F3A68; }

/* ---------- streamlit widgets ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:16px; }
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
  background: #3478F6; border:none; color:#fff; font-weight:700; border-radius:12px; padding:.55rem 1.2rem;
  
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover { filter:brightness(1.1); border:none; color:#fff; }
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] { border-radius:12px; border:1px solid #C8D9F0; background:#EEF4FD; color:#1F3A68; font-weight:600; }
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover { border-color:#3478F6; color:#2B63D6; }
button[data-baseweb="tab"] { font-weight:600; }
div[data-testid="stExpander"] { border-radius:14px; border:1px solid #C8D9F0; background:#EEF4FD; }
.card, .stat, .step, .art-card, .flowrow .node, .arch-branch, .st-key-topnav, .notice { box-shadow:0 1px 2px rgba(36,52,75,.06), 0 8px 22px rgba(36,52,75,.06); }
.stApp { background:radial-gradient(900px 460px at 8% -10%, rgba(52,120,246,.10), transparent 60%), #DCEBFA; color:#142B55; }
.hero { background:linear-gradient(135deg,#FFFFFF 0%,#E5F1FF 100%); }
.iv-card { background:linear-gradient(135deg,#FFFFFF,#E5F1FF); }
.marker { background:#FFFFFF; }
/* ===== pastel dashboard theme (tokens are replaced from the central palette constants) ===== */
.stApp { background: radial-gradient(900px 520px at 6% -8%, rgba(255,231,213,.75), transparent 60%), radial-gradient(900px 560px at 100% 4%, rgba(233,231,255,.95), transparent 58%), radial-gradient(900px 520px at 50% 112%, rgba(221,247,243,.85), transparent 60%), #DCEBFA; color:#142B55; }
.block-container { padding: 1rem 1.4rem 2rem 1.4rem !important; }
h1, h2, h3, h4, h5 { color:#142B55; }

/* top navigation */
.st-key-topnav { background:linear-gradient(90deg,#E5F1FF 0%,#EDE9FF 52%,#FFF1E3 100%); border:1px solid rgba(255,255,255,.85); border-radius:24px; padding:12px 24px; margin-bottom:18px; box-shadow:0 12px 32px rgba(20,43,85,.10); }
.st-key-topnav [data-testid="stHorizontalBlock"] { align-items:center; gap:.5rem; }
.nav-brand { display:flex; align-items:center; gap:14px; }
.nav-logo { width:46px; height:46px; flex:0 0 46px; filter:drop-shadow(0 6px 12px rgba(36,87,214,.3)); }
.nav-logo svg { width:100%; height:100%; display:block; }
.nav-name { font-weight:800; font-size:1.12rem; color:#142B55; letter-spacing:-.01em; line-height:1.15; }
.nav-sub { font-size:.78rem; color:#425B82; margin-top:1px; }
.st-key-topnav button { width:100%; min-height:46px; border-radius:14px; font-weight:600; }
.st-key-topnav button[kind="secondary"], .st-key-topnav button[data-testid="stBaseButton-secondary"] { background:transparent; border:none; color:#142B55; }
.st-key-topnav button[kind="secondary"]:hover, .st-key-topnav button[data-testid="stBaseButton-secondary"]:hover { background:rgba(255,255,255,.75); color:#142B55; border:none; }
.st-key-topnav button[kind="primary"], .st-key-topnav button[data-testid="stBaseButton-primary"] { background:#CFE0FB; color:#1F4FD1; border:none; }
.st-key-topnav button[kind="primary"]:hover, .st-key-topnav button[data-testid="stBaseButton-primary"]:hover { background:#CFE0FB; color:#1F4FD1; filter:none; }
.st-key-nav_cta button { background:linear-gradient(135deg,#3F7BF2,#2457D6) !important; color:#fff !important; border:none !important; border-radius:14px !important; min-height:48px; box-shadow:0 10px 22px rgba(52,120,246,.35) !important; font-weight:700; }
.st-key-nav_cta button:hover { filter:brightness(1.08); }

/* left sidebar */
.st-key-leftpanel { background:linear-gradient(180deg,#E6F0FD 0%,#ECEAFF 68%,#E5F6F3 100%); border:1px solid rgba(255,255,255,.85); border-radius:26px; padding:18px 14px 6px 14px; box-shadow:0 12px 30px rgba(20,43,85,.08); }
.panel-label { color:#425B82; font-size:.72rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; margin:6px 6px 10px 6px; }
.panel-divider { height:1px; background:rgba(66,91,130,.18); margin:14px 6px 12px 6px; }
.st-key-leftpanel button { width:100%; min-height:48px; padding:.4rem .9rem; border-radius:14px; background:rgba(255,255,255,.72); border:1px solid rgba(255,255,255,.9); color:#142B55; transition:all .15s ease; }
.st-key-leftpanel button p { color:inherit; font-weight:600; font-size:.93rem; }
.st-key-leftpanel button:hover { background:#fff; border-color:#BCD3F8; transform:translateX(2px); color:#142B55; }
.st-key-leftpanel button[kind="primary"], .st-key-leftpanel button[data-testid="stBaseButton-primary"] { background:#CFE0FB; border:1px solid #BCD3F8; color:#1F4FD1; box-shadow:inset 4px 0 0 #3478F6; }
.side-art { display:flex; align-items:flex-end; gap:4px; margin:10px 0 4px 0; }
.side-art svg { width:56%; height:auto; display:block; flex:0 0 56%; }
.side-art p { font-size:.86rem; color:#425B82; line-height:1.4; font-weight:600; margin:0 0 18px 0; }

/* home hero */
.hero2 { display:grid; grid-template-columns:1.02fr 1fr; gap:6px; align-items:center; padding:30px 28px 22px 34px; border-radius:30px; background:linear-gradient(135deg,#E5F1FF 0%,#F0E7FF 55%,#FFE7D5 125%); border:1px solid rgba(255,255,255,.9); box-shadow:0 18px 44px rgba(20,43,85,.10); }
.hero-badge { display:inline-flex; align-items:center; gap:8px; padding:7px 14px; border-radius:999px; background:#DDF7EA; color:#0B6B5F; font-weight:700; font-size:.8rem; border:1px solid #BFEBD8; }
.hero2 h1 { font-size:2.3rem; line-height:1.14; font-weight:800; margin:16px 0 14px 0; color:#142B55; letter-spacing:-.02em; }
.hero2 h1 .hl { color:#3478F6; }
.hero2 .desc { color:#425B82; font-size:1.02rem; line-height:1.6; max-width:540px; }
.benefits { list-style:none; padding:0; margin:18px 0 0 0; display:grid; gap:10px; }
.benefits li { display:flex; align-items:center; gap:12px; font-weight:600; color:#142B55; font-size:1rem; }
.ck { width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; color:#fff; font-size:.8rem; font-weight:800; flex:0 0 26px; }
.ck.b { background:#3478F6; } .ck.p { background:#9B7CF0; } .ck.m { background:#38C18F; }
.hero-art svg, .hero-art img { width:100%; height:auto; display:block; }
.hero-pills { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin-top:4px; }
.hero-pills span { padding:8px 22px; border-radius:999px; font-weight:700; font-size:.86rem; }
.pill-b { background:#DCE8FF; color:#2457D6; } .pill-m { background:#D5F3E5; color:#0F7A66; } .pill-l { background:#E8DEFF; color:#6A3FD0; }
.collab { border-radius:30px; overflow:hidden; background:linear-gradient(180deg,#FFE7D5 0%,#DDF7EA 58%,#E5F1FF 100%); border:1px solid rgba(255,255,255,.9); box-shadow:0 18px 44px rgba(20,43,85,.10); }
.collab svg { width:100%; height:auto; display:block; }
.collab .cap { padding:20px 22px 26px 22px; }
.collab h3 { font-size:1.25rem; margin:0 0 8px 0; color:#142B55; font-weight:800; }
.collab p { color:#425B82; font-size:.96rem; line-height:1.55; margin:0; }

/* action buttons */
.st-key-act1 button { width:100%; min-height:58px; border-radius:16px; background:linear-gradient(135deg,#3F7BF2,#2457D6); color:#fff; border:none; font-weight:700; box-shadow:0 12px 26px rgba(52,120,246,.35); }
.st-key-act2 button { width:100%; min-height:58px; border-radius:16px; background:#E1EDFF; color:#142B55; border:1px solid #CFE0FB; font-weight:700; }
.st-key-act3 button { width:100%; min-height:58px; border-radius:16px; background:#DDF7EA; color:#142B55; border:1px solid #BFEBD8; font-weight:700; }
.st-key-act1 button p, .st-key-act2 button p, .st-key-act3 button p { color:inherit; font-weight:700; font-size:1rem; }
.st-key-act1 button:hover, .st-key-act2 button:hover, .st-key-act3 button:hover { transform:translateY(-2px); filter:brightness(1.03); }
.st-key-act2 button:hover { border-color:#3478F6; color:#1F4FD1; } .st-key-act3 button:hover { border-color:#109A8A; color:#0B6B5F; }

/* feature cards */
.feat-ic { width:58px; height:58px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-bottom:14px; }
.feat-ic svg { width:28px; height:28px; }
.feat-title { font-weight:800; font-size:1.08rem; color:#142B55; margin-bottom:6px; }
.feat-desc { color:#425B82; font-size:.9rem; line-height:1.5; padding-right:46px; }
.st-key-feat0, .st-key-feat1, .st-key-feat2, .st-key-feat3 { border-radius:22px; padding:22px 22px 18px 22px; position:relative; min-height:200px; border:1px solid rgba(255,255,255,.9); box-shadow:0 12px 30px rgba(20,43,85,.07); transition:transform .18s ease, box-shadow .18s ease; }
.st-key-feat0:hover, .st-key-feat1:hover, .st-key-feat2:hover, .st-key-feat3:hover { transform:translateY(-4px); box-shadow:0 18px 38px rgba(20,43,85,.12); }
.st-key-feat0 { background:linear-gradient(135deg,#EDF5FF,#DCEBFF); } .st-key-feat1 { background:linear-gradient(135deg,#F5EFFF,#E8DEFF); }
.st-key-feat2 { background:linear-gradient(135deg,#E9FAF2,#D5F3E5); } .st-key-feat3 { background:linear-gradient(135deg,#FFF3E8,#FFE2CC); }
.st-key-feat0 [data-testid="stButton"], .st-key-feat1 [data-testid="stButton"], .st-key-feat2 [data-testid="stButton"], .st-key-feat3 [data-testid="stButton"] { position:absolute; right:16px; bottom:14px; width:auto; }
.st-key-feat0 button, .st-key-feat1 button, .st-key-feat2 button, .st-key-feat3 button { width:42px; height:42px; min-height:42px; padding:0; border-radius:50%; background:#fff; border:none; box-shadow:0 6px 16px rgba(20,43,85,.12); font-weight:800; font-size:1.05rem; }
.st-key-feat0 button { color:#2457D6; } .st-key-feat1 button { color:#6A3FD0; } .st-key-feat2 button { color:#0F7A66; } .st-key-feat3 button { color:#C2570C; }
.st-key-feat0 button:hover, .st-key-feat1 button:hover, .st-key-feat2 button:hover, .st-key-feat3 button:hover { transform:scale(1.1); }

/* shared pastel components used on every page */
.card { background:rgba(255,255,255,.84); border:1px solid rgba(255,255,255,.95); border-radius:20px; box-shadow:0 10px 28px rgba(20,43,85,.07); transition:transform .18s ease, box-shadow .18s ease; }
.card:hover { transform:translateY(-2px); box-shadow:0 16px 34px rgba(20,43,85,.10); }
.grid > .card:nth-child(4n+1), .grid > .stat:nth-child(4n+1) { background:linear-gradient(135deg,#EDF5FF,#DCEBFF); }
.grid > .card:nth-child(4n+2), .grid > .stat:nth-child(4n+2) { background:linear-gradient(135deg,#F5EFFF,#E8DEFF); }
.grid > .card:nth-child(4n+3), .grid > .stat:nth-child(4n+3) { background:linear-gradient(135deg,#E9FAF2,#D5F3E5); }
.grid > .card:nth-child(4n+4), .grid > .stat:nth-child(4n+4) { background:linear-gradient(135deg,#FFF3E8,#FFE2CC); }
.stat { border:1px solid rgba(255,255,255,.95); border-radius:20px; box-shadow:0 10px 28px rgba(20,43,85,.07); background:rgba(255,255,255,.84); }
.steps > .step:nth-child(1) { background:linear-gradient(135deg,#EDF5FF,#DCEBFF); } .steps > .step:nth-child(3) { background:linear-gradient(135deg,#F5EFFF,#E8DEFF); }
.steps > .step:nth-child(5) { background:linear-gradient(135deg,#E9FAF2,#D5F3E5); } .steps > .step:nth-child(7) { background:linear-gradient(135deg,#FFF3E8,#FFE2CC); }
.steps > .step:nth-child(9) { background:linear-gradient(135deg,#DDF7F3,#C9EFE9); }
.step { border:1px solid rgba(255,255,255,.95); border-radius:18px; }
.stages .stage:nth-child(1) { background:#DCEBFF; color:#2457D6; } .stages .stage:nth-child(3) { background:#E8DEFF; color:#6A3FD0; } .stages .stage:nth-child(5) { background:#D5F3E5; color:#0F7A66; }
.stages .stage:nth-child(7) { background:#FFE2CC; color:#C2570C; } .stages .stage:nth-child(9) { background:#C9EFE9; color:#0B6B5F; }
.stages .stage { border:none; }
.stages .stage.active { background:linear-gradient(135deg,#3F7BF2,#2457D6); color:#fff; box-shadow:0 8px 20px rgba(52,120,246,.35); }
.rtable th { background:#E5F1FF; color:#142B55; border-bottom:1px solid #C8D9F0; }
.rtable td { color:#142B55; border-bottom:1px solid #DCE8F8; }
.rtable tr:hover td { background:rgba(229,241,255,.55); }
.rtable tr.sel td { background:#DCEBFF; }
.chip.active { background:linear-gradient(135deg,#3F7BF2,#2457D6); color:#fff; }
.chip.done { background:#DDF7EA; color:#0F7A66; border-color:#BFEBD8; }
.chip { background:rgba(255,255,255,.75); }
.notice { background:rgba(255,255,255,.8); border-radius:16px; }
.notice.info { background:#E1EDFF; border-color:#BCD3F8; color:#142B55; }
.notice.warn { background:#FFF0E0; border-color:#F6C99A; color:#6B3A0B; }
.notice.ok { background:#DDF7EA; border-color:#BFEBD8; color:#0B5B4E; }
.art-card { background:linear-gradient(180deg,#FFF1E6 0%,#E5F6EF 60%,#E5F1FF 100%); border:1px solid rgba(255,255,255,.95); border-radius:24px; box-shadow:0 12px 30px rgba(20,43,85,.08); }
.footer { background:linear-gradient(135deg,#E5F1FF 0%,#EDE9FF 55%,#FFF1E3 100%); border-radius:24px; border-top:none; box-shadow:0 12px 30px rgba(20,43,85,.08); padding:24px 20px; }
.footer .fb { color:#142B55; } .footer .ft { color:#425B82; } .footer .fs { color:#425B82; }
div[data-testid="stVerticalBlockBorderWrapper"] { background:rgba(255,255,255,.82); border:1px solid #D4E3F7 !important; border-radius:20px; box-shadow:0 10px 26px rgba(20,43,85,.06); }
div[data-testid="stExpander"] { background:rgba(255,255,255,.75); border:1px solid #D4E3F7; border-radius:16px; }
button[data-baseweb="tab"] { color:#425B82; font-weight:700; }
button[data-baseweb="tab"][aria-selected="true"] { color:#1F4FD1; }
div[data-testid="stProgress"] > div > div > div > div { background:linear-gradient(90deg,#3F7BF2,#8757E8); }
button[kind="primary"], button[data-testid="stBaseButton-primary"] { background:linear-gradient(135deg,#3F7BF2,#2457D6); box-shadow:0 8px 20px rgba(52,120,246,.28); }
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] { background:rgba(255,255,255,.85); border:1px solid #CFE0FB; color:#142B55; }

/* responsive: stack panels on tablet and phone */
@media (max-width: 1100px) {
  .hero2 { grid-template-columns:1fr; }
  .st-key-homehero [data-testid="stHorizontalBlock"] { flex-direction:column; }
  .st-key-homehero [data-testid="stColumn"], .st-key-homehero [data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:100% !important; }
  .st-key-features [data-testid="stHorizontalBlock"], .st-key-actions [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
  .st-key-features [data-testid="stColumn"], .st-key-features [data-testid="column"] { flex:1 1 calc(50% - 1rem) !important; min-width:calc(50% - 1rem) !important; }
}
@media (max-width: 900px) {
  .st-key-shell > div > [data-testid="stHorizontalBlock"] { flex-direction:column; }
  .st-key-shell > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"], .st-key-shell > div > [data-testid="stHorizontalBlock"] > [data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:100% !important; }
  .st-key-actions [data-testid="stColumn"], .st-key-actions [data-testid="column"] { flex:1 1 100% !important; min-width:100% !important; }
  .hero2 h1 { font-size:1.8rem; }
}
@media (max-width: 640px) {
  .st-key-features [data-testid="stColumn"], .st-key-features [data-testid="column"] { flex:1 1 100% !important; min-width:100% !important; }
  .block-container { padding:.6rem .7rem 1.5rem .7rem !important; }
}
/* ===== readable form widgets (work with a light or a dark Streamlit base theme) ===== */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] span { color:#142B55 !important; font-weight:600; font-size:.96rem; line-height:1.4; }
[data-testid="stTooltipIcon"] svg, [data-testid="stTooltipHoverTarget"] svg { color:#5A7096 !important; stroke:#5A7096 !important; }
div[data-baseweb="select"] > div { background:#FFFFFF !important; border:1px solid #BCD3F8 !important; border-radius:12px !important; color:#142B55 !important; min-height:48px; }
div[data-baseweb="select"] span, div[data-baseweb="select"] div, div[data-baseweb="select"] input { color:#142B55 !important; -webkit-text-fill-color:#142B55 !important; }
div[data-baseweb="select"] svg { fill:#425B82 !important; color:#425B82 !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] [role="listbox"], div[data-baseweb="menu"] { background:#FFFFFF !important; }
div[data-baseweb="popover"] li, div[data-baseweb="popover"] [role="option"] { background:#FFFFFF !important; color:#142B55 !important; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] [role="option"]:hover, [role="option"][aria-selected="true"] { background:#E5F1FF !important; }
[data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="base-input"], [data-testid="stNumberInput"] > div > div { background:#FFFFFF !important; border:1px solid #BCD3F8 !important; border-radius:12px !important; }
[data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input, textarea { background:#FFFFFF !important; color:#142B55 !important; -webkit-text-fill-color:#142B55 !important; }
[data-testid="stNumberInput"] button { background:#E5F1FF !important; color:#142B55 !important; }
[data-testid="stNumberInput"] button svg { fill:#142B55 !important; }
[data-testid="stTextArea"] [data-baseweb="textarea"], [data-testid="stTextArea"] [data-baseweb="base-input"] { background:#FFFFFF !important; border:1px solid #BCD3F8 !important; border-radius:12px !important; }
textarea::placeholder { color:#8FA6C9 !important; -webkit-text-fill-color:#8FA6C9 !important; }
[data-testid="stSlider"] [data-testid="stSliderThumbValue"], [data-testid="stSlider"] [data-testid="stTickBarMin"], [data-testid="stSlider"] [data-testid="stTickBarMax"] { color:#142B55 !important; }
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] p, [data-testid="stCheckbox"] span { color:#142B55 !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:#425B82 !important; }
div[data-testid="stProgress"] p { color:#142B55 !important; font-weight:600; }
div[data-testid="stProgress"] [role="progressbar"] > div { background:#C9DAF3 !important; border-radius:99px; }
div[data-testid="stProgress"] [role="progressbar"] > div > div { background:linear-gradient(90deg,#3F7BF2,#8757E8) !important; border-radius:99px; }

/* assessment section header (a real question, not a small caption) */
.q-card { display:flex; gap:18px; align-items:flex-start; padding:24px 26px; border-radius:22px; background:linear-gradient(135deg,#E5F1FF 0%,#F0E7FF 60%,#FFE7D5 130%); border:1px solid rgba(255,255,255,.9); box-shadow:0 12px 30px rgba(20,43,85,.08); margin:6px 0 4px 0; }
.q-num { flex:0 0 52px; width:52px; height:52px; border-radius:16px; background:linear-gradient(135deg,#3F7BF2,#2457D6); color:#fff; font-weight:800; font-size:1.4rem; display:flex; align-items:center; justify-content:center; box-shadow:0 8px 18px rgba(52,120,246,.35); }
.q-kicker { color:#109A8A; font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; margin-bottom:4px; }
.q-title { color:#142B55; font-size:1.55rem; font-weight:800; line-height:1.25; letter-spacing:-.01em; }
.q-sub { color:#425B82; font-size:1rem; line-height:1.55; margin-top:6px; }
.q-hint { display:inline-block; margin-top:12px; padding:6px 14px; border-radius:999px; background:#FFFFFF; color:#2457D6; font-weight:700; font-size:.82rem; border:1px solid #CFE0FB; }

/* sidebar illustration + caption: stacked so no word is split */
.side-art { display:flex; flex-direction:column; align-items:center; text-align:center; gap:2px; margin:10px 0 4px 0; }
.side-art svg { width:66%; height:auto; flex:0 0 auto; display:block; }
.side-art p { margin:2px 8px 16px 8px; font-size:.88rem; line-height:1.4; word-break:normal; overflow-wrap:normal; hyphens:none; }

/* invisible helper that scrolls the page back to the top after navigation */
.st-key-scrollhook { position:absolute; height:0; width:0; overflow:hidden; margin:0; padding:0; }
/* arrows drawn with CSS (crisp, always inside the button, no font glyphs) */
.st-key-assess_next button p::after, .st-key-top_cta button p::after, .st-key-home_start button p::after, .st-key-why_iv button p::after, .st-key-iv_profile button p::after, .st-key-prof_mi button p::after, .st-key-feat_btn_0 button p::after, .st-key-feat_btn_1 button p::after, .st-key-feat_btn_2 button p::after, .st-key-feat_btn_3 button p::after {
  content:""; display:inline-block; width:18px; height:18px; margin-left:8px; vertical-align:-3px; background-color:currentColor;
  -webkit-mask:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 12h15m-6-6 6 6-6 6' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;
  mask:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 12h15m-6-6 6 6-6 6' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;
}
.st-key-feat_btn_0 button p, .st-key-feat_btn_1 button p, .st-key-feat_btn_2 button p, .st-key-feat_btn_3 button p { font-size:0; margin:0; }
.st-key-feat_btn_0 button p::after, .st-key-feat_btn_1 button p::after, .st-key-feat_btn_2 button p::after, .st-key-feat_btn_3 button p::after { margin-left:0; vertical-align:middle; }

/* Back / Next row: Back on the left edge, Next on the right edge, same size */
.st-key-assess_back button, .st-key-assess_next button { min-width:150px; min-height:46px; border-radius:14px; font-weight:700; }
.st-key-assess_next [data-testid="stButton"] { display:flex; justify-content:flex-end; }
/* feature cards: the whole card is clickable (invisible button covers it) and opens a detail page */
.st-key-feat_btn_0, .st-key-feat_btn_1, .st-key-feat_btn_2, .st-key-feat_btn_3 { position:absolute !important; top:0 !important; left:0 !important; right:0 !important; bottom:0 !important; width:100% !important; height:100% !important; z-index:5; margin:0 !important; }
.st-key-feat_btn_0 [data-testid="stButton"], .st-key-feat_btn_1 [data-testid="stButton"], .st-key-feat_btn_2 [data-testid="stButton"], .st-key-feat_btn_3 [data-testid="stButton"] { position:static !important; width:100% !important; height:100% !important; }
.st-key-feat_btn_0 button, .st-key-feat_btn_1 button, .st-key-feat_btn_2 button, .st-key-feat_btn_3 button { width:100% !important; height:100% !important; min-height:100% !important; opacity:0; border-radius:22px !important; cursor:pointer; box-shadow:none !important; }
.st-key-feat0:focus-within, .st-key-feat1:focus-within, .st-key-feat2:focus-within, .st-key-feat3:focus-within { outline:2px solid #2B63D6; outline-offset:3px; }
.feat-more { margin-top:14px; font-weight:700; font-size:.92rem; display:inline-flex; align-items:center; gap:6px; }
.feat-more::after { content:""; width:18px; height:18px; background-color:currentColor; -webkit-mask:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 12h15m-6-6 6 6-6 6' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat; mask:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 12h15m-6-6 6 6-6 6' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat; transition:transform .18s ease; }
.st-key-feat0:hover .feat-more::after, .st-key-feat1:hover .feat-more::after, .st-key-feat2:hover .feat-more::after, .st-key-feat3:hover .feat-more::after { transform:translateX(4px); }
.feat-desc { padding-right:0 !important; }
.feat-hero { display:flex; gap:22px; align-items:center; padding:26px 28px; border-radius:26px; border:1px solid rgba(255,255,255,.9); box-shadow:0 12px 30px rgba(20,43,85,.08); margin:12px 0 18px 0; }
.feat-hero .feat-ic { width:76px; height:76px; margin:0; flex:0 0 76px; }
.feat-hero .feat-ic svg { width:36px; height:36px; }
.feat-hero h2 { margin:2px 0 6px 0; font-size:1.9rem; color:#142B55; }
.feat-hero p { margin:0; color:#425B82; font-size:1.02rem; line-height:1.55; }
.feat-list { margin:8px 0 0 0; padding-left:20px; color:#425B82; line-height:1.9; }
button:focus-visible, input:focus-visible, textarea:focus-visible, [role="slider"]:focus-visible { outline:2px solid #2B63D6 !important; outline-offset:2px; }

/* ===== Cognivue additions ===== */
div[data-testid="stRadio"] label { background:#FFFFFF; border:1px solid #CFE0FB; border-radius:12px; padding:8px 14px; margin:0 2px 0 0; transition:all .15s ease; }
div[data-testid="stRadio"] label:hover { border-color:#3478F6; background:#F3F8FF; }
div[data-testid="stRadio"] label:has(input:checked) { background:#DCEBFF; border-color:#3478F6; box-shadow:0 4px 12px rgba(52,120,246,.18); }
div[data-testid="stRadio"] [role="radiogroup"] { gap:8px; flex-wrap:wrap; }
div[data-testid="stRadio"] label p { color:#142B55 !important; font-weight:600; font-size:.92rem; }
.qq-label { font-size:.72rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:#2B63D6; margin-bottom:4px; }
.qq-text { font-size:1.05rem; font-weight:600; color:#142B55; line-height:1.5; margin:0 0 8px 0; }
.q-missing { color:#D6455D; font-size:.85rem; font-weight:700; margin-top:4px; }
.scale-one { position:relative; height:14px; border-radius:999px; background:linear-gradient(90deg,#BFE3FF 0%,#D9CCFF 55%,#FFD3B8 100%); }
.scale-one .mid { position:absolute; top:-4px; width:2px; height:22px; background:#425B82; opacity:.55; }
.review-wrap { overflow-x:auto; }
.rtable td.ans { font-weight:700; }
.rtable td.miss { color:#D6455D; font-weight:700; }
</style>
"""


def md_html(markup: str) -> None:
    """Render raw HTML through Streamlit markdown (indentation stripped so
    Markdown never mistakes it for a code block)."""
    flat = "\n".join(line.strip() for line in markup.strip().splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


def esc(value) -> str:
    return htmllib.escape(str(value))


def inject_css() -> None:
    md_html(CSS)


DISCLAIMER = (
    "This research prototype estimates potential Generative AI overreliance using self-reported "
    "questionnaire responses. Results are intended for educational reflection and research decision "
    "support. They are not clinical or psychological diagnoses, do not measure actual AI prompt "
    "behaviour, and should not be used to make high-stakes decisions about students."
)


def card(title, body, icon=""):
    return f'<div class="card"><h4>{title}</h4><p>{body}</p></div>'


def stat(value, label, sub="", color=None):
    style = f' style="color:{color}"' if color else ""
    sub_html = f'<div class="s">{sub}</div>' if sub else ""
    return f'<div class="stat"><div class="v"{style}>{value}</div><div class="l">{label}</div>{sub_html}</div>'


def section_title(title, sub=""):
    md_html(f'<div class="section-title">{title}</div>' + (f'<div class="section-sub">{sub}</div>' if sub else ""))


def notice(text, kind="info"):
    md_html(f'<div class="notice {kind}">{text}</div>')


def themed_fig(width=7.5, height=4.0):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor(C_CARD)
    ax.set_facecolor(C_CARD)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=C_MUTED, labelsize=9, length=0)
    ax.grid(color="#D3E2F5", linewidth=0.7, alpha=0.85)
    ax.set_axisbelow(True)
    ax.xaxis.label.set_color(C_MUTED)
    ax.yaxis.label.set_color(C_MUTED)
    ax.title.set_color(C_TEXT)
    return fig, ax


def show_fig(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def chart_card(question):
    """Bordered container headed by the question the chart answers."""
    box = st.container(border=True)
    box.markdown(f"**{question}**")
    return box


def footer() -> None:
    md_html(
        f"""
        <div class="footer"><div class="fb">Cognivue AI</div>
        <div class="ft">AI-Based Framework for Detecting Generative AI Overreliance and Providing Adaptive Interventions</div>
        <div class="fs">{DISCLAIMER}</div></div>
        """
    )