import re
from typing import Dict, Any
from collections import Counter

def parse_resume(input_path: str) -> Dict[str, Any]:
    # Read the resume text from the file
    if input_path.endswith('.pdf'):
        resume_text = read_text_from_pdf(input_path)
    elif input_path.endswith('.docx'):
        resume_text = read_text_from_docx(input_path)
    else:
        resume_text = read_text_from_file(input_path)
    
    # Check ATS-friendliness
    ats_score, suggestions = check_ats_friendly(resume_text)
    
    return {
        "ats_score": ats_score,
        "suggestions": suggestions
    }

def read_text_from_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_text_from_pdf(file_path: str) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text

def read_text_from_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def check_ats_friendly(resume_text: str) -> (int, list):
    keywords = ['Python', 'Java', 'C++', 'Project Management', 'Data Analysis']
    sections = ['Education', 'Skills', 'Experience']
    ats_score = 0
    suggestions = []

    # Check for keywords
    text_lower = resume_text.lower()
    keyword_count = sum(text_lower.count(keyword.lower()) for keyword in keywords)
    if keyword_count < len(keywords) / 2:
        suggestions.append("Add more relevant keywords related to skills and experience.")
    else:
        ats_score += 30

    # Check for sections
    section_count = sum(1 for section in sections if re.search(r'\b' + section + r'\b', resume_text, re.IGNORECASE))
    if section_count < len(sections):
        suggestions.append("Ensure all major sections (Education, Skills, Experience) are present.")
    else:
        ats_score += 30

    # Check for simple formatting
    if re.search(r'[^\w\s,.]', resume_text):
        suggestions.append("Avoid using special characters and complex formatting.")
    else:
        ats_score += 40

    return ats_score, suggestions