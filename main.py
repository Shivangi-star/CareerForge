import streamlit as st

st.set_page_config(
    page_title="CareerForge - AI Career Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply High-Contrast Modern Dark Theme CSS
st.markdown("""
<style>
    /* Main Backdrop */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%) !important;
        color: #f8fafc !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(17, 24, 39, 0.95) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    
    /* Universal Text & Labels */
    h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown, .stMarkdown p {
        color: #f8fafc !important;
    }
    
    .hero-title {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1.3rem;
        color: #cbd5e1 !important;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Custom Card Glassmorphism */
    .feature-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(129, 140, 248, 0.5);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.25);
    }

    .feature-icon {
        font-size: 2.6rem;
        margin-bottom: 0.8rem;
        display: inline-block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff !important;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 1rem;
        color: #cbd5e1 !important;
        line-height: 1.5;
    }
    
    .badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-purple { background: rgba(168, 85, 247, 0.25); color: #e9d5ff !important; border: 1px solid rgba(168, 85, 247, 0.4); }
    .badge-indigo { background: rgba(99, 102, 241, 0.25); color: #c7d2fe !important; border: 1px solid rgba(99, 102, 241, 0.4); }
    .badge-emerald { background: rgba(16, 185, 129, 0.25); color: #a7f3d0 !important; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-amber { background: rgba(245, 158, 11, 0.25); color: #fde68a !important; border: 1px solid rgba(245, 158, 11, 0.4); }
    
    /* Form Inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    .stTextInput label, .stTextArea label, .stRadio label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    ::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.65) !important;
    }
    
    /* Metric Card */
    .stat-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
    }
    .stat-val { font-size: 1.9rem; font-weight: 800; color: #818cf8 !important; }
    .stat-lbl { font-size: 0.9rem; color: #cbd5e1 !important; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# Sidebar Branding
with st.sidebar:
    st.markdown("## ⚡ CareerForge")
    st.caption("AI-Powered Placement Prep Toolkit")
    st.markdown("---")
    st.markdown("### 📌 Navigation Quick Guide")
    st.markdown("""
    Select a module from the sidebar menu to begin:
    - **📄 1. Resume ATS Scanner**
    - **🎤 2. AI Mock Interviewer**
    - **💻 3. Coding Practice**
    - **🧠 4. Aptitude & Proctoring**
    """)
    st.markdown("---")
    st.info("💡 **Local AI Powered**: Mock Interviews & Resume analysis run using local LLM models.")

# Main Hero Header
col_hero, col_stats = st.columns([2, 1])

with col_hero:
    st.markdown('<div class="hero-title">CareerForge</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Forge your career path with AI-driven interview practice, ATS resume auditing, live proctored aptitude tests & coding prep.</div>', unsafe_allow_html=True)

with col_stats:
    s1, s2 = st.columns(2)
    with s1:
        st.markdown('''
        <div class="stat-card">
            <div class="stat-val">4 Modules</div>
            <div class="stat-lbl">Full Toolkit</div>
        </div>
        ''', unsafe_allow_html=True)
    with s2:
        st.markdown('''
        <div class="stat-card">
            <div class="stat-val">100%</div>
            <div class="stat-lbl">Private & Fast</div>
        </div>
        ''', unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🛠️ Career Tooling Suite")

c1, c2 = st.columns(2)

with c1:
    st.markdown('''
    <div class="feature-card">
        <span class="badge badge-purple">AI Powered</span>
        <div class="feature-icon">📄</div>
        <div class="feature-title">Resume ATS Analyzer</div>
        <div class="feature-desc">Upload your resume alongside target job descriptions. Get instant ATS compatibility score, missing keywords analysis, and HR feedback.</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("🚀 Launch Resume ATS", key="btn_ats"):
        st.switch_page("pages/1_Resume_ATS.py")

    st.markdown('''
    <div class="feature-card">
        <span class="badge badge-emerald">Interactive</span>
        <div class="feature-icon">💻</div>
        <div class="feature-title">Coding Practice</div>
        <div class="feature-desc">Master Data Structures & Algorithms with categorized coding problems, test cases, solution explanations, and progress metrics.</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("🚀 Launch Coding Practice", key="btn_coding"):
        st.switch_page("pages/3_Coding_Practice.py")

with c2:
    st.markdown('''
    <div class="feature-card">
        <span class="badge badge-indigo">Vision & Speech</span>
        <div class="feature-icon">🎤</div>
        <div class="feature-title">AI Mock Interview</div>
        <div class="feature-desc">Simulate realistic technical interviews with real-time audio response transcription, face tracking, and LLM feedback.</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("🚀 Launch Mock Interview", key="btn_mock"):
        st.switch_page("pages/2_Mock_Interview.py")

    st.markdown('''
    <div class="feature-card">
        <span class="badge badge-amber">Live Proctoring</span>
        <div class="feature-icon">🧠</div>
        <div class="feature-title">Aptitude & Proctoring Test</div>
        <div class="feature-desc">Take General & Technical aptitude assessments with live gaze & multi-face detection proctoring, detailed score breakdowns, and analytics.</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("🚀 Launch Aptitude Module", key="btn_apti"):
        st.switch_page("pages/4_Aptitude.py")

st.markdown("---")
st.caption("CareerForge v2.0 • High-Contrast Design & Performance Upgrade")