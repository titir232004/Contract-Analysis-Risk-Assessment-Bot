import streamlit as st
import json

# --------- IMPORT YOUR MODULES ---------
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

st.title("⚖️ NyayaSahayak – AI Contract Risk Analyzer")
st.caption("Indian Employment & Legal Contract Analysis using AI")

st.divider()

# ---------- SESSION STATE ----------
if "clauses" not in st.session_state:
    st.session_state.clauses = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "report" not in st.session_state:
    st.session_state.report = None


# ---------- FILE UPLOAD ----------
st.header("📤 Upload Contract")

uploaded_file = st.file_uploader(
    "Upload PDF / DOCX / TXT",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

    # ---------- PREPROCESSING ----------
    with st.spinner("📄 Extracting & cleaning text..."):
        raw_text = extract_text(uploaded_file)
        cleaned_text = clean_text(raw_text)

    with st.spinner("🔍 Splitting into clauses..."):
        clauses = split_into_clauses(cleaned_text)

    st.info(f"Detected **{len(clauses)} clauses**")

    if st.button("🚀 Start Legal Analysis"):
        st.session_state.clauses = clauses
        st.session_state.analysis_done = False
        st.session_state.report = None

        progress = st.progress(0)
        analyzed_clauses = []

        st.subheader("⏳ Clause Analysis Progress")

        for idx, clause in enumerate(clauses):
            result = explain_clause_gpt(clause["text"])

            analyzed_clauses.append({
                "title": f"Clause {idx+1}",
                "content": clause["text"],
                "ai_data": result
            })

            progress.progress((idx + 1) / len(clauses))

        # ---------- SUMMARY ----------
        with st.spinner("🧠 Generating executive summary..."):
            flat_ai = [c["ai_data"] for c in analyzed_clauses]
            summary = summarize_contract(flat_ai)

        # ---------- REPORT ----------
        generator = ReportGenerator()
        report = generator.generate_analysis_report(
            filename=uploaded_file.name,
            summary_data={
                "executive_summary": summary.get("executive_summary"),
                "final_verdict": summary.get("recommendation"),
                "compliance_check": summary.get("overall_risk_score"),
                "safety_score": 75,  # placeholder (can be improved later)
                "key_obligations": []
            },
            clauses=analyzed_clauses,
            entities=[]
        )

        st.session_state.report = report
        st.session_state.analysis_done = True
        st.success("✅ Analysis completed!")


# ---------- RESULTS ----------
if st.session_state.analysis_done and st.session_state.report:
    report = st.session_state.report

    st.divider()
    st.header("📊 Executive Summary")

    exec_sum = report["executive_summary"]
    stats = report["risk_stats"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Final Verdict", exec_sum["final_verdict"])
    col2.metric("Compliance", exec_sum["compliance_check"])
    col3.metric("High Risk Clauses", stats["high_risk_clauses"])

    st.markdown(f"""
    **Strategic Overview:**  
    {exec_sum["strategic_overview"]}
    """)

    st.divider()
    st.header("📑 Clause-wise Risk Analysis")

    for clause in report["detailed_clause_analysis"]:
        analysis = clause["ai_analysis"]
        risk = analysis["risk_level"]

        icon = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"

        with st.expander(f"{icon} {clause['clause_id']} – {risk} Risk"):
            st.markdown("**Plain Language Explanation**")
            st.write(analysis["plain_language"])

            if analysis["risks_detected"]:
                st.markdown("**⚠️ Risks Detected**")
                for r in analysis["risks_detected"]:
                    st.write(f"- {r}")

                st.markdown("**✅ Safer Alternative**")
                st.info(analysis["safer_alternative"])

    st.divider()
    st.header("⬇️ Download Report")

    col1, col2 = st.columns(2)

    col1.download_button(
        "📄 Download JSON",
        data=json.dumps(report, indent=4),
        file_name="legal_analysis.json",
        mime="application/json"
    )

    md_report = ReportGenerator().export_to_markdown(report)
    col2.download_button(
        "📝 Download Markdown",
        data=md_report,
        file_name="legal_analysis.md",
        mime="text/markdown"
    )
