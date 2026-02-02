import pdfplumber
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

PDF_PATH = "course_handbook_onlyskill.pdf"
OUTPUT_JSON = "course_code_skill.json"


def extract_pdf_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def call_llm(text_chunk):
    prompt = f"""
You are given text from a university Computer Science syllabus.

TASK:
Extract course information and return STRICT JSON only.

Rules:
- Each course must include:
  - course_code
  - course_title
  - skills (languages + tools + technical concepts)
- Ignore credits, hours, notes, and footers
- Merge multi-line titles correctly
- Do NOT hallucinate skills
- 1st & 2nd semester courses → include ONLY the main programming language
- 3rd semester onwards → include languages, tools, and core technical concepts
- include all electives and their associated skills

Output format:
[
  {{
    "course_code": "...",
    "course_title": "...",
    "skills": ["...", "..."]
  }}
]

TEXT:
{text_chunk}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content


def main():
    raw_text = extract_pdf_text(PDF_PATH)

    # Chunk to avoid token overflow
    chunk_size = 4000
    chunks = [
        raw_text[i:i + chunk_size]
        for i in range(0, len(raw_text), chunk_size)
    ]

    all_courses = []

    for chunk in chunks:
        llm_output = call_llm(chunk)
        try:
            data = json.loads(llm_output)
            all_courses.extend(data)
        except json.JSONDecodeError:
            print("JSON parsing failed for a chunk")

    # Deduplicate by course_code
    final = {}
    for c in all_courses:
        final[c["course_code"]] = c

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(list(final.values()), f, indent=2)

    print(f"Extracted {len(final)} courses")


if __name__ == "__main__":
    main()
