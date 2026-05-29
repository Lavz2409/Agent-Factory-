```
def generate_suggestions(ats_results):
    suggestions = []

    # Check for missing sections
    if not ats_results.get('has_education_section', False):
        suggestions.append("Add an 'Education' section to your resume.")
    if not ats_results.get('has_skills_section', False):
        suggestions.append("Include a 'Skills' section to highlight your abilities.")
    if not ats_results.get('has_experience_section', False):
        suggestions.append("Add an 'Experience' section to detail your work history.")

    # Check for keyword presence
    if not ats_results.get('has_required_keywords', False):
        suggestions.append("Incorporate relevant keywords related to your skills and experience.")

    # Check for formatting issues
    if ats_results.get('has_special_characters', False):
        suggestions.append("Remove special characters to ensure ATS compatibility.")
    if ats_results.get('has_tables', False):
        suggestions.append("Avoid using tables as they may not be ATS-friendly.")

    # Check for overall ATS-friendliness
    if not ats_results.get('is_ats_friendly', False):
        suggestions.append("Revise your resume to improve ATS compatibility.")

    return suggestions
```