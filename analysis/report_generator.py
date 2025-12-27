import json
from datetime import datetime

class ReportGenerator:
    def generate_analysis_report(self, filename, summary_data, clauses, entities):
        """
        Builds the master report dictionary using:
        1. The 'Summary Agent' output (Risk Score, Verdict)
        2. The 'Clause Agent' output (Plain Language, Specific Risks)
        """
        
        # 1. Calculate Aggregates based on Friend's Code Logic
        total_risks = 0
        high_risks = 0
        for c in clauses:
            ai_data = c.get('ai_data', {})
            risks = ai_data.get('risks_detected', [])
            total_risks += len(risks)
            if ai_data.get('risk_level') == 'High':
                high_risks += 1

        # 2. Build the Report Structure (Matching your concept)
        report = {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "file_name": filename,
                "processing_status": "completed",
                "tool_version": "NyayaSahayak v2.0 (OpenAI)"
            },
            
            "executive_summary": {
                # Data from summarizer_agent.py
                "strategic_overview": summary_data.get("executive_summary", "N/A"),
                "final_verdict": summary_data.get("final_verdict", "Review Required"),
                "compliance_check": summary_data.get("compliance_check", "N/A"),
                "key_obligations": summary_data.get("key_obligations", [])
            },

            "risk_stats": {
                # Data derived from aggregating Clause Agent results
                "safety_score": summary_data.get("safety_score", 0),
                "total_issues_found": total_risks,
                "high_risk_clauses": high_risks
            },

            "entities_detected": entities,

            "detailed_clause_analysis": self._process_clauses(clauses),
            
            "recommendations": self._generate_recommendations(summary_data.get("safety_score", 0), high_risks)
        }
        
        return report

    def _process_clauses(self, raw_clauses):
        """
        Formats the clauses to align strictly with Friend's Code Structure.
        """
        processed = []
        for c in raw_clauses:
            ai = c.get('ai_data', {}) # This is the dict from explain_clause_gpt
            
            entry = {
                "clause_id": c.get('title'),
                "original_text": c.get('content'),
                # The Friend's Logic:
                "ai_analysis": {
                    "plain_language": ai.get('plain_language', 'Not analyzed'),
                    "risk_level": ai.get('risk_level', 'Unknown'),
                    "risks_detected": ai.get('risks_detected', []), # List of violations
                    "key_points": ai.get('key_points', []),
                    "safer_alternative": ai.get('safer_alternative', 'N/A')
                }
            }
            processed.append(entry)
        return processed
    
    def _generate_recommendations(self, score, high_risk_count):
        """Generates dynamic advice based on the score."""
        recs = []
        if score < 60 or high_risk_count > 2:
            recs.append("🔴 CRITICAL: Multiple high-risk clauses detected. Do not sign without negotiation.")
            recs.append("👉 Focus negotiation on the 'Safer Alternatives' suggested in the report.")
        elif score < 85:
            recs.append("🟡 CAUTION: Several unfavorable terms found. Request amendments.")
        else:
            recs.append("🟢 SAFE: Contract appears standard, but verify specific dates/amounts.")
            
        recs.append("Verify all 'Entities' and 'Dates' extracted in the summary.")
        return recs
    
    # --- EXPORT FORMAT 1: JSON (Data) ---
    def export_to_json(self, report):
        return json.dumps(report, indent=4, ensure_ascii=False)

    # --- EXPORT FORMAT 2: MARKDOWN (Readable) ---
    def export_to_markdown(self, report):
        """
        Creates a beautiful, printable document string.
        """
        meta = report['analysis_metadata']
        exec_sum = report['executive_summary']
        stats = report['risk_stats']
        
        md = f"""# ⚖️ Legal Analysis Report: {meta['file_name']}
**Date:** {meta['timestamp']} | **Verdict:** {exec_sum['final_verdict']}

---

## 1. Executive Summary
> **{exec_sum['strategic_overview']}**

* **Compliance Note:** {exec_sum['compliance_check']}
* **Safety Score:** {stats['safety_score']}/100
* **Total Issues:** {stats['total_issues_found']}

### 🔑 Key Obligations
"""
        for ob in exec_sum['key_obligations']:
            md += f"* {ob}\n"

        md += "\n---\n## 2. Detailed Clause Analysis\n"

        for clause in report['detailed_clause_analysis']:
            analysis = clause['ai_analysis']
            icon = "🔴" if analysis['risk_level'] == "High" else "🟡" if analysis['risk_level'] == "Medium" else "🟢"
            
            md += f"""
### {icon} {clause['clause_id']} ({analysis['risk_level']} Risk)
**Plain Language:** {analysis['plain_language']}

"""
            if analysis['risks_detected']:
                md += "**⚠️ Risks:**\n"
                for r in analysis['risks_detected']:
                    md += f"* {r}\n"
                
                md += f"\n**✅ Suggested Change:**\n_{analysis['safer_alternative']}_\n"
            
            md += "\n---\n"

        return md
