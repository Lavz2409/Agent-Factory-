```
def calculate_score(ats_results: dict) -> int:
    """
    Calculate a score based on the ATS results.

    Args:
    - ats_results (dict): A dictionary containing the results of ATS checks with keys:
        - 'keywords_count' (int): Number of relevant keywords found.
        - 'sections_count' (int): Number of proper sections found.
        - 'formatting_ok' (bool): Whether the formatting is simple and ATS-friendly.

    Returns:
    - int: A score between 0 and 100.
    """
    keywords_count = ats_results.get('keywords_count', 0)
    sections_count = ats_results.get('sections_count', 0)
    formatting_ok = ats_results.get('formatting_ok', False)

    # Define weights for each component
    keywords_weight = 0.4
    sections_weight = 0.4
    formatting_weight = 0.2

    # Calculate individual scores
    keywords_score = min(keywords_count, 10) * 10  # Max 100 if 10 or more keywords
    sections_score = min(sections_count, 3) * (100 / 3)  # Max 100 if 3 or more sections
    formatting_score = 100 if formatting_ok else 0

    # Calculate total score
    total_score = (keywords_score * keywords_weight +
                   sections_score * sections_weight +
                   formatting_score * formatting_weight)

    return int(total_score)


def generate_suggestions(ats_results: dict) -> list:
    """
    Generate suggestions to improve the resume based on the ATS results.

    Args:
    - ats_results (dict): A dictionary containing the results of ATS checks with keys:
        - 'keywords_count' (int): Number of relevant keywords found.
        - 'sections_count' (int): Number of proper sections found.
        - 'formatting_ok' (bool): Whether the formatting is simple and ATS-friendly.

    Returns:
    - list: A list of suggestions for improving the resume.
    """
    suggestions = []
    keywords_count = ats_results.get('keywords_count', 0)
    sections_count = ats_results.get('sections_count', 0)
    formatting_ok = ats_results.get('formatting_ok', False)

    # Suggest adding more keywords if less than 10
    if keywords_count < 10:
        suggestions.append(f"Add more relevant keywords. Currently, you have {keywords_count}.")

    # Suggest adding more sections if less than 3
    if sections_count < 3:
        suggestions.append(f"Include more sections. Currently, you have {sections_count}. Consider adding 'Education', 'Skills', and 'Experience'.")

    # Suggest improving formatting if not ATS-friendly
    if not formatting_ok:
        suggestions.append("Simplify the formatting. Avoid special characters, tables, and complex layouts.")

    return suggestions
```