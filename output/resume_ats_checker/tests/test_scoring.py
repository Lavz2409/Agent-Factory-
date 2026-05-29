import pytest
from scoring import calculate_score, generate_suggestions

def test_calculate_score():
    # Test cases for calculate_score function
    ats_results_1 = {
        'keywords_count': 5,
        'sections_count': 3,
        'formatting_ok': True
    }
    ats_results_2 = {
        'keywords_count': 2,
        'sections_count': 2,
        'formatting_ok': False
    }
    ats_results_3 = {
        'keywords_count': 0,
        'sections_count': 1,
        'formatting_ok': False
    }

    assert calculate_score(ats_results_1) == 85  # Expected score based on logic
    assert calculate_score(ats_results_2) == 50  # Expected score based on logic
    assert calculate_score(ats_results_3) == 20  # Expected score based on logic

def test_generate_suggestions():
    # Test cases for generate_suggestions function
    ats_results_1 = {
        'keywords_count': 5,
        'sections_count': 3,
        'formatting_ok': True
    }
    ats_results_2 = {
        'keywords_count': 2,
        'sections_count': 2,
        'formatting_ok': False
    }
    ats_results_3 = {
        'keywords_count': 0,
        'sections_count': 1,
        'formatting_ok': False
    }

    suggestions_1 = generate_suggestions(ats_results_1)
    suggestions_2 = generate_suggestions(ats_results_2)
    suggestions_3 = generate_suggestions(ats_results_3)

    assert suggestions_1 == []  # No suggestions needed
    assert 'Improve formatting' in suggestions_2  # Suggestion for formatting
    assert 'Add more keywords' in suggestions_2  # Suggestion for keywords
    assert 'Add more sections' in suggestions_3  # Suggestion for sections
    assert 'Improve formatting' in suggestions_3  # Suggestion for formatting
    assert 'Add more keywords' in suggestions_3  # Suggestion for keywords

if __name__ == "__main__":
    pytest.main()