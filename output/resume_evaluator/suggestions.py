def generate_suggestions(ats_results: dict) -> list:
    suggestions = []

    # Check for missing keywords
    if not ats_results.get('keywords_present', True):
        suggestions.append("Add more relevant keywords related to your skills and experience.")

    # Check for missing sections
    if not ats_results.get('has_education_section', True):
        suggestions.append("Include an 'Education' section with your academic background.")
    if not ats_results.get('has_skills_section', True):
        suggestions.append("Include a 'Skills' section listing your relevant skills.")
    if not ats_results.get('has_experience_section', True):
        suggestions.append("Include an 'Experience' section detailing your work history.")

    # Check for formatting issues
    if not ats_results.get('simple_formatting', True):
        suggestions.append("Simplify the formatting: avoid special characters, tables, or complex layouts.")

    # General suggestions
    if ats_results.get('score', 100) < 70:
        suggestions.append("Consider revising your resume to improve its ATS compatibility.")

    return suggestions