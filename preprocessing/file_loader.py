import pdfplumber
import docx

def extract_text(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return _extract_pdf(uploaded_file)

    elif filename.endswith(".docx"):
        return _extract_docx(uploaded_file)

    elif filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    else:
        raise ValueError("Unsupported file format")


def _extract_pdf(file):
    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def _extract_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)
