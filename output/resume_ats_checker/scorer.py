def score_resume(check_results):
    """
    Calculate a score for the resume based on ATS-friendly checks and generate suggestions for improvement.

    Args:
        check_results (Dict[str, Any]): Results from ATS-friendly checks including presence of keywords, sections, and formatting issues.

    Returns:
        Tuple[int, List[str]]: A score between 0 and 100, and a list of suggestions for improvement.
    """
    score = 100
    suggestions = []

    # Check for presence of essential sections
    essential_sections = ['Education', 'Skills', 'Experience']
    for section in essential_sections:
        if not check_results.get(f'has_{section.lower()}'):
            score -= 10
            suggestions.append(f"Add a '{section}' section to your resume.")

    # Check for presence of keywords
    if not check_results.get('has_keywords'):
        score -= 20
        suggestions.append("Include relevant keywords related to your skills and experience.")

    # Check for simple formatting
    if check_results.get('has_special_characters'):
        score -= 10
        suggestions.append("Remove special characters for better ATS compatibility.")

    if check_results.get('has_tables'):
        score -= 10
        suggestions.append("Avoid using tables as they may not be ATS-friendly.")

    # Ensure score is not negative
    score = max(score, 0)

    return score, suggestions