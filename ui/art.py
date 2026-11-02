"""ui/art.py - SVG illustrations (same set as the earlier project)."""

HERO_ART = """<svg viewBox="0 0 560 390" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A student using a laptop with an AI assistant, message cards and a behaviour analytics chart">
<defs>
<linearGradient id="hb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4C8DFF"/><stop offset="1" stop-color="#2457D6"/></linearGradient>
<linearGradient id="hh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3F7BF2"/><stop offset="1" stop-color="#2B5FDB"/></linearGradient>
<radialGradient id="hg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
</defs>
<circle cx="330" cy="150" r="150" fill="#F3EDFF" opacity=".75"/><circle cx="250" cy="250" r="130" fill="#FFEBDD" opacity=".7"/>
<circle cx="330" cy="130" r="92" fill="url(#hg)"/>
<g fill="none" stroke="#4C8DFF" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="1 8">
<path d="M150 82 C 190 70, 230 80, 276 104"/><path d="M384 108 C 420 84, 440 80, 468 84"/><path d="M372 160 C 400 170, 418 182, 438 200"/><path d="M220 215 C 238 190, 262 168, 292 150"/>
</g>
<g><rect x="80" y="42" width="110" height="72" rx="14" fill="#FFFFFF" stroke="#D7E5FA"/><rect x="96" y="58" width="42" height="32" rx="9" fill="#4C8DFF"/><path d="M106 90 l-6 10 l14 -6z" fill="#4C8DFF"/><rect x="104" y="68" width="26" height="4" rx="2" fill="#fff"/><rect x="104" y="76" width="18" height="4" rx="2" fill="#fff"/><rect x="148" y="62" width="30" height="5" rx="2.5" fill="#C9D9F3"/><rect x="148" y="74" width="24" height="5" rx="2.5" fill="#C9D9F3"/></g>
<g><rect x="440" y="52" width="104" height="70" rx="14" fill="#FFFFFF" stroke="#D7E5FA"/><rect x="456" y="68" width="72" height="6" rx="3" fill="#C9D9F3"/><rect x="456" y="82" width="72" height="6" rx="3" fill="#C9D9F3"/><rect x="456" y="96" width="48" height="6" rx="3" fill="#C9D9F3"/></g>
<circle cx="330" cy="130" r="58" fill="#FFFFFF" stroke="#DCE8FA" stroke-width="3"/>
<circle cx="330" cy="122" r="34" fill="url(#hb)"/>
<g fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M322 112 c-8 0 -10 8 -6 12 c-5 3 -3 12 4 12 h2"/><path d="M338 112 c8 0 10 8 6 12 c5 3 3 12 -4 12 h-2"/><path d="M330 108 v32"/><path d="M322 122 h8 M330 130 h8"/></g>
<text x="330" y="188" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12.5" font-weight="700" fill="#142B55">AI</text><text x="330" y="203" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12.5" font-weight="700" fill="#142B55">Assistant</text>
<g><rect x="446" y="188" width="96" height="92" rx="14" fill="#FFFFFF" stroke="#D7E5FA"/>
<rect x="458" y="238" width="14" height="30" rx="3" fill="#8757E8"/><rect x="478" y="226" width="14" height="42" rx="3" fill="#3478F6"/><rect x="498" y="212" width="14" height="56" rx="3" fill="#109A8A"/><rect x="518" y="200" width="14" height="68" rx="3" fill="#109A8A" opacity=".75"/>
<path d="M458 232 L480 214 L498 222 L530 196" fill="none" stroke="#F4A261" stroke-width="2.6" stroke-linecap="round"/><circle cx="530" cy="196" r="4" fill="#F4A261"/></g>
<text x="492" y="304" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="11" font-weight="700" fill="#142B55">Behaviour Analysis</text>
<rect x="30" y="338" width="360" height="9" rx="4.5" fill="#CFE0F6"/>
<g><rect x="42" y="324" width="104" height="14" rx="3" fill="#109A8A"/><rect x="50" y="311" width="92" height="13" rx="3" fill="#7ED6A8"/><rect x="46" y="298" width="98" height="13" rx="3" fill="#4C8DFF"/><rect x="52" y="318" width="26" height="2.5" fill="#fff" opacity=".7"/></g>
<g><path d="M118 300 C 96 270, 104 246, 116 228 C 128 250, 132 276, 118 300Z" fill="#5BBF8E"/><path d="M118 300 C 138 276, 150 262, 168 256 C 162 280, 142 296, 118 300Z" fill="#3FA574"/><path d="M118 300 C 92 292, 76 276, 70 258 C 94 262, 112 278, 118 300Z" fill="#7CD1A0"/></g>
<path d="M150 342 C 170 300, 188 280, 214 268 L 258 268 C 262 290, 262 320, 266 342Z" fill="url(#hh)"/>
<path d="M196 270 C 204 286, 226 286, 236 270 L 226 262 L 206 262Z" fill="#2457D6"/>
<rect x="206" y="236" width="22" height="30" rx="9" fill="#FFD2B0"/>
<circle cx="214" cy="218" r="27" fill="#FFD7B5"/>
<path d="M186 214 C 184 186, 210 176, 230 188 C 244 196, 246 210, 240 218 C 234 206, 222 200, 208 202 C 198 204, 190 208, 186 214Z" fill="#1B2A55"/>
<path d="M190 200 C 196 178, 226 178, 238 196" fill="none" stroke="#1B2A55" stroke-width="8" stroke-linecap="round"/>
<circle cx="224" cy="222" r="2.6" fill="#1B2A55"/><path d="M222 233 q6 5 12 0" fill="none" stroke="#C97B5A" stroke-width="2" stroke-linecap="round"/>
<g><rect x="262" y="262" width="104" height="70" rx="8" fill="#2A3A6B" transform="rotate(-8 262 332)"/><circle cx="312" cy="296" r="7" fill="#7F93C9" opacity=".8" transform="rotate(-8 262 332)"/>
<path d="M248 336 L388 336 L376 346 L238 346Z" fill="#1B2A55"/></g>
<path d="M244 296 C 256 316, 272 328, 292 334" fill="none" stroke="#3F7BF2" stroke-width="13" stroke-linecap="round"/>
<g><path d="M372 336 q-3 -22 6 -32 q8 10 6 32z" fill="#7CD1A0"/><path d="M380 336 q8 -16 22 -18 q-2 14 -22 18z" fill="#3FA574"/><rect x="368" y="334" width="22" height="14" rx="4" fill="#C9B8F2"/></g>
</svg>"""

COLLAB_ART = """<svg viewBox="0 0 320 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A student collaborating with an AI assistant in a calm landscape">
<defs><linearGradient id="cs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE9D2"/><stop offset=".6" stop-color="#E3F6EE"/><stop offset="1" stop-color="#DDEBFF"/></linearGradient>
<linearGradient id="c1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7CC7A0"/><stop offset="1" stop-color="#4FA982"/></linearGradient>
<linearGradient id="c2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AD8B8"/><stop offset="1" stop-color="#6CBF97"/></linearGradient>
<radialGradient id="cg"><stop offset="0" stop-color="#FFE29A" stop-opacity=".9"/><stop offset="1" stop-color="#FFE29A" stop-opacity="0"/></radialGradient></defs>
<rect width="320" height="210" fill="url(#cs)"/>
<circle cx="190" cy="62" r="62" fill="url(#cg)"/><circle cx="190" cy="62" r="26" fill="#FFD27A"/>
<path d="M0 120 C 50 70, 96 78, 140 112 C 180 84, 230 70, 320 118 L320 210 L0 210Z" fill="#B7DFC9"/>
<path d="M0 150 C 60 118, 110 126, 170 150 C 220 126, 270 124, 320 146 L320 210 L0 210Z" fill="url(#c2)"/>
<path d="M0 178 C 70 156, 130 162, 200 180 C 250 166, 290 168, 320 178 L320 210 L0 210Z" fill="url(#c1)"/>
<g fill="#3C9A76"><path d="M30 150 C 20 120, 30 100, 42 90 C 52 108, 54 130, 46 152Z"/><path d="M52 154 C 52 130, 64 112, 76 106 C 80 126, 74 144, 62 156Z"/><path d="M270 152 C 262 124, 272 106, 286 98 C 294 118, 292 138, 282 154Z"/></g>
<g fill="#2F8A66"><path d="M18 156 C 10 134, 18 118, 28 112 C 36 126, 38 142, 32 158Z"/><path d="M296 156 C 300 136, 306 124, 316 120 C 318 136, 314 148, 306 158Z"/></g>
<g><path d="M96 200 C 98 170, 124 160, 148 164 C 168 168, 176 186, 176 200Z" fill="#3F7BF2"/><circle cx="136" cy="146" r="17" fill="#FFD7B5"/><path d="M119 144 C 118 126, 138 120, 150 130 C 156 136, 154 146, 152 150 C 146 140, 130 138, 119 144Z" fill="#1B2A55"/><rect x="120" y="178" width="58" height="34" rx="6" fill="#2A3A6B"/></g>
<g><circle cx="226" cy="126" r="26" fill="#FFFFFF" stroke="#DCE8FA" stroke-width="3"/><circle cx="226" cy="126" r="16" fill="#3478F6"/><path d="M219 122 q4 -6 8 0 q4 -4 7 2 M219 130 q4 6 8 0 q4 4 7 -2" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></g>
<path d="M156 140 C 180 120, 196 118, 202 124" fill="none" stroke="#3478F6" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="1 7"/>
<rect x="244" y="86" width="40" height="26" rx="8" fill="#FFFFFF" opacity=".95"/><rect x="252" y="94" width="24" height="4" rx="2" fill="#C9D9F3"/><rect x="252" y="102" width="16" height="4" rx="2" fill="#C9D9F3"/>
</svg>"""

SIDE_ART = """<svg viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A plant growing from a pot beside stacked books">
<defs><linearGradient id="sp" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D9C9FA"/><stop offset="1" stop-color="#A98CF0"/></linearGradient></defs>
<ellipse cx="112" cy="144" rx="100" ry="5" fill="#BFD3EE" opacity=".6"/>
<g><path d="M60 150 L 66 112 L 112 112 L 118 150Z" fill="url(#sp)"/><rect x="58" y="104" width="62" height="12" rx="6" fill="#C7B3F7"/></g>
<g><path d="M89 108 C 66 98, 58 72, 66 50 C 86 62, 94 86, 89 108Z" fill="#4FB68A"/><path d="M89 108 C 100 82, 116 62, 138 54 C 138 82, 118 102, 89 108Z" fill="#3AA175"/><path d="M89 108 C 74 108, 54 98, 44 82 C 66 80, 84 90, 89 108Z" fill="#6FCB9E"/><path d="M89 108 C 90 80, 92 56, 100 34 C 112 58, 108 88, 89 108Z" fill="#5BC092"/></g>
<g><rect x="132" y="130" width="92" height="16" rx="3" fill="#2F6BF0"/><rect x="140" y="114" width="80" height="16" rx="3" fill="#3F86F5"/><rect x="136" y="98" width="86" height="16" rx="3" fill="#1F3F9E"/><rect x="140" y="104" width="30" height="3" fill="#fff" opacity=".6"/><rect x="146" y="136" width="30" height="3" fill="#fff" opacity=".6"/></g>
</svg>"""

LOGO_SVG = """<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3F7BF2"/><stop offset="1" stop-color="#17358F"/></linearGradient></defs><rect width="48" height="48" rx="13" fill="url(#lg)"/><path d="M24 11 L41 19 L24 27 L7 19Z" fill="#FFFFFF"/><path d="M14 24 V31 C 18 35, 30 35, 34 31 V24 L24 29Z" fill="#DCE8FF"/><path d="M41 19 V30" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/></svg>"""

_ART_DEFS = '<defs><linearGradient id="ag" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3478F6"/><stop offset="1" stop-color="#8757E8"/></linearGradient><linearGradient id="abg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E5F1FF"/><stop offset="1" stop-color="#F0E7FF"/></linearGradient></defs>'
_ART_HEAD = '<svg viewBox="0 0 300 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true">' + _ART_DEFS + '<rect width="300" height="190" fill="url(#abg)"/>'

ART = {
    "collab": _ART_HEAD + '''
<circle cx="150" cy="100" r="76" fill="#109A8A" opacity=".07"/>
<circle cx="76" cy="84" r="21" fill="#142B55" opacity=".92"/><path d="M40 156 Q76 102 112 156 Z" fill="url(#ag)"/>
<polygon points="226,64 254,80 254,112 226,128 198,112 198,80" fill="#FFFFFF" stroke="url(#ag)" stroke-width="3"/>
<text x="226" y="102" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif" font-size="18" font-weight="800" fill="#109A8A">AI</text>
<path d="M112 104 Q154 70 198 96" stroke="#109A8A" stroke-width="2" stroke-dasharray="4 5" fill="none"><animate attributeName="stroke-dashoffset" from="18" to="0" dur="1.5s" repeatCount="indefinite"/></path>
<circle cx="154" cy="86" r="5" fill="#3478F6"/><circle cx="154" cy="38" r="12" fill="none" stroke="#2B63D6" stroke-width="2.5"/><path d="M149 52 h10" stroke="#2B63D6" stroke-width="3"/>
</svg>''',
    "think": _ART_HEAD + '''
<circle cx="150" cy="86" r="62" fill="#8757E8" opacity=".08"/>
<circle cx="150" cy="80" r="30" fill="none" stroke="#2B63D6" stroke-width="3"/><path d="M138 116 h24 M141 124 h18" stroke="#2B63D6" stroke-width="3" stroke-linecap="round"/>
<path d="M150 28 v-10 M108 44 l-8 -7 M192 44 l8 -7" stroke="#2B63D6" stroke-width="2.5" stroke-linecap="round"/>
<g stroke="#3478F6" stroke-width="1.6" opacity=".8"><line x1="150" y1="80" x2="70" y2="140"/><line x1="150" y1="80" x2="230" y2="140"/><line x1="70" y1="140" x2="150" y2="162"/><line x1="230" y1="140" x2="150" y2="162"/></g>
<circle cx="70" cy="140" r="9" fill="#3478F6"/><circle cx="230" cy="140" r="9" fill="#8757E8"/><circle cx="150" cy="162" r="9" fill="#109A8A"/>
</svg>''',
    "gauge": _ART_HEAD + '''
<path d="M70 150 A80 80 0 0 1 129.3 72.7" stroke="#16A34A" stroke-width="15" fill="none" opacity=".85"/>
<path d="M129.3 72.7 A80 80 0 0 1 190 80.7" stroke="#3478F6" stroke-width="15" fill="none" opacity=".9"/>
<path d="M190 80.7 A80 80 0 0 1 230 150" stroke="#D97706" stroke-width="15" fill="none" opacity=".85"/>
<line x1="150" y1="150" x2="158" y2="88" stroke="#142B55" stroke-width="3" stroke-linecap="round"/><circle cx="150" cy="150" r="8" fill="#142B55"/>
<g font-family="Inter,Segoe UI,sans-serif" font-size="11" fill="#425B82" text-anchor="middle"><text x="70" y="172">1</text><text x="150" y="176">Low · Moderate · High</text><text x="230" y="172">7</text></g>
</svg>''',
    "xai": _ART_HEAD + '''
<line x1="150" y1="22" x2="150" y2="170" stroke="#425B82" stroke-width="1.5"/>
<rect x="150" y="34" width="86" height="18" rx="5" fill="#D97706"/><rect x="150" y="62" width="58" height="18" rx="5" fill="#D97706" opacity=".85"/>
<rect x="150" y="90" width="34" height="18" rx="5" fill="#D97706" opacity=".7"/>
<rect x="76" y="118" width="74" height="18" rx="5" fill="#109A8A"/><rect x="104" y="146" width="46" height="18" rx="5" fill="#109A8A" opacity=".8"/>
<g font-family="Inter,Segoe UI,sans-serif" font-size="10" fill="#425B82"><text x="30" y="30">lower</text><text x="238" y="30">higher</text></g>
</svg>''',
    "path": _ART_HEAD + '''
<rect x="30" y="132" width="40" height="30" rx="5" fill="#B9C9E6"/><rect x="74" y="112" width="40" height="50" rx="5" fill="#B9C9E6"/>
<rect x="118" y="92" width="40" height="70" rx="5" fill="#3478F6" opacity=".8"/><rect x="162" y="72" width="40" height="90" rx="5" fill="#8757E8" opacity=".85"/>
<rect x="206" y="52" width="40" height="110" rx="5" fill="url(#ag)"/>
<circle cx="226" cy="36" r="6" fill="#109A8A"/><path d="M226 30 v-14 l14 5 l-14 5" fill="#2B63D6"/>
<path d="M50 120 L94 100 L138 80 L182 60 L226 42" stroke="#109A8A" stroke-width="2" stroke-dasharray="4 5" fill="none"/>
</svg>''',
    "radar": _ART_HEAD + '''
<polygon points="150,30 216.6,78.4 191.1,156.6 108.9,156.6 83.4,78.4" fill="none" stroke="#C8D9F0" stroke-width="1.5"/>
<polygon points="150,65 183.3,89.2 170.5,128.3 129.5,128.3 116.7,89.2" fill="none" stroke="#C8D9F0" stroke-width="1.2"/>
<polygon points="150,44 186.6,88.1 178.8,139.6 113,151 110.1,87" fill="#109A8A" fill-opacity=".2" stroke="#109A8A" stroke-width="2.2"/>
<g fill="#109A8A"><circle cx="150" cy="44" r="4"/><circle cx="186.6" cy="88.1" r="4"/><circle cx="178.8" cy="139.6" r="4"/><circle cx="113" cy="151" r="4"/><circle cx="110.1" cy="87" r="4"/></g>
</svg>''',
    "lab": _ART_HEAD + '''
<path d="M40 30 V160 H262" stroke="#425B82" stroke-width="1.6" fill="none"/>
<g fill="#3478F6" opacity=".9"><circle cx="70" cy="132" r="4"/><circle cx="95" cy="118" r="4"/><circle cx="118" cy="124" r="4"/><circle cx="142" cy="98" r="4"/><circle cx="170" cy="92" r="4"/><circle cx="198" cy="70" r="4"/><circle cx="226" cy="64" r="4"/></g>
<path d="M56 140 L240 56" stroke="#109A8A" stroke-width="2.2" stroke-dasharray="5 5" fill="none"/>
<rect x="196" y="116" width="14" height="44" fill="#8757E8" opacity=".8"/><rect x="216" y="100" width="14" height="60" fill="#8757E8" opacity=".8"/><rect x="236" y="130" width="14" height="30" fill="#8757E8" opacity=".8"/>
</svg>''',
}


ART_FOR_PAGE = {
    "Home": ("collab", "Human\u2013AI collaboration", "AI as a learning assistant, with the student still doing the thinking."),
    "Assess": ("think", "Independent thinking", "Reflect on how you work with AI. Your answers stay in this session."),
    "Results": ("gauge", "From behaviour to estimate", "A continuous 1\u20135 estimate from your self-reported habits."),
    "Why This Result?": ("xai", "Explainable AI", "SHAP shows which answers moved the model's estimate up or down."),
    "Intervention": ("path", "Adaptive learning support", "Rule-based activities that encourage independent reasoning."),
    "Behavioural Insights": ("radar", "Behavioural insights", "Your self-reported habits across four learning dimensions."),
    "Model Insights": ("lab", "Research laboratory", "Validation, baselines, experiments and explainability."),
    "Research": ("lab", "Research laboratory", "Dataset, methods, experiments and honest limitations."),
    "Testing": ("lab", "Testing and validation", "Automated checks that the pipeline reproduces the Colab results."),
    "About": ("collab", "Human\u2013AI collaboration", "Promoting responsible AI-assisted learning."),
}