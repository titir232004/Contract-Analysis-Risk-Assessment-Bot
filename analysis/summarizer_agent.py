from openai import OpenAI
import json

client = OpenAI()

def summarize_contract(analyzed_clauses: list):
    """
    Takes a list of analyzed clause dictionaries (from explain_clause_gpt)
    and generates an overall executive summary and risk score.
    """
    
    # 1. Pre-computation: Aggregate risks manually to save tokens/improve accuracy
    high_risk_count = sum(1 for c in analyzed_clauses if c.get('risk_level') == 'High')
    medium_risk_count = sum(1 for c in analyzed_clauses if c.get('risk_level') == 'Medium')
    
    # Collect all detected risks into a single text block for the LLM
    all_risks = []
    for idx, clause in enumerate(analyzed_clauses):
        risks = ", ".join(clause.get('risks_detected', []))
        if risks:
            all_risks.append(f"Clause {idx+1} ({clause.get('risk_level')} Risk): {risks}")
            
    risk_summary_text = "\n".join(all_risks)

    prompt = f"""
    You are a Lead Legal Consultant.
    
    Based on the following aggregated risks from a contract review, write an Executive Summary (max 150 words).
    
    Stats:
    - High Risk Clauses: {high_risk_count}
    - Medium Risk Clauses: {medium_risk_count}
    
    Detailed Risk List:
    {risk_summary_text}
    
    Output Strict JSON:
    {{
      "executive_summary": "...",
      "overall_risk_score": "Low/Medium/High/Critical",
      "recommendation": "Sign / Negotiate / Reject"
    }}
    """

    try:
        # Using standard chat completion (adjust model as needed)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        return {
            "executive_summary": "Could not generate summary due to error.",
            "overall_risk_score": "Unknown",
            "recommendation": "Manual Review Required",
            "error": str(e)
        }