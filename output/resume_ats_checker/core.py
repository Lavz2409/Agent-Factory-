import re
from typing import List, Tuple

def analyze_resume(resume_text: str) -> Tuple[int, List[str]]:
    """
    Analyzes the resume text for ATS compliance and returns a score and suggestions.
    
    Args:
        resume_text (str): The text of the resume to analyze.
        
    Returns:
        Tuple[int, List[str]]: A score from 0 to 100 indicating ATS compliance and a list of suggestions for improvement.
    """
    score = 100
    suggestions = []

    # Check for presence of key sections
    required_sections = ['Education', 'Skills', 'Experience']
    for section in required_sections:
        if section.lower() not in resume_text.lower():
            score -= 10
            suggestions.append(f"Add a '{section}' section.")

    # Check for presence of keywords
    keywords = ['Python', 'AI', 'Machine Learning', 'Data Analysis', 'Project Management']
    keyword_count = sum(1 for keyword in keywords if keyword.lower() in resume_text.lower())
    if keyword_count < 3:
        score -= 10
        suggestions.append("Include more relevant keywords related to your skills and experience.")

    # Check for simple formatting
    if re.search(r'[^\x00-\x7F]+', resume_text):
        score -= 10
        suggestions.append("Remove special characters and non-ASCII text for better ATS compatibility.")

    if re.search(r'<table>|<tr>|<td>', resume_text, re.IGNORECASE):
        score -= 10
        suggestions.append("Avoid using tables; use simple text formatting instead.")

    # Ensure score is within bounds
    score = max(0, min(score, 100))

    return score, suggestions