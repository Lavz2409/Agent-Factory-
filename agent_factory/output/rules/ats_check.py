```
import re
from typing import Dict, Any

def check_ats_friendly(resume_text: str) -> Dict[str, Any]:
    score = 0
    suggestions = []

    # Keywords to check for
    keywords = ['Python', 'Java', 'C++', 'Project Management', 'Data Analysis']
    keyword_score = 0
    keyword_suggestions = []

    # Sections to check for
    sections = ['Education', 'Skills', 'Experience']
    section_score = 0
    section_suggestions = []

    # Check for keywords
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', resume_text, re.IGNORECASE):
            keyword_score += 1
        else:
            keyword_suggestions.append(f"Consider adding the keyword: {keyword}")

    # Check for sections
    for section in sections:
        if re.search(r'\b' + re.escape(section) + r'\b', resume_text, re.IGNORECASE):
            section_score += 1
        else:
            section_suggestions.append(f"Consider adding a section for: {section}")

    # Check for simple formatting
    formatting_score = 0
    formatting_suggestions = []

    # Avoid special characters and tables
    if not re.search(r'[^\w\s,.]', resume_text):
        formatting_score += 1
    else:
        formatting_suggestions.append("Avoid using special characters or tables.")

    # Calculate total score
    total_possible_score = len(keywords) + len(sections) + 1
    score = (keyword_score + section_score + formatting_score) / total_possible_score * 100

    # Compile suggestions
    suggestions.extend(keyword_suggestions)
    suggestions.extend(section_suggestions)
    suggestions.extend(formatting_suggestions)

    return {
        'score': score,
        'suggestions': suggestions
    }
```