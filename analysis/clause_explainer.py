from openai import OpenAI
import json
import os

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment")

client = OpenAI(api_key=api_key)

def explain_clause_gpt(clause_text: str):
    prompt = f"""
    You are a legal assistant familiar with Indian labor laws.

Analyze the contract clause below and return STRICT JSON with:
- plain_language
- key_points (list)
- risks_detected (list, include violations or non-compliance with Indian labor laws)
- risk_level (Low / Medium / High)
- safer_alternative

    Clause:
    \"\"\"{clause_text}\"\"\"
    """

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        text_output = response.output_text.strip()

        # Try to parse JSON safely
        try:
            return json.loads(text_output)
        except:
            return {
                "plain_language": text_output,
                "key_points": [],
                "risks_detected": [],
                "risk_level": "Unknown",
                "safer_alternative": "Could not structure response."
            }

    except Exception as e:
        return {
            "plain_language": "Error analyzing clause.",
            "key_points": [],
            "risks_detected": [],
            "risk_level": "Unknown",
            "safer_alternative": str(e)
        }


# -------- CLI TEST --------
if __name__ == "__main__":
    print("=== GPT-5-Nano Clause Explainer Test ===\n")
    clause = input("Enter a clause to analyze:\n\n")
    print("\nAnalyzing clause...\n")
    result = explain_clause_gpt(clause)
    print(json.dumps(result, indent=4))
