import re
from typing import Dict, Any, List

def check_ats_friendly(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    suggestions = []

    # Define required sections and keywords
    required_sections = ['Education', 'Skills', 'Experience']
    keywords = ['Python', 'Java', 'Project Management', 'Data Analysis', 'Machine Learning']

    # Check for presence of required sections
    for section in required_sections:
        if section in parsed_data:
            score += 10
        else:
            suggestions.append(f"Add a section for {section}.")

    # Check for presence of keywords
    found_keywords = [kw for kw in keywords if kw in parsed_data.get('text', '')]
    score += len(found_keywords) * 5
    if len(found_keywords) < len(keywords):
        missing_keywords = set(keywords) - set(found_keywords)
        suggestions.append(f"Consider adding keywords: {', '.join(missing_keywords)}.")

    # Check for simple formatting
    if not re.search(r'[^a-zA-Z0-9\s,.]', parsed_data.get('text', '')):
        score += 20
    else:
        suggestions.append("Avoid using special characters or complex formatting.")

    # Cap the score at 100
    score = min(score, 100)

    return {
        'score': score,
        'suggestions': suggestions
    }