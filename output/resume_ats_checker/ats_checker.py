import re

def check_keywords(resume_text: str) -> int:
    # Define a list of common keywords to check for
    keywords = ['Python', 'Java', 'C++', 'Project Management', 'Team Leadership', 
                'Data Analysis', 'Machine Learning', 'Communication', 'Problem Solving']
    count = 0
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', resume_text, re.IGNORECASE):
            count += 1
    return count

def check_sections(resume_text: str) -> int:
    # Define the required sections
    sections = ['Education', 'Skills', 'Experience']
    count = 0
    for section in sections:
        if re.search(r'\b' + re.escape(section) + r'\b', resume_text, re.IGNORECASE):
            count += 1
    return count

def check_formatting(resume_text: str) -> bool:
    # Check for simple formatting: no special characters, no tables
    if re.search(r'[^a-zA-Z0-9\s,.]', resume_text):
        return False
    # Check for tables (simple heuristic: multiple spaces or tabs in a row)
    if re.search(r'\s{2,}|\t', resume_text):
        return False
    return True

def calculate_score(keywords_count: int, sections_count: int, formatting_ok: bool) -> int:
    # Calculate score based on the presence of keywords, sections, and formatting
    score = 0
    score += (keywords_count / 10) * 30  # Assume 10 keywords for full score
    score += (sections_count / 3) * 30   # 3 sections for full score
    score += 40 if formatting_ok else 0  # Formatting contributes 40 points
    return int(score)

def generate_suggestions(keywords_count: int, sections_count: int, formatting_ok: bool) -> list:
    suggestions = []
    if keywords_count < 10:
        suggestions.append("Add more relevant keywords related to your skills and experience.")
    if sections_count < 3:
        suggestions.append("Ensure your resume includes sections for Education, Skills, and Experience.")
    if not formatting_ok:
        suggestions.append("Simplify the formatting of your resume. Avoid special characters and tables.")
    return suggestions

def check_ats_friendly(resume_text: str) -> dict:
    keywords_count = check_keywords(resume_text)
    sections_count = check_sections(resume_text)
    formatting_ok = check_formatting(resume_text)
    score = calculate_score(keywords_count, sections_count, formatting_ok)
    suggestions = generate_suggestions(keywords_count, sections_count, formatting_ok)
    
    return {
        'score': score,
        'suggestions': suggestions
    }