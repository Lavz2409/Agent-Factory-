```
def generate_suggestions(analysis_results):
    suggestions = []

    # Check for missing sections
    required_sections = ['Education', 'Skills', 'Experience']
    for section in required_sections:
        if section not in analysis_results['sections']:
            suggestions.append(f"Add a '{section}' section to your resume.")

    # Check for keyword presence
    if analysis_results['keyword_score'] < 50:
        suggestions.append("Include more relevant keywords to improve ATS compatibility.")

    # Check formatting issues
    if analysis_results['formatting_score'] < 50:
        suggestions.append("Simplify the formatting of your resume. Avoid special characters and tables.")

    # Overall score suggestions
    overall_score = analysis_results.get('overall_score', 0)
    if overall_score < 70:
        suggestions.append("Overall, your resume needs improvement to increase its ATS-friendliness.")

    return suggestions
```