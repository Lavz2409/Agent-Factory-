```
import re
from typing import Dict, List

def parse_resume(resume_text: str) -> Dict[str, List[str]]:
    """
    Parses the resume text and extracts sections such as Education, Skills, and Experience.
    
    Args:
        resume_text (str): The text content of the resume.
        
    Returns:
        Dict[str, List[str]]: A dictionary with section names as keys and list of lines as values.
    """
    sections = {
        'Education': [],
        'Skills': [],
        'Experience': []
    }
    
    current_section = None
    
    # Define patterns for section headers
    section_patterns = {
        'Education': re.compile(r'\bEducation\b', re.IGNORECASE),
        'Skills': re.compile(r'\bSkills\b', re.IGNORECASE),
        'Experience': re.compile(r'\bExperience\b', re.IGNORECASE)
    }
    
    # Split resume text into lines
    lines = resume_text.splitlines()
    
    for line in lines:
        # Check for section headers
        for section, pattern in section_patterns.items():
            if pattern.search(line):
                current_section = section
                break
        
        # If a section header was found, skip to the next line
        if current_section and any(pattern.search(line) for pattern in section_patterns.values()):
            continue
        
        # Add line to the current section
        if current_section:
            sections[current_section].append(line.strip())
    
    return sections
```