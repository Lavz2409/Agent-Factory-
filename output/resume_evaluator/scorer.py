def calculate_score(ats_results: dict) -> int:
    """
    Calculate a score based on ATS checks results.

    Args:
        ats_results (dict): A dictionary containing the results of ATS checks.
                            Expected keys are 'keywords', 'sections', and 'formatting'.

    Returns:
        int: A score between 0 and 100 representing the ATS-friendliness of the resume.
    """
    # Define weights for each ATS check category
    weights = {
        'keywords': 0.4,
        'sections': 0.3,
        'formatting': 0.3
    }

    # Calculate individual scores
    keyword_score = ats_results.get('keywords', 0) * weights['keywords']
    section_score = ats_results.get('sections', 0) * weights['sections']
    formatting_score = ats_results.get('formatting', 0) * weights['formatting']

    # Calculate total score
    total_score = keyword_score + section_score + formatting_score

    # Ensure the score is within the range of 0 to 100
    return max(0, min(100, int(total_score)))