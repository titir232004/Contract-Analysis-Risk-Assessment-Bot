
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
from io import BytesIO

from preprocessing import preprocess_contract
from clause_explainer import explain_clause_gpt
from risk_scorer import RiskScorer

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ContractShield AI", layout="wide", page_icon="⚖️")

# ================= SESSION STATE =================
for key, default in [("clauses", None), ("analysis", None), ("history", []), ("theme", "light"), ("chat", []), ("chat_open", False), ("overall_score", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ================= HELPER FUNCTIONS =================
def analyze_contract_with_gpt(clauses):
    """Analyze contract using GPT-based clause explainer"""
    results = []
    all_risks = []
    
    for idx, clause in enumerate(clauses):
        # Get GPT analysis
        gpt_result = explain_clause_gpt(clause['text'])
        
        # Map risk level to scoring weight
        risk_weights = {"High": 15, "Medium": 8, "Low": 3, "Unknown": 5}
        risk_level = gpt_result.get('risk_level', 'Unknown')
        weight = risk_weights.get(risk_level, 5)
        
        # Store risk for scoring
        all_risks.append({
            'clause_id': idx + 1,
            'risk_level': risk_level,
            'weight': weight
        })
        
        # Format result for display
        result = {
            'clause_id': idx + 1,
            'text': clause['text'],
            'risk_level': risk_level,
            'explanation': gpt_result.get('plain_language', 'No explanation available'),
            'key_points': gpt_result.get('key_points', []),
            'risks': '\n'.join(gpt_result.get('risks_detected', ['No risks detected'])),
            'suggested_alternative': gpt_result.get('safer_alternative', 'No alternative suggested')
        }
        results.append(result)
    
    # Calculate overall risk score
    scorer = RiskScorer()
    overall_score = scorer.calculate_score(all_risks)
    risk_category = scorer.get_risk_level(overall_score)
    
    return results, overall_score, risk_category
def generate_summary_text():
    """Generate text summary for download"""
    high = sum(1 for r in st.session_state.analysis if r["risk_level"] == "High")
    medium = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Medium")
    low = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Low")
    
    summary = f"""CONTRACT ANALYSIS REPORT - ContractShield AI
Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}

EXECUTIVE SUMMARY
{'='*60}
Overall Risk Score: {st.session_state.overall_score}/100
Risk Category: {st.session_state.risk_category}

Total Clauses Analyzed: {len(st.session_state.analysis)}
High Risk Clauses: {high}
Medium Risk Clauses: {medium}
Low Risk Clauses: {low}

DETAILED CLAUSE ANALYSIS
{'='*60}

"""
    for r in st.session_state.analysis:
        key_points_text = '\n'.join([f"  • {point}" for point in r.get('key_points', [])])
        
        summary += f"""
Clause {r['clause_id']} - {r['risk_level']} Risk
{'-'*60}
Original Text:
{r['text']}

Plain Language Explanation:
{r['explanation']}

Key Points:
{key_points_text if key_points_text else '  • No key points identified'}

Risks Detected:
{r['risks']}

Safer Alternative:
{r['suggested_alternative']}

{'='*60}
"""
    return summary

def generate_csv_report():
    """Generate CSV report"""
    data = [{
        'Clause ID': r['clause_id'],
        'Risk Level': r['risk_level'],
        'Text': r['text'],
        'Explanation': r['explanation'],
        'Key Points': ', '.join(r.get('key_points', [])),
        'Risks': r['risks'],
        'Suggested Alternative': r['suggested_alternative']
    } for r in st.session_state.analysis]
    return pd.DataFrame(data).to_csv(index=False, escapechar='\\', quoting=1).encode('utf-8')

def show_success_animation():
    """Custom success animation"""
    st.markdown("""
    <style>
    @keyframes checkmark {
        0% { stroke-dashoffset: 100; }
        100% { stroke-dashoffset: 0; }
    }
    @keyframes circle {
        0% { stroke-dashoffset: 166; }
        100% { stroke-dashoffset: 0; }
    }
    @keyframes fadeInScale {
        0% { opacity: 0; transform: scale(0.5); }
        100% { opacity: 1; transform: scale(1); }
    }
    .success-animation {
        animation: fadeInScale 0.5s ease-out;
    }
    </style>
    <div style='display: flex; justify-content: center; align-items: center; padding: 20px;'>
        <svg class='success-animation' width='80' height='80' viewBox='0 0 52 52' style='border-radius: 50%;'>
            <circle cx='26' cy='26' r='25' fill='none' stroke='#22c55e' stroke-width='2'
                    style='stroke-dasharray: 166; stroke-dashoffset: 166; animation: circle 0.6s ease-out forwards;'/>
            <path fill='none' stroke='#22c55e' stroke-width='3' stroke-linecap='round'
                  d='M14 27l7.5 7.5L38 18'
                  style='stroke-dasharray: 100; stroke-dashoffset: 100; animation: checkmark 0.4s 0.4s ease-out forwards;'/>
        </svg>
    </div>
    """, unsafe_allow_html=True)

# ================= THEME COLORS =================
if st.session_state.theme == "dark":
    bg, card, text, text_sec = "#0f172a", "#1e293b", "#f1f5f9", "#cbd5e1"
    accent, success, danger, warning = "#6366f1", "#22c55e", "#ef4444", "#f59e0b"
    border, shadow = "#334155", "rgba(0,0,0,0.3)"
    chat_bg = "#0f172a"
else:
    bg, card, text, text_sec = "#f8fafc", "#ffffff", "#0f172a", "#475569"
    accent, success, danger, warning = "#6366f1", "#22c55e", "#ef4444", "#f59e0b"
    border, shadow = "#e2e8f0", "rgba(0,0,0,0.1)"
    chat_bg = "#ffffff"

# ================= CSS =================
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
.stTextInput label, .stSelectbox label {{ color: {text} !important; font-weight: 600 !important; }}
.stRadio label, .stDataFrame, p, span, div {{ color: {text} !important; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes slideIn {{ from {{ opacity: 0; transform: translateX(100px); }} to {{ opacity: 1; transform: translateX(0); }} }}
@keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} }}
.fade-in {{ animation: fadeIn 0.6s ease; }}
.card {{
    background: {card};
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 6px {shadow};
    margin-bottom: 20px;
    border: 1px solid {border};
    transition: all 0.3s ease;
}}
.card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px {shadow}; }}
.feature-card {{
    background: {card};
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px {shadow};
    text-align: center;
    transition: all 0.4s ease;
}}
.feature-card:hover {{ transform: translateY(-8px) scale(1.02); }}
.title {{
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, {accent}, {success});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
}}
.subtitle {{ font-size: 20px; color: {text_sec}; font-weight: 500; margin-bottom: 32px; }}
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
[data-testid="stSidebar"] {{ background-color: {card} !important; border-right: 1px solid {border}; }}
[data-testid="stSidebar"] * {{ color: {text} !important; }}
[data-testid="stMetricValue"] {{ font-size: 36px !important; font-weight: 700 !important; color: {accent} !important; }}
[data-testid="stMetricLabel"] {{ color: {text} !important; }}
.streamlit-expanderHeader {{ background-color: {card} !important; color: {text} !important; border: 1px solid {border} !important; }}
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-thumb {{ background: {accent}; border-radius: 10px; }}

.chat-toggle-btn {{
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, {accent}, {success});
    color: white;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    transition: all 0.3s ease;
    animation: pulse 2s infinite;
    z-index: 9999;
}}

.chat-toggle-btn:hover {{
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(99,102,241,0.6);
}}
</style>
""", unsafe_allow_html=True)

# ================= HEADER WITH THEME TOGGLE =================
col1, col2 = st.columns([11, 1])
with col2:
    if st.button("🌙" if st.session_state.theme == "light" else "☀️", help="Toggle Theme"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# ================= SIDEBAR =================
st.sidebar.markdown(f"<h1 style='text-align: center; color: {text};'>ContractShield AI</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", ["Overview", "Upload", "Preprocessing", "Risk Analysis", "Clause Insights", "Summary", "History"], label_visibility="collapsed")

# ================= CHAT IN SIDEBAR =================
with st.sidebar:
    st.markdown("---")
    if st.button("Help Assistant" if not st.session_state.chat_open else "Close Chat", use_container_width=True):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()
    
    if st.session_state.chat_open:
        st.markdown(f"""<div style='background: linear-gradient(135deg, {accent}, {success}); 
                    padding: 16px; border-radius: 12px; margin: 10px 0; box-shadow: 0 4px 12px {shadow};'>
                    <h4 style='color: white; margin: 0; font-size: 16px;'>Contract Assistant</h4>
                    <p style='color: rgba(255,255,255,0.9); font-size: 11px; margin: 4px 0 0 0;'>
                    Specialized in contract analysis</p></div>""", unsafe_allow_html=True)
        
        # Chat messages container with scroll
        st.markdown(f"<div style='max-height: 300px; overflow-y: auto; padding: 5px 0;'>", unsafe_allow_html=True)
        for role, msg in st.session_state.chat:
            if role == "user":
                st.markdown(f"""<div style='display: flex; justify-content: flex-end; margin: 8px 0;'>
                            <div style='background: {accent}; color: white; padding: 10px 14px; 
                            border-radius: 18px 18px 4px 18px; max-width: 75%; word-wrap: break-word;
                            box-shadow: 0 2px 8px rgba(99,102,241,0.3);'>
                            <span style='font-size: 13px; line-height: 1.5;'>{msg}</span></div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style='display: flex; justify-content: flex-start; margin: 8px 0;'>
                            <div style='background: {card}; color: {text}; padding: 10px 14px; 
                            border-radius: 18px 18px 18px 4px; max-width: 75%; word-wrap: break-word;
                            border: 1px solid {border}; box-shadow: 0 2px 6px {shadow};'>
                            <span style='font-size: 13px; line-height: 1.5;'>{msg}</span></div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Quick question buttons
        st.markdown(f"<p style='color: {text_sec}; font-size: 11px; margin: 15px 0 8px 0; font-weight: 600;'>Suggested Questions:</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Formats", key="q1", use_container_width=True):
                st.session_state.chat.append(("user", "What file formats are supported?"))
                st.session_state.chat.append(("bot", "I support PDF, DOCX, and TXT file formats for contract analysis. Simply upload your contract document in any of these formats from the Upload page, and I'll extract and analyze all clauses automatically."))
                st.rerun()
            if st.button("Risks", key="q2", use_container_width=True):
                st.session_state.chat.append(("user", "What do risk levels mean?"))
                st.session_state.chat.append(("bot", "Risk Levels:\n\n• HIGH: Critical issues that could significantly harm your interests. Requires immediate legal review and negotiation.\n\n• MEDIUM: Notable concerns that should be carefully considered. May need modifications.\n\n• LOW: Minor issues or standard terms that are generally acceptable in contracts."))
                st.rerun()
        with col2:
            if st.button("Reports", key="q3", use_container_width=True):
                st.session_state.chat.append(("user", "How do I download reports?"))
                st.session_state.chat.append(("bot", "After running your analysis, navigate to the Summary page using the sidebar. You'll find two download options: TXT format (detailed narrative report) and CSV format (spreadsheet with all data). Both contain complete clause analysis, risk assessments, and recommendations."))
                st.rerun()
            if st.button("Guide", key="q4", use_container_width=True):
                st.session_state.chat.append(("user", "How do I use this app?"))
                st.session_state.chat.append(("bot", "Quick Start Guide:\n\n1. Upload: Go to Upload page, select your contract file\n2. Preprocess: View clause extraction statistics (optional)\n3. Analyze: Click 'Run Analysis' on Risk Analysis page\n4. Review: Check Clause Insights for detailed findings\n5. Export: Download reports from Summary page\n\nNeed help with any step?"))
                st.rerun()
        
        # Input area with better styling
        st.markdown(f"<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        user_input = st.text_input("", key="chat_input", 
                                   placeholder="Ask about contracts, risks, features...",
                                   label_visibility="collapsed")
        
        # Buttons in single row
        send_clicked = st.button("Send Message", key="send_chat", use_container_width=True, type="primary")
        
        if send_clicked and user_input:
            st.session_state.chat.append(("user", user_input))
            
            # Enhanced response logic with context awareness
            user_lower = user_input.lower()
            
            # Check current state for context-aware responses
            has_clauses = st.session_state.clauses is not None
            has_analysis = st.session_state.analysis is not None
            
            # Contract types questions
            if any(word in user_lower for word in ["contract", "type", "kind", "support", "handle", "agreement"]):
                reply = "I specialize in analyzing various contract types:\n\n• Employment Agreements\n• Non-Disclosure Agreements (NDAs)\n• Service Agreements\n• Vendor Contracts\n• Lease Agreements\n• Purchase Agreements\n• Partnership Agreements\n• Licensing Agreements\n\nAny legal document with clauses can be analyzed for potential risks and unfavorable terms!"
            
            # Risk-related questions
            elif any(word in user_lower for word in ["risk", "high", "medium", "low", "danger", "level"]):
                reply = "Risk Level Classification:\n\n🔴 HIGH RISK\nCritical issues that could significantly harm your interests, such as:\n- Unlimited liability clauses\n- Severe penalty terms\n- Unfair termination rights\n- Intellectual property losses\n→ Requires immediate legal review\n\n🟡 MEDIUM RISK\nNotable concerns that should be considered:\n- Ambiguous terms\n- One-sided obligations\n- Unclear payment terms\n→ Should be negotiated\n\n🟢 LOW RISK\nMinor issues or standard terms:\n- Common boilerplate clauses\n- Fair and balanced terms\n→ Generally acceptable"
            
            # Preprocessing questions
            elif any(word in user_lower for word in ["preprocess", "extract", "clause", "split", "segment"]):
                reply = "Preprocessing is the first analysis stage where I:\n\n1. Extract text from your document (PDF/DOCX/TXT)\n2. Identify clause boundaries using AI\n3. Segment the contract into individual clauses\n4. Calculate statistics (word count, clause distribution)\n5. Prepare data for risk analysis\n\nThis allows precise, clause-by-clause analysis rather than reviewing the entire document as one block. You can view extraction statistics on the Preprocessing page!"
            
            # Download/Export questions
            elif any(word in user_lower for word in ["download", "export", "report", "save", "print"]):
                reply = "Report Download Options:\n\n📄 TXT Report\n- Comprehensive narrative format\n- Includes all clause details\n- Explanations and recommendations\n- Easy to read and share\n\n📊 CSV Report\n- Spreadsheet format\n- Structured data columns\n- Perfect for Excel analysis\n- Sortable and filterable\n\nBoth reports contain: Clause ID, Risk Level, Original Text, Explanation, Identified Risks, and Suggested Alternatives. Available on Summary page after analysis!"
            
            # File format questions
            elif any(word in user_lower for word in ["format", "file", "pdf", "docx", "txt", "upload", "size"]):
                reply = "Supported File Formats:\n\n✓ PDF (.pdf) - Most common for contracts\n✓ DOCX (.docx) - Microsoft Word documents\n✓ TXT (.txt) - Plain text files\n\nRecommendations:\n- File size: Typically under 10MB works best\n- Quality: Clear, readable text (not scanned images)\n- Language: English contracts only\n- Structure: Properly formatted with clause breaks\n\nUpload from the Upload page in the sidebar!"
            
            # How to use / Tutorial
            elif any(word in user_lower for word in ["how", "use", "start", "tutorial", "guide", "step", "begin"]):
                if not has_clauses:
                    reply = "📚 Complete Usage Guide:\n\nSTEP 1: Upload Contract\n- Navigate to 'Upload' page\n- Click 'Choose a file'\n- Select your contract (PDF/DOCX/TXT)\n- Wait for automatic extraction\n\nSTEP 2: Review Statistics (Optional)\n- Go to 'Preprocessing' page\n- View clause distribution\n- Check word count analysis\n\nSTEP 3: Run AI Analysis\n- Navigate to 'Risk Analysis'\n- Click 'Run Analysis' button\n- Wait for AI assessment (20-30 seconds)\n\nSTEP 4: Review Results\n- Check 'Clause Insights' for details\n- Filter by risk level\n- Read explanations and alternatives\n\nSTEP 5: Download Reports\n- Go to 'Summary' page\n- Download TXT or CSV report\n- Share with legal team if needed\n\n👉 Start now by uploading a contract!"
                elif not has_analysis:
                    reply = "✅ Great! Your contract is uploaded.\n\n📍 Next Step: Run Analysis\n\n1. Go to 'Risk Analysis' page (use sidebar)\n2. Click the 'Run Analysis' button\n3. Wait 20-30 seconds for AI processing\n4. Review results on 'Clause Insights'\n\nThe AI will assess each clause for:\n- Risk level (High/Medium/Low)\n- Potential issues\n- Plain-language explanations\n- Suggested alternatives\n\nReady to analyze?"
                else:
                    reply = "🎉 Your analysis is complete!\n\n📊 What you can do now:\n\n1. REVIEW DETAILS\n→ Go to 'Clause Insights'\n→ Filter by risk level\n→ Read each clause analysis\n\n2. VIEW SUMMARY\n→ Go to 'Summary' page\n→ See overall risk distribution\n→ Check recommendations\n\n3. DOWNLOAD REPORTS\n→ TXT format for detailed review\n→ CSV format for data analysis\n\n4. ANALYZE ANOTHER CONTRACT\n→ Go to 'Upload' page\n→ Upload a new document\n\nNeed help understanding any specific clause?"
            
            # Analysis questions
            elif any(word in user_lower for word in ["analy", "assess", "check", "review", "ai", "algorithm"]):
                if not has_clauses:
                    reply = "🤖 AI Analysis Process:\n\nOur advanced AI engine:\n\n1. Reads each clause individually\n2. Identifies legal language patterns\n3. Detects unfavorable terms\n4. Assesses potential risks\n5. Compares against fair standards\n6. Generates plain-language explanations\n7. Suggests balanced alternatives\n\nThe analysis considers:\n- Liability limitations\n- Termination rights\n- Payment terms\n- Intellectual property\n- Confidentiality obligations\n- Dispute resolution\n- Force majeure clauses\n\n📤 To begin: Upload your contract on the Upload page!"
                elif not has_analysis:
                    reply = f"📂 Contract Ready for Analysis!\n\nYour document has {len(st.session_state.clauses)} extracted clauses.\n\n🚀 Next: Run Analysis\n\nGo to 'Risk Analysis' page and click 'Run Analysis'. The AI will:\n\n✓ Evaluate each clause\n✓ Identify risks\n✓ Provide explanations\n✓ Suggest improvements\n\nEstimated time: 20-30 seconds\n\nReady to proceed?"
                else:
                    high_count = sum(1 for r in st.session_state.analysis if r["risk_level"] == "High")
                    medium_count = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Medium")
                    low_count = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Low")
                    reply = f"✅ Analysis Complete!\n\n📊 Results Summary:\n\n🔴 High Risk: {high_count} clauses\n🟡 Medium Risk: {medium_count} clauses\n🟢 Low Risk: {low_count} clauses\n\nTotal Clauses: {len(st.session_state.analysis)}\n\n{'⚠️ Recommendation: Legal review strongly advised' if high_count > 0 else '✓ Contract appears acceptable'}\n\n📍 Next Steps:\n- Review 'Clause Insights' for details\n- Download reports from 'Summary'\n- Consult legal professional if needed"
            
            # Specific clause questions
            elif any(word in user_lower for word in ["clause", "term", "provision", "section"]):
                if has_analysis:
                    reply = f"Your contract has {len(st.session_state.analysis)} analyzed clauses.\n\n🔍 To review specific clauses:\n\n1. Go to 'Clause Insights' page\n2. Use the risk filter dropdown\n3. Expand any clause to see:\n   - Original clause text\n   - Risk assessment\n   - Detailed explanation\n   - Identified concerns\n   - Suggested alternatives\n\nYou can filter by:\n- All clauses\n- High risk only\n- Medium risk only\n- Low risk only\n\nWhich clauses would you like to focus on?"
                else:
                    reply = "Clauses are individual provisions or sections in your contract. Each clause covers specific terms like:\n\n- Payment obligations\n- Delivery terms\n- Warranties\n- Liability limitations\n- Termination rights\n- Confidentiality\n- Dispute resolution\n\nI analyze each clause separately to identify risks and provide targeted recommendations. Upload a contract to see clause-by-clause analysis!"
            
            # Legal/lawyer questions
            elif any(word in user_lower for word in ["legal", "lawyer", "attorney", "advice", "professional"]):
                reply = "⚖️ Important Notice:\n\nI provide AI-powered contract analysis to help you understand risks, but:\n\n❗ I am NOT a substitute for legal advice\n❗ Always consult a qualified attorney for:\n   - Legal interpretation\n   - Binding decisions\n   - Court proceedings\n   - Complex negotiations\n\n✓ I CAN help you:\n   - Identify potential risks\n   - Understand clause implications\n   - Prepare questions for your lawyer\n   - Save review time\n   - Make informed decisions\n\nFor high-risk clauses, professional legal review is strongly recommended!"
            
            # Help/General
            elif any(word in user_lower for word in ["help", "what", "can you", "feature", "capability"]):
                reply = "🤖 I'm your Contract Analysis Assistant!\n\nI can help you with:\n\n📄 CONTRACT ANALYSIS\n- Upload and extract clauses\n- AI risk assessment\n- Plain-language explanations\n- Alternative suggestions\n\n📊 FEATURES\n- Support PDF, DOCX, TXT formats\n- Multiple contract types\n- Clause-by-clause review\n- Risk level classification\n- Statistical insights\n- Export reports (TXT/CSV)\n\n💡 INFORMATION\n- How to use the platform\n- Understanding risk levels\n- Preprocessing details\n- Download instructions\n\n❓ Ask me anything about:\n- Contract types\n- Risk assessment\n- Platform features\n- Usage guidance\n\nWhat would you like to know?"
            
            # Context-aware default
            else:
                if not has_clauses:
                    reply = "👋 Welcome! I'm your Contract Analysis Assistant.\n\nI can help you:\n\n✓ Analyze contract risks\n✓ Understand complex clauses\n✓ Get plain-language explanations\n✓ Navigate the platform\n\n🚀 To get started:\n1. Upload a contract (Upload page)\n2. Or ask me questions about:\n   - Supported file formats\n   - Risk levels\n   - How to use features\n   - Contract types\n\nWhat would you like to do?"
                elif not has_analysis:
                    reply = f"📂 Your contract is uploaded ({len(st.session_state.clauses)} clauses extracted)!\n\n🎯 Next Step: Run Analysis\n\nGo to 'Risk Analysis' page and click 'Run Analysis' to begin AI assessment.\n\n💬 Or ask me:\n- What will the analysis show?\n- How long does it take?\n- What are risk levels?\n- Any other questions!\n\nHow can I help you?"
                else:
                    high_count = sum(1 for r in st.session_state.analysis if r["risk_level"] == "High")
                    reply = f"✅ Your contract analysis is complete!\n\n📊 Found {high_count} high-risk clauses out of {len(st.session_state.analysis)} total.\n\n💬 I can help you:\n- Understand specific clauses\n- Explain risk levels\n- Guide through results\n- Download reports\n- Analyze another contract\n\nWhat would you like to know?"
            
            st.session_state.chat.append(("bot", reply))
            st.rerun()
        
        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.chat = []
            st.rerun()

# =================================================
# PAGES
# =================================================

if page == "Overview":
    st.markdown(f"<div class='title fade-in'>ContractShield AI</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Intelligent Contract Analysis for Risk Protection</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    cols = st.columns(3)
    features = [
        ("📄", "Multi-Contract Support", "Handle multiple contract types with ease"),
        ("🧠", "Plain Language Analysis", "Understand complex clauses instantly"),
        ("⚠️", "Risk Detection", "Tailored analysis for SMEs")
    ]
    
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""<div class='feature-card fade-in'>
                <div style='font-size: 48px;'>{icon}</div>
                <div style='font-size: 20px; font-weight: 700; color: {text}; margin-top: 15px;'>{title}</div>
                <div style='font-size: 14px; color: {text_sec}; margin-top: 10px;'>{desc}</div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""<div class='card fade-in'>
        <h3 style='color: {accent}; margin-bottom: 15px;'>How It Works</h3>
        <ol style='color: {text}; line-height: 2;'>
            <li><strong>Upload:</strong> Submit your contract document (PDF, DOCX, or TXT)</li>
            <li><strong>Preprocessing:</strong> AI automatically extracts and segments clauses</li>
            <li><strong>Analysis:</strong> Advanced algorithms assess risk levels for each clause</li>
            <li><strong>Review:</strong> Get plain-language explanations and recommendations</li>
            <li><strong>Export:</strong> Download comprehensive reports for your records</li>
        </ol>
    </div>""", unsafe_allow_html=True)

elif page == "Upload":
    st.markdown(f"<div class='title fade-in'>Upload Contract</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Upload your contract document to begin analysis</div>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"], help="Supported formats: PDF, DOCX, TXT")
    
    if uploaded_file:
        with st.spinner("Extracting clauses from your document..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            st.session_state.clauses = preprocess_contract(uploaded_file)
            progress.empty()
        
        show_success_animation()
        st.success(f"Successfully extracted {len(st.session_state.clauses)} clauses from your document")
        
        st.markdown(f"""<div class='card'>
            <h4 style='color: {accent}; margin-bottom: 15px;'>Document Details</h4>
            <div style='color: {text}; line-height: 1.8;'>
                <p><strong>Filename:</strong> {uploaded_file.name}</p>
                <p><strong>Size:</strong> {uploaded_file.size/1024:.2f} KB</p>
                <p><strong>Extracted Clauses:</strong> {len(st.session_state.clauses)}</p>
                <p><strong>Status:</strong> <span style='color: {success}; font-weight: 600;'>Ready for Analysis</span></p>
            </div>
        </div>""", unsafe_allow_html=True)
        
        st.info("Navigate to 'Preprocessing' to view clause statistics, or go directly to 'Risk Analysis' to begin assessment.")

elif page == "Preprocessing" and st.session_state.clauses:
    st.markdown(f"<div class='title fade-in'>Preprocessing Insights</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Statistical analysis of extracted clauses</div>", unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.clauses)
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Clauses", len(df))
    col2.metric("Average Length", f"{int(df['word_count'].mean())} words")
    col3.metric("Longest Clause", f"{df['word_count'].max()} words")
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="word_count", nbins=15, title="Clause Length Distribution", 
                          color_discrete_sequence=[accent], labels={"word_count": "Word Count"})
        fig.update_layout(plot_bgcolor=card, paper_bgcolor=card, font_color=text, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.box(df, y="word_count", title="Word Count Statistics", 
                    color_discrete_sequence=[success], labels={"word_count": "Word Count"})
        fig.update_layout(plot_bgcolor=card, paper_bgcolor=card, font_color=text, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""<div class='card'>
        <h4 style='color: {accent};'>Statistical Summary</h4>
        <p style='color: {text};'><strong>Median Length:</strong> {int(df['word_count'].median())} words</p>
        <p style='color: {text};'><strong>Standard Deviation:</strong> {df['word_count'].std():.2f}</p>
        <p style='color: {text};'><strong>Total Words:</strong> {df['word_count'].sum():,}</p>
    </div>""", unsafe_allow_html=True)

elif page == "Risk Analysis" and st.session_state.clauses:
    st.markdown(f"<div class='title fade-in'>AI Risk Analysis</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Automated risk assessment powered by GPT AI</div>", unsafe_allow_html=True)
    
    if st.button("Run Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing contract clauses with AI..."):
            progress = st.progress(0)
            
            # Analyze with GPT
            results, overall_score, risk_category = analyze_contract_with_gpt(st.session_state.clauses)
            
            # Update progress
            for i in range(100):
                time.sleep(0.02)
                progress.progress(i + 1)
            
            st.session_state.analysis = results
            st.session_state.overall_score = overall_score
            st.session_state.risk_category = risk_category
            
            st.session_state.history.append({
                "Time": datetime.now().strftime("%d %b %Y %H:%M"),
                "Clauses": len(st.session_state.analysis),
                "High Risk": sum(1 for r in st.session_state.analysis if r["risk_level"] == "High"),
                "Overall Score": overall_score
            })
            progress.empty()
        
        show_success_animation()
        st.success("Analysis completed successfully")
        
        # Display overall score prominently
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            score_color = success if overall_score >= 85 else (warning if overall_score >= 60 else danger)
            st.markdown(f"""<div class='card' style='text-align: center; padding: 30px; border: 3px solid {score_color};'>
                <h2 style='color: {text}; margin-bottom: 10px;'>Overall Risk Score</h2>
                <div style='font-size: 64px; font-weight: 800; color: {score_color}; margin: 20px 0;'>{overall_score}</div>
                <div style='font-size: 24px; color: {score_color}; font-weight: 600;'>{risk_category}</div>
                <p style='color: {text_sec}; margin-top: 15px; font-size: 14px;'>Based on {len(st.session_state.analysis)} clauses analyzed</p>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        high = sum(1 for r in st.session_state.analysis if r["risk_level"] == "High")
        medium = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Medium")
        low = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Low")
        
        col1, col2, col3 = st.columns(3)
        risk_data = [
            ("High Risk Clauses", high, danger),
            ("Medium Risk Clauses", medium, warning),
            ("Low Risk Clauses", low, success)
        ]
        
        for col, (label, val, color) in zip([col1, col2, col3], risk_data):
            with col:
                st.markdown(f"""<div class='card' style='text-align: center; border-left: 4px solid {color};'>
                    <div style='color: {text_sec}; font-size: 14px; margin-bottom: 8px;'>{label}</div>
                    <div style='font-size: 36px; font-weight: 700; color: {color};'>{val}</div>
                </div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=['High', 'Medium', 'Low'], 
                values=[high, medium, low], 
                marker=dict(colors=[danger, warning, success]), 
                hole=0.4,
                textinfo='label+percent',
                textfont=dict(size=14, color=text)
            )])
            fig.update_layout(
                title="Risk Distribution",
                plot_bgcolor=card,
                paper_bgcolor=card,
                font_color=text,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(data=[go.Bar(
                x=['High', 'Medium', 'Low'],
                y=[high, medium, low],
                marker=dict(color=[danger, warning, success]),
                text=[high, medium, low],
                textposition='auto'
            )])
            fig.update_layout(
                title="Risk Count Breakdown",
                plot_bgcolor=card,
                paper_bgcolor=card,
                font_color=text,
                xaxis_title="Risk Level",
                yaxis_title="Number of Clauses"
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "Clause Insights" and st.session_state.analysis:
    st.markdown(f"<div class='title fade-in'>Clause Insights</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Detailed breakdown of each contract clause</div>", unsafe_allow_html=True)
    
    # Show overall score at top
    if st.session_state.overall_score:
        score_color = success if st.session_state.overall_score >= 85 else (warning if st.session_state.overall_score >= 60 else danger)
        st.markdown(f"""<div class='card' style='text-align: center; padding: 20px; border-left: 4px solid {score_color};'>
            <span style='color: {text_sec}; font-size: 14px;'>Contract Health Score: </span>
            <span style='font-size: 32px; font-weight: 700; color: {score_color};'>{st.session_state.overall_score}/100</span>
            <span style='color: {text_sec}; font-size: 14px; margin-left: 15px;'>{st.session_state.risk_category}</span>
        </div>""", unsafe_allow_html=True)
    
    risk_filter = st.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"])
    filtered = st.session_state.analysis if risk_filter == "All" else [r for r in st.session_state.analysis if r["risk_level"] == risk_filter]
    
    st.markdown(f"<p style='color: {text_sec};'>Displaying {len(filtered)} of {len(st.session_state.analysis)} clauses</p>", unsafe_allow_html=True)
    
    for r in filtered:
        color = danger if r["risk_level"] == "High" else (warning if r["risk_level"] == "Medium" else success)
        with st.expander(f"Clause {r['clause_id']} | {r['risk_level']} Risk"):
            st.markdown(f"<span style='background: {color}; color: white; padding: 4px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;'>{r['risk_level']} Risk</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("**Original Clause Text**")
            st.info(r["text"])
            
            st.markdown("**Plain Language Explanation**")
            st.write(r["explanation"])
            
            # Display key points if available
            if r.get('key_points') and len(r['key_points']) > 0:
                st.markdown("**Key Points**")
                for point in r['key_points']:
                    st.markdown(f"• {point}")
            
            st.markdown("**Risks Detected**")
            st.warning(r["risks"])
            
            st.markdown("**Safer Alternative**")
            st.success(r["suggested_alternative"])

elif page == "Summary" and st.session_state.analysis:
    st.markdown(f"<div class='title fade-in'>Executive Summary</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Comprehensive overview of your contract analysis</div>", unsafe_allow_html=True)
    
    high = sum(1 for r in st.session_state.analysis if r["risk_level"] == "High")
    medium = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Medium")
    low = sum(1 for r in st.session_state.analysis if r["risk_level"] == "Low")
    
    # Overall score display
    if st.session_state.overall_score:
        score_color = success if st.session_state.overall_score >= 85 else (warning if st.session_state.overall_score >= 60 else danger)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""<div class='card' style='text-align: center; padding: 30px; border: 3px solid {score_color};'>
                <h3 style='color: {text}; margin-bottom: 10px;'>Contract Health Score</h3>
                <div style='font-size: 72px; font-weight: 800; color: {score_color}; margin: 20px 0;'>{st.session_state.overall_score}/100</div>
                <div style='font-size: 20px; color: {score_color}; font-weight: 600;'>{st.session_state.risk_category}</div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""<div class='card'>
        <h3 style='color: {accent}; margin-bottom: 20px;'>Analysis Results</h3>
        <div style='color: {text}; line-height: 2;'>
            <p><strong>High Risk Clauses:</strong> <span style='color: {danger}; font-weight: 700;'>{high}</span></p>
            <p><strong>Medium Risk Clauses:</strong> <span style='color: {warning}; font-weight: 700;'>{medium}</span></p>
            <p><strong>Low Risk Clauses:</strong> <span style='color: {success}; font-weight: 700;'>{low}</span></p>
            <p><strong>Total Clauses Analyzed:</strong> {len(st.session_state.analysis)}</p>
            <hr style='border-color: {border}; margin: 20px 0;'>
            <p><strong>Recommendation:</strong> <span style='color: {"#ef4444" if high > 0 else success}; font-weight: 600;'>{"Legal review strongly advised due to high-risk clauses" if high > 0 else "Contract appears acceptable with minor concerns"}</span></p>
        </div>
    </div>""", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color: {accent}; margin-top: 30px;'>Download Reports</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        txt_data = generate_summary_text()
        st.download_button(
            "Download TXT Report",
            txt_data,
            file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        csv_data = generate_csv_report()
        st.download_button(
            "Download CSV Report",
            csv_data,
            file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    fig = go.Figure(data=[go.Bar(
        x=['High Risk', 'Medium Risk', 'Low Risk'],
        y=[high, medium, low],
        marker=dict(color=[danger, warning, success]),
        text=[high, medium, low],
        textposition='auto',
        textfont=dict(size=16, color='white')
    )])
    fig.update_layout(
        title="Final Risk Assessment",
        plot_bgcolor=card,
        paper_bgcolor=card,
        font_color=text,
        height=400,
        xaxis_title="Risk Category",
        yaxis_title="Number of Clauses"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "History":
    st.markdown(f"<div class='title fade-in'>Analysis History</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Track your past contract analyses</div>", unsafe_allow_html=True)
    
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True, height=400)
        
        st.markdown(f"""<div class='card'>
            <h4 style='color: {accent};'>History Statistics</h4>
            <p style='color: {text};'><strong>Total Analyses:</strong> {len(st.session_state.history)}</p>
            <p style='color: {text};'><strong>Total Clauses Processed:</strong> {sum(h['Clauses'] for h in st.session_state.history)}</p>
            <p style='color: {text};'><strong>Total High Risk Found:</strong> {sum(h['High Risk'] for h in st.session_state.history)}</p>
            <p style='color: {text};'><strong>Average Risk Score:</strong> {sum(h.get('Overall Score', 0) for h in st.session_state.history) / len(st.session_state.history):.1f}/100</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("No analysis history available yet. Upload and analyze a contract to get started.")

else:
    welcome_card = f"""<div class='card' style='text-align: center; padding: 60px;'>
        <h3 style='color: {accent};'>Welcome to Contract Intelligence</h3>
        <p style='color: {text_sec}; font-size: 16px; margin-top: 20px;'>
            Please upload a contract document to begin your analysis journey.
        </p>
        <p style='color: {text_sec}; margin-top: 10px;'>
            Navigate to the <strong>Upload</strong> page from the sidebar to get started.
        </p>
    </div>"""
    st.markdown(welcome_card, unsafe_allow_html=True)