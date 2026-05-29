```
import re
from typing import List

def check_keywords(resume_text: str, keywords: List[str]) -> bool:
    """
    Check if the resume contains any of the specified keywords.
    
    Args:
        resume_text (str): The text of the resume.
        keywords (List[str]): A list of keywords to check for.

    Returns:
        bool: True if any keyword is found, False otherwise.
    """
    resume_text_lower = resume_text.lower()
    for keyword in keywords:
        if keyword.lower() in resume_text_lower:
            return True
    return False

def check_sections(resume_text: str, sections: List[str]) -> bool:
    """
    Check if the resume contains all the specified sections.
    
    Args:
        resume_text (str): The text of the resume.
        sections (List[str]): A list of sections to check for.

    Returns:
        bool: True if all sections are found, False otherwise.
    """
    resume_text_lower = resume_text.lower()
    for section in sections:
        if section.lower() not in resume_text_lower:
            return False
    return True

def check_formatting(resume_text: str) -> bool:
    """
    Check if the resume uses simple formatting.
    
    Args:
        resume_text (str): The text of the resume.

    Returns:
        bool: True if the formatting is simple, False otherwise.
    """
    # Check for special characters or patterns that indicate complex formatting
    # such as tables or excessive special characters
    if re.search(r'[\t\n\r\f\v]', resume_text):
        return False
    if re.search(r'[^\w\s,.]', resume_text):
        return False
    return True
```