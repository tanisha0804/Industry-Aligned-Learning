import pdfplumber
from pathlib import Path

#to extract raw texts from pdf
def pdf_to_text(pdf_path: Path) -> str:
    text_chunks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)

    return "\n".join(text_chunks)
