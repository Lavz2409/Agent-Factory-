import pytest
from suggestions import generate_suggestions

@pytest.fixture
def sample_parsed_resume():
    return {
        "sections": {
            "Education": "Bachelor of Science in Computer Science",
            "Skills": "Python, Java, SQL",
            "Experience": "Software Developer at XYZ Corp"
        },
        "keywords": {
            "Python": 5,
            "Java": 3,
            "SQL": 2
        }
    }

@pytest.fixture
def incomplete_parsed_resume():
    return {
        "sections": {
            "Skills": "Python, Java",
            "Experience": "Software Developer at XYZ Corp"
        },
        "keywords": {
            "Python": 5,
            "Java": 3
        }
    }

@pytest.fixture
def complex_format_parsed_resume():
    return {
        "sections": {
            "Education": "Bachelor of Science in Computer Science",
            "Skills": "Python, Java, SQL",
            "Experience": "Software Developer at XYZ Corp"
        },
        "keywords": {
            "Python": 5,
            "Java": 3,
            "SQL": 2
        },
        "formatting_issues": ["Tables", "Special Characters"]
    }

def test_generate_suggestions_perfect_resume(sample_parsed_resume):
    suggestions = generate_suggestions(sample_parsed_resume)
    assert suggestions == [], "Expected no suggestions for a perfect resume"

def test_generate_suggestions_incomplete_resume(incomplete_parsed_resume):
    suggestions = generate_suggestions(incomplete_parsed_resume)
    assert "Add an Education section" in suggestions, "Expected suggestion to add Education section"

def test_generate_suggestions_complex_formatting(complex_format_parsed_resume):
    suggestions = generate_suggestions(complex_format_parsed_resume)
    assert "Avoid using tables" in suggestions, "Expected suggestion to avoid tables"
    assert "Remove special characters" in suggestions, "Expected suggestion to remove special characters"