import pdfplumber
from pathlib import Path

def file_to_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        return ""

    try:
        # PDF files
        if path.suffix.lower() == ".pdf":
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text

        # TXT files
        elif path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")

        else:
            print(f"[WARN] Unsupported file type: {path.suffix}")
            return ""

    except Exception as e:
        print(f"[WARN] Failed to parse file: {file_path}")
        print(f"       Reason: {e}")
        return ""

