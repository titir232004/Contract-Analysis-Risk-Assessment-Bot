import re
from typing import List, Dict

EXCLUDED_KEYWORDS = [
    "SIGNATURE",
    "IN WITNESS WHEREOF",
    "ACKNOWLEDGMENT",
    "FOR THE EMPLOYER",
    "FOR THE EMPLOYEE",
    "AUTHORIZED SIGNATORY"
]

MIN_CLAUSE_LENGTH = 100  # Merge anything shorter into previous clause


def split_into_clauses(contract_text: str) -> List[Dict]:
    clauses = []
    clause_id = 1

    # Normalize newlines and split by double newlines or numbering
    chunks = re.split(r'\n\s*\n|(?=\d+(\.\d+)*[\)\.]?\s+)|(?=[IVXLCDM]+[\)\.]\s+)', contract_text.replace("\r", ""))
    buffer = ""

    for chunk in chunks:
        if not isinstance(chunk, str):
            continue
        chunk = chunk.strip()
        if not chunk:
            continue

        if is_excluded_line(chunk):
            continue

        # Merge small chunks with buffer
        if len(chunk) < MIN_CLAUSE_LENGTH:
            buffer += " " + chunk
            continue

        # If buffer has content, finalize it as a clause
        if buffer:
            clauses.append({
                "clause_id": clause_id,
                "text": buffer.strip()
            })
            clause_id += 1
            buffer = ""

        buffer = chunk

    # Flush last buffer
    if buffer:
        clauses.append({
            "clause_id": clause_id,
            "text": buffer.strip()
        })

    return clauses


def is_excluded_line(line: str) -> bool:
    upper = line.upper()
    return any(keyword in upper for keyword in EXCLUDED_KEYWORDS)
