def calculate_score(ats_results: dict) -> int:
    """
    Calculate a score for the resume based on ATS-friendly checks.

    Args:
        ats_results (dict): A dictionary containing the results of ATS checks.
                            Expected keys include 'keywords', 'sections', and 'formatting'.

    Returns:
        int: A score from 0 to 100 indicating how ATS-friendly the resume is.
    """
    # Define weightings for each category
    weights = {
        'keywords': 0.4,
        'sections': 0.3,
        'formatting': 0.3
    }

    # Initialize score
    score = 0

    # Calculate score based on presence of keywords
    if 'keywords' in ats_results:
        keyword_score = ats_results['keywords'] * weights['keywords']
        score += keyword_score

    # Calculate score based on presence of proper sections
    if 'sections' in ats_results:
        section_score = ats_results['sections'] * weights['sections']
        score += section_score

    # Calculate score based on formatting simplicity
    if 'formatting' in ats_results:
        formatting_score = ats_results['formatting'] * weights['formatting']
        score += formatting_score

    # Ensure the score is within 0 to 100
    score = max(0, min(100, int(score)))

    return score