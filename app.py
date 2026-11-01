
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Cognivue AI | Learning Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #080D18;
    color: #F1F5F9;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

section[data-testid="stSidebar"] {
    background: #101827;
    border-right: 1px solid #243047;
}

section[data-testid="stSidebar"] * {
    color: #E2E8F0;
}

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 25px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -1px;
}

.brand span {
    color: #8B9CFF;
}

.eyebrow {
    color: #A5B4FC;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(38px, 5vw, 65px);
    line-height: 1.12;
    font-weight: 800;
    letter-spacing: -2.5px;
    color: #F8FAFC;
    margin-top: 15px;
    margin-bottom: 20px;
}

.gradient-text {
    background: linear-gradient(90deg, #A5B4FC, #67E8F9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    font-size: 17px;
    line-height: 1.8;
    color: #A8B4C8;
    max-width: 720px;
}

.section-title {
    font-family: 'Manrope', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.8px;
}

.section-description {
    color: #94A3B8;
    line-height: 1.7;
}

.feature-card {
    background: linear-gradient(145deg, #131F33, #101827);
    border: 1px solid #263650;
    border-radius: 16px;
    padding: 23px;
    min-height: 190px;
}

.feature-icon {
    font-size: 27px;
    margin-bottom: 15px;
}

.feature-heading {
    font-size: 17px;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 9px;
}

.feature-text {
    color: #A3B2C7;
    font-size: 14px;
    line-height: 1.7;
}

.info-panel {
    background: #111C2D;
    border: 1px solid #263650;
    border-radius: 16px;
    padding: 25px;
}

.footer {
    color: #718096;
    font-size: 12px;
    text-align: center;
    padding: 30px 0 10px 0;
    border-top: 1px solid #263650;
}

div.stButton > button {
    background: linear-gradient(90deg, #6366F1, #818CF8);
    color: white;
    border: none;
    border-radius: 9px;
    padding: 12px 25px;
    font-weight: 700;
    min-height: 48px;
}

div.stButton > button:hover {
    border: 1px solid #A5B4FC;
    color: white;
    background: #4F46E5;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        '<div class="brand">Cognivue<span> AI</span></div>',
        unsafe_allow_html=True
    )

    st.caption("LEARNING INTELLIGENCE PLATFORM")

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Home",
            "Assessment",
            "Results",
            "Explainable AI",
            "Interventions",
            "About"
        ],
        index=0
    )

    st.markdown("---")

    st.markdown("**Research Prototype**")
    st.caption(
        "An AI-based framework for understanding "
        "Generative AI overreliance in student learning."
    )

    st.markdown("---")
    st.caption("Cognivue AI · 2026")


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "Home":

    st.markdown(
        '<div class="eyebrow">UNDERSTAND YOUR LEARNING. '
        'USE AI MINDFULLY.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-title">
            Think independently.<br>
            <span class="gradient-text">
                Learn intelligently.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-description">
            Discover how your Generative AI usage relates to
            your independent learning, verification habits and
            metacognitive strategies. Get an evidence-informed
            assessment with explainable insights and adaptive
            learning recommendations.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button("Start Your Assessment  →", key="home_assessment"):
        st.session_state["selected_page"] = "Assessment"
        st.rerun()

    st.write("")
    st.write("")

    st.markdown(
        '<div class="section-title">What Cognivue AI offers</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'A structured approach to understanding your AI-assisted '
        'learning behaviour.'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-heading">
                Learning Assessment
            </div>
            <div class="feature-text">
                Answer questions about your GenAI usage,
                independent learning, verification and
                metacognitive habits.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-heading">
                Predictive Insights
            </div>
            <div class="feature-text">
                Explore an estimated overreliance score
                generated using our trained machine learning
                model.
            </div>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-heading">
                Explainable AI
            </div>
            <div class="feature-text">
                Understand the factors that contributed
                to your model's prediction through
                explainable AI.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-heading">
                Adaptive Interventions
            </div>
            <div class="feature-text">
                Receive learning recommendations designed
                to encourage independent thinking,
                verification and self-testing.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.markdown(
        '<div class="info-panel">'
        '<div class="section-title">Our approach</div>'
        '<p class="feature-text">'
        'Cognivue AI combines machine learning, clustering '
        'and explainable AI to examine self-reported learning '
        'patterns. Its predictions are research estimates, '
        'not clinical assessments or diagnoses.'
        '</p></div>',
        unsafe_allow_html=True
    )

    st.write("")
    st.markdown(
        '<div class="footer">'
        'COGNIVUE AI · AI-BASED FRAMEWORK FOR DETECTING '
        'GENERATIVE AI OVERRELIANCE AND PROVIDING '
        'ADAPTIVE INTERVENTIONS<br><br>'
        'Research prototype · 2026'
        '</div>',
        unsafe_allow_html=True
    )


# --------------------------------------------------
# PLACEHOLDER PAGES
# --------------------------------------------------

elif page == "Assessment":
    st.title("Student Assessment")
    st.info(
        "The questionnaire will be integrated using "
        "your existing Colab preprocessing design."
    )

elif page == "Results":
    st.title("Assessment Results")
    st.info("Your prediction dashboard will appear here.")

elif page == "Explainable AI":
    st.title("Explainable AI")
    st.info("SHAP explanations will appear here.")

elif page == "Interventions":
    st.title("Adaptive Interventions")
    st.info("Personalized learning recommendations will appear here.")

elif page == "About":
    st.title("About Cognivue AI")

    st.markdown("""
    Cognivue AI is a research prototype designed to
    investigate patterns of Generative AI overreliance
    in student learning.

    **Research components:**
    - Random Forest Regression
    - K-Means Clustering
    - Deep Learning comparison
    - SHAP Explainable AI
    - Adaptive Intervention Framework

    **Important:** This system uses self-reported
    questionnaire responses. Its output is an estimate,
    not a clinical diagnosis or proof of cognitive decline.
    """)
