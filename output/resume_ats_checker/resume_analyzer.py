from typing import Dict, List, Union

def analyze_resume(parsed_resume: Dict[str, List[str]]) -> Dict[str, Union[int, List[str]]]:
    # Define the criteria for ATS-friendliness
    required_sections = {"Education", "Skills", "Experience"}
    keywords = {"Python", "Java", "Project Management", "Data Analysis", "Team Leadership"}
    suggestions = []
    score = 100

    # Check for required sections
    missing_sections = required_sections - parsed_resume.keys()
    if missing_sections:
        score -= 20 * len(missing_sections)
        suggestions.append(f"Add missing sections: {', '.join(missing_sections)}")

    # Check for presence of keywords
    found_keywords = set()
    for section in parsed_resume.values():
        for line in section:
            found_keywords.update(keywords.intersection(line.split()))

    missing_keywords = keywords - found_keywords
    if missing_keywords:
        score -= 10 * len(missing_keywords)
        suggestions.append(f"Include more relevant keywords: {', '.join(missing_keywords)}")

    # Check for simple formatting
    for section, lines in parsed_resume.items():
        for line in lines:
            if any(char in line for char in {'#', '*', '|', '>'}):
                score -= 5
                suggestions.append(f"Remove special characters in section '{section}'")
                break

    # Ensure score is within 0 to 100
    score = max(0, min(100, score))

    return {
        "score": score,
        "suggestions": suggestions
    }