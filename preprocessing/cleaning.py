# cleaning.py
import re
from bs4 import BeautifulSoup

def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = BeautifulSoup(raw_text, "html.parser").get_text(separator="\n")

    # Remove carriage returns
    text = re.sub(r'\r+', '', text)

    # Normalize multiple newlines to a single newline
    text = re.sub(r'\n+', '\n', text)

    # Normalize spaces within each line
    text = re.sub(r'[ ]+', ' ', text)

    # Remove unwanted characters but keep Hindi, English letters, numbers, basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\u0900-\u097F\s\.\,\-\(\)\:]', '', text)

    # Strip leading/trailing spaces from each line
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])

    return text
