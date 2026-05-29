```
from typing import Dict, Any, Tuple, List

def check_ats_friendly(parsed_resume: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Checks if the resume is ATS-friendly and calculates a score.

    Args:
        parsed_resume (Dict[str, Any]): A dictionary containing parsed resume data.

    Returns:
        Tuple[int, List[str]]: A score from 0 to 100 and a list of suggestions for improvement.
    """
    score = 0
    suggestions = []

    # Check for required sections
    required_sections = ['Education', 'Skills', 'Experience']
    for section in required_sections:
        if section not in parsed_resume['sections']:
            suggestions.append(f"Add a section for {section}.")
        else:
            score += 20  # Each section contributes to the score

    # Check for presence of keywords
    if 'keywords' in parsed_resume and parsed_resume['keywords']:
        keyword_count = sum(parsed_resume['keywords'].values())
        if keyword_count > 10:
            score += 20
        else:
            suggestions.append("Include more relevant keywords related to skills and experience.")
    else:
        suggestions.append("No keywords found. Include relevant skills and experience keywords.")

    # Check for simple formatting
    if 'text' in parsed_resume:
        text = parsed_resume['text']
        if any(char in text for char in ['@', '#', '$', '%', '^', '&', '*', '(', ')', '=', '+']):
            suggestions.append("Remove special characters from the resume.")
        else:
            score += 20

        if any(tag in text for tag in ['<table>', '<tr>', '<td>']):
            suggestions.append("Avoid using tables in the resume.")
        else:
            score += 20
    else:
        suggestions.append("Resume text is missing for formatting check.")

    # Ensure score does not exceed 100
    score = min(score, 100)

    return score, suggestions
```