```
import re
from typing import Dict, Any

def parse_resume(resume_text: str) -> Dict[str, Any]:
    """
    Parses the resume text and extracts relevant sections, checks for ATS-friendliness,
    and provides a score and suggestions for improvement.

    Args:
        resume_text (str): The text content of the resume.

    Returns:
        Dict[str, Any]: A dictionary containing the score, suggestions, and extracted sections.
    """
    sections = extract_sections(resume_text)
    keywords = extract_keywords(resume_text)
    score, suggestions = evaluate_resume(sections, keywords)

    return {
        "score": score,
        "suggestions": suggestions,
        "sections": sections
    }

def extract_sections(text: str) -> Dict[str, str]:
    """
    Extracts sections from the resume text.

    Args:
        text (str): The text content of the resume.

    Returns:
        Dict[str, str]: A dictionary with section names as keys and section text as values.
    """
    section_patterns = {
        "Education": r"(Education|Academic Background|Qualifications)",
        "Skills": r"(Skills|Technical Skills|Expertise)",
        "Experience": r"(Experience|Work Experience|Employment History)"
    }
    
    sections = {}
    for section, pattern in section_patterns.items():
        match = re.search(f"{pattern}.*?(?=\\n\\n|$)", text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[section] = match.group().strip()
        else:
            sections[section] = ""

    return sections

def extract_keywords(text: str) -> Dict[str, int]:
    """
    Extracts keywords from the resume text.

    Args:
        text (str): The text content of the resume.

    Returns:
        Dict[str, int]: A dictionary with keywords as keys and their occurrence count as values.
    """
    keywords = ["Python", "Machine Learning", "Data Analysis", "Project Management"]
    keyword_count = {keyword: len(re.findall(rf"\b{keyword}\b", text, re.IGNORECASE)) for keyword in keywords}
    return keyword_count

def evaluate_resume(sections: Dict[str, str], keywords: Dict[str, int]) -> (int, list):
    """
    Evaluates the resume based on sections and keyword presence.

    Args:
        sections (Dict[str, str]): Extracted sections from the resume.
        keywords (Dict[str, int]): Count of important keywords in the resume.

    Returns:
        (int, list): A tuple containing the score and a list of suggestions for improvement.
    """
    score = 0
    suggestions = []

    # Check for presence of sections
    for section, content in sections.items():
        if content:
            score += 20
        else:
            suggestions.append(f"Consider adding a {section} section.")

    # Check for keyword presence
    keyword_score = sum(min(count, 3) for count in keywords.values()) * 5
    score += keyword_score

    if keyword_score < 10:
        suggestions.append("Add more relevant keywords to improve ATS compatibility.")

    # Check for simple formatting
    if re.search(r"[^\x00-\x7F]+", resume_text):
        suggestions.append("Remove special characters for better ATS compatibility.")
    else:
        score += 20

    # Ensure score is capped at 100
    score = min(score, 100)

    return score, suggestions
```