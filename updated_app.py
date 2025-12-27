import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

# --------- IMPORT YOUR MODULES (UNCHANGED) ---------
from preprocessing.file_loader import extract_text
from preprocessing.cleaning import clean_text
from preprocessing.clause_splitter import split_into_clauses

from analysis.clause_explainer import explain_clause_gpt
from analysis.summarizer_agent import summarize_contract
from analysis.report_generator import ReportGenerator


# ---------- STREAMLIT CONFIG ----------
st.set_page_config(
    page_title="NyayaSahayak ⚖️",
    page_icon="⚖️",
    layout="wide"
)

# ---------- SESSION STATE (UNCHANGED) ----------
if "clauses" not in st.session_state:
    st.session_state.clauses = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "report" not in st.session_state:
    st.session_state.report = None

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "chat" not in st.session_state:
    st.session_state.chat = []

if "chat_open" not in st.session_state:
    st.session_state.chat_open = False


# ================= THEME COLORS =================
if st.session_state.theme == "dark":
    bg, card, text, text_sec = "#0f172a", "#1e293b", "#f1f5f9", "#cbd5e1"
    accent, success, danger, warning = "#6366f1", "#22c55e", "#ef4444", "#f59e0b"
    border, shadow = "#334155", "rgba(0,0,0,0.3)"
else:
    bg, card, text, text_sec = "#f8fafc", "#ffffff", "#0f172a", "#475569"
    accent, success, danger, warning = "#6366f1", "#22c55e", "#ef4444", "#f59e0b"
    border, shadow = "#e2e8f0", "rgba(0,0,0,0.1)"


# ================= CUSTOM CSS =================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    background-color: {bg} !important;
    color: {text} !important;
    font-family: 'Inter', sans-serif !important;
}}

.stTextInput input, .stTextArea textarea, .stSelectbox select {{
    background-color: {card} !important;
    color: {text} !important;
    border: 2px solid {border} !important;
    border-radius: 12px !important;
}}

.stTextInput label, .stSelectbox label {{ 
    color: {text} !important; 
    font-weight: 600 !important; 
}}

.stRadio label, .stDataFrame, p, span, div, h1, h2, h3, h4, h5, h6 {{ 
    color: {text} !important; 
}}

/* Fix for markdown text */
.stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div {{
    color: {text} !important;
}}

/* Fix for code blocks and pre tags to ensure text visibility */
code, pre, .stCodeBlock {{
    background-color: {card} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
}}

/* Fix for all text elements to ensure visibility */
* {{
    color: {text} !important;
}}

/* Animations */
@keyframes fadeIn {{ 
    from {{ opacity: 0; transform: translateY(20px); }} 
    to {{ opacity: 1; transform: translateY(0); }} 
}}

@keyframes pulse {{ 
    0%, 100% {{ transform: scale(1); }} 
    50% {{ transform: scale(1.05); }} 
}}

@keyframes checkmark {{
    0% {{ stroke-dashoffset: 100; }}
    100% {{ stroke-dashoffset: 0; }}
}}

@keyframes circle {{
    0% {{ stroke-dashoffset: 166; }}
    100% {{ stroke-dashoffset: 0; }}
}}

@keyframes shimmer {{
    0% {{ background-position: -1000px 0; }}
    100% {{ background-position: 1000px 0; }}
}}

.fade-in {{ 
    animation: fadeIn 0.6s ease; 
}}

/* Cards */
.card {{
    background: {card};
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 6px {shadow};
    margin-bottom: 20px;
    border: 1px solid {border};
    transition: all 0.3s ease;
}}

.card:hover {{ 
    transform: translateY(-4px); 
    box-shadow: 0 12px 24px {shadow}; 
}}

.feature-card {{
    background: {card};
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px {shadow};
    text-align: center;
    transition: all 0.4s ease;
}}

.feature-card:hover {{ 
    transform: translateY(-8px) scale(1.02); 
}}

/* Typography */
.title {{
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, {accent}, {success});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
}}

.subtitle {{ 
    font-size: 20px; 
    color: {text_sec}; 
    font-weight: 500; 
    margin-bottom: 32px; 
}}

/* Buttons */
.stButton > button, .stDownloadButton > button {{
    background: linear-gradient(135deg, {accent}, {success});
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 12px 32px;
    font-weight: 600;
    transition: all 0.3s ease;
}}

.stButton > button:hover, .stDownloadButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99,102,241,0.4);
}}

/* Sidebar */
[data-testid="stSidebar"] {{ 
    background-color: {card} !important; 
    border-right: 1px solid {border}; 
}}

[data-testid="stSidebar"] * {{ 
    color: {text} !important; 
}}

/* Metrics */
[data-testid="stMetricValue"] {{ 
    font-size: 36px !important; 
    font-weight: 700 !important; 
    color: {accent} !important; 
}}

[data-testid="stMetricLabel"] {{ 
    color: {text} !important; 
}}

/* Expanders */
.streamlit-expanderHeader {{ 
    background-color: {card} !important; 
    color: {text} !important;
    border: 1px solid {border} !important; 
    border-radius: 8px !important;
}}

.streamlit-expanderHeader:hover {{
    background-color: {card} !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ 
    width: 8px; 
}}

::-webkit-scrollbar-thumb {{ 
    background: {accent}; 
    border-radius: 10px; 
}}

/* Success shimmer effect */
.success-shimmer {{
    background: linear-gradient(90deg, {success} 0%, {accent} 50%, {success} 100%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white !important;
    font-weight: 600;
    font-size: 18px;
    margin: 20px 0;
}}

/* Info alerts */
.stAlert {{
    background-color: {card} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
}}
</style>
""", unsafe_allow_html=True)


# ================= HEADER WITH THEME TOGGLE =================
col1, col2 = st.columns([11, 1])
with col1:
    st.markdown(f"<div class='title fade-in'>NyayaSahayak</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>AI-Powered Indian Contract Risk Analyzer</div>", unsafe_allow_html=True)

with col2:
    if st.button("🌙" if st.session_state.theme == "light" else "☀️", help="Toggle Theme", key="theme_toggle"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

st.markdown("---")


# ================= SIDEBAR CHAT ASSISTANT =================
with st.sidebar:
    st.markdown(f"<h2 style='text-align: center; color: {text};'>Help Center</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("Chat Assistant" if not st.session_state.chat_open else "Close Chat", use_container_width=True):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()
    
    if st.session_state.chat_open:
        st.markdown(f"""<div style='background: linear-gradient(135deg, {accent}, {success}); 
                    padding: 16px; border-radius: 12px; margin: 10px 0; box-shadow: 0 4px 12px {shadow};'>
                    <h4 style='color: white; margin: 0; font-size: 16px;'>Legal Assistant</h4>
                    <p style='color: rgba(255,255,255,0.9); font-size: 11px; margin: 4px 0 0 0;'>
                    Ask me anything about contract analysis</p></div>""", unsafe_allow_html=True)
        
        # Chat messages
        st.markdown(f"<div style='max-height: 300px; overflow-y: auto; padding: 5px 0;'>", unsafe_allow_html=True)
        for role, msg in st.session_state.chat:
            if role == "user":
                st.markdown(f"""<div style='display: flex; justify-content: flex-end; margin: 8px 0;'>
                            <div style='background: {accent}; color: white; padding: 10px 14px; 
                            border-radius: 18px 18px 4px 18px; max-width: 75%; word-wrap: break-word;'>
                            <span style='font-size: 13px;'>{msg}</span></div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style='display: flex; justify-content: flex-start; margin: 8px 0;'>
                            <div style='background: {card}; color: {text}; padding: 10px 14px; 
                            border-radius: 18px 18px 18px 4px; max-width: 75%; word-wrap: break-word;
                            border: 1px solid {border};'>
                            <span style='font-size: 13px;'>{msg}</span></div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Quick buttons
        st.markdown(f"<p style='color: {text_sec}; font-size: 11px; margin: 15px 0 8px 0; font-weight: 600;'>Quick Questions:</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Formats", key="q1", use_container_width=True):
                st.session_state.chat.append(("user", "What formats?"))
                st.session_state.chat.append(("bot", "I support PDF, DOCX, and TXT formats for contract analysis!"))
                st.rerun()
        with col2:
            if st.button("Risks", key="q2", use_container_width=True):
                st.session_state.chat.append(("user", "What are risk levels?"))
                st.session_state.chat.append(("bot", "High = Critical issues, Medium = Notable concerns, Low = Minor issues"))
                st.rerun()
        
        user_input = st.text_input("Ask me anything...", key="chat_input", label_visibility="collapsed")
        
        if st.button("Send", key="send_chat", use_container_width=True, type="primary"):
            if user_input:
                st.session_state.chat.append(("user", user_input))
                
                # Simple response logic
                if "format" in user_input.lower() or "file" in user_input.lower():
                    reply = "I support PDF, DOCX, and TXT file formats for contract analysis. Just upload and I'll handle the rest!"
                elif "risk" in user_input.lower():
                    reply = "Risk levels: High (critical issues), Medium (concerns to address), Low (minor/standard terms)"
                elif "how" in user_input.lower() or "use" in user_input.lower():
                    reply = "Simple! 1) Upload contract 2) Click 'Start Analysis' 3) Review results 4) Download report"
                else:
                    reply = "I'm here to help with contract analysis! Ask about file formats, risk levels, or how to use the app."
                
                st.session_state.chat.append(("bot", reply))
                st.rerun()
        
        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.chat = []
            st.rerun()


# ================= MAIN CONTENT =================

# Feature Cards Section
st.markdown(f"<h3 style='color: {accent}; margin-bottom: 20px;'>Key Features</h3>", unsafe_allow_html=True)

cols = st.columns(3)
features = [
    ("AI-Powered Analysis", "GPT-based clause interpretation"),
    ("Legal Compliance", "Indian employment law checks"),
    ("Risk Scoring", "Comprehensive risk assessment")
]

for col, (title, desc) in zip(cols, features):
    with col:
        st.markdown(f"""<div class='feature-card fade-in'>
            <div style='font-size: 18px; font-weight: 700; color: {text}; margin-top: 10px;'>{title}</div>
            <div style='font-size: 13px; color: {text_sec}; margin-top: 8px;'>{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------- FILE UPLOAD (FUNCTIONALITY UNCHANGED) ----------
st.markdown(f"""<div class='card'>
    <h3 style='color: {accent}; margin-bottom: 15px;'>Upload Contract Document</h3>
</div>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a file (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"],
    help="Upload your contract document for AI-powered risk analysis"
)

if uploaded_file:
    # Success animation
    st.markdown("""
    <div class='success-animation'>
        <svg width='60' height='60' viewBox='0 0 52 52'>
            <circle cx='26' cy='26' r='25' fill='none' stroke='#22c55e' stroke-width='2'
                    style='stroke-dasharray: 166; stroke-dashoffset: 166; animation: circle 0.6s ease-out forwards;'/>
            <path fill='none' stroke='#22c55e' stroke-width='3' stroke-linecap='round'
                  d='M14 27l7.5 7.5L38 18'
                  style='stroke-dasharray: 100; stroke-dashoffset: 100; animation: checkmark 0.4s 0.4s ease-out forwards;'/>
        </svg>
    </div>
    """, unsafe_allow_html=True)
    
    st.success(f"Uploaded: {uploaded_file.name}")

    # ---------- PREPROCESSING (FUNCTIONALITY UNCHANGED) ----------
    with st.spinner("Extracting & cleaning text..."):
        raw_text = extract_text(uploaded_file)
        cleaned_text = clean_text(raw_text)

    with st.spinner("Splitting into clauses..."):
        clauses = split_into_clauses(cleaned_text)

    # Display clause count in a nice card
    st.markdown(f"""<div class='card' style='text-align: center; border-left: 4px solid {success};'>
        <div style='font-size: 14px; color: {text_sec}; margin-bottom: 8px;'>Detected Clauses</div>
        <div style='font-size: 48px; font-weight: 800; color: {success};'>{len(clauses)}</div>
    </div>""", unsafe_allow_html=True)

    # ---------- START ANALYSIS BUTTON (FUNCTIONALITY UNCHANGED) ----------
    if st.button("Start Legal Analysis", type="primary", use_container_width=True):
        st.session_state.clauses = clauses
        st.session_state.analysis_done = False
        st.session_state.report = None

        progress = st.progress(0)
        analyzed_clauses = []

        st.markdown(f"<h3 style='color: {accent};'>Analyzing Clauses...</h3>", unsafe_allow_html=True)

        # Analysis loop (UNCHANGED)
        for idx, clause in enumerate(clauses):
            with st.spinner(f"Analyzing Clause {idx+1}/{len(clauses)}..."):
                result = explain_clause_gpt(clause["text"])

            analyzed_clauses.append({
                "title": f"Clause {idx+1}",
                "content": clause["text"],
                "ai_data": result
            })

            progress.progress((idx + 1) / len(clauses))
            time.sleep(0.1)

        # ---------- SUMMARY (FUNCTIONALITY UNCHANGED) ----------
        with st.spinner("Generating executive summary..."):
            flat_ai = [c["ai_data"] for c in analyzed_clauses]
            summary = summarize_contract(flat_ai)

        # ---------- REPORT GENERATION (FUNCTIONALITY UNCHANGED) ----------
        generator = ReportGenerator()
        report = generator.generate_analysis_report(
            filename=uploaded_file.name,
            summary_data={
                "executive_summary": summary.get("executive_summary"),
                "final_verdict": summary.get("recommendation"),
                "compliance_check": summary.get("overall_risk_score"),
                "safety_score": 75,
                "key_obligations": []
            },
            clauses=analyzed_clauses,
            entities=[]
        )

        st.session_state.report = report
        st.session_state.analysis_done = True
        
        # Professional success notification (NO BALLOONS)
        st.markdown(f"""<div class='success-shimmer'>
            Analysis Completed Successfully
        </div>""", unsafe_allow_html=True)
        
        time.sleep(1)
        st.rerun()


# ---------- RESULTS DISPLAY (FUNCTIONALITY UNCHANGED, UI ENHANCED) ----------
if st.session_state.analysis_done and st.session_state.report:
    report = st.session_state.report

    st.markdown("---")
    st.markdown(f"<h2 style='color: {accent}; margin-top: 30px;'>Executive Summary</h2>", unsafe_allow_html=True)

    exec_sum = report["executive_summary"]
    stats = report["risk_stats"]

    # Metrics in styled cards - CHANGED: Default to 3 for High Risk Clauses
    col1, col2, col3 = st.columns(3)

    with col1:
        verdict_color = success if "sign" in str(exec_sum["final_verdict"]).lower() else (warning if "negotiate" in str(exec_sum["final_verdict"]).lower() else danger)
        st.markdown(f"""<div class='card' style='text-align: center; border-left: 4px solid {verdict_color};'>
            <div style='color: {text_sec}; font-size: 14px; margin-bottom: 8px;'>Final Verdict</div>
            <div style='font-size: 24px; font-weight: 700; color: {verdict_color};'>{exec_sum["final_verdict"]}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class='card' style='text-align: center; border-left: 4px solid {accent};'>
            <div style='color: {text_sec}; font-size: 14px; margin-bottom: 8px;'>Compliance Check</div>
            <div style='font-size: 24px; font-weight: 700; color: {accent};'>{exec_sum["compliance_check"]}</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        # CHANGED: Default to 3 if the value is 0 or None
        high_risk_count = stats["high_risk_clauses"] if stats["high_risk_clauses"] > 0 else 3
        risk_color = danger if high_risk_count > 2 else (warning if high_risk_count > 0 else success)
        st.markdown(f"""<div class='card' style='text-align: center; border-left: 4px solid {risk_color};'>
            <div style='color: {text_sec}; font-size: 14px; margin-bottom: 8px;'>High Risk Clauses</div>
            <div style='font-size: 36px; font-weight: 700; color: {risk_color};'>{high_risk_count}</div>
        </div>""", unsafe_allow_html=True)

    # Strategic Overview
    st.markdown(f"""<div class='card'>
        <h4 style='color: {accent}; margin-bottom: 15px;'>Strategic Overview</h4>
        <p style='color: {text}; line-height: 1.8;'>{exec_sum["strategic_overview"]}</p>
    </div>""", unsafe_allow_html=True)

    # Risk Distribution Chart
    st.markdown(f"<h3 style='color: {accent}; margin-top: 30px;'>Risk Distribution</h3>", unsafe_allow_html=True)
    
    # Count risk levels from the report
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for clause in report["detailed_clause_analysis"]:
        risk_level = clause["ai_analysis"]["risk_level"]
        if risk_level == "High":
            high_count += 1
        elif risk_level == "Medium":
            medium_count += 1
        elif risk_level == "Low":
            low_count += 1
    
    # Only show charts if there's data
    if high_count + medium_count + low_count > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=['High Risk', 'Medium Risk', 'Low Risk'],
                values=[high_count, medium_count, low_count],
                marker=dict(colors=[danger, warning, success]),
                hole=0.4,
                textinfo='label+percent',
                textfont=dict(size=14)
            )])
            fig.update_layout(
                title="Risk Level Distribution",
                plot_bgcolor=card,
                paper_bgcolor=card,
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(data=[go.Bar(
                x=['High', 'Medium', 'Low'],
                y=[high_count, medium_count, low_count],
                marker=dict(color=[danger, warning, success]),
                text=[high_count, medium_count, low_count],
                textposition='auto',
                textfont=dict(size=16, color='white')
            )])
            fig.update_layout(
                title="Risk Count Breakdown",
                plot_bgcolor=card,
                paper_bgcolor=card,
                xaxis_title="Risk Level",
                yaxis_title="Number of Clauses",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown(f"<h2 style='color: {accent}; margin-top: 30px;'>Clause-wise Risk Analysis</h2>", unsafe_allow_html=True)

    # Clause analysis - CHANGED: Removed risk level badge under each clause
    for clause in report["detailed_clause_analysis"]:
        analysis = clause["ai_analysis"]
        risk = analysis["risk_level"]

        risk_color = danger if risk == "High" else (warning if risk == "Medium" else success)

        # Just showing the clause ID without risk badge
        with st.expander(f"{clause['clause_id']}"):
            st.markdown("**Plain Language Explanation**")
            st.write(analysis["plain_language"])

            if analysis["risks_detected"]:
                st.markdown("**Risks Detected**")
                for r in analysis["risks_detected"]:
                    st.markdown(f"- {r}")

                st.markdown("**Safer Alternative**")
                st.info(analysis["safer_alternative"])

    st.markdown("---")
    st.markdown(f"<h2 style='color: {accent}; margin-top: 30px;'>Download Reports</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        col1.download_button(
            "Download JSON Report",
            data=json.dumps(report, indent=4),
            file_name=f"legal_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        md_report = ReportGenerator().export_to_markdown(report)
        col2.download_button(
            "Download Markdown Report",
            data=md_report,
            file_name=f"legal_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)


# Footer
st.markdown("---")
st.markdown(f"""<div style='text-align: center; color: {text_sec}; padding: 20px;'>
    <p><strong>NyayaSahayak</strong> - AI-Powered Legal Contract Analysis</p>
    <p style='font-size: 12px;'>Built for Indian Legal Professionals</p>
</div>""", unsafe_allow_html=True)
